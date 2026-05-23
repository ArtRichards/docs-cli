# M6 — PyPI distribution as `docs-cli`

Status: draft
Role: milestone
Project: docs
Updated: 2026-05-23

Related:
- child-of: plan.md
- implements: charter.md
- pairs-with: architecture.md
- pairs-with: cli.md
- pairs-with: m5-claude-code-skill.md

## Overview

- Milestone: M6 (first v1.1 milestone)
- Title: PyPI distribution as `docs-cli`
- Surface: a buildable, installable Python distribution **`docs-cli`** on
  PyPI; a real importable package (`docs_cli`) backing the existing executable;
  a one-shot **`docs install-skill`** verb that places the bundled Claude Code
  skill onto a host without requiring a repo clone; the corresponding repo,
  pyproject, README, and architecture rewiring.
- Status: **DRAFT** — not yet started. This file is a proposal for v1.1;
  `Status: draft` until accepted and moved to `active` at the milestone's
  own Phase 1.

### Goal

Today `docs` ships **only** as a `git clone` + symlink. That works on the
author's box but is the wrong shape for adoption — there's no `pip install`,
no version pinning, no wheel for CI, and the Claude Code skill at
`skills/docs/` can only be installed by someone who has the repo on disk.

M6 closes that gap. The distribution is published to PyPI as **`docs-cli`**
(the bare name `docs` is squatted as an empty PyPI placeholder — `pip install
docs` fails with no distributions, and the name is unobtainable without a
PEP 541 transfer). The dominant UX is preserved: users `pip install docs-cli`
and type `docs ...`. The skill ships *inside* the wheel as package data and
is installable via `docs install-skill`, so PyPI users get the same agent
behaviour `git clone` users get. M6 also performs the long-deferred
`bin/docs` single-file-vs-package split (`status.md`'s parked question), but
keeps the file logically monolithic — it relocates to `src/docs_cli/cli.py`
as one file with an importable `main()` entry point, rather than fragmenting
into 12 sub-modules. The exit criterion is concrete and verifiable end-to-end:
a freshly-created Python virtualenv on a clean host can `pip install
docs-cli`, run `docs --version`, run `docs install-skill`, and the installed
skill drives the verbs identically to the in-repo install.

### Requirements

- **The distribution name is `docs-cli`.** `docs` is squat-blocked on PyPI
  (an empty placeholder with `simple` index 200 and zero release files; no
  PEP 541 transfer attempted). `docs-cli` is verified available at draft
  time.
- **The command name stays `docs`.** Wired via `[project.scripts] docs =
  "docs_cli.cli:main"`. Users type `docs ...` exactly as today. No
  `docs-cli` alias is exposed (OQ1 resolved 2026-05-23 — see Decisions).
- **A real importable package.** `bin/docs` (a script with no `.py` extension,
  loaded by `conftest.py` via `importlib.machinery.SourceFileLoader`) becomes
  `src/docs_cli/cli.py` — a normal Python module with a public `main()` that
  the entry point invokes. `bin/docs` either disappears or becomes a thin
  one-line shim `from docs_cli.cli import main; raise SystemExit(main())` for
  in-repo dogfooding. **The file stays logically monolithic** — M6 does **not**
  fragment the 2,534-line script into per-verb sub-modules. That is a
  separate refactor, not a packaging change.
- **A build backend in `pyproject.toml`.** Add `[build-system]` with
  hatchling (no plugins; defaults are sufficient). Add `[project.scripts]
  docs = "docs_cli.cli:main"`. Add `[project.urls]` (Homepage, Repository,
  Issues). Bump `version` to `1.1.0` (drop the milestone-suffix scheme used
  during v1 development — `0.4.0-m4` was an in-development marker, not a
  release version). `__version__` in `docs_cli/cli.py` follows.
- **The wheel and sdist both build cleanly.** `python -m build` produces
  `dist/docs_cli-1.1.0-py3-none-any.whl` and
  `dist/docs_cli-1.1.0.tar.gz`. Both install into a throwaway venv and the
  `docs` entry point works.
- **The skill ships inside the wheel as package data.** `skills/docs/`
  relocates (or is mirrored) under `src/docs_cli/skill/` (final path per
  OQ4) and is declared as package data so it survives the wheel build. A
  new verb **`docs install-skill [--dest DIR] [--symlink|--copy] [--force]`**
  resolves the bundled skill directory via `importlib.resources` and
  installs it to `~/.claude/skills/docs/` (or `--dest`). Default action is
  `--copy`; `--symlink` is rejected for wheel installs (a wheel may not
  expand to real on-disk paths under all installers).
- **Tests pass against the installed wheel, not just the in-tree source.**
  A new `tests/test_packaging.py` builds the wheel in a `tmp_path`, installs
  it into a `venv.EnvBuilder`-created throwaway venv, and exercises:
  (a) `docs --version` reports `1.1.0`; (b) `docs --help` lists every verb;
  (c) `docs install-skill --dest <tmp>` produces the expected file tree at
  `<tmp>/docs/SKILL.md` etc.; (d) the installed `docs check <fixture-tree>`
  exits 0 against a known-clean fixture; (e) `import docs_cli` succeeds and
  `docs_cli.cli.main` is callable. This is the milestone's most important
  test: a green in-tree suite *cannot* catch packaging failures (missing
  package data, bad entry point, broken wheel manifest).
- **The existing test suite remains green** after the relocation. Every
  `from docs import X` either keeps working (via a `conftest.py` shim that
  aliases `docs_cli.cli` as `docs` in `sys.modules`) or is mechanically
  rewritten to `from docs_cli.cli import X`. Decision is OQ2.
- **A GitHub Actions release workflow.** On a `v*` tag push: build sdist +
  wheel, run the in-tree quality gate, publish to PyPI via **Trusted
  Publishing** (OIDC; no API token in repo secrets). A separate manual-trigger
  workflow publishes to **TestPyPI** for dry-run rehearsal before any real
  release.
- **A documented release procedure.** New `docs/release-runbook.md` (Role:
  runbook) — the per-release checklist: bump version, regenerate INDEX,
  green quality gate, tag, watch the workflow, install from PyPI in a
  throwaway venv, smoke-test, write a GitHub release note. The runbook is
  the artifact that makes M7+ releases boring.
- **The README and `architecture.md` install sections are rewritten.**
  `pip install docs-cli` becomes the primary install; `git clone` is
  documented second, for contributors. The skill install becomes either
  `docs install-skill` (PyPI users) or a one-line `ln -s` (contributors with
  a checkout).
- **The repo and local checkout are renamed.** GitHub repo and local
  directory move from `docs` to `docs-cli` so the on-disk name, the PyPI
  distribution, and the GitHub `Repository:` URL are consistent. The skill
  name (`docs`) and the command (`docs`) are unchanged. (Repo rename mechanics
  and timing are OQ3.)
- **No change to the on-disk Markdown convention.** `Project: docs` in every
  metadata block stays `docs`. The convention is independent of the
  distribution name; the project's identity in its own metadata is its
  long-standing name, not its packaging label.

### Deliverables

- [ ] `pyproject.toml`: `name = "docs-cli"`, `version = "1.1.0"`,
      `[build-system]` (hatchling), `[project.scripts] docs =
      "docs_cli.cli:main"`, `[project.urls]`, package data for the bundled
      skill. Old `keywords`, `classifiers`, `authors`, `license`, optional
      `[dev]` extras preserved.
- [ ] `src/docs_cli/__init__.py` — re-exports `main` from `cli`.
- [ ] `src/docs_cli/cli.py` — the relocated `bin/docs`, byte-identical
      module-body content, with `__version__` bumped to `1.1.0` and the
      file extension/path change being the only structural diff.
- [ ] `src/docs_cli/skill/SKILL.md` + `src/docs_cli/skill/references/{convention,cli}.md`
      — relocated (or symlinked from the original `skills/docs/` for
      development; final layout per OQ4) so the wheel can ship them.
- [ ] `bin/docs` — either removed (if dev workflow runs the entry point via
      `docs` after `pip install -e .`) or reduced to a 2-line shim. Decision
      in OQ5.
- [ ] New verb `docs install-skill [--dest DIR] [--copy|--symlink] [--force]`
      implemented in `cli.py`; respects `~/.claude/skills/docs/` as default
      dest; idempotent (re-running on an unchanged install is a no-op);
      `--force` overwrites; surface and exit codes specified in `cli.md`.
- [ ] `tests/test_packaging.py` — the in-tmpvenv install-and-run test
      suite (see Requirements above for the five sub-cases).
- [ ] `tests/conftest.py` — updated to load `docs_cli.cli` directly (no
      `SourceFileLoader` gymnastics) and, per OQ2, optionally alias it as
      `docs` in `sys.modules` so existing `from docs import X` test
      imports remain unchanged.
- [ ] `tests/test_skill.py` — paths updated; the "every named verb is
      real" check now reads `docs_cli.cli._build_parser()`.
- [ ] `.github/workflows/release.yml` — tag-triggered PyPI publish via
      Trusted Publishing.
- [ ] `.github/workflows/testpypi.yml` — manual-trigger TestPyPI publish.
- [ ] `docs/release-runbook.md` — the per-release checklist (Role: runbook).
- [ ] `README.md` — `pip install docs-cli` as the primary install; `docs
      install-skill` for the skill; `git clone` documented as the contributor
      path.
- [ ] `docs/architecture.md` — Shape section updated for the new package
      layout; Install section rewritten; Sibling-artifact note updated for
      the bundled-skill-in-wheel.
- [ ] `docs/cli.md` — new `install-skill` verb documented (synopsis,
      flags, exit codes).
- [ ] `docs/charter.md` — distribution paragraph added (it currently
      assumes git-clone install).
- [ ] `docs/plan.md` — v1.1 section added with M6 as the first milestone;
      the parked `[vocabulary] add_fields` allowlist question remains as a
      separate v1.1 entry, unrelated to M6.
- [ ] `docs/status.md` — M6 added to the milestone table; `Current
      milestone` rewritten; reading-order updated.
- [ ] `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` regenerated
      in lockstep.
- [ ] GitHub repo renamed `docs` → `docs-cli`; local checkout moved
      `~/opt/docs` → `~/opt/docs-cli`. Git remote URL updated. Mechanics
      in OQ3.
- [ ] PyPI release **1.1.0** published; install from PyPI in a throwaway
      venv exercised (the Phase 9 dogfood gate).

## Current state analysis (snapshot at draft, 2026-05-23)

- **What ships today.** A single executable Python file at `bin/docs`
  (2,534 lines, Python 3.11+, stdlib only). Eight verbs (`index`, `new`,
  `archive`, `mv`, `touch`, `check`, `list`, `migrate`). A Claude Code
  skill at `skills/docs/` with two bundled reference files. Test suite at
  246 tests, ruff + mypy clean tree-wide. `bin/docs check docs/` exits 0.
- **What `pyproject.toml` already has.** `name = "docs"`, `version =
  "0.2.0-m2"`, author, license, classifiers, keywords, optional `[dev]`
  extras (`pytest`, `ruff`, `mypy`), `[tool.pytest.ini_options]`,
  `[tool.ruff]` (including the critical `extend-include = ["bin/docs"]`
  so ruff lints the extensionless executable), `[tool.mypy]` (including
  `scripts_are_modules = true` for the same reason). **No `[build-system]`
  section.** **No entry point.** **No `name = "docs-cli"`.** **The
  declared version is stale** (still `0.2.0-m2`; v1 shipped at M5).
- **The PyPI name problem.** `pip install docs` fails — the project page
  `https://pypi.org/project/docs/` exists (HTTP 200, status `active`) but
  the simple index is empty (`<h1>Links for docs</h1>` with zero `<a>`
  entries) and the JSON API returns 404. The name is squatted as an empty
  placeholder. Recovering it would require a PEP 541 abandoned-project
  request to PyPI admins — multi-week timeline, not guaranteed. **`docs-cli`
  is available** (simple index 404 at draft time) and is the chosen
  distribution name.
- **The parked single-file/package-split question.** `docs/status.md`'s
  "Watch out for" calls out "the deferred `bin/docs` single-file vs
  package split" as v1.1 scope. M4's milestone Decisions parked it
  explicitly. M5 added no Python so it was untouched. **M6 forces the
  decision** because `[project.scripts]` requires a `module:function`
  entry point, not a path — so `bin/docs` must become an importable
  module *at some module path*. M6's resolution is the minimal one:
  relocate the single file to `src/docs_cli/cli.py` and add a public
  `main()` — keep the monolithic shape, do **not** split into per-verb
  modules. The deeper "should this be 12 files?" question stays parked.
- **How tests currently reach the script.** `tests/conftest.py` uses
  `importlib.machinery.SourceFileLoader("docs", str(REPO_ROOT / "bin" /
  "docs"))` and registers the loaded module as `docs` in `sys.modules`,
  letting test files write `from docs import Doc, parse, ...`. After
  relocation the import is `from docs_cli import cli` (or `from
  docs_cli.cli import main, Doc, parse, ...`). The conftest can preserve
  the `docs` alias to avoid touching ~18 test files (OQ2).
- **The skill's deploy path.** Today: `ln -s ~/opt/docs/skills/docs
  ~/.claude/skills/docs`. After M6, a PyPI user has no checkout to
  symlink from — the skill must reach the host via the wheel. Mechanism:
  `importlib.resources` reads the bundled `src/docs_cli/skill/`
  directory; `docs install-skill` materialises it under
  `~/.claude/skills/docs/`. The committed skill artifact stays
  host-agnostic; the host-specific path is still the install step, per
  M5's OQ2 resolution.
- **The existing `architecture.md` install snippet.** Three `ln -s` lines
  for binary + skill. After M6 these become `pip install docs-cli` +
  `docs install-skill` for end-users, with the symlink form kept as the
  contributor path.
- **What v1.1's roadmap currently says.** `plan.md` is open-question-only
  for v1.1 — the `[vocabulary] add_fields` allowlist. `status.md`'s
  "Next action: none — v1 is complete" needs to be replaced once M6 is
  accepted. No prior v1.1 milestone numbering exists; **M6 is the first
  v1.1 milestone** and the numbering continues monotonically (M1-M5 → M6).

## TDD Implementation Plan

The ten phases follow the methodology in [status.md](status.md). Because M6
adds a small code surface (one new verb) **and** restructures the repo
**and** introduces a wheel-build pathway, the phases bias toward the
RED→GREEN cycle running against `tests/test_packaging.py` — the suite that
can only pass when the wheel actually builds and the entry point actually
works.

### Phase 1: Define Contract

- **Objective:** Promote this milestone from `idea` to `active`; commit the
  scope and the OQ resolutions before any code moves.
- **Files:**
  - `docs/m6-pypi-distribution.md` — flip `Status: draft` → `active`,
    bump `Updated:`, resolve OQ1–OQ5 (record each in Decisions).
  - `docs/m6-pypi-distribution-log.md` — created; OQ resolutions and the
    Phase-1 commit logged.
  - `docs/plan.md` — add `## v1.1` section; M6 listed as first v1.1
    milestone; the parked allowlist question stays where it is.
  - `docs/status.md` — `Current milestone` rewritten; M6 added to the
    milestone table as `In flight`; "Next action" replaced.
  - `docs/architecture.md` — Shape section gains a forward-pointer that
    the layout will change at Phase 5; no actual change yet. `Updated:`
    bumped.
  - `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` regenerated
    in lockstep so the two new M6 docs appear.
- **Exit:** M6 is `active`; OQs are resolved (or explicitly carried to
  Phase 2 with a deadline); ruff/mypy/pytest still green; `docs check
  docs/` exits 0; the INDEX snapshot matches.

### Phase 2: Write Tests (RED)

- **Objective:** Express every M6 requirement as a failing check, in code
  where possible and as a release-runbook checklist where not.
- **Files:**
  - `tests/test_packaging.py` — implement all five sub-cases:
    (1) wheel builds via `python -m build` into a `tmp_path` dist dir;
    (2) wheel installs into a `venv.EnvBuilder` throwaway venv without
    errors; (3) the venv's `docs --version` prints `1.1.0`;
    (4) `docs --help` lists every verb the in-tree parser lists (use the
    in-tree `_build_parser()` to derive the expected verb set);
    (5) `docs install-skill --dest <tmp>` produces `<tmp>/SKILL.md` and
    `<tmp>/references/{convention,cli}.md` byte-identical to the source
    skill files; (6) the venv's `docs check <fixture-tree>` exits 0 on a
    known-clean fixture.
  - `tests/test_skill.py` — extend with one check: `tests/fixtures/expected`
    or a tmp dir installed via `docs install-skill` produces a directory
    structure that satisfies the same structural checks as the in-repo
    `skills/docs/`.
  - `docs/release-runbook.md` — created as a checklist of items the dogfood
    pass must hit (this is the manual-execution analogue of M5's
    trigger-scenario checklist).
- **Exit:** every new check fails for the right reason — no build backend,
  no entry point, no `install-skill` verb, no relocated package. The
  existing 246-test suite remains green (since nothing has been moved yet).

### Phase 3: Create Data/Fixtures

- **Objective:** Stage the fixtures the packaging tests need.
- **Files:**
  - `tests/fixtures/trees/packaging-clean/` — a tiny known-clean docs tree
    (one `.docs.toml`, one charter, one plan, no errors) used by the
    `docs check` sub-case in `test_packaging.py`.
  - Nothing else — the wheel itself is built fresh in each test run; no
    pre-built artifact is checked in.
- **Exit:** every fixture a Phase-2 check references is present; running
  Phase 2's tests now fails on the *intended* reason (no build backend,
  no entry point) rather than on a missing fixture.

