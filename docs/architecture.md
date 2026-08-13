# docs — Architecture

Lifecycle: active
Role: reference
Project: docs
Updated: 2026-08-13

Related:
- implements: charter.md
- pairs-with: convention.md
- pairs-with: cli.md
- pairs-with: test-strategy.md
- pairs-with: archive/2026-05-23/m5-claude-code-skill.md

## Shape

Single Python module at `src/docs_cli/cli.py`, exposed as the
`docs` console-script via the `docs_cli.cli:main` entry point declared
in `pyproject.toml`. The `docs_cli/` package ships as a wheel on PyPI
(distribution name `docs-cli`); the bundled Claude Code skill rides
inside the same wheel as package data.

```
src/docs_cli/                            (Python 3.11+, stdlib only)
├── __init__.py                          ─ lazy re-export of `main`
├── cli.py                               ─ the CLI module (~7.0k lines)
│   ├── dunder version                   (__version__ = importlib.metadata.version("docs-cli"))
│   ├── config        — TOML load, Vocab merging, archive-dir resolution,
│   │                   `[migrate]` per-tree overrides (M7),
│   │                   `[exclude]` + `.docsignore` (M8)
│   ├── model         — Doc dataclass; metadata block parser + editors
│   ├── walker        — directory traversal, filter, archive detection
│   ├── index         — INDEX.md render with marker-block preservation
│   ├── archive       — atomic move + lifecycle edit (M2; M7 rename;
│   │                   M12 referring-edge rewrite; M26 plan/pre-flight/
│   │                   apply + `--json` operation record)
│   ├── mv            — rename + Related: rewrite across tree (M2)
│   ├── new           — scaffolded doc creation (M2)
│   ├── touch         — Updated: bump (M2; M12 outside-root refusal)
│   ├── check         — validation rules + exit-code matrix (M3)
│   ├── list          — query view, human + --json (M3)
│   ├── migrate       — foreign-tree inference + plan/apply (M4)
│   ├── project       — rename verb (M12)
│   ├── install-skill — materialise the bundled skill onto a host (M6)
│   └── cli           — argparse dispatch, exit codes, --root resolution
└── skill/                               ─ bundled Claude Code skill (M5)
    ├── SKILL.md                          (frontmatter + trigger surface)
    └── references/
        ├── convention.md                 (byte-identical mirror)
        ├── cli.md                        (byte-identical mirror)
        ├── use-cases.md                  (M5; bundle-only, no `docs/` mirror)
        ├── adoption-playbook.md          (M8 F8; bundle-only, no mirror)
        └── docs-toml-template.toml       (M8 F8; bundle-only starter)
```

> Pinned by `tests/test_packaging.py` A3 to the bumping-target literal;
> runtime read goes through stdlib `importlib.metadata` so a single
> `pyproject.toml` version bump propagates to `docs --version`
> automatically (M12). Fallback to `0.0.0+local` (M12 — OQ-4) if
> `importlib.metadata.PackageNotFoundError` is raised — protects
> fresh-clone runs without `pip install -e .`.

**Sibling artifact: the Claude Code skill.** The Claude Code skill at
`src/docs_cli/skill/` (M5) is **not** a `cli.py` module and adds no
Python — it is a standalone Markdown artifact that *drives* the verbs
above: its `description` triggers an agent doing documentation work in
a `docs`-managed tree, and its body redirects to the right `docs` verb.
Alongside `SKILL.md` sit two bundled reference files at
`src/docs_cli/skill/references/` — byte-identical mirrors of
`docs/convention.md` and `docs/cli.md` — so an agent reading the skill
on any installed host has the spec on hand without needing the docs
repo checked out. Lockstep between the source specs and the bundle is
enforced by `tests/test_skill_refs.py`. The skill is authored and
version-controlled here, **ships as package data inside the
`docs-cli` wheel**, and is materialised onto a host via
`docs install-skill` (M6).

## Module responsibilities

### `model`

