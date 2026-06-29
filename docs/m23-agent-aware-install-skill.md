# M23 — Agent-aware install-skill + recorded-dest skill-refresh hint

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-06-29

Related:
- child-of: plan.md
- parent-of: m23-agent-aware-install-skill-impl.md
- implements: charter.md
- pairs-with: m23-agent-aware-install-skill-impl.md
- pairs-with: status.md
- references: m21-update-check.md

## Overview

- Milestone: M23 (v1.8.0 recommended — see OPEN QUESTIONS)
- Title: Agent-aware install-skill + recorded-dest skill-refresh hint
- Surface: `docs install-skill` becomes **agent-aware** — `--dest` is the
  single, agent-agnostic source of truth for where the bundled skill lands; the
  resolved dest is **recorded** to a small per-user state file; the
  "Claude Code skill" framing in `install-skill`'s help/description is
  neutralised to **"agent skill"**; and M21's update-check notice is extended
  with an agent-appropriate **skill-refresh hint** that points at the
  **recorded** dest. No new verb. The change is to `install-skill`'s
  resolution + a tiny state-write, plus a second (skill) line on M21's existing
  STDERR notice channel.
- Progress: **Draft (milestone-setup, 2026-06-29).** Scaffolded this session as
  the follow-on to the M21 re-scope (M21 dropped its skill half — the offline
  skill-drift notice D5 + the dual `docs install-skill --force` nudge — because
  it inspected the user's installed skill and assumed Claude Code). M23 rebuilds
  the skill-refresh story the **honest** way: record where the agent actually
  installs the skill, then replay that location in a refresh hint — **never**
  inspect the installed skill's content, **never** guess the agent. No TDD phase
  started. **Depends on M21** (it extends M21's update-notice channel). Genuine
  OPEN QUESTIONS remain (non-TTY default-vs-refuse; state-file location;
  multiple recorded dests; final version number) — for a later M23
  milestone-setup / planning pass, NOT decided here. Stays LIVE at root,
  lifecycle `draft`.

### Goal

After the M21 re-scope, docs-cli's update notice nudges only the CLI
(`pip install -U docs-cli`). The skill half — "and refresh your installed
skill" — was cut because the original design inspected the host's installed
skill (content-inspection) and assumed Claude Code (a single hardcoded dest,
`~/.claude/skills/docs/`). Both are wrong for an agent-agnostic tool: docs-cli
ships exactly **one** skill artifact (the `SKILL.md` shape), so there is no
per-agent skill *format* to detect — the only honest axis is **which directory**
the user installs it into, and that is exactly what `--dest` already expresses.

M23 makes `install-skill` honest about that axis and gives the refresh nudge a
real target:

1. `--dest` is the agent-agnostic source of truth. When it is **not** given,
   resolution is TTY-aware: an interactive human **may** be prompted for the
   dest; an agent (non-TTY) is **never** blocked on a prompt — it either takes a
   default or is refused with a clear "pass `--dest`" message (the exact
   non-TTY behaviour is an OPEN QUESTION).
2. The resolved dest is **recorded** to a small per-user state file, so a later
   run — and M21's update notice — can **replay** it. Recording/remembering is
   allowed; **content-inspection of the installed skill is not**. M23 stores a
   *path*, never a hash or a diff of the user's skill.
3. M21's update-check notice gains a second, agent-appropriate line that points
   at the **recorded** dest (e.g. `…then run: docs install-skill` to refresh
   your skill at `<recorded-dest>`), riding M21's same suppression matrix +
   24h throttle channel — so the skill nudge inherits all of M21's silence
   guarantees (`--quiet` / `--json` / `CI` / `DOCS_CLI_NO_UPDATE_CHECK` /
   `DO_NOT_TRACK`, STDERR-only, exit-code-untouched, non-TTY-visible).
4. The "Claude Code skill" wording baked into `install-skill`'s argparse
   help/description is neutralised to "agent skill", matching what `cli.md`
   already says ("Materialise the bundled `docs` **agent skill**").

Success is: an agent that ran `docs install-skill --dest <X>` once, and later
sees a newer CLI on PyPI, gets a notice that nudges both the CLI update **and**
a skill refresh at `<X>` — without docs-cli ever reading the bytes of the
installed skill or guessing which agent the user runs.

### Requirements

**Functional.**

- **D1 — `--dest` as the agent-agnostic source of truth.** `--dest` remains the
  one knob that decides where the skill lands. No agent auto-detection, no
  per-agent default map. (Out of scope: guessing the agent — see Non-goals.)
- **D2 — TTY-aware resolution when `--dest` is omitted.** Interactive TTY: MAY
  prompt the human for the dest (default offered). Non-TTY (an agent): **NEVER**
  block on a prompt — either fall back to a default dest or refuse with a clear
  actionable "pass `--dest`" message. **The non-TTY default-vs-refuse choice is
  an OPEN QUESTION** (surface, do not decide here).
- **D3 — Record the resolved dest.** On a successful `install-skill`, write the
  resolved dest path to a small per-user state file so future runs / the M21
  notice can replay it. Recording a **path only** — never the skill's content,
  never a hash/diff (the content-inspection line M21 must not cross). Idempotent
  / last-write-wins by default. **The state-file location is an OPEN QUESTION**
  (user config vs the M21 update-check cache).
- **D4 — Neutralise the Claude-Code framing.** Rewrite `install-skill`'s
  argparse `help`/`description` (`cli.py:3313-3325`) from "Claude Code skill" /
  "an agent driving Claude Code" to agent-agnostic "agent skill" wording,
  reconciling with `cli.md` (which already says "agent skill" at the
  `install-skill` synopsis). The hardcoded **default** dest may stay
  `~/.claude/skills/docs/` (a default is not an assumption that the user runs
  Claude Code) — but the prose stops *claiming* Claude Code.
- **D5 — Extend M21's update notice with a recorded-dest skill-refresh hint.**
  When a recorded dest exists AND the CLI notice fires, append an
  agent-appropriate skill-refresh hint pointed at the recorded dest, on M21's
  **same** STDERR channel under M21's **same** suppression matrix + throttle.
  When no dest has been recorded, emit only the CLI line (M21 behaviour
  unchanged). This is where the skill-refresh nudge originally in M21 lands —
  rebuilt against a *recorded path*, not a content compare.

**Non-functional.**

- **Agent-agnostic — no agent guessing.** docs-cli must not detect or assume the
  agent. The only signals are `--dest` (explicit) and the recorded dest (a
  replay of a prior explicit choice).
- **No content-inspection of the installed skill.** M23 records and replays a
  path; it never reads, hashes, or diffs the user's installed skill. (This is
  the exact line the cut D5 crossed.)
- **Zero-dependency wheel preserved** — stdlib only; no new runtime dependency.
- **Inherits M21's silence guarantees** — the skill hint rides M21's channel:
  STDERR-only, never alters the exit code, suppressed under the full M21 matrix,
  fail-silent, throttled.
- **Surface parity (plan.md "Ongoing conventions")** — the reworded `--help`,
  the bundled `SKILL.md` + `references/`, and the byte-identical
  `references/{cli,convention}.md` mirrors land in the same change; `cli.md`
  §install-skill documents the new resolution + recording + the notice's skill
  line.

### Deliverables

- [ ] **D1 — `--dest` source of truth** (no agent guessing). Pinned by tests.
- [ ] **D2 — TTY-aware resolution** when `--dest` omitted (TTY may prompt;
      non-TTY never blocks). Pinned by a TTY/non-TTY test pair. *(non-TTY
      default-vs-refuse — OPEN QUESTION.)*
- [ ] **D3 — Record resolved dest** to a per-user state file (path only).
      Pinned by a record-then-read test. *(location — OPEN QUESTION.)*
- [ ] **D4 — Reword install-skill help/description** to "agent skill"
      (reconcile with `cli.md`). Pinned by a help-string test + the skill-refs
      byte-identity gate.
- [ ] **D5 — Recorded-dest skill-refresh hint** on M21's notice channel.
      Pinned by tests (hint present when a dest is recorded; absent + M21
      unchanged when none; full M21 suppression matrix honoured for the hint).
- [ ] **D6 — Offline test harness** — TTY behaviour and the recording exercised
      offline; the M21 notice channel stays mocked (no real network).
- [ ] **D7 — Docs / version plumbing** — version bump (recommend **1.8.0** —
      OPEN QUESTION); `cli.md` §install-skill + the update-notice section
      updated; CHANGELOG entry; bundled-skill surface parity; bundled refs
      byte-identical.
- [ ] **Surface-parity gate** + INDEX/frozen-snapshot lockstep throughout.
- [ ] **Full suite GREEN**; ruff / format / mypy / `docs check docs/` exit 0.

## Current State Analysis

- **Existing code.** `install-skill` is fully built (M6): the parser is at
  `cli.py:3311-3357`, with the `help`/`description` at `cli.py:3313-3325`
  framing it as "the bundled `docs` **Claude Code** skill" / "an agent driving
  **Claude Code**" — this Claude-Code framing + the hardcoded default
  `--dest ~/.claude/skills/docs/` are the M23 problem (D4). `_cmd_install_skill`
  (`cli.py:5114`) resolves the dest at `cli.py:5124`
  (`dest = Path(os.path.expanduser(args.dest)).resolve()`) and copies/symlinks
  the bundle. The skill-tree helpers already exist:
  `_SKILL_RELATIVE_FILES` (`cli.py:5055`), `_locate_bundled_skill()`
  (`cli.py:5070`), `_trees_byte_identical()` (`cli.py:5097`). `cli.md`'s
  `install-skill` section already says "agent skill" — so D4 is a
  reconcile-the-help-to-the-spec change, not a spec rewrite.
- **M21 dependency.** M21 introduces the update-check module
  (`src/docs_cli/update_check.py`) + the `main()` notice hook (`cli.py:5194`)
  and the per-user cache
  `${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json`. M23's D5 extends
  that notice; M23's D3 state file is either a new user-config file or a key in
  M21's cache (OPEN QUESTION). `__version__` (`cli.py:44`) is the
  `importlib.metadata` SoT (M12).
- **Missing.** No dest-recording state anywhere; no TTY-aware resolution
  (`--dest` has a static default and is never prompted); the help text still
  names Claude Code; the M21 notice has no skill line.
- **Known issues / constraints.** No content-inspection of the installed skill
  (the cut-D5 line). No agent guessing. Exit codes load-bearing; `--json`
  stdout byte-clean; zero-dependency wheel; suite stays offline.

## TDD Implementation Plan

Phases follow the canonical 10-phase TDD methodology. Several phase objectives
depend on the OPEN QUESTIONS (non-TTY default-vs-refuse; state-file location;
version) — a later M23 planning pass resolves those before Phase 1 freezes the
contract.

### Phase 1: Define Contract
- Objective: freeze the `install-skill` resolution contract (TTY-aware,
  `--dest` SoT), the recorded-dest state-file schema + location, the reworded
  "agent skill" help, and the M21-notice skill-hint wording — in `cli.md`
  (§install-skill + §update-check). Resolve the four OPEN QUESTIONS first.
- Files: `docs/cli.md`, `docs/convention.md` (if the state file is user-config),
  `src/docs_cli/skill/references/{cli,convention}.md`, INDEX + snapshot.
- Exit: contract strings present; `test_skill_refs` GREEN; `docs check` exit 0.

### Phase 2: Write Tests (RED)
- Objective: failing tests for D1-D5 — `--dest` SoT; TTY-prompt vs non-TTY
  no-block; record-then-replay (path only); reworded help; the recorded-dest
  skill hint on M21's channel + suppression-matrix coverage; all offline (M21
  notice mocked).
