# M18 — Archive edge integrity (intra-archive Related: rewriting)

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-06-03

Related:
- child-of: plan.md
- parent-of: m18-archive-edge-integrity-impl.md
- pairs-with: m18-archive-edge-integrity-impl.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: status.md

## Overview

- Milestone: M18
- Title: Archive edge integrity (intra-archive Related: rewriting)
- Surface: a correctness fix to `docs archive` (and, pending an Open Q,
  `docs mv`) so that archiving interrelated docs into the archive subtree
  does not orphan their `Related:` edges. Two legs: (a) the moved doc's OWN
  outgoing edges that point at docs which now live under `archive/` are
  rewritten to their root-relative archive paths; (b) ALREADY-archived
  referrers are repointed when a doc they reference moves into the archive.
  No new verb, no publish — a behaviour fix to existing archive machinery.
  Headline acceptance: after the fix, archiving the completed-milestone
  backlog (M1–M9 + M12 plan/log pairs, the M16 trio, the three stray
  impl-logs) leaves `docs check docs/` clean.
- Progress: Draft (scaffolded 2026-06-03 from the empirically-confirmed
  archive edge-integrity bug — see Decisions). Depends on nothing; unblocks
  the completed-milestone archival backlog that is currently DEFERRED in the
  live tree pending this fix.

### Goal

`docs archive` already keeps the index and the *referring* edges of LIVE
docs consistent with a move (M12 — `_rewrite_referring_edges`). But two edge
classes are left dangling when interrelated docs are archived, and both now
produce `broken-ref` errors → `docs check` exit 2:

1. **The moved doc's OWN outgoing edges.** `_archive_one` (cli.py:3595) sets
   `Lifecycle: archived` / `Updated:` / `Archived-reason:` and moves the file
   — but never rewrites the moved doc's own `Related:` bullets. A `Related:`
   edge is a bare basename validated ROOT-RELATIVE (`root / target`,
   cli.py:1586). So when a milestone PLAN and its LOG are archived together
   into the same `archive/<date>/` folder, the plan's
   `parent-of: <slug>-log.md` edge still resolves as `root/<slug>-log.md`,
   which no longer exists — the plan↔log edge is orphaned.

2. **Already-archived referrers.** `_rewrite_referring_edges` (cli.py:4000)
   walks live docs and rewrites edges pointing AT the archived doc, but
   DELIBERATELY skips already-archived docs (`if doc.archived: continue`,
   cli.py:4017) — a behaviour PINNED by
   `tests/test_cli_archive.py::test_archive_does_not_rewrite_archive_subtree_edges`
   (~line 606). So when a doc that an already-archived doc points to is
   itself moved into the archive (e.g. sweeping a stray impl-log in beside
   its already-archived plan), the already-archived referrer's edge dangles.

This was never hit before because the only prior archivals (M10/M11/M13)
archived the PLAN solo and left the impl-log LIVE — neither leg fires when
exactly one doc of a related set is in the archive and the other is live at
the root. The moment a related PAIR (or a doc + an already-archived
neighbour) lands in the archive subtree, the edges break. It also means
`create-milestones`' advertised `docs archive --cascade` pair-archival
(SKILL.md completion checklist) hits leg (1) directly.

M18 makes archive-subtree edges first-class: archiving a doc rewrites BOTH
its own outgoing archive-subtree edges AND any already-archived referrers'
edges to it, mirroring how live referring edges are already rewritten. This
**deliberately revisits and flips** the contract pinned by
`test_archive_does_not_rewrite_archive_subtree_edges` (see Decisions).

### Scope — archive edge integrity

- **D1 — rewrite the moved doc's OWN archive-subtree edges.** When
  `_archive_one` moves doc X into `archive/<date>/`, rewrite X's own
  `Related:` bullets whose target now resolves under the archive subtree to
  the correct root-relative archive path. The set of "targets that moved" is
  exactly the batch of moves the archive op is performing (single archive:
  `{X}`; `--cascade`: X + every cascaded relation), composed with any docs
  ALREADY under `archive/`. The rewrite must compose with `--cascade` so a
  whole pair/trio archived in one call lands with every intra-archive edge
  pointing at the new paths. Exact contract → Phase 1.
- **D2 — repoint already-archived referrers.** When a doc moves into the
  archive, walk the archive subtree too and rewrite already-archived docs'
  `Related:` edges that pointed at the now-moved doc (the leg
  `_rewrite_referring_edges` skips today). This **flips** the pinned
  `test_archive_does_not_rewrite_archive_subtree_edges` expectation: an
  archived referrer's edge to a doc that moves into the archive SHOULD be
  rewritten (the old test asserted it must NOT be). The flip is deliberate
  and is the headline contract change — recorded in Decisions, re-pinned by
  an updated/replacement test in Phase 2.
