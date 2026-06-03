# M4 — Implementation Log

Lifecycle: archived
Role: log
Project: docs
Updated: 2026-05-22

Related:
- child-of: archive/2026-05-22/m4-migration-helper.md
- pairs-with: status.md

## Implementation metadata

- Project: docs
- Milestone: M4 — Migration helper (`docs migrate`)
- Started: 2026-05-22
- Completed: 2026-05-22
- Progress: All ten TDD phases complete (2026-05-22). Phases 1-4 (contract, RED
  tests, the `foreign/` fixture tree, RED baseline) landed on `m4/phases-1-4`;
  phases 5-10 (implement + ship) landed on `m4/phases-5-10`. A fresh-eyes
  branch review of phases 5-10 added the extra-metadata-preservation and
  archive-collision behaviours (see the "Branch review" section below). Full
  suite: 236 passed, 0 failed; `ruff` / `mypy` clean tree-wide. All
  milestone-setup and task-plan questions resolved (operator-confirmed
  2026-05-22). M4 is complete.

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
| 2. Write Tests (RED) | Complete | 2026-05-22 | `tests/test_migrate.py` (inference + planning units) and `tests/test_cli_migrate.py` (CLI dry-run / `--apply` / `--json` tests); a post-review follow-up strengthened coverage to 46 + 9 = 55 M4 tests total. |
| 3. Create Data/Fixtures | Complete | 2026-05-22 | `tests/fixtures/trees/foreign/` — 9 non-conforming docs incl. an archive-style subdir and a benign nested subdir; refuse-guard reuses `minimal/`. |
| 4. Run Tests (RED Baseline) | Complete | 2026-05-22 | `pytest tests/` — 48 failed, 165 passed at the baseline snapshot; a post-review follow-up commit added 6 tests, moving the baseline to 54 failed / 165 passed (219 collected) before Phase 5. Every M4 failure is `NotImplementedError` from a stub. |
| 5. Update Base Interfaces | Complete | 2026-05-22 | `infer_role` / `infer_project` / `infer_status` / `infer_updated` / `detect_archive_layout` / `insert_metadata_block` implemented; 30 inference + block-insertion units green. |
| 6. Implement Offline/Core Path | Complete | 2026-05-22 | `plan_migration` + `_in_archive_subdir` + `_cmd_migrate` dry-run human output (+ refuse-guard); all 14 plan-migration units and the dry-run CLI tests green. |
| 7. Update Tool/Wrapper Layer | Complete | 2026-05-22 | `apply_migration` + `migration_to_json` implemented; the `--apply` / `--json` `_cmd_migrate` branches were wired at Phase 6 and now resolve; all 9 `test_cli_migrate.py` tests green. |
| 8. Run Tests (GREEN) | Complete | 2026-05-22 | `pytest tests/` — 219 passed, 0 failed; `ruff check` / `ruff format --check` / `mypy` all green tree-wide. |
| 9. Implement Online/Integration | Complete | 2026-05-22 | Dogfood: `migrate` dry-run on `foreign/` (exit 0, 9 files, all ambiguities flagged); `--json` 10-key schema verified; `--apply` on a copy → `docs check` exit 0, `docs index` clean; `docs check docs/` exit 0. |
| 10. Quality, Docs, Refactor | Complete | 2026-05-22 | Full quality gate green; `status.md` / milestone doc + this log updated; M4 → Complete, M5 → next; `INDEX.md` + snapshot regenerated; single-file split deferred to v1.1. |

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
| `tests/test_migrate.py` | Create | 46 — `infer_role` per suffix (spec/plan/adr→decision/log/status/charter/guide/runbook/reference), `notes` fallback, in-file override, always-built-in; `infer_project` common-prefix / dir-name fallback / single-file; `infer_status` in-file-wins / archive default / active default / out-of-vocab rejection / always-built-in; `infer_updated` in-file / mtime fallback / malformed fallback / non-default date_format; `detect_archive_layout` per archive style + already-conformant no-move + active-tree; `insert_metadata_block` H1-present, no-H1 synthesis, reconcile-not-duplicate, trailing-newline, parse round-trip, `check_doc`-clean; `plan_migration` shape, per-file count, path order, confidence/ambiguities consistency, the pinned high/low fixture files, inferred values, reconciled-metadata, no-H1 flag, archive-move presence/absence. |
| `tests/test_cli_migrate.py` | Create | 9 — `--help`, dry-run-is-default-writes-nothing, dry-run-reports-every-file, the pinned `--json` schema, `--apply` writes blocks, `--apply` normalises archives, `--apply` leaves the active layout unchanged, the refuse-on-`.docs.toml` guard, applied-tree-passes-`check`. |

