# M7 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-05-25

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
| 5. Update Base Interfaces | Complete | 2026-05-25 | **F0 rename landed.** Parser requires `Lifecycle:`; free-form `Status:` becomes a preserved extra field. `Doc.status` → `Doc.lifecycle`; `FileMigration.status` → `FileMigration.lifecycle`; `Config.statuses` → `Config.lifecycles`; `validate_status` → `validate_lifecycle`; TOML key `add_statuses` → `add_lifecycles`. `FileMigration.confidence` extended to `{high, medium, low}` (medium requires empty ambiguities). `Config` grows `role_suffixes: dict` + `project_name: str | None` (consumed at Phase 6). `MigrationPlan` grows `project_original: str \| None` + `multi_project_hints: tuple[str, ...]` (populated at Phase 6). Argparse: `docs list --status` → `--lifecycle`; `docs migrate --config-project NAME` added (consumed at Phase 6). `insert_metadata_block` writes `Lifecycle:`; `scaffold_doc` writes `Lifecycle: draft`; `_archive_one` writes `Lifecycle: archived`. `check_doc` reads `Lifecycle:`. `_REQUIRED_METADATA_FIELDS` swaps `Status` → `Lifecycle` so a free-form `Status:` line lands in the extra-field preservation path. Sweep of `docs/*.md` (29 files) and conformant test-tree fixtures (31 files + `parser/well-formed.md`) via `^Status: <vocab>$` → `^Lifecycle: <vocab>$`. Skill refs resynced (deferred from plan to keep Phase 5 GREEN). pytest: 290 passed / 30 failed (RED for Phase 6 surface — inference broadening, project normalisation, per-file mtime, multi-project hints, medium-confidence check wiring); ruff / format / mypy / docs check / docs index --dry-run all clean. |
| 6. Implement Offline/Core Path | Complete | 2026-05-25 | **F1 / F10 / F11 / F12 / F4 / F5 landed.** `infer_role` now: word-boundary tolerance (splits on `-` / `_` / whitespace / case-transition); 7 new core vocab role suffixes (`_implementation`, `_sketch`, `_outline`, `_memo`, `_brief`, `_template`, `_example`); `_M\d+` milestone-number pattern (medium); `_v\d+`/`_Draft`/`_Ready` non-role suffix strip + re-match (medium). New `normalise_project_name()` splits on case + letter↔digit boundaries; `plan_migration` consults precedence (CLI `--config-project` > `.docs.toml [migrate] project_name` > F11-normalised) and surfaces the `(normalised from "X")` annotation via `MigrationPlan.project_original`. New `_multi_project_hints()` emits one `hint:` line per immediate subdir whose `.md` common prefix differs from the parent project AND covers ≥ 5 files; surfaced through `MigrationPlan.multi_project_hints` and printed in the human plan footer (suppressed when `--config-project` is set). New H1-content / section-header / sibling-set inference helpers run a medium-confidence upgrade pass over `notes`-fallback files. `check_doc` emits a `medium-confidence-inference` warning (exit 1) instead of a `missing-field` error when the missing `Role:` is resolvable via the H1 or section signal. `_cmd_migrate` narrows the `.docs.toml` refusal to managed-root markers (`[project]`, `[archive]`, `[vocabulary]`) so a `[migrate]`-only sidecar is readable; threads `args.config_project` into `plan_migration`; F4 per-file mtime/Updated: drives archive-move dates when `--date` is absent. pytest: **320 / 320 GREEN**. Quality gate clean. |
| 7. Update Tool/Wrapper Layer | Complete | 2026-05-25 | **Specs + CHANGELOG rewritten; v1.2.0 bumped.** convention.md: Required-fields table swaps `Status:` → `Lifecycle:` with a breaking-change callout; new "Status" optional-field row (free-form prose, preserved-not-vocab-checked); Lifecycle section header renamed; Role table gains 7 M7 additions; new "Inference and confidence" section documenting high/medium/low semantics; new "Per-tree `[migrate]` config" section documenting `project_name` and `role_suffixes`; archive subtree rules updated. cli.md: F0 breaking-change callout at top of `docs migrate`; `docs list --status` → `--lifecycle`; `--json` schema field `status` → `lifecycle` in both `docs list` and `docs migrate`; expanded Inference rules (5 passes + word-boundary + case-transition + medium signals + sibling-set); F11 normalisation section with `(normalised from "X")` annotation; F5 multi-project hint section with the literal hint line shape; `--config-project NAME` synopsis added; `docs check` rule list gains `medium-confidence-inference`; exit-code matrix updated. architecture.md: new `config` module section (Config dataclass + `validate_lifecycle` rename + new `[migrate]` fields); `model` Doc.status → Doc.lifecycle; INDEX role-order updated with 7 new roles; `migrate` module — every new inference helper (`normalise_project_name`, `_infer_role_from_h1`, `_infer_role_from_sections`, `_sibling_default`, `_multi_project_hints`) documented; FileMigration.lifecycle / confidence widens; MigrationPlan.project_original / multi_project_hints documented; `__version__ = "1.2.0"`. status.md: "Watch out for" entry for M7's breaking rename + skill-refs lockstep. README.md: lone `Status:` swapped to `Lifecycle:`. CHANGELOG.md: new `## 1.2.0 — UNRELEASED` section above 1.1.0 with Changed (breaking) + Added blocks documenting every M7 feature. pyproject.toml + `__version__` → 1.2.0. Bundled skill refs (`src/docs_cli/skill/references/{convention,cli}.md`) resynced from `docs/`. Updated dates on touched docs bumped to 2026-05-25. `tests/test_packaging.py` version expectations bumped (1.1.0 → 1.2.0; function name `test_a3_project_version_is_1_1_0` → `_1_2_0`). pytest: **320 / 320 GREEN**; `docs --version` → `docs 1.2.0`. |
| 8. Run Tests (GREEN) | Complete | 2026-05-25 | **GREEN gate captured verbatim at `/tmp/m7-phase-8-green.txt`.** pytest: `320 passed in 7.67s`; ruff check + ruff format --check: clean; mypy: `Success: no issues found in 28 source files`; `docs check docs/`: `no violations found`; `docs index --root docs/ --dry-run` diff against `docs/INDEX.md`: empty (exit 0); `docs --version`: `docs 1.2.0`. |
| 9. Implement Online/Integration | Complete | 2026-05-25 | **All 5 success criteria PASS.** New `tests/manual/m7_success_criteria.py` (stdlib-only; lives under `tests/manual/` so pytest does NOT auto-collect it). Per-fixture `docs migrate --json` dumps captured at `/tmp/m7-phase-9/*.json` (5 trees, 117 files total). Measured: **high+medium = 103/117 = 88.0%** (≥ 50%); **notes = 16/117 = 13.7%** (≤ 30%); **archive-subdir fixture archive_move = 5/5 = 100%** (≥ 80%); **distinct project values = 3/3 normalised** (≥ 90%); **free-form `Status:` preservation = 4/4 = 100%** (criterion 3 verified via spot-apply against `tests/fixtures/status-prose/`). pytest still 320/320 GREEN. |
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

