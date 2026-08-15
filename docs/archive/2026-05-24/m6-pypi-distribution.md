# M6 — PyPI distribution as `docs-cli`

Lifecycle: archived
Role: milestone
Project: docs
Updated: 2026-08-14

Related:
- parent-of: archive/2026-05-24/m6-pypi-distribution-log.md
- child-of: plan.md
- implements: charter.md
- pairs-with: architecture.md
- pairs-with: cli.md
- pairs-with: test-strategy.md

Revision:
- 2026-08-14: M27 one-time body-link migration; body-link destinations repaired (destination tokens only)

## Overview

> **Scope reframe 2026-05-24 (operator decision).** M6 is now
> **preparation only** — the milestone delivered the packaging
> machinery (build backend, package shape, `install-skill` verb,
> runbook, README/architecture rewrites, GitHub repo) and closed at
> Phase 10. The **actual PyPI publish is M9** (see
> [m9-pypi-publish.md](../2026-05-25/m9-pypi-publish.md)), which runs post-M8 and
> ships M6 + M7 + M8 as one batched `1.3.0` release per
> [release-runbook.md](../../release-runbook.md). Read every "operator
> publishes / Phase 10 flips after publish" bullet below as
> superseded by M9; nothing in M6's scope is publish-dependent.

> **Scope refinement at Step 2 (operator-resolved 2026-05-23).** Two
> changes from the draft-time plan, both narrowing implementation
> scope:
>
> 1. **No CI workflows.** The original
>    `.github/workflows/{release,testpypi}.yml` Trusted-Publishing
>    design is parked as a future-iteration note in
>    [release-runbook.md](../../release-runbook.md). M6 ships via manual
>    `twine upload` driven by the operator.
> 2. **Operator-driven publish.** The implementation agent prepares
>    every artifact, exercises every code path locally, and stages a
>    ready-for-operator commit. The operator runs `twine upload` for
>    both TestPyPI and PyPI, then the post-publish tag/visibility/
>    release-create sequence per the runbook.
>
> Wherever this file's Phase 7 / 9 / 10 text describes workflow
> dispatches or automated publishes, read it as the original design.
> The Phase 9 and Phase 10 sections below have been rewritten to
> reflect the new scope.

- Milestone: M6 (first v1.1 milestone)
- Title: PyPI distribution as `docs-cli`
- Surface: a buildable, installable Python distribution **`docs-cli`** on
  PyPI; a real importable package (`docs_cli`) backing the existing executable;
  a one-shot **`docs install-skill`** verb that places the bundled Claude Code
  skill onto a host without requiring a repo clone; the corresponding repo,
  pyproject, README, and architecture rewiring.
- Status: ACTIVE (started 2026-05-23)

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
  during v1 development — `0.2.0-m2` was an in-development marker that
  was never bumped after M2, not a release version). `__version__` in
  `docs_cli/cli.py` follows.
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
  it into a `venv.EnvBuilder`-created throwaway venv, and exercises six
  sub-cases: (1) the wheel + sdist build cleanly via `python -m build`;
  (2) `pip install` of the wheel into the throwaway venv succeeds;
  (3) `docs --version` reports `1.1.0`; (4) `docs --help` lists every verb
  the in-tree parser lists (introspected via `_build_parser()`);
  (5) `docs install-skill --dest <tmp>` produces a tree byte-identical to
  the bundled source; (6) the installed `docs check <fixture-tree>` exits
  0 on a known-clean fixture. This is the milestone's most important
  test: a green in-tree suite *cannot* catch packaging failures (missing
  package data, bad entry point, broken wheel manifest).
- **The existing test suite remains green** after the relocation. Every
  `from docs import X` keeps working via a `conftest.py` shim that aliases
  `docs_cli.cli` as `docs` in `sys.modules` (OQ2 resolved 2026-05-23 — see
  Decisions; a mechanical import sweep is a clean follow-up commit, not
  M6 scope).
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
- **The repo and local checkout are renamed at Phase 1, before any publish
  work.** OQ3 resolved 2026-05-23 — see Decisions. The repo currently has
  **no git remote** (fresh local-only repo), so Phase 1 does **not** run
  `gh repo rename`. Instead it creates a new GitHub repo with
  `gh repo create ArtRichards/docs-cli --source=. --private --remote=origin`
  (private until v1.1 publishes; see Decisions for the public-flip plan),
  pushes the `m6/phases-1-4` branch, and moves the local checkout
  `mv ~/opt/docs ~/opt/docs-cli`. `~/CLAUDE.md` and the project-memory
  pointer file at
  `/home/user/.claude/projects/-home-user/memory/project_docs_cli.md`
  update to the new path in the same phase. The skill name (`docs`) and
  the command (`docs`) are unchanged.
- **No change to the on-disk Markdown convention.** `Project: docs` in every
  metadata block stays `docs`. The convention is independent of the
  distribution name; the project's identity in its own metadata is its
  long-standing name, not its packaging label.

### Deliverables

- [x] `pyproject.toml`: `name = "docs-cli"`, `version = "1.1.0"`,
      `[build-system]` (hatchling), `[project.scripts] docs =
      "docs_cli.cli:main"`, `[project.urls]`, package data for the bundled
      skill. Old `keywords`, `classifiers`, `authors`, `license`, optional
      `[dev]` extras preserved. (Classifiers also bumped Alpha → Beta + 3.13.)
- [x] `src/docs_cli/__init__.py` — re-exports `main` from `cli`
      (lazy via `__getattr__` to avoid the `runpy`
      "found in sys.modules" warning under `python -m docs_cli.cli`).
- [x] `src/docs_cli/cli.py` — the relocated `bin/docs`, byte-identical
      module-body content except for the M6 additions (`__version__ =
      "1.1.0"`, `--version` global flag, `install-skill` subparser +
      `_cmd_install_skill` handler, the module docstring update).
- [x] `src/docs_cli/skill/SKILL.md` + `src/docs_cli/skill/references/{convention,cli}.md`
      — relocated from `skills/docs/` (per OQ4). Top-level
      `skills/docs/` is gone.
- [x] `bin/docs` — removed (per OQ5). Contributors run
      `pip install -e ".[dev]"`; the `docs` entry point lands on PATH
      directly. Every M1-M5 doc that referenced `bin/docs` swept in
      Phases 5–7.
- [x] New verb `docs install-skill [--dest DIR] [--copy|--symlink] [--force]`
      (+ `--quiet`) implemented in `cli.py`; default dest
      `~/.claude/skills/docs/`; idempotent byte-identical no-op; `--force`
      overwrites; `--symlink` rejected from wheel installs via
      site-packages-ancestor heuristic; exit codes 0/2; surface specified
      in `cli.md`.
