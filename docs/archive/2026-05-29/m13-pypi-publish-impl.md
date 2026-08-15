# M13 — Implementation Log

Lifecycle: archived
Role: log
Project: docs
Updated: 2026-08-14

Related:
- child-of: archive/2026-05-29/m13-pypi-publish.md
- pairs-with: archive/2026-05-29/m13-pypi-publish.md
- pairs-with: status.md

Revision:
- 2026-08-14: M27 one-time body-link migration; body-link destinations repaired (destination tokens only)

## Overview

Chronological log of work on M13 — PyPI publish 1.5.0.
Append a section per runbook phase (operator prep → pre-publish
prep → TestPyPI rehearsal → real PyPI publish → post-release)
with objective, actions, results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M13 — PyPI publish 1.5.0
- Started: 2026-05-29
- Progress: **Complete 2026-05-29** — `docs-cli==1.5.0` shipped
  to PyPI. All five runbook phases done in one
  `/ship-milestone M13` run (the conductor drove the
  release-runbook directly, since an operational publish
  milestone has no 10-phase TDD cycle).

(Note: doc-lifecycle status is in the front-matter `Lifecycle:`
field above. This section tracks milestone-implementation
progress, which is distinct.)

## Runbook Phase Progress

M13 has no TDD code phases — the runbook's sections are the
phases (mirrors M9/M11).

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Operator one-time prep | Complete | 2026-05-29 | `~/.pypirc` mode 600 + both token sections; PyPI `docs-cli` 200, 1.5.0 slot free; TestPyPI `docs-cli-rehearsal` 1.5.0 slot free; bare `docs-cli` squatter unchanged (0.1.0, author None); `gh` authed |
| 2. Pre-publish prep | Complete | 2026-05-29 | version pins all 1.5.0; quality gate 433 passed + ruff/format/mypy/`docs check`/`index --dry-run` clean; fresh build; twine check PASS; local-install smoke + 4 M12 contracts PASS |
| 3. TestPyPI rehearsal | Complete | 2026-05-29 | uploaded `docs-cli-rehearsal==1.5.0`; installed from TestPyPI; smoke + 3 behavioral contracts PASS; `docs --version` → `0.0.0+local` (rename-detour artifact, see summary); rename reverted, `git diff` clean |
| 4. Real PyPI publish | Complete | 2026-05-29 | CHANGELOG dated + committed (`c893c3d`); canonical rebuild; twine check PASS; uploaded; chain-of-custody bit-perfect; smoke + 4 contracts PASS against PyPI-served wheel |
| 5. Post-release | Complete | 2026-05-29 | `m13/milestone-setup` ff-merged to `main` + pushed; `v1.5.0` annotated tag + push; GitHub release; doc closeouts; milestone doc archived (impl log stays `Lifecycle: active`); INDEX + expected snapshot lockstep |

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

Per-release re-verification (the one-time bootstrap from M9 is
intact; these are the cheap rot/drift probes):

- `~/.pypirc` mode 600, carries `[pypi]` + `[testpypi]` with
  `username = __token__` and `pypi-…` token prefixes.
- PyPI `docs-cli` simple index → HTTP 200; `releases` =
  `[1.3.0, 1.4.0]`, **1.5.0 slot free**.
- TestPyPI `docs-cli-rehearsal` → `[1.3.0, 1.4.0]`, **1.5.0
  slot free**.
- Bare `docs-cli` on TestPyPI re-checked: still the M9-era
  squatter (`latest: 0.1.0`, author None) → rehearsal-name
  detour continues.
- `gh` authed as `ArtRichards`.

## Phase 2 — Pre-publish prep

- Version pins all `1.5.0`: `pyproject.toml` `version`;
  `__version__` via `importlib.metadata.version("docs-cli")`;
  `tests/test_packaging.py` A3 pinned `1.5.0`.
- CHANGELOG header `## 1.5.0 — UNRELEASED` (dated at Phase 4);
  body reads accurately (publish-survival wording from M12).
- **Quality gate (tree-wide): 433 passed** in ~14.5s; `ruff
  check` clean; `ruff format --check` clean (35 files); `mypy`
  clean (36 files); `docs check docs/` exit 0; `docs index
  --root docs/ --dry-run` exit 0 / idempotent.
- Fresh artefact build (`rm -rf dist/ && python -m build`):
  wheel `b8023fff…b70b`, sdist `c5f83c6d…9c39`; `twine 6.2.0`
  `twine check` PASS on both.
- Local-install smoke (wheel into `/tmp/docs-local-smoke`):
  `docs --version` → `docs 1.5.0`; `install-skill`
  byte-identical / no-op / `--symlink` exit 2; `docs check`
  minimal exit 0. Four M12 headline contracts all PASS against
  the local wheel.

## Phase 3 — TestPyPI rehearsal

- Squatter unchanged → temporarily renamed `[project] name` to
  `docs-cli-rehearsal`, rebuilt, `twine check` PASS.
- Uploaded to TestPyPI:
  https://test.pypi.org/project/docs-cli-rehearsal/1.5.0/.
- Installed from TestPyPI into `/tmp/docs-test-venv`
  (`--index-url` test + `--extra-index-url` pypi). Smoke:
  `install-skill` byte-identical / no-op / `--symlink` exit 2;
  `docs check` minimal exit 0; `docs index --dry-run` exit 0.
- Three behavioral M12 contracts PASS against the TestPyPI
  wheel (project rename round-trip byte-identical; touch
  outside-root exit 2 + unchanged; archive referring-edge
  rewrite).
- **Deviation:** `docs --version` printed `docs 0.0.0+local`,
  not `docs 1.5.0` — the M12 `importlib.metadata` SoT can't
  resolve a distribution installed as `docs-cli-rehearsal`, so
  it hits the documented `PackageNotFoundError` fallback. Not
  a regression (see Milestone-completion summary); the version
  string is verified against the canonical-name local (Phase 2)
  and PyPI (Phase 4) wheels.
