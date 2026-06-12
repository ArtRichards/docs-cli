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
  live milestone and is independent. **Implementation-complete (2026-06-12)** —
  all ten TDD phases done (Step 1 phases 1-4 on `m19/phases-1-4`; Step 2
  phases 5-10 on `m19/phases-5-10`); full suite 533/533 GREEN, gate clean,
  `docs --version` → `docs 1.6.5` (built locally; publish is a later
  operator-driven milestone). OPEN QUESTIONS Q1–Q6 are RESOLVED
  (operator decisions 2026-06-12, each per the recommended default —
  see the milestone doc's Decisions › "Resolved questions (Q1-Q6, BINDING)");
  the Step-2 implementation forks OQ-1..OQ-5 are RESOLVED (conductor decisions
  — see the milestone doc's Decisions › "Implementation-phase open questions");
  a post-draft operator addition (2026-06-12) folds **threshold provenance**
  into D2 — the stale finding's message must name where the threshold is set
  (`set in .docs.toml [check] stale_days` for config-sourced, `via --stale`
  for CLI-sourced).

(Note: doc-lifecycle status is the front-matter `Lifecycle:` field. This
section tracks implementation progress, which is distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | **Complete** | 2026-06-12 | `cli.md` §touch `--check [--stale N]` block + heading; §check stale-window resolution (CLI `--stale` > `[check] stale_days` > unset) + threshold-provenance message contract; §list Q6 note; `convention.md` `[check]` subsection. Bundled refs resynced byte-identical (`test_skill_refs` GREEN); `docs check docs/` exit 0; INDEX snapshot in lockstep. The three Phase-2 verbatim strings (`--stale requires --check`, `set in .docs.toml [check] stale_days`, `via --stale`) all present. Q-A provenance-plumbing (`stale_source` + `resolve_stale` helper) noted in the contract. |
| 2. Write Tests (RED) | **Complete** | 2026-06-12 | 23 new tests, split by layer (Q-C). D1 touch `--check` (12) in `test_cli_touch.py`; D2 config-parse (2) in `test_config.py`; D2 check CLI + provenance (6) in `test_cli_check.py`; Q6 list locks (2) in `test_cli_list.py`; D3 help (1) in `test_body_from.py`; version pin flipped `test_a3_..._1_6_0` → `..._1_6_5` in `test_packaging.py` (B1/B2/C2 untouched — Q-D, Phase-7 surface). Reused `_multi_file_tree` / `_orphan_doc` / `_touch_excluded_malformed_tree` (touch) + `_stale_tree` (check). Suite collects 533 (510 + 23); ruff + format clean on the new files. |
| 3. Create Data/Fixtures | **Complete** | 2026-06-12 | All fixtures are inline `tmp_path` builders with `today`-relative dates (no committed static fixtures — committed dates rot). `_stale_config_tree(tmp_path, name, *, stale_days)` in `test_cli_check.py` mirrors `_stale_tree` + the `[check] stale_days = N` sidecar; `_check_tree` (touch) and `_list_stale_config_tree` (list) likewise; the broken-ref + clean + config-default cases are inline. No `tests/fixtures/trees/` additions; the byte-frozen `docs-INDEX.md` snapshot is the only committed fixture, kept in lockstep. (Builders authored in the Phase-2 commit — tests cannot collect without them; this phase confirms the inline-only fixture decision.) |
| 4. Run Tests (RED Baseline) | **Complete** | 2026-06-12 | Full suite: **533 collected, 19 failed (RED), 514 passed.** The 19 RED are exactly the intended set, each failing for its classified reason (below). The 514 passing = 509 untouched pre-existing + 5 new GREEN-at-baseline locks (`check_cli_stale_overrides_config`, `check_no_check_section_unchanged`, `check_stale_zero_honored`, `list_stale_config_does_not_filter_bare_list`, `list_explicit_stale_unaffected_by_config`). Note: the version-pin rename flipped the old `test_a3_..._1_6_0` (was GREEN) → `..._1_6_5` (now RED), so "pre-existing still GREEN" is 509, not 510. |
| 5. Update Base Interfaces | **Complete** | 2026-06-12 | `Config.stale_days: int \| None = None` field + docstring; `load_config` reads `[check] stale_days` leniently (OQ-1 — no bespoke validation, mirrors `add_roles`); `resolve_stale(cli_stale, config_stale_days) -> (window, source)` helper after `exit_code_for` (CLI > config > unset; `--stale 0` honoured, only `None` is absent); `check_doc` + `check_tree` gained `stale_source: str \| None = None` (forwarded, defaults keep all callers valid); `touch` argparse gained `--check` (store_true) + `--stale` (type=int, metavar N, no default). 2 config tests GREEN; `touch --help` shows both flags; 12 touch tests moved off argparse-reject onto behavior-RED (7 still RED awaiting Phase 6 wiring; 5 pass coincidentally on clean/fail trees). ruff/format/mypy clean. |
| 6. Implement Offline/Core Path | **Complete** | 2026-06-12 | `check_doc` stale message gains the provenance suffix (config → `, set in .docs.toml [check] stale_days`; cli → `, via --stale`; None → bare form unchanged). **OQ-2 audit DONE**: `grep -rn "stale threshold" tests/` → only the 3 new M19 provenance tests pin message text; all pre-existing stale asserts are rule/severity-based (`test_check.py`) or loose substrings (`test_check_stale_only_tree_exits_1` — `"stale" in stdout.lower()` survives `via --stale`); zero regression. `_cmd_check` calls `resolve_stale` + `_print_check_findings` (extracted, shared). `_cmd_touch`: Q3 guard at top (byte-unchanged file), Q4 dry-run fold + Q1 success fold via new `_run_touch_check` (Q-F predicate parity, Q-E findings-on-stdout-regardless-of-quiet, OQ-5 no --json). D3 `--body-from` help replaced (ASCII `>=`; no "first 20 lines"; carries `---` + `Lifecycle`). **18 of 19 RED → GREEN; only the version pin (test_a3) stays RED.** All 5 GREEN-at-baseline locks + pre-existing suite still GREEN. ruff/format/mypy clean. |
| 7. Update Tool/Wrapper Layer | **Complete** | 2026-06-12 | `pyproject.toml` version 1.6.0 → 1.6.5. Lockstep packaging flips: `test_b1_wheel_builds` → `docs_cli-1.6.5-`, `test_b2_sdist_builds` → `docs_cli-1.6.5.tar.gz`, `test_c2_docs_version_is_1_6_0` renamed → `..._is_1_6_5` (token `1.6.5`); `test_b3`/`test_b4` (version-agnostic) untouched. Editable reinstall (`pip install -e . --no-deps`) → `docs --version` reads `docs 1.6.5`. NEW `## 1.6.5 — UNRELEASED` CHANGELOG section above the dated 1.6.0 (binding Decision — not a fold-in): Added `docs touch --check [--stale N]` + `[check] stale_days = N`; Fixed `--body-from` help drift. Bundled refs unchanged this phase (specs frozen Step 1) — `test_skill_refs` GREEN; `test_a3` GREEN. |
| 8. Run Tests (GREEN) | **Complete** | 2026-06-12 | Full suite **533 passed, 0 failed** (24 s; build-gated b1/b2/c2 rebuilt + GREEN). Gate clean: `ruff check .` All checks passed; `ruff format --check .` 39 files formatted; `mypy` no issues (40 files); `docs check docs/` exit 0; `docs index --root docs/` regen is a byte-no-op (no pending diff); `docs --version` → `docs 1.6.5`. INDEX == frozen snapshot (byte-identical); bundled `cli.md`/`convention.md` byte-identical to source. Verbatim gate output captured at `/tmp/m19-phase-8-green.txt`. |
| 9. Implement Online/Integration | **Complete** | 2026-06-12 | Dogfooded the editable `docs 1.6.5` binary on throwaway `/tmp` trees — all 5 9a exercises GREEN: **(1)** `touch <file> --check` on a clean tree → exit 0, one invocation refreshed INDEX + bumped the doc to today + validated; **(2)** stale active doc + `[check] stale_days = 30` < its 400-day age → `touch <fresh> --check` → exit 1, finding named `(stale threshold 30, set in .docs.toml [check] stale_days)`, no `via --stale`; **(3)** broken `Related:` ref → `touch --check` → exit 2 (`broken-ref`); **(4)** `touch --stale 14` (no `--check`) → exit 2, `docs: touch: --stale requires --check`, file byte-unchanged, no INDEX; **(5)** bare `docs check` on the `[check]` tree → exit 1 config-sourced provenance, `docs check --stale 30` → exit 1 `via --stale` (no config clause). **9b (OQ-3):** real repo `docs/` exercised read-only (`touch --dry-run --check` → exit 0, INDEX untouched); the config path exercised on a `cp -r` throwaway copy of `docs/` with `[check] stale_days = 7` injected into the COPY only (8 stale findings, all config-provenance-named) — the repo's own `docs/.docs.toml` left untouched. Throwaway trees cleaned; working tree clean. |
| 10. Quality, Docs, Refactor | **Complete** | 2026-06-12 | **Surface-parity gate:** `docs touch --help` shows `--check`/`--stale`; `docs check --help` shows `--stale`; `docs new --help` shows the corrected `--body-from` wording — all reconcile against the CHANGELOG surface. `grep -rn "first 20 lines" src/` → **zero source hits** (remaining hits are `docs/` narrative referencing the old string as history/fix-target). **OQ-4:** `src/docs_cli/skill/SKILL.md` verb table touch row → `[--check [--stale N]]` + "--check folds in docs check"; added a `[check] stale_days` paragraph (no byte-identity test counterpart — no lockstep cost; `test_skill`/`test_skill_refs`/`test_skill_quality_artifacts` GREEN). **Simplify sanity (10b):** `resolve_stale`, `_run_touch_check`, `_print_check_findings` each earn their keep (precedence+provenance centralization; touch-side check entry; shared grouped output across `_cmd_check` + `_run_touch_check`); `--dry-run --check` branch reads linearly. Deep `/simplify` deferred to Step 3 per plan. **Local build (M14 precedent):** standalone `python -m build` → `docs_cli-1.6.5.tar.gz` + `docs_cli-1.6.5-py3-none-any.whl`; `twine check dist/*` both **PASSED** (wheel sha256 `05e9126d…`, sdist `9f47ed75…`; dist/ gitignored, NO publish/tag/release). Closeout: milestone Phase Checklist 5-10 + Deliverables D1-D4 + Success Criteria ticked; OQ-1..OQ-5 recorded in Decisions; status.md + plan.md → M19 implementation-complete; lifecycle stays `draft`, M19 stays LIVE at root. |

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

## Phase 1 — Define Contract (2026-06-12, branch `m19/phases-1-4`)

**Objective.** Pin the M19 surface in the specs (no code, no tests) so the
Phase-2 RED tests assert against frozen, byte-identical contract text.

**Files changed.**

- `docs/cli.md` (+ bundled `src/docs_cli/skill/references/cli.md`, resynced):
  - §`docs touch` heading → `### \`docs touch <file>... [--check [--stale N]]\``;
    new **`--check [--stale N]`** block after the dry-run paragraph pinning:
    tree-wide `check_tree` after the end-of-batch reindex *replacing* the
    `docs check .` loop step (Q2); combined exit `max(touch, check)` with the
    touch-fail short-circuit (Q1); `--stale` forwarding + the
    `docs: touch: --stale requires --check` hard exit 2 (Q3); `--dry-run
    --check` over the un-mutated on-disk tree (Q4); `--quiet` gates only
    touch's stderr lines, never the check findings on stdout (Q-E); the
    `[exclude]`/`.docsignore` predicate parity (Q-F).
  - §`docs check` → **Stale-window resolution** (CLI `--stale` > `[check]
    stale_days` > unset; `--stale 0` honoured; a configured key makes bare
    `docs check` apply the rule — Q5) + **Threshold provenance** message
    contract (config-sourced → `(stale threshold N, set in .docs.toml [check]
    stale_days)`; CLI-sourced → `(stale threshold N, via --stale)`; id +
    severity + exit code unchanged). The Q-A provenance plumbing — a
    `stale_source` (`"config"`/`"cli"`/`None`) threaded alongside the window
    and a shared `resolve_stale(cli_stale, config.stale_days) -> (window,
    source)` helper — is noted in the contract (interface lands Phase 5).
    The existing `--stale N` stale bullet was reworded to point at the
    resolution subsection.
  - §`docs list` → Q6 note: `[check] stale_days` does NOT affect `docs list
    --stale`; bare `docs list` still lists everything; explicit `--stale N`
    unaffected.
- `docs/convention.md` (+ bundled `references/convention.md`, resynced): new
  `### Per-tree \`[check]\` config (M19 — D2)` subsection modeled on
  `[migrate]` — `stale_days = N` non-negative int; absent → no default
  window; supplies the window to `docs check` / `docs touch --check`, NOT
  `docs list`; CLI `--stale` overrides.
- D3: no spec edit (the `docs/cli.md` §`docs new` `--body-from` prose is
  already correct — only the argparse help string in `cli.py` drifts, fixed
  at Phase 6).
- `docs/cli.md` + `docs/convention.md` `Updated:` bumped to 2026-06-12 via
  `docs touch`; `docs/INDEX.md` refreshed; the frozen snapshot
  `tests/fixtures/expected/docs-INDEX.md` re-synced byte-identical.

**Verification.**

- Verbatim Phase-2 assertion strings all present in `cli.md`:
  `--stale requires --check`, `set in .docs.toml [check] stale_days`,
  `via --stale` (1 occurrence each).
- `tests/test_skill_refs.py` GREEN (bundled refs byte-identical to source).
- `.venv/bin/docs check docs/` → exit 0 (`docs: no violations found`).
- `docs/INDEX.md` == `tests/fixtures/expected/docs-INDEX.md` (byte-identical).

**Exit criteria met.** Every string Phase-2 asserts appears verbatim in
`cli.md`; the Q-A provenance-plumbing approach is noted in the contract;
`test_skill_refs.py` GREEN.

## Phase 2 — Write Tests (RED) (2026-06-12, branch `m19/phases-1-4`)

**Objective.** Pin the M19 contract in tests, split by layer into the
existing suites (Q-C — no new test file), following the subprocess-`_run`
convention.

**Files changed (23 new tests).**

- `tests/test_cli_touch.py` (**D1 — 12 tests**, `import timedelta` added;
  reused `_multi_file_tree` / `_orphan_doc` / `_touch_excluded_malformed_tree`;
  new local `_check_tree` builder, today-relative dates):
  `test_touch_check_clean_tree_exits_0`,
  `test_touch_check_stale_tree_exits_1`,
  `test_touch_check_broken_ref_tree_exits_2`,
  `test_touch_check_runs_check_after_reindex`,
  `test_touch_check_touch_failure_short_circuits_check`,
  `test_touch_check_outside_root_short_circuits`,
  `test_touch_stale_without_check_exits_2`,
  `test_touch_dry_run_check_writes_nothing_and_checks_unmutated_tree`,
  `test_touch_check_forwards_stale_value`,
  `test_touch_check_quiet_suppresses_touch_lines_not_findings`,
  `test_touch_check_excluded_malformed_file_does_not_fail_check` (Q-F lock),
  `test_touch_check_config_default_provenance`.
- `tests/test_config.py` (**D2 config — 2 tests**):
  `test_load_config_reads_stale_days`,
  `test_load_config_stale_days_defaults_to_none`.
- `tests/test_cli_check.py` (**D2 check + provenance — 6 tests**, new
  `_stale_config_tree` builder + `import timedelta`):
  `test_check_config_stale_days_applies_to_bare_check` (HEADLINE Q5),
  `test_check_cli_stale_overrides_config`,
  `test_check_no_check_section_unchanged` (GREEN-at-baseline),
  `test_check_config_sourced_provenance_message`,
  `test_check_cli_sourced_provenance_message`,
  `test_check_stale_zero_honored` (GREEN-at-baseline).
- `tests/test_cli_list.py` (**Q6 — 2 GREEN-at-baseline locks**, new
  `_list_stale_config_tree` builder + `import date, timedelta`):
  `test_list_stale_config_does_not_filter_bare_list`,
  `test_list_explicit_stale_unaffected_by_config`.
- `tests/test_body_from.py` (**D3 — 1 test**):
  `test_new_body_from_help_no_first_20_lines`.
- `tests/test_packaging.py` (**version pin**):
  `test_a3_project_version_is_1_6_0` → `test_a3_project_version_is_1_6_5`
  asserting `"1.6.5"`. **B1/B2/C2 left for Phase 7** (Q-D — slow
  build-gated; the editable-install / wheel-version surface is reconciled
  when `pyproject.toml` flips at Phase 7).

**RED classifications (carried into the Phase-4 row).**

- D1 touch `--check` / `--stale` tests: argparse rejects the undeclared flags
  with **exit 2** ("unrecognized arguments") until Phase 5 — documented honest
  RED (Q-B/Q-D style). The intended-exit-2 tests
  (`outside_root_short_circuits`, `stale_without_check`) assert the *contract*
  message, not argparse's, so they also fail at baseline.
- D2 `Config.stale_days` tests: **AttributeError** until the field lands at
  Phase 5 (Q-B — not pulled into Phase 3).
- D2 check-CLI behaviour/provenance + D3 help + A3 version-pin: plain
  **assertion** failures.
- GREEN-at-baseline locks (`no_check_section_unchanged`, `stale_zero_honored`,
  the two Q6 list locks): pass today and must keep passing.

**Verification.** `pytest --co` collects 533 (510 + 23). `ruff check` +
`ruff format --check` clean on all six edited test files.

**Exit criteria met.** Tests written RED per the plan; collection clean; the
intended-RED vs GREEN-at-baseline split is classified for Phase 4.

## Phase 3 — Create Data/Fixtures (2026-06-12, branch `m19/phases-1-4`)

**Objective.** Provide the test data the Phase-2 RED tests need, preferring
inline `tmp_path` builders over committed dated fixtures (committed dates
rot as the wall clock advances).

**Decision: inline-only, today-relative.** Every M19 fixture is an inline
`tmp_path` builder whose stale dates are computed as
`date.today() - timedelta(days=400)` (and "fresh" as `date.today()`), so no
case rots. No files were added under `tests/fixtures/trees/`.

**Builders (authored in the Phase-2 commit — tests cannot collect without
them; recorded here as the Phase-3 fixture surface):**

- `tests/test_cli_check.py` — `_stale_config_tree(tmp_path, name, *,
  stale_days)`: mirrors the existing `_stale_tree` and adds the
  `[check] stale_days = N` sidecar + one 400-day-old active doc. Used by the
  config-default, CLI-override, and both provenance tests.
- `tests/test_cli_touch.py` — `_check_tree(tmp_path, name)`: a root with one
  fresh + one ancient active doc, for the touch `--check` exit-code and
  forwarding/quiet tests. The broken-ref and clean cases are inline within
  their tests.
- `tests/test_cli_list.py` — `_list_stale_config_tree(tmp_path, name, *,
  with_check)`: a fresh + ancient pair, optionally carrying the
  `[check] stale_days = 1` sidecar, for the Q6 list regression locks.

**Static fixtures.** None added. The only committed fixture in M19's blast
radius is the byte-frozen `tests/fixtures/expected/docs-INDEX.md`, kept
identical to `docs/INDEX.md` after every INDEX regen (the repo's lockstep
invariant). Confirmed `git status` shows no new `tests/fixtures/` files.

**Exit criteria met.** All Phase-2 tests have date-independent inline data;
no rotting committed fixture introduced.

## Phase 4 — Run Tests (RED Baseline) (2026-06-12, branch `m19/phases-1-4`)

**Objective.** Confirm every intended-RED test fails for its *classified*
reason, the GREEN-at-baseline locks pass, and the pre-existing suite still
passes.

**Result: `533 collected, 19 failed (RED), 514 passed`** (`pytest tests/ -q`,
23.6 s).

- **19 RED** — exactly the intended set.
- **514 GREEN** = 509 untouched pre-existing + 5 new GREEN-at-baseline locks.
  (The version-pin rename flipped the old `test_a3_..._1_6_0`, previously
  GREEN, into the now-RED `..._1_6_5`, so the untouched pre-existing GREEN
  count is 509, not 510 — the headline 510 minus the one renamed test.)

**RED classifications (each verified against the captured failure line).**

| Tests | # | RED reason (verified) |
|---|---|---|
| D1 touch `--check` / `--stale` (all 12 in `test_cli_touch.py`) | 12 | argparse `error: unrecognized arguments: --check` / `--stale` → **exit 2** (flags undeclared until Phase 5). The two intended-exit-2 cases (`stale_without_check`, `outside_root_short_circuits`) get argparse's exit 2 but fail their *message* assertion (`--stale requires --check` / `is not under a docs root`), so they are genuinely RED, not falsely green. Documented honest RED (Q-B/Q-D style). |
| `Config.stale_days` parse (2 in `test_config.py`) | 2 | `AttributeError: 'Config' object has no attribute 'stale_days'` — the field lands Phase 5 (Q-B; not pulled into Phase 3). |
| D2 check behaviour + provenance (3 in `test_cli_check.py`) | 3 | plain assertion failures: bare check on a `[check]`-configured tree still exits 0 (config not read); the stale message is `(stale threshold N)` with no `set in .docs.toml [check] stale_days` / `via --stale` provenance clause. |
| D3 help (1 in `test_body_from.py`) | 1 | assertion: `'first 20 lines' in help_text` — the stale argparse string is still shipped (`...the body's first 20 lines looks like a metadata...`). |
| Version pin (1 in `test_packaging.py`) | 1 | assertion: `version == '1.6.5'` but pyproject still `'1.6.0'` (bumps at Phase 7). |

**GREEN-at-baseline locks (5, all passing — must stay GREEN).**
`test_check_cli_stale_overrides_config` (CLI `--stale 99999` → exit 0;
degenerate today since config is ignored, but the correct post-impl outcome
too); `test_check_no_check_section_unchanged`;
`test_check_stale_zero_honored` (`--stale 0` honoured — exit 1);
`test_list_stale_config_does_not_filter_bare_list`;
`test_list_explicit_stale_unaffected_by_config` (Q6 — `docs list` is not a
config consumer).

**No tracebacks / collection errors / xfails.** The two AttributeError cases
are the accepted, documented Q-B RED (the field is intentionally absent until
Phase 5); every other RED is a clean assertion or an
honest-argparse-then-message-assert failure. The suite is in the exact state
the phase requires.

**Phase-7 follow-through (Q-D, recorded for the wrapper phase).** Only
`test_a3` (`test_a3_project_version_is_1_6_5`) was flipped to 1.6.5. Three
slow build-gated packaging tests still hard-code `1.6.0` and pass against the
stale cached wheel; they are **deliberately left for Phase 7** and must flip
in lockstep when `pyproject.toml` bumps 1.6.0 → 1.6.5 and the built/installed
wheel is refreshed. By exact function name, so Step 2 cannot miss any:

- `test_b1_wheel_builds` (`tests/test_packaging.py:192`) — asserts the wheel
  filename starts `docs_cli-1.6.0-`; flip to `docs_cli-1.6.5-`.
- `test_b2_sdist_builds` (`tests/test_packaging.py:204`) — asserts the sdist
  is `docs_cli-1.6.0.tar.gz`; flip to `docs_cli-1.6.5.tar.gz`.
- `test_c2_docs_version_is_1_6_0` (`tests/test_packaging.py:326`) — asserts
  `docs --version` prints the `1.6.0` token; rename to `..._is_1_6_5` and flip
  the asserted token to `1.6.5`.

(The version-agnostic packaging tests — `test_b3_wheel_contains_cli_and_skill`,
`test_b4_entry_point_recorded_in_wheel` — carry NO version literal and must
stay untouched.) None of the three are part of this step's RED set.

**Exit criteria met.** Every intended-RED test fails for its classified
reason; the 5 GREEN-at-baseline locks pass; the untouched pre-existing suite
(509) stays GREEN; counts captured above.

## Step 1 review fixes (2026-06-12, branch `m19/phases-1-4`)

Fresh-eyes review of Step 1 (phases 1-4) surfaced four contract-tightening
fixes (no operator decisions; all consistent with the binding Decisions) plus
one log-only confirmation. Applied — RED/GREEN membership unchanged
(**still 533 collected, 19 RED, 514 GREEN**; no test added or dropped):

- **Provenance wording pinned to the full frozen parenthetical.** The three
  provenance tests asserted only the trailing substring; the Decision froze
  the whole clause. Strengthened to the exact parenthetical with the concrete
  `N` each tree uses:
  - `test_check_config_sourced_provenance_message`
    (`tests/test_cli_check.py`) → `(stale threshold 30, set in .docs.toml
    [check] stale_days)` (tree's `stale_days=30`).
  - `test_check_cli_sourced_provenance_message` → `(stale threshold 30, via
    --stale)` (the test passes `--stale 30`).
  - `test_touch_check_config_default_provenance` (`tests/test_cli_touch.py`)
    → `(stale threshold 30, set in .docs.toml [check] stale_days)` (tree's
    `[check] stale_days = 30`).
  Each stays RED for its prior reason (assertion / argparse-reject).
- **Provenance mutual exclusion asserted on the config side too.** Added
  `assert "via --stale" not in proc.stdout` to
  `test_check_config_sourced_provenance_message` and
  `test_touch_check_config_default_provenance` (the CLI-sourced test already
  carried the symmetric `set in .docs.toml [check] stale_days` negative).
- **D3 help assertion tightened (nit).**
  `test_new_body_from_help_no_first_20_lines` (`tests/test_body_from.py`)
  weakened the C4-detector check to `"Lifecycle" in help_text or "metadata
  block" in help_text` — satisfiable by the *drifted* string's own "metadata
  block". Narrowed to `assert "Lifecycle" in help_text` (the corrected spec
  wording carries it); the `"first 20 lines" not in help_text` guard is
  unchanged, so the test stays RED until Phase 6 fixes the help string.
- **Short-circuit test made observable (nit).**
  `test_touch_check_touch_failure_short_circuits_check` (`tests/test_cli_touch.py`)
  on a clean tree could not distinguish a true short-circuit from a
  wrongly-run-and-folded check (`max(1, 0) = 1`). Seeded a `broken-ref`
  sibling (`brokenref.md` → unresolved `nonexistent-target.md`) into the
  `_multi_file_tree` root: a wrongly-run check would report `broken-ref` →
  exit 2 (`max(1, 2) = 2`) and surface the target on stdout. Added
  `assert "nonexistent-target.md" not in proc.stdout` and `assert "broken-ref"
  not in proc.stdout` alongside the existing exit-1 + no-INDEX assertions. The
  test stays RED via argparse-reject (`--check` undeclared → exit 2) until
  Phase 5; the new stdout-negatives harden the GREEN behaviour at Phase 8.
- **Phase-7 packaging follow-through made explicit (log-only).** The Phase-4
  follow-through note above now names the three lockstep-flip tests by exact
  function name — `test_b1_wheel_builds`, `test_b2_sdist_builds`,
  `test_c2_docs_version_is_1_6_0` — and calls out that the version-agnostic
  `test_b3`/`test_b4` must stay untouched, so Step 2 cannot miss any.

**Verification.** Affected files re-run: `test_cli_check.py` +
`test_cli_touch.py` + `test_body_from.py` → 16 failed / 47 passed (the same 16
RED as baseline). Full suite → **533 collected, 19 failed (RED), 514 passed**
— membership identical to the Phase-4 baseline. Quality gate (`ruff check`,
`ruff format --check`, `mypy`) clean; `docs check docs/` exit 0; INDEX snapshot
byte-identical.

## Step 2 review fixes (2026-06-12, branch `m19/phases-5-10`)

Fresh-eyes review of Step 2 (phases 5-10) surfaced one should-fix bug + two
nits + one log-only heads-up. The conductor triaged the should-fix as a real
bug and **amended OQ-1** (the original "leniency parity" rationale was
disproved). Applied — **suite rose 533 → 540** (+7: the 5-case parametrized
`resolve_stale` unit test counts as 5, plus 2 new CLI tests); all GREEN:

- **Malformed `[check] stale_days` now refused cleanly (OQ-1 amendment;
  should-fix).** A non-integer `stale_days` (e.g. the TOML string
  `stale_days = "14"`) flowed raw through `resolve_stale` into `check_doc`'s
  `(today - updated).days > stale` comparison and raised an **uncaught
  `TypeError` traceback** (reproduced by the reviewer). The recorded OQ-1
  rationale — leniency parity with `add_roles` — was factually wrong: the
  sibling reads coerce via `frozenset()` / `tuple()` and never crash, whereas
  `stale_days` is stored raw and detonates. Fix in `load_config`
  (`src/docs_cli/cli.py`): a present-but-non-int `stale_days` now raises
  `tomllib.TOMLDecodeError("[check] stale_days must be an integer")`, which
  every caller already catches → **exit 2**, `docs: malformed .docs.toml:
  [check] stale_days must be an integer`. `bool` is excluded explicitly
  (`isinstance(x, int) and not isinstance(x, bool)` — `isinstance(True, int)`
  is True, so `stale_days = true` would otherwise pass). **Negative ints stay
  honoured** (aggressive-but-graceful, `--stale 0` precedent). Pinned by
  `test_check_malformed_stale_days_refused_cleanly` (`tests/test_cli_check.py`:
  exit 2 + message, no `Traceback` / `TypeError` on stderr). OQ-1's Decision
  entry (`m19-post-edit-validation.md`) records the amendment; the refusal
  contract is documented in `convention.md` › *Per-tree `[check]` config* (and
  the bundled `convention.md` ref re-copied byte-identical) + a sentence in the
  CHANGELOG 1.6.5 entry.
- **Config-side `stale_days = 0` lock (nit).** Added
  `test_check_config_stale_days_zero_honored` (`tests/test_cli_check.py`):
  `_stale_config_tree(..., stale_days=0)` flags a >0-day-old active doc → exit
  1, config-sourced provenance `(stale threshold 0, set in .docs.toml [check]
  stale_days)`. The config-side mirror of `test_check_stale_zero_honored`,
  locking `resolve_stale`'s `is not None` (vs truthiness) on the config path.
- **`resolve_stale` precedence unit test (nit).** Added the parametrized
  `test_resolve_stale_precedence` (`tests/test_config.py`, where pure helpers
  are unit-tested): `(None,None)→(None,None)`, `(0,30)→(0,"cli")`,
  `(None,0)→(0,"config")`, `(14,None)→(14,"cli")`, `(None,30)→(30,"config")` —
  CLI `--stale` > `[check] stale_days` > unset, with the `is not None`
  (not truthiness) semantics pinned directly on the helper.
- **Provenance-suffix heads-up (log + CHANGELOG only).** The stale finding's
  message text carries the provenance suffix in both human and `--json` output
  (intended per D2; rule id `stale` / severity `warning` unchanged). Noted in
  the CHANGELOG 1.6.5 entry; no code action.

**Verification.** Full suite → **540 passed** (533 + 7). Quality gate
(`ruff check`, `ruff format --check`, `mypy`) clean; `docs check docs/` exit 0;
bundled `convention.md` ref re-copied byte-identical (`test_skill_refs` GREEN).
