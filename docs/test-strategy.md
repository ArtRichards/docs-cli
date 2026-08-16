# docs — Test Strategy

Lifecycle: active
Role: reference
Project: docs
Updated: 2026-08-16

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
   - `movelink-*/` — the M28 family, **one semantic per tree**, for
     move-safe body-link rewriting: `-incoming` (class 1 — one target, two
     spellings, two depths, plus a prose mention and a code span that must
     survive byte-identical), `-moved-referrer` (class 2, deepening and
     flattening in one move), `-both` (both classes in one archive, plus the
     co-moving no-op), `-archived-referrer` (the D5 shape — an archived
     referrer, a non-moving edge, a non-moving destination and a bare prose
     mention, so the byte-identity boundary is pinned with it), `-nested`
     (the path math, three spellings including `../../sub/../root.md`),
     `-strand` (D6 leg 1 — a live child outside the plan, alongside a
     legitimate closeout that must **not** trip it), and `-closeout` (the
     `archive-pair` / `archive-trio` shape **reproduced** with real body
     links, so no committed tree had to be edited). Structure only, never
     dates — and the **line and column numbers are contract**, asserted
     verbatim by the CLI locks. The **exotic grammar** — angle destinations,
     titles, percent- and backslash-escapes, fragments, directory
     destinations, reference definitions, colons and non-ASCII filenames —
     lives in inline strings against the pure planner, and the mutation-shaped
     cases that write and then byte-compare use inline `tmp_path` builders:
     the M25 rule, plus one M28-specific reason, which is that no committed
     fixture filename may carry a space or a parenthesis (`tests/` ships in
     every sdist).
   - `archivedate-*/` — the M28a family, **one semantic per tree**, for the
     archive-date witness and its two legs: `-clean` (a corroborated witness,
     one of them nested a level deeper so the first-segment reading is pinned,
     plus a deliberate cross-dated `pairs-with` pair that locks the **declined**
     rule), `-drifted` (the witness against a *different* dated directory —
     message form A, the headline E1d case), `-absent` (a pre-2.0 archived
     document carrying `Archived-reason:` and **no** witness, so the
     present-only contract is measured rather than asserted), `-outside` (the
     witness on a document in the active tree, in both the `status-drift`-firing
     and `status-drift`-silent polarities), `-undated` (the witness under an
     undated archive subdirectory — form B's second shape), and
     `-two-dated-dirs` (two populated dated directories holding a
     witness-carrying and a witness-less document plus an ordinary `archive/notes/`
     sibling, so Leg 2's refusal, its permitted same-directory rename and its
     archive-root neighbour are all reachable on one tree). Structure only, with
     fixed past dates, never run-time ones. Three of the six are **deliberately
     drifted**, which is why they get their own `_pre_m28a_tree_names()` sweep
     rather than widening `_legacy_tree_names` — widening one would both move
     pre-existing parametrized ids and make these three fail it. Every
     non-default `[archive] dir` / `date_format` case and every
     write-then-byte-compare case uses inline `tmp_path` builders, the M25 rule.
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
- Coordinated move: a rename and a scoped archive each leave `docs check` **clean**, with the diff touching only destination tokens and the metadata the move already owned — the tool must never produce a tree that fails its own gate.
- Strand-check leg 1: a plan that would archive a document a still-active document declares itself `child-of` refuses at exit 2 with **zero bytes written** and both ends named, while a legitimate milestone closeout **completes** — the over-fire lock is as required as the refusal, because a check that fires on correct trees is one operators route around.

## Coverage targets

No hard percentage. Required: every code path in the model module has a unit test; every CLI verb has an integration test; the dogfood test runs in CI.

## Quality gates

Per the methodology, run before each milestone closes:

```
ruff check .
ruff format --check .
mypy src/ tests/               # errors must be zero
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
