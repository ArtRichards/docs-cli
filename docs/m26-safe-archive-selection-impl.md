# M26 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-08-13

Related:
- child-of: m26-safe-archive-selection.md
- pairs-with: m26-safe-archive-selection.md
- pairs-with: status.md
- references: feedback-log.md

## Overview

Chronological implementation log for M26 — Safe explicit archive selection.
Append one evidence-backed section per TDD phase; keep the progress table and
the milestone checklist synchronized.

## Implementation metadata

- Project: docs
- Milestone: M26 — Safe explicit archive selection
- Started: 2026-08-12 (milestone setup; no TDD phase started)
- Progress: **Implementation-complete — all ten TDD phases done
  2026-08-13, audited and fresh-eyes reviewed. Full suite 895 GREEN.** Step 1 (Phases 1–4) was complete,
  audited, and fresh-eyes reviewed at the classified RED baseline of 884
  collected / 104 failed / 780 passed. All seven setup
  questions were RESOLVED before Phase 1 (Q1/Q5/Q6 by the operator;
  Q2/Q3/Q4/Q7 conductor-resolved) and Phase 1 did not re-open them; it froze
  the exact surface against them, plus the seventeen Step-1 planning
  questions. Phase 2 wrote the RED suite and closed two Phase-1 gaps; Phase 3
  added the four `archive-*` fixture trees; Phase 4 classified every failure
  and proved mechanically that 769 of the 777 pre-existing ids are still
  GREEN, the other 8 deliberately changed. **Phases 1–4 changed no product
  code** — `git diff src/docs_cli/cli.py` was empty at the end of Step 1.
  **Step 2 (Phases 5–10) landed on `m26/phases-5-10`:** the models and
  planner, the whole seam, the CLI and every parallel surface, the GREEN gate
  with 774 of the 777 pre-existing ids mechanically proven present and
  passing (3 deliberately removed, 114 new), the closeout workflow dogfooded
  on a throwaway copy of this tree, and the simplify-and-close pass. The
  same-instance audit added one failure-path lock and the fresh-eyes review
  fold-in six more — including the fix for its one blocker, a primary resolving
  outside the docs root being archived into the tree — so the suite stands at
  **895**. The
  milestone stays `Lifecycle: active` until the M29 publish closeout.
- Source: the operator-confirmed cascade-safety decision in `feedback-log.md`
  (2026-08-09/10) and the M26 registration in `plan.md` (2026-08-10).
- Branch: `m26/milestone-setup` for setup; `m26/phases-1-4` for Step 1
  (Phases 1–4); `m26/phases-5-10` for Step 2 (Phases 5–10).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | **Done** | 2026-08-12 | Froze the compatibility matrix, the message catalog (refusals, preview/apply lines, partial-state admission), the exit-code split, the `--json` schema and field table, and the Phase-5 signatures. Seventeen Step-1 planning questions recorded as BINDING. No `cli.py` edit (logged deviation). |
