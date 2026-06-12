# M19 — Implementation Log

Lifecycle: draft
Role: log
Project: docs
Updated: 2026-06-12

Related:
- child-of: m19-post-edit-validation.md
- pairs-with: m19-post-edit-validation.md
- pairs-with: status.md

## Overview

Chronological log of work on M19 — Post-edit validation ergonomics
(`docs touch --check` + configurable stale window). Append a section per TDD
phase with objective, files changed, actions, test results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M19 — Post-edit validation ergonomics (touch --check +
  configurable stale window)
- Started: 2026-06-12 (scaffolded)
- Progress: **Milestone pair scaffolded 2026-06-12** from the status.md
  "Single-step 'update metadata + validate' loop + configurable stale window"
  follow-on (operator feedback 2026-06-12, retargeted from v1.7 to **v1.6.5**
  by operator decision). Three deliverables: (D1) `docs touch --check
  [--stale N]` folds the existing `check_tree` machinery into `docs touch`
  after its end-of-batch reindex, collapsing the three-command post-edit loop
  (`touch` → `index` → `check --stale 14`) to one invocation; (D2) a
  `.docs.toml [check] stale_days = N` per-tree default the stale window reads
  from when no CLI `--stale` is given (CLI `--stale` overrides; absent config
  preserves today's behaviour); (D3) the cosmetic `docs new --body-from`
  argparse help-string fix closing the rolled-forward follow-on. No new verb,
  no new check rule — additive flag + config key + help string. Ships as
  **1.6.5 locally**; the PyPI publish is a later operator-driven milestone
  (M12→M13, M14+M15→M17 pattern). Depends on nothing; M18 is the only other
  live milestone and is independent. **Implementation not yet started** —
  Phase 1 (Define Contract) is next. OPEN QUESTIONS Q1–Q6 are RESOLVED
  (operator decisions 2026-06-12, each per the recommended default —
  see the milestone doc's Decisions › "Resolved questions (Q1-Q6, BINDING)");
  a post-draft operator addition (2026-06-12) folds **threshold provenance**
  into D2 — the stale finding's message must name where the threshold is set
  (`set in .docs.toml [check] stale_days` for config-sourced, `via --stale`
  for CLI-sourced).

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

The scope is the status.md "Open follow-ons (rolled forward)" entry
**"Single-step 'update metadata + validate' loop + configurable stale window
(v1.7 candidates)"** — operator feedback 2026-06-12, since retargeted from
v1.7 to **v1.6.5**. Two parts plus a cosmetic fold-in:

- **(a) Single-step touch+validate.** The common post-edit workflow runs as
  three commands — `docs touch <files>`, `docs index .`,
  `docs check . --stale 14` — and should be one step. `docs touch` already
  runs the end-of-batch INDEX refresh (M10 — OQ-C, `_cmd_touch`
  `cli.py:3951` calls `_refresh_index`), so the explicit `docs index .` is
  already redundant — but nothing on the surface says so, and the real gap is
  that validation is not bundled. Candidate shape: `docs touch --check
  [--stale N]`, running the existing `check_tree` (`cli.py:1641`) after the
  reindex. → **D1.**
- **(b) Configurable stale window.** A fixed `--stale 14` is too short for
  multi-week projects — an active doc can be legitimately untouched for weeks
  while its milestone is in flight, so a hard-coded 14 mis-flags healthy
  trees. Candidate shape: a `.docs.toml [check] stale_days = N` per-tree
  default (explicit CLI `--stale` overrides), so the window is tuned per
  project instead of hard-coded in agent workflows/skills. → **D2.** A
  post-draft operator addition (2026-06-12) extends D2's contract: the
  stale finding's message must name the threshold's **provenance** so the
  operator knows which knob to turn — config-sourced thresholds append
  `set in .docs.toml [check] stale_days`, CLI-sourced thresholds append
  `via --stale`.
- **(c) Cosmetic fold-in (auto-resolved by the conductor per triage —
  stale spec text).** The one-line `docs new --body-from` argparse
  help-string fix (`src/docs_cli/cli.py:2900-2905`, still describing the
  pre-M15-C4 "first 20 lines" heuristic; correct wording is in the
  [m17-pypi-publish-impl.md](m17-pypi-publish-impl.md) Open follow-on note).
  → **D3**; closes that follow-on.

Code anchors (verified against the current tree at scaffold time, 2026-06-12):

- `_cmd_touch` (`cli.py:3880`) — the touch command; its end-of-batch
  `_refresh_index(...)` call is at `cli.py:3951`; the `--check` flag + the
  post-reindex `check_tree` call land here (D1).
- `check_tree` (`cli.py:1641`) — already takes `stale: int | None`; reused
  unchanged by both D1 and the D2 resolution.
- `_cmd_check` (`cli.py:4533`) + its `check_tree(..., args.stale, ...)` call
  (`cli.py:4552`); `_cmd_list` (`cli.py:4572`) + its `query_docs(..., stale=
  args.stale, ...)` call (`cli.py:4592`) — the two existing `--stale`
  consumers the D2 config default threads into.
- `Config` (`cli.py:209`) + `load_config` (`cli.py:943`, the `[check]`
  section read lands beside the existing `[project]`/`[archive]`/
  `[vocabulary]`/`[migrate]`/`[exclude]` reads) — `Config.stale_days`
  field + parse (D2).
- `--body-from` argparse help (`cli.py:2897-2906`) — the D3 one-line fix
  target; the runtime detector `_body_has_metadata_block` (`cli.py:3371`)
  and the refusal message (`cli.py:3504`) are already correct.
- `tests/test_packaging.py:100` (`test_a3_project_version_is_1_6_0`) +
  `pyproject.toml:7` (`version = "1.6.0"`) — the version-pin + version
  bump to `1.6.5` (D4).
- Lockstep: `tests/test_skill_refs.py` (bundled `references/{cli,convention}.md`
  byte-identical to `docs/`), `tests/fixtures/expected/docs-INDEX.md`
  (frozen INDEX snapshot kept identical to `docs/INDEX.md`).

See [m19-post-edit-validation.md](m19-post-edit-validation.md) Decisions +
OPEN QUESTIONS for the full contract analysis and the Q1–Q6 forks with
recommended defaults.
