# M24 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-07-03

Related:
- child-of: archive/2026-07-03/m24-pypi-publish.md
- pairs-with: archive/2026-07-03/m24-pypi-publish.md
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
- Progress: **Complete 2026-07-03 — `docs-cli==1.8.0` shipped to PyPI.** The
  batched publish of the post-1.6.5 train (M21 update-check + M22 doc guidance +
  M23 agent-aware install-skill) as one public release (M17/M9 batched
  precedent). All five runbook phases done; chain-of-custody **bit-perfect for
  both wheel AND sdist** (wheel `29ac3ced…`, sdist `62a29285…`); all M21 + M23
  headline contracts hold against the PyPI-served wheel; `v1.8.0` annotated tag
  at `1a01f74` + GitHub release; host skills refreshed. Driven under **D3**
  ("author now, confirm at the gate") — the operator authorized the irreversible
  upload + `main` push + tag + release at the Phase-4 gate. Decisions: **D1**
  batched 1.8.0; **D2** folded CHANGELOG 1.7.0 → 1.8.0 (1.7.0 skipped on PyPI);
  **D4** M23 OQ-1/OQ-2 confirmed as-shipped; **D5** closeout archived the
  M21+M22+M23 pairs + the M24 milestone doc to `archive/2026-07-03/` (this impl
  log stays `Lifecycle: active`).

(Note: doc-lifecycle status is in the front-matter `Lifecycle:` field above.
This section tracks milestone-implementation progress, which is distinct.)

## Runbook Phase Progress

M24 has no TDD code phases — the runbook's sections are the phases (mirrors
M9/M11/M13/M17/M20).

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Operator one-time prep | Complete | 2026-07-03 | `~/.pypirc` intact (600; `[pypi]`+`[testpypi]`; both `__token__`; testpypi `…/legacy/`; prefixes `pypi-AgE…`). PyPI `docs-cli` simple-index 200, releases {1.3.0,1.4.0,1.5.0,1.6.0,1.6.5} — **1.8.0 slot free** (1.7.0 absent → skipped). TestPyPI squatter unchanged (`docs-cli` 0.1.0, author None) → rehearsal detour continues; `docs-cli-rehearsal` 1.8.0 slot free. `gh` OK (ArtRichards, `repo` scope). twine 6.2.0, build 1.5.0. |
| 2. Pre-publish prep | Complete | 2026-07-03 | Version SoT `1.8.0` (`__version__` via `importlib.metadata`); packaging pins 1.8.0. Surface parity GREEN: bundled `references/{cli,convention}.md` byte-identical to `docs/`; zero "Claude Code skill" residue. Gate GREEN **636 passed**; ruff/format(43)/mypy(44)/`docs check docs/`/index-dry-run idempotent; INDEX == fixture. Fresh build: wheel `29ac3ced…`, sdist `295ba009…`; both `twine check` PASS; CHANGELOG not in sdist (0). Local-wheel smoke `docs 1.8.0`; M23 contracts (dest record path-only `{"dest":"/tmp/skill-smoke"}`, byte-identical, no-op, `--symlink` exit 2, non-TTY no-dest → default exit 0, "agent skill" wording); M21 contracts (both notice lines to STDERR, exit parity, `--json` stdout-clean, full suppression matrix 0). |
| 3. TestPyPI rehearsal | Complete | 2026-07-03 | Uploaded `docs-cli-rehearsal==1.8.0` (squatter parked → detour kept); both `twine check` PASS. Installed from TestPyPI first try. Smoke: M23 install-skill contracts PASS against served wheel (dest byte-identical, `--symlink` exit 2, recorded dest path-only, "agent skill"); `docs --version` → `docs 0.0.0+local` (known-expected M13 rename caveat); M21 notice **correctly does not fire** under the rehearsal name (`0.0.0+local` fails the fail-closed version compare — verified against the canonical local wheel Phase 2 instead); `--json` stdout clean. Rename reverted (`git diff pyproject.toml` empty); canonical rebuild wheel `29ac3ced…` **byte-identical to Phase 2**, sdist `cb4944c6…` moved via `docs/` drift (Phase-1/2 log edits; CHANGELOG in neither artefact). Both `twine check` PASS. **GO.** |
| 4. Real PyPI publish | Complete | 2026-07-03 | CHANGELOG folded+dated `## 1.8.0 — 2026-07-03` (1.7.0 → 1.8.0, header dropped), committed `1a01f74` (the chain-of-custody / `v1.8.0` tag-target commit) + pushed `main`; fresh canonical rebuild → wheel `29ac3ced…` (**byte-identical to Phase 2/3**), sdist `62a29285…` (re-anchored at the tag-target commit); both `twine check` PASS; **uploaded to PyPI**; install from PyPI first try → `docs 1.8.0`; **chain-of-custody BIT-PERFECT** (PyPI-served wheel `29ac3ced…` AND sdist `62a29285…` byte-identical to local); smoke + all M21 + M23 headline contracts PASS against the PyPI-served wheel. |
| 5. Post-release | Complete | 2026-07-03 | Annotated `v1.8.0` tag at `1a01f74` pushed; GitHub release live with `## 1.8.0` notes; **host skills refreshed** (`docs install-skill --force` from the published wheel → host `docs` byte-identical; workflow-skill sweep found NO docs-cli drift — M21/M23 added surfaces none of the workflow skills prescribe); doc closeouts (status/plan/INDEX + fixture) landed; `docs archive` swept the M21 + M22 + M23 pairs + the M24 milestone doc to `archive/2026-07-03/` (M24 impl log + release-runbook + status stay active). Token re-scope rolls forward as the M9 follow-on. |

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

