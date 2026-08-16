# M29 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-08-16

Related:
- child-of: m29-pypi-publish-2-0-0.md
- pairs-with: m29-pypi-publish-2-0-0.md
- pairs-with: status.md
- pairs-with: release-runbook.md
- references: feedback-log.md

## Overview

Chronological log of work on **M29 — PyPI publish 2.0.0**. Append a section
per runbook phase (operator prep → pre-publish prep → TestPyPI rehearsal →
real PyPI publish → post-release) with objective, actions, results, decisions.
M29 has **no TDD code phases** — the sections of
[release-runbook.md](release-runbook.md) are the phases (mirrors
M9/M11/M13/M17/M20/M24).

## Implementation metadata

- Project: docs
- Milestone: M29 — PyPI publish 2.0.0
- Started: 2026-08-16 (milestone setup; no runbook phase started)
- Progress: **Setup complete 2026-08-16; no runbook phase started.** The whole
  v2.0 train is merged to `main` — M25 (`822e086`), M26 (`393fb53`), M27
  (`58955ef`), M28 (`b1ec74b`), M28a (`91cc839`) — and the tree is
  publish-ready except for the two pieces of work M29 owns by design: the
  single version bump `1.8.0` → `2.0.0`, and dating the `## UNRELEASED`
  CHANGELOG heading. Setup ran the read-only half of the runbook's Phase 1 and
  Phase 2 gates and produced seven pieces of measured evidence (**E1–E7**), one
  of which is a **release blocker in the toolchain, not the package** (E3).

(Note: doc-lifecycle status is in the front-matter `Lifecycle:` field above.
This section tracks milestone-implementation progress, which is distinct.)

## Runbook Phase Progress

M29 has no TDD code phases — the runbook's sections are the phases (mirrors
M9/M11/M13/M17/M20/M24).

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Operator one-time prep | Complete | 2026-08-16 | Re-confirmed: PyPI `2.0.0` slot free (released `1.3.0 1.4.0 1.5.0 1.6.0 1.6.5 1.8.0`); `docs-cli-rehearsal` `2.0.0` free; TestPyPI squatter unchanged (`0.1.0`, author `None`) so the detour continues; `~/.pypirc` `600` with two `pypi-` tokens; `gh` holds `repo`. |
| 2. Pre-publish prep | Complete | 2026-08-16 | D1 twine 6.2.0 → **7.0.0** (+ `twine>=7.0.0` added to the `[dev]` extra); version `1.8.0` → **2.0.0** across `pyproject.toml` and the four packaging pins; CHANGELOG `## UNRELEASED` → `## 2.0.0 — 2026-08-16`; README refreshed (all four items). Gate green: **1504 passed**, ruff/format/mypy clean, `docs check` 0, index idempotent, INDEX == fixture, mirrors byte-identical. Build: wheel `bcd8aa45…`, sdist `3cd137ab…`, both `twine check` **PASSED** at `Metadata-Version: 2.5`; CHANGELOG not in sdist (0). Local smoke `docs 2.0.0` + **9/9** headline contracts. |
| 3. TestPyPI rehearsal | Complete | 2026-08-16 | Uploaded `docs-cli-rehearsal==2.0.0` (detour kept); both `twine check` PASSED. Installed from TestPyPI first try. Served-wheel smoke: install-skill byte-identical, `--symlink` exit 2, `check` 0, `index --dry-run` 0, and **9/9** headline contracts. `docs --version` → `docs 0.0.0+local`, the known M13 rehearsal-name caveat. Rename reverted (`git diff pyproject.toml` empty); canonical rebuild wheel `bcd8aa45…` **byte-identical to Phase 2**, sdist `33ceac03…` moved via `docs/` drift. **GO.** |
| 4. Real PyPI publish | Pending | — | Irreversible. Operator authorization at the gate (D2). |
| 5. Post-release | Pending | — | Tag, GitHub release, host-skill refresh, issue #1 reply, README refresh (E6), docs closeout + archive manifest (D3). |

## Setup — readiness measurement (2026-08-16)

Ran the **non-mutating** half of the runbook: every read-only probe, the
tree-wide quality gate, a throwaway-directory artifact build, and a local
install smoke. Nothing was uploaded, tagged, pushed or renamed; the repository
`dist/` still holds the shipped 1.8.0 artifacts untouched, and the build under
test was written to a scratch directory instead.

### E1 — PyPI registry: the 2.0.0 slot is free

`curl -sI https://pypi.org/simple/docs-cli/` → `HTTP/2 200`. Released
versions: `1.3.0, 1.4.0, 1.5.0, 1.6.0, 1.6.5, 1.8.0`; `info.version` = `1.8.0`.
**`2.0.0` is absent**, so the slot is free. (1.7.0 is absent by design — M24
folded it into 1.8.0.)

### E2 — TestPyPI: the squatter is unchanged, the detour continues

Bare `docs-cli` on TestPyPI is still the unrelated squatted project — version
`0.1.0`, author `None`, summary "Um toolkit para processamento e avaliação de
documentação." Unchanged since M9, so the **`docs-cli-rehearsal` detour stays
in force**. That project's released versions are
`1.3.0, 1.4.0, 1.5.0, 1.6.0, 1.6.5, 1.8.0`; **`2.0.0` is free**.

`~/.pypirc` is mode `600` with `[distutils]`, `[pypi]` and `[testpypi]`
sections, `username = __token__` in both, two `pypi-`-prefixed password values,
and the testpypi `repository = https://test.pypi.org/legacy/`. (Prefixes only —
no token value was printed.) `gh` is authenticated as `ArtRichards` with the
`repo` scope, so the tag and release steps are covered.

### E3 — BLOCKER: `twine 6.2.0` rejects the artifacts this tree now builds

A fresh `python -m build` produces **`Metadata-Version: 2.5`** for both the
wheel and the sdist, and `.venv/bin/twine check` fails on both:

```
InvalidDistribution: Invalid distribution metadata: '2.5' is not a valid metadata version
```

The cause is **twine, not the package**. `twine/package.py:32` monkeypatches
`packaging.metadata._VALID_METADATA_VERSIONS` to a hardcoded list ending at
`2.4`; the installed `packaging 26.2` accepts `2.5` on its own. The metadata
version moved because `[build-system] requires = ["hatchling"]` is unpinned, so
each isolated build resolves the current hatchling — the shipped 1.8.0 wheel in
`dist/` is `Metadata-Version: 2.4`, and today's rebuild of the *same* source is
`2.5`.

**PyPI itself accepts 2.5**: hatchling 1.32.0's own wheel, uploaded to PyPI
2026-08-11, serves `Metadata-Version: 2.5`. And **twine 7.0.0 drops the
monkeypatch** — installed into a throwaway venv, `twine check` **PASSES** both
of today's artifacts.

Resolution recorded as **D1**: upgrade the release toolchain to
`twine>=7.0.0` at Phase 2, before the gate. 2.0.0 will be this project's first
`Metadata-Version: 2.5` release; that is a consequence of the toolchain, not of
anything M25–M28a changed.

### E4 — Tree-wide quality gate is green today

| Gate | Result |
|---|---|
| `.venv/bin/python -m pytest -q` | **1504 passed / 0 failed** (M24 shipped at 636) |
| `.venv/bin/ruff check .` | All checks passed |
| `.venv/bin/ruff format --check .` | 48 files already formatted |
| `.venv/bin/mypy` | Success: no issues found in 49 source files |
| `docs check --root docs` | exit 0, no violations |
| `docs index --root docs --dry-run` | exit 0, idempotent |
| `docs/INDEX.md` vs `tests/fixtures/expected/docs-INDEX.md` | identical |
| bundled `references/{cli,convention}.md` vs `docs/` | byte-identical |
| sdist contains `CHANGELOG.md` | 0 (expected — M13 established this) |

### E5 — Every v2.0 headline contract holds against a locally built wheel

Built to a scratch directory, installed into a throwaway venv, exercised on
throwaway copies of this tree. `docs --version` → `docs 1.8.0` (pre-bump, as
designed). `docs --help` lists all twelve verbs including `relate`.
`install-skill` materialises byte-identically, re-runs as a no-op at exit 0,
and refuses `--symlink` at exit 2 (M23 contracts).

