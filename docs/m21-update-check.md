# M21 — Update-check notification (PyPI new-version notice)

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-06-29

Related:
- child-of: plan.md
- parent-of: m21-update-check-impl.md
- implements: charter.md
- pairs-with: m21-update-check-impl.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: status.md
- references: m23-agent-aware-install-skill.md

## Overview

- Milestone: M21 (v1.7.0)
- Title: Update-check notification (PyPI new-version notice)
- Surface: docs-cli's **first network surface** — a once-per-24h, fail-silent
  check of PyPI for a newer `docs-cli` release that, when one exists, emits a
  single STDERR line nudging the user/agent to update **the CLI**
  (`pip install -U docs-cli`). The notice never touches stdout, never changes
  an exit code, is suppressed under `--quiet` / `--json` / CI / opt-out
  env+config, and — **deliberately inverting gh's TTY-gated rule** — shows on
  non-TTY too, because the primary consumer is an agent that is itself the
  actor who performs the update. Ships as **v1.7.0** (minor bump — additive
  feature; matches the 1.3→1.6 minor precedent; 1.6.5 was an operator-decreed
  patch exception). Implementation milestone — builds 1.7.0 locally; the PyPI
  publish is a later operator-driven milestone (the M19→M20, M14+M15→M17
  pattern).
- Progress: **Draft (re-scoped 2026-06-29; originally scaffolded
  2026-06-12).** Re-scoped to **CLI-only** this session: the former
  skill-drift notice (D5) is **CUT** and the dual-action nudge collapses to a
  single CLI-update line (see Decisions › "Re-scope to CLI-only"). The skill
  story — install where the agent actually uses it, then nudge a refresh at the
  recorded location — moves to the follow-on **M23 (agent-aware install-skill +
  recorded-dest skill-refresh hint)**. No TDD phase started. Depends on nothing;
  M22 ran ahead of M21 (operator run-order 2026-06-24) and is
  implementation-complete. Stays LIVE at root, lifecycle `draft`, until a later
  milestone sweeps it in (the M14/M15/M18/M19 completed-but-live precedent).
  OPEN QUESTIONS are netted out — **none outstanding** (the re-scope resolves or
  moots all of OQ-1..OQ-9; see Decisions + OPEN QUESTIONS). Phase 1 (Define
  Contract) is next.

### Goal

Today an installed `docs-cli` never tells the operator (or the agent driving
it) that a newer release is on PyPI. The standing refresh flow asks the user to
`pip install -U docs-cli`, and nothing surfaces that it is due. M21 makes
`docs-cli` self-announce the **CLI** update.

On any invocation, **at most once per 24h** and **fail-silent always**, the CLI
consults PyPI for the latest `docs-cli` version, compares it against the running
version (the `importlib.metadata` SoT from M12), and — when newer — prints
**one** STDERR line nudging `pip install -U docs-cli`. The check is gated by a
per-user state cache (one network attempt per 24h) and a separate per-user
notify throttle (one notice per 24h), so it never spams and never adds latency
or noise to the common case. Offline, timeout, HTTP error, or a corrupt cache
all degrade to **byte-identical behaviour and exit code** vs today — the notice
simply does not appear.

The primary consumer is an **agent**, and the agent is the actor who can
*perform* the update (run `pip install -U docs-cli`). That is why M21
deliberately inverts gh's TTY-gated convention: the notice shows on non-TTY too.
The suppression matrix (`--quiet`, `--json`, CI, two disable env vars) keeps it
out of machine-readable streams, scripts, and CI logs.

**Why CLI-only (the skill half moved to M23).** An earlier draft of M21 also
named a second action — `docs install-skill --force` — and shipped a
zero-network skill-drift notice (D5) that compared the host's installed skill
against the CLI's own bundled skill. A planning pass (2026-06-29) found this
contradicts two project principles: docs-cli must **not inspect or manage the
user's installed skills**, and must **not assume Claude Code**. docs-cli ships
exactly one skill (the Claude-Code `SKILL.md` shape); there is no per-agent
skill format, so "which agent" is the wrong axis — "which directory" (the
`install-skill --dest`) is the honest one. The real fix for "refresh the skill
where the user actually uses it" is making `install-skill` agent-aware and
*recording* the chosen dest so a future notice can replay it — a larger,
separate surface. That work is the follow-on **M23**; M21 is the runtime CLI
notice only. The 2026-06-12 host skill-drift miss (a stale `--body-from`
reference caught only at the M20 publish-closeout sweep) is therefore addressed
by **M23** (install-where-you-use-it + recorded-path refresh), **not** by
runtime inspection in M21.

