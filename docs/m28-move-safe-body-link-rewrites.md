# M28 — Move-safe Markdown body-link rewrites

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-08-15

Related:
- child-of: plan.md
- parent-of: m28-move-safe-body-link-rewrites-impl.md
- implements: charter.md
- pairs-with: m28-move-safe-body-link-rewrites-impl.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: test-strategy.md
- pairs-with: status.md
- references: feedback-log.md
- follows: m27-markdown-body-link-validation.md
- depends-on: m26-safe-archive-selection.md
- depends-on: m27-markdown-body-link-validation.md
- required-by: m29-pypi-publish-2-0-0.md
- precedes: m28a-archive-date-witness.md

## Overview

- Milestone: M28 (v2.0 train)
- Title: Move-safe Markdown body-link rewrites
- Surface: extend `docs mv` and `docs archive` to rebase only the parsed local
  Markdown destination tokens a coordinated move makes stale, and to refuse a
  move whose *consequences* are provably wrong. M27 supplies the validated
  scanner and the destination spans; M26 supplies the operation plan; M28
  supplies mutation, the pre-move plan for `mv`, and the strand-check.
- Progress: **ALL TEN PHASES COMPLETE (2026-08-15) — M28 is
  implementation-complete.** Step 1 (Phases 1–4) landed on `m28/phases-1-4`
  and Step 2 (Phases 5–10) on `m28/phases-5-10`. Phase 5 landed the pure
  planner seam as three insertions into `cli.py` with no verb wired; Phase 6
  inverted `_cmd_mv` to plan-before-move, added `docs archive`'s steps 5b /
  8b / 8c / 8d, threaded each moving member's planned text into `_archive_one`
  so the contract stays at one write per document, and **deleted**
  `_rewrite_referring_edges`; Phase 7 reconciled every parallel surface;
  Phase 8 proved the gate at **1333 passed** with **0** test ids removed
  against the pre-M28 commit; Phase 9 dogfooded nine flows on throwaway
  copies — E1's 42 findings, E2's 13 and E3's 6 all went to **0**, plan A
  completed with its leg-2 report naming exactly the 16 references the setup
  census measured, plans B and C refused with zero bytes, and a there-and-back
  move left the tree byte-identical; Phase 10 ran `/simplify` (net −18 lines,
  four collapses) and closed `architecture.md`, `test-strategy.md`, `plan.md`
  and `status.md`. The full record is in the implementation log. What follows
  is the setup and Phase-1 record, unchanged. The whole machine-facing contract is frozen in
  *Decisions (Phase 1 — BINDING)* below — the rewrite formula and its BINDING
  step order, the emitted spelling and both encode sets, the no-op rule, the
  never-creates-an-escape proof, the write pipeline, the pre-flight, the
  archived-referrer rule, both strand legs, both verbs' check orders, the
  message catalogue, both `--json` schemas and the Phase-5 signatures — with
  three **amendments to setup-frozen material** and eleven **Step-1
  resolutions** recorded in place. The author-facing halves landed in
  `cli.md` › *Move-safe body-link rewrites (M28 — D1–D7)* / *`docs mv`* and
  `convention.md` › *Body links (M27)* / *Archive subtree*. Phase 2 then wrote
  **182 new test ids** — a new pure-planner module `tests/test_move_links.py`
  (153) plus appended CLI, check and skill locks (29) — leaving the suite at
  **1269 collected, 181 failed, 1088 passed**: every one of the 1087
  pre-existing ids still present and GREEN, zero collection errors, and zero
  deleted or altered test lines. Phase 3 then authored the **seven
  `movelink-*` fixture trees** — every one `docs check`-clean as committed,
  every existing fixture byte-identical — sweeping the two directory-derived
  parametrizations from 29 to 36 and from 33 to 40 and taking the suite to
  **1283 collected, 180 failed, 1103 passed**. A read-only prototype census
  under the Phase-1 contract confirmed each tree yields exactly its intended
  plan, line numbers included. Phase 4 captured the baseline: **1332
  collected, 229 failed, 1103 passed** (restated after the Step-1
  same-instance audit, its adversarial second pass, and the fresh-eyes
  fold-in), zero collection errors, zero xfail / xpass, exactly **two**
  exception classes (193 `AttributeError` from the pure seam, 36
  `AssertionError` from the CLI and skill locks), and a mechanical proof
  against the pre-M28 commit that **0** test ids were removed, **0** test lines
  were deleted, and exactly **one** pre-existing id is RED — `test_mv_help`,
  strengthened by operator decision so that Phase 7's argparse half is a lock
  rather than a promise. The fresh-eyes review returned **no blockers**; its
  five should-fix items and three nits are folded in, the largest being
  **amendment 4**, which narrows Q4's "already broken" clause to "already
  escaping" because its literal wording is unimplementable in a planner that
  never stats. The operator also **closed the colon residual here** rather than
  deferring it: item (C) now carries the renderer post-condition
  `classify_destination(new_raw) == "local"`. No product code changed in any of
  the four phases — `git diff --stat 58955ef -- src/docs_cli/cli.py` is empty
  by design. What follows is the setup record, unchanged. M27 is
  implementation-complete
  and merged to `main` (`58955ef`), so M28 is the next implementation
  milestone in the v2.0 train. Setup measured this repository read-only and on
  throwaway copies and produced eight pieces of evidence (**E1–E8**), the
  headline being that **`docs mv` and `docs archive` now produce trees that
  fail the tool's own `docs check`**: one ordinary
  `docs archive m17-pypi-publish-impl.md` exits 0 and leaves **13**
  `broken-body-link` errors, and one `docs mv plan.md milestone-plan.md`
  rewrites 35 `Related:` bullets and leaves **42**. **All seven setup
  questions are RESOLVED** — Q1, Q2 and Q3 by the operator; Q4, Q5, Q6 and Q7
  conductor-resolved — and are recorded in *Resolved setup questions
  (Q1–Q7, BINDING)* below. **Q1 amends the 2026-08-15 routing entry**: the
  routed strand-check predicate was measured against this repository and
  refuses its own standard milestone closeout, so the refusal is narrowed to
  the `child-of` direction and every other still-active inbound reference is
  **reported** instead. **Q2 supersedes the registered stub's Open question 1
  recommendation.** The three durable decisions those two answers and Q3
  produced are restated in *Decisions recorded at setup (BINDING)* so a
  Phase-1 agent can reconstruct them from this document alone. Phase 1 does
  not re-open any of them.

### Goal

Moving or archiving documents should preserve every supported local Markdown
link automatically, without changing labels, titles, fragments, unrelated
prose, examples, or code — and a move whose consequences the tool can *prove*
wrong should refuse before the first byte moves rather than complete and leave
the operator to discover the damage.

### Primary use-case acceptance

- **Rename safely.** An agent renames a document with `docs mv` and commits a
  focused diff. Incoming links point at the new name, links inside the moved
  document are rebased from its new directory, and `docs check` is clean —
  metadata relationships *and* body navigation both intact.
- **Close out a milestone safely.** An agent archives a completed milestone
  pair with `docs archive FILE --cascade-only GLOB`. The tracker and the plan
  keep pointing at the pair, now at its `archive/YYYY-MM-DD/` path; the pair's
  own outgoing links are rebased two directories deeper; the archived
  referrers that already point at the pair keep resolving; and `docs check`
  exits 0 with one deterministic INDEX refresh.
- **Refuse what is provably wrong.** A move that would strand a still-active
  document — the case issue #1 reported, where a broad glob archives the live
  plan out from under its live children — refuses before any write, names both
  ends, and changes zero bytes.
- **Never rewrite prose.** Plain-text mentions, code samples, external URLs,
  images, raw HTML, titles, and link labels are byte-identical afterwards. A
  destination whose meaning did not change keeps the spelling its author gave
  it.

## Binding scope

The eight decisions below are binding for M28. Each carries the setup question
it resolves; the reasoning for those resolutions is in *Resolved setup
questions (Q1–Q7, BINDING)*, and the three answers that changed something
already written down are restated in *Decisions recorded at setup (BINDING)*.
Phase 1 makes them exact and does not re-open them.

### D1 — Two independent move classes, one formula

A coordinated move breaks local body links in exactly two ways, and both are
in scope:

1. **Incoming** — a link whose *target* moved. The referrer stays where it is;
   its destination must be repointed.
2. **Moved referrer** — a link *inside* a document that itself moved. The
   target did not move; the destination must be rebased from the referrer's
   new directory.

They are independent — a document can suffer both, and a document that moves
while linking to another document moving in the same operation suffers both at
once — but they are **one formula**, not two code paths. For a move set `M`
mapping each moving document's old canonical root-relative path to its new
one, and for each recognised local destination in each walked document `D`:

1. resolve the destination from `D`'s **old** location, giving a canonical
   root-relative target;
2. map that target through `M` when it is a key, leaving it unchanged
   otherwise;
3. relativise the result against `D`'s **new** directory.

Class 1 is the case where step 2 fires; class 2 is the case where `D` itself
is in `M`, so step 3's base differs from step 1's. Nothing else is a case.

**The mapping is by canonical target, not by string.** Every spelling that
normalises to a moving document is rewritten — `plan.md`, `./plan.md`,
`sub/../plan.md` and `../../plan.md` alike — because step 1 normalises before
step 2 looks anything up. This is a real advantage over the `Related:`
rewriter, which matches the declared string exactly and therefore needed
M26 — Q5's per-alias pair list to catch a `./b.md` bullet (D6, E6).

### D2 — M27's scanner, M27's spans, M27's grammar — nothing widened

- **One parser.** `scan_body_links` is the only Markdown reader. M28 adds no
  second matcher, no regex over destinations, and no third-party dependency
  (`architecture.md` pins stdlib-only).
- **The span is the edit.** Each `BodyLink` carries the exact `(start, end)`
  offsets of its **destination token** in the original text. M28 splices a
  replacement into `[start, end)` and copies every other byte. The span
  **includes** a surrounding `<…>` pair and **excludes** any title, so a
  replacement containing a space lands inside the delimiters rather than
  outside them. `text[link.start:link.end] == link.raw` is M27's named
  invariant and M28 is the consumer it was frozen for.
- **Right-to-left within a document.** Splices are applied in descending
  `start` order so earlier offsets stay valid — the exact technique M27's
  Phase-6 live-tree repair used for 140 occurrences across 30 documents, with
  30/30 byte-identical round-trip reconstructions proving no other byte moved.
- **The validated grammar is not widened.** Anything M27 does not validate,
  M28 does not rewrite: images, autolinks, raw HTML, reference *uses*, and
  4-space indented code stay out (M27 — D1/D2, and M27's *Follow-ups* item 1
  stays deferred). Widening the grammar here would silently widen the rewrite
  surface in the same stroke, which is the reason M27 excluded images in the
  first place.
- **Only `local` destinations are ever touched.** `empty`, `fragment`,
  `scheme`, `protocol-relative`, and `root-absolute` destinations are copied
  byte-for-byte, always (Q4).

### D3 — What the tool writes: canonical relative form, everything else preserved

- **The new destination is the `posixpath.relpath` form** of the new target
  against the referrer's new directory — no leading `./`, `..` segments where
  the path really does go up. This is the spelling the tree already uses
  everywhere (`plan.md` from the root, `../../plan.md` from
  `archive/YYYY-MM-DD/`), and it is what M27's repair produced.
- **The fragment is reattached verbatim**, after a single `#`, neither decoded
  nor re-encoded nor validated (M27 — D3; the 2026-08-10 operator decision that
  headings are never checked stands for M28 too).
- **The delimiter form is preserved.** An angle-wrapped destination stays
  angle-wrapped; a plain one stays plain unless the new path contains a
  character the plain form cannot carry, in which case Phase 1 fixes the single
  escape strategy. Titles, labels, and quoting style are outside the span and
  are never touched.
- **A semantically unchanged destination keeps its original bytes** (Q5). If
  step 3 of D1's formula reproduces the destination's existing meaning, the
  token is left exactly as written — no normalisation of `./x.md` to `x.md`, no
  re-spelling of a legitimate `sub/../x.md`. The diff of a move contains only
  destinations the move actually made stale.
- **M28 can never create an `outside-root-body-link`.** Both the old and the
  new target are canonical root-relative paths inside the root, so their
  relative form always normalises back inside the root. Phase 1 states this as
  an invariant with its one-line proof rather than leaving it to be inferred,
  and Phase 2 locks it.

### D4 — Validate-all-first: one rewrite plan before the first byte moves

M26 — D4's shape, extended to `mv` and to body text. The complete rewrite plan
is built and validated **before** any mutation, covering every document the
walk yields:

- every planned splice is computed from text already read, so the plan is a
  pure function of the tree and the move set;
- every document the plan will write is proven parseable and writable;
- no two splices in one document overlap, and every span still matches the
  text it was scanned from;
- the strand-check (D6) runs over the completed plan.

Any **handled** failure refuses the whole operation: non-zero exit, **zero
bytes written**, including the moved document itself. A residual unexpected
`OSError` *during* execution is reported as an exact partial-state admission
naming what was written and what was not, and is **not** rolled back — M26 — D4's
stated boundary, unchanged and not re-litigated here.

