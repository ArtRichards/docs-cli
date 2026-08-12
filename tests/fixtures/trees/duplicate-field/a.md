# A

Lifecycle: active
Role: notes
Project: duplicate-field
Updated: 2026-05-20

Related:
- precedes: b.md

Related:
- references: b.md

## Body

Two `Related:` labels. `parse_metadata_block` builds a dict, so the second
label REPLACES the first: `precedes: b.md` is silently discarded before any
rule, the INDEX renderer, or `Related:` resolution ever sees it. One
semantic per tree — the only finding here is `duplicate-field`.
