# Release Runbook

Status: active
Role: runbook
Project: docs
Updated: 2026-05-24

Related:
- pairs-with: m6-pypi-distribution.md
- pairs-with: status.md

Per-release checklist for shipping a new `docs-cli` to PyPI. **M6 ships
via manual twine** (operator override of the draft-time
GitHub-Actions/Trusted-Publishing recommendation): the implementation
agent prepares the artifacts and verifies them locally; the operator
runs the actual `twine upload` and the post-publish tag/visibility/
release-create sequence. The Trusted-Publishing path is preserved as a
future-iteration note at the bottom of this file.

## Pre-flight (impl agent runs at Phase 8 + 9)

- [ ] `docs/status.md` reflects the milestone state about to ship.
- [ ] `docs/plan.md` reflects the milestone state about to ship.
- [ ] `pyproject.toml`'s `version` is the next intended PyPI version.
- [ ] `__version__` in `src/docs_cli/cli.py` matches `pyproject.toml`.
- [ ] `CHANGELOG.md` `## <VERSION>` entry exists (the `UNRELEASED`
      placeholder is replaced with today's date at operator-publish time).
- [ ] `docs/INDEX.md` regenerated; `tests/fixtures/expected/docs-INDEX.md`
      lockstep-updated.
- [ ] `.venv/bin/python -m pytest tests/ -q` — full suite green.
- [ ] `.venv/bin/ruff check .` — clean.
- [ ] `.venv/bin/ruff format --check .` — clean.
- [ ] `.venv/bin/mypy` — clean.
- [ ] `docs check docs/` — exit 0.
- [ ] Rebuild artifacts cleanly:
      ```sh
      rm -rf dist/
      .venv/bin/python -m build
      ```
      Expected output: `dist/docs_cli-<VERSION>-py3-none-any.whl` +
      `dist/docs_cli-<VERSION>.tar.gz`.
- [ ] `.venv/bin/pip install --quiet twine` (if not already present).
- [ ] `.venv/bin/twine check dist/*` — both artifacts PASS.
- [ ] Local install smoke into a throwaway venv:
      ```sh
      python3 -m venv /tmp/docs-local-smoke
      /tmp/docs-local-smoke/bin/pip install dist/docs_cli-<VERSION>-py3-none-any.whl
      /tmp/docs-local-smoke/bin/docs --version          # → "docs <VERSION>"
      /tmp/docs-local-smoke/bin/docs --help             # lists install-skill
      /tmp/docs-local-smoke/bin/docs install-skill --dest /tmp/skill-smoke
      diff -ru src/docs_cli/skill /tmp/skill-smoke      # empty (byte-identical)
      /tmp/docs-local-smoke/bin/docs install-skill --dest /tmp/skill-smoke   # exit 0 (no-op)
      /tmp/docs-local-smoke/bin/docs install-skill --dest /tmp/skill-smoke --symlink   # exit 2
      /tmp/docs-local-smoke/bin/docs check tests/fixtures/trees/minimal/    # exit 0
      ```

## TestPyPI rehearsal (operator runs after Phase 9 handoff)

Operator should have a PyPI API token configured at
`~/.pypirc` under the `[testpypi]` section, or pass `--username
__token__` + `--password $TESTPYPI_TOKEN` inline. (Trusted-Publishing
note at the bottom for the future-CI alternative.)

- [ ] Upload to TestPyPI:
      ```sh
      .venv/bin/twine upload --repository testpypi dist/*
      ```
- [ ] Artifact visible at `https://test.pypi.org/project/docs-cli/<VERSION>/`.
- [ ] Throwaway venv install from TestPyPI:
      ```sh
      python3 -m venv /tmp/docs-test-venv
      /tmp/docs-test-venv/bin/pip install --index-url https://test.pypi.org/simple/ \
          --extra-index-url https://pypi.org/simple/ \
          docs-cli==<VERSION>
      ```
      (The `--extra-index-url` lets pip resolve `docs-cli`'s
      well-formed dist-info even though we have no runtime deps; it
      also prevents a future-day surprise if a dep is added.)
- [ ] `/tmp/docs-test-venv/bin/docs --version` → `docs <VERSION>`.
- [ ] `/tmp/docs-test-venv/bin/docs install-skill --dest /tmp/docs-test-skill`
      → bundled tree appears byte-identical to `src/docs_cli/skill/`.
- [ ] `/tmp/docs-test-venv/bin/docs install-skill --dest /tmp/docs-test-skill --symlink`
      → exit 2 (wheel-install rejects symlink; the dest is left
      unchanged).
- [ ] `/tmp/docs-test-venv/bin/docs check tests/fixtures/trees/minimal/`
      → exit 0.
- [ ] `/tmp/docs-test-venv/bin/docs index --root docs/ --dry-run`
      → exit 0.

## Real PyPI publish (operator runs after TestPyPI passes)

- [ ] Operator's `~/.pypirc` has a `[pypi]` token configured (or
      `--username __token__ --password $PYPI_TOKEN` inline).