**This inverts `docs mv`'s current ordering.** `_cmd_mv` today runs its
pre-flight walk, then `old_path.replace(new_path)`, then the rewrite walk. A
class-2 rewrite needs the moved document's own text and both of its paths, and
an all-or-nothing contract needs the plan complete before the move, so M28
computes the plan first and moves second. The M14 (A1) pre-flight walk and the
M14 (A4) `OSError` mapping stay.

**One write per document.** The `Related:` bullet rewrite and the body-link
splices for the same document are applied to one in-memory text and committed
with a single `atomic_write`. Two passes would double the write count, double
the failure surface, and make a half-written document possible in a way the
current single-pass `_rewrite_referring_edges` avoids.

### D5 — Archived referrers: M18's exception widened along its own axis

Archived documents are walked, validated, and — since M18 — already **written**
by a move: `_rewrite_referring_edges` repoints an archived document's
`Related:` bullet when, and only when, its target is moving in that same
operation. M28's archived-referrer edit is the same trigger, in the same
operation, in the same file write, for the same reason.

- **It is not a fourth exception** (Q2, operator). `convention.md` grants three
  narrow exceptions to archived-document immutability — M18's move-driven edge
  integrity, M25 — D4's audited relationship repair, and M27 — D6's one-time
  body-link migration, which is written as "the last one this convention
  grants". M28 **widens M18's** along its own stated axis, from "`Related:`
  bullets pointing at a document moving in this operation" to "`Related:`
  bullets **and body-link destinations** pointing at a document moving in this
  operation". The move-driven-only qualifier, the byte-identical-otherwise
  guarantee, and the blast radius are M18's, unchanged. Phase 7 must
  **reconcile M27 — D6's "last one this convention grants" sentence** with the
  widened M18 paragraph rather than leave the two contradicting each other:
  M28 grants no new exception, and that sentence has to say so.
- **This is not optional.** E5 measures **131 body links in 27 archived
  documents pointing at active documents**. Since M27 those are hard
  `docs check` errors the moment their target moves, and no verb can repair
  them: `docs archive` and `docs mv` are the only writers that touch archived
  documents, and there is no `docs fix-links`. Declining the archived-referrer
  rewrite would make `docs mv plan.md …` an operation that *cannot* be
  completed cleanly.
- **The edit carries no audit metadata** (Q2, operator, BINDING). **Destination
  tokens only** — no `Updated:` bump, no `Revision:` bullet, M18's shape
  exactly. Same trigger, same operation, same single `atomic_write` as the
  `Related:` half; nothing new is asserted, because the document still points
  at the same target in a different spelling; and an `Updated:` bump would make
  an archived document's date a record of some **other** document's move, and
  would churn `INDEX.md` and the frozen index snapshot on every move.
  **This supersedes the registered stub's Open question 1 recommendation**,
  which proposed M25 — D4's audited shape (bump plus a dated `Revision:`
  naming the move); the superseding argument is recorded in *Resolved setup
  questions* › *Q2* and in *Decisions recorded at setup (BINDING)* so the
  reversal is auditable rather than silent.

### D6 — The post-plan strand-check (`feedback-log.md` issue #1, finding 1)

**Added to M28's scope 2026-08-15**, routed from issue #1's finding 1, whose
residual is a semantics gap rather than a defect against M26 as specified.

The reported harm, reproduced live during setup (E7):
`docs archive m27-markdown-body-link-validation.md --cascade-only '*'` selects
`plan.md`, `cli.md`, `convention.md`, `test-strategy.md` and `status.md` — this
project's entire specification spine — for archiving, at exit 0. M26 made
archive selection *authorized* (an explicit scope is required, and the preview
names everything), but a glob is a syntactic filter that cannot know what it
selects, so the live plan is still reachable through the target's outgoing
`child-of` edge. M26 — Q3 froze the candidate set deliberately and the
reporter's suggested fix — follow *incoming* `child-of` edges — was considered
and declined, because `pairs-with` is symmetric and a live sibling stays
reachable through it.

**Validating the plan's consequences is the direction-agnostic answer**, and it
belongs to M28 because M28 already builds the inbound-reference graph the
predicate needs — over both `Related:` edges and body links, in the same pass,
for the same plan. It does not re-open M26 — Q3: the candidate set stays
exactly as frozen, and the new invariant makes its direction moot.

**The predicate has two legs, and both are binding** (Q1, operator, and an
**amendment to the routing entry** — see *Decisions recorded at setup
(BINDING)* › *A1*). The routing entry's literal wording — *refuse if applying
the plan would leave a still-active document pointing at a newly-archived one* —
was measured against this repository during setup and **refuses this project's
own standard milestone closeout**: a textbook `--cascade-only 'm26-*'` leaves 8
still-active `Related:` edges and 8 still-active body links, from 7 active
referrers, every one of them deliberate (E7, plan A). It is therefore narrowed:

- **Leg 1 — refuse on the `child-of` direction.** The operation refuses when a
  still-active document **outside the plan** declares itself `child-of` a
  document the plan would archive. That is a parent archived out from under its
  live children — the exact reported harm, provable from the graph the plan
  already builds, and measured at **0** occurrences on plan A against **6** on
  both plan B (issue #1's `--cascade-only '*'`) and plan C (archiving `plan.md`
  alone). Exit 2, before any write, naming both ends.
- **Leg 2 — report everything else, refuse nothing.** Every other still-active
  inbound reference into the newly-archived set — any other `Related:` verb
  (`pairs-with`, `precedes` / `follows`, `depends-on` / `required-by`,
  `blocks` / `blocked-by`, and free-form verbs) **and every body link** — is
  named in the preview, in the apply output, and in the machine-readable
  record, without refusing.

**Leg 2 is not decoration.** It is the half that answers issue #1's actual
complaint — that the safety rested on a human reading a preview, and that an
agent generating the glob has the same blind spot a skimming human does — by
delivering the consequences to the caller in a form it can parse. It carries
its own deliverable, its own success criterion, and its own named regression
coverage, exactly as leg 1 does.

Three properties bind both legs:

- **They run over the completed plan, before the first write**, inside D4's
  pre-flight, so a refusal changes zero bytes.
- **They run in the preview too.** `--cascade-dry-run` must show what the write
  would do; M26 — *Follow-ups* item 2 already records that the frozen check
  order lets a preview miss a pre-flight refusal, and repeating that mistake
  for the strand-check would put the safety back on a human reading prose.
  A preview still exits 0 (M26 — D6), including one whose plan leg 1 would
  refuse — the preview reports the verdict rather than adopting it.
- **Both ends are always named** — the still-active document and the document
  it would be left pointing at — in the refusal, in the report, in the preview,
  and in the record.

### D7 — The move is machine-readable, and the answer to `--report-links`

`feedback-log.md` issue #1 finding 4 offers a lighter alternative worth
weighing here and explicitly left unresolved for M28 planning: declare prose
links out of scope in the documentation and ship a `--report-links` mode that
only *lists* inbound prose references to moved files.

**`--report-links` is DECLINED AS A DESIGN, and its OUTPUT is adopted**
(Q3, operator, BINDING — recorded in *Decisions recorded at setup (BINDING)* ›
*A3* so finding 4 is visibly answered rather than dropped). M27 has already
made a broken prose link a hard `docs check` error, so "declare them out of
scope" is no longer available — the tool would knowingly produce a tree that
fails its own gate (E1, E2, E3 measure exactly that). The charter promises that
archiving is one command after which status, location and index are consistent,
and the whole v2.0 train's principle, recorded in the same feedback entry, is
that the tool refuses or repairs what it can prove and asks only about what it
genuinely cannot determine. A *report* leaves the repair to the same agent
whose blind spot produced the problem.

What the reporter actually wanted — visibility before and after — is delivered
as a **plan record** rather than a separate mode, and it is delivered on both
verbs (Q3, operator):

- **`docs mv` gains a real preview and a `--json` rewrite-plan record.**
  `--dry-run` names every planned destination rewrite — document, line, old
  spelling, new spelling — instead of today's single "would move" line, and
  `--json` emits one record. `docs mv` has no machine-readable surface at all
  today, and M28 is about to make it the verb that writes the most bytes.
- **`docs archive --json` gains the same rewrite section plus a `strands`
  array** carrying D6 leg 2's report.
- **One schema, shared by preview and apply**, following M26 — D7's
  operator-approved `archive --json` addition and M25's `relate --json` pattern
  for shape and field-table conventions, so a preview record and an apply
  record stay diffable. M26's *Out of scope* named generalizing the plan record
  to `docs mv` as deliberately not-that-milestone's work; this is that work.

### D8 — Compatibility, upgrade guidance, and surface parity

- **Behaviour-changing, deliberately, and in the safe direction.** `docs mv`
  and `docs archive` start writing prose bytes they never wrote before, and a
  provably-stranding archive starts refusing. Both are v2.0 changes; the
  refusal is designed to be legible and to name both ends.
- **No version bump.** M25 — D6 binds the whole train: the package stays
  `1.8.0` through M25–M28 (and M28a) and **M29** performs the single bump to
  `2.0.0`. M28 touches neither `pyproject.toml` nor the packaging version
  pins; its CHANGELOG entries accumulate under the existing `UNRELEASED`
  heading.
- **Surface parity in the same change** (`plan.md` › *Ongoing conventions*;
  `CLAUDE.md` › *Skill update flow*): argparse `--help`, `docs/cli.md`,
  `docs/convention.md`, the bundled `src/docs_cli/skill/` (`SKILL.md`,
  `references/use-cases.md`, and `references/cli.md` /
  `references/convention.md` kept **byte-identical** to `docs/cli.md` /
  `docs/convention.md`), and `CHANGELOG.md` all describe the same behaviour.
- **The upgrade note names what changed for existing automation**: a move now
  edits prose; a move now refuses in a case it previously completed; and the
  M27 detect-then-repair sequencing is stated plainly, because between M27 and
  M28 an adopter is told about prose-link damage they must still fix by hand
  (`feedback-log.md`, *Ordering note*).
- **Host-machine and Agent Playbook Suite skills are out of scope.** Per
  `CLAUDE.md`, host skills under `~/.claude/skills/` refresh only at a
  production ship (M29).

## Out of scope

- **Widening the validated Markdown grammar.** Images, autolinks, raw HTML,
  and reference *uses* stay out (M27 — D1/Q2 and M27 *Follow-ups* item 1).
  M28 rewrites exactly what M27 validates, and no more.
- **Heading/anchor validation.** Fragments are carried through untouched; the
  2026-08-10 operator decision put anchor checking outside M27 *and* M28.
- **`docs migrate --apply`'s archive-normalising moves** (Q6). `apply_migration`
  relocates archive-shaped files into `archive/<date>/` and has never rewritten
  a `Related:` bullet either, so extending it is a different job on a foreign
  tree whose links were authored under no convention.
- **`docs project rename` and `docs project set`.** Neither moves a file, so
  neither can make a destination stale.
