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
| 1. Operator one-time prep | Pending | — | Credentials + registry slots pre-measured at setup (E1, E2); no action expected beyond re-confirmation on the day. |
| 2. Pre-publish prep | Pending | — | Version bump + CHANGELOG dating land here (E7); **twine must be upgraded first** (E3). |
| 3. TestPyPI rehearsal | Pending | — | `docs-cli-rehearsal` detour continues — the bare `docs-cli` TestPyPI name is still squatted (E2). |
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

## Phase 1 — Operator one-time prep

_Not started._
