# M13 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-05-29

Related:
- child-of: m13-pypi-publish.md
- pairs-with: m13-pypi-publish.md
- pairs-with: status.md

## Overview

Chronological log of work on M13 — PyPI publish 1.5.0.
Append a section per runbook phase (operator prep → pre-publish
prep → TestPyPI rehearsal → real PyPI publish → post-release)
with objective, actions, results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M13 — PyPI publish 1.5.0
- Started: 2026-05-29
- Progress: **Milestone doc + log created 2026-05-29**
  (m13/milestone-setup). Phase 1 (operator one-time prep)
  opens in the next session via `/ship-milestone M13` (which
  for an operational publish milestone walks the
  release-runbook rather than the 10-phase TDD cycle).

(Note: doc-lifecycle status is in the front-matter `Lifecycle:`
field above. This section tracks milestone-implementation
progress, which is distinct.)

## Runbook Phase Progress

M13 has no TDD code phases — the runbook's sections are the
phases (mirrors M9/M11).

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Operator one-time prep | Pending | — | |
| 2. Pre-publish prep | Pending | — | |
| 3. TestPyPI rehearsal | Pending | — | |
| 4. Real PyPI publish | Pending | — | |
| 5. Post-release | Pending | — | |

## Current state analysis (snapshot at milestone kickoff, 2026-05-29)

_Captured before Phase 1; historical._

- **Codebase (1.5.0 ready locally; 1.4.0 shipped on PyPI):**
  `src/docs_cli/cli.py` post-M12; 433 passing tests across
  25 files; ruff / format / mypy clean tree-wide; `docs check
  docs/` exit 0; `dist/docs_cli-1.5.0-py3-none-any.whl` +
  `dist/docs_cli-1.5.0.tar.gz` built at M12 Phase 8 and pass
  `twine check`.
- **What M13 inherits:**
  - `docs-cli==1.4.0` live at
    https://pypi.org/project/docs-cli/1.4.0/ from M11
    (2026-05-27).
  - `pyproject.toml` `version = "1.5.0"` (bumped M12 Phase 7);
    `src/docs_cli/cli.py` `__version__` reads through
    `importlib.metadata.version("docs-cli")` per M12 SoT
    refactor; `tests/test_packaging.py` A3 pinned at `1.5.0`.
  - `CHANGELOG.md` `## 1.5.0 — UNRELEASED` entry already
    authored with publish-survival wording (M11 lesson —
    no "ready locally" / "deferred to MX" suffixes); runbook
    step at Phase 4 is to drop `UNRELEASED` and replace with
    publish date.
  - `~/.pypirc` carries the M9-era PyPI + TestPyPI API tokens
    (entire-account scope; re-scope to project-`docs-cli`
    remains an open follow-on rolling forward from M9 →
    M11 → M13).
  - TestPyPI `docs-cli` is parked by the M9-era squatter at
    0.1.0; M13 will continue the `docs-cli-rehearsal` detour
    that M9/M11 established. Re-check ownership at Phase 1.
  - GitHub repo `ArtRichards/docs-cli` is public from M9;
    `v1.4.0` tag + GitHub release exist from M11.
- **What M13 produces:**
  - `docs-cli==1.5.0` published on PyPI.
  - `docs-cli-rehearsal==1.5.0` published on TestPyPI as the
    rehearsal artifact.
  - `v1.5.0` git tag pushed.
  - GitHub release at the v1.5.0 tag, notes sourced from
    `## 1.5.0`.
  - Post-publish doc closeouts (M12 + M13 rows finalised in
    `status.md` + `plan.md`; INDEX + dogfood snapshot
    regenerated in lockstep).
  - Milestone-completion summary with sha256 + publish
    timestamp + any deviations recorded for v1.6+.

## Phase 1 — Operator one-time prep

_Not started. Opens via `/ship-milestone M13`._

## Phase 2 — Pre-publish prep

_Not started._

## Phase 3 — TestPyPI rehearsal

_Not started._

## Phase 4 — Real PyPI publish

_Not started._

## Phase 5 — Post-release

_Not started._
