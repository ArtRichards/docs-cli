# docs — Status

Lifecycle: active
Role: status
Project: docs
Updated: 2026-05-25

Related:
- pairs-with: plan.md
- pairs-with: m6-pypi-distribution.md
- pairs-with: m7-migration-accuracy.md
- pairs-with: m8-adoption-workflow.md
- pairs-with: m9-pypi-publish.md
- pairs-with: release-runbook.md

**This is the single source of truth for project progress. Update only this file when milestones complete or phases advance.**

## Current milestone

**M6 closed 2026-05-24 as preparation only.** The 2026-05-24 scope
reframe split the actual PyPI publish out of M6 into a new
milestone — **M9 — PyPI publish 1.3.0** — so M6 could close
cleanly instead of hanging at "implementation done, publish
pending" for the M7 + M8 weeks. Two follow-on implementation
milestones cluster the 2026-05-24 multi-tree trial's findings:
**M7 — Migration plan accuracy** (Complete 2026-05-25;
ship-ready locally, publish deferred to M9 batched 1.3.0) and
**M8 — Adoption workflow** (in flight; depends on M7's ship,
which is now landed). M9 runs last, post-M8, as an operator-
driven publish of the batched M6 + M7 + M8 surface. See
`plan.md`'s v1.1 section.

### M6 — preparation complete (2026-05-24)

M6 was merged to `main` 2026-05-24 as commit `ff7f9d5` and
closed at Phase 10 as **preparation only** — packaging machinery
(build backend, package shape, `install-skill` verb, runbook
scaffold, GitHub repo) delivered; no PyPI upload was ever in
M6's scope after the 2026-05-24 reframe. The wheel + sdist in
local `dist/` from 2026-05-23 are not uploaded; M9 will rebuild
fresh from the post-M8 tree at publish time. See
[m6-pypi-distribution.md](m6-pypi-distribution.md)'s top
"Scope reframe" callout and the
[release-runbook.md](release-runbook.md) for the operative
checklist.

### M9 — PyPI publish 1.3.0 (stub, post-M8)

[m9-pypi-publish.md](m9-pypi-publish.md) stub-drafted 2026-05-24.
Activates once M8 ships. The operative checklist is
[release-runbook.md](release-runbook.md): operator one-time prep
(accounts, 2FA, API tokens, `~/.pypirc`) done in parallel with
M7 / M8; then a single contiguous post-M8 session for version
bump → CHANGELOG restructure → tree state → quality gate →
artifact build → local smoke → TestPyPI rehearsal → real PyPI
publish → post-release closeouts (repo public flip, tag +
GitHub release, token re-scope, doc closeouts). M6 / M7 / M8
ship together as `docs-cli==1.3.0`. No code work; no TDD phases.

### M7 + M8 — stubs drafted from the 2026-05-24 trial

The multi-tree trial against 25 real-world foreign trees (501 .md
files) surfaced 11 categorical findings. They cluster into two
milestones:

- **M7 — Migration plan accuracy** (Complete 2026-05-25):
  renamed the controlled-vocab field `Status:` → `Lifecycle:`
  (breaking, no backward compat), broadened role inference
  (suffix matching, H1 + section signals, sibling defaulting),
  normalised project names to lowercase-kebab, normalised
  `archived/` subdirs into `archive/YYYY-MM-DD/`, expanded the
  role vocab with 7 core additions (`implementation`, `sketch`,
  `outline`, `memo`, `brief`, `template`, `example`). One new
  CLI flag: `docs migrate --config-project NAME` (plus
  `--lifecycle` rename on `docs list`). Trial-2 dogfood: 88%
  high+medium against the sanitised real-tree fixtures. Plan
  at [m7-migration-accuracy.md](m7-migration-accuracy.md).
