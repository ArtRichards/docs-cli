# M25 — Reciprocal relationship integrity and docs relate

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-08-10

Related:
- child-of: plan.md
- parent-of: m25-reciprocal-relationship-integrity-impl.md
- implements: charter.md
- pairs-with: m25-reciprocal-relationship-integrity-impl.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: test-strategy.md
- pairs-with: status.md
- references: feedback-log.md
- precedes: m26-safe-archive-selection.md
- required-by: m29-pypi-publish-2-0-0.md

## Overview

- Milestone: M25 (v2.0 train)
- Title: Reciprocal relationship integrity and `docs relate`
- Surface: define three useful reciprocal relationship pairs, make missing
  inverses a hard `docs check` error, and add a narrow two-document
  `docs relate add/remove` mutation for explicit repair. The mutation works on
  active docs and, with a reasoned audit record, on archived endpoints.
- Progress: **Active / milestone-setup complete (2026-08-10).** This is the
  next implementation milestone. No TDD phase has started; Phase 1 must freeze
  the remaining command/output and archive-audit details before RED tests.

### Goal

Make the `Related:` graph useful to the agent working in a document without
turning relationships into archive authorization. From any milestone, an agent
should be able to see adjacent execution order, durable prerequisites, and
current blockers. `docs check` should identify an incomplete reciprocal edge
precisely, and `docs relate` should let the agent repair or remove the intended
pair without hand-editing either endpoint.

### Primary use-case acceptance

- **Navigate the work locally.** A reader of one milestone can follow
  `precedes`/`follows`, distinguish a durable `depends-on` relationship from a
  transient `blocked-by` relationship, and reach the reciprocal context.
- **Upgrade and repair an existing tree.** `docs check` names the source,
  verb, target, and exact missing inverse. The agent judges whether the source
  edge is valid, then explicitly adds the inverse or removes the invalid pair.
- **Repair history without rewriting history.** When an endpoint is archived,
  only the exact recognized `Related:` bullets and the audit metadata required
  for the repair change; lifecycle, archive location, original
  `Archived-reason:`, unrelated metadata, and prose remain intact.

## Binding scope

### D1 — Reciprocal relationship vocabulary

The recognized inverse map is:

| Forward | Reverse | Meaning |
|---|---|---|
| `precedes` | `follows` | Adjacent execution order |
| `depends-on` | `required-by` | Durable planned prerequisite |
| `blocks` | `blocked-by` | Current inability to proceed |

The inverse is symmetric in both directions. Sequence, dependency, and
blocking stay distinct. None implies archive membership. Other `Related:`
verbs remain free-form and do not gain reciprocal validation.

### D2 — Hard `missing-inverse` validation

`docs check` emits an error when a recognized edge lacks its exact inverse.
The rule applies only when both endpoints are included by the effective tree
predicate, successfully parsed managed Markdown docs, and the target already
passes existing resolution checks. Existing `broken-ref`, exclusion,
malformed-doc, lifecycle, and vocabulary rules retain ownership of their
cases. The finding must be actionable in both human and JSON output and must
not invent whether the correct repair is add or remove.

### D3 — Explicit two-endpoint `docs relate add/remove`

Add a narrow relationship mutation namespace. The setup recommendation to
freeze in Phase 1 is:

```text
docs relate add SOURCE VERB TARGET [--reason TEXT] [--date YYYY-MM-DD]
docs relate remove SOURCE VERB TARGET [--reason TEXT] [--date YYYY-MM-DD]
```

The command accepts only the six recognized verbs, infers the inverse, edits
both endpoints as one coordinated operation, is idempotent, supports
`--dry-run`, refreshes `INDEX.md` once, and has machine-readable output. It is
not a generic `Related:` editor and does not bulk-repair a tree.

### D4 — Controlled archived-endpoint repair

An add/remove touching an archived endpoint requires an explicit reason. The
only permitted archived changes are the exact reciprocal relationship bullets,
`Updated:`, and a dated/reasoned repeatable `Revision:` audit record. The
original `Archived-reason:` remains the explanation for entry into the archive.
Lifecycle, role, project, location, unrelated edges/metadata, and prose are
byte-identical. Active endpoints receive the relationship edit and normal
`Updated:` bump without an archive revision record unless Phase 1 deliberately
pins one common audit shape.

### D5 — Compatibility and upgrade guidance

Document that trees with one-sided recognized edges can begin failing
`docs check` after upgrade. Human and JSON findings carry enough information
for an agent to choose add-vs-remove. CLI help, `cli.md`, `convention.md`, the
bundled skill, CHANGELOG, and upgrade examples stay in surface parity. No
automatic conversion of free-form edges occurs.