| Milestone | Contract | Result |
|---|---|---|
| M25 | `missing-inverse` fires on a one-sided `precedes:` edge | 1 finding |
| M26 | bare `--cascade` refuses, writes nothing | exit 2, message names `--cascade-dry-run` / `--cascade-only`, file count unchanged |
| M27 | `broken-body-link` fires on a dead prose link | 1 finding |
| M28 | `docs mv plan.md milestone-plan.md --dry-run` names each planned rewrite with file, line, old and new destination | full plan printed, `plan.md` still in place |
| M28 | archive reports still-active inbound references | `15 still-active inbound reference(s)` on a real `--cascade-only 'm27-*'` closeout |
| M28a | `docs archive` writes the witness to **every** moved member | `Archived: 2026-08-16` on both members of the pair |
| M28a | `docs mv` refuses across dated archive directories | exit 2, both dates named, source in place, destination absent, by-hand escape printed |
| M28a | `archive-date-drift` detects a hand-made relocation | 1 finding |

### E6 — `README.md` needs four fixes, not the three the plan listed

`README.md` is outside every surface-parity gate and is also the **PyPI project
page** (`readme = "README.md"`). Measured today:

- All **8** `blob/main/…` links resolve, including the
  `docs/archive/2026-05-25/m8-adoption-workflow.md` one M28 repaired. They must
  be re-checked **after** the closeout archive runs, not before.
- The `## Commands` block lists **9 of the 12 shipped verbs** — `relate`
  (M25), `stamp` (M15) and `project rename|set` (M12) are absent.
- The feature summary predates the train: no reciprocal rules, no body-link
  rules, no move-safe rewrites, no `Archived:` witness, and no mention that
  bare `--cascade` is retired.
- **New at setup:** README still says "**Claude Code** skill" in **three**
  places (lines 51, 60, 67) while `src/docs_cli/` carries **zero** such
  mentions — M23 neutralised the shipping surface to "agent skill" and README,
  being outside the gate, was never swept. Shipping a 2.0.0 whose PyPI front
  page contradicts the tool's own agent-agnostic stance is the same class of
  self-refutation that made M28 fix the dead README link inside its own
  milestone.

### E7 — Version SoT is 1.8.0 by design; M29 owns the single bump

`pyproject.toml` `version = "1.8.0"`; `tests/test_packaging.py` A3 pins
`1.8.0`; `CHANGELOG.md`'s open heading is `## UNRELEASED` with the explicit
note that the package version stays 1.8.0 until M29. `__version__` is read at
import time via `importlib.metadata`, so there is no second literal to move.
This is M25 — D6 working as intended, and it means M29's Phase 2 does the
version bump, the packaging-pin flip and the CHANGELOG dating in one commit.

## Phase 1 — Operator one-time prep (2026-08-16)

### Objective

Re-verify, not establish. The accounts and tokens have shipped six releases;
this phase confirms nothing rotted between setup and publish day.

### Results

Every setup probe re-run unchanged, same day:

- **PyPI** — released `1.3.0, 1.4.0, 1.5.0, 1.6.0, 1.6.5, 1.8.0`; the `2.0.0`
  slot is free.
- **TestPyPI** — the bare `docs-cli` name is still the unrelated squatted
  `0.1.0` project (author `None`), so the **`docs-cli-rehearsal` detour stays in
  force**; its `2.0.0` slot is free.
- **`~/.pypirc`** — mode `600`, `[pypi]` + `[testpypi]`, both
  `username = __token__`, both passwords `pypi-`-prefixed (prefixes only; no
  value printed).
- **`gh`** — authenticated as `ArtRichards` with the `repo` scope.

No action was required. Nothing on this list has moved since M24.

## Phase 2 — Pre-publish prep (2026-08-16)

### Objective

The only phase that changes the source tree: clear the E3 blocker, perform the
single version bump, date the CHANGELOG, refresh the README, then run the full
gate and build the artifacts that Phase 3 rehearses and Phase 4 publishes.

### Files Changed

