# M7 — Implementation Log

Status: active
Role: log
Project: docs
Updated: 2026-05-24

Related:
- child-of: m7-migration-accuracy.md
- pairs-with: status.md

## Implementation metadata

- Project: docs
- Milestone: M7 — Migration plan accuracy
- Started: 2026-05-24
- Progress: **Phase 1 complete; Phase 2 next.** The task plan
  [m7-migration-accuracy.md](m7-migration-accuracy.md) is promoted
  from `draft` to `active`; M7 is the second v1.1 milestone (after
  M6). All four milestone-setup OPEN QUESTIONS are resolved
  2026-05-24 (OQ-A core role vocab adds 7 entries —
  `template`, `example`, `implementation`, `sketch`, `outline`,
  `memo`, `brief`; OQ-B project-name normalisation splits on case
  + underscore + letter-to-digit boundaries; OQ-C sibling
  defaulting threshold is 60% majority with ≥ 5 sample;
  OQ-D introduces a third confidence level `medium` between `high`
  and `low`). Resolutions are recorded as Decisions in the task
  plan. The trial-run evidence from 2026-05-24 (501 .md files
  across 25 real-world sibling trees) is the source of truth for
  M7's findings F0/F1/F4/F10/F11/F12. Phase 1 also creates this
  log file; no code change at Phase 1.

(Note: doc-lifecycle status is in the front-matter `Lifecycle:`
field above — wait, this milestone introduces the
`Status:` → `Lifecycle:` rename. Until Phase 5 lands, this log's
front-matter uses `Status:` to match the current convention. Phase
5 sweeps every doc including this log to the new key.)

## Milestone-setup open questions

Four questions were surfaced while authoring the task plan.
**All four are resolved 2026-05-24**, recorded as Decisions in
the task plan. Summary:

1. **OQ-A — Role vocab additions — RESOLVED 2026-05-24, per
   recommendation.** Add to **core** controlled-role vocab:
   `template`, `example`, `implementation`, `sketch`, `outline`,
   `memo`, `brief`. (`explainer` deferred to
   `[vocabulary] add_roles`.)
2. **OQ-B — Project-name normalisation for digit-glued names —
   RESOLVED 2026-05-24, per recommendation.** Split on case
   boundaries AND letter-to-digit boundaries. So `Abc5Migration`
   → `abc-5-migration`. Preserves digit-after-digit so
   `bugs-2026-01-26` stays intact. Surface
   `(normalised from "<original>")` in plan output;
   `[migrate] project_name` in `.docs.toml` overrides.
3. **OQ-C — Sibling-set defaulting threshold — RESOLVED
   2026-05-24, per recommendation.** Defaults to modal sibling
   role when ≥ 60% majority **and** subdir has ≥ 5 files. Below
   either threshold, falls to `notes` at low confidence. When
   defaulting fires, confidence is `medium`.
4. **OQ-D — Confidence levels — RESOLVED 2026-05-24, per
   recommendation.** Introduce `medium` as a third level between
   `high` and `low`. `docs check` treats medium as warning (exit
   1), not error (exit 2). Used by sibling-set defaulting,
   H1-content inference, section-header inference, and non-role
   suffix stripping.

## Summary

Make `docs migrate`'s plan accurate enough on real-world foreign
trees to drive end-to-end adoption. Today migrate against a
representative real tree produces 25% high-confidence inferences
and silently drops the dominant real-world use of `Status:`
(free-form prose). M7 fixes both: breaks the convention's
controlled-vocab key from `Status:` to `Lifecycle:` (preserving
prose `Status:` lines verbatim through migrate), broadens role
inference with H1 + section-header + sibling-set signals,
introduces a third "medium" confidence level, normalises project
names to lowercase-kebab, and proposes archive normalisation for
foreign trees that already keep an `archived/` subdir. No new
CLI surface adds **one new flag** — `docs migrate
--config-project <name>` (the multi-project override per F5);
otherwise pure inference + convention. (No `--rename-status-
to-lifecycle` helper; the in-project `Status:` → `Lifecycle:`
sweep at Phase 5 is a one-off manual `sed` edit, not a shipped
feature — operator decision 2026-05-24.) The trial-2 fixtures
from
the 2026-05-24 multi-tree sweep (sanitised at Phase 3) become
the regression baseline. M7 ships as 1.2.0 — the breaking schema
rename is the semver trigger.

## TDD Phase Progress