- [x] `tests/test_packaging.py` — 25 tests grouped A-F (Phase 2);
      builds wheel in tmp_path, installs into a `venv.EnvBuilder` venv,
      exercises every install-skill code path, runs installed `docs check`
      against the minimal fixture.
- [x] `tests/conftest.py` — drops `SourceFileLoader`; inserts `src/`
      on sys.path; aliases `docs_cli.cli` as `docs` in `sys.modules`
      (OQ2). `docs_script` fixture retained (re-pointed at
      `src/docs_cli/cli.py`) since ~70 test_cli_*.py invocations depend
      on it — see Phase 5 log issues/decisions for the deviation.
- [x] `tests/test_skill.py` — `SKILL_DIR` repath, failure-message
      update, docstring update, and verb-extraction regex widened
      to `[a-z][a-z-]*` so `install-skill` matches.
- [x] `tests/test_skill_refs.py` — `BUNDLE_DIR` repath + resync hints
      updated.
- [ ] ~~`.github/workflows/release.yml`~~ **Scope-refined out at Step 2
      (operator-resolved): NO CI workflows.** M6 ships via manual
      `twine upload` driven by the operator per `docs/release-runbook.md`.
      Trusted-Publishing path parked as a future-iteration note.
- [ ] ~~`.github/workflows/testpypi.yml`~~ **Scope-refined out at Step 2.**
      Same reason as above; operator runs `twine upload --repository
      testpypi dist/*` manually.
- [x] `docs/release-runbook.md` — Status: active; concrete `twine`
      command list for Pre-flight (impl) / TestPyPI rehearsal (operator)
      / real PyPI publish (operator) / post-release (operator).
- [x] `README.md` — `pip install docs-cli` primary install; `docs
      install-skill` for the skill; `git clone` documented for
      contributors; absolute github.com URLs throughout (Q6); M6 row
      added; v1.1 release notes paragraph.
- [x] `docs/architecture.md` — Shape diagram redrawn for `src/docs_cli/`;
      Sibling-artifact rewritten to describe wheel-package-data shipment;
      Install + Development-setup sections rewritten for `pip install
      docs-cli` (end users) + `pip install -e ".[dev]"` (contributors).
- [x] `docs/cli.md` — `install-skill` section added between `touch`
      and `migrate`; global `--version` added to the flags list.
- [x] `docs/charter.md` — `## Distribution` paragraph added.
- [x] `docs/plan.md` — `## v1.1` section added with M6 as the first
      milestone; the parked `[vocabulary] add_fields` allowlist
      question remains as a separate v1.1 entry, unrelated to M6.
      (Landed at Phase 1.)
- [x] `docs/status.md` — M6 added to the milestone table; `Current
      milestone` rewritten; reading-order updated; "Watch out for" /
      verify-environment sweep replaced `bin/docs` with the package
      layout. (Landed at Phases 1, 5, 6, 7, 9, 10.)
- [x] `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
      regenerated in lockstep (continuously through every phase).
- [x] GitHub repo **created** at `ArtRichards/docs-cli` (private until
      v1.1 publishes — see Decisions); `m6/phases-1-4` pushed;
      local checkout moved `~/opt/docs` → `~/opt/docs-cli`;
      `/home/user/.claude/projects/-home-user/memory/project_docs_cli.md`
      and `MEMORY.md` updated to the new path. (Phase 1 work.)
- [ ] GitHub repo flipped from private to public at Phase 10,
      immediately before / coincident with the first PyPI publish —
      **operator-executed** per `release-runbook.md`.
- [ ] PyPI release **1.1.0** published; install from PyPI in a
      throwaway venv exercised — **operator-executed**; impl agent
      built the artifacts at Phase 9 and ran the local-wheel smoke
      against the same venv shape.

## Current state analysis (snapshot at milestone kickoff, 2026-05-23)

_Captured before Phase 1; historical. Post-milestone state lives in the
Milestone-completion summary at the bottom of this file._

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

The ten phases follow the methodology in [status.md](../../status.md). Because M6
adds a small code surface (one new verb) **and** restructures the repo
**and** introduces a wheel-build pathway, the phases bias toward the
RED→GREEN cycle running against `tests/test_packaging.py` — the suite that
can only pass when the wheel actually builds and the entry point actually
works.

### Phase 1: Define Contract (+ identity rename)

- **Objective:** Declare the M6 surface **and adopt the new identity
  before any publishing work**. Promote this milestone from `draft` to
  `active`; the milestone-setup OQ resolutions are already folded into
  Decisions at milestone-setup time (2026-05-23). Phase 1 then carries
  the GitHub-repo create + local-checkout move that OQ3 sequenced here.
  No packaging surface or new verb stubs implemented; no Python relocated.
- **Files (text/docs work):**
  - `docs/m6-pypi-distribution.md` — flip `Status: draft` → `active`,
    bump `Updated:`. (OQ2–OQ5 resolutions are already in Decisions.)
  - `docs/m6-pypi-distribution-log.md` — phase-progress skeleton; Phase 1
    commit logged.
  - `docs/plan.md` — add a `## v1.1` section; M6 listed as first v1.1
    milestone; the parked `[vocabulary] add_fields` allowlist question
    stays where it is, as a separate v1.1 entry.
  - `docs/status.md` — `Current milestone` rewritten; M6 added to the
    milestone table as _in flight_; "Next action" replaced (mirrors how
    M1–M5 transitions wrote their in-flight state). The "Watch out for"
    block keeps its `bin/docs` reference unchanged at Phase 1 — that
    sweep is Phase 7 work.
  - `docs/architecture.md` — `Updated:` bumped; the Shape/Install
    sections are **not** rewritten yet (that is Phase 7 work after the
    packaging surface lands at Phase 6); a one-line forward-pointer note
    is acceptable but not required.
  - `docs/cli.md` — drop nothing yet; `docs install-skill` is added to
    cli.md at Phase 6 when the verb is implemented (mirroring M4's
    Phase-1 stub registration). Phase 1 may add a short forward-pointer
    paragraph or defer entirely.
  - `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` regenerated
    in lockstep so the two new M6 docs appear.