Total: 55 new M4 tests (46 + 9); 219 in the suite. (A post-Phase-4 review
follow-up strengthened the initial 49 to 55.)

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

### Phase 3 — Create Data/Fixtures

**Completed:** 2026-05-22

#### Objective

Build the `foreign/` fixture tree the Phase 2 tests reference, so the only
cause of failure at Phase 4 is missing implementation.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `tests/fixtures/trees/foreign/` | Create | A non-conforming foreign tree — **no `.docs.toml`**. Nine `.md` files of genuine prose, every basename sharing the `proj-` prefix (so `infer_project` yields `proj`): `proj-auth-spec.md` (`-spec`, no metadata block), `proj-release-plan.md` (`-plan`), `proj-db-adr.md` (`-adr` → decision), `proj-deploy-log.md` (`-log`), `proj-overview.md` (no inferable suffix → `notes` fallback), `proj-no-h1.md` (no H1 — first line is body), `proj-has-metadata.md` (partial `Status:`/`Updated:`-shaped lines under the H1, `Status: wip` out-of-vocab — to reconcile), `archived/proj-old-decision.md` (an archive-style subdir → `detect_archive_layout` + `Status: archived`), and `topics/proj-deep-notes.md` (a benign nested non-archive subdir, exercising recurse-and-migrate-in-place per resolved Q6). |

The refuse-on-`.docs.toml` guard test reuses the existing `minimal/` fixture
(it carries a `.docs.toml`) — no new fixture needed.

#### Issues / decisions

- **`foreign/` must stay non-conforming.** `docs check tests/fixtures/trees/
  foreign` exits 2 with `missing-field` / `malformed` / `bad-vocab` violations
  across all nine files — that is the point of the fixture. No M1-M3 test
  walks it, so its broken docs harm nothing.
- **One shared `proj-` prefix.** Every basename — nested file included —
  starts `proj-`, so `infer_project`'s longest-common-prefix rule trims to
  `proj` and the project-inference test has a deterministic target.

#### Exit criteria

- [x] Every fixture path a Phase 2 test references exists.
- [x] `docs check tests/fixtures/trees/foreign` reports violations (exit 2).
- [x] `infer_project` over the basenames would yield `proj`.
- [x] Ready for Phase 4: run pytest and capture the RED baseline.

### Phase 4 — Run Tests (RED Baseline)

**Completed:** 2026-05-22

#### Objective

Confirm every M4 test fails for the right reason — missing implementation, not
misconfiguration. Log-only; no implementation. **The milestone pauses here for
this session by request; Phase 5 resumes implementation.**

#### Command + summary

```
.venv/bin/python -m pytest tests/ -q
=========================== 48 failed, 165 passed in ~3.4s ===========================
```

213 tests collected at the baseline snapshot; no collection / import /
fixture-path errors.

**Post-Phase-4 follow-up:** a review of the Phase 1-4 work strengthened the
plan-level test coverage with 6 additional `test_migrate.py` units (committed
on `m4/phases-1-4`), moving the RED baseline to **54 failed / 165 passed (219
collected)**. That is the baseline Phase 5 resumed from; the failure
attribution below is the original 48-failure snapshot.

