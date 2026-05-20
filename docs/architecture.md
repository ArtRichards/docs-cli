# docs — Architecture

Status: active
Role: reference
Project: docs
Updated: 2026-05-20

Related:
- implements: charter.md
- pairs-with: convention.md
- pairs-with: cli.md
- pairs-with: test-strategy.md

## Shape

Single Python file at the repo root, executable, shebanged. Layout inside the file is logical (no separate modules) until v1.1 forces a package split.

```
docs (executable; Python 3.11+, stdlib only)
├── shebang + dunder version
├── config        — TOML load, Vocab merging, archive-dir resolution
├── model         — Doc dataclass; metadata block parser; serializer
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

- `Doc` dataclass: `path`, `title`, `status`, `role`, `project`, `updated`, `related: list[(verb, path)]`, `extra: dict[str, str|list[str]]`, `body_offset` (where content starts).
- `parse(text: str, path: Path) -> Doc` — H1 + metadata block parser.
- Pure: no I/O, no global state. Round-trippable in principle (read → write back produces equivalent metadata block).

### `walker`

- `walk(root: Path, config: Config) -> Iterator[Doc]` — yields parsed Docs.
- Skips non-`.md`, hidden files, anything matching ignore patterns in `.docs.toml` (future).
- Distinguishes active tree from archive subtree (via configured `archive_dir`).

### `index`

- `render(docs: list[Doc], config: Config, existing: str | None) -> str`.
- If `existing` contains marker block, preserves everything outside the markers.
- If `existing` is None or has no markers, creates a minimal file with markers.
- Groups by `Status` then `Role`. Archived docs in their own section.
- Deterministic: same inputs produce byte-identical output.

**Display order within Status: active.** Roles are listed in the canonical
convention order (charter, plan, spec, milestone, log, status, decision,
guide, runbook, reference, postmortem, idea, notes), **except `status` is
pinned to the top** — it's the "you are here" pin and the entry point for
most navigation. Within each Role section, entries are sorted by `Updated:`
descending, then by path ascending as a deterministic tiebreaker.

**INDEX.md is excluded from walking** by name. The file is read once for
marker-block preservation, then ignored as a traversal target.

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

For archive operations (M2): edit in-place first (atomic write), then move (`Path.rename` or `shutil.move` if cross-FS). The move happens last so failure mid-edit leaves the original untouched.

## What's deliberately not architected

- No plugin system. Verbs are functions; adding one is editing this file.
- No abstract base classes. Dataclasses + free functions only.
- No async. Single-threaded; the largest expected tree is in low thousands of files.
- No caching layer. Re-parse on every command; profiling will tell us if this matters.
- No logging framework. `print(..., file=sys.stderr)` is sufficient.

## Dependencies

- Python 3.11+ (for `tomllib` in stdlib).
- No third-party runtime dependencies.
- Test-time: `pytest`. Development: `ruff`, optionally `mypy`. Specified in `pyproject.toml` (created in M1 Phase 5).

## Commands (development)

```
ruff check .
ruff format .
mypy docs        # if mypy installed
pytest -q
./docs index docs/   # smoke test against own docs root
```

## Install

```
ln -s $PWD/docs ~/bin/docs
```

The script is self-contained; no `pip install` step needed.
