# M28a — Structured archive-date witness

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-08-16

Related:
- child-of: plan.md
- parent-of: m28a-archive-date-witness-impl.md
- implements: charter.md
- pairs-with: m28a-archive-date-witness-impl.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: test-strategy.md
- pairs-with: status.md
- references: feedback-log.md
- follows: m28-move-safe-body-link-rewrites.md
- precedes: m29-pypi-publish-2-0-0.md
- depends-on: m26-safe-archive-selection.md
- required-by: m29-pypi-publish-2-0-0.md

## Overview

- Milestone: M28a (v2.0 train)
- Title: Structured archive-date witness
- Surface: **two legs.** `docs archive` records the archive date as a
  structured `Archived:` field on every document it moves, and `docs check`
  gains a rule reporting a document whose recorded archive date its location
  does not corroborate (**detect**); `docs mv` refuses a move whose source and
  destination are different dated archive directories, before it writes
  anything (**prevent**).
- Progress: **Step 1 (Phases 1–4) complete — contract 2026-08-15; RED tests,
  fixtures and the classified baseline 2026-08-16. Step 2 (Phases 5–10) is in
  flight on `m28a/phases-5-10`: Phase 5 — Update Base Interfaces complete
  2026-08-16 (the vocabulary entry, `parse_date`'s keyword-only `label` and all
  three pure helpers, wired nowhere; 43 ids flipped, suite 28 failed / 1474
  passed), and Phase 6 — Implement Offline/Core Path complete 2026-08-16 (the
  three touch points — the writer, the rule and Leg 2's refusal; 26 ids
  flipped, suite 2 failed / 1500 passed with only the two bundled-skill ids
  left), and Phase 7 — Update Tool/Wrapper Layer complete 2026-08-16, taking
  the suite fully **GREEN at 1502 passed / 0 failed**, and Phase 8 — Run Tests
  (GREEN) complete 2026-08-16 with every gate clean and 0 of the 1341
  pre-existing ids removed or failing, and Phase 9 — Integrate / Accept /
  Dogfood complete 2026-08-16 across ten flows on throwaway copies. Phase 10 —
  Quality, Docs, Refactor is next.** The machine-facing contract is
  frozen in *Decisions (Phase 1 — BINDING)* below, with **six** amendments to
  setup-frozen material and nine Step-1 resolutions (OQ-1 … OQ-9, one of them
  an operator decision). Phases 2–4 authored **149** test ids and six
  `archivedate-*` fixture trees against it — 131 in Phase 2, five more at the
  same-instance audit and thirteen at the fresh-eyes fold-in, which closed the
  one wrong implementation the suite had not caught (a config-blind Leg-2
  predicate). The suite stands at **1502 collected, 71 RED and 90 GREEN** of
  the 161 new ids, in exactly two exception classes, with **no** pre-existing
  id removed or failing and `cli.py` untouched. M28 is implementation-complete
  and merged to `main` (`b1ec74b`), so M28a is the last implementation
  milestone in the v2.0 train before the M29 publish. Setup measured this
  repository read-only and reproduced the reported drift on throwaway copies,
  producing nine pieces of evidence (**E1–E9**). Two of them reshape the
  milestone. **E1** enumerates all four ways a document can move relative to
  the archive subtree and finds that **exactly one is silent** — and that it
  is reachable through a shipped verb in one command, which corrects the
  registered stub's claim that the tool already prevents this (*Decisions
  recorded at setup* › *A1*). **E2** replays that one command against the
  pre-M28 CLI and against merged `main`: **13 hard errors and exit 2 before,
  zero findings and exit 0 after** — M28 removed the tree's only, accidental,
  alarm for this class of damage. **M28a is therefore a consequence of M28,
  not an independent idea, and that is why it blocks M29**: shipping M28 in
  2.0.0 without M28a would leave the release **strictly quieter about
  archived-document relocation than 1.8.0 was**. **All seven setup questions
  are RESOLVED** — **Q4** by operator decision (adopt **both** legs, so the
  refusal is binding scope rather than an option) and **Q1** auto-resolved to
  `Archived:` under the naming-with-an-obvious-default rule; Q2, Q3, Q5, Q6
  and Q7 conductor-resolved. Phase 1 freezes the contract against those
  answers and does not re-open scope.

### Numbering note

This milestone is `M28a`, not `M30`, because it is an insertion between M28 and
M29 rather than an extension of the train's tail. Renumbering M29 would have
required editing the completed M25, M26 and M27 milestone docs and
implementation logs — closed historical records — in 100 places. Execution
order is carried by the reciprocal `precedes` / `follows` edges, not by the
number, so the ordinal only has to be readable, not arithmetic.

### Goal

Make an archived document's location provable against its own metadata, so that
a relocated archived document is detectable by the tool instead of being
invisible.

### Primary use-case acceptance

- **Close out a milestone and keep the evidence.** An agent archives a
  completed pair with `docs archive FILE --cascade-only GLOB`. **Every**
  document the operation moves — the primary and each selected candidate —
  carries the archive date as a structured field, so the set's own metadata
  records the event that created it, not just the directory it happens to sit
  in.
- **Refuse the relocation the tool itself performs.** `docs mv` given a
  source and a destination in two different dated archive directories refuses
  outright — exit 2, both dates named, **zero bytes written** — for every
  archived document, whether or not it carries the witness. The escape for a
  genuinely mis-dated archive is documented in the same breath as the refusal.
- **Catch a relocation the tool cannot prevent.** A document archived on one
  date and later moved into a different dated archive directory by something
  other than `docs mv` — a hand `git mv`, a bulk script, an `rsync`, or any
  future defect — is reported by `docs check` as a hard error naming both the
  recorded date and the directory it now sits in. A document archived normally
  is silent.
- **Upgrade without a repair queue.** A 1.x tree upgrading to 2.0.0 gains
  **zero** findings from this rule. Every document archived before the witness
  existed stays silent forever, because the rule fires only on documents that
  carry the field.
- **Never cry wolf.** On this repository's own tree — 46 archived documents
  across 13 dated directories, including 7 deliberate cross-milestone
  `pairs-with` edges that span different dated directories — the rule emits
  nothing.

## Binding scope

The nine decisions below are binding for M28a, and **all seven setup
questions are resolved**. Each decision carries the question it resolves; the
reasoning is in *Setup questions (Q1–Q7)*, and the two answers that changed
something already written down are restated in *Decisions recorded at setup
(BINDING)*. Phase 1 makes them exact and does not re-open them.

M28a has **two legs**, and the operator's answer to Q4 made both binding:
**D3 detects** drift for documents that carry the witness, and **D5 prevents**
the one relocation the tool itself performs, for every archived document
whether or not it carries one. They are complementary, not alternative.

### D1 — A new structured field, because neither existing field can carry the witness

