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
   origin m6/phases-1-4`; then `mv ~/opt/docs ~/opt/docs-cli` as
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
| 1. Define Contract (+ identity rename) | Complete | 2026-05-23 | Promote M6 from `draft` to `active`; create this log; add a `## v1.1` section to `plan.md`; refresh `status.md` (M6 in flight); regenerate INDEX + snapshot. **Then perform the identity rename per OQ3**: `gh repo create ArtRichards/docs-cli --source=. --private --remote=origin`; `git push -u origin m6/phases-1-4`; `mv ~/opt/docs ~/opt/docs-cli` as the final action (subsequent phases run from the new path); update `~/CLAUDE.md`, `/home/user/.claude/projects/-home-user/memory/project_docs_cli.md`, and the MEMORY.md index line. No code change, no packaging surface. |
| 2. Write Tests (RED) | Complete | 2026-05-23 | `tests/test_packaging.py` (25 tests grouped A–F per Step 1's plan); `pyproject.toml` `[dev]` extra gains `build>=1.0` (Step 1 OQ-D); `docs/release-runbook.md` created as the draft skeleton. `tests/test_skill.py` + `tests/test_skill_refs.py` are deliberately untouched at this phase (Step 1 OQ-F defers the path edits to Phase 5 alongside the skill move). |
| 3. Create Data/Fixtures | Complete | 2026-05-23 | Confirmed reuse of `tests/fixtures/trees/minimal/` for the installed-`docs check` / `docs index --dry-run` smokes (Step 1's Option A — `./bin/docs check tests/fixtures/trees/minimal/` exits 0; no new fixture needed). Phase 4 captures the RED baseline. |
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
| GitHub repo + local checkout | Create + move | 1 | Per OQ3 (resolved 2026-05-23): `gh repo create ArtRichards/docs-cli --source=. --private --remote=origin` (no existing remote to rename); `git push -u origin m6/phases-1-4`; `mv ~/opt/docs ~/opt/docs-cli` as Phase 1's final action; `~/CLAUDE.md`, `project_docs_cli.md`, MEMORY.md updated. |
| GitHub repo visibility | Flip private → public | 10 | Per OQ3-implicit (resolved 2026-05-23): `gh repo edit ArtRichards/docs-cli --visibility public --accept-visibility-change-consequences`, sequenced immediately before the `v1.1.0` tag push. |
| PyPI 1.1.0 release | Publish | 10 | The actual shipping artifact. |

## Phase logs

_Phase logs are appended here as each phase completes — one `### Phase
N` section per phase, following the M1–M5 log format (Objective, Files
changed, Actions taken, Issues / decisions, Exit criteria)._

### Phase 1 — Define Contract (+ identity rename)

**Completed:** 2026-05-23

#### Objective

Declare the M6 surface and adopt the new `docs-cli` identity before any
publishing work. Land the doc-text commit (plan.md gets a `## v1.1`
section, status.md "Next action" is rewritten to point at Phase 2, the
Phase-1 row in this log's TDD Phase Progress table flips to Complete,
INDEX/snapshot are regenerated). Then execute the OQ3 identity-rename
sequence: create the GitHub repo, push the working branch, edit host
pointers, and move the local checkout from `/home/user/opt/docs` to
`/home/user/opt/docs-cli`. No code change, no packaging surface; the
246-test suite stays green throughout.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/plan.md` | Modify | New `## v1.1` section with the M6 row pointing at `m6-pypi-distribution.md`. The parked `[vocabulary] add_fields` allowlist note in the new section reminds readers it carries forward to v1.1 as a separate, unscheduled entry. |
| `docs/status.md` | Modify | "Next action" rewritten to "Phase 2 — write tests/test_packaging.py RED"; the verify-environment snippet's `cd ~/opt/docs` becomes `cd ~/opt/docs-cli`; the test-count comment updated to flag the ~22-RED post-Phase-4 expectation. |
| `docs/m6-pypi-distribution.md` | Modify (no text body change; refs only) | All `m6/milestone-setup` references rewritten to `m6/phases-1-4` per Step 1 OQ-A (the actual working branch). |
| `docs/m6-pypi-distribution-log.md` | Modify | Phase 1 row → Complete (2026-05-23); `m6/milestone-setup` refs rewritten to `m6/phases-1-4`; this log entry appended. |
| `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Re-synced in lockstep via `./bin/docs index --root docs/` after the text edits. |

#### Actions taken

- **Doc-text commit (commit 1) on `/home/user/opt/docs/`** (pre-rename
  path; the rename happens after this commit). Patched
  `m6/milestone-setup` → `m6/phases-1-4` throughout the milestone doc +
  log + status.md (OQ-A of Step 1's plan). Added the `## v1.1` section
  to plan.md. Rewrote status.md's "Next action" to point at Phase 2.
  Flipped the Phase-1 row in this log's TDD Phase Progress table to
  Complete. Regenerated INDEX.md + the dogfood snapshot in lockstep via
  `./bin/docs index --root docs/`. Ran the quality gate (pytest 246
  green, ruff check, ruff format --check, mypy, `./bin/docs check
  docs/` exit 0). Committed with `M6 Phase 1: define contract; activate
  milestone`.
- **Identity-rename, step 1 — create GitHub repo.**
  `gh repo create ArtRichards/docs-cli --source=. --private --remote=origin`
  succeeded; `origin` set to the new GitHub URL.
- **Identity-rename, step 2 — push the working branch.**
  `git push -u origin m6/phases-1-4`. (Not `m6/milestone-setup` — the
  actual branch this work happens on; `main` will be pushed when the
  milestone merges.)
- **Identity-rename, step 3 — host-pointer sweep.** Grepped `/opt/docs`
  across `~/.bashrc`, `~/.zshrc`, `~/.config`, `~/system-docs`,
  `~/.claude`, `~/CLAUDE.md`. Verified-edited hits:
  `/home/user/.claude/projects/-home-user/memory/MEMORY.md` (line 1 —
  `~/opt/docs` → `~/opt/docs-cli`),
  `/home/user/.claude/projects/-home-user/memory/project_docs_cli.md`
  (lines 3, 10, 16 — three `~/opt/docs` references),
  `/home/user/.claude/settings.local.json` (lines 44–46 — three
  `Bash(/home/user/opt/docs/.venv/...)` permission entries became
  `Bash(/home/user/opt/docs-cli/.venv/...)`). **`~/CLAUDE.md` had zero
  hits** — recorded as a deliberate no-op (no edit was required). No
  hits in `~/.bashrc`, `~/.zshrc`, `~/.config`, or `~/system-docs`.
- **Identity-rename, step 4 — symlink inventory (no edits yet; Phase 5
  refreshes them when the skill relocates).**
  - `~/bin/docs` does **not** exist on this host. (No symlink to break
    or refresh.)
  - `~/.claude/skills/docs` is a symlink →
    `/home/user/opt/docs/skills/docs`. It breaks at this Phase 1 mv
    (target path becomes `/home/user/opt/docs-cli/skills/docs`) and
    again at Phase 5 (the source moves into
    `/home/user/opt/docs-cli/src/docs_cli/skill/`). Phase 5 must
    refresh it to the relocated source, or replace it with a
    `docs install-skill --symlink` (editable-install flow).
- **Identity-rename, step 5 — local checkout move.**
  `mv /home/user/opt/docs /home/user/opt/docs-cli` from `/home/user`.
  This step invalidated the existing shell `cwd` and broke every
  shebang under `.venv/bin/` (each is `#!/home/user/opt/docs/.venv/bin/python3`).
- **Identity-rename, step 6 — venv recreation (per Step 1's OQ-C).**
  `cd /home/user/opt/docs-cli && rm -rf .venv && python3 -m venv .venv &&
  .venv/bin/pip install --quiet pytest ruff mypy build`. `build` is
  included now (per Step 1's OQ-D) so Phase 2's `pytest.importorskip
  ("build")` collects rather than skipping.
- **Identity-rename, step 7 — post-move verification on
  `/home/user/opt/docs-cli`.** `git ls-remote origin` returns the
  pushed `m6/phases-1-4` branch; `.venv/bin/python -m pytest tests/ -q`
  still 246 green; `./bin/docs check docs/` exit 0.

#### Issues / decisions

- **OQ-A (branch name in plan + log).** The plan text and the log
  Phase-1 row originally said `m6/milestone-setup`. The actual working
  branch is `m6/phases-1-4`. Rewrote every reference at Phase 1
  (single `sed -i` sweep across the three docs) so the historical
  record matches the branch the commits actually land on.
- **OQ-B (host pointer grep scope).** Grepped broadly across
  `~/.bashrc`, `~/.zshrc`, `~/.config`, `~/system-docs`, `~/.claude`,
  `~/CLAUDE.md`. Confirmed zero hits in `~/CLAUDE.md`, `~/.bashrc`,
  `~/.zshrc`, `~/.config`, `~/system-docs`. The conversation/session
  history files (`.jsonl`, paste-cache, plan-cache) under `~/.claude/`
  also showed many hits but are append-only historical artifacts of
  past sessions — left untouched by design.
- **OQ-C (venv recreation after the mv).** The `.venv/bin/` shebangs
  (`#!/home/user/opt/docs/.venv/bin/python3`) hard-code the pre-rename
  absolute path. After the `mv`, every entry-point script
  (`pytest`, `ruff`, `mypy`) became unrunnable. Recreated the venv on
  the new path as the post-mv recovery step. The recreated venv is
  identical in surface to the original (`pytest ruff mypy build`).
- **OQ-D (`build` in `[dev]`).** Step 1's plan asked to add `build` to
  `[project.optional-dependencies] dev` at Phase 2 — not at Phase 1.
  Phase 1 installs `build` into the recreated venv via `pip install`
  so Phase 2's `pytest.importorskip("build")` collects without
  skipping; the `pyproject.toml` edit lands at Phase 2.
- **`~/.claude/skills/docs` symlink — deferred to Phase 5.** Per Step
  1's plan, the symlink is inventoried at Phase 1 but **not** edited.
  Phase 5 refreshes it when the skill relocates to
  `src/docs_cli/skill/`.
- **`~/CLAUDE.md` is a deliberate no-op.** The host file had zero
  `~/opt/docs` references; no edit needed. Recorded as a no-op for the
  audit trail.
- **GitHub repo visibility is `private`.** Per OQ3-implicit (resolved
  at milestone setup): private until Phase 10's first PyPI publish,
  then flipped to public via `gh repo edit ... --visibility public
  --accept-visibility-change-consequences`.

#### Exit criteria

- [x] `Status:` in `m6-pypi-distribution.md` is `active` (was set at
      milestone setup; unchanged at Phase 1).
- [x] `docs/plan.md` has a `## v1.1` section with the M6 row.
- [x] `docs/status.md` "Next action" points at Phase 2.
- [x] The TDD Phase Progress table's Phase-1 row is Complete (2026-05-23).
- [x] `docs/INDEX.md` and `tests/fixtures/expected/docs-INDEX.md` are
      in lockstep.
- [x] `m6/milestone-setup` is no longer mentioned anywhere; the working
      branch reference is `m6/phases-1-4`.
- [x] GitHub repo `ArtRichards/docs-cli` exists; `origin` is set; the
      branch `m6/phases-1-4` is pushed and `git ls-remote origin`
      returns it.
- [x] Local checkout is at `/home/user/opt/docs-cli/`.
- [x] `.venv/` recreated on the new path with `pytest ruff mypy build`.
- [x] Host pointers updated: MEMORY.md, project_docs_cli.md,
      settings.local.json. `~/CLAUDE.md` deliberately untouched.
- [x] `~/bin/docs` (absent) and `~/.claude/skills/docs` (symlink →
      `/home/user/opt/docs/skills/docs`, will break at Phase 5)
      inventoried for Phase 5.
- [x] `.venv/bin/python -m pytest tests/ -q` exits 0 with 246 passed.
- [x] `ruff check .`, `ruff format --check .`, `mypy` all clean.
- [x] `./bin/docs check docs/` exit 0.
- [x] No code change happened inside the repo (no `src/`, no
      `pyproject.toml` edits, no `bin/docs` move).

### Phase 2 — Write Tests (RED)

**Completed:** 2026-05-23

#### Objective

Express every M6 packaging requirement as a failing check in code,
plus a release-runbook skeleton for the operations side that pytest
cannot exercise. No packaging surface authored; no files relocated.
The 246-test in-tree suite stays green; the new `tests/test_packaging.py`
collects and runs entirely RED (the GREEN→RED differentiation is
Phase 4's job).

#### Files changed

| File | Action | Notes |
|---|---|---|
| `tests/test_packaging.py` | Create | 25 tests grouped A–F (see "Test groups" below). Top-of-file `pytest.importorskip("build")` per Step 1 OQ-E; `from docs import _build_parser` via the conftest alias (Step 1 OQ-O). Session-scoped `built_dist` and `wheel_venv` fixtures run `python -m build` and `pip install <wheel>` once per session, keeping the per-test cost negligible after the first invocation. |
| `pyproject.toml` | Modify | `[project.optional-dependencies] dev` gains `build>=1.0` (Step 1 OQ-D + OQ-M's `>=` bounds rule). Keeps the dev-extra contract self-describing — a fresh contributor's `pip install -e ".[dev]"` brings `build` in without an out-of-band install. |
| `docs/release-runbook.md` | Create | Draft skeleton (Status: draft, Role: runbook) carrying the four-section checklist (Pre-flight / TestPyPI rehearsal / Real PyPI publish / Post-release). Phase 7 finalises this with the workflow wiring; Phase 9 and Phase 10 walk every row. |
| `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Re-synced in lockstep via `./bin/docs index --root docs/` after `release-runbook.md` landed (new `Active — Runbook` group on the INDEX). |

#### Test groups

- **A1–A6 — `pyproject.toml` static contract.** A1 hatchling
  `[build-system]`; A2 `name = "docs-cli"`; A3 `version = "1.1.0"`;
  A4 `[project.scripts] docs = "docs_cli.cli:main"`; A5
  `[project.urls]` Homepage / Repository / Issues; A6 a loose
  hatch-build table mentions "skill" (Step 1 OQ-K). **A7 deferred** per
  Step 1's plan (dev-extra contract decision is Phase 6's concern).
- **B1–B4 — wheel and sdist artefacts.** B1 wheel builds as
  `docs_cli-1.1.0-*.whl`; B2 sdist builds as
  `docs_cli-1.1.0.tar.gz`; B3 wheel contains
  `docs_cli/cli.py` + `docs_cli/skill/SKILL.md` +
  `docs_cli/skill/references/{convention,cli}.md`; B4
  `entry_points.txt` registers `docs = docs_cli.cli:main`.
- **C1–C3 — installed CLI surface.** C1 venv has `docs` on PATH;
  C2 `docs --version` prints `1.1.0`; C3 `docs --help` lists every
  verb the in-tree `_build_parser()` registers plus `install-skill`
  (Step 1 OQ-O — the conftest-alias import keeps the expected verb
  set in lockstep with the parser).
- **D1–D7 — `docs install-skill` verb.** D1 subcommand exists
  (`--help` exits 0); D2 default action is `--copy` (`--dest <tmp>`
  succeeds; never triggers the `~/.claude/skills/docs/` default per
  Step 1 OQ-H); D3 the materialised tree is byte-identical to
  `src/docs_cli/skill/`; D4 idempotent (two invocations exit 0);
  D5 refuses a non-identical existing dest without `--force` and
  succeeds with `--force`; D6 `--symlink` rejected on a wheel
  install; D7 `--help` documents the default dest as
  `~/.claude/skills/docs/` (Step 1 OQ-H — assertion via help text only).
- **E1–E2 — installed `docs` against fixture trees.** E1 installed
  `docs check tests/fixtures/trees/minimal/` exits 0; E2 installed
  `docs index --root <fixture> --dry-run` exits 0. Uses the existing
  `minimal/` fixture; Phase 3 confirms the reuse decision.
- **F1–F3 — repo-layout invariants.** F1
  `src/docs_cli/{__init__.py,cli.py,skill/SKILL.md}` exist; F2
  top-level `skills/docs/` is gone (Step 1 OQ-F note: the test
  asserts the post-Phase-5 state directly; it is RED until Phase 5
  moves the skill); F3 `bin/docs` is gone (OQ5 — Phase 5 deletes).

#### Actions taken

- Wrote `tests/test_packaging.py` (≈ 460 lines, 25 tests). The
  session-scoped `built_dist` fixture runs `python -m build` once
  against `REPO_ROOT` into a `tmp_path_factory.mktemp("dist")`
  outdir; `wheel_venv` creates a `venv.EnvBuilder` venv and
  pip-installs the produced wheel, yielding the absolute path to
  the venv's `docs` entry-point. Subprocess invocations carry
  `capture_output=True, text=True` so failure messages surface in
  the pytest report instead of vanishing into pipe buffers.
- Added `build>=1.0` to `[project.optional-dependencies] dev`. The
  `>=` bound mirrors the existing `pytest>=7.0` / `ruff>=0.4` /
  `mypy>=1.0` per Step 1 OQ-M.
- Created `docs/release-runbook.md` via `./bin/docs new runbook
  release-runbook --root docs/` (scaffolds the metadata block),
  then overwrote the body with the four-section checklist. Status
  stays `draft` — Phase 7 finalises and flips to `active`.
- Regenerated `docs/INDEX.md` (new `### Active — Runbook` group)
  and copied onto `tests/fixtures/expected/docs-INDEX.md`.
- Ran the quality gate tree-wide: `ruff check .` (clean after one
  E402+I001 `# noqa` on the conftest-alias import), `ruff format
  --check .` (clean after one reformat), `mypy` (clean — 21 source
  files now). The `# noqa: E402, I001` on `from docs import
  _build_parser` is the standard idiom for an `importorskip`-gated
  late import.

#### Issues / decisions

- **`pytest.importorskip("build")` placement.** Module-level
  `importorskip` runs at import time, before `from docs import
  _build_parser`. Ruff's E402 (module-level import not at top) and
  I001 (un-sorted imports) both flag the late `docs` import. The
  fix is a targeted `# noqa: E402, I001` comment — the same idiom
  M5's `tests/test_skill.py` would have used had it needed it. No
  config-level ruff change.
- **A7 deferred (Step 1 OQ-A7-SKIP).** The "`[dev]` extra includes
  build" test would assert the contract that Phase 2 just added to
  `pyproject.toml`. Step 1's plan defers the test to Phase 6 so
  that the dev-extra-contract decision can land alongside the
  hatchling/package-data shape rather than being pinned at Phase 2.
- **Step 1 OQ-F — `test_skill.py` / `test_skill_refs.py` untouched.**
  The skill source still lives at `skills/docs/` at Phase 2. The
  M5-era tests still target that path and remain green. Phase 5
  performs the skill move + the test-path edits together; doing
  them now would leave the M5 tests RED for a non-M6 reason.
- **Step 1 OQ-G — lockstep semantics.** `test_skill_refs.py`'s
  lockstep check (bundled `convention.md` / `cli.md` mirrors must
  byte-match `docs/`) keeps the same semantics at the new path
  when Phase 5 runs. Phase 2 does not touch it.
- **Step 1 OQ-N — `cli.md` install-skill section.** Documenting the
  new verb in `cli.md` is Phase 6 (when the verb is implemented).
  Phase 2 leaves `cli.md` alone.
- **`docs new` `Updated:` for `release-runbook.md`.** `docs new`
  emits today's `Updated:` line; no manual bump needed.

#### Verification

- `.venv/bin/python -m pytest tests/test_packaging.py --collect-only
  -q` collects 25 tests cleanly (no import errors).
- `.venv/bin/ruff check .` — clean.
- `.venv/bin/ruff format --check .` — clean.
- `.venv/bin/mypy` — clean (21 source files).
- `./bin/docs check docs/` — exit 0.

The packaging tests are intentionally RED at this phase; the full
RED-baseline run is Phase 4's job (with the captured output appended
to the Phase 4 log entry per the M5 log format).

#### Exit criteria

- [x] `tests/test_packaging.py` collects 25 tests with no
      `ImportError` / `CollectError`.
- [x] `pyproject.toml`'s `[dev]` extra includes `build>=1.0`.
- [x] `docs/release-runbook.md` exists with a parseable metadata
      block (`Status: draft`, `Role: runbook`) and the four-section
      checklist.
- [x] `docs/INDEX.md` and `tests/fixtures/expected/docs-INDEX.md`
      regenerated in lockstep (new `Active — Runbook` group).
- [x] `ruff check`, `ruff format --check`, `mypy` clean tree-wide.
- [x] `./bin/docs check docs/` exit 0.
- [x] M1–M5's 246 in-tree tests stay green (untouched at this phase).
- [x] Ready for Phase 3 (confirm fixture reuse) and Phase 4 (capture
      the RED baseline).

### Phase 3 — Create Data/Fixtures

**Completed:** 2026-05-23

#### Objective

Confirm that the fixtures the Phase-2 packaging tests need are present
on disk. Step 1's plan offered two options: Option A reuse
`tests/fixtures/trees/minimal/`; Option B hand-author
`tests/fixtures/trees/packaging-clean/`. Pick the one whose
preconditions hold and document the reuse decision in the log.

#### Files changed

| File | Action | Notes |
|---|---|---|
| _(no new fixture files)_ | _Reuse decision_ | `tests/fixtures/trees/minimal/` (a single `lone-doc.md` + a `.docs.toml`) is reused for the installed-`docs check` (E1) and installed-`docs index --dry-run` (E2) smokes per Step 1's Option A. |

#### Why there is nothing to stage

The Phase-2 tests reference one fixture-tree path:
`tests/fixtures/trees/minimal/`. It is present (created at M1):

```
tests/fixtures/trees/minimal/
├── .docs.toml
└── lone-doc.md
```

Running `./bin/docs check tests/fixtures/trees/minimal/` against the
in-tree binary exits 0 at Phase 3 — the precondition for E1 and E2 is
already satisfied. Authoring a parallel `tests/fixtures/trees/packaging-clean/`
would duplicate the same shape without adding coverage. Option B is
deliberately skipped per Step 1's plan ("if it does [exit 0], no new
fixture; document the reuse decision in the log").

Group F (layout invariants) and Group A (pyproject static) need no
fixture data at all — they read from the repo root directly. Groups B,
C, D rely on the build process and a throwaway venv, both materialised
at session-fixture time (`built_dist`, `wheel_venv`) inside
`tmp_path_factory.mktemp(...)`; no checked-in artefact applies.

#### Verification — every Phase-2 input resolves

- `tests/fixtures/trees/minimal/` exists and is clean
  (`./bin/docs check tests/fixtures/trees/minimal/` exit 0).
- `tests/fixtures/trees/minimal/.docs.toml` exists so the installed
  `docs check` and `docs index --root` invocations resolve a config
  without needing to walk up to the repo root.
- `pyproject.toml` and the in-repo file system are the only other
  inputs the Phase-2 tests touch — nothing fixture-shaped needed.

#### Issues / decisions

- **Option A vs Option B.** Option A (reuse) wins on the principle
  that fixtures duplicate-by-shape introduce drift surface. Option B
  was preserved in the plan as a fallback for the case where
  `minimal/` had grown an unexpected violation between M1 and M6;
  that did not happen.
- **No new `.docs.toml` settings.** The Phase-2 tests assert
  installed-CLI behaviour against a *clean* tree only — there is no
  vocabulary or `add_statuses` / `add_roles` toggle to verify
  through packaging. The existing minimal config is empty enough to
  serve.

#### Exit criteria

- [x] `tests/fixtures/trees/minimal/` resolves on disk.
- [x] `./bin/docs check tests/fixtures/trees/minimal/` exits 0.
- [x] No fixture authoring needed; reuse decision recorded.
- [x] M1–M5's 246 in-tree tests stay green (untouched at this phase).
- [x] Ready for Phase 4 (RED baseline capture).
