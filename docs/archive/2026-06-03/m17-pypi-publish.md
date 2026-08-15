# M17 — PyPI publish 1.6.0

Lifecycle: archived
Role: milestone
Project: docs
Updated: 2026-08-14
Archived-reason: Milestone M17 complete; docs-cli==1.6.0 shipped to PyPI 2026-06-03

Related:
- parent-of: m17-pypi-publish-impl.md
- child-of: plan.md
- pairs-with: release-runbook.md
- pairs-with: status.md
- pairs-with: archive/2026-06-03/m14-robustness-agent-native.md
- pairs-with: archive/2026-06-03/m15-agent-native-authoring.md

Revision:
- 2026-08-14: M27 one-time body-link migration; body-link destinations repaired (destination tokens only)

## Overview

> **Stub-drafted 2026-06-03, post M14 + M15 closeout.** M17
> enters active state immediately — M14 and M15 are both
> implementation-complete, each building `docs-cli==1.6.0`
> locally (M14 owns the `pyproject.toml` bump + the
> `## 1.6.0 — UNRELEASED` CHANGELOG section; M15 appended its
> authoring entries to that same section). The operative
> checklist is [release-runbook.md](../../release-runbook.md); this
> milestone doc exists to give the publish work a named home,
> exit criteria, and a log to record what actually happened.

- Milestone: M17 (the v1.6 publish milestone)
- Title: PyPI publish `docs-cli` 1.6.0
- Surface: an operator-driven release of the post-M15 tree to
  PyPI as `docs-cli==1.6.0`, plus the `v1.6.0` git tag, the
  GitHub release with notes sourced from the CHANGELOG, and the
  post-publish doc closeouts that turn the M14 + M15 + M17 rows
  in `status.md` and `plan.md` into the post-publish narrative.
- Status: **Complete (2026-06-03)** — `docs-cli==1.6.0` shipped
  to PyPI, batching M14 + M15. All five runbook phases done;
  chain-of-custody bit-perfect; all seven M14 + M15 headline
  contracts hold against the PyPI-served wheel. `v1.6.0` tag at
  `95f23a6` + GitHub release are the closeout git sequence.

### Goal

The v1.6 implementation train delivered two milestones
locally. **M14 — Robustness + autonomous archive** burned down
the post-1.5.0 multi-agent-review correctness/atomicity findings
(`docs mv` all-or-nothing pre-flight; `docs new` strict-root
refusal; the empty-segment slug reject; the `OSError` →
exit-2 mapping; the `atomic_write` fsync; the four-verb
`touch`/`archive`/`mv`/`project rename` exclude-predicate fix),
landed the non-interactive `docs archive --cascade` agent
affordance (B1), and corrected a packaging guard (C3). **M15 —
Agent-native doc authoring** added the single-doc
`docs project set` (B2), the write-then-stamp `docs stamp` (B3),
and replaced the `docs new --body-from` refusal heuristic with a
real-metadata-block detector (C4). Neither published. Per the
M8/M10/M12 → M9/M11/M13 cadence (build locally + publish in a
separate operator-driven milestone), M17 is the publish — and
it ships **M14 + M15 together** as one public release, just as
M9 batched M6+M7+M8.

M17 is operator-driven by design: re-confirm pre-publish prep,
rebuild fresh artefacts from the post-M15 tree (M14/M15 built
1.6.0 locally, but a fresh rebuild at M17 start is the
discipline — M11 set the precedent and M13 confirmed it),
TestPyPI rehearsal under the disambiguated dist name
`docs-cli-rehearsal==1.6.0` (continuing the M9/M11/M13
TestPyPI-squatter detour), real PyPI publish, tag + GitHub
release, post-release closeouts. No code work; no new verbs; no
TDD code phases. The success criterion is concrete: a fresh
venv on a clean host can `pip install docs-cli==1.6.0`,
`docs --version` prints `docs 1.6.0`, the M14 + M15 headline
contracts hold against the PyPI-served wheel (see Success
Criteria below), `docs check <tree>` exits 0, and the public
GitHub repo carries the matching `v1.6.0` tag + release.