The archive date is recorded as a **new** metadata field, **`Archived:`**
(Q1, BINDING), written by `docs archive`, whose value is the **same
`date_str`** that names the dated archive directory the document is moved
into — one value, one source, rendered once in the tree's `[archive]
date_format`.

**The name is permanent.** `convention.md` states that `.docs.toml` may *add*
to vocabularies but **never remove or rename built-ins**, so from the moment
2.0.0 ships this label cannot be changed — it is fixed here deliberately
rather than discovered in Phase 1. `Archived:` mirrors `Updated:`'s
established shape (a date-valued past participle that does not name its own
type) and pairs with `Archived-reason:` as event and reason:

```
Updated: 2026-08-15
Archived: 2026-08-15
Archived-reason: Milestone M26 complete
```

**`Archived-date:` is the rejected alternative.** It is unambiguous against a
boolean reading and morphologically parallel to `Archived-reason:`, but
`Updated:` is already a date-valued past participle in the same block, so the
ambiguity is one this convention has never had — and `-date` would make it the
only field in the vocabulary that names its own type. `Archive-date:` loses on
both counts. Setup measured **zero** occurrences of any `Archived:` label
anywhere (E6), so no spelling collides with existing data.

It has to be a new field, and this is measured rather than assumed:

- **`Updated:` cannot be it.** The archive move bumps it; M27 — D6's one-time
  body-link migration bumped it on 29 archived documents, which is why **29 of
  this tree's 46** archived documents now carry an `Updated:` value that
  differs from their dated directory; and an ordinary `docs touch` on an
  archived document bumps it again at exit 0 with `docs check` clean (E3). A
  value any verb may move cannot corroborate a location.
- **`Archived-reason:` cannot be it.** It is free text, and M26 — D1 writes it
  to the **primary only**, so it covers 13 of this tree's 46 archived
  documents (E4).

The vocabulary consequences are small and enumerated, so Phase 1 can freeze
them and Phase 7 cannot miss one:

- The label joins `_BUILTIN_METADATA_FIELDS`, for exactly the reason M25 added
  `Revision:` — *a label the tool writes must never trip the tool's own
  allowlist warning*. It is therefore unaffected by `[vocabulary] add_fields`,
  which stays opt-in and off by default (E6).
- It stays **out of** `parse()`'s `known` set, so it surfaces through
  `docs list --json` under `extra_fields` exactly as `Archived-reason:` and
  `Revision:` already do. M28a adds no field to any JSON record.
- Its **position in the metadata block is pinned**, because nothing else pins
  it: there is no field-order list and no `field-order` rule, and
  `set_metadata_field` appends a new inline label at the end of the inline run
  (E7). `_archive_one` writes it **before** `Archived-reason:`, so an archived
  document reads `Lifecycle:` / `Role:` / `Project:` / `Updated:` /
  `Archived:` / `Archived-reason:` — the date, then the reason for it.

### D2 — Written to every document an archive operation moves, not to the primary only

This is the one place M28a deliberately does **not** copy `Archived-reason:`.
The reason explains why *this archive was requested*, so M26 — D1 confines it
to the named primary. The date is a fact about **each document's own move**, so
it is written to the primary and to every selected cascade candidate alike.

The evidence is the reported case itself: issue #1's real-tree replay was *a
coherent archived trio split across two dated directories*, and a trio's
non-primary members are exactly the documents that would carry nothing under a
primary-only rule. A witness that covers 28% of archived documents (E4) is not
a witness.

Mechanically this is free: `_archive_one` already receives `date_str` for every
member, while `apply_archive_plan` special-cases only the reason
(`plan.reason if index == 0 else None`). The field is written uniformly and the
special case is not touched.

### D3 — Leg 1 (detect): `archive-date-drift`, a corroboration test decided by path arithmetic alone

The rule asks one question: **does this document's location corroborate the
archive date it records?**

A document's location corroborates its recorded date when **all** of the
following hold, computed from the canonical root-relative path and the tree's
config, with no filesystem access of any kind:

1. the path's first segment is the configured `[archive] dir`;
2. the segment immediately after it parses, in the tree's `date_format`, as a
   date;
3. that date **equals** the parsed value of the recorded field.

Anything else is a finding. Two non-corroborating shapes exist and both are in
scope (Q7):

- **A different dated directory** — the headline case, and the only one that is
  silent today (E1d).
- **No dated directory at all** — the document is not under the archive
  subtree, or sits under an undated subdirectory of it. Its recorded date has
  no corroborating location.

Three properties bind the predicate:

- **Comparison is on parsed dates, never on raw strings** (Q2). `date_format`
  is configurable, and M25 already settled that a document must not carry two
  date spellings — *"the ISO spelling below is the default format, not a
  second hardcoded one (two date spellings in one file would be a defect)"*.
  M28a adds neither a third spelling nor a fourth parser. A recorded value that
  does not parse in the tree's `date_format` is a **`bad-date`**-shaped
  condition, not a drift finding; Phase 1 pins which rule owns it.
  **Both sides of the comparison are parsed with `config.date_format`**, via
  the same `parse_date` path `check_doc` already uses for `Updated:` — never
  through `parse()`'s hardcoded default. That is deliberate: E8 measures a
  pre-existing defect on exactly that hardcoded path, M28a does **not** fix it
  (*Follow-ups* item 1), and M28a's own logic must not inherit it.
- **It is config-aware.** The only dated-archive-directory parser in the
  codebase today, `detect_archive_layout`, is hardcoded to the literal
  `"archive"` and `"%Y-%m-%d"`, ignores `Config`, and lives in the migrate half
  (E7). M28a adds a config-aware sibling honouring `config.archive_dir` and
  `config.date_format`; it does not add a fourth copy of a config-blind
  predicate.
- **Deeper paths still corroborate.** Corroboration reads the **first** segment
  under the archive directory, matching how `status-drift` and
  `_is_archived_rel` already treat the subtree, so `archive/<date>/sub/x.md`
  corroborates `<date>`.

`archive-date-drift` and `status-drift` are **independent** and may both fire
on one document. They report different facts — a lifecycle that disagrees with
a location, and a recorded date that does — and the case that motivates the
rule (a document moved out of the archive whose `Lifecycle:` is then
hand-edited) is precisely the one where `status-drift` is silent. This is a
deliberate departure from M27's non-overlap rule, which applied because that
milestone's two rules were mutually exclusive *classifications of one
destination*, not two independent assertions about one document (Q7).

### D4 — Hard error, exit 2, one finding per document, closed record, no opt-out

The `status-drift` / `broken-body-link` shape, unchanged:

- `severity: error`, exit code 2. The condition is objective — two tool-written
  facts disagreeing — which is the standard M27 applied when it declined an
  opt-in flag for body links, and it is the feedback log's own recorded
  principle: *the tool should refuse what it can prove is wrong*.
- **One finding per document**, not per condition. A document has one recorded
  date and one location.
- **The `Finding` record's key set stays closed** at `{path, severity, rule,
  message}`. M27 — D4 already froze the rule: *a new rule adds a value to
  `rule`, never a field to the record.* Both dates travel in `message`, which
  is what an agent parses to repair.
- **No `.docs.toml` opt-out.** M27 — Q6 declined one for an objective rule and
  the same answer holds here. `[exclude]` / `.docsignore` remain the only
  (coarse) escape, and they govern the walk, never the predicate.
- **Per-document only.** No graph traversal, no comparison against a document's
  `pairs-with` partners, no second `check_tree` pass. The rule needs this
  document's own metadata, its own path, and the tree's config.

### D5 — Leg 2 (prevent): `docs mv` refuses a cross-dated archived relocation, before it writes

**Q4, operator decision: M28a ships both legs.** D3 *detects* drift for
documents that carry the witness. This leg *prevents* the one relocation the
tool itself performs — for **every** archived document, whether or not it
carries the field.

It exists because A1's measurement says it must. `docs mv archive/<D1>/x.md
archive/<D2>/x.md` completes at exit 0 today, rewrites every stale reference so
nothing dangles, and leaves `docs check` clean (E1d). The witness cannot reach
that case for the 46 documents this tree archived before the field existed, nor
for any tree upgrading from 1.x — so without this leg the tool would keep
offering a command that silently falsifies the only archive-date record those
documents have.

**The predicate, decidable from the two paths alone.** The move refuses when
the source **and** the destination are both under the configured `[archive]
dir`, and the first path segment under it parses, in the tree's `date_format`,
to **different** dates. Nothing else is examined: no metadata, no filesystem,
no graph — the same path-arithmetic discipline D3 uses, and deliberately
independent of whether the moving document carries the witness.

**What it does not refuse**, stated so the predicate cannot creep:

- a rename **within** one dated archive directory — the basename changes, the
  date does not;
- a move whose source or destination is outside the archive subtree — those are
  the two loud paths `status-drift` already catches at exit 2 (E1b, E1c), and
  this leg does not double-report them;
- a move whose two segments do not **both** parse as dates in the tree's
  `date_format` — there is no pair of dates to disagree;
- every other existing `docs mv` behaviour, unchanged.

**It reuses M28's machinery and invents nothing.** The refusal is evaluated in
`docs mv`'s existing plan-before-move window — the window M28's pre-flight
occupies, one step earlier: immediately after the two root-relative paths are
derived and **before** the `--dry-run` branch, so it refuses in every mode
rather than letting a preview print `would move …` for an operation the apply
refuses (Phase-1 amendment 2). That window already guarantees a handled failure
writes **zero bytes**, including the moved document itself. Exit 2, before the
first byte moves, naming both dates. There is no second refusal mechanism, no
new flag, no new JSON key and no opt-out. Its message is frozen in Phase 1 beside `archive-date-drift`'s and
pinned by locks the same way.

**The escape is documented in the same paragraph as the refusal**, in both
`cli.md` and `convention.md`, so the refusal never reads as a dead end. An
operator correcting a genuinely mis-dated archive moves the file by hand,
corrects the recorded date to match its new directory, and re-runs
`docs check` — which then confirms the two agree. The refusal blocks the
*silent* path, not the deliberate one. The narrower alternative — refuse only
when the moving document carries the witness — was considered and rejected: it
makes the refusal depend on the very field whose absence is the problem, and
leaves the pre-2.0 population unprotected, which is the whole reason for this
leg.

### D6 — Present-only, and that is the entire compatibility story

The rule fires **only when the field is present**. A document that does not
carry it produces nothing, ever.

This is not a mitigation bolted onto the design; it is the design. Every
document archived before 2.0.0 — 46 in this repository, an unknown number in
every adopter's tree — was archived by a tool that never wrote a witness, and
no honest value can be reconstructed for them. So:

- **A 1.x tree gains zero findings from this rule on upgrade.** M28a is the
  only rule in the v2.0 train with that property, and it is the reason the rule
  can be a hard error at all.
- **There is no backfill and no migration** (Q3). `docs archive` refuses an
  already-archived primary (E1a) and M26 — Q4 excludes already-archived
  candidates, so no code path could backfill honestly; inventing a date is
  precisely the falsification this milestone exists to prevent. M27 — D6 is the
  precedent and the boundary: that migration was performed once, by the
  milestone, and `convention.md` records that **no CLI verb performs it**.
- **Coverage grows by use, not by sweep.** Every future archive event writes
  the witness for the documents it moves; the historical population stays
  silent.

### D7 — `docs migrate` never writes the witness, and never promotes a foreign one

`docs migrate --apply` is a **third** file mover: it relocates archive-shaped
files into `archive/<date>/`, and — absent an in-file `Lifecycle:` line
carrying a built-in value — it defaults a document to `Lifecycle: archived`
purely because the first path segment is `archive` / `archived` /
`project-history`. It is therefore the obvious place to ask for the witness —
and the answer is no (Q5).

Its date is not a fact. `plan_migration` takes each file's archive-directory
date from the file's own `Updated:` line, falling back to its **mtime**, with
`--date` as a global override (E9). On a fresh clone mtime is *today*. A
`migrate` that wrote the witness would stamp today's date as the archive date
on every historical document it adopts, and would give a filesystem timestamp
the authority of a tool-written record.

A foreign document that already carries an `Archived:` line keeps today's
behaviour: it is **demoted** into the `## Migrated metadata` body section as
`Migrated-Archived:`, preserved but never promoted into a tool-trusted witness.
The label is therefore **not** added to migrate's supersession set.

This is the same boundary M28 — Q6 drew when it put `docs migrate --apply`'s
reference repair out of scope, for the same reason: a foreign tree's history
was authored under no convention.

### D8 — The rule that stays declined, and what the two legs still do not reach

Two limits are stated up front rather than discovered later.

**The declined rule.** `feedback-log.md` issue #1's suggested fix for finding
3 — warn when `pairs-with` partners sit in different dated archive directories
— is **declined**, and setup gives the decline a number. On this tree, at
`docs check` exit 0, **7** archived↔archived `pairs-with` edges span different
dated directories: `m7↔m4`, `m8↔m5`, `m8↔m6`, `m9↔m6`, `m12↔m11`, `m12↔m10`,
`m13↔m12` (E5). Every one is a deliberate cross-milestone reference between
milestones archived at different events. The rule would emit 7 findings on a
correct tree — the charter's *never cry wolf* criterion, failed on the first
tree it met. The witness detects the same drift objectively and emits 0 here.

**What the two legs reach, and what they do not.** D5 refuses the one silent
**cross-dated** relocation `docs mv` performs, for every archived document
regardless of the field. D3 reports drift produced any *other* way — a hand
`git mv`, a bulk script, an `rsync`, a future defect — for every document
archived from 2.0.0 onward. **Two** residuals remain outside both, and Phase 1
states the second rather than letting the first stand for the whole truth
(Phase-1 amendment 1):

- A **hand-made** relocation of a **pre-2.0** archived document: no witness to
  disagree with, and no tool invocation to refuse.
- A **tool-driven** relocation *out of* a dated directory that is not
  cross-dated — `docs mv archive/<D>/x.md archive/x.md`, or a move into an
  undated subdirectory of the archive. It is a permitted neighbour **by
  design** (*Out of scope*: a move whose two segments do not both parse as
  dates is not refused, because refusing it would also refuse a legitimate
  reorganisation of the archive subtree that the convention permits). It
  destroys the only archive-date record a pre-2.0 archived document has, and
  `status-drift` stays silent because the destination is still inside the
  archive subtree. Leg 1 catches it for witness-carrying documents — message
  form B — and nothing catches it for the rest.

Both residuals are stated rather than papered over, and both shrink with every
archive event. Neither is closable without either reconstructing dates the tool
never observed — which D6 and Q3 refuse on principle — or refusing a
reorganisation the convention allows. The second is registered as *Follow-ups*
item 7 and locked by a Phase-2 test proving Leg 1 does reach the
witness-carrying half.

### D9 — Compatibility, upgrade guidance, and surface parity

- **Additive and silent on existing trees, with exactly one behaviour
  change.** The new field appears only on documents archived from 2.0.0
  onward, and the new rule fires only on documents that carry it, so nothing
  an adopter already has starts failing. The one behaviour change is D5's
  refusal: a `docs mv` between two dated archive directories that used to
  complete now exits 2 and writes nothing. It is a refusal in the safe
  direction, it names both dates, and it ships with its escape in the same
  paragraph.
- **M28a is a consequence of M28, and that is why it blocks M29.** E2 measures
  it: the relocation D5 now refuses left 13 hard errors at exit 2 under pre-M28
  `main` and leaves zero findings at exit 0 today. M28 rebased those
  destinations exactly as specified; the side effect was that this tree lost
  its only — accidental — alarm for the damage. Shipping M28 in 2.0.0 without
  M28a would leave the release **strictly quieter about archived-document
  relocation than 1.8.0 was**.
- **No version bump.** M25 — D6 binds the whole train: the package stays
  `1.8.0` through M25–M28a and **M29** performs the single bump to `2.0.0`.
  M28a touches neither `pyproject.toml` nor the packaging version pins; its
  CHANGELOG entries accumulate under the existing `UNRELEASED` heading.
- **Three archived-immutability guarantees must name the new field** (Q6).
  `convention.md` enumerates, in three separate paragraphs, exactly what may
  change inside an archived document — M18's move-driven edge integrity as
  widened by M28 — D5, M25 — D4's audited relationship repair, and M27 — D6's
  one-time body-link migration. Two of the three already name
  `Archived-reason:` in the byte-identical list; M18's says "other metadata"
  generically, and Phase 1 makes it explicit there too (amendment 5).
  Each must name the witness too, or the guarantee that it
  survives a `relate` repair and a move-driven rewrite is a promise no document
  makes.
- **Surface parity in the same change** (`plan.md` › *Ongoing conventions*;
  `CLAUDE.md` › *Skill update flow*): argparse `--help`, `docs/cli.md`,
  `docs/convention.md`, the bundled `src/docs_cli/skill/` (`SKILL.md`,
  `references/use-cases.md`, and `references/cli.md` /
  `references/convention.md` kept **byte-identical** to `docs/cli.md` /
  `docs/convention.md`), and `CHANGELOG.md` all describe the same behaviour.
  M28a adds **no new flag**, so the argparse delta is expected to be empty —
  which Phase 7 must confirm rather than assume.
- **The upgrade note states the present-only contract plainly**, because it is
  the one thing an adopter needs to know: nothing they already have will start
  failing, and the witness begins with their next archive.
- **`feedback-log.md` issue #1 is closed by this milestone.** Finding 3's
  archive-date half is its last open item; Phase 7 writes the answer onto the
  entry, as M28's Phase 7 did for findings 1 and 4.
- **Host-machine and Agent Playbook Suite skills are out of scope.** Per
  `CLAUDE.md`, host skills under `~/.claude/skills/` refresh only at a
  production ship (M29).

