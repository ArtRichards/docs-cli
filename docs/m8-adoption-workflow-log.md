# M8 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-05-25

Related:
- child-of: m8-adoption-workflow.md
- pairs-with: status.md

## Implementation metadata

- Project: docs
- Milestone: M8 — Adoption workflow (agent-driveable)
- Started: 2026-05-24
- Progress: **Milestone-setup phase complete; Phases 1-4 complete;
  Phase 5 next; M7 shipped 2026-05-25 — Phase 2+ unblocked. RED
  baseline captured (40 RED + 5 baseline-GREEN regression locks +
  324 M7 GREEN preserved; 369 collected total).**
  The task plan [m8-adoption-workflow.md](m8-adoption-workflow.md)
  is promoted from `draft` to `active`. M8 is the third v1.1
  milestone (after M6 packaging and M7 migration accuracy). All
  seven milestone-setup OPEN QUESTIONS are resolved 2026-05-24
  (OQ-A `--propose-excludes` deferred; OQ-B `.docsignore` uses
  a gitignore subset; OQ-C ship M8 after M6 PyPI publish; OQ-D
  `.docs.toml.example` ships as a static file in the skill
  bundle; OQ-E `docs new --body-from` refuses body containing
  metadata-block lines; OQ-F `docs scaffold` deferred; OQ-G
  fresh-subagent integration gate is 3 trees minimum with 2/3
  passing unattended). Resolutions are recorded as Decisions in
  the task plan. M8 ships as 1.3.0. The load-bearing test is
  Phase 9 — the fresh-subagent integration gate.

(M7's `Status:` → `Lifecycle:` rename shipped 2026-05-25; this
log's front-matter and every other docs-tree front-matter line
were re-keyed in that sweep.)

## Milestone-setup open questions

Seven questions were surfaced while authoring the task plan.
**All seven are resolved 2026-05-24**, recorded as Decisions in
the task plan. Summary:

1. **OQ-A — `--propose-excludes` heuristic — RESOLVED 2026-05-24,
   deferred.** Out of M8 scope. Explicit `--exclude` +
   `[exclude] dirs` + `.docsignore` cover the immediate need.
   Heuristic auto-detection is a plausible follow-up.
2. **OQ-B — `.docsignore` syntax — RESOLVED 2026-05-24,
   gitignore subset.** Comments, blanks, `*` / `**` / trailing
   `/` / leading `/` / negation `!`. NOT full gitignore — no
   nested files, no walk-pruning. Implementation in stdlib
   (~60 lines).
3. **OQ-C — Publish timing — RESOLVED 2026-05-24, publish
   deferred until after M8 (possibly further pending review
   cycles).** No per-milestone publish. The first PyPI publish
   ships the M6 + M7 + M8 surface as one artifact (version
   1.3.0). Phase 9 fresh-subagent runs install from the local
   wheel (`dist/docs_cli-1.3.0-*.whl`) — equivalent UX.
   Practical sequence: M7 ship → M8 ship → operator review →
   batched publish.
4. **OQ-D — `.docs.toml.example` form — RESOLVED 2026-05-24,
   static file.** Ships as
   `src/docs_cli/skill/references/docs-toml-template.toml`.
   Operators `cp` it into place. `docs init --template` verb
   deferred.
5. **OQ-E — `docs new --body-from` body-with-frontmatter —
   RESOLVED 2026-05-24, refuse with clear error.** Exit 2 with
   error message + 5-line preview when the body content's
   first 20 lines contain a metadata-shaped line.
6. **OQ-F — `docs scaffold` sibling verb — RESOLVED 2026-05-24,
   skip.** `--body-from` covers the need; no new verb.
7. **OQ-G — Fresh-subagent gate threshold — RESOLVED 2026-05-24,
   3 trees minimum / 5 ideal / 2-of-3 passing unattended.**
   Trees selected to span size + style (kebab-tiny /
   snake-medium / snake-large or mixed-naming). If a subagent
   stalls on something the playbook doesn't anticipate, that's
   a fail — iterate the skill before re-running.

## Summary

