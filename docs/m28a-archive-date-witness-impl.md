# M28a — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-08-15

Related:
- child-of: m28a-archive-date-witness.md
- pairs-with: m28a-archive-date-witness.md
- pairs-with: status.md
- references: feedback-log.md

## Overview

Chronological implementation log for M28a — Structured archive-date witness.
Append one evidence-backed section per TDD phase; keep the progress table and
the milestone checklist synchronized.

## Implementation metadata

- Project: docs
- Milestone: M28a — Structured archive-date witness
- Started: 2026-08-15 (milestone setup; no TDD phase started)
- Progress: **Milestone setup complete, with all seven setup questions
  RESOLVED (Q4 by the operator; Q1 auto-resolved under the
  naming-with-an-obvious-default rule; Q2/Q3/Q5/Q6/Q7 conductor-resolved).
  Phase 1 — Define Contract is next and does not re-open them.** Setup
  measured this repository read-only and reproduced the reported drift on
  throwaway copies, producing nine pieces of evidence (**E1–E9**). The headline
  is that **M28 removed the accidental tripwire**: the same archived-document
  relocation that left 13 `broken-body-link` errors at exit 2 under pre-M28
  `main` (`58955ef`) now completes at exit 0 with `docs check` **clean** under
  merged `main` (`b1ec74b`). M28a is the consequence of M28, which is why it
  blocks M29 rather than trailing it — shipping M28 in 2.0.0 without M28a would
  leave the release strictly quieter about archived-document relocation than
  1.8.0 was. **Q4's answer changed the milestone's shape**: M28a ships **two
  legs** — the witness plus a narrow `docs mv` refusal (D5) — so the tool's own
  relocation path is closed for every archived document, not only for those
  carrying the field. **Q1 fixes the label as `Archived:`**, permanently, since
  the convention never renames a built-in.
- Source: `feedback-log.md` issue #1 finding 3's archive-date half — the only
  one of the issue's four findings still open — routed to a new milestone
  M28a on 2026-08-15, with the reporter's own suggested rule declined in the
  same note.
