# M28a — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-08-16

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
- Progress: **M28a is IMPLEMENTATION-COMPLETE across all ten TDD phases.**
  Step 1 (Phases 1–4) on `m28a/phases-1-4` — contract 2026-08-15; RED tests,
  fixtures and the classified baseline 2026-08-16. Step 2 (Phases 5–10) on
  `m28a/phases-5-10`; Phases 5–8 complete 2026-08-16 with the suite
  fully **GREEN at 1502 passed / 0 failed**, every gate clean and 0 of the
  1341 pre-existing ids removed or failing, Phase 9 complete across ten
  dogfood flows, and **Phase 10 complete — M28a is implementation-complete
  across all ten TDD phases**. A same-instance audit fixed fifteen issues and
  a no-blocker fresh-eyes review (19/19 mutations killed, zero survivors)
  returned four should-fixes and six binding nits, all folded in. Final state
  **1504 passed / 0 failed** with every gate clean. It stays
  `Lifecycle: active` until the M29 publish closeout.** All seven setup
  questions were RESOLVED before Phase 1 (Q4 by the operator; Q1 auto-resolved
  under the naming-with-an-obvious-default rule; Q2/Q3/Q5/Q6/Q7
  conductor-resolved), and Phase 1 froze the contract against them without
  re-opening any — adding six amendments to setup-frozen material (the sixth
  at the fresh-eyes fold-in) and nine Step-1 resolutions (OQ-1 … OQ-9, OQ-7 an
  operator decision). Phases 2–4
  authored 149 test ids and six fixture trees against that contract and
  captured the classified baseline: 1502 collected, 71 RED and 90 GREEN of the
  161 new ids, exactly two exception classes, and no pre-existing id removed or
  failing. Setup
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
- Branch: `m28a/milestone-setup` for setup; `m28a/phases-1-4` for Step 1
  (Phases 1–4); `m28a/phases-5-10` for Step 2 (Phases 5–10).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-08-15 | Frozen in the milestone's *Decisions (Phase 1 — BINDING)*: items (A)–(H), six amendments to setup-frozen material (the sixth added at the fresh-eyes fold-in), and nine Step-1 resolutions (OQ-1 … OQ-9). Author-facing halves landed in `cli.md` and `convention.md`; both bundled mirrors re-synced. No product code. Suite still **1341 passed**. Original scope: freeze **both legs**. Leg 1: the field's name (`Archived:`), its `date_format` rendering, its position in the metadata block, and the every-member write rule; the vocabulary changes (`_BUILTIN_METADATA_FIELDS`, `parse()`'s `known` set, `[vocabulary] add_fields`); the `archive-date-drift` predicate as a corroboration test, its severity and exit, its position in `check_doc`'s append order, its independence from `status-drift`, and its frozen message forms. Leg 2: D5's `docs mv` refusal predicate, its frozen message beside `archive-date-drift`'s, its exit code, its position in M28's existing plan-before-move window (Phase-1 amendment 2 places it one step earlier, before the `--dry-run` branch), its four enumerated permitted neighbours (Phase-1 amendment 6) and its documented escape. Plus the present-only compatibility contract; `docs migrate`'s non-write; the three archived-immutability paragraphs that must name the field; and the Phase-5 signatures. |
| 2. Write Tests (RED) | Complete | 2026-08-16 | 131 authored ids across ten test files; 1472 collected, **68 RED / 63 GREEN** at baseline, 0 pre-existing ids failing. Two weak RED reasons (`TypeError`) rewritten into signature assertions, and one falsely-GREEN keyword-only test corrected. Original scope: **both legs.** Pure-rule unit tests over every corroboration shape; `docs archive` writer locks including a cascaded closeout where **every** member carries the field; D5's refusal proven with **and** without the witness present, with zero bytes written, plus the four permitted neighbours proven to complete; the present-only silence lock over all 46 field-less archived documents; `migrate` non-write and demotion locks; byte-identity locks for `touch` / `relate` / the M18-M28 widened exception; the closed four-key `Finding` record. |
| 3. Create Data/Fixtures | Complete | 2026-08-16 | Six committed `archivedate-*` trees, one semantic each, structure-only with fixed past dates. Suite: 1484 collected, **58 RED / 85 GREEN** of the 143 new ids; every pre-M28a fixture tree byte-identical (`git diff --numstat -- tests/fixtures/` empty; the six trees are additions only). Original scope: new `archivedate-*` trees, one semantic each — `-clean`, `-drifted`, `-absent`, `-outside`, `-undated`, and `-two-dated-dirs` for D5's refusal and its permitted same-directory rename — plus the hand-written registration tuple and the two whole-corpus sweep tests that a deliberately drifted tree would otherwise trip. |
| 4. Run Tests (RED Baseline) | Complete | 2026-08-16 | **1502 collected, 71 failed, 1431 passed** (after the Step-1 audit and the fresh-eyes fold-in; 1484 / 58 / 1426 as first measured). Exactly two exception classes (36 `AttributeError`, 35 `AssertionError`); 0 collection errors, 0 xfail/xpass/error, 0 warnings, 0 tracebacks. Mechanical proof against `7f7853b`: **0 ids removed**, **0 pre-existing ids failing**, 0 deleted test-source lines, `cli.py` untouched. Every RED failure traced to a family and a landing phase (43 → Phase 5, 26 → Phase 6, 2 → Phase 7); all 90 GREEN-at-baseline ids classified by name. |
| 5. Update Base Interfaces | Complete | 2026-08-16 | **28 failed / 1474 passed** — the 43 ids the Phase-4 classification assigned here, flipped. `Archived` into `_BUILTIN_METADATA_FIELDS` (and out of `parse()`'s `known` set and migrate's supersession set); `parse_date`'s keyword-only `label: str = "Updated"` (OQ-3, item (H)); and **all three** pure helpers — `archive_dir_date`, `cross_dated_archive_move` (Leg 2's predicate, delegating to it) and `archive_date_findings` — wired nowhere, so `check_doc`, `_archive_one` and `_cmd_mv` are untouched and every CLI-level id stays honestly RED at the seam. |
| 6. Implement Offline/Core Path | Complete | 2026-08-16 | **2 failed / 1500 passed** — the 26 ids the Phase-4 classification assigned here, flipped; only the two Phase-7 bundled-skill ids remain. One `set_metadata_field` call in `_archive_one` at the pinned position; one `findings.extend` in `check_doc` at the frozen position; and D5's refusal in `docs mv`'s plan-before-move window at the position Phase-1 amendment 2 froze — immediately after `old_rel` / `new_rel` are derived, before the `--dry-run` branch and before the first byte moves. Follow-through item 9's remaining three in-code prose surfaces landed here with the rule they describe. |
| 7. Update Tool/Wrapper Layer | Complete | 2026-08-16 | **1502 passed / 0 failed** — the suite is fully GREEN one phase early, as Phase 8 is the verification phase. Phase 1 had already landed the author-facing halves in `cli.md` / `convention.md`, so this phase **verified** them item by item and found two real gaps, both corrected: `convention.md`'s built-in always-allowed label list omitted `Archived`, and its `docs mv` refusal paragraph still said three permitted neighbours where amendment 6 says four. Bundled `SKILL.md` (three verb rows) and `references/use-cases.md` (three rows plus a new *Upgrade: the archive-date witness* section) landed; both mirrors re-copied in the same commit. Two argparse `description` strings gained one clause each (RESOLVED OQ-1) — the flag delta itself is **confirmed empty**, measured against `7f7853b`. `UNRELEASED` CHANGELOG gained both `Added` entries, the BREAKING `Changed` entry and the upgrade note including OQ-2's residual; `feedback-log.md` issue #1 is **CLOSED**. No new flag, no version bump. |
| 8. Run Tests (GREEN) | Complete | 2026-08-16 | **1502 passed / 0 failed**, 0 errors / xfails / warnings. `ruff check`, `ruff format --check` and `mypy src/ tests/` clean; `docs check --root docs` exit 0; both mirrors byte-identical. Mechanical proof against `7f7853b`: **0** of the 1341 pre-existing ids removed, 161 added, and **0 deleted lines in every test SOURCE file** — the only deletions anywhere under `tests/` are 8 lines in the frozen INDEX snapshot, every one an `Updated:` value or the generated-on line. **No test was relaxed, weakened, deleted or rewritten**, and Step 2 changed no test source at all. |
| 9. Integrate / Accept / Dogfood | Complete | 2026-08-16 | **Ten flows, all on throwaway copies.** E1d refuses at exit 2 with the copy byte-identical, on a document **without** the witness and on one **with** it, in every mode (`--dry-run` prints no `would move` line; `--json` prints 0 bytes). A hand-made relocation adds exactly **one** `archive-date-drift` where the pre-M28a CLI on the same tree adds none. All **four** permitted neighbours complete, the two-spellings-of-one-date case included. A non-default `attic` / `%d-%m-%Y` tree refuses on its configured dir and **completes** on an ordinary `archive/` subdirectory — both polarities of the config-blindness trap. All **46** pre-witness archived documents stay silent (0 findings total, exit 0). A real `--cascade-only 'm26-*'` closeout writes the witness to **every** member with one shared date, the reason to the primary alone, `docs check` clean. `migrate --apply` writes **no** witness and demotes a foreign one. The **7** cross-dated `pairs-with` edges emit nothing. Runtime delta below the 10 ms floor. One operator error during flow 8 wrote to the repository root and was fully reverted from HEAD with nothing lost; recorded in the entry rather than hidden. Original scope: Replay E1d and prove `docs mv` now **refuses** it with the tree byte-identical, on a document with **and** without the witness; reproduce the relocation by hand on a witness-carrying document and prove `docs check` exits 2 naming both dates; prove all four permitted neighbours still complete; prove all 46 field-less archived documents stay silent; run a real closeout and prove every member carries the field; prove `migrate --apply` writes none; measure the added `docs check` runtime. The real tree is never written to. |
| 10. Quality, Docs, Refactor | Complete | 2026-08-16 | `/simplify` took *Follow-ups* item 4 in full — **five** inline copies of the archive-subtree predicate (E7 counted three; reading for the collapse found two more, in `walk` and `_known_projects`) are now calls, and `_is_archived_rel` was hoisted beside `_root_relative`, which also removes Phase 5's forward reference. Behaviour-preserving: 1502 passed before and after, `docs check` runtime unchanged at 0.18 s over 73 documents. Four candidates evaluated and **rejected** with reasons. `architecture.md`'s `check`, `archive` **and `mv`** sections closed (RESOLVED OQ-4 places `mv` here); `test-strategy.md` gained the `archivedate-*/` family; completion summaries written. M28a stays `Lifecycle: active` for the M29 closeout. **After Phase 10** a same-instance audit fixed fifteen issues and a no-blocker fresh-eyes review (19/19 mutations killed) added four should-fix and six binding-nit fixes plus three new locks, ending at **1504 passed / 0 failed**. Original scope: `/simplify`, close `architecture.md` and `test-strategy.md`, completion summaries, hand to M29. |

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
  two paths alone, evaluated in the plan-before-move,
  refuse-with-zero-mutation window M28 just built — at the position Phase-1
  amendment 2 froze, before the `--dry-run` branch, so it refuses in every
  mode — at exit 2 with both dates named and zero bytes written. It invents no
  second refusal mechanism, adds no flag and adds no JSON key. **Four**
  neighbours are enumerated as **permitted** so the predicate cannot creep
  (Phase-1 amendment 6) — a rename within one dated directory, a move
  `status-drift` already catches, a move whose segments do not both parse, and
  two spellings of one date. The argument against — that a cross-dated relocation is
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
| Q2 | Must the recorded value equal the directory date exactly? *(stub Open question 2)* | **RESOLVED (conductor) → D3, as recommended.** Exact equality, compared as **parsed dates** in the tree's `date_format` rather than as raw strings (E8). No verb can legitimately produce a divergence, so any divergence is drift. |
| Q3 | Does `docs archive` backfill the field? *(stub Open question 3)* | **RESOLVED (conductor) → D6, as recommended.** No. `docs archive` refuses an already-archived primary and excludes already-archived candidates, so no code path could backfill honestly; inventing a date is the falsification this milestone prevents (M27 — D6 precedent). |
| Q4 | Does `docs mv` also **refuse** the one silent relocation (E1d), or does M28a only detect it? | **RESOLVED (operator) → D5, BINDING. Both legs.** `docs mv` refuses when source and destination are both under the archive dir and their first segments parse to **different** dates — path arithmetic only, in M28's plan-before-move window at the position Phase-1 amendment 2 froze (immediately after `old_rel` / `new_rel` are derived, **before** the `--dry-run` branch, so it refuses in every mode), exit 2, both dates named, zero bytes written, no flag and no JSON key. Four permitted neighbours are enumerated so the predicate cannot creep (Phase-1 amendment 6), and the by-hand escape ships in the same paragraph as the refusal in both specs. Rejected: witness-only (leaves the pre-2.0 population unprotected) and a refusal conditioned on the witness being present (depends on the very field whose absence is the problem). |
| Q5 | Does `docs migrate --apply` write the field for the archive-shaped files it relocates? | **RESOLVED (conductor) → D7 + *Out of scope*.** No. Its date comes from `Updated:` or **mtime**, which on a fresh clone is today (E9); writing it would stamp today as the archive date on every adopted historical document. A foreign `Archived:` line keeps today's demotion to `Migrated-Archived:`. |
| Q6 | Which archived-document immutability guarantees must name the field? | **RESOLVED (conductor) → D9.** All three: M18's move-driven exception as widened by M28 — D5, M25 — D4's audited repair, and M27 — D6's one-time migration. Two of the three already name `Archived-reason:` in the byte-identical list (M18's says "other metadata" generically — Phase-1 amendment 5); all three must name the witness. |
| Q7 | Does the rule fire on a document carrying the field **outside** a dated archive directory? | **RESOLVED (conductor) → D3.** Yes — it is the same predicate. Corroboration means the first path segment under `<archive_dir>` parses to the recorded date; a document elsewhere in the tree, or under an undated archive subdirectory, has no corroborating location. `status-drift` and `archive-date-drift` are independent and may both fire; they report different facts. |

## Phase 1 — Define Contract — 2026-08-15

### Objective

Freeze, against the resolved Q1–Q7, everything Phase 2 will assert against:
the field's name, value source, rendering, pinned block position and
every-member write rule; the three vocabulary changes and the one deliberately
*not* made; Leg 1's corroboration predicate as an exact evaluation order, both
non-corroborating shapes, parsed-date comparison, and which rule owns a
recorded value that does not parse; the rule's id, severity, exit code,
one-finding-per-document cardinality, its position in `check_doc`'s append
order and its independence from `status-drift`; the frozen message catalogue
for both legs; Leg 2's predicate, its position, its permitted neighbours and
its documented escape; the present-only contract; `docs migrate`'s non-write
and non-promotion; and the Phase-5 signatures. **No product code lands** —
signatures are frozen in prose, following the M25/M26/M27/M28 precedent,
because stubs would perturb the Phase-4 subprocess RED reasons.

### Actions taken

