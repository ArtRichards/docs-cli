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
| 4. Run Tests (RED Baseline) | Complete | 2026-05-20 | 54 failed (all `NotImplementedError`), 3 passed (1 legit, 2 false-pass). Log-only, no commit. |
| 5. Update Base Interfaces | Complete | 2026-05-20 | `__post_init__` on `Doc` and `Config`; 5 shared utilities (`parse_date`, `validate_status`, `validate_role`, `parse_metadata_block`, `atomic_write`). RED baseline preserved at 54/3. |
| 6. Implement Offline/Core Path | Pending | — | — |
| 7. Update Tool/Wrapper Layer | Pending | — | — |
| 8. Run Tests (GREEN) | Pending | — | — |
| 9. Dogfood pass | Pending | — | — |
| 10. Quality, Docs, Refactor | Pending | — | — |

## Current State Analysis

- **Codebase:** No source code. `tests/` contains only `.gitkeep`.
- **Docs:** Eleven Markdown files in `docs/` plus this log. All hand-authored.
- **Build/test infra:** None. `pyproject.toml` does not yet exist.
- **Install path:** Intended `~/bin/docs` symlink to `~/opt/docs/bin/docs`; symlink not yet created.

## Files to Create / Modify

| File | Action | Phase | Notes |
|---|---|---|---|
| `bin/docs` (executable) | Create | 1, 5, 6, 7 | Single-file Python script. Relocated from repo root to `bin/` to avoid the file-vs-directory name collision with `docs/`. |
| `pyproject.toml` | Create | 1 | Project metadata + dev deps (pytest, ruff, mypy). Moved into Phase 1 from Phase 5 so pytest is discoverable before tests are written. |
| `tests/conftest.py` | Create | 1 | Loads `bin/docs` via `importlib.SourceFileLoader`, registers in `sys.modules['docs']`; provides `docs_script` and `fixtures_dir` fixtures. |
| `tests/test_model.py` | Create | 2 | Parser unit tests (16). |
| `tests/test_walker.py` | Create | 2 | Walker unit tests (9). |
| `tests/test_index.py` | Create | 2 | Renderer unit tests (13). |
| `tests/test_config.py` | Create | 2 | `load_config` + `find_root` (12). Added on Plan-agent recommendation to isolate pure functions from the walker. |
| `tests/test_cli_index.py` | Create | 2 | End-to-end CLI tests via subprocess (7). |
| `tests/fixtures/parser/*.md` | Create | 3 | Single-doc parser fixtures. |
| `tests/fixtures/trees/minimal/` | Create | 3 | Smallest valid tree (1 doc + `.docs.toml`). |
| `tests/fixtures/trees/with-archive/` | Create | 3 | Active + archive subtree + non-md + dotfile + dotdir + nested INDEX. |
| `tests/fixtures/trees/marker-preservation/` | Create | 3 | INDEX with hand-edited preamble + trailer outside the markers. |
| `tests/fixtures/expected/docs-INDEX.md` | Create | 3 | Frozen snapshot of live `docs/INDEX.md`; breaks circular acceptance in the dogfood test. |
| `docs/architecture.md` | Modify | 1 | Renderer-format subspec; file-location correction (`bin/docs`). |
| `README.md` | Modify | 1 | Install path corrected to `~/opt/docs/bin/docs`. |
| `docs/m1-parser-and-index.md` | Modify | every phase | Phase Checklist updated as phases complete. |
| `docs/m1-parser-and-index-log.md` | Modify | every phase | Phase log entries appended. |
| `docs/status.md` | Modify | every phase | Current phase advanced; M1 → Complete + M2 → ACTIVE at Phase 10. |
| `docs/plan.md` | Modify | 10 | If M1 work surfaces plan changes. |
| `docs/INDEX.md` | Regenerate | 9, 10 | Via `./bin/docs index docs/`. |

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

### Phase 4 — Run Tests (RED Baseline)

