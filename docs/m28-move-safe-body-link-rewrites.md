# M28 — Move-safe Markdown body-link rewrites

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-08-15

Related:
- child-of: plan.md
- implements: charter.md
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
- Surface: extend `docs mv` and `docs archive` to rebase only parsed local
  Markdown destination tokens affected by a coordinated move. M27 supplies the
  validated scanner; M28 supplies mutation and move integration.
- Progress: **Registered draft (2026-08-10).** Depends on M26 and M27. No
  implementation log or TDD phase has started.

### Goal

Moving or archiving documents should preserve every supported local Markdown
link automatically, without changing labels, titles, fragments, unrelated
prose, examples, or code.

### Primary use-case acceptance

An agent renames or archives a document and commits the resulting focused diff.
Incoming links now point to the moved target, and links inside any moved source
are rebased from its new directory. A final `docs check` proves both metadata
relationships and body navigation remain intact.

## Binding scope

- Reuse M27's scanner and spans; no second Markdown parser.
- Handle two independent move classes:
  1. incoming links whose target moves; and
  2. local links inside a referring document that itself moves and therefore
     need rebasing even when their target does not move.
- For a batch, resolve each destination from the referrer's old location, map
  its target through the old→new move set when applicable, then relativize from
  the referrer's new location.
- Preserve link labels, optional titles, quoting/angle form, fragments, and
  unrelated bytes. Do not rewrite plain text or code.
- Validate every planned rewrite and destination before mutation; integrate
  with M26's deduplicated archive operation plan and refresh INDEX once.
- Define the narrow audited exception, if any, for move-driven destination
  rewrites in archived referrers; do not create a general archive editor.
- **Post-plan strand-check** (added 2026-08-15 from `feedback-log.md` issue #1,
  finding 1). Over the complete, already-computed plan, refuse the operation if
  applying it would leave a still-active document pointing at a newly-archived
  one — through a `Related:` edge or a body link — and name both ends in the
  refusal. Rationale: M26 made archive selection *authorized* (an explicit
  `--cascade-only` scope is required) but a glob is a syntactic filter that
  cannot know what it selects, so `--cascade-only '*'` still archives a live
  `milestone-plan.md` reached through the target's outgoing `child-of` edge.
  Validating the plan's *consequences* is direction-agnostic — it closes the
  `child-of` route, the symmetric `pairs-with` route, and the body-link route
  together — and it self-cancels for legitimate whole-set archiving, because a
  set archived together strands nothing. It does not re-open M26 — Q3: the
  candidate set stays exactly as frozen; the new invariant makes its direction
  moot. This belongs to M28 because M28 already builds the inbound-reference
  graph it needs.

## Current state and risks

- `rewrite_related_refs` cannot be reused for path math: `Related:` targets are
  root-relative, while Markdown destinations are source-document-relative.
- `_cmd_mv` and `_cmd_archive` currently repair metadata edges only.
- Historical dangling links demonstrate that class (2)—rebasing links inside a
  moved doc—is as important as incoming-target rewrites.
- Multi-document archive and cross-file write failures require a precomputed
  plan; partial body rewrites would be worse than a clean refusal.

## Deliverables

- [ ] Pure old-referrer/old-target/move-map/new-referrer rewrite planner.
- [ ] Minimal destination-token editor preserving every unrelated byte.
- [ ] `mv` and archive integration for single and batch moves.
- [ ] Archived-referrer policy and audit implementation.
- [ ] Failure-injection, nested-path, fragment/title, and no-op regression tests.
- [ ] End-to-end dogfood proving zero dangling supported links after moves.

## TDD plan summary

1. Freeze rebasing/path/audit/atomicity contracts.
2. Write RED planner/editor/mv/archive tests.
3. Create nested single/batch/archive fixtures.
4. Capture the RED baseline.
5. Add move-map and body-rewrite plan interfaces.
6. Implement pure path planning and token edits.
7. Wire `mv`/archive, output, docs, bundled skill, and CHANGELOG.
8. Run focused/full GREEN gates.
9. Dogfood representative rename/archive batches on a throwaway live tree.
10. Simplify, close docs, and hand the complete implementation train to M29.

## Open questions for M28 Phase 1

1. Archived referrers. Recommendation: permit only move-driven destination
   token changes, bump `Updated:`, and append a generated `Revision:` audit
   reason that names the move; preserve all other prose/metadata.
2. Absolute root paths and links escaping the docs root. Recommendation: local
   absolute filesystem paths remain out of scope/error; `../` is supported only
   when the resolved file remains within the managed root.
3. Same-path textual normalization. Recommendation: if the computed semantic
   destination is unchanged, preserve original spelling byte-for-byte.

## Success criteria

- Both incoming-target and moved-referrer classes stay valid across nested
  single/batch moves.
- Only destination tokens and required archive audit metadata change.
- Handled validation/write failures leave no deliberate half-rewrite.
- `docs mv` and explicit scoped archive end with `docs check` clean and one
  deterministic INDEX refresh.
- Full quality and dogfood gates are GREEN.
