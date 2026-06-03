# M17 — Implementation Log

Lifecycle: draft
Role: log
Project: docs
Updated: 2026-06-03

Related:
- child-of: m17-pypi-publish.md
- pairs-with: m17-pypi-publish.md
- pairs-with: status.md

## Overview

Chronological log of work on M17 — PyPI publish 1.6.0. Append a
section per runbook phase (operator prep → pre-publish prep →
TestPyPI rehearsal → real PyPI publish → post-release) with
objective, actions, results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M17 — PyPI publish 1.6.0
- Started: 2026-06-03 (milestone-setup)
- Progress: **Setup — authorized, not yet executed.** M14 + M15
  are both implementation-complete, each building
  `docs-cli==1.6.0` locally; M17 is the operator-driven publish
  that ships them together. The operator has **authorized** a
  fully-autonomous run including the irreversible real-PyPI
  upload + `main` push + `v1.6.0` tag + GitHub release (Step 0
  resolution of OPEN QUESTION Q1 — see the milestone doc's
  Decisions). The publish itself has **not** run yet — it runs
  after this milestone-setup commit, with the five runbook phases
  in one pass (the conductor drives the release-runbook directly,
  since an operational publish milestone has no 10-phase TDD
  cycle).

(Note: doc-lifecycle status is in the front-matter `Lifecycle:`
field above. This section tracks milestone-implementation
progress, which is distinct.)

## Runbook Phase Progress

M17 has no TDD code phases — the runbook's sections are the
phases (mirrors M9/M11/M13).

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Operator one-time prep | Pending | — | — |
| 2. Pre-publish prep | Pending | — | — |
| 3. TestPyPI rehearsal | Pending | — | — |
| 4. Real PyPI publish | Pending | — | — |
| 5. Post-release | Pending | — | — |

## Current state analysis (snapshot at milestone kickoff, 2026-06-03)

_Captured before Phase 1; historical._

- **Codebase (1.6.0 ready locally; 1.5.0 shipped on PyPI):**
  `src/docs_cli/cli.py` post-M14/M15 (the full
  `index/new/archive/mv/touch/stamp/project/check/list/migrate/install-skill`
  verb surface); the suite was 510 GREEN at M18's
  implementation-complete state; ruff / format / mypy clean
  tree-wide; `docs check docs/` exit 0. The repo `dist/`
  currently holds the **stale 1.5.0** artefacts from M13
  (`docs_cli-1.5.0-py3-none-any.whl` + `docs_cli-1.5.0.tar.gz`);
  M17 Phase 2 clears them with `rm -rf dist/` and builds fresh
  1.6.0 artefacts.
- **What M17 inherits:**
  - `docs-cli==1.5.0` live at
    https://pypi.org/project/docs-cli/1.5.0/ from M13
    (2026-05-29).
  - `pyproject.toml` `version = "1.6.0"` (bumped M14 Phase 7);
    `src/docs_cli/cli.py` `__version__` reads through
    `importlib.metadata.version("docs-cli")` per the M12 SoT
    refactor; `tests/test_packaging.py` A3 pinned at `1.6.0`.
  - `CHANGELOG.md` `## 1.6.0 — UNRELEASED` entry already
    authored with publish-survival wording (M14 opened the
    section; M15 appended its `Added`/`Changed`/`Fixed`
    authoring entries; M18's edge fix folded an entry in too);
    the runbook step at Phase 4 is to drop `UNRELEASED` and
    replace with publish date.
  - `~/.pypirc` (mode 600) carries the M9-era PyPI + TestPyPI
    API tokens (entire-account scope; re-scope to
    project-`docs-cli` remains an open follow-on rolling forward
    from M9 → M11 → M13 → M17).
  - TestPyPI `docs-cli` is parked by the M9-era squatter at
    0.1.0; M17 will continue the `docs-cli-rehearsal` detour
    that M9/M11/M13 established. Re-check ownership at Phase 1.
  - GitHub repo `ArtRichards/docs-cli` is public from M9;
    tags exist through `v1.5.0` (the M13 tag); `v1.6.0` does
    not yet exist.
  - **Two M13 deviations, now known-expected:** the TestPyPI
    rehearsal wheel prints `docs 0.0.0+local` under the rename
    detour; `CHANGELOG.md` is not in the sdist. Both are folded
    into the release-runbook already.
- **What M17 produces:**
  - `docs-cli==1.6.0` published on PyPI.
  - `docs-cli-rehearsal==1.6.0` published on TestPyPI as the
    rehearsal artifact.
  - `v1.6.0` git tag pushed.
  - GitHub release at the v1.6.0 tag, notes sourced from
    `## 1.6.0`.
  - Post-publish doc closeouts (M14 + M15 + M17 rows finalised
    in `status.md` + `plan.md`; M14 + M15 milestone docs
    archived; INDEX + dogfood snapshot regenerated in lockstep).
  - Milestone-completion summary with sha256 + publish timestamp
    + any deviations recorded for v1.7+.

## Phase 1 — Operator one-time prep

_Pending — to be filled during the publish run._

## Phase 2 — Pre-publish prep

_Pending — to be filled during the publish run._

## Phase 3 — TestPyPI rehearsal

_Pending — to be filled during the publish run._

## Phase 4 — Real PyPI publish

_Pending — to be filled during the publish run._

## Phase 5 — Post-release

_Pending — to be filled during the publish run._

## Milestone-completion summary

_Pending — appended at M17 closeout with the published version,
wheel + sdist sha256, publish timestamp, chain-of-custody
result, and every deviation recorded for v1.7+._
