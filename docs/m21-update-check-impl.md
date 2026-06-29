# M21 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-06-29

Related:
- child-of: m21-update-check.md
- pairs-with: m21-update-check.md
- pairs-with: status.md
- references: m23-agent-aware-install-skill.md

## Overview

Chronological log of work on M21 — Update-check notification (PyPI new-version
notice). Append a section per TDD phase with objective, files changed, actions,
test results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M21 — Update-check notification (PyPI new-version notice) (v1.7.0)
- Started: 2026-06-12 (scaffolded — milestone-setup; no TDD phase started)
- Progress: **Milestone pair scaffolded 2026-06-12; re-scoped to CLI-only
  2026-06-29.** Headline: `docs-cli` checks PyPI for a newer release and, once
  per 24h and fail-silent, emits ONE STDERR line nudging the user/agent to
  update **the CLI** (`pip install -U docs-cli`). This is the tool's **first
  network surface** (stdlib `urllib` only, 1.0s timeout, 24h-cache-gated,
  fail-silent always — zero-dependency wheel preserved). The notice is
  STDERR-only, never alters the exit code, and is suppressed under `--quiet` /
  `--json` / CI / `DOCS_CLI_NO_UPDATE_CHECK` / `DO_NOT_TRACK` (a user-level
  config opt-out is DEFERRED out of v1.7.0 — OQ-5/5a) — but **deliberately
  shows on non-TTY** (inverting gh's TTY rule) because the agent is the actor
  who performs the update. The former skill-drift notice (D5) and the
  dual-action `docs install-skill --force` half are **CUT** (re-scope
  2026-06-29); the skill story moves to the follow-on **M23**. Ships as **1.7.0
  locally** (minor bump — additive feature; 1.6.5 was the operator-decreed
  patch exception); the PyPI publish is a later operator-driven milestone
  (M19→M20, M14+M15→M17 pattern). Depends on nothing. **No TDD phase started** —
  milestone-setup only. OPEN QUESTIONS are netted out — **none outstanding**
  (the re-scope resolves or moots OQ-1..OQ-9; OQ-6's "ship D5" is REVERSED). See
  the milestone doc's Decisions.

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

Operator-directed M21 scope (2026-06-12), **re-scoped to CLI-only 2026-06-29**
(see the dated re-scope log below). The headline: docs-cli checks PyPI for a
newer version and notifies that the user/agent should `pip install -U
docs-cli`. The motivating miss is on this very host — the M20 publish-closeout
host-skill sweep (2026-06-12) caught a stale `docs new --body-from` "first 20
lines" reference in the `project-foundation` workflow skill, the pre-M19-D3
heuristic; the drift was only catchable at publish time, by hand. That
skill-drift class of miss is now addressed by the **M23** follow-on
(install-where-you-use-it + recorded-path refresh), **not** by runtime
inspection in M21. M21 makes the **CLI** update signal self-announcing at every
invocation.

Design + precedent were researched and operator-reviewed and are recorded in
the milestone doc's Decisions: gh CLI's 24h persisted-timestamp notifier
(cli/cli#85, #743 — TTY-gated, `GH_NO_UPDATE_NOTIFIER`, CI skip), npm
`update-notifier` (1-day default, deferred notify-next-run, `NO_UPDATE_NOTIFIER`,
auto-skip CI/test), Terraform Checkpoint (`CHECKPOINT_DISABLE`), pip's always-on
notice as the anti-pattern (CI noise, stream regressions), and aider as the
agent-CLI precedent (default-on launch check, exit-code machine mode, disable
toggle). M21's deliberate departure is the **TTY inversion** — show on non-TTY
too, because the agent is the actor.

Code anchors (verified against the current tree; M22 was docs-only so the
`cli.py` line anchors still hold):

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
- No existing network/cache surface anywhere (`grep urllib|http|socket|.cache|
  XDG_CACHE src/` → zero hits) — M21 is the first.
- `tests/test_packaging.py` A3 + B1/B2/C2 + `pyproject.toml` `version` — the
  version-pin + bump to `1.7.0` (D7), the A3-fast / B1-B2-C2-slow split (M19
  precedent). The B3 wheel-contents test (~line 215) makes only
  positive-presence assertions and ships the whole `src/docs_cli` package, so
  the dedicated `update_check.py` module (OQ-7) needs no packaging change.
- Lockstep: `tests/test_skill_refs.py` (bundled `references/{cli,convention}.md`
  byte-identical to `docs/`), `tests/fixtures/expected/docs-INDEX.md` (frozen
  INDEX snapshot kept identical to `docs/INDEX.md`).

See [m21-update-check.md](m21-update-check.md) Decisions for the full contract
analysis and the OQ resolutions; the OPEN QUESTIONS analysis is retained there
as historical record. The follow-on **M23** (agent-aware install-skill +
recorded-dest skill-refresh hint) restores the skill-refresh nudge that was cut
from M21 — see [m23-agent-aware-install-skill.md](m23-agent-aware-install-skill.md).

## Re-scope log — CLI-only (2026-06-29)

A planning agent and the operator pressure-tested M21's D5 ("offline
skill-drift notice") and the dual-action nudge, and found they contradict two
core principles: docs-cli must **not inspect or manage the user's installed
skills**, and must **not assume Claude Code**. Findings and the resulting
binding decisions:

- **docs-cli ships exactly ONE skill** (the Claude-Code `SKILL.md` shape) —
  there is no per-agent skill format, so "which agent" is the wrong axis;
  "which directory" (`install-skill --dest`) is the honest one, and already
  exists. D5's premise was **content-inspection** of the installed skill → cut.
- **The notice becomes CLI-only.** The original notice named both
  `pip install -U docs-cli` AND `docs install-skill --force`; the second half
  assumes Claude Code and assumes the user even has the skill installed →
  dropped. New reference wording (DECISION 2):
  `docs: update available <current> -> <latest> — run: pip install -U docs-cli`.
- **Cache schema loses the drift key (DECISION 3):**
  `{last_check, latest_version, last_notified}` — `last_skill_drift_notified`
  dropped.
- **D5 is CUT** (not deferred-as-D5); **OQ-6's "ship D5" resolution is
  REVERSED.** Everything else M21 specced stays: the first-network-surface
  (stdlib `urllib`, 1.0s timeout, fail-silent always), the per-user JSON cache,
  the two 24h throttles, the suppression matrix, the deliberate TTY inversion,
  the offline test harness, and the 1.7.0 version/docs plumbing.
- **The skill half moves to the new follow-on M23.** Making `install-skill`
  agent-aware (via `--dest`), recording the resolved dest, and then extending
  M21's notice channel with a skill-refresh hint pointed at the *recorded*
  dest. Replay/remember is allowed; content-inspection is NOT. See
  [m23-agent-aware-install-skill.md](m23-agent-aware-install-skill.md).
- **Surviving resolved findings folded in:** the dedicated
  `src/docs_cli/update_check.py` module stands (OQ-7; the B3 wheel-contents test
  tolerates it); the suite offline guard sets `DOCS_CLI_NO_UPDATE_CHECK=1` in
  `tests/conftest.py`; the not-yet-existing-module import guard
  (`try/except ModuleNotFoundError → uc = None`) covers the Phase-2/4 RED
  baseline; cache timestamps are ISO-8601 UTC; the baseline test count is
  **543** (not the stale 540). The earlier dual-notice ordering question is
  moot (single notice now).

Net effect: M21 is the runtime **CLI-update** notice only; no skill inspection,
no Claude-Code assumption. No TDD phase has run; the re-scope is a docs-only
change to the milestone pair (no product code touched).

## Phase 1 — Define Contract

_Not started._
