# Release Runbook

Lifecycle: active
Role: runbook
Project: docs
Updated: 2026-05-29

Related:
- pairs-with: m9-pypi-publish.md
- pairs-with: archive/2026-05-27/m11-pypi-publish.md
- pairs-with: m6-pypi-distribution.md
- pairs-with: m7-migration-accuracy.md
- pairs-with: m8-adoption-workflow.md
- pairs-with: status.md
- pairs-with: plan.md

The operator-driven checklist for shipping `docs-cli` to PyPI.
This runbook drove **M9 — `docs-cli==1.3.0`** (shipped
2026-05-25) and **M11 — `docs-cli==1.4.0`** (shipped
2026-05-27); it stays the operative reference for future
releases (v1.5+). Every "operator runs X" bullet below is the
walked-top-to-bottom procedure. The bullets are scoped tight
enough to copy-paste; the prose framing for each release lives
in its milestone doc
([m9-pypi-publish.md](m9-pypi-publish.md),
[archive/2026-05-27/m11-pypi-publish.md](archive/2026-05-27/m11-pypi-publish.md)).

**Before driving a new release, read the
[Cumulative lessons + deviations](#cumulative-lessons--deviations)
section at the bottom of this file.** It captures the
M9 + M11 walkthrough surprises (CHANGELOG amend timing, JSON
metadata cache lag, what-to-skip-after-first-publish) that
the body-of-runbook steps are too tactical to flag in passing.

**TestPyPI rehearsal name caveat (still applies as of
M11 publish 2026-05-27).** The bare project name `docs-cli`
was parked on TestPyPI by an unrelated project at M9 publish
time, and the squatter was still unchanged (`latest: 0.1.0`,
no author surface) at M11 re-check. The TestPyPI rehearsal
therefore runs under a disambiguated dist name
(`docs-cli-rehearsal`) — same wheel contents, same entry
point `docs`, same `docs_cli` package import, only
`[project] name` in `pyproject.toml` temporarily renamed for
the rehearsal build and reverted before the real PyPI build.
Every release re-checks TestPyPI's `docs-cli` ownership at
the operator-prep step (the original squatter may move on;
if so, drop the rehearsal-name detour).

**Publish-milestone cadence (M9 + M11 confirmed pattern).** Each
implementation milestone with code or version-bumping changes
lands its `pyproject.toml` / `__version__` / `CHANGELOG.md`
bump inline at its own Phase 7 (and dates the CHANGELOG entry
at its own Phase 10). The actual PyPI publish is then a
separate operator-driven milestone that re-runs this runbook
top to bottom — M9 published M6+M7+M8 as 1.3.0 (batched per
the M9 OQ-C split); M11 published M10 as 1.4.0 (one-to-one).
**Fresh artifacts are always built at the publish milestone's
start** — never reused from the implementation milestone's
local `dist/`. The Trusted-Publishing / OIDC path remains
parked as a future-iteration note at the bottom of this file.

## Operator one-time prep (do BEFORE the first publish)

Administrative and independent of code work. This block is
**one-time per host** — once `~/.pypirc` carries valid tokens
and both accounts have 2FA, future releases skip straight to
"Pre-publish prep" below. Re-verify at every release start
that the bootstrap state hasn't rotted (tokens revoked,
account locked, ownership changes); the
[per-release re-verification](#per-release-re-verification)
section below the body lists the actual probes.

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

## Pre-publish prep (publish-milestone start — operator runs)

Once the implementation milestone(s) being shipped are merged
to `main`, the operator drives this block from
`/home/user/opt/docs-cli/`. The impl agent finishing the
implementation milestone does **not** run this — that milestone
closes at its own Phase 10 commits and the publish is a
separate operator-driven milestone.

### Per-release re-verification

Cheap probes that catch token rot / ownership drift before
the network-mutating phases:

- [ ] `~/.pypirc` mode is 600 and carries `[pypi]` +
      `[testpypi]` sections with `username = __token__` and
      `password = pypi-…` token values. (Sanity-check token
      *prefixes* — never print values into logs.)
- [ ] PyPI registry HTTP status for `docs-cli`:
      `curl -sI https://pypi.org/simple/docs-cli/` → 200; JSON
      `releases` array does **not** contain the about-to-publish
      version. (M9 + M11 both verified the slot was free
      pre-upload; PyPI rejects re-uploads even after yank.)
- [ ] TestPyPI registry: `docs-cli-rehearsal` slot for the
      about-to-publish version is free; bare `docs-cli`
      TestPyPI ownership re-checked (squatter may have lapsed
      → drop the rehearsal-name detour; if unchanged → detour
      continues).
- [ ] PyPI + TestPyPI account login + 2FA — passive
      confirmation is fine; positive proof surfaces at the
      first `twine upload`.

### Version + CHANGELOG verification

The version + CHANGELOG bumps land at the implementation
milestone's Phase 7 (typically) + Phase 10 (date) commits. The
publish milestone's job at this block is **verification**:

- [ ] `pyproject.toml` `version` matches the about-to-publish
      version.
- [ ] `__version__` in `src/docs_cli/cli.py` matches.
- [ ] `tests/test_packaging.py` A3 assertion is pinned at the
      about-to-publish version.
- [ ] `CHANGELOG.md` `## <VERSION>` header dated correctly for
      publish day (one-line bump if implementation-milestone
      date and publish-milestone date differ).

**Lesson from M11 (2026-05-27):** the M10-authored CHANGELOG
entry carried a parenthetical suffix `(LOCAL; not on PyPI)`
that needed dropping at publish-milestone Phase 4 (before
fresh artefact rebuild + upload). For future releases:
either author the implementation-milestone CHANGELOG entry
with publish-survival wording (no "ready locally" / "deferred
to MX" phrasing) or plan for a Phase-4 CHANGELOG amend before
build. See
[Cumulative lessons + deviations](#cumulative-lessons--deviations)
for the full M11 deviation record.

**M9 worked example (historical reference):**
M6 + M7 + M8 batched into a single 1.3.0 entry per the OQ-C
split; `## 1.1.0 — UNRELEASED` got renamed to `## 1.3.0 — UNRELEASED`
at M8 Phase 7 (intermediate 1.1.0 / 1.2.0 never reached PyPI);
the breaking `Status:` → `Lifecycle:` rename (M7) and the
adoption workflow (M8) each got their own sub-block; date was
filled in at the moment of upload (Phase 4).

**M11 worked example:** straight 1.3.0 → 1.4.0 carrying just
M10's surface; CHANGELOG header dated at M10 Phase 10 with the
trailing `(LOCAL; not on PyPI)` marker that got stripped at
M11 Phase 4 before fresh build.

### Tree state

- [ ] `docs/status.md` reflects M6 / M7 / M8 / M9 in flight or
      shipped state; "Current milestone" + "Next action" point
      at this runbook.
- [ ] `docs/plan.md` v1.1 section reflects the same.
- [ ] `docs/INDEX.md` regenerated; `tests/fixtures/expected/docs-INDEX.md`
      lockstep-updated.

### Quality gate (tree-wide)

- [ ] `.venv/bin/python -m pytest tests/ -q` — full suite green.
      Baseline counts: M6 ship 271; M9 ship 369; M11 ship 401.
      Record the current count into the publish-milestone's
      impl log Phase 2 entry so reviewers can spot a
      missing-test regression.
- [ ] `.venv/bin/ruff check .` — clean.
- [ ] `.venv/bin/ruff format --check .` — clean.
- [ ] `.venv/bin/mypy` — clean.
- [ ] `docs check docs/` — exit 0.
- [ ] `docs index --root docs/ --dry-run` — exit 0 / idempotent.

### Artifact build

- [ ] Rebuild artifacts cleanly — never reuse the
      implementation milestone's local `dist/`. Different
      tree state, different bytes:
      ```sh
      rm -rf dist/
      .venv/bin/python -m build
      ```
      Expected output:
      `dist/docs_cli-<VERSION>-py3-none-any.whl` +
      `dist/docs_cli-<VERSION>.tar.gz`.
- [ ] **Capture the sha256 of both artefacts.** They are the
      chain-of-custody anchors for Phase 4's PyPI-served-vs-local
      verification: `sha256sum dist/*` into the impl log. The
      wheel sha256 will typically be byte-identical to a
      previous pre-publish build of the same `src/` (M11
      confirmed this — Phase 2 build sha matched Phase 4 build
      sha because only `docs/` evolved). The sdist captures
      `docs/` (and `tests/`) but **not** `CHANGELOG.md` (M13
      verified: `tar tzf dist/*.tar.gz | grep -c CHANGELOG` →
      0) — so within one publish milestone the Phase 2 and
      Phase 4 sdist shas are byte-identical when `docs/` is
      untouched between them, even though the CHANGELOG is
      dated in between (M13 confirmed). Across milestones the
      sdist sha moves because `docs/` evolves.
- [ ] `.venv/bin/pip install --quiet twine` (if not already
      present; `twine 6.2.0` was the version smoke-tested at M6
      ship and re-used unchanged through M11).
- [ ] `.venv/bin/twine check dist/*` — both artifacts PASS.

### Local-install smoke (no PyPI involvement)

```sh
python3 -m venv /tmp/docs-local-smoke
/tmp/docs-local-smoke/bin/pip install dist/docs_cli-<VERSION>-py3-none-any.whl
/tmp/docs-local-smoke/bin/docs --version          # → "docs <VERSION>"
/tmp/docs-local-smoke/bin/docs --help             # lists install-skill + every implementation-milestone verb addition
/tmp/docs-local-smoke/bin/docs install-skill --dest /tmp/skill-smoke
diff -ru src/docs_cli/skill /tmp/skill-smoke      # empty (byte-identical)
/tmp/docs-local-smoke/bin/docs install-skill --dest /tmp/skill-smoke   # exit 0 (no-op)
/tmp/docs-local-smoke/bin/docs install-skill --dest /tmp/skill-smoke --symlink   # exit 2
/tmp/docs-local-smoke/bin/docs check tests/fixtures/trees/minimal/    # exit 0
```

Each release adds a headline-contract probe against the local
wheel here. M11 added `docs migrate --apply --quiet
/tmp/<foreign-tree>` and asserted exit 0 / stdout 0 bytes /
stderr 0 bytes / `.docs.toml` auto-emitted — the M10 contract
under test. Future releases should add their own headline
probe in this same block before TestPyPI upload.

## TestPyPI rehearsal (operator runs)

**If the TestPyPI `docs-cli` ownership re-check (per-release
re-verification, above) showed the squatter unchanged:**
temporarily rename `pyproject.toml` `[project] name` to
`docs-cli-rehearsal`, rebuild `dist/`, then upload. Revert the
rename and rebuild *cleanly* before Phase 4 — the real PyPI
build must go out under `docs-cli`.

- [ ] Upload to TestPyPI:
      ```sh
      .venv/bin/twine upload --repository testpypi dist/*
      ```
- [ ] Artifact visible at
      `https://test.pypi.org/project/docs-cli-rehearsal/<VERSION>/`
      (or `…/docs-cli/<VERSION>/` if the squatter ever lapses
      and the rename-detour is dropped).
- [ ] Throwaway venv install from TestPyPI:
      ```sh
      python3 -m venv /tmp/docs-test-venv
      /tmp/docs-test-venv/bin/pip install --index-url https://test.pypi.org/simple/ \
          --extra-index-url https://pypi.org/simple/ \
          docs-cli-rehearsal==<VERSION>
      ```
      (The `--extra-index-url` lets pip resolve `docs-cli`'s
      well-formed dist-info even though we have no runtime deps;
      it also prevents a future-day surprise if a dep is added.)
- [ ] `/tmp/docs-test-venv/bin/docs --version` — **caveat
      (M13+):** under the rehearsal-name rename this prints
      `docs 0.0.0+local`, NOT `docs <VERSION>`, because
      `__version__` reads `importlib.metadata.version("docs-cli")`
      (M12 SoT) and the rehearsal installs as
      `docs-cli-rehearsal`, so the lookup misses and hits the
      `PackageNotFoundError` fallback. This is expected, not a
      failure. Verify the version-string contract against the
      canonical-name **local** wheel (pre-publish smoke) and
      the **PyPI** wheel (Phase 4) — never the rehearsal wheel.
- [ ] `/tmp/docs-test-venv/bin/docs install-skill --dest /tmp/docs-test-skill`
      → bundled tree appears byte-identical to `src/docs_cli/skill/`.
- [ ] `/tmp/docs-test-venv/bin/docs install-skill --dest /tmp/docs-test-skill --symlink`
      → exit 2 (wheel-install rejects symlink; the dest is left
      unchanged).
- [ ] `/tmp/docs-test-venv/bin/docs check tests/fixtures/trees/minimal/`
      → exit 0.
- [ ] `/tmp/docs-test-venv/bin/docs index --root docs/ --dry-run`
      → exit 0.
- [ ] Re-run the headline-contract probe from the local-install
      smoke block above, this time against the TestPyPI-served
      wheel.

**JSON metadata cache lag.** Immediately post-upload, the
TestPyPI JSON metadata API (`/pypi/<pkg>/json`) lags the simple
index by ~60-120s. `pip install` reads the simple index and
works first try; `curl … /json` may still show the
previous-version `releases` array for a minute or two. Don't
gate verification on JSON refresh — `pip install` is the
authoritative signal. (M9 + M11 both hit this.)

If anything fails: **stop**, fix the issue, bump to the next
patch version (TestPyPI also rejects re-uploads of the same
version), and rerun from "Artifact build". Do not proceed to
real PyPI until TestPyPI is clean.

**Revert the rename** before continuing to Phase 4:
`pyproject.toml` `[project] name = "docs-cli-rehearsal"` →
`name = "docs-cli"`. Confirm `git diff pyproject.toml` is
empty.

## Real PyPI publish (operator runs after TestPyPI passes)

- [ ] CHANGELOG state for publish day:
      - If the header still carries an `UNRELEASED` placeholder
        (M9 pattern): replace with `## <VERSION> — <today's date>`.
      - If the header carries a stale "ready locally" / "deferred
        to MX" suffix from the implementation milestone (M11
        pattern): drop the suffix.
      - Commit on `main` **before** the fresh rebuild below; this
        commit's CHANGELOG.md ships in the sdist.
- [ ] Fresh rebuild under canonical `[project] name = "docs-cli"`:
      ```sh
      rm -rf dist/
      .venv/bin/python -m build
      .venv/bin/twine check dist/*
      ```
      Capture sha256 of both artefacts — these are the
      chain-of-custody anchors compared back to the
      PyPI-served wheel below.
- [ ] Upload to PyPI:
      ```sh
      .venv/bin/twine upload dist/*
      ```
- [ ] Artifact visible at
      `https://pypi.org/project/docs-cli/<VERSION>/`.
      (JSON metadata cache lag applies here too; trust the
      simple index / `pip install`.)
- [ ] Throwaway venv install from PyPI:
      ```sh
      python3 -m venv /tmp/docs-real-venv
      /tmp/docs-real-venv/bin/pip install docs-cli==<VERSION>
      ```
- [ ] **Chain-of-custody check:** pull the PyPI-served wheel
      and sha256-compare against the local Phase 4 build:
      ```sh
      mkdir /tmp/docs-pypi-served
      /tmp/docs-real-venv/bin/pip download --no-deps \
          --dest /tmp/docs-pypi-served docs-cli==<VERSION>
      sha256sum /tmp/docs-pypi-served/*.whl dist/*.whl
      ```
      Both wheel sha256s **must** be byte-identical. (M11
      confirmed bit-perfect; any mismatch is an immediate
      stop-and-investigate signal.)
- [ ] Re-run the smoke subset (`docs --version`,
      `docs install-skill --dest …`,
      `docs check tests/fixtures/trees/minimal/`) and the
      headline-contract probe against the PyPI-served wheel.

## Post-release (operator)

- [ ] **Flip the GitHub repo to public** — *only on first
      publish*. The flip happened at M9 (2026-05-25); for v1.4+
      releases this step is N/A (repo already public).
      Reference command for the first-publish run:
      ```sh
      gh repo edit ArtRichards/docs-cli --visibility public
      ```
      `gh` prompts interactively to confirm the
      irreversible-ish visibility change.
      (`--accept-visibility-change-consequences` was not
      present in `gh` 2.x at M9 publish time 2026-05-25; the
      interactive confirmation is the documented path.)
- [ ] Merge the publish-milestone branch stack into `main`
      (typically fast-forward), push `main`:
      ```sh
      git checkout main
      git merge --ff-only <publish-milestone-branch>
      git push origin main
      ```
- [ ] Tag at the publish-milestone's Phase 4 commit (the one
      whose tree state matches what's in PyPI) and push:
      ```sh
      git tag -a v<VERSION> -m "docs-cli <VERSION> — <one-line summary>"
      git push origin v<VERSION>
      ```
      M9 used a lightweight tag; M11 used an annotated tag.
      Annotated is preferred for the message + author metadata;
      both are accepted.
- [ ] Create the GitHub release:
      ```sh
      gh release create v<VERSION> \
          --title "docs-cli <VERSION>" \
          --notes "$(awk '/^## <VERSION> —/{flag=1; next} /^## /{flag=0} flag' CHANGELOG.md)"
      ```
      If the CHANGELOG entry needed a post-publish accuracy
      amend (M11 pattern: stale "deferred to MX" wording), apply
      it as a separate `main` commit *and* push corrected notes
      to the GitHub release with
      `gh release edit v<VERSION> --notes "..."`. The
      PyPI-served sdist's CHANGELOG.md is immutable; the
      GitHub release notes are not — keep them aligned with the
      post-publish narrative.
- [ ] **Re-scope the PyPI API token** to project `docs-cli`.
      Account settings → API tokens → add a project-scoped
      token, swap it into `~/.pypirc`, revoke the original
      entire-account token. Same drill on TestPyPI. *Status as
      of M11 close: rolled forward from M9 — still
      entire-account scoped. Operator UI work, async; not a
      release blocker.*
- [ ] Doc closeouts:
      - `docs/status.md`: implementation milestone(s) + this
        publish milestone rows → `Complete (DATE)`; "Current
        milestone" rewritten ("docs-cli <VERSION> shipped" +
        next milestone, or unscoped); "Next action" rewritten.
      - `docs/plan.md`: rows finalised + Sequencing timeline
        grew the new line.
      - `docs/m<N>-pypi-publish.md`: Phase Checklist all
        ticked; Success Criteria all ticked with evidence;
        milestone-completion summary appended (sha256 of
        published wheel + sdist, publish timestamp,
        chain-of-custody result, every deviation).
      - `docs/m<N>-pypi-publish-impl.md`: per-phase entries
        appended; impl-log milestone-completion summary
        (longer than the milestone-doc one — full deviation
        prose).
      - Implementation milestone doc(s): equivalent Phase 10 /
        completion-summary updates if the publish flips state
        they record.
      - `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
        regenerated in lockstep.
- [ ] `docs archive docs/m<N>-pypi-publish.md --reason
      "Milestone M<N> complete; docs-cli==<VERSION> shipped to
      PyPI <DATE>"`. The impl log stays at root with
      `Lifecycle: active` per the M8 / M9 / M10 / M11 pattern.
      After archive, update referring `Related:` edges in
      `status.md` and the impl log to point at the
      `archive/<DATE>/` path (the archive verb doesn't rewrite
      referring edges; that's `docs mv` territory — see the
      [Cumulative lessons + deviations](#cumulative-lessons--deviations)
      enhancement candidate).
- [ ] Clean up scratch dirs:
      ```sh
      rm -rf /tmp/docs-*-venv /tmp/docs-*-skill /tmp/skill-smoke* /tmp/docs-pypi-served /tmp/<foreign-tree>
      ```

## Notes

- A PyPI release is **append-only**. A bad artifact can be
  yanked but not deleted; the same applies to TestPyPI. The
  TestPyPI rehearsal is non-optional — name typos, missing
  package-data globs, bad classifier values, and README
  rendering errors caught there cost nothing; caught on PyPI
  they burn the version number.
- **Manual twine vs Trusted Publishing.** The 1.3.0 + 1.4.0
  releases ship via manual twine (continuing the M6 stance).
  For a future iteration, GitHub Actions Trusted Publishing
  (OIDC) would replace the API tokens entirely: configure the
  PyPI Trusted Publisher binding once, then a tag-triggered
  `.github/workflows/release.yml` exchanges a short-lived OIDC
  token for upload rights. Trade-off: no long-lived secret in
  the repo, at the cost of carrying a workflow file and
  depending on PyPI's OIDC provider behaviour. Track as a
  follow-up if the manual flow proves cumbersome at v1.5+ / v2.
- **Throwaway venvs.** Every smoke step builds a fresh venv at
  `/tmp/docs-<purpose>-venv` so a previous failed install can't
  pollute the next attempt. Always clean up after success.
- **Version is hardcoded in two places** (`pyproject.toml` +
  `src/docs_cli/cli.py`'s `__version__`). Migrating to
  `importlib.metadata` for single-source-of-truth is parked as
  a future-iteration note (recorded in the M6 plan's "What's
  deliberately deferred" section).

## Cumulative lessons + deviations

Per-release surprises that the body-of-runbook steps are too
tactical to flag in passing. Append to this section at every
release closeout; do **not** rewrite past entries.

### From M9 (2026-05-25, `docs-cli==1.3.0`)

- **TestPyPI `docs-cli` was parked by a squatter.** Discovered
  at M9 publish time; M9 + M11 both ran the rehearsal under
  `docs-cli-rehearsal` with a temporary `pyproject.toml`
  rename. Real PyPI `docs-cli` was always clean.
- **Token re-scope deferred as async operator UI work.** M9
  bootstrap tokens are "Entire account" scoped because PyPI
  doesn't offer project-scoped tokens until the project exists.
  Re-scoping to project-`docs-cli` is operator UI work that
  hasn't blocked any release; rolls forward indefinitely.
- **First-publish repo-visibility flip.** Repo went public at
  M9. Subsequent releases skip — see Post-release section
  guidance.
- **`gh` 2.x has no `--accept-visibility-change-consequences`
  flag.** Older runbook drafts referenced it; the actual path
  is interactive confirmation.

### From M11 (2026-05-27, `docs-cli==1.4.0`)

- **JSON metadata cache lag at both registries.** Immediately
  post-`twine upload`, both TestPyPI's and PyPI's
  `/pypi/<pkg>/json` endpoints reported the *previous* version
  as `latest` and a `releases` array missing the freshly-uploaded
  version. The simple index that `pip install` uses was current
  on both. **Do not** gate post-upload verification on JSON
  refresh — `pip install` is the authoritative signal. Cache TTL
  observed at ~60–120 s.
- **CHANGELOG amend at publish-milestone Phase 4 + Phase 5.**
  The M10-authored 1.4.0 CHANGELOG entry carried a parenthetical
  `(LOCAL; not on PyPI)` header suffix + a body sentence "1.4.0
  is ready locally; the PyPI publish is deferred to M11." Both
  needed editing at publish time:
  - Phase 4 stripped the header suffix before fresh build (so
    the sdist that ships carries clean text).
  - Phase 5 (post-publish) amended the body sentence and
    pushed corrected text to the GitHub release with
    `gh release edit --notes …`. The sdist's CHANGELOG.md is
    immutable on PyPI; the GitHub release notes are mutable
    and were brought into alignment.
  - **Future-release prevention:** author the
    implementation-milestone CHANGELOG entry with
    publish-survival wording — describe what the version
    *contains*, not its publish state. Avoid `(LOCAL;
    not on PyPI)` markers and "deferred to MX" sentences.
- **TestPyPI squatter rolls forward.** Re-checked at M11
  Phase 1 — still `latest: 0.1.0`, no author. Detour stays
  active until ownership lapses.
- **Chain-of-custody proof via `pip download` + sha256sum.**
  M11 added this as an explicit Phase 4 step: pull the
  PyPI-served wheel back, sha256-compare to the local build.
  Bit-perfect match expected (`src/` is the only thing that
  ends up in the wheel, and `src/` is unchanged across a
  publish milestone). Bake this check into every future
  release.
- **`docs touch` on non-docs-root files is a footgun.** Calling
  `docs touch CHANGELOG.md` from the repo root (no `.docs.toml`
  above the file) inserted an unintended `Updated:` line into
  CHANGELOG.md and then crashed the post-touch INDEX refresh on
  `README.md: missing Lifecycle`. Caught and reverted at M11
  Phase 5. **Future-feature candidate:** `docs touch` should
  refuse gracefully when the target is outside a docs root, not
  modify the file. Logged as an M11 open follow-on.
- **`docs archive` does not rewrite referring `Related:`
  edges.** Archiving the milestone doc moved
  `docs/m11-pypi-publish.md` → `docs/archive/2026-05-27/`, but
  `status.md` + the impl log still pointed at the old path
  until manually fixed. **Future-feature candidate:** archive
  should call into the same machinery `docs mv` uses to rewrite
  referring `Related:` bullets atomically. Logged as an M11
  open follow-on.
- **Tokens validated by use.** Token validity probes correctly
  at the *first* `twine upload` (Phase 3 TestPyPI). M11 chose
  not to add an active pre-upload token probe — the false-alarm
  surface of "check tokens are valid" tooling isn't worth it
  when the upload itself is the cheapest definitive test.

### From M13 (2026-05-29, `docs-cli==1.5.0`)

- **The TestPyPI rehearsal can no longer verify `docs
  --version` after the M12 `importlib.metadata` SoT refactor.**
  `__version__` now reads
  `importlib.metadata.version("docs-cli")`; the rehearsal
  installs the distribution as `docs-cli-rehearsal`, so the
  lookup raises `PackageNotFoundError` and falls back to the
  documented `0.0.0+local`. The rehearsal wheel therefore
  prints `docs 0.0.0+local`, not the real version. This is
  **expected**, not a regression — M9/M11 never hit it because
  `__version__` was a hardcoded literal back then. The
  version-string contract is verified against the
  canonical-name local wheel and the PyPI wheel instead (both
  print the real version). Caveat folded into the TestPyPI
  block's `docs --version` step above.
- **`CHANGELOG.md` is not shipped in the sdist.** The hatchling
  sdist carries `src/`, `docs/`, `tests/`, `README.md`,
  `LICENSE`, `pyproject.toml` — verified `tar tzf dist/*.tar.gz
  | grep -c CHANGELOG` → 0. Earlier runbook wording ("the sdist
  captures docs/ + CHANGELOG.md") was wrong on the CHANGELOG
  part; corrected in the Artifact-build section. Consequence:
  the "commit the dated CHANGELOG before the fresh rebuild so it
  ships in the sdist" instinct is moot — the dated CHANGELOG
  reaches users via the git repo and the GitHub release notes,
  not the PyPI sdist. (Still commit it before the build so the
  tag points at a tree with the dated CHANGELOG.)
- **Chain-of-custody bit-perfect again.** PyPI-served wheel
  sha256 byte-identical to the local Phase 4 build — third
  release running (M11 + M13 confirmed; the `pip download` +
  `sha256sum` check stays in the runbook).
- **Squatter still parked.** TestPyPI bare `docs-cli` re-checked
  at M13 Phase 1 — unchanged (`latest: 0.1.0`, author None).
  The `docs-cli-rehearsal` detour continues.
- **Fully-autonomous publish.** M13 was driven by
  `/ship-milestone M13` end-to-end (operator authorized the
  irreversible PyPI upload + `main` push up front). The
  conductor walked this runbook directly rather than the
  10-phase TDD step stack, since a publish milestone has no
  code phases. The runbook's internal hard gates (twine check,
  clean rehearsal, bit-perfect chain-of-custody) remained the
  go/no-go conditions.
