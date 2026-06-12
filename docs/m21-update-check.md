# M21 — Update-check notification (PyPI version check + skill-refresh nudge)

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-06-12

Related:
- child-of: plan.md
- parent-of: m21-update-check-impl.md
- implements: charter.md
- pairs-with: m21-update-check-impl.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: status.md

## Overview

- Milestone: M21 (v1.7.0)
- Title: Update-check notification (PyPI version check + skill-refresh nudge)
- Surface: docs-cli's **first network surface** — a once-per-24h, fail-silent
  check of PyPI for a newer `docs-cli` release that, when one exists, emits a
  single STDERR line nudging the user/agent to update **both** the CLI and
  their installed skills (`pip install -U docs-cli`, then `docs install-skill
  --force`). The notice never touches stdout, never changes an exit code, is
  suppressed under `--quiet` / `--json` / CI / opt-out env+config, and —
  **deliberately inverting gh's TTY-gated rule** — shows on non-TTY too,
  because the primary consumer is an agent that is itself the actor who
  performs the update. A zero-network skill-drift check rides
  along (ships IN — D5, OQ-6): when the host's installed skill differs from
  the CLI's own bundled skill, the same one-line channel nudges
  `docs install-skill --force`. Ships as **v1.7.0** (minor bump — additive
  feature; matches the 1.3→1.6 minor precedent; 1.6.5 was an operator-decreed
  patch exception). Implementation milestone — builds 1.7.0 locally; the PyPI
  publish is a later operator-driven milestone (the M19→M20, M14+M15→M17
  pattern).
- Progress: **Draft (milestone-setup, 2026-06-12).** Scaffolded 2026-06-12
  from the operator-directed M21 scope (design + precedent researched and
  operator-reviewed this session). No TDD phase started. Depends on nothing;
  nothing else in flight (M18/M19/M20 all shipped + archived). Stays LIVE at
  root; lifecycle `draft` until a later milestone sweeps it in (the
  M14/M15/M18/M19 completed-but-live precedent). OPEN QUESTIONS OQ-1..OQ-9 are
  RESOLVED (conductor decisions 2026-06-12, each per the recommended default —
  see Decisions › "Resolved questions"); milestone-setup is complete and
  Phase 1 (Define Contract) is next.

### Goal

Today an installed `docs-cli` never tells the operator (or the agent driving
it) that a newer release is on PyPI. The CLAUDE.md ship-time flow is a
two-step refresh — `pip install -U docs-cli`, then `docs install-skill
--force` to refresh the host skills — and nothing surfaces that it is due. The
host's own 2026-06-12 drift (a stale `--body-from` reference in a workflow
skill, caught only at the M20 publish-closeout sweep) is the motivating miss:
the update signal arrives too late, by hand, at publish time.

M21 makes `docs-cli` self-announce. On any invocation, **at most once per 24h**
and **fail-silent always**, the CLI consults PyPI for the latest `docs-cli`
version, compares it against the running version (the `importlib.metadata` SoT
from M12), and — when newer — prints **one** STDERR line that names **both**
update actions. The check is gated by a per-user state cache (one network
attempt per 24h) and a separate per-user notify throttle (one notice per 24h),
so it never spams and never adds latency or noise to the common case. Offline,
timeout, HTTP error, or a corrupt cache all degrade to **byte-identical
behaviour and exit code** vs today — the notice simply does not appear.

The primary consumer is an **agent**, and the agent is the actor who can
*perform* the update (run the two commands). That is why M21 deliberately
inverts gh's TTY-gated convention: the notice shows on non-TTY too. The
suppression matrix (`--quiet`, `--json`, CI, two disable env vars, a config
opt-out) keeps it out of machine-readable streams, scripts, and CI logs.

### Requirements

**Functional.**

- **Update check (D1).** GET `https://pypi.org/pypi/docs-cli/json`, parse
  `info.version`, compare against `__version__` (the M12 `importlib.metadata`
  SoT). **At most one network attempt per 24h**, gated by a per-user state
  cache. **Stdlib `urllib` only** (the zero-dependency wheel is preserved —
  no `requests`). **Short timeout** (recommend 1.0s — OQ-2). **Fail-silent
  always**: offline / DNS failure / timeout / non-200 / malformed JSON /
  unparseable version → no notice, no traceback, exit code and all streams
  byte-identical to today.
- **State cache (D1).** `${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json`
  with `last_check` (ISO timestamp), `latest_version` (last seen PyPI version),
  `last_notified` (ISO timestamp of the last emitted notice). Created on first
  successful check; read on every invocation to gate the network call and the
  notice. A missing / unreadable / malformed cache is treated as "no data" and
  silently rewritten — never fatal.
- **Notification (D2).** When `latest_version > __version__` (stdlib numeric
  tuple-compare, fail-closed on pre-release/local/unparseable — OQ-3), emit
  **one** line on **STDERR**, at most once per 24h (the separate
  `last_notified` throttle), naming **both** actions. Reference wording:
  `docs: update available 1.6.5 -> 1.7.0 — pip install -U docs-cli, then docs
  install-skill --force to refresh skills`. **NEVER** on stdout; **NEVER**
  affects the exit code (exit codes are load-bearing — the M19 `touch --check`
  fold proves the project treats them as a contract).
