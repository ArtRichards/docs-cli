# docs-cli Feedback Log

Lifecycle: draft
Role: log
Project: docs
Updated: 2026-08-10

## Purpose

This log records operator and downstream-consumer feedback that may become a
future docs-cli milestone. Entries preserve the observed use case, desired
behavior, ownership, compatibility constraints, and unresolved design choices
without starting implementation. When feedback is promoted, its entry remains
as the discovery and decision audit source and records the owning milestones.

## Entries

### 2026-08-09 — Useful relationship graphs, strict reciprocity, and upgrade repair

- Source: Agent Playbook Suite dogfooding feedback from a real milestone archive and follow-on relationship-model discovery.
- Feedback: the `Related:` graph should primarily make documents easier for an agent to use during active work. It should expose completed and upcoming work, execution order, actual dependencies, current blockers, and direct context. Archive convenience must adapt to that useful graph rather than determine its default relationships.
- Observed evidence:
  - A completed milestone had intentional, useful cross-milestone `pairs-with` links. Bare `docs archive --cascade` would also have archived the next milestone, a paused milestone, an exploration, and `milestone-plan.md`; a dry run plus `--cascade-only 'm2e1a4-*'` safely bounded the operation.
  - `docs archive` repaired `Related:` targets but left fifteen prose Markdown links to be repointed manually. A whole-tree dangling-`.md` sweep was required in addition to `docs check`.
  - Current suite guidance makes the over-cascade structural: a milestone is `child-of: milestone-plan.md`, may have useful contextual `pairs-with` edges, and is then archived with bare cascade.
- Desired relationship semantics:
  - The tracker remains the authoritative complete view of milestone order, status, and next work.
  - Individual milestone docs also provide direct local navigation.
  - Adjacent execution order uses reciprocal `precedes` / `follows` edges.
  - Planned prerequisites use reciprocal, durable `depends-on` / `required-by` edges.
  - Current inability to proceed uses reciprocal, transient `blocks` / `blocked-by` edges; removing the blocker pair does not erase the durable dependency history.
  - Sequence, dependency, and blocking remain distinct. None implies archive membership.
  - Do not introduce `archives-with` as the default relationship direction; the model optimizes active use, not archive automation.
- Validation outcome: `docs check` should treat a missing inverse for the three recognized pairs as an error, not a compatibility warning. Other verbs remain free-form. Reciprocal validation applies only when both endpoints are included, successfully parsed managed Markdown docs; existing broken-target, exclusion, and malformed-doc rules retain their ownership.
- Upgrade and repair outcome: upgrading must assist an agent in repairing trees that become invalid under the stronger invariant. Findings should identify the exact missing reverse edge, and the workflow needs a supported way to apply coordinated repairs, including a policy for archived endpoints.
- Archived-endpoint decision: controlled upgrade repair may modify the required `Related:` metadata in archived documents and the audit metadata needed to represent that real change honestly. Each real repair updates `Updated:` and appends a dated, reasoned `Revision:` audit record while preserving the original `Archived-reason:` as the explanation for why the document entered the archive. Archived lifecycle, role, project, location, unrelated metadata, and prose remain immutable. This permits strict reciprocal links between active and archived milestones without turning the archive back into an ordinary editable tree.
- Complexity constraint: use a dedicated CLI mutation only if needed, and keep it narrow. Do not add a general archive editor or an automatic graph-rewrite engine; archives should remain unchanged apart from the exact relationship bullets and corresponding `Updated:` / reason audit metadata required for strict reciprocity.
- Complexity assessment: the required implementation is bounded because docs-cli already parses and rewrites `Related:` fields, validates targets, performs atomic per-file writes, emits machine-readable check findings, and refreshes the index. The new work is validate-all-first two-endpoint editing, inverse-verb lookup, idempotent add/remove behavior, exact dry-run output, and explicit failure handling across coordinated writes. It does not require a separate graph store or general migration framework.
- Smallest candidate workflow: `docs check` emits an actionable hard `missing-inverse` finding naming the exact reverse edge; an agent invokes a narrow relationship mutation only for those repairs. When either endpoint is archived, the mutation changes only the recognized reciprocal `Related:` bullets, updates `Updated:`, and appends the repeatable `Revision:` record with its date and reason, leaving the original `Archived-reason:`, unrelated edges, and content untouched.
- Repair-command decision: the first version provides an explicit two-document `docs relate add/remove` operation and defers bulk repair. The agent uses the actionable check finding to decide whether the original edge is valid, then chooses to add its missing inverse or remove the invalid pair. The CLI previews and atomically applies both reciprocal edits, including the controlled archived-endpoint audit behavior. This assists upgrades without turning accidental edges into consistent but still incorrect relationships.
- Alternatives considered:
  - Exempt archived endpoints from reciprocal validation: preserves byte immutability but leaves the useful relationship graph incomplete and weakens the hard-error invariant.
  - Store late relationships in an active overlay or central graph: preserves archived bytes but creates a second source of truth and removes direct context from the archived document.
  - Permit relationship repair only during a one-time version migration: handles existing trees but not dependencies or blockers discovered after that migration.
  - Unarchive, copy, or rearchive documents to add links: introduces lifecycle, path, and historical churn for a metadata-only graph repair.
  - A dedicated, auditable relationship-only mutation remains the smallest option that preserves archive history, direct use, and strict validation.