### Requirements

**Functional.**

- **Update check (D1).** GET `https://pypi.org/pypi/docs-cli/json`, parse
  `info.version`, compare against `__version__` (the M12 `importlib.metadata`
  SoT). **At most one network attempt per 24h**, gated by a per-user state
  cache. **Stdlib `urllib` only** (the zero-dependency wheel is preserved —
  no `requests`). **Short timeout** (1.0s — OQ-2). **Fail-silent always**:
  offline / DNS failure / timeout / non-200 / malformed JSON / unparseable
  version → no notice, no traceback, exit code and all streams byte-identical
  to today.
- **State cache (D1).** `${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json`
  with **exactly three keys** — `last_check` (ISO-8601 UTC timestamp),
  `latest_version` (last seen PyPI version), `last_notified` (ISO-8601 UTC
  timestamp of the last emitted notice). (The former `last_skill_drift_notified`
  key is **dropped** with the D5 cut — DECISION, 2026-06-29.) Created on first
  successful check; read on every invocation to gate the network call and the
  notice. A missing / unreadable / malformed cache is treated as "no data" and
  silently rewritten — never fatal.
- **Notification (D2).** When `latest_version > __version__` (stdlib numeric
  tuple-compare, fail-closed on pre-release/local/unparseable — OQ-3), emit
  **one** line on **STDERR**, at most once per 24h (the separate
  `last_notified` throttle). **Reference wording (CLI-only):**
  `docs: update available <current> -> <latest> — run: pip install -U docs-cli`
  (em-dash `—`, ASCII `->`; concrete example
  `docs: update available 1.7.0 -> 1.7.1 — run: pip install -U docs-cli`). The
  byte-exact string is pinned in `cli.md` during Phase 1. **NEVER** on stdout;
  **NEVER** affects the exit code (exit codes are load-bearing — the M19
  `touch --check` fold proves the project treats them as a contract).
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
- **~~D5 — Offline skill-drift notice.~~ CUT (2026-06-29).** The former
  zero-network skill-drift compare (installed skill vs bundled skill →
  `docs install-skill --force` nudge) is **removed**, not deferred-as-D5: it
  required content-inspection of the user's installed skill and assumed Claude
  Code, both of which violate project principles. The skill-refresh nudge is
  rebuilt — agent-appropriate and pointed at a *recorded* dest — in the
  follow-on **M23**, riding M21's same suppression/throttle channel. (OQ-6's
  earlier "ship D5" resolution is **REVERSED** — see Decisions.)

**Non-functional.**

- **Zero-dependency wheel preserved** — stdlib `urllib` only; no new runtime
  dependency in `pyproject.toml`.
- **No measurable latency in the common case** — the cache read short-circuits
  before any network work; the 24h gate means the network is touched at most
  once per day; the timeout bounds the rare network path.
- **Suite stays fully offline** — the checker is **injectable / mockable**;
  no test makes a real network call (D6). The default test posture is
  network-disabled, and the dispatch hook is **hard-disabled in the suite** via
  `DOCS_CLI_NO_UPDATE_CHECK=1` set in `tests/conftest.py` (resolved decision)
  so the existing subprocess suites never reach PyPI.
- **Surface parity (plan.md "Ongoing conventions")** — any new `--help`
  strings, the bundled skill (`SKILL.md` + `references/`), and the byte-identical
  `references/{cli,convention}.md` mirrors all land in the same change.

### Deliverables

- [ ] **D1 — Update check + state cache.** A mockable checker queries
      `https://pypi.org/pypi/docs-cli/json` (stdlib `urllib`, 1.0s timeout),
      compares `info.version` to `__version__`, and persists the three-key
      `{last_check, latest_version, last_notified}` (ISO-8601 UTC) to
      `${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json`. One network
      attempt per 24h (cache-gated). Fail-silent on every error path
      (offline / timeout / non-200 / malformed JSON / corrupt cache) →
      byte-identical behaviour + exit code. Pinned by Phase-2 tests.