- Wrote the machine-facing contract as *Decisions (Phase 1 — BINDING)* in the
  milestone: **(A)** the field, **(B)** the vocabulary's three changes and one
  deliberate non-change, **(C)** Leg 1's two pure helpers with their BINDING
  evaluation order, **(D)** the rule's position, severity and cardinality,
  **(E)** the frozen message catalogue (three Leg-1 forms, two Leg-2 lines),
  **(F)** Leg 2's predicate, its position and its four permitted neighbours,
  **(G)** the author-facing surface and the authoring traps, **(H)** the
  Phase-5 signatures.
- Recorded **five amendments to setup-frozen material** in place — a sixth
  was added later, at the fresh-eyes fold-in. Amendments 1
  and 2 are Phase-1 decisions: **D8's residual is incomplete** (a *tool-driven*
  relocation out of a dated directory that is not cross-dated destroys the only
  archive-date record a pre-2.0 document has, and `status-drift` stays silent),
  and **D5's "inside the pre-flight" is refined** to the plan-before-move
  window one step earlier, so the refusal reaches `--dry-run`. Amendments 3, 4
  and 5 are corrections of statements of fact: "the product change is two
  lines" is three touch points; the log's Q→D summary table carried pre-D5
  numbers; and Q6's "each of the three paragraphs already names
  `Archived-reason:`" is true of two of them.