### Phase 4: Run Tests (RED Baseline)

- **Objective:** Confirm every failure traces to the unimplemented
  packaging surface, not misconfiguration. **Session pauses here.**
- **Actions:** `.venv/bin/python -m pytest tests/test_packaging.py -v` —
  capture full output; confirm each sub-case fails on the expected
  ModuleNotFoundError / FileNotFoundError / wheel-build error.
- **Exit:** `tests/test_packaging.py` is fully RED for the right reasons;
  the rest of the suite remains green; runbook checklist is fully
  unsatisfied.

### Phase 5: Update Base Interfaces

- **Objective:** Restructure the repo. This is the largest single phase
  diff in M6 by line count, but it is mechanical: file moves, not logic
  changes.
- **Actions:**
  - `git mv bin/docs src/docs_cli/cli.py` (or equivalent — verify
    `__version__` line and `if __name__ == "__main__": main()` guard).
  - Create `src/docs_cli/__init__.py` re-exporting `main`.
  - Relocate the skill: `git mv skills/docs src/docs_cli/skill` (final
    layout per OQ4). If OQ4 picks "mirror not move", leave `skills/docs/`
    in place and add a sync check.
  - Update `tests/conftest.py`: drop the `SourceFileLoader` block, replace
    with `from docs_cli import cli as docs; sys.modules.setdefault("docs",
    cli)` (the alias preserves existing `from docs import X` imports per
    OQ2) — or rewrite every test import per the OQ2 resolution.
  - Update `tests/test_skill.py` and `tests/test_skill_refs.py` for new
    skill paths.
  - Update `pyproject.toml`'s `extend-include` (ruff) and `files` (mypy)
    lists: `bin/docs` removed, `src/docs_cli/` added, `scripts_are_modules`
    deleted (no longer needed).