- [ ] **D2 — Notification.** One STDERR line, ≤ once per 24h (separate
      `last_notified` throttle), in the **CLI-only** reference wording
      (`pip install -U docs-cli`). Never on stdout; never alters the exit code.
      Pinned by Phase-2 tests (byte-exact notice text + stream +
      exit-code-unchanged on success AND failure verbs).
- [ ] **D3 — Suppression matrix.** `--quiet`, `--json`, `CI`,
      `DOCS_CLI_NO_UPDATE_CHECK`, and `DO_NOT_TRACK` each suppress the notice;
      `CI` + the two env vars also skip the network call (the user-level config
      opt-out is DEFERRED out of v1.7.0 — OQ-5/5a). Pinned by one Phase-2 test
      per path + a `--json` stdout-byte-clean lock.
- [ ] **D4 — TTY inversion.** Notice shows on non-TTY (recorded as a binding
      Decision with precedent). Pinned by a non-TTY (piped-stderr) test that
      still sees the notice.
- [ ] **~~D5 — Offline skill-drift notice.~~ CUT (2026-06-29)** — moved to
      M23 (agent-aware install-skill + recorded-dest skill-refresh hint). No
      drift compare, no `last_skill_drift_notified` key, no drift tests in M21.
- [ ] **D6 — Offline test harness.** The checker is injectable/mockable; the
      suite makes **no** real network call (dispatch hook hard-disabled in
      `tests/conftest.py` via `DOCS_CLI_NO_UPDATE_CHECK=1`). Tests pin: no
      network when cache fresh; both 24h throttles (check + notify,
      independently); every suppression path; exit codes unchanged on every
      verb incl. failures; malformed/corrupt cache handled silently; the
      byte-exact CLI-only notice format; and that `--json` stdout stays
      byte-clean.
- [ ] **D7 — Docs / version plumbing.** Version → **1.7.0**
      (`pyproject.toml` + the `test_packaging.py` A3/B1/B2/C2 version pins, the
      A3-fast / B1-B2-C2-slow split per the M19 precedent); **APPEND** to the
      existing `## 1.7.0 — UNRELEASED` CHANGELOG section (opened by M22 — do
      NOT create a second 1.7.0 header); `cli.md` (a new §update-check /
      §Output-conventions note + the suppression-env table — env vars + `CI`
      only; the config opt-out is DEFERRED, OQ-5/5a) contract sections;
      bundled-skill surface parity; `references/{cli,convention}.md`
      byte-identical.
- [ ] **Surface-parity gate (Phase 10, plan.md "Ongoing conventions").** Run
      `docs --help` / any changed verb `--help`; reconcile against the
      CHANGELOG surface; confirm the bundled skill documents the new env vars +
      notice; grep for stale wording. INDEX + frozen snapshot
      (`tests/fixtures/expected/docs-INDEX.md`) in lockstep throughout.
- [ ] **Full suite GREEN** (current 543 + the new M21 tests); ruff / ruff
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
  on every namespace — see OQ-1; the hook reads them defensively).
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
  The CHANGELOG already carries a `## 1.7.0 — UNRELEASED` section (opened by
  M22, a docs-only milestone that ran ahead of M21) — Phase 7 **appends** to
  it.

## TDD Implementation Plan

Phases follow the canonical 10-phase TDD methodology. The re-scope to CLI-only
(D5 cut) is folded into every phase below; refine only as implementation
surfaces detail.

### Phase 1: Define Contract
- Objective: pin the M21 surface in the specs (no code, no tests) — `cli.md`
  §update-check (the **byte-exact CLI-only** notice wording, STDERR-only,
  exit-code-untouched, the per-user three-key cache schema + path, the 24h
  check + notify throttles, the suppression matrix incl. the env-var table, the
  TTY-inversion), `cli.md` §Output-conventions note; **no skill-drift contract
  section** (D5 cut); the user-level config opt-out is DEFERRED out of v1.7.0
  (OQ-5/5a — no `convention.md` opt-out row this milestone); resync the bundled
  refs byte-identical; record the CHANGELOG decision (**append** to the existing
  `## 1.7.0 — UNRELEASED`).
- Files: `docs/cli.md`, `docs/convention.md`, `src/docs_cli/skill/references/{cli,convention}.md`, `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md`.
- Exit: every Phase-2 assertion string present verbatim in the specs;
  `test_skill_refs` GREEN; `docs check docs/` exit 0; INDEX == snapshot.