**Completed:** 2026-05-24 (post-fresh-eyes-review tightening: 2026-05-25)

#### Objective

Capture the verbatim RED baseline before any implementation.
Confirm every new RED test fails for its intended unimplemented
reason; surface the GREEN-at-baseline regression locks. Pin
M6's 271 GREEN baseline + the quality gate.

#### Verbatim pytest output

Initial Phase-4 capture (2026-05-24):

```text
$ .venv/bin/python -m pytest tests/ -q --tb=short
... (315 items collected) ...
34 failed, 281 passed in 7.52s
```

Captured at `/tmp/m7-phase-4-baseline.txt`.

Post-fresh-eyes-review (2026-05-25): the Step-1 reviewer surfaced
should-fix tightening (strict-medium pinning per OQ-D, parametric
expansion of `test_migrate_preserves_freeform_status` across all 4
status-prose fixtures, new `FileMigration(confidence="medium")`
constructor anchor, new `docs check` exit-1 medium anchor). Net
delta: +5 RED tests (3 from parametric expansion, 1 FileMigration
constructor, 1 `docs check` exit-1 medium anchor). The strict-medium
assertion tightenings on H1 / section / sibling-defaulting /
`_v\d+`-strip categories do not add RED count — they replace the
forward-compatible `(medium, high, True)` sentinel with strict
`"medium"` checks on the first parametric case (so the existing
RED-on-role-mismatch still fires first at baseline; the medium
strictness asserts post-Phase-6).

```text
$ .venv/bin/python -m pytest tests/ -q --tb=short
... (320 items collected) ...
39 failed, 281 passed in 7.44s
```

#### Per-test attribution table

| Test group | Source file | RED count | GREEN-at-baseline (regression-lock) count | Failure mode → root cause |
|---|---|---:|---:|---|
| F0 — `Lifecycle:` rename | `test_lifecycle_rename.py` | 5 (baseline) → 10 (post-review: parametric expansion ×4 prose fixtures + `FileMigration(confidence="medium")` anchor + `docs check` exit-1 medium anchor) | 0 | parser only knows `Status:` today / coerces prose `Status:` to vocab; `FileMigration.__post_init__` rejects `medium`; `docs check` exits 2 on missing required field today |
| F1 — word-boundary + H1 + section + sibling | `test_inference.py` | 4 | 2 | matcher splits only on `-`/`_`; no H1/section/sibling signals; sibling-not-defaulting cases are correctly NOT defaulting today |
| F10 — new core vocab + non-role suffix strip | `test_inference.py` | 10 | 0 | `_Implementation` / `_Sketch` / `_Outline` / `_Memo` / `_Brief` / `_Template` / `_Example` not in `_ROLE_SUFFIXES`; `_v\d+` / `_Draft` not stripped |
| F12 — `_M\d+` milestone suffix | `test_inference.py` | 4 | 1 | `M1` token not in matchers today; `_Log` shape still wins for `_M1_Implementation_Log.md` (regression lock) |
| F11 — project normalisation | `test_project_normalisation.py` | 6 | 2 | no normalisation today: inferred project inherits dir name verbatim; kebab + digit-after-digit cases happen to pass through correctly today |
| F5 — multi-project hints + `--config-project` flag | `test_multi_project_hints.py` | 2 | 1 | no hint emission; argparse rejects `--config-project`; below-threshold case correctly emits no hint today |
| F4 — archive per-file mtime | `test_archive_normalisation.py` | 1 | 3 | `plan_migration` uses single migration-wide `archive_date` for every move today; `archive/`-no-d, `--date` global, already-conformant-no-move are M4 behaviours that remain correct |
| Confidence-distribution success criterion | `test_migrate.py` | 1 | 0 | snake-medium scores 4/17 = 24% < 0.5 today (RED for the intended reason — inference broadening unimplemented) |
| F11 — `--config-project` short-circuits normalisation | `test_project_normalisation.py` | (counted above) | 0 | (covered by F11 row above; the assertion shape is two-checks-in-one: argparse accepts the flag AND human output omits "(normalised from")) |
| **TOTAL** |  | **34** (baseline) → **39** (post-review) | **10** | — |

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

#### Post-review tightening (2026-05-25)

Fresh-eyes reviewer surfaced ALL should-fix and nits across the
five Step-1 commits (`d91cf41` Phase 1 → `cbf274e` audit fixes).
NO blockers. Applied 1-3 commits' worth of fixes:

