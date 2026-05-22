# M3 — Implementation Log

Status: active
Role: log
Project: docs
Updated: 2026-05-22

Related:
- child-of: m3-validation-and-query.md
- pairs-with: status.md

## Implementation metadata

- Project: docs
- Milestone: M3 — Validation and query (`check`, `list`)
- Started: 2026-05-22
- Progress: Phases 1–4 complete — contract, RED tests, fixtures, and the RED
  baseline (55 failed / 109 passed) are in place. **The session paused at the
  RED baseline by request;** phases 5–10 resume implementation.

(Note: doc-lifecycle status is in the front-matter `Status:` field above. This
section tracks milestone progress, which is distinct.)

## Summary

Add the two read-only verbs — `docs check` (validation with CI-usable exit
codes) and `docs list` (filterable query view with a stable JSON schema) — and
rework the INDEX renderer into a two-level `Project` → `Role` layout. `check`
and `list` reach docs through a new lenient traversal (`_iter_doc_texts`) so a
malformed tree is reported, not crashed on.

## TDD Phase Progress

| Phase | Status | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-05-22 | `Finding` + 8 helper stubs + 2 `_cmd_*` stubs + `check`/`list` subparsers in `bin/docs`; `cli.md` JSON schemas pinned; `architecture.md` INDEX format reworked; M3 plan + log created. |
| 2. Write Tests (RED) | Complete | 2026-05-22 | 52 M3 tests across 4 new files; `test_index.py` reworked for two-level grouping (5 updated, 3 added). 164 tests collect cleanly. |
| 3. Create Data/Fixtures | Complete | 2026-05-22 | Three fixture trees: `drift/` (4 docs), `invalid/` (7 docs), `multi-project/` (9 docs). |
| 4. Run Tests (RED Baseline) | Complete | 2026-05-22 | 55 failed / 109 passed. Every M3 failure traces to `NotImplementedError`, a stub exit code, or the un-reworked renderer. **Session paused here by request.** |
| 5. Update Base Interfaces | Pending | — | `_iter_doc_texts`, `check_doc`, `exit_code_for`, `_resolved_project`; INDEX renderer rework. |
| 6. Implement Offline/Core Path | Pending | — | `check_tree`, `query_docs`, verb cores. |
| 7. Update Tool/Wrapper Layer | Pending | — | `--json` output, exit-code mapping. |
| 8. Run Tests (GREEN) | Pending | — | |
| 9. Implement Online/Integration | Pending | — | Dogfood `check` / `list` on `docs/`. |
| 10. Quality, Docs, Refactor | Pending | — | |

## Current State Analysis (snapshot at milestone kickoff, 2026-05-22)

_Captured before Phase 1; historical._

- **Codebase:** `bin/docs` shipped at M1+M2 — parser, walker, renderer, five
  verbs, config loading, surgical metadata editors. 112 passing tests across
  10 files.
- **Reuse available:** `parse`, `parse_metadata_block`, `_metadata_line_span`,
  `walk`, `validate_status`, `validate_role`, `parse_date`, `load_config`,
  `find_root`, `render_index`, `_format_entry`, `atomic_write`,
  `_refresh_index` — all tested.
- **Gap:** `parse()` / `walk()` raise on a malformed doc; `check` must report
  such docs, and `list` must still exit 0. M3 adds a lenient traversal.
- **Renderer:** `render_index` groups by `Role` only; M3 reworks it to a
  two-level `Project` → `Role` layout (resolves a plan.md open question).

## Files to Create / Modify