- Branch: `m28a/milestone-setup` for setup; implementation branches are chosen
  when Phase 1 begins.

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Pending | — | Freeze **both legs**. Leg 1: the field's name (`Archived:`), its `date_format` rendering, its position in the metadata block, and the every-member write rule; the vocabulary changes (`_BUILTIN_METADATA_FIELDS`, `parse()`'s `known` set, `[vocabulary] add_fields`); the `archive-date-drift` predicate as a corroboration test, its severity and exit, its position in `check_doc`'s append order, its independence from `status-drift`, and its frozen message forms. Leg 2: D5's `docs mv` refusal predicate, its frozen message beside `archive-date-drift`'s, its exit code, its position inside M28's existing plan-before-move pre-flight, its three enumerated permitted neighbours and its documented escape. Plus the present-only compatibility contract; `docs migrate`'s non-write; the three archived-immutability paragraphs that must name the field; and the Phase-5 signatures. |
| 2. Write Tests (RED) | Pending | — | **Both legs.** Pure-rule unit tests over every corroboration shape; `docs archive` writer locks including a cascaded closeout where **every** member carries the field; D5's refusal proven with **and** without the witness present, with zero bytes written, plus the three permitted neighbours proven to complete; the present-only silence lock over all 46 field-less archived documents; `migrate` non-write and demotion locks; byte-identity locks for `touch` / `relate` / the M18-M28 widened exception; the closed four-key `Finding` record. |
| 3. Create Data/Fixtures | Pending | — | New `archivedate-*` trees, one semantic each — `-clean`, `-drifted`, `-absent`, `-outside`, `-undated`, and `-two-dated-dirs` for D5's refusal and its permitted same-directory rename — plus the hand-written registration tuple and the two whole-corpus sweep tests that a deliberately drifted tree would otherwise trip. |
| 4. Run Tests (RED Baseline) | Pending | — | Classified failure set against the 1341-test baseline; every GREEN-at-baseline lock named. |
| 5. Update Base Interfaces | Pending | — | `Archived` into `_BUILTIN_METADATA_FIELDS`; a config-aware dated-archive-directory reader; the pure `archive_date_findings(...)` helper — wired nowhere, so the CLI tests stay honestly RED at the seam. |
| 6. Implement Offline/Core Path | Pending | — | One `set_metadata_field` call in `_archive_one` at the frozen position; one `findings.extend` in `check_doc` at the frozen position; and D5's refusal inside `docs mv`'s existing plan-before-move pre-flight, before the first byte moves. |
| 7. Update Tool/Wrapper Layer | Pending | — | `cli.md`'s archive step list, check-rule list, `rule` table row and built-in-field set; `convention.md`'s *Optional fields*, *Archive subtree* and the **three** archived-immutability paragraphs; **both specs' `docs mv` paragraphs carrying D5's refusal, its exit code and its by-hand escape together**; the migrate section; the upgrade recipe naming the one behaviour change; both byte-identical skill mirrors; `UNRELEASED` CHANGELOG; a dated note closing `feedback-log.md` issue #1. No new flag, no version bump. |
| 8. Run Tests (GREEN) | Pending | — | Full product and quality gates with exact counts; mechanical no-regression proof against the 1341 pre-existing ids. |
| 9. Integrate / Accept / Dogfood | Pending | — | Replay E1d and prove `docs mv` now **refuses** it with the tree byte-identical, on a document with **and** without the witness; reproduce the relocation by hand on a witness-carrying document and prove `docs check` exits 2 naming both dates; prove the three permitted neighbours still complete; prove all 46 field-less archived documents stay silent; run a real closeout and prove every member carries the field; prove `migrate --apply` writes none; measure the added `docs check` runtime. The real tree is never written to. |
| 10. Quality, Docs, Refactor | Pending | — | `/simplify`, close `architecture.md` and `test-strategy.md`, completion summaries, hand to M29. |

## Setup record — 2026-08-15

### Objective

Bring the registered M28a draft stub up to full milestone-task-plan depth and
create this log, without starting Phase 1. M28 is implementation-complete and
merged to `main` (`b1ec74b`), so M28a is the last implementation milestone in
the v2.0 train before the M29 publish. The stub's binding scope, its two
declines, and its numbering note are carried forward rather than replaced; its
three "Open questions for M28a Phase 1" are carried forward as Q1, Q2 and Q3
and evaluated against the specs and the M25–M28 precedent.

### Actions taken

- Read the milestone's inputs end to end: `plan.md`'s v2.0 narrative and M28a
  row, `charter.md`, the pinned specs (`cli.md`, `convention.md`,
  `architecture.md`, `test-strategy.md`), `status.md`, and `feedback-log.md` —
  issue #1 in particular, whose finding 3 splits into a link half M27 fixed
  and an archive-date half routed here, and whose *Design rationale* bullet
  declines the reporter's own suggested rule outright.
- Read the code M28a must extend: `_BUILTIN_METADATA_FIELDS`,
  `set_metadata_field`, `append_revision_entry`, `parse()`'s `known` set,
  `parse_date` and the `[archive] date_format` config, `_cmd_archive`'s
  numbered check order, `plan_archive` / `apply_archive_plan` / `_archive_one`
  / `_archive_destination`, `check_doc` and `body_link_findings`, `Finding` /
  `finding_to_json` / `exit_code_for`, `_is_archived_rel` /
  `_in_archive_subdir` / `detect_archive_layout`, and `plan_migration` /
  `apply_migration` / `infer_lifecycle` / `insert_metadata_block`.
- Ran a **read-only** census over the live `docs/` tree and all 46 committed
  fixture trees: archived-document counts per dated directory, `Updated:`
  against directory date, `Archived-reason:` coverage, and the full
  archived↔archived `Related:` graph filtered to edges spanning different
  dated directories.
