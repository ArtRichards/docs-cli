# M23 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-07-02

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
  (v1.8.0)
- Started: 2026-06-29 (scaffolded — milestone-setup); TDD Phase 1 opened
  2026-07-02.
- Progress: **Phase 1–4 in progress (Contract & RED baseline, 2026-07-02).**
  Scaffolded 2026-06-29 as the follow-on to the M21 re-scope (M21 became a
  CLI-only update notice and CUT its skill half — the offline skill-drift notice
  D5 + the dual `docs install-skill --force` nudge — because it inspected the
  user's installed skill and assumed Claude Code). M23 rebuilds the
  skill-refresh story honestly: make `install-skill` agent-aware (`--dest` is
  the agent-agnostic source of truth; TTY-aware resolution that never blocks an
  agent), **record** the resolved dest to a per-user state file (a *path*, never
  the skill's content), neutralise the "Claude Code skill" framing in
  `install-skill`'s help → "agent skill", and extend M21's update-notice channel
  with a skill-refresh hint pointed at the **recorded** dest. **Depends on M21.**
  The four OPEN QUESTIONS are **resolved** (OQ-1 default / OQ-2 separate
  XDG_STATE file — provisional pending operator confirm; OQ-3 single dest;
  OQ-4 1.8.0); see the milestone doc Decisions.

(Note: doc-lifecycle status is the front-matter `Lifecycle:` field. This
section tracks implementation progress, which is distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-07-02 | cli.md §install-skill + §Update check; refs resynced; OQs folded into Decisions |
| 2. Write Tests (RED) | Complete | 2026-07-02 | new test_install_skill_dest.py; D5 additions to test_update_check.py; packaging pins flipped to 1.8.0 |
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

**Objective.** Freeze the four contract surfaces in the specs (no code, no
tests): the TTY-aware `--dest` resolution, the recorded-dest state file, the
reworded "agent skill" help, and the M21-notice skill-refresh hint.

**Files changed.**

- `docs/cli.md` §install-skill — added two paragraphs: *Destination resolution*
  (`--dest` is the single agent-agnostic SoT; omitted → TTY may prompt with the
  default offered / empty accepts default, non-TTY silently uses the default
  `~/.claude/skills/docs/` and exits 0) and *Recorded destination* (any success
  — copy, symlink, or already-identical no-op — records the resolved **path**
  to `${XDG_STATE_HOME:-~/.local/state}/docs-cli/install-skill.json`, schema
  `{"dest": "<absolute-path>"}`, last-write-wins, fail-silent; a refusal records
  nothing; path replayed verbatim, never inspected). Cross-reference to
  §Update check.
- `docs/cli.md` §Update check — added the **Skill-refresh hint** subsection
  pinning the byte-exact template
  `docs: refresh the agent skill at <dest> — run: docs install-skill --dest <dest> --force`,
  its coupling to the CLI notice (same suppression matrix + 24h `last_notified`
  throttle, no independent trigger), verbatim replay (no fs check), and the
  M21-unchanged "no recorded dest → CLI line only" behaviour.
- `src/docs_cli/skill/references/cli.md` — resynced byte-identical (surface
  parity; `tests/test_skill_refs.py` green).
- `docs/m23-agent-aware-install-skill.md` — folded the four OPEN QUESTIONS into
  Decisions as resolved (OQ-1 default / OQ-2 separate XDG_STATE file — both
  provisional pending operator confirm; OQ-3 single dest; OQ-4 1.8.0) plus
  AF-1/AF-2/AF-3; updated Overview, Requirements D2/D3, Deliverables D2/D3/D7.
- `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` — regenerated in
  lockstep (the milestone-doc description + m23 doc dates changed). The `cli.md`
  edits are mid-file and did **not** bump its `Updated:` date, so its INDEX row
  is a byte no-op.

**Decisions bound.** OQ-1..OQ-4 + AF-1..AF-3 (see the milestone doc). The
`convention.md` mirror is intentionally NOT touched — per-user runtime state is
a `cli.md` runtime detail (like M21's cache), not the docs-tree format.

**Result.** `docs check docs/` exit 0; `tests/test_skill_refs.py` green;
`docs index --root docs/ --dry-run` clean.

## Phase 2 — Write Tests (RED)

**Objective.** Failing tests for D1–D5 + the state-file / hint seams; all
offline (M21 notice fake-injected, XDG_STATE + HOME pointed at tmp).

**Files changed.**

- `tests/test_install_skill_dest.py` (**new**) — drives
  `cli.main(["install-skill", ...])` in-process:
  - **D1** explicit `--dest` installs and never prompts (`builtins.input`
    raises) — GREEN at baseline (a lock).
  - **D2** TTY prompt → prompted dest used (RED); TTY empty input → default
    (GREEN lock); non-TTY never blocks → default, exit 0 (GREEN lock, OQ-1).
  - **D3** copy-success records `{"dest": <resolved>}` path-only (RED); an
    already-identical no-op also records (RED); a refusal records nothing
    (GREEN lock).
  - **D4** subparser description + one-line help say "agent skill", never
    "Claude Code" (RED).
  - State-file helpers `state_path` / `read_recorded_dest` /
    `write_recorded_dest`: existence, XDG_STATE path + `~/.local/state`
    default, roundtrip, last-write-wins, missing/corrupt → None, unwritable →
    silent (all RED via `hasattr` guards giving clean assertion failures).
- `tests/test_update_check.py` (**additions**) — D5 recorded-dest hint on
  M21's channel, reusing `_prep_dispatch` / `_FetchSpy` / `_expected_notice`
  and adding `_prep_state` / `_write_recorded_dest` / `_expected_hint`:
  - hint present as the byte-exact LAST stderr line, exactly once, never on
    stdout (RED); verbatim replay of a non-existent path (RED); no-dest →
    CLI line only, M21 unchanged (GREEN lock); `--json` / `--quiet` / CI /
    `DOCS_CLI_NO_UPDATE_CHECK` / `DO_NOT_TRACK` silence both lines (GREEN
    locks); fresh `last_notified` throttles the hint too (GREEN lock);
    current version → no hint (GREEN lock).
  - `SKILL_HINT_TEMPLATE` / `format_skill_hint` seam + byte-exact formatter
    (RED); the AF-1 spec-content lock on `docs/cli.md` (GREEN).
- `tests/test_packaging.py` — A3 / B1 / B2 / C2 version pins flipped
  1.7.0 → 1.8.0 (RED until Phase 7; function names + docstrings updated).

**INVARIANT preserved.** The M21 dispatch tests run list/check/touch — never
install-skill — so they never record a dest; their
`endswith(_expected_notice)` locks stay GREEN.

**Result.** New tests collect cleanly (no import/argparse-SystemExit
surprises); ruff check + format clean on all three files; each intended-RED
fails for its stated reason (see Phase 4).
