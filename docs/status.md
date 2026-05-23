# docs — Status

Status: active
Role: status
Project: docs
Updated: 2026-05-23

Related:
- pairs-with: plan.md
- pairs-with: m6-pypi-distribution.md

**This is the single source of truth for project progress. Update only this file when milestones complete or phases advance.**

## Current milestone

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
2026-05-23). It is the project's final v1 deliverable: a Claude Code
skill — a `SKILL.md` artifact at `skills/docs/` — that makes an agent
reach for the `docs` verbs automatically when doing documentation work
in a `docs`-managed tree. It adds no CLI surface and changes no verb
behaviour: it is a markdown artifact whose `description` triggers on
the right contexts (creating a plan/spec/charter/milestone, archiving
or renaming a doc, listing docs, checking the tree, regenerating
`INDEX.md`, adopting a foreign Markdown directory) and whose body
redirects to the appropriate `docs` verb instead of hand-editing
metadata, `INDEX.md`, or `archive/`. The convention itself is not
re-taught — the body links to the bundled spec references at
`skills/docs/references/`. The four M5 milestone-setup OPEN QUESTIONS
(OQ1-OQ4) were resolved and recorded as Decisions in the task plan.
**Post-ship polish (2026-05-23)** shortened `SKILL.md` to a trigger
surface (verb-task table + when-to-use scenarios + never-hand-edit
rule), bundled `convention.md` and `cli.md` as `skills/docs/references/`
(byte-identical mirrors with a lockstep test), and cleaned dev
cross-refs out of the source specs. See
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
| M6 — PyPI distribution as `docs-cli` | _in flight_ (started 2026-05-23) | [Plan](m6-pypi-distribution.md) | [Log](m6-pypi-distribution-log.md) |

v1 (M1-M5) shipped 2026-05-22. **v1.1 is in flight** with M6 as its first
milestone — PyPI publication, an importable package, and an
`install-skill` verb that places the bundled Claude Code skill on a host
without requiring a repo clone. Per-milestone task plans were created
when each milestone was activated, not all up front.

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
3. `docs/plan.md` — the roadmap; v1 (M1-M5) is shipped, v1.1 has begun with M6 as its first milestone. Read the v1-completion note and the Open questions (the parked extra-field allowlist still carries to v1.1).
4. `docs/m6-pypi-distribution.md` — the active milestone's task plan; "Decisions" records the five milestone-setup OQs resolved 2026-05-23 (the full text is preserved under "OPEN QUESTIONS — resolved").
5. `docs/m6-pypi-distribution-log.md` — the milestone log with the per-phase status table.
6. `docs/cli.md` — the command spec; the full eight-verb `docs` surface.
7. `docs/convention.md`, `docs/architecture.md` — the on-disk format and the module sketch.
8. `docs/m5-claude-code-skill.md` — v1's final milestone; its **Milestone-completion summary** describes the Claude Code skill that M6's `install-skill` verb will deliver via the wheel.
9. `src/docs_cli/skill/SKILL.md` — the M5 deliverable: the Claude Code skill that drives the verbs (relocated to its M6 home under the package source).
10. `docs/charter.md` — what + why.
11. `docs/definition-of-ready.md` — the gate cleared before implementation.

**Verify environment** before doing any work:
```sh
cd ~/opt/docs-cli
.venv/bin/python -m pytest tests/ -q          # 249 passed (Phase 5); 271 after Phase 8
.venv/bin/ruff check .                        # All checks passed!
.venv/bin/ruff format --check .               # all files formatted
.venv/bin/mypy                                # Success (tree-wide)
.venv/bin/python -m docs_cli.cli check docs/  # dogfood — exit 0 (Phase 5; post-Phase-6 use `.venv/bin/docs`)
.venv/bin/python -m docs_cli.cli index --root docs/ --dry-run  # smoke: idempotent dogfood
```
If `.venv/` is missing (fresh clone) or stale shebangs after the M6
working-tree move:
```sh
rm -rf .venv && python3 -m venv .venv         # needs python3-venv on Debian/Ubuntu
.venv/bin/pip install -e ".[dev]"             # post-Phase-6: lands `docs` on PATH; pre-Phase-6: `pytest ruff mypy build`
```

**Next action: Phase 7 — update wrappers (specs/runbook/CHANGELOG, no
CI per operator).** Phase 6 (implement core) is complete on branch
`m6/phases-5-10`. `pyproject.toml` rewritten with hatchling backend,
`name = "docs-cli"`, `version = "1.1.0"`, `[project.scripts] docs =
docs_cli.cli:main`, `[project.urls]` pointing at
`github.com/ArtRichards/docs-cli`, classifiers bumped to Beta + 3.13.
`src/docs_cli/cli.py` carries `__version__ = "1.1.0"`, a global
`--version` flag, the `install-skill` subparser (`--dest`/`--copy`/
`--symlink`/`--force`/`--quiet`), and the `_cmd_install_skill`
handler (importlib.resources lookup, site-packages-ancestor heuristic
for the wheel-symlink refusal, byte-identical idempotency, --force
overwrite, atomic clear-then-write). `docs/cli.md` documents both
`--version` and the new verb; `src/docs_cli/skill/SKILL.md` adds the
new verb to its verbs table; `src/docs_cli/skill/references/cli.md`
resynced. `pip install -e ".[dev]"` lands `docs` on PATH;
`.venv/bin/docs --version` prints `docs 1.1.0`; `python -m build`
produces a clean `docs_cli-1.1.0-py3-none-any.whl` (5 source entries
+ dist-info). **All 271 tests GREEN.**

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