_Executed 2026-07-03 against `main` (HEAD `d9b4458`, the m24(setup) commit).
Per-release re-verification — cheap probes before the network-mutating phases._

- **`~/.pypirc` intact.** Mode `600`; `[distutils]`/`[pypi]`/`[testpypi]`
  present; both `username = __token__`; testpypi `repository =
  https://test.pypi.org/legacy/`; token prefixes `pypi-AgE…` (values never
  printed).
- **PyPI `docs-cli` 1.8.0 slot free.** `curl -sI
  https://pypi.org/simple/docs-cli/` → `HTTP/2 200`; JSON `info.version`
  (latest) = `1.6.5`; `releases` = `{1.3.0, 1.4.0, 1.5.0, 1.6.0, 1.6.5}` —
  **1.8.0 absent** → slot free. `1.7.0` is also absent (skipped on PyPI per D1).
- **TestPyPI squatter unchanged.** Bare `docs-cli` on TestPyPI still
  `latest 0.1.0`, `author None` → the `docs-cli-rehearsal` rename detour
  continues (M9/M11/M13/M17/M20 posture). `docs-cli-rehearsal` releases
  `{1.3.0, 1.4.0, 1.5.0, 1.6.0, 1.6.5}` — **1.8.0 slot free**.
- **gh auth.** Logged in to github.com as `ArtRichards`, active account, token
  scopes include `repo` (sufficient for the Phase-5 tag push + release).
- **Tooling.** `twine 6.2.0`, `build 1.5.0`.

## Phase 2 — Pre-publish prep

_Executed 2026-07-03 against `main` (HEAD `d9b4458`)._

**Version + CHANGELOG verification.** `pyproject.toml` `version = "1.8.0"`,
`name = "docs-cli"`; `src/docs_cli/cli.py` `__version__` reads through
`importlib.metadata.version("docs-cli")` (M12 SoT); `tests/test_packaging.py`
A3/B1 pinned at `1.8.0`. `CHANGELOG.md` carries **two** `— UNRELEASED`
sections (`## 1.8.0` for M22+M23, `## 1.7.0` for M21) — the D2 fold (1.7.0 →
1.8.0 + date) is Phase 4's first act, **not done here**.

**Surface parity (help + bundled skill) — GREEN.** `diff -q
src/docs_cli/skill/references/cli.md docs/cli.md` and the `convention.md` pair
both **byte-identical**. Stale "Claude Code skill" wording across the
install-skill surface (cli.py + docs/cli.md + bundled ref): **0** — M23's
"agent skill" neutralisation holds.

**Quality gate (tree-wide) — all GREEN.** `pytest` → **636 passed** (~26s);
`ruff check` clean; `ruff format --check` 43 files formatted; `mypy` no issues
in 44 files; `docs check docs/` exit 0; `docs index --root docs/ --dry-run`
idempotent (date-normalised); `docs/INDEX.md` **byte-identical** to
`tests/fixtures/expected/docs-INDEX.md`.