- **D3 — `docs mv` parity (pending Open Q1).** `_cmd_mv` (cli.py:3803) walks
  ALL docs (it does NOT carry the `if doc.archived: continue` skip the
  cascade rewriter has), so it already rewrites archived referrers when a
  doc is `mv`'d — but, like archive, it never rewrites the MOVED doc's own
  outgoing edges. Decide (Open Q1) whether `mv` needs the same own-edge
  rewrite as archive's D1, and whether the two share one helper. The
  archive-subtree-rewrite machinery D1 introduces should be reusable by
  `mv` without a second implementation.
- **D4 — `cli.md` / `convention.md` + bundled-ref docs.** Document the new
  archive edge-integrity behaviour in `cli.md` §archive (and §mv if D3
  lands), note the convention that archive-subtree `Related:` edges are now
  maintained across moves in `convention.md`, refresh the bundled skill
  references byte-identical (M14 C1: `docs/` is canonical), and — if the
  pair-archival guidance changes — touch the `create-milestones` skill
  expectations. The byte-identity invariant (`tests/test_skill_refs.py`)
  holds throughout.

## Deliverables

- [ ] D1 `_archive_one` (or its caller) rewrites the moved doc's OWN
      `Related:` edges that point at archive-subtree targets to their
      root-relative archive paths; composes with `--cascade` so a whole
      pair/trio lands edge-clean.
- [ ] D2 already-archived referrers are repointed when a doc they reference
      moves into the archive; the pinned
      `test_archive_does_not_rewrite_archive_subtree_edges` expectation is
      flipped (re-pinned by an updated/replacement test).
- [ ] D3 `docs mv` own-edge / archive-referrer parity decided (Open Q1) and,
      if in scope, implemented via the shared D1 machinery.
- [ ] D4 `cli.md` §archive (+ §mv) + `convention.md` document the new
      behaviour; bundled skill refs resynced byte-identical; INDEX + frozen
      snapshot in lockstep.
- [ ] Phase 9 integrate/dogfood payoff: archive the completed-milestone
      backlog (M1–M9 + M12 pairs → `archive/<completion-date>/`; the M16
      trio → `archive/2026-06-01`; the three stray impl-logs swept into their
      plans' existing folders — m10/m11 → `archive/2026-05-27`, m13 →
      `archive/2026-05-29`) and confirm `docs check docs/` exit 0.
- [ ] Full suite GREEN; ruff / ruff format / mypy / `docs check` clean
      tree-wide; bundled cli.md / convention.md byte-identical.

## Phase Checklist (10-phase TDD)

- [ ] 1. Define Contract — `cli.md` §archive deltas for the own-edge rewrite
      (D1) + already-archived-referrer repoint (D2); the precise "targets
      that moved" set under single vs `--cascade` archive; exit-code rows;
      the D3 `mv` decision (Open Q1); `convention.md` archive-subtree-edge
      note; bundled refs resynced byte-identical.
- [ ] 2. Write Tests (RED) — pair-archival leaves both directions clean
      (plan's own `parent-of: …-log.md` → archive path; log's `child-of`);
      sweep-a-doc-in-beside-an-already-archived-referrer repoints the
      archived referrer (the FLIPPED case replacing/superseding
      `test_archive_does_not_rewrite_archive_subtree_edges`); `--cascade`
      pair/trio lands edge-clean; the backlog-shaped acceptance fixture;
      (if D3) the `mv` own-edge case.
- [ ] 3. Create Fixtures — small trees with a plan/log pair + an
      already-archived referrer + a trio (plan/impl/test-matrix) mirroring
      the real backlog shape, under `tests/fixtures/`.
- [ ] 4. Run Tests (RED Baseline) — confirm the intended red baseline; every
      red is "behaviour not yet implemented" (broken-ref / un-rewritten
      edge), none a traceback / collection error. Classify the flipped test.
- [ ] 5. Update Interfaces — declare the shared archive-subtree-edge rewrite
      helper signature; thread it into `_archive_one`'s caller (and `mv` if
      D3). No core logic.
- [ ] 6. Implement Core — the own-edge rewrite (D1) + the already-archived
      referrer repoint (D2) + (if D3) the `mv` parity. All RED → GREEN.
