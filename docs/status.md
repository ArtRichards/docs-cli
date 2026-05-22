# docs — Status

Status: active
Role: status
Project: docs
Updated: 2026-05-22

Related:
- pairs-with: plan.md
- pairs-with: m1-parser-and-index.md

**This is the single source of truth for project progress. Update only this file when milestones complete or phases advance.**

## Current milestone

**M3 — Validation and query (`check`, `list`) is in flight.** Started 2026-05-22.

- Task plan: [m3-validation-and-query.md](m3-validation-and-query.md)
- Implementation log: [m3-validation-and-query-log.md](m3-validation-and-query-log.md)

M3 adds two read-only verbs — `docs check` (validate the tree, with CI-usable
exit codes) and `docs list` (filterable query view with a stable JSON schema) —
and regroups `INDEX.md` by `Project` then `Role`. Phases 1–4 (contract, RED
tests, fixtures, RED baseline) run first; the session **pauses at the RED
baseline**, and phases 5–10 resume implementation.

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
| M3 — Validation and query (`check`, `list`) | **In flight** (started 2026-05-22) | [Plan](m3-validation-and-query.md) | [Log](m3-validation-and-query-log.md) |
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
3. `docs/plan.md` — five-milestone roadmap; M1 and M2 are shipped, **M3 is in flight**. Read the M3 section and the Resolved / Open questions.
4. `docs/cli.md` — the command spec; the `docs check` and `docs list` subsections are the M3 contract
5. `docs/m2-mutating-verbs.md` — most recently shipped milestone; the **Milestone-completion summary** lists the M2 code surface (four verbs + shared helpers)
6. `docs/m2-mutating-verbs-log.md` — M2 per-phase history, for implementation detail
7. `docs/m1-parser-and-index.md` — M1 summary: the parser / walker / renderer / config surface M3 builds on
8. `docs/convention.md`, `docs/architecture.md` — the specs the implementation must satisfy
9. `docs/definition-of-ready.md` — the gate to clear before M3 implementation starts

**Verify environment** before doing any work:
```sh
cd ~/opt/docs
.venv/bin/python -m pytest tests/ -q          # M3 in flight: M1/M2 green; M3 + reworked INDEX tests RED at the Phase 4 baseline
.venv/bin/ruff check .                        # All checks passed!
.venv/bin/ruff format --check .               # all files formatted
.venv/bin/mypy                                # Success (tree-wide)
./bin/docs index --root docs/ --dry-run       # smoke: idempotent dogfood
```
If `.venv/` is missing (fresh clone):
```sh
python3 -m venv .venv                         # needs python3-venv on Debian/Ubuntu
.venv/bin/pip install pytest ruff mypy
```

**Next action: resume M3 at Phase 5 — Update Base Interfaces.** Phases 1–4
(contract, RED tests, fixtures, RED baseline) are complete; the session paused
at the RED baseline by request. Phase 5 implements the shared helpers
(`_iter_doc_texts`, `check_doc`, `exit_code_for`, `_resolved_project`) and the
INDEX Project→Role renderer rework; phases 6–10 finish the verbs and ship. See
[m3-validation-and-query.md](m3-validation-and-query.md) for the full phase plan
and [m3-validation-and-query-log.md](m3-validation-and-query-log.md) for
per-phase history. M3's exit criteria: `docs check` returns 0 on this repo's
own `docs/`, and `docs list --json` matches the schema pinned in `cli.md`.

**Watch out for** (durable gotchas, still current):
- The executable is at `bin/docs`, **not** `docs` at repo root — `~/opt/docs/docs/` is the documentation directory; a same-name file would collide.
- Quality gates run **tree-wide**: `ruff check .`, `ruff format --check .`, and `mypy` (no args — `pyproject.toml` scopes it to `bin/docs` + `tests/`). Commit once per TDD phase on `main`.
- The dogfood snapshot (`tests/fixtures/expected/docs-INDEX.md`) is spec-compliant, not hand-authored. If you change a `docs/*.md` body so its first paragraph or `Updated:` line changes, regenerate `docs/INDEX.md` and the snapshot in lockstep (`./bin/docs index --root docs`, then copy `docs/INDEX.md` onto the fixture). Editing a doc means bumping that doc's own `Updated:` per the convention.
- `docs mv` rewrites `Related:` metadata bullets only — prose markdown links in bodies are deliberately left alone (see the M2 Phase 9 log). Relevant to M3: `docs check` validates `Related:` paths, not prose links.
- INDEX markers quoted in a doc's preamble must be backtick-styled inline code, so the line-anchored detector (`_find_marker_lines`) does not false-match them.
- The metadata block may contain one blank line between the inline `Label: value` run and a trailing bare-label group (`Related:` + bullets). `_metadata_line_span` in `bin/docs` is the single source of that block-boundary rule.
- Git author email for this repo is `art@bitholdersinc.com` (locally configured), not the `art@trucktech.in` default from `~/CLAUDE.md`.
