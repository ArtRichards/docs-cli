This file has no H1 — its first non-empty line is body prose.

The `docs` parser requires an `# H1` first line; without it `parse()` (and
therefore `walk()`) raises `MetadataError`. `docs mv` must surface that
error from its referring-edge rewrite walk; the M14 A1 fix moves the
validate-all-first pre-flight walk AHEAD of the `old_path.replace(new_path)`
move so the abort leaves `good-a.md` / `referrer.md` / INDEX untouched.