- **Identity-rename actions (the new Phase 1 scope, executed in order
  after the text-work commits land):**
  1. **Create the GitHub repo and push.**
     `gh repo create ArtRichards/docs-cli --source=. --private --remote=origin`
     (private until v1.1 publishes; flipped to public at Phase 10 — see
     Decisions). The repo currently has no remote — this is a fresh
     local-only history — so `gh repo rename` is not the right verb.
     Then `git push -u origin m6/phases-1-4`. (The branch stack is
     `m6/*`; pushing the branch is sufficient — `main` is pushed when
     the milestone merges.)
  2. **Move the local checkout.** `mv ~/opt/docs ~/opt/docs-cli`. **This
     changes the implementation agent's working directory mid-phase.**
     Do this as the **last** action of Phase 1; all subsequent phases
     and commands run from `/home/user/opt/docs-cli/`. The log records
     the move; the conductor resumes from the new path.
  3. **Update host pointers.** Edit `~/CLAUDE.md` — any line referencing
     `~/opt/docs` becomes `~/opt/docs-cli` (mostly the `docs CLI project`
     memory pointer line). Rename
     `/home/user/.claude/projects/-home-user/memory/project_docs.md` →
     `project_docs_cli.md` (slug + any in-file path references); update
     the corresponding line in
     `/home/user/.claude/projects/-home-user/memory/MEMORY.md`.
- **Order discipline.** The doc-text commit lands **first** (so the
  Phase 1 plan-changes commit is reviewable in isolation, on the current
  filesystem path), the remote-create + push commit lands **second**,
  and the local move is the **final** action — performed without a
  preceding commit, since the move itself is not a tracked change. The
  log entry for Phase 1 documents the post-move working directory.
- **Exit:** M6 is `active`; ruff/mypy/pytest still green (246 passed);
  `docs check docs/` exits 0; the INDEX snapshot matches; the new
  origin URL exists and `git ls-remote origin` returns the pushed
  branch; the local checkout is now at `/home/user/opt/docs-cli/`;
  `~/CLAUDE.md` + project-memory pointer file reflect the new path;
  **no code change has happened yet** inside the repo (no `src/`, no
  `pyproject.toml` edits, no `bin/docs` move).

### Phase 2: Write Tests (RED)

- **Objective:** Express every M6 requirement as a failing check — in code
  where possible (`tests/test_packaging.py`) and as a release-runbook
  checklist for the operations side that pytest cannot exercise. **No
  packaging surface authored; no files relocated.**
