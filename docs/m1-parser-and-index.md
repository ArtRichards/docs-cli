# M1 — Parser and `docs index`

Status: active
Role: milestone
Project: docs
Updated: 2026-05-20

Related:
- parent-of: m1-parser-and-index-log.md
- child-of: plan.md
- implements: charter.md
- pairs-with: convention.md
- pairs-with: cli.md
- pairs-with: architecture.md
- pairs-with: test-strategy.md

## Overview

- Milestone: M1
- Title: Parser and `docs index`
- Surface: Python module `docs`, CLI subcommand `docs index`
- Status: ACTIVE

### Goal

Read the on-disk convention reliably and produce a usable INDEX.md. This is the foundational milestone — every later verb (archive, mv, check, list, migrate) depends on the parser + walker.

### Requirements

- Parse a single Markdown file into a `Doc` value with all metadata extracted.
- Walk a docs root, yielding `Doc` instances; distinguish active tree from archive subtree.
- Load `.docs.toml` config; merge vocabulary additions into built-in set.
- Render INDEX.md with marker-block preservation; idempotent output.
- CLI subcommand `docs index [DIR]` wires walker + renderer; resolves root via `--root` or upward search for `.docs.toml`.
- No mutating verbs in this milestone (those are M2).
- Exit codes per [cli.md](cli.md).

### Deliverables

- [ ] `bin/docs` executable (Python 3.11+, single file, stdlib only) with `index` subcommand functional.
- [ ] `pyproject.toml` (project metadata, dev dependencies: pytest, ruff, mypy).
- [ ] `tests/test_model.py`, `tests/test_walker.py`, `tests/test_index.py`, `tests/test_cli_index.py`.
- [ ] `tests/fixtures/` with `minimal/`, `with-archive/`, `marker-preservation/` trees.
- [ ] Dogfood: `./docs index docs/` produces output that matches the hand-written `docs/INDEX.md` byte-for-byte (or with a diff small enough to review and intentionally accept).
- [ ] All quality gates green: `ruff check`, `ruff format --check`, `mypy docs`, `pytest -q`.
- [ ] `docs/status.md` and `docs/plan.md` updated to reflect M1 complete.

## Current state analysis

- **Existing code:** none. No `docs` executable, no `tests/` content beyond `.gitkeep`.
- **Existing docs:** charter, convention, cli, plan, architecture, test-strategy, vocab-adr, dual-status-adr, INDEX, definition-of-ready, status, this file. All authored manually.
- **Missing:** every line of source code; the entire test suite; `pyproject.toml`.
- **Known issues:** none. The hand-written INDEX.md must be reproducible by the tool — if M1's generated output diverges, we reconcile by editing whichever is wrong.

## TDD Implementation Plan

### Phase 1: Define Contract

- **Objective:** Specify types, signatures, exceptions. No implementation.
- **Files:**
  - `docs` (executable) — top of file: `Doc` dataclass, `Vocab` dataclass, `Config` dataclass, exception classes (`MetadataError`, `VocabularyError`), function signatures (`parse`, `walk`, `render_index`, `load_config`, `find_root`, `main`).
- **Exit:** Types compile under `python -c "import docs"` (or equivalent ast parse). No business logic. Docstrings reference [convention.md](convention.md) for semantics.

### Phase 2: Write Tests (RED)

- **Objective:** Express every required behavior as a failing test.
- **Files:**
  - `tests/test_model.py` — parser happy path, missing H1, missing required field, malformed Updated, unknown vocab value, multi-value Related, extra labels harvested.
  - `tests/test_walker.py` — yields docs in deterministic order, excludes non-md, distinguishes active vs archive.
  - `tests/test_index.py` — renders expected sections, preserves marker-block context, idempotent on re-run, handles missing INDEX.md.
  - `tests/test_cli_index.py` — invokes `docs index` via subprocess on each fixture tree; exit code 0; output diff matches expectation.
- **Exit:** Tests import without errors and fail with `NotImplementedError` or `AttributeError` (not configuration errors).

### Phase 3: Create Data/Fixtures

- **Objective:** Hand-built sample trees and inline-string fixtures covering every variant.
- **Files:**
  - `tests/fixtures/trees/minimal/` — one doc, one INDEX.md placeholder, no archive subtree.
  - `tests/fixtures/trees/with-archive/` — 3 active docs (charter/spec/plan roles), 2 archived docs under `archive/2026-01-01/`.
  - `tests/fixtures/trees/marker-preservation/` — INDEX.md with hand-edited preamble before markers + trailer after.
  - `tests/fixtures/parser/` — directory of single-doc samples for parser tests (well-formed, missing-h1, missing-status, malformed-related, etc.).
- **Exit:** Fixtures load via `pathlib.Path.read_text()`. Walk over `with-archive/` yields exactly 5 docs in deterministic order.

### Phase 4: Run Tests (RED Baseline)