### Phase 2: Write Tests (RED)
- Objective: express the contract as failing tests, split by layer (the M19
  no-new-file-where-possible precedent), all behind the mock seam (no real
  network). Cover: fresh-cache-no-network; check-throttle (24h); notify-
  throttle (24h, independent); newer→notice / same→silent / older→silent;
  byte-exact CLI-only notice text + STDERR stream; exit-code unchanged on a
  success verb AND a failing verb; each suppression path; `--json` stdout
  byte-clean; corrupt cache silent; offline/timeout/non-200/malformed-JSON each
  silent; non-TTY still sees notice; A3 version pin 1.7.0. **No skill-drift
  tests** (D5 cut). Guard the not-yet-existing module with
  `try/except ModuleNotFoundError → uc = None` so the RED baseline collects
  cleanly.
- Files: a new `tests/test_update_check.py` (the unit + injectable-checker
  surface) + targeted additions to existing CLI suites for the dispatch-level
  notice; `tests/conftest.py` (set `DOCS_CLI_NO_UPDATE_CHECK=1` for the suite);
  `tests/test_packaging.py` A3 flip.
- Exit: tests import + collect cleanly; intended-RED vs GREEN-at-baseline
  classified for Phase 4.

### Phase 3: Create Data/Fixtures
- Objective: provide the test data — a fake PyPI JSON payload builder and cache
  files in each state (fresh / stale / missing / corrupt) — preferring inline
  `tmp_path` builders with today-relative UTC timestamps (the M19 "committed
  dates rot" decision). **No fake skill-pair fixture** (D5 cut).
- Files: inline builders in `tests/test_update_check.py`; no committed dated
  fixtures; the byte-frozen `docs-INDEX.md` snapshot stays the only committed
  fixture, in lockstep.
- Exit: every Phase-2 test has date-independent data; no rotting fixture.

### Phase 4: Run Tests (RED Baseline)
- Objective: confirm every intended-RED test fails for its classified reason
  (no tracebacks / collection errors / argparse-exit-2 surprises; the
  module-import guard keeps collection clean); classify RED vs GREEN-at-baseline;
  capture the baseline count verbatim.
- Files: none (run only).
- Exit: the RED set matches the plan; GREEN-at-baseline locks pass; the
  untouched pre-existing 543 stay GREEN.

### Phase 5: Update Base Interfaces
- Objective: declare the seams with minimal logic — the cache dataclass +
  read/write helpers (XDG-aware path, ISO-8601 UTC timestamps), the injectable
  `fetch_latest_version` hook (default = real `urllib` GET; tests inject a
  fake), the stdlib tuple-compare helper (fail-closed on
  pre-release/local/unparseable — OQ-3), the env-var suppression predicate, and
  the `main()` hook point (interface declared; full wiring may land Phase 6 per
  the honest split).
- Files: a dedicated `src/docs_cli/update_check.py` module (OQ-7 ACCEPTED — the
  B3 wheel-contents test (`test_packaging.py`, ~line 215) makes only
  positive-presence assertions and packages the whole `src/docs_cli` package, so
  the new module needs no packaging change — resolved decision);
  `src/docs_cli/cli.py` for the `main()` hook point.
- Exit: type checks pass; tests can import the seam; behaviour may stay
  unchanged this phase.

### Phase 6: Implement Offline/Core Path
- Objective: implement the offline/core path — cache read/write + both 24h
  throttles + the suppression matrix + the stdlib fail-closed tuple-compare
  (OQ-3) + the CLI-only notice formatter + the `main()` STDERR emission with
  exit-code pass-through. **No D5 skill-drift compare** (cut). The **network**
  call stays behind the injected hook (its real-`urllib` body is the Phase-9
  online surface). All offline RED → GREEN.
- Files: `src/docs_cli/update_check.py` (the OQ-7 module) + `src/docs_cli/cli.py`
  (the `main()` hook).
- Exit: offline target tests GREEN; no regression in the 543.

### Phase 7: Update Tool/Wrapper Layer
- Objective: `pyproject.toml` `version` → `1.7.0`; the `test_packaging.py`
  A3/B1/B2/C2 version pins flipped in lockstep (A3 fast; B1/B2/C2 slow,
  build-gated — the M19 split); **APPEND** to the existing
  `## 1.7.0 — UNRELEASED` CHANGELOG section (Added: update-check notice + the
  disable env vars) — do NOT add a second 1.7.0 header (M22 already opened it);
  bundled `cli.md`/`convention.md` resynced byte-identical; the new
  `--help` / env-var wording reconciled into the bundled `SKILL.md`.
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

- [x] Phase 1 — Define Contract
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

- **Re-scope to CLI-only — D5 CUT; the notice nudges only the CLI
  (2026-06-29, BINDING).** A planning pass + the operator pressure-tested the
  former D5 ("offline skill-drift notice") and found it contradicts core
  principles: docs-cli must **not inspect or manage the user's installed
  skills**, and must **not assume Claude Code**. Findings: (1) docs-cli ships
  exactly ONE skill (the Claude-Code `SKILL.md` shape) — there is no per-agent
  skill format, so "which agent" is the wrong axis; "which directory"
  (`install-skill --dest`) is the honest one, and it already exists. (2) D5's
  whole premise is **content-inspection** of the installed skill → cut. (3) The
  original notice named both `pip install -U docs-cli` AND
  `docs install-skill --force`; the second half assumes Claude Code and assumes
  the user even has the skill installed → the notice becomes **CLI-only**. (4)
  The real fix for "install where the user is using it" is making
  `install-skill` **agent-aware** + **recording** the chosen dest so the notice
  can later replay it — a separate, larger surface → the follow-on **M23**.
  Consequences folded here: D5 is removed (not deferred-as-D5); the cache loses
  `last_skill_drift_notified` (DECISION 3 — three keys only); the notice uses
  the CLI-only wording (DECISION 2); **OQ-6's earlier "ship D5" resolution is
  REVERSED**. The skill-refresh nudge is rebuilt in M23, pointed at the
  *recorded* dest, riding this same suppression/throttle channel.
- **Notice wording (CLI-only) — DECISION (2026-06-29).**
  `docs: update available <current> -> <latest> — run: pip install -U docs-cli`
  (em-dash `—`, ASCII `->`; STDERR only; never alters the exit code). The
  byte-exact string is pinned in `cli.md` at Phase 1 and asserted verbatim by
  Phase-2 tests. (Supersedes the earlier dual-action wording that also named
  `docs install-skill --force`.)
- **Cache schema — three keys (DECISION, 2026-06-29).**
  `{last_check, latest_version, last_notified}`, all timestamps ISO-8601 **UTC**
  (`datetime.now(timezone.utc)`). The former `last_skill_drift_notified` key is
  dropped with the D5 cut.
- **Ships as v1.7.0 (minor bump).** The update-check notice is an additive,
  backward-compatible feature: no flag removed, no default changed, no exit
  code altered, and trees/users who set a disable env var see byte-identical
  behaviour to 1.6.5. Minor is the right SemVer bucket and matches the 1.3.0 →
  1.4.0 → 1.5.0 → 1.6.0 minor cadence; 1.6.5 was the operator-decreed **patch**
  exception (M19), not the rule. `pyproject.toml` `version` + the
  `test_packaging.py` A3/B1/B2/C2 pins bump to `1.7.0` at Phase 7;
  `importlib.metadata` stays the SoT (M12), so `docs --version` reads `1.7.0`
  after an editable reinstall. Builds locally; the PyPI publish is a later
  operator-driven milestone (the M19→M20, M14+M15→M17 cadence).
- **CHANGELOG: APPEND to the existing `## 1.7.0 — UNRELEASED` section.** M22 (a
  docs-only milestone that ran ahead of M21) already opened
  `## 1.7.0 — UNRELEASED` with a Documentation entry. M21's Phase 7 **adds an
  `### Added` entry** under that same section — it does **not** create a second
  1.7.0 header. The eventual publish milestone dates the section.
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
  (`pip install -U docs-cli`). Gating on TTY would hide the nudge from the one
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
  notice and still warm the cache.) With D5 cut there is a **single** notice,
  so the old dual-notice ordering question is **moot**.