### Requirements

- **Version is `1.6.0`.** Already bumped at M14 Phase 7
  (`pyproject.toml` `version = "1.6.0"`;
  `tests/test_packaging.py` A3 pinned to `1.6.0`;
  `__version__` reads through
  `importlib.metadata.version("docs-cli")` per the M12 SoT
  refactor — so the version comes from `pyproject.toml`'s
  `[project] version` automatically). M17 publishes that
  version verbatim. Mirrors the M9/M11/M13 cadence (one bump
  per implementation milestone; only the implementation
  milestone's version reaches PyPI — here M14 owns the bump and
  M15 builds on the same `1.6.0`).
- **Pre-publish operator state already current** from M13 —
  PyPI + TestPyPI accounts registered, 2FA active, API tokens
  in `~/.pypirc` (mode 600). The M9-era follow-on "token
  re-scope from entire-account to project-`docs-cli`" remains
  operator-side async work; M17 publishes with whatever scope
  the tokens currently carry (consistent with the M11/M13
  posture). If re-scoping landed between M13 and M17, the
  runbook step is a no-op; if not, the publish proceeds with the
  existing tokens and the re-scope follow-on rolls forward.
- **CHANGELOG `## 1.6.0 — UNRELEASED`** is already authored with
  publish-survival wording (M11 lesson — no "ready locally" /
  "deferred to MX" suffixes). M14 opened the section; M15
  appended its `Added`/`Changed`/`Fixed` entries; M18's edge
  fix also folded an entry into the same section. M17's runbook
  step is to drop `UNRELEASED` and replace with the publish date
  — verify the surrounding body still reads accurately at
  publish time.
- **Quality gate green tree-wide** before any upload: pytest
  (510 at M18 implementation-complete — the exact count gets
  recorded into the runbook checklist at the moment of M17 run;
  the M16 trio + M1–M9/M12 archival sweeps and the in-flight
  state of M18 mean the count is whatever the M17-setup tree
  carries), ruff, ruff format, mypy, `docs check docs/`,
  `docs index --root docs/ --dry-run`.
- **Fresh artifact build at M17 start.** M14/M15 built 1.6.0
  locally during their own phases; M17 rebuilds from the
  post-merge-to-main tree (which carries the M14 + M15 stack +
  any M17-only edits — the dated CHANGELOG at Phase 4) so the
  artefact bytes line up with what `git log --oneline main`
  will show at the moment of publish. Never reuse the
  implementation milestones' local `dist/` — and note the
  current repo `dist/` still holds the **stale 1.5.0**
  artefacts, which the `rm -rf dist/` at build start clears.
- **TestPyPI rehearsal is non-optional** (mirrors M9/M11/M13).
  Upload to TestPyPI under `docs-cli-rehearsal==1.6.0` (the bare
  `docs-cli` is parked on TestPyPI per the M9 open follow-on;
  re-check ownership at M17 start in case the squatter project
  lapsed), install from TestPyPI into a fresh
  `/tmp/docs-test-venv`, exercise the smoke set including the
  M14 + M15 headline contracts. **Known-expected (carried from
  M13):** the rehearsal wheel prints `docs 0.0.0+local`, not
  `docs 1.6.0`, because `__version__` reads
  `importlib.metadata.version("docs-cli")` and the rehearsal
  installs the distribution as `docs-cli-rehearsal` — the
  lookup misses and falls back to the documented `0.0.0+local`.
  Verify the version-string contract against the canonical-name
  local wheel (pre-publish smoke) and the PyPI wheel (Phase 4),
  never the rehearsal wheel. If anything else fails, bump to
  `1.6.1` (TestPyPI also rejects re-uploads of the same version)
  and rerun from artifact build.
