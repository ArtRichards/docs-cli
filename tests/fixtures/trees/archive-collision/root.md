# Root

Lifecycle: active
Role: milestone
Project: archive-collision
Updated: 2026-06-01

Related:
- pairs-with: x/dup.md
- pairs-with: y/dup.md

## Body

E3 — two candidates in different subdirectories sharing a basename. The
archive layout is `archive/<date>/<basename>`, so both would land on ONE
destination. The pre-flight must detect the intra-plan collision and refuse
the whole operation before any byte moves; in 1.x one document was archived,
the other left behind with a bare-path message, and the run exited 0.
