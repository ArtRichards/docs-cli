# M24 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-07-03

Related:
- child-of: m24-pypi-publish.md
- pairs-with: m24-pypi-publish.md
- pairs-with: status.md

## Overview

Chronological log of work on **M24 — PyPI publish 1.8.0**. Append a section
per runbook phase (operator prep → pre-publish prep → TestPyPI rehearsal →
real PyPI publish → post-release) with objective, actions, results,
decisions. M24 has **no TDD code phases** — the release-runbook's sections are
the phases (mirrors M9/M11/M13/M17/M20).

## Implementation metadata

- Project: docs
- Milestone: M24 — PyPI publish 1.8.0
- Started: 2026-07-03 (milestone-setup)
- Progress: **Setup complete 2026-07-03 — publish pending.** M23 merged to
  `main` (`839daef`); the post-1.6.5 train (M21 update-check + M22 doc guidance
  + M23 agent-aware install-skill) is implementation-complete locally at
  `1.8.0`, none yet on PyPI. M24 will ship them **batched** as `docs-cli==1.8.0`
  (M17/M9 batched precedent). Operator decisions locked at setup (2026-07-03):
  **D1** batched publish as 1.8.0; **D2** fold the CHANGELOG `## 1.7.0`
  entries up into the dated `## 1.8.0` section (1.7.0 skipped on PyPI); **D3**
  "author now, confirm at the gate" — no runbook execution until an explicit
  operator go-ahead, with a confirmation pause before every
  irreversible/outward-facing step; **D4** M23 OQ-1/OQ-2 confirmed as-shipped
  (flag cleared, no re-bump); **D5** closeout archives the M21+M22+M23 pairs +
  the M24 milestone doc. The runbook walk (Phases 1–5) has **not** started.

(Note: doc-lifecycle status is in the front-matter `Lifecycle:` field above.
This section tracks milestone-implementation progress, which is distinct.)

## Runbook Phase Progress

M24 has no TDD code phases — the runbook's sections are the phases (mirrors
M9/M11/M13/M17/M20).

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Operator one-time prep | Pending | — | |
| 2. Pre-publish prep | Pending | — | |
| 3. TestPyPI rehearsal | Pending | — | |
| 4. Real PyPI publish | Pending | — | |
| 5. Post-release | Pending | — | |

## Current state analysis (snapshot at milestone kickoff, 2026-07-03)

_Captured before Phase 1._

- **Codebase (1.8.0 ready locally; 1.6.5 shipped on PyPI):** `main` at merge
  commit `839daef` (M23 merged in). `pyproject.toml` `version = "1.8.0"`
  (bumped M23 Phase 7); `src/docs_cli/cli.py` `__version__` reads through
  `importlib.metadata.version("docs-cli")` (M12 SoT). Full suite **636 GREEN**;
  gate clean tree-wide (ruff / ruff format / mypy / `docs check docs/`). The
  repo `dist/` is gitignored; M24 Phase 2 clears it with `rm -rf dist/` and
  builds fresh 1.8.0 artefacts.
- **What M24 inherits (the three unpublished milestones):**
  - **M21 — Update-check notification** (built as 1.7.0): first network
    surface (stdlib `urllib`, 1.0s timeout, 24h cache under
    `${XDG_CACHE_HOME}/docs-cli/update-check.json`); single STDERR notice;
    full suppression matrix; shows on non-TTY. `1.7.0` never reached PyPI.
  - **M22 — Doc-tree root placement guidance** (doc-only, no bump, no code):
    `convention.md` §Subdirectories + bundled `SKILL.md` guidance.
  - **M23 — Agent-aware install-skill + recorded-dest skill-refresh hint**
    (built as 1.8.0): agent-aware `--dest`, TTY-aware resolution, recorded
    dest at `${XDG_STATE_HOME}/docs-cli/install-skill.json` (path only),
    "agent skill" rewording, the second skill-refresh notice line.
  - `CHANGELOG.md` carries **two** `— UNRELEASED` sections (`## 1.8.0` for
    M22+M23, `## 1.7.0` for M21); D2 folds 1.7.0 into 1.8.0 at Phase 4.
  - `~/.pypirc` (mode 600) carries the M9-era PyPI + TestPyPI API tokens
    (entire-account scope; re-scope to project-`docs-cli` remains the open
    follow-on rolling forward from M9 → … → M20).
  - TestPyPI bare `docs-cli` parked by the M9-era squatter at 0.1.0; M24
    continues the `docs-cli-rehearsal` detour. Re-check ownership at Phase 1.
  - GitHub repo `ArtRichards/docs-cli` public since M9; tags exist through
    `v1.6.5` (the M20 tag); `v1.7.0` and `v1.8.0` do not yet exist (only
    `v1.8.0` will be created — 1.7.0 is skipped).
  - **Known-expected deviations, carried forward:** the TestPyPI rehearsal
    wheel prints `docs 0.0.0+local` under the rename detour (M13);
    `CHANGELOG.md` is not in the sdist (M13); cross-commit `docs/` drift can
    move the sdist sha while the wheel stays bit-stable (M13/M17/M20).
- **What M24 produces:**
  - `docs-cli==1.8.0` published on PyPI.
  - `docs-cli-rehearsal==1.8.0` on TestPyPI as the rehearsal artifact.
  - `v1.8.0` git tag pushed; GitHub release with `## 1.8.0` notes.
  - Host-machine skills refreshed from the published 1.8.0 surface.
  - Post-publish doc closeouts (M21 + M22 + M23 + M24 rows finalised in
    `status.md` + `plan.md`; the M21 + M22 + M23 milestone pairs archived;
    INDEX + fixture snapshot regenerated in lockstep).
  - Milestone-completion summary with sha256 + publish timestamp + any
    deviations recorded for v1.9+.

## Phase 1 — Operator one-time prep

_Not started._
