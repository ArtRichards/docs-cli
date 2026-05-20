# docs — Status

Status: active
Role: status
Project: docs
Updated: 2026-05-20

Related:
- pairs-with: plan.md
- pairs-with: m1-parser-and-index.md

**This is the single source of truth for project progress. Update only this file when milestones complete or phases advance.**

## Current milestone

**Active:** M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`)

**Task plan:** _not yet created (created at the start of M2)_
**Implementation log:** _not yet created (created at the start of M2)_
**Current phase:** _M2 not yet started_

M1 — Parser and `docs index` shipped 2026-05-20 across ten TDD phases.
See [m1-parser-and-index-log.md](m1-parser-and-index-log.md) for the
per-phase history and [m1-parser-and-index.md](m1-parser-and-index.md)
for the milestone summary.

## Milestone progress

| Milestone | Status | Task plan | Log |
|---|---|---|---|
| M1 — Parser and `docs index` | **Complete** (2026-05-20) | [Plan](m1-parser-and-index.md) | [Log](m1-parser-and-index-log.md) |
| M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) | **ACTIVE** | _not yet created_ | _not yet created_ |
| M3 — Validation and query (`check`, `list`) | Pending | _not yet created_ | _not yet created_ |
| M4 — Migration helper (`docs migrate`) | Pending | _not yet created_ | _not yet created_ |
| M5 — Claude Code skill | Pending | _not yet created_ | _not yet created_ |

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
3. `docs/plan.md` — five-milestone roadmap (M2 scope is the active section)
4. `docs/m1-parser-and-index.md` — completed M1 milestone doc; scan the **Milestone-completion summary** at the bottom for the code surface, the design decisions, and the lessons compounded
5. `docs/m1-parser-and-index-log.md` — per-phase history; skim entries that look relevant. The Phase 9 entry documents a real renderer bug (substring vs line-anchored marker detection); the Phase 5 entry documents the Vocab deferral and the convention.md blank-line nuance.
6. `docs/convention.md`, `docs/architecture.md`, `docs/cli.md` — the specs the implementation must satisfy
7. (Optional) `~/.claude/plans/` — historical Claude Code plan files; M1's are archived. M2 will author its own plan files there.

**Verify environment** before doing any work:
```sh
cd ~/opt/docs
.venv/bin/python -m pytest tests/ -q          # expect: 58 passed
.venv/bin/ruff check .                        # All checks passed!
.venv/bin/ruff format --check .               # 7 files already formatted
.venv/bin/mypy bin/docs                       # Success
./bin/docs index --root docs/ --dry-run       # smoke: idempotent dogfood
```
If `.venv/` is missing (fresh clone):
```sh
python3 -m venv .venv                         # needs python3-venv on Debian/Ubuntu
.venv/bin/pip install pytest ruff mypy
```

**Next action: kick off M2.** Author `docs/m2-mutating-verbs.md` (the milestone task plan) and `docs/m2-mutating-verbs-log.md`. Re-run the ten-phase TDD cycle for the four mutating verbs: `new`, `archive`, `mv`, `touch`. Reuse the Phase 5 `atomic_write` helper, the `parse`/`walk` core, and the argparse harness from Phase 7. See [plan.md](plan.md) for the M2 scope summary.

**Watch out for** (issues already resolved but worth knowing):
- The executable is at `bin/docs`, **not** `docs` at repo root — `~/opt/docs/docs/` is the documentation directory; same-name file would collide.
- The dogfood snapshot (`tests/fixtures/expected/docs-INDEX.md`) is now spec-compliant, not hand-authored. If you edit a body in `docs/*.md`, the renderer's "first paragraph" extraction changes — regenerate both `docs/INDEX.md` and the snapshot in lockstep. The Phase 9 + consistency-sweep commits show the workflow.
- Markers in the preamble must be quoted in backticks (or otherwise not appear as a standalone line). The line-anchored detector (`_find_marker_lines` in `bin/docs`) prevents false-matches but only when prose mentions are styled as inline code.
- The metadata-block rule in `convention.md` is more permissive than the original "ends at first blank line" wording: a blank line is allowed between inline `Label: value` lines and a following bare-label multi-value group (e.g. `Related:` + bullets). Both the parser and every project doc use this style. The convention text was rewritten in the post-M1 audit to match practice — read the "Metadata block" section if writing a new doc.
- This repo uses `art@bitholdersinc.com` as git author email (locally configured), not the `art@trucktech.in` default from `~/CLAUDE.md`. Memory entry at `~/.claude/projects/-home-user/memory/project_docs_cli.md` records this.
- Quality-gate scope: `ruff check .` / `ruff format --check .` / `mypy` should run **tree-wide**, not just over `bin/docs`. Phases 1–7 only checked the executable and missed lint debt in `tests/` that Phase 8 found. The configured `mypy` (no args) covers `bin/docs` + `tests/` per `pyproject.toml`.