- **Suppression matrix (D3).** Each of the following suppresses the notice;
  those marked *(check too)* also skip the network call entirely:
  - `--quiet` — suppress the notice (the check may still warm the cache —
    OQ-4).
  - `--json` (any verb in JSON mode) — suppress the notice; stdout stays
    byte-clean JSON (the check may still warm the cache — OQ-4).
  - `CI` env var set (any value) — suppress notice **and** check *(check too)*
    (npm / gh precedent: never nag in CI).
  - `DOCS_CLI_NO_UPDATE_CHECK` env set — disable the feature entirely *(check
    too)* (the project-specific kill switch; gh's `GH_NO_UPDATE_NOTIFIER`
    analogue).
  - `DO_NOT_TRACK` env set — disable the feature entirely *(check too)* (the
    emerging cross-tool convention; consoledonottrack.com).

  A user-level **config opt-out is DEFERRED out of v1.7.0** (OQ-5/5a resolved):
  the two env vars + the `CI` skip cover every realistic per-user opt-out, so
  M21 ships **no config file**. When a future milestone adds one, its location
  is already settled — a **user-level** config at
  `${XDG_CONFIG_HOME:-~/.config}/docs-cli/config.toml` with `[update_check]
  enabled = false`, **never** `.docs.toml` (which is per-tree, while this check
  is per-user) — and need not be re-litigated.