- **Files:**
  - `tests/test_packaging.py` — implement the six sub-cases:
    1. **Wheel builds.** `python -m build` produces
       `dist/docs_cli-1.1.0-py3-none-any.whl` + `dist/docs_cli-1.1.0.tar.gz`
       in a `tmp_path` dist dir.
    2. **Wheel installs.** A `venv.EnvBuilder`-created throwaway venv
       installs the wheel via `pip install` without errors.
    3. **`docs --version` prints `1.1.0`.** The venv's `docs` entry-point
       exits 0 and stdout matches the declared `__version__`.
    4. **`docs --help` lists every verb the in-tree parser lists.** Derive
       the expected verb set from the in-tree parser (the same
       `_build_parser()` introspection M5's `test_skill.py` uses), assert
       the wheel-installed `docs --help` output covers it. Catches a
       missing entry-point or a broken subparser registration.
    5. **`docs install-skill --dest <tmp>` produces the bundled tree.**
       `<tmp>/SKILL.md` and `<tmp>/references/{convention,cli}.md` exist
       and are byte-identical to the in-repo `src/docs_cli/skill/` source
       (or `skills/docs/`, depending on OQ4's resolution).
    6. **`docs check <fixture-tree>` exits 0.** The wheel-installed `docs`
       passes `check` against a known-clean fixture tree
       (`tests/fixtures/trees/packaging-clean/`).
  - `tests/test_skill.py`, `tests/test_skill_refs.py` — paths updated for
    the relocated skill source (OQ4 resolution).
  - `docs/release-runbook.md` — created as the manual-execution checklist
    walked at Phase 9 (TestPyPI) and Phase 10 (real PyPI). This is the
    operational analogue of M1–M4's "dogfood against a fixture tree" and
    M5's trigger-scenario checklist: bump version, regenerate INDEX, green
    quality gate, tag, watch the workflow, install from PyPI in a
    throwaway venv, smoke-test, write the GitHub release note.
- **Exit:** every new `test_packaging.py` sub-case fails for the right
  reason — no build backend (1), no entry point (2/3/4), no
  `install-skill` verb (5), no relocated package (everything). The
  existing 246-test suite remains green (nothing has moved yet); the
  release runbook is fully unsatisfied.

### Phase 3: Create Data/Fixtures

- **Objective:** Stage the fixtures the packaging tests need.
- **Files:**
  - `tests/fixtures/trees/packaging-clean/` — a tiny known-clean docs tree
    (one `.docs.toml`, one charter or status, one plan; **no errors**)
    used by sub-case 6 of `test_packaging.py`. Either a minimal hand-
    authored tree or a reuse of an existing M1–M4 fixture if one already
    qualifies as clean (e.g. `tests/fixtures/trees/minimal/`).
  - Nothing else — the wheel itself is built fresh in each test run; no
    pre-built artifact is checked in.
- **Exit:** every fixture a Phase-2 check references is present; running
  Phase 2's tests now fails on the *intended* reason (no build backend,
  no entry point, no `install-skill` verb) rather than on a missing
  fixture path.

### Phase 4: Run Tests (RED Baseline)

- **Objective:** Confirm every failure traces to the unimplemented
  packaging surface, not misconfiguration. **Step 1 (Phases 1–4) pauses
  here** per the project's TDD discipline.
- **Actions:** `.venv/bin/python -m pytest tests/ -q` — capture full
  output; confirm each `test_packaging.py` sub-case fails on the expected
  `ModuleNotFoundError` (`docs_cli`), wheel-build error (no
  `[build-system]`), `FileNotFoundError` (no relocated skill), or
  argparse error (no `install-skill` verb).
- **Exit:** `tests/test_packaging.py` is fully RED for the right reasons;
  M1–M5's 246 tests stay green; ruff/format/mypy clean tree-wide; the
  release-runbook checklist stands fully unsatisfied.

### Phase 5: Update Base Interfaces

- **Objective:** Restructure the repo. This is the largest single phase
  diff in M6 by line count, but it is mechanical: file moves, not logic
  changes.
- **Actions:**
  - `git mv bin/docs src/docs_cli/cli.py` — verify the `#!/usr/bin/env
    python3` shebang is dropped (no longer needed for an importable
    module), the `__version__` line is preserved, and the
    `if __name__ == "__main__": main()` guard is preserved (so the file
    is still directly runnable if a contributor wants).
  - Create `src/docs_cli/__init__.py` re-exporting `main` and
    `__version__`.
  - Relocate the skill per OQ4 (recommended: `git mv skills/docs
    src/docs_cli/skill`; the alternative — mirror — keeps the original
    path and adds a sync test).
  - Update `tests/conftest.py`: drop the `SourceFileLoader` block;
    replace with `from docs_cli import cli` and (per OQ2's recommended
    "alias" resolution) `sys.modules.setdefault("docs", cli)` so existing
    `from docs import X` imports keep working without test-file edits.
  - Update `tests/test_skill.py` and `tests/test_skill_refs.py` for the
    relocated skill paths.
  - Update `pyproject.toml`'s `extend-include` (ruff) and `files` (mypy)
    lists: `bin/docs` removed, `src/docs_cli/` added,
    `scripts_are_modules` deleted (no longer needed).
  - Resolve `bin/docs` per OQ5 (recommended: delete; alternative: keep a
    2-line shim).
- **Exit:** the existing 246-test suite is green again after the move;
  `ruff check` / `ruff format --check` / `mypy` clean tree-wide; `docs
  check docs/` exits 0 from the relocated module (via the conftest alias
  or an editable `pip install -e .` install); `tests/test_packaging.py`
  is still RED (no `[build-system]` yet, no `install-skill` yet).

### Phase 6: Implement Offline/Core Path

- **Objective:** Make the wheel build. Make the entry point work. Make
  `docs install-skill` work.
- **Files:**
  - `pyproject.toml` — `name = "docs-cli"`; `version = "1.1.0"` (drops the
    `-m4` milestone-suffix scheme; see Decisions); add `[build-system]`
    (hatchling, no plugins); add `[project.scripts] docs =
    "docs_cli.cli:main"`; add `[project.urls]` (Homepage, Repository,
    Issues); declare package data for `docs_cli/skill/**` so the bundled
    skill ships inside the wheel.
  - `src/docs_cli/cli.py` — bump `__version__` to `1.1.0`; implement the
    `install-skill` verb (argparse subparser, handler `_cmd_install_skill`,
    exit codes per `cli.md`); resolve the bundled skill via
    `importlib.resources.files("docs_cli") / "skill"`; `--copy` is the
    default action, `--symlink` is offered for contributor / editable
    installs, `--force` overwrites an existing destination.
  - `docs/cli.md` — `install-skill` section added: synopsis, flags
    (`--dest`, `--copy`/`--symlink`, `--force`), exit codes, idempotency
    note.
- **Exit:** `python -m build` succeeds in a temp dir; the built wheel
  contains the skill files (verifiable with `unzip -l`); every
  `tests/test_packaging.py` sub-case (1)–(6) passes; the full suite is
  green; `docs install-skill --dest <tmp>` produces a tree that
  `tests/test_skill.py`'s structural checks accept.

### Phase 7: Update Tool/Wrapper Layer

- **Objective:** Wire the release workflows and rewrite the install-facing
  docs around the new packaging.
- **Files:**
  - `.github/workflows/release.yml` — tag-triggered (`v*`); jobs: lint,
    test, `python -m build`, publish-to-PyPI via **Trusted Publishing**
    (OIDC; no API token in repo secrets — see Decisions).
  - `.github/workflows/testpypi.yml` — `workflow_dispatch` trigger;
    publishes to TestPyPI; same lint/test/build prelude. This is the
    dress-rehearsal workflow Phase 9 runs against.
  - `docs/release-runbook.md` — finalised: per-release checklist (bump
    version, regenerate INDEX, green quality gate, tag, watch the
    workflow, install from the published artifact in a throwaway venv,
    smoke-test, write the GitHub release note).
  - `README.md` — install section rewritten: `pip install docs-cli`
    first, `docs install-skill` second, `git clone` third (contributor
    path).
  - `docs/architecture.md` — Shape section updated for the new package
    layout (`src/docs_cli/cli.py`, `src/docs_cli/skill/`); Sibling-
    artifact note updated for the bundled-skill-in-wheel; Install
    section rewritten (`pip install docs-cli` + `docs install-skill`).
  - `docs/charter.md` — one-paragraph distribution note added; the
    charter currently assumes a `git clone` install.
- **Exit:** workflows lint cleanly (`actionlint` or `gh workflow view`);
  README and architecture install sections describe the wheel path
  correctly; the release runbook is reviewable end-to-end; the suite
  remains green.

### Phase 8: Run Tests (GREEN)

- **Objective:** Full suite green; quality gate clean tree-wide; the
  wheel builds and installs cleanly in CI.
- **Actions:** `.venv/bin/python -m pytest tests/ -q`;
  `.venv/bin/ruff check .`; `.venv/bin/ruff format --check .`;
  `.venv/bin/mypy`; `python -m build` (verifies the build outside the
  in-test path); `docs check docs/` exit 0; `docs index --root docs/
  --dry-run` idempotent.
- **Exit:** all green. Test count is 246 + the new `test_packaging.py`
  sub-cases (≈ 6 new tests). `tests/test_skill.py` and
  `tests/test_skill_refs.py` pass against the relocated skill source.

### Phase 9: Implement Online/Integration (local build + smoke)

> **Scope refinement at Step 2 (operator-resolved 2026-05-23):** the
> TestPyPI dress-rehearsal is **operator-executed**, not impl-agent
> executed. The impl agent prepares the artifacts and exercises every
> code path locally; the operator drives the actual TestPyPI and PyPI
> uploads following `docs/release-runbook.md`. The original
> Trusted-Publishing-via-GitHub-Actions design is parked as a
> future-iteration note in the runbook.

- **Objective (impl-side, Step 2):** Build a clean wheel + sdist,
  verify both with `twine check`, and exercise every CLI surface
  locally in a throwaway venv. Leave the artifacts and a handoff
  section in the log so the operator can publish without rerunning the
  build.
- **Actions:**
  - `rm -rf dist/ && .venv/bin/python -m build` — produces
    `dist/docs_cli-1.1.0-py3-none-any.whl` + `.tar.gz`.
  - `.venv/bin/pip install --quiet twine && .venv/bin/twine check dist/*`
    — both artifacts PASS.
  - Throwaway venv smoke (no PyPI involvement):
    `python3 -m venv /tmp/docs-local-smoke`;
    `/tmp/docs-local-smoke/bin/pip install dist/docs_cli-1.1.0-py3-none-any.whl`;
    then exercise `docs --version`, `docs --help`,
    `docs install-skill --dest /tmp/docs-local-smoke-skill`,
    re-run `install-skill` (no-op), `install-skill … --symlink`
    (exit 2 — wheel rejects), and `docs check tests/fixtures/trees/minimal/`
    (exit 0).
  - Append the wheel + sdist SHA256s, the `twine check` output, and
    every smoke command's expected/actual output to the Phase 9 log
    entry. Add a "OPERATOR ACTION REQUIRED" handoff section with the
    exact `twine upload` commands for TestPyPI and PyPI.
- **Exit:** wheel + sdist are byte-clean and twine-check-PASS; every
  install-skill code path is exercised; impl agent commits Phase 9 and
  hands off to the operator. **No PyPI upload from the impl agent.**

### Phase 10: Quality, Docs, Refactor (closeout, impl side)

> **Scope refinement at Step 2 (operator-resolved 2026-05-23):** the
> actual PyPI publish + repo-public-flip + tag-push + release-create
> are **operator-executed** AFTER this run completes. The impl agent's
> Phase 10 is closeout edits ONLY — status flip, milestone-doc
> checkboxes, log appendix, INDEX regen — staged as a
> ready-for-operator commit.

- **Objective:** Land the impl-side closeout edits so that the moment
  the operator's `twine upload` succeeds, the repo state already
  reflects the milestone shipping (modulo the operator-flipped
  `docs/status.md` M6-row date and the M6 row in `docs/plan.md`).
- **Actions:**
  - Tick every Phase Checklist box for Phases 5–9. **Phase 10 box
    stays unchecked** with a note `operator-executed; flip after
    publish lands`.
  - Append the milestone-completion summary at the bottom of this
    file, parallel to M1–M5's closeout — describe the shipped scope.
  - Append a Phase 10 log entry covering "what's ready: wheel built,
    smoke green, runbook fleshed out, branch ready to merge after
    operator publishes". Include the runbook-step appendix.
  - `docs/status.md`: M6 row → in-flight-with-edits; "Next action"
    rewritten to the operator's publish-driven closeout sequence
    (`twine upload`, tag push, repo visibility flip, gh release
    create). The M6 row will flip to "Complete (DATE)" by the
    operator after they publish.
  - `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
    regenerated in lockstep.
  - Quality gate green tree-wide.
- **Exit (impl side):** the branch is ready to merge once the operator
  publishes; every doc edit that depends on the publish date is
  flagged as operator-executed; the milestone summary is appended.
  Operator-side closing actions (PyPI upload, repo public flip, tag
  push, gh release create) are documented in `docs/release-runbook.md`
  and are NOT performed by the impl agent.

## Phase Checklist

- [x] Phase 1: Define Contract
- [x] Phase 2: Write Tests (RED)
- [x] Phase 3: Create Data/Fixtures
- [x] Phase 4: Run Tests (RED Baseline)
- [x] Phase 5: Update Base Interfaces
- [x] Phase 6: Implement Offline/Core Path
- [x] Phase 7: Update Tool/Wrapper Layer
- [x] Phase 8: Run Tests (GREEN)
- [x] Phase 9: Implement Online/Integration (local build + smoke; impl side)
- [x] Phase 10: Quality, Docs, Refactor — _closed 2026-05-24 as preparation only; publish moved to [M9](../2026-05-25/m9-pypi-publish.md)_

## Decisions

Key choices applying to this milestone (broader decisions live in
`vocab-adr.md` / `dual-status-adr.md`; M5's Decisions section is the
nearest precedent for milestone-local choices). The first block records
the milestone-setup OPEN QUESTIONS as resolved (the full
question / why-it-matters / recommendation text is preserved under
"OPEN QUESTIONS — resolved" below); the remaining items are durable
decisions independent of the OQ list.

- **OQ1 — the command name stays `docs`; no `docs-cli` script alias
  (RESOLVED 2026-05-23, operator-confirmed as recommended).** Users
  type `docs ...` exactly as they do today; the distribution name
  `docs-cli` appears only at install time (`pip install docs-cli`).
  This is the dominant pattern for the `<dist>-cli` family — `pip
  install python-dateutil` → `import dateutil`; `pip install docs-cli`
  → `$ docs ...`. No defensive `docs-cli` alias is added; if a future
  host has a PATH collision on `docs`, the resolution is local (rename
  the offender, or alias) rather than baked into the distribution.
- **OQ2 — `tests/conftest.py` aliases `docs_cli.cli` as `docs` in
  `sys.modules` (RESOLVED 2026-05-23, operator-confirmed as
  recommended).** Every existing `from docs import X` test import keeps
  working without edits; M6's diff stays scoped to packaging. A
  mechanical import sweep (`from docs import` → `from docs_cli.cli
  import`) across the ~18 test files is deferred as a clean
  follow-up commit, not M6 scope. The alias is set with
  `sys.modules.setdefault("docs", cli)` so a real `docs` module
  installed by some unrelated package (none exists today) would still
  win.
- **OQ3 — repo identity moves to `docs-cli` at Phase 1, before any
  publish work (RESOLVED 2026-05-23, operator override of the
  draft-time Phase-10 recommendation).** Rationale: adopt the new
  identity from the start so the publishing path debuts under the
  permanent name — no last-minute rename touching working-directory,
  remote URL, and host pointers in the same hour as the first PyPI
  release. **Important qualifiers** (Phase 1 plan reflects each):
  1. **No `gh repo rename`.** The repo currently has **no git remote** —
     this is a fresh local-only history. Phase 1 creates the GitHub
     repo from scratch:
     `gh repo create ArtRichards/docs-cli --source=. --private --remote=origin`
     then `git push -u origin m6/phases-1-4` (the m6/* branch
     stack — `main` is pushed later when the milestone merges).
  2. **Local checkout move:** `mv ~/opt/docs ~/opt/docs-cli` as the
     **final** action of Phase 1, since it changes the implementation
     agent's working directory mid-phase. The Phase 1 log entry
     records the post-move working directory; subsequent phases run
     from `/home/user/opt/docs-cli/`.
  3. **Host pointers update in lockstep:** `~/CLAUDE.md` (the
     `~/opt/docs` references become `~/opt/docs-cli`),
     `/home/user/.claude/projects/-home-user/memory/project_docs.md` →
     `project_docs_cli.md` (slug + in-file references), and
     `/home/user/.claude/projects/-home-user/memory/MEMORY.md` (the
     index line for the project memory).
  4. GitHub's automatic redirect from any future-old URLs is irrelevant
     here — there is no old URL to redirect from. The first publish in
     Phase 10 is therefore the **only** publish, from the **only** URL
     this project has ever had.
- **OQ3-implicit — repo visibility: private until first PyPI publish,
  then public (RESOLVED 2026-05-23, recommended).** Phase 1 creates
  the repo `--private`. Phase 10 flips it to public immediately before
  the `v1.1.0` tag push: `gh repo edit ArtRichards/docs-cli
  --visibility public --accept-visibility-change-consequences`. The
  rationale is conservative: between Phase 1 and Phase 10 the repo
  contains an in-flight v1.1 milestone, a `pyproject.toml` whose
  `name` flips mid-stream, and packaging surface that has not yet
  been TestPyPI-rehearsed — none of which benefits from public
  visibility before the first published artifact exists. Public is
  cheap to acquire (one `gh repo edit` call) and irreversible-ish to
  retract (existing public clones cannot be recalled). Public-from-
  day-one is offered as the alternative but is **not** recommended
  for M6.
- **OQ4 — skill source moves to `src/docs_cli/skill/`; top-level
  `skills/docs/` is removed (RESOLVED 2026-05-23, operator-confirmed
  as recommended).** Single source of truth under the package; the
  wheel ships exactly the directory the author edits; no sync surface
  to police. For contributors doing `pip install -e .`, the editable
  install means edits to `src/docs_cli/skill/SKILL.md` are immediately
  visible to `docs install-skill --symlink`. `tests/test_skill_refs.py`
  is updated to read the relocated source.
- **OQ5 — `bin/docs` is deleted; contributors `pip install -e ".[dev]"`
  once (RESOLVED 2026-05-23, operator-confirmed as recommended).**
  Retires the executable-script tooling overhead M6 was built to drop
  (`extend-include = ["bin/docs"]` in ruff, `scripts_are_modules =
  true` in mypy). The pip-install-editable flow gives the contributor
  the same `docs` binary the PyPI user gets — cleanest possible
  parity. Phase 7 sweeps every M1–M5 doc that still references
  `bin/docs` and the `status.md` "Watch out for" note that calls it
  out as a still-current gotcha.
- **The distribution name is `docs-cli`** — non-negotiable for v1.1
  PyPI publishing. The bare `docs` name on PyPI is squat-blocked as an
  empty placeholder (project page returns 200 with status `active`;
  simple index empty; JSON API 404). Recovering it would require a PEP
  541 abandoned-project request — multi-week, uncertain. **No PEP 541
  transfer is attempted in M6**; `docs-cli` is verified available and
  is descriptive enough that the bare-name squat is not a UX problem
  (users type `docs ...` regardless).
- **The version jumps from `0.2.0-m2` to `1.1.0`, dropping the
  milestone-suffix scheme.** `pyproject.toml`'s declared version is
  stale (`0.2.0-m2`; v1 shipped at M5 without bumping the package
  version because nothing was being published). M6 publishes, so the
  version is now consequential. The scheme transitions: `1.0.0` is
  implicit (v1 reached completion at M5 but was never released to
  PyPI); M6 ships v1.1 because it changes the install story
  observably (`pip install docs-cli` + `docs install-skill`).
  `__version__` in `docs_cli/cli.py` follows.
- **The single-file-vs-package question stays parked, but the file is
  relocated.** M6 needs an importable module to wire
  `[project.scripts]`, so `bin/docs` becomes `src/docs_cli/cli.py`.
  **The ~2,500 lines stay in one file.** Per-verb splitting into
  sub-modules is a separate refactor; it would inflate M6 by an order
  of magnitude with no packaging benefit. The deeper question stays
  parked.
- **The skill ships inside the wheel.** A PyPI user must get the same
  skill behaviour a `git clone` user gets, or PyPI distribution is
  half-built. The skill files are package data under
  `src/docs_cli/skill/`; a new `docs install-skill` verb places them on
  the host. No `setup.py install`-style hook, no `post_install`
  script — these are deprecated and do not survive `pip install --user`
  / `pipx` anyway. An explicit verb is preferable: the user runs it,
  sees the destination, confirms the copy.
- **`docs install-skill` defaults to `--copy`, not `--symlink`.** A
  wheel installed via `pip` may live anywhere — including read-only
  mounts, containers, or zip-imported eggs — and a symlink from
  `~/.claude/skills/docs` into that location is fragile. `--copy` is
  the safe default; `--symlink` is offered for the contributor case
  (it symlinks the source directory of an editable `pip install -e .`
  install into the skills dir). `--force` overwrites an existing
  destination; without `--force`, an existing non-identical directory
  is an error. The verb is idempotent: re-running on an unchanged
  install is a no-op exit 0.
- **Trusted Publishing (OIDC), not API tokens.** No long-lived PyPI
  token in repo secrets; the GitHub Action authenticates to PyPI via
  OIDC. One configuration step on the PyPI side: register the Trusted
  Publisher binding for `docs-cli` against the `docs-cli` GitHub repo
  on the `release.yml` workflow. Standard for new projects.
- **TestPyPI rehearsal before every real release.** The Phase 9
  dry-run via TestPyPI is part of the runbook, not optional. The cost
  is one workflow run and a throwaway venv; the upside is that the
  dress rehearsal catches name typos, missing package-data globs, bad
  classifier values, and rendering errors in the README *before* they
  hit pypi.org/project/docs-cli/ where they cannot be deleted, only
  yanked.
- **`hatchling` as the build backend, no plugins.** It is the modern
  pythonic default, ships with the `build` tool's typical setup, and
  needs no plugin to bundle package data the way M6 needs. No reason
  to reach for `setuptools` (legacy semantics) or `flit` (less
  flexibility around `[project.scripts]`).

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
.venv/bin/python -m pytest tests/test_packaging.py -v    # in-tmpvenv install + run
```

Plus the M6-specific dogfood gate at Phase 9 (TestPyPI) and Phase 10
(real PyPI): walk `docs/release-runbook.md` end-to-end against the
published artifact.

Expected at Phase 4: M1–M5's 246 tests green; every
`tests/test_packaging.py` sub-case RED for the intended reason
(`ModuleNotFoundError`, no `[build-system]`, no entry point, no
`install-skill` verb); the release runbook fully unsatisfied. Expected
at Phase 8/10: all commands green, packaging tests included; the
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
- [ ] The GitHub repo `ArtRichards/docs-cli` exists and is public; the
      local checkout is at `~/opt/docs-cli/`; `~/CLAUDE.md` and the
      project-memory pointer file reflect the new path; the
      `Repository:` URL in `pyproject.toml` matches.
- [ ] `docs/status.md` reflects M6 → Complete and the project as
      v1.1-in-progress.
- [ ] `docs/m6-pypi-distribution-log.md` contains a milestone-completion
      summary.

## OPEN QUESTIONS

_All milestone-setup OQs resolved 2026-05-23._ Each resolution is
recorded as a Decision in the "Decisions" section above; the full
question, why-it-matters, and recommendation text is preserved under
"OPEN QUESTIONS — resolved" below with a **RESOLVED** line at the head
of each. This mirrors M5's milestone-setup precedent.

## OPEN QUESTIONS — resolved

_All five milestone-setup questions were triaged against [plan.md](../../plan.md)
and the M1–M5 precedent and operator-confirmed on 2026-05-23. Each
resolution is recorded as a Decision in the "Decisions" section above
(OQ1–OQ5). The full question, why-it-matters, and recommendation text is
preserved here as the historical record; a **RESOLVED** line at the head
of each gives the verdict._

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

### OQ2 — Test import shape: alias `docs_cli.cli` as `docs`, or rewrite every test?

**RESOLVED (operator-confirmed 2026-05-23) — alias `docs_cli.cli` as
`docs` in `tests/conftest.py`.** Approved as recommended. A mechanical
import sweep across the ~18 test files is deferred as a clean follow-up
commit, not M6 scope. See the OQ2 Decision above.

**Question.** After `bin/docs` becomes `src/docs_cli/cli.py`, should
`tests/conftest.py` alias the new module as `docs` in `sys.modules` —
preserving every existing `from docs import X` import in the ~18 test
files — or should every test be mechanically rewritten to
`from docs_cli.cli import X`?

**Why it matters.** It decides M6's blast radius. The alias keeps the
diff narrowly scoped to packaging — one `conftest.py` change, zero
test-file churn. The rewrite is mechanical but touches every test file
that imports from the executable (a ~150-line import-edit sweep
unrelated to the packaging story), and conflates two changes
(packaging + import-style sweep) in the same milestone.

**Recommended answer.** **Alias.** `conftest.py` does `from docs_cli
import cli; sys.modules.setdefault("docs", cli)`, and every existing
`from docs import X` keeps working. The rewrite is a clean follow-up
sweep the team can do post-M6 in a single mechanical commit,
separately reviewable. **Alternative:** full rewrite — clearer
long-term, but expands M6's blast radius unnecessarily.

### OQ3 — Repo rename: when, and how invasive?

**RESOLVED (operator override of recommendation 2026-05-23) — adopt
the new identity at Phase 1, before any publishing work.** The operator
overrode the draft-time Phase-10 recommendation. Important qualifiers:
the repo currently has **no git remote**, so Phase 1 does **not** run
`gh repo rename` — it runs `gh repo create ArtRichards/docs-cli
--source=. --private --remote=origin` to create the repo from scratch
and `git push -u origin m6/phases-1-4` to land the branch. The
local checkout move `mv ~/opt/docs ~/opt/docs-cli` is the final action
of Phase 1, and subsequent phases run from the new path. `~/CLAUDE.md`
and the project-memory pointer (and MEMORY.md index line) update in
the same phase. See the OQ3 Decision above for the full sequencing and
the OQ3-implicit Decision for the private→public visibility plan.

**Question.** When does the GitHub repo rename from `docs` to
`docs-cli` (and the local checkout move from `~/opt/docs` to
`~/opt/docs-cli`) happen — at Phase 1 (matches the new identity from
the start) or at Phase 10 (after the first PyPI publish succeeds)?

**Why it matters.** The rename touches the git remote URL, the local
filesystem path, `~/CLAUDE.md`'s `~/opt/docs` references, and the
project-memory pointer file. Doing it early matches the new identity
from the start but runs the first publish from a freshly-renamed repo
(two unknowns interacting); doing it late keeps the publishing path
isolated for its debut. GitHub provides automatic redirects from the
old URL for the foreseeable future, so the rename does not break
clones or fetches in flight regardless of timing.

**Recommended answer (drafted above; overridden by the operator).**
**Rename at Phase 10**, after the first PyPI publish succeeds.
Sequence: tag and publish from the still-named `docs` repo, confirm
the PyPI artifact works, *then* rename the GitHub repo (`gh repo
rename docs-cli`) and the local checkout
(`mv ~/opt/docs ~/opt/docs-cli && git -C ~/opt/docs-cli remote
set-url origin git@github.com:<owner>/docs-cli.git`). `~/CLAUDE.md`
and the project-memory pointer file update at the same time.
**Alternative (chosen by the operator):** rename at Phase 1 —
matches the new identity from the start but bundles two unknowns.
The "two unknowns" objection is moderated by the fact that the
publishing path is itself only rehearsed against TestPyPI at Phase
9 before the real PyPI publish at Phase 10, so the rename runs many
phases before the first publish is even attempted.

### OQ4 — Bundled skill layout: move into `src/docs_cli/skill/`, or mirror from `skills/docs/`?

**RESOLVED (operator-confirmed 2026-05-23) — move the skill source
into `src/docs_cli/skill/` and remove the top-level `skills/docs/`.**
Approved as recommended. `tests/test_skill_refs.py` is updated to read
the relocated source. See the OQ4 Decision above.

**Question.** Should the skill source relocate fully — `git mv
skills/docs src/docs_cli/skill` so there is a single source of truth
under the package — or stay at `skills/docs/` with a build hook /
lockstep test that mirrors it into `src/docs_cli/skill/` for the wheel
build?

**Why it matters.** It decides whether the skill has one path or two.
A move is the simplest possible state: one file, one path, the wheel
ships exactly the directory the author edits. A mirror preserves the
existing top-level `skills/docs/` path but introduces a sync surface
that a lockstep test must police — exactly the shape M5's
`tests/test_skill_refs.py` already enforces for `convention.md` /
`cli.md`, so the precedent for "mirror with lockstep test" exists.

**Recommended answer.** **Move** (and remove `skills/docs/`). A single
source of truth is preferable to a mirror when nothing actively needs
the old path. For contributors doing `pip install -e .`, the editable
install means edits to `src/docs_cli/skill/SKILL.md` are immediately
visible to `docs install-skill --symlink`. The README and architecture
docs point at the new path (Phase 7). M5's existing
`tests/test_skill_refs.py` is updated to read the relocated source.
**Alternative:** mirror — preserves the existing `skills/docs/` path
but introduces a sync surface and one more thing to maintain.

### OQ5 — `bin/docs`: delete, or keep as a thin shim?

**RESOLVED (operator-confirmed 2026-05-23) — delete `bin/docs`.**
Approved as recommended. Contributors run `pip install -e ".[dev]"`
once; the entry point lands on PATH. Phase 7 sweeps every M1–M5 doc
and the `status.md` "Watch out for" note that referenced `bin/docs`.
See the OQ5 Decision above.

**Question.** After `bin/docs` is relocated to `src/docs_cli/cli.py`,
should the `bin/docs` path disappear entirely, or remain as a 2-line
shim (`from docs_cli.cli import main; raise SystemExit(main())`) for
in-repo contributors who do not want to `pip install -e .`?

**Why it matters.** It decides the in-repo contributor's friction
floor. Delete means contributors **must** `pip install -e ".[dev]"`
to get a working `docs` command (it lands on PATH via the entry
point). A shim means `./bin/docs` keeps working without any install
step, but resurrects the original "executable script with no
extension" complexity (`extend-include = ["bin/docs"]` in ruff,
`scripts_are_modules = true` in mypy) that M6 was about to retire.
Also relevant: every M1–M5 doc and the existing `status.md` "Watch
out for" note refer to `bin/docs`; those references must update if
the path disappears.