- **Real PyPI publish.** `twine upload dist/*` to PyPI, install
  from PyPI into a fresh `/tmp/docs-real-venv`, re-run the smoke
  subset against the real artefact; chain-of-custody check via
  `pip download` + `sha256sum` (PyPI-served wheel sha256
  byte-identical to the local Phase 4 build — bit-perfect at
  M11/M13).
- **Post-release sequence.** `git tag -a v1.6.0 && git push
  origin v1.6.0` at the Phase 4 commit, `gh release create
  v1.6.0` with notes sourced from the CHANGELOG `## 1.6.0`
  section, doc closeouts (M14 + M15 + M17 rows in `status.md`
  and `plan.md` finalised; `docs/INDEX.md` +
  `tests/fixtures/expected/docs-INDEX.md` regenerated in
  lockstep). No repo-visibility flip — repo is already public
  from M9. **M14 + M15 milestone-doc archival** is part of the
  closeout — they were deliberately left LIVE at root by M18's
  Phase-9 sweep precisely "awaiting the M17 publish" (now
  resolved — see the Decisions entry "M17 closeout archives
  M14 + M15 + its own milestone doc").

### Deliverables

- [x] PyPI release `docs-cli` 1.6.0 published; project page live
      at `https://pypi.org/project/docs-cli/1.6.0/`.
- [x] TestPyPI release `docs-cli-rehearsal` 1.6.0 published as
      the rehearsal artifact at
      `https://test.pypi.org/project/docs-cli-rehearsal/1.6.0/`
      (continues the M9/M11/M13 disambiguated dist-name detour).
- [x] `pyproject.toml` `version` confirmed at `1.6.0` (landed at
      M14 Phase 7; `__version__` flows through `importlib.metadata`
      per M12 SoT refactor — verified at Phase 2).
- [x] `CHANGELOG.md` `## 1.6.0 — UNRELEASED` section dated to
      `## 1.6.0 — 2026-06-03`; surrounding body re-verified
      accurate (stale lead-in line dropped at Phase 4).
- [x] `v1.6.0` git tag pushed; GitHub release created with notes
      sourced from the CHANGELOG `## 1.6.0` section (the closeout
      git sequence, at commit `95f23a6`).
- [x] `docs/status.md`: M14 + M15 + M17 rows finalised; "Current
      milestone" + "Next action" rewritten post-publish.
- [x] `docs/plan.md`: M14 + M15 + M17 rows finalised; Sequencing
      timeline grew the publish line.
- [x] `docs/m17-pypi-publish.md` (this file): Phase Checklist
      ticked; milestone-completion summary appended; lifecycle
      archived via `docs archive` to `archive/2026-06-03/`.
- [x] `docs/m17-pypi-publish-impl.md`: per-phase log entries +
      final milestone-completion summary; stays `Lifecycle:
      active` after milestone-doc archive (per the
      M8/M9/M10/M11/M13 pattern).
- [x] `docs/m14-robustness-agent-native.md` +
      `docs/m15-agent-native-authoring.md` (and their impl logs)
      archived as part of the M17 closeout to `archive/2026-06-03/`
      — they were left LIVE at root by M18's Phase-9 sweep
      "awaiting the M17 publish" (now resolved — see Decisions).
- [x] `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
      regenerated in lockstep.

## Phase Checklist

M17 has no TDD code phases — it is an operational milestone. The
runbook's sections are the phases (mirrors M9/M11/M13 exactly):

- [x] Operator one-time prep — session-verifiable state captured
      at M17 start (`~/.pypirc` intact mode 600; PyPI `docs-cli`
      at 1.5.0, 1.6.0 slot free; TestPyPI `docs-cli` squatter
      status re-checked — still parked; TestPyPI
      `docs-cli-rehearsal` at 1.5.0, 1.6.0 slot free; twine +
      build tool versions ready).
- [x] Pre-publish prep — versions verified `1.6.0` (M14 Phase 7
      landed `pyproject.toml`; M12 SoT refactor flows
      `__version__` through `importlib.metadata`), CHANGELOG
      header `## 1.6.0 — UNRELEASED`, tree at the M17 setup
      commit, quality gate green tree-wide (510 passed), fresh
      artefacts rebuilt (clearing the stale 1.5.0 `dist/`),
      local-install smoke + all 7 M14 + M15 headline contracts
      verified against the wheel.
- [x] TestPyPI rehearsal — uploaded as `docs-cli-rehearsal==1.6.0`;
      throwaway-venv install from TestPyPI succeeded; full smoke
      including the M14 + M15 headline contracts passed against
      the TestPyPI-served wheel (with the known-expected
      `docs --version` → `0.0.0+local` rehearsal-name caveat).
- [x] Real PyPI publish — `docs-cli==1.6.0` LIVE on PyPI; both
      artefacts twine-check PASS; upload PASS; chain-of-custody
      bit-perfect (PyPI-served wheel sha256 byte-identical to
      local Phase 4 build, `b0822709…`); throwaway-venv install
      from PyPI succeeded (`docs 1.6.0`); full smoke + all 7
      M14 + M15 headline contracts PASS against the PyPI-served
      wheel.
- [x] Post-release — `m17/milestone-setup` ff-merged into `main`
      and pushed; annotated `v1.6.0` tag pushed to `origin`;
      GitHub release live with notes sourced from `## 1.6.0`; doc
      closeouts (plan/status/INDEX + dogfood snapshot + the
      M14 + M15 milestone-doc archival — both plan + impl pairs,
      four docs) landed; `docs archive --cascade` /
      `--cascade-only` ran (M14 + M15 both pairs **and** the M17
      milestone doc archived to `archive/<publish-date>/`; M17
      impl log stays `Lifecycle: active` per the
      M8/M9/M10/M11/M13 pattern; release-runbook + status
      declined; M18 untouched). Token re-scope continues to roll
      forward as the M9 open follow-on.

Each ticks as the runbook's corresponding section completes.

## Decisions

- **Version is 1.6.0.** Already bumped at M14 Phase 7 across
  `pyproject.toml` and `tests/test_packaging.py`; `__version__`
  reads through `importlib.metadata.version("docs-cli")` per the
  M12 SoT refactor — so the version comes from `pyproject.toml`'s
  `[project] version` automatically. M17 publishes that version
  verbatim. Mirrors the M9/M11/M13 cadence (one bump per
  implementation milestone; only the implementation milestone's
  version reaches PyPI).
- **M17 ships M14 + M15 together as one 1.6.0 release.** Both
  built `1.6.0` locally against the same CHANGELOG section; the
  publish batches them, exactly as M9 batched M6+M7+M8 into
  1.3.0. (M11→M10 and M13→M12 were one-to-one; M17→M14+M15 is
  the batched shape again.)
- **Manual `twine`, not Trusted Publishing.** Continues the
  M6 + M9 + M11 + M13 stance. OIDC / GitHub-Actions Trusted
  Publishing remains a future iteration; manual `twine` is
  acceptable at v1.6. Revisit at v2 if the manual flow proves
  cumbersome.
- **TestPyPI rehearsal under disambiguated dist name.**
  Continues the M9/M11/M13 detour while the TestPyPI `docs-cli`
  squatter project is still parked. M17 re-checks ownership at
  the operator-prep step; if the squatter project ever lapses,
  M17 (or a later release) drops the rehearsal-name detour.
- **Fresh artifacts at M17, not the M14/M15 local build.** The
  M14/M15 `dist/` predates any merge-to-main commits and the
  Phase-4 dated CHANGELOG. M17 rebuilds from post-merge-to-main
  HEAD at publish time. (The repo `dist/` currently holds the
  stale 1.5.0 artefacts from M13; `rm -rf dist/` clears them.)
- **Repo visibility flip is N/A.** Repo is already public from
  M9's post-release sequence.
- **No feature work in M17.** No new verbs, no scope additions.
  M17 is a publish-only milestone mirroring M9's/M11's/M13's
  discipline; mixing release-event work with feature work is
  rejected by design.
- **CHANGELOG publish-survival wording already locked.** The
  `## 1.6.0 — UNRELEASED` entry was authored conservatively by
  M14/M15 per the M11 lesson — no "ready locally" / "deferred to
  MX" sentences (the lead-in line "M14 + M15 landed locally; the
  publish milestone (M17) ships 1.6.0 to PyPI" describes state,
  not a deferral, and is dropped/rewritten as part of the Phase-4
  date edit if it would read stale). M17's runbook step is
  mechanical: drop `UNRELEASED`, replace with publish date,
  re-verify body reads accurately. No `gh release edit` amend
  post-publish expected (the M11 deviation should not recur).
