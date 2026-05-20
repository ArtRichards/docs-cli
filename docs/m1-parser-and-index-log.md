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
| 6. Implement Offline/Core Path | Complete | 2026-05-20 | `parse`, `walk`, `render_index`, `load_config`, `find_root` implemented. 4 unit-test files all green (50/50). Tightened false-pass `test_load_config_invalid_toml_raises` → `pytest.raises(tomllib.TOMLDecodeError)`. Suite now 51 passed / 6 failed (CLI tests). |
| 7. Update Tool/Wrapper Layer | Complete | 2026-05-20 | `main()` wired with argparse + `_cmd_index` dispatch. 6/7 CLI tests green; the 7th (`test_index_output_matches_frozen_snapshot`) fails on hand-curated snapshot text — deferred to Phase 9. Tightened false-pass `test_index_nonexistent_root_exits_nonzero` with stderr substring check. Suite now 56 passed / 1 failed. |
| 8. Run Tests (GREEN) | Complete | 2026-05-20 | First repo-wide `ruff check .` / `ruff format --check .` surfaced an import-block lint warning in `tests/test_model.py`; fixed. Test count unchanged. |
| 9. Dogfood pass | Complete | 2026-05-20 | Dogfood revealed a renderer bug: substring-based marker detection false-matched against backtick-quoted marker mentions in the preamble prose, corrupting `docs/INDEX.md`. Fixed with line-anchored detection (`_find_marker_lines`). Added regression test. Reconciled `tests/fixtures/expected/docs-INDEX.md` against the spec-correct rendered output. Suite now 58 passed / 0 failed. |
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

### Phase 6 — Implement Offline/Core Path

**Completed:** 2026-05-20

#### Objective
Implement the five core functions on top of the Phase 5 utilities: `parse`, `walk`, `render_index`, `load_config`, `find_root`. Drive all four unit-test files (`test_model.py`, `test_walker.py`, `test_index.py`, `test_config.py`) green. CLI subprocess tests in `test_cli_index.py` stay RED until Phase 7 wires `main()`.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `bin/docs` | Modify | Implementations replace `NotImplementedError` stubs for `parse`, `walk`, `render_index`, `load_config`, `find_root`. New module-level helpers `_format_entry` and `_description`. New imports: `os`, `dataclasses.replace`. `tomllib` and `re` lose their `# noqa: F401` markers (now used). |
| `tests/test_config.py` | Modify | Tightened `test_load_config_invalid_toml_raises` from `pytest.raises(Exception)` to `pytest.raises(tomllib.TOMLDecodeError)` (Phase 4 false-pass cleanup). |
| `docs/m1-parser-and-index.md` | Modify | Phase 6 checkbox ticked. |
| `docs/m1-parser-and-index-log.md` | Modify | This entry; progress table row updated. |
| `docs/status.md` | Modify | Current phase → Phase 7; next-action paragraph rewritten for CLI work. |

#### What landed

**`parse(text, path, root)`** — uses `parse_metadata_block` for syntax, then checks required `Status`/`Role`/`Updated`, runs `validate_status`/`validate_role` against `BUILTIN_STATUSES`/`BUILTIN_ROLES`, parses the date via `parse_date`, splits `Related:` bullets into `(verb, target)` tuples, and harvests every remaining metadata field into `extra`. Always sets `archived=False`; walker flips it.

**`walk(root, config)`** — `os.walk` with `topdown=True` so dotdirs prune in-place via `dirnames[:] = ...`. Skips dotfiles, non-`.md`, and the root-level `INDEX.md` (root-relative path == `"INDEX.md"`). Re-stamps `archived=True` via `dataclasses.replace` for paths under `config.archive_dir`. Final sort is by root-relative POSIX path, lexicographic.

**`render_index(docs, config, existing)`** — builds the derived content (summary line + per-role groups + Archived section) and handles marker-block preservation. Role ordering: `status` pinned first, then `CANONICAL_ROLE_ORDER` minus `status`. Within-group sort: `(-updated.toordinal(), path.name)` so newer comes first and ties break by filename. Empty role groups omitted. Archived section shows `_None._` when empty. Marker handling splits on `MARKER_START` / `MARKER_END` substrings to preserve preamble and trailer verbatim.

