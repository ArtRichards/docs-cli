# Witness

Lifecycle: active
Role: notes
Project: cascade-refs
Updated: 2026-05-20

Related:
- references: master.md
- references: sidekick.md

## Body

A doc that references both `master.md` and `sidekick.md`. After
`docs archive master.md --cascade`, both edges must be rewritten to the
archive paths in a single atomic batch.