- `Doc` dataclass (frozen): `path`, `title`, `lifecycle` (M7-renamed from `status`), `role`, `project`, `updated`, `related: tuple[(verb, path), ...]`, `extra: Mapping[str, str | tuple[str, ...]]`, `body`, `archived`.
- `parse(text: str, path: Path, root: Path) -> Doc` — H1 + metadata block parser, layered on `parse_metadata_block` / `_metadata_line_span`.
- `parse` is pure (no I/O). M2 writes metadata back with surgical, minimal-diff line edits (`set_metadata_field`, `rewrite_related_refs`, `scaffold_doc`) rather than a full re-serializer — see the M2 milestone Decisions. M25 adds three more editors on the same contract: `add_related_edge` / `remove_related_edge` (one typed `Related:` bullet each way, creating the group when absent and dropping it when it empties, matching targets canonically) and `append_revision_entry` (one bullet into the repeatable `Revision:` audit group at the end of the metadata block). All three share `_bare_label_run` for group location — one label-parameterised scan serving both the `Related:` and `Revision:` groups — and `_metadata_line_span` for block boundaries, so no editor has its own notion of where the block or a group is.

### `config`

- `Config` dataclass (frozen): `project`, `archive_dir`, `date_format`,
  `lifecycles: frozenset[str]` (M7-renamed from `statuses`), `roles:
  frozenset[str]`, `index_filename`, plus M7's two `[migrate]` per-tree
  overrides: `role_suffixes: dict[str, str]` (custom filename-suffix →
  role mapping) and `project_name: str | None` (per-tree project override,
  equivalent to the `--config-project NAME` CLI flag), plus M8's four
  exclude fields: `exclude_dirs: tuple[str, ...]`, `exclude_globs:
  tuple[str, ...]`, `exclude_exts: tuple[str, ...]` from the `[exclude]`
  table, and `docsignore_patterns: tuple[str, ...]` carrying the raw
  line contents of a root-level `.docsignore` file.
- `load_config(root) -> Config` reads `.docs.toml` (or returns defaults
  when absent). M7: the `[vocabulary] add_statuses` TOML key was renamed
  `add_lifecycles` without a backward-compat alias; the new `[migrate]`
  section is optional. M8: also reads the optional `[exclude]` table
  and a root-level `.docsignore` file (raw line contents — compilation
  to regex is deferred to `compile_exclude_predicate`).
- `validate_lifecycle` / `validate_role` are the two vocab-checks (M7:
  `validate_status` was renamed `validate_lifecycle`).
- `compile_exclude_predicate(config, cli_excludes=(), cli_exts=()) ->
  Callable[[str], bool]` (M8 F3) returns a single layered predicate
  the walker consults. Combines `[exclude]` config, the root
  `.docsignore` file, and CLI overrides additively. Stdlib-only
  (`re`; uses an internal `_compile_docsignore_pattern` helper).

### `walker`

- `walk(root: Path, config: Config, predicate=None) -> Iterator[Doc]`
  — yields parsed Docs. M8 (F3) adds the optional `predicate`
  keyword for layered exclusion (see `config.compile_exclude_predicate`).
- Skips non-`.md`, hidden files, the root-level `INDEX.md`, and
  (when `predicate` is set) any path the predicate flags. The
  sibling `_iter_doc_texts` (lenient counterpart used by `check`,
  `list`, `migrate`) carries the same `predicate` keyword.
- Distinguishes active tree from archive subtree (via configured `archive_dir`).

### `index`

- `render_index(docs: list[Doc], config: Config, existing: str | None, root: Path) -> str`.
- If `existing` contains the marker block, preserves everything outside the markers.
- If `existing` is None or has no markers, creates a minimal file with markers.
- Active docs are grouped by `Project`, then by `Role` within each project;
  archived docs share one section.
- Deterministic: same inputs produce byte-identical output.

**Display order within Lifecycle: active.** The top level is one section per
`Project` — the docs root's own project first, then the rest in ascending
lexicographic order. Within a project, Roles follow the canonical convention
order (charter, plan, spec, milestone, log, status, decision, guide, runbook,
reference, postmortem, idea, implementation, sketch, outline, memo, brief,
template, example, notes — M7 adds the 7 core roles between `idea` and
`notes`), **except `status` is pinned to the top**
— it's the "you are here" pin and the entry point for most navigation. Within
each Role section, entries are sorted by `Updated:` descending, then by path
ascending as a deterministic tiebreaker.

**INDEX.md is excluded from walking** by name. The file is read once for
marker-block preservation, then ignored as a traversal target. The exclusion
is **root-level only** — a nested file named `INDEX.md` deeper in the tree
IS a walkable doc and is treated like any other Markdown file.

### INDEX renderer format

The renderer's output between the markers has a fixed shape so that
`docs index` is byte-deterministic and reviewable in diffs:

