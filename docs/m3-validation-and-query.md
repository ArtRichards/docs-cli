# M3 — Validation and query (`check`, `list`)

Status: done
Role: milestone
Project: docs
Updated: 2026-05-22

Related:
- parent-of: m3-validation-and-query-log.md
- child-of: plan.md
- implements: charter.md
- pairs-with: convention.md
- pairs-with: cli.md
- pairs-with: architecture.md
- pairs-with: test-strategy.md

## Overview

- Milestone: M3
- Title: Validation and query (`check`, `list`)
- Surface: two new read-only CLI subcommands on the `docs` executable, plus a
  rework of the INDEX renderer.
- Status: COMPLETE (shipped 2026-05-22)

### Goal

M1 made the tree *readable*; M2 made it *writable*. M3 makes the convention
*enforceable and queryable*. `docs check` validates a tree and returns exit
codes a CI hook can branch on (0 clean / 1 warnings / 2 errors). `docs list`
gives a filterable query view with a JSON schema that is stable from this
milestone on. Alongside the two verbs, the INDEX renderer is regrouped from a
flat Role list into a two-level `Project` → `Role` layout, so a multi-project
tree navigates by project.

### Requirements

- `docs check [DIR] [--stale N] [--json]` reports every violation listed in
  [cli.md](cli.md): missing/empty required fields, out-of-vocabulary
  Status/Role, unparseable `Updated:`, structural breakage, status/location
  drift, broken `Related:` references, and — with `--stale N` — stale active
  docs. Exit 0 clean, 1 warnings only, 2 errors.
- `docs list [--status S] [--role R] [--project P] [--stale N] [--json]`
  filters the tree (filters AND-combined) and prints a table grouped by Status
  then Role, or a JSON array. The `--json` record schema is pinned in
  [cli.md](cli.md) and stable from M3 on. Exits 0.
- `check` and `list` are read-only — no `--dry-run`, no mutation.
- The INDEX renderer groups active docs by `Project` (docs-root project first,
  then alphabetical), then by `Role` within each project; `## Archived` stays a
  single flat trailing section.
- Both verbs cope with a malformed tree without crashing: `check` reports the
  breakage; `list` skips what it cannot parse and still exits 0.

### Deliverables

- [x] Two subcommands functional on `bin/docs`: `check`, `list`.
- [x] `Finding` model + shared validators; the lenient traversal
      `_iter_doc_texts` reused by both verbs.
- [x] INDEX renderer reworked to two-level `Project` → `Role` grouping.
- [x] `tests/test_check.py`, `tests/test_query.py`, `tests/test_cli_check.py`,
      `tests/test_cli_list.py`; `tests/test_index.py` updated for the new layout.
- [x] Fixture trees for validation (`drift/`, `invalid/`) and query
      (`multi-project/`).
- [x] Dogfood: `docs check docs/` returns exit 0 on this repo; `docs list
      --json` validates against the documented schema.
- [x] All quality gates green tree-wide: `ruff check .`, `ruff format --check
      .`, `mypy`, `pytest -q`.
- [x] `docs/status.md` and `docs/plan.md` updated; M3 → Complete.

## Current state analysis (snapshot at milestone kickoff, 2026-05-22)

_Captured before Phase 1; historical. Post-milestone state lives in the
Milestone-completion summary at the bottom of this file._

- **Existing code:** `bin/docs` shipped M1+M2 — parser, walker, renderer, five
  verbs, config loading, surgical metadata editors. `parse`,
  `parse_metadata_block`, `_metadata_line_span`, `walk`, `validate_status`,
  `validate_role`, `parse_date`, `load_config`, `find_root`, `render_index`,
  `_format_entry`, `atomic_write`, `_refresh_index` are all available and tested.
- **Existing tests:** 112 (M1+M2), all green at kickoff.
- **Reuse map:** `check` builds its per-doc validator on `parse_metadata_block`
  (lenient) plus `validate_status` / `validate_role` / `parse_date`; `list`
  reuses `parse`. Both reach docs through a new lenient traversal
  `_iter_doc_texts` rather than `walk()`.
- **Gap M1/M2 left:** `parse()` and `walk()` *raise* `MetadataError` /
  `VocabularyError` on a malformed doc — exactly the docs `check` must
  *report*. M3 adds a non-raising traversal so `check` (and `list`, which must
  still exit 0) can inspect a messy tree.
