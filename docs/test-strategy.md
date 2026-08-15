# docs — Test Strategy

Lifecycle: active
Role: reference
Project: docs
Updated: 2026-08-14

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
   - `duplicate-field/` — a doc with two `Related:` labels, for M25's D7
     rule. Isolates that one semantic: it emits `duplicate-field` and
     nothing else, deliberately, so it does not also trip the
     `test_check_tree_legacy_fixtures_gain_no_new_findings` lock. The
     interaction with `missing-inverse` is pinned inline instead.
   - `archive-*/` — the M26 family, **one semantic per tree**, for safe
     explicit archive selection: `-neighborhood` (E1 — a milestone with all
     six one-hop candidates), `-duplicate-edge` (E2 — one doc reachable by
     two verbs), `-collision` (E3 — two candidates sharing a basename), and
     `-archived-neighbour` (E4 — an archive-subtree candidate, plus its
     bullet pointing at the moving primary, so the M18 boundary is pinned
     with it). Structure only, never dates. Mutation-shaped cases use inline
     `tmp_path` builders for the same reason as the M25 family.
   - `bodylink-*/` — the M27 family, **one semantic per tree**, for the two
     body-link rules: `-clean` (every supported form, resolving), `-broken`
     (one unresolved inline link and nothing else), `-excluded-forms` (image,
     autolink, raw HTML, fenced and inline code, reference *uses*,
     fragment-only, schemed, protocol-relative, root-absolute and a
     backslash-escaped opt-out — all silent), `-nested` (resolution relative
     to the referring document, up and down, including
     `../sub/../back-inside.md`, which normalises back under the root),
     `-archived` (the un-rebased archive shape that is 132 of this repo's own
     139 breaks), and `-outside-root` (two escapes, one aimed at a path that
     **cannot** exist and one self-referential and therefore guaranteed to
     exist — the pair that makes "whether or not it would have resolved"
     testable without mocking). Structure only, never dates. The **exotic
     grammar** — angle destinations, all three title quotings, percent- and
     backslash-escapes, balanced parens, reference definitions — lives in
     inline strings against the pure scanner instead, because those cases
     assert on parse output rather than on a tree walk.
   - `reciprocal-*/` — the M25 family, **one semantic per tree**, for the
     `missing-inverse` rule: `-clean` (all three pairs complete),
     `-missing` (the one-sided edge), `-freeform` (the supersedes trap),
     `-broken` (`broken-ref` keeps ownership), `-excluded`, `-malformed`,
     `-nonmd`, `-archived-missing` / `-archived-complete`, and
     `-self-edge` (the amendment-A exemption, spelled non-canonically so
     amendment B is pinned with it). Structure only, never dates: no stale
     window is ever passed to them, so nothing rots. Mutation-shaped cases
     use inline `tmp_path` builders instead, because those tests write and
     then byte-compare — a `copytree` would be pure overhead.
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
- Archive planner: a `--cascade-only` scope selecting nothing on a **write** refuses with zero mutation — the primary is not archived either, and the two causes ("none of the N matched" vs "no candidates at all") get different messages.
- Archive apply: a mid-execution `OSError` produces an exact partial-state admission naming what moved and what did not — never a silent partial write that exits 0.

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
- Markdown rendering, headings and anchors, prose style, and document structure. From M27 the body is no longer opaque, but it is read for exactly **one** purpose — resolving the destinations of the bounded set of local links `cli.md` › *Markdown body-link validation* names. Nothing else about the body is parsed, validated, or asserted on: a fragment is preserved and never checked against a heading, and the scanner claims no CommonMark conformance.

## Data plan note

All fixture data is synthetic and committed to the repo. No real-world docs are imported into the test tree (except the repo's own `docs/` for dogfood, which is intentional). No privacy or compliance considerations.