- **Objective:** Confirm failures are due to missing implementation, not misconfigured tests.
- **Actions:** `pytest -q tests/` — capture full output.
- **Exit:** Every assertion failure traces to a `NotImplementedError`, missing function body, or absent attribute. No `ImportError`, no fixture-loading errors, no path errors.

### Phase 5: Update Base Interfaces

- **Objective:** Lock in `Doc`, `Vocab`, `Config` dataclasses with `__post_init__` validation hooks. Provide shared utilities (`parse_date`, `validate_vocab_value`, `find_root`).
- **Files:** `docs` (executable), top of file.
- **Exit:** `python -c "from docs import Doc, Vocab, Config; ..."` succeeds. Importable from tests without errors.

### Phase 6: Implement Offline/Core Path

- **Objective:** Implement parser, walker, render_index. Make unit tests pass.
- **Files:** `docs` (executable), respective sections.
- **Exit:** All `tests/test_model.py`, `tests/test_walker.py`, `tests/test_index.py` green. CLI tests still failing (`main` not wired).

### Phase 7: Update Tool/Wrapper Layer

- **Objective:** Wire `main()` with argparse; resolve `--root`; dispatch `index` subcommand; exit-code handling.
- **Files:** `docs` (executable), bottom of file.
- **Exit:** `./docs index --help` prints usage. `./docs index tests/fixtures/trees/minimal` runs without error. `tests/test_cli_index.py` green.

### Phase 8: Run Tests (GREEN)

- **Objective:** Full suite passing; quality gates clean.
- **Actions:** `pytest -q tests/`; `ruff check`; `ruff format --check`; `mypy docs`.
- **Exit:** All four commands exit 0. Any deferred TODOs documented in log.

### Phase 9: Dogfood pass (mapped from "Online/Integration")

- **Objective:** Run `./docs index docs/` against this repo's own docs root; reconcile any drift between hand-written and generated INDEX.md.
- **Actions:**
  - `./docs index docs/` — capture output.
  - `diff docs/INDEX.md <generated>` — if diff exists, decide: edit the hand-written file to match the tool, edit the tool to match the hand-written file, or split the difference and document why.
- **Exit:** Hand-written INDEX.md reproduces under `docs index` with no diff, or the surviving diff is documented in the log as intentional and consistent across runs.

### Phase 10: Quality, Docs, Refactor

- **Objective:** Final polish, docs updated, M1 marked complete.
- **Actions:**
  - Run full quality gate (see Phase 8).
  - Refactor any code that's grown past the readable budget.
  - Update [status.md](status.md): set M1 to Complete, M2 to ACTIVE; update Current Milestone block.
  - Update [plan.md](plan.md) if the M1 work surfaced changes to the M2-M5 plan.
  - Append milestone-completion summary to [m1-parser-and-index-log.md](m1-parser-and-index-log.md).
  - Append the milestone-completion summary to this file (lessons learned, files added).
- **Exit:** Quality gate green; docs updated; ready to start M2.

## Phase Checklist

- [x] Phase 1: Define Contract
- [x] Phase 2: Write Tests (RED)
- [ ] Phase 3: Create Data/Fixtures
- [ ] Phase 4: Run Tests (RED Baseline)
- [ ] Phase 5: Update Base Interfaces
- [ ] Phase 6: Implement Offline/Core Path
- [ ] Phase 7: Update Tool/Wrapper Layer
- [ ] Phase 8: Run Tests (GREEN)
- [ ] Phase 9: Dogfood pass (Online/Integration mapping)
- [ ] Phase 10: Quality, Docs, Refactor

## Decisions

Key choices applying to this milestone (broader decisions live in `vocab-adr.md` and `dual-status-adr.md`):

- **Phase 9 mapping.** Standard methodology calls Phase 9 "Implement Online/Integration"; we have no network surface in M1. Repurposed as the dogfood pass — running the tool against its own `docs/` root is the realistic integration test for M1.
- **Single-file budget.** Aim for the `docs` executable to stay under ~500 lines for M1. If it exceeds, defer non-essential refinements rather than splitting the file (split decision lives in M3).
- **Marker-block format.** Locked to `<!-- docs:generated start -->` / `<!-- docs:generated end -->` — verbatim. The renderer matches these strings exactly; no regex with variant whitespace.

## Testing / Quality Gate

Commands run at Phase 8 and Phase 10:

```
ruff check .
ruff format --check .
mypy docs
pytest -q
./docs index docs/   # dogfood smoke
```

Expected at Phase 10: all commands exit 0. Dogfood produces zero diff against the committed `docs/INDEX.md`.

## Success Criteria

M1 is complete when:

- All Phase Checklist items are checked.
- The `docs` executable is committed, executable, and works from `~/bin/docs` (or wherever symlinked).
- All deliverables above are checked off.
- `./docs index docs/` reproduces this repo's `docs/INDEX.md`.
- [status.md](status.md) reflects M1 → Complete, M2 → ACTIVE.
- [m1-parser-and-index-log.md](m1-parser-and-index-log.md) contains a milestone-completion summary.