- **M13's two deviations carry forward as known-expected at
  M17.** (1) The TestPyPI rehearsal wheel prints `docs
  0.0.0+local` under the rename detour (the `importlib.metadata`
  SoT can't resolve the renamed `docs-cli-rehearsal`
  distribution) — verify the version string against the
  canonical-name local + PyPI wheels, never the rehearsal wheel.
  (2) `CHANGELOG.md` is not shipped inside the sdist (hatchling
  captures `src/`, `docs/`, `tests/`, `README.md`, `LICENSE`,
  `pyproject.toml`). Both are already folded into the runbook's
  Cumulative-lessons + TestPyPI + Artifact-build sections, so
  M17 inherits them automatically; they are recorded here only
  so the Phase-3 `0.0.0+local` print and the Phase-2 ≡ Phase-4
  sdist sha are not mistaken for regressions.
- **Fully-autonomous publish authorized (resolves Q1).** The
  operator explicitly authorized a fully-autonomous M17 run
  including the irreversible real-PyPI `twine upload` of
  `docs-cli==1.6.0`, the `main` push, the `v1.6.0` tag push, and
  the GitHub release — exactly as the M13 operator authorized
  the irreversible PyPI upload + `main` push. M17 therefore does
  **not** stop at the pre-publish-prep / TestPyPI-rehearsal
  boundary; the conductor walks the release-runbook end-to-end
  in one pass. The authorization is recorded here at Step 0; the
  publish itself runs after the milestone-setup commit.
