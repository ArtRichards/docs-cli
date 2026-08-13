# Feature milestone

Lifecycle: active
Role: milestone
Project: archive-neighborhood
Updated: 2026-06-01

Related:
- child-of: plan.md
- pairs-with: milestone-impl.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: test-strategy.md
- pairs-with: status.md

## Body

E1 — the over-cascade neighborhood, mirroring this project's own shape at a
milestone closeout. Six one-hop candidates: the long-lived planning spine
(`plan.md`, `status.md`), the two specification documents (`cli.md`,
`convention.md`), the test strategy, and the milestone's own implementation
log. Only the last of those belongs in the same archive event.

`docs archive milestone.md --cascade-dry-run` must name all six.
`--cascade-only 'milestone*'` must select `milestone-impl.md` and name the
other five as not selected — the judgement the preview exists to support.
