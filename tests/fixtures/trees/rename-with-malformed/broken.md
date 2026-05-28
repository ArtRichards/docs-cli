This file has no H1 — its first line is body prose.

The `docs` parser requires an `# H1` first line; without it `parse()` raises
`MetadataError`. `docs project rename` must surface that error before
mutating `good-a.md` / `good-b.md` / `.docs.toml` (atomic validate-first).
