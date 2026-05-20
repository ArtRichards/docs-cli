# M1 — Implementation Log

Status: active
Role: log
Project: docs
Updated: 2026-05-20

Related:
- child-of: m1-parser-and-index.md
- pairs-with: status.md

## Implementation metadata

- Project: docs
- Milestone: M1 — Parser and `docs index`
- Started: 2026-05-20
- Progress: Phase 1 (Define Contract) — not yet started; foundations complete

(Note: doc-lifecycle status is in the front-matter `Status:` field above. This
section tracks milestone progress, which is distinct.)

## Summary

Implement the parser, walker, and `docs index` subcommand. Foundational milestone: every later verb depends on the parser + walker. No mutating verbs in this milestone.

## TDD Phase Progress

| Phase | Status | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Pending | — | — |
| 2. Write Tests (RED) | Pending | — | — |
| 3. Create Data/Fixtures | Pending | — | — |
| 4. Run Tests (RED Baseline) | Pending | — | — |
| 5. Update Base Interfaces | Pending | — | — |
| 6. Implement Offline/Core Path | Pending | — | — |
| 7. Update Tool/Wrapper Layer | Pending | — | — |
| 8. Run Tests (GREEN) | Pending | — | — |
| 9. Dogfood pass | Pending | — | — |
| 10. Quality, Docs, Refactor | Pending | — | — |

## Current State Analysis

- **Codebase:** No source code. `tests/` contains only `.gitkeep`.
- **Docs:** Eleven Markdown files in `docs/` plus this log. All hand-authored.
- **Build/test infra:** None. `pyproject.toml` does not yet exist.
- **Install path:** Intended `~/bin/docs` symlink to `~/opt/docs/docs`; symlink not yet created.

## Files to Create / Modify

| File | Action | Phase | Notes |
|---|---|---|---|
| `docs` (executable) | Create | 1, 5, 6, 7 | Single-file Python script |
| `pyproject.toml` | Create | 5 | Project metadata + dev deps (pytest, ruff, mypy) |
| `tests/test_model.py` | Create | 2 | Parser unit tests |
| `tests/test_walker.py` | Create | 2 | Walker unit tests |
| `tests/test_index.py` | Create | 2 | Index render unit tests |
| `tests/test_cli_index.py` | Create | 2 | End-to-end CLI tests via subprocess |
| `tests/fixtures/parser/*.md` | Create | 3 | Single-doc parser fixtures |
| `tests/fixtures/trees/minimal/` | Create | 3 | Smallest valid tree |
| `tests/fixtures/trees/with-archive/` | Create | 3 | Active + archive subtree |
| `tests/fixtures/trees/marker-preservation/` | Create | 3 | INDEX with hand-edited regions |
| `docs/status.md` | Modify | 10 | M1 → Complete, M2 → ACTIVE |
| `docs/plan.md` | Modify | 10 | If M1 work surfaces plan changes |
| `docs/INDEX.md` | Regenerate | 9, 10 | Via `./docs index docs/` |

## Phase logs

_Phase logs are appended below as each phase completes._

<!-- Phase 1 log goes here -->

<!-- Phase 2 log goes here -->

<!-- ...etc... -->