| File | Action | Notes |
|------|--------|-------|
| `pyproject.toml` | modified | `version` `1.8.0` → `2.0.0`; `[dev]` extra gains `twine>=7.0.0` |
| `tests/test_packaging.py` | modified | A3, B1, B2, C2 pins moved to `2.0.0`; docstrings re-attributed from M23 to M29 |
| `CHANGELOG.md` | modified | `## UNRELEASED` → `## 2.0.0 — 2026-08-16`; the "stays 1.8.0 until then" note replaced with the release summary |
| `README.md` | modified | all four E6 items |
| `dist/` | rebuilt | `docs_cli-2.0.0-py3-none-any.whl` + `docs_cli-2.0.0.tar.gz` |

### Actions Taken

**1. D1 — the toolchain fix, first.** `.venv/bin/pip install --upgrade
'twine>=7.0.0'` → **twine 7.0.0**. To keep the constraint documented rather than
machine-local — the stated reason D1 rejected pinning hatchling — `twine>=7.0.0`
was also added to the `[dev]` extra, which previously listed only pytest, ruff,
mypy and build. This is the first release whose toolchain requirement is
recorded in `pyproject.toml` instead of in the runbook's prose.

**2. The single version bump.** `pyproject.toml` `1.8.0` → `2.0.0`, in lockstep
with all four packaging pins (A3 `[project].version`, B1 wheel filename, B2
sdist filename, C2 `docs --version`). `__version__` needed no edit — M12's
version SoT reads it from `importlib.metadata`. `tests/test_update_check.py`
needed no edit either: it computes `CURRENT` from `cli.__version__` and uses a
`99.0.0` sentinel for "newer", deliberately bump-proof.

**3. CHANGELOG dated.** `## UNRELEASED` → `## 2.0.0 — 2026-08-16`. The
placeholder's "the package version deliberately stays `1.8.0` until then" note
was replaced with a summary naming the five milestones and the reason for the
major bump. A sweep of the whole release section for the M11-lesson wording
classes — `UNRELEASED`, "ready locally", "not on PyPI", "deferred to MX",
forward references to M29 — found **zero**; the section was authored to survive
publication. Its `### Upgrading from 1.x` subsection was already in place.

**4. README refresh — all four E6 items.** The `## Commands` block now
documents **12 of 12** shipped verbs (mechanically verified against
`docs --help`), with `relate`, `stamp` and `project rename|set` added and
`archive`'s cascade flags and `touch --check` shown. A new
**What 2.0 enforces** section covers the five behaviour changes an upgrader
meets, and points at the CHANGELOG's *Upgrading from 1.x* for the repair
recipes. All three "Claude Code skill" mentions are now "agent skill"; the only
surviving `.claude` string is the factual default destination
`~/.claude/skills/docs/`, which `--help` also prints. The *Status* section's
claim that the `Status:` → `Lifecycle:` rename is "the only breaking keyword
change to date" was **true but misleading** at 2.0 and now distinguishes what
2.0 breaks — automation — from what it does not: on-disk data, since `Archived:`
is added going forward and no upgrade rewrites an existing file.

### Test Results

| Gate | Result |
|---|---|
| `pytest -q` | **1504 passed / 0 failed** (M24 shipped at 636) |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 48 files already formatted |
| `mypy` | Success: no issues found in 49 source files |
| `docs check --root docs` | exit 0 |
| `docs index --root docs --dry-run` | exit 0, idempotent |
| INDEX vs `tests/fixtures/expected/docs-INDEX.md` | identical |
| bundled `references/{cli,convention}.md` vs `docs/` | byte-identical |
| "Claude Code" in `src/docs_cli/` + `README.md` | 0 |

**Artifacts (chain-of-custody anchors):**

```
bcd8aa453415dfe66868f22830fce318c7149d6642935d6167d4de9b2cdaab23  dist/docs_cli-2.0.0-py3-none-any.whl
3cd137ab2dadd67a6446e9bc2490225923d3f80170d8ca7b091457a822e6bb74  dist/docs_cli-2.0.0.tar.gz
```

Both `twine check` **PASSED** at `Metadata-Version: 2.5` — D1 confirmed in
practice, on the exact artifacts twine 6.2.0 rejected. `tar tzf … | grep -c
CHANGELOG` → **0**, as M13 established.