- Reproduced the reported drift on **throwaway copies** of this tree outside
  the repository, and enumerated all four ways a document can move relative to
  the archive subtree, measuring each. Additionally replayed the same
  relocation against the **pre-M28** CLI at `58955ef` to measure what M28
  changed. No repository file was mutated during setup; the live tree was only
  read.
- Expanded *Binding scope* into nine decisions (D1–D9), added *Out of scope*,
  the E1–E9 evidence with an *Evidence → regression coverage* table, the
  ten-phase TDD plan with per-phase objective / files / exit, the phase
  checklist, the testing gate, evidence-anchored success criteria, and
  *Follow-ups recorded for later milestones*.
- Carried the registered stub's three "Open questions for M28a Phase 1"
  forward as Q1, Q2 and Q3, and added Q4–Q7 for the scope and contract
  decisions the reading surfaced. Resolved Q2, Q3, Q5, Q6 and Q7 as conductor
  decisions determined by the convention, the charter, the measured evidence
  and the M25–M28 precedent, and surfaced **Q1** (the field's permanent public
  name) and **Q4** (whether `docs mv` also *refuses* the one silent
  relocation) with recommendations and the alternatives that lost. **Both were
  then answered and folded in**: Q1 auto-resolved to `Archived:` under the
  naming-with-an-obvious-default rule, with `Archived-date:` recorded as the
  rejected alternative so the label's permanence is on the record; and **Q4
  resolved by operator decision to adopt BOTH legs**, which promoted the
  `docs mv` refusal from an option into binding scope as **D5**, renumbering
  the later decisions and adding its own deliverable, fixtures, RED tests,
  phase items and success criterion.
- Registered the one defect setup found that M28a deliberately does **not**
  fix — the hardcoded-ISO `Updated:` parse in `parse()` that makes
  `docs archive` exit 2 on a non-default-`date_format` tree (E8) — as a dated
  entry in `feedback-log.md` and as *Follow-ups* item 1, and pinned in D3 that
  M28a's own comparison parses both sides with `config.date_format` so it never
  depends on the broken path.
- Kept the reciprocal `follows` / `precedes` and `depends-on` / `required-by`
  edges intact, flipped the milestone to `Lifecycle: active`, and added the
  milestone ↔ log pair edges.
- Scaffolded this log with `docs new log m28a-archive-date-witness-impl`,
  bumped dates and validated with `docs touch … --check`, and refreshed the
  frozen dogfood INDEX snapshot `tests/fixtures/expected/docs-INDEX.md` for
  the new log entry — the same snapshot refresh the M25, M26, M27 and M28
  setups performed.
- Updated the trackers: `status.md` and `plan.md` now describe M28a as in
  flight with its plan and log linked.

### Current-tree evidence (docs-cli 1.8.0 with M25–M28 merged at `b1ec74b`)

