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
| 1. Operator one-time prep | Complete | 2026-07-03 | `~/.pypirc` intact (600; `[pypi]`+`[testpypi]`; both `__token__`; testpypi `…/legacy/`; prefixes `pypi-AgE…`). PyPI `docs-cli` simple-index 200, releases {1.3.0,1.4.0,1.5.0,1.6.0,1.6.5} — **1.8.0 slot free** (1.7.0 absent → skipped). TestPyPI squatter unchanged (`docs-cli` 0.1.0, author None) → rehearsal detour continues; `docs-cli-rehearsal` 1.8.0 slot free. `gh` OK (ArtRichards, `repo` scope). twine 6.2.0, build 1.5.0. |
| 2. Pre-publish prep | Complete | 2026-07-03 | Version SoT `1.8.0` (`__version__` via `importlib.metadata`); packaging pins 1.8.0. Surface parity GREEN: bundled `references/{cli,convention}.md` byte-identical to `docs/`; zero "Claude Code skill" residue. Gate GREEN **636 passed**; ruff/format(43)/mypy(44)/`docs check docs/`/index-dry-run idempotent; INDEX == fixture. Fresh build: wheel `29ac3ced…`, sdist `295ba009…`; both `twine check` PASS; CHANGELOG not in sdist (0). Local-wheel smoke `docs 1.8.0`; M23 contracts (dest record path-only `{"dest":"/tmp/skill-smoke"}`, byte-identical, no-op, `--symlink` exit 2, non-TTY no-dest → default exit 0, "agent skill" wording); M21 contracts (both notice lines to STDERR, exit parity, `--json` stdout-clean, full suppression matrix 0). |
| 3. TestPyPI rehearsal | Complete | 2026-07-03 | Uploaded `docs-cli-rehearsal==1.8.0` (squatter parked → detour kept); both `twine check` PASS. Installed from TestPyPI first try. Smoke: M23 install-skill contracts PASS against served wheel (dest byte-identical, `--symlink` exit 2, recorded dest path-only, "agent skill"); `docs --version` → `docs 0.0.0+local` (known-expected M13 rename caveat); M21 notice **correctly does not fire** under the rehearsal name (`0.0.0+local` fails the fail-closed version compare — verified against the canonical local wheel Phase 2 instead); `--json` stdout clean. Rename reverted (`git diff pyproject.toml` empty); canonical rebuild wheel `29ac3ced…` **byte-identical to Phase 2**, sdist `cb4944c6…` moved via `docs/` drift (Phase-1/2 log edits; CHANGELOG in neither artefact). Both `twine check` PASS. **GO.** |
| 4. Real PyPI publish | **GATE — awaiting operator go** | — | |
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

_GATE — awaiting explicit operator go-ahead (D3). Not started._

Phase-4 sequence when authorized: (1) fold the CHANGELOG `## 1.7.0` entries up
into a dated `## 1.8.0 — 2026-07-03` section, drop the `## 1.7.0` header (D2);
(2) commit on `main` (the chain-of-custody / `v1.8.0` tag-target commit) — this
is the `main` push; (3) fresh canonical rebuild from that commit; (4) `twine
upload dist/*` to **real PyPI** (irreversible, append-only); (5) install from
PyPI, chain-of-custody sha256 (wheel + sdist) vs local, smoke + M21 + M23
contracts against the PyPI-served wheel.
