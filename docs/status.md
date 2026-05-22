# docs — Status

Status: active
Role: status
Project: docs
Updated: 2026-05-22

Related:
- pairs-with: plan.md
- pairs-with: m5-claude-code-skill.md

**This is the single source of truth for project progress. Update only this file when milestones complete or phases advance.**

## Current milestone

**M5 — Claude Code skill is in flight (activated 2026-05-22).** M1-M4 are
shipped. M5 is the final v1 milestone: a Claude Code skill (a `SKILL.md`
artifact at `skills/docs/`) that makes an agent reach for the `docs` verbs
automatically when doing documentation work in a `docs`-managed tree. It adds
no CLI surface — it is a markdown artifact whose `description` triggers on the
right contexts and whose body redirects to the appropriate `docs` verb instead
of hand-editing metadata or `INDEX.md`. The task plan and log were created on
`m5/milestone-setup`; the four milestone-setup OPEN QUESTIONS (OQ1-OQ4 —
chiefly how the ten-phase TDD cycle maps onto a markdown artifact) are resolved
(operator-confirmed 2026-05-22) and recorded as Decisions in the task plan. The
ten TDD phases have not yet started; Phase 1 (Define Contract) is the next
action. See [m5-claude-code-skill.md](m5-claude-code-skill.md) for the
per-phase task plan and the Decisions, and
[m5-claude-code-skill-log.md](m5-claude-code-skill-log.md) for the log.

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
| M5 — Claude Code skill | **In flight** (started 2026-05-22) | [Plan](m5-claude-code-skill.md) | [Log](m5-claude-code-skill-log.md) |

Per-milestone task plans are created when each milestone is activated, not all up front.

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
- [Plan](plan.md) — five-milestone roadmap
- [Definition of Ready](definition-of-ready.md) — gate to start

## Resuming this work (fresh session)

If you're starting a new Claude Code session against this repo:

**Reading order** (≤ 10 minutes):
1. `~/CLAUDE.md` — host-level guidance + memory pointers
2. `docs/status.md` — this file
3. `docs/plan.md` — five-milestone roadmap; M1–M4 are shipped, **M5 is in flight**. Read the M5 section and the Resolved / Open questions.
4. `docs/m5-claude-code-skill.md` — the **active milestone's task plan**: the ten-phase plan and the Decisions (the four milestone-setup questions OQ1-OQ4 are resolved and recorded there)
5. `docs/m5-claude-code-skill-log.md` — the M5 log and the trigger-scenario checklist
6. `docs/cli.md` — the command spec; the full `docs` command surface the skill redirects to
7. `docs/m4-migration-helper.md` — most recently shipped milestone; its **Milestone-completion summary** lists the full M1-M4 verb + code surface the skill drives
8. `docs/convention.md`, `docs/architecture.md` — the specs the skill points at (and must not re-teach)
9. `docs/charter.md` — what + why
10. `docs/definition-of-ready.md` — the gate cleared before implementation; its risk register parks the cross-host-portability risk explicitly for M5

**Verify environment** before doing any work:
```sh
cd ~/opt/docs
.venv/bin/python -m pytest tests/ -q          # 236 passed (M1-M4 all green)
.venv/bin/ruff check .                        # All checks passed!
.venv/bin/ruff format --check .               # all files formatted
.venv/bin/mypy                                # Success (tree-wide)
./bin/docs check docs/                        # dogfood — exit 0
./bin/docs index --root docs/ --dry-run       # smoke: idempotent dogfood
```
All 236 tests pass — M1-M4 are shipped. If `.venv/` is missing (fresh clone):
```sh
python3 -m venv .venv                         # needs python3-venv on Debian/Ubuntu
.venv/bin/pip install pytest ruff mypy
```

**Next action: M5 — Claude Code skill is in flight; begin Phase 1.** M1-M4 are
complete. M5 is the final milestone — a Claude Code skill (`SKILL.md` artifact)
that drives the `docs` CLI. The task plan and log exist
([m5-claude-code-skill.md](m5-claude-code-skill.md),
[m5-claude-code-skill-log.md](m5-claude-code-skill-log.md)) and the four
milestone-setup OPEN QUESTIONS (OQ1-OQ4) are resolved and recorded as Decisions
in the task plan. The next action is Phase 1 (Define Contract): create
`skills/docs/SKILL.md` with valid frontmatter and a stub body, and
`tests/test_skill.py` with check signatures.

**Watch out for** (durable gotchas, still current):
- The executable is at `bin/docs`, **not** `docs` at repo root — `~/opt/docs/docs/` is the documentation directory; a same-name file would collide.
- Quality gates run **tree-wide**: `ruff check .`, `ruff format --check .`, and `mypy` (no args — `pyproject.toml` scopes it to `bin/docs` + `tests/`). Commit once per TDD phase on `main`.
- The dogfood snapshot (`tests/fixtures/expected/docs-INDEX.md`) is spec-compliant, not hand-authored. If you change a `docs/*.md` body so its first paragraph or `Updated:` line changes, regenerate `docs/INDEX.md` and the snapshot in lockstep (`./bin/docs index --root docs`, then copy `docs/INDEX.md` onto the fixture). Editing a doc means bumping that doc's own `Updated:` per the convention.
- `docs mv` rewrites `Related:` metadata bullets only — prose markdown links in bodies are deliberately left alone (see the M2 Phase 9 log). `docs check` likewise validates `Related:` paths, not prose links.
- `docs check`'s `malformed` rule covers a **missing H1 only** — `parse_metadata_block` ends the metadata block at the first non-label line rather than raising, so a malformed in-block line is not separately detectable (M3 Phase 5 decision).
- INDEX markers quoted in a doc's preamble must be backtick-styled inline code, so the line-anchored detector (`_find_marker_lines`) does not false-match them.
- The metadata block may contain one blank line between the inline `Label: value` run and a trailing bare-label group (`Related:` + bullets). `_metadata_line_span` in `bin/docs` is the single source of that block-boundary rule.
- Git author email for this repo is `art@bitholdersinc.com` (locally configured), not the `art@trucktech.in` default from `~/CLAUDE.md`.