- **M17 closeout archives M14 + M15 + its own milestone doc
  (resolves Q2).** M18's Phase-9 sweep deliberately left M14 and
  M15 (both plan + impl pairs, four docs) LIVE at root "awaiting
  the M17 publish," precisely because archiving a milestone is
  what marks it shipped. The operator confirmed M17's Phase-5
  closeout is where that happens: it archives M14 + M15 (both
  pairs) **and** M17's own milestone doc to
  `archive/<publish-date>/` via `docs archive --cascade` /
  `--cascade-only` (the M12 + M18 edge machinery repoints
  referring `Related:` edges atomically), and flips the M14 +
  M15 `status.md` / `plan.md` rows to Complete with the publish
  date. The M17 impl log, the release-runbook, and `status.md`
  stay `Lifecycle: active` per the established
  M8/M9/M10/M11/M13 pattern. M18 is untouched — it is a separate
  in-flight milestone, not part of the 1.6.0 publish.

## Testing / Quality Gate

The same tree-wide gate the M14/M15 implementations ran, plus
the publish-specific smokes the runbook details:

```sh
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/docs check docs/
.venv/bin/docs index --root docs/ --dry-run
rm -rf dist/ && .venv/bin/python -m build
.venv/bin/twine check dist/*
```

Plus the M17-specific dogfood: walk
[release-runbook.md](../../release-runbook.md) end-to-end against
TestPyPI then real PyPI, with the smoke set covering the M14 +
M15 headline contracts (see Success Criteria).

## Success Criteria

M17 is complete when:

- [x] `pip install docs-cli==1.6.0` works from PyPI on a clean
      host with Python 3.11+ and produces a working `docs`
      command. (Verified: fresh `/tmp/docs-pypi-served-venv`;
      `pip install docs-cli==1.6.0` succeeded; `docs` drives the
      full verb surface.)
- [x] `docs --version` from the PyPI-installed wheel prints
      `docs 1.6.0`. (Verified against the PyPI-served wheel.)
