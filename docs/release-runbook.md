# Release Runbook

Lifecycle: active
Role: runbook
Project: docs
Updated: 2026-05-24

Related:
- pairs-with: m9-pypi-publish.md
- pairs-with: m6-pypi-distribution.md
- pairs-with: m7-migration-accuracy.md
- pairs-with: m8-adoption-workflow.md
- pairs-with: status.md
- pairs-with: plan.md

The operator-driven checklist for shipping `docs-cli` to PyPI.
This runbook is **M9's operative artifact** — every "operator
runs X" bullet below is M9 work, walked top-to-bottom once M8
ships. The bullets are scoped tight enough to copy-paste; the
prose framing lives in [m9-pypi-publish.md](m9-pypi-publish.md).

**Publish timing.** Per operator decision 2026-05-24, the first
PyPI publish is **M9** — one batched release at version
**`1.3.0`** that ships the M6 + M7 + M8 surface together.
Intermediate versions (`1.1.0`, `1.2.0`) never reach PyPI; no
prior public release exists, so there is no continuity to
preserve. **M6's wheel + sdist sitting in local `dist/` from
2026-05-23 are not uploaded** — fresh artifacts are built at M9
start (post-M8 ship). The Trusted-Publishing/OIDC path remains
parked as a future-iteration note at the bottom of this file.

## Operator one-time prep (do BEFORE M8 ships)

Administrative and independent of code work — do these in
parallel with M7 / M8 so the publish window itself is purely
`twine upload`.

### Account registration

- [ ] Register a TestPyPI account at
      https://test.pypi.org/account/register/
- [ ] Register a PyPI account at https://pypi.org/account/register/
      (a separate service from TestPyPI — separate accounts,
      separate tokens)
- [ ] Enable 2FA on **both** accounts (PyPI requires it before
      any upload). TOTP via authenticator app is the simplest
      path; stash the recovery codes somewhere durable.

### API tokens

- [ ] Create a TestPyPI API token: Account settings → API tokens →
      "Add API token" → name `docs-cli upload`, scope **"Entire
      account"** (the per-project scope is unavailable until the
      project exists; re-scope to project after the first
      successful TestPyPI upload).
- [ ] Create a PyPI API token via the same flow on pypi.org.
- [ ] Copy each token **immediately** — they are shown once.
      Tokens begin `pypi-…`.

### Credentials file

Create `~/.pypirc` (chmod 600):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEI…YOUR-REAL-PYPI-TOKEN

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEN…YOUR-REAL-TESTPYPI-TOKEN
```

Alternative: skip `~/.pypirc` and pass
`--username __token__ --password $TOKEN` inline on each
`twine upload`.

### Name availability

`docs-cli` was verified available at M6 draft time (2026-05-23).
Re-confirm at publish time — `curl -sI https://pypi.org/simple/docs-cli/`
should return 404 (or the equivalent "no such project" response)
right up until the first successful upload.

## Pre-publish prep (M9 start, after M8 ships — operator runs)

Once M8 is merged to `main`, the operator drives this block from
`/home/user/opt/docs-cli/`. The impl agent finishing M8 does
**not** run this — M8 closes at its own Phase 10 commits.

### Version + changelog

- [ ] Bump `pyproject.toml` `version` from `1.1.0` to `1.3.0`.
- [ ] Bump `__version__` in `src/docs_cli/cli.py` from `1.1.0` to
      `1.3.0`.
- [ ] Restructure `CHANGELOG.md`:
      - Rename the `## 1.1.0 — UNRELEASED` header to
        `## 1.3.0 — UNRELEASED`.
      - Rewrite the entry-body intro ("The first PyPI release …")
        to describe a M6 + M7 + M8 batched release; note that
        the implementation milestones each landed on `main`
        separately but ship together as 1.3.0.
      - Add an `### M7 — Migration plan accuracy (breaking)`
        block under Changed: the `Status:` → `Lifecycle:`
        controlled-vocab rename (no backward compat), broadened
        role inference (suffix matching, H1 + section signals,
        sibling defaulting), project-name normalisation to
        lowercase-kebab, archive-style subdir normalisation
        (`archived/` → `archive/YYYY-MM-DD/`), expanded role
        vocab (`implementation`, `sketch`, `outline`, `memo`,
        `brief`). `add_statuses` config key renamed to
        `add_lifecycles`. **Breaking** — call it out at the top
        of the 1.3.0 entry.
      - Add an `### M8 — Adoption workflow` block under Added:
        tree-wide `--exclude` (in `migrate` + `index` + `check`
        + `list`), `.docs.toml` `[exclude]` section,
        `--summary` and `--only ambiguous` triage flags,
        `docs new --body-from <-|path>`, and the bundled skill's
        rewritten adoption-flow references.
      - Leave `UNRELEASED` in the header until the moment of
        upload (replaced with the actual publish date below).