- **Renderer:** `render_index` groups by `Role` only. The plan.md open question
  on directory- / `Project`-grouped INDEX is resolved in M3 — see Decisions.

## TDD Implementation Plan

The ten phases follow the fixed methodology in [status.md](status.md). Phases
1–4 establish the contract, tests, fixtures, and RED baseline with **no verb
implementation**; phases 5–10 implement and ship. **All ten phases are
complete — see the Milestone-completion summary at the end of this file.**

### Phase 1: Define Contract

- **Objective:** Declare the M3 surface. No business logic.
- **Files:**
  - `bin/docs` — `Finding` dataclass; stub signatures + docstrings for
    `_iter_doc_texts`, `_resolved_project`, `check_doc`, `check_tree`,
    `exit_code_for`, `query_docs`, `finding_to_json`, `doc_to_json` (bodies
    raise `NotImplementedError`); `_cmd_check` / `_cmd_list` stub handlers;
    `check` and `list` subparsers in `_build_parser()`; `main()` dispatch
    extended; `__version__` → `0.3.0-m3`.
  - `docs/cli.md` — pin the `check --json` and `list --json` record schemas;
    add `--json` to the `check` usage line; drop the unimplementable "unknown
    extra fields" warning from the exit-1 description.
  - `docs/architecture.md` — INDEX renderer-format subspec reworked to the
    two-level `Project` → `Role` layout.
  - `docs/status.md` — M3 marked in flight.
  - `docs/m3-validation-and-query.md`, `docs/m3-validation-and-query-log.md` —
    created (this file and its log).
- **Exit:** `docs --help` lists seven subcommands; `check`/`list` parse their
  args then exit non-zero on the stub; `ruff` / `mypy` clean; `docs/INDEX.md`
  and the dogfood snapshot regenerated in lockstep (still the flat layout —
  the renderer rework lands in Phase 5).

### Phase 2: Write Tests (RED)

- **Objective:** Express every M3 behavior as a failing test.
- **Files:**
  - `tests/test_check.py` — unit tests for `check_doc` (one per validation
    rule), `check_tree` (aggregation + ordering), and `exit_code_for`.
  - `tests/test_query.py` — unit tests for `query_docs` filters and sort order.
  - `tests/test_cli_check.py` — exit-code matrix (0/1/2), `--json` array shape,
    grouped human output, dogfood `check docs/` → exit 0.
  - `tests/test_cli_list.py` — table output, every filter, `--json` schema and
    field types, exit 0.
  - `tests/test_index.py` — renderer tests reworked to expect the two-level
    `Project` → `Role` layout; RED until Phase 5.
- **Exit:** all tests collect without import / fixture-path errors; every M3
  test, and the reworked renderer tests, fail for the right reason.

### Phase 3: Create Data/Fixtures

- **Objective:** Build the fixture trees the Phase 2 tests reference.
- **Files:**
  - `tests/fixtures/trees/drift/` — status/location mismatches.
  - `tests/fixtures/trees/invalid/` — one doc per non-drift error rule.
  - `tests/fixtures/trees/multi-project/` — docs across multiple projects,
    statuses, and roles; for `list` filters and the INDEX grouping tests.
  - Reuse `minimal/`, `with-archive/`, `cross-refs/`, `nested/` for clean-tree
    cases.
- **Exit:** every fixture path a Phase 2 test references exists; the
  deliberately-broken trees are referenced only by M3 `check` tests.

### Phase 4: Run Tests (RED Baseline)

- **Objective:** Confirm every failure traces to missing implementation, not
  misconfiguration. Log-only; no implementation. **This session pauses here.**
- **Actions:** `.venv/bin/python -m pytest tests/` — capture full output.
- **Exit:** every M3 failure traces to `NotImplementedError`, a wrong stub exit
  code, or the un-reworked renderer; no `ImportError`, no fixture-path error;
  M1/M2's tests stay green except the `test_index.py` renderer tests
  intentionally rewritten in Phase 2.

### Phase 5: Update Base Interfaces

- **Objective:** Implement the shared pure helpers and the INDEX renderer rework.
- **Files:** `bin/docs` — `_iter_doc_texts`, `_resolved_project`, `check_doc`,
  `exit_code_for`; `render_index` / `_format_entry` reworked to the two-level
  `Project` → `Role` grouping.
- **Exit:** `test_check.py` per-doc rules green; `test_index.py` green.