## Out of scope

- **Reconstructing true archive dates for documents archived before this
  milestone.** The witness never existed for them; git history is the
  operator's recourse, not the tool's (D6).
- **Reporting `pairs-with` partners that sit in different dated archive
  directories.** That was issue #1's literal request and it is **declined**,
  now with a measured number (D8, E5).
- **A backfill verb, a `docs fix-dates`, or any sweep over existing archived
  documents.** There is no `docs fix-links` either, for the same reason
  (M27 — D6).
- **`docs migrate --apply` writing the witness** (D7, Q5), and any change to
  how migrate infers its archive-directory dates. The pre-existing
  `Updated:`-versus-mtime inference is left exactly as it is.
- **`docs stamp` and `docs touch`.** Neither archives a document: `stamp`
  writes `Lifecycle: draft` on a fresh file and only bumps `Updated:` on an
  already-stamped one; `touch` bumps `Updated:` and nothing else. Neither
  gains the field, and the fact that `touch` moves `Updated:` on an archived
  document (E3) is evidence for D1, not a defect to fix here.
- **Fixing the `date_format` asymmetry between `parse()` and `check_doc`**
  (E8). It is a real pre-existing defect on a non-default-`date_format` tree —
  `docs archive` completes and then exits 2 on the INDEX refresh — and it is
  recorded as *Follow-ups* item 1 rather than absorbed here.
- **Any `docs mv` refusal beyond D5's predicate.** A rename inside one dated
  directory, a move with one end outside the archive subtree, and a move whose
  segments do not both parse as dates are all permitted; `status-drift` owns
  the second class and M28a does not double-report it.
- **Validating the archive subtree's shape.** M28a never requires a dated
  directory; the convention already permits any subdirectory under the archive
  subtree. The rule reports a document whose *own recorded date* is not
  corroborated, never a tree whose layout it dislikes.
- **Any new `docs check --json` field, any opt-out knob, and any graph
  traversal** (D4).
- **The `2.0.0` version bump, CHANGELOG dating, and release notes** (M29).

## Current state and risks

Measured against this repository at docs-cli 1.8.0 with M25–M28 merged
(`b1ec74b`, 1341 passed, `docs check` exit 0) during setup. Census runs were
**read-only** against the live tree; every mutation was performed on a
throwaway copy outside the repository. The full evidence table lives in the
implementation log's setup record. Each numbered item grounds a specific
decision and maps to named regression coverage in *Evidence → regression
coverage* below.

- **E1 — exactly one of the four relocation paths is silent.** All four ways a
  document can move relative to the archive subtree, measured on throwaway
  copies: (a) `docs archive` on an already-archived primary **refuses** at exit
  2 (`is already under the archive subtree; refusing before any write`);
  (b) `docs mv` archived → active root completes, and `docs check` reports
  **`status-drift`** at exit 2; (c) `docs mv` active → `archive/<date>/`
  completes, and `docs check` reports **`status-drift`** at exit 2;
  (d) `docs mv archive/2026-05-25/m9-pypi-publish.md
  archive/2026-07-03/m9-pypi-publish.md` completes at exit 0 and `docs check`
  exits **0**. The hole is reachable through a shipped verb, in one command, on
  this repository, today.
- **E2 — M28 removed the accidental tripwire.** The same relocation (d),
  replayed against the **pre-M28** CLI at `58955ef`, reports
  `moved … (4 reference(s) rewritten)` and then **13 `broken-body-link`**
  errors across 6 documents at exit 2. Against merged `main` it rewrites
  `13 destination(s) in 6 document(s), 4 Related: bullet(s)` and `docs check`
  finds **no violations**. Nothing regressed — M28 did exactly what it
  promised — but the only alarm this tree had for archived-document relocation
  was a side effect of the defect M28 fixed. Shipping M28 in 2.0.0 without
  M28a would ship a release strictly quieter about this damage than 1.8.0 was.
- **E3 — `Updated:` cannot be the witness.** **29 of 46** archived documents
  carry an `Updated:` value that differs from their dated directory — all 29
  now `2026-08-14`, the date of M27 — D6's one-time migration. And
  `docs touch archive/2026-05-20/m1-parser-and-index.md` bumps it again, exit
  0, `docs check` clean. Three unrelated writers move it, one of them a
  general-purpose verb.
- **E4 — `Archived-reason:` cannot be the witness either.** Only **13 of 46**
  archived documents carry it, because `apply_archive_plan` passes
  `plan.reason if index == 0 else None` — M26 — D1's primary-only rule. The
  reported case is a cascaded trio, whose members are exactly the 33 that carry
  nothing.
- **E5 — the declined rule would fire 7 times on a correct tree.** **7**
  archived↔archived `pairs-with` edges span different dated directories today,
  at `docs check` exit 0, every one a deliberate cross-milestone reference. No
  other `Related:` verb produces such an edge here.
- **E6 — the label is free and the vocabulary surface is one line.** **Zero**
  occurrences of an `Archived:` metadata label anywhere — not in any of
  `docs/`'s 73 documents, not in the 46 committed fixture trees, not in the
  bundled skill. The `unknown-field` rule is gated on `if config.fields:` and
  this tree sets no `add_fields`, so it is off here; the built-in set must gain
  the label anyway, for M25's stated reason.
- **E7 — no rule registry, no field order, no config-aware directory parser.**
  `docs check`'s 13 rule ids are inline `findings.append(Finding(...))` calls
  inside `check_doc` / `body_link_findings` / `reciprocity_findings`, and
  `Finding` is frozen at four fields. `set_metadata_field` appends a *new*
  inline label at the end of the inline run, so a new field's position is
  decided only by the order of the `set_metadata_field` calls in `_archive_one`
  — which is why D1 pins it. The archive-subtree predicate is spelled inline in
  **three** places (`check_doc`, the `docs list` walk, `docs project set`)
  beside the `_is_archived_rel` helper that already provides it. And
  `detect_archive_layout` is the only code that `strptime`s a directory
  segment: hardcoded to the literal `"archive"` and `"%Y-%m-%d"`, taking no
  `Config` at all, and living in the migrate half.
- **E8 — a non-default `date_format` tree already breaks.** On a throwaway tree
  with `[archive] dir = "attic"` and `date_format = "%d-%m-%Y"`,
  `docs archive thing.md --date 04-03-2026` correctly writes
  `attic/04-03-2026/thing.md` with `Updated: 04-03-2026`, then fails:
  `INDEX refresh failed: … Updated: malformed date '04-03-2026' (expected
  %Y-%m-%d)`, exit 2. `parse()` uses the hardcoded default while `check_doc`
  honours `config.date_format`. Pre-existing, out of scope, and the reason D3
  compares parsed dates rather than strings.
- **E9 — nothing in the corpus exercises this, and `migrate` is the
  falsification risk.** Ten of the 46 fixture trees carry an archive subtree,
  holding **11** archived documents plus one archived `INDEX.md`, every one at
  a single `archive/<ISO>/`; **no
  fixture anywhere carries an archive-date field**, because none exists. And
  `plan_migration` takes each file's archive-directory date from its `Updated:`
  line or its mtime.
- **Structural risk — a witness that can lie.** Every write path that could
  produce a date the tool did not observe is a way to turn a safety feature
  into a false record. Two are live: `docs migrate`'s inferred date (D7) and
  any backfill (D6). Both are refused, and both refusals are load-bearing
  rather than conservative.
- **Structural risk — a refusal that blocks a legitimate repair.** D5 refuses
  the operation an operator would also use to correct a genuinely mis-dated
  archive, and no other verb can perform it. Mitigated deliberately rather than
  accepted: the predicate is the narrowest one that closes the hole, the three
  permitted neighbours are enumerated and locked, and the by-hand escape is
  documented in the same paragraph as the refusal in both specs — so the
  refusal can never read as a dead end.
- **Structural risk — wide blast radius for a small change.** The product
  change is **three touch points** — one `set_metadata_field` call in
  `_archive_one`, one `findings.extend` in `check_doc`, and one refusal in
  `_cmd_mv` (Phase-1 amendment 3: the original "two lines" predates Q4's
  answer) — but it touches the metadata vocabulary, the
  `unknown-field` allowlist, three archived-immutability paragraphs in
  `convention.md`, the migrate demotion path, and two byte-identical skill
  mirrors. The contract freeze must enumerate every surface before any code,
  because nothing in the test suite will notice a paragraph that was not
  updated.
- **Structural risk — the fixture sweeps.** `tests/test_cli_check.py` carries
  whole-corpus sweeps asserting that every committed fixture tree gains no new
  findings, and a hand-written registration tuple guarding against a
  parametrization that would be vacuously green. A deliberately drifted fixture
  trips both unless Phase 3 updates them in the same change.
- **Mitigating existing strengths.** The rule is a pure function of one
  document's metadata, its path and the tree's config — no filesystem access,
  no second pass, no graph — so it is the cheapest rule in the suite to
  implement and to reason about. `docs archive` already threads one `date_str`
  to every member, so D2 costs nothing. M26 already refuses the re-archive path
  outright. And this repository is itself a 46-document dogfood corpus for the
  present-only contract.

### Evidence → regression coverage

| Evidence | Addressed by | Named coverage (Phases 2–3) |
|---|---|---|
| E1 one silent relocation — **prevented** | D5 | `docs mv archive/<D1>/x.md archive/<D2>/x.md` **refuses** at exit 2 with **zero bytes written**, naming both dates, proven identically on a document **with** and **without** the witness; the refusal is asserted to fire in the plan-before-move window (Phase-1 amendment 2: before the `--dry-run` branch), before the move, with `--dry-run` and `--quiet` each proven to refuse too |
| E1 the permitted neighbours | D5 | a rename **within** one dated archive directory, a move with one end outside the archive subtree, and a move whose two segments do not both parse as dates each **complete**; the two `status-drift` paths keep their existing locks and gain no second finding; every pre-M28a `docs mv` behaviour is proven byte-stable. The neighbour that costs something — `docs mv archive/<D>/x.md archive/x.md`, D8's second residual — is proven both to **complete** and, on a witness-carrying document, to be reported by Leg 1's second message form (Phase-1 amendment 1) |
| E1 one silent relocation — **detected** | D1 + D3 | an `archivedate-drifted` fixture — a document carrying the witness in a *different* dated directory — yields exactly one `archive-date-drift` error naming both dates, at exit 2, however the relocation was produced |
| E2 M28 silenced the alarm | D1 + D3 + D5 | the E1d relocation replayed end-to-end inside the suite: `docs mv` now refuses it outright, and a hand-made equivalent relocation of a witness-carrying document leaves a tree that `docs check` **fails** — where both flows were silent before |
| E3 `Updated:` is not a witness | D1 | a lock proving `docs touch` on an archived document bumps `Updated:` and leaves the witness **byte-identical**, so the two fields cannot be conflated |
| E4 `Archived-reason:` is primary-only | D2 | a cascaded closeout over `archive-trio` where **every** moved member carries the witness with the operation's single date, while `Archived-reason:` stays on the primary alone |
| E5 the declined rule over-fires | D8 | an `archivedate-clean` fixture carrying a cross-dated `pairs-with` pair, both corroborated, asserted to yield **zero** findings — the decline, locked |
| E6 vocabulary surface | D1 + D9 | the label is accepted with `add_fields` absent, with `add_fields` set to an unrelated value, and with the label itself absent from `add_fields` — no `unknown-field` warning in any of the three |
| E7 no field order | D1 | a byte-level assertion on a freshly archived document's metadata block: the exact line order, with and without `--reason` |
| E8 parsed-date comparison | D3 | a non-default-`date_format` tree in which the witness and the directory agree, proven silent; and one in which they disagree, proven to fire — neither decided by string equality |
| E9 corpus and migrate | D6 + D7 + Phase 3 | an `archivedate-absent` fixture (a pre-2.0 archived document) proven silent; `docs migrate --apply` over the `real-trees/archive-subdir` shape proven to write **no** witness; a foreign `Archived:` line proven demoted to `Migrated-Archived:` |
| Q7 non-dated locations | D3 | `archivedate-outside` (the witness on a document in the active tree) and `archivedate-undated` (the witness under an undated archive subdirectory) each yield exactly one finding, and the `status-drift` interaction is asserted in both directions |

