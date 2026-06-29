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
- Started: 2026-06-12 (scaffolded — milestone-setup); TDD Phases 1–4 run
  2026-06-29.
- Progress: **Phases 1–4 complete (RED baseline, 2026-06-29)** on branch
  `m21/phases-1-4`; re-scoped to CLI-only 2026-06-29. Headline: `docs-cli`
  checks PyPI for a newer release and, once
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
  (M19→M20, M14+M15→M17 pattern). Depends on nothing. **Phases 1–4 done (RED
  baseline: 598 collected, 47 RED / 9 GREEN-at-baseline locks, prior 543 GREEN);
  Phase 5 next.** OPEN QUESTIONS are netted out — **none outstanding** (the
  re-scope resolves or moots OQ-1..OQ-9; OQ-6's "ship D5" is REVERSED). See the
  milestone doc's Decisions.

(Note: doc-lifecycle status is the front-matter `Lifecycle:` field. This
section tracks implementation progress, which is distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Done | 2026-06-29 | `cli.md` §Update check + §Output-conventions note; bundled `cli.md` mirror resynced byte-identical; INDEX + frozen snapshot refrozen (single delta = `cli.md` `Updated:` bump); `convention.md` untouched. 543 GREEN. |
| 2. Write Tests (RED) | Done | 2026-06-29 | New `tests/test_update_check.py` (55 tests: unit seam + in-process dispatch + Q7 spec-lock + inline builders); `conftest.py` offline guard (`DOCS_CLI_NO_UPDATE_CHECK=1`); `test_packaging.py` A3 flipped to 1.7.0. Collects 598; gate clean. |
| 3. Create Data/Fixtures | Done | 2026-06-29 | Inline, date-independent `tmp_path` builders in `tests/test_update_check.py`; no committed dated fixtures (the frozen `docs-INDEX.md` stays the only committed fixture). |
| 4. Run Tests (RED Baseline) | Done | 2026-06-29 | 598 collected; 47 RED (46 update-check + A3 flip), 9 GREEN-at-baseline locks; prior 543 intact (542 + 9 new green = 551 passed). Every RED a clean classified assertion; gate clean tree-wide. |
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

## Conductor triage — Step 1 OQ dispositions (binding)

The conductor triaged ten open questions for Step 1 (Phases 1–4) and
auto-resolved each per the recommended default. Recorded here so the
implementation record is complete:

- **Q1 (cli.md section heading / placement)** → top-level `## Update check`
  inserted between `## Output conventions` and `## Exit codes (summary)`, plus
  one cross-ref bullet in `## Output conventions`.
- **Q2 (convention.md change?)** → **NO.** The cache is per-user
  `XDG_CACHE_HOME` host state; env vars are CLI surface (cli.md); the config
  opt-out is deferred (OQ-5/5a). `convention.md` stays byte-identical; its
  bundled mirror copy is a no-op. Not edited.
- **Q3 (bump cli.md `Updated:` + refreeze snapshot in Phase 1?)** → **YES** —
  bump `2026-06-12` → `2026-06-29`, regenerate INDEX, refreeze the snapshot.
  Single expected snapshot delta this phase.
- **Q4 (notice termination / position)** → one `\n`-terminated line, emitted as
  the command's **last** stderr line. The formatter **returns the line without a
  trailing newline**; the emitter adds the `\n`. The byte-exact dispatch test
  asserts the trailing `\n` on emitted stderr; the formatter unit test asserts
  no trailing newline.
- **Q5 (fail-silent completeness — unwritable cache)** → **ADD** the
  unwritable/uncreatable cache dir-or-file path to the fail-silent enumeration
  in cli.md **and** add the unit test (write swallows `OSError`, no raise).
- **Q6 (`last_notified` advance semantics)** → stated explicitly in cli.md:
  `last_notified` advances **only when a notice is actually emitted**; a
  `--quiet` / `--json` run warms `last_check` but not `last_notified`. Pinned by
  the `--quiet`-warms-cache test.
- **Q7 (spec-content lock test)** → **ADD** one minimal lock asserting
  `docs/cli.md` contains (a) the byte-exact notice template
  `docs: update available <current> -> <latest> — run: pip install -U docs-cli`
  and (b) the three suppression env-var names `DOCS_CLI_NO_UPDATE_CHECK`,
  `DO_NOT_TRACK`, `CI`. `test_skill_refs` transitively locks the bundled mirror.
  Kept minimal (no extra spec-grep tests).
- **Q8 (conftest offline-guard mechanism)** → module-level
  `os.environ["DOCS_CLI_NO_UPDATE_CHECK"] = "1"` in `tests/conftest.py`; new
  dispatch tests opt back in via `monkeypatch.delenv(..., raising=False)`.
- **Q9 (A3-only flip in Phase 2)** → **YES** — Phase 2 flips only `test_a3` to
  expect `1.7.0`. B1/B2/C2 stay `1.6.5` until Phase 7 (the pyproject bump).
- **Q10 (no notice on `--version` / `--help`)** → stated in cli.md (the check
  runs after dispatch returns, so it never runs for `--version` / `-h`). A cheap
  GREEN lock (`docs --version` emits no notice) is optional.

## Phase 1 — Define Contract

**Objective.** Pin the M21 surface in the specs — no code, no tests — so every
Phase-2 assertion string is present verbatim in `cli.md`.

**Files changed.**

- `docs/cli.md` — added a top-level `## Update check` section between
  `## Output conventions` and `## Exit codes (summary)`, containing: the
  byte-exact CLI-only notice template
  (`docs: update available <current> -> <latest> — run: pip install -U docs-cli`,
  em-dash `—`, ASCII `->`) + the concrete `1.7.0 -> 1.7.1` example; STDERR-only,
  last-stderr-line, `\n`-terminated, ≤ once/24h, never stdout, never alters the
  exit code; the one-HTTPS-GET to `https://pypi.org/pypi/docs-cli/json` (stdlib
  `urllib`, 1.0s timeout) compared against `__version__`; the three-key cache
  schema table (`last_check`, `latest_version`, `last_notified`, ISO-8601 UTC)
  at `${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json`; the two
  independent 24h throttles + the `last_notified`-advances-only-on-emit rule;
  the stdlib numeric tuple-compare fail-closed on pre-release / `0.0.0+local` /
  unparseable; the full fail-silent enumeration (incl. the unwritable/
  uncreatable cache path — Q5); the non-TTY inversion + rationale; the
  suppression matrix table (`--quiet` / `--json` warm the cache; `CI` /
  `DOCS_CLI_NO_UPDATE_CHECK` / `DO_NOT_TRACK` skip the network); the
  config-opt-out-deferred note (OQ-5/5a); and the "runs after dispatch returns,
  so never for `--version` / `-h`" statement.
- `docs/cli.md` `## Output conventions` — appended one cross-ref bullet.
- `src/docs_cli/skill/references/cli.md` — resynced byte-identical to
  `docs/cli.md` (surface-parity gate; `test_skill_refs` GREEN).
- `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` — regenerated and
  refrozen after the `cli.md` `Updated:` bump (`2026-06-12` → `2026-06-29`); the
  single delta is that date.

**Not changed (by decision).** `docs/convention.md` and its bundled mirror
(Q2 — NO change); `SKILL.md` (env-var / `--help` reconciliation is Phase 7);
`CHANGELOG.md` (Phase 7 **appends** an `### Added` entry under the existing
`## 1.7.0 — UNRELEASED` header opened by M22 — no second 1.7.0 header).

**Lifecycle commands.** Bumped the date + regenerated INDEX via the docs CLI
(`docs touch docs/cli.md --check --root docs`); confirmed `docs check docs/`
exit 0 and `docs index --root docs/ --dry-run` a byte no-op before commit.

**Test state.** The pre-existing 543 stay GREEN (`test_skill_refs` +
`test_index_output_matches_frozen_snapshot` included). No tests added this
phase (Phase 2).

## Phase 2 — Write Tests (RED)

**Objective.** Express the Phase-1 contract as failing tests, split by layer,
all behind the mock seam (no real network) so the suite stays 100% offline.

**Files changed.**

- `tests/test_update_check.py` (NEW, 55 tests) — guarded import
  (`importlib.import_module("docs_cli.update_check")` → `uc`, `None` until
  Phase 5; `importlib` + `uc: Any` keeps mypy clean before AND after the module
  exists). UNIT tests (each opens `assert uc is not None, "<not-impl>"`):
  `is_newer` (numeric, fail-closed on local / pre-release / unparseable),
  `format_notice` (byte-exact, no trailing `\n`), cache path + I/O (XDG-aware;
  missing / corrupt / malformed → no-data; three-key round-trip with no fourth
  key; parent-dir creation; unwritable → swallow `OSError`), the two 24h
  throttles + their independence, the `fetch_latest_version` hook (monkeypatched
  `urllib`: 200 → version + asserts the PyPI URL & `timeout=1.0`; URLError /
  timeout / HTTPError 500 / malformed body → `None`), and the
  `notice_suppressed` / `network_suppressed` predicates (defensive `getattr`;
  `--quiet`/`--json` warm the cache; `CI`/`DOCS_CLI_NO_UPDATE_CHECK`/
  `DO_NOT_TRACK` skip the network). DISPATCH tests (`cli.main([...])` in-process
  + capsys; `_prep_dispatch` delenvs the suppression vars + points
  `XDG_CACHE_HOME` at tmp; a `_FetchSpy` that lives outside `uc` so call-counts
  hold at the RED baseline): intended-RED notice/cache-effect tests + GREEN-at-
  baseline absence locks.
- `tests/conftest.py` — module-level `os.environ["DOCS_CLI_NO_UPDATE_CHECK"]="1"`
  (D6 offline guard; inert at baseline, inherited by every subprocess child).
- `tests/test_packaging.py` — A3 only: renamed `test_a3_project_version_is_1_6_5`
  → `_1_7_0`, asserting `1.7.0` (RED until the Phase-7 pyproject bump; B1/B2/C2
  stay `1.6.5`).

**Mock seam.** No real network anywhere: the fetch unit tests monkeypatch
`urllib.request.urlopen`; the dispatch tests inject `_FetchSpy` onto
`uc.fetch_latest_version` (a no-op while `uc is None`) and never reach PyPI.

**Quality gate.** Tree-wide clean at the RED baseline — ruff / ruff format
--check / mypy all pass (the guarded `importlib` import + `uc: Any` avoids the
`import-not-found` mypy error the literal `from docs_cli import update_check`
form would raise).

## Phase 3 — Create Data/Fixtures

**Objective.** Provide every Phase-2 test's data as inline, date-independent
`tmp_path` builders — no committed dated fixtures that rot (the M19 "committed
dates rot" decision).

**Files changed.** None beyond the Phase-2 file — by design the builders are
inline in `tests/test_update_check.py`:

- `_fake_pypi_json(version)` → `{"info": {"version": version}}`; `_FetchSpy`
  (callable returning a version or raising) and `_FakeResp` (context-manager
  HTTP response) for the fetch/dispatch seams.
- `_iso_hours_ago(n)` stamps `datetime.now(UTC) - timedelta(hours=n)` (e.g. 1 =
  fresh, 25 = stale) so the 24h throttle data is always relative to "now".
- `_write_dispatch_cache(...)` / `_read_dispatch_cache(...)` seed and read
  `$XDG_CACHE_HOME/docs-cli/update-check.json`; corrupt = `b"{not json"`,
  malformed = JSON missing keys, both written inline. `XDG_CACHE_HOME` is always
  pointed at `tmp_path`.

**Exit.** Every Phase-2 test has date-independent inline data; no real
`~/.cache` or network is touched; the byte-frozen `docs-INDEX.md` (regenerated
in Phase 1) stays the only committed fixture.

## Phase 4 — Run Tests (RED Baseline)

**Objective.** Confirm every intended-RED test fails for its classified reason
(no tracebacks / collection errors / argparse-exit-2 surprises), classify RED vs
GREEN-at-baseline, and capture the baseline count.

**Commands.**

```sh
.venv/bin/python -m pytest tests/ -q          # 47 failed, 551 passed (598 total)
.venv/bin/python -m pytest tests/test_update_check.py -q   # 46 failed, 9 passed
```

**Baseline counts.**

- **598** collected (= prior 543 + 55 new).
- **47 RED**: 46 in `test_update_check.py` (unit + intended-RED dispatch) + the
  single A3 flip (`test_a3_project_version_is_1_7_0`).
- **9 GREEN-at-baseline** (new regression locks): the Q7 spec-lock + 8 dispatch
  absence tests.
- The prior 543 stay GREEN, except the deliberately-flipped A3 (542 prior pass
  + 9 new green = 551 passed).

**RED-vs-GREEN classification (the contract for this phase).**

| Test(s) | Class | RED reason / GREEN basis |
|---|---|---|
| all unit tests (`is_newer`, `format_notice`, cache I/O, throttles, fetch, suppression) | RED | `AssertionError: update_check module not yet implemented (Phase 5)` (`uc is None`) |
| `test_dispatch_newer_emits_one_stderr_notice` | RED | empty stderr — `''.endswith(notice)` is False (no hook yet) |
| `test_dispatch_failing_verb_keeps_exit_code_and_shows_notice` | RED | `code == 2` holds; empty stderr fails the notice assertion |
| `test_dispatch_stale_check_fetches_once_and_advances_last_check` | RED | `spy.calls == 0 != 1` (no hook calls the fetch) |
| `test_dispatch_notify_throttle_is_independent_of_check` | RED | `spy.calls == 0 != 1` |
| `test_dispatch_quiet_warms_cache_without_notice` | RED | `after is None` (no cache file written) |
| `test_dispatch_corrupt_cache_recovers_and_notifies` | RED | empty stderr fails the notice assertion (asserted before the cache read, so no JSON traceback) |
| `test_dispatch_non_tty_still_sees_notice` | RED | non-TTY asserted true; empty stderr fails the notice assertion |
| `test_a3_project_version_is_1_7_0` | RED | `AssertionError` — pyproject still `1.6.5` |
| `test_cli_md_pins_notice_template_and_suppression_env_vars` (Q7 lock) | GREEN | Phase 1 pinned the template + env vars in cli.md |
| `test_dispatch_same_version_is_silent` / `_older_latest_is_silent` / `_offline_*` | GREEN | tool emits no notice today (no hook) |
| `test_dispatch_fresh_cache_skips_network` / `_ci_env_*` / `_no_update_check_env_*` / `_do_not_track_env_*` | GREEN | `spy.calls == 0` (fetch never installed/called at baseline) |
| `test_dispatch_json_keeps_stdout_clean_and_suppresses_notice` | GREEN | `list --json` already emits byte-clean JSON, no notice |

**Verification.** Sampled the RED tracebacks: unit → the not-impl assertion;
dispatch → `AssertionError` on empty stderr / `spy.calls` / `after is None`;
A3 → `AssertionError`. No tracebacks, no collection errors, no argparse exit-2.
Confirmed the only non-`test_update_check` failure is the A3 flip, and the 9
GREEN-at-baseline locks pass. The quality gate (ruff / ruff format --check /
mypy) is clean tree-wide at the RED baseline.
