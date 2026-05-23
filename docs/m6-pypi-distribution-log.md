# M6 — Implementation Log

Status: active
Role: log
Project: docs
Updated: 2026-05-23

Related:
- child-of: m6-pypi-distribution.md
- pairs-with: status.md

## Implementation metadata

- Project: docs
- Milestone: M6 — PyPI distribution as `docs-cli`
- Started: 2026-05-23
- Progress: **Milestone-setup phase complete; awaiting Phase 1
  execution.** The task plan
  [m6-pypi-distribution.md](m6-pypi-distribution.md) is promoted from
  `draft` to `active`; M6 is the first v1.1 milestone. All five
  milestone-setup OPEN QUESTIONS are resolved 2026-05-23 (OQ1 command
  name stays `docs`; OQ2 conftest aliases `docs_cli.cli` as `docs`;
  OQ3 repo-identity moves at Phase 1 with the new-repo qualifier
  since the local repo has no remote yet; OQ4 skill source moves to
  `src/docs_cli/skill/`; OQ5 `bin/docs` is deleted). Resolutions are
  recorded as Decisions in the task plan. Phase 1 has **not** yet
  executed — Phase 1 in this revised plan also performs the
  identity-rename (new GitHub repo, local checkout move, host-pointer
  updates); the implementation agent must handle the working-directory
  move at the end of Phase 1 and log the post-move path. Packaging
  surface untouched, no Python relocation, no new test file.

(Note: doc-lifecycle status is in the front-matter `Status:` field above. This
section tracks milestone progress, which is distinct.)

## Milestone-setup open questions

Five questions were surfaced while authoring the task plan. **All five
are resolved 2026-05-23**, recorded as Decisions in the task plan, and
preserved in full (question, why-it-matters, recommendation, resolution)
under "OPEN QUESTIONS — resolved" in
[m6-pypi-distribution.md](m6-pypi-distribution.md). This log
summarises:

1. **Command name (OQ1) — RESOLVED 2026-05-23, operator-confirmed as
   recommended.** Stay `docs` only; no `docs-cli` script alias. The
   distribution name `docs-cli` appears only at install time.
2. **Test import shape (OQ2) — RESOLVED 2026-05-23, operator-confirmed
   as recommended.** `tests/conftest.py` aliases `docs_cli.cli` as
   `docs` in `sys.modules` so existing `from docs import X` imports
   keep working without test-file edits. A mechanical rewrite of the
   ~18 test files is deferred as a clean follow-up commit, not M6
   scope.
3. **Repo rename timing (OQ3) — RESOLVED 2026-05-23, operator
   override of the Phase-10 recommendation.** Adopt the new identity at
   Phase 1, **before** any publish work. The repo currently has no git
   remote (fresh local-only history), so Phase 1 runs
   `gh repo create ArtRichards/docs-cli --source=. --private
   --remote=origin` rather than `gh repo rename`. Then `git push -u
   origin m6/milestone-setup`; then `mv ~/opt/docs ~/opt/docs-cli` as
   the final action of Phase 1 — the implementation agent's working
   directory moves mid-phase, and subsequent phases run from
   `/home/user/opt/docs-cli/`. `~/CLAUDE.md` and the project-memory
   pointer file (and MEMORY.md index line) are updated in the same
   phase.
4. **OQ3-implicit — repo visibility — RESOLVED 2026-05-23,
   recommended.** Phase 1 creates the repo `--private`. Phase 10 flips
   it to public immediately before the `v1.1.0` tag push:
   `gh repo edit ArtRichards/docs-cli --visibility public
   --accept-visibility-change-consequences`. Public is cheap to
   acquire and effectively irreversible — defer it until the first
   published artifact exists.
5. **Bundled skill layout (OQ4) — RESOLVED 2026-05-23,
   operator-confirmed as recommended.** `git mv skills/docs
   src/docs_cli/skill` — a single source of truth under the package;
   the wheel ships exactly what the author edits. The top-level
   `skills/docs/` path disappears. `tests/test_skill_refs.py` is
   updated to read the relocated source.
6. **`bin/docs` after relocation (OQ5) — RESOLVED 2026-05-23,
   operator-confirmed as recommended.** Delete. Contributors run
   `pip install -e ".[dev]"` once and the `docs` entry point lands on
   PATH directly — same binary the PyPI user gets. Retires the
   executable-script tooling overhead (`extend-include`,
   `scripts_are_modules`) M6 was built to drop. Phase 7 sweeps every
   M1–M5 doc and the `status.md` "Watch out for" note that referenced
   `bin/docs`.

