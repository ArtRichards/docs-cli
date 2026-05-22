# Carries Extra Metadata

Status: wip
Owner: alice
Tags: infra, urgent
Updated: 2025-09-12
Related:
- pairs-with: proj-overview.md
- see-also: some-external-doc.md

This file carries metadata-shaped lines beyond the four the convention
requires — an `Owner:`, a `Tags:`, and a `Related:` block. The migration
helper supersedes the four required fields (`Status` / `Role` / `Project` /
`Updated`) with inferred values, but it must **not** drop the extra fields.

## What migrate does with the extras

Every non-required field is preserved into a `## Migrated metadata` body
section, placed immediately below the canonical metadata block, with each
label renamed under a `Migrated-` prefix. Because the preserved fields then
live in the body — under a `## ` heading — `docs check` does not validate
them, so a stale foreign `Related:` path cannot fail the applied tree's
check.
