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

**M4 — Migration helper (`docs migrate`) is in flight.** Activated 2026-05-22;
the contract-and-RED phases (1-4) are underway. M4 adds one verb —
`docs migrate <dir>` — that adopts a non-conforming directory into the
convention: it walks a foreign tree, infers the required metadata per file, and
produces a migration plan (dry-run by default; `--apply` writes). See
[m4-migration-helper.md](m4-migration-helper.md) for the ten-phase plan and
[m4-migration-helper-log.md](m4-migration-helper-log.md) for the per-phase log
(its phase table is the detailed tracker).

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
| M4 — Migration helper (`docs migrate`) | **In flight** (started 2026-05-22) | [Plan](m4-migration-helper.md) | [Log](m4-migration-helper-log.md) |
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
3. `docs/m4-migration-helper.md` — the **in-flight** milestone's task plan: the ten-phase TDD plan, Decisions, and Success Criteria for `docs migrate`
4. `docs/m4-migration-helper-log.md` — M4's per-phase log; check the phase table for where work stands
5. `docs/plan.md` — five-milestone roadmap; M1–M3 are shipped, **M4 is in flight**. Read the M4 section and the Resolved / Open questions.
6. `docs/cli.md` — the command spec; the full `docs` command surface
7. `docs/m3-validation-and-query.md` — most recently shipped milestone; its **Milestone-completion summary** lists the M3 code surface (`check` / `list` + the validation/query helpers M4 reuses)
8. `docs/m1-parser-and-index.md`, `docs/m2-mutating-verbs.md` — the parser / walker / renderer / config / mutating-verb surface M4 builds on
9. `docs/convention.md`, `docs/architecture.md` — the specs the implementation must satisfy
10. `docs/definition-of-ready.md` — the gate to clear before a milestone's implementation starts

**Verify environment** before doing any work:
```sh
cd ~/opt/docs
.venv/bin/python -m pytest tests/ -q          # M4 phases 1-4: 48 failed, 165 passed (intended RED)
.venv/bin/ruff check .                        # All checks passed!
.venv/bin/ruff format --check .               # all files formatted
.venv/bin/mypy                                # Success (tree-wide)
./bin/docs check docs/                        # dogfood — exit 0
./bin/docs index --root docs/ --dry-run       # smoke: idempotent dogfood
```
The 48 failures are M4's RED baseline — every one is a `NotImplementedError`
from a Phase-1 stub that Phases 5-7 implement. M1/M2/M3's 164 tests plus
`migrate --help` are green. If `.venv/` is missing (fresh clone):
```sh
python3 -m venv .venv                         # needs python3-venv on Debian/Ubuntu
.venv/bin/pip install pytest ruff mypy
```

**Next action: resume M4 — Migration helper (`docs migrate`) at Phase 5
(Update Base Interfaces).** Phases 1-4 are complete on branch `m4/phases-1-4`
— the contract is defined, the RED tests and `foreign/` fixture tree are
written, and the RED baseline is captured. Phase 5 implements the pure
inference helpers (`infer_role`, `infer_project`, `infer_status`,
`infer_updated`, `detect_archive_layout`) and `insert_metadata_block`. The M4
log's phase table tracks progress; see the M4 task plan's TDD Implementation
Plan for each phase's scope.

**Watch out for** (durable gotchas, still current):
- The executable is at `bin/docs`, **not** `docs` at repo root — `~/opt/docs/docs/` is the documentation directory; a same-name file would collide.
- Quality gates run **tree-wide**: `ruff check .`, `ruff format --check .`, and `mypy` (no args — `pyproject.toml` scopes it to `bin/docs` + `tests/`). Commit once per TDD phase on `main`.
- The dogfood snapshot (`tests/fixtures/expected/docs-INDEX.md`) is spec-compliant, not hand-authored. If you change a `docs/*.md` body so its first paragraph or `Updated:` line changes, regenerate `docs/INDEX.md` and the snapshot in lockstep (`./bin/docs index --root docs`, then copy `docs/INDEX.md` onto the fixture). Editing a doc means bumping that doc's own `Updated:` per the convention.
- `docs mv` rewrites `Related:` metadata bullets only — prose markdown links in bodies are deliberately left alone (see the M2 Phase 9 log). `docs check` likewise validates `Related:` paths, not prose links.
- `docs check`'s `malformed` rule covers a **missing H1 only** — `parse_metadata_block` ends the metadata block at the first non-label line rather than raising, so a malformed in-block line is not separately detectable (M3 Phase 5 decision).
- INDEX markers quoted in a doc's preamble must be backtick-styled inline code, so the line-anchored detector (`_find_marker_lines`) does not false-match them.
- The metadata block may contain one blank line between the inline `Label: value` run and a trailing bare-label group (`Related:` + bullets). `_metadata_line_span` in `bin/docs` is the single source of that block-boundary rule.
- Git author email for this repo is `art@bitholdersinc.com` (locally configured), not the `art@trucktech.in` default from `~/CLAUDE.md`.
