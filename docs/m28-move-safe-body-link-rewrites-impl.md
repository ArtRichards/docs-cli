# M28 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-08-15

Related:
- child-of: m28-move-safe-body-link-rewrites.md
- pairs-with: m28-move-safe-body-link-rewrites.md
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
- Progress: **Phases 1–4 are COMPLETE (2026-08-15) — Step 1 of the
  milestone is done; Phase 5 — Update Base Interfaces is next.** The whole machine-facing contract is frozen in
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
  (Phases 1–4).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | **Complete** | 2026-08-15 | Frozen in the milestone's *Decisions (Phase 1 — BINDING)*: items (A)–(M), three amendments to setup-frozen material, eleven Step-1 resolutions (R1–R11). Author-facing halves in `cli.md` (*Move-safe body-link rewrites (M28 — D1–D7)*, the rewritten `docs mv` section, the amended archive check order, the widened `archive --json` schema, three exit tables) and `convention.md` (M18's widened exception, M27 — D6's reconciled sentence, the author-facing move guarantee). Zero product-code change. Original objective: Freeze the three-step rewrite formula and its move map, the emitted spelling / fragment / delimiter / re-encoding rules, the byte-for-byte no-op rule, the never-creates-an-escape invariant, the archived-referrer policy (destination tokens only) and its `convention.md` wording, **both** strand-check legs — leg 1's `child-of` refusal predicate and message, leg 2's report, its ordering and the lines and record keys that carry it — the pre-flight and partial-state boundary, the preview and `--json` shapes for **both** verbs (including `mv`'s new record and `archive --json`'s rewrite section and `strands` array), and the Phase-5 signatures — against the resolved Q1–Q7. |
| 2. Write Tests (RED) | **Complete** | 2026-08-15 | 182 new ids: `tests/test_move_links.py` (153, the pure seam) plus 12 `mv`, 14 `archive`, 1 `check` and 2 skill locks. Suite 1269 collected / 181 failed / 1088 passed; the 1087 pre-existing ids all present and GREEN; zero collection errors; zero deleted test lines. Original objective: Pure-planner unit tests for both move classes and every grammar form; `mv` / `archive` integration and subprocess locks; both strand-check legs — the refusal, the leg-1 over-fire lock proving a legitimate closeout completes, and the leg-2 report in prose and in `strands`; failure-injection, byte-identity, idempotence and no-op locks. |
| 3. Create Data/Fixtures | **Complete** | 2026-08-15 | Seven `movelink-*` trees authored — `-incoming`, `-moved-referrer`, `-both`, `-archived-referrer`, `-nested`, `-strand`, `-closeout` — each `docs check`-clean as committed; every existing fixture byte-identical; the two directory-derived sweeps 29→36 and 33→40; suite 1283 / 180 failed / 1103 passed. A read-only prototype census confirmed every intended plan, line numbers included. Original objective: `movelink-*` trees, one semantic each — `-incoming`, `-moved-referrer`, `-both`, `-archived-referrer`, `-nested`, `-strand`; exotic grammar as inline strings and mutation cases as inline `tmp_path` builders (the M25 rule). |
| 4. Run Tests (RED Baseline) | **Complete** | 2026-08-15 | 1286 collected / 182 failed / 1104 passed (restated after the Step-1 audit); 0 collection errors, 0 xfail/xpass, 0 warnings; exactly two exception classes (152 `AttributeError`, 28 `AssertionError`); mechanically proven 0 removed ids and 0 failing pre-existing ids against `58955ef`. Original objective: Classified failure set against the 1087-test baseline; every GREEN-at-baseline and transitional lock named. |
| 5. Update Base Interfaces | Pending | — | The rewrite record, the rewrite plan, the pure planner, the splicer, the strand predicate (leg 1), the strand report (leg 2) and the JSON serializer — no verb wired, so the CLI tests stay honestly RED at the seam. |
| 6. Implement Offline/Core Path | Pending | — | Invert `_cmd_mv` to plan before it moves; fold the splices into `_rewrite_referring_edges`' single per-document write; apply the archived-referrer policy (tokens only); run **both** strand-check legs in the pre-flight **and** the preview; implement the refusal, the report and the partial-state paths. |
| 7. Update Tool/Wrapper Layer | Pending | — | argparse for both verbs including `mv --json` and its real `--dry-run`, human output for rewrites and for the strand report, the JSON records and field tables, `cli.md` / `convention.md` (M18's widened exception **and** the reconciliation of M27 — D6's "last one this convention grants" sentence), a dated note on `feedback-log.md`'s issue #1 entry answering findings 1 and 4, the bundled skill, `UNRELEASED` CHANGELOG and the upgrade note. No version bump. |
| 8. Run Tests (GREEN) | Pending | — | Full product and quality gates with exact counts; mechanical no-regression proof against the 1087 pre-existing ids. |
| 9. Integrate / Accept / Dogfood | Pending | — | Replay E1, E2 and E3 on throwaway copies and prove each ends `docs check` clean with a destination-token-only diff; exercise the leg-1 refusal on plans B and C and byte-compare; confirm plan A completes with its leg-2 report naming all 16 still-active inbound references; prove idempotence; measure the added runtime. The real tree is never written to. |
| 10. Quality, Docs, Refactor | Pending | — | `/simplify`, close `architecture.md` and `test-strategy.md`, update the shipped use-case catalog, completion summaries, hand to M28a and M29. |

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
  collection errors.