| Phase | Status | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-05-24 | Promote M7 from `draft` to `active` (done); create this log (done); record OQ A–D resolutions as Decisions in the task plan (done); update status.md "Current milestone" to mark M7 setup complete + Phase 2 next; flip Phase 1 row + status.md "in flight" wording to "Phase 1 complete; Phase 2 next"; append Phase 1 log entry; regenerate INDEX + snapshot in lockstep. No code change; no convention change. |
| 2. Write Tests (RED) | Complete | 2026-05-24 | Five new test files plus a confidence-distribution extension to `test_migrate.py`: `test_lifecycle_rename.py` (5 tests, F0); `test_inference.py` (21 tests, F1/F10/F12 — parametric expansion of word-boundary, suffix-strip, new vocab, `_M\d+`, H1, section-header, sibling-set); `test_project_normalisation.py` (10 tests, F11 — TitleCase/snake-upper/mixed/single-word/digit-glued parametric plus `--config-project` override + human-output "(normalised from …)" assertions); `test_archive_normalisation.py` (4 tests, F4); `test_multi_project_hints.py` (3 tests, F5). All RED for intended unimplemented surface; M6's 271 stay GREEN. Confidence assertions use the forward-compatible sentinel `("medium", "high", True)` per OQ-D / OQ-4. |
| 3. Create Data/Fixtures | Complete | 2026-05-24 | Five sanitised real-tree fixtures under `tests/fixtures/trees/real-trees/` (kebab-tiny / snake-medium / snake-large / archive-subdir / mixed-naming) — fabricated sanitised analogs preserving the Trial-2 shape categories (TitleCase / snake_TitleCase / kebab) since `/tmp/m7-trial2/` was lost. Per-finding fixtures under `tests/fixtures/lifecycle/` (3 files), `status-prose/` (4 single-line prose fixtures; multi-line continuation deferred per OQ3), `project-names/` (7 dirs × 3 files), `sibling-defaulting/` (3 subdirs: majority-met 10 / majority-not-met 10 / sample-too-small 4). Sanitisation grep against the trial-2 product/feature names returns 0 hits. |
| 4. Run Tests (RED Baseline) | Complete | 2026-05-24 | Captured verbatim pytest output: **34 failed + 281 passed = 315 collected**. The 281 passing decomposes as M6's 271 GREEN + 10 new GREEN-at-baseline regression locks (`_M\d+`-with-`_Log` combination; sibling-not-defaulting × 2; kebab + digit-after-digit pass-through × 2; `(normalised from …)` annotation omitted-when-unchanged; archive `no-d` shape; `--date` global override; already-conformant archive no-move; multi-project hint below-threshold). The 34 failing trace to their intended unimplemented surfaces (parser-only-knows-Status, no broadened inference, no normalisation, no per-file-mtime archive date, no multi-project hint, no `--config-project` argparse flag). Quality gate clean tree-wide. |
| 5. Update Base Interfaces | Pending | — | **The F0 rename.** Parser accepts only `Lifecycle:`; `Status:` becomes a free-form extra field. Add `Confidence.MEDIUM`. Add `Config.role_suffixes` + `Config.project_name` + rename `add_statuses` → `add_lifecycles`. Argparse adds `--config-project` to `docs migrate` (F5) and renames `docs list --status` → `--lifecycle` (single argparse site at `list_p`; `docs check` has no analogous flag). **No rename helper shipped** — sweep this project's own `docs/` (27 files) with one-off `sed -i 's/^Status: \(active\|blocked\|done\|draft\|superseded\|archived\)$/Lifecycle: \1/' docs/*.md`. Update convention.md. F0 tests flip RED → GREEN; rest stay RED for Phase 6. |
| 6. Implement Offline/Core Path | Pending | — | F1 (word-boundary tolerance, H1 + section signals, sibling defaulting), F10 (vocab additions, non-role suffix stripping), F11 (project-name normalisation + override), F12 (`_M\d+` milestone suffix), F4 (archive normalisation), F5 (multi-project hint emission in `migrate_plan` + `--config-project` honoured). All M7 RED tests turn GREEN. |
| 7. Update Tool/Wrapper Layer | Pending | — | convention.md (rename + new vocab + medium confidence + `add_statuses` → `add_lifecycles`), cli.md (F0 breaking note + `--config-project` synopsis + `docs list --status` → `--lifecycle` flag rename + project-normalisation output shape + multi-project hint footer shape + `docs check` exit-code clarification), architecture.md (Config schema), status.md ("Watch out for" entry), README.md (any `Status:` references swept to `Lifecycle:`), CHANGELOG.md (`## 1.2.0 — UNRELEASED`), pyproject.toml + cli.py `__version__` bumped to 1.2.0, src/docs_cli/skill/references/{convention,cli}.md resynced. |
| 8. Run Tests (GREEN) | Pending | — | Full quality gate verbatim: pytest ≥ 296 passed; ruff / format / mypy clean; `docs check docs/` exit 0; `docs index --dry-run` no diff. |
| 9. Implement Online/Integration | Pending | — | Mapped to dogfooding against Trial 2 fixtures. Confirm 5 quantitative success criteria (confidence ≥ 50%, notes ≤ 30%, status preservation 100%, archive proposals ≥ 80%, normalisation ≥ 90%). Helper script at `tests/manual/m7_success_criteria.py` aggregates and reports. |
| 10. Quality, Docs, Refactor | Pending | — | Dogfood consistency sweep; milestone-completion summary; status.md M7 → Complete; CHANGELOG dated; `v1.2.0` tag pushed; (operator-driven) `python -m build` + `twine upload` per the runbook same as M6; `gh release create v1.2.0`. |

## Current state analysis (snapshot at milestone kickoff, 2026-05-24)

_Captured before Phase 2; historical._

