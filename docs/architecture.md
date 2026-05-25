# docs — Architecture

Lifecycle: active
Role: reference
Project: docs
Updated: 2026-05-25

Related:
- implements: charter.md
- pairs-with: convention.md
- pairs-with: cli.md
- pairs-with: test-strategy.md
- pairs-with: m5-claude-code-skill.md

## Shape

Single Python module at `src/docs_cli/cli.py`, exposed as the
`docs` console-script via the `docs_cli.cli:main` entry point declared
in `pyproject.toml`. The `docs_cli/` package ships as a wheel on PyPI
(distribution name `docs-cli`); the bundled Claude Code skill rides
inside the same wheel as package data.

```
src/docs_cli/                            (Python 3.11+, stdlib only)
├── __init__.py                          ─ lazy re-export of `main`
├── cli.py                               ─ the CLI module (~2.5k lines)
│   ├── dunder version                   (__version__ = "1.2.0")
│   ├── config        — TOML load, Vocab merging, archive-dir resolution,
│   │                   `[migrate]` per-tree overrides (M7)
│   ├── model         — Doc dataclass; metadata block parser + editors
│   ├── walker        — directory traversal, filter, archive detection
│   ├── index         — INDEX.md render with marker-block preservation
│   ├── archive       — atomic move + lifecycle edit (M2; M7 rename)
│   ├── mv            — rename + Related: rewrite across tree (M2)
│   ├── new           — scaffolded doc creation (M2)
│   ├── touch         — Updated: bump (M2)
│   ├── check         — validation rules + exit-code matrix (M3)
│   ├── list          — query view, human + --json (M3)
│   ├── migrate       — foreign-tree inference + plan/apply (M4)
│   ├── install-skill — materialise the bundled skill onto a host (M6)
│   └── cli           — argparse dispatch, exit codes, --root resolution
└── skill/                               ─ bundled Claude Code skill (M5)
    ├── SKILL.md                          (frontmatter + trigger surface)
    └── references/
        ├── convention.md                 (byte-identical mirror)
        └── cli.md                        (byte-identical mirror)
```

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
- `parse` is pure (no I/O). M2 writes metadata back with surgical, minimal-diff line edits (`set_metadata_field`, `rewrite_related_refs`, `scaffold_doc`) rather than a full re-serializer — see the M2 milestone Decisions.

### `config`

- `Config` dataclass (frozen): `project`, `archive_dir`, `date_format`,
  `lifecycles: frozenset[str]` (M7-renamed from `statuses`), `roles:
  frozenset[str]`, `index_filename`, plus M7's two `[migrate]` per-tree
  overrides: `role_suffixes: dict[str, str]` (custom filename-suffix →
  role mapping) and `project_name: str | None` (per-tree project override,
  equivalent to the `--config-project NAME` CLI flag).
- `load_config(root) -> Config` reads `.docs.toml` (or returns defaults
  when absent). M7: the `[vocabulary] add_statuses` TOML key was renamed
  `add_lifecycles` without a backward-compat alias; the new `[migrate]`
  section is optional.
- `validate_lifecycle` / `validate_role` are the two vocab-checks (M7:
  `validate_status` was renamed `validate_lifecycle`).

### `walker`

- `walk(root: Path, config: Config) -> Iterator[Doc]` — yields parsed Docs.
- Skips non-`.md`, hidden files, anything matching ignore patterns in `.docs.toml` (future).
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
    Confidence is `True`/`"medium"`/`False`.
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
  `atomic_write` per file, plus the archive moves.
  `migration_to_json(plan)` serialises the whole plan to the `--json`
  schema pinned in [cli.md](cli.md).
- **Models** — `FileMigration` (frozen) carries one per-file decision: the
  inferred `role`/`project`/`lifecycle` (M7-renamed)/`updated`,
  `confidence` (`"high"|"medium"|"low"` — M7 widens to three values per
  OQ-D; `medium` requires empty `ambiguities`), `ambiguities`,
  `synthesized_h1`, `reconciled_metadata`, and an optional
  `archive_move` destination. `MigrationPlan` (frozen) holds the `root`,
  the tuple of `FileMigration`s in root-relative path order,
  `project_original: str | None` (M7 — the pre-normalisation project
  name when F11 changed the value, else `None`), and
  `multi_project_hints: tuple[str, ...]` (M7 — F5 advisory hints, empty
  when none apply or when the CLI override is in force).
- **Scope boundary** — the active-tree directory layout is left untouched;
  `--apply` adds metadata in place and only ever moves docs out of detected
  archive-style subdirs. No role-bucket flattening or project re-foldering.

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
