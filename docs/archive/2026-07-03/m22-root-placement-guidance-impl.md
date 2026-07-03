# M22 — Implementation Log

Lifecycle: archived
Role: log
Project: docs
Updated: 2026-07-03
Archived-reason: Milestone M22 complete; shipped to PyPI as docs-cli==1.8.0 (batched via M24) 2026-07-03

Related:
- pairs-with: archive/2026-07-03/m22-root-placement-guidance.md

## Overview

Chronological log of work on M22 (Doc-tree root placement guidance). Append a section per phase with objective, files changed, actions, test results, decisions.

## TDD Phase Progress

| Phase | Progress |
|---|---|
| 1. Define Contract | Complete |
| 2. Write Tests (RED) | Complete |
| 3. Create Data/Fixtures | Complete (N/A) |
| 4. Run Tests (RED Baseline) | Complete |
| 5. Update Base Interfaces | Complete (N/A) |
| 6. Implement Offline/Core Path | Complete |
| 7. Update Tool/Wrapper Layer | Complete |
| 8. Run Tests (GREEN) | Complete |
| 9. Implement Online/Integration | Complete (dogfood) |
| 10. Quality, Docs, Refactor | Complete |

## Phase 1 — Define Contract (2026-06-24)

### Objective
Freeze the guidance claims and the exact pin-phrases the RED test will
assert; resolve the CHANGELOG-handling decision (OQ-1).

### The contract — guidance claims

1. **Project ≠ directory.** A `Project:` is a controlled metadata field, not
   a directory; one docs root can hold many projects (by `Project:` slug),
   and a single project never requires a subdirectory of its own.
2. **Consequence.** Because `Related:` paths are root-relative, nesting a
   lone project's docs beneath a parent root prefixes every intra-project
   sibling reference with a redundant `<subdir>/`; the parent root then wraps
   exactly one project.
3. **Default — one project:** put `.docs.toml` at the directory that holds
   the docs, so the root *is* the project (docs flat, clean refs). This
   repo's own `docs/` tree models it.
4. **Multi-project:** keep one root, separate by `Project:` metadata;
   per-project subdirs optional, and only then are prefixed refs warranted.
5. **Don't** create a parent root and nest a single project one level down.

### Pin-phrases (what the Phase-2 test asserts)

Chosen to be currently ABSENT in both surfaces (verified by grep), so the
RED baseline is genuine. `"root-relative"` was rejected as a discriminator —
it already occurs in `convention.md` (line 271, re: `docs index`).

- `SKILL.md` must contain: `Where to put`, `not a directory`, `redundant`,
  and the pointer `references/convention.md`.
- `docs/convention.md` AND `src/docs_cli/skill/references/convention.md`
  (byte-identical) must contain: `metadata field, not a directory`,
  `root is the project`, `redundant`, `Where to put`.
- Parity: the bundled references copy carries the same guidance phrase
  (self-containment, M16 pattern; `tests/test_skill_refs.py` already pins
  full byte-identity).

### Files
- `docs/m22-root-placement-guidance.md` (Decisions / OQ-1).

### Issues/Decisions
- **OQ-1 (CHANGELOG):** stage M22 under a new `## 1.7.0 — UNRELEASED`
  CHANGELOG section as a Documentation entry; do **not** bump the pyproject
  version (M21 owns the actual 1.7.0 build; version is sourced from
  `importlib.metadata`). Recommended default — confirm at Phase 10.
- Documentation-only, M16-shaped: no CLI/code change, no new verb/flag.

### Test Results
N/A — Phase 2 owns tests.

## Phase 2 — Write Tests (RED) (2026-06-24)

### Objective
Pin the Phase-1 contract as a failing test before any doc edit.

### Files Changed
| File | Action | Notes |
|------|--------|-------|
| tests/test_skill_root_placement.py | added | 3 tests: SKILL.md note, convention.md guidance, bundled-reference self-containment |

### Actions Taken
- `test_skill_md_has_root_placement_note` — asserts `Where to put`,
  `not a directory`, `redundant`, `references/convention.md` in `SKILL.md`.
- `test_convention_documents_root_placement` — asserts `Where to put`,
  `metadata field, not a directory`, `root is the project`, `redundant` in
  `docs/convention.md`.
- `test_bundled_convention_carries_root_placement_guidance` — asserts the
  guidance phrases in the bundled `references/convention.md` (self-contained
  installed skill; full byte-identity stays pinned by `test_skill_refs.py`).

### Test Results
Not run here — Phase 4 captures the baseline.

## Phase 3 — Create Data/Fixtures (2026-06-24)

### Objective
None — documentation-only milestone; the "fixtures" are the live surfaces
(`SKILL.md`, `convention.md`) the test reads directly.

### Actions Taken
- N/A. No synthetic data needed.

## Phase 4 — Run Tests (RED Baseline) (2026-06-24)

