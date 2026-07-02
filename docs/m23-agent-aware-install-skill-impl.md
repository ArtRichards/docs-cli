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
| 3. Create Data/Fixtures | Complete | 2026-07-02 | inline tmp builders (state seed + TTY harness); date-independent; no real-path/network; frozen INDEX snapshot the only committed fixture |
| 4. Run Tests (RED Baseline) | Complete | 2026-07-02 | 634 total: 613 pass / 21 intended-RED; pre-existing suite green (only the 4 flipped packaging pins went RED) |
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
- `docs/cli.md` `Updated:` bumped to 2026-07-02 per the convention (an edited
  doc bumps its own `Updated:` — status.md "How to keep this file honest");
  `references/cli.md` re-synced byte-identical; `docs/INDEX.md` +
  `tests/fixtures/expected/docs-INDEX.md` regenerated in lockstep. (The
  date-bump was applied during the post-Phase-4 audit — the initial Phase-1
  commit had left cli.md's date unchanged to keep the INDEX row a no-op, which
  the audit corrected.)

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

## Phase 3 — Create Data/Fixtures

**Objective.** Ensure date-independent, hermetic test data with no rotting
fixture and no real-path / network access.

**Actions.** All builders are inline in the two test files (landed in Phase 2);
no new committed fixture:

- `tests/test_install_skill_dest.py`: `_prep_state` (XDG_STATE → tmp),
  `_prep_home` (HOME → tmp so the `~/.claude/skills/docs/` default is contained
  in tmp), `_read_state_raw` / `_state_file`, and a TTY harness
  (`monkeypatch.setattr("sys.stdin.isatty", ...)` + `builtins.input`).
- `tests/test_update_check.py`: `_prep_state` / `_write_recorded_dest`
  (present/absent/stale-path variants) / `_expected_hint`, layered on M21's
  reused `_prep_dispatch` / `_FetchSpy` / `_expected_notice` / `_iso_hours_ago`.

**Hermeticity.** Every test that could touch per-user state points XDG_STATE
(and HOME where `--dest` is omitted) at `tmp_path`; install runs read only the
in-repo bundled skill and the M21 fetch is fake-injected — no real `~/.cache`,
`~/.local/state`, or network. Timestamps are all relative to
`datetime.now(UTC)`. The frozen `tests/fixtures/expected/docs-INDEX.md`
snapshot stays the only committed fixture (regenerated in lockstep in Phase 1).

**Result.** Date-independent test data; no rotting fixture; no real-path or
network access.

## Phase 4 — Run Tests (RED Baseline)

**Objective.** Confirm the intended-RED set fails for its reason and the
pre-existing suite stays GREEN; capture the exact baseline count.

**Command.** `.venv/bin/python -m pytest tests/ -q`

**Baseline count.** **634 tests: 613 passed, 21 failed** (all intended-RED).
(The pre-M23 suite was 604; M23 added 30 tests — 17 in
`test_install_skill_dest.py`, 13 D5/seam/spec-lock additions to
`test_update_check.py` — of which 13 are GREEN-at-baseline locks.)

**Intended-RED set (21), each failing for its stated reason:**

- `test_install_skill_dest.py` (13):
  - `test_d2_tty_prompt_installs_at_prompted_dest` — no TTY-aware resolver yet;
    the static `--dest` default is used, so the prompted dest is not honoured.
  - `test_d3_copy_success_records_dest_path_only`, `test_d3_noop_also_records`
    — `read_recorded_dest` absent (no recording yet).
  - `test_d4_install_skill_description_says_agent_skill_not_claude_code`,
    `test_d4_install_skill_short_help_says_agent_skill_not_claude_code` — help
    still says "Claude Code".
  - `test_state_helpers_exist`, `test_state_path_honours_xdg_state_home`,
    `test_state_path_defaults_to_local_state_when_xdg_unset`,
    `test_recorded_dest_roundtrips`, `test_recorded_dest_last_write_wins`,
    `test_read_recorded_dest_missing_returns_none`,
    `test_read_recorded_dest_corrupt_returns_none`,
    `test_write_recorded_dest_unwritable_swallows_oserror` — state-file helpers
    not yet implemented (clean `hasattr`-guarded assertion failures).
