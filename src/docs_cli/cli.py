#!/usr/bin/env python3
"""docs — prescriptive CLI for managing trees of structured Markdown docs.

See `docs/` (relative to repo root) for the full specification:

- convention.md      on-disk Markdown convention this tool reads/writes
- cli.md             command surface
- architecture.md    module sketch, data flow, INDEX renderer format

The single-file module is exposed as the ``docs`` console-script via
the ``docs_cli.cli:main`` entry point declared in ``pyproject.toml``.
The agent skill ships alongside under ``docs_cli/skill/`` and is
materialised onto a host via the ``docs install-skill`` verb.

M1: parser, walker, renderer, `docs index`, config loading. M2 adds the
mutating verbs `new`, `archive`, `mv`, and `touch`. M3 adds the
validation and query verbs `check` and `list`, and regroups the INDEX
by Project then Role. M4 adds the migration verb `migrate`, which adopts
a non-conforming foreign directory into the convention. M6 packages the
CLI as `docs-cli` on PyPI and adds the `install-skill` verb. M25 makes a
one-sided reciprocal `Related:` edge a hard `check` error and adds the
`relate add|remove` repair verb. M26 separates relationship context from
archive authorization: `archive` retires bare `--cascade` / `--interactive`,
previews the whole one-hop neighborhood under `--cascade-dry-run`, requires
an explicit `--cascade-only GLOB` — validated as one complete plan before
the first byte moves — for any related-document write, and emits that plan
as a `--json` record. M27 adds a pure, stdlib-only Markdown body-link
scanner and makes an unresolved (`broken-body-link`) or escaping
(`outside-root-body-link`) local body-link destination a hard `check` error.
"""

from __future__ import annotations

import argparse
import contextlib
import difflib
import enum
import importlib.metadata
import importlib.resources
import json
import os
import posixpath
import re
import shutil
import string
import sys
import tomllib
import urllib.parse

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

from docs_cli import update_check

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

# M25 (D1): the recognized reciprocal relationship verbs. Each key maps to
# the verb the OTHER endpoint must declare back. The map is symmetric —
# applying it twice is the identity — and matching is case-sensitive exact
# (the `add_fields` precedent), so `Precedes` is a free-form verb, not a
# recognized one. Every other `Related:` verb (`pairs-with`, `child-of` /
# `parent-of`, `supersedes` / `superseded-by`, a user's own) stays free-form
# and gains NO reciprocal validation: promoting them would retroactively
# break existing trees for no navigational gain.
RECIPROCAL_INVERSES: Mapping[str, str] = {
    "precedes": "follows",
    "follows": "precedes",
    "depends-on": "required-by",
    "required-by": "depends-on",
    "blocks": "blocked-by",
    "blocked-by": "blocks",
}
RECIPROCAL_VERBS: frozenset[str] = frozenset(RECIPROCAL_INVERSES)

# M26 (D3/D7): the machine-stable `exclusion_reason` values a
# `docs archive --json` candidate record can carry. `not-selected` is not an
# ineligibility — it marks an eligible candidate the scope did not select (or
# that had no scope to select it); the other three are the ineligibilities,
# reported by the precedence `outside-root`, `already-archived`,
# `unresolved-target` when more than one holds.
ARCHIVE_EXCLUSION_REASONS: frozenset[str] = frozenset(
    {"not-selected", "already-archived", "unresolved-target", "outside-root"}
)

# M27 (D1/D2): the closed vocabularies of the body-link scanner. `BodyLink.kind`
# names the Markdown form a destination was written in — a third member would
# mean a grammar change, not a tweak. `classify_destination` returns a
# `DESTINATION_KINDS` member and only `local` is ever resolved or reported.
# `MAX_DESTINATION_PAREN_DEPTH` bounds how deep balanced parentheses may nest
# inside a plain destination; it is a docs-cli bounded-scanner bound, NOT a
# CommonMark conformance claim (D1 licenses that framing).
BODY_LINK_KINDS: frozenset[str] = frozenset({"inline", "reference-definition"})
DESTINATION_KINDS: frozenset[str] = frozenset(
    {"local", "empty", "fragment", "scheme", "protocol-relative", "root-absolute"}
)
MAX_DESTINATION_PAREN_DEPTH: int = 3