**Recommended answer.** **Delete.** The pip-install-editable flow
(`pip install -e ".[dev]"`) is one command, standard for modern
Python work, and gives the contributor exactly the same `docs`
binary the PyPI user gets — the cleanest possible parity. The
README's contributor section is updated to spell this out. Every
doc reference to `bin/docs` is updated in lockstep (a Phase-7 edit
sweep). **Alternative:** keep the 2-line shim — preserves the
existing in-repo workflow without an install step, at the cost of
the executable-script tooling overhead M6 was about to retire.

## Milestone-completion summary

> **M6 complete 2026-05-24 as preparation only.** Phase 10 closed
> as part of the 2026-05-24 scope reframe: the actual PyPI publish
> is **[M9](../2026-05-25/m9-pypi-publish.md)**, which runs post-M8 and ships
> M6 + M7 + M8 as one batched `1.3.0` release per
> [release-runbook.md](../../release-runbook.md). The "Operator-side
> closeout work" sub-list at the bottom of this summary is
> superseded by M9 + the runbook — kept for historical context but
> not to be followed standalone.

M6 shipped the first PyPI release of `docs`. Concretely:

- **Distribution.** `docs-cli` 1.1.0 builds cleanly from the in-tree
  `pyproject.toml` (hatchling backend). Wheel + sdist both pass
  `twine check`. The `docs` console-script lands on PATH via
  `[project.scripts] docs = "docs_cli.cli:main"`.
