# Good A

Lifecycle: active
Role: notes
Project: mv-malformed
Updated: 2026-05-20

## Body

The `docs mv` source. The A1 atomicity test moves this to `good-b.md`; a
malformed sibling (`broken.md`) must make the move all-or-nothing — the
validate-all-first pre-flight walk surfaces `broken.md`'s `MetadataError`
BEFORE the move, so this file stays at `good-a.md` on the abort.
