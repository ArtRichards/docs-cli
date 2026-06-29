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
  baseline, finalized by the 2026-06-29 fresh-eyes review fold-in: 600 collected;
  48 RED [47 update-check + the deliberately-flipped A3] / 10 GREEN-at-baseline
  locks; prior suite 542 GREEN + the A3 flip (RED); 552 passed); Phase 5 next.**
  OPEN QUESTIONS are netted out — **none outstanding** (the
  re-scope resolves or moots OQ-1..OQ-9; OQ-6's "ship D5" is REVERSED). See the
  milestone doc's Decisions.

(Note: doc-lifecycle status is the front-matter `Lifecycle:` field. This
section tracks implementation progress, which is distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Done | 2026-06-29 | `cli.md` §Update check + §Output-conventions note; bundled `cli.md` mirror resynced byte-identical; INDEX + frozen snapshot refrozen (single delta = `cli.md` `Updated:` bump); `convention.md` untouched. 543 GREEN. |
| 2. Write Tests (RED) | Done | 2026-06-29 | New `tests/test_update_check.py` (55 tests at the Phase-2 run; the 2026-06-29 fresh-eyes review fold-in later added +2 → **57**: a `--version`-absence GREEN lock, a `should_notify` no-cache RED unit, and a hardened failing-verb assertion — see the review fold-in note); `conftest.py` offline guard (`DOCS_CLI_NO_UPDATE_CHECK=1`); `test_packaging.py` A3 flipped to 1.7.0. Collects 598 (600 post-review); gate clean. |
| 3. Create Data/Fixtures | Done | 2026-06-29 | Inline, date-independent `tmp_path` builders in `tests/test_update_check.py`; no committed dated fixtures (the frozen `docs-INDEX.md` stays the only committed fixture). |
| 4. Run Tests (RED Baseline) | Done | 2026-06-29 (finalized by the review fold-in same day) | **600 collected; 48 RED (47 update-check + A3 flip), 10 GREEN-at-baseline locks; prior suite 542 GREEN + the A3 flip (RED); 552 passed** (542 prior + 10 new green). Every RED a clean classified assertion; gate clean tree-wide. |
| 5. Update Base Interfaces | Done | 2026-06-29 | New `src/docs_cli/update_check.py` (Cache + leaf helpers fully implemented; `maybe_notify` a declared no-op until Phase 6); `cli.py` extracts `_dispatch(args)` and reduces `main()` to dispatch → `maybe_notify(args, os.environ, __version__)` → return. All 40 unit tests GREEN; 7 orchestration dispatch tests + A3 stay RED (8 failed / 592 passed); gate clean. |
| 6. Implement Offline/Core Path | Done | 2026-06-29 | Implemented `maybe_notify` (broad fail-silent net) + `_check_and_notify` (network-suppress short-circuit → cache read → 24h-gated fetch → `is_newer` + notice-suppress + 24h notify-gate → STDERR emit → write on fetch-or-emit) + `_now_iso`. All 47 RED dispatch+unit → GREEN; 10 locks stay GREEN. Full suite **1 failed (A3 only), 599 passed**; gate clean. |
| 7. Update Tool/Wrapper Layer | Done | 2026-06-29 | `pyproject.toml` `version` 1.6.5 → **1.7.0**; `test_packaging.py` B1/B2/C2 pins + docstrings flipped to 1.7.0 (C2 renamed `…_1_6_5` → `…_1_7_0`); `CHANGELOG.md` `### Added` block appended under the existing `## 1.7.0 — UNRELEASED` (one header, both `### Added` + M22's `### Documentation`); `SKILL.md` gained an "Update notices" section (advisory line + `CI`/`DOCS_CLI_NO_UPDATE_CHECK`/`DO_NOT_TRACK`). `cli.md`/`convention.md` untouched (contract pinned Phase 1) → bundled refs stay byte-identical (`test_skill_refs` GREEN). A3 GREEN; gate clean. |
| 8. Run Tests (GREEN) | Done | 2026-06-29 | Editable reinstall (`pip install -e .`) refreshed the dist-info → `importlib.metadata` reports 1.7.0. Full suite **600 passed**; `ruff check` / `ruff format --check` / `mypy` (43 files) clean; `docs check docs/` 0 violations; `docs index` a byte no-op; `docs --version` → `docs 1.7.0`. |
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
.venv/bin/python -m pytest tests/ -q          # 48 failed, 552 passed (600 total)
.venv/bin/python -m pytest tests/test_update_check.py -q   # 47 failed, 10 passed
```

(Counts are the finalized baseline after the 2026-06-29 fresh-eyes review
fold-in added +2 tests — see the review fold-in note. The original Phase-4 run
collected 598: 47 RED / 9 GREEN-at-baseline / 551 passed.)

**Baseline counts.**

- **600** collected (= prior suite 543 + 57 new in `test_update_check.py`).
- **48 RED**: 47 in `test_update_check.py` (unit + intended-RED dispatch) + the
  single A3 flip (`test_a3_project_version_is_1_7_0`).
- **10 GREEN-at-baseline** (new regression locks): the Q7 spec-lock + 9 dispatch
  absence tests (incl. the `--version`-absence lock).
- The prior suite is **542 GREEN + the deliberately-flipped A3 (RED)**; total
  passed is **552** (542 prior + 10 new green). Reconciles: 542 + 1 (A3) + 57
  new = 600 collected; 48 RED + 552 GREEN = 600.

**RED-vs-GREEN classification (the contract for this phase).**

| Test(s) | Class | RED reason / GREEN basis |
|---|---|---|
| all unit tests (`is_newer`, `format_notice`, cache I/O, throttles, fetch, suppression) | RED | `AssertionError: update_check module not yet implemented (Phase 5)` (`uc is None`) |
| `test_dispatch_newer_emits_one_stderr_notice` | RED | empty stderr — `''.endswith(notice)` is False (no hook yet) |
| `test_dispatch_failing_verb_keeps_exit_code_and_shows_notice` (hardened, FI-3) | RED | `code == 2` and the additive guard (`"error:" in out.out` — `check` prints findings to **stdout**) both hold; empty stderr fails the notice-present assertion. The own-line guard (`before == "" or before.endswith("\n")`) is unreached at baseline |
| `test_dispatch_stale_check_fetches_once_and_advances_last_check` | RED | `spy.calls == 0 != 1` (no hook calls the fetch) |
| `test_dispatch_notify_throttle_is_independent_of_check` | RED | `spy.calls == 0 != 1` |
| `test_dispatch_quiet_warms_cache_without_notice` | RED | `after is None` (no cache file written) |
| `test_dispatch_corrupt_cache_recovers_and_notifies` | RED | empty stderr fails the notice assertion (asserted before the cache read, so no JSON traceback) |
| `test_dispatch_non_tty_still_sees_notice` | RED | non-TTY asserted true; empty stderr fails the notice assertion |
| `test_a3_project_version_is_1_7_0` | RED | `AssertionError` — pyproject still `1.6.5` |
| `test_cli_md_pins_notice_template_and_suppression_env_vars` (Q7 lock) | GREEN | Phase 1 pinned the template + env vars in cli.md |
| `test_dispatch_version_flag_never_emits_notice` (FI-2) | GREEN | `docs --version` SystemExits in argument parsing, before the post-dispatch hook → no notice (trivially silent now; a real hook-placement lock once Phase 5/6 lands) |
| `test_should_notify_true_when_no_cache` (FI-4) | RED | unit — `AssertionError: update_check module not yet implemented (Phase 5)` (`uc is None`); symmetric to `should_check`'s no-cache case |
| `test_dispatch_same_version_is_silent` / `_older_latest_is_silent` / `_offline_*` | GREEN | tool emits no notice today (no hook) |
| `test_dispatch_fresh_cache_skips_network` / `_ci_env_*` / `_no_update_check_env_*` / `_do_not_track_env_*` | GREEN | `spy.calls == 0` (fetch never installed/called at baseline) |
| `test_dispatch_json_keeps_stdout_clean_and_suppresses_notice` | GREEN | `list --json` already emits byte-clean JSON, no notice |

**Verification.** Sampled the RED tracebacks: unit → the not-impl assertion;
dispatch → `AssertionError` on empty stderr / `spy.calls` / `after is None`;
A3 → `AssertionError`. No tracebacks, no collection errors, no argparse exit-2.
Confirmed the only non-`test_update_check` failure is the A3 flip, and the 10
GREEN-at-baseline locks pass. The quality gate (ruff / ruff format --check /
mypy) is clean tree-wide at the RED baseline.

## Fresh-eyes review fold-in (Step 1 finalize, 2026-06-29)

An independent fresh-eyes review found Step 1 sound — no blockers, no
correctness bugs (it verified the baseline numbers, the byte-exact notice, the
three-key cache with no leftover `last_skill_drift_notified`, `convention.md`
untouched, INDEX/snapshot lockstep, the full D5 cut, and that the Phase-2 tests
genuinely pin the contract). The conductor triaged its findings into four
binding fold-ins, all auto-resolved (no operator decision pending), applied
here as **test additions + test hardening + doc-accuracy fixes only** — the
implementation module `src/docs_cli/update_check.py` is still deliberately
absent (Phase 5). The classified RED baseline is preserved.

- **FI-1 (doc accuracy).** The rolled-up baseline one-liners overstated the
  green count: "prior 543 GREEN" alongside "47 RED / 9 GREEN-at-baseline"
  double-counted the A3 test (it is one of the 47 RED **and** part of the prior
  543), implying 599 collected vs the 598 actually collected. Reconciled
  everywhere the loose phrasing appeared (this impl-log's Overview + Phase-4
  entry/table, `status.md`, `plan.md`, and the milestone doc's Progress) to the
  recomputed numbers: **prior suite 542 GREEN + the deliberately-flipped A3
  (RED); 57 new = 47 RED + 10 GREEN-at-baseline locks; 600 collected; 552
  passed.**
- **FI-2 (test-hardening — Q10 lock elevated to should-fix).** Added
  `test_dispatch_version_flag_never_emits_notice`: with the offline guard
  cleared and `fetch_latest_version` returning a strictly-newer version,
  `docs --version` (which SystemExits inside argument parsing, before the
  post-dispatch hook) emits **no** notice on stderr. GREEN-at-baseline (no hook
  yet → trivially silent); a real hook-placement lock once Phase 5/6 lands. The
  pre-existing `docs --version` test only inspected stdout, so a hook-placement
  regression would have been uncaught.
- **FI-3 (test-hardening).** Hardened
  `test_dispatch_failing_verb_keeps_exit_code_and_shows_notice` so a hook that
  (a) clobbered the command's own output or (b) glued the notice onto a prior
  line could no longer pass. `docs check` prints its findings to **stdout**
  (stderr is empty until the notice lands), so the additive guard asserts the
  findings survive on stdout (`"error:" in out.out`); the own-line guard asserts
  what precedes the notice on stderr is either nothing or ends in a newline
  (`before == "" or before.endswith("\n")`). Still intended-RED at baseline —
  the notice-present assertion (`out.err.endswith(notice)`) drives the RED.
- **FI-4 (test completeness).** Added `test_should_notify_true_when_no_cache`,
  the symmetric no-prior-notice unit case for `should_notify` (mirrors
  `should_check`'s no-cache case). RED-at-baseline via the `uc is None` guard.

**Re-run after the fold-ins:** `.venv/bin/python -m pytest tests/ -q` →
**48 failed, 552 passed (600 collected)**; `tests/test_update_check.py` →
47 failed, 10 passed (57 tests). Every RED is a clean classified assertion
(unit → the not-impl guard; intended-RED dispatch → empty-stderr notice /
`spy.calls` / `after is None`; A3 → pyproject still `1.6.5`) — no tracebacks, no
collection errors, no argparse exit-2. Quality gate clean tree-wide (ruff / ruff
format --check / mypy / `docs check docs/`).

## Phase 5 — Update Base Interfaces

**Objective.** Declare the `docs_cli.update_check` seam and wire the `main()`
hook, fully implementing the leaf/unit-tested functions so every UNIT test goes
GREEN; the dispatch orchestration is deferred to Phase 6 (the honest split).

**Files changed.**

- `src/docs_cli/update_check.py` (NEW) — the cohesive update-check module
  (OQ-7). Constants `PYPI_URL`, `TIMEOUT = 1.0`, `THROTTLE = timedelta(hours=24)`,
  and the byte-exact `NOTICE_TEMPLATE` (em-dash U+2014, ASCII `->`). The
  `Cache` dataclass (three optional keys). Leaf helpers fully implemented:
  `is_newer` (stdlib numeric tuple-compare on dot-split release segments,
  fail-closed on any non-digit segment → pre-release / `0.0.0+local` /
  unparseable never notify); `format_notice` (no trailing newline);
  `cache_path` (XDG-aware); `read_cache` (missing / corrupt / non-dict /
  missing-`last_check`-or-`latest_version` → `Cache()`; `last_notified`
  optional); `write_cache` (exactly three keys; `mkdir(parents=True)` then
  `write_text`, swallowing `OSError`); `should_check` / `should_notify` via a
  `_stale` helper (None / unparseable / ≥24h → True); `fetch_latest_version`
  (calls `urllib.request.urlopen(PYPI_URL, timeout=TIMEOUT)` as a module
  attribute so the monkeypatch is seen; returns `info.version` or `None` on
  URLError/timeout/HTTPError/OSError/malformed-JSON/KeyError/TypeError); and the
  `notice_suppressed` / `network_suppressed` predicates (defensive `getattr`;
  env presence-not-truthiness via `_env_disabled`). `maybe_notify` is a declared
  no-op this phase (`return None`).
- `src/docs_cli/cli.py` — added `from docs_cli import update_check` (first-party
  import; no cycle — `update_check` imports no `docs_cli` symbol, the running
  version is threaded in). Extracted the verbatim dispatch ladder into a new
  module-level `def _dispatch(args) -> int:` and reduced `main()` to
  `args = _build_parser().parse_args(argv)` → `code = _dispatch(args)` →
  `update_check.maybe_notify(args, os.environ, __version__)` → `return code`.
  Placement after `parse_args` means `--version` / `-h` (which `SystemExit`
  inside parsing) never reach the hook.

**Decisions applied (from the Step-2 plan).** Q3 — the running version is
threaded in as `current` (no `importlib.metadata` recompute inside
`update_check`, no circular import). Q4 — `_dispatch` extracted; the hook fires
once between dispatch and `return code`. Q1 — `read_cache` requires `last_check`
AND `latest_version` (so a 2-key warm cache is honored — keeps
`test_dispatch_fresh_cache_skips_network` GREEN) but treats a `last_check`-only
file as no-data. The `write_cache` `try/except OSError: return` mirrors the
codebase's `contextlib.suppress(OSError)` posture (`cli.py`).

**Test results.** `tests/test_update_check.py` → **50 passed, 7 failed** (all 40
unit tests GREEN; the 7 RED are exactly the orchestration-dependent dispatch
tests, plus A3 elsewhere). Full suite → **8 failed, 592 passed** (the 7 dispatch
+ A3; prior 542 + the 10 locks GREEN — the hook is inert under the conftest
`DOCS_CLI_NO_UPDATE_CHECK=1` guard and the no-op `maybe_notify`). Gate clean:
`ruff check` / `ruff format --check` / `mypy` (43 source files) all pass.

## Phase 6 — Implement Offline/Core Path

**Objective.** Complete the orchestration so all 17 offline dispatch RED tests
go GREEN while the 10 absence locks stay GREEN.

**Files changed.**

- `src/docs_cli/update_check.py` — added `import sys`, `_now_iso()`
  (`datetime.now(UTC).isoformat()`), and replaced the no-op `maybe_notify`
  with the real two-function core path (Q2/Q9):
  - `maybe_notify(args, env, current)` wraps `_check_and_notify` in a top-level
    `except Exception: return` — the documented fail-silent net (ruff does not
    select BLE; the leaf functions keep their own specific catches). No
    update-check error can reach `main()`.
  - `_check_and_notify(...)`: `network_suppressed` short-circuit (CI /
    `DOCS_CLI_NO_UPDATE_CHECK` / `DO_NOT_TRACK` → no network, no notice) →
    `read_cache` → if `should_check`, `fetch_latest_version`; on a non-None
    result rebuild the cache with a fresh `last_check` + `latest_version`,
    **preserving `last_notified`** (the notify budget) and setting `fetched` →
    then, when `latest is not None and is_newer(current, latest) and not
    notice_suppressed and should_notify`, `print(format_notice(...),
    file=sys.stderr)` (the emitter adds the `\n`; last stderr line), advance
    `last_notified` **only on the actual emit**, set `notified` → finally
    `write_cache` when `fetched or notified`.

**Decisions applied / recorded.**

- **Q2 — write on success-or-emit; bounded offline-retry property.** The cache
  is written only after a successful fetch or an actual emit. Because
  `read_cache` treats a `last_check`-only file as "no data" (Q1), a
  permanently-**offline** host re-attempts the network on *every* invocation
  (each bounded by the 1.0s timeout) rather than once/24h — there is never a
  successful fetch to persist a `last_check`, and a `last_check`-only file would
  be ignored on read anyway. This is **forced by the locked tests + cli.md**
  ("created on first **successful** check") and is an accepted, bounded
  property; no un-pinned `last_check`-only persistence path was added (it would
  be ignored on read).
- **Q6 — `last_notified` advances only on emit.** A `--quiet` / `--json` run
  warms `last_check` (and `latest_version`) but never `last_notified`, so the
  notice budget is untouched (pinned by `test_dispatch_quiet_warms_cache_…`).
- **Q9 — fail-silent boundary** kept as the top-level `except Exception:
  return` with specific catches in the leaves.

**Test results.** `tests/test_update_check.py` → **57 passed** (all 47 prior-RED
now GREEN; the 10 locks hold). Full suite → **1 failed, 599 passed** — the only
RED is `test_a3_project_version_is_1_7_0` (pyproject still `1.6.5` until Phase
7's bump; expected, not a regression). No network touched in-suite (the conftest
guard + the injected `fetch_latest_version`). Gate clean: `ruff check` / `ruff
format --check` / `mypy` (43 source files) all pass.

## Phase 7 — Update Tool/Wrapper Layer

**Objective.** Flip the version/packaging surface to 1.7.0 and reconcile the
CHANGELOG + bundled skill — no new argparse flag (the controls are env vars +
the existing `--quiet` / `--json`), so `docs --help` / per-verb `--help` are
unchanged.

**Files changed.**

- `pyproject.toml` — `[project].version` `1.6.5` → **`1.7.0`** (the minor bump;
  `importlib.metadata` stays the SoT, so `docs --version` reads `1.7.0` after
  the Phase-8 editable reinstall).
- `tests/test_packaging.py` — flipped the slow build-gated pins in lockstep with
  the A3 fast pin (already 1.7.0 from Phase 2): **B1** `startswith
  "docs_cli-1.7.0-"`, **B2** `== "docs_cli-1.7.0.tar.gz"`, **C2** renamed
  `test_c2_docs_version_is_1_6_5` → `…_1_7_0` and now requires `"1.7.0"` as a
  standalone token; bumped each docstring (M19 → M21). B3 is positive-presence
  and ships the whole package, so the new `update_check.py` module needs no
  packaging change (OQ-7, verified).
- `CHANGELOG.md` — **appended** an `### Added` block **under** the existing
  `## 1.7.0 — UNRELEASED` header (opened by M22's `### Documentation`) — no
  second 1.7.0 header. Documents the STDERR-only ≤once/24h fail-silent notice,
  the `DOCS_CLI_NO_UPDATE_CHECK` / `DO_NOT_TRACK` / `CI` disable controls, and
  the `--quiet` / `--json` suppression (cache still warms; `--json` stdout stays
  byte-clean).
- `src/docs_cli/skill/SKILL.md` — added a short "Update notices" section naming
  the advisory line and the three disable env vars (Q8 — surface-parity policy).
  No `](../` repo-relative link; the strings `test_skill_quality_artifacts.py`
  pins are untouched.

**Not changed (by decision).** `docs/cli.md` and `docs/convention.md` (the
contract was pinned in Phase 1) → the bundled `references/{cli,convention}.md`
mirrors stay byte-identical (`test_skill_refs` re-run GREEN, no re-sync needed).

**Test results.** `test_a3` GREEN at 1.7.0; `test_skill_refs` +
`test_skill_quality_artifacts` GREEN; `tests/test_update_check.py` 57 GREEN.
Gate clean (`ruff check` / `ruff format --check`). The build-gated B1/B2/C2 +
the editable-reinstall version match run in Phase 8.

## Phase 8 — Run Tests (GREEN)

**Objective.** Full suite GREEN; gate clean tree-wide; `docs --version` →
`docs 1.7.0`.

**Editable reinstall (Q7).** After the Phase-7 pyproject bump,
`importlib.metadata` still reported 1.6.5 until the dist-info was refreshed (the
M19 precedent), so `test_version_metadata::test_version_matches_pyproject` was
RED until `.venv/bin/pip install -e .` ran. Post-reinstall: docs-cli 1.7.0
installed; `__version__` → 1.7.0; the dispatch tests still pass (the fake PyPI
1.7.1 > 1.7.0).

**Commands + output.**

```sh
$ .venv/bin/pip install -e .
Successfully installed docs-cli-1.7.0
$ .venv/bin/python -m pytest tests/ -q
600 passed in 26.10s
$ .venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
All checks passed!
42 files already formatted
Success: no issues found in 43 source files
$ .venv/bin/docs check docs/
docs: no violations found
$ .venv/bin/docs index --root docs/        # byte no-op (git diff --quiet clean)
$ .venv/bin/docs --version
docs 1.7.0
```

**Exit.** Full suite **600 GREEN**; gate clean tree-wide; `docs --version` →
`docs 1.7.0`. (The single `mypy` note —
`[annotation-unchecked]` on a test helper — is informational, not an error;
`mypy` reports "Success".)
