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
| 1. Operator one-time prep | In progress | 2026-05-27 | Session-verifiable state captured; account login + 2FA + token-validity await operator confirmation or Phase 3 upload surfacing |
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

**Started 2026-05-27.** Objective: re-verify M9-era account /
token / `~/.pypirc` state still current; re-check whether the
TestPyPI `docs-cli` squatter project lapsed since 2026-05-25.

### Session-verifiable state (captured 2026-05-27)

- **`~/.pypirc` intact.** Mode `-rw-------` (600), 543 bytes,
  dated 2026-05-25. Sections present: `[distutils]`,
  `[pypi]` (`username = __token__`), `[testpypi]`
  (`username = __token__`, `repository =
  https://test.pypi.org/legacy/`). Token prefixes
  `pypi-AgEIcHl…` (PyPI) and `pypi-AgENdGV…` (TestPyPI)
  match the canonical PyPI / TestPyPI scoped-token shape.
  Token *values* not printed.
- **PyPI `docs-cli`** — HTTP 200 at
  `https://pypi.org/simple/docs-cli/`; JSON metadata reports
  `latest: 1.3.0`, `releases: ['1.3.0']`. M9's release intact;
  1.4.0 slot is free for M11 to publish into.
- **TestPyPI `docs-cli`** — HTTP 200 at
  `https://test.pypi.org/simple/docs-cli/`; JSON metadata
  reports `latest: 0.1.0`, `author: None`, `releases:
  ['0.1.0']`. **Squatter has NOT lapsed since 2026-05-25** —
  same `0.1.0` placeholder, no author surface. M11 continues
  M9's disambiguated-dist-name detour: TestPyPI rehearsal
  uploads under `docs-cli-rehearsal==1.4.0`. The
  rehearsal-name-drop is a follow-on for a future release.
- **TestPyPI `docs-cli-rehearsal`** — JSON metadata reports
  `latest: 1.3.0`, `releases: ['1.3.0']`. M9's rehearsal
  artefact intact; 1.4.0 slot under this name is free.
- **Local tooling.** `twine 6.2.0` (matches M9 baseline;
  identical version smoke-tested at M6 ship),
  `python 3.12.3`, `build 1.5.0`. Both installed under
  `.venv/`.
- **Local `dist/`.** Holds M9's `docs_cli-1.3.0-{whl,tar.gz}`
  (2026-05-25, the actually-shipped artefacts) plus M10
  Phase 10's `docs_cli-1.4.0-{whl,tar.gz}` (2026-05-27, the
  pre-merge build). Phase 2 will `rm -rf dist/` and rebuild
  from post-merge-to-`main` HEAD per the milestone-doc
  Requirements.

### Operator-confirmation items (cannot verify from session)

- PyPI account login + 2FA active.
- TestPyPI account login + 2FA active.
- Tokens not rotated / revoked since M9 (no negative signal so
  far; positive confirmation surfaces at Phase 3 first
  `twine upload --repository testpypi`).

These are not blockers — token validity gets validated by
the actual upload at Phase 3. If a token rotted, that's where
the failure surfaces and Phase 1 re-opens for an operator
token-refresh round-trip.

### Decisions recorded at Phase 1

- **TestPyPI rehearsal under `docs-cli-rehearsal==1.4.0`**
  confirmed (squatter unchanged).
- **No token re-scope inside M11.** The M9 follow-on to
  re-scope the bootstrap "Entire account" tokens to
  project-`docs-cli` remains async operator UI work; M11
  publishes with whatever scope the tokens currently carry.
  If the re-scope happened between M9 close and M11 start,
  the publish is a no-op; if not, the follow-on rolls forward
  to a post-M11 close.
- **Local `main` is at `8998747`** (M10 stack merged + pushed
  to `origin/main` at M11 Phase 1 start). The fresh artefact
  build at Phase 2 will run from this commit.

### Phase 1 outcome

Session-side state green. Operator confirmation requested for
the three login / 2FA / token-rotation items above before
Phase 2 fresh build runs.

## Phase 2 — Pre-publish prep

_Not started._

## Phase 3 — TestPyPI rehearsal

_Not started._

## Phase 4 — Real PyPI publish

_Not started._

## Phase 5 — Post-release

_Not started._
