# M9 — PyPI publish 1.3.0

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-05-24

Related:
- parent-of: m9-pypi-publish-log.md
- child-of: plan.md
- pairs-with: release-runbook.md
- pairs-with: m6-pypi-distribution.md
- pairs-with: m7-migration-accuracy.md
- pairs-with: m8-adoption-workflow.md

## Overview

> **Stub-drafted 2026-05-24, post M6 scope reframe.** M9 enters
> active state once M8 ships. The operative checklist is
> [release-runbook.md](release-runbook.md); this milestone doc
> exists to give the publish work a named home, exit criteria,
> and a log to record what actually happened.

- Milestone: M9 (the v1.1 publish milestone)
- Title: PyPI publish `docs-cli` 1.3.0
- Surface: an operator-driven release of the post-M8 tree to PyPI
  as `docs-cli==1.3.0`, plus the public-flip of the GitHub repo,
  the v1.3.0 tag + GitHub release, and the post-publish doc
  closeouts that turn M6 / M7 / M8 / M9 rows in `status.md` and
  `plan.md` into `Complete (DATE)`.
- Status: DRAFT — activates when M8 ships

### Goal

M6 delivered the packaging machinery — wheel build, entry point,
`install-skill` verb, runbook scaffold, GitHub repo. It did **not**
publish. The 2026-05-24 scope reframe split the publish out of M6
and parked it here so M6 could close cleanly rather than hang for
the M7 + M8 weeks at "implementation done, publish pending".

M9 is the publish. It is operator-driven by design: register PyPI
+ TestPyPI accounts, mint API tokens, bump versions, restructure
the CHANGELOG to cover M6 + M7 + M8, rebuild fresh artifacts,
TestPyPI rehearsal, real PyPI publish, post-release closeouts.
No code work; no new verbs; no TDD phases. The success criterion
is concrete: a fresh venv on a clean host can `pip install
docs-cli==1.3.0`, `docs --version` prints `docs 1.3.0`, `docs
install-skill` materialises a working bundled skill, and the
public GitHub repo carries the matching `v1.3.0` tag + release.

### Requirements

- **Version is `1.3.0`.** The batched M6 + M7 + M8 ship — one
  bump per implementation milestone — landing at 1.3.0. Intermediate
  versions `1.1.0` and `1.2.0` are never published (no public
  release exists to break continuity with). Recorded as a Decision
  in M6 and reaffirmed here.
- **Pre-publish operator prep** (account registration, 2FA, API
  tokens, `~/.pypirc`) is done in parallel with M7 / M8 so the
  publish window itself is purely `twine upload`. The runbook
  carries the per-step checklist.
- **Pre-publish tree state** (`pyproject.toml` version bump,
  `__version__` bump in `src/docs_cli/cli.py`, CHANGELOG
  restructure to add M7 + M8 sections under a `## 1.3.0 —
  UNRELEASED` header, `docs/INDEX.md` + fixture lockstep) is
  operator-executed at M9 start. The runbook carries the per-step
  checklist.
- **Quality gate green tree-wide** before any upload: pytest
  (≥ 271, raised by M7 + M8 — the actual count gets recorded into
  the runbook checklist at the moment of run), ruff, ruff format,
  mypy, `docs check docs/`, `docs index --root docs/ --dry-run`.
- **Fresh artifact build.** The May 23 M6 wheel + sdist sitting in
  local `dist/` are **not** uploaded. M9 rebuilds from the post-M8
  tree (`rm -rf dist/ && python -m build`), runs `twine check`,
  and exercises every install-skill code path in a throwaway
  local venv.
- **TestPyPI rehearsal is non-optional.** Upload to TestPyPI,
  install from TestPyPI into a fresh `/tmp/docs-test-venv`,
  exercise the smoke set. If anything fails, bump to `1.3.1`
  (TestPyPI also rejects re-uploads of the same version) and
  rerun from artifact build.
- **Real PyPI publish.** `twine upload dist/*` to PyPI, install
  from PyPI into a fresh `/tmp/docs-real-venv`, re-run the smoke
  subset against the real artifact.
- **Post-release sequence.** `gh repo edit ... --visibility
  public`, `git tag v1.3.0 && git push origin v1.3.0`, `gh release
  create v1.3.0`, re-scope PyPI API tokens from entire-account to
  project-`docs-cli`-scoped, doc closeouts (M6 / M7 / M8 / M9 rows
  in `status.md` and `plan.md` → Complete; `docs/INDEX.md` +
  `tests/fixtures/expected/docs-INDEX.md` regenerated in lockstep).