## Summary

Ship the project's first PyPI release. M6 publishes the CLI as
`docs-cli` on PyPI, relocates `bin/docs` to an importable package at
`src/docs_cli/cli.py`, ships the Claude Code skill inside the wheel as
package data, and adds one new verb — `docs install-skill` — that
materialises the bundled skill onto a host. A new
`tests/test_packaging.py` builds the wheel in a `tmp_path`, installs it
into a throwaway venv, and exercises the `docs` entry point against a
known-clean fixture tree — the test no in-tree green run can replace.
The release path is wired via GitHub Actions Trusted Publishing (OIDC)
to PyPI and TestPyPI; the latter is the Phase 9 dress rehearsal before
the Phase 10 real publish. The repo and local checkout move to
`docs-cli` at **Phase 1** — before any publishing work — per OQ3
(operator override of the draft-time Phase-10 recommendation): the
local repo has no remote, so Phase 1 creates a new GitHub repo at
`ArtRichards/docs-cli` (private until v1.1 publishes, then flipped to
public at Phase 10) and moves the local checkout
`~/opt/docs` → `~/opt/docs-cli`. The on-disk name, the PyPI
distribution, and the `Repository:` URL are all consistent from the
first commit forward. The on-disk Markdown convention is
unchanged — `Project: docs` stays `docs`.

## TDD Phase Progress

| Phase | Status | Date | Notes |
|---|---|---|---|
| 1. Define Contract (+ identity rename) | Pending | — | Promote M6 from `draft` to `active`; create this log; add a `## v1.1` section to `plan.md`; refresh `status.md` (M6 in flight); regenerate INDEX + snapshot. **Then perform the identity rename per OQ3**: `gh repo create ArtRichards/docs-cli --source=. --private --remote=origin`; `git push -u origin m6/milestone-setup`; `mv ~/opt/docs ~/opt/docs-cli` as the final action (subsequent phases run from the new path); update `~/CLAUDE.md`, `/home/user/.claude/projects/-home-user/memory/project_docs_cli.md`, and the MEMORY.md index line. No code change, no packaging surface. |
| 2. Write Tests (RED) | Pending | — | `tests/test_packaging.py` with the six packaging sub-cases; `tests/test_skill.py` + `tests/test_skill_refs.py` paths updated; `docs/release-runbook.md` created as the operations checklist. |
| 3. Create Data/Fixtures | Pending | — | `tests/fixtures/trees/packaging-clean/` (a known-clean docs tree) or reuse an existing M1–M4 fixture (e.g. `minimal/`) for sub-case 6. |
| 4. Run Tests (RED Baseline) | Pending | — | Confirm every `test_packaging.py` sub-case fails on the unimplemented packaging surface (no `[build-system]`, no entry point, no `install-skill`, no `docs_cli` module); existing 246 tests stay green; **session pauses here**. |
| 5. Update Base Interfaces | Pending | — | `git mv bin/docs src/docs_cli/cli.py`; `src/docs_cli/__init__.py` created; skill relocated per OQ4; `tests/conftest.py` updated per OQ2; `tests/test_skill.py` / `tests/test_skill_refs.py` paths updated; `pyproject.toml` ruff/mypy include lists updated; `bin/docs` resolved per OQ5. |
| 6. Implement Offline/Core Path | Pending | — | `pyproject.toml` build backend (hatchling) + `[project.scripts]` + `[project.urls]` + package-data; `__version__` → `1.1.0`; `docs install-skill` verb (handler, argparse subparser, `importlib.resources` lookup); `cli.md` updated. |
| 7. Update Tool/Wrapper Layer | Pending | — | `.github/workflows/release.yml` (Trusted Publishing); `.github/workflows/testpypi.yml`; `docs/release-runbook.md` finalised; `README.md` install section rewritten; `architecture.md` Shape/Install updated; `charter.md` distribution paragraph added. |
| 8. Run Tests (GREEN) | Pending | — | Full quality gate green tree-wide; `python -m build` succeeds outside the in-test path; `test_packaging.py` GREEN. |
| 9. Implement Online/Integration | Pending | — | TestPyPI publish via `testpypi.yml`; install from TestPyPI in a clean venv; walk every row of `docs/release-runbook.md`. |
| 10. Quality, Docs, Refactor | Pending | — | Flip GitHub repo to public (`gh repo edit ArtRichards/docs-cli --visibility public --accept-visibility-change-consequences`); tag `v1.1.0`; PyPI publish; runbook smoke against the real artifact; `status.md` → M6 Complete + v1.1 released; INDEX + snapshot regenerated; completion summaries appended. (The identity rename already landed at Phase 1.) |

