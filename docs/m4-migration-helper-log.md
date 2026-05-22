# M4 — Implementation Log

Status: active
Role: log
Project: docs
Updated: 2026-05-22

Related:
- child-of: m4-migration-helper.md
- pairs-with: status.md

## Implementation metadata

- Project: docs
- Milestone: M4 — Migration helper (`docs migrate`)
- Started: 2026-05-22
- Progress: Not started — milestone activated, task plan and this log
  authored, and all four milestone-setup open questions resolved
  (operator-confirmed 2026-05-22, see below). Phase 1 (Define Contract) is the
  next action.

(Note: doc-lifecycle status is in the front-matter `Status:` field above. This
section tracks milestone progress, which is distinct.)

## Milestone-setup open questions — resolved (2026-05-22)

Four questions were surfaced while authoring the task plan; all four were
triaged against [plan.md](plan.md) and the M1–M3 precedent and operator-
confirmed. Each is recorded as a Decision in
[m4-migration-helper.md](m4-migration-helper.md):

1. **Dry-run by default, `--apply` to write** — confirmed. plan.md's M4
   section mandates "produces a dry-run report by default; `--apply` performs
   the edits".
2. **Positional `<dir>`, no `--root`** — confirmed. plan.md notates the verb
   as `docs migrate <dir>`; a foreign tree has no `.docs.toml` for `--root`
   to resolve.
3. **Normalise archive-style subdirs only; active-tree directory layout is
   left untouched (metadata only)** — confirmed. Active-tree role-bucket
   flattening is explicitly out of M4 scope; the milestone doc's Deliverables
   and Success Criteria make this explicit.
4. **No new `plan.md` open question for M4** — confirmed. Phase-1 housekeeping
   drops `docs migrate` from cli.md's "not in v1" list; the parked extra-field
   allowlist question in plan.md is left alone.

## Summary

Add the migration verb — `docs migrate` — which adopts a non-conforming
directory into the convention. It walks a foreign tree, infers the required
metadata (`Status`, `Role`, `Project`, `Updated`) per file from filename
patterns, in-file signals, and mtime, and produces a migration plan with an
explicit decision and confidence for every file and every ambiguity flagged.
Dry-run by default; `--apply` inserts the metadata blocks atomically and
normalises archive-style subdirectories. The plan is the contract surface an
agent consumes to resolve ambiguities before applying.

## TDD Phase Progress

| Phase | Status | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-05-22 | `FileMigration` / `MigrationPlan` models + inference/plan/apply helper stubs + `_cmd_migrate` stub + `migrate` subparser in `bin/docs`; `cli.md` migrate section + `--json` schema; `architecture.md` migrate module spec; M4 plan + log created. |
| 2. Write Tests (RED) | Complete | 2026-05-22 | `tests/test_migrate.py` (40 inference + planning units) and `tests/test_cli_migrate.py` (9 CLI dry-run / `--apply` / `--json` tests). |
| 3. Create Data/Fixtures | Not started | — | `tests/fixtures/trees/foreign/` — non-conforming docs; archive-style subdir; refuse-guard tree. |
| 4. Run Tests (RED Baseline) | Not started | — | `pytest tests/` — capture the RED baseline. **Session pauses here.** |
| 5. Update Base Interfaces | Not started | — | `infer_role` / `infer_project` / `infer_status` / `infer_updated` / `detect_archive_layout` / `insert_metadata_block`. |
| 6. Implement Offline/Core Path | Not started | — | `plan_migration` + `_cmd_migrate` dry-run human output. |
| 7. Update Tool/Wrapper Layer | Not started | — | `apply_migration`, `migration_to_json`, the `--apply` / `--json` branches; refuse-on-`.docs.toml` guard. |
| 8. Run Tests (GREEN) | Not started | — | Full suite + quality gates green tree-wide. |
| 9. Implement Online/Integration | Not started | — | Dogfood: `migrate` dry-run plan + `--apply` on a copy → `docs check` clean. |
| 10. Quality, Docs, Refactor | Not started | — | `status.md` / `plan.md` / milestone doc + this log updated; M4 → Complete. |

## Current State Analysis (snapshot at milestone kickoff, 2026-05-22)

_Captured before Phase 1; historical._

- **Codebase:** `bin/docs` shipped at M1+M2+M3 (~1,790 lines) — parser,
  walker, renderer, seven verbs (`index`, `new`, `archive`, `mv`, `touch`,
  `check`, `list`), config loading, surgical metadata editors, validation,
  and query. 164 passing tests across 14 files.
- **Reuse available:** `_iter_doc_texts` (lenient traversal), `parse` /
  `parse_metadata_block` / `_metadata_line_span` (block detection),
  `scaffold_doc` / `set_metadata_field` (metadata writing), `_slug_to_title`
  (title inference), `atomic_write` (atomic writes), `_archive_one`'s
  edit-then-move pattern, `check_doc` (the post-migration acceptance oracle),
  and the `_build_parser` / `main` subcommand harness — all tested.
- **Gap:** the tool can only write metadata into a doc that already conforms.
  M4 must *insert* a metadata block between an existing H1 and body (or
  synthesise the H1) and *infer* the values the convention requires that a
  foreign doc does not carry. Neither inference nor block-insertion exists.
