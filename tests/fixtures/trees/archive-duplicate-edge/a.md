# A

Lifecycle: active
Role: milestone
Project: archive-duplicate-edge
Updated: 2026-06-01

Related:
- pairs-with: b.md
- child-of: b.md

## Body

E2 — one document reachable through TWO cascade verbs. The candidate set is
deduplicated on the canonical root-relative path with the first declaration
winning, so `b.md` is ONE candidate discovered by `pairs-with`. Without the
dedup the second archive attempt reads a file that has already moved and the
run prints a false failure while still exiting 0.
