# M12 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-05-28

Related:
- child-of: m12-project-rename.md
- pairs-with: m12-project-rename.md
- pairs-with: status.md

## Overview

Chronological log of work on M12 — Project rename verb + M11
wart fixes + version SoT (v1.5.0). Append a section per TDD
phase (Contract → Tests → Fixtures → RED → Base interfaces →
Core path → Tool/Wrapper → GREEN → Dogfood → Quality/Docs/
Refactor) with objective, actions, results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M12 — Project rename verb + M11 wart fixes +
  version SoT (v1.5.0)
- Started: 2026-05-28
- Progress: **Phase 1 (Contract) opens after operator triages
  OQ-A through OQ-D from the milestone doc.**

(Note: doc-lifecycle status is in the front-matter `Lifecycle:`
field above. This section tracks milestone-implementation
progress, which is distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Pending | — | |
| 2. Write Tests (RED) | Pending | — | |
| 3. Create Data/Fixtures | Pending | — | |
| 4. Run Tests (RED Baseline) | Pending | — | |
| 5. Update Base Interfaces | Pending | — | |
| 6. Implement Offline/Core Path | Pending | — | |
| 7. Update Tool/Wrapper Layer | Pending | — | |
| 8. Run Tests (GREEN) + quality gate | Pending | — | |
| 9. Dogfood | Pending | — | |
| 10. Quality, Docs, Refactor | Pending | — | |

## Current state analysis (snapshot at milestone kickoff, 2026-05-28)

_Captured before Phase 1; historical._

- **Codebase (1.4.0 shipped on PyPI):** `src/docs_cli/cli.py`
  post-M11; 401 passing tests across 24 files; ruff / format /
  mypy clean tree-wide; `docs check docs/` exit 0.
- **What M12 inherits:**
  - `docs-cli==1.4.0` live at
    https://pypi.org/project/docs-cli/1.4.0/.
  - `pyproject.toml` `version = "1.4.0"`, `src/docs_cli/cli.py`
    `__version__ = "1.4.0"` (hardcoded literal — M12 replaces
    with `importlib.metadata.version("docs-cli")`),
    `tests/test_packaging.py` A3 pinned at `1.4.0`.
  - `docs touch <file>` outside any docs root currently
    inserts an unwanted `Updated:` line and crashes the
    downstream INDEX refresh on whatever sibling first fails
    its Lifecycle check. The M11 Phase 5 closeout caught this
    by accident.
  - `docs archive <doc>` moves the doc to `archive/<date>/`
    and sets `Lifecycle: archived` but does **not** rewrite
    referring `Related:` edges in other docs. Operator runs
    a manual `Related:` cleanup post-archive (M11 Phase 5
    did this for `status.md` + impl log).
  - `docs project rename` does not exist; renaming a `docs`
    root's `[project] name` requires hand-editing every
    conformant `Project:` line + the `.docs.toml` sidecar +
    regenerating INDEX. The M10 follow-on TODO captured the
    full target spec at
    [archive/2026-05-27/m10-adoption-polish.md](archive/2026-05-27/m10-adoption-polish.md)
    lines 261-268.
- **What M12 produces:**
  - `docs project rename <new-name>` verb (new namespace).
  - `docs touch` outside-docs-root graceful refusal (exit 2).
  - `docs archive` referring-edge rewrite (atomic with move).
  - `__version__` sourced from `importlib.metadata`.
  - `pyproject.toml` `version = "1.5.0"`,
    `test_packaging.py` A3 → `1.5.0`,
    `CHANGELOG.md ## 1.5.0 — UNRELEASED` entry authored with
    publish-survival wording (M11 lesson).
  - `dist/docs_cli-1.5.0-*` built locally; `twine check` PASS.
  - NO PyPI publish — that's M13's scope.

## Phase 1 — Define Contract

_Not started. Opens after OQ-A through OQ-D are triaged into
Decisions._

## Phase 2 — Write Tests (RED)

_Not started._

## Phase 3 — Create Data/Fixtures

_Not started._

## Phase 4 — Run Tests (RED Baseline)

_Not started._

## Phase 5 — Update Base Interfaces

_Not started._

## Phase 6 — Implement Offline/Core Path

_Not started._

## Phase 7 — Update Tool/Wrapper Layer

_Not started._

## Phase 8 — Run Tests (GREEN) + quality gate

_Not started._

## Phase 9 — Dogfood

_Not started._

## Phase 10 — Quality, Docs, Refactor

_Not started._