- **Fixture reserved:** [test-strategy.md](test-strategy.md) already lists
  `tests/fixtures/trees/foreign/` "for `docs migrate` tests (M4)"; Phase 3
  builds it.

## Files to Create / Modify

| File | Action | Phase | Notes |
|---|---|---|---|
| `bin/docs` | Modify | 1, 5, 6, 7 | M4 contract stubs (P1); inference + block-insertion helpers (P5); `plan_migration` + verb core (P6); `--apply` / `--json` + CLI wiring (P7). |
| `docs/m4-migration-helper.md` | Create | 1 | This milestone's task plan. |
| `docs/m4-migration-helper-log.md` | Create | 1 | This log. |
| `docs/cli.md` | Modify | 1 | `docs migrate` subcommand section + `--json` plan schema pinned; `migrate` removed from "not in v1"; `Updated` bumped. |
| `docs/architecture.md` | Modify | 1 | `migrate` module bullet fleshed out with inference + plan/apply responsibilities; `Updated` bumped. |
| `docs/status.md` | Modify | 1, …, 10 | M4 phase tracking; M4 → Complete at Phase 10. |
| `docs/plan.md` | Not modified | — | M4 opens no `plan.md` open question (operator-confirmed 2026-05-22); the parked extra-field allowlist question is left as-is. `docs migrate` is dropped from cli.md's "not in v1" list at Phase 1, not plan.md. |
| `docs/INDEX.md` | Regenerate | 1, 10 | Picks up the two new M4 docs (P1); description bumps (P10). |
| `tests/fixtures/expected/docs-INDEX.md` | Modify | 1, 10 | Re-synced with `docs/INDEX.md` in lockstep. |
| `tests/test_migrate.py` | Create | 2 | Inference + `insert_metadata_block` + `plan_migration` unit tests. |
| `tests/test_cli_migrate.py` | Create | 2 | `docs migrate` CLI tests (dry-run / `--apply` / `--json` / guards). |
| `tests/fixtures/trees/foreign/` | Create | 3 | Non-conforming docs; archive-style subdir; project-prefix case. |

## Phase logs

_Phase logs are appended here as each phase completes, following the M1–M3
format: Objective, Files changed (table), Actions taken, Issues / decisions,
Exit criteria._

### Phase 1 — Define Contract

**Completed:** 2026-05-22

#### Objective