**Fresh artifact build.** `rm -rf dist/ && python -m build` →
`docs_cli-1.8.0-py3-none-any.whl` + `docs_cli-1.8.0.tar.gz`. **Phase-2 sha256
(chain-of-custody anchors):**

- wheel `docs_cli-1.8.0-py3-none-any.whl`:
  `29ac3ced37843dd422cd10f6d6b1689124ca0f19eac8a2063322cda440374f70`
- sdist `docs_cli-1.8.0.tar.gz`:
  `295ba00926a412d617ff5e0ab17d277cfb3d92da9a436b46b8fb201eb285f9cd`

`twine check dist/*` → both **PASSED**. `CHANGELOG.md` not in the sdist
(`grep -c` → 0; known-expected M13).

**Local-install smoke (no PyPI), `/tmp/docs-local-smoke`, canonical wheel:**

- `docs --version` → `docs 1.8.0`; `docs --help` lists `install-skill`.
- **M23 contracts:** `install-skill --dest /tmp/skill-smoke` exit 0,
  `diff -ru src/docs_cli/skill /tmp/skill-smoke` empty (byte-identical);
  re-run no-op exit 0; `--symlink` exit 2; the resolved dest recorded to
  `${XDG_STATE_HOME}/docs-cli/install-skill.json` as `{"dest":
  "/tmp/skill-smoke"}` (**path only, no content/hash**); a **non-TTY** run with
  **no `--dest`** fell back to the default `~/.claude/skills/docs` and exited 0
  (OQ-1, never blocked); `install-skill --help` reads "agent skill" (1) not
  "Claude Code skill" (0). `docs check tests/fixtures/trees/minimal/` exit 0;
  installed skill refs carry no `](../` links (0).
- **M21 contracts** (against a seeded throwaway cache
  `latest_version = 9.9.9`, so the notice fires offline; pytest stays 100%
  offline in the suite): a normal command emits **both** STDERR lines — `docs:
  update available 1.8.0 -> 9.9.9 — run: pip install -U docs-cli` and the M23
  hint `docs: refresh the agent skill at /tmp/skill-smoke — run: docs
  install-skill --dest /tmp/skill-smoke --force` — while stdout stays clean
  (`docs: no violations found`) and the **exit code is unchanged** (0 with and
  without the notice). `--json` → stdout valid JSON, **0** notice lines.
  Suppression matrix (`--quiet` / `CI` / `DOCS_CLI_NO_UPDATE_CHECK` /
  `DO_NOT_TRACK`) → **0** notice lines each.

**VERDICT (Phase 2): GREEN.** dist/ holds the canonical 1.8.0 candidates
(wheel `29ac3ced…`, sdist `295ba009…`). Proceeding to the TestPyPI rehearsal
(Phase 3).

## Phase 3 — TestPyPI rehearsal

_Executed 2026-07-03 (network egress authorized for the upload/install probes)._

- **Rehearsal build + upload.** Temporarily set `[project] name =
  "docs-cli-rehearsal"` (version unchanged at `1.8.0`); `rm -rf dist/ && python
  -m build` → `docs_cli_rehearsal-1.8.0-{whl,tar.gz}`; `twine check` both
  **PASSED**; `twine upload --repository testpypi dist/*` → live at
  **https://test.pypi.org/project/docs-cli-rehearsal/1.8.0/**.
- **Install from TestPyPI** into `/tmp/docs-test-venv` (`--index-url
  test.pypi.org/simple/ --extra-index-url pypi.org/simple/`) → **succeeded
  first try**.
- **Smoke against the served wheel:**
  - `docs --version` → **`docs 0.0.0+local`** — **known-expected** (M13): the
    rehearsal installs as `docs-cli-rehearsal`, so
    `importlib.metadata.version("docs-cli")` misses → documented
    `0.0.0+local` fallback. Not a failure.
  - **M23 install-skill contracts (version-independent) PASS:** `--dest`
    byte-identical to `src/docs_cli/skill/`; `--symlink` exit 2; recorded dest
    `{"dest": "/tmp/docs-test-skill"}` (path only); `install-skill --help`
    reads "agent skill" (1). `docs check tests/fixtures/trees/minimal/` exit 0.
  - **M21 notice correctly does NOT fire** under the rehearsal name: with a
    seeded cache (`latest_version = 9.9.9`) a normal command emitted **0**
    notice lines, because the current version `0.0.0+local` fails the
    fail-closed numeric compare. This is the exact reason the runbook verifies
    the notice against the canonical **local** wheel (Phase 2, both lines
    present ✓) and the **PyPI** wheel (Phase 4), never the rehearsal wheel.
    `--json` stdout stayed valid JSON with 0 notice lines.