- **Exit:** the existing 246-test suite is green again after the move; ruff
  / mypy clean tree-wide; `bin/docs` is gone or is a 2-line shim;
  `tests/test_packaging.py` is still RED (no `[build-system]` yet).

### Phase 6: Implement Offline/Core Path

- **Objective:** Make the wheel build. Make the entry point work. Make
  `docs install-skill` work.
- **Files:**
  - `pyproject.toml` — add `[build-system]` (hatchling), `[project.scripts]
    docs = "docs_cli.cli:main"`, `[project.urls]`, package-data declaration
    for `docs_cli/skill/**`, `version = "1.1.0"`.
  - `src/docs_cli/cli.py` — bump `__version__` to `1.1.0`; add the
    `install-skill` verb (argparse subparser, handler `_install_skill`,
    exit codes per `cli.md`); resolve the bundled skill via
    `importlib.resources.files("docs_cli") / "skill"`.
  - `docs/cli.md` — `install-skill` synopsis, flags, exit codes added.
- **Exit:** `python -m build` succeeds in a temp dir; the wheel contains
  the skill files; `tests/test_packaging.py` sub-cases (1)–(5) pass; (6)
  passes; the whole suite green.

### Phase 7: Update Tool/Wrapper Layer

- **Objective:** Wire the release workflow and the docs.
- **Files:**
  - `.github/workflows/release.yml` — tag-triggered (`v*`); jobs: lint,
    test, build, publish-to-pypi via Trusted Publishing (OIDC).
  - `.github/workflows/testpypi.yml` — `workflow_dispatch` trigger;
    publishes to TestPyPI; same lint/test/build prelude.
  - `docs/release-runbook.md` — finalised: per-release checklist (bump,
    INDEX, gate, tag, watch, throwaway-venv smoke, GitHub release note).
  - `README.md` — install section rewritten: `pip install docs-cli` first,
    `docs install-skill` second, `git clone` third (contributor path).
  - `docs/architecture.md` — Shape section updated (`src/docs_cli/cli.py`,
    `src/docs_cli/skill/`); Sibling-artifact note updated; Install section
    rewritten.
  - `docs/charter.md` — one-paragraph distribution note added.
