#!/usr/bin/env python3
"""docs — prescriptive CLI for managing trees of structured Markdown docs.

See `docs/` (relative to repo root) for the full specification:

- convention.md      on-disk Markdown convention this tool reads/writes
- cli.md             command surface
- architecture.md    module sketch, data flow, INDEX renderer format

The single-file module is exposed as the ``docs`` console-script via
the ``docs_cli.cli:main`` entry point declared in ``pyproject.toml``.
The Claude Code skill ships alongside under ``docs_cli/skill/`` and is
materialised onto a host via the ``docs install-skill`` verb.

M1: parser, walker, renderer, `docs index`, config loading. M2 adds the
mutating verbs `new`, `archive`, `mv`, and `touch`. M3 adds the
validation and query verbs `check` and `list`, and regroups the INDEX
by Project then Role. M4 adds the migration verb `migrate`, which adopts
a non-conforming foreign directory into the convention. M6 packages the
CLI as `docs-cli` on PyPI and adds the `install-skill` verb.
"""

from __future__ import annotations

import argparse
import contextlib
import enum
import importlib.metadata
import importlib.resources
import json
import os
import re
import shutil
import sys
import tomllib

# M12 — version SoT. `pyproject.toml`'s `[project] version` is the single
# source of truth; `__version__` is read at import time via
# `importlib.metadata.version("docs-cli")`. PackageNotFoundError (e.g. a
# fresh-clone run that hasn't `pip install -e`'d yet) falls back to
# `0.0.0+local` (M12 — OQ-4).
try:
    __version__ = importlib.metadata.version("docs-cli")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0+local"
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------

BUILTIN_STATUSES: frozenset[str] = frozenset(
    {"draft", "active", "blocked", "done", "archived", "superseded"}
)

# Order matches convention.md. The INDEX renderer pins `status` to the top
# of the Active section; this order applies to all other Roles. M7 (F10/OQ-A)
# adds 7 new core vocab roles between `idea` and `notes` so `notes` stays
# the catch-all tail: implementation, sketch, outline, memo, brief, template,
# example.
CANONICAL_ROLE_ORDER: tuple[str, ...] = (
    "charter",
    "plan",
    "spec",
    "milestone",
    "log",
    "status",
    "decision",
    "guide",
    "runbook",
    "reference",
    "postmortem",
    "idea",
    "implementation",
    "sketch",
    "outline",
    "memo",
    "brief",
    "template",
    "example",
    "notes",
)
BUILTIN_ROLES: frozenset[str] = frozenset(CANONICAL_ROLE_ORDER)

# M10 (OQ-O + OQ-P): metadata labels the `unknown-field` check rule
# treats as built-in — always allowed regardless of the
# `[vocabulary] add_fields` configuration. Covers the required fields
# (`Lifecycle`, `Role`, `Project`, `Updated`), the relationship label
# (`Related:`, a bare-label-with-bullet container that is structurally
# required by parts of the convention), and the documented
# archive-time hint label (`Archived-reason:`, written by
# `docs archive --reason`). User-extensible metadata vocabulary lives
# on `Config.fields` (sourced from `[vocabulary] add_fields`).
_BUILTIN_METADATA_FIELDS: frozenset[str] = frozenset(
    {"Lifecycle", "Role", "Project", "Updated", "Related", "Archived-reason"}
)


