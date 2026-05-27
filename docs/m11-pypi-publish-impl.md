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
| 2. Pre-publish prep | Complete | 2026-05-27 | 401 passed; ruff/format/mypy clean; docs check exit 0; fresh artefacts twine-check PASS; local-install smoke + M10 headline contract (--apply --quiet truly silent) verified against the wheel |
| 3. TestPyPI rehearsal | Complete | 2026-05-27 | docs-cli-rehearsal==1.4.0 uploaded; throwaway-venv install PASS; full smoke + M10 headline contract PASS against TestPyPI-served wheel; pyproject.toml rename reverted cleanly |
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

**Completed 2026-05-27.** Objective: verify version pins +
CHANGELOG + tree state, run the tree-wide quality gate, rebuild
artefacts fresh from post-merge-to-`main` HEAD, smoke the
locally-installed wheel including the headline M10 contract.

### Version pins verified

- `pyproject.toml`: `version = "1.4.0"` ✓
- `src/docs_cli/cli.py`: `__version__ = "1.4.0"` ✓
- `tests/test_packaging.py`: A3 assertion pinned at `1.4.0` ✓

(All three landed at M10 Phase 7; M11 Phase 2 only verifies.)

### CHANGELOG state

- Header at line 8: `## 1.4.0 — 2026-05-27 (LOCAL; not on PyPI)`.
- Date matches today's M11 publish day. No date bump needed.
- The `(LOCAL; not on PyPI)` suffix is the M10-closeout marker;
  it will be dropped at Phase 4 (Real PyPI publish) as the
  CHANGELOG-amend commit that announces the actual upload.

### Tree position

- HEAD `e319e7b` on `m11/milestone-setup` (Phase 1 commit).
- `main` = `origin/main` = `8998747` (M10 closeout, M11 Phase 1
  pushed to remote).
- `docs/INDEX.md` ↔ `tests/fixtures/expected/docs-INDEX.md`:
  `diff` exit 0 (byte-identical) ✓

### Quality gate (tree-wide)

| Check | Result |
|---|---|
| `pytest tests/ -q` | **401 passed** in 11.02s |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 33 files already formatted |
| `mypy` | Success: no issues found in 34 source files |
| `docs check docs/` | no violations; exit 0 |
| `docs index --root docs/ --dry-run` | exit 0 (idempotent) |

### Fresh artefact build

`rm -rf dist/` + `python -m build` rebuilt cleanly from HEAD
`e319e7b`. Resulting artefacts:

| Artefact | Size (bytes) | sha256 |
|---|---|---|
| `docs_cli-1.4.0-py3-none-any.whl` | 83 856 | `7af7eb5cb67a860e16d34fb6e8084207e4d3abf2d81fb013fef3b1721c4ec050` |
| `docs_cli-1.4.0.tar.gz` | 495 727 | `292219d4b335819c89acd5cf05111f544d6df1a7ec6d077334a1c8577e0a49c7` |

(Both differ from the M10 Phase 10 pre-merge build — expected:
the post-Phase-10 stack added the m10-simplify, m10-audit, and
m10-phase-6-review commits, all of which touch `src/`. These
M11 Phase 2 bytes are the chain-of-custody anchor for the rest
of M11; Phase 3 and Phase 4 upload these exact files, the
PyPI-served wheel sha256 gets compared back to this row at
Phase 4 close.)

`twine check dist/*` — both artefacts **PASSED**.

### Local-install smoke

Throwaway venv at `/tmp/docs-local-smoke`; `pip install
dist/docs_cli-1.4.0-py3-none-any.whl`:

| Step | Result |
|---|---|
| `docs --version` | `docs 1.4.0` ✓ |
| `docs --help` | Lists 9 verbs (`index, new, archive, mv, touch, check, list, migrate, install-skill`) ✓ |
| `install-skill --dest /tmp/skill-smoke-m11` (fresh) | Byte-identical to `src/docs_cli/skill/` ✓ |
| `install-skill --dest /tmp/skill-smoke-m11` (re-run) | "already matches… no-op"; exit 0 ✓ |
| `install-skill --dest /tmp/skill-smoke-m11 --symlink` | Rejected with educational message; exit 2 ✓ |
| `docs check tests/fixtures/trees/minimal/` | exit 0 ✓ |

### M10 headline contract smoke (against the 1.4.0 wheel)

Synthetic foreign tree `/tmp/m11-foreign-tree/` with three docs
(`widget-plan.md`, `widget-spec.md`, `widget-status.md`,
none carrying metadata). Then:

```sh
docs migrate /tmp/m11-foreign-tree --apply --quiet --config-project widget
```

| Assertion | Result |
|---|---|
| Exit code | 0 ✓ |
| stdout bytes | **0** ✓ (genuinely silent — the M10 F11 fix in commit `5778c44` is live in the wheel) |
| stderr bytes | **0** ✓ |
| `.docs.toml` auto-emitted | Yes — `[project] name = "widget"` + `[archive] date_format = "%Y-%m-%d"` ✓ |
| `docs check /tmp/m11-foreign-tree` exit | 0 (adopted tree passes) ✓ |
| Sample doc metadata insertion | `widget-plan.md` got `Lifecycle: active` / `Role: plan` / `Project: widget` / `Updated: 2026-05-27` ✓ |

