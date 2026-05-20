# Decision: Dual-status (location + in-doc)

Status: active
Role: decision
Project: docs
Updated: 2026-05-20

Related:
- decision: vocab-adr.md
- spec-of: convention.md

## Context

A doc's lifecycle state could be expressed by:

1. Its location on disk (e.g., a doc under `archive/` is archived).
2. A `Status:` line inside the doc.
3. Both.

Each choice has tradeoffs. We need to pick one and live with it.

## Decision

**Both. Location and in-doc `Status:` are independently maintained; the `docs` CLI keeps them consistent.**

Specific rules:

- A doc in the active tree MUST have `Status` in `{draft, active, blocked, done, superseded}`.
- A doc under the archive subtree MUST have `Status: archived`.
- `docs archive` and `docs mv` keep them in sync automatically; manual `mv` or editing can introduce drift.
- `docs check` reports drift with nonzero exit. Location wins on conflict (the path is harder to silently misread than a header).

## Rationale

The naive options each fail in a specific way:

- **Location only** ("archive/ subtree = archived"). Loses information. A doc opened from a search result, in an editor, or in a code review tells you nothing about its lifecycle without you noticing the path. Worse, `Status:` can carry *prose* about the state ("Draft normative companion spec") that pure location can't.
- **In-doc only** ("Status: archived"). Active and archived docs sit in the same directory, indistinguishable by `ls`. Filesystem operations (rsync, find, grep) need to read every file's header to filter. Archive becomes a logical concept the filesystem doesn't reflect.

Combining them gives both: the path is a fast index for filesystem operations, the in-doc status carries the precise state (including prose annotations like "Draft normative companion spec" or "Done; staged for archival").

The cost is a consistency invariant the tool has to maintain. That's exactly what `docs archive` exists for — it's the only verb that should ever be moving things between active and archive, and it always updates both. Manual `mv` is allowed but `docs check` will catch the drift.

## Alternatives considered

- **Pure location.** Rejected for the reasons above; specifically loses the ability to carry prose annotations on Status.
- **Pure in-doc.** Rejected because filesystem-level operations (`ls`, `find`, backup tooling, `git log archive/`) become blind to lifecycle.
- **Status derived from location, in-doc field as a cache.** Rejected because then the cache can rot, and the prose annotation problem returns.

## Consequences

- The tool has a non-trivial invariant to maintain across operations. We accept this; it's why the tool exists.
- Users hand-archiving via `mv` will introduce drift. `docs check` surfaces it. Documentation (and the skill, M5) will discourage manual moves.
- The same dual-source pattern shows up for `Updated:` (a doc's mtime vs its `Updated:` field). We deliberately do *not* enforce consistency there — mtimes change for incidental reasons (line-ending normalization, encoding fixes) that don't represent a meaningful update. `Updated:` is hand- or `docs touch`-maintained.
