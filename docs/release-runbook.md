# Release Runbook

Lifecycle: active
Role: runbook
Project: docs
Updated: 2026-10-29

Related:
- pairs-with: archive/2026-05-25/m9-pypi-publish.md
- pairs-with: archive/2026-05-27/m11-pypi-publish.md
- pairs-with: archive/2026-05-24/m6-pypi-distribution.md
- pairs-with: archive/2026-05-25/m7-migration-accuracy.md
- pairs-with: archive/2026-05-25/m8-adoption-workflow.md
- pairs-with: status.md
- pairs-with: milestone-plan.md

The operator-driven checklist for shipping `docs-cli` to PyPI.
This runbook drove **M9 — `docs-cli==1.3.0`** (shipped
2026-05-25), **M11 — `docs-cli==1.4.0`** (shipped 2026-05-27),
and **M13 — `docs-cli==1.5.0`** (shipped 2026-05-29); it stays
the operative reference for future releases (v1.6+). Every
"operator runs X" bullet below is the walked-top-to-bottom
procedure. The bullets are scoped tight enough to copy-paste;
the prose framing for each release lives in its milestone doc
([archive/2026-05-25/m9-pypi-publish.md](archive/2026-05-25/m9-pypi-publish.md),
[archive/2026-05-27/m11-pypi-publish.md](archive/2026-05-27/m11-pypi-publish.md),
[archive/2026-05-29/m13-pypi-publish.md](archive/2026-05-29/m13-pypi-publish.md)).

