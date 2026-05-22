# Has Partial Metadata

Status: wip
Updated: 2025-11-30

This file already carries a couple of metadata-shaped lines under its H1,
but the block is incomplete — there is no `Role:` and no `Project:` line,
and the `Status:` value (`wip`) is not in the convention's vocabulary.

The migration helper must reconcile these existing lines into a proper
metadata block rather than leaving duplicates or stacking a second block on
top of them.

## Detail

The out-of-vocabulary `Status: wip` is the interesting case: inference must
map it to a built-in status and flag the substitution as an ambiguity.