### Objective
Confirm the new tests fail for the right reason (guidance absent), not
misconfiguration.

### Test Results (verbatim)
```
$ .venv/bin/python -m pytest tests/test_skill_root_placement.py -v
FAILED tests/test_skill_root_placement.py::test_skill_md_has_root_placement_note
FAILED tests/test_skill_root_placement.py::test_convention_documents_root_placement
FAILED tests/test_skill_root_placement.py::test_bundled_convention_carries_root_placement_guidance
3 failed in 0.02s    (exit 1)
```
First failing assert in each is the discriminating phrase (`assert "Where to
put" in body`, `assert "metadata field, not a directory" in bundled`) — the
files load fine; the guidance simply isn't there yet. Genuine RED.

## Phase 5 — Update Base Interfaces (2026-06-24)

### Objective
No code interfaces — documentation-only. Repurposed to finalize the exact
guidance wording before applying it.

### Actions Taken
- Finalized the convention.md subsection wording (long-line prose to match
  the file) and the SKILL.md note wording (hard-wrapped to match), confirming
  each carries its pin-phrases verbatim and the SKILL.md note adds no
  non-existent `docs <verb>` span and no `](../` link.

## Phase 6 — Implement Offline/Core Path (2026-06-24)

### Objective
Add the convention.md §Subdirectories guidance and mirror it byte-identically
into the bundled reference.

### Files Changed
| File | Action | Notes |
|------|--------|-------|
| docs/convention.md | modified | new `### Where to put .docs.toml (project ≠ directory)` subsection in §Subdirectories; `Updated:` bumped via `docs touch` |
| src/docs_cli/skill/references/convention.md | modified | byte-identical mirror (`cp docs/convention.md …`) |

### Actions Taken
- Added the subsection: project = metadata not a directory; root-relative
  `Related:` ⇒ redundant `<subdir>/` prefix when a lone project is nested;
  single-project default (root = project, flat, clean refs, citing this
  repo's `docs/`); multi-project (one root + `Project:` metadata, subdirs
  optional); explicit "do not nest a lone project under a parent root";
  ties back to the M3 INDEX-groups-by-Project decision.
- `docs touch docs/convention.md` then `cp` to the bundle.

### Test Results
- `diff docs/convention.md src/docs_cli/skill/references/convention.md` →
  IDENTICAL (parity gate, `tests/test_skill_refs.py`).

## Phase 7 — Update Tool/Wrapper Layer (2026-06-24)

### Objective
Add the user-facing "Where to put `.docs.toml`" note to the bundled SKILL.md.

### Files Changed
| File | Action | Notes |
|------|--------|-------|
| src/docs_cli/skill/SKILL.md | modified | concise placement note after the cwd-fallback paragraph, pointing at references/convention.md |

### Actions Taken
- Added the note (project = metadata not a directory; root = project; nesting
  a lone project ⇒ redundant prefix; group by `Project:` not folder), wrapped
  to match SKILL.md style; link `](references/convention.md)` resolves and is
  not parent-relative.

## Phase 8 — Run Tests (GREEN) (2026-06-24)

### Objective
Full suite + quality gate green, including the new pinning test and the parity
test.

### Files Changed
| File | Action | Notes |
|------|--------|-------|
| tests/fixtures/expected/docs-INDEX.md | modified | dogfood-snapshot refresh: the frozen `docs index` acceptance fixture now reflects the added M22 pair (delta verified to be the M22 entries + bumped `Updated:`/active-count on touched docs + `convention.md` correctly sorting above `cli.md` in the Spec group after its 2026-06-24 touch (within-group order is `Updated` descending, then path ascending) — no broken links) |

### Actions Taken
- Ran the M22 test (3 passed), the skill suite (17 passed), then the full
  suite. One expected failure surfaced — `test_index_output_matches_frozen_
  snapshot` — because adding M22 changed the real `docs/` tree the dogfood
  guard mirrors; refreshed the fixture from the freshly-generated INDEX.

### Test Results (verbatim)
```
$ .venv/bin/python -m pytest tests/ -q
543 passed in 24.05s
$ .venv/bin/ruff check .            → All checks passed!
$ .venv/bin/ruff format --check .   → 40 files already formatted
$ .venv/bin/mypy                    → Success: no issues found in 41 source files
$ .venv/bin/docs check docs/        → no violations found (exit 0)
```

## Phase 9 — Implement Online/Integration (dogfood) (2026-06-24)

### Objective
No online surface — dogfood the guidance by reproducing, in throwaway trees,
the exact behavior the new docs describe.

### Actions Taken
Built two trees and ran the read-only `docs check`:

