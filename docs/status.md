# docs — Status

Lifecycle: active
Role: status
Project: docs
Updated: 2026-08-16

Related:
- pairs-with: plan.md
- pairs-with: archive/2026-05-24/m6-pypi-distribution.md
- pairs-with: archive/2026-05-25/m7-migration-accuracy.md
- pairs-with: archive/2026-05-25/m8-adoption-workflow.md
- pairs-with: archive/2026-05-25/m9-pypi-publish.md
- pairs-with: archive/2026-05-27/m10-adoption-polish.md
- pairs-with: archive/2026-05-27/m11-pypi-publish.md
- pairs-with: archive/2026-05-28/m12-project-rename.md
- pairs-with: archive/2026-05-29/m13-pypi-publish.md
- pairs-with: release-runbook.md
- pairs-with: archive/2026-06-03/m14-robustness-agent-native.md
- pairs-with: archive/2026-06-03/m15-agent-native-authoring.md
- pairs-with: archive/2026-06-01/m16-bundled-docs-skill-quality.md
- pairs-with: archive/2026-06-03/m17-pypi-publish.md
- pairs-with: m17-pypi-publish-impl.md
- pairs-with: archive/2026-06-12/m18-archive-edge-integrity.md
- pairs-with: archive/2026-06-12/m19-post-edit-validation.md
- pairs-with: archive/2026-06-12/m20-pypi-publish.md
- pairs-with: m20-pypi-publish-impl.md
- pairs-with: archive/2026-07-03/m21-update-check.md
- pairs-with: archive/2026-07-03/m21-update-check-impl.md
- pairs-with: archive/2026-07-03/m23-agent-aware-install-skill.md
- pairs-with: archive/2026-07-03/m23-agent-aware-install-skill-impl.md
- pairs-with: archive/2026-07-03/m24-pypi-publish.md
- pairs-with: m24-pypi-publish-impl.md
- pairs-with: m25-reciprocal-relationship-integrity.md
- pairs-with: m25-reciprocal-relationship-integrity-impl.md
- pairs-with: m26-safe-archive-selection.md
- pairs-with: m26-safe-archive-selection-impl.md
- pairs-with: m27-markdown-body-link-validation.md
- pairs-with: m27-markdown-body-link-validation-impl.md
- pairs-with: m28-move-safe-body-link-rewrites.md
- pairs-with: m28-move-safe-body-link-rewrites-impl.md
- pairs-with: m28a-archive-date-witness.md
- pairs-with: m28a-archive-date-witness-impl.md
- pairs-with: m29-pypi-publish-2-0-0.md

**This is the single source of truth for project progress. Update only this file when milestones complete or phases advance.**

## Current milestone

**M28a — Structured archive-date witness is the current milestone, and it is
now IMPLEMENTATION-COMPLETE across all ten TDD phases** — 1502 passed / 0
failed, every quality gate clean, `docs check --root docs` exit 0, both
bundled mirrors byte-identical, and `feedback-log.md` issue #1 CLOSED. It
stays `Lifecycle: active` until the M29 publish closeout. Step 1 —
Phases 1–4 — completed on `m28a/phases-1-4` (contract 2026-08-15; RED tests,
fixtures and the classified baseline 2026-08-16), and Step 2 — Phases 5–10 —
on `m28a/phases-5-10` (2026-08-16). **Phase 5 — Update Base Interfaces
completed 2026-08-16**, landing the vocabulary entry, `parse_date`'s
keyword-only `label`, and all three pure helpers wired nowhere — 43 ids
flipped, the suite at **28 failed / 1474 passed**, and `check_doc`,
`_archive_one` and `_cmd_mv` untouched so every CLI-level id stayed honestly
RED at the seam — and **Phase 6 — Implement Offline/Core Path completed
2026-08-16**, wiring both legs at their three frozen touch points and nowhere
else: the witness write in `_archive_one`, the rule in `check_doc`, and Leg 2's
refusal in `_cmd_mv` before the `--dry-run` branch. 26 more ids flipped, the
suite stands at 2 failed / 1500 passed with only the two bundled-skill ids
left, and `docs check --root docs` still exits 0 with the rule live — and
**Phase 7 — Update Tool/Wrapper Layer completed 2026-08-16**, landing the
bundled skill, two argparse `description` clauses (the flag delta itself is
confirmed **empty**), the `UNRELEASED` CHANGELOG entries and issue #1's
closeout, and correcting the two spec gaps verification found. The suite is
fully **GREEN at 1502 passed / 0 failed**. **Phase 8 — Run Tests (GREEN)
completed 2026-08-16**: every gate clean, and the mechanical proof against
`7f7853b` shows **0** of the 1341 pre-existing ids removed and **0 deleted
lines in every test source file** — no test was relaxed, weakened, deleted or
rewritten, and Step 2 changed no test source at all. **Phase 9 — Integrate /
Accept / Dogfood completed 2026-08-16** across ten flows on throwaway copies:
E1d refuses at exit 2 leaving the copy byte-identical, on a document with the
witness and on one without; a hand-made relocation adds exactly **one**
`archive-date-drift` where the pre-M28a CLI on the same tree adds none; all
four permitted neighbours complete; a non-default `attic` / `%d-%m-%Y` tree
refuses on its configured dir and completes on an ordinary `archive/`
subdirectory; all **46** pre-witness archived documents stay silent; a real
`--cascade-only 'm26-*'` closeout writes the witness to every member with one
shared date and leaves `docs check` clean; `migrate --apply` writes none and
demotes a foreign one; the **7** cross-dated `pairs-with` edges emit nothing;
and the runtime delta is below the 10 ms measurement floor. **Phase 10 —
Quality, Docs, Refactor completed 2026-08-16**: `/simplify` took *Follow-ups*
item 4 in full — **five** inline copies of the archive-subtree predicate (E7
counted three; reading for the collapse found two more) are now calls to
`_is_archived_rel`, which was hoisted beside `_root_relative`, also removing
Phase 5's forward reference — behaviour-preserving at 1502 passed before and
after with the `docs check` runtime unchanged, and four further candidates
evaluated and rejected with reasons. `architecture.md`'s `check`, `archive`
and `mv` sections and `test-strategy.md`'s fixture-source list are closed, and
the completion summaries are written. **M28a is implementation-complete and
handed to M29.** All seven
setup questions were RESOLVED before Phase 1,
and Phase 1 froze the contract against them without re-opening any: the
machine-facing contract is items (A)–(H) of the milestone's *Decisions
(Phase 1 — BINDING)*, with **six amendments** to setup-frozen material and
**nine Step-1 resolutions** (OQ-1 … OQ-9; OQ-7 an operator decision declining
to widen the `docs mv` predicate). No product code has changed; Phases 2–4
authored **149** test ids and **six** `archivedate-*` fixture trees against
that contract and captured the classified baseline — 1502 collected, **71 RED
and 90 GREEN** of the 161 new ids, in exactly two exception classes, with
**no** pre-existing id removed or failing. M28a ships **two
legs**. **Detect:** `docs archive` writes an
archived document's own archive date as a structured **`Archived:`** field — to
**every** document an operation moves, not the primary only — and `docs check`
gains `archive-date-drift`, reporting a document whose recorded date its
location does not corroborate. **Prevent:** `docs mv` refuses a move whose
source and destination are different dated archive directories, at exit 2,
before it writes anything. The rule fires **only when the field is present**,
so every document archived before 2.0.0 stays silent forever and a 1.x tree
gains zero findings on upgrade — that present-only contract is the whole
compatibility story, and it is what lets the rule be a hard error at all. The
refusal needs no field at all, which is how the two legs together close the
tool's own surface completely.

Setup measured this tree read-only and reproduced the drift on throwaway
copies, producing nine pieces of evidence (**E1–E9**). Two of them reshape the
milestone. **E1** enumerates all four ways a document can move relative to the
archive subtree and finds that **exactly one is silent**: `docs archive`
refuses an already-archived primary at exit 2; `docs mv` out of the archive
and into it are both caught by `status-drift` at exit 2; and
`docs mv archive/2026-05-25/m9-pypi-publish.md
archive/2026-07-03/m9-pypi-publish.md` **completes at exit 0** and leaves
`docs check` reporting no violations. That corrects the registered stub's claim
that the tool already prevents this — it is true of `docs archive` and false of
`docs mv`. **E2** replays that one command against the pre-M28 CLI (`58955ef`)
and against merged `main`: **13 `broken-body-link` errors and exit 2 before,
zero findings and exit 0 after.** Nothing regressed — M28 rebased those
destinations exactly as specified — but the only alarm this tree had for
archived-document relocation was a side effect of the defect M28 fixed. M28a is
therefore a **consequence** of M28, and that is why it **blocks M29**:
shipping M28 in 2.0.0 without M28a would leave the release **strictly quieter
about archived-document relocation than 1.8.0 was**.

The rest of the evidence settles the design. **Neither existing field can
carry the witness**: 29 of this tree's 46 archived documents carry an
`Updated:` value that differs from their dated directory (the M27 — D6
migration), and an ordinary `docs touch` bumps it again at exit 0 (E3); while
`Archived-reason:` is free text written to the **primary only**, so it covers
13 of 46 (E4) — which is why the witness deliberately does *not* inherit that
rule, since issue #1's real-tree replay was a cascaded **trio** split across
two dated directories. The reporter's own suggested rule — warn when
`pairs-with` partners sit in different dated directories — stays **declined**,
now with a number: it would emit **7** findings on this tree, at `docs check`
exit 0, on deliberate cross-milestone edges (E5). The label is free (zero
occurrences anywhere, E6); there is no rule registry, no field-order rule, and
the only dated-directory parser is config-blind and lives in the migrate half
(E7); a non-default `date_format` tree already breaks on a pre-existing
hardcoded-ISO parse, which is why comparison is on **parsed dates** (E8); and
`docs migrate` derives each file's archive-directory date from `Updated:` or
**mtime**, which on a fresh clone is today — so migrate must never write the
witness (E9).

**All seven setup questions are RESOLVED.** **Q4 is the operator decision
that shaped the milestone: adopt BOTH legs.** The witness alone can never
reach the 46 documents this tree archived before the field existed, nor any
tree upgrading from 1.x, so `docs mv` also refuses — on a predicate decidable
from the two paths alone (both ends under the archive dir, first segments
parsing to different dates), evaluated in the plan-before-move,
refuse-with-zero-mutation window **M28 already built** — at the position
Phase-1 amendment 2 froze, immediately after the two root-relative paths are
derived and **before** the `--dry-run` branch, so it refuses in every mode —
with both dates named and zero bytes written. **Four** neighbours are
enumerated as **permitted** so the predicate cannot creep (amendment 6) — a
rename within one dated directory, a move `status-drift` already catches, a
move whose segments do not both parse, and two spellings of one date —
and the by-hand escape for a genuinely mis-dated archive ships in the **same
paragraph** as the refusal in both specs, so it never reads as a dead end.
**Q1** fixes the label as **`Archived:`**, permanently: the convention never
renames a built-in, and `Archived-date:` is recorded as the rejected
alternative because `Updated:` already establishes that a date field here does
not name its own type. The conductor-resolved five: **Q2** exact equality
compared on **parsed dates** in the tree's `date_format`, **Q3** no backfill,
**Q5** migrate never writes the witness, **Q6** all three
archived-immutability paragraphs must name it, **Q7** one rule covers the
non-dated locations too. The two corrections to previously written material are
restated as **A1** and **A2** in the milestone doc's *Decisions recorded at
setup (BINDING)*.

The package version stays **1.8.0** (M25 — D6); CHANGELOG entries accumulate
under `UNRELEASED` for M29. M28a adds no CLI flag and no JSON key; its one
behaviour change is D5's refusal. Setup also registered, in `feedback-log.md`,
the one defect it found and deliberately did **not** fix — `docs archive`
exiting 2 on the INDEX refresh in a non-default-`date_format` tree, because
`parse()` parses `Updated:` with a hardcoded ISO format while `check_doc`
honours the configured one; M28a's own comparison parses both sides with
`config.date_format` so it cannot inherit the bug. The prepared pair is [m28a-archive-date-witness.md](m28a-archive-date-witness.md) and
[m28a-archive-date-witness-impl.md](m28a-archive-date-witness-impl.md).

**M28 — Move-safe Markdown body-link rewrites is complete and merged to
`main`, and
all ten TDD phases are done — it is implementation-complete.** Step 1
(Phases 1–4) landed on `m28/phases-1-4` (2026-08-15) and Step 2 (Phases 5–10)
on `m28/phases-5-10` (2026-08-15): the suite is fully GREEN at **1341 passed**,
the nine-flow dogfood ran unattended on throwaway copies with the live tree
never written to, and `/simplify` plus the documentation closure landed in
Phase 10. A **second `/simplify` pass** then ran on `m28/simplify`
(2026-08-15) over the code the Step-2 same-instance audit and the fresh-eyes
fold-in had changed since — three behaviour-preserving collapses, net
**−11 lines**, the suite unchanged at 1341, and Phase 10's archive `try`-block
merge deliberately **not** re-made, because F1's rewrite-phase admission means
the two phases no longer fail identically. M28 stays `Lifecycle: active` until
the M29 publish closeout; **M28a** and **M29** are next. M28a's milestone setup completed 2026-08-15 with all
seven setup questions RESOLVED, and its **Step 1 — Phases 1–4** completed on
`m28a/phases-1-4` (contract 2026-08-15; RED tests, fixtures and the classified
baseline 2026-08-16) without re-opening them. M28 extends `docs mv` and `docs archive` to rebase the
parsed local Markdown destination tokens a move makes stale — reusing M27's
scanner and its exact destination spans, never a second parser — and to refuse
a move whose consequences the tool can prove wrong. Two move classes are in
scope and they are **one formula**: a link whose *target* moved, and a link
*inside* a document that itself moved. Resolve each destination from the
referrer's old location, map the resolved target through the move set, and
relativise against the referrer's new directory; class 1 is the case where the
map fires, class 2 the case where the referrer moved. Because the mapping is by
**normalised target**, every spelling of the same file is rewritten — unlike
the `Related:` rewriter, which matches the declared string exactly and needed
M26 — Q5's alias list.

Setup measured the tree read-only and reproduced each defect on throwaway
copies, producing eight pieces of evidence (**E1–E8**). The headline is that
**both verbs now produce trees that fail the tool's own `docs check`**:
`docs mv plan.md milestone-plan.md` rewrites 35 `Related:` bullets, exits 0,
and leaves **42 `broken-body-link`** findings across 14 documents (E1);
`docs archive m17-pypi-publish-impl.md` exits 0 and leaves **13** — 10 incoming
(4 of them inside archived referrers) and 3 inside the moved document itself,
so one ordinary command produces **both** classes (E2); and the real
milestone-closeout invocation `docs archive m25-… --cascade-only 'm25-*'`
leaves **6** in `status.md` and `plan.md`, the two documents an agent reads
first (E3). The exposure is large and concentrated — 379 local destinations
over 71 documents resolving to 69 targets, worst-hit `release-runbook.md` (49
occurrences in 17 documents) and `plan.md` (42 in 14) — and **131 body links in
27 archived documents point at active documents** (E5), which makes the
archived-referrer policy a blocker rather than a nicety: without it, moving any
core document leaves hard errors that no verb can repair. M18's exception
already licenses exactly this move-driven class of write, so M28 widens M18
along its own axis rather than granting the fourth exception `convention.md`
says it will not grant.

**All seven setup questions are RESOLVED** — Q1, Q2 and Q3 by the operator;
Q4, Q5, Q6 and Q7 conductor-resolved. **Q1 amends the 2026-08-15 routing
entry.** The harm it targets is real and reproduces live —
`docs archive m27-….md --cascade-dry-run --cascade-only '*'` marks `plan.md`,
`cli.md`, `convention.md`, `test-strategy.md` and `status.md` **selected** —
but the routed literal predicate, *refuse if the plan would leave a
still-active document pointing at a newly-archived one*, was measured against
this repository and **refuses its own standard milestone closeout**: a textbook
`--cascade-only 'm26-*'` leaves 8 still-active `Related:` edges and 8
still-active body links from 7 active referrers, every one deliberate (the
tracker, the plan, and the neighbouring milestones' `precedes` / `follows` /
`depends-on`, which is what M25's graph exists to record). The routing note's
claim that the check "self-cancels for legitimate whole-set archiving" does not
hold on a real tree. So the predicate is split into **two binding legs**:
**leg 1 refuses** only when a still-active document outside the plan declares
itself `child-of` a document the plan would archive — 0 occurrences on the
legitimate closeout, 6 on both harm plans — and **leg 2 reports** every other
still-active inbound reference, any other `Related:` verb and every body link
alike, in the preview, the apply output and the record's `strands` array,
**refusing nothing**. Leg 2 is not optional: it is the half that answers issue
#1's actual complaint — that the safety rested on a human reading a preview —
and it carries its own deliverable, success criterion and named coverage.
Shipping the literal form would have failed the charter's *never cry wolf*
criterion, the same criterion applied in the same feedback entry when issue
#1's finding-3 rule was declined; the two narrower alternatives (refusing an
unbounded `'*'` scope, a `Role:`-based rule) are recorded with the reason each
lost.

**Q2 supersedes the registered stub's own recommendation**: the
archived-referrer rewrite carries **destination tokens only** — no `Updated:`
bump, no `Revision:` bullet — because it is the same trigger, operation and
single write as M18's `Related:` half, asserts nothing new, and a bump would
make an archived document's date a record of some *other* document's move. It
is implemented by **widening M18's exception**, granting no fourth one, with
M27 — D6's "last one this convention grants" sentence reconciled in Phase 7.
**Q3** gives `docs mv` a real preview and a `--json` rewrite-plan record and
`docs archive --json` the same rewrite section plus a `strands` array, one
schema shared by preview and apply (M26 — D7 / M25 `relate --json`
conventions), and answers issue #1 finding 4: `--report-links` is **declined as
a design** — M27 already made a broken prose link a hard error, so a
report-only option would mean knowingly shipping failing trees — while its
**output is adopted** as that plan record. The four conductor-resolved answers:
destinations a move does not own stay byte-identical and do not gate the move
(**Q4**); a semantically unchanged destination keeps its bytes, otherwise the
`posixpath.relpath` form with the fragment verbatim and one stated escape
strategy (**Q5**); `docs migrate --apply` is out of scope, recorded as a
follow-up (**Q6**); and M26's duplicate-`Related:`-bullet follow-up is
re-deferred explicitly rather than reaching into M26's frozen Phase-1 Q5
contract (**Q7**). All three answers that changed something already written
down are restated as **A1/A2/A3** in the milestone doc's *Decisions recorded at
setup (BINDING)*, so a Phase-1 agent can reconstruct them from that document
alone.

The package version stays **1.8.0** (M25 — D6); CHANGELOG entries accumulate
under `UNRELEASED` for M29. The prepared pair is
[m28-move-safe-body-link-rewrites.md](m28-move-safe-body-link-rewrites.md) and
[m28-move-safe-body-link-rewrites-impl.md](m28-move-safe-body-link-rewrites-impl.md).