- `test_update_check.py` (4):
  - `test_skill_hint_template_and_formatter_seam`,
    `test_format_skill_hint_is_byte_exact_without_trailing_newline` —
    `SKILL_HINT_TEMPLATE` / `format_skill_hint` absent.
  - `test_dispatch_recorded_dest_appends_skill_hint`,
    `test_dispatch_recorded_dest_replayed_verbatim` — no hint appended to the
    M21 notice yet.
- `test_packaging.py` (4): `test_a3_project_version_is_1_8_0`,
  `test_b1_wheel_builds`, `test_b2_sdist_builds`, `test_c2_docs_version_is_1_8_0`
  — pyproject is still 1.7.0 (RED until Phase 7).

**GREEN-at-baseline locks that PASS** (proving the contract is honoured before
the change and M21 is unchanged): D1 explicit-dest / D2 empty-input + non-TTY /
D3 refusal-records-nothing; the AF-1 spec-content lock; hint-absent →
CLI-line-only; the full suppression matrix + throttle-coupling + current-version
hint-silence; `test_skill_refs` byte-identity; the frozen INDEX snapshot.

**Gate note.** `ruff check .` + `ruff format --check .` clean tree-wide;
`mypy` reports "Success: no issues found in 44 source files" (the new test file
types `uc` as `Any`, so referencing the not-yet-existing seams is mypy-clean).
The behaviour gate (the 21 RED) goes GREEN in Phases 6–8.

**Result.** RED baseline matches the plan exactly; no collection errors; the
untouched pre-existing suite is fully GREEN (only the 4 deliberately-flipped
packaging pins moved to RED).

## Post-Phase-4 audit (consistency / completeness / accuracy)

Ran the same-instance audit (ship-milestone `consistency-check.md`). The RED
baseline was re-verified as intact (634: 613 pass / 21 intended-RED). Three
issues found and fixed:

1. **cli.md `Updated:` not bumped.** Phase 1 kept `docs/cli.md` at 2026-06-29
   (to keep the INDEX row a no-op), but the project convention is that an
   edited doc bumps its own `Updated:`. Fixed: bumped to 2026-07-02, re-synced
   `references/cli.md`, regenerated INDEX + frozen snapshot in lockstep. (This
   deviates from the plan's "cli.md is a mid-file INDEX no-op" expectation, in
   favour of the documented convention.)
2. **status.md M23 row stale.** It claimed "No TDD phase started" and "Four
   genuine OPEN QUESTIONS open" — both now false. Fixed: the M23 table row +
   prose now report Phases 1–4 complete on `m23/phases-1-4` (634: 613/21) and
   the four OQs resolved (OQ-1/OQ-2 provisional pending operator confirm);
   status.md `Updated:` bumped; INDEX + snapshot regenerated in lockstep.
3. **Dispatch-test hermeticity.** The reused `_prep_dispatch` did not isolate
   `XDG_STATE_HOME`, so once the Phase-6 hint reads the recorded dest the M21
   dispatch tests could pick up the host's real `~/.local/state`. Fixed:
   `_prep_dispatch` now points `XDG_STATE_HOME` at a fresh tmp dir, keeping the
   M21 `endswith(_expected_notice)` locks robust (plan Phase 3 "every test
   points XDG_STATE at tmp").

**Test-adequacy (the phases-1–4 highest-leverage check).** The RED tests pin
the contract, not trivial passes: the state-file location is pinned to the
exact `XDG_STATE` path + `~/.local/state` default; recording asserts the exact
`{"dest": <resolved>}` shape with **no** hash/content key; the hint is pinned
byte-exact as the LAST stderr line (order + count + not-on-stdout), with
verbatim replay of a non-existent path, full suppression-matrix + throttle
coupling, and current-version silence; D4 pins both the description and the
one-line help. GREEN-at-baseline locks (D1, D2 empty/non-TTY, D3 refusal,
hint-absent M21-unchanged, AF-1 spec lock) guard the pre-change contract.

Surfaced for operator decision at branch review: OQ-1 (non-TTY = default) and
OQ-2 (separate `XDG_STATE` file) were resolved **provisionally while the
operator was away** and are flagged in the milestone doc Decisions + status.md
for confirmation.