### Tree state

- [ ] `docs/status.md` reflects M6 / M7 / M8 / M9 in flight or
      shipped state; "Current milestone" + "Next action" point
      at this runbook.
- [ ] `docs/plan.md` v1.1 section reflects the same.
- [ ] `docs/INDEX.md` regenerated; `tests/fixtures/expected/docs-INDEX.md`
      lockstep-updated.

### Quality gate (tree-wide)

- [ ] `.venv/bin/python -m pytest tests/ -q` — full suite green.
      Baseline at M6 ship was **271 passed**; M7 + M8 will raise
      that. Record the post-M8 count into this checklist before
      uploading so reviewers can spot a missing-test regression.
- [ ] `.venv/bin/ruff check .` — clean.
- [ ] `.venv/bin/ruff format --check .` — clean.
- [ ] `.venv/bin/mypy` — clean.
- [ ] `docs check docs/` — exit 0.
- [ ] `docs index --root docs/ --dry-run` — exit 0 / idempotent.

### Artifact build

- [ ] Rebuild artifacts cleanly. The May 23 M6 wheel is stale —
      `pyproject.toml` `version` and the CLI surface have moved:
      ```sh
      rm -rf dist/
      .venv/bin/python -m build
      ```
      Expected output: `dist/docs_cli-1.3.0-py3-none-any.whl` +
      `dist/docs_cli-1.3.0.tar.gz`.
- [ ] `.venv/bin/pip install --quiet twine` (if not already
      present; `twine 6.2.0` was the version smoke-tested at M6
      ship).
- [ ] `.venv/bin/twine check dist/*` — both artifacts PASS.

### Local-install smoke (no PyPI involvement)

```sh
python3 -m venv /tmp/docs-local-smoke
/tmp/docs-local-smoke/bin/pip install dist/docs_cli-1.3.0-py3-none-any.whl
/tmp/docs-local-smoke/bin/docs --version          # → "docs 1.3.0"
/tmp/docs-local-smoke/bin/docs --help             # lists install-skill + every M7/M8 verb addition
/tmp/docs-local-smoke/bin/docs install-skill --dest /tmp/skill-smoke
diff -ru src/docs_cli/skill /tmp/skill-smoke      # empty (byte-identical)
/tmp/docs-local-smoke/bin/docs install-skill --dest /tmp/skill-smoke   # exit 0 (no-op)
/tmp/docs-local-smoke/bin/docs install-skill --dest /tmp/skill-smoke --symlink   # exit 2
/tmp/docs-local-smoke/bin/docs check tests/fixtures/trees/minimal/    # exit 0
```

## TestPyPI rehearsal (operator runs)

- [ ] Upload to TestPyPI:
      ```sh
      .venv/bin/twine upload --repository testpypi dist/*
      ```
- [ ] Artifact visible at `https://test.pypi.org/project/docs-cli/1.3.0/`.
- [ ] Throwaway venv install from TestPyPI:
      ```sh
      python3 -m venv /tmp/docs-test-venv
      /tmp/docs-test-venv/bin/pip install --index-url https://test.pypi.org/simple/ \
          --extra-index-url https://pypi.org/simple/ \
          docs-cli==1.3.0
      ```
      (The `--extra-index-url` lets pip resolve `docs-cli`'s
      well-formed dist-info even though we have no runtime deps;
      it also prevents a future-day surprise if a dep is added.)
- [ ] `/tmp/docs-test-venv/bin/docs --version` → `docs 1.3.0`.
- [ ] `/tmp/docs-test-venv/bin/docs install-skill --dest /tmp/docs-test-skill`
      → bundled tree appears byte-identical to `src/docs_cli/skill/`.
- [ ] `/tmp/docs-test-venv/bin/docs install-skill --dest /tmp/docs-test-skill --symlink`
      → exit 2 (wheel-install rejects symlink; the dest is left
      unchanged).
- [ ] `/tmp/docs-test-venv/bin/docs check tests/fixtures/trees/minimal/`
      → exit 0.
- [ ] `/tmp/docs-test-venv/bin/docs index --root docs/ --dry-run`
      → exit 0.