- **Rename reverted + canonical rebuild.** `[project] name` restored to
  `docs-cli`; **`git diff pyproject.toml` empty**; `rm -rf dist/ && python -m
  build` → **canonical sha256:**
  - wheel `docs_cli-1.8.0-py3-none-any.whl`:
    `29ac3ced37843dd422cd10f6d6b1689124ca0f19eac8a2063322cda440374f70` —
    **byte-identical to the Phase-2 wheel** (`src/` unchanged → reproducible).
  - sdist `docs_cli-1.8.0.tar.gz`:
    `cb4944c629356e751f6bbe66cebd89882eb6753c81629fbf830ae5019e8dd4dd` —
    moved from the Phase-2 sdist (`295ba009…`) purely because `docs/` evolved
    (the Phase-1/2 impl-log edits); CHANGELOG is in neither artefact (M13/M20).
    The Phase-4 canonical build (from the committed CHANGELOG-folded tree) will
    re-anchor the sdist sha.
  - `twine check dist/*` → both **PASSED**.

**VERDICT (Phase 3): GO** for the real PyPI publish (Phase 4).

## Phase 4 — Real PyPI publish

_Executed 2026-07-03 (operator authorized the irreversible upload at the D3
gate; network egress for the upload/install/download probes)._

- **CHANGELOG folded + dated (D2).** `## 1.8.0 — UNRELEASED` → `## 1.8.0 —
  2026-07-03`; M21's `## 1.7.0 — UNRELEASED` entries (the update-check `Added`
  item + M22's `Documentation` item) merged up into the 1.8.0 section, the
  `## 1.7.0` header dropped. The 1.8.0 section now reads: M21 update-check +
  the three M23 install-skill items (`Added`) + M22 root-placement guidance
  (`Documentation`). Committed on `main` as **`1a01f74`** — the
  chain-of-custody / `v1.8.0` tag-target commit — and **pushed to `main`**.
- **Fresh canonical rebuild** from `1a01f74`: `rm -rf dist/ && python -m build`
  → **Phase-4 sha256:**
  - wheel `docs_cli-1.8.0-py3-none-any.whl`:
    `29ac3ced37843dd422cd10f6d6b1689124ca0f19eac8a2063322cda440374f70` —
    **byte-identical to the Phase-2/3 wheel** (`src/` unchanged; CHANGELOG is
    in neither wheel nor sdist, so the date edit could not move the wheel sha).
  - sdist `docs_cli-1.8.0.tar.gz`:
    `62a29285bf80326cfdba6154a757ddb33e91e0ad69c31b9a0c3861c50023a17b` —
    re-anchored at the tag-target commit (moved from the Phase-3 `cb4944c6…`
    purely via `docs/` drift between commits — the M13/M20 generalisation; the
    CHANGELOG date edit itself moves neither artefact).
  - `twine check dist/*` → both **PASSED**.
- **Uploaded to PyPI:** `twine upload dist/*` → exit 0, live at
  **https://pypi.org/project/docs-cli/1.8.0/**.
- **Install from PyPI** into `/tmp/docs-real-venv`: `pip install
  docs-cli==1.8.0` resolved **first try** → `docs --version` → **`docs 1.8.0`**
  (canonical name resolves the `importlib.metadata` SoT — confirms the Phase-3
  `0.0.0+local` was purely the rehearsal-name detour).
- **Chain-of-custody — BIT-PERFECT (wheel AND sdist).** `pip download
  --no-deps` (wheel) + `--no-binary :all:` (sdist) pulled both PyPI-served
  artefacts; each sha256 == the local Phase-4 build: served wheel `29ac3ced…`
  == local; served sdist `62a29285…` == local. **Sixth release running**
  (M11 + M13 + M17 + M20 + M24; M20 first extended the check to the sdist).