- **M8 — Adoption workflow** (after M7): `--exclude` tree-wide
  (in `migrate` + `index` + `check` + `list` via `.docs.toml`'s
  new `[exclude]` section), triage flags
  (`--summary`, `--only ambiguous`), `docs new --body-from <-|path>`
  (closes Read-before-Write friction), and a substantial rewrite
  of the bundled skill's references for the adoption flow
  (SKILL.md stays slim — one pointer line). Stub at
  [m8-adoption-workflow.md](m8-adoption-workflow.md). Load-bearing
  ship gate: **fresh-subagent dogfooding** of the adoption loop
  end-to-end against trees the M8 author hasn't tuned for.

### M6 milestone-setup history (kept for context)

**M6 — PyPI distribution as `docs-cli` is in flight (milestone-setup
phase complete, 2026-05-23).** The task plan
[m6-pypi-distribution.md](m6-pypi-distribution.md) is promoted from
`draft` to `active`; the log
[m6-pypi-distribution-log.md](m6-pypi-distribution-log.md) is created.
M6 is the first v1.1 milestone: it publishes the CLI as `docs-cli` on
PyPI, relocates `bin/docs` to an importable package at
`src/docs_cli/cli.py`, ships the Claude Code skill inside the wheel as
package data, and adds one new verb — `docs install-skill` — that
materialises the bundled skill onto a host. **All five milestone-setup
OPEN QUESTIONS are resolved 2026-05-23** (OQ1 command name stays
`docs`; OQ2 conftest aliases `docs_cli.cli` as `docs`; OQ3 repo
identity moves at Phase 1 with a new GitHub repo created since the
local repo has no remote yet — `ArtRichards/docs-cli` private until
v1.1 publishes; OQ4 skill source moves to `src/docs_cli/skill/`; OQ5
`bin/docs` is deleted). Phase 1's scope was expanded by the OQ3
override to carry the identity rename — new GitHub repo, local
checkout move `~/opt/docs` → `~/opt/docs-cli`, host-pointer updates —
in addition to the usual milestone-activation docs work. See the log
for the per-phase status table.

**Project v1 shipped 2026-05-22 — M1-M5 all complete.** M5 — Claude
Code skill closed the v1 roadmap on 2026-05-22 (post-ship polish on
2026-05-23; relocated under the package at M6 Phase 5). It is the
project's final v1 deliverable: a Claude Code skill — a `SKILL.md`
artifact at `src/docs_cli/skill/` (was `skills/docs/` at M5 ship) —
that makes an agent reach for the `docs` verbs automatically when
doing documentation work in a `docs`-managed tree. It adds no CLI
surface and changes no verb behaviour: it is a markdown artifact
whose `description` triggers on the right contexts (creating a
plan/spec/charter/milestone, archiving or renaming a doc, listing
docs, checking the tree, regenerating `INDEX.md`, adopting a foreign
Markdown directory) and whose body redirects to the appropriate `docs`
verb instead of hand-editing metadata, `INDEX.md`, or `archive/`. The
convention itself is not re-taught — the body links to the bundled
spec references at `src/docs_cli/skill/references/` (relocated from
`skills/docs/references/` at M6 Phase 5). The four M5 milestone-setup
OPEN QUESTIONS (OQ1-OQ4) were resolved and recorded as Decisions in
the task plan. **Post-ship polish (2026-05-23)** shortened `SKILL.md`
to a trigger surface (verb-task table + when-to-use scenarios +
never-hand-edit rule), bundled `convention.md` and `cli.md` as
references (byte-identical mirrors with a lockstep test), and
cleaned dev cross-refs out of the source specs. See
[m5-claude-code-skill-log.md](m5-claude-code-skill-log.md) for the
per-phase history (and the post-ship section appended to it) and
[m5-claude-code-skill.md](m5-claude-code-skill.md) for the milestone
summary.

M4 — Migration helper (`docs migrate`) shipped 2026-05-22 across ten TDD
phases. It added one verb — `docs migrate <dir>` — that adopts a
non-conforming directory into the convention: it walks a foreign tree, infers
the required metadata per file, and produces a migration plan (dry-run by
default; `--apply` writes the metadata blocks and normalises archive-style
subdirectories). See [m4-migration-helper-log.md](m4-migration-helper-log.md)
for the per-phase history and [m4-migration-helper.md](m4-migration-helper.md)
for the milestone summary.