# M10 (OQ-O + OQ-P): metadata labels the `unknown-field` check rule
# treats as built-in — always allowed regardless of the
# `[vocabulary] add_fields` configuration. Covers the required fields
# (`Lifecycle`, `Role`, `Project`, `Updated`), the relationship label
# (`Related:`, a bare-label-with-bullet container that is structurally
# required by parts of the convention), and the documented
# archive-time hint label (`Archived-reason:`, written by
# `docs archive --reason`). User-extensible metadata vocabulary lives
# on `Config.fields` (sourced from `[vocabulary] add_fields`).
#
# M25 (D4) adds `Revision:` — the repeatable audit group `docs relate`
# itself writes onto an archived endpoint. A label the tool writes must
# never trip the tool's own allowlist warning, so it joins the built-in
# always-allowed set rather than requiring every tree with an
# `add_fields` allowlist to list it.
_BUILTIN_METADATA_FIELDS: frozenset[str] = frozenset(
    {"Lifecycle", "Role", "Project", "Updated", "Related", "Archived-reason", "Revision"}
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


class CoordinatedWriteError(OSError):
    """A coordinated multi-file publish failed (M25 — D5; M26 — D4).

    ``str(exc)`` is the fully-rendered operator-facing detail; the calling
    verb prints it as ``docs: <verb>: <exc>``. Two producers:

    - `docs relate` (M25 — D5): every stage-3/4/5 failure of the two-file
      coordinated publish — for the pre-write stages ``rolled_back`` is
      True because the tree is (trivially) unchanged.
    - `docs archive` (M26 — D4): every pre-flight refusal (``rolled_back``
      True, ``published`` empty — nothing was written) and the residual
      mid-execution partial-state admission (``rolled_back`` False,
      ``published`` naming what really moved).

    Attributes:
        rolled_back: True iff the tree is byte-identical to its pre-publish
            state — i.e. nothing was published, or every published endpoint
            was restored.
        published: Root-relative POSIX paths successfully published before
            the failure, in publish order.
        exit_code: The process exit code the calling verb returns. Defaults
            to 2, which is every `docs relate` failure and every NEW M26
            refusal. `preflight_archive_plan` overrides it with 1 for the
            two conditions 1.x already assigned that code — a plan member
            with no editable metadata block, and an occupied destination
            slot — because `cli.md`'s exit-code matrix pins them and they
            must not silently change meaning (M26 — Phase-1 Q4).
    """

    def __init__(
        self,
        message: str,
        *,
        rolled_back: bool,
        published: tuple[str, ...],
        exit_code: int = 2,
    ) -> None:
        super().__init__(message)
        self.rolled_back = rolled_back
        self.published = published
        self.exit_code = exit_code


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

    M19 (D2) adds ``stale_days`` — the per-tree default stale window
    sourced from the ``[check]`` table's ``stale_days`` key. When set,
    it supplies the window to ``docs check`` and ``docs touch --check``
    whenever no explicit CLI ``--stale`` is given; absent (``None``) →
    no default window (today's behaviour). The key is check-scoped — it
    does NOT feed ``docs list --stale``.

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
        stale_days = None
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
    stale_days: int | None = None

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
            ``stale``, ``malformed``, ``unknown-field`` (M10),
            ``medium-confidence-inference`` (`docs migrate --triage`),
            ``duplicate-field`` / ``missing-inverse`` (M25), or
            ``broken-body-link`` / ``outside-root-body-link`` (M27).
            Emitted in ``--json`` output so CI
            hooks can filter on it. The JSON record's key set is closed at
            ``{path, severity, rule, message}``; a new rule adds a value
            here, never a field there.
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


@dataclass(frozen=True)
class RelateEdit:
    """One endpoint's half of a `docs relate` operation (M25 — D3).

    Produced by `plan_relate`, consumed by `apply_relate_plan` and
    `relate_plan_to_json`. Mirrors `FileMigration`'s role inside a
    `MigrationPlan`: a fully-staged, write-free description of exactly
    what this one file's bytes would become.

    Attributes:
        path: Absolute path of the endpoint.
        rel: Its root-relative POSIX path — the form every human message
            and JSON field names, whatever spelling was typed.
        archived: True iff `rel` lies under the configured archive
            subtree. Drives the D4 audit rules.
        edge: The `<verb>: <other-rel>` bullet body as written in THIS
            document — the forward verb for the source, its inverse for
            the target.
        original: The endpoint's text on disk at planning time.
        new_text: The complete staged text. Equal to `original` when
            nothing changes.
        change: ``"added"`` / ``"removed"`` / ``"unchanged"``.
            ``change != "unchanged"`` is the "did this endpoint move"
            predicate everywhere.
        present_before: True iff `edge` was already declared before.
        present_after: True iff `edge` is declared in `new_text`.
        updated_bumped: True iff `Updated:` was rewritten — only ever on
            an endpoint whose bytes change.
        revision_appended: True iff a `Revision:` bullet was appended —
            only ever on an archived endpoint that really mutated (D4's
            audit asymmetry).
    """

    path: Path
    rel: str
    archived: bool
    edge: str
    original: str
    new_text: str
    change: str
    present_before: bool
    present_after: bool
    updated_bumped: bool
    revision_appended: bool


@dataclass(frozen=True)
class RelatePlan:
    """A complete, write-free `docs relate add|remove` operation (M25 — D3).

    The `MigrationPlan` analogue for the relationship verbs: `plan_relate`
    builds it by reading both endpoints, `apply_relate_plan` publishes it,
    and `relate_plan_to_json` renders the `--json` operation record. The
    same object backs a `--dry-run` preview and a real apply, which is why
    the two are diffable.

    Attributes:
        action: ``"add"`` or ``"remove"``.
        verb: The recognized verb as typed.
        inverse: `verb`'s recognized inverse (`inverse_verb`).
        source_rel / target_rel: Root-relative POSIX endpoint paths.
        reason: The `--reason` value, or None. Required by the CLI
            whenever either endpoint is archived; accepted but unused on
            an all-active pair.
        date_str: The date written into `Updated:` and any `Revision:`
            bullet, already rendered in the tree's `date_format`.
        edits: Always exactly two, ``(source, target)`` in that order.
    """

    action: str
    verb: str
    inverse: str
    source_rel: str
    target_rel: str
    reason: str | None
    date_str: str
    edits: tuple[RelateEdit, ...]


@dataclass(frozen=True)
class ArchiveMove:
    """One document's place in a `docs archive` operation plan (M26 — D3/D4).

    The `RelateEdit` analogue for the archive verb: an immutable,
    write-free description of one document — the primary or one one-hop
    candidate — and what the plan intends to do with it. Produced by
    `archive_candidates` / `plan_archive`, consumed by
    `preflight_archive_plan`, `apply_archive_plan`, `_print_archive_lines`,
    and `archive_plan_to_json`.

    Attributes:
        path: Absolute source path. For an `outside-root` candidate this is
            ``root / <escaping rel>`` — a path that does not lie under
            `root` at all. Harmless: an ineligible member is never opened,
            never pre-flighted, and never written.
        rel: The canonical root-relative POSIX path
            (`_canonical_related_target`), which is the identity the set is
            deduplicated on, the form `--cascade-only` matches against, and
            the form every human message and JSON field names.
        aliases: Every declared `Related:` spelling that resolves to `rel`,
            in declaration order (e.g. ``("./b.md", "b.md")``). Empty for
            the primary, which is named on the command line rather than
            declared by an edge. Load-bearing: `_rewrite_referring_edges`
            rewrites a bullet iff its target EXACTLY equals an `old_rel`,
            so `apply_archive_plan` returns one pair per alias.
        verb: The discovering verb — `pairs-with` or `child-of`, first
            declaration winning. None for the primary.
        dest / dest_rel: The absolute and canonical root-relative archive
            destination. Both are None until `plan_archive` fills them, and
            it fills them for SELECTED members only — `archive_candidates`
            takes no date, so it cannot compute a destination at all.
        selected: True iff this member will be written. Always True for the
            primary.
        exclusion_reason: None iff `selected`; otherwise one of
            `ARCHIVE_EXCLUSION_REASONS`.
    """

    path: Path
    rel: str
    aliases: tuple[str, ...]
    verb: str | None
    dest: Path | None
    dest_rel: str | None
    selected: bool
    exclusion_reason: str | None


@dataclass(frozen=True)
class ArchivePlan:
    """A complete, write-free `docs archive` operation (M26 — D4).

    The `RelatePlan` analogue for the archive verb: `plan_archive` builds
    it by reading the primary's declared edges, `preflight_archive_plan`
    proves every member writable before a byte moves, `apply_archive_plan`
    executes it, and `archive_plan_to_json` renders the `--json` record.
    The same object backs a `--cascade-dry-run` preview and a real apply,
    which is why the two are diffable.

    Attributes:
        root: The resolved docs root.
        config: The tree's config (supplies `archive_dir`).
        primary: The named document. Always `selected`, always destined.
        candidates: The whole deduplicated one-hop set in `Related:`
            declaration order — selected, not-selected, and ineligible
            alike. Present in every mode, because the `--json` record
            carries the whole neighborhood even when the prose stays quiet
            about it (D1 / Phase-1 Q14).
        scope: The `--cascade-only` value exactly as typed, or None.
        date_str: The archive date, already in the tree's `date_format`.
        reason: The `--reason` value, or None. Applies to the PRIMARY only
            (D1 / Phase-1 Q10).
        source: The `FILE` argument EXACTLY as typed — a relative argument
            stays relative. Threaded onto the plan because
            `archive_plan_to_json` only ever sees the plan, and
            ``str(primary.path)`` is always absolute.
    """

    root: Path
    config: Config
    primary: ArchiveMove
    candidates: tuple[ArchiveMove, ...]
    scope: str | None
    date_str: str
    reason: str | None
    source: str

    @property
    def moves(self) -> tuple[ArchiveMove, ...]:
        """The members that will be written: the primary, then the selected.

        Primary first is contractual — it is the order `apply_archive_plan`
        executes in, so the partial-state admission's "archived / still at
        their original paths" split reads in execution order.
        """
        return (self.primary, *(c for c in self.candidates if c.selected))


@dataclass(frozen=True)
class BodyLink:
    """One recognised Markdown body-link destination occurrence (M27 — D5).

    `scan_body_links` produces these; `body_link_findings` validates the
    `local` ones. **M28 is the other consumer**: it rewrites destinations when
    a document moves, by splicing a replacement into `[start, end)` and copying
    every other byte. Two properties make that safe and are frozen:

    - ``text[start:end] == raw`` — the span IS the destination token. It
      includes the ``<…>`` angle brackets when the destination has them and
      excludes any title, so a replacement containing a space lands inside the
      delimiters rather than outside them.
    - the record is frozen. M28 collects spans and then splices; an in-place
      edit of `raw` or `start` between those two steps would silently
      invalidate every remaining span in the same document, so mutation is a
      `TypeError` at the moment of the mistake instead of a corrupted rewrite.

    Attributes:
        kind: A `BODY_LINK_KINDS` member — the Markdown form the destination
            was written in. Both rules and both message templates are
            otherwise identical: the kind lives here, never in a `Finding`.
        line: 1-based line of the destination token's first character.
        column: 1-based column of that same character.
        raw: The destination token EXACTLY as written — angle brackets,
            percent-escapes and backslash escapes included. This is what a
            finding reports, so the author can find what they typed.
        path: The path part: a surrounding ``<…>`` pair stripped, the fragment
            removed, then backslash-unescaped and percent-decoded. This is
            what resolution runs on.
        fragment: Everything after the FIRST ``#``, without the ``#``, carried
            verbatim (neither unescaped nor decoded, because nothing ever
            resolves it). None when the destination carries no ``#``.
        start: Offset of the token's first character into the ORIGINAL text.
        end: One past the token's last character.
    """

    kind: str
    line: int
    column: int
    raw: str
    path: str
    fragment: str | None
    start: int
    end: int


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


def inverse_verb(verb: str) -> str | None:
    """Return `verb`'s recognized reciprocal inverse, or None (M25 — D1).

    Case-sensitive exact match, mirroring the `add_fields` precedent:
    `Precedes` is a free-form verb, not a recognized one. A None result is
    the single "this verb gains no reciprocal validation" signal shared by
    `reciprocity_findings` (skip it) and `_cmd_relate` (refuse it).
    """
    return RECIPROCAL_INVERSES.get(verb)


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
    """Write `content` to `path` atomically via tmpfile + fsync + rename.

    POSIX-atomic on the same filesystem. Cross-filesystem renames fall back
    to a copy + unlink under the hood (`Path.replace` handles that).

    M14 (A5): durability — the tmpfile's bytes are `os.fsync`'d before the
    rename, and the parent directory is `os.fsync`'d after, so the rename
    that publishes the new name is itself persisted (flushing the file's
    bytes alone does not durably record the directory entry). The
    parent-dir fsync is wrapped in `try/except OSError` for portability
    (Windows / filesystems that disallow directory fds). Content is
    encoded UTF-8 so the on-disk bytes match `Path.write_text`'s default
    (golden byte-equality tests rely on this).
    """
    tmp = path.with_suffix(path.suffix + ".docs-tmp")
    data = content.encode()
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        # Write-all loop: a single os.write may short-write, so keep
        # writing until every byte lands (PEP 475 handles EINTR retries).
        written = 0
        while written < len(data):
            written += os.write(fd, data[written:])
        os.fsync(fd)
    finally:
        os.close(fd)
    tmp.replace(path)
    # Persist the rename itself: fsync the parent directory entry. Best
    # effort — some platforms/filesystems reject opening a directory for
    # fsync, in which case the rename is still atomic, just not flushed.
    try:
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError:
        pass


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
    # `parse_metadata_block`, `validate_lifecycle`, `validate_role`, and
    # `parse_date` all raise without a path prefix (they're path-agnostic
    # helpers). Honour MetadataError's docstring ("includes the file path")
    # by tagging any bare message with `path:` here, so every caller gets
    # a self-locating error and no caller needs to re-scan the tree to
    # recover the offending file.
    try:
        title, metadata, body = parse_metadata_block(text)
    except MetadataError as exc:
        raise MetadataError(f"{path}: {exc}") from exc

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

    try:
        validate_lifecycle(lifecycle, BUILTIN_STATUSES)
        validate_role(role, BUILTIN_ROLES)
        updated = parse_date(updated_raw)
    except MetadataError as exc:
        raise MetadataError(f"{path}: {exc}") from exc
    except VocabularyError as exc:
        raise VocabularyError(f"{path}: {exc}") from exc

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

    M19 (D2) also reads the optional ``[check]`` section's ``stale_days``
    key into ``Config.stale_days`` — the per-tree default stale window for
    ``docs check`` / ``docs touch --check`` (absent → ``None``).

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
    check_section = data.get("check", {})

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

    # M19 (D2; OQ-1 amended by Step-2 review): `[check] stale_days` is the
    # per-tree default stale window. Unlike `add_roles` / `project_name` —
    # which sibling reads coerce via `frozenset()` / `tuple()` and so never
    # crash — `stale_days` is stored raw and flows straight into check_doc's
    # `(today - updated).days > stale` comparison, where a non-int (e.g. a TOML
    # string `stale_days = "14"`) raises an uncaught TypeError traceback. A
    # traceback on malformed config is a bug, so refuse it here: a present-but-
    # non-int value fails the config load like any other malformed `.docs.toml`
    # condition (the callers' `except tomllib.TOMLDecodeError` → exit 2 with the
    # `docs: malformed .docs.toml:` prefix). `bool` is excluded explicitly
    # because `isinstance(True, int)` is True in Python — TOML `stale_days =
    # true` would otherwise slip through. Negative ints stay honoured
    # (aggressive-but-graceful, mirroring the `--stale 0` precedent).
    stale_days = check_section.get("stale_days")
    if stale_days is not None and not (
        isinstance(stale_days, int) and not isinstance(stale_days, bool)
    ):
        raise tomllib.TOMLDecodeError("[check] stale_days must be an integer")

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
        stale_days=stale_days,
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


def _bare_label_run(lines: list[str], start: int, end: int, label: str) -> tuple[int, int] | None:
    """Locate a bare-label group (`Related:`, `Revision:`) in a metadata-block span.

    Returns ``(label_idx, run_end)`` — the index of the bare ``<label>:`` line
    and the index one past its last `- ` bullet — or None when the group is
    absent. Uses the same label idiom `rewrite_related_refs` does, so the
    three M25 editors and `mv`'s rewriter agree on where a group is; it is
    called for both bare-label groups M25 touches, so `Related:` and
    `Revision:` can never drift apart on what "the group" means.
    """
    for idx in range(start, end):
        m = _LABEL_RE.match(lines[idx])
        if m and m.group(1) == label and not m.group(2).strip():
            run_end = idx + 1
            while run_end < end and lines[run_end].startswith("- "):
                run_end += 1
            return idx, run_end
    return None


def _bullet_matches(line: str, verb: str, target: str) -> bool:
    """True iff the `- <verb>: <target>` bullet `line` is that exact edge.

    Targets are compared CANONICALLY (M25 — D2 amendment B), so
    `- precedes: ./b.md` is the same edge as `- precedes: b.md`. Without
    this, `docs relate add` would append a duplicate bullet on exactly the
    loosely-spelled trees the canonical-matching amendment exists to
    tolerate — i.e. `relate` would stop being idempotent there.
    """
    verb_part, sep, target_part = line[2:].partition(":")
    if not sep:
        return False
    return verb_part.strip() == verb and _canonical_related_target(
        target_part.strip()
    ) == _canonical_related_target(target)


def _preserve_tail(original: str, edited: str) -> str:
    """Restore `original`'s trailing-newline state on `edited` (M25).

    The three `Related:` / `Revision:` editors insert and delete whole
    newline-terminated lines. When the metadata block runs to EOF — a doc
    with no body — the insertion point IS the tail, so a file that lacked a
    trailing newline would silently gain one (and a deletion that removes
    the unterminated final line would leave the new last line terminated).

    That would break the M2 surgical contract's trailing-newline promise and,
    more importantly, D4's "these are the ONLY bytes an archived endpoint may
    change". Exactly one trailing newline is removed, never more.
    """
    if original.endswith(("\n", "\r")) or not edited.endswith("\n"):
        return edited
    return edited[:-1]


def add_related_edge(text: str, verb: str, target: str) -> tuple[str, bool]:
    """Ensure `text` carries `- <verb>: <target>` in its `Related:` group.

    Appends the bullet at the END of the existing `Related:` run (never
    after a trailing `Revision:` group), or creates a blank-line-separated
    `Related:` group at the end of the metadata block when absent. Returns
    ``(new_text, changed)``; an already-present edge returns
    ``(text, False)``.

    The M2 surgical minimal-diff contract: exactly one line is inserted (or
    three, when the group is created); every other byte, and the file's
    trailing-newline state, is preserved. Nothing is reflowed, re-sorted, or
    blank-line-normalised.

    Raises:
        MetadataError: `text` has no H1 / metadata block.
    """
    lines, _title, start, end = _metadata_line_span(text)
    keep = text.splitlines(keepends=True)

    located = _bare_label_run(lines, start, end, "Related")
    if located is None:
        # Create the group. It must land BEFORE any trailing `Revision:`
        # group, which D4 defines as sitting at the END of the block —
        # reachable when `relate remove` drops the last recognized edge
        # (and its emptied label) and a later `relate add` re-creates it.
        insert_at = end
        revision = _bare_label_run(lines, start, end, "Revision")
        if revision is not None:
            revision_idx = revision[0]
            blank_before = revision_idx > start and lines[revision_idx - 1].strip() == ""
            insert_at = revision_idx - 1 if blank_before else revision_idx
        new_lines = ["\n", "Related:\n", f"- {verb}: {target}\n"]
    else:
        label_idx, run_end = located
        for idx in range(label_idx + 1, run_end):
            if _bullet_matches(lines[idx], verb, target):
                return text, False
        insert_at = run_end
        new_lines = [f"- {verb}: {target}\n"]

    if insert_at > 0 and not keep[insert_at - 1].endswith(("\n", "\r")):
        keep[insert_at - 1] += "\n"
    keep[insert_at:insert_at] = new_lines
    return _preserve_tail(text, "".join(keep)), True


def remove_related_edge(text: str, verb: str, target: str) -> tuple[str, bool]:
    """Remove every `- <verb>: <target>` bullet from `text`'s `Related:` group.

    Only the exact (verb, canonical-target) bullet is removed: the same verb
    at another target and the same target under another verb survive. When
    the run empties, the bare `Related:` label — and one immediately
    preceding blank line, if present — is dropped too, so the metadata block
    is left in a shape `_metadata_line_span` still accepts. Returns
    ``(new_text, changed)``.

    Raises:
        MetadataError: `text` has no H1 / metadata block.
    """
    lines, _title, start, end = _metadata_line_span(text)
    keep = text.splitlines(keepends=True)

    located = _bare_label_run(lines, start, end, "Related")
    if located is None:
        return text, False
    label_idx, run_end = located

    doomed = [
        idx for idx in range(label_idx + 1, run_end) if _bullet_matches(lines[idx], verb, target)
    ]
    if not doomed:
        return text, False

    if len(doomed) == run_end - label_idx - 1:
        # The run empties: drop the now-bare label, and the blank line that
        # separated it from the inline metadata run above it.
        doomed.append(label_idx)
        if label_idx > start and lines[label_idx - 1].strip() == "":
            doomed.append(label_idx - 1)

    for idx in sorted(doomed, reverse=True):
        del keep[idx]
    return _preserve_tail(text, "".join(keep)), True


def append_revision_entry(text: str, entry: str) -> str:
    """Append `- <entry>` to `text`'s `Revision:` group (M25 — D4).

    A repeatable bare-label group at the END of the metadata block:
    appended to the existing bullet run when the group exists (never a
    second label), otherwise created after `Related:` separated by one blank
    line — the shape `_metadata_line_span` already accepts for multi-value
    groups. Exactly one line is added when the group exists, three when it
    is created; nothing else moves.

    Raises:
        MetadataError: `text` has no H1 / metadata block.
    """
    lines, _title, start, end = _metadata_line_span(text)
    keep = text.splitlines(keepends=True)

    located = _bare_label_run(lines, start, end, "Revision")
    if located is None:
        insert_at, new_lines = end, ["\n", "Revision:\n", f"- {entry}\n"]
    else:
        insert_at, new_lines = located[1], [f"- {entry}\n"]

    if insert_at > 0 and not keep[insert_at - 1].endswith(("\n", "\r")):
        keep[insert_at - 1] += "\n"
    keep[insert_at:insert_at] = new_lines
    return _preserve_tail(text, "".join(keep))


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


def _canonical_related_target(target: str) -> str:
    """Canonical root-relative POSIX form of a `Related:` target (M25 — D2 amendment B).

    `./b.md`, `sub/../b.md`, and `b.md` are one edge. Purely lexical (no
    filesystem access, no symlink resolution) so a walked doc's rel key and a
    bullet's target compare on the same normal form. `posixpath` rather than
    `os.path` because `Related:` targets are POSIX paths on every platform.
    """
    return posixpath.normpath(target)


def _duplicate_labels(text: str) -> dict[str, int]:
    """Labels appearing more than once in `text`'s metadata block (M25 — D7).

    Returns ``{label: occurrence count}`` in first-appearance order, empty
    when every label is unique. A doc with no H1 / metadata block returns
    empty — `malformed` owns that case.

    Works on the raw label lines rather than on `parse_metadata_block`'s
    output, and it has to: that function assigns ``metadata[label] =
    tuple(values)``, so by the time the parsed mapping exists a repeated
    label has already overwritten the earlier one and every value under it
    is gone. Counting labels here is the only place the duplication is still
    observable.

    Purely structural — inline (`Updated:`) and bare (`Related:`) labels are
    counted alike, known or not. A bare label's ``- `` bullet run is skipped
    wholesale, so many bullets under ONE label never count as a duplicate:
    repeatability lives in the bullets, never in a second label.
    """
    try:
        lines, _title, start, end = _metadata_line_span(text)
    except MetadataError:
        return {}

    counts: dict[str, int] = {}
    idx = start
    while idx < end:
        m = _LABEL_RE.match(lines[idx])
        idx += 1
        if m is None:
            continue
        counts[m.group(1)] = counts.get(m.group(1), 0) + 1
        if not m.group(2).strip():
            while idx < end and lines[idx].startswith("- "):
                idx += 1
    return {label: n for label, n in counts.items() if n > 1}


def _related_pairs(
    metadata: Mapping[str, str | tuple[str, ...]],
) -> tuple[tuple[str, str], ...]:
    """`(verb, target)` pairs from a parsed metadata block's `Related:` group.

    The lenient counterpart to `parse`'s strict harvesting: a bullet with no
    colon or an empty target is skipped rather than raising, matching what
    `check_doc`'s broken-ref loop and the reciprocity pass both need — a
    validator must not itself blow up on the malformed input it is there to
    describe. Targets are returned as written; canonicalisation is the
    caller's job.
    """
    raw = metadata.get("Related")
    if raw is None:
        return ()
    entries = raw if isinstance(raw, tuple) else (raw,)
    pairs: list[tuple[str, str]] = []
    for entry in entries:
        verb, sep, target = entry.partition(":")
        target = target.strip()
        if not sep or not target:
            continue
        pairs.append((verb.strip(), target))
    return tuple(pairs)


# ---------------------------------------------------------------------------
# Markdown body links — the shared scanner (M27 — D1/D2/D5)
# ---------------------------------------------------------------------------
#
# A pure, stdlib-only scanner over a deliberately bounded, CommonMark-*shaped*
# subset. It is not a CommonMark parser and claims no conformance; what it
# recognises is exactly `cli.md` › *Markdown body-link validation*. M27
# validates; M28 rewrites. There is one scanner and there is never a second
# Markdown parser.
#
# Everything here is a pure function of the text except `body_link_findings`,
# whose only filesystem call is one `.exists()` on an already-contained,
# already-normalised candidate under the root.

_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

# D1 rule 7: a `\` followed by any ASCII punctuation character OR A SPACE
# yields that character literally; a `\` before anything else is a literal
# backslash. The space leg follows from rule 3 — a plain destination ends at
# the first *unescaped* whitespace — and is what makes `my\ doc.md` work.
_ESCAPABLE: frozenset[str] = frozenset(string.punctuation) | {" "}


def _mask_inline_spans(line: str) -> str:
    """Blank the contents of matched backtick runs within one line (D2).

    A span never crosses a line boundary, so this is called per line: one
    unpaired backtick can mask at most the rest of its own line, never the
    remainder of a 112 KB document.

    The `next_same` index is built by a single BACKWARD pass over the runs.
    The obvious alternative — scan forward from every opener looking for a
    partner — is O(line^2) on an adversarial line of unmatched runs, and the
    pathological-input runtime lock is what measures that.
    """
    runs: list[tuple[int, int]] = []
    i = 0
    while i < len(line):
        if line[i] != "`":
            i += 1
            continue
        j = i
        while j < len(line) and line[j] == "`":
            j += 1
        runs.append((i, j - i))
        i = j
    if len(runs) < 2:
        return line

    next_same: dict[int, int] = {}
    last_seen: dict[int, int] = {}
    for idx in range(len(runs) - 1, -1, -1):
        length = runs[idx][1]
        if length in last_seen:
            next_same[idx] = last_seen[length]
        last_seen[length] = idx

    chars = list(line)
    idx = 0
    while idx < len(runs):
        partner = next_same.get(idx)
        if partner is None:
            idx += 1
            continue
        for k in range(runs[idx][0] + runs[idx][1], runs[partner][0]):
            chars[k] = " "
        idx = partner + 1
    return "".join(chars)


def _mask_code(text: str) -> str:
    """Replace the CONTENTS of code with spaces, preserving every offset (D2).

    The result has the same length as `text` and a newline at every offset
    `text` has one, so every span the scanner reports is an offset into the
    ORIGINAL text. That is the guarantee M28's rewrite rests on.

    Two passes, and **the order is part of the contract**: fenced blocks
    first (line-based), then inline spans over the already-masked text, so a
    stray backtick inside a fenced block cannot open a phantom span that
    swallows real prose after the block.

    Fences: ``` and ~~~, three or more markers, 0–3 leading spaces, closed by
    the SAME character at EQUAL OR GREATER length with only whitespace after
    the marker. The whole fence line — info string included — is kept
    verbatim; only the block's contents are blanked. An UNCLOSED fence masks
    to the end of the document, matching CommonMark and matching what a reader
    actually sees.

    Nothing else is code: there is deliberately no 4-space indented-code rule
    (Q3 / E6), because every 4-space-indented link-shaped span in this
    repository is a real link in a blockquote or list continuation.
    """
    open_marker: str | None = None
    fenced: list[str] = []
    for line in text.split("\n"):
        match = _FENCE_RE.match(line)
        if open_marker is None:
            fenced.append(line)
            if match is not None:
                open_marker = match.group(1)
        elif (
            match is not None
            and match.group(1)[0] == open_marker[0]
            and len(match.group(1)) >= len(open_marker)
            and not match.group(2).strip()
        ):
            open_marker = None
            fenced.append(line)
        else:
            fenced.append(" " * len(line))
    return "\n".join(_mask_inline_spans(line) for line in fenced)


def _escape_flags(text: str) -> bytearray:
    """One flag per character: 1 where the character is backslash-escaped (D1 rule 7).

    Computed in a single forward pass so `\\\\[` reads correctly — the first
    backslash escapes the second, leaving the `[` unescaped and able to open a
    link. Every "is this delimiter real?" test in the scanner is a lookup here
    rather than a backward walk, which is what keeps the scan linear.
    """
    flags = bytearray(len(text))
    i = 0
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text) and text[i + 1] in _ESCAPABLE:
            flags[i + 1] = 1
            i += 2
        else:
            i += 1
    return flags


def _line_starts(text: str) -> list[int]:
    """Offset of every line's first character, ascending (always starts at 0)."""
    starts = [0]
    idx = text.find("\n")
    while idx != -1:
        starts.append(idx + 1)
        idx = text.find("\n", idx + 1)
    return starts


def _blank_line_starts(text: str, line_starts: list[int]) -> list[int]:
    """Offsets of the whitespace-only lines, ascending (CommonMark's blank line).

    Precomputed once per document so the per-candidate bound is a monotonic
    cursor into this list. Re-deriving the bound from scratch at each
    candidate is quadratic on a long fence-free document — one of the two
    shapes the Phase-1 linearity note names.
    """
    blanks: list[int] = []
    for idx, start in enumerate(line_starts):
        end = line_starts[idx + 1] - 1 if idx + 1 < len(line_starts) else len(text)
        if not text[start:end].strip():
            blanks.append(start)
    return blanks


def _unescape_backslashes(token: str) -> str:
    """Resolve D1 rule 7 escapes: `\\x` → `x` for escapable `x`, else a literal `\\`."""
    out: list[str] = []
    i = 0
    while i < len(token):
        if token[i] == "\\" and i + 1 < len(token) and token[i + 1] in _ESCAPABLE:
            out.append(token[i + 1])
            i += 2
        else:
            out.append(token[i])
            i += 1
    return "".join(out)


def _split_destination(raw: str) -> tuple[str, str | None]:
    """Split a destination token into `(path, fragment)` — the BINDING order.

    Strip a surrounding `<…>` pair → split on the FIRST `#` in the remaining
    **raw** text → backslash-unescape the left half → percent-decode it
    (invalid sequences pass through unchanged). The fragment is carried
    verbatim, neither unescaped nor decoded, because nothing ever resolves it.

    Three consequences are specified rather than emergent, and all three fall
    out of doing it in exactly this order in exactly one place:

    - a percent-encoded `%23` is NOT a fragment delimiter (the split already
      happened), so `plan%23x.md` is a path named `plan#x.md`;
    - a percent-encoded `%2F` IS a path separator, because decoding precedes
      the join;
    - a backslash cannot escape a `#` out of being the fragment delimiter, for
      the same reason — the split precedes unescaping.
    """
    token = raw[1:-1] if len(raw) >= 2 and raw.startswith("<") and raw.endswith(">") else raw
    path_part, sep, fragment = token.partition("#")
    return urllib.parse.unquote(_unescape_backslashes(path_part)), fragment if sep else None


def _scan_destination(
    masked: str, escaped: bytearray, pos: int, bound: int
) -> tuple[int, int] | None:
    """`(start, end)` of the destination token at/after `pos`, or None (D1 rules 3/4).

    A zero-width `(k, k)` span means an EMPTY destination: the inline form
    `[a]()` is a recognised link with an empty destination token, while the
    reference-definition form rejects it (rule 6(c)). The caller decides.

    Plain destinations end at the first unescaped whitespace or at an
    unescaped `)` at nesting depth 0. Unescaped parentheses nest and must
    balance; exceeding `MAX_DESTINATION_PAREN_DEPTH` returns None IMMEDIATELY
    rather than scanning on, which is what keeps `"[a](" * 40_000` constant
    per candidate. An angle destination is bounded at the newline for the same
    reason: an unterminated `<` must not swallow the rest of the document.
    """
    k = pos
    while k < bound and masked[k].isspace():
        k += 1
    if k >= bound:
        return (k, k)
    if masked[k] == "<" and not escaped[k]:
        eol = masked.find("\n", k)
        stop = bound if eol == -1 else min(bound, eol)
        j = k + 1
        while j < stop:
            if masked[j] == ">" and not escaped[j]:
                return (k, j + 1)
            j += 1
        return None
    if masked[k] == ")" and not escaped[k]:
        return (k, k)

    depth = 0
    j = k
    while j < bound:
        if escaped[j]:
            j += 1
            continue
        char = masked[j]
        if char.isspace():
            break
        if char == "(":
            depth += 1
            if depth > MAX_DESTINATION_PAREN_DEPTH:
                return None
        elif char == ")":
            if depth == 0:
                break
            depth -= 1
        j += 1
    return None if depth else (k, j)


def _scan_title(masked: str, escaped: bytearray, pos: int, bound: int) -> int | None:
    """One past a `"…"` / `'…'` / `(…)` title starting at `pos`, or None (D1 rule 5).

    The `(…)` form is scanned to its first unescaped `)` with NO nesting — the
    simplest rule that keeps rule 5's whitespace-based destination/title
    disambiguation honest. An unterminated title, or a non-title trailer, is
    None: the whole span is then not a recognised link, so `[a](plan.md extra)`
    is prose.
    """
    closers = {'"': '"', "'": "'", "(": ")"}
    closer = closers.get(masked[pos])
    if closer is None or escaped[pos]:
        return None
    j = pos + 1
    while j < bound:
        if masked[j] == closer and not escaped[j]:
            return j + 1
        j += 1
    return None


def _skip_spaces(masked: str, pos: int, bound: int) -> int:
    """First offset at/after `pos` that is not whitespace (bounded by `bound`)."""
    k = pos
    while k < bound and masked[k].isspace():
        k += 1
    return k


def _close_inline(masked: str, escaped: bytearray, pos: int, bound: int) -> int | None:
    """One past the `)` closing an inline link whose destination ended at `pos`.

    Between the destination and the closing `)` only whitespace and at most
    one title may appear (D1 rules 3 and 5). None means the span is not a
    recognised link.
    """
    k = _skip_spaces(masked, pos, bound)
    if k < bound and masked[k] == ")" and not escaped[k]:
        return k + 1
    if k >= bound:
        return None
    after_title = _scan_title(masked, escaped, k, bound)
    if after_title is None:
        return None
    k = _skip_spaces(masked, after_title, bound)
    if k < bound and masked[k] == ")" and not escaped[k]:
        return k + 1
    return None


def _close_reference_definition(masked: str, escaped: bytearray, pos: int, bound: int) -> bool:
    """True when only whitespace and at most one title follow a refdef destination.

    D1 rule 6(b): a trailing non-title remainder disqualifies the definition
    exactly as it does the inline form, so `[plan]: plan.md and more` is prose.
    """
    k = _skip_spaces(masked, pos, bound)
    if k >= bound:
        return True
    after_title = _scan_title(masked, escaped, k, bound)
    if after_title is None:
        return False
    return _skip_spaces(masked, after_title, bound) >= bound


def scan_body_links(text: str) -> tuple[BodyLink, ...]:
    """Every recognised body-link destination occurrence in `text`, in source order.

    A pure function of the text (D5). It reports EVERY recognised occurrence,
    in-root or not, `local` or not — containment and existence are
    `body_link_findings`' job. That split is what lets
    `outside-root-body-link` exist at all, and it is what M28 consumes.

    The whole document is scanned, metadata block included, with offsets into
    the original text: a `Related:` bullet cannot be link-shaped, so scanning
    the whole text costs nothing and gives M28 a single offset base.

    One linear forward pass over the masked text. Three details are what keep
    it linear on adversarial input, and all three are easy to lose:

    - the blank-line bound comes from a MONOTONIC cursor into a precomputed
      list, never from a fresh search per candidate;
    - a candidate whose `]` is missing resumes at its blank-line bound, and a
      candidate that fails to form a link resumes at its `]` — never at the
      opening `[` + 1. Whether a candidate forms a link depends on what
      follows the `]`, not on which `[` found it; the one exception is the
      image rejection, which does depend on the `[` and therefore reuses the
      cached closing position rather than rescanning;
    - the destination parser bails the moment parentheses nest too deep, and
      bounds an angle destination at the newline.
    """
    masked = _mask_code(text)
    escaped = _escape_flags(masked)
    line_starts = _line_starts(masked)
    blank_starts = _blank_line_starts(masked, line_starts)
    end_of_text = len(masked)

    links: list[BodyLink] = []
    blank_cursor = 0
    line_cursor = 0
    i = 0
    while True:
        i = masked.find("[", i)
        if i == -1:
            break
        if escaped[i]:
            i += 1
            continue

        # One bound for the WHOLE candidate — label, destination and title
        # alike. Bounding only the label would let the destination parser run
        # to EOF.
        while blank_cursor < len(blank_starts) and blank_starts[blank_cursor] <= i:
            blank_cursor += 1
        limit = blank_starts[blank_cursor] if blank_cursor < len(blank_starts) else end_of_text

        close = -1
        j = i + 1
        while j < limit:
            if masked[j] == "]" and not escaped[j]:
                close = j
                break
            j += 1
        if close == -1:
            # No `]` before the blank line — and no later `[` in this
            # paragraph can find one either.
            i = limit
            continue

        if i and masked[i - 1] == "!" and not escaped[i - 1]:
            i = close + 1  # an image (D1 rule 2 / Q2), rejected after the fact
            continue

        while line_cursor + 1 < len(line_starts) and line_starts[line_cursor + 1] <= i:
            line_cursor += 1

        span: tuple[int, int] | None = None
        kind = ""
        resume = close + 1
        after = close + 1
        if after < end_of_text and masked[after] == "(":
            found = _scan_destination(masked, escaped, after + 1, limit)
            if found is not None:
                closed = _close_inline(masked, escaped, found[1], limit)
                if closed is not None:
                    span, kind, resume = found, "inline", closed
        elif after < end_of_text and masked[after] == ":":
            indent = masked[line_starts[line_cursor] : i]
            eol = masked.find("\n", i)
            eol = end_of_text if eol == -1 else eol
            if len(indent) <= 3 and not indent.strip(" ") and close < eol:
                bound = min(eol, limit)
                found = _scan_destination(masked, escaped, after + 1, bound)
                # Rule 6(c): an empty destination is not a recognised
                # reference definition at all — not a `BodyLink` carrying an
                # empty `raw`, which would hand M28 a zero-width span.
                if (
                    found is not None
                    and found[1] > found[0]
                    and _close_reference_definition(masked, escaped, found[1], bound)
                ):
                    span, kind, resume = found, "reference-definition", bound

        if span is None:
            i = close + 1
            continue

        start, stop = span
        while line_cursor + 1 < len(line_starts) and line_starts[line_cursor + 1] <= start:
            line_cursor += 1
        # `raw` is sliced from the ORIGINAL text, never from the mask, which
        # is what makes `text[start:end] == raw` true by construction.
        raw = text[start:stop]
        path, fragment = _split_destination(raw)
        links.append(
            BodyLink(
                kind=kind,
                line=line_cursor + 1,
                column=start - line_starts[line_cursor] + 1,
                raw=raw,
                path=path,
                fragment=fragment,
                start=start,
                end=stop,
            )
        )
        i = resume
    return tuple(links)


def classify_destination(raw: str) -> str:
    """Classify a destination token as a `DESTINATION_KINDS` member (M27 — D2).

    Runs on the token AS WRITTEN — escapes are not decoded first, so a
    percent-encoded `%23` at the front does not make a destination
    fragment-only — with one exception: a surrounding `<…>` pair is stripped
    first, or an angle-wrapped autolink-shaped destination would classify as
    `local` and be resolved as a path.

    The order of the tests is contractual: `//host/x` is `protocol-relative`
    rather than `root-absolute`. Only `local` is ever resolved or reported;
    the other five produce no finding of any kind, ever. A Windows-style
    `C:\\docs\\plan.md` is therefore scheme-shaped and silent — deliberate,
    and stated in `cli.md` so it is not mistaken for a gap.
    """
    token = raw[1:-1] if len(raw) >= 2 and raw.startswith("<") and raw.endswith(">") else raw
    if token == "":
        return "empty"
    if token.startswith("#"):
        return "fragment"
    if token.startswith("//"):
        return "protocol-relative"
    if token.startswith("/"):
        return "root-absolute"
    if _SCHEME_RE.match(token):
        return "scheme"
    return "local"


def normalise_body_link_target(doc_rel: str, dest_path: str) -> str:
    """Resolve `dest_path` against the REFERRING document's directory (M27 — D3).

    `doc_rel` is the referring document's root-relative POSIX path (e.g.
    `archive/2026-01-01/old-log.md`); this drops the last segment itself, so
    callers never pre-compute a directory. The single most important
    difference from a `Related:` target, which is root-relative — `../` is
    normal and expected in a body link and never appears in a `Related:`
    bullet.

    Purely lexical: `..` segments collapse textually, `resolve()` is never
    called and no symlink is followed, so the verdict is a function of two
    strings and cannot vary with filesystem state. `posixpath` rather than
    `os.path` for `_canonical_related_target`'s stated reason — on Windows
    `os.path.normpath` rewrites `/` to `\\` and treats `\\` as a separator,
    which would make containment platform-dependent and destroy exactly the
    hermeticity property D4b exists to guarantee.
    """
    return posixpath.normpath(posixpath.join(posixpath.dirname(doc_rel), dest_path))


def _body_link_is_contained(candidate: str) -> bool:
    """True when a normalised body-link candidate stays inside the root (M27 — D4b).

    `_candidate_exclusion_reason`'s `outside-root` predicate MINUS its leading
    `/` leg, and the divergence is deliberate: a root-absolute *body*
    destination names a web-server root rather than a tree path, so it is
    classified `root-absolute` and silenced before containment ever runs,
    whereas a root-absolute `Related:` target is `outside-root`.

    The test is `== ".."` or `startswith("../")`, never `startswith("..")` —
    `..foo.md` is an ordinary in-root file whose name happens to begin with
    two dots, and reporting it would be an over-fire with no repair available.
    """
    return not (candidate == ".." or candidate.startswith("../"))


def body_link_findings(path: Path, text: str, root: Path) -> list[Finding]:
    """`broken-body-link` / `outside-root-body-link` for one document (M27 — D4/D4b).

    The BINDING evaluation order, per occurrence: classify (not `local` →
    silence, stop), then containment by path arithmetic alone (escapes →
    `outside-root-body-link`, stop), then existence inside the root (missing →
    `broken-body-link`). An escaping destination is therefore NEVER also
    reported as broken — deciding whether it is broken would require precisely
    the stat the hermetic boundary forbids.

    Any existing filesystem entry satisfies a contained destination — file or
    directory, any extension (Q7) — so this calls `.exists()`, not
    `.is_file()`. A dangling symlink inside the root reports broken, because
    `.exists()` follows links and the destination really is unreachable from
    the reader's point of view.

    The single `.exists()` on an already-contained, already-normalised
    candidate is the only filesystem access in the whole scanner. That is what
    makes `docs check` a function of the tree alone: the same bytes checked
    from a different location yield the identical verdict.
    """
    doc_rel = _root_relative(path, root)
    findings: list[Finding] = []
    for link in scan_body_links(text):
        if classify_destination(link.raw) != "local":
            continue
        candidate = normalise_body_link_target(doc_rel, link.path)
        if not _body_link_is_contained(candidate):
            findings.append(
                Finding(
                    path,
                    "error",
                    "outside-root-body-link",
                    f"body link at line {link.line} leaves the docs root: {link.raw} "
                    f"(normalises to {candidate}); links outside the tree must be URLs",
                )
            )
            continue
        if not (root / candidate).exists():
            findings.append(
                Finding(
                    path,
                    "error",
                    "broken-body-link",
                    f"body link at line {link.line} does not resolve to an existing path: "
                    f"{link.raw} (resolves to {candidate})",
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Check rules, query, and JSON records (M3)
# ---------------------------------------------------------------------------


def check_doc(
    path: Path,
    text: str,
    root: Path,
    config: Config,
    stale: int | None,
    today: date,
    stale_source: str | None = None,
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

    # --- M25 (D7) duplicate metadata labels ------------------------------
    # Evaluated against the metadata block's RAW label lines, because by the
    # time `metadata` exists the evidence is gone: `parse_metadata_block`
    # builds a dict, so a second copy of a label has already replaced the
    # first and silently discarded everything under it. That is data loss
    # affecting every other rule, the INDEX renderer, and `Related:`
    # resolution alike — hence an error, not a warning.
    for label, count in _duplicate_labels(text).items():
        findings.append(
            Finding(
                path,
                "error",
                "duplicate-field",
                f"metadata field '{label}:' appears {count} times; "
                "only the last occurrence is read",
            )
        )

    # --- broken Related: refs ---
    for _verb, target in _related_pairs(metadata):
        if not (root / target).is_file():
            findings.append(
                Finding(
                    path,
                    "error",
                    "broken-ref",
                    f"Related: target does not resolve to a file: {target}",
                )
            )

    # --- stale (warning; only with a stale window, only Lifecycle: active) ---
    if (
        stale is not None
        and isinstance(lifecycle, str)
        and lifecycle.strip() == "active"
        and updated is not None
        and (today - updated).days > stale
    ):
        # M19 (D2): name the threshold's provenance so the operator knows
        # which knob to turn. `stale_source` ("config"/"cli"/None) comes from
        # `resolve_stale`; a bare/legacy call (no source) keeps the old form.
        if stale_source == "config":
            provenance = ", set in .docs.toml [check] stale_days"
        elif stale_source == "cli":
            provenance = ", via --stale"
        else:
            provenance = ""
        findings.append(
            Finding(
                path,
                "warning",
                "stale",
                f"Lifecycle: active but not updated in {(today - updated).days} days "
                f"(stale threshold {stale}{provenance})",
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


def reciprocity_findings(
    entries: Sequence[tuple[Path, str]], root: Path
) -> dict[Path, list[Finding]]:
    """Cross-document `missing-inverse` findings for a materialised walk (M25 — D2).

    The only rule in `docs check` that needs more than one document, so it
    runs as a second pass over the same `(path, text)` entries `check_tree`
    already read, and its results are keyed by source path so `check_tree`
    can interleave them into its existing per-doc grouping.

    A recognized edge (`inverse_verb(verb) is not None`) obliges its target
    to declare the exact inverse pointing BACK at the source. Everything
    else is silence: free-form verbs, a target outside the walked/parseable
    set (excluded, unresolvable, non-Markdown, or malformed — those rules
    keep ownership), and a self-edge (amendment A). Paths are compared
    canonically (amendment B), and one finding is emitted per distinct
    `(source, verb, canonical-target)` triple.

    Args:
        entries: `(absolute path, text)` for every walked doc, in walk order.
        root: The docs root the paths are relative to.

    Returns:
        A mapping from source path to its findings, in bullet order. Docs
        with no finding are absent from the mapping.
    """
    # Pass 1 — index the walked set by root-relative path. A doc whose
    # metadata block does not parse is SKIPPED: `malformed` owns that case,
    # both as a source and as a target.
    index: dict[str, tuple[Path, tuple[tuple[str, str], ...]]] = {}
    for path, text in entries:
        try:
            _title, metadata, _body = parse_metadata_block(text)
        except MetadataError:
            continue
        index[_root_relative(path, root)] = (path, _related_pairs(metadata))

    # Pass 2 — validate. The five applicability conditions are NOT five
    # branches: they fall out of "the target must be an indexed, parseable,
    # walked doc that is not me". The single `index` lookup covers excluded
    # (never walked), unresolvable (never walked), non-Markdown (never
    # walked), and malformed (skipped above) in one place.
    findings: dict[Path, list[Finding]] = {}
    for source_rel, (source_path, pairs) in index.items():
        seen: set[tuple[str, str]] = set()
        for verb, raw_target in pairs:
            inverse = inverse_verb(verb)
            if inverse is None:
                continue
            target_rel = _canonical_related_target(raw_target)
            if target_rel == source_rel:
                continue  # amendment A — a self-edge is exempt
            target = index.get(target_rel)
            if target is None:
                continue
            if (verb, target_rel) in seen:
                continue  # one finding per (source, verb, canonical target)
            seen.add((verb, target_rel))
            # The inverse must point BACK at the source — declaring the
            # right verb at some other target does not reciprocate.
            if any(
                v == inverse and _canonical_related_target(t) == source_rel for v, t in target[1]
            ):
                continue
            findings.setdefault(source_path, []).append(
                Finding(
                    source_path,
                    "error",
                    "missing-inverse",
                    f"Related: '{verb}: {target_rel}' has no inverse; "
                    f"{target_rel} must declare '{inverse}: {source_rel}' "
                    "(or remove the edge)",
                )
            )
    return findings


def check_tree(
    root: Path,
    config: Config,
    stale: int | None,
    today: date,
    predicate: Callable[[str], bool] | None = None,
    stale_source: str | None = None,
) -> list[Finding]:
    """Validate every doc under ``root``; return all findings.

    Iterates `_iter_doc_texts`, applies `check_doc` to each doc, and
    concatenates the results in root-relative POSIX path order.

    M25 (D2): the walk is materialised once so the cross-document
    `reciprocity_findings` pass can see every doc, and its results are
    interleaved into the existing per-doc grouping rather than appended as a
    separate tail block. Within a doc the order is therefore `check_doc`'s
    findings first, in its own order, then any `missing-inverse`.

    M8 (F3): the optional ``predicate`` argument is threaded into
    `_iter_doc_texts` so excluded files are skipped before validation.

    M19 (D2): the optional ``stale_source`` (``"cli"`` / ``"config"`` /
    ``None``, from `resolve_stale`) is forwarded to `check_doc` so the stale
    finding's message can name the threshold's provenance.
    """
    findings: list[Finding] = []
    entries = list(_iter_doc_texts(root, config, predicate=predicate))
    recip = reciprocity_findings(entries, root)
    for path, text in entries:
        findings.extend(check_doc(path, text, root, config, stale, today, stale_source))
        findings.extend(recip.get(path, ()))
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


def resolve_stale(
    cli_stale: int | None, config_stale_days: int | None
) -> tuple[int | None, str | None]:
    """Resolve the stale window + its provenance (M19 — D2).

    Precedence: CLI ``--stale`` > ``[check] stale_days`` > unset. Returns a
    ``(window, source)`` pair where ``source`` is ``"cli"`` when the window
    came from an explicit ``--stale`` (including ``--stale 0`` — only ``None``
    means "flag absent"), ``"config"`` when it came from the tree's
    ``[check] stale_days``, and ``None`` when neither is set (no stale window).

    The ``source`` lets ``check_doc`` name the threshold's provenance in the
    stale finding so the operator knows which knob to turn. Shared by both
    check-path consumers — bare/explicit ``docs check`` and ``docs touch
    --check``; ``docs list --stale`` is NOT a consumer (Q6).
    """
    if cli_stale is not None:
        return cli_stale, "cli"
    if config_stale_days is not None:
        return config_stale_days, "config"
    return None, None


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
# Relationship repair — `docs relate` (M25)
# ---------------------------------------------------------------------------


def plan_relate(
    root: Path,
    config: Config,
    *,
    action: str,
    source: Path,
    verb: str,
    target: Path,
    reason: str | None,
    date_str: str,
) -> RelatePlan:
    """Stage both endpoints' complete new texts without writing (M25 — D3/D5).

    The `plan_migration` analogue for the relationship verbs, and D5's
    stages 1–2: both files are read, both new texts are computed in memory,
    and nothing is written. `apply_relate_plan` publishes the result.

    Per endpoint the edit is applied, then — only when the edge actually
    moved — `Updated:` is bumped and, for an archived endpoint, a
    `Revision:` bullet is appended. An endpoint whose edge is already in the
    requested state is `change="unchanged"` with `new_text is original`:
    that single rule is the whole of D3's idempotency and D4's "one bullet
    per REAL mutation".

    Args:
        root: The resolved docs root.
        config: The tree's config (supplies `archive_dir`).
        action: ``"add"`` or ``"remove"``.
        source: Absolute path of the declaring endpoint.
        verb: A recognized reciprocal verb.
        target: Absolute path of the other endpoint.
        reason: The `--reason` value; required when either endpoint is
            archived (the CLI enforces that before planning).
        date_str: The date to write, already in the tree's `date_format`.

    Raises:
        ValueError: `verb` is not recognized, or an archived endpoint would
            change without a `reason` — both programming errors, refused by
            `_cmd_relate` long before planning.
        MetadataError: an endpoint has no H1 / metadata block.
        OSError: an endpoint cannot be read.
    """
    inverse = inverse_verb(verb)
    if inverse is None:
        raise ValueError(f"not a recognized reciprocal verb: {verb!r}")

    source_rel = _root_relative(source, root)
    target_rel = _root_relative(target, root)
    return RelatePlan(
        action=action,
        verb=verb,
        inverse=inverse,
        source_rel=source_rel,
        target_rel=target_rel,
        reason=reason,
        date_str=date_str,
        edits=(
            _plan_relate_edit(
                source,
                source_rel,
                config,
                action=action,
                verb=verb,
                other_rel=target_rel,
                reason=reason,
                date_str=date_str,
            ),
            _plan_relate_edit(
                target,
                target_rel,
                config,
                action=action,
                verb=inverse,
                other_rel=source_rel,
                reason=reason,
                date_str=date_str,
            ),
        ),
    )


def _plan_relate_edit(
    path: Path,
    rel: str,
    config: Config,
    *,
    action: str,
    verb: str,
    other_rel: str,
    reason: str | None,
    date_str: str,
) -> RelateEdit:
    """Stage one endpoint's half of a `docs relate` operation (M25 — D3/D4).

    `verb` and `other_rel` are already this document's OWN bullet body: the
    forward verb at the target for the source, the inverse at the source for
    the target.

    The ordering is contractual, not incidental — the archived byte-delta
    assertion pins it: apply the edge; if nothing moved, stop (that single
    `if changed:` guard is the whole of D3's idempotency and D4's "one bullet
    per REAL mutation"); otherwise bump `Updated:` and, only for an archived
    endpoint, append the `Revision:` audit bullet.
    """
    original = path.read_text()
    edge = f"{verb}: {other_rel}"
    archived = _is_archived_rel(rel, config)

    if action == "add":
        new_text, changed = add_related_edge(original, verb, other_rel)
        present_before, present_after = not changed, True
    else:
        new_text, changed = remove_related_edge(original, verb, other_rel)
        present_before, present_after = changed, False

    change = "unchanged"
    revision_appended = False
    if changed:
        change = "added" if action == "add" else "removed"
        new_text = set_metadata_field(new_text, "Updated", date_str)
        if archived:
            if reason is None:
                raise ValueError(f"{rel} is under the archive subtree; a reason is required")
            new_text = append_revision_entry(
                new_text, f"{date_str}: relate {action} '{edge}'; reason: {reason}"
            )
            revision_appended = True

    return RelateEdit(
        path=path,
        rel=rel,
        archived=archived,
        edge=edge,
        original=original,
        new_text=new_text,
        change=change,
        present_before=present_before,
        present_after=present_after,
        updated_bumped=changed,
        revision_appended=revision_appended,
    )


def apply_relate_plan(plan: RelatePlan) -> None:
    """Publish a `RelatePlan`, rolling back on a later failure (M25 — D5).

    D5's stages 3–5: re-validate each staged text, pre-flight each changed
    endpoint for write permission, then publish in plan order (source, then
    target) via `atomic_write`. A failure at any stage raises
    `CoordinatedWriteError` carrying the fully-rendered operator message;
    `_cmd_relate` prints it as ``docs: relate: <exc>`` and exits 2.

    If a publish fails after an earlier one succeeded, every published
    endpoint is restored — also via `atomic_write`, so the restore inherits
    the same tmpfile + fsync + rename durability as the write it undoes. A
    restore that itself fails is reported as an explicit non-atomic
    admission (`ROLLBACK FAILED`), never swallowed.

    A plan whose edits are all `unchanged` writes nothing and returns.

    Raises:
        CoordinatedWriteError: any stage-3/4/5 failure.
    """
    changed = [edit for edit in plan.edits if edit.change != "unchanged"]
    if not changed:
        return

    # Stage 3 — re-validate the staged texts. Defensive: the editors cannot
    # remove an H1, so this is unreachable in practice; it exists so a future
    # editor bug aborts before publishing rather than after.
    for edit in changed:
        try:
            parse_metadata_block(edit.new_text)
        except MetadataError as exc:
            raise CoordinatedWriteError(
                f"staged text for {edit.rel} would not parse ({exc}); refusing before any write",
                rolled_back=True,
                published=(),
            ) from exc

    # Stage 4 — writability pre-flight on the FILE, and on nothing else.
    # `atomic_write` publishes via tmpfile + rename, which SUCCEEDS on a
    # read-only file in a writable directory, so only this explicit check
    # honours a read-only archive. Scanning every changed endpoint before
    # publishing any is what keeps the source untouched when the target is
    # the unwritable one. Deliberately NOT a parent-directory check: an
    # unwritable directory is a stage-5 failure with a rollback, not a
    # stage-4 refusal.
    for edit in changed:
        if not os.access(edit.path, os.W_OK):
            raise CoordinatedWriteError(
                f"{edit.rel} is not writable; refusing before any write",
                rolled_back=True,
                published=(),
            )

    # Stage 5 — publish in plan order, rolling back on a later failure.
    published: list[RelateEdit] = []
    for edit in changed:
        try:
            atomic_write(edit.path, edit.new_text)
        except OSError as exc:
            raise _rollback_relate(plan, edit, exc, published) from exc
        published.append(edit)


def _rollback_relate(
    plan: RelatePlan,
    failed: RelateEdit,
    exc: OSError,
    published: list[RelateEdit],
) -> CoordinatedWriteError:
    """Undo `published` after `failed`'s write raised; build the D5 admission.

    Restores through the module-global `atomic_write` (binding per D5) so a
    restore inherits the same tmpfile + fsync + rename durability as the
    write it undoes — a restore torn by a crash is the very failure the
    rollback exists to prevent.
    """
    unrestored: list[RelateEdit] = []
    for done in reversed(published):
        try:
            atomic_write(done.path, done.original)
        except OSError:
            unrestored.append(done)
    unrestored.reverse()

    prefix = f"write failed for {failed.rel}: {exc}"
    if unrestored:
        # The admission must describe what each file ACTUALLY carries now,
        # which is the opposite way round for `remove` (M25 — R4).
        carries = "still carries" if plan.action == "add" else "no longer carries"
        names = ", ".join(edit.rel for edit in unrestored)
        detail = "; ".join(f"{edit.rel} {carries} '{edit.edge}'" for edit in unrestored)
        message = f"{prefix}; ROLLBACK FAILED for {names} — repair manually: {detail}"
    elif published:
        names = ", ".join(edit.rel for edit in published)
        message = f"{prefix}; rolled back {names} — the tree is unchanged"
    else:
        message = f"{prefix}; nothing was published — the tree is unchanged"

    return CoordinatedWriteError(
        message,
        rolled_back=not unrestored,
        published=tuple(edit.rel for edit in published),
    )


def relate_plan_to_json(
    plan: RelatePlan, *, dry_run: bool, applied: bool, index_refreshed: bool
) -> dict[str, object]:
    """Convert a `RelatePlan` to its `docs relate --json` operation record.

    One object with the same shape for a `--dry-run` preview and for a real
    apply, so the two are diffable (the schema cli.md pins). `edits` is
    always exactly two records, ``[source, target]`` in that order.

    Args:
        plan: The plan produced by `plan_relate`.
        dry_run: True under `--dry-run`.
        applied: True iff bytes were actually written.
        index_refreshed: True iff the end-of-run reindex ran and succeeded.

    Returns:
        A JSON-serialisable record dict.
    """
    return {
        "action": plan.action,
        "verb": plan.verb,
        "inverse": plan.inverse,
        "source": plan.source_rel,
        "target": plan.target_rel,
        "reason": plan.reason,
        "date": plan.date_str,
        "dry_run": dry_run,
        "applied": applied,
        "index_refreshed": index_refreshed,
        "edits": [
            {
                "path": edit.rel,
                "archived": edit.archived,
                "edge": edit.edge,
                "present_before": edit.present_before,
                "present_after": edit.present_after,
                "change": edit.change,
                "updated_bumped": edit.updated_bumped,
                "revision_appended": edit.revision_appended,
            }
            for edit in plan.edits
        ],
    }


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


def _add_relate_subverb(
    sub: argparse._SubParsersAction[argparse.ArgumentParser],
    common: argparse.ArgumentParser,
    action: str,
) -> None:
    """Register `docs relate add` / `docs relate remove` (M25 — D3).

    Both subverbs take the identical `SOURCE VERB TARGET` grammar and the
    same flags; only the help wording differs.

    `VERB` deliberately does NOT use argparse `choices=`: argparse's own
    "invalid choice" message would replace the frozen
    ``docs: relate: unknown verb '<verb>'; expected one of: …`` refusal that
    `cli.md` pins and eight tests assert.
    """
    verbing = "Add" if action == "add" else "Remove"
    p = sub.add_parser(
        action,
        parents=[common],
        help=f"{verbing} one reciprocal relationship pair across two docs.",
        description=(
            f"{verbing} the reciprocal relationship pair `VERB` between "
            "SOURCE and TARGET (M25 — D3). Writes BOTH halves as one "
            "coordinated operation: SOURCE's `<VERB>: <target>` bullet and "
            "TARGET's `<inverse>: <source>` bullet. Only the six recognized "
            "verbs are accepted. Idempotent — a fully-satisfied invocation "
            "writes zero bytes, bumps no `Updated:`, and does not reindex. "
            "Every endpoint whose bytes change gets its `Updated:` bumped; "
            "INDEX.md is refreshed exactly once at the end. An endpoint "
            "under the archive subtree requires `--reason` and receives a "
            "dated `Revision:` audit bullet."
        ),
    )
    p.add_argument("source", metavar="SOURCE", help="The declaring document.")
    p.add_argument(
        "verb",
        metavar="VERB",
        help="One of: precedes, follows, depends-on, required-by, blocks, blocked-by.",
    )
    p.add_argument("target", metavar="TARGET", help="The other endpoint.")
    p.add_argument(
        "--reason",
        help=(
            "Audit reason; REQUIRED when either endpoint is under the "
            "archive subtree. Single non-empty line."
        ),
    )
    p.add_argument(
        "--date",
        help="Date YYYY-MM-DD for Updated:/Revision: (default: today).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit the operation-plan record as JSON on stdout.",
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
            "the scaffold's frontmatter. Refused (exit 2) only if the body itself "
            "contains a metadata block — a leading `---` fence or >=2 adjacent "
            "{Lifecycle, Role, Updated} lines (lone prose like a `Plan:` line is "
            "fine). Pass body content only; `docs new` owns the frontmatter."
        ),
    )

    archive_p = subparsers.add_parser(
        "archive",
        parents=[common],
        help="Archive a doc: edit Lifecycle, move to archive/<date>/, reindex.",
        description=(
            "Set Lifecycle: archived and bump Updated:, move the file to "
            "<archive_dir>/<YYYY-MM-DD>/, then regenerate INDEX.md. The "
            "metadata edit is atomic; the move runs only after it succeeds. "
            "Exactly three shapes write, and no other invocation writes a "
            "related document (M26): `docs archive FILE` archives FILE alone; "
            "`--cascade-dry-run` previews the whole one-hop neighbourhood and "
            "writes nothing; `--cascade-only GLOB` archives FILE plus exactly "
            "the candidates matching GLOB, planned in full before the first "
            "byte moves."
        ),
    )
    archive_p.add_argument("file", help="Path to the doc to archive.")
    archive_p.add_argument("--reason", help="Free-form Archived-reason: metadata line.")
    archive_p.add_argument("--date", help="Archive date YYYY-MM-DD (default: today).")
    # M26 (D2): `--cascade` and `--interactive` are RETIRED. They stay
    # REGISTERED so an obsolete script or workflow skill gets a legible,
    # actionable refusal rather than argparse's generic `unrecognized
    # arguments`, and they are deliberately NOT in a mutually-exclusive
    # group (Phase-1 Q12): the single unconditional refusal at the top of
    # `_cmd_archive` covers every combination, so no cell is intercepted by
    # argparse's "not allowed with" error instead.
    _retired_help = (
        "RETIRED in docs 2.0 — refuses (exit 2) and writes nothing. Preview "
        "with --cascade-dry-run, then write with --cascade-only GLOB."
    )
    archive_p.add_argument("--cascade", action="store_true", help=_retired_help)
    archive_p.add_argument("--interactive", action="store_true", help=_retired_help)
    archive_p.add_argument(
        "--cascade-only",
        metavar="GLOB",
        help=(
            "Also archive exactly the one-hop pairs-with / child-of candidates whose "
            "CANONICAL root-relative path matches GLOB — the only way to archive a "
            "related document. A scope that selects nothing refuses (exit 2)."
        ),
    )
    archive_p.add_argument(
        "--cascade-dry-run",
        action="store_true",
        help=(
            "Preview the primary plus EVERY one-hop candidate (selected, not selected, "
            "or ineligible) and write nothing (exit 0); composes with --cascade-only."
        ),
    )
    archive_p.add_argument(
        "--json",
        action="store_true",
        help="Emit the operation-plan record as JSON on stdout.",
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
    touch_p.add_argument(
        "--check",
        action="store_true",
        help=(
            "After the end-of-batch reindex, run the same tree-wide `docs check` "
            "over the resolved root and fold its result into the exit code "
            "(max(touch, check); a failed touch short-circuits the check)."
        ),
    )
    touch_p.add_argument(
        "--stale",
        type=int,
        metavar="N",
        help=(
            "Stale window forwarded to --check's validation (active docs not "
            "updated in more than N days). Requires --check; absent → the "
            "[check] stale_days config default applies."
        ),
    )

    # M15 (B3): `docs stamp <file>...` — write-then-stamp. Inserts a
    # convention-correct metadata block onto files an agent already wrote,
    # preserving the body. Standalone top-level verb, mutating-verb polarity
    # (writes by default; --dry-run to opt out).
    stamp_p = subparsers.add_parser(
        "stamp",
        parents=[common],
        help="Stamp a metadata block onto one or more already-written files.",
        description=(
            "Insert a convention-correct metadata block (Lifecycle: draft, "
            "Role, Project, Updated: today) onto one or more files an agent "
            "has already written, preserving the body verbatim (M15 — B3). "
            "The write-then-stamp counterpart to `docs new --body-from`. Role "
            "is `--role` else the default `notes` (NO H1-role inference); "
            "project is `--project` else the docs root's configured project; "
            "title is the file's H1 (or `--title`, or synthesised from the "
            "filename). Re-stamping an already-stamped file refreshes only "
            "Updated:. Foreign metadata is parked under `## Migrated "
            "metadata`. Atomic multi-file batch; one end-of-batch INDEX "
            "refresh; `--dry-run` previews."
        ),
    )
    stamp_p.add_argument("files", nargs="+", help="Path(s) to the file(s) to stamp.")
    stamp_p.add_argument(
        "--role", help="Doc role (default: notes); must be in the Role vocabulary."
    )
    stamp_p.add_argument("--project", help="Project slug (overrides the configured default).")
    stamp_p.add_argument("--title", help="H1 title (overrides the file's H1 / synthesised title).")

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

    # M15 (B2): `docs project set <doc>... <new-project>` — the single-doc
    # counterpart to `rename`. A single nargs="+" positional run is split as
    # `*docs, new_project` inside the command (NOT two positionals; argparse
    # cannot split a variadic run + a trailing positional unambiguously).
    project_set_p = project_sub.add_parser(
        "set",
        parents=[common],
        help="Reassign one or more docs' Project: field to <new-project>.",
        description=(
            "Reassign the `Project:` field of one or more named docs (M15 — "
            "B2). A single positional run is split as `*docs, <new-project>`: "
            "the last token is the new project name, the earlier tokens are "
            "doc paths. Rewrites only the named docs' `Project:` line "
            "(inserting it when absent) and regenerates INDEX.md once; never "
            "touches `.docs.toml`, non-named docs, or `Related:` edges. "
            "`<new-project>` is auto-normalised; a value new to the tree is "
            "refused unless `--new-project` is passed (the typo guard). A "
            "named archived doc refuses the whole batch (exit 2); validate-"
            "all-first atomic semantics; `--dry-run` previews."
        ),
    )
    project_set_p.add_argument(
        "args",
        nargs="+",
        metavar="doc ... new-project",
        help="One or more doc paths followed by the new project name.",
    )
    project_set_p.add_argument(
        "--new-project",
        action="store_true",
        help="Acknowledge creating a new project group (bypasses the typo guard).",
    )

    # M25 (D3): `docs relate` verb namespace with nested subverbs, shaped
    # like `docs project`. Deliberately narrow — it edits only the six
    # recognized reciprocal verbs, only two documents, and only one pair per
    # invocation. It is the repair verb for `docs check`'s `missing-inverse`.
    relate_p = subparsers.add_parser(
        "relate",
        help="Add or remove one reciprocal relationship pair across two docs.",
        description=(
            "Relationship-namespace verbs (M25). Today: `add`, `remove`. "
            "The repair verb for `docs check`'s `missing-inverse` finding: "
            "`check` names the incomplete edge, you decide whether it should "
            "exist, and `relate` writes (or unwrites) both halves as one "
            "coordinated operation. Not a generic `Related:` editor — free-"
            "form verbs stay hand-edited."
        ),
    )
    relate_sub = relate_p.add_subparsers(dest="relate_command", required=True)
    _add_relate_subverb(relate_sub, common, "add")
    _add_relate_subverb(relate_sub, common, "remove")

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
        help="Materialise the bundled agent skill onto this host.",
        description=(
            "Copy (or symlink) the bundled `docs` agent skill from the "
            "installed `docs_cli` package onto a host so an agent can pick it "
            "up. The default destination is "
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
        default=None,
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


def _resolve_managed_root(args: argparse.Namespace, start: Path, *, verb: str) -> Path | int:
    """Resolve a strict docs root for a mutating verb, or print a refusal + exit code.

    The shared root-resolution behaviour for the write verbs (M12 — OQ-C /
    OQ-1 / OQ-η; M14 — A2; M15 — B2 / B3). `verb` parametrises the
    `docs: <verb>:` message prefix so every verb refuses in its own voice
    (e.g. `project set` must NOT emit `project rename:`).

    When `--root` is set, the directory must contain a `.docs.toml`;
    otherwise return 2 with the `--root`-named refusal. When `--root` is
    absent, walk up from `start`; if no `.docs.toml` ancestor is found,
    return 2 with the start-path-named refusal. A write into an unmanaged
    tree is the footgun this closes (the read verbs keep the cwd-fallback —
    a wrong-tree read is recoverable; a write is not).
    """
    if args.root:
        root = Path(args.root).resolve()
        if not (root / ".docs.toml").is_file():
            print(
                f"docs: {verb}: --root {args.root} does not contain .docs.toml; refusing",
                file=sys.stderr,
            )
            return 2
        return root
    found = _find_root_strict(start)
    if found is None:
        print(
            f"docs: {verb}: {start} is not under a docs root with .docs.toml; refusing",
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


# M15 (C4): the required-field labels whose adjacent clustering signals a
# real convention metadata block in a `--body-from` body. `Project` is
# intentionally excluded — a prose `Project:` line is common and weak signal;
# the block-shape signal is the {Lifecycle, Role, Updated} cluster.
_C4_REQUIRED_LABEL_RE = re.compile(r"^(Lifecycle|Role|Updated):\s")


def _body_has_metadata_block(body_text: str) -> bool:
    """True iff a `--body-from` body carries a real convention metadata block (M15 — C4).

    Two signals trip detection (the footgun of pasting a whole front-matter
    document as a body):

    - **(a)** the first non-blank line, stripped, is ``---`` (a leading YAML
      front-matter fence); or
    - **(b)** within the first ~20 lines (after an optional single leading
      ``# `` H1), a **contiguous run** of ``≥ 2`` of the required-field labels
      ``{Lifecycle, Role, Updated}`` appears on directly-adjacent lines. Any
      blank/prose line OR a *non-required* ``Label:`` line resets the run, so a
      lone prose required-field line — or two required-field lines separated by
      anything — does NOT trip the refusal.

    A lone prose ``Reason:`` / ``Plan:`` / ``Updated:`` line is accepted
    (``Reason``/``Plan`` are not even required labels). Mirrors the cli.md C4
    contract.
    """
    lines = body_text.splitlines()

    # Signal (a): a leading `---` YAML fence (first non-blank line).
    for line in lines:
        if line.strip() == "":
            continue
        if line.strip() == "---":
            return True
        break

    # Signal (b): a >=2 required-field cluster on adjacent lines, scanning the
    # first ~20 lines after skipping ONE optional leading `# ` H1.
    head = lines[:20]
    start = 0
    for idx, line in enumerate(head):
        if line.strip() == "":
            continue
        if line.startswith("# "):
            start = idx + 1
        break
    run = 0
    for line in head[start:]:
        if _C4_REQUIRED_LABEL_RE.match(line):
            run += 1
            if run >= 2:
                return True
        else:
            run = 0
    return False


def _slug_to_title(slug: str) -> str:
    """Derive a default H1 title from a slug: last path segment, title-cased.

    `-` and `_` are treated as word separators (`sub/my-feature` → `My Feature`).
    """
    segment = slug.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]
    return segment.replace("-", " ").replace("_", " ").title()


def _cmd_new(args: argparse.Namespace) -> int:
    # M14 (A2): refuse the cwd-as-root fallback. `docs new` must not
    # silently scaffold into an unmanaged dir with default config; it
    # resolves a real `.docs.toml` root or refuses with exit 2 (mirrors
    # `touch` / `project rename`). The read verbs keep the cwd-fallback.
    root_or_exit = _resolve_managed_root(args, Path.cwd(), verb="new")
    if isinstance(root_or_exit, int):
        return root_or_exit
    root = root_or_exit
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
    # M14 (A3): reject an empty final segment. `foo/` (target `foo/.md`)
    # and `foo/.md` (slug `foo/.` after the `.md` strip) both resolve to
    # an invisible `.md` dotfile that every read verb skips. Split on the
    # last `/` WITHOUT stripping a trailing slash so the empty / `.`
    # segment is detected.
    final_seg = slug.replace("\\", "/").rsplit("/", 1)[-1]
    if (
        not slug.strip()
        or final_seg in ("", ".")
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
    # appends it under the scaffold. M15 (C4): the body is refused (BEFORE the
    # `--dry-run` check, so an agent dry-running an invalid body still gets the
    # failure) only when it carries an *actual* metadata block — a leading
    # `---` fence or a >=2 required-field cluster on adjacent lines — not
    # whenever any line is `Label:`-shaped. See `_body_has_metadata_block`.
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

        # C4 refusal — a real metadata block (cluster or fence).
        if _body_has_metadata_block(body_text):
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


def _is_archived_rel(rel: str, config: Config) -> bool:
    """True iff `rel` IS the configured archive subtree or lies under it.

    The idiom `check_doc` and `_cmd_relate` already use, lifted to a named
    helper because M26 asks it of every plan member. Deliberately NOT
    `_in_archive_subdir`, which hardcodes `archive` / `archived` /
    `project-history` and ignores `[archive] dir`: on a tree configured with
    ``dir = "history"`` a plain `archive/` directory is an ordinary
    subdirectory whose docs are perfectly eligible candidates.
    """
    return rel == config.archive_dir or rel.startswith(config.archive_dir + "/")


def _archive_destination(root: Path, config: Config, date_str: str, name: str) -> Path:
    """The archive destination of a document named `name`.

    One expression, one place: `_archive_one` computes it to write, the
    planner computes it to preview, and the two must not drift.
    """
    return root / config.archive_dir / date_str / name


def _candidate_exclusion_reason(rel: str, root: Path, config: Config) -> str | None:
    """Why `rel` is an INELIGIBLE archive candidate, or None (M26 — D3).

    Two conditions can hold at once (`../ghost.md` both escapes the root and
    does not exist), so the order here IS the frozen precedence:
    `outside-root`, then `already-archived`, then `unresolved-target` — the
    more structural fact wins, and the answer is deterministic.

    `not-selected` is never returned: it is not an ineligibility but the
    scope's verdict on an otherwise eligible candidate, and ineligibility
    always wins over it.
    """
    if rel.startswith("/") or rel == ".." or rel.startswith("../"):
        return "outside-root"
    if _is_archived_rel(rel, config):
        return "already-archived"
    if not (root / rel).is_file():
        return "unresolved-target"
    return None


def archive_candidates(
    doc: Doc, root: Path, config: Config, scope: str | None
) -> tuple[ArchiveMove, ...]:
    """The one-hop archive candidates of `doc`, in declaration order (M26 — D3).

    Pure: reads `doc.related` and stats candidate paths, writes nothing, and
    computes no destination — `plan_archive` owns that, and only for the
    selected members.

    The set is the existing one-hop `pairs-with` / `child-of` edges (M2's
    no-transitive-cascade decision is unchanged), **deduplicated on the
    canonical root-relative POSIX path** with the first declaration winning
    the reported verb. Every declared spelling of a deduplicated candidate
    survives in `aliases`, because `_rewrite_referring_edges` repoints a
    bullet iff its target exactly equals an `old_rel`. A self-edge — a
    candidate whose canonical path equals the primary's — is silently
    excluded and is not reported as ineligible (Phase-1 Q6).

    `scope` is compiled by the matcher `compile_exclude_predicate` uses and
    matched against the CANONICAL path, so a `./b.md` spelling can neither
    dodge nor defeat a scope. A pattern that compiles to nothing, or a
    negated one, selects nothing here — `_cmd_archive` has already refused
    both at check-order step 2, so this is a defensive fallback, not the
    contract.

    The scan deliberately does **not** consult `[exclude]` / `.docsignore`
    (Phase-1 Q8, BINDING): those govern the tree walks — the pre-flight
    validation walk and the reindex — not the primary's own declared edges.
    Nor does it `parse()` a candidate: an unparseable candidate is still a
    candidate, and the pre-flight owns that refusal.
    """
    rgx: re.Pattern[str] | None = None
    if scope is not None:
        compiled = _compile_docsignore_pattern(scope)
        if compiled is not None and not compiled[0]:
            rgx = compiled[1]

    primary_rel = _root_relative(doc.path, root)
    by_rel: dict[str, ArchiveMove] = {}
    for verb, target in doc.related:
        if verb not in _CASCADE_VERBS:
            continue
        rel = _canonical_related_target(target)
        if rel == primary_rel:
            continue
        seen = by_rel.get(rel)
        if seen is not None:
            if target not in seen.aliases:
                by_rel[rel] = replace(seen, aliases=(*seen.aliases, target))
            continue
        reason = _candidate_exclusion_reason(rel, root, config)
        selected = reason is None and rgx is not None and bool(rgx.match(rel))
        by_rel[rel] = ArchiveMove(
            path=root / rel,
            rel=rel,
            aliases=(target,),
            verb=verb,
            dest=None,
            dest_rel=None,
            selected=selected,
            exclusion_reason=None if selected else (reason or "not-selected"),
        )
    return tuple(by_rel.values())


def plan_archive(
    root: Path,
    config: Config,
    *,
    primary: Path,
    source: str,
    doc: Doc,
    scope: str | None,
    date_str: str,
    reason: str | None,
) -> ArchivePlan:
    """Build the complete `docs archive` operation plan (M26 — D4).

    The `plan_relate` analogue: everything is read and decided here, and
    nothing is written — a preview and a real apply differ only in whether
    `apply_archive_plan` is then called. Destinations are filled for the
    primary and for the SELECTED candidates only; an ineligible or
    unselected candidate keeps `dest is None`, which is exactly what the
    `--json` record's "destination non-null iff selected" rule means.

    Args:
        root: The resolved docs root.
        config: The tree's config (supplies `archive_dir`).
        primary: Absolute path of the named document.
        source: The `FILE` argument exactly as typed (carried into the
            `--json` record; never derived from `primary`, which is
            resolved and therefore always absolute).
        doc: The parsed primary — its `Related:` edges are the candidate
            set.
        scope: The `--cascade-only` value as typed, or None.
        date_str: The archive date, already in the tree's `date_format`.
        reason: The `--reason` value, or None; it applies to the primary
            only.
    """
    dest = _archive_destination(root, config, date_str, primary.name)
    primary_move = ArchiveMove(
        path=primary,
        rel=_root_relative(primary, root),
        aliases=(),
        verb=None,
        dest=dest,
        dest_rel=_root_relative(dest, root),
        selected=True,
        exclusion_reason=None,
    )

    candidates: list[ArchiveMove] = []
    for candidate in archive_candidates(doc, root, config, scope):
        if not candidate.selected:
            candidates.append(candidate)
            continue
        cdest = _archive_destination(root, config, date_str, candidate.path.name)
        candidates.append(replace(candidate, dest=cdest, dest_rel=_root_relative(cdest, root)))

    return ArchivePlan(
        root=root,
        config=config,
        primary=primary_move,
        candidates=tuple(candidates),
        scope=scope,
        date_str=date_str,
        reason=reason,
        source=source,
    )


def preflight_archive_plan(plan: ArchivePlan) -> None:
    """Prove every plan member writable before the first byte moves (M26 — D4).

    Validate-all-first: the five proofs `cli.md` § *The scoped write and its
    pre-flight* lists, each over the whole plan, so a handled failure refuses
    the WHOLE operation with zero mutation — the primary included. Each
    refusal raises `CoordinatedWriteError` with `rolled_back=True` and
    `published=()`, because the tree is trivially unchanged, and carries the
    Phase-1 Q4 exit code: **1** for the two conditions 1.x already owned (no
    editable metadata block; an occupied destination slot), **2** for the
    four new M26 refusals.

    Deliberately exactly two `os.access` checks — the source FILE and the
    destination directory. A source-PARENT-directory check is NOT one of
    them: a `0o644` file inside a `0o555` directory is genuinely writable by
    that test and must be admitted here, failing later as the D4 residual
    partial-state admission. That is the milestone's only end-to-end
    partial-state lock, and it is also why `apply_relate_plan` (M25 — D5)
    refuses to add the same check.

    Raises:
        CoordinatedWriteError: any of the five proofs fails.
    """
    for move in plan.moves:
        try:
            parse_metadata_block(move.path.read_text())
        except MetadataError as exc:
            raise CoordinatedWriteError(
                f"{move.rel} has no editable metadata block; refusing before any write",
                rolled_back=True,
                published=(),
                exit_code=1,
            ) from exc

    for move in plan.moves:
        if _is_archived_rel(move.rel, plan.config):
            raise CoordinatedWriteError(
                f"{move.rel} is already under the archive subtree; refusing before any write",
                rolled_back=True,
                published=(),
            )

    for move in plan.moves:
        # Every member of `moves` is selected, so `plan_archive` has filled
        # its destination.
        assert move.dest is not None and move.dest_rel is not None
        if move.dest.exists():
            raise CoordinatedWriteError(
                f"archive destination already exists: {move.dest_rel} (for {move.rel}); "
                "refusing before any write",
                rolled_back=True,
                published=(),
                exit_code=1,
            )

    claimed: dict[str, str] = {}
    for move in plan.moves:
        assert move.dest_rel is not None
        if move.dest_rel in claimed:
            raise CoordinatedWriteError(
                f"{claimed[move.dest_rel]} and {move.rel} would both archive to "
                f"{move.dest_rel}; refusing before any write",
                rolled_back=True,
                published=(),
            )
        claimed[move.dest_rel] = move.rel

    for move in plan.moves:
        if not os.access(move.path, os.W_OK):
            raise CoordinatedWriteError(
                f"{move.rel} is not writable; refusing before any write",
                rolled_back=True,
                published=(),
            )

    # The dated directory usually does not exist yet, so the nearest EXISTING
    # ancestor is the one that has to be writable. The walk terminates: the
    # docs root exists.
    assert plan.primary.dest is not None
    ancestor = plan.primary.dest.parent
    while not ancestor.exists():
        ancestor = ancestor.parent
    if not os.access(ancestor, os.W_OK):
        raise CoordinatedWriteError(
            f"{_root_relative(ancestor, plan.root)} is not writable; refusing before any write",
            rolled_back=True,
            published=(),
        )


def apply_archive_plan(plan: ArchivePlan) -> list[tuple[str, str]]:
    """Execute a validated `ArchivePlan` in order (M26 — D4).

    Drives `_archive_one` — unchanged since M2 — over `plan.moves`, primary
    first. `--reason` is written onto the primary only (Phase-1 Q10).

    Returns the `(old_rel, new_rel)` pairs `_rewrite_referring_edges`
    consumes: the canonical pair per member plus **one extra pair per
    declared spelling** (Phase-1 Q5), so a `./b.md` bullet elsewhere in the
    tree is repointed exactly like a `b.md` one.

    There is no rollback (D4, deliberately). Every failure the tool can
    foresee was refused by `preflight_archive_plan`; an unexpected `OSError`
    here — or a `MetadataError` the pre-flight's proof says is unreachable,
    caught anyway so a wrong assumption surfaces as an admission rather than
    a traceback — becomes the exact partial-state admission.

    Raises:
        CoordinatedWriteError: a member's write failed; `published` names
            what really moved and `rolled_back` is False.
    """
    published: list[ArchiveMove] = []
    pairs: list[tuple[str, str]] = []
    for index, move in enumerate(plan.moves):
        try:
            _archive_one(
                move.path,
                plan.root,
                plan.config,
                plan.date_str,
                plan.reason if index == 0 else None,
            )
        except (MetadataError, OSError) as exc:
            raise _archive_partial_state(plan, move, exc, published) from exc
        published.append(move)
        assert move.dest_rel is not None
        pairs.append((move.rel, move.dest_rel))
        pairs.extend((alias, move.dest_rel) for alias in move.aliases if alias != move.rel)
    return pairs


def _archive_partial_state(
    plan: ArchivePlan,
    failed: ArchiveMove,
    exc: Exception,
    published: list[ArchiveMove],
) -> CoordinatedWriteError:
    """Build the D4 residual partial-state admission for a failed execution.

    Names what moved and what did not, in execution order, so the message is
    checkable against the disk line by line. An empty archived list renders
    as the literal word `none` — never as a blank (the M25 `_rollback_relate`
    lesson).

    When nothing had moved, the dated directory `_archive_one` creates before
    its first write is pruned: it `mkdir`s the destination parent BEFORE
    `atomic_write`, so a first-member failure would otherwise leave an empty
    `archive/<date>/` behind and a refusal that promised zero mutation would
    have changed the tree. `rmdir` is suppressed because a non-empty
    directory (an earlier archive on the same date) must be left alone.
    """
    if published:
        archived = ", ".join(f"{move.rel} -> {move.dest_rel}" for move in published)
    else:
        archived = "none"
        assert plan.primary.dest is not None
        dated = plan.primary.dest.parent
        for directory in (dated, dated.parent):
            with contextlib.suppress(OSError):
                directory.rmdir()

    remaining = ", ".join(move.rel for move in plan.moves[len(published) :])
    return CoordinatedWriteError(
        f"write failed for {failed.rel}: {exc}; PARTIAL ARCHIVE — not rolled back. "
        f"Archived: {archived}. Still at their original paths: {remaining}. Repair manually.",
        rolled_back=False,
        published=tuple(move.rel for move in published),
    )


def _archive_one(path: Path, root: Path, config: Config, date_str: str, reason: str | None) -> Path:
    """Archive a single doc: edit metadata, then move it into the dated dir.

    Sets `Lifecycle: archived`, bumps `Updated:` to `date_str`, and appends an
    `Archived-reason:` line when `reason` is given.

    Ordering is the atomicity contract (cf. `cli.md` §archive). The
    edited text is committed to the *original* path via `atomic_write`
    (tmpfile + rename — see `atomic_write`) BEFORE the
    `path.replace(dest)` move. A failure in the metadata edit raises
    before the move, so the original doc is left untouched; the move
    runs only once the edit has landed. The archive destination's
    existence is checked first so an occupied slot fails fast (no
    partial edit-then-collide). Returns the doc's new path.

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


def archive_plan_to_json(
    plan: ArchivePlan, *, dry_run: bool, applied: bool, index_refreshed: bool
) -> dict[str, object]:
    """Convert an `ArchivePlan` to its `docs archive --json` record (M26 — D7).

    One object with the same shape for a preview and for a real apply, so
    the two are diffable (the schema `cli.md` pins). The top-level key set is
    closed and ordered as written here. `primary.source` is the `FILE`
    argument exactly as typed; every other path is canonical root-relative
    POSIX. `candidates` carries the WHOLE deduplicated one-hop set in
    `Related:` declaration order, in every mode — D1's quiet rule governs
    stderr prose, not the record (Phase-1 Q14).

    Args:
        plan: The plan produced by `plan_archive`.
        dry_run: True under `--dry-run` or `--cascade-dry-run`.
        applied: True iff bytes were actually written.
        index_refreshed: True iff the end-of-batch reindex ran and succeeded.

    Returns:
        A JSON-serialisable record dict.
    """
    return {
        "primary": {
            "source": plan.source,
            "path": plan.primary.rel,
            "destination": plan.primary.dest_rel,
        },
        "date": plan.date_str,
        "scope": plan.scope,
        "reason": plan.reason,
        "candidates": [
            {
                "path": candidate.rel,
                "verb": candidate.verb,
                "selected": candidate.selected,
                "destination": candidate.dest_rel,
                "exclusion_reason": candidate.exclusion_reason,
            }
            for candidate in plan.candidates
        ],
        "dry_run": dry_run,
        "applied": applied,
        "index_refreshed": index_refreshed,
    }


# M26 (D6): the human prose for each INELIGIBILITY token. `not-selected` is
# absent deliberately — it is not an ineligibility, its line depends on
# whether a scope was given, and membership in this mapping is what the
# counts footer uses to tell "ineligible" from "not selected".
_ARCHIVE_INELIGIBLE_PROSE: Mapping[str, str] = {
    "already-archived": "already archived",
    "unresolved-target": "target does not resolve to a file",
    "outside-root": "target resolves outside the docs root",
}


def _candidate_state(candidate: ArchiveMove, scope: str | None) -> str:
    """The frozen `— <state>` half of a preview/apply `candidate` line."""
    if candidate.selected:
        return f"selected -> {candidate.dest_rel}"
    if candidate.exclusion_reason == "not-selected":
        if scope is None:
            return "not selected (no --cascade-only scope)"
        return f"not selected (outside --cascade-only '{scope}')"
    # An unselected candidate always carries a reason.
    assert candidate.exclusion_reason is not None
    return f"ineligible ({_ARCHIVE_INELIGIBLE_PROSE[candidate.exclusion_reason]})"


def _print_archive_lines(plan: ArchivePlan, *, dry_run: bool, cascade: bool) -> None:
    """Print `docs archive`'s human summary to stderr (M26 — D6).

    The primary's line always; then, only when a cascade flag is present,
    one line per candidate with its state, the `matched none` line when a
    scope selected nothing, and the counts footer. That gate is D1's quiet
    rule: a plain `docs archive FILE` says nothing about the candidates it
    leaves in place, because a notice on every single-document archive would
    be noise and the safe behaviour needs no announcement.

    `cascade` is a parameter rather than a property of the plan because the
    plan cannot distinguish the two invocations that produce it:
    `--cascade-dry-run` with no scope (candidate lines REQUIRED) and a plain
    `--dry-run` (candidate lines FORBIDDEN) both yield ``scope is None``.

    The candidate lines are identical in preview and apply — a scoped write
    is all-or-nothing, so the plan is what happened. Only the primary's verb
    and the trailing `preview only` line carry the mode.

    Gated by the caller on `not --quiet` alone — NOT on `--json`: these go to
    stderr, so `--json` stdout stays byte-clean either way.
    """
    verb = "would archive" if dry_run else "archived"
    print(
        f"docs: archive: {verb} {plan.primary.rel} -> {plan.primary.dest_rel}",
        file=sys.stderr,
    )
    if not cascade:
        return

    for candidate in plan.candidates:
        print(
            f"docs: archive: candidate {candidate.rel} — {_candidate_state(candidate, plan.scope)}",
            file=sys.stderr,
        )

    selected = sum(1 for c in plan.candidates if c.selected)
    ineligible = sum(1 for c in plan.candidates if c.exclusion_reason in _ARCHIVE_INELIGIBLE_PROSE)
    if plan.scope is not None and plan.candidates and not selected:
        print(
            f"docs: archive: --cascade-only '{plan.scope}' matched none of the "
            f"{len(plan.candidates)} one-hop candidate(s)",
            file=sys.stderr,
        )
    print(
        f"docs: archive: {len(plan.candidates)} candidate(s): {selected} selected, "
        f"{len(plan.candidates) - selected - ineligible} not selected, "
        f"{ineligible} ineligible",
        file=sys.stderr,
    )
    if dry_run:
        print("docs: archive: preview only — nothing was written", file=sys.stderr)


def _cmd_archive(args: argparse.Namespace) -> int:
    # M26 (D1-D7) — the check order `cli.md` freezes, every step before any
    # write. Steps 1 and 2 run before any filesystem access at all, so
    # neither refusal can depend on the state of the tree.

    # 1 — the retired flags. One template, two flags, `--cascade` first
    # (declaration order decides when both are passed). Unconditional: no
    # other flag, and no combination, changes the outcome (D2).
    for flag, passed in (("--cascade", args.cascade), ("--interactive", args.interactive)):
        if passed:
            print(
                f"docs: archive: {flag} is retired in docs 2.0 and writes nothing; "
                "preview with `docs archive <file> --cascade-dry-run`, then write an "
                "explicit scope with `docs archive <file> --cascade-only '<glob>'`",
                file=sys.stderr,
            )
            return 2

    # 2 — the `--cascade-only` shape. Purely lexical, so it precedes the
    # missing-file check. A blank / comment-only / negated pattern is a
    # MALFORMED INVOCATION, not a selection outcome, so it refuses in every
    # mode — a preview included (D6's "a preview never fails" governs a valid
    # glob that selects nothing).
    scope: str | None = args.cascade_only
    if scope is not None:
        compiled = _compile_docsignore_pattern(scope)
        if compiled is None:
            print("docs: archive: --cascade-only must not be empty", file=sys.stderr)
            return 2
        if compiled[0]:
            print(
                "docs: archive: --cascade-only does not support negated ('!') patterns; "
                "state the exact bounded selection",
                file=sys.stderr,
            )
            return 2

    # 3 — the primary exists, the root and config load, `--date` parses, the
    # primary parses.
    file_path = Path(args.file)
    if not file_path.is_file():
        print(f"docs: file not found: {file_path}", file=sys.stderr)
        return 1

    root = (Path(args.root) if args.root else find_root(file_path.parent)).resolve()
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

    # Both sides resolved before any rel is derived: `_root_relative` falls
    # back to the bare filename for a path it cannot relativise, which would
    # silently mis-name a `sub/x.md` primary given relatively.
    primary = file_path.resolve()

    # ...and that fallback is exactly why the primary must be PROVEN to lie
    # under the root before anything else happens. A symlink pointing out of
    # the tree, or a `--root` naming a different tree, otherwise yields a
    # fabricated in-tree rel — and the archive would move a foreign file INTO
    # this tree, name it in the record as though it had always lived here, and
    # exit 0. 1.x raised `ValueError` here and hard-stopped; this restores that
    # stop, at the same exit 1 and in the same words `touch`, `stamp`,
    # `project set`, and `relate` already use for the condition.
    if not primary.is_relative_to(root):
        print(
            f"docs: archive: {primary} is outside the resolved docs root ({root}); "
            "refusing before any write",
            file=sys.stderr,
        )
        return 1

    try:
        doc = parse(primary.read_text(), primary, root)
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        # An unreadable primary. Same mapping as an unreadable plan member and
        # an unreadable referring doc: one clean exit 2, never a traceback.
        print(f"docs: archive: {exc}", file=sys.stderr)
        return 2

    # 4 — an already-archived primary is a refusal in all three D1 shapes
    # (Phase-1 Q1), checked before the plan so it wins over an empty
    # selection: re-archiving history is the more fundamental fact.
    primary_rel = _root_relative(primary, root)
    if _is_archived_rel(primary_rel, config):
        print(
            f"docs: archive: {primary_rel} is already under the archive subtree; "
            "refusing before any write",
            file=sys.stderr,
        )
        return 2

    # 5 — the plan. Pure: nothing is written, whatever happens next.
    plan = plan_archive(
        root,
        config,
        primary=primary,
        source=args.file,
        doc=doc,
        scope=scope,
        date_str=date_str,
        # `--reason ""` is dropped rather than carried: `_archive_one`'s
        # `if reason:` already declines to write an empty `Archived-reason:`,
        # so a record carrying `""` would MISDESCRIBE the file it reports on —
        # the one thing the D7 record exists to prevent.
        reason=args.reason or None,
    )
    # `--cascade-dry-run` previews the neighbourhood with or without a scope;
    # a bare `--dry-run` does not (D1's quiet rule).
    cascade = args.cascade_dry_run or scope is not None
    is_dry = args.dry_run or args.cascade_dry_run

    def _emit_json(*, applied: bool, index_refreshed: bool) -> None:
        if args.json:
            print(
                json.dumps(
                    archive_plan_to_json(
                        plan,
                        dry_run=is_dry,
                        applied=applied,
                        index_refreshed=index_refreshed,
                    ),
                    indent=2,
                )
            )

    # A preview is never a write, so it never fails: it stops here at exit 0
    # even when the scope selected nothing (D6 / Phase-1 Q2).
    if is_dry:
        if not args.quiet:
            _print_archive_lines(plan, dry_run=True, cascade=cascade)
        _emit_json(applied=False, index_refreshed=False)
        return 0

    # 6 — an empty selection on a WRITE is a refusal, and says which case it
    # is (D5). `<N>` counts the whole deduplicated set, ineligible members
    # included: "matched" means SELECTED.
    if scope is not None and not any(candidate.selected for candidate in plan.candidates):
        if plan.candidates:
            print(
                f"docs: archive: --cascade-only '{scope}' matched none of the "
                f"{len(plan.candidates)} one-hop candidate(s); refusing before any write",
                file=sys.stderr,
            )
        else:
            print(
                f"docs: archive: {primary_rel} has no one-hop pairs-with / child-of "
                "candidates; refusing before any write (use `docs archive <file>` to "
                "archive it alone)",
                file=sys.stderr,
            )
        return 2

    # 7 — the plan pre-flight, deliberately BEFORE the whole-tree walk: both
    # can fire on the same malformed file, and naming the document the
    # operator asked for is strictly more actionable. `CoordinatedWriteError`
    # is an `OSError` subclass, so it must be caught first wherever both
    # appear, or every refusal is swallowed by the generic handler.
    try:
        preflight_archive_plan(plan)
    except CoordinatedWriteError as exc:
        print(f"docs: archive: {exc}", file=sys.stderr)
        return exc.exit_code
    except OSError as exc:
        # An unenumerated read failure — an existing but unreadable plan
        # member reaches the pre-flight's `read_text()` before its writability
        # is ever tested. Mapped to the same clean exit 2 as the M14 (A4)
        # rewrite failure rather than a traceback; the pre-flight has written
        # nothing, so the tree is still untouched. Must come AFTER the
        # `CoordinatedWriteError` clause, which is a subclass.
        print(f"docs: archive: {exc}", file=sys.stderr)
        return 2

    # 8 — M12 / M14 (A6): the whole-tree validation walk, which catches a
    # malformed REFERRING doc before the move so a later edge rewrite cannot
    # leave a half-archived tree. Honours [exclude] / .docsignore, as does
    # the end-of-batch reindex.
    predicate = compile_exclude_predicate(config, [])
    try:
        list(walk(root, config, predicate=predicate))
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        # An unreadable REFERRING doc. Malformed is exit 1 (unchanged since
        # M12); unreadable is the third face of the same condition as the
        # unreadable primary and plan member, and gets their single clean
        # exit 2 rather than a traceback.
        print(f"docs: archive: {exc}", file=sys.stderr)
        return 2

    # 9 — execution. All-or-nothing by construction; the only residual is an
    # unexpected `OSError`, admitted exactly and never rolled back (D4).
    try:
        moves = apply_archive_plan(plan)
    except CoordinatedWriteError as exc:
        print(f"docs: archive: {exc}", file=sys.stderr)
        return 2

    # M12 / M18: repoint every referring `Related:` bullet — active tree and
    # the narrow archive-subtree exception — in one batch with the move.
    try:
        _rewrite_referring_edges(root, config, moves, predicate=predicate)
    except (MetadataError, VocabularyError, OSError) as exc:
        # M14 (A4). No `--json` record: the operation did not complete.
        print(f"docs: archive: {exc}", file=sys.stderr)
        return 2

    # Announce only what actually happened, and only once the writes landed.
    if not args.quiet:
        _print_archive_lines(plan, dry_run=False, cascade=cascade)

    # The one post-write failure that still emits a record (Phase-1 Q3): every
    # document moved correctly, so `applied` is true and the caller needs to
    # know the INDEX is stale.
    index_refreshed = True
    try:
        _refresh_index(root, config, predicate=predicate)
    except (MetadataError, VocabularyError, OSError) as exc:
        print(f"docs: INDEX refresh failed: {exc}", file=sys.stderr)
        index_refreshed = False

    _emit_json(applied=True, index_refreshed=index_refreshed)
    return 0 if index_refreshed else 2


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

    # M14 (A6): the reindex / rewrite walks honour persistent [exclude] /
    # .docsignore (no new CLI flag), so a malformed *excluded* file never
    # fails the post-move walk.
    predicate = compile_exclude_predicate(config, [])

    # M14 (A1): validate-all-first pre-flight walk BEFORE the move, so a
    # malformed sibling aborts cleanly (exit 2) leaving the source in
    # place + the destination absent + referring edges untouched. Without
    # this, `old_path.replace(new_path)` runs first and the rewrite walk
    # raises afterwards — a dangling edge + a non-atomic half-move. Mirrors
    # the archive pre-flight, but exits 2 (not archive's 1): mv has no
    # legacy exit-1 referring-edge contract (RQ#8).
    try:
        list(walk(root, config, predicate=predicate))
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 2

    new_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.replace(new_path)

    try:
        rewrites = 0
        for doc in walk(root, config, predicate=predicate):
            updated_text, n = rewrite_related_refs(doc.path.read_text(), old_rel, new_rel)
            if n:
                atomic_write(doc.path, updated_text)
                rewrites += n
        _refresh_index(root, config, predicate=predicate)
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        # M14 (A4): an OSError mid-rewrite (e.g. a referrer in a read-only
        # directory) is mapped to a clean exit 2 rather than escaping as a
        # traceback after the move.
        print(f"docs: mv: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(
            f"docs: moved {old_rel} -> {new_rel} ({rewrites} reference(s) rewritten)",
            file=sys.stderr,
        )
    return 0


def _cmd_touch(args: argparse.Namespace) -> int:
    # M19 (Q3): `--stale` is only meaningful as `--check`'s window. Passing
    # it without `--check` is an incoherent-flag hard refusal (exit 2) — the
    # guard precedes every path read so the file stays byte-unchanged.
    if args.stale is not None and not args.check:
        print("docs: touch: --stale requires --check", file=sys.stderr)
        return 2

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

    # M12 (OQ-C / OQ-11): refuse outside any docs root. Resolution
    # happens AFTER the file-existence check (OQ-β) so the existing
    # missing-file → exit 1 contract is preserved; an explicit
    # `--root` is validated against `.docs.toml` presence in
    # `_resolve_managed_root`. The first file's path (not its parent)
    # is named in the refusal message so the operator sees the
    # offending doc.
    start = file_paths[0] if file_paths else Path.cwd()
    root_or_exit = _resolve_managed_root(args, start, verb="touch")
    if isinstance(root_or_exit, int):
        return root_or_exit
    root = root_or_exit

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
        # M19 (Q4): `--dry-run --check` previews the touch and runs the check
        # against the UN-MUTATED on-disk tree (no INDEX refresh runs under
        # dry-run, so a doc the dry-run would refresh may still read as stale).
        if args.check:
            return _run_touch_check(root, config, args.stale)
        return 0

    for fp, new_text in rewrites:
        atomic_write(fp, new_text)

    # OQ-C: single end-of-batch INDEX refresh. M14 (A6): honour persistent
    # [exclude] / .docsignore so a malformed *excluded* file (e.g. a
    # bundled plugin README) never fails the post-stamp reindex — the
    # dates are already written, so an unfiltered raise here is a partial,
    # non-atomic result.
    try:
        _refresh_index(root, config, predicate=compile_exclude_predicate(config, []))
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: INDEX refresh failed: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        for fp, _ in rewrites:
            print(f"docs: touched {fp}", file=sys.stderr)

    # M19 (Q1): touch succeeded (0). With --check, fold the tree-wide check's
    # 0/1/2 into the command's exit code. (Every earlier touch failure already
    # returned 1/2 above, so the touch-fail short-circuit is automatic.)
    if args.check:
        return _run_touch_check(root, config, args.stale)
    return 0


def _run_touch_check(root: Path, config: Config, cli_stale: int | None) -> int:
    """Run `docs touch --check`'s tree-wide validation; return its exit code.

    Mirrors bare `docs check` over the resolved root (M19 — D1/Q2): the same
    `[exclude]` / `.docsignore` predicate parity (Q-F), the same
    CLI-`--stale` > `[check] stale_days` > unset resolution + provenance
    (D2), and the same grouped human output on stdout via the shared
    `_print_check_findings`. Findings print regardless of `--quiet` (Q-E —
    `--quiet` gates only touch's own stderr lines). No `--json` mode in M19
    (OQ-5 — deliberate non-goal).
    """
    predicate = compile_exclude_predicate(config, [])
    window, source = resolve_stale(cli_stale, config.stale_days)
    findings = check_tree(
        root, config, window, date.today(), predicate=predicate, stale_source=source
    )
    _print_check_findings(findings, root)
    return exit_code_for(findings)


def _rewrite_sidecar_project_name(text: str, old: str, new: str) -> str:
    """Rewrite the `.docs.toml` `[project] name = "<old>"` line to `name = "<new>"`.

    Surgical, minimal-diff rewrite: only the matching line is touched
    (single replacement; the rest of the file is byte-identical). If
    the expected `name = "<old>"` line is absent, returns `text`
    unchanged; the caller treats that as a malformed-sidecar error.
    """
    pattern = rf'^name[ \t]*=[ \t]*"{re.escape(old)}"[ \t]*$'
    return re.sub(pattern, f'name = "{new}"', text, count=1, flags=re.MULTILINE)


def _print_project_rename_footer(
    old_name: str,
    new_name: str,
    rewrites: int,
    archived_count: int,
    non_matching: dict[str, int],
    dry_run: bool,
) -> None:
    """Print the M12 (OQ-2) single-line project-rename success footer.

    Drops empty clauses when their counts are 0. `dry_run` is accepted
    so callers can suppress; today it is always passed True/False but
    the footer text is the same shape — the caller decides emission.
    """
    clauses = [f"rewrote .docs.toml + {rewrites} doc(s)"]
    if archived_count:
        clauses.append(f"{archived_count} archived skipped")
    if non_matching:
        total = sum(non_matching.values())
        names = ", ".join(sorted(non_matching.keys()))
        clauses.append(f"{total} non-matching project(s) untouched: {names}")
    body = "; ".join(clauses)
    print(f"docs: project rename: {old_name} -> {new_name} ({body})", file=sys.stderr)


def _rewrite_referring_edges(
    root: Path,
    config: Config,
    moves: list[tuple[str, str]],
    predicate: Callable[[str], bool] | None = None,
) -> None:
    """Walk the whole tree once; rewrite `Related:` bullets per (old, new) move.

    Reuses `rewrite_related_refs` per (old_rel, new_rel) pair; atomic-writes
    touched docs. M12 helper shared by `_cmd_archive` (single-move) and
    `_cmd_archive --cascade` (batch). M14 (A6): the optional `predicate` is
    threaded into `walk` so a malformed *excluded* file never fails this
    rewrite walk.

    M18 (D2/Q4) — archive-subtree edge integrity. Archived docs are skipped
    by default (the M3 "archive subtree is read-only by convention" stance),
    EXCEPT when one of their `Related:` targets equals a batch `old_rel` —
    i.e. the archived doc references a doc that is moving in THIS archival.
    In that narrow case the archived referrer's edge IS repointed to the new
    archive path, so an already-archived doc whose target sweeps into the
    archive does not dangle. The exception is move-driven only: the
    `rewrite_related_refs` matcher rewrites a bullet iff its target ==
    `old_rel`, so no non-moving edge, prose, or other metadata of an archived
    doc is ever touched. `old_rels` is the set of batch move sources used to
    gate the otherwise-unconditional archived skip.
    """
    if not moves:
        return
    old_rels = {old for old, _new in moves}
    for doc in walk(root, config, predicate=predicate):
        # M18 (D2/Q4): skip archived docs UNLESS one of their `Related:`
        # targets is moving in this batch — then repoint that edge (the
        # narrow move-driven exception to the M3 read-only stance).
        if doc.archived and not any(target in old_rels for _verb, target in doc.related):
            continue
        text = doc.path.read_text()
        original = text
        for old_rel, new_rel in moves:
            text, _n = rewrite_related_refs(text, old_rel, new_rel)
        if text != original:
            atomic_write(doc.path, text)


def _cmd_project_rename(args: argparse.Namespace) -> int:
    # M12 — atomic project rename across .docs.toml + every conformant
    # `Project:` line in every active doc. Validate-then-commit-then-
    # INDEX-once, mirroring `_cmd_touch`. OQ-α through OQ-ι decisions
    # apply throughout.

    # OQ-1: refuse cleanly when no .docs.toml ancestor.
    root_or_exit = _resolve_managed_root(args, Path.cwd(), verb="project rename")
    if isinstance(root_or_exit, int):
        return root_or_exit
    root = root_or_exit

    try:
        config = load_config(root)
    except tomllib.TOMLDecodeError as exc:
        print(f"docs: malformed .docs.toml: {exc}", file=sys.stderr)
        return 2

    # OQ-A — auto-normalise the operator-supplied input via M7's
    # `normalise_project_name()`. Empty / whitespace input rejected
    # post-normalisation (OQ-9). Normalisation note gated on `not
    # --quiet`.
    raw = args.new_name
    normalised = normalise_project_name(raw)
    if not normalised.strip():
        print(
            f"docs: project rename: {raw} normalises to empty string; "
            "project name must be non-empty",
            file=sys.stderr,
        )
        return 2
    if normalised != raw and not args.quiet:
        print(
            f'docs: project rename: normalised "{raw}" to "{normalised}"',
            file=sys.stderr,
        )
    new_name = normalised

    # OQ-3: compare normalised-new against the sidecar `[project] name`
    # as written. No double-normalisation.
    old_name = config.project

    # M14 (A6): both the validate-all-first walk and the end-of-batch
    # reindex honour persistent [exclude] / .docsignore (no new CLI flag),
    # so a malformed *excluded* file never fails either walk.
    predicate = compile_exclude_predicate(config, [])

    # Validate-all-first walk: parse every active doc, bucket into
    # matching vs. non-matching, count archived. A MetadataError or
    # VocabularyError on any doc aborts the whole batch before any
    # write. `parse()` prefixes the offending path on every error it
    # bubbles, so `exc` is self-locating.
    matching: list[Path] = []
    archived_count = 0
    non_matching: dict[str, int] = {}
    try:
        for doc in walk(root, config, predicate=predicate):
            if doc.archived:
                archived_count += 1
                continue
            # OQ-γ-bis: docs without explicit Project: resolve to
            # config.project; treated as implicitly matching, so
            # set_metadata_field inserts a Project: line.
            resolved = _resolved_project(doc, config)
            if resolved == old_name:
                matching.append(doc.path)
            else:
                non_matching[resolved] = non_matching.get(resolved, 0) + 1
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 1

    # No-op test: new equals old AND no rewrites planned (the latter
    # is implicit — if matching list is empty, the only writes would
    # be a sidecar self-rewrite that produces byte-identical output).
    if new_name == old_name:
        if not args.quiet:
            print(
                f"docs: project rename: {new_name} already current — no rewrites needed",
                file=sys.stderr,
            )
        return 0

    # Build the doc rewrite plan. `set_metadata_field` inserts a
    # Project: line for docs that did not have one (OQ-γ-bis).
    doc_writes: list[tuple[Path, str]] = []
    for path in matching:
        try:
            new_text = set_metadata_field(path.read_text(), "Project", new_name)
        except MetadataError as exc:
            print(f"docs: {exc}", file=sys.stderr)
            return 1
        doc_writes.append((path, new_text))

    # Build the sidecar rewrite. An absent / unparseable `name =
    # "<old>"` line is a malformed sidecar.
    sidecar_path = root / ".docs.toml"
    sidecar_text = sidecar_path.read_text()
    new_sidecar = _rewrite_sidecar_project_name(sidecar_text, old_name, new_name)
    if new_sidecar == sidecar_text:
        print(
            f'docs: malformed .docs.toml: missing or unparseable name = "{old_name}" line',
            file=sys.stderr,
        )
        return 2

    root_resolved = root.resolve()

    if args.dry_run:
        if not args.quiet:
            for path, _ in doc_writes:
                rel = path.resolve().relative_to(root_resolved).as_posix()
                print(f"docs: would rewrite Project: in {rel}", file=sys.stderr)
            print(
                f'docs: would rewrite [project] name in .docs.toml: "{old_name}" -> "{new_name}"',
                file=sys.stderr,
            )
            _print_project_rename_footer(
                old_name,
                new_name,
                len(doc_writes),
                archived_count,
                non_matching,
                dry_run=True,
            )
        return 0

    # Commit phase: every doc, then the sidecar.
    for path, new_text in doc_writes:
        atomic_write(path, new_text)
    atomic_write(sidecar_path, new_sidecar)

    # INDEX refresh: reload config so the new project name renders. M14
    # (A6): reuse the original exclude predicate — exclude rules
    # (dirs/globs/exts/.docsignore) do not depend on the project name, so
    # they are stable across the rename.
    try:
        _refresh_index(root, load_config(root), predicate=predicate)
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: INDEX refresh failed: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        _print_project_rename_footer(
            old_name,
            new_name,
            len(doc_writes),
            archived_count,
            non_matching,
            dry_run=False,
        )
    return 0


def _known_projects(root: Path, config: Config) -> set[str]:
    """Return the set of known projects in `root` for the `project set` typo guard.

    The resolved `Project:` of every **active** doc (its explicit `Project:`,
    or the docs-root project for a doc with none) plus the `.docs.toml`
    `[project] name` (M15 — B2; resolved Q1). The walk **tolerates** parse
    errors — an unparseable doc is skipped, never aborting the guard — and
    always seeds `config.project`, so a tree of all-malformed docs still has
    its root project in the known set.
    """
    known: set[str] = {config.project}
    archive_prefix = config.archive_dir
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in filenames:
            if fname.startswith(".") or not fname.endswith(".md"):
                continue
            file_path = Path(dirpath) / fname
            rel = file_path.relative_to(root).as_posix()
            if rel == INDEX_FILENAME:
                continue
            if rel == archive_prefix or rel.startswith(archive_prefix + "/"):
                continue
            try:
                doc = parse(file_path.read_text(), file_path, root)
            except (MetadataError, VocabularyError):
                continue
            known.add(_resolved_project(doc, config))
    return known


def _cmd_project_set(args: argparse.Namespace) -> int:
    # M15 (B2) — reassign the `Project:` field of one or more named docs.
    # Validate-all-first atomic semantics (mirrors `_cmd_touch` /
    # `_cmd_project_rename`): no write until every named doc passes. Never
    # touches `.docs.toml`, non-named docs, or `Related:` edges.

    # Grammar: a single nargs="+" run split as `*docs, new_project`. At least
    # two tokens — a single token is ambiguous (doc or project?).
    *docs, raw_new = args.args
    if not docs:
        print(
            "docs: project set: need at least one <doc> and a <new-project>",
            file=sys.stderr,
        )
        return 2

    # Resolve the docs root (verb-specific prefix; NOT `project rename:`).
    root_or_exit = _resolve_managed_root(args, Path.cwd(), verb="project set")
    if isinstance(root_or_exit, int):
        return root_or_exit
    root = root_or_exit

    try:
        config = load_config(root)
    except tomllib.TOMLDecodeError as exc:
        print(f"docs: malformed .docs.toml: {exc}", file=sys.stderr)
        return 2

    # Auto-normalise the new project name. Empty / whitespace-after-normalise
    # is rejected BEFORE the typo guard (the empty/whitespace tests pass
    # --new-project, which would otherwise bypass the guard).
    normalised = normalise_project_name(raw_new)
    if not normalised.strip():
        print(
            f"docs: project set: {raw_new} normalises to empty string; "
            "project name must be non-empty",
            file=sys.stderr,
        )
        return 2
    if normalised != raw_new and not args.quiet:
        print(
            f'docs: project set: normalised "{raw_new}" to "{normalised}"',
            file=sys.stderr,
        )

    # Typo guard (skipped when --new-project): refuse a value new to the tree.
    if not args.new_project:
        known = _known_projects(root, config)
        if normalised not in known:
            close = difflib.get_close_matches(normalised, sorted(known), n=1)
            prefix = f"did you mean '{close[0]}'? " if close else ""
            print(
                f"docs: project set: '{normalised}' is not a project in this tree; refusing",
                file=sys.stderr,
            )
            print(
                f"  → {prefix}to create a new project group, pass --new-project",
                file=sys.stderr,
            )
            return 2

    # Validate-all-first: resolve every named doc's path + parse it. No writes
    # until all pass. The archived check (path-based) takes PRECEDENCE over
    # missing / outside / malformed (resolved Q4) and is ORDER-INDEPENDENT: it
    # runs as a dedicated pre-pass over EVERY named doc, so a batch with any
    # archived token refuses (exit 2) regardless of where that token sits
    # relative to a missing / outside / malformed one.
    root_resolved = root.resolve()
    archive_dir = config.archive_dir

    # Archived-only pre-pass: if ANY named doc's root-relative first segment is
    # the archive dir, refuse the whole batch (exit 2) naming the path — even
    # when other tokens are missing / outside / malformed.
    for raw_doc in docs:
        doc_path = Path(raw_doc)
        target = doc_path if doc_path.is_absolute() else root / doc_path
        try:
            arc_rel = target.resolve().relative_to(root_resolved).as_posix()
        except ValueError:
            continue  # outside the root → cannot be archived; deferred to next pass
        if arc_rel == archive_dir or arc_rel.startswith(archive_dir + "/"):
            print(
                f"docs: project set: {arc_rel} is under the archive subtree (read-only); refusing",
                file=sys.stderr,
            )
            return 2

    # Existence / outside-root / malformed pass (exit 1 on the first failure).
    # Read + parse each doc exactly once here; the no-op/rewrite pass below
    # reuses that text + Doc (the file is untouched until every doc passes).
    planned: list[tuple[Path, str, Doc, str]] = []  # (path, root-relative posix, doc, text)
    for raw_doc in docs:
        doc_path = Path(raw_doc)
        target = doc_path if doc_path.is_absolute() else root / doc_path

        rel: str | None
        try:
            rel = target.resolve().relative_to(root_resolved).as_posix()
        except ValueError:
            rel = None

        # Outside the resolved root → exit 1 (explicit-path error, not a
        # no-root refusal — the cross-verb exit-code convention).
        if rel is None:
            print(
                f"docs: project set: {target} is outside the resolved docs root ({root_resolved})",
                file=sys.stderr,
            )
            return 1

        # Missing → exit 1.
        if not target.is_file():
            print(f"docs: project set: file not found: {target}", file=sys.stderr)
            return 1

        # Malformed (parse raises) → exit 1.
        text = target.read_text()
        try:
            doc = parse(text, target, root)
        except (MetadataError, VocabularyError) as exc:
            print(f"docs: {exc}", file=sys.stderr)
            return 1
        planned.append((target, rel, doc, text))

    # No-op: every named doc already resolves to the normalised project.
    rewrites: list[tuple[Path, str, str]] = []  # (path, rel, new_text)
    for target, rel, doc, text in planned:
        if _resolved_project(doc, config) == normalised:
            continue
        new_text = set_metadata_field(text, "Project", normalised)
        rewrites.append((target, rel, new_text))

    if not rewrites:
        if not args.quiet:
            print(
                f"docs: project set: {normalised} already current — no rewrites needed",
                file=sys.stderr,
            )
        return 0

    if args.dry_run:
        if not args.quiet:
            for _target, rel, _new_text in rewrites:
                print(f"docs: would rewrite Project: in {rel}", file=sys.stderr)
        return 0

    for target, _rel, new_text in rewrites:
        atomic_write(target, new_text)

    try:
        _refresh_index(root, config, predicate=compile_exclude_predicate(config, []))
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: INDEX refresh failed: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(
            f"docs: project set: set {normalised} on {len(rewrites)} doc(s)",
            file=sys.stderr,
        )
    return 0


def _resolve_relate_endpoint(raw: str, root: Path, root_resolved: Path) -> str | int:
    """Resolve one `relate` endpoint, or print a refusal and return its exit code.

    M25 (OQ-A): an absolute path is used as given; a relative one resolves
    **root-relative first**, falling back to cwd-relative only when the
    root-relative form is not a file. Root-relative-first is what lets an
    agent paste a path straight out of a `missing-inverse` finding.

    Returns the endpoint's root-relative POSIX form — the spelling every
    message and JSON field uses — or 1 when it is missing, outside the
    resolved root, or unparseable (the cross-verb explicit-path-error
    convention; nothing is written in any of the three cases).
    """
    given = Path(raw)
    if given.is_absolute():
        candidate = given
    else:
        # Root-relative is the primary interpretation, so it is also the
        # candidate a `file not found:` refusal names (M25 — R5).
        candidate = root / given
        if not candidate.is_file():
            from_cwd = Path.cwd() / given
            if from_cwd.is_file():
                candidate = from_cwd

    if not candidate.is_file():
        print(f"docs: relate: file not found: {candidate}", file=sys.stderr)
        return 1

    try:
        rel = candidate.resolve().relative_to(root_resolved).as_posix()
    except ValueError:
        print(
            f"docs: relate: {candidate} is outside the resolved docs root ({root_resolved})",
            file=sys.stderr,
        )
        return 1

    # Parse through `root / rel`, not the resolved path, so the parser's own
    # self-locating message names the file the way the tree does.
    endpoint = root / rel
    try:
        parse(endpoint.read_text(), endpoint, root)
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 1
    return rel


def _print_relate_lines(plan: RelatePlan, *, dry_run: bool) -> None:
    """Print `docs relate`'s human summary to stderr (M25 — D3).

    One line per endpoint plus one `recorded revision in <rel>` line per
    archived endpoint that gained an audit bullet (`would record …` under
    `--dry-run`). Gated by the caller on `not --quiet` alone — NOT on
    `--json`: these go to stderr, so `--json` stdout stays byte-clean
    either way.
    """
    # Every word that varies is fixed by the action and the mode, so they are
    # all chosen once, side by side, rather than re-derived per endpoint.
    if plan.action == "add":
        state, preposition = "already present in", "to"
        verb = "would add" if dry_run else "added"
    else:
        state, preposition = "already absent from", "from"
        verb = "would remove" if dry_run else "removed"
    recorded = "would record" if dry_run else "recorded"

    for edit in plan.edits:
        if edit.change == "unchanged":
            print(f"docs: relate: no change — '{edit.edge}' {state} {edit.rel}", file=sys.stderr)
        else:
            print(
                f"docs: relate: {verb} '{edit.edge}' {preposition} {edit.rel}",
                file=sys.stderr,
            )
    # A dry-run must preview the audit bullet too — otherwise an archived
    # repair's most consequential effect is invisible in the human preview
    # (the `--json` record has always carried `revision_appended`).
    for edit in plan.edits:
        if edit.revision_appended:
            print(f"docs: relate: {recorded} revision in {edit.rel}", file=sys.stderr)


def _cmd_relate(args: argparse.Namespace) -> int:
    # M25 (D3/D4/D5) — add or remove ONE reciprocal relationship pair across
    # exactly two documents. Validate-all-first: stage 1 below writes
    # nothing, so every refusal leaves the tree byte-identical.
    root_or_exit = _resolve_managed_root(args, Path.cwd(), verb="relate")
    if isinstance(root_or_exit, int):
        return root_or_exit
    root = root_or_exit

    try:
        config = load_config(root)
    except tomllib.TOMLDecodeError as exc:
        print(f"docs: malformed .docs.toml: {exc}", file=sys.stderr)
        return 2

    # The verb is validated here rather than by argparse `choices=`: the
    # frozen refusal names the six recognized verbs in `relate`'s own voice.
    if inverse_verb(args.verb) is None:
        print(
            f"docs: relate: unknown verb {args.verb!r}; "
            f"expected one of: {', '.join(sorted(RECIPROCAL_VERBS))}",
            file=sys.stderr,
        )
        return 2

    root_resolved = root.resolve()
    source_rel = _resolve_relate_endpoint(args.source, root, root_resolved)
    if isinstance(source_rel, int):
        return source_rel
    target_rel = _resolve_relate_endpoint(args.target, root, root_resolved)
    if isinstance(target_rel, int):
        return target_rel

    if source_rel == target_rel:
        print("docs: relate: SOURCE and TARGET must be different documents", file=sys.stderr)
        return 2

    reason: str | None = args.reason
    if reason is not None:
        # Shape is only checked when the flag is present, so an archived
        # pair invoked with `--reason ""` gets the empty-reason message
        # rather than the archive-rule one.
        if "\n" in reason:
            print("docs: relate: --reason must be a single line", file=sys.stderr)
            return 2
        if not reason.strip():
            print("docs: relate: --reason must not be empty", file=sys.stderr)
            return 2
    else:
        # OQ-C: required whenever EITHER endpoint is archived, checked
        # before planning — so an idempotent no-op still refuses.
        for rel in (source_rel, target_rel):
            if _is_archived_rel(rel, config):
                print(
                    f"docs: relate: {rel} is under the archive subtree; --reason is required",
                    file=sys.stderr,
                )
                return 2

    if args.date:
        try:
            when = parse_date(args.date, config.date_format)
        except MetadataError as exc:
            print(f"docs: relate: --date: {exc}", file=sys.stderr)
            return 2
    else:
        when = date.today()
    date_str = when.strftime(config.date_format)

    plan = plan_relate(
        root,
        config,
        action=args.relate_command,
        source=root / source_rel,
        verb=args.verb,
        target=root / target_rel,
        reason=reason,
        date_str=date_str,
    )

    def _emit_json(*, applied: bool, index_refreshed: bool) -> None:
        if args.json:
            print(
                json.dumps(
                    relate_plan_to_json(
                        plan,
                        dry_run=args.dry_run,
                        applied=applied,
                        index_refreshed=index_refreshed,
                    ),
                    indent=2,
                )
            )

    # `--dry-run` writes nothing at all — neither endpoint, nor the INDEX.
    # An all-unchanged plan is the same story with a different cause.
    if args.dry_run or all(edit.change == "unchanged" for edit in plan.edits):
        if not args.quiet:
            _print_relate_lines(plan, dry_run=args.dry_run)
        _emit_json(applied=False, index_refreshed=False)
        return 0

    try:
        apply_relate_plan(plan)
    except CoordinatedWriteError as exc:
        # No `--json` record on a coordinated-write failure (M25 — R6): the
        # operation aborted, and after a failed rollback the `applied` bit
        # is genuinely undefined. The stderr admission is the contract.
        print(f"docs: relate: {exc}", file=sys.stderr)
        return 2

    # Announce only after the publish succeeded — never a write that was
    # then rolled back.
    if not args.quiet:
        _print_relate_lines(plan, dry_run=False)

    index_refreshed = True
    try:
        _refresh_index(root, config, predicate=compile_exclude_predicate(config, []))
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: INDEX refresh failed: {exc}", file=sys.stderr)
        index_refreshed = False

    _emit_json(applied=True, index_refreshed=index_refreshed)
    return 0 if index_refreshed else 2


def _replace_or_prepend_h1(text: str, title: str) -> str:
    """Return `text` with its leading H1 replaced by `# {title}` (or one prepended).

    Local helper for `stamp --title` (resolved Q3): the override happens
    BEFORE `insert_metadata_block` so the block-insertion machinery is left
    untouched (`migrate` depends on it). If the first non-blank line is a
    `# ` H1 it is replaced in place; otherwise a `# {title}` line + blank
    line is prepended. The file's trailing-newline state is preserved by
    operating on `splitlines(keepends=True)`.
    """
    keep = text.splitlines(keepends=True)
    for idx, line in enumerate(keep):
        if line.strip() == "":
            continue
        if line.lstrip().startswith("# "):
            ending = line[len(line.rstrip("\r\n")) :] or "\n"
            keep[idx] = f"# {title}{ending}"
            return "".join(keep)
        break
    # No leading H1 — prepend one. `insert_metadata_block` will keep it.
    prefix = f"# {title}\n\n"
    return prefix + text


def _cmd_stamp(args: argparse.Namespace) -> int:
    # M15 (B3) — write-then-stamp. Insert a convention-correct metadata block
    # onto files an agent already wrote, preserving the body. Atomic
    # multi-file batch (mirrors `_cmd_touch`): a bad/missing file aborts
    # before any write.

    # Resolve the docs root first (start from the first named file so the
    # cwd-walk anchors on the doc, not the process cwd). The strict-root
    # refusal carries the `stamp:` prefix.
    start = Path(args.files[0]) if args.files else Path.cwd()
    root_or_exit = _resolve_managed_root(args, start, verb="stamp")
    if isinstance(root_or_exit, int):
        return root_or_exit
    root = root_or_exit

    try:
        config = load_config(root)
    except tomllib.TOMLDecodeError as exc:
        print(f"docs: malformed .docs.toml: {exc}", file=sys.stderr)
        return 2

    # Resolve each named file: a relative path is taken under the root when
    # `--root` is given (matching `project set`); otherwise relative to cwd
    # (the cwd-walk case, where cwd is inside the tree). An absolute path is
    # used as-is.
    def _resolve_file(raw: str) -> Path:
        fp = Path(raw)
        if fp.is_absolute() or not args.root:
            return fp
        return root / fp

    file_paths = [_resolve_file(p) for p in args.files]

    # Existence pass: a missing file aborts the batch before any write.
    for fp in file_paths:
        if not fp.is_file():
            print(f"docs: file not found: {fp}", file=sys.stderr)
            return 1

    # Outside-root pass → exit 1 (explicit-path error).
    root_resolved = root.resolve()
    for fp in file_paths:
        try:
            fp.resolve().relative_to(root_resolved)
        except ValueError:
            print(
                f"docs: stamp: {fp} is outside the resolved docs root ({root_resolved})",
                file=sys.stderr,
            )
            return 1

    # Role: --role else default `notes`; validate against config.roles. The
    # refusal must NAME the role and must NOT be argparse's "invalid choice".
    role = args.role or "notes"
    if role not in config.roles:
        print(
            f"docs: stamp: invalid role {role!r} (not in the Role vocabulary)",
            file=sys.stderr,
        )
        return 2

    today = date.today()
    project = args.project or config.project

    # Build every stamp in memory (validate-all-first). A file that parses
    # cleanly is ALREADY STAMPED → refresh only Updated:; otherwise it is a
    # FRESH file → insert the block.
    stamps: list[tuple[Path, str, bool]] = []  # (path, new_text, already_stamped)
    for fp in file_paths:
        text = fp.read_text()
        try:
            parse(text, fp, root)
            # Clean parse → already stamped. Bump Updated: only.
            new_text = set_metadata_field(text, "Updated", today.strftime(config.date_format))
            stamps.append((fp, new_text, True))
        except (MetadataError, VocabularyError):
            # Fresh file — insert the metadata block. Title: --title overrides
            # the leading H1 (via a local helper, BEFORE insert); else the
            # file's H1 / a synthesised title from the filename.
            source = text
            if args.title:
                source = _replace_or_prepend_h1(text, args.title)
            title = args.title or _slug_to_title(fp.stem)
            new_text = insert_metadata_block(
                source,
                title=title,
                status="draft",
                role=role,
                project=project,
                updated=today,
                date_format=config.date_format,
            )
            stamps.append((fp, new_text, False))

    if args.dry_run:
        if not args.quiet:
            for fp, _new_text, _already in stamps:
                print(f"docs: would stamp {fp}", file=sys.stderr)
        return 0

    for fp, new_text, _already in stamps:
        atomic_write(fp, new_text)

    try:
        _refresh_index(root, config, predicate=compile_exclude_predicate(config, []))
    except (MetadataError, VocabularyError) as exc:
        print(f"docs: INDEX refresh failed: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        for fp, _new_text, already in stamps:
            if already:
                print(f"docs: stamp: {fp} already stamped — refreshed Updated:", file=sys.stderr)
            else:
                print(f"docs: stamped {fp}", file=sys.stderr)
    return 0


def _print_check_findings(findings: list[Finding], root: Path) -> None:
    """Print `docs check` findings as grouped human output (M19 — D1 reuse).

    One file header per group, one indented line per finding. Empty findings
    print the "no violations found" line. Shared by `_cmd_check`'s non-json
    branch and `docs touch --check`'s `_run_touch_check`.
    """
    if not findings:
        print("docs: no violations found")
        return
    current: str | None = None
    for finding in findings:
        rel = _root_relative(finding.path, root)
        if rel != current:
            if current is not None:
                print()
            print(rel)
            current = rel
        print(f"  {finding.severity}: [{finding.rule}] {finding.message}")


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
    # M19 (D2): CLI --stale > [check] stale_days > unset; `source` lets the
    # stale finding name its provenance.
    window, source = resolve_stale(args.stale, config.stale_days)
    findings = check_tree(
        root, config, window, date.today(), predicate=predicate, stale_source=source
    )

    if args.json:
        print(json.dumps([finding_to_json(f, root) for f in findings], indent=2))
    else:
        _print_check_findings(findings, root)

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
# `docs install-skill` materialises the bundled agent skill onto a host.
# ---------------------------------------------------------------------------


# The default destination when `--dest` is omitted. A default is not an
# assumption about which agent the user runs — it is a convenient common
# location; `--dest` remains the agent-agnostic source of truth (M23 D1/D2).
_DEFAULT_SKILL_DEST = "~/.claude/skills/docs/"


def _resolve_install_dest(args: argparse.Namespace) -> str:
    """Resolve the raw dest string, TTY-aware, without expanding it (M23 D2).

    - Explicit ``--dest`` wins verbatim (raw string; caller expands/resolves).
    - Omitted + interactive TTY: prompt (default offered; empty accepts it).
    - Omitted + non-TTY (an agent): NEVER block — fall back to the default.

    Returns the RAW string; ``_cmd_install_skill`` applies the single
    ``expanduser().resolve()`` so the recorded path is the resolved absolute
    dest in every case (OQ-1 / OQ-C).
    """
    if args.dest is not None:
        return str(args.dest)
    if sys.stdin.isatty():
        answer = input(f"Install destination [{_DEFAULT_SKILL_DEST}]: ").strip()
        return answer or _DEFAULT_SKILL_DEST
    return _DEFAULT_SKILL_DEST


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
    Path("references") / "quality-artifacts.md",
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
    """Materialise the bundled `docs` agent skill onto the host, then record it.

    Resolves the dest TTY-aware (`--dest` is the source of truth; omitted →
    prompt on a TTY, default on a non-TTY — never blocks). On any success
    (copy / symlink / already-identical no-op) records the resolved dest path
    to the per-user state file so M21's update notice can replay it (M23 D3).
    Refusals (exit 2) skip recording naturally — the single recording call site
    sits behind the ``code == 0`` guard.

    Exit codes:
        0 — success (copy/symlink performed, or destination already
            byte-identical so this is a no-op).
        2 — refusal: destination exists with non-identical content and
            ``--force`` was not supplied, or ``--symlink`` was requested
            from a wheel install.
    """
    dest = Path(os.path.expanduser(_resolve_install_dest(args))).resolve()
    source = _locate_bundled_skill()
    code = _materialise_skill(args, dest, source)
    if code == 0:
        update_check.write_recorded_dest(str(dest))
    return code


def _materialise_skill(args: argparse.Namespace, dest: Path, source: Path) -> int:
    """Copy / symlink the bundled skill from ``source`` to ``dest``.

    The pre-M23 materialisation body, unchanged: wheel-symlink refusal (2),
    byte-identical no-op (0), conflict refusal (2), clean-slate + symlink (0),
    clean-slate + copy (0). ``dest`` is captured pre-mutation so a symlink
    install records the dest resolved *before* the link exists.
    """
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


def _dispatch(args: argparse.Namespace) -> int:
    """Route a parsed namespace to its verb handler, returning the exit code."""
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
    if args.command == "stamp":
        return _cmd_stamp(args)
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
        if args.project_command == "set":
            return _cmd_project_set(args)
        return 2
    if args.command == "relate":
        return _cmd_relate(args)
    return 2


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns the process exit code.

    Subcommands:
        index — regenerate INDEX.md from metadata in the docs root (M1).
        new, archive, mv, touch — mutating verbs (M2).
        check, list — validation and query verbs (M3).
        migrate — adopt a non-conforming foreign directory (M4).
        install-skill — materialise the bundled agent skill (M6).
        project rename|set — project-namespace verbs (M12/M15).
        relate add|remove — reciprocal relationship repair (M25).

    Exit codes (per cli.md):
        0 — success (or warnings-only on `check`).
        1 — recoverable error (file conflict, validation warning,
            missing input).
        2 — hard error (invalid vocab, atomic-operation failure,
            validation errors).

    After the command dispatch returns, a best-effort PyPI update-check (M21)
    may emit one advisory line to STDERR; it never alters the exit code. The
    hook runs after ``parse_args`` so ``--version`` / ``-h`` (which exit inside
    parsing) never reach it.
    """
    args = _build_parser().parse_args(argv)
    code = _dispatch(args)
    update_check.maybe_notify(args, os.environ, __version__)
    return code


if __name__ == "__main__":
    sys.exit(main())
