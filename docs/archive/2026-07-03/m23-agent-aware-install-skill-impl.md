# M23 — Implementation Log

Lifecycle: archived
Role: log
Project: docs
Updated: 2026-07-03
Archived-reason: Milestone M23 complete; shipped to PyPI as docs-cli==1.8.0 (batched via M24) 2026-07-03

Related:
- child-of: archive/2026-07-03/m23-agent-aware-install-skill.md
- pairs-with: archive/2026-07-03/m23-agent-aware-install-skill.md
- pairs-with: status.md
- references: archive/2026-07-03/m21-update-check.md

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
- Progress: **Implementation complete — all ten TDD phases done (2026-07-02);
  1.8.0 built locally (publish is a later milestone); lifecycle `draft`.**
  Phases 1–4 on `m23/phases-1-4`; Phases 5–10 on `m23/phases-5-10`. Full suite
  **636 GREEN**, gate clean tree-wide, `docs --version` = `docs 1.8.0`; online
  path dogfooded against a seeded throwaway cache (pytest 100% offline).
  OQ-1/OQ-2 remain flagged for confirmation at branch review.
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
| 4. Run Tests (RED Baseline) | Complete | 2026-07-02 | 636 total: 613 pass / 23 intended-RED (after the fresh-eyes fold added 2 nit RED tests); pre-existing suite green (only the 4 flipped packaging pins went RED) |
| 5. Update Base Interfaces | Complete | 2026-07-02 | update_check seams (SKILL_HINT_TEMPLATE/format_skill_hint + state_path/read/write_recorded_dest); cli.py _DEFAULT_SKILL_DEST + _resolve_install_dest; --dest default → None. Seam tests GREEN; behaviour RED |
| 6. Implement Offline/Core Path | Complete | 2026-07-02 | extract-method _materialise_skill + single recording call site (OQ-A); D4 help reword; D5 hint in _check_and_notify. 17 behaviour RED → GREEN; 4 packaging pins still RED |
| 7. Update Tool/Wrapper Layer | Complete | 2026-07-02 | pyproject 1.8.0 + editable reinstall; NEWER sentinel hoisted + dispatch-block "newer" literals rebased (OQ-D); CHANGELOG 1.8.0; packaging pins GREEN; test_skill_refs GREEN |
| 8. Run Tests (GREEN) | Complete | 2026-07-02 | Full suite 636 GREEN; ruff/format/mypy clean; docs check exit 0; docs index --dry-run byte no-op; docs --version = 1.8.0 |
| 9. Implement Online/Integration | Complete | 2026-07-02 | Dogfooded on the editable install (seeded throwaway cache; no real network): copy/no-op/symlink all record; newer-PyPI notice fires CLI line + hint (byte-exact, hint LAST); non-TTY piped install never blocks + records resolved default; --json/--quiet/CI/DOCS_CLI_NO_UPDATE_CHECK/DO_NOT_TRACK silence both. Suite stays offline |
| 10. Quality, Docs, Refactor | Complete | 2026-07-02 | OQ-B stale-wording sweep (4 stray "Claude Code" strings reworded; install-skill surface grep clean); status.md + plan.md M23 rows + milestone-doc checklist/criteria/deliverables ticked; INDEX + frozen snapshot in lockstep; surface-parity gate re-verified (test_skill_refs GREEN); lifecycle left `draft`; no /simplify (conductor's Step 3) |

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

**Baseline count.** **636 tests: 613 passed, 23 failed** (all intended-RED)
— the post-Phase-4 fresh-eyes fold (below) added 2 nit RED tests, moving the
original 634/21 baseline to 636/23. (The pre-M23 suite was 604; M23 added 32
tests — 19 in `test_install_skill_dest.py`, 13 D5/seam/spec-lock additions to
`test_update_check.py` — of which 13 are GREEN-at-baseline locks.)

**Intended-RED set (23), each failing for its stated reason:**

- `test_install_skill_dest.py` (15):
  - `test_d2_tty_prompt_installs_at_prompted_dest` — no TTY-aware resolver yet;
    the static `--dest` default is used, so the prompted dest is not honoured.
  - `test_d3_copy_success_records_dest_path_only`, `test_d3_noop_also_records`,
    `test_d3_omitted_dest_records_resolved_default_path` (fresh-eyes nit — pins
    that an OMITTED `--dest` records the *resolved* default path, not None /
    unexpanded `~`), `test_d3_symlink_success_records_dest` (fresh-eyes nit —
    pins symlink-success recording, the third `cli.md` success trigger)
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

## Post-Phase-4 fresh-eyes review fold (2026-07-02)

A fresh-eyes review of the phases-1–4 RED baseline returned four findings — all
test-strengthening / latent-trap fixes, **no** scope or behaviour-intent change.
Folded on `m23/phases-1-4`; the suite stays at the intended RED baseline (now
**636: 613 pass / 23 intended-RED** — the two nit tests below are the +2 RED).

1. **SHOULD-FIX — version-literal hazard (D5 hint tests).** The new D5 hint
   tests hardcoded `_FetchSpy(version="1.7.1")` as the "newer" PyPI version.
   `is_newer("1.8.0", "1.7.1")` is False, so once Phase 7 bumps `CURRENT` to
   1.8.0 the CLI notice — and thus the hint — stops firing: the present-hint
   tests would fail at Phase 8 GREEN and the absence-asserting ones would pass
   for the wrong reason. Fixed: introduced a bump-proof `NEWER = "99.0.0"`
   sentinel in the M23 section and rebased **all** M23 D5 `1.7.1` literals onto
   it (both present- and absence-asserting tests). The pre-existing M21 dispatch
   block (~513–747) still uses `1.7.1` (GREEN at the current 1.7.0, out of this
   step's scope) — a **Phase 7 sweep note** was added to the milestone doc
   Phase 7 objective + the Phase 7 row/notes here so Step 2 rebases those.
2. **SHOULD-FIX — hermeticity leak (Group-D packaging tests).** The Group-D
   `tests/test_packaging.py` tests run `docs install-skill --dest <tmp>` as
   subprocesses without isolating `XDG_STATE_HOME`; once Phase 6 adds recording
   each would silently write `install-skill.json` to the host's real
   `~/.local/state/docs-cli/`. Fixed: added a `_isolated_env(tmp_path)` helper
   (ambient env + `XDG_STATE_HOME` → tmp) and passed `env=` into every Group-D
   install subprocess (D2–D6). Harmless before recording exists; the packaging
   tests still behave (the 4 flipped version pins stay RED; the rest unchanged).
3. **NIT — omitted-`--dest` recording unpinned.** Every D3 recording test used
   an explicit `--dest`. Added `test_d3_omitted_dest_records_resolved_default_path`
   — a default-resolved install (no `--dest`, non-TTY) must record the
   **resolved** default path (not None / unexpanded `~`). NEW intended-RED (no
   recording until Phase 6); hermetic (XDG_STATE + HOME at tmp).
4. **NIT — symlink-success recording unpinned.** `cli.md`'s *Recorded
   destination* prose lists a symlink among the success triggers, but no test
   exercised it (only copy + no-op + refusal). Added
   `test_d3_symlink_success_records_dest` — the editable-install `--symlink`
   path records the resolved dest (expected value captured **before** the
   symlink exists, so `resolve()` does not chase the link to the source). NEW
   intended-RED until Phase 6; hermetic.

**Gate after the fold.** `ruff check` + `ruff format --check` clean tree-wide;
`mypy` "Success: no issues found in 44 source files"; `docs check docs/` exit 0;
`docs index --root docs/ --dry-run` a byte no-op vs the committed INDEX. RED
baseline re-verified: **636: 613 pass / 23 intended-RED**, every RED failing for
its stated reason; the pre-existing suite stays GREEN (only the 4 flipped
packaging pins are RED). No constraint relaxed; no Phase-5+ behaviour landed.

## Phase 5 — Update Base Interfaces

**Objective.** Declare the M23 seams with minimal logic, mirroring M21's
fail-silent idioms; tests import the seam; behaviour tests stay RED.

**Files changed.**

- `src/docs_cli/update_check.py` — added `SKILL_HINT_TEMPLATE` (byte-exact
  AF-1 template, em-dash U+2014 before `run:`, `{dest}` placeholder) beside
  `NOTICE_TEMPLATE`; `format_skill_hint(dest)` beside `format_notice`; and the
  path-only per-user state trio beside the cache helpers — `state_path()`
  (`${XDG_STATE_HOME:-~/.local/state}/docs-cli/install-skill.json`),
  `read_recorded_dest()` (fail-silent on OSError/ValueError; dict + str `dest`
  guard else `None`), `write_recorded_dest(dest)` (mkdir parents; write
  `{"dest": dest}`; swallow OSError). M21's frozen 3-key `Cache` is untouched
  (OQ-2).
- `src/docs_cli/cli.py` — module const `_DEFAULT_SKILL_DEST =
  "~/.claude/skills/docs/"`; `_resolve_install_dest(args)` (returns the RAW
  string — explicit `--dest` verbatim; omitted + TTY → prompt, empty accepts
  default; omitted + non-TTY → default, never blocks; OQ-1/OQ-C); `--dest`
  argparse `default` flipped `"~/.claude/skills/docs/"` → `None` (the help=
  literal "(default: ~/.claude/skills/docs/)" kept — packaging D7 + the human
  default depend on it). The section comment above `_cmd_install_skill` was
  reworded "Claude Code skill" → "agent skill" here (an OQ-B target folded early
  — a zero-risk comment adjacent to the section being made agent-aware).

**Result.** `mypy` clean (44 files); ruff/format clean; the seam +
state-helper + formatter tests GREEN; the D2/D3/D4 behaviour tests and the 2
dispatch-hint tests + 4 packaging pins stay RED (Phases 6–7).

## Phase 6 — Implement Offline/Core Path

**Objective.** Flip every non-packaging behaviour RED to GREEN: TTY-aware
resolution + dest recording + reworded help + the recorded-dest skill hint.

**Files changed.**

- `src/docs_cli/cli.py` — `_cmd_install_skill` refactored (OQ-A extract-method):
  it resolves `dest = Path(os.path.expanduser(_resolve_install_dest(args)))
  .resolve()` (the SINGLE expanduser/resolve, OQ-C — captured pre-mutation so a
  symlink install records the dest resolved before the link exists), calls
  `_materialise_skill(args, dest, source)` (the pre-M23 body moved VERBATIM —
  wheel-symlink refusal 2 / no-op 0 / conflict 2 / clean-slate + symlink 0 /
  copy 0), and records at the ONE call site behind `if code == 0`
  (refusals skip recording naturally, D3). D4: the `install-skill` argparse
  `help`/`description` reworded to "agent skill" (both "Claude Code" phrases
  dropped; the default path kept — a path is not a Claude-Code claim). No bundle
  re-sync needed for D4 (docs/cli.md + references/cli.md already say "agent
  skill").
- `src/docs_cli/update_check.py` — `_check_and_notify`: inside the existing
  single emit guard, immediately after the CLI notice print, `recorded =
  read_recorded_dest(); if recorded is not None: print(format_skill_hint(
  recorded), file=sys.stderr)`. Sitting inside the
  `if latest and is_newer and not notice_suppressed and should_notify(cache):`
  guard gives the hint the full suppression matrix + 24h throttle for free
  (AF-3), fires once, always last on stderr (AF-1), never stdout, verbatim
  (no fs check, AF-2); fail-silent via the `None` guard + `maybe_notify`'s
  broad except.

**Result.** All 17 non-packaging behaviour tests GREEN (D2 prompt / D3 copy /
noop / omitted-default / symlink recording / refusal-records-nothing; D4
description + short help; the dispatch hint present / verbatim-replay). Only the
4 packaging version pins remain RED. mypy/ruff/format clean; `test_skill_refs`
GREEN.

## Phase 7 — Update Tool/Wrapper Layer

**Objective.** Version bump + the OQ-D version-literal sweep + packaging parity.

**Files changed.**

- `pyproject.toml` — `version` `1.7.0` → `1.8.0`; `.venv/bin/pip install -e
  ".[dev]"` so `importlib.metadata` (= `cli.__version__` = `CURRENT`) reads
  1.8.0 (`docs --version` → 1.8.0).
- `tests/test_update_check.py` — OQ-D sweep: hoisted the `NEWER = "99.0.0"`
  sentinel up next to `CURRENT` and rebased every dispatch-block "newer PyPI
  version" literal (`_FetchSpy(version="1.7.1")` → `_FetchSpy(version=NEWER)`,
  `_expected_notice("1.7.1")` → `_expected_notice(NEWER)`) across both fires-
  and absence-asserting tests. Left the self-contained unit literals
  (`is_newer` / `format_notice` compare inputs, cache `latest_version` data,
  the fetch fake-JSON) untouched — none compare against `CURRENT`. ruff-format
  reflowed the touched lines.
- `CHANGELOG.md` — added `## 1.8.0 — UNRELEASED` above the 1.7.0 header with an
  `### Added` block (agent-aware install-skill, recorded-dest state file,
  recorded-dest skill-refresh hint).
- `tests/test_packaging.py` — no edit (A3/B1/B2/C2 already flipped to 1.8.0 in
  Phase 2 → GREEN post-reinstall).

**Result.** Packaging pins A3/B1/B2/C2 GREEN; `test_skill_refs` GREEN (cli.md /
convention.md + bundle refs unchanged in 5–7). No stale "1.7.1"-as-newer literal
remains below `CURRENT`.

## Phase 8 — Run Tests (GREEN)

**Objective.** Full suite GREEN; gate clean tree-wide; version reflects the bump.

**Command.** `.venv/bin/python -m pytest tests/ -q`

**Result.** **636 passed** (0 failed). Gate: `ruff check .` all passed;
`ruff format --check .` all formatted; `mypy` "Success: no issues found in 44
source files"; `docs check docs/` exit 0 ("no violations found"); `docs index
--root docs/ --dry-run` a byte no-op vs the committed INDEX; `docs --version`
prints `1.8.0`.

## Phase 9 — Implement Online/Integration

**Objective.** Dogfood the end-to-end behaviour on the editable install; the
pytest suite stays OFFLINE (M21 invariant). LOG ONLY — no test added.

**Method.** Ran the real `docs` console-script (editable install) with
`XDG_STATE_HOME` and `XDG_CACHE_HOME` pointed at a throwaway scratch dir; the
"newer PyPI" notice was simulated by seeding the update-check cache with a fresh
`last_check` + `latest_version = 99.0.0` (so no network is consulted — the cache
is fresh, the fetch is never called), reproducing the M21 mocked/throwaway-cache
path.

**Results.**

1. **Recording (all three success triggers).** `docs install-skill --dest <tmp>
   --copy` recorded `{"dest": "<resolved-abs>"}` to
   `$XDG_STATE_HOME/docs-cli/install-skill.json`; deleting the file and re-running
   (an already-identical **no-op**, exit 0) re-recorded it; a **`--symlink`**
   install (editable → symlink succeeds) recorded the resolved dest (the link's
   own path, not the source it points at).
2. **Newer-PyPI notice + hint.** With a dest recorded and the seeded newer
   version, `docs list --root docs/` emitted the CLI line
   `docs: update available 1.8.0 -> 99.0.0 — run: pip install -U docs-cli`
   followed by the byte-exact hint
   `docs: refresh the agent skill at <dest> — run: docs install-skill --dest <dest> --force`
   as the **LAST** stderr line.
3. **Non-TTY, `--dest` omitted, never blocks.** `docs install-skill --copy`
   with stdin redirected from `/dev/null` (non-TTY) and `HOME` at tmp exited 0
   without prompting, materialised the skill at the default
   `~/.claude/skills/docs`, and recorded that **resolved** absolute path — which
   the same run then replayed verbatim in the skill hint.
4. **Suppression matrix silences BOTH lines.** `--json` (stdout stays clean
   JSON), `--quiet` (on the `--quiet`-capable `touch`; cache still warmed),
   `CI=1`, `DOCS_CLI_NO_UPDATE_CHECK=1`, and `DO_NOT_TRACK=1` each silenced the
   CLI line and the hint together.
5. **Suite offline.** `tests/conftest.py` sets `DOCS_CLI_NO_UPDATE_CHECK=1`
   process-wide; the dispatch tests that exercise the notice re-enable it but
   inject a fake `fetch_latest_version` (`_patch_fetch` / `_FetchSpy`), so no
   test reaches the network. No networked test was added.

## Phase 10 — Quality, Docs, Refactor

**Objective.** Closeout: OQ-B stale-wording sweep, doc updates, INDEX + frozen
snapshot lockstep, surface-parity re-verify, lifecycle left `draft`. (No
`/simplify` — that is the conductor's Step 3, a separate agent.)

**Files changed.**

- **OQ-B stale-wording sweep** — reworded the four stray "Claude Code" strings
  on the install-skill surface to "agent skill": `src/docs_cli/cli.py:12`
  (module docstring), the `_DEFAULT_SKILL_DEST` const comment (reworded to "an
  assumption about which agent the user runs" so the grep is clean too),
  `main()`'s docstring subcommand line, and `src/docs_cli/__init__.py:8`. (The
  section comment above `_cmd_install_skill` was already reworded in Phase 5.)
  A tree grep confirms the install-skill **surface** (help / description /
  docstrings / comments) is clean of "Claude Code"; remaining tree hits are
  legitimately out of scope — historical archive milestones (M5/M6),
  `README.md`/`CHANGELOG.md` history, test-file docstrings, and the D4
  assertions in `test_install_skill_dest.py` that enforce the *absence* of the
  phrase.
- `docs/status.md` — M23 prose block + milestone-table row updated to
  implementation-complete (all 10 phases, 636 GREEN, `docs --version` 1.8.0,
  suite offline); the OQ-1/OQ-2 provisional-confirmation flag preserved.
- `docs/plan.md` — M23 row rewritten from the stale "Draft / milestone-setup,
  no TDD phase started / four OPEN QUESTIONS open" to implementation-complete
  with the four OQs resolved (OQ-1/OQ-2 flagged for branch-review confirm).
- `docs/m23-agent-aware-install-skill.md` — Phase Checklist (5–10), Deliverables
  (D1–D7 + gate), and Success Criteria all ticked; Overview Progress line
  updated.
- `docs/m23-agent-aware-install-skill-impl.md` — Phases 5–10 sections + progress
  table filled; Overview Progress line updated.
- `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` — regenerated in
  lockstep (`docs touch <bumped files> --check`) so the frozen snapshot matches.

**Result.** Surface-parity gate re-verified (`test_skill_refs` GREEN — cli.md /
convention.md + bundle refs byte-identical, untouched by M23's code-only
reword). Full suite **636 GREEN**; ruff / format / mypy / `docs check docs/`
clean; `docs index --root docs/ --dry-run` a byte no-op. Lifecycle left
`draft` (a later milestone publishes 1.8.0). No `/simplify` run (Step 3).

**Surfaced for operator decision (branch review).** OQ-1 (non-TTY = default)
and OQ-2 (separate `XDG_STATE` state file) were resolved **provisionally while
the operator was away**; both remain flagged in the milestone Decisions,
status.md, and plan.md for confirmation.

## Post-Phase-10 audit (consistency / completeness / accuracy)

Ran the same-instance audit (ship-milestone `consistency-check.md`) over the
phases-5–10 work. Verified every Deliverable D1–D7 + the four Success Criteria
against the milestone doc and the frozen `cli.md` contract (not memory): the
code matches the §install-skill resolution + recorded-dest prose and the
§Update-check skill-refresh-hint prose (template, coupling, verbatim replay,
no-recorded-dest → M21 unchanged) exactly; no stubs / TODOs / commented-out
code; suite fully GREEN from Phase 8. Two consistency issues found and fixed:

1. **plan.md `Updated:` not bumped.** plan.md was edited this step (the M23
   table row) but still carried `Updated: 2026-06-29`. Fixed via `docs touch
   docs/plan.md --check` → 2026-07-02; `docs/INDEX.md` + the frozen
   `tests/fixtures/expected/docs-INDEX.md` regenerated **in lockstep**
   (byte-identical, only plan.md's INDEX-row date moved).
2. **plan.md "Sequencing" prose stale.** The M23 Sequencing paragraph still
   read "draft / milestone-setup (scaffolded 2026-06-29, no TDD phase started)"
   with "Genuine OPEN QUESTIONS remain … not decided now" — contradicting the
   updated table row. Reworded to implementation-complete (all 10 phases, 636
   GREEN, `docs --version` 1.8.0) with the four OQs resolved (OQ-1/OQ-2 flagged
   for branch-review confirm).

Gate after the fixes: full suite **636 GREEN**; ruff / format / mypy clean;
`docs check docs/` exit 0; `docs index --root docs/ --dry-run` a byte no-op vs
the committed INDEX. Diff scope contained only M23 work.

## Step-2 fresh-eyes review closeout (2026-07-02)

The Step-2 fresh-eyes review returned **no blockers and no should-fix items** —
the phases-5–10 implementation is sound and ship-ready. It raised exactly one
NIT / operator-awareness judgment call, recorded here (and in the milestone doc
Decisions › "Known limitation — repeated `--symlink` recording") and **not**
code-fixed, because a fix would deviate from a binding decision:

- **NIT — repeated `--symlink` re-records the source path.** On a *repeated*
  `docs install-skill --dest <D> --symlink` where `<D>` is already the symlink
  from a prior run, `_cmd_install_skill`'s top-of-function
  `Path(os.path.expanduser(_resolve_install_dest(args))).resolve()`
  (`cli.py:5158`) chases the existing symlink to the bundled **source** tree, so
  the no-op re-run writes the source-tree path (not `<D>`) via
  `write_recorded_dest`; the D5 hint would then read
  `docs install-skill --dest <source-tree> --force`. Scope is narrow — editable
  installs only (the wheel rejects `--symlink`) and only on a *repeated*
  `--symlink` install; the first install and every copy / fresh install record
  correctly, and any later copy / fresh install re-corrects the record
  (last-write-wins, D3), so it self-heals. This is a direct consequence of the
  binding implementation-choice **OQ-C** (keep M6's single
  `expanduser().resolve()` semantics byte-for-byte, Phase 6). A fix would record
  `os.path.abspath(os.path.expanduser(<raw>))` for the recorded value **only**,
  leaving `_materialise_skill`'s `resolve()`d `dest` untouched — but that
  deviates from binding OQ-C, so it is **deferred to the operator's branch
  review**, bundled with the existing OQ-1/OQ-2 confirm-at-review flag. No code
  changed.
