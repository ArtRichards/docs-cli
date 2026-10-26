# M30 — Lifecycle verb and free-form `docs relate`

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-10-26

Related:
- child-of: milestone-plan.md
- implements: charter.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: test-strategy.md
- pairs-with: status.md
- references: feedback-log.md

## Overview

- Milestone: M30 (first post-2.0 milestone; first under the canonical tracker)
- Slug: `lifecycle-and-free-form-relate` — tracker identity and branch root
  (`lifecycle-and-free-form-relate/milestone-setup`, …)
- Title: Lifecycle verb and free-form `docs relate`
- Surface: a new `docs lifecycle` verb for top-level lifecycle transitions,
  and `docs relate add|remove` widened to free-form verbs, written one-sided.
- Progress: **Registered draft (2026-10-26).** No implementation log or TDD
  phase has started.

### Goal

Every metadata edit a suite workflow prescribes has a verb, so an agent holding
the bundled `docs` skill never meets a step it can complete only by
hand-editing a metadata block or asking the operator for an exception.

### Primary use-case acceptance

An agent running `create-milestones` against a downstream tree scaffolds a
milestone with `docs new`, links its impl log and test matrix with
`docs relate add <milestone> pairs-with <companion>`, promotes it with
`docs lifecycle <milestone> active`, and passes `docs check`. It never
hand-edits the metadata block and never stops to ask the operator.

## Binding scope

- `docs lifecycle FILE STATE` sets `Lifecycle:` to any **top-level** state
  (`draft`, `active`, `blocked`, `done`, `superseded`, plus any
  `add_lifecycles` extension), bumps `Updated:`, and reindexes once.
- It refuses `archived` as a target and refuses a document under the archive
  subtree as a source: `docs archive` keeps sole ownership of lifecycle and
  location moving together.
- Idempotent: a document already in STATE writes zero bytes, bumps no
  `Updated:`, and does not reindex (the `docs relate` precedent).
- `--root`, `--dry-run`, `--json`, `--quiet` behave as on the other mutating
  verbs.
- `docs relate add|remove SOURCE VERB TARGET` accepts any free-form verb
  (anything other than the six recognized reciprocal verbs) and writes
  **SOURCE's bullet only**, with no inverse obligation. Recognized verbs keep
  M25 — D3's two-endpoint behaviour byte-for-byte.
- Free-form edges stay outside reciprocal validation; `child-of` /
  `parent-of` remain deliberately unvalidated (`convention.md`).
- CLI help, `cli.md`, `convention.md`, the bundled `docs` skill and its
  references, and CHANGELOG describe the same surface (surface-parity gate).
  The bundled skill's *Three things never to hand-edit* names the two new
  verbs as the route for lifecycle and free-form `Related:` edits.

## Current state and risks

- 2.0.0 has no verb that writes a non-archived `Lifecycle:` and none that
  writes a free-form `Related:` bullet (feedback-log 2026-10-26, findings 1–2).
- `create-milestones` rule 3 sanctioned exactly those two hand-edits while the
  bundled skill forbade them. The stopgap (operator decision 2026-10-26) drops
  the suite's carve-outs in favour of an operator ask; M30 removes the need
  for the ask.
- `pairs-with` / `child-of` feed the archive cascade candidate set (M26 — D1)
  and M28's leg-1 `child-of` strand refusal. Making them easier to write must
  not change either; tests must pin that.
- Widening `relate` to free-form verbs touches M25 — D4's audited
  archived-endpoint exception, which today names only the recognized bullet.

## Deliverables

- [ ] Flag/exit/message matrix for `docs lifecycle` and free-form `relate`
      frozen in Phase 1.
- [ ] `docs lifecycle` with refusal, idempotence and reindex tests.
- [ ] One-sided free-form `relate add|remove` with recognized-verb
      regression coverage.
- [ ] Cascade-candidate and strand-check regression locks.
- [ ] Surface parity: argparse help, `cli.md`, `convention.md`, bundled
      skill + byte-identical references, CHANGELOG.
- [ ] Dogfood the primary use case on a throwaway copy of this tree.
- [ ] Hand-off note for the publish milestone: its closeout sweep must
      retire the Agent Playbook Suite verbless-metadata stopgap (below).

## TDD plan summary

1. Define the contract: verb shape, state vocabulary, refusals, idempotence,
   archived-endpoint policy for free-form edges, JSON record.
2. Write RED CLI/integration tests.
3. Create fixtures (extension lifecycles, archived endpoints, free-form verbs).
4. Capture the RED baseline.
5. Extend the `relate` plan interface for one-sided operations.
6. Implement `docs lifecycle` and free-form `relate`.
7. Reconcile argparse, docs, bundled skill, CHANGELOG, feedback log.
8. Run the focused and full GREEN gates.
9. Dogfood the use case on a throwaway tree.
10. Simplify, close docs, hand off to the publish milestone.

## Decisions carried from discovery

- Lifecycle gets a verb, not a second sanctioned hand-edit exception
  (operator, 2026-10-26).
- Free-form edges are written one-sided by `docs relate`; no new symmetric
  pair, so `missing-inverse` reports nothing new on any existing tree
  (operator, 2026-10-26).
- Stopgap: the Agent Playbook Suite drops its hand-edit carve-outs and asks
  the operator until this ships (operator, 2026-10-26).

## Open questions for M30 Phase 1

1. Verb shape: `docs lifecycle FILE... STATE` vs `docs lifecycle set FILE
   STATE`. Recommendation: flat verb accepting one or more files, like
   `docs touch`; no subcommand until a second lifecycle operation exists.
2. Free-form edge whose SOURCE is archived. Recommendation: refuse, keeping
   M25 — D4 limited to recognized bullets; an archived TARGET is fine because
   it is never written.
3. Free-form verb syntax. Recommendation: accept exactly the token grammar
   `docs check` already parses for `Related:` bullets, and refuse anything
   `docs check` would reject.
4. Release vehicle. Recommendation: additive, so **2.1.0** through a separate
   publish milestone (the M19 → M20 pattern), at which point host skills and
   the suite prescriptions are refreshed per CLAUDE.md.

## Success criteria

- The primary use case completes with zero hand-edits and zero operator asks.
- No transition into or out of `archived` is possible through `docs lifecycle`.
- Recognized-verb `relate` behaviour and the archive cascade set are
  byte-for-byte unchanged.
- Full quality, compatibility, and dogfood gates are GREEN.
- **The suite stopgap is retired in the suite release that pins the docs-cli
  version carrying M30** — not at M30's merge or at the PyPI publish alone,
  because downstream projects follow the suite's pin and keep the 2.0 surface
  until it moves. That one suite PR bumps `DOCS_CLI_VERSION`, replaces every
  operator-approved hand-edit prescription with `docs lifecycle` / free-form
  `docs relate`, deletes `_shared/references/verbless-metadata-edits.md`, and
  drops ship-milestone Step 0's up-front approval. The suite CI guard
  *Validate verbless-metadata stopgap matches the pinned docs-cli* enforces
  it: it fails while the stopgap still covers an edit the pinned binary can
  perform. If Phase 1 descopes either verb, only that half of the stopgap
  retires.
