# M13 — PyPI publish 1.5.0

Lifecycle: archived
Role: milestone
Project: docs
Updated: 2026-08-14
Archived-reason: Milestone M13 complete; docs-cli==1.5.0 shipped to PyPI 2026-05-29

Related:
- parent-of: archive/2026-05-29/m13-pypi-publish-impl.md
- child-of: plan.md
- pairs-with: release-runbook.md
- pairs-with: status.md
- pairs-with: archive/2026-05-28/m12-project-rename.md

Revision:
- 2026-08-14: M27 one-time body-link migration; body-link destinations repaired (destination tokens only)

## Overview

> **Stub-drafted 2026-05-29, post M12 closeout.** M13 enters
> active state immediately — the M12 wheel + sdist already live
> in local `dist/` and pass `twine check`. The operative
> checklist is [release-runbook.md](../../release-runbook.md); this
> milestone doc exists to give the publish work a named home,
> exit criteria, and a log to record what actually happened.

- Milestone: M13 (the v1.5 publish milestone)
- Title: PyPI publish `docs-cli` 1.5.0
- Surface: an operator-driven release of the post-M12 tree to PyPI
  as `docs-cli==1.5.0`, plus the `v1.5.0` git tag, the GitHub
  release with artefacts attached, and the post-publish doc
  closeouts that turn the M12 + M13 rows in `status.md` and
  `plan.md` into the post-publish narrative.
- Status: Active (Phase 1 opens immediately — M12 already built
  fresh 1.5.0 artefacts during its Phase 8 + Phase 10)

### Goal

M12 delivered the operator-facing `docs project rename` verb
(deferred from M10), two M11-surfaced wart fixes (`docs touch`
outside-root refusal; `docs archive` referring-edge rewrite),
and a packaging refactor (`__version__` sourced from
`importlib.metadata`). It did **not** publish. Per the
M7/M8/M10/M12 cadence (build locally + publish in a separate
milestone), M13 is the publish.

M13 is operator-driven by design: re-confirm pre-publish prep,
rebuild fresh artefacts from the post-M12 tree (the M12 Phase 8
+ Phase 10 `dist/` exists and passes `twine check`, but a fresh
rebuild at M13 start is the discipline — M11 set the precedent),
TestPyPI rehearsal under the disambiguated dist name
`docs-cli-rehearsal==1.5.0` (continuing M9/M11's TestPyPI-squatter
detour), real PyPI publish, tag + GitHub release, post-release
closeouts. No code work; no new verbs; no TDD code phases. The
success criterion is concrete: a fresh venv on a clean host can
`pip install docs-cli==1.5.0`, `docs --version` prints
`docs 1.5.0`, the four M12 headline contracts hold against the
PyPI-served wheel (`docs project rename` against a copied
fixture tree round-trips byte-identical; `docs touch` outside
any `.docs.toml`-rooted tree refuses with exit 2; `docs archive`
referring-edge rewrite is atomic; `docs --version` flows through
`importlib.metadata`), `docs check <tree>` exits 0, and the
public GitHub repo carries the matching `v1.5.0` tag + release.

### Requirements

