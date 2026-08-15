# M28a — Structured archive-date witness

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-08-15

Related:
- child-of: plan.md
- implements: charter.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: status.md
- references: feedback-log.md
- follows: m28-move-safe-body-link-rewrites.md
- precedes: m29-pypi-publish-2-0-0.md
- depends-on: m26-safe-archive-selection.md
- required-by: m29-pypi-publish-2-0-0.md

## Overview

- Milestone: M28a (v2.0 train)
- Title: Structured archive-date witness
- Surface: `docs archive` records the archive date as a structured metadata
  field; `docs check` gains a rule that reports a document whose recorded
  archive date disagrees with its dated archive directory.
- Progress: **Registered draft (2026-08-15).** Promoted from `feedback-log.md`
  issue #1, finding 3. Depends on M26. No implementation log or TDD phase has
  started.

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

A document archived on one date and later relocated into a different dated
archive directory — by a manual `git mv`, a `docs migrate` run, or any future
defect — is reported by `docs check` as a hard error naming both dates. A
document archived normally is silent.

## Binding scope

- `docs archive` writes a structured archive-date field (working name
  `Archived:`) alongside the existing `Archived-reason:` at archive time.
- `docs check` gains a rule (working name `archive-date-drift`) comparing that
  field against the containing `archive/<date>/` directory. Hard error,
  exit 2, one finding per document, closed JSON key set — the `status-drift`
  and `broken-body-link` shape.
- The rule fires **only when the field is present**, so every pre-2.0 archived
  document stays silent rather than failing on upgrade. This is the whole
  compatibility story and it is not negotiable.
- Per-document check only. No graph traversal, no comparison against a
  document's `pairs-with` partners.

## Out of scope

- Reconstructing true archive dates for documents archived before this
  milestone. The witness never existed for them; git history is the operator's
  recourse, not the tool's.
- Reporting `pairs-with` partners that sit in different dated archive
  directories. That was issue #1's literal request and it is **declined**: two
  documents archived months apart may legitimately carry an edge, so the rule
  would fire on correct trees. It fails the charter's *never cry wolf*
  criterion, and the drift it was reaching for is what the witness detects
  directly.

## Current state and risks

- The dated archive directory is the *only* record of when a document was
  archived. `Archived-reason:` is free text and `Updated:` is bumped by the
  move itself, so once a document is relocated no independent witness survives.
  This is precisely why `docs check` exited 0 on issue #1's reproduction.
- Adding a built-in label touches the metadata vocabulary, the `unknown-field`
  rule, `docs migrate`, and the bundled skill's convention mirror — a small
  change with a wide blast radius. The contract freeze should enumerate every
  surface before any code.
- M26 already prevents the tool from relocating archived documents
  (`already-archived` ineligibility), so this milestone is defence in depth
  against paths the convention forbids but nothing currently detects.

## Deliverables

- [ ] Structured archive-date field written by `docs archive`, with its
      vocabulary, ordering, and format pinned against the tree's `date_format`.
- [ ] The `archive-date-drift` check rule, present-only, with its frozen
      message and closed JSON record.
- [ ] `docs migrate` behaviour for foreign trees that carry a dated archive
      layout but no field.
- [ ] Fixture trees for the drifted, the clean, and the field-absent cases.
- [ ] Convention and CLI spec updates, byte-mirrored into the bundled skill.

## TDD plan summary

1. Freeze the field name, format, ordering, the rule, its message, and the
   present-only compatibility contract.
2. Write the RED suite across the writer, the rule, and the CLI surface.
3. Create the drifted / clean / field-absent fixture trees.
4. Capture the classified RED baseline.
5. Add the vocabulary and the writer interface.
6. Implement the writer and the check rule.
7. Wire `migrate`, the argparse surface, the bundled skill, and CHANGELOG.
8. Run the GREEN gates with the no-regression proof.
9. Dogfood against a throwaway copy carrying real archived sets.
10. Simplify, close the specs, and hand to M29.

## Open questions for M28a Phase 1

1. Field name. Recommendation: `Archived:`, beside the existing
   `Archived-reason:`, so the pair reads as one archive record.
2. Whether the field's value must equal the directory date exactly, or may
   record a true archive date that predates the directory (the legacy-repair
   case). Recommendation: exact equality — anything looser reintroduces the
   ambiguity the witness exists to remove.
3. Whether `docs archive` backfills the field on documents it re-reads.
   Recommendation: no. Backfill is a migration concern, and inventing a date
   for a document whose true date is unknown is the falsification this
   milestone exists to prevent.

## Success criteria

- A relocated archived document is a hard `docs check` error naming both the
  recorded and the directory date.
- A normally archived document, and every pre-2.0 archived document lacking the
  field, are silent.
- The live tree and every fixture tree pass unchanged apart from the
  deliberately drifted fixture.
- Full quality gates GREEN; specs and bundled mirror byte-identical.