Declare the full M4 surface in `bin/docs` — the `FileMigration` /
`MigrationPlan` models, the inference / plan / apply helper signatures, the
`_cmd_migrate` handler, the `migrate` subparser — with no business logic. Pin
the `--json` plan schema in `cli.md` and the `migrate` module spec in
`architecture.md`.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `bin/docs` | Modify | `__version__` → `0.4.0-m4`; module docstring refreshed; `Sequence` added to the `collections.abc` import. New `FileMigration` / `MigrationPlan` frozen dataclasses. New "Migration (M4)" section with stub signatures + docstrings for `infer_role`, `infer_project`, `infer_status`, `infer_updated`, `detect_archive_layout`, `insert_metadata_block`, `plan_migration`, `apply_migration`, `migration_to_json`. `_cmd_migrate` stub handler. `migrate` subparser in `_build_parser()`. `main()` dispatch + docstring extended. |
| `docs/cli.md` | Modify | `docs migrate` subcommand section added (usage, inference rules, dry-run / `--apply` semantics, refuse-on-`.docs.toml` guard, exit codes); `--json` plan record schema pinned as a table; `migrate` dropped from "What's deliberately not in v1"; `m4-migration-helper.md` added to `Related:`. |
| `docs/architecture.md` | Modify | One-line `migrate` bullet replaced with the inference + plan/apply responsibilities; new `migrate` module subsection paralleling `index`. |
| `docs/status.md` | Modify | M4 in-flight paragraph refreshed — "phases 1-4 underway". |
| `docs/m4-migration-helper-log.md` | Modify | Phase 1 row → Complete; this log entry. |
| `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Re-synced in lockstep after the spec edits. |

#### Actions taken

- Added the `migrate` subparser directly (not via the `common` parent parser):
  `migrate` is dry-run by default and takes `--apply` to opt *in* to writing —
  the inverse of `common`'s `--dry-run`. It takes a positional `dir`, plus
  `--apply` / `--json` / `--quiet` / `--date`; no `--root` (a foreign tree has
  no `.docs.toml` for an up-walk to resolve).
- Declared nine migration helpers with full docstrings; bodies raise
  `NotImplementedError("… — Phase N")` naming the phase that implements them
  (inference + `insert_metadata_block` → Phase 5; `plan_migration` → Phase 6;
  `apply_migration` / `migration_to_json` → Phase 7).
- `_cmd_migrate` raises `NotImplementedError` — Phase 6.
- Pinned the `--json` plan schema in `cli.md` as the M4 stability contract.

#### Issues / decisions

- **Dataclass field names reconciled with the `--json` keys (resolved Q1).**
  The plan's draft `has_h1` / `had_metadata` are the inverses of the pinned
  JSON keys `synthesized_h1` / `reconciled_metadata`. The `synthesized_h1` /
  `reconciled_metadata` orientation was chosen and used consistently in both
  the `FileMigration` dataclass and the JSON schema, so the mapping is a
  straight field-to-key copy.
- **`--date` flag added to `migrate` (resolved Q3).** A single optional
  `--date YYYY-MM-DD` per run, defaulting to today, keeps the plan
  deterministic — parallel to `docs archive --date`.
- **`FileMigration` enforces the confidence/ambiguities invariant.** Its
  `__post_init__` rejects `confidence` outside `{high, low}` and requires
  `ambiguities` non-empty iff `confidence == "low"` — the model cannot carry
  an inconsistent decision.
- **`architecture.md` had no `check` / `list` subsections.** The plan said to
  add a `migrate` subsection "paralleling check/list", but M3 never added
  those — `architecture.md` documents `model` / `walker` / `index` / `cli`.
  The new `migrate` subsection parallels the existing `index` subsection's
  style instead.

#### Exit criteria

- [x] `FileMigration` / `MigrationPlan` models + 9 helper stubs + `_cmd_migrate`
      stub + `migrate` subparser in `bin/docs`; `main()` dispatch extended.
- [x] `docs --help` lists all eight subcommands; `migrate` parses its args then
      exits non-zero from the stub.
- [x] `ruff check` / `ruff format --check` / `mypy` clean tree-wide.
- [x] `cli.md` `--json` plan schema pinned; `architecture.md` `migrate` spec
      added; `migrate` dropped from cli.md's "not in v1".
- [x] `docs/INDEX.md` and the dogfood snapshot regenerated in lockstep.
- [x] Ready for Phase 2 to write failing tests against the contract.

### Phase 2 — Write Tests (RED)

**Completed:** 2026-05-22

#### Objective

Express every M4 behaviour — each inference helper, `insert_metadata_block`,
`plan_migration`, and the `migrate` CLI surface — as a failing test before any
implementation.

#### Files changed

| File | Action | Tests |
|---|---|---|
| `tests/test_migrate.py` | Create | 40 — `infer_role` per suffix (spec/plan/adr→decision/log/status/charter/guide/runbook/reference), `notes` fallback, in-file override, always-built-in; `infer_project` common-prefix / dir-name fallback / single-file; `infer_status` in-file-wins / archive default / active default / out-of-vocab rejection / always-built-in; `infer_updated` in-file / mtime fallback / malformed fallback; `detect_archive_layout` per archive style + already-conformant no-move + active-tree; `insert_metadata_block` H1-present, no-H1 synthesis, reconcile-not-duplicate, trailing-newline, parse round-trip, `check_doc`-clean; `plan_migration` shape, per-file count, path order, confidence/ambiguities consistency, no-H1 flag, archive-move presence/absence. |
| `tests/test_cli_migrate.py` | Create | 9 — `--help`, dry-run-is-default-writes-nothing, dry-run-reports-every-file, the pinned `--json` schema, `--apply` writes blocks, `--apply` normalises archives, `--apply` leaves the active layout unchanged, the refuse-on-`.docs.toml` guard, applied-tree-passes-`check`. |

Total: 49 new M4 tests; 213 in the suite.

#### Actions taken

- Unit tests import `from docs import …` — `conftest.py` registers `bin/docs`
  as the `docs` module, so the natural import works.
- `plan_migration` and the CLI tests run against the `foreign/` fixture tree
  (built in Phase 3); the pure-inference tests use inline data.
- CLI tests follow the M1-M3 idiom — a local `_run()` subprocess helper with a
  `cwd` parameter; `--apply` tests `shutil.copytree` the fixture into
  `tmp_path` so the committed fixtures are never mutated, and snapshot the tree
  before/after to assert dry-run writes nothing.

#### Issues / decisions

- **False-pass guard.** A stub's `NotImplementedError` exits the process with
  code 1. The exit-0 `migrate` tests fail honestly against that; the
  refuse-guard test asserts a non-zero exit *and* a real-message substring.
  Every non-`--help` CLI test additionally asserts
  `"NotImplementedError" not in (stdout + stderr)`, so a stub cannot
  false-pass.
- **`migrate --help` passes at the RED baseline.** Phase 1 declared the CLI
  surface, so `docs migrate --help` works — a legitimate contract-test pass.
- **`insert_metadata_block` body-verbatim is asserted via `parse`.** The
  block-insertion tests round-trip the result through `parse` /
  `parse_metadata_block` and run `check_doc`, so the implementation has a
  precise, convention-anchored target rather than a brittle string match.

#### Exit criteria

- [x] Both new test files collect with no `ImportError`.
- [x] Every new M4 test fails for the right reason — `NotImplementedError`
      from a stub (or, once the fixture lands, a wrong stub exit code caught by
      the false-pass guard).
- [x] `migrate --help` passes (the contract test).
- [x] `ruff` / `mypy` clean tree-wide.
- [x] Ready for Phase 3 (fixtures) → Phase 4 (RED baseline).

## Milestone-completion summary

_Filled in at Phase 10 when M4 ships._
