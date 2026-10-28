# Raw Invalid Block

Lifecycle: draft
Role: not-a-real-role
Project: tree
Updated: 2026-01-01

BODYMARKER — this file already carries a metadata-block-shaped header, but
its `Role:` is NOT in the vocabulary, so the tree's configuration rejects it.

## Section

The block is complete — `Lifecycle:`, `Role:` and `Updated:` are each
present — so `docs stamp` must REFUSE it: exit 1, the failing `Role:` named,
and zero bytes written. Re-stamping would replace the document's lifecycle,
role and project, so the refusal points at `docs check` and `docs touch`
instead.