| File | Action | Phase | Notes |
|---|---|---|---|
| `bin/docs` | Modify | 1, 5, 6, 7 | M3 contract stubs (P1); helpers + renderer rework (P5); verb cores (P6); `--json` + CLI wiring (P7). |
| `docs/m3-validation-and-query.md` | Create | 1 | This milestone's task plan. |
| `docs/m3-validation-and-query-log.md` | Create | 1 | This log. |
| `docs/cli.md` | Modify | 1 | `check --json` / `list --json` schemas pinned; `--json` added to `check`; "unknown extra fields" dropped; `Updated` bumped. |
| `docs/architecture.md` | Modify | 1 | INDEX renderer-format subspec → two-level grouping; `Updated` bumped. |
| `docs/status.md` | Modify | 1, …, 10 | M3 phase tracking; M3 → Complete at Phase 10. |
| `docs/plan.md` | Modify | 10 | Resolve the INDEX-grouping open question. |
| `docs/INDEX.md` | Regenerate | 1, 5, 9 | Picks up the two new M3 docs (P1, still flat); two-level layout (P5). |
| `tests/fixtures/expected/docs-INDEX.md` | Modify | 1, 5 | Re-synced with `docs/INDEX.md` in lockstep. |
| `tests/test_check.py` | Create | 2 | `check_doc` / `check_tree` / `exit_code_for` unit tests. |
| `tests/test_query.py` | Create | 2 | `query_docs` filter / sort unit tests. |
| `tests/test_cli_check.py` | Create | 2 | `docs check` CLI tests. |
| `tests/test_cli_list.py` | Create | 2 | `docs list` CLI tests. |
| `tests/test_index.py` | Modify | 2 | Renderer tests reworked for two-level grouping. |
| `tests/fixtures/trees/drift/` | Create | 3 | Status/location mismatches. |
| `tests/fixtures/trees/invalid/` | Create | 3 | One doc per non-drift error rule. |
| `tests/fixtures/trees/multi-project/` | Create | 3 | Multi-project / status / role tree. |

## Phase logs

### Phase 1 — Define Contract

**Completed:** 2026-05-22

#### Objective

Declare the full M3 surface in `bin/docs` — the `Finding` model, the validation
and query helper signatures, the two `_cmd_*` handlers, the `check` / `list`
subparsers — with no business logic. Pin the JSON schemas in `cli.md` and the
reworked INDEX format in `architecture.md`. Create this milestone's plan and
log.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `bin/docs` | Modify | `__version__` → `0.3.0-m3`; module docstring refreshed. New `Finding` frozen dataclass. New "Validation and query (M3)" section with stub signatures + docstrings for `_iter_doc_texts`, `_resolved_project`, `check_doc`, `check_tree`, `exit_code_for`, `query_docs`, `finding_to_json`, `doc_to_json`. `_cmd_check` / `_cmd_list` stub handlers. `check` / `list` subparsers in `_build_parser()`. `main()` dispatch extended. |
| `docs/cli.md` | Modify | `list --json` and `check --json` record schemas pinned as tables; `--json` added to the `docs check` usage; structural-breakage rule made explicit; "unknown extra fields" dropped from exit 1; `Updated` → 2026-05-22. |
| `docs/architecture.md` | Modify | INDEX renderer-format subspec reworked to the two-level `Project` → `Role` layout; `Updated` → 2026-05-22. |
| `docs/status.md` | Modify | M3 marked in flight; progress table + resume note updated; `Updated` → 2026-05-22. |
| `docs/m3-validation-and-query.md` | Create | Milestone task plan (ten phases). |
| `docs/m3-validation-and-query-log.md` | Create | This log. |
| `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Picked up the two new M3 docs and the spec `Updated` bumps; still the flat layout (the renderer rework lands in Phase 5). |

#### Actions taken

- Added the `check` and `list` subparsers directly (not via the `common` parent
  parser) — both verbs are read-only, so the `--dry-run` flag `common` carries
  does not apply. `check` takes a positional `[DIR]` plus `--root` / `--stale` /
  `--json`; `list` takes `--root` / `--status` / `--role` / `--project` /
  `--stale` / `--json`.
- Declared eight validation/query helpers with full docstrings; bodies raise
  `NotImplementedError("… — Phase N")` naming the phase that implements them.
- `_cmd_check` / `_cmd_list` raise `NotImplementedError` — Phase 6.
- Pinned both `--json` schemas in `cli.md` as the M3 stability contract.
- Reworked the `architecture.md` INDEX renderer-format subspec to describe the
  two-level grouping ahead of the Phase 5 implementation.

#### Issues / decisions

- **`check` needs a non-raising traversal.** `parse()` / `walk()` raise on the
  malformed docs `check` must report. M3 adds `_iter_doc_texts`, a lenient
  traversal shared by `check` and `list`. Recorded in the milestone Decisions.
- **No "unknown extra fields" warning.** `cli.md`'s exit-1 description listed
  one, but no registry of "known" extra fields exists and the convention treats
  extra fields as a feature. The phrase was removed; exit 1 is stale docs only.
- **`Finding` carries a `rule` id.** A stable machine-readable rule id per
  finding, emitted in `--json`, supports CI filtering and precise tests.

#### Exit criteria

- [x] `Finding` + 8 helper stubs + 2 `_cmd_*` stubs + `check`/`list` subparsers
      in `bin/docs`; `main()` dispatch extended.
- [x] `docs --help` lists all seven subcommands; `check` / `list` reachable.
- [x] `ruff check` / `ruff format --check` / `mypy` clean tree-wide.
- [x] `cli.md` JSON schemas pinned; `architecture.md` INDEX format reworked.
- [x] `docs/INDEX.md` and the dogfood snapshot regenerated in lockstep.
- [x] Ready for Phase 2 to write failing tests against the contract.

### Phase 2 — Write Tests (RED)

**Completed:** 2026-05-22

#### Objective
Express every M3 behavior — each `check` rule, each `list` filter, the JSON
schemas, the exit-code matrix, and the two-level INDEX layout — as a failing
test, before any implementation.

#### Files changed

| File | Action | Tests |
|---|---|---|
| `tests/test_check.py` | Create | 23 — `check_doc` per rule (clean, missing/empty field, malformed, bad vocab, bad date, status drift in/out of archive, broken/resolvable refs, stale boundary), `exit_code_for` (0/1/2), `check_tree` (clean/drift/invalid trees, sort order). |
| `tests/test_query.py` | Create | 8 — `query_docs` filters (status, role, project, project-less fallback, AND-combination, stale) and within-group Updated-descending sort. |
| `tests/test_cli_check.py` | Create | 9 — `--help`, exit-code matrix (0/1/2), `--json` array shape, grouped human output, dogfood `check docs/`. |
| `tests/test_cli_list.py` | Create | 9 — `--help`, table output, every filter, the `--json` record schema and field types. |
| `tests/test_index.py` | Modify | 5 renderer tests reworked for the two-level `## Project — … / ### Active — …` layout; 3 project-grouping tests added; `_doc` gained a `project` parameter. |

