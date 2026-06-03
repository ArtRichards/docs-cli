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
| 1. Define Contract | Not started | — | `cli.md` §archive deltas (own-edge rewrite D1 + already-archived-referrer repoint D2); "targets that moved" set under single vs `--cascade`; the D3 `mv` decision (Open Q1); `convention.md` archive-subtree-edge note; bundled refs resynced byte-identical. |
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

The bug was confirmed empirically on 2026-06-03 (this scaffolding session)
on throwaway copies of the live `docs/` tree:

- **Leg (1) — moved doc's OWN edge.** `docs archive m1-parser-and-index.md
  --cascade` archived the plan with its own `parent-of:
  m1-parser-and-index-log.md` edge left as a bare basename →
  `docs check` exit 2 (broken-ref). The same run also swept the ACTIVE
  specs (convention.md / cli.md / architecture.md / test-strategy.md) and
  plan.md into the archive — the over-archival concern (Open Q3).
- **Leg (2) — already-archived referrer.** Archiving the M1 plan SOLO left
  `docs check` clean (the live log's edge still resolved); sweeping the log
  into the same dated folder afterward left the now-archived PLAN's
  `parent-of: m1-parser-and-index-log.md` edge dangling (`_rewrite_referring_edges`
  skips archived docs) → `docs check` exit 2.

Code anchors: `_archive_one` (cli.py:3595 — sets metadata + moves, no own-edge
rewrite); `_rewrite_referring_edges` (cli.py:4000, `if doc.archived: continue`
at 4017); the `broken-ref` root-relative resolution (cli.py:1586); `_cmd_mv`
(cli.py:3803 — walks all docs incl. archived for referrers, but no own-edge
rewrite); the pinned `tests/test_cli_archive.py::test_archive_does_not_rewrite_
archive_subtree_edges` (~line 606).

See [m18-archive-edge-integrity.md](m18-archive-edge-integrity.md) Decisions
+ OPEN QUESTIONS for the full analysis and the contract-change-flips-a-pinned-test
note.
