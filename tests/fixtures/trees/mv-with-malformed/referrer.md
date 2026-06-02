# Referrer

Lifecycle: active
Role: notes
Project: mv-malformed
Updated: 2026-05-21

Related:
- pairs-with: good-a.md

## Body

A doc whose `Related:` edge points at `good-a.md`. On a successful `mv`
this edge would be rewritten; the A1 atomicity test asserts it is
byte-identical after an ABORTED mv (the malformed sibling blocks the
rewrite walk), confirming no partial rewrite occurred.
