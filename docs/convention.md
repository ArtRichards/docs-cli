# docs — Convention Spec

Status: active
Role: spec
Project: docs
Updated: 2026-05-20

Related:
- implements: charter.md
- pairs-with: cli.md
- decision: vocab-adr.md
- decision: dual-status-adr.md

## Scope

This spec defines the on-disk convention that `docs` reads and writes. It is the portable, tool-independent part: any directory following this convention is navigable with `grep` and `ls` alone. The `docs` CLI is convenience over this convention, not a prerequisite for it.

## Document shape

Every `.md` file managed by `docs` has this structure:

```markdown
# <Title>

<metadata-block>

## <first content section>
...
```

### H1 title

The first non-empty line of the file MUST be a single `#` H1. This is the doc's display title in indexes and `docs list` output.

### Metadata block

Lines immediately after the H1 (separated by a blank line) form the **metadata block**. The block is a contiguous run of `Label: value` lines, ending at the next blank line.

Within the block, two line shapes are allowed:

```
Label: inline value
Label:
- value
- value
```

The first form is for single values. The second form is for multi-valued labels (used by `Related:` and any other label that takes a list).

The metadata block terminates at the first blank line. Content sections begin after that.

### Required fields

| Field | Type | Meaning |
|---|---|---|
| `Status` | controlled vocab | doc's lifecycle state |
| `Role` | controlled vocab | what kind of doc this is |
| `Updated` | `YYYY-MM-DD` | last meaningful update |

### Optional fields

| Field | Type | Meaning |
|---|---|---|
| `Project` | kebab-case slug | project this doc belongs to; defaults to `project.name` in `.docs.toml` if absent |
| `Related` | list of `<verb>: <path>` | typed cross-references to other docs |
| `Owner` | free-form | the human or team accountable for this doc |
| `Tags` | comma-separated | free-form tags for filtering |

Any additional `Label:` fields are harvested and exposed under `docs list --json` but not interpreted by the tool.

## Vocabularies

### Status (built-in)

| Status | When |
|---|---|
| `draft` | Being written, not ready for use. |
| `active` | Current, in use, source of truth. |
| `blocked` | Paused, waiting on something external. Pair with `Related: blocked-by: …`. |
| `done` | Complete; intentionally kept in the active tree (evergreen reference). |
| `archived` | Complete and moved to the archive subtree. |
| `superseded` | Replaced by another doc. Pair with `Related: superseded-by: …`. |

### Role (built-in)

| Role | What |
|---|---|
| `charter` | What we're building and why. |
| `plan` | How we'll get there (sequencing, milestones). |
| `spec` | Detailed design or contract. |
| `milestone` | A specific milestone definition. |
| `log` | Implementation log tied to a milestone. |
| `status` | Living status document. |
| `decision` | ADR-style: one decision, alternatives, rationale. |
| `guide` | Instructional / how-to. |
| `runbook` | Operational procedure. |
| `reference` | Evergreen technical reference. |
| `postmortem` | Incident retrospective. |
| `idea` | Pre-decision exploration. |
| `notes` | Catch-all. |

### Extending vocabularies

`.docs.toml` may **add** statuses and roles via `[vocabulary]` — never remove or rename built-ins. Additions are local to that docs root. Cross-project queries collapse to the built-in set; per-project queries see the union.

## Relationship verbs

`Related:` entries use the form `<verb>: <path>`. Verbs are free-form, but a small set is conventional:

- `pairs-with` — bidirectional sibling (spec ↔ status, milestone ↔ log).
- `child-of` / `parent-of` — hierarchical.
- `implements` — this doc realizes that spec/charter.
- `spec-of` — this doc specifies that thing.
- `supersedes` / `superseded-by` — replacement.
- `blocked-by` — pause causation.
- `decision` — points at a decision doc that justifies this one.
- `references` — weakest form, "see also."

`docs check` does not validate verbs (free-form), but it does validate that every `Related:` path resolves to a file under the docs root.

## Archive subtree

Completed work moves to an archive subtree. Default subdir name: `archive/`. Convention: `archive/YYYY-MM-DD/` per archive event. Configurable via `[archive] dir` in `.docs.toml`.

Status/location consistency rules:

- A doc at the top level (active tree) MUST have `Status:` in `{draft, active, blocked, done, superseded}`.
- A doc under the archive subtree MUST have `Status: archived`.
- `docs check` reports any mismatch with nonzero exit.

`done` vs `archived`: `done` stays in the active tree (evergreen reference); `archived` is moved to the archive subtree. Use `done` when the doc is finished but still referenced day-to-day.

## INDEX file

The `INDEX.md` file at the root of the docs tree is a **generated view, not a managed doc**. It does not require a metadata block, and `docs` excludes it from traversal by filename. (Specifically: any file at the docs root literally named `INDEX.md` is read as the existing index for marker-block preservation and skipped during walking; it never appears as an entry in itself.)

The docs root contains an `INDEX.md` with this structure:

```markdown
# <Root title>

<optional hand-edited preamble>

<!-- docs:generated start -->
... derived content ...
<!-- docs:generated end -->

<optional hand-edited trailer>
```

`docs` only rewrites content between the markers. Everything outside is preserved verbatim. The derived section groups by Status and Role, lists every `.md` file in the tree with its title and a one-line excerpt, and separates the active tree from the archive subtree.

## File naming

Names are free-form. The metadata block carries the load; the filename is for humans. Kebab-case is recommended (`vocab-adr.md`, not `Vocab_ADR.md`), but not enforced.

## What `docs` does not promise

- No automatic `Updated:` bumping on every write. Use `docs touch` or hand-edit.
- No link-graph traversal. `Related:` is metadata, not a query target in v1.
- No content validation beyond metadata. The body of a doc is opaque to the tool.