- Files: a new `tests/test_install_skill_dest.py` (+ additions to the
  update-check + install-skill suites); `tests/test_packaging.py` version flip.
- Exit: tests collect cleanly; RED vs GREEN-at-baseline classified.

### Phase 3: Create Data/Fixtures
- Objective: inline `tmp_path` builders — a fake recorded-dest state file in
  each state (present / absent / stale-path), a TTY/non-TTY harness. No
  committed dated fixtures.
- Files: inline builders; the frozen `docs-INDEX.md` snapshot stays the only
  committed fixture, in lockstep.
- Exit: date-independent test data; no rotting fixture.

### Phase 4: Run Tests (RED Baseline)
- Objective: confirm intended-RED fails for its reason; capture the baseline
  count; pre-existing suite stays GREEN.
- Files: none (run only).
- Exit: RED set matches the plan.

### Phase 5: Update Base Interfaces
- Objective: declare seams — the dest-recording read/write helpers (path-only),
  the TTY-aware resolver, and the M21-notice extension point (a recorded-dest
  accessor the notice formatter can call). Minimal logic.
- Files: `src/docs_cli/cli.py` (resolver + recording) and/or
  `src/docs_cli/update_check.py` (the notice extension + the state accessor,
  depending on the state-file-location OPEN QUESTION).
