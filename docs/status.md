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

**Active:** M1 — Parser and `docs index`

**Task plan:** [m1-parser-and-index.md](m1-parser-and-index.md)
**Implementation log:** [m1-parser-and-index-log.md](m1-parser-and-index-log.md)
**Current phase:** Phase 8 — Run Tests (GREEN) (next; Phases 1–7 complete)

## Milestone progress

| Milestone | Status | Task plan | Log |
|---|---|---|---|
| M1 — Parser and `docs index` | **ACTIVE** | [Plan](m1-parser-and-index.md) | [Log](m1-parser-and-index-log.md) |
| M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) | Pending | _not yet created_ | _not yet created_ |
| M3 — Validation and query (`check`, `list`) | Pending | _not yet created_ | _not yet created_ |
| M4 — Migration helper (`docs migrate`) | Pending | _not yet created_ | _not yet created_ |
| M5 — Claude Code skill | Pending | _not yet created_ | _not yet created_ |

Per-milestone task plans are created when each milestone is activated, not all up front.

## TDD phase order (for the active milestone)

1. Define Contract
2. Write Tests (RED)
3. Create Data/Fixtures
4. Run Tests (RED Baseline)
5. Update Base Interfaces
6. Implement Offline/Core Path
7. Update Tool/Wrapper Layer
8. Run Tests (GREEN)
9. Implement Online/Integration (N/A for M1; mapped to dogfooding pass)
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
3. `docs/m1-parser-and-index.md` — current milestone TDD plan
4. `docs/m1-parser-and-index-log.md` — per-phase history (skim Phase 1–4 entries)
5. `docs/convention.md`, `docs/architecture.md`, `docs/cli.md` — the specs the implementation must satisfy
6. (Optional) `~/.claude/plans/start-m1-phase-1-quiet-bonbon.md` — the full execution plan with design choices the Plan agent surfaced

**Verify environment** before doing any work:
```sh
cd ~/opt/docs
.venv/bin/python -m pytest tests/ -q          # expect: 54 failed, 3 passed
```
If `.venv/` is missing (fresh clone):
```sh
python3 -m venv .venv                         # needs python3-venv on Debian/Ubuntu
.venv/bin/pip install pytest ruff mypy
```
Then re-run pytest; baseline = **54 failed, 3 passed in <1s**. All failures are `NotImplementedError`. This is the expected RED state.

**Next action: Phase 8 — Run Tests (GREEN).** Run the full quality gate (`pytest -q`, `ruff check .`, `ruff format --check .`, `mypy bin/docs`). All except `test_index_output_matches_frozen_snapshot` should be green — 56/57. Phase 8 will likely fold into Phase 9 since the only outstanding failure is the dogfood snapshot match; decide at the top of Phase 8 whether to run as a no-op gate check + log entry, or merge into Phase 9's reconciliation work.

**Watch out for** (issues already resolved but worth knowing):
- The executable is at `bin/docs`, **not** `docs` at repo root — `~/opt/docs/docs/` is the documentation directory; same-name file would collide.
- Two false-pass tests at the RED baseline (logged in Phase 4 entry of m1 log). Tighten them when their target functions land.
- This repo uses `art@bitholdersinc.com` as git author email (locally configured), not the `art@trucktech.in` default from `~/CLAUDE.md`. Memory entry at `~/.claude/projects/-home-user/memory/project_docs_cli.md` records this.
