# M20 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-06-12

Related:
- child-of: m20-pypi-publish.md
- pairs-with: m20-pypi-publish.md
- pairs-with: status.md

## Overview

Chronological log of work on M20 — PyPI publish 1.6.5. Append a section per
runbook phase (operator prep → pre-publish prep → TestPyPI rehearsal → real
PyPI publish → post-release) with objective, actions, results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M20 — PyPI publish 1.6.5
- Started: 2026-06-12 (milestone-setup)
- Progress: **Milestone-setup complete 2026-06-12; publish pending.** M20 is
  the publish-only counterpart to M19 — it ships `docs-cli==1.6.5` (built and
  implementation-complete on `main` at the M19 merge `2a270b0`) to PyPI,
  one-to-one (as M13 shipped M12 and M11 shipped M10; M9 and M17 were the
  batched shapes). An operational publish milestone has no 10-phase TDD cycle;
  the conductor walks the [release-runbook.md](release-runbook.md) directly,
  and the runbook's five sections are the phases. The two OPEN QUESTIONS (Q1
  publish-authorization, Q2 M18 + M19 archival at closeout) carry recommended
  defaults matching the M17 posture and are resolved by the operator at Step 0
  before the irreversible upload. **NEW vs M17:** the Phase-5 closeout refreshes
  the host-machine skills (`docs install-skill --force` + workflow-skill sweep)
  per the CLAUDE.md skill-update-flow policy — production ship is when the
  `~/.claude/skills/` copies refresh.

(Note: doc-lifecycle status is in the front-matter `Lifecycle:` field above.
This section tracks milestone-implementation progress, which is distinct.)

## Runbook Phase Progress

M20 has no TDD code phases — the runbook's sections are the phases (mirrors
M9/M11/M13/M17).

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Operator one-time prep | Pending | — | — |
| 2. Pre-publish prep | Pending | — | — |
| 3. TestPyPI rehearsal | Pending | — | — |
| 4. Real PyPI publish | Pending | — | — |
| 5. Post-release | Pending | — | — |

## Current state analysis (snapshot at milestone kickoff, 2026-06-12)

_Captured before Phase 1; historical._

- **Codebase (1.6.5 ready locally; 1.6.0 shipped on PyPI):**
  `src/docs_cli/cli.py` post-M19 (the full
  `index/new/archive/mv/touch/stamp/project/check/list/migrate/install-skill`
  verb surface, now with `touch --check [--stale N]` + the `[check]
  stale_days` config consumer); the suite was 540 GREEN at M19's
  implementation-complete state (533 at Phase 8 + 7 from the Step-2 review);
  ruff / format / mypy clean tree-wide; `docs check docs/` exit 0. The repo
  `dist/` is gitignored; M20 Phase 2 clears it with `rm -rf dist/` and builds
  fresh 1.6.5 artefacts.
- **What M20 inherits:**
  - `docs-cli==1.6.0` live at https://pypi.org/project/docs-cli/1.6.0/ from
    M17 (2026-06-03).
  - `pyproject.toml` `version = "1.6.5"` (bumped M19 Phase 7);
    `src/docs_cli/cli.py` `__version__` reads through
    `importlib.metadata.version("docs-cli")` per the M12 SoT refactor;
    `tests/test_packaging.py` A3/B1/B2/C2 pinned at `1.6.5`.
  - `CHANGELOG.md` `## 1.6.5 — UNRELEASED` entry already authored with
    publish-survival wording (M19 Phase 7 opened a NEW section above the
    dated `## 1.6.0` — a fresh line, not a fold-in, since 1.6.0 is published);
    the runbook step at Phase 4 is to drop `UNRELEASED` and replace with the
    publish date.
  - `~/.pypirc` (mode 600) carries the M9-era PyPI + TestPyPI API tokens
    (entire-account scope; re-scope to project-`docs-cli` remains an open
    follow-on rolling forward from M9 → M11 → M13 → M17 → M20).
  - TestPyPI `docs-cli` is parked by the M9-era squatter at 0.1.0; M20 will
    continue the `docs-cli-rehearsal` detour that M9/M11/M13/M17 established.
    Re-check ownership at Phase 1.
  - GitHub repo `ArtRichards/docs-cli` is public from M9; tags exist through
    `v1.6.0` (the M17 tag); `v1.6.5` does not yet exist.
  - **Two M13 deviations, now known-expected:** the TestPyPI rehearsal wheel
    prints `docs 0.0.0+local` under the rename detour; `CHANGELOG.md` is not
    in the sdist. Both are folded into the release-runbook already.
  - **NEW since M17:** the CLAUDE.md "Skill update flow" policy (2026-06-12) —
    host skills (`~/.claude/skills/`) refresh at production ship. M20's
    closeout runs `docs install-skill --force` from the published 1.6.5 +
    sweeps the workflow skills' docs-cli prescriptions.
- **What M20 produces:**
  - `docs-cli==1.6.5` published on PyPI.
  - `docs-cli-rehearsal==1.6.5` published on TestPyPI as the rehearsal
    artifact.
  - `v1.6.5` git tag pushed.
  - GitHub release at the v1.6.5 tag, notes sourced from `## 1.6.5`.
  - Host-machine skills refreshed from the published 1.6.5 surface (NEW vs
    M17).
  - Post-publish doc closeouts (M18 + M19 + M20 rows finalised in `status.md`
    + `plan.md`; M18 + M19 milestone docs archived; INDEX + dogfood snapshot
    regenerated in lockstep).
  - Milestone-completion summary with sha256 + publish timestamp + any
    deviations recorded for v1.7+.

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