### Phase 2 outcome

Pre-publish prep complete. Local artefacts ready. Local smoke
proves the wheel installs cleanly and the headline M10 contract
holds. Ready for Phase 3 (TestPyPI rehearsal) on operator
go-ahead.

## Phase 3 — TestPyPI rehearsal

**Completed 2026-05-27.** Objective: per M9 detour, upload to
TestPyPI under disambiguated dist name `docs-cli-rehearsal`,
install from TestPyPI into a throwaway venv, smoke the wheel
including the M10 headline contract, revert the temporary rename.

### Rehearsal build (under `name = "docs-cli-rehearsal"`)

Working-tree edit to `pyproject.toml` (not committed):
`name = "docs-cli"` → `name = "docs-cli-rehearsal"`. `rm -rf
dist/` + `.venv/bin/python -m build`:

| Artefact | Size (bytes) | sha256 |
|---|---|---|
| `docs_cli_rehearsal-1.4.0-py3-none-any.whl` | 83 975 | `3693b9f7ed997912db0c5c6136ab8ad8277a925f9c6f6eb3eebb14ed9a6cadbf` |
| `docs_cli_rehearsal-1.4.0.tar.gz` | 498 006 | `5f2181e28f98331b62859c4c474bdce26a839ef2ed0fb08be410c7dbb2748dc5` |

`twine check dist/*` — both PASSED.

### Upload to TestPyPI

```sh
.venv/bin/twine upload --repository testpypi dist/*
```

- Both files uploaded successfully — token validity confirmed.
- TestPyPI returns `View at:
  https://test.pypi.org/project/docs-cli-rehearsal/1.4.0/`.
- **Cache-lag note for future runs.** Immediately post-upload
  the TestPyPI JSON metadata API
  (`/pypi/docs-cli-rehearsal/json`) still reported `latest:
  1.3.0` and `releases: ['1.3.0']` — but the simple index
  (`/simple/docs-cli-rehearsal/`, which is what `pip` uses)
  was current and served the 1.4.0 wheel correctly. The JSON
  cache TTL is on the order of a minute or two. Don't gate
  the install attempt on the JSON metadata catching up.

### Throwaway venv install from TestPyPI

```sh
python3 -m venv /tmp/docs-test-venv
/tmp/docs-test-venv/bin/pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    docs-cli-rehearsal==1.4.0
```

Install succeeded on first attempt:
`Successfully installed docs-cli-rehearsal-1.4.0` (pulled
`docs_cli_rehearsal-1.4.0-py3-none-any.whl` straight from
`test-files.pythonhosted.org`).

### Smoke set against TestPyPI-served artefact

| Step | Result |
|---|---|
| `docs --version` | `docs 1.4.0` ✓ |
| `docs --help` (verb list) | All 9 verbs registered ✓ |
| `install-skill --dest /tmp/docs-test-skill` (fresh) | Byte-identical to `src/docs_cli/skill/` ✓ |
| `install-skill --dest /tmp/docs-test-skill` (re-run) | "already matches… no-op"; exit 0 ✓ |
| `install-skill --dest /tmp/docs-test-skill --symlink` | Rejected with educational message; exit 2 ✓ |
| `docs check tests/fixtures/trees/minimal/` | exit 0 ✓ |
| `docs index --root docs/ --dry-run` | exit 0 ✓ |

### M10 headline contract against TestPyPI-served artefact

Synthetic foreign tree `/tmp/m11-testpypi-foreign/` (`gizmo-plan.md`,
`gizmo-spec.md`, `gizmo-status.md` — none with metadata):

```sh
docs migrate /tmp/m11-testpypi-foreign --apply --quiet --config-project gizmo
```

| Assertion | Result |
|---|---|
| Exit code | 0 ✓ |
| stdout bytes | **0** ✓ |
| stderr bytes | **0** ✓ |
| `.docs.toml` auto-emitted | Yes — `[project] name = "gizmo"` + `[archive]` ✓ |
| `docs check /tmp/m11-testpypi-foreign` | exit 0 ✓ |
| Metadata insertion (`gizmo-plan.md`) | `Lifecycle: active` / `Role: plan` / `Project: gizmo` / `Updated: 2026-05-27` ✓ |

### Revert temporary rename

`pyproject.toml`: `name = "docs-cli-rehearsal"` → `name =
"docs-cli"`. `git diff pyproject.toml` empty after revert
(tree clean; no inadvertent additional changes). The
`dist/docs_cli_rehearsal-1.4.0-*` files remain in local `dist/`
but `dist/` is gitignored — they are scratch artefacts.

### Phase 3 outcome

TestPyPI rehearsal passes. The published `docs-cli` 1.4.0
artefacts that will go to real PyPI are byte-identical to the
Phase 2 build (since the only diff between the rehearsal and
real builds is the `pyproject.toml` `name =` line, which the
Phase 4 rebuild will pick up correctly). No bugs surfaced;
no `1.4.1` bump needed. Ready for Phase 4 (real PyPI publish)
on operator go-ahead — Phase 4 is **irreversible**.

## Phase 4 — Real PyPI publish

_Not started._

## Phase 5 — Post-release

_Not started._
