# Decision: Status and Role vocabularies

Status: active
Role: decision
Project: docs
Updated: 2026-05-20

Related:
- decision: dual-status-adr.md
- spec-of: convention.md

## Context

The convention requires controlled vocabularies for `Status` and `Role`. Too small a set fails to express common situations; too large a set fragments and rots. We need a built-in vocabulary that covers the common cases for both human-authored and agent-authored docs.

## Decision

**Status — 6 values:** `draft`, `active`, `blocked`, `done`, `archived`, `superseded`.

**Role — 13 values:** `charter`, `plan`, `spec`, `milestone`, `log`, `status`, `decision`, `guide`, `runbook`, `reference`, `postmortem`, `idea`, `notes`.

Both vocabularies are extensible via `.docs.toml` `[vocabulary]`, but additions only — built-ins cannot be removed or renamed.

## Rationale

### Status

Most lifecycle systems use 3–4 states (todo / in-progress / done). That works for tasks but not for docs, which have lifecycle states tasks don't:

- `draft` vs `active` — a doc can exist and be referenced before it's authoritative. Tasks don't have this distinction.
- `blocked` — captured because "paused waiting on something" is a real, frequent state that disappears under prose if there's no slot for it.
- `done` vs `archived` — some completed docs live forever in the active tree (runbooks, reference). Others are moved to archive. Different physical states; both deserve a name.
- `superseded` — replaced docs are kept for history. Distinct from archived (which is about completion, not replacement).

### Role

The 13 roles fall into four clusters:

- **Planning** (`charter`, `plan`, `spec`, `milestone`) — what we're building.
- **Execution** (`log`, `status`) — how it's going.
- **Decisions and learning** (`decision`, `postmortem`) — what we chose and why; what we learned.
- **Reference and exploration** (`guide`, `runbook`, `reference`, `idea`, `notes`) — operational and pre-decision material.

`decision` (ADRs) and `postmortem` are explicit because they're common, distinct patterns that other doc systems treat as second-class. `reference` is distinct from `guide` because instructional vs. evergreen-lookup is a real-world distinction.

`log` covers any chronological record where entries accumulate over time. The role isn't narrowly tied to "implementation log per milestone" — it also fits decision logs (a reviewer's running record of choices), operational logs (recurring on-call notes), and similar patterns where the doc grows over time rather than being rewritten. What distinguishes a `log` from a `status` doc: a status doc is rewritten as state evolves (snapshot of "where we are now"); a log appends.

`notes` is the explicit escape hatch. Without it, anything that doesn't fit gets shoehorned into a wrong role.

## Alternatives considered

- **Free-form vocabularies.** Rejected: cross-doc grouping and `docs check` enforcement both require a known set. Free-form lets `Status: working-on-it` slip in next to `Status: in-progress`, then `Status: WIP`, and within months the convention isn't one.
- **Smaller set (Status: 4, Role: 6).** Rejected: forces prose-decoding to recover information the metadata should already convey. Specifically, `blocked` and `done` (vs `archived`) save real work.
- **YAML-frontmatter-style with a schema file.** Rejected: more ceremony than the value justifies, and we want the convention to read as natural prose.

## Consequences

- Docs migrated from other conventions need their Status/Role coerced into the built-in set. The `docs migrate` verb (M4) handles this with agent assistance for ambiguous cases.
- Teams that genuinely need a new status (e.g., `shipped` for product orgs, `internal-review` for compliance) can add it via `.docs.toml`. Cross-project queries collapse to the built-in set; project-local queries see the union.
- Vocabulary changes ARE breaking changes. The version of `docs` that knows a new role is the only one that can validate docs using it. We accept this — vocab growth should be rare.