- **Package shape.** `bin/docs` → `src/docs_cli/cli.py` (history
  preserved through `git mv`; module remains logically monolithic
  per the M6 Decision). `skills/docs/` → `src/docs_cli/skill/`; the
  skill ships inside the wheel as package data (5 files total in
  the wheel: `__init__.py`, `cli.py`, `skill/SKILL.md`, and the two
  bundled references).
- **New verb: `docs install-skill`.** Materialises the bundled
  Claude Code skill onto a host. `--dest` overrides the default
  `~/.claude/skills/docs/`; `--copy` (default) / `--symlink`;
  `--force` overwrites a non-identical existing destination;
  `--quiet` suppresses success messages. Idempotent
  (byte-identical destination → no-op exit 0). `--symlink` is
  rejected when running from a wheel install (site-packages
  ancestor heuristic). Exit codes: 0 success / no-op; 2 refusal.
- **Global `--version` flag.** `docs --version` prints `docs 1.1.0`.
- **Convention unchanged.** `Project: docs` stays `docs`; the
  on-disk Markdown convention, every existing verb, and the M5
  Claude Code skill all behave identically. Only the distribution
  name (`docs-cli`), the install path (`pip install`), and the
  skill's delivery vehicle (`install-skill` instead of `ln -s`)
  changed.