**Local-install smoke** (throwaway venv, wheel only): `docs --version` →
`docs 2.0.0`; `install-skill` byte-identical to `src/docs_cli/skill/`, no-op on
re-run at exit 0, `--symlink` refused at exit 2; `check` on the minimal fixture
exit 0; `index --root docs --dry-run` exit 0. The **headline-contract probe**
was scripted so the identical nine checks can be re-run against each served
artifact: **9/9 passed** — baseline clean, `missing-inverse`, the bare
`--cascade` refusal at exit 2 with 75 files unchanged, `broken-body-link`, `mv
--dry-run` planning **42** rewrites with nothing written, the strand report, the
`Archived:` witness on both members with one shared date, the cross-dated `mv`
refusal, and `archive-date-drift`.

### Issues/Decisions

- **One expected failure, resolved:** the first full run after the bump failed
  `test_version_matches_pyproject` at `'1.8.0' == '2.0.0'`. This is the editable
  install's recorded metadata lagging `pyproject.toml` — `__version__` resolves
  through `importlib.metadata`, which reads the installed dist-info, not the
  source file. `pip install -e ".[dev]"` refreshed it and the suite returned to
  1504. Worth a runbook note: **the version bump requires an editable
  reinstall before the gate**, and the test that catches it is doing exactly its
  job.
- No test was relaxed, deleted or rewritten. `tests/test_packaging.py` is the
  only test file touched, and only where the version literal is the assertion's
  subject; the four docstrings were re-attributed from M23 to M29 so the
  provenance stays honest.

## Phase 3 — TestPyPI rehearsal (2026-08-16)

### Objective

Publish the real artifact shape to a throwaway index first, install it the way
a user will, and prove the served bytes behave — before the append-only PyPI
upload.

### Actions Taken

The Phase-1 re-check found the TestPyPI squatter unchanged, so the
**`docs-cli-rehearsal` detour stayed in force**: `pyproject.toml`
`[project] name` was temporarily renamed, `dist/` rebuilt
(`docs_cli_rehearsal-2.0.0`, wheel `01ce7177…`, sdist `21ffe80a…`, both
`twine check` PASSED), and both artifacts uploaded to
`https://test.pypi.org/project/docs-cli-rehearsal/2.0.0/`.

Installed into a throwaway venv from the TestPyPI simple index with
`--extra-index-url https://pypi.org/simple/`; **first try, no retry needed** and
no JSON-lag workaround required, since `pip` reads the simple index.

### Test Results

Against the **TestPyPI-served** wheel:

| Probe | Result |
|---|---|
| `docs --version` | `docs 0.0.0+local` — **expected**, see below |
| `install-skill --dest …` | byte-identical to `src/docs_cli/skill/` |
| `install-skill --symlink` | exit 2 |
| `check tests/fixtures/trees/minimal/` | exit 0 |
| `index --root docs --dry-run` | exit 0 |
| headline-contract probe | **9/9 passed** |

The nine contracts are the same script Phase 2 ran against the local wheel, so
local and served builds are compared on identical evidence rather than on
similar-looking manual runs.

### Issues/Decisions

- **`docs 0.0.0+local` is the documented M13 caveat, not a failure.**
  `__version__` resolves `importlib.metadata.version("docs-cli")`, and the
  rehearsal installs as `docs-cli-rehearsal`, so the lookup misses and hits the
  `PackageNotFoundError` fallback. The version-string contract is verified
  against the canonical-name local wheel (Phase 2) and the PyPI wheel (Phase 4)
  — never the rehearsal wheel.
- **Rename reverted and proven:** `git diff pyproject.toml` is empty. The
  canonical rebuild then produced a wheel at **`bcd8aa45…`, byte-identical to
  Phase 2's**, confirming that the rename detour left no trace in the artifact
  that ships.
- **The sdist sha moved** (`3cd137ab…` → `33ceac03…`) and that is correct: the
  sdist captures `docs/`, and the Phase-2 impl-log entry was committed between
  the two builds. M13 established exactly this — the wheel is stable across
  rebuilds of the same `src/`, the sdist tracks `docs/`.
- **GO** recorded for Phase 4.
