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
- Progress: **All 10 TDD phases complete (2026-05-25); shipped
  locally as 1.3.0 — publish DEFERRED to M9 per OQ-C. RED
  baseline at Phase 4 captured (41 RED + 4 baseline-GREEN
  regression locks + 324 M7 GREEN preserved; 369 collected
  total); all 369 GREEN at Phase 8 close. Phase 9 re-run with
  real fresh Opus subagents — 3/3 PASS unattended (kebab-tiny /
  snake-medium / snake-large adopted end-to-end, no operator
  intervention, no playbook iterations needed).**
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
| 3. Create Data/Fixtures | Complete | 2026-05-25 | Reused M7's 5 sanitised real-trees fixtures (kebab-tiny + snake-medium drive the triage tests; the other 3 remain Phase 9 substrate). 1 new on-disk fixture set: `body-from/{with-frontmatter,clean-body,edge-case-keyword}`. The `.docsignore` syntax cases and `[exclude]`-bearing trees are written **inline via `tmp_path`** by the Phase-2 tests themselves (`_write(root / ".docsignore", ...)` pattern in `tests/test_exclude.py`) — established codebase convention; no on-disk fixture dirs needed. Sanitisation grep (per M7 log line 405) zero hits on the new on-disk fixtures. |
| 4. Run Tests (RED Baseline) | Complete | 2026-05-25 | Captured verbatim at `/tmp/m8-phase-4-baseline.txt`. **324 M7 GREEN preserved + 4 baseline-GREEN regression locks + 41 RED for intended reasons (45 new collected items; 369 collected total; 328 passed + 41 failed).** Per-file: test_exclude.py 20 RED + 2 locks; test_triage_flags.py 6 RED; test_non_md_surfacing.py 2 RED + 1 lock; test_body_from.py 7 RED + 1 lock; test_skill_adoption.py 5 RED; test_migrate.py mutex 1 RED. Audit round 2 tightened tests 5 + 6 in test_exclude.py — added conformant docs under build/ and nested/ so the `list` / `index` assertions pin Phase 6's exclude predicate (vs. the today-coincidence of malformed-doc walker-skipping). Fresh-eyes review then swapped test 7 case 1 from `*.tmp` to `*.draft.md` so the `.docsignore` parser path — not the markdown-only walker — is what excludes the file at Phase 6; tightened `test_default_plan_footer_shows_counts` to anchor all four footer tokens to the footer slice; deleted the unused `tests/fixtures/docsignore/sample/` and `tests/fixtures/trees/exclude-test/` directories (inline-via-tmp_path is the codebase convention). Quality gate clean tree-wide. |
| 5. Update Base Interfaces | Complete | 2026-05-25 | `Config` gained the four exclude fields; `MigrationPlan` gained 3 optional human-output-only fields (per OQ1; OMITTED from `migration_to_json`). `load_config` reads `[exclude]` + root `.docsignore`. New `_compile_docsignore_pattern` + `compile_exclude_predicate` helpers (stdlib `re` only). `predicate=` keyword threaded through `_iter_doc_texts` / `walk` / `check_tree` / `query_docs` / `_refresh_index` (per OQ2). Argparse: `--exclude PATTERN` on idx/check/list/migrate via shared `_add_exclude_flag` helper; `--summary` ⊻ `--json` mutex + `--only {ambiguous}` + `--group-by {role,confidence}` + `--exclude-ext EXTS` on migrate; `--body-from PATH` on new. `_cmd_migrate` managed-marker comment carries M8 OQ1 `[exclude]` carve-out. Quality gate clean. 340 GREEN / 29 RED — argparse-error → behaviour-RED transition complete; predicate already flips 8 index/check/list-arm REDs to GREEN. |
| 6. Implement Offline/Core Path | Complete | 2026-05-25 | `plan_migration` gained `cli_excludes` / `cli_exclude_exts` kwargs + the predicate wire-up; excluded files counted + bucketed by top-level prefix; `MigrationPlan` populated with the three new fields. `_print_migration_plan` gained `mode` / `only` / `group_by` kwargs — `--summary` emits one tabular line per file; `--only ambiguous` filters; `--group-by role/confidence` sorts. Footer (after per-file block per OQ3): excluded counts → non-md siblings → multi-project hints → default summary (`summary:` / `roles:` / `confidence:` / `ambiguities:`). `_cmd_new` handles `--body-from` (file or `-`/stdin) with OQ-E refusal scanning the first 20 lines for `^[A-Z][A-Za-z-]+:\s` — validation runs BEFORE the dry-run check per OQ4. `_cmd_migrate` carve-out widened: `[exclude]` in `.docs.toml` waives the managed-marker refusal even alongside `[project]/[archive]/[vocabulary]` (the operator's explicit signal "use migrate to triage this managed tree"). 364 GREEN / 5 RED — all 5 remaining REDs are F8 skill-content (Phase 7). |
| 7. Update Tool/Wrapper Layer (skill rewrite) | Complete | 2026-05-25 | SKILL.md: appended 4 adoption triggers to description (1024-char ceiling OK); added one-line pointer block (`**Adopting an existing Markdown directory?** Read [references/adoption-playbook.md]`); also swept M7 misses (`docs list --status` → `--lifecycle`; "hand-flip `Status:`" → "hand-flip `Lifecycle:`"; metadata-block `Status:` → `Lifecycle:`). New `references/adoption-playbook.md` (343 lines; six required H2s + worked example + pitfalls; frontmatter Lifecycle/Role/Project/Updated/Related). New `references/docs-toml-template.toml` (~90 lines; `[exclude]` + `[migrate]` + `[vocabulary]` + `[project]` + `[archive]`; every example commented). `_SKILL_RELATIVE_FILES` extended with `use-cases.md` (pre-existing packaging gap) + the 2 new files. `pyproject.toml` + `cli.py __version__`: 1.2.0 → 1.3.0. `tests/test_packaging.py` version pins bumped (3 spots) + the two helper-function names refreshed for clarity. docs/cli.md: synopses extended for `new` (`--body-from`) + `index` / `check` / `list` (`--exclude`) + `migrate` (full new surface); + "Triage flags (M8)" + "Plan footer (M8)" subsections + a new "Common: exclusion" top-level section. docs/convention.md: new `## Exclusion` section after Subdirectories + one-paragraph M8 F7 note on the Non-Markdown section. docs/architecture.md: bumped version comment to 1.3.0; layout sketch extended with use-cases / adoption-playbook / docs-toml-template; Config + walker sections extended with the M8 fields + predicate. README.md: Adoption section (5 lines) after Install; Commands list extended; Status section adds M8 row + bumps publish-strategy framing. CHANGELOG.md: new `## 1.3.0 — UNRELEASED` block (Added / Changed / Notes). Lockstep resync of skill references after `docs touch`. Quality gate clean; **all 369 GREEN — F8 RED tests flipped to GREEN.** |
| 8. Run Tests (GREEN) | Complete | 2026-05-25 | **369/369 GREEN** (45 new M8 items + 324 M7-baseline). Quality gate: ruff `All checks passed`; ruff format `33 files already formatted`; mypy `Success: no issues found in 34 source files`; `docs check docs/` `no violations found`; `docs index --dry-run` no diff. `python -m build` produced `docs_cli-1.3.0-py3-none-any.whl` + `docs_cli-1.3.0.tar.gz`; twine check `PASSED` on both. `docs --version` reports `docs 1.3.0`. Verbatim capture: `/tmp/m8-phase-8-green.txt`. |
| 9. Implement Online/Integration — **FRESH-SUBAGENT GATE** | Complete | 2026-05-25 | **3/3 PASS unattended.** Initial Phase 9 pass ran as same-instance dogfood substitution (the implementation agent couldn't nest Agent tool calls) — surfaced and fixed a real playbook bug in Step 3 ordering. Per operator decision the gate was then re-run with three real fresh Opus subagents spawned via the conductor's Agent tool: kebab-tiny (commit `8d80627`), snake-medium (commit `eb62d9d`), snake-large (commit `ba09da9`) — all completed the adoption loop end-to-end with no operator intervention and no further playbook iterations needed. Adopted state captured to `tests/fixtures/trees/real-trees-adopted/{kebab-tiny,snake-medium,snake-large}/`; sanitisation grep zero hits; `docs check` exit 0 on each adopted fixture. Minor playbook polish opportunities surfaced (`--quiet` semantics, INDEX ordering wording, project-name inference source) — documented as follow-ons; non-blocking. |
| 10. Quality, Docs, Refactor | Complete | 2026-05-25 | Dogfood sweep: M7-era `migrate_plan` / `_render_migrate_plan` references left intact in milestone-doc historical Phase 6 sketch (the surrounding context makes the historical reference clear; not misleading to a future reader). Milestone-completion summary appended to docs/m8-adoption-workflow.md. status.md M8 row → Complete; Current-milestone narrative + Next-action updated. CHANGELOG dated 2026-05-25. INDEX + snapshot regen'd in lockstep. Final quality gate: 369 GREEN; ruff/format/mypy clean; `docs check docs/` exit 0; `python -m build` → `docs_cli-1.3.0-py3-none-any.whl` + `docs_cli-1.3.0.tar.gz`; twine check PASSED on both. **NO `twine upload`, NO `git tag v1.3.0`, NO GitHub release** — per OQ-C the publish surface is deferred to M9. |

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
| _(no on-disk fixtures for `.docsignore` / `[exclude]` cases)_ | — | 3 | `.docsignore` syntax cases and `[exclude]`-bearing trees are written **inline via `tmp_path`** by the Phase-2 tests themselves (see `_write(root / ".docsignore", ...)` in `tests/test_exclude.py`); no on-disk fixture dir is staged. Established codebase convention. |
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
M7's 5 sanitised real-trees fixtures heavily; new on-disk
fixtures only for body-from edge cases. The `.docsignore`
syntax cases and small `[exclude]`-bearing synthetic trees are
authored **inline via `tmp_path`** by the Phase-2 tests
themselves — the established codebase convention.

#### Files changed

| Path | Action | Notes |
|---|---|---|
| `tests/fixtures/body-from/with-frontmatter.txt` | Create | Real metadata block at the head (`Owner: alice` + `Tags: infra`) — triggers OQ-E refusal. |
| `tests/fixtures/body-from/clean-body.md` | Create | Happy-path body with no metadata-shaped lines (`## Overview` + `## Details`). |
| `tests/fixtures/body-from/edge-case-keyword.md` | Create | OQ5 false-positive trade-off — `Plan: stage one then stage two` matches `^[A-Z][A-Za-z-]+:\s` so the conservative-by-design heuristic refuses. Test 4's parametrisation pins the documented behaviour. |
| _(none)_ for `.docsignore` / `[exclude]` cases | — | Every `.docsignore` test in `tests/test_exclude.py::test_docsignore_syntax_subset` writes its `.docsignore` inline via `_write(root / ".docsignore", ...)` into `tmp_path`; every `[exclude]` test (5 + 6 + 8) writes its `.docs.toml` + sample tree the same way. No on-disk fixture directory is staged for these — the inline tmp_path pattern is the established convention in this codebase. |
| `tests/fixtures/trees/real-trees/` | (reuse from M7) | M7's `kebab-tiny` + `snake-medium` drive the triage tests; `snake-large`, `archive-subdir`, `mixed-naming` remain Phase 9 substrate. No new copies. |

#### Actions taken

- Built each body-from fixture by hand. Generic placeholders
  (`alice` / `infra` / `Foo` / `Bar`). No third-party product /
  customer / feature names appear.
- Authored `.docsignore` and `[exclude]` cases inline in the
  Phase-2 tests (see the `_write(...)` helper in
  `tests/test_exclude.py`). No on-disk fixture directories
  needed; the tests build the trees they need in `tmp_path`
  per pytest convention.
- Ran the sanitisation grep over the new on-disk fixtures
  (mirror M7 log line 405):

  ```sh
  grep -ri "langfuse\|festo\|orginfo\|embedded.ai\|gpt5\|treatment.rubric\|disambiguation\|risk.prompt\|software.first\|standalone.agents\|orgcontext" tests/fixtures/body-from/
  ```

  Zero hits.

#### Issues / decisions

- **Reuse over re-author.** kebab-tiny + snake-medium drive the
  triage tests directly; snake-large + archive-subdir + mixed-naming
  remain Phase 9 substrate. No new copies of the M7 fixtures.
- **Inline-via-tmp_path over on-disk fixture dirs for
  `.docsignore` + `[exclude]`.** The `.docsignore` syntax cases
  vary widely per parametric case (pattern + present-files +
  excluded-paths + kept-paths); maintaining an on-disk
  exerciser fixture would duplicate effort with no benefit
  beyond what the inline `_write(root / ".docsignore", ...)`
  pattern already gives the tests. Same for the small
  `[exclude]`-bearing trees in tests 5/6/8. Established
  codebase convention — keeps the test bodies self-contained
  and avoids a `build/` gitignore tension that would otherwise
  arise (the repo's project-level .gitignore excludes `build/`).

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
41 failed, 328 passed in 9.49s
```

Captured at `/tmp/m8-phase-4-baseline.txt`. (Initial 38-failed-331-passed
baseline was captured before the same-instance audit strengthened
test_exclude.py tests 5 and 6 by adding conformant docs under the
excluded subdirs. A subsequent fresh-eyes review then swapped the
test 7 case-1 pattern from `*.tmp` to `*.draft.md` so the predicate
path — not the markdown-only walker — is what excludes the file at
Phase 6; that swap converted the case-1 baseline-GREEN lock to a
proper RED. Final baseline above is post-both-rounds.)

#### Per-test attribution table

| Test group | Source file | RED count | GREEN-at-baseline (regression-lock) count | Failure mode → root cause |
|---|---|---:|---:|---|
| F3 — `--exclude` flag, `[exclude]` config, `.docsignore`, plan-footer count | `test_exclude.py` | 20 | 2 | argparse rejects `--exclude` / `--exclude-ext` on every verb (exit 2); `.docsignore` not parsed; `[exclude]` not consulted by walker; footer absent. Remaining locks: docsignore patterns where the today-absent predicate yields the contract-correct outcome (comment-only and blank-only patterns are correctly no-ops). |
| F6 — triage flags + default footer | `test_triage_flags.py` | 6 | 0 | argparse rejects `--summary` / `--only` / `--group-by` (exit 2); default footer doesn't emit the documented substrings. |
| F6 — `--summary` × `--json` mutex | `test_migrate.py` | 1 | 0 | argparse rejects `--summary` as "unrecognized" today; Phase 5 flips to "not allowed with" via mutex group. |
| F7 — non-md sibling surfacing | `test_non_md_surfacing.py` | 2 | 1 | footer line absent today. Lock: N==0 → no footer line (correctly absent today). |
| F9 — `docs new --body-from` | `test_body_from.py` | 7 | 1 | argparse rejects `--body-from` (exit 2); OQ-E refusal absent; idempotency contract unstable today. Lock: missing-value → exit 2 (today's "unrecognized" path coincidentally matches the contract). |
| F8 — skill adoption playbook + template | `test_skill_adoption.py` | 5 | 0 | SKILL.md description has no adoption phrases; one-line pointer absent; `references/adoption-playbook.md` and `references/docs-toml-template.toml` do not exist. |
| **TOTAL** |  | **41** | **4** | — |

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

The 41 REDs partition cleanly: 20 F3 + 6 F6-triage + 1 F6-mutex
+ 2 F7 + 7 F9 + 5 F8 (matches the per-test attribution table
above; the 4 baseline-GREEN regression locks are listed there
as well).

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

### Phase 5 — Update Base Interfaces

**Completed:** 2026-05-25

#### Objective

Land the M8 schema + argparse surface: extend `Config` with the
four exclude fields, extend `MigrationPlan` with three
optional human-output-only fields (per OQ1), teach `load_config`
to read `[exclude]` + `.docsignore`, add `_compile_docsignore_pattern`
+ `compile_exclude_predicate` helpers, thread an optional
`predicate` parameter through `_iter_doc_texts` / `walk` /
`check_tree` / `query_docs` / `_refresh_index` (per OQ2), add
identical `--exclude PATTERN` to `idx` / `check_p` / `list_p` /
`migrate_p` (via a shared `_add_exclude_flag` helper), and add
the migrate-only `--exclude-ext` / `--summary` / `--only
{ambiguous}` / `--group-by {role,confidence}` flags (with
`--summary | --json` mutex), plus `--body-from` on `new`.
Update the `_cmd_migrate` managed-marker comment to note the
M8 (OQ1) carve-out: `[exclude]` joins `[migrate]` as a
foreign-tree sidecar section. No business logic; that's
Phase 6.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `src/docs_cli/cli.py` | Modify | + `Callable` import. + 4 `Config` fields (defaulted; additive). + 3 `MigrationPlan` fields (defaulted; OMITTED from `migration_to_json` per OQ1, mirroring the M7 `multi_project_hints` precedent). + `[exclude]` table + root `.docsignore` reader in `load_config`. + `_compile_docsignore_pattern` + `compile_exclude_predicate` helpers (~150 lines, stdlib only). Threaded `predicate=` through `_iter_doc_texts`, `walk`, `check_tree`, `query_docs`, `_refresh_index`. + `_add_exclude_flag` argparse helper. + `--exclude` on idx/check/list/migrate; + `--exclude-ext` / `--summary` / `--only` / `--group-by` on migrate; mutex group `--summary` ⊻ `--json`; + `--body-from` on `new`. Predicate built + threaded at the `_cmd_index` / `_cmd_check` / `_cmd_list` handler layer (the migrate-side predicate-build lands in Phase 6 once `plan_migration` exposes the surface). Managed-marker refusal comment extended with the M8 OQ1 `[exclude]` carve-out. |

#### Actions taken

1. Extended `Config` with `exclude_dirs` / `exclude_globs` /
   `exclude_exts` / `docsignore_patterns` (all defaulted to
   `()`). Docstring extended with the M8 (F3) note. No
   `__post_init__` changes — the new fields are tuples or
   defaulted, and `load_config` already coerces.
2. Extended `MigrationPlan` with `excluded_count: int = 0`,
   `excluded_breakdown: tuple[tuple[str, int], ...] = ()`,
   `suppressed_exts: tuple[str, ...] = ()`. Docstring marks
   all three HUMAN-OUTPUT ONLY per OQ1. `migration_to_json`
   left untouched — the JSON schema stays flat.
3. Extended `load_config` to read `[exclude]` table from
   `.docs.toml` (dirs/globs/exts → tuples) and `.docsignore`
   raw lines from the tree root if present. No nested-file
   support — OQ-B-pinned.
4. Authored `_compile_docsignore_pattern` (returns `None` for
   blanks/comments; emits `(negate, regex)` for everything
   else) and `compile_exclude_predicate` (layers dirs / globs /
   exts / docsignore additively; returns a single
   `Callable[[str], bool]`). The two helpers are stdlib-only
   (`re` only; no `fnmatch` after lint cleanup — the
   docsignore translator handles `*` / `**` / `?` uniformly).
5. Threaded an optional `predicate: Callable[[str], bool] | None
   = None` parameter through `_iter_doc_texts`, `walk`,
   `check_tree`, `query_docs`, `_refresh_index`. Default
   `None` keeps every pre-M8 caller backward-compatible.
6. Wired the predicate at the `_cmd_index` / `_cmd_check` /
   `_cmd_list` verb handlers via `compile_exclude_predicate(
   config, args.exclude)`. The `_cmd_migrate` predicate-build
   waits for Phase 6 (it depends on `plan_migration` exposing
   `cli_excludes` / `cli_exclude_exts` keyword args).
7. Argparse extension: `_add_exclude_flag` helper applied to
   four subparsers (idx, check_p, list_p, migrate_p). On
   `new_p` added `--body-from`. On `migrate_p`: moved `--json`
   into a `--summary` ⊻ `--json` mutex group, added `--only
   {ambiguous}`, `--group-by {role,confidence}`,
   `--exclude-ext EXTS` (csv).
8. Updated `_cmd_migrate` managed-marker comment with the
   M8 (OQ1) carve-out: `[exclude]` joins `[migrate]` as an
   allowed foreign-tree sidecar section.
9. Quality gate clean: ruff / format / mypy / `docs check
   docs/` all exit 0.

#### Issues / decisions

- **`fnmatch` import removed** after first lint pass — the
  docsignore translator handles `*` / `**` / `?` uniformly,
  so the standard-library `fnmatch.fnmatchcase` is redundant.
  The plan recommended either path; rolled-our-own won.
- **Dir-match semantic** is "any segment matches the dir name"
  rather than "the rel path starts with `<dir>/`". Pinned by
  test 1 of `test_exclude.py` (`--exclude build/` excludes
  `build/a.md` at the root) AND the `**/build/**` docsignore
  case (which expects `nested/build/y.md` to match). The
  predicate's dir-name check on `segments[:-1]` covers both.
- **`getattr(args, "exclude", []) or []`** in the verb handlers
  guards against the verb not having `--exclude` registered
  (defensive; today every verb that walks the tree does).
- **Predicate plumbing already flipped 3 RED tests GREEN at
  Phase 5** beyond the argparse-error → assertion-error
  transition: the `index` / `check` / `list` arms of
  `test_docs_toml_exclude_dirs_applies_tree_wide` and
  `test_docs_toml_exclude_globs_apply_tree_wide`. This is
  expected — `load_config` reads `[exclude]` regardless of
  verb. The `migrate` arm stays RED until Phase 6 wires the
  predicate into `plan_migration`.

#### Exit criteria

- [x] `Config` carries `exclude_dirs` / `exclude_globs` /
      `exclude_exts` / `docsignore_patterns` (defaulted; M7
      callers unchanged).
- [x] `MigrationPlan` carries `excluded_count` /
      `excluded_breakdown` / `suppressed_exts` (defaulted;
      OMITTED from `migration_to_json` per OQ1).
- [x] `load_config` reads `[exclude]` and `.docsignore`.
- [x] `compile_exclude_predicate` exists and returns a single
      layered predicate per OQ2.
- [x] `_iter_doc_texts` / `walk` / `check_tree` / `query_docs`
      / `_refresh_index` each carry a `predicate=` keyword.
- [x] All M8 argparse flags wired; `--summary` ⊻ `--json`
      mutex enforced by argparse.
- [x] `_cmd_migrate` managed-marker comment carries the M8
      OQ1 carve-out for `[exclude]`.
- [x] Quality gate clean: ruff / ruff-format / mypy / `docs
      check docs/`.
- [x] **340 GREEN / 29 RED (369 total)** — argparse-error
      REDs flipped to behaviour REDs as planned; the 12 new
      GREEN items split between 4 mutex-now-real flips
      (`test_summary_and_json_are_mutually_exclusive`,
      `test_summary_and_only_ambiguous_compose`, the two
      F7 footer-absent locks newly satisfied, …) and 8
      predicate-already-works flips (the index/check/list arms
      of tests 5 + 6 in `test_exclude.py`, plus
      `test_body_from_with_missing_value_argparse_errors`,
      `test_summary_emits_one_line_per_file`,
      `test_group_by_role_orders_plan_by_role`,
      `test_migrate_exclude_supports_glob_patterns[*memo*-memo]`).
      The 29 remaining REDs are all behaviour-RED — Phase 6
      makes them GREEN (except the 5 F8 skill-content REDs
      which Phase 7 handles).

### Phase 6 — Implement Core

**Completed:** 2026-05-25

#### Objective

Wire the Phase 5 schema + predicate into the migrate plan
builder + printer; implement the M8 triage flags (`--summary`,
`--only ambiguous`, `--group-by role|confidence`), the default
plan footer summary, the non-md sibling surfacing (with
`--exclude-ext` suppression), and `docs new --body-from <PATH|-`
with the OQ-E metadata-block refusal heuristic. Flip every
F3/F6/F7/F9 RED test GREEN; F8 stays RED for Phase 7.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `src/docs_cli/cli.py` | Modify | `plan_migration` gained `cli_excludes` + `cli_exclude_exts` kwargs; predicate built + applied; excluded files counted + bucketed by top-level dir prefix; `MigrationPlan` populated with `excluded_count` + `excluded_breakdown` + `suppressed_exts`. `_print_migration_plan` gained `mode` / `only` / `group_by` kwargs — default mode prints the verbose per-file block; summary mode prints one `path<60> role<12> conf<8> notes` line per file. Both modes share the same footer order (per OQ3, bottom): excluded counts → non-md siblings (suppressed per `suppressed_exts`) → multi-project hints → default summary (`summary:` / `roles:` / `confidence:` / `ambiguities:`). New `_AMBIGUITY_BUCKETS` constant + `_ambiguity_bucket` helper. `_cmd_migrate`: parses `--exclude-ext` CSV via inline tuple comprehension; passes `cli_excludes` + `cli_exclude_exts` to `plan_migration`; passes `mode/only/group_by` to the printer. `_cmd_new`: `--body-from -` reads stdin; `<path>` reads file (exit 2 on missing); OQ-E heuristic scans first 20 lines for `^[A-Z][A-Za-z-]+:\s` and refuses with the documented error message (BEFORE the dry-run check per OQ4); scaffold + body compose so `written.endswith(body)` byte-equal holds. `_cmd_migrate` managed-marker carve-out widened: `[exclude]` waives refusal even alongside `[project]/[archive]/[vocabulary]` so `test_docs_toml_exclude_dirs_applies_tree_wide[migrate]` etc. flip GREEN. |

#### Actions taken

1. Extended `plan_migration` signature to take `cli_excludes:
   Sequence[str] = ()` and `cli_exclude_exts: Sequence[str] = ()`.
   Inside, built `predicate = compile_exclude_predicate(config,
   cli_excludes, cli_exclude_exts)`, iterated the raw walker
   output, partitioned into `pairs` (kept) and an excluded
   bucket-counter (`excluded_breakdown_map`). Populated the
   three new `MigrationPlan` fields at return time.
2. `excluded_breakdown` prefix attribution: a path's top-level
   dir + `/` is its bucket; root-level excluded files fall back
   to the bare filename. Matches the test 9 footer wording
   "5 files excluded under build/".
3. Rewrote `_print_migration_plan` with three new kwargs.
   Default mode is byte-identical to M7's per-file block.
   Summary mode swaps in the column shape pinned by
   `test_summary_emits_one_line_per_file` (3 lines for
   kebab-tiny).
4. Footer order (per OQ3, all-after): excluded counts,
   non-md siblings, multi-project hints, default summary. The
   default summary is emitted unconditionally (even with no
   files / no ambiguities); the test pins all four tokens to
   the footer slice via `out.index("summary:")`.
5. Authored `_AMBIGUITY_BUCKETS` (4 stable keys —
   notes-fallback, synthesised-h1, out-of-vocab, collision) +
   `_ambiguity_bucket(note)` helper so the footer
   `ambiguities:` token stays human-stable across runs.
6. `_cmd_migrate`: parse `--exclude-ext` once via inline
   tuple comp; pass both `cli_excludes` and `cli_exclude_exts`
   into `plan_migration`; pass `mode/only/group_by` into the
   printer. The single-source-of-CSV-parse principle from OQ8.
7. `_cmd_new --body-from`: read body from stdin (`-`) or file
   (exit 2 with `not found` on missing); OQ-E heuristic scans
   first 20 lines for `^[A-Z][A-Za-z-]+:\s` and refuses with
   the documented three-line error message + 5-line preview;
   validation BEFORE the dry-run check per OQ4.
8. Composition: `text + body` when body starts with `\n`,
   else `text + "\n" + body`. Keeps `written.endswith(body)`
   byte-equal as test 3 asserts.
9. Widened the M7 managed-marker refusal carve-out so a
   `.docs.toml` carrying `[project]` + `[exclude]` is accepted
   by `migrate`. Rationale: `[exclude]` is the operator's
   explicit "use migrate to triage / re-migrate this tree but
   skip the listed paths" signal. The
   `test_migrate_refuses_a_docs_root` lock (no `[exclude]`)
   stays GREEN.

#### Issues / decisions

- **Managed-marker carve-out widening.** The Step 1 OQ1
  comment said the refusal set stays unchanged; the M8 RED
  tests force the widening (parametric tests over
  `[index, check, list, migrate]` would otherwise have no way
  to test the predicate against a fixture that's a docs root
  for the other three verbs). Surfaced as a Phase 6 "test
  contract is stricter than the planning OQ" finding. The
  widening is conservative: it activates only when `[exclude]`
  is present, matching the operator's explicit consent.
- **`fnmatch` not needed.** The docsignore translator already
  handles `*` / `**` / `?` correctly, so the glob bucket of
  the predicate uses the same translator — no `fnmatch` import.
- **Footer placement (OQ3).** All footer sections emit AFTER
  per-file lines. `test_default_plan_footer_shows_counts`
  anchors via `out.index("summary:")` so any ordering with
  the four tokens after that anchor passes.
- **Default summary always emitted.** Even on an empty plan
  the four tokens print (with `n_files=0` / `none`), so the
  test's substring assertions never miss a token because of
  early-exit paths.
- **`--body-from` separator.** `scaffold_doc` ends with one
  `\n`. Body starting with `\n` → no extra newline;
  otherwise prepend `\n`. Test 3 asserts
  `written.endswith(body)` byte-equal; both branches satisfy
  the contract.
- **Quality gate clean** after one round of `ruff format`
  (SIM108 ternary) — single trivial style nit, no logic
  change.

#### Exit criteria

- [x] `test_exclude.py` — 22/22 GREEN (was 20 RED + 2 lock).
- [x] `test_triage_flags.py` — 6/6 GREEN (was 6 RED).
- [x] `test_non_md_surfacing.py` — 3/3 GREEN (was 2 RED + 1
      lock).
- [x] `test_body_from.py` — 8/8 GREEN (was 7 RED + 1 lock).
- [x] `test_migrate.py::test_summary_and_json_are_mutually_exclusive`
      — GREEN (Phase 5 already flipped via mutex group).
- [x] M7's 324 + M5/M6 baseline tests stay GREEN.
- [x] `test_skill_adoption.py` — 5 RED (intended — Phase 7).
- [x] Quality gate clean: ruff / ruff-format / mypy / `docs
      check docs/`.
- [x] Tally: **364 GREEN / 5 RED (369 total)**.

### Phase 7 — Update Tool/Wrapper Layer (skill rewrite)

**Completed:** 2026-05-25

#### Objective

Author the F8 skill-content deliverables (adoption playbook +
`.docs.toml` template); make the minimal SKILL.md additions
(four adoption-trigger phrases in the description + a one-line
pointer block); extend `_SKILL_RELATIVE_FILES`; bump the
project version 1.2.0 → 1.3.0 across `pyproject.toml`,
`cli.py`, and `tests/test_packaging.py`; widen the M7 spec docs
(`cli.md`, `convention.md`, `architecture.md`) with the M8
surface; add a 5-line README "Adoption" section; author the
`CHANGELOG.md` `## 1.3.0 — UNRELEASED` block; resync the
skill-reference lockstep after the spec edits.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `src/docs_cli/skill/SKILL.md` | Modify | Description: 4 adoption-trigger phrases appended ("adopt this directory", "migrate this folder", "bring this into docs convention", "import existing markdown specs") — well under the 1024-char ceiling. Body: new one-line pointer block before the "Three things never to hand-edit" heading, naming both `references/adoption-playbook.md` and the bundled `docs-toml-template.toml`. M7 sweep misses cleaned up — `docs list --status` → `--lifecycle`; hand-flip `Status:` → `Lifecycle:`; metadata-block enumeration starts with `Lifecycle:` instead of `Status:`. Size: 89 lines (well under the 500-line budget). |
| `src/docs_cli/skill/references/adoption-playbook.md` | Create | 343 lines. Frontmatter (`Lifecycle: active`, `Role: guide`, `Project: docs`, `Updated: 2026-05-25`, `Related: child-of SKILL.md` + `references: cli.md` + `references: convention.md`). Required H2s: `## When this applies`, `## Step 1 — Dry-run plan`, `## Step 2 — Triage the plan`, `## Step 3 — Create .docs.toml from references/docs-toml-template.toml`, `## Step 4 — Iterate`, `## Step 5 — Apply`, `## Step 6 — Verify`, `## Worked example`, `## Pitfalls`. Pitfalls cover `Status:`→`Lifecycle:` (M7 F0), `_v2`/`_Draft` non-role suffixes (M7 F10), inferred-project-name override (M7 F5 + F11), generated-data dirs needing `--exclude` (M8 F3), sidecars via `--body-from` for non-md binaries (M8 F7 + F9), multi-project subdir hint (F5). Generic sanitised content; sourced from kebab-tiny / snake-medium-style examples; NO third-party names. |
| `src/docs_cli/skill/references/docs-toml-template.toml` | Create | ~90 lines. `[exclude]` (dirs/globs/exts), `[migrate]` (role_suffixes inline-table + commented project_name), `[vocabulary]` (add_lifecycles + add_roles), plus commented `[project]` and `[archive]` for completeness. Every example commented. Heavily commented prose explaining each section's purpose. Parses cleanly via `tomllib.loads`. |
| `src/docs_cli/cli.py` | Modify | `__version__` 1.2.0 → 1.3.0. `_SKILL_RELATIVE_FILES` extended with `use-cases.md` + `adoption-playbook.md` + `docs-toml-template.toml`. The `use-cases.md` addition closes a pre-existing packaging gap — the file shipped in the wheel as package-data but `install-skill --copy` walked this tuple, so the file silently never landed on a host. |
| `pyproject.toml` | Modify | `version = "1.2.0"` → `"1.3.0"`. |
| `tests/test_packaging.py` | Modify | 3 occurrences of `1.2.0` → `1.3.0` (the docstrings + version assertions + the wheel/sdist filename pins). Two helper function names refreshed: `test_a3_project_version_is_1_2_0` → `..._1_3_0`; `test_c2_docs_version_is_1_1_0` → `..._1_3_0` (existing rename oversight from M7 — body already asserted 1.2.0). |
| `docs/cli.md` | Modify | `docs new` synopsis: `[--body-from PATH|-]`. `docs index` / `check` / `list` synopses: `[--exclude PATTERN]`. `docs migrate` synopsis: full new surface (`--summary` / `--only` / `--group-by` / `--exclude` / `--exclude-ext`; mutex `--json`/`--summary`). New "Triage flags (M8 — F6)" + "Plan footer (M8 — F3/F5/F6/F7)" subsections under migrate. New top-level "Common: exclusion" section before "Output conventions" documenting the four layered sources. M8 (OQ1) carve-out bullet added to the migrate refusal description. |
| `docs/convention.md` | Modify | New `## Exclusion` section after "Subdirectories" / before "INDEX file" covering all four layered sources + the OQ-B `.docsignore` syntax subset + cross-link to the bundled adoption playbook. Existing "Non-Markdown files in the tree" section extended with a one-paragraph "Migration-time surfacing (M8 — F7)" note. |
| `docs/architecture.md` | Modify | Layout sketch: `__version__ = "1.3.0"`; config row notes the M8 additions; skill/references/ tree extended with `use-cases.md`, `adoption-playbook.md`, `docs-toml-template.toml` (bundle-only, no `docs/` mirror). `Config` module section: four new fields documented + `compile_exclude_predicate` helper added. `walker` module section: `predicate=` keyword added with M8 F3 cross-reference. |
| `README.md` | Modify | Commands block: `--body-from` + `--exclude` synopses added. New `## Adopting an existing tree` section (5 lines) right after Install. Status section: M8 row added; publish-strategy framing bumped (1.2.0/1.3.0 narrative). |
| `CHANGELOG.md` | Modify | New `## 1.3.0 — UNRELEASED` block at the top: Added (12 bullets covering F3/F6/F7/F8/F9), Changed (migrate carve-out widening + `_SKILL_RELATIVE_FILES` extension), Notes (publish batching + MigrationPlan-fields-omitted-from-JSON note). |
| `src/docs_cli/skill/references/cli.md` | Modify | Lockstep re-sync after `docs/cli.md` edits. Byte-identical mirror. |
| `src/docs_cli/skill/references/convention.md` | Modify | Lockstep re-sync after `docs/convention.md` edits. Byte-identical mirror. |
| `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Re-synced after the `docs touch` bumps + the new skill-reference-content drops. |

#### Actions taken

1. Read `tests/test_packaging.py` per OQ7 — confirmed it
   `zipfile`-inspects the wheel for fixed paths, doesn't iterate
   `_SKILL_RELATIVE_FILES`. Adding files to the tuple is safe;
   only the version pins (`1.2.0` → `1.3.0`) need updating.
2. Bumped version: `pyproject.toml`, `cli.py __version__`, and 3
   string occurrences in `tests/test_packaging.py` (helper
   function names + the assertion bodies). Also refreshed
   `test_c2_docs_version_is_1_1_0` → `..._1_3_0` — a pre-
   existing rename oversight in the function name.
3. Extended `_SKILL_RELATIVE_FILES` with `use-cases.md` +
   `adoption-playbook.md` + `docs-toml-template.toml`.
4. Authored `references/docs-toml-template.toml` — `[exclude]`,
   `[migrate]` (with inline-table `role_suffixes = {}` valid
   TOML), `[vocabulary]`, plus commented `[project]` / `[archive]`.
   Verified parses cleanly via `tomllib.loads` and that all three
   required substrings (`[exclude]` / `[migrate]` / `[vocabulary]`)
   are present.
5. Authored `references/adoption-playbook.md` — frontmatter with
   full M5/M7 metadata; all nine required H2s; worked example
   sourced from the kebab-tiny / snake-medium-style fixtures
   (generic `Foo` / `foo-bar` naming, NO third-party names);
   pitfalls section covering all six known traps.
6. SKILL.md minimal additions: appended 4 adoption-trigger
   phrases to the description (well under 1024 chars); added a
   one-line pointer block before the "Three things never to
   hand-edit" heading; swept three M7 misses in the body
   (`--status` → `--lifecycle`; hand-flip `Status:` → `Lifecycle:`;
   metadata enumeration). Final body 89 lines (under the 500-
   line budget). All M7 verbs still named in the body so
   `test_every_named_verb_is_a_real_subcommand` stays GREEN.
7. Widened the docs (`cli.md`, `convention.md`, `architecture.md`)
   with the M8 surface — new flag synopses, the "Triage flags"
   + "Plan footer" subsections, the "Common: exclusion" top-
   level section, the `Config` schema additions, the layout
   sketch extension, and the OQ-B `.docsignore` syntax subset
   under `## Exclusion`.
8. Added 5-line README "Adoption" section after Install; updated
   the Commands block synopses; bumped the Status section's
   M8 row + publish-strategy narrative.
9. Authored `CHANGELOG.md ## 1.3.0 — UNRELEASED` (Added /
   Changed / Notes; ~80 lines covering every F3/F6/F7/F8/F9
   surface change).
10. Touched `docs/cli.md` / `docs/convention.md` /
    `docs/architecture.md` via `docs touch`; regen'd
    `docs/INDEX.md` + snapshot in lockstep. Re-cp'd
    `docs/{cli,convention}.md` into
    `src/docs_cli/skill/references/` to satisfy
    `tests/test_skill_refs.py` byte-identity.

#### Issues / decisions

- **OQ7 verified.** `tests/test_packaging.py` inspects the
  wheel zip directly; no iteration over
  `_SKILL_RELATIVE_FILES`. Adding files to the tuple required
  no test edit beyond the version bumps.
- **Pre-existing test_c2 function name typo** ("1_1_0") was
  also fixed in the same pass — body asserted 1.2.0 before
  this commit, now correctly asserts 1.3.0 and the function
  name matches.
- **SKILL.md size stays well within the 500-line budget** —
  89 lines after the M8 additions. The plan's "stay ≤ ~90
  lines" target is met exactly.
- **Worked-example sanitisation.** The adoption playbook's
  worked example uses generic `Foo` / `foo` naming +
  hypothetical filenames — no third-party product / customer
  / feature names. The fixture pool inspected is the M7
  sanitised set (`tests/fixtures/trees/real-trees/`).
- **`docs-toml-template.toml` inline-table syntax** for
  `role_suffixes = {}` — valid TOML, parses cleanly via
  `tomllib`; matches the M7 `[migrate] role_suffixes`
  convention.

#### Exit criteria

- [x] `tests/test_skill_adoption.py` — 5/5 GREEN (was 5 RED).
- [x] `tests/test_skill.py` — still GREEN (size budget OK; new
      pointer line increased to 89 lines from 84).
- [x] `tests/test_skill_refs.py` — still GREEN (lockstep re-sync
      successful).
- [x] `tests/test_packaging.py` — version pins updated 1.2.0 →
      1.3.0; tests don't fire at the unit-level pytest run (the
      Group B/C/D/E tests build a wheel + run it, gated at
      Phase 8).
- [x] `docs check docs/` — exit 0.
- [x] `docs index --root docs/` — INDEX.md regen'd; snapshot
      lockstep maintained.
- [x] Ruff / ruff-format / mypy — clean.
- [x] **All 369 tests GREEN.** Every M8 RED has flipped to
      GREEN — the spec contract is fully implemented and
      tested.

### Phase 8 — Run Tests (GREEN)

**Completed:** 2026-05-25

#### Objective

Capture the full GREEN gate verbatim before the load-bearing
fresh-subagent gate at Phase 9. Eight commands, each captured
to `/tmp/m8-phase-8-green.txt`:

1. `pytest tests/ -q`
2. `ruff check .`
3. `ruff format --check .`
4. `mypy`
5. `docs check docs/`
6. `docs index --root docs/ --dry-run`
7. `python -m build`
8. `python -m twine check dist/*`

#### Verbatim gate (excerpt)

```text
=== pytest ===
369 passed in 9.86s

=== ruff check ===
All checks passed!

=== ruff format --check ===
33 files already formatted

=== mypy ===
Success: no issues found in 34 source files

=== docs check docs/ ===
docs: no violations found

=== docs index --root docs/ --dry-run head ===
# docs — Documentation
...

=== rm dist + python -m build ===
Successfully built docs_cli-1.3.0.tar.gz and docs_cli-1.3.0-py3-none-any.whl

=== twine check ===
Checking dist/docs_cli-1.3.0-py3-none-any.whl: PASSED
Checking dist/docs_cli-1.3.0.tar.gz: PASSED

=== ls dist/ ===
docs_cli-1.3.0-py3-none-any.whl
docs_cli-1.3.0.tar.gz
```

`docs --version` → `docs 1.3.0`. Full capture at
`/tmp/m8-phase-8-green.txt`.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/m8-adoption-workflow-log.md` | Modify | This Phase 8 entry + TDD Phase Progress row flipped Complete. |
| `dist/docs_cli-1.3.0-py3-none-any.whl` + `dist/docs_cli-1.3.0.tar.gz` | Create | Local build artefacts. NOT committed (`dist/` is gitignored); Phase 10 may rebuild as the closeout step. |

#### Issues / decisions

- **`tests/test_packaging.py` runs the full build path** as part
  of pytest (it has session-scoped fixtures `built_dist` and
  `wheel_venv`). Those tests already exercised the wheel build
  + venv install + `docs install-skill --dest` and all passed —
  no separate Phase 8 step required to verify wheel
  internals. The 369 GREEN count includes the 22 packaging
  tests (B/C/D/E groups).
- **45 new M8 collected items in total** (41 originally-RED +
  4 originally-GREEN regression-lock + the audit-tightening
  carry-over) all flipped GREEN as planned. Combined with the
  324 M7-era baseline → 369 collected.
- **`docs index --dry-run`** produces stdout that matches the
  on-disk INDEX.md byte-for-byte (after the Phase 7 regen +
  snapshot cp). No diff.

#### Exit criteria

- [x] pytest 369 GREEN, 0 RED, 0 skipped.
- [x] Ruff / ruff-format / mypy all clean.
- [x] `docs check docs/` exit 0.
- [x] `docs index --dry-run` no diff.
- [x] `python -m build` produced `docs_cli-1.3.0-py3-none-any.whl`
      + `docs_cli-1.3.0.tar.gz`.
- [x] `twine check dist/*` PASSED on both artefacts.
- [x] `docs --version` reports `docs 1.3.0`.
- [x] Verbatim capture written to `/tmp/m8-phase-8-green.txt`
      for the Phase 9 conductor.

### Phase 9 — Fresh-subagent integration gate

**Completed:** 2026-05-25

#### Objective

Validate that the adoption workflow is agent-driveable
end-to-end against the M7 fixtures the M8 author did not
specifically tune for. The pass criterion (per OQ-G): ≥ 2 of
3 fresh Opus subagents complete the loop unattended.

#### Two-stage execution history

The Phase 9 gate ran in two stages:

**Stage 1 — same-instance dogfood substitution (initial pass).**
The implementation agent driving phases 5-10 could not nest
`Agent` tool calls, so it substituted a same-instance dogfood
pass — running every adoption step against each fixture in its
own `/tmp/m8-gate-N/` workspace with the freshly-built 1.3.0
wheel + freshly-installed skill. The mechanics were tested
faithfully and one substantive playbook bug surfaced and was
fixed (Step 3 ordering vs the OQ1 `[exclude]` carve-out — see
**Playbook iteration** below). What stage 1 did NOT verify was
the "fresh model with no prior context" property the plan calls
out — the same instance authored the playbook and ran the
pass.

**Stage 2 — real fresh-subagent gate (operator-directed re-run,
2026-05-25).** Per operator decision the conductor (running at
the top level, with `Agent` tool access) spawned three fresh
Opus subagents in parallel via the Agent tool, each with a
minimal "adopt this directory" prompt and explicit `/tmp` paths
to the wheel-installed `docs` binary + the bundled skill — no
hints, no playbook quotes, no host-skill-discovery. **All 3
completed the loop unattended; no further playbook iterations
needed.**

#### Playbook iteration (from stage 1)

Stage 1's Run 1 (kebab-tiny) initially failed because the
original playbook's Step 3 said "write `.docs.toml` with
`[project] name = ...` before `--apply`". That triggers the
`_cmd_migrate` managed-marker refusal: `docs: <tree> is already
a docs root (.docs.toml has ['project']) — migrate is for
foreign trees`. The M8 OQ1 carve-out only waives the refusal
when `[exclude]` is also present; for trees that need no
persistent excludes, writing `.docs.toml` before `--apply`
blocks the apply.

Edits applied to
`src/docs_cli/skill/references/adoption-playbook.md`:

- Rewrote Step 3 with an "IMPORTANT ordering note" spelling
  out three patterns (no persistent excludes → defer
  `.docs.toml` to after `--apply`; persistent excludes →
  write `.docs.toml` with ONLY `[exclude]`/`[migrate]` and
  then `--apply`; one-off excludes → CLI flags only, no
  `.docs.toml`).
- Extended Step 5 with the carve-out refusal explainer + the
  exact error string.
- Renamed Step 6 to "Verify (`docs check <dir>` exit 0;
  write final `.docs.toml`; commit)" with a code example for
  post-`--apply` `.docs.toml` authoring.

Rebuilt the wheel + reinstalled the skill before stage 2.

#### Per-run log (stage 2 — real fresh-subagent gate)

##### Run 1 — kebab-tiny (3 files)

**Workspace:** `/tmp/m8-gate-1/{venv,skill,work-tree}/`
**Wheel:** `dist/docs_cli-1.3.0-py3-none-any.whl` (rebuilt
fresh from the post-stage-1 branch HEAD).
**Skill:** materialised via `docs install-skill --dest
/tmp/m8-gate-1/skill/` — 5 files present (`SKILL.md` +
`references/{convention,cli,use-cases,adoption-playbook,
docs-toml-template}.{md,toml}`).
**Subagent prompt:** minimal — adopt the directory at the
explicit /tmp path; read SKILL.md at the explicit /tmp path
(no host-skill auto-discovery); commit when done.

**Outcome:** PASS unattended (no iterations). Read SKILL.md →
followed pointer to `adoption-playbook.md` → ran
`docs migrate --summary` (3 files / 0 ambiguous / no non-md
siblings / all high confidence) → recognised the
"no excludes needed" path → ran `--apply --quiet` → wrote
`.docs.toml` with `[project] name = "foo-bar"` → `docs
index --root` → `docs check` exit 0 → committed.

**Final commit sha:** `8d80627baec7af2183be44e597f3b78f353d0c5f`.

##### Run 2 — snake-medium (17 files)

**Workspace:** `/tmp/m8-gate-2/{venv,skill,work-tree}/`

**Outcome:** PASS unattended (no iterations). Dry-run
plan showed 17 files / 11 high + 4 medium + 2 low
confidence / project normalised from "Foo" → "foo".
Spot-checked the two low-confidence files
(`Foo_Architecture.md`, `Foo_Strategy_v2.md`) — both
intentional notes-fallback per the playbook's Pitfalls
section. Ran `--apply --quiet` → wrote `[project] name =
"foo"` → `docs index` → `docs check` exit 0 → committed.

**Final commit sha:** `eb62d9de07dffaef49f29ddc738cf5c8ee25a4d8`.

##### Run 3 — snake-large (72 files)

**Workspace:** `/tmp/m8-gate-3/{venv,skill,work-tree}/`

**Outcome:** PASS unattended (no iterations). 72 files /
6 ambiguous (all notes-fallback — Architecture, Cards,
Constraints, Decision_Tree, Handoff, Strategy_v2 — the
documented intentional pattern incl. the `_v2` revision-
marker case the playbook explicitly calls out). No
`multi_project_hints`, no non-md siblings, no
collisions. Triage via `--summary --only ambiguous`
showed all 6 ambiguous lines were the expected
notes-fallback. Ran `--apply` → wrote `[project] name =
"foo"` → `docs index` → `docs check` exit 0 →
committed.

**Final commit sha:** `ba09da9e5e60ac484e36a10b235b8079988b746b`.

#### Polish opportunities surfaced by the real-subagent runs

All three fresh subagents flagged minor friction items.
Documented as follow-ons; none blocked the loop:

- **`--quiet` does not actually suppress the per-file plan
  output** when paired with `--apply`. Three subagents
  followed Step 5's `--apply --quiet` example verbatim and
  all noticed the per-file block still printed. Worth wiring
  through OR updating the playbook to set expectations.
- **INDEX.md authoring/timing in Step 5 → Step 6 is fuzzy.**
  `--apply` does not produce `INDEX.md`; the `docs index`
  invocation in Step 6 is actually the FIRST index
  generation, not a regeneration smoke-test. A one-line
  "always run `index` before the final commit so `INDEX.md`
  is part of the adopted state" would remove the guesswork.
- **Step 6 heading vs. body ordering.** Heading reads
  "check → write final `.docs.toml` → commit"; the body
  text supports either ordering. `docs check` passes via
  cwd-fallback whether `.docs.toml` exists or not, so both
  orderings work — but the doc could be tightened.
- **Project-name inference source (Run 1 only).** The
  directory basename was `work-tree` but `migrate` correctly
  inferred `project: foo-bar` from the filename prefix. The
  playbook describes project as basename-derived with
  `--config-project` / `[migrate] project_name` as the
  override; no mention of prefix-based inference. Adding a
  "the `project` field reflects whichever inference path the
  migrator took — confirm it matches the operator's intent"
  line would close the gap.
- **`git diff INDEX.md` smoke step lands oddly on first
  adoption** (no pre-existing `INDEX.md` to diff against).
  Re-wording would help.
- **Commit-message convention unprescribed** — three
  subagents all noticed and all picked sensible phrasings
  matching the worked example. Acceptable to leave open.

#### Adopted-state capture

Copied each `/tmp/m8-gate-N/work-tree/` content (minus
`.git/`) into
`tests/fixtures/trees/real-trees-adopted/{kebab-tiny,
snake-medium,snake-large}/` — refreshed from the stage-2
real-subagent runs. Each adopted fixture verified locally
via the in-tree CLI (`.venv/bin/docs check <path>`) exit 0.

**Sanitisation grep** (mirroring M7 log line 405 pattern):
```
grep -ril -E 'truck.?tech|trucktech|bit.?holders' \
    tests/fixtures/trees/real-trees-adopted/
```
Zero hits — the fixtures inherit M7's sanitisation; the
adoption-time edits are confined to metadata blocks
(`Lifecycle: active`, `Role: ...`, `Project: foo`/`foo-bar`,
`Updated: 2026-05-25`).

#### Files changed

| File | Action | Notes |
|---|---|---|
| `src/docs_cli/skill/references/adoption-playbook.md` | Modify (stage 1) | Step 3 rewritten with the IMPORTANT-ordering-note block; Step 5 extended with the carve-out refusal explainer; Step 6 extended with the post-`--apply` `.docs.toml` authoring example. |
| `tests/fixtures/trees/real-trees-adopted/kebab-tiny/` | Create / refresh | 3 .md + `.docs.toml` + `INDEX.md` — adopted state from stage-2 Run 1 (sha `8d80627`). |
| `tests/fixtures/trees/real-trees-adopted/snake-medium/` | Create / refresh | 17 .md + `.docs.toml` + `INDEX.md` — adopted state from stage-2 Run 2 (sha `eb62d9d`). |
| `tests/fixtures/trees/real-trees-adopted/snake-large/` | Create / refresh | 72 .md + `.docs.toml` + `INDEX.md` — adopted state from stage-2 Run 3 (sha `ba09da9`). |
| `dist/docs_cli-1.3.0-{whl,tar.gz}` | Rebuild | Rebuilt twice — once mid-stage-1 after the playbook iteration, once before stage 2 to pick up the audit fixes. NOT committed (`dist/` is gitignored). |

#### Issues / decisions

- **Two-stage execution acknowledged.** Stage 1 (same-instance
  dogfood) caught and fixed the real playbook bug; stage 2
  (real fresh subagents, operator-directed) verified the
  fresh-context property. The plan-intended single-stage gate
  was not achievable from inside the implementation agent's
  nested-tool restriction; the conductor's top-level Agent
  access closed the gap.
- **Playbook bug surfaced + fixed in stage 1 (Step 3/5/6
  ordering).** Real bug; iterated; stage 2's three subagents
  followed the corrected playbook end-to-end with no further
  iterations. Mirrors the spec's intent: "if a subagent
  stalls on something the playbook doesn't anticipate, that's
  a fail — iterate."
- **Polish opportunities documented above (`--quiet`,
  INDEX timing, project-name inference, etc.)** — all three
  stage-2 subagents independently surfaced the same friction
  items; none blocked the loop; recorded as follow-ons for a
  future polish pass (could fold into Step 3 simplify or a
  dedicated post-M8 playbook polish).
- **`MigrationPlan.suppressed_exts` ordering preservation.**
  `--exclude-ext` values are normalised lowercase + stripped
  of `.`; the predicate uses the same lookup. Verified
  working in Phase 6; no Phase 9 issue.

#### Exit criteria

- [x] 3/3 fresh-subagent runs PASS unattended (stage 2).
- [x] 3/3 fixtures adopted; `docs check <fixture>` exit 0
      on each.
- [x] Adopted state committed to
      `tests/fixtures/trees/real-trees-adopted/<tree>/`
      (refreshed from stage-2 runs).
- [x] Sanitisation grep zero hits.
- [x] Playbook iteration applied + documented (stage 1);
      stage 2 ran on the corrected playbook with no further
      iterations needed.

### Phase 10 — Quality, Docs, Refactor (publish DEFERRED to M9)

**Completed:** 2026-05-25

#### Objective

Polish + ship locally. Per OQ-C: NO publish, NO tag, NO
GitHub release — that surface is M9.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/m8-adoption-workflow.md` | Modify | Phase Checklist boxes checked; Milestone-completion summary appended (mirrors the M7 closeout structure). |
| `docs/m8-adoption-workflow-log.md` | Modify | This Phase 10 entry + TDD Phase Progress row flipped Complete. |
| `docs/status.md` | Modify | M8 milestone-table row → **Complete**; Current-milestone narrative paragraph rewritten to reflect M8 closing; Next-action line names M9 + the release-runbook. |
| `CHANGELOG.md` | Modify | `## 1.3.0 — UNRELEASED` → `## 1.3.0 — 2026-05-25`. |
| `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` | Regenerate | After the three `docs touch` calls; snapshot lockstep maintained. |
| `dist/docs_cli-1.3.0-py3-none-any.whl` + `dist/docs_cli-1.3.0.tar.gz` | Build (LOCAL ONLY) | Rebuilt fresh in Phase 10 from the post-closeout tree. `twine check` PASSED on both. NOT pushed anywhere; `dist/` is gitignored. |

#### Actions taken

1. Dogfood sweep — grep'd `docs/` for stale planning-era
   function names (`migrate_plan`, `_render_migrate_plan`).
   Found references in `docs/m7-migration-accuracy.md` (M7
   historical) + `docs/m8-adoption-workflow.md` (M8 Phase 6
   historical sketch) + `docs/m7-migration-accuracy-log.md`
   (M7 historical). Per plan-doc Phase 10 guidance ("leave
   as-is if the surrounding context makes the historical
   reference clear"), left intact — the milestone-doc Phase 6
   section is explicitly the Phase 1 planning artifact and a
   future reader sees the historical scope from the
   surrounding text.
2. Appended Milestone-completion summary to
   `docs/m8-adoption-workflow.md`: shipped date, Surface
   delivered (one bullet per F3/F6/F7/F8/F9 + OQ1 carve-out
   widening), Tests tally (324 → 369), Fresh-subagent gate
   outcome (3/3 PASS with the same-instance caveat), Ship
   surface (local artefacts; publish deferred), Open
   follow-ons (4 items).
3. Updated `docs/status.md` M8 milestone-table row to
   **Complete**; rewrote the Current-milestone paragraph to
   reflect M8 closing; added Next-action line naming M9.
4. CHANGELOG dated 2026-05-25 (no content change beyond the
   header).
5. `docs touch` on the three modified docs;
   `docs index --root docs/` regen'd; snapshot lockstep
   `cp docs/INDEX.md tests/fixtures/expected/docs-INDEX.md`.
6. Final quality gate (everything exit 0):
   - `pytest tests/ -q` — **369 GREEN, 0 RED, 0 skipped**.
   - `ruff check .` — clean.
   - `ruff format --check .` — 33 files already formatted.
   - `mypy` — Success: no issues found in 34 source files.
   - `docs check docs/` — no violations found.
7. Built artefacts LOCAL ONLY: `rm -rf dist/ && python -m
   build` → `dist/docs_cli-1.3.0-py3-none-any.whl` +
   `dist/docs_cli-1.3.0.tar.gz`. `twine check dist/*` PASSED
   on both. **NO `twine upload`. NO `git tag v1.3.0`. NO
   `gh release create`.**

#### Files of Interest — milestone deliverable mapping

Per the spec pressure-test "tie every shipped file to its
milestone-doc deliverable":

| Shipped file | M8 deliverable |
|---|---|
| `src/docs_cli/cli.py` (Phase 5+6+7 edits — Config + MigrationPlan + predicate + walkers + flags + `--body-from` + version) | F3 (exclude predicate + `[exclude]` + `.docsignore`), F6 (triage flags + footer), F7 (non-md sibling), F9 (`--body-from` + OQ-E refusal), OQ1 (carve-out widening) |
| `src/docs_cli/skill/SKILL.md` | F8 (description triggers + pointer block) |
| `src/docs_cli/skill/references/adoption-playbook.md` (NEW) | F8 (the substantive playbook deliverable) |
| `src/docs_cli/skill/references/docs-toml-template.toml` (NEW) | F8 (the `.docs.toml` starter) |
| `src/docs_cli/skill/references/{cli,convention}.md` | F8 (lockstep mirror of the M8-extended specs) |
| `src/docs_cli/skill/references/use-cases.md` (newly bundled via install-skill) | M8 packaging-gap fix (was shipped in wheel but not by `install-skill --copy`) |
| `pyproject.toml` + `tests/test_packaging.py` | M8 version bump 1.2.0 → 1.3.0 |
| `tests/test_exclude.py` + `test_triage_flags.py` + `test_non_md_surfacing.py` + `test_body_from.py` + `test_skill_adoption.py` + the `test_migrate.py` mutex test | M8 Phase 2 RED baseline (now all GREEN) |
| `tests/fixtures/body-from/` | M8 Phase 3 on-disk fixtures for F9 |
| `tests/fixtures/trees/real-trees-adopted/{kebab-tiny,snake-medium,snake-large}/` (NEW; Phase 9 capture) | M8 Phase 9 committed adopted state per the milestone exit criterion |
| `docs/{cli,convention,architecture}.md` | F8 spec sweep (cli flags + Exclusion section + Config schema) |
| `README.md` | F8 README adoption section + Commands updates |
| `CHANGELOG.md` | F8 release-runbook input — `## 1.3.0 — 2026-05-25` entry |

#### Issues / decisions

- **Phase 9 gate: two-stage execution.** Stage 1 same-instance
  dogfood surfaced + fixed a real playbook bug; stage 2
  (operator-directed real-fresh-subagent re-run, 2026-05-25)
  passed 3/3 unattended on the corrected playbook. Both
  stages documented in the Phase 9 log. Phase 10 closeout
  proceeds on the strength of the verified gate.
- **No publish work at Phase 10.** Per OQ-C the publish is
  M9's scope; Phase 10's job is "ship locally + close out
  the milestone doc + status.md". The release-runbook will
  drive the M9 publish session.
- **`migrate_plan` / `_render_migrate_plan` references in
  historical docs** — left intact per the plan-doc Phase 10
  guidance. They appear inside milestone-doc Phase 6
  sketches that are explicitly Phase 1 planning artifacts;
  the surrounding text makes the historical scope clear.

#### Exit criteria

- [x] `docs/m8-adoption-workflow.md` carries the
      Milestone-completion summary (mirrors M7's structure).
- [x] `docs/m8-adoption-workflow-log.md` Phase 10 entry
      appended; all 10 phase rows Complete.
- [x] `docs/status.md` M8 row → Complete; Next-action → M9.
- [x] `CHANGELOG.md` `## 1.3.0 — 2026-05-25` dated.
- [x] `dist/docs_cli-1.3.0-py3-none-any.whl` +
      `dist/docs_cli-1.3.0.tar.gz` exist; `twine check`
      PASSED on both.
- [x] pytest 369 GREEN; ruff / ruff-format / mypy / `docs
      check docs/` all exit 0.
- [x] **NO `twine upload`, NO `git tag v1.3.0`, NO GitHub
      release** — per OQ-C.
- [x] **Awaiting operator review → batched publish (M9).**
      Branch `m8/phases-5-10` ready for fresh-eyes review.

### Post-Phase-10 — Step 2 fresh-eyes review fix

**Completed:** 2026-05-25

#### Objective

Address Nit #1 from the Step 2 fresh-eyes review: the
`tests/test_packaging.py` byte-identity / wheel-contents checks
(`test_d3` + `test_b3`) pinned only the 3 pre-M8 bundled skill
files and did NOT include the 3 additions that joined the
`_SKILL_RELATIVE_FILES` allowlist in M8
(`use-cases.md`, `adoption-playbook.md`,
`docs-toml-template.toml`). A typo in that tuple would silently
break `docs install-skill --copy` for those files with no test
catching it.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `tests/test_packaging.py` | Modify | Extended `test_b3` explicit-assertion set and `test_d3` byte-identity for-loop with the 3 new relative paths. Pure additive — no new test files, no new fixtures, no behaviour change. |
| `docs/m8-adoption-workflow-log.md` | Modify | This sub-entry. |
| `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Lockstep after `docs touch` on the impl log. |

#### Actions taken

1. Read `_SKILL_RELATIVE_FILES` at `src/docs_cli/cli.py:3614`
   to confirm the 3 new entries and the exact relative paths
   (`Path("references") / "use-cases.md"` etc.).
2. Extended `test_b3_wheel_contains_cli_and_skill` with 3
   additional `assert "docs_cli/skill/references/<file>" in
   names` lines and a comment explaining why every
   allowlist file must also ship in the wheel.
3. Extended the `for rel in (...)` tuple in
   `test_d3_install_skill_tree_is_byte_identical` with the
   3 new `Path(...)` entries so the byte-identity check
   covers them too. Pinning these here means a typo or stale
   walk in `_SKILL_RELATIVE_FILES` trips a loud
   byte-identity failure.
4. Ran the full quality gate (all exit 0):
   - `pytest tests/test_packaging.py -v` — 25 PASSED.
   - `pytest tests/ -q` — **369 PASSED** (count unchanged;
     extension lived inside an existing for-loop, did not
     add new parametric items).
   - `ruff check .` — clean.
   - `ruff format --check .` — 33 files already formatted.
   - `mypy` — Success: no issues found in 34 source files.
   - `docs check docs/` — no violations found.
5. Committed as `m8 review fix: extend test_packaging to
   cover the 3 new bundled skill files` (sha `992f4a2`).

#### Issues / decisions

- **Nit #2 deferred.** The review surfaced a second nit:
  `_print_migration_plan` always emits per-file lines on
  `--apply`, so the playbook's `--apply --quiet` examples in
  Steps 5/6 are mildly misleading (`--quiet` only suppresses
  the trailing stderr success line). This is pre-existing
  pre-M8 behaviour and the review's own verdict was to
  defer it. Options for Step 3 (simplify) or a follow-on:
  (a) wire `--quiet` to skip `_print_migration_plan` on
  `--apply`, or (b) update the playbook examples to drop
  the misleading `--quiet`. Operator picks at Step 3.
- **No code change.** Pure test-surface widening; the M8
  shipped bits (`cli.py`, skill bundle, docs, CHANGELOG)
  did not move. 1.3.0 wheel artefacts remain the same.

#### Exit criteria

- [x] `test_b3` + `test_d3` cover all 6 entries of
      `_SKILL_RELATIVE_FILES` (no allowlist file can be
      silently skipped by `install-skill --copy`).
- [x] Full quality gate clean (369 GREEN, ruff, ruff-format,
      mypy, `docs check`).
- [x] Review-fix commit `992f4a2` landed on `m8/phases-5-10`.
- [x] Nit #2 documented as a deferred follow-on; no Step 2
      regression.
