# M29 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-08-16

Related:
- pairs-with: archive/2026-08-16/m29-pypi-publish-2-0-0.md
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
- Started: 2026-08-16 (milestone setup)
- Progress: **Complete 2026-08-16 — `docs-cli==2.0.0` shipped to PyPI.** All
  five runbook phases done in one session, the same day M28a merged. The whole
  v2.0 train — M25 (`822e086`), M26 (`393fb53`), M27 (`58955ef`), M28
  (`b1ec74b`), M28a (`91cc839`) — went public in one `main` push of **101
  commits** (`f855b80..408ef6c`), tagged `v2.0.0` at the chain-of-custody
  commit. **Chain of custody bit-perfect for both wheel and sdist**; the
  nine-check headline-contract script passed **9/9 against all three builds**
  (local, TestPyPI-served, PyPI-served). Driven under **D2** — the operator
  authorized the irreversible set (upload, `main` push, tag, release)
  explicitly before Phase 4. Decisions: **D1** upgraded twine 6.2.0 → 7.0.0 and
  moved the floor into the `[dev]` extra, clearing the one blocker setup found;
  **D3** archived the five plan/log pairs plus the M29 milestone doc, this log
  staying active; **D4** refreshed the README in Phase 2 (it ships as the PyPI
  long description) and re-verified its links after the closeout archive.
  **All success criteria are now met.** The last one closed after the
  milestone doc was archived: issue #1's reply was posted and the issue closed
  by the operator on 2026-08-16, `gh issue comment` having been blocked by a
  local permission classifier during Phase 5 itself. The archived milestone doc
  still shows that criterion unticked, correctly — it is a snapshot of what was
  true at closeout, and the convention grants no exception for editing archived
  prose to tidy it up. This log is the living record; see *Post-closeout* at the
  end.

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
| 4. Real PyPI publish | Complete | 2026-08-16 | Operator authorized the irreversible set explicitly (D2). `main` fast-forwarded `f855b80..408ef6c` (**101 commits** — the whole v2.0 train) and pushed; canonical rebuild at the tag-target commit `408ef6c`; both `twine check` PASSED; **uploaded to PyPI**; install from PyPI first try → `docs 2.0.0`; **chain of custody BIT-PERFECT for wheel AND sdist** (`bcd8aa45…` / `c62f22d3…`); **9/9** headline contracts against the PyPI-served wheel. |
| 5. Post-release | Complete | 2026-08-16 | Annotated `v2.0.0` tag at `408ef6c` pushed; GitHub release live with the `## 2.0.0` notes; **host skill refreshed** from the published wheel, byte-identical, recorded dest corrected to `~/.claude/skills/docs`; workflow-skill sweep found **real drift** (below); doc closeouts + D3's eleven-document archive. **Issue #1 reply verified but NOT posted at the time** — blocked by a local permission classifier; the operator posted it and closed the issue the same day (see *Post-closeout*). |

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

## Phase 4 — Real PyPI publish (2026-08-16)

### Objective

Publish `docs-cli==2.0.0`, and prove the bytes PyPI serves are the bytes this
tree built.

### Authorization (D2)

The operator authorized the irreversible set explicitly — the PyPI upload, the
`main` push, the tag and the GitHub release — before this phase began. D2's
"author now, confirm at the gate" was satisfied by that instruction; every step
below ran under it.

### Actions Taken