- **Test surface.** 271 tests pass (M1–M5: 246 + M5 skill: 10 +
  M6 packaging: 25). `tests/test_packaging.py` builds the wheel
  in a `tmp_path`, pip-installs it into a throwaway venv, and
  exercises every install-skill code path plus the installed
  `docs check` against the minimal fixture — the test no in-tree
  green run can replace. ruff, ruff format, mypy all clean
  tree-wide.
- **Operator runbook.** `docs/release-runbook.md` is the active
  per-release checklist. Manual `twine upload` for both TestPyPI
  and PyPI; the operator runs the publish, tag push, repo
  visibility flip, and `gh release create` after this commit
  lands. The Trusted-Publishing/OIDC alternative is preserved as
  a future-iteration note.

What's deliberately deferred:

- **CI publish workflows** (GitHub Actions Trusted Publishing).
  Scope-refined out of M6 per operator override. Lives on as a
  follow-up note in the runbook.
- **Per-verb module split.** `src/docs_cli/cli.py` remains a single
  ~2.5k-line module; M6 picked the minimum-viable package shape.
  Splitting is a non-packaging refactor any future milestone can
  take up.
- **`importlib.metadata` for `__version__`.** Hardcoded in both
  `cli.py` and `pyproject.toml` (Q1 decision). The metadata-based
  source-of-truth pattern is a follow-up.

Operator-side closeout work _(historical — superseded by M9, see
[m9-pypi-publish.md](../2026-05-25/m9-pypi-publish.md) + [release-runbook.md](../../release-runbook.md))_:

1. `twine upload --repository testpypi dist/*`; install from
   TestPyPI in a throwaway venv; smoke.
2. Replace `## 1.1.0 — UNRELEASED` in `CHANGELOG.md` with today's
   date; commit.
3. `twine upload dist/*` (real PyPI).
4. `gh repo edit ArtRichards/docs-cli --visibility public --accept-visibility-change-consequences`.
5. `git tag v1.1.0 && git push origin v1.1.0`.
6. `gh release create v1.1.0 --title "docs-cli 1.1.0" --notes "..."`.
7. Doc closeouts: M6 row in `status.md` → Complete (DATE); Phase 10
   checkbox in this file → checked; INDEX + fixture regenerated.

The above describes the M6-standalone publish that **never
happened**. The 2026-05-24 scope reframe moved the publish to M9
at version `1.3.0`, batched with M7 + M8. The M6 wheel + sdist in
local `dist/` from 2026-05-23 are not uploaded; M9 rebuilds at M8
ship time. See [release-runbook.md](../../release-runbook.md) for the
operative checklist.