- **Exit:** workflows lint cleanly; README and architecture install
  sections describe the wheel path correctly; the release runbook is
  reviewable end-to-end.

### Phase 8: Run Tests (GREEN)

- **Objective:** Full suite green; quality gate clean tree-wide; wheel
  builds and installs cleanly in CI.
- **Actions:** `pytest -q`; `ruff check .`; `ruff format --check .`;
  `mypy`; `python -m build` + smoke-install in a throwaway venv via the
  in-test path.
- **Exit:** all green.

### Phase 9: Implement Online/Integration (dogfood + TestPyPI dry-run)

- **Objective:** Real publish to TestPyPI, real install from TestPyPI,
  real exercise. The packaging equivalent of M1–M4's "dogfood against a
  fixture tree" phase.
- **Actions:**
  - Trigger `testpypi.yml`; confirm wheel + sdist land on TestPyPI under
    `docs-cli`.
  - On a clean throwaway venv: `pip install --index-url
    https://test.pypi.org/simple/ docs-cli==1.1.0` — confirm install
    succeeds; run every checklist row in `docs/release-runbook.md`.
  - Walk the runbook to completion against the TestPyPI artifact: `docs
    --version`, `docs --help`, `docs install-skill`, `docs check` against
    a fresh tree, the skill is discoverable by Claude Code, regenerate
    this repo's `INDEX.md` via the installed `docs index`.