- **Links in files outside the docs root** — the repository `README.md`,
  `CHANGELOG.md`, and the bundled skill. Only documents the walk yields are
  scanned, and only they are rewritten (M27's boundary, unchanged).
- **Plain-text mentions, code samples, and external URLs.** A bare `plan.md`
  in a sentence, a fenced example, and an `https://` destination are never
  touched.
- **Repairing pre-existing damage.** M28 rewrites what *this* move makes
  stale; it never *repairs* a destination and never re-aims one. An already
  **escaping** destination is copied byte-for-byte in every case. An already
  **broken** but contained destination keeps its bytes while its referrer
  stays put, and is rebased to the **same, still-broken target** when the
  referrer itself moves — because the planner is pure and cannot know the
  target is missing, and because rebasing is what preserves the author's aim
  (amendment 4 to Q4). Either way the M27 finding survives the move. There is
  no `docs fix-links`; M27 — D6 repaired this repository once and adopters get
  the recipe.
- **Unarchive / undo**, and rolling back an interrupted execution batch —
  M26 — D4 considered and explicitly declined the latter, and that decision
  stands.
- **A general archive editor.** The archived-referrer rewrite is move-driven
  only (D5); no other byte of an archived document is in reach.
- **Changing the candidate set or the relationship vocabulary.** M25 owns the
  graph; M26 — Q3 owns the one-hop `pairs-with` / `child-of` discovery set and
  M28 does not re-open it (D6).
- **The `2.0.0` version bump, CHANGELOG dating, and release notes** (M29).

## Current state and risks

Measured against this repository at docs-cli 1.8.0 with M25–M27 merged
(`58955ef`, 1087 passed, `docs check` exit 0) during setup. Census runs were
**read-only** against the live tree; every mutation was performed on a
throwaway copy outside the repository. The full evidence table lives in the
implementation log's setup record. Each numbered item grounds a specific
decision and maps to named regression coverage in *Evidence → regression
coverage* below.

- **E1 — `docs mv` now produces a tree that fails `docs check`.** On a
  throwaway copy, `docs mv plan.md milestone-plan.md` reports
  `moved plan.md -> milestone-plan.md (35 reference(s) rewritten)` and exits
  **0**; `docs check` immediately exits **2** with **42 `broken-body-link`
  findings across 14 documents** (13 of them archived, plus the active
  `agent-native-invocation.md`). The metadata repair the tool performs is
  *smaller* than the damage it leaves behind.
- **E2 — one ordinary archive produces both classes at once.**
  `docs archive m17-pypi-publish-impl.md` exits 0 and leaves **13**
  `broken-body-link` findings: **10 class 1** (incoming — `status.md` ×3,
  `plan.md` ×2, `release-runbook.md` ×1, and **4 inside archived referrers**
  whose `../../m17-pypi-publish-impl.md` now dangles) and **3 class 2** (inside
  the moved document itself, whose `plan.md` and `release-runbook.md` links now
  resolve to `archive/2026-08-15/…`). One command, both classes, one verb.
- **E3 — the real milestone-closeout workflow damages the two most-read
  documents.** `docs archive m25-reciprocal-relationship-integrity.md
  --cascade-only 'm25-*' --reason …` — the exact invocation M26 prescribes and
  `create-milestones` will prescribe — exits 0 and leaves **6**
  `broken-body-link` findings in `status.md` (×4) and `plan.md` (×2). This is
  issue #1 finding 4 at this repository's scale; the reporter measured 29 link
  targets across 24 lines in 4 live files for two three-document sets, repaired
  by hand.
- **E4 — the exposure is large and concentrated.** The live tree carries
  **395** recognised spans over **71** documents, of which **379** are local
  destinations resolving to **69** distinct targets. The most-referenced:
  `release-runbook.md` (49 occurrences in 17 documents), `plan.md` (42 in 14),
  `cli.md` (24 in 10), `status.md` (24 in 9). Ten active documents carry 211
  outgoing local links between them.
- **E5 — the archived-referrer question is a blocker, not a nicety.** **131
  body links in 27 archived documents point at active documents** —
  `plan.md` ×38, `status.md` ×24, `release-runbook.md` ×23, `cli.md` ×20,
  `definition-of-ready.md` ×6, `agent-native-invocation.md` ×5,
  `test-strategy.md` ×4, and five more. Any move of those documents is
  **unrepairable** without writing to archived documents, and since M27 the
  unrepaired state is a hard `docs check` error. M18 already licenses exactly
  this class of move-driven write (D5).
- **E6 — `rewrite_related_refs` cannot be reused for this.** `Related:`
  targets are root-relative and matched by **exact string** — which is why
  M26 — Q5 had to carry a per-alias pair list to catch a `./b.md` bullet.
  Markdown destinations are **referrer-relative**, so the same target is
  spelled `plan.md` from the root and `../../plan.md` from
  `archive/YYYY-MM-DD/`; the E1 reproduction rewrote 35 bullets by string while
  leaving 42 destinations, in three different spellings, broken. The body-link
  rewriter must match on the **normalised** target (D1).
- **E7 — the strand-check's literal predicate over-fires on correct
  operations.** Three plans measured over this tree:

  | Plan | still-active `Related:` edges into the set | still-active body links | distinct active referrers |
  |---|---|---|---|
  | **A** `--cascade-only 'm26-*'` (a textbook closeout) | 8 | 8 | 7 |
  | **B** `--cascade-only '*'` (issue #1's harm) | 45 | 8 | 17 |
  | **C** archiving `plan.md` alone | 11 (incl. **6** live `child-of`) | 4 | 12 |

  A and B differ in **magnitude, not in kind**. Plan A's referrers are
  `status.md`'s tracker edges, `plan.md`'s `parent-of`, and the neighbouring
  milestones' `precedes` / `follows` / `depends-on` — every one of them
  deliberate, and every one repaired by the operation itself. Plan B and plan C
  are distinguished by something A does not have: **six still-active documents
  declaring `child-of: plan.md`**, i.e. a parent archived out from under live
  children. The harm itself is confirmed live:
  `docs archive m27-markdown-body-link-validation.md --cascade-dry-run
  --cascade-only '*'` marks `plan.md`, `cli.md`, `convention.md`,
  `test-strategy.md` and `status.md` **selected**.
- **E8 — nothing in the fixture corpus exercises this.** Across all **39**
  committed fixture trees there are 110 local body links, and **every one** is
  in the six `bodylink-*` trees (18) or the `real-trees-adopted` migrate
  fixture (92). The `archive-*`, `mv-with-malformed`, `rename-with-*`,
  `cross-refs` and `with-archive` trees — the ones `mv` and `archive` are
  tested against — carry **zero**. Re-verified against `docs/` as well:
  **zero** angle-bracket, percent-escaped or backslash-escaped destinations,
  and exactly **one** local destination anywhere in the tree carries a
  fragment (`convention.md` → `cli.md#common-exclusion`). Phase 3 must author
  every rewrite-relevant form deliberately, exactly as M27 — E8 forced.
- **Structural risk — ordering and atomicity.** `_cmd_mv` moves the file
  before it rewrites anything, so a class-2 rewrite and an all-or-nothing
  contract cannot both be satisfied without inverting it (D4). Getting this
  wrong produces the worst outcome in the milestone's space: a moved document
  with half its references repaired.
- **Structural risk — the convention.** Writing prose bytes into archived
  documents collides with a convention that calls M27 — D6 "the last
  [exception] this convention grants". D5 resolves it by widening M18's
  existing move-driven exception rather than granting a fourth, but the wording
  must be changed deliberately, not quietly.
- **Structural risk — a check that cries wolf.** A strand predicate that fires
  on correct trees fails the charter's success criteria and would push
  operators toward a bypass flag, which is how safety features die. E7
  quantifies the risk; Q1 is where it is answered.
- **Structural risk — re-encoding.** The scanner hands M28 a **decoded** path
  and a **raw** token. Writing a new destination means re-encoding, and no
  destination anywhere in the corpus exercises any escape (E8), so every
  re-encoding rule ships against authored fixtures only. Phase 1 must pin one
  strategy; Phase 3 must author the cases.
- **Mitigating existing strengths.** M27's span contract is already proven on
  real data at scale — its Phase-6 repair spliced 140 destinations across 30
  documents by offset, right-to-left, with 30/30 byte-identical round-trip
  reconstructions and every non-`equal` diff opcode inside a recorded span,
  which is literally M28's operation performed once by hand. M26 has just
  established the plan / pre-flight / apply / JSON-record split M28 extends to
  a second verb. M18 already writes move-driven repairs into archived
  documents. `atomic_write` and the M14 pre-flight walks are unchanged. And
  the scanner is fast enough to be run over the whole tree inside a move: 81 ms
  for this 2.5 MB tree at M27's Phase-10 measurement.

### Evidence → regression coverage

| Evidence | Addressed by | Named coverage (Phases 2–3) |
|---|---|---|
| E1 `mv` leaves 42 broken links | D1 + D4 | a `movelink-incoming` fixture whose root document is renamed leaves **zero** body-link findings; the moved-file diff touches only destination tokens; the pre-move plan is proven complete by refusing a rename whose referrer is unwritable, with zero bytes changed |
| E2 both classes in one archive | D1 (one formula) | a fixture where the archived document is both a target and a referrer yields zero findings afterwards, and the moved document's own destinations gain exactly the `../../` its new depth requires |
| E3 closeout damages the trackers | D1 + D4 | **(amended at Phase 1 — see *Amendments to the setup-frozen material*, item 3)** a new `movelink-closeout` tree **reproduces** the `archive-pair` / `archive-trio` shape, carrying real body links into the pair — the committed `archive-*` trees stay byte-identical; after `--cascade-only`, the tracker's links resolve to the `archive/YYYY-MM-DD/` paths and `docs check` is clean |
| E4 scale and concentration | D2 (span splice) | a nested multi-referrer fixture proves every occurrence is rewritten, one per occurrence, with labels/titles/fragments byte-identical |
| E5 archived referrers | D5 | an archived referrer whose target moves has its destination repointed and **nothing else** changed — `Lifecycle:`, `Archived-reason:`, H1, prose and every non-moving edge byte-identical; a companion lock asserts the Q2-resolved audit-metadata shape |
| E6 exact-string matching is wrong here | D1 step 1 | one target spelled three ways (`x.md`, `./x.md`, `sub/../x.md`) in three referrers is rewritten in all three, with no alias list |
| E7 strand over-fire and harm | D6 leg 1 | plan A (a scoped closeout) **completes**, plan B / plan C **refuse** with both ends named and zero bytes written, and the preview reports the same verdict at exit 0; a dedicated over-fire lock asserts that a plan whose only still-active inbound references are `pairs-with` / `precedes` / `follows` / `depends-on` / body links **does not refuse** |
| E7 leg 2 — the report | D6 leg 2 | every still-active inbound reference that does **not** refuse is named — both ends — on stderr in the preview, on stderr in the apply output, and in the record's `strands` array; the array is present and correct for plan A (which completes) as well as for plan B — **(amended at Phase 1 — item 2)** plan B's array is observed in its **preview**, which exits 0 and emits the record, because a leg-1 refusal emits no `--json` record at all; an empty neighborhood yields an empty array, never a missing key |
| E8 unexercised forms | D2/D3 + Phase 3 | authored fixtures for an angle destination, a titled destination, a percent- and a backslash-escaped destination, a fragment-bearing destination, a directory destination, and a reference definition — each rewritten with only its destination token changed; every non-`local` kind proven byte-identical |

## Deliverables

- [x] The rewrite formula, the emitted spelling and re-encoding rules, the
      no-op rule, the archived-referrer policy, the strand-check predicate and
      its message, the atomicity boundary, and the Phase-5 signatures frozen in
      Phase 1 against the resolved Q1–Q7. *(Done — see* Decisions (Phase 1 —
      BINDING) *below.)*
- [x] A pure, stdlib-only rewrite planner over `(old referrer rel, new referrer
      rel, move map, BodyLink)` with no filesystem access of its own.
- [x] A minimal destination-token editor that preserves every unrelated byte,
      applied right-to-left, one `atomic_write` per document.
- [x] `docs mv` and `docs archive` integration for single and batch moves,
      with `mv`'s plan built before the move and every handled failure refusing
      with zero mutation.
- [x] **The strand-check's refusal leg** (D6 leg 1) — the `child-of` predicate,
      running in the write path **and** the preview, naming both ends, with
      zero false positives on this tree's legitimate closeouts.
- [x] **The strand-check's reporting leg** (D6 leg 2) — every other
      still-active inbound reference, `Related:` and body link alike, named
      with both ends in the preview, in the apply output, and in the record's
      `strands` array, refusing nothing. This is the half that answers issue #1
      finding 1's actual complaint and is not optional.
- [x] `docs mv --dry-run` / `docs mv --json` and the `archive --json` rewrite
      section, one schema shared by preview and apply (Q3).
- [x] Archived-referrer rewriting implemented under the D5 policy — destination
      tokens only — with `convention.md`'s M18 exception widened and
      M27 — D6's "last one this convention grants" sentence reconciled.
- [x] Regression coverage for E1–E8 plus failure-injection, nested-path,
      fragment/title/angle-form, non-`local`, idempotence, and no-op locks, and
      proof that M12 referring-edge, M18 archive-edge, and M26 plan behaviour
      are unchanged.
- [x] Surface parity across `--help`, `cli.md`, `convention.md`, the bundled
      skill (byte-identical mirrors), and the `UNRELEASED` CHANGELOG, plus the
      v2.0 upgrade note.
- [x] End-to-end dogfood on a throwaway copy proving zero dangling supported
      links after a rename, a single archive, and a real milestone closeout —
      and proving the second run of the same move changes nothing.

## TDD implementation plan

### Phase 1 — Define Contract

- Objective: freeze — against the resolved Q1–Q7 — D1's three-step rewrite
  formula and the move map it consumes; the emitted spelling, the fragment
  rule, the delimiter-preservation rule and the single re-encoding strategy;
  the byte-for-byte no-op rule; the never-creates-an-escape invariant with its
  proof; the archived-referrer policy (destination tokens only — Q2) and its
  exact `convention.md` wording; the strand-check's **two legs** — leg 1's
  `child-of` refusal predicate, the documents it examines, its message, its
  exit code, and leg 2's report, its ordering, and the exact lines and record
  keys that carry it; the pre-flight boundary and the partial-state admission
  wording; the preview and `--json` shapes for **both** verbs including
  `mv`'s new record and `archive --json`'s new rewrite section and `strands`
  array; and the Phase-5 signatures. No business logic lands. Phase 1 does
  **not** re-open the setup decisions.
- Files: `docs/cli.md` (the `mv` and `archive` sections, the rewrite
  behaviour, the strand refusal and its exit-code rows, any `--json` field
  table), `docs/convention.md` (M18's widened exception; the author-facing
  statement that a move rebases supported links), this milestone. Interface
  signatures are frozen in a *Decisions (Phase 1 — BINDING)* section here
  rather than stubbed in `src/docs_cli/cli.py`, following the M25/M26/M27
  precedent — stubs would perturb the Phase-4 subprocess RED reasons.
- Exit: specs, help strings, the messages and the frozen signatures are
  internally consistent; no behavior changes; `docs check --root docs` still
  exits 0 and the suite is still 1087 GREEN.

### Phase 2 — Write Tests (RED)

- Objective: express planning, splicing, both move classes, the archived
  referrer, **both** strand-check legs, the failure paths and the no-op rule
  before any implementation — including every case that must stay GREEN at
  baseline, and including the leg-1 over-fire lock proving a legitimate
  closeout completes.
- Files: a new pure-planner module `tests/test_move_links.py` (the
  `tests/test_relate_plan.py` / `tests/test_archive_plan.py` /
  `tests/test_body_links.py` precedent), `tests/test_cli_mv.py`,
  `tests/test_cli_archive.py`, `tests/test_check.py` /
  `tests/test_cli_check.py` for the post-move clean assertions, and the
  skill-parity tests where the surface moves.
- Exit: the E1–E8 locks in *Evidence → regression coverage* are RED **only**
  for missing M28 behavior; the M12 referring-edge, M18 archive-edge, M26
  plan/pre-flight/`--json` and M27 finding locks stay GREEN at baseline and are
  classified as such; the closed four-key `Finding` record is asserted
  unchanged, and `archive --json`'s top-level key set is asserted to widen by
  exactly the Q3-resolved rewrite and `strands` keys and nothing else.

### Phase 3 — Create Data/Fixtures

- Objective: provide small committed trees isolating one semantic each, per
  `test-strategy.md`'s fixture policy, plus inline builders for the mutation
  cases.
- Files: new `tests/fixtures/trees/movelink-*` trees — `-incoming` (class 1),
  `-moved-referrer` (class 2), `-both` (a document that moves *and* links to
  another document moving in the same operation), `-archived-referrer` (E5's
  shape), `-nested` (a deep subdirectory linking up and down), and `-strand`
  (the issue #1 shape: a live child, a parent selected by a glob). Exotic
  grammar (angle destinations, titles, percent- and backslash-escapes,
  fragments, reference definitions, directory destinations) lives in inline
  strings against the pure planner, and mutation-shaped cases that write and
  then byte-compare use inline `tmp_path` builders — the M25 rule, because
  those assert on written bytes rather than on a tree walk.
- Exit: fixtures are structure-only (never date-sensitive), parse
  deterministically, and each yields exactly its intended plan; the existing
  `archive-*` / `mv-*` / `rename-*` trees stay byte-identical, and the
  no-new-findings locks over the pre-M28 trees are extended to cover the new
  ones.

### Phase 4 — Run Tests (RED Baseline)

- Objective: prove the new tests fail for the intended missing behavior and for
  nothing else.
- Files: implementation log only.
- Exit: full baseline captured with exact counts; zero collection errors, zero
  tracebacks, zero xfails; every one of the 1087 pre-existing test ids
  mechanically proven still present and GREEN; every GREEN-at-baseline lock
  classified by name, including any test whose expected state is
  **transitional** across Phase 6.

### Phase 5 — Update Base Interfaces

- Objective: add the planning models and pure helpers without wiring any verb —
  an immutable per-occurrence rewrite record (document, `BodyLink`, old
  canonical target, new canonical target, new token text), a whole rewrite plan
  (root, config, move map, per-document rewrites in deterministic order, the
  strand set), the pure planner, the splicer, the strand predicate (leg 1) and
  the strand report (leg 2), and a JSON
  serializer. Shaped after M25's `RelateEdit` / `RelatePlan` / `plan_relate` /
  `apply_relate_plan` / `relate_plan_to_json` and M26's `ArchiveMove` /
  `ArchivePlan` split, which the codebase already proves out. The planner stays
  a pure function of `(text, old rel, new rel, move map)`; existence checks and
  writes are the caller's job.
- Files: `src/docs_cli/cli.py` and `tests/test_move_links.py`.
- Exit: interfaces typecheck and are unit-tested; `_cmd_mv` and `_cmd_archive`
  are untouched, so the CLI-level tests stay honestly RED at the seam;
  `docs check --root docs` still exits 0.

### Phase 6 — Implement Offline/Core Path

- Objective: wire the planner into both verbs — invert `_cmd_mv` to plan before
  it moves, fold the body-link splices into `_rewrite_referring_edges`' single
  per-document write, apply the archived-referrer policy (destination tokens
  only), run **both** strand-check legs inside the pre-flight and in the
  preview, and implement the refusal, the report, and the partial-state paths.
- Files: `src/docs_cli/cli.py`, the mv/archive/check unit and integration
  tests.
- Exit: core and integration tests GREEN; a rename, a single archive and a
  scoped batch each leave `docs check` clean; every handled failure refuses
  before the first write; the diff of a move touches only destination tokens
  and the metadata a move already owned; M12, M18 and M26 behaviour
  byte-stable; `docs check --root docs` still exits 0.

### Phase 7 — Update Tool/Wrapper Layer

- Objective: reconcile every parallel surface — the argparse surface for both
  verbs (including `mv --json` and its real `--dry-run`, Q3), human stderr
  output for the rewrites and for the strand report, the JSON records and their
  field tables, exit codes, the single end-of-batch reindex, `cli.md`'s `mv`
  and `archive` sections and exit-code rows, `convention.md`'s widened M18
  exception **and the reconciliation of M27 — D6's "last one this convention
  grants" sentence**, its author-facing move guarantee, the bundled skill, and
  the `UNRELEASED` CHANGELOG with the upgrade note. `feedback-log.md`'s issue
  #1 entry gains a dated note recording that finding 4's `--report-links`
  option was answered — declined as a design, adopted as the plan record — and
  that finding 1's routed predicate was amended (A1), so the feedback trail
  stays complete.
- Files: CLI parser/dispatch, `docs/cli.md`, `docs/convention.md`,
  `src/docs_cli/skill/` (`SKILL.md`, `references/use-cases.md`, and the
  byte-identical `cli.md` / `convention.md` mirrors), `CHANGELOG.md`.
  **Not** `pyproject.toml` or the version pins (M25 — D6).
- Exit: subprocess tests, the reference byte-identity tests and the
  surface-parity checks are GREEN; `docs mv --help` / `docs archive --help` and
  `cli.md` agree.

### Phase 8 — Run Tests (GREEN)

- Objective: run the focused and full suites plus lint, format, types,
  reference byte identity, and docs integrity.
- Files: implementation log only unless a real defect is found.
- Exit: all gates GREEN with exact counts recorded, and every pre-existing test
  id mechanically proven still present and GREEN.

### Phase 9 — Integrate / Accept / Dogfood

- Objective: on a throwaway copy of this docs tree, replay each measured
  defect and prove it gone. Rename `plan.md` (E1) and confirm `docs check`
  exits 0 with a destination-token-only diff instead of 42 findings; archive
  `m17-pypi-publish-impl.md` (E2) and confirm both classes are repaired,
  including the four archived referrers; run the real closeout
  `docs archive m25-… --cascade-only 'm25-*'` (E3) and confirm the tracker and
  the plan still resolve. Exercise the leg-1 refusal on plan B and plan C and
  byte-compare the tree afterwards, and confirm plan A **completes** with its
  leg-2 report naming all 16 of its still-active inbound references. Prove
  **idempotence** — re-running an equivalent move changes nothing — and measure
  the added runtime of a move over this 71-document tree. The real tree is
  never written to.
- Files: throwaway trees only; the committed docs record the evidence.
- Exit: every flow runs unattended with no stdin; `docs check` is clean after
  each repair flow; the refusal flows change zero bytes; plan A completes and
  its report matches the setup census exactly; the preview and apply records
  agree; runtime is recorded and bounded; the real tree is untouched.

### Phase 10 — Quality, Docs, Refactor

- Objective: run the `/simplify` pass over the planner and the two verbs, close
  `architecture.md` (the `mv` / `archive` sections and the move pipeline) and
  `test-strategy.md`, update the shipped use-case catalog, and write the
  completion summaries.
- Files: code/docs as justified, this milestone and the implementation log.
- Exit: full gate GREEN; no placeholders; M28 implementation-complete and
  handed to M28a and M29, staying `Lifecycle: active` until the M29 publish
  closeout.

## Phase checklist

- [x] Phase 1 — Define Contract
- [x] Phase 2 — Write Tests (RED)
- [x] Phase 3 — Create Data/Fixtures
- [x] Phase 4 — Run Tests (RED Baseline)
- [x] Phase 5 — Update Base Interfaces
- [x] Phase 6 — Implement Offline/Core Path
- [x] Phase 7 — Update Tool/Wrapper Layer
- [x] Phase 8 — Run Tests (GREEN)
- [x] Phase 9 — Integrate / Accept / Dogfood
- [x] Phase 10 — Quality, Docs, Refactor

## Decisions carried from discovery

- `docs mv` and `docs archive` should automatically rewrite actual Markdown
  body-link destinations that resolve to a moved document, while leaving
  plain-text mentions and code examples unchanged. Path repair belongs to the
  coordinated move rather than to a separate whole-tree substitution pass
  (`feedback-log.md`, 2026-08-09/10).
- Move-time rewrites preserve fragments such as `#section`, and neither M27 nor
  M28 validates whether the referenced heading exists.
- Detection (M27) and mutation (M28) are separate milestones sharing **one**
  scanner; there is never a second Markdown parser.
- Relationships provide context, never archive authorization (M26 — D1); M28
  does not re-open the candidate set, it validates the plan's consequences.
- Escaping destinations are a *forbidden and reported* condition after M27, so
  a clean tree contains none and M28 never has to rebase one (M27 *Follow-ups*
  item 5, which answers this milestone's original Open question 2).
- The package version stays `1.8.0`; M29 performs the single bump
  (M25 — D6).

## Decisions recorded at setup (BINDING)

Three of the seven setup answers changed something that was already written
down — a routed scope item, the registered stub's own recommendation, and an
unresolved feedback option. They are restated here, in one place, so a Phase-1
agent with none of the setup conversation can reconstruct **what** was decided,
**what it replaced**, and **why**, from this document alone. The full reasoning
stays in *Resolved setup questions (Q1–Q7, BINDING)*.

### A1 — Amendment to the 2026-08-15 routing entry (Q1, operator)

`feedback-log.md`'s 2026-08-15 promotion note routed issue #1 finding 1 into
M28 with a **literal predicate**: *over the complete plan M26 already computes
before writing, refuse the operation if applying it would leave a still-active
document pointing at a newly-archived one, naming both ends*, and asserted that
it "self-cancels for legitimate whole-set archiving, because a set archived
together strands nothing".

**That predicate was measured against this repository during setup, and the
self-cancelling claim does not hold on a real tree.** Plan A — a textbook
milestone closeout, `docs archive m26-safe-archive-selection.md --cascade-only
'm26-*'` — leaves **8 still-active `Related:` edges and 8 still-active body
links, from 7 active referrers** (E7). Every one is deliberate: `status.md`'s
tracker `pairs-with` edges, `plan.md`'s `parent-of`, and the neighbouring
milestones' `precedes` / `follows` / `depends-on`, which is precisely what
M25's reciprocal graph exists to record, and `status.md` already carries 20+
archive-subtree edges by design. Under the routed wording, **this project's own
standard closeout would refuse.**

**The amendment (BINDING).** The predicate is split into a narrow refusal and a
broad report:

- **Leg 1 (refusal):** refuse only when a still-active document **outside the
  plan** declares itself **`child-of`** a document the plan would archive.
  Measured **0** on plan A, **6** on plan B (`--cascade-only '*'`), **6** on
  plan C (`plan.md` alone). Exit 2, before any write, both ends named.
- **Leg 2 (report):** every other still-active inbound reference — any other
  `Related:` verb and every body link — is **named, not refused**, in the
  preview, in the apply output, and in the record's `strands` array.

**Why this and not the literal form.** The literal predicate fails the
charter's *never cry wolf* criterion — and that is not an abstract objection:
it is **the same criterion the operator applied in the same feedback entry**
when declining issue #1's finding-3 suggestion ("two documents archived months
apart may legitimately carry an edge, so the rule would fire on correct trees
and fail the charter's *never cry wolf* criterion"). Applying that standard
consistently to finding 1 is what produced this amendment. Leg 2 preserves the
routing note's stated purpose — direction-agnostic visibility that closes the
`child-of`, `pairs-with` and body-link routes together — by delivering it to
the agent that generates the glob rather than to prose it may skim, which is
issue #1's own diagnosis of where the safety was resting. M26 — Q3's frozen
candidate set is untouched.

**Alternatives considered and rejected**, recorded so the decision is
auditable:

| Alternative | Rejected because |
|---|---|
| Ship the routed literal predicate unchanged | Refuses plan A — this repository's own standard milestone closeout — on 16 deliberate references. A safety check that blocks the workflow the tool exists for is one operators route around. |
| Refuse an **unbounded** `--cascade-only '*'` pattern, by M26's negated-pattern reasoning ("a negated scope means *everything except X*, the unbounded selection D1 exists to prevent") | Trivially defeated by `*.md`, `[a-z]*`, or any equivalent spelling, so it stops one literal invocation rather than the class of harm. Not adopted; not forbidden either, if a later milestone wants it as defence in depth. |
| Refuse when the plan archives a document whose `Role:` is a long-lived one (`plan`, `charter`, `status`, `spec`) | Turns a consequence check into a vocabulary policy: it decides what *may* be archived rather than what a plan *would do*, which is a different contract living in `convention.md`, and it would fire on legitimately superseded specs. |
| The reporter's own suggestion — follow *incoming* `child-of` for candidate discovery | Already considered and declined at routing time: it changes discovery rather than validating consequences, and `pairs-with` is symmetric, so a live sibling stays reachable. Leg 1 uses the `child-of` direction as a **consequence** test over the finished plan, which is a different mechanism with a different blast radius. |

### A2 — Supersession of the registered stub's Open question 1 (Q2, operator)

The registered M28 stub recommended, for archived referrers, to "permit only
move-driven destination token changes, **bump `Updated:`, and append a
generated `Revision:` audit reason that names the move**". **That
recommendation is superseded.** The archived-referrer rewrite carries
**destination tokens only** — no `Updated:` bump, no `Revision:` bullet
(D5) — and is implemented by **widening M18's existing move-driven exception**
rather than by granting a fourth exception to archived-document immutability.

Why the reversal: it is the same trigger, the same operation and the same
single `atomic_write` as M18's `Related:` half, so auditing one half and not
the other would be incoherent; nothing new is asserted, because the document
still points at the same target in a different spelling, whereas M25 — D4's
`Revision:` records a document *changing what it claims*; and an `Updated:`
bump would make an archived document's date a record of some **other**
document's move while churning `INDEX.md` and the frozen index snapshot on
every move. The apparent counter-precedent, M27 — D6, bumped `Updated:` and
appended `Revision:` on 29 archived documents — but that was a one-time
migration performed by the milestone, of which `convention.md` explicitly says
**no CLI verb performs it**.

Phase 7 must also **reconcile M27 — D6's sentence calling itself "the last one
this convention grants"** with the widened M18 paragraph. M28 grants no new
exception, and the convention has to say so rather than contradict itself.

### A3 — Issue #1 finding 4 is answered, not dropped (Q3, operator)

`feedback-log.md` issue #1 finding 4 recorded a scope option and explicitly
deferred it to M28 planning: *declare prose links out of scope in the
documentation and ship a `--report-links` mode that only lists inbound prose
references to moved files*.

**Decision: `--report-links` is DECLINED AS A DESIGN; its OUTPUT is ADOPTED.**
Declining is forced by M27, which already made a broken prose link a hard
`docs check` error — so "declare them out of scope" would mean the tool
knowingly ships trees that fail its own gate, which E1, E2 and E3 measure at
42, 13 and 6 findings respectively. The output is adopted, and widened, as a
**plan record on both verbs**: `docs mv` gains a real `--dry-run` preview and a
`--json` rewrite-plan record, and `docs archive --json` gains the same rewrite
section plus the `strands` array, one schema shared by preview and apply
following M26 — D7 and M25's `relate --json` conventions (D7).

Phase 7 adds a dated note to `feedback-log.md`'s issue #1 entry recording this
answer and the A1 amendment, so the feedback trail shows findings 1 and 4 were
resolved rather than silently absorbed.

## Resolved setup questions (Q1–Q7, BINDING)

Seven questions were raised at setup and **all seven are resolved before
Phase 1**. The originals are kept, with the reasoning that produced each
answer, so the decision trail reads end-to-end. Three were operator decisions
(Q1, Q2, Q3); four were conductor-resolved (Q4, Q5, Q6, Q7) as determined by
the specs, the measured evidence, or the M25/M26/M27 precedent. Q2, Q4 and Q5
are the registered stub's three "Open questions for M28 Phase 1", carried
forward and sharpened by the setup measurements — and **Q2 was resolved against
the stub's own recommendation** (A2). Phase 1 freezes the contract against
these answers and does not re-litigate scope.

### Q1 — What exactly does the post-plan strand-check refuse?

**RESOLVED → D6 (operator). Narrow the refusal to the `child-of` direction;
report everything else.** Recorded as an amendment to the routing entry in
*Decisions recorded at setup (BINDING)* › *A1*.

**Why it mattered.** This is the difference between a safety feature and a
feature operators disable. The routing entry's literal wording — *refuse if
applying the plan would leave a still-active document pointing at a
newly-archived one, through a `Related:` edge or a body link* — was measured
against this tree (E7) and **refuses the standard milestone closeout**: plan A,
a textbook `--cascade-only 'm26-*'`, leaves 8 still-active `Related:` edges and
8 still-active body links from 7 active referrers, every one of them
deliberate. The routing entry expected the predicate to "self-cancel for
legitimate whole-set archiving, because a set archived together strands
nothing"; on a real tree it does not, because the tracker (`status.md`), the
plan (`plan.md`) and the neighbouring milestones' `precedes` / `follows` /
`depends-on` edges are *supposed* to survive the closeout and keep pointing at
completed work. That is what M25's reciprocal graph exists to record, and
`status.md` already carries 20+ archive-subtree edges by design.

**The resolution — two legs, both binding:**

1. **Refuse on the parent-strand direction.** Refuse when the plan would
   archive a document that a **still-active document outside the plan declares
   itself `child-of`**. Measured: **0** occurrences in plan A, **6** in plan B,
   **6** in plan C. This is exactly the reported harm — a live
   `milestone-plan.md` archived out from under its live children — it is
   provable from the graph the plan already builds, it costs no false positive
   on this tree's legitimate operations, and it does not re-open M26 — Q3's
   candidate set. The refusal names both ends and exits 2, before any write.
2. **Report every other still-active reference into the set** — `pairs-with`,
   `precedes` / `follows`, `depends-on` / `required-by`, `blocks` /
   `blocked-by`, free-form verbs, and body links — in the preview, in the apply
   output, and as a `strands` array in the machine-readable record, **without
   refusing**. This is the direction-agnostic visibility the routing entry
   asked for, delivered to the caller that actually needs it rather than as
   prose a skimming agent misses. **It is not optional**: it carries its own
   deliverable, its own success criterion, and its own named regression
   coverage, because it is the half that answers issue #1's actual complaint.

The rejected alternatives — shipping the literal predicate, refusing an
unbounded `'*'` scope, and a `Role:`-based rule — are tabulated with the reason
each lost in *A1*.

### Q2 — Does an archived referrer's body-link rewrite carry audit metadata?

**RESOLVED → D5 (operator). No: destination tokens only — M18's shape.**
**This resolves the question against the registered stub's own
recommendation**; the supersession is recorded in *Decisions recorded at setup
(BINDING)* › *A2*.

**Why it mattered.** E5 measures 131 body links in 27 archived documents
pointing at active documents, so this fires on almost every future move of a
core document, and the two available precedents disagree. M18's move-driven
edge rewrite changes **only** the stale `Related:` bullet — no `Updated:` bump,
no `Revision:` bullet. M25 — D4's audited relationship repair changes the
bullet, the `Updated:` value **and** appends a dated `Revision:` record. The
registered stub recommended M25 — D4's shape.

**The resolution — M18's shape: destination tokens only, no `Updated:` bump,
no `Revision:` bullet.** Three reasons. **(a) Same trigger, same operation,
same write.** M28's archived-referrer edit is `_rewrite_referring_edges`'
existing edit with the destination token added to it; making the body half
audited while the `Related:` half stays silent would be incoherent in a single
file write. **(b) Nothing new is asserted.** A `Revision:` record exists to
explain a *semantic* change to what an archived document claims — M25 adds or
removes an edge. A move-driven destination rewrite claims the same thing in a
different spelling. **(c) Cost.** An `Updated:` bump on every archived referrer
churns `INDEX.md` and the frozen index snapshot on every move, and would make
`Updated:` a record of other documents' moves.

The counter-argument, recorded: M27 — D6's one-time repair *did* bump
`Updated:` and append `Revision:` on 29 archived documents. But that was a
migration performed once, deliberately, by the milestone — `convention.md`
states that **no CLI verb performs it** — not a per-operation behaviour, and
the distinction is exactly why M18 and M25 — D4 already differ.

The implementation follows from the answer: D5's widening of M18's exception is
written into `convention.md` with a stated blast radius, **no fourth exception
is granted**, and the *last exception this convention grants* sentence in
M27 — D6's paragraph is reconciled in Phase 7 rather than left contradicting the
widened M18 paragraph.

### Q3 — Does `docs mv` gain a preview and a `--json` rewrite-plan record?

**RESOLVED → D7 (operator). Yes to both**, and issue #1 finding 4's
`--report-links` is **declined as a design while its output is adopted** —
recorded in *Decisions recorded at setup (BINDING)* › *A3*.

**Why it mattered.** M28 turns `docs mv` from a rename-plus-metadata-fixup into
a tree-wide prose mutation. `docs mv --dry-run` today prints one line — the
old and new path — and there is no machine-readable surface at all; `docs
archive` has had an operation-plan record since M26 — D7. This is also where
`feedback-log.md` issue #1 finding 4's `--report-links` alternative is answered
(D7). M26's own *Out of scope* named "generalizing the archive planner or the
`--json` plan record to `docs mv`" as deliberately not-that-milestone's work,
which makes it this one's question rather than a settled matter.

**The resolution — yes, both.** `docs mv --dry-run` names every planned
destination rewrite (document, line, old spelling, new spelling) and the strand
report instead of one line; `docs mv --json` emits one rewrite-plan record with
**the same shape for a preview and a real apply**, following M26 — D7's
operator-approved `archive --json` addition and M25's `relate --json` pattern
for shape and field-table conventions. The planner is being built anyway, so
the incremental cost is the record and its field table; the benefit is that an
agent can diff the plan before and after and never has to parse stderr — the
fragility M25 removed and M26 extended. `docs archive --json` gains the same
rewrite section and the `strands` array, its top-level key set widening by
those keys only.

The alternative — keep `mv`'s single-line `--dry-run`, add nothing, and defer
the record to M29+ — was rejected: it would leave the verb that now writes the
most bytes as the only one with no machine-readable plan.

### Q4 — What happens to destinations a move does not own?

*(The registered stub's Open question 2, sharpened.)*
**RESOLVED → D2 + D3 (conductor), as recommended.**

**Why it mattered.** M27's *Follow-ups* item 5 already answers the original
form: because an escaping destination is a forbidden and reported condition,
a clean tree contains none and **M28 never has to rebase one** — including the
decoded forms (`%2F…`, `\/…`). What remains is what M28 does when it meets one
anyway, in a tree that has not been repaired, since neither `mv` nor `archive`
runs `docs check` first.

**The resolution — leave every non-`local` and every escaping destination
byte-identical, never repair a broken one, and do not gate the move on any of
them.** The five non-`local` kinds are copied through untouched by construction
(D2). An escaping `local` destination is copied byte-for-byte in every case. An
already-broken but *contained* destination keeps its M27 finding either way:
its bytes are untouched while its referrer stays put, and it is rebased to the
**same, still-broken target** when the referrer moves — see *Decisions
(Phase 1 — BINDING)* › *Amendments* › item 4, which narrows this answer's
"already broken" clause for the reason that the planner is pure and cannot
know. Rewriting a broken destination to something *else* would require deciding
what it *should* have said, and refusing the move because of unrelated
pre-existing damage would make an unrelated repair a precondition for a rename.
`docs check` owns pre-existing damage; `docs mv` owns the damage it would
otherwise cause.

### Q5 — Same-path normalisation and the emitted spelling

*(The registered stub's Open question 3, sharpened.)*
**RESOLVED → D3 (conductor), as recommended.**

**Why it mattered.** Two sub-questions, both of which change what a move's diff
looks like. First: when the computed destination denotes the same file as the
existing one, does the tool rewrite it into canonical form? Second: when it
*must* rewrite, which spelling does it emit, and how does it re-encode a path
containing a space, a `#`, a `%`, or parentheses — given that **no destination
anywhere in the corpus exercises any of those** (E8), so the rule ships against
authored fixtures only.

**The resolution.** (a) **Byte-for-byte preservation when the meaning is
unchanged** — no gratuitous normalisation, so a move's diff contains only what
the move made stale. (b) When a rewrite is required, emit the
`posixpath.relpath` form (no leading `./`), reattach the fragment verbatim
after a single `#`, and preserve the original delimiter form: an angle-wrapped
destination stays angle-wrapped, and a plain destination that would need to
carry a space or an unbalanced parenthesis is percent-encoded rather than
promoted to angle brackets — one strategy, no "it depends" cell, stated in
`cli.md` and locked by a parametrized round-trip test asserting that decoding
the emitted token reproduces the intended path.

### Q6 — Does `docs migrate --apply` get the same treatment?

**RESOLVED → Out of scope (conductor), as recommended.**

**Why it mattered.** `apply_migration` is a **third** file mover: it relocates
archive-shaped files into `archive/<date>/`. After M27 those moves can leave
`broken-body-link` errors in a freshly adopted tree, and an adopter's first
`docs check` would then fail on damage the adoption itself caused — the same
shape as E1/E2.

**The resolution — out of scope for M28, recorded as *Follow-ups* item 1.**
`docs migrate` has never rewritten a `Related:` bullet either, so its
reference-repair story is *uniformly* absent rather than half-present; it
operates on a foreign tree whose links were authored under no convention and
whose ambiguities are already agent-resolved rather than tool-resolved; and its
`--apply` is preceded by a dry-run report by design. Folding it in would widen
M28 from two verbs to three and from a coordinated move to an adoption
workflow. The honest alternative — doing it here — is recorded so a later
milestone picks it up knowingly.

### Q7 — Does M28 fix M26's duplicate-`Related:`-bullet follow-up?

**RESOLVED → Re-deferred (conductor), as recommended.**

**Why it mattered.** M26's *Follow-ups* item 3 is homed explicitly to "M28 (it
reworks that rewriter for body links)": a primary declaring both `beta.md` and
`./beta.md` yields one `(alias, new_rel)` pair per spelling, so the moved
document ends up with two byte-identical `Related:` bullets. Current behaviour
is pinned by
`tests/test_cli_archive.py::test_two_spellings_of_one_edge_survive_the_rewrite_as_duplicate_bullets`.

**The resolution — re-deferred explicitly, with the reason, rather than left
to lapse.** M28 builds a *destination-token splicer over body text*, not a
`Related:`-block editor, so it does not in fact bring the tool the duplicate
fix needs; the cost is cosmetic (every edge resolves and `docs check` is
clean); and the correct fix — `Related:`-block-aware editing — belongs beside
M25's editors. Worth noting for contrast: the body-link rewriter has **no**
alias problem at all, because it matches on the normalised target (D1, E6), so
the two surfaces genuinely differ. The rejected alternative — making
`apply_archive_plan` deduplicate its pairs on `(rel, dest_rel)` and flipping
that pinned test — is small but **reaches into M26's frozen Phase-1 Q5
contract**, and M28 does not do that.

### Also settled, without a question

- **Version staging.** The package stays `1.8.0`; **M29** performs the single
  bump to `2.0.0`. CHANGELOG entries accumulate under `UNRELEASED`
  (M25 — D6).
- **Exclusion predicates govern the walk, not the destination.** `[exclude]` /
  `.docsignore` decide which documents are walked and therefore which are
  rewritten — exactly as they already decide which `Related:` bullets
  `_rewrite_referring_edges` repoints — and never decide what a destination may
  point at (M26 — Q8 / M27 — D3, restated).
- **`INDEX.md` is never scanned and never spliced.** `_iter_doc_texts` skips
  the root-level generated index for every rule; the move refreshes it once at
  the end, as it already does.
- **Fragments are preserved and never validated**, in M28 exactly as in M27.
- **One finding vocabulary.** M28 adds no new `docs check` rule; it removes the
  conditions under which M27's two rules fire. Any refusal is a CLI message
  with an exit code, not a `Finding`.
- **Skill channels.** The bundled skill in `src/docs_cli/skill/` updates in the
  **same change** as the surface, with `references/cli.md` and
  `references/convention.md` byte-identical to `docs/cli.md` and
  `docs/convention.md`. Host-machine skills — including `create-milestones`,
  whose milestone-completion step prescribes the archive invocation E3
  measures — refresh only at the M29 production ship, and the Agent Playbook
  Suite update stays a post-M29 cross-repository follow-up (`CLAUDE.md`;
  `plan.md`).

## Decisions (Phase 1 — BINDING)

Phase 1 freezes the surface Phase 2 asserts against. Everything below is
binding for M28; Phases 5–7 implement it verbatim. The setup decisions (D1–D8)
and the resolved setup questions (Q1–Q7) are **not** re-opened — this section
makes them exact. The author-facing statement lives in `cli.md` ›
*Move-safe body-link rewrites (M28 — D1–D7)*, `cli.md` › *`docs mv`* and
`convention.md` › *Body links (M27)* / *Archive subtree*; what follows is the
machine-facing contract plus the decisions that could not be read off the
setup text.

### Amendments to the setup-frozen material (BINDING)

Three frozen items could not stand as written. All three are recorded here so
the binding scope and the frozen contract cannot disagree — M27's precedent
for amending setup-frozen material in place rather than diverging silently.

| # | Amendment | Why the frozen form could not stand |
|---|---|---|
| 1 | **M26's compatibility matrix row "a preview writes nothing and exits 0, full stop" is amended: a preview adopts failures of plan *construction* and reports-but-does-not-adopt *consequence* verdicts.** A malformed tree makes `archive --cascade-dry-run` exit **1** and `mv --dry-run` exit **2** — the codes their write paths already use — while a leg-1 strand verdict is reported at exit 0. `docs/m26-safe-archive-selection.md` › *The compatibility matrix (BINDING)* is amended by this row. | D6 requires both strand legs to run in the preview, and a preview cannot report a plan it could not build. M26's own *Follow-ups* item 2 records that the frozen check order lets a preview miss a pre-flight refusal and names repeating it as the mistake to avoid. The distinction is not "preview vs write" but "can I describe this operation at all" vs "what would this operation cost" — the first is adopted, the second is reported. |
| 2 | **The E7 leg-2 coverage row's observation point for plan B is its PREVIEW.** The row asks for the `strands` array "for plan B (which refuses)". A leg-1 refusal emits **no** `--json` record (M26's frozen Phase-1 Q3 rule, restated in `cli.md`), so plan B's array is asserted in `archive --cascade-dry-run --cascade-only '*'` — exit 0, record emitted, leg-1 verdict reported. The row is amended in place. | Otherwise Phase 2 would have to assert a record that the frozen no-record-on-refusal rule forbids. The preview is exactly where D6 says the leg-1 verdict is reported rather than adopted, so it is the natural observation point and no rule has to bend. |
| 3 | **The E3 coverage row's "the `archive-pair` / `archive-trio` shapes **gain** body links" is amended to "a new `movelink-closeout` tree reproduces the `archive-pair` / `archive-trio` SHAPE, carrying real body links".** Every existing fixture tree stays byte-identical. | The row contradicted the Phase-3 exit criterion "the existing `archive-*` / `mv-*` / `rename-*` trees stay byte-identical" in the same document. Editing them would also move M26-era assertions onto new bytes for no benefit. Copying the shape delivers the stated coverage and keeps the no-regression proof at a clean zero moved test ids. |
| 4 | **Q4's "already broken, or already escaping" clause is narrowed to "already escaping".** An already-**escaping** destination is copied byte-for-byte in every case (formula step 3). An already-**broken** but *contained* destination is copied only while its referrer stays put; when the referrer itself moves, it is **rebased to the same, still-broken target** — never repaired, never re-aimed. *Out of scope* › *Repairing pre-existing damage* and `cli.md` › *What a move never touches* are reworded to say so. | Q4's literal wording is **unimplementable** in the frozen architecture, and the frozen architecture is right. The planner is pure — it never stats — so it cannot know a contained target is missing; the only way to honour "never touched" would be a filesystem probe inside the planner, which destroys the hermeticity D4 and (L) exist to guarantee. Rebasing preserves the author's aim (the link still names the same file); *not* rebasing would silently re-aim it at a different path as the referrer's directory changes, which is strictly worse. The deviation is recorded here because three lesser ones are, and because `cli.md` ships in the bundled skill: a Phase-6 implementer reading only the author-facing spec would otherwise implement the opposite of `tests/test_move_links.py`'s pinned behaviour. |

### Step-1 resolutions (BINDING)

Eleven questions were raised by Step-1 planning. Three were operator decisions;
eight were conductor-resolved from the specs, the frozen material, or the
measured evidence. All eleven are binding; Phases 2–10 do not re-open them.

| # | Question | Resolution |
|---|---|---|
| R1 | Does a preview adopt a plan-construction failure? | **Operator. Yes.** Amendment 1 above. The frozen line: a preview adopts failures of plan **construction** and reports-but-does-not-adopt **consequence** verdicts. |
| R2 | Where is plan B's `strands` array observed, given no `--json` record on a refusal? | **Operator. In the preview.** M26's rule stands unchanged; amendment 2 above. |
| R3 | Which rewrite and strand lines print, and when? | **Operator. Everything unless `--quiet`,** in both archive shapes and in `mv`, in preview and in apply alike, with a counts footer for skimming. M26 — D1's quiet rule governs *candidate* prose only; it is not widened and not narrowed. The leg-1 **refusal** lines print even under `--quiet`, as every refusal does. |
| R4 | Does `mv --json` carry a `strands` key? | **Conductor. No — `strands` is `archive`-only.** `mv` produces no newly-archived set, so the key would be permanently `[]` and a schema wart. D7's "one schema, shared by preview and apply" is read as preview-vs-apply, which is what it literally says. Recorded as *Follow-ups* item 6: `docs mv <doc> archive/<date>/<doc>` can still strand a live child today — already a `status-drift` error, but nothing refuses it — and M28 does not change that. |
| R5 | How is the E3 fixture contradiction resolved? | **Conductor. By copying the shape, never by editing a committed tree.** Amendment 3 above. |
| R6 | What granularity does the leg-1 refusal print at? | **Conductor. One line per orphaned pair**, in deterministic order, then one summary line carrying the count, then exit 2. Matches M26's one-line-per-refusal catalogue and D6's requirement that both ends be named for **each** pair. |
| R7 | Does a directory destination keep its trailing slash? | **Conductor. Yes.** The `/` is reattached iff the original token's path part ended with `/`. M27 resolves a directory destination to an existing directory, and dropping the slash would change what the author wrote for no reason — the no-op rule's spirit applied to the one character `relpath` discards. |
| R8 | What exactly is percent-encoded on a rewritten token? | **Conductor. The grammar-derived minimal set** in item (C), `%` first, plain and angle forms differing, pinned by a parametrized decode round-trip against the scanner's own `_split_destination`. A blanket `urllib.parse.quote` is rejected: it would mangle accented and CJK filenames that need no encoding at all. Two residuals are recorded rather than hidden — see *(C) Known residuals*. |
| R9 | What does `docs mv` print when an `OSError` escapes mid-execution? | **Conductor. Exit 2 and the no-traceback guarantee are unchanged; the message is upgraded** to M26's partial-state admission shape extended by a `Rewritten:` clause. This resolves the D4-vs-D8 contradiction (D4 promises an exact partial-state admission; today `mv` prints `docs: mv: <OSError>`), no test pins the current string, and the two verbs stay symmetrical. |
| R10 | Is there a rewrite-count key in either `--json` record? | **Conductor. No.** The stderr footer keeps the count, `len(rewrites)` is derivable, and omitting it keeps the two verbs' `rewrites` sections byte-comparable. |
| R11 | Are excluded documents inside the strand-check? | **Conductor. No — and `cli.md` says so explicitly** rather than leaving it to be inferred. `[exclude]` / `.docsignore` govern the walk, so an excluded document is neither rewritten nor examined for strands, exactly as they already govern which `Related:` bullets `_rewrite_referring_edges` repoints (M26 — Q8 / M27 — D3). It is a knowable gap, so it is named. |

### (A) The move map

`moves: Mapping[str, str]`, keyed by **canonical root-relative POSIX old
path** → canonical new path.

- `docs mv` builds `{old_rel: new_rel}`.
- `docs archive` builds `{m.rel: m.dest_rel for m in plan.moves}` — the primary
  plus every selected candidate.

`ArchiveMove.aliases` is consulted **only** by the `Related:` half. The body
planner matches on the **normalised target** and therefore needs no alias list
at all (D1, E6) — every spelling that normalises to a moving document is
already a hit. The two halves are fed separately: `plan_move` takes `moves`
(canonical, for destinations) and `related_pairs` (alias-expanded, for
bullets), defaulting to `tuple(moves.items())`.

### (B) The three-step formula — BINDING order

Per recognised destination occurrence in each walked document `D`, where
`rel(D)` is its old canonical root-relative path and `new_rel(D)` is
`moves.get(rel(D), rel(D))`:

1. `classify_destination(link.raw) != "local"` → copy byte-for-byte, stop
   (Q4).
2. `old_target = normalise_body_link_target(rel(D), link.path)`.
3. `not _body_link_is_contained(old_target)` → copy byte-for-byte, stop
   (Q4 — M28 never rebases an escape and never repairs pre-existing damage).
4. `new_target = moves.get(old_target, old_target)`.
5. **The no-op test (Q5a), stated as the semantic test rather than a string
   test.** If `normalise_body_link_target(new_rel(D), link.path) ==
   new_target`, the existing spelling still means the right thing → copy
   byte-for-byte, stop. This is what makes a co-moving pair produce a
   **zero-byte** diff and what forbids normalising `./x.md` to `x.md`.
6. `new_path = posixpath.relpath(new_target, posixpath.dirname(new_rel(D)))` —
   no leading `./`. A trailing `/` is reattached iff `link.path` ended with one
   (R7).
7. The fragment is reattached verbatim after a single `#` (D3, M27 — D3).
8. The token is rendered by item (C).

The order is contractual. In particular step 5 runs **after** step 4, or a
class-2 rebase of a link to a co-moving document would be computed against the
wrong target; and steps 1 and 3 run before anything is resolved through
`moves`, or M28 would reach outside the grammar M27 validates.

Class 1 (**incoming**) is the case where step 4 fires. Class 2 (**moved
referrer**) is the case where `D` is itself in `moves`, so step 6's base
differs from step 2's. Nothing else is a case, and a document can be both.

### (C) The destination-token renderer — one strategy, no "it depends" cell

**The delimiter form is invariant.** Angle stays angle, plain stays plain. A
plain destination that cannot carry a character is **percent-encoded**, never
promoted to `<…>`.

**The encode set is derived from the grammar.** A plain destination ends at
the first unescaped whitespace or unescaped `)` at depth 0, and `(` beyond
`MAX_DESTINATION_PAREN_DEPTH` kills the link; an angle destination ends at the
first unescaped `>` on the line; `#` opens the fragment; `\` escapes; `%`
introduces an escape.

- **plain**: `%` → `%25` **first**, then space `%20`, tab `%09`, `(` `%28`,
  `)` `%29`, `#` `%23`, `<` `%3C`, `>` `%3E`, `\` `%5C`.
- **angle**: `%` → `%25` **first**, then `>` `%3E`, `<` `%3C`, `#` `%23`,
  `\` `%5C`. A space stays literal — that is what the angle form is for.
- Everything else, non-ASCII included, passes through literally. There is no
  blanket `urllib.parse.quote`.

`%` is encoded first so the introducer can never be double-encoded.

**Round-trip invariant (the lock).** `_split_destination(new_raw)` returns
`(new_path, link.fragment)` — the scanner's own decoder, run on the emitted
token, reproduces exactly what the token was built from. Phase 2 pins this
parametrized over every character in both sets.

**Reattaching the fragment cannot break the token, and the proof is one
line:** the fragment came out of a token that already parsed inside the *same*
delimiter form, so it contains no character that terminates that form. It is
therefore copied verbatim and never re-encoded.

**A rewritten token is minimally encoded.** An author's redundant escape
(`plan%2Ex.md`) is not reproduced, because the renderer works from the decoded
path. A **no-op** token keeps every byte, redundant escapes included, because
it is copied rather than rendered.

**The post-condition (BINDING): `classify_destination(new_raw) == "local"`.**
The table above is the mechanism; this is the property it exists to deliver,
and it is stated separately because the table alone does not obviously imply
it. Two entries are there for this reason and no other:

- **`#` in both sets.** A relative path whose first character is `#` would
  re-classify as `fragment` and stop being a link at all.
- **`:` → `%3A` in the first path segment** — everything before the first `/`,
  in both delimiter forms (operator decision at the Step-1 review). A first
  segment matching `[A-Za-z][A-Za-z0-9+.-]*:` re-classifies the emitted token
  as `scheme`, which means M27 stops validating it: a working link would be
  **silently** killed by the move and `docs check` would never report it — the
  exact failure class M28 exists to prevent. The rule is first-segment-only and
  that is exactly sufficient rather than conservative, because `_SCHEME_RE`
  anchors at `^` and `/` is not in its character class, so a colon after a `/`
  can never open a scheme and `sub/a:b.md` keeps its literal colon.

The post-condition's proof is complete, which is why it can be asserted rather
than hoped for: `empty` cannot occur (`relpath` never returns an empty string),
`fragment` is blocked by `#`, `root-absolute` and `protocol-relative` cannot
occur (both endpoints are in-root relative paths), and `scheme` is blocked by
the first-segment colon rule.

**Known residual (recorded, not hidden).** One input falls outside the set: **a
path component containing a whitespace character other than space or tab**
(newline, carriage return, form feed, vertical tab) is not encoded, so the
emitted plain token would terminate early. Unlike the colon, this fails
**loudly** — the truncated destination does not resolve, so `docs check`
reports it — and `docs new` never creates such a filename, no fixture or live
document carries one, and the angle form is unaffected. It stays *Follow-ups*
item 7. Phase 2 asserts nothing about it, so closing it later needs no test
flipped.

### (D) The never-creates-an-escape invariant, with its proof

`new_target` is either `old_target` — proven contained by step 3 — or a `moves`
value, which is a real in-root canonical path. For any in-root normalised `t`
and any in-root referrer path `r`,
`normalise_body_link_target(r, posixpath.relpath(t, posixpath.dirname(r))) == t`.
Containment is therefore preserved exactly, and M28 can never manufacture an
`outside-root-body-link`. The emitted spelling may contain `..` segments; what
the invariant forbids is a *normalised* result outside the root.

### (E) The per-document write pipeline — BINDING order

Forced, not stylistic: body-link spans are offsets into the text they were
scanned from, and `rewrite_related_refs` / `set_metadata_field` change lengths.

1. **Body-link splices**, applied in **descending `start`**
   (`text[:start] + new_raw + text[end:]`) — M27's Phase-6 technique, proven at
   140 occurrences over 30 documents with 30-of-30 byte-identical round trips.
2. `rewrite_related_refs(text, old_rel, new_rel)` once per `related_pairs`
   entry — line-structural, so it is safe on modified text.
3. Archive metadata edits (`Lifecycle`, `Updated`, `Archived-reason`) — moving
   members only, applied by the archive path **on top of** the planned text,
   never on a re-read of the file.
4. **One `atomic_write` per document.** Never two.

`DocRewrite.new_text` carries the result of steps 1–2 and equals `original`
when nothing changed. Step 3 is layered on by `docs archive`'s execution.

### (F) Validate-all-first (D4)

The plan is complete before the first byte moves. The rewrite-plan pre-flight
proves, over exactly the documents the plan will **write**:

- the document parses (already proven by the walk that produced the plan);
- `os.access(path, os.W_OK)`;
- `text[link.start:link.end] == link.raw` for every planned span;
- no two planned spans in one document overlap.

Every failure raises `CoordinatedWriteError(rolled_back=True, published=())`
with `exit_code=2` — a refusal, never an `assert`. Exit 1 stays reserved for
the conditions 1.x owned (M26's Q4 split, unchanged). A refusal writes zero
bytes, **the moved document included**, and emits no `--json` record.

### (G) The archived-referrer policy (D5 / A2), as ONE rule

Today `_rewrite_referring_edges` writes an archived document iff one of its
`Related:` targets is a moving `old_rel`. M28's rule is the same sentence with
one clause added:

> An archived document is written iff a `Related:` target **or a local
> body-link destination** of its resolves to a document moving in **this**
> operation — and then only that bullet and those destination tokens change.
> No `Updated:` bump, no `Revision:` bullet, no other byte.

Also frozen, because A2 discusses only archived referrers and the asymmetry
would otherwise be inventable: **no `Updated:` bump on an *active* referrer
either**, uniform with the existing `Related:` behaviour. And: an archived
document that is itself moved by `docs mv` gets class-2 rebasing of its own
destinations, under the same move-driven licence.

`convention.md`'s M27 — D6 paragraph now says M28 leaves the exception count at
three, because M28 — D5 widens M18's along its own axis instead of adding a
fourth — otherwise the convention would contradict itself the moment M28 ships.

### (H) The strand-check, both legs — `archive` only

**Source set (both legs):** every walked document `D` with `rel(D) not in
moves` **and** `not _is_archived_rel(rel(D), config)`. Plan members are exempt
(a document being archived cannot be stranded); already-archived documents are
not "still active"; `[exclude]` / `.docsignore` govern the walk, so an excluded
document is neither examined nor reported (R11).

**Leg 1 — refusal.** Fires when such a `D` declares `child-of: T` with
`_canonical_related_target(T) in moves`. Exit **2**, before any write, both
ends named per pair, printed even under `--quiet`. Applies to **all three**
archive shapes, including a plain `docs archive FILE`.

**Leg 2 — report.** Every other still-active inbound reference: any other
`Related:` verb, free-form verbs included, whose canonical target is in
`moves`, and every body link whose `old_target` is in `moves`. Reported, never
refused.

**Leg 2 is not a damage report.** Those references are *repaired* by the same
operation; what is reported is the post-plan consequence "active `X` still
points at newly-archived `Y`". `cli.md` says so, because every reader would
otherwise misread it.

**Ordering (deterministic):** referrer walk order; within a referrer,
`Related:` bullets in declaration order, then body links in `(line, column)`
order.

**Preview:** reports both legs' verdicts and exits **0** — it reports leg 1
rather than adopting it (D6).

**`docs mv` runs neither leg** (R4). A rename produces no newly-archived set.

### (I) Check order — write-path precedence unchanged, preview extended

`docs archive`, preserving M26's message-precedence decisions **exactly**:

1 retired flags → 2 scope shape → 3 root/config/`--date`/primary → 4 archived
primary → 5 archive plan built → **5b preview branch: whole-tree walk, rewrite
plan, strand analysis; prints candidates, rewrites, strands and the leg-1
verdict; exit 0** → 6 empty-selection refusal → 7 member pre-flight → 8
whole-tree walk (unchanged position) → **8b rewrite plan + strand analysis** →
**8c rewrite-plan pre-flight (F)** → **8d leg-1 refusal** → 9 execution.

The walk sits at **5b for the preview and at 8 for the write path**, and that
split is deliberate. `cli.md` states, and M26 froze, that "the plan pre-flight
deliberately precedes the whole-tree walk … naming the document the operator
actually asked for is strictly more actionable than naming an unrelated
referring doc". Building the rewrite plan at 5b on the *write* path would have
inverted that precedence: an unwritable member and a malformed referrer would
swap messages, and — on a tree that is **also** malformed — a `--cascade-only`
write selecting nothing would exit 1 instead of 2. The message-precedence
inversion alone carries the justification. M28 changes no message precedence
M26 froze.

**What the split costs, stated rather than left to be discovered.** The preview
no longer previews the *write path's* precedence: a plan whose planned referrer
is unwritable **previews at exit 0 and prints the plan**, while the write
refuses at exit 2 at step 8c. That is defensible — a preview writes nothing, so
writability is irrelevant to it — but it is the same shape as M26 — *Follow-ups*
item 2, so it is **named in `cli.md`** rather than left for an operator to hit.
It is also exactly the boundary amendment 1 draws: plan *construction* is
adopted by the preview, plan *consequences* and plan *permissions* are not.

`docs mv`: 1 `<old>` is a file (exit 1) → 2 `<new>` exists (exit 1) → 3
root/config (exit 2) → 4 both under root (exit 2) → **5 whole-tree walk +
rewrite plan** → **5b preview branch: prints rewrites; exit 0** → 6
rewrite-plan pre-flight → 7 execution: the moved document's planned text is
written to its **old** path, then `replace`, then every other planned
document, then one `_refresh_index`.

**Where the moved document lands in a partial-state admission.** Writing its
rebased text before the `replace` means a `replace` that raises leaves the old
path holding text whose links are rebased for a directory the file is not in.
The admission must say so: the moved document is reported under `Moved:` **iff
the `replace` succeeded**, and under `Rewritten:` otherwise — so that failure
renders as `Moved: none. Rewritten: <old-rel>. Not written: <…>.` and names the
one document an operator has to inspect.

Two consequences, written down rather than discovered: `mv --dry-run` now
walks, so a malformed tree turns its exit 0 into exit **2**; and
`archive --cascade-dry-run` now walks, so a malformed tree turns its exit 0
into exit **1**. Both are amendment 1.

### (J) Frozen message catalogue

Every new message is prefixed `docs: mv: ` / `docs: archive: `; every path is
canonical root-relative POSIX; every interpolated author token passes through
`_one_line` so a percent-decoded control character cannot split a line
(M27 — N2). `<doc-rel>` is the referrer's **old** canonical path and `<line>`
indexes into the text the plan was computed from.

```
docs: mv: would move <old-rel> -> <new-rel>
docs: mv: moved <old-rel> -> <new-rel>
docs: mv: rewrite <doc-rel>:<line> <old-token> -> <new-token>
docs: mv: <R> destination(s) in <D> document(s), <E> Related: bullet(s)
docs: mv: preview only — nothing was written
docs: mv: <rel> is not writable; refusing before any write
docs: mv: write failed for <rel>: <err>; PARTIAL MOVE — not rolled back. Moved: <old-rel> -> <new-rel>. Rewritten: <rel>, <rel>. Not written: <rel>. Repair manually.

docs: archive: rewrite <doc-rel>:<line> <old-token> -> <new-token>
docs: archive: <R> destination(s) in <D> document(s) rebased
docs: archive: strand <src-rel> — still active, '<verb>: <dst-rel>'
docs: archive: strand <src-rel>:<line> — still active, links to <dst-rel>
docs: archive: <N> still-active inbound reference(s) into the archived set
docs: archive: <child-rel> is still active and declares 'child-of: <parent-rel>', which this operation would archive; refusing before any write
docs: archive: <N> still-active child(ren) would be stranded; zero bytes written
docs: archive: would strand <child-rel> — still active, declares 'child-of: <parent-rel>'; a write would refuse
docs: archive: <N> still-active child(ren) would be stranded
```

The last two lines are the **preview's** leg-1 pair; the two before them are
the **write path's**. Each of `Moved:` / `Rewritten:` / `Not written:` renders
the literal word `none` when its list is empty, never a blank (the M25
`_rollback_relate` lesson, and M26's `_archive_partial_state` precedent).

Everything prints unless `--quiet`, in preview and apply alike (R3), except
the two leg-1 **refusal** lines, which print even under `--quiet` as every
refusal does.

**Two of these are RE-SPELLINGS of shipped lines, not new messages.** `docs mv`
prints `docs: would move <old> -> <new>` and
`docs: moved <old> -> <new> (<N> reference(s) rewritten)` today. Both gain the
`mv: ` verb prefix, matching every other verb, and the second **drops its
trailing count**, which moves into the richer counts footer. No test pins
either string (grep-verified), so nothing goes RED — but anyone parsing
`docs mv` stderr breaks silently at 2.0, so the Phase-7 upgrade note and the
`UNRELEASED` CHANGELOG must name this alongside "a move now edits prose" and
"an archive now refuses".

### (K) `--json` schemas

`archive --json`'s closed top-level key set widens by **exactly two** —
`rewrites` and `strands` — inserted after `candidates`. Phase 2 asserts exactly
that and nothing else moves.

```json
"rewrites": [
  {"path": "status.md", "line": 412, "column": 5,
   "old": "m26-safe-archive-selection.md",
   "new": "archive/2026-08-15/m26-safe-archive-selection.md"}
],
"strands": [
  {"path": "status.md", "target": "m26-safe-archive-selection.md",
   "kind": "related", "verb": "pairs-with", "line": null},
  {"path": "plan.md", "target": "m26-safe-archive-selection.md",
   "kind": "body-link", "verb": null, "line": 118}
]
```

- `rewrites[]`: `path` is the referrer's **old** canonical root-relative POSIX
  path; `line` / `column` are 1-based, of the destination token's first
  character in the text the plan was computed from; `old` is `link.raw`
  (exactly as written, delimiters and escapes included); `new` is the emitted
  token, delimiters included. Order: walk order, then ascending
  `(line, column)` within a document. Key set closed and ordered as shown.
- `strands[]`: `MOVE_STRAND_KINDS = frozenset({"related", "body-link"})`.
  `verb` is null **iff** `kind == "body-link"`; `line` is null **iff**
  `kind == "related"` (`Doc.related` carries no line). `target` is the
  document's **old** canonical path — the one the referrer names today. Key set
  closed and ordered as shown.
- Both arrays are **present and `[]`** when empty, never missing.
- No record is emitted on any refusal, including M28's two new ones (M26's
  frozen Phase-1 Q3 rule, unchanged). A plan that leg 1 would refuse is
  observed in its preview (amendment 2).

`mv --json` — a new record, the same shape for preview and apply:

```json
{"old": {"source": "docs/plan.md", "path": "plan.md"},
 "new": {"source": "docs/milestone-plan.md", "path": "milestone-plan.md"},
 "rewrites": [],
 "dry_run": true, "applied": false, "index_refreshed": false}
```

`source` is the argument **exactly as typed** (mirroring `archive`'s
`primary.source`); `path` is canonical. The `rewrites` array is produced by the
**same serializer** as `archive`'s, so the two are byte-comparable (R10). There
is no `strands` key (R4) and no count key (R10). Top-level key set closed and
ordered as shown.

### (L) Frozen Phase-5 signatures

```python
MOVE_STRAND_KINDS: frozenset[str]        # "related", "body-link"

@dataclass(frozen=True)
class LinkRewrite:
    link: BodyLink          # M27's record verbatim — never re-derived
    old_target: str         # canonical root-relative, from the OLD referrer dir
    new_target: str         # after the move map
    new_raw: str            # replacement destination token, delimiters included

@dataclass(frozen=True)
class DocRewrite:
    path: Path
    rel: str                # OLD canonical root-relative POSIX
    new_rel: str            # == rel unless this document moves
    archived: bool
    original: str           # the text the plan was computed from
    new_text: str           # after (E) steps 1-2; == original when nothing changes
    links: tuple[LinkRewrite, ...]      # ascending start
    related_rewrites: int

@dataclass(frozen=True)
class Strand:
    path: str; target: str; kind: str; verb: str | None; line: int | None

@dataclass(frozen=True)
class MovePlan:
    root: Path
    config: Config
    moves: Mapping[str, str]
    rewrites: tuple[DocRewrite, ...]    # ONLY documents whose bytes change, walk order
    strands: tuple[Strand, ...]         # leg 2
    orphans: tuple[Strand, ...]         # leg 1, kind == "related", verb == "child-of"

def plan_body_link_rewrites(rel: str, new_rel: str, text: str,
                            moves: Mapping[str, str]) -> tuple[LinkRewrite, ...]
def render_destination_token(raw: str, new_path: str, fragment: str | None) -> str
def splice_body_links(text: str, rewrites: Sequence[LinkRewrite]) -> str
def plan_move(root: Path, config: Config, *, entries: Sequence[tuple[Doc, str]],
              moves: Mapping[str, str],
              related_pairs: Sequence[tuple[str, str]] | None = None,
              strand_check: bool = False) -> MovePlan
def preflight_move_plan(plan: MovePlan) -> None            # raises CoordinatedWriteError
def apply_move_plan(plan: MovePlan) -> None                # non-moving documents only
def move_plan_to_json(plan: MovePlan) -> dict[str, object]  # {"rewrites": [...], "strands": [...]}
def _print_move_lines(plan: MovePlan, *, verb: str, dry_run: bool) -> None
```

Four points the plain signatures do not carry:

- `plan_body_link_rewrites` is **pure** — no filesystem access of any kind.
  Phase 2 locks it with monkeypatched `Path.exists` / `Path.is_file` / `open`
  sentinels (M27's precedent).
- `plan_move` takes `entries` as `(Doc, text)` pairs, so the walk is the
  caller's and the planner reads nothing. `related_pairs` defaults to
  `tuple(moves.items())`; `docs archive` passes the alias-expanded pairs
  (A, M26 — Q5). `strand_check` is False for `docs mv` (R4).
- `move_plan_to_json` returns the **shared section** — `{"rewrites": [...],
  "strands": [...]}` — and each verb splices what it carries into its own
  record: `mv` takes `rewrites` only, `archive` takes both, inserted after
  `candidates`. One serializer is what makes the two byte-comparable (R10).
- **A moving member is ALWAYS present in `rewrites`**, with
  `new_text == original` when nothing about it changed; `rewrites` otherwise
  carries only documents whose bytes change. Without this the common case —
  `docs mv a.md b.md` on a document with no body links and no self-edges —
  leaves the moved document with no `DocRewrite` at all, which makes (E)'s
  "`new_text` == `original` when nothing changes" unreachable and (I)'s mv
  execution step ("the moved document's planned text is written to its **old**
  path") undefined.
- `apply_move_plan` writes every **non-moving** document whose text changed,
  one `atomic_write` each, and **never** a moving member. That is the verb's
  own business — the two verbs relocate differently — and each verb takes that
  member's final text from its `DocRewrite`, never from a re-read (E).
- `_print_move_lines` prints the rewrite lines, the counts footer and leg 2.
  The leg-1 **refusal** lines are the verb's, because they print under
  `--quiet` and precede a non-zero return.

`_rewrite_referring_edges` is **superseded** by `apply_move_plan` and deleted
in Phase 6/7 on M26's `_cascade_set` precedent — not in Phase 1.

**Reuse — no new machinery.** Scanner `scan_body_links`; classification
`classify_destination`; resolution `normalise_body_link_target`; containment
`_body_link_is_contained`; decode `_split_destination`; canonical rel
`_root_relative` and `_canonical_related_target`; archived test
`_is_archived_rel`; `Related:` edit `rewrite_related_refs` **unchanged**;
failure carrier `CoordinatedWriteError`; write `atomic_write`; walk `walk` with
`compile_exclude_predicate`; message hygiene `_one_line`; reindex
`_refresh_index`. M28 adds no second Markdown parser, no regex over
destinations, and no dependency.

### (M) Authoring traps — restated, because M28's subject *is* link syntax

1. The literal substring `](../` is forbidden in `cli.md` and
   `convention.md`, fences included, because both are copied byte-identically
   into the bundled skill. M28 wants to write a `../../plan.md` worked example
   in link form; it must not. Rewritten destinations are written as bare paths
   in inline code or in a table, never in link form. Both files are at **0**
   occurrences and stay there.
2. `../src/docs_cli/` and `../../../../docs/` are forbidden in the same two
   files.
3. Every link-shaped example lives in a fence or an inline code span, or it
   becomes a real scannable span and can break the dogfood `docs check`.
   Nothing may become a real reference definition — a line-anchored
   `[x]: y.md` in unfenced prose.

## Follow-ups recorded for later milestones

Raised during setup, judged out of M28's scope, and deliberately **not**
implemented here.

| # | Follow-up | Home |
|---|---|---|
| 1 | **`docs migrate --apply` rewrites references across its own moves** (Q6) — `Related:` bullets and body-link destinations alike. Today the adoption workflow moves archive-shaped files and repairs neither, so a freshly adopted tree can fail its first `docs check` on damage the adoption caused. | Later |
| 2 | **Images join the validated grammar** (M27 *Follow-ups* item 1). Still a one-character change to the matcher, still deliberately excluded — and now it would widen the *rewrite* surface as well as the validation surface, which is what M27 predicted. | Later |
| 3 | **Duplicate `Related:` bullets from alias rewriting** (M26 *Follow-ups* item 3, re-deferred here — Q7). Needs `Related:`-block-aware editing, which M28's destination splicer does not provide. | Later |
| 4 | **Rolling back an interrupted execution batch** — M25 — D5's staged-publish-plus-rollback extended to N documents. Declined by M26 — D4, still declined here, still available. | Later |
| 5 | **Heading/anchor validation for fragments**, out of scope for M27 *and* M28 by the 2026-08-10 operator decision, and now also out of scope for rewriting: M28 carries a fragment across a move without ever resolving it. | Later |
| 6 | **`docs mv <doc> archive/<date>/<doc>` can still strand a live child** (Phase 1, R4). The strand-check is `archive`-only because only `archive` produces a newly-archived set, and `mv` into the archive subtree is already a `status-drift` error the operator has to repair — but nothing *refuses* it before the write. Extending leg 1 to a `mv` whose destination lands under the archive subtree is a small, self-contained follow-up. | Later |
| 7 | **One residual in the destination encode set** (Phase 1, R8 / item (C) *Known residual*): a path component carrying a whitespace character other than space or tab — newline, carriage return, form feed, vertical tab — is not encoded, so the emitted plain token would terminate early. It fails **loudly** (the truncated destination does not resolve, so `docs check` reports it), no filename this tool creates carries one, and the angle form is unaffected. The colon case that sat here at Phase 1 was **closed in Phase 1** by operator decision at the Step-1 review — it failed *silently*, which is the failure class M28 exists to prevent — and is now item (C)'s first-segment `:` rule under the `classify_destination(new_raw) == "local"` post-condition. | Later |

## Testing and quality gate

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q
.venv/bin/docs check --root docs
```

Additional gates: a post-move `docs check` clean assertion for every mutation
flow; byte-identity assertions on every refusal path and on every document a
move must not touch; an idempotence lock (an equivalent second move changes
nothing); the strand-check's **leg-1 over-fire lock** (a legitimate closeout
completes) and its **leg-2 report lock** (every non-refusing still-active
inbound reference named, both ends, in prose and in the `strands` array); a
`mv --json` / `archive --json` preview-equals-apply shape assertion; the closed
four-key `Finding` record; `docs mv --help` / `docs archive --help` / `cli.md`
surface parity; bundled `references/cli.md` and `references/convention.md` byte
identity; the pre-M28 fixture-tree no-new-findings locks; and the live INDEX
snapshot.

## Success criteria

- Both move classes stay valid across nested single moves, batch moves, and a
  document that moves while linking to another document moving in the same
  operation — proven by `docs check` exiting 0 after each of E1's, E2's and
  E3's reproductions, which today produce 42, 13 and 6 hard errors.
- Only destination tokens change in prose. Labels, titles, quoting form,
  fragments, code, examples, external URLs, plain-text mentions and every
  unrelated byte are identical afterwards, verified by a byte-level review of
  every changed line and by round-trip reconstruction.
- A destination whose meaning the move did not change keeps its original
  spelling, byte for byte.
- Archived referrers keep resolving under the D5 policy, with **nothing but
  the move-driven destination token** changed in them (Q2): no `Updated:` bump,
  no `Revision:` bullet, and `Lifecycle:`, `Archived-reason:`, the H1, the
  prose and every non-moving edge byte-identical.
- A handled validation or write failure leaves **zero** bytes written,
  including the moved document; only an unexpected mid-execution `OSError`
  produces a partial state, and it is admitted exactly.
- **Leg 1:** a plan that would archive a document a still-active document
  declares itself `child-of` refuses before any write, names both ends, and
  reports the identical verdict in the preview at exit 0 — while a legitimate
  milestone closeout on this repository's own tree **completes**, with zero
  false positives measured across plan A.
- **Leg 2:** every other still-active inbound reference into the newly-archived
  set — any other `Related:` verb and every body link — is named, with both
  ends, in the preview, in the apply output, and in the record's `strands`
  array, on plans that complete as well as on plans that refuse. The report is
  a deliverable in its own right, because it is what answers issue #1
  finding 1's actual complaint.
- `docs mv --dry-run` names every planned rewrite instead of one line, and
  `docs mv --json` and `docs archive --json` emit one rewrite-plan record whose
  shape is identical for a preview and a real apply.
- `docs mv` and a scoped `docs archive` each end with `docs check` clean and
  one deterministic INDEX refresh, and re-running an equivalent move changes
  nothing.
- All pre-M28 fixture trees and the bundled skill gain zero findings, and the
  M12, M18, M25 and M26 behaviours are proven byte-stable.
- Full quality, compatibility and dogfood gates are GREEN, leaving M28a and
  M29 ready to prepare next.