#### Failure attribution

Every one of the 48 baseline failures traces to a `NotImplementedError` raised
by a Phase-1 stub (the 6 added units distribute across `infer_*` /
`insert_metadata_block` / `plan_migration` the same way):

| Stub | Failures | Implements in |
|---|---|---|
| `infer_role` | 12 | Phase 5 |
| `infer_status` | 5 | Phase 5 |
| `infer_updated` | 3 | Phase 5 |
| `infer_project` | 3 | Phase 5 |
| `detect_archive_layout` | 4 | Phase 5 |
| `insert_metadata_block` | 6 | Phase 5 |
| `plan_migration` | 7 | Phase 6 |
| `_cmd_migrate` | 8 | Phase 6 |

The 8 `_cmd_migrate` failures are the CLI tests: the stub raises
`NotImplementedError`, the process exits 1, and the exit-code / output
assertions fail honestly — the `"NotImplementedError" not in (stdout +
stderr)` false-pass guard fires on each, so no stub can accidentally satisfy
an assertion (including the refuse-guard test, which asserts a non-zero exit).

No failure traces to an `ImportError`, a fixture-path error, or a misconfigured
test. M1/M2/M3's 164 tests stay green; `migrate --help` passes — the
contract-test pass, total 165 passed.

#### Quality gates

```
.venv/bin/ruff check .          → All checks passed!
.venv/bin/ruff format --check . → 18 files already formatted
.venv/bin/mypy                  → Success: no issues found in 18 source files
```

#### Exit criteria

- [x] M1/M2/M3's 164 tests stay green.
- [x] Every new M4 test fails for the right reason — `NotImplementedError`
      from a stub, verified by the false-pass guard.
- [x] No `ImportError`, no fixture-path error.
- [x] `migrate --help` passes.
- [x] `ruff` / `mypy` clean tree-wide.
- [x] RED baseline captured. **Session pauses here — Phase 5 resumes
      implementation.**

### Phase 5 — Update Base Interfaces

**Completed:** 2026-05-22

#### Objective

Implement the five pure inference helpers (`infer_role`, `infer_project`,
`infer_status`, `infer_updated`, `detect_archive_layout`) and the
block-insertion helper `insert_metadata_block` — the base layer
`plan_migration` and `apply_migration` build on.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `bin/docs` | Modify | Added module-level `_ROLE_SUFFIXES` (filename token → built-in role) and `_ARCHIVE_SUBDIR_NAMES`. Filled in the six Phase-5 helper bodies. |

#### Actions taken

- `infer_role`: in-file `Role:` carrying a built-in role wins; else the
  filename's trailing token (split on `[-_]`, `.md` dropped) maps via
  `_ROLE_SUFFIXES`; else `("notes", False)`.
- `infer_project`: `os.path.commonprefix` of the stems, trimmed to the last
  `-`/`_`; the trimmed prefix is used only when ≥ 2 chars, else `dir_name`.
- `infer_status`: in-file built-in `Status:` wins; else `archived` (confident)
  when in-archive, `active` (best-effort) otherwise.
- `infer_updated`: in-file `Updated:` parsed via `parse_date` (reused for
  consistency, honours `date_format`); on `MetadataError` or no line, falls
  back to `date.fromtimestamp(mtime)`.
- `detect_archive_layout`: validates the dated archive segment against a fixed
  ISO `%Y-%m-%d` (resolved Q2) and always emits `archive/<ISO-date>/`. A
  conformant `archive/<ISO-date>/<file>` returns `None`; `archived/`,
  `project-history/`, a bare `archive/file.md`, and a non-date
  `archive/<seg>/file.md` are all normalised.
- `insert_metadata_block`: parses the block leniently — when an H1 exists, the
  *parsed* old title is re-emitted (the `title` kwarg is only for the
  synthesised-H1 case); the canonical block follows `scaffold_doc`'s field
  order with `Project:` always written; pre-existing metadata lines are
  discarded (`parse_metadata_block` already excludes them from the body, so no
  duplication); the result's trailing newline mirrors the original text's.

