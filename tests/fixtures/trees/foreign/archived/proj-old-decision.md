# Retire the Legacy Import Path

This decision is finished work — it lives in an `archived/` subdirectory,
the kind of non-conformant archive-style layout the migration helper detects
and normalises into `archive/YYYY-MM-DD/`.

## Decision

The legacy bulk-import path was removed in favour of the streaming importer.

## Status

Done and shipped long ago; kept only for the historical record. After
migration this file should carry `Status: archived` and sit under the
conventional dated archive directory.