- [x] **M14 contract — `docs mv` is all-or-nothing:** a malformed
      sibling aborts with exit 2, leaving the source in place,
      the destination absent, and every referring `Related:` edge
      + the INDEX untouched (re-verified against the published
      artefact, not just the local build).
- [x] **M14 contract — `docs new` strict-root refusal:** outside
      any `.docs.toml` root (no `--root`) it refuses with exit 2
      and never writes to cwd (re-verified against the
      PyPI-served wheel).
- [x] **M14 contract — non-interactive `docs archive --cascade`:**
      `--cascade` archives the one-hop `pairs-with`/`child-of`
      set with no prompt; `--cascade-dry-run` previews and writes
      nothing (re-verified against the PyPI-served wheel).
- [x] **M14 contract — four-verb exclude-honouring reindex:**
      `docs touch` (and `archive`/`mv`/`project rename`) over a
      tree whose `[exclude]` set holds a malformed file stamps
      the dates *and* refreshes the INDEX cleanly, leaving the
      excluded file unindexed (re-verified against the PyPI-served
      wheel).
- [x] **M15 contract — `docs project set`:** reassigns one doc's
      `Project:` atomically; `--new-project` guards typos (a
      value new to the tree refuses with exit 2 + did-you-mean);
      archived docs untouched (re-verified against the PyPI-served
      wheel).
- [x] **M15 contract — single-file `docs stamp`:** stamps a valid
      metadata block onto a raw file an agent already wrote
      (title from H1, role/project from flags or `.docs.toml`,
      `Lifecycle: draft`); re-stamping is a no-op bar `Updated:`
      (re-verified against the PyPI-served wheel).
- [x] **M15 contract — `--body-from` real-frontmatter detector:**
      `docs new --body-from` accepts a body whose prose contains
      `Reason:`/`Plan:` lines yet still refuses a whole
      doc-with-frontmatter body (a `---` fence or a ≥2
      `{Lifecycle, Role, Updated}` adjacent cluster) (re-verified
      against the PyPI-served wheel).
- [x] `docs install-skill` from the PyPI-installed wheel places a
      host-correct skill that drives the verbs identically to the
      in-repo install; bundled references carry no repo-relative
      `../` links. (Verified against the PyPI-served wheel:
      byte-identical to `src/docs_cli/skill`, re-run no-op exit 0,
      `--symlink` exit 2, no `](../` links.)
- [x] The `v1.6.0` tag and GitHub release exist at
      `https://github.com/ArtRichards/docs-cli/releases/tag/v1.6.0`.
      (The annotated `v1.6.0` tag at `95f23a6` + the GitHub
      release are the closeout git sequence the conductor runs
      immediately after the M17 closeout commit.)
- [x] All Phase Checklist items above are ticked.
- [x] `docs/status.md` reflects M14 + M15 + M17 as Complete with
      the actual publish date.
- [x] `docs/m17-pypi-publish-impl.md` carries a
      milestone-completion summary with the published version
      (`1.6.0` — assuming no TestPyPI-surfaced regression forces a
      `1.6.x` bump), wheel + sdist sha256, publish timestamp, and
      any deviations from the runbook recorded for v1.7+
      reference.

## Milestone-completion summary

**M17 complete — `docs-cli==1.6.0` shipped to PyPI 2026-06-03**,
batching **M14 + M15** into one public release (as M9 batched
M6+M7+M8). Driven end-to-end as a fully-autonomous run walking
[release-runbook.md](../../release-runbook.md) directly (no TDD code
phases). The full per-phase record + deviation prose lives in
[m17-pypi-publish-impl.md](../../m17-pypi-publish-impl.md)'s
milestone-completion summary.

- **PyPI:** https://pypi.org/project/docs-cli/1.6.0/ ·
  **TestPyPI rehearsal:**
  https://test.pypi.org/project/docs-cli-rehearsal/1.6.0/