## Current state analysis (snapshot at milestone kickoff, 2026-05-23)

_Captured before Phase 1; historical._

- **Codebase.** A single executable Python file at `bin/docs` (2,534
  lines; Python 3.11+; stdlib only). Eight verbs — `index`, `new`,
  `archive`, `mv`, `touch`, `check`, `list`, `migrate`. The Claude
  Code skill at `skills/docs/SKILL.md` (M5) with bundled spec
  references at `skills/docs/references/{convention,cli}.md`.
- **Tests.** 246 passing tests across 19 files (236 M1-M4 + 8 M5
  `test_skill.py` + 2 M5 `test_skill_refs.py`); `ruff` / `mypy` clean
  tree-wide; `bin/docs check docs/` exits 0; the dogfood snapshot
  matches the regenerated INDEX.md.
- **Install today.** `git clone` + symlink: `ln -s $PWD/bin/docs
  ~/bin/docs` and `ln -s $PWD/skills/docs ~/.claude/skills/docs`. No
  `pip install`. No wheel. No CI release.
- **`pyproject.toml` today.** `name = "docs"`, `version = "0.2.0-m2"`,
  classifiers, keywords, `[dev]` extras, ruff config with
  `extend-include = ["bin/docs"]`, mypy config with `scripts_are_modules
  = true`. **No `[build-system]`. No entry point. No `name =
  "docs-cli"`. The declared version is stale** (still `0.2.0-m2`; v1
  shipped at M5).
- **The PyPI name problem.** `pip install docs` fails — the project
  page `https://pypi.org/project/docs/` exists (HTTP 200, status
  `active`) but the simple index is empty and the JSON API returns
  404. The name is squatted as an empty placeholder. Recovering it
  would require a PEP 541 abandoned-project request to PyPI admins
  (multi-week, not guaranteed). **`docs-cli` is available** (simple
  index 404 at draft time) and is the chosen distribution name. No
  PEP 541 transfer attempted.
- **The parked single-file/package-split question.** `docs/status.md`'s
  "Watch out for" calls out "the deferred `bin/docs` single-file vs
  package split" as v1.1 scope. M4's Decisions parked it explicitly;
  M5 added no Python so it was untouched. **M6 forces a minimal
  resolution** because `[project.scripts]` requires a `module:function`
  entry point, not a path — so `bin/docs` must become an importable
  module *at some module path*. M6 picks the smallest move: relocate
  the single file to `src/docs_cli/cli.py` with a public `main()`;
  per-verb splitting stays parked.
