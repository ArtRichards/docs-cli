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
- Progress: **Milestone-setup phase complete; Phase 1 in
  progress.** The task plan
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
| 1. Define Contract | In progress | 2026-05-24 | Promote M7 from `draft` to `active` (done); create this log (done); record OQ A–D resolutions as Decisions in the task plan (done); update status.md "Current milestone" to mark M7 setup complete + Phase 2 next. No code change; no convention change. Regenerate INDEX + snapshot. |
| 2. Write Tests (RED) | Pending | — | New test files: `test_lifecycle_rename.py` (6 tests, F0), `test_inference.py` (9 tests, F1/F10/F12), `test_project_normalisation.py` (per-fixture, F11), `test_archive_normalisation.py` (4 tests, F4). Extension to `test_migrate.py`: confidence-distribution test. All RED for intended unimplemented surface; M6's 271 stay GREEN. |
| 3. Create Data/Fixtures | Pending | — | Promote 5 Trial-2 trees to `tests/fixtures/trees/real-trees/` (kebab-tiny / snake-medium / snake-large / archive-subdir / mixed-naming). Aggressive sanitisation — no third-party product / customer / feature names. Plus small single-file fixtures under `tests/fixtures/status-prose/`, `tests/fixtures/project-names/`, `tests/fixtures/sibling-defaulting/`. |
| 4. Run Tests (RED Baseline) | Pending | — | Capture verbatim pytest output. Expected: M6's 271 GREEN + ~25 M7 RED for intended reasons (no `Lifecycle:` parser, no broadened inference, no normalisation, no archive moves). Quality gate clean tree-wide. |
| 5. Update Base Interfaces | Pending | — | **The F0 rename.** Parser accepts only `Lifecycle:`; `Status:` becomes a free-form extra field. Add `Confidence.MEDIUM`. Add `Config.role_suffixes` + `Config.project_name` + rename `add_statuses` → `add_lifecycles`. Argparse adds `--config-project` to `docs migrate` (F5). **No rename helper shipped** — sweep this project's own `docs/` (27 files) with one-off `sed -i 's/^Status: \(active\|draft\|superseded\|archived\)$/Lifecycle: \1/' docs/*.md`. Update convention.md. F0 tests flip RED → GREEN; rest stay RED for Phase 6. |
| 6. Implement Offline/Core Path | Pending | — | F1 (word-boundary tolerance, H1 + section signals, sibling defaulting), F10 (vocab additions, non-role suffix stripping), F11 (project-name normalisation + override), F12 (`_M\d+` milestone suffix), F4 (archive normalisation), F5 (multi-project hint emission in `migrate_plan` + `--config-project` honoured). All M7 RED tests turn GREEN. |
| 7. Update Tool/Wrapper Layer | Pending | — | convention.md (rename + new vocab + medium confidence + `add_statuses` → `add_lifecycles`), cli.md (F0 breaking note + `--config-project` synopsis + project-normalisation output shape + multi-project hint footer shape + `docs check` exit-code clarification), architecture.md (Config schema), status.md ("Watch out for" entry), README.md (any `Status:` references swept to `Lifecycle:`), CHANGELOG.md (`## 1.2.0 — UNRELEASED`), pyproject.toml + cli.py `__version__` bumped to 1.2.0, src/docs_cli/skill/references/{convention,cli}.md resynced. |
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
| `tests/fixtures/trees/real-trees/{kebab-tiny,snake-medium,snake-large,archive-subdir,mixed-naming}/` | Create | 3 | 5 sanitised Trial-2 trees. |
| `tests/fixtures/{status-prose,project-names,sibling-defaulting}/` | Create | 3 | Small single-file fixtures per finding. |
| `src/docs_cli/cli.py` | Modify | 5, 6, 7 | Phase 5: F0 parser rename + Confidence enum + `add_statuses` → `add_lifecycles` Config rename + `--config-project` argparse addition (F5). Phase 6: F1/F10/F11/F12/F4/F5 inference + normalisation + archive normalisation + multi-project hint emission. Phase 7: `__version__` bumped to 1.2.0. |
| `docs/convention.md` | Modify | 5, 7 | Phase 5: rename `Status:` → `Lifecycle:` in the schema. Phase 7: document new vocab + medium confidence + `[migrate]` config knobs. |
| `docs/cli.md` | Modify | 7 | F0 breaking-change note at the top of the migrate verb section; `--config-project <name>` synopsis + example (F5); project-normalisation output shape; multi-project hint footer shape; `docs check` exit-code clarification for medium confidence. |
| `docs/architecture.md` | Modify | 7 | `Config` schema includes `role_suffixes` + `project_name`. |
| `README.md` | Modify | 7 | Any `Status:` references swept to `Lifecycle:`. |
| `CHANGELOG.md` | Modify | 7, 10 | Phase 7: `## 1.2.0 — UNRELEASED` entry. Phase 10: dated. |
| `pyproject.toml` | Modify | 7 | `version = "1.2.0"`. |
| `src/docs_cli/skill/references/convention.md` | Modify | 7 | Resync from `docs/convention.md`. |
| `src/docs_cli/skill/references/cli.md` | Modify | 7 | Resync from `docs/cli.md`. |
| Every `docs/*.md` Status: line | Modify | 5 | Mechanical one-off sweep via `sed -i 's/^Status: \(active\|draft\|superseded\|archived\)$/Lifecycle: \1/' docs/*.md` (no shipped helper). ~25 files touched. Verify with `grep -l "^Status:" docs/` → empty after. |
| `tests/manual/m7_success_criteria.py` | Create | 9 | Aggregates the 5 success metrics from the Phase 9 JSON dumps. |

## Phase logs

_Per-phase entries are appended below as each phase completes,
mirroring M5/M6 log shape: Objective / Files changed / Actions
taken / Issues / decisions / Exit criteria._
