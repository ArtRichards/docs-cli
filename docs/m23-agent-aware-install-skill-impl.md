# M23 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-06-29

Related:
- child-of: m23-agent-aware-install-skill.md
- pairs-with: m23-agent-aware-install-skill.md
- pairs-with: status.md
- references: m21-update-check.md

## Overview

Chronological log of work on M23 — Agent-aware install-skill + recorded-dest
skill-refresh hint. Append a section per TDD phase with objective, files
changed, actions, test results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M23 — Agent-aware install-skill + recorded-dest skill-refresh hint
  (v1.8.0 recommended)
- Started: 2026-06-29 (scaffolded — milestone-setup; no TDD phase started)
- Progress: **Milestone pair scaffolded 2026-06-29** as the follow-on to the
  M21 re-scope. M21 became a CLI-only update notice and CUT its skill half (the
  offline skill-drift notice D5 + the dual `docs install-skill --force` nudge)
  because it inspected the user's installed skill and assumed Claude Code. M23
  rebuilds the skill-refresh story honestly: make `install-skill` agent-aware
  (`--dest` is the agent-agnostic source of truth; TTY-aware resolution that
  never blocks an agent), **record** the resolved dest to a per-user state file
  (a *path*, never the skill's content), neutralise the "Claude Code skill"
  framing in `install-skill`'s help → "agent skill", and extend M21's
  update-notice channel with a skill-refresh hint pointed at the **recorded**
  dest. **Depends on M21.** No TDD phase started. Four genuine OPEN QUESTIONS
  remain for a later planning pass (non-TTY default-vs-refuse; state-file
  location; multiple recorded dests; final version number — recommend 1.8.0).

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

M23 was scoped this session (2026-06-29) directly out of the M21 re-scope. The
binding context:

- M21 dropped its skill half because the design **content-inspected** the user's
  installed skill (compared it byte-wise against the bundled skill) and
  **assumed Claude Code** (a single hardcoded dest `~/.claude/skills/docs/`).
  docs-cli ships exactly ONE skill artifact — there is no per-agent skill
  *format* to detect — so the only honest axis is **which directory** the user
  installs into, i.e. `install-skill --dest`.
- The honest rebuild: record where the agent installs the skill, then **replay**
  that path in a refresh hint on M21's notice channel. Replay/remember is
  allowed; content-inspection is NOT.

Code anchors (verified against the current tree, 2026-06-29):

- `install-skill` parser `cli.py:3311-3357`; help/description `cli.py:3313-3325`
  currently frame it as "the bundled `docs` **Claude Code** skill" / "an agent
  driving **Claude Code**" — the D4 problem. `cli.md`'s install-skill synopsis
  already says "agent skill", so D4 reconciles the help to the spec.
- `--dest` default `~/.claude/skills/docs/` (`cli.py:3328-3330`).
- `_cmd_install_skill` `cli.py:5114`; dest resolved `cli.py:5124`
  (`Path(os.path.expanduser(args.dest)).resolve()`).
- Skill-tree helpers reused for the install (not for content compare):
  `_SKILL_RELATIVE_FILES` `cli.py:5055`, `_locate_bundled_skill()` `cli.py:5070`,
  `_trees_byte_identical()` `cli.py:5097`.
- M21 surface this extends: `src/docs_cli/update_check.py` (the notice module)
  + the `main()` hook (`cli.py:5194`) + the per-user cache
  `${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json`. `__version__`
  (`cli.py:44`) is the `importlib.metadata` SoT (M12).

See [m23-agent-aware-install-skill.md](m23-agent-aware-install-skill.md)
Decisions + OPEN QUESTIONS for the full contract, and
[m21-update-check.md](m21-update-check.md) Decisions › "Re-scope to CLI-only"
for the provenance.

## Phase 1 — Define Contract

_Not started._