- **Exit:** the runbook is fully satisfied against the TestPyPI artifact;
  no checklist row is open. If anything fails, the failure goes back into
  Phase 6 or 7, not papered over.

### Phase 10: Quality, Docs, Refactor (real PyPI publish + closeout)

- **Objective:** Ship `docs-cli==1.1.0` to real PyPI; mark M6 complete.
- **Actions:**
  - Tag `v1.1.0`; release workflow publishes to PyPI; install from PyPI
    in a throwaway venv re-runs the runbook smoke subset.
  - GitHub release notes written referencing the M6 summary.
  - GitHub repo rename `docs` → `docs-cli` (per OQ3); local checkout
    `~/opt/docs` → `~/opt/docs-cli`; git remote URL updated; CLAUDE.md
    and the docs-cli project memory updated.
  - `docs/status.md` — M6 → Complete, v1.1 in progress; reading order
    updated.
  - `docs/plan.md` — v1.1 section's M6 row marked shipped; remaining
    parked questions unchanged.
  - `docs/INDEX.md` + snapshot regenerated in lockstep.
- **Exit:** `pip install docs-cli` from any host installs a working
  `docs` command and a `docs install-skill` that places the skill
  correctly; all docs reflect the new install story; the milestone is
  complete.

## Phase Checklist

