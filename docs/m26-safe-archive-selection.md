# M26 — Safe explicit archive selection

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-08-10

Related:
- child-of: plan.md
- implements: charter.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: test-strategy.md
- pairs-with: status.md
- references: feedback-log.md
- follows: m25-reciprocal-relationship-integrity.md
- precedes: m27-markdown-body-link-validation.md
- required-by: m28-move-safe-body-link-rewrites.md
- required-by: m29-pypi-publish-2-0-0.md

## Overview

- Milestone: M26 (v2.0 train)
- Title: Safe explicit archive selection
- Surface: decouple relationship context from archive authorization. A named
  archive with no cascade option moves only the named document; preview remains
  available; every multi-document write requires an explicit
  `--cascade-only GLOB` scope.
- Progress: **Registered draft (2026-08-10).** M25 runs first. No
  implementation log or TDD phase has started.

### Goal

Make it impossible for an agent to archive a useful neighborhood merely
because the documents are related. Previewing candidates should be effortless,
but a write must state the exact bounded selection the operator intends.

### Primary use-case acceptance

An agent preparing to archive a completed milestone previews the one-hop
candidates, sees upcoming/paused/context documents without moving them, then
archives only the named milestone artifacts through an explicit path scope.
A typo or obsolete unscoped command fails loudly before any document moves.

## Binding scope

- Bare `docs archive FILE --cascade` does not write and fails with safe-flow
  guidance.
- `docs archive FILE` archives only `FILE`.
- `--cascade-dry-run` previews the candidate set and writes nothing.
- A write that includes related documents requires explicit
  `--cascade-only GLOB` selection.
- Relationship verbs remain context; none grants archive authorization.
- Candidate planning is validate-all-first, deduplicated, collision-checked,
  and all-or-nothing for handled errors before mutation begins.
- CLI help, `cli.md`, `convention.md`, the bundled docs skill and references,
  CHANGELOG, and upgrade notes describe the same safe flow. Agent Playbook
  Suite workflow changes remain a post-M29 cross-repository follow-up.

## Current state and risks

- v1.8.0 bare `--cascade` is non-interactive and writes every one-hop
  `pairs-with`/`child-of` candidate.
- `--interactive` is another unscoped multi-document write path and therefore
  conflicts with the confirmed “explicit `--cascade-only` for every related
  write” invariant unless deliberately redesigned or retired.
- The current scoped loop can partially archive on a later candidate failure
  and does not deduplicate a document reached through multiple edges.
- M18 fixes moved-edge integrity but does not make candidate selection safe.

## Deliverables

- [ ] Exact flag/exit/message compatibility matrix frozen in Phase 1.
- [ ] Bare cascade and any unscoped related-write path refuse before writes.
- [ ] Deterministic preview and explicit-scope planning output.
- [ ] Deduplicated, preflighted scoped archive batch with failure tests.
- [ ] Regression coverage for primary-only archive and edge rewriting.
- [ ] Surface-parity and v2.0 migration guidance.

## TDD plan summary

1. Define the compatibility matrix, candidate semantics, no-match behavior,
   atomicity boundary, and `--interactive` disposition.
2. Write RED CLI/integration/failure-injection tests.
3. Create candidate/dedup/collision fixtures.
4. Capture the RED baseline.
5. Add an immutable archive-operation plan interface.
6. Implement validation/deduplication and safe refusal/write behavior.
7. Reconcile argparse, output, docs, skill, version, and CHANGELOG.
8. Run the focused and full GREEN gates.
9. Dogfood preview + explicit selection on a throwaway copy of this tree.
10. Simplify, close docs, and hand off to M27.

## Decisions carried from discovery

- Relationships provide context, never archive permission.
- Bare cascade must not write.
- Preview remains supported.
- Explicit `--cascade-only` scope is required for a related-document write.

## Open questions for M26 Phase 1

1. Retire `--interactive` or require it to compose with an explicit scope.
   Recommendation: retire/refuse it with migration guidance; the explicit
   non-interactive operation is clearer for both humans and agents.
2. Candidate verb set. Recommendation: retain the current one-hop
   `pairs-with`/`child-of` discovery set for compatibility; the scope, not the
   relationship, grants authorization. New M25 sequence/dependency/blocker
   verbs never become cascade candidates.
3. No-match behavior. Recommendation: if candidates exist but the explicit
   GLOB matches none, fail before archiving the primary so a typo cannot look
   successful; pin the empty-candidate case separately.
4. Exact handled-failure atomicity. Recommendation: build and validate the full
   move/edit plan before the first write and test collisions/duplicates/OSError
   boundaries explicitly.

## Success criteria

- No unscoped flag can archive a related document.
- Preview and scoped output name the deterministic candidate/selected sets.
- An invalid or empty accidental scope causes no mutation.
- A valid explicit scope archives exactly the intended documents, keeps all
  relationships resolvable, refreshes INDEX once, and passes `docs check`.
- Full quality, compatibility, and dogfood gates are GREEN.