- **How tests reach the script today.** `tests/conftest.py` uses
  `importlib.machinery.SourceFileLoader("docs", str(REPO_ROOT / "bin"
  / "docs"))` and registers the loaded module as `docs` in
  `sys.modules`, letting test files write `from docs import Doc,
  parse, ...`. After relocation the import is `from docs_cli import
  cli` (or `from docs_cli.cli import main, Doc, parse, ...`). The
  conftest can preserve the `docs` alias to avoid touching ~18 test
  files (OQ2's recommended resolution).
- **The skill's deploy path today.** `ln -s ~/opt/docs/skills/docs
  ~/.claude/skills/docs`. After M6, a PyPI user has no checkout to
  symlink from — the skill must reach the host via the wheel.
  Mechanism: `importlib.resources` reads the bundled
  `src/docs_cli/skill/`; `docs install-skill` materialises it under
  `~/.claude/skills/docs/`. The committed skill stays host-agnostic;
  the host-specific path is the install step.
- **v1.1 roadmap state.** `plan.md` carries one Open question — the
  post-v1 `[vocabulary] add_fields` allowlist — and no v1.1
  numbering. `status.md`'s "Next action: none — v1 is complete"
  needs to be replaced once M6 is accepted. **M6 is the first v1.1
  milestone**; numbering continues monotonically (M1–M5 → M6).

## Files to Create / Modify

| File | Action | Phase | Notes |
|---|---|---|---|
| `docs/m6-pypi-distribution.md` | Created (draft committed at HEAD) / Modify | 1, 10 | Promoted draft → active (Phase 1); milestone-completion summary appended (Phase 10). |
| `docs/m6-pypi-distribution-log.md` | Create | 1 | This log. |
| `docs/plan.md` | Modify | 1, 10 | Add `## v1.1` section with M6 (Phase 1); M6 → shipped (Phase 10). |
| `docs/status.md` | Modify | 1, …, 10 | M6 in flight (Phase 1); per-phase progress; M6 → Complete + v1.1 released (Phase 10). |
| `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` | Regenerate | 1, …, 10 | Lockstep; picks up new docs and `Updated:` bumps. |
| `pyproject.toml` | Modify | 5, 6 | ruff/mypy include lists updated for relocated layout (P5); `name`, `version`, `[build-system]`, `[project.scripts]`, `[project.urls]`, package data (P6). |
| `bin/docs` | Move / Delete | 5 | Relocates to `src/docs_cli/cli.py`; the path itself disappears or becomes a 2-line shim (per OQ5). |
| `src/docs_cli/__init__.py` | Create | 5 | Re-exports `main` and `__version__` from `cli`. |
| `src/docs_cli/cli.py` | Move from `bin/docs` | 5, 6 | Relocated content (P5); `__version__` bumped to `1.1.0` + `install-skill` verb (P6). |
| `src/docs_cli/skill/` | Move from `skills/docs/` | 5 | Per OQ4's recommended resolution; the wheel ships this as package data. |
| `tests/conftest.py` | Modify | 5 | Drop `SourceFileLoader`; load `docs_cli.cli` directly; alias as `docs` per OQ2. |
| `tests/test_skill.py` | Modify | 5 | Skill source path updated; verb-set check reads `docs_cli.cli._build_parser()`. |
| `tests/test_skill_refs.py` | Modify | 5 | Reference paths updated for the relocated `src/docs_cli/skill/references/`. |
| `tests/test_packaging.py` | Create | 2 | Six sub-cases — wheel builds; venv installs; `docs --version`; `docs --help`; `docs install-skill` produces the bundled tree; `docs check <fixture>` exits 0. |
| `tests/fixtures/trees/packaging-clean/` (or reused fixture) | Create / Reuse | 3 | Known-clean tree for `test_packaging.py` sub-case 6. |
| `docs/release-runbook.md` | Create | 2, 7 | Skeleton at P2 as the manual-execution oracle; finalised at P7 with the per-release checklist. |
| `docs/cli.md` | Modify | 6 | `install-skill` synopsis, flags, exit codes added. |
| `docs/architecture.md` | Modify | 7 | Shape, Sibling-artifact, Install sections updated for the new layout. |
| `docs/charter.md` | Modify | 7 | One-paragraph distribution note added. |
| `README.md` | Modify | 7 | Install section rewritten: `pip install docs-cli` first; `docs install-skill`; `git clone` third (contributor path). |
| `.github/workflows/release.yml` | Create | 7 | Tag-triggered (`v*`); Trusted Publishing to PyPI. |
| `.github/workflows/testpypi.yml` | Create | 7 | `workflow_dispatch`; publishes to TestPyPI for Phase 9 rehearsal. |
| GitHub repo + local checkout | Create + move | 1 | Per OQ3 (resolved 2026-05-23): `gh repo create ArtRichards/docs-cli --source=. --private --remote=origin` (no existing remote to rename); `git push -u origin m6/milestone-setup`; `mv ~/opt/docs ~/opt/docs-cli` as Phase 1's final action; `~/CLAUDE.md`, `project_docs_cli.md`, MEMORY.md updated. |
| GitHub repo visibility | Flip private → public | 10 | Per OQ3-implicit (resolved 2026-05-23): `gh repo edit ArtRichards/docs-cli --visibility public --accept-visibility-change-consequences`, sequenced immediately before the `v1.1.0` tag push. |
| PyPI 1.1.0 release | Publish | 10 | The actual shipping artifact. |

## Phase logs

_Phase logs are appended here as each phase completes — one `### Phase
N` section per phase, following the M1–M5 log format (Objective, Files
changed, Actions taken, Issues / decisions, Exit criteria)._