**M27 — Markdown body-link validation is
implementation-complete: Step 1 on `m27/phases-1-4` and Step 2 on
`m27/phases-5-10`, all ten phases (2026-08-14). The live tree is repaired,
`docs check` is clean with both rules in force, and the suite is fully GREEN
at 1087 passed / 0 failed. The milestone stays `Lifecycle: active` until the
M29 publish closeout.** M27 adds a pure, stdlib-only, linear scanner over a
deliberately bounded Markdown grammar and makes a local body link whose
destination is missing a hard `docs check` error (`broken-body-link`, severity
`error`, exit 2), while producing nothing at all for code, examples, external
URLs, images, raw HTML, and plain-text mentions. Destinations resolve
**relative to the referring document** — the opposite of `Related:` —
fragments are preserved and never validated, and the scanner records the exact
character span of each destination token so **M28** can rewrite it without a
second parser. Setup measured the tree read-only and produced eight pieces of
evidence (**E1–E8**): **139 local destinations do not resolve, across 29
documents, and every one of them is under `archive/`** — the active tree is
clean; 132 of the 139 are a pure `../../` rebase that was never applied when
the document moved into the archive, 5 name a target that itself later moved,
and 2 name a bundled-skill file that never lived in the docs tree;
`docs check` exits **0** today with all 139 broken; and
`test_check_dogfood_repo_docs_is_clean` asserts this repository's own tree
exits 0, which makes the legacy-damage policy a **hard gate inside the suite**
rather than an aspiration. Setup also proved the parser risks are real on this
tree: without code masking the scan gains 4 false positives inside fenced code
(including `architecture.md:182`'s `[<path>](<path>)`) and 3 inside inline
code spans, while a 4-space indented-code rule would mask 9 spans that are
all **real links** in blockquote and list continuations — six of them
genuinely broken.

**All seven setup questions are RESOLVED** — Q1, Q2, and Q5 by the operator;
Q3, Q4, Q6, and Q7 conductor-resolved. **Q1: repair, and the rule stays
uniform** across archived and active documents. The deciding argument is
ownership rather than volume: this breakage class is produced by `docs archive`
itself — no version of the tool has ever rebased a moved document's body links,
and 8 of the 33 fixture trees already carry `archive/` directories — so a rule
exempting archived documents would leave the tool silent about the exact damage
it causes; and `docs/`, archive included, ships in every PyPI **sdist** and is
public on GitHub, where the worst-hit files (`plan.md`, `status.md`,
`release-runbook.md`, `cli.md`) are what a prospective adopter reads. The
one-time repair is destination-tokens-only, audited with an `Updated:` bump and
a dated `Revision:` bullet (M25 — D4's shape), and lands in **Phase 6** in the
same change that wires the rules; `convention.md` gains a third narrow
exception to archived-document immutability with a **stated blast radius**.
**Q5 was resolved against the setup recommendation and then amended**, and the
result is the milestone's second rule: `docs check` must never touch the
filesystem outside the tree it was pointed at — a check has to be a function of
the tree alone, since `charter.md:52` resolves today only because `docs/`
happens to sit beside `src/` in a checkout — but silently skipping such a link
would let a working link rot unnoticed. So an escaping destination is detected
by **path arithmetic alone** and reported as **`outside-root-body-link`**
(error, exit 2), an operator-approved post-draft scope addition following M25's
`duplicate-field` precedent. Containment is tested **before** existence so the
two rules never double-report, `convention.md` adopts the invariant *a local
Markdown body link stays inside the tree root; anything outside the tree is a
URL*, `cli.md` states the boundary explicitly, and `charter.md:52` is converted
to the canonical GitHub URL in Phase 6 — the same treatment Q1 gives the two
`adoption-playbook` links, and doubly right because the relative alternative
would itself have violated Q5. A containment census over `docs/`, all 33
fixture trees and the bundled skill confirms **exactly one** escape exists and
**no fixture needs updating**. **Phase 1 re-opened none of this**: it froze the
grammar and its exactness rules, the masking contract and its ordering,
destination classification, the containment test and **its precedence over
existence**, **both** message templates, and the `BodyLink` span record — in
`cli.md` › *Markdown body-link validation*, `convention.md` › *Body links*,
and the milestone's *Decisions (Phase 1 — BINDING)*. Three setup-frozen items
were amended under conductor decision and recorded as amendments:
`broken-body-link`'s message (D4's "to a file" contradicted the
operator-binding Q7, under which a **directory** also satisfies a
destination), `outside-root-body-link`'s message (D4b never gave one), and the
33-tree no-new-findings lock (a **new sibling** test, because the existing
one's list covers 23 trees and would fail on the damaged `bodylink-*`
fixtures). The package version stays **1.8.0**
(M25 — D6); CHANGELOG entries accumulate under `UNRELEASED` for M29. The
prepared pair is
[m27-markdown-body-link-validation.md](m27-markdown-body-link-validation.md)
and
[m27-markdown-body-link-validation-impl.md](m27-markdown-body-link-validation-impl.md).

**M26 — Safe explicit archive selection is
implementation-complete — all ten TDD phases done 2026-08-13 (Step 1 on
`m26/phases-1-4`, Step 2 on `m26/phases-5-10`). Full suite 895 GREEN, with
774 of the 777 pre-existing test ids mechanically proven present and passing
and 3 deliberately removed.** M26 decouples relationship context from archive
authorization: bare `docs archive FILE --cascade` refuses before any write,
`--interactive` is retired under the same refusal, `--cascade-dry-run` keeps
previewing every one-hop candidate (selected, not-selected, or ineligible),
and every write that includes a related document requires an explicit
`--cascade-only GLOB` scope whose full plan is validated — deduplicated,
canonical-path matched, collision- and writability-checked, archived
neighbours excluded — before the first byte moves. `docs archive` also gains a
`--json` operation-plan record, one shape for preview and apply, reusing
M25's `relate --json` pattern. Setup reproduced five concrete v1.8.0 defects
(**E1–E5**), each now mapped to named regression coverage: the headline is
that `docs archive m25-reciprocal-relationship-integrity.md --cascade` would
archive `plan.md`, `cli.md`, `convention.md`, `test-strategy.md`, and
`status.md` — this project's whole specification spine — with no prompt; a
basename collision or a typo'd scope leaves a partial archive that exits 0;
and an archive-subtree `pairs-with` edge makes `--cascade` silently relocate
and re-date an already-archived document (data corruption, load-bearing here
because `status.md` carries 20+ archive-subtree edges). **All seven setup
questions are RESOLVED** — Q1 retire `--interactive`, Q2 keep the refusing
flags registered, Q3 retain the `pairs-with`/`child-of` candidate set, Q4
exclude archived candidates and refuse an archived primary, Q5 pre-flight
everything with a partial-state admission instead of rollback (extending
M25 — D5's rollback to N docs explicitly declined), Q6 add
`docs archive --json`, Q7 no primary-only candidate notice. Phase 1 did not
re-open them: it froze the compatibility matrix (no "it depends" cell), the
refusal / preview / apply / partial-state message catalog, the exit-code split
(exit 1 stays for the three conditions 1.x already assigned it; the five new
M26 refusals exit 2), the `--json` schema and field table, and the Phase-5
signatures — in `cli.md`, `convention.md`, and the milestone's *Decisions
(Phase 1 — BINDING)* section, which also records seventeen resolved Step-1
planning questions. **A preview never fails**: a `--cascade-only` that selects
nothing exits 0 under `--cascade-dry-run` and 2 on a write, and the D5/D6
contradiction that allowed both readings is amended away. The package version
stays **1.8.0** (M25 — D6); CHANGELOG entries accumulate under `UNRELEASED`
for M29. The prepared pair is
[m26-safe-archive-selection.md](m26-safe-archive-selection.md) and
[m26-safe-archive-selection-impl.md](m26-safe-archive-selection-impl.md).

**M25 — Reciprocal relationship integrity and `docs relate` is
IMPLEMENTATION-COMPLETE — all ten TDD phases are done
(Phases 1–4 2026-08-11 amended 2026-08-12 on `m25/phases-1-4`; Phases 5–10
2026-08-12 on `m25/phases-5-10`). It stays `Lifecycle: active` until the
M29 publish closeout.** M25 defines three reciprocal relationship
pairs (`precedes`/`follows`, `depends-on`/`required-by`, and
`blocks`/`blocked-by`), makes a missing exact inverse a hard `docs check` error,
and adds explicit two-endpoint `docs relate add/remove` repair, including a
narrow reasoned/audited exception for archived endpoints. Phase 1 froze the
whole surface in the milestone's *Decisions (Phase 1 — BINDING)* section and in
`cli.md` / `convention.md`: the six-verb inverse map, the `missing-inverse`
finding and its exact message, the `relate` grammar / human / JSON / dry-run
output, root-relative-first endpoint resolution, the archived `--reason` +
`Revision:` audit rules, and the staged-publish-with-rollback failure contract.
All five Phase-1 open questions are RESOLVED. Phase 2 wrote the RED suite
across six edited and two new test files, Phase 3 added ten committed
`reciprocal-*` fixture trees, and Phase 4 captured the classified RED
baseline. Including the same-instance audit and the fresh-eyes review
fold-in, Step 1 contributed **121 test items** and the RED baseline was
**757 collected, 87 failed, 670 passed** — every RED matching its classified reason, zero
collection errors, and the 636 pre-existing tests all still GREEN. The
review returned **no blockers**; its two operator-binding contract
amendments (a self-referential recognized edge is **exempt** from
`missing-inverse`, and reciprocity matches on **canonical** root-relative
paths so a `./` prefix cannot fail a hard check) are folded into the
specs, the bundled mirrors, and the tests. **Step 2 (Phases 5–10) is
complete on `m25/phases-5-10`: the full suite is 777 passed / 0 failed,
every one of the 636 pre-existing test ids proven still GREEN by `comm`
against the Phase-1 commit, and the eight-flow dogfood ran unattended on a
throwaway copy of this tree.** Phase 5 landed the vocabulary, the three
`Related:`/`Revision:` editors, the planning models, and the `Revision`
built-in label; Phase 6 landed the cross-document reciprocity pass
(interleaved into `check_tree`'s per-doc grouping) and the
validate-all-first coordinated edit with its staged-publish-and-rollback
contract; Phase 7 wired `docs relate add|remove`, added the bundled
skill's verb row, opened an `UNRELEASED` CHANGELOG section, and folded
eight conductor-resolved spec corrections into `cli.md` (a
nothing-was-published rollback branch, a remove-shaped `ROLLBACK FAILED`
admission, the stage-3 refusal string, root-relative promises scoped to
*resolved* endpoints, the `--json`-on-failure rule, and `Revision:`
following the tree's `date_format`). Phase 8 proved the GREEN gate and zero
pre-existing regressions — and corrected, under operator approval, one
Step-1 assertion that was unsatisfiable alongside another test in the same
file (the replacement is stronger; the shipped behaviour did not move).
Phase 9 dogfooded detect → repair → re-check plus an audited archived
repair, touching 1 of 46 archived files. Phase 10 closed
`architecture.md` / `test-strategy.md`, added the upgrade-and-repair flow to
the shipped use-case catalog, and wrote the completion summaries. An
independent fresh-eyes review then returned **no blockers**; its fold-in
fixed two real editor defects (trailing-newline state was not preserved
when the metadata block runs to EOF — a D4 allowed-byte violation; and a
re-created `Related:` group landed after a trailing `Revision:` group),
added four missing failure-path locks, and carried one
**operator-approved post-freeze scope addition**: the **`duplicate-field`**
check rule (D7). A metadata label may now appear at most once — a second
copy silently replaced the first and discarded its values, a data-loss
defect predating M25 that also made one `missing-inverse` state unfixable.
The live tree and all 28 fixture trees were verified duplicate-free before
it landed. Suite: **777 passed**.
**Version staging (Q5):
`docs-cli` stays `1.8.0` through M25–M28; M29 performs the single bump to
`2.0.0` at publish.** The prepared pair is
[m25-reciprocal-relationship-integrity.md](m25-reciprocal-relationship-integrity.md)
and
[m25-reciprocal-relationship-integrity-impl.md](m25-reciprocal-relationship-integrity-impl.md).

The full breaking safety train is registered in execution order:

- **M26 — Safe explicit archive selection (IMPLEMENTATION-COMPLETE
  2026-08-13, all ten TDD phases, 895 GREEN):** unscoped related-document
  writes refuse; preview remains and names the whole neighborhood; explicit
  `--cascade-only` scope is required, planned in full before any write;
  `docs archive --json` emits the operation plan. Stays `Lifecycle: active`
  until the M29 publish closeout.
- **M27 — Markdown body-link validation (IMPLEMENTATION-COMPLETE
  2026-08-14, all ten phases, all seven setup questions RESOLVED):** a bounded stdlib-only
  scanner with exact destination spans; two hard errors —
  `broken-body-link` for a missing in-root destination and
  `outside-root-body-link` for one that leaves the tree, decided by path
  arithmetic so the check never stats outside its own root; and a one-time
  audited repair of the live tree's 139 archived breaks (all under `archive/`,
  132 of them a single un-rebased `../../`) plus the one escaping active
  link.
- **M28 — Move-safe body-link rewrites (IMPLEMENTATION-COMPLETE — all ten TDD
  phases done 2026-08-15, all seven setup questions RESOLVED):**
  depends on M26 + M27; preserves both incoming
  links to moved targets and links inside moved referrers — one formula over
  M27's spans, mapped on the normalised target — plans before it moves so a
  handled failure writes zero bytes, rewrites archived referrers under M18's
  widened move-driven exception, and (added 2026-08-15) refuses a move whose
  plan would strand a still-active document — on a predicate Q1 narrowed to the
  `child-of` direction so it cannot fire on a legitimate closeout, paired with
  a report of every other still-active inbound reference.
- **M28a — Structured archive-date witness (IN FLIGHT, Step 1 — Phases 1–4 —
  complete on `m28a/phases-1-4`; all seven setup questions RESOLVED, the
  contract frozen, and 149 classified RED-baseline test ids plus six fixture
  trees authored against it):** depends on M26; **two
  legs**. Detect — an `Archived:` field written to **every** document an
  archive operation moves, not to the primary only, plus a present-only
  `archive-date-drift` rule reporting a document whose recorded date its
  location does not corroborate. Prevent — `docs mv` refuses a move between two
  different dated archive directories, before any write, for every archived
  document whether or not it carries the field (Q4, operator). Setup measured
  that exactly one of the four relocation paths is silent, that it is reachable
  through `docs mv` in one command, and that M28 removed the tree's only
  accidental alarm for it — which is why M28a blocks M29.
- **M29 — PyPI publish 2.0.0:** depends on M25–M28a and releases them together.

The six plans use reciprocal sequence edges and only real durable dependency
edges; no `blocks`/`blocked-by` edge exists because planned prerequisites are
not transient blockers. M26, M27, M28 and M28a all have full task plans and
implementation logs; M29 remains a draft stub with no implementation log or
phase started.
Because those edges are already complete in both directions,
this tree passes M25's new hard rule as-is — the existing dogfood
`docs check docs/` gate doubles as an M25 lock.

**docs-cli 1.8.0 shipped 2026-07-03 — the v1.8.0 train is complete.**
**M24 — PyPI publish 1.8.0** is **Complete (2026-07-03)**: `docs-cli==1.8.0`
is live at https://pypi.org/project/docs-cli/1.8.0/, the operator-driven
**batched** publish of the whole post-1.6.5 train — **M21** (update-check,
built as 1.7.0) + **M22** (doc-only root-placement guidance, no bump) + **M23**
(agent-aware install-skill, 1.8.0) — as one public release (mirroring M17 =
M14+M15 → 1.6.0 and M9 = M6+M7+M8 → 1.3.0). **1.7.0 was skipped on PyPI** — its
CHANGELOG entries were folded into the dated `## 1.8.0` section (D2). The
`v1.8.0` annotated tag points at the Phase-4 dated-CHANGELOG commit
(`1a01f74`); the GitHub release carries the `## 1.8.0` notes. Chain-of-custody
verified **bit-perfect for both wheel AND sdist** — PyPI-served wheel `29ac3ced…`
+ sdist `62a29285…` byte-identical to the local Phase-4 build; all M21 + M23
headline contracts hold against the PyPI-served wheel (update notice + M23
skill-refresh hint fire to STDERR under the seeded-cache probe, exit-parity,
full suppression matrix; install-skill `--dest` records path-only, non-TTY
falls back to default, "agent skill" wording). Ran the
[release-runbook.md](release-runbook.md) on `main` (no TDD code phases) —
driven under **D3** "author now, confirm at the gate": the operator authorized
the irreversible upload + `main` push + tag + release at the Phase-4 gate (not
M20's up-front full-autonomous authorization). **D4:** M23 OQ-1/OQ-2 confirmed
as-shipped (branch-review flag cleared, no re-bump). The closeout refreshed the
host-machine skills (`docs install-skill --force` → host `docs` byte-identical;
workflow-skill sweep found no docs-cli drift this release) per the CLAUDE.md
skill-update-flow policy, and archived the M21 + M22 + M23 pairs + M24's own
milestone doc to `archive/2026-07-03/`; the M24 impl log, release-runbook, and
this status doc stay `Lifecycle: active`. Full publish record + deviations live
in [m24-pypi-publish-impl.md](m24-pypi-publish-impl.md)'s milestone-completion
summary.

**M22 — Doc-tree root placement guidance (project ≠ directory)** is
**implementation-complete (2026-06-24)** — all ten TDD phases done; full
suite 543 GREEN, ruff/format/mypy clean, `docs check docs/` exit 0; Phase-9
dogfood empirically reproduced the redundant-prefix consequence. It **stays
LIVE at root, lifecycle `active`**, to be swept into the archive at the next
publish closeout (the M18/M19/M21 + M16 precedent — feature/skill milestones
ride live until a later milestone archives them). A documentation-only,
M16-shaped milestone (no CLI/code
change, no version bump): it adds "where to put `.docs.toml`" guidance to
`convention.md` §Subdirectories and the bundled `SKILL.md`, making explicit
that `Project:` is a metadata slug — **not** a directory — and that because
`Related:` paths are root-relative, nesting a lone project beneath a parent
root prefixes every intra-project sibling reference with a redundant
`<subdir>/`. Default: a single project's docs root is the project's own
directory (root = project, docs flat, clean refs); reserve per-project
subdirs under one shared root for genuinely multi-project trees. Scoped to
run **before** M21 (operator decision 2026-06-24 — run-order before M21, no
renumber; milestone numbers here are creation-order, not execution order, as
M14+M15→M17 / M18+M19→M20 already show). The matching `project-foundation`
note is a separate companion follow-on in the `agent-playbook-suite` repo
(tracked with the workflow-skill drift-lint follow-on). Pair:
[m22-root-placement-guidance.md](archive/2026-07-03/m22-root-placement-guidance.md) +
[m22-root-placement-guidance-impl.md](archive/2026-07-03/m22-root-placement-guidance-impl.md);
**shipped to PyPI as `docs-cli==1.8.0` (batched via M24) 2026-07-03; the pair is now archived to `archive/2026-07-03/`.**

**M21 — Update-check notification (PyPI new-version notice)** is
**Complete — shipped to PyPI as `docs-cli==1.8.0` (batched via M24) 2026-07-03;
pair archived to `archive/2026-07-03/`**: **all 10 TDD phases are complete (2026-06-29)** —
Phases 1–4 (RED baseline) on branch `m21/phases-1-4`, Phases 5–10 on
`m21/phases-5-10`. The `update_check.py` seam (cache I/O, numeric fail-closed
compare, injectable `urllib` fetch hook, suppression predicates, notice
formatter) + the `main()` post-dispatch hook are implemented; `pyproject` is at
**1.7.0** (editable reinstall → `docs --version` = `docs 1.7.0`); the full suite
is **604 GREEN** (+4 from the 2026-06-29 Step-2 fresh-eyes review fold-in) with
the gate clean tree-wide (ruff / ruff format --check /
mypy / `docs check docs/`). The Phase-9 online path was verified against live
PyPI (real `urllib`) and dogfooded end-to-end (notice / both 24h throttles /
the full suppression matrix / `--json` byte-clean stdout / exit-code parity);
pytest stays 100% offline. **Re-scoped to CLI-only 2026-06-29**
(was "PyPI version check + skill-refresh nudge"): the former offline skill-drift
notice (D5) and the dual-action `docs install-skill --force` half are **CUT**,
and the skill story moves to the new follow-on **M23**. Headline: `docs-cli`
checks PyPI for a newer release and, once per 24h and **fail-silent**, emits ONE
STDERR line nudging the user/agent to update **the CLI**
(`pip install -U docs-cli`). New reference wording:
`docs: update available <current> -> <latest> — run: pip install -U docs-cli`.
This is the tool's **first network surface** (stdlib `urllib` only, 1.0s
timeout, 24h-cache-gated under
`${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json` with a three-key
`{last_check, latest_version, last_notified}` schema, fail-silent always — the
zero-dependency wheel preserved). The notice is STDERR-only, **never** alters
the exit code, and is suppressed under `--quiet` / `--json` / `CI` /
`DOCS_CLI_NO_UPDATE_CHECK` / `DO_NOT_TRACK` (a user-level config opt-out is
DEFERRED out of v1.7.0 — OQ-5/5a) — but **deliberately shows on non-TTY**
(inverting gh's TTY rule) because the agent is the actor who performs the
update. Ships as **1.7.0** (minor bump — additive feature; 1.6.5 was the
operator-decreed patch exception); the PyPI publish is a later operator-driven
milestone (the M19→M20, M14+M15→M17 pattern). The milestone pair is
[m21-update-check.md](archive/2026-07-03/m21-update-check.md) +
[m21-update-check-impl.md](archive/2026-07-03/m21-update-check-impl.md); the pair was swept to `archive/2026-07-03/` at the M24 closeout (the
M14/M15/M18/M19 precedent). **OPEN QUESTIONS are netted out — none outstanding.** The original
OQ-1..OQ-9 are RESOLVED (conductor decisions 2026-06-12, each per the
recommended default) with one amendment by the re-scope: **OQ-6 (ship D5) is
REVERSED to NO** (D5 CUT; skill story → M23); the dual-notice ordering question
is moot (single notice now). Surviving resolved findings: the dedicated
`update_check.py` module stands (OQ-7; the B3 wheel-contents test tolerates it);
the suite sets `DOCS_CLI_NO_UPDATE_CHECK=1` in `tests/conftest.py` to stay
offline; cache timestamps are ISO-8601 UTC; the baseline test count is **543**.
**Shipped to PyPI as `docs-cli==1.8.0` (batched via M24) 2026-07-03.** See the
milestone doc's Decisions › "Re-scope to CLI-only".

**M23 — Agent-aware install-skill + recorded-dest skill-refresh hint** is
**Complete — shipped to PyPI as `docs-cli==1.8.0` (batched via M24) 2026-07-03;
pair archived to `archive/2026-07-03/`** — the follow-on that restores the
skill-refresh nudge cut from M21. **All ten TDD phases are done (2026-07-02)** — Phases 1–4
(Contract & RED baseline) on branch `m23/phases-1-4`, Phases 5–10 on
`m23/phases-5-10`: the full suite is **636 GREEN**, gate clean tree-wide
(ruff / format / mypy / `docs check docs/` all clean), `pyproject` at **1.8.0**
(editable reinstall → `docs --version` = `docs 1.8.0`), and the online path was
dogfooded end-to-end against a seeded throwaway cache (pytest stays 100%
offline). It
makes `docs install-skill` **agent-aware**: `--dest` is the agent-agnostic
source of truth, resolution is TTY-aware (a human may be prompted; an agent
[non-TTY] is **never** blocked on a prompt → falls back to the default), the
resolved dest is **recorded** to a small per-user state file (a *path* only —
**never** the skill's content), the "Claude Code skill" framing in
`install-skill`'s help/description/docstrings is neutralised to
**"agent skill"** (reconciled with `cli.md`; a stale-wording grep across the
install-skill surface is clean), and M21's update notice gains a
skill-refresh hint pointed at the **recorded** dest (riding M21's same
suppression matrix + throttle). Replay/remember is allowed; content-inspection
and agent-guessing are NOT (the exact line the cut D5 crossed). Out of scope:
multi-agent skill *formats* and agent auto-detection. **Depends on M21**
(extends its notice channel). Ships **1.8.0** (OQ-4). **The four OPEN
QUESTIONS are resolved** (see the milestone doc Decisions): OQ-1 = non-TTY
**default** (never refuse), OQ-2 = a **separate** `${XDG_STATE_HOME:-~/.local/state}/docs-cli/install-skill.json`
(M21's 3-key cache stays frozen), OQ-3 = last-write-wins single dest, OQ-4 =
**1.8.0** — OQ-1/OQ-2 were resolved **provisionally while the operator was
away** and were **confirmed as-shipped at the M24 publish gate (D4, 2026-07-03)** —
the branch-review flag is cleared. The pair is
[m23-agent-aware-install-skill.md](archive/2026-07-03/m23-agent-aware-install-skill.md) +
[m23-agent-aware-install-skill-impl.md](archive/2026-07-03/m23-agent-aware-install-skill-impl.md);
the pair was archived to `archive/2026-07-03/` at the M24 closeout.

**docs-cli 1.6.5 shipped 2026-06-12 — the v1.6.5 train is complete.**
**M20 — PyPI publish 1.6.5** is **Complete (2026-06-12)**:
`docs-cli==1.6.5` is live at https://pypi.org/project/docs-cli/1.6.5/, the
operator-driven publish-only counterpart to **M19**, shipped **one-to-one**
(as M13 shipped M12 and M11 shipped M10; M9 and M17 were the batched shapes).
The `v1.6.5` annotated tag points at the M20 Phase-4 dated-CHANGELOG commit
(`0855466`); the GitHub release carries the `## 1.6.5` CHANGELOG notes.
Chain-of-custody verified **bit-perfect for both the wheel AND the sdist**
(M20 extended the M17 wheel-only check) — PyPI-served wheel sha256
`aba36e92…` + sdist `f9de1eb4…` byte-identical to the local Phase-4 build;
all M19 headline contracts hold against the PyPI-served wheel (`touch
--check` exit fold clean/stale; `--stale` requires `--check`; `[check]
stale_days` arms bare check + CLI override + non-integer refusal; both
provenance variants; `--body-from` help = real detector). Ran the
[release-runbook.md](release-runbook.md) end-to-end as a fully-autonomous
pass (no TDD code phases — the runbook sections are the phases, on `main`).
**NEW vs M17:** the Phase-5 closeout refreshed the host-machine skills
(`docs install-skill --force` from the published 1.6.5 → host `docs` skill
byte-identical to the published bundled skill; a workflow-skill sweep that
caught + fixed one stale `--body-from` reference in `project-foundation`) per
the CLAUDE.md skill-update-flow policy. The M20 closeout archived the M18
pair + the M19 pair + M20's own milestone doc to `archive/2026-06-12/`; the
M20 impl log, release-runbook, and this status doc stay `Lifecycle: active`.
Full publish record + deviations live in
[m20-pypi-publish-impl.md](m20-pypi-publish-impl.md)'s milestone-completion
summary.

**M19 — Post-edit validation ergonomics (touch --check + configurable stale
window)** is **Complete (2026-06-12)** — **shipped to PyPI as
`docs-cli==1.6.5` via M20 on 2026-06-12** (operator decision 2026-06-12 —
1.6.5, not 1.7.0; M20 was the publish-only milestone, one-to-one). Three
deliverables: (D1) `docs touch --check [--stale N]` folds the existing
`check_tree` machinery into `docs touch` after its end-of-batch reindex, so
the three-command post-edit loop (`touch` → `index` → `check --stale 14`)
collapses to one invocation; (D2) a `.docs.toml [check] stale_days = N`
per-tree default the stale window reads from when no CLI `--stale` is given
(CLI `--stale` overrides; absent config preserves today's behaviour); (D3)
the cosmetic `docs new --body-from` help-string fix closing the rolled-forward
follow-on. No new verb, no new check rule — additive + backward-compatible.
A post-draft operator addition (2026-06-12) folds **threshold provenance** into
D2 — the stale finding names where the window is set (`set in .docs.toml
[check] stale_days` config-sourced, `via --stale` CLI-sourced). The milestone
pair is
[m19-post-edit-validation.md](archive/2026-06-12/m19-post-edit-validation.md)
+ [m19-post-edit-validation-impl.md](archive/2026-06-12/m19-post-edit-validation-impl.md);
it was archived to `archive/2026-06-12/` at the M20 closeout. The six questions (Q1–Q6 — exit-code folding, check
scope, `--stale`-without-`--check`, `--dry-run --check`, whether a configured
`stale_days` makes bare `docs check` apply the stale rule, and whether it
feeds `docs list --stale`) are **RESOLVED** (operator decisions 2026-06-12,
each per the recommended default — see the milestone doc's Decisions). **Step 1
(Phases 1-4 — Contract + RED baseline) complete on branch `m19/phases-1-4`**
(2026-06-12): contract specs frozen, 23 new tests written RED across 5 suites +
the version-pin flip to 1.6.5, inline today-relative fixtures, RED baseline
captured (533 collected, 19 RED, 514 GREEN). **Step 2 (implement & ship,
Phases 5-10) complete on branch `m19/phases-5-10`** (2026-06-12):
`Config.stale_days` + `load_config` `[check]` read, `resolve_stale`
precedence/provenance helper, `stale_source` threading, `touch --check`/`--stale`
flags (Phase 5); `check_doc` provenance suffix + `_cmd_touch` check-fold +
`_run_touch_check`/`_print_check_findings` + D3 help fix (Phase 6, after the
mandatory OQ-2 message-regression audit — zero regression); version 1.6.5 +
packaging lockstep + `## 1.6.5 — UNRELEASED` CHANGELOG (Phase 7); **full suite
533/533 GREEN, gate clean, `docs --version` → `docs 1.6.5`** (Phase 8); all 5
dogfood exercises GREEN + config path verified on a throwaway `docs/` copy
(OQ-3 — repo tree not adopted) (Phase 9); surface-parity gate + SKILL.md verb
table (OQ-4) + standalone `python -m build` & `twine check` both PASSED locally
(Phase 10). The full suite reached **540 GREEN** (533 + the Step-2 review +7).
**M20 published it to PyPI as `docs-cli==1.6.5` on 2026-06-12**; the M19 pair
was archived to `archive/2026-06-12/` at the M20 closeout.

**M18 — Archive edge integrity (intra-archive Related: rewriting)** is
**implementation-complete (2026-06-03)**. The correctness fix to
`docs archive` (rewrite the moved doc's own archive-subtree `Related:`
edges + repoint already-archived referrers, via the conditioned
archived-skip in `_rewrite_referring_edges`) landed, and its Phase-9 payoff
archived the completed-milestone backlog on the live tree — see the
*Completed-milestone doc archival is DONE* note below. **The M18 pair was
archived to `archive/2026-06-12/` at the M20 closeout** (it rode along in the
1.6.0 tree as an already-merged archive-edge fix and added no new public
surface to 1.6.5; the archival is a doc-lifecycle sweep, not a code ship).
Full suite 510 GREEN at M18 close, gate clean tree-wide.

**M16 — Bundled docs skill quality artifacts** was implementation-complete
2026-06-01 and is now **archived** (trio → `archive/2026-06-01/` by M18's
Phase-9 sweep): the Agent Playbook Suite risk-aware quality upgrade, scoped
to the bundled `docs` skill under `src/docs_cli/skill/` (document test
matrices, quality logs, generated report artifacts, and the mechanical
limits of `docs check`). The milestone pair is now
[archive/2026-06-01/m16-bundled-docs-skill-quality.md](archive/2026-06-01/m16-bundled-docs-skill-quality.md)
+ [archive/2026-06-01/m16-bundled-docs-skill-quality-impl.md](archive/2026-06-01/m16-bundled-docs-skill-quality-impl.md).

**Completed-milestone doc archival is DONE (2026-06-03), via M18.** The
[M18 — Archive edge integrity](archive/2026-06-12/m18-archive-edge-integrity.md) fix landed
(the conditioned archived-skip in `_rewrite_referring_edges`), and its
Phase-9 payoff archived the completed-milestone backlog on the live `docs/`
tree in strict completion-date order — `docs check docs/` exit 0 after every
op and at the end. Manifest:
- M1–M9 plan/log pairs → `archive/2026-05-{20,21,22,22,23,24,25,25,25}/`
  (each archived the LOG with `--cascade-only "<plan>"`; `child-of` pulls
  the plan, so both land together edge-clean);
- M12 plan/impl pair → `archive/2026-05-28/`;
- the three stray impl-logs swept into their plans' existing folders —
  `m10`/`m11` → `archive/2026-05-27/`, `m13` → `archive/2026-05-29/`
  (each repointed its already-archived plan's `parent-of` edge, the M18
  D2 flip);
- the M16 trio (plan + impl + test-matrix) → `archive/2026-06-01/`
  (`--cascade-only "m16-*"`).
Live referrers (architecture.md, plan.md, status.md, release-runbook.md)
were repointed automatically to the new archive paths. **M18 (both pairs)
is LEFT LIVE at root** — it is itself the in-flight milestone (a milestone
is not self-archived; it flips to `archived` only when a later milestone
sweeps it in). **M14 + M15 + M17 were archived to `archive/2026-06-03/` at
the M17 closeout** (see the v1.6-publish note below).

**docs-cli 1.6.0 shipped 2026-06-03 — the v1.6 train is complete.**
**M17 — PyPI publish 1.6.0** is **Complete (2026-06-03)**:
`docs-cli==1.6.0` is live at https://pypi.org/project/docs-cli/1.6.0/,
the operator-driven publish that shipped **M14 + M15 together** as one
public release (batched, as M9 shipped M6+M7+M8; M11→M10 and M13→M12 were
one-to-one). The `v1.6.0` annotated tag points at the M17 Phase-4
dated-CHANGELOG commit (`95f23a6`); the GitHub release carries the
`## 1.6.0` CHANGELOG notes. Chain-of-custody verified **bit-perfect**
(PyPI-served wheel sha256 `b0822709…` byte-identical to the local Phase-4
build); all seven M14 + M15 headline contracts hold against the
PyPI-served wheel (M14 `mv` all-or-nothing; M14 `new` strict-root refusal;
M14 non-interactive `archive --cascade` + `--cascade-dry-run`; M14
four-verb exclude-honouring reindex; M15 `project set` atomic + typo
guard; M15 single-file `stamp`; M15 `--body-from` real-frontmatter
detector). Ran the [release-runbook.md](release-runbook.md) end-to-end as
a fully-autonomous pass (no TDD code phases — the runbook sections are the
phases, mirroring M9/M11/M13). Full publish record + deviations live in
[m17-pypi-publish-impl.md](m17-pypi-publish-impl.md)'s
milestone-completion summary.

- **M14 — Robustness + autonomous archive** (impl-complete 2026-06-02):
  `docs mv` atomicity, `docs new` strict-root refusal, the four-verb
  `touch`/`archive`/`mv`/`project rename` exclude-predicate fix,
  slug/`OSError`/`atomic_write`-fsync guards, non-interactive
  `archive --cascade`, the bundled-ref guard + packaging fix.
- **M15 — Agent-native doc authoring** (impl-complete 2026-06-03, carved
  from M14): `docs project set`, single-file `docs stamp`
  (write-then-stamp), the `--body-from` real-frontmatter detector, and
  the skill/cli docs. **Depends on M14.**

Both built `docs-cli==1.6.0` locally against the same CHANGELOG section;
M17 published them together. Their milestone pairs (plan + impl, four
docs) **and** the M17 milestone doc were archived to `archive/2026-06-03/`
at the M17 closeout via `docs archive` (the Q2 decision); the M17 impl
log, release-runbook, and this status doc stay `Lifecycle: active` per the
M8/M9/M10/M11/M13 pattern. **M18 is untouched — a separate in-flight
milestone.**

**docs-cli 1.5.0 shipped 2026-05-29.** **M13 — PyPI publish
1.5.0** is **Complete (2026-05-29)** — `docs-cli==1.5.0` is
live at https://pypi.org/project/docs-cli/1.5.0/, the
publish-only counterpart to M12 (mirroring M11 → M10 and
M9 → M8). The `v1.5.0` annotated tag points at the M13 Phase 4
commit; the GitHub release carries the `## 1.5.0` CHANGELOG
notes. Chain-of-custody verified bit-perfect (PyPI-served
wheel sha256 byte-identical to the local Phase 4 build); all
four M12 headline contracts (project rename round-trip; touch
outside-root refusal; archive referring-edge rewrite;
`importlib.metadata` version SoT) hold against the PyPI-served
wheel. The milestone pair is
[m13-pypi-publish.md](archive/2026-05-29/m13-pypi-publish.md)
(archived at closeout) +
[m13-pypi-publish-impl.md](archive/2026-05-29/m13-pypi-publish-impl.md); the
operative checklist was
[release-runbook.md](release-runbook.md). Full publish record
+ deviations live in the impl log's milestone-completion
summary.

**M12 — Project rename + M11 wart fixes + version SoT (v1.5.0)**
is **Complete (2026-05-28)** — `dist/docs_cli-1.5.0-py3-none-any.whl`
+ `dist/docs_cli-1.5.0.tar.gz` built locally, twine check PASS,
433/433 pytest GREEN at simplify close; PyPI publish is M13's
scope (mirroring the M10 → M11, M8 → M9 cadence). M12 bundled four threads in
one TDD cycle:

1. **`docs project rename <new-name>`** — operator-facing
   headline; the M10 follow-on TODO captured at
   [archive/2026-05-27/m10-adoption-polish.md](archive/2026-05-27/m10-adoption-polish.md)
   lines 261-268. Atomic semantics (validate up-front, fail the
   whole batch on any error, commit only after validation pass,
   refresh INDEX once at end) mirroring `docs touch` (M2) +
   `docs migrate --apply` (M10). Rewrites `.docs.toml`
   `[project] name` + every conformant `Project:` line across
   active docs. Archive subtree is read-only (M3 stance).
2. **`docs touch <path>` outside any docs root → exit 2.**
   Burn-down of the M11 Phase 5 wart: `docs touch` on a file
   outside any `.docs.toml`-rooted tree currently inserts an
   unwanted `Updated:` line and then crashes the downstream
   INDEX refresh on whatever sibling first fails its Lifecycle
   check (M11 caught this when accidentally touching
   `CHANGELOG.md` from the repo root). M12 refuses cleanly with
   exit 2 + clear stderr; file unchanged; no INDEX refresh.
3. **`docs archive <doc>` rewrites referring `Related:` edges.**
   Burn-down of the M11 Phase 5 wart: archiving a doc moves
   the file but leaves referring `Related:` edges in other docs
   pointing at the pre-archive path (M11 Phase 5 ran a manual
   cleanup for `status.md` + impl log). M12 makes the rewrite
   atomic with the move — same machinery `docs mv` already
   uses (M2 Phase 6).
4. **`importlib.metadata` version single-source-of-truth.**
   Parked since M6. `src/docs_cli/cli.py` `__version__` becomes
   `importlib.metadata.version("docs-cli")`; `pyproject.toml`
   `version` is the single SoT. Eliminates the two-place version
   hardcode (and the corresponding lockstep-bump discipline) at
   every implementation milestone.

M12 shipped locally as 1.5.0 on 2026-05-28. The four features
(`docs project rename`, `docs touch` outside-root refusal,
`docs archive` referring-edge rewrite, `importlib.metadata`
version SoT) all landed atomically; the validate-all-first
pattern proved robust across the 17 project-rename + 4 touch +
6 archive new tests. Phase 9 dogfood PASS on all four
exercises (kebab-tiny round-trip byte-identical; orphan touch
refused; archive referring-edge rewrite atomic; repo's own
docs/ round-tripped byte-identical). OQ-1 through OQ-11
(Phase 1 scope decisions) + OQ-α through OQ-ι (Step 2
implementation decisions) all auto-resolved per operator
recommendation. M13 is the publish counterpart
(release-runbook-driven, mirrors M11 with the M11 lessons
already folded into the runbook).

**docs-cli 1.4.0 shipped 2026-05-27.** **M11 — PyPI publish
1.4.0** is complete: `docs-cli==1.4.0` is live at
https://pypi.org/project/docs-cli/1.4.0/, the publish-only
counterpart to M10 (mirroring M9's relationship to M8). The
`v1.4.0` tag points at the M11 Phase 4 commit; the GitHub
release lives at
https://github.com/ArtRichards/docs-cli/releases/tag/v1.4.0.
Chain-of-custody verified **bit-perfect** — the PyPI-served
wheel sha256 (`7af7eb5c…`) is byte-identical to the local
Phase 4 build. The headline M10 contract
(`docs migrate --apply --quiet` produces empty stdout + empty
stderr; `.docs.toml` auto-emitted with `[project]` +
`[archive]`) was re-verified against the PyPI-served wheel
during Phase 4 smoke against a synthetic foreign tree. The
TestPyPI rehearsal again ran under the disambiguated dist
name `docs-cli-rehearsal==1.4.0` (the bare `docs-cli` on
TestPyPI is still parked by the M9-era squatter at 0.1.0; the
detour rolls forward to v1.5+). See
[m11-pypi-publish.md](archive/2026-05-27/m11-pypi-publish.md)'s
milestone-completion summary for the full publish record +
deviations; the
[release-runbook.md](release-runbook.md) stays the operative
reference for future releases.

**M10 — Adoption-flow polish + 1.3.0 carry-overs** is
**Complete (2026-05-27)** — shipped to PyPI as 1.4.0 via M11
on 2026-05-27. The milestone bundled the two user-surfaced
agent-driveability features (`docs touch <file...>` with
multi-file atomic semantics, `docs migrate --apply` writes
`.docs.toml` automatically + opportunistic empty-archive-
parent rmdir) with the carry-overs from M3 (`[vocabulary]
add_fields` allowlist + `unknown-field` check rule), M7
(`Confidence` enum replacing the `bool | str` tri-value), and
M8 (`--apply --quiet` per-file output suppression,
`MigrationPlan.excluded_count` removal, adoption-playbook
restructured to 4 steps). 400/400 pytest GREEN at M10 close
(401/401 across M11 phases — Phase 1 added the `~/.pypirc`
+ ownership inventory). Phase 9 kebab-tiny dogfood (in
`/tmp/m10-dogfood` against the 1.4.0 wheel in
`/tmp/docs-m10-venv`) confirmed `--apply --quiet` produces
empty stdout + empty stderr, the auto-emitted `.docs.toml`
carries OQ-A's `[project]` + OQ-M's `[archive] date_format`
under the provenance header, and `docs check` exits 0
immediately. See
[m10-adoption-polish-impl.md](archive/2026-05-27/m10-adoption-polish-impl.md)
for the per-phase log; the milestone doc was archived at
Phase 10 closeout per the M8/M9 pattern (impl log stays
Lifecycle: active).

**docs-cli 1.3.0 shipped 2026-05-25.** **M9 — PyPI publish
1.3.0** is complete: `docs-cli==1.3.0` is live at
https://pypi.org/project/docs-cli/1.3.0/, batching the M6 + M7
+ M8 surface into one public release. (The release closes the
M6 → M9 backlog grouping internally tracked as "v1.1".) The GitHub repo
`ArtRichards/docs-cli` is public; source tag `v1.3.0` +
GitHub release exist. See
[m9-pypi-publish.md](archive/2026-05-25/m9-pypi-publish.md)'s
milestone-completion summary for the published version, wheel
+ sdist sha256, publish timestamp, and the deviations from the
runbook recorded for v1.4+ releases. The release-runbook stays
the operative reference for future publishes.

**Next action:** **M29 — PyPI publish 2.0.0**, which the whole v2.0 train
(M25–M28a) is now waiting on. M28a is implementation-complete across all ten
TDD phases and stays `Lifecycle: active` until that closeout. **Phase 7 — Update Tool/Wrapper Layer completed
2026-08-16** on `m28a/phases-5-10`, taking the suite fully **GREEN at 1502
passed / 0 failed**: the bundled `SKILL.md` and `references/use-cases.md`
carry the witness, the refusal and `archive-date-drift`; the argparse flag
delta is **confirmed empty** (mechanically diffed against `7f7853b`) while two
`description` strings gained one clause each under the surface-parity gate;
the `UNRELEASED` CHANGELOG gained both `Added` entries, the BREAKING `Changed`
entry and an upgrade note stating the present-only contract plainly; and
`feedback-log.md` **issue #1 is CLOSED**, its last open item answered. Phase 1
had already landed the author-facing specs, so this phase verified them item
by item — and found two real gaps, both corrected: `convention.md`'s built-in
always-allowed label list omitted `Archived`, and its `docs mv` refusal
paragraph still said three permitted neighbours where amendment 6 says four.
**Phase 6 — Implement Offline/Core Path
completed 2026-08-16** on `m28a/phases-5-10`: the three touch points Phase-1
amendment 3 named, and nowhere else — one `set_metadata_field` in
`_archive_one` writing the same `date_str` that names the dated directory to
**every** member (the reason stays primary-only, untouched); one
`findings.extend` in `check_doc` between `status-drift` and `duplicate-field`;
and Leg 2's two-line refusal in `_cmd_mv` immediately after `old_rel` /
`new_rel` are derived and before the `--dry-run` branch, so it refuses in every
mode with zero bytes written and no `--json` record. 26 ids flipped to
**2 failed / 1500 passed**; `docs check --root docs` still exits 0 with the
rule live over the 46-document archive. **Phase 5 — Update Base Interfaces completed
2026-08-16** on `m28a/phases-5-10`: `Archived` joined
`_BUILTIN_METADATA_FIELDS` (and stayed out of `parse()`'s `known` set and
migrate's supersession set); `parse_date` gained its keyword-only
`label: str = "Updated"` so one parser spells both date-error messages with no
existing call site's bytes moving; and all three pure helpers landed —
`archive_dir_date`, the shared config-aware dated-directory reader,
`cross_dated_archive_move` (Leg 2's predicate, which delegates to it so the two
legs can never disagree), and `archive_date_findings`. All three are wired
nowhere, so the 26 CLI-level ids stay honestly RED at the seam: 43 ids flipped
and the suite stands at **28 failed / 1474 passed**. M28a's milestone setup completed 2026-08-15 on
`m28a/milestone-setup`: the registered draft stub is expanded to a full
ten-phase task plan with **nine binding decisions**, nine pieces of measured
evidence (E1–E9), an *Evidence → regression coverage* table, and two setup
corrections recorded as A1 and A2; the implementation log is open; **all seven
setup questions are RESOLVED** — Q4 by operator decision (adopt both legs, so
`docs mv`'s refusal is binding scope as D5), Q1 auto-resolved to `Archived:`,
and Q2/Q3/Q5/Q6/Q7 conductor-resolved. **Phase 1 — Define Contract completed
2026-08-15** on `m28a/phases-1-4`: the machine-facing contract is frozen as
items (A)–(H) of *Decisions (Phase 1 — BINDING)*, with **six amendments** to
setup-frozen material — D8's residual widened to name a second, tool-driven
case; D5's refusal moved to the plan-before-move window one step earlier so it
reaches `--dry-run`; and four factual corrections, the last of them sweeping
"three permitted neighbours" to four — and **nine Step-1 resolutions** (OQ-1 … OQ-9), of which **OQ-7 is an operator decision** declining
to widen the `docs mv` predicate. The author-facing halves landed in `cli.md`
and `convention.md` with both bundled mirrors re-synced; no product code
changed and the suite was unchanged at **1341 passed**. **Phases 2–4 completed 2026-08-16**:
**149** authored ids across twelve test files and **six** `archivedate-*`
fixture trees; 1502 collected, **71 RED / 90 GREEN** of the 161 new ids in
exactly two exception classes (36 `AttributeError` across the three pure-seam
groups, 35 `AssertionError`), **0** collection errors / xfails / tracebacks,
**0** ids removed and **0** pre-existing ids failing against `7f7853b`, every
pre-M28a fixture tree byte-identical, and `cli.py` untouched. The
**same-instance audit** found and fixed eight issues — the largest being that
both message catalogues under-constrained their raw-string requirement, and
that `cli.md`'s promise that five verbs never write the witness was locked for
only three — adding five locks. An independent **fresh-eyes review** then
returned **no blockers** and one real gap: `cross_dated_archive_move` had no
tests of its own and every Leg-2 CLI test ran on a default-config tree, so a
config-blind predicate would have passed the whole suite while leaving M28a's
hole open on an `attic` tree and *falsely* refusing on a `history` one. Closed
with thirteen more ids. Neither pass escalated anything to the operator. **M28 is complete and merged to `main`**
(2026-08-15, merge `b1ec74b`) across all ten TDD phases — Step 1 on
`m28/phases-1-4`, Step 2 on `m28/phases-5-10`, Step 3 on `m28/simplify` — and
stays `Lifecycle: active` until M29 publishes the train. The merged suite is
**1341 GREEN** with the gate clean tree-wide. **Phase 10** ran `/simplify` over the new planner and the
two verbs (net **−18 lines**, four collapses, suite still 1333 GREEN) and
closed the documentation: `architecture.md` gained a *Move-safe body-link
rewrites (M28)* subsection, had its archive pipeline re-drawn through
`apply_move_plan`, and gained a `mv` pipeline it never had;
`test-strategy.md` gained the `movelink-*` fixture family and two
critical-path rows; `plan.md` and this file record the completion.
**Phase 9** dogfooded nine flows on throwaway copies, never touching the live
tree: E1's rename went from **42** `broken-body-link` findings to **0** with a
77-line diff in which every changed line names the moved document; E2's single
archive from **13** to **0**, including its four archived referrers; E3's real
closeout from **6** to **0**; plan A — the E7 census invocation — **completed**
with its leg-2 report naming exactly **16** still-active inbound references
(8 `Related:` + 8 body links, 7 referrers), reproducing the census; plans B and
C **refused** at exit 2 with zero bytes and empty stdout, while plan B's
preview reported the identical verdict at exit 0 with a populated record; the
refusal survived `--quiet`; a there-and-back move left the tree
**byte-identical**, `INDEX.md` included; and both verbs' preview and apply
records differ in exactly the three state bits. The move costs **+80 ms** and a
solo archive **+113 ms** over the 73-document tree.
**Phase 8** took the whole gate GREEN — **1333 collected, 1333 passed**, zero
collection errors, zero xfail/xpass/error, lint / format / types clean,
`docs check --root docs` exit 0, both bundled mirrors `cmp`-identical, the
frozen INDEX snapshot identical and `pyproject.toml` untouched — and proved
mechanically against `58955ef` that **0** test ids were removed, 246 added,
and all 1087 pre-existing ids are present and GREEN. Exactly **11** test lines
were deleted, all inside the one re-pointed lock, with both test edits named
and justified as strengthenings rather than reported as "0 lines changed". **Phase 7** reconciled every parallel
surface — both argparse descriptions, the bundled `SKILL.md` and
`references/use-cases.md` (whose "prose links are not rewritten — a deliberate
scope cut" line was false as of Phase 6), the `UNRELEASED` CHANGELOG with its
three-part upgrade note naming the two re-spelled `docs mv` stderr lines, and
a dated resolution bullet on `feedback-log.md`'s issue #1 entry answering
findings 1 and 4. Two test expected-values changed, both **strengthenings**:
`archive --json`'s closed top-level key set went from eight keys to ten, and
the primary-only record lock was re-pointed at a tree whose primary has no
live `child-of` children — the tree it left now carries its own leg-1 refusal
lock, because that scenario is exactly the harm leg 1 exists to prevent.
**Phase 5** landed `MOVE_STRAND_KINDS`, the four frozen records and the seven
pure functions of item (L) as three pure insertions into `cli.py`, with
`_cmd_mv` and `_cmd_archive` byte-identical, so the CLI locks stayed honestly
RED at the seam; `tests/test_move_links.py` went 194/194 and the
`AttributeError` class went to zero. **Phase 6** inverted `_cmd_mv` to
plan-then-move with the R9 partial-state admission, added `docs archive`'s
steps 5b / 8b / 8c / 8d, threaded each moving member's planned text into
`_archive_one` so the contract stays at one write per document, lifted
`preview only` into the verb so a preview ends on it, and **deleted**
`_rewrite_referring_edges` — superseded by `apply_move_plan`, whose M18
archived-doc gate is unnecessary by construction. The suite is **5 failed,
1327 passed**, and every remaining RED is a Phase-7 item: the two
`_JSON_TOP_LEVEL_KEYS` ids, one M26-era fixture whose primary-only archive now
correctly refuses on leg 1, and the two bundled-skill locks. **Step 1
(Phases 1–4) is complete on `m28/phases-1-4`** (2026-08-15), on top of the
milestone setup completed 2026-08-15 on `m28/milestone-setup` with all seven
setup questions resolved. **Phase 1** froze the whole machine-facing contract
in the [M28 plan](m28-move-safe-body-link-rewrites.md)'s *Decisions (Phase 1 —
BINDING)* — items (A)–(M): the move map, the three-step formula with its
BINDING step order and its semantic no-op test, the destination-token renderer
and both grammar-derived encode sets with `%` encoded first, the
never-creates-an-escape invariant with its one-line proof, the per-document
write pipeline, the validate-all-first pre-flight, the archived-referrer rule
as a single sentence, both strand legs, both verbs' check orders, the frozen
message catalogue, both `--json` schemas and the Phase-5 signatures — with the
author-facing halves in `cli.md` › *Move-safe body-link rewrites (M28 —
D1–D7)* and the rewritten `docs mv` section, and in `convention.md`, where
M18's exception is **widened** along its own axis and M27 — D6's "the last one
this convention grants" sentence is **reconciled** (M28 leaves the count at
three). Three setup-frozen items were amended in place: M26's compatibility
matrix now says **a preview adopts failures of plan *construction* and
reports-but-does-not-adopt *consequence* verdicts**, so a malformed tree makes
`archive --cascade-dry-run` exit 1 and `mv --dry-run` exit 2 while a leg-1
verdict is reported at exit 0; plan B's `strands` array is observed in its
**preview**, because a refusal emits no record; and `movelink-closeout`
**reproduces** the `archive-pair` shape rather than the committed trees gaining
body links. Eleven Step-1 resolutions (R1–R11) are recorded with their
reasoning. Zero `cli.py` edits, 1087 passed unchanged, `docs check --root docs`
exit 0. **Phase 2** wrote the RED suite — a 153-item pure-planner module plus
12 `mv`, 14 `archive`, 1 `check` and 2 bundled-skill locks — with zero deleted
test lines and zero collection errors (1269 collected, 181 failed, 1088 passed at
the time). **Phase 3** authored the seven `movelink-*` fixture trees, each
`docs check`-clean as committed and each proven by a read-only prototype census
to yield exactly its intended plan, line numbers included; no existing fixture
was edited, and the two directory-derived sweeps grew 29 → 36 and 33 → 40.
**Phase 4** captured the classified RED baseline — **1332 collected, 229
failed, 1103 passed** after the Step-1 same-instance audit and the fresh-eyes
fold-in, zero collection errors, zero xfail/xpass, zero warnings,
exactly two exception classes (193 `AttributeError` through the `_m28()`
indirection, 36 `AssertionError`), every RED in a named family with a
Phase-5/6/7 landing point, every GREEN-at-baseline lock classified
degenerate / genuine / **transitional**, and all **1087** pre-existing ids
mechanically proven present, 0 removed and 0 test lines deleted — with exactly
**one** pre-existing id deliberately RED, `test_mv_help`, strengthened by
operator decision so Phase 7's `docs mv --json` argparse half is a lock rather
than a promise. The fresh-eyes review returned **no blockers**; its five
should-fix items and three nits are folded in, the largest being **amendment
4**, which narrows Q4's "already broken" clause to "already escaping" because
its literal wording is unimplementable in a planner that never stats, and the
operator **closed the colon encode residual** here rather than deferring it —
item (C) now carries the renderer post-condition
`classify_destination(new_raw) == "local"`. No product code was touched across
Phases 1–4, by design. The phase records live in the
[M28 log](m28-move-safe-body-link-rewrites-impl.md).

M27's milestone setup completed 2026-08-14 on
`m27/milestone-setup` with **all seven setup questions resolved**;
**Step 1 (Phases 1–4) is complete on `m27/phases-1-4`**, and **Step 2
(Phases 5–10) is complete on `m27/phases-5-10`** — all ten phases
(2026-08-14). Phase 1 froze the
contract: the supported Markdown grammar subset and its exactness rules, the length-preserving code-masking
contract and its ordering, destination classification and document-relative
resolution, **the containment test** (join → lexical canonicalisation →
under-root membership, with the `..`-escape-then-return and symlink cases
decided) and **its precedence over the existence test** so
`broken-body-link` and `outside-root-body-link` never double-report, both
findings' exact message templates with the JSON record's key set left closed,
and the `BodyLink` destination-span contract M28 consumes are frozen in
`cli.md` › *Markdown body-link validation* (including the explicitly stated
out-of-root boundary), `convention.md` › *Body links* (the inside-the-root
invariant, fence-your-code-samples, and the third archived-document
exception), and the
[M27 plan](m27-markdown-body-link-validation.md)'s *Decisions (Phase 1 —
BINDING)*. Zero `cli.py` edits, 895 passed unchanged, `docs check --root docs`
exit 0. Phase 2 wrote the RED suite against those frozen strings — a new
105-item pure-scanner module plus the rule-level, subprocess, touch and
bundled-skill locks, **+163 test ids with zero removed and zero collection
errors** (1058 collected, 129 failed, 929 passed). Phase 3 authored the six
`bodylink-*` fixture trees — 17 files, each tree yielding exactly its intended
finding set, **no** pre-existing fixture edited, collection +6 for the
parametrizations they add (1064 collected, 122 failed, 942 passed as the seven
predicted degenerate locks flipped GREEN). Phase 4 captured the classified RED
baseline: **1079 collected, 137 failed, 942 passed** (restated after the
Step-1 same-instance audit and the fresh-eyes review fold-in), zero collection
errors, zero tracebacks, zero xfails, exactly two exception classes (119
`AttributeError` through the `_m27()` indirection, 18 `AssertionError`), and
**all 895** pre-existing ids mechanically proven still present and still
passing — `comm -23` and
`comm -12 failed old` both **zero**, because M27 removes and modifies no
pre-existing test. The audit found and fixed six issues, none needing an
operator decision: a stale `plan.md`, an E5 lock narrower than the coverage
the milestone claims, an ordering lock that pinned only half of the
findings' placement, a specified-but-unlocked nested-vs-root `INDEX.md` split,
an under-constrained mask assertion, and `BodyLink`'s immutability being
frozen in the signature but untested. An independent **fresh-eyes review**
then found **no blockers** and reproduced the whole baseline, returning nine
should-fix items and four nits — all conductor-resolved and folded in. Their
unifying theme was that a wrong-but-plausible Phase-5 implementation could
still pass the suite: the BINDING percent/backslash/`#` decode order had no
test at all (the natural `unquote()`-then-`split()` implementation violates
it and went GREEN), the ordering lock never mixed the two rules, the
angle-destination newline bound and the unclosed-fence case were unpinned,
and the never-stat spy's containment test was a prefix comparison that would
have admitted the very probe it forbids. The specs also gained three settled
reference-definition points, an explicit whitespace-both-sides rule, the
unclosed-fence rule with its deliberate divergence from the single-line
inline-span bound, and a corrected worked instance; and a Phase-6 trap is now
recorded — the D6 repair bumps 30 `Updated:` lines, so
`tests/fixtures/expected/docs-INDEX.md` must be regenerated inside Phase 6's
own commit. **Phase 5 (2026-08-14)** landed the whole pure scanner in one new
banner section of `src/docs_cli/cli.py` — `BodyLink`, the length-preserving
`_mask_code`, `scan_body_links`, `classify_destination`, the
resolution/containment helpers and `body_link_findings` — while wiring **no**
rule, so the 18 rule/CLI/skill tests stay honestly RED at the `check_doc`
seam: **18 failed, 1061 passed**, all 119 pure-scanner tests GREEN, every
remaining failure an `AssertionError` and none an `AttributeError`, and no
test file edited. The real scanner reproduces every published census number
exactly — 393 recognised spans, 139 broken and 1 escape across 30 documents in
`docs/`, and 0 broken / 0 escapes across all 33 pre-M27 fixture trees and the
bundled skill — which is the point of measuring twice. Seven grammar points
the frozen contract left silent (an empty inline destination is a recognised
link with a zero-width span; newlines are ordinary whitespace either side of
an inline destination; the blank-line bound covers the whole candidate; the
closing-fence and verbatim-fence-line rules; a reference definition's label
opens and closes on one line and its destination ends at an unescaped `)` at
depth 0; a `(…)` title does not nest; and `Path.exists()` is kept so a
dangling in-root symlink is `broken-body-link`) were settled in `cli.md` and
its byte-identical mirror rather than only in the log, because every one of
them changes what the scanner hands M28. **Phase 6 (2026-08-14)**
wired both rules into `check_doc` in three lines — after the `broken-ref`
group and before `stale`, with `check_tree`, `exit_code_for`,
`finding_to_json`, `_print_check_findings`, `_run_touch_check`,
`_iter_doc_texts` and the argparse all untouched — and, in the **same
commit**, performed the D6 live-tree repair: **140 occurrences across 30
documents**, split **132** root rebases / **5** move-map lookups / **2**
playbook URLs / **1** escape URL, driven by the Phase-5 scanner itself and
spliced by offset right-to-left, which is literally the M28 operation and the
first live proof the span contract works. All 30 got an `Updated:` bump and
the 29 archived ones a single uniform dated `Revision:` bullet;
`convention.md`'s promised repair date is now the real one. Six independent
checks prove no other byte moved — 30/30 round-trip reconstructions
byte-identical, 166 changed lines with every non-`equal` opcode inside a
recorded destination span, `+3`/`+0` net line arithmetic, every metadata
invariant held, a re-census at **0 broken / 0 escapes with the
recognised-span count still 393**, and both gates green. The `docs/INDEX.md`
churn (29 archived entries relocated to the top of the archived group plus
`charter.md`'s date, 30 changed lines) is the mechanical consequence of the
operator-confirmed `Updated:` bump and was regenerated with its frozen
snapshot inside the same commit. Suite: **2 failed, 1077 passed**, the only
REDs left being Phase 7's two surface locks. **Phase 7 (2026-08-14)**
reconciled every parallel surface — `docs check`'s argparse description, the
bundled `SKILL.md` check row and `references/use-cases.md` (the *Validate in
CI* row plus a new M27 upgrade section), and `CHANGELOG.md` under
`UNRELEASED` with one `Added` entry per rule, a BREAKING `Changed` entry, and
the adopter recipe for **both** repairs. No spec edit was needed, so both
mirrors stayed byte-identical and the INDEX snapshot needed no regeneration;
no version bump. The suite is now **fully GREEN at 1079 passed**, one phase
early. **Phase 8 (2026-08-14)** ran the formal gate: **1079 collected, 1079
passed, 0 failed**, zero xfail/xpass, zero tracebacks, every quality gate
clean, and the `comm` proof against **both** anchors — **0** ids removed
since the pre-M27 `d61da1d` and since the Step-1 head `ddf0a45`, **0 added by
Step 2**, and 895 + 184 = 1079. `git diff ddf0a45 -- tests/*.py` is empty:
no test was relaxed, weakened, deleted or rewritten to reach GREEN, and none
needed to be. **Phase 9 (2026-08-14)** replayed the pre-repair damage on
throwaway copies (140 findings, 139 + 1, exit 2, 30 documents) and walked the
**documented** recipe from `docs check --json` alone — never the scanner API
— reaching exit 0 with the same 132/5/3 split and **0 destination-token
mismatches** against the repaired tree. Hermeticity was proven end to end on
the pre-repair copy, the only one where the escaping link still exists:
identical stdout and exit code from a location with a resolving sibling `src/`
and from a bare one, with **0 probes outside the root** under a `Path.exists`
/ `Path.is_file` spy. All 39 fixture trees and the bundled skill sweep clean
bar M27's three deliberately damaged ones. Runtime: 183 ms over the 2.5 MB
live tree and 61 ms for the 303 KB adversarial set — **33× under the 2.0 s
lock**. The real tree was never written to. **Phase 10 (2026-08-14)** ran
the `/simplify` pass — four changes applied, six candidates considered and
rejected with the reason recorded — closed `architecture.md` › `check` and
`test-strategy.md` › *What we don't test* (which still claimed the body was
opaque), extended README's one-line `docs check` summary, and folded in the
Phase-9 quality item: the live-tree scan went from 183 ms to **81 ms**, with
`docs check` at **0.16 s** end to end. **M27 is implementation-complete** —
all ten phases, every deliverable met, and the `BodyLink` span contract
handed to M28. The **Step-2 same-instance audit** then found **twelve** issues and fixed all twelve — **three of them real behavioural defects in the scanner**, every one invisible to the finding set and to the suite, reachable only by reading the frozen contract as a specification. The critical one is a **hermeticity hole**: a percent- or backslash-encoded leading slash (`%2Fetc/passwd`) classifies `local` because classification runs on the token as written, decodes to `/etc/passwd`, wins the `posixpath.join`, and — because Phase-1 point 9 dropped the containment predicate's leading-`/` leg — read as *contained*, so `docs check` **stat'd a path outside its own root**, the single thing D4b exists to forbid. The leg is restored; point 9's stated intent survives (a literally-written `/path` is still silenced by classification) while its unsound mechanism does not, and **point 9 is amended in place — a BINDING Phase-1 decision, flagged for the operator**. The other two defects: a link nested inside an image label was silently dropped, which the Phase-1 linearity note had foreseen and which would have left M28 unable to rewrite that destination; rule 5's *at least one whitespace character* before a title was not enforced; and two docstrings asserted things that were false. All three scanner fixes are **behaviour-neutral on every real input** — the live-tree census (393/0/0), the pre-repair replay (139 + 1 across 30 documents) and the 39-tree fixture sweep are all unchanged — and the three reachable defects are now **locked**, taking the suite to **1082 passed / 0 failed**. The remaining findings were spec and documentation corrections: an `architecture.md` line-count and module-annotation drift, a Success criterion that called all 139 archived repairs "rebases" when only 132 are, a `convention.md` promise of *29 named archived documents* that no surface actually named, a `Progress:` line and an "in flight" claim that contradicted "all ten phases complete", a CHANGELOG example mixing a real filename with a synthetic destination, a self-contradictory fence-line clause, and runtime figures that had drifted. Three items are surfaced for the operator rather than auto-decided. An independent **fresh-eyes review** then reproduced all of that adversarially — a 40,000-case destination fuzz under a `Path.exists` spy (21,747 stats, 0 outside the root), an `strace` of a real `docs check`, its own round-trip of the 140-occurrence repair (30/30 byte-identical), a 20,000-input mask/span fuzz, and 40 grammar shapes walked clause by clause — and returned **one blocker plus eight further items**, every one folded in. The blocker was the mirror image of the audit's own A2: a link whose **label** is an image (`[![diagram](diagram.png)](full-size.md)`, the ordinary badge / thumbnail idiom) ended its label at the *image's* `]`, so `docs check` **reported the image** as `broken-body-link` — against the success criterion that images produce no finding, and against operator-binding Q2's own words — and never emitted the real destination, so M28 would never rewrite it. Rule 2 is amended (a nested image consumes one `]`) and implemented as a level table, because the accepted `]` depends on where the label started and a rescan is quadratic. The review also closed **two residual quadratics** — many unterminated `<` or `(…)` titles inside one paragraph, measured at 3.27 s and 5.96 s, now 6.7 ms and 10.8 ms — corrected three places that claimed a linearity which did not hold, had the dangling-symlink lock written rather than deferred, qualified a spec sentence that could not be true alongside S9, stopped a percent-decoded control character splitting a finding across two lines, and fixed a **pre-existing** `OSError` crash on an over-long path segment at **both** the body-link and `broken-ref` probes. Final: **1087 passed / 0 failed**, eight test ids added across the audit and the review, **zero removed** against both anchors, and no assertion loosened.
The Step-3 `/simplify` pass is **done** (2026-08-14, `m27/simplify`) and made
**two** code changes, both in code the Phase-10 pass never saw — the
fresh-eyes review introduced it afterwards. `_blank_line_starts`' five lines
of line-end index arithmetic collapse to one
`zip(line_starts, text.split("\n"), strict=True)` comprehension, and
`_label_closers`' image scan becomes a two-character `find("![")` with two
conditions removed that can never fire: the bounds test, vacuous once the
needle is two characters, and the `[`'s escape test, vacuous because the only
character that could escape it *is* the `!`. Both were proven
behaviour-identical as differential oracles over **30,609 inputs** — every
`.md` in the repository plus 30,000 adversarial randoms — **before** being
applied. Every load-bearing piece was left alone and re-measured rather than
argued: the adversarial 485 KB / six-shape lock is 81 ms before and after, the
2.5 MB live tree 83 ms, and both formerly-quadratic shapes keep their ~2× per
doubling. One stale figure was corrected — the completion summary quoted
Phase 9/10's **three**-shape 303 KB lock (`~44 ms`, `~45×`) in the present
tense, where the head's six-shape 485 KB lock is ~81 ms and ~25×. 1087 GREEN
and the gate clean before and after, with `tests/` byte-identical, the live
tree still 393 spans / 0 broken / 0 escapes, and both bundled-skill mirrors
byte-identical; the nine rejected candidates and their reasons are recorded in
the log. Each phase is recorded in the
[M27 log](m27-markdown-body-link-validation-impl.md). M26 is
implementation-complete on `m26/phases-5-10` (2026-08-13) across all ten TDD
phases. Step 1 froze the contract — the compatibility matrix, the message
catalog, the exit-code split, the `--json` schema, and the Phase-5 signatures
in the [M26 plan](m26-safe-archive-selection.md)'s *Decisions (Phase 1 —
BINDING)* section and in `cli.md` / `convention.md` — wrote the RED suite over
four new `archive-*` fixture trees, and captured the classified baseline
(**884 collected, 104 failed, 780 passed**), passing a same-instance audit and
an independent fresh-eyes review whose blocker was an unsatisfiable
byte-identity assertion that collided with M18. Step 2 landed the
implementation: Phase 5 the `ArchiveMove` / `ArchivePlan` models, the two
pure helpers and the `--json` serializer; Phase 6 candidate discovery,
planning, the validate-all-first pre-flight, ordered execution and the
residual partial-state admission; Phase 7 the nine-step check order in
`_cmd_archive`, the retirement of bare `--cascade` and `--interactive`
(both still registered, refusing before any filesystem access), the deletion
of the three 1.x cascade helpers — and with them the verb's last stdin read —
and every parallel surface: `--help`, `cli.md`, the bundled skill, and the
`UNRELEASED` CHANGELOG; Phase 8 the GREEN gate (**888 passed**; 889 after the Step-2 audit's failure-path lock and 895 after the fresh-eyes review fold-in) with **774 of
777** pre-existing ids mechanically proven present and passing, 3 deliberately
removed and 114 new at that gate (121 after the audit and review fold-ins);
Phase 9 the dogfood, where the unfiltered preview of the
M25 pair reproduced **E1** exactly — all six spine documents named and none
authorized — and four refusals each changed zero bytes on a fresh copy;
Phase 10 the simplify-and-close pass. Two frozen signatures were amended
under conductor decision and are recorded in the milestone doc
(`CoordinatedWriteError.exit_code`, `_print_archive_lines(cascade=…)`), and
one defective Step-1 test helper — a `mkdir` missing `parents=True` that no
implementation could satisfy — was fixed in its own labelled commit with no
assertion changed. The same-instance audit then caught an unreadable plan
member producing a traceback, and the independent fresh-eyes review caught the
step's one **blocker**: a primary that resolves outside the docs root — through
a symlink, or a `--root` naming a different tree — was archived **into** the
tree, at exit 0 in one shape with `docs check` clean afterwards. It now refuses
at exit 1 before any write, in the cross-verb wording `touch` / `stamp` /
`project set` / `relate` already use. **The package version deliberately stays
1.8.0.** The Step-3 `/simplify` pass is **done** (2026-08-13, `m26/simplify`)
and made **no code changes**: Step 2's Phase-10 pass had already taken the one
real win (the `_is_archived_rel` dedup), and every remaining candidate —
the pre-flight's five per-check loops, the four read-failure handlers, the
`CoordinatedWriteError`-before-`OSError` clause order, the two-check
`os.access` pre-flight, and `_archive_one`'s verbatim body — was re-examined
against the post-review code and found load-bearing. 895 GREEN and the gate
clean before and after, with `src/` and `tests/` byte-identical; the rejected
candidates and their reasons are recorded in the log.
Each phase is recorded in the
[M26 log](m26-safe-archive-selection-impl.md), which carries the milestone
completion summary. M25 is
complete and **merged to `main`** (2026-08-12, merge `822e086`) across all ten
TDD phases (**777 GREEN**, gate clean, dogfood done, fresh-eyes review folded
in) and stays `Lifecycle: active` until
M29 publishes the train. The Step-3 `/simplify` pass is **done**
(2026-08-12, `m25/simplify`): three duplicated bare-label scans collapsed
onto one `_bare_label_run`, `_plan_relate_edit`'s doubled `RelateEdit`
construction merged, `_print_relate_lines`' per-iteration word choices
hoisted, and `_duplicate_labels`' split cursor advance unified — **-17
lines**, 777 GREEN before and after, no shipped string or contract moved.
The package version deliberately remains **1.8.0**;
M25's CHANGELOG entries sit under `## UNRELEASED` for M29 to name and date.
M27–M29 stay draft until their turn.
The [release-runbook.md](release-runbook.md) remains the operative M29
publication path. The PyPI token re-scope and workflow-skill drift-lint items
remain non-blocking follow-ons below.

**Open follow-ons (rolled forward):**
- **Token re-scope** to project-`docs-cli` — async operator UI work, not a
  release blocker; rolls forward from M9 → M11 → M13 → M17 → M20.
- **Workflow-skill / bundled-skill drift lint (NEW, v1.7+ candidate).** The M20
  host-skill sweep (the NEW publish-closeout step) caught a stale
  `docs new --body-from` "first 20 lines" reference in the
  `project-foundation` workflow skill — the pre-M19-D3 heuristic, fixed at the
  M20 closeout. The drift was only catchable at publish time. Candidate: an
  in-repo lint that diffs the workflow skills' docs-cli prescriptions against
  the bundled `references/` surface so this class of drift surfaces before a
  publish, not at it. Logged for v1.7+; not a release blocker. The lint is a
  repo-side CI artifact and stays a separate follow-on.
- **Runtime skill-refresh nudge now lives in M23 (NEW, 2026-06-29).** The
  *runtime* skill-refresh idea — when the user updates the CLI, also nudge them
  to refresh the installed skill — was originally M21's D5 (an offline
  skill-drift *notice* that inspected the host's installed skill). That premise
  (content-inspecting the user's skill; assuming Claude Code) was rejected this
  session; **D5 is CUT from M21**. The honest version — make `install-skill`
  agent-aware via `--dest`, **record** the resolved dest, then extend M21's
  notice channel with a skill-refresh hint pointed at the *recorded* dest — is
  the follow-on **M23** ([m23-agent-aware-install-skill.md](archive/2026-07-03/m23-agent-aware-install-skill.md)).
  Not a loose follow-on any more; it is a scoped (draft) milestone.

**Shipped (cleared follow-ons):**
- **Stale `docs new --body-from` help string → FIXED in M19 (D3), shipped to
  PyPI as `docs-cli==1.6.5` via M20 on 2026-06-12.** The argparse `--help` text
  shipped in 1.6.0 still described the pre-M15-C4 "first 20 lines" heuristic;
  M19 D3 replaced it with the real-detector wording (leading `---` fence or ≥2
  adjacent `{Lifecycle, Role, Updated}` lines), pinned by
  `test_new_body_from_help_no_first_20_lines` and re-verified against the
  PyPI-served 1.6.5 wheel at the M20 Phase-4 smoke. Closed.
- **Single-step "update metadata + validate" loop + configurable stale window →
  IMPLEMENTED in M19 (v1.6.5), shipped to PyPI via M20 on 2026-06-12.** (a) The
  three-command post-edit workflow collapses to one step via `docs touch
  --check [--stale N]` (D1). (b) The fixed `--stale 14` window becomes a
  `.docs.toml [check] stale_days = N` per-tree default (D2 — arms bare `docs
  check`, CLI `--stale` overrides, provenance-named messages); does not affect
  `docs list --stale` (Q6). Both verified against the PyPI-served 1.6.5 wheel at
  the M20 Phase-4 smoke. Closed.

- **M14 — Robustness + autonomous archive (v1.6.0)** — **Complete**;
  shipped to PyPI as `docs-cli==1.6.0` via M17 on 2026-06-03. `docs mv`
  atomicity, `docs new` strict-root refusal, the four-verb
  `touch`/`archive`/`mv`/`project rename` exclude-predicate fix,
  slug/`OSError`/`atomic_write`-fsync guards, non-interactive
  `archive --cascade`, bundled-ref + packaging fixes. Pair archived to
  `archive/2026-06-03/`.
- **M15 — Agent-native doc authoring (v1.6.0)** — **Complete**; shipped
  to PyPI as `docs-cli==1.6.0` via M17 on 2026-06-03. `docs project set`,
  single-file `docs stamp` (write-then-stamp), the `--body-from`
  real-frontmatter detector, and the skill/cli docs. Carved out of M14 on
  2026-06-02 (it outgrew M12 scale); **depended on M14**. Pair archived to
  `archive/2026-06-03/`.
- **M17 — PyPI publish 1.6.0** — **Complete (2026-06-03)**: the
  operator-driven publish that shipped M14 + M15 together (batched, as M9
  shipped M6+M7+M8). Ran the [release-runbook.md](release-runbook.md)
  end-to-end as a fully-autonomous pass; chain-of-custody bit-perfect;
  `v1.6.0` annotated tag at `95f23a6` + GitHub release. Milestone doc
  archived to `archive/2026-06-03/`; the
  [m17-pypi-publish-impl.md](m17-pypi-publish-impl.md) impl log stays
  `Lifecycle: active`.

The broader agent-native surface (global `--json`,
`docs context`/`capabilities`, hooks, MCP) is deferred — see
the M14 Decisions.

[release-runbook.md](release-runbook.md) remains the operative
publish reference, with M13's cumulative lessons folded in
(TestPyPI rehearsal prints `0.0.0+local` under the rename
detour because the M12 `importlib.metadata` SoT can't resolve
the renamed distribution — verify the version string against
the canonical-name local + PyPI wheels; and `CHANGELOG.md` is
not shipped inside the sdist).

### M6 — preparation complete (2026-05-24)

M6 was merged to `main` 2026-05-24 as commit `ff7f9d5` and
closed at Phase 10 as **preparation only** — packaging machinery
(build backend, package shape, `install-skill` verb, runbook
scaffold, GitHub repo) delivered; no PyPI upload was ever in
M6's scope after the 2026-05-24 reframe. The wheel + sdist in
local `dist/` from 2026-05-23 are not uploaded; M9 will rebuild
fresh from the post-M8 tree at publish time. See
[m6-pypi-distribution.md](archive/2026-05-24/m6-pypi-distribution.md)'s top
"Scope reframe" callout and the
[release-runbook.md](release-runbook.md) for the operative
checklist.

### M9 — PyPI publish 1.3.0 (Complete 2026-05-25)

[m9-pypi-publish.md](archive/2026-05-25/m9-pypi-publish.md) walked top-to-bottom
in one contiguous session 2026-05-25. Quality gate green
(pytest 369), artefacts rebuilt fresh from the post-M8 tree,
TestPyPI rehearsal ran under a disambiguated dist name
`docs-cli-rehearsal==1.3.0` (the bare `docs-cli` was parked
on TestPyPI by an unrelated user — real PyPI was clean), real
PyPI upload + smoke install confirmed bit-perfect
chain-of-custody, repo flipped public, `v1.3.0` tag pushed +
GitHub release created, doc closeouts in lockstep. Token
re-scope deferred as out-of-band operator UI work. Full
record (and deviations recorded for v1.4+) in M9's
milestone-completion summary.

### M7 + M8 — stubs drafted from the 2026-05-24 trial

The multi-tree trial against 25 real-world foreign trees (501 .md
files) surfaced 11 categorical findings. They cluster into two
milestones:

- **M7 — Migration plan accuracy** (Complete 2026-05-25):
  renamed the controlled-vocab field `Status:` → `Lifecycle:`
  (breaking, no backward compat), broadened role inference
  (suffix matching, H1 + section signals, sibling defaulting),
  normalised project names to lowercase-kebab, normalised
  `archived/` subdirs into `archive/YYYY-MM-DD/`, expanded the
  role vocab with 7 core additions (`implementation`, `sketch`,
  `outline`, `memo`, `brief`, `template`, `example`). One new
  CLI flag: `docs migrate --config-project NAME` (plus
  `--lifecycle` rename on `docs list`). Trial-2 dogfood: 88%
  high+medium against the sanitised real-tree fixtures. Plan
  at [m7-migration-accuracy.md](archive/2026-05-25/m7-migration-accuracy.md).
- **M8 — Adoption workflow** (after M7): `--exclude` tree-wide
  (in `migrate` + `index` + `check` + `list` via `.docs.toml`'s
  new `[exclude]` section), triage flags
  (`--summary`, `--only ambiguous`), `docs new --body-from <-|path>`
  (closes Read-before-Write friction), and a substantial rewrite
  of the bundled skill's references for the adoption flow
  (SKILL.md stays slim — one pointer line). Stub at
  [m8-adoption-workflow.md](archive/2026-05-25/m8-adoption-workflow.md). Load-bearing
  ship gate: **fresh-subagent dogfooding** of the adoption loop
  end-to-end against trees the M8 author hasn't tuned for.

### M6 milestone-setup history (kept for context)

**M6 — PyPI distribution as `docs-cli` is in flight (milestone-setup
phase complete, 2026-05-23).** The task plan
[m6-pypi-distribution.md](archive/2026-05-24/m6-pypi-distribution.md) is promoted from
`draft` to `active`; the log
[m6-pypi-distribution-log.md](archive/2026-05-24/m6-pypi-distribution-log.md) is created.
M6 is the first v1.1 milestone: it publishes the CLI as `docs-cli` on
PyPI, relocates `bin/docs` to an importable package at
`src/docs_cli/cli.py`, ships the Claude Code skill inside the wheel as
package data, and adds one new verb — `docs install-skill` — that
materialises the bundled skill onto a host. **All five milestone-setup
OPEN QUESTIONS are resolved 2026-05-23** (OQ1 command name stays
`docs`; OQ2 conftest aliases `docs_cli.cli` as `docs`; OQ3 repo
identity moves at Phase 1 with a new GitHub repo created since the
local repo has no remote yet — `ArtRichards/docs-cli` private until
v1.1 publishes; OQ4 skill source moves to `src/docs_cli/skill/`; OQ5
`bin/docs` is deleted). Phase 1's scope was expanded by the OQ3
override to carry the identity rename — new GitHub repo, local
checkout move `~/opt/docs` → `~/opt/docs-cli`, host-pointer updates —
in addition to the usual milestone-activation docs work. See the log
for the per-phase status table.

**Project v1 shipped 2026-05-22 — M1-M5 all complete.** M5 — Claude
Code skill closed the v1 roadmap on 2026-05-22 (post-ship polish on
2026-05-23; relocated under the package at M6 Phase 5). It is the
project's final v1 deliverable: a Claude Code skill — a `SKILL.md`
artifact at `src/docs_cli/skill/` (was `skills/docs/` at M5 ship) —
that makes an agent reach for the `docs` verbs automatically when
doing documentation work in a `docs`-managed tree. It adds no CLI
surface and changes no verb behaviour: it is a markdown artifact
whose `description` triggers on the right contexts (creating a
plan/spec/charter/milestone, archiving or renaming a doc, listing
docs, checking the tree, regenerating `INDEX.md`, adopting a foreign
Markdown directory) and whose body redirects to the appropriate `docs`
verb instead of hand-editing metadata, `INDEX.md`, or `archive/`. The
convention itself is not re-taught — the body links to the bundled
spec references at `src/docs_cli/skill/references/` (relocated from
`skills/docs/references/` at M6 Phase 5). The four M5 milestone-setup
OPEN QUESTIONS (OQ1-OQ4) were resolved and recorded as Decisions in
the task plan. **Post-ship polish (2026-05-23)** shortened `SKILL.md`
to a trigger surface (verb-task table + when-to-use scenarios +
never-hand-edit rule), bundled `convention.md` and `cli.md` as
references (byte-identical mirrors with a lockstep test), and
cleaned dev cross-refs out of the source specs. See
[m5-claude-code-skill-log.md](archive/2026-05-23/m5-claude-code-skill-log.md) for the
per-phase history (and the post-ship section appended to it) and
[m5-claude-code-skill.md](archive/2026-05-23/m5-claude-code-skill.md) for the milestone
summary.

M4 — Migration helper (`docs migrate`) shipped 2026-05-22 across ten TDD
phases. It added one verb — `docs migrate <dir>` — that adopts a
non-conforming directory into the convention: it walks a foreign tree, infers
the required metadata per file, and produces a migration plan (dry-run by
default; `--apply` writes the metadata blocks and normalises archive-style
subdirectories). See [m4-migration-helper-log.md](archive/2026-05-22/m4-migration-helper-log.md)
for the per-phase history and [m4-migration-helper.md](archive/2026-05-22/m4-migration-helper.md)
for the milestone summary.

M3 — Validation and query (`check`, `list`) shipped 2026-05-22 across ten TDD
phases. It added two read-only verbs — `docs check` (validate the tree, with
CI-usable exit codes) and `docs list` (filterable query view with a stable
JSON schema) — and regrouped `INDEX.md` by `Project` then `Role`. See
[m3-validation-and-query-log.md](archive/2026-05-22/m3-validation-and-query-log.md) for the
per-phase history and [m3-validation-and-query.md](archive/2026-05-22/m3-validation-and-query.md)
for the milestone summary.

M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) shipped 2026-05-21
across ten TDD phases. See [m2-mutating-verbs-log.md](archive/2026-05-21/m2-mutating-verbs-log.md)
for the per-phase history and [m2-mutating-verbs.md](archive/2026-05-21/m2-mutating-verbs.md)
for the milestone summary.

M1 — Parser and `docs index` shipped 2026-05-20 across ten TDD phases.
See [m1-parser-and-index-log.md](archive/2026-05-20/m1-parser-and-index-log.md) for the
per-phase history and [m1-parser-and-index.md](archive/2026-05-20/m1-parser-and-index.md)
for the milestone summary.

## Milestone progress

| Milestone | Status | Task plan | Log |
|---|---|---|---|
| M1 — Parser and `docs index` | **Complete** (2026-05-20) | [Plan](archive/2026-05-20/m1-parser-and-index.md) | [Log](archive/2026-05-20/m1-parser-and-index-log.md) |
| M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) | **Complete** (2026-05-21) | [Plan](archive/2026-05-21/m2-mutating-verbs.md) | [Log](archive/2026-05-21/m2-mutating-verbs-log.md) |
| M3 — Validation and query (`check`, `list`) | **Complete** (2026-05-22) | [Plan](archive/2026-05-22/m3-validation-and-query.md) | [Log](archive/2026-05-22/m3-validation-and-query-log.md) |
| M4 — Migration helper (`docs migrate`) | **Complete** (2026-05-22) | [Plan](archive/2026-05-22/m4-migration-helper.md) | [Log](archive/2026-05-22/m4-migration-helper-log.md) |
| M5 — Claude Code skill | **Complete** (2026-05-22) | [Plan](archive/2026-05-23/m5-claude-code-skill.md) | [Log](archive/2026-05-23/m5-claude-code-skill-log.md) |
| M6 — PyPI distribution preparation as `docs-cli` | **Complete** (2026-05-24, preparation only; publish moved to M9) | [Plan](archive/2026-05-24/m6-pypi-distribution.md) | [Log](archive/2026-05-24/m6-pypi-distribution-log.md) |
| M7 — Migration plan accuracy | **Complete** (2026-05-25; ship-ready locally, publish DEFERRED to M9 batched 1.3.0 per OQ-C) | [Plan](archive/2026-05-25/m7-migration-accuracy.md) | [Log](archive/2026-05-25/m7-migration-accuracy-log.md) |
| M8 — Adoption workflow (agent-driveable) | **Complete** (2026-05-25; ship-ready locally as 1.3.0, publish DEFERRED to M9 batched 1.3.0 per OQ-C) | [Plan](archive/2026-05-25/m8-adoption-workflow.md) | [Log](archive/2026-05-25/m8-adoption-workflow-log.md) |
| M9 — PyPI publish 1.3.0 | **Complete** (2026-05-25; `docs-cli==1.3.0` on PyPI; repo public; `v1.3.0` tag + GitHub release) | [Plan](archive/2026-05-25/m9-pypi-publish.md) | [Log](archive/2026-05-25/m9-pypi-publish-log.md) |
| M10 — Adoption-flow polish + 1.3.0 carry-overs (v1.4.0) | **Complete** (2026-05-27; shipped to PyPI via M11; 400/400 GREEN at M10 close; kebab-tiny dogfood PASS) | [Plan](archive/2026-05-27/m10-adoption-polish.md) | [Log](archive/2026-05-27/m10-adoption-polish-impl.md) |
| M11 — PyPI publish 1.4.0 | **Complete** (2026-05-27; `docs-cli==1.4.0` on PyPI; `v1.4.0` tag + GitHub release; chain-of-custody bit-perfect; headline M10 contract holds against PyPI-served wheel) | [Plan](archive/2026-05-27/m11-pypi-publish.md) | [Log](archive/2026-05-27/m11-pypi-publish-impl.md) |
| M12 — Project rename + M11 wart fixes + version SoT (v1.5.0) | **Complete** (2026-05-28; `dist/docs_cli-1.5.0-*` built locally, twine check PASS, 433/433 pytest GREEN at simplify close; shipped to PyPI as 1.5.0 via M13 on 2026-05-29) | [Plan](archive/2026-05-28/m12-project-rename.md) | [Log](archive/2026-05-28/m12-project-rename-impl.md) |
| M13 — PyPI publish 1.5.0 | **Complete** (2026-05-29; `docs-cli==1.5.0` on PyPI; `v1.5.0` annotated tag + GitHub release; chain-of-custody bit-perfect; all four M12 headline contracts hold against the PyPI-served wheel) | [Plan](archive/2026-05-29/m13-pypi-publish.md) | [Log](archive/2026-05-29/m13-pypi-publish-impl.md) |
| M14 — Robustness + autonomous archive (v1.6.0) | **Complete** (2026-06-02 impl-complete; **shipped to PyPI as `docs-cli==1.6.0` via M17 on 2026-06-03**, batched with M15; `mv` atomicity, `new` strict-root, four-verb `touch`/`archive`/`mv`/`project rename` excludes, slug/`OSError`/`atomic_write`-fsync guards, non-interactive `--cascade`, bundled-ref guard + packaging fix; the M14 pair was archived to `archive/2026-06-03/` at the M17 closeout) | [Plan](archive/2026-06-03/m14-robustness-agent-native.md) | [Log](archive/2026-06-03/m14-robustness-agent-native-impl.md) |
| M15 — Agent-native doc authoring (v1.6.0) | **Complete** (2026-06-03 impl-complete, Phases 1–10; **shipped to PyPI as `docs-cli==1.6.0` via M17 on 2026-06-03**, batched with M14 — `docs project set`, single-file `docs stamp`, `--body-from` real-frontmatter detector, skill/cli docs; 501 GREEN at M15 close, gate clean tree-wide; the M15 pair was archived to `archive/2026-06-03/` at the M17 closeout) | [Plan](archive/2026-06-03/m15-agent-native-authoring.md) | [Log](archive/2026-06-03/m15-agent-native-authoring-impl.md) |
| M16 — Bundled docs skill quality artifacts | **Complete / archived** (2026-06-01 impl-complete; documentation-only bundled `docs` skill guidance; code on `main` as `9ceb113`; the M16 trio was archived to `archive/2026-06-01/` by M18's Phase-9 sweep on 2026-06-03) | [Plan](archive/2026-06-01/m16-bundled-docs-skill-quality.md) | [Log](archive/2026-06-01/m16-bundled-docs-skill-quality-impl.md) |
| M17 — PyPI publish 1.6.0 | **Complete** (2026-06-03; `docs-cli==1.6.0` on PyPI, batching M14 + M15 as M9 batched M6+M7+M8; `v1.6.0` annotated tag at `95f23a6` + GitHub release; chain-of-custody bit-perfect; all seven M14 + M15 headline contracts hold against the PyPI-served wheel; milestone doc archived to `archive/2026-06-03/`, impl log stays `Lifecycle: active`) | [Plan](archive/2026-06-03/m17-pypi-publish.md) | [Log](m17-pypi-publish-impl.md) |
| M18 — Archive edge integrity (intra-archive Related: rewriting) | **Complete / archived** (2026-06-03 impl-complete; correctness fix to `docs archive` — the conditioned archived-skip in `_rewrite_referring_edges` rewrites the moved doc's own archive-subtree `Related:` edges + repoints already-archived referrers; flipped the pinned `test_archive_does_not_rewrite_archive_subtree_edges` → `test_archive_repoints_already_archived_referrer`. `docs mv` own-edge parity (Open Q1 INCLUDED) verified already satisfied — no code change. Phase-9 payoff archived the M1–M9/M12 pairs + M16 trio + 3 stray impl-logs; `docs check docs/` exit 0. 510 GREEN. The M18 pair was archived to `archive/2026-06-12/` at the M20 closeout — it rode along in the 1.6.0 tree as an already-merged fix and added no new public surface to 1.6.5) | [Plan](archive/2026-06-12/m18-archive-edge-integrity.md) | [Log](archive/2026-06-12/m18-archive-edge-integrity-impl.md) |
| M19 — Post-edit validation ergonomics (touch --check + configurable stale window) (v1.6.5) | **Complete** (2026-06-12; feature milestone — `docs touch --check [--stale N]` folds the existing `check_tree` into the touch loop after the end-of-batch reindex; `.docs.toml [check] stale_days = N` makes the stale window per-tree configurable (CLI `--stale` overrides); cosmetic `docs new --body-from` help-string fix closes the rolled-forward follow-on. No new verb, no new check rule; additive + backward-compatible. **Shipped to PyPI as `docs-cli==1.6.5` via M20 on 2026-06-12.** Q1–Q6 + OQ-1..OQ-5 RESOLVED; threshold-provenance folded into D2. Full suite 540/540 GREEN (533 + the Step-2 review +7), gate clean tree-wide, `docs --version` → `docs 1.6.5`. The M19 pair was archived to `archive/2026-06-12/` at the M20 closeout) | [Plan](archive/2026-06-12/m19-post-edit-validation.md) | [Log](archive/2026-06-12/m19-post-edit-validation-impl.md) |
| M20 — PyPI publish 1.6.5 | **Complete** (2026-06-12; `docs-cli==1.6.5` on PyPI, the publish-only counterpart to M19 one-to-one as M13 shipped M12; `v1.6.5` annotated tag at the Phase-4 commit `0855466` + GitHub release; chain-of-custody **bit-perfect for both wheel AND sdist** (wheel `aba36e92…`, sdist `f9de1eb4…`); all M19 headline contracts hold against the PyPI-served wheel; ran the [release-runbook.md](release-runbook.md) on `main` (M17 precedent — no TDD code phases). NEW vs M17: the Phase-5 closeout refreshed the host-machine skills (`docs install-skill --force` + a workflow-skill sweep that caught + fixed one stale `--body-from` reference in `project-foundation`) per the CLAUDE.md skill-update-flow policy. Q1 → FULL AUTONOMOUS, Q2 → archive the M18 + M19 pairs + M20's own milestone doc to `archive/2026-06-12/`; the M20 impl log stays `Lifecycle: active`) | [Plan](archive/2026-06-12/m20-pypi-publish.md) | [Log](m20-pypi-publish-impl.md) |
| M21 — Update-check notification (PyPI new-version notice) (v1.7.0) | **Complete** (shipped to PyPI as `docs-cli==1.8.0` **batched via M24** 2026-07-03; pair archived to `archive/2026-07-03/`; impl-complete 2026-06-29, all 10 TDD phases; **1.7.0 skipped on PyPI**) (scaffolded 2026-06-12; **re-scoped to CLI-only 2026-06-29**; **all 10 TDD phases done 2026-06-29** — Phases 1–4 (RED baseline) on `m21/phases-1-4`, Phases 5–10 on `m21/phases-5-10`: full suite **604 GREEN**, gate clean tree-wide, `pyproject` at 1.7.0, `docs --version` → `docs 1.7.0`; the online path verified against live PyPI + dogfooded end-to-end, pytest 100% offline) — feature milestone introducing docs-cli's **first network surface**: a once-per-24h, fail-silent PyPI version check (stdlib `urllib` only, 1.0s timeout, 24h-cache-gated under a three-key `{last_check, latest_version, last_notified}` cache, zero-dependency wheel preserved) that emits ONE STDERR line nudging the user/agent to update **the CLI** (`pip install -U docs-cli`; wording `docs: update available <current> -> <latest> — run: pip install -U docs-cli`). STDERR-only, never alters the exit code, suppressed under `--quiet`/`--json`/`CI`/`DOCS_CLI_NO_UPDATE_CHECK`/`DO_NOT_TRACK` (the user-level config opt-out is DEFERRED out of v1.7.0 — OQ-5/5a), but **deliberately shows on non-TTY** (inverting gh's TTY rule — the agent is the actor). The former skill-drift notice (D5) + the dual-action `docs install-skill --force` half are **CUT** (re-scope 2026-06-29 — no skill inspection, no Claude-Code assumption); the skill story moves to follow-on **M23**. Ships as **1.7.0** (minor — additive; 1.6.5 was the operator-decreed patch exception); a later milestone publishes (M19→M20 pattern). **OPEN QUESTIONS netted out — none outstanding** (OQ-1..OQ-9 RESOLVED 2026-06-12; OQ-6 "ship D5" REVERSED by the re-scope). Shipped batched as 1.8.0 via M24; archived 2026-07-03. | [Plan](archive/2026-07-03/m21-update-check.md) | [Log](archive/2026-07-03/m21-update-check-impl.md) |
| M22 — Doc-tree root placement guidance (project ≠ directory) | **Complete** (impl-complete 2026-06-24; shipped to PyPI as `docs-cli==1.8.0` **batched via M24** 2026-07-03, pair archived; all ten TDD phases; documentation-only, M16-shaped — no CLI/code change, no version bump; convention.md §Subdirectories + bundled SKILL.md "where to put `.docs.toml`" guidance: `Project:` is metadata not a directory, and root-relative `Related:` makes a nested lone project prefix every sibling ref; RED-first `tests/test_skill_root_placement.py`; bundled reference mirrored byte-identical; dogfood-snapshot refreshed; CHANGELOG staged under 1.7.0 UNRELEASED. Full suite 543 GREEN, gate clean, Phase-9 dogfood reproduced the redundant-prefix consequence. Ran **before** M21 per the operator's run-order decision 2026-06-24 — number = creation order, not execution order. Shipped batched as 1.8.0 via M24; archived 2026-07-03 (the publish closeout swept it, M18/M19/M21 + M16 precedent). Companion `project-foundation` note tracked separately in `agent-playbook-suite`) | [Plan](archive/2026-07-03/m22-root-placement-guidance.md) | [Log](archive/2026-07-03/m22-root-placement-guidance-impl.md) |
| M23 — Agent-aware install-skill + recorded-dest skill-refresh hint (v1.8.0) | **Complete** (shipped to PyPI as `docs-cli==1.8.0` **batched via M24** 2026-07-03; pair archived to `archive/2026-07-03/`; impl-complete 2026-07-02, all 10 TDD phases) (Phases 1–4 (Contract & RED baseline) on `m23/phases-1-4`; Phases 5–10 (implementation → dogfood → closeout) on `m23/phases-5-10`: full suite **636 GREEN**, gate clean tree-wide, `pyproject` at 1.8.0, `docs --version` → `docs 1.8.0`; online path dogfooded against a seeded throwaway cache, pytest 100% offline) — follow-on to the M21 re-scope that restores the skill-refresh nudge cut from M21. Makes `docs install-skill` **agent-aware**: `--dest` is the agent-agnostic source of truth; TTY-aware resolution (human may be prompted; an agent [non-TTY] is **never** blocked → falls back to the default, OQ-1); the resolved dest is **recorded** (path only — **never** content) to a separate `${XDG_STATE_HOME:-~/.local/state}/docs-cli/install-skill.json` (OQ-2; M21's 3-key cache stays frozen); the "Claude Code skill" framing in `install-skill`'s help is neutralised to **"agent skill"** (reconciling with `cli.md`); and M21's update notice gains a skill-refresh hint pointed at the **recorded** dest (riding M21's same suppression matrix + throttle). Replay/remember allowed; content-inspection + agent-guessing NOT. Out of scope: multi-agent skill *formats* + agent auto-detection. **Depends on M21.** Ships **1.8.0** (OQ-4). **The four OPEN QUESTIONS are resolved** (OQ-1 default / OQ-2 separate XDG_STATE file — **confirmed as-shipped at the M24 gate, D4**; OQ-3 last-write-wins single dest; OQ-4 1.8.0). Shipped batched as 1.8.0 via M24; archived 2026-07-03. | [Plan](archive/2026-07-03/m23-agent-aware-install-skill.md) | [Log](archive/2026-07-03/m23-agent-aware-install-skill-impl.md) |
| M24 — PyPI publish 1.8.0 | **Complete** (2026-07-03; `docs-cli==1.8.0` live on PyPI; `v1.8.0` tag at `1a01f74` + GitHub release; chain-of-custody bit-perfect wheel `29ac3ced…` + sdist `62a29285…`; all M21+M23 contracts hold against the served wheel; host skills refreshed) — operator-driven publish shipping the post-1.6.5 train **batched** as `docs-cli==1.8.0`: M21 (update-check, built 1.7.0) + M22 (doc-only, no bump) + M23 (agent-aware install-skill, 1.8.0), mirroring M17 (M14+M15→1.6.0) / M9 (M6+M7+M8→1.3.0). Tree at 1.8.0 (M23 Phase 7, merged `839daef`); **1.7.0 skipped on PyPI** (its CHANGELOG entries fold into 1.8.0, D2). Runbook-driven — no TDD code phases; the [release-runbook.md](release-runbook.md) sections are the phases. Setup decisions: D1 batched 1.8.0; D2 CHANGELOG fold; D3 "author now, confirm at the gate" (runbook starts on explicit go-ahead, pauses before every irreversible step); D4 M23 OQ-1/OQ-2 confirmed as-shipped (flag cleared); D5 closeout archived the M21+M22+M23 pairs + the M24 milestone doc to `archive/2026-07-03/` (impl log stays active). Ran the release-runbook end-to-end under D3 (operator go at the Phase-4 gate). | [Plan](archive/2026-07-03/m24-pypi-publish.md) | [Log](m24-pypi-publish-impl.md) |
| M25 — Reciprocal relationship integrity and `docs relate` | **Active / implementation-complete — all ten TDD phases** (Phases 1–4 2026-08-11 on `m25/phases-1-4`; Phases 5–10 2026-08-12 on `m25/phases-5-10`; **777 GREEN**, gate clean, dogfood done, fresh-eyes review folded in incl. the operator-approved post-freeze `duplicate-field` rule; Step-3 `/simplify` done 2026-08-12 on `m25/simplify` (-17 lines, 777 GREEN unchanged, no contract moved); stays `Lifecycle: active` until the M29 publish closeout) — hard inverse validation + explicit active/archived repair; first v2.0 implementation milestone. Six recognized verbs, the `missing-inverse` rule, and `docs relate add|remove` (idempotent, `--dry-run`/`--json`, one reindex, staged publish + rollback, audited archived repair) are implemented; the version deliberately stays 1.8.0 (D6) with CHANGELOG entries under `UNRELEASED` for M29 to name. | [Plan](m25-reciprocal-relationship-integrity.md) | [Log](m25-reciprocal-relationship-integrity-impl.md) |
| M26 — Safe explicit archive selection | **Active / implementation-complete — all ten TDD phases (2026-08-13); Step-3 `/simplify` done 2026-08-13 on `m26/simplify` — no code changes, 895 GREEN unchanged, every remaining candidate re-examined and found load-bearing** (Step 1 Phases 1–4 on `m26/phases-1-4` 2026-08-12 / 2026-08-13, classified RED baseline 884 collected / 104 failed / 780 passed with 769 of 777 pre-existing ids still GREEN, Step-1 audit and fresh-eyes review folded; Step 2 Phases 5–10 on `m26/phases-5-10` 2026-08-13 — **895 GREEN** (888 at the Phase-8 gate, 889 after the audit's lock, 895 after the fresh-eyes review fold-in), 774 of the 777 pre-existing ids mechanically proven present and passing, 3 deliberately removed, 121 new; the closeout workflow dogfooded on a throwaway copy of this tree, where the unfiltered preview reproduces E1 exactly; `pyproject.toml` untouched at 1.8.0) — bare `--cascade` and the retired `--interactive` refuse before any write (registered-and-refusing, exit 2, migration guidance), `--cascade-dry-run` previews every one-hop candidate as selected / not-selected / ineligible, a related-document write requires an explicit `--cascade-only GLOB` whose full plan is validated first (deduplicated, canonical-path matched, collision- and writability-checked, archived neighbours excluded, archived primary refused, empty selection refused), and `docs archive --json` emits one operation-plan record whose shape is identical for preview and apply. Registered 2026-08-10, planned in depth 2026-08-12 on `m26/milestone-setup`; setup reproduced five v1.8.0 defects **E1–E5**, each mapped to named regression coverage — bare `--cascade` on the M25 pair proposing to archive `plan.md` + `cli.md` + `convention.md` + `test-strategy.md` + `status.md`; a duplicate edge printing a false failure; a basename collision leaving a partial archive at exit 0 with `docs check` clean; an archive-subtree edge silently relocating and re-dating an archived doc; a typo'd scope looking like success. **All seven setup questions RESOLVED** (Q1/Q5/Q6 operator; Q2/Q3/Q4/Q7 conductor-resolved); extending M25 — D5's staged-publish-plus-rollback to N docs was considered and declined. Two frozen signatures were amended under conductor decision and recorded in the milestone doc (`CoordinatedWriteError.exit_code`, `_print_archive_lines(cascade=…)`), and one defective Step-1 test helper that no implementation could satisfy was fixed in its own labelled commit with no assertion changed. The same-instance audit and an independent fresh-eyes review then folded in eight more fixes, the review's **blocker** among them: a primary resolving outside the docs root — through a symlink, or a `--root` naming a different tree — was being archived INTO the tree (exit 0 in one shape, `docs check` clean afterwards); it now refuses at exit 1 before any write, in the cross-verb wording the other explicit-path verbs use. No version bump (M25 — D6); stays `Lifecycle: active` until the M29 publish closeout. | [Plan](m26-safe-archive-selection.md) | [Log](m26-safe-archive-selection-impl.md) |
| M27 — Markdown body-link validation | **Implementation-complete — all ten phases done** (2026-08-14, `m27/phases-1-4` + `m27/phases-5-10`; stays `Lifecycle: active` until the M29 closeout) — a pure stdlib-only scanner over a deliberately bounded, named Markdown subset (inline links with plain/angle destinations and optional titles, plus reference definitions; images, autolinks, raw HTML and reference uses excluded), length-preserving fenced- and inline-code masking, destinations resolved **relative to the referring document** with fragments preserved and never validated, and **two** hard errors: `broken-body-link` (a missing in-root destination) and `outside-root-body-link` (a destination that leaves the tree), both `severity: error`, exit 2, one finding per occurrence, JSON key set left **closed** with the location carried in `message`. The check **never stats outside its own root** — an escape is decided by path arithmetic, and containment is tested **before** existence so the two rules never double-report. The `BodyLink` record's exact destination-token span is the handoff to M28 — no second parser. Registered 2026-08-10, planned in depth 2026-08-14 on `m27/milestone-setup`; setup measured the tree read-only and produced eight pieces of evidence **E1–E8** — **139 unresolved local destinations across 29 documents, 100% of them under `archive/`** (132 a pure `../../` rebase, 5 a moved target, 2 a bundled-skill file that never lived in the docs tree); `docs check` exits **0** today with all 139 broken; `test_check_dogfood_repo_docs_is_clean` makes the legacy policy a hard gate inside the suite; code masking prevents 7 measured false positives (including `architecture.md:182`'s `[<path>](<path>)`) while a 4-space indented-code rule would mask 9 spans that are all real links; a containment census over `docs/`, all 33 fixture trees and the bundled skill finds **exactly one** escape (`charter.md:52`) and none in any fixture; and nothing in the repository exercises the exotic grammar, so Phase 3 must author it. **All seven setup questions RESOLVED** — Q1/Q2/Q5 operator, Q3/Q4/Q6/Q7 conductor. **Q1: repair, rule stays uniform** — the breakage class is produced by `docs archive` itself and `docs/` ships in every PyPI sdist and is public on GitHub, so exempting archived docs would leave the tool silent about the damage it causes; the one-time destination-token-only repair is `Updated:` + `Revision:` audited and lands in Phase 6, and `convention.md` gains a third archived-document exception with a stated blast radius. **Q5 was resolved against the setup recommendation and then amended**: the hermetic boundary is kept (a check must be a function of the tree alone) but the escape is **reported** rather than skipped — `outside-root-body-link` is an operator-approved post-draft scope addition following M25's `duplicate-field` precedent, and `charter.md:52` is converted to the canonical GitHub URL in Phase 6, the same treatment Q1 gives the two `adoption-playbook` links and doubly right since the relative alternative would itself have violated Q5. **Phase 1 (2026-08-14)** froze the grammar and its exactness rules, the masking contract and its ordering, destination classification, the containment test and its precedence over existence, **both** message templates, and the `BodyLink` span record — in `cli.md`, `convention.md` and the milestone's *Decisions (Phase 1 — BINDING)* — with **zero** `cli.py` edits, 895 passed unchanged and `docs check --root docs` at exit 0; three setup-frozen items were amended under conductor decision and recorded as amendments (`broken-body-link`'s message contradicted Q7's directory rule, `outside-root-body-link` had no message at all, and the 33-tree no-new-findings lock becomes a new sibling test rather than an extension that would cover only 23 trees and fail on the damaged `bodylink-*` fixtures), and a third bundled-skill authoring trap was found by tripping it (`test_installed_skill_references_do_not_depend_on_source_checkout` forbids the literal `../src/docs_cli/`, which is exactly E7's real escaping destination). **Phase 2 (2026-08-14)** wrote the RED suite — **+163 test ids, zero removed, zero collection errors** (1058 collected, 129 failed, 929 passed) — across a new 105-item pure-scanner module and the rule, subprocess, `touch --check` and bundled-skill locks; it closed one Phase-1 gap in the specs (a reference definition has no enclosing `)`, so its plain destination ends at whitespace or end of line) and caught a whole falsely-GREEN family before it existed, since `load_config` tolerates a missing directory and every "silent tree" lock would otherwise have passed on a fixture that was never written. **Phase 3 (2026-08-14)** authored six `bodylink-*` fixture trees (17 files, one semantic each, static dates, **no** pre-existing fixture edited): every supported form resolving, one unresolved link, every excluded form silent, nested up-and-down resolution including `../sub/../back-inside.md`, the un-rebased archive shape, and two escapes chosen so one cannot exist while the other provably does — the pair that makes E7's "whether or not it would have resolved" testable. **Phase 4 (2026-08-14)** captured the classified RED baseline — **1079 collected, 137 failed, 942 passed** after the Step-1 same-instance audit's six fixes and the fresh-eyes review's thirteen further locks — zero collection errors, zero tracebacks, zero xfails, exactly two exception classes, every RED in a named family and every one of the 47 GREEN-at-baseline locks classified degenerate / genuine / transitional — with **all 895** pre-existing ids mechanically proven present and passing (`comm -23` = 0 and `comm -12 failed old` = 0; M27 removes and modifies no pre-existing test, which is what Phase-1 amendment 3 bought). No product code was touched across Phases 1–4. The audit's six fixes were a stale `plan.md`, an E5 lock narrower than the coverage the milestone claims, an ordering lock pinning only half the findings' placement, a specified-but-unlocked nested-vs-root `INDEX.md` split, an under-constrained mask assertion, and `BodyLink`'s untested immutability; two items were surfaced for the reviewer and both came back settled (the repair-clause asymmetry between the two messages is intentional and stays; specs describing Phase-6 behaviour ahead of the code is accepted per M26). The independent **fresh-eyes review** found **no blockers**, reproduced the whole baseline, and returned nine should-fix items and four nits, all conductor-resolved and folded in — the headline being that the BINDING percent/backslash/`#` decode order had no test at all, so the natural `unquote()`-then-`split()` implementation violated the frozen contract and passed. **Phase 5 (2026-08-14)** landed the whole pure scanner in one new banner section of `src/docs_cli/cli.py` — `BodyLink`, the length-preserving `_mask_code`, `scan_body_links`, `classify_destination`, the resolution/containment helpers and `body_link_findings` — while wiring **no** rule, so the 18 rule/CLI/skill tests stay honestly RED at the `check_doc` seam (**18 failed, 1061 passed**; all 119 pure-scanner tests GREEN; every remaining failure an `AssertionError` and none an `AttributeError`; no test file edited). The real scanner reproduces every published census number exactly — 393 recognised spans, 139 broken and 1 escape across 30 documents in `docs/`, and 0/0 across all 33 pre-M27 fixture trees and the bundled skill. Seven grammar points the frozen contract left silent were settled in `cli.md` and its byte-identical mirror rather than only in the log, because each changes what the scanner hands M28: an empty inline destination is a recognised link with a zero-width span; newlines are ordinary whitespace either side of an inline destination; the blank-line bound covers the whole candidate rather than only the label; the closing fence needs the same character, equal-or-greater length and nothing but whitespace after the marker, and the whole fence line survives verbatim; a reference definition's label opens and closes on one line and its destination ends at an unescaped `)` at depth 0; a `(…)` title does not nest; and `Path.exists()` is kept, so a dangling symlink inside the root is `broken-body-link`. **Phase 6 (2026-08-14)** wired both rules into `check_doc` in three lines — after the `broken-ref` group and before `stale`, with `check_tree`, `exit_code_for`, `finding_to_json`, `_print_check_findings`, `_run_touch_check`, `_iter_doc_texts` and the argparse all untouched — and, in the **same commit**, performed the D6 live-tree repair: **140 occurrences across 30 documents**, split **132** root rebases / **5** move-map lookups / **2** playbook URLs / **1** escape URL, driven by the Phase-5 scanner itself and spliced by offset right-to-left (literally the M28 operation, and the first live proof the span contract works). All 30 got an `Updated:` bump and the 29 archived ones a single uniform dated `Revision:` bullet; `convention.md`'s promised repair date is now the real 2026-08-14. Six independent checks prove no other byte moved — 30/30 round-trip reconstructions byte-identical, 166 changed lines with every non-`equal` opcode inside a recorded destination span, `+3`/`+0` net line arithmetic, every metadata invariant held, a re-census at **0 broken / 0 escapes with the recognised-span count still 393**, `docs check --root docs` at exit 0 with both rules live, and the INDEX snapshot identical after its 30-line mechanical churn was regenerated in the same commit. Suite: **2 failed, 1077 passed**, the only REDs left being Phase 7's two surface locks. **Phase 7 (2026-08-14)** reconciled every parallel surface — `docs check`'s argparse description, the bundled `SKILL.md` check row and `references/use-cases.md` (the *Validate in CI* row plus a new M27 upgrade section), and `CHANGELOG.md` under `UNRELEASED` with one `Added` entry per rule, a BREAKING `Changed` entry, and the adopter recipe for **both** repairs; no spec edit was needed, so both mirrors stayed byte-identical and the INDEX snapshot needed no regeneration. The suite went **fully GREEN at 1079 passed**, one phase early (**1082** after the Step-2 audit's three locks). **Phase 8 (2026-08-14)** ran the formal gate — **1079 collected, 1079 passed, 0 failed**, zero xfail/xpass, zero tracebacks, all quality gates clean — plus the `comm` no-regression proof against **both** anchors: 0 ids removed since the pre-M27 `d61da1d` and since the Step-1 head `ddf0a45`, **0 added by Step 2**, 895 + 184 = 1079, and `git diff ddf0a45 -- tests/*.py` empty, so no test was relaxed, weakened, deleted or rewritten to reach GREEN. Deliverables 2–5 ticked. **Phase 9 (2026-08-14)** replayed the pre-repair damage on throwaway copies (140 findings, 139 + 1, exit 2, 30 documents) and walked the documented recipe from `docs check --json` alone — never the scanner API — reaching exit 0 with the same 132/5/3 split and **0 destination-token mismatches** against the repaired tree; hermeticity proven end to end on the pre-repair copy with identical stdout and exit code from a with-sibling and a bare location and **0 probes outside the root** under a spy; all 39 fixture trees and the bundled skill sweep clean bar M27's three damaged ones; runtime 183 ms over the 2.5 MB live tree and 61 ms for the 303 KB adversarial set, **33× under the 2.0 s lock**. **Phase 10 (2026-08-14)** ran the `/simplify` pass — four changes applied, six candidates considered and rejected with the reason recorded — closed `architecture.md` › `check` (the pure pipeline, the per-document-not-cross-document contrast with `reciprocity_findings`, the length-preserving mask as the reason offsets stay valid, and the span record as M28's input) and `test-strategy.md` › *What we don't test* (which still claimed the body was opaque), extended README's one-line `docs check` summary, and folded in the Phase-9 quality item: the live-tree scan went from 183 ms to **81 ms**, with `docs check` at **0.16 s** end to end. **M27 is implementation-complete**: all ten phases, every deliverable met, and the `BodyLink` span contract handed to M28. The **Step-2 same-instance audit** then found **twelve** issues and fixed all twelve — **three of them real behavioural defects in the scanner**, every one invisible to the finding set and to the suite, reachable only by reading the frozen contract as a specification. The critical one is a **hermeticity hole**: a percent- or backslash-encoded leading slash (`%2Fetc/passwd`) classifies `local` because classification runs on the token as written, decodes to `/etc/passwd`, wins the `posixpath.join`, and — because Phase-1 point 9 dropped the containment predicate's leading-`/` leg — read as *contained*, so `docs check` **stat'd a path outside its own root**, the single thing D4b exists to forbid. The leg is restored; point 9's stated intent survives (a literally-written `/path` is still silenced by classification) while its unsound mechanism does not, and **point 9 is amended in place — a BINDING Phase-1 decision, flagged for the operator**. The other two defects: a link nested inside an image label was silently dropped, which the Phase-1 linearity note had foreseen and which would have left M28 unable to rewrite that destination; rule 5's *at least one whitespace character* before a title was not enforced; and two docstrings asserted things that were false. All three scanner fixes are **behaviour-neutral on every real input** — the live-tree census (393/0/0), the pre-repair replay (139 + 1 across 30 documents) and the 39-tree fixture sweep are all unchanged — and the three reachable defects are now **locked**, taking the suite to **1082 passed / 0 failed**. The remaining findings were spec and documentation corrections: an `architecture.md` line-count and module-annotation drift, a Success criterion that called all 139 archived repairs "rebases" when only 132 are, a `convention.md` promise of *29 named archived documents* that no surface actually named, a `Progress:` line and an "in flight" claim that contradicted "all ten phases complete", a CHANGELOG example mixing a real filename with a synthetic destination, a self-contradictory fence-line clause, and runtime figures that had drifted. Three items are surfaced for the operator rather than auto-decided. An independent **fresh-eyes review** then reproduced all of that adversarially — a 40,000-case destination fuzz under a `Path.exists` spy (21,747 stats, 0 outside the root), an `strace` of a real `docs check`, its own round-trip of the 140-occurrence repair (30/30 byte-identical), a 20,000-input mask/span fuzz, and 40 grammar shapes walked clause by clause — and returned **one blocker plus eight further items**, every one folded in. The blocker was the mirror image of the audit's own A2: a link whose **label** is an image (`[![diagram](diagram.png)](full-size.md)`, the ordinary badge / thumbnail idiom) ended its label at the *image's* `]`, so `docs check` **reported the image** as `broken-body-link` — against the success criterion that images produce no finding, and against operator-binding Q2's own words — and never emitted the real destination, so M28 would never rewrite it. Rule 2 is amended (a nested image consumes one `]`) and implemented as a level table, because the accepted `]` depends on where the label started and a rescan is quadratic. The review also closed **two residual quadratics** — many unterminated `<` or `(…)` titles inside one paragraph, measured at 3.27 s and 5.96 s, now 6.7 ms and 10.8 ms — corrected three places that claimed a linearity which did not hold, had the dangling-symlink lock written rather than deferred, qualified a spec sentence that could not be true alongside S9, stopped a percent-decoded control character splitting a finding across two lines, and fixed a **pre-existing** `OSError` crash on an over-long path segment at **both** the body-link and `broken-ref` probes. Final: **1087 passed / 0 failed**, eight test ids added across the audit and the review, **zero removed** against both anchors, and no assertion loosened. No version bump (M25 — D6). | [Plan](m27-markdown-body-link-validation.md) | [Log](m27-markdown-body-link-validation-impl.md) |
| M28 — Move-safe Markdown body-link rewrites | **Active / implementation-complete — all ten TDD phases done** (2026-08-15 on `m28/milestone-setup` + `m28/phases-1-4` + `m28/phases-5-10`; **all seven setup questions RESOLVED** — Q1/Q2/Q3 operator, Q4–Q7 conductor; depends on M26 + M27) — `docs mv` and `docs archive` rebase the parsed local Markdown destination tokens a move makes stale, reusing M27's scanner and its exact destination spans (no second parser) and splicing right-to-left so every unrelated byte survives. The two move classes — a link whose *target* moved, and a link *inside* a document that itself moved — are **one formula**: resolve from the referrer's old location, map the resolved target through the move set, relativise against the referrer's new directory. Mapping is by **normalised target**, so every spelling of one file is rewritten and no alias list is needed (unlike M26 — Q5's, forced by `Related:`' exact-string match). The plan is built and validated **before** the first byte moves — which inverts `_cmd_mv`'s move-then-rewrite ordering and gives `mv` M26 — D4's refuse-with-zero-mutation guarantee for the first time — and the `Related:` rewrite and the body splices land in **one** `atomic_write` per document. Registered 2026-08-10, scope extended 2026-08-15 from issue #1 finding 1 (the strand-check), planned in depth 2026-08-15; setup measured the tree read-only and reproduced each defect on throwaway copies, producing **E1–E8**. Both verbs now produce trees that fail the tool's own gate: `docs mv plan.md milestone-plan.md` rewrites 35 `Related:` bullets, exits 0, and leaves **42 `broken-body-link`** across 14 documents (E1); `docs archive m17-pypi-publish-impl.md` exits 0 and leaves **13** — 10 incoming, 4 of those inside archived referrers, plus 3 inside the moved document itself, so one command produces **both** classes (E2); the real closeout `--cascade-only 'm25-*'` leaves **6** in `status.md` and `plan.md` (E3). 379 local destinations over 71 documents resolve to 69 targets, worst-hit `release-runbook.md` 49 / 17 docs and `plan.md` 42 / 14 (E4); **131 body links in 27 archived documents point at active documents** (E5), making the archived-referrer rewrite a blocker — without it, moving a core document leaves hard errors no verb can repair — resolved by widening M18's move-driven exception along its own axis rather than granting the fourth exception `convention.md` says it will not grant. `rewrite_related_refs` cannot be reused: it matches by exact string while the same target is spelled three ways in this tree (E6). No `mv` / `archive` fixture carries a body link at all, and the corpus has zero angle / percent / backslash destinations and exactly one fragment, so Phase 3 authors every form (E8). **Q1 amended the routing entry (A1)**: the routed strand-check's literal predicate — refuse if the plan leaves a still-active document pointing at a newly-archived one — was measured over three plans (E7) and **refuses a textbook `--cascade-only 'm26-*'` closeout** (8 still-active edges + 8 body links from 7 deliberate referrers), so the routing note's "self-cancels for legitimate whole-set archiving" claim does not hold on a real tree, while issue #1's harm reproduces live (`--cascade-only '*'` marks `plan.md`, `cli.md`, `convention.md`, `test-strategy.md`, `status.md` selected). Resolved into **two binding legs**: leg 1 refuses only when a still-active document outside the plan declares itself `child-of` a document the plan would archive (0 on the closeout, 6 on both harm plans), and leg 2 **reports** every other still-active inbound reference — any other `Related:` verb, every body link — in the preview, the apply output and the record's `strands` array, refusing nothing; leg 2 is the half that answers issue #1's actual complaint and carries its own deliverable, success criterion and coverage. Rejected with reasons: the literal predicate, an unbounded-`'*'` refusal (defeated by `*.md`), a `Role:`-based rule. **Q2 (A2)** supersedes the stub's own recommendation — archived referrers get **destination tokens only**, no `Updated:` bump and no `Revision:` bullet, by widening M18's exception rather than granting a fourth. **Q3 (A3)** gives `docs mv` a real preview and a `--json` rewrite-plan record and `archive --json` the same rewrite section plus `strands`, one schema for preview and apply, and answers issue #1 finding 4 by declining `--report-links` as a design while adopting its output. Q4–Q7 conductor-resolved: untouched non-`local`/broken/escaping destinations, byte-for-byte no-op preservation with a `posixpath.relpath` rewrite otherwise, `docs migrate` out of scope, and M26's duplicate-bullet follow-up re-deferred rather than reaching into its frozen Q5 contract. **Phase 1 (2026-08-15)** froze the whole machine-facing contract as *Decisions (Phase 1 — BINDING)* items (A)–(M) — the move map keyed by canonical target with aliases feeding the `Related:` half only; the formula's BINDING step order with the no-op test stated **semantically** rather than as a string test, which is what makes a co-moving pair a zero-byte diff; one renderer with an invariant delimiter form and a grammar-derived encode set per form, `%` first, locked by a decode round-trip against the scanner's own `_split_destination`; the never-creates-an-escape proof; splices descending then `Related:` then archive metadata in **one** `atomic_write`; the pre-flight's three proofs at exit 2 with zero bytes written (parseability is the walk's, not the pre-flight's); the archived-referrer rule as one sentence, plus the two things A2 left inventable (no `Updated:` bump on an **active** referrer either, and an archived document `mv`'d gets class-2 rebasing of its own destinations); both strand legs and their source set; both check orders; the message catalogue; both `--json` schemas; and the Phase-5 signatures — with the author-facing halves in `cli.md` and `convention.md` (M18's exception **widened**, M27 — D6's *last one this convention grants* sentence **reconciled** at three). Three setup-frozen items were amended in place — M26's compatibility matrix (**a preview adopts plan-*construction* failures and reports-but-does-not-adopt *consequence* verdicts**, closing M26's own follow-up item 2), the E7 leg-2 row (plan B's `strands` is observed in its **preview**, because a refusal emits no record), and the E3 row (`movelink-closeout` **reproduces** the `archive-pair` shape, resolving the milestone's own contradiction with its Phase-3 exit criterion) — and eleven Step-1 resolutions R1–R11 recorded with reasoning. One contract decision is worth naming: the Step-1 plan put the whole-tree walk at check-order 5b for **both** paths, which would have inverted the precedence `cli.md` freezes (an unwritable member and a malformed referrer would swap messages, and a `--cascade-only` write selecting nothing would exit 1 instead of 2); the frozen contract puts it at **5b for the preview and 8 for the write path**, so M28 adds steps around M26's order without changing one precedence it froze. Zero `cli.py` edits, 1087 passed unchanged, `docs check --root docs` exit 0. **Phase 2 (2026-08-15)** wrote 182 new ids with **zero** deleted test lines and zero collection errors (1269 collected, 181 failed, 1088 passed at the time; 194 authored after the audit): a 153-item pure seam reached through one `_m28()` wrapper, plus 12 `mv`, 14 `archive`, 1 `check` and 2 bundled-skill locks. Three things keep them honest — every fixture-backed test asserts its tree **exists** so the family was RED before Phase 3 rather than green on an empty copy; the `movelink-*` check lock names its seven trees explicitly, because a parametrization over a glob would have generated **zero** ids; and every intended-exit-2 subprocess test asserts a frozen contract string as well as the code. The purity test needed `pytest.MonkeyPatch.context()` rather than the fixture, whose teardown-time revert left `Path.exists` poisoned while pytest rendered the traceback. **Phase 3 (2026-08-15)** authored the seven `movelink-*` trees — `-incoming`, `-moved-referrer`, `-both`, `-archived-referrer`, `-nested`, `-strand`, `-closeout` — each `docs check`-clean as committed, **no** existing fixture edited (`git status`: exactly seven new directories), the two directory-derived sweeps growing 29 → 36 and 33 → 40, and a read-only prototype of the Phase-1 contract over the **shipped** M27 scanner reproducing every expectation Phase 2 asserts, hand-computed line numbers included. It also caught two Phase-2 tests the fixtures made observable: one was GREEN for the wrong reason (no `Revision:` appears today because no body-link write happens at all) and one RED for the wrong reason (the fixture ships without an `INDEX.md`, which the first move generates). **Phase 4 (2026-08-15)** captured the classified RED baseline — **1332 collected, 229 failed, 1103 passed** after the Step-1 audit and the fresh-eyes fold-in — zero collection errors, zero xfail/xpass, zero warnings, exactly **two** exception classes (193 `AttributeError`, 36 `AssertionError`) after three `KeyError: 'strands'` RED reasons were replaced with explicit key-presence assertions, every RED in a named family with a Phase-5/6/7 landing point, every GREEN-at-baseline lock classified with `test_mv_oserror_mid_rewrite_exits_2` marked **transitional**, and all **1087** pre-existing ids mechanically proven present against `58955ef` with **0** removed and **0** deleted test lines, and exactly one pre-existing id deliberately RED (`test_mv_help`, strengthened by operator decision so Phase 7's argparse half is a lock). The **fresh-eyes review returned no blockers**; its five should-fix items and three nits are folded in — the largest being **amendment 4**, narrowing Q4's "already broken" clause to "already escaping" because its literal wording is unimplementable in a planner that never stats, and a Phase-6 implementer reading only `cli.md` would have implemented the opposite of the pinned behaviour — and the operator **closed the colon encode residual here** rather than deferring it, because the emitted token would re-classify as `scheme`, M27 would stop validating it, and `docs check` would never report the link the move just killed: item (C) now states the renderer post-condition `classify_destination(new_raw) == "local"` with a complete proof. M26's false-positive trap was hit for real and recorded: `grep -c INTERNALERROR` over a `--tb=long` run returns 1, and the single match is a test docstring printed as source context. No product code was touched across Phases 1–4, by design. **Step 2 (Phases 5–10, 2026-08-15 on `m28/phases-5-10`)** landed it. **Phase 5** added `MOVE_STRAND_KINDS`, the four frozen records and the seven pure functions of item (L) as **three pure insertions** into `cli.py` with `_cmd_mv` / `_cmd_archive` byte-identical, taking the pure seam to 194/194 and the `AttributeError` class to **zero** while the CLI locks stayed honestly RED. **Phase 6** inverted `_cmd_mv` to plan-before-move with R9's partial-state admission, added `docs archive`'s steps 5b / 8b / 8c / 8d, threaded each moving member's planned text into `_archive_one` (`apply_archive_plan(texts=…)`) so the contract stays at **one `atomic_write` per document, never two**, lifted `preview only` into the verb so a preview ends on it, and **deleted** `_rewrite_referring_edges` — superseded by `apply_move_plan`, whose M18 archived-doc gate is unnecessary *by construction* because an archived document's text now changes iff a `Related:` target or a body-link destination resolved into the move set, which is exactly rule (G). **Phase 7** reconciled every parallel surface: both argparse descriptions, the bundled `SKILL.md` and `references/use-cases.md` — whose *"prose markdown links in bodies are not rewritten — that's a deliberate scope cut"* line was **false as of Phase 6** — the `UNRELEASED` CHANGELOG with a three-part upgrade note naming the two re-spelled `docs mv` stderr lines that no test pins and that therefore break **silently** for stderr parsers, and a dated resolution bullet on `feedback-log.md`'s issue #1 entry answering findings 1 and 4 so the trail is closed rather than absorbed. Two test expected-values changed, both **strengthenings** and both named in the log with their justification: `archive --json`'s closed top-level key set went from **eight keys to ten** (item (K) forbids omitting an empty array, so ten is the only honest pin), and the primary-only record lock was re-pointed at a tree whose primary has no live `child-of` children — the tree it left now correctly **refuses**, and that scenario gained its own lock, `test_archive_primary_only_leg_1_refuses_on_a_live_child`, on an M26-era tree with no body links, which also proves leg 1 does not depend on the `movelink-*` family. **Phase 8** took the whole gate GREEN at **1333 collected / 1333 passed**, zero xfail/xpass/error, and proved mechanically against `58955ef` that **0** ids were removed, 246 added, and all 1087 pre-existing ids are present and GREEN, with exactly **11** deleted test lines — all inside the one re-pointed lock, stated explicitly rather than reported as "0 test lines changed", because an unexplained test edit inside a no-regression claim is what makes such claims worthless. **Phase 9** dogfooded **nine** flows on throwaway copies with the live tree never written to and the "before" column **measured** by running the pre-M28 `cli.py` from a throwaway worktree against a copy of the same tree: E1's rename went **42 → 0** with a 77-line diff in which *every* changed line names the moved document; E2's single archive **13 → 0** including its four archived referrers; E3's real closeout **6 → 0**; plan A — the E7 census invocation — **completed** with 0 orphans and its leg-2 report naming exactly **16** still-active inbound references (8 `Related:` + 8 body links from 7 referrers), reproducing the census; plans B and C **refused** at exit 2 with empty stdout and an unchanged tree SHA-256, while plan B's preview reported the identical verdict at exit 0 with a populated record; the refusal survived `--quiet` (7 lines, all refusal); a there-and-back move left every file **byte-identical**, `INDEX.md` included; and both verbs' preview and apply records differ in exactly `['applied', 'dry_run', 'index_refreshed']`. Added runtime over this 73-document / 3.1 MB tree: **+80 ms** on a move, **+113 ms** on a solo archive, +121 ms on a preview that now walks where 1.x printed one line. Plan B yielded **5** orphans rather than the census's 6, correctly: its primary is itself a `child-of: plan.md` declarer and item (H) exempts plan members — plan C, where only `plan.md` moves, yields the full 6. **Phase 10** ran `/simplify` (net **−18 lines**: one duplicated `except` clause collapsed into one by moving the detail/published derivation next to the message it produces, `_mv_member_changes` folded into a single lookup, `archive_plan_to_json` restored to one dict literal with a `**` splice, and the two adjacent post-move `try` blocks merged since both fail identically — the `_refresh_index` handler stays separate because it is the one post-write failure that still emits a record) and closed `architecture.md` (a *Move-safe body-link rewrites (M28)* subsection, the archive pipeline diagram re-drawn through `apply_move_plan`, and a new `mv` pipeline), `test-strategy.md` (the `movelink-*` family and two critical-path rows), `plan.md` and this file. No version bump (M25 — D6); M28 stays `Lifecycle: active` until the M29 publish closeout. A **Step-2 same-instance audit** — three passes: code against contract, documents against each other and against measured ground truth, and an adversarial pass reproducing every contract claim on throwaway trees — then found **sixteen** issues and fixed all sixteen. The four that matter most: `convention.md` still carried Q4's PRE-amendment wording — that an already-**broken** destination is byte-identical after a move — which amendment 4 reversed and which the pinned planner test contradicts, and which matters because `convention.md` ships byte-identically inside the wheel (the amendment named `cli.md` and *Out of scope* but not `convention.md`, so it slipped); two shipped `docs mv` behaviours were undocumented (an unreadable document in the plan walk, and the INDEX-refresh failure's new message, record and exit); and **two locks the Step-2 resolutions explicitly required had shipped as promises** — `--quiet` over a PREVIEW whose plan has orphans (the only place item (L)'s report-vs-refusal split is observable) and `docs mv`'s INDEX-refresh record. Both new locks were **mutation-tested**: reverting the code to the shape each forbids fails that id and leaves every other test green. The renderer's two post-conditions and the never-creates-an-escape invariant were additionally **fuzzed** — 60,000 and 18,646 cases, zero failures over the reachable domain. Its largest single find was a **false claim in `cli.md`** — that a move never rewrites 4-space-indented code, which the same file has contradicted since M27 and which was reproduced live: D2's RULE was implemented exactly right, its ENUMERATION was wrong, and `cli.md` ships byte-identically inside the wheel, so an agent was being told a code sample is safe from a move that silently edits it (corrected in both places and recorded as **amendment 5**). It also pruned the directory a failed `docs mv` rename could leave behind while admitting it had moved nothing, normalised and pinned two undocumented refusal strings, and gave the overlap proof its first real witness — the test named after it could not reach it, because (F)'s order trips span-match first. One item is **surfaced, not implemented**: `docs archive` has no partial-state admission for its rewrite phase, now *Follow-ups* item 8. Final suite after the audit: **1338 passed / 0 failed**. A **fresh-eyes review** then returned **no blockers on the product code** — it re-ran the gate, reproduced the no-regression proof, and swept the pure seam exhaustively for zero contract violations — but eight findings, all folded in. The largest, by **operator decision**, closed the one item the audit had surfaced rather than fixed: `docs archive` now emits a **partial-state admission for its REWRITE phase** too (amendment 7 to item (J)), so both verbs behave the same and three shipped promises — `cli.md`'s *Residual boundary*, its *Validate-all-first* section (which opens "governs **both**" verbs), and the milestone's verb-agnostic success criterion — become true as written instead of false in a file that ships inside the wheel. Also by operator decision: `preview only — nothing was written` now closes **every** preview, not only a cascade one, because M26's "one line needs no disclaimer" rationale died when the block grew; and the unconditional zero footer **stays**, now pinned together with leg 2's deliberately conditional count line. The review also found the plan-B census number stale in four BINDING passages (**amendment 6**: plan B measures 5, not 6, because item (H) exempts its own primary — the code was right), and a **dead link on the project's front page** (`README.md` → `blob/main/docs/m8-adoption-workflow.md`, archived since M8), fixed here because shipping a 2.0.0 whose README carries a dead documentation link would be self-refuting in the milestone whose subject is link integrity. Final suite: **1341 passed / 0 failed**. A **second `/simplify` pass** on `m28/simplify` then re-read the whole M28 surface as the audit and the fold-in had left it and made three behaviour-preserving collapses (net **−11 lines**: a nested renderer call lifted out of a `LinkRewrite(…)` argument list the formatter had exploded across seven lines, a pure dict comprehension hoisted out of archive step 9a's `try` so the guarded block is the one call it guards, and `docs mv`'s admission computed before it is printed instead of concatenated inside the `print`). Four candidates were considered and **rejected with reasons** — chiefly a shared `_planned_writes` helper, which is net-zero on lines and moves a rule out of the two message-renderers whose whole value is that each clause is checkable where it is read — and Phase 10's archive `try`-block merge was deliberately **not** re-made, because F1's rewrite-phase admission means the two phases no longer fail identically. Suite unchanged at 1341. | [Plan](m28-move-safe-body-link-rewrites.md) | [Log](m28-move-safe-body-link-rewrites-impl.md) |
| M28a — Structured archive-date witness | **Active / Step 1 (Phases 1–4) complete** (setup 2026-08-15 on `m28a/milestone-setup`; **Phase 1 — Define Contract** 2026-08-15 and **Phases 2–4 — RED tests, fixtures, classified baseline** 2026-08-16 on `m28a/phases-1-4`, Phase 5 next; 1502 collected, 71 RED / 90 GREEN; **all seven setup questions RESOLVED** — Q4 operator, Q1 auto, Q2/Q3/Q5/Q6/Q7 conductor — and the contract frozen in *Decisions (Phase 1 — BINDING)* items (A)–(H) with six amendments and nine Step-1 resolutions OQ-1 … OQ-9, OQ-7 an operator decision; depends on M26) — promoted from issue #1 finding 3, the issue's last open item. **Two legs.** Leg 1 (detect): `docs archive` records the archive date as a structured **`Archived:`** field (Q1, binding and permanent — the convention never renames a built-in; `Archived-date:` rejected because `Updated:` already establishes that a date field here does not name its own type) written to **every** document the operation moves — deliberately **not** `Archived-reason:`'s primary-only rule (**A2**), because the reported case was a cascaded trio split across two dated directories and only 13 of this tree's 46 archived documents carry a reason line (E4). `docs check` gains one rule, `archive-date-drift`: a **corroboration test** decided by path arithmetic alone — the first segment under the configured archive dir must parse, in the tree's `date_format`, to the recorded date — hard error, exit 2, one finding per document, closed four-key `Finding` record, no new flag, no new JSON key, no opt-out. It fires **only when the field is present**, so all 46 of this tree's archived documents and every pre-2.0 archived document anywhere stay silent and a 1.x tree gains **zero** findings on upgrade; that present-only contract is the whole compatibility story and is what lets the rule be an error at all. Setup measured the tree read-only and reproduced the drift on throwaway copies, producing **E1–E9**. **E1** enumerates all four relocation paths and finds **exactly one silent**: `docs archive` refuses an already-archived primary at exit 2, `docs mv` out of and into the archive are both caught by `status-drift`, and `docs mv archive/2026-05-25/m9-pypi-publish.md archive/2026-07-03/m9-pypi-publish.md` completes at **exit 0** with `docs check` clean — which corrects the registered stub's claim that the tool already prevents this (**A1**: true of `docs archive`, false of `docs mv`). **E2** replays that command against pre-M28 `main` (`58955ef`) and merged `main`: **13 `broken-body-link` errors at exit 2 before, 0 findings at exit 0 after** — M28 rebased those destinations exactly as specified and, in the same stroke, removed the tree's only accidental alarm, which is why M28a is a consequence of M28 and lands before the publish. **E3** kills `Updated:` as a candidate witness (29 of 46 differ from their directory after the M27 — D6 migration; `docs touch` bumps it again at exit 0). **E5** gives the decline a number: the reporter's suggested `pairs-with` rule would emit **7** findings on this correct tree. **E6–E9** settle the rest — the label is unused anywhere, there is no rule registry and no field-order rule (so the block position must be pinned), the only dated-directory parser is config-blind and lives in the migrate half, a non-default `date_format` tree already breaks on a pre-existing hardcoded-ISO parse (so comparison is on **parsed dates**), and `docs migrate` derives its archive dates from `Updated:` or **mtime** — today, on a fresh clone — so migrate must never write the witness and a foreign `Archived:` line stays demoted to `Migrated-Archived:`. **Q4 is the operator decision that shaped the milestone: adopt BOTH legs.** Leg 2 (prevent) is **D5** — `docs mv` refuses when source and destination are both under the configured archive dir and their first segments parse, in the tree's `date_format`, to **different** dates. Path arithmetic only; evaluated in the plan-before-move, refuse-with-zero-mutation window **M28 already built** — Phase-1 amendment 2 places it one step earlier, immediately after the two root-relative paths are derived and **before** the `--dry-run` branch, so a preview cannot promise a move the apply refuses — and no second refusal mechanism is invented; exit 2, both dates named, **zero bytes written**; no flag, no JSON key, no opt-out. It is deliberately independent of whether the moving document carries the witness, which is how it reaches the 46 documents archived before the field existed and every tree upgrading from 1.x. **Four** neighbours are enumerated as **permitted** so the predicate cannot creep (Phase-1 amendment 6) — a rename within one dated directory, a move `status-drift` already catches, a move whose two segments do not both parse, and two spellings of one date — and the by-hand escape for a genuinely mis-dated archive (move, correct the field, re-check) ships in the **same paragraph** as the refusal in both `cli.md` and `convention.md`. Rejected: witness-only (leaves the pre-2.0 population unprotected) and a refusal conditioned on the witness being present (depends on the very field whose absence is the problem). Consequence: the residual narrows to **two** named cases (Phase-1 amendment 1) — a hand-made relocation of a pre-2.0 document, and the tool-driven relocation *out of* a dated directory that is not cross-dated (`docs mv archive/<D>/x.md archive/x.md`), which stays a permitted neighbour by **operator decision (OQ-7)** because refusing it would also refuse a legitimate reorganisation of the archive subtree; Leg 1 reaches the witness-carrying half of it and *Follow-ups* item 7 carries the rest. D5's refusal is M28a's single behaviour change. Setup also registered in `feedback-log.md` the one defect it found and deliberately did **not** fix (E8's hardcoded-ISO `Updated:` parse); M28a's comparison parses both sides with `config.date_format` so it cannot inherit it. No version bump (M25 — D6). | [Plan](m28a-archive-date-witness.md) | [Log](m28a-archive-date-witness-impl.md) |
| M29 — PyPI publish 2.0.0 | **Registered release stub** (2026-08-10; depends on M25–M28a; no log/runbook phase started). | [Plan](m29-pypi-publish-2-0-0.md) | _not yet created_ |

v1 (M1-M5) shipped 2026-05-22. **docs-cli 1.3.0 shipped
2026-05-25** as the first public PyPI release — M6 (PyPI
distribution preparation), M7 (migration accuracy — breaking
`Status:` → `Lifecycle:` rename + inference broadening), M8
(adoption workflow — `--exclude` tree-wide, triage flags,
`docs new --body-from`, skill-reference rewrite for adoption)
all complete locally over 2026-05-24 to 2026-05-25; M9 (the
operator-driven publish) shipped them together as one batched
PyPI release on 2026-05-25, closing the M6 → M9 backlog
grouping internally tracked as "v1.1". The CLI is now installable via `pip install
docs-cli` on any Python 3.11+ host.

## TDD phase order (used per milestone)

1. Define Contract
2. Write Tests (RED)
3. Create Data/Fixtures
4. Run Tests (RED Baseline)
5. Update Base Interfaces
6. Implement Offline/Core Path
7. Update Tool/Wrapper Layer
8. Run Tests (GREEN)
9. Implement Online/Integration (mapped to dogfooding pass when no network surface)
10. Quality, Docs, Refactor

## Quick links

- [Charter](charter.md) — what + why
- [Convention spec](convention.md) — on-disk format
- [CLI spec](cli.md) — command surface
- [Architecture](architecture.md) — module sketch + dev setup commands
- [Plan](plan.md) — milestone roadmap (v1 + v1.1)
- [Definition of Ready](definition-of-ready.md) — gate to start

## Resuming this work (fresh session)

If you're starting a new Claude Code session against this repo:

**Reading order** (≤ 10 minutes):
1. `~/CLAUDE.md` — host-level guidance + memory pointers
2. `docs/status.md` — this file
3. `docs/plan.md` — the roadmap; v1 (M1-M5) shipped, v1.1 in
   flight (M6 merged + publish-pending; M7+M8 stub-drafted).
4. `docs/m6-pypi-distribution.md` — M6 task plan; "Decisions"
   records the five milestone-setup OQs resolved 2026-05-23.
5. `docs/m6-pypi-distribution-log.md` — M6 log with the per-phase
   status table.
6. `docs/m7-migration-accuracy.md` — M7 stub: the breaking
   `Status:` → `Lifecycle:` rename and inference broadening
   (findings F0–F12 from the 2026-05-24 trial).
7. `docs/m8-adoption-workflow.md` — M8 stub: the agent + operator
   ergonomics (tree-wide `--exclude`, triage flags,
   `docs new --body-from`, skill-reference rewrite).
7a. `docs/m9-pypi-publish.md` + `docs/release-runbook.md` — M9
   shipped 2026-05-25 as `docs-cli==1.3.0`; the milestone-
   completion summary in `m9-pypi-publish.md` is the canonical
   record of what shipped + deviations; the runbook is the
   operative reference for future releases.
8. `docs/cli.md` — the command spec; the full eight-verb `docs`
   surface.
9. `docs/convention.md`, `docs/architecture.md` — the on-disk
   format and the module sketch.
10. `docs/m5-claude-code-skill.md` — v1's final milestone; its
    **Milestone-completion summary** describes the skill that
    M6's `install-skill` verb delivers via the wheel.
11. `src/docs_cli/skill/SKILL.md` — the bundled skill (relocated
    under the package source at M6 Phase 5).
12. `docs/charter.md` — what + why.
13. `docs/definition-of-ready.md` — the gate cleared before
    implementation.

**Verify environment** before doing any work:
```sh
cd ~/opt/docs-cli
.venv/bin/python -m pytest tests/ -q          # 433 passed (current suite, as of 1.5.0 / M13)
.venv/bin/ruff check .                        # All checks passed!
.venv/bin/ruff format --check .               # all files formatted
.venv/bin/mypy                                # Success (tree-wide)
.venv/bin/docs check docs/                    # dogfood — exit 0
.venv/bin/docs index --root docs/ --dry-run   # smoke: idempotent dogfood
```
If `.venv/` is missing (fresh clone) or `.venv/bin/docs` is absent:
```sh
rm -rf .venv && python3 -m venv .venv         # needs python3-venv on Debian/Ubuntu
.venv/bin/pip install -e ".[dev]"             # lands `docs` on PATH via the entry point
```

**Next action:** none scoped — **M12 shipped to PyPI as
`docs-cli==1.5.0` via M13 on 2026-05-29** (M12 built the four
features locally; M13 published them, mirroring M11 → M10).
Both milestones are Complete. The next implementation
milestone (M14) is unscoped; pick it up via
`create-milestones` / `/ship-milestone next milestone`. The
authoritative current state lives in the "Current milestone"
and top "Next action" sections above; this resume-snapshot
block is historical.

**docs-cli 1.4.0 shipped 2026-05-27** as M11 — the
operator-driven publish milestone for the M10-built artefacts,
mirroring M9's relationship to M8. PyPI:
https://pypi.org/project/docs-cli/1.4.0/; source:
https://github.com/ArtRichards/docs-cli/releases/tag/v1.4.0;
`v1.4.0` annotated tag at the M11 Phase 4 commit. M11 ran the
[release-runbook.md](release-runbook.md) end-to-end:
operator-state inventory → fresh artefact build → TestPyPI
rehearsal under `docs-cli-rehearsal==1.4.0` (squatter detour
continues) → real PyPI upload → chain-of-custody verified
bit-perfect → smoke + M10 headline contract against the
PyPI-served wheel → tag + GitHub release → doc closeouts.
Full publish record + deviations in
[m11-pypi-publish.md](archive/2026-05-27/m11-pypi-publish.md)'s
milestone-completion summary.

**docs-cli 1.3.0 shipped 2026-05-25** — one batched PyPI
publish covering the M6 + M7 + M8 surface per the operator's
OQ-C split, closing the M6 → M9 backlog grouping internally
tracked as "v1.1". PyPI:
https://pypi.org/project/docs-cli/1.3.0/; source:
https://github.com/ArtRichards/docs-cli/releases/tag/v1.3.0;
GitHub repo public; `v1.3.0` lightweight tag at the M8 simplify
commit. Intermediate versions `1.1.0` and `1.2.0` never reached
PyPI (no prior public release existed; no continuity to
preserve). Full publish record + deviations recorded for
future releases in
[m9-pypi-publish.md](archive/2026-05-25/m9-pypi-publish.md)'s milestone-completion
summary. The [release-runbook.md](release-runbook.md) stays
the operative reference for the next release (v1.5+).

**M7 Phases 1-4 complete (2026-05-24; review-tightening 2026-05-25):**
task plan promoted to active, OQ A–D recorded as Decisions, log +
per-phase entries written, 44 new test items authored at Phase 2
(34 RED + 10 GREEN-at-baseline regression locks), sanitised
fixtures staged at
`tests/fixtures/{lifecycle,status-prose,project-names,sibling-defaulting}/`
+ `tests/fixtures/trees/real-trees/{kebab-tiny,snake-medium,snake-large,archive-subdir,mixed-naming}/`,
RED baseline captured at `/tmp/m7-phase-4-baseline.txt`
(34 failed, 281 passed; M6's 271 GREEN preserved + 10 new
regression locks). **Fresh-eyes review 2026-05-25** added 5
contract anchors (strict-medium pinning + parametric expansion
of status-prose preservation + `FileMigration(confidence="medium")`
constructor + `docs check` exit-1 medium anchor) for a post-fix
count of **39 RED + 281 passed (320 collected)**; M6's 271 still
GREEN. Quality gate clean tree-wide.

**M7 Phase 5 complete (2026-05-25):** the F0 controlled-vocab
rename landed across parser, dataclasses, writers, validators,
JSON serialisers, the `.docs.toml` reader, and argparse.
`Doc.lifecycle`, `FileMigration.lifecycle`, `Config.lifecycles`,
`validate_lifecycle`, `add_lifecycles` (TOML), `Lifecycle:` in
the on-disk block. `FileMigration.confidence` extended to
`high|medium|low`. `MigrationPlan` grows the
`project_original` + `multi_project_hints` fields with safe
defaults (populated at Phase 6). `Config` grows
`role_suffixes` + `project_name`. argparse:
`docs list --lifecycle` and `docs migrate --config-project NAME`.
29 docs/*.md files swept, 31 conformant fixture files swept,
existing-test fabrications updated. Skill refs resynced.
pytest: **290 passed, 30 failed (320 collected)** — every
failure on the Phase-6 surface (inference broadening,
project normalisation, per-file mtime archive, multi-project
hints, medium-confidence check wiring, snake-medium fixture
high+medium ratio). Quality gate clean.

**M7 Phase 6 complete (2026-05-25):** F1 / F10 / F11 / F12 /
F4 / F5 all landed. `infer_role` now does word-boundary +
case-transition splitting, recognises the 7 new core vocab
roles + `_M\d+` milestone pattern + `_v\d+`/`_Draft`/`_Ready`
strip with medium confidence. `normalise_project_name()`
produces lowercase-kebab and `plan_migration` honours CLI
> sidecar > inferred precedence with the `(normalised from
"X")` annotation. Per-file mtime drives archive moves when
`--date` is absent. Multi-project hints surface in the plan
footer. `check_doc` emits `medium-confidence-inference`
warnings (exit 1) when a missing `Role:` is resolvable via
H1 or section pattern. `.docs.toml` refusal narrowed so a
`[migrate]`-only sidecar is readable. **pytest: 320 / 320
GREEN.** Quality gate clean.

**M7 Phase 7 complete (2026-05-25):** convention.md, cli.md,
architecture.md, status.md, README.md, CHANGELOG.md all
updated to document M7's surface. New CHANGELOG entry
`## 1.2.0 — UNRELEASED` lists every breaking + additive
change (F0 rename, --lifecycle flag, JSON schema field
rename, add_lifecycles, 7 new core roles, medium
confidence, F11 normalisation, F4 per-file mtime, F5 hints,
--config-project, [migrate] sidecar). architecture.md gets
a new `config` module section. pyproject.toml +
`__version__` bumped to 1.2.0; `docs --version` prints
`docs 1.2.0`. Bundled skill refs resynced via byte-copy
(test_skill_refs.py GREEN). docs/INDEX.md regenerated;
fixture snapshot byte-equal. pytest: 320 / 320 GREEN.
Quality gate clean tree-wide.

**M7 Phase 8 complete (2026-05-25):** verbatim quality gate
captured at `/tmp/m7-phase-8-green.txt`. pytest 320 / 320
GREEN; ruff / format / mypy / docs check / docs index
--dry-run all clean; `docs --version` prints `docs 1.2.0`.

**M7 Phase 9 complete (2026-05-25):** all 5 quantitative
success criteria PASS. high+medium = 88.0% (103/117) ≥ 50%;
notes = 13.7% (16/117) ≤ 30%; free-form Status: preservation
= 4/4 = 100%; archive-subdir archive_move = 5/5 = 100% ≥ 80%;
project normalisation = 3/3 = 100% ≥ 90%.
`tests/manual/m7_success_criteria.py` aggregates; per-fixture
JSON dumps at `/tmp/m7-phase-9/*.json`.

**M7 Phase 10 complete (2026-05-25)**: milestone-completion
summary appended to `m7-migration-accuracy.md`; M7 row in
this file flipped to Complete; CHANGELOG `## 1.2.0 —
UNRELEASED` dated; local dist artefacts produced via
`python -m build` and verified with `twine check` (NO upload,
NO tag, NO GitHub release). M7 is ship-ready locally; the
public PyPI release ships as v1.3.0 batched with M6 + M8 at
the M9 milestone per the operator OQ-C split.

**M8 shipped locally as 1.3.0** (2026-05-25). All 10 TDD
phases complete; Phase 9 fresh-subagent gate **PASSED 3/3
unattended** on real fresh Opus subagents (operator-directed
re-run after the implementation agent's same-instance dogfood
substitution; both stages documented in the Phase 9 log).
Surface delivered: F3
(tree-wide `--exclude` + `[exclude]` + `.docsignore`), F6
(triage flags + default footer summary), F7 (non-md sibling
surfacing), F8 (substantial skill rewrite + adoption playbook
+ `.docs.toml` template), F9 (`docs new --body-from`). Tests:
**369 GREEN** (324 M7 + 45 new M8 items). Quality gate clean.
Local artefacts: `dist/docs_cli-1.3.0-py3-none-any.whl` +
`dist/docs_cli-1.3.0.tar.gz`; `twine check` PASSED on both.
**NO publish, NO tag, NO GitHub release** — per OQ-C the
publish is M9's scope.

**M8 Phases 1-4 complete (2026-05-25):** task plan promoted to
active and OQ A–G recorded as Decisions at milestone-setup; log +
per-phase Phase 1-4 entries written; 31 new test functions / 45
new collected items authored at Phase 2 across 5 new test files
+ 1 added test in `test_migrate.py`; new sanitised fixtures
staged at `tests/fixtures/body-from/` (3 files; the
`.docsignore` syntax cases and `[exclude]`-bearing trees are
written inline via `tmp_path` in the Phase 2 tests
themselves);
RED baseline captured at `/tmp/m8-phase-4-baseline.txt`
(**41 failed, 328 passed; 369 collected total** — M7's 324
GREEN preserved + 4 new baseline-GREEN regression locks + 41 RED
for intended reasons; the initial 40+5 baseline tightened to
41+4 in the fresh-eyes audit pass, which converted two weak
locks into proper REDs). Quality gate clean tree-wide.

**Watch out for** (durable gotchas, still current):
- The CLI module lives at `src/docs_cli/cli.py`. After Phase 6's
  editable install (`pip install -e ".[dev]"`), the `docs` command
  lands on PATH via the `[project.scripts]` entry-point — same binary
  the PyPI user gets. (Pre-Phase-6, invoke as
  `.venv/bin/python -m docs_cli.cli …`.)
- Quality gates run **tree-wide**: `ruff check .`, `ruff format --check .`, and `mypy` (no args — `pyproject.toml` scopes it to `src/` + `tests/`). Commit once per TDD phase on the active branch.
- The dogfood snapshot (`tests/fixtures/expected/docs-INDEX.md`) is spec-compliant, not hand-authored. If you change a `docs/*.md` body so its first paragraph or `Updated:` line changes, regenerate `docs/INDEX.md` and the snapshot in lockstep (`docs index --root docs`, then copy `docs/INDEX.md` onto the fixture). Editing a doc means bumping that doc's own `Updated:` per the convention.
- `docs mv` rewrites `Related:` metadata bullets only — prose markdown links in bodies are deliberately left alone (see the M2 Phase 9 log). `docs check` likewise validates `Related:` paths, not prose links.
- `docs check`'s `malformed` rule covers a **missing H1 only** — `parse_metadata_block` ends the metadata block at the first non-label line rather than raising, so a malformed in-block line is not separately detectable (M3 Phase 5 decision).
- INDEX markers quoted in a doc's preamble must be backtick-styled inline code, so the line-anchored detector (`_find_marker_lines`) does not false-match them.
- The metadata block may contain one blank line between the inline `Label: value` run and a trailing bare-label group (`Related:` + bullets). `_metadata_line_span` in `src/docs_cli/cli.py` is the single source of that block-boundary rule.
- Git author email for this repo is `art@bitholdersinc.com` (locally configured), not the `art@trucktech.in` default from `~/CLAUDE.md`.
- M7 (v1.2.0) renames the controlled-vocab field from `Status:` to `Lifecycle:` on disk — breaking, no backward-compat alias. References to `Status:` inside M1-M5 historical log narrative are deliberately preserved verbatim (the field-name swap is the only on-disk change). Bundled skill references at `src/docs_cli/skill/references/` must be resynced from `docs/{convention,cli}.md` in lockstep — `tests/test_skill_refs.py` enforces byte-equality.