M3 — Validation and query (`check`, `list`) shipped 2026-05-22 across ten TDD
phases. It added two read-only verbs — `docs check` (validate the tree, with
CI-usable exit codes) and `docs list` (filterable query view with a stable
JSON schema) — and regrouped `INDEX.md` by `Project` then `Role`. See
[m3-validation-and-query-log.md](m3-validation-and-query-log.md) for the
per-phase history and [m3-validation-and-query.md](m3-validation-and-query.md)
for the milestone summary.

M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) shipped 2026-05-21
across ten TDD phases. See [m2-mutating-verbs-log.md](m2-mutating-verbs-log.md)
for the per-phase history and [m2-mutating-verbs.md](m2-mutating-verbs.md)
for the milestone summary.

M1 — Parser and `docs index` shipped 2026-05-20 across ten TDD phases.
See [m1-parser-and-index-log.md](m1-parser-and-index-log.md) for the
per-phase history and [m1-parser-and-index.md](m1-parser-and-index.md)
for the milestone summary.

## Milestone progress

| Milestone | Status | Task plan | Log |
|---|---|---|---|
| M1 — Parser and `docs index` | **Complete** (2026-05-20) | [Plan](m1-parser-and-index.md) | [Log](m1-parser-and-index-log.md) |
| M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) | **Complete** (2026-05-21) | [Plan](m2-mutating-verbs.md) | [Log](m2-mutating-verbs-log.md) |
| M3 — Validation and query (`check`, `list`) | **Complete** (2026-05-22) | [Plan](m3-validation-and-query.md) | [Log](m3-validation-and-query-log.md) |
| M4 — Migration helper (`docs migrate`) | **Complete** (2026-05-22) | [Plan](m4-migration-helper.md) | [Log](m4-migration-helper-log.md) |
| M5 — Claude Code skill | **Complete** (2026-05-22) | [Plan](m5-claude-code-skill.md) | [Log](m5-claude-code-skill-log.md) |
| M6 — PyPI distribution preparation as `docs-cli` | **Complete** (2026-05-24, preparation only; publish moved to M9) | [Plan](m6-pypi-distribution.md) | [Log](m6-pypi-distribution-log.md) |
| M7 — Migration plan accuracy | **Complete** (2026-05-25; ship-ready locally, publish DEFERRED to M9 batched 1.3.0 per OQ-C) | [Plan](m7-migration-accuracy.md) | [Log](m7-migration-accuracy-log.md) |
| M8 — Adoption workflow (agent-driveable) | _in flight_ (started 2026-05-24; Phase 1 in progress; Phase 2+ blocked on M7 ship; all 7 milestone-setup OQs resolved) | [Plan](m8-adoption-workflow.md) | [Log](m8-adoption-workflow-log.md) |
| M9 — PyPI publish 1.3.0 | _stub-drafted_ (2026-05-24; activates post-M8 ship; operator-driven per [release-runbook.md](release-runbook.md)) | [Plan](m9-pypi-publish.md) | [Log](m9-pypi-publish-log.md) |

v1 (M1-M5) shipped 2026-05-22. **v1.1 is in flight**: M6 (PyPI
distribution preparation) closed 2026-05-24 as preparation only
after the scope reframe split publish out into M9; M7 (migration
accuracy — breaking `Status:` → `Lifecycle:` rename + inference
broadening) is the next implementation milestone to enter setup;
M8 (adoption workflow — `--exclude` tree-wide, triage flags,
`docs new --body-from`, skill-reference rewrite for adoption)
follows M7; M9 (PyPI publish 1.3.0) is the operator-driven
publish of the batched M6 + M7 + M8 surface, runs last. Per-
milestone task plans are expanded when each milestone activates.

## TDD phase order (used per milestone)