- **Published artefact sha256:**
  - wheel `docs_cli-1.6.0-py3-none-any.whl`:
    `b0822709ec297223efeba9945a44f624b6f9d3edefaaff02a42abc31b499d45c`
  - sdist `docs_cli-1.6.0.tar.gz`:
    `04175cda15694fbc90a263da31cac752b1f58aee377dd029eecf3a3b5e1f6d88`
- **Chain-of-custody:** PyPI-served wheel sha256 byte-identical
  to the local Phase-4 build — **bit-perfect** (matches M11/M13).
- **Quality gate at publish:** 510 passed; ruff / ruff format /
  mypy clean tree-wide; `docs check docs/` exit 0;
  `docs index --root docs/ --dry-run` idempotent.
- **Smoke + all seven M14 + M15 headline contracts** verified
  against the PyPI-served wheel: `docs --version` → `docs 1.6.0`;
  `install-skill` byte-identical / no-op / `--symlink` exit 2;
  M14 `mv` all-or-nothing; M14 `new` strict-root refusal; M14
  non-interactive `archive --cascade` (+ `--cascade-dry-run`
  writes nothing); M14 four-verb exclude-honouring reindex; M15
  `project set` (atomic + typo guard + did-you-mean +
  archived-untouched); M15 single-file `stamp` (title-from-H1,
  draft, re-stamp no-op bar `Updated:`); M15 `--body-from`
  real-frontmatter detector.
- **`v1.6.0`** annotated tag at `95f23a6` (the Phase-4
  dated-CHANGELOG commit whose tree matches PyPI); GitHub release
  live with notes sourced from the `## 1.6.0` CHANGELOG section.

### Deviations (recorded for v1.7+)

1. **TestPyPI rehearsal wheel prints `docs 0.0.0+local`, not
   `docs 1.6.0`** — known-expected since the M12 `importlib.metadata`
   SoT refactor (the rehearsal installs as `docs-cli-rehearsal`,
   so the lookup misses and falls back). Not a regression — the
   real version string is proven by the canonical-name local
   wheel (Phase 2) and the PyPI wheel (Phase 4).
2. **`CHANGELOG.md` is not in the sdist** — known-expected since
   M13. At M17 the **wheel** sha was byte-identical across
   Phase 2 ≡ Phase 4 (`src/` unchanged → reproducible), while the
   **sdist** sha moved (`da1a60b8…` → `04175cda…`) ONLY because
   `docs/` evolved between the two builds (the impl-log
   Phase-2/3 commit) — not because of the Phase-4 CHANGELOG date
   edit. Recorded so the moved sdist sha is not mistaken for a
   regression.

No `1.6.x` bump was forced. Token re-scope to project-`docs-cli`
continues to roll forward as the M9 open follow-on.

## OPEN QUESTIONS

None (Q1, Q2 resolved by the operator at Step 0 — see Decisions).

- **Q1 — Publish-execution authorization & mode → resolved
  FULL AUTONOMOUS.** The operator explicitly authorized a
  fully-autonomous run including the irreversible real-PyPI
  upload of `docs-cli==1.6.0`, the `main` push, the `v1.6.0` tag
  push, and the GitHub release — mirroring the M13 operator's
  authorization. M17 does not stop at the TestPyPI-rehearsal
  boundary. Folded into Decisions ("Fully-autonomous publish
  authorized").
- **Q2 — M14 + M15 milestone-doc archival at the M17 closeout →
  resolved ARCHIVE AT M17 CLOSEOUT.** M17's Phase-5 closeout
  archives M14 + M15 (both plan + impl pairs, four docs) **plus**
  M17's own milestone doc to `archive/<publish-date>/` via
  `docs archive --cascade` / `--cascade-only`, flipping the
  M14 + M15 `status.md` / `plan.md` rows to Complete with the
  publish date. The M17 impl log, release-runbook, and
  `status.md` stay `Lifecycle: active`; M18 is untouched. Folded
  into Decisions ("M17 closeout archives M14 + M15 + its own
  milestone doc").
