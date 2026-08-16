# M28 — Implementation Log

Lifecycle: archived
Role: log
Project: docs
Updated: 2026-08-16
Archived: 2026-08-16

Related:
- child-of: archive/2026-08-16/m28-move-safe-body-link-rewrites.md
- pairs-with: archive/2026-08-16/m28-move-safe-body-link-rewrites.md
- pairs-with: status.md
- references: feedback-log.md

## Overview

Chronological implementation log for M28 — Move-safe Markdown body-link
rewrites. Append one evidence-backed section per TDD phase; keep the progress
table and the milestone checklist synchronized.

## Implementation metadata

- Project: docs
- Milestone: M28 — Move-safe Markdown body-link rewrites
- Started: 2026-08-15 (milestone setup; no TDD phase started)
- Progress: **ALL TEN PHASES COMPLETE (2026-08-15) — M28 is
  implementation-complete.** Step 1 (Phases 1–4) landed on `m28/phases-1-4`;
  Step 2 (Phases 5–10) on `m28/phases-5-10`, taking the suite to **1341
  passed / 0 failed** (1333 at the Phase-8 gate, plus the five locks the
  Step-2 audit added and three more from the fresh-eyes fold-in) with 0 test ids removed against the pre-M28 commit, and
  proving the whole thing on nine dogfood flows over throwaway copies. See
  *Milestone completion summary* at the end of this log. The whole machine-facing contract is frozen in
  the milestone's *Decisions (Phase 1 — BINDING)* — items (A)–(M), three
  amendments to setup-frozen material, and eleven Step-1 resolutions (R1–R11)
  — with the author-facing halves in `cli.md` and `convention.md` and zero
  product-code change. The setup record below is unchanged. Milestone setup
  had resolved all seven setup questions (Q1/Q2/Q3 by the operator;
  Q4/Q5/Q6/Q7 conductor-resolved) and Phase 1 did not re-open them. Q1 **amends
  the 2026-08-15 routing entry**: setup measured that the routed strand-check
  predicate refuses this repository's own standard milestone closeout, so the
  refusal is narrowed to the `child-of` direction and everything else is
  reported instead. Q2 **supersedes the registered stub's own Open question 1
  recommendation**: the archived-referrer rewrite carries destination tokens
  only. Q3 answers `feedback-log.md` issue #1 finding 4 — `--report-links`
  declined as a design, its output adopted as a plan record on both verbs. All
  three are restated in the milestone doc's *Decisions recorded at setup
  (BINDING)*.
- Source: the operator-confirmed body-link decisions in `feedback-log.md`
  (2026-08-09/10), the M28 registration in `plan.md` (2026-08-10), and the
  2026-08-15 routing of `feedback-log.md` issue #1 finding 1 (the strand-check)
  and finding 4 (the `--report-links` scope option) into this milestone.
- Branch: `m28/milestone-setup` for setup; `m28/phases-1-4` for Step 1
  (Phases 1–4); `m28/phases-5-10` for Step 2 (Phases 5–10).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | **Complete** | 2026-08-15 | Frozen in the milestone's *Decisions (Phase 1 — BINDING)*: items (A)–(M), three amendments to setup-frozen material, eleven Step-1 resolutions (R1–R11). Author-facing halves in `cli.md` (*Move-safe body-link rewrites (M28 — D1–D7)*, the rewritten `docs mv` section, the amended archive check order, the widened `archive --json` schema, three exit tables) and `convention.md` (M18's widened exception, M27 — D6's reconciled sentence, the author-facing move guarantee). Zero product-code change. Original objective: Freeze the three-step rewrite formula and its move map, the emitted spelling / fragment / delimiter / re-encoding rules, the byte-for-byte no-op rule, the never-creates-an-escape invariant, the archived-referrer policy (destination tokens only) and its `convention.md` wording, **both** strand-check legs — leg 1's `child-of` refusal predicate and message, leg 2's report, its ordering and the lines and record keys that carry it — the pre-flight and partial-state boundary, the preview and `--json` shapes for **both** verbs (including `mv`'s new record and `archive --json`'s rewrite section and `strands` array), and the Phase-5 signatures — against the resolved Q1–Q7. |
| 2. Write Tests (RED) | **Complete** | 2026-08-15 | 182 new ids: `tests/test_move_links.py` (153, the pure seam) plus 12 `mv`, 14 `archive`, 1 `check` and 2 skill locks. Suite 1269 collected / 181 failed / 1088 passed; the 1087 pre-existing ids all present and GREEN; zero collection errors; zero deleted test lines. Original objective: Pure-planner unit tests for both move classes and every grammar form; `mv` / `archive` integration and subprocess locks; both strand-check legs — the refusal, the leg-1 over-fire lock proving a legitimate closeout completes, and the leg-2 report in prose and in `strands`; failure-injection, byte-identity, idempotence and no-op locks. |
| 3. Create Data/Fixtures | **Complete** | 2026-08-15 | Seven `movelink-*` trees authored — `-incoming`, `-moved-referrer`, `-both`, `-archived-referrer`, `-nested`, `-strand`, `-closeout` — each `docs check`-clean as committed; every existing fixture byte-identical; the two directory-derived sweeps 29→36 and 33→40; suite 1283 / 180 failed / 1103 passed. A read-only prototype census confirmed every intended plan, line numbers included. Original objective: `movelink-*` trees, one semantic each — `-incoming`, `-moved-referrer`, `-both`, `-archived-referrer`, `-nested`, `-strand`; exotic grammar as inline strings and mutation cases as inline `tmp_path` builders (the M25 rule). |
| 4. Run Tests (RED Baseline) | **Complete** | 2026-08-15 | 1332 collected / 229 failed / 1103 passed (restated after the Step-1 audit and the fresh-eyes fold-in); 0 collection errors, 0 xfail/xpass, 0 warnings; exactly two exception classes (193 `AttributeError`, 36 `AssertionError`); mechanically proven 0 removed ids, 0 deleted test lines, and exactly **one** pre-existing id RED — `test_mv_help`, strengthened by operator decision. Original objective: Classified failure set against the 1087-test baseline; every GREEN-at-baseline and transitional lock named. |
| 5. Update Base Interfaces | **Complete** | 2026-08-15 | `MOVE_STRAND_KINDS`, the four frozen records (`LinkRewrite`, `DocRewrite`, `Strand`, `MovePlan`) and the seven pure functions of item (L) landed as three pure INSERTIONS — 518 lines, zero existing lines touched, `_cmd_mv` / `_cmd_archive` byte-identical. `tests/test_move_links.py` 194/194; suite 1332 / **36 failed** / 1296 passed; the `AttributeError` class is at **0** and only `AssertionError` remains. Original objective: The rewrite record, the rewrite plan, the pure planner, the splicer, the strand predicate (leg 1), the strand report (leg 2) and the JSON serializer — no verb wired, so the CLI tests stay honestly RED at the seam. |
| 6. Implement Offline/Core Path | **Complete** | 2026-08-15 | `_cmd_mv` inverted to plan-then-move with the R9 partial-state admission; `_cmd_archive` gained steps 5b / 8b / 8c / 8d and threads each member's planned text into `_archive_one`; `_print_move_lines` added and `preview only` lifted into the verb; `_rewrite_referring_edges` **deleted** (43 lines), superseded by `apply_move_plan`. Suite **5 failed, 1327 passed** — every remaining RED is a Phase-7 item (two `_JSON_TOP_LEVEL_KEYS` ids, one re-pointed fixture, two bundled-skill locks). Original objective: Invert `_cmd_mv` to plan before it moves; fold the splices into `_rewrite_referring_edges`' single per-document write; apply the archived-referrer policy (tokens only); run **both** strand-check legs in the pre-flight **and** the preview; implement the refusal, the report and the partial-state paths. |
| 7. Update Tool/Wrapper Layer | **Complete** | 2026-08-15 | Both argparse descriptions; the two contract-mandated test expected-value updates (`_JSON_TOP_LEVEL_KEYS` +2 keys, and the primary-only record re-pointed at `_two_relation_tree` with a **new** leg-1 lock added on the tree it left); bundled `SKILL.md` + `references/use-cases.md`; `CHANGELOG.md` (three `Added`, four `Changed` incl. one BREAKING, and the three-part upgrade note naming the two re-spelled `docs mv` lines); `feedback-log.md`'s issue #1 resolution bullet. `cli.md` / `convention.md` verified rather than rewritten (Phase 1 landed them); both mirrors `cmp`-identical; `](../` still 0. Suite **1333 passed, 0 failed**. Original objective: argparse for both verbs including `mv --json` and its real `--dry-run`, human output for rewrites and for the strand report, the JSON records and field tables, `cli.md` / `convention.md` (M18's widened exception **and** the reconciliation of M27 — D6's "last one this convention grants" sentence), a dated note on `feedback-log.md`'s issue #1 entry answering findings 1 and 4, the bundled skill, `UNRELEASED` CHANGELOG and the upgrade note. No version bump. |
| 8. Run Tests (GREEN) | **Complete** | 2026-08-15 | **1333 collected, 1333 passed, 0 failed**; 0 collection errors, 0 xfail/xpass/error. Mechanically proven against `58955ef`: **0** ids removed, 246 added, and — because nothing fails — all **1087** pre-existing ids present and GREEN. `git diff --numstat 58955ef -- 'tests/*.py'` shows exactly **11** deleted lines, every one inside the re-pointed primary-only lock, both edits named and justified as strengthenings. Lint / format / types clean; `docs check --root docs` exit 0; both bundled mirrors `cmp`-identical; INDEX snapshot identical; `](../` 0/0; `pyproject.toml` unchanged. Original objective: Full product and quality gates with exact counts; mechanical no-regression proof against the 1087 pre-existing ids. |
| 9. Integrate / Accept / Dogfood | **Complete** | 2026-08-15 | Nine flows on throwaway copies; the live `docs/` tree never written to (`git status` empty throughout). E1 42→**0** findings with a 77-line diff in which **every changed line names the moved document**; E2 13→**0** including the 4 archived referrers; E3 6→**0**; plan A completes with its leg-2 report naming exactly **16** references from **7** referrers — the E7 census reproduced; plans B and C refuse at exit 2 with **zero bytes** and empty stdout; plan B's preview reports the same verdict at exit 0 with a populated record; the refusal survives `--quiet` (7 lines, all refusal); a there-and-back move is **byte-identical**, `INDEX.md` included; both verbs' preview and apply records differ in exactly the three state bits. Added runtime: +80 ms on `mv`, +113 ms on a solo archive. Original objective: Replay E1, E2 and E3 on throwaway copies and prove each ends `docs check` clean with a destination-token-only diff; exercise the leg-1 refusal on plans B and C and byte-compare; confirm plan A completes with its leg-2 report naming all 16 still-active inbound references; prove idempotence; measure the added runtime. The real tree is never written to. |
| 10. Quality, Docs, Refactor | **Complete** | 2026-08-15 | `/simplify` over the planner and both verbs — net **−18 lines**, four collapses, suite still 1333 GREEN. `architecture.md` gained a *Move-safe body-link rewrites (M28)* subsection, had its archive pipeline re-drawn through `apply_move_plan`, and gained a `mv` pipeline it never had; `test-strategy.md` gained the `movelink-*` family and two critical-path rows; the shipped use-case catalog landed in Phase 7 with the rest of the surface; `plan.md` and `status.md` record the completion and hand the train to M28a and M29. Original objective: `/simplify`, close `architecture.md` and `test-strategy.md`, update the shipped use-case catalog, completion summaries, hand to M28a and M29. |

## Setup record — 2026-08-15

### Objective

Bring the registered M28 draft stub up to full milestone-task-plan depth and
create this log, without starting Phase 1. M27 is implementation-complete and
merged to `main` (`58955ef`), so M28 is the next implementation milestone in
the v2.0 train. The stub's binding scope — including the post-plan
strand-check added 2026-08-15 — and its three Phase-1 open questions are
carried forward rather than replaced.

### Actions taken

- Read the milestone's inputs end to end: `plan.md`'s v2.0 narrative and M28
  row, `charter.md`, the pinned specs (`cli.md`, `convention.md`,
  `architecture.md`, `test-strategy.md`), `feedback-log.md` — issue #1 in
  particular, whose finding 1 routed the strand-check here and whose finding 4
  left a scope option explicitly unresolved for M28 planning — and the M26 and
  M27 milestone/log pairs, whose *Follow-ups* tables both name M28 as a home.
- Read the code M28 must extend: `scan_body_links` and the `BodyLink` span
  record, `classify_destination`, `normalise_body_link_target`,
  `_body_link_is_contained`, `body_link_findings`, `_cmd_mv`,
  `_cmd_archive`, `plan_archive` / `preflight_archive_plan` /
  `apply_archive_plan`, `_archive_one`, `rewrite_related_refs`, and
  `_rewrite_referring_edges` with its M18 archived-referrer exception.
- Ran a **read-only** body-link census over the live `docs/` tree and over all
  39 committed fixture trees using the shipped M27 scanner — never a
  reimplementation — building the inbound reference map, the outgoing per
  document map, the archived-referrer map, and a per-form inventory.
- Reproduced the milestone's headline defects on **throwaway copies** of this
  tree outside the repository: a rename (E1), a single-document archive (E2),
  and the real milestone-closeout invocation (E3). No repository file was
  mutated during setup; the live tree was only read.
- Probed the routed strand-check predicate against three concrete archive
  plans over the live graph — a legitimate closeout, issue #1's
  `--cascade-only '*'` harm, and archiving `plan.md` alone — and measured that
  its literal form refuses the first (E7). That measurement is what turns Q1
  from a wording detail into the milestone's largest question.
- Expanded *Binding scope* into eight decisions (D1–D8), added *Out of scope*,
  the E1–E8 evidence with an *Evidence → regression coverage* table, the
  ten-phase TDD plan with per-phase objective / files / exit, the phase
  checklist, the testing gate, evidence-anchored success criteria, and
  *Follow-ups recorded for later milestones*.
- Carried the registered stub's three "Open questions for M28 Phase 1" forward
  as Q2, Q4 and Q5 — sharpened by the measurements — rather than dropping
  them, and added Q1, Q3, Q6 and Q7 for the scope and contract decisions the
  reading surfaced. Raised all seven with recommendations rather than deciding
  any of them silently, and then **resolved all seven before Phase 1** — Q1
  (the strand-check predicate), Q2 (archived-referrer audit metadata) and Q3
  (the `mv` preview / `--json` record and the `--report-links` answer) by
  operator decision; Q4, Q5, Q6 and Q7 conductor-resolved from the specs, the
  measured evidence and the M25/M26/M27 precedent.
- Recorded the three answers that changed something already written down in a
  dedicated *Decisions recorded at setup (BINDING)* section of the milestone
  doc — **A1** the amendment to the 2026-08-15 routing entry, **A2** the
  supersession of the stub's Open question 1 recommendation, **A3** the answer
  to issue #1 finding 4 — each with what it replaced, why, and the rejected
  alternatives, so a Phase-1 agent with none of this context can reconstruct
  all three from the document alone.
- Kept the reciprocal `follows` / `precedes`, `depends-on` / `required-by`
  edges intact, flipped the milestone to `Lifecycle: active`, and added the
  milestone ↔ log pair edges.
- Scaffolded this log with
  `docs new log m28-move-safe-body-link-rewrites-impl`, bumped dates and
  validated with `docs touch … --check`, and refreshed the frozen dogfood
  INDEX snapshot `tests/fixtures/expected/docs-INDEX.md` for the new log entry
  — the same snapshot refresh the M25, M26 and M27 setups performed.
- Updated the trackers: `status.md` (current milestone, milestone-progress
  row) now describes M28 as in flight with its plan and log linked.

### Current-tree evidence (docs-cli 1.8.0 with M25–M27 merged at `58955ef`)