- **Stdlib numeric tuple-compare (no `packaging` dep), fail-closed.** Compare
  `latest_version` to `__version__` with a stdlib-only numeric tuple-compare on
  the dot-split release segments (no `packaging` dependency — the zero-dep
  wheel holds). A pre-release or local-version running build (`0.0.0+local`),
  and any unparseable version on either side, fails **closed** (no notice);
  only a strictly-greater released version notifies. (The exact routine is
  resolved by OQ-3 — see Decisions › "Resolved questions".)
- **Dedicated `src/docs_cli/update_check.py` module (OQ-7 ACCEPTED, STANDS).**
  The update-check is a cohesive, independently-testable unit (cache I/O,
  network hook, compare, suppression, formatter) with a clean seam; `main()`
  calls one entry function. The B3 wheel-contents test (`test_packaging.py`,
  ~line 215) makes only **positive-presence** assertions and packages the whole
  `src/docs_cli` package, so the new module needs **no packaging change**
  (verified this session). (Rejected: inline in `cli.py` — buries the network
  seam in the largest file.)
- **Suite offline guard (resolved decision).** Phase 2 sets
  `DOCS_CLI_NO_UPDATE_CHECK=1` in `tests/conftest.py` so the dispatch hook
  never lets the existing subprocess suites reach PyPI; the
  `tests/test_update_check.py` unit tests exercise the seam directly via the
  injected `fetch_latest_version` hook. Preserves the offline-suite invariant
  (D6).
