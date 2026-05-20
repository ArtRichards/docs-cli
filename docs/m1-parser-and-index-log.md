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
| 2. Write Tests (RED) | Complete | 2026-05-20 | 57 tests across 5 files. Collect cleanly; expected to fail with NotImplementedError. |
| 3. Create Data/Fixtures | Complete | 2026-05-20 | 15 fixture files across `parser/`, `trees/{minimal,with-archive,marker-preservation}/`, `expected/`. |
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

### Phase 2 — Write Tests (RED)

**Completed:** 2026-05-20

#### Objective
Express every required behavior as a failing test. Tests will fail with `NotImplementedError` (or fixture-missing errors until Phase 3 lands) — the GREEN state is Phase 6+.

#### Files changed

| File | Action | Tests |
|---|---|---|
| `tests/test_model.py` | Create | 16 — parser happy path, missing fields, malformed Updated, unknown vocab, multi-value Related, extra labels harvested, body extraction, archived-false-by-default. |
| `tests/test_walker.py` | Create | 9 — minimal tree, root-INDEX exclusion, nested-INDEX inclusion, non-md exclusion, dotfile exclusion, determinism, sort order, archived flag set under archive_dir, active+archive counts. |
| `tests/test_index.py` | Create | 13 — minimal vs preserved INDEX, idempotency, summary line, count correctness, status pinned, canonical role order, empty role omission, sort tiebreaker, archived section, entry format, description from first paragraph, truncation. |
| `tests/test_config.py` | Create | 12 — defaults, project from dir name, explicit project, archive_dir override, additive status/role extension, root edge case, find_root upward walk and fallback, invalid TOML. |
| `tests/test_cli_index.py` | Create | 7 — `--help`, minimal-tree exit 0, writes INDEX.md, `--dry-run` non-mutating, nonexistent root nonzero, marker preservation, frozen-snapshot match. |

Total: 57 tests collected. Pytest collection time: 0.03s, no import errors.

#### Actions taken

- Wrote unit tests against the imported `docs` module (`from docs import …`).
- CLI tests use `subprocess.run([sys.executable, str(docs_script), …])` rather than relying on `chmod +x` or PATH — robust across hosts.
- Tests reference fixture files at `tests/fixtures/{parser,trees,expected}/`. These don't exist yet; Phase 3 creates them.
- The `test_index_output_matches_frozen_snapshot` test is the dogfood guard against circular acceptance — it asserts against a frozen snapshot rather than the live `docs/INDEX.md`.

#### Issues / decisions

- **`parse()` does not set `archived`.** During test design realized that `parse()` doesn't have access to `Config.archive_dir`, so it can't know if a path is "under the archive subtree." Decision: `parse()` always sets `archived=False`; the walker uses `dataclasses.replace(doc, archived=True)` when the path is under `root/config.archive_dir`. Updated `test_parse_archived_flag_is_false_by_default` (model) and `test_walk_archived_flag_set_for_archive_subtree` (walker) to reflect this split of responsibilities.
- **Vocab validation in `parse()` (bare call).** Tests construct text inline and call `parse(text, path, root)` directly — no Config. The `parse()` docstring (Phase 1) says the bare call validates against `BUILTIN_STATUSES`/`BUILTIN_ROLES`. Tests rely on this.
- **CLI test `test_index_nonexistent_root_exits_nonzero`** asserts only that exit code is non-zero — leaving Phase 7 free to choose 1 or 2 per `cli.md`'s exit-code matrix.
- **Description truncation indicator.** Test accepts either Unicode ellipsis `…` or ASCII `...` to give Phase 6 implementation flexibility (the spec in `architecture.md` says "suffix with `…`" but `...` is acceptable for terminals without good Unicode).
- **No fixture for `tests/fixtures/expected/docs-INDEX.md` at this point.** Phase 3 creates it as a frozen snapshot of the live `docs/INDEX.md`.

#### Exit criteria

- [x] 57 tests collected without import errors.
- [x] Tests cover every critical-path item from `test-strategy.md`.
- [x] Tests use the conftest-loaded `docs` module; no path manipulation in individual test files.
- [x] Subprocess CLI tests use `sys.executable` for portability.
- [x] Ready for Phase 3 (build fixtures) → Phase 4 (RED baseline confirms NotImplementedError failures).