- [ ] Phase 1: Define Contract
- [ ] Phase 2: Write Tests (RED)
- [ ] Phase 3: Create Data/Fixtures
- [ ] Phase 4: Run Tests (RED Baseline)
- [ ] Phase 5: Update Base Interfaces
- [ ] Phase 6: Implement Offline/Core Path
- [ ] Phase 7: Update Tool/Wrapper Layer
- [ ] Phase 8: Run Tests (GREEN)
- [ ] Phase 9: Implement Online/Integration (TestPyPI dry-run)
- [ ] Phase 10: Quality, Docs, Refactor (real PyPI publish + closeout)

## Decisions

Key choices applying to this milestone (broader decisions live in
`vocab-adr.md` / `dual-status-adr.md`; M5's Decisions section is the
nearest precedent for milestone-local choices). Each open question below
becomes a Decision here once resolved.

- **OQ1 — the command name stays `docs`; no `docs-cli` script alias
  (RESOLVED 2026-05-23, operator-confirmed as recommended).** Users type
  `docs ...` exactly as they do today; the distribution name `docs-cli`
  appears only at install time (`pip install docs-cli`). This is the
  dominant pattern for the `<dist>-cli` family — `pip install
  python-dateutil` → `import dateutil`; `pip install docs-cli` → `$ docs
  ...`. No defensive `docs-cli` alias is added; if a future host has a
  PATH collision on `docs`, the resolution is local (rename the offender,
  or alias) rather than baked into the distribution.
- **The distribution name is `docs-cli`.** The bare `docs` name on PyPI is
  squat-blocked as an empty placeholder (simple index returns 200 with
  zero release files; JSON API 404; project page 200). Recovering it
  requires a PEP 541 transfer — multi-week, uncertain. `docs-cli` is
  available, descriptive, and parallel to many established CLI gems
  (`build`, `pip`, `pipx` all expose a `cli` form when their bare name
  was taken). This is non-negotiable for v1.1 PyPI publishing.
- **The single-file-vs-package question stays parked, but the file is
  relocated.** M6 needs an importable module to wire `[project.scripts]`,
  so `bin/docs` becomes `src/docs_cli/cli.py`. **The 2,534 lines stay in
  one file.** Per-verb splitting is a separate refactor the team can
  revisit post-v1.1; it would inflate M6 by an order of magnitude with
  no packaging benefit.
- **The skill ships inside the wheel.** A PyPI user must get the same
  skill behaviour a `git clone` user gets, or PyPI distribution is
  half-built. The skill files are package data under `src/docs_cli/skill/`;
  a new `docs install-skill` verb places them on the host. No `setup.py
  install`-style hook, no `post_install` script — these are deprecated and
  do not survive `pip install --user` / pipx anyway. Explicit verb is
  preferable: the user runs it, sees the dest, confirms the copy.
- **`docs install-skill` defaults to `--copy`, not `--symlink`.** A wheel
  installed via `pip` may live anywhere — including read-only mounts,
  containers, or zip-imported eggs — and a symlink from
  `~/.claude/skills/docs` into that location is fragile. `--copy` is the
  safe default; `--symlink` is offered for the contributor case (it
  symlinks the source directory of an editable `pip install -e .` install
  into the skills dir).
- **Trusted Publishing (OIDC), not API tokens.** No long-lived PyPI token
  in repo secrets; the GitHub Action authenticates to PyPI via OIDC. One
  configuration step on the PyPI side (register the Trusted Publisher
  binding for `docs-cli` against the `docs-cli` GitHub repo on the
  `release.yml` workflow). Standard for new projects.
- **TestPyPI rehearsal before every real release.** The Phase 9 dry-run
  via TestPyPI is part of the runbook, not optional. The cost is one
  workflow run and a throwaway venv; the upside is that the dress
  rehearsal catches name typos, missing package-data globs, bad classifier
  values, and rendering errors in the README *before* they hit
  pypi.org/project/docs-cli/ where they cannot be deleted (only yanked).

## Testing / Quality Gate

Commands run at Phase 4 (RED baseline), Phase 8 (GREEN), and Phase 10:

```
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
docs check docs/                                    # repo still clean
docs index --root docs/ --dry-run                   # INDEX idempotent
python -m build                                     # wheel + sdist build
pytest tests/test_packaging.py -v                   # in-tmpvenv install + run
```

Plus the M6-specific dogfood gate at Phase 9: walk `docs/release-runbook.md`
end-to-end against the TestPyPI artifact, then again against the real PyPI
artifact at Phase 10.

Expected at Phase 4: existing 246 tests green; every
`tests/test_packaging.py` sub-case RED for the intended reason; runbook
unsatisfied. Expected at Phase 8/10: all green, packaging tests included;
runbook fully satisfied against the published artifacts.

## Success Criteria

M6 is complete when:

- [ ] All Phase Checklist items are checked.
- [ ] `pip install docs-cli==1.1.0` works from PyPI on a clean host with
      Python 3.11+ and produces a working `docs` command.
- [ ] `docs install-skill` places a host-correct skill that drives the
      verbs identically to the in-repo install.
- [ ] `tests/test_packaging.py` passes, including the in-tmpvenv install +
      run sub-case.
- [ ] The Phase 9 dogfood pass (TestPyPI) and the Phase 10 dogfood pass
      (real PyPI) both satisfy `docs/release-runbook.md` end-to-end.
- [ ] `pyproject.toml`, `README.md`, `docs/architecture.md`, `docs/cli.md`,
      and `docs/charter.md` all describe the new install story
      consistently.
- [ ] The GitHub repo and local checkout are renamed `docs-cli`; the
      `Repository:` URL in `pyproject.toml` matches.
- [ ] `docs/status.md` reflects M6 → Complete and the project as
      v1.1-in-progress.
- [ ] `docs/m6-pypi-distribution-log.md` contains a milestone-completion
      summary.

## OPEN QUESTIONS

Four open questions to resolve at Phase 1 (Decisions above will absorb the
verdicts). OQ1 was resolved at draft time (2026-05-23, operator-confirmed)
and is preserved below under "OPEN QUESTIONS — resolved".