- **TTY inversion (D4).** Show the notice on **non-TTY** too (the deliberate
  inversion of gh's TTY-gated rule). Rationale + precedent recorded as a
  binding Decision. This is what makes the agent — the non-TTY consumer — the
  recipient of the nudge it can act on.
- **Offline skill-drift check (D5 — ships IN M21, OQ-6 resolved).** A fully
  **offline, zero-network** check: `install-skill` already knows its default
  dest (`~/.claude/skills/docs/`, `cli.py:3329`); the CLI can cheaply compare
  the installed skill against its own bundled skill
  (`importlib.resources` → `src/docs_cli/skill/`) and, on a difference, emit
  the same one-line channel nudging `docs install-skill --force`. Zero network,
  zero new risk; it catches the exact host drift found 2026-06-12. Ships as a
  second, independent notice gated by the same suppression matrix + its own
  third throttle key (`last_skill_drift_notified`); every ambiguous install
  state (absent dir, unreadable, partially-installed, symlinked, a *newer* host
  skill than the bundled one) falls **silent**.

**Non-functional.**

- **Zero-dependency wheel preserved** — stdlib `urllib` only; no new runtime
  dependency in `pyproject.toml`.
- **No measurable latency in the common case** — the cache read short-circuits
  before any network work; the 24h gate means the network is touched at most
  once per day; the timeout bounds the rare network path.
- **Suite stays fully offline** — the checker is **injectable / mockable**;
  no test makes a real network call (D6). The default test posture is
  network-disabled.
- **Surface parity (plan.md "Ongoing conventions")** — any new `--help`
  strings, the bundled skill (`SKILL.md` + `references/`), and the byte-identical
  `references/{cli,convention}.md` mirrors all land in the same change.

### Deliverables

- [ ] **D1 — Update check + state cache.** A mockable checker queries
      `https://pypi.org/pypi/docs-cli/json` (stdlib `urllib`, short timeout),
      compares `info.version` to `__version__`, and persists
      `{last_check, latest_version, last_notified}` to
      `${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json`. One network
      attempt per 24h (cache-gated). Fail-silent on every error path
      (offline / timeout / non-200 / malformed JSON / corrupt cache) →
      byte-identical behaviour + exit code. Pinned by Phase-2 tests.
- [ ] **D2 — Notification.** One STDERR line, ≤ once per 24h (separate
      `last_notified` throttle), naming both actions in the reference wording.
      Never on stdout; never alters the exit code. Pinned by Phase-2 tests
      (notice text + stream + exit-code-unchanged on success AND failure verbs).
- [ ] **D3 — Suppression matrix.** `--quiet`, `--json`, `CI`,
      `DOCS_CLI_NO_UPDATE_CHECK`, and `DO_NOT_TRACK` each suppress the notice;
      `CI` + the two env vars also skip the network call (the user-level config
      opt-out is DEFERRED out of v1.7.0 — OQ-5/5a). Pinned by one Phase-2 test
      per path + a `--json` stdout-byte-clean lock.
- [ ] **D4 — TTY inversion.** Notice shows on non-TTY (recorded as a binding
      Decision with precedent). Pinned by a non-TTY (piped-stderr) test that
      still sees the notice.
- [ ] **D5 — Offline skill-drift notice (ships IN M21 — OQ-6 resolved YES).**
      Zero-network compare of the installed skill vs the bundled skill; on
      drift, a one-line `docs install-skill --force` nudge through the same
      suppressed/throttled channel (its own third throttle key
      `last_skill_drift_notified`). Pinned by Phase-2 tests (drift → notice;
      in-sync → silent; missing/ambiguous install dir → silent; suppression
      honoured).
- [ ] **D6 — Offline test harness.** The checker is injectable/mockable; the
      suite makes **no** real network call. Tests pin: no network when cache
      fresh; both 24h throttles (check + notify, independently); every
      suppression path; exit codes unchanged on every verb incl. failures;
      malformed/corrupt cache handled silently; the notice format; and that
      `--json` stdout stays byte-clean.
- [ ] **D7 — Docs / version plumbing.** Version → **1.7.0**
      (`pyproject.toml` + the `test_packaging.py` A3/B1/B2/C2 version pins, the
      A3-fast / B1-B2-C2-slow split per the M19 precedent); a NEW
      `## 1.7.0 — UNRELEASED` CHANGELOG section; `cli.md` (a new
      §update-check / §Output-conventions note + the suppression-env table —
      env vars + `CI` only; the config opt-out is DEFERRED, OQ-5/5a) contract
      sections; bundled-skill surface parity; `references/{cli,
      convention}.md` byte-identical.
- [ ] **Surface-parity gate (Phase 10, plan.md "Ongoing conventions").** Run
      `docs --help` / any changed verb `--help`; reconcile against the
      CHANGELOG surface; confirm the bundled skill documents the new env vars +
      notice; grep for stale wording. INDEX + frozen snapshot
      (`tests/fixtures/expected/docs-INDEX.md`) in lockstep throughout.
- [ ] **Full suite GREEN** (current 540 + the new M21 tests); ruff / ruff
      format --check / mypy / `docs check docs/` exit 0; bundled cli.md /
      convention.md byte-identical; `docs --version` → `docs 1.7.0`.

## Current State Analysis

- **Existing code.** `__version__` is the M12 `importlib.metadata.version(
  "docs-cli")` SoT (`cli.py:44`) with a `0.0.0+local` fallback — exactly the
  string the check compares against. `main()` (`cli.py:5194`) is a flat
  dispatch that returns an `int` exit code; the update-check hook lands here
  (after the command runs, before `main` returns, emitting only to STDERR and
  **passing the command's exit code through untouched**). `--quiet` and
  `--json` are per-verb argparse flags today (no global `args.quiet`/`args.json`
  on every namespace — see OQ-1). `install-skill`'s default dest
  (`~/.claude/skills/docs/`, `cli.py:3329`) + the bundled skill via
  `importlib.resources` give D5 everything it needs offline.
- **Missing.** No network surface exists anywhere in the tree (`grep urllib |
  http | socket | .cache | XDG_CACHE` → zero hits) — M21 introduces the first,
  recorded as an explicit architectural Decision. No cache directory handling,
  no version-compare helper, no env-var suppression plumbing.
- **Known issues / constraints.** Exit codes are a load-bearing contract
  (M19 `touch --check` fold; cli.md "Exit codes"). The suite is fully offline
  and must stay so (D6). The zero-dependency wheel is a charter promise
  (charter.md "runs on any host with Python 3.11+ … no third-party
  dependencies") — stdlib `urllib` only. `--json` stdout must stay
  byte-clean (existing `docs check --json` / `docs list --json` consumers).

## TDD Implementation Plan

Phases follow the canonical 10-phase TDD methodology. OQ-1..OQ-9 are RESOLVED
(see Decisions › "Resolved questions"), so the per-phase objectives, files, and
exit criteria below are settled; refine only as implementation surfaces detail.

### Phase 1: Define Contract
- Objective: pin the M21 surface in the specs (no code, no tests) — `cli.md`
  §update-check (notice wording, STDERR-only, exit-code-untouched, the
  per-user cache schema + path, the 24h check + notify throttles, the
  suppression matrix incl. the env-var table, the TTY-inversion), `cli.md`
  §Output-conventions note, the D5 skill-drift notice (IN — OQ-6); the
  user-level config opt-out is DEFERRED out of v1.7.0 (OQ-5/5a — no
  `convention.md` opt-out row this milestone); OQ-1..OQ-9 already resolved into
  Decisions at milestone-setup; resync the bundled refs byte-identical; record
  the CHANGELOG version decision (new `## 1.7.0 — UNRELEASED`).
- Files: `docs/cli.md`, `docs/convention.md`, `src/docs_cli/skill/references/{cli,convention}.md`, `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md`.
- Exit: every Phase-2 assertion string present verbatim in the specs;
  `test_skill_refs` GREEN; `docs check docs/` exit 0; INDEX == snapshot.

### Phase 2: Write Tests (RED)
- Objective: express the contract as failing tests, split by layer (the M19
  no-new-file-where-possible precedent), all behind the mock seam (no real
  network). Cover: fresh-cache-no-network; check-throttle (24h); notify-
  throttle (24h, independent); newer→notice / same→silent / older→silent;
  notice text + STDERR stream; exit-code unchanged on a success verb AND a
  failing verb; each suppression path; `--json` stdout byte-clean; corrupt
  cache silent; offline/timeout/non-200/malformed-JSON each silent; non-TTY
  still sees notice; D5 drift/in-sync/missing cases; A3 version pin 1.7.0.
- Files: a new `tests/test_update_check.py` (the unit + injectable-checker
  surface) + targeted additions to existing CLI suites for the dispatch-level
  notice; `tests/test_packaging.py` A3 flip.
- Exit: tests import + collect cleanly; intended-RED vs GREEN-at-baseline
  classified for Phase 4.

### Phase 3: Create Data/Fixtures
- Objective: provide the test data — a fake PyPI JSON payload builder, cache
  files in each state (fresh / stale / missing / corrupt), and a fake bundled-
  vs-installed skill pair for D5 — preferring inline `tmp_path` builders with
  today-relative timestamps (the M19 "committed dates rot" decision).
- Files: inline builders in `tests/test_update_check.py`; no committed dated
  fixtures; the byte-frozen `docs-INDEX.md` snapshot stays the only committed
  fixture, in lockstep.
- Exit: every Phase-2 test has date-independent data; no rotting fixture.

### Phase 4: Run Tests (RED Baseline)
- Objective: confirm every intended-RED test fails for its classified reason
  (no tracebacks / collection errors / argparse-exit-2 surprises); classify
  RED vs GREEN-at-baseline; capture the baseline count verbatim.
- Files: none (run only).
- Exit: the RED set matches the plan; GREEN-at-baseline locks pass; the
  untouched pre-existing 540 stay GREEN.

### Phase 5: Update Base Interfaces
- Objective: declare the seams with minimal logic — the cache dataclass +
  read/write helpers (XDG-aware path), the injectable `fetch_latest_version`
  hook (default = real `urllib` GET; tests inject a fake), the stdlib
  tuple-compare helper (fail-closed on pre-release/local/unparseable — OQ-3),
  the env-var suppression predicate, and the `main()` hook point (interface
  declared; full wiring may land Phase 6 per the honest split).
- Files: a dedicated `src/docs_cli/update_check.py` module (OQ-7 ACCEPTED — the
  Step-1 planning agent pressure-tests it against the single-file `cli.py`
  convention + confirms the B3 wheel-contents test tolerates the new module
  before this phase commits to it); `src/docs_cli/cli.py` for the `main()` hook
  point.
- Exit: type checks pass; tests can import the seam; behaviour may stay
  unchanged this phase.

### Phase 6: Implement Offline/Core Path
- Objective: implement the offline/core path — cache read/write + both 24h
  throttles + the suppression matrix + the stdlib fail-closed tuple-compare
  (OQ-3) + the notice formatter + the `main()` STDERR emission with exit-code
  pass-through; the D5 offline skill-drift compare (its own third throttle
  key). The **network** call stays behind the injected hook (its real-`urllib`
  body is the Phase-9 online surface). All offline RED → GREEN.
- Files: `src/docs_cli/update_check.py` (the OQ-7 module) + `src/docs_cli/cli.py`
  (the `main()` hook).
- Exit: offline target tests GREEN; no regression in the 540.

### Phase 7: Update Tool/Wrapper Layer
- Objective: `pyproject.toml` `version` → `1.7.0`; the `test_packaging.py`
  A3/B1/B2/C2 version pins flipped in lockstep (A3 fast; B1/B2/C2 slow,
  build-gated — the M19 split); a NEW `## 1.7.0 — UNRELEASED` CHANGELOG
  section (Added: update-check notice + the disable env vars + the offline
  skill-drift notice); bundled `cli.md`/`convention.md` resynced byte-identical;
  the new `--help` / env-var wording reconciled into the bundled `SKILL.md`.
- Files: `pyproject.toml`, `tests/test_packaging.py`, `CHANGELOG.md`,
  `src/docs_cli/skill/`.
- Exit: `test_a3` GREEN at 1.7.0; `test_skill_refs` GREEN.

### Phase 8: Run Tests (GREEN)
- Objective: full suite GREEN; quality gate clean tree-wide (ruff / format /
  mypy / `docs check docs/` / INDEX dry-run byte-no-op); `docs --version` →
  `docs 1.7.0` after an editable reinstall. Paste the GREEN output verbatim.
- Files: none (run + capture).
- Exit: all targeted tests green; gate clean.

### Phase 9: Implement Online/Integration
- Objective: the **only** genuinely-online phase in the project's history —
  implement + exercise the real `urllib` GET behind the injected hook against
  the live PyPI JSON endpoint on a throwaway cache dir (read-only probe; never
  in the unit suite), and dogfood the end-to-end notice on the editable
  `docs 1.7.0`: confirm the notice appears once, the 24h gate suppresses the
  second invocation, each suppression env var silences it, `--json` keeps
  stdout byte-clean, and the exit code is unchanged. Document the measured
  behaviour. (OQ-8 RESOLVED: the single real probe runs OUTSIDE the pytest
  suite on a throwaway cache; pytest stays 100% offline.)
- Files: log only (+ the real-`urllib` body finalised if deferred from Phase 6).
- Exit: online path verified + dogfooded (OQ-8); cache/throttle/suppression
  confirmed end-to-end.

### Phase 10: Quality, Docs, Refactor
- Objective: closeout summaries (checklist + Deliverables + Success Criteria
  ticked, impl-log rows); INDEX + frozen snapshot lockstep; status/plan
  updated; the surface-parity gate run (`--help` reconciliation + the env-var
  table + stale-wording grep); lifecycle left `draft` (the M14/M15/M18/M19
  completed-but-live precedent — M21 stays live until a later milestone sweeps
  it in; the PyPI publish is a separate future milestone). `/simplify` pass
  over the new wiring.
- Files: the M21 pair, `status.md`, `plan.md`, `src/docs_cli/skill/`.
- Exit: gate green; docs current; lifecycle `draft`; ready for a later
  publish milestone.

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

- **Ships as v1.7.0 (minor bump).** The update-check notice is an additive,
  backward-compatible feature: no flag removed, no default changed, no exit
  code altered, and trees/users who set a disable env var or config key see
  byte-identical behaviour to 1.6.5. Minor is the right SemVer bucket and
  matches the 1.3.0 → 1.4.0 → 1.5.0 → 1.6.0 minor cadence; 1.6.5 was the
  operator-decreed **patch** exception (M19), not the rule. `pyproject.toml`
  `version` + the `test_packaging.py` A3/B1/B2/C2 pins bump to `1.7.0` at
  Phase 7; `importlib.metadata` stays the SoT (M12), so `docs --version` reads
  `1.7.0` after an editable reinstall. Builds locally; the PyPI publish is a
  later operator-driven milestone (the M19→M20, M14+M15→M17 cadence).
- **CHANGELOG: a NEW `## 1.7.0 — UNRELEASED` section.** The `## 1.6.5` section
  is dated + published (M20, 2026-06-12), so M21 opens a fresh section above it
  with publish-survival wording (no "ready locally" / "deferred" markers — the
  M11 lesson). The eventual publish milestone dates it.
- **First network surface — recorded as an explicit architectural Decision.**
  Until M21, `docs-cli` made **zero** network calls (verified:
  `grep urllib|http|socket|.cache` over `src/` → zero hits). M21 introduces
  one, and only one: an HTTPS GET to `https://pypi.org/pypi/docs-cli/json`.
  The guard rails make it safe to be the first: **stdlib `urllib` only** (the
  zero-dependency wheel — a charter promise — is preserved), a **short
  timeout**, **at most one attempt per 24h** (cache-gated), **fail-silent on
  every error path** (so an offline host, a DNS failure, a PyPI outage, or a
  corrupt cache all leave behaviour + exit code byte-identical to today), and
  **no telemetry** — the request is a plain version GET that sends nothing
  about the user (no UUID, no usage data; `DO_NOT_TRACK` is honoured anyway as
  the cross-tool courtesy). The network body lives behind an **injectable
  hook** so the entire test suite stays offline.
- **DELIBERATE inversion of gh's TTY rule — show the notice on non-TTY too.**
  gh, npm, and most update-notifiers gate the notice on an interactive TTY (so
  it never corrupts piped/scripted output). M21 **inverts** that: the primary
  consumer of `docs-cli` is an **agent**, the agent runs non-interactively
  (non-TTY), and the agent is precisely the actor who can *perform* the update
  (`pip install -U docs-cli` + `docs install-skill --force` — automating the
  CLAUDE.md ship-time flow). Gating on TTY would hide the nudge from the one
  consumer who can act on it. The safety the TTY rule buys — never corrupting a
  consumed stream — is instead bought by **(i)** emitting only to **STDERR**
  (never stdout), **(ii)** suppressing under `--json` (the machine-readable
  stdout path), and **(iii)** the env opt-outs (`CI`, `DO_NOT_TRACK`,
  `DOCS_CLI_NO_UPDATE_CHECK`). Precedent cited for the design (each studied
  this session):
  - **gh CLI** — a 24h notifier with persisted timestamps (cli/cli#85, #743):
    TTY-gated, `GH_NO_UPDATE_NOTIFIER` kill switch, skips CI. M21 keeps the
    24h-persisted-timestamp shape + the kill switch and the CI skip; it
    **drops** the TTY gate (the inversion).
  - **npm `update-notifier`** — 1-day default check interval, defers the
    notice to the *next* run (never blocks the current one), `NO_UPDATE_NOTIFIER`
    opt-out, auto-skips CI + tests. M21 borrows the deferred/throttled,
    cache-persisted shape and the CI/test auto-skip.
  - **Terraform Checkpoint** — `CHECKPOINT_DISABLE` single env kill switch.
    M21 mirrors the single-env-var disable (`DOCS_CLI_NO_UPDATE_CHECK`).
  - **pip's always-on "new release" notice** — cited as the **anti-pattern**:
    it nags in CI, has regressed output streams, and cannot be cleanly
    silenced per-invocation. M21 avoids it via the suppression matrix + the
    STDERR-only + the throttle.
  - **aider** — the agent-CLI precedent: a default-on launch update check, an
    exit-code-clean machine mode, and a disable toggle. M21 matches the
    agent-first, default-on, machine-clean posture.
- **STDERR only; exit code never touched.** The notice is informational, not a
  result. It goes to STDERR (so stdout — especially `--json` — stays the
  command's clean output) and the `main()` hook returns the command's own exit
  code unchanged. Exit codes are a load-bearing contract in this project (the
  M19 `touch --check` `max(touch, check)` fold; cli.md "Exit codes"); the
  notice must never participate in them.
- **Two independent 24h throttles.** `last_check` gates the **network** (one
  GET/24h); `last_notified` gates the **notice** (one line/24h). They are
  separate so that, e.g., a `--quiet` run can warm the cache (advancing
  `last_check`) without consuming the notice budget, and a run that fetches a
  new version still throttles the notice to once a day. (Their interaction
  under `--quiet`/`--json` is resolved by OQ-4: those flags suppress only the
  notice and still warm the cache.)
- **Stdlib numeric tuple-compare (no `packaging` dep), fail-closed.** Compare
  `latest_version` to `__version__` with a stdlib-only numeric tuple-compare on
  the dot-split release segments (no `packaging` dependency — the zero-dep
  wheel holds). A pre-release or local-version running build (`0.0.0+local`),
  and any unparseable version on either side, fails **closed** (no notice);
  only a strictly-greater released version notifies. (The exact routine is
  resolved by OQ-3 — see Decisions › "Resolved questions".)
- **Lifecycle stays `draft` (M14/M15/M18/M19 precedent).** A milestone flips to
  `archived` only when physically swept into the archive subtree by a later
  milestone; M21 stays live at root through implementation-complete. The plan
  forbids self-archiving the M21 pair.
- **Resolved questions (OQ-1..OQ-9, BINDING — conductor decisions 2026-06-12).**
  The nine OPEN QUESTIONS are resolved as follows; each takes the recommended
  default the draft was written against, so no Scope, Deliverable, or
  Phase-Checklist text moves:
  - **OQ-1 (where the `main()` hook reads `--quiet` / `--json`) → defensive
    `getattr`, no argparse refactor.** The hook reads the effective quiet/json
    state with `getattr(args, "quiet", False)` / `getattr(args, "json", False)`,
    covering every verb that carries the per-verb flag without promoting them to
    global flags. If a future milestone makes them global, the hook needs no
    change. (Rejected: promoting `--quiet`/`--json` to global flags now — a
    larger, orthogonal surface change touching every verb's help + tests.)
  - **OQ-2 (network timeout) → 1.0 second** connect+read timeout. The check is
    best-effort and fail-silent, so a miss is harmless (the cache simply isn't
    warmed and the next eligible run retries); 1.0s keeps even the worst-case
    path snappy.
  - **OQ-3 (version comparison, no `packaging` dep) → stdlib numeric
    tuple-compare on dot-split release segments, fail-closed on
    pre-release/local/unparseable versions.** Compare `latest_version` to
    `__version__` with a small `tuple(int(x) for x in ver.split(".")[...])`
    compare over docs-cli's `MAJOR.MINOR.PATCH` scheme, guarded so any
    unparseable / pre-release / local version on **either** side fails closed
    (no notice) — a `0.0.0+local` running build never nudges. (Rejected:
    vendoring a PEP 440 parser — overkill for a 3-segment scheme; adding
    `packaging` — breaks the zero-dep wheel.)
  - **OQ-4 (do `--quiet` / `--json` still warm the cache?) → YES — they
    suppress ONLY the notice and still run the cache-warming check.** `--quiet`
    and `--json` advance `last_check` / `latest_version` so a later
    human-facing run notifies without waiting another 24h. This differs from
    `CI` / `DOCS_CLI_NO_UPDATE_CHECK` / `DO_NOT_TRACK` (and any future config
    opt-out), which skip the network **entirely** (those are "do not touch the
    network" signals; `--quiet`/`--json` are "do not print" signals). The
    headline D3 sub-contract.
  - **OQ-5 + OQ-5a (config opt-out location + whether to ship it) → DEFER the
    user-level config file; env vars + CI detection suffice for v1.7.0; never
    `.docs.toml`.** The two env vars (`DOCS_CLI_NO_UPDATE_CHECK`,
    `DO_NOT_TRACK`) plus the `CI` skip cover every realistic per-user opt-out;
    a new user-level config file (path resolution, schema, precedence, tests)
    is a meaningfully larger surface for marginal benefit, so it is deferred.
    When a future milestone adds it, the location is settled here and need not
    be re-litigated: a **user-level** config at
    `${XDG_CONFIG_HOME:-~/.config}/docs-cli/config.toml` with `[update_check]
    enabled = false` (XDG-consistent with the cache path), **never**
    `.docs.toml` (which is per-tree, while the check is per-user). M21's D3 +
    D7 + the spec sections drop the live config-opt-out row and keep only the
    env-var + CI matrix; the deferred config opt-out is recorded as future
    work, not a v1.7.0 surface.
  - **OQ-6 (ship the optional offline skill-drift notice D5?) → YES, ships IN
    M21.** It is zero-network, zero-new-risk, reuses the same
    suppressed/throttled STDERR channel, and directly catches the motivating
    2026-06-12 host drift. It is gated by the same suppression matrix + its own
    third throttle key (`last_skill_drift_notified`), and every ambiguous
    install state (absent dir, unreadable, partially-installed, symlinked, a
    *newer* host skill than the bundled one) falls **silent**.
  - **OQ-7 (dedicated `src/docs_cli/update_check.py` module vs inline in
    `cli.py`) → ACCEPTED — dedicated module, with a Step-1 pressure-test
    flag.** The update-check is a cohesive, independently-testable unit (cache
    I/O, network hook, compare, suppression, formatter) with a clean seam;
    `main()` calls one entry function. **Flagged for the Step-1 planning
    agent:** pressure-test the dedicated module against the repo's single-file
    `cli.py` convention before Phase 5 commits to it, and confirm
    `test_packaging.py`'s B3 wheel-contents assertions tolerate the new module
    either way (the bundled-wheel packaging already ships the whole `docs_cli`
    package, so no packaging change is expected — but verify B3 does not pin an
    exact module list). (Rejected: inline in `cli.py` — buries the network seam
    in the largest file.)
  - **OQ-8 (is Phase 9 genuinely online?) → ONE real read-only PyPI probe
    OUTSIDE the pytest suite, on a throwaway cache; pytest stays 100%
    offline.** Phase 9 exercises the real `urllib` GET once against the live
    `https://pypi.org/pypi/docs-cli/json` endpoint on a throwaway cache dir
    (read-only probe), plus an offline end-to-end dogfood of the
    notice/throttle/suppression on the editable `docs 1.7.0`. The `pytest`
    suite makes **no** real network call (D6 invariant preserved).
  - **OQ-9 (rolled-forward follow-on fold-ins) → fold in NONE.** The M20
    workflow-skill / bundled-skill **drift lint** is *related in spirit* to
    D5's skill-drift *notice* but is a different artifact (a repo-side CI lint
    vs a runtime user notice) — it stays a separate follow-on, not folded into
    M21. The other rolled-forward candidates (`touch --check --json`; the repo
    adopting `[check] stale_days`) are unrelated to update-check and likewise
    not folded. M21 is the runtime notice only.

## Testing / Quality Gate

The standard tree-wide gate plus the new behaviour tests, **all offline**:

```sh
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
.venv/bin/docs check docs/
.venv/bin/docs index --root docs/ --dry-run
.venv/bin/docs --version            # must print `docs 1.7.0` after Phase 7 + reinstall
```

Test invariants (D6): the injected checker is the default test seam — **no
test performs a real network call**. Pin: no network when the cache is fresh
(< 24h `last_check`); the check throttle (24h) and the notify throttle (24h)
**independently**; every suppression path (`--quiet`, `--json`, `CI`,
`DOCS_CLI_NO_UPDATE_CHECK`, `DO_NOT_TRACK` — the config opt-out is DEFERRED,
OQ-5/5a); exit codes
**unchanged on every verb including failing ones**; a malformed/corrupt cache
handled silently (no traceback, behaviour byte-identical); the notice format
(both actions named, STDERR, ≤ once/24h); and `--json` stdout stays
**byte-clean**. The one genuinely-online exercise (Phase 9, OQ-8) runs outside
the unit suite against the live PyPI endpoint on a throwaway cache, never in
`pytest`.

## Success Criteria

M21 is complete when:

- [ ] A newer PyPI version produces **one** STDERR line naming both actions
      (`pip install -U docs-cli`, then `docs install-skill --force`), at most
      once per 24h; stdout (incl. `--json`) is byte-unchanged and the exit code
      is byte-unchanged vs the same invocation today.
- [ ] At most one network attempt per 24h (cache-gated); offline / timeout /
      non-200 / malformed-JSON / corrupt-cache all degrade to byte-identical
      behaviour + exit code, no traceback.
- [ ] Every suppression path silences the notice; `CI` + `DOCS_CLI_NO_UPDATE_CHECK`
      + `DO_NOT_TRACK` also skip the network call (the config opt-out is
      DEFERRED out of v1.7.0 — OQ-5/5a); `--json` stdout stays byte-clean.
- [ ] The notice shows on **non-TTY** (the deliberate TTY inversion), verified
      by a piped-stderr test.
- [ ] The offline skill-drift notice (D5 — IN, OQ-6) fires when the installed
      skill differs from the bundled skill and is silent when in sync / the
      install dir is absent or ambiguous — zero network.
- [ ] The suite is fully offline (no real network call); the checker is
      injectable/mockable.
- [ ] `pyproject.toml` + packaging A3/B1/B2/C2 pins at `1.7.0`; a
      `## 1.7.0 — UNRELEASED` CHANGELOG section authored; `docs --version` →
      `docs 1.7.0`. NO publish, NO tag, NO GitHub release (a later milestone
      publishes).
- [ ] `cli.md` / `convention.md` document the feature; bundled refs
      byte-identical (`test_skill_refs` GREEN); INDEX + frozen snapshot in
      lockstep.
- [ ] Full suite GREEN (540 + new); quality gate clean tree-wide.

## OPEN QUESTIONS

**None outstanding.** All nine (OQ-1–OQ-9) are RESOLVED — conductor decisions
2026-06-12, each per the recommended default — and recorded in Decisions ›
"Resolved questions (OQ-1..OQ-9, BINDING)" above: OQ-1 (`main()` quiet/json
read) → defensive `getattr`, no argparse refactor; OQ-2 (network timeout) →
1.0s; OQ-3 (version compare, no `packaging` dep) → stdlib numeric tuple-compare
on dot-split release segments, fail-closed on pre-release/local/unparseable;
OQ-4 (do `--quiet`/`--json` warm the cache?) → YES, they suppress only the
notice and still run the check; OQ-5 + 5a (config opt-out) → DEFER the
user-level config file (env vars + CI suffice for v1.7.0), never `.docs.toml`,
location settled for a future milestone; OQ-6 (ship the offline skill-drift
notice D5?) → YES, ships IN M21 with its own third throttle key; OQ-7
(dedicated `update_check.py` module) → ACCEPTED, with a Step-1 pressure-test
flag against the single-file convention + the B3 wheel-contents test; OQ-8
(Phase 9 online?) → one real read-only PyPI probe OUTSIDE pytest on a throwaway
cache, suite stays 100% offline; OQ-9 (rolled-forward fold-ins) → fold NONE
(the M20 workflow-skill-lint candidate stays a separate follow-on). The
analysis below is retained as the historical record of the forks and why each
was decided.

Genuine scope/contract forks for the operator/conductor. Each: question, why
it matters, recommended answer. (The draft is written against the recommended
default for each, so resolving each per its recommendation moves no
Scope/Deliverable/Phase text.)

- **OQ-1 — Where does the `main()` hook read `--quiet` / `--json` from?**
  *Why it matters:* `--quiet` and `--json` are **per-verb** argparse flags
  today, not global — not every parsed namespace carries `args.quiet` /
  `args.json`. The notice hook in `main()` must read the *effective* quiet/json
  state to honour D3, so it needs a uniform way to detect them across verbs.
  *Recommendation:* read them defensively with `getattr(args, "quiet", False)`
  / `getattr(args, "json", False)` in the hook (no argparse refactor); this is
  the smallest change and covers every verb that has the flag. If a future
  milestone promotes them to global flags, the hook needs no change. (Rejected:
  promoting `--quiet`/`--json` to global flags now — a larger, orthogonal
  surface change that would touch every verb's help and tests.)
- **OQ-2 — Network timeout value.** *Why it matters:* too long adds latency to
  the once-a-day network path on a slow/blocked network; too short produces
  spurious misses. *Recommendation:* **1.0 second** connect+read timeout. The
  check is best-effort and fail-silent, so a miss is harmless (the cache simply
  isn't warmed and the next eligible run retries); 1.0s keeps even the
  worst-case path snappy. (Surfaced because it is a tunable the operator may
  have a preference on; alternatives 0.5s / 2.0s are all defensible.)
- **OQ-3 — Version comparison routine (no `packaging` dep).** *Why it matters:*
  the zero-dependency wheel forbids importing `packaging.version`. A naive
  string compare is wrong (`1.10.0` < `1.9.0` lexically); we need PEP 440-ish
  ordering with stdlib only, and must NOT nudge when running a pre-release or
  `0.0.0+local`. *Recommendation:* a small stdlib tuple-compare on the
  dot-split numeric release segments (`tuple(int(x) for x in
  ver.split(".")[...])`), guarded so any unparseable / pre-release / local
  version on **either** side fails closed (no notice). This covers docs-cli's
  simple `MAJOR.MINOR.PATCH` scheme without a dependency. (Rejected: vendoring
  a PEP 440 parser — overkill for a 3-segment scheme; adding `packaging` —
  breaks the zero-dep wheel.)
- **OQ-4 — Do `--quiet` / `--json` still warm the cache (run the check) while
  suppressing the notice?** *Why it matters:* if `--quiet`/`--json` skip the
  network too, an agent that *always* runs `--json` would never learn of an
  update — defeating the agent-first purpose. If they warm the cache, the next
  non-`--json` run can notify immediately. *Recommendation:* **`--quiet` and
  `--json` suppress only the NOTICE, not the check** — they still warm the
  cache (advance `last_check` / `latest_version`) so a later human-facing run
  notifies without waiting another 24h. This differs from CI / the env vars /
  the config opt-out, which skip the check **entirely** (those are "do not
  touch the network at all" signals; `--quiet`/`--json` are "do not print"
  signals). Flag prominently — this is the headline D3 sub-contract.
- **OQ-5 — Config opt-out location: user-level config vs `.docs.toml`.**
  *Why it matters:* `.docs.toml` is **per-tree**, but the update check is
  **per-user** (the cache lives in `~/.cache`, the CLI is installed per-user).
  A `.docs.toml` opt-out would only silence the notice inside that one tree and
  would be wrong/absent when `docs` runs outside any tree. *Recommendation:* a
  **user-level config** at `${XDG_CONFIG_HOME:-~/.config}/docs-cli/config.toml`
  with `[update_check] enabled = false` (XDG-consistent with the cache path),
  NOT `.docs.toml`. The env vars (`DOCS_CLI_NO_UPDATE_CHECK`, `DO_NOT_TRACK`)
  are the primary per-user kill switches and may be sufficient on their own —
  so a sub-fork is **OQ-5a: ship the config opt-out at all in M21, or rely on
  the two env vars and defer the config file?** Recommended: **defer the config
  file**; the two env vars + CI cover every realistic opt-out, and a new
  user-level config file is a meaningfully larger surface (path resolution,
  schema, precedence, tests) for marginal benefit. If the operator wants
  belt-and-suspenders, adopt the user-level TOML above — **never** `.docs.toml`.
- **OQ-6 — Ship the optional offline skill-drift notice (D5) in M21?**
  *Why it matters:* it is genuinely independent of the network check (zero
  network, different signal) and catches the exact host drift found 2026-06-12,
  but it is a second notice with its own edge cases (install dir absent /
  partially-installed / symlinked / a *newer* host skill than the bundled one).
  *Recommendation:* **YES, ship it (recommend IN)** — it is cheap, zero-risk
  (no network), reuses the same suppressed/throttled STDERR channel, and
  directly addresses the motivating miss. Gate it behind the same suppression
  matrix + a third throttle key (`last_skill_drift_notified`), and make every
  ambiguous install state (absent dir, unreadable, newer-than-bundled) fall
  **silent**. (If the operator prefers a tighter M21, defer D5 to a follow-on
  and keep M21 to the network check only — the two are cleanly separable.)
- **OQ-7 — New `src/docs_cli/update_check.py` module vs inline in `cli.py`.**
  *Why it matters:* `cli.py` is already ~5200 lines; the update-check is a
  cohesive, independently-testable unit (cache I/O, network hook, compare,
  suppression, formatter) with a clean seam. *Recommendation:* a **dedicated
  `src/docs_cli/update_check.py` module** — keeps the network surface, the
  cache I/O, and the mock seam in one isolated place, and makes the
  offline-test boundary obvious. `main()` calls one entry function. (The
  bundled-wheel packaging already ships the whole `docs_cli` package, so a new
  module needs no packaging change — but confirm `test_packaging.py`'s
  wheel-contents assertions (B3) don't pin an exact module list. Rejected:
  inline in `cli.py` — buries the network seam in the largest file.)
- **OQ-8 — Is Phase 9 genuinely online, or offline like every prior
  milestone?** *Why it matters:* every milestone to date mapped Phase 9 to
  offline dogfooding (no network surface existed). M21 has a real online
  surface for the first time, but the project's "suite stays fully offline"
  invariant is sacred. *Recommendation:* **Phase 9 exercises the real network
  ONCE, outside the unit suite** — a manual read-only probe against the live
  `https://pypi.org/pypi/docs-cli/json` on a throwaway cache dir, plus an
  offline end-to-end dogfood of the notice/throttle/suppression on the editable
  `docs 1.7.0`. The `pytest` suite stays 100% offline (D6). If the operator
  wants zero real network even in Phase 9, substitute a localhost stub server
  (stdlib `http.server`) for the probe. (This narrows "how do we online-test
  the first network feature without breaking the offline-suite invariant.")
- **OQ-9 — Rolled-forward follow-on fold-ins (default: NONE).** *Why it
  matters:* status.md lists v1.7+ candidates — the **workflow-skill /
  bundled-skill drift lint** (an in-repo lint diffing workflow-skill
  prescriptions against `references/`), plus the M19/M20 rolled-forward
  candidates (`touch --check --json`; the repo adopting `[check] stale_days`).
  *Recommendation:* **fold NONE silently.** The skill-drift **lint** is
  *related in spirit* to D5's skill-drift *notice* but is a different artifact
  (a repo-side CI lint vs a runtime user notice) — keep them separate; M21 is
  the runtime notice only. The other two are unrelated to update-check. If the
  operator judges the drift-lint a natural companion to D5, that is the one
  candidate worth a fold-in conversation — surfaced here, **not** folded.
