# M17 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-06-03

Related:
- child-of: archive/2026-06-03/m17-pypi-publish.md
- pairs-with: archive/2026-06-03/m17-pypi-publish.md
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
- Progress: **Complete 2026-06-03** — `docs-cli==1.6.0` shipped to
  PyPI, batching M14 + M15 into one public release (as M9 shipped
  M6+M7+M8). All five runbook phases done in one fully-autonomous
  pass (the conductor drove the release-runbook directly, since an
  operational publish milestone has no 10-phase TDD cycle). The
  operator authorized the irreversible real-PyPI upload + `main`
  push + `v1.6.0` tag + GitHub release up front (Step 0 resolution
  of OPEN QUESTION Q1 — see the milestone doc's Decisions).
  Chain-of-custody bit-perfect (PyPI-served wheel sha256
  byte-identical to the local Phase 4 build); all seven M14 + M15
  headline contracts hold against the PyPI-served wheel.

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
| 4. Real PyPI publish | Complete | 2026-06-03 | CHANGELOG dated `## 1.6.0 — 2026-06-03` + committed (`95f23a6`, the chain-of-custody / tag-target commit); canonical rebuild; both `twine check` PASS; uploaded to PyPI; **chain-of-custody bit-perfect** (PyPI-served wheel sha256 == local Phase-4 wheel `b0822709…`); install from PyPI → `docs 1.6.0`; smoke + all 7 M14+M15 contracts PASS against the PyPI-served wheel. Published sha256 below. |
| 5. Post-release | Complete | 2026-06-03 | `m17/milestone-setup` ff-merged to `main` + pushed; annotated `v1.6.0` tag at `95f23a6` pushed to origin; GitHub release `v1.6.0` live with notes sourced from `## 1.6.0`; doc closeouts landed (status/plan/INDEX + dogfood snapshot + the M14 + M15 milestone-doc archival — both plan + impl pairs); `docs archive --cascade` ran (M14 + M15 both pairs **and** the M17 milestone doc → `archive/2026-06-03/`; M17 impl log stays `Lifecycle: active` per M8/M9/M10/M11/M13; release-runbook + status declined; M18 untouched). Token re-scope rolls forward as the M9 open follow-on. |

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

_Executed 2026-06-03 (network egress authorized; sandbox off for the
upload/install/download probes)._

- **CHANGELOG dated.** `## 1.6.0 — UNRELEASED` → `## 1.6.0 — 2026-06-03`;
  the stale lead-in line ("M14 + M15 landed locally; the publish milestone
  (M17) ships 1.6.0 to PyPI") dropped/rewritten per the anticipated Phase-4
  edit (milestone-doc Decision "CHANGELOG publish-survival wording already
  locked"). Committed on `m17/milestone-setup` as **`95f23a6`** — the
  chain-of-custody / tag-target commit whose tree state matches what's in
  PyPI.
- **Fresh canonical rebuild** (`[project] name = "docs-cli"`):
  `rm -rf dist/ && python -m build` produced
  `docs_cli-1.6.0-py3-none-any.whl` + `docs_cli-1.6.0.tar.gz`;
  `twine check dist/*` → both **PASSED**. **Phase-4 sha256:**
  - wheel:
    `b0822709ec297223efeba9945a44f624b6f9d3edefaaff02a42abc31b499d45c`
    — **byte-identical to the Phase-2 wheel** (`src/` unchanged →
    reproducible build).
  - sdist:
    `04175cda15694fbc90a263da31cac752b1f58aee377dd029eecf3a3b5e1f6d88`
    — **differs from the Phase-2 sdist** (`da1a60b8…`) ONLY because `docs/`
    evolved between the builds (the impl-log Phase-2/3 commit); `CHANGELOG.md`
    is not in the sdist, so the Phase-4 date edit did not move the sha. This
    is expected, not a regression (M13 deviation #2, generalised:
    cross-commit `docs/` drift moves the sdist sha while the wheel stays
    bit-stable).
- **Uploaded to PyPI:** `twine upload dist/*` → exit 0, visible at
  **https://pypi.org/project/docs-cli/1.6.0/**.
- **Install from PyPI** into a fresh `/tmp/docs-real-venv`:
  `pip install docs-cli==1.6.0` → `docs --version` → **`docs 1.6.0`**
  (canonical name resolves the `importlib.metadata` SoT correctly —
  confirms the Phase-3 `0.0.0+local` was purely the rehearsal-name detour).
- **Chain-of-custody — BIT-PERFECT.** `pip download --no-deps` pulled the
  PyPI-served wheel; `sha256sum` == the local Phase-4 wheel
  (`b0822709…`) — byte-identical (fourth release running: M11 + M13 + M17
  confirmed).
- **Smoke + all seven M14 + M15 headline contracts re-run against the
  PyPI-served wheel → all PASS:**
  - `docs --version` → `docs 1.6.0`; `docs --help` lists the full
    `index/new/archive/mv/touch/stamp/project/check/list/migrate/install-skill`
    surface (incl. `stamp` + `project set`).
  - `install-skill` byte-identical (`diff` empty) / re-run no-op exit 0 /
    `--symlink` exit 2; `docs check tests/fixtures/trees/minimal/` exit 0;
    installed skill references carry no repo-relative `](../` links.
  - 1. **M14 `mv` all-or-nothing** — malformed sibling → exit 2; source
       stays, dest absent, referring `Related:` edge + INDEX untouched.
    2. **M14 `new` strict-root refusal** — outside any root, no `--root` →
       exit 2; nothing written to cwd.
    3. **M14 non-interactive `archive --cascade`** — `--cascade` (stdin
       closed) archives primary + its one-hop `pairs-with`/`child-of` set,
       no prompt, exit 0; `--cascade-dry-run` writes nothing (exit 0);
       post-cascade `docs check` exit 0.
    4. **M14 four-verb exclude-honouring reindex** — `touch` (and
       `archive`/`mv`/`project rename`) over a tree whose `[exclude] globs`
       set holds a malformed file stamps the date AND refreshes the INDEX
       cleanly (exit 0); the excluded file stays unindexed.
    5. **M15 `project set`** — typo (`beto`) → exit 2 + `did you mean
       'beta'?` + `--new-project` recovery hint, no write; `--new-project`
       accepts a genuinely new value; reassigning to an existing value is
       atomic (exit 0); archived doc byte-identical.
    6. **M15 single-file `stamp`** — raw file → metadata block (title from
       H1, `Lifecycle: draft`, role from flag, project from `.docs.toml`),
       body verbatim; re-stamp no-op bar `Updated:`; exactly one metadata
       block.
    7. **M15 `--body-from` real-frontmatter detector** — prose body with
       `Reason:`/`Plan:` lines accepted (exit 0); `---`-fenced body refused
       (exit 2); ≥2-adjacent `{Lifecycle, Role, Updated}` cluster body
       refused (exit 2); refused docs not created.

## Phase 5 — Post-release

_Executed 2026-06-03 on `m17/milestone-setup` as the M17 closeout._

- **Re-verification gate first.** Before any doc edit, the published
  artefact was re-verified against the PyPI-served wheel: fresh
  `/tmp/docs-pypi-served-venv`, `pip install docs-cli==1.6.0`,
  `docs --version` → `docs 1.6.0`, full smoke + all seven M14 + M15
  contracts PASS (the "re-verified against the PyPI-served wheel" Success
  Criterion). Chain-of-custody re-confirmed bit-perfect.
- **Repo-visibility flip:** N/A (public since M9).
- **Doc closeouts landed** on `m17/milestone-setup`:
  - `m17-pypi-publish-impl.md` (this log): Phase 4 + Phase 5 sections;
    Runbook-Phase table rows 4 + 5 → Complete; flipped to `Lifecycle:
    active`; milestone-completion summary below.
  - `m17-pypi-publish.md`: every `[ ]` in Phase Checklist, Deliverables,
    and Success Criteria ticked with evidence; milestone-completion summary
    appended; front-matter flipped to the completed-milestone lifecycle for
    the archive step.
  - `status.md`: M14 + M15 + M17 rows → Complete (2026-06-03); "Current
    milestone" + "Next action" rewritten to the post-publish narrative
    (docs-cli 1.6.0 shipped; M18 remains the in-flight implementation
    milestone). M18 representation kept intact.
  - `plan.md`: M14 + M15 + M17 rows finalised; the v1.6 Sequencing line
    grew the 1.6.0 publish.
- **`docs/INDEX.md` regenerated** (`docs index --root docs/`);
  `tests/fixtures/expected/docs-INDEX.md` regenerated in lockstep; full
  pytest re-run GREEN.
- **Archival (the Q2 decision).** Via `.venv/bin/docs archive` (never a
  hand-move), to `archive/2026-06-03/`:
  - M17 milestone doc `m17-pypi-publish.md` archived **without** cascade
    (its `pairs-with` edges to M14/M15/runbook/status must not pull
    anything; `parent-of` to this impl log is not a cascade verb). This
    repointed **this impl log's** `child-of`/`pairs-with` edges to the
    `archive/2026-06-03/m17-pypi-publish.md` path automatically (the M12 +
    M18 edge machinery), while the impl log stays `Lifecycle: active`.
  - M14 pair: archived the M14 impl log with
    `--cascade-only "m14-robustness-agent-native.md"` — `child-of` pulls
    the milestone doc, so both land together edge-clean (the M18 Phase-9
    log-with-cascade-only-plan pattern).
  - M15 pair: archived the M15 impl log with
    `--cascade-only "m15-agent-native-authoring.md"` — same shape.
  - Live referrers (`plan.md`, `status.md`) repointed automatically to the
    new `archive/2026-06-03/` paths. `docs check docs/` exit 0 after every
    op and at the end (no broken refs). The M17 impl log, the
    release-runbook, and `status.md` stay `Lifecycle: active` per the
    M8/M9/M10/M11/M13 pattern. **M18 untouched.**
- **The closeout git sequence** (executed by the conductor immediately
  after this commit, mirroring how M13's impl log narrated its Phase 5):
  `m17/milestone-setup` ff-merged into `main` and pushed; annotated
  `v1.6.0` tag at **`95f23a6`** (the Phase-4 dated-CHANGELOG commit whose
  tree matches PyPI) pushed to `origin`; GitHub release `v1.6.0` created
  with notes sourced from the `## 1.6.0` CHANGELOG section. No
  `gh release edit` amend expected (the M11 deviation did not recur — the
  CHANGELOG was authored with publish-survival wording).
- **Token re-scope** to project-`docs-cli` rolls forward as the M9 open
  follow-on (async operator UI work; not a blocker).
- Scratch `/tmp/docs-*` dirs cleaned up.

## Milestone-completion summary

**M17 complete — `docs-cli==1.6.0` shipped to PyPI 2026-06-03**, batching
**M14 + M15** into one public release (as M9 batched M6+M7+M8; M11→M10 and
M13→M12 were one-to-one). Driven end-to-end as a fully-autonomous run
walking [release-runbook.md](release-runbook.md) directly (M17 has no TDD
code phases; the runbook sections are the phases); the operator authorized
the irreversible PyPI upload + `main` push + tag + release up front.

- **PyPI:** https://pypi.org/project/docs-cli/1.6.0/ ·
  **TestPyPI rehearsal:**
  https://test.pypi.org/project/docs-cli-rehearsal/1.6.0/
- **Published artefact sha256 (chain-of-custody anchors):**
  - wheel `docs_cli-1.6.0-py3-none-any.whl`:
    `b0822709ec297223efeba9945a44f624b6f9d3edefaaff02a42abc31b499d45c`
  - sdist `docs_cli-1.6.0.tar.gz`:
    `04175cda15694fbc90a263da31cac752b1f58aee377dd029eecf3a3b5e1f6d88`
- **Chain-of-custody — BIT-PERFECT.** The PyPI-served wheel sha256 is
  byte-identical to the local Phase-4 build (`b0822709…`); re-confirmed at
  Phase 5 by re-downloading from PyPI. Fourth release running (M11 + M13 +
  M17).
- **Quality gate at publish:** 510 passed; ruff / ruff format / mypy clean
  tree-wide; `docs check docs/` exit 0; `docs index --root docs/ --dry-run`
  idempotent.
- **Smoke + all seven M14 + M15 headline contracts** verified against the
  PyPI-served wheel: `docs --version` → `docs 1.6.0`;
  `install-skill` byte-identical / no-op / `--symlink` exit 2;
  `docs check tests/fixtures/trees/minimal/` exit 0; installed skill refs
  carry no `../` links; and the seven contracts (M14 `mv` all-or-nothing;
  M14 `new` strict-root refusal; M14 non-interactive `archive --cascade` +
  `--cascade-dry-run` writes-nothing; M14 four-verb exclude-honouring
  reindex; M15 `project set` atomic + typo guard + did-you-mean +
  archived-untouched; M15 single-file `stamp`; M15 `--body-from`
  real-frontmatter detector).
- **`v1.6.0`** annotated tag at **`95f23a6`** (the Phase-4 dated-CHANGELOG
  commit whose tree matches PyPI); GitHub release live with notes sourced
  from the `## 1.6.0` CHANGELOG section.

### Deviations (carry forward to v1.7+)

1. **TestPyPI rehearsal wheel prints `docs 0.0.0+local`, not
   `docs 1.6.0`** (Phase 3). Known-expected since the M12 `importlib.metadata`
   version-SoT refactor: the rehearsal renames the distribution to
   `docs-cli-rehearsal`, so `importlib.metadata.version("docs-cli")` raises
   `PackageNotFoundError` and falls back to the documented `0.0.0+local`.
   **Not a regression** — the real `docs 1.6.0` string is proven by the
   canonical-name local wheel (Phase 2) and the PyPI wheel (Phase 4). The
   runbook's TestPyPI version probe already carries this caveat (folded in
   at M13).
2. **`CHANGELOG.md` is not shipped inside the sdist.** Known-expected since
   M13: the hatchling sdist captures `src/`, `docs/`, `tests/`,
   `README.md`, `LICENSE`, `pyproject.toml` — `tar tzf … | grep -c
   CHANGELOG` → 0. Consequence at M17: the **wheel** sha was byte-identical
   across Phase 2 ≡ Phase 4 (`src/` unchanged → reproducible), while the
   **sdist** sha *moved* (`da1a60b8…` → `04175cda…`) — but ONLY because
   `docs/` evolved between the two builds (the impl-log Phase-2/3 commit),
   not because of the Phase-4 CHANGELOG date edit (the CHANGELOG isn't in
   the sdist). Recorded so the moved sdist sha is not mistaken for a
   regression. The dated CHANGELOG reaches users via the git repo + the
   GitHub release notes.

No `1.6.x` bump was forced — the TestPyPI rehearsal surfaced no packaging
defect (the `0.0.0+local` print is the rename-detour artifact above, not a
regression), so `1.6.0` published as-is. The runbook's internal hard gates
(twine check, clean rehearsal, bit-perfect chain-of-custody) all passed.
Token re-scope to project-`docs-cli` continues to roll forward as the M9
open follow-on (async operator UI work; not a release blocker).

### Open follow-on (v1.7) — stale `docs new --body-from` help string

The post-publish dogfood found one **cosmetic help-text drift** that shipped
in 1.6.0: the `docs new --body-from` argparse help string at
`src/docs_cli/cli.py:2900-2905` still describes the **pre-M15-C4** detector —
"Refused (exit 2) if any of the body's first 20 lines looks like a metadata
block". M15-C4 replaced that "first 20 lines" heuristic; the actual detector
`_body_has_metadata_block` (`cli.py:3370`) and the runtime refusal message
(`cli.py:3500-3509`) are **correct** — they refuse only on a real metadata
block (a leading `---` fence, or ≥2 of `{Lifecycle, Role, Updated}` on
adjacent lines) and now *accept* lone prose like a `Plan:`/`Reason:` line.
Only the argparse help text drifted; the prose docs (`docs/cli.md`) and the
bundled `references/cli.md` were verified to **not** carry the "first 20
lines" wording, so the fix is **doc-only and one line** in `cli.py`. Not
fixing now (1.6.0 already shipped). Proposed corrected wording for the v1.7
fix (turnkey):

> Read body content from PATH (or `-` for stdin) and append it under the
> scaffold's frontmatter. Refused (exit 2) only if the body itself contains
> a metadata block — a leading `---` fence or ≥2 adjacent
> `{Lifecycle, Role, Updated}` lines (lone prose like a `Plan:` line is
> fine). Pass body content only; `docs new` owns the frontmatter.

This miss motivated the new **surface-parity gate** (CLI `--help` + bundled
skill) added to [plan.md](plan.md) and
[release-runbook.md](release-runbook.md) — see the M17 entry in the runbook's
Cumulative lessons + deviations.
