# A — recognized edge into an excluded dir

Lifecycle: active
Role: milestone
Project: reciprocal-excluded
Updated: 2026-05-20

Related:
- precedes: vendor/b.md

## Body

`vendor/` is excluded by `.docs.toml [exclude] dirs`, so `vendor/b.md` is never walked. The target file EXISTS (no `broken-ref`), but reciprocity may not be asserted against a doc the tree predicate hides.