1. Define Contract
2. Write Tests (RED)
3. Create Data/Fixtures
4. Run Tests (RED Baseline)
5. Update Base Interfaces
6. Implement Offline/Core Path
7. Update Tool/Wrapper Layer
8. Run Tests (GREEN)
9. Implement Online/Integration (mapped to dogfooding pass when no network surface)
10. Quality, Docs, Refactor

## Quick links

- [Charter](charter.md) — what + why
- [Convention spec](convention.md) — on-disk format
- [CLI spec](cli.md) — command surface
- [Architecture](architecture.md) — module sketch + dev setup commands
- [Plan](plan.md) — milestone roadmap (v1 + v1.1)
- [Definition of Ready](definition-of-ready.md) — gate to start

## Resuming this work (fresh session)

If you're starting a new Claude Code session against this repo:

**Reading order** (≤ 10 minutes):
1. `~/CLAUDE.md` — host-level guidance + memory pointers
2. `docs/status.md` — this file
3. `docs/plan.md` — the roadmap; v1 (M1-M5) shipped, v1.1 in
   flight (M6 merged + publish-pending; M7+M8 stub-drafted).
4. `docs/m6-pypi-distribution.md` — M6 task plan; "Decisions"
   records the five milestone-setup OQs resolved 2026-05-23.
5. `docs/m6-pypi-distribution-log.md` — M6 log with the per-phase
   status table.
6. `docs/m7-migration-accuracy.md` — M7 stub: the breaking
   `Status:` → `Lifecycle:` rename and inference broadening
   (findings F0–F12 from the 2026-05-24 trial).
7. `docs/m8-adoption-workflow.md` — M8 stub: the agent + operator
   ergonomics (tree-wide `--exclude`, triage flags,
   `docs new --body-from`, skill-reference rewrite).
7a. `docs/m9-pypi-publish.md` + `docs/release-runbook.md` — M9
   stub + operative publish checklist; activates post-M8.
8. `docs/cli.md` — the command spec; the full eight-verb `docs`
   surface.
9. `docs/convention.md`, `docs/architecture.md` — the on-disk
   format and the module sketch.
10. `docs/m5-claude-code-skill.md` — v1's final milestone; its
    **Milestone-completion summary** describes the skill that
    M6's `install-skill` verb delivers via the wheel.
11. `src/docs_cli/skill/SKILL.md` — the bundled skill (relocated
    under the package source at M6 Phase 5).
12. `docs/charter.md` — what + why.
13. `docs/definition-of-ready.md` — the gate cleared before
    implementation.

**Verify environment** before doing any work:
```sh
cd ~/opt/docs-cli
.venv/bin/python -m pytest tests/ -q          # 271 passed
.venv/bin/ruff check .                        # All checks passed!
.venv/bin/ruff format --check .               # all files formatted
.venv/bin/mypy                                # Success (tree-wide)
.venv/bin/docs check docs/                    # dogfood — exit 0
.venv/bin/docs index --root docs/ --dry-run   # smoke: idempotent dogfood
```
If `.venv/` is missing (fresh clone) or `.venv/bin/docs` is absent:
```sh
rm -rf .venv && python3 -m venv .venv         # needs python3-venv on Debian/Ubuntu
.venv/bin/pip install -e ".[dev]"             # lands `docs` on PATH via the entry point
```

**Next action: M8 — execute the adoption-workflow milestone (which blocked on M7 ship). M9 is the batched 1.3.0 publish runs after M8.**

**Publish is M9** (operator decision 2026-05-24, scope-reframed
2026-05-24): a dedicated milestone, runs post-M8, ships M6 + M7
+ M8 as one batched `docs-cli==1.3.0` artifact per
[release-runbook.md](release-runbook.md). Intermediate versions
`1.1.0` and `1.2.0` never reach PyPI, which is fine — no prior
public release exists. The wheel + sdist sitting in local
`dist/` from M6 are NOT uploaded; M9 rebuilds fresh from the
post-M8 tree.

