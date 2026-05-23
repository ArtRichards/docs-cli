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
| 4. Run Tests (RED Baseline) | Complete | 2026-05-23 | Captured the verbatim `pytest -q --tb=short` output: **9 FAILED + 16 ERRORS + 246 PASSED = 271 collected**. The 9 FAIL are the assertion-level RED on the pyproject static contract (A1–A6) + the layout invariants (F1–F3); the 16 ERROR are setup-fixture failures cascading from `built_dist` (`python -m build` rejects `version = "0.2.0-m2"` as non-PEP440 — exactly the Phase-6-fixes condition). M1–M5's 246 tests stay green; ruff/format/mypy clean tree-wide; `docs check docs/` exit 0. **Session pauses here** per the project's TDD discipline. |
| 5. Update Base Interfaces | Complete | 2026-05-23 | `git mv bin/docs src/docs_cli/cli.py`; `git mv skills/docs src/docs_cli/skill`; `src/docs_cli/__init__.py` re-exports `main`; `tests/conftest.py` rewritten (drop SourceFileLoader; insert `src/` on sys.path; alias `docs_cli.cli` as `docs`); `tests/test_skill.py` SKILL_DIR + failure-message updated; `tests/test_skill_refs.py` BUNDLE_DIR + resync hint updated; `pyproject.toml` ruff `extend-include` dropped, mypy `files = ["src/", "tests/"]`, `scripts_are_modules` dropped; `~/.claude/skills/docs` symlink refreshed to the relocated source. Quality gate: 246 M1–M5 + F1/F2/F3 GREEN, A1–E2 still RED for Phase 6. |
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

### Phase 4 — Run Tests (RED Baseline)

**Completed:** 2026-05-23

#### Objective