- **Lifecycle stays `draft` (M14/M15/M18/M19 precedent).** A milestone flips to
  `archived` only when physically swept into the archive subtree by a later
  milestone; M21 stays live at root through implementation-complete. The plan
  forbids self-archiving the M21 pair.
- **Resolved questions (OQ-1..OQ-9, BINDING — conductor decisions 2026-06-12,
  amended by the 2026-06-29 re-scope).** The nine original OPEN QUESTIONS:
  - **OQ-1 (where the `main()` hook reads `--quiet` / `--json`) → defensive
    `getattr`, no argparse refactor.** The hook reads the effective quiet/json
    state with `getattr(args, "quiet", False)` / `getattr(args, "json", False)`,
    covering every verb that carries the per-verb flag without promoting them to
    global flags. (Rejected: promoting `--quiet`/`--json` to global flags now.)
  - **OQ-2 (network timeout) → 1.0 second** connect+read timeout. The check is
    best-effort and fail-silent, so a miss is harmless; 1.0s keeps even the
    worst-case path snappy.
  - **OQ-3 (version comparison, no `packaging` dep) → stdlib numeric
    tuple-compare on dot-split release segments, fail-closed on
    pre-release/local/unparseable versions.** A `0.0.0+local` running build
    never nudges. (Rejected: vendoring a PEP 440 parser; adding `packaging`.)
  - **OQ-4 (do `--quiet` / `--json` still warm the cache?) → YES — they
    suppress ONLY the notice and still run the cache-warming check.** This
    differs from `CI` / `DOCS_CLI_NO_UPDATE_CHECK` / `DO_NOT_TRACK`, which skip
    the network **entirely**. The headline D3 sub-contract.
  - **OQ-5 + OQ-5a (config opt-out location + whether to ship it) → DEFER the
    user-level config file; env vars + CI detection suffice for v1.7.0; never
    `.docs.toml`.** When a future milestone adds it: a **user-level** config at
    `${XDG_CONFIG_HOME:-~/.config}/docs-cli/config.toml` with `[update_check]
    enabled = false`, **never** `.docs.toml`.
  - **OQ-6 (ship the optional offline skill-drift notice D5?) → REVERSED to NO
    (2026-06-29).** The earlier "ship D5 IN M21" answer is **reversed by the
    re-scope**: D5 is CUT (it inspected the installed skill and assumed Claude
    Code). The skill-refresh story moves to M23. No drift compare, no third
    throttle key, no drift tests in M21.
  - **OQ-7 (dedicated `src/docs_cli/update_check.py` module) → ACCEPTED
    (STANDS).** The B3 wheel-contents test makes only positive-presence
    assertions and ships the whole package, so the new module needs no
    packaging change. (Rejected: inline in `cli.py`.)
  - **OQ-8 (is Phase 9 genuinely online?) → ONE real read-only PyPI probe
    OUTSIDE the pytest suite, on a throwaway cache; pytest stays 100%
    offline.** The `pytest` suite makes **no** real network call (D6 invariant
    preserved).
  - **OQ-9 (rolled-forward follow-on fold-ins) → fold in NONE.** The M20
    workflow-skill / bundled-skill **drift lint** stays a separate follow-on
    (repo-side CI lint, not a runtime notice); the other rolled-forward
    candidates are unrelated to update-check. M21 is the runtime CLI notice
    only.

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
test performs a real network call** (the dispatch hook is hard-disabled in
`tests/conftest.py` via `DOCS_CLI_NO_UPDATE_CHECK=1`). Pin: no network when the
cache is fresh (< 24h `last_check`); the check throttle (24h) and the notify
throttle (24h) **independently**; every suppression path (`--quiet`, `--json`,
`CI`, `DOCS_CLI_NO_UPDATE_CHECK`, `DO_NOT_TRACK` — the config opt-out is
DEFERRED, OQ-5/5a); exit codes **unchanged on every verb including failing
ones**; a malformed/corrupt cache handled silently (no traceback, behaviour
byte-identical); the **byte-exact CLI-only** notice format (single action named,
STDERR, ≤ once/24h); and `--json` stdout stays **byte-clean**. **No
skill-drift tests** (D5 cut). The one genuinely-online exercise (Phase 9,
OQ-8) runs outside the unit suite against the live PyPI endpoint on a throwaway
cache, never in `pytest`.