1. **Anti-pattern** — parent root `specs/.docs.toml` + single nested project
   `specs/demo/` (charter + scope). The natural sibling edge
   `pairs-with: scope.md` **fails**:
   `error: [broken-ref] Related: target does not resolve to a file: scope.md`
   (exit 2) — root-relative resolution looks for `specs/scope.md`. It passes
   only after rewriting to the **redundant** `pairs-with: demo/scope.md`.
2. **Recommended** — root IS the project dir (`demo/.docs.toml`). The same
   natural edge `pairs-with: scope.md` resolves and `docs check` exits 0 — no
   prefix needed.

### Test Results
- Anti-pattern, clean sibling ref → exit 2 (broken-ref).
- Anti-pattern, `demo/`-prefixed ref → exit 0.
- Recommended layout, clean sibling ref → exit 0.

This is precisely the redundant-prefix consequence the convention.md
subsection and the SKILL.md note now warn about — the guidance matches tool
behavior. (Throwaway trees under the session scratchpad; the repo tree was
untouched.)

## Phase 10 — Quality, Docs, Refactor (2026-06-24)

### Objective
Final gate, CHANGELOG, surface-parity reconciliation, completion summaries.

### Files Changed
| File | Action | Notes |
|------|--------|-------|
| CHANGELOG.md | modified | new `## 1.7.0 — UNRELEASED` › Documentation entry for M22 (OQ-1 confirmed: stage here, no version bump) |
| docs/m22-root-placement-guidance.md | modified | milestone-completion summary appended |
| docs/m22-root-placement-guidance-impl.md | modified | this section |

### Actions Taken
- OQ-1 **confirmed** as the recommended default: M22 logged under `## 1.7.0 —
  UNRELEASED`; `pyproject.toml` version untouched (stays 1.6.5; M21 owns the
  1.7.0 build; version is `importlib.metadata`-sourced).
- Surface-parity reconciliation: **no CLI verb/flag/behavior changed**, so no
  argparse `--help` reconciliation is needed; the only surface is the bundled
  skill, and `references/convention.md` is byte-identical to `docs/convention.md`.
- Refactor/simplify: not applicable — documentation-only change, prose already
  minimal and matches each file's house style.
- Appended milestone-completion summaries to both docs.

### Test Results (final gate)
```
$ .venv/bin/python -m pytest tests/ -q   → 543 passed
$ .venv/bin/ruff check .                  → All checks passed!
$ .venv/bin/ruff format --check .         → all files formatted
$ .venv/bin/mypy                          → Success
$ .venv/bin/docs check docs/              → no violations found (exit 0)
```
(Re-confirmed after the Phase-10 doc touches below.)

## Milestone-completion summary

M22 complete (2026-06-24), all ten phases. Documentation-only: convention.md
§Subdirectories + bundled SKILL.md now teach where to put `.docs.toml`
(project = metadata, not a directory; root-relative refs ⇒ redundant prefix
when a lone project is nested; default root = project dir). RED-first test
`tests/test_skill_root_placement.py` (3 tests); bundled reference mirrored
byte-identical; dogfood-snapshot refreshed; CHANGELOG staged under 1.7.0
UNRELEASED. No CLI change, no version bump. Full suite 543 GREEN, gate clean,
`docs check docs/` exit 0. Companion `project-foundation` note tracked
separately in `agent-playbook-suite`. Ready to archive with `--cascade`.

## Fresh-eyes review (2026-06-26)

Independent reviewer (ship-milestone gate, run retroactively because M22 was
built as a single commit outside the branch-stack flow). Verdict: **sound — no
blockers, no should-fixes.** The central redundant-prefix claim was verified
against the resolution code (`cli.py` root-relative `Related:` check) and
empirically in throwaway trees; the RED baseline was genuine; the three
surfaces are consistent; SKILL.md/parity invariants hold; the dogfood-fixture
delta was M22-only.

Three nits surfaced; resolution:
- **Finding 1 (impl-log accuracy) — fixed.** The Phase-8 fixture note claimed
  "no reordering"; corrected — `convention.md` sorts above `cli.md` in the Spec
  group after its 2026-06-24 touch (within-group order: `Updated` desc, path asc).
- **Finding 2 (test strength) — fixed.** The consequence claim was pinned only
  by the word "redundant"; added `assert "<subdir>/" in ...` to all three pin
  tests (genuine discriminator — absent in every surface before M22). Contract
  amendment to the Phase-1 pin set, recorded here.
- **Finding 3 (multi-project wording) — DEFERRED (operator).** convention.md's
  multi-project note ("only then do prefixed references reflect a genuine
  cross-folder path") could read as if only cross-folder refs need a prefix; a
  same-folder intra-project sibling in a multi-project tree with per-project
  subdirs still needs the `<subdir>/` prefix. A convention-spec clarity edit —
  per operator policy it goes through a test-first milestone, not an ad-hoc edit
  — so left for the operator to schedule. The lone-project teaching (M22's
  actual scope) is correct and unaffected.