- Recorded **nine Step-1 resolutions (OQ-1 … OQ-9)** — one operator decision
  (**OQ-7**: do *not* widen Leg 2's predicate to refuse
  `docs mv archive/<date>/x.md archive/x.md`, because refusing it would also
  refuse a legitimate reorganisation of the archive subtree; name the residual,
  lock Leg 1's reach over it, and register it as a follow-up) and eight
  conductor decisions (the refusal's position; `bad-date` owns an unparseable
  witness; `parse_date` gains a keyword-only `label`; the rule uses the pure
  `_root_relative`; a `/`-bearing `date_format` is document-only; both the
  `Archived` and the missing `Archived-reason` rows land in *Optional fields*;
  the log's Q→D table is corrected in place; and the compatibility proof is
  phrased as a durable property rather than a fact a later archive would
  falsify).
- Landed the author-facing halves in `docs/cli.md`: the `docs archive` step
  list plus a witness paragraph pinning the block position and the every-member
  rule; a widened `bad-date` bullet and a new `archive-date-drift` bullet in the
  `docs check` rule list, with the `rule` table row, the exit-2 line and the
  built-in always-allowed field set; a new
  *Archive-date corroboration (M28a — D1 / D3)* subsection carrying the three
  conditions, both message forms verbatim, the `bad-date` form and its own
  *Upgrading from 1.x*; and a new
  *Cross-dated archived relocations (M28a — D5)* subsection under `docs mv`
  carrying both refusal lines, the exit code, the zero-bytes guarantee, the
  four permitted neighbours and the by-hand escape in the same place. The
  `docs mv` exit-code table and the global exit-code summary are amended.
- Landed the convention halves in `docs/convention.md`: an `Archived` row and
  the previously-missing `Archived-reason` row in *Optional fields*; the
  witness, the present-only rule, the never-requires-a-dated-directory rule and
  D5's refusal-with-escape under *Archive subtree*; the single-path-segment
  constraint on `[archive] dir` and `[archive] date_format` (OQ-5); and
  `Archived:` named on the byte-identical side of **all three**
  archived-immutability paragraphs plus M26's *Safe explicit archive selection*
  list.
- Registered two new *Follow-ups*: item 6 (a `/`-bearing `[archive]
  date_format`) and item 7 (D8's second residual).
- Mirrored both specs byte-identically into `src/docs_cli/skill/references/`
  and confirmed the frozen dogfood INDEX snapshot did not move (all four edited
  docs were already `Updated: 2026-08-15`, and today is 2026-08-15).

### Contract decisions worth calling out

- **Leg 2 refuses before the `--dry-run` branch, not inside the pre-flight.**
  D5's literal wording put it in `preflight_move_plan`, but `_cmd_mv` returns
  at its `--dry-run` branch *before* the pre-flight runs, so the literal
  reading would have left `docs mv --dry-run` printing `would move …` at exit 0
  for an operation the apply refuses. In the milestone whose whole point is
  that nothing silently falsifies the archive record, a preview that lies is
  not an acceptable residual. The refusal is decidable from the two arguments
  alone, which is exactly the class `docs archive --cascade-only`'s shape check
  already refuses in every mode.
- **`bad-date` owns an unparseable `Archived:` value, and `parse_date` gains a
  `label`.** D3 deferred the ownership question to Phase 1. Making it a
  `bad-date` keeps one rule id for "a date field that does not parse", parallel
  to `Updated:` — but `parse_date` hardcodes `Updated:` in its message, so a
  malformed witness would have named the wrong field. A keyword-only
  `label: str = "Updated"` keeps every existing call site byte-identical and
  leaves exactly one date-error message in the tool.
- **The residual is named rather than refused away.** Widening Leg 2 to catch
  `docs mv archive/<date>/x.md archive/x.md` was surfaced to the operator and
  declined: the same move is how an operator legitimately reorganises the
  archive subtree, which the convention permits. So D8 now states two
  residuals, a Phase-2 lock proves Leg 1 reaches the witness-carrying half, and
  *Follow-ups* item 7 carries the rest. A binding document must not claim
  closure it does not have.
- **The compatibility proof is a durable property, not a census.** "No archived
  document carries `Archived:`" would become false the first time a later
  milestone archives anything. The lock is instead "`check_tree(docs/)` yields
  zero `archive-date-drift` findings over a tree with at least 46 archived
  documents"; the exact 46-carry-no-field measurement stays in the Phase-9
  dogfood record as dated evidence.

### Verification

- `git diff --stat -- src/docs_cli/cli.py` — **empty**. No product code
  changed.
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 48 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues found in 49 source files.
- `.venv/bin/python -m pytest -q` — **1341 passed** (unchanged).
- `.venv/bin/docs check --root docs` — no violations found (exit 0).
- `cmp docs/cli.md src/docs_cli/skill/references/cli.md` and the same for
  `convention.md` — identical.
- `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.
- `grep -c '](\.\./' docs/cli.md docs/convention.md` — **0** in both.

## Phase 2 — Write Tests (RED) — 2026-08-16

### Objective

Express the whole Phase-1 contract as tests before any implementation: the
pure seam (`archive_dir_date`, `archive_date_findings`), every corroboration
shape and both non-corroborating ones, the rule's position and its
independence from `status-drift`, the writer's every-member rule and its
pinned block position, Leg 2's refusal and all four permitted neighbours, the
vocabulary integration, `docs migrate`'s non-write and non-promotion, every
byte-identity guarantee, and the two bundled-skill parity locks — including
every case that must stay GREEN at baseline.

### Actions taken

- `tests/test_check.py` (+87 ids — 41 authored plus the 46-way
  `_pre_m28a_tree_names()` parametrization): the two pure helpers behind an `_m28a(name)`
  indirection — the M28 `_m28(name)` precedent, so a missing symbol is one
  clean `AttributeError` rather than a collection error and `mypy` stays green;
  both purity locks (`Path.exists` / `is_file` / `is_dir` / `resolve` / `open`
  monkeypatched to raise); every message form asserted **verbatim**, including
  under a non-default `[archive] dir` so the message can never hardcode
  `archive/`; the `check_doc` position asserted as an exact rule **sequence**
  on a document that trips three rules at once; the `status-drift` independence
  in both directions; the E8 lock in both polarities on a `%d-%m-%Y` tree; the
  three `parse_date` label locks; the `unknown-field` sweep; the new
  `_pre_m28a_tree_names()` sweep; and the dogfood silence proof phrased as
  OQ-9's durable property.
- `tests/test_cli_check.py` (+8 ids): `_ARCHIVEDATE_TREES`, a **hand-written**
  registration tuple carrying each tree's COMPLETE expected finding set as
  committed — not "clean", because three of the six are deliberately drifted —
  plus one subprocess test per tree asserting the frozen message and the closed
  four-key `--json` record.
- `tests/test_cli_archive.py` (+10 ids): the witness matching its directory,
  `--date` proving one value drives both, the byte-level metadata block with
  and without `--reason`, the cascaded closeout over `archive-trio` where every
  member carries the date and only the primary carries the reason, the
  replace-in-place edge case, the `Related:`-group edge case, the `%d-%m-%Y` /
  `attic` rendering (with E8's pre-existing exit-2 tail asserted explicitly so
  the test cannot be satisfied by the defect being fixed), the unwidened
  `archive --json` key set, and the end-to-end "an archive leaves `docs check`
  clean".
- `tests/test_cli_mv.py` (+15 ids): the E1d reproduction with and without the
  witness, `--dry-run`, `--quiet`, precedence over the whole-tree walk, all four
  permitted neighbours, **both** halves of OQ-7's residual (Leg 1 reports the
  witness-carrying case; nothing reports the other, locked as the known gap),
  and the move-driven byte-identity of an archived referrer's witness. Every
  refusal test snapshots the whole tree and asserts zero bytes written.
- `tests/test_cli_migrate.py` (+2), `tests/test_cli_touch.py` (+1),
  `tests/test_cli_relate.py` (+1), `tests/test_config.py` (+3),
  `tests/test_model.py` (+2), `tests/test_skill.py` (+2).

### Decisions / issues

- **Two RED reasons were rewritten into assertions.** The `parse_date` label
  tests first failed with `TypeError: unexpected keyword argument 'label'`,
  which is a weaker reason than an assertion and hides which half is missing;
  they now assert on `inspect.signature` first. And the keyword-only test was
  **falsely GREEN**: calling with three positionals raises `TypeError` today
  for the opposite reason — there is no third parameter at all — so it now
  asserts the parameter's `kind` and default instead.
- **`_pre_m28a_tree_names()` is a sibling, never a widening.** Widening
  `_legacy_tree_names` or `_pre_m27_tree_names` would move pre-existing
  parametrized test ids, and extending either one's assertion would make M28a's
  three deliberately drifted fixtures fail it.
- **The registration tuple carries expected findings, not "clean".** Three of
  the six `archivedate-*` trees are deliberately drifted, so the M28 template's
  "every tree is clean as committed" gate does not transfer; the honest
  equivalent is each tree's complete `(path, rule)` list.
- **Neighbour 2 is locked in both polarities.** Moving the *witness-less*
  member out of the archive yields `status-drift` alone (E1b, no
  double-report); moving the *witness-carrying* member out yields
  `status-drift` **and** `archive-date-drift`, which is Q7's independence rule
  observed through a real move rather than a hand-built fixture.

### Verification

- `.venv/bin/python -m pytest tests/ -q --co` — **1472 collected**, 0
  collection errors (1341 pre-existing + 131 authored).
- `.venv/bin/python -m pytest tests/ -q` — **68 failed, 1404 passed**. Of the
  131 new ids, 68 are RED and 63 GREEN at baseline.
- Pre-existing ids failing: **0**, proven by `comm -12` of the failing-id list
  against the id list collected from a stashed working tree.
- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean.
- `git diff --stat -- src/docs_cli/cli.py` — **empty**.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).

## Phase 3 — Create Data/Fixtures — 2026-08-16

### Objective

Author the six committed trees Phase 2's locks point at — one semantic each,
structure-only, with fixed past dates rather than wall-clock-relative ones —
and update the whole-corpus sweeps in the same change, so a deliberately
drifted fixture cannot trip a sweep that promises silence.

### The six trees

| Tree | Contents | `docs check` as committed | After Phase 6 |
|---|---|---|---|
| `archivedate-clean` | `active.md`; `archive/2026-01-01/first.md` (witness + `pairs-with` the other dated directory); `archive/2026-03-04/second.md` (witness + the reciprocal bullet); `archive/2026-01-01/sub/nested.md` (deeper-path corroboration) | exit 0 | exit 0 — **the E5 decline, locked** |
| `archivedate-drifted` | `active.md`; `archive/2026-03-04/moved.md` carrying `Archived: 2026-01-01` | exit 0 | exit 2, one `archive-date-drift` (form A) |
| `archivedate-absent` | `active.md`; `archive/2026-01-01/old.md` with `Archived-reason:` and **no** witness | exit 0 | exit 0 — the whole compatibility story |
| `archivedate-outside` | `escaped.md` (`Lifecycle: active` + witness — Q7's motivating case); `stale-both.md` (`Lifecycle: archived` outside the archive + witness) | exit 2, one `status-drift` | exit 2; 2 × `archive-date-drift` + 1 × `status-drift` |
| `archivedate-undated` | `active.md`; `archive/misc/filed.md` (`Lifecycle: archived` + witness) | exit 0 | exit 2, one `archive-date-drift` (form B), **no** `status-drift` |
| `archivedate-two-dated-dirs` | `active.md`; `archive/2026-01-01/with-witness.md`; `archive/2026-01-01/no-witness.md`; `archive/2026-03-04/other.md`; `archive/notes/keep.md` | exit 0 | exit 0 — so every `docs mv` assertion measures the move |

Each carries a `.docs.toml` with `[project] name` and the explicit
`[archive] dir = "archive"` / `date_format = "%Y-%m-%d"` pair. No `Related:`
edge exists anywhere except the deliberate `-clean` cross-dated pair, which is
what E5's decline is about; `pairs-with` is free-form, so it produces no
`missing-inverse`. No fixture body carries a Markdown link, so the M27 sweep
stays silent, and no fixture filename carries a space or a parenthesis (M28's
sdist rule).

### Decisions / issues

- **Every non-default `date_format` / `[archive] dir` case stays an inline
  `tmp_path` builder** (the M25 rule): those assert on written bytes or need a
  non-default sidecar, so a committed tree would only add a `copytree` step.
  The same goes for the `2026-1-1` neighbour, the migrate demotion, and the
  `touch` / `relate` byte-identity locks.
- **`archivedate-two-dated-dirs` carries a witness-less member on purpose.**
  It is what makes Leg 2's independence from the field observable through a
  real `docs mv`, and it is the endpoint of D8's second residual.
- **Sweep bookkeeping, verified against the code rather than assumed.**
  `_legacy_tree_names()` excludes `reciprocal-*` and so picks up all six
  (**+6 ids**, GREEN — none uses a recognized reciprocal verb);
  `_pre_m27_tree_names()` excludes `bodylink-*` and picks up all six (**+6
  ids**, GREEN — no fixture body carries a link); `_pre_m28a_tree_names()`
  excludes `archivedate-*` and therefore does **not** grow.

### Verification

- `.venv/bin/python -m pytest tests/ -q --co` — **1484 collected**, 0
  collection errors (1341 pre-existing + 131 authored + 12 swept).
- `.venv/bin/python -m pytest tests/ -q` — **58 failed, 1426 passed**. Of the
  143 new ids, 58 RED and 85 GREEN at baseline.
- `git diff --numstat -- tests/fixtures/` — **empty**; the six trees are
  additions only, so every pre-M28a fixture tree is byte-identical.
- Each tree's finding set as committed, measured with `docs check`, matches the
  table above.
- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean.
- `git diff --stat -- src/docs_cli/cli.py` — **empty**.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).

## Phase 4 — Run Tests (RED Baseline) — 2026-08-16

### Objective

Prove the new tests fail for the intended missing behaviour and for nothing
else, and prove mechanically that no pre-existing test id moved.

### The baseline

```
.venv/bin/python -m pytest tests/ -q --co   ->  1502 collected, 0 collection errors
.venv/bin/python -m pytest tests/ -q        ->  71 failed, 1431 passed
```

Arithmetic, and it closes: **1341** pre-existing + **149** authored ids +
**12** swept ids (6 into `test_check_tree_legacy_fixtures_gain_no_new_findings`,
6 into `test_check_tree_pre_m27_fixtures_gain_no_body_link_findings`) =
**1502**. Of the 161 new ids, **71** are RED and **90** are GREEN at baseline.
No pre-existing id is RED.

*(Restated twice: after the Step-1 same-instance audit, which added five locks,
and after the fresh-eyes fold-in, which added thirteen more — see both sections
below. The figures Phase 4 first measured were 1484 / 58 / 85.)*

### Probes, stated honestly

- **Collection errors: 0.** `--co` collects 1502 and reports no errors.
- **xfail / xpass / errors: 0.** `pytest -rxXE --tb=no` emits no `XFAIL`,
  `XPASS` or `ERROR` line.
- **Warnings: 0.** No warnings summary is emitted.
- **Tracebacks: 0, and the probe was run correctly.** `grep -c Traceback` over
  the `--tb=line` output is **0** and `grep -c INTERNALERROR` is **0**. M28 hit
  a false positive here for real — several tests assert `"Traceback" not in
  proc.stderr` in their own source, and a `--tb=long` run prints that source as
  context — so the count is taken over `--tb=line`, which prints no source.

### Exception-class census (`--tb=line`)

Exactly **two** classes, and the arithmetic closes:

| Class | Count | Where | Why |
|---|---|---|---|
| `AttributeError` | 36 | the **three** pure-seam groups in `tests/test_check.py` — `archive_dir_date`, `archive_date_findings` and `cross_dated_archive_move` | every M28a symbol is fetched through `_m28a(name)`, so the RED reason is one clean missing attribute rather than a collection error |
| `AssertionError` | 35 | 8 `check_doc` / vocabulary / `parse_date` in `test_check.py`, 8 `docs archive`, 9 `docs mv`, 5 `docs check`, 3 `test_config.py`, 2 bundled-skill locks | the behaviour is absent, not the symbol |

Three failures first rendered as bare `assert` lines with no class name, and
two others were `TypeError`. Both were fixed rather than accepted: the
`TypeError`s came from calling `parse_date(..., label=…)` before the parameter
exists — a weaker reason that also hides which half is missing — and now assert
on `inspect.signature` first; the bare asserts gained messages. The census is
two classes by construction, not by luck.

### Mechanical no-regression proof

Test ids were collected from a throwaway `git worktree` at the pre-Phase-1
commit `7f7853b` and from HEAD, and compared with `comm`:

| Measure | Result |
|---|---|
| ids at `7f7853b` | **1341** |
| ids at HEAD | **1502** |
| `comm -23 old new` — **removed** ids | **0** |
| `comm -13 old new` — added ids | **161** (110 `test_check.py` — 52 authored + 46 the new sweep + 12 swept into the two pre-existing ones; 19 `test_cli_mv.py`, 11 `test_cli_archive.py`, 8 `test_cli_check.py`, 3 `test_config.py`, 2 each `test_cli_migrate.py` / `test_model.py` / `test_skill.py`, 1 each `test_cli_new.py` / `test_cli_relate.py` / `test_cli_stamp.py` / `test_cli_touch.py`) |
| pre-existing ids now FAILING | **0** (`comm -12` of the failing-id list against the `7f7853b` id list) |
| `git diff --numstat 7f7853b -- tests/` | **0 deleted lines in every test source file.** The only deletions anywhere under `tests/` are **5 lines in `tests/fixtures/expected/docs-INDEX.md`** — the frozen dogfood snapshot re-synced when `docs touch` moved four `Updated:` values (`status.md`, `plan.md`, and the two M28a docs) from 2026-08-15 to 2026-08-16 across the phase commits, plus the generated-on line. No test source line and no pre-existing fixture-tree byte was removed. |
| `git diff --stat 7f7853b -- src/docs_cli/cli.py` | **empty** |

`tests/test_edit.py`, `tests/test_relate_plan.py`, `tests/test_archive_plan.py`
and `tests/test_move_links.py` are untouched: M25's frozen plan contract and
M28's move-rewrite seam are not reached into.

### RED classification — every failure traced to a family and a landing point

| # | Family | Landing |
|---|---|---|
| 26 | **Leg 1's pure seam** (`tests/test_check.py`): `archive_dir_date` over every path shape, both non-default config axes, the unpadded spelling and its purity lock; `archive_date_findings` over absence / blank / bare-label / corroboration / both drift forms / the `bad-date` form / parsed-not-string equality / the raw-strings-from-disk message / the closed four-key record / its own purity lock | **Phase 5** — `archive_dir_date`, `archive_date_findings` |
| 10 | **Leg 2's pure seam** (`tests/test_check.py`, added at the fresh-eyes fold-in): `cross_dated_archive_move` over the raw-segment return value, all four permitted neighbours, **both** non-default config axes in **both** polarities, an exhaustive agreement check against `archive_dir_date`, and its own purity lock | **Phase 5** — `cross_dated_archive_move`, which item (H) freezes as a Phase-5 signature |
| 7 | **The vocabulary and the parser** (`test_check.py` ×4, `test_config.py` ×3): `Archived` must never trip `unknown-field` and must be built-in rather than config-sourced (2 + 3); `parse_date` must gain its keyword-only `label` with an unchanged default and the right `kind` (2) | **Phase 5** — `_BUILTIN_METADATA_FIELDS`, `parse_date` |
| 4 | **`check_doc` wiring** (`test_check.py`): the finding's exact position in the returned rule sequence, the `status-drift` independence in both directions, and the two-`bad-date` order | **Phase 6** — one `findings.extend` at the frozen position |
| 5 | **The rule at the CLI** (`test_cli_check.py`): the registration tuple's complete per-tree finding sets, `-drifted`'s frozen form-A line and its closed `--json` record, `-outside`'s three findings, `-undated`'s form-B line with no `status-drift` | **Phase 6** |
| 8 | **The writer** (`test_cli_archive.py`): the witness matching its directory, `--date` driving both from one value, the byte-level block order with and without `--reason`, the cascaded every-member rule, the replace-in-place and `Related:`-group edge cases, and the tree's own `date_format` rendering | **Phase 6** — one `set_metadata_field` in `_archive_one` |
| 9 | **Leg 2 at the CLI** (`test_cli_mv.py`): the refusal with and without the witness, under `--dry-run` and `--quiet`, its raw-segment message, its precedence over the whole-tree walk, **one refusal on a tree with a non-default `[archive] dir` and `date_format`**, and the two locks that need Leg 1 to exist as well | **Phase 6** — one refusal in `_cmd_mv` |
| 2 | **Bundled skill parity** (`test_skill.py`): `SKILL.md`'s `docs archive` / `docs mv` rows and `references/use-cases.md` | **Phase 7** — the bundled skill lands in the same change as the CLI surface |

The arithmetic closes: 26 + 10 + 7 = **43 land at Phase 5**, 4 + 5 + 8 + 9 =
**26 at Phase 6**, **2 at Phase 7** — 71 in total.

**A classification call, recorded rather than left implicit.** The fresh-eyes
review suggested filing the `cross_dated_archive_move` unit group under
Phase 6, as Leg-2 work. It is recorded under **Phase 5** instead, because item
(H) freezes that signature as a Phase-5 one alongside the other three and
Phase 5's exit criterion is *"interfaces typecheck and are unit-tested"* — a
pure helper with no unit group would leave that criterion uncheckable. The
milestone's Phase-5 objective, which named only Leg 1's two helpers, is
corrected in the same change so the two never disagree. Nothing about the tests
changes either way: the group flips no later than Phase 6, and Leg 2's nine
CLI-level ids stay at Phase 6 where the refusal is wired.

### GREEN at baseline — every lock classified

The 90 new GREEN ids:

| Lock | Count | Classification |
|---|---|---|
| `test_check_tree_pre_m28a_fixtures_gain_no_archive_date_findings[*]` | 46 | **degenerate** now (the rule does not exist); a genuine whole-corpus regression lock after Phase 6, including for trees added by later milestones |
| `test_check_tree_legacy_fixtures_gain_no_new_findings[archivedate-*]` | 6 | **degenerate** (none of the six uses a recognized reciprocal verb); genuine afterwards |
| `test_check_tree_pre_m27_fixtures_gain_no_body_link_findings[archivedate-*]` | 6 | **degenerate** (no fixture body carries a Markdown link); genuine afterwards |
| `test_check_doc_is_silent_on_a_corroborated_witness`, `..._with_no_witness`, `test_check_doc_malformed_document_never_reaches_the_rule`, `test_check_doc_duplicate_archived_label_still_fires_duplicate_field` | 4 | **degenerate** now; each becomes a genuine over-fire guard at Phase 6 — the last one in particular catches an implementation that read the FIRST duplicate label |
| `test_check_doc_archived_field_never_flagged_by_unknown_field[no-add-fields]` | 1 | **degenerate** by construction: `unknown-field` is gated on `if config.fields:`, so with no allowlist it can never fire. Kept as the third leg of E6's three-way lock; its two siblings are RED |
| `test_exit_code_for_archive_date_drift_is_2` | 1 | **degenerate** by construction *as it stood at Phase 4* — it hand-built a `Finding(..., "error", ...)`, and `exit_code_for` keys on `severity`, never on `rule`, so it tested `exit_code_for` rather than M28a. **Rewritten at the Step-2 fresh-eyes fold-in** (T5) to wire the real producer to the real consumer: it now takes all three findings from `archive_date_findings` itself and asserts each carries `severity: error` and drives exit 2. It is therefore no longer GREEN-at-baseline — at `7f7853b` it would have raised the same `AttributeError` as the rest of the pure-seam group, moving one id from this census to the RED classification's Phase-5 row. The Phase-4 counts above (71 RED / 90 GREEN, 43/26/2) are the measurement taken **at that commit** and stay true of it |
| `test_check_tree_dogfood_repo_docs_gains_no_archive_date_drift` | 1 | **degenerate** now; the milestone's headline compatibility claim after Phase 6, and phrased as OQ-9's durable property so a later milestone's archive event cannot falsify it |
| `test_parse_date_defaults_to_the_updated_label` | 1 | **genuine**: it is what proves Phase 5's signature change moved no byte of any existing message |
| `test_check_archivedate_clean_tree_exits_0`, `..._absent_tree_exits_0`, `..._two_dated_dirs_tree_is_clean_as_committed` | 3 | **genuine at Phase 3** for the fixture-shape half they assert (the cross-dated `pairs-with` pair, the witness-less archived document, the witness-carrying and witness-less members); **degenerate** for the exit-0 half until Phase 6, when they become the over-fire guards |
| `test_archive_leaves_the_tree_check_clean` | 1 | **degenerate** now (neither the writer nor the rule exists); the strongest single end-to-end assertion in the milestone after Phase 6 |
| `test_archive_json_top_level_key_set_does_not_widen` | 1 | **genuine**: a pure regression lock that stops a Phase-6/7 implementer adding a key beside `date` |
| the seven `docs mv` permitted-neighbour locks — two for neighbour 1, two for neighbour 2, two for neighbour 3 and one for neighbour 4 | 7 | **genuine today**, and the locks that keep the Phase-6 predicate from creeping. `neighbour_4` is the one a raw-string comparison would fail; `neighbour_3_to_the_archive_root_is_silent_without_a_witness` is D8's second residual pinned as the KNOWN GAP |
| `test_migrate_apply_writes_no_archive_date_witness`, `..._demotes_a_foreign_archived_line_without_promoting_it` | 2 | **genuine** — D7 is satisfied by construction, so these are pure regression locks; the second is what stops `Archived` being added to migrate's supersession set in the same change that adds it to the built-in set |
| `test_touch_on_an_archived_document_leaves_the_witness_byte_identical`, `test_relate_archived_repair_leaves_the_witness_byte_identical`, `test_mv_of_an_archived_document_leaves_its_witness_byte_identical` | 3 | **degenerate only in that the witness they preserve is hand-authored** — no verb writes one until Phase 6. The behaviour each pins (exactly one label rewritten; exactly three things changed by an audited repair; exactly the moving destination changed) is genuine today |
| `test_parse_harvests_archived_into_extra`, `test_doc_to_json_surfaces_archived_under_extra_fields` | 2 | **genuine**: item (B)'s deliberate non-change. A Phase-5 implementer adding the label to `parse()`'s `known` set would drop it from `docs list --json`'s `extra_fields` |
| `test_new_never_writes_the_archive_date_witness`, `test_stamp_never_writes_the_archive_date_witness` | 2 | **genuine** (added at the Step-1 audit): `cli.md` claims five verbs never write the witness, and these are the two nothing else covered |
| `test_archive_leaves_an_archived_referrers_witness_byte_identical` | 1 | **degenerate only in that the witness is hand-authored** (added at the Step-1 audit); it is the `docs archive` half of M18's widened move-driven exception, whose `docs mv` half already had a lock |
| `test_mv_does_not_refuse_inside_an_ordinary_archive_named_subdirectory` | 1 | **genuine today** (added at the fresh-eyes fold-in), and the more dangerous half of the config-blindness trap: on a tree configured `dir = "attic"` a config-blind predicate would FALSELY refuse an everyday reorganisation under an ordinary `archive/` subdirectory |
| `test_mv_collision_still_exits_1_before_the_cross_dated_refusal` | 1 | **genuine today** (added at the fresh-eyes fold-in): it freezes the precedence between the two exit-1 argument errors and the exit-2 refusal, so Phase 6 cannot hoist the predicate above the `is_file` / `exists` guards |

The arithmetic closes: 46 + 6 + 6 + 4 + 1 + 1 + 1 + 1 + 3 + 1 + 1 + 7 + 2 + 3 +
2 + 2 + 1 + 1 + 1 = **90**.
| `test_check_every_archivedate_fixture_tree_matches_its_registration` | — | **RED**, listed here only to record that it is deliberately not on this table: three of the six trees are drifted, so it cannot go GREEN until Phase 6 |

Pre-existing locks whose expected state is worth naming, all verified GREEN at
this gate:

| Lock | Classification |
|---|---|
| every `movelink-*` / `bodylink-*` / `reciprocal-*` lock, `test_edit.py`, `test_relate_plan.py`, `test_archive_plan.py`, `test_move_links.py` | GREEN throughout. M18, M25, M26, M27 and M28 behaviour is byte-stable; M28a reaches into none of it |
| `test_cli_check.py::test_check_dogfood_repo_docs_is_clean` | **Genuine**, GREEN throughout. If it goes RED, a Phase-1 spec example became a real broken link |
| `test_cli_index.py::test_index_output_matches_frozen_snapshot` | **Genuine**. Re-synced in the Phase-2 commit, when `docs touch` moved four `Updated:` values across the day boundary |
| `test_skill_refs.py::test_bundled_ref_matches_source[cli.md]` / `[convention.md]`, `test_bundled_skill_has_no_repo_relative_links` | **Genuine**. Phase 1 kept both mirrors byte-identical and both specs at zero repo-relative link prefixes |
| `test_a3_project_version_is_1_8_0`, `test_c2_docs_version_is_1_8_0` | **Genuine**. No version bump; M29 owns it (M25 — D6) |

### Falsely-GREEN check at this gate

Done mechanically over every M28a test, test by test:

- **Every intended-exit-2 test asserts a frozen contract string** as well as the
  code, so an unrelated failure with the same code cannot later satisfy it.
  Three assertions that rendered without a class name gained messages in this
  phase for the same reason.
- **Every fixture-backed test asserts its tree directory exists**, through
  `_archivedate_tree`, so the family was honestly RED before Phase 3 rather
  than green on an empty copy.
- **Every intended-exit-0 test asserts structure or the absence of a NAMED
  finding**, never bare silence. Three `docs mv` neighbour tests were
  strengthened at this gate: they asserted exit 0 and a clean `docs check`
  without asserting that the destination file existed, which a `mv` that
  silently no-opped would have satisfied. They now assert the destination, and
  the residual-gap lock additionally asserts that the moved document carries no
  witness — which is the whole reason nothing reports the loss.
- **The three "clean as committed" fixture tests assert fixture SHAPE first** —
  the cross-dated `pairs-with` pair, the `Archived-reason:`-without-witness
  document, the witness-carrying and witness-less members — so they measure the
  fixture rather than the absence of a rule.

### Phase-5/6/7 follow-through, carried from Phase 1

1. `parse_date` gains a keyword-only `label: str = "Updated"`; every existing
   call site stays byte-identical (Phase 5, OQ-3).
2. `Archived` joins `_BUILTIN_METADATA_FIELDS` and stays out of `parse()`'s
   `known` set and out of `_REQUIRED_METADATA_FIELDS` (Phase 5, item (B)).
3. `archive_dir_date` and `archive_date_findings` land pure, wired nowhere, so
   the CLI tests stay honestly RED at the seam (Phase 5).
4. One `set_metadata_field` in `_archive_one` at the pinned position; one
   `findings.extend` in `check_doc` at the frozen position; one refusal in
   `_cmd_mv` before the `--dry-run` branch (Phase 6).
5. Bundled `SKILL.md` and `references/use-cases.md`, with `references/cli.md` /
   `references/convention.md` kept byte-identical (Phase 7).
6. `CHANGELOG.md` under the existing `UNRELEASED` heading, with the upgrade note
   naming the one behaviour change **and** OQ-2's residual: a hand-adopted
   foreign tree carrying a non-date `Archived:` value gains a new `bad-date`
   error (Phase 7).
7. A dated note on `feedback-log.md`'s issue #1 entry closing finding 3's
   archive-date half (Phase 7).
8. `test-strategy.md`'s fixture-source list gains the `archivedate-*` family,
   and `architecture.md`'s `check` and `archive` sections are closed
   (Phase 10).
9. **Three in-code prose surfaces no test can police**, enumerated here because
   the milestone's own wide-blast-radius risk says the freeze must name every
   surface before any code (Phases 5–6):
   - the comment block above `_BUILTIN_METADATA_FIELDS` (`cli.py:160–168`),
     which explains why each label is built-in and currently stops at M25's
     `Revision:`;
   - `check_doc`'s docstring rule list (`cli.py:3354–3377`), which enumerates
     every rule `docs check` runs and must gain `archive-date-drift` beside the
     M27 body-link entries, and whose `bad-date` line must widen to name both
     date fields;
   - `check_doc`'s `unknown-field` comment (`cli.py:3558–3560`) and `Finding`'s
     own docstring rule enumeration (`cli.py:415–419`), which lists the stable
     rule ids the `--json` record can carry.

### Verification

- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).
- `git diff --stat 7f7853b -- src/docs_cli/cli.py` — **empty**. Phases 1–4
  change no product code, by design.

## Step-1 same-instance audit — 2026-08-16

Run against Phases 1–4 after the last phase and before returning, per the
ship-milestone consistency / completeness / accuracy checklist. Eight issues
found; all eight fixed here. Nothing found changes milestone scope or
behaviour intent, so nothing is escalated as a decision; three observations are
recorded at the end for the operator's awareness.

### Issues found and fixed

1. **The Phase-4 RED classification's arithmetic did not close.** The
   vocabulary/parser row counted 5 where 7 land at Phase 5 — it omitted the two
   `parse_date` label ids — so the table summed to 56 against a measured 58.
   Corrected in place, and an explicit arithmetic-closes line added beneath the
   table so the next reader does not have to re-add it.
2. **The snapshot-deletion count was wrong.** The mechanical proof said 4
   deleted lines in `tests/fixtures/expected/docs-INDEX.md`; it is **5** — four
   `Updated:` values (`status.md`, `plan.md`, and both M28a docs) plus the
   generated-on line. Corrected, and the sentence now names which values moved.
3. **`cli.md` claims five verbs never write the witness; only three were
   locked.** `docs touch`, `docs relate` and `docs migrate` had locks;
   `docs new` and `docs stamp` had none, so two fifths of a shipped promise was
   untested. Added `test_new_never_writes_the_archive_date_witness` and
   `test_stamp_never_writes_the_archive_date_witness` (the second also
   re-stamps, because a re-stamp is the path that touches an existing block).
4. **The M18/M28-widened move exception was only half locked.** The milestone
   deliverable names byte-identity locks for "the M18–M28 widened move
   exception", and only the `docs mv` half existed. M18's exception is
   originally the ARCHIVE-driven one, so
   `test_archive_leaves_an_archived_referrers_witness_byte_identical` was added:
   an already-archived, witness-carrying referrer whose `Related:` bullet **and**
   whose body-link destination are repointed by an archive, with everything else
   — the witness, the reason, `Updated:`, the H1, the prose — asserted
   byte-identical and no `Revision:` bullet added.
5. **Both message catalogues under-constrained the raw-string requirement.**
   Item (E) says `<recorded>`, `<segment>`, `<D1>` and `<D2>` are the RAW
   strings as written on disk — but every existing assertion used zero-padded
   spellings, which survive a round trip through `strftime`. An implementation
   that re-rendered the parsed dates through `config.date_format` would have
   passed every one of them and then named directories the tree does not have.
   Added `test_archive_date_findings_message_prints_the_raw_strings_from_disk`
   (`archive/2026-1-1/` with `Archived: 2026-3-4`) and
   `test_mv_refusal_names_the_raw_directory_segments` (an inline tree whose
   source directory is `archive/2026-1-1/`). Both RED, at Phases 5 and 6.
6. **Q6 / D9's factual claim was false for one of the three paragraphs.**
   "Each already names `Archived-reason:` in its byte-identical list" is true of
   M25 — D4's and M27 — D6's; M18's says "other metadata" generically. Recorded
   as Phase-1 amendment 5 and corrected in `convention.md`, the milestone doc
   and this log, so the guarantee now reads alike in all three.
7. **This log's *Setup questions — summary* table carried pre-D5 decision
   numbers.** Q2→D6, Q3→D7, Q6→D8, Q7→D6 against the milestone's Q2→D3,
   Q3→D6, Q5→D7, Q6→D9, Q7→D3. Renumbered in place (Phase-1 amendment 4, OQ-8).
8. **"Inside the pre-flight" survived amendment 2 in several places.** The
   milestone doc's D5, its Phase-1 and Phase-6 objectives, its Leg-2
   deliverable, its E1 coverage row and Q4's *adopted scope*, plus this log's
   phase table and `status.md` / `plan.md`, all still described the refusal as
   sitting inside `preflight_move_plan`. Reconciled everywhere to the
   plan-before-move window at the position amendment 2 froze, with the
   amendment named at each site.

### Checked clean

- Every Phase-1–4 deliverable and success criterion in range is met against the
  milestone doc, read rather than recalled: the frozen contract covers the
  field, the vocabulary, both predicates, the rule's position / severity /
  cardinality, both message catalogues, Leg 2's position and neighbours, the
  present-only contract and the Phase-5 signatures; the six fixture trees exist
  with the registration tuple and all three sweeps.
- No placeholder, `NotImplementedError`, TODO or commented-out code anywhere in
  the diff. (The `TODO` hits under `tests/` are pre-existing assertions that a
  TODO must **not** appear in the bundled skill.)
- `git diff --stat 7f7853b -- src/docs_cli/cli.py` is empty: Phases 1–4 change
  no product code, by design.
- `cmp docs/cli.md src/docs_cli/skill/references/cli.md` and the same for
  `convention.md` — identical, re-copied in the same commit that edited the
  source. Both specs carry zero repo-relative `](../` links.
- `docs/INDEX.md` and `tests/fixtures/expected/docs-INDEX.md` are byte-identical
  and were re-synced in the phase commit whose `docs touch` moved a date.
- `docs check --root docs` exits 0; every `Related:` edge in the edited docs
  resolves; every edited doc's `Updated:` was bumped by `docs touch`.
- `status.md`, `plan.md`, the milestone doc and this log agree on the phase
  state, the branch, the dates and the counts.
- The diff contains only M28a's work: twelve test files, two spec files, their
  two mirrors, six fixture trees, four tracker docs and the two INDEX
  artifacts. (Restated after the fresh-eyes fold-in, which touched three of the
  same test files and one spec plus its mirror, and added no new file.)

### Adversarial pass — do the tests actually pin the contract?

Walked as "what wrong implementation would still pass?", which is what produced
issues 3, 4 and 5 above. The cases that were already covered, recorded so a
later reader does not have to re-derive them:

- A helper reading `parts[-2]` instead of `parts[1]` fails
  `..._reads_the_first_segment_of_a_deeper_path`, which uses a two-level
  subdirectory precisely so `[-2]` and `[1]` differ.
- A helper copying `detect_archive_layout`'s hardcoded `"archive"` /
  `"%Y-%m-%d"` fails the two non-default-config locks.
- A rule using `path.resolve().relative_to(root.resolve())` fails the purity
  lock, which monkeypatches `Path.resolve` alongside `exists` / `is_file` /
  `is_dir` / `open`.
- A `findings.extend` at the wrong position fails the exact-rule-sequence lock,
  which uses a document tripping `status-drift`, the new rule and
  `duplicate-field` at once, so both the too-early and the too-late placement
  produce a different sequence.
- A Leg-2 refusal placed inside `preflight_move_plan` fails the `--dry-run`
  lock; one placed after the whole-tree walk fails the precedence lock, which
  plants a malformed sibling and asserts it is **not** the document reported.
- A Leg-2 predicate comparing raw segments fails the neighbour-4 lock
  (`2026-01-01` to `2026-1-1` must complete).
- A rule reading the FIRST of two duplicate `Archived:` labels fails the
  `duplicate-field` co-existence lock.
- `Archived` added to `parse()`'s `known` set fails the two `test_model.py`
  locks; added to migrate's `_REQUIRED_METADATA_FIELDS` fails the demotion
  lock; satisfied through `[vocabulary] add_fields` instead of the built-in set
  fails the three `test_config.py` locks.

One residual is recorded rather than closed: neighbour 3 is proven in both
directions for the undated-subdirectory endpoint, but only in the outbound
direction for the archive-root endpoint. The predicate is symmetric by
construction — it requires **both** segments to parse — so the inbound case
cannot behave differently without also breaking the outbound lock.

### Observations for the operator (no decision required)

1. **The shipped specs describe behaviour that lands in Phases 5–7.** `cli.md`
   and `convention.md` ship byte-identically inside the wheel, so between now
   and Phase 7 the packaged skill documents a rule the code does not yet
   enforce. This is the M25/M26/M27/M28 Phase-1 precedent, not a deviation, and
   Step 2 closes it.
2. **`cli.md`'s `bad-date` bullet was corrected in passing.** It said
   "`Updated:` not parseable as `YYYY-MM-DD`"; `check_doc` has honoured
   `config.date_format` since M2. OQ-2 required the bullet to widen anyway, and
   it now states the accurate rule for both fields.
3. **One test deliberately pins a KNOWN GAP.**
   `test_mv_neighbour_3_to_the_archive_root_is_silent_without_a_witness` asserts
   that nothing reports D8's second residual (*Follow-ups* item 7). If a later
   milestone closes that gap, this is the test that must be revisited
   deliberately rather than "fixed".

## Step-1 fresh-eyes review fold-in — 2026-08-16

An independent fresh-eyes pass over Phases 1–4 returned **no blockers**: the
frozen contract is implementable verbatim, every message string is
byte-identical across `cli.md`, `convention.md`, the milestone doc and the
tests, `cli.py` is untouched, the surface-parity gate holds, and the RED
baseline reproduces. It attacked the suite with roughly fifteen candidate wrong
implementations and the suite caught all but one. Three should-fixes and eight
nits were returned; every one is folded in below, with the conductor's binding
calls applied.

### The one wrong implementation the suite did not catch

**Leg 2's predicate had no tests of its own, and every Leg-2 CLI test ran on a
default-config tree.** `cross_dated_archive_move` appeared nowhere under
`tests/`, unlike the other three frozen item-(H) signatures. So a Phase-6
implementation that inlined `rel.startswith("archive/")` and
`strptime(seg, "%Y-%m-%d")` — `detect_archive_layout`'s config-blind idiom, the
exact mistake E7 warns against — would have passed **100%** of the suite while:

- never refusing on a tree configured `dir = "attic"`, leaving open the very
  hole M28a exists to close; and
- **falsely refusing** a legitimate reorganisation on a tree configured
  `dir = "history"`, where `archive/` is an ordinary subdirectory — the trap
  `_is_archived_rel`'s own docstring names.

It would also have silently defeated item (C)'s stated guarantee that the two
legs can never disagree about what a dated archive directory is.

Closed with **thirteen** ids. Ten unit ids in `tests/test_check.py`, beside the
`archive_dir_date` group: the raw-segment return value, all four permitted
neighbours, both non-default config axes in **both** polarities (the `attic`
tree must refuse for `attic/` **and** must not refuse for `archive/`), an
exhaustive agreement check running `cross_dated_archive_move` against
`archive_dir_date` over a 7 × 7 matrix of path shapes on a doubly non-default
config, and a purity lock. Three ids in `tests/test_cli_mv.py`: a cross-dated
refusal on an inline `dir = "attic"` / `date_format = "%d-%m-%Y"` tree with the
frozen message naming the configured directory and the raw segments; the
ordinary-`archive/`-subdirectory move proven to **complete** on that same tree;
and the exit-1 precedence lock below. Ten are RED at Phase 5, one at Phase 6,
two GREEN today.

### The other findings

| # | Finding | Resolution |
|---|---|---|
| should-fix 2 | Two sites still described Leg 2's refusal as living "inside the pre-flight" — `status.md` and this log's Q4 summary row — while `status.md` stated the corrected position twice elsewhere, contradicting itself. The Step-1 audit's issue 8 claimed these were reconciled; they were not. | Both reconciled to the amendment-2 wording, along with a third site in this log's setup record. |
| should-fix 3 | `status.md` said "authored **131** test ids … of the **148** new ids"; 131 + 12 swept is 143, and the post-audit figure was 136. | Corrected to 136, and then to 149 with this fold-in. |
| nit 4 (binding) | Item (F) enumerates **four** permitted neighbours and the tests lock four, but eight derived surfaces still said three — including the **Phase-9 dogfood instruction**, which would have under-covered the one neighbour a raw-string comparison fails. | Recorded as **Phase-1 amendment 6** and swept across the milestone doc (deliverable, Phase-2 files, Phase-6 exit, Phase-9 dogfood, success criterion, Q4, A1), this log and `status.md` / `plan.md`. Phase 9 now also names a non-default-config refusal. |
| nit 5 (binding) | Two sites still said D8's residual narrows to a hand-made relocation of a pre-2.0 document (singular) while amendment 1, D8 itself and the tests say two — inconsistent within one section. | Both reconciled to the two named cases. |
| nit 6 | `status.md`'s M28-narrative paragraph still said "M28a … its Phase 1 completed the same day", contradicting the same file's header. | Reconciled to Step 1 (Phases 1–4). |
| nit 7 | This log's Phase-2 per-file breakdown summed to 107, not the 131 claimed. | The `test_check.py` line now reads **+87** (41 authored plus the 46-way sweep parametrization), and the breakdown sums to 131. |
| nit 8 (binding) | `test_archive_renders_the_witness_in_the_trees_date_format` pins defect E8's failure mode as required behaviour, so **fixing** *Follow-ups* item 1 will break it — the inverse of what its docstring claimed. | The strict assertion is **kept**, per the binding call: it is what stops the witness half being satisfied by E8 being fixed elsewhere. Instead the coupling is registered where a later milestone will look — *Follow-ups* item 1 now names the test and says its expected exit code and stderr are what change — and the docstring states the real consequence. |
| nit 9 (binding) | `_cmd_mv` returns 1 for "not a file" / collision before `old_rel` / `new_rel` exist, so a cross-dated move onto an occupied destination exits **1**, while `cli.md`'s exit table listed the refusal under exit 2 with no precedence note. | Frozen: a **Precedence** paragraph in `cli.md` › *Cross-dated archived relocations* (mirrored), an amended exit-1 row in the `docs mv` exit table, and `test_mv_collision_still_exits_1_before_the_cross_dated_refusal`, which also stops Phase 6 hoisting the predicate above the two guards. |
| nit 10 | The follow-through list did not name the three **in-code prose** surfaces the new rule touches. | Added as item 9: the comment above `_BUILTIN_METADATA_FIELDS`, `check_doc`'s docstring rule list (including its `bad-date` line), and `check_doc`'s `unknown-field` comment beside `Finding`'s own rule enumeration. The milestone's wide-blast-radius risk says exactly this: nothing in the suite will notice a paragraph that was not updated. |
| nit 11 (binding) | Five `docs mv` neighbour tests asserted whole-tree `check` exit 0 rather than the absence of a NAMED finding — the project's own consistency standard, and these were the exception. | All five now go through a `_check_pairs` helper and assert the exact `(path, rule)` list, with the KNOWN-GAP test asserting the absence of a named finding on the **named** document. |

### What the reviewer confirmed

- The refusal position **before** the `--dry-run` branch is correct and
  implementable verbatim between `cli.py:7140` and `:7142`.
- Pinning D8's second residual as a KNOWN-GAP test is the right call and the
  test is honest; only nit 11 applied to it.
- The five rewritten RED reasons are genuinely the intended ones, verified by
  running the suite.

No finding required an operator decision, and none changes milestone scope or
behaviour intent.

## Phase 5 — Update Base Interfaces — 2026-08-16

### Objective

Land the vocabulary entry, `parse_date`'s keyword-only `label`, and **all
three** pure helpers item (H) freezes as Phase-5 signatures — wired nowhere, so
`check_doc`, `_archive_one` and `_cmd_mv` stay untouched and every CLI-level id
stays honestly RED at the seam.

### Actions taken

- **`parse_date` gained its keyword-only `label`** (`cli.py`, *Shared
  utilities*), verbatim from item (H):
  `parse_date(value, date_format="%Y-%m-%d", *, label="Updated")`. The body
  change is one interpolation — `f"{label}: malformed date {value!r} (expected
  {date_format})"`. **None of the six existing call sites was touched**; the
  default is what keeps every pre-M28a message byte-identical, and
  `test_parse_date_defaults_to_the_updated_label` (GREEN at baseline, and
  classified *genuine* for exactly this reason) is the proof rather than the
  claim.
- **`Archived` joined `_BUILTIN_METADATA_FIELDS`** (item (B)), and the comment
  block above it gained an M28a paragraph mirroring M25's `Revision:` one — a
  label the tool writes must never trip the tool's own allowlist warning. The
  paragraph also records the **two deliberate non-changes** at the site where an
  implementer would otherwise make them: the label stays out of `parse()`'s
  `known` set (so it surfaces through `docs list --json` under `extra_fields`)
  and out of migrate's `_REQUIRED_METADATA_FIELDS` (so a foreign `Archived:`
  line is demoted, never promoted — D7). This is follow-through item 9's first
  prose surface; the other three land in Phase 6, when the rule starts existing
  and the id starts being emitted.