- **Version is `1.5.0`.** Already bumped at M12 Phase 7
  (`pyproject.toml` + `tests/test_packaging.py` pinned to 1.5.0;
  `__version__` flows through `importlib.metadata.version("docs-cli")`
  per the M12 SoT refactor — so the version comes from
  `pyproject.toml`'s `[project] version` automatically). M13
  publishes that version verbatim.
- **Pre-publish operator state already current** from M11 —
  PyPI + TestPyPI accounts registered, 2FA active, API tokens
  in `~/.pypirc`. The M9-era follow-on "token re-scope from
  entire-account to project-`docs-cli`" remains operator-side
  async work; M13 publishes with whatever scope the tokens
  currently carry (consistent with M11's posture). If
  re-scoping landed between M11 and M13, the runbook step is a
  no-op; if not, the publish proceeds with the existing
  tokens and the re-scope follow-on rolls forward.
- **CHANGELOG `## 1.5.0 — UNRELEASED`** is already authored
  with publish-survival wording (M11 lesson — no "ready locally"
  / "deferred to MX" suffixes). M13's runbook step is to drop
  `UNRELEASED` and replace with the publish date — verify the
  surrounding body still reads accurately at publish time
  (the M11 lesson about CHANGELOG amend at Phase 5 is the
  reason this entry was authored conservatively).
- **Quality gate green tree-wide** before any upload: pytest
  (433 at M12 closeout — exact count gets recorded into the
  runbook checklist at the moment of M13 run), ruff, ruff
  format, mypy, `docs check docs/`, `docs index --root docs/
  --dry-run`.
- **Fresh artifact build at M13 start.** The 2026-05-28 M12
  Phase 8 wheel + sdist sitting in local `dist/` is the M12
  closeout-commit build; M13 rebuilds from the post-merge-to-main
  tree (which carries the M12 stack + any M13-only edits — none
  expected, but enforce the discipline per the M11 precedent)
  so the artefact-bytes line up with what `git log --oneline main`
  will show at the moment of publish.
- **TestPyPI rehearsal is non-optional** (mirrors M9/M11).
  Upload to TestPyPI under `docs-cli-rehearsal==1.5.0` (the
  bare `docs-cli` is parked on TestPyPI per the M9 open
  follow-on; re-check ownership at M13 start in case the
  squatter project lapsed), install from TestPyPI into a fresh
  `/tmp/docs-test-venv`, exercise the smoke set including the
  four M12 headline contracts. If anything fails, bump to
  `1.5.1` (TestPyPI also rejects re-uploads of the same
  version) and rerun from artifact build.
- **Real PyPI publish.** `twine upload dist/*` to PyPI,
  install from PyPI into a fresh `/tmp/docs-real-venv`,
  re-run the smoke subset against the real artefact.
- **Post-release sequence.** `git tag v1.5.0 && git push
  origin v1.5.0`, `gh release create v1.5.0` with notes
  sourced from the CHANGELOG `## 1.5.0` section, doc closeouts
  (M12 + M13 rows in `status.md` and `plan.md` finalised;
  `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
  regenerated in lockstep). No repo-visibility flip — repo is
  already public from M9.

### Deliverables

- [x] PyPI release `docs-cli` 1.5.0 published; project page
      live at `https://pypi.org/project/docs-cli/1.5.0/`.
- [x] TestPyPI release `docs-cli-rehearsal` 1.5.0 published as
      the rehearsal artifact at
      `https://test.pypi.org/project/docs-cli-rehearsal/1.5.0/`
      (continues the M9/M11 disambiguated dist-name detour).
- [x] `pyproject.toml` `version` confirmed at `1.5.0` (already
      landed at M12 Phase 7; `__version__` flows through
      `importlib.metadata` per M12 SoT refactor).
- [x] `CHANGELOG.md` `## 1.5.0 — UNRELEASED` section dated to
      publish day; surrounding body re-verified accurate.
- [x] `v1.5.0` git tag pushed; GitHub release created with
      notes sourced from the CHANGELOG `## 1.5.0` section.
- [x] `docs/status.md`: M12 + M13 rows finalised; "Current
      milestone" + "Next action" rewritten post-publish.
- [x] `docs/plan.md`: M12 + M13 rows finalised.
- [x] `docs/m13-pypi-publish.md` (this file): Phase Checklist
      ticked; milestone-completion summary appended; lifecycle
      archived via `docs archive --cascade`.
- [x] `docs/m13-pypi-publish-impl.md`: per-phase log entries +
      final milestone-completion summary; stays `Lifecycle:
      active` after milestone-doc archive (per the
      M8/M9/M10/M11 pattern).
- [x] `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
      regenerated in lockstep.

## Phase Checklist

M13 has no TDD code phases — it is an operational milestone.
The runbook's sections are the phases (mirrors M9/M11 exactly):

- [x] Operator one-time prep — session-verifiable state
      captured at M13 start (`~/.pypirc` intact mode 600; PyPI
      `docs-cli` at 1.4.0, 1.5.0 slot free; TestPyPI
      `docs-cli` squatter status re-checked; TestPyPI
      `docs-cli-rehearsal` at 1.4.0, 1.5.0 slot free; twine +
      build tool versions ready).
- [x] Pre-publish prep — versions verified `1.5.0` (M12
      Phase 7 landed `pyproject.toml`; M12 SoT refactor flows
      `__version__` through `importlib.metadata`), CHANGELOG
      header `## 1.5.0 — UNRELEASED`, tree at the M13 setup
      commit, quality gate green tree-wide, fresh artefacts
      rebuilt, local-install smoke + M12 headline contracts
      verified against the wheel.
- [x] TestPyPI rehearsal — uploaded as
      `docs-cli-rehearsal==1.5.0`; throwaway-venv install from
      TestPyPI succeeded; full smoke including the four M12
      headline contracts (project rename round-trip; touch
      outside-root refusal; archive referring-edge rewrite;
      version SoT via `importlib.metadata`) passed against
      TestPyPI-served wheel.
- [x] Real PyPI publish — `docs-cli==1.5.0` LIVE on PyPI;
      both artefacts twine-check PASS; upload PASS;
      chain-of-custody bit-perfect (PyPI-served wheel sha256
      byte-identical to local Phase 4 build); throwaway-venv
      install from PyPI succeeded; full smoke + M12 headline
      contracts PASS against PyPI-served wheel.
- [x] Post-release — `m13/milestone-setup` ff-merged into
      `main` and pushed; annotated `v1.5.0` tag pushed to
      `origin`; GitHub release live with notes sourced from
      `## 1.5.0`; doc closeouts (plan/status/INDEX + dogfood
      snapshot) landed; `docs archive --cascade` ran
      (milestone doc archived, impl log stays `Lifecycle:
      active` per M8/M9/M10/M11 pattern, release-runbook +
      status declined). Token re-scope continues to roll
      forward as M9 open follow-on.

Each ticks as the runbook's corresponding section completes.

## Decisions

- **Version is 1.5.0.** Already bumped at M12 Phase 7 across
  `pyproject.toml` and `tests/test_packaging.py`; `__version__`
  reads through `importlib.metadata.version("docs-cli")` per
  the M12 SoT refactor — so the version comes from
  `pyproject.toml`'s `[project] version` automatically.
  M13 publishes that version verbatim. Mirrors the M9/M11
  cadence (one bump per implementation milestone; only the
  implementation milestone's version reaches PyPI).
- **Manual `twine`, not Trusted Publishing.** Continues the
  M6 + M9 + M11 stance. OIDC / GitHub-Actions Trusted
  Publishing remains a future iteration; manual `twine` is
  acceptable at v1.5. Revisit at v2 if the manual flow
  proves cumbersome.
- **TestPyPI rehearsal under disambiguated dist name.**
  Continues the M9/M11 detour while the TestPyPI `docs-cli`
  squatter project is still parked. M13 re-checks ownership
  at the operator-prep step; if the squatter project ever
  lapses, M13 (or a later release) drops the rehearsal-name
  detour.
- **Fresh artifacts at M13, not the M12 Phase 8 build.** The
  M12 Phase 8 dist/ predates any merge-to-main commits and
  any M13-only edits (none expected, but enforce the
  discipline per M11). M13 rebuilds from post-merge-to-main
  HEAD at publish time.
- **Repo visibility flip is N/A.** Repo is already public
  from M9's post-release sequence.
- **No feature work in M13.** No new verbs, no scope
  additions. M13 is a publish-only milestone mirroring
  M9's/M11's discipline; mixing release-event work with
  feature work is rejected by design (consistent with the
  M11 scope decision).
- **CHANGELOG publish-survival wording already locked.** The
  M12 `## 1.5.0 — UNRELEASED` entry was authored conservatively
  per the M11 lesson — no "ready locally" / "deferred to MX"
  sentences. M13's runbook step is mechanical: drop
  `UNRELEASED`, replace with publish date, re-verify body
  reads accurately. No `gh release edit` amend post-publish
  expected (the M11 deviation should not recur).

## Testing / Quality Gate

The same tree-wide gate the M12 implementation ran, plus the
publish-specific smokes the runbook details:

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

Plus the M13-specific dogfood: walk
[release-runbook.md](../../release-runbook.md) end-to-end against
TestPyPI then real PyPI, with the smoke set covering the four
M12 headline contracts (project rename round-trip + touch
outside-root refusal + archive referring-edge rewrite + version
SoT via `importlib.metadata`).

## Success Criteria

M13 is complete when:

- [x] `pip install docs-cli==1.5.0` works from PyPI on a clean
      host with Python 3.11+ and produces a working `docs`
      command.
- [x] `docs --version` from the PyPI-installed wheel prints
      `docs 1.5.0`.
- [x] `docs project rename` against a copied fixture tree
      round-trips byte-identical (the headline M12 contract —
      re-verified against the published artefact, not just the
      local build).
- [x] `docs touch <path>` outside any `.docs.toml`-rooted tree
      refuses with exit 2 and leaves the file unchanged (M12
      wart fix — re-verified against the PyPI-served wheel).
- [x] `docs archive <doc>` rewrites referring `Related:`
      edges atomically across the active tree (M12 wart fix —
      re-verified against the PyPI-served wheel).
- [x] `docs install-skill` from the PyPI-installed wheel
      places a host-correct skill that drives the verbs
      identically to the in-repo install.
- [x] The `v1.5.0` tag and GitHub release exist at
      `https://github.com/ArtRichards/docs-cli/releases/tag/v1.5.0`.
- [x] All Phase Checklist items above are ticked.
- [x] `docs/status.md` reflects M12 + M13 as Complete with the
      actual publish date.
- [x] `docs/m13-pypi-publish-impl.md` carries a
      milestone-completion summary with the published version
      (`1.5.0` — assuming no TestPyPI-surfaced regression
      forces a `1.5.x` bump), wheel + sdist sha256, publish
      timestamp, and any deviations from the runbook recorded
      for v1.6+ reference.

## OPEN QUESTIONS

_None at draft time. The release-runbook has M11's cumulative
lessons + deviations folded in, so M13 inherits them
automatically (no separate carry-forward decision needed).
Open questions surfaced during the publish walk (TestPyPI
ownership status; token re-scope status; any runbook-deviation
needed for v1.5 specifically) will be recorded in the
Milestone-completion summary as they surface, mirroring the
M9/M11 pattern._

## Milestone-completion summary

**M13 complete — `docs-cli==1.5.0` shipped to PyPI 2026-05-29.**
Driven end-to-end via `/ship-milestone M13` walking
[release-runbook.md](../../release-runbook.md) (M13 has no TDD code
phases; the runbook sections are the phases).

- **PyPI:** https://pypi.org/project/docs-cli/1.5.0/
- **TestPyPI rehearsal:**
  https://test.pypi.org/project/docs-cli-rehearsal/1.5.0/
- **Published artefact sha256 (chain-of-custody anchors):**
  - wheel `docs_cli-1.5.0-py3-none-any.whl`:
    `b8023fffb3393aeff5ac85943164a414916e06ea85e68502e167f0948e85b70b`
  - sdist `docs_cli-1.5.0.tar.gz`:
    `c5f83c6d57c63c7116e06a777eb0f0394968b0233fe15f0a084c2ab2c61f9c39`
- **Chain-of-custody:** PyPI-served wheel sha256 byte-identical
  to the local Phase 4 build — bit-perfect (matches M11).
- **Quality gate at publish:** 433 passed; ruff / ruff format /
  mypy clean tree-wide; `docs check docs/` exit 0;
  `docs index --root docs/ --dry-run` idempotent.
- **Smoke + four M12 headline contracts** verified against the
  PyPI-served wheel: `docs --version` → `docs 1.5.0`;
  `docs project rename` round-trips byte-identical;
  `docs touch` outside any docs root refuses with exit 2 and
  leaves the file unchanged; `docs archive` rewrites referring
  `Related:` edges atomically; version flows through
  `importlib.metadata`. `install-skill` byte-identical /
  no-op / `--symlink` exit 2.
- **`v1.5.0`** annotated tag at the M13 Phase 4 commit
  (the dated-CHANGELOG commit whose tree matches PyPI); GitHub
  release live with notes sourced from the `## 1.5.0` CHANGELOG
  section.

### Deviations (recorded for v1.6+)

1. **TestPyPI rehearsal wheel prints `docs 0.0.0+local`, not
   `docs 1.5.0`.** New since M12: `__version__` reads
   `importlib.metadata.version("docs-cli")`, but the rehearsal
   detour installs the distribution as `docs-cli-rehearsal`, so
   the lookup misses and falls back to the documented
   `0.0.0+local`. This is *not* a regression — the version
   string is genuinely verified against the canonical-name
   local wheel (Phase 2) and the real PyPI wheel (Phase 4),
   both of which print `docs 1.5.0`. M9/M11 never hit this
   because `__version__` was hardcoded pre-M12. **Runbook
   action taken:** the version probe in the TestPyPI block now
   carries a caveat; verify `docs --version` against the
   canonical-name wheels, never the rehearsal wheel.
2. **`CHANGELOG.md` is not shipped inside the sdist.** The
   hatchling sdist captures `src/`, `docs/`, `tests/`,
   `README.md`, `LICENSE`, `pyproject.toml` — but not
   `CHANGELOG.md` (verified: `tar tzf … | grep -c CHANGELOG`
   → 0). This corrects the runbook's "the sdist captures
   docs/ + CHANGELOG.md" claim and explains why the Phase 2
   and Phase 4 sdist sha256 were byte-identical despite the
   CHANGELOG date edit between them (only `docs/`, unchanged,
   affects the sdist). Harmless: the dated CHANGELOG ships via
   the git repo and the GitHub release notes.

No version bump was forced — the TestPyPI rehearsal surfaced no
packaging regression (the `0.0.0+local` print is the
rename-detour artifact above, not a defect), so `1.5.0`
published as-is. Token re-scope to project-`docs-cli` continues
to roll forward as the M9 open follow-on (async operator UI
work; not a release blocker).
