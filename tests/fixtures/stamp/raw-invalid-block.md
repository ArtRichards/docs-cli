# Raw Invalid Block

Lifecycle: draft
Role: not-a-real-role
Project: tree
Updated: 2026-01-01

BODYMARKER — this file already carries a metadata-block-shaped header, but
its `Role:` is NOT in the vocabulary, so strict `parse()` rejects it.

## Section

`docs stamp` must treat this as a FRESH file: the four required fields are
superseded with valid values (the bogus `Role:` is replaced, never parked),
yielding exactly ONE valid metadata block — no orphaned or doubled block —
and a tree that passes `docs check`.