- Current capability gap: docs-cli can report missing target paths and can rewrite moved targets through `docs mv` and `docs archive`, but it has no reciprocal validation, managed-tree upgrade, `relate`, or `repair` verb. `docs migrate` is a foreign-tree adoption workflow, not an existing reciprocal-link upgrade mechanism.
- Archive implications: relationship semantics and archive selection must be decoupled. Archive commands and bundled guidance need a safe explicit-selection model, and prose-link detection or repair remains a separate gap because metadata validation alone cannot prove body links resolve.
- Cascade-safety decision: after reviewing the behavior in plain language, the operator confirmed that relationships provide context, never archive authorization. Bare `--cascade` must not write and should fail with safe-flow guidance; `--cascade-dry-run` previews the related candidates; a write that includes related documents requires an explicit `--cascade-only` scope; and omitting cascade archives only the named document.
- Body-link decision: `docs mv` and `docs archive` should automatically rewrite actual Markdown body-link destinations that resolve to a moved document, while leaving plain-text mentions and code examples unchanged. Path repair belongs to the coordinated move rather than a separate whole-tree manual substitution pass; implementation discovery must still pin the supported Markdown forms, path resolution, and validation behavior.
- Body-link validation decision: `docs check` should emit a hard error when a parsed local Markdown body link points to a missing file, including damage introduced outside `docs mv` or `docs archive`. Links inside code and external URLs are out of scope. Move-time rewrites preserve fragments such as `#section`, but the first implementation does not validate whether the referenced heading exists.
- Scope boundary for the first implementation milestone: reciprocal semantics, hard-error validation, and agent-usable upgrade repair. Cycle detection, sequence cardinality, tracker-order agreement, and coupling blockers to `Lifecycle: blocked` are explicitly outside this feedback and are not required follow-ups.
- Ownership: primarily docs-cli for the convention, checker, repair/upgrade surface, archive behavior, and bundled `docs` skill. Agent Playbook Suite should consume the released behavior later by updating its foundation, milestone, and shipping workflows.
- Release ordering: implement and release the required docs-cli milestones before releasing dependent Agent Playbook Suite versions.
- Status: discovery complete and behavior/routing operator-confirmed on 2026-08-10; no implementation started. The operator will plan and run docs-cli milestones before releasing dependent Agent Playbook Suite changes.
- Milestone design details: pin the detailed `docs relate` arguments and machine-readable dry-run output; define compatibility and upgrade communication for the confirmed cascade and link-check changes; choose which structural Markdown link forms enter the first rewrite milestone; and sequence the accepted scope into docs-cli milestones.
- Promotion (2026-08-10): discovery is now registered as the v2.0 train — M25 reciprocal relationship integrity + `docs relate`; M26 safe explicit archive selection; M27 Markdown body-link validation and legacy repair policy; M28 move-safe body-link rewrites; M29 PyPI publish 2.0.0. M25 is fully prepared with Phase 1 next; M26–M29 remain draft stubs. The feedback entry stays as the discovery/audit source rather than being deleted after promotion.
