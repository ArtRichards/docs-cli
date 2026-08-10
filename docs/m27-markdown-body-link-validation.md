# M27 — Markdown body-link validation

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
- follows: m26-safe-archive-selection.md
- precedes: m28-move-safe-body-link-rewrites.md
- required-by: m28-move-safe-body-link-rewrites.md
- required-by: m29-pypi-publish-2-0-0.md

## Overview

- Milestone: M27 (v2.0 train)
- Title: Markdown body-link validation
- Surface: parse a deliberately bounded set of real local Markdown body links
  and make a missing destination a hard `docs check` error. This milestone
  detects damage and establishes the shared scanner; M28 owns mutation.
- Progress: **Registered draft (2026-08-10).** Follows M26. No implementation
  log or TDD phase has started.

### Goal

Let an agent trust `docs check` to catch both broken metadata relationships and
broken local navigation in prose, without flagging examples, code, external
URLs, or plain-text mentions.

### Primary use-case acceptance

After a manual edit or an upgrade, an agent runs `docs check` and receives an
exact source location and destination for each real local Markdown link whose
file is missing. Valid links with fragments pass without validating the
heading; external links and code examples are ignored.

## Binding scope

- Add a reusable stdlib-only Markdown link scanner with source spans and
  destination components.
- Resolve local destinations relative to the referring document, not the docs
  root (unlike `Related:`).
- Ignore external/schemed URLs, fragment-only links, images, raw HTML, plain
  text, fenced code, and inline code in the first version.
- Preserve fragments conceptually but do not validate heading existence.
- Emit a hard, machine-readable `docs check` finding for a missing local file.
- Keep validation read-only. `docs mv`/`archive` rewriting is M28.
- Provide a deliberate v2.0 upgrade path for pre-existing broken links,
  including the archived-doc policy; do not silently grandfather unknown
  damage without documenting the boundary.

## Current state and risks

- `check_doc` validates only metadata and `Related:` targets; the body is
  otherwise opaque.
- A conservative scan of the live tree found roughly 139 unresolved local-link
  occurrences across 29 docs, mostly archived historical milestones whose
  relative links were not rebased when the documents moved.
- The convention currently treats archived prose as immutable except for the
  narrow M18 move-driven `Related:` rewrite. Enabling a hard body-link rule
  requires an explicit one-time repair/audit decision or a principled
  exemption; ordinary cleanup is not authorized by current policy.
- A regex-only implementation is likely to rewrite code or mis-handle titles
  and escapes. The scanner needs a pinned, deliberately limited grammar.

## Deliverables

- [ ] Supported Markdown forms and resolution rules frozen in Phase 1.
- [ ] Pure scanner with exact source spans and code masking.
- [ ] Hard human/JSON finding with line/location and destination.
- [ ] Unit/fixture/subprocess coverage for supported and excluded forms.
- [ ] Controlled legacy-tree repair or explicit compatibility policy.
- [ ] Live-tree dogfood clean with documented migration evidence.

## TDD plan summary

1. Define grammar, path normalization, finding rule/schema, and archive-upgrade
   policy.
2. Write RED scanner and check tests, plus GREEN exclusion locks.
3. Create syntactic and realistic legacy fixtures.
4. Capture the RED baseline and live-tree inventory.
5. Add scanner/link model interfaces.
6. Implement scanning, resolution, and check integration.
7. Wire human/JSON docs, bundled references, and upgrade messaging.
8. Run focused/full GREEN gates.
9. Repair or migrate the live legacy set under the Phase-1 policy and dogfood.
10. Simplify, document the scanner contract, and hand off to M28.

## Open questions for M27 Phase 1

1. Initial syntax set. Recommendation: inline destinations and reference
   definition destinations, including angle-bracket destinations and optional
   titles; exclude images/autolinks/raw HTML/code.
2. Escapes, whitespace, nested parentheses, and URL encoding. Pin the exact
   CommonMark-shaped subset rather than implying full Markdown conformance.
3. Finding rule id and location schema. Recommendation: a distinct
   `broken-body-link` error with root-relative source path, 1-based line, raw
   destination, and resolved candidate.
4. Existing archived damage. Recommendation: a controlled one-time
   destination-token-only repair with `Updated:`/`Revision:` audit, rather than
   weakening the hard invariant or silently editing historical prose.

## Success criteria

- Supported local links resolve correctly from root and nested documents.
- Missing files make `docs check` exit 2 with stable human and JSON detail.
- Code, examples, external URLs, images, raw HTML, and fragment-only links do
  not produce false positives.
- The live tree has a documented, auditable path to a clean result.
- The scanner is reusable by M28 without duplicating parsing logic.