## Out of scope

- Bulk auto-repair or automatic choice of which edge is true.
- A graph database, graph query/rendering command, or `archives-with` verb.
- Cycle detection, sequence cardinality, tracker-order agreement, or deriving
  one relationship class from another.
- Coupling `blocks`/`blocked-by` to `Lifecycle: blocked`.
- General archived-document editing.
- Archive-selection behavior (M26) and Markdown body links (M27/M28).
- Agent Playbook Suite changes; that repository consumes the released v2.0
  behavior after M29.

## Current state analysis

- `Doc.related` already preserves ordered `(verb, target)` pairs and
  `parse_metadata_block` understands the `Related:` bullet group.
- `check_doc` owns target-level `broken-ref` validation, while `check_tree`
  currently validates documents independently and has no cross-document
  reciprocal pass.
- `rewrite_related_refs` can rewrite targets but cannot add/remove a typed edge.
- `set_metadata_field` edits scalar metadata; repeatable `Revision:` history
  needs a minimal group editor rather than lossy full serialization.
- `atomic_write` provides per-file durability. M25 must define and test the
  two-file failure contract before claiming coordinated atomicity.
- Archived docs are normally immutable except narrow move-driven `Related:`
  rewrites from M18. M25 adds a second, explicitly requested and audited,
  relationship-only exception.
- The live docs tree already uses reciprocal `precedes/follows` and
  `depends-on/required-by` edges for M25–M29, providing Phase-9 dogfood data.

## Deliverables

- [ ] D1 inverse vocabulary and semantics documented.
- [ ] D2 hard `missing-inverse` rule in human and JSON `docs check` output.
- [ ] D3 idempotent, validate-all-first `docs relate add/remove` for active docs.
- [ ] D4 reasoned, narrowly audited archived-endpoint repair.
- [ ] D5 upgrade guidance, CLI/bundled-skill parity, and release notes.
- [ ] RED/GREEN unit, integration, CLI, failure-injection, and dogfood coverage.

## TDD implementation plan

### Phase 1 — Define Contract

- Objective: freeze the inverse map, finding schema/message, command grammar,
  output modes, idempotency, two-file failure behavior, `Revision:` encoding,
  archived reason/date rules, and v2.0 compatibility language.
- Files: `docs/cli.md`, `docs/convention.md`, this milestone, bundled reference
  mirrors, and contract-level function signatures in `src/docs_cli/cli.py`.
- Exit: every remaining open question below is resolved; specs and signatures
  are internally consistent; no business logic lands.

### Phase 2 — Write Tests (RED)

- Objective: express inverse validation and two-endpoint mutation behavior
  before implementation.
- Files: `tests/test_check.py`, `tests/test_cli_check.py`, new
  `tests/test_cli_relate.py`, plus focused parser/editor tests as needed.
- Exit: happy, idempotent, missing-inverse, malformed, excluded, unknown-verb,
  dry-run/JSON, active/archive, and injected-second-write-failure cases are RED
  only for missing M25 behavior.

### Phase 3 — Create Data/Fixtures

- Objective: provide small trees for every relationship direction and archived
  repair boundary.
- Files: new fixtures under `tests/fixtures/trees/` for clean reciprocal,
  missing inverse, excluded/malformed endpoint, and active↔archived pairs.
- Exit: fixtures parse deterministically and isolate one semantic per case.

### Phase 4 — Run Tests (RED Baseline)

- Objective: prove the new tests fail for the intended missing behavior.
- Files: implementation log only.
- Exit: full baseline captured; no collection errors, tracebacks, or unrelated
  regressions; GREEN-at-baseline locks classified explicitly.

### Phase 5 — Update Base Interfaces

- Objective: add inverse lookup, relationship-edit planning models/helpers,
  finding context, and revision-audit primitives without completing behavior.
- Files: `src/docs_cli/cli.py` and unit tests.
- Exit: interfaces typecheck; tests remain honestly RED at the behavior seam.

### Phase 6 — Implement Offline/Core Path

- Objective: implement reciprocal tree validation and validate-all-first,
  idempotent paired edits including the archived audit boundary.
- Files: `src/docs_cli/cli.py`, core/editor/check tests.
- Exit: core tests GREEN; injected failures satisfy the Phase-1 contract; no
  unrelated bytes change.

### Phase 7 — Update Tool/Wrapper Layer