## Success Criteria

M21 is complete when:

- [ ] A newer PyPI version produces **one** STDERR line in the CLI-only wording
      (`docs: update available <current> -> <latest> — run: pip install -U
      docs-cli`), at most once per 24h; stdout (incl. `--json`) is byte-unchanged
      and the exit code is byte-unchanged vs the same invocation today.
- [ ] At most one network attempt per 24h (cache-gated); offline / timeout /
      non-200 / malformed-JSON / corrupt-cache all degrade to byte-identical
      behaviour + exit code, no traceback.
- [ ] Every suppression path silences the notice; `CI` + `DOCS_CLI_NO_UPDATE_CHECK`
      + `DO_NOT_TRACK` also skip the network call (the config opt-out is
      DEFERRED out of v1.7.0 — OQ-5/5a); `--json` stdout stays byte-clean.
- [ ] The notice shows on **non-TTY** (the deliberate TTY inversion), verified
      by a piped-stderr test.
- [ ] The suite is fully offline (no real network call; dispatch hook
      hard-disabled in `tests/conftest.py`); the checker is injectable/mockable.
- [ ] `pyproject.toml` + packaging A3/B1/B2/C2 pins at `1.7.0`; an `### Added`
      entry **appended** to the existing `## 1.7.0 — UNRELEASED` CHANGELOG
      section (no second 1.7.0 header); `docs --version` → `docs 1.7.0`. NO
      publish, NO tag, NO GitHub release (a later milestone publishes).
- [ ] `cli.md` / `convention.md` document the feature; bundled refs
      byte-identical (`test_skill_refs` GREEN); INDEX + frozen snapshot in
      lockstep.
- [ ] Full suite GREEN (543 + new); quality gate clean tree-wide.

## OPEN QUESTIONS

**None outstanding.** The 2026-06-29 re-scope to CLI-only resolves or moots
everything:

- The original OQ-1..OQ-9 are all RESOLVED (conductor decisions 2026-06-12,
  each per the recommended default) and recorded in Decisions ›
  "Resolved questions" — with one amendment: **OQ-6 (ship D5) is REVERSED to
  NO** by the re-scope (D5 CUT; the skill story moved to M23).
- The earlier dual-notice ordering question is **moot** — D5's cut leaves a
  **single** notice.
- The surviving planning-agent findings are folded in as resolved decisions:
  the dedicated `update_check.py` module stands (OQ-7; B3 tolerates it); the
  suite offline guard sets `DOCS_CLI_NO_UPDATE_CHECK=1` in `tests/conftest.py`;
  the not-yet-existing-module import guard (`try/except ModuleNotFoundError`)
  covers the Phase-2/4 RED baseline; cache timestamps are ISO-8601 UTC; the
  baseline test count is **543** (not 540).

The follow-on **M23 (agent-aware install-skill + recorded-dest skill-refresh
hint)** owns the skill half of the original M21 idea — making `install-skill`
agent-aware via `--dest`, recording the resolved dest, and then extending this
notice's channel with a skill-refresh hint pointed at the recorded location.
M23 carries its own genuine OPEN QUESTIONS (non-TTY default-vs-refuse; the
state-file location; multiple recorded dests; final version number); they are
**not** M21's to decide.