**Before driving a new release, read the
[Cumulative lessons + deviations](#cumulative-lessons--deviations)
section at the bottom of this file.** It captures the
M9 + M11 + M13 walkthrough surprises (CHANGELOG amend timing,
JSON metadata cache lag, what-to-skip-after-first-publish, and
the M13 findings — the rehearsal-wheel `0.0.0+local` artifact
under the rename detour and `CHANGELOG.md` not shipping inside
the sdist) that the body-of-runbook steps are too tactical to
flag in passing.

**TestPyPI rehearsal name caveat (still applies as of
M13 publish 2026-05-29).** The bare project name `docs-cli`
was parked on TestPyPI by an unrelated project at M9 publish
time, and the squatter was still unchanged (`latest: 0.1.0`,
no author surface) at the M11 and M13 re-checks. The TestPyPI rehearsal
therefore runs under a disambiguated dist name
(`docs-cli-rehearsal`) — same wheel contents, same entry
point `docs`, same `docs_cli` package import, only
`[project] name` in `pyproject.toml` temporarily renamed for
the rehearsal build and reverted before the real PyPI build.
Every release re-checks TestPyPI's `docs-cli` ownership at
the operator-prep step (the original squatter may move on;
if so, drop the rehearsal-name detour).

**Publish-milestone cadence (M9 + M11 + M13 confirmed pattern).**
Each implementation milestone with code or version-bumping
changes lands its `pyproject.toml` / `__version__` /
`CHANGELOG.md` bump inline at its own Phase 7 (and dates the
CHANGELOG entry at its own Phase 10). The actual PyPI publish
is then a separate operator-driven milestone that re-runs this
runbook top to bottom — M9 published M6+M7+M8 as 1.3.0 (batched
per the M9 OQ-C split); M11 published M10 as 1.4.0 (one-to-one);
M13 published M12 as 1.5.0 (one-to-one).
**Fresh artifacts are always built at the publish milestone's
start** — never reused from the implementation milestone's
local `dist/`. The Trusted-Publishing / OIDC path remains
parked as a future-iteration note at the bottom of this file.

**Since M31 (2.1.0) a publish can run through `/ship-milestone`.**
Step 1 (Phases 1–4) runs everything before the upload — the release
checks, build (a), the TestPyPI rehearsal — and both reviewers judge the
frozen irreversible commands before they run; Step 2 uploads, verifies
the served bytes, tags, releases and refreshes the host. The milestone's
task plan freezes the exact command lines; this runbook keeps the
procedure and the standing checks. The [M31 task
plan](pypi-publish-2-1-0.md)'s *Decisions (Phase 1 — BINDING)* (P1.1–P1.6)
and *Error cases* are the worked reference for every command named below.

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
      `password = pypi-…` token values. Check the **shape
      only**, with a command that prints fixed text and
      booleans and fails closed on any read, parse or field
      error: a parser's error message quotes the offending
      line, which may hold a token (M31; the command is P1.5's
      shape command). Never print a value into a log.
- [ ] The release toolchain: the installed `twine` is PyPI's
      newest and at least 7.0.0 (a read-only check; see
      *Artifact build*); record `build`, `pip` and Python.
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

### Isolation and hygiene (every step)

Every smoke, probe, rehearsal install and download runs in a
throwaway venv and throwaway trees under one session scratch
directory `$S`, never the repository or `/tmp` at large, with
this environment sourced first (M31):

```sh
export XDG_STATE_HOME=$S/xdg/state XDG_CACHE_HOME=$S/xdg/cache
export DOCS_CLI_NO_UPDATE_CHECK=1 PYTHONDONTWRITEBYTECODE=1 PIP_CONFIG_FILE=/dev/null
unset PIP_INDEX_URL PIP_EXTRA_INDEX_URL TWINE_REPOSITORY TWINE_REPOSITORY_URL TWINE_USERNAME TWINE_PASSWORD
unset SOURCE_DATE_EPOCH   # it moves hatchling's fixed mtimes, and with them every sha
```

- `docs install-skill` records its destination on every
  success, the no-op included, so an unisolated smoke
  overwrites the host's recorded destination (M29, M31).
  Only the post-release host step writes host state.
- **Host check**, before and after every block that runs a
  `docs` executable: the recorded destination
  (`~/.local/state/docs-cli/install-skill.json`) is as the
  last authorized step left it, and the update cache's sha
  (`~/.cache/docs-cli/update-check.json`) is unchanged across
  the block. Compare pairwise, not with a morning baseline:
  the cache's 24-hour throttle lets any ordinary `docs` run
  rewrite it (M31).
- **Index installs name exactly one index** and pass
  `--no-deps`. Downloads land in fresh empty directories, and
  nothing runs from inside them.
- **Before every commit**, search the staged diff for
  token-shaped strings without printing them: git's own
  pickaxe, `git diff --cached --text --name-only -G"$TOKEN_RE"`,
  names the files only, and a failing search stops the commit
  like a match. Never pipe a diff into `grep -q` — it exits at
  the first match, the producer dies of SIGPIPE, and under
  `pipefail` the pipeline reads as "no match" (M31; the gate is
  P1.4's).

### Version + CHANGELOG verification

The version + CHANGELOG bumps land at the implementation
milestone's Phase 7 (typically) + Phase 10 (date) commits. The
publish milestone's job at this block is **verification**:

- [ ] `pyproject.toml` `version` matches the about-to-publish
      version.
- [ ] **After bumping, re-run `.venv/bin/pip install -e ".[dev]"`
      before the gate.** `__version__` resolves through
      `importlib.metadata`, which reads the *installed*
      dist-info, not `pyproject.toml` — so an un-refreshed
      editable install fails `test_version_matches_pyproject`
      with the old version on the left. M29 hit this; the test
      is doing its job, the install is stale.
- [ ] The editable install's `docs --version` prints the
      version (`__version__` reads `importlib.metadata` since
      M12; there is no second literal to bump).
- [ ] `tests/test_packaging.py` A3 assertion is pinned at the
      about-to-publish version.
- [ ] `CHANGELOG.md` `## <VERSION>` header dated with the local
      date of the upload. Date it at prep; if the day rolls
      before the tag-target build, re-date it in a one-line
      commit, and re-check `date +%F` against the heading
      immediately before the upload (M31).
- [ ] `tests/manual/release_readiness.py` passes — it checks
      the version, the dated CHANGELOG section against its
      reviewed text, the README (every verb, every synopsis's
      arity and flags against `--help`, no "Claude Code", every
      GitHub link on `main`) and the reference byte identity:
      ```sh
      .venv/bin/python tests/manual/release_readiness.py --docs .venv/bin/docs \
          --version <VERSION> --release-date <D> --changelog-base <implementation merge> \
          --drop-sentence "<publish-state sentence, if any>"
      ```

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

### Surface parity (help + bundled skill)

The CLI `--help` strings and the bundled skill must describe the
*actual* shipping behavior — including behavior a milestone
*replaced*, not just behavior it added. Replaced-behavior drift is
the easy miss (the `docs new --body-from` "first 20 lines" help
shipped stale in 1.6.0; see the M17 entry in
[Cumulative lessons + deviations](#cumulative-lessons--deviations)).

- [ ] For every verb/flag the shipping milestone(s) added or
      changed, `docs <verb> --help` matches the actual behavior —
      reconcile against the `## <VERSION>` CHANGELOG surface for
      this release.
- [ ] `docs --help` lists every new top-level verb; the relevant
      subcommand `--help` lists every new flag.
- [ ] The bundled skill `src/docs_cli/skill/` (SKILL.md +
      `references/`) documents the new surface, and
      `references/cli.md` is byte-identical to `docs/cli.md`
      (`diff -q src/docs_cli/skill/references/cli.md docs/cli.md`).
- [ ] `grep` the help strings + bundled skill for stale wording of
      any behavior a milestone *replaced* (not just added) —
      replaced-behavior drift is the easy miss.

### Tree state

- [ ] The publish milestone's row in
      [`milestone-plan.md`](milestone-plan.md), the canonical
      tracker, is `active`; `docs/status.md`'s narrative
      describes the release and links the tracker without
      restating its rows.
- [ ] `docs/INDEX.md` regenerated; `tests/fixtures/expected/docs-INDEX.md`
      lockstep-updated.

### Quality gate (tree-wide)

- [ ] `.venv/bin/python -m pytest -q` — full suite green.
      Record the passed and collected counts in the publish
      milestone's log so reviewers can spot a missing-test
      regression.
- [ ] `.venv/bin/ruff check .` — clean.
- [ ] `.venv/bin/ruff format --check .` — clean.
- [ ] `.venv/bin/mypy src/ tests/` — clean.
- [ ] From `docs/`: `docs check .` — exit 0.
- [ ] From `docs/`: `docs index . --dry-run` reproduces
      `INDEX.md` apart from the `_Generated YYYY-MM-DD.` stamp,
      which is today's date. Compare with that stamp normalised,
      as `tests/test_cli_index.py` does: a byte-exact compare
      fails on any day after the tree was indexed (M31).

### Artifact build

- [ ] Rebuild artifacts cleanly on a clean tree — never reuse
      the implementation milestone's local `dist/`. Different
      tree state, different bytes. **Every build starts from an
      empty `dist/`**, so a leftover rehearsal artifact can never
      reach an upload:
      ```sh
      rm -rf dist/
      .venv/bin/python -m build
      ls -A dist/       # exactly the two files below
      ```
      Expected output:
      `dist/docs_cli-<VERSION>-py3-none-any.whl` +
      `dist/docs_cli-<VERSION>.tar.gz`.
- [ ] **Record the build backend.** The `Generator:` line of
      the wheel's `WHEEL` file, and the environment the
      isolated build resolved (`python -m build -v` prints it:
      hatchling and each of its dependencies). `[build-system]`
      leaves hatchling unpinned, so a backend released between
      two builds of one release can move the wheel's bytes (M31
      built the day hatchling 1.33.0 shipped). The one remedy
      for a later build whose wheel differs: rebuild with
      `--dependency-constraints-txt <file>` pinning that whole
      recorded environment, `name==version` per line — it counts
      only if it reproduces the first wheel's sha.
- [ ] **Capture the sha256 of both artefacts.** They are the
      chain-of-custody anchors for the PyPI-served-vs-local
      verification: `sha256sum` of both files, named explicitly,
      into the impl log, and the sdist's per-member sha256
      manifest for every member outside `docs/` and `tests/`
      (`tar -xzf` into scratch, then `find … | LC_ALL=C sort -z |
      xargs -0 sha256sum`) — a later build's sdist must match it
      there even though `docs/` moves it. The
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
- [ ] **The installed twine is PyPI's newest and at least
      7.0.0** — a read-only check, before the first build. If it
      fails, upgrade then (`.venv/bin/pip install --upgrade
      'twine>=7.0.0'`), never between two builds of one release:
      an upgrade is a toolchain change (M31). Presence alone is
      not enough. M29 (2026-08-16) lost a gate to exactly that:
      `twine 6.2.0` monkeypatches
      `packaging.metadata._VALID_METADATA_VERSIONS` to stop at
      `2.4`, so it rejects the `Metadata-Version: 2.5` artifacts
      an unpinned `hatchling` now builds — while `packaging`
      itself accepts 2.5, PyPI accepts 2.5, and `twine 7.0.0`
      passes. The floor also lives in `pyproject.toml`'s `[dev]`
      extra, so `pip install -e ".[dev]"` carries it.
- [ ] `.venv/bin/twine check dist/docs_cli-<VERSION>-py3-none-any.whl
      dist/docs_cli-<VERSION>.tar.gz` — both artifacts PASS.
- [ ] **The dependency oracle** (wheel `METADATA`): every
      `Requires-Dist` carries an `extra ==` marker, with
      `Provides-Extra: dev` and `Requires-Python: >=3.11`, as
      the served 2.0.0 metadata does; `CHANGELOG` is in neither
      artifact; the wheel's `docs_cli/skill/` equals
      `src/docs_cli/skill` (seven files).

### Local-install smoke (no PyPI involvement)

The standing probe is `tests/manual/release_probe.py` (M31). It
runs one `docs` executable black-box on throwaway trees, with
`HOME` and XDG redirected and the update check off, in two
groups: **contract** (any executable — the release's headline
contracts, downstream CI capability probes, and earlier
releases' contracts as regression) and **distribution** (wheel
installs only — `docs --version`, `install-skill` byte identity,
its no-op re-run, the wheel-only `--symlink` refusal). The same
probe runs on every wheel a release builds, rehearses or ships:

```sh
python3 -m venv "$S/venv-a"
"$S/venv-a/bin/pip" install --no-deps --no-index dist/docs_cli-<VERSION>-py3-none-any.whl
python3 -I -m zipfile -e dist/docs_cli-<VERSION>-py3-none-any.whl "$S/x/a-wheel"
diff -r -x __pycache__ "$S/x/a-wheel/docs_cli" "$S"/venv-a/lib/python3.*/site-packages/docs_cli   # empty
.venv/bin/python tests/manual/release_probe.py --docs "$S/venv-a/bin/docs" \
    --group all --expect-version <VERSION> --repo . --scratch "$S/probe"     # every check PASS
```

Each release adds its own headline contracts to the probe's
contract group before the TestPyPI upload, with expected values
quoted from `cli.md`, the CHANGELOG and the product tests —
never from a build's output. A run against the previous
release's wheel is the control: it must fail exactly the new
checks. M11's `docs migrate --apply --quiet` probe and M29's nine
2.0 contracts are the precedents.

## TestPyPI rehearsal (operator runs)

**If the TestPyPI `docs-cli` ownership re-check (per-release
re-verification, above) showed the squatter unchanged:**
temporarily rename `pyproject.toml` `[project] name` to
`docs-cli-rehearsal`, rebuild `dist/`, then upload. Revert the
rename and rebuild *cleanly* before Phase 4 — the real PyPI
build must go out under `docs-cli`.

- [ ] Upload to TestPyPI, once the rehearsal version's
      per-version JSON returns 404 and `ls -A dist/` shows
      exactly the two rehearsal files:
      ```sh
      .venv/bin/twine upload --repository testpypi --non-interactive \
          dist/docs_cli_rehearsal-<VERSION>-py3-none-any.whl dist/docs_cli_rehearsal-<VERSION>.tar.gz
      ```
- [ ] Artifact visible at
      `https://test.pypi.org/project/docs-cli-rehearsal/<VERSION>/`
      (or `…/docs-cli/<VERSION>/` if the squatter ever lapses
      and the rename-detour is dropped).
- [ ] **The served bytes, before anything runs** (M31): poll the
      per-version JSON (at most 10 × 30 s) until it lists both
      files; `curl -sSf -o` each listed `url` into a fresh empty
      directory; each sha equals the local rehearsal build and
      the JSON digest; the served wheel's `docs_cli/` equals the
      canonical wheel's byte for byte, and every other entry sits
      under the rehearsal dist-info.
- [ ] Throwaway venv install from TestPyPI **alone**, then the
      payload diff before running it:
      ```sh
      python3 -m venv "$S/venv-rehearsal"
      "$S/venv-rehearsal/bin/pip" install --no-cache-dir --no-deps \
          --index-url https://test.pypi.org/simple/ docs-cli-rehearsal==<VERSION>
      diff -r -x __pycache__ "$S/x/a-wheel/docs_cli" "$S"/venv-rehearsal/lib/python3.*/site-packages/docs_cli
      ```
      Never add `--extra-index-url https://pypi.org/simple/`:
      `docs-cli-rehearsal` is unclaimed on real PyPI, so anyone
      who claims it would run on this token-bearing host. The
      wheel has no runtime dependency to resolve (M31).
- [ ] `docs --version` — **caveat
      (M13+):** under the rehearsal-name rename this prints
      `docs 0.0.0+local`, NOT `docs <VERSION>`, because
      `__version__` reads `importlib.metadata.version("docs-cli")`
      (M12 SoT) and the rehearsal installs as
      `docs-cli-rehearsal`, so the lookup misses and hits the
      `PackageNotFoundError` fallback. This is expected, not a
      failure. Verify the version-string contract against the
      canonical-name **local** wheel (pre-publish smoke) and
      the **PyPI** wheel — never the rehearsal wheel.
- [ ] The standing probe against the TestPyPI-served install,
      `release_probe.py --docs "$S/venv-rehearsal/bin/docs" --group
      all --no-version-check …`: its result lines equal the local
      wheel's, except the version check, which is skipped.

**JSON metadata cache lag.** Immediately post-upload, the
TestPyPI JSON metadata API (`/pypi/<pkg>/json`) lags the simple
index by ~60-120s. `pip install` reads the simple index and
works first try; `curl … /json` may still show the
previous-version `releases` array for a minute or two. Don't
gate verification on JSON refresh — `pip install` is the
authoritative signal. (M9 + M11 both hit this.)

**A rehearsal failure is a stop, not a re-run** (M31). The old
remedy — fix, bump the patch version, rerun — changes what the
publish ships. The re-run rules instead:
- **A release-input change** after the rehearsal (`src/`,
  `pyproject.toml`, `README.md`, `LICENSE`, `.gitignore`)
  invalidates the build, smoke, probe and rehearsal; re-run all
  four, re-rehearsing under the rehearsal name as
  `<VERSION>.post1`, `.post2`, … (TestPyPI refuses a reused
  version). The `.postN` lives only in the temporary rehearsal
  edit; the canonical version never changes.
- **A release-check script change** re-runs that script against
  the canonical wheel and a fresh install of the already-served
  rehearsal, recording its new git blob sha.
- **A documents-only change** invalidates nothing.

Do not proceed to real PyPI until TestPyPI is clean.

**Revert the rename** before continuing: `pyproject.toml`
`[project] name = "docs-cli-rehearsal"` → `name = "docs-cli"`.
Confirm `git diff --exit-code pyproject.toml` and an empty
`git status --porcelain`, then rebuild from an empty `dist/`: the
canonical wheel's sha must equal the first build's.

## Real PyPI publish (operator runs after TestPyPI passes)

- [ ] CHANGELOG state for publish day:
      - If the header still carries an `UNRELEASED` placeholder
        (M9 pattern): replace with `## <VERSION> — <today's date>`.
      - If the header carries a stale "ready locally" / "deferred
        to MX" suffix from the implementation milestone (M11
        pattern): drop the suffix.
      - Commit on the publish branch **before** the fresh
        rebuild below; this commit's tree is what ships in the
        sdist, and it is the **tag target**.
- [ ] Pre-upload gate, at the clean tag-target commit: the
      per-version JSON (`https://pypi.org/pypi/docs-cli/<VERSION>/json`)
      returns 404; the release inputs are unchanged since the
      rehearsed build (`git diff --quiet <build commit>..HEAD --
      src pyproject.toml README.md LICENSE .gitignore`);
      readiness passes with today's date; the full suite passes;
      `git ls-remote origin refs/heads/main` and `gh auth status`
      exit 0; the `~/.pypirc` shape is unchanged.
- [ ] Fresh rebuild under canonical `[project] name = "docs-cli"`:
      ```sh
      rm -rf dist/
      .venv/bin/python -m build
      ls -A dist/
      .venv/bin/twine check dist/docs_cli-<VERSION>-py3-none-any.whl dist/docs_cli-<VERSION>.tar.gz
      ```
      Its wheel sha must equal the rehearsed canonical build's
      (else the backend-pin remedy in *Artifact build*), and its
      sdist manifest outside `docs/` and `tests/` must equal the
      recorded one. Record both shas before uploading — they
      are the chain-of-custody anchors.
- [ ] Upload to PyPI, immediately after re-checking `date +%F`
      against the CHANGELOG heading, the 404, `ls -A dist/` and
      both shas:
      ```sh
      env -u TWINE_REPOSITORY -u TWINE_REPOSITORY_URL -u TWINE_USERNAME -u TWINE_PASSWORD \
          .venv/bin/twine upload --repository pypi --non-interactive \
          dist/docs_cli-<VERSION>-py3-none-any.whl dist/docs_cli-<VERSION>.tar.gz
      ```
      Never a glob, never `--skip-existing`. **The outcome
      precedence** (M31): poll the per-version JSON (at most
      10 × 30 s) and record exactly which files PyPI publishes;
      then any 4xx stops; one file confirmed and the other
      failed transiently gets one by-name re-send of the missing
      file; anything else stops for the operator. A published
      file is never re-sent.
- [ ] Artifact visible at
      `https://pypi.org/project/docs-cli/<VERSION>/`; the
      per-version JSON's two digests equal the local shas.
      (JSON metadata cache lag applies here too; the
      per-version endpoint and the simple index are
      authoritative.)
- [ ] **Chain-of-custody check**, before anything served runs:
      `curl -sSf -o` each per-version JSON `url` into a fresh
      empty directory; both shas equal the local build and the
      JSON digests. Do not use `pip download --no-binary
      :all:` for the sdist: it runs the build backend on
      downloaded code on a host holding tokens (M31). Every wheel
      sha so far has been bit-perfect (M11 onward); any mismatch
      is an immediate stop.
- [ ] Throwaway venv install from PyPI alone, after polling the
      PEP 691 simple JSON (`https://pypi.org/simple/docs-cli/`,
      at most 10 × 30 s) until both files are listed with the
      local shas:
      ```sh
      python3 -m venv "$S/venv-served"
      "$S/venv-served/bin/pip" install --no-cache-dir --no-deps \
          --index-url https://pypi.org/simple/ docs-cli==<VERSION>
      diff -r -x __pycache__ <extracted local wheel>/docs_cli \
          "$S"/venv-served/lib/python3.*/site-packages/docs_cli   # empty
      ```
- [ ] The standing probe against the served install, run from a
      worktree at the tag target so its fixtures, docs copy and
      skill reference are the tag target's bytes:
      ```sh
      git worktree add --detach "$S/tag-tree" <tag-target>
      .venv/bin/python "$S/tag-tree/tests/manual/release_probe.py" --docs "$S/venv-served/bin/docs" \
          --group all --expect-version <VERSION> --repo "$S/tag-tree" --scratch "$S/probe"
      git worktree remove "$S/tag-tree"
      ```
      Every result line equals the local wheel's. If a
      downstream consumer's CI probes this release's
      capabilities (M31: the Agent Playbook Suite's guard step),
      extract that step verbatim and run it against the served
      install from an empty directory too.

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
- [ ] **Tag the tag-target commit** — the commit the uploaded
      build came from — only after the served bytes pass the
      chain-of-custody check and the standing probe. Annotated,
      then check the **peeled** remote ref: the plain tag ref
      returns the tag object, not the commit (M31; `v2.0.0` is
      tag object `af3bdb5`, commit `408ef6c`):
      ```sh
      git tag -a v<VERSION> -m "docs-cli <VERSION> — <one-line summary>" <tag-target>
      git push origin v<VERSION>                      # this tag only; never --tags
      git ls-remote origin 'refs/tags/v<VERSION>^{}'  # = <tag-target>
      ```
- [ ] Create the GitHub release from the tag-target's CHANGELOG
      section (non-empty):
      ```sh
      gh release create v<VERSION> --verify-tag --title "docs-cli <VERSION>" \
          --notes "$(git show <tag-target>:CHANGELOG.md | awk '/^## <VERSION> —/{flag=1; next} /^## /{flag=0} flag')"
      gh release view v<VERSION>
      ```
      If the CHANGELOG entry needed a post-publish accuracy
      amend (M11 pattern: stale "deferred to MX" wording), apply
      it as a separate `main` commit *and* push corrected notes
      to the GitHub release with
      `gh release edit v<VERSION> --notes "..."`. The
      PyPI-served sdist's CHANGELOG.md is immutable; the
      GitHub release notes are not — keep them aligned with the
      post-publish narrative.
- [ ] **Merge the publish stack into `main`** at the operator's
      direction, outside the milestone, as a history-preserving
      **merge commit** — never squash or rebase, which would
      leave the tagged commit off `main` — and promptly: the PyPI
      page's README links `blob/main/CHANGELOG.md`, which reads
      the pre-publish heading until the stack lands (M31).
- [ ] **Host step** (`CLAUDE.md`: host skills move only at a
      production ship), in this order, each verified before the
      next (M29 left the binary behind the skill; M31 closed the
      gap):
      1. **The update notice.** Once the aggregate JSON
         (`https://pypi.org/pypi/docs-cli/json`) reports
         `<VERSION>`, run the previous release's binary on a
         command that reaches dispatch — `docs check .` in a
         scratch tree with an empty `.docs.toml`, not `--version`
         or `-h` — with a scratch `XDG_CACHE_HOME` and the kill
         switches (`DOCS_CLI_NO_UPDATE_CHECK`, `CI`,
         `DO_NOT_TRACK`) unset. Expect one
         `docs: update available <old> -> <VERSION> — run: pip
         install -U docs-cli` line on stderr and an unchanged exit
         code. Its fetch has a 1 s timeout: retry with a fresh
         cache.
      2. **The binary.** After the simple-index poll, `pipx
         upgrade docs-cli`; `~/.local/bin/docs --version` prints
         `docs <VERSION>`, and the pipx venv's `docs_cli/` equals
         the served wheel's. Expect "upgrading shared libraries…":
         pipx's `upgrade` always runs a pip upgrade in its shared
         libraries and touches `shared/bin/pip` (M31).
      3. **The skill**, at the destination the operator names
         (never guessed), with the published binary and the
         host's real XDG state so the destination is recorded:
         `env -u XDG_STATE_HOME -u XDG_CACHE_HOME
         DOCS_CLI_NO_UPDATE_CHECK=1 ~/.local/bin/docs install-skill
         --force --dest <dest>`; then `diff -r` against the served
         wheel's `docs_cli/skill/` is empty and
         `~/.local/state/docs-cli/install-skill.json` names it.
      4. **The sweep.** A read-only census of the workflow skills'
         docs-cli prescriptions the release supersedes, in the
         installed plugin and its source repository. Freeze the
         patterns first, and require them to hit the known sites.
         The findings go to the feedback-log hand-off; the suite
         rides its own release cycle.
- [ ] **Re-scope the PyPI API token** to project `docs-cli`.
      Account settings → API tokens → add a project-scoped
      token, swap it into `~/.pypirc`, revoke the original
      entire-account token. Same drill on TestPyPI. *Status as
      of M11 close: rolled forward from M9 — still
      entire-account scoped. Operator UI work, async; not a
      release blocker.*
- [ ] Doc closeouts:
      - The publish milestone's trio: phase checklist and
        success criteria ticked with evidence; completion
        summaries (the published shas, the upload time, the
        chain-of-custody result, every deviation).
      - `docs/status.md`: a narrative paragraph; the tracker row
        moves to `complete` in `docs/milestone-plan.md` at
        closeout.
      - `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
        regenerated in lockstep.
      - Anything that must outlive the archive lives in a live
        document: the hand-off in `feedback-log.md`, the
        narrative in `status.md`, the procedure here.
- [ ] **Archive the trio together**:
      `docs archive <stem>.md --cascade-only '<stem>-*'`, after a
      `--cascade-dry-run` preview that selects exactly the two
      companions. The impl log no longer stays at root: the
      2026-10-26 migration archived M17's, M20's, M24's and M29's.
      **Referring edges and body links are rebased by the
      archive verb itself** as of M18 (`Related:`) and M28
      (Markdown body links); verify with `docs check`.
- [ ] **Archiving more than the primary needs an explicit
      scope.** Bare `--cascade` is retired as of 2.0 and refuses
      at exit 2 writing nothing. Check the agent playbooks before
      a closeout: skills written against 1.x still prescribe the
      retired flag.
- [ ] Clean up: `rm -rf "$S"`, `git worktree prune`, `rm -rf dist/`.

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
- **Throwaway venvs.** Every smoke step builds a fresh venv
  under the session scratch `$S` (*Isolation and hygiene*) so a
  previous failed install can't pollute the next attempt. Always
  clean up after success.

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

### From M17 (2026-06-03, `docs-cli==1.6.0`)

- **Fully-autonomous publish shipped M14 + M15 as 1.6.0.** M17
  was driven end-to-end as a fully-autonomous pass walking this
  runbook directly (no 10-phase TDD stack — a publish milestone
  has no code phases); the operator authorized the irreversible
  PyPI upload + `main` push + `v1.6.0` tag + GitHub release up
  front. It batched M14 + M15 into one public release (as M9
  batched M6+M7+M8); M18's already-merged archive-edge fix rode
  along in the same tree. Chain-of-custody bit-perfect — fourth
  release running (M11 + M13 + M17): the PyPI-served wheel sha256
  (`b0822709…`) is byte-identical to the local Phase-4 build.
- **Help-drift finding → surface-parity gate.** The post-publish
  dogfood found a stale CLI `--help` string that **shipped in
  1.6.0**: `docs new --body-from`'s argparse help
  (`src/docs_cli/cli.py:2900-2905`) still described the
  pre-M15-C4 "first 20 lines looks like a metadata block"
  heuristic, which M15-C4 had replaced. The runtime detector
  (`_body_has_metadata_block`) and refusal message were correct;
  only the help text drifted, and the prose docs (`docs/cli.md`)
  + bundled `references/cli.md` were already correct — so the fix
  is doc-only and one line. **Not fixed in 1.6.0** (already
  shipped); logged as a v1.7 one-line follow-on (see
  [m17-pypi-publish-impl.md](archive/2026-10-26/m17-pypi-publish-impl.md)'s Open
  follow-on note). This miss motivated the new
  [Surface parity (help + bundled skill)](#surface-parity-help--bundled-skill)
  pre-publish gate above — **replaced-behavior drift** (not just
  newly-added surface) is what slipped through.

### From M20 (2026-06-12, `docs-cli==1.6.5`)

- **Fully-autonomous publish shipped M19 as 1.6.5 (one-to-one).** M20
  was driven end-to-end as a fully-autonomous pass walking this
  runbook directly (no 10-phase TDD stack — a publish milestone has no
  code phases); the operator authorized the irreversible PyPI upload +
  `main` push + `v1.6.5` tag + GitHub release up front. It shipped M19
  alone (as M11 shipped M10 and M13 shipped M12; M9 and M17 were the
  batched shapes). Chain-of-custody bit-perfect — **fifth release
  running** (M11 + M13 + M17 + M20).
- **Chain-of-custody extended to the sdist.** M11/M13/M17 sha256-compared
  only the PyPI-served **wheel** against the local build. M20 also pulled
  the served **sdist** (`pip download --no-deps --no-binary :all:`) and
  sha256-compared it — **also bit-perfect** (`f9de1eb4…`). Worth keeping:
  the sdist check is cheap and catches a class of mismatch the wheel check
  can't (sdist-only packaging globs). Note the sdist sha is only stable
  *within* a publish when `docs/` is untouched between builds — here it
  moved from the Phase-2/3 GO-report build (`78cef9cc…`) to the Phase-4
  dated-commit build (`f9de1eb4…`) purely because `docs/` evolved (the
  impl-log Phase-2/3 commit), **not** because of the CHANGELOG date edit
  (CHANGELOG is in neither sdist nor wheel — M13 generalised). The
  dated-commit build is canonical; the served sdist matched it bit-for-bit.
- **CHANGELOG is in neither the sdist nor the wheel — confirmed by
  manifest.** M13 verified CHANGELOG isn't in the sdist; M20 additionally
  inspected the **wheel** manifest (`docs_cli/` + `docs_cli-1.6.5.dist-info`
  only) and confirmed CHANGELOG isn't in the wheel either. So dating the
  CHANGELOG at Phase 4 cannot move *either* artefact's sha — the wheel was
  byte-identical to the GO-report build (`aba36e92…`), and the sdist moved
  only via `docs/` drift. The dated CHANGELOG reaches users via the git repo
  + the GitHub release notes.
- **Host-machine skill refresh is a NEW publish-closeout step (CLAUDE.md
  policy, 2026-06-12) — and it caught a real drift on first run.** Per the
  CLAUDE.md "Skill update flow" policy, host skills under `~/.claude/skills/`
  refresh only at production ship. M20's closeout ran `docs install-skill
  --force` from the published wheel (host `docs` skill came back
  byte-identical to the published bundled skill) and swept the workflow
  skills (`sync-and-commit`/`create-milestones`/`project-foundation`/
  `ship-milestone`) for the new surface (`touch --check`, `[check]
  stale_days`). The sweep found one genuine stale reference:
  `project-foundation/references/foundation-playbook.md` still described
  `docs new --body-from` with the pre-M19-D3 "first 20 lines" heuristic —
  fixed in place to the real detector. This is the first time the
  workflow-skill sweep surfaced a real drift, validating its place in the
  closeout. **v1.7+ candidate:** an in-repo lint that diffs the workflow
  skills' docs-cli prescriptions against the bundled `references/` surface so
  this drift is caught before publish, not at it.
- **JSON metadata cache lag recurred (as M11).** Immediately post-upload,
  the aggregate `/pypi/docs-cli/json` `releases` array still listed 1.6.0 as
  latest for a couple of minutes, while the per-version
  `/pypi/docs-cli/1.6.5/json` endpoint and the project page were already
  200 and `pip install docs-cli==1.6.5` resolved first try. Trust `pip
  install` / the per-version endpoint, not the lagging aggregate JSON.
- **Squatter still parked.** TestPyPI bare `docs-cli` re-checked at M20
  Phase 1 — unchanged (`latest: 0.1.0`, author None). The
  `docs-cli-rehearsal` detour continues. Token re-scope to project-`docs-cli`
  rolls forward as the M9 open follow-on.

### From M24 (2026-07-03, `docs-cli==1.8.0`)

- **Interactive gated publish, not fully-autonomous.** Unlike M13/M17/M20 (the
  operator authorized the irreversible steps up front and the conductor ran the
  runbook to completion), M24 ran under a "author now, confirm at the gate"
  decision: Phases 1–3 (prep → local gate → TestPyPI rehearsal) ran
  autonomously, then the walk **stopped at the Phase-4 gate** for an explicit
  operator go before the real PyPI upload + `main` push + tag + release. A valid
  driving mode — record which one a given publish used.
- **Batched publish of THREE milestones with two accrued version bumps →
  version skip.** M24 shipped M21 (built 1.7.0) + M22 (doc-only) + M23 (built
  1.8.0) as one `1.8.0` release. Because two implementation milestones each
  bumped `pyproject` (1.6.5 → 1.7.0 → 1.8.0), the CHANGELOG carried **two**
  `— UNRELEASED` sections. **New CHANGELOG shape vs M9/M17:** where those had a
  single UNRELEASED section to date, M24 had to **fold** the older section
  (1.7.0 → 1.8.0) and drop its header — `1.7.0` is a version number **skipped on
  PyPI**. Sixth release; first time a publish skipped an intermediate bumped
  version. When batching milestones that each bumped the version, decide fold-vs-
  keep-both at Phase 4 (M24 folded, per operator decision).
- **Chain-of-custody bit-perfect again (wheel AND sdist).** Sixth release
  running (M11 + M13 + M17 + M20 + M24). Wheel `29ac3ced…` was byte-identical
  across Phase 2/3/4 (`src/` unchanged); the sdist moved between phases purely
  via `docs/` drift and re-anchored at the Phase-4 tag-target commit
  (`62a29285…`) — the M13/M20 generalisation held.
- **M21's update-notice cannot be exercised on the TestPyPI rehearsal wheel.**
  Beyond the `docs 0.0.0+local` version print (M13), the rehearsal-name
  `0.0.0+local` also **fails M21's fail-closed version compare**, so the notice
  never fires under the rehearsal name. Verify the notice contract against the
  canonical **local** wheel (Phase 2) and the **PyPI** wheel (Phase 4), never
  the rehearsal wheel — the same rule the version string already follows.
- **Workflow-skill sweep found no drift — the first quiet sweep.** The
  host-skill refresh (`docs install-skill --force`) came back byte-identical,
  and the workflow-skill sweep surfaced nothing, because M21/M23 **added**
  surfaces (update-check, install-skill agent-awareness) rather than **changing**
  a verb the workflow skills prescribe (contrast M20's stale `--body-from`
  help). The in-repo drift-lint candidate (diff workflow-skill docs-cli
  prescriptions vs the bundled `references/` surface) still stands as the
  durable guard; it rolls forward.
- **Squatter still parked.** TestPyPI bare `docs-cli` re-checked at M24
  Phase 1 — unchanged (`latest: 0.1.0`, author None). The `docs-cli-rehearsal`
  detour continues. Token re-scope to project-`docs-cli` rolls forward as the
  M9 open follow-on.

### From M29 (2026-08-16, `docs-cli==2.0.0`)

- **The release toolchain can break without the package changing.** M29's
  pre-publish gate failed at `twine check` on artifacts that were otherwise
  perfect: an unpinned `hatchling` had started emitting
  `Metadata-Version: 2.5`, and `twine 6.2.0` monkeypatches
  `packaging.metadata._VALID_METADATA_VERSIONS` down to a list ending at `2.4`
  (`twine/package.py:32`). The installed `packaging` accepted 2.5, **PyPI**
  accepted 2.5, and `twine 7.0.0` passed — the checker was the only thing that
  did not. Two lasting changes came out of it: the *Artifact build* step now
  says **upgrade** twine rather than install-if-absent (the old wording is what
  let a stale twine survive), and the `twine>=7.0.0` floor moved into
  `pyproject.toml`'s `[dev]` extra so the constraint is version-controlled
  rather than living in this file's prose. Pinning `hatchling` backwards was
  considered and rejected: it would freeze the build backend to accommodate a
  stale checker and leave the real constraint undocumented.
- **A version bump needs an editable reinstall before the gate.**
  `test_version_matches_pyproject` failed at `'1.8.0' == '2.0.0'` immediately
  after the bump, because `__version__` resolves through `importlib.metadata`
  and reads the *installed* dist-info. `pip install -e ".[dev]"` fixed it. The
  test is correct; the install was stale. Now a checklist item in
  *Version + CHANGELOG verification*.
- **The workflow-skill sweep found real drift for the first time, and it was a
  retired flag.** Nine bare `--cascade` prescriptions across `create-milestones`
  (SKILL.md, `milestone-playbook.md`, `tdd-phases.md`, README) and
  `project-foundation` (`role-mapping.md`) — every one the milestone-completion
  step, which under 2.0 refuses at exit 2 and writes nothing. This is the case
  M24's entry predicted in the abstract: a release that **changes** a verb the
  workflow skills prescribe, not one that only adds surface. M29's own closeout
  hit the hazard and used `--cascade-only`. The in-repo drift-lint candidate —
  diff workflow-skill docs-cli prescriptions against the bundled `references/`
  surface — is now more than a nicety and rolls forward with a concrete failure
  behind it.
- **Chain of custody bit-perfect for both artifacts, and the wheel sha was
  stable across all three builds** (Phase 2, post-rehearsal canonical rebuild,
  Phase 4) — proof that the rehearsal-name detour leaves no trace in what
  ships. The sdist moved between builds exactly as M13 predicted, tracking
  `docs/`.
- **`README.md` is the PyPI project page and sits outside every parity gate.**
  M29 found it three releases stale: 3 of 12 verbs undocumented and three
  "Claude Code skill" mentions that M23's neutralisation never swept, in the
  one file no test reads. It was refreshed in **Phase 2**, not the closeout,
  because it ships inside the artifact as the long description. Future
  releases should treat the README as a Phase-2 artifact, not a doc chore.
- **The archive verb now rebases referring edges.** This runbook's post-release
  step told the operator to fix them by hand and pointed at an enhancement
  candidate; M18 shipped the `Related:` half and M28 the body-link half, so the
  instruction was obsolete and has been corrected in place.
- **Squatter still parked.** TestPyPI bare `docs-cli` re-checked at M29
  Phase 1 — unchanged (`0.1.0`, author None). The `docs-cli-rehearsal` detour
  continues. Token re-scope to project-`docs-cli` rolls forward as the M9 open
  follow-on, now six releases old.

### From M31 (2026-10-29, `docs-cli==2.1.0`)

- **The first publish run through `/ship-milestone`, with an automatic
  upload.** The operator authorized the upload, the tag push and the release
  up front, conditional on every stop condition holding at the moment of
  each action; Step 2 ran them without a further go. Step 1 (prep, gate,
  build, rehearsal) closed with a dual-provider review *before* anything
  irreversible ran. A third valid driving mode, after M13–M20's
  fully autonomous walk and M24's gated one.
- **Review the frozen irreversible-step commands with synthetic controls.**
  Step 1's review found three defects in commands written to run
  unattended: a token search that printed what it matched, then — once
  fixed — failed open under `pipefail` because `grep -q` exits at its first
  match and kills the producer; a `~/.pypirc` shape check whose parser error
  would quote the offending line; and stop rules that gave two outcomes for
  a partial upload. Each fix was proven on synthetic tokens and files, never
  real ones. *Isolation and hygiene* and the upload step describe them; the
  M31 task plan's P1.4 and P1.5 hold their exact text.
- **A check compared wall-clock output byte for byte.** The probe's
  `docs index --dry-run` check compared stdout with the tree's `INDEX.md`
  exactly, but `render_index` stamps today's date. Run after midnight
  against the tag target's INDEX, it would have failed *after* the upload
  and before the tag. Step 2's planning caught it; the check now normalises
  only the `_Generated` stamp, as the product test does, and the script's
  re-run proved the cross-day case passes and an edited entry still fails.
  Any release check that compares generated output should be read for the
  calendar.
- **A build backend shipped the same day.** hatchling 1.33.0 was released
  the morning of M31's first build. The resolved build environment was
  recorded, and the tag-target build reproduced the first wheel's sha
  without the constraints remedy — `[build-system]` stays unpinned.
- **The midnight crossing.** The tag-target build waited for the local date
  to roll, so the CHANGELOG was re-dated once (a one-line commit) rather
  than racing the clock; the upload ran at 00:04 CET, which PyPI records as
  23:04 UTC the previous day. The heading follows the local date.
- **`install-skill` records its destination on every success**, so every
  throwaway run redirects `XDG_STATE_HOME` and `XDG_CACHE_HOME`; only the
  host step writes host state, and it unsets both on purpose.
- **The rehearsal name is unclaimed on real PyPI.** An `--extra-index-url
  https://pypi.org/simple/` rehearsal install would run whoever claims
  `docs-cli-rehearsal` on a token-bearing host, so every index install
  names one index with `--no-deps`.
- **Binary and skill moved together**, closing M29's gap: `pipx upgrade`
  first, then `install-skill --force` with the published binary, each
  verified byte for byte against the served wheel. pipx's `upgrade` also
  ran a pip upgrade in its shared libraries and touched `shared/bin/pip`,
  regardless of their age; no package changed.
- **A downstream consumer's capability probe, run before the tag.** The
  Agent Playbook Suite's CI guard step, extracted verbatim, read
  `lifecycle verb: True, free-form relate: True` against the PyPI-served
  wheel, and its full guard failed with exactly the ten lines its pin-bump
  PR must clear.
- **Chain of custody bit-perfect for wheel and sdist**, the seventh release
  running (M11, M13, M17, M20, M24, M29, M31): one wheel sha across the
  first build, the post-rehearsal rebuild, the tag-target build, the JSON
  and the served bytes; the sdist anchored at the tag target and equal to
  both served forms.
- **Squatter still parked.** TestPyPI bare `docs-cli` re-checked at M31
  Phase 1 — unchanged (`0.1.0`, author None). The `docs-cli-rehearsal`
  detour continues. Token re-scope to project-`docs-cli` rolls forward as the
  M9 open follow-on, now seven releases old.