| 2. Write Tests (RED) | **Done** | 2026-08-13 | New `tests/test_archive_plan.py`, `tests/test_cli_archive.py` (6 pre-existing ids deliberately changed, 3 deleted/replaced), `tests/test_skill.py` (+2), `tests/test_cli_check.py` (+1). Two Phase-1 gaps closed: ineligibility-reason precedence and the nine-step check order. Six more locks from the Step-1 audit and eleven from the fresh-eyes review; final total **884 collected**. |
| 3. Create Data/Fixtures | **Done** | 2026-08-13 | Four committed trees (`archive-neighborhood` E1, `archive-duplicate-edge` E2, `archive-collision` E3, `archive-archived-neighbour` E4), each `docs check`-clean; three existing fixtures' prose corrected off the retired flag; +4 parametrizations of `test_check_tree_legacy_fixtures_gain_no_new_findings`. |
| 4. Run Tests (RED Baseline) | **Done** | 2026-08-13 | **884 collected, 104 failed, 780 passed** (post-review); 0 collection errors, 0 tracebacks, 0 xfail/xpass; 34 `AttributeError` + 70 `AssertionError`. Mechanical proof against `37d7f1a`: 769 of the 777 pre-existing ids still GREEN, the other 8 deliberately changed (3 removed, 5 failing). One falsely-GREEN `--json` refusal test caught and fixed, plus eight audit findings and a fresh-eyes review whose blocker was an unsatisfiable M18 assertion. |
| 5. Update Base Interfaces | **Done** | 2026-08-13 | `CoordinatedWriteError` widened (+ keyword-only `exit_code`, defaulting to today's 2), `ARCHIVE_EXCLUSION_REASONS`, `ArchiveMove` / `ArchivePlan` (+ `moves`), `_is_archived_rel`, `_archive_destination`, `archive_plan_to_json`. No behaviour change; `_cmd_archive` untouched. **781 passed, 103 failed** — exactly the predicted +1. |
| 6. Implement Offline/Core Path | **Done** | 2026-08-13 | `_candidate_exclusion_reason`, `archive_candidates`, `plan_archive`, `preflight_archive_plan`, `apply_archive_plan`, `_archive_partial_state`. `_archive_one` verbatim; `_cmd_archive` still untouched. **814 passed, 70 failed** — exactly the predicted +33, the whole of `tests/test_archive_plan.py`. |
| 7. Update Tool/Wrapper Layer | **Done** | 2026-08-13 | argparse (mutex group deleted, both retired flags marked, local `--json`), `_cmd_archive` rewritten in the nine-step check order, `_print_archive_lines`; `_cascade_set` / `_print_cascade_footer` / `_cascade_archive` deleted — the verb's last stdin read goes with them. Surface parity: SKILL.md, `references/use-cases.md`, byte-identical mirrors, `UNRELEASED` CHANGELOG, `cli.md`, `plan.md`. **887 passed, 1 failed of 888** — the one RED is a defective Step-1 test helper, fixed in its own commit. |
| 8. Run Tests (GREEN) | **Done** | 2026-08-13 | **888 collected, 888 passed**, 0 collection errors, 0 tracebacks, 0 xfail/xpass. ruff / format / mypy / `docs check --root docs` clean; mirrors byte-identical; INDEX snapshot in sync. Mechanical proof against `37d7f1a`: 774 of the 777 pre-existing ids present and **all GREEN** (re-run as an explicit id list), 3 deliberately removed, 114 new — 774 + 114 = 888. Ran as uid 1000, so the five root-skipped locks really executed. |
| 9. Integrate / Accept / Dogfood | **Done** | 2026-08-13 | On a throwaway copy of this docs tree: E1 reproduced and defused (all six candidates named, none authorized), filtered preview, real scoped write of the M25 pair with `docs check` clean and `docs index` a byte no-op, preview/apply records identical, and four refusals each on a fresh copy with zero bytes and no new directory. `--interactive` with no stdin refused in 0s. `git status --porcelain docs/` empty — the live tree was never touched. |
| 10. Quality, Docs, Refactor | **Done** | 2026-08-13 | `/simplify` pass (the `_is_archived_rel` dedup at the two M25 sites; the pre-flight's per-check loops deliberately kept separate); `architecture.md` gains an `archive (M26)` block, `test-strategy.md` the `archive-*` fixture family and two critical paths, the `cli.py` module docstring one M26 sentence; milestone, log, `status.md`, and `plan.md` closed out. `pyproject.toml` untouched — still 1.8.0. Final gate all GREEN. |
| Step-2 consistency audit | **Done** | 2026-08-13 | Found and fixed a real defect (an unreadable plan member produced a traceback) plus four doc inaccuracies; +1 failure-path lock → **889 passed**. Four items surfaced, not auto-decided. |
| Step-2 fresh-eyes review fold-in | **Done** | 2026-08-13 | One **blocker** fixed — a primary resolving outside the root (symlink, or a mismatched `--root`) was archived INTO the tree, at exit 0 in one shape, with `docs check` clean afterwards. Plus three should-fixes (the two remaining traceback paths, a `--json` key documented but never emitted, a drifted second exit-code table), four nits, and the `--reason ""` one-liner. +6 locks → **895 passed**. |

## Setup record — 2026-08-12

### Objective

Bring the registered M26 draft stub up to full milestone-task-plan depth and
create this log, without starting Phase 1. M25 is implementation-complete and
merged to `main`, so M26 is the next implementation milestone in the v2.0
train.

### Actions taken

- Re-derived the stub's four Phase-1 open questions against the real v1.8.0
  implementation (`_cascade_set`, `_cascade_archive`, `_archive_one`,
  `_cmd_archive`) and against `cli.md`, `convention.md`, and `feedback-log.md`.
- Reproduced the current cascade behaviour on throwaway trees and on a
  read-only preview of this repo's own docs tree; the evidence is tabulated
  below and drives the milestone's *Current state and risks* section.
- Expanded *Binding scope* into seven decisions (D1–D7), added *Out of scope*,
  the ten-phase TDD plan with per-phase objective/files/exit, the phase
  checklist, the testing gate, and evidence-anchored success criteria.
- Kept the reciprocal `follows`/`precedes` and `required-by` edges intact and
  added the milestone↔log pair edges.
- Raised seven setup questions with recommendations rather than deciding any
  of them silently, and then **resolved all seven before Phase 1** — Q1
  (`--interactive` retirement), Q5 (atomicity boundary), and Q6
  (`docs archive --json`) by operator decision; Q2 (refusing-flag retention),
  Q3 (candidate verb set), Q4 (already-archived documents), and Q7
  (primary-only notice) conductor-resolved from the specs, `plan.md`,
  `CLAUDE.md`, and the M14/M18/M25 precedent. Every resolution is recorded in
  the milestone doc's *Resolved setup questions (Q1–Q7, BINDING)* and folded
  into the binding scope D1–D8.
- Scaffolded this log with `docs new log m26-safe-archive-selection-impl`,
  bumped dates and validated with
  `docs touch … --check` (exit 0), and refreshed the frozen dogfood INDEX
  snapshot `tests/fixtures/expected/docs-INDEX.md` for the new log entry
  (22 → 23 active docs) — the same snapshot refresh the M25 setup performed.
- Updated the trackers: `status.md` (current milestone, train listing, next
  action, milestone-progress row) and `plan.md` (v2.0 narrative and the M26
  row) now describe M26 as in flight with its plan and log linked.

### Current-behaviour evidence (docs-cli 1.8.0, reproduced during setup)

| Evidence | Invocation | Observed today | Why it matters | Fixed by |
|---|---|---|---|---|
| **E1** | `docs archive m25-reciprocal-relationship-integrity.md --cascade-dry-run` on this repo | Would archive **6** related docs: `plan.md`, the impl log, `cli.md`, `convention.md`, `test-strategy.md`, `status.md` | Bare `--cascade` on a completed milestone would move this project's entire spec spine into the archive | D2 refusal |
| **E2** | `--cascade` where one doc is reachable by two edges (`pairs-with` + `child-of`) | `docs: could not archive b.md: [Errno 2] No such file or directory`, then `cascade archived 1 related doc(s)`, **exit 0** | A successful operation prints a false failure; no deduplication exists | D3 dedup |
| **E3** | `--cascade` where two candidates share a basename (`x/dup.md`, `y/dup.md`) | `x/dup.md` archived, `y/dup.md` left behind, bare-path error message, **exit 0**, and `docs check` afterwards reports **no violations** | A partial multi-document write reports success and leaves no detectable drift | D4 pre-flight |
| **E4** | `--cascade` where a candidate is already archived (`archive/2026-01-01/old.md`) | Silently relocated to `archive/2026-08-12/old.md` with `Updated:` rewritten from `2026-01-01` to `2026-08-12` | History is rewritten; on this tree `status.md` carries 20+ archive-subtree `pairs-with` edges | D3 exclusion + D4 primary refusal |
| **E5** | `--cascade-only 'typo-*'` where candidates exist but none match | `docs: cascade: no one-hop relations to archive`, primary archived, **exit 0** | A typo'd scope is indistinguishable from a deliberate primary-only archive | D5 empty-selection refusal |

E1 was produced with `--cascade-dry-run` against the live tree (writes
nothing); E2–E5 were produced on disposable trees outside the repository. No
repository file was mutated during setup.

### Verification

- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 45 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 46 source files.
- `.venv/bin/python -m pytest -q` — 777 passed.
- `.venv/bin/docs check --root docs` — no violations found.

### Decisions / issues

- The v1.8.0 defects in the evidence table are **not** separate bug fixes; they
  are exactly the behaviour M26's planning model replaces, so they are fixed as
  a consequence of D2–D5 rather than as standalone patches. They are carried in
  the milestone doc as **E1–E5** and each maps to named regression coverage in
  its *Evidence → regression coverage* table.
- **E4 is data corruption, not just over-reach**, and is squarely in M26's
  remit (Q4): bare `--cascade` relocates and re-dates an already-archived
  document. It is load-bearing on the live tree, where `status.md` carries 20+
  archive-subtree edges. Archived documents are excluded from the candidate
  set with a named ineligibility reason, and an already-archived **primary**
  is refused.
- **`docs archive --json` is in scope** (Q6): one operation-plan record, the
  same shape for preview and apply, reusing M25's `relate --json` pattern —
  primary, candidates, selected, excluded-with-reason, destinations, and
  whether anything was written. It gets its own tests and its own `cli.md` /
  bundled-skill surface-parity rows.
- **Atomicity boundary settled at pre-flight** (Q5): every handled error
  refuses with zero mutation; a residual mid-execution `OSError` is reported
  as an exact partial-state admission and is **not** rolled back. Extending
  M25 — D5's staged-publish-plus-rollback to N documents was considered and
  **explicitly declined** for M26; it is recorded in the milestone doc so a
  later milestone can pick it up.
- Version staging is already settled by M25 — D6: the package stays `1.8.0`
  through M25–M28 and M29 performs the single bump to `2.0.0`. M26 touches
  neither `pyproject.toml` nor the packaging version pins; its CHANGELOG
  entries accumulate under the existing `UNRELEASED` heading.
- Host-machine workflow skills (notably `create-milestones`, which prescribes
  `docs archive <slug>.md --cascade` at milestone completion) are **not**
  updated by this milestone. Per `CLAUDE.md`, host skills refresh only at a
  production ship, and `plan.md` records the Agent Playbook Suite update as a
  post-M29 cross-repository follow-up. The bundled skill inside
  `src/docs_cli/skill/` **is** updated in lockstep, in Phase 7.
- **No OPEN QUESTIONS remain.** All seven are resolved and recorded as binding
  in the milestone doc; Phase 1 freezes exact messages, exit codes, and the
  `--json` schema against them rather than re-litigating scope.

## Phase 1 — Define Contract — 2026-08-12

### Objective

Freeze every byte of surface Phase 2 will assert against: the compatibility
matrix (no "it depends" cell), the refusal / preview / apply / partial-state
message catalog, the exit-code split, the candidate discovery, dedup,
canonicalization and ineligibility rules, the `--json` operation-plan schema
and its field table, and the Phase-5 signatures. No business logic lands, and
the seven setup questions are not re-opened.

### Actions taken

**`docs/cli.md`** — the whole `docs archive` section rewritten (the heading's
flag list now reads `[--cascade-dry-run] [--cascade-only GLOB] [--json]
[--dry-run] [--quiet]`), with new subsections:

- *Safe explicit archive selection (M26 — D1)* — the three-shape
  authorization table, the quiet-stderr rule with its `--json` exception, and
  the `--cascade-only GLOB --dry-run` ≡ `--cascade-dry-run --cascade-only GLOB`
  equivalence.
- *Retired flags (M26 — D2)* — both verbatim refusal lines, the
  runs-first / independent-of-every-flag / prints-under-`--quiet` /
  no-argparse-mutex statements, the `--cascade`-wins tie-break, and an
  **Upgrading from 1.x** block with the two replacement invocations.
- *Candidate discovery (M26 — D3)* — one hop, the never-candidate reciprocal
  verbs, canonical dedup with first-declaration-wins, canonical scope
  matching, the silent self-edge exclusion, the explicit
  no-`[exclude]`-consultation statement, and the three-row ineligibility table
  (`already-archived`, `unresolved-target`, `outside-root`) plus the
  `not-selected` non-ineligibility.
- *Preview (M26 — D6)* — the ten verbatim stderr lines, the
  cascade-flag-gating of the `candidate` lines, the "a preview is never a
  write, so it never fails" exit-0 rule, and the two differences an apply
  shows.
- *The scoped write and its pre-flight (M26 — D4)* — the five per-member
  proofs (including the explicit writability access test and the
  nearest-existing-ancestor rule), the six verbatim pre-flight refusals, the
  all-three-shapes archived-primary statement, and the residual partial-state
  admission with its `Archived: none` branch.
- *An empty selection is a refusal (M26 — D5)* — the two write-path refusals,
  the definition of "matched" as *selected*, `<N>` counted over the whole
  deduplicated set, and the empty-pattern refusal.
- *`docs archive --json` (M26 — D7)* — the worked record, the seven-row field
  table in the `relate --json` style, the per-candidate key set, the closed
  key set, the always-present candidate list, and the
  no-record-on-refusal / record-on-INDEX-refresh-failure boundary.
- *`docs archive` exit codes* — the Q4 split as its own table.
- The M12 referring-edge and M18 archive-subtree-edge blocks kept, with
  `--cascade` prose updated to `--cascade-only`, the per-candidate-failure
  sentence replaced by the all-or-nothing statement, and a new sentence
  pinning the one-`(alias, new_rel)`-pair-per-declared-spelling rule.
- Deleted as now-false: the four-mutually-exclusive-flags paragraph, the
  `--cascade` / `--interactive` bullets, the "`--cascade-dry-run` alone is
  shorthand for `--cascade --dry-run`" sentence, the two legacy footer
  strings, and the old *Invariant: `docs` never prompts unless
  `--interactive`* paragraph (replaced by the unconditional
  **`docs archive` never prompts on stdin at all**).
- `## Exit codes (summary)`: both archive rows rewritten against the Q4 split.

**`docs/convention.md`** — new *Safe explicit archive selection (M26 — D1)*
paragraph in `## Archive subtree`, beside the M18 and M25 — D4 exceptions:
entry into the archive is authorized explicitly, never by relationship; the
three shapes; and the two author-facing rules (an archived doc is never
re-archived, in either role; `Archived-reason:` is primary-only).

**Milestone doc** — new `## Decisions (Phase 1 — BINDING)` carrying the
compatibility matrix, the Q4 exit split, the frozen message catalog, the
`--json` schema, the frozen Phase-5 signatures with their reuse list, the
seventeen resolved Step-1 planning questions, and the logged Phase-1
deviation. D1, D2, D3, D5, D6, and D7 amended in place so the binding scope
and the frozen contract cannot disagree — in particular **the D5/D6
contradiction is removed, not papered over** (D5 now says "a `--cascade-only`
**write** that selects nothing"; D6 states the exit-0 preview rule and both
cross-reference each other). Phase-1 checklist row and deliverable 1 ticked;
Progress line updated.

**Lockstep chores** — `cp docs/{cli,convention}.md
src/docs_cli/skill/references/`; `docs touch` on the four edited docs
(implicit reindex); `tests/fixtures/expected/docs-INDEX.md` re-synced from the
regenerated `docs/INDEX.md`.

### Decisions / issues

- **Q2 (operator) forced a real amendment, not a footnote.** The setup text
  had D5 ("an empty selection refuses, exit 2") and D6 ("a preview writes
  nothing and exits 0") both claiming
  `archive F --cascade-dry-run --cascade-only <no-match>`. D5 is now scoped to
  the **write** path in its own heading sentence, and D6 carries the exit-0
  rule explicitly with the `matched none` line and the record's every-candidate
  `"selected": false` named. The compatibility matrix has a dedicated row for
  the case. (Phase 1 wrote `"selected": []` here and in three other places; the
  top-level key set is closed and has no `selected` key, so the Step-2 review
  had all four corrected — see the post-review record below.)
- **Q4 (operator) — the exit-code split is a table, not prose.** Exit 1 stays
  for a plan member with no editable metadata block, an occupied destination
  slot, and the whole-tree pre-flight walk; the five new M26 refusals exit 2.
  The pre-existing pins (`cli.md`'s matrix row and
  `test_archive_referring_edge_rewrite_is_atomic`) therefore keep their exact
  meaning.
- **The `matched none` preview line is gated on `not --quiet`.** The operator's
  answer calls it "loud", which it is — it is on stderr and explicit — but
  making it the one preview line that ignores `--quiet` would add an
  it-depends rule to the very matrix D2 exists to flatten. `--quiet` plus a
  preview is already a contradiction in intent, and the `--json` record
  carries every candidate's `"selected": false` for the machine consumer. Refusals, by contrast,
  **do** print under `--quiet` — they are failures, not output.
- **The `candidate` lines are identical in preview and apply.** Only the
  primary's verb (`would archive` / `archived`) and the presence of the
  `preview only — nothing was written` line distinguish the modes. A scoped
  write is all-or-nothing, so the plan is literally what happened; one form
  means one string to keep in parity, and it makes a preview/apply stderr diff
  as small and readable as the `--json` diff.
- **`docs: archive: <rel> has no editable metadata block; refusing before any
  write` was added to the catalog.** The Step-1 plan's catalog listed no
  message for the exit-1 metadata-block pre-flight refusal that its own test
  #17 (`test_preflight_refuses_a_candidate_without_a_metadata_block`)
  requires. Added in the same family and the same shape as its neighbours. The
  **primary**'s malformed case is unchanged — it is still caught by the
  existing `parse()` call before the plan exists, and still prints
  `docs: <exc>` at exit 1.
- **The frozen `--json` key set carries no `reason` field**, so `--reason` is
  observable only in the archived primary's `Archived-reason:` line, not in
  the operation-plan record — unlike `relate --json`, which does carry
  `reason`. The Step-1 plan froze the top-level key set as closed and ordered,
  so Phase 1 implemented it verbatim rather than widening the contract
  unilaterally. **Surfaced for the fresh-eyes review**; a Phase-7 addition
  would be a one-line schema change if the reviewer wants the symmetry.
- **Deviation (approved, same as M25).** Phase 1 made **zero** `cli.py` edits.
  Stubs would change the Phase-4 subprocess RED reasons and risk baseline
  behaviour, and the phase's own exit criterion is "no behavior changes". The
  signatures are frozen in the milestone doc's Decisions and land in Phase 5.
- **Phase-7 follow-through recorded by exact name:** `plan.md:454`'s stale
  resolved-question bullet (still claims `--cascade` prompts `y/N`);
  `src/docs_cli/skill/SKILL.md:62`'s archive row (lists `--cascade`);
  `src/docs_cli/skill/references/use-cases.md:25` ("`--cascade` opt-in for
  one-hop dependents"); `CHANGELOG.md` under `UNRELEASED`. Also noted, and
  **not** in the Phase-7 list: `docs/agent-native-invocation.md:250`, a
  `Lifecycle: draft`, `Project: ideas` proposal doc from 2026-06-03 whose
  Layer-5 bullet still names `--cascade` as a pre-answerable replacement for
  the prompt. It is a historical proposal record, not a spec on the
  surface-parity gate; left for the operator to decide.

### Verification

- `grep` for every verbatim string Phase 2 will assert, in `docs/cli.md` — all
  present (`is retired in docs 2.0 and writes nothing`,
  `is already under the archive subtree`, `--cascade-only must not be empty`,
  `matched none of the`, `has no one-hop pairs-with / child-of candidates`,
  `would both archive to`, `has no editable metadata block`,
  `archive destination already exists`, `is not writable; refusing before any
  write`, `candidate `, `— selected -> `, `not selected (outside
  --cascade-only`, `not selected (no --cascade-only scope)`,
  `ineligible (already archived)`, `ineligible (target does not resolve to a
  file)`, `ineligible (target resolves outside the docs root)`,
  `candidate(s): `, `preview only — nothing was written`,
  `PARTIAL ARCHIVE — not rolled back`, `Archived: none`, `not-selected`,
  `already-archived`, `unresolved-target`, `outside-root`).
- `.venv/bin/python -m pytest tests/test_skill_refs.py tests/test_cli_index.py
  tests/test_cli_check.py -q` — passed (bundled refs byte-identical; INDEX
  snapshot re-synced).
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 45 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 46 source files.
- `.venv/bin/python -m pytest -q` — **777 passed** (unchanged from the Phase-0
  baseline; no test file and no source file was touched in Phase 1).
- `.venv/bin/docs check --root docs` — no violations (exit 0).
- `git diff --stat src/docs_cli/cli.py` — **empty**, per the logged deviation.
- `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.


## Phase 2 — Write Tests (RED) — 2026-08-13

### Objective

Express the retirement, preview, scoped-write, pre-flight, and `--json`
behaviour before any implementation exists, including every failure path the
1.8.0 code silently swallows, so each Phase-5/6/7 change answers a written
test rather than the reverse.

### Authoring rules applied (carried from M25)

- **No module-level import of a Phase-5 symbol.** Each is reached through a
  one-line `_m26(name)` wrapper over `getattr(cli, name)` — a clean
  `AttributeError` at run time (never a collection error, which the Phase-4
  exit criterion forbids), `Any` for mypy, and no ruff `B009`.
- **Every intended-exit-2 test also asserts its contract stderr string.**
  Argparse already exits 2 on `unrecognized arguments: --json` and on the
  mutex group, so a returncode-only assertion would be falsely GREEN for the
  entire refusal family.
- **Every refusal test asserts whole-tree byte identity** through a shared
  `_snapshot(root) -> dict[str, bytes]` over `sorted(root.rglob("*"))`,
  `INDEX.md` and `.docs.toml` included. That is what makes "zero bytes
  written" a real assertion instead of a `not (root / "archive").exists()`
  proxy.
- Each docstring names its intended RED reason; every GREEN-at-baseline lock
  says so and says whether it is **degenerate** or **genuine**.

### Pre-existing tests M26 deliberately changes

The complete list — nothing else in the 777 moves. All in
`tests/test_cli_archive.py`.

| Test | Action | Baseline after edit |
|---|---|---|
| `test_archive_interactive_yes_also_archives_related` | **deleted** — the prompt path it pins no longer exists | — |
| `test_archive_interactive_no_leaves_related_in_place` | **deleted** — same | — |
| `test_archive_cascade_no_prompt_archives_all_relations` | **replaced** by `test_archive_bare_cascade_refuses_and_writes_nothing`; its take-all/exit-0 contract is exactly what D2 reverses | RED |
| `test_archive_cascade_dry_run_composes_with_cascade_only` | `assert "beta.md" not in stderr` **inverted** — D6 requires the unselected candidate to be named | RED |
| `test_archive_cascade_dry_run_rejects_interactive` | retirement-message assertion added; the bespoke "incoherent pair" message is retired | RED |
| `test_archive_mutually_exclusive_cascade_flags_rejected` (×3) | retirement-message assertion added per case, plus `not allowed with` asserted **absent**; docstring corrected (the mutex group is no longer what produces exit 2 — Phase-1 Q12) | RED |
| `test_archive_cascade_rewrites_edges_for_both_moves_atomically` | `--cascade` → `--cascade-only "sidekick.md"`, `stdin_text` dropped | GREEN |
| `test_archive_cascade_rewrites_moved_docs_own_edges` | same | GREEN |
| `test_archive_cascade_trio_lands_edge_clean` | `--cascade` → `--cascade-only "feature-*.md"`, `stdin_text` dropped | GREEN |
| `test_archive_cascade_preserves_reciprocal_pair` | `--cascade` → `--cascade-only "b.md"` | GREEN |

`test_archive_cascade_dry_run_previews_and_writes_nothing`,
`test_archive_cascade_only_filters_by_glob`, and
`test_archive_pair_leaves_check_clean` need **no** edit and stay GREEN — the
last one only gained a docstring note that M18 — Q3's "never bare `--cascade`
on the plan" advice has since become a hard refusal.

The bare `sidekick.md` / `b.md` / `feature-*.md` scopes work because
`_compile_docsignore_pattern` gives a no-slash pattern gitignore semantics:
match any path segment at any depth.

### New tests

**`tests/test_archive_plan.py`** (new, 32 items) — the core seam, modelled on
`tests/test_relate_plan.py`, every tree an inline `tmp_path` builder because
every test writes and byte-compares:

- **D3 candidate discovery (13):** the two-verb candidate set against all six
  M25 reciprocal verbs plus `references`/`implements`/`parent-of`;
  declaration order; dedup across two verbs (E2) and across two spellings,
  with `aliases` preserved; canonical scope matching (`./b.md` selected by
  `'b.md'`); the silent self-edge exclusion; `already-archived` (E4),
  `unresolved-target`, and `outside-root` ineligibility; the reason-precedence
  parametrization; `not-selected`; and the frozen
  `ARCHIVE_EXCLUSION_REASONS` token set.
- **D4 planning purity and pre-flight (13):** `plan_archive` writes nothing;
  the six refusals each asserting their **exact** message — intra-plan
  collision (E3), occupied destination, unwritable source, unwritable
  destination directory, archived primary (E4), member with no metadata
  block — plus a parametrization over all six asserting
  `rolled_back is True`, `published == ()`, and whole-tree byte identity.
- **D4 execution (3):** `apply_archive_plan` returns one `(old_rel, new_rel)`
  pair per declared spelling; the injected-`OSError` partial-state admission
  with its exact string, `rolled_back is False` and `published == (…)`,
  cross-checked against the disk; and the `Archived: none` branch.
- **D7 serializer (3):** the exact preview record, preview/apply shape
  identity, and the no-scope record carrying the whole candidate set.

**`tests/test_cli_archive.py`** (+34 items) — the subprocess surface:

- **Retirement / E1 (7 functions, 25 items):** bare `--cascade` refuses and
  writes nothing; the refusal names both replacement invocations;
  `--interactive` refuses; `--interactive` refuses **without reading stdin**
  (no `stdin_text` supplied — today EOF declines the prompt and the primary
  still archives at exit 0); the 2 × 8 flag matrix that makes "no it-depends
  cell" real and simultaneously pins refusal-under-`--quiet` and
  no-record-on-refusal; `--help` still registering both flags with the word
  `retired` (the **only** lock on the retention shape — without it Phase 7
  could legally delete the flags and every other retirement test would still
  pass on argparse's own exit 2); and the three D1 shapes never prompting.
- **Preview / D6 (6):** the unfiltered preview naming all six candidates; the
  filtered preview still naming the five spine docs (E1, on the committed
  fixture per Q13); an ineligible archived candidate named; the primary-only
  preview naming none (Q7); `--cascade-only … --dry-run` ≡
  `--cascade-dry-run --cascade-only …`; and the Q2 exit-0 non-matching
  preview.
- **Scoped write (8 functions, 12 items):** E2 dedup with no false failure;
  E3 collision refusing before any write; E4 archived neighbour excluded
  byte-for-byte; the archived **primary** refused in all three D1 shapes
  (Q1); E5 none-matched; the distinct no-candidates message; the empty and
  comment-only scope refusals (Q9); the dotted-edge `docs check` guard; and
  `--reason` on the primary only (Q10).
- **The Q4 exit-code split at the CLI (3):** malformed member → 1, occupied
  destination → 1, unwritable member → 2.
- **`--json` / D7 (7 functions, 9 items):** preview shape, preview/apply key
  identity, per-candidate `selected` + `reason`, exactly-one-object stdout,
  no record on three different refusals (Q3), the no-scope candidate list
  (Q14), and `index_refreshed`.

**`tests/test_skill.py`** (+2) — the archive row of `SKILL.md` and of
`references/use-cases.md` must teach `--cascade-dry-run` / `--cascade-only`
and must not prescribe bare `--cascade`. The "not bare" half is a
`--cascade(?![-\w])` regex, so `--cascade-only` cannot satisfy it by
accident. RED until Phase 7.

**`tests/test_cli_check.py`** (+1) — a scoped archive of the neighborhood
fixture's milestone pair leaves `docs check` at exit 0 and the five spine docs
in the active tree: the M12/M18 no-regression proof restated for the
invocation that replaces bare `--cascade`.

### Decisions / issues

- **Two Phase-1 gaps were found by writing the tests, and closed in the specs
  in this phase** (recorded in the milestone's *Decisions (Phase 1 —
  BINDING)*, in `cli.md`, and mirrored into the bundled refs):
  1. **Ineligibility reason precedence.** `../ghost.md` is *both*
     `outside-root` and `unresolved-target`; `archive/…/ghost.md` is both
     `already-archived` and `unresolved-target`. Phase 1 named the four tokens
     but left the overlap undetermined, so
     `test_ineligibility_reason_precedence_is_pinned` had no answer to assert.
     Fixed order: **`outside-root`, then `already-archived`, then
     `unresolved-target`** — the more structural fact wins.
  2. **Check order.** Q11 fixed only the retirement check's position. The
     malformed-candidate case exposed the rest: today's whole-tree validation
     walk raises on the same file the M26 plan pre-flight would name, so
     without an order the exit-1 message is undetermined. Pinned as a
     nine-step list, with the **plan pre-flight before the whole-tree walk** —
     both can fire on one malformed file, and naming the document the operator
     asked for is strictly more actionable than naming an unrelated referring
     doc.
- **`primary.source` wording corrected** from "the `FILE` argument exactly as
  typed" to "as given on the command line": `plan_archive` receives a `Path`,
  so `Path("./a.md")` serialises as `a.md`. The looser wording is the one the
  code can actually honour.
- **`test_archive_never_prompts_on_stdin` is GREEN-degenerate today** — none
  of the three D1 shapes reads stdin at baseline either. It is kept because it
  becomes the load-bearing lock the moment Phase 7 deletes `_cascade_archive`,
  the verb's last stdin reader.
- **The four migrated cascade tests are the deliberate GREEN half.** They are
  the M12 referring-edge and M18 archive-subtree-edge no-regression proof;
  migrating them to `--cascade-only` (rather than deleting them) is what keeps
  that proof alive across the D2 retirement.
- **`tests/test_check.py` needs no edit**, but Phase 3's four new trees
  automatically add four parametrizations to
  `test_check_tree_legacy_fixtures_gain_no_new_findings`, whose list is
  derived from `_TREES.iterdir()`. Those must pass — which constrains the
  fixtures: no recognized reciprocal verb unless the pair is complete.
- **No `src/docs_cli/cli.py` change.** `git diff --stat` against the Phase-1
  commit is empty.

### Verification

- `.venv/bin/python -m pytest tests/ -q --co` — **863 collected, zero
  collection errors** (777 → 863: −3 deleted/replaced ids, +89 new).
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — all files formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 47 source files.
- `.venv/bin/docs check --root docs` — no violations (exit 0).
- `cmp docs/{cli,convention}.md src/docs_cli/skill/references/` — identical.
- The full RED census is Phase 4's; at the end of Phase 2 the fixture-backed
  tests still fail on a missing `tests/fixtures/trees/archive-*` directory,
  which Phase 3 supplies.

## Phase 3 — Create Data/Fixtures — 2026-08-13

### Objective

Give Phase 2's E1–E5 locks committed trees to run against — one semantic per
tree, structure-only, static dates — per `test-strategy.md`'s fixture policy,
and stop the existing fixtures teaching a flag M26 retires.

### Trees added

| Tree | Contents | Isolates |
|---|---|---|
| `archive-neighborhood/` | `milestone.md` with `child-of: plan.md` and `pairs-with:` {`milestone-impl.md`, `cli.md`, `convention.md`, `test-strategy.md`, `status.md`}, plus those six docs | **E1** — six one-hop candidates; only the impl log belongs in the archive event, and `--cascade-only 'milestone*'` must name the other five as not selected |
| `archive-duplicate-edge/` | `a.md` with `pairs-with: b.md` **and** `child-of: b.md`; `b.md` | **E2** — one candidate, first declaration wins, no false failure line |
| `archive-collision/` | `root.md` with `pairs-with: x/dup.md` and `pairs-with: y/dup.md`; both `dup.md`s | **E3** — two sources, one `archive/<date>/dup.md` destination |
| `archive-archived-neighbour/` | `plan.md` with `pairs-with: log.md` and `pairs-with: archive/2026-01-01/old.md`; `log.md`; the archived doc with `Lifecycle: archived`, `Archived-reason:`, `Updated: 2026-01-01` | **E4** — the ineligible candidate, the byte/date-immutability target, and the archived-primary refusal target |

Each carries its own `.docs.toml` (`[project] name`, `[archive] dir`,
`date_format`). Every `Updated:` is static and no test passes a stale window
to these trees, so no committed date can rot.

**Split decision (the M25 rule, `test-strategy.md`).** Static trees for the
*shape* semantics above — discovery, dedup, collision, ineligibility — and
inline `tmp_path` builders for everything that writes and then
byte-compares: `tests/test_archive_plan.py` in its entirety, the retired-flag
matrix, the empty-scope and unwritable cases, the canonical-spelling case, and
the exit-code-split cases. A `copytree` of a static tree would be pure
overhead there.

**E1 is pinned on the committed fixture, not the live `docs/` tree**
(Phase-1 Q13), so the lock cannot rot as this project's own neighborhood
changes. The live-tree run stays Phase-9 dogfood evidence.

### Fixture prose corrected

Three committed fixtures still taught the retired flag in their bodies, which
would have made them lie the moment Phase 7 lands. No test byte-compares those
bodies against a snapshot, so the edit is safe:

- `archive-trio/feature.md` — `--cascade` → `--cascade-only 'feature-*.md'`,
  plus an explicit "bare `--cascade` is retired (M26 — D2)" note.
- `archive-with-incoming-refs/master.md` — the "invokes `--cascade` and
  answers `y`" sentence replaced by the scoped, promptless invocation the
  migrated test now runs.
- `archive-with-incoming-refs/witness.md` — same substitution.

### Verification

- `.venv/bin/docs check tests/fixtures/trees/<tree>` for all four new trees —
  **no violations found (exit 0)** in every case. Intended finding set is
  therefore empty by construction: the trees exercise archive *selection*, not
  `docs check` rules, so any finding would be an accident. Re-checked
  `archive-trio`, `archive-with-incoming-refs`, and `archive-pair` after the
  prose edits — all still clean.
- **Reciprocal-verb constraint honoured.** None of the four trees uses a
  recognized reciprocal verb (`precedes`/`follows`, `depends-on`/`required-by`,
  `blocks`/`blocked-by`), so the four parametrizations they add to
  `test_check_tree_legacy_fixtures_gain_no_new_findings` (its list is derived
  from `_TREES.iterdir()`) pass: **23 passed** for that test, up from 19.
- Collection: 863 → **867** items, exactly the four new parametrizations.
- Two Phase-2 locks flipped GREEN as intended now that their trees exist:
  `test_preview_of_a_primary_only_archive_names_no_candidates` (degenerate)
  and `test_check_clean_after_a_scoped_archive` (the M12/M18 no-regression
  proof at the check gate).
- `git status` shows exactly the intended new files: 15 files across four new
  directories, plus the three prose corrections.
- No `src/docs_cli/cli.py` change.

## Phase 4 — Run Tests (RED Baseline) — 2026-08-13

### Objective

Prove the new tests fail for the intended missing behaviour and for nothing
else, and prove mechanically — not by assertion — that every pre-existing test
either still passes or was deliberately changed.

### Baseline

```
.venv/bin/python -m pytest tests/ -q --co   →  884 collected, 0 collection errors
.venv/bin/python -m pytest tests/ -q        →  104 failed, 780 passed
```

(Counts restated after the Step-1 audit and the fresh-eyes review fold-in
below, which added six and eleven locks respectively.)

Zero collection errors, zero tracebacks
(`grep -c "Traceback (most recent call last)"` → **0**; note the
false-positive trap: several tests assert `"Traceback" not in proc.stderr`,
which the failure listing echoes, so the bare word is not a usable probe),
zero xfail, zero xpass.

Exception-class census over `--tb=line`: **34 `AttributeError`, 70
`AssertionError`, nothing else.**

### Mechanical no-regression proof

Test-id lists collected from a throwaway `git worktree` at the pre-M26 commit
`37d7f1a` and from HEAD, then intersected with the failing set:

| Set | Count |
|---|---|
| ids at `37d7f1a` | 777 |
| ids now | 884 |
| ids added | 110 |
| pre-existing ids **removed** | **3** |
| pre-existing ids **failing** | **5** |
| pre-existing ids still GREEN | **769** |

`769 + 5 = 774 = 777 − 3`. The 8 moved ids are exactly the deliberate
changes recorded in the Phase-2 entry, and nothing else moved:

- removed — `test_archive_cascade_no_prompt_archives_all_relations` (replaced
  by `test_archive_bare_cascade_refuses_and_writes_nothing`),
  `test_archive_interactive_yes_also_archives_related`,
  `test_archive_interactive_no_leaves_related_in_place`;
- failing — `test_archive_cascade_dry_run_composes_with_cascade_only`,
  `test_archive_cascade_dry_run_rejects_interactive`, and the three
  parametrizations of `test_archive_mutually_exclusive_cascade_flags_rejected`.

A bare "0 pre-existing regressions" claim would be **false** for M26, and
hiding that is the failure mode this check exists to catch; the honest number
is 8 deliberately-moved ids, itemised above.

### RED classification — all 104 traced to a reason (family counts as of the review fold-in)

| Count | Family | RED reason |
|---|---|---|
| 34 | `tests/test_archive_plan.py` (whole module) | `AttributeError` through the `_m26()` getattr indirection on `archive_candidates`, `plan_archive` (via `_plan`), and `ARCHIVE_EXCLUSION_REASONS` — all landing in Phase 5 |
| 28 | Retirement (D2 / E1) | today the outcome varies by cell: `--cascade` alone archives everything at exit 0; `--cascade --cascade-dry-run` previews at exit 0; `--json` is an unrecognized argument; the mutex-group pairs die with argparse's `not allowed with`; `--cascade-dry-run --interactive` prints the bespoke "incoherent" message; `--help` never says `retired`; and the flags are examined only after the file, config, date and primary metadata have already been checked |
| 8 | Preview (D6) | the candidate-state vocabulary does not exist, and a filtered preview omits every non-matching candidate |
| 10 | Scoped write (E2–E5) | plain assertions against real 1.8.0 defects: the false `could not archive` line on a deduplicated edge, the partial write at exit 0 on a basename collision, the re-dated archived neighbour, the archived primary re-archived in all three shapes, and the typo'd scope that looks like success |
| 3 | Exit-code split (Q4) | the malformed member is reported by the whole-tree walk rather than by the plan pre-flight; the occupied slot and the unwritable member do not refuse the plan at all |
| 9 | `--json` (D7) | argparse `unrecognized arguments: --json` → exit 2 — **each of these also asserts the record or the contract stderr string**, so none is falsely GREEN (see below) |
| 2 | `tests/test_skill.py` | plain assertions; the bundled skill still prescribes bare `--cascade`. Phase 7 |

### Falsely-GREEN test caught and fixed at this gate

`test_archive_json_emits_no_record_on_a_refusal` passed all three
parametrizations at the first baseline run — for entirely the wrong reason.
`--json` is an unrecognized argument today, so argparse already exits 2 with
an empty stdout and an untouched tree, satisfying every assertion the test
made. It now asserts the **contract refusal message** per case and asserts
`unrecognized arguments` **absent**, and is honestly RED. This is precisely
the trap the Phase-2 authoring rule ("every intended-exit-2 test also asserts
its contract stderr string") exists to prevent, and one instance slipped
through; the whole `--json` family was re-verified one by one afterwards.

A second Phase-2 defect was fixed here:
`test_cascade_only_unwritable_candidate_refuses_with_exit_2`'s `finally:`
`chmod` raised `FileNotFoundError` because the baseline archive succeeds and
moves the file, masking the test's real RED reason. Both unwritable cleanups
(here and in `test_archive_plan.py`) now tolerate absence.

### GREEN-at-baseline locks, classified by name

| Lock | Honest status |
|---|---|
| `test_archive_cascade_dry_run_previews_and_writes_nothing` | genuine — a preview writes nothing today too |
| `test_archive_cascade_only_filters_by_glob` | genuine |
| `test_archive_pair_leaves_check_clean` | genuine (M18) |
| `test_archive_cascade_rewrites_edges_for_both_moves_atomically`, `…_rewrites_moved_docs_own_edges`, `test_archive_cascade_trio_lands_edge_clean`, `test_archive_cascade_preserves_reciprocal_pair` | genuine — the four migrated tests ARE the M12 referring-edge and M18 archive-edge no-regression proof, carried across the retirement by re-pointing them at `--cascade-only` |
| `test_scoped_write_with_a_dotted_edge_leaves_check_clean` | **genuine and load-bearing** — the only guard against the Q5 canonicalization regression: once candidates are keyed on the canonical path, the batch must still carry the declared `./b.md` spelling as an alias or the bullet dangles |
| `test_check_clean_after_a_scoped_archive` | genuine — the M12/M18 proof restated at the `docs check` gate on the E1 fixture |
| `test_archive_reason_is_written_to_the_primary_only` | genuine (Q10) — today's cascade already passes `None`; pinned so the rewrite cannot generalise it |
| `test_preview_of_a_primary_only_archive_names_no_candidates` | **degenerate** (Q7) — today's `--dry-run` prints no candidate line because the preview is gated on a cascade flag |
| `test_archive_never_prompts_on_stdin` ×3 | **degenerate** — none of the three D1 shapes reads stdin today either; load-bearing once Phase 7 deletes `_cascade_archive`, the verb's last stdin reader |
| `test_check_tree_legacy_fixtures_gain_no_new_findings[archive-*]` ×4 | genuine — the four Phase-3 trees must add no `missing-inverse` finding |
| `test_archive_referring_edge_rewrite_is_atomic`, `…_refreshes_index_once`, `test_archive_repoints_already_archived_referrer`, `test_archive_leaves_unrelated_archived_content_byte_identical`, `test_archive_oserror_mid_rewrite_exits_2`, `test_archive_with_malformed_excluded_file_succeeds_and_reindexes`, `test_archive_one_endpoint_preserves_reciprocal_pair` | genuine, untouched |
| `test_a3_project_version_is_1_8_0`, `test_c2_docs_version_is_1_8_0`, `test_b1`, `test_b2` | genuine — no version bump in M26 (D8 / M25 — D6) |

### ~~Accepted coverage boundary~~ — WITHDRAWN, the claim was false

Phase 4 originally recorded that the mid-execution `OSError` partial-state
admission "is not reachable from a subprocess test", on the reasoning that
D4's pre-flight catches every filesystem arrangement that would trigger it.
**That was wrong**, the fresh-eyes review disproved it, and the claim is
withdrawn rather than restated: a plan member at mode `0o644` inside a
`0o555` directory passes `os.access(file, W_OK)` — so the pre-flight
legitimately admits the plan — while `atomic_write` still raises
`PermissionError` creating its `.docs-tmp` sibling. The technique was already
in this very test file, in `_readonly_referrer_tree`, whose docstring says in
so many words that a read-only *directory* is the portable trigger.

Re-verified directly before the fix was written: on that arrangement today's
CLI archives the primary, leaves the candidate in place, swallows the
`OSError` in the cascade loop, and exits **0**.
`test_mid_execution_failure_admits_the_partial_state` now pins exit 2, the
admission string **including** the `docs: archive: ` prefix, `stdout == ""`,
and the disk state the admission claims. The unit-seam tests stay as the
`Archived: none` and multi-member coverage.

The remaining honest statement is much narrower: the `<err>` span inside the
admission is the operating system's text and carries an absolute path, so it
is the one part not asserted verbatim; everything either side of it is.

### Phase-7 follow-through list (recorded here so it cannot be lost)

1. `docs/plan.md:454` — the *Resolved questions* bullet still says `--cascade`
   "prompts (`y/N`, defaulting to no) before archiving each one-hop
   `pairs-with` / `child-of` relation". That has been false since M14 and is
   about to be doubly false. Correct it (Phase-1 Q17).
2. `src/docs_cli/skill/SKILL.md:62` — the archive row lists `--cascade` in its
   flag column. Locked by `test_skill_md_teaches_safe_archive_selection`.
3. `src/docs_cli/skill/references/use-cases.md:25` — "`--cascade` opt-in for
   one-hop dependents". Locked by
   `test_bundled_use_cases_teaches_safe_archive_selection`.
4. `CHANGELOG.md` — M26 entries under the existing `UNRELEASED` heading, with
   the upgrade guidance naming both replacement invocations. **No** version
   bump (M25 — D6).
5. `docs/agent-native-invocation.md:250` — a `Lifecycle: draft`,
   `Project: ideas` proposal from 2026-06-03 whose Layer-5 bullet still names
   `--cascade` as a pre-answerable replacement for the prompt. It is a
   historical proposal record, not a spec on the surface-parity gate.
   **Superseded by conductor decision B** (recorded below, and the later
   binding record): the proposal text is kept verbatim — rewriting it would
   falsify what was proposed in June — and a short dated note pointing at the
   safe flow is a **required** edit, so an agent reading the proposal is not
   trapped. Landed with the review fold-in.

### Verification

- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — all files formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 47 source files.
- `.venv/bin/docs check --root docs` — no violations (exit 0).
- `cmp docs/{cli,convention}.md src/docs_cli/skill/references/` — identical.
- `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.
- `git diff --stat <phase-1-commit> -- src/docs_cli/cli.py` — **empty**.
  Phases 1–4 changed no product code, by design.

## Step-1 same-instance audit — 2026-08-13

Consistency / completeness / accuracy audit over Phases 1–4, run by the
implementing instance before handing back. **Eight findings, all fixed;
nothing needed an operator decision.** Two items are surfaced for the
operator/reviewer without being auto-decided (below).

### Accuracy — tests vs the frozen spec

The audit's central check was mechanical: extract every frozen
`docs: archive: …` line from a fenced block in `docs/cli.md`, extract every
string constant (including implicit concatenations and f-string templates, via
`ast`) from `tests/test_cli_archive.py` and `tests/test_archive_plan.py`, and
require each spec line to be matched by some test string. Twenty-two frozen
lines; three findings.

1. **Two ineligibility preview lines were unpinned** —
   `candidate <rel> — ineligible (target does not resolve to a file)` and
   `… (target resolves outside the docs root)`. The unit tests asserted the
   machine-stable `reason` tokens, but no test asserted the rendered human
   line, so Phase 7 could word them freely. Added
   `test_preview_names_the_unresolved_and_outside_root_ineligibilities` on an
   inline tree carrying one eligible, one unresolved, and one escaping
   candidate — which also pins that an escaping candidate is named by its
   canonical form, escape included, and that both count as ineligible in the
   footer.
2. **The apply-mode primary line was unpinned.**
   `docs: archive: archived <rel> -> <dest-rel>` and the ABSENCE of the
   `preview only` line are the only two things distinguishing an apply from a
   preview on stderr. Now asserted in
   `test_cascade_only_dedups_and_prints_no_false_failure`.
3. **The partial-state admission is pinned without its `docs: archive: `
   prefix** — the exception carries the bare message and `_cmd_archive` adds
   the prefix. That is correct, and the prefix is unreachable from a
   subprocess test for the reason already recorded under *Accepted coverage
   boundary*. Left as-is, recorded rather than papered over.

### Tests genuinely pin the contract (the highest-leverage check)

Four further under-constraints found by reading the frozen contract back
against the suite:

4. **The retirement check's ORDER was unpinned.** Phase-1 Q11 says it runs
   before any filesystem access, and every existing retirement test used a
   perfectly valid tree — so an implementation that checked the file, the
   config, the date and the primary's metadata first would have passed them
   all. Added
   `test_archive_retired_flag_is_checked_before_any_filesystem_access`,
   parametrized over a missing file, a malformed `--date`, and a primary that
   does not parse.
5. **The `--quiet` gate was unpinned in both directions.** Added
   `test_quiet_silences_the_preview_but_never_a_refusal`: `--quiet` suppresses
   the candidate lines and the `preview only` line, and a **non-argparse**
   refusal still prints. (The retirement matrix's `--quiet` cell only covered
   a refusal that argparse could also produce.)
6. **"Already archived" being decided by `[archive] dir` was unpinned.** The
   Phase-1 reuse note is explicit that `_in_archive_subdir` is the wrong
   helper because it hardcodes `archive` / `archived` / `project-history`,
   and nothing tested the difference. Added
   `test_archived_test_honours_the_configured_archive_dir` on a tree with
   `dir = "history"`: a candidate under `history/` is ineligible and one under
   a plain `archive/` directory — an ordinary subdirectory on that tree — is
   eligible.
7. **The `archive F --dry-run` matrix row promised a `--json` record that no
   test read.** `test_cascade_only_with_global_dry_run_matches_cascade_dry_run`
   now runs both spellings with `--json` and asserts the two records are equal
   (modulo `primary.source`, which differs by tmp root) and that `dry_run` is
   True / `applied` is False. Also pinned `plan.primary.aliases == ()`.

### Consistency — documentation

8. **`docs/plan.md` was stale.** Both the v2.0-train prose and the M26 tracker
   row still read "milestone setup completed … no TDD phase has started".
   Updated with the Step-1 phase state and the baseline counts. Restated the
   counts across `status.md`, the milestone doc, the phase table, and the
   Phase-2/3/4 records after the audit's six new locks: 867 → **873**
   collected, 87 → **93** failed, 780 passed unchanged.

Also re-verified in this pass: every `Related:` link resolves
(`docs check --root docs` exit 0); every doc edited this step had `Updated:`
bumped through `docs touch`; `docs/INDEX.md` and
`tests/fixtures/expected/docs-INDEX.md` are byte-identical (the `plan.md`
touch above had desynced them, which surfaced as a real
`test_index_output_matches_frozen_snapshot` failure and was re-synced);
`src/docs_cli/skill/references/{cli,convention}.md` are byte-identical to
their sources; the diff across all four commits contains only M26 work; and
one commit per phase, each with the project's `Co-Authored-By` trailer.

### Surfaced, not auto-decided

- **The frozen `--json` key set carries no `reason` field**, so `--reason` is
  observable only in the archived primary's `Archived-reason:` line and not in
  the operation-plan record — unlike `relate --json`, which does carry
  `reason`. The Step-1 plan froze the top-level key set as closed and ordered,
  so Phase 1 implemented it verbatim rather than widening the contract. Adding
  it in Phase 7 would be a one-line schema change plus a field-table row.
  **Resolved by conductor decision A** (below): the top-level `reason` was
  added and the candidate-level field renamed `exclusion_reason`, and both
  shipped in Phase 5/7.
- **`docs/agent-native-invocation.md:250`** — a `Lifecycle: draft`,
  `Project: ideas` proposal from 2026-06-03 whose Layer-5 bullet still names
  `--cascade` as a pre-answerable replacement for the interactive prompt. It
  is a historical proposal record, not a spec on the surface-parity gate.
  **Conductor decision B settled it** and is the later, binding record: keep
  the proposal text verbatim and add a short dated note pointing at the safe
  flow — a required edit, not the operator's call. Landed with the review
  fold-in.

### Post-audit gates

- `.venv/bin/python -m pytest tests/ -q` — **873 collected, 93 failed, 780
  passed** (the intended RED baseline); 0 collection errors, 0 tracebacks,
  0 xfail/xpass; census 33 `AttributeError` + 60 `AssertionError`.
- Mechanical no-regression proof re-run: **769** of the 777 pre-existing ids
  still GREEN, 5 deliberately failing, 3 deliberately removed
  (769 + 5 = 774 = 777 − 3) — unchanged by the audit.
- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/`, `.venv/bin/docs check --root docs` — all
  clean.
- `git diff --stat 37d7f1a..HEAD -- src/docs_cli/cli.py` — **empty** across
  the whole step.

## Step-1 fresh-eyes review fold-in — 2026-08-13

Independent fresh-eyes review of Step 1. It confirmed the suite state, re-derived
the no-regression arithmetic mechanically, re-did the `ast` message-catalog
lockstep check independently, and spot-verified the E1–E5 RED reasons against
real 1.8.0 runs. It returned **one blocker, six should-fixes and nine nits**,
plus three conductor decisions. All of the blocker and should-fixes and eight
of the nits are folded in below. **No `src/docs_cli/cli.py` change** — the
whole step is still contract, tests and fixtures.

### Blocker — an unsatisfiable assertion that hid an M18 regression

`test_cascade_only_excludes_an_archived_neighbour` asserted
`archived.read_bytes() == archived_before` over
`archive/2026-01-01/old.md`. But that fixture doc carries
`- references: plan.md`, and `plan.md` is the **primary moving in that very
invocation**, so M18 — D1 leg 2 *requires* the bullet to be repointed to
`archive/2026-05-28/plan.md`. Verified against live 1.8.0 on the committed
fixture: a plain `docs archive plan.md` rewrites `old.md`
(`a468745755d540dc` → `f80f3519bfa53735`) while leaving `Lifecycle:`,
`Updated: 2026-01-01` and `Archived-reason:` byte-stable.

The test was RED at an earlier assertion, so the contradiction would not have
surfaced until the Phase-8 GREEN gate — the exact M25 "unsatisfiable Step-1
assertion" failure mode. Worse, the cheapest way to make it pass would have
been to suppress the referring-edge rewrite for ineligible archived
candidates, leaving `old.md`'s edge dangling as a `broken-ref` that **no**
test would catch (`test_archive_repoints_already_archived_referrer` archives
with no candidates at all, and nothing ran `docs check` on that tree after a
scoped write).

Now asserted: the file did not move; `Lifecycle:`, `Updated:`,
`Archived-reason:`, the H1 and the prose are unchanged; the M18 rewrite **did**
happen (`- references: archive/2026-05-28/plan.md`, and the bare form gone);
and `docs check` exits 0 on the tree afterwards.

### Should-fixes

| # | Finding | Fix |
|---|---|---|
| 2 | The D1 paragraph in `convention.md` overclaimed — "an archived doc's location, `Updated:` value, and **bytes** are never rewritten by a later archive event" — contradicting `cli.md`'s M18 block. This was the root cause of the blocker, and it had already shipped into the bundled mirror. | Narrowed to name exactly what is immutable and to name the one `Related:` bullet M18 does repoint. Mirror re-synced byte-identically; the milestone's E4 coverage row updated to match. |
| 3 | The recorded "accepted coverage boundary" was **factually wrong** (see the withdrawn section above), leaving the whole `OSError` mid-execution matrix row unpinned. | Withdrawn, not restated. `test_mid_execution_failure_admits_the_partial_state` added on the `0o555`-directory trigger, verified firing before the test was written. |
| 4 | The one documented exception to "no `--json` record on a refusal" — the INDEX-refresh failure emitting `applied: true, index_refreshed: false` — had zero coverage; suppressing the record there (the natural reading of the rule) passed everything. | `test_archive_json_record_is_emitted_on_an_index_refresh_failure`, on a tree whose docs are writable but whose root is not, so the plan executes and only the end-of-batch `INDEX.md` write fails. Trigger verified first: both docs move, exit 2, no `INDEX.md`. |
| 5 | Phase-1 Q8 is BINDING and had **zero** coverage: the candidate scan must not consult `[exclude]` / `.docsignore`. An implementation threading `compile_exclude_predicate` into `archive_candidates` passed the whole suite. | Pinned at both seams — `test_candidate_scan_ignores_the_exclude_predicate` (which first asserts the predicate really does hide the file from a walk, so it cannot pass for the wrong reason) and `test_preview_names_a_candidate_the_exclude_predicate_hides`. |
| 6 | `primary.source` was specified three mutually inconsistent ways, and since `archive_plan_to_json` only sees the plan it could only ever have been `str(plan.primary.path)` — always absolute, so **no** prose reading held. Every test passed an absolute path. | Conductor-binding: `source` IS the `FILE` argument exactly as typed. `ArchivePlan` gains `source: str`; `plan_archive` takes it as a keyword. All three statements aligned; pinned by a unit assertion (`source="./a.md"`) and by `test_archive_json_source_is_the_file_argument_exactly_as_typed`, which invokes the CLI with a relative argument via `cwd=root`. |
| 7 | The apply-mode `--json` `primary` object was never value-asserted — it was excluded from the preview/apply comparison and read nowhere else, so returning `"destination": null` on apply passed. | Asserted by value on the apply side, with `path`/`destination` cross-checked against the preview. |

### Nits folded in (8–13, 15)

- **8** — `"--cascade" in help.stdout` was satisfied by `--cascade-only` alone,
  and one global `"retired"` did not prove **both** flags are marked. Now a
  bare-`--cascade` regex plus `count("retired") >= 2`, and each flag gets its
  own fresh tree so the first invocation cannot mutate the second's.
- **9** — `test_none_matched_counts_ineligible_candidates_and_is_not_no_candidates`:
  `<N>` counts ineligible members, and a glob hitting only an already-archived
  neighbour is "matched none", not "no candidates". Both halves of `cli.md`'s
  "matched means *selected*" sentence.
- **10** — check-order steps 2 and 4 pinned
  (`test_empty_scope_is_checked_before_the_filesystem`,
  `test_archived_primary_is_checked_before_the_selection`); only step 1 had a
  lock. An archived primary with a non-matching scope had an undetermined
  message.
- **11** — `--quiet` now asserted to suppress the `would archive` primary line
  too, not just the candidate lines.
- **12** — `_snapshot` records directories with a marker, so a refusal that
  had already `mkdir`'d `archive/<date>/` before aborting is no longer
  "byte-identical" tree-wide; the collision and none-matched tests also gained
  the explicit `not (root / "archive").exists()` guard.
- **13** — `_SKIP_AS_ROOT` narrowed from the whole
  `test_every_preflight_refusal_leaves_the_tree_byte_identical` to the two
  parametrizations that need mode bits, so a root CI keeps the
  `rolled_back` / `published` assertions for the other four.
- **15** — the `_BARE_CASCADE` regex is stricter than "must not prescribe": it
  forbids naming the flag at all. That is the intent — the skill's flag column
  reads as a prescription — so the docstring was corrected to say so rather
  than the regex loosened.

Nit 14 became conductor decision C below.

### Conductor decisions applied

- **A — `--json` gains a top-level `reason`** carrying `--reason`, mirroring
  `relate --json`, and the candidate-level `reason` is **renamed
  `exclusion_reason`** to remove the collision, matching
  `ARCHIVE_EXCLUSION_REASONS`. The `ArchiveMove` field is renamed in step with
  the JSON key so code and record cannot drift. Applied to the milestone's
  BINDING schema and frozen signatures, the `cli.md` field table and example,
  the bundled mirror, and every test. Cheap now; a breaking change after 2.0.
- **B — `docs/agent-native-invocation.md` keeps its proposal text** (rewriting
  it would falsify the record of what was proposed in June) and gains a short
  dated note pointing at the safe flow. The doc is not restructured.
- **C — `--cascade-only` refuses a negated (`!`) pattern**, exit 2:
  `docs: archive: --cascade-only does not support negated ('!') patterns; state the exact bounded selection`.
  `_compile_docsignore_pattern` returns a `negate` flag that 1.x's
  `_cascade_set` silently **discarded**, so `!plan.md` behaved as `plan.md` —
  the opposite of how it reads. And the honest meaning, "everything except X",
  is the unbounded selection D1 exists to prevent. Documented in `cli.md` and
  the mirror, added to the frozen catalog and to check-order step 2, pinned by
  `test_cascade_only_negated_pattern_refuses`.

### Post-fold-in baseline

- **884 collected, 104 failed, 780 passed.** Zero collection errors, zero
  tracebacks, zero xfail/xpass. Census: **34 `AttributeError`, 70
  `AssertionError`**, nothing else.
- Mechanical no-regression proof re-run against `37d7f1a`: **769** of the 777
  pre-existing ids still GREEN, **5** deliberately failing, **3** deliberately
  removed (769 + 5 = 774 = 777 − 3) — unchanged by the review fold-in.
- Both engineered triggers were verified to fire against the shipped 1.8.0
  binary **before** their tests were written, and the CLI-level RED reason for
  each is currently argparse rejecting `--json`; each carries the contract
  assertion behind it that makes the eventual GREEN honest.
- `ruff check` / `ruff format --check` / `mypy src/ tests/` /
  `docs check --root docs` — all clean; bundled refs byte-identical; INDEX
  snapshot re-synced.
- `git diff --stat 37d7f1a..HEAD -- src/docs_cli/cli.py` — still **empty**.

## Phase 5 — Update Base Interfaces — 2026-08-13

### Objective

Land the frozen Phase-5 signatures as real code — the archive plan models,
the two pure helpers, and the `--json` serializer — without completing any
behaviour, so the behaviour tests stay honestly RED at the seam rather than
failing for a second, accidental reason.

### Actions taken

- **`CoordinatedWriteError` widened** (`cli.py`) from "a `docs relate`
  coordinated two-file publish" to a coordinated multi-file publish naming
  both producers, and given a keyword-only `exit_code: int = 2`. This is the
  sanctioned widening the frozen reuse note calls for ("widen its docstring;
  do not add a second exception class"), and it is the only way the frozen
  `preflight_archive_plan(plan) -> None` signature can carry the Phase-1 Q4
  exit-code split — see *Deviations* below. The default preserves every M25
  construction site byte-for-byte.
- **`ARCHIVE_EXCLUSION_REASONS`** added to the Vocabulary block beside
  `RECIPROCAL_VERBS`, with the precedence rule in its comment.
- **`ArchiveMove` / `ArchivePlan`** added to the Models section immediately
  after `RelatePlan`, verbatim from the frozen signature block, plus the
  `moves` property (primary first, then the selected candidates — the
  execution order the partial-state admission reads in). Their docstrings
  record two facts a reader would otherwise have to derive: `dest` /
  `dest_rel` are None until `plan_archive` fills them and only for SELECTED
  members, and an `outside-root` candidate's `path` deliberately does not lie
  under `root` (it is never opened).
- **`_is_archived_rel(rel, config)`** — the
  `rel == config.archive_dir or rel.startswith(config.archive_dir + "/")`
  idiom already used by `check_doc` and `_cmd_relate`, lifted to a named
  helper. Explicitly **not** `_in_archive_subdir`, which hardcodes
  `archive` / `archived` / `project-history` and ignores `[archive] dir`;
  `test_archived_test_honours_the_configured_archive_dir` exists to catch
  exactly that substitution.
- **`_archive_destination(root, config, date_str, name)`** — one expression
  for the destination `_archive_one` writes and the planner previews, so the
  two cannot drift.
- **`archive_plan_to_json(plan, *, dry_run, applied, index_refreshed)`** —
  modelled on `relate_plan_to_json`, with the closed, ordered top-level key
  set the schema pins.

### Evidence

```
.venv/bin/ruff check .            →  All checks passed!
.venv/bin/ruff format --check .   →  46 files already formatted
.venv/bin/mypy src/ tests/        →  Success: no issues found in 47 source files
.venv/bin/python -m pytest -q     →  781 passed, 103 failed
```

Exactly the predicted ledger: **+1 GREEN**,
`test_archive_exclusion_reasons_is_the_frozen_token_set`. Every other M26
test still fails with `AttributeError: archive_candidates / plan_archive` —
the honest seam. `_cmd_archive` is untouched in this phase.

### Deviations

- **`CoordinatedWriteError` gains `exit_code`** (conductor-resolved, BINDING).
  The frozen signature block does not mention it. The CLI must exit **1** for
  two pre-existing conditions and **2** for four new ones, and a
  `preflight_archive_plan(plan) -> None` that raises a single exception class
  has nowhere else to carry that split; matching on message text would be the
  only alternative and is fragile. Defaults to 2, so `docs relate` is
  byte-identical.
- **Placement.** `archive_plan_to_json` lands in the archive block with the
  rest of the M26 planner rather than immediately after `relate_plan_to_json`
  as the Step-2 plan sketched: that section is headed *Relationship repair —
  `docs relate` (M25)*, and filing an archive serializer under it would
  mis-shelve it. Cosmetic; no behaviour difference.

## Phase 6 — Implement Offline/Core Path — 2026-08-13

### Objective

Implement the whole archive seam behind the CLI — candidate discovery,
planning, the validate-all-first pre-flight, ordered execution, and the
residual partial-state admission — with `_cmd_archive` still untouched, so
the unit contract goes GREEN on its own and the CLI contract stays honestly
RED.

### Actions taken

Five functions added to the archive block (`cli.py`), between
`_archive_destination` and the still-live 1.x cascade helpers:

- **`_candidate_exclusion_reason(rel, root, config)`** — the ineligibility
  test, written in the frozen precedence order so the order IS the
  precedence: `outside-root`, `already-archived`, `unresolved-target`. It
  never returns `not-selected`, which is the scope's verdict, not an
  ineligibility.
- **`archive_candidates(doc, root, config, scope)`** — one-hop
  `pairs-with` / `child-of` edges in declaration order, deduplicated on the
  canonical path with the first declaration winning the verb and every
  declared spelling kept in `aliases`; self-edges silently skipped; the scope
  compiled by `_compile_docsignore_pattern` and matched against the CANONICAL
  path. It does **not** consult `compile_exclude_predicate` (Phase-1 Q8) and
  does **not** `parse()` a candidate — an unparseable candidate is still a
  candidate, and the pre-flight owns that refusal.
- **`plan_archive(...)`** — pure; builds the primary move and fills
  destinations for the selected candidates only, which is precisely the
  record's "destination non-null iff selected" rule.
- **`preflight_archive_plan(plan)`** — the five proofs, each over the whole
  plan, raising `CoordinatedWriteError(rolled_back=True, published=())` with
  `exit_code=1` for the two pre-existing conditions and the default 2 for the
  four new ones. Exactly **two** `os.access` checks: the source file and the
  nearest existing ancestor of the dated destination directory.
- **`apply_archive_plan(plan)`** / **`_archive_partial_state(...)`** —
  `_archive_one` kept verbatim as the per-document executor, driven in
  `plan.moves` order with `--reason` on the primary only; returns the
  canonical `(old_rel, new_rel)` pair per member plus one per declared alias.

### Two traps the tests pin, and how they are handled

- **No source-parent-directory writability check.** A `0o644` file inside a
  `0o555` directory passes `os.access(file, W_OK)` and still breaks
  `atomic_write`, which is the engineered trigger behind
  `test_mid_execution_failure_admits_the_partial_state` — the milestone's
  only end-to-end partial-state lock. A parent-directory check would convert
  it into a pre-flight refusal and delete the lock. `apply_relate_plan`
  (M25 — D5) declines the same check for the same reason; the code now says
  so in both places.
- **The dated directory is pruned when nothing had moved.** `_archive_one`
  does `dest.parent.mkdir(parents=True, exist_ok=True)` BEFORE `atomic_write`,
  so a first-member failure leaves an empty `archive/<date>/` behind.
  `_archive_partial_state` removes it (and its parent) with a suppressed
  `rmdir`, the `_opportunistic_rmdir` idiom, so a non-empty archive directory
  is left alone. Without it
  `test_apply_archive_plan_admission_when_nothing_had_moved_yet`'s
  `assert not (root / "archive").exists()` fails.

`MetadataError` is caught alongside `OSError` in `apply_archive_plan` even
though the pre-flight makes it unreachable: "unreachable plus an uncaught
raise" equals a traceback if that reasoning is ever wrong, and several tests
pin `"Traceback" not in stderr`. The frozen admission wording reads correctly
for either.

### Evidence

```
.venv/bin/ruff check .            →  All checks passed!
.venv/bin/ruff format --check .   →  46 files already formatted
.venv/bin/mypy src/ tests/        →  Success: no issues found in 47 source files
.venv/bin/python -m pytest -q     →  814 passed, 70 failed
.venv/bin/python -m pytest -q tests/test_archive_plan.py  →  34 passed
```

Exactly the predicted ledger: **+33 GREEN**, the whole of
`tests/test_archive_plan.py` — the D3 discovery set, the D4 pre-flight set
including all six `test_every_preflight_refusal_leaves_the_tree_byte_identical`
parametrizations, the D4 execution set, and the D7 serializer set. The
remaining 70 failures are all CLI-level (68 in `tests/test_cli_archive.py`,
2 in `tests/test_skill.py`) and are Phase 7's work.

`git diff -- src/docs_cli/cli.py` for this phase is a single insertion hunk;
`_cmd_archive` is byte-unchanged, and the 1.x `_cascade_set` /
`_print_cascade_footer` / `_cascade_archive` helpers are still live because
`_cmd_archive` still calls them. Phase 7d deletes all three in the same
change that stops calling them.

## Phase 7 — Update Tool/Wrapper Layer — 2026-08-13

### Objective

Wire the seam to the command line in the frozen check order, delete the 1.x
cascade machinery it supersedes, and bring every surface — `--help`,
`cli.md`, `convention.md`, the bundled skill, and the `UNRELEASED`
CHANGELOG — into parity in the same change.

### 7a — argparse

- **The mutually-exclusive group is gone.** `--cascade`, `--cascade-only`,
  and `--interactive` are now plain arguments (Phase-1 Q12). Nothing else may
  go in a mutex group, or a combination naming a retired flag would still die
  with argparse's `not allowed with` instead of the M26 refusal.
- `--cascade` and `--interactive` keep `action="store_true"` and share ONE
  help string beginning `RETIRED in docs 2.0`, so `--help` marks both.
- `--json` added locally on the subparser (as `check` / `list` / `migrate` /
  `relate` do), and the subparser `description` now names the three D1
  shapes.

### 7b / 7c — `_cmd_archive` in check order

Rewritten end to end as the nine frozen steps. The details that are contract,
not style:

- **Steps 1 and 2 run before any filesystem access.** The retirement guard is
  the first statement in the function, so it wins over a missing file, a bad
  `--date`, and a malformed primary; the `--cascade-only` shape test is purely
  lexical, so it precedes even the missing-file check.
- **A blank / comment-only / negated scope refuses in EVERY mode**,
  a preview included (conductor-resolved). D6's "a preview never fails"
  governs a *valid glob that selects nothing* — a selection outcome. A
  malformed pattern is a malformed invocation. `cli.md` § *Preview* now states
  the carve-out explicitly rather than leaving it to be inferred, and both
  `test_cascade_only_empty_pattern_refuses` and
  `test_cascade_only_negated_pattern_refuses` gained a `preview`
  parametrization (+4 test ids; the suite is now **888 collected**).
- **`root` and the primary are both resolved once, up front.**
  `_root_relative` falls back to the bare filename for a path it cannot
  relativise, which would silently mis-name a `sub/x.md` primary given
  relatively.
- **`source=args.file`** — the raw argument, never `str(primary)`.
- **`CoordinatedWriteError` is caught BEFORE `OSError`** wherever both could
  apply. It is an `OSError` subclass, so the reverse order silently swallows
  every refusal into the generic handler.
- **The post-move `try` is split in two.** `_rewrite_referring_edges` failing
  is M14 (A4): exit 2, **no record**. `_refresh_index` failing is the one
  documented post-write exception: exit 2 **with** the record, carrying
  `"applied": true, "index_refreshed": false`. It catches `OSError` too —
  `_cmd_relate`'s refresh handler catches only the two metadata errors, and a
  read-only root raises `OSError`, which is exactly what
  `test_archive_json_record_is_emitted_on_an_index_refresh_failure` triggers.

`_print_archive_lines(plan, *, dry_run, cascade)` renders the frozen
preview/apply vocabulary, with `_candidate_state` and a module-level
`_ARCHIVE_INELIGIBLE_PROSE` mapping keyed on the three ineligibility tokens
(membership in that mapping is also what the counts footer uses to tell
"ineligible" from "not selected").

### 7d — deletions

`_cascade_set`, `_print_cascade_footer`, and `_cascade_archive` are deleted.
`_CASCADE_VERBS` stays, now consumed by `archive_candidates`. Deleting
`_cascade_archive` removes `docs archive`'s last `sys.stdin` read, which is
what turns `test_archive_never_prompts_on_stdin` (×3) from a degenerate lock
into a genuine one. `grep -n "stdin" src/docs_cli/cli.py` now shows only
`docs new --body-from -` and `docs install-skill`'s TTY prompt.

1.x's `docs: could not create archive directory: <exc>` (exit 2) disappears
with them: that `OSError` now surfaces as the D4 partial-state admission,
also exit 2. No test and no spec line asserted the string; `cli.md`'s exit-2
row no longer lists "archive-dir creation failure" separately, because the
admission row covers it.

### 7e — surface parity

| Target | Edit |
|---|---|
| `src/docs_cli/skill/SKILL.md` | the archive row now teaches `--reason`, `--date`, `--json`, and the preview-then-scope flow. It does not name bare `--cascade` **at all** — the flag column reads as a prescription, and `references/cli.md` ships alongside carrying the retirement in full. |
| `src/docs_cli/skill/references/use-cases.md` | same prescription in the shipped use-case catalog. |
| `src/docs_cli/skill/references/{cli,convention}.md` | re-copied after the spec edits; `cmp` byte-identical. |
| `CHANGELOG.md` (`UNRELEASED`) | `### Added` — the three safe shapes, `--cascade-dry-run`, `--cascade-only`, `--json`. `### Changed` — the two retirements (BREAKING) and the new human vocabulary. `### Upgrading from 1.x` — the two-line replacement recipe. **No version bump, no dating** (M25 — D6 / M29). |
| `docs/cli.md` | the § *Preview* carve-out sentence, and the exit-2 row corrected. |
| `docs/plan.md` | the *Resolved questions* bullet still claimed `--cascade` "prompts (`y/N`, defaulting to no)" — false since M14 (B1) and doubly false now. Rewritten to the M26 authorization rule (Phase-1 Q17). |
| `docs/agent-native-invocation.md` | already carries conductor decision B's dated note (landed with the review fold-in); the Phase-4 follow-through list's "operator's call" wording is corrected here, since decision B is the later binding record. |

### Evidence

```
.venv/bin/ruff check .            →  All checks passed!
.venv/bin/ruff format --check .   →  46 files already formatted
.venv/bin/mypy src/ tests/        →  Success: no issues found in 47 source files
.venv/bin/python -m pytest -q     →  887 passed, 1 failed  (888 collected)
```

Every M26 behaviour test is GREEN. The single failure is **not** missing
behaviour — it is a defect in a Step-1 test's own tree builder, described
next, and it is fixed in its own labelled commit rather than folded in here.

## Defect in a Step-1 test — `test_archive_help_still_registers_the_retired_flags`

The test's final loop builds a fresh tree per retired flag:

```python
for flag in ("--cascade", "--interactive"):
    root = _two_relation_tree(tmp_path / flag.strip("-"))
```

`_two_relation_tree` does `root = tmp_path / "two-rel"; root.mkdir()` with
`parents=False`, and `tmp_path / "cascade"` does not exist — so the helper
raises `FileNotFoundError` **inside the test body, before the CLI is ever
invoked**. No product code can satisfy it. It was masked at the Phase-4
baseline because the test failed earlier, on the `--help` assertions, and it
surfaced the moment Phase 7a made those pass.

The fix is `root.mkdir(parents=True)` in the helper — one word, in a
directory-creation call. **No assertion is changed, relaxed, or removed**, and
the fix strictly *strengthens* enforcement: the loop's
`"unrecognized arguments" not in proc.stderr` assertions — the only lock on
the flags staying registered rather than deleted — could never run before and
now do. Every other caller passes an existing `tmp_path`, for which
`parents=True` is a no-op.

Recorded here, and surfaced to the operator and the fresh-eyes review, rather
than folded silently into the Phase-7 commit — the M25 precedent for a
defective Step-1 test (`7e4feb1`).

## Phase 8 — Run Tests (GREEN) — 2026-08-13

### Objective

Run every gate, and prove mechanically — not by assertion — that no
pre-existing test was lost or broken.

### The gate

```
.venv/bin/python -m pytest tests/ -q --co   →  888 collected, 0 collection errors
.venv/bin/python -m pytest tests/ -q        →  888 passed, 0 failed
.venv/bin/ruff check .                      →  All checks passed!
.venv/bin/ruff format --check .             →  46 files already formatted
.venv/bin/mypy src/ tests/                  →  Success: no issues found in 47 source files
.venv/bin/docs check --root docs            →  no violations (exit 0)
cmp docs/cli.md src/docs_cli/skill/references/cli.md               →  identical
cmp docs/convention.md src/docs_cli/skill/references/convention.md →  identical
diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md           →  identical
```

Zero collection errors, zero xfail, zero xpass, and
`grep -c "Traceback (most recent call last)"` over the run output → **0**.
(The Phase-4 false-positive trap still applies in the other direction:
several tests assert `"Traceback" not in proc.stderr`, so the bare word can
appear in a failure echo — with no failures there is nothing to echo.)

`id -u` → **1000**, not root, so the five `_SKIP_AS_ROOT` locks really ran:
two of the six `test_every_preflight_refusal_leaves_the_tree_byte_identical`
parametrizations plus the unwritable-candidate, mid-execution partial-state,
and INDEX-refresh-failure CLI tests. Under a root CI those would silently
skip and the writability and partial-state contracts would go unproven.

### Mechanical no-regression proof

Test-id lists collected from a throwaway `git worktree` at the pre-M26 commit
`37d7f1a` and from HEAD, then intersected:

```
pre-existing ids at 37d7f1a                        777
  deliberately removed at M26 (comm -23)             3
  carried over to HEAD (comm -12)                  774      777 − 3 = 774 ✓
carried-over ids re-run explicitly                 774 passed, 0 failed
new ids added by M26 (comm -13)                    114      774 + 114 = 888 ✓
```

The three removed ids are the ones M26 deliberately reverses, each named in
the Phase-2 record and replaced by a test asserting the new contract:

```
tests/test_cli_archive.py::test_archive_cascade_no_prompt_archives_all_relations
tests/test_cli_archive.py::test_archive_interactive_no_leaves_related_in_place
tests/test_cli_archive.py::test_archive_interactive_yes_also_archives_related
```

The 774 carried ids were re-run as an explicit id list (`pytest -q @ids`),
not inferred from the full-suite total: **774 passed**. Among them are the
**5** pre-existing ids that were RED at the Phase-4 baseline and are now
GREEN — `test_archive_cascade_dry_run_composes_with_cascade_only`,
`test_archive_cascade_dry_run_rejects_interactive`, and the three
`test_archive_mutually_exclusive_cascade_flags_rejected` parametrizations —
so the Phase-4 accounting (769 GREEN + 5 RED + 3 removed = 777) closes
exactly.

The 114 new ids are Phase 2/3's 110 plus the 4 preview-mode parametrizations
Phase 7 added for the conductor-resolved malformed-scope carve-out.

A bare "0 regressions" claim would be false: 3 pre-existing ids really are
gone, deliberately. The arithmetic above is the honest form.

### Defect found and fixed

One, described in full under *Defect in a Step-1 test* above: a missing
`parents=True` in `_two_relation_tree`, which made
`test_archive_help_still_registers_the_retired_flags` unsatisfiable by any
implementation. Fixed in its own labelled commit; no assertion changed.

## Phase 9 — Integrate / Accept / Dogfood — 2026-08-13

### Objective

Run the real milestone-closeout workflow end to end against this project's
own docs tree — the tree E1 was reproduced on — and then exercise every
refusal, proving each changes zero bytes.

**On a throwaway copy only.** Everything below ran in
`…/scratchpad/m26-dogfood/`, never against the live `docs/`. Proof:
`git status --porcelain docs/` is **empty** afterwards. Each refusal got its
own fresh `cp -a` copy, so no flow could observe another's mutation.

### 1 — Unfiltered preview: E1, reproduced and defused

`docs archive tree/m25-reciprocal-relationship-integrity.md --cascade-dry-run
--json --date 2026-08-13` → exit **0**, 71-file tree byte-identical:

```
docs: archive: would archive m25-reciprocal-relationship-integrity.md -> archive/2026-08-13/m25-reciprocal-relationship-integrity.md
docs: archive: candidate plan.md — not selected (no --cascade-only scope)
docs: archive: candidate m25-reciprocal-relationship-integrity-impl.md — not selected (no --cascade-only scope)
docs: archive: candidate cli.md — not selected (no --cascade-only scope)
docs: archive: candidate convention.md — not selected (no --cascade-only scope)
docs: archive: candidate test-strategy.md — not selected (no --cascade-only scope)
docs: archive: candidate status.md — not selected (no --cascade-only scope)
docs: archive: 6 candidate(s): 0 selected, 6 not selected, 0 ineligible
docs: archive: preview only — nothing was written
```

This is E1 exactly: the six documents 1.x's bare `--cascade` would have
swept into the archive — this project's entire specification spine — now
named, counted, and **not** authorized. The record carries all six with
`"selected": false, "exclusion_reason": "not-selected"`.

### 2 — Filtered preview: what the scope leaves behind

Adding `--cascade-only 'm25-*'` → exit 0, still byte-identical: the impl log
`selected -> archive/2026-08-13/…`, and the five spine docs each
`not selected (outside --cascade-only 'm25-*')` —
`6 candidate(s): 1 selected, 5 not selected, 0 ineligible`, `preview only`.
The judgement the preview exists to support is visible without running it.

### 3 — The scoped write

Dropping `--cascade-dry-run` → exit **0**. Both M25 documents landed in
`archive/2026-08-13/`; `plan.md`, `cli.md`, `convention.md`,
`test-strategy.md`, and `status.md` are still at the root. The stderr is the
preview's, verbatim, with two differences: `archived` instead of `would
archive`, and no `preview only` line.

`docs check --root tree` → **no violations** (exit 0). A follow-up
`docs index` is a **byte no-op**, so the end-of-batch reindex left INDEX
fully refreshed.

### 4 — The preview and apply records are diffable

Dropping the three state bits and `primary.source`, the scoped preview
record and the apply record are **identical**, key order included — which is
the whole point of D7's one-shape rule.

### 5 — Refusals, each on a fresh copy, each byte-verified

| Flow | Exit | stdout | Tree |
|---|---|---|---|
| `--cascade` | 2 | empty | byte-identical, no new directory |
| `--interactive` with `< /dev/null` | 2 | empty | byte-identical; **0** `[y/N]` prompts, elapsed **0s** against a 20s timeout — it never blocks |
| `--cascade-only 'typo-*' --json` | 2 | empty | byte-identical, no new directory |
| an already-archived primary (`archive/2026-06-01/m16-…md`) under `--cascade-dry-run --json` | 2 | empty | byte-identical, no new directory |

Each printed its frozen message. The typo'd scope reported
`matched none of the 6 one-hop candidate(s); refusing before any write` —
E5, which in 1.x archived the primary and exited 0. The archived primary was
refused under the **preview** shape, confirming the refusal is not an
authorization question.

"No new directory" is asserted from a `find -type d` snapshot, not just a
file-hash set: a refusal that had already created `archive/<date>/` would
otherwise pass a files-only comparison.

### 6 — The live tree

`git status --porcelain docs/` → empty. The throwaway trees are not
committed.

## Phase 10 — Quality, Docs, Refactor — 2026-08-13

### Simplify pass

Two candidates, both from the Step-2 plan:

- **`_is_archived_rel` replaces the duplicated inline idiom.** The
  `rel == config.archive_dir or rel.startswith(config.archive_dir + "/")`
  expression existed at five sites; the two M25 `relate` ones
  (`_plan_relate_edit` and `_cmd_relate`'s archived-endpoint guard) now call
  the named helper. Suite re-run: **888 passed** — the condition for making
  the change at all.
- **`preflight_archive_plan`'s per-check loops stay separate.** Collapsing
  them into one per-member loop would save four lines and cost the frozen
  proof order: each loop owns a distinct message and a distinct exit code,
  and the order across members is what makes the refusal an operator sees
  deterministic.

The three remaining copies of the idiom (`check_doc`, `_cmd_list`, and
`project set`, the last against a bare `archive_dir` local rather than a
`Config`) are left alone: they are outside M26's blast radius, and a
mechanical sweep of untouched verbs is not what a milestone's simplify pass
is for. Noted for a future pass.

### Docs closed

- **`docs/architecture.md`** — a new `### archive (M26)` block after
  `### relate (M25)` with the `archive_candidates` → `plan_archive` →
  `preflight_archive_plan` → `apply_archive_plan` →
  `_rewrite_referring_edges` → `_refresh_index` pipeline, and the point that
  matters most: M26's boundary is **validate-all-first with a residual
  admission**, deliberately not M25's staged publish plus rollback.
- **`src/docs_cli/cli.py` module docstring** — one M26 sentence in the
  milestone paragraph.
- **`docs/test-strategy.md`** — the `archive-*` fixture family in the
  fixture-source list, and two *Critical paths* entries: a scope selecting
  nothing on a write refuses with zero mutation, and a mid-execution
  `OSError` produces an exact partial-state admission.
- **Trackers** — this log, the milestone doc (every phase and all eight
  deliverables ticked, Progress rewritten), `docs/status.md`, and
  `docs/plan.md`'s M26 row.
- **`pyproject.toml` untouched.** The package stays `1.8.0`; M29 performs the
  single bump (M25 — D6). `test_a3_project_version_is_1_8_0` and
  `test_c2_docs_version_is_1_8_0` are the guards.

### Final gate

```
.venv/bin/ruff check .            →  All checks passed!
.venv/bin/ruff format --check .   →  46 files already formatted
.venv/bin/mypy src/ tests/        →  Success: no issues found in 47 source files
.venv/bin/python -m pytest -q     →  888 passed
.venv/bin/docs check --root docs  →  no violations (exit 0)
cmp docs/{cli,convention}.md src/docs_cli/skill/references/  →  identical
diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md     →  identical
```

## Step-2 same-instance consistency audit — 2026-08-13

Run against Step 2's own work after Phase 10, per the ship-milestone
`consistency-check.md`.

### Found and fixed

1. **A real defect: an unreadable plan member produced a traceback.**
   `preflight_archive_plan`'s first proof calls `read_text()` on every member,
   so a member that exists but is mode `0o000` raises `PermissionError`
   *before* its writability is ever tested — and `PermissionError` is an
   `OSError`, not a `CoordinatedWriteError`, so it escaped `_cmd_archive`'s
   refusal handler. Reproduced directly: exit 1 with a full traceback. It is
   not one of the five enumerated refusals, and 1.x handled it (badly worded,
   but cleanly), so this was a robustness regression. Fixed with an `OSError`
   clause **after** the `CoordinatedWriteError` one — the same clean
   `docs: archive: <exc>` at exit 2 the M14 (A4) rewrite failure gets, with
   the tree untouched because the pre-flight writes nothing. Pinned by the new
   `test_unreadable_plan_member_exits_cleanly_without_a_traceback`
   (`_SKIP_AS_ROOT`), and `cli.md`'s exit-2 row now names the condition.
   Suite: **889 passed**.
2. **`docs/plan.md`'s v2.0 narrative still said "Phase 5 opens Step 2."**
   Rewritten to the implementation-complete state with Step 2's numbers.
3. **A stale "surfaced, not auto-decided" bullet** in the Step-1 audit record
   claimed the `--json` key set carries no `reason` field. Conductor decision
   A added it; the bullet now says so and points at the decision.
4. **`docs/architecture.md`'s module map** described `archive` as "M2; M7
   rename; M12 referring-edge rewrite" and `cli.py` as "~3.8k lines". Both
   refreshed (M26 added; ~7.0k lines).
5. **A CHANGELOG transcript was internally inconsistent** — it showed two
   candidate lines under a `6 candidate(s)` footer. Rewritten as a coherent
   four-candidate transcript that also demonstrates an ineligible member.

### Verified clean

- **Completeness.** All eight Deliverables and all eight Success criteria
  checked against the milestone doc, not from memory; every phase in range has
  a dated entry and an accurate progress-table row. No TODO / FIXME /
  `NotImplementedError` / commented-out code in the new block.
- **Code vs spec.** All **23** frozen `docs: archive: …` lines in `cli.md` are
  pinned verbatim by a passing test; the two retirement lines were
  additionally byte-compared against `cli.md` by running the CLI and diffing.
  The `--json` schema matches the spec exactly — top-level key set, order, and
  the five per-candidate keys. Every frozen Phase-5 signature exists in
  `cli.py`, and `ArchiveMove` / `ArchivePlan` carry exactly the frozen fields
  in the frozen order. The milestone catalog and `cli.md` agree on every line
  (the one apparent difference, the `archived <primary-rel>` apply line, is in
  `cli.md` as prose rather than in the fenced block).
- **Docs.** `status.md`, the milestone, the log, and `plan.md` agree on phase
  progress, counts, dates, and next pointers. No live prescription of
  bare `--cascade` survives anywhere in `docs/` or the bundled skill — the
  remaining mentions are historical logs, the upgrade recipe, and the M26
  contract itself.
- **Generated artifacts.** `docs check --root docs` exit 0; `docs/INDEX.md`
  and `tests/fixtures/expected/docs-INDEX.md` byte-identical;
  `references/{cli,convention}.md` byte-identical to their sources.
- **Codebase.** The diff across the whole step touches 15 files, all M26's;
  `pyproject.toml` is byte-untouched. New code follows the file's existing
  naming, error-handling, and output conventions.
- **Commits.** One per phase, plus two deliberately separate ones (the Step-1
  test-helper fix and this audit), each with the project's `Co-Authored-By`
  trailer. No secrets staged.

### Surfaced, not auto-decided

- **A Step-1 test was changed.** `_two_relation_tree`'s `mkdir` gained
  `parents=True` (see *Defect in a Step-1 test* above). No assertion was
  touched and the change strictly increases what is enforced, but it is a
  Step-1 artifact and belongs in front of the operator.
- **The unparseable-primary refusal keeps its bare `docs: <exc>` prefix**
  (exit 1) while every new M26 message is prefixed `docs: archive: `. The
  `parse()` call predates the milestone and no test pins the prefix; changing
  it would be an unpinned behaviour change, so it was deliberately left. A
  one-line M29 nit if the inconsistency is judged worth closing.
- **`--reason ""` is accepted and silently dropped**, unlike `docs relate`,
  which refuses an empty reason. Untested, 1.x-compatible, out of M26's frozen
  scope; the record faithfully carries `""`. Also an M29 nit.
- **Three copies of the archived-rel idiom remain** in `check_doc`,
  `_cmd_list`, and `project set` (the last against a bare `archive_dir` local
  rather than a `Config`). Left alone as outside M26's blast radius.

## Step-2 fresh-eyes review fold-in — 2026-08-13

An independent review exercised the built code rather than reading this log.
It confirmed D1–D8 and E1–E5 genuinely fixed, the Q4 exit-code split correct,
both frozen-signature amendments matching the code, the mirrors byte-identical,
the no-regression arithmetic exact, the `_two_relation_tree` claim (by re-running
the entire Step-1 suite against the implementation and finding exactly that one
genuine failure, with no assertion weakened anywhere), the +4 preview
parametrizations genuine, and the Phase-9 dogfood reproducible verbatim on a
fresh copy. It found **one blocker — a path Step 2 created.**

### Blocker — a primary resolving outside the root was archived INTO the tree

Step 2 replaced 1.x's `file_path.resolve().relative_to(root_resolved)` — which
raised `ValueError` and hard-stopped **before any write** — with
`_root_relative()`, whose bare-filename fallback the docstring calls "only
reachable for the synthetic paths in unit tests". That invariant was **false at
the new call site**. Two shapes, both reproduced:

- **A symlink out of the tree.** `ln -s /ext/real.md w/link.md; docs archive
  link.md` → exit 2 with `[Errno 2] No such file or directory`, *after*
  `/ext/real.md` had already been moved to `w/archive/<date>/real.md`, leaving
  `w/link.md` dangling and `INDEX.md` stale. 1.x: exit 1, nothing moved.
- **A mismatched `--root`.** `docs archive /outside/foreign.md --root w` →
  **exit 0**, the foreign document moved across the tree boundary, every
  stderr line and the `--json` `primary.path` naming a **fabricated** in-tree
  rel, and `docs check` afterwards reporting no violations.

The second is precisely the silent, undetectable partial write E3 exists to
eliminate, in the milestone whose entire purpose is to stop unauthorized
archive writes — and it was the sole falsification of Step 2's "no pre-existing
exit code silently changed" claim (1 → 0/2, with a write).

**Fixed** by proving the primary lies under the root immediately after it is
resolved, before `parse()` and before anything else:

```
docs: archive: <path> is outside the resolved docs root (<root>); refusing before any write
```

Exit **1** — 1.x's own code for the condition, and the cross-verb convention
`cli.md` already states for `touch` / `stamp` / `project set` / `relate`; the
wording is those verbs' phrase plus M26's frozen-catalog prefix and suffix, so
archive invents neither new semantics nor new vocabulary. Added to the frozen
message catalog, the compatibility matrix, the exit-code split paragraph, both
of `cli.md`'s exit-code tables, the check-order list, the cross-verb convention
block, and the mirror; pinned by
`test_primary_reached_through_a_symlink_out_of_the_tree_refuses` and
`test_primary_outside_an_explicit_root_refuses`, which assert the foreign file
is byte-unchanged, the dated directory is never created, and no INDEX is
written.

### Should-fixes

- **The `OSError`-escapes-the-handler fix covered one of three sites.** The
  Step-2 audit fixed the unreadable plan MEMBER; an unreadable PRIMARY
  (`parse(primary.read_text(), …)`) and an unreadable REFERRING doc (the
  whole-tree walk) still tracebacked. Both are 1.x-byte-identical and so not
  regressions, but M26 had created the inconsistency. All three now share one
  rule — **an unreadable file is `docs: archive: <exc>` at exit 2, never a
  traceback** — stated that way in both exit-code tables and pinned by
  `test_unreadable_primary_exits_cleanly_without_a_traceback` and
  `test_unreadable_referring_doc_exits_cleanly_without_a_traceback`. A
  *malformed* referring doc keeps its exit 1 (M12, unchanged).
  `_cmd_relate` has the same shape via `plan_relate`'s endpoint reads; out of
  M26's blast radius and recorded as an M27+ follow-up.
- **`cli.md` documented a `--json` key that does not exist.** Four places said
  a scope selecting nothing stays visible as `"selected": []` in the record.
  The top-level key set is **closed** and has no `selected` key — the miss is
  every candidate's `"selected": false`, so `record["selected"]` is a
  `KeyError` for the agent this reference is written for. The Step-2 audit
  checked the schema block and missed the prose. All four sites reworded, plus
  two more in this log.
- **`cli.md`'s second (per-verb) exit-code table had drifted from the first.**
  It still said "empty or comment-only `--cascade-only`" (no negated), still
  listed "archive-dir creation failure" (deleted in Phase 7), and never
  mentioned the unreadable member. Brought into step, with the new outside-root
  row added to **both** tables.

### Nits

- **The pre-flight does not prove the document "parses".**
  `parse_metadata_block` raises only on a missing H1, so a member with an H1
  but a missing or out-of-vocabulary `Lifecycle:` slips past and is caught by
  the whole-tree walk — same exit 1, same zero mutation, less actionable
  message. `cli.md`'s bullet is **reworded to the narrower truth**; promoting
  the proof to `parse()` is recorded as follow-up 1 in the milestone doc.
- **A preview can never warn about a pre-flight failure** (check order exits
  the preview at step 5, the pre-flight is step 7). Per contract; recorded as
  follow-up 2, not implemented.
- **A no-slash `--cascade-only` matches the FINAL segment, not "any segment at
  any depth"** — the compiled regex is `$`-anchored, so `'sub'` selects nothing
  while `'sub/'` selects `sub/child.md`. Safe failure mode, misleading wording;
  `cli.md` and the mirror now say so and name the two working spellings.
- **`docs/plan.md`'s M26 row conflated the Phase-8 gate with the audit's
  extra lock** ("889 … 114 new"; 774 + 114 = 888). Corrected — see *Counts*
  below.
- **Alias rewriting can leave duplicate `Related:` bullets.** Reproduced: a
  primary declaring both `beta.md` and `./beta.md` yields one pair per spelling
  (Phase-1 Q5) and both bullets repoint to the same new path. The fix is **not
  local** — the duplicate exists because two different `old_rel`s map to one
  `new_rel`, so suppressing it needs `Related:`-block-aware editing rather than
  `rewrite_related_refs`' per-pair exact-match substitution, and dropping the
  alias pair instead would leave the `./` bullet **dangling**, which is
  strictly worse than a cosmetic duplicate. Taken as the recorded-follow-up
  branch: milestone follow-up 3 (M28's natural home) plus
  `test_two_spellings_of_one_edge_survive_the_rewrite_as_duplicate_bullets`
  documenting today's behaviour so it cannot change silently either way.

### The four surfaced items, decided

- **(a) The unparseable-primary refusal keeps its bare `docs: <exc>` prefix.**
  Agreed — but the *reason recorded here was wrong*. "Unpinned by a test, so
  leave it" is **not** this milestone's precedent: Phase-1 Q15/Q16 deliberately
  moved other unpinned legacy strings to the new form. The right reason is
  **cross-verb consistency**: the bare form is shared with the whole-tree-walk
  message and with `mv` / `touch`, so changing archive alone would trade one
  inconsistency for another.
- **(b) `--reason ""` — one-line fix taken.** Not the refusal (that would add
  to the frozen catalog; left as an M29 nit), but `reason=args.reason or None`
  where the plan is built. `_archive_one`'s `if reason:` has always declined to
  write an empty `Archived-reason:`, so a record carrying `""` **misdescribed
  the file it reports on** — the one failure mode D7 exists to prevent. Pinned
  by `test_empty_reason_is_dropped_from_the_record`.
- **(c) The three remaining copies of the archived-rel idiom stay.** Agreed:
  out of blast radius, and the two that were collapsed are exactly the two the
  helper's docstring cites.
- **(d) No scope creep, no unmet deliverable or success criterion**, each
  checked against the built code by the reviewer.

### Counts after the fold-in

```
.venv/bin/python -m pytest -q   →  895 passed
pre-existing ids at 37d7f1a                  777
  deliberately removed (the same three)        3
  carried over, re-run as an explicit list   774  →  774 passed
  new                                        121  →  774 + 121 = 895
```

Checkpoints, so no single number is quoted out of context: **888** at the
Phase-8 gate (114 new), **889** after the audit's failure-path lock (115), and
**895** after this fold-in's six (121) — two outside-root locks, two unreadable
-file locks, the empty-`--reason` lock, and the duplicate-bullet documentation
test.

## Milestone completion summary

**M26 — Safe explicit archive selection is implementation-complete
(2026-08-13).** All ten TDD phases done: Phases 1–4 on `m26/phases-1-4`,
Phases 5–10 on `m26/phases-5-10`. The milestone stays `Lifecycle: active`
until the M29 publish closeout.

### What shipped

Relationship verbs now supply the archive **candidate set** and never grant
**authorization**. Exactly three shapes write, and no other invocation
writes a related document:

| Invocation | Writes | Exit |
|---|---|---|
| `docs archive FILE` | `FILE` only | 0 |
| `docs archive FILE --cascade-dry-run [--cascade-only GLOB]` | nothing (preview) | 0 |
| `docs archive FILE --cascade-only GLOB` | `FILE` plus exactly the one-hop candidates matching `GLOB` | 0 |

- **Bare `--cascade` and `--interactive` are retired** and refuse
  unconditionally at exit 2, before any filesystem access, naming the
  replacement invocation. Both stay registered so an obsolete script gets a
  legible refusal rather than `unrecognized arguments`. Retiring
  `--interactive` removed the verb's last stdin read: `docs archive` now
  never prompts on stdin at all, under any flag combination.
- **The preview names the whole neighborhood** — every one-hop candidate
  marked selected, not selected, or ineligible — writes nothing, and exits 0
  even when the scope selects nothing.
- **A scoped write is one complete plan, validated first**: deduplicated on
  the canonical root-relative path, destination-collision checked,
  writability checked with an explicit access test, already-archived
  candidates excluded and an already-archived primary refused, an empty
  selection refused with two distinguishable messages. Every handled failure
  refuses with **zero bytes written**, the primary included.
- **`docs archive --json`** emits one operation-plan record, identical in
  shape for a preview and a real apply.

### Evidence against the five reproduced defects

| Evidence | Before (1.8.0) | After |
|---|---|---|
| **E1** over-cascade | bare `--cascade` would sweep this project's whole specification spine into the archive, no prompt | refuses at exit 2; the preview names all six candidates and authorizes none — verified on the live tree shape in Phase 9 |
| **E2** duplicate edge | archived once, then a false `could not archive b.md: [Errno 2]` line | one candidate, first declaration winning the verb, every declared spelling kept as an alias so the edge rewrite still lands |
| **E3** basename collision | one doc silently dropped, exit **0**, `docs check` clean afterwards | refused before any write, naming both sources, exit 2 |
| **E4** archived neighbour | silently relocated and re-dated — data corruption | excluded and named ineligible; its bytes stay put, while M18's one move-driven bullet is still repointed and `docs check` stays clean |
| **E5** typo'd scope | archived the primary, exit **0** | refused at exit 2, primary not archived, "matched none of the N" distinguished from "no candidates at all" |

### Numbers

- **895 tests, all passing.** 774 of the 777 pre-existing ids mechanically
  proven present and GREEN (re-run as an explicit id list), 3 deliberately
  removed, 121 new. Checkpoints: 888 at the Phase-8 gate, 889 after the
  audit's lock, 895 after the review fold-in's six.
- `ruff` / `ruff format` / `mypy src/ tests/` / `docs check --root docs`
  clean; bundled `references/cli.md` and `references/convention.md`
  byte-identical to the specs; the INDEX snapshot in sync.
- **No version bump.** `pyproject.toml` stays `1.8.0`; CHANGELOG entries
  accumulate under `UNRELEASED`.

### Deliberate deviations, all logged

1. `CoordinatedWriteError` gained a keyword-only `exit_code` (Phase 5) — the
   only way a `preflight_archive_plan(plan) -> None` can carry the Q4 split.
2. `_print_archive_lines` gained a keyword-only `cascade` (Phase 7) — the
   plan cannot distinguish `--cascade-dry-run` with no scope from a plain
   `--dry-run`, and D1's quiet rule needs that bit.
3. A blank / comment-only / negated `--cascade-only` refuses in **every**
   mode, a preview included (conductor-resolved); `cli.md` now states the
   carve-out and two tests gained a `preview` parametrization.
4. One Step-1 test helper was defective — `_two_relation_tree` mkdir'd
   without `parents=True`, making
   `test_archive_help_still_registers_the_retired_flags` unsatisfiable by any
   implementation. Fixed in its own labelled commit; no assertion changed.

Both signature deviations are recorded in the milestone doc's *Step-2
amendments to the frozen signatures*, so the contract and the code agree.

### Handoff

M27 — Markdown body-link validation is ready to prepare. M28 reuses this
milestone's move planning for body-link rebasing, and M29 publishes the
whole v2.0 train.
