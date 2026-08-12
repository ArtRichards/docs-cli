# Master

Lifecycle: active
Role: spec
Project: cascade-refs
Updated: 2026-05-20

Related:
- pairs-with: sidekick.md

## Body

The "master" half of a pairs-with pair. The scoped-cascade test invokes
`docs archive master.md --cascade-only 'sidekick.md'`, which moves both
`master.md` and `sidekick.md` into `archive/<date>/` with no prompt — bare
`--cascade` is retired (M26 — D2) and `docs archive` never reads stdin.
