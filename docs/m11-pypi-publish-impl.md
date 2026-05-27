# M11 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-05-27

Related:
- child-of: m11-pypi-publish.md
- pairs-with: m11-pypi-publish.md
- pairs-with: release-runbook.md
- pairs-with: status.md

## Overview

Chronological log of work on M11 — PyPI publish `docs-cli` 1.4.0.
Append a section per phase (Operator prep → Pre-publish prep →
TestPyPI rehearsal → Real PyPI publish → Post-release) with
objective, actions, results, deviations, decisions. Mirrors the
M9 impl-log shape exactly.

## Implementation metadata

- Project: docs
- Milestone: M11 — PyPI publish `docs-cli` 1.4.0
- Started: 2026-05-27
- Progress: **Phase 1 opens immediately — M10 Phase 10 already
  built fresh 1.4.0 artefacts that pass `twine check`; M11
  awaits operator publish-window.**

(Note: doc-lifecycle status is in the front-matter `Lifecycle:`
field above. This section tracks milestone progress, which is
distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Operator one-time prep | Pending | — | |
| 2. Pre-publish prep | Pending | — | |
| 3. TestPyPI rehearsal | Pending | — | |
| 4. Real PyPI publish | Pending | — | |
| 5. Post-release | Pending | — | |

(M11 has no TDD code phases — it is an operational milestone.
The five rows above mirror the [release-runbook.md](release-runbook.md)
sections.)

## Current state analysis (snapshot at milestone kickoff, 2026-05-27)

_Captured before Phase 1; historical._

- **Codebase (1.4.0 ready locally, not on PyPI):** `src/docs_cli/cli.py`
  post-M10; 401 passing tests across 24 files; ruff / format / mypy
  clean tree-wide; `docs check docs/` exit 0.
- **What M11 inherits:**
  - `dist/docs_cli-1.4.0-py3-none-any.whl` + `dist/docs_cli-1.4.0.tar.gz`
    built at M10 Phase 10 (post-closeout-commit state); `twine check`
    PASS. M11 will rebuild fresh from post-merge-to-main HEAD per
    discipline.
  - `pyproject.toml` `version = "1.4.0"`, `src/docs_cli/cli.py`
    `__version__ = "1.4.0"`, `tests/test_packaging.py` pins at
    `1.4.0` — landed at M10 Phase 7.
  - `CHANGELOG.md` `## 1.4.0 — 2026-05-27 (LOCAL; not on PyPI)`
    landed at M10 Phase 10. The "(LOCAL; not on PyPI)" suffix gets
    dropped at M11 publish time; the date gets verified or bumped
    to the actual publish day.
  - M9 operator state: PyPI + TestPyPI accounts registered, 2FA
    active, `~/.pypirc` carrying API tokens (entire-account scoped
    pending M9 open follow-on for project re-scope).
  - M9 TestPyPI detour: bare `docs-cli` name parked by squatter;
    rehearsal runs under `docs-cli-rehearsal==1.4.0` unless
    ownership changed since 2026-05-25.
- **What M11 produces:**
  - `docs-cli==1.4.0` live on PyPI.
  - `v1.4.0` git tag + GitHub release.
  - Final doc closeouts (M10 + M11 rows in plan.md/status.md;
    INDEX + dogfood snapshot in lockstep).

## Phase 1 — Operator one-time prep

_Not started._

## Phase 2 — Pre-publish prep

_Not started._

## Phase 3 — TestPyPI rehearsal

_Not started._

## Phase 4 — Real PyPI publish

_Not started._

## Phase 5 — Post-release

_Not started._