- **The three pure helpers landed in one banner section** immediately above
  `check_doc` — the slot M27 used for `body_link_findings`, and the slot the
  rule reads from:
  - `archive_dir_date(rel, config)` — the shared config-aware reader. Three
    pins are stated in the docstring because each has a lock aimed at it: it
    reads `parts[1]` (the **first** segment, so `archive/<d>/sub/x.md`
    corroborates), it parses through `parse_date` with `config.date_format`
    (never `detect_archive_layout`'s hardcoded `strptime(parts[1],
    "%Y-%m-%d")`, and never `parse()`'s hardcoded default — defect E8), and
    `len(parts) < 3` is what makes `archive/x.md` carry no date.
  - `cross_dated_archive_move(old_rel, new_rel, config)` — Leg 2's predicate.
    The delegation to `archive_dir_date` **is** the contract, not an
    implementation detail:
    `test_cross_dated_archive_move_agrees_with_archive_dir_date` runs a 7 × 7
    matrix on a doubly non-default config against `archive_dir_date` itself, so
    any re-derivation — even a correct one — is the failure mode the fresh-eyes
    review added that group for. It returns the raw segments, never a
    `strftime` re-rendering.
  - `archive_date_findings(path, metadata, root, config)` — the pure rule, in
    item (C)'s binding evaluation order: `isinstance(recorded, str)` (not `is
    not None`, so a bare `Archived:` bullet group is *absent* rather than an
    `AttributeError` inside a function that never raises), `bad-date`
    **returns** with no drift finding after it (OQ-2), `_root_relative` rather
    than `path.resolve().relative_to(root.resolve())` (OQ-4 — the purity lock
    monkeypatches `Path.resolve` alongside `exists` / `is_file` / `is_dir` /
    `open`), and both messages interpolating `config.archive_dir` and the raw
    on-disk strings.

### Decisions & issues

- **Helper placement, and a named forward reference.** The banner section sits
  above `check_doc` rather than beside `_is_archived_rel`, which it
  forward-references. That is legal at module level and it is recorded in the
  banner comment as a **decision, not an oversight**: item (C) requires the
  *shared* archive-subtree notion, and *Follow-ups* item 4 hands the hoist to
  Phase 10, where `_is_archived_rel` can move next to `_root_relative` together
  with the three inlined copies of the predicate as one justified move. Phase 5
  stays minimal.
- **`recorded` is interpolated as received.** It arrives pre-stripped from
  `parse_metadata_block`, and interpolating it un-stripped matches
  `parse_date`'s own un-stripped `{value!r}`. No behaviour difference today and
  no test distinguishes the two; the docstring records why.
- **A factual correction to this log's own progress table.** Row 5 still named
  only Leg 1's two helpers, although the Phase-4 classification (*A
  classification call, recorded rather than left implicit*) had already recorded
  that `cross_dated_archive_move` lands here too and that the milestone's
  Phase-5 objective was corrected to match. The row is corrected in place; it is
  a correction of a stale statement of fact, not a scope change.
- `status.md`'s "authored **136** test ids" was likewise stale — the fresh-eyes
  fold-in moved the figure to 149 everywhere else. Corrected in the same commit.

### Verification

| Gate | Result |
|---|---|
| `pytest -q` | **28 failed / 1474 passed** (1502 collected) — exactly the 43 ids the Phase-4 classification assigned to Phase 5, flipped |
| residual RED | 26 at Phase 6 (4 `check_doc` wiring, 5 `docs check`, 8 `docs archive`, 9 `docs mv`) + 2 at Phase 7 (bundled skill) |
| `ruff check .` / `ruff format --check .` / `mypy src/ tests/` | clean |
| `docs check --root docs` | no violations (exit 0) |
| `git diff -- src/docs_cli/cli.py \| grep '^+' \| grep -E 'check_doc\|_archive_one\|_cmd_mv'` | only a banner comment and a docstring **naming** `check_doc`; **no line of any of the three functions changed** — the real Phase-5 exit criterion |

## Phase 6 — Implement Offline/Core Path — 2026-08-16

### Objective

Wire both legs at their three frozen touch points and nowhere else: one
`set_metadata_field` in `_archive_one`, one `findings.extend` in `check_doc`,
and one refusal in `_cmd_mv` — the "three touch points" Phase-1 amendment 3
corrected the wide-blast-radius bullet to.

### Actions taken

- **The writer** — one line in `_archive_one`, between the `Updated:` bump and
  the conditional `Archived-reason:`. It writes the `date_str` the member was
  already handed (computed once in `_cmd_archive` as
  `archive_date.strftime(config.date_format)` and already used to name the
  dated directory): **never a second `strftime`, never a `date.today()`
  re-read**. `apply_archive_plan`'s `plan.reason if index == 0 else None` was
  deliberately **not** touched, so the reason stays primary-only (M26 — D1)
  while the date reaches every member (A2). Position is decided *only* by this
  call order — `set_metadata_field` appends a new inline label at the end of
  the inline run and inserts before the first bare-label group — which yields
  item (A)'s `Lifecycle / Role / Project / Updated / Archived /
  Archived-reason` with a `Related:` group still following the run. Both are
  byte-level locks.
- **The rule** — one `findings.extend(archive_date_findings(path, metadata,
  root, config))` between the `status-drift` block and M25's `duplicate-field`
  block, at item (D)'s frozen position.
  `test_check_doc_reports_archive_date_drift_at_the_frozen_position` asserts
  the exact sequence `["status-drift", "archive-date-drift",
  "duplicate-field"]` on a document that trips all three, so the too-early and
  the too-late placement each fail.
- **Leg 2's refusal** — in `_cmd_mv`, between the `old_rel` / `new_rel`
  derivation's `except ValueError` return and the `compile_exclude_predicate`
  comment: amendment 2's position, which the fresh-eyes reviewer confirmed
  verbatim at those two line numbers. Both stderr lines are item (E)'s frozen
  strings. Returning 2 here emits **no** `--json` record — `_emit_json` is
  defined below it and never called — which the refusal test asserts with
  `proc.stdout == ""` under `--json`.
- **Follow-through item 9's remaining prose surfaces**, per the conductor's
  split (they land with the rule rather than with the helpers):
  `check_doc`'s docstring gained an `archive-date-drift` entry beside the M27
  body-link ones and its `bad-date` line widened from "`Updated:` not
  parseable" to "a date field that does not parse — `Updated:`, or
  `Archived:`" (matching `cli.md`); `Finding`'s docstring rule enumeration
  gained `archive-date-drift (M28a)`; the `unknown-field` comment now names
  `Archived:` in the built-in list; and `set_metadata_field`'s "Used by …"
  line names the new label.

### Decisions & issues

- **No implementation surprise.** Every one of the 26 ids flipped on the first
  run, and the four placement traps the Phase-4 adversarial pass enumerated
  (inside `preflight_move_plan`, after the walk, above the `is_file` /
  `exists` guards, and an inlined config-blind predicate) were avoided by
  construction rather than discovered by failure.
- **Two ids are contracts and were deliberately left alone.**
  `test_mv_neighbour_3_to_the_archive_root_is_silent_without_a_witness` pins
  D8's second residual (*Follow-ups* item 7, operator decision OQ-7) and stays
  GREEN as a KNOWN GAP;
  `test_archive_renders_the_witness_in_the_trees_date_format` still asserts
  defect E8's exit-2 INDEX-refresh failure, which the `label` default keeps
  byte-identical (`parse()` retains its hardcoded ISO default). *Follow-ups*
  item 1 owns the coupling. Neither was "fixed".

### Verification

| Gate | Result |
|---|---|
| `pytest -q` | **2 failed / 1500 passed** — only `test_skill.py`'s two Phase-7 ids remain RED |
| `ruff check .` / `ruff format --check .` / `mypy src/ tests/` | clean |
| `docs check --root docs` | no violations (exit 0) — the dogfood tree stays silent with the rule live |
| `git diff ac66005 --numstat -- tests/` | **empty** — no test source changed in Step 2 at all, let alone was relaxed |
| spot-run: `test_archive_leaves_the_tree_check_clean`, `test_check_doc_duplicate_archived_label_still_fires_duplicate_field`, `test_check_tree_dogfood_repo_docs_gains_no_archive_date_drift`, `test_check_tree_pre_m28a_fixtures_gain_no_archive_date_findings` (46) | 49 passed — the four families that were degenerate before this phase and are genuine now |

## Phase 7 — Update Tool/Wrapper Layer — 2026-08-16

### Objective

Reconcile every parallel surface. Phase 1 landed the author-facing halves in
`cli.md` and `convention.md`, so most of this phase is **verification, not
authoring** — and the parts that were genuinely outstanding are the bundled
skill, the argparse strings, the CHANGELOG and the feedback-log closeout.

### Actions taken

- **Bundled skill** (the two RED ids, and the third row parity asks for):
  `SKILL.md`'s `docs archive` row now names `Archived:` by its exact label and
  says it lands on **every** doc the operation moves while `Archived-reason:`
  stays on the primary; its `docs mv` row says the move **refuses** and says
  which moves, so the refusal cannot read as universal; and its `docs check`
  row names `archive-date-drift` and its present-only nature.
  `references/use-cases.md` gained the witness on the closeout row, the
  refusal on the `docs mv` row, `archive-date-drift` on the `docs check` row,
  and a new *Upgrade: the archive-date witness (M28a)* section — the honest
  analogue of the M25 and M27 upgrade sections — whose four rows carry the
  closeout, the refusal, the drift repair, and the `bad-date` residual.
- **Spec verification, item by item, against the Phase-7 objective.** Every
  surface it names was re-read rather than recalled: `cli.md`'s archive step
  list + witness paragraph, its `docs check` rule list / `rule` table row /
  built-in field set / exit-2 line / *Archive-date corroboration* subsection
  with its own *Upgrading from 1.x*, its `docs mv` *Cross-dated archived
  relocations* subsection with the Precedence paragraph and the
  four-neighbour table; `convention.md`'s *Optional fields* rows, its
  *Archive subtree* paragraphs, and all three archived-immutability
  paragraphs plus M26's byte-identity list. **Two real gaps were found and
  corrected** (below).
- **Argparse** (RESOLVED OQ-1): the flag delta is **empty (confirmed, not
  assumed)** — `docs archive` / `docs mv` / `docs check` option sets were
  diffed mechanically against a `git worktree` at `7f7853b` and are
  identical — and the **two `description` strings gained one clause each
  under the surface-parity gate**, following M28's own precedent for a
  behaviour change with no flag delta: `mv_p` now says a move between two
  different dated archive directories refuses (exit 2, zero bytes) in every
  mode, and `check_p`'s rule-family list now names an archived document whose
  recorded `Archived:` date its location does not corroborate.
- **`CHANGELOG.md`**, under the existing `UNRELEASED` heading (no
  `pyproject.toml`, no version pin — M25 — D6): two `Added` entries (the
  witness, with the pinned block position and the one-value/one-source rule;
  and `archive-date-drift`, with both message forms, the closed four-key
  record and the present-only contract), one **BREAKING** `Changed` entry for
  the `docs mv` refusal with both frozen lines, the four permitted neighbours
  and the exit-1 precedence, and an *Upgrading from 1.x* passage stating the
  present-only contract plainly (**zero** findings on a 1.x tree, no
  backfill), the by-hand escape, and **OQ-2's residual** — a hand-adopted
  foreign tree carrying a non-date `Archived:` value gains a new `bad-date`
  error. The heading's own scope line moved from "M25–M28" to "M25–M28a".
- **`feedback-log.md` issue #1 is CLOSED.** A dated 2026-08-16 *Resolution*
  bullet records that finding 3's archive-date half is answered by M28a's two
  legs, why both were needed (the witness can never reach the 46 documents
  archived before it existed), and that the reporter's literal `pairs-with`
  rule stays declined with its measured number — 7 findings on a correct
  tree, every one a deliberate cross-milestone edge. The Status bullet now
  says the issue has no open item left.

### Decisions & issues

- **Two spec gaps found by verification, both corrected here.** Neither
  changes scope or behaviour intent; both were factually wrong statements in
  a spec that ships byte-identically inside the wheel:
  1. `convention.md`'s built-in always-allowed metadata label list
     (`Lifecycle`, `Role`, `Project`, `Updated`, `Related`,
     `Archived-reason`, `Revision`) **omitted `Archived`** — while `cli.md`'s
     parallel list named it and `_BUILTIN_METADATA_FIELDS` contains it. Added,
     with the M25/M28a reason stated once for both labels.
  2. `convention.md`'s *Cross-dated archived relocations refuse* paragraph
     still enumerated **three** permitted neighbours. Phase-1 amendment 6
     swept "three" to "four" across eight derived surfaces, but its list did
     not include `convention.md`, so the sentence survived — disagreeing with
     `cli.md`'s own four-row table two documents away. Swept to four, naming
     the two-spellings-of-one-date case and why it completes.
- **The mirrors were re-copied in the same commit** as the source edits, per
  the CLAUDE.md surface-parity gate, and `tests/fixtures/expected/docs-INDEX.md`
  was re-synced in the same commit because `docs touch` moved
  `feedback-log.md`'s `Updated:` across the day boundary.

### Verification

| Gate | Result |
|---|---|
| `pytest -q` | **1502 passed / 0 failed** — fully GREEN |
| `ruff check .` / `ruff format --check .` / `mypy src/ tests/` | clean |
| `docs check --root docs` | no violations (exit 0) |
| `cmp docs/cli.md src/docs_cli/skill/references/cli.md` and the same for `convention.md` | byte-identical |
| flag delta vs `7f7853b` for `archive` / `mv` / `check` | **empty** (mechanically diffed) |
| `docs mv --help` / `docs check --help` | carry the new clauses and agree with `cli.md` |

## Phase 8 — Run Tests (GREEN) — 2026-08-16

### Objective

Run every product and quality gate with exact counts, and prove mechanically
that no pre-existing test id was removed and no test was weakened to get here.

### Verification

| Gate | Result |
|---|---|
| `.venv/bin/python -m pytest -q` | **1502 passed, 0 failed** in ~55s; 0 errors, 0 xfail/xpass, 0 warnings, 0 collection errors |
| `.venv/bin/ruff check .` | All checks passed |
| `.venv/bin/ruff format --check .` | 48 files already formatted |
| `.venv/bin/mypy src/ tests/` | Success: no issues found in 49 source files |
| `.venv/bin/docs check --root docs` | no violations found (exit 0) |
| `cmp docs/cli.md src/docs_cli/skill/references/cli.md`; same for `convention.md` | byte-identical |

### Mechanical no-regression proof

Ids collected from a throwaway `git worktree` at the pre-Phase-1 commit
`7f7853b` and from HEAD, and compared with `comm` — the same method Phase 4
used:

| Measure | Result |
|---|---|
| ids at `7f7853b` | **1341** |
| ids at HEAD | **1502** |
| `comm -23 old new` — **removed** ids | **0** |
| `comm -13 old new` — added ids | **161** |
| pre-existing ids now failing | **0** (the suite has no failures at all) |
| `git diff 7f7853b --numstat -- tests/` | **0 deleted lines in every test SOURCE file.** The only deletions anywhere under `tests/` are **8 lines in `tests/fixtures/expected/docs-INDEX.md`** — seven `Updated:` values (`status.md`, `plan.md`, `cli.md`, `convention.md`, `feedback-log.md` and both M28a docs) and the generated-on line, re-synced whenever `docs touch` moved a date across the day boundary. |
| `git diff ac66005 --numstat -- tests/` (Step 2 alone) | **2 changed lines, both in the INDEX snapshot.** Step 2 changed **no test source at all** |

**No test was relaxed, weakened, deleted or rewritten** — not in Step 2, and
not across the milestone. Every one of the 71 RED ids went GREEN because the
behaviour it asserts now exists, in the phase the Phase-4 classification
assigned it to: 43 at Phase 5, 26 at Phase 6, 2 at Phase 7. Two ids that a
careless implementer would have "fixed" were deliberately left alone and are
still GREEN as written —
`test_mv_neighbour_3_to_the_archive_root_is_silent_without_a_witness` (D8's
second residual, *Follow-ups* item 7, operator decision OQ-7) and
`test_archive_renders_the_witness_in_the_trees_date_format` (defect E8's
exit-2 INDEX-refresh failure, *Follow-ups* item 1).

## Phase 9 — Integrate / Accept / Dogfood — 2026-08-16

### Objective

Prove each measured property on throwaway copies, unattended and with no
stdin. Ten flows; the real tree is never written to.

### Flows and results

**1 — E1d refused, on a document that carries NO witness.** On a `cp -a` copy
of `docs/`:

```console
$ docs mv archive/2026-05-25/m9-pypi-publish.md archive/2026-07-03/m9-pypi-publish.md
docs: mv: archive/2026-05-25/m9-pypi-publish.md -> archive/2026-07-03/m9-pypi-publish.md crosses dated archive directories (2026-05-25 to 2026-07-03); refusing before any write
docs: mv: the dated directory records when a document was archived; to correct a genuinely mis-dated archive, move the file by hand, correct its `Archived:` line, and re-run `docs check`
exit 2
```

`diff -r` against a pristine copy: **identical** — zero bytes written. This
document carries no `Archived:` line, which is the case Leg 1 can never reach
and the reason Q4 adopted both legs. Setup measured the same command
completing at **exit 0** with `docs check` clean.

**2 — E1d refused, on a document that DOES carry the witness, in every mode.**
`docs archive feedback-log.md --reason …` on the copy first, which wrote:

```
Lifecycle: archived
Role: log
Project: docs
Updated: 2026-08-16
Archived: 2026-08-16
Archived-reason: dogfood flow 2
```

— item (A)'s pinned order exactly. The cross-dated `mv` of it then refuses:
**exit 2** plain, **exit 2** under `--dry-run` (2 stderr lines, and **no**
`would move …` line — the preview does not lie), **exit 2** under `--quiet`
(both lines still printed), and **exit 2** under `--json` with **0 bytes** on
stdout. Tree byte-identical after each.

**3 — a hand-made relocation is detected, where it was silent before.** On a
fresh copy: archive a document (so it gains the witness), then relocate it
with a plain `mv` into a different dated directory. `docs check --json` rule
tally, on **one** tree, from **two** CLIs:

| CLI | tally |
|---|---|
| M28a (HEAD) | `broken-ref: 11`, **`archive-date-drift: 1`** |
| pre-M28a (`7f7853b` worktree) | `broken-ref: 11` |

The delta is exactly the one new finding; the `broken-ref` noise is the hand
`mv` not rewriting references, and predates M28a. The record, showing the
closed four-key set:

```json
{"path": "archive/2026-07-03/feedback-log.md", "severity": "error", "rule": "archive-date-drift",
 "message": "Archived: 2026-08-16 but the file is in archive/2026-07-03/ (move it back, or correct the recorded date)"}