- Reverted the rename; `git diff pyproject.toml` empty.

## Phase 4 — Real PyPI publish

- CHANGELOG header dated `## 1.5.0 — 2026-05-29`; committed on
  `m13/milestone-setup` as `c893c3d` (the chain-of-custody /
  tag-target commit).
- Fresh canonical rebuild (`name = "docs-cli"`): wheel
  `b8023fff…b70b`, sdist `c5f83c6d…9c39` — **byte-identical to
  the Phase 2 build** (`CHANGELOG.md` is not in the sdist; only
  `docs/`, unchanged between phases, affects it). `twine check`
  PASS.
- **Uploaded to PyPI:** https://pypi.org/project/docs-cli/1.5.0/.
- Installed from PyPI into `/tmp/docs-real-venv`: `docs
  --version` → `docs 1.5.0` (canonical name resolves the SoT
  correctly — confirms the Phase 3 artifact was purely the
  rename).
- **Chain-of-custody:** `pip download` the PyPI-served wheel,
  sha256 == local Phase 4 wheel (`b8023fff…b70b`) — bit-perfect.
- Smoke subset + all four M12 headline contracts PASS against
  the PyPI-served wheel.

## Phase 5 — Post-release

- Repo-visibility flip: N/A (public since M9).
- Doc closeouts landed on `m13/milestone-setup`: `status.md`
  (M12 + M13 rows → Complete; "Current milestone" + both
  "Next action" blocks rewritten), `plan.md` (M12 + M13 rows
  finalised; M12 `432/432` → `433/433` typo corrected; M13
  prose → shipped), this impl log, and the milestone doc
  (Phase Checklist + Deliverables + Success Criteria all
  ticked; completion summary appended).
- `docs/INDEX.md` regenerated; `tests/fixtures/expected/docs-INDEX.md`
  regenerated in lockstep; full pytest re-run GREEN.
- `m13/milestone-setup` ff-merged into `main` and pushed.
- `v1.5.0` annotated tag at `c893c3d` (the Phase 4 commit whose
  tree matches PyPI), pushed to `origin`.
- GitHub release `v1.5.0` created with notes sourced from the
  `## 1.5.0` CHANGELOG section.
- `docs archive` moved the milestone doc to
  `archive/2026-05-29/` and rewrote referring `Related:` edges
  automatically (the M12 feature — no manual edge fix-up needed,
  unlike M11). Impl log stays `Lifecycle: active` per the
  M8/M9/M10/M11 pattern.
- Token re-scope to project-`docs-cli` rolls forward as the M9
  open follow-on (async operator UI work; not a blocker).
- Scratch `/tmp/docs-*` dirs cleaned up.

## Milestone-completion summary

**M13 complete — `docs-cli==1.5.0` shipped to PyPI 2026-05-29**,
driven end-to-end via `/ship-milestone M13`. Because M13 is an
operational publish milestone (no TDD code phases), the
conductor walked [release-runbook.md](../../release-runbook.md)
directly on `m13/milestone-setup` rather than spinning up the
standard phases-1-4 / phases-5-10 sub-agent stack; the
operator explicitly authorized a fully-autonomous run including
the irreversible PyPI upload and `main` push.

- **PyPI:** https://pypi.org/project/docs-cli/1.5.0/ ·
  **TestPyPI rehearsal:**
  https://test.pypi.org/project/docs-cli-rehearsal/1.5.0/
- **Published sha256:** wheel
  `b8023fffb3393aeff5ac85943164a414916e06ea85e68502e167f0948e85b70b`;
  sdist
  `c5f83c6d57c63c7116e06a777eb0f0394968b0233fe15f0a084c2ab2c61f9c39`.
- **Chain-of-custody:** PyPI-served wheel byte-identical to the
  local Phase 4 build — bit-perfect (matches M11).
- **`v1.5.0`** annotated tag at `c893c3d`; GitHub release live.

### Deviations (carry forward to v1.6+)

1. **TestPyPI rehearsal wheel prints `docs 0.0.0+local`.** New
   interaction since the M12 `importlib.metadata` version-SoT
   refactor: the rehearsal renames the distribution to
   `docs-cli-rehearsal`, so `importlib.metadata.version("docs-cli")`
   raises `PackageNotFoundError` and falls back to the
   documented `0.0.0+local`. **Not a regression** — proven by
   the canonical-name local wheel (Phase 2 → `docs 1.5.0`) and
   the PyPI wheel (Phase 4 → `docs 1.5.0`). M9/M11 never saw
   this because `__version__` was a hardcoded literal pre-M12.
   The release-runbook's TestPyPI version probe gains a caveat:
   the `docs --version` contract must be checked against the
   canonical-name wheels, never the rehearsal wheel.
2. **`CHANGELOG.md` is not in the sdist.** Verified: the
   hatchling sdist carries `src/`, `docs/`, `tests/`,
   `README.md`, `LICENSE`, `pyproject.toml` — `tar tzf … |
   grep -c CHANGELOG` → 0. This corrects the runbook's "sdist
   captures docs/ + CHANGELOG.md" wording and explains the
   Phase 2 ≡ Phase 4 sdist sha (only the unchanged `docs/`
   feeds the sdist; the CHANGELOG date edit didn't touch it).
   No impact — the dated CHANGELOG ships via git + the GitHub
   release notes.

No `1.5.x` bump was forced — the rehearsal surfaced no
packaging defect. The runbook's internal hard gates (twine
check, clean rehearsal, bit-perfect chain-of-custody) all
passed; `1.5.0` published as-is.