Total: 52 new M3 tests; 164 in the suite.

#### Actions taken
- `check_doc` unit tests use inline doc strings; the status-drift and
  broken-ref tests use `tmp_path` because those rules touch the filesystem.
- `check_doc` / `query_docs` are tested with an explicit `today` argument, so
  the stale-boundary assertions are deterministic regardless of the wall clock.
- CLI tests follow the M1/M2 idiom — a local `_run()` subprocess helper. The
  `check --stale` CLI test builds its tree with `date.today()`-relative dates,
  so it does not rot as the calendar advances.
- The `test_index.py` renderer tests were rewritten to the two-level layout
  now (RED until Phase 5), keeping the test suite the single description of
  desired behavior.

#### Issues / decisions
- **False-pass guard.** A stub's `NotImplementedError` exits the process with
  code 1. Exit-2 and exit-0 tests fail honestly against that. The one exit-1
  test (`check --stale` warnings-only) additionally asserts a real-output
  substring and `"NotImplementedError" not in` stderr, so a stub that happens
  to exit 1 cannot make it false-pass. Confirmed at Phase 4.
- **`--help` tests pass at the RED baseline.** Phase 1 declared the CLI
  surface, so `docs check --help` / `docs list --help` work — these two are
  contract tests, a legitimate pass.

#### Exit criteria
- [x] 164 tests collect without import or fixture-path errors.
- [x] Every M3 test fails with `NotImplementedError`, a wrong stub exit code,
      or (the reworked renderer tests) the un-reworked layout.
- [x] `ruff` / `mypy` clean tree-wide, including the new test files.
- [x] Ready for Phase 3 (fixtures) → Phase 4 (RED baseline).

### Phase 3 — Create Data/Fixtures