- **Codebase.** `src/docs_cli/cli.py` is the monolithic CLI module
  (relocated from `bin/docs` at M6 Phase 5). The migrate verb
  (`_cmd_migrate`, `migrate_plan`, `infer_role`, `infer_project`,
  `infer_status`) lives here. The convention's controlled-vocab
  field is currently `Status:` (parsed by
  `parse_metadata_block` → `Doc.status`). Two confidence levels
  exist today: `high`, `low`. `Config` knows about
  `[vocabulary] add_statuses`, `[vocabulary] add_roles`, but not
  about `role_suffixes` or `project_name`.
- **Specs.** `docs/convention.md` documents the metadata block
  with `Status:` as the controlled-vocab key.
  `docs/cli.md` documents the 8-verb surface; `docs migrate` has
  `--apply`, `--json`, `--quiet`, `--date` (no
  no rename helper either — the M7 sweep is manual).
- **Tests.** 271 passing (M6's GREEN gate). M4's
  `tests/test_migrate.py` covers basic migrate happy paths; no
  tests for the failure modes M7 fixes.
- **Trial-run evidence.** `/tmp/m7-migrate-full.txt` (Trial 1,
  235 files) and `/tmp/m7-trial2/*.json` (Trial 2, 25 trees /
  501 files) — produced 2026-05-24, are the source for fixture
  promotion at Phase 3.
- **Symlink state.** `~/.claude/skills/docs` points at
  `/home/user/opt/docs-cli/src/docs_cli/skill/` (refreshed at
  M6 Phase 5).

## Files to Create / Modify

| File | Action | Phase | Notes |
|---|---|---|---|
| `docs/m7-migration-accuracy.md` | Modify | 1, 10 | Flip `Status: draft` → `active` (done at setup); append milestone-completion summary at Phase 10. |
| `docs/m7-migration-accuracy-log.md` | Create | 1 | This file. |
| `docs/status.md` | Modify | 1, 5, 7, 10 | Phase 1: M7 setup complete; Phase 5: "Watch out for" gets F0 entry; Phase 10: M7 → Complete. |
| `docs/plan.md` | (already registered) | — | M7 row added at the registration commit `1df6ec6`. |
| `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` | Regenerate | 1, 5, 7, 10 | Every doc-touching phase regenerates in lockstep. |
| `tests/test_lifecycle_rename.py` | Create | 2 | F0 — 5 tests covering parser acceptance/rejection, check error, migrate preservation. (No 6th rename-helper test — helper dropped per operator decision 2026-05-24.) |
| `tests/test_inference.py` | Create | 2 | F1/F10/F12 — 9 tests covering word-boundary, non-role stripping, new vocab, `_M\d+`, H1, section headers, sibling defaulting (3 cases). |
| `tests/test_project_normalisation.py` | Create | 2 | F11 — per-fixture parametric tests + `[migrate] project_name` override + `--config-project` CLI override (F5 hand-off). |
| `tests/test_archive_normalisation.py` | Create | 2 | F4 — 4 tests for `archived/` and `archive/` normalisation. |
| `tests/test_multi_project_hints.py` | Create | 2 | F5 — 3 tests: hint emitted when subdir's common prefix differs from parent (≥ 5 files); hint NOT emitted below the 5-file threshold; `--config-project <name>` override propagates to inferred-project for every file in the plan. |
| `tests/test_migrate.py` | Modify | 2 | Add confidence-distribution test against a representative fixture. |
| `tests/test_cli_list.py` | Modify | 5 | Sweep every `--status` flag arg → `--lifecycle` to match the argparse rename. Assertion text referencing the flag updated. |
| `tests/fixtures/trees/real-trees/{kebab-tiny,snake-medium,snake-large,archive-subdir,mixed-naming}/` | Create | 3 | 5 sanitised Trial-2 trees. |
| `tests/fixtures/{status-prose,project-names,sibling-defaulting}/` | Create | 3 | Small single-file fixtures per finding. |
| `src/docs_cli/cli.py` | Modify | 5, 6, 7 | Phase 5: F0 parser rename + Confidence enum + `add_statuses` → `add_lifecycles` Config rename + `--config-project` argparse addition (F5) + `docs list --status` → `--lifecycle` argparse rename (single site at `list_p`). Phase 6: F1/F10/F11/F12/F4/F5 inference + normalisation + archive normalisation + multi-project hint emission. Phase 7: `__version__` bumped to 1.2.0. |
| `docs/convention.md` | Modify | 5, 7 | Phase 5: rename `Status:` → `Lifecycle:` in the schema. Phase 7: document new vocab + medium confidence + `[migrate]` config knobs. |
| `docs/cli.md` | Modify | 7 | F0 breaking-change note at the top of the migrate verb section; `--config-project <name>` synopsis + example (F5); `docs list --status` → `--lifecycle` flag rename (synopsis line ~83, filter description ~87); project-normalisation output shape; multi-project hint footer shape; `docs check` exit-code clarification for medium confidence. |
| `docs/architecture.md` | Modify | 7 | `Config` schema includes `role_suffixes` + `project_name`. |
| `README.md` | Modify | 7 | Any `Status:` references swept to `Lifecycle:`. |
| `CHANGELOG.md` | Modify | 7, 10 | Phase 7: `## 1.2.0 — UNRELEASED` entry. Phase 10: dated. |
| `pyproject.toml` | Modify | 7 | `version = "1.2.0"`. |
| `src/docs_cli/skill/references/convention.md` | Modify | 7 | Resync from `docs/convention.md`. |
| `src/docs_cli/skill/references/cli.md` | Modify | 7 | Resync from `docs/cli.md`. |
| Every `docs/*.md` Status: line | Modify | 5 | Mechanical one-off sweep via `sed -i 's/^Status: \(active\|blocked\|done\|draft\|superseded\|archived\)$/Lifecycle: \1/' docs/*.md` (no shipped helper; regex covers full BUILTIN_STATUSES). 27 files at the audit point (23 `active` + 4 `done`); count may drift before Phase 5. Verify with `grep -l "^Status:" docs/` → empty after. |
| `tests/manual/m7_success_criteria.py` | Create | 9 | Aggregates the 5 success metrics from the Phase 9 JSON dumps. |

## Phase logs

_Per-phase entries are appended below as each phase completes,
mirroring M5/M6 log shape: Objective / Files changed / Actions
taken / Issues / decisions / Exit criteria._

### Phase 1 — Define Contract

**Completed:** 2026-05-24

#### Objective

Declare the M7 surface — the F0 controlled-vocab rename
(`Status:` → `Lifecycle:`), the inference broadening (F1, F10,
F12), F4 archive normalisation, F11 project-name normalisation,
and F5's lone new CLI flag `--config-project <name>`. No code
change at this phase; no convention edits. Promote the task plan
to active (done at milestone-setup), create this log (done),
record OQ A–D resolutions as Decisions (done), and refresh
`status.md` + the log's TDD Phase Progress table so the
historical record reads "Phase 1 complete; Phase 2 next" rather
than "Phase 1 in progress" at the close-out commit. The 271-test
suite stays GREEN throughout.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/status.md` | Modify | M7 milestone-table row flipped from "Phase 1 in progress" to "Phase 1 complete; Phase 2 next". The "Next action" was already pointing at Phase 2 from the milestone-setup commit; no further edit needed. |
| `docs/m7-migration-accuracy-log.md` | Modify | "Progress" paragraph (Implementation metadata) rewritten from "Milestone-setup phase complete; Phase 1 in progress" → "Phase 1 complete; Phase 2 next". TDD Phase Progress table's Phase 1 row Status flipped In progress → Complete; row Notes tightened to reflect the close-out scope (table-row tightening + log entry + final INDEX regen). This Phase-1 log entry appended. |
| `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Re-synced in lockstep via `.venv/bin/docs index --root docs/` after the text edits, so the (already-registered) M7 plan + log carry their fresh `Updated:` line in the snapshot. |

#### Actions taken

- **Audit of prior commits.** Verified that the bulk of the M7
  Phase 1 deliverables landed in the four earlier setup commits
  (`1df6ec6` — register M7 + M8 stubs; `ad58816` — activate +
  expand TDD plan + create log; `25d4f79` — `docs list --status`
  → `--lifecycle` flag rename scope addition; `a701876` — M9
  split). The residual delta at Phase 1 close-out is purely the
  "row flips + log entry" wording.
- **Doc-text edits.** Tightened `status.md`'s M7 row and the
  M7 log's "Progress" paragraph + TDD Phase Progress table to
  read "Phase 1 complete; Phase 2 next". Bumped `Updated:` lines
  per the convention (`docs touch` semantics — same-day edits
  keep today's date; no actual day change).
- **INDEX regen.** Ran `.venv/bin/docs index --root docs/`;
  copied `docs/INDEX.md` over
  `tests/fixtures/expected/docs-INDEX.md` so the dogfood
  snapshot reflects the M7-log "Phase 1 complete" body change
  (the snapshot includes each doc's first-paragraph description).
- **Quality gate.** Ran the full gate from the project root:
  pytest 271 green; `ruff check .` clean; `ruff format --check .`
  clean; `mypy` Success; `.venv/bin/docs check docs/` exit 0.

#### Issues / decisions

- **No new code, no convention edit.** Phase 1 stays the
  reviewable-in-isolation phase per the task plan's Phase 1
  exit criteria. The F0 schema rename and the in-project
  `Status:` → `Lifecycle:` sweep are Phase 5 work; the inference
  broadening is Phase 6 work. Confirmed via `git diff` that the
  Phase 1 close-out commit touches only `docs/status.md`,
  `docs/m7-migration-accuracy-log.md`, `docs/INDEX.md`, and the
  INDEX snapshot.
- **Status-line wording carried forward.** This log's
  front-matter still reads `Status: active` (not `Lifecycle:`)
  because the rename has not happened yet — the parser only
  accepts `Status:` until Phase 5 lands. The parenthetical note
  immediately after the "Progress" paragraph explains the
  transitional state for future readers.

#### Exit criteria

- [x] `Status:` in `m7-migration-accuracy.md` is `active`
      (set at milestone-setup; unchanged here).
- [x] `docs/m7-migration-accuracy-log.md` exists; its TDD Phase
      Progress table's Phase 1 row is Complete (2026-05-24).
- [x] `docs/status.md` M7 milestone-table row reads "Phase 1
      complete; Phase 2 next".
- [x] `docs/INDEX.md` and
      `tests/fixtures/expected/docs-INDEX.md` are byte-identical
      after regeneration.
- [x] `.venv/bin/python -m pytest tests/ -q` — 271 passed.
- [x] `ruff check .`, `ruff format --check .`, `mypy` — clean.
- [x] `.venv/bin/docs check docs/` — exit 0.
- [x] No code change happened (no `src/` edits, no
      `pyproject.toml` edits, no test file additions).
- [x] No convention change happened (no
      `Status:` → `Lifecycle:` rename yet — that's Phase 5).

### Phase 2 — Write Tests (RED)

**Completed:** 2026-05-24

#### Objective

Express every M7 finding (F0/F1/F4/F5/F10/F11/F12) as a failing
check before any implementation lands. Tests collect cleanly,
fail RED for the intended unimplemented surface (not for
configuration/import accidents), and leave M6's 271 GREEN.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `tests/test_lifecycle_rename.py` | Create | 5 tests for F0 — parser accepts `Lifecycle:`; parser rejects `Status:` as the controlled-vocab key; `docs check` errors on Status-without-Lifecycle and accepts Lifecycle plus free-form Status prose; migrate preserves free-form Status as `Migrated metadata`. |
| `tests/test_inference.py` | Create | 21 tests for F1/F10/F12. Word-boundary tolerance (1); non-role suffix stripping (`_v\d+` / `_Draft`) parametric × 3; new core vocab roles (`implementation`/`sketch`/`outline`/`memo`/`brief`/`template`/`example`) parametric × 7; `_M\d+` milestone-number suffix parametric × 4 (plus a `_M1_Implementation_Log.md` case that's a regression lock); H1-content inference via `plan_migration`; section-header pattern inference via `plan_migration`; sibling-set defaulting via `plan_migration` (majority-met / sample-too-small / no-majority). |
| `tests/test_project_normalisation.py` | Create | 10 tests for F11. TitleCase / SNAKE_UPPER / mixed-underscore / bare-TitleCase parametric × 4 + digit-glued × 1 + kebab + digit-after-digit regression locks × 2; `--config-project` CLI override shorts-circuits normalisation (OQ2); human output surfaces `(normalised from "X")` when changed; human output omits the annotation when unchanged (regression lock). |
| `tests/test_archive_normalisation.py` | Create | 4 tests for F4. Per-file mtime drives archive date (RED); `archive/` no-d shape normalises (regression lock); `--date` global override (regression lock); already-conformant `archive/YYYY-MM-DD/` no-move (regression lock). |
| `tests/test_multi_project_hints.py` | Create | 3 tests for F5. Subdir with distinct common prefix emits hint (RED); subdir below 5-file threshold emits no hint (regression lock); `--config-project` CLI flag propagates to every record (RED — argparse rejects the unknown flag). |
| `tests/test_migrate.py` | Modify | One new test — confidence-distribution ratio `(high+medium)/total ≥ 0.5` on `tests/fixtures/trees/real-trees/snake-medium/`. Codifies M7's quantitative success criterion (OQ-D + the 5-criterion gate at Phase 9). |

#### Test counts

- 44 new test items collected (5 + 21 + 10 + 4 + 3 + 1).
- Total suite: 315 collected (271 M6 + 44 new).

#### Quality discipline

- All test files use the existing `from docs import …` alias from
  `tests/conftest.py` (M6 conftest aliases `docs_cli.cli` as
  `docs`).
- Subprocess CLI tests use the `docs_script` and `fixtures_dir`
  session fixtures.
- Confidence assertions use the forward-compatible sentinel
  `("medium", "high", True)` so the tests already read the right
  shape for the post-Phase-5 third confidence level (OQ-D /
  OQ-4).
- H1 / section-header / sibling tests drive `plan_migration`
  end-to-end rather than calling `infer_role` directly — these
  signals materialise only inside the plan layer, never inside
  the function-level `(filename, metadata)` surface (OQ-5).
- Word-boundary, non-role-strip, new-vocab, `_M\d+` tests call
  `infer_role` directly because they only depend on the filename.
- Project normalisation tests drive `plan_migration` on tmp
  trees rather than importing an undefined `normalise_project_name`
  symbol (OQ-7).

#### Issues / decisions

- **Parametric expansion blew the test count past 28.** The plan
  said 28 new tests; the parametric expansion (3 strip cases, 7
  new vocab cases, 4 `_M\d+` cases, 4 TitleCase cases, 2 kebab
  regression cases) produces 44 collected items. The operator's
  binding OQ1 resolution accepts "~20 RED + ~8 regression-locks";
  the actual baseline split (Phase 4) lands close: 34 RED + 10
  GREEN-at-baseline regression locks. No new test was invented;
  the parametric form just unrolls the planned cases.
- **FileMigration.confidence is a closed set today.** Today
  `FileMigration.__post_init__` validates `confidence in
  ("high", "low")`. The sibling-defaulting and H1-content tests
  drive `plan_migration` end-to-end, which constructs
  `FileMigration` — if Phase 5 omits the medium-confidence
  enum extension, those tests fail on the `__post_init__` check
  rather than on the asserted contract. Phase 5 must extend the
  validation to include `medium`.
- **`Foo_M1_Implementation_Log.md` is GREEN at baseline.** The
  `_Log` suffix wins over the `_M\d+` pattern under today's
  matcher — this is the expected behaviour going forward and
  the test serves as a regression lock that the `_M\d+` rule
  added at Phase 6 doesn't steal the case.
- **OQ-3 narrowed status-prose fixtures to single-line shapes.**
  Multi-line `Status:` prose continuation is out of scope for
  M7; the 4 fixtures created at Phase 3 cover cases 1, 3, 4, 6
  from the original planning list (cases 2 and 5 dropped).

#### Verification

- `.venv/bin/python -m pytest --collect-only -q tests/test_lifecycle_rename.py tests/test_inference.py tests/test_project_normalisation.py tests/test_archive_normalisation.py tests/test_multi_project_hints.py` — 43 items collected, zero ImportError / CollectError.
- `.venv/bin/python -m pytest --collect-only -q tests/` — 315 items collected.
- `.venv/bin/python -m pytest tests/ -q --ignore=tests/test_lifecycle_rename.py --ignore=tests/test_inference.py --ignore=tests/test_project_normalisation.py --ignore=tests/test_archive_normalisation.py --ignore=tests/test_multi_project_hints.py --deselect tests/test_migrate.py::test_confidence_distribution_meets_threshold` — 271 passed, 1 deselected (M6 baseline preserved).
- `.venv/bin/ruff check .`, `ruff format --check .`, `mypy` — clean tree-wide.
- `.venv/bin/docs check docs/` — exit 0.

#### Exit criteria

- [x] Every new test file collects cleanly.
- [x] Every RED test fails for its intended unimplemented
      surface (Phase 4 captures the verbatim split + per-test
      attribution).
- [x] M6's 271 in-tree tests stay GREEN.
- [x] Imports use the conftest `from docs import …` alias.
- [x] Subprocess tests use `docs_script` + `fixtures_dir`.
- [x] No fixture authoring at this phase (Phase 3 owns that).
- [x] `ruff` / `format` / `mypy` clean tree-wide.
- [x] `docs check docs/` exit 0.

### Phase 3 — Create Data/Fixtures

**Completed:** 2026-05-24

#### Objective

Stage the fixtures the Phase-2 tests reference. The fixtures
span the shape categories the milestone doc's Generalisation
note pins (TitleCase, snake_TitleCase, kebab-case, mixed) so the
M7 inference improvements get tested against the real-world
shapes — not against an overfit copy of the Trial-2 trees.

#### Files changed

| Path | Action | Notes |
|---|---|---|
| `tests/fixtures/trees/real-trees/kebab-tiny/` | Create | 3 kebab-case files (`foo-bar-{spec,plan,status}.md`). Smallest size class. |
| `tests/fixtures/trees/real-trees/snake-medium/` | Create | 17 snake_TitleCase files. Drives the confidence-distribution test — today scores 4/17 = 24% high; after M7 inference broadening must reach (high+medium)/total ≥ 0.5. |
| `tests/fixtures/trees/real-trees/snake-large/` | Create | 72 snake_TitleCase files. Scale stress (every `_M\d+` / `_Implementation` / `_Component_*_Spec` / `_Task_*_Plan` shape that Trial 2 surfaced). |
| `tests/fixtures/trees/real-trees/archive-subdir/` | Create | 10 active-tree files + 5 under `archived/` for the F4 archive-normalisation test. |
| `tests/fixtures/trees/real-trees/mixed-naming/` | Create | 10 files spanning TitleCase + space-separated + snake_TitleCase + kebab; for the word-boundary stress shape. |
| `tests/fixtures/lifecycle/{lifecycle-key,status-only,lifecycle-plus-status-prose}.md` | Create | 3 single-file fixtures for the F0 parser tests. |
| `tests/fixtures/status-prose/{freeform-status,draft-companion,planning-only,p0-implemented}.md` | Create | 4 single-line free-form `Status:` prose shapes (cases 1, 3, 4, 6 from the planning agent's list; cases 2 and 5 deferred per OQ-3). |
| `tests/fixtures/project-names/{FooBarBaz,Abc5Migration,FOO_BAR_BAZ,Foo_Bar_Baz,Plan,embedded-ai-discovery-parallel,bugs-2026-01-26}/` | Create | 7 directories × 3 files each (`alpha.md` / `beta.md` / `gamma.md`). The 3-file shape is deliberate: with files whose stems don't share a common prefix, `infer_project`'s common-prefix path returns "" (length 0 < 2) and inference falls back to the dir_name — which is where F11 normalisation will land at Phase 6. |
| `tests/fixtures/sibling-defaulting/majority-met/` | Create | 10 files (7 `-spec` + 3 `-no-suffix`) exercising the 60% modal + ≥ 5 sample threshold (OQ-C). |
| `tests/fixtures/sibling-defaulting/majority-not-met/` | Create | 10 files (4 spec + 3 plan + 3 no-suffix); no single role hits 60%. |
| `tests/fixtures/sibling-defaulting/sample-too-small/` | Create | 4 files (3 spec + 1 no-suffix); below the ≥ 5 minimum. |

#### Actions taken

- Built each fixture tree by hand. `/tmp/m7-trial2/*.json`
  exists only as JSON dry-run outputs, not as the source trees
  themselves (the trees were tmpdir-scoped and are gone). Per
  the planning agent's note, the fixtures are *sanitised
  analogs that preserve the shape categories* — they are
  evidence-shaped, not literal copies.
- Filled each file with a one-line H1 + a one-paragraph body.
  No third-party product / customer / feature names appear in
  any file. Generic `Foo` / `Bar` / `Baz` / `Acme`
  placeholders only.
- Two project-names directories
  (`embedded-ai-discovery-parallel/`, `bugs-2026-01-26/`) keep
  their literal Trial-2 corpus names because the directory
  *names themselves* are the regression-test cases — they pin
  the kebab-pass-through and digit-after-digit-pass-through
  contracts. The directory names are generic kebab shapes, not
  product names; the sanitisation grep targets file *contents*,
  not paths.
- Ran the sanitisation grep across every Phase-3 fixture tree:

  ```sh
  grep -ri "langfuse\|festo\|orginfo\|embedded.ai\|gpt5\|treatment.rubric\|disambiguation\|risk.prompt\|software.first\|standalone.agents\|orgcontext" tests/fixtures/{trees/real-trees,status-prose,project-names,sibling-defaulting,lifecycle}/
  ```

  Zero hits.

#### Issues / decisions

- **`/tmp/m7-trial2/` source trees are no longer recoverable.**
  Only the per-tree JSON dry-run outputs survived. Per the
  planning agent's contingency, the fixtures are fabricated to
  preserve the *shape categories* (TitleCase / snake_TitleCase
  / kebab-case / mixed), not to mirror specific source trees.
  The Generalisation note in the milestone doc confirms this is
  the intended discipline — the trial trees are evidence, not
  the target.
- **snake-medium is sized to fail RED at baseline.** With 17
  files split as 4 high (today: `Foo_Plan`, `Foo_Status`,
  `Foo_Charter`, `Foo_Log` — suffix tokens already in
  `_ROLE_SUFFIXES`) and 13 low (today: `Foo_Architecture`,
  `Foo_M{1..4}`, `Foo_M1_Implementation`, `Foo_M2_Implementation`,
  `Foo_Sketch`, `Foo_Outline`, `Foo_Memo`, `Foo_Brief`,
  `Foo_Implementation`, `Foo_Strategy_v2`), the confidence
  ratio is 4/17 = 24% at baseline. After Phase 6's inference
  broadening (new vocab + `_M\d+` + non-role suffix strip),
  the expected ratio climbs above 50%.
- **project-names dirs have 3 files each, not 1.** A single
  file in `infer_project` lets the common-prefix path dominate
  (e.g. `["foo-spec.md"]` → prefix "foo-spec" → trim to "foo"
  → returns "foo", ignoring the dir name). With 3 files whose
  stems share no prefix (`alpha`/`beta`/`gamma`),
  `os.path.commonprefix` returns "", len < 2, and inference
  falls back to the dir name — which is where normalisation
  lands at Phase 6.

#### Exit criteria

- [x] Every fixture path the Phase-2 tests reference exists.
- [x] Sanitisation grep returns 0 hits across every fixture.
- [x] M6's 271 in-tree tests stay GREEN.
- [x] `docs check docs/` exit 0 (`tests/fixtures/trees/` is
      not a docs root — no `.docs.toml`).
- [x] `ruff` / `format` / `mypy` clean tree-wide.
- [x] Phase 4 RED baseline failures trace to the unimplemented
      surface, not to missing fixtures.

### Phase 4 — Run Tests (RED Baseline)

**Completed:** 2026-05-24

#### Objective

Capture the verbatim RED baseline before any implementation.
Confirm every new RED test fails for its intended unimplemented
reason; surface the GREEN-at-baseline regression locks. Pin
M6's 271 GREEN baseline + the quality gate.

#### Verbatim pytest output

```text
$ .venv/bin/python -m pytest tests/ -q --tb=short
... (315 items collected) ...
34 failed, 281 passed in 7.52s
```

Captured at `/tmp/m7-phase-4-baseline.txt`.

#### Per-test attribution table

| Test group | Source file | RED count | GREEN-at-baseline (regression-lock) count | Failure mode → root cause |
|---|---|---:|---:|---|
| F0 — `Lifecycle:` rename | `test_lifecycle_rename.py` | 5 | 0 | parser only knows `Status:` today / coerces prose `Status:` to vocab |
| F1 — word-boundary + H1 + section + sibling | `test_inference.py` | 4 | 2 | matcher splits only on `-`/`_`; no H1/section/sibling signals; sibling-not-defaulting cases are correctly NOT defaulting today |
| F10 — new core vocab + non-role suffix strip | `test_inference.py` | 10 | 0 | `_Implementation` / `_Sketch` / `_Outline` / `_Memo` / `_Brief` / `_Template` / `_Example` not in `_ROLE_SUFFIXES`; `_v\d+` / `_Draft` not stripped |
| F12 — `_M\d+` milestone suffix | `test_inference.py` | 4 | 1 | `M1` token not in matchers today; `_Log` shape still wins for `_M1_Implementation_Log.md` (regression lock) |
| F11 — project normalisation | `test_project_normalisation.py` | 6 | 2 | no normalisation today: inferred project inherits dir name verbatim; kebab + digit-after-digit cases happen to pass through correctly today |
| F5 — multi-project hints + `--config-project` flag | `test_multi_project_hints.py` | 2 | 1 | no hint emission; argparse rejects `--config-project`; below-threshold case correctly emits no hint today |
| F4 — archive per-file mtime | `test_archive_normalisation.py` | 1 | 3 | `plan_migration` uses single migration-wide `archive_date` for every move today; `archive/`-no-d, `--date` global, already-conformant-no-move are M4 behaviours that remain correct |
| Confidence-distribution success criterion | `test_migrate.py` | 1 | 0 | snake-medium scores 4/17 = 24% < 0.5 today (RED for the intended reason — inference broadening unimplemented) |
| F11 — `--config-project` short-circuits normalisation | `test_project_normalisation.py` | (counted above) | 0 | (covered by F11 row above; the assertion shape is two-checks-in-one: argparse accepts the flag AND human output omits "(normalised from")) |
| **TOTAL** |  | **34** | **10** | — |

(F11 row counts 6 RED including `test_config_project_cli_override_wins_over_normalisation` and `test_migrate_plan_human_output_shows_normalised_from_when_changed`; the `_omits_normalised_from_when_unchanged` case is one of the 2 regression locks in that row.)

#### Quality gate (verbatim)

```text
$ .venv/bin/ruff check .
All checks passed!

$ .venv/bin/ruff format --check .
27 files already formatted

$ .venv/bin/mypy
Success: no issues found in 28 source files

$ .venv/bin/docs check docs/
docs: no violations found
```

#### Attestation — no RED-for-wrong-reason

Every RED test was inspected against its `--tb=short` traceback
(captured at `/tmp/m7-phase-4-baseline.txt`):

- No `ImportError` / `ModuleNotFoundError`.
- No `FileNotFoundError` / fixture-not-found failures.
- No `argparse` errors except the intended `--config-project`
  rejections (which are themselves the RED-for-the-intended-
  unimplemented-surface — `argparse` rejecting an
  unimplemented flag is the contract surface the test pins).
- Every assertion failure message names the contract the
  Phase 5/6 implementation will satisfy.

The 34 REDs partition cleanly: 5 F0 + 18 F1/F10/F12 inference +
6 F11 project + 1 F4 archive + 2 F5 hint/override + 1 F11
human-output + 1 confidence-distribution.

#### Issues / decisions

- **34 RED vs the plan's ~20 RED + ~8 regression-lock target.**
  Parametric expansion on the 7-new-vocab and 4-`_M\d+` cases
  (in particular) yielded more items than the planning agent's
  pre-Phase-2 estimate. Per OQ-1 (operator decision binding,
  2026-05-24): "accept ~20 RED + ~8 GREEN regression-locks; the
  milestone-doc table at line 638-647 can be tightened at
  Phase 4 actuals capture time." Actuals: 34 RED + 10 regression
  locks. The Phase-4 attribution table here is the tightened
  record; the milestone doc's Expected RED Matrix is preserved
  as Phase-2 estimation and not retroactively edited.
- **Sibling-set defaulting RED count is 1.** Only the
  majority-met fixture is RED (the no-suffix files default to
  `notes`/low today). The `sample-too-small` and `no-majority`
  fixtures are GREEN regression locks — those code paths
  remain non-defaulting after Phase 6.
- **No structural surprise.** Every RED's failure message was
  the assertion the test was designed to fail. No fixture
  oversight, no import accident, no off-by-one mismatch.

#### Exit criteria

- [x] Verbatim pytest output captured at
      `/tmp/m7-phase-4-baseline.txt`.
- [x] 271 M6 tests still GREEN.
- [x] 10 new GREEN-at-baseline regression locks.
- [x] 34 RED tests, every one for an intended unimplemented
      surface (per-test attribution table above).
- [x] No RED-for-wrong-reason in the baseline.
- [x] `ruff check`, `ruff format --check`, `mypy`,
      `docs check docs/` all exit 0.
- [x] Phase 2 / 3 / 4 rows in the TDD Phase Progress table
      flipped to Complete with today's date.
- [x] Ready for Phase 5 (Update Base Interfaces — F0 rename +
      Confidence.MEDIUM enum extension).