| Evidence | Measurement | Why it matters | Bears on |
|---|---|---|---|
| **E1** | On a throwaway copy, `docs mv plan.md milestone-plan.md` prints `moved plan.md -> milestone-plan.md (35 reference(s) rewritten)` and exits **0**; `docs check` then exits **2** with **42 `broken-body-link`** findings across **14** documents — 13 archived plus the active `agent-native-invocation.md`. Worst hit: `archive/2026-05-23/m5-claude-code-skill.md` ×16, `archive/2026-05-22/m4-migration-helper.md` ×6. | The tool now produces trees that fail its own gate, and the metadata repair it performs (35 bullets) is *smaller* than the damage it leaves (42 destinations). | D1, D4 |
| **E2** | `docs archive m17-pypi-publish-impl.md` exits **0**; `docs check` then reports **13** findings — **10 class 1** (`status.md` ×3, `plan.md` ×2, `release-runbook.md` ×1, and **4 inside archived referrers** now dangling on `../../m17-pypi-publish-impl.md`) and **3 class 2** (inside the moved document itself, whose `plan.md` and `release-runbook.md` links now resolve to `archive/2026-08-15/…`). | One ordinary command produces **both** move classes at once, which is why D1 treats them as one formula rather than two features — and 4 of the 13 are only repairable by writing to archived documents. | D1, D5 |
| **E3** | `docs archive m25-reciprocal-relationship-integrity.md --cascade-only 'm25-*' --reason …` — the exact invocation M26 prescribes for a milestone closeout — exits **0** and leaves **6** `broken-body-link` findings in `status.md` (×4) and `plan.md` (×2). | The damage lands in the two documents an agent reads first, on the single most common multi-document write this project performs. It is issue #1 finding 4 at this repository's scale. | D1, D7 |
| **E4** | The live tree carries **395** recognised spans over **71** documents; **379** are `local`, resolving to **69** distinct targets. Most referenced: `release-runbook.md` 49 occurrences / 17 documents, `plan.md` 42 / 14, `cli.md` 24 / 10, `status.md` 24 / 9. Ten active documents carry **211** outgoing local links. | Quantifies both classes' blast radius and shows the exposure is concentrated in exactly the documents most likely to be renamed or reorganised. | D1, D2 |
| **E5** | **131** body links in **27 archived** documents point at **active** documents — `plan.md` ×38, `status.md` ×24, `release-runbook.md` ×23, `cli.md` ×20, `definition-of-ready.md` ×6, `agent-native-invocation.md` ×5, `test-strategy.md` ×4, `architecture.md` ×3, `m17-pypi-publish-impl.md` ×4, and three more. | The archived-referrer policy is a **blocker**, not a nicety: without it, moving any core document leaves errors no verb can repair. M18 already licenses exactly this move-driven class of write. | D5, Q2 |
| **E6** | `rewrite_related_refs` matches a `Related:` bullet's target by **exact string** — the reason M26 — Q5 carries a per-alias pair list. In the E1 reproduction it rewrote 35 bullets by string while leaving 42 destinations broken across three spellings of the same target (`plan.md`, `../plan.md`, `../../plan.md`). | The `Related:` rewriter cannot be reused for path math. The body-link rewriter must resolve first and map on the **normalised** target — which incidentally gives it no alias problem at all. | D1 |
| **E7** | The routed strand predicate, measured over the live graph for three plans. **A** — a textbook `--cascade-only 'm26-*'` closeout: **8** still-active `Related:` edges + **8** still-active body links, from **7** active referrers. **B** — issue #1's `--cascade-only '*'`: **45** + **8**, from **17**. **C** — archiving `plan.md` alone: **11** (including **6** live `child-of`) + **4**, from **12**. Separately confirmed live: `docs archive m27-markdown-body-link-validation.md --cascade-dry-run --cascade-only '*'` marks `plan.md`, `cli.md`, `convention.md`, `test-strategy.md` and `status.md` **selected**. | The literal predicate **refuses the standard milestone closeout**; A and B differ in magnitude, not in kind. The one structural feature B and C have and A does not is six still-active documents declaring `child-of: plan.md` — a parent archived out from under live children. | D6, Q1 |
| **E8** | Across all **39** committed fixture trees there are 110 local body links, **all** of them in the six `bodylink-*` trees (18) or the `real-trees-adopted` migrate fixture (92); the `archive-*`, `mv-with-malformed`, `rename-with-*`, `cross-refs` and `with-archive` trees carry **zero**. In `docs/`: **zero** angle-bracket, percent-escaped or backslash-escaped destinations, and exactly **one** local destination anywhere carries a fragment (`convention.md` → `cli.md#common-exclusion`). | No existing `mv` or `archive` fixture exercises a body link at all, and no corpus anywhere exercises the forms the re-encoding rules govern. Phase 3 must author every one deliberately — the same conclusion M27 — E8 forced. | Phase 3, Q5 |

### Verification

- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 47 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues found in 48 source files.
- `.venv/bin/python -m pytest -q` — 1087 passed.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).

### Decisions / issues

- **The damage class is the one M27 already repaired by hand.** M27 — D6's
  one-time migration fixed 139 archived breaks, 132 of them a pure un-rebased
  `../../` — which is class 2 of D1's formula, produced by `docs archive`
  itself. M28 is that repair, generalised and moved into the verb, and M27's
  Phase-6 execution is the best available evidence that the span-splice
  approach works on real data: 140 occurrences over 30 documents, spliced by
  offset right-to-left, with 30/30 byte-identical round-trip reconstructions.
- **The two classes are one formula, not two features.** Resolving each
  destination from the referrer's *old* location, mapping the resolved target
  through the move set, and relativising against the referrer's *new*
  directory produces class 1 when the map fires and class 2 when the referrer
  itself moved. E2 shows a single archive producing both, which is why they
  cannot be separate code paths.
- **Matching on the normalised target is strictly better than the `Related:`
  rewriter's exact-string match**, and it is not a stylistic preference: E6
  shows the same target spelled three ways in one tree. It also means M28
  needs no analogue of M26 — Q5's alias list.
- **The archived-referrer question is a blocker.** E5's 131 links mean that
  without D5 the tool cannot complete a clean move of `plan.md`, `cli.md`,
  `status.md` or `release-runbook.md` at all — the resulting `broken-body-link`
  errors are hard, and no verb can repair them. M18's exception already
  licenses move-driven writes to archived documents for the `Related:` half of
  exactly this repair, so D5 widens M18 along its own axis rather than
  granting the fourth exception `convention.md` says it will not grant.
  **Q2 resolved the audit-metadata half against the registered stub's own
  recommendation** (A2): destination tokens only, no `Updated:` bump, no
  `Revision:` bullet — the same trigger, operation and single write as M18's
  half, asserting nothing new, and avoiding an archived document's date
  becoming a record of some *other* document's move. Phase 7 reconciles
  M27 — D6's "last one this convention grants" sentence with the widened M18
  paragraph.
- **The strand-check's literal predicate does not survive contact with a real
  tree, and this is the milestone's central finding.** The routing entry
  reasoned that the check "self-cancels for legitimate whole-set archiving,
  because a set archived together strands nothing". Measured, it does not: a
  correct M26 closeout leaves 7 active referrers pointing into the archived
  set, every one of them deliberate — `status.md`'s tracker edges, `plan.md`'s
  `parent-of`, and the neighbouring milestones' `precedes` / `follows` /
  `depends-on`, which is precisely what M25's reciprocal graph exists to
  record. Refusing that would break the workflow the tool is for. **Q1
  resolved it as an amendment to the routing entry** (A1), in two binding
  legs: **leg 1** refuses only when a still-active document outside the plan
  declares itself `child-of` a document the plan would archive — 0 occurrences
  on plan A against 6 on both plan B and plan C — and **leg 2** *reports*
  every other still-active inbound reference, `Related:` and body link alike,
  in the preview, the apply output and the record's `strands` array, refusing
  nothing. Leg 2 is not decoration: it is the half that answers issue #1's
  actual complaint — that the safety rested on a human reading a preview — by
  handing the consequences to the caller in a parseable form, so it carries
  its own deliverable, success criterion and named coverage. Three
  alternatives were rejected and are tabulated in A1 with the reason each
  lost: shipping the literal predicate, refusing an unbounded `'*'` scope
  (trivially defeated by `*.md`), and a `Role:`-based rule (a vocabulary
  policy, not a consequence check).
- **Consistency with how issue #1's other suggestion was handled matters
  here.** In the same feedback entry the operator declined the reporter's
  finding-3 rule because "two documents archived months apart may legitimately
  carry an edge, so the rule would fire on correct trees and fail the
  charter's *never cry wolf* criterion". The literal strand predicate fails the
  same test on the same tree, which is the argument for narrowing it rather
  than shipping it as written.
- **`docs mv` has to be inverted before it can be safe.** It moves the file and
  *then* rewrites, so a class-2 rewrite and an all-or-nothing contract cannot
  both hold. Planning before the move also lets `mv` inherit M26 — D4's
  refuse-with-zero-mutation guarantee, which it has never had.
- **One write per document, not two.** The `Related:` rewrite and the body-link
  splices for the same document are applied to one text and committed with a
  single `atomic_write`; `_rewrite_referring_edges` is already single-pass, and
  keeping it so avoids doubling the failure surface.
- **`feedback-log.md` issue #1 finding 4's `--report-links` alternative is
  answered, not ignored** (D7, Q3, operator — A3): **declined as a design** —
  M27 has already made a broken prose link a hard error, so "declare them out
  of scope" would leave the tool knowingly producing failing trees — but its
  **output is adopted**, and widened, as a plan record on **both** verbs.
  `docs mv` gains a real `--dry-run` preview and a `--json` rewrite-plan
  record; `docs archive --json` gains the same rewrite section plus the
  `strands` array; one schema is shared by preview and apply, following
  M26 — D7's operator-approved `archive --json` addition and M25's
  `relate --json` conventions. Phase 7 adds a dated note to the issue #1 entry
  so findings 1 and 4 are visibly resolved rather than silently absorbed.
- **M28 cannot create an escaping destination.** Both endpoints of every
  rewrite are canonical in-root paths, so their relative form always
  normalises back inside the root. Worth stating as an invariant with its
  one-line proof, because it is what lets M28 inherit M27's guarantee rather
  than re-argue it.
- **Nothing in the fixture corpus exercises this** (E8). Every `mv` / `archive`
  fixture has zero body links, and the whole repository has zero angle,
  percent-escaped or backslash-escaped destinations and exactly one fragment.
  Phase 3 authors all of it — the same position M27 — E8 put Phase 3 in, and
  the reason Q5's re-encoding rules must be pinned in Phase 1 rather than
  discovered in Phase 6.
- Version staging is already settled by M25 — D6: the package stays `1.8.0`
  through M25–M28 (and M28a) and M29 performs the single bump to `2.0.0`. M28
  touches neither `pyproject.toml` nor the packaging version pins; its
  CHANGELOG entries accumulate under the existing `UNRELEASED` heading.
- Host-machine workflow skills are **not** updated by this milestone. Per
  `CLAUDE.md`, host skills refresh only at a production ship; the bundled skill
  inside `src/docs_cli/skill/` **is** updated in lockstep, in Phase 7.
- **No OPEN QUESTIONS remain.** All seven are resolved and recorded as binding
  in the milestone doc's *Resolved setup questions (Q1–Q7, BINDING)*, with the
  three that changed prior decisions restated in *Decisions recorded at setup
  (BINDING)*. Phase 1 freezes the rewrite formula, the emitted spelling and
  re-encoding rules, the archived-referrer policy, both strand-check legs, the
  atomicity boundary and the two verbs' preview / `--json` shapes against them
  rather than re-litigating scope.

### Resolved setup questions — summary

Full reasoning in the milestone doc's *Resolved setup questions
(Q1–Q7, BINDING)*; the three answers that changed something already written
down are restated in *Decisions recorded at setup (BINDING)* as A1, A2 and A3.

| # | Question | Resolution |
|---|---|---|
| Q1 | What exactly does the post-plan strand-check refuse? Its literal form refuses this repository's own standard closeout (E7). | **RESOLVED (operator) → D6, and an AMENDMENT to the 2026-08-15 routing entry (A1).** Two binding legs. **Leg 1** refuses only when a still-active document outside the plan declares itself `child-of` a document the plan would archive — 0 hits on plan A, 6 on plans B and C. **Leg 2** names every other still-active inbound reference — any other `Related:` verb and every body link — in the preview, the apply output and the record's `strands` array, refusing nothing; it is not optional and carries its own deliverable, success criterion and coverage. Rejected with reasons in A1: the literal predicate (refuses a correct closeout), an unbounded-`'*'` refusal (defeated by `*.md`), a `Role:`-based rule (a vocabulary policy, not a consequence check). |
| Q2 | Does an archived referrer's body-link rewrite carry audit metadata? *(stub Open question 1)* | **RESOLVED (operator) → D5, against the stub's own recommendation (A2).** **M18's shape** — destination tokens only, no `Updated:` bump, no `Revision:` bullet: same trigger, same operation, same single write; nothing new is asserted; and a bump would make an archived document's date a record of another document's move while churning INDEX. Implemented by **widening M18's exception**, granting no fourth one, with M27 — D6's "last one this convention grants" sentence reconciled in Phase 7. |
| Q3 | Does `docs mv` gain a real preview and a `--json` rewrite-plan record? Also the home of issue #1 finding 4's `--report-links` option. | **RESOLVED (operator) → D7 (A3). Yes, both.** `docs mv` gains a real `--dry-run` preview and a `--json` rewrite-plan record; `docs archive --json` gains the same rewrite section plus a `strands` array; one schema shared by preview and apply, following M26 — D7 and M25's `relate --json` conventions. `--report-links` is **declined as a design** (M27 already made a broken prose link a hard error, so a report-only option would mean knowingly shipping failing trees) while its **output is adopted** as the plan record. |
| Q4 | What happens to destinations a move does not own — non-`local`, already broken, or escaping? *(stub Open question 2)* | **RESOLVED (conductor) → D2 + D3, as recommended.** Leave them byte-identical and do **not** gate the move on them. M27 already guarantees a clean tree has no escaping link; pre-existing damage keeps its M27 finding, and `docs check` owns it. |
| Q5 | Same-path normalisation, the emitted spelling, and re-encoding. *(stub Open question 3)* | **RESOLVED (conductor) → D3, as recommended.** Byte-for-byte preservation when the computed semantic destination is unchanged; otherwise the `posixpath.relpath` form, fragment reattached verbatim, original delimiter form preserved, one stated escape strategy, locked by a decode round-trip test. No corpus destination exercises any escape (E8), so that path ships against authored fixtures only. |
| Q6 | Does `docs migrate --apply`'s archive-normalising move get the same treatment? | **RESOLVED (conductor) → out of scope, as recommended**, recorded as *Follow-ups* item 1. `docs migrate` repairs no references at all today, operates on a foreign tree, and folding it in would widen M28 from a coordinated move to an adoption workflow. |
| Q7 | Does M28 fix M26 — *Follow-ups* item 3 (duplicate `Related:` bullets from alias rewriting), which is homed here? | **RESOLVED (conductor) → re-deferred explicitly, with the reason, as recommended.** M28 builds a destination-token splicer over body text, not a `Related:`-block editor; the cost is cosmetic. The alternative — deduplicating `apply_archive_plan`'s pairs and flipping the pinned test — **reaches into M26's frozen Phase-1 Q5 contract**, and M28 does not do that. |

## Phase 1 — Define Contract — 2026-08-15

### Objective

Freeze, against the resolved Q1–Q7, everything Phase 2 will assert against:
D1's formula and the move map, the emitted spelling / fragment / delimiter /
re-encoding rules, the byte-for-byte no-op rule, the never-creates-an-escape
invariant with its proof, the archived-referrer policy (destination tokens
only) and its `convention.md` wording, both strand-check legs, the pre-flight
and partial-state boundary, both verbs' preview and `--json` shapes, and the
Phase-5 signatures. **No product code lands** — signatures are frozen in prose
following the M25/M26/M27 precedent, because stubs would perturb the Phase-4
subprocess RED reasons.

### Actions taken

- Wrote the machine-facing contract as *Decisions (Phase 1 — BINDING)* in the
  milestone: items **(A)** the move map, **(B)** the formula's BINDING step
  order, **(C)** the destination-token renderer and both encode sets, **(D)**
  the never-creates-an-escape invariant with its one-line proof, **(E)** the
  per-document write pipeline, **(F)** validate-all-first, **(G)** the
  archived-referrer rule stated as one sentence, **(H)** both strand legs,
  **(I)** both check orders, **(J)** the message catalogue, **(K)** both
  `--json` schemas, **(L)** the Phase-5 signatures, **(M)** the authoring
  traps.
- Recorded **three amendments to setup-frozen material** in place, so the
  binding scope and the frozen contract cannot disagree (M27's precedent):
  M26's compatibility-matrix row (a preview adopts plan-**construction**
  failures and reports-but-does-not-adopt **consequence** verdicts), the E7
  leg-2 coverage row (plan B's `strands` array is observed in its *preview*,
  because a refusal emits no record), and the E3 coverage row (a new
  `movelink-closeout` tree **reproduces** the `archive-pair` / `archive-trio`
  shape instead of the committed trees gaining body links). The E3 and E7 rows
  are edited in place in *Evidence → regression coverage*.
- Recorded **eleven Step-1 resolutions (R1–R11)** — three operator decisions
  (a preview adopts construction failures; no `--json` record on a refusal, so
  plan B is observed in its preview; print everything unless `--quiet`) and
  eight conductor decisions (`strands` is `archive`-only; the fixture
  contradiction is resolved by copying; one refusal line per orphaned pair plus
  a count; a directory destination keeps its trailing slash; the grammar-derived
  minimal encode set with `%` first; `mv`'s upgraded partial-state admission;
  no count key in either record; excluded documents are named as a limitation
  rather than left to inference).
- Landed the author-facing halves in `docs/cli.md`: a new
  *Move-safe body-link rewrites (M28 — D1–D7)* block covering both verbs; a
  rewritten `docs mv` section with its preview, its `--json` record and field
  table, its partial-state admission and its own exit table; the archive check
  order amended with 5b / 8b / 8c / 8d as sub-steps of the numbering M26 froze;
  the `archive --json` example, field table and record descriptions widened by
  `rewrites` and `strands`; and the archive and global exit tables amended.
- Landed the convention halves in `docs/convention.md`: M18's exception
  **widened** along its own axis (destinations beside bullets, no audit
  metadata, active referrers treated the same), M27 — D6's "the last one this
  convention grants" sentence **reconciled** (M28 leaves the count at three),
  and a new author-facing statement under *Body links (M27)* — a coordinated
  move rebases supported links, keeps an unchanged meaning byte-identical, and
  can refuse before it writes.
