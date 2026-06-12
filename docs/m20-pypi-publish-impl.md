# M20 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-06-12

Related:
- child-of: archive/2026-06-12/m20-pypi-publish.md
- pairs-with: archive/2026-06-12/m20-pypi-publish.md
- pairs-with: status.md

## Overview

Chronological log of work on M20 — PyPI publish 1.6.5. Append a section per
runbook phase (operator prep → pre-publish prep → TestPyPI rehearsal → real
PyPI publish → post-release) with objective, actions, results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M20 — PyPI publish 1.6.5
- Started: 2026-06-12 (milestone-setup)
- Progress: **Complete 2026-06-12** — `docs-cli==1.6.5` shipped to PyPI, the
  publish-only counterpart to M19 (one-to-one, as M13 shipped M12 and M11
  shipped M10; M9 and M17 were the batched shapes). All five runbook phases
  done in one fully-autonomous pass (the conductor drove the release-runbook
  directly, since an operational publish milestone has no 10-phase TDD cycle).
  The operator authorized the irreversible real-PyPI upload + `main` push +
  `v1.6.5` tag + GitHub release up front (Step 0 resolution of Q1; Q2 → archive
  the M18 + M19 pairs + the M20 milestone doc at closeout). Chain-of-custody
  **bit-perfect for both wheel AND sdist** (M20 extended the M17 wheel-only
  check); all M19 headline contracts hold against the PyPI-served wheel.
  **NEW vs M17:** the Phase-5 closeout refreshed the host-machine skills
  (`docs install-skill --force` + workflow-skill sweep) per the CLAUDE.md
  skill-update-flow policy — and the sweep caught + fixed one real stale
  `--body-from` surface reference in the `project-foundation` workflow skill.

(Note: doc-lifecycle status is in the front-matter `Lifecycle:` field above.
This section tracks milestone-implementation progress, which is distinct.)

## Runbook Phase Progress

