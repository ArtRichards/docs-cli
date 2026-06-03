# M18 — Implementation Log

Lifecycle: draft
Role: log
Project: docs
Updated: 2026-06-03

Related:
- child-of: m18-archive-edge-integrity.md
- pairs-with: m18-archive-edge-integrity.md
- pairs-with: status.md

## Overview

Chronological log of work on M18 — Archive edge integrity (intra-archive
`Related:` rewriting). Append a section per TDD phase with objective, files
changed, actions, test results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M18 — Archive edge integrity (intra-archive Related: rewriting)
- Started: 2026-06-03 (scaffolded)
- Progress: **Milestone pair scaffolded 2026-06-03.** Files the
  archive-edge-integrity bug confirmed empirically this session: archiving
  interrelated docs into the archive subtree orphans `Related:` edges
  because (1) `_archive_one` never rewrites the moved doc's OWN outgoing
  edges and (2) `_rewrite_referring_edges` deliberately skips already-archived
  referrers (the pinned `test_archive_does_not_rewrite_archive_subtree_edges`).
  Both legs reproduced on copies of the live `docs/` tree → `docs check`
  exit 2. Scope is a correctness fix to archive (and pending Open Q1, `mv`):
  rewrite the moved doc's own archive-subtree edges + repoint already-archived
  referrers, deliberately flipping the pinned test. Depends on nothing;
  unblocks the completed-milestone archival backlog (currently DEFERRED in
  the live tree). Phase 1 (Define Contract) opens via
  `/ship-milestone M18`.

(Note: doc-lifecycle status is the front-matter `Lifecycle:` field. This
section tracks implementation progress, which is distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Done | 2026-06-03 | `cli.md` §archive M18 block (own-edge D1 + already-archived-referrer D2; "targets that moved" = the batch `moves`, rewrite iff target == an `old_rel`; narrowed read-only boundary, Q4); §mv own-edge delta (D3 INCLUDED, Q1=operator); `convention.md` archive-subtree-edge note. No new exit codes (GREEN-path). Bundled refs resynced byte-identical (`test_skill_refs` GREEN). `Updated:` bumped on cli/convention/milestone via `docs touch`; that auto-refreshed `docs/INDEX.md` (convention date 06-02→06-03), so the frozen snapshot `tests/fixtures/expected/docs-INDEX.md` was kept in lockstep (Q6: snapshot RED is a fixture-sync chore, fixed immediately — INDEX+snapshot both at 06-03). Milestone Decisions updated: Q1-Q6 recorded BINDING; D3 reworded INCLUDED. Full suite GREEN (505). |
| 2. Write Tests (RED) | Not started | — | Pair-archival both-directions-clean; sweep-beside-already-archived-referrer repoint (the FLIPPED `test_archive_does_not_rewrite_archive_subtree_edges`); `--cascade` pair/trio edge-clean; backlog-shaped acceptance; (if D3) `mv` own-edge. |
| 3. Create Data/Fixtures | Not started | — | Trees with a plan/log pair + an already-archived referrer + a trio mirroring the real backlog shape, under `tests/fixtures/`. |
| 4. Run Tests (RED Baseline) | Not started | — | Confirm + classify the intended red baseline (broken-ref / un-rewritten edge; no tracebacks); classify the flipped test. |
| 5. Update Base Interfaces | Not started | — | Declare the shared archive-subtree-edge rewrite helper; thread into `_archive_one`'s caller (+ `mv` if D3). No core logic. |
| 6. Implement Offline/Core Path | Not started | — | Own-edge rewrite (D1) + already-archived referrer repoint (D2) + (if D3) `mv` parity. All RED → GREEN. |
| 7. Update Tool/Wrapper Layer | Not started | — | CHANGELOG (Open Q2); SKILL.md / `create-milestones` pair-archival guidance if it changes; bundled refs byte-identical. |
| 8. Run Tests (GREEN) | Not started | — | Full suite GREEN; ruff / format / mypy / `docs check docs/` / index dry-run clean; bundled refs byte-identical. |
| 9. Implement Online/Integration | Not started | — | Dogfood on copies, then run the completed-milestone archival backlog on the REAL `docs/` tree (the payoff) — `docs check docs/` exit 0, M14/M15 left live. |
| 10. Quality, Docs, Refactor | Not started | — | Closeout summaries; INDEX + frozen snapshot lockstep; status/plan updated; simplify pass. |

## Provenance — where the scope came from

The bug was confirmed empirically and RE-VERIFIED on 2026-06-03 on throwaway
copies of the live `docs/` tree (the M1 plan↔log pair):

- **Leg (1) — moved docs' OWN edges (pair archived in ONE op).**
  `docs archive m1-parser-and-index-log.md --cascade-only "m1-parser-and-index.md"`
  (log→plan is `child-of`) moved BOTH into `archive/2026-05-20/` and left
  BOTH own edges as bare basenames — the plan's `parent-of: …-log.md` and the
  log's `child-of: …-index.md` → two broken-refs, `docs check` exit 2.
- **Leg (2) — already-archived referrer (two-step).** Archiving the M1 plan
  SOLO is clean (`docs check` exit 0; the live log's `child-of` is repointed
  to the plan's archive path DURING that op, and the archived plan's
  `parent-of: …-log.md` still resolves while the log is live). Sweeping the
  log in afterward then leaves the now-archived PLAN's `parent-of: …-log.md`
  dangling — the second op's rewriter skips the already-archived plan
  (`_rewrite_referring_edges`: `if doc.archived: continue`) → `docs check`
  exit 2 on that one edge.
- **Adjacent (NOT a leg; Open Q3).** `docs archive m1-parser-and-index.md
  --cascade` does NOT pull the log (`parent-of` ∉ `_CASCADE_VERBS`); it
  sweeps the plan's `pairs-with` specs (convention.md / cli.md /
  architecture.md / test-strategy.md) + `child-of: plan.md` into the archive
  — the over-archival concern, separate from the edge-integrity legs.

Code anchors: `_archive_one` (cli.py:3595 — sets metadata + moves, no own-edge
rewrite); `_rewrite_referring_edges` (cli.py:4000, `if doc.archived: continue`
at 4017); the `broken-ref` root-relative resolution (cli.py:1586); `_cmd_mv`
(cli.py:3803 — walks all docs incl. archived for referrers, but no own-edge
rewrite); the pinned `tests/test_cli_archive.py::test_archive_does_not_rewrite_
archive_subtree_edges` (~line 606).

See [m18-archive-edge-integrity.md](m18-archive-edge-integrity.md) Decisions
+ OPEN QUESTIONS for the full analysis and the contract-change-flips-a-pinned-test
note.
