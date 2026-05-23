# Release Runbook

Status: draft
Role: runbook
Project: docs
Updated: 2026-05-23

Related:
- pairs-with: m6-pypi-distribution.md
- pairs-with: status.md

Per-release checklist for shipping a new `docs-cli` to PyPI. Finalised at
M6 Phase 7 with the workflow wiring; this skeleton is the Phase 9 (TestPyPI
dress rehearsal) and Phase 10 (real PyPI) oracle. Each row stays unchecked
until satisfied against a published artefact.

## Pre-flight

- [ ] `docs/status.md` reflects the milestone state about to ship.
- [ ] `docs/plan.md` reflects the milestone state about to ship.
- [ ] `pyproject.toml`'s `version` is the next intended PyPI version.
- [ ] `__version__` in `src/docs_cli/cli.py` matches `pyproject.toml`.
- [ ] `docs/INDEX.md` regenerated; `tests/fixtures/expected/docs-INDEX.md`
      lockstep-updated.
- [ ] `.venv/bin/python -m pytest tests/ -q` — full suite green.
- [ ] `.venv/bin/ruff check .` — clean.
- [ ] `.venv/bin/ruff format --check .` — clean.
- [ ] `.venv/bin/mypy` — clean.
- [ ] `docs check docs/` — exit 0.
- [ ] `python -m build` outside the in-test path — wheel + sdist build clean.

## TestPyPI rehearsal (Phase 9)

- [ ] Trigger `testpypi.yml` (`workflow_dispatch`).
- [ ] Workflow exits 0; wheel + sdist appear on `test.pypi.org/project/docs-cli`.
- [ ] Throwaway venv: `python3 -m venv /tmp/docs-test-venv`.
- [ ] `pip install --index-url https://test.pypi.org/simple/ docs-cli==<VERSION>`
      from the throwaway venv — succeeds.
- [ ] `docs --version` from the throwaway venv prints `<VERSION>`.
- [ ] `docs --help` from the throwaway venv lists every verb including
      `install-skill`.
- [ ] `docs install-skill --dest /tmp/docs-test-skill` materialises the
      bundled tree byte-identical to `src/docs_cli/skill/`.
- [ ] `docs check tests/fixtures/trees/minimal/` (a clean fixture) — exit 0.
- [ ] `docs index --root docs/ --dry-run` against this repo — exit 0 (no diff).

## Real PyPI publish (Phase 10)

- [ ] GitHub repo flipped from private to public:
      `gh repo edit ArtRichards/docs-cli --visibility public --accept-visibility-change-consequences`.
- [ ] Tag pushed: `git tag v<VERSION> && git push origin v<VERSION>`.
- [ ] `release.yml` (tag-triggered) workflow exits 0.
- [ ] Wheel + sdist appear on `pypi.org/project/docs-cli`.
- [ ] Throwaway venv: `python3 -m venv /tmp/docs-real-venv`.
- [ ] `pip install docs-cli==<VERSION>` from the throwaway venv — succeeds.
- [ ] Smoke subset of the TestPyPI rows re-runs against the real artefact.
- [ ] GitHub release notes written referencing the milestone's completion
      summary.

## Post-release

- [ ] `docs/status.md` flipped to the milestone Complete state.
- [ ] `docs/plan.md` row updated to "shipped".
- [ ] Milestone-completion summary appended to the milestone plan + log.
- [ ] `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` regenerated
      in lockstep.

## Notes

- **Trusted Publishing (OIDC)** is the auth mechanism — no long-lived PyPI
  token in repo secrets. Configure the PyPI Trusted Publisher binding once
  for `docs-cli`.
- A PyPI release is **append-only**. A bad artefact can be yanked but not
  deleted; TestPyPI rehearsal is non-optional.
- The release-runbook is finalised at M6 Phase 7. Until then this skeleton
  exists as the Phase 2 RED checklist surface.