# M26 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-08-12

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
- Progress: **Phase 1 — Define Contract complete (2026-08-12).** All seven
  setup questions were RESOLVED before Phase 1 (Q1/Q5/Q6 by the operator;
  Q2/Q3/Q4/Q7 conductor-resolved) and Phase 1 did not re-open them; it froze
  the exact surface against them, plus the seventeen Step-1 planning
  questions. Phase 2 — Write Tests (RED) is next.
- Source: the operator-confirmed cascade-safety decision in `feedback-log.md`
  (2026-08-09/10) and the M26 registration in `plan.md` (2026-08-10).
- Branch: `m26/milestone-setup` for setup; `m26/phases-1-4` for Step 1
  (Phases 1–4).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | **Done** | 2026-08-12 | Froze the compatibility matrix, the message catalog (refusals, preview/apply lines, partial-state admission), the exit-code split, the `--json` schema and field table, and the Phase-5 signatures. Seventeen Step-1 planning questions recorded as BINDING. No `cli.py` edit (logged deviation). |
| 2. Write Tests (RED) | Pending | — | E1–E5 regression locks, refusals (bare cascade, `--interactive`, archived primary), preview, scoped write, `--json` preview/apply shape identity, and failure-path locks. |
| 3. Create Data/Fixtures | Pending | — | One-semantic-per-tree candidate (E1), duplicate (E2), collision (E3), and archived-neighbour (E4) trees. |
| 4. Run Tests (RED Baseline) | Pending | — | Capture the classified failure set; prove no unrelated regression. |
| 5. Update Base Interfaces | Pending | — | Archive plan/move models, candidate-planning helpers, pre-flight validators, `archive_plan_to_json`; no behaviour change. |
| 6. Implement Offline/Core Path | Pending | — | Validate-all-first planning, deduplication, archived exclusion, collision detection, safe refusal, partial-state admission. |
| 7. Update Tool/Wrapper Layer | Pending | — | argparse surface (refusing flags + local `--json`), human output, JSON record, docs, bundled skill, CHANGELOG (no version bump). |
| 8. Run Tests (GREEN) | Pending | — | Full product and quality gates with exact counts. |
| 9. Integrate / Accept / Dogfood | Pending | — | Preview + scoped archive of a real milestone pair on a throwaway tree copy. |
| 10. Quality, Docs, Refactor | Pending | — | Simplify, close docs, completion summaries, hand off to M27. |

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
  rule explicitly with the `matched none` line and `"selected": []` named. The
  compatibility matrix has a dedicated row for the case.
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
  carries `"selected": []` for the machine consumer. Refusals, by contrast,
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


## Milestone completion summary

_Not complete._