- Exit: type checks pass; tests import the seam.

### Phase 6: Implement Offline/Core Path
- Objective: implement TTY-aware resolution + dest recording + the reworded help
  + the recorded-dest skill hint on M21's channel; honour the full M21
  suppression matrix for the hint. All offline RED → GREEN.
- Files: `src/docs_cli/cli.py`, `src/docs_cli/update_check.py`.
- Exit: offline target tests GREEN; no regression.

### Phase 7: Update Tool/Wrapper Layer
- Objective: version bump (recommend 1.8.0 — OQ); packaging version pins in
  lockstep; CHANGELOG entry; bundled `SKILL.md` + `references/` resynced
  byte-identical; reconcile the reworded `--help` into the bundle.
- Files: `pyproject.toml`, `tests/test_packaging.py`, `CHANGELOG.md`,
  `src/docs_cli/skill/`.
- Exit: version pin GREEN; `test_skill_refs` GREEN.

### Phase 8: Run Tests (GREEN)
- Objective: full suite GREEN; gate clean tree-wide; `docs --version` reflects
  the bump.
- Files: none (run + capture).
- Exit: all targeted tests green; gate clean.

### Phase 9: Implement Online/Integration
- Objective: dogfood end-to-end on an editable install — `install-skill --dest`
  records the dest; a simulated newer-PyPI notice (M21's mocked/throwaway-cache
  path) shows the CLI line **and** the recorded-dest skill hint; non-TTY never
  blocks; suppression matrix silences both lines. The pytest suite stays
  offline (M21 invariant).
