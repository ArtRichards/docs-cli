# M11 — PyPI publish 1.4.0

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-05-27

Related:
- parent-of: m11-pypi-publish-impl.md
- child-of: plan.md
- pairs-with: release-runbook.md
- pairs-with: status.md
- pairs-with: archive/2026-05-27/m10-adoption-polish.md

## Overview

> **Stub-drafted 2026-05-27, post M10 closeout.** M11 enters
> active state immediately — the M10 wheel + sdist already live
> in local `dist/` and pass `twine check`. The operative
> checklist is [release-runbook.md](release-runbook.md); this
> milestone doc exists to give the publish work a named home,
> exit criteria, and a log to record what actually happened.

- Milestone: M11 (the v1.4 publish milestone)
- Title: PyPI publish `docs-cli` 1.4.0
- Surface: an operator-driven release of the post-M10 tree to PyPI
  as `docs-cli==1.4.0`, plus the `v1.4.0` git tag, the GitHub
  release with artefacts attached, and the post-publish doc
  closeouts that turn the M10 + M11 rows in `status.md` and
  `plan.md` into the post-publish narrative.
- Status: Active (Phase 1 opens immediately — M10 already built
  fresh 1.4.0 artefacts during its Phase 8 + Phase 10)

### Goal

M10 delivered the adoption-flow polish + 1.3.0 carry-overs (multi-file
atomic `docs touch`, `docs migrate --apply` auto-writes `.docs.toml`,
`--apply --quiet` truly silent, `[vocabulary] add_fields` allowlist +
`unknown-field` check rule, `Confidence` enum, `MigrationPlan.excluded_count`
removal, 4-step adoption playbook restructure). It did **not** publish.
Per the M7/M8/M10 cadence (build locally + publish in a separate milestone),
M11 is the publish.

