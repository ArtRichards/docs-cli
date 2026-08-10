# M25 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-08-10

Related:
- child-of: m25-reciprocal-relationship-integrity.md
- pairs-with: m25-reciprocal-relationship-integrity.md
- pairs-with: status.md
- references: feedback-log.md

## Overview

Chronological implementation log for M25 — Reciprocal relationship integrity
and `docs relate`. Append one evidence-backed section per TDD phase; keep the
progress table and milestone checklist synchronized.

## Implementation metadata

- Project: docs
- Milestone: M25 — Reciprocal relationship integrity and `docs relate`
- Started: 2026-08-10 (milestone setup; no TDD phase started)
- Progress: **Milestone setup complete. Phase 1 — Define Contract is next.**
- Source: the operator-confirmed relationship, repair, archive-audit, and
  release-ordering decisions in `feedback-log.md` (2026-08-09/10).
- Branch: `m25-m29/milestone-setup` for setup; implementation branches are
  chosen when Phase 1 begins.

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Pending | — | Freeze inverse/finding/CLI/audit/atomicity/version contract. |
| 2. Write Tests (RED) | Pending | — | Validation + paired mutation + archive boundaries. |
| 3. Create Data/Fixtures | Pending | — | Reciprocal, missing, excluded, malformed, archived pairs. |
| 4. Run Tests (RED Baseline) | Pending | — | Capture intended failure set. |
| 5. Update Base Interfaces | Pending | — | Inverse/edit/audit planning primitives. |
| 6. Implement Offline/Core Path | Pending | — | Checker + coordinated idempotent edits. |
| 7. Update Tool/Wrapper Layer | Pending | — | CLI, JSON/dry-run, docs, bundled skill, version. |
| 8. Run Tests (GREEN) | Pending | — | Full product and quality gates. |
| 9. Integrate / Accept / Dogfood | Pending | — | Real upgrade/repair flows on a throwaway tree. |
| 10. Quality, Docs, Refactor | Pending | — | Simplify, close docs, completion summary. |

## Setup record — 2026-08-10

### Objective

Promote completed relationship-model discovery into a risk-bounded v2.0
milestone train and prepare the first implementation milestone without starting
Phase 1.

### Actions taken

- Registered M25–M29 in execution order using reciprocal sequence edges.
- Kept durable dependency edges distinct: M28 depends on M27; M29 depends on
  all four implementation milestones.
- Scoped M25 to the confirmed first boundary: semantics, hard validation,
  explicit two-endpoint repair, and narrowly audited archived repair.
- Recorded remaining command/output/audit/failure/version choices for Phase 1.
- Mapped acceptance to real agent workflows: local navigation, upgrade repair,
  and audited historical repair.

### Verification

- `.venv/bin/ruff check .` — passed.
- `.venv/bin/ruff format --check .` — 43 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 44 source files.
- `.venv/bin/python -m pytest -q` — 636 passed.
- `.venv/bin/docs check --root docs` — no violations.

### Decisions / issues

- No bulk repair: the agent must decide whether an edge should be completed or
  removed.
- M26 owns archive authorization, M27/M28 own body links, and M29 owns release.
- The shipped bundle-only use-case catalog remains the project source of truth;
  M25 Phase 10 updates it only when the behavior exists.

## Phase 1 — Define Contract

_Not started._

## Milestone completion summary

_Not complete._
