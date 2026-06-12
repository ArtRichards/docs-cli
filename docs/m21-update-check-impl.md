# M21 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-06-12

Related:
- child-of: m21-update-check.md
- pairs-with: m21-update-check.md
- pairs-with: status.md

## Overview

Chronological log of work on M21 — Update-check notification (PyPI version
check + skill-refresh nudge). Append a section per TDD phase with objective,
files changed, actions, test results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M21 — Update-check notification (PyPI version check + skill-refresh
  nudge) (v1.7.0)
- Started: 2026-06-12 (scaffolded — milestone-setup; no TDD phase started)
- Progress: **Milestone pair scaffolded 2026-06-12** from the operator-directed
  M21 scope (design + precedent researched and operator-reviewed this session).
  Headline: `docs-cli` checks PyPI for a newer release and, once per 24h and
  fail-silent, emits ONE STDERR line nudging the user/agent to update **both**
  the CLI (`pip install -U docs-cli`) and their installed skills
  (`docs install-skill --force`) — automating the CLAUDE.md ship-time flow.
  This is the tool's **first network surface** (stdlib `urllib` only, short
  timeout, 24h-cache-gated, fail-silent always — zero-dependency wheel
  preserved). The notice is STDERR-only, never alters the exit code, and is
  suppressed under `--quiet` / `--json` / CI / `DOCS_CLI_NO_UPDATE_CHECK` /
  `DO_NOT_TRACK` (a user-level config opt-out is DEFERRED out of v1.7.0 —
  OQ-5/5a) — but
  **deliberately shows on non-TTY** (inverting gh's TTY rule) because the agent
  is the actor who performs the update. A zero-network skill-drift
  notice (D5, ships IN — OQ-6) catches the exact host drift found 2026-06-12.
  Ships as **1.7.0 locally** (minor bump — additive feature; 1.6.5 was the
  operator-decreed patch exception); the PyPI publish is a later operator-driven
  milestone (M19→M20, M14+M15→M17 pattern). Depends on nothing; nothing else in
  flight. **No TDD phase started** — milestone-setup only. OPEN QUESTIONS OQ-1
  through OQ-9 are **RESOLVED** (conductor decisions 2026-06-12, each per the
  recommended default the draft was written against — see the milestone doc's
  Decisions › "Resolved questions"); milestone-setup is complete and Phase 1
  (Define Contract) is next.

(Note: doc-lifecycle status is the front-matter `Lifecycle:` field. This
section tracks implementation progress, which is distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Pending | — | — |
| 2. Write Tests (RED) | Pending | — | — |
| 3. Create Data/Fixtures | Pending | — | — |
| 4. Run Tests (RED Baseline) | Pending | — | — |
| 5. Update Base Interfaces | Pending | — | — |
| 6. Implement Offline/Core Path | Pending | — | — |
| 7. Update Tool/Wrapper Layer | Pending | — | — |
| 8. Run Tests (GREEN) | Pending | — | — |
| 9. Implement Online/Integration | Pending | — | — |
| 10. Quality, Docs, Refactor | Pending | — | — |

## Provenance — where the scope came from

Operator-directed M21 scope (2026-06-12). The headline: docs-cli checks PyPI
for a newer version and notifies that the user/agent should update both the CLI
and their installed skills. The motivating miss is on this very host — the M20
publish-closeout host-skill sweep (2026-06-12) caught a stale
`docs new --body-from` "first 20 lines" reference in the `project-foundation`
workflow skill, the pre-M19-D3 heuristic; the drift was only catchable at
publish time, by hand. M21 makes the update signal self-announcing at every
invocation instead.

Design + precedent were researched and operator-reviewed this session and are
recorded in the milestone doc's Decisions: gh CLI's 24h persisted-timestamp
notifier (cli/cli#85, #743 — TTY-gated, `GH_NO_UPDATE_NOTIFIER`, CI skip), npm
`update-notifier` (1-day default, deferred notify-next-run, `NO_UPDATE_NOTIFIER`,
auto-skip CI/test), Terraform Checkpoint (`CHECKPOINT_DISABLE`), pip's always-on
notice as the anti-pattern (CI noise, stream regressions), and aider as the
agent-CLI precedent (default-on launch check, exit-code machine mode, disable
toggle). M21's deliberate departure is the **TTY inversion** — show on non-TTY
too, because the agent is the actor.

Code anchors (verified against the current tree at scaffold time, 2026-06-12):

- `__version__` (`cli.py:44`) — `importlib.metadata.version("docs-cli")`, the
  M12 SoT, with the `0.0.0+local` `PackageNotFoundError` fallback. This is the
  string the PyPI `info.version` compares against (and the `0.0.0+local` /
  pre-release fail-closed guard — OQ-3).
- `main()` (`cli.py:5194`) — the flat dispatch returning an `int` exit code.
  The update-check hook lands here, AFTER the command runs and BEFORE `main`
  returns, emitting only to STDERR and passing the command's exit code through
  untouched.
- `--quiet` / `--json` are **per-verb** argparse flags (no global namespace
  attr on every verb) — the hook reads them defensively (OQ-1).
- `install-skill` default dest (`~/.claude/skills/docs/`, `cli.py:3329`;
  `_cmd_install_skill` resolves it at `cli.py:5124`) + the bundled skill via
  `importlib.resources` — everything D5's offline skill-drift compare needs.
- No existing network/cache surface anywhere (`grep urllib|http|socket|.cache|
  XDG_CACHE src/` → zero hits) — M21 is the first.
- `tests/test_packaging.py` A3 (`test_a3_project_version_is_1_6_5`, line ~100)
  + B1/B2/C2 (lines ~192/204/326) + `pyproject.toml` `version = "1.6.5"` — the
  version-pin + bump to `1.7.0` (D7), the A3-fast / B1-B2-C2-slow split (M19
  precedent).
- Lockstep: `tests/test_skill_refs.py` (bundled `references/{cli,convention}.md`
  byte-identical to `docs/`), `tests/fixtures/expected/docs-INDEX.md` (frozen
  INDEX snapshot kept identical to `docs/INDEX.md`).

See [m21-update-check.md](m21-update-check.md) Decisions for the full contract
analysis and the OQ-1..OQ-9 resolutions (all RESOLVED 2026-06-12, each per the
recommended default; the OPEN QUESTIONS analysis is retained as historical
record).

## Phase 1 — Define Contract

_Not started._