- **Smoke + all M21 + M23 headline contracts re-run against the PyPI-served
  wheel → all PASS:**
  - `docs --version` → `docs 1.8.0`; `docs --help` lists `install-skill`.
  - **M23:** `install-skill --dest` byte-identical / no-op exit 0 / `--symlink`
    exit 2; recorded dest `{"dest": "/tmp/docs-real-skill"}` (path only);
    `install-skill --help` reads "agent skill" (1) / "Claude Code skill" (0);
    `docs check tests/fixtures/trees/minimal/` exit 0; no `](../` links.
  - **M21** (seeded cache `latest_version = 9.9.9`): normal command emits both
    STDERR lines (`update available 1.8.0 -> 9.9.9`; `refresh the agent skill
    at /tmp/docs-real-skill`), stdout clean, **exit unchanged** (0 vs 0
    feature-off); `--json` stdout valid JSON with 0 notice lines; suppression
    matrix (`--quiet` / `CI` / `DOCS_CLI_NO_UPDATE_CHECK` / `DO_NOT_TRACK`) → 0
    each.

## Phase 5 — Post-release

_Executed 2026-07-03 on `main` as the M24 closeout._

- **Tag + GitHub release.** Annotated **`v1.8.0`** tag at **`1a01f74`** (the
  Phase-4 dated-CHANGELOG commit whose tree matches PyPI) — message `docs-cli
  1.8.0 — update-check notice (M21) + doc-tree root-placement guidance (M22) +
  agent-aware install-skill (M23)` — pushed to `origin`. GitHub release
  `docs-cli 1.8.0` created with notes sourced from the `## 1.8.0` CHANGELOG
  section — live at
  **https://github.com/ArtRichards/docs-cli/releases/tag/v1.8.0**.
- **Host-machine skill refresh (CLAUDE.md policy).** From the PyPI-served venv:
  `docs install-skill --force --dest ~/.claude/skills/docs` → exit 0; `diff -r`
  against the published wheel's bundled skill → **byte-identical**.
  Workflow-skill sweep of `~/.claude/skills/{sync-and-commit,create-milestones,
  project-foundation,ship-milestone}` for the 1.8.0 surface (M21 update-check,
  M23 install-skill agent-awareness) — **NO docs-cli drift found**: none of the
  workflow skills prescribe `install-skill`, and M21/M23 *added* surfaces
  rather than changing a verb these skills call (contrast M20, where the
  `--body-from` help drift was a *changed* surface). The "Claude Code skill"
  strings in the workflow-skill READMEs describe those skills *themselves*, not
  docs-cli's bundled skill — not in scope. (Host-skill edits are host state
  under `~/.claude/skills/`, outside the repo commit.)
- **Doc closeouts landed** on `main`:
  - `m24-pypi-publish-impl.md` (this log): Phase 4 + Phase 5 sections;
    Runbook-Phase table rows 4 + 5 → Complete; milestone-completion summary
    below. Stays `Lifecycle: active`.
  - `m24-pypi-publish.md`: Deliverables + Phase Checklist + Success Criteria
    ticked with evidence; milestone-completion summary appended; archived at
    closeout.
  - `status.md` + `plan.md`: M21 + M22 + M23 + M24 rows finalised; "Current
    milestone" + "Next action" rewritten to the post-publish narrative
    (`docs-cli 1.8.0` shipped; next implementation milestone unscoped).
  - `release-runbook.md`: a `### From M24 (2026-07-03, docs-cli==1.8.0)`
    cumulative-lessons section appended.
  - `docs/INDEX.md` regenerated; `tests/fixtures/expected/docs-INDEX.md`
    regenerated in lockstep.
- **Archival.** Via `docs archive` (never a hand-move), to `archive/2026-07-03/`:
  the M21 pair, the M22 pair, and the M23 pair (each: archive the impl log with
  `--cascade-only "<milestone-doc>"` — `child-of` pulls the milestone doc, both
  land together edge-clean, the M20 pattern); then the M24 milestone doc
  **without** cascade (its `child-of`/`pairs-with` edges must not pull
  plan/status/runbook). Live referrers repointed automatically by the M12 + M18
  edge machinery; `docs check docs/` exit 0 after the sweep. The M24 impl log,
  release-runbook, and `status.md` stay `Lifecycle: active`.
- **Token re-scope** to project-`docs-cli` rolls forward as the M9 follow-on.
  Scratch `/tmp/docs-*` dirs cleaned up.

## Milestone-completion summary