- **Strict-medium pinning (review finding #1).** Per-category
  `confidence == "medium"` exact assertion (vs the forward-
  compatible `(medium, high, True)` sentinel) on the
  sibling-defaulting majority-met test, the H1-content inference
  test, the section-header pattern test, and the first parametric
  case of non-role-suffix strip (`MyPlan_v2.md`). New CLI exit-code
  anchor `test_check_exits_1_on_medium_confidence_inference` pins
  the OQ-D `medium → warning (exit 1)` contract surface.
- **F10 new-vocab high-only (review finding #2).** Tightened
  `test_infer_role_new_core_vocab_roles` to `conf in ("high", True)`
  — dropped `medium` from the accepted set since OQ-A puts these
  7 roles in the CORE controlled-role vocab → high confidence.
- **F12 `_M01` annotation (review finding #3).** Inline parametrize-
  block comment marking `Foo_M01.md` as the intentional regex-
  coverage addition (not in milestone task plan line 530's list).
- **Multi-project below-threshold robustness (review finding #4).**
  Walk plan output line-by-line, asserting no `hint:`-prefixed
  line names `small-sub` (replaces the brittle substring-in-stdout
  check).
- **`real-trees/README.md` (review finding #5).** Declares the
  four currently-unwired fixtures (`kebab-tiny`, `snake-large`,
  `archive-subdir`, `mixed-naming`) as staged for Phase 9 manual
  dogfooding (`tests/manual/m7_success_criteria.py`, not yet
  created).
- **Operator precedence (review finding #6).** Parenthesised the
  `or`/`and` clause in
  `test_migrate_preserves_freeform_status_as_migrated_metadata`.
- **Filter tightening (review finding #7).** Removed redundant
  `f.rel.endswith(("08.md", "09.md", "10.md"))` clause in
  `test_sibling_set_defaulting_fires_when_majority_met`; keeps
  `"no-suffix" in f.rel` only.
- **Status-prose parametric expansion (review finding #8).**
  Parametrised `test_migrate_preserves_freeform_status` over all
  4 fixtures (`freeform-status.md`, `draft-companion.md`,
  `planning-only.md`, `p0-implemented.md`). +3 RED at baseline.
- **`FileMigration(confidence="medium")` constructor anchor
  (review finding #9).** New
  `test_file_migration_accepts_medium_confidence`. Pins Phase 5
  validator extension as explicit contract surface; RED today on
  `__post_init__`'s `("high", "low")` check.
- **Milestone-doc `architecture` correction (review finding #10).**
  F10 finding table row for `_Architecture` rewritten — `architecture`
  is NOT in the core role vocab; needs `add_roles` per-tree opt-in
  (consistent with the operator rationale that deferred `explainer`).
  OQ-A Decisions block updated to mark both `explainer` and
  `architecture` as `add_roles`-only.
- **Phase-4 expected matrix preamble (review finding #11).**
  Inline note pointing at this log entry's actuals (34 RED + 10
  locks baseline; 39 RED + 10 locks post-review). The milestone
  doc's pre-Phase-2 estimation table is preserved unchanged as
  historical record.

Post-fix counts:

- 320 tests collected (M6's 271 + 49 M7 new).
- 39 failed, 281 passed (39 = 34 baseline RED + 3 prose-fixture
  parametric expansion + 1 FileMigration medium anchor + 1
  `docs check` exit-1 medium anchor; 281 = M6's 271 + 10
  regression locks, unchanged from baseline).
- 0 RED-for-wrong-reason: every failure traces to its intended
  unimplemented surface (parser-only-knows-`Status`,
  `__post_init__` rejects `medium`, missing-field-is-error not
  medium-warning, no broadened inference, no normalisation, no
  multi-project hint, argparse rejects `--config-project`).
- Quality gate: `ruff check`, `ruff format --check`, `mypy`,
  `docs check docs/` all exit 0.

#### Exit criteria

- [x] Verbatim pytest output captured at
      `/tmp/m7-phase-4-baseline.txt`.
- [x] 271 M6 tests still GREEN.
- [x] 10 new GREEN-at-baseline regression locks.
- [x] 34 RED tests at baseline; 39 RED post-review-tightening
      (per-test attribution table above), every one for an
      intended unimplemented surface.
- [x] No RED-for-wrong-reason in the baseline or post-tightening.
- [x] `ruff check`, `ruff format --check`, `mypy`,
      `docs check docs/` all exit 0.
- [x] Phase 2 / 3 / 4 rows in the TDD Phase Progress table
      flipped to Complete with today's date.
- [x] Ready for Phase 5 (Update Base Interfaces — F0 rename +
      Confidence.MEDIUM enum extension).


### Phase 5 — Update Base Interfaces

**Completed:** 2026-05-25

#### Objective

Land M7's F0 rename across every base interface: parser
(`parse()` requires `Lifecycle:` not `Status:`), dataclasses
(`Doc.lifecycle`, `FileMigration.lifecycle`, `Config.lifecycles`),
metadata writers (`scaffold_doc`, `insert_metadata_block`,
`_archive_one`), validators (`validate_lifecycle`, `check_doc`),
JSON serialisers (`doc_to_json`, `migration_to_json`), the
`.docs.toml` reader (`add_statuses` → `add_lifecycles`), and the
argparse CLI surface (`docs list --lifecycle`, `docs migrate
--config-project NAME`). Extend `FileMigration.confidence` to
accept the new `"medium"` sentinel introduced by OQ-D. Add the
Phase-6-consumed `Config.role_suffixes`, `Config.project_name`,
`MigrationPlan.project_original`, and
`MigrationPlan.multi_project_hints` fields with safe defaults.
Sweep every conformant `Lifecycle:` site in this project's own
`docs/`, the conformant fixture trees, and the existing-test
fabricated metadata bodies. Resync the bundled skill references
in lockstep so `tests/test_skill_refs.py` stays GREEN.

#### Files changed

- **src/docs_cli/cli.py** — load-bearing F0 rename:
  - `Doc.status` → `Doc.lifecycle`; docstring rewritten;
    `__post_init__` error message updated.
  - `FileMigration.status` → `FileMigration.lifecycle`;
    `confidence` validator extended to accept `"medium"`
    with empty ambiguities; docstring rewritten.
  - `MigrationPlan` grows `project_original: str | None = None`
    and `multi_project_hints: tuple[str, ...] = ()` with
    defaults — Phase 6 populates them.
  - `Config.statuses` → `Config.lifecycles`; new fields
    `role_suffixes: dict[str, str]` (default `{}`) and
    `project_name: str | None` (default `None`); error message
    in `__post_init__` updated.
  - `validate_status` → `validate_lifecycle`; error message
    now `"Lifecycle: <value> not in vocabulary"`.
  - `parse()` reads `metadata["Lifecycle"]` and the
    required-fields tuple becomes
    `("Lifecycle", "Role", "Updated")`; a free-form `Status:`
    line is harvested into `Doc.extra` like any other
    non-required label (the `known` set drops `"Status"`).
  - `infer_status()` reads `metadata.get("Lifecycle")`
    (function name preserved per OQ3 — Phase 10 simplify
    candidate).
  - `plan_migration()` ambiguity rule rewords as
    `"In-file Lifecycle: <value> is out of vocabulary"`.
  - `apply_migration()` passes `status=fm.lifecycle` into
    `insert_metadata_block` (parameter name preserved).
  - `migration_to_json()` JSON record key `"status"` →
    `"lifecycle"`; `confidence` schema doc updated to
    `high|medium|low`.
  - `doc_to_json()` JSON record key `"status"` → `"lifecycle"`.
  - `_print_migration_plan()` per-file line now prints
    `lifecycle: <val>` (not `status:`); hint / normalisation
    annotation hooks land at Phase 6.
  - `_REQUIRED_METADATA_FIELDS` swaps `"Status"` → `"Lifecycle"`
    so `_extra_metadata_fields` catches free-form `Status:`.
  - `insert_metadata_block` writes `Lifecycle: <val>` (block
    template rewritten; parameter still named `status` per
    OQ3).
  - `scaffold_doc()` writes `Lifecycle: draft`.
  - `_archive_one()` writes `Lifecycle: archived`.
  - `check_doc()` reads `Lifecycle:`; messages reworded;
    docstring updated.
  - `query_docs()` parameter `status` → `lifecycle`; sort key
    uses `d.lifecycle`.
  - `_cmd_list()` passes `lifecycle=args.lifecycle`; group
    header prints `lifecycle — role`.
  - `load_config()` reads `add_lifecycles` (no
    `add_statuses` alias); reads the new `[migrate]` section's
    `role_suffixes` map + `project_name`.
  - argparse: `docs list --status` → `--lifecycle`;
    `docs migrate --config-project NAME` added.
- **tests/_typing/docs.pyi** — unchanged (re-exports
  `Doc`/`Config`/`FileMigration` via `import *`; attribute
  shapes flow through automatically).
- **tests/test_lifecycle_rename.py** — Phase 2 RED tests
  updated to assert `doc.lifecycle` and to construct
  `FileMigration(..., lifecycle=...)`. All 5 baseline tests
  flip RED → GREEN at Phase 5.
- **tests/test_config.py** — TOML key `add_statuses` →
  `add_lifecycles`; `cfg.statuses` → `cfg.lifecycles`.
- **tests/test_check.py**, **tests/test_index.py**,
  **tests/test_walker.py** — `Config(... statuses=...)`
  keyword renamed to `lifecycles=...`.
- **tests/test_index.py** — `_doc()` helper now constructs
  `Doc(..., lifecycle=status, ...)`; helper param name
  preserved.
- **tests/test_query.py** — `_q()` helper passes `lifecycle=`
  to `query_docs`; assertions read `d.lifecycle`.
- **tests/test_model.py, test_check.py, test_edit.py,
  test_cli_check.py, test_cli_new.py, test_cli_archive.py** —
  fabricated conformant-doc bodies' `Status:` lines swapped
  to `Lifecycle:`. Error-path tests
  (`test_parse_missing_status`, `test_parse_unknown_status`)
  update the regex match to `"Lifecycle"`.
- **tests/test_migrate.py** — `infer_status` tests'
  metadata-fabrication keys swap `Status` → `Lifecycle` (the
  function still NAMED `infer_status` per OQ3, but reads
  `Lifecycle:` internally). Foreign-tree `Status: wip`
  fabrications kept verbatim (they exercise the new
  extra-field preservation path); assertions about the
  inserted block updated:
  `metadata["Status"]` → `metadata["Lifecycle"]`;
  `Migrated-Status: wip` now expected in
  `## Migrated metadata`. `_extra_metadata_fields` set
  assertion swaps to `{"Lifecycle", "Role", "Project",
  "Updated"}`. `confidence in ("high", "low")` extends to
  `("high", "medium", "low")` in cli-json schema test.
- **tests/test_cli_list.py** — `--status` flag → `--lifecycle`;
  JSON schema key `status` → `lifecycle`.
- **tests/test_cli_migrate.py** — JSON expected-keys set:
  `"status"` → `"lifecycle"`; confidence value set widens to
  `("high", "medium", "low")`.
- **docs/*.md** (29 files swept) — every conformant
  `^Status: <vocab>$` metadata line renamed to
  `^Lifecycle: <vocab>$`. Body-prose `Status:` mentions
  (M1–M5 historical narrative) untouched per OQ10.
- **tests/fixtures/trees/{with-archive,nested,minimal,
  multi-project,cross-refs,drift,marker-preservation,
  invalid}/** (31 files) — conformant metadata `Status:` →
  `Lifecycle:` (`invalid/bad-status.md` keeps the
  out-of-vocab value `frobnicated` but on the renamed
  `Lifecycle:` key). Foreign fixtures
  (`trees/foreign/`, `status-prose/`, `project-names/`,
  `lifecycle/status-only.md`) preserved verbatim.
- **tests/fixtures/parser/well-formed.md** — renamed in
  lockstep.
- **src/docs_cli/skill/references/{convention,cli}.md** —
  resynced from `docs/{convention,cli}.md` (the byte-equality
  test pins the lockstep; deferring this to Phase 7 would
  leave 2 tests RED at Phase 5).
- **docs/INDEX.md** + **tests/fixtures/expected/docs-INDEX.md** —
  regenerated in lockstep via `docs index --root docs/`.

#### Test status at Phase 5 close

```text
$ .venv/bin/python -m pytest tests/ -q
... 30 failed, 290 passed in 7.60s ...
```

- 320 collected (unchanged).
- 290 passed: M6's 271 + 9 new GREEN (test_lifecycle_rename's
  5 F0 baseline tests + the 4 prose-fixture parametric F0
  preservation cases + the `FileMigration` medium-confidence
  anchor — count includes some test_inference.py regression
  locks that were green at baseline). Specifically the 9 new
  Phase-5 flips are: 5 test_lifecycle_rename tests
  (`test_parse_accepts_lifecycle_key`,
  `test_parse_rejects_status_as_controlled_vocab_key`,
  `test_check_errors_on_status_without_lifecycle`,
  `test_check_accepts_lifecycle_with_freeform_status_line`,
  `test_file_migration_accepts_medium_confidence`); 4
  `test_migrate_preserves_freeform_status_as_migrated_metadata`
  parametric cases.
- 30 failed: all Phase-6 surfaces — `test_inference.py`
  word-boundary / suffix-strip / new-vocab / `_M\d+` /
  H1-content / section-header / sibling defaulting (17 tests);
  `test_project_normalisation.py` TitleCase / SNAKE_UPPER /
  mixed underscore / single-word / digit-glued normalisation +
  `--config-project` override + human-output "(normalised
  from …)" annotation (7 tests);
  `test_archive_normalisation.py` per-file mtime drives
  archive date (1 test); `test_multi_project_hints.py`
  emission + override (2 tests);
  `test_lifecycle_rename.test_check_exits_1_on_medium_confidence_inference`
  medium-confidence check-time wiring (1 test);
  `test_migrate.test_confidence_distribution_meets_threshold`
  ≥ 50% high+medium dogfood metric (1 test). One additional
  inference regression-lock case
  (`test_infer_role_strips_non_role_suffixes[MyPlan_v2.md-True]`)
  failing for the strict-medium anchor that's still on the
  Phase-6 surface.

- Quality gate: `ruff check`, `ruff format --check`, `mypy`,
  `docs check docs/`, `docs index --dry-run` all exit 0.

#### Exit criteria

- [x] Parser requires `Lifecycle:` (not `Status:`); free-form
      `Status:` becomes a preserved extra field.
- [x] `Doc.status` → `Doc.lifecycle`; `FileMigration.status`
      → `FileMigration.lifecycle`;
      `FileMigration.confidence` accepts `medium`.
- [x] `Config.statuses` → `Config.lifecycles`; new fields
      `role_suffixes` + `project_name` with safe defaults.
- [x] `MigrationPlan.project_original` +
      `multi_project_hints` fields added with safe defaults.
- [x] `validate_status` → `validate_lifecycle`;
      `add_statuses` → `add_lifecycles` in TOML reader.
- [x] argparse: `docs list --lifecycle` (single rename),
      `docs migrate --config-project NAME` added.
- [x] All conformant `^Status: <vocab>$` lines in
      `docs/*.md`, `tests/fixtures/trees/` and
      `tests/fixtures/parser/` renamed; `grep -l "^Status:"
      docs/` empty. Foreign-tree fixtures preserved verbatim.
- [x] All existing-test conformant fabrications renamed;
      foreign-tree fabrications preserved.
- [x] Skill refs resynced via byte-copy.
- [x] `docs/INDEX.md` regenerated and
      `tests/fixtures/expected/docs-INDEX.md` byte-equal.
- [x] pytest: 290 passed, 30 failed (every failure on the
      Phase-6 surface). Quality gate clean. No
      RED-for-wrong-reason.

### Phase 6 — Implement Offline/Core Path

**Completed:** 2026-05-25

#### Objective

Land the broadened inference (F1, F10, F12), project-name
normalisation (F11), per-file mtime archive dates (F4),
multi-project hint emission (F5), and the medium-confidence
wiring into `check_doc`. All 30 Phase-5-residual RED tests
flip GREEN; the regression locks stay GREEN; M6's 271 stay
GREEN. Total: 320 / 320.

#### Files changed

- **src/docs_cli/cli.py**:
  - `CANONICAL_ROLE_ORDER` and `BUILTIN_ROLES` extended with
    the 7 OQ-A core roles (`implementation`, `sketch`,
    `outline`, `memo`, `brief`, `template`, `example`).
    Position: between `idea` and `notes` so `notes` stays
    the catch-all tail (the INDEX renderer's role-order
    iteration relies on this).
  - `_ROLE_SUFFIXES` extended with same-key entries for the
    7 new roles so the direct-suffix match path catches
    them.
  - `infer_role()` rewritten:
    * Pass 1 (in-file `Role:` line, high) preserved.
    * Pass 2 — direct suffix match via `_match_direct(stem)`.
      Tokeniser now splits on `-` / `_` / whitespace AND
      case-transition (`MyPlan` → `My Plan` → tokens
      `[My, Plan]` → suffix `plan`). Word-boundary
      tolerance (F1).
    * Pass 3 — `_M\d+` (case-insensitive, leading zeros
      allowed): `("milestone", "medium")` (F12).
    * Pass 4 — strip `_v\d+` / `_Draft` / `_Ready` and
      re-run Pass 2 on the stripped stem; medium confidence
      (F10).
    * Pass 5 — `("notes", False)` fallback (preserved).
    * Signature widened: optional `config: Config | None`
      keyword extends `_ROLE_SUFFIXES` with
      `config.role_suffixes` when given. Default `None`
      keeps the unit-test direct-callers' shape unchanged.
    * Return-type widened: `tuple[str, bool | str]` — `True`
      for high, `"medium"` for derived, `False` for notes
      fallback. Matches `_CONFIDENCE_OK` test sentinel and
      preserves the M4 high-confidence test assertions.
  - New `normalise_project_name()` helper: splits on case
    boundaries (`FooBar` → `Foo-Bar`), letter↔digit
    boundaries (`Abc5Mig` → `Abc-5-Mig`), and underscores;
    lowercases; collapses repeats; trims dashes. Digit-
    after-digit is NOT a split point (date-like sequences
    such as `2026-01-26` survive intact). F11 / OQ-B.
  - New `_ROLE_WORDS_TO_ROLES` mapping (H1-trailing-word →
    role hint) and `_infer_role_from_h1()` helper.
    Longest-match wins (`"specification"` beats `"spec"`);
    the trailing word must be on a word boundary
    (whitespace before it) so `# Foospec` does NOT match.
  - New `_infer_role_from_sections()` helper: pattern-matches
    top-level `## ` headings — plan shape
    (`Goal` + `Scope` + `Requirements` or `Goal` + `Exit
    criteria`); status shape (`Current state` + `Progress`
    or `Updates`); decision/ADR shape
    (`Context` + `Decision` + `Consequences`); log shape
    (≥ 2 dated `## YYYY-MM-DD` headings).
  - New `_sibling_default()` helper: returns the modal sibling
    role when ≥ 60% of ≥ 5 same-subdir suffix-confident
    files share it (OQ-C). Notes-fallback files do NOT
    seed the pool so the defaulting is not self-reinforcing.
  - New `_multi_project_hints()` helper: per-subdir
    longest-common-prefix; trims back to last `-`/`_`;
    requires ≥ 2 chars and ≥ 5 `.md` files. Emits one
    `"hint: subdir '<name>'/ looks like a separate project
    (common prefix '<prefix>', N .md files). Migrate it
    independently: docs migrate <name>/ --config-project
    <candidate>"` line. The candidate name is the
    file-prefix candidate (OQ6 — file naming is the
    Trial-2-measured signal).
  - `plan_migration()` rewritten:
    * Signature gains `cli_config_project: str | None`
      keyword.
    * F11 project-name precedence: CLI override > config
      `[migrate] project_name` > F11-normalised(inferred).
    * `MigrationPlan.project_original` carries the
      pre-normalisation name iff normalisation changed it
      (and no override was in force).
    * F4 archive date: when `archive_date` is `None`, each
      file's archive_move uses the resolved `Updated:`/mtime
      date; with an explicit `archive_date` the global value
      wins (preserves the regression-lock tests).
    * `infer_role()` called with `config` (per-tree
      `role_suffixes` override).
    * Tri-state `role_conf`: `False` → notes fallback
      ambiguity + low; `"medium"` → medium confidence
      (no ambiguity); `True` → high.
    * Medium-confidence upgrade pass: for every file whose
      role landed at `notes` with the notes-fallback as
      one of its ambiguities, read the file text and try
      `_infer_role_from_h1` → `_infer_role_from_sections` →
      `_sibling_default(rel, sibling_roles)`. When a real
      role is found, drop the notes-fallback ambiguity and
      promote to medium (or stay low if other ambiguities
      remain). Only suffix-high-confidence files seed the
      sibling pool.
    * F5 hints: emit `_multi_project_hints(root, project)`
      onto `MigrationPlan.multi_project_hints` unless the
      CLI `--config-project` override is in force.
  - `_print_migration_plan()`: prints the
    `project: <final> (normalised from "<original>")`
    annotation ONCE at the top when
    `plan.project_original` is set; appends every
    `plan.multi_project_hints` line in the plan footer.
  - `_cmd_migrate()`:
    * `.docs.toml` refusal narrowed (OQ5): only when the
      file carries `[project]`, `[archive]`, or
      `[vocabulary]` sections does migrate refuse. A
      `[migrate]`-only sidecar (e.g.
      `[migrate] project_name = "foo"`) is read.
    * Threads `args.config_project` into `plan_migration`.
    * `--date` absent now passes `archive_date=None` to
      `plan_migration` so per-file F4 dates apply; an
      explicit `--date` continues to override globally.
  - `check_doc()`: missing `Role:` with a medium-confidence
    H1 or section signal now emits a `Finding(severity=
    "warning", rule="medium-confidence-inference", ...)`
    instead of the hard `missing-field` error. Wires the
    OQ-D exit-code-1-on-medium contract via the existing
    `exit_code_for()` mapping (warning-only ⇒ 1).

- **tests/test_model.py:** `BUILTIN_ROLES` size expectation
  updated from `13` to `20` (7 new core roles).

#### Test status at Phase 6 close

```text
$ .venv/bin/python -m pytest tests/ -q
... 320 passed in 7.54s ...
```

- 320 collected, 320 passed.
- All 30 Phase-5-residual RED tests flipped GREEN:
  `test_inference.py` (17 tests including the strict-medium
  pinning anchors), `test_project_normalisation.py` (7
  tests: 4 TitleCase / SNAKE_UPPER / mixed underscore /
  single-word + 1 digit-glued + 1 `--config-project`
  override + 1 normalised-from human-output annotation),
  `test_archive_normalisation.py::test_archived_subdir_generates_move_with_mtime_date`
  (1 test), `test_multi_project_hints.py` (2 tests:
  emission + override), `test_lifecycle_rename.py::
  test_check_exits_1_on_medium_confidence_inference`
  (1 test), `test_migrate.py::
  test_confidence_distribution_meets_threshold` (1 test —
  the dogfood ≥ 50% (high+medium) ratio).
- All 10 regression-lock tests stay GREEN: `_M\d+`-with-
  `_Log` combination → `log`; sibling-not-defaulting × 2
  (sample too small + no majority); kebab + digit-after-
  digit pass-through × 2; multi-project hint
  below-threshold; archive `no-d` shape; `--date` global
  override; already-conformant archive no-move;
  `(normalised from …)` omitted-when-unchanged.
- M6's 271 GREEN tests preserved.

#### Confidence distribution on snake-medium dogfood

`test_confidence_distribution_meets_threshold` passes: the
`tests/fixtures/trees/real-trees/snake-medium/` fixture's
17 files produce ≥ 50% high+medium under the new inference
(measured: 88% high+medium per the milestone task plan's
Phase 6 calculation — 9 high from direct suffix matches +
6 medium from `_M\d+` / post-strip / H1 / section / sibling
signals).

#### Exit criteria

- [x] `infer_role()` returns `True`/`"medium"`/`False`;
      word-boundary, `_M\d+`, non-role-suffix-strip all
      land at their pinned confidence (strict-medium
      anchors pass).
- [x] 7 new core vocab roles added to
      `CANONICAL_ROLE_ORDER` + `_ROLE_SUFFIXES`.
- [x] `normalise_project_name()` produces lowercase-kebab
      per OQ-B (case, letter↔digit, snake_upper);
      digit-after-digit preserved (`2026-01-26` survives).
- [x] CLI `--config-project` > `.docs.toml [migrate]
      project_name` > F11-normalised(inferred) precedence
      threaded through `plan_migration` and consumed by
      every plan record.
- [x] Per-file mtime/Updated: drives archive-move dates
      when `--date` is absent; explicit `--date` still
      overrides globally.
- [x] Multi-project hint emitted in plan footer when
      threshold met; suppressed when `--config-project`
      is set.
- [x] H1-content / section-header / sibling-set medium-
      confidence upgrade pass populates the right roles
      and confidences.
- [x] `check_doc()` `medium-confidence-inference` warning
      lands on exit-1; missing-field-error semantics
      preserved when no medium signal exists.
- [x] `.docs.toml` refusal narrowed to managed-root markers
      (OQ5).
- [x] pytest 320 / 320 GREEN. Quality gate clean.

### Phase 7 — Update Tool/Wrapper Layer

**Completed:** 2026-05-25

#### Objective

Document M7's surface in every user-facing spec so the agent
reading `docs install-skill`'s materialised skill and the
operator reading `docs/` see the same set of facts. Bump the
version to 1.2.0 and resync the bundled skill references in
lockstep. No code changes; no test status change.

#### Files changed

- **docs/convention.md:** Required-fields table swaps to
  `Lifecycle:` with a breaking-change callout pointing at
  `dual-status-adr.md`; new "Status" optional-field row
  (free-form prose, preserved verbatim, not vocab-checked);
  Lifecycle section header renamed from "Status (built-in)"
  to "Lifecycle (built-in)"; Role table gains 7 M7 additions
  (`implementation`, `sketch`, `outline`, `memo`, `brief`,
  `template`, `example`) with an "M7 — F10 / OQ-A" anchor;
  new "Inference and confidence" section documenting
  high/medium/low semantics + the OQ-D exit-1-on-medium
  contract; new "Per-tree `[migrate]` config" section
  documenting `project_name` + `role_suffixes` + the OQ5
  sidecar-shape narrow-refusal; archive subtree rules
  updated to `Lifecycle:` (with `status-drift` rule id
  preserved); `[vocabulary] add_lifecycles` TOML key noted
  as renamed without alias.

- **docs/cli.md:** F0 breaking-change callout at top of
  `docs migrate`; `docs list` synopsis flag renamed
  `--status` → `--lifecycle` (no alias note); `--json`
  schema rows `status` → `lifecycle` in BOTH `docs list`
  and `docs migrate` schemas; expanded Inference rules
  describing all 5 passes (in-file Role: high → suffix
  match high → `_M\d+` medium → strip + retry medium →
  H1/section/sibling medium → notes low); F11 normalisation
  section with the literal `(normalised from "X")` shape;
  F5 multi-project hint section with the literal hint line
  shape (`hint: subdir 'X/' looks like a separate project
  (common prefix 'P', N .md files). Migrate it
  independently: docs migrate X/ --config-project Y`);
  `--config-project NAME` synopsis added with precedence
  chain (CLI > sidecar > inferred-and-normalised);
  `docs check` rule list gains
  `medium-confidence-inference`; exit-code matrix updated
  with the medium → exit 1 path. `.docs.toml` refusal
  narrowed-to-managed-root-markers documented (OQ5).

- **docs/architecture.md:** New `config` module section
  (Config dataclass + `lifecycles` field + new `[migrate]`
  fields + `validate_lifecycle` rename); `model` Doc.status
  → Doc.lifecycle; `__version__` → 1.2.0; INDEX role-order
  updated to include the 7 new core roles between `idea`
  and `notes`; `migrate` module section — every new
  inference helper (`normalise_project_name`,
  `_infer_role_from_h1`, `_infer_role_from_sections`,
  `_sibling_default`, `_multi_project_hints`) documented
  with its signature, purpose, and OQ anchor;
  `FileMigration.lifecycle` + `confidence` widening
  documented; `MigrationPlan.project_original` +
  `multi_project_hints` documented; `archive` module note
  updated for the lifecycle edit.

- **docs/status.md:** "Watch out for" gotcha entry for M7
  (the on-disk rename + skill-refs lockstep test).

- **README.md:** the lone `Status:` line in the example
  metadata block swapped to `Lifecycle:`.

- **CHANGELOG.md:** new `## 1.2.0 — UNRELEASED` section
  inserted ABOVE the existing `## 1.1.0 — UNRELEASED`
  section. Documents every M7 surface — Changed (breaking)
  block: F0 rename + flag rename + JSON schema field
  rename + TOML key rename. Added block: medium confidence,
  7 new core role additions, F11 normalisation, per-file
  archive-move dates (F4), multi-project hints (F5),
  `--config-project NAME` (F5), `[migrate] role_suffixes`
  (F1), broadened role inference (F1/F10/F12). Notes
  block: Trial-2 measurements, OQ5 sidecar shape.

- **pyproject.toml:** `version = "1.1.0"` → `"1.2.0"`.
- **src/docs_cli/cli.py:** `__version__ = "1.1.0"` →
  `"1.2.0"`.
- **tests/test_packaging.py:** every `1.1.0` literal
  swapped to `1.2.0` (A3 / B1 / B2 / C2 wheel-name,
  sdist-name, `docs --version` token, function name
  `test_a3_project_version_is_1_1_0` →
  `test_a3_project_version_is_1_2_0`).

- **src/docs_cli/skill/references/convention.md** +
  **src/docs_cli/skill/references/cli.md** — resynced from
  `docs/` via byte-copy. `tests/test_skill_refs.py`
  enforces lockstep.

- **docs/INDEX.md** + **tests/fixtures/expected/docs-INDEX.md**
  — regenerated in lockstep (Updated: dates bumped for the
  4 touched docs: convention.md, cli.md, architecture.md,
  status.md, plus the M7 log).

#### Test status at Phase 7 close

```text
$ .venv/bin/python -m pytest tests/ -q
... 320 passed in 7.55s ...
```

- 320 / 320 GREEN. No test count change at Phase 7 (the
  packaging tests' version assertions flipped from `1.1.0`
  to `1.2.0`; the skill-refs lockstep test re-verified
  after the resync).
- `docs --version` prints `docs 1.2.0`.
- Quality gate: `ruff check`, `ruff format --check`,
  `mypy`, `docs check docs/`, `docs index --dry-run` all
  exit 0.

#### Exit criteria

- [x] convention.md documents the `Lifecycle:` rename, the
      7 new core role additions, the medium confidence
      semantic, the `[migrate]` per-tree config, and the
      `add_lifecycles` rename.
- [x] cli.md documents the F0 breaking change, the
      `--lifecycle` flag rename, the `--config-project` flag,
      the full inference cascade, the F11 normalisation
      annotation, the F5 multi-project hint footer, and the
      new `medium-confidence-inference` rule.
- [x] architecture.md adds the `config` module section and
      every new migrate helper.
- [x] status.md carries the M7 watch-out entry.
- [x] README.md `Status:` swept to `Lifecycle:`.
- [x] CHANGELOG.md `## 1.2.0 — UNRELEASED` section in place
      above 1.1.0.
- [x] pyproject.toml + cli.py `__version__` at 1.2.0.
- [x] tests/test_packaging.py version expectations bumped.
- [x] Skill refs at `src/docs_cli/skill/references/` byte-
      equal to `docs/`.
- [x] docs/INDEX.md regenerated; fixture snapshot byte-equal.
- [x] pytest 320 / 320 GREEN; quality gate clean.

### Phase 8 — Run Tests (GREEN)

**Completed:** 2026-05-25

#### Objective

Capture the GREEN gate verbatim at `/tmp/m7-phase-8-green.txt`
so the implementation log carries a reproducible artefact of
M7's clean-tree state, then commit a thin log-only commit
marking the gate.

#### Verbatim quality-gate output (`/tmp/m7-phase-8-green.txt`)

```text
=== pytest tests/ -q ===
........................................................................ [ 22%]
........................................................................ [ 45%]
........................................................................ [ 67%]
........................................................................ [ 90%]
................................                                         [100%]
320 passed in 7.67s

=== ruff check . ===
All checks passed!

=== ruff format --check . ===
27 files already formatted

=== mypy ===
Success: no issues found in 28 source files

=== docs check docs/ ===
docs: no violations found

=== docs index --root docs/ --dry-run | diff - docs/INDEX.md ===
exit=0

=== docs --version ===
docs 1.2.0
```

#### Exit criteria

- [x] pytest 320 / 320 GREEN.
- [x] `ruff check .` clean.
- [x] `ruff format --check .` clean.
- [x] `mypy` Success.
- [x] `docs check docs/` exit 0.
- [x] `docs index --root docs/ --dry-run` byte-equals
      `docs/INDEX.md`.
- [x] `docs --version` prints `docs 1.2.0`.
- [x] Verbatim output captured at
      `/tmp/m7-phase-8-green.txt`; the count reproduced in
      this log entry.

### Phase 9 — Dogfood Trial 2 fixtures

**Completed:** 2026-05-25

#### Objective

Codify M7's 5 quantitative success criteria as an
operator-runnable aggregator script, then exercise it against
every sanitised real-tree fixture under
`tests/fixtures/trees/real-trees/`. Confirm that the M7
inference broadening lifts the Trial-2-measured 25.3%
high-confidence baseline above the 50% high+medium threshold,
and that the new normalisation / archive / preservation
surfaces hit their pinned thresholds.

#### Artefacts

- **`tests/manual/m7_success_criteria.py`** (new, ~110 lines,
  stdlib-only). Lives under `tests/manual/` per OQ9 so pytest
  auto-collection does NOT pick it up (it is an operator
  artefact, not a unit test — the unit-test embodiment of
  criterion 1 already lives at
  `test_migrate.py::test_confidence_distribution_meets_threshold`).
  Loads any number of `--json` migration-plan dumps, computes
  the 5 criteria, prints a PASS / FAIL block, exits 0 on
  unanimous PASS / 1 otherwise.
- **`/tmp/m7-phase-9/*.json`** — per-fixture `docs migrate
  --json` dumps:
  - archive-subdir.json
  - kebab-tiny.json
  - mixed-naming.json
  - snake-large.json
  - snake-medium.json

#### Measured results

```text
$ .venv/bin/python tests/manual/m7_success_criteria.py /tmp/m7-phase-9/*.json
Total files across 5 fixtures: 117
  1. high+medium / total: 103/117 = 88.0%
  2. notes / total:        16/117 = 13.7%
  5. normalised project values: 3/3 = 100.0%

Per-tree archive proposals (criterion 4):
  archive-subdir: 5/5 in-archive files have archive_move = 100.0% [OK]
  kebab-tiny: no archive-style files (criterion 4 not applicable)
  mixed-naming: no archive-style files (criterion 4 not applicable)
  snake-large: no archive-style files (criterion 4 not applicable)
  snake-medium: no archive-style files (criterion 4 not applicable)

Pass/Fail summary:
  Criterion 1 (high+medium >= 50%): PASS
  Criterion 2 (notes <= 30%):       PASS
  Criterion 4 (archive >= 80%):     PASS
  Criterion 5 (normalised >= 90%):  PASS
  Criterion 3 (Status: preservation): see Phase 9 log spot-apply
```

**Criterion 3 spot-apply** (free-form `Status:` preservation):
copied the 4 fixtures in `tests/fixtures/status-prose/` into a
tmp dir, ran `docs migrate --apply --quiet`, then grepped each
applied file for `Migrated-Status:`:

```text
free-form Status: preservation: 4/4
```

All 5 quantitative success criteria PASS:

| # | Criterion | Threshold | Measured |
|---|---|---|---|
| 1 | (high + medium) / total | ≥ 50% | **88.0%** (103/117) |
| 2 | notes / total | ≤ 30% | **13.7%** (16/117) |
| 3 | free-form `Status:` preservation | 100% | **100%** (4/4) |
| 4 | archive-subdir archive_move rate | ≥ 80% | **100%** (5/5) |
| 5 | distinct project values lowercase-kebab | ≥ 90% | **100%** (3/3) |

#### Notes

- The Trial-2 baseline was 25.3% high-confidence under M4
  inference. M7 lifts the same `snake-medium`-shape fixture to
  88% (high + medium) — a ~62-point margin over the 50%
  threshold and a ~22-point margin even compared to the
  60% stretch goal mentioned in the milestone plan.
- The 16 `notes` fallbacks (13.7%) are concentrated in
  `snake-large/` (large monorepo-style component spec sets
  whose filename shape doesn't match any role-word vocab —
  fully expected and within budget).
- 3 distinct project values come from 5 fixtures: `archive-
  subdir` / `kebab-tiny` / `snake-large` / `snake-medium`
  all infer to `foo`-prefixed projects; `mixed-naming` infers
  to a single shared common-prefix value too. All three are
  already lowercase-kebab so no normalisation annotation
  fired.
- `tests/manual/m7_success_criteria.py` is checked in for
  re-running on demand against any future `--json` dump set.

#### Exit criteria

- [x] `tests/manual/m7_success_criteria.py` exists; stdlib
      only; not pytest-collected.
- [x] Per-fixture JSON dumps captured at
      `/tmp/m7-phase-9/*.json` (5 trees).
- [x] All 5 quantitative success criteria PASS with
      measured values inside the milestone log.
- [x] pytest 320 / 320 GREEN; quality gate clean.
