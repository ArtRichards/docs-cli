# docs — Architecture

Status: active
Role: reference
Project: docs
Updated: 2026-05-22

Related:
- implements: charter.md
- pairs-with: convention.md
- pairs-with: cli.md
- pairs-with: test-strategy.md

## Shape

Single Python file at `bin/docs`, executable, shebanged. (Not at repo root — the `docs/` documentation directory already lives there, and POSIX filesystems don't allow a file and directory with the same name in the same parent.) Layout inside the file is logical (no separate modules) until v1.1 forces a package split.

```
bin/docs (executable; Python 3.11+, stdlib only)
├── shebang + dunder version
├── config        — TOML load, Vocab merging, archive-dir resolution
├── model         — Doc dataclass; metadata block parser + editors
├── walker        — directory traversal, filter, archive detection
├── index         — INDEX.md render with marker-block preservation
├── archive       — atomic move + status edit (M2)
├── mv            — rename + Related: rewrite across tree (M2)
├── new           — scaffolded doc creation (M2)
├── touch         — Updated: bump (M2)
├── check         — validation rules + exit-code matrix (M3)
├── list          — query view, human + --json (M3)
├── migrate       — foreign-tree import (M4)
└── cli           — argparse dispatch, exit codes, --root resolution
```

## Module responsibilities

### `model`

- `Doc` dataclass (frozen): `path`, `title`, `status`, `role`, `project`, `updated`, `related: tuple[(verb, path), ...]`, `extra: Mapping[str, str | tuple[str, ...]]`, `body`, `archived`.
- `parse(text: str, path: Path, root: Path) -> Doc` — H1 + metadata block parser, layered on `parse_metadata_block` / `_metadata_line_span`.
- `parse` is pure (no I/O). M2 writes metadata back with surgical, minimal-diff line edits (`set_metadata_field`, `rewrite_related_refs`, `scaffold_doc`) rather than a full re-serializer — see the M2 milestone Decisions.

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

**Display order within Status: active.** The top level is one section per
`Project` — the docs root's own project first, then the rest in ascending
lexicographic order. Within a project, Roles follow the canonical convention
order (charter, plan, spec, milestone, log, status, decision, guide, runbook,
reference, postmortem, idea, notes), **except `status` is pinned to the top**
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
  `bin/docs`) — charter, plan, spec, milestone, log, decision, guide,
  runbook, reference, postmortem, idea, notes. Role groups with zero
  entries are omitted. `## Archived` appears last, after every project.
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
git clone https://github.com/<you>/docs.git ~/opt/docs
ln -s $PWD/bin/docs ~/bin/docs   # or wherever your $PATH wants it
```

The script is self-contained; no `pip install` step needed for runtime use.

## Development setup

```sh
cd ~/opt/docs
python3 -m venv .venv                          # Python 3.11+; needs python3-venv on Debian/Ubuntu
.venv/bin/pip install --upgrade pip
.venv/bin/pip install pytest ruff mypy         # or: .venv/bin/pip install -e ".[dev]"
```

The `.venv/` directory is gitignored. Recreate it from scratch in a fresh clone.

## Commands (development)

```sh
.venv/bin/python -m pytest -q                  # run tests
.venv/bin/ruff check .                         # lint
.venv/bin/ruff format --check .                # format check
.venv/bin/mypy                                 # type-check (tree-wide, per pyproject)
./bin/docs index docs/                         # dogfood smoke (post-M1)
```
