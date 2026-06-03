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
| 2. Pre-publish prep | Complete | 2026-06-03 | Gate GREEN 510 passed; ruff/format/mypy/`docs check`/index-dry-run clean. Fresh 1.6.0 build (stale 1.5.0 cleared); both `twine check` PASS. Local-wheel smoke `docs 1.6.0`; install-skill byte-identical / no-op / `--symlink` exit 2; all 7 M14+M15 contracts PASS; no `../` links. sha256 below. |
| 3. TestPyPI rehearsal | Complete | 2026-06-03 | Uploaded `docs-cli-rehearsal==1.6.0` (squatter still parked → detour kept). Installed from TestPyPI first try; smoke + all 7 contracts PASS against the served wheel; `docs --version` → `0.0.0+local` (known-expected, M13). Rename reverted; `git diff pyproject.toml` empty. |
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

_Executed 2026-06-03 against branch `m17/milestone-setup` (HEAD 2473454)._

**Version + CHANGELOG verification.** `pyproject.toml` `version = "1.6.0"`,
`name = "docs-cli"`; `src/docs_cli/cli.py` `__version__` reads through
`importlib.metadata.version("docs-cli")` with the `0.0.0+local` fallback
(M12 SoT); `tests/test_packaging.py` A3 (`test_a3_project_version_is_1_6_0`)
pinned at `1.6.0`. `CHANGELOG.md` carries `## 1.6.0 — UNRELEASED` with
publish-survival wording (no "ready locally" / "deferred to MX" markers).
**Phase-4 NOTE for the conductor:** the section's lead-in line
"M14 + M15 landed locally; the publish milestone (M17) ships 1.6.0 to PyPI."
describes state, not a deferral, but reads stale post-publish — drop/rewrite
it as part of the Phase-4 `UNRELEASED` → date edit (this is the
already-anticipated edit per the milestone-doc Decision "CHANGELOG
publish-survival wording already locked"). Not edited here — dating the
CHANGELOG is Phase 4.

**Quality gate (tree-wide) — all GREEN:**

- `pytest tests/ -q` → **510 passed** in ~24s (matches the expected ~510).
- `ruff check .` → All checks passed.
- `ruff format --check .` → 39 files already formatted.
- `mypy` → Success, no issues in 40 source files.
- `docs check docs/` → no violations (exit 0).
- `docs index --root docs/ --dry-run` → exit 0, reproduced the existing
  INDEX (idempotent).

**Fresh artifact build.** `rm -rf dist/` cleared the stale 1.5.0 artefacts;
`python -m build` produced `docs_cli-1.6.0-py3-none-any.whl` +
`docs_cli-1.6.0.tar.gz`. **Phase-2 sha256 (chain-of-custody anchors):**

- wheel `docs_cli-1.6.0-py3-none-any.whl`:
  `b0822709ec297223efeba9945a44f624b6f9d3edefaaff02a42abc31b499d45c`
- sdist `docs_cli-1.6.0.tar.gz`:
  `da1a60b8409d91305a1ee6d3dee465a377151cc27608e18df02a94fd80859743`

`twine check dist/*` → both **PASSED**. `CHANGELOG.md` not in the sdist
(`tar tzf … | grep -c CHANGELOG` → 0; known-expected per M13).

**Local-install smoke (no PyPI), `/tmp/docs-local-smoke`, canonical wheel:**

- `docs --version` → `docs 1.6.0` (canonical name resolves the SoT).
- `docs --help` lists `install-skill`, `stamp`, `project` (with `set`),
  plus the full verb surface.
- `install-skill --dest /tmp/skill-smoke` → exit 0; `diff -ru
  src/docs_cli/skill /tmp/skill-smoke` empty (byte-identical); re-run →
  exit 0 no-op; `--symlink` → exit 2.
- `docs check tests/fixtures/trees/minimal/` → exit 0.
- Installed skill references carry no repo-relative `](../` links
  (grep on both the site-packages skill and the installed copy → no match).

**The seven M14 + M15 headline contracts (local wheel) — all PASS:**

1. **M14 `mv` all-or-nothing** — malformed sibling → exit 2; source stays,
   dest absent, referring `Related:` edge + INDEX untouched.
2. **M14 `new` strict-root refusal** — outside any root, no `--root` →
   exit 2; nothing written to cwd.
3. **M14 non-interactive `archive --cascade`** — `--cascade` (stdin closed)
   archives primary + its one-hop `pairs-with` set, no prompt, exit 0;
   `--cascade-dry-run` writes nothing (exit 0); post-cascade `docs check`
   exit 0.
4. **M14 four-verb exclude-honouring reindex** — `touch` over a tree whose
   `[exclude]` set holds a malformed file stamps the date AND refreshes the
   INDEX cleanly (exit 0); the excluded file stays unindexed.
5. **M15 `project set`** — typo (`beto`) → exit 2 + `did you mean 'beta'?`
   + `--new-project` recovery hint, no write; existing value reassigns
   atomically (exit 0); archived doc byte-identical.
6. **M15 single-file `stamp`** — raw file → metadata block (title from H1,
   `Lifecycle: draft`, project from `.docs.toml`), body verbatim; re-stamp
   no-op bar `Updated:`; exactly one metadata block.
7. **M15 `--body-from` real-frontmatter detector** — prose body with
   `Reason:`/`Plan:` lines accepted (exit 0); `---`-fenced body refused
   (exit 2); ≥2-adjacent `{Lifecycle, Role, Updated}` cluster body refused
   (exit 2); refused docs not created.

## Phase 3 — TestPyPI rehearsal

_Executed 2026-06-03 (network egress authorized; sandbox off for the
upload/install/JSON probes)._

**Pre-checks.** `~/.pypirc` intact: mode 600; `[distutils]`/`[pypi]`/
`[testpypi]` sections; both `username = __token__`; both `password` lines
present; testpypi `repository = https://test.pypi.org/legacy/` (token
values never printed). TestPyPI bare `docs-cli` re-checked — **squatter
still parked** (`latest 0.1.0`, author `None`) → the `docs-cli-rehearsal`
detour continues. `docs-cli-rehearsal` had `1.3.0/1.4.0/1.5.0`; the
**1.6.0 slot was free**.

**Rehearsal build + upload.** Temporarily set `pyproject.toml`
`[project] name = "docs-cli-rehearsal"`; `rm -rf dist/ && python -m build`
→ `docs_cli_rehearsal-1.6.0-py3-none-any.whl` +
`docs_cli_rehearsal-1.6.0.tar.gz`; `twine check` both **PASSED**.
`twine upload --repository testpypi dist/*` → exit 0, visible at
**https://test.pypi.org/project/docs-cli-rehearsal/1.6.0/**.

**Install from TestPyPI** into `/tmp/docs-test-venv` via
`pip install --index-url https://test.pypi.org/simple/ --extra-index-url
https://pypi.org/simple/ docs-cli-rehearsal==1.6.0` → **succeeded first
try** (no index lag; per the runbook, `pip install` is the authoritative
signal, not the lagging JSON API).

**Smoke against the TestPyPI-served wheel:**

- `docs --version` → **`docs 0.0.0+local`** — **known-expected** (M13): the
  rehearsal installs as `docs-cli-rehearsal`, so
  `importlib.metadata.version("docs-cli")` misses and falls back. NOT a
  failure; the real `docs 1.6.0` string is proven by the canonical-name
  local wheel (Phase 2) and will be re-proven by the PyPI wheel (Phase 4).
- `install-skill` byte-identical (`diff` exit 0); `--symlink` → exit 2.
- `docs check tests/fixtures/trees/minimal/` → exit 0;
  `docs index --root docs/ --dry-run` → exit 0.
- Installed skill references carry no repo-relative `](../` links.
- **All seven M14 + M15 headline contracts re-run against the
  TestPyPI-served wheel → all PASS** (same assertions as Phase 2:
  37/37 sub-checks green).

**Rename reverted.** `pyproject.toml` `[project] name` restored to
`docs-cli`; **`git diff pyproject.toml` is empty**; `git status --short`
clean (dist/ gitignored). `dist/` left holding the rehearsal-named
artefacts as-is — Phase 4 will `rm -rf dist/` and rebuild canonical.

**No regressions.** The only deviation observed was the known-expected
`docs 0.0.0+local` rehearsal-name print; no packaging/metadata/install
regression surfaced. No forced `1.6.x` bump.

## Phase 4 — Real PyPI publish

_Pending — to be filled during the publish run._

## Phase 5 — Post-release

_Pending — to be filled during the publish run._

## Milestone-completion summary

_Pending — appended at M17 closeout with the published version,
wheel + sdist sha256, publish timestamp, chain-of-custody
result, and every deviation recorded for v1.7+._