class Confidence(enum.Enum):
    """Confidence level for a per-file migration decision (M10 — OQ-E / OQ-N).

    The enum replaces the M4-era ``bool | str`` tri-value (``True``,
    ``"medium"``, ``False``) used by `infer_role` and `FileMigration`.
    The string values match the M4 JSON wire format byte-for-byte:
    ``migration_to_json`` serialises ``confidence`` via ``enum.value`` so
    existing consumers see ``"high" | "medium" | "low"`` strings
    unchanged.
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Filenames and markers — exact strings.
INDEX_FILENAME = "INDEX.md"
MARKER_START = "<!-- docs:generated start -->"
MARKER_END = "<!-- docs:generated end -->"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class MetadataError(Exception):
    """Doc metadata is missing, malformed, or structurally invalid.

    Raised by `parse()`. The message includes the file path and a
    short description of the problem.
    """


class VocabularyError(Exception):
    """Doc uses a Lifecycle or Role value not in the configured vocabulary.

    Distinct from MetadataError because the metadata block parsed
    successfully — the issue is the value, not the structure.
    """


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Doc:
    """A parsed Markdown doc.

    Attributes:
        path: Absolute path on disk.
        title: The H1 title (text after the leading `# `).
        lifecycle: Controlled-vocab lifecycle value (M7's F0 rename);
            must be in the configured vocabulary. The on-disk metadata
            key is ``Lifecycle:``. A free-form ``Status:`` line, if
            present in the source, is harvested into ``extra`` like any
            other non-required field — it is NOT vocab-checked.
        role: Doc role; must be in the configured vocabulary.
        project: Project slug, from the metadata `Project:` line or the
            `.docs.toml` default. None only if no default is configured
            and the doc has no `Project:` line.
        updated: Last meaningful update date, from `Updated:`.
        related: Tuple of (verb, root-relative path) pairs harvested
            from the `Related:` block. Paths are normalized to be
            relative to the docs root, not the doc's own directory.
        extra: Additional `Label: value` fields harvested from the
            metadata block (e.g. Owner, Tags, free-form Status). Single-
            value labels become strings; multi-value labels (those
            followed by a bullet list) become tuples of strings.
        body: Doc text after the metadata block. Used by the index
            renderer to extract a one-line description (first non-empty
            paragraph).
        archived: True iff `path` is under the configured archive
            subtree (root/archive_dir/...). May disagree with
            `lifecycle` if the doc was hand-edited; the `check` verb
            (M3) surfaces such drift.
    """

    path: Path
    title: str
    lifecycle: str
    role: str
    project: str | None
    updated: date
    related: tuple[tuple[str, str], ...]
    extra: Mapping[str, str | tuple[str, ...]]
    body: str
    archived: bool

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise MetadataError(f"{self.path}: empty title")
        if not self.lifecycle:
            raise MetadataError(f"{self.path}: empty Lifecycle")
        if not self.role:
            raise MetadataError(f"{self.path}: empty Role")
        if not isinstance(self.updated, date):
            raise MetadataError(
                f"{self.path}: Updated must be a date, got {type(self.updated).__name__}"
            )


@dataclass(frozen=True)
class Config:
    """Resolved configuration for a docs root.

    Loaded from `.docs.toml` at the root, with built-in defaults for any
    missing fields. The vocabulary frozensets are the *union* of the
    built-in set and any `add_lifecycles`/`add_roles` from the config
    (additive only — removing built-ins is not supported).

    M7 (F0) renames the lifecycle vocab config key from `add_statuses`
    to `add_lifecycles`; the `Config.lifecycles` attribute holds the
    union. M7 (F1/F5/F11) also adds the optional `[migrate]` section
    fields: `role_suffixes` (a custom suffix → role map) and
    `project_name` (a per-tree project override consumed by
    `plan_migration`).

    M8 (F3) adds the four exclude fields below: ``exclude_dirs`` /
    ``exclude_globs`` / ``exclude_exts`` come from the ``[exclude]``
    table in ``.docs.toml``; ``docsignore_patterns`` carries the raw
    line contents of a root-level ``.docsignore`` file (compilation
    is deferred to ``compile_exclude_predicate``).

    M10 (OQ-H) adds ``fields`` — the metadata label allowlist sourced
    from ``[vocabulary] add_fields``. Matching is case-sensitive exact
    match (mirroring how ``add_lifecycles`` / ``add_roles`` already
    work; the on-disk convention is ``Capital:``, so ``owner:`` is
    malformed and rejected by the parser). ``check_doc``'s
    ``unknown-field`` rule consults this set together with
    ``_BUILTIN_METADATA_FIELDS`` to decide which extra metadata labels
    are allowed.

    Defaults when `.docs.toml` is absent:
        project = root.resolve().name or "root"
        archive_dir = "archive"
        date_format = "%Y-%m-%d"
        lifecycles = BUILTIN_STATUSES
        roles = BUILTIN_ROLES
        index_filename = INDEX_FILENAME ("INDEX.md")
        role_suffixes = {}
        project_name = None
        exclude_dirs = ()
        exclude_globs = ()
        exclude_exts = ()
        docsignore_patterns = ()
        fields = frozenset()
    """

    project: str
    archive_dir: str
    date_format: str
    lifecycles: frozenset[str]
    roles: frozenset[str]
    index_filename: str = INDEX_FILENAME
    role_suffixes: dict[str, str] = field(default_factory=dict)
    project_name: str | None = None
    exclude_dirs: tuple[str, ...] = ()
    exclude_globs: tuple[str, ...] = ()
    exclude_exts: tuple[str, ...] = ()
    docsignore_patterns: tuple[str, ...] = ()
    fields: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.project.strip():
            raise ValueError("Config.project must be non-empty")
        if not self.archive_dir or "/" in self.archive_dir:
            raise ValueError(
                f"Config.archive_dir must be a single path segment, got {self.archive_dir!r}"
            )
        if not self.date_format:
            raise ValueError("Config.date_format must be non-empty")
        if not self.lifecycles >= BUILTIN_STATUSES:
            missing = BUILTIN_STATUSES - self.lifecycles
            raise ValueError(f"Config.lifecycles missing built-ins: {sorted(missing)}")
        if not self.roles >= BUILTIN_ROLES:
            missing = BUILTIN_ROLES - self.roles
            raise ValueError(f"Config.roles missing built-ins: {sorted(missing)}")


@dataclass(frozen=True)
class Finding:
    """A single validation finding produced by `docs check` (M3).

    Attributes:
        path: Absolute path of the doc the finding is about.
        severity: ``"error"`` or ``"warning"``. An error drives exit
            code 2; a warning with no error present drives exit code 1.
        rule: Stable machine-readable rule id — one of ``missing-field``,
            ``bad-vocab``, ``bad-date``, ``status-drift``, ``broken-ref``,
            ``stale``, ``malformed``. Emitted in ``--json`` output so CI
            hooks can filter on it.
        message: Human-readable one-line description of the problem.
    """

    path: Path
    severity: str
    rule: str
    message: str


@dataclass(frozen=True)
class FileMigration:
    """One per-file decision in a `MigrationPlan` produced by `docs migrate` (M4).

    A `FileMigration` is the migration helper's complete decision for a single
    foreign `.md` file: the metadata `migrate` will insert (`role`, `project`,
    `lifecycle`, `updated`), how confident the inference was, every ambiguity
    it surfaced, and whether the file needs an H1 synthesised or a planned
    archive-normalising move.

    Attributes:
        path: Absolute path of the foreign file on disk.
        rel: Root-relative POSIX path of the file (relative to the migration
            root). The stable identifier used for display and `--json`.
        role: Inferred `Role:` value. Always a built-in role (see
            `BUILTIN_ROLES`) — inference never invents an out-of-vocab role.
        project: Inferred `Project:` value.
        lifecycle: Inferred `Lifecycle:` value (M7's F0 rename). Always a
            built-in lifecycle vocab value (see `BUILTIN_STATUSES`).
        updated: Inferred `Updated:` date.
        synthesized_h1: True iff the file has no H1 and `migrate` will
            synthesise one from the filename (via `_slug_to_title`).
        reconciled_metadata: True iff the file already carried
            metadata-shaped lines that `migrate` will reconcile into the
            inserted block rather than duplicate.
        confidence: A `Confidence` enum member (HIGH / MEDIUM / LOW).
            LOW iff ``ambiguities`` is non-empty; HIGH or MEDIUM iff it is
            empty. MEDIUM carries the derived-signal semantic (H1-content,
            section-header pattern, sibling-set defaulting, non-role suffix
            strip) — no ambiguity to report, but the signal is weaker than
            a direct suffix or in-file `Role:` match. The JSON wire format
            crosses back to a string via ``Confidence.value`` so existing
            consumers see ``"high" | "medium" | "low"`` unchanged.
        ambiguities: Human-readable notes, one per unresolved inference
            question. Non-empty iff ``confidence is Confidence.LOW``;
            empty for HIGH and MEDIUM.
        archive_move: The planned destination as a root-relative POSIX path
            when the file lives in a non-conformant archive-style subdir and
            will be relocated into ``archive/<date>/``; ``None`` when the file
            stays where it is (the active-tree layout is left untouched, and a
            file already under a conformant ``archive/<valid-date>/`` is not
            moved — see `detect_archive_layout`).
    """

    path: Path
    rel: str
    role: str
    project: str
    lifecycle: str
    updated: date
    synthesized_h1: bool
    reconciled_metadata: bool
    confidence: Confidence
    ambiguities: tuple[str, ...]
    archive_move: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.confidence, Confidence):
            raise ValueError(
                f"FileMigration.confidence must be a Confidence enum member, "
                f"got {type(self.confidence).__name__}: {self.confidence!r}"
            )
        if self.confidence is Confidence.LOW and not self.ambiguities:
            raise ValueError("FileMigration.confidence LOW requires a non-empty ambiguities")
        if self.confidence is not Confidence.LOW and self.ambiguities:
            raise ValueError(
                f"FileMigration.confidence {self.confidence!r} requires an empty ambiguities"
            )


@dataclass(frozen=True)
class MigrationPlan:
    """The complete plan `docs migrate` produces for a foreign directory (M4).

    A `MigrationPlan` carries one `FileMigration` per `.md` file under the
    migration root. It is the contract surface a dry-run emits and `--apply`
    consumes: `plan_migration` builds it, `apply_migration` executes it, and
    `migration_to_json` serialises it.

    Attributes:
        root: Absolute path of the foreign directory being migrated.
        files: One `FileMigration` per `.md` file, ordered by root-relative
            POSIX path (the same order `_iter_doc_texts` yields).
        project_original: The raw inferred project name when M7's F11
            normalisation changed the value (e.g. ``"FooBarBaz"`` was
            normalised to ``"foo-bar-baz"``). ``None`` when normalisation
            didn't change the value or when a CLI/sidecar override
            short-circuited normalisation. Surfaced once in the human plan
            footer as ``project: <final> (normalised from "<original>")``.
        multi_project_hints: M7's F5 advisory hints — one per immediate
            subdir whose ``.md`` files share a common filename prefix that
            differs meaningfully from the parent's project and covers
            ≥ 5 files. Empty tuple when no subdir triggers the heuristic
            and when a CLI override (``--config-project``) is in force.
        excluded_breakdown: M8 (F3) — one ``(prefix, count)`` per
            top-level dir that the predicate excluded; the human plan
            footer renders one ``"<count> files excluded under <prefix>"``
            line per pair. HUMAN-OUTPUT ONLY (per the M7 precedent above).
            The aggregate count is no longer carried as a separate field
            (M10 / OQ-D removed the unused ``excluded_count``); consumers
            who need the total compute ``sum(c for _, c in
            excluded_breakdown)``.
        suppressed_exts: M8 (F7) — extensions passed to
            ``--exclude-ext``; used by the non-md sibling footer to drop
            those extensions from the displayed list, and to suppress
            the footer entirely when the displayed list ends up empty.
            HUMAN-OUTPUT ONLY (per the M7 precedent above).
    """

    root: Path
    files: tuple[FileMigration, ...]
    project_original: str | None = None
    multi_project_hints: tuple[str, ...] = ()
    excluded_breakdown: tuple[tuple[str, int], ...] = ()
    suppressed_exts: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------


def parse_date(value: str, date_format: str = "%Y-%m-%d") -> date:
    """Parse a date string, raising MetadataError on malformed input.

    The default format matches `convention.md`. Trims surrounding whitespace
    before parsing so trailing newlines from metadata-line splits don't trip
    the parser.
    """
    try:
        return datetime.strptime(value.strip(), date_format).date()
    except ValueError as exc:
        raise MetadataError(f"Updated: malformed date {value!r} (expected {date_format})") from exc


def validate_lifecycle(value: str, lifecycles: frozenset[str]) -> None:
    """Raise VocabularyError if `value` is not in `lifecycles`."""
    if value not in lifecycles:
        raise VocabularyError(f"Lifecycle: {value!r} not in vocabulary")


def validate_role(value: str, roles: frozenset[str]) -> None:
    """Raise VocabularyError if `value` is not in `roles`."""
    if value not in roles:
        raise VocabularyError(f"Role: {value!r} not in vocabulary")


_LABEL_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):(.*)$")


def _metadata_line_span(text: str) -> tuple[list[str], str, int, int]:
    """Locate the H1 and the metadata block within `text`.

    Returns ``(lines, title, start, end)`` where ``lines`` is
    ``text.splitlines()``, ``title`` is the H1 text, and ``[start, end)`` is
    the half-open line span of the metadata block — from the first metadata
    line through the line after the last. The span may contain a single
    internal blank line separating the inline run from a trailing bare-label
    multi-value group (the convention the project's own docs use).

    This is the single source of metadata-block boundary detection:
    `parse_metadata_block` and the M2 editing helpers all rely on it, so
    their notion of "where the block is" cannot drift.

    Raises:
        MetadataError: missing H1.
    """
    lines = text.splitlines()
    n = len(lines)

    # Find the H1.
    i = 0
    while i < n and lines[i].strip() == "":
        i += 1
    if i >= n:
        raise MetadataError("missing H1 (file is empty)")
    if not lines[i].startswith("# "):
        raise MetadataError(f"missing H1 (first non-empty line: {lines[i]!r})")
    title = lines[i][2:].rstrip()
    i += 1

    # Skip the blank line(s) between H1 and metadata block.
    while i < n and lines[i].strip() == "":
        i += 1
    start = i

    # Scan the block. A blank line continues the block only when the next
    # non-blank line is a bare label immediately followed by a `- ` bullet.
    while i < n:
        if lines[i].strip() == "":
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            if j >= n:
                break
            m = _LABEL_RE.match(lines[j])
            if not m or m.group(2).strip():
                break
            if j + 1 >= n or not lines[j + 1].startswith("- "):
                break
            i = j
            continue

        m = _LABEL_RE.match(lines[i])
        if not m:
            # First non-label content terminates the metadata block; the
            # line is the start of the body.
            break
        if m.group(2).strip():
            # Inline `Label: value`.
            i += 1
            continue
        # Bare label → consume the `- value` bullet run.
        i += 1
        while i < n and lines[i].startswith("- "):
            i += 1

    return lines, title, start, i


def parse_metadata_block(
    text: str,
) -> tuple[str, dict[str, str | tuple[str, ...]], str]:
    """Split doc text into (title, metadata, body).

    Pure syntax: extracts the H1, the metadata block that follows it,
    and the remaining body. The metadata block is a run of `Label: value`
    lines and bare-label-with-bullet groups (e.g. `Related:` followed by
    `- pairs-with: ...`). Bare-label-with-bullet groups may be separated
    from earlier metadata by a blank line — this matches the convention
    used in the project's own docs. An inline `Label: value` line after
    a blank line is treated as body, not metadata.

    Block-boundary detection is delegated to `_metadata_line_span`; this
    function layers the metadata dict and body extraction on top. Does not
    enforce required fields, vocabulary, or date format — `parse()` does.

    Raises:
        MetadataError: missing H1, or a malformed line inside the metadata
            block.
    """
    lines, title, start, end = _metadata_line_span(text)
    n = len(lines)

    metadata: dict[str, str | tuple[str, ...]] = {}
    i = start
    while i < end:
        if lines[i].strip() == "":
            i += 1
            continue
        m = _LABEL_RE.match(lines[i])
        if not m:
            i += 1
            continue
        label, rest = m.group(1), m.group(2)
        rest_stripped = rest.strip()
        if rest_stripped:
            metadata[label] = rest_stripped
            i += 1
            continue
        # Bare label → multi-value list of "- value" bullets.
        i += 1
        values: list[str] = []
        while i < end and lines[i].startswith("- "):
            values.append(lines[i][2:].strip())
            i += 1
        metadata[label] = tuple(values)

    # Body starts at the first content line after the block.
    j = end
    while j < n and lines[j].strip() == "":
        j += 1
    body = "\n".join(lines[j:])
    if text.endswith("\n") and body and not body.endswith("\n"):
        body += "\n"
    return title, metadata, body


def atomic_write(path: Path, content: str) -> None:
    """Write `content` to `path` atomically via tmpfile + rename.

    POSIX-atomic on the same filesystem. Cross-filesystem renames fall back
    to a copy + unlink under the hood (`Path.replace` handles that).
    """
    tmp = path.with_suffix(path.suffix + ".docs-tmp")
    tmp.write_text(content)
    tmp.replace(path)


# ---------------------------------------------------------------------------
# Core API (skeleton — implementations land in Phases 5–7)
# ---------------------------------------------------------------------------


def parse(text: str, path: Path, root: Path) -> Doc:
    """Parse a Markdown doc into a Doc.

    Reads the H1 title, the metadata block (a contiguous run of
    `Label: value` lines under the H1, ending at a blank line),
    and the body.

    Args:
        text: Full doc text.
        path: Doc's absolute path. Used for the `Doc.path` field and
            for error messages.
        root: Docs root (used to determine the archived flag and to
            keep `Related:` paths root-relative).

    Returns:
        A frozen `Doc` instance.

    Raises:
        MetadataError: structural problems (missing H1, missing
            required label, malformed Updated, etc.).
        VocabularyError: Lifecycle or Role value not in the vocabulary.
            Vocabulary validation is performed at parse time but
            requires a Config; in practice this means callers should
            re-validate via the walker when a Config is available.
            For the bare `parse()` call (used in tests), validation
            uses BUILTIN_STATUSES and BUILTIN_ROLES.
    """
    title, metadata, body = parse_metadata_block(text)

    for required in ("Lifecycle", "Role", "Updated"):
        if required not in metadata or not metadata[required]:
            raise MetadataError(f"{path}: missing {required}")
        if not isinstance(metadata[required], str):
            raise MetadataError(f"{path}: {required} must be a single value")

    lifecycle = metadata["Lifecycle"]
    role = metadata["Role"]
    updated_raw = metadata["Updated"]
    assert isinstance(lifecycle, str)
    assert isinstance(role, str)
    assert isinstance(updated_raw, str)

    validate_lifecycle(lifecycle, BUILTIN_STATUSES)
    validate_role(role, BUILTIN_ROLES)
    updated = parse_date(updated_raw)

    project_raw = metadata.get("Project")
    project: str | None
    if project_raw is None:
        project = None
    elif isinstance(project_raw, str):
        project = project_raw
    else:
        raise MetadataError(f"{path}: Project must be a single value")

    related: tuple[tuple[str, str], ...] = ()
    raw_related = metadata.get("Related")
    if raw_related is not None:
        entries = raw_related if isinstance(raw_related, tuple) else (raw_related,)
        parsed_related: list[tuple[str, str]] = []
        for entry in entries:
            verb, sep, target = entry.partition(":")
            if not sep or not target.strip():
                raise MetadataError(f"{path}: malformed Related entry {entry!r}")
            parsed_related.append((verb.strip(), target.strip()))
        related = tuple(parsed_related)

    # F0: a free-form `Status:` line (if present) is no longer a known
    # convention field — it is harvested into `extra` like any other
    # non-required label and preserved verbatim.
    known = {"Lifecycle", "Role", "Updated", "Project", "Related"}
    extra: dict[str, str | tuple[str, ...]] = {k: v for k, v in metadata.items() if k not in known}

    return Doc(
        path=path,
        title=title,
        lifecycle=lifecycle,
        role=role,
        project=project,
        updated=updated,
        related=related,
        extra=extra,
        body=body,
        archived=False,
    )


def walk(
    root: Path,
    config: Config,
    predicate: Callable[[str], bool] | None = None,
) -> Iterator[Doc]:
    """Yield every parseable Markdown doc under root in deterministic order.

    Skip rules:
        - Files not ending in `.md`.
        - The root-level file literally named `INDEX.md` (it's a
          generated view, not a managed doc). Nested `INDEX.md` files
          deeper in the tree ARE walked.
        - Dotfiles and dotdirectories (`.docs.toml`, `.git`, etc.).

    Order: Docs are yielded sorted by their root-relative POSIX path
    (lexicographic). The `archived` flag is set per `Doc.archived` based
    on whether the path lies under `root/config.archive_dir`.

    M8 (F3): the optional ``predicate`` parameter — when provided —
    filters out every root-relative POSIX path for which
    ``predicate(rel)`` is True. Defaults to ``None`` (no filtering) so
    pre-M8 callers stay backward-compatible.
    """
    archive_prefix = config.archive_dir
    yielded: list[Doc] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in filenames:
            if fname.startswith("."):
                continue
            if not fname.endswith(".md"):
                continue
            file_path = Path(dirpath) / fname
            rel = file_path.relative_to(root).as_posix()
            if rel == INDEX_FILENAME:
                continue
            if predicate is not None and predicate(rel):
                continue
            text = file_path.read_text()
            doc = parse(text, file_path, root)
            if rel == archive_prefix or rel.startswith(archive_prefix + "/"):
                doc = replace(doc, archived=True)
            yielded.append(doc)
    yielded.sort(key=lambda d: d.path.relative_to(root).as_posix())
    yield from yielded


def render_index(
    docs: list[Doc],
    config: Config,
    existing: str | None,
    root: Path,
) -> str:
    """Render an INDEX.md from a list of Docs.

    Behavior:
        - If `existing` contains the markers `MARKER_START` and
          `MARKER_END`, only the content between them is rewritten;
          everything outside the markers is preserved verbatim.
        - If `existing` is None or contains no markers, returns a
          minimal INDEX containing only the marker block.

    Format details (see architecture.md "INDEX renderer format"):
        - Summary line: `_Generated YYYY-MM-DD. N docs active, M archived._`
        - Active docs group two levels deep: `## Project — <name>` then
          `### Active — <Role-titlecased>`. A single `## Archived` heading
          trails, flat (not project-grouped).
        - Projects: the docs-root project first, then the rest in
          ascending order. Within a project, role groups follow
          CANONICAL_ROLE_ORDER, with `status` pinned to the top.
        - Within each group: Updated descending, then path ascending.
        - Entry format: `- [path](path) — _role_ — <desc>. Updated YYYY-MM-DD.`
          where `path` is the doc's `root`-relative POSIX path, so docs in
          subdirectories link correctly.

    `root` is the docs root, used to derive each entry's root-relative path.
    The renderer is deterministic: same `docs`, `existing`, and `root` inputs
    produce byte-identical output.
    """
    active = [d for d in docs if not d.archived]
    archived = [d for d in docs if d.archived]
    today = date.today().strftime(config.date_format)
    summary = f"_Generated {today}. {len(active)} docs active, {len(archived)} archived._"

    role_order = ["status"] + [r for r in CANONICAL_ROLE_ORDER if r != "status"]
    sort_key = lambda d: (  # noqa: E731
        -d.updated.toordinal(),
        d.path.relative_to(root).as_posix(),
    )

    # Active docs group two levels deep: Project, then Role. The docs-root
    # project leads; the rest follow in ascending order.
    by_project: dict[str, dict[str, list[Doc]]] = {}
    for d in active:
        by_project.setdefault(_resolved_project(d, config), {}).setdefault(d.role, []).append(d)
    others = sorted(p for p in by_project if p != config.project)
    project_order = ([config.project] if config.project in by_project else []) + others

    lines: list[str] = [summary, ""]
    for project in project_order:
        lines.append(f"## Project — {project}")
        lines.append("")
        role_groups = by_project[project]
        for role in role_order:
            group = role_groups.get(role)
            if not group:
                continue
            group.sort(key=sort_key)
            lines.append(f"### Active — {role.title()}")
            lines.append("")
            for d in group:
                lines.append(_format_entry(d, config, root))
            lines.append("")

    lines.append("## Archived")
    lines.append("")
    if archived:
        archived.sort(key=sort_key)
        for d in archived:
            lines.append(_format_entry(d, config, root))
    else:
        lines.append("_None._")

    derived = "\n".join(lines).rstrip() + "\n"

    if existing:
        marker_span = _find_marker_lines(existing)
        if marker_span is not None:
            pre_end, post_start = marker_span
            pre = existing[:pre_end]
            trailer = existing[post_start:]
            return f"{pre}{MARKER_START}\n{derived}{MARKER_END}{trailer}"
    return f"{MARKER_START}\n{derived}{MARKER_END}\n"


def _find_marker_lines(text: str) -> tuple[int, int] | None:
    """Locate the standalone marker lines in `text`.

    Returns ``(pre_end, post_start)`` where ``pre_end`` is the offset where the
    preamble ends (exclusive — the marker-start line begins here) and
    ``post_start`` is the offset where the trailer begins (the character after
    the marker-end line's trailing newline, if any).

    A marker is recognized only when it appears as a whole line. This avoids
    matching the marker text inside prose mentions (e.g. backtick-quoted
    references in the preamble).

    Returns ``None`` if either marker is missing or they're out of order.
    """
    pre_end: int | None = None
    post_start: int | None = None
    cursor = 0
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        if pre_end is None and stripped == MARKER_START:
            pre_end = cursor
        elif pre_end is not None and stripped == MARKER_END:
            # Trailer "owns" everything past the marker text, including the
            # marker line's own trailing newline. This keeps idempotency: a
            # re-render produces byte-identical output.
            post_start = cursor + len(stripped)
            break
        cursor += len(line)
    if pre_end is None or post_start is None:
        return None
    return pre_end, post_start


def _format_entry(doc: Doc, config: Config, root: Path) -> str:
    rel = doc.path.relative_to(root).as_posix()
    desc = _description(doc.body)
    updated = doc.updated.strftime(config.date_format)
    return f"- [{rel}]({rel}) — _{doc.role}_ — {desc}. Updated {updated}."


def _description(body: str, limit: int = 120) -> str:
    """Extract the first content paragraph from a doc body.

    Skips leading blank lines and header lines (``## ``, ``### ``, etc.),
    then joins consecutive non-blank lines into a single paragraph with
    whitespace collapsed. Trims to ``limit`` characters at the last
    whitespace boundary; appends ``…`` if truncated.
    """
    lines = body.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        stripped = lines[i].strip()
        if stripped == "":
            i += 1
            continue
        if stripped.startswith("#"):
            i += 1
            continue
        break
    if i >= n:
        return ""
    para: list[str] = []
    while i < n and lines[i].strip() != "":
        para.append(lines[i].strip())
        i += 1
    text = " ".join(para)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text.rfind(" ", 0, limit)
    if cut == -1:
        return text[:limit] + "…"
    return text[:cut].rstrip() + "…"


def load_config(root: Path) -> Config:
    """Load `.docs.toml` from root, or return defaults if absent.

    Vocabulary additions from `.docs.toml [vocabulary]` are merged
    into the built-in sets. Removals are not supported (additive
    only — see vocab-adr.md). M7 (F0) renames the lifecycle key
    from `add_statuses` to `add_lifecycles`; no backward-compat alias.

    M7 also reads the optional `[migrate]` section for the F1/F5/F11
    inference-broadening surface:

    - ``role_suffixes``: a custom suffix → role map merged into the
      built-in suffix mapping for this tree's ``docs migrate`` runs.
    - ``project_name``: a per-tree override consumed by
      ``plan_migration`` — short-circuits F11 normalisation when set.

    M8 (F3) also reads the optional ``[exclude]`` section
    (``dirs`` / ``globs`` / ``exts``) and a root-level ``.docsignore``
    file (raw line contents) so the four ``Config`` exclude fields are
    populated for ``compile_exclude_predicate``.

    Args:
        root: Docs root directory (the one that may contain `.docs.toml`).

    Returns:
        A frozen `Config` instance.
    """
    data: dict = {}
    toml_path = root / ".docs.toml"
    if toml_path.is_file():
        data = tomllib.loads(toml_path.read_text())

    project_section = data.get("project", {})
    archive_section = data.get("archive", {})
    vocab_section = data.get("vocabulary", {})
    migrate_section = data.get("migrate", {})
    exclude_section = data.get("exclude", {})

    project = project_section.get("name")
    if not project:
        resolved_name = root.resolve().name
        project = resolved_name if resolved_name else "root"

    archive_dir = archive_section.get("dir", "archive")
    date_format = archive_section.get("date_format", "%Y-%m-%d")

    lifecycles = BUILTIN_STATUSES | frozenset(vocab_section.get("add_lifecycles", []))
    roles = BUILTIN_ROLES | frozenset(vocab_section.get("add_roles", []))
    # M10 (OQ-H): `[vocabulary] add_fields` widens the `unknown-field`
    # check rule's allowlist; case-sensitive exact match.
    fields = frozenset(vocab_section.get("add_fields", []))

    role_suffixes = dict(migrate_section.get("role_suffixes", {}))
    project_name = migrate_section.get("project_name")

    exclude_dirs = tuple(exclude_section.get("dirs", []))
    exclude_globs = tuple(exclude_section.get("globs", []))
    exclude_exts = tuple(exclude_section.get("exts", []))

    # `.docsignore` is OQ-B-pinned to a single file at the tree root —
    # nested files are NOT supported. Raw lines stored verbatim; the
    # compile step in `compile_exclude_predicate` strips comments / blanks
    # and translates patterns to regex.
    docsignore_path = root / ".docsignore"
    docsignore_patterns: tuple[str, ...] = (
        tuple(docsignore_path.read_text().splitlines()) if docsignore_path.is_file() else ()
    )

    return Config(
        project=project,
        archive_dir=archive_dir,
        date_format=date_format,
        lifecycles=lifecycles,
        roles=roles,
        role_suffixes=role_suffixes,
        project_name=project_name,
        exclude_dirs=exclude_dirs,
        exclude_globs=exclude_globs,
        exclude_exts=exclude_exts,
        docsignore_patterns=docsignore_patterns,
        fields=fields,
    )


def find_root(start: Path) -> Path:
    """Walk up from `start` looking for `.docs.toml`; return its directory.

    If no `.docs.toml` is found by the time the walk reaches the
    filesystem root (`Path('/')` on POSIX), returns `start.resolve()`
    as a cwd-as-root fallback. The walk explicitly stops at the root
    sentinel to avoid an infinite loop.
    """
    current = start.resolve()
    while True:
        if (current / ".docs.toml").is_file():
            return current
        parent = current.parent
        if parent == current:
            return start.resolve()
        current = parent


def _find_root_strict(start: Path) -> Path | None:
    """Walk up from `start` looking for `.docs.toml`; return None if absent.

    M12: variant of `find_root` used by verbs that must refuse rather
    than silently treat a non-managed dir as a docs root (`docs touch`
    outside-root refusal; `docs project rename` no-`.docs.toml`
    refusal).
    """
    current = start.resolve()
    while True:
        if (current / ".docs.toml").is_file():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


# ---------------------------------------------------------------------------
# Doc-editing helpers (M2 — implementations land in Phase 5)
# ---------------------------------------------------------------------------
#
# M1 only reads metadata. The mutating verbs must write it back. Rather than
# re-serialize a whole doc (lossy — `parse_metadata_block` discards line order
# and in-block formatting), these helpers do surgical, minimal-diff edits:
# every byte outside the target line(s) is preserved. See the M2 milestone
# doc's Decisions section for the rationale.


def set_metadata_field(text: str, label: str, value: str) -> str:
    """Return `text` with the inline metadata line `<label>: …` set to `value`.

    If a line `<label>: <old>` exists in the metadata block, its value is
    replaced in place — the label, indentation, and every other line are left
    byte-for-byte identical. If no such line exists, a new `<label>: <value>`
    line is appended to the end of the inline-metadata run (before any
    bare-label multi-value group and before the terminating blank line).

    Only the metadata block is considered: a `Label:`-shaped line in the body
    is never matched. The file's trailing-newline state is preserved.

    Used by `touch` (Updated), `archive` (Lifecycle, Updated, Archived-reason).

    Raises:
        MetadataError: `text` has no H1 / metadata block.
    """
    lines, _title, start, end = _metadata_line_span(text)
    keep = text.splitlines(keepends=True)

    # Replace an existing inline `<label>: <value>` line in place, keeping
    # the line's original ending so the trailing-newline state survives.
    for idx in range(start, end):
        m = _LABEL_RE.match(lines[idx])
        if m and m.group(1) == label and m.group(2).strip():
            ending = keep[idx][len(lines[idx]) :]
            keep[idx] = f"{label}: {value}{ending}"
            return "".join(keep)

    # No such line — insert at the end of the inline-metadata run: before
    # the first bare-label group or internal blank line in the span.
    insert_at = end
    for idx in range(start, end):
        line = lines[idx]
        if line.strip() == "":
            insert_at = idx
            break
        m = _LABEL_RE.match(line)
        if m and not m.group(2).strip():
            insert_at = idx
            break
    if insert_at > 0 and not keep[insert_at - 1].endswith(("\n", "\r")):
        keep[insert_at - 1] += "\n"
    keep.insert(insert_at, f"{label}: {value}\n")
    return "".join(keep)


def rewrite_related_refs(text: str, old_rel: str, new_rel: str) -> tuple[str, int]:
    """Rewrite `Related:` bullets whose target path equals `old_rel`.

    Scans the metadata block's `Related:` group; for every bullet of the form
    `- <verb>: <old_rel>`, replaces the path with `new_rel`. The verb and every
    non-matching line are preserved. Returns `(new_text, n)` where `n` is the
    number of bullets rewritten — `n == 0` means `text` is returned unchanged.

    `old_rel` and `new_rel` are root-relative POSIX paths. Used by `mv`.
    """
    lines, _title, start, end = _metadata_line_span(text)
    keep = text.splitlines(keepends=True)

    count = 0
    in_related = False
    for idx in range(start, end):
        line = lines[idx]
        if not in_related:
            m = _LABEL_RE.match(line)
            if m and m.group(1) == "Related" and not m.group(2).strip():
                in_related = True
            continue
        if not line.startswith("- "):
            break
        verb, sep, target = line[2:].partition(":")
        if sep and target.strip() == old_rel:
            ending = keep[idx][len(line) :]
            keep[idx] = f"- {verb.strip()}: {new_rel}{ending}"
            count += 1

    if count == 0:
        return text, 0
    return "".join(keep), count


def scaffold_doc(
    title: str,
    role: str,
    project: str | None,
    updated: date,
    date_format: str = "%Y-%m-%d",
) -> str:
    """Return the full text of a freshly scaffolded doc.

    Produces an `# <title>` H1, a blank line, then the metadata block:
    `Lifecycle: draft`, `Role: <role>`, `Project: <project>` (the `Project:`
    line is omitted entirely when `project` is None), and `Updated:` formatted
    with `date_format`. The body is empty. Output ends with a single trailing
    newline and parses cleanly back through `parse()`. Used by `new`.
    """
    lines = [f"# {title}", "", "Lifecycle: draft", f"Role: {role}"]
    if project is not None:
        lines.append(f"Project: {project}")
    lines.append(f"Updated: {updated.strftime(date_format)}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Exclude predicate (M8 F3 — `.docs.toml [exclude]` + `.docsignore` + CLI)
# ---------------------------------------------------------------------------
#
# A single layered predicate consulted by every walker (`walk` + `_iter_doc_texts`).
# Pattern semantics (OQ-B-pinned subset, gitignore-flavoured):
#
# - `#`-prefixed lines are comments; blank lines are no-ops.
# - Trailing `/` → directory match (any file under that dir).
# - Leading `/` → root-anchored (matches the exact rel path only).
# - `**` → any number of segments; `*` → any single segment chunk; `?` → one char.
# - Leading `!` → re-include (last match wins, mirroring gitignore).
# - A pattern with NO `/` matches against any path segment at any depth.
#
# The three "static" inputs (`config.exclude_dirs` / `exclude_globs` /
# `exclude_exts`) are pure additions to the CLI's `--exclude` / `--exclude-ext`
# overrides — layered, never replaced. The `.docsignore` lines are interleaved
# with the static config but evaluated in file order so negations work.


def _compile_docsignore_pattern(pattern: str) -> tuple[bool, re.Pattern[str]] | None:
    """Compile one raw `.docsignore` line to ``(negate, regex)``.

    Returns ``None`` for comments and blank lines. The regex matches a
    root-relative POSIX path string. Pattern translation (OQ-B subset):

    - Leading ``!`` flips the ``negate`` flag.
    - Leading ``/`` anchors at the root (no nested matching).
    - Trailing ``/`` marks a directory match — the regex matches paths
      that start with ``<dir>/``.
    - ``**`` matches any number of path segments (including zero).
    - ``*`` matches any non-slash chunk.
    - ``?`` matches any single non-slash character.
    - A pattern with NO ``/`` matches any path segment at any depth
      (gitignore semantics).
    - Everything else is taken literally.

    The compilation is intentionally narrow: no character-class brackets,
    no escape sequences. Anything outside this subset is left as a
    literal substring, which is the conservative outcome for an unknown
    syntax fragment.
    """
    stripped = pattern.strip()
    if not stripped or stripped.startswith("#"):
        return None

    negate = stripped.startswith("!")
    if negate:
        stripped = stripped[1:]

    anchored = stripped.startswith("/")
    if anchored:
        stripped = stripped[1:]

    directory_only = stripped.endswith("/")
    if directory_only:
        stripped = stripped[:-1]

    no_slash = "/" not in stripped

    # Walk char-by-char so `**`, `*`, `?` are honoured without re.escape
    # mangling them, and every other char is literal-escaped.
    regex_parts: list[str] = []
    i = 0
    while i < len(stripped):
        if stripped[i : i + 2] == "**":
            regex_parts.append(".*")
            i += 2
        elif stripped[i] == "*":
            regex_parts.append("[^/]*")
            i += 1
        elif stripped[i] == "?":
            regex_parts.append("[^/]")
            i += 1
        else:
            regex_parts.append(re.escape(stripped[i]))
            i += 1
    body = "".join(regex_parts)

    if directory_only:
        # Match any file under <dir>/.
        if anchored:
            full = rf"^{body}/.*$"
        elif no_slash:
            # Bare `data/` matches a `data/` segment at any depth.
            full = rf"(?:^|.*/){body}/.*$"
        else:
            full = rf"^(?:.*/)?{body}/.*$"
    elif anchored:
        full = rf"^{body}$"
    elif no_slash:
        # Bare `*.draft.md` style — match against any path segment.
        full = rf"(?:^|.*/){body}$"
    else:
        full = rf"^{body}$"

    return negate, re.compile(full)


def compile_exclude_predicate(
    config: Config,
    cli_excludes: Sequence[str] = (),
    cli_exts: Sequence[str] = (),
) -> Callable[[str], bool]:
    """Return ``predicate(rel_path)`` → True iff ``rel_path`` should be EXCLUDED.

    Layers four sources additively (never replacing):

    1. ``config.exclude_dirs`` + any ``cli_excludes`` value that is a bare
       dir name (no glob chars, possibly trailing ``/``).
    2. ``config.exclude_globs`` + any ``cli_excludes`` value containing
       glob chars — translated through the same ``.docsignore`` compiler
       so ``**/foo/**`` and ``*memo*`` work uniformly.
    3. ``config.exclude_exts`` + ``cli_exts`` — matched against the
       trailing extension of the path.
    4. ``config.docsignore_patterns`` — evaluated in file order so a
       trailing ``!keep-me.md`` can re-include a file the earlier
       ``*.md`` line had excluded (gitignore last-match-wins).

    The returned predicate takes a root-relative POSIX path (the exact
    rel-key shape `_iter_doc_texts` and `walk` emit) and returns True
    when the path should be filtered out. Callers default to no
    predicate (passing ``None``) when no exclude config / CLI flag is
    in force — keeping the existing pre-M8 walker contract intact.
    """
    # --- bucket 1: directory matchers ----------------------------------------
    dir_names: list[str] = list(config.exclude_dirs)
    glob_patterns: list[str] = list(config.exclude_globs)
    for raw in cli_excludes:
        token = raw.strip()
        if not token:
            continue
        if any(ch in token for ch in "*?["):
            glob_patterns.append(token)
        else:
            dir_names.append(token.rstrip("/"))

    # --- bucket 3: extensions -------------------------------------------------
    ext_set: set[str] = set()
    for ext in list(config.exclude_exts) + list(cli_exts):
        e = ext.strip().lstrip(".")
        if e:
            ext_set.add(e.lower())

    # --- bucket 2: glob matchers (translated via the .docsignore compiler) ---
    glob_compiled: list[re.Pattern[str]] = []
    for raw in glob_patterns:
        compiled = _compile_docsignore_pattern(raw)
        if compiled is not None:
            _negate, rgx = compiled
            glob_compiled.append(rgx)

    # --- bucket 4: docsignore (ordered; negation flips state) -----------------
    docsignore_compiled: list[tuple[bool, re.Pattern[str]]] = []
    for raw in config.docsignore_patterns:
        compiled = _compile_docsignore_pattern(raw)
        if compiled is not None:
            docsignore_compiled.append(compiled)

    def _predicate(rel_path: str) -> bool:
        # Dir match: any prefix segment equals an excluded dir name.
        if dir_names:
            segments = rel_path.split("/")
            # Match the dir at any depth, not just the root, so
            # `[exclude] dirs = ["build"]` excludes both `build/` and
            # `nested/build/`.
            for d in dir_names:
                if d in segments[:-1]:
                    return True

        # Glob match.
        for rgx in glob_compiled:
            if rgx.match(rel_path):
                return True

        # Extension match.
        if ext_set:
            ext = rel_path.rsplit(".", 1)[-1].lower() if "." in rel_path.rsplit("/", 1)[-1] else ""
            if ext in ext_set:
                return True

        # .docsignore — last-match-wins so a trailing `!keep-me.md`
        # re-includes a file the earlier `*.md` line had excluded.
        excluded = False
        for negate, rgx in docsignore_compiled:
            if rgx.match(rel_path):
                excluded = not negate
        return bool(excluded)

    return _predicate


# ---------------------------------------------------------------------------
# Validation and query (M3 — implementations land in Phases 5–7)
# ---------------------------------------------------------------------------
#
# `docs check` validates a tree; `docs list` queries it. Both must cope with
# docs that `parse()` / `walk()` would reject — `check` exists precisely to
# report malformed docs, and `list` must still exit 0 per cli.md. They share
# `_iter_doc_texts`, a lenient traversal that reads raw text without parsing,
# applying the same skip rules as `walk()`.


def _iter_doc_texts(
    root: Path,
    config: Config,
    predicate: Callable[[str], bool] | None = None,
) -> Iterator[tuple[Path, str]]:
    """Yield ``(path, text)`` for every managed Markdown doc under ``root``.

    Lenient counterpart to `walk()`: reads each file's raw text but does not
    parse it, so callers can inspect docs that `parse()` would reject. Applies
    `walk()`'s skip rules exactly — non-``.md`` files, the root-level
    ``INDEX.md``, and dotfiles / dotdirectories are skipped. Yields in
    root-relative POSIX path order, matching `walk()`.

    M8 (F3): the optional ``predicate`` parameter — when provided —
    filters out every root-relative POSIX path for which
    ``predicate(rel)`` is True. Defaults to ``None`` (no filtering) so
    pre-M8 callers stay backward-compatible.
    """
    collected: list[tuple[str, Path]] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in filenames:
            if fname.startswith("."):
                continue
            if not fname.endswith(".md"):
                continue
            file_path = Path(dirpath) / fname
            rel = file_path.relative_to(root).as_posix()
            if rel == INDEX_FILENAME:
                continue
            if predicate is not None and predicate(rel):
                continue
            collected.append((rel, file_path))
    collected.sort(key=lambda pair: pair[0])
    for _rel, file_path in collected:
        yield file_path, file_path.read_text()


def _resolved_project(doc: Doc, config: Config) -> str:
    """Return ``doc``'s project, falling back to the config default.

    `parse()` leaves `Doc.project` None when the doc has no ``Project:`` line;
    the INDEX renderer and `docs list` group and report by the resolved value,
    never None.
    """
    return doc.project if doc.project is not None else config.project


def _root_relative(path: Path, root: Path) -> str:
    """Return ``path`` as a root-relative POSIX string, for display and JSON.

    Falls back to the bare filename if ``path`` is not under ``root`` — only
    reachable for the synthetic paths in unit tests, never for a real walk.
    """
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def check_doc(
    path: Path,
    text: str,
    root: Path,
    config: Config,
    stale: int | None,
    today: date,
) -> list[Finding]:
    """Validate a single doc's raw ``text``; return every finding, never raise.

    Runs the rules cli.md pins for `docs check`:

    - missing or empty required field (``Lifecycle``, ``Role``, ``Updated``) —
      error, rule ``missing-field``.
    - ``Lifecycle`` / ``Role`` not in the configured vocabulary — error,
      rule ``bad-vocab``.
    - ``Updated:`` not parseable in the configured date format — error,
      rule ``bad-date``.
    - structural breakage — a missing H1 — error, rule ``malformed``.
    - lifecycle / location mismatch (``Lifecycle: archived`` outside the
      archive subtree, or any other lifecycle inside it) — error, rule
      ``status-drift``.
    - a ``Related:`` target that does not resolve to a file under ``root`` —
      error, rule ``broken-ref``.
    - with ``stale`` set, a ``Lifecycle: active`` doc whose ``Updated:`` is
      more than ``stale`` days before ``today`` — warning, rule ``stale``.
    - M7 (Phase 6): a missing ``Role:`` whose value is resolvable at
      medium confidence from an H1-content or section-header signal —
      warning, rule ``medium-confidence-inference``.

    Built on `parse_metadata_block` (lenient — it enforces neither required
    fields, vocabulary, nor the date format) plus `validate_lifecycle`,
    `validate_role`, and `parse_date`, each guarded so a rejection becomes a
    `Finding` rather than an exception.

    Note: `parse_metadata_block` terminates the metadata block at the first
    non-label line rather than raising, so the only structural breakage it
    surfaces — and thus the only `malformed` finding — is a missing H1.
    """
    findings: list[Finding] = []

    # --- structural parse: a missing H1 is `malformed`, nothing else to do ---
    try:
        _title, metadata, _body = parse_metadata_block(text)
    except MetadataError as exc:
        findings.append(Finding(path, "error", "malformed", str(exc)))
        return findings

    def _is_empty(value: str | tuple[str, ...] | None) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        return len(value) == 0

    # --- missing or empty required fields ---
    for required in ("Lifecycle", "Role", "Updated"):
        if _is_empty(metadata.get(required)):
            # M7 (Phase 6): a missing `Role:` line whose value is
            # resolvable at medium confidence from an H1-content or
            # section-header signal becomes a warning (rule
            # `medium-confidence-inference`) rather than the hard
            # `missing-field` error — OQ-D's exit-1-on-medium contract.
            if required == "Role":
                inferred = _infer_role_from_h1(text) or _infer_role_from_sections(text)
                if inferred and inferred != "notes":
                    findings.append(
                        Finding(
                            path,
                            "warning",
                            "medium-confidence-inference",
                            f"Role: missing; inferred as {inferred!r} from H1/section signal "
                            f"(medium confidence).",
                        )
                    )
                    continue
            findings.append(
                Finding(
                    path,
                    "error",
                    "missing-field",
                    f"missing or empty required field: {required}",
                )
            )

    lifecycle = metadata.get("Lifecycle")
    role = metadata.get("Role")
    updated_raw = metadata.get("Updated")

    # --- vocabulary ---
    if isinstance(lifecycle, str) and lifecycle.strip():
        try:
            validate_lifecycle(lifecycle.strip(), config.lifecycles)
        except VocabularyError as exc:
            findings.append(Finding(path, "error", "bad-vocab", str(exc)))
    if isinstance(role, str) and role.strip():
        try:
            validate_role(role.strip(), config.roles)
        except VocabularyError as exc:
            findings.append(Finding(path, "error", "bad-vocab", str(exc)))

    # --- date ---
    updated: date | None = None
    if isinstance(updated_raw, str) and updated_raw.strip():
        try:
            updated = parse_date(updated_raw, config.date_format)
        except MetadataError as exc:
            findings.append(Finding(path, "error", "bad-date", str(exc)))

    # --- lifecycle / location drift ---
    if isinstance(lifecycle, str) and lifecycle.strip():
        try:
            rel = path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            rel = path.name
        in_archive = rel == config.archive_dir or rel.startswith(config.archive_dir + "/")
        lifecycle_value = lifecycle.strip()
        if lifecycle_value == "archived" and not in_archive:
            findings.append(
                Finding(
                    path,
                    "error",
                    "status-drift",
                    "Lifecycle: archived but the file is outside the archive subtree",
                )
            )
        elif lifecycle_value != "archived" and in_archive:
            findings.append(
                Finding(
                    path,
                    "error",
                    "status-drift",
                    f"Lifecycle: {lifecycle_value!r} but the file is inside the archive subtree",
                )
            )

    # --- broken Related: refs ---
    raw_related = metadata.get("Related")
    if raw_related is not None:
        entries = raw_related if isinstance(raw_related, tuple) else (raw_related,)
        for entry in entries:
            _verb, sep, target = entry.partition(":")
            target = target.strip()
            if not sep or not target:
                continue
            if not (root / target).is_file():
                findings.append(
                    Finding(
                        path,
                        "error",
                        "broken-ref",
                        f"Related: target does not resolve to a file: {target}",
                    )
                )

    # --- stale (warning; only with --stale, only Lifecycle: active) ---
    if (
        stale is not None
        and isinstance(lifecycle, str)
        and lifecycle.strip() == "active"
        and updated is not None
        and (today - updated).days > stale
    ):
        findings.append(
            Finding(
                path,
                "warning",
                "stale",
                f"Lifecycle: active but not updated in {(today - updated).days} days "
                f"(stale threshold {stale})",
            )
        )

    # --- M10 unknown-field (OQ-F + OQ-H + OQ-O + OQ-P) -------------------
    # The rule is opt-in: it only fires when the tree has set
    # `[vocabulary] add_fields = [...]` (i.e. `config.fields` is non-
    # empty). Trees without the allowlist see no `unknown-field`
    # findings — extra metadata labels (`Owner:`, `Tags:`, free-form
    # `Status:` …) are simply opaque to this rule. Once the allowlist
    # is configured, any label not on the built-in always-allowed set
    # AND not on `config.fields` drives a warning. The built-in set
    # carries the required labels + `Related:` + `Archived-reason:`
    # so structural metadata is never flagged.
    if config.fields:
        allowed = _BUILTIN_METADATA_FIELDS | config.fields
        for label in metadata:
            if label in allowed:
                continue
            findings.append(
                Finding(
                    path,
                    "warning",
                    "unknown-field",
                    f"metadata field '{label}:' not in [vocabulary] add_fields allowlist",
                )
            )

    return findings


def check_tree(
    root: Path,
    config: Config,
    stale: int | None,
    today: date,
    predicate: Callable[[str], bool] | None = None,
) -> list[Finding]:
    """Validate every doc under ``root``; return all findings.

    Iterates `_iter_doc_texts`, applies `check_doc` to each doc, and
    concatenates the results in root-relative POSIX path order. Within a doc,
    findings keep `check_doc`'s order (errors before warnings).

    M8 (F3): the optional ``predicate`` argument is threaded into
    `_iter_doc_texts` so excluded files are skipped before validation.
    """
    findings: list[Finding] = []
    for path, text in _iter_doc_texts(root, config, predicate=predicate):
        findings.extend(check_doc(path, text, root, config, stale, today))
    return findings


def exit_code_for(findings: list[Finding]) -> int:
    """Map ``findings`` to a `docs check` exit code.

    Returns 2 when any finding is an error, 1 when there are warnings but no
    error, and 0 when ``findings`` is empty — the matrix cli.md pins so CI
    hooks can branch on it.
    """
    if any(f.severity == "error" for f in findings):
        return 2
    if any(f.severity == "warning" for f in findings):
        return 1
    return 0


def query_docs(
    root: Path,
    config: Config,
    *,
    lifecycle: str | None,
    role: str | None,
    project: str | None,
    stale: int | None,
    today: date,
    predicate: Callable[[str], bool] | None = None,
) -> list[Doc]:
    """Return the docs under ``root`` matching the filters, sorted.

    Parses each doc from `_iter_doc_texts` leniently — a doc that cannot be
    parsed into a `Doc` at all is omitted (it surfaces under `docs check`, so
    `list` can still exit 0). Filters are AND-combined: ``lifecycle`` and
    ``role`` match exactly; ``project`` matches the resolved project; ``stale``
    keeps only docs whose ``Updated:`` is more than that many days before
    ``today``. Sorted to match the human table — by Lifecycle, then Role, then
    ``Updated`` descending.

    M8 (F3): the optional ``predicate`` keyword filters out excluded
    files before the parse / match pipeline.
    """
    docs: list[Doc] = []
    for path, text in _iter_doc_texts(root, config, predicate=predicate):
        try:
            doc = parse(text, path, root)
        except (MetadataError, VocabularyError):
            # A doc `parse()` rejects surfaces under `docs check`, not here —
            # `list` stays lenient so it can still exit 0 on a messy tree.
            continue
        rel = path.relative_to(root).as_posix()
        if rel == config.archive_dir or rel.startswith(config.archive_dir + "/"):
            # `parse()` hardcodes archived=False; recompute it as `walk()` does.
            doc = replace(doc, archived=True)
        docs.append(doc)

    if lifecycle is not None:
        docs = [d for d in docs if d.lifecycle == lifecycle]
    if role is not None:
        docs = [d for d in docs if d.role == role]
    if project is not None:
        docs = [d for d in docs if _resolved_project(d, config) == project]
    if stale is not None:
        docs = [d for d in docs if (today - d.updated).days > stale]

    docs.sort(key=lambda d: (d.lifecycle, d.role, -d.updated.toordinal()))
    return docs


def finding_to_json(finding: Finding, root: Path) -> dict[str, object]:
    """Convert ``finding`` to its `docs check --json` record.

    Produces ``{path, severity, rule, message}``, with ``path`` rendered as
    the doc's root-relative POSIX path.
    """
    return {
        "path": _root_relative(finding.path, root),
        "severity": finding.severity,
        "rule": finding.rule,
        "message": finding.message,
    }


def doc_to_json(doc: Doc, config: Config, root: Path) -> dict[str, object]:
    """Convert ``doc`` to its `docs list --json` record.

    Produces the schema cli.md pins (M7 renames the lifecycle field):
    ``{path, title, lifecycle, role, project, updated, related,
    extra_fields}`` — ``path`` the root-relative POSIX path, ``project``
    the resolved project, ``updated`` an ISO ``YYYY-MM-DD`` string,
    ``related`` an array of ``{verb, target}`` objects, and
    ``extra_fields`` an object mapping each extra label (e.g. a
    free-form ``Status:`` prose line) to its string or list-of-strings
    value.
    """
    extra_fields: dict[str, object] = {
        label: list(value) if isinstance(value, tuple) else value
        for label, value in doc.extra.items()
    }
    return {
        "path": _root_relative(doc.path, root),
        "title": doc.title,
        "lifecycle": doc.lifecycle,
        "role": doc.role,
        "project": _resolved_project(doc, config),
        "updated": doc.updated.isoformat(),
        "related": [{"verb": verb, "target": target} for verb, target in doc.related],
        "extra_fields": extra_fields,
    }


# ---------------------------------------------------------------------------
# Migration (M4 — implementations land in Phases 5-7)
# ---------------------------------------------------------------------------
#
# `docs migrate` adopts a non-conforming foreign directory into the convention.
# It walks the tree, infers the metadata each file needs (`Lifecycle`, `Role`,
# `Project`, `Updated`) from filename patterns, in-file signals, and mtime,
# and produces a `MigrationPlan` — one `FileMigration` decision per file, with
# every ambiguity surfaced. The inference helpers below are pure; `plan_migration`
# assembles the plan; `apply_migration` executes it. Dry-run by default.

# Filename trailing-token → built-in role. `-adr` maps to the `decision` role
# (ADR is the common spelling of an architecture decision record). M7 (F10)
# adds the 7 new core vocab roles as direct-match suffixes — same-value-as-key
# entries needed since `infer_role` first consults `_ROLE_SUFFIXES` before
# falling through to `BUILTIN_ROLES` membership.
_ROLE_SUFFIXES: dict[str, str] = {
    "spec": "spec",
    "plan": "plan",
    "adr": "decision",
    "log": "log",
    "status": "status",
    "charter": "charter",
    "guide": "guide",
    "runbook": "runbook",
    "reference": "reference",
    "implementation": "implementation",
    "sketch": "sketch",
    "outline": "outline",
    "memo": "memo",
    "brief": "brief",
    "template": "template",
    "example": "example",
}

# Archive-style directory names `detect_archive_layout` recognises as the first
# path segment of a non-conformant archive layout.
_ARCHIVE_SUBDIR_NAMES: frozenset[str] = frozenset({"archive", "archived", "project-history"})


def infer_role(
    filename: str,
    metadata: Mapping[str, str | tuple[str, ...]],
    config: Config | None = None,
) -> tuple[str, Confidence]:
    """Infer a doc's `Role:` from its filename and any in-file metadata.

    Inference passes (M7 — F1 / F10 / F12; M10 — OQ-E):

    1. An in-file ``Role:`` metadata line, when it carries a built-in role
       (see `BUILTIN_ROLES`), wins outright — ``Confidence.HIGH``.
    2. The filename's trailing token (split on ``-`` / ``_`` / whitespace,
       with the ``.md`` suffix dropped) is mapped to a role via
       ``_ROLE_SUFFIXES`` (extended with ``config.role_suffixes`` when
       given) or by ``BUILTIN_ROLES`` membership — ``Confidence.HIGH``.
    3. A trailing ``_M\\d+`` (case-insensitive, leading zeros allowed) is the
       Trial-2 milestone-task-plan shape — returns ``("milestone",
       Confidence.MEDIUM)``.
    4. ``_v\\d+`` / ``_Draft`` / ``_Ready`` non-role suffixes are stripped
       (case-insensitive) and pass 2 is re-tried on the stripped stem —
       ``Confidence.MEDIUM`` (derived signal).
    5. Otherwise the role falls back to ``"notes"`` — ``Confidence.LOW``.

    Args:
        filename: The file's basename (e.g. ``auth-spec.md``).
        metadata: Metadata-shaped lines already present in the file, as
            produced by `parse_metadata_block`.
        config: Optional `Config` whose ``role_suffixes`` extends the
            built-in suffix map for this run (per-tree custom mapping via
            ``[migrate] role_suffixes`` in ``.docs.toml``). ``None`` is the
            test-friendly default and consults ``_ROLE_SUFFIXES`` only.

    Returns:
        ``(role, confidence)`` — ``role`` is always a member of
        `BUILTIN_ROLES`. ``confidence`` is a `Confidence` enum member.
    """
    in_file = metadata.get("Role")
    if isinstance(in_file, str) and in_file.strip() in BUILTIN_ROLES:
        return in_file.strip(), Confidence.HIGH

    suffix_map: dict[str, str] = (
        dict(_ROLE_SUFFIXES) if config is None else {**_ROLE_SUFFIXES, **config.role_suffixes}
    )

    stem = filename[:-3] if filename.endswith(".md") else filename

    def _match_direct(s: str) -> str | None:
        # Word-boundary tolerance (F1): split on `-`, `_`, whitespace, AND
        # case-transitions (`FooPlan` → `Foo`, `Plan`). Case-transition
        # splitting lets a TitleCase-glued name like `MyPlan` resolve to
        # `plan` once the v-suffix is stripped.
        boundaried = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)
        tokens = re.split(r"[-_\s]+", boundaried)
        if not tokens or not tokens[-1]:
            return None
        suffix = tokens[-1].lower()
        if suffix in suffix_map:
            return suffix_map[suffix]
        if suffix in BUILTIN_ROLES:
            return suffix
        return None

    # Pass 2: direct suffix match (high confidence).
    direct = _match_direct(stem)
    if direct is not None:
        return direct, Confidence.HIGH

    # Pass 3: trailing `_M\d+` milestone-number pattern (medium).
    if re.search(r"_M\d+$", stem, flags=re.IGNORECASE):
        return "milestone", Confidence.MEDIUM

    # Pass 4: strip non-role suffixes and re-try (medium).
    stripped = re.sub(r"_(?:Draft|Ready|v\d+)$", "", stem, flags=re.IGNORECASE)
    if stripped != stem:
        retried = _match_direct(stripped)
        if retried is not None:
            return retried, Confidence.MEDIUM

    return "notes", Confidence.LOW


def infer_project(filenames: Sequence[str], dir_name: str) -> str:
    """Infer a tree's `Project:` slug from its filenames, or the directory name.

    Computes the longest common prefix across every basename in ``filenames``,
    then trims it back to the last ``-`` or ``_`` separator. The trimmed prefix
    is used only when it is at least 2 characters long *and* shared by every
    file; otherwise inference falls back to ``dir_name``.

    Args:
        filenames: The basenames of every ``.md`` file in the tree.
        dir_name: The migration directory's own name — the fallback project.

    Returns:
        The inferred project slug. Never empty.
    """
    stems = [n[:-3] if n.endswith(".md") else n for n in filenames]
    prefix = os.path.commonprefix(stems)
    idx = max(prefix.rfind("-"), prefix.rfind("_"))
    if idx >= 0:
        prefix = prefix[:idx]
    if len(prefix) >= 2:
        return prefix
    return dir_name


def normalise_project_name(name: str) -> str:
    """Normalise a project slug to lowercase-kebab (M7 — F11 / OQ-B).

    Splits on case boundaries (`FooBar` → `Foo-Bar`), letter↔digit
    boundaries (`Abc5Mig` → `Abc-5-Mig`), and underscores; lowercases the
    result; collapses repeats; trims leading / trailing dashes.

    Digit-after-digit is NOT a split point, so a date-like sequence such
    as ``2026-01-26`` survives intact.
    """
    if not name:
        return name
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "-", name)
    s = re.sub(r"(?<=[A-Za-z])(?=\d)", "-", s)
    s = re.sub(r"(?<=\d)(?=[A-Za-z])", "-", s)
    s = s.replace("_", "-")
    s = s.lower()
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def infer_lifecycle(
    metadata: Mapping[str, str | tuple[str, ...]], in_archive: bool
) -> tuple[str, bool]:
    """Infer a doc's `Lifecycle:` from in-file metadata or its archive membership.

    An in-file ``Lifecycle:`` line wins when it carries a built-in lifecycle
    value (see `BUILTIN_STATUSES`) — confident. Otherwise the value defaults
    to ``archived`` when ``in_archive`` is True, ``active`` when it is False
    — a confident default for the archive case, a best-effort default for
    the active case. An in-file ``Lifecycle:`` value outside the vocabulary
    is rejected and the default is used instead. A free-form ``Status:``
    prose line carries no controlled-vocab signal and is ignored here (it is
    preserved as an extra field by `insert_metadata_block`).

    Args:
        metadata: Metadata-shaped lines already present in the file.
        in_archive: True iff the file lives under a detected archive-style
            subdirectory.

    Returns:
        ``(lifecycle, confident)`` — ``lifecycle`` is always a member of
        `BUILTIN_STATUSES`.
    """
    in_file = metadata.get("Lifecycle")
    if isinstance(in_file, str) and in_file.strip() in BUILTIN_STATUSES:
        return in_file.strip(), True
    return ("archived", True) if in_archive else ("active", False)


def infer_updated(
    metadata: Mapping[str, str | tuple[str, ...]],
    mtime: float,
    date_format: str = "%Y-%m-%d",
) -> tuple[date, bool]:
    """Infer a doc's `Updated:` date from an in-file line or the file mtime.

    An in-file ``Updated:`` line that parses cleanly in ``date_format`` wins —
    confident. Otherwise — no line, or a malformed value — the date falls back
    to the file's modification time, normalised to a calendar date.

    Args:
        metadata: Metadata-shaped lines already present in the file.
        mtime: The file's POSIX modification time (seconds since the epoch).
        date_format: The ``strptime`` format the in-file line must match.

    Returns:
        ``(updated, confident)`` — ``confident`` is True when a parseable
        in-file ``Updated:`` line determined it, False on the mtime fallback.
    """
    in_file = metadata.get("Updated")
    if isinstance(in_file, str):
        try:
            return parse_date(in_file, date_format), True
        except MetadataError:
            pass
    return date.fromtimestamp(mtime), False


def detect_archive_layout(rel_path: str, archive_date: str) -> str | None:
    """Return the conformant archive destination for ``rel_path``, or ``None``.

    Recognises common non-conformant archive-style layouts and maps a file
    under one to the convention's ``archive/<archive_date>/<basename>``:

    - ``archived/old.md`` -> ``archive/<archive_date>/old.md``
    - ``project-history/x.md`` -> ``archive/<archive_date>/x.md``
    - a bare ``archive/file.md`` (no dated subdir) -> ``archive/<date>/file.md``

    A file that is *already* at ``archive/<valid-YYYY-MM-DD>/<basename>``
    returns ``None`` — it is conformant and only needs ``Lifecycle: archived``
    metadata, not a move. A file in the active tree (no archive-style
    ancestor) also returns ``None``.

    Args:
        rel_path: The file's root-relative POSIX path.
        archive_date: The migration run's archive date (``YYYY-MM-DD``).

    Returns:
        The root-relative POSIX destination path when the file must move, or
        ``None`` when it stays where it is.
    """
    parts = rel_path.split("/")
    first = parts[0]
    if first not in _ARCHIVE_SUBDIR_NAMES:
        return None

    # A file already at the conformant `archive/<ISO-date>/<basename>` needs no
    # move; every other archive-style shape (bare `archive/file.md`, a non-date
    # subdir, `archived/`, `project-history/`) normalises to `archive/<date>/`.
    if first == "archive" and len(parts) == 3:
        try:
            datetime.strptime(parts[1], "%Y-%m-%d")
            return None
        except ValueError:
            pass

    return f"archive/{archive_date}/{parts[-1]}"


# The four metadata fields the convention requires. `migrate` always writes
# these from inferred values; any *other* metadata-shaped line a foreign doc
# carries is "extra" and is preserved (see `_extra_metadata_fields`). M7 (F0)
# replaces `Status` with `Lifecycle`; a free-form `Status:` prose line now
# falls through to the extra-field preservation path.
_REQUIRED_METADATA_FIELDS: frozenset[str] = frozenset({"Lifecycle", "Role", "Project", "Updated"})

# Heading of the body section `insert_metadata_block` parks preserved foreign
# metadata under. Exact string — pinned by the milestone Decisions.
_MIGRATED_METADATA_HEADING = "## Migrated metadata"


def _extra_metadata_fields(
    metadata: Mapping[str, str | tuple[str, ...]],
) -> list[tuple[str, str | tuple[str, ...]]]:
    """Return a foreign doc's non-required metadata fields, in file order.

    The four required convention fields (``Lifecycle`` / ``Role`` /
    ``Project`` / ``Updated``) are dropped — `migrate` supersedes them with
    inferred values. Every *other* metadata-shaped line (``Owner:``,
    ``Tags:``, a ``Related:`` bullet block, a free-form ``Status:`` prose
    line, any ``Label: value`` line) is "extra" and is returned so
    `insert_metadata_block` can preserve it.

    Args:
        metadata: The metadata dict from `parse_metadata_block` — values are
            ``str`` for inline ``Label: value`` lines and ``tuple[str, ...]``
            for bare-label-with-bullet groups.

    Returns:
        A list of ``(label, value)`` pairs for every non-required field, in
        the order they appeared in the file.
    """
    return [(k, v) for k, v in metadata.items() if k not in _REQUIRED_METADATA_FIELDS]


def _render_migrated_metadata_section(
    extra: list[tuple[str, str | tuple[str, ...]]],
) -> str:
    """Render the `## Migrated metadata` body section for preserved fields.

    Each preserved field's label is prefixed with ``Migrated-`` so the line is
    no longer a convention field name (and, living under a ``## `` heading in
    the body, is not re-harvested by `parse_metadata_block`). Inline values
    render as ``Migrated-<Label>: <value>``; a bare-label bullet group (e.g.
    ``Related:``) renders as ``Migrated-<Label>:`` followed by its ``- ``
    bullets verbatim.

    Args:
        extra: The non-required fields from `_extra_metadata_fields`. Must be
            non-empty — callers skip the section entirely when there are none.

    Returns:
        The section text, ending with a single trailing newline.
    """
    lines = [_MIGRATED_METADATA_HEADING, ""]
    for label, value in extra:
        if isinstance(value, str):
            lines.append(f"Migrated-{label}: {value}")
        else:
            lines.append(f"Migrated-{label}:")
            lines.extend(f"- {item}" for item in value)
    return "\n".join(lines) + "\n"


def insert_metadata_block(
    text: str,
    *,
    title: str,
    status: str,
    role: str,
    project: str,
    updated: date,
    date_format: str = "%Y-%m-%d",
) -> str:
    """Return ``text`` with a convention-correct metadata block inserted.

    The core foreign-doc edit: places a metadata block immediately under the
    H1, preserving the existing body verbatim. Behaviour:

    - When ``text`` has an H1, the block is inserted between it and the body.
    - When ``text`` has no H1, ``# <title>`` is synthesised as the first line.
    - When ``text`` already carries metadata-shaped lines under the H1, the
      four required fields (``Lifecycle`` / ``Role`` / ``Project`` /
      ``Updated``) are superseded by the inserted values. Any *other*
      metadata-shaped line (``Owner:``, ``Tags:``, a ``Related:`` block, a
      free-form ``Status:`` prose line, …) is preserved into a ``## Migrated
      metadata`` body section, placed immediately below the canonical block
      and above the rest of the body; each preserved label is renamed with a
      ``Migrated-`` prefix. A foreign doc with no extra fields gets no such
      section.
    - The file's trailing-newline state is preserved.

    The result round-trips cleanly through `parse()` and is accepted by
    `check_doc` — the preserved fields live in the body, not the metadata
    block, so `docs check` does not validate them.

    Args:
        text: The foreign file's full current text.
        title: The H1 title to synthesise when the file has none.
        status: The ``Lifecycle:`` value to write (a built-in lifecycle).
            The parameter is named ``status`` for back-compat; the on-disk
            key is ``Lifecycle:``. Phase 10 simplify candidate.
        role: The ``Role:`` value to write (a built-in role).
        project: The ``Project:`` value to write.
        updated: The ``Updated:`` date to write.
        date_format: The ``strftime`` format for the ``Updated:`` line.

    Returns:
        The full text of the doc with the metadata block inserted.
    """
    extra: list[tuple[str, str | tuple[str, ...]]] = []
    try:
        old_title, old_metadata, body = parse_metadata_block(text)
        h1_title = old_title
        extra = _extra_metadata_fields(old_metadata)
    except MetadataError:
        # No H1 — the whole text is body; synthesise an H1 from `title`.
        body = text
        h1_title = title

    block = (
        f"# {h1_title}\n"
        "\n"
        f"Lifecycle: {status}\n"
        f"Role: {role}\n"
        f"Project: {project}\n"
        f"Updated: {updated.strftime(date_format)}\n"
    )
    # Preserved foreign metadata is parked in a body section immediately below
    # the canonical block and above the rest of the body.
    migrated = _render_migrated_metadata_section(extra) if extra else ""
    body_part = f"{migrated}\n{body}" if (migrated and body) else (migrated or body)

    result = f"{block}\n{body_part}" if body_part else block.rstrip("\n")
    # Preserve the original file's trailing-newline state.
    if text.endswith("\n"):
        if not result.endswith("\n"):
            result += "\n"
    else:
        result = result.rstrip("\n")
    return result


def _in_archive_subdir(rel_path: str) -> bool:
    """True iff ``rel_path``'s first segment is an archive-style directory.

    Recognises ``archive`` / ``archived`` / ``project-history`` — the same set
    `detect_archive_layout` normalises. Used by `plan_migration` to decide the
    default `Lifecycle:` for a file with no in-file lifecycle line.
    """
    return rel_path.split("/")[0] in _ARCHIVE_SUBDIR_NAMES


# H1-trailing-word → built-in role hint (M7 — F1). Used by
# `_infer_role_from_h1` when the filename suffix gave no signal.
_ROLE_WORDS_TO_ROLES: dict[str, str] = {
    "plan": "plan",
    "spec": "spec",
    "specification": "spec",
    "status": "status",
    "charter": "charter",
    "log": "log",
    "decision": "decision",
    "guide": "guide",
    "runbook": "runbook",
    "reference": "reference",
    "implementation": "implementation",
    "sketch": "sketch",
    "outline": "outline",
    "memo": "memo",
    "brief": "brief",
    "milestone": "milestone",
    "postmortem": "postmortem",
    "template": "template",
    "example": "example",
}


def _infer_role_from_h1(text: str) -> str | None:
    """Find the first H1 in ``text``; return a role hint if its trailing
    word matches a known role-word, else None.

    Longest match wins (``"specification"`` beats ``"spec"``). The trailing
    word must be on a word boundary — preceded by whitespace or the H1's
    opening ``# `` so a title like ``# Foospec`` does NOT match.
    """
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].rstrip().lower()
            if not title:
                return None
            for word in sorted(_ROLE_WORDS_TO_ROLES, key=len, reverse=True):
                if title == word:
                    return _ROLE_WORDS_TO_ROLES[word]
                if title.endswith(word) and title[-len(word) - 1].isspace():
                    return _ROLE_WORDS_TO_ROLES[word]
            return None
    return None


def _infer_role_from_sections(text: str) -> str | None:
    """Pattern-match top-level ``## `` headings; return a role hint or None.

    The patterns mirror the Trial-2 conventional shapes:

    - plan: ``## Goal`` + ``## Scope`` + ``## Requirements`` (or
      ``## Exit criteria``).
    - status: ``## Current state`` + either ``## Progress`` or ``## Updates``.
    - decision (ADR): ``## Context`` + ``## Decision`` + ``## Consequences``.
    - log: at least two dated ``## YYYY-MM-DD`` headings.
    """
    headings = [line[3:].strip().lower() for line in text.splitlines() if line.startswith("## ")]
    headings_set = set(headings)
    if {"goal", "scope", "requirements"}.issubset(headings_set) or {
        "goal",
        "exit criteria",
    }.issubset(headings_set):
        return "plan"
    if {"current state", "progress"}.issubset(headings_set) or {
        "current state",
        "updates",
    }.issubset(headings_set):
        return "status"
    if {"context", "decision", "consequences"}.issubset(headings_set):
        return "decision"
    dated = sum(1 for h in headings if re.match(r"\d{4}-\d{2}-\d{2}", h))
    if dated >= 2:
        return "log"
    return None


def _sibling_default(
    rel: str,
    sibling_roles: dict[str, list[str]],
    *,
    min_majority: float = 0.6,
    min_sample: int = 5,
) -> str | None:
    """Return the modal sibling role when ≥ ``min_majority`` of ≥ ``min_sample``
    siblings share it; else ``None``. M7 — F1 / OQ-C.

    Siblings are files in the same immediate subdir whose role was inferred
    at high confidence (the function-level direct-suffix path); the modal
    pool intentionally excludes files that also reached the fallback so the
    defaulting is not self-reinforcing.
    """
    subdir = "/".join(rel.split("/")[:-1])
    siblings = sibling_roles.get(subdir, [])
    if len(siblings) < min_sample:
        return None
    counts: dict[str, int] = {}
    for r in siblings:
        counts[r] = counts.get(r, 0) + 1
    role, count = max(counts.items(), key=lambda kv: kv[1])
    if count / len(siblings) >= min_majority:
        return role
    return None


def _multi_project_hints(
    root: Path,
    parent_project: str,
    *,
    threshold: int = 5,
) -> tuple[str, ...]:
    """For each immediate subdir whose ``.md`` files share a common
    filename prefix distinct from ``parent_project`` AND cover ≥
    ``threshold`` files, return one advisory ``"hint: …"`` line. M7 — F5.

    The candidate name is the normalised longest common prefix of the
    subdir's ``.md`` filenames (OQ6 — file naming is the Trial-2-measured
    signal; when prefix and subdir name normalise to the same kebab value
    they are interchangeable, and when they diverge the file-prefix wins).
    """
    hints: list[str] = []
    for child in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        md_files = sorted(f for f in child.iterdir() if f.is_file() and f.suffix == ".md")
        if len(md_files) < threshold:
            continue
        stems = [f.stem for f in md_files]
        prefix = os.path.commonprefix(stems)
        idx = max(prefix.rfind("-"), prefix.rfind("_"))
        if idx >= 0:
            prefix = prefix[:idx]
        if len(prefix) < 2:
            continue
        candidate = normalise_project_name(prefix)
        if candidate == parent_project:
            continue
        # OQ6: prefer the file-prefix candidate when it differs from the
        # subdir name. When they match, the candidate is already aligned.
        hint = (
            f"hint: subdir {child.name!r}/ looks like a separate project "
            f"(common prefix {prefix!r}, {len(md_files)} .md files). "
            f"Migrate it independently: docs migrate {child.name}/ "
            f"--config-project {candidate}"
        )
        hints.append(hint)
    return tuple(hints)


def plan_migration(
    root: Path,
    archive_date: str | None = None,
    *,
    cli_config_project: str | None = None,
    cli_excludes: Sequence[str] = (),
    cli_exclude_exts: Sequence[str] = (),
) -> MigrationPlan:
    """Build the `MigrationPlan` for the foreign directory ``root``.

    Recurses the whole tree via `_iter_doc_texts` (with a default `Config`),
    inspects every ``.md`` file, and assembles a `FileMigration` per file:
    runs `infer_role` / `infer_project` / `infer_lifecycle` / `infer_updated`,
    flags every ambiguity, sets ``confidence``, and calls
    `detect_archive_layout` to plan any archive-normalising move. The
    active-tree directory layout is left untouched — only files under
    detected archive-style subdirs carry an ``archive_move``.

    M7 — F4 / F5 / F11 surface:

    - When ``archive_date`` is ``None``, archive moves use a per-file date
      derived from the file's ``Updated:`` line (or its mtime fall-back)
      instead of a single migration-run-wide default. An explicit
      ``archive_date`` continues to override globally — the existing
      ``--date`` flag's semantics.
    - The inferred project name is normalised to lowercase-kebab (F11). A
      ``[migrate] project_name`` entry in the tree's ``.docs.toml`` (when
      present), and the ``cli_config_project`` argument (the
      ``--config-project NAME`` CLI flag) both short-circuit normalisation
      — precedence is CLI > sidecar > inferred-and-normalised. The
      pre-normalisation name is carried on
      ``MigrationPlan.project_original`` when normalisation changed it.
    - When the override path is NOT taken, immediate subdirs whose ``.md``
      files share a common filename prefix distinct from the parent's
      project AND cover ≥ 5 files are surfaced as advisory
      ``"hint: …"`` lines on ``MigrationPlan.multi_project_hints``.
    - Files whose role falls back to ``notes`` get a medium-confidence
      upgrade pass via H1-content, section-header pattern, and sibling-set
      defaulting — derived signals OQ-D pins at the ``"medium"`` confidence
      level.

    Args:
        root: The foreign directory to plan a migration for.
        archive_date: Explicit ``YYYY-MM-DD`` archive date that overrides
            the per-file date selection. ``None`` activates the F4 per-file
            mtime / Updated: path.
        cli_config_project: The ``--config-project NAME`` CLI value, or
            ``None`` when the flag is absent. Wins over ``.docs.toml``'s
            ``[migrate] project_name``.

    Returns:
        A `MigrationPlan` whose ``files`` are in root-relative path order
        and whose ``project_original`` / ``multi_project_hints`` describe
        F5 / F11 surfaces.
    """
    date_explicit = archive_date is not None

    config = load_config(root)

    # M8 (F3): build a single layered predicate from `[exclude]` config +
    # `.docsignore` + CLI overrides; apply it inside the walker. Count the
    # excluded files (and bucket them by top-level dir) so the human plan
    # footer can surface "<N> files excluded under <prefix>".
    predicate = compile_exclude_predicate(config, cli_excludes, cli_exclude_exts)
    all_pairs = list(_iter_doc_texts(root, config))
    pairs: list[tuple[Path, str]] = []
    excluded_breakdown_map: dict[str, int] = {}
    for path, text in all_pairs:
        rel = path.relative_to(root).as_posix()
        if predicate(rel):
            # Bucket by the top-level dir prefix (`build/`, `generated/`,
            # …). Root-level files keep the bare filename — they're a
            # degenerate "bucket of one"; OQ-resolved footer wording
            # ("<N> files excluded under <prefix>") is most useful for
            # dir-prefix matches, so root-level excluded files still
            # surface but with the bare name as their prefix.
            prefix = rel.split("/", 1)[0] + "/" if "/" in rel else rel
            excluded_breakdown_map[prefix] = excluded_breakdown_map.get(prefix, 0) + 1
            continue
        pairs.append((path, text))

    # F11 project-name precedence: CLI override > `.docs.toml [migrate]
    # project_name` > F11-normalised(inferred).
    inferred_raw = infer_project([p.name for p, _ in pairs], root.resolve().name)
    inferred_normalised = normalise_project_name(inferred_raw)
    if cli_config_project is not None:
        project = cli_config_project
        project_original: str | None = None
    elif config.project_name is not None:
        project = config.project_name
        project_original = None
    else:
        project = inferred_normalised
        project_original = inferred_raw if inferred_raw != inferred_normalised else None

    # First pass: per-file inference, building one `FileMigration` per file.
    migrations: list[FileMigration] = []
    for path, text in pairs:
        rel = path.relative_to(root).as_posix()
        in_archive = _in_archive_subdir(rel)

        try:
            _t, metadata, _b = parse_metadata_block(text)
            synthesized_h1 = False
        except MetadataError:
            metadata = {}
            synthesized_h1 = True
        reconciled_metadata = bool(metadata)

        role, role_conf = infer_role(path.name, metadata, config)
        lifecycle, _lifecycle_conf = infer_lifecycle(metadata, in_archive)
        updated, _updated_conf = infer_updated(metadata, path.stat().st_mtime, config.date_format)

        # F4: when --date is not set, the archive-move date comes per-file
        # from the resolved `Updated:` (or mtime fall-back) instead of a
        # single migration-run default. With an explicit archive_date the
        # global override wins for every file.
        file_archive_date: str = (
            archive_date
            if date_explicit and archive_date is not None
            else updated.strftime("%Y-%m-%d")
        )
        archive_move = detect_archive_layout(rel, file_archive_date)

        # Ambiguity-flagging rule (resolved Q1): flag for exactly three
        # sources — a `notes` role fallback, a synthesised H1, and an
        # out-of-vocab in-file `Lifecycle:` that had to be substituted. The
        # plain active-tree lifecycle default and the mtime-derived `Updated:`
        # fallback are expected best-effort defaults and are NOT flagged.
        # Preserving extra metadata fields is deterministic and lossless, so
        # it is NOT an ambiguity; an archive-move collision IS — that
        # cross-file check is the second pass below. M7 (F0): a free-form
        # `Status:` prose line is no longer vocab-checked; it is preserved
        # via the extra-field pathway.
        ambiguities: list[str] = []
        # `role_conf` is a Confidence enum member (M10 — OQ-E).
        notes_fallback = role_conf is Confidence.LOW
        if notes_fallback:
            ambiguities.append(
                f"Role inferred as 'notes' fallback — no filename suffix or "
                f"in-file Role: matched ({path.name})."
            )
        if synthesized_h1:
            ambiguities.append("No H1 in the file — a title was synthesised from the filename.")
        in_file_lifecycle = metadata.get("Lifecycle")
        if isinstance(in_file_lifecycle, str) and in_file_lifecycle.strip() not in BUILTIN_STATUSES:
            ambiguities.append(
                f"In-file Lifecycle: {in_file_lifecycle.strip()!r} is out of vocabulary "
                f"— substituted with built-in {lifecycle!r}."
            )

        if ambiguities:
            confidence: Confidence = Confidence.LOW
        elif role_conf is Confidence.MEDIUM:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.HIGH
        migrations.append(
            FileMigration(
                path=path,
                rel=rel,
                role=role,
                project=project,
                lifecycle=lifecycle,
                updated=updated,
                synthesized_h1=synthesized_h1,
                reconciled_metadata=reconciled_metadata,
                confidence=confidence,
                ambiguities=tuple(ambiguities),
                archive_move=archive_move,
            )
        )

    # F1 medium-confidence upgrade pass: for files that landed on `notes`
    # at low confidence (the suffix-only inference fall-back), re-run
    # H1-content → section-header → sibling-set in order. Only files whose
    # ONLY ambiguity is the notes-fallback note can fully upgrade to
    # medium; any remaining ambiguity keeps confidence at low (per the
    # M4 invariant that any ambiguity ⇒ low).
    sibling_roles: dict[str, list[str]] = {}
    for fm in migrations:
        # Only suffix-confident files seed the sibling pool so the
        # defaulting is not self-reinforcing across notes-fallback files.
        if fm.confidence is Confidence.HIGH:
            subdir = "/".join(fm.rel.split("/")[:-1])
            sibling_roles.setdefault(subdir, []).append(fm.role)

    upgraded: list[FileMigration] = []
    notes_fallback_note = "Role inferred as 'notes' fallback"
    for fm in migrations:
        if fm.role != "notes" or fm.confidence is not Confidence.LOW:
            upgraded.append(fm)
            continue
        # Only consider files whose low-confidence rationale includes the
        # notes-fallback (i.e. the role inference itself failed).
        if not any(notes_fallback_note in note for note in fm.ambiguities):
            upgraded.append(fm)
            continue
        # Read the file text once per upgrade candidate.
        try:
            file_text = fm.path.read_text()
        except OSError:
            upgraded.append(fm)
            continue
        new_role = (
            _infer_role_from_h1(file_text)
            or _infer_role_from_sections(file_text)
            or _sibling_default(fm.rel, sibling_roles)
        )
        if not new_role or new_role == "notes":
            upgraded.append(fm)
            continue
        # Drop the now-resolved notes-fallback note; remaining ambiguities
        # (synthesised H1, out-of-vocab Lifecycle:) keep the file at low.
        remaining = tuple(a for a in fm.ambiguities if notes_fallback_note not in a)
        new_confidence: Confidence = Confidence.MEDIUM if not remaining else Confidence.LOW
        upgraded.append(
            replace(fm, role=new_role, confidence=new_confidence, ambiguities=remaining)
        )
    migrations = upgraded

    # Second pass (resolved review finding): two foreign files in different
    # archive-style subdirs can normalise to the same `archive/<date>/<name>`
    # destination — applying the plan would silently overwrite the first.
    # Flag every file sharing a destination as an ambiguity so the dry-run
    # surfaces the collision before `--apply`.
    dest_counts: dict[str, int] = {}
    for fm in migrations:
        if fm.archive_move is not None:
            dest_counts[fm.archive_move] = dest_counts.get(fm.archive_move, 0) + 1
    colliding = {dest for dest, n in dest_counts.items() if n > 1}
    if colliding:
        migrations = [
            replace(
                fm,
                confidence=Confidence.LOW,
                ambiguities=fm.ambiguities
                + (
                    f"Archive-move destination collision — {dest_counts[fm.archive_move]} "
                    f"files normalise to {fm.archive_move!r}; resolve before --apply or "
                    f"files would be overwritten.",
                ),
            )
            if fm.archive_move in colliding
            else fm
            for fm in migrations
        ]

    # F5: multi-project hint emission. The CLI override path
    # short-circuits hint emission — the operator already pinned a
    # project so the heuristic adds no value.
    hints: tuple[str, ...] = (
        () if cli_config_project is not None else _multi_project_hints(root, project)
    )

    excluded_breakdown: tuple[tuple[str, int], ...] = tuple(sorted(excluded_breakdown_map.items()))
    suppressed_exts = tuple(
        e.strip().lstrip(".").lower() for e in cli_exclude_exts if e and e.strip()
    )

    return MigrationPlan(
        root=root,
        files=tuple(migrations),
        project_original=project_original,
        multi_project_hints=hints,
        excluded_breakdown=excluded_breakdown,
        suppressed_exts=suppressed_exts,
    )


# M10 (OQ-A): provenance header for the auto-written `.docs.toml` block.
# Sits immediately above the `[project]` section so an operator
# inspecting the file knows the block was added by `docs migrate
# --apply` (not hand-authored).
_DOCS_TOML_HEADER = "# Added by docs migrate --apply"


def _opportunistic_rmdir(old_parent: Path, root: Path) -> None:
    """Remove `old_parent` if it is now empty after an archive-move.

    Called only after an archive-move; never tree-walks (Step-2
    follow-on #3 — pin the scope tight). The rmdir is opportunistic:
    we swallow `OSError` (typically `ENOTEMPTY` when a non-migrating
    sibling lives in the dir) so the M4 normalisation never destroys
    operator content (OQ-Q).

    Two guards on top of the OSError-swallow:

    - Never remove the plan root itself (a degenerate case where the
      whole tree was a single archive-style dir).
    - Never remove a directory that is itself under the new conformant
      `archive/` subtree (those land at `archive/<date>/` and must
      survive future runs).
    """
    old_resolved = old_parent.resolve()
    root_resolved = root.resolve()
    if old_resolved == root_resolved:
        return
    if old_resolved.is_relative_to(root_resolved / "archive"):
        return
    # ENOTEMPTY (non-migrating sibling), ENOENT (already gone),
    # EBUSY (locked), … — every reason to keep the directory.
    with contextlib.suppress(OSError):
        old_parent.rmdir()


def _ensure_docs_toml(plan: MigrationPlan) -> None:
    """Write or extend the `.docs.toml` sidecar at the plan root (OQ-A).

    Layered protection: this is the OQ-A safety net layered on top of
    the M7 carve-out. The existing-`[project]` early-return inside
    this function is the second gate; the first gate is the
    `_cmd_migrate` carve-out matrix that refuses apply when the
    sidecar carries `[project]` without `[migrate]` / `[exclude]`.

    When the sidecar is absent, writes a minimal `.docs.toml` carrying
    `[project] name = "<resolved-project>"` + `[archive] date_format`
    (per OQ-M, no redundant `dir = "archive"` — the default is
    stable). When the sidecar exists but does NOT carry a `[project]`
    block, appends the new block at the bottom under the
    `# Added by docs migrate --apply` provenance header (OQ-L). When
    `[project]` is already present, this is a no-op (OQ-A
    never-overwrite).
    """
    sidecar = plan.root / ".docs.toml"
    project_name = plan.files[0].project if plan.files else plan.root.resolve().name

    new_block = (
        f"{_DOCS_TOML_HEADER}\n"
        f"[project]\n"
        f'name = "{project_name}"\n'
        f"\n"
        f"[archive]\n"
        f'date_format = "%Y-%m-%d"\n'
    )

    if not sidecar.is_file():
        atomic_write(sidecar, new_block)
        return

    try:
        existing_text = sidecar.read_text()
        parsed = tomllib.loads(existing_text)
    except tomllib.TOMLDecodeError:
        # Surfacing here is best-effort — the file mutations already
        # happened; log to stderr and leave the malformed sidecar
        # alone rather than overwrite it.
        print(
            f"docs: warning: malformed .docs.toml at {sidecar}; not extending",
            file=sys.stderr,
        )
        return

    if "project" in parsed:
        # OQ-A never-overwrite: an existing `[project]` block wins.
        return

    # Append the new block. Strip every trailing newline off the
    # existing content and reattach exactly two — guarantees exactly
    # one blank line between existing content and the provenance
    # comment in every case (empty file, single `\n` tail, double-blank
    # tail, or jagged `\n\n\n` tail all collapse to the same shape).
    atomic_write(sidecar, existing_text.rstrip("\n") + "\n\n" + new_block)


def apply_migration(plan: MigrationPlan) -> None:
    """Execute a `MigrationPlan`: insert metadata blocks, normalise archives, write `.docs.toml`.

    For each `FileMigration` in ``plan``: inserts the decided metadata block
    via `insert_metadata_block`, writes it back atomically (`atomic_write`),
    and — when ``archive_move`` is set — moves the file to its conformant
    ``archive/<date>/`` destination. The metadata edit happens before the
    move, mirroring `_archive_one`, so a failure leaves the original
    untouched. After every archive-move, the now-empty archive-style parent
    dir is opportunistically removed (M10 / OQ-G).

    After the file loop, writes or extends the root `.docs.toml` sidecar
    (M10 / OQ-A) so the adopted tree is immediately self-describing — a
    fresh agent / operator never has to hand-author the sidecar.

    An archive-move whose destination is already occupied raises
    `FileExistsError` rather than silently overwriting it — mirroring the
    `_archive_one` guard. `plan_migration` flags such collisions as an
    ambiguity in the dry-run plan; this guard is the apply-time backstop.

    Args:
        plan: The plan produced by `plan_migration`.

    Raises:
        FileExistsError: an archive-move destination is already occupied.
    """
    for fm in plan.files:
        text = fm.path.read_text()
        new_text = insert_metadata_block(
            text,
            title=_slug_to_title(fm.path.stem),
            status=fm.lifecycle,
            role=fm.role,
            project=fm.project,
            updated=fm.updated,
            date_format="%Y-%m-%d",
        )
        atomic_write(fm.path, new_text)
        if fm.archive_move is not None:
            dest = plan.root / fm.archive_move
            if dest.exists():
                raise FileExistsError(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            # M10 / OQ-G: capture the now-empty source parent BEFORE the
            # move so the rmdir target is unambiguous even if the move
            # changes the tree shape.
            old_parent = fm.path.parent
            fm.path.replace(dest)
            _opportunistic_rmdir(old_parent, plan.root)

    # M10 / OQ-A: write / extend the `.docs.toml` sidecar after the file
    # loop so an in-flight failure does not leave a half-adopted tree
    # with a fresh sidecar pointing at no migrated files.
    _ensure_docs_toml(plan)


def migration_to_json(plan: MigrationPlan) -> list[dict[str, object]]:
    """Convert a `MigrationPlan` to its `docs migrate --json` records.

    Produces one flat record per `FileMigration`, in plan order — the schema
    cli.md pins (M7 renames the lifecycle field and widens confidence):
    ``{path, role, project, lifecycle, updated, confidence, ambiguities,
    archive_move, synthesized_h1, reconciled_metadata}`` — ``path`` the
    root-relative POSIX path, ``updated`` an ISO ``YYYY-MM-DD`` string,
    ``confidence`` one of ``high|medium|low``, ``ambiguities`` an array of
    strings, ``archive_move`` the destination path string or ``null``.

    Args:
        plan: The plan produced by `plan_migration`.

    Returns:
        A list of JSON-serialisable record dicts.
    """
    return [
        {
            "path": fm.rel,
            "role": fm.role,
            "project": fm.project,
            "lifecycle": fm.lifecycle,
            "updated": fm.updated.isoformat(),
            # OQ-E: serialise the Confidence enum as its string value so
            # the documented wire format stays byte-stable.
            "confidence": fm.confidence.value,
            "ambiguities": list(fm.ambiguities),
            "archive_move": fm.archive_move,
            "synthesized_h1": fm.synthesized_h1,
            "reconciled_metadata": fm.reconciled_metadata,
        }
        for fm in plan.files
    ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _add_exclude_flag(p: argparse.ArgumentParser) -> None:
    """Attach the M8 ``--exclude`` flag to a subparser.

    Repeatable; supports gitignore-flavoured patterns (``*`` / ``**`` /
    trailing-``/`` / leading-``/``). Layered on top of any
    ``.docs.toml [exclude]`` config and the root ``.docsignore`` file.
    """
    p.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help=(
            "Exclude paths matching PATTERN; repeatable; supports * / ** / "
            "trailing-/ glob. Layered on top of `.docs.toml [exclude]` and "
            ".docsignore."
        ),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docs",
        description="Prescriptive CLI for managing trees of structured Markdown docs.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"docs {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Shared flags for the M2 mutating verbs. `index` keeps its own copies
    # (M1); folding it into this parent is a Phase 7 cleanup, not a contract
    # change.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root",
        help="Explicit docs root; overrides the upward .docs.toml search.",
    )
    common.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress success messages on stderr.",
    )
    common.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change; make no edits.",
    )

    idx = subparsers.add_parser(
        "index",
        help="Regenerate INDEX.md from metadata in the docs root.",
        description=(
            "Walk the docs root, parse every .md file, and regenerate the "
            "INDEX.md marker block. Hand-edited content outside the markers "
            "is preserved verbatim."
        ),
    )
    idx.add_argument(
        "dir",
        nargs="?",
        default=None,
        help="Docs root (positional alternative to --root).",
    )
    idx.add_argument(
        "--root",
        help="Explicit docs root; overrides positional DIR.",
    )
    idx.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress success messages on stderr.",
    )
    idx.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the would-be INDEX.md to stdout; do not write.",
    )
    _add_exclude_flag(idx)

    new_p = subparsers.add_parser(
        "new",
        parents=[common],
        help="Scaffold a new doc with a correct metadata block.",
        description=(
            "Create <slug>.md in the resolved docs root with a metadata block "
            "(Lifecycle: draft, Role, Project, Updated: today). Does not refresh "
            "INDEX.md. A slug may name a subdirectory (sub/foo); it may not "
            "escape the root or land under the archive subtree."
        ),
    )
    new_p.add_argument("role", help="Doc role; must be in the Role vocabulary.")
    new_p.add_argument("slug", help="File slug, without the .md suffix.")
    new_p.add_argument("--project", help="Project slug (overrides the inferred default).")
    new_p.add_argument("--title", help="H1 title (default: title-cased slug).")
    new_p.add_argument(
        "--body-from",
        metavar="PATH",
        help=(
            "Read body content from PATH (or `-` for stdin) and append it under "
            "the scaffold's frontmatter. Refused (exit 2) if any of the body's "
            "first 20 lines looks like a metadata block — pass body content "
            "only; `docs new` owns the frontmatter."
        ),
    )

    archive_p = subparsers.add_parser(
        "archive",
        parents=[common],
        help="Archive a doc: edit Lifecycle, move to archive/<date>/, reindex.",
        description=(
            "Set Lifecycle: archived and bump Updated:, move the file to "
            "<archive_dir>/<YYYY-MM-DD>/, then regenerate INDEX.md. The "
            "metadata edit is atomic; the move runs only after it succeeds."
        ),
    )
    archive_p.add_argument("file", help="Path to the doc to archive.")
    archive_p.add_argument("--reason", help="Free-form Archived-reason: metadata line.")
    archive_p.add_argument("--date", help="Archive date YYYY-MM-DD (default: today).")
    archive_p.add_argument(
        "--cascade",
        action="store_true",
        help="Also prompt to archive docs related by pairs-with / child-of (one hop).",
    )

    mv_p = subparsers.add_parser(
        "mv",
        parents=[common],
        help="Move/rename a doc and rewrite Related: references tree-wide.",
        description=(
            "Move <old> to <new> (a new name in the same directory or a "
            "different directory under the root), rewrite every Related: entry "
            "across the tree that points at <old>, and regenerate INDEX.md."
        ),
    )
    mv_p.add_argument("old", help="Current path of the doc.")
    mv_p.add_argument("new", help="New path for the doc.")

    touch_p = subparsers.add_parser(
        "touch",
        parents=[common],
        help="Bump one or more docs' Updated: fields to today and reindex.",
        description=(
            "Set Updated: to today in each <file>. No other change. All paths "
            "must resolve under the same docs root; the batch is atomic "
            "(all-or-nothing on errors) and INDEX.md is refreshed exactly "
            "once at end."
        ),
    )
    touch_p.add_argument("files", nargs="+", help="Path(s) to the doc(s) to touch.")

    # M12: `docs project` verb namespace. Today the only nested verb is
    # `rename`; the namespace is reserved for future per-project verbs
    # (`show`, `validate`, ...).
    project_p = subparsers.add_parser(
        "project",
        help="Project-namespace verbs (rename, ...).",
        description=(
            "Project-namespace verbs (M12). Today: `rename`. Reserved for "
            "future per-project verbs (show, validate, ...)."
        ),
    )
    project_sub = project_p.add_subparsers(dest="project_command", required=True)

    project_rename_p = project_sub.add_parser(
        "rename",
        parents=[common],
        help="Rename the docs root's project across .docs.toml + every Project: line.",
        description=(
            "Rename the docs root's project (M12). Rewrites `.docs.toml`'s "
            '`[project] name = "<old>"` to `name = "<new>"` and every '
            "conformant `Project: <old>` line in every active doc, "
            "atomically, with a single end-of-batch INDEX refresh. "
            "`<new-name>` is auto-normalised via `normalise_project_name()`; "
            "empty post-normalised input exits 2. `--dry-run` prints the "
            "plan without writing. Archived docs are skipped + reported; "
            "docs whose `Project:` does not match the old name are reported "
            "in the success footer but not mutated."
        ),
    )
    project_rename_p.add_argument(
        "new_name",
        metavar="new-name",
        help="The new project slug. Auto-normalised; rejected if empty.",
    )

    # M3 read-only verbs. They take neither --dry-run nor the `common` parent
    # (it carries --dry-run, meaningless when nothing is mutated).
    check_p = subparsers.add_parser(
        "check",
        help="Validate the docs tree; report violations with CI-usable exit codes.",
        description=(
            "Walk the docs root and report convention violations: missing or "
            "malformed metadata, unknown vocabulary, status/location drift, "
            "and broken Related: references. Exit 0 clean, 1 warnings only, "
            "2 errors."
        ),
    )
    check_p.add_argument(
        "dir",
        nargs="?",
        default=None,
        help="Docs root (positional alternative to --root).",
    )
    check_p.add_argument(
        "--root",
        help="Explicit docs root; overrides positional DIR.",
    )
    check_p.add_argument(
        "--stale",
        type=int,
        metavar="N",
        help="Also warn on Lifecycle: active docs not updated in more than N days.",
    )
    check_p.add_argument(
        "--json",
        action="store_true",
        help="Emit findings as a JSON array instead of grouped human output.",
    )
    _add_exclude_flag(check_p)

    list_p = subparsers.add_parser(
        "list",
        help="Query the docs tree with filters; human table or JSON output.",
        description=(
            "List docs in the tree, optionally filtered by lifecycle, role, "
            "project, or staleness. Default output is a table grouped by "
            "Lifecycle then Role; --json emits an array of records."
        ),
    )
    list_p.add_argument(
        "--root",
        help="Explicit docs root; overrides the upward .docs.toml search.",
    )
    list_p.add_argument("--lifecycle", help="Keep only docs with this Lifecycle.")
    list_p.add_argument("--role", help="Keep only docs with this Role.")
    list_p.add_argument("--project", help="Keep only docs with this Project.")
    list_p.add_argument(
        "--stale",
        type=int,
        metavar="N",
        help="Keep only docs not updated in more than N days.",
    )
    list_p.add_argument(
        "--json",
        action="store_true",
        help="Emit an array of records instead of a human table.",
    )
    _add_exclude_flag(list_p)

    # M4 migration verb. It takes neither --root nor the `common` parent: a
    # foreign tree has no `.docs.toml` for `--root` to resolve, and `migrate`
    # inverts the mutating-verb polarity — it is dry-run by default and takes
    # `--apply` to opt *in* to writing (vs `common`'s `--dry-run` to opt out).
    migrate_p = subparsers.add_parser(
        "migrate",
        help="Adopt a non-conforming foreign directory into the convention.",
        description=(
            "Walk a foreign directory, infer the metadata the convention "
            "requires for every .md file, and produce a migration plan — one "
            "decision per file, every ambiguity flagged. Dry-run by default; "
            "--apply inserts the metadata blocks and normalises archive-style "
            "subdirectories. Refuses a directory whose .docs.toml carries a "
            "managed-root marker ([project], [archive], or [vocabulary]); a "
            ".docs.toml containing only a [migrate] section is read as a "
            "foreign-tree migration-sidecar (M7). M8 widens this further: "
            "an [exclude] section in .docs.toml waives the refusal even "
            "alongside the managed markers — the operator's explicit "
            "signal 'use migrate to triage / re-migrate this managed tree'."
        ),
    )
    migrate_p.add_argument("dir", help="The foreign directory to migrate.")
    migrate_p.add_argument(
        "--apply",
        action="store_true",
        help="Write the inferred metadata blocks and perform archive moves.",
    )
    # M8 (F6): `--summary` and `--json` are mutually exclusive output modes
    # (one human-tabular, one machine-readable). argparse renders the
    # documented "not allowed with argument" error.
    out_group = migrate_p.add_mutually_exclusive_group()
    out_group.add_argument(
        "--json",
        action="store_true",
        help="Emit the migration plan as a JSON array instead of human output.",
    )
    out_group.add_argument(
        "--summary",
        action="store_true",
        help=(
            "Compact triage view — one line per file (path  role  conf  notes). "
            "Mutually exclusive with --json."
        ),
    )
    migrate_p.add_argument(
        "--only",
        choices=["ambiguous"],
        help="Filter the per-file plan to a subset; today only `ambiguous` is supported.",
    )
    migrate_p.add_argument(
        "--group-by",
        choices=["role", "confidence"],
        help="Group the per-file plan lines by role or by confidence (high → low).",
    )
    migrate_p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress success messages on stderr.",
    )
    migrate_p.add_argument(
        "--date",
        help="Archive date YYYY-MM-DD for normalised moves (default: today).",
    )
    migrate_p.add_argument(
        "--config-project",
        metavar="NAME",
        help=(
            "Override the inferred project name for this run (F5). Bypasses "
            "project-name normalisation and multi-project hint emission."
        ),
    )
    migrate_p.add_argument(
        "--exclude-ext",
        default="",
        metavar="EXTS",
        help=(
            "Comma-separated list of extensions to suppress from the non-Markdown "
            "sibling footer (and from any exclude-predicate evaluation). Example: "
            "`--exclude-ext xlsx,html`."
        ),
    )
    _add_exclude_flag(migrate_p)

    install_skill_p = subparsers.add_parser(
        "install-skill",
        help="Materialise the bundled Claude Code skill onto this host.",
        description=(
            "Copy (or symlink) the bundled `docs` Claude Code skill from the "
            "installed `docs_cli` package onto a host so an agent driving "
            "Claude Code can pick it up. The default destination is "
            "~/.claude/skills/docs/; an existing destination must already be "
            "byte-identical to the bundled source or carry --force. "
            "--symlink is rejected when running from a wheel install (the "
            "bundled skill lives under site-packages; symlinking would couple "
            "the skill's stability to the venv's lifecycle); use it only with "
            "an editable install. On Windows, --symlink may require "
            "developer-mode or elevated privileges; --copy is recommended."
        ),
    )
    install_skill_p.add_argument(
        "--dest",
        default="~/.claude/skills/docs/",
        help="Destination directory (default: ~/.claude/skills/docs/).",
    )
    mode = install_skill_p.add_mutually_exclusive_group()
    mode.add_argument(
        "--copy",
        dest="mode",
        action="store_const",
        const="copy",
        help="Copy the bundled skill files (default).",
    )
    mode.add_argument(
        "--symlink",
        dest="mode",
        action="store_const",
        const="symlink",
        help="Symlink to the bundled skill source (editable installs only).",
    )
    install_skill_p.set_defaults(mode="copy")
    install_skill_p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite a non-identical existing destination.",
    )
    install_skill_p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress success messages on stderr.",
    )

    return parser


def _resolve_touch_root(args: argparse.Namespace, start: Path) -> Path | int:
    """M12: resolve a docs root for `docs touch`, or print a refusal + exit code.

    When `--root` is set, the directory must contain a `.docs.toml`;
    otherwise return 2 with the `--root`-named refusal. When `--root` is
    absent, walk up from `start`; if no `.docs.toml` ancestor is found,
    return 2 with the start-path-named refusal (M12 — OQ-C / OQ-11 /
    OQ-η).
    """
    if args.root:
        root = Path(args.root).resolve()
        if not (root / ".docs.toml").is_file():
            print(
                f"docs: touch: --root {args.root} does not contain .docs.toml; refusing",
                file=sys.stderr,
            )
            return 2
        return root
    found = _find_root_strict(start)
    if found is None:
        print(
            f"docs: touch: {start} is not under a docs root with .docs.toml; refusing",
            file=sys.stderr,
        )
        return 2
    return found


def _resolve_project_root(args: argparse.Namespace, start: Path) -> Path | int:
    """M12: resolve a docs root for `docs project rename`, or print a refusal.

    Mirrors `_resolve_touch_root`'s split (`--root` named when set; the
    start path named when not) for the `docs project rename` no-root
    refusal (M12 — OQ-1 / OQ-η).
    """
    if args.root:
        root = Path(args.root).resolve()
        if not (root / ".docs.toml").is_file():
            print(
                f"docs: project rename: --root {args.root} does not contain .docs.toml; refusing",
                file=sys.stderr,
            )
            return 2
        return root
    found = _find_root_strict(start)
    if found is None:
        print(
            f"docs: project rename: {start} is not under a docs root with .docs.toml; refusing",
            file=sys.stderr,
        )
        return 2
    return found


def _refresh_index(
    root: Path,
    config: Config,
    predicate: Callable[[str], bool] | None = None,
) -> Path:
    """Walk `root`, render its INDEX.md, and write it atomically.

    Returns the INDEX path. Shared by `docs index` (write path) and the M2
    mutating verbs, which reindex after a successful mutation.

    M8 (F3): the optional ``predicate`` is threaded into `walk` so
    excluded files never appear in the INDEX.

    Raises:
        MetadataError, VocabularyError: a doc in the tree is malformed;
            callers map these to exit code 2.
    """
    collected = list(walk(root, config, predicate=predicate))
    index_path = root / config.index_filename
    existing = index_path.read_text() if index_path.is_file() else None
    output = render_index(collected, config, existing, root)
    atomic_write(index_path, output)
    return index_path


def _cmd_index(args: argparse.Namespace) -> int:
    if args.root:
        root = Path(args.root)
    elif args.dir:
        root = Path(args.dir)
    else:
        root = find_root(Path.cwd())

    if not root.exists() or not root.is_dir():
        print(f"docs: root not found: {root}", file=sys.stderr)
        return 1

    try:
        config = load_config(root)
        predicate = compile_exclude_predicate(config, getattr(args, "exclude", []) or [])
        if args.dry_run:
            collected = list(walk(root, config, predicate=predicate))
            index_path = root / config.index_filename
            existing = index_path.read_text() if index_path.is_file() else None
            sys.stdout.write(render_index(collected, config, existing, root))
            return 0
        index_path = _refresh_index(root, config, predicate=predicate)
    except tomllib.TOMLDecodeError as exc:
        print(f"docs: malformed .docs.toml: {exc}", file=sys.stderr)
        return 2
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(f"docs: wrote {index_path}", file=sys.stderr)
    return 0


def _slug_to_title(slug: str) -> str:
    """Derive a default H1 title from a slug: last path segment, title-cased.

    `-` and `_` are treated as word separators (`sub/my-feature` → `My Feature`).
    """
    segment = slug.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]
    return segment.replace("-", " ").replace("_", " ").title()


def _cmd_new(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else find_root(Path.cwd())
    if not root.is_dir():
        print(f"docs: root not found: {root}", file=sys.stderr)
        return 1
    try:
        config = load_config(root)
    except tomllib.TOMLDecodeError as exc:
        print(f"docs: malformed .docs.toml: {exc}", file=sys.stderr)
        return 2

    if args.role not in config.roles:
        print(f"docs: invalid role {args.role!r} (not in the Role vocabulary)", file=sys.stderr)
        return 2

    # Resolve the slug to a path under the root. A trailing `.md` is stripped;
    # absolute paths, `..` components, and the archive subtree are rejected.
    slug = args.slug
    if slug.endswith(".md"):
        slug = slug[:-3]
    rel = Path(slug)
    target_rel = Path(slug + ".md")
    if (
        not slug.strip()
        or rel.is_absolute()
        or ".." in rel.parts
        or (len(target_rel.parts) >= 2 and target_rel.parts[0] == config.archive_dir)
    ):
        print(f"docs: invalid slug {args.slug!r}", file=sys.stderr)
        return 2
    target = root / target_rel

    if target.exists():
        print(f"docs: file already exists: {target}", file=sys.stderr)
        return 1

    # M8 (F9): `--body-from` reads body content from a file or stdin and
    # appends it under the scaffold. The OQ-E refusal heuristic
    # (per-OQ4: BEFORE the `--dry-run` check so an agent dry-running an
    # invalid body still gets the failure) scans the first 20 lines for
    # `^[A-Z][A-Za-z-]+:\s` and refuses if any line matches.
    body_text: str | None = None
    if args.body_from is not None:
        if args.body_from == "-":
            body_text = sys.stdin.read()
        else:
            body_path = Path(args.body_from)
            if not body_path.is_file():
                print(
                    f"docs: --body-from: file not found: {body_path}",
                    file=sys.stderr,
                )
                return 2
            try:
                body_text = body_path.read_text()
            except OSError as exc:
                print(f"docs: --body-from: {exc}", file=sys.stderr)
                return 2

        # OQ-E refusal heuristic — scan the first 20 lines.
        head = body_text.splitlines()[:20]
        metadata_re = re.compile(r"^[A-Z][A-Za-z-]+:\s")
        if any(metadata_re.match(line) for line in head):
            preview = "\n".join(body_text.splitlines()[:5])
            print(
                "docs: --body-from content appears to contain a metadata block.\n"
                "      Pass body content only — `docs new` owns the frontmatter.\n"
                f"      Stripped first 5 lines:\n{preview}",
                file=sys.stderr,
            )
            return 2

    title = args.title or _slug_to_title(slug)
    project = args.project or config.project
    text = scaffold_doc(title, args.role, project, date.today(), config.date_format)
    if body_text is not None:
        # Compose scaffold + body. The scaffold ends with a single `\n`;
        # we want exactly one blank line separating the frontmatter from
        # the body, so inject one only when the body doesn't already
        # start with a newline. The body text itself is appended
        # verbatim — `test_body_from_output_matches_scaffold_plus_body_golden`
        # asserts `written.endswith(body)` byte-equality.
        separator = "" if body_text.startswith("\n") else "\n"
        text = text + separator + body_text

    if args.dry_run:
        if not args.quiet:
            print(f"docs: would create {target}", file=sys.stderr)
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(target, text)
    if not args.quiet:
        print(f"docs: created {target}", file=sys.stderr)
    return 0


# Relationship verbs that `archive --cascade` follows (one hop only).
_CASCADE_VERBS = ("pairs-with", "child-of")


def _archive_one(path: Path, root: Path, config: Config, date_str: str, reason: str | None) -> Path:
    """Archive a single doc: edit metadata, then move it into the dated dir.

    Sets `Lifecycle: archived`, bumps `Updated:` to `date_str`, and appends an
    `Archived-reason:` line when `reason` is given. The edited text is written
    back atomically *before* the move, so a failure leaves the original doc
    untouched. Returns the doc's new path.

    Raises:
        MetadataError: the doc has no editable metadata block.
        FileExistsError: the archive destination is already occupied.
    """
    new_text = set_metadata_field(path.read_text(), "Lifecycle", "archived")
    new_text = set_metadata_field(new_text, "Updated", date_str)
    if reason:
        new_text = set_metadata_field(new_text, "Archived-reason", reason)
    dest = root / config.archive_dir / date_str / path.name
    if dest.exists():
        raise FileExistsError(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(path, new_text)
    path.replace(dest)
    return dest


def _cascade_archive(doc: Doc, root: Path, config: Config, date_str: str, quiet: bool) -> None:
    """Prompt to archive each one-hop `pairs-with` / `child-of` relation of `doc`.

    Each related doc that still exists prompts for a y/N confirmation on stdin;
    on `y` it is archived into the same dated directory. Declined docs — and
    docs whose archive fails — are left in place (drift `docs check` surfaces).
    The cascade is one hop only: the related docs' own relations are not
    followed.
    """
    for verb, target in doc.related:
        if verb not in _CASCADE_VERBS:
            continue
        candidate = root / target
        if not candidate.is_file():
            continue
        print(f"docs: also archive {target}? [y/N] ", end="", file=sys.stderr, flush=True)
        if sys.stdin.readline().strip().lower() not in ("y", "yes"):
            if not quiet:
                print(f"docs: left {target} in place", file=sys.stderr)
            continue
        try:
            dest = _archive_one(candidate, root, config, date_str, None)
        except (MetadataError, FileExistsError, OSError) as exc:
            print(f"docs: could not archive {target}: {exc}", file=sys.stderr)
            continue
        if not quiet:
            print(f"docs: archived {target} -> {dest}", file=sys.stderr)


def _cmd_archive(args: argparse.Namespace) -> int:
    file_path = Path(args.file)
    if not file_path.is_file():
        print(f"docs: file not found: {file_path}", file=sys.stderr)
        return 1

    root = Path(args.root) if args.root else find_root(file_path.parent)
    try:
        config = load_config(root)
    except tomllib.TOMLDecodeError as exc:
        print(f"docs: malformed .docs.toml: {exc}", file=sys.stderr)
        return 2

    if args.date:
        try:
            archive_date = parse_date(args.date, config.date_format)
        except MetadataError as exc:
            print(f"docs: --date: {exc}", file=sys.stderr)
            return 2
    else:
        archive_date = date.today()
    date_str = archive_date.strftime(config.date_format)

    # Validate the doc has the required metadata before mutating anything.
    try:
        doc = parse(file_path.read_text(), file_path, root)
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 1

    dest = root / config.archive_dir / date_str / file_path.name

    if args.dry_run:
        if not args.quiet:
            print(f"docs: would archive {file_path} -> {dest}", file=sys.stderr)
            cascadable = [t for v, t in doc.related if v in _CASCADE_VERBS]
            if args.cascade and cascadable:
                print(f"docs: --cascade would prompt for: {', '.join(cascadable)}", file=sys.stderr)
        return 0

    try:
        dest = _archive_one(file_path, root, config, date_str, args.reason)
    except MetadataError as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 1
    except FileExistsError as exc:
        print(f"docs: archive destination already exists: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"docs: could not create archive directory: {exc}", file=sys.stderr)
        return 2

    if args.cascade:
        _cascade_archive(doc, root, config, date_str, args.quiet)

    try:
        _refresh_index(root, config)
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: INDEX refresh failed: {exc}", file=sys.stderr)
        return 2
    if not args.quiet:
        print(f"docs: archived {file_path.name} -> {dest}", file=sys.stderr)
    return 0


def _cmd_mv(args: argparse.Namespace) -> int:
    old_path = Path(args.old)
    new_path = Path(args.new)
    if not old_path.is_file():
        print(f"docs: file not found: {old_path}", file=sys.stderr)
        return 1
    if new_path.exists():
        print(f"docs: destination already exists: {new_path}", file=sys.stderr)
        return 1

    root = Path(args.root) if args.root else find_root(old_path.parent)
    try:
        config = load_config(root)
    except tomllib.TOMLDecodeError as exc:
        print(f"docs: malformed .docs.toml: {exc}", file=sys.stderr)
        return 2

    root_abs = root.resolve()
    try:
        old_rel = old_path.resolve().relative_to(root_abs).as_posix()
        new_rel = new_path.resolve().relative_to(root_abs).as_posix()
    except ValueError:
        print(f"docs: mv: both paths must be under the docs root {root}", file=sys.stderr)
        return 2

    if args.dry_run:
        if not args.quiet:
            print(f"docs: would move {old_rel} -> {new_rel}", file=sys.stderr)
        return 0

    new_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.replace(new_path)

    try:
        rewrites = 0
        for doc in walk(root, config):
            updated_text, n = rewrite_related_refs(doc.path.read_text(), old_rel, new_rel)
            if n:
                atomic_write(doc.path, updated_text)
                rewrites += n
        _refresh_index(root, config)
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(
            f"docs: moved {old_rel} -> {new_rel} ({rewrites} reference(s) rewritten)",
            file=sys.stderr,
        )
    return 0


def _cmd_touch(args: argparse.Namespace) -> int:
    # M10 (OQ-C): atomic multi-file touch. Validate every path first; if
    # any path is missing or any rewrite would raise, exit 1 + name the
    # bad path BEFORE any on-disk mutation. Otherwise: write every rewrite
    # via `atomic_write`, then refresh the INDEX exactly once at end-of-
    # batch. Single-INDEX-refresh, all-or-nothing semantics.
    file_paths = [Path(p) for p in args.files]

    # First pass: every path must exist + be a real file.
    for fp in file_paths:
        if not fp.is_file():
            print(f"docs: file not found: {fp}", file=sys.stderr)
            return 1

    # Resolve the docs root from the first path; every subsequent path
    # must resolve under the same root (Step-2 follow-on #4: multi-root
    # touch is undefined behaviour, out of M10 scope).
    root = Path(args.root) if args.root else find_root(file_paths[0].parent)
    try:
        config = load_config(root)
    except tomllib.TOMLDecodeError as exc:
        print(f"docs: malformed .docs.toml: {exc}", file=sys.stderr)
        return 2

    root_resolved = root.resolve()
    for fp in file_paths:
        try:
            fp.resolve().relative_to(root_resolved)
        except ValueError:
            print(
                f"docs: {fp} is outside the resolved docs root ({root_resolved})",
                file=sys.stderr,
            )
            return 1

    # Second pass: build every rewrite in memory, catching MetadataError
    # before any disk write so a malformed sibling does not partially
    # mutate the batch.
    today = date.today().strftime(config.date_format)
    rewrites: list[tuple[Path, str]] = []
    for fp in file_paths:
        try:
            new_text = set_metadata_field(fp.read_text(), "Updated", today)
        except MetadataError as exc:
            print(f"docs: {fp}: {exc}", file=sys.stderr)
            return 1
        rewrites.append((fp, new_text))

    if args.dry_run:
        if not args.quiet:
            for fp, _ in rewrites:
                print(f"docs: would touch {fp} (Updated: {today})", file=sys.stderr)
        return 0

    for fp, new_text in rewrites:
        atomic_write(fp, new_text)

    # OQ-C: single end-of-batch INDEX refresh.
    try:
        _refresh_index(root, config)
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: INDEX refresh failed: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        for fp, _ in rewrites:
            print(f"docs: touched {fp}", file=sys.stderr)
    return 0


def _cmd_project_rename(args: argparse.Namespace) -> int:
    # Phase 5: stub. Behaviour lands in Phase 6.
    return 2


def _cmd_check(args: argparse.Namespace) -> int:
    if args.root:
        root = Path(args.root)
    elif args.dir:
        root = Path(args.dir)
    else:
        root = find_root(Path.cwd())

    if not root.exists() or not root.is_dir():
        print(f"docs: root not found: {root}", file=sys.stderr)
        return 1

    try:
        config = load_config(root)
    except tomllib.TOMLDecodeError as exc:
        print(f"docs: malformed .docs.toml: {exc}", file=sys.stderr)
        return 2

    predicate = compile_exclude_predicate(config, getattr(args, "exclude", []) or [])
    findings = check_tree(root, config, args.stale, date.today(), predicate=predicate)

    if args.json:
        print(json.dumps([finding_to_json(f, root) for f in findings], indent=2))
    elif not findings:
        print("docs: no violations found")
    else:
        current: str | None = None
        for finding in findings:
            rel = _root_relative(finding.path, root)
            if rel != current:
                if current is not None:
                    print()
                print(rel)
                current = rel
            print(f"  {finding.severity}: [{finding.rule}] {finding.message}")

    return exit_code_for(findings)


def _cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else find_root(Path.cwd())

    if not root.exists() or not root.is_dir():
        print(f"docs: root not found: {root}", file=sys.stderr)
        return 1

    try:
        config = load_config(root)
    except tomllib.TOMLDecodeError as exc:
        print(f"docs: malformed .docs.toml: {exc}", file=sys.stderr)
        return 2

    predicate = compile_exclude_predicate(config, getattr(args, "exclude", []) or [])
    docs = query_docs(
        root,
        config,
        lifecycle=args.lifecycle,
        role=args.role,
        project=args.project,
        stale=args.stale,
        today=date.today(),
        predicate=predicate,
    )

    if args.json:
        print(json.dumps([doc_to_json(d, config, root) for d in docs], indent=2))
    elif not docs:
        print("docs: no docs match")
    else:
        current: tuple[str, str] | None = None
        for doc in docs:
            group = (doc.lifecycle, doc.role)
            if group != current:
                print(f"\n{doc.lifecycle} — {doc.role}")
                current = group
            rel = _root_relative(doc.path, root)
            updated = doc.updated.strftime(config.date_format)
            print(f"  {rel}  {updated}  {doc.title}")

    return 0


def _count_preserved_fields(fm: FileMigration) -> int:
    """Return how many non-required metadata fields `migrate` will preserve.

    Re-reads the file and counts the metadata-shaped lines `apply_migration`
    would park in the file's ``## Migrated metadata`` section (see
    `_extra_metadata_fields`). Used only for the dry-run human report; 0 when
    the file carries no extra fields or has no parseable metadata block.
    """
    try:
        _t, metadata, _b = parse_metadata_block(fm.path.read_text())
    except (MetadataError, OSError):
        return 0
    return len(_extra_metadata_fields(metadata))


_AMBIGUITY_BUCKETS: tuple[tuple[str, str], ...] = (
    ("notes-fallback", "Role inferred as 'notes' fallback"),
    ("synthesised-h1", "No H1 in the file"),
    ("out-of-vocab", "is out of vocabulary"),
    ("collision", "Archive-move destination collision"),
)


def _ambiguity_bucket(note: str) -> str:
    """Map a free-form ambiguity sentence to a stable footer-summary key."""
    for key, marker in _AMBIGUITY_BUCKETS:
        if marker in note:
            return key
    return "other"


def _print_migration_plan(
    plan: MigrationPlan,
    *,
    mode: str = "default",
    only: str | None = None,
    group_by: str | None = None,
    quiet: bool = False,
) -> None:
    """Print a human-readable dry-run migration plan to stdout.

    M8 (F6) widens the signature with three triage kwargs:

    - ``mode``: ``"default"`` (verbose per-file block) or ``"summary"``
      (one ``path  role  conf  notes`` line per file).
    - ``only``: ``None`` (no filter) or ``"ambiguous"`` (drop high-
      confidence-no-ambiguity rows).
    - ``group_by``: ``None`` / ``"role"`` / ``"confidence"``.

    Both modes emit the F3 excluded-count footer (`<N> files excluded under
    <prefix>`), the F7 non-md sibling footer, and the default footer
    summary (`summary:` / `roles:` / `confidence:` / `ambiguities:`),
    all printed AFTER the per-file block per OQ3 (consistent placement;
    operator pipes through `less` or scrolls back). Footer ordering:
    excluded counts → non-md siblings → multi-project hints → default
    summary.
    """
    # M10 (OQ-B): `--apply --quiet` suppresses the per-file body entirely.
    # Footer / per-file output are both gated; caller picks `_cmd_migrate`'s
    # default branch only. JSON / summary modes are requested outputs and
    # never call this with quiet=True. The guard sits above EVERY downstream
    # print (including the F11 normalisation announcement) so `--apply
    # --quiet` is byte-empty on stdout for every tree shape.
    if quiet:
        return

    # F11: when project normalisation changed the inferred value, print
    # the annotation ONCE at the top so per-file lines stay flat.
    if plan.project_original is not None and plan.files:
        print(f'project: {plan.files[0].project} (normalised from "{plan.project_original}")')
        print()

    # Triage filters apply equally to both modes.
    files: list[FileMigration] = list(plan.files)
    if only == "ambiguous":
        files = [fm for fm in files if fm.ambiguities]
    if group_by == "role":
        files = sorted(files, key=lambda fm: (fm.role, fm.rel))
    elif group_by == "confidence":
        order: dict[Confidence, int] = {
            Confidence.HIGH: 0,
            Confidence.MEDIUM: 1,
            Confidence.LOW: 2,
        }
        files = sorted(files, key=lambda fm: (order.get(fm.confidence, 99), fm.rel))

    if mode == "summary":
        # Compact one-line-per-file view for triage. Columns:
        #   path<60> role<12> confidence<8> notes
        for fm in files:
            notes = "; ".join(fm.ambiguities) if fm.ambiguities else "-"
            print(f"{fm.rel:<60} {fm.role:<12} {fm.confidence.value:<8} {notes}")
        if files:
            print()
    else:
        for fm in files:
            print(fm.rel)
            print(f"  role: {fm.role}    project: {fm.project}    lifecycle: {fm.lifecycle}")
            print(f"  updated: {fm.updated.isoformat()}    confidence: {fm.confidence.value}")
            if fm.archive_move is not None:
                print(f"  archive move: -> {fm.archive_move}")
            if fm.synthesized_h1:
                print("  synthesized H1: yes (title from filename)")
            if fm.reconciled_metadata:
                preserved = _count_preserved_fields(fm)
                if preserved:
                    print(
                        f"  reconciled metadata: yes (pre-existing lines folded in; "
                        f"{preserved} extra field(s) preserved under '## Migrated metadata')"
                    )
                else:
                    print("  reconciled metadata: yes (pre-existing lines folded in)")
            for note in fm.ambiguities:
                print(f"  ambiguity: {note}")
            print()

    # --- Footer (per OQ3, all sections emit AFTER the per-file lines) -------

    # F3: one line per excluded prefix bucket.
    for prefix, count in plan.excluded_breakdown:
        print(f"{count} files excluded under {prefix}")

    # F7: non-Markdown root-sibling surfacing. Suppress per --exclude-ext;
    # the whole footer line is suppressed when the displayed list is empty.
    try:
        non_md = sorted(
            p.name
            for p in plan.root.iterdir()
            if p.is_file() and not p.name.startswith(".") and not p.name.endswith(".md")
        )
    except OSError:
        non_md = []
    suppressed_set = set(plan.suppressed_exts or ())
    displayed = [n for n in non_md if n.rsplit(".", 1)[-1].lower() not in suppressed_set]
    if displayed:
        names = ", ".join(displayed)
        print(f"{len(displayed)} non-Markdown siblings at root not considered: {names}")

    # F5: multi-project hints.
    for hint in plan.multi_project_hints:
        print(hint)

    # F6 default footer summary — emitted unconditionally (OQ3).
    # Token-pinned by `test_default_plan_footer_shows_counts` —
    # `summary:`, `roles:`, `confidence:`, `ambiguities:` must all appear
    # in the footer slice.
    role_counts: dict[str, int] = {}
    confidence_counts: dict[Confidence, int] = {
        Confidence.HIGH: 0,
        Confidence.MEDIUM: 0,
        Confidence.LOW: 0,
    }
    ambiguity_counts: dict[str, int] = {}
    n_files = len(plan.files)
    n_ambiguous = 0
    for fm in plan.files:
        role_counts[fm.role] = role_counts.get(fm.role, 0) + 1
        confidence_counts[fm.confidence] = confidence_counts.get(fm.confidence, 0) + 1
        if fm.ambiguities:
            n_ambiguous += 1
        for note in fm.ambiguities:
            bucket = _ambiguity_bucket(note)
            ambiguity_counts[bucket] = ambiguity_counts.get(bucket, 0) + 1

    print(
        f"summary: {n_files} files; {n_ambiguous} ambiguous "
        f"(low={confidence_counts[Confidence.LOW]}, "
        f"medium={confidence_counts[Confidence.MEDIUM]}, "
        f"high={confidence_counts[Confidence.HIGH]})"
    )
    roles_token = " ".join(f"{r}={c}" for r, c in sorted(role_counts.items()))
    print(f"roles: {roles_token if roles_token else '-'}")
    conf_token = " ".join(
        f"{c.value}={confidence_counts[c]}"
        for c in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    )
    print(f"confidence: {conf_token}")
    if ambiguity_counts:
        amb_token = " ".join(f"{k}={v}" for k, v in sorted(ambiguity_counts.items()))
        print(f"ambiguities: {amb_token}")
    else:
        print("ambiguities: none")


def _cmd_migrate(args: argparse.Namespace) -> int:
    target = Path(args.dir)
    if not target.is_dir():
        print(f"docs: directory not found: {target}", file=sys.stderr)
        return 2

    # `migrate` refuses a directory whose `.docs.toml` carries the
    # managed-root marker sections (`[project]`, `[archive]`, or
    # `[vocabulary]`) — that tree is for index / check / list, and
    # re-inserting blocks could duplicate metadata. M7 (OQ5) narrows the
    # refusal: a sidecar `.docs.toml` containing ONLY a `[migrate]`
    # section is a foreign-tree migration hint (e.g. `[migrate]
    # project_name = "foo-bar"`) and is read without refusing.
    # M8 (OQ1) extends the carve-out further: when `[exclude]` is
    # present, the refusal is waived even alongside managed markers.
    # Rationale: `[exclude]` is the operator's explicit signal "use
    # migrate to triage / re-migrate this tree but skip the listed
    # paths" — a legitimate operation on a managed tree. The walker
    # itself is idempotent for already-conformant files (it leaves
    # them untouched on --apply), so the M7 "could duplicate metadata"
    # concern doesn't fire on a managed tree that's already conformant.
    toml_path = target / ".docs.toml"
    if toml_path.is_file():
        try:
            data = tomllib.loads(toml_path.read_text())
        except tomllib.TOMLDecodeError as exc:
            print(f"docs: malformed .docs.toml: {exc}", file=sys.stderr)
            return 2
        managed_sections = {"project", "archive", "vocabulary"}
        if managed_sections & data.keys() and "exclude" not in data:
            print(
                f"docs: {target} is already a docs root (.docs.toml has "
                f"{sorted(managed_sections & data.keys())!r}) — "
                "migrate is for foreign trees; use index / check / list instead.",
                file=sys.stderr,
            )
            return 2

    if args.date:
        try:
            parse_date(args.date, "%Y-%m-%d")
        except MetadataError as exc:
            print(f"docs: --date: {exc}", file=sys.stderr)
            return 2
        # `args.date` explicitly set ⇒ override per-file dates globally
        # (M4 semantics retained).
        date_str: str | None = args.date
    else:
        # Absent ⇒ F4: plan_migration picks the per-file Updated:/mtime
        # date for each archive move.
        date_str = None

    # M8 (F3 + F7): parse `--exclude-ext` once; thread the tuple into both
    # the predicate (so .xlsx/.html files never participate in the plan)
    # and into the printer (so the non-md sibling footer suppresses them).
    cli_exclude_exts: tuple[str, ...] = tuple(
        s.strip() for s in (args.exclude_ext or "").split(",") if s.strip()
    )
    cli_excludes: tuple[str, ...] = tuple(getattr(args, "exclude", []) or [])

    try:
        plan = plan_migration(
            target,
            date_str,
            cli_config_project=args.config_project,
            cli_excludes=cli_excludes,
            cli_exclude_exts=cli_exclude_exts,
        )
        if args.apply:
            apply_migration(plan)
    except (MetadataError, VocabularyError, OSError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 2

    if args.json:
        # JSON is a requested output — `--quiet` never suppresses it.
        print(json.dumps(migration_to_json(plan), indent=2))
    elif args.summary:
        # `--summary` is a requested output — `--quiet` does not suppress
        # the compact block (OQ-B's scope is per-file plan chatter only).
        _print_migration_plan(plan, mode="summary", only=args.only, group_by=args.group_by)
    else:
        # Default (verbose) plan is per-file chatter — gated by
        # `--apply --quiet` per OQ-B. Dry-run + `--quiet` still emits the
        # plan because the plan IS the requested output.
        _print_migration_plan(
            plan,
            mode="default",
            only=args.only,
            group_by=args.group_by,
            quiet=(args.apply and args.quiet),
        )

    if args.apply and not args.quiet:
        moves = sum(1 for fm in plan.files if fm.archive_move is not None)
        print(
            f"docs: migrated {len(plan.files)} file(s) under {target} ({moves} archive move(s))",
            file=sys.stderr,
        )
    return 0


# ---------------------------------------------------------------------------
# `docs install-skill` materialises the bundled Claude Code skill onto a host.
# ---------------------------------------------------------------------------


# Files the bundled skill is allowed to contain. Pinned by
# tests/test_skill.py's "no clutter" check; we list them here so the
# materialisation step copies exactly the supported surface.
_SKILL_RELATIVE_FILES: tuple[Path, ...] = (
    Path("SKILL.md"),
    Path("references") / "convention.md",
    Path("references") / "cli.md",
    # M8 (F8) additions + the M5-era pre-existing use-cases.md that
    # `install-skill --copy` previously missed (it walked the bundle
    # via this very tuple, so a file not in the tuple silently shipped
    # in the wheel but never landed at the host).
    Path("references") / "use-cases.md",
    Path("references") / "adoption-playbook.md",
    Path("references") / "docs-toml-template.toml",
)


def _locate_bundled_skill() -> Path:
    """Return the absolute path to the bundled `docs_cli/skill/` directory.

    Uses ``importlib.resources.files`` so the lookup works for both the
    editable install (path points back into ``src/docs_cli/skill/``) and
    the wheel install (path points into the venv's
    ``site-packages/docs_cli/skill/``). The return is a real
    ``pathlib.Path``; ``importlib.resources`` may return an abstract
    ``Traversable`` for namespace packages, but ``docs_cli`` is a real
    on-disk package in both deployment shapes.
    """
    base = importlib.resources.files("docs_cli") / "skill"
    return Path(str(base))


def _running_from_wheel_install(source: Path) -> bool:
    """True iff the bundled source lives under a `site-packages` directory.

    The heuristic intentionally matches both regular venv installs
    (`.venv/lib/python3.x/site-packages/docs_cli/skill`) and user-site
    installs (`~/.local/lib/python3.x/site-packages/docs_cli/skill`).
    An editable install resolves back to the in-tree
    `src/docs_cli/skill/`, which has no `site-packages` ancestor.
    """
    return any(part == "site-packages" for part in source.resolve().parts)


def _trees_byte_identical(src: Path, dest: Path) -> bool:
    """True iff every file listed in ``_SKILL_RELATIVE_FILES`` exists at
    ``dest`` with the same byte contents as at ``src``.

    Used to decide whether a populated destination is a clean no-op
    (skip) or a real conflict (refuse, unless --force).
    """
    for rel in _SKILL_RELATIVE_FILES:
        src_file = src / rel
        dst_file = dest / rel
        if not dst_file.exists():
            return False
        if src_file.read_bytes() != dst_file.read_bytes():
            return False
    return True


def _cmd_install_skill(args: argparse.Namespace) -> int:
    """Materialise the bundled `docs` skill onto the host.

    Exit codes:
        0 — success (copy/symlink performed, or destination already
            byte-identical so this is a no-op).
        2 — refusal: destination exists with non-identical content and
            ``--force`` was not supplied, or ``--symlink`` was requested
            from a wheel install.
    """
    dest = Path(os.path.expanduser(args.dest)).resolve()
    source = _locate_bundled_skill()

    # Wheel-install symlink refusal (Q3 — site-packages ancestor heuristic).
    if args.mode == "symlink" and _running_from_wheel_install(source):
        print(
            "docs: install-skill --symlink is rejected for wheel installs "
            "(the bundled skill lives under site-packages and may be replaced "
            "by a future `pip install --upgrade docs-cli`). Use an editable "
            "install (`pip install -e .`) or drop --symlink for the default "
            "--copy.",
            file=sys.stderr,
        )
        return 2

    # No-op fast path: dest already matches the bundled source byte-for-byte.
    if dest.exists() and _trees_byte_identical(source, dest):
        if not args.quiet:
            print(
                f"docs: install-skill: {dest} already matches the bundled skill; no-op.",
                file=sys.stderr,
            )
        return 0

    # Conflict: dest exists with different content and --force was not given.
    if dest.exists() and not args.force:
        print(
            f"docs: install-skill: destination {dest} exists with content that "
            "differs from the bundled skill. Re-run with --force to overwrite. "
            "(Use --dest <DIR> to install elsewhere.)",
            file=sys.stderr,
        )
        return 2

    # If we're here, either dest does not exist or --force is set. Ensure a
    # clean slate before writing so partial leftovers from a previous attempt
    # do not contaminate the materialised tree.
    if dest.exists():
        if dest.is_symlink() or dest.is_file():
            dest.unlink()
        else:
            shutil.rmtree(dest)

    if args.mode == "symlink":
        # Editable install: point dest at the source directory.
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(source, target_is_directory=True)
        if not args.quiet:
            print(
                f"docs: install-skill: symlinked {dest} -> {source}",
                file=sys.stderr,
            )
        return 0

    # Copy mode (default). Walk the supported file set explicitly rather than
    # blanket-copying the source dir; this matches the
    # `_SKILL_RELATIVE_FILES` allowlist that the no-clutter test pins.
    dest.mkdir(parents=True, exist_ok=True)
    for rel in _SKILL_RELATIVE_FILES:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / rel, target)
    if not args.quiet:
        print(
            f"docs: install-skill: copied bundled skill to {dest}",
            file=sys.stderr,
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns the process exit code.

    Subcommands:
        index — regenerate INDEX.md from metadata in the docs root (M1).
        new, archive, mv, touch — mutating verbs (M2).
        check, list — validation and query verbs (M3).
        migrate — adopt a non-conforming foreign directory (M4).
        install-skill — materialise the bundled Claude Code skill (M6).

    Exit codes (per cli.md):
        0 — success (or warnings-only on `check`).
        1 — recoverable error (file conflict, validation warning,
            missing input).
        2 — hard error (invalid vocab, atomic-operation failure,
            validation errors).
    """
    args = _build_parser().parse_args(argv)
    if args.command == "index":
        return _cmd_index(args)
    if args.command == "new":
        return _cmd_new(args)
    if args.command == "archive":
        return _cmd_archive(args)
    if args.command == "mv":
        return _cmd_mv(args)
    if args.command == "touch":
        return _cmd_touch(args)
    if args.command == "check":
        return _cmd_check(args)
    if args.command == "list":
        return _cmd_list(args)
    if args.command == "migrate":
        return _cmd_migrate(args)
    if args.command == "install-skill":
        return _cmd_install_skill(args)
    if args.command == "project":
        if args.project_command == "rename":
            return _cmd_project_rename(args)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