**M7 Phases 1-4 complete (2026-05-24; review-tightening 2026-05-25):**
task plan promoted to active, OQ A–D recorded as Decisions, log +
per-phase entries written, 44 new test items authored at Phase 2
(34 RED + 10 GREEN-at-baseline regression locks), sanitised
fixtures staged at
`tests/fixtures/{lifecycle,status-prose,project-names,sibling-defaulting}/`
+ `tests/fixtures/trees/real-trees/{kebab-tiny,snake-medium,snake-large,archive-subdir,mixed-naming}/`,
RED baseline captured at `/tmp/m7-phase-4-baseline.txt`
(34 failed, 281 passed; M6's 271 GREEN preserved + 10 new
regression locks). **Fresh-eyes review 2026-05-25** added 5
contract anchors (strict-medium pinning + parametric expansion
of status-prose preservation + `FileMigration(confidence="medium")`
constructor + `docs check` exit-1 medium anchor) for a post-fix
count of **39 RED + 281 passed (320 collected)**; M6's 271 still
GREEN. Quality gate clean tree-wide.

**M7 Phase 5 complete (2026-05-25):** the F0 controlled-vocab
rename landed across parser, dataclasses, writers, validators,
JSON serialisers, the `.docs.toml` reader, and argparse.
`Doc.lifecycle`, `FileMigration.lifecycle`, `Config.lifecycles`,
`validate_lifecycle`, `add_lifecycles` (TOML), `Lifecycle:` in
the on-disk block. `FileMigration.confidence` extended to
`high|medium|low`. `MigrationPlan` grows the
`project_original` + `multi_project_hints` fields with safe
defaults (populated at Phase 6). `Config` grows
`role_suffixes` + `project_name`. argparse:
`docs list --lifecycle` and `docs migrate --config-project NAME`.
29 docs/*.md files swept, 31 conformant fixture files swept,
existing-test fabrications updated. Skill refs resynced.
pytest: **290 passed, 30 failed (320 collected)** — every
failure on the Phase-6 surface (inference broadening,
project normalisation, per-file mtime archive, multi-project
hints, medium-confidence check wiring, snake-medium fixture
high+medium ratio). Quality gate clean.

**M7 Phase 6 complete (2026-05-25):** F1 / F10 / F11 / F12 /
F4 / F5 all landed. `infer_role` now does word-boundary +
case-transition splitting, recognises the 7 new core vocab
roles + `_M\d+` milestone pattern + `_v\d+`/`_Draft`/`_Ready`
strip with medium confidence. `normalise_project_name()`
produces lowercase-kebab and `plan_migration` honours CLI
> sidecar > inferred precedence with the `(normalised from
"X")` annotation. Per-file mtime drives archive moves when
`--date` is absent. Multi-project hints surface in the plan
footer. `check_doc` emits `medium-confidence-inference`
warnings (exit 1) when a missing `Role:` is resolvable via
H1 or section pattern. `.docs.toml` refusal narrowed so a
`[migrate]`-only sidecar is readable. **pytest: 320 / 320
GREEN.** Quality gate clean.

**M7 Phase 7 complete (2026-05-25):** convention.md, cli.md,
architecture.md, status.md, README.md, CHANGELOG.md all
updated to document M7's surface. New CHANGELOG entry
`## 1.2.0 — UNRELEASED` lists every breaking + additive
change (F0 rename, --lifecycle flag, JSON schema field
rename, add_lifecycles, 7 new core roles, medium
confidence, F11 normalisation, F4 per-file mtime, F5 hints,
--config-project, [migrate] sidecar). architecture.md gets
a new `config` module section. pyproject.toml +
`__version__` bumped to 1.2.0; `docs --version` prints
`docs 1.2.0`. Bundled skill refs resynced via byte-copy
(test_skill_refs.py GREEN). docs/INDEX.md regenerated;
fixture snapshot byte-equal. pytest: 320 / 320 GREEN.
Quality gate clean tree-wide.

**M7 Phase 8 complete (2026-05-25):** verbatim quality gate
captured at `/tmp/m7-phase-8-green.txt`. pytest 320 / 320
GREEN; ruff / format / mypy / docs check / docs index
--dry-run all clean; `docs --version` prints `docs 1.2.0`.

**M7 Phase 9 complete (2026-05-25):** all 5 quantitative
success criteria PASS. high+medium = 88.0% (103/117) ≥ 50%;
notes = 13.7% (16/117) ≤ 30%; free-form Status: preservation
= 4/4 = 100%; archive-subdir archive_move = 5/5 = 100% ≥ 80%;
project normalisation = 3/3 = 100% ≥ 90%.
`tests/manual/m7_success_criteria.py` aggregates; per-fixture
JSON dumps at `/tmp/m7-phase-9/*.json`.

**M7 Phase 10 complete (2026-05-25)**: milestone-completion
summary appended to `m7-migration-accuracy.md`; M7 row in
this file flipped to Complete; CHANGELOG `## 1.2.0 —
UNRELEASED` dated; local dist artefacts produced via
`python -m build` and verified with `twine check` (NO upload,
NO tag, NO GitHub release). M7 is ship-ready locally; the
public PyPI release ships as v1.3.0 batched with M6 + M8 at
the M9 milestone per the operator OQ-C split.

**M8** is in flight (Phase 1 complete; **Phase 2+ unblocked by
M7 ship 2026-05-25**). All 7 OQs (A–G) resolved 2026-05-24.
Setup committed 2026-05-24 as `929e525`.

**Watch out for** (durable gotchas, still current):
- The CLI module lives at `src/docs_cli/cli.py`. After Phase 6's
  editable install (`pip install -e ".[dev]"`), the `docs` command
  lands on PATH via the `[project.scripts]` entry-point — same binary
  the PyPI user gets. (Pre-Phase-6, invoke as
  `.venv/bin/python -m docs_cli.cli …`.)
- Quality gates run **tree-wide**: `ruff check .`, `ruff format --check .`, and `mypy` (no args — `pyproject.toml` scopes it to `src/` + `tests/`). Commit once per TDD phase on the active branch.
- The dogfood snapshot (`tests/fixtures/expected/docs-INDEX.md`) is spec-compliant, not hand-authored. If you change a `docs/*.md` body so its first paragraph or `Updated:` line changes, regenerate `docs/INDEX.md` and the snapshot in lockstep (`docs index --root docs`, then copy `docs/INDEX.md` onto the fixture). Editing a doc means bumping that doc's own `Updated:` per the convention.
- `docs mv` rewrites `Related:` metadata bullets only — prose markdown links in bodies are deliberately left alone (see the M2 Phase 9 log). `docs check` likewise validates `Related:` paths, not prose links.
- `docs check`'s `malformed` rule covers a **missing H1 only** — `parse_metadata_block` ends the metadata block at the first non-label line rather than raising, so a malformed in-block line is not separately detectable (M3 Phase 5 decision).
- INDEX markers quoted in a doc's preamble must be backtick-styled inline code, so the line-anchored detector (`_find_marker_lines`) does not false-match them.
- The metadata block may contain one blank line between the inline `Label: value` run and a trailing bare-label group (`Related:` + bullets). `_metadata_line_span` in `src/docs_cli/cli.py` is the single source of that block-boundary rule.
- Git author email for this repo is `art@bitholdersinc.com` (locally configured), not the `art@trucktech.in` default from `~/CLAUDE.md`.
- M7 (v1.2.0) renames the controlled-vocab field from `Status:` to `Lifecycle:` on disk — breaking, no backward-compat alias. References to `Status:` inside M1-M5 historical log narrative are deliberately preserved verbatim (the field-name swap is the only on-disk change). Bundled skill references at `src/docs_cli/skill/references/` must be resynced from `docs/{convention,cli}.md` in lockstep — `tests/test_skill_refs.py` enforces byte-equality.