If anything fails: **stop**, fix the issue, bump to `1.3.1`
(TestPyPI also rejects re-uploads of the same version), and
rerun from "Artifact build". Do not proceed to real PyPI until
TestPyPI is clean.

## Real PyPI publish (operator runs after TestPyPI passes)

- [ ] Replace `## 1.3.0 — UNRELEASED` in `CHANGELOG.md` with
      `## 1.3.0 — <today's date>`; commit on `main`.
- [ ] Upload to PyPI:
      ```sh
      .venv/bin/twine upload dist/*
      ```
- [ ] Artifact visible at `https://pypi.org/project/docs-cli/1.3.0/`.
- [ ] Throwaway venv install from PyPI:
      ```sh
      python3 -m venv /tmp/docs-real-venv
      /tmp/docs-real-venv/bin/pip install docs-cli==1.3.0
      ```
- [ ] Re-run the smoke subset (`docs --version`, `docs install-skill --dest …`,
      `docs check tests/fixtures/trees/minimal/`) against the
      real artifact.

## Post-release (operator)

- [ ] Flip the GitHub repo to public:
      ```sh
      gh repo edit ArtRichards/docs-cli \
          --visibility public --accept-visibility-change-consequences
      ```
- [ ] Tag and push:
      ```sh
      git tag v1.3.0
      git push origin v1.3.0
      ```
- [ ] Create the GitHub release:
      ```sh
      gh release create v1.3.0 \
          --title "docs-cli 1.3.0" \
          --notes "$(awk '/^## 1.3.0 —/{flag=1; next} /^## /{flag=0} flag' CHANGELOG.md)"
      ```
      (Or hand-author the notes referencing the M6 / M7 / M8
      milestone-completion summaries.)
- [ ] **Re-scope the PyPI API token** to project `docs-cli` (now
      that the project exists). Account settings → API tokens →
      add a project-scoped token, swap it into `~/.pypirc`,
      revoke the original entire-account token. Same drill on
      TestPyPI.
- [ ] Doc closeouts:
      - `docs/status.md`: M6 / M7 / M8 / M9 rows →
        `Complete (DATE)`; "Current milestone" rewritten
        (next milestone, or "v1.1 shipped" if M9 is the last
        v1.1 entry); "Next action" rewritten.
      - `docs/plan.md`: M6 / M7 / M8 / M9 rows → shipped.
      - `docs/m9-pypi-publish.md`: Phase Checklist boxes ticked;
        milestone-completion summary appended (which `1.3.x`
        actually shipped, sha256 of published wheel + sdist,
        publish timestamp, any runbook deviations).
      - `docs/m9-pypi-publish-log.md`: per-phase entries
        appended with what actually happened.
      - `docs/m7-migration-accuracy.md` +
        `docs/m8-adoption-workflow.md`: equivalent Phase 10 /
        completion-summary updates (these milestones close on
        their own implementation; the publish flip is M9's
        responsibility).
      - `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
        regenerated in lockstep.
- [ ] Clean up scratch dirs:
      ```sh
      rm -rf /tmp/docs-*-venv /tmp/docs-*-skill /tmp/skill-smoke
      ```

## Notes

- A PyPI release is **append-only**. A bad artifact can be
  yanked but not deleted; the same applies to TestPyPI. The
  TestPyPI rehearsal is non-optional — name typos, missing
  package-data globs, bad classifier values, and README
  rendering errors caught there cost nothing; caught on PyPI
  they burn the version number.
- **Manual twine vs Trusted Publishing.** The 1.3.0 release
  ships via manual twine (continuing the M6 stance). For a
  future iteration, GitHub Actions Trusted Publishing (OIDC)
  would replace the API tokens entirely: configure the PyPI
  Trusted Publisher binding once, then a tag-triggered
  `.github/workflows/release.yml` exchanges a short-lived OIDC
  token for upload rights. Trade-off: no long-lived secret in
  the repo, at the cost of carrying a workflow file and
  depending on PyPI's OIDC provider behaviour. Track as a
  follow-up if the manual flow proves cumbersome at v1.4 / v2.
- **Throwaway venvs.** Every smoke step builds a fresh venv at
  `/tmp/docs-<purpose>-venv` so a previous failed install can't
  pollute the next attempt. Always clean up after success.
- **Version is hardcoded in two places** (`pyproject.toml` +
  `src/docs_cli/cli.py`'s `__version__`). Migrating to
  `importlib.metadata` for single-source-of-truth is parked as
  a future-iteration note (recorded in the M6 plan's "What's
  deliberately deferred" section).