### Phase 6: Implement Offline/Core Path

- **Objective:** `check_tree`, `query_docs`, and the two verb cores.
- **Files:** `bin/docs` — `check_tree`, `query_docs`, `_cmd_check`, `_cmd_list`
  (human output).
- **Exit:** `test_check.py`, `test_query.py`, and the human-output CLI tests green.

### Phase 7: Update Tool/Wrapper Layer

- **Objective:** Finalize the CLI — `--json` output for both verbs, exit-code
  mapping, error messages to stderr.
- **Files:** `bin/docs` — `finding_to_json`, `doc_to_json`, the `--json`
  branches of `_cmd_check` / `_cmd_list`.
- **Exit:** every CLI test green; exit codes match the [cli.md](cli.md) matrix.

### Phase 8: Run Tests (GREEN)

- **Objective:** Full suite passing; quality gates clean tree-wide.
- **Actions:** `pytest -q`; `ruff check .`; `ruff format --check .`; `mypy`.
- **Exit:** all green.

### Phase 9: Implement Online/Integration (dogfood pass)

- **Objective:** Exercise `check` and `list` against this repo's own `docs/`.
- **Actions:** `docs check docs/` → exit 0; `docs list` and `docs list --json`
  produce correct output; reconcile the INDEX two-level snapshot.
- **Exit:** `check docs/` returns 0; `list --json` validates against the schema.

### Phase 10: Quality, Docs, Refactor

- **Objective:** Close out M3.
- **Actions:** full quality gate; update [status.md](status.md) (M3 → Complete,
  M4 → next) and [plan.md](plan.md) (resolve the INDEX-grouping open question);
  append milestone-completion summaries here and in the log.
- **Exit:** quality gate green; docs updated; ready to start M4.

## Phase Checklist

- [x] Phase 1: Define Contract
- [x] Phase 2: Write Tests (RED)
- [x] Phase 3: Create Data/Fixtures
- [x] Phase 4: Run Tests (RED Baseline)
- [x] Phase 5: Update Base Interfaces
- [x] Phase 6: Implement Offline/Core Path
- [x] Phase 7: Update Tool/Wrapper Layer
- [x] Phase 8: Run Tests (GREEN)
- [x] Phase 9: Implement Online/Integration (dogfood pass)
- [x] Phase 10: Quality, Docs, Refactor

## Decisions

Key choices applying to this milestone (broader decisions live in `vocab-adr.md`
and `dual-status-adr.md`):

- **`check` cannot reuse `walk()` / `parse()`.** Both raise `MetadataError` /
  `VocabularyError` on exactly the docs `check` exists to report. M3 adds
  `_iter_doc_texts`, a lenient traversal that reads raw text and applies
  `walk()`'s skip rules without parsing. `check_doc` builds on
  `parse_metadata_block` (which enforces no required fields / vocab / date) and
  wraps `validate_status` / `validate_role` / `parse_date` so a rejection
  becomes a `Finding` instead of an exception. `list` shares the lenient
  traversal so it can still exit 0 on a messy tree.
- **INDEX grouped by `Project` then `Role`.** The [plan.md](plan.md) open
  question (group the INDEX by directory or `Project`) is resolved: by
  `Project`. It is metadata-driven — consistent with the convention's
  deliberate replacement of role-bucket subdirectories with `Role:` metadata —
  and parallel to `docs list --project`. Directory grouping was rejected for
  cutting against that convention. Layout: `## Project — <name>` (docs-root
  project first, then alphabetical) → `### Active — <Role>`; `## Archived`
  stays a single flat trailing section.
- **No "unknown extra fields" warning.** cli.md's exit-1 line mentioned one,
  but the convention defines no registry of "known" extra fields and treats
  extra `Label: value` lines as a designed feature. There is nothing
  implementable to warn about; Phase 1 removed the phrase from cli.md. Exit 1
  is stale docs only. A possible future opt-in extra-field allowlist is scoped
  as an open question in [plan.md](plan.md).
- **`Finding` carries a stable `rule` id.** Beyond `severity` and `message`,
  each finding has a machine-readable `rule` (`missing-field`, `bad-vocab`,
  `bad-date`, `malformed`, `status-drift`, `broken-ref`, `stale`). It is
  emitted in `--json` so CI hooks can filter on it, and it keeps the exit-code
  tests precise.