### OQ2 — Test import shape: alias `docs_cli.cli` as `docs`, or rewrite every test?

**Recommendation: alias.** `conftest.py` does `from docs_cli import cli;
sys.modules.setdefault("docs", cli)`, and every existing `from docs import
X` keeps working. The alternative — rewriting ~18 test files from `from
docs import X` to `from docs_cli.cli import X` — is mechanical but pollutes
the M6 diff with churn unrelated to packaging. Aliasing is one line;
rewriting is ~150 lines of import edits. If the team later wants the
explicit import, that's a separate sweep. **Alternative:** full rewrite —
clearer long-term, but expands M6's blast radius unnecessarily.

### OQ3 — Repo rename: when, and how invasive?

**Recommendation: rename at Phase 10 (after the first PyPI publish
succeeds), not before.** Sequence: tag and publish from the still-named
`docs` repo, confirm the PyPI artifact works, *then* rename the GitHub
repo (`gh repo rename docs-cli`) and the local checkout (`mv ~/opt/docs
~/opt/docs-cli && git -C ~/opt/docs-cli remote set-url origin
git@github.com:<owner>/docs-cli.git`). Rationale: the publish workflow is
the unknown; renaming first risks two failures interacting. GitHub
provides automatic redirects from the old repo URL for the foreseeable
future, so the rename does not break clones or fetches in flight. CLAUDE.md
and the project-memory pointer file update at the same time.
**Alternative:** rename at Phase 1 (matches the new identity from the
start, but means the first publish runs from a freshly-renamed repo —
two changes at once).

### OQ4 — Bundled skill layout: move into `src/docs_cli/skill/`, or mirror?

**Recommendation: move (and remove `skills/docs/`).** A single source of
truth for the skill — under `src/docs_cli/skill/` — that the wheel ships
directly. The README and architecture docs point at the new path. For
contributors doing `pip install -e .`, the editable install means edits to
`src/docs_cli/skill/SKILL.md` are immediately visible to `docs install-skill
--symlink`. **Alternative:** mirror (keep `skills/docs/` as the authored
copy and have a build hook copy into `src/docs_cli/skill/`) — preserves
the existing top-level path but introduces a sync surface that
`test_skill_refs.py`-style lockstep tests must police. Move is simpler.

### OQ5 — `bin/docs`: delete, or keep as a thin shim?

**Recommendation: delete.** After Phase 5 the contributor workflow is `pip
install -e ".[dev]"`, which provides the `docs` command on `$PATH`
directly. `bin/docs` becomes redundant. The single concession: `README.md`'s
contributor section explicitly tells contributors to `pip install -e .`
before expecting `docs ...` to work. **Alternative:** keep a 2-line shim
(`from docs_cli.cli import main; raise SystemExit(main())`) for
contributors who do not want an editable install — but this resurrects
the original "executable script with no extension" complexity (ruff
`extend-include`, mypy `scripts_are_modules`) that M6 was about to retire.
Delete is cleaner.

## OPEN QUESTIONS — resolved

_Questions resolved before Phase 1 are recorded here; the resolution itself
lives in the Decisions section above. The full question, why-it-matters, and
recommendation text is preserved here as the historical record; a **RESOLVED**
line at the head of each gives the verdict._

### OQ1 — Command name: stay `docs`, or also expose `docs-cli`?

**RESOLVED (operator-confirmed 2026-05-23) — stay `docs` only, no
`docs-cli` alias.** Approved as recommended. See the OQ1 Decision above.

**Question.** With the distribution renamed `docs-cli` on PyPI, should the
installed command (the entry point name in `[project.scripts]`) stay `docs`,
also expose a `docs-cli` alias, or rename to `docs-cli` outright?

**Why it matters.** It decides the user's daily-typed name. The skill body,
the README, every test, and every existing piece of documentation says
`docs ...`. Changing the command pessimises that UX to fix a problem
(PATH collision with another `docs`) that does not exist on any known host.

**Recommended answer (drafted above).** Stay `docs` only. The distribution
name `docs-cli` appears only at install time; the dominant `<dist>-cli`
pattern (`pip install python-dateutil` → `import dateutil`) is the right
analogue. Adding a defensive `docs-cli` script alias is one line and
harmless but pointless when no one would type it. Renaming the command to
`docs-cli` is rejected outright. **Alternative A:** expose both. **Alternative
B:** rename the command to `docs-cli`. Recommended: stay `docs` only.