- `.venv/bin/python -m pytest tests/ -q` — **180 failed, 1103 passed**.
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
.venv/bin/python -m pytest tests/ -q --co   ->  1286 collected, 0 collection errors
.venv/bin/python -m pytest tests/ -q        ->  182 failed, 1104 passed
```

*(Restated after the Step-1 same-instance audit, which added three `docs mv`
locks — see* Step-1 same-instance audit *below. The pre-audit figures were
1283 / 180 / 1103.)*

Arithmetic, and it closes: **1087** pre-existing + **185** authored ids +
**14** swept ids (7 into `test_check_tree_legacy_fixtures_gain_no_new_findings`,
7 into `test_check_tree_pre_m27_fixtures_gain_no_body_link_findings`) =
**1286**. Of the 199 new ids, **182** are RED and **17** are GREEN at
baseline.

### Probes, stated honestly

- **Collection errors: 0.** `--co` collects 1283 and reports no errors.
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
| `AttributeError` | 152 | the whole of `tests/test_move_links.py` | every M28 symbol is fetched through `_m28(name)`, so the RED reason is one clean missing attribute rather than a collection error |
| `AssertionError` | 30 | 14 `docs mv`, 14 `docs archive`, 2 bundled-skill locks | the behaviour is absent, not the symbol; 28 carry a message and 2 are bare `assert`s pytest rewrote |

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
| ids at HEAD | **1286** |
| `comm -23 old new` — **removed** ids | **0** |
| `comm -13 old new` — added ids | **199** (153 `test_move_links.py`, 15 `test_cli_mv.py`, 14 `test_cli_archive.py`, 14 `test_check.py` sweeps, 2 `test_skill.py`, 1 `test_cli_check.py`) |
| `comm -12 failed old` — pre-existing ids now FAILING | **0** |
| `git diff --numstat 58955ef -- tests/` | **0** deleted lines in every test file |
| `git diff --stat 58955ef -- src/docs_cli/cli.py` | **empty** |

`tests/test_edit.py`, `tests/test_relate_plan.py` and `tests/test_archive_plan.py`
are untouched: `rewrite_related_refs` and M26's frozen plan contract are not
reached into.

### RED classification — every failure traced to a family and a landing point

| # | Family | Landing |
|---|---|---|
| 152 | **The pure seam** (`tests/test_move_links.py`): the formula and both classes, the no-op rule and idempotence, out-of-reach destinations, the never-creates-an-escape invariant, the emitted spelling, the re-encoding round-trip, the splicer, the pipeline order, purity, both strand legs, the pre-flight, the shared record | **Phase 5** — `LinkRewrite`, `DocRewrite`, `Strand`, `MovePlan`, `MOVE_STRAND_KINDS`, `plan_body_link_rewrites`, `render_destination_token`, `splice_body_links`, `plan_move`, `preflight_move_plan`, `apply_move_plan`, `move_plan_to_json` |
| 12 | **`docs mv` behaviour**: class-2 rebasing, nested both-directions, E1's post-rename `docs check`-clean, the archived referrer's byte boundary and its no-`Revision:` sibling, prose and code untouched, the zero-mutation refusal, the malformed-tree preview at exit 2, idempotence, the preview's rewrite lines, the apply path's identical lines, and the mid-execution partial-state admission | **Phase 6** — invert `_cmd_mv` to plan before it moves |
| 2 | **`docs mv` surface**: `--json`'s record and its preview/apply equality | **Phase 7** — `--json` on the `mv` subparser (`cli.py:4852`) |
| 14 | **`docs archive` behaviour and surface**: E2, E3, E5, leg 1's refusal and its `--quiet` sibling, leg 1's preview at exit 0, the over-fire lock, leg 2's stderr report in both modes, the widened `--json` key set, `strands` on a completing plan and in a refusing plan's preview, empty-array-not-missing, preview/apply rewrite equality, and the malformed-tree preview at exit 1 | **Phase 6** (behaviour) and **Phase 7** (the record and the amended check order) |
| 2 | **Bundled skill parity**: `SKILL.md`'s `mv` / `archive` rows and `references/use-cases.md` | **Phase 7** — the bundled skill lands in the same change as the CLI surface |

### GREEN at baseline — every lock classified

The 16 new GREEN ids:

| Lock | Classification |
|---|---|
| `test_check_tree_legacy_fixtures_gain_no_new_findings[movelink-*]` ×7 | **degenerate** now (none of the seven uses a reciprocal verb); a genuine regression lock after Phase 6 |
| `test_check_tree_pre_m27_fixtures_gain_no_body_link_findings[movelink-*]` ×7 | **degenerate** now; genuine afterwards — a Phase-6 rewrite that emitted a wrong spelling would break them |
| `test_check_every_movelink_fixture_tree_is_clean_as_committed` | **genuine**; it landed at Phase 3, and it is what makes every post-move clean assertion measure the MOVE rather than pre-existing fixture damage |
| `test_relpath_of_a_root_level_target_needs_no_special_case` | **degenerate** now; genuine afterwards — it pins the `posixpath` behaviour item (B) step 6 relies on, so a Phase-5 implementation cannot "fix" it with an `or '.'` that changes every emitted spelling |
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
   note: a move now edits prose, and an archive now refuses in a case it
   previously completed.
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

The baseline is restated accordingly: **1286 collected, 182 failed, 1104
passed** (from 1283 / 180 / 1103), still exactly two exception classes, still
zero deleted test lines and zero removed ids against `58955ef`.

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

## Milestone completion summary

_Not complete._
