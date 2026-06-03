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
  exit 2. Scope is a correctness fix to archive (and `mv` — Open Q1 RESOLVED
  INCLUDED, operator): rewrite the moved doc's own archive-subtree edges +
  repoint already-archived referrers, deliberately flipping the pinned test.
  (Phase 2 finding: the `mv` own-edge leg is already satisfied by existing
  code — see the Phase-2 table row.) Depends on nothing;
  unblocks the completed-milestone archival backlog (currently DEFERRED in
  the live tree). Phase 1 (Define Contract) opens via
  `/ship-milestone M18`.

(Note: doc-lifecycle status is the front-matter `Lifecycle:` field. This
section tracks implementation progress, which is distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Done | 2026-06-03 | `cli.md` §archive M18 block (own-edge D1 + already-archived-referrer D2; "targets that moved" = the batch `moves`, rewrite iff target == an `old_rel`; narrowed read-only boundary, Q4); §mv own-edge delta (D3 INCLUDED, Q1=operator); `convention.md` archive-subtree-edge note. No new exit codes (GREEN-path). Bundled refs resynced byte-identical (`test_skill_refs` GREEN). `Updated:` bumped on cli/convention/milestone via `docs touch`; that auto-refreshed `docs/INDEX.md` (convention date 06-02→06-03), so the frozen snapshot `tests/fixtures/expected/docs-INDEX.md` was kept in lockstep (Q6: snapshot RED is a fixture-sync chore, fixed immediately — INDEX+snapshot both at 06-03). Milestone Decisions updated: Q1-Q6 recorded BINDING; D3 reworded INCLUDED. Full suite GREEN (505). |
| 2. Write Tests (RED) | Done | 2026-06-03 | Authored 5 archive tests + 1 mv test. Archive: #1 `test_archive_cascade_rewrites_moved_docs_own_edges` (D1 leg-1, RED); #2 `test_archive_pair_leaves_check_clean` (D1 via check gate, needs archive-pair fixture); #3 `test_archive_repoints_already_archived_referrer` (FLIPPED replacement; DELETED old `test_archive_does_not_rewrite_archive_subtree_edges`, RED); #4 `test_archive_leaves_unrelated_archived_content_byte_identical` (Q4 boundary, GREEN lock); #5 `test_archive_cascade_trio_lands_edge_clean` (needs archive-trio fixture). mv: #6 `test_mv_rewrites_moved_docs_own_archive_edge`. **Scope finding (SURFACED):** #6 is GREEN at baseline, NOT red — `_cmd_mv` already walks the whole tree post-move and applies `rewrite_related_refs(old_rel,new_rel)` to the moved doc itself, so a single-move own-edge (only ever the self-edge) is already repointed. mv has no `--cascade`, so no multi-move own-edge gap exists; D3 is already satisfied by existing code (Phase 6 expects NO mv code change, only this regression lock). Verified empirically (3 scratch trees). Without fixtures: #1,#3 RED (clean assertion), #4,#6 GREEN. |
| 3. Create Data/Fixtures | Done | 2026-06-03 | Added `tests/fixtures/trees/archive-pair/` (plan `feature.md` role milestone `parent-of: feature-log.md`; log `feature-log.md` role log `child-of`+`pairs-with: feature.md` — real M1 plan↔log shape; used by #2) and `tests/fixtures/trees/archive-trio/` (plan `feature.md` `pairs-with` impl + test-matrix; children back-edge `pairs-with: feature.md` — m16-* trio shape; used by #5). Both pass `docs check` clean pre-archive (exit 0). #1/#3/#4 reuse `archive-with-incoming-refs`/`cross-refs` + inline trees; #6 inline. With fixtures present, #2/#5 now RED for the right reason (#2: archive op exit 0 + cascade pulls the plan, but post-archive `docs check` exit 2 with broken-ref on un-rewritten intra-pair edges; #5: bare `pairs-with: feature-impl.md` un-rewritten) — clean assertion fails, no tracebacks. |
| 4. Run Tests (RED Baseline) | Done | 2026-06-03 | Full suite: **4 failed, 506 passed** (510 total = 505 pre-M18 + 6 new − 1 deleted). The 4 fails are exactly the intended archive behaviour reds — all clean `AssertionError`s (0 tracebacks / argparse-exit-2 / collection errors, grep-verified). Classification: #1 `…_moved_docs_own_edges` RED (own edges bare); #2 `…pair_leaves_check_clean` RED (archive exit 0 + cascade pulls plan, but post-archive `docs check` exit 2 broken-ref); #3 `…repoints_already_archived_referrer` RED (flipped; archived referrer skipped at cli.py:4017); #5 `…cascade_trio_lands_edge_clean` RED (trio own edges bare + check exit 2); #4 `…unrelated_archived_content_byte_identical` **GREEN** (Q4 regression lock); #6 `test_mv_rewrites_moved_docs_own_archive_edge` **GREEN** (deviates from plan's "RED today" — D3 already satisfied; see scope finding in Phase 2 / surfaced to operator). Deleted `test_archive_does_not_rewrite_archive_subtree_edges` does not appear as a failure (removed; name survives only in #3's docstring per plan). Collection delta +5/−1 confirmed (archive 26→30 fns, mv 11→12 fns). |
| 5. Update Base Interfaces | Done | 2026-06-03 | `_rewrite_referring_edges`: added the binding `old_rels = {old for old, _new in moves}` after the `if not moves: return` guard and rewrote the docstring for the M18 D2/Q4 contract (archived docs skipped EXCEPT when a `Related:` target == a batch `old_rel` → that edge repointed). LEFT the `if doc.archived: continue` skip UNCONDITIONAL — interface declared, behaviour unchanged. Suite still 4 red / 506 pass (honest phase split, Q-F; the flip is phase 6). No reuse of `_archive_one`'s caller signature change needed — `moves` already carried the full batch; the gate threads through the existing `moves` arg. |
| 6. Implement Offline/Core Path | Done | 2026-06-03 | Flipped the skip to `if doc.archived and not any(target in old_rels for _verb, target in doc.related): continue`. After `_archive_one` moves docs into `archive/<date>/`, the post-move walk yields them archived with bare own-edges whose targets ∈ `old_rels` → repointed (D1 leg-1 + leg-2); already-archived referrers whose target sweeps in → repointed (D2). Greened #1/#2/#3/#5 simultaneously; #4/#6 stayed GREEN. **Strengthened #4** (`test_archive_leaves_unrelated_archived_content_byte_identical`): added a SECOND pre-archived bystander `mover-ref.md` in a DIFFERENT date (`archive/2026-03-01/`) whose edge target IS the moving `core.md`; assert that edge IS repointed to `archive/2026-05-28/core.md` while the first bystander (edge → non-moving `helper.md`) stays byte-identical. **Q4 boundary finding (recorded):** the `old_rels` gate and an unconditional "walk all archived" produce BYTE-IDENTICAL output — `rewrite_related_refs` is target-exact, so the matcher (not the gate) is the edge-level boundary guard; the gate is an intent/efficiency screen. Verified empirically: under-broad (unconditional skip) → #4 FAILS (mover-ref edge dangles); over-broad (no skip) → #4 GREEN (matcher target-exact). The byte-identity bystander catches over-broad fixes that escape the matcher (prose/arbitrary content). No `mv` code change (D3 already satisfied; #6 regression-locks it). Full suite **510 passed / 0 failed**; ruff/format/mypy/`docs check` clean. |
| 7. Update Tool/Wrapper Layer | Done | 2026-06-03 | CHANGELOG (Q2): one Fixed bullet appended to the open `## 1.6.0 — UNRELEASED` `### Fixed` subsection — archiving interrelated docs no longer orphans `Related:` edges; own intra-archive edges + already-archived referrers repointed; narrows M3 read-only to move-driven rewrites only; `docs mv` already carried this. No version bump (M17 ships 1.6.0). cli.md / convention.md NOT re-edited (already carry the full contract from phase 1; byte-identical to bundled mirrors — `diff -q` IDENTICAL, `test_skill_refs` GREEN). No external-skill edit (Q-E). CHANGELOG touches no docs/ metadata → INDEX unchanged here. |
| 8. Run Tests (GREEN) | Done | 2026-06-03 | Full Phase-8 gate BEFORE the integration mutation: pytest **510 passed / 0 failed**; `ruff check` clean; `ruff format --check` clean (39 files); `mypy` clean (40 files); `docs check docs/` exit 0 (tree still pre-archival); `docs index --root docs/ --dry-run` exit 0; bundled cli.md / convention.md byte-identical; `docs/INDEX.md` == frozen snapshot. No code change this phase — this log row + status are the commit. All phase 5-8 work committed before Leg B so `git restore docs/ && git clean -fd docs/` is a clean rollback boundary. |
| 9. Implement Online/Integration | Not started | — | Dogfood on copies, then run the completed-milestone archival backlog on the REAL `docs/` tree (the payoff) — `docs check docs/` exit 0, M14/M15 left live. |
| 10. Quality, Docs, Refactor | Not started | — | Closeout summaries; INDEX + frozen snapshot lockstep; status/plan updated; simplify pass. |

## Carry-forward to Phase 6

- **Strengthen the Q4 boundary lock.** `test_archive_leaves_unrelated_
  archived_content_byte_identical` (#4) currently guards prose/`Updated:`/
  byte-identity for a bystander whose edge points at a NON-moving target, so
  it does not actually exercise the edge-level boundary "rewrite an edge
  ONLY when its target equals a batch `old_rel`." Phase 6: add a SECOND
  pre-archived bystander whose edge target IS a batch `old_rel` reached via
  a DIFFERENT archive date, and assert it is rewritten ONLY when the target
  genuinely equals a batch `old_rel` (i.e. an over-broad fix that rewrote
  edges to non-moving targets would fail). This closes the gap the current
  #4 leaves open.

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
