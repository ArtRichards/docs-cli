# M1 — Implementation Log

Status: active
Role: log
Project: docs
Updated: 2026-05-20

Related:
- child-of: m1-parser-and-index.md
- pairs-with: status.md

## Implementation metadata

- Project: docs
- Milestone: M1 — Parser and `docs index`
- Started: 2026-05-20
- Progress: Phase 1 (Define Contract) — not yet started; foundations complete

(Note: doc-lifecycle status is in the front-matter `Status:` field above. This
section tracks milestone progress, which is distinct.)

## Summary

Implement the parser, walker, and `docs index` subcommand. Foundational milestone: every later verb depends on the parser + walker. No mutating verbs in this milestone.

## TDD Phase Progress

| Phase | Status | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-05-20 | Skeleton + test infra; corrected file location to `bin/docs`. |
| 2. Write Tests (RED) | Pending | — | — |
| 3. Create Data/Fixtures | Pending | — | — |
| 4. Run Tests (RED Baseline) | Pending | — | — |
| 5. Update Base Interfaces | Pending | — | — |
| 6. Implement Offline/Core Path | Pending | — | — |
| 7. Update Tool/Wrapper Layer | Pending | — | — |
| 8. Run Tests (GREEN) | Pending | — | — |
| 9. Dogfood pass | Pending | — | — |
| 10. Quality, Docs, Refactor | Pending | — | — |

## Current State Analysis

- **Codebase:** No source code. `tests/` contains only `.gitkeep`.
- **Docs:** Eleven Markdown files in `docs/` plus this log. All hand-authored.
- **Build/test infra:** None. `pyproject.toml` does not yet exist.
- **Install path:** Intended `~/bin/docs` symlink to `~/opt/docs/docs`; symlink not yet created.

## Files to Create / Modify

| File | Action | Phase | Notes |
|---|---|---|---|
| `docs` (executable) | Create | 1, 5, 6, 7 | Single-file Python script |
| `pyproject.toml` | Create | 5 | Project metadata + dev deps (pytest, ruff, mypy) |
| `tests/test_model.py` | Create | 2 | Parser unit tests |
| `tests/test_walker.py` | Create | 2 | Walker unit tests |
| `tests/test_index.py` | Create | 2 | Index render unit tests |
| `tests/test_cli_index.py` | Create | 2 | End-to-end CLI tests via subprocess |
| `tests/fixtures/parser/*.md` | Create | 3 | Single-doc parser fixtures |
| `tests/fixtures/trees/minimal/` | Create | 3 | Smallest valid tree |
| `tests/fixtures/trees/with-archive/` | Create | 3 | Active + archive subtree |
| `tests/fixtures/trees/marker-preservation/` | Create | 3 | INDEX with hand-edited regions |
| `docs/status.md` | Modify | 10 | M1 → Complete, M2 → ACTIVE |
| `docs/plan.md` | Modify | 10 | If M1 work surfaces plan changes |
| `docs/INDEX.md` | Regenerate | 9, 10 | Via `./docs index docs/` |

## Phase logs

### Phase 1 — Define Contract

**Completed:** 2026-05-20

#### Objective
Lock in the public API surface of the `docs` executable: dataclasses, exception classes, function signatures. No business logic. Make the test infrastructure (`pyproject.toml`, `tests/conftest.py`) ready so Phase 2 can write failing tests.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `bin/docs` | Create | Skeleton with constants, exceptions, `Doc`/`Config` dataclasses, function signatures (`NotImplementedError` bodies); shebanged + executable. |
| `pyproject.toml` | Create | Project metadata, dev deps (`pytest`, `ruff`, `mypy`), tool configs. `[tool.ruff] extend-include = ["bin/docs"]` and `[tool.mypy] scripts_are_modules = true` handle the no-extension executable. |
| `tests/conftest.py` | Create | Loads `bin/docs` via `importlib.machinery.SourceFileLoader`, registers in `sys.modules['docs']` so tests can `from docs import …`. Provides `docs_script` and `fixtures_dir` session fixtures. |
| `docs/architecture.md` | Modify | (1) File-location correction: executable lives at `bin/docs`, not at repo root, because of POSIX file-vs-dir name collision with `docs/`. (2) Added "INDEX renderer format" subspec codifying summary-line, section-headings, role group order (`status` pinned), within-section sort, entry format, and marker handling. (3) Noted INDEX exclusion is root-level only. |
| `README.md` | Modify | Install path: `~/opt/docs/bin/docs`, not `~/opt/docs/docs.py`. |
| `.venv/` (local only, gitignored) | Create | Python venv with pytest/ruff/mypy installed. |

#### Actions taken

- Created `bin/` subdir and the `docs` executable (skeleton).
- Verified the skeleton imports cleanly via `importlib` after registering in `sys.modules` before `exec_module` (a subtlety required because `@dataclass(frozen=True)` resolves field annotations through `sys.modules[cls.__module__]`).
- Installed `python3-venv` via scoped sudo (per CLAUDE.md sudo grant), then created `~/opt/docs/.venv/` with `pytest`, `ruff`, `mypy`.
- Ran `pytest -q tests/` to confirm conftest loads without errors — 0 tests collected (none written yet), 0 errors.

#### Issues / decisions

- **File-location correction.** The committed design said the executable was named `docs` at the repo root. That's impossible because `~/opt/docs/docs/` is a directory — POSIX disallows a file and directory with the same name in one parent. **Resolution:** moved to `~/opt/docs/bin/docs`. Updated `architecture.md`, `README.md`, and noted here. Clean Unix convention; minor extra hop in the install symlink command.
- **`Doc.archived` semantics.** Decided that the parser sets `archived` from path location, not from the in-doc `Status:` field. The two should agree (and `docs check` will report drift in M3), but at parse time we trust the filesystem as ground truth. This matches the dual-status decision (`docs/dual-status-adr.md`).
- **Vocabulary validation in `parse()`.** Documented in the `parse()` docstring that the bare call validates against `BUILTIN_STATUSES`/`BUILTIN_ROLES`. Callers needing per-project additions go through the walker, which has the Config in hand.
- **`scripts_are_modules` for mypy.** Mypy doesn't treat extensionless files as Python by default; the `scripts_are_modules = true` setting in `pyproject.toml` makes it work without renaming the file or symlinking a `.py` shim.

#### Exit criteria

- [x] Skeleton imports cleanly (`importlib` + `sys.modules` registration).
- [x] All declared dataclass fields and function signatures present.
- [x] Test infrastructure ready (`pyproject.toml`, `conftest.py`); `pytest` discovers 0 tests cleanly.
- [x] `architecture.md` renderer-format subspec written; file-location corrected.
- [x] Ready for Phase 2 to write failing tests against the contract.

#### Test results

`.venv/bin/python -m pytest tests/ -q` → `no tests ran in 0.00s` (expected; Phase 2 adds them).