- **Summary line.** First line inside the marker block:
  ```
  _Generated YYYY-MM-DD. N docs active, M archived._
  ```
- **Section headings.** Active docs are grouped two levels deep — a
  level-2 heading per `Project`, then a level-3 heading per Role group:
  ```
  ## Project — <name>

  ### Active — <Role-titlecased>
  ```
  A doc with no `Project:` line is bucketed under the docs root's
  configured default project. Archived docs share one level-2 heading,
  `## Archived` — flat, not project-grouped.
- **Project group order.** The docs root's own project (the configured
  `project`) comes first; the remaining projects follow in ascending
  lexicographic order. Projects with zero active docs are omitted.
- **Role group order.** Within each project, `status` is pinned to the
  top. The remaining Roles follow `CANONICAL_ROLE_ORDER` (defined in
  `src/docs_cli/cli.py`) — charter, plan, spec, milestone, log,
  decision, guide, runbook, reference, postmortem, idea,
  implementation, sketch, outline, memo, brief, template, example,
  notes (M7 — F10 adds the 7 core roles between `idea` and `notes`).
  Role groups with zero entries are omitted. `## Archived` appears last,
  after every project.
- **Within-section sort.** Primary key: `Updated:` descending. Tiebreaker:
  path ascending (lexicographic on the root-relative path).
- **Entry format.** One bullet per doc:
  ```
  - [<path>](<path>) — _role_ — <description>. Updated YYYY-MM-DD.
  ```
  Both the link text and the href are the doc's **root-relative POSIX
  path** (e.g. `topics/deep-dive.md` for a doc in a subdirectory) — not the
  bare basename, which would break links for any doc outside the root.
  Description source: the first non-empty paragraph of the doc body
  (after the metadata block), with internal newlines collapsed to spaces
  and trimmed to ~120 characters (cut at the last whitespace before the
  limit; suffix with `…` if truncated).
- **Markers verbatim.** `<!-- docs:generated start -->` and
  `<!-- docs:generated end -->` — exact strings, including the spacing.
  The renderer matches them as literal substrings; no regex with variant
  whitespace.

Preservation rule: everything outside the markers (preamble before
`<!-- docs:generated start -->` and trailer after `<!-- docs:generated end -->`)
is copied verbatim into the regenerated file. If the existing INDEX
contains no markers, the renderer creates a minimal file containing only
the marker block and the derived content.

### `migrate`

- `migrate` adopts a *non-conforming* foreign directory into the convention.
  It is read-only by default (a dry-run plan); `--apply` performs the edits.
- **Inference helpers** — pure functions, no I/O:
  - `infer_role(filename, metadata, config=None) -> (role, confidence)` —
    multi-pass: in-file `Role:` (high) → filename-suffix match (high) →
    `_M\d+` milestone pattern (medium) → non-role-suffix strip
    (`_v\d+`/`_Draft`/`_Ready`) + re-match (medium) → `notes` fallback
    (low). Word-boundary tolerance: tokeniser splits on `-`/`_`/whitespace
    AND case-transition (`MyPlan` → suffix `plan`). Optional `config`
    extends the built-in suffix map with `config.role_suffixes`.
    Confidence is a `Confidence(enum.Enum)` member (`HIGH | MEDIUM |
    LOW`) — M10 replaces the legacy `True | "medium" | False` tri-value.
    The enum's `value` strings (`"high"`/`"medium"`/`"low"`) match the
    M4 JSON wire format byte-for-byte; `migration_to_json` crosses
    enum→string via `fm.confidence.value` at the boundary.
  - `infer_project(filenames, dir_name) -> str` — the longest common
    `-`/`_`-delimited filename prefix, or the directory name.
  - `normalise_project_name(name) -> str` (M7 — F11) — splits on case
    boundaries (`FooBar`), letter↔digit (`Abc5Mig`), underscores;
    lowercases; trims; collapses repeats. Preserves digit-after-digit so
    `2026-01-26` survives intact.
  - `infer_lifecycle(metadata, in_archive) -> (lifecycle, confident)` —
    in-file `Lifecycle:` line, else `archived` (in an archive subdir)
    or `active`. (Renamed from `infer_status` at M7 Phase 10 simplify.)
  - `infer_updated(metadata, mtime, date_format) -> (updated, confident)` —
    in-file `Updated:` line, else the file mtime.
  - `detect_archive_layout(rel_path, archive_date) -> str | None` — maps a
    non-conformant archive-style path (`archived/`, `project-history/`, a
    bare `archive/file.md`) to `archive/<date>/<basename>`; returns `None`
    for an active-tree file or one already at `archive/<valid-date>/`.
  - `_infer_role_from_h1(text) -> str | None` (M7 — F1) — H1 trailing-word
    match; longest match wins; word-boundary required.
  - `_infer_role_from_sections(text) -> str | None` (M7 — F1) — top-level
    `## ` heading pattern match (plan / status / decision / log shapes).
  - `_sibling_default(rel, sibling_roles) -> str | None` (M7 — F1 / OQ-C)
    — modal sibling role at ≥ 60% over ≥ 5 same-subdir suffix-confident
    files.
  - `_multi_project_hints(root, parent_project, threshold=5) -> tuple[str, ...]`
    (M7 — F5) — emits one `"hint: …"` line per immediate subdir whose
    `.md` common-filename-prefix differs from `parent_project` and
    covers ≥ `threshold` files. Candidate name is the file-prefix
    (per OQ6).