- Files: log only.
- Exit: end-to-end behaviour verified + dogfooded.

### Phase 10: Quality, Docs, Refactor
- Objective: closeout summaries; INDEX + frozen snapshot lockstep; status/plan
  updated; surface-parity gate (`--help` reconciliation + stale-wording grep
  for "Claude Code"); lifecycle left `draft`; `/simplify` pass.
- Files: the M23 pair, `status.md`, `plan.md`, `src/docs_cli/skill/`.
- Exit: gate green; docs current; lifecycle `draft`.

## Phase Checklist

- [ ] Phase 1 — Define Contract
- [ ] Phase 2 — Write Tests (RED)
- [ ] Phase 3 — Create Data/Fixtures
- [ ] Phase 4 — Run Tests (RED Baseline)
- [ ] Phase 5 — Update Base Interfaces
- [ ] Phase 6 — Implement Offline/Core Path
- [ ] Phase 7 — Update Tool/Wrapper Layer
- [ ] Phase 8 — Run Tests (GREEN)
- [ ] Phase 9 — Implement Online/Integration
- [ ] Phase 10 — Quality, Docs, Refactor

## Decisions

- **Provenance — born from the M21 re-scope (2026-06-29).** M21 was re-scoped
  to a CLI-only update notice; its skill half (the offline skill-drift notice
  D5 + the dual `docs install-skill --force` nudge) was **CUT** because it
  inspected the user's installed skill and assumed Claude Code. M23 is the
  honest rebuild: record where the skill is installed, then replay that path in
  a refresh hint. See [m21-update-check.md](m21-update-check.md) Decisions ›
  "Re-scope to CLI-only".
- **`--dest` is the source of truth, agent-agnostically (BINDING).** docs-cli
  ships exactly one skill artifact; there is no per-agent skill *format* to
  detect, so "which directory" (`--dest`) is the only honest axis. No agent
  auto-detection, no per-agent default map.
- **Record/replay a path; never inspect content (BINDING).** M23 stores the
  resolved dest *path* and replays it; it never reads, hashes, or diffs the
  installed skill. This is the precise line the cut D5 crossed and the
  invariant M23 must hold.
- **Non-TTY never blocks on a prompt (BINDING).** An agent (non-TTY) must never
  hang waiting for input. When `--dest` is omitted on a non-TTY, the tool takes
  a default or refuses with an actionable message — the *which* is an OPEN
  QUESTION, but "never block" is fixed.