## Deliverables

- [x] Both legs frozen in Phase 1 against the resolved Q1–Q7: the field's
      name, value source, rendering, block position and every-member write
      rule; the vocabulary changes; the corroboration predicate and the rule's
      severity / exit / cardinality / message forms; the `docs mv` refusal
      predicate, its message, its exit code, its plan-before-move position and
      its documented escape; the present-only contract; and the Phase-5
      signatures.
- [x] The structured archive-date field written by `docs archive` to **every**
      document the operation moves, at the pinned block position, with the same
      `date_str` that names the directory.
- [x] A pure, config-aware corroboration helper over `(path, metadata, root,
      config)` with no filesystem access of its own, and the
      `archive-date-drift` rule wired into `check_doc` at the frozen position.
- [x] Vocabulary integration: the label in `_BUILTIN_METADATA_FIELDS`, out of
      `parse()`'s `known` set, out of migrate's supersession set, and unaffected
      by `[vocabulary] add_fields`.
- [x] `docs migrate` behaviour pinned by test: never writes the witness, never
      promotes a foreign one. (Complete at Phase 2: D7 is satisfied by
      construction, so the deliverable IS the pair of locks, and both are GREEN
      — including the one that stops `Archived` being added to migrate's
      supersession set in the same change that adds it to the built-in set.)
- [x] Fixture trees for the corroborated, the drifted, the field-absent, the
      outside-the-archive, the undated-directory and the two-dated-directory
      (`docs mv` refusal) cases, with the registration tuple and both
      whole-corpus sweeps updated in the same change.
- [x] Regression coverage for E1–E9 plus the present-only silence proof over
      all 46 of this tree's archived documents, byte-identity locks for
      `touch` / `relate` / the M18–M28 widened move exception, and proof that
      the closed four-key `Finding` record and the M26 archive plan behaviour
      are unchanged.
- [x] `convention.md`'s three archived-immutability paragraphs, its *Optional
      fields* table and its *Archive subtree* rules updated; `cli.md`'s archive
      step list, check-rule list, `rule` table row, built-in-field set and
      upgrade recipe updated; both byte-identical skill mirrors re-synced; the
      `UNRELEASED` CHANGELOG entry written.
- [x] A dated note on `feedback-log.md`'s issue #1 entry recording that finding
      3's archive-date half is answered, closing the issue's last open item.
- [x] End-to-end dogfood on a throwaway copy proving that E1d's `docs mv` now
      refuses with zero bytes written, that a hand-made equivalent relocation
      of a witness-carrying document is a hard error naming both dates, that
      all 46 pre-witness archived documents stay silent, and that a real
      milestone closeout writes the witness to every member and leaves
      `docs check` clean.
- [x] **Leg 2** — `docs mv`'s refusal of a cross-dated archived relocation
      (D5), evaluated in M28's plan-before-move window at the position
      Phase-1 amendment 2 froze, with
      its frozen message, exit 2, its zero-bytes-written guarantee, its four
      enumerated permitted neighbours (amendment 6), and its escape documented
      in the same paragraph in both `cli.md` and `convention.md`.

## TDD implementation plan

### Phase 1 — Define Contract

- Objective: freeze — against the resolved Q2, Q3, Q5, Q6, Q7 and the
  operator's answers to Q1 and Q4 — the field's name, the source and rendering
  of its value, its pinned position in the metadata block, and the rule that it
  is written to every document an archive operation moves; the three vocabulary
  changes and the one that is deliberately *not* made (`parse()`'s `known`
  set); the corroboration predicate as three exact conditions, the two
  non-corroborating shapes, parsed-date comparison, and which rule owns a
  recorded value that does not parse; the rule id, severity, exit code,
  one-finding-per-document cardinality, its position in `check_doc`'s append
  order, its independence from `status-drift`, and the frozen message forms;
  the present-only contract and its consequence for upgrade; `docs migrate`'s
  non-write and non-promotion; the exact `convention.md` wording for all three
  archived-immutability paragraphs; **D5's refusal predicate, its frozen
  message beside `archive-date-drift`'s, its exit code, its position in
  `docs mv`'s plan-before-move window, its enumerated permitted neighbours
  and its documented escape**; and the Phase-5 signatures. No business logic
  lands. Phase 1 does **not** re-open the setup decisions.
- Files: `docs/cli.md` (the `docs archive` step list, the `docs check` rule
  list and `rule` table row, the built-in-field set, the exit-code rows, the
  upgrade recipe, and the `docs mv` section carrying D5's refusal and its
  escape in one paragraph),
  `docs/convention.md` (*Optional fields*, *Archive subtree*, and the three
  archived-immutability paragraphs), this milestone. Interface signatures are
  frozen in a *Decisions (Phase 1 — BINDING)* section here rather than stubbed
  in `src/docs_cli/cli.py`, following the M25/M26/M27/M28 precedent — stubs
  would perturb the Phase-4 subprocess RED reasons.
- Exit: specs, help strings, the messages and the frozen signatures are
  internally consistent; no behavior changes; `docs check --root docs` still
  exits 0 and the suite is still 1341 GREEN.

### Phase 2 — Write Tests (RED)

- Objective: express the writer, the corroboration predicate, every
  non-corroborating shape, the present-only silence, the vocabulary
  integration, the `migrate` non-write and every byte-identity guarantee before
  any implementation — including every case that must stay GREEN at baseline.
- Files: `tests/test_check.py` (the pure predicate and the rule),
  `tests/test_cli_check.py` (subprocess and fixture-tree locks),
  `tests/test_cli_archive.py` (the writer, the block position, the cascaded
  every-member rule, the `--date` and `date_format` paths),
  `tests/test_cli_mv.py` (the E1d reproduction, D5's refusal with and without
  the witness present, on a default-config tree **and** on one with a
  non-default `[archive] dir` / `date_format`, and the four permitted
  neighbours it must **not** refuse), `tests/test_cli_migrate.py` (non-write and demotion),
  `tests/test_cli_touch.py` and `tests/test_cli_relate.py` (byte identity),
  `tests/test_config.py` (`add_fields` interaction), `tests/test_model.py`
  (`extra_fields` surfacing), and the skill-parity tests where the surface
  moves.
- Exit: the E1–E9 locks in *Evidence → regression coverage* are RED **only**
  for missing M28a behavior; the M18 archive-edge, M25 `relate`, M26 plan and
  M27/M28 body-link locks stay GREEN at baseline and are classified as such;
  the closed four-key `Finding` record is asserted unchanged, and
  `archive --json`'s top-level key set is asserted **not** to widen.

### Phase 3 — Create Data/Fixtures

- Objective: provide small committed trees isolating one semantic each, per
  `test-strategy.md`'s fixture policy, plus inline builders for the mutation
  cases.
- Files: new `tests/fixtures/trees/archivedate-*` trees — `-clean` (a
  corroborated witness, plus a deliberate cross-dated `pairs-with` pair so the
  decline is locked), `-drifted` (the witness against a different dated
  directory), `-absent` (a pre-2.0 archived document with no field),
  `-outside` (the witness on a document in the active tree), `-undated` (the
  witness under an undated archive subdirectory) and `-two-dated-dirs` (two
  populated dated archive directories, so D5's refusal and the permitted
  same-directory rename can both be exercised, with and without the witness).
  Non-default `date_format` and
  `[archive] dir` cases and every write-then-byte-compare case live in inline
  `tmp_path` builders — the M25 rule, because those assert on written bytes
  rather than on a tree walk.
- Exit: fixtures are structure-only (never date-sensitive at run time), parse
  deterministically, and each yields exactly its intended finding set; the
  hand-written registration tuple in `tests/test_cli_check.py` and **both**
  whole-corpus sweeps are updated in the same change; every pre-M28a fixture
  tree stays byte-identical and gains zero findings.

### Phase 4 — Run Tests (RED Baseline)

- Objective: prove the new tests fail for the intended missing behavior and for
  nothing else.
- Files: implementation log only.
- Exit: full baseline captured with exact counts; zero collection errors, zero
  tracebacks, zero xfails; every one of the 1341 pre-existing test ids
  mechanically proven still present and GREEN; every GREEN-at-baseline lock
  classified by name.

### Phase 5 — Update Base Interfaces

- Objective: add the vocabulary entry and **all three** pure helpers without
  wiring any verb — the label into `_BUILTIN_METADATA_FIELDS`; a config-aware
  reader returning the dated archive directory's date for a root-relative path,
  or `None`; the pure `archive_date_findings(path, metadata, root, config) ->
  list[Finding]` helper shaped exactly after `body_link_findings`; and Leg 2's
  `cross_dated_archive_move(old_rel, new_rel, config)`, which item (H) freezes
  as a Phase-5 signature and which **shares** the same directory reader, so the
  two legs can never disagree about what a dated archive directory is. Every
  helper stays a pure function of its arguments; the filesystem is never
  consulted. `parse_date` gains its keyword-only `label` (OQ-3) in the same
  change, with every existing call site's message byte-identical.
- Files: `src/docs_cli/cli.py`, `tests/test_check.py`, `tests/test_config.py`.
- Exit: interfaces typecheck and are unit-tested — all three pure-seam groups
  in `tests/test_check.py` GREEN, including both non-default-config axes for
  the shared reader and for Leg 2's predicate; `check_doc`, `_archive_one` and
  `_cmd_mv` are untouched, so every CLI-level test stays honestly RED at the
  seam; `docs check --root docs` still exits 0.

### Phase 6 — Implement Offline/Core Path

- Objective: wire both ends — one `set_metadata_field` call in `_archive_one`
  at the pinned position, and one `findings.extend(archive_date_findings(...))`
  in `check_doc` at the frozen position; and D5's refusal in `docs mv`'s
  plan-before-move window at the position Phase-1 amendment 2 froze —
  immediately after `old_rel` / `new_rel` are derived, before the `--dry-run`
  branch and before the first byte moves.
- Files: `src/docs_cli/cli.py`, the archive/check/mv unit and integration
  tests.
- Exit: core and integration tests GREEN; a normal archive writes the witness
  to every member and leaves `docs check` clean; a drifted document is a hard
  error naming both dates; a field-absent document is silent; a cross-dated
  `docs mv` refuses at exit 2 with zero bytes written while all four permitted
  neighbours complete; M18, M25, M26 and M28 behaviour byte-stable;
  `docs check --root docs` still exits 0.

### Phase 7 — Update Tool/Wrapper Layer

- Objective: reconcile every parallel surface — `cli.md`'s `docs archive` step
  list, `docs check` rule list, `rule` table row, built-in-field set,
  exit-code rows and upgrade recipe; `convention.md`'s *Optional fields* table,
  *Archive subtree* rules and **all three** archived-immutability paragraphs;
  the `docs migrate` section's statement that the witness is never written and
  a foreign one is demoted; **`cli.md`'s and `convention.md`'s `docs mv`
  paragraphs carrying D5's refusal, its exit code and its by-hand escape
  together, so the refusal never reads as a dead end**; the argparse surface
  (expected to be unchanged — M28a adds no flag — confirmed, not assumed); the
  bundled skill including the two byte-identical mirrors; and the `UNRELEASED`
  CHANGELOG with the upgrade note naming the one behaviour change.
  `feedback-log.md`'s issue #1 entry gains a dated note recording that finding
  3's archive-date half is answered, closing the issue's last open item.
- Files: `src/docs_cli/cli.py` (D5's human-facing refusal message only — no
  parser change, because M28a adds no flag), `docs/cli.md`,
  `docs/convention.md`, `src/docs_cli/skill/` (`SKILL.md`,
  `references/use-cases.md`, and the byte-identical `cli.md` / `convention.md`
  mirrors), `CHANGELOG.md`, `docs/feedback-log.md`. **Not** `pyproject.toml` or
  the version pins (M25 — D6).
- Exit: subprocess tests, the reference byte-identity tests and the
  surface-parity checks are GREEN; `docs archive --help` / `docs check --help`
  and `cli.md` agree.

### Phase 8 — Run Tests (GREEN)

- Objective: run the focused and full suites plus lint, format, types,
  reference byte identity, and docs integrity.
- Files: implementation log only unless a real defect is found.
- Exit: all gates GREEN with exact counts recorded, and every pre-existing test
  id mechanically proven still present and GREEN.