#### Issues / decisions

- `infer_updated` reuses `parse_date` rather than a bare `strptime` so the
  one date parser stays the single source of truth; it still honours the
  `date_format` parameter, verified by
  `test_infer_updated_honours_a_non_default_date_format`.

#### Exit criteria

- [x] All 30 inference + `insert_metadata_block` unit tests green.
- [x] `plan_migration` tests still RED (Phase 6).
- [x] `ruff check` / `ruff format --check` / `mypy` clean tree-wide.

### Phase 6 — Implement Offline/Core Path

**Completed:** 2026-05-22

#### Objective

Implement `plan_migration` — assemble a `FileMigration` per file, set
confidence, flag ambiguities, plan archive moves — and the `_cmd_migrate`
dry-run path (directory-not-found guard, refuse-on-`.docs.toml` guard, `--date`
validation, human plan output).

#### Files changed

| File | Action | Notes |
|---|---|---|
| `bin/docs` | Modify | Added `_in_archive_subdir`; implemented `plan_migration` and `_print_migration_plan`; implemented `_cmd_migrate` (dry-run + guards; `--apply`/`--json` branches call the Phase-7 helpers). |
| `docs/cli.md` | Modify | Role-inference rule note: a trailing token that is itself a built-in role resolves to that role directly. |

#### Actions taken

- `plan_migration`: defaults `archive_date` to today; loads a (default-on-a-
  foreign-tree) `Config`; walks via `_iter_doc_texts` (already path-sorted);
  infers a tree-wide `Project:` once; per file runs the four inference
  helpers, parses metadata leniently, computes `synthesized_h1` /
  `reconciled_metadata`, plans the archive move, flags ambiguities, sets
  confidence, and builds the `FileMigration`.
- `_cmd_migrate`: `Path(args.dir)` not-a-dir → stderr, exit 2;
  `.docs.toml`-present refuse-guard → stderr (message names `.docs.toml`),
  exit 2; `--date` validated as ISO via `parse_date`; dry-run prints the
  human plan; the `--apply`/`--json` branches are wired (Phase 7 fills the
  helpers they call).

#### Issues / decisions

- **Ambiguity-flagging rule (resolved Q1) — recorded.** `plan_migration`
  flags an ambiguity for exactly three sources: (a) a `notes` role fallback,
  (b) a synthesised H1, (c) an out-of-vocab in-file `Status:` substituted with
  a built-in. It does NOT flag the plain active-tree status default nor the
  mtime-derived `Updated:` fallback — those are expected best-effort defaults.
  This is the only rule consistent with all 14 plan-migration tests (notably
  `test_plan_migration_pins_a_high_confidence_fixture_file`, which requires
  the clean active-tree `proj-auth-spec.md` to be `high`).
- **`-decision` suffix.** `proj-old-decision.md` ends in the token
  `decision`, a built-in role not in the `_ROLE_SUFFIXES` alias map (which
  only carries `adr → decision`). `infer_role` was extended so a trailing
  token that is itself a built-in role resolves to that role directly — a
  natural extension, documented in `cli.md` and the `infer_role` docstring.
- **mtime-derived `Updated:` non-determinism (resolved Q3) — noted.** A
  foreign doc with no in-file `Updated:` line gets `date.fromtimestamp(mtime)`.
  No M4 test asserts a fixed `updated` value for a fixture file; a future
  `migrate --apply` snapshot test must pin `--date` and avoid asserting an
  mtime-derived `Updated:`.

#### Exit criteria

- [x] All 14 `test_plan_migration_*` units green.
- [x] `test_migrate_dry_run_is_default_and_writes_nothing` +
      `test_migrate_dry_run_reports_every_file` green; refuse-guard green.