1. **`main` fast-forwarded and pushed** — `f855b80..408ef6c`, **101 commits**:
   the entire v2.0 train (M25, M26, M27, M28, M28a and M29's own three commits)
   became public in one push. `main` had been held locally since M24's ship,
   which is the project's deliberate pattern — main moves at publish, not at
   merge.
2. **Canonical rebuild at the tag-target commit `408ef6c`**, on a clean tree,
   so the sdist captures the `docs/` state that ships.
3. `twine check` — both **PASSED**.
4. **Uploaded to PyPI**: https://pypi.org/project/docs-cli/2.0.0/
5. Installed from PyPI into a throwaway venv, first try.

### Test Results

**Chain of custody — BIT-PERFECT for both artifacts.** The PyPI-served bytes,
pulled back with `pip download`, are byte-identical to the local Phase-4 build:

| Artifact | sha256 | Served == local |
|---|---|---|
| `docs_cli-2.0.0-py3-none-any.whl` | `bcd8aa453415dfe66868f22830fce318c7149d6642935d6167d4de9b2cdaab23` | **yes** |
| `docs_cli-2.0.0.tar.gz` | `c62f22d35067cb42a8c241e1d36e161f60ac533b33658ab41f804a2a2c862b66` | **yes** |

The wheel sha has been stable across **all three** builds — Phase 2, the
post-rehearsal canonical rebuild, and Phase 4 — confirming both that the
rehearsal rename left no trace and that no `docs/` churn reaches the wheel.

Against the **PyPI-served** wheel: `docs --version` → `docs 2.0.0` (the
canonical-name check the rehearsal could not make); `install-skill`
byte-identical, no-op on re-run at exit 0, `--symlink` refused at exit 2;
`check` on the minimal fixture exit 0; `index --root docs --dry-run` exit 0;
and the headline-contract probe **9/9**, the third identical run of the same
script across local, TestPyPI-served and PyPI-served builds.

## Phase 5 — Post-release (2026-08-16)

### Objective

Tag, release, refresh the host skill, sweep the workflow skills, answer the
issue that shaped the train, and close the docs out.

### Actions Taken

**Tag + release.** Annotated `v2.0.0` at `408ef6c` — the chain-of-custody
commit, so the tagged tree is exactly what PyPI serves — pushed, and the GitHub
release created with the `## 2.0.0` CHANGELOG section as its notes
(https://github.com/ArtRichards/docs-cli/releases/tag/v2.0.0).

**Host-machine skill refresh.** Per the CLAUDE.md policy that production ship
is the only time `~/.claude/skills/` moves, the host `docs` skill was
re-materialised **from the published wheel** with `install-skill --force` and
verified byte-identical to the published bundle. This also corrected the M23
recorded dest, which the pre-publish smoke runs had left pointing at a scratch
directory; it now records `~/.claude/skills/docs`.

**Workflow-skill sweep — this one found real drift.** The policy's sweep of the
workflow skills' docs-cli prescriptions turned up **nine bare `--cascade`
prescriptions that 2.0 retires**, spread across two skills:

| Skill | File | Occurrences |
|---|---|---|
| `create-milestones` | `SKILL.md` | 3 (invariant 4, invariant 7, completion checklist) |
| `create-milestones` | `references/milestone-playbook.md` | 3 (Step 4, its explanation, the worked example) |
| `create-milestones` | `references/tdd-phases.md` | 1 (Phase 10 exit) |
| `create-milestones` | `README.md` | 1 (deliverables) |
| `project-foundation` | `references/role-mapping.md` | 1 (milestone lifecycle row) |

Every one of them is the **milestone-completion step** — `docs archive
<slug>.md --cascade --reason "…"` — which under 2.0 refuses at exit 2 and
writes nothing. The correct form is a preview with `--cascade-dry-run` followed
by an explicit `docs archive <slug>.md --cascade-only '<glob>' --reason "…"`.

This is **recorded, not fixed here**: the milestone doc's *Closeout intent*
scopes the Agent Playbook Suite update out of M29 as a cross-repository change,
and that constraint is now discharged — 2.0.0 is available, so the suite update
is unblocked and is M29's named follow-on. It is worth stating plainly that the
sweep earned its place in the policy: without it, the first milestone closeout
after this release would have failed at exit 2 with the operator's own playbook
telling them to run the retired flag. This closeout hit exactly that hazard and
used `--cascade-only`.

**Issue #1 — verified and prepared; posted just after closeout.** Every claim in the prepared
reply was re-verified against the **shipped** wheel rather than the plan, which
is what the milestone doc demanded:

| Claim | Verified against the PyPI-served wheel |
|---|---|
| bare `--cascade` refuses, writes nothing | exit 2, 75 files unchanged |
| already-archived candidates are reported | verbatim `ineligible (already archived)`, 4 of them |
| `archive --json` carries `strands` **and** `rewrites` | top-level keys include both |
| `mv --dry-run` / `--json` carry the rewrite plan | 42 `rewrites` entries |
| `broken-body-link`, `missing-inverse`, `archive-date-drift` | all fire |
| the `Archived:` witness on every moved member | both members, one shared date |
| the cross-dated `mv` refusal | exit 2, zero writes |

The comment could not be posted **from inside the milestone**: `gh issue
comment` was blocked by a local permission classifier, not by GitHub. It was
recorded as the one M29 success criterion not met, deliberately, rather than
quietly dropped — and the operator posted it the same day. See *Post-closeout*.

### Issues/Decisions

- **Two runbook corrections** found by walking it, both landing in the runbook
  at this closeout:
  1. *Artifact build* still says to install twine "if not already present" — the
     shape of the trap D1 hit, since a stale twine **is** present. It now
     carries the `twine>=7.0.0` floor and the `[dev]`-extra pointer.
  2. *Post-release* still says "the archive verb doesn't rewrite referring
     edges; that's `docs mv` territory". **M18 and M28 made that false**: this
     closeout's own archive rebased the referring edges and body links
     automatically. The enhancement candidate it points at has shipped.
- The version bump needs an **editable reinstall** before the gate; added to the
  runbook's Phase-2 block so the next publish does not rediscover it.
- **The closeout archive was refused by M26's leg-1 strand check — correctly.**
  D3 archives the milestone doc while the log stays active (M17/M20/M24), but
  the log declared `child-of: m29-pypi-publish-2-0-0.md`, so `docs archive`
  refused at exit 2 with zero bytes written:

  ```
  docs: archive: m29-pypi-publish-2-0-0-impl.md is still active and declares
  'child-of: m29-pypi-publish-2-0-0.md', which this operation would archive;
  refusing before any write
  docs: archive: 1 still-active child(ren) would be stranded; zero bytes written
  ```

  This is the milestone's own train catching a modelling error in the project's
  own precedent, and it is the single most satisfying moment of the release: a
  rule written for issue #1's "parent archived out from under a live child"
  fired on the closeout of the release that shipped it. The fix is not to
  suppress the rule but to model the relationship honestly — a publish log that
  **deliberately outlives** its milestone doc is that doc's **pair**, not its
  child. The `child-of` / `parent-of` edge was dropped from both sides, leaving
  the `pairs-with` that already described them, and the archive completed at
  exit 0.

  The whole eleven-document manifest was rehearsed on a **throwaway copy** of
  the tree before touching the live one, which is how the refusal was met
  without a half-finished closeout to unwind. Note for the next publish:
  `m17-`, `m20-` and `m24-pypi-publish-impl.md` carry the same `child-of` edge
  into `archive/`, where it is harmless — the rule fires only when the plan
  would archive a **live** parent — so this is an inherited pattern that will
  recur at the next closeout unless those edges are re-modelled too.

## Milestone-completion summary (2026-08-16)

**M29 is complete: `docs-cli==2.0.0` is live on PyPI**, published from commit
`408ef6c` and tagged `v2.0.0`. All five runbook phases ran in one session on
2026-08-16, the same day M28a merged.

### What shipped

The whole v2.0 safety train as one breaking release — M25 reciprocal
relationship integrity and `docs relate`, M26 safe explicit archive selection,
M27 Markdown body-link validation, M28 move-safe body-link rewrites, M28a the
structured archive-date witness. M25 — D6 held the package at `1.8.0` across
all five so the train could ship together; M29 performed the single bump.

### Verification

| Anchor | Value |
|---|---|
| Wheel sha256 | `bcd8aa453415dfe66868f22830fce318c7149d6642935d6167d4de9b2cdaab23` |
| Sdist sha256 | `c62f22d35067cb42a8c241e1d36e161f60ac533b33658ab41f804a2a2c862b66` |
| Chain of custody | **bit-perfect, wheel and sdist** |
| Tag target | `408ef6c` (annotated `v2.0.0`) |
| `main` push | `f855b80..408ef6c`, 101 commits |
| Suite at publish | 1504 passed / 0 failed |
| Headline contracts | 9/9 local · 9/9 TestPyPI-served · 9/9 PyPI-served |

The single most useful piece of method here was scripting the headline-contract
probe once and running it unchanged against all three builds. Three manual
walkthroughs would have compared three slightly different things; one script
compared the same nine facts, and the only difference between runs was which
wheel answered.

### Lessons

1. **The toolchain is part of the release surface.** D1 — twine 6.2.0 rejecting
   `Metadata-Version: 2.5` — was found by running the read-only gate at
   *milestone setup* rather than at the upload. Had setup skipped the build
   step as "nothing to measure, the version has not been bumped yet", the
   failure would have surfaced mid-publish. Cheap dry runs early are worth more
   than their cost.
2. **"Install if absent" is not a version policy.** The runbook's twine step
   read as satisfied while being exactly wrong. Constraints belong in
   `pyproject.toml` where they are version-controlled and enforced, not in prose
   that a present-but-stale tool silently passes.
3. **A release that *changes* a verb breaks the playbooks that prescribe it.**
   M24's sweep was quiet because M21 and M23 only added surface. M29 retired a
   flag, and nine prescriptions across two workflow skills went stale at once.
   The in-repo drift-lint candidate — diff workflow-skill prescriptions against
   the bundled `references/` surface — now has a concrete failure behind it.
4. **Documents outside the gate rot fastest, and `README.md` is the worst
   place for that** because it is the PyPI project page. Three of twelve verbs
   undocumented and three "Claude Code" mentions M23 thought it had removed.
   Refreshing it in Phase 2 rather than the closeout is the durable fix — it
   ships inside the artifact.
5. **Trackers describe state that changes under them.** Both runbook
   corrections were sentences that were true when written and became false when
   a later milestone shipped. Neither had a test, because neither is testable —
   only a walk of the document catches them.

### Outstanding

- **PyPI token re-scope** to project `docs-cli` — rolls forward from M9, now
  six releases old. The only item M29 leaves open.

## Post-closeout (2026-08-16)

Two items that were outstanding at the closeout closed the same day, after
`docs archive` had already moved the milestone doc. They are recorded here
rather than in that document: the convention grants exactly three narrow
exceptions for editing an archived file — M18's move-driven reference rewrite,
M25 — D4's audited relationship repair, and M27 — D6's one-time body-link
migration — and none covers tidying prose after the fact. The archived
milestone doc's unticked criterion is an honest snapshot of what was true when
it was archived. This is precisely why the M17/M20/M24 precedent keeps the
publish log active at the root.

**Issue #1 is CLOSED.** The operator posted the verified reply and closed the
issue at 2026-08-16T10:54:25Z (two comments on the thread: the original report
and the reply). Every claim in it had been checked against the PyPI-served
wheel rather than the plan. **M29's success criteria are now all met**, the
last one outside the milestone's own boundary.

**The host CLI is upgraded.** `~/.local/bin/docs` reports **2.0.0**, closing a
gap this closeout created: Phase 5 refreshed the host `docs` skill from the
published wheel while the host binary was still 1.8.0, so the host briefly held
2.0 instructions and a 1.x CLI — an agent following the refreshed skill would
have called `--cascade-only`, `--cascade-dry-run` or `docs relate` against a
binary without them. Re-verified after the upgrade: the host skill is still
byte-identical to what 2.0.0 ships.

That split is worth remembering for the next publish. The CLAUDE.md policy
refreshes host **skills** at production ship and says nothing about the host
**binary**; nothing in either repository detects the mismatch, and the suite's
new retired-flag check does not either — it validates the repo against its
pinned version, not a machine against the repo. Upgrading the binary belongs in
the same step as refreshing the skill.