- [ ] 7. Update Wrappers — CHANGELOG entry (1.6.0 section or its successor,
      per Open Q2); SKILL.md / `create-milestones` guidance if pair-archival
      expectations change; bundled refs byte-identical.
- [ ] 8. Run Tests (GREEN) + quality gate — full suite GREEN; ruff / format /
      mypy / `docs check docs/` / index dry-run clean; bundled refs
      byte-identical.
- [ ] 9. Integrate — dogfood the fix on copies, then perform the
      completed-milestone archival backlog ON THE REAL `docs/` tree (the
      milestone payoff) and confirm `docs check docs/` exit 0 with M14/M15
      left live (await M17 publish).
- [ ] 10. Quality, Docs, Refactor — closeout summaries; INDEX + snapshot
      lockstep; status/plan updated; simplify pass.

## Decisions

- **The bug (empirically confirmed 2026-06-03; this scaffolding session).**
  Reproduced on throwaway copies of the live `docs/` tree:
  - **Leg (1) — moved doc's own edge.** `docs archive m1-parser-and-index.md
    --cascade` (cascade pulls the plan's `pairs-with` specs + `child-of:
    plan.md`) archived the plan with its own `parent-of:
    m1-parser-and-index-log.md` edge left as a bare basename → `docs check`
    exit 2 (broken-ref). (Also surfaced the over-archival concern — see
    Open Q3 — because bare `--cascade` swept the ACTIVE specs convention.md /
    cli.md / architecture.md / test-strategy.md along with plan.md.)
  - **Leg (2) — already-archived referrer.** Archiving the M1 plan SOLO
    (`docs check` clean — the live log's edge still resolves), THEN sweeping
    the log into the same dated folder, left the now-archived PLAN's
    `parent-of: m1-parser-and-index-log.md` edge dangling (the rewriter
    skips archived docs) → `docs check` exit 2. Note the log's OWN
    `child-of` edge WAS rewritten to the archive path in this second op —
    because the referring-edge rewriter walks all docs INCLUDING the
    just-swept log and repoints edges to the plan that moved in the FIRST
    op. So leg (1) bites hardest when a pair moves in ONE op (`--cascade`),
    where the moved plan's own `parent-of: …-log.md` is never rewritten.
- **Never hit before — why now.** M10/M11/M13 archived the PLAN solo and
  left the impl-log LIVE; neither leg fires while exactly one doc of a
  related set is archived and its neighbour is live at the root. The
  completed-milestone archival backlog (pairs + a trio + sweeping live
  logs in beside already-archived plans) hits both legs — which is why that
  backlog is DEFERRED pending M18 (see status.md).
- **Contract change — flips a pinned test (binding intent).**
  `tests/test_cli_archive.py::test_archive_does_not_rewrite_archive_subtree_edges`
  (~line 606) currently PINS "an already-archived referrer is read-only and
  must NOT be rewritten when its target is archived." M18 deliberately
  reverses that for the archive-into-archive case: an archived referrer
  whose target MOVES INTO the archive SHOULD be repointed to the new path
  (otherwise the edge dangles). The test is updated/replaced in Phase 2; the
  general "archive subtree is read-only by convention" stance (M3) is
  preserved for everything EXCEPT edges to docs that are themselves moving in
  the same logical archival — Phase 1 pins the exact boundary.
- **Related-target resolution is root-relative (cli.py:1586).** The
  `broken-ref` check resolves `root / target`; the fix must produce
  root-relative POSIX archive paths (e.g. `archive/2026-05-20/…-log.md`),
  matching how `_rewrite_referring_edges` + `rewrite_related_refs` already
  rewrite live referring edges. No change to the resolution rule itself.
- **No publish.** M18 is a correctness fix to existing archive machinery;
  the version/CHANGELOG handling (fold into the open 1.6.0 section vs a new
  patch line) is Open Q2. M17 still owns the PyPI publish.

## Testing / Quality Gate

The standard tree-wide gate plus the new behaviour tests:

```sh
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
.venv/bin/docs check docs/
.venv/bin/docs index --root docs/ --dry-run
```

Dogfood at Phase 9: on throwaway copies, archive a plan/log PAIR (single
`--cascade` call) and a plan/impl/test-matrix TRIO and confirm `docs check`
exit 0 with every intra-archive edge resolved; sweep a doc in beside an
already-archived referrer and confirm the referrer's edge is repointed. Then
the milestone payoff — run the completed-milestone archival backlog on the
REAL `docs/` tree and confirm `docs check docs/` exit 0, M14/M15 left live.

## Success Criteria

- [ ] Archiving a milestone plan + log together (single op, incl.
      `--cascade`) leaves every intra-archive `Related:` edge resolving to a
      file; `docs check` exit 0.
- [ ] Sweeping a doc into the archive beside an already-archived referrer
      repoints the referrer's edge (the flipped contract); `docs check`
      exit 0.
- [ ] `docs mv` parity resolved (Open Q1) and consistent with archive.
- [ ] `cli.md` / `convention.md` document the behaviour; bundled refs
      byte-identical (`tests/test_skill_refs.py` GREEN).
- [ ] The completed-milestone archival backlog (M1–M9 + M12 pairs, M16 trio,
      three stray impl-logs) is archived and `docs check docs/` exits 0,
      with M14/M15 still live.
- [ ] Full suite GREEN; quality gate clean tree-wide.

## OPEN QUESTIONS

Genuine scope/contract forks for the operator. Each: question, why it
matters, recommended answer.

- **Open Q1 — Does `docs mv` get the same own-edge rewrite (D3)?**
  *Why it matters:* `_cmd_mv` already rewrites archived referrers (it has no
  `doc.archived` skip), but — like archive — never rewrites the MOVED doc's
  own outgoing edges. A `mv` of a doc whose `Related:` target also lives
  under the archive (or moves) would orphan the moved doc's own edge, the
  same class of bug as D1. Leaving `mv` unfixed ships an inconsistent
  archive-vs-mv edge contract. *Recommendation:* YES — fix `mv` in the same
  milestone via the shared D1 helper (rewrite the moved doc's own
  archive-subtree edges), since `mv` is the general move primitive and the
  machinery is identical. Keep the test surface small (one `mv` own-edge
  case) — the risk is low because `mv` already walks all docs for referrers.

- **Open Q2 — CHANGELOG/version handling for a fix that lands after M14/M15
  but before the M17 publish.** *Why it matters:* M14 opened
  `## 1.6.0 — UNRELEASED` and M15 appended to it; M17 publishes 1.6.0. M18 is
  a correctness fix on the same unreleased train. Folding it into the open
  1.6.0 section keeps one publish; starting a new line implies a separate
  release. *Recommendation:* APPEND M18's fix to the open
  `## 1.6.0 — UNRELEASED` section (it is part of the same unpublished train
  M17 ships), with a "Fixed" bullet for archive edge integrity. Do NOT bump
  the version — M17 still publishes 1.6.0 once.