Run the full test suite and capture the RED baseline before any
packaging surface is implemented. Confirm every `test_packaging.py`
test fails for its *intended* reason (no `[build-system]`, no entry
point, no `docs_cli` package, no `install-skill` verb, `bin/docs` and
`skills/docs/` still in place). M1–M5's 246 tests stay green. Per the
project's TDD discipline, **Step 1 pauses here.**

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/m6-pypi-distribution-log.md` | Modify | Phase 4 row → Complete; this log entry appended (Phase-4 baseline output + per-test attribution table). |

#### Captured command output

```
$ .venv/bin/python -m pytest tests/ -q --tb=short 2>&1 | tee /tmp/m6-phase-4-baseline.txt
........................................................................ [ 26%]
........................................................................ [ 53%]
........................................................................ [ 79%]
...FFFFFFEEEEEEEEEEEEEEEEFFF...........................                  [100%]
…
9 failed, 246 passed, 16 errors in 4.46s
```

Aggregate: **271 collected → 246 green (M1–M5) + 25 RED (test_packaging
group: 9 assertion-failures + 16 fixture-setup errors).**

Full one-line list of every RED outcome:

```
ERROR tests/test_packaging.py::test_b1_wheel_builds - Failed: `python -m build` failed …
ERROR tests/test_packaging.py::test_b2_sdist_builds - Failed: `python -m build` failed …
ERROR tests/test_packaging.py::test_b3_wheel_contains_cli_and_skill - Failed: …
ERROR tests/test_packaging.py::test_b4_entry_point_recorded_in_wheel - Failed: …
ERROR tests/test_packaging.py::test_c1_docs_on_path_in_venv - Failed: …
ERROR tests/test_packaging.py::test_c2_docs_version_is_1_1_0 - Failed: …
ERROR tests/test_packaging.py::test_c3_docs_help_lists_every_verb - Failed: …
ERROR tests/test_packaging.py::test_d1_install_skill_subcommand_exists - Failed: …
ERROR tests/test_packaging.py::test_d2_install_skill_default_action_is_copy
ERROR tests/test_packaging.py::test_d3_install_skill_tree_is_byte_identical
ERROR tests/test_packaging.py::test_d4_install_skill_is_idempotent - Failed: …
ERROR tests/test_packaging.py::test_d5_install_skill_refuses_non_identical_without_force
ERROR tests/test_packaging.py::test_d6_install_skill_rejects_symlink_on_wheel_install
ERROR tests/test_packaging.py::test_d7_install_skill_default_dest_documented
ERROR tests/test_packaging.py::test_e1_installed_docs_check_passes_minimal_fixture
ERROR tests/test_packaging.py::test_e2_installed_docs_index_dry_run_clean - Failed: …
FAILED tests/test_packaging.py::test_a1_build_system_is_hatchling - AssertionError …
FAILED tests/test_packaging.py::test_a2_project_name_is_docs_cli - AssertionError …
FAILED tests/test_packaging.py::test_a3_project_version_is_1_1_0 - AssertionError …
FAILED tests/test_packaging.py::test_a4_console_script_entry_point_present - …
FAILED tests/test_packaging.py::test_a5_project_urls_present - AssertionError …
FAILED tests/test_packaging.py::test_a6_hatch_build_packages_the_skill - AssertionError …
FAILED tests/test_packaging.py::test_f1_src_docs_cli_layout - AssertionError: …
FAILED tests/test_packaging.py::test_f2_top_level_skills_docs_removed - AssertionError …
FAILED tests/test_packaging.py::test_f3_bin_docs_removed - AssertionError: …
```

Verbatim output preserved at `/tmp/m6-phase-4-baseline.txt`.

#### Failure attribution — every RED for its intended reason

| Test | Outcome | Intended RED reason at Phase 4 | Phase that GREENs it |
|---|---|---|---|
| `test_a1_build_system_is_hatchling` | FAIL | `[build-system]` missing from `pyproject.toml` | Phase 6 (adds hatchling) |
| `test_a2_project_name_is_docs_cli` | FAIL | `name = "docs"` still | Phase 6 |
| `test_a3_project_version_is_1_1_0` | FAIL | `version = "0.2.0-m2"` still | Phase 6 |
| `test_a4_console_script_entry_point_present` | FAIL | `[project.scripts]` missing | Phase 6 |
| `test_a5_project_urls_present` | FAIL | `[project.urls]` missing | Phase 6 |
| `test_a6_hatch_build_packages_the_skill` | FAIL | no `[tool.hatch.build...]` table | Phase 6 |
| `test_b1_wheel_builds` | ERROR | `built_dist` fixture: `python -m build` rejects non-PEP440 `version = "0.2.0-m2"` (and would fall back to setuptools with no `[build-system]` — both Phase-6 fixes) | Phase 6 |
| `test_b2_sdist_builds` | ERROR | same as B1 | Phase 6 |
| `test_b3_wheel_contains_cli_and_skill` | ERROR | same as B1 (cascades from `built_dist`) | Phase 6 |
| `test_b4_entry_point_recorded_in_wheel` | ERROR | same as B1 | Phase 6 |
| `test_c1_docs_on_path_in_venv` | ERROR | `wheel_venv` fixture cascades from `built_dist` failure | Phase 6 |
| `test_c2_docs_version_is_1_1_0` | ERROR | same | Phase 6 |
| `test_c3_docs_help_lists_every_verb` | ERROR | same | Phase 6 |
| `test_d1_install_skill_subcommand_exists` | ERROR | same (also: verb does not exist) | Phase 6 |
| `test_d2_install_skill_default_action_is_copy` | ERROR | same | Phase 6 |
| `test_d3_install_skill_tree_is_byte_identical` | ERROR | same (also: `src/docs_cli/skill/` not present until Phase 5) | Phase 6 |
| `test_d4_install_skill_is_idempotent` | ERROR | same | Phase 6 |
| `test_d5_install_skill_refuses_non_identical_without_force` | ERROR | same | Phase 6 |
| `test_d6_install_skill_rejects_symlink_on_wheel_install` | ERROR | same | Phase 6 |
| `test_d7_install_skill_default_dest_documented` | ERROR | same | Phase 6 |
| `test_e1_installed_docs_check_passes_minimal_fixture` | ERROR | `wheel_venv` cascade | Phase 6 |
| `test_e2_installed_docs_index_dry_run_clean` | ERROR | same | Phase 6 |
| `test_f1_src_docs_cli_layout` | FAIL | `src/docs_cli/` does not exist | Phase 5 (file moves) |
| `test_f2_top_level_skills_docs_removed` | FAIL | `skills/docs/` still present | Phase 5 |
| `test_f3_bin_docs_removed` | FAIL | `bin/docs` still present | Phase 5 |

Every error/failure traces to the *intended* unimplemented packaging
surface. There is no RED-for-wrong-reason on the books — the
contract is correctly pinned, and Phase 5 / 6 can proceed.

#### Per-check RED / GREEN breakdown

- **Group A (pyproject contract — 6 tests).** All 6 FAIL on the
  expected assertion (pyproject still has the pre-M6 stale shape).
- **Group B (build artefacts — 4 tests).** All 4 ERROR via the
  `built_dist` fixture; the root cause is the non-PEP440 version
  string `0.2.0-m2`. `python -m build` validates `[project].version`
  before even invoking the backend, so the test never reaches the
  "no `[build-system]`" condition. Phase 6's version bump to
  `1.1.0` AND hatchling registration fix this in one motion.
- **Group C (CLI surface — 3 tests).** All 3 ERROR via the
  `wheel_venv` fixture, which depends on a successful `built_dist`
  build. Cascades cleanly.
- **Group D (install-skill — 7 tests).** All 7 ERROR via
  `wheel_venv`. (D1–D7 individually depend on the verb existing in
  `cli.py`, which is Phase 6.)
- **Group E (installed docs surface — 2 tests).** Both ERROR via
  `wheel_venv` cascade.
- **Group F (layout invariants — 3 tests).** All 3 FAIL on the
  pre-Phase-5 layout (no `src/docs_cli/`, `skills/docs/` still
  present, `bin/docs` still present).
- **M1–M5 untouched.** All 246 in-tree tests still pass.

#### Issues / decisions

- **The 16 ERRORs are intentional, not lazy.** Step 1's plan flagged
  RED-for-wrong-reason as a Phase-5-trust-breaker. The fixture
  cascades here are RED-for-the-right-reason: `built_dist` is
  *designed* to surface the no-build-backend / non-PEP440-version
  state as a single `pytest.fail` with a clear message ("this is
  the intended Phase-4 RED if no [build-system] is declared"), and
  every downstream test ERRORs through that one root cause. When
  Phase 6 fixes the root cause, all 16 unblock in lockstep.
- **The non-PEP440 version string was the more proximate cause than
  "no `[build-system]`."** Python's `build` tool validates
  `[project].version` against PEP 440 before it tries to read
  `[build-system]`. Either condition would block the build; only
  one error message surfaces, and the version-string check fires
  first. Phase 6 fixes both in the same commit, so the distinction
  is bookkeeping only.
- **OQ-L aggregate check.** Step 1's OQ-L expected ~22 RED
  packaging tests; the actual count is 25 (9 FAIL + 16 ERROR).
  The delta is the D group running 7 sub-tests rather than the
  ~6 the OQ-E plan-text mentioned (D7's help-text default-dest
  check is per OQ-H, and the F group runs 3 layout invariants
  rather than baking them into a single multi-assert test). The
  numerical drift is within the OQ-L "~22" band; no functional
  change.

#### Trigger-scenario checklist — N/A at Phase 4

M5 walked a behavioural-trigger checklist at Phase 4 because the
skill's GREEN oracle was partly judgement-driven. M6's packaging
contract is fully structural — every check is a code-side assertion
in `test_packaging.py`. There is no separate trigger-scenario list
at this phase; the operational analogue is `docs/release-runbook.md`,
which is walked at Phases 9 and 10.

#### Exit criteria

- [x] `tests/test_packaging.py` is fully RED — every test in the
      file fails or errors.
- [x] Each RED traces to the *intended* unimplemented surface (the
      attribution table above is complete; no RED-for-wrong-reason).
- [x] M1–M5's 246 in-tree tests stay green.
- [x] `ruff check .` — clean.
- [x] `ruff format --check .` — clean.
- [x] `mypy` — clean.
- [x] `./bin/docs check docs/` — exit 0.
- [x] `docs/release-runbook.md` skeleton stands fully unsatisfied
      (no checklist row is checked).
- [x] Verbatim baseline output preserved at
      `/tmp/m6-phase-4-baseline.txt`.
- [x] **Step 1 (Phases 1–4) pauses here.**

#### Review fixes

After Step 1 paused, a fresh-eyes review returned **ship-with-fixes**
with one should-fix and one cheap nit. Both folded in on
`m6/phases-1-4` at `6be7e4c`:

- **D5 — should-fix.** `test_d5_install_skill_refuses_non_identical_without_force`
  previously only asserted a non-zero exit, then re-ran with `--force`.
  A buggy implementation that errored out *after* partially overwriting
  files would still satisfy that. Added a byte-content assertion
  between the two `subprocess.run` calls: `dest/SKILL.md` must still
  read `DIFFERENT CONTENT\n` after the no-force rejection. Pins the
  spec's implicit "dest is preserved on rejection" guarantee.
- **C2 — cheap nit.** `test_c2_docs_version_is_1_1_0` used
  `"1.1.0" in combined`, which would also accept `21.1.0` or
  `1.1.0.dev0`. Tightened to a whitespace-token match
  (`"1.1.0" in combined.split()`).

Deferred (with rationale):

- **A6** — loose substring match for `"skill"`. Backstopped by B3
  (wheel-contents check). Leave for Phase 6 if desired.
- **C3** — substring `"verb in out"` matches M5 precedent in
  `tests/test_skill.py`. Leave for codebase consistency.
- **F2/F3** — non-existence assertions; backstopped by F1 + B3. Leave.
- **conftest shape** — old wheel-venv shape; rewritten in Phase 5
  per OQ2. Leave.
- **`~/.claude/skills/docs` dangling symlink** — host-state nit
  already inventoried for Phase 5 refresh. No action at Step 1.

Both fixed tests remain RED at Phase 4 (D5 still ERRORs in the
install-skill cascade because the verb does not exist yet; C2 still
ERRORs in the wheel-build cascade). The new assertions take effect
once Phase 6 implements the surfaces they pin. Quality gate post-fix:
246 green + 25 RED (baseline unchanged); ruff, `ruff format --check`,
mypy, and `./bin/docs check docs/` all clean.

### Phase 5 — Update Base Interfaces (structural relocation)

**Completed:** 2026-05-23

#### Objective

Move the executable script and the bundled Claude Code skill into a
real Python package layout under `src/docs_cli/`, with zero behaviour
changes. The phase exists to flip the three layout-invariant
packaging tests (F1/F2/F3) GREEN and pin the import shape Phase 6
will build on top of. The M1–M5 246-test suite stays green throughout
via the conftest's `docs` alias (OQ2).

#### Files changed

| File | Action | Notes |
|---|---|---|
| `bin/docs` → `src/docs_cli/cli.py` | `git mv` | History preserved; no content edit. Empty `bin/` directory removed. |
| `skills/docs/` → `src/docs_cli/skill/` | `git mv` | History preserved; empty `skills/` directory removed. The wheel ships exactly what the author edits (OQ4). |
| `src/docs_cli/__init__.py` | Create | Re-exports `main` from `docs_cli.cli`. `__version__` deliberately left to Phase 6 (single source of truth in `cli.py` per Q1). |
| `tests/conftest.py` | Rewrite | Dropped `importlib.machinery.SourceFileLoader` block. Inserts `src/` on `sys.path`; imports `docs_cli.cli`; aliases it as `docs` in `sys.modules` so `from docs import …` keeps working in the ~18 pre-M6 test files (OQ2). `docs_script` fixture retained (the plan called for dropping it, but every `test_cli_*.py` depends on it for the subprocess-invocation tests; now points at the relocated `src/docs_cli/cli.py`). |
| `tests/test_skill.py` | Modify | `SKILL_DIR` → `REPO_ROOT / "src" / "docs_cli" / "skill"`; clutter-allowlist failure message updated to reference the new path; docstring at line 45 updated. |
| `tests/test_skill_refs.py` | Modify | `BUNDLE_DIR` → `REPO_ROOT / "src" / "docs_cli" / "skill" / "references"`; module docstring resync hint and failure message both updated. |
| `pyproject.toml` | Modify | Dropped `[tool.ruff].extend-include = ["bin/docs"]`; added `[tool.ruff].extend-exclude = ["tests/_typing/"]`; dropped `[tool.mypy].scripts_are_modules = true`; mypy `files` flipped from `["bin/docs", "tests/"]` to `["src/", "tests/"]`; added `[tool.mypy].mypy_path = "$MYPY_CONFIG_FILE_DIR/src:$MYPY_CONFIG_FILE_DIR/tests/_typing"`. `[project]` table left for Phase 6 (it owns name/version/build-system). |
| `tests/_typing/docs.pyi` | Create | Mypy-only stub re-exporting `docs_cli.cli`'s public surface. The conftest aliases the runtime module as `docs` in `sys.modules`, but mypy can't observe that — the stub fills the typing gap without weakening any error code. |
| `~/.claude/skills/docs` (host symlink) | Refresh | `ln -sfn /home/user/opt/docs-cli/src/docs_cli/skill ~/.claude/skills/docs` — pointed at the relocated source. The pre-Phase-1 symlink was dangling after the `~/opt/docs` → `~/opt/docs-cli` rename and again after this move. |
| `docs/status.md` | Modify | "Next action" rewritten to point at Phase 6; verify-environment block updated for the new layout (post-Phase-5 use `.venv/bin/python -m docs_cli.cli …`; post-Phase-6 use `.venv/bin/docs`); "Watch out for" sweep replaced `bin/docs` references; reading-order line for the skill points at the new path. |
| `docs/m6-pypi-distribution-log.md` | Modify | Phase-5 row → Complete; this log entry appended. |

#### Actions taken

- `git mv bin/docs src/docs_cli/cli.py` (preserved history with no
  content edit). Removed empty `bin/__pycache__/` and `rmdir bin`.
- `git mv skills/docs src/docs_cli/skill` (history preserved).
  `rmdir skills` (empty parent).
- Wrote `src/docs_cli/__init__.py` with `from docs_cli.cli import
  main; __all__ = ["main"]`. Per Q1, the version constant lives in
  `cli.py` only (single source of truth); `__init__.py` does not
  re-declare `__version__`.
- Rewrote `tests/conftest.py` per OQ2 + the Phase 5 plan: inserts
  `src/` on `sys.path` before any test import resolves; imports
  `docs_cli.cli`; aliases it as `docs` in `sys.modules`. Retains
  the `docs_script` session fixture (re-pointed at
  `src/docs_cli/cli.py`) so the subprocess-driven `test_cli_*.py`
  tests keep launching the CLI exactly as before.
- Updated `tests/test_skill.py` line 37 (`SKILL_DIR`), line 45
  (docstring), line 228 (clutter-allowlist failure message).
- Updated `tests/test_skill_refs.py` line 22 (`BUNDLE_DIR`), lines
  3 / 10–11 (docstring + resync command), lines 31–32 (failure
  message).
- Cleaned `pyproject.toml` of the now-irrelevant
  executable-script tooling: dropped `extend-include = ["bin/docs"]`
  from `[tool.ruff]`, dropped `scripts_are_modules = true` from
  `[tool.mypy]`, and flipped mypy's `files` list to `["src/",
  "tests/"]`. The `[project]` table is intentionally untouched —
  Phase 6 owns the name/version/build-system rewrite.
- Refreshed `~/.claude/skills/docs` →
  `/home/user/opt/docs-cli/src/docs_cli/skill`.
- Updated `docs/status.md`: "Next action" now points at Phase 6;
  verify-environment commands updated to use `python -m docs_cli.cli`
  pre-Phase-6 and `.venv/bin/docs` post-Phase-6; "Watch out for"
  references to `bin/docs` and the in-`pyproject` `extend-include`
  shape rewritten; the resuming-this-work line for the bundled skill
  now points at the relocated path.

#### Issues / decisions

- **`tests/_typing/docs.pyi` stub added to keep mypy GREEN.** With
  the script-as-module trick gone (`scripts_are_modules` dropped),
  mypy can no longer resolve `from docs import X` — the alias is a
  runtime `sys.modules` insertion that static analysis cannot see.
  The minimal fix is a stub at `tests/_typing/docs.pyi` that
  re-exports `docs_cli.cli`'s public surface, plus a `mypy_path`
  entry pointing at `tests/_typing` (the directory is ruff-excluded
  so its hand-grouped import block survives `ruff check`). Mypy
  goes back to "Success" without weakening any error-code or
  silencing real defects in test code. Not in the Phase 5 plan; a
  necessary follow-on from the OQ5 `bin/docs` deletion.
- **Plan called for dropping the `docs_script` fixture; kept it.**
  The plan text said "Drop the SourceFileLoader block and the unused
  docs_script fixture." The fixture is NOT unused — eight
  `test_cli_*.py` files reference it (`test_cli_archive.py`,
  `test_cli_check.py`, `test_cli_index.py`, `test_cli_list.py`,
  `test_cli_migrate.py`, `test_cli_mv.py`, `test_cli_new.py`,
  `test_cli_touch.py`) and pass it to `_run(script, *args)` which
  invokes the CLI as `[sys.executable, str(script), …]`. Dropping the
  fixture would error-out ~70 tests at fixture-setup time. Kept the
  fixture and re-pointed it at the relocated `src/docs_cli/cli.py`;
  the file is plain stdlib Python and runs as a script unchanged.
  Recorded as a Phase 5 plan deviation.
- **`~/bin/docs` convenience symlink (Q9).** Per the resolved
  question this is a no-op for the repo — host-only. The host had no
  `~/bin/docs` at Phase 1 inventory and still does not; nothing to
  refresh.
- **`/home/user/opt/docs-cli/.venv/`** still has stale shebangs from
  the Phase-1-era recreation (built against the old path), but
  pytest/ruff/mypy are still reachable via
  `.venv/bin/python -m pytest …` etc. The venv recreation only
  matters once Phase 6's editable install lands the `docs` entry
  point on PATH.

#### Verification

- `.venv/bin/python -m pytest tests/ --ignore=tests/test_packaging.py
  -q` → **246 passed** (M1–M5 untouched).
- `.venv/bin/python -m pytest tests/test_packaging.py -q` → **3
  passed, 6 failed, 16 errors**. The 3 passed are F1
  (`src/docs_cli/{__init__.py, cli.py, skill/SKILL.md}` exist), F2
  (top-level `skills/docs/` is gone), F3 (`bin/docs` is gone) —
  exactly the layout invariants Phase 5 is supposed to flip. The 6
  failed + 16 errored are A1–A6 + B1–E2, every one of them blocked
  on the Phase 6 surface (no `[build-system]`, no
  `[project.scripts]`, no `install-skill` verb).

#### Exit criteria

- [x] `src/docs_cli/{__init__.py, cli.py, skill/SKILL.md}` exist;
      history preserved through both `git mv` operations.
- [x] `bin/docs` is gone (the parent `bin/` directory is gone too).
- [x] `skills/docs/` is gone (the parent `skills/` directory is gone
      too).
- [x] `tests/conftest.py` no longer references `SourceFileLoader`
      or `bin/docs`; `docs_cli.cli` is aliased as `docs` in
      `sys.modules` per OQ2.
- [x] `tests/test_skill.py` and `tests/test_skill_refs.py` reference
      the new source path.
- [x] `pyproject.toml` ruff/mypy config no longer references
      `bin/docs`; `scripts_are_modules` removed.
- [x] `~/.claude/skills/docs` symlink resolves to
      `/home/user/opt/docs-cli/src/docs_cli/skill`.
- [x] **246 M1–M5 tests still green.**
- [x] **F1/F2/F3 packaging tests GREEN.** A1–E2 still RED; their RED
      reasons all map to Phase 6 work (`[build-system]`,
      `[project.scripts]`, `install-skill` verb).
- [x] `docs/status.md` updated for Phase 5 completion.