- [ ] Replace `## <VERSION> — UNRELEASED` in `CHANGELOG.md` with
      today's date; commit on `main` (or on the milestone branch
      before merging — operator's call).
- [ ] Upload to PyPI:
      ```sh
      .venv/bin/twine upload dist/*
      ```
- [ ] Artifact visible at `https://pypi.org/project/docs-cli/<VERSION>/`.
- [ ] Throwaway venv install from PyPI:
      ```sh
      python3 -m venv /tmp/docs-real-venv
      /tmp/docs-real-venv/bin/pip install docs-cli==<VERSION>
      ```
- [ ] Re-run the smoke subset (`docs --version`, `docs install-skill --dest …`,
      `docs check tests/fixtures/trees/minimal/`) against the real artifact.

## Post-release (operator)

- [ ] Flip the GitHub repo to public:
      ```sh
      gh repo edit ArtRichards/docs-cli \
          --visibility public --accept-visibility-change-consequences
      ```
- [ ] Tag and push:
      ```sh
      git tag v<VERSION>
      git push origin v<VERSION>
      ```
- [ ] Create the GitHub release:
      ```sh
      gh release create v<VERSION> \
          --title "docs-cli <VERSION>" \
          --notes "$(awk '/^## <VERSION> —/{flag=1; next} /^## /{flag=0} flag' CHANGELOG.md)"
      ```
      (Or hand-author the notes referencing the milestone's
      Milestone-completion summary in `docs/<milestone>.md`.)
- [ ] `docs/status.md` flipped to the milestone Complete state.
- [ ] `docs/plan.md` row updated to "shipped".
- [ ] Milestone-completion summary appended to the milestone plan +
      log (impl agent did the closeout at Phase 10; operator's
      post-publish edits flip the timestamps and the M6 row).
- [ ] `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
      regenerated in lockstep.

## Notes

- A PyPI release is **append-only**. A bad artifact can be yanked but
  not deleted; TestPyPI rehearsal is non-optional.
- **Manual twine vs Trusted Publishing.** M6 ships via manual twine
  per operator decision. For a future iteration, GitHub Actions
  Trusted Publishing (OIDC) would replace the API tokens entirely:
  configure the PyPI Trusted Publisher binding once, then a
  tag-triggered `.github/workflows/release.yml` exchanges a short-lived
  OIDC token for upload rights. Trade-off: no long-lived secret in
  the repo, at the cost of carrying a workflow file and depending on
  PyPI's OIDC provider behaviour. Track as a follow-up if the manual
  flow proves cumbersome.
- **Throwaway venvs.** Every smoke step builds a fresh venv at
  `/tmp/docs-<purpose>-venv` so a previous failed install can't
  pollute the next attempt. Clean up after success:
  `rm -rf /tmp/docs-*-venv /tmp/docs-*-skill /tmp/skill-smoke`.