| Evidence | Measurement | Why it matters | Bears on |
|---|---|---|---|
| **E1** | All four ways a document can move relative to the archive subtree, measured on throwaway copies. (a) `docs archive` on an already-archived primary: **refuses**, exit 2, `is already under the archive subtree; refusing before any write`. (b) `docs mv archive/2026-05-25/m9-pypi-publish-log.md m9-moved-out.md`: completes, and `docs check` reports **`status-drift`**, exit 2. (c) `docs mv definition-of-ready.md archive/2026-07-03/definition-of-ready.md`: completes, and `docs check` reports **`status-drift`**, exit 2. (d) `docs mv archive/2026-05-25/m9-pypi-publish.md archive/2026-07-03/m9-pypi-publish.md`: completes at exit 0, and `docs check` exits **0**. | **Exactly one of the four is silent**, and it is the one the issue reported. The hole is not a hypothetical: it is reachable through a shipped verb, in one command, on this repository, today. | D1, D2, Q4 |
| **E2** | The same relocation (d), replayed against the **pre-M28** CLI at `58955ef`: `moved … (4 reference(s) rewritten)`, then `docs check` reports **13 `broken-body-link`** errors across 6 documents, exit 2. Against merged `main` (`b1ec74b`): `13 destination(s) in 6 document(s), 4 Related: bullet(s)` rewritten, then `docs check` **no violations found**, exit 0. | **M28 removed the accidental tripwire.** The drift used to be loud only because the tool could not rebase prose links; M28 correctly fixed that and, in the same stroke, made this class of damage invisible. M28a is the consequence of M28, which is why it belongs in the same train and before the publish. | D1, D2 |
| **E3** | **29 of the 46** archived documents in this tree carry an `Updated:` value that differs from their dated directory — all 29 now read `2026-08-14`, the date of M27 — D6's one-time body-link migration. Separately, `docs touch archive/2026-05-20/m1-parser-and-index.md` bumps `Updated:` from `2026-08-14` to `2026-08-15` at exit 0 with `docs check` clean. | `Updated:` **cannot** be the witness. It is bumped by the archive move itself, by the one-time migration, and by an ordinary `docs touch` — three unrelated writers, one of which is a general-purpose verb. A field any verb may move cannot corroborate a location. | D1, D3 |
| **E4** | Only **13 of the 46** archived documents carry an `Archived-reason:` line, because M26 — D1 writes it to the **primary only**: `apply_archive_plan` passes `plan.reason if index == 0 else None`. | `Archived-reason:` cannot be the witness either — and, more importantly, the witness must **not** copy its primary-only rule. The reporter's real-tree replay was a coherent archived **trio split across two dated directories**; its cascaded members are exactly the documents that would carry nothing. | D3, D4 |
| **E5** | **7** archived↔archived `pairs-with` edges in this tree span **different** dated archive directories, on a tree at `docs check` exit 0: `m7↔m4`, `m8↔m5`, `m8↔m6`, `m9↔m6`, `m12↔m11`, `m12↔m10`, `m13↔m12`. No other `Related:` verb produces such an edge here. | Quantifies the decline the feedback log already recorded: the reporter's suggested rule — warn when `pairs-with` partners sit in different dated directories — would emit **7 findings on a correct tree**, failing the charter's *never cry wolf* criterion. The witness detects the same drift objectively and emits **0** here. | D2 (decline), D5 |
| **E6** | **Zero** occurrences of an `Archived:` metadata label anywhere: not in any of `docs/`'s 73 documents, not in the 46 committed fixture trees, not in the bundled skill. The `unknown-field` rule is **opt-in** — `check_doc` gates the whole rule on `if config.fields:` — and this tree sets no `add_fields`, so it is off here. | The label is free, and the compatibility surface is one line: `Archived` must join `_BUILTIN_METADATA_FIELDS` for the same reason M25 added `Revision` — *a label the tool writes must never trip the tool's own allowlist warning* — and for no other. | D3, D8 |
| **E7** | There is **no rule registry**: `docs check`'s 13 rule ids are inline `findings.append(Finding(...))` calls inside `check_doc`, `body_link_findings` and `reciprocity_findings`; `Finding` is frozen at four fields and `finding_to_json` serialises exactly those. There is **no field-order list and no `field-order` rule**: `set_metadata_field` appends a *new* inline label at the end of the inline run, so a new field's position is decided solely by the order of the `set_metadata_field` calls in `_archive_one`. And the only dated-archive-directory parser in the codebase, `detect_archive_layout`, is hardcoded to the literal `"archive"` and `"%Y-%m-%d"`, ignores `config`, and lives in the migrate half. | Three concrete consequences for Phase 1: the rule is one helper plus one `extend` at a contractual position; the block position must be **pinned** because nothing else pins it; and the corroboration test needs a **config-aware** sibling honouring `config.archive_dir` and `config.date_format`, not a fourth copy of a config-blind predicate. | D4, D6, Phase 5 |
| **E8** | On a throwaway tree with `[archive] dir = "attic"` and `date_format = "%d-%m-%Y"`, `docs archive thing.md --date 04-03-2026` correctly writes `attic/04-03-2026/thing.md` with `Updated: 04-03-2026` — and then **fails**: `INDEX refresh failed: … Updated: malformed date '04-03-2026' (expected %Y-%m-%d)`, exit 2. Root cause: `parse()` parses `Updated:` with the hardcoded default while `check_doc` honours `config.date_format`. | A **pre-existing defect**, out of scope here, but squarely on this milestone's path. It is the reason the contract must say the witness is rendered in the tree's `date_format` and compared as **parsed dates** — M25's *two date spellings in one file would be a defect* — rather than by string equality, so M28a adds no third spelling and no fourth parser. Recorded as *Follow-ups* item 1 **and** as its own dated `feedback-log.md` entry, since no milestone owns it. D3 pins that M28a parses both sides with `config.date_format`, never through the broken path. | D3, D6 |
| **E9** | Ten of the 46 fixture trees carry an archive subtree, holding **11** archived documents plus one archived `INDEX.md`, every one at a single `archive/<ISO>/`; **no fixture anywhere carries an archive-date field**, because none exists. Meanwhile `docs migrate --apply` defaults a document to `Lifecycle: archived` **from the directory name alone** whenever no in-file `Lifecycle:` line carries a built-in value (`infer_lifecycle(metadata, in_archive)` with `in_archive` from `_in_archive_subdir`, i.e. a first path segment of `archive` / `archived` / `project-history`) and picks each file's `archive/<date>/` bucket from the file's own `Updated:` line or, failing that, its **mtime** — which on a fresh clone is today. | Phase 3 must author every corroboration shape deliberately, exactly as M27 — E8 and M28 — E8 forced. And it settles Q5 by measurement: a `migrate` that wrote the witness would stamp **today's date** as the archive date on every historical document it adopts — the precise falsification this milestone exists to prevent. | Phase 3, D7, Q5 |

### Verification

- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 48 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues found in 49 source files.
- `.venv/bin/python -m pytest -q` — 1341 passed.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).

### Decisions / issues

- **The milestone's premise is now measured, not asserted.** The registered
  stub said M26 "already prevents the tool from relocating archived
  documents", making M28a "defence in depth against paths the convention
  forbids but nothing currently detects". That is true of `docs archive`
  (E1a) and **not** true of `docs mv` (E1d): one shipped command relocates an
  archived document between dated directories, rewrites all 13 stale
  destinations and 4 `Related:` bullets so nothing dangles, exits 0, and
  leaves `docs check` clean. The *Current state and risks* section is
  corrected accordingly, and the correction is what makes Q4 a real question
  rather than a formality.
- **M28 is why this is urgent.** E2 measures the same operation before and
  after M28: 13 hard errors and exit 2 before, zero findings and exit 0 after.
  Nothing regressed — M28 did exactly what it promised — but the tree's only
  accidental alarm for this class of damage was a side effect of the very
  defect M28 fixed. Shipping M28 in 2.0.0 without M28a would ship a release
  that is strictly quieter about archived-document relocation than 1.8.0 was.
- **Neither existing field can carry the witness.** `Updated:` is written by
  the archive move, by the M27 — D6 migration and by any `docs touch`
  (E3); `Archived-reason:` is free text and lands on the primary only, so it
  covers 13 of 46 archived documents and none of a cascaded set's members
  (E4). The witness therefore has to be a new field, and it has to be written
  to **every** document an archive operation moves — which is the one place
  M28a deliberately does not copy `Archived-reason:`'s rule.
- **The reporter's own rule stays declined, and now has a number.** E5
  measures **7** archived↔archived `pairs-with` edges spanning different dated
  directories on a tree `docs check` calls clean. The operator declined the
  rule in the feedback entry on exactly this reasoning; setup confirms it
  quantitatively rather than restating it.