**Completed:** 2026-05-22

#### Objective
Build the fixture trees the Phase 2 tests reference, so the only cause of
failure at Phase 4 is missing implementation.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `tests/fixtures/trees/drift/` | Create | `.docs.toml` + 4 docs: `wrongly-archived.md` (archived status in the active tree), `archive/2026-01-01/wrongly-active.md` (active status in the archive subtree), plus `clean.md` and `archive/2026-01-01/properly-archived.md` as negative controls. |
| `tests/fixtures/trees/invalid/` | Create | `.docs.toml` + 7 docs, one per non-drift rule: missing `Status`, empty `Role`, unknown status, unknown role, unparseable `Updated`, a broken `Related:` ref, and a doc with no H1. |
| `tests/fixtures/trees/multi-project/` | Create | `.docs.toml` + 9 docs across projects `alpha` / `beta` / (root default), spanning every status and several roles, with varied `Updated:` dates, one `Related:` block, one extra field, a subdirectory, and an archived doc. Two `alpha` specs share a Status/Role group so the within-group sort is exercised. |

Existing `trees/minimal/` is reused for the clean-tree `check` test.

#### Issues / decisions
- **`invalid/` must only be reached by `check`.** `walk()` raises on its
  deliberately broken docs; only the M3 `check` tests (which use the lenient
  `_iter_doc_texts`) reference it. Verified no M1/M2 test walks it.
- `multi-project/` doubles as the `list` fixture and the data behind the
  INDEX two-level-grouping tests — one tree, several concerns.

#### Exit criteria
- [x] Every fixture path a Phase 2 test references exists.
- [x] `drift/` and `multi-project/` parse cleanly under `walk()`; `invalid/`
      raises (as designed — `check` reads it leniently).
- [x] Ready for Phase 4: run pytest and capture the RED baseline.

### Phase 4 — Run Tests (RED Baseline)

**Completed:** 2026-05-22

#### Objective
Confirm every M3 test fails for the right reason — missing implementation, not
misconfiguration. Log-only; no implementation. **The milestone pauses here for
this session by request; Phase 5 resumes implementation.**

#### Command + summary

```
.venv/bin/python -m pytest tests/ -q
=========================== 55 failed, 109 passed in ~2.4s ===========================
```

164 tests collected; no collection / import / fixture-path errors.

#### Failure attribution

- **`test_check.py` (23)** and **`test_query.py` (8)** — fail with
  `NotImplementedError` from the `check_doc` / `check_tree` / `exit_code_for` /
  `query_docs` stubs.
- **CLI verb tests (16 across `test_cli_check.py` and `test_cli_list.py`)** —
  the `_cmd_check` / `_cmd_list` stubs raise `NotImplementedError` → exit 1 →
  the exit-code and output assertions fail.
- **`test_index.py` (8)** — the 5 reworked renderer tests and the 3 new
  project-grouping tests fail because `render_index` still emits the flat
  `## Active — <Role>` layout. They go green when Phase 5 lands the renderer
  rework.

No failure traces to an import error, a fixture-path error, or a misconfigured
test.

#### The 109 baseline passes

- **107 — M1/M2's suite**, minus the 5 `test_index.py` renderer tests reworked
  in Phase 2. All green.
- **2 — the M3 `--help` tests** (`check` / `list`). They pass because Phase 1
  declared the CLI surface — contract tests, a legitimate pass.

The exit-1 test that could have *false*-passed against a stub exiting 1
(`check --stale` warnings-only) was confirmed to fail on its
`"NotImplementedError" not in` guard — no false pass.

#### Quality gates

```
.venv/bin/ruff check .          -> All checks passed!
.venv/bin/ruff format --check . -> 16 files already formatted
.venv/bin/mypy                  -> Success: no issues found in 16 source files
```

#### Exit criteria
- [x] All M3 failures attributable to missing implementation.
- [x] No false passes among the exit-code tests.
- [x] M1/M2's tests green except the 5 renderer tests reworked in Phase 2.
- [x] No code implemented beyond the Phase 1 contract stubs.
- [x] Ready for Phase 5: implement the helpers and the renderer rework.
