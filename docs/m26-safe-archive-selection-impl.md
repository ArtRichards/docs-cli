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
- Progress: **Milestone setup complete, with all seven setup questions
  RESOLVED (Q1/Q5/Q6 by the operator; Q2/Q3/Q4/Q7 conductor-resolved).
  Phase 1 — Define Contract is next and does not re-open them.**
- Source: the operator-confirmed cascade-safety decision in `feedback-log.md`
  (2026-08-09/10) and the M26 registration in `plan.md` (2026-08-10).
- Branch: `m26/milestone-setup` for setup; implementation branches are chosen
  when Phase 1 begins.

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Pending | — | Freeze exact refusal messages/exit codes, candidate/dedup/canonicalization rules, ineligibility reasons, empty-selection messages, preview shape, pre-flight boundary + partial-state admission wording, and the `--json` record schema — against the already-resolved Q1–Q7. |
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

## Phase 1 — Define Contract

_Not started._

## Milestone completion summary

_Not complete._