- **`check` / `list` take no `--dry-run`.** They are read-only, so they do not
  use the `common` parent parser (which carries `--dry-run`). `check` takes a
  positional `[DIR]` like `index`; `list` is `--root`-only, matching cli.md.
- **`bin/docs` stays a single file.** [definition-of-ready.md](definition-of-ready.md)'s
  risk log and M2's Decisions both flagged a possible package split "at M3".
  After the Phase 1 contract `bin/docs` is ~1,520 lines — large, but sectioned
  with header comments and clean under `ruff` / `mypy`. M3 adds two verbs and a
  renderer rework within that structure; the file is not "unworkable", so the
  split stays deferred — revisit at M4/M5 or v1.1.

## Testing / Quality Gate

Commands run at Phase 4 (RED baseline), Phase 8 (GREEN), and Phase 10:

```
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
./bin/docs check docs/        # dogfood — exit 0 once M3 lands
```

Expected at Phase 4: M1/M2 tests green except the `test_index.py` renderer
tests intentionally rewritten for the two-level layout; every new M3 test RED
with `NotImplementedError` or a wrong stub exit code. Expected at Phase 8/10:
all commands green; `docs check docs/` exits 0.

## Success Criteria

M3 is complete when:

- [x] All Phase Checklist items are checked.
- [x] `docs check` and `docs list` work per [cli.md](cli.md), including
      `--json` and the documented exit codes.
- [x] `docs check docs/` returns exit 0 on this repo's own docs tree.
- [x] `docs list --json` output validates against the schema pinned in cli.md.
- [x] The INDEX renders the two-level `Project` → `Role` layout.
- [x] All Deliverables above are checked off.
- [x] [status.md](status.md) reflects M3 → Complete and [plan.md](plan.md)'s
      INDEX-grouping open question is resolved.
- [x] [m3-validation-and-query-log.md](m3-validation-and-query-log.md) contains
      a milestone-completion summary.

## Milestone-completion summary

**Shipped 2026-05-22**, all ten TDD phases complete. Full suite green —
164 passed; `ruff check` / `ruff format --check` / `mypy` clean tree-wide;
`docs check docs/` exits 0.

### Code surface added to `bin/docs`

- **`docs check [DIR] [--root R] [--stale N] [--json]`** — validates a tree
  and returns CI-usable exit codes (0 clean / 1 warnings only / 2 errors).
  Reports seven rules: `missing-field`, `bad-vocab`, `bad-date`, `malformed`,
  `status-drift`, `broken-ref`, and (with `--stale N`) `stale`.
- **`docs list [--root R] [--status S] [--role R] [--project P] [--stale N]
  [--json]`** — filters the tree (filters AND-combined), prints a table
  grouped by Status then Role, or a JSON array; always exits 0.
- **`Finding`** frozen dataclass — `path`, `severity`, `rule`, `message`.
- **`_iter_doc_texts`** — lenient traversal: mirrors `walk()`'s skip rules
  but yields raw `(path, text)` without parsing, so `check` / `list` cope
  with docs `parse()` would reject.
- **`check_doc` / `check_tree` / `exit_code_for`** — per-doc validation, tree
  aggregation, and the exit-code mapping.
- **`query_docs`** — lenient parse + AND-combined filtering + Status/Role/
  Updated-descending sort.
- **`_resolved_project`** — `Doc.project` or the config default, never None.
- **`finding_to_json` / `doc_to_json`** — the `--json` record builders for
  the schemas pinned in [cli.md](cli.md).
- **`render_index`** — reworked to the two-level `## Project — <name>` /
  `### Active — <Role>` layout; `_format_entry` and the marker-splice logic
  unchanged.

### Decisions realised

All six milestone Decisions held through implementation. One spec gap was
accepted in Phase 5: the `malformed` rule covers a **missing H1 only** —
`parse_metadata_block` ends the metadata block at the first non-label line
rather than raising, so a malformed in-block line is not separately
detectable. No fixture exercises it; recorded in the log and in
[status.md](status.md)'s durable gotchas.

### Verification

`docs check docs/` → exit 0; `docs list --root docs/ --json` → 16 records
matching the pinned schema; `docs check tests/fixtures/trees/invalid --json`
→ exit 2 with five rules reported. `docs/INDEX.md` and the frozen snapshot
`tests/fixtures/expected/docs-INDEX.md` were regenerated in lockstep with the
renderer rework.