- **Block-insertion** — `insert_metadata_block(text, *, title, status, role,
  project, updated, date_format)` places (or synthesises) the H1, inserts the
  required metadata block (M7 — writes `Lifecycle:`), preserves the body
  verbatim, and reconciles any pre-existing metadata-shaped lines into the
  block instead of duplicating them; non-required pre-existing lines (a
  free-form `Status:`, `Owner:`, `Tags:`, `Related:`, etc.) are preserved
  into a `## Migrated metadata` body section with each label `Migrated-`
  prefixed. Distinct from `set_metadata_field` (edits an existing
  block) and `scaffold_doc` (builds from nothing) — see the M4 Decisions.
  The function-signature parameter is still named `status` for back-
  compat (Phase 10 simplify candidate).
- **Plan / apply** — `plan_migration(root, archive_date=None, *,
  cli_config_project=None) -> MigrationPlan` walks the tree (via
  `_iter_doc_texts` with a default `Config`), runs the inference helpers,
  and assembles one `FileMigration` per `.md` file with a confidence and
  every ambiguity flagged. M7 (F11) consults the precedence chain
  CLI `--config-project` > `.docs.toml [migrate] project_name` >
  F11-normalised(inferred); the pre-normalisation name flows onto
  `MigrationPlan.project_original` when normalisation changed it. M7 (F4)
  uses each file's `Updated:`/mtime as the archive-move date when
  `archive_date` is `None`. A medium-confidence upgrade pass over
  `notes`-fallback files runs H1 → section → sibling-set in order. M7
  (F5) emits `MigrationPlan.multi_project_hints` via
  `_multi_project_hints` unless `cli_config_project` is set.
  `apply_migration(plan)` executes it: `insert_metadata_block` +
  `atomic_write` per file, plus the archive moves. After each
  archive-move it calls `_opportunistic_rmdir(old_parent, plan.root)`
  to clear the now-empty source dir (M10 — OQ-G; swallows OSError on
  a non-empty parent so non-migrating siblings survive). After the
  file loop it calls `_ensure_docs_toml(plan)` which writes (or
  extends) the root `.docs.toml` sidecar so the adopted tree is
  immediately self-describing — absent sidecar gets a minimal
  `[project] name = "<resolved>"` + `[archive] date_format` block;
  existing sidecar without `[project]` gets the new block appended
  under a `# Added by docs migrate --apply` provenance comment;
  existing `[project]` is never overwritten (M10 — OQ-A).
  `migration_to_json(plan)` serialises the whole plan to the `--json`
  schema pinned in [cli.md](cli.md).
- **Models** — `FileMigration` (frozen) carries one per-file decision: the
  inferred `role`/`project`/`lifecycle` (M7-renamed)/`updated`,
  `confidence: Confidence` (a `Confidence` enum member — M10 replaces
  the M7 tri-string with the enum; `Confidence.MEDIUM` requires empty
  `ambiguities`), `ambiguities`, `synthesized_h1`,
  `reconciled_metadata`, and an optional `archive_move` destination.
  `MigrationPlan` (frozen) holds the `root`, the tuple of
  `FileMigration`s in root-relative path order, `project_original:
  str | None` (M7 — the pre-normalisation project name when F11
  changed the value, else `None`), and `multi_project_hints:
  tuple[str, ...]` (M7 — F5 advisory hints, empty when none apply or
  when the CLI override is in force). M10 — OQ-D — drops the unused
  `excluded_count: int` field (set in `plan_migration` but read
  nowhere in shipped code); consumers that need the total compute it
  from `excluded_breakdown`.
