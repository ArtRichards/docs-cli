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
**Current phase:** Phase 2 — Write Tests (RED) (next; Phase 1 complete)

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
- [Architecture](architecture.md) — module sketch
- [Plan](plan.md) — five-milestone roadmap
- [Definition of Ready](definition-of-ready.md) — gate to start