### Phase 9 — Integrate / Accept / Dogfood

- Objective: on a throwaway copy of this docs tree, prove each measured
  property. Replay E1d and confirm `docs mv` now **refuses** it at exit 2 with
  the tree byte-identical afterwards, where it previously completed at exit 0 —
  and confirm the same refusal on a document that carries **no** witness, which
  is the case the witness alone could never reach. Reproduce the relocation by
  hand on a witness-carrying document and confirm `docs check` now exits **2**
  naming both dates where it exited 0. Confirm all **four** permitted
  neighbours still complete — including the two-spellings-of-one-date case
  (`archive/2026-01-01/` to `archive/2026-1-1/`), which is the one a raw-string
  comparison would refuse, and one cross-dated refusal on a tree with a
  non-default `[archive] dir` and `date_format`. Confirm all
  **46** existing archived documents — none of which carry the field — stay
  silent, which is the whole compatibility story measured rather than asserted.
  Run the real closeout `docs archive m26-… --cascade-only 'm26-*'` and confirm
  **every** moved member carries the witness with one shared date, that
  `Archived-reason:` is still on the primary alone, and that `docs check` is
  clean. Run `docs migrate --apply` over an archive-shaped foreign copy and
  confirm **no** witness is written. Confirm the E5 cross-dated `pairs-with`
  edges still produce nothing. Measure the added `docs check` runtime over this
  73-document tree. The real tree is never written to.
- Files: throwaway trees only; the committed docs record the evidence.
- Exit: every flow runs unattended with no stdin; the refusal flow leaves the
  throwaway tree byte-identical; the silence proof covers all 46 documents; the
  closeout flow ends `docs check` clean; runtime is recorded and bounded; the
  real tree is untouched.

### Phase 10 — Quality, Docs, Refactor

- Objective: run the `/simplify` pass over the new helper and the two touch
  points — the three inlined copies of the archive-subtree predicate are the
  obvious candidate — close `architecture.md` (the `check` and `archive`
  sections) and `test-strategy.md`, update the shipped use-case catalog, and
  write the completion summaries.
- Files: code/docs as justified, this milestone and the implementation log.
- Exit: full gate GREEN; no placeholders; M28a implementation-complete and
  handed to M29, staying `Lifecycle: active` until the M29 publish closeout.

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
- [ ] Phase 10 — Quality, Docs, Refactor

## Decisions carried from discovery

- The dated archive directory is today the **only** record of when a document
  was archived, which is exactly why `docs check` exited 0 on issue #1's
  reproduction (`feedback-log.md`, 2026-08-15).
- The reporter's suggested rule — warn when `pairs-with` partners sit in
  different dated directories — is **declined outright**, because two documents
  archived months apart may legitimately carry an edge, so the rule would fire
  on correct trees and fail the charter's *never cry wolf* criterion. The drift
  it reaches for is detected directly, and objectively, by the witness field
  (`feedback-log.md`, 2026-08-15).
- The tool should refuse or repair what it can **prove** is wrong and ask only
  about what it genuinely cannot determine; the safe outcome is the default and
  the dangerous one the explicit exception (`feedback-log.md`, *Underlying
  principle*).
- Archived documents are immutable except through named, narrow, enumerated
  exceptions, and `convention.md` states the count deliberately — M28 left it
  at three by widening M18's rather than granting a fourth.
- The package version stays `1.8.0`; M29 performs the single bump
  (M25 — D6).

## Decisions recorded at setup (BINDING)

Two setup findings changed something that was already written down — the
registered stub's own statement of the risk, and the nearest precedent for how
an archive-time field is written. They are restated here, in one place, so a
Phase-1 agent with none of the setup conversation can reconstruct **what** was
decided, **what it replaced**, and **why**, from this document alone.

### A1 — Correction to the registered stub's *Current state and risks*

The registered M28a stub asserted: *"M26 already prevents the tool from
relocating archived documents (`already-archived` ineligibility), so this
milestone is defence in depth against paths the convention forbids but nothing
currently detects."*

**That is true of `docs archive` and false of `docs mv`.** Setup enumerated all
four relocation paths and measured each (E1). `docs archive` does refuse an
already-archived primary, at exit 2, before any write. But
`docs mv archive/2026-05-25/m9-pypi-publish.md
archive/2026-07-03/m9-pypi-publish.md` **completes at exit 0**, rewrites the 13
stale destinations and 4 `Related:` bullets so nothing dangles, and leaves
`docs check` reporting **no violations**. The convention forbids it; a shipped
verb performs it in one command.

**The correction (BINDING).** M28a is not defence in depth against a
hypothetical. It closes a live, reachable, silent path in the tool's own
surface. Two consequences follow:

- The *Current state and risks* section is written against the measurement, not
  the assumption, and E1 is the item it opens with.
- **Q4 became a real question, and the operator answered it.** Because the
  tool itself offers the path, "detect after the fact" and "refuse before the
  write" are genuinely different products, and the second is available cheaply
  because M28 has already built `docs mv`'s plan-before-move,
  refuse-with-zero-mutation machinery. **Both legs are adopted** (D5), so the
  refusal is binding scope rather than an option, and D8's residual narrows
  from "every pre-2.0 document" to the **two** cases D8 now names (amendment
  1): a hand-made relocation of a pre-2.0 document, and the tool-driven
  relocation *out of* a dated directory that is not cross-dated.

**And E2 explains the timing.** The same relocation, replayed against the
pre-M28 CLI at `58955ef`, leaves **13 `broken-body-link`** errors at exit 2.
M28 rebases those destinations correctly — that is the milestone working as
specified — and in doing so removes the only signal this tree had for the
damage. M28a is therefore a **consequence** of M28 rather than an independent
idea, and shipping M28 in 2.0.0 without it would ship a release **strictly
quieter about archived-document relocation than 1.8.0 was**. That is why this
milestone blocks M29 rather than trailing it.

### A2 — The witness does not inherit `Archived-reason:`'s primary-only rule

`Archived-reason:` is the nearest precedent for a field written by
`docs archive`, and M26 — D1 confines it to the **named primary**: *"an
`Archived-reason:` line records why that document was archived, so it is
written to the named primary only, never to a cascaded candidate."*
`apply_archive_plan` implements exactly that.

**The witness deliberately does not follow it** (D2). It is written to the
primary **and** to every selected cascade candidate.

Why the divergence: the two fields record different kinds of thing. A *reason*
explains why an operation was requested, and there is one operation, so there
is one reason. A *date* is a fact about each document's own move, and every
member moved. The measurement makes the cost concrete: `Archived-reason:`
covers **13 of this tree's 46** archived documents (E4), and issue #1's
real-tree replay was a **cascaded trio split across two dated directories** —
whose non-primary members are precisely the documents a primary-only witness
would leave blind. Mechanically the divergence is free: `_archive_one` already
receives `date_str` for every member, and M26 — D1's reason special-case is
left untouched.

## Setup questions (Q1–Q7)

Seven questions were raised at setup and **all seven are resolved before
Phase 1**. **Q4 is an operator decision** — the one that changed the
milestone's shape, adding D5's preventive leg to binding scope. **Q1** was
auto-resolved to `Archived:` under the naming-with-an-obvious-default rule,
with the rejected alternative recorded so the label's permanence is on the
record. **Q2, Q3, Q5, Q6 and Q7** are conductor-resolved as determined by the
convention, the charter, the measured evidence, or the M25–M28 precedent. Q1,
Q2 and Q3 are the registered stub's three "Open questions for M28a Phase 1",
carried forward and sharpened by the setup measurements. Phase 1 freezes the
contract against these answers and does not re-litigate scope.

### Q1 — What is the field called?