M11 is operator-driven by design: re-confirm pre-publish prep, rebuild
fresh artefacts from the post-M10 tree (the M10 Phase 10 dist/ exists
and passes `twine check`, but a fresh rebuild at M11 start is the
discipline), TestPyPI rehearsal under the disambiguated dist name
`docs-cli-rehearsal==1.4.0` (continuing M9's TestPyPI-squatter detour),
real PyPI publish, tag + GitHub release, post-release closeouts. No
code work; no new verbs; no TDD code phases. The success criterion is
concrete: a fresh venv on a clean host can `pip install
docs-cli==1.4.0`, `docs --version` prints `docs 1.4.0`, `docs migrate
--apply --quiet <tree>` is genuinely quiet (the headline M10 contract),
`docs check <tree>` exits 0, and the public GitHub repo carries the
matching `v1.4.0` tag + release.

### Requirements

- **Version is `1.4.0`.** Already bumped at M10 Phase 7 (`pyproject.toml`
  + `src/docs_cli/cli.py:__version__` + `tests/test_packaging.py`
  pinned to 1.4.0). M11 publishes that version verbatim.
- **Pre-publish operator state already current** from M9 — PyPI +
  TestPyPI accounts registered, 2FA active, API tokens in `~/.pypirc`.
  The M9 follow-on "token re-scope from entire-account to
  project-`docs-cli`" remains operator-side async work; M11 publishes
  with whatever scope the tokens currently carry. If re-scoping landed
  between M9 and M11, the runbook step is a no-op; if not, the publish
  proceeds with the bootstrap tokens and the re-scope follow-on rolls
  forward.
- **CHANGELOG `## 1.4.0` is already dated 2026-05-27** (landed at M10
  Phase 10). The runbook's "replace UNRELEASED with today's date" step
  is therefore a verify-only step at M11 (not a no-op — confirm the
  date matches reality at publish time; if M11 publishes on a different
  date the entry needs a one-line bump).
- **Quality gate green tree-wide** before any upload: pytest (401 at
  M10 closeout — exact count gets recorded into the runbook checklist
  at the moment of M11 run), ruff, ruff format, mypy, `docs check
  docs/`, `docs index --root docs/ --dry-run`.
- **Fresh artifact build at M11 start.** The 2026-05-27 M10 Phase 10
  wheel + sdist sitting in local `dist/` is the M10 closeout-commit
  build; M11 rebuilds from the post-merge-to-main tree (which carries
  the M10 stack + any M11-only edits) so the artefact-bytes line up
  with what `git log --oneline main` will show at the moment of
  publish.
- **TestPyPI rehearsal is non-optional** (mirrors M9). Upload to
  TestPyPI under `docs-cli-rehearsal==1.4.0` (the bare `docs-cli` name
  is parked on TestPyPI per the M9 open follow-on; re-check ownership
  at M11 start in case the squatter project lapsed), install from
  TestPyPI into a fresh `/tmp/docs-test-venv`, exercise the smoke set
  including the headline M10 contracts (`docs migrate --apply --quiet`
  against a synthetic foreign tree; `.docs.toml` auto-emitted; `docs
  check` exit 0). If anything fails, bump to `1.4.1` (TestPyPI also
  rejects re-uploads of the same version) and rerun from artifact
  build.
- **Real PyPI publish.** `twine upload dist/*` to PyPI, install from
  PyPI into a fresh `/tmp/docs-real-venv`, re-run the smoke subset
  against the real artefact.
- **Post-release sequence.** `git tag v1.4.0 && git push origin
  v1.4.0`, `gh release create v1.4.0` with notes sourced from the
  CHANGELOG `## 1.4.0` section, doc closeouts (M10 + M11 rows in
  `status.md` and `plan.md` finalised; `docs/INDEX.md` +
  `tests/fixtures/expected/docs-INDEX.md` regenerated in lockstep).
  No repo-visibility flip — repo is already public from M9.

### Deliverables

- [ ] PyPI release `docs-cli` 1.4.0 published; project page live
      at `https://pypi.org/project/docs-cli/1.4.0/`.
- [ ] TestPyPI release `docs-cli-rehearsal` 1.4.0 published as the
      rehearsal artifact at
      `https://test.pypi.org/project/docs-cli-rehearsal/1.4.0/`
      (continues the M9 disambiguated dist-name detour).
- [ ] `pyproject.toml` `version` and `src/docs_cli/cli.py`
      `__version__` confirmed at `1.4.0` (already landed at M10
      Phase 7).
- [ ] `CHANGELOG.md` `## 1.4.0` section date matches publish day;
      if mismatch, one-line bump.
- [ ] `v1.4.0` git tag pushed; GitHub release created with notes
      sourced from the CHANGELOG `## 1.4.0` section.
- [ ] `docs/status.md`: M10 + M11 rows finalised; "Current milestone"
      + "Next action" rewritten post-publish.
- [ ] `docs/plan.md`: M10 + M11 rows finalised.
- [ ] `docs/m11-pypi-publish.md` (this file): Phase Checklist
      ticked; milestone-completion summary appended; lifecycle
      archived via `docs archive --cascade`.
- [ ] `docs/m11-pypi-publish-impl.md`: per-phase log entries + final
      milestone-completion summary; stays `Lifecycle: active` after
      milestone-doc archive (per the M8/M9/M10 pattern).
- [ ] `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
      regenerated in lockstep.

## Phase Checklist

M11 has no TDD code phases — it is an operational milestone. The
runbook's sections are the phases (mirrors M9 exactly):

- [ ] Operator one-time prep — verify M9-era state (accounts + 2FA +
      tokens + `~/.pypirc`) still current; re-check TestPyPI
      `docs-cli` ownership in case the squatter lapsed since
      2026-05-25
- [ ] Pre-publish prep — versions verified `1.4.0`, CHANGELOG date
      matches publish day, tree state clean (post-merge-to-main),
      quality gate green (pytest 401 at M10 closeout), fresh
      artifact build, local smoke
- [ ] TestPyPI rehearsal — under disambiguated dist name
      `docs-cli-rehearsal==1.4.0` unless TestPyPI ownership of the
      bare name changed; smoke set MUST include `docs migrate --apply
      --quiet` against a synthetic foreign tree
- [ ] Real PyPI publish — `docs-cli==1.4.0` live; sha256
      chain-of-custody from build → upload → PyPI-served wheel
      verified bit-perfect
- [ ] Post-release — `v1.4.0` tag + GitHub release; doc closeouts
      (M10 + M11); token re-scope rolls forward as M9 open follow-on
      (operator UI work, async)

Each ticks as the runbook's corresponding section completes.

## Decisions

- **Version is 1.4.0.** Already bumped at M10 Phase 7 across
  `pyproject.toml`, `__version__`, and `tests/test_packaging.py`;
  M11 publishes that version verbatim. Mirrors the M9 cadence
  (one bump per implementation milestone; only the implementation
  milestone's version reaches PyPI).
- **Manual `twine`, not Trusted Publishing.** Continues the M6 + M9
  stance. OIDC / GitHub-Actions Trusted Publishing remains a future
  iteration; manual `twine` is acceptable at v1.4. Revisit at v2 if
  the manual flow proves cumbersome.
- **TestPyPI rehearsal under disambiguated dist name.** Continues
  the M9 detour while the TestPyPI `docs-cli` squatter project is
  still parked. M11 re-checks ownership at the operator-prep step;
  if the squatter project ever lapses, M11 (or a later release)
  drops the rehearsal-name detour.
- **Fresh artifacts at M11, not the M10 Phase 10 build.** The M10
  Phase 10 dist/ predates any merge-to-main commits and any M11-only
  edits (none expected, but enforce the discipline). M11 rebuilds
  from post-merge-to-main HEAD at publish time.
- **Repo visibility flip is N/A.** Repo is already public from M9's
  post-release sequence.
- **No project-rename verb in M11.** The M10 follow-on TODO
  (first-class `docs project rename <new-name>`) stays deferred —
  M11 is a publish-only milestone mirroring M9's discipline; mixing
  release-event work with feature work was explicitly rejected
  during M11 scope confirmation (operator answer 2026-05-27).

## Testing / Quality Gate

The same tree-wide gate the M10 implementation ran, plus the
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

Plus the M11-specific dogfood: walk [release-runbook.md](release-runbook.md)
end-to-end against TestPyPI then real PyPI, with the smoke set
covering the headline M10 contracts (`docs migrate --apply --quiet`
truly silent; `.docs.toml` auto-emitted; `docs check` exit 0).

## Success Criteria

M11 is complete when:

- [ ] `pip install docs-cli==1.4.0` works from PyPI on a clean
      host with Python 3.11+ and produces a working `docs` command.
- [ ] `docs --version` from the PyPI-installed wheel prints
      `docs 1.4.0`.
- [ ] `docs migrate --apply --quiet <foreign-tree>` from the
      PyPI-installed wheel produces empty stdout + empty stderr
      (the headline M10 contract — re-verified against the
      published artefact, not just the local build).
- [ ] `docs install-skill` from the PyPI-installed wheel places a
      host-correct skill that drives the verbs identically to the
      in-repo install.
- [ ] The `v1.4.0` tag and GitHub release exist at
      `https://github.com/ArtRichards/docs-cli/releases/tag/v1.4.0`.
- [ ] All Phase Checklist items above are ticked.
- [ ] `docs/status.md` reflects M10 + M11 as Complete with the
      actual publish date.
- [ ] `docs/m11-pypi-publish-impl.md` carries a
      milestone-completion summary describing what actually
      happened (which `1.4.x` shipped — if TestPyPI surfaced a
      bug forcing a `1.4.1` rebuild, the published version, the
      sha256 of the published wheel + sdist, the publish
      timestamp, any deviations from the runbook).

## OPEN QUESTIONS

_None at draft time. Open questions surfaced during the publish
walk (TestPyPI ownership status; token re-scope status; any
runbook-deviation needed for v1.4 specifically) will be recorded
in the Milestone-completion summary as they surface, mirroring
the M9 pattern._