- **Config** — `Config` (frozen) carries the resolved configuration
  for a docs root. M10 — OQ-H — adds `fields: frozenset[str]` (sourced
  from `[vocabulary] add_fields`, case-sensitive exact match;
  defaults to the empty set) which widens the `unknown-field` check's
  allowlist on top of the built-in always-allowed metadata labels
  (`_BUILTIN_METADATA_FIELDS`). The rule is opt-in: an empty
  `Config.fields` switches the warning OFF entirely.
- **Scope boundary** — the active-tree directory layout is left untouched;
  `--apply` adds metadata in place and only ever moves docs out of detected
  archive-style subdirs. No role-bucket flattening or project re-foldering.

### `check`

- `check_doc(path, text, root, config, stale, today, stale_source) -> list[Finding]`
  — every **single-document** rule (`missing-field`, `bad-vocab`,
  `bad-date`, `status-drift`, `broken-ref`, `stale`, `malformed`,
  `unknown-field`, `duplicate-field`). Never raises: a validator must
  describe malformed input, not blow up on it.
- M25 (D7) adds `duplicate-field` via `_duplicate_labels(text)`, which
  counts the metadata block's **raw label lines** rather than reading
  `parse_metadata_block`'s output. It has to: that function assigns
  `metadata[label] = tuple(values)`, so a repeated label has already
  overwritten the earlier one — and discarded its values — by the time the
  parsed mapping exists. This is the one rule whose evidence is destroyed
  by parsing.
- `check_tree(...)` materialises the `_iter_doc_texts` walk **once**, so
  the one rule that needs more than one document can see the whole set.
- M25 adds that rule: `reciprocity_findings(entries, root) ->
  dict[Path, list[Finding]]` is a **cross-document pass** that indexes
  every parseable walked doc by root-relative path and then requires each
  recognized reciprocal edge (`inverse_verb(verb) is not None`) to have its
  exact inverse pointing back. Its results are keyed by source path and
  interleaved into `check_tree`'s existing per-doc grouping — `check_doc`'s
  findings first, then any `missing-inverse` — rather than appended as a
  tail block. A target that is excluded, unresolvable, non-Markdown, or
  malformed is simply absent from the index, so those four applicability
  conditions collapse into a single lookup and the owning rules keep their
  cases.

### `relate` (M25)

- `plan_relate(...) -> RelatePlan` reads both endpoints and stages both
  complete texts in memory; `apply_relate_plan(plan)` publishes them.
  The `plan_migration` / `apply_migration` split, applied to a two-file
  edit.
- `apply_relate_plan` implements the D5 contract: re-validate the staged
  texts, `os.access` writability pre-flight on each changed **file**, then
  publish source-then-target through the module-global `atomic_write`,
  rolling every already-published endpoint back through the same
  `atomic_write` on a later failure. Best-effort staged publish + rollback,
  not a filesystem transaction — two files cannot be renamed atomically as
  a unit on POSIX, and the spec says so rather than implying otherwise.

### `archive` (M26)

The same plan/apply split as `relate`, one stage longer and with a
deliberately different failure boundary:

```
archive_candidates(doc, root, config, scope)   pure — one-hop pairs-with /
        │                                      child-of edges, deduplicated on
        ▼                                      the canonical rel, scope matched
plan_archive(...) -> ArchivePlan               pure — destinations for the
        │                                      SELECTED members only
        ▼
preflight_archive_plan(plan)                   proves all five per-member
        │                                      properties; raises before any write
        ▼
apply_archive_plan(plan) -> [(old, new), ...]  drives `_archive_one` in
        │                                      plan.moves order, primary first
        ▼
_rewrite_referring_edges(root, config, moves)  M12 + M18, one batch
        │
        ▼
_refresh_index(root, config)                   exactly once, at the end
```

- **Validate-all-first with a residual admission**, in contrast to M25's
  staged publish plus rollback. Every failure the tool can foresee is a
  pre-flight refusal with **zero** bytes written — the primary included.
  There is no rollback: an unexpected `OSError` mid-execution produces an
  exact partial-state admission naming what moved and what did not.
  Extending D5's rollback from two documents to N was considered and
  explicitly declined (M26 — D4), because each undo must reverse both a move
  and a metadata edit and the referring-edge rewrite runs afterwards.