- **The skill hint rides M21's channel (BINDING).** The recorded-dest
  skill-refresh hint reuses M21's STDERR notice, suppression matrix, and 24h
  throttle — it inherits every silence guarantee and never alters the exit code.
- **Out of scope: skill FORMATS + agent detection.** M23 is about skill
  *location* + recording, not multi-agent skill formats and not
  guessing/detecting the agent. (Operator rule: don't guess the agent — ask on
  a TTY or take `--dest`.)
- **Recommended version: 1.8.0** (a minor bump — additive, consistent with the
  1.3→1.7 minor cadence). Not finalised — see OPEN QUESTIONS (it ships a later
  version than M21's 1.7.0 regardless).

## Testing / Quality Gate

The standard tree-wide gate plus the new behaviour tests, **all offline**:

```sh
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
.venv/bin/docs check docs/
.venv/bin/docs index --root docs/ --dry-run
```

Test invariants: TTY-aware resolution (TTY may prompt; non-TTY never blocks),
record-then-replay of the dest **path only** (no content read), the reworded
"agent skill" help, and the recorded-dest skill hint on M21's channel — present
when a dest is recorded, absent (M21 unchanged) when none, and silenced by the
full M21 suppression matrix. The M21 notice stays mocked; **no test performs a
real network call** (M21's offline invariant preserved).

## Success Criteria

M23 is complete when:

- [ ] `install-skill` resolves the dest TTY-aware (`--dest` SoT; TTY may prompt;
      non-TTY never blocks) and **records** the resolved path to the per-user
      state file (path only — no content read).
- [ ] `install-skill`'s help/description say "agent skill" (no "Claude Code"),
      reconciled with `cli.md`; a stale-wording grep for "Claude Code" in the
      install-skill surface is clean.
- [ ] M21's update notice gains a recorded-dest skill-refresh hint on the same
      STDERR channel, under the same suppression matrix + throttle; absent when
      no dest is recorded (M21 behaviour unchanged).
- [ ] No content-inspection of the installed skill; no agent guessing anywhere.
- [ ] Suite fully offline; bundled refs byte-identical (`test_skill_refs`
      GREEN); INDEX + frozen snapshot in lockstep.
- [ ] Version bumped (recommend 1.8.0 — OQ); CHANGELOG entry; `docs --version`
      reflects it; full suite GREEN; gate clean. NO publish (a later milestone
      publishes).

## OPEN QUESTIONS

Genuine scope/contract forks for a later M23 milestone-setup / planning pass.
Each: question, why it matters, leaning. **Do not decide here.**

- **OQ-1 — Non-TTY (agent) behaviour when `--dest` is omitted: default vs
  refuse?** *Why:* an agent must never block on a prompt, so the tool either
  falls back to a default dest (convenient, but writes to a Claude-Code-shaped
  path the user may not want) or refuses with "pass `--dest`" (explicit, but
  one more step for the common agent case). *Leaning:* undecided — both are
  defensible; resolve at the next planning pass. (Fixed regardless: non-TTY
  never blocks.)
- **OQ-2 — Where is the recorded dest stored: a user-level config file vs a key
  in M21's update-check cache?** *Why:* M21 already owns
  `${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json` (a cache — ephemeral,
  XDG_CACHE) and has a *deferred* user-config location
  `${XDG_CONFIG_HOME:-~/.config}/docs-cli/config.toml` (durable, XDG_CONFIG). A
  recorded dest is arguably durable user state (config), but co-locating it in
  the update-check cache keeps the notice's replay read trivial. *Leaning:*
  undecided — weigh durability vs locality.
- **OQ-3 — Support multiple recorded dests, or last-write-wins single dest?**
  *Why:* a user may install the skill into more than one location (e.g. two
  agents/hosts). One recorded dest is simplest; a small set is more faithful but
  complicates the notice (which dest(s) to name). *Leaning:* start with
  last-write-wins single dest; revisit if real multi-dest use appears.
- **OQ-4 — Final version number (recommend 1.8.0).** *Why:* M23 is additive
  (new resolution behaviour + a recorded-state file + an extra notice line) and
  the project uses minor bumps for features (1.3→1.7). It ships a later version
  than M21's 1.7.0. *Leaning:* **1.8.0** — but confirm at planning (e.g. if it
  is batched with another feature, or if the operator wants a different bucket).