### Phase 3 — Create Data/Fixtures

**Completed:** 2026-05-20

#### Objective
Hand-build the fixture trees and the frozen INDEX snapshot referenced by Phase 2 tests, so the only remaining cause of test failures at Phase 4 is `NotImplementedError`.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `tests/fixtures/parser/well-formed.md` | Create | Single-doc parser fixture: H1, full metadata block, two content sections. |
| `tests/fixtures/trees/minimal/.docs.toml` | Create | Root marker + all defaults explicit (also documents what defaults look like). |
| `tests/fixtures/trees/minimal/lone-doc.md` | Create | Only doc in the minimal tree. `Role: notes`. |
| `tests/fixtures/trees/with-archive/.docs.toml` | Create | Root marker. |
| `tests/fixtures/trees/with-archive/alpha.md` | Create | Active spec. Newer Updated date (2026-05-21). |
| `tests/fixtures/trees/with-archive/beta.md` | Create | Active charter. Older Updated date (2026-05-19). |
| `tests/fixtures/trees/with-archive/notes.txt` | Create | Non-Markdown file. Walker must skip. |
| `tests/fixtures/trees/with-archive/.hidden-file` | Create | Dotfile. Walker must skip. |
| `tests/fixtures/trees/with-archive/.private/should-not-be-walked.md` | Create | Doc under a dotdir. Walker must skip the directory entirely. |
| `tests/fixtures/trees/with-archive/archive/2026-01-01/old-plan.md` | Create | Archived plan. `Status: archived`, under archive subtree. Walker sets `archived=True`. |
| `tests/fixtures/trees/with-archive/archive/2026-01-01/INDEX.md` | Create | Nested INDEX.md. `Role: log` (exercises the broadened log definition from vocab-adr.md). Walker treats it as a regular doc — only the **root-level** INDEX is special. |
| `tests/fixtures/trees/marker-preservation/.docs.toml` | Create | Root marker. |
| `tests/fixtures/trees/marker-preservation/lone-doc.md` | Create | Active spec, sole doc in the tree. |
| `tests/fixtures/trees/marker-preservation/INDEX.md` | Create | Has hand-edited preamble before `<!-- docs:generated start -->` and trailer after `<!-- docs:generated end -->`. Renderer must preserve both. |
| `tests/fixtures/expected/docs-INDEX.md` | Create | Frozen snapshot of the live `docs/INDEX.md` at the time of this commit. The CLI test `test_index_output_matches_frozen_snapshot` asserts against this, breaking the circular-acceptance risk that Phase 9 alone would have. |

#### Actions taken

- Created the directory structure under `tests/fixtures/` (parser, trees/minimal, trees/with-archive + archive subtree + dotdir, trees/marker-preservation, expected).
- Used `cp` to freeze the current `docs/INDEX.md` into `tests/fixtures/expected/docs-INDEX.md`. If Phase 9 produces output that diverges, reconciliation will update either the snapshot or the renderer (per the dogfood acceptance criterion).
- Verified `git add --dry-run` includes all 15 fixture files, including the dotfile and dotdir contents (git tracks them; the walker just needs to ignore them at runtime).

#### Issues / decisions

- **Nested INDEX.md uses `Role: log`.** Per the convention.md update broadening the `log` role, a chronological snapshot at archive time is a natural fit (the doc accumulated entries for the duration of that archive date, then closed when the directory was sealed).
- **Both active docs in `with-archive/` have distinct Updated dates** so renderer tests can verify descending-by-Updated sort independently of the path-ascending tiebreaker.
- **`marker-preservation/INDEX.md` placeholder content.** Inside the markers I put a deliberately wrong placeholder (`_Generated 2000-01-01. 0 docs active, 0 archived._`) so it's obvious when a successful run has overwritten it.

#### Exit criteria

- [x] All test fixture paths referenced by Phase 2 tests exist.
- [x] `with-archive/` includes the full matrix of fixture concerns: non-md, dotfile, dotdir, archive subtree, nested INDEX.
- [x] Frozen `expected/docs-INDEX.md` snapshot in place.
- [x] Ready for Phase 4: run pytest and capture the RED baseline.