### Deliverables

- [ ] PyPI release `docs-cli` 1.3.0 published; project page live
      at `https://pypi.org/project/docs-cli/1.3.0/`.
- [ ] TestPyPI release `docs-cli` 1.3.0 published as the
      rehearsal artifact at `https://test.pypi.org/project/docs-cli/1.3.0/`.
- [ ] `pyproject.toml` `version` and `src/docs_cli/cli.py`
      `__version__` bumped from `1.1.0` to `1.3.0`.
- [ ] `CHANGELOG.md` carries a `## 1.3.0 — <DATE>` section
      describing the M6 + M7 + M8 surface.
- [ ] GitHub repo `ArtRichards/docs-cli` flipped from private to
      public.
- [ ] `v1.3.0` git tag pushed; GitHub release created with notes
      sourced from the CHANGELOG section.
- [ ] PyPI + TestPyPI API tokens re-scoped to project
      `docs-cli`; entire-account bootstrap tokens revoked.
- [ ] `docs/status.md`: M6 / M7 / M8 / M9 rows → Complete (DATE);
      "Current milestone" + "Next action" rewritten; v1.1
      declared shipped (or pointing at the v1.2 roadmap if one
      exists by then).
- [ ] `docs/plan.md`: M6 / M7 / M8 / M9 rows → shipped.
- [ ] `docs/m9-pypi-publish.md` (this file): Phase Checklist
      ticked; milestone-completion summary appended.
- [ ] `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
      regenerated in lockstep.

## Phase Checklist

M9 has no TDD code phases — it is an operational milestone. The
runbook's sections are the phases:

- [ ] Operator one-time prep — accounts + 2FA + API tokens +
      `~/.pypirc` (done in parallel with M7 / M8)
- [ ] Pre-publish prep — version bump, CHANGELOG restructure,
      tree state, quality gate, artifact build, local smoke
- [ ] TestPyPI rehearsal
- [ ] Real PyPI publish
- [ ] Post-release — repo public, tag + GitHub release, token
      re-scope, doc closeouts

Each ticks as the runbook's corresponding section completes.

## Decisions

- **Version is 1.3.0** (reaffirms M6 + plan.md decision). One
  bump per implementation milestone: M6 = 1.1.0, M7 = 1.2.0,
  M8 = 1.3.0; only the M8-ship version reaches PyPI.
- **Manual `twine`, not Trusted Publishing.** Continues the M6
  stance. OIDC / GitHub-Actions Trusted Publishing is a
  future-iteration follow-up if the manual flow proves cumbersome
  at v1.4 / v2.
- **TestPyPI rehearsal is mandatory**, not a "nice to have."
  PyPI is append-only; a bad upload burns the version number.
- **Fresh artifacts at M9, not the May 23 M6 build.** The M6
  artifacts predate M7 + M8 code changes and the version bump.
- **GitHub repo flip to public happens at M9 post-release**,
  not earlier — keeps the repo private until the artifact is
  live and verified working.

## Testing / Quality Gate

The same tree-wide gate the other v1.1 milestones run, plus the
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

Plus the M9-specific dogfood: walk [release-runbook.md](release-runbook.md)
end-to-end against TestPyPI then real PyPI.

## Success Criteria

M9 is complete when:

- [ ] `pip install docs-cli==1.3.0` works from PyPI on a clean
      host with Python 3.11+ and produces a working `docs` command.
- [ ] `docs install-skill` from the PyPI-installed wheel places a
      host-correct skill that drives the verbs identically to the
      in-repo install.
- [ ] The GitHub repo `ArtRichards/docs-cli` is public; the
      `v1.3.0` tag and release exist.
- [ ] All Phase Checklist items above are ticked.
- [ ] `docs/status.md` reflects M6 / M7 / M8 / M9 as Complete
      with the actual publish date.
- [ ] `docs/m9-pypi-publish-log.md` carries a
      milestone-completion summary describing what actually
      happened (which `1.3.x` shipped — if TestPyPI surfaced a
      bug forcing a `1.3.1` rebuild, the published version, the
      sha256 of the published wheel + sdist, the publish
      timestamp, any deviations from the runbook).

## OPEN QUESTIONS

_None at draft time. Open questions surface when M9 activates
(post-M8 ship) and the operator walks the runbook._