- **Q1 — the field is `Archived:`, and the name is now binding.** The
  convention states that `.docs.toml` may *add* to vocabularies but never
  remove or rename built-ins, so the label is permanent from the moment 2.0.0
  ships and will appear in every archived document this tool ever writes;
  fixing it at setup rather than in Phase 1 is deliberate. `Archived:` is
  exactly parallel to `Updated:` (a past-participle label whose value is a
  date, rendered in the tree's `date_format`) and pairs with
  `Archived-reason:` as event and reason. **`Archived-date:` is recorded as
  the rejected alternative**: unambiguous against a boolean reading, but
  `Updated:` already establishes that a date field in this block does not name
  its own type, and `-date` would make it the only field in the vocabulary
  that does. `Archive-date:` loses on both counts. Setup measured zero
  collisions anywhere (E6).
- **Q4 — the operator adopted BOTH legs, and it is the answer that changed
  the milestone's shape.** The witness makes drift *detectable* for documents
  that carry it; it can never reach the 46 documents already archived without
  one, nor any tree that upgrades from 1.x. So M28a also ships a narrow second
  leg — **D5**: `docs mv` refuses a move whose source and destination are
  **different dated directories under the archive subtree**, decided from the
  two paths alone, evaluated inside the plan-before-move,
  refuse-with-zero-mutation pre-flight M28 just built, at exit 2 with both
  dates named and zero bytes written. It invents no second refusal mechanism,
  adds no flag and adds no JSON key. Three neighbours are enumerated as
  **permitted** so the predicate cannot creep — a rename within one dated
  directory, a move `status-drift` already catches, and a move whose segments
  do not both parse. The argument against — that a cross-dated relocation is
  also how an operator corrects a mis-dated archive, and no other verb can do
  it — is answered by a **documented escape shipped in the same paragraph as
  the refusal** in both `cli.md` and `convention.md`: move by hand, correct the
  recorded date, re-check. The narrower alternative, refusing only when the
  moving document carries the witness, was rejected for making the refusal
  depend on the very field whose absence is the problem. Consequence: D8's
  residual narrows to a **hand-made** relocation of a **pre-2.0** document, and
  D9 gains M28a's single behaviour change.
- **Q2 (exact equality) and Q3 (backfill) are conductor-resolved as the stub
  recommended.** Equality is exact because no verb can legitimately produce a
  divergence — `docs archive` refuses an already-archived primary (E1a) and
  M26 — Q4 excludes already-archived candidates — so any divergence is drift
  by construction; the only refinement is that the comparison is on **parsed
  dates** in the tree's `date_format`, not on raw strings (E8). Backfill is
  refused because there is no code path that could perform it honestly:
  `docs archive` never re-reads an archived document, and inventing a date is
  the falsification the milestone exists to prevent. M27 — D6 is the
  precedent — the migration was performed once, by the milestone, and
  `convention.md` records that **no CLI verb performs it**.
- **`docs migrate` must not write the witness** (Q5), and E9 is why: its
  archive-directory date comes from each file's `Updated:` line or its mtime,
  and mtime on a fresh clone is today. A foreign document that already carries
  an `Archived:` line keeps today's behaviour — demoted to the
  `## Migrated metadata` body section as `Migrated-Archived:` — which is
  exactly right: a foreign tree's assertion is preserved but never promoted
  into a tool-trusted witness.
- **Three convention paragraphs must name the new field** (Q6). M18's
  move-driven exception as widened by M28 — D5, M25 — D4's audited
  relationship repair, and M27 — D6's one-time body-link migration each
  enumerate what may change in an archived document and each names
  `Archived-reason:` in its byte-identical list. All three must name the
  witness too, or the guarantee that survives a `relate` repair and a
  move-driven rewrite is a promise no document makes.
- **No new JSON key, no opt-out, no version bump.** The `Finding` record's
  key set is closed at four (E7) and M27 — D4 already froze the rule that a
  new rule adds a value to `rule` and never a field to the record; both dates
  travel in `message`. M27 — Q6 declined a `.docs.toml` opt-out for an
  objective rule and the same answer holds here. The package stays `1.8.0`
  and M29 performs the single bump (M25 — D6).
- Host-machine workflow skills are **not** updated by this milestone. Per
  `CLAUDE.md`, host skills refresh only at a production ship; the bundled
  skill inside `src/docs_cli/skill/` **is** updated in lockstep, in Phase 7.
- **No OPEN QUESTIONS remain.** All seven are resolved and recorded as binding
  in the milestone doc's *Setup questions (Q1–Q7)*, with the two findings that
  changed prior material restated in *Decisions recorded at setup (BINDING)* as
  A1 and A2. Phase 1 freezes both legs — the field, the corroboration rule and
  the `docs mv` refusal — against those answers rather than re-litigating
  scope.

### Setup questions — summary

Full reasoning in the milestone doc's *Setup questions (Q1–Q7)*.

| # | Question | Resolution |
|---|---|---|
| Q1 | What is the field called? *(stub Open question 1)* | **RESOLVED (auto, naming-with-an-obvious-default) → D1, BINDING.** The field is **`Archived:`** — beside `Archived-reason:`, parallel to `Updated:`, permanent and unrenameable once 2.0.0 ships. Rejected alternative recorded: `Archived-date:` (and `Archive-date:`), because `Updated:` already establishes that a date field here does not name its own type. Zero collisions measured (E6). |
| Q2 | Must the recorded value equal the directory date exactly? *(stub Open question 2)* | **RESOLVED (conductor) → D6, as recommended.** Exact equality, compared as **parsed dates** in the tree's `date_format` rather than as raw strings (E8). No verb can legitimately produce a divergence, so any divergence is drift. |
| Q3 | Does `docs archive` backfill the field? *(stub Open question 3)* | **RESOLVED (conductor) → D7, as recommended.** No. `docs archive` refuses an already-archived primary and excludes already-archived candidates, so no code path could backfill honestly; inventing a date is the falsification this milestone prevents (M27 — D6 precedent). |
| Q4 | Does `docs mv` also **refuse** the one silent relocation (E1d), or does M28a only detect it? | **RESOLVED (operator) → D5, BINDING. Both legs.** `docs mv` refuses when source and destination are both under the archive dir and their first segments parse to **different** dates — path arithmetic only, inside M28's existing plan-before-move pre-flight, exit 2, both dates named, zero bytes written, no flag and no JSON key. Three permitted neighbours are enumerated so the predicate cannot creep, and the by-hand escape ships in the same paragraph as the refusal in both specs. Rejected: witness-only (leaves the pre-2.0 population unprotected) and a refusal conditioned on the witness being present (depends on the very field whose absence is the problem). |
| Q5 | Does `docs migrate --apply` write the field for the archive-shaped files it relocates? | **RESOLVED (conductor) → D7 + *Out of scope*.** No. Its date comes from `Updated:` or **mtime**, which on a fresh clone is today (E9); writing it would stamp today as the archive date on every adopted historical document. A foreign `Archived:` line keeps today's demotion to `Migrated-Archived:`. |
| Q6 | Which archived-document immutability guarantees must name the field? | **RESOLVED (conductor) → D8.** All three: M18's move-driven exception as widened by M28 — D5, M25 — D4's audited repair, and M27 — D6's one-time migration. Each already names `Archived-reason:` in its byte-identical list; each must name the witness. |
| Q7 | Does the rule fire on a document carrying the field **outside** a dated archive directory? | **RESOLVED (conductor) → D6.** Yes — it is the same predicate. Corroboration means the first path segment under `<archive_dir>` parses to the recorded date; a document elsewhere in the tree, or under an undated archive subdirectory, has no corroborating location. `status-drift` and `archive-date-drift` are independent and may both fire; they report different facts. |

## Phase 1 — Define Contract

_Not started._

## Milestone completion summary

_Not complete._
