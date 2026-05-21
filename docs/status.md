# docs — Status

Status: active
Role: status
Project: docs
Updated: 2026-05-21

Related:
- pairs-with: plan.md
- pairs-with: m1-parser-and-index.md

**This is the single source of truth for project progress. Update only this file when milestones complete or phases advance.**

## Current milestone

**Active:** M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`)

**Task plan:** [m2-mutating-verbs.md](m2-mutating-verbs.md)
**Implementation log:** [m2-mutating-verbs-log.md](m2-mutating-verbs-log.md)
**Current phase:** Phase 7 — Update Tool/Wrapper Layer (next). Phases 1–6 complete (contract, tests, fixtures, RED baseline, base interfaces, verb cores).

M1 — Parser and `docs index` shipped 2026-05-20 across ten TDD phases.
See [m1-parser-and-index-log.md](m1-parser-and-index-log.md) for the
per-phase history and [m1-parser-and-index.md](m1-parser-and-index.md)
for the milestone summary.

## Milestone progress

| Milestone | Status | Task plan | Log |
|---|---|---|---|
| M1 — Parser and `docs index` | **Complete** (2026-05-20) | [Plan](m1-parser-and-index.md) | [Log](m1-parser-and-index-log.md) |
| M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) | **ACTIVE** (Phases 1–6 done) | [Plan](m2-mutating-verbs.md) | [Log](m2-mutating-verbs-log.md) |
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
4. `docs/m2-mutating-verbs.md` — active milestone task plan; Phases 1–4 done, Phase 5 next
5. `docs/m2-mutating-verbs-log.md` — M2 per-phase history; read the Phase 4 entry and the **Pre-Phase-1 design note** (subdirectories, the renderer bug, scope)
6. `docs/m1-parser-and-index.md` — completed M1 milestone; the **Milestone-completion summary** has the code surface and design decisions
7. `docs/m1-parser-and-index-log.md` — M1 per-phase history; skim entries that look relevant
8. `docs/convention.md`, `docs/architecture.md`, `docs/cli.md` — the specs the implementation must satisfy

**Verify environment** before doing any work:
```sh
cd ~/opt/docs
.venv/bin/python -m pytest tests/ -q          # expect: 48 failed, 62 passed (M2 RED baseline)
.venv/bin/ruff check .                        # All checks passed!
.venv/bin/ruff format --check .               # all files formatted
.venv/bin/mypy                                # Success (tree-wide)
./bin/docs index --root docs/ --dry-run       # smoke: idempotent dogfood
```

The 48 failures are the expected M2 RED baseline — every mutating verb and
editing helper is a `NotImplementedError` stub. They are the spec for
Phases 5–7; do not "fix" them by deleting tests.
If `.venv/` is missing (fresh clone):
```sh
python3 -m venv .venv                         # needs python3-venv on Debian/Ubuntu
.venv/bin/pip install pytest ruff mypy
```

**Next action: resume M2 at Phase 5 — Update Base Interfaces.** Phases 1–4 (contract, tests, fixtures, RED baseline) are complete — see [m2-mutating-verbs-log.md](m2-mutating-verbs-log.md). Phase 5 implements the three editing helpers (`set_metadata_field`, `rewrite_related_refs`, `scaffold_doc`), extracts `_refresh_index` from `_cmd_index`, and fixes `_format_entry` to emit root-relative INDEX links (the regression test `test_index_nested_doc_link_is_root_relative` goes green). The 48 RED tests are the executable spec; drive them green across Phases 5–7. See [m2-mutating-verbs.md](m2-mutating-verbs.md) for the full phase breakdown.

**Watch out for** (issues already resolved but worth knowing):
- The executable is at `bin/docs`, **not** `docs` at repo root — `~/opt/docs/docs/` is the documentation directory; same-name file would collide.
- The dogfood snapshot (`tests/fixtures/expected/docs-INDEX.md`) is now spec-compliant, not hand-authored. If you edit a body in `docs/*.md`, the renderer's "first paragraph" extraction changes — regenerate both `docs/INDEX.md` and the snapshot in lockstep. The Phase 9 + consistency-sweep commits show the workflow.
- Markers in the preamble must be quoted in backticks (or otherwise not appear as a standalone line). The line-anchored detector (`_find_marker_lines` in `bin/docs`) prevents false-matches but only when prose mentions are styled as inline code.
- The metadata-block rule in `convention.md` is more permissive than the original "ends at first blank line" wording: a blank line is allowed between inline `Label: value` lines and a following bare-label multi-value group (e.g. `Related:` + bullets). Both the parser and every project doc use this style. The convention text was rewritten in the post-M1 audit to match practice — read the "Metadata block" section if writing a new doc.
- This repo uses `art@bitholdersinc.com` as git author email (locally configured), not the `art@trucktech.in` default from `~/CLAUDE.md`. Memory entry at `~/.claude/projects/-home-user/memory/project_docs_cli.md` records this.
- Quality-gate scope: `ruff check .` / `ruff format --check .` / `mypy` should run **tree-wide**, not just over `bin/docs`. Phases 1–7 only checked the executable and missed lint debt in `tests/` that Phase 8 found. The configured `mypy` (no args) covers `bin/docs` + `tests/` per `pyproject.toml`.