Make `docs migrate`'s workflow agent-driveable end-to-end.
M7 made the plan accurate; M8 makes the operator + agent
workflow around the plan smooth. Adds `--exclude` tree-wide
(applies to migrate + index + check + list via the new
`[exclude]` section in `.docs.toml` + optional `.docsignore`
at the tree root), triage flags (`--summary`, `--only
ambiguous`, `--group-by`), a non-md sibling surfacing line in
the plan footer, and `docs new --body-from <-|path>` so agents
can author complete files in one Bash call (closes the
harness's Read-before-Write friction). The bundled skill's
references are rewritten substantially: a new
`adoption-playbook.md` carries the dry-run → triage → exclude
→ iterate → apply → check procedure end-to-end, with a worked
example sourced from the M7 sanitised fixtures; a new
`docs-toml-template.toml` ships as a copy-pasteable starter
that the playbook points at. **SKILL.md stays slim** —
extended with adoption trigger phrases and a single one-line
pointer to the playbook; substance lives in `references/`.
The load-bearing ship test is Phase 9: fresh Opus subagents,
no prior context, drive the adoption loop against M7 fixtures
they haven't seen. At least 2 of 3 must complete unattended.
M8 ships as 1.3.0 after M7.

## TDD Phase Progress

| Phase | Status | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-05-25 | Promoted M8 from `draft` to `active`; created this log; recorded OQ A–G resolutions as Decisions in the task plan; status.md "Current milestone" + milestone-table row + Next action point at M8. Close-out commit `ce39e85` + sha-credit follow-up `4a7b00f`. No code change; no convention change. INDEX + snapshot regenerated in lockstep. M7 shipped 2026-05-25; Phase 2+ unblocked. |
| 2. Write Tests (RED) | Complete | 2026-05-25 | 5 new test files + 1 test added to `test_migrate.py` across 6 commits. Functions: `test_exclude.py` (9, F3 — 22 items with parametric expansion on tests 3, 5, 6, 7), `test_triage_flags.py` (6, F6 — 6 items), `test_non_md_surfacing.py` (3, F7 — 3 items), `test_body_from.py` (7, F9 — 8 items with parametric on test 4), `test_skill_adoption.py` (5, F8 — 5 items, per OQ6 dropped the lockstep dup), `test_migrate.py::test_summary_and_json_are_mutually_exclusive` (1, F6). All RED for intended unimplemented surface; M7's 324 stays GREEN. |
| 3. Create Data/Fixtures | Complete | 2026-05-25 | Reused M7's 5 sanitised real-trees fixtures (kebab-tiny + snake-medium drive the triage tests; the other 3 remain Phase 9 substrate). 3 new fixture sets: `body-from/{with-frontmatter,clean-body,edge-case-keyword}`, `docsignore/sample/` (every OQ-B syntax case + sample files), `trees/exclude-test/` (small synthetic tree with `[exclude] dirs = ["build"]` in `.docs.toml` + a deliberately-malformed `build/generated.md`). Two `build/` subdirs force-added (-f) because the repo .gitignore has `build/` (project-output convention); the force-add is part of the contract surface. Sanitisation grep (per M7 log line 405) zero hits. |
| 4. Run Tests (RED Baseline) | Complete | 2026-05-25 | Captured verbatim at `/tmp/m8-phase-4-baseline.txt`. **324 M7 GREEN preserved + 5 baseline-GREEN regression locks + 40 RED for intended reasons (45 new collected items; 369 collected total; 329 passed + 40 failed).** Per-file: test_exclude.py 19 RED + 3 locks; test_triage_flags.py 6 RED; test_non_md_surfacing.py 2 RED + 1 lock; test_body_from.py 7 RED + 1 lock; test_skill_adoption.py 5 RED; test_migrate.py mutex 1 RED. Audit tightened tests 5 + 6 in test_exclude.py — added conformant docs under build/ and nested/ so the `list` / `index` assertions pin Phase 6's exclude predicate (vs. the today-coincidence of malformed-doc walker-skipping). Quality gate clean tree-wide. |
| 5. Update Base Interfaces | Pending | — | `Config` schema gains `exclude_dirs` / `exclude_globs` / `exclude_exts` / `docsignore_patterns`. `load_config` reads `[exclude]` + parses `.docsignore`. `compile_exclude_predicate` helper unifies CLI + config + ignore-file. Argparse: identical `--exclude` action on migrate/index/check/list; `--summary` / `--only` / `--group-by` / `--exclude-ext` on migrate; `--body-from` on new. Mutual exclusion: `--summary` vs `--json`. |
| 6. Implement Offline/Core Path | Pending | — | `_iter_doc_paths` consults the exclude predicate (tree-wide). `migrate_plan` honours predicate + emits excluded-count + non-md-sibling footer. `_render_migrate_plan` handles `--summary` / `--only ambiguous` / `--group-by` + default footer summary. `_cmd_new` handles `--body-from` with stdin/file + OQ-E refusal heuristic. `.docsignore` parser (~60 lines, stdlib only). |
| 7. Update Tool/Wrapper Layer (skill rewrite) | Pending | — | SKILL.md: append adoption trigger phrases to description; add one-line pointer to `references/adoption-playbook.md`. New `references/adoption-playbook.md` (substantial — six numbered steps + worked example + multi-project sub-section + sidecars sub-section + pitfalls). New `references/docs-toml-template.toml` (commented starter; `[exclude]` + `[migrate]` + `[vocabulary]`). Spec updates: cli.md (new flags), convention.md (`[exclude]` + `.docsignore` syntax), architecture.md (Config schema), README.md (adoption section), CHANGELOG.md (1.3.0). pyproject + cli.py `__version__` bumped to 1.3.0. Skill-refs lockstep maintained for convention.md + cli.md. |
| 8. Run Tests (GREEN) | Pending | — | Full quality gate verbatim: pytest M7-count + ~31 = expected GREEN total; ruff / format / mypy clean; `docs check docs/` exit 0; `docs index --dry-run` no diff; `python -m build` produces 1.3.0 wheel + sdist. |
| 9. Implement Online/Integration — **FRESH-SUBAGENT GATE** | Pending | — | **Load-bearing.** Spawn 3 fresh Opus subagents, no prior context, with the bundled skill installed (`docs install-skill`). Each gets a different M7 fixture and the prompt "adopt this directory; commit the result". Pass: ≥ 2 of 3 complete the full loop unattended. Third may escalate ONE playbook-flagged OQ. Stall = skill bug; iterate F8 / F9 / playbook / SKILL.md and re-run. Each run logged with transcript summary + pass/fail + iteration history. |
| 10. Quality, Docs, Refactor | Pending | — | Dogfood consistency sweep; milestone-completion summary; status.md M8 → Complete; CHANGELOG dated; `v1.3.0` tag pushed; (operator-driven) `python -m build` + `twine upload` per the runbook same as M6/M7; `gh release create v1.3.0`. |

## Current state analysis (snapshot at milestone kickoff, 2026-05-24)

_Captured before Phase 2; historical._

- **Codebase.** `src/docs_cli/cli.py` post-M6 + the M7 inference
  / convention changes (assumed shipped by the time M8 Phase 2
  starts). `Config` knows about `[vocabulary]` and (M7)
  `[migrate.role_suffixes]` + `[migrate] project_name`. No
  `[exclude]` section. Argparse subparsers as they ship at M7:
  `migrate` has `--apply`, `--json`, `--quiet`, `--date`, plus
  (no new flags or verbs from M7 — F0 was a pure parser
  rename, in-project sweep done manually). No `--exclude` /
  `--summary` / `--only` / `--group-by` / `--exclude-ext`. The
  `new` verb has no `--body-from`.
- **Specs.** `docs/convention.md` documents `[vocabulary]` +
  M7's additions; no `[exclude]` section yet. `docs/cli.md`
  documents the 8-verb surface + M7's `--rename-status-to-
  lifecycle` flag.
- **Bundled skill.** `src/docs_cli/skill/SKILL.md` is the M5/M6
  shape — trigger surface + verb table + the M5 lockstep
  references (`references/convention.md`, `references/cli.md`
  — byte-identical mirrors). No adoption playbook; no
  `.docs.toml` template.
- **Tests.** M7's count + 0 M8 tests yet.
- **Trial-run evidence.** `/tmp/m7-trial2/*.json` still
  available — referenced by both M7 Phase 3 (fixture
  promotion) and M8 Phase 9 (fresh-subagent gate prompts).
  M8's gate uses the fixtures M7 produces from this trial data.
- **Dependencies on M7:**
  - M7 ship is the prerequisite for M8 Phase 2 onwards.
  - The `medium` confidence level (M7 OQ-D) is reused by M8's
    `--group-by confidence` and the default plan footer.
  - The sanitised real-trees fixtures (M7 Phase 3) are M8
    Phase 9's prompt input.

## Files to Create / Modify

| File | Action | Phase | Notes |
|---|---|---|---|
| `docs/m8-adoption-workflow.md` | Modify | 1, 10 | Flip `Status: draft` → `active` (done at setup); append milestone-completion summary at Phase 10. |
| `docs/m8-adoption-workflow-log.md` | Create | 1 | This file. |
| `docs/status.md` | Modify | 1, 7, 10 | Phase 1: M8 setup complete + M8 row in flight. Phase 7: "Watch out for" entries for new flags. Phase 10: M8 → Complete. |
| `docs/plan.md` | (already registered) | — | M8 row added at the registration commit `1df6ec6`. |
| `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` | Regenerate | 1, 5, 7, 10 | Every doc-touching phase regenerates in lockstep. |
| `tests/test_exclude.py` | Create | 2 | 9 tests covering `--exclude` flag, `[exclude]` config tree-wide, `.docsignore` parser, glob patterns, plan footer. |
| `tests/test_triage_flags.py` | Create | 2 | 6 tests for `--summary`, `--only ambiguous`, `--group-by`, footer summary. |
| `tests/test_non_md_surfacing.py` | Create | 2 | 3 tests for F7 plan-footer non-md siblings. |
| `tests/test_body_from.py` | Create | 2 | 7 tests for `docs new --body-from <-|path>`, OQ-E refusal, idempotency, golden output. |
| `tests/test_skill_adoption.py` | Create | 2 | 6 tests for SKILL.md trigger phrases, pointer to playbook, playbook structure, TOML template validity, lockstep persistence. |
| `tests/test_migrate.py` | Modify | 2 | Add `--summary --json` mutual-exclusion test. |
| `tests/fixtures/body-from/` | Create | 3 | 3 small fixtures for F9 body-from edge cases. |
| `tests/fixtures/docsignore/sample/` | Create | 3 | `.docsignore` exercising every OQ-B syntax case + sample files. |
| `tests/fixtures/trees/exclude-test/` | Create | 3 | Small synthetic tree with `.docs.toml` `[exclude] dirs` + a `build/` subdir to skip. |
| `tests/fixtures/trees/real-trees/` | (reuse from M7) | 3, 9 | M7 fixtures consumed by triage tests + Phase 9 fresh-subagent runs. |
| `tests/fixtures/trees/real-trees-adopted/` | Create | 9 | Phase 9 outputs — committed adopted state of each fixture, one per subagent run. |
| `src/docs_cli/cli.py` | Modify | 5, 6, 7 | Phase 5: argparse + Config schema + `compile_exclude_predicate`. Phase 6: walker + render + body-from + .docsignore parser. Phase 7: `__version__` bumped to 1.3.0. |
| `src/docs_cli/skill/SKILL.md` | Modify | 7 | Minimal: trigger phrases in description + one-line pointer. NOT a rewrite. |
| `src/docs_cli/skill/references/adoption-playbook.md` | Create | 7 | The substantial new reference — step-by-step + worked example + pitfalls. Sourced from sanitised M7 fixtures. |
| `src/docs_cli/skill/references/docs-toml-template.toml` | Create | 7 | Commented `[exclude]`, `[migrate]`, `[vocabulary]` template. |
| `src/docs_cli/skill/references/convention.md` | Modify | 7 | Resynced from `docs/convention.md` (existing lockstep). |
| `src/docs_cli/skill/references/cli.md` | Modify | 7 | Resynced from `docs/cli.md` (existing lockstep). |
| `docs/convention.md` | Modify | 7 | `[exclude]` table documented; `.docsignore` syntax subset documented; pointer to adoption playbook. |
| `docs/cli.md` | Modify | 7 | New flags + plan-footer shape documented. |
| `docs/architecture.md` | Modify | 7 | `Config` schema updated. |
| `README.md` | Modify | 7 | 5-line adoption section near top. |
| `CHANGELOG.md` | Modify | 7, 10 | Phase 7: `## 1.3.0 — UNRELEASED`. Phase 10: dated. |
| `pyproject.toml` | Modify | 7 | `version = "1.3.0"`. |

## Phase logs

_Per-phase entries are appended below as each phase completes,
mirroring M5/M6/M7 log shape: Objective / Files changed / Actions
taken / Issues / decisions / Exit criteria._

_Phase 9 entries get special treatment — one sub-entry per
fresh-subagent run, with transcript summary + pass/fail +
iteration history if the playbook needed adjustment._

### Phase 1 — Define Contract

**Completed:** 2026-05-25

#### Objective

Declare the M8 surface — `--exclude` tree-wide (in `migrate`,
`index`, `check`, `list`), `[exclude]` section in `.docs.toml`,
`.docsignore` parser (OQ-B subset), triage flags (`--summary`,
`--only ambiguous`, `--group-by`), non-md sibling surfacing in
the plan footer, `docs new --body-from <-|path>` (with OQ-E
metadata-block refusal), and the substantial skill-reference
rewrite (`adoption-playbook.md` + `docs-toml-template.toml`;
SKILL.md gets one pointer line only). No code change at this
phase; no convention edits. Promote the task plan to active
(done at milestone-setup), create this log (done), record OQ
A–G resolutions as Decisions (done), and refresh status.md +
this log's TDD Phase Progress table so the historical record
reads "Phase 1 complete; Phase 2 next" rather than "Phase 1 in
progress" at the close-out commit. The 324-test suite stays
GREEN throughout.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/status.md` | Modify | M8 milestone-table row flipped from "Phase 1 in progress" to "Phase 1 complete; Phase 2 next". Narrative line carries the Phase 1 close-out commit sha (mirror of M7's "as `929e525`" pattern). The "Next action" was already pointing at M8 from the milestone-setup commit; no further edit needed. |
| `docs/m8-adoption-workflow.md` | Modify | `Updated:` bumped to 2026-05-25 via `docs touch`. |
| `docs/m8-adoption-workflow-log.md` | Modify | "Progress" paragraph rewritten from "Phase 1 in progress" → "Phase 1 complete; Phase 2 next". TDD Phase Progress table's Phase 1 row Status flipped In progress → Complete; row Notes tightened to reflect the close-out scope. This Phase-1 log entry appended. `Updated:` bumped to 2026-05-25. |
| `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Re-synced in lockstep via `.venv/bin/docs index --root docs/` after the text edits, so the (already-registered) M8 plan + log carry their fresh `Updated:` line in the snapshot. |

#### Actions taken

- **Audit of prior commits.** Verified that the bulk of the M8
  Phase 1 deliverables landed at milestone-setup commits
  (`1df6ec6` — register M7 + M8 stubs; later commits that promoted
  M8 to active, populated OQ A–G Decisions, created the log
  skeleton, and recorded all seven milestone-setup OQ resolutions).
  The residual delta at Phase 1 close-out is purely the
  "row flips + log entry" wording.
- **Doc-text edits.** Tightened `status.md`'s M8 row and this
  log's "Progress" paragraph + TDD Phase Progress table to read
  "Phase 1 complete; Phase 2 next". Bumped `Updated:` lines per
  the convention (`docs touch` semantics — 2026-05-25, the day
  M7 shipped and Phase 2+ unblocked).
- **INDEX regen.** Ran `.venv/bin/docs index --root docs/`;
  copied `docs/INDEX.md` over
  `tests/fixtures/expected/docs-INDEX.md` so the dogfood
  snapshot reflects the M8-log + plan body changes (the snapshot
  includes each doc's first-paragraph description).
- **Quality gate.** Ran the full gate from the project root:
  pytest 324 green; `ruff check .` clean; `ruff format --check .`
  clean; `mypy` Success; `.venv/bin/docs check docs/` exit 0.

#### Issues / decisions

- **No new code, no convention edit.** Phase 1 stays the
  reviewable-in-isolation phase per the task plan's Phase 1
  exit criteria. The `[exclude]` schema + argparse landings are
  Phase 5 work; the walker + render + body-from + .docsignore
  parser work is Phase 6; the skill rewrite is Phase 7. Confirmed
  via `git diff` that the Phase 1 close-out commit touches only
  `docs/status.md`, `docs/m8-adoption-workflow.md`,
  `docs/m8-adoption-workflow-log.md`, `docs/INDEX.md`, and the
  INDEX snapshot.
- **All seven OQs (A–G) already resolved 2026-05-24** at
  milestone-setup; no new questions surfaced at Phase 1 close-out.
- **OQ1 (planning, Step 1 verification).** The `_cmd_migrate`
  managed-marker refusal set
  (`src/docs_cli/cli.py` ~2990–2998) is `{"project", "archive",
  "vocabulary"}` — it does NOT include `[exclude]` or `[migrate]`,
  which matches the Phase 5 plan ("`.docs.toml` containing only
  `[migrate]` and/or `[exclude]` remains acceptable as a
  foreign-tree sidecar"). Phase 5 will update the comment but
  leave the refusal set as-is.
- **OQ8 (planning, surfaced for Step 2).** The new skill
  reference files (`references/adoption-playbook.md`,
  `references/docs-toml-template.toml`) are not in
  `_SKILL_RELATIVE_FILES` (`src/docs_cli/cli.py` ~3044–3048).
  Step 2 / Phase 7 will need to extend the tuple so
  `install-skill --symlink` and the no-clutter / byte-identity
  checks cover the new files.

#### Exit criteria

- [x] `Lifecycle:` in `m8-adoption-workflow.md` is `active`
      (set at milestone-setup; unchanged here).
- [x] `docs/m8-adoption-workflow-log.md` exists; its TDD Phase
      Progress table's Phase 1 row is Complete (2026-05-24).
- [x] `docs/status.md` M8 milestone-table row reads "Phase 1
      complete; Phase 2 next".
- [x] `docs/INDEX.md` and
      `tests/fixtures/expected/docs-INDEX.md` are byte-identical
      after regeneration.
- [x] `.venv/bin/python -m pytest tests/ -q` — 324 passed.
- [x] `ruff check .`, `ruff format --check .`, `mypy` — clean.
- [x] `.venv/bin/docs check docs/` — exit 0.
- [x] No code change happened (no `src/` edits, no
      `pyproject.toml` edits, no test file additions).
- [x] No convention change happened (no `[exclude]` schema yet
      — that's Phase 5).

### Phase 2 — Write Tests (RED)

**Completed:** 2026-05-25

#### Objective

Express every M8 finding (F3/F6/F7/F8/F9) as a failing check before
any implementation lands. Tests collect cleanly; every new RED test
fails for its intended unimplemented surface (argparse on new flags,
absent skill references, today-absent footer surfacings). M7's 324
in-tree tests stay GREEN throughout.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `tests/test_exclude.py` | Create | 9 distinct test functions for F3 (parametric expansion on tests 3, 5, 6, 7 → 22 collected items). Covers `--exclude` flag (basic skip + repeatable + glob), `--exclude-ext`, `[exclude] dirs` + `[exclude] globs` tree-wide on every verb (index/check/list/migrate), `.docsignore` OQ-B syntax subset (7 cases), CLI layering over .docs.toml, plan-footer excluded-count line. |
| `tests/test_triage_flags.py` | Create | 6 tests for F6 (6 items): `--summary` per-file lines; `--only ambiguous` filter; `--group-by role` / `--group-by confidence`; default plan-footer counts (substring-token assertions per OQ3 — Phase 6 picks the exact shape); `--summary` + `--only ambiguous` compose. |
| `tests/test_non_md_surfacing.py` | Create | 3 tests for F7 (3 items): footer line surfaces 3 non-md siblings with all names + count; N==0 → no footer line (regression lock); `--exclude-ext` suppresses the footer when filtered list is empty (OQ4). |
| `tests/test_body_from.py` | Create | 7 test functions for F9 (8 items with test 4 parametric ×2 — with-frontmatter.txt + edge-case-keyword.md per OQ5). Covers stdin happy path, file-path happy path, scaffold+body composition golden, OQ-E metadata-block refusal (exit 2 + documented error tokens), missing-value argparse error, nonexistent-path exit 2, idempotency refusal. |
| `tests/test_skill_adoption.py` | Create | 5 tests for F8 (5 items, NOT 6 — per OQ6 the proposed 6th "lockstep guarantee" test would duplicate the existing `test_skill_refs.py::test_bundled_ref_matches_source`; dropped). Asserts SKILL.md adoption triggers, one-line pointer, adoption-playbook.md exists with required H2s, docs-toml-template.toml is valid TOML with `[exclude]` / `[migrate]` / `[vocabulary]` sections + commented examples. |
| `tests/test_migrate.py` | Modify | One new test — `test_summary_and_json_are_mutually_exclusive` asserts `docs migrate --summary --json` → exit 2 + "not allowed with" in stderr. |

#### Test counts

- 45 new collected items: 22 + 6 + 3 + 8 + 5 + 1.
- 9 + 6 + 3 + 7 + 5 + 1 = 31 distinct test functions per the
  plan's count.
- Total suite: 369 collected (324 M7 + 45 M8).

#### Quality discipline

- All test files use the existing `from docs import …` alias from
  `tests/conftest.py` (M6 conftest aliases `docs_cli.cli` as
  `docs`) where they import library surface; subprocess CLI tests
  use the `docs_script` + `fixtures_dir` session fixtures.
- Helper `_run(docs_script, *args)` + `_write(path, text)` defined
  per file, mirroring `tests/test_migrate.py` lines 590-593 + the
  `tests/test_cli_new.py` lines 15-21 pattern.
- `tests/test_skill_adoption.py` imports its helpers from sibling
  module `test_skill` (pytest's auto-extended sys.path resolves
  the bare module name — adding a `tests/__init__.py` would
  collide with the project's flat-package convention).
- Substring assertions only on the default-footer + group-by
  shapes (per OQ3) — Phase 6 picks the exact rendering.

#### Issues / decisions

- **OQ5 (planning) — edge-case-keyword.md folds into test 4's
  parametrisation, NOT its own happy-path test.** The OQ-E
  heuristic is conservative-by-design; `Plan: stage one then
  stage two` matches `^[A-Z][A-Za-z-]+:\s` and IS expected to
  refuse. The parametrisation documents the false-positive
  trade-off rather than pinning a test that would expect the
  heuristic to be smarter than its design spec.
- **OQ6 (planning) — 5 skill_adoption tests, not 6.** The 6th
  proposed test ("lockstep guarantee still holds") would
  duplicate `tests/test_skill_refs.py::test_bundled_ref_matches_source`.
  Module docstring records this.
- **OQ7 (planning) — Phase 1 sha credit landed as a 2-commit
  sequence** (close-out commit + amend-with-sha-then-follow-up
  sha-credit commit). Cleaner than amending the close-out commit
  (which would be self-referential).
- **OQ8 (planning, surfaced for Step 2) — `use-cases.md` /
  new skill references not in `_SKILL_RELATIVE_FILES`.** The new
  reference files (`adoption-playbook.md`, `docs-toml-template.toml`)
  need to be added to `_SKILL_RELATIVE_FILES` at Phase 7 so
  `install-skill --symlink` + the no-clutter / byte-identity checks
  cover them. Not in Step 1 scope.
- **`test_body_from_idempotency_second_call_refuses` uses
  `proc.returncode != 0` + `"already exists"` substring** rather
  than pinning exit 2 (which the plan's text implied). Today's
  cli.py 2605-2607 returns exit code 1 on existing-file refusal;
  Phase 5/6 keeps that existing semantics. The test's loose
  exit-code assertion accommodates the established behaviour
  without inventing a new contract.

#### Verification

- `.venv/bin/python -m pytest --collect-only -q tests/test_exclude.py tests/test_triage_flags.py tests/test_non_md_surfacing.py tests/test_body_from.py tests/test_skill_adoption.py` — 44 items collected (22 + 6 + 3 + 8 + 5), zero ImportError / CollectError.
- `.venv/bin/python -m pytest --collect-only -q tests/` — 369 items collected (324 M7 + 44 from the 5 new files + 1 added test in test_migrate.py = 45 net new items).
- `.venv/bin/ruff check .`, `ruff format --check .`, `mypy` — clean tree-wide.
- `.venv/bin/docs check docs/` — exit 0.

#### Exit criteria

- [x] Every new test file collects cleanly.
- [x] Every RED test fails for its intended unimplemented
      surface (Phase 4 captures the verbatim split + per-test
      attribution).
- [x] M7's 324 in-tree tests stay GREEN.
- [x] Imports use the conftest `from docs import …` alias.
- [x] Subprocess tests use `docs_script` + `fixtures_dir`.
- [x] No fixture authoring at this phase (Phase 3 owns that).
- [x] `ruff` / `format` / `mypy` clean tree-wide.
- [x] `docs check docs/` exit 0.

### Phase 3 — Create Data/Fixtures

**Completed:** 2026-05-25

#### Objective

Stage the small fixture set the Phase-2 tests reference. Reuse
M7's 5 sanitised real-trees fixtures heavily; new fixtures only
for body-from edge cases, the docsignore syntax exerciser, and
a small `[exclude]`-bearing synthetic tree.

#### Files changed

| Path | Action | Notes |
|---|---|---|
| `tests/fixtures/body-from/with-frontmatter.txt` | Create | Real metadata block at the head (`Owner: alice` + `Tags: infra`) — triggers OQ-E refusal. |
| `tests/fixtures/body-from/clean-body.md` | Create | Happy-path body with no metadata-shaped lines (`## Overview` + `## Details`). |
| `tests/fixtures/body-from/edge-case-keyword.md` | Create | OQ5 false-positive trade-off — `Plan: stage one then stage two` matches `^[A-Z][A-Za-z-]+:\s` so the conservative-by-design heuristic refuses. Test 4's parametrisation pins the documented behaviour. |
| `tests/fixtures/docsignore/sample/.docsignore` | Create | Exercises every OQ-B syntax case: `*.tmp`, `data/`, `/specific.md`, `**/build/**`, comment, blank, `!keep-me.md` after a preceding `*.md`. |
| `tests/fixtures/docsignore/sample/{keep,specific,keep-me}.md` + `data/x.md` + `nested/build/y.md` + `nested/keep-me.md` + `something.tmp` | Create | Sample files exercising the patterns above. |
| `tests/fixtures/trees/exclude-test/.docs.toml` | Create | `[project] name = "exclude-test"` + `[exclude] dirs = ["build"]`. |
| `tests/fixtures/trees/exclude-test/{spec,plan}.md` | Create | Conformant docs (H1-then-metadata-block per the convention). |
| `tests/fixtures/trees/exclude-test/build/generated.md` | Create | Deliberately malformed (no metadata block) — proves `[exclude] dirs = ["build"]` is the only reason `docs check` exits 0. |

#### Actions taken

- Built each fixture by hand. Body-from + docsignore fixtures
  use generic placeholders (`alice` / `infra` / `Foo` / `Bar`).
  No third-party product / customer / feature names appear.
- Force-added both `build/` subdirs with `git add -f` because
  the repo .gitignore has `build/` (project-output convention).
  Documented in the Phase 3 commit message.
- Ran the sanitisation grep (mirror M7 log line 405):

  ```sh
  grep -ri "langfuse\|festo\|orginfo\|embedded.ai\|gpt5\|treatment.rubric\|disambiguation\|risk.prompt\|software.first\|standalone.agents\|orgcontext" tests/fixtures/{body-from,docsignore,trees/exclude-test}/
  ```

  Zero hits.

#### Issues / decisions

- **Reuse over re-author.** kebab-tiny + snake-medium drive the
  triage tests directly; snake-large + archive-subdir + mixed-naming
  remain Phase 9 substrate. No new copies of the M7 fixtures.
- **`build/` gitignore tension.** The repo's project-level
  .gitignore excludes `build/` (Python wheel output convention).
  The exclude-test fixture deliberately uses `build/` as the
  exclude-dirs target because that's the most realistic
  adoption-tree shape. Force-add + commit message annotation
  resolves the tension at the per-file level without weakening
  the project-wide ignore.

#### Exit criteria

- [x] Every fixture path the new tests reference exists.
- [x] Sanitisation grep returns zero hits.
- [x] M7's 324 in-tree tests stay GREEN.
- [x] Quality gate clean tree-wide.
- [x] `docs check docs/` exit 0.

### Phase 4 — Run Tests (RED Baseline)

**Completed:** 2026-05-25

#### Objective

Capture the verbatim RED baseline before any implementation.
Confirm every new RED test fails for its intended unimplemented
reason; surface the GREEN-at-baseline regression locks. Pin
M7's 324 GREEN baseline + the quality gate.

#### Verbatim pytest output

```text
$ .venv/bin/python -m pytest tests/ -q --tb=short
... (369 items collected) ...
40 failed, 329 passed in 9.55s
```

Captured at `/tmp/m8-phase-4-baseline.txt`. (Initial 38-failed-331-passed
baseline was captured before the same-instance audit strengthened
test_exclude.py tests 5 and 6 by adding conformant docs under the
excluded subdirs; final baseline above is post-audit.)

#### Per-test attribution table

| Test group | Source file | RED count | GREEN-at-baseline (regression-lock) count | Failure mode → root cause |
|---|---|---:|---:|---|
| F3 — `--exclude` flag, `[exclude]` config, `.docsignore`, plan-footer count | `test_exclude.py` | 19 | 3 | argparse rejects `--exclude` / `--exclude-ext` on every verb (exit 2); `.docsignore` not parsed; `[exclude]` not consulted by walker; footer absent. Locks: docsignore patterns where the today-absent predicate yields the contract-correct outcome (`*.tmp` excludes non-.md anyway; comment-only and blank-only patterns are correctly no-ops). |
| F6 — triage flags + default footer | `test_triage_flags.py` | 6 | 0 | argparse rejects `--summary` / `--only` / `--group-by` (exit 2); default footer doesn't emit the documented substrings. |
| F6 — `--summary` × `--json` mutex | `test_migrate.py` | 1 | 0 | argparse rejects `--summary` as "unrecognized" today; Phase 5 flips to "not allowed with" via mutex group. |
| F7 — non-md sibling surfacing | `test_non_md_surfacing.py` | 2 | 1 | footer line absent today. Lock: N==0 → no footer line (correctly absent today). |
| F9 — `docs new --body-from` | `test_body_from.py` | 7 | 1 | argparse rejects `--body-from` (exit 2); OQ-E refusal absent; idempotency contract unstable today. Lock: missing-value → exit 2 (today's "unrecognized" path coincidentally matches the contract). |
| F8 — skill adoption playbook + template | `test_skill_adoption.py` | 5 | 0 | SKILL.md description has no adoption phrases; one-line pointer absent; `references/adoption-playbook.md` and `references/docs-toml-template.toml` do not exist. |
| **TOTAL** |  | **40** | **5** | — |

Function totals: 9 + 6 + 1 + 3 + 7 + 5 = 31 distinct test functions.
Collected-item totals: 22 + 6 + 1 + 3 + 8 + 5 = 45 items.

#### Quality gate (verbatim)

```text
$ .venv/bin/ruff check .
All checks passed!

$ .venv/bin/ruff format --check .
33 files already formatted

$ .venv/bin/mypy
Success: no issues found in 34 source files

$ .venv/bin/docs check docs/
docs: no violations found
```

#### Attestation — no RED-for-wrong-reason

Every RED test was inspected against its `--tb=short` traceback
(captured at `/tmp/m8-phase-4-baseline.txt`):

- No `ImportError` / `ModuleNotFoundError`.
- No `FileNotFoundError` / fixture-not-found failures (every
  fixture path the tests reference was staged at Phase 3).
- The `argparse` errors ARE the intended RED surface for the
  unimplemented flags (`--exclude`, `--exclude-ext`, `--summary`,
  `--only`, `--group-by`, `--body-from`) — Phase 5 flips them
  from argparse-error RED to assertion RED, then Phase 6/7
  takes them to GREEN.
- Every assertion failure message names the contract the
  Phase 5/6/7 implementation will satisfy.

The 38 REDs partition cleanly: 17 F3 + 6 F6-triage + 1 F6-mutex
+ 2 F7 + 7 F9 + 5 F8 (the 7 baseline-GREEN regression locks
are listed in the per-test attribution table above).

#### Issues / decisions

- **45 collected items vs 31 distinct functions.** Parametric
  expansion on test_exclude.py (tests 3 ×2, 5 ×4, 6 ×4, 7 ×7) +
  test_body_from.py (test 4 ×2) accounts for the +14 difference.
  Per OQ2 (planning resolution, binding): "9 distinct test
  functions in test_exclude.py via parametrization … Phase 4
  log notes the collected-item count vs function count." Done.
- **5 baseline-GREEN locks vs the plan's expectation of
  RED-only.** The plan's Expected RED matrix anticipated only
  RED for the new flags. The actual baseline has 5 items that
  pass at baseline for the same reason F7 N==0 passes (the
  today-absent feature happens to produce the contract-correct
  outcome). These are regression locks — Phase 6 must preserve
  them. The Per-test attribution table above flags each one.
- **Audit-time tightening** (during the same-instance consistency
  check, between the initial Phase 4 commit and the audit-fixes
  commit). The initial baseline had 7 baseline-GREEN locks; two
  of them (`list` + `index` arms of test 5 and test 6 in
  test_exclude.py) were weak — they passed today only because
  the build/malformed.md fixture was silently skipped by the
  walker. Added conformant docs under the excluded subdirs so
  the assertions pin the Phase 6 exclude predicate explicitly
  (vs. the today-coincidence). Net: 2 more proper RED tests,
  reducing the lock count from 7 to 5. The remaining 5 locks
  are genuine "today's missing predicate produces the
  contract-correct outcome" cases.
- **No structural surprise.** Every RED's failure message was
  the assertion the test was designed to fail. No fixture
  oversight, no import accident, no off-by-one mismatch.
