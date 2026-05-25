# M8 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-05-24

Related:
- child-of: m8-adoption-workflow.md
- pairs-with: status.md

## Implementation metadata

- Project: docs
- Milestone: M8 — Adoption workflow (agent-driveable)
- Started: 2026-05-24
- Progress: **Milestone-setup phase complete; Phase 1 in
  progress; blocked on M7 ship before Phase 2 can begin.**
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

(Note: doc-lifecycle status is in the front-matter `Status:`
field above — M7 introduces the `Status:` → `Lifecycle:` rename
at its Phase 5; this M8 log uses `Status:` until that sweep
lands, then will be re-keyed automatically by the same M7
helper.)

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
| 1. Define Contract | In progress | 2026-05-24 | Promote M8 from `draft` to `active` (done); create this log (done); record OQ A–G resolutions as Decisions in the task plan (done); update status.md "Current milestone" + milestone-table row + Next action. No code change; no convention change. Regenerate INDEX + snapshot. Phase 2 blocked on M7 ship. |
| 2. Write Tests (RED) | Pending (waits on M7 ship) | — | New test files: `test_exclude.py` (9 tests, F3), `test_triage_flags.py` (6 tests, F6), `test_non_md_surfacing.py` (3 tests, F7), `test_body_from.py` (7 tests, F9), `test_skill_adoption.py` (6 tests, F8). Extension to `test_migrate.py`: `--summary --json` mutual exclusion. All RED for intended unimplemented surface; M7's full suite stays GREEN. |
| 3. Create Data/Fixtures | Pending | — | Reuse M7's 5 sanitised real-trees fixtures heavily. New small fixtures: `body-from/{with-frontmatter,clean-body,edge-case-keyword}`, `docsignore/sample/` (gitignore syntax exercises), `trees/exclude-test/` (small synthetic tree with `[exclude]` in `.docs.toml`). |
| 4. Run Tests (RED Baseline) | Pending | — | Capture verbatim pytest output. Expected: M7's full suite GREEN + ~31 M8 RED for intended reasons (argparse errors on new flags; config KeyErrors on `[exclude]`; skill-reference FileNotFoundErrors). Quality gate clean tree-wide. |
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