**M24 complete — `docs-cli==1.8.0` shipped to PyPI 2026-07-03**, the batched
publish of the whole post-1.6.5 train — **M21** (update-check notice) + **M22**
(doc-tree root-placement guidance) + **M23** (agent-aware install-skill +
recorded-dest skill-refresh hint) — as one public release (the batched shape:
M17 shipped M14+M15 as 1.6.0; M9 shipped M6+M7+M8 as 1.3.0). Driven under the
D3 "author now, confirm at the gate" decision — the runbook walked
interactively with an explicit operator go-ahead at the Phase-4 gate before the
irreversible PyPI upload + `main` push + tag + release. **1.7.0 was skipped on
PyPI** (its CHANGELOG entries folded into the dated 1.8.0 section, D2).

- **PyPI:** https://pypi.org/project/docs-cli/1.8.0/ ·
  **TestPyPI rehearsal:** https://test.pypi.org/project/docs-cli-rehearsal/1.8.0/ ·
  **GitHub release:** https://github.com/ArtRichards/docs-cli/releases/tag/v1.8.0
- **Published artefact sha256 (chain-of-custody anchors):**
  - wheel `docs_cli-1.8.0-py3-none-any.whl`:
    `29ac3ced37843dd422cd10f6d6b1689124ca0f19eac8a2063322cda440374f70`
  - sdist `docs_cli-1.8.0.tar.gz`:
    `62a29285bf80326cfdba6154a757ddb33e91e0ad69c31b9a0c3861c50023a17b`
- **Chain-of-custody — BIT-PERFECT (wheel AND sdist).** Both PyPI-served sha256s
  byte-identical to the local Phase-4 build. Sixth release running (M11 + M13 +
  M17 + M20 + M24).
- **Quality gate at publish:** 636 passed; ruff / ruff format / mypy clean
  tree-wide; `docs check docs/` exit 0; INDEX idempotent + fixture-locked;
  surface parity (bundled refs byte-identical, "agent skill" wording clean).
- **Smoke + all M21 + M23 headline contracts** verified against the PyPI-served
  wheel (see Phase 4).
- **`v1.8.0`** annotated tag at **`1a01f74`**; GitHub release live with
  `## 1.8.0` notes.
- **Host-machine skills refreshed:** `~/.claude/skills/docs` byte-identical to
  the published bundle; workflow-skill sweep found no docs-cli drift.

### Deviations (carry forward to v1.9+)

1. **TestPyPI rehearsal wheel prints `docs 0.0.0+local` AND the M21 notice
   cannot fire under the rehearsal name** (Phase 3). Known-expected since the
   M12 `importlib.metadata` SoT: the rehearsal installs as
   `docs-cli-rehearsal`, so `version("docs-cli")` misses → `0.0.0+local`
   fallback, which additionally fails the M21 fail-closed version compare (so
   no notice). Not a regression — the real `docs 1.8.0` string and both notice
   lines are proven by the canonical-name local wheel (Phase 2) and the PyPI
   wheel (Phase 4).
2. **`CHANGELOG.md` is in neither the sdist nor the wheel** (M13/M20). The
   Phase-4 CHANGELOG date/fold edit moved neither artefact's sha; the wheel was
   byte-identical to the Phase-2/3 build, and the sdist moved only via `docs/`
   drift across commits. The dated CHANGELOG reaches users via the git repo +
   the GitHub release notes.
3. **Workflow-skill sweep found no drift this release** — the first publish
   since the sweep was added (M20) where it surfaced nothing, because M21/M23
   *added* surfaces rather than *changing* ones the workflow skills prescribe.
   The v1.7+ candidate (an in-repo lint diffing workflow-skill docs-cli
   prescriptions against the bundled `references/` surface) still stands as the
   durable guard; rolls forward.
4. **A pre-existing `## 1.1.0 — UNRELEASED` marker** remains near the bottom of
   `CHANGELOG.md` (M6-era internal versioning, never on PyPI). Out of M24's
   scope; left untouched. Candidate cleanup for a future release.

No `1.8.x` bump was forced — the TestPyPI rehearsal surfaced no packaging
defect (the `0.0.0+local` + no-notice prints are the rename-detour artifacts
above), so `1.8.0` published as-is. Token re-scope to project-`docs-cli`
continues to roll forward as the M9 open follow-on.