- Objective: wire `docs relate add/remove`, help, human/JSON/dry-run output,
  exit codes, one final reindex, version/CHANGELOG, and bundled skill surface.
- Files: CLI parser/dispatch, `docs/cli.md`, `docs/convention.md`,
  `src/docs_cli/skill/`, `CHANGELOG.md`, packaging/version pins.
- Exit: subprocess tests and surface-parity checks GREEN.

### Phase 8 — Run Tests (GREEN)

- Objective: run focused and full suites plus lint, format, types, reference
  byte-identity, and docs integrity.
- Files: implementation log only unless a real defect is found.
- Exit: all gates GREEN with exact counts recorded.

### Phase 9 — Integrate / Accept / Dogfood

- Objective: exercise the upgrade workflow on a throwaway copy of this docs
  tree: detect a deliberately removed inverse, repair it with `docs relate`,
  remove an invalid pair, and repair an archived endpoint with an audit reason.
- Files: throwaway tree only; committed docs record evidence.
- Exit: use-case flows pass unattended, `docs check` returns clean afterward,
  and unrelated archived bytes remain identical.

### Phase 10 — Quality, Docs, Refactor

- Objective: simplify the implementation, close surface/upgrade docs, update
  the shipped use-case catalog, and write milestone completion summaries.
- Files: code/docs as justified, milestone and implementation log.
- Exit: full gate GREEN; no placeholders; M25 implementation-complete and ready
  to hand off to M26 while remaining live until the M29 publish closeout.

## Phase checklist

- [ ] Phase 1 — Define Contract
- [ ] Phase 2 — Write Tests (RED)
- [ ] Phase 3 — Create Data/Fixtures
- [ ] Phase 4 — Run Tests (RED Baseline)
- [ ] Phase 5 — Update Base Interfaces
- [ ] Phase 6 — Implement Offline/Core Path
- [ ] Phase 7 — Update Tool/Wrapper Layer
- [ ] Phase 8 — Run Tests (GREEN)
- [ ] Phase 9 — Integrate / Accept / Dogfood
- [ ] Phase 10 — Quality, Docs, Refactor

## Decisions carried from discovery

- The tracker remains the complete authoritative view; individual docs provide
  direct local context.
- The three inverse pairs and their distinct meanings are binding.
- Missing inverses are errors, not compatibility warnings, only when both
  endpoints are included and parseable.
- The repair is an explicit two-document add/remove operation; bulk repair is
  deferred.
- Archived relationship repair is permitted only through the narrow audited
  exception described in D4.
- Relationships never grant archive authorization.

## Open questions for Phase 1

1. Exact positional grammar and whether machine output is `--json`,
   `--dry-run --json`, or one stable operation-plan record shared by both.
   Recommendation: `SOURCE VERB TARGET`, with a JSON record naming both before
   and after edges.
2. Exact repeatable `Revision:` representation. Recommendation: a bullet group
   with one ISO-dated entry per mutation, carrying action, inverse pair, and
   operator reason.
3. Coordinated-write failure contract. Recommendation: stage and validate both
   complete texts first, then publish with rollback on a second write failure;
   pin recovery behavior with failure injection rather than claiming impossible
   filesystem-wide transactional guarantees.
4. Active↔archived audit symmetry. Recommendation: require `--reason` when
   either endpoint is archived, append `Revision:` only to archived endpoints,
   and bump `Updated:` on every endpoint whose bytes change.
5. Version staging. Recommendation: begin the v2.0 train in M25 and publish only
   through M29; Phase 1 decides whether the local package becomes 2.0.0 here or
   at a later implementation milestone.

## Testing and quality gate

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q
.venv/bin/docs check --root docs
```

Additional gates: `docs check --json` schema assertions, bundled
`cli.md`/`convention.md` byte identity, `docs --help`/`docs relate --help`
surface parity, archive byte-identity checks, and the live INDEX snapshot.

## Success criteria

- Every recognized relationship pair is locally navigable in both directions.
- A one-sided recognized edge makes `docs check` exit 2 with one actionable
  `missing-inverse` finding; excluded/malformed/non-managed endpoints do not
  produce a misleading inverse finding.
- `docs relate add/remove` changes exactly the intended pair, is idempotent,
  previews without writing, and never leaves a deliberate half-pair after a
  handled failure.
- Archived repair preserves lifecycle/history and produces a dated reason audit
  with no unrelated byte changes.
- Existing free-form verbs and existing `broken-ref` ownership stay compatible.
- Full quality and dogfood gates are GREEN, leaving M26 ready to prepare next.