M20 has no TDD code phases — the runbook's sections are the phases (mirrors
M9/M11/M13/M17).

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Operator one-time prep | Complete | 2026-06-12 | `~/.pypirc` intact (mode 600; `[pypi]`+`[testpypi]`; both `username = __token__`; testpypi `repository = …/legacy/`; token prefixes `pypi-AgEI…`/`pypi-AgEN…`). PyPI `docs-cli` simple-index 200, releases {1.3.0,1.4.0,1.5.0,1.6.0} — **1.6.5 slot free**. TestPyPI squatter **unchanged** (`docs-cli` latest 0.1.0, author None) → rehearsal-name detour continues; `docs-cli-rehearsal` 1.6.5 slot free. `gh auth` OK (ArtRichards, `repo` scope). twine 6.2.0. |
| 2. Pre-publish prep | Complete | 2026-06-12 | Gate GREEN **540 passed**; ruff/format(39)/mypy(40 files)/`docs check docs/`/index-dry-run clean; INDEX == fixture snapshot byte-identical. Surface parity GREEN: `touch --help`/`check --help`/`new --help` match `## 1.6.5` surface; `--body-from` help = real detector (no "first 20 lines"); bundled `references/cli.md`+`convention.md` byte-identical to `docs/`. Fresh canonical 1.6.5 build; both `twine check` PASS; CHANGELOG not in sdist (0). Local-wheel smoke `docs 1.6.5`; install-skill byte-identical/no-op/`--symlink` exit 2; no `../` links. All M19 headline contracts PASS (local wheel). sha256 below. |
| 3. TestPyPI rehearsal | Complete | 2026-06-12 | Uploaded `docs-cli-rehearsal==1.6.5` (squatter parked → detour kept); both `twine check` PASS. Installed from TestPyPI first try (no index lag); baseline smoke + all M19 headline contracts PASS against the served wheel; `docs --version` → `docs 0.0.0+local` (known-expected, M13 rehearsal-name caveat). Rename reverted (`git diff pyproject.toml` empty); fresh canonical rebuild → dist/ holds real 1.6.5 candidates; both `twine check` PASS; canonical sha256 byte-identical to Phase-2 (re-recorded below). No forced 1.6.x bump. **GO.** |
| 4. Real PyPI publish | Complete | 2026-06-12 | CHANGELOG dated `## 1.6.5 — 2026-06-12` + stale "Built locally" lead-in dropped, committed `0855466` (the chain-of-custody / `v1.6.5` tag-target commit); fresh canonical rebuild from the dated commit; both `twine check` PASS; uploaded to PyPI; **chain-of-custody bit-perfect** (PyPI-served **wheel AND sdist** sha256 byte-identical to the local Phase-4 build); install from PyPI → `docs 1.6.5`; smoke + all M19 headline contracts PASS against the PyPI-served wheel. Published sha256 below. |
| 5. Post-release | Complete | 2026-06-12 | Annotated `v1.6.5` tag at `0855466` pushed to origin; GitHub release `v1.6.5` live with notes sourced from `## 1.6.5`; **host skills refreshed** (`docs install-skill --force` from the PyPI-served venv → host `~/.claude/skills/docs` byte-identical to the published wheel's bundled skill; workflow-skill sweep found + fixed one stale `--body-from` "first 20 lines" reference in `project-foundation` — NEW vs M17); doc closeouts landed (status/plan/INDEX + dogfood snapshot + the M18 pair + M19 pair archival); `docs archive` ran (M18 + M19 both pairs **and** the M20 milestone doc → `archive/2026-06-12/`; M20 impl log + release-runbook + status stay `Lifecycle: active`). Token re-scope rolls forward as the M9 open follow-on. |

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

_Executed 2026-06-12 against `main` (HEAD `048bcab`, the m20(setup) commit).
Per-release re-verification — cheap probes that catch token rot / ownership
drift before the network-mutating phases._

- **`~/.pypirc` intact.** Mode `600`; `[distutils]`/`[pypi]`/`[testpypi]`
  sections present; both `username = __token__`; testpypi `repository =
  https://test.pypi.org/legacy/`; token prefixes `pypi-AgEI…` (pypi) /
  `pypi-AgEN…` (testpypi) — values never printed.
- **PyPI `docs-cli` 1.6.5 slot free.** `curl -sI
  https://pypi.org/simple/docs-cli/` → `HTTP/2 200`; JSON `info.version`
  (latest) = `1.6.0`; `releases` keys = `{1.3.0, 1.4.0, 1.5.0, 1.6.0}` —
  **1.6.5 absent** → slot free (PyPI rejects re-uploads even after yank).
- **TestPyPI squatter unchanged.** Bare `docs-cli` on TestPyPI still
  `latest 0.1.0`, `author None`, releases `{0.1.0}` → the
  `docs-cli-rehearsal` rename detour continues (M9/M11/M13/M17 posture).
  `docs-cli-rehearsal` releases `{1.3.0, 1.4.0, 1.5.0, 1.6.0}` — **1.6.5
  slot free**.
- **gh auth.** Logged in to github.com as `ArtRichards`, active account,
  ssh git protocol, token scopes include `repo` (sufficient for the
  Phase-5 tag push + GitHub release — not run by this phase).
- **Tooling.** `twine 6.2.0` (same version smoke-tested M6→M17).

## Phase 2 — Pre-publish prep

_Executed 2026-06-12 against `main` (HEAD `048bcab`)._

**Version + CHANGELOG verification.** `pyproject.toml` `version = "1.6.5"`,
`name = "docs-cli"`; `src/docs_cli/cli.py` `__version__` reads through
`importlib.metadata.version("docs-cli")` with the `0.0.0+local`
`PackageNotFoundError` fallback (M12 SoT); `tests/test_packaging.py` A3/B1/B2/C2
pinned at `1.6.5`. `CHANGELOG.md` carries `## 1.6.5 — UNRELEASED` with the M19
surface (touch `--check`, `[check] stale_days` + provenance, `--body-from` help
fix) and publish-survival wording. **Phase-4 NOTE for the conductor:** the
section's lead-in line "Built locally; a later operator-driven milestone
publishes to PyPI." describes state, not a deferral, but reads stale
post-publish — drop/rewrite it as part of the Phase-4 `UNRELEASED` → date edit
(the already-anticipated edit per the milestone-doc Decision "CHANGELOG
publish-survival wording already locked"). **Not edited here — dating the
CHANGELOG is Phase 4's first act.**

**Surface parity (help + bundled skill) — GREEN:**

- `docs touch --help` describes `--check` (max(touch, check) fold + failed-touch
  short-circuit) and `--stale N` (requires `--check`; absent → `[check]
  stale_days` config default) — matches the M19 D1 CHANGELOG surface.
- `docs check --help` is the base surface (`--stale`/`--json`/`--exclude`).
- `docs new --help` `--body-from` names the **real** detector ("a leading
  `---` fence or ≥2 adjacent `{Lifecycle, Role, Updated}` lines; lone prose
  like a `Plan:` line is fine") — the M19 D3 fix. The stale "first 20 lines"
  wording is gone everywhere: `cli.py` help (0), bundled skill tree (0),
  `docs/cli.md` (0).
- Bundled refs byte-identical: `diff -q src/docs_cli/skill/references/cli.md
  docs/cli.md` and the `convention.md` pair both report **byte-identical**.

**Quality gate (tree-wide) — all GREEN:**

- `pytest tests/ -q` → **540 passed** in ~24s (matches the expected 540 —
  533 at M19 Phase 8 + 7 from the Step-2 review).
- `ruff check .` → All checks passed.
- `ruff format --check .` → 39 files already formatted.
- `mypy` → Success, no issues in 40 source files.
- `docs check docs/` → no violations (exit 0).
- `docs index --root docs/ --dry-run` → exit 0; output byte-identical to the
  on-disk `docs/INDEX.md` (idempotent).
- INDEX lockstep: `docs/INDEX.md` **byte-identical** to
  `tests/fixtures/expected/docs-INDEX.md`.

**Fresh artifact build.** `rm -rf dist/` (gitignored — cleared whatever was
there); `python -m build` produced `docs_cli-1.6.5-py3-none-any.whl` +
`docs_cli-1.6.5.tar.gz`. **Phase-2 sha256 (chain-of-custody anchors):**

- wheel `docs_cli-1.6.5-py3-none-any.whl`:
  `aba36e92d92363958f0b9e91e52a769e2f10f69d92437a44c83cebeef396b4e0`
- sdist `docs_cli-1.6.5.tar.gz`:
  `78cef9cc89e0affa7a187111987ed39d608e23d53038c78c59a725cc916e997c`

`twine check dist/*` → both **PASSED**. `CHANGELOG.md` not in the sdist
(`tar tzf … | grep -c CHANGELOG` → 0; known-expected per M13).

**Local-install smoke (no PyPI), `/tmp/docs-local-smoke`, canonical wheel:**

- `docs --version` → `docs 1.6.5` (canonical name resolves the SoT).
- `docs --help` lists the full
  `index/new/archive/mv/touch/stamp/project/check/list/migrate/install-skill`
  surface (incl. `install-skill`).
- `install-skill --dest /tmp/skill-smoke` → exit 0; `diff -ru
  src/docs_cli/skill /tmp/skill-smoke` empty (byte-identical); re-run → exit 0
  no-op; `--symlink` → exit 2.
- `docs check tests/fixtures/trees/minimal/` → exit 0.
- Installed skill references carry no repo-relative `](../` links (grep → 0).

**The M19 headline contracts (local wheel) — all PASS:**

1. **`docs touch --check` exit fold (clean):** `touch alpha --check` over a
   tree with all docs fresh → exit 0, `no violations found` (touch's
   end-of-batch reindex then a bare check, folded `max(touch, check)`).
2. **`docs touch --check --stale N` exit fold (stale present):** `touch alpha
   --check --stale 30` with a `Lifecycle: active` doc 162 days stale → exit 1
   (stale-only fold); finding carries the CLI provenance suffix `via --stale`.
3. **`--stale` requires `--check`:** `touch alpha --stale 5` (no `--check`) →
   hard exit 2, `docs: touch: --stale requires --check`; the file **and** the
   INDEX are byte-unchanged (no reindex ran).
4. **`[check] stale_days` arms bare check + CLI override + non-integer
   refusal:**
   - bare `docs check` with **no** `[check]` section → exit 0 (stale rule
     disarmed; today's behaviour preserved).
   - bare `docs check` with `[check] stale_days = 30` → exit 1; finding =
     `stale threshold 30, set in .docs.toml [check] stale_days` (config-sourced
     provenance variant — the per-tree opt-in arming bare check).
   - `docs check --stale 90` overrides the config → `stale threshold 90, via
     --stale` (CLI-sourced provenance variant; CLI wins).
   - `[check] stale_days = "14"` (TOML string) → exit 2, `malformed .docs.toml:
     [check] stale_days must be an integer`, **no traceback**.
5. **`docs new --body-from` help (D3):** the installed wheel's `--body-from`
   help names the real detector; `grep -c 'first 20 lines'` → 0.

## Phase 3 — TestPyPI rehearsal

_Executed 2026-06-12 (network egress authorized for the upload/install/JSON
probes)._

**Pre-checks (recap of Phase-1 probes).** `~/.pypirc` intact (mode 600, both
sections, both `username = __token__`, testpypi `repository = …/legacy/`; token
values never printed). TestPyPI bare `docs-cli` re-checked — **squatter still
parked** (`latest 0.1.0`, author `None`) → the `docs-cli-rehearsal` detour
continues. `docs-cli-rehearsal` had `{1.3.0, 1.4.0, 1.5.0, 1.6.0}`; the **1.6.5
slot was free**.

**Rehearsal build + upload.** Temporarily set `pyproject.toml` `[project] name =
"docs-cli-rehearsal"` (version unchanged at `1.6.5`); `rm -rf dist/ && python -m
build` → `docs_cli_rehearsal-1.6.5-py3-none-any.whl` +
`docs_cli_rehearsal-1.6.5.tar.gz`; `twine check` both **PASSED**. `twine upload
--repository testpypi dist/*` → exit 0, visible at
**https://test.pypi.org/project/docs-cli-rehearsal/1.6.5/**.

**Install from TestPyPI** into `/tmp/docs-test-venv` via `pip install
--index-url https://test.pypi.org/simple/ --extra-index-url
https://pypi.org/simple/ docs-cli-rehearsal==1.6.5` → **succeeded first try**
(no index lag; per the runbook, `pip install` is the authoritative signal, not
the lagging JSON API).

**Smoke against the TestPyPI-served wheel:**

- `docs --version` → **`docs 0.0.0+local`** — **known-expected** (M13): the
  rehearsal installs as `docs-cli-rehearsal`, so
  `importlib.metadata.version("docs-cli")` misses and falls back to the
  documented `0.0.0+local`. NOT a failure; the real `docs 1.6.5` string is
  proven by the canonical-name local wheel (Phase 2) and will be re-proven by
  the PyPI wheel (Phase 4).
- `install-skill` byte-identical (`diff` empty); re-run no-op exit 0;
  `--symlink` → exit 2; no repo-relative `](../` links in the installed skill.
- `docs check tests/fixtures/trees/minimal/` → exit 0; `docs index --root docs/
  --dry-run` → exit 0.
- **All M19 headline contracts re-run against the TestPyPI-served wheel → all
  PASS** (same assertions as Phase 2): `touch --check` clean → exit 0;
  `touch --check --stale 30` → exit 1 `via --stale`; `--stale` without
  `--check` → exit 2 byte-unchanged; bare check disarmed → exit 0; `[check]
  stale_days = 30` arms bare check → exit 1 `set in .docs.toml [check]
  stale_days`; CLI `--stale 90` overrides → `via --stale`; non-integer → exit 2
  `malformed .docs.toml: [check] stale_days must be an integer` (no traceback);
  `--body-from` help = real detector, "first 20 lines" → 0.

**Rename reverted + canonical rebuild.** `pyproject.toml` `[project] name`
restored to `docs-cli`; **`git diff pyproject.toml` is empty**; tracked tree
clean (dist/ gitignored). Per the runbook, the rehearsal artefacts were
discarded and a **fresh canonical rebuild** ran so dist/ holds the real 1.6.5
candidates: `rm -rf dist/ && python -m build` → `docs_cli-1.6.5-py3-none-any.whl`
+ `docs_cli-1.6.5.tar.gz`; `twine check dist/*` → both **PASSED**. **Re-recorded
canonical sha256:**

- wheel `docs_cli-1.6.5-py3-none-any.whl`:
  `aba36e92d92363958f0b9e91e52a769e2f10f69d92437a44c83cebeef396b4e0`
  — **byte-identical to the Phase-2 wheel** (`src/` unchanged → reproducible
  build across the rehearsal detour).
- sdist `docs_cli-1.6.5.tar.gz`:
  `78cef9cc89e0affa7a187111987ed39d608e23d53038c78c59a725cc916e997c`
  — **byte-identical to the Phase-2 sdist** (`docs/` untouched between the
  Phase-2 and post-rehearsal builds; CHANGELOG isn't in the sdist anyway).

**No regressions.** The only deviation observed was the known-expected `docs
0.0.0+local` rehearsal-name print; no packaging/metadata/install regression
surfaced. **No forced 1.6.x bump.** The runbook's internal hard gates (twine
check ×2, clean first-try TestPyPI install, all M19 contracts green against the
served wheel, empty `git diff pyproject.toml` after revert) all passed.

**VERDICT (this agent's scope, pre-publish + rehearsal): GO** for the real PyPI
publish (Phase 4). dist/ holds the canonical 1.6.5 candidates (wheel
`aba36e92…`, sdist `78cef9cc…`); the conductor's Phase-4 first act is to date
the CHANGELOG (`## 1.6.5 — UNRELEASED` → `## 1.6.5 — <publish-date>`) and drop
the stale "Built locally" lead-in, commit, then fresh canonical rebuild before
upload.

## Phase 4 — Real PyPI publish

_Executed 2026-06-12 (network egress authorized for the upload/install/download
probes)._

- **CHANGELOG dated.** `## 1.6.5 — UNRELEASED` → `## 1.6.5 — 2026-06-12`; the
  stale lead-in line "Built locally; a later operator-driven milestone publishes
  to PyPI." dropped (so the dated section reads like the dated `## 1.6.0`
  section). Committed on `main` as **`0855466`** — the chain-of-custody /
  `v1.6.5` tag-target commit whose tree state matches what's in PyPI.
- **Fresh canonical rebuild** from the dated commit (`[project] name =
  "docs-cli"`): `rm -rf dist/ && python -m build` produced
  `docs_cli-1.6.5-py3-none-any.whl` + `docs_cli-1.6.5.tar.gz`; `twine check
  dist/*` → both **PASSED**. **Phase-4 sha256:**
  - wheel:
    `aba36e92d92363958f0b9e91e52a769e2f10f69d92437a44c83cebeef396b4e0`
    — **byte-identical to the GO-report (Phase-2/3) wheel** (`src/` unchanged →
    reproducible build; `CHANGELOG.md` is **not** in the wheel — verified the
    wheel manifest carries only `docs_cli/` + `docs_cli-1.6.5.dist-info`, so the
    Phase-4 date edit could not move the wheel sha).
  - sdist:
    `f9de1eb49ff84271969c6b4b7e0faef93a138bea0813cb1effd1d1314eff12be`
    — **differs from the GO-report sdist** (`78cef9cc…`) ONLY because `docs/`
    evolved between the Phase-3 build and this dated commit (the impl-log
    Phase-2/3 GREEN/GO commit `46385dc` updated `docs/m20-pypi-publish-impl.md`);
    `CHANGELOG.md` is not in the sdist, so the Phase-4 date edit did not move the
    sha — `docs/` drift did. This is the M13/M17 generalisation (cross-commit
    `docs/` drift moves the sdist sha while the wheel stays bit-stable). **The
    dated-commit build is canonical** — built from HEAD `0855466`, the tree the
    `v1.6.5` tag points at.
- **Uploaded to PyPI:** `twine upload dist/*` → exit 0, visible at
  **https://pypi.org/project/docs-cli/1.6.5/**.
- **Verified live.** `https://pypi.org/pypi/docs-cli/1.6.5/json` → HTTP 200; the
  project page → HTTP 200. The aggregate `/pypi/docs-cli/json` `releases` array
  lagged (still listed 1.6.0 as latest for ~minutes — the M11 JSON-cache-lag
  known-expected); `pip install` (the authoritative signal) resolved 1.6.5 first
  try.
- **Install from PyPI** into a fresh `/tmp/docs-real-venv`:
  `pip install docs-cli==1.6.5` → `docs --version` → **`docs 1.6.5`** (canonical
  name resolves the `importlib.metadata` SoT — confirms the Phase-3
  `0.0.0+local` was purely the rehearsal-name detour).
- **Chain-of-custody — BIT-PERFECT (wheel AND sdist).** `pip download --no-deps`
  (binary) + `pip download --no-deps --no-binary :all:` (sdist) pulled both
  PyPI-served artefacts; `sha256sum` of each == the local Phase-4 build:
  - PyPI-served wheel `aba36e92…` == local `aba36e92…`.
  - PyPI-served sdist `f9de1eb4…` == local `f9de1eb4…`.
  Fifth release running (M11 + M13 + M17 + M20). M17 only chain-of-custody'd the
  wheel; M20 additionally confirmed the sdist is bit-perfect.
- **Smoke + all M19 headline contracts re-run against the PyPI-served wheel →
  all PASS:**
  - `docs --version` → `docs 1.6.5`; `docs --help` lists the full
    `index/new/archive/mv/touch/stamp/project/check/list/migrate/install-skill`
    surface.
  - `install-skill` byte-identical (`diff -ru` empty) / re-run no-op exit 0 /
    `--symlink` exit 2; `docs check tests/fixtures/trees/minimal/` exit 0;
    installed skill references carry no repo-relative `](../` links (grep → 0).
  - 1. **`docs touch --check` exit fold (clean)** — `touch alpha --check` over a
       fresh tree → exit 0, `no violations found`.
    2. **`docs touch --check --stale 30` exit fold (stale present)** — an
       untouched 162-day-stale sibling → exit 1 (stale-only fold); finding
       carries the CLI provenance suffix `via --stale`.
    3. **`--stale` requires `--check`** — `touch alpha --stale 5` (no `--check`)
       → hard exit 2, `docs: touch: --stale requires --check`; the file AND the
       INDEX byte-unchanged (sha256 before == after; no reindex ran).
    4. **`[check] stale_days` arms bare check + CLI override + non-integer
       refusal** — bare `docs check`, no `[check]` section → exit 0 (rule
       disarmed); `[check] stale_days = 30` arms bare check → exit 1, finding
       `set in .docs.toml [check] stale_days` (config provenance); `docs check
       --stale 90` overrides → `via --stale` (CLI wins); `[check] stale_days =
       "14"` (TOML string) → exit 2, `malformed .docs.toml: [check] stale_days
       must be an integer`, **no traceback**.
    5. **`docs new --body-from` help (D3)** — the installed wheel's
       `--body-from` help names the real detector (a leading `---` fence or ≥2
       adjacent `{Lifecycle, Role, Updated}` lines); `grep -c 'first 20 lines'`
       → 0.
  - The harness was first validated against the in-repo `.venv` wheel (9/9
    PASS) so a harness bug could not masquerade as a contract failure, then run
    against the PyPI-served wheel (9/9 PASS).

## Phase 5 — Post-release

_Executed 2026-06-12 on `main` as the M20 closeout._

- **Tag + GitHub release.** Annotated `v1.6.5` tag created at **`0855466`** (the
  Phase-4 dated-CHANGELOG commit whose tree matches PyPI) with message
  `docs-cli 1.6.5 — post-edit validation ergonomics (M19)` (matches the
  `v1.6.0` tag-message format) and pushed to `origin`. GitHub release `v1.6.5`
  created via `gh release create --title "docs-cli 1.6.5"` with notes sourced
  from the `## 1.6.5` CHANGELOG section — live at
  **https://github.com/ArtRichards/docs-cli/releases/tag/v1.6.5**. No
  `gh release edit` amend needed (the CHANGELOG was authored with
  publish-survival wording; the M11 deviation did not recur).
- **Host-machine skill refresh (NEW vs M17 — CLAUDE.md policy).** From the
  PyPI-served venv: `docs install-skill --force --dest ~/.claude/skills/docs` →
  exit 0, reported `already matches the bundled skill; no-op` (the host copy was
  pre-materialised 2026-06-12 from the same surface). `diff -r
  ~/.claude/skills/docs` against the published wheel's bundled skill (in the
  PyPI venv's `site-packages/docs_cli/skill`) → **byte-identical (exit 0)**.
  Workflow-skill sweep of `~/.claude/skills/{sync-and-commit,create-milestones,
  project-foundation,ship-milestone}` for the now-published 1.6.5 surface
  (`touch --check`, `[check] stale_days`): all reference the published surface,
  **except** one genuine stale-surface drift — `project-foundation/references/
  foundation-playbook.md:71` still described `docs new --body-from` with the
  pre-M19-D3 "refuses content whose first 20 lines contain a `Label: value`
  line" heuristic. Corrected in place to the real detector (a leading `---`
  fence or ≥2 adjacent `{Lifecycle, Role, Updated}` lines; lone prose is fine),
  matching the published 1.6.5 behaviour and `docs/cli.md`. After the fix,
  `grep -rl 'first 20 lines'` across all four workflow skills → 0.
  `project-foundation`'s README explicitly pins `v1.6.5 (M19+)` for the `[check]
  stale_days` window — it tracks the published surface correctly. (The host-skill
  edit is host state under `~/.claude/skills/`, outside the repo commit.)
- **Doc closeouts landed** on `main`:
  - `m20-pypi-publish-impl.md` (this log): Phase 4 + Phase 5 sections;
    Runbook-Phase table rows 4 + 5 → Complete; milestone-completion summary
    below. Stays `Lifecycle: active`.
  - `m20-pypi-publish.md`: Phase Checklist + Deliverables + Success Criteria
    ticked with evidence; milestone-completion summary appended; front-matter
    flipped for the archive step.
  - `status.md` + `plan.md`: M18 + M19 + M20 rows finalised; "Current
    milestone" + "Next action" rewritten to the post-publish narrative
    (`docs-cli 1.6.5` shipped; next implementation milestone unscoped).
  - `release-runbook.md`: a `### From M20 (2026-06-12, docs-cli==1.6.5)`
    cumulative-lessons section appended.
  - `docs/INDEX.md` regenerated (`docs index --root docs/`);
    `tests/fixtures/expected/docs-INDEX.md` regenerated in lockstep.
- **Archival (the Q2 decision).** Via `.venv/bin/docs archive` (never a
  hand-move), to `archive/2026-06-12/`:
  - M18 pair: archived the M18 impl log with
    `--cascade-only "m18-archive-edge-integrity.md"` — `child-of` pulls the
    milestone doc, so both land together edge-clean (the M17 pattern).
  - M19 pair: archived the M19 impl log with
    `--cascade-only "m19-post-edit-validation.md"` — same shape.
  - M20 milestone doc `m20-pypi-publish.md` archived **without** cascade (its
    `pairs-with` edges to the runbook/status/M18/M19 must not pull anything;
    `parent-of` to this impl log is not a cascade verb). This repointed **this
    impl log's** `child-of`/`pairs-with` edges to the
    `archive/2026-06-12/m20-pypi-publish.md` path automatically, while the impl
    log stays `Lifecycle: active`.
  - Live referrers (`plan.md`, `status.md`, and this impl log) repointed
    automatically by the M12 + M18 edge machinery. `docs check docs/` exit 0
    after every archive op and at the end (no broken refs). The M20 impl log,
    the release-runbook, and `status.md` stay `Lifecycle: active` per the
    M8/M9/M10/M11/M13/M17 pattern.
- **Token re-scope** to project-`docs-cli` rolls forward as the M9 open
  follow-on (async operator UI work; not a blocker).
- Scratch `/tmp/docs-*` dirs cleaned up.

## Milestone-completion summary

**M20 complete — `docs-cli==1.6.5` shipped to PyPI 2026-06-12**, the
publish-only counterpart to **M19** shipped **one-to-one** (as M13 shipped M12
and M11 shipped M10; M9 and M17 were the batched shapes). Driven end-to-end as
a fully-autonomous run walking [release-runbook.md](release-runbook.md)
directly (M20 has no TDD code phases; the runbook sections are the phases); the
operator authorized the irreversible PyPI upload + `main` push + tag + release
up front (Q1 resolution). **NEW vs M17:** the closeout refreshed the
host-machine skills per the CLAUDE.md skill-update-flow policy.

- **PyPI:** https://pypi.org/project/docs-cli/1.6.5/ ·
  **TestPyPI rehearsal:**
  https://test.pypi.org/project/docs-cli-rehearsal/1.6.5/ ·
  **GitHub release:** https://github.com/ArtRichards/docs-cli/releases/tag/v1.6.5
- **Published artefact sha256 (chain-of-custody anchors):**
  - wheel `docs_cli-1.6.5-py3-none-any.whl`:
    `aba36e92d92363958f0b9e91e52a769e2f10f69d92437a44c83cebeef396b4e0`
  - sdist `docs_cli-1.6.5.tar.gz`:
    `f9de1eb49ff84271969c6b4b7e0faef93a138bea0813cb1effd1d1314eff12be`
- **Chain-of-custody — BIT-PERFECT (wheel AND sdist).** Both PyPI-served
  artefact sha256s are byte-identical to the local Phase-4 build. Fifth release
  running (M11 + M13 + M17 + M20); M20 additionally verified the sdist (M17
  checked only the wheel).
- **Quality gate at publish:** 540 passed; ruff / ruff format / mypy clean
  tree-wide; `docs check docs/` exit 0; `docs index --root docs/ --dry-run`
  idempotent.
- **Smoke + all M19 headline contracts** verified against the PyPI-served wheel:
  `docs --version` → `docs 1.6.5`; `install-skill` byte-identical / no-op /
  `--symlink` exit 2; `docs check tests/fixtures/trees/minimal/` exit 0;
  installed skill refs carry no `../` links; and the M19 contracts (`touch
  --check` clean → 0; `touch --check --stale 30` stale-present → 1 `via
  --stale`; `--stale` without `--check` → 2, file+INDEX byte-unchanged; bare
  check disarmed → 0; `[check] stale_days = 30` arms bare check → 1 `set in
  .docs.toml [check] stale_days`; CLI `--stale 90` overrides → `via --stale`;
  non-integer stale_days → 2 clean no-traceback; `--body-from` help = real
  detector).
- **`v1.6.5`** annotated tag at **`0855466`** (the Phase-4 dated-CHANGELOG
  commit whose tree matches PyPI); GitHub release live with notes sourced from
  the `## 1.6.5` CHANGELOG section.
- **Host-machine skills refreshed (NEW vs M17):** `~/.claude/skills/docs`
  byte-identical to the published wheel's bundled skill; one stale `--body-from`
  surface reference in the `project-foundation` workflow skill found and
  corrected to the published 1.6.5 wording.

### Deviations (carry forward to v1.7+)

1. **TestPyPI rehearsal wheel prints `docs 0.0.0+local`, not `docs 1.6.5`**
   (Phase 3, recorded at the GO report). Known-expected since the M12
   `importlib.metadata` version-SoT refactor: the rehearsal renames the
   distribution to `docs-cli-rehearsal`, so `importlib.metadata.version(
   "docs-cli")` raises `PackageNotFoundError` and falls back to the documented
   `0.0.0+local`. **Not a regression** — the real `docs 1.6.5` string is proven
   by the canonical-name local wheel (Phase 2) and the PyPI wheel (Phase 4).
2. **`CHANGELOG.md` is not shipped inside the sdist (or the wheel).**
   Known-expected since M13: the hatchling sdist captures `src/`, `docs/`,
   `tests/`, `README.md`, `LICENSE`, `pyproject.toml` (`tar tzf … | grep -c
   CHANGELOG` → 0); the wheel carries only `docs_cli/` + dist-info. Consequence
   at M20: the **wheel** sha was byte-identical to the GO-report build (`src/`
   unchanged → reproducible), while the **sdist** sha *moved* (`78cef9cc…` →
   `f9de1eb4…`) — but ONLY because `docs/` evolved between the GO-report build
   and the Phase-4 dated commit (the impl-log Phase-2/3 commit `46385dc`), not
   because of the Phase-4 CHANGELOG date edit. Recorded so the moved sdist sha is
   not mistaken for a regression. The dated CHANGELOG reaches users via the git
   repo + the GitHub release notes.
3. **Host-skill drift caught by the NEW M20 sweep.** The `project-foundation`
   workflow skill (a host skill, not the bundled `docs` skill) still carried the
   pre-M19-D3 `--body-from` "first 20 lines" description. The M20 host-skill
   refresh step (new vs M17) caught and fixed it. This is the first time the
   workflow-skill sweep found a real drift — it validates adding the sweep to
   the publish closeout. **v1.7+ candidate:** consider a lint that greps the
   workflow skills' docs-cli prescriptions against the bundled `references/`
   surface so drift is caught in-repo, not only at publish.

No `1.6.x` bump was forced — the TestPyPI rehearsal surfaced no packaging
defect (the `0.0.0+local` print is the rename-detour artifact above), so `1.6.5`
published as-is. The runbook's internal hard gates (twine check ×2, clean
first-try TestPyPI + PyPI install, bit-perfect chain-of-custody, all M19
contracts green against the served wheel) all passed. Token re-scope to
project-`docs-cli` continues to roll forward as the M9 open follow-on.