- Mirrored both specs byte-identically into `src/docs_cli/skill/references/`
  and re-synced the frozen dogfood INDEX snapshot after `docs touch` moved
  `cli.md`'s and `convention.md`'s `Updated:` values.

### Contract decisions worth calling out

- **The write path's message precedence is unchanged.** The Step-1 plan put the
  whole-tree walk at step 5b for *both* paths, which would have inverted the
  ordering `cli.md` freezes ("the plan pre-flight deliberately precedes the
  whole-tree walk … naming the document the operator actually asked for is
  strictly more actionable"). Under that ordering an unwritable member and a
  malformed referrer would have swapped messages, and a `--cascade-only` write
  selecting nothing would have exited 1 instead of 2. The frozen contract puts
  the walk at **5b for the preview and at 8 for the write path** instead, so
  M28 adds steps around M26's order without changing a single precedence it
  froze. Recorded in item (I).
- **`move_plan_to_json` returns the shared section**, `{"rewrites": …,
  "strands": …}`, and each verb splices what it carries into its own record.
  That is what makes "byte-comparable between the two verbs" a property of
  construction rather than of discipline, and it keeps the frozen name and
  arity while `mv` legitimately omits `strands` (R4).
- **`plan_move` gained `related_pairs` and `strand_check`.** The alias-expanded
  `Related:` pairs (M26 — Q5) and the canonical body-link move map are genuinely
  different inputs — item (A) — and R4 makes the strand analysis
  `archive`-only, so both had to be parameters rather than assumptions.
- **Two encode-set residuals are recorded rather than hidden** (item (C) ›
  *Known residuals*, *Follow-ups* item 7): a path component carrying whitespace
  other than space or tab, and a colon in the first path segment, which would
  re-classify the emitted token as `scheme`. Neither is reachable from a
  filename this tool creates. Phase 2 pins the frozen set and asserts nothing
  about either, so closing them later flips no test.

### Verification

- `git diff --stat -- src/docs_cli/cli.py` — **empty**. No product code changed.
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 47 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues found in 48 source files.
- `.venv/bin/python -m pytest -q` — **1087 passed** (unchanged).
- `.venv/bin/docs check --root docs` — no violations found (exit 0).
- `cmp docs/cli.md src/docs_cli/skill/references/cli.md` and the same for
  `convention.md` — identical.
- `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.
- `grep -c '](\.\./' docs/cli.md docs/convention.md` — **0** in both.

## Phase 2 — Write Tests (RED) — 2026-08-15

### Objective

Express the whole Phase-1 contract as tests before any implementation:
planning, splicing, both move classes, the archived referrer, **both**
strand-check legs, the failure paths, the no-op rule and both `--json`
records — including every case that must stay GREEN at baseline, and
including the leg-1 over-fire lock proving a legitimate closeout completes.

### Actions taken

- Authored **`tests/test_move_links.py`** (153 ids), the pure seam. Every M28
  symbol is reached through a single `_m28(name)` wrapper over
  `getattr(cli, …)` — a module-level import of a missing name would be a
  COLLECTION error, which the Phase-4 exit criterion forbids, and a literal
  `getattr` trips ruff's B009. Groups: the formula and its two classes; the
  no-op rule and idempotence; out-of-reach destinations (every non-`local`
  kind, an escape, pre-existing damage); the never-creates-an-escape invariant
  over 16 depth/direction combinations; the emitted spelling; the re-encoding
  rules including a 72-case decode round-trip against the scanner's own
  `_split_destination`; the splicer; the pipeline order; purity; both strand
  legs; the pre-flight; and the shared record.
- Appended **12 `docs mv` locks** — the real preview, the `--json` record and
  its preview/apply equality, E1's post-rename `docs check`-clean assertion,
  class-2 rebasing, nested both-directions, the archived referrer's byte
  boundary and its no-`Revision:` sibling, prose and code untouched, the
  zero-mutation refusal, the malformed-tree preview at exit 2, and
  idempotence.
- Appended **14 `docs archive` locks** — E2's both-classes-at-once, E3's
  closeout, E5's archived referrer, leg 1's refusal (zero bytes, both ends,
  no record) and its `--quiet` sibling, leg 1's preview at exit 0, the
  over-fire lock, leg 2's stderr report in preview and apply, the widened
  `--json` key set, `strands` on a plan that completes, `strands` observed in
  the preview of a refusing plan, the empty-array-not-missing lock, the
  preview/apply rewrite-section equality, and the malformed-tree preview at
  exit 1.
- Appended **1 `docs check` lock** asserting every `movelink-*` tree is clean
  as committed, and **2 bundled-skill locks** for the M28 surface.
- Every fixture-backed test routes through a helper that asserts the tree
  directory **exists**, so the family is honestly RED between Phase 2 and
  Phase 3 rather than vacuously green on an empty copy (M27's Phase-2 catch).
  The `movelink-*` check lock names its seven trees explicitly rather than
  deriving them from a glob, which would generate **zero** ids before Phase 3.
- Every intended-exit-2 (and exit-1) subprocess test asserts a **frozen
  contract string** as well as the code, so an unrelated failure with the same
  code cannot later satisfy it (M26's falsely-GREEN lesson).

### Decisions / issues

- **The purity test uses `pytest.MonkeyPatch.context()`, not the fixture.**
  The fixture reverts at teardown, so a failure inside the block left
  `Path.exists` poisoned while pytest rendered the traceback — an
  INTERNALERROR instead of a readable RED reason. Caught by running the file;
  the context manager reverts as the exception unwinds (M27's
  `test_normalise_is_lexical_…` precedent, for the same reason).
- **Line numbers are part of the fixture contract.** `movelink-incoming`'s
  destinations are pinned at `note.md:13` and `sub/deep.md:10`, and
  `movelink-closeout`'s at `feature.md:16`, `plan.md:13` and `status.md:13`,
  because Phase 2 asserts `rewrite <doc>:<line>` and
  `strand <src>:<line>` lines verbatim. Phase 3 authors exactly those shapes.
- **The closed four-key `Finding` record is asserted unchanged by the existing
  M27 lock** (`tests/test_cli_check.py` › *D4/Q4: no new JSON field*), which
  stays GREEN at baseline. M28 adds no `docs check` rule, so duplicating it
  here would add an id without adding coverage.
- **No pre-existing test is deleted, renamed, or has an assertion altered.**
  `git diff --numstat -- tests/` shows **0** deleted lines across all four
  appended files, and `tests/test_edit.py`, `tests/test_relate_plan.py` and
  `tests/test_archive_plan.py` are untouched — `rewrite_related_refs` and the
  M26 plan contract are not reached into.

### Verification

- `git diff --stat -- src/docs_cli/cli.py` — **empty**.
- `.venv/bin/python -m pytest tests/ -q --co` — **1269 collected**, 0
  collection errors (1087 + 182 new).
- `.venv/bin/python -m pytest tests/ -q` — **181 failed, 1088 passed**. The
  one new GREEN id is `test_relpath_of_a_root_level_target_needs_no_special_case`
  — degenerate at baseline (it pins a `posixpath` property the Phase-5
  implementation must not "fix"), a genuine lock afterwards.
- `git diff --numstat -- tests/` — 777 insertions, **0 deletions**.
- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).

## Phase 3 — Create Data/Fixtures — 2026-08-15

### Objective

Author the committed trees the CLI locks need — one semantic each, per
`test-strategy.md`'s fixture policy — given E8: **not one** existing `mv` or
`archive` fixture carries a body link, and the whole corpus carries zero
angle, percent-escaped or backslash-escaped destinations and exactly one
fragment. Every rewrite-relevant tree form is authored deliberately.

### Actions taken

Seven new trees under `tests/fixtures/trees/`, each with its own
`.docs.toml`, structure-only and static-dated:

| Tree | Shape | Isolates |
|---|---|---|
| `movelink-incoming` | `plan.md`, `note.md`, `sub/deep.md` | class 1 — one target, two spellings, two depths; plus a prose mention and a code span that must survive |
| `movelink-moved-referrer` | `guide.md` linking `target.md` and `sub/ref.md` | class 2, both directions in one move |
| `movelink-both` | `a.md` ↔ `b.md` co-moving, `c.md` staying | E2 — both classes in one archive, and the co-moving no-op |
| `movelink-archived-referrer` | `plan.md`, `keep.md`, `archive/2026-01-01/old-log.md` | E5 + the byte-identity boundary (a non-moving edge, a non-moving destination, a bare prose mention) |
| `movelink-nested` | `sub/deep/x.md` linking up, down, and up-then-down | E4 path math, three spellings |
| `movelink-strand` | `plan.md`, `live-child.md`, `milestone.md`, `milestone-impl.md` | D6 leg 1 — a live child outside the plan, and a legitimate closeout that must NOT trip it |
| `movelink-closeout` | `feature.md` + `feature-impl.md` + `status.md` + `plan.md` | E3 + the leg-1 over-fire lock at tree scale |

- **`movelink-closeout` reproduces the `archive-pair` / `archive-trio`
  SHAPE** rather than those trees gaining body links — Phase-1 amendment 3.
  `git status` shows exactly **seven new directories** and no modified
  fixture.
- **No committed fixture filename carries a space or a parenthesis.** The
  `%20` / `%28` re-encoding cases are renderer calls and `tmp_path` builders
  in `tests/test_move_links.py`; `tests/` ships in every sdist.
- **Line numbers are contract**, and they are the ones Phase 2 asserts
  verbatim: `note.md:13`, `sub/deep.md:10`, `feature.md:16`, `plan.md:13`,
  `status.md:13`.
- No `precedes` / `follows`, `depends-on` / `required-by` or `blocks` /
  `blocked-by` verb appears anywhere in the seven, so all of them pass the
  legacy no-new-findings sweep; `child-of`, `parent-of`, `pairs-with` and
  `references` are free-form and carry no reciprocal obligation.

### The prototype census (read-only)

A throwaway prototype of the Phase-1 contract — the formula, the renderer
and both strand legs, over the shipped M27 scanner and never a
reimplementation of it — was run read-only over all seven trees. It
reproduced **every** expectation Phase 2 asserts, including the ones that
were hand-computed:

- `movelink-closeout` under `--cascade-only 'feature-*'` yields exactly
  `feature.md:16 plan.md -> ../../plan.md`, `plan.md:13`, and two on
  `status.md:13` — **4 destinations in 3 documents** — with the co-moving
  pair's links to each other left untouched, and exactly the **five** leg-2
  strands in the frozen order (walk order; bullets before body links).
- `movelink-strand` archiving the roadmap yields **two** orphans in walk
  order (`live-child.md`, `milestone.md`) and one leg-2 strand; the scoped
  closeout of the milestone pair yields **zero** orphans — the over-fire lock
  at tree scale.
- `movelink-archived-referrer` yields `../../renamed-plan.md` under `mv` and
  `../2026-08-15/plan.md` under `archive` — the archived-referrer rebase, from
  one dated directory to another.

### Decisions / issues

- **Two Phase-2 tests were strengthened once the fixtures made their real
  state observable**, which is exactly what a fixture phase is for:
  - `test_mv_archived_referrer_gains_no_revision_bullet` was GREEN at
    baseline **for the wrong reason** — no `Revision:` appears today because
    no body-link write happens at all. It now asserts the destination rewrite
    first, so it observes the M28 write and the absence of audit metadata in
    the same document.
  - `test_mv_second_equivalent_move_changes_nothing` was RED for the wrong
    reason: the fixture ships without an `INDEX.md` and the first move
    generates one, so a whole-tree byte compare could never pass. `INDEX.md`
    is now excluded from the comparison and asserted separately, and the test
    additionally proves the FIRST move actually rewrote something.
- `sub/ref.md` initially carried a stray blank line inside its metadata
  block, which ends the block early and surfaces as `missing-field: Updated`.
  Caught by the per-tree `docs check`, which is why that gate runs before the
  suite.

### Verification

- `git diff --stat -- src/docs_cli/cli.py` — **empty**.
- `.venv/bin/docs check tests/fixtures/trees/movelink-<each>` — exit 0 for all
  **seven**.
- `test_check_tree_legacy_fixtures_gain_no_new_findings` — **36 passed**
  (29 + 7).
- `test_check_tree_pre_m27_fixtures_gain_no_body_link_findings` — **40
  passed** (33 + 7).
- `.venv/bin/python -m pytest tests/ -q --co` — **1283 collected**, 0
  collection errors *(as Phase 3 left it; the Step-1 audit and the fresh-eyes
  fold-in later took it to 1332)*.
- `.venv/bin/python -m pytest tests/ -q` — **180 failed, 1103 passed** *(as
  Phase 3 left it)*.
- `git diff --numstat 58955ef -- tests/` — **0** deleted lines in every test
  file; the only deletions anywhere are the frozen INDEX snapshot's re-synced
  `Updated:` values from Phase 1.
- `git status` — exactly seven new fixture directories.
- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).

## Phase 4 — Run Tests (RED Baseline) — 2026-08-15

### Objective

Prove the new tests fail for the intended missing behaviour and for nothing
else, and prove mechanically that no pre-existing test id moved.

### The baseline

```
.venv/bin/python -m pytest tests/ -q --co   ->  1332 collected, 0 collection errors
.venv/bin/python -m pytest tests/ -q        ->  229 failed, 1103 passed
```

*(Restated twice: after the Step-1 same-instance audit, which added twelve
locks, and after the fresh-eyes fold-in, which added thirty-seven more and
strengthened one pre-existing test by operator decision. The figures Phase 4
first measured were 1283 / 180 / 1103.)*

Arithmetic, and it closes: **1087** pre-existing + **231** authored ids +
**14** swept ids (7 into `test_check_tree_legacy_fixtures_gain_no_new_findings`,
7 into `test_check_tree_pre_m27_fixtures_gain_no_body_link_findings`) =
**1332**. Of the 245 new ids, **228** are RED and **17** are GREEN at
baseline; the 229th failure is `test_mv_help`, a **pre-existing** id
strengthened by operator decision (see *Fresh-eyes review fold-in* below).

### Probes, stated honestly

- **Collection errors: 0.** `--co` collects 1332 and reports no errors.
- **xfail / xpass / errors: 0.** `pytest -rxXE` reports no `XFAIL`, `XPASS`
  or `ERROR` line.
- **Warnings: 0.** No warnings summary is emitted.
- **Tracebacks: 0, but the bare word is not a usable probe** — M26's
  false-positive trap, hit here for real. `grep -c Traceback` over the
  `--tb=line` output is 0; `grep -c INTERNALERROR` over a `--tb=long` run is
  **1**, and that single match is
  `tests/test_move_links.py`'s own docstring — the sentence explaining why the
  purity test uses `pytest.MonkeyPatch.context()` — printed as source context.
  Several tests additionally assert `"Traceback" not in proc.stderr` in their
  source. Both probes must exclude source-context lines to mean anything.

### Exception-class census (`--tb=line`)

Exactly **two** classes, and the arithmetic closes:

| Class | Count | Where | Why |
|---|---|---|---|
| `AttributeError` | 193 | the whole of `tests/test_move_links.py` | every M28 symbol is fetched through `_m28(name)`, so the RED reason is one clean missing attribute rather than a collection error |
| `AssertionError` | 36 | 17 `docs mv` (one of them the strengthened `test_mv_help`), 17 `docs archive`, 2 bundled-skill locks | the behaviour is absent, not the symbol; 34 carry a message and 2 are bare `assert`s pytest rewrote |

An earlier run showed a third class — **3 `KeyError: 'strands'`** from indexing
a record that has no such key. That is a weaker RED reason than an assertion
and it hid the very property the tests exist to pin, so all three now assert
`"strands" in record` first. The census is two classes by construction, not by
luck.

### Mechanical no-regression proof

Test ids were collected from a throwaway `git worktree` at the pre-M28 commit
`58955ef` and from HEAD, and compared with `comm`:

| Measure | Result |
|---|---|
| ids at `58955ef` | **1087** |
| ids at HEAD | **1332** |
| `comm -23 old new` — **removed** ids | **0** |
| `comm -13 old new` — added ids | **245** (194 `test_move_links.py`, 17 `test_cli_mv.py`, 17 `test_cli_archive.py`, 14 `test_check.py` sweeps, 2 `test_skill.py`, 1 `test_cli_check.py`) |
| `comm -12 failed old` — pre-existing ids now FAILING | **1** — `test_mv_help`, and only that one. It is a **deliberate operator decision** taken at the Step-1 review: `cli.md` advertises `docs mv --json`, the test asserted only that `old` and `new` appear in `--help`, and nothing would have flagged the gap if Phase 7 forgot the argparse half. Strengthening it converts Phase-7 follow-through item 2 from a promise into a lock, and going RED until Phase 7 is exactly what a RED-baseline step is for. No assertion was weakened or removed. |
| `git diff --numstat 58955ef -- tests/` | **0** deleted lines in every test file |
| `git diff --stat 58955ef -- src/docs_cli/cli.py` | **empty** |

`tests/test_edit.py`, `tests/test_relate_plan.py` and `tests/test_archive_plan.py`
are untouched: `rewrite_related_refs` and M26's frozen plan contract are not
reached into.

### RED classification — every failure traced to a family and a landing point

| # | Family | Landing |
|---|---|---|
| 156 | **The pure seam** (`tests/test_move_links.py`): the formula and both classes, the no-op rule and idempotence, out-of-reach destinations, the never-creates-an-escape invariant, the emitted spelling, the re-encoding round-trip, the splicer, the pipeline order and its one-write-per-document count, purity, both strand legs and the bullet declaration order, the pre-flight, the alias-pair split, and the shared record | **Phase 5** — `LinkRewrite`, `DocRewrite`, `Strand`, `MovePlan`, `MOVE_STRAND_KINDS`, `plan_body_link_rewrites`, `render_destination_token`, `splice_body_links`, `plan_move`, `preflight_move_plan`, `apply_move_plan`, `move_plan_to_json` |
| 16 | **`docs mv` behaviour and surface**: class-2 rebasing, nested both-directions, an **archived** document `mv`'d rebasing its own destinations, E1's post-rename `docs check`-clean, the archived referrer's byte boundary and its no-`Revision:` sibling, prose and code untouched, the zero-mutation refusal, the malformed-tree preview at exit 2, idempotence, the preview's rewrite lines and its zero-byte guarantee, the apply path's identical lines, the mid-execution partial-state admission, and the `--json` record with its `source`/`path` split and its preview/apply equality | **Phase 6** — invert `_cmd_mv` to plan before it moves — and **Phase 7** for `--json` on the `mv` subparser (`cli.py:4852`) |
| 17 | **`docs archive` behaviour and surface**: E2, E3, E5, leg 1's refusal and its `--quiet` sibling, leg 1's preview at exit 0, the over-fire lock, leg 2's stderr report ordered in both modes, the rewrite-plan pre-flight over a planned **referrer**, `--quiet` on a completing run, the excluded-document limitation, the widened `--json` key set, `strands` on a completing plan and exactly-one in a refusing plan's preview, empty-array-not-missing, preview/apply rewrite equality with a zero-byte preview, and the malformed-tree preview at exit 1 | **Phase 6** (behaviour) and **Phase 7** (the record and the amended check order) |
| 2 | **Bundled skill parity**: `SKILL.md`'s `mv` / `archive` rows and `references/use-cases.md` | **Phase 7** — the bundled skill lands in the same change as the CLI surface |

### GREEN at baseline — every lock classified

The 17 new GREEN ids:

| Lock | Classification |
|---|---|
| `test_check_tree_legacy_fixtures_gain_no_new_findings[movelink-*]` ×7 | **degenerate** now (none of the seven uses a reciprocal verb); a genuine regression lock after Phase 6 |
| `test_check_tree_pre_m27_fixtures_gain_no_body_link_findings[movelink-*]` ×7 | **degenerate** now; genuine afterwards — a Phase-6 rewrite that emitted a wrong spelling would break them |
| `test_check_every_movelink_fixture_tree_is_clean_as_committed` | **genuine**; it landed at Phase 3, and it is what makes every post-move clean assertion measure the MOVE rather than pre-existing fixture damage |
| `test_relpath_of_a_root_level_target_needs_no_special_case` | **degenerate** now, and it can never fail for any M28 implementation — it pins the `posixpath` behaviour item (B) step 6 relies on, so a Phase-5 implementation cannot "fix" it with an `or '.'` that changes every emitted spelling. Kept deliberately as ground truth. |
| `test_mv_quiet_suppresses_every_line_but_prints_a_refusal` | **degenerate** now (`docs mv --quiet` prints nothing today because there is nothing to print); genuine at Phase 6, when the move line, every rewrite line and the counts footer exist and `--quiet` must still silence all of them while the refusal survives |

Pre-existing locks whose expected state is worth naming, all verified GREEN at
this gate:

| Lock | Classification |
|---|---|
| `test_cli_mv.py::test_mv_oserror_mid_rewrite_exits_2` | GREEN, and **TRANSITIONAL**: today the `OSError` is mapped after the move; after Phase 6 the rewrite-plan pre-flight refuses before it, so the observable exit 2 and the no-traceback guarantee survive while the mechanism changes underneath. Its Phase-2 sibling `test_mv_refuses_before_the_move_when_a_planned_referrer_is_unwritable` locks the zero-mutation half the old test cannot see. |
| `test_cli_mv.py::test_mv_dry_run_makes_no_change` | GREEN throughout. Its `cross-refs` tree is clean, so the new preview walk does not fire. |
| `test_cli_archive.py::test_archive_does_not_touch_prose_references_to_old_path` | Becomes a **genuine** M28 lock: a bare-text mention is not a link, and M28 is the first milestone that could get that wrong. |
| `test_cli_archive.py::test_archive_leaves_unrelated_archived_content_byte_identical` | **Genuine**. Its bystanders carry prose, not links, so the widened D5 gate must leave them byte-identical. |
| `test_cli_archive.py::test_two_spellings_of_one_edge_survive_the_rewrite_as_duplicate_bullets` | GREEN and **unchanged**. Q7 is re-deferred; M26's frozen Phase-1 Q5 contract is not reached into. |
| `test_cli_check.py::test_check_dogfood_repo_docs_is_clean` | **Genuine**, GREEN throughout. M27 already repaired the live tree. If it goes RED, a Phase-1 spec example became a real broken link. |
| `test_cli_index.py::test_index_output_matches_frozen_snapshot` | **Genuine**. Re-sync `tests/fixtures/expected/docs-INDEX.md` inside any commit whose `docs touch` moves an `Updated:` value — done in Phase 1. |
| `test_skill_refs.py::test_bundled_ref_matches_source[cli.md]` / `[convention.md]`, `test_bundled_skill_has_no_repo_relative_links`, `test_skill_quality_artifacts.py::test_installed_skill_references_do_not_depend_on_source_checkout` | **Genuine**. Phase 1 kept both mirrors byte-identical and both specs at zero repo-relative link prefixes. |
| `test_a3_project_version_is_1_8_0`, `test_c2_docs_version_is_1_8_0` | **Genuine**. No version bump; M29 owns it (M25 — D6). |

### Falsely-GREEN check at this gate

Done mechanically over every M28 subprocess test, test by test:

- **Every intended-exit-2 and intended-exit-1 test asserts a frozen contract
  string as well as the code**, so an unrelated failure with the same code
  cannot later satisfy it. `test_archive_leg_1_refuses_even_under_quiet` was
  the one weak case — it asserted a substring rather than the frozen line —
  and now asserts both frozen lines plus the absence of the ordinary prose
  `--quiet` suppresses.
- **Every fixture-backed test asserts its tree directory exists**, through
  `_movelink_tree` / `_m28_tree`, so the family was honestly RED before
  Phase 3 rather than green on an empty copy.
- Three intended-**exit-0** tests assert structure rather than a message
  string — `test_legitimate_closeout_completes_despite_still_active_referrers`
  (exit 0 plus the *absence* of both refusal lines), and the two `strands`
  record tests (key presence, closed key set, exact values). They are named
  here so the residual is recorded rather than glossed.

### Phase-5/6/7 follow-through, carried from Phase 1

1. Delete `_rewrite_referring_edges`, superseded by `apply_move_plan`
   (Phase 6/7, on M26's `_cascade_set` precedent).
2. `mv` gains `--json` on its subparser (`cli.py:4852`) and its `--dry-run`
   becomes a real preview.
3. `mv` and `archive` argparse descriptions gain the new behaviour.
4. Bundled `SKILL.md` and `references/use-cases.md` (Phase 7), with
   `references/cli.md` / `references/convention.md` kept byte-identical.
5. `CHANGELOG.md` under the existing `UNRELEASED` heading, with the upgrade
   note: a move now edits prose; an archive now refuses in a case it
   previously completed; **and `docs mv`'s two shipped stderr lines are
   re-spelled** — both gain the `mv: ` verb prefix and
   `docs: moved … (<N> reference(s) rewritten)` loses its trailing count to the
   richer footer. No test pins either string, so nothing goes RED, which is
   precisely why the upgrade note has to name it: anyone parsing `docs mv`
   stderr breaks silently at 2.0 (item (J)).
6. A dated note on `feedback-log.md`'s issue #1 entry answering findings 1
   and 4 (Phase 7).
7. `test-strategy.md`'s fixture-source list gains the `movelink-*` family, and
   `architecture.md`'s move pipeline is closed (Phase 10).
8. The two encode-set residuals (*Follow-ups* item 7) need an operator
   decision before they can be closed or accepted.

### Verification

- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).
- `git diff --stat 58955ef -- src/docs_cli/cli.py` — **empty**. Phases 1–4
  change no product code, by design.

## Step-1 same-instance audit — 2026-08-15

Run against Phases 1–4 after the last phase and before returning, per the
ship-milestone consistency / completeness / accuracy checklist. Seven issues
found; all seven fixed here. Three items are **surfaced** for the operator
rather than auto-decided, because each touches intent rather than accuracy.

### Issues found and fixed

1. **`status.md` was stale in four places.** The *Current milestone* block
   still said "Milestone setup is complete … Phase 1 is next … **No TDD phase
   has started**", the roadmap bullet said "setup complete", the *Next action*
   said "begin M28 Phase 1 — Define Contract", and the *Milestone progress*
   row said "Phase 1 next, no TDD phase started". All four now state Step 1
   (Phases 1–4) complete on `m28/phases-1-4`, with the per-phase narrative and
   the real counts, and the next action is Phase 5.
2. **`plan.md` was stale in two places** — the M28 narrative paragraph and the
   milestone-table row, both still asserting "Phase 1 is next". Both updated;
   the v2.0 sequencing sentence now says M28 is *in flight* rather than *next*.
3. **The `mv` partial-state line disagreed between the two surfaces.** A
   mechanical cross-check of item (J)'s catalogue against every
   `docs: mv: ` / `docs: archive: ` line in `cli.md` found the same template
   written with different placeholders — `Moved: <…>` in (J) against
   `Moved: <old-rel> -> <new-rel>` in `cli.md`. (J) now carries `cli.md`'s
   concrete form, so the frozen catalogue and the spec are byte-comparable.
4. **Two frozen catalogue lines had no test at all**, found by the same
   cross-check, and both are load-bearing:
   - `docs: mv: moved <old-rel> -> <new-rel>` — the apply path's success line.
     A Phase-6 implementation could have printed anything on success and
     passed. Fixed by `test_mv_apply_names_every_rewrite_and_the_move`, which
     also pins that the apply path prints the **same** rewrite lines and
     counts footer as the preview (R3).
   - The whole `PARTIAL MOVE — not rolled back. Moved: … Rewritten: … Not
     written: …` admission — R9's upgrade of `mv`'s residual `OSError` message.
     The pre-existing `test_mv_oserror_mid_rewrite_exits_2` asserts only exit 2
     and no traceback, so an implementation that kept today's bare
     `docs: mv: <OSError>` would have passed. Fixed by
     `test_mv_oserror_mid_execution_admits_the_partial_state`, which exercises
     M26 — D4's own documented boundary: a `0o644` file inside a `0o555`
     directory passes the pre-flight's `os.access` test, must be admitted
     there, and fails later as the residual admission.
5. **R3's quiet rule had no `mv` lock.** Added
   `test_mv_quiet_suppresses_every_line_but_prints_a_refusal` — GREEN at
   baseline and **degenerate** (there is nothing to suppress yet), genuine at
   Phase 6 when the move line, every rewrite line and the footer exist and
   `--quiet` must silence all of them while the refusal survives.
6. **`test_archive_leg_1_refuses_even_under_quiet` asserted a substring rather
   than the frozen refusal line**, so an unrelated exit 2 mentioning
   `child-of` could have satisfied it. It now asserts both frozen lines plus
   the absence of the ordinary prose `--quiet` suppresses. (Found at the
   Phase-4 falsely-GREEN gate and recorded there too.)
7. **Three RED reasons were `KeyError: 'strands'` rather than assertions**,
   which is both a weaker signal and a failure to pin the very
   present-and-empty property those tests exist for. All three now assert
   `"strands" in record` first, which is what makes the Phase-4
   exception-class census two classes by construction. (Also recorded at
   Phase 4.)

### A second, adversarial pass over the same question

The checklist calls the *"do the tests genuinely pin the contract"* item the
highest-leverage check of a 1–4 step, so it was run a second time by a fresh
reader with no memory of writing the tests, working from the frozen contract
rather than from the code. It measured its claims rather than asserting them —
re-deriving all 20 inline formula cases and all 13 renderer expectations from
item (B)/(C), running left-to-right splicing and `Related:`-before-splices to
confirm the ordering locks really do catch those mistakes, and checking every
verbatim line and column against the shipped M27 scanner. It found **five more
gaps that a wrong-but-plausible implementation would have walked through**, and
six weaker ones. All eleven are fixed:

1. **No test proved that a *completing* preview writes zero bytes** — in
   either verb. `test_mv_dry_run_names_every_planned_rewrite` checked only the
   two move endpoints, and **every** `_m28_snapshot` lock in the archive file
   was on a *refusal* path. A Phase-6 preview that walked, built the plan,
   printed it, **applied the rewrites**, and then declined to rename would have
   passed. Whole-tree snapshots added to both completing previews.
2. **Item (G)'s last sentence had zero coverage** — "an archived document that
   is itself moved by `docs mv` gets class-2 rebasing of its own destinations".
   The corpus exercises the archived document only as a class-**1** referrer,
   so an implementation gating class-2 rebasing on `not doc.archived` — a very
   plausible reading of M3's read-only stance — passed everything.
   `test_mv_of_an_archived_document_rebases_its_own_destinations` closes it.
3. **`tab -> %09` was unpinned, and the round-trip lock is blind to it.**
   `_split_destination` is a *decoder*, not a tokenizer, so dropping any plain
   terminator but `%` or `#` from the encode table leaves the 72-cell round trip
   GREEN — measured. Tab was the one grammar-derived entry with no explicit
   assertion; it now has one, alongside the angle form's literal tab.
4. **The `column` field's VALUE was never asserted** — only
   `isinstance(int) and >= 1`. A serializer emitting `link.start` (a byte
   offset), the `[` column, or a 0-based column passed. The `mv --json` tuples
   now pin columns 16 and 59, verified against the scanner.
5. **Nothing proved the reported `<old-token>` is `link.raw`** rather than a
   re-derived canonical spelling. Every asserted `old` was a token whose raw
   form equals its canonicalisation. `movelink-nested`'s
   `../../sub/../root.md` is the one spelling in the corpus that separates
   them, and it is now asserted through `mv --json`.

The six weaker ones, also fixed: the frozen `none` rendering in `mv`'s
partial-state admission (`"Rewritten: "` was satisfied by a blank); the archive
side of the (F) pre-flight, which had no CLI test at all over a planned
**referrer**; `--quiet` on a *completing* archive (the existing lock is on a
refusal, which has nothing to suppress); R11's excluded-document limitation,
which was stated in `cli.md` and pinned nowhere; the `Related:`
declaration-order clause, which no fixture could distinguish from a sort;
`(E)`'s "one `atomic_write` per document, never two", which is unobservable
from the resulting bytes and now has a call-count spy; `plan_move`'s
`related_pairs` parameter, never exercised; `mv --json`'s `source` vs `path`
distinction, invisible when the argument is already canonical;
`test_mv_preview_record_equals_apply_record`, which passed on two empty arrays;
the apply-side strand ordering, checked only by membership; and the refusing
plan's leg-2 set, asserted only as non-empty. Three nits closed too: the
percent-first test did not distinguish first from last (both emit
`a%2520b.md` for `a%20b.md` — measured; it now uses a path carrying both a
literal percent and a real space), the `movelink-*` tree list is now
cross-checked against the directory so an eighth tree cannot be silently
unswept, and the bundled-skill assertion required `--dry-run` **or** `--json`
where it must require both.

That pass also confirmed three dimensions clean and said so with evidence:
every verbatim line and column matches the real scanner, no fixture makes a
test vacuous and every count reconciles; no contradiction exists between the
tests, item (J)/(K) and `cli.md` (em-dashes U+2014 on both sides, plural forms
matching); and the splicer, pipeline-order and no-op locks are genuinely
strong — left-to-right splicing produces visible corruption on the fixture, a
*string* no-op test instead of the semantic one fails
`test_dot_slash_spelling_is_never_normalised`, and running step 5 before step 4
fails `test_a_co_moving_pair_keeps_its_sibling_link_byte_identical`.

The baseline is restated accordingly: **1295 collected, 191 failed, 1104
passed** at the end of the audit (from 1283 / 180 / 1103), still exactly two
exception classes, still zero deleted test lines and zero removed ids against
`58955ef`. The fresh-eyes fold-in below takes it to its final
**1332 / 229 / 1103**.

## Fresh-eyes review fold-in — 2026-08-15

An independent fresh-eyes review of Step 1 returned **no blockers**. It
reproduced the baseline, re-derived the exception-class census, hand-recomputed
formula (B) against all seven `movelink-*` trees and every pinned line and
column, and judged the formula sound. It returned five should-fix items and
three nits; all eight are folded in, together with the operator's answers to
the three items the same-instance audit had surfaced.

### Should-fix

- **S1 — the frozen contract contradicted the frozen formula.** `cli.md`,
  *Out of scope* and Q4's binding resolution all said an already-**broken**
  destination is never touched, but formula (B) exempts only **escaping**
  targets, so a contained-but-broken destination inside a **moving** referrer
  runs through steps 4–6 and is rebased — which is what
  `tests/test_move_links.py` correctly pins, because the planner is pure and
  cannot know a target is missing. Q4's literal wording is *unimplementable*
  in the frozen architecture, and the frozen architecture is right: the only
  way to honour it would be a filesystem probe inside the planner, destroying
  the hermeticity D4 and (L) exist to guarantee. A Phase-6 implementer reading
  only `cli.md` — which ships in the bundled skill — would have implemented the
  opposite of the pinned behaviour. Recorded as **amendment 4**, with `cli.md`
  and *Out of scope* reworded to say a contained-but-broken destination in a
  moving document is rebased to the same, still-broken target, never repaired
  and never re-aimed. No test flipped.
- **S2 — whether a moving member appears in `MovePlan.rewrites` was
  undefined**, and three frozen statements disagreed. (L) now states it: a
  moving member is **always** present, with `new_text == original` when nothing
  changed — which makes (E)'s "== `original` when nothing changes" reachable
  and (I)'s mv execution step total, instead of undefined in the common case
  (`docs mv a.md b.md` with no body links and no self-edges). Two new locks:
  the moving document is in the plan even when unchanged, and
  `apply_move_plan` **never** writes it — the latter needed a plan whose moving
  document has real bytes to write, because in every earlier test it happened
  to have none, so an implementation that wrote moving members passed.
- **S3 — leg 2's free-form-verb and canonical-target rules were unpinned**,
  and both plausible wrong implementations were GREEN across the whole suite:
  iterating `RECIPROCAL_VERBS` (which is how `docs relate` is written) misses
  `references:`, and testing `T in moves` without canonicalising (which is how
  `rewrite_related_refs` matches, per M26 — Q5) misses `./plan.md`. Every
  strand fixture used a recognised verb and a canonical spelling. Fixed at both
  levels: a new pure-seam lock over a referrer declaring `references: plan.md`
  and `pairs-with: ./plan.md`, and a `references: ./plan.md` bullet added to
  `movelink-strand`'s `live-child.md` so the CLI and the `strands` array see it
  too — which incidentally makes that document contribute an orphan **and** a
  strand, demonstrating that the two legs partition the graph by *edge*, not by
  document.
- **S4 — `docs mv`'s "no `--json` record on a refusal" had no lock.** Every mv
  refusal test asserted `stdout == ""` *without* `--json`, so a build that
  emitted a record on refusal satisfied them. `--json` added to the
  unwritable-referrer refusal.
- **S5 — two shipped `docs mv` stderr lines are re-spelled** (the `mv: ` prefix
  added, the trailing `(<N> reference(s) rewritten)` count dropped) and item
  (J)'s preamble called every line in it "new". Nothing goes RED, because no
  test pins them — which is exactly why an adopter parsing `docs mv` stderr
  would break silently at 2.0. Recorded in (J) and added to the Phase-7
  CHANGELOG / upgrade-note follow-through.

### Nits

- **N1 — three stale counts in this log**, the artifact Phases 5–10 trust: the
  phase-progress row's exception census, a `--co` figure the audit had already
  superseded, and "the 16 new GREEN ids" against an arithmetic and a table that
  both said 17. All three corrected, and every count in this file now derives
  from the same measured run.
- **N2 — `test_an_already_broken_destination_is_left_as_written` was
  mislabeled**: neither end moves in its fixture, so the no-op rule alone
  satisfies it and it locked nothing about Q4. Renamed to
  `…_in_a_stationary_document_is_untouched` and its docstring now points at the
  sibling that carries the half Q4 actually had to decide.
- **N3 — (I)'s mv execution order had an undocumented failure mode.** The
  moved document's rebased text is written to its **old** path before the
  `replace`, so a `replace` that raises leaves that path holding text rebased
  for a directory the file is not in. (I) now states which clause it lands in:
  under `Moved:` iff the `replace` succeeded, under `Rewritten:` otherwise.

### Operator answers to the three surfaced items

1. **The encode-set residuals — split decision.** The **colon** case is
   **closed here**, not deferred, and the argument is the one the contract
   already accepts one clause earlier for `#`: the emitted token re-classifies
   as `scheme`, M27 stops validating it, and `docs check` never reports the
   link the move just killed — a **silent** failure, which is the failure class
   M28 exists to prevent. Applying that principle to `#` and not to `:` was
   internally inconsistent, and the inconsistency was the finding. The cost was
   an artifact of framing the fix as a blanket table entry: `_SCHEME_RE`
   anchors at `^` and `/` is not in its character class, so a **first-segment**
   rule closes it at **zero** cost to `sub/a:b.md`. Item (C) now states the
   renderer **post-condition** `classify_destination(new_raw) == "local"` as
   the mechanism, with a complete proof, and four new locks pin it. The
   whitespace residual stays *Follow-ups* item 7 — it fails *loudly*, so
   `docs check` reports it.
2. **The check-order split stands.** One overstatement corrected: the
   `--cascade-only`-selects-nothing consequence manifests only when the tree is
   **also** malformed, so the message-precedence inversion alone carries the
   justification. And the previously-unwritten cost is now **named in
   `cli.md`**: the preview does not preview the write path's *permissions* — a
   plan whose planned referrer is unwritable previews at exit 0 and prints the
   plan, while the write refuses at exit 2 at step 8c. Defensible, since a
   preview writes nothing, but it is the same shape as M26 — *Follow-ups*
   item 2, so it is stated rather than left to be discovered.
3. **Spec ahead of code — accepted**, with one addition: `test_mv_help`
   asserted only that `old` and `new` appear, far too weak to notice that
   `docs mv --help` is behind `cli.md`. It now asserts `--json`, which makes it
   the **one** pre-existing id that is RED at this baseline — deliberately, by
   operator decision, and it converts Phase-7 follow-through item 2 from a
   promise into a lock.

### Verification

- `git diff --stat 58955ef -- src/docs_cli/cli.py` — **empty**.
- `.venv/bin/python -m pytest tests/ -q --co` — **1332 collected**, 0
  collection errors.
- `.venv/bin/python -m pytest tests/ -q` — **229 failed, 1103 passed**;
  exactly two exception classes (193 `AttributeError`, 36 `AssertionError`).
- `comm -23 old new` — **0** ids removed; `comm -12 failed old` — **1**, and it
  is `test_mv_help` by operator decision.
- `git diff --numstat 58955ef -- 'tests/*.py'` — **0** deleted lines.
- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean; `.venv/bin/docs check --root docs` —
  exit 0; both bundled mirrors byte-identical.

### Checked clean

- Deliverable 1 — the only deliverable in this step's phase range — is
  genuinely met and ticked; deliverables 2–10 and every success criterion are
  Phase 5+ outcomes and stay unticked, on M27's precedent.
- No placeholder, `NotImplementedError`, TODO or commented-out code anywhere
  in the step's diff.
- Every frozen `--json` key set agrees between `cli.md`, item (K) and the
  tests, in order: `archive` at `primary, date, scope, reason, candidates,
  rewrites, strands, dry_run, applied, index_refreshed`; `mv` at `old, new,
  rewrites, dry_run, applied, index_refreshed`; `rewrites[]` at `path, line,
  column, old, new`; `strands[]` at `path, target, kind, verb, line`.
- Every other line of item (J) is asserted verbatim somewhere in the suite.
- `cli.md`'s check-order sub-steps 8b / 8c / 8d match item (I); the `mv` and
  `archive` exit tables agree with the global exit-code table.
- Both bundled mirrors byte-identical; both specs at **0** occurrences of the
  three forbidden substrings; the frozen dogfood INDEX snapshot identical to
  `docs/INDEX.md`; `docs check --root docs` exit 0; every doc edited this step
  bumped via `docs touch`.
- `git diff --numstat 58955ef -- 'tests/*.py'` — **0** deleted lines; the diff
  contains only M28 work.
- Lint, format and types clean tree-wide; one commit per phase on
  `m28/phases-1-4` following the project's convention.

### Surfaced for the operator (not auto-decided)

1. **The two encode-set residuals** (item (C) › *Known residuals*,
   *Follow-ups* item 7). The frozen set is the grammar-derived minimal one, and
   two inputs fall outside it: a path component carrying whitespace other than
   space or tab, and a **colon in the first path segment**, which would make
   `classify_destination` read the emitted token as `scheme` and silence a link
   that worked before the move. Neither is reachable from a filename this tool
   creates, and Phase 2 asserts nothing about either, so closing them later
   flips no test — but closing the colon case costs `%3A` in every legitimately
   colon-bearing destination, which is an intent decision.
2. **The check-order refinement in item (I).** The Step-1 plan put the
   whole-tree walk at 5b for **both** paths; the frozen contract puts it at 5b
   for the preview and at **8** for the write path, because the plan's ordering
   would have silently inverted the message precedence `cli.md` freezes and
   turned a `--cascade-only` write selecting nothing from exit 2 into exit 1.
   This *preserves* M26's frozen behaviour rather than changing it, but it is a
   deviation from the plan of record and should be seen.
3. **`cli.md` describes Phase-6/7 behaviour ahead of the code** — the
   `docs mv` heading advertises `[--json]`, and the M28 block specifies
   rewrites that no verb performs yet. This is the M26/M27 precedent for
   Phases 1–4 (the spec *is* the frozen contract), recorded here rather than
   "fixed", so it is a deliberate state and not an oversight.

## Phase 5 — Update Base Interfaces — 2026-08-15

### Objective

Land every symbol in item (L) except `_print_move_lines` as pure code, so all
193 `AttributeError`s become GREEN and **no verb changes** — the CLI locks must
stay honestly RED at the seam rather than half-wired.

### Actions taken

Three pure **insertions** into `src/docs_cli/cli.py`; not one existing line
was edited.

| Where | What |
|---|---|
| *Vocabulary*, after `MAX_DESTINATION_PAREN_DEPTH` | `MOVE_STRAND_KINDS = frozenset({"related", "body-link"})` |
| *Models*, after `BodyLink` | the four frozen records — `LinkRewrite`, `DocRewrite`, `Strand`, `MovePlan` — verbatim from item (L) |
| a new banner section after `body_link_findings` | `render_destination_token`, `plan_body_link_rewrites`, `splice_body_links`, `plan_move`, `preflight_move_plan`, `apply_move_plan`, `move_plan_to_json`, plus the two module-level encode tables |

The section sits **before** `_is_archived_rel` (which `plan_move` calls) and
after the scanner it consumes. That forward reference is established practice
in this file — `_plan_relate_edit` does the same — and the alternative would
have been to move an M26 helper for no behavioural reason.

### Decisions worth calling out

- **The colon post-condition is applied AFTER the escape table, on the first
  path segment only.** Applying it before would let the table's `%` rule
  double-encode the `%3A` the renderer itself just wrote. Segment splitting is
  safe on the *encoded* string because no escape in either table contains a
  `/`, so the boundary computed there is the boundary of the decoded path.
- **`plan_move` derives body-link strands from the planned rewrites rather
  than re-scanning**, and the equivalence is provable rather than assumed: a
  strand source never moves, so `old_target in moves` implies
  `new_target != old_target`, which means the no-op test cannot fire and a
  `LinkRewrite` therefore exists. Re-scanning would have been a second walk
  over the same text for the same answer.
- **`preflight_move_plan` runs its three proofs per `DocRewrite` in plan
  order**, in item (F)'s order, rather than as three whole-plan passes. Item
  (F) lists the proofs in an order, and a per-document loop is what makes that
  order observable; the writability proof is skipped for a document the plan
  does not write, exactly as (F) scopes it ("the documents the plan will
  **write**").
  - Consequence, recorded rather than discovered: with span-match ahead of
    overlap, `test_overlapping_spans_refuse_rather_than_corrupt`'s widened
    span trips the **span-match** proof first. The test asserts `exit_code ==
    2` and not the message, so it holds either way, and the frozen order is
    what decided it. The overlap proof stays reachable on its own (two
    planned spans that both still match their text and still overlap).
- **`MovePlan.moves` snapshots the caller's mapping** (`dict(moves)`), so a
  plan cannot be mutated out from under `apply_move_plan` by a caller that
  keeps editing the dict it passed in.

### Verification

- `.venv/bin/python -m pytest tests/test_move_links.py -q` — **194 passed**
  (the whole pure seam, from 1 passing at baseline).
- `.venv/bin/python -m pytest tests/ -q` — **36 failed, 1296 passed**, exactly
  the Phase-4 `AssertionError` set; `pytest --tb=line | grep -c AttributeError`
  → **0**. The two exception classes are down to one.
- `git diff -U0 58955ef -- src/docs_cli/cli.py` — **three** hunks, all pure
  insertions at lines 144, 775 and 2960; `git diff 58955ef` touches no line
  inside `_cmd_mv` or `_cmd_archive`.
- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).

## Phase 6 — Implement Offline/Core Path — 2026-08-15

### Objective

Wire the Phase-5 planner into both verbs under item (I)'s check orders, without
relaxing a single Phase-2 lock.

### Actions taken

**`_cmd_mv` — inverted (item (I)).** `<old>` is a file (1) → `<new>` exists (1)
→ root/config (2) → both under root (2) → **the whole-tree walk + `plan_move`**
→ **5b the preview** (prints, `--json`, exit 0) → the rewrite-plan pre-flight →
execution: the moved document's planned text to its **old** path, then
`replace`, then `apply_move_plan`, then one `_refresh_index`. The M14 (A1)
pre-flight walk is not a second walk — it *is* the plan walk, which is why the
inversion costs nothing.

**`_cmd_mv` — the R9 partial-state admission.** `_mv_partial_state` renders
M26's shape extended by a `Rewritten:` clause. The moved document lands under
`Moved:` iff the `replace` succeeded and under `Rewritten:` otherwise, so a
`replace` that raises names the one document holding text rebased for a
directory it is not in.

**`_cmd_archive` — steps 5b / 8b / 8c / 8d.** `predicate` hoisted to just after
`load_config`; a `_plan_rewrites()` closure shared by the preview (at 5b) and
the write path (at 8) so both build the plan from the same walk with the same
failure mapping (malformed → 1, unreadable → 2); `preflight_move_plan` at 8c;
leg 1's refusal at 8d, printed even under `--quiet`; then execution.

**One write per member.** `_archive_one` gained `text: str | None = None` and
`apply_archive_plan` gained `texts: Mapping[str, str] | None = None`, so a
moving member's archive metadata edits are layered on **top of** its planned
text instead of a re-read. Without this a moving member is written twice,
violating (E)'s "never two". Both defaults are the pre-M28 behaviour, which is
what keeps `tests/test_archive_plan.py`'s direct calls untouched.

**`_archive_move_map` / `_archive_related_pairs`** extracted as pure helpers.
The pairs were previously built *inside* `apply_archive_plan`, i.e. only after
execution — a chicken-and-egg for step 8b, which needs them at plan time.
`apply_archive_plan` now returns `_archive_related_pairs(plan)`, so its
contract and its M26 unit lock are unchanged.

**`_rewrite_referring_edges` deleted** (43 lines), superseded by
`apply_move_plan` on M26's `_cascade_set` precedent. Its M18 archived-doc gate
becomes unnecessary *by construction*: under the new pipeline an archived
document's text changes iff a `Related:` target or a body-link destination
resolved into `moves` — exactly rule (G). Two docstrings that named it now name
`rewrite_related_refs` / `_archive_related_pairs`.

### Decisions / issues

- **`preview only — nothing was written` moved out of `_print_archive_lines`
  into `_cmd_archive`**, still gated on `cascade and dry_run` so M26's
  behaviour is byte-identical, and emitted **last** — a preview now ends on the
  sentence that says nothing happened, rather than burying it above the rewrite
  and strand lines.
- **The rewrite-counts footer prints unconditionally; leg 2's count line does
  not.** R3 read literally for the footer (it is the skimming aid, and `0
  destination(s) in 0 document(s) rebased` is a real answer); leg 2's count is
  the summary *of a list*, and `0 still-active inbound reference(s)` on every
  archive would be pure noise.
- **`--quiet` suppresses the leg-1 PREVIEW pair**; only the two write-path
  refusal lines survive it. That is item (L)'s split — the preview pair is a
  report, not a refusal — so the pair lives in `_print_move_lines(dry_run=True)`
  (caller-gated on `not --quiet`) and the refusal pair lives in `_cmd_archive`.
- **A `docs mv` INDEX-refresh failure now mirrors `archive` exactly**: `docs:
  INDEX refresh failed: <err>`, a record with `applied: true,
  index_refreshed: false`, exit 2. Symmetry between the two verbs is the point
  of one shared schema, and otherwise `index_refreshed`'s documented `false`
  value is unobservable on `mv`.
- **`_cmd_mv` tolerates a missing moving-member `DocRewrite`.** When
  `[exclude]` / `.docsignore` hides the moved document from the walk it has no
  plan entry, so the pre-`replace` write is skipped and the file is simply
  renamed — today's behaviour exactly, and R11's exclusion contract honoured.
  Synthesising an entry would violate it. `_mv_member_changes` names that
  condition once so both the execution path and the admission agree.
- **`mv --json`'s argparse flag landed HERE, not in Phase 7.** `_cmd_mv`'s
  record emission reads `args.json`, so the one-line declaration cannot be
  separated from the behaviour without a `getattr` shim. Named rather than
  quietly done; the rest of the wrapper layer (both descriptions, the bundled
  skill, `CHANGELOG.md`, `feedback-log.md`, the two contract-mandated test
  expected-value updates) stayed in Phase 7.
- **`plan_move` is handed `root`, not `root.resolve()`, by `_cmd_mv`.** `walk`
  yields paths under the *unresolved* root, and `_root_relative` falls back to
  the bare filename for a path it cannot relativise — so passing the resolved
  root would silently mis-name every `sub/x.md` referrer whenever `--root` is
  given relatively.

### Verification

- `.venv/bin/python -m pytest tests/ -q` — **5 failed, 1327 passed**. All 17
  `mv` and 17 `archive` M28 behaviour ids are GREEN; every remaining RED is a
  Phase-7 item: `test_archive_json_preview_record_shape` and
  `test_archive_json_apply_record_has_the_same_key_set` (the
  `_JSON_TOP_LEVEL_KEYS` expected-value update),
  `test_archive_json_of_a_primary_only_archive_lists_candidates_as_not_selected`
  (re-pointed fixture) and the two bundled-skill locks.
- The primary-only fixture's failure is **correct behaviour**, verified by
  hand: `archive-neighborhood`'s `milestone-impl.md` is still active and
  declares `child-of: milestone.md`, so archiving `milestone.md` alone strands
  a live child and leg 1 refuses at exit 2 with zero bytes written. That is the
  harm leg 1 exists to prevent, reproduced by an M26-era fixture.
- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).
- `grep -rn 'docs: would move\|docs: moved\|reference(s) rewritten' tests/
  docs/cli.md src/docs_cli/skill/ CHANGELOG.md` — **no hits**, re-confirming
  item (J)'s claim that no test pins the two re-spelled `docs mv` lines.