```

**4 — all FOUR permitted neighbours complete** (amendment 6), each with the
destination asserted to exist afterwards: (i) a rename within
`archive/2026-05-25/`; (ii) `archive/2026-05-25/…` → the active root;
(iii) a dated directory → the archive root (D8's second residual, permitted by
design); (iv) `archive/2026-05-25/` → `archive/2026-5-25/` — **two spellings
of one date**, the case a raw-string predicate would refuse. All exit 0.

**5 — one refusal, and one non-refusal, on a non-default tree.** A throwaway
tree with `[archive] dir = "attic"` and `date_format = "%d-%m-%Y"`:
`attic/01-01-2026/old.md` → `attic/04-03-2026/old.md` **refuses**, naming the
configured directory and the raw segments in the tree's own format
(`crosses dated archive directories (01-01-2026 to 04-03-2026)`); and on the
**same** tree `archive/2026-01-01/note.md` → `archive/2026-03-04/note.md`
**completes at exit 0**, because there `archive/` is an ordinary
subdirectory. Both polarities of the config-blindness trap, live.

**6 — the silence proof over all 46.** On a clean copy: **46** archived
documents (excluding `INDEX.md`), `docs check --json` → **0 findings total**,
therefore **0** `archive-date-drift` and **0** `Archived:`-sourced
`bad-date`, exit 0. Exactly **two** files in the tree contain an
`^Archived: ` line — `cli.md` and the milestone doc — and in both the first
occurrence is far past the metadata-block terminator (line 123 and line 149
against a block ending at line 7), i.e. inside fences. The durable form of
the claim (OQ-9) is what the suite pins: **zero drift findings over a tree
with at least 46 archived documents**.

**7 — a real closeout.** `docs archive m26-safe-archive-selection.md
--cascade-only 'm26-*' --reason "M26 complete (dogfood)"` on a copy: exit 0,
and **every** moved member carries `Archived: 2026-08-16` — the operation's
one shared date — while `Archived-reason:` is on the **primary alone**. The
`Related:` bare-label group still follows the inline run. `docs check` on the
result: **exit 0**.

**8 — `docs migrate --apply` writes no witness.** An isolated archive-shaped
foreign tree (`archived/old-notes/` holding a bare legacy file and one
carrying a foreign `Archived: true`). Migrate normalised it into
`archive/2026-08-16/` and set `Lifecycle: archived` — and wrote **no**
`Archived:` line anywhere (`grep -rn '^Archived:'` → none), while the foreign
one was **demoted** to `Migrated-Archived: true` under `## Migrated
metadata`. D7, live.

**9 — the E5 decline holds.** The same copy carries exactly **7**
archived↔archived `pairs-with` edges spanning different dated directories —
`m12↔m10`, `m12↔m11`, `m13↔m12`, `m7↔m4`, `m8↔m5`, `m8↔m6`, `m9↔m6` — and
the rule emits **0** findings on it. The declined rule would have emitted 7 on
a correct tree; the witness emits 0.

**10 — runtime.** Five runs each of `docs check` over the copy — **73**
documents plus the generated `INDEX.md`, the tree the milestone's Phase-9
instruction calls the 73-document tree:
HEAD **0.18 s** (steady state; 0.23 s cold), pre-M28a `7f7853b` **0.18 s**.
The delta is **below the 10 ms measurement floor** — indistinguishable from
zero, which is what pure path arithmetic with no filesystem access and no
second pass predicts.

### Decisions & issues

- **An operator error during flow 8, fully reverted, recorded rather than
  hidden.** A `cp -a` of a fixture path that does not exist failed, its
  following `cd` failed with it, and the next command — `docs migrate .
  --apply` — therefore ran against the **repository root** instead of the
  throwaway copy, writing metadata blocks across the tracked tree and
  creating an untracked `.docs.toml` and `archive/` at the root. **No commit
  was involved and nothing was lost**: `git restore --source=HEAD --staged
  --worktree .` plus removing the two untracked paths returned the tree to
  `19147ea` exactly — `git status --porcelain` empty, 1502 passed,
  `docs check --root docs` exit 0, both mirrors byte-identical, all
  re-verified. **Zero deletions or renames** were involved at any point. Flow
  8 was then redone against an isolated tree built from scratch, and every
  remaining flow used **absolute `--root` paths only** — never `cd`, never a
  bare `.` root. The exit criterion "the real tree is untouched" holds as of
  this entry and was re-measured, but it is recorded here that it was
  transiently violated and repaired rather than never violated.

### Verification

- Every flow ran unattended with no stdin, on `cp -a` copies or trees built
  from scratch under `/tmp`.
- The refusal flows left their copies **byte-identical** (`diff -r` against a
  pristine copy).
- The silence proof covers all **46** archived documents; the closeout flow
  ends `docs check` clean; runtime is recorded and bounded below 10 ms.
- `git status --porcelain` on the real repository: **empty**. HEAD is
  `19147ea`.

## Phase 10 — Quality, Docs, Refactor — 2026-08-16

### Objective

Run `/simplify` over the new code and the named candidate, close
`architecture.md` and `test-strategy.md`, and write the completion summaries.

### `/simplify` — the candidate taken

***Follow-ups* item 4, taken in full, and it turned out to be larger than
recorded.** E7 counted **three** inline copies of the archive-subtree
predicate (`check_doc`, the `docs list` walk, `docs project set`) beside
`_is_archived_rel`, which already provides exactly that expression. Reading
for the collapse found **five**: `walk` and `_known_projects` each hoist the
prefix into a local (`archive_prefix = config.archive_dir`) and then spell the
test by hand inside their `os.walk` loop — a micro-optimisation that reads as
noise and saves nothing measurable.

All five are now calls, and `_is_archived_rel` was **hoisted** from beside the
archive verb up next to `_root_relative`, where every consumer of a
root-relative POSIX string already lives. Two things follow:

- The predicate has **one** spelling in the tool. That matters more after
  M28a than before it, because item (C)'s guarantee — that Leg 1 and Leg 2
  can never disagree about what the archive subtree is — was structural for
  the two new helpers and by-convention for everything else.
- Phase 5's **forward reference disappears**. The banner comment above the
  M28a helpers no longer has to explain why `archive_dir_date` calls a
  function defined 2,800 lines below it; it now records the positive reason
  (the shared notion) instead of excusing the layout.

Verified behaviour-preserving: **1502 passed** before and after, gate clean,
`docs check --root docs` exit 0, and the `docs check` runtime over the
73-document copy unchanged at **0.18 s** (five runs each) — `walk` is the
hottest path in the tool, so the loss of its hoisted local was measured rather
than assumed.

### `/simplify` — candidates evaluated and REJECTED

Recorded with reasons, as M28's simplify pass did:

| Candidate | Rejected because |
|---|---|
| Have `archive_dir_date` return `(date, segment)` so `cross_dated_archive_move` and `archive_date_findings` stop re-splitting the path | It widens the **shared** reader's return type for one caller's convenience, and Leg 1 would unpack a tuple it does not need. `test_cross_dated_archive_move_agrees_with_archive_dir_date` compares the two against each other over a 7 × 7 matrix precisely because the delegation is the contract; changing that signature is the coupling item (C) exists to avoid. The "duplication" is two occurrences of `rel.split("/")[1]`. |
| Collapse `archive_date_findings`'s two message branches into one f-string with a conditional | They are **two frozen message forms** (item (E), A and B), each pinned verbatim by its own test and each quoted in `cli.md`, `convention.md` and the CHANGELOG. A merged expression is harder to read and harder to grep for than the two it replaces. |
| Extract `_cmd_mv`'s refusal block into a helper | It is one predicate call, one unpack and two `print`s, sitting where every other `_cmd_mv` refusal sits — inline, in reading order. A helper would add an indirection to read one exit path and would hide the position that Phase-1 amendment 2 spent a whole amendment fixing. |
| Fold `len(parts) < 3` into the `_is_archived_rel` guard | The two conditions answer different questions — *is this in the archive subtree* and *is there a segment after it* — and item (C) numbers them separately because `archive/x.md` answers yes then no. Merging them makes the `None` for the archive-root case unexplainable. |

### Documentation closed

- **`docs/architecture.md` › `check`** — `archive-date-drift` added to
  `check_doc`'s rule list, plus a bullet for the two pure helpers stating
  explicitly that `archive_dir_date` is **shared by both legs** and that it is
  the config-aware sibling `detect_archive_layout` is not.
- **`docs/architecture.md` › `archive`** — the section title now names M28a,
  and the `_archive_one` bullet (previously "unchanged since M2") records the
  witness write, the one-value/one-source rule, and that the field's block
  position is decided only by the `set_metadata_field` call order because the
  tool has no field-order rule.
- **`docs/architecture.md` › `mv`** — RESOLVED OQ-4 places this here in
  Phase 10 alongside `check` and `archive`, so its omission from Phase 7's
  file list is a decision rather than a gap. The pipeline diagram gains the
  refusal above the walk, and a closing paragraph gives the three consequences
  of that position (every mode; the named document rather than a malformed
  sibling; unreachable by `[exclude]`) and why it is **not** inside
  `preflight_move_plan`.
- **`docs/test-strategy.md`** — the fixture-source list gains the
  `archivedate-*/` family beside `bodylink-*/`, `movelink-*/` and
  `reciprocal-*/`, one semantic per tree, including why three deliberately
  drifted trees need their own sweep rather than a widened
  `_legacy_tree_names`.
- Completion summaries in this log and the milestone doc; the phase
  checklist, both progress tables, `docs/status.md` and `docs/plan.md`.
  **M28a stays `Lifecycle: active`** until the M29 publish closeout; it is
  deliberately **not** archived here.

### Verification

| Gate | Result |
|---|---|
| `pytest -q` | **1502 passed / 0 failed**, before and after the refactor |
| `ruff check .` / `ruff format --check .` / `mypy src/ tests/` | clean |
| `docs check --root docs` | no violations (exit 0) |
| both skill mirrors | byte-identical |
| `docs check` runtime over 73 documents | 0.18 s, unchanged by the hoist |

## Step-2 same-instance audit — 2026-08-16

Run against Phases 5–10 after the last phase and before returning, per the
ship-milestone consistency / completeness / accuracy checklist. **Fifteen
issues found; all fifteen fixed here.** Nothing found changes milestone scope
or behaviour intent, so nothing is escalated as a decision; three observations
are recorded at the end for the operator's awareness.

### Issues found and fixed — documentation consistency (ten)

A cross-document sweep of `status.md`, `plan.md`, the milestone doc and this
log against measured reality found that the trackers had been updated *forward*
phase by phase but never swept *backward* for statements written at an earlier
phase that had since become false.

1. **`status.md`'s M28a milestone-table row was a whole step behind** — "Step 1
   (Phases 1–4) complete", "Phase 5 next", and "71 RED / 90 GREEN" as the live
   state, all contradicting the same file's own *Current milestone* section
   twelve hundred lines above it.
2. **`status.md`'s v2.0 backlog bullet still said "IN FLIGHT, Step 1 — Phases
   1–4 — complete".**
3. **`status.md`'s M28 narrative still said "M28a and M29 are next"**, while
   the same file's *Next action* paragraph correctly named M29 alone.
4. **`plan.md` said "Step 2 (Phases 5–10) is next."**
5. **`plan.md` said "M28a is in flight (Step 1, Phases 1–4, complete
   2026-08-16)"** — which also mis-dated Phase 1, whose contract is
   2026-08-15 everywhere else.
6. **The milestone doc's `Progress:` bullet opened with "Step 2 is in flight"
   and declared the milestone implementation-complete six lines later.**
7. **This log's `Progress:` bullet had the same defect.**
8. **`status.md` said "No product code has changed"** in the present tense,
   inside a section that had already listed the three touch points.
9. **The milestone doc said "The suite stands at 1502 collected, 71 RED and 90
   GREEN … and `cli.py` untouched"** — true of the Phase-4 baseline, false of
   the shipped state. Reworded as the captured baseline it describes.
10. **`plan.md` said the Step-1 audit and review "between them fixed eleven
    issues".** This log records eight at the audit and eleven at the review,
    plus the one wrong implementation the suite had not caught. Corrected to
    nineteen, with the split named.

### Issues found and fixed — accuracy against the code (five)

11. **This log's phase-progress table had a stray `|` in rows 9 and 10**,
    giving those two rows a fifth column: the "Original scope:" text appended
    to each ran into the cell's own terminator. Found by counting pipes per
    row rather than by reading.
12. **`architecture.md`'s module map was stale in four places.**
    `cli.py (~7.7k lines)` against an actual 8,981; the `check` line
    enumerated the rule-adding milestones M3 / M25 / M27 but not M28a; the
    `archive` line stopped at M26; and the `mv` line still stopped at M2,
    missing M28's plan-before-move as well as M28a's refusal. All four
    corrected — the `mv` one is a correction of an M28-era omission made in
    passing, recorded so it does not read as M28a's.
13. **`cli.md` claimed `archive-date-drift` "carries **both** dates" in
    `message`.** That is true of message form A and **false of form B**, which
    names the recorded value and says there is no dated directory to compare
    it against — because in that shape there is no second date to name. The
    same file printed the form-B line correctly 600 lines later, so the spec
    contradicted itself. Reworded to state both forms.
14. **Three parallel byte-identity lists outside `convention.md` still named
    only `Archived-reason:`.** Q6 / D9 requires the witness to be named
    wherever an archived-document guarantee is enumerated — a field not named
    in those lists is a field with no stated guarantee — and Phase 1 swept
    `convention.md`'s four (three immutability paragraphs plus M26's list) but
    not their siblings elsewhere: `cli.md`'s `docs relate` archived-endpoint
    list, the `UNRELEASED` CHANGELOG's M25 `relate` entry, and the bundled
    `references/use-cases.md` repair row. All three now name `Archived:`
    beside `Archived-reason:`. The code already agreed with `convention.md` —
    `docs relate` writes only `Related:` / `Updated:` / `Revision:`, and the
    sole writer of `Archived` is `_archive_one` — so these were incomplete
    enumerations rather than wrong ones.
15. **`references/use-cases.md` overstated the drift message the same way as
    issue 13** ("naming the recorded date and the directory the file now sits
    in"). Corrected to name the directory only for the different-dated-directory
    shape.

`docs/cli.md` changed for issues 13 and 14, so **both mirrors were re-copied
and the INDEX artifacts re-synced in the same commit**, per the CLAUDE.md
surface-parity gate.

### Checked clean

- **Every deliverable and success criterion in Phases 5–10's range is met**,
  verified against the milestone doc read rather than recalled: the witness on
  every member at the pinned position; the pure config-aware helper and the
  rule at the frozen position; the vocabulary entry with both deliberate
  non-changes still in place (`parse()`'s `known` set at `cli.py:1234` and
  migrate's `_REQUIRED_METADATA_FIELDS` at `:4276` are unchanged, confirmed by
  reading); both specs, both mirrors, the CHANGELOG and the feedback log; the
  dogfood; and Leg 2.
- **All four item-(H) signatures match the freeze byte-for-byte**, confirmed
  by `inspect.signature` rather than by eye.
- **Every frozen message string is byte-identical** across `cli.py`,
  `docs/cli.md`, `CHANGELOG.md` and the tests — both `docs mv` refusal lines,
  both `archive-date-drift` forms, and the `Archived:` `bad-date` line.
- No placeholder, `NotImplementedError`, TODO or commented-out code anywhere
  in the Step-2 diff.
- The diff contains **only** M28a's work: 23 hunks in `cli.py`, each traceable
  to a named change (vocabulary, `parse_date`, the three helpers, the three
  touch points, four in-code prose surfaces, two argparse strings, and the
  five simplify sites plus the hoist), and fifteen files in total with no
  unrelated edit.
- Both exit-code tables in `cli.md` — the `docs mv` one and the global summary
  — carry the refusal and the exit-1 precedence.
- `docs check --root docs` exits 0; every edited doc's `Updated:` was bumped by
  `docs touch`; `docs/INDEX.md` and `tests/fixtures/expected/docs-INDEX.md` are
  in lockstep; both skill mirrors are byte-identical.
- Six commits, one per phase, plus this audit; messages follow the project's
  convention; no secrets in the diff.

### Observations for the operator (no decision required)

1. **The real tree was transiently mutated during Phase 9 and fully
   reverted.** A failed `cp -a` and its failed `cd` left a subsequent
   `docs migrate . --apply` pointing at the repository root. No commit was
   involved, `git restore --source=HEAD` returned the tree to `19147ea`
   exactly, and zero deletions or renames were involved. It is recorded in the
   Phase-9 entry rather than hidden, and every later flow used absolute
   `--root` paths only.
2. **`cli.md`'s M18 archive-exception paragraph still says "other metadata"
   generically** where `convention.md`'s now names `Archived:` and
   `Archived-reason:` explicitly (Phase-1 amendment 5). That asymmetry is
   deliberate: amendment 5 scoped the explicit naming to `convention.md`'s
   three paragraphs, and `cli.md`'s generic phrasing remains true. Left as
   Phase 1 decided it.
3. **`architecture.md`'s `mv` module-map line was stale for M28, not just
   M28a**, and was corrected here. If a future audit wants a rule, it is that
   the module map's per-verb annotations are not covered by any test and are
   swept only when a milestone happens to read them.

## Step-2 fresh-eyes review fold-in — 2026-08-16

An independent fresh-eyes pass over Phases 5–10 returned **no blockers** and
the verdict *ship it*: items (A)–(H) implemented verbatim, every frozen string
byte-for-byte, all four pinned positions exact. It **mutation-tested the suite
on an isolated copy — 19 mutations, 19 killed, zero survivors**, including the
three "passes everything else and fails only here" cases (parsed-versus-string
comparison, raw-versus-re-rendered message strings, and config-blindness).
Every finding was documentation or test hygiene. All four should-fixes and all
six binding nits are folded in below; the conductor made the calls on the nits
and none required an operator decision.

### The three disclosed items, independently cleared

- **The Phase-9 mutation is fully repaired**, verified six ways by the
  reviewer and again by the conductor: `git status -uall` empty; no stash; 628
  on-disk files equal to 628 in the index with zero drift; `19147ea..HEAD`
  thirteen files all `M` with zero deletions or renames; only two `docs/*.md`
  metadata blocks changed, both legitimate `Updated:` bumps; no `^Migrated-`
  anywhere under `docs/` or `src/`; no root `.docs.toml` / `INDEX.md` /
  `archive/`; reflog clean with no reset or amend; and `cli.py`'s working blob
  hash equal to its HEAD blob. **The damage window is provably empty.**
  Recording it rather than hiding it was confirmed as the right call.
- **The five collapses and the hoist are provably behaviour-preserving**:
  every site carried the literally identical expression, `Config` is a frozen
  dataclass so it cannot change mid-loop, and in `walk` the predicate only
  sets `archived=True` while directory pruning is a separate statement — which
  files are visited is untouched. Going beyond item 4's stated three was
  confirmed fine; no revert wanted.
- **The "both dates" correction is accurate** in `cli.md`, its mirror and
  `use-cases.md`. One instance survived, which is F5 below.

### Should-fixes folded in

| # | Finding | Resolution |
|---|---|---|
| F1 | `cli.md`'s M28a *Upgrading from 1.x* said "Nothing an adopter already has starts failing… The one behaviour change is in `docs mv`, **not in `docs check`**." Measurably wrong: a document carrying `Archived: true` gave exit 0 before and now gives `error: [bad-date] Archived: malformed date 'true'` at exit 2. OQ-2 is BINDING and requires that residual to be **named** in the upgrade note — the CHANGELOG named it and `cli.md` **denied** it, eight lines below `cli.md`'s own `bad-date` paragraph. **A second instance of the exact self-contradiction the same-instance audit caught as its issue 13.** | Adopted the CHANGELOG's two-item form verbatim in shape: item 1 the `docs mv` refusal, item 2 the `bad-date` residual with why only a hand-adopted tree can reach it. Mirror re-copied. |
| F2 | **`docs archive --help` never mentioned the witness.** `mv` and `check` each got their M28a clause at Phase 7; the verb that **writes** the field did not. The milestone's *Testing and quality gate* names `docs archive --help` in the surface-parity list, and Phase 7's own verification table checked only `mv --help` and `check --help` — `archive` was silently dropped. Nothing guarded it: no test asserted M28a content in **any** `--help`. | `archive_p.description` extended with the every-member witness and the primary-only reason, and a new lock — `test_argparse_help_teaches_the_archive_date_witness_and_the_mv_refusal` — asserts M28a content in **all three** descriptions, so the gap cannot re-open on any of them. |
| F3 | **`SKILL.md` prescribed an escape its own rules forbid.** The `docs mv` row told the agent to "move the file by hand, correct its `Archived:` line, and re-run `docs check`", while *Three things never to hand-edit* says never `mv`/`git mv` out of `archive/<date>/` and that a metadata block is "Never hand-write or hand-edit". An agent obeying the never-rules could not execute the documented escape. | The never-rules section gains **The one sanctioned exception** — named as exactly the escape `docs mv` prints, scoped to a genuinely mis-dated archive, with `docs check` as the proof the repair landed — and the `docs mv` row now points at it. `Archived:` also added to the metadata-block bullet's field list. |
| F4 | **Migrate's demotion statement was absent from both specs.** Phase 7's objective names "the `docs migrate` section's statement that the witness is never written **and a foreign one is demoted**". The non-write half was present; `Migrated-Archived` appeared nowhere in `docs/cli.md` or `docs/convention.md` — only in `CHANGELOG.md` and `use-cases.md`. The behaviour is correct and test-locked; the spec simply did not say it. | One clause added to `cli.md` › *Preserving extra metadata*, naming the demotion and **why** (migrate's dates come from `Updated:` or mtime, neither observed by the tool — D7). Mirror re-copied. |

### Binding nits folded in

| # | Finding | Resolution |
|---|---|---|
| F5 | The form-B overclaim survived a **third** time, in `docs/feedback-log.md` ("naming both the recorded date and the directory the file now sits in"). | Corrected to the same two-form wording used in `cli.md` and `use-cases.md`. |
| F6 | `docs check --help` said "an **archived** document"; the rule also fires on **non-archived** documents — Q7's motivating case is a document moved *out* of the archive whose `Lifecycle:` was then hand-edited, where `status-drift` is silent. Both specs correctly say "a document". | Help string brought into line, and the new F2 lock asserts `"archived document" not in check_help` so it cannot drift back. |
| F7 | The *Follow-ups* preamble said every item is "deliberately **not** implemented here", but item 4 **was** implemented in Phase 10 — and item 4 still said "Three inlined copies" where five were collapsed. | Preamble now states the item-4 exception explicitly; item 4 is marked **DONE in Phase 10**, records three-measured-versus-five-found, and keeps the trail from E7 to the collapse readable. |
| F8 | Two stale worktrees at `58955ef` (18.6 MB) were registered in `.git/worktrees/{base,pre}` from the setup session. | `git worktree prune` was a no-op because both directories still existed. Both verified clean (`git status --porcelain` empty in each), removed with `git worktree remove`, then pruned. `.git/worktrees` is gone, `git worktree list` shows only the repository, and HEAD / branch / working tree are undisturbed. |
| T1 | `test_mv_does_not_refuse_inside_an_ordinary_archive_named_subdirectory` was **weaker than its docstring**: `_attic_tree` varies both config axes at once, but its ordinary `archive/` children were ISO-named — so a predicate hardcoding only the *directory* while honouring `date_format` would pass for the wrong reason (the segments simply would not parse). | The two directories are now named in the tree's own `%d-%m-%Y` format (`archive/01-01-2026/` → `archive/04-03-2026/`), so only a predicate honouring `config.archive_dir` completes. The docstring says why. **Re-proved by mutation, not assumed** — see below. |
| T2 | **Leg 2's stderr was never asserted by equality** — only by containment, which would accept a third line, a `would move …` preamble, or the two lines in the wrong order. | `test_mv_refuses_a_cross_dated_relocation_of_a_witness_carrying_document` now asserts `proc.stderr.splitlines() == [refusal, escape]`. The order matters: the escape reading *before* the reason it escapes is not "the escape ships in the same breath as the refusal". |
| T4 | **Item (F) reason 3 — "exclusion governs the walk, never the predicate" — was unlocked.** | Added `test_mv_cross_dated_refusal_ignores_exclusion`: with `[exclude] globs = ["archive/**"]` hiding the moving document from the walk entirely (verified genuinely excluding — `docs list` shows only `active.md`), the refusal still fires with both frozen lines and zero bytes. A predicate evaluated against walked entries, or inside `preflight_move_plan` which only ever sees walked documents, would let an excluded archived document be silently re-dated — the hole M28a exists to close, reachable by adding one line to `.docs.toml`. |
| T5 | `test_exit_code_for_archive_date_drift_is_2` was a **tautology**: it hand-built a `Finding(..., "error", ...)` and asserted `exit_code_for` returned 2, but `exit_code_for` keys on `severity` and never on `rule`, so it tested `exit_code_for` rather than M28a. Conductor's call: give it a real assertion or remove it. | **Given a real assertion.** It now takes all three findings from `archive_date_findings` itself — both drift forms and the `bad-date` form — and asserts each carries `severity: error` and drives exit 2, individually and together. An implementation emitting `severity="warning"` (the one plausible way to get this wrong, and the shape M27 — Q6 declined for an objective rule) now fails here. **Consequence recorded rather than hidden:** the test is no longer GREEN-at-baseline — at `7f7853b` it would raise the same `AttributeError` as the rest of the pure-seam group — so its GREEN-at-baseline census row is annotated, and the Phase-4 counts stand as the measurement taken at that commit. |

### T1 re-proved by mutation, on a throwaway copy

The reviewer's 19/19 kill result was pinned to `3743035`, and T1 changes
`_attic_tree` — the very fixture whose `[archive] dir` axis mutation **(e)**
had shown was *not* load-bearing. A fix to a fixture that a mutation proved
inert has to be re-measured, or it may have moved the hole rather than closed
it. Both relevant mutations were therefore re-run against the amended tree, on
a `tar`-piped throwaway copy under `/tmp` with the real repository untouched:

| Mutation | Applied to | Result |
|---|---|---|
| **(e)** hardcode the archive directory — `rel == "archive" or rel.startswith("archive/")` instead of consulting `config.archive_dir` | `_is_archived_rel` | **KILLED — 6 genuine failures**, and critically **`test_mv_does_not_refuse_inside_an_ordinary_archive_named_subdirectory` is now one of them**. That is the proof asked for: before the rename it survived this mutation; after it, it does not. The hole is closed, not moved. The other five are `test_archived_test_honours_the_configured_archive_dir`, the two `..._honours_a_non_default_archive_dir` unit locks, `test_archive_date_findings_message_names_the_configured_archive_dir`, and `test_mv_refuses_a_cross_dated_relocation_on_a_non_default_archive_tree`. |
| **(g)** hardcode `"%Y-%m-%d"` instead of consulting `config.date_format` | `archive_dir_date` | **KILLED — 4 genuine failures**: the two `..._honours_a_non_default_date_format` unit locks, `test_archive_date_findings_parses_both_sides_in_the_tree_format`, and `test_mv_refuses_a_cross_dated_relocation_on_a_non_default_archive_tree`. |

Under (g) the renamed test correctly **passes**, and that is not a gap: with
ISO hardcoded, `archive/01-01-2026/` parses on neither end, `archive_dir_date`
returns `None` for both, and the move completes — which is the behaviour the
test asserts. The rename makes that test load-bearing on the **directory**
axis specifically, which is exactly what its docstring now claims; the
`date_format` axis is killed four other ways.

One unrelated failure appears in both runs and in the un-mutated control:
`test_packaging.py::test_d6_install_skill_rejects_symlink_on_wheel_install`,
which resolves a symlink against the source tree's real path and therefore
cannot pass from a copy. Confirmed as a copy artifact by running it against
the un-mutated copy before applying either mutation.

### Recorded, no action (T3, T6)

- **T3 — an end-to-end coverage gap that cannot be closed until E8 is fixed.**
  There is no subprocess-level `docs check` on a tree with a non-default
  `[archive] dir`, and the `date_format` axis **genuinely cannot** be
  exercised end-to-end, because pre-existing defect E8 makes `docs archive`
  exit 2 on the INDEX refresh for any non-default-`date_format` tree.
  Both axes are covered at the pure seam instead — `archive_dir_date`,
  `cross_dated_archive_move` and `archive_date_findings` each have
  non-default-config locks in both polarities, and `docs mv` has two
  subprocess locks on an `attic` / `%d-%m-%Y` tree. **This is registered
  against *Follow-ups* item 1**: the milestone that fixes E8 should add the
  end-to-end `docs check` coverage that becomes possible at the same time, in
  the same change that updates
  `test_archive_renders_the_witness_in_the_trees_date_format`.
- **T6 — a theoretical hole in `_snapshot`.** It compares files only, so it
  would not notice an empty destination *directory* left behind by a refusal.
  It cannot fire for M28a: `_cmd_mv` refuses before any `mkdir`, and the
  destination directory is created only in the execution phase, well past the
  return. Recorded so a later change that moves the refusal downward knows the
  guarantee is not actually snapshot-enforced.

### Verification after the fold-in

| Gate | Result |
|---|---|
| `pytest -q` | **1504 passed / 0 failed** — 1502 plus the two new locks (T4's exclusion lock and F2's `--help` surface-parity lock). T1, T2 and T5 strengthened existing ids without adding any |
| `ruff check .` / `ruff format --check .` / `mypy src/ tests/` | clean |
| `docs check --root docs` | no violations (exit 0) |
| both skill mirrors | byte-identical (`cli.md` changed for F1 and F4, re-copied in the same commit) |
| ids vs `7f7853b` | 1341 → **1504**; **0 removed**, 163 added |
| `git diff 7f7853b --numstat -- tests/` | **0 deleted lines in every test SOURCE file**; the only deletions are 10 lines in the frozen INDEX snapshot, every one an `Updated:` value or the generated-on line |
| worktrees | `git worktree list` shows the repository alone; `.git/worktrees` is gone |

**No test was relaxed** by this fold-in. Three were **strengthened** (T1 made
its fixture mean what its docstring says, T2 replaced containment with
equality, T5 replaced a tautology with the real producer), two were **added**,
and none was weakened, deleted or rewritten to pass.

## Second `/simplify` pass — 2026-08-16

Run on `m28a/simplify` over the whole M28a surface after the same-instance
audit and the fresh-eyes fold-in, mirroring M28's second pass. **Outcome: no
changes.** The code is already minimal, and that verdict is measured rather
than asserted.

**Why M28's second pass found three collapses and this one finds none.** M28's
was justified by a real gap — "the surface Phase 10's `/simplify` last saw is
not the surface that shipped", because the audit and the fold-in had reshaped
`cli.py` afterwards. That gap does not exist here. `git diff e099f55..HEAD --
src/docs_cli/cli.py` is **twelve changed lines (+8 / −4), all of them prose
inside two argparse `description=` strings** (F2's archive-help extension and
the form-B overclaim fix). Not one executable line of M28a moved after Phase 10's pass, so its
analysis is still current and its four recorded rejections still hold — each
was re-examined against the shipped code and none has changed.

**Two mechanical sweeps, to avoid resting on the prior pass's word.**

- A duplicate-block scan over **all 3,209 added lines** (`src/` + `tests/`,
  6-line window) found exactly **one** repeated block in the whole milestone:
  the three purity locks' `mp.setattr(Path, …)` scaffolding. Nothing else in
  M28a repeats anywhere.
- An extended lint sweep the project does not run — `ruff --isolated --select
  C90,RET,PLR,SIM,C4,PERF,FURB,RUF` — produced exactly **one** finding inside
  M28a's line ranges: `PLR2004` on `len(parts) < 3`. (The `check_doc`
  findings it also reports are pre-existing; M28a added one line to that
  function.) `SIM` is already in the project's enabled set and is clean, which
  independently rules out the nested-`if`, redundant-boolean and
  `if`/`else`-return collapses.

### Candidates evaluated and REJECTED

| Candidate | Rejected because |
|---|---|
| Collapse the three purity locks in `tests/test_check.py` into one `_no_filesystem(...)` context manager — the milestone's only duplicated block | The inline spelling is the idiom every purity lock in the suite already uses — `test_body_links.py` (M27) and `test_move_links.py` (M28) each spell their own `_boom` — and the door lists deliberately **differ** per lock: M27's normalise lock guards `exists`/`is_file`/`resolve`, M28's planner lock adds `read_text`, M28a's adds `is_dir`/`open`. A shared helper would either freeze one list for locks it does not own or take the list as a parameter, at which point it saves nothing. A module-local abstraction contradicting both sibling modules costs a reader more than the ~10 lines it saves, and the sentinel list is precisely what a purity test exists to make visible. |
| Name the `3` in `archive_dir_date`'s `len(parts) < 3` (the lone `PLR2004`) | A constant **adds** a concept rather than removing one. Step 2 of the docstring already says exactly what the 3 means — "there is a segment after it… what makes `archive/x.md` carry no date" — and item (C) step 2 freezes the literal `len(parts) < 3` as the contract. |
| Pass `check_doc`'s already-computed `rel` into `archive_date_findings` instead of it calling `_root_relative` | Three independent blocks. It changes the item-(H) **frozen** signature; `check_doc`'s `rel` comes from `path.resolve().relative_to(root.resolve())`, the expression **OQ-4 binds the rule away from**; and `check_doc` computes it only inside the `if lifecycle` branch, so the rule would inherit a conditional. It is also a behaviour change on synthetic and symlinked paths — the two expressions agree only for a real `os.walk`. |
| Rewrite `_cmd_mv`'s refusal guard with a walrus — `if (crossed := cross_dated_archive_move(...)) is not None:` | `cli.py` contains **zero** walrus operators across 8,985 lines, while the plain `is not None` guard appears at **32** sites. It saves one line at the cost of introducing the file's only instance of a second idiom. |
| Trim the banner above the three helpers, which restates the purity property and the shared-`_is_archived_rel` reason that both reappear in the docstrings below it | The banner's shared-notion sentence is a deliberate **output** of Phase 10's pass — this log records that it "now records the positive reason (the shared notion) instead of excusing the layout". Cutting it would reverse that decision, not simplify past it. |

Phase 10's own four rejections — widening `archive_dir_date`'s return type,
merging the two frozen message forms, extracting `_cmd_mv`'s refusal into a
helper, and folding `len(parts) < 3` into the `_is_archived_rel` guard — were
re-read against the shipped code and all four still hold for the reasons
recorded above.

### Verification

| Gate | Result |
|---|---|
| `pytest -q` | **1504 passed / 0 failed**, before and after (no code changed) |
| `ruff check .` / `ruff format --check .` / `mypy src/ tests/` | clean |
| `docs check --root docs` | no violations (exit 0) |
| both skill mirrors | byte-identical |
| `git diff` over `src/` and `tests/` | **empty** — the pass is analysis, and the log entry is its only artifact |

## Milestone completion summary

**M28a — Structured archive-date witness is implementation-complete across all
ten TDD phases, same-instance audited, independently fresh-eyes reviewed and
re-simplified** (Step 1 — Phases 1–4 — on `m28a/phases-1-4`, 2026-08-15/16;
Step 2 — Phases 5–10 — on `m28a/phases-5-10`, 2026-08-16). The suite is
**1504 passed / 0 failed**, every quality gate is clean, and
`docs check --root docs` exits 0.

**What shipped, in three touch points.** One `set_metadata_field` call in
`_archive_one` writes `Archived: <date_str>` — the same date that names the
dated archive directory — to **every** document an archive operation moves,
at the pinned block position, while `Archived-reason:` stays primary-only. One
`findings.extend` in `check_doc` reports a document whose location does not
corroborate its own recorded date as `archive-date-drift`: a hard error, exit
2, one finding per document, on the unchanged four-key `Finding` record. One
refusal in `_cmd_mv` blocks a move between two different dated archive
directories at exit 2 with zero bytes written, in every mode. Behind them sit
three pure helpers with no filesystem access of any kind, and the two legs
share `archive_dir_date`, so they can never disagree about what a dated
archive directory is.

**The compatibility story is the design, not a mitigation.** The rule fires
only when the field is present, so a 1.x tree gains **zero** findings on
upgrade — measured on this repository's own 46 pre-witness archived documents,
which stay silent at exit 0. There is no backfill and no sweep, because no
honest source exists for a date the tool never observed. The milestone's one
behaviour change is the `docs mv` refusal, and its by-hand escape ships in the
same breath as the refusal, in the CLI and in both specs.

**What it closes.** `feedback-log.md` issue #1 — finding 3's archive-date half
was its last open item — with the reporter's own suggested `pairs-with` rule
still declined and now measured at **7 findings on a correct tree**. And it
closes the gap M28 opened: the same relocation left 13 `broken-body-link`
errors at exit 2 under pre-M28 `main` and zero findings at exit 0 after, so
without M28a the 2.0.0 release would have been strictly quieter about
archived-document relocation than 1.8.0 was.

**Deliberately not done, and recorded.** Defect E8 (`parse()`'s hardcoded ISO
`Updated:` parse) is untouched — *Follow-ups* item 1 owns it and names the
test that must change with it. D8's second residual — a tool-driven relocation
*out of* a dated directory that is not cross-dated — stays a permitted
neighbour by operator decision (OQ-7), is pinned by a KNOWN-GAP test, and is
*Follow-ups* item 7. No version bump: the package stays `1.8.0` and **M29**
performs the single bump to `2.0.0`.

M28a stays `Lifecycle: active` and is handed to M29.
