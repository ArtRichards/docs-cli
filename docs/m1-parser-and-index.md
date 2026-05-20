# M1 — Parser and `docs index`

Status: done
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
- Status: COMPLETE (2026-05-20)

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

- [x] `bin/docs` executable (Python 3.11+, single file, stdlib only) with `index` subcommand functional.
- [x] `pyproject.toml` (project metadata, dev dependencies: pytest, ruff, mypy).
- [x] `tests/test_model.py`, `tests/test_walker.py`, `tests/test_index.py`, `tests/test_config.py`, `tests/test_cli_index.py`.
- [x] `tests/fixtures/` with `minimal/`, `with-archive/`, `marker-preservation/` trees.
- [x] Dogfood: `./bin/docs index docs/` produces output matching the reconciled snapshot byte-for-byte (Phase 9 reconciled hand-authored snapshot to spec-compliant output; live `docs/INDEX.md` regenerates idempotently).
- [x] All quality gates green: `ruff check .`, `ruff format --check .`, `mypy bin/docs`, `pytest -q`.
- [x] `docs/status.md` updated to reflect M1 complete + M2 active.

## Current state analysis (snapshot at milestone kickoff, 2026-05-20)

_Captured before Phase 1; historical. Post-milestone state lives in the
Milestone-completion summary at the bottom of this file._

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

> _Deviation: `Vocab` dataclass was not added — `Config.statuses` / `Config.roles` already carry the merged vocab and no consumer needed a standalone `Vocab` value in M1. See the Phase 5 log entry for rationale._

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
- **Exit:** `./bin/docs index --help` prints usage. `./bin/docs index tests/fixtures/trees/minimal` runs without error. `tests/test_cli_index.py` green.

### Phase 8: Run Tests (GREEN)

- **Objective:** Full suite passing; quality gates clean.
- **Actions:** `pytest -q tests/`; `ruff check`; `ruff format --check`; `mypy bin/docs`.
- **Exit:** All four commands exit 0. Any deferred TODOs documented in log.

### Phase 9: Dogfood pass (mapped from "Online/Integration")

- **Objective:** Run `./bin/docs index docs/` against this repo's own docs root; reconcile any drift between hand-written and generated INDEX.md.
- **Actions:**
  - `./bin/docs index docs/` — capture output.
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
- [x] Phase 3: Create Data/Fixtures
- [x] Phase 4: Run Tests (RED Baseline)
- [x] Phase 5: Update Base Interfaces
- [x] Phase 6: Implement Offline/Core Path
- [x] Phase 7: Update Tool/Wrapper Layer
- [x] Phase 8: Run Tests (GREEN)
- [x] Phase 9: Dogfood pass (Online/Integration mapping)
- [x] Phase 10: Quality, Docs, Refactor

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
mypy bin/docs
pytest -q
./bin/docs index docs/   # dogfood smoke
```

Expected at Phase 10: all commands exit 0. Dogfood produces zero diff against the committed `docs/INDEX.md`.

## Success Criteria

M1 is complete when:

- [x] All Phase Checklist items are checked.
- [x] The `docs` executable is committed, executable, and works from `~/bin/docs` (or wherever symlinked).
- [x] All deliverables above are checked off.
- [x] `./bin/docs index docs/` reproduces this repo's `docs/INDEX.md` (and matches the spec-compliant snapshot in `tests/fixtures/expected/docs-INDEX.md` byte-for-byte).
- [x] [status.md](status.md) reflects M1 → Complete, M2 → ACTIVE.
- [x] [m1-parser-and-index-log.md](m1-parser-and-index-log.md) contains a milestone-completion summary.

## Milestone-completion summary

**Shipped:** 2026-05-20.

**Code (single file).** `bin/docs` (~520 lines, stdlib only, Python 3.11+):
- Dataclasses `Doc` and `Config` with `__post_init__` invariants.
- Exception classes `MetadataError`, `VocabularyError`.
- Utilities `parse_date`, `validate_status`, `validate_role`, `parse_metadata_block`, `atomic_write`, `_find_marker_lines`.
- Public API: `parse`, `walk`, `render_index`, `load_config`, `find_root`.
- CLI: `docs index [DIR] [--root R] [--quiet] [--dry-run]` with exit-code dispatch per `cli.md`.

**Tests (58 total, 100% passing).**
- `tests/test_model.py` (16) — parser unit tests.
- `tests/test_walker.py` (9) — directory traversal.
- `tests/test_index.py` (14) — renderer unit tests (1 new regression test from Phase 9).
- `tests/test_config.py` (12) — config + find_root.
- `tests/test_cli_index.py` (7) — end-to-end subprocess tests.

**Fixtures.** `tests/fixtures/parser/well-formed.md`, three `trees/{minimal,with-archive,marker-preservation}/` directories, and the dogfood snapshot at `tests/fixtures/expected/docs-INDEX.md`.

**Quality gates clean.** `ruff check .`, `ruff format --check .`, `mypy bin/docs`, `pytest -q` — all exit 0.

**Lessons compounded.**
- **Hand-authored snapshots before implementation are aspirational, not authoritative.** The original `tests/fixtures/expected/docs-INDEX.md` had hand-curated descriptions that didn't match any derivable source; Phase 9 reconciled it against the spec.
- **Substring matching is brittle when content can mention the substring.** The original marker detection split on `MARKER_START` anywhere — corrupted by the preamble's backtick-quoted prose mention. The fix (`_find_marker_lines`) anchors matching to whole lines.
- **Repo-wide quality gates catch what file-scoped ones miss.** Phases 1–7 ran ruff/mypy only on `bin/docs`; Phase 8 found tests/ lint debt that had been quietly accumulating.
- **The 10-phase TDD cycle worked.** Each phase had a clear exit criterion; the log entries make resumption from any phase cheap. Carry forward into M2.

**Files added during M1.**
- `bin/docs`, `pyproject.toml`, `tests/conftest.py`, five test files, 15 fixture files.
- `docs/m1-parser-and-index.md`, `docs/m1-parser-and-index-log.md`.
- `docs/architecture.md` updated with the INDEX renderer-format subspec and the file-location correction.

**Next.** M2 — mutating verbs (`new`, `archive`, `mv`, `touch`). All four will reuse `atomic_write` + the `parse`/`walk` core; the argparse harness in `main()` extends naturally to additional subparsers.