*(The registered stub's Open question 1.)*
**RESOLVED → D1 (BINDING). The field is `Archived:`.** Auto-resolved under the
naming-with-an-obvious-default rule: the registered stub and the independent
setup analysis landed on the same name, it mirrors an established shape in the
same metadata block, and setup measured zero collisions.

**Why it matters.** `convention.md` states that `.docs.toml` may *add* to
vocabularies but **never remove or rename built-ins**. The label is therefore
permanent from the moment 2.0.0 ships, it becomes part of a public spec that
also ships byte-identically inside the wheel, and it will appear in every
archived document this tool ever writes. It is also the milestone's title
noun — every message, every spec paragraph and every fixture spells it.

**The resolution — `Archived:`.** A past-participle label whose value is a
date, rendered in the tree's `date_format`, which is *exactly* the shape
`Updated:` already has; and it pairs with the existing `Archived-reason:` as
event and reason, so the two read as one archive record:

```
Updated: 2026-08-15
Archived: 2026-08-15
Archived-reason: Milestone M26 complete
```

**The rejected alternative, recorded because the label is permanent:**
`Archived-date:` is unambiguous against a boolean reading (`Archived: true`)
and is morphologically parallel to `Archived-reason:`. It lost because
`Updated:` is already a date-valued past participle in the same block, so the
ambiguity is one this convention has never had — and `-date` would make it the
only field in the vocabulary that names its own type. A third option,
`Archive-date:`, loses on both counts.

Setup found **zero** occurrences of any `Archived:` label anywhere in `docs/`,
the 46 fixture trees or the bundled skill (E6), so no spelling collides with
existing data. The residual risk is a *foreign* tree carrying `Archived: true`,
which D7 handles by demotion rather than promotion regardless of which name was
chosen.

### Q2 — Must the recorded value equal the directory date exactly?

*(The registered stub's Open question 2.)*
**RESOLVED → D3 (conductor), as recommended.**

**Why it mattered.** The looser reading — allow a recorded date that *predates*
the directory, to accommodate a legacy repair where the true archive date is
known and the directory is not — would let the tool tolerate the exact
condition it exists to detect.

**The resolution — exact equality**, with one refinement the stub did not
state. No verb can legitimately produce a divergence: `docs archive` refuses an
already-archived primary (E1a) and M26 — Q4 excludes already-archived
candidates from a cascade, so the field and the directory are written from one
`date_str` in one operation and can only diverge afterwards. The legacy-repair
case is answered by scope rather than by tolerance: M28a does not reconstruct
true archive dates, and an operator who knows the true date differs should move
the document into the right directory, not record a date its location
contradicts.

**The refinement: comparison is on parsed dates, not raw strings.**
`date_format` is configurable, and M25 already settled the principle when it
wrote `Revision:` — *"the ISO spelling below is the default format, not a
second hardcoded one (two date spellings in one file would be a defect)"*. So
the witness renders in the tree's `date_format` and is compared as a parsed
date against the directory segment parsed in the same format. E8 shows why this
is not pedantry: a non-default-`date_format` tree already trips a pre-existing
hardcoded-ISO parse, and M28a must not add a third spelling or a fourth parser
to that surface.

### Q3 — Does `docs archive` backfill the field on documents it re-reads?

*(The registered stub's Open question 3.)*
**RESOLVED → D6 (conductor), as recommended.**

**Why it mattered.** Backfill is the obvious way to make the rule cover the
existing population, and this repository alone has 46 archived documents that
will otherwise never carry a witness.

**The resolution — no, and there is no code path that could do it honestly.**
`docs archive` refuses an already-archived primary (E1a, measured) and reports
an already-archived candidate as ineligible (M26 — Q4), so the verb never
re-reads an archived document at all. Backfilling would require a *new* verb, a
sweep, and a source for the date — and the only sources available are the
directory (which would make the witness a tautology that can never disagree
with its own corroborator) or a guess. Inventing a date for a document whose
true date is unknown is the falsification this milestone exists to prevent.

The precedent is exact and it is the boundary: M27 — D6 repaired this
repository's archived body links once, by the milestone, deliberately, and
`convention.md` records that **no CLI verb performs it**. M28a takes the same
position — the historical population stays silent (D6), and coverage grows by
use.

### Q4 — Does `docs mv` also refuse the one silent relocation, or does M28a only detect it?

**RESOLVED → D5 (operator). Adopt BOTH legs** — the witness *and* a narrow
`docs mv` refusal. This is the answer that changed the milestone's shape, so
the refusal is binding scope (D5) rather than an option, and it carries its own
deliverables, fixtures, locks and success criteria.

**Why it mattered, and why it was new.** The registered stub assumed the tool
already prevents this (A1). It does not: `docs mv` performs the one silent
relocation in one command, at exit 0, leaving `docs check` clean (E1d). That
makes "detect" and "prevent" genuinely different products rather than a
phrasing choice:

- The **witness alone** makes drift detectable for documents that carry it, and
  only for those. The 46 archived documents already in this tree — and the
  whole archived population of every tree that upgrades from 1.x — stay
  permanently undetectable, by construction (D6). The tool would keep offering
  a command that silently falsifies their only archive-date record.
- A **narrow refusal** closes the tool's own path for **every** archived
  document, field or no field, and is decidable from the two paths alone: the
  source and the destination are both under `<archive_dir>` and their first
  segments parse to **different** dates. It refuses at exit 2 before the first
  byte moves, reusing the plan-before-move, refuse-with-zero-mutation machinery
  M28 built one milestone ago, and it names both dates.

**The adopted scope.** One predicate in `docs mv`'s existing plan-before-move
window — reusing M28's refuse-with-zero-mutation machinery rather than
inventing a second refusal mechanism; Phase-1 amendment 2 fixes its exact
position, one step earlier than the pre-flight call, so it reaches
`--dry-run` — one frozen message pinned in Phase 1
beside `archive-date-drift`'s, one exit code, one `cli.md` paragraph, one
`convention.md` sentence, and locks for both the refusal and the **four**
*permitted* neighbours that must keep working (amendment 6): a rename
**within** one dated directory, a move that `status-drift` already catches, a
move whose two segments do not both parse, and two spellings of one date. It adds no flag and no JSON key. Both legs get RED
tests in Phase 2 and fixtures in Phase 3.

**The argument against, and the answer.** A cross-dated relocation is also how
an operator corrects a *mis-dated* archive, and no other verb can do it — a
refusal would remove the only tool-driven repair. The answer is that the escape
stays available and documented (move the file by hand, then correct the field,
then `docs check`), that the operation being refused is one the convention
already forbids, and that a repair which silently rewrites a document's only
archive-date record is exactly the operation this milestone exists to make
visible. The narrower alternative — refuse only when the moving document
carries the witness — was considered and rejected: it makes the refusal depend
on the very field whose absence is the problem, and leaves the pre-2.0
population unprotected, which is the whole reason for the second leg.

**What the answer changed.** D5 is new binding scope; D8's residual narrows
from *"every pre-2.0 document is permanently undetectable"* to the **two**
cases D8 now names (Phase-1 amendment 1) — a hand-made relocation of a pre-2.0
document, and the tool-driven relocation *out of* a dated directory that is not
cross-dated — because the tool's own **cross-dated** path is now closed for
every archived document regardless of the field; and D9 gains M28a's one
behaviour change — a `docs mv` that used to complete now refuses. The escape
ships in the same paragraph as the refusal in both specs.

### Q5 — Does `docs migrate --apply` write the witness for the files it relocates?

**RESOLVED → D7 (conductor), as recommended by measurement.**

**Why it mattered.** `docs migrate --apply` is a third file mover: it relocates
archive-shaped files into `archive/<date>/` and sets `Lifecycle: archived`
purely from the directory name. It is the one verb that could give an adopted
tree witness coverage in a single command — and an adopted tree is exactly the
large, historical, high-value archive M28a otherwise cannot help.

**The resolution — no.** `plan_migration` takes each file's archive-directory
date from the file's own `Updated:` line, falling back to its **mtime**, with
`--date` as a global override (E9). On a fresh clone mtime is *today*. A
migrate that wrote the witness would stamp today's date as the archive date on
every historical document it adopts, and would give a filesystem timestamp the
authority of a tool-written record — the falsification Q3 refuses, at scale,
with the tool's own signature on it.

Two consequences are pinned rather than left implicit:

- A foreign document already carrying an `Archived:` line keeps today's
  behaviour — demoted into the `## Migrated metadata` body section as
  `Migrated-Archived:`. The label is **not** added to migrate's supersession
  set, so a foreign tree's assertion is preserved but never promoted.
- Migrate's existing date inference is untouched. M28a does not improve it and
  does not depend on it.

This is the same boundary, for the same reason, that M28 — Q6 drew when it put
`docs migrate --apply`'s reference repair out of scope.

### Q6 — Which archived-document immutability guarantees must name the field?

**RESOLVED → D9 (conductor).** All three.

**Why it mattered.** `convention.md` grants exactly three narrow exceptions to
archived-document immutability, and each states its blast radius as an explicit
list of what may change and what stays byte-identical — two of the three naming
`Archived-reason:` by hand, and M18's saying "other metadata" generically
(amendment 5). A new archive-time field that is not named in those
lists is a field with no stated guarantee: nothing in the suite would notice,
and an adopter reading the convention could not tell whether a `docs relate`
repair or a move-driven rewrite may touch it.

**The resolution — all three paragraphs name the witness** (landed in Phase 1
with the rest of the author-facing surface, re-verified in Phase 7)**:**
M18's move-driven edge integrity as widened by M28 — D5, M25 — D4's audited
relationship repair, and M27 — D6's one-time body-link migration. In every one
of them the witness sits on the byte-identical side, beside
`Archived-reason:` — no verb and no migration may change it. The `Archived:`
value records entry into the archive, exactly as `Archived-reason:` records
why, and neither is ever a record of a later repair.

### Q7 — Does the rule fire on a document carrying the field outside a dated archive directory?

**RESOLVED → D3 (conductor).** Yes — it is the same predicate, not a second
rule.

**Why it mattered.** Two shapes reach it. A document moved out of the archive
subtree whose `Lifecycle:` is then hand-edited to an active value: `status-drift`
goes quiet, and the stale witness is the only evidence left. And a document
under an *undated* archive subdirectory (`archive/misc/x.md`), which the
convention permits and which no verb produces.

**The resolution — one rule, one finding per document, two message forms.**
Corroboration is a positive test (D3): the first segment under `<archive_dir>`
parses to the recorded date. A document elsewhere in the tree, or under an
undated subdirectory, simply has no corroborating location, and the finding
says so. Making it a second rule id would split one assertion — *this recorded
date is not corroborated* — across two vocabulary entries for no gain.

Crying wolf was considered and does not apply: a hand-organised undated archive
tree carries **no** witness, because only `docs archive` writes one and it
always writes a dated directory, so the only way to reach this shape is to have
been moved.

**`status-drift` and `archive-date-drift` are independent** and may both fire
on one document. They report different facts — a lifecycle that disagrees with
a location, and a date that does — and the case that motivates the rule
(hand-edited `Lifecycle:`) is precisely the one where `status-drift` is silent.
This is a deliberate departure from M27's non-overlap rule, which applied
because that milestone's two rules were mutually exclusive classifications of
one destination; these are two independent assertions about one document.

### Also settled, without a question

- **Version staging.** The package stays `1.8.0`; **M29** performs the single
  bump to `2.0.0`. CHANGELOG entries accumulate under `UNRELEASED`
  (M25 — D6).
- **No new JSON field, anywhere.** The `Finding` record stays closed at
  `{path, severity, rule, message}` (M27 — D4), and `archive --json`'s
  top-level key set does not widen — it already carries `date`, which is the
  same value the field records.
- **No new flag.** M28a adds no CLI option; the surface change is a field the
  tool writes and a rule it enforces. Phase 7 confirms the argparse delta is
  empty rather than assuming it.
- **Exclusion predicates govern the walk, never the predicate.** `[exclude]` /
  `.docsignore` decide which documents are checked, exactly as they already do
  for every other rule (M26 — Q8 / M27 — D3, restated).
- **`INDEX.md` is unaffected.** Extra metadata fields are opaque to the human
  INDEX renderer, so the witness changes no rendered byte; the frozen dogfood
  snapshot moves only for the new log entry this setup adds.
- **`docs stamp` and `docs touch` never write it.** `stamp` writes
  `Lifecycle: draft` on a fresh file and only bumps `Updated:` on an
  already-stamped one; `touch` bumps `Updated:` alone. Neither archives a
  document, so neither has a date to witness.
- **Skill channels.** The bundled skill in `src/docs_cli/skill/` updates in the
  **same change** as the surface, with `references/cli.md` and
  `references/convention.md` byte-identical to `docs/cli.md` and
  `docs/convention.md`. Host-machine skills refresh only at the M29 production
  ship, and the Agent Playbook Suite update stays a post-M29 cross-repository
  follow-up (`CLAUDE.md`; `plan.md`).

## Decisions (Phase 1 — BINDING)

Phase 1 freezes the surface Phase 2 asserts against. Everything below is
binding for M28a; Phases 5–7 implement it verbatim. The setup decisions (D1–D9)
and the resolved setup questions (Q1–Q7) are **not** re-opened — this section
makes them exact. The author-facing statement lives in `cli.md` ›
`docs archive`, `cli.md` › `docs check` › *Archive-date corroboration*,
`cli.md` › `docs mv` › *Cross-dated archived relocations*, and `convention.md`
› *Optional fields* / *Archive subtree*; what follows is the machine-facing
contract plus the decisions that could not be read off the setup text.

**No product code lands in Phase 1.** The signatures are frozen here rather
than stubbed in `src/docs_cli/cli.py`, following the M25/M26/M27/M28
precedent — a stub would perturb the Phase-4 subprocess RED reasons.

### Amendments to the setup-frozen material (BINDING)

Six frozen items could not stand as written. All six are recorded here so the
binding scope and the frozen contract cannot disagree — M27's and M28's
precedent for amending setup-frozen material in place rather than diverging
silently. Amendments 1 and 2 are Phase-1 decisions; 3, 4, 5 and 6 are
corrections of statements of fact. None re-opens a decision, and none changes
what M28a ships.

| # | Amendment | Why the frozen form could not stand |
|---|---|---|
| 1 | **D8's residual is incomplete, and is amended in place.** It said the only thing neither leg reaches is "a hand-made relocation of a pre-2.0 archived document". `docs mv archive/2026-01-01/x.md archive/x.md` — D5's *third permitted neighbour*, by design — is a **tool-driven** relocation of any archived document that destroys the only archive-date record it has, leaves `status-drift` silent (the destination is still under the archive subtree), and is reached by Leg 1 only for witness-carrying documents. The predicate is **not** widened; D8 now names both residuals, *Follow-ups* item 7 registers the second, and the E1-neighbours coverage row gains the Leg-1 lock. | A binding document must not claim closure it does not have. Widening the predicate was considered and rejected by operator decision (OQ-7): it would also refuse a legitimate reorganisation of the archive subtree, which `convention.md` permits. The honest move is to name the cost, not to pay it with a false refusal. |
| 2 | **D5's "evaluated inside `docs mv`'s existing plan-before-move pre-flight" is refined to "in the plan-before-move *window*, one step earlier — immediately after `old_rel` / `new_rel` are derived and before the `--dry-run` branch".** It therefore refuses in **every** mode, `--dry-run` and `--quiet` included. | `_cmd_mv` returns at its `--dry-run` branch *before* `preflight_move_plan` runs, so D5's literal reading would leave `docs mv --dry-run` printing `would move …` at exit 0 for an operation the apply refuses — a preview that lies, in the milestone whose entire point is that nothing silently falsifies the archive record. This is the same window one step earlier, not a second refusal mechanism, and it matches `docs archive --cascade-only`'s malformed-invocation precedent: a verdict decidable from the arguments alone refuses in every mode, a preview included. |
| 3 | **"The product change is two lines" (*Current state and risks*, the wide-blast-radius bullet) becomes three touch points**: one `set_metadata_field` in `_archive_one`, one `findings.extend` in `check_doc`, and one refusal in `_cmd_mv`. | Factual correction. The sentence predates Q4's answer, which added D5's leg. |
| 4 | **The implementation log's *Setup questions — summary* table carried pre-D5 decision numbers** — Q2→D6, Q3→D7, Q6→D8, Q7→D6 — while this document has Q2→D3, Q3→D6, Q5→D7, Q6→D9, Q7→D3. Renumbered in place. | Factual correction. Q4's answer inserted D5 and renumbered everything after it; the log's summary table was not re-swept. A Phase-5 agent reading the log would chase the wrong decision. |
| 5 | **D9 / Q6's "Each already names `Archived-reason:` in its byte-identical list" is true of two of the three paragraphs, not three.** M25 — D4's and M27 — D6's paragraphs name it; M18's (as widened by M28 — D5) says "other metadata" generically. Phase 1 names **both** `Archived:` and `Archived-reason:` explicitly in that paragraph, so all three now read alike. The M26 *Safe explicit archive selection* paragraph's own byte-identity list gains `Archived:` for the same reason. | Factual correction, found by reading the three paragraphs rather than the claim about them. Q6's decision is unchanged and is now literally true; the fix strengthens the weakest of the three. |
| 6 | **"Three permitted neighbours" becomes FOUR everywhere it is derived.** Item (F) enumerates four — a rename within one dated directory, one end outside the archive subtree, segments that do not both parse, and **two spellings of one date** — the fourth being implied by Q2's parsed-date comparison rather than stated in D5's prose. Every derived surface (the Leg-2 deliverable, the Phase-2 file list, the Phase-6 exit, the Phase-9 dogfood instruction, the success criterion, Q4's adopted scope, `status.md` and `plan.md`) is swept from three to four. | The Phase-9 dogfood instruction is the one that mattered: at three it would have under-covered the neighbour a **raw-string** comparison would fail — the single case that distinguishes a correct predicate from the obvious wrong one. A count stated in eight places and locked in four tests must not disagree with either. |

### Step-1 resolutions (BINDING)

Nine questions were raised by Step-1 planning. **OQ-7 is an operator
decision.** OQ-1 was resolved by the conductor as a clear defect in D5's
literal wording. The remaining seven are conductor-resolved from the specs, the
frozen material, or the measured evidence. All nine are binding; Phases 2–10 do
not re-open them.

| # | Question | Resolution |
|---|---|---|
| OQ-1 | Where exactly does Leg 2's refusal sit, given `_cmd_mv` returns at `--dry-run` before the pre-flight? | **Conductor.** In `_cmd_mv`, immediately after `old_rel` / `new_rel` are derived and **before** the `--dry-run` branch. It refuses in every mode. Amendment 2 above; item (F). |
| OQ-2 | Which rule owns an `Archived:` value that does not parse? (D3 deferred this to Phase 1.) | **Conductor. `bad-date`**, message form C, **one** finding for that document and **no** drift finding. `bad-date` stays the single vocabulary entry for *a date field that does not parse*, exactly parallel to `Updated:`. The residual is named in the upgrade note: a hand-adopted foreign tree carrying a non-date `Archived:` value gains a new error — E6 measured **zero** occurrences anywhere, and `docs migrate` demotes a foreign one (D7). |
| OQ-3 | `parse_date` hardcodes the label `Updated:` in its message, so a malformed witness would name the wrong field. | **Conductor.** Add a keyword-only `label: str = "Updated"` parameter in Phase 5. Every existing call site keeps a **byte-identical** message — verified explicitly and locked by a test. One parser survives, and the two messages cannot drift. Item (H). |
| OQ-4 | Which root-relative expression does the rule use? | **Conductor.** The pure `_root_relative(path, root)`, never `path.resolve().relative_to(root.resolve())`: D3 forbids filesystem access and `body_link_findings` is the precedent. For every real `check_tree` walk the two agree, because paths come from `os.walk(root)`. Item (C) step 3. |
| OQ-5 | What about an `[archive] date_format` containing `/` (e.g. `%Y/%m/%d`)? | **Conductor. Document only.** One sentence in `convention.md` › *Archive subtree* saying the archive date must render as a single path segment, plus *Follow-ups* item 6. **No** code and **no** test: the shape is already broken pre-M28a and D3's first-segment reading pins it. Same treatment as defect E8. |
| OQ-6 | Does `convention.md`'s *Optional fields* table gain a row? | **Conductor.** Both an `Archived` row **and** the currently-missing `Archived-reason` row. |
| OQ-7 | Should Leg 2's predicate widen to refuse `docs mv archive/<date>/x.md archive/x.md` — leaving a dated directory for the archive root? | **OPERATOR. No — do not widen.** It stays a permitted neighbour, because refusing it would also refuse a legitimate reorganisation of the archive subtree, which the convention permits. Instead, all three of: (a) D8's residual sentence names this second, tool-driven residual honestly; (b) a Phase-2 lock proves Leg 1 **does** catch it (message form B) for witness-carrying documents; (c) it is registered as *Follow-ups* item 7. |
| OQ-8 | The implementation log's Q→D summary table contradicts this document. | **Conductor.** Corrected in place as a factual correction, and said to be one in the Phase-1 log entry. Amendment 4 above. |
| OQ-9 | How is the compatibility proof phrased so a later milestone's archive event cannot falsify it? | **Conductor.** As the durable property: `check_tree(docs/)` yields **zero** `archive-date-drift` findings over a tree with **at least 46** archived documents. Never as "no archived document carries `Archived:`" — that becomes false the first time a later milestone archives anything. The exact "46 carry no field" measurement stays in the Phase-9 dogfood record, as dated evidence. |

### (A) The field

- **Label: `Archived`**, rendered `Archived: <value>`. Permanent (D1 / Q1).
- **Value: the same `date_str`** `_archive_one` already receives —
  `archive_date.strftime(config.date_format)`, computed once in `_cmd_archive`
  and already used by `_archive_destination` to name the dated directory. One
  value, one source, one rendering. Never a second `strftime`, and never a
  `date.today()` re-read inside `_archive_one`.
- **Written by `_archive_one` to every member** (D2 / A2).
  `apply_archive_plan`'s `plan.reason if index == 0 else None` special case is
  **not** touched: the reason stays primary-only, the date does not.
- **Position: pinned by the `set_metadata_field` call order** in
  `_archive_one`, which becomes `Lifecycle` → `Updated` → **`Archived`** →
  `Archived-reason` (conditional). `set_metadata_field` appends a new inline
  label at the end of the inline run and replaces an existing one in place, so
  an archived document reads:

```
Lifecycle: archived
Role: <role>
Project: <project>
Updated: <date_str>
Archived: <date_str>
Archived-reason: <reason>
```

- **Pinned edge cases.** A document that **already** carries `Archived:` has it
  replaced in place — the archive event's date wins. A `Related:` bare-label
  group still follows the inline run, because `set_metadata_field` inserts
  before the first bare-label group.
- **No other verb writes it.** `docs new`, `docs stamp`, `docs touch`,
  `docs relate` and `docs migrate` never do, and there is no backfill (D6, D7).

### (B) The vocabulary — three changes and one deliberate non-change

| Surface | Change |
|---|---|
| `_BUILTIN_METADATA_FIELDS` | gains `"Archived"` — M25's `Revision:` reason verbatim: a label the tool writes must never trip the tool's own allowlist warning |
| `parse()`'s `known` set | **unchanged** — the field surfaces via `Doc.extra` into `doc_to_json`'s `extra_fields`, exactly as `Archived-reason:` and `Revision:` already do. M28a adds no field to any JSON record |
| migrate's supersession set `_REQUIRED_METADATA_FIELDS` | **unchanged** — so a foreign `Archived:` line is demoted by `_render_migrated_metadata_section` to `Migrated-Archived:` under `## Migrated metadata`, preserved but never promoted (D7) |
| `Finding`'s docstring rule enumeration, and `cli.md`'s `rule` table row | gain `archive-date-drift` |

### (C) Leg 1 — the corroboration predicate

Two pure helpers. `archive_dir_date` is shared with Leg 2, so the two legs can
never disagree about what a dated archive directory is.

**`archive_dir_date(rel, config)`** — the date of the dated archive directory
`rel` sits in, or `None`:

1. `_is_archived_rel(rel, config)` is False → `None`. (`Config` validates that
   `archive_dir` is a **single path segment**, which is what makes step 3
   unambiguous.)
2. `parts = rel.split("/")`; `len(parts) < 3` → `None`. This is what makes
   `archive/x.md` — a document directly in the archive root — carry no date.
3. `parse_date(parts[1], config.date_format)` → the date; `MetadataError` →
   `None`.

Step 3 is the D3 pin honoured literally: the **same** `parse_date` path
`check_doc` already uses for `Updated:`, always with `config.date_format`,
never through `parse()`'s hardcoded default (defect E8, *Follow-ups* item 1).
It deliberately does **not** copy `detect_archive_layout`'s hardcoded
`datetime.strptime(parts[1], "%Y-%m-%d")`.

**`archive_date_findings(path, metadata, root, config)`** — the evaluation
order is BINDING:

1. `recorded = metadata.get("Archived")`. Not a `str`, or blank → `[]`
   (**present-only**, D6). This also covers a bare `Archived:` bullet group,
   which `parse_metadata_block` yields as a `tuple` — pinned as *absent*,
   mirroring how `check_doc` already silently skips a tuple-valued `Updated:`.
2. `parse_date(recorded, config.date_format, label="Archived")` → on
   `MetadataError`, return **one `bad-date`** finding (form C) and stop. **No**
   drift finding for that document (OQ-2).
3. `rel = _root_relative(path, root)` — **not**
   `path.resolve().relative_to(root.resolve())`. `body_link_findings` is the
   precedent, and `.resolve()` is filesystem access, which D3 forbids. For
   every real `check_tree` walk the two expressions agree, because paths come
   from `os.walk(root)` (OQ-4).
4. `dir_date = archive_dir_date(rel, config)`. Equal to the recorded date →
   `[]`. `None` → form B. Otherwise → form A.

**No filesystem access of any kind**, in either helper — pinned by a purity
test that monkeypatches `Path.exists` / `Path.is_file` / `Path.open` to raise.

Pinned consequences:

- **Deeper paths corroborate.** `archive/<date>/sub/x.md` reads `parts[1]`.
- **Parsed, never string, equality.** `archive/2026-1-1/` corroborates
  `Archived: 2026-01-01` under the default format — `strptime` accepts
  unpadded fields.
- **`archive-date-drift` and `status-drift` are independent** and may both fire
  on one document (Q7).
- A `malformed` document (no H1) never reaches the rule: `check_doc` returns
  early.
- `duplicate-field` still fires independently on a doubled `Archived:` label;
  the rule reads the last occurrence, as every rule does.
- **The compatibility proof is phrased as a durable property** (OQ-9):
  `check_tree` over this repository's `docs/` yields **zero**
  `archive-date-drift` findings over a tree with **at least 46** archived
  documents.

### (D) Leg 1 — the rule's position, severity and cardinality

`findings.extend(archive_date_findings(path, metadata, root, config))` goes
**immediately after the lifecycle/location `status-drift` block** and
**before** the M25 `duplicate-field` block, so the two location-versus-metadata
rules stay adjacent — M27's reason for placing `body_link_findings` immediately
after the `broken-ref` group. The frozen intra-document order asserted by
`test_check_tree_findings_grouped_by_path` is unaffected.

Severity `error`, exit **2** through the existing `exit_code_for`. **One
finding per document** — a document has one recorded date and one location. No
opt-out, no `check_tree` second pass, no graph traversal, and `Finding`'s key
set stays closed at four (D4).

### (E) The frozen message catalogue

Leg 1 — the `Finding.message` field; the human line is
`  error: [<rule>] <message>`:

```
A  archive-date-drift : Archived: <recorded> but the file is in <archive_dir>/<segment>/ (move it back, or correct the recorded date)
B  archive-date-drift : Archived: <recorded> but the file is not under a dated <archive_dir>/ directory (move it back, or remove the field)
C  bad-date           : Archived: malformed date '<value>' (expected <date_format>)
```

`<recorded>` and `<segment>` are the raw strings as written on disk — both
already proven to parse for form A. Form A is the headline case and names
**both** dates. Form B covers both non-dated shapes — outside the archive
subtree, and an undated subdirectory of it — which is Q7's "one rule, two
message forms". Form C is `parse_date`'s **own** message with its `label`
argument set to `Archived` (OQ-3), so there is exactly one date-error message
in the tool and it cannot drift from `Updated:`'s.

Leg 2 — two lines on stderr, both printed **even under `--quiet`**, as every
refusal is:

```
docs: mv: <old-rel> -> <new-rel> crosses dated archive directories (<D1> to <D2>); refusing before any write
docs: mv: the dated directory records when a document was archived; to correct a genuinely mis-dated archive, move the file by hand, correct its `Archived:` line, and re-run `docs check`
```

`<D1>` / `<D2>` are the raw directory segments. The two-line shape is
`docs archive`'s leg-1 precedent — a per-condition line, then a second line —
and it is what makes "the escape ships in the same breath as the refusal" true
in the CLI as well as in both specs.

### (F) Leg 2 — the predicate, its position and its permitted neighbours

`cross_dated_archive_move(old_rel, new_rel, config)` returns
`(seg_old, seg_new)` — the two raw directory segments — iff
`archive_dir_date(old_rel, config)` and `archive_dir_date(new_rel, config)` are
both non-`None` **and different**; otherwise `None`. Path arithmetic only: no
metadata, no filesystem, no graph, and therefore independent of whether the
moving document carries the witness.

**Position (BINDING, amendment 2).** Evaluated in `_cmd_mv` immediately after
`old_rel` / `new_rel` are derived and **before** the `--dry-run` branch — the
plan-before-move window, where nothing has been written and no `--json` record
has been emitted. Three reasons, each with a precedent on disk:

1. It is an **invalid invocation**, not a state-dependent consequence —
   decidable from the two arguments alone, exactly like `docs archive`'s
   `--cascade-only` shape check, which `cli.md` pins as "a MALFORMED
   INVOCATION, not a selection outcome, so it refuses in every mode — a
   preview included".
2. `_cmd_mv` returns at its `--dry-run` branch *before* `preflight_move_plan`.
   Inside the pre-flight, `docs mv --dry-run` would print `would move …` at
   exit 0 for an operation the apply refuses.
3. Before the walk, it gives M26's stated precedence — naming the document the
   operator asked for is strictly more actionable — and makes exclusion
   irrelevant to the predicate, which is exactly what *Also settled* pins:
   exclusion governs the walk, never the predicate.

It is **not** placed inside `preflight_move_plan`, which `_cmd_archive` also
calls: archive never moves an already-archived member, so the predicate would
be dead code there.

Exit **2**, zero bytes written, no `--json` record. **Permitted neighbours** —
D5's three, plus the fourth Q2's parsed-date comparison implies:

| # | Move | Verdict |
|---|---|---|
| 1 | a rename within one dated directory (`archive/D/a.md` to `archive/D/b.md`, and to `archive/D/sub/b.md`) | completes |
| 2 | one end outside the archive subtree | completes; `status-drift` owns the aftermath, and this leg does not double-report it |
| 3 | the two segments do not both parse (`archive/D/x.md` to `archive/misc/x.md` or to `archive/x.md`, either direction) | completes — **and this is D8's second residual**, named in D8 and registered as *Follow-ups* item 7 |
| 4 | two spellings of one date (`archive/2026-01-01/` to `archive/2026-1-1/`) | completes — the predicate compares **parsed** dates (Q2) |

### (G) The author-facing surface

- `cli.md` › `docs archive`: step 2 records the date on **every** document the
  operation moves; a following paragraph pins the block position, the
  every-member rule, the replace-in-place edge case, and that no other verb
  writes it.
- `cli.md` › `docs check`: an `archive-date-drift` bullet in the rule list, the
  `rule` table row, the exit-2 line, the built-in always-allowed field set —
  and, because form C exists, the `bad-date` bullet widens from "`Updated:` not
  parseable" to "a date field that does not parse — `Updated:`, or `Archived:`".
  A new *Archive-date corroboration* subsection carries the three conditions,
  the two message forms verbatim, the present-only contract, the independence
  from `status-drift`, and its own *Upgrading from 1.x*.
- `cli.md` › `docs mv`: a *Cross-dated archived relocations* subsection
  carrying the refusal, its exit code, its zero-bytes guarantee, both frozen
  lines, its four permitted neighbours **and its by-hand escape in the same
  subsection**; one amended row in the `docs mv` exit-code table and one in the
  global exit-code summary.
- `convention.md` › *Optional fields*: an `Archived` row and the
  previously-missing `Archived-reason` row (OQ-6).
- `convention.md` › *Archive subtree*: the witness, the present-only rule, the
  fact that M28a never requires a dated directory, D5's refusal with its
  escape, and the single-path-segment constraint on `[archive] dir` and
  `[archive] date_format` (OQ-5).
- `convention.md`: **all three** archived-immutability paragraphs name
  `Archived:` on the byte-identical side beside `Archived-reason:`, and M26's
  *Safe explicit archive selection* byte-identity list gains it too
  (amendment 5).
- **Authoring traps** (M28 item (M), still binding): no `](../` and no
  link-shaped span in either spec — both ship byte-identically in the wheel and
  are validated by the dogfood `docs check`. Every `Archived:` sample and every
  `docs mv archive/...` example goes in a fence or in inline code.

### (H) The Phase-5 signatures

```python
def parse_date(
    value: str, date_format: str = "%Y-%m-%d", *, label: str = "Updated"
) -> date:
    """Parse a date string, raising MetadataError on malformed input.

    `label` names the field in the error message (M28a — OQ-3). Every
    pre-M28a call site keeps a byte-identical message.
    """


def archive_dir_date(rel: str, config: Config) -> date | None:
    """The date of the dated archive directory `rel` sits in, or None (M28a — D3)."""


def archive_date_findings(
    path: Path,
    metadata: Mapping[str, str | tuple[str, ...]],
    root: Path,
    config: Config,
) -> list[Finding]:
    """`archive-date-drift` for one document (M28a — D3). Pure; no filesystem access."""


def cross_dated_archive_move(
    old_rel: str, new_rel: str, config: Config
) -> tuple[str, str] | None:
    """The two dated-directory segments when a move crosses them, else None (M28a — D5)."""
```

## Follow-ups recorded for later milestones

Raised during setup, judged out of M28a's scope, and deliberately **not**
implemented here.

| # | Follow-up | Home |
|---|---|---|
| 1 | **The `date_format` asymmetry between `parse()` and `check_doc` — a pre-existing defect, explicitly NOT fixed here** (E8). On a tree with a non-default `[archive] date_format`, `docs archive thing.md --date 04-03-2026` writes `attic/04-03-2026/thing.md` with `Updated: 04-03-2026` correctly and **then exits 2** on the INDEX refresh: `INDEX refresh failed: … Updated: malformed date '04-03-2026' (expected %Y-%m-%d)`. Root cause: `parse()` parses `Updated:` with the hardcoded default while `check_doc` honours `config.date_format`. It predates M28a, it is unowned by any milestone, and M28a does **not** touch it — instead D3 pins that **both sides** of the drift comparison are parsed with `config.date_format` via the same path `check_doc` already uses, so M28a's own logic never depends on the broken one. Registered separately in `feedback-log.md` (2026-08-15). **A milestone that fixes this must also update `tests/test_cli_archive.py::test_archive_renders_the_witness_in_the_trees_date_format`**, which asserts the exit-2 INDEX-refresh failure explicitly so that the witness half of that test cannot be satisfied by the defect being fixed elsewhere. Fixing E8 will therefore break it, deliberately, and its expected exit code and stderr are what change. | Later |
| 2 | **Backfilling the witness onto pre-2.0 archived documents** (Q3). Refused here because no honest source for the date exists. If a later milestone wants it, the only defensible source is the repository's own history, which makes it a git-aware operation the charter currently keeps out (*"Git owns history; `docs` owns lifecycle"*). | Later |
| 3 | **`docs migrate --apply` writing the witness for the archive-shaped files it relocates** (Q5). Refused here because migrate's date is inferred from `Updated:` or mtime. It becomes available if migrate ever gains a date an operator asserts per file rather than per run. | Later |
| 4 | **Three inlined copies of the archive-subtree predicate** (E7). `check_doc`, the `docs list` walk, and `docs project set` each spell `rel == config.archive_dir or rel.startswith(config.archive_dir + "/")` inline, although `_is_archived_rel` already provides exactly that. A `/simplify` candidate M28a's Phase 10 should evaluate, not a defect. | M28a Phase 10 / Later |
| 5 | **`docs migrate --apply` rewriting references across its own moves** (M28 *Follow-ups* item 1, unchanged and still deferred). | Later |
| 6 | **An `[archive] date_format` that renders with a `/`** (e.g. `%Y/%m/%d`). `Config` already validates that `[archive] dir` is a single path segment, but nothing validates the rendered date. Such a tree's dated directory is two segments deep, which every archive-subtree rule in this convention — `status-drift`, `_is_archived_rel`, `detect_archive_layout`, and now M28a's corroboration — reads as one. The shape is already broken pre-M28a and D3's first-segment reading pins it, so M28a adds **no** code and **no** test for it and documents the constraint in `convention.md` › *Archive subtree* instead. Same treatment as defect E8 (Phase-1 resolution OQ-5). | Later |
| 7 | **A tool-driven relocation out of a dated directory that is not cross-dated** — `docs mv archive/<D>/x.md archive/x.md`, or into an undated archive subdirectory. Permitted by design (D5's third neighbour), because refusing it would also refuse a legitimate reorganisation of the archive subtree; but it destroys the only archive-date record a pre-2.0 archived document has, and `status-drift` is silent because the destination is still inside the archive subtree. D8's second residual, made explicit by Phase-1 amendment 1. Closable only by a narrower refusal that distinguishes reorganisation from erasure — which needs a signal the two paths alone do not carry (operator decision, OQ-7). | Later |

## Testing and quality gate

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q
.venv/bin/docs check --root docs
```

Additional gates: the present-only silence proof over every archived document
in every committed fixture tree **and** over this repository's own 46;
byte-identity assertions on the witness across `docs touch`, `docs relate`'s
audited archived-endpoint repair, and M18–M28's widened move-driven exception;
a metadata-block line-order assertion with and without `--reason`; a cascaded
closeout asserting every moved member carries the witness while
`Archived-reason:` stays on the primary alone; non-default `date_format` and
`[archive] dir` locks on both the writer and the rule; `docs migrate` non-write
and demotion locks; the closed four-key `Finding` record and the unwidened
`archive --json` key set; the pre-M28a fixture-tree no-new-findings sweeps and
their hand-written registration tuple; `docs archive --help` /
`docs check --help` / `cli.md` surface parity; bundled `references/cli.md` and
`references/convention.md` byte identity; and the live INDEX snapshot.

## Success criteria

- A document archived by 2.0.0 carries the archive date as a structured field,
  in the tree's `date_format`, at the pinned block position — and so does
  **every** member of a cascaded closeout, not only the primary.
- **Leg 1:** a relocated archived document that carries the witness is a hard
  `docs check` error naming both the recorded date and the dated directory it
  now sits in, at exit 2 — proven by reproducing E1d's relocation by hand,
  which today leaves `docs check` clean.
- A normally archived document, and every one of this tree's **46** pre-witness
  archived documents, are silent. A 1.x tree gains zero findings from this rule
  on upgrade.
- The declined rule stays declined and is proven not to have been smuggled in:
  the **7** cross-dated `pairs-with` edges this tree carries produce nothing.
- The witness survives every operation the convention permits on an archived
  document — a `docs touch`, a `docs relate` audited repair, and a move-driven
  destination rewrite — byte-identically, and all three convention paragraphs
  say so.
- `docs migrate --apply` writes no witness, and a foreign `Archived:` line is
  demoted rather than promoted.
- `docs check --json`'s record key set is unchanged, `archive --json`'s
  top-level key set is unchanged, no new flag exists, and no opt-out exists.
- **Leg 2:** `docs mv` refuses a cross-dated archived relocation before any
  write, naming both dates and leaving the tree byte-identical — proven on a
  document that carries the witness **and** on one that does not, which is the
  case leg 1 alone can never reach. All **four** permitted neighbours complete:
  a rename within one dated directory, a move `status-drift` already catches, a
  move whose segments do not both parse, and two spellings of one date
  (amendment 6). Every other existing `docs mv`
  behaviour is byte-stable, and the by-hand escape is documented in the same
  paragraph as the refusal in both `cli.md` and `convention.md`.
- The live tree and every fixture tree pass unchanged apart from the
  deliberately drifted fixtures; full quality, compatibility and dogfood gates
  are GREEN; specs and bundled mirrors byte-identical; and `feedback-log.md`
  issue #1's last open finding is closed, leaving M29 ready to publish the
  train.
