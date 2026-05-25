# docs — Test Strategy

Lifecycle: active
Role: reference
Project: docs
Updated: 2026-05-20

Related:
- pairs-with: architecture.md
- pairs-with: cli.md

## Layers

| Layer | Tool | Scope |
|---|---|---|
| Unit | pytest | Parser, walker, render, vocab loading. Pure-function focus. |
| Integration | pytest + tmp_path | Multi-file operations: index over a tree, archive move, mv rewrite. |
| End-to-end | pytest + subprocess | Invoke `docs` as a subprocess on a fixture tree. CLI exit codes verified. |
| Dogfood | manual + CI | Run `docs index docs/` on this repo; assert generated INDEX matches hand-written one (M1 acceptance). |

## Fixture sources

Three sources of test docs, in increasing realism:

1. **Inline strings** — for parser unit tests. Short, focused on one rule (well-formed, malformed metadata, missing H1, multi-value `Related:`).
2. **`tests/fixtures/trees/`** — hand-built sample trees, one per scenario:
   - `minimal/` — one doc, no archive subtree
   - `with-archive/` — active + archive subtree with mixed roles
   - `marker-preservation/` — INDEX.md with hand-edited preamble and trailer outside markers
   - `drift/` — status/location mismatches for `docs check` tests (M3)
   - `foreign/` — non-conforming docs for `docs migrate` tests (M4)
3. **`docs/`** (this repo's own docs root) — real-world tree, used for dogfood and integration tests. Anything that breaks here breaks the project's own self-documentation.

## Critical paths

Each must have at least one test before merging:

- Parser: well-formed doc → all metadata extracted.
- Parser: missing `Status` → raises a specific exception with file path and line number.
- Parser: `Related:` with mixed inline/bullet shapes → bullets only (inline form not allowed for `Related:`).
- Walker: archive subtree distinguished from active tree.
- Index render: marker block preserved verbatim, content between markers regenerated.
- Index render: idempotent (run twice → same output).
- CLI: invalid role on `docs new` → exit 2.
- CLI: missing `.docs.toml` → falls back to cwd defaults, exit 0.
- Atomic write: simulated failure mid-write leaves original file untouched. (Tested with mock that raises after tmp write but before rename.)

## Coverage targets

No hard percentage. Required: every code path in the model module has a unit test; every CLI verb has an integration test; the dogfood test runs in CI.

## Quality gates

Per the methodology, run before each milestone closes:

```
ruff check .
ruff format --check .
mypy bin/docs                  # warnings OK in v1; errors must be zero
pytest -q
./bin/docs check docs/         # once M3 lands; for M1 this is `./bin/docs index docs/`
```

Phase 10 of each milestone runs these.

## What we don't test

- Performance / scale. The tool targets trees in the low thousands of files; no benchmarks until that limit is hit.
- File-system semantics specific to non-POSIX hosts. POSIX-atomic rename is assumed.
- Non-UTF-8 encodings. The tool assumes UTF-8; non-UTF-8 input is a documented failure mode.
- Markdown rendering. The tool reads metadata; the body content is opaque.

## Data plan note

All fixture data is synthetic and committed to the repo. No real-world docs are imported into the test tree (except the repo's own `docs/` for dogfood, which is intentional). No privacy or compliance considerations.