**`_format_entry(doc, config)`** — emits `- [name](name) — _role_ — desc. Updated YYYY-MM-DD.`. Link target is the basename (matches the test contract and the snapshot's root-doc format).

**`_description(body, limit=120)`** — skips leading blank and header lines (`#…` of any depth), joins the first paragraph's lines with spaces, collapses runs of whitespace, and truncates at the last whitespace ≤ `limit` with a `…` suffix. Falls back to a hard cut if no whitespace is found within `limit`.

**`load_config(root)`** — reads `root/.docs.toml` with `tomllib.loads` (propagating `tomllib.TOMLDecodeError` on malformed input), pulls `[project] name`, `[archive] dir`, `[archive] date_format`, and `[vocabulary] add_statuses` / `add_roles`. Project name falls back to `root.resolve().name` and then `"root"` for the empty-name edge case. Vocab is the frozenset union of built-ins with project additions.

**`find_root(start)`** — walks up from `start.resolve()` looking for `.docs.toml`. Terminates at the filesystem root (`parent == current`) and falls back to `start.resolve()` when none is found.

#### Issues / decisions

- **`parse()` validates against built-in vocab only.** Per the Phase 1 docstring decision: the bare `parse()` call doesn't have a Config, so it uses `BUILTIN_STATUSES` / `BUILTIN_ROLES`. The walker passes through the parsed Doc without re-validating against the project's extended vocab. M3's `docs check` is the place to enforce extended vocab consistently across the tree.
- **`Related:` paths preserved as-written.** Spec says paths normalize to root-relative, but the M1 test contract just uses simple filenames like `other.md`. Preserving as-written is byte-equivalent for those cases and avoids guessing what root-relative means when the path is already root-relative. M3's `docs check` will resolve and validate.
- **Renderer uses `d.path.name` for the link.** Matches `test_render_entry_format` and the snapshot's format. For nested docs (e.g., `archive/2026-01-01/old-plan.md`), links would be ambiguous if two siblings share a basename — flagged in the plan's open/deferred section, no M1 test exercises it.
- **Renderer date uses `date.today()`.** No test asserts a specific date; idempotency tests pass twice in quick succession. Phase 9 dogfood will be sensitive to this on day boundaries — acceptable risk for M1.
- **Empty body → empty description.** No test exercises this; entry line gets awkward spacing (`— _role_ — . Updated …`) but no behavioral breakage. Leave for Phase 9 polish if it shows up.
- **`tomllib` and `re` lose `# noqa: F401`.** Both are now consumed; the comments became stale.

#### Test results

```
.venv/bin/python -m pytest tests/ -q
=========================== 6 failed, 51 passed in 0.24s ===========================
```

Breakdown:
- `tests/test_model.py` 16/16 ✓
- `tests/test_walker.py` 9/9 ✓
- `tests/test_index.py` 13/13 ✓
- `tests/test_config.py` 12/12 ✓ (including the tightened false-pass)
- `tests/test_cli_index.py` 1/7 (only the surviving false-pass `test_index_nonexistent_root_exits_nonzero` passes; the rest fail on `main()` `NotImplementedError`)

The plan predicted 50 passing, 7 failing. The actual 51/6 split reflects the lingering CLI false-pass: `test_index_nonexistent_root_exits_nonzero` only checks `returncode != 0`, which `main()` raising `NotImplementedError` satisfies. Phase 7 will tighten it.

Quality gates:
```
.venv/bin/ruff check bin/docs             # All checks passed!
.venv/bin/ruff format --check bin/docs    # 1 file already formatted
.venv/bin/mypy bin/docs                   # Success: no issues found in 1 source file
```

#### Exit criteria

- [x] `parse`, `walk`, `render_index`, `load_config`, `find_root` implemented.
- [x] All four unit-test files green (50/50 unit tests passing).
- [x] False-pass `test_load_config_invalid_toml_raises` tightened.
- [x] Quality gates clean on `bin/docs`.
- [x] CLI tests fail only because `main()` is still `NotImplementedError` (expected).
- [x] Ready for Phase 7: wire argparse, dispatch `index` subcommand, handle exit codes.

### Phase 7 — Update Tool/Wrapper Layer

**Completed:** 2026-05-20

#### Objective
Wire the CLI: argparse for the `index` subcommand, dispatch to the Phase 6 implementations, map errors to the `cli.md` exit-code matrix, and tighten the second Phase-4-flagged false-pass. After this phase, every test except the dogfood snapshot match goes green.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `bin/docs` | Modify | `main()` replaced with argparse dispatcher + `_build_parser()` + `_cmd_index()`. Dropped `# noqa: F401` on `argparse` (now used). |
| `tests/test_cli_index.py` | Modify | (1) Tightened `test_index_nonexistent_root_exits_nonzero` to additionally assert `"not found" in proc.stderr.lower()`. (2) Fixed `test_index_minimal_tree_exits_zero` to `shutil.copytree` the fixture into `tmp_path` first; previously it ran the CLI directly against the source fixture and wrote `INDEX.md` into `tests/fixtures/trees/minimal/`, polluting the working tree. |
| `docs/m1-parser-and-index.md` | Modify | Phase 7 checkbox ticked. |
| `docs/m1-parser-and-index-log.md` | Modify | This entry; progress table row updated. |
| `docs/status.md` | Modify | Current phase advanced to Phase 8; next-action paragraph rewritten to flag the Phase 8 + Phase 9 overlap. |

#### What landed

**`_build_parser()`** — `ArgumentParser(prog="docs")` with `add_subparsers(required=True)`. One subparser `index` carrying:
- `dir` (positional, optional) — alternative to `--root`.
- `--root ROOT` — explicit docs root; overrides positional `DIR` if both given.
- `--quiet` — suppresses the "wrote …" success message on stderr.
- `--dry-run` — writes the rendered output to stdout instead of touching the INDEX.md file.

`--json` from cli.md is not relevant to `index` (write-only operation) and is deferred to M3 when `docs list` / `docs check` land.

**`_cmd_index(args)`** — root resolution → existence check → load_config + walk (wrapped in try/except for the two exception categories) → render → either dry-run print or `atomic_write`. Exit-code mapping per cli.md:
- `0` — success, including dry-run.
- `1` — recoverable: root path missing or not a directory.
- `2` — hard error: TOMLDecodeError on `.docs.toml`, MetadataError or VocabularyError surfacing from `parse()` during `walk`.

**`main(argv=None)`** — builds the parser, parses args, dispatches to `_cmd_index`. The defensive `return 2` for unknown commands is unreachable in practice (`required=True` on the subparsers makes argparse error before we look at `args.command`) but documents intent.

**Tightened test.** `test_index_nonexistent_root_exits_nonzero` was a Phase 4 false-pass — `NotImplementedError` triggered a nonzero exit, satisfying `returncode != 0` for the wrong reason. Now it pins:
- `returncode != 0`
- `proc.stderr` non-empty
- `"not found" in proc.stderr.lower()` — locks the error wording from `_cmd_index` step 2.

#### Issues / decisions

- **Root resolution precedence.** `--root` > positional `dir` > `find_root(Path.cwd())`. This matches cli.md's "--root DIR — explicit docs root" wording (explicit means it wins over inference). The positional `dir` is the `[DIR]` form from cli.md for `docs index [DIR]`.
- **Dry-run writes to stdout, not stderr.** Pipe-friendly (`docs index --dry-run | less`). Tests don't assert the stream, so the choice is free; stdout is the conventional "data" stream.
- **`--quiet` only silences success messages.** Errors always go to stderr regardless of `--quiet`. cli.md's "Human output goes to stdout; errors and progress to stderr" is the guiding rule.
- **Exception → exit code mapping.** TOMLDecodeError, MetadataError, VocabularyError → 2 (per cli.md "invalid vocab, atomic operation failure, validation errors"). Missing root → 1 (per cli.md "missing input"). No other branches needed for M1's `index`.
- **No global flags before the subcommand.** All flags live on the `index` subparser. When M2 adds more subcommands, refactor to a parent parser if they share flags. YAGNI for one subcommand.

#### Test results

```
.venv/bin/python -m pytest tests/test_cli_index.py -q
1 failed, 6 passed in 0.23s

.venv/bin/python -m pytest tests/ -q
1 failed, 56 passed in 0.27s
```

The lone failure is `test_index_output_matches_frozen_snapshot`. The hand-curated descriptions in `tests/fixtures/expected/docs-INDEX.md` (e.g. "What we're building, why, success criteria, non-goals, audience.") don't match the renderer's `_description()` extraction of the first body paragraph from the source docs. This is exactly the dogfood-acceptance gap that Phase 9 exists to reconcile.

Manual smoke confirmed clean:
- `./bin/docs index --help` exits 0 and prints the subcommand usage.
- `./bin/docs index --root tests/fixtures/trees/minimal --dry-run` prints the marker block + entry for `lone-doc.md` with no file written.

Quality gates:
```
.venv/bin/ruff check bin/docs              # All checks passed!
.venv/bin/ruff format --check bin/docs     # 1 file already formatted
.venv/bin/mypy bin/docs                    # Success: no issues found in 1 source file
```

#### Exit criteria

- [x] `main()` and the `index` subcommand fully wired.
- [x] argparse `--help` / exit codes / flag combinations exercised by tests.
- [x] False-pass `test_index_nonexistent_root_exits_nonzero` tightened.
- [x] All but the dogfood-snapshot test pass.
- [x] Quality gates clean on `bin/docs`.
- [x] Ready for Phase 8 (quality gate sweep) and Phase 9 (snapshot reconciliation) — likely combined in the next session since the snapshot diff is the only outstanding work.

### Phase 8 — Run Tests (GREEN)

**Completed:** 2026-05-20

#### Objective
Run the full quality gate over the repo (not just `bin/docs`). Confirm the only outstanding failure is the dogfood snapshot mismatch — which Phase 9 owns.

#### What landed

- Found and fixed an import-block lint issue in `tests/test_model.py` (extra blank line between `from docs import (…)` and `WELL_FORMED`). Ruff's `--fix` handled it; format pass picked up `tests/test_config.py` for a trivial line collapse too.
- Tests unchanged at 56 passed / 1 failed (snapshot mismatch). Quality gates clean.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `tests/test_model.py` | Modify | Lint fix (`I001`) — removed extra blank line. |
| `tests/test_config.py` | Modify | Format pass — single line collapse, no semantic change. |
| `docs/m1-parser-and-index.md` | Modify | Phase 8 checkbox ticked. |
| `docs/m1-parser-and-index-log.md` | Modify | This entry. |

#### Issues / decisions

- **Repo-wide ruff was never invoked.** Prior phases ran `ruff check bin/docs` and `ruff format --check bin/docs` because the executable was the only Phase 1–7 work. The test files inherited lint debt from when they were written in Phase 2. Phase 8 closes that gap; from now on the quality gate covers `.` (the whole tree).

#### Exit criteria

- [x] `pytest -q` — same baseline as Phase 7 entry (56 passed / 1 failed).
- [x] `ruff check .` clean.
- [x] `ruff format --check .` clean.
- [x] `mypy bin/docs` clean.
- [x] Ready for Phase 9: reconcile the dogfood snapshot.

### Phase 9 — Dogfood pass (mapped from "Online/Integration")

**Completed:** 2026-05-20

#### Objective
Run `./bin/docs index docs/` against this repo's own docs root, surface any drift between hand-written and generated INDEX.md, and reconcile. Originally framed as a snapshot-update step; uncovered a real renderer bug along the way.

#### What landed

**Bug found and fixed:** the renderer's marker detection used `existing.split(MARKER_START, 1)` which matches the first occurrence anywhere in the text. The live `docs/INDEX.md` preamble documents the marker convention with backtick-quoted mentions like `` `<!-- docs:generated start -->` ``. The naive split matched the prose mention, treated the preamble's first marker reference as the real marker, and corrupted the output (the trailer became literal text like `` ` is rewritten.\n ``).

**Fix:** new module-level helper `_find_marker_lines(text)` scans the input line by line and matches a marker only when it appears as a standalone line. Returns character offsets so the renderer can slice `pre` / `trailer` precisely. The trailer "owns" what's past the marker text (including newlines), keeping idempotency byte-exact.

**Regression test:** `tests/test_index.py::test_render_ignores_marker_mentions_inside_prose` constructs a preamble that mentions the markers inside backticks and verifies the real (standalone-line) marker is the one consumed.

**Snapshot reconciliation:** with the bug fixed, ran `./bin/docs index --root docs/` to regenerate the live INDEX.md, then copied the result over `tests/fixtures/expected/docs-INDEX.md`. The previous snapshot had two issues that came from being hand-authored before the implementation existed:
1. **Hand-curated descriptions** — every entry's description was custom prose, while the spec (`architecture.md`'s "INDEX renderer format") says descriptions come from the first non-empty body paragraph. The snapshot text wasn't derivable from any doc body.
2. **Non-canonical section order** — Spec appeared after Log, but `CANONICAL_ROLE_ORDER` puts Spec at position 2 (after charter, plan) — well before Milestone and Log.

Reconciliation favored the spec: the snapshot now matches what the spec-compliant renderer produces. Future drift in the live `docs/INDEX.md` (real bodies change) will require updating both files in lockstep — the dogfood test guards against silent drift.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `bin/docs` | Modify | Replaced `existing.split(MARKER_START, 1)` with a line-anchored `_find_marker_lines` helper. Trailer now owns what follows the marker text. |
| `tests/test_index.py` | Modify | Added `test_render_ignores_marker_mentions_inside_prose` regression test. |
| `tests/fixtures/expected/docs-INDEX.md` | Modify | Reconciled against the spec-compliant renderer output. Replaces the hand-authored aspirational snapshot. |
| `docs/INDEX.md` | Modify | Regenerated via `./bin/docs index docs/`. Hand-edited preamble and trailer preserved verbatim. |
| `docs/m1-parser-and-index.md` | Modify | Phase 9 checkbox ticked. |
| `docs/m1-parser-and-index-log.md` | Modify | This entry. |

#### Issues / decisions

- **Bug class: substring vs line.** The original `MARKER_START in existing` check is forgiving (it'll match anywhere), but the slice operation downstream relies on the marker appearing in a structural position. Mixing those two contracts is the bug. Line-anchored matching aligns the structural use with the contract.
- **Reconciling forward, not backward.** The hand-authored snapshot's descriptions were unreachable from any algorithmic source. Three options were considered: (a) update the renderer to match — but the renderer follows the spec, and there's no derivable rule; (b) add a `Description:` metadata field — out of M1 scope; (c) update the snapshot — accepts the spec as the source of truth. Picked (c).
- **Idempotency preserved.** The line-anchored helper returns `post_start = cursor + len(stripped_marker)`, so the trailer takes ownership of the marker line's `\n`. Re-rendering yields byte-identical output (`test_render_is_idempotent` still passes).

#### Test results

```
.venv/bin/python -m pytest tests/ -q
=========================== 58 passed in 0.27s ===========================
```

Includes the new regression test. All Phase 7 false-pass cleanup holds.

```
.venv/bin/ruff check .                  # All checks passed!
.venv/bin/ruff format --check .         # 7 files already formatted
.venv/bin/mypy bin/docs                 # Success: no issues found
```

Dogfood idempotency confirmed: running `./bin/docs index docs/` twice in a row produces zero diff against the committed snapshot.

#### Exit criteria

- [x] `./bin/docs index docs/` produces output matching the (reconciled) snapshot byte-for-byte.
- [x] Re-running is a no-op (idempotent).
- [x] Hand-edited preamble and trailer in `docs/INDEX.md` survived the dogfood run.
- [x] Bug surfaced by dogfood is fixed with a regression test.
- [x] Ready for Phase 10: M1 close-out (status.md, plan.md, milestone summary).