- [x] `ruff check` / `ruff format --check` / `mypy` clean tree-wide.

### Phase 7 — Update Tool/Wrapper Layer

**Completed:** 2026-05-22

#### Objective

Implement `apply_migration` (atomic in-place metadata writes + archive moves)
and `migration_to_json` (the pinned 10-key flat record). The `--apply` /
`--json` branches of `_cmd_migrate` were wired at Phase 6; this phase fills the
helpers they call.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `bin/docs` | Modify | Implemented `apply_migration` and `migration_to_json`. |

#### Actions taken

- `apply_migration`: per `FileMigration`, edits in place first (mirroring
  `_archive_one`'s edit-then-move ordering) — `insert_metadata_block` with the
  decided metadata and a `_slug_to_title` title, written via `atomic_write` —
  then, when `archive_move` is set, `mkdir -p` the destination parent and
  `Path.replace` the file into `archive/<date>/`.
- `migration_to_json`: one flat dict per `FileMigration` in plan order, the
  exact 10 keys `cli.md` pins (`path`, `role`, `project`, `status`, `updated`
  as ISO, `confidence`, `ambiguities` as a list, `archive_move`,
  `synthesized_h1`, `reconciled_metadata`).

#### Issues / decisions

- **`--json` is orthogonal to `--apply` (resolved Q4).** `--json` is a pure
  output-format switch: `--json` alone prints the dry-run plan as JSON;
  `--apply --json` performs the apply *and* prints the plan as JSON —
  consistent with `check` / `list`. `_cmd_migrate` calls `apply_migration`
  inside the same `try` that builds the plan, then chooses JSON-or-human
  output independently.
- `plan_migration` / `apply_migration` are wrapped in
  `except (MetadataError, VocabularyError, OSError)` → stderr, exit 2.

#### Exit criteria

- [x] All 9 `tests/test_cli_migrate.py` tests green.
- [x] Exit codes match `cli.md` (0 success, 2 already-a-docs-root /
      nonexistent dir).
- [x] `ruff` / `mypy` clean tree-wide.

### Phase 8 — Run Tests (GREEN)

**Completed:** 2026-05-22

#### Command + summary

```
.venv/bin/python -m pytest tests/ -q
=========================== 219 passed in ~3.1s ===========================

.venv/bin/ruff check .          → All checks passed!
.venv/bin/ruff format --check . → 18 files already formatted
.venv/bin/mypy                  → Success: no issues found in 18 source files
```

#### Exit criteria

- [x] Full suite green — 219 passed, 0 failed (164 M1-M3 tests + 55 M4 tests,
      all GREEN for the right reason; no test relaxed or rewritten).
- [x] `ruff check` / `ruff format --check` / `mypy` all green tree-wide.

### Phase 9 — Implement Online/Integration (dogfood pass)

**Completed:** 2026-05-22

#### Objective

Exercise `migrate` against the real `foreign/` fixture tree end-to-end —
dry-run plan completeness, `--json` schema, and an `--apply` on a *copy* that
`docs check` and `docs index` accept. No network surface; this is the
dogfooding pass.

#### Actions taken

- `./bin/docs migrate tests/fixtures/trees/foreign` → exit 0; the plan covers
  all 9 `.md` files; every low-confidence file lists ≥ 1 ambiguity and every
  high-confidence file lists none.
- `./bin/docs migrate tests/fixtures/trees/foreign --json` → exit 0; each of
  the 9 records carries exactly the pinned 10 keys.
- Copied `foreign/` to a scratch dir, `migrate --apply --date 2026-05-22` →
  exit 0; the `archived/` doc moved to `archive/2026-05-22/` with
  `Status: archived`, the no-H1 file got a synthesised `# Proj No H1`, the
  reconciled file's pre-existing `Status:`/`Updated:` lines folded into one
  block. `docs check <copy>` → exit 0; `docs index <copy>` → exit 0.
- `./bin/docs check docs/` → exit 0 (repo docs still clean).

#### Issues / decisions

- **`topics/proj-deep-notes.md` is `notes` role at `high` confidence.** Its
  filename's trailing token is literally `notes`, a built-in role, so
  `infer_role` resolves it confidently via the direct-builtin-suffix path —
  not the `notes` *fallback*. Only an unconfident `notes` fallback flags an
  ambiguity, so this file is correctly `high`. This is consistent behaviour,
  not a gap.
- **mtime-derived `Updated:` (resolved Q3).** Files with no in-file
  `Updated:` line show today's date in the dogfood run because the freshly
  `cp`-ed scratch copy carries a current mtime. A future `migrate --apply`
  snapshot test must pin `--date` and must not assert mtime-derived
  `Updated:` values.
- The empty `archived/` directory is left behind after the archive move
  (the file is `Path.replace`-d out, the now-empty dir is harmless and
  invisible to `_iter_doc_texts` / `walk`). No cleanup is in M4 scope.

#### Exit criteria

- [x] The `migrate` dry-run produces a complete plan — a decision for every
      file, every ambiguity flagged.
- [x] `--json` validates against the pinned 10-key schema.
- [x] `migrate --apply` on a copy yields a tree `docs check` accepts (exit 0)
      and `docs index` renders cleanly.
- [x] `docs check docs/` exit 0.

### Phase 10 — Quality, Docs, Refactor

**Completed:** 2026-05-22

#### Objective

Close out M4: full quality gate, update `status.md` / the milestone doc / this
log, regenerate `INDEX.md` and its dogfood snapshot, verify `cli.md` /
`architecture.md` / `plan.md` read as shipped, and make the conscious
single-file-vs-package-split call.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/m4-migration-helper.md` | Modify | Phase Checklist, Deliverables, Success Criteria all checked; Milestone-completion summary filled. |
| `docs/m4-migration-helper-log.md` | Modify | Phases 5-10 entries appended; TDD table + Progress line updated; this completion summary filled. |
| `docs/status.md` | Modify | M4 → Complete; milestone-progress table row; "Current milestone" prose; "Next action" → M5; "Resuming this work" verify-env block refreshed (test count → 219); `Updated:` bumped. |
| `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Re-synced in lockstep after the doc `Updated:` bumps. |

#### Actions taken

- Ran the full quality gate: `pytest tests/` → 219 passed; `ruff check` /
  `ruff format --check` / `mypy` → clean tree-wide.
- Updated `status.md`: M4 → Complete in the milestone-progress table and the
  "Current milestone" prose; "Next action" now points at M5 (Claude Code
  skill); the "Resuming this work" verify-env block's expected test count
  updated from the RED baseline to 219 passed.
- Verified `cli.md`'s `docs migrate` section and `--json` schema table match
  shipped behaviour (the role-inference rule note about a built-in-role
  trailing token was added at Phase 6).
- Verified `architecture.md`'s `migrate` module subsection matches shipped
  behaviour — no change needed.
- Verified `plan.md`'s M4 section reads as shipped; M4 opens no `plan.md` open
  question (operator-confirmed); the parked extra-field allowlist question is
  left untouched. `plan.md` body unchanged, so its `Updated:` is not bumped.
- Regenerated `docs/INDEX.md` via `./bin/docs index --root docs/` and copied
  it onto `tests/fixtures/expected/docs-INDEX.md` in lockstep.

#### Issues / decisions

- **`bin/docs` single-file vs package split — deferred to v1.1.** After M4 the
  file is ~2,200 lines. It is large but still cleanly sectioned with header
  comments (`Shared utilities`, `Core API`, `Validation and query`,
  `Migration (M4)`, `CLI`) and clean under `ruff` / `mypy`. M4 added one verb
  plus a self-contained cluster of inference helpers — the sectioning still
  carries the file. Per the M2/M3 precedent the split is the default-deferred
  choice; it is re-evaluated at v1.1 if the file outgrows its sectioning.
- **`/simplify` — light-touch only.** A dedicated Step 3 `/simplify` pass
  follows this implementation step, so Phase 10 made no structural refactor.
  The Phase 5-7 code is already linear and obvious (the inference helpers are
  short pure functions; `plan_migration` is one straight loop). Nothing was
  found that warranted a pre-emptive refactor here.

#### Exit criteria

- [x] Full quality gate green — 219 passed; `ruff` / `mypy` clean tree-wide.
- [x] `status.md` updated — M4 → Complete, M5 → next.
- [x] Milestone doc + this log updated; completion summaries filled.
- [x] `INDEX.md` + dogfood snapshot regenerated in lockstep.
- [x] `cli.md` / `architecture.md` / `plan.md` verified to read as shipped.
- [x] Single-file-vs-package-split call recorded (deferred to v1.1).

## Branch review — phases 5-10 fresh-eyes pass (2026-05-22)

A fresh-eyes review of the Step 2 implementation (M4 phases 5-10) on
`m4/phases-5-10` returned three should-fix findings and five nits. All
should-fixes and the operator-decided finding were addressed on this branch;
the documented-choice nits were left as-is per the reviewer.

#### Should-fix 1 — archive-move destination collision (silent data loss)

Two foreign files with the same basename in different archive-style subdirs
(e.g. `archived/dup.md` and `project-history/dup.md`) both normalise to one
`archive/<date>/dup.md` — `apply_migration`'s `path.replace(dest)` would
silently overwrite the first. Fixed: `apply_migration` now guards each move
with `if dest.exists(): raise FileExistsError(dest)` (mirroring
`_archive_one`), and `plan_migration` gained a cross-file second pass that
flags every file sharing a destination as a low-confidence ambiguity, so the
dry-run surfaces the collision before `--apply`. `_cmd_migrate`'s existing
`OSError` handler maps the apply-time `FileExistsError` to exit 2.

#### Should-fix 2 — `--date` error leaked the wrong field label

An invalid `docs migrate --date` reported `docs: Updated: malformed date …`
because `parse_date`'s `MetadataError` hard-codes the `Updated:` prefix.
Fixed to match `docs archive --date`: `_cmd_migrate` now prints
`docs: --date: {exc}`, naming the flag the user actually supplied.

#### Should-fix 3 (operator-decided) — preserve foreign extra metadata

`insert_metadata_block` previously dropped any metadata-shaped line that was
not one of the four required fields. Per the operator's binding decision,
non-required fields (`Owner:`, `Tags:`, `Related:` blocks, any other
`Label: value` line) are now **preserved** into a `## Migrated metadata` body
section placed immediately below the canonical block, each label renamed under
a `Migrated-` prefix (`Related:` keeps its bullet sub-items verbatim). A
foreign doc with no extra fields gets no section. The preserved fields live in
the body under a `## ` heading, so `parse_metadata_block` does not re-harvest
them and `docs check` does not validate them — the applied tree still passes
`docs check` and round-trips through `parse()` with exactly the four required
fields in the real block (verified). The `Migrated-` rename rule was not
specified by the operator; the prefix is the **conductor's default choice**,
recorded in the milestone Decisions for operator review. New fixture
`tests/fixtures/trees/foreign/proj-extra-metadata.md` carries `Owner:` /
`Tags:` / a `Related:` block to exercise the path; the dry-run human plan
reports a preserved-field count per file.

#### Nits

- Nit 4 — stale `(M4, in progress)` in `main()`'s docstring corrected to
  `(M4)`. (The pre-existing stale M2 comment elsewhere is out of M4 scope and
  left untouched.)
- Nit 5 — added a unit test for the `-milestone` branch of `infer_role`'s
  built-in-role trailing-token extension (previously uncovered); the
  extension itself is sound and unchanged.
- Nit 7 — added a `--quiet` CLI test.
- Nits 6 and 8 — documented-choice edge cases (`detect_archive_layout`
  edges; `apply_migration` non-transactionality); left as-is per the
  reviewer.

#### Result

Full suite **236 passed, 0 failed** (72 M4 tests, +17 over the original 55);
`ruff check` / `ruff format --check` / `mypy` clean tree-wide;
`./bin/docs check docs/` exit 0. `INDEX.md` and the dogfood snapshot
regenerated in lockstep with the doc-body changes.

## Simplify pass — phases 5-10 (2026-05-22)

A `/simplify` pass over the M4 migration code (the inference helpers, models,
`plan_migration` / `apply_migration` / `migration_to_json`, and the `migrate`
CLI wiring) on `m4/simplify`. The inference helpers are already short pure
functions and `plan_migration` is one straight loop plus the reviewed
collision pass — the only genuine simplification found was in
`detect_archive_layout`.

- **`detect_archive_layout` — collapsed a duplicated return and an inverted
  try/except.** The function spelled the archive-style name set three ways
  (`("archived", "project-history")` tuple, a separate `first == "archive"`
  check, and the unused module constant `_ARCHIVE_SUBDIR_NAMES`) and wrote the
  `archive/<date>/<basename>` destination string in three places, once inside
  a try-block whose `except` returned the *normalise* result. Rewritten to an
  early `if first not in _ARCHIVE_SUBDIR_NAMES: return None` guard, a single
  conformant-`archive/<ISO-date>/` exception, and one trailing
  `return f"archive/{archive_date}/{parts[-1]}"`. Same behaviour for all five
  input shapes (verified by the unchanged `detect_archive_layout` tests);
  the archive-name set is now spelled once, in `_ARCHIVE_SUBDIR_NAMES`.

Nothing else changed — the rest of the M4 code is already minimal. Full suite
**236 passed, 0 failed**; `ruff check` / `ruff format --check` / `mypy` clean
tree-wide. No doc-body change, so `INDEX.md` and the dogfood snapshot were not
regenerated.

## Milestone-completion summary

**M4 — Migration helper (`docs migrate`) shipped 2026-05-22** across the ten
TDD phases. Phases 1-4 (contract, RED tests, the `foreign/` fixture tree, RED
baseline) landed on `m4/phases-1-4`; phases 5-10 (implement + ship) on
`m4/phases-5-10`.

`docs migrate <dir>` adopts a non-conforming foreign directory into the
convention: it walks the tree, infers the four required fields per file
(`Role` from filename suffixes + in-file signals, `Project` from a shared
filename prefix, `Status` from in-file signals or archive membership,
`Updated` from an in-file line or mtime), and produces a complete migration
plan — a decision and a confidence for every file, with every ambiguity
surfaced. Dry-run by default; `--apply` inserts the metadata blocks atomically
and normalises archive-style subdirectories into `archive/YYYY-MM-DD/`. It
refuses a directory that is already a docs root.

The implementation added the `FileMigration` / `MigrationPlan` models, five
pure inference helpers, `insert_metadata_block`, `plan_migration` /
`apply_migration` / `migration_to_json`, and the `migrate` verb wiring to
`bin/docs`. A subsequent fresh-eyes branch review of phases 5-10 added two
should-fixes (archive-move collision detection; the `--date` error label) and
the operator-decided extra-metadata-preservation behaviour — see the "Branch
review" section above. 72 M4 tests across `tests/test_migrate.py` and
`tests/test_cli_migrate.py`; the full suite stands at **236 passed, 0 failed**
with `ruff` / `mypy` clean tree-wide.

The active-tree directory layout is left untouched — `--apply` adds metadata
in place; the only directory moves are archive-style subdirs normalised to the
convention's layout. The `bin/docs` single-file-vs-package split was
re-evaluated and **deferred to v1.1** — the file's sectioning still carries it.

Next: M5 — Claude Code skill.