## Phase 7 — Update Tool/Wrapper Layer — 2026-08-15

### Objective

Reconcile every parallel surface with the behaviour Phase 6 landed, and take
the suite fully GREEN.

### Actions taken

- **argparse.** `mv_p`'s `help` and `description` now name the body-link
  rebasing, the plan-before-move contract and both new flags; `archive_p`'s
  names the rebasing **and** the leg-1 refusal with its exit code. `mv --json`
  itself landed in Phase 6 (see that section's note).
- **Bundled skill.** `SKILL.md`'s `docs mv` row gains `--dry-run`, `--json`
  and the body-link rewrite; its `docs archive` row gains the rebasing, the
  `child-of` refusal with its repair ("archive the child first, or widen the
  scope"), and the leg-2 report. `references/use-cases.md`'s line 24 —
  *"Prose markdown links in bodies are not rewritten — that's a deliberate
  scope cut"* — was **false as of Phase 6** and is replaced; its archive row
  and its M27 upgrade paragraph now say the repair loop is a one-time upgrade
  chore rather than something every move re-creates.
- **`CHANGELOG.md`**, under the existing `UNRELEASED` heading: three `Added`
  entries (the rewrites, `mv`'s preview + `--json`, `archive --json`'s two new
  keys), four `Changed` entries — one **BREAKING** (the leg-1 refusal), plus
  prose writes, the `mv` inversion, and previews adopting plan-construction
  failures — and the three-part upgrade note.
- **`docs/feedback-log.md`**: a dated resolution bullet on the issue #1 entry
  recording that finding 4's `--report-links` was declined as a design and
  adopted as the plan record on both verbs, and that finding 1's routed
  predicate was amended to leg 1 + leg 2 because the literal form refuses this
  repository's own closeout.
- **`docs/cli.md` / `docs/convention.md`**: verified, not rewritten — Phase 1
  landed both (`convention.md` carries the widened M18 exception and the
  reconciled M27 — D6 sentence; `cli.md:568-813` carries the whole M28 block
  plus the amended check order, the widened `--json` schema and the three exit
  tables). Re-verified against the shipped `--help` text by hand.

### The two test edits, and why each is a STRENGTHENING

Named explicitly, because an unexplained test edit inside a no-regression
claim is what makes such claims worthless.

1. **`tests/test_cli_archive.py::_JSON_TOP_LEVEL_KEYS` gains `"rewrites",
   "strands"` after `"candidates"`** — a contract-mandated expected-value
   update. Item (K) freezes the widening at exactly those two keys in exactly
   that position and forbids the escape hatch of omitting an empty array, so
   the two ids that assert this list (`test_archive_json_preview_record_shape`,
   `test_archive_json_apply_record_has_the_same_key_set`) now pin a **ten-key
   closed set** where they pinned an eight-key one. The assertion is
   **strengthened**, never weakened: every key it demanded before it still
   demands, in the same relative order, plus two more.
   `tests/test_archive_plan.py::_TOP_LEVEL_KEYS` is deliberately **untouched**,
   which the `move_plan: MovePlan | None = None` keyword default is what makes
   possible.
2. **`test_archive_json_of_a_primary_only_archive_lists_candidates_as_not_selected`
   is re-pointed from `archive-neighborhood` to `_two_relation_tree`.** Its
   subject — the Q14 claim that a plain `docs archive FILE --json` carries the
   WHOLE candidate set — is preserved exactly, on the **apply** path
   (`--dry-run` was rejected as a fallback: it would weaken an apply-path lock
   into a preview-path one). The original tree's refusal is **correct
   behaviour, not a defect**: `archive-neighborhood`'s `milestone-impl.md` is
   still active and declares `child-of: milestone.md`, so archiving
   `milestone.md` alone archives a parent out from under a live child —
   precisely the harm leg 1 exists to prevent. That scenario is too good a
   leg-1 witness to lose, so it is now pinned in its own right by the **new**
   `test_archive_primary_only_leg_1_refuses_on_a_live_child`, on an M26-era
   tree with no body links anywhere in it — which additionally proves leg 1
   does not depend on the `movelink-*` family.

Net test-line accounting: `_JSON_TOP_LEVEL_KEYS` +2 value lines (+8 comment
lines), the re-pointed id's body rewritten in place, and one new id added.
**No test id was removed and no assertion was relaxed.**

### Verification

- `.venv/bin/python -m pytest tests/ -q` — **1333 passed, 0 failed**
  (1332 + the new leg-1 lock).
- `docs mv --help` / `docs archive --help` read back against `cli.md` ›
  *`docs mv`* and *Safe explicit archive selection* — agree.
- `cmp docs/cli.md src/docs_cli/skill/references/cli.md` and
  `cmp docs/convention.md src/docs_cli/skill/references/convention.md` — both
  identical.
- `grep -rn '](\.\./' src/docs_cli/skill/` — no hits;
  `grep -c '](\.\./' docs/cli.md docs/convention.md` — **0** and **0**
  (item (M)).
- `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — no difference
  (every doc edited this step already carried `Updated: 2026-08-15`).
- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).
- No `pyproject.toml` or version change (M25 — D6): the package stays `1.8.0`.

## Phase 8 — Run Tests (GREEN) — 2026-08-15

### The gate

| Command | Result |
|---|---|
| `pytest tests/ -q --co` | **1333 collected**, 0 collection errors |
| `pytest tests/ -q` | **1333 passed, 0 failed** |
| `pytest tests/ -q -rxXE` | 0 XFAIL / 0 XPASS / 0 ERROR |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 48 files already formatted |
| `mypy src/ tests/` | no issues found in 49 source files |
| `docs check --root docs` | no violations found (exit 0) |
| `cmp docs/cli.md src/docs_cli/skill/references/cli.md` | identical |
| `cmp docs/convention.md src/docs_cli/skill/references/convention.md` | identical |
| `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` | no difference |
| `grep -c '](\.\./' docs/cli.md docs/convention.md` | **0** and **0** (item (M)) |
| `git diff --stat 58955ef -- pyproject.toml` | empty — no version bump (M25 — D6) |

### Mechanical no-regression proof against `58955ef`

Phase 4's method, repeated: a throwaway `git worktree` at the pre-M28 commit,
ids collected with `pytest -q --co` on both sides, compared with `comm`.

| Measure | Value |
|---|---|
| Pre-M28 ids | **1087** |
| Current ids | **1333** |
| `comm -23 old new` — ids **removed** | **0** |
| `comm -13 old new` — ids added | **246** |
| Pre-existing ids failing | **0** — the suite has no failures at all, so every one of the 1087 is present *and* GREEN |

`git diff --numstat 58955ef -- 'tests/*.py'`:

| File | + | − |
|---|---|---|
| `tests/test_cli_archive.py` | 594 | **11** |
| `tests/test_cli_check.py` | 46 | 0 |
| `tests/test_cli_mv.py` | 441 | 0 |
| `tests/test_move_links.py` | 1335 | 0 |
| `tests/test_skill.py` | 59 | 0 |

**All 11 deleted lines are inside
`test_archive_json_of_a_primary_only_archive_lists_candidates_as_not_selected`** —
the docstring's obsolete `RED reason:` line, the three lines that built and
ran the old invocation, and the seven-line expected candidate list — replaced
in place by the `_two_relation_tree` equivalent. The
`_JSON_TOP_LEVEL_KEYS` edit deletes **nothing**: the list gained two entries
and a comment block, so it is a pure insertion. Both edits are justified in
Phase 7's *The two test edits* section, and both are **strengthenings or
equal, never weakenings**:

- the top-level key set went from an eight-key closed assertion to a
  **ten**-key one, every original key still demanded in the same relative
  order — and item (K) forbids the escape hatch of omitting an empty array,
  so a ten-key pin is the only honest expected value;
- the re-pointed lock keeps its subject (a plain `docs archive FILE --json`
  carries the whole candidate set) and keeps observing it on the **apply**
  path; the coverage its old tree provided is not lost but *promoted*, into
  the new `test_archive_primary_only_leg_1_refuses_on_a_live_child`.

Total changed test lines: **2475 added, 11 deleted**, across five files, zero
ids removed — the per-file table above sums to exactly that. Both figures are
measured at the Phase-8 commit `570499c`; re-run today they read **2666 added,
11 deleted** over 1338 ids, because the Step-2 audit added five more locks
afterwards. The deleted count is the one that matters and it has not moved.

## Phase 9 — Integrate / Accept / Dogfood — 2026-08-15

### Method

**The live `docs/` tree was never written to.** Every flow ran as
`cp -a docs "$SCRATCH/<tag>"` followed by a `--root "$SCRATCH/<tag>"`
invocation, and `git status --short` was empty before and after the whole
phase. The "before" column is not quoted from the setup record: the pre-M28
`cli.py` was checked out into a throwaway `git worktree` at `58955ef` and run
against a copy of the **same** current tree, so both columns measure the same
73 documents / 3.1 MB.

### The flows

| # | Flow | Before (pre-M28 binary) | After (M28) |
|---|---|---|---|
| E1 | `docs mv plan.md milestone-plan.md` | exit 0, then `docs check` exit 2 with **42** `broken-body-link` across **14** documents | exit 0, `42 destination(s) in 14 document(s), 35 Related: bullet(s)`, `docs check` exit **0** |
| E2 | `docs archive m17-pypi-publish-impl.md --date …` | exit 0, then **13** `broken-body-link` (7 of them inside the archive subtree) | `13 destination(s) in 7 document(s) rebased`, **4** of the rewrite lines naming `archive/…` referrers, `docs check` exit **0** |
| E3 | `docs archive m25-…md --cascade-only 'm25-*' --reason …` | exit 0, then **6** `broken-body-link` | exit 0, `6 destination(s) in 2 document(s) rebased`, **11** leg-2 strands, **0** orphans, `docs check` exit **0** |
| Plan A | `docs archive m26-…md --cascade-only 'm26-*' --reason …` (the E7 census invocation) | — | exit **0**, **0** orphans, `8 destination(s) in 2 document(s) rebased`, **16** still-active inbound references — **8 `Related:` + 8 body links from 7 distinct referrers**, reproducing the setup census exactly — `docs check` exit 0 |
| Plan B | `docs archive m27-…md --cascade-only '*'` (issue #1's harm) | — | exit **2**, **5** orphans named with both ends, stdout **0 bytes**, tree SHA-256 unchanged |
| Plan C | `docs archive plan.md` | — | exit **2**, **6** orphans, stdout **0 bytes**, tree SHA-256 unchanged |
| Preview parity | plan B with `--cascade-dry-run --json` | — | exit **0**, record emitted (10 keys, 277 rewrites, 49 strands), leg-1 verdict **reported** (`would strand …` / `5 still-active child(ren) would be stranded`), tree SHA-256 unchanged |
| `--quiet` refusal | plan C with `--quiet` | — | exit 2, **7** stderr lines, **all 7** refusal lines and **0** ordinary prose |
| Idempotence | E1 forward, then `docs mv milestone-plan.md plan.md` | — | **every file byte-identical**, `INDEX.md` included, `docs check` exit 0 |

### The E1 diff, audited line by line

77 lines changed (`-77 / +77`) across 40 documents plus `INDEX.md`. **Every
one of the 154 changed lines contains the string `plan.md`** — i.e. every
change is a `Related:` bullet or a body-link destination naming the moved
document. Nothing else moved: no prose, no `Updated:` value, no heading, no
metadata field. 77 = 42 destinations + 35 bullets, matching the summary line
the verb printed.

### Record parity, measured

Invoked with **identical argument spellings** (so `source` cannot differ for a
trivial reason), the preview and apply records differ in exactly
`['applied', 'dry_run', 'index_refreshed']` — for **both** verbs. `rewrites`
compares equal element-for-element (42 records on `mv`, 8 on `archive`), as
does `archive`'s `strands` (16 records), and the two verbs' `rewrites` record
key sets are identical — which is what one shared serializer buys.

### Runtime

Mean of three runs each, same tree, same machine:

| Flow | pre-M28 | M28 | added |
|---|---|---|---|
| `docs mv` | 317 ms | 397 ms | **+80 ms** |
| `docs archive` (solo) | 140 ms | 253 ms | **+113 ms** |
| `docs mv --dry-run` | 74 ms | 195 ms | **+121 ms** |

The preview's is the largest relative jump and the expected one: it walks and
plans now, where 1.x printed one line without reading the tree. Every flow is
far inside the "well under 1 s" bound.

### Deviations from the plan of record, and why each is correct

- **Plan B produced 5 orphans, not the 6 the setup census predicted.** The
  census counted `child-of: plan.md` declarers without applying item (H)'s
  plan-member exemption; `m27-markdown-body-link-validation.md` is the primary
  of this invocation, so it is a plan member and cannot be stranded by it. The
  exemption is contractual and locked by
  `test_leg_1_ignores_a_child_of_declared_by_a_plan_member`. Plan C, where
  only `plan.md` moves, produces the full **6**, matching the census exactly.
- **E3 reported 11 leg-2 strands, not 16.** 16 is plan A's number — the E7
  census measured `--cascade-only 'm26-*'` — and plan A was run separately and
  reproduced **exactly** 16 (8 + 8, from 7 referrers). E3 archives the *m25*
  pair, a different neighbourhood.

### Verification

- `git status --short` — empty before and after; the live tree is untouched.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).
- Every refusal flow re-hashed with SHA-256 over the whole tree
  (path + bytes, sorted): identical to the pre-run hash.
- Both throwaway `git worktree`s removed; `git worktree list` shows only the
  repository itself.

## Phase 10 — Quality, Docs, Refactor — 2026-08-15

### The `/simplify` pass

Four changes, all behaviour-preserving, verified by the same 1333-test suite
before and after. Net **−18 lines** in `src/docs_cli/cli.py`.

| Change | Why it simplifies |
|---|---|
| `_cmd_mv`'s two near-identical `except` clauses collapsed into **one** `except OSError`, with the detail/`published` derivation moved into `_mv_partial_state` | The two handlers differed in exactly two expressions and repeated a nine-line `print(...)` call. Moving "which exception carries what" next to the message it produces puts that knowledge in one place and removes a whole branch from the execution path — 34 lines to 16 at the call site. |
| `_mv_member_changes` deleted; `moved` looked up **once** and reduced to `member_text: str \| None` | The helper existed only to avoid repeating a one-line test, and the caller then scanned `plan.rewrites` a *second* time to fetch the record it had just proven present. "The text the member needs written to its old path, or None" is one concept where there were three. |
| `archive_plan_to_json` restored to a **single dict literal** with a `**rewrite_section` splice | The `move_plan` parameter had turned one expression into a literal plus a conditional `.update()` plus three assignments. The splice keeps the key order the schema freezes and makes "the shared section goes here" visible in the shape of the code. |
| The two adjacent post-move `try` blocks in `_cmd_archive` merged into one | `apply_archive_plan` and `apply_move_plan` fail identically — M14 (A4): exit 2, no record — so two handlers printing the same line were duplication. The `_refresh_index` handler stays **separate**, deliberately: it is the one post-write failure that still emits a record, which is the M26 split the log records. |

Two smaller ones in the same pass: the overlap proof in `preflight_move_plan`
became one `any(...)` over adjacent span pairs, and `_print_move_lines`'
preview block lost a redundant `if plan.orphans` by folding it into the guard.

Nothing else was touched. `_archive_move_map` and `_archive_related_pairs`
were considered for collapsing and **kept**: they name the single most
misunderstood distinction in the milestone — the move map is canonical and
feeds the destination half, the pairs are alias-expanded and feed the
`Related:` half — and inlining them would hide it. `_plan_rewrites`' `MovePlan
| int` return was likewise kept: it is this file's established idiom
(`_resolve_managed_root`, `_resolve_relate_endpoint`), and consistency beats
novelty.

### Documentation closed

- **`docs/architecture.md`** — the `archive` pipeline diagram still ended in
  `_rewrite_referring_edges`, a function that no longer exists; it is re-drawn
  through steps 8 / 8b / 8c / 8d and `apply_move_plan`, with the preview's 5b
  split named. A new **`mv` (M14, inverted by M28)** section gives that verb a
  pipeline diagram it never had. A new *Move-safe body-link rewrites (M28)*
  subsection sits under the M27 body-link block, which already
  forward-referenced M28 as the span consumer.
- **`docs/test-strategy.md`** — the `movelink-*` family joins *Fixture
  sources* (seven trees, one semantic each, with the line/column numbers named
  as contract and the reason exotic grammar and mutation cases stay inline),
  and *Critical paths* gains two rows: a coordinated move leaves `docs check`
  clean with a destination-token-only diff, and leg 1 refuses with zero bytes
  **while a legitimate closeout completes**.
- **`docs/plan.md`** and **`docs/status.md`** — M28's narrative, table row,
  roadmap bullet, current-milestone block and *Next action* all record
  implementation-complete and hand the train to **M28a** and **M29**. M28
  stays `Lifecycle: active` until the M29 publish closeout.
- The **shipped use-case catalog** (`references/use-cases.md`) landed in
  Phase 7 with the rest of the surface, because its now-false "prose links are
  not rewritten" sentence was a correctness problem the moment Phase 6 shipped,
  not a Phase-10 polish item.

### Verification

- `.venv/bin/python -m pytest tests/ -q` — **1333 passed, 0 failed**, before
  and after the `/simplify` pass.
- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).
- `git diff --stat` for the `/simplify` pass — `src/docs_cli/cli.py` only,
  57 insertions / 75 deletions.

## Step-2 same-instance audit — 2026-08-15

Run against Phases 5–10 after the last phase and before returning, per the
ship-milestone consistency / completeness / accuracy checklist, in three
passes: one reading the code against the frozen contract, one reading the
documents against each other and against measured ground truth, and one
reading the code adversarially, reproducing every contract claim on throwaway
trees rather than reading for agreement. **Sixteen** issues found; all sixteen
fixed here. Four items are **surfaced** for the operator rather
than auto-decided, because each touches intent rather than accuracy.

### Issues found and fixed

1. **`convention.md` still carried Q4's PRE-amendment wording, which the code
   contradicts.** It said an *"external URL, an image, an autolink, raw HTML, a
   bare filename in a sentence, anything inside a fence or backticks, and a
   destination that was **already broken** or already escaping before the move
   are all byte-identical afterwards"*. **Amendment 4 (BINDING) reversed the
   broken half**: an already-broken but *contained* destination keeps its bytes
   only while its referrer stays put, and is **rebased to the same, still-broken
   target** when the referrer itself moves — which is what
   `test_a_moving_referrer_rebases_a_broken_destination_without_repairing_it`
   pins. The amendment named `cli.md` › *What a move never touches* and the
   milestone's *Out of scope*, both of which were reworded correctly in Phase 1,
   but it did **not** name `convention.md`, so that file slipped through. This
   is the exact failure mode amendment 4 was written to prevent, and
   `convention.md` ships **byte-identically inside the wheel**, so a reader of
   the bundled skill would have been told the opposite of the shipped
   behaviour. Reworded; the bundled mirror re-synced. Swept every other shipped
   surface (`cli.md`, `CHANGELOG.md`, `SKILL.md`, all four other bundled
   references, `cli.py`) for the same claim — no other occurrence.
2. **Two shipped `docs mv` behaviours were undocumented.** `cli.md`'s `docs mv`
   exit table and its compatibility-matrix row covered neither (a) an
   **unreadable** document met during the plan walk — new in Phase 6, where 1.x
   let the `OSError` escape as a traceback and the code now maps it to the same
   clean exit 2 `docs archive` uses — nor (b) the **INDEX-refresh failure**,
   whose message, record and exit code changed under Step-2 resolution 5. Both
   rows updated, and the `docs mv --json` section gained the INDEX-refresh
   paragraph mirroring `docs archive`'s. Mirror re-synced.
3. **Two locks the Step-2 resolutions required were missing.**
   - Resolution 4 explicitly asked for a lock on `--quiet` over a **preview**
     whose plan has orphans, noting that nothing in the suite exercised it.
     It did not get written during Phase 6. Added
     `test_archive_leg_1_preview_pair_is_suppressed_by_quiet`. This is the only
     place the item-(L) split between the preview pair (a report, suppressed)
     and the write pair (a refusal, never suppressed) is observable: the
     existing `--quiet` locks run on a refusal, which has no preview pair, and
     on a completing apply, whose plan has no orphans at all.
   - Resolution 5's `docs mv` INDEX-refresh behaviour was a **promise, not a
     lock** — exactly the state the operator rejected for `test_mv_help`.
     Added `test_mv_json_record_is_emitted_on_an_index_refresh_failure`,
     mirroring `test_archive_json_record_is_emitted_on_an_index_refresh_failure`
     and its `_readonly_root_tree` trick (documents in `w/`, the ROOT read-only,
     so every write lands and only the end-of-move `INDEX.md` write fails).
   - **Both were mutation-tested rather than assumed.** Reverting the code to
     the shape each forbids — hoisting `_print_move_lines` out of the
     `not --quiet` guard, and restoring 1.x's bare `docs: mv: <err>` +
     unconditional exit 2 — makes each new id fail and **leaves every other
     test green**, which is the proof that each closes a real gap rather than
     re-asserting something already covered.

4. **`README.md`'s verb table under-described both verbs.** `docs mv` still
   read *"Move + rewrite Related: references across the tree"*, with no mention
   of body links and neither new flag; `docs archive` did not mention the
   rebase. `README.md` is deliberately outside D8's surface-parity list, and
   neither line was *false* — but it is the project's front door, and the
   change it omitted is a **BREAKING** one. Two lines, adding nothing `cli.md`
   and the CHANGELOG do not already carry.

Suite: **1333 → 1335 passed**, still 0 failed.

### A second pass, over the documentation alone

The four above came from reading the code against the contract. A separate
pass read the *documents* against each other and against measured ground
truth, and found six more — none behavioural, all fixed here.

5. **A wrong headline number in this log's own no-regression proof.** Phase 8's
   *Total changed test lines* read **2486 added**; the per-file table directly
   above it sums to **2475**, and so does `git diff --numstat`. `2486 =
   2475 + 11` — the deleted lines had been added into the *added* total. The
   worst possible place for an arithmetic slip, because it is the one figure a
   reader re-derives to check the claim. Corrected, and the sentence now says
   it sums to the table.
6. **This log's `## Milestone completion summary` heading was destroyed when
   the audit section was inserted**, leaving the summary body running on from
   *Surfaced for the operator* item 2 — and the log's own `Progress:` bullet
   pointing at a heading that no longer existed. Both sibling logs (M25's,
   M27's) carry it as their final `##`. `docs check` cannot see this: it is
   prose, not a link. Reinstated.
7. **`status.md`'s current-milestone block rendered with its emphasis
   inverted.** The opening `**M28 — … is the current milestone.` was closed by
   the next `**`, so every headline fact — *all ten phases done*, *1335
   passed*, *M28a*, *M29* — rendered plain while the connective filler between
   them rendered bold. Restructured so the emphasis nests as intended.
8. **`status.md` said the rewrite-plan pre-flight runs "four proofs"; it runs
   three.** The fourth is item (F)'s first bullet, *"the document parses"*,
   which that bullet itself annotates as *already proven by the walk*.
   `architecture.md` and this log both said three. Corrected, with the
   parseability precondition named so the discrepancy cannot come back.
9. **`plan.md`'s surface-parity convention named only half the byte-identity
   gate** — `references/cli.md` ≡ `docs/cli.md`, omitting the
   `convention.md` half that `tests/test_skill_refs.py` and `CLAUDE.md` both
   enforce. Load-bearing, and not hypothetically: audit finding 1 above *was* a
   `convention.md` divergence shipping inside the wheel. Both halves now named.
10. **`docs/feedback-log.md`'s issue #1 entry still read as open at the top.**
    Finding 4 was marked *"owned by M28, pending"* and the `Status:` line said
    *"finding 4 is registered as M28"* — true when written, false now. The
    Phase-7 *Resolution* bullet supersedes them but sits **below**, so a
    top-down reader got the stale state first. Both markers now say
    implemented-and-unreleased and point down at the resolution.
11. **`m29-pypi-publish-2-0-0.md`'s drafted public reply stated the
    PRE-amendment predicate**, and would have been posted to a GitHub issue as
    fact. It said 2.0.0 *"refuses an operation that would leave a still-active
    document pointing at a newly-archived one"* and that this *"self-cancels
    for the legitimate case"* — the second being the exact sentence M28 setup
    measured to be **false** (E7: an ordinary closeout leaves 16 deliberate
    references), and the first describing a predicate M28 deliberately did not
    ship. The file's own guard note told the poster to rewrite **finding 4's**
    paragraph; it never named finding 1, which is the one that went wrong. Both
    paragraphs rewritten to the two legs that shipped, with the measurement that
    produced the split stated, and the guard note updated to record which
    paragraphs are now fact and which (finding 3's, awaiting M28a) are still
    intention.

### A third pass, adversarial, over the code against the contract

A separate pass read every item of the frozen contract against the shipped
code, reproducing each claim on throwaway trees rather than reading for
agreement. It confirmed items (B), (C), (E), (F), (G), (H), (I), (K) and (L)
clean — including a fuzz of the renderer, a per-path `atomic_write` count, and
a step-by-step walk of both check orders — and found five more issues, plus one
item that needs an operator decision (below).

12. **`cli.md` told the reader a move never rewrites 4-space-indented code. It
    does — and correctly.** The M28 block listed *"images, autolinks, raw HTML,
    reference uses, and 4-space-indented code"* among the exclusions, while
    **the same file** has said since M27 that there is *"no 4-space
    indented-code rule (M27 — Q3): a link indented four spaces … **is**
    scanned"*. **Reproduced**: a `    [indented](target.md)` block had its
    destination rewritten by `docs mv`, while the fenced and inline-code copies
    were untouched. D2's *rule* — "anything M27 does not validate, M28 does not
    rewrite" — was implemented exactly right; its *enumeration* was a statement
    of fact about M27 that M27 contradicts. This is the worst kind of doc bug:
    `cli.md` ships **byte-identically inside the wheel**, no test can see a
    false prose claim, and an agent was being told a code sample is safe from a
    move that silently edits it. `cli.md` now states the boundary in **both**
    directions and names the three real opt-outs (fence, backticks, backslash);
    the milestone's D2 bullet is corrected and the correction recorded as
    **amendment 5**, flagged as a factual correction rather than a decision.
    The CHANGELOG had it right all along ("fenced and inline code"), which is
    what identifies this as an authoring slip in exactly two places.
13. **`docs mv` could leave a directory behind while admitting it had moved
    nothing.** `mkdir(parents=True)` runs before `replace`, so a `replace` that
    raises left an empty destination directory *and* an admission reading
    `Moved: none. Rewritten: none. Not written: none.` — over a tree the call
    had in fact changed. `_archive_partial_state` prunes its dated directory
    for precisely this reason ("a refusal that promised zero mutation would
    have changed the tree"); `mv` has the same failure shape and now gets the
    same care, pruning only what this call created and only when the rename did
    not happen. Locked by `test_mv_failed_rename_leaves_no_directory_behind`
    and mutation-tested.
14. **Two shipped refusal strings were undocumented and used a shape no other
    refusal uses.** (F)'s span-mismatch and overlap refusals read
    `<rel>: <predicate>`, where every M25/M26 sibling reads `<rel> <predicate>;
    refusing before any write`. Item (J) left them unpinned deliberately, which
    is exactly how an operator-facing string drifts. Both normalised to the
    sibling shape, added to `cli.md`'s *Validate-all-first* section with a note
    on why they are defensive, and **pinned** by the two unit tests that
    previously asserted only the exit code.
15. **The overlap proof had no witness — the test named after it could not
    reach it.** `test_overlapping_spans_refuse_rather_than_corrupt` widens a
    span so it overlaps its neighbour, but widening also breaks that span's
    text match, and (F)'s order runs span-match **first** — so the overlap
    branch was unreachable code that no test distinguished from a `pass`. The
    existing test now asserts the message the *order* really produces (and says
    why), and a new `test_two_matching_spans_that_overlap_refuse` reaches the
    overlap proof with two `LinkRewrite`s over the same occurrence: both still
    match their text, so only overlap can refuse.
16. **A `./` destination is now pinned, because it looks like a bug.** A
    directory destination whose target becomes the referrer's own new directory
    relativises to `.`, and R7 reattaches the slash — `./`, the one emitted
    spelling carrying the leading `./` that (B) step 6 forbids elsewhere. It is
    required: the empty alternative classifies as `empty` and stops being a
    link at all, breaking (C)'s post-condition. Pinned so that "fixing" it
    cannot silently kill every such link.

Two further observations were examined and **accepted as correct**, recorded
here so they are not re-raised:

- **(F)'s span-match proof is a tautology in production.** The plan's
  `original` is the exact string the spans were scanned from, in the same
  process, so it can only fail for a hand-built `MovePlan`. `cli.md` words it
  as "still matches the text it was scanned from", which is what the code
  checks. It is a defensive invariant against a corrupting splice, and it is
  now documented as defensive rather than as protection it does not provide.
- **`plan_body_link_rewrites` calls `os.getcwd()`,** via `posixpath.relpath`
  on two relative paths. The cwd prefix cancels, so the emitted spelling is
  genuinely cwd-independent (pinned by
  `test_emitted_spelling_is_independent_of_the_process_cwd`) — but "no
  filesystem access of any kind" overstated it, and the Phase-2 purity lock
  cannot see it. The docstring now says exactly what the guarantee is: opens
  nothing, stats nothing, writes nothing, and the result is a function of the
  tree's bytes.

Suite: **1335 → 1338 passed**.

### Checked clean

- **The frozen message catalogue (item (J)) is byte-exact in three places.**
  All 16 lines were extracted programmatically from the milestone doc's fence
  and found verbatim in `cli.md`; every one was then rendered from the shipped
  CLI against fixture trees and compared by eye against the template.
- **Both check orders (item (I))** were walked step by step against the code.
  `_cmd_archive` runs 1 → 2 → 3 → 4 → 5 → 5b → 6 → 7 → 8/8b → 8c → 8d → 9, and
  `_cmd_mv` runs 1 → 2 → 3 → 4 → 5 → 5b → 6 → 7, exactly as frozen. The one
  structural change — hoisting `compile_exclude_predicate` to just after
  `load_config` so the preview and the write path share it — was proven
  behaviour-neutral: the compiler escapes every non-metacharacter through
  `re.escape` and has no raise path, so no refusal can change order because of
  it.
- **The renderer's two post-conditions, fuzzed.** 60,000 random paths × both
  delimiter forms × three fragment shapes: **0** round-trip failures and **0**
  delimiter drift. `classify_destination(new_raw) == "local"` failed only for
  inputs beginning with `/` — which item (C)'s own proof excludes ("`root-absolute`
  and `protocol-relative` cannot occur, both endpoints are in-root relative
  paths"). That exclusion was then *verified* rather than trusted: `moves`
  values are `relative_to(root).as_posix()` on both verbs, `old_target` is
  proven contained by formula step 3 (whose predicate rejects a leading `/`),
  and `posixpath.relpath` of two relative paths is never absolute — 0 of 36
  pairs. Restricted to that reachable domain, 60,000 cases give **0** failures.
- **The never-creates-an-escape invariant (item (D)), fuzzed** over the whole
  planner: 18,646 planned rewrites across random referrer/target/destination
  combinations produced **0** escaping results and **0** whose emitted spelling
  denoted something other than the intended target.
- **Deliverables and success criteria** re-read one by one against reality
  rather than memory. All ten deliverables and all eleven success criteria are
  met; the `convention.md` half of deliverable 7 (M18's exception widened,
  M27 — D6's *last one this convention grants* sentence reconciled at three)
  was verified by reading the shipped text, not the plan.
- **No placeholders**: no `TODO` / `FIXME` / `NotImplementedError` /
  commented-out code in the new source; no `Pending` row and no
  `_Not complete._` left in the milestone doc or the log; all ten deliverable
  boxes and all ten phase boxes ticked; every phase has a dated log section.
- **The diff is only this milestone's work**: `git diff --name-only 58955ef`
  touches nothing outside `docs/`, `tests/`, `src/` and `CHANGELOG.md`.
- **Generated artifacts in lockstep**: `docs/INDEX.md` and
  `tests/fixtures/expected/docs-INDEX.md` byte-identical; both bundled mirrors
  `cmp`-identical to their sources; `](../` at **0** in `cli.md`,
  `convention.md` and every bundled `.md` (item (M)).
- **Commits**: one per phase on `m28/phases-5-10`, `m28(phase N): …` following
  the project's convention, each carrying the required trailers; no secrets.

### Surfaced for the operator (not auto-decided)

1. **The archive rewrite footer now prints on every archive, including one with
   nothing to rebase.** Step-2 resolution 3 read R3 literally and made the
   counts footer unconditional, so the most common invocation of all gained a
   second line:

   ```console
   $ docs archive a.md
   docs: archive: archived a.md -> archive/2026-08-15/a.md
   docs: archive: 0 destination(s) in 0 document(s) rebased
   ```

   That is the decision as given and it is implemented as given; it is surfaced
   because the *rendered* result is what an operator judges, and the leg-2
   count line was given the opposite treatment (printed only when its list is
   non-empty) in the same resolution. Nothing pins the zero case, so changing
   it later flips no test.
2. **Plan B's orphan count is 5, not the 6 the setup census recorded** (Phase 9).
   The census counted `child-of: plan.md` declarers without item (H)'s
   plan-member exemption, and plan B's primary is itself one of them. The code
   is right and the exemption is locked; the *census* line in the setup record
   is the stale number, left as the historical measurement it was.
3. **`docs archive` has no partial-state admission for its REWRITE phase, and
   closing that needs a decision rather than an edit.** A mid-execution
   `OSError` while `apply_move_plan` writes referrers prints only
   `docs: archive: write failed for <rel>: <err>` and exits 2 — no
   `PARTIAL ARCHIVE` clause and no moved/rewritten/not-written split — while
   `docs mv` admits exactly that state. It is **not** a regression: pre-M28 the
   same failure in `_rewrite_referring_edges` printed `docs: archive: <err>`,
   and the frozen catalogue (J) defines no rewrite-phase admission for
   `archive`. But M28 widened that phase from `Related:` bullets to prose bytes
   across the whole tree, archived documents included, so it is now the phase
   with the **largest** partial-state window and the only one with no
   admission — which sits awkwardly beside D4's "admitted exactly" and R9's
   "the two verbs stay symmetrical". `CoordinatedWriteError.published` already
   carries everything an admission would need; `_cmd_archive` discards it.
   Closing it means **one new message outside the frozen catalogue**, so it is
   recorded as *Follow-ups* item 8 rather than done.
4. **Three staleness items outside M28's diff were found and deliberately NOT
   fixed**, because the checklist also requires that the diff contain only this
   milestone's work:
   - `README.md`'s command list omits `docs relate` (M25), `docs stamp` and
     `docs project` (M12) entirely. The two lines M28 made wrong were fixed
     (finding 4 above); the missing verbs are older gaps and belong to whoever
     owns the README, most naturally the M29 publish.
   - `status.md`'s *resume snapshot* block still says `433 passed (current
     suite, as of 1.5.0 / M13)` and `mypy` without arguments, and describes
     `plan.md` as covering "v1 + v1.1". The block carries a
     "historical" disclaimer, but that disclaimer sits **below** the
     *Verify environment* code block, which therefore reads as a live
     instruction. A one-line move of the disclaimer would fix it.
   - `docs/test-strategy.md`'s quality gate named `mypy bin/docs`, a path that
     has not existed since M6. That one **was** fixed, because Phase 10 claims
     to have closed `test-strategy.md` and its `Updated:` now says so — but it
     is flagged here as a pre-existing defect, not an M28 regression.

## Fresh-eyes review fold-in — 2026-08-15

An independent review of Step 2 returned **no blockers on the product code**.
It re-ran the whole gate, mechanically reproduced the no-regression proof,
exercised the pure seam directly (~600 planner cases plus an exhaustive
renderer sweep over both delimiter forms × 16 special characters × 4 path
prefixes × 4 fragment shapes) and found **zero** violations of the round-trip
invariant, the `classify_destination` post-condition, the colon rule, the
no-op rule, (B)'s step order or the never-creates-an-escape invariant. It
re-ran E1/E2/E3 and every refusal flow on throwaway copies and reproduced each
one. It also cleared four things that look like defects and are not:
`preflight_move_plan`'s `os.access` on the file rather than the parent
directory (item (F) verbatim, and byte-for-byte what `preflight_archive_plan`
documents and defends), `plan_move` dropping M18's `doc.archived` gate
(equivalent by construction — rule (G)), `MOVE_STRAND_KINDS` being
declared-and-asserted-only (consistent with `BODY_LINK_KINDS` /
`DESTINATION_KINDS`), and the surface-parity gate.

Eight findings were returned; all eight are folded in, together with the
operator's answers to the four items the audit surfaced.

### F1 — the archive rewrite-phase admission, CLOSED IN CODE (operator decision)

The audit had surfaced this as *Follow-ups* item 8. The review reproduced it
and showed it was worse than recorded: `docs archive` exits 2 having archived
the primary and rewritten one referrer but not another, printing only
`docs: archive: write failed for ro/ref.md: …` — while `docs mv` on the
identical tree prints the complete admission. What the follow-up entry had
missed is that **three shipped promises were already false**: `cli.md`'s
*Validate-all-first* sits inside a section that opens *"Everything in this
section governs **both** `docs archive` … and `docs mv`"*; `cli.md`'s
*Residual boundary* makes the same promise; and the milestone's own success
criterion is verb-agnostic. Two of the three ship **byte-identically in the
wheel** — the amendment-5 failure class again.

**Operator decision: close it in code**, because the alternative was narrowing
a safety promise in the milestone whose entire point is that a move never
leaves silent damage. `_archive_rewrite_partial_state` renders M26's
`PARTIAL ARCHIVE` prefix with `docs mv`'s `Rewritten:` / `Not written:`
clauses — the right clauses, because by phase 9b every member has archived and
what splits is the rewrite. The data was already there: `apply_move_plan`'s
`CoordinatedWriteError.published` carried it and `_cmd_archive` discarded it.
The one new message is recorded as **amendment 7** to item (J) with its
reasoning; the Phase-10 merge of the two post-move `try` blocks is undone,
because its justification was that both halves fail identically and they no
longer do. Locked by `test_archive_rewrite_oserror_admits_the_partial_state`,
which reproduces the reviewer's `0o644`-file-inside-`0o555`-directory shape and
places a second referrer **outside** that directory so `Rewritten:` is
non-empty — otherwise three of four clauses render `none` and the test cannot
tell a real admission from a template. Mutation-tested. The documentation half
was done as **verification that the three promises are now true**, not as a
narrowing.

### F2 — plan B measures 5, not 6 (amendment 6)

Independently verified twice by the reviewer. Six documents declare
`child-of: plan.md`; plan B's primary is one of them; item (H) exempts plan
members. The code was right and four **binding** passages carried the census
number. Corrected in place at all four sites, with **amendment 6** recording
that the census predates item (H) — a census artefact, not a behaviour change.
Amendment 5 was the precedent.

### F3 — the upgrade note now names every changed stderr line

Item 3 of *Upgrading from 1.x* exists precisely to name stderr changes that
break **silently**, and it named only the two re-spelled `docs mv` lines. It
now also names both new counts footers, the zero case, and the widened
`preview only` gate.

### F4 — the `docs mv` line block contradicted the `--quiet` rule

The block opened *"Every line prints unless `--quiet`"* and then listed the
not-writable **refusal**, which prints even under `--quiet`. Qualified.

### F5 — every preview now says it wrote nothing (operator decision)

M26 gated `preview only — nothing was written` on a cascade flag because a
plain preview was one line and a disclaimer under it was noise. Since Phase 6
that same preview prints the rewrite lines, the counts footer, both strand
blocks and possibly `a write would refuse`. **Operator decision: print it for
every preview** — the M26 rationale is void now the block is long, and a
preview that never says it wrote nothing is exactly the ambiguity M28 exists
to remove. Kept last, and locked by
`test_every_preview_ends_by_saying_it_wrote_nothing`, which asserts it is the
**final** line on both shapes: a preview announcing itself in the middle of its
own plan would be worse than one that did not announce itself at all.

### F6 — the zero-count footer stays, and is now pinned (operator decision)

**Operator decision: keep it.** A zero is positive evidence the new rewrite
phase ran, and it keeps the two verbs' footers symmetrical; leg 2's count line
staying conditional is correct because it summarises a *list*.
`test_the_rewrite_footer_prints_its_zero` pins **both halves of that
asymmetry**, because each looks like the other's bug, and `cli.md` now states
it.

### F7 / F8 — the two reference tables, and one docstring

The amendments table read 1, 2, 3, **5**, 4 and Follow-ups read …6, **8**, 7;
both reordered, since readers scan them by number. Follow-up 8 is retired into
amendment 7. `archive_plan_to_json`'s `move_plan=None` default now says in its
docstring that the record it produces is **not** a conforming
`docs archive --json` record — item (K) requires both arrays present-and-`[]`
rather than omitted — and that the CLI must never use it.

### The README item the review sharpened

The audit had listed README staleness among three things deliberately left out
of this diff. The reviewer found that list **incomplete and one member a real
bug**: `README.md` linked to `blob/main/docs/m8-adoption-workflow.md`, which
has lived under `docs/archive/2026-05-25/` since M8's closeout — a dead link on
the project's front page, heading into a 2.0.0 publish, in the milestone whose
subject is link integrity. **Fixed here**, and all six `blob/main/…` links
re-verified against the working tree. The remaining README staleness — three
shipped verbs missing from the command list, and a feature summary that
predates the v2.0 train — is routed to `m29-pypi-publish-2-0-0.md` as an
explicit publish-time item, because nothing else surfaces it at any gate and
because M29's own archive step is what can break those links again.

### Verification

- `.venv/bin/python -m pytest tests/ -q` — **1341 passed, 0 failed**
  (1338 plus the three locks this fold-in added).
- Lint, format, types clean; `docs check --root docs` exit 0; both bundled
  mirrors `cmp`-identical; INDEX snapshot in sync; `](../` 0/0.
- The F1 fix reproduced by hand before and after, on the reviewer's tree
  shape, and mutation-tested.
- Every `blob/main/…` link in `README.md` resolved against the working tree.

## Second `/simplify` pass — 2026-08-15

Run on `m28/simplify` over the whole M28 surface — the planner seam, the output
helpers and both verbs' rewiring — after the audit and the fresh-eyes fold-in
had changed the code Phase 10's pass last saw. Three changes, all
behaviour-preserving, verified by the same 1341-test suite before and after.
Net **−11 lines** in `src/docs_cli/cli.py`, the only file touched.

| Change | Why it simplifies |
|---|---|
| `plan_body_link_rewrites` — `render_destination_token(…)` lifted out of the `LinkRewrite(…)` argument list into a named `new_raw` | The nested call inside a positional argument list is what forced the formatter to explode one statement across **seven** lines, one argument per line. Two lines now, and the local's name matches the field it fills. |
| `_cmd_archive` step 9a — the member-text dict hoisted out of the `try` into `member_texts` | A pure dict comprehension cannot raise the failure the handler admits to, so it was noise inside the guarded block. The `try` body is now the one call it guards. |
| `_cmd_mv`'s partial-state admission computed into `admission`, then printed with an f-string | `print("docs: mv: " + _mv_partial_state(…), file=sys.stderr)` put `file=sys.stderr` ten lines below the `print(`, and the `+` concatenation is the only one of its kind here — the archive sibling already interpolates. Compute, then print. |

**Deliberately NOT re-made: the archive `try`-block merge.** Phase 10's pass
merged 9a and 9b on the justification that `apply_archive_plan` and
`apply_move_plan` "fail identically"; the fresh-eyes fold-in (F1) undid it,
because since amendment 7 the rewrite phase has its own partial-state
admission and the two no longer fail identically at all. Re-merging would
reintroduce that defect. The blocks stay separate.

**Considered and rejected**, each for a stated reason:

- **A shared `_planned_writes(plan)` helper** for the "documents
  `apply_move_plan` writes" predicate, which appears three times — the
  executor's skip and both verbs' `Not written:` clause. Net **zero** lines
  once its docstring is written, and it moves the rule out of the two
  *message-rendering* functions whose entire value is that each clause is
  checkable where it is read. Kept local.
- **Extracting the `<…>` predicate** shared by `_strip_angle_pair` and
  `render_destination_token`. A named helper costs about seven lines to remove
  one duplicated boolean; `angled = raw != _strip_angle_pair(raw)` costs none
  but is indirect where the explicit test says exactly what `angled` means.
- **The frozen item (L) seam** — `render_destination_token`,
  `splice_body_links` and `plan_body_link_rewrites` each have exactly one
  in-tree caller, but all three are contract-frozen signatures with direct
  unit tests; collapsing them would break the contract, not simplify it.
- **`_plan_rewrites`' `MovePlan | int` return**, **`_archive_move_map` /
  `_archive_related_pairs`**, the `preflight_move_plan` refusal blocks and the
  `_print_move_lines` orphan guard — all re-examined, all kept, for the
  reasons Phase 10 already recorded or because both forms are equally
  defensible and churn is not a simplification.

### Verification

- `.venv/bin/python -m pytest -q` — **1341 passed, 0 failed**, before and
  after the pass.
- `.venv/bin/ruff format --check .`, `.venv/bin/ruff check .`,
  `.venv/bin/mypy` — clean.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).
- Both bundled mirrors `diff`-identical to their sources; INDEX snapshot in
  sync; `pyproject.toml` untouched.
- `git diff --stat` — `src/docs_cli/cli.py` only, 17 insertions / 28
  deletions.

## Milestone completion summary

**M28 — Move-safe Markdown body-link rewrites is implementation-complete. All
ten TDD phases are done (2026-08-15)**, Step 1 (Phases 1–4) on
`m28/phases-1-4` and Step 2 (Phases 5–10) on `m28/phases-5-10`. The package
stays `1.8.0`; **M29** performs the single bump to `2.0.0` (M25 — D6), and M28
stays `Lifecycle: active` until that closeout.

**What shipped.** `docs mv` and `docs archive` now rebase the local Markdown
body links a move makes stale — in the same operation, in the same
per-document write, and under the same all-or-nothing contract as the
`Related:` rewrite. Two independent breakages are handled by **one formula**
over M27's scanner and its exact destination spans, mapped on the **normalised
target** so every spelling of one file is rewritten with no alias list.
`docs mv` was inverted to plan-before-move, gaining M26 — D4's
zero-mutation refusal, a real `--dry-run` preview and a `--json` record.
`docs archive` gained the same rewrite section plus a `strands` array, and a
**strand-check**: leg 1 refuses a plan that would archive a parent out from
under a live child, leg 2 reports every other still-active inbound reference
without refusing. `_rewrite_referring_edges` is deleted, superseded by
`apply_move_plan`.

**The defect it closed, measured.** Before M28 both verbs produced trees that
failed the tool's own gate. On this repository, on throwaway copies, with the
pre-M28 binary as the control: a rename left **42** `broken-body-link` findings
across 14 documents, a single archive left **13** spanning both move classes
including four inside archived referrers, and the real milestone closeout left
**6** in the two most-read documents. All three are now **0**, with `docs check`
exiting 0 after each, and the rename's diff is 77 lines in which every changed
line names the moved document.

**The judgement calls, and why they went the way they did.**

- **Leg 1 was narrowed to `child-of`, and leg 2 was not optional.** The routed
  predicate, taken literally, refuses this repository's own standard milestone
  closeout — 16 deliberate references from 7 referrers. A safety check that
  blocks the workflow the tool exists for is one operators route around, which
  is the same *never cry wolf* criterion the operator applied when declining
  issue #1's finding 3. Leg 2 is what preserves the routing note's actual
  purpose: it delivers the consequences to the agent generating the glob, in a
  form it can parse.
- **Archived referrers get destination tokens only** — M18's shape, widened
  along its own axis rather than granted as a fourth exception, superseding the
  registered stub's own recommendation. Same trigger, same operation, same
  single write; nothing new is asserted; and an `Updated:` bump would make an
  archived document's date a record of some *other* document's move.
- **`--report-links` was declined as a design and its output adopted.** M27
  had already made a broken prose link a hard error, so "declare them out of
  scope" would ship trees that fail the tool's own gate — and a *report* leaves
  the repair to the same agent whose blind spot produced the problem.
- **A preview adopts plan *construction* failures and only reports plan
  *consequences*.** That single sentence resolves M26's own follow-up item 2
  without bending the no-record-on-refusal rule.

**Evidence quality.** 254 test ids added, **0** removed against the pre-M28
commit, 11 test lines deleted — all inside one deliberately re-pointed lock,
named and justified as a strengthening rather than reported as "no test
changes". The suite is **1341 passed / 0 failed** (1333 at the Phase-8 gate,
plus the five locks the Step-2 audit added — two for Step-2 resolutions that
had shipped as promises rather than locks, and three closing gaps the
adversarial pass found — plus three from the fresh-eyes fold-in). Nine dogfood flows ran
unattended on throwaway copies, the live tree never written to, with the
"before" column measured rather than quoted. Plan A reproduced the setup census
exactly (16 references, 8 + 8, from 7 referrers). A there-and-back move leaves
the tree byte-identical, `INDEX.md` included. The cost is +80 ms on a move and
+113 ms on a solo archive over a 73-document tree.

**Handed on.** Seven follow-ups are recorded in the milestone doc — the two
largest being `docs migrate --apply`'s missing reference repair and extending
leg 1 to a `docs mv` into the archive subtree. **M28a — Structured
archive-date witness** and **M29 — PyPI publish 2.0.0** are ready to prepare
next.
