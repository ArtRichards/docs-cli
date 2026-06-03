# M15 — Implementation Log

Lifecycle: draft
Role: log
Project: docs
Updated: 2026-06-03

Related:
- child-of: m15-agent-native-authoring.md
- pairs-with: m15-agent-native-authoring.md
- pairs-with: status.md

## Overview

Chronological log of work on M15 — Agent-native doc authoring. Append a
section per TDD phase with objective, files changed, actions, test
results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M15 — Agent-native doc authoring (v1.6.0)
- Started: 2026-06-02 (scaffolded; carved from M14)
- Progress: **Milestone pair scaffolded 2026-06-02.** Carved out of M14
  (operator-confirmed) when the post-1.5.0 contract outgrew M12 scale.
  Scope is the agent-native authoring set: B2 `docs project set`, B3
  `docs stamp`, C4 the `--body-from` real-frontmatter detector, C2 the
  skill/cli docs. **Depends on M14** — implement after it; M17 publishes
  both as 1.6.0. Phase 1 (Define Contract) opens via `/ship-milestone M15`.

(Note: doc-lifecycle status is the front-matter `Lifecycle:` field. This
section tracks implementation progress, which is distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Done | 2026-06-03 | cli.md: `project set` + `stamp` sections; `--body-from` cluster/fence detector rewrite; per-verb exit-code rows; bundled ref resynced byte-identical. |
| 2. Write Tests (RED) | Done | 2026-06-03 | `test_cli_project_set.py` (20) + `test_cli_stamp.py` (15) new; `test_body_from.py` extended (C4 flip + prose-pass + true-positive refusals + cluster boundary). 47 collect across the three files; intended RED. |
| 3. Create Data/Fixtures | Done | 2026-06-03 | `tests/fixtures/stamp/` (5 files) + 3 new `body-from/` fixtures; `with-frontmatter.txt` deleted (demoted). B2 reuses existing trees inline. Every Phase-2 fixture reference resolves. |
| 4. Run Tests (RED Baseline) | Done | 2026-06-03 | 39 → **41** intended RED (20 project_set + **16** stamp + **5** body_from after the review-fix pass), classified below; 459 GREEN incl. test_skill_refs + the lockstep-regenerated frozen snapshot. ruff / format / mypy clean. (Review-fix pass added the `--title` stamp test + the C4 non-adjacent body-from PASS test, +2 reds — see the Review-fix pass section.) |
| 5. Update Base Interfaces | Pending | — | |
| 6. Implement Offline/Core Path | Pending | — | |
| 7. Update Tool/Wrapper Layer | Pending | — | |
| 8. Run Tests (GREEN) | Pending | — | |
| 9. Implement Online/Integration | Pending | — | |
| 10. Quality, Docs, Refactor | Pending | — | |

## Provenance — where the scope came from

The four items were carved out of M14 on 2026-06-02 (operator-confirmed)
when the A6/B3/C4 widening pushed M14 past M12 scale:

- **B2 `docs project set`** — [agent-native-invocation.md](agent-native-invocation.md)
  §5E (the single-doc counterpart to `docs project rename`).
- **B3 `docs stamp` + C4 `--body-from` detector** — surfaced by the M16
  bundled-docs-skill dogfood: an agent wrote a full test-matrix body and
  `docs new --body-from` refused it on a `Reason:` line. Write-then-stamp
  (B3) is the structural fix; the detector (C4) hardens the legacy path.
- **C2 skill/cli docs** — the bundled-skill + `cli.md` documentation for
  the above, kept with the surface it describes.

See [m14-robustness-agent-native.md](m14-robustness-agent-native.md)
Decisions for the split rationale and monotonic numbering.

## Phase 1 — Define Contract

**Objective.** Pin the `cli.md` contract for the four M15 items (B2
`project set`, B3 `stamp`, C4 `--body-from` detector, C2 docs) so the
RED tests (Phase 2) and the implementation (Phases 5–6) have a single
source of truth. CONTRACT ONLY — no `_cmd_*`, no argparse wiring, no
detector rewrite this phase.

**Files changed.**

- `docs/cli.md` — (1) added a `### docs project set <doc>... <new-project>`
  section modeled on `project rename` (grammar split + ≥2-token guard;
  strict-root resolution; `normalise_project_name()` + empty-string
  rejection; the `--new-project` typo guard with the §5E did-you-mean
  shape via `difflib.get_close_matches`; per-doc `Project:` rewrite with
  insertion-when-absent and ONE end-of-batch INDEX refresh; NO
  `.docs.toml` / `Related:`-edge rewrite; archived-target → whole-batch
  exit 2; validate-all-first atomic semantics; `--dry-run` / no-op /
  success footer gated on `not --quiet`). (2) Added a
  `### docs stamp <file>...` section (write-then-stamp: Lifecycle:draft,
  role `--role` else `notes` with NO H1-role inference, project `--project`
  else config, title from H1 / synthesised, `insert_metadata_block`
  insertion preserving body + `## Migrated metadata`; idempotent re-stamp
  = Updated-only refresh; strict-root; atomic multi-file batch;
  `--dry-run`; one end-of-batch INDEX; invalid `--role` exit 2). (3)
  Rewrote the `--body-from` refusal heuristic paragraph + the `new` exit
  clause: refuse only on a leading `---` fence OR a ≥2 `{Lifecycle, Role,
  Updated}` adjacent cluster; lone prose `Reason:`/`Plan:`/`Updated:` now
  passes; error tokens unchanged; noted `edge-case-keyword.md` now passes.
  (4) Added `project set` + `stamp` rows to the per-verb exit-code table.
- `src/docs_cli/skill/references/cli.md` — resynced byte-identical to
  `docs/cli.md` (M14 C1: `docs/` canonical), keeping
  `tests/test_skill_refs.py` GREEN. SKILL.md verb table + frontmatter
  description deferred to Phase 7 (C2) per the plan.

**Actions.** Edited `docs/cli.md`; `docs touch docs/cli.md` (Updated →
2026-06-03); `cp docs/cli.md src/docs_cli/skill/references/cli.md`;
`docs index docs/` (INDEX regenerated in lockstep); `docs check docs/`
clean.

**Test results.** `tests/test_skill_refs.py` GREEN (3 passed) — bundled
ref byte-identical. No code touched, so the rest of the suite is
unchanged from the 459-passing pre-phase baseline.

**Decisions applied (conductor-resolved, binding).**

1. `stamp` is a STANDALONE top-level verb, mutating-verb polarity (writes
   by default; `--dry-run` to opt out), `parents=[common]`; reuses
   `insert_metadata_block` internally but is NOT routed through / aliased
   to `migrate`. (Wiring is Phase 5.)
2. `stamp` default `Lifecycle: draft`.
3. `stamp` role = `--role` else `notes` (NO H1-role inference);
   project = `--project` else `config.project`; title from H1 (synthesise
   from filename when absent).
4. `--body-from` detector: refuse on a leading `---` fence OR ≥2 adjacent
   `{Lifecycle, Role, Updated}` lines in the first ~20 lines (after an
   optional `# H1`); a lone prose required-field line passes.
5. C4 fixtures: add `real-frontmatter-body.md` + `yaml-fence-body.md`
   (refusal), `reason-in-body.md` (pass), flip `edge-case-keyword.md` to
   pass, demote `with-frontmatter.txt` from a refusal case. Refusal
   coverage is carried by the cluster/fence fixtures (load-bearing).
6. `docs/` canonical; Phase 1 edits `docs/cli.md` AND resyncs the bundled
   ref in the same commit; SKILL.md verb-table/description → Phase 7.
7. `project set` grammar: one `nargs="+"` positional split into
   `*docs, new_project`; ≥2 tokens required (exit 2 otherwise).
8. `project set` archived target: refuse the WHOLE batch (exit 2) naming
   the path — not an incidental skip (unlike `project rename`).

## Phase 2 — Write Tests (RED)

**Objective.** Write subprocess CLI tests that pin the Phase 1 contract so
the Phase 5–6 implementation has executable acceptance criteria. RED by
construction (verbs unregistered; old `--body-from` heuristic still in
place).

**Files changed.**

- `tests/test_cli_project_set.py` (new, 20 tests) — modeled on
  `test_cli_project_rename.py` (subprocess + `docs_script` + `tmp_path`).
  Covers: help/registration; single-doc set; multi-doc atomic batch +
  one-INDEX-refresh (follow-up `docs index` byte-identical no-op); inserts
  `Project:` when absent (`topics/orphan.md`); normalises input; empty /
  whitespace name → exit 2; unknown-without-`--new-project` refuses (exit 2
  + did-you-mean + `--new-project` hint); unknown-with-flag succeeds;
  did-you-mean candidate (inline `ideas` doc → `idea` → `ideas`);
  archived-target refuses the whole batch (exit 2, byte-identical live doc,
  no INDEX); atomic validate failure — missing doc (exit 1) and malformed
  doc (`rename-with-malformed` tree, exit 1) with the good doc byte-identical
  + no INDEX; no-op already-current (exit 0, no INDEX); `--dry-run`
  no-change; outside-root refusal (exit 2); does-not-rewrite-`Related:`-edges
  (inline referrer byte-identical); single-token grammar error (exit 2).
- `tests/test_cli_stamp.py` (new, 15 tests). Covers: help/registration;
  inserts metadata block (Lifecycle:draft, Role, Project, Updated; body
  verbatim via a `BODYMARKER`; `docs check` clean); title from H1;
  synthesises H1 when absent; role from flag; role default `notes` with NO
  H1-role inference (a fixture whose H1 trailing word is "Plan" still gets
  `notes`); project from flag; project from config; idempotent re-stamp =
  `Updated:`-only refresh (all other lines byte-identical, reports already
  stamped); preserves foreign metadata under `## Migrated metadata`
  (`Migrated-Owner: alice`); `--dry-run` no-write; multi-file atomic (a
  missing file aborts before any write, exit 1, good file byte-identical);
  invalid `--role` exit 2; outside-root exit 2.
- `tests/test_body_from.py` (extended). Flipped the test-4 refusal
  parametrize off `edge-case-keyword.md` / `with-frontmatter.txt` onto the
  true-positive `real-frontmatter-body.md` (cluster) + `yaml-fence-body.md`
  (fence) fixtures (unchanged error tokens). Updated the OQ5 docstring to
  the C4 detector. Added test 8 (prose with `Plan:`/`Reason:` lines —
  `edge-case-keyword.md` + `reason-in-body.md` — ACCEPTED, body byte-equal
  at tail) and test 9 (cluster boundary: a single `Updated:` prose line
  passes; two adjacent `Lifecycle:`/`Role:` lines refuse).

**Actions.** Wrote the two new files + extended `test_body_from.py`;
`ruff format` (2 files reformatted) + `ruff check` clean; `pytest
--collect-only` → 47 tests collect cleanly across the three files (no
collection / import errors).

**Test results.** Intended RED — full classification recorded in Phase 4.
Fixtures land in Phase 3, so a full run of these files comes after Phase 3.

## Phase 3 — Create Fixtures

**Objective.** Put every fixture the Phase-2 tests reference on disk so the
Phase-4 run exercises real files (no path errors), and the intended RED is
"behaviour not yet implemented", not "fixture missing".

**Files changed.**

- `tests/fixtures/stamp/` (new dir, 5 files):
  - `raw-no-frontmatter.md` — `# Raw Title` + body (`BODYMARKER`).
  - `raw-no-h1.md` — body only, no H1 (stamp synthesises `# Raw No H1`).
  - `raw-with-foreign-meta.md` — `# H1` + `Owner: alice` / `Tags: infra`
    foreign lines + body (parked under `## Migrated metadata`).
  - `already-stamped.md` — a complete valid doc with `Updated: 2026-01-01`
    (a past date, so the idempotent re-stamp's `Updated:` refresh is
    observable).
  - `raw-h1-suggests-role.md` — `# Deployment Rollout Plan` (H1 trailing
    word "Plan") to pin "stamp does NO H1-role inference".
- `tests/fixtures/body-from/` (3 new):
  - `reason-in-body.md` — the dogfood shape (`## Risk level` / `Reason: …`
    + `## Plan` / `Plan: …`) — ACCEPTED under C4.
  - `real-frontmatter-body.md` — `# H1` + `Lifecycle`/`Role`/`Updated`
    cluster + body — REFUSED (cluster signal b).
  - `yaml-fence-body.md` — leading `---` YAML fence — REFUSED (fence
    signal a).
- `tests/fixtures/body-from/with-frontmatter.txt` — **deleted** (demoted):
  its `Owner:` / `Tags:` lines are not required-field labels, so under the
  C4 cluster detector they no longer refuse; leaving it as a refusal case
  would be wrong. Refusal coverage now lives in the cluster/fence fixtures.

B2 (`project set`) needs no new tree: the tests reuse the existing
`multi-project-alpha-sidecar` (multi-project + orphan + archive) and
`rename-with-malformed` trees, with extra docs (`ideas-doc.md`,
`referrer.md`, outside-root doc) written inline per
`test_cli_project_rename.py` convention.

**Actions.** Created the fixture files; `git rm with-frontmatter.txt`;
cross-checked every fixture-file reference in the three Phase-2 test files
against disk — all resolve (tmp-path outputs like `my-feature.md`,
`missing.md` are written by the tests, not fixtures).

## Phase 4 — Run Tests (RED Baseline)

**Objective.** Run the new files + full suite and CLASSIFY every failure to
confirm the *intended* RED — every red is "behaviour not yet implemented",
none is a traceback / import / collection error.

**Result.** `pytest tests/ -q` → **39 failed, 459 passed**. Quality gate
clean: `ruff check` (all checks passed), `ruff format --check` (39 files
formatted), `mypy` (no issues, 40 source files), `docs check docs/` exit 0.

**RED classification (all intended).**

- **B2 `project set` — 20 RED.** All fail with a clean argparse
  `SystemExit(2)` "invalid choice: 'set' (choose from 'rename')" — the
  `project set` subcommand is NOT registered (Phase 5). The
  message-asserting tests (typo guard, no-root, single-token, etc.) reach
  exit 2 but the asserted message is absent because the verb never runs.
  No tracebacks, no import errors.
- **B3 `stamp` — 15 RED.** All fail with a clean argparse `SystemExit(2)`
  "invalid choice: 'stamp'" — the top-level `stamp` verb is NOT registered
  (Phase 5). `test_stamp_invalid_role_exit_2` was strengthened to assert
  the error NAMES the bad role (not argparse's "invalid choice"), so it is
  genuinely RED rather than passing on the unregistered-verb exit 2.
- **C4 `--body-from` — 4 RED, 2 green-now (regression guards):**
  - RED (red-now — old any-`Label:` heuristic still refuses, so the change
    is needed): `…accepts_prose_with_label_lines[edge-case-keyword.md]`,
    `…[reason-in-body.md]`, `…single_required_field_passes` — all exit 2
    today; go green when the C4 cluster/fence detector ships (Phase 6).
  - RED (red-now — NEW fence behaviour): `…rejects_real_metadata_block_in_body
    [yaml-fence-body.md]` exits 0 today (the old heuristic matches only
    uppercase `Label:` lines, not a `---` fence or lowercase `title:`), so
    it refuses only after the C4 fence detector ships. NB: this is a
    stronger classification than the plan's note (which expected both
    true-positive refusals to be green-now) — the fence fixture genuinely
    pins the new `(a)` signal and must be RED until C4.
  - GREEN-now (regression guards that stay green across C4):
    `…rejects_real_metadata_block_in_body[real-frontmatter-body.md]` (old
    heuristic already refuses the uppercase `Lifecycle`/`Role`/`Updated`
    cluster; C4 keeps refusing it via signal (b)) and
    `…two_required_fields_refuses` (two adjacent uppercase required-field
    lines refuse under both heuristics).
- **Existing-test churn.** The only change to a pre-existing test is
  `test_body_from.py` test 4 — its refusal parametrize was repointed off
  `edge-case-keyword.md` / `with-frontmatter.txt` onto the true-positive
  `real-frontmatter-body.md` / `yaml-fence-body.md` fixtures. Intentional
  (the C4 flip). All other pre-existing `test_body_from` cases (1,2,3,5,6,7)
  stay GREEN.
- **`tests/test_skill_refs.py` GREEN** (3 passed) — Phase 1 resynced the
  bundled ref byte-identical.

**Lockstep fix (committed this phase).** The Phase-1–3 `docs touch` /
`docs index` edits bumped `cli.md` + the two M15 docs to 2026-06-03 and
re-sorted their INDEX groups, which left the frozen acceptance snapshot
`tests/fixtures/expected/docs-INDEX.md` stale (the dogfood guard
`test_index_output_matches_frozen_snapshot` normalises only the `_Generated_`
line, not per-doc `Updated:` dates). Regenerated the snapshot from the live
`docs/INDEX.md` — back in lockstep, that test GREEN again. This was the
only collateral breakage; no other pre-existing test changed.

### Post-Phase-4 consistency audit (2026-06-03)

Ran the same-instance consistency / completeness / accuracy audit
(`ship-milestone/references/consistency-check.md`, phases-1–4
interpretation — the suite should be in the intended RED baseline and the
highest-leverage check is whether the Phase-2 tests genuinely pin the
contract). Findings + fixes (all committed):

1. **Typo-guard message ambiguity (contract self-inconsistency, FIXED).**
   The Phase-1 `project set` typo-guard contract put the
   `to create a new project group, pass --new-project` recovery hint on the
   same `→` line as the optional `did you mean '<closest>'?` clause, yet
   also said "when nothing is close the `→ did you mean …` clause is
   omitted (the `--new-project` hint still prints)" — contradictory, and
   `test_project_set_unknown_project_without_flag_refuses` (uses `gamma`,
   no close match) asserts the recovery hint prints. Rewrote the cli.md
   wording so the recovery hint **always** prints and only the
   `did you mean '<closest>'?` prefix is conditional (dropped when nothing
   is close). Resynced the bundled ref. Both typo-guard tests are
   consistent with the disambiguated contract.
2. **Under-constrained `test_stamp_invalid_role_exit_2` (FIXED in Phase 4
   commit).** It passed-now purely because the unregistered `stamp` verb's
   argparse error is exit 2 + no write. Strengthened to assert the error
   NAMES the bad role and is NOT argparse's "invalid choice" — now
   genuinely RED, pins the role-vocabulary refusal.
3. **Missing success-output coverage (FIXED).** No test pinned the
   `project set` success footer (`set <new-project> on <N> doc(s)`) or the
   `stamp` fresh-stamp success line (`stamped <path>`). Added a footer
   assertion to the multi-doc `project set` test and a `stamped …`
   assertion to `test_stamp_inserts_metadata_block`.
4. **Stale milestone OPEN QUESTIONS (FIXED).** The three OQs (stamp shape,
   detector boundary, canonical source) were conductor-resolved; converted
   the section to "OPEN QUESTIONS — RESOLVED" summarising the binding
   answers and pointing at the Phase-1 Decisions block.
5. **Stale `cli.py` line reference (FIXED).** The milestone Scope cited the
   `--body-from` heuristic at `cli.py:3336-3347`; the actual location is
   `cli.py:3429-3440` in `_cmd_new`. Corrected.
6. **status.md / plan.md M15 row stale (FIXED).** Both listed M15 as
   "Draft"; updated to "In progress — Phases 1–4 (contract + RED) done on
   branch `m15/phases-1-4`, Phases 5–10 pending"; aligned the status.md
   narrative.

Re-verified after fixes: full suite 39 intended RED / 459 GREEN;
`test_skill_refs` + frozen snapshot GREEN; bundled ref byte-identical;
`ruff check` / `ruff format --check` / `mypy` clean; `docs check docs/`
exit 0. The diff is contract + tests + fixtures + docs only — no `cli.py`
change (correct for phases 1–4).

**Surfaced for operator (no scope/intent change made):** none — every
audit fix is an internal-consistency or test-quality correction within the
already-resolved contract; no decision changes milestone scope or behavior
intent.

### Review-fix pass (fresh-eyes findings, 2026-06-03)

A fresh-eyes review of this step (still phases 1–4 only: contract + RED
tests + fixtures + one cross-spec doc fix; NO `cli.py`) returned seven
conductor-resolved findings, all applied:

1. **§5E cross-spec contradiction (should-fix, FIXED).**
   `agent-native-invocation.md` §5E still said `project set` archived docs
   are "skip + report" (matching `rename`). Rewrote the §5E archived bullet
   and the TDD-sketch `archived-skip` item to record the resolved
   divergence: `set` takes **explicit** paths, so a named archived doc
   **refuses the whole batch (exit 2)** — UNLIKE `rename`'s incidental
   tree-walk skip. `docs touch` bumped its Updated → 2026-06-03; INDEX +
   frozen snapshot regenerated in lockstep; `docs check` clean.
2. **Outside-root exit-code polarity (should-fix, binding, FIXED).** Verified
   the cli.py convention: no-docs-root / no-`.docs.toml`-ancestor → exit 2
   for all verbs (the `_resolve_*_root` refusals: touch 3228 / rename 3254 /
   new 3284); a **named target resolving outside an already-resolved root** →
   exit 1 (the `_cmd_touch` precedent, cli.py:3850-3853). `project set` and
   `stamp` both take explicit paths, so the closest precedent is `touch`:
   named-doc-outside-root = exit 1. `stamp`'s contract already said exit 1
   (kept). Moved `project set`'s "named doc outside the docs root" from the
   exit-2 column to exit-1 in the per-verb table + both prose paragraphs
   (Atomic semantics + Exit codes); added an explicit **"Cross-verb
   exit-code convention (no-root vs outside-root)"** note to the Exit codes
   summary. Resynced the bundled ref (byte-identical). Updated
   `test_project_set_refuses_doc_outside_root` to expect exit 1 (still
   red-now on the unregistered-verb SystemExit(2), so its red status is
   unchanged — but it now asserts the correct code so Phase 8 turns it green
   right). The no-docs-root test stays exit 2. Decision recorded in the
   milestone doc.
3. **`stamp --title` unpinned (should-fix, FIXED).** Added
   `test_stamp_title_flag_overrides_existing_h1` (`--title "Custom Title"` on
   `raw-no-frontmatter.md`, whose H1 is `# Raw Title`, must yield
   `# Custom Title`; the doc parses + `docs check` clean) and added `--title`
   to `test_stamp_help`. RED-now on the unregistered `stamp` verb (+1 red).
4. **Under-constrained synthesised-H1 assertion (should-fix, FIXED).**
   `test_stamp_synthesises_h1_when_absent` used `startswith("# Raw No H1")`,
   which would accept a leaked `.md`/`.Md` extension. Strengthened to assert
   the H1 LINE equals exactly `# Raw No H1` and that no `.md` leaks into it.
5. **Did-you-mean recovery-hint pinning (nit, FIXED).** Extended
   `test_project_set_did_you_mean_candidate` to find the single `→` line and
   assert BOTH the `did you mean 'ideas'?` prefix AND the always-printed
   `to create a new project group, pass --new-project` recovery hint appear
   together on it — guarding against regression to the original ambiguous
   wording the post-Phase-4 audit fixed.
6. **Per-verb message-prefix pinning (nit, FIXED) + IMPLEMENTATION TRAP.**
   Added `assert "docs: project set:" in stderr` to the project-set
   no-docs-root test and `assert "docs: stamp:" in stderr` to the stamp
   strict-root test. **TRAP for Phase 5/6:** `_resolve_project_root`
   (cli.py:3235) **hardcodes the `docs: project rename:` prefix**;
   `project set` must NOT emit `project rename:` — the helper must be
   generalized (verb-label param) or a set-specific resolver used. Pinning
   the prefix now forces that.
7. **C4 adjacency PASS test (nit, FIXED).** Added
   `test_body_from_two_required_fields_non_adjacent_passes`: a body with two
   required-field prose lines (`Lifecycle:` … prose … `Role:`) that are
   NON-adjacent within the first ~20 lines must PASS — the C4 refusal needs a
   CONTIGUOUS run of ≥ 2 adjacent required fields. Catches an implementation
   that refuses on "≥ 2 required fields *anywhere* in 20 lines". RED-now (the
   old any-`Label:` heuristic refuses any `Lifecycle:`-shaped line), goes
   green only after the C4 detector ships (+1 red).

**New RED/GREEN baseline after the review-fix pass:** **41 intended RED**
(20 project_set + 16 stamp + 5 body_from), **459 GREEN**. The +2 over the
prior 39 are findings 3 (`--title` stamp test) and 7 (C4 non-adjacent
body-from PASS). Re-classification: every red is either a clean argparse
`SystemExit(2)` on the still-unregistered `set`/`stamp` verb, or the old
`--body-from` any-`Label:` heuristic refusing a body the C4 detector will
accept — no tracebacks, imports, or collection errors. The exit-code change
(finding 2) and the strengthened assertions (findings 4/5/6) stay in their
correct red-now state.

**Gate after the pass:** `ruff check` (all passed) / `ruff format --check`
(39 files) / `mypy` (40 source files, no issues) clean; `docs check docs/`
exit 0; `tests/test_skill_refs.py` GREEN (3) + `docs/cli.md` ≡
`src/docs_cli/skill/references/cli.md` byte-identical (`cmp`); the frozen
INDEX snapshot regenerated in lockstep with `docs/INDEX.md` (the
`agent-native-invocation.md` Updated-date bump from finding 1). Decisions
recorded; diff is docs + tests only — no `cli.py` change (correct for
phases 1–4).