- **Open Q3 — Should plain `docs archive --cascade` be scoped/constrained
  for the pair-archival use case (adjacent, NOT decided here)?** *Why it
  matters:* bare `--cascade` takes EVERY one-hop `pairs-with`/`child-of`
  relation. For a milestone plan that includes ACTIVE specs (convention.md,
  cli.md, architecture.md, test-strategy.md) and plan.md — confirmed
  empirically in this session, where `--cascade` on the M1 plan swept all
  four active specs + plan.md. So bare `--cascade` over-archives: it would
  drag long-lived parents and active specs into the archive. M18's
  edge-integrity fix makes the *edges* survive an archival, but does not
  decide *what* should cascade. *Recommendation:* DEFER the design but
  RECORD the preferred direction — for pair/trio archival the intended path
  is `docs archive <log>.md --cascade-only "<glob>"` (or archiving the LOG,
  whose only cascade edge is `child-of: <plan>`, not the plan whose edges
  fan out to specs), NOT bare `--cascade`. Whether to additionally
  *constrain* bare `--cascade` (e.g. never pull `Lifecycle: active`
  long-lived specs/parents) is a separate, larger question worth its own
  milestone; M18 should not change `--cascade`'s set semantics, only fix the
  edges. Flag for the operator: this directly affects how the Phase 9
  backlog archival is driven (archive logs with `--cascade`, or each doc
  explicitly).

- **Open Q4 — Exact boundary of the "archive subtree is read-only"
  convention after D2.** *Why it matters:* M3 established that the archive
  subtree is read-only by convention (and `test_archive_does_not_rewrite_
  archive_subtree_edges` pinned it). D2 must rewrite SOME archived docs'
  edges (referrers whose target moves into the archive) while NOT becoming a
  general "rewrite arbitrary archived-doc content" license. *Recommendation:*
  Scope the exception narrowly to `Related:` EDGE REWRITES caused by a move
  in the SAME archive operation (or to a target that has demonstrably moved
  into the archive subtree) — never prose, never other metadata. Pin the
  boundary with a test that an archived doc's UNRELATED content/edges are
  left byte-identical. (Recommended, not decided — confirm the boundary
  wording in Phase 1.)
