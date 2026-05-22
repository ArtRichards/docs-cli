# Deep-Dive Notes

This file lives in a nested `topics/` subdirectory that is **not** an
archive-style folder — it is just an ordinary grouping subdirectory of the
active tree.

The migration helper must recurse into it and add metadata in place, leaving
the file exactly where it sits. The active-tree directory layout, nested
subdirectories included, is never restructured by `migrate`.

## Why this fixture exists

It exercises the recursion-and-migrate-in-place behaviour: a foreign tree is
not required to be flat, and a non-archive subdirectory is left untouched on
disk.