**Completed:** 2026-05-20

#### Objective
Confirm that all 57 collected tests fail for the **right** reason — missing implementation, not misconfiguration or fixture errors. Log-only phase; no commit.

#### Command + summary

```
.venv/bin/python -m pytest tests/
=========================== 54 failed, 3 passed in 0.34s ===========================
```

Every failure traces to one of:
- `NotImplementedError: parse() — Phase 6`
- `NotImplementedError: walk() — Phase 6`
- `NotImplementedError: render_index() — Phase 6`
- `NotImplementedError: load_config() — Phase 6`
- `NotImplementedError: find_root() — Phase 6`
- `NotImplementedError: main() — Phase 7` (CLI tests, raised inside subprocess)

No import errors. No fixture-path errors. No collection errors. Conftest loads cleanly.

#### The three baseline passes

| Test | Reason it passes | Action |
|---|---|---|
| `test_model.py::test_builtin_vocab_sizes` | Legitimate — only inspects constants, doesn't invoke any unimplemented function. | None. |
| `test_config.py::test_load_config_invalid_toml_raises` | **False pass.** Uses `pytest.raises(Exception)` which catches `NotImplementedError` too. | Tighten in Phase 6 to expect a more specific exception (e.g., `tomllib.TOMLDecodeError`). |
| `test_cli_index.py::test_index_nonexistent_root_exits_nonzero` | **False pass.** Asserts `returncode != 0`; `main()` raises NotImplementedError → nonzero exit → assertion satisfied. | Tighten in Phase 7 to additionally check stderr contains a recognizable error message. |

The two false-passes are flagged in this log so they're remembered when Phase 6/7 lands the implementations — without that, they would continue to pass and silently mask regressions.

#### Exit criteria

- [x] All failures attributable to missing implementation, not misconfiguration.
- [x] False-pass tests identified and queued for tightening in later phases.
- [x] No code committed in this phase (log-only).
- [x] Ready for Phase 5: implement dataclass validation and shared utilities.

### Phase 5 — Update Base Interfaces

**Completed:** 2026-05-20

#### Objective
Lock in dataclass invariants and ship the small, pure helpers that Phase 6 will compose into `parse()`, `load_config()`, and `render_index()` (and that M2 verbs will reuse for atomic writes). No business logic — `parse`, `walk`, `render_index`, `load_config`, `find_root`, and `main` stay `NotImplementedError`. RED baseline must not move.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `bin/docs` | Modify | Added `__post_init__` to `Doc` and `Config`; new "Shared utilities" section with `parse_date`, `validate_status`, `validate_role`, `parse_metadata_block`, `atomic_write`; added `import re` and `datetime` to the existing `from datetime import date` line. |
| `docs/m1-parser-and-index.md` | Modify | Phase 5 checkbox ticked. |
| `docs/m1-parser-and-index-log.md` | Modify | This entry; progress table row updated. |
| `docs/status.md` | Modify | Current phase advanced to Phase 6; resuming-this-work next action rewritten. |

#### What landed

**`Doc.__post_init__`** — structural invariants only (no vocab lookup, since vocab is Config-dependent):
- `title.strip()` non-empty
- `status`, `role` non-empty strings
- `updated` is a `date` instance

Raises `MetadataError` on violation. Compatible with the test_index.py `_doc()` helper and walker construction patterns.

**`Config.__post_init__`** — invariants on a resolved config:
- `project.strip()` non-empty
- `archive_dir` non-empty and a single path segment (no `/`)
- `date_format` non-empty
- `statuses` ⊇ `BUILTIN_STATUSES` (additive vocab per `vocab-adr.md`)
- `roles` ⊇ `BUILTIN_ROLES`

Raises `ValueError` (Config comes from TOML / programmer code, not from doc text — `MetadataError` would be the wrong category).