- The two exceptions share one carrier. `CoordinatedWriteError` now spans
  both verbs; `exit_code` on the exception carries M26's exit-1/exit-2 split
  so `preflight_archive_plan` can stay `-> None`.
- `_archive_one` is unchanged since M2 — `apply_archive_plan` is only its
  ordered driver. The per-member work, and its edit-then-move atomicity,
  live where they always did.
- **Authorization is a CLI-layer concept, discovery is not.**
  `archive_candidates` reports the whole neighborhood with each member's
  state; `_cmd_archive` decides what that means for the exit code. That is
  why `--json` can carry the full candidate set in every mode while the
  stderr prose stays quiet under a plain `docs archive FILE`.

### `cli`

- `argparse` subparsers per verb.
- Resolves docs root by walking up from cwd, looking for `.docs.toml`; falls back to cwd.
- Exit codes per [cli.md](cli.md).
- Top-level `main()` is what the shebang executes.

## Data flow (M1 happy path: `docs index`)

```
cwd ──► find_root() ──► load_config(.docs.toml) ──┐
                                                  ▼
                                          walk(root, config)
                                                  │
                                                  ▼
                                          [Doc, Doc, ...]
                                                  │
                                                  ▼
                  read INDEX.md (if exists) ──► render(docs, config, existing)
                                                  │
                                                  ▼
                                          write INDEX.md atomically
```

## Atomic write pattern

Used everywhere the tool mutates a file:

```python
tmp = path.with_suffix(path.suffix + ".docs-tmp")
tmp.write_text(new_content)
tmp.replace(path)   # POSIX-atomic on same filesystem
```

For archive operations (M2): edit in-place first (atomic write), then move with `Path.replace` (atomic within the docs root's filesystem). The move happens after the edit, so a failure during the edit leaves the original untouched.

## What's deliberately not architected

- No plugin system. Verbs are functions; adding one is editing this file.
- No abstract base classes. Dataclasses + free functions only.
- No async. Single-threaded; the largest expected tree is in low thousands of files.
- No caching layer. Re-parse on every command; profiling will tell us if this matters.
- No logging framework. `print(..., file=sys.stderr)` is sufficient.

## Dependencies

- Python 3.11+ (for `tomllib` in stdlib).
- No third-party runtime dependencies.
- Test-time: `pytest`. Development: `ruff` and `mypy`. All declared under `[project.optional-dependencies] dev` in `pyproject.toml`.

## Install (end users)

```sh
pip install docs-cli                           # lands `docs` on PATH
docs install-skill                             # materialise the bundled skill at ~/.claude/skills/docs/
```

`docs-cli` is published on PyPI; the wheel carries the bundled Claude
Code skill inside as package data, so a single `pip install` plus the
one-shot `docs install-skill` is enough to use the CLI and to make the
skill discoverable by Claude Code. No git clone required for runtime
use. The committed skill artifact is host-agnostic; the host-specific
path lives only in the `install-skill` invocation.

`install-skill --dest <DIR>` overrides the default destination; `--force`
overwrites a non-identical existing directory; `--symlink` is supported
only for editable installs. The release runbook at
[release-runbook.md](release-runbook.md) covers the publishing side.

## Development setup

```sh
git clone https://github.com/ArtRichards/docs-cli.git ~/opt/docs-cli
cd ~/opt/docs-cli
python3 -m venv .venv                          # Python 3.11+; needs python3-venv on Debian/Ubuntu
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"              # editable install + pytest/ruff/mypy/build
```

The editable install lands `.venv/bin/docs` on PATH pointing at the
in-tree `src/docs_cli/cli.py`. `.venv/` is gitignored; recreate it
from scratch in a fresh clone.

## Commands (development)

```sh
.venv/bin/python -m pytest -q                  # run tests
.venv/bin/ruff check .                         # lint
.venv/bin/ruff format --check .                # format check
.venv/bin/mypy                                 # type-check (tree-wide, per pyproject)
.venv/bin/docs check docs/                     # dogfood smoke
.venv/bin/docs index --root docs/ --dry-run    # smoke: idempotent dogfood
.venv/bin/python -m build                      # produces dist/docs_cli-<v>-*.whl + .tar.gz
```