**`parse_date(value, date_format="%Y-%m-%d") -> date`** — wraps `datetime.strptime(...).date()`; raises `MetadataError` with a uniform message on `ValueError`. Pulled out so Phase 6 `parse()` gets a consistent error string for the `Updated:` field.

**`validate_status` / `validate_role`** — pure value-in-set checks; raise `VocabularyError` on miss.

**`parse_metadata_block(text) -> (title, metadata, body)`** — combined helper per the answered design question. Pure syntax extraction:

- Finds the H1 (raises `MetadataError` if missing or wrong shape).
- Parses a run of `Label: value` and `Label:` + `- bullet` items.
- **Allows blank-line-separated multi-value groups** (e.g., `Related:` after a blank line, with bullets) — this matches the project's own doc fixtures (`tests/fixtures/parser/well-formed.md`, the `WELL_FORMED` string in `test_model.py`).
- An inline `Label: value` line after a blank line terminates the metadata block (body), matching `test_parse_metadata_block_terminates_at_blank_line`.
- A non-label non-blank line silently ends the metadata block — `parse()` will report the actual missing-required-field error in Phase 6 with better context than this helper could give.

The body preserves blank lines between paragraphs and a trailing newline if the input ended in one.

**`atomic_write(path, content)`** — tmpfile + `Path.replace`, exactly as `architecture.md` specifies. Used by Phase 6 `render_index` (INDEX.md write) and reused by every M2 mutating verb.

#### Issues / decisions

- **No `Vocab` dataclass.** The M1 plan Phase 5 description listed `Doc`, `Vocab`, `Config`. Phase 1 settled on `Config` carrying `statuses` and `roles` directly, and no Phase 2 test references `Vocab`. Introducing it now would be churn with no consumer. Defer until something needs to pass vocab around independently of Config (possibly M3 query views).
- **`find_root` deferred to Phase 6.** The M1 plan lists it under Phase 5, but the session brief from the user groups it with `load_config` in Phase 6. Both `load_config` and `find_root` touch the filesystem and are best implemented together with consistent error handling — keeping them in Phase 6 simplifies that.
- **Lenient metadata-block termination.** Originally drafted strict: any non-label non-blank line inside the block raised `MetadataError("malformed metadata line: …")`. Relaxed to "non-label terminates the block" because (a) it handles the degenerate "H1 + body, no metadata" case gracefully, and (b) `parse()` will produce a clearer "missing Status" / "missing Role" / "missing Updated" message in Phase 6 than a "malformed metadata line" error pointing at the first body line ever could.
- **Blank-line-separated multi-value groups.** `convention.md` says "contiguous run of Label: value lines, ending at the next blank line", but the project's own fixtures (and the `WELL_FORMED` test string) separate the inline group from `Related:` with a blank line and still expect `Related` to be metadata. The helper handles this with a peek-past-blank-lines pass that continues the block iff the next non-blank line is a bare label followed by a `- ` bullet. The convention text may want a follow-up clarification; flagged here rather than edited in Phase 5.

#### Test results

```
.venv/bin/python -m pytest tests/ -q
=========================== 54 failed, 3 passed in 0.36s ===========================
```

Identical to the Phase 4 RED baseline — Phase 5 changes are purely additive and don't alter any test outcome.

Quality gates over the changed file:
```
.venv/bin/ruff check bin/docs              # All checks passed!
.venv/bin/ruff format --check bin/docs     # 1 file already formatted
.venv/bin/mypy bin/docs                    # Success: no issues found in 1 source file
```

#### Exit criteria

- [x] `Doc.__post_init__` and `Config.__post_init__` enforce structural invariants without referencing Config-dependent vocab.
- [x] Five shared utilities implemented and importable.
- [x] `import re`, `datetime` added; no other new top-level deps.
- [x] RED baseline preserved (54 failed, 3 passed).
- [x] ruff + mypy clean on `bin/docs`.
- [x] Ready for Phase 6: implement `parse`, `walk`, `render_index`, `load_config`, `find_root` using these utilities.
