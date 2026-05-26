# M10 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-05-27

Related:
- child-of: m10-adoption-polish.md
- pairs-with: m10-adoption-polish.md
- pairs-with: status.md

## Overview

Chronological log of work on M10 — Adoption-flow polish + 1.3.0 carry-overs. Append a section per phase with objective, files changed, actions, test results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M10 — Adoption-flow polish + 1.3.0 carry-overs
- Started: 2026-05-25
- Progress: **Phase 1 complete (2026-05-25); Phase 2 next, pending operator confirmation of OPEN QUESTIONS A-I in the milestone doc.**

(Note: doc-lifecycle status is in the front-matter `Lifecycle:` field above. This section tracks milestone progress, which is distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-05-25; OQ closeout 2026-05-26 | Milestone pair authored + paired (`Related:` edges both directions); milestone-doc flipped `Lifecycle: draft` → `active`; M10 row added to plan.md (and parked `add_fields` Open question scheduled into M10 item #8); status.md "Current milestone" rewritten + M10 row appended to milestone progress table; OPEN QUESTIONS A-I surfaced for operator review before Phase 2; INDEX + dogfood snapshot regenerated in lockstep; full quality gate green (369 pytest, ruff/format/mypy/`docs check` all clean). **OQ closeout 2026-05-26**: operator-confirmed OQ-A through OQ-I recorded as 9 Decisions bullets in the milestone doc; AWAITING-OPERATOR checkbox flipped in the impl log; INDEX + snapshot regenerated. |
| 2. Write Tests (RED) | Complete | 2026-05-26 | 27 new test items added across `tests/test_cli_touch.py` (5 multi-file/atomic/INDEX-refresh-and-idempotency), `tests/test_cli_migrate.py` (6 `--apply` writes/extends `.docs.toml` + `--quiet` + OQ-G rmdir), `tests/test_check.py` (5 `unknown-field` rule incl. OQ-O Related-never-flagged lock), `tests/test_cli_check.py` (2 CLI `unknown-field`), `tests/test_config.py` (3 `add_fields` schema), `tests/test_migrate.py` (5 `Confidence` enum + 1 `excluded_count` removal). 23 RED + 4 GREEN regression-locks; M9's 369 GREEN preserved (no existing test regressed). Test count: 396 collected (369 + 27). **Review-fix tighten 2026-05-26**: per fresh-eyes review, 4 additional tests added (+1 OQ-G `OSError`-swallow sibling, +1 OQ-O `Archived-reason:` sibling, +1 Pass-4 `_v\d+`-strip Confidence.MEDIUM, +1 `--apply --quiet --summary`/`--json` requested-output coverage) and 6 in-place tightenings (SF1 [exclude]-waiver so no-overwrite body runs; SF2 immediately-above ordering; SF3 exact OQ-F message + path; SF5 content-idempotence over mtime; SF6 stderr success-line token; N3 resolved-project-name pin). Net: 25 RED + 6 GREEN-locks; total 400 collected (369 + 31). |
| 3. Create Data/Fixtures | Complete | 2026-05-26 | No-op per the Phase-3 recommendation in the milestone plan: every Phase-2 test that needed a real tree on disk built it inline via `tmp_path` (multi-file touch trees, vocab trees, OQ-G rmdir tree) so the test files own their setup and Phase 3 had no fixtures to stage. Sign-off folded into the Phase 4 commit. |
| 4. Run Tests (RED Baseline) | Complete | 2026-05-26 | Verbatim baseline captured at `/tmp/m10-phase-4-baseline.txt`: **23 failed, 373 passed (396 collected)**. Per-deliverable attribution table below; every RED traces to an intended unimplemented Phase-5/6 surface (no fixture FNF, no unintended ImportError outside the documented `Confidence` import, no flaky assertion). M9's 369 GREEN baseline preserved + 4 GREEN regression-locks added. Quality gate clean. **Post-review-fix (2026-05-26)**: with 4 added tests + 6 in-place tightenings, the partition is **25 failed, 375 passed (400 collected)** — net +2 REDs (N2 sibling `Archived-reason:`, N6 Pass-4 derived MEDIUM), +2 GREEN-locks (N1 sibling OQ-G `OSError`-swallow, SF7 `--apply --quiet --summary`/`--json` requested-output coverage). M9 369 baseline still GREEN; quality gate still clean. |
| 5. Update Base Interfaces | Complete | 2026-05-27 | `Confidence` enum + `Config.fields` + `MigrationPlan.excluded_count` removal + `touch` `nargs="+"` + `unknown-field` scaffold + `--apply --quiet` plumbed. 16 of the 25 RED tests flipped GREEN by scaffolding; 9 behaviour-side REDs remain for Phase 6 (3 multi-file touch body, 3 `apply_migration` writes, 3 `unknown-field` rule body). Pytest 9F/391P; ruff / ruff format / mypy / `docs check` all clean. M9 369-baseline tests re-expressed against `Confidence.HIGH`/`MEDIUM`/`LOW` enum identity (no test deleted; contract coverage preserved). |
| 6. Implement Offline/Core Path | Pending | — | |
| 7. Update Tool/Wrapper Layer | Pending | — | |
| 8. Run Tests (GREEN) | Pending | — | |
| 9. Implement Online/Integration | Pending | — | |
| 10. Quality, Docs, Refactor | Pending | — | |

## Current state analysis (snapshot at milestone kickoff, 2026-05-25)

_Captured before Phase 2; historical._

- **Codebase (1.3.0 shipped on PyPI 2026-05-25):** `src/docs_cli/cli.py` post-M8; 369 passing tests across 24 files; ruff / format / mypy clean tree-wide; `docs check docs/` exit 0.
- **What M10 inherits:**
  - `_cmd_touch` single-positional; INDEX refresh per call. (Item 1.)
  - `apply_migration` writes metadata blocks but never `.docs.toml`. (Item 2.)
  - `_cmd_migrate --quiet` only suppresses success line, not per-file plan block (M8 simplify deferred). (Item 3.)
  - `infer_role` returns `tuple[str, bool | str]` — `True | "medium" | False` confidence encoding (M7 NIT 1 deferred). (Item 6.)
  - `MigrationPlan.excluded_count: int` set but never read (M8 carry-over). (Item 7.)
  - `[vocabulary] add_fields` allowlist long-parked in plan.md Open questions since M3. (Item 8.)
- **Trial-run evidence:** the M8 fresh-subagent gate's three runs (`kebab-tiny` / `snake-medium` / `snake-large`) each surfaced manual `.docs.toml` authoring and per-file output friction. M10's success is re-running the gate on `kebab-tiny` post-1.4.0 with zero friction.

## Phase 1 — Define Contract (Complete 2026-05-25)

### Objective

Author M10's task plan + this impl log; surface the OPEN QUESTIONS block for operator resolution; defer the active-flip + plan.md/status.md edits until the operator confirms OQs A-I. No code change.

### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/m10-adoption-polish.md` | Create | Task plan, lifecycle `draft` initially; OPEN QUESTIONS A-I surfaced; TDD phase plan filled; deferral list explicit. |
| `docs/m10-adoption-polish-impl.md` | Create | This log. |

_The active-flip on `m10-adoption-polish.md`, the `docs/plan.md` M10 row, and the `docs/status.md` "Current milestone" rewrite are scheduled for the Phase 1 close-out commit AFTER operator confirms the OQ block. Until then, M10's draft sits alongside M9's shipped state without disturbing the published-release narrative._

### Actions taken

- Read every M1-M9 milestone log; consolidated all deferred / follow-on / open items into a single list.
- Confirmed two user-suggested features against current `src/docs_cli/cli.py`:
  - `_cmd_touch` at line 3238 takes a single positional `file`; multi-file is a real gap.
  - `apply_migration` at line 2471 inserts metadata blocks + normalises archives; never writes `.docs.toml`. The M8 adoption playbook Step 3/6 explicitly tells operators to hand-write `[project] name = ...` after `--apply` — this is the largest residual friction the M8 fresh-subagent gate surfaced.
- Drafted M10's scope to bundle the two new features with the M3/M7/M8 carry-overs that share the "adoption-loop friction" theme.
- Surfaced 9 OPEN QUESTIONS (OQ-A through OQ-I) with recommendations.
- Followed the create-milestones playbook Step 2 template; ran `docs new milestone m10-adoption-polish --body-from /tmp/m10-body.md`.

### Issues / decisions

- **Auto-mode scope call.** Per the conversation context, the operator wants M10 created and the OPEN QUESTIONS surfaced — not driven all the way through Phase 1's active-flip in this session. The milestone doc lifecycle stays `draft` until the OQs resolve; the impl log lifecycle is `active` per the M5-M9 pattern (impl logs are immediately active as the place where Phase 1 audit-trail lands).
- **Scope-vs-defer call.** The M10 scope intentionally leaves 16 carry-overs on the cutting-room floor (see Decisions block in the milestone doc). The unifying theme is "items that reduce adoption-loop friction or close long-parked Open questions"; deferred items are either too speculative (LLM-assisted classification), too narrow to justify a milestone slice (M4 mtime snapshot test), or already serviced by existing mechanisms (`add_roles` covers `explainer`/`architecture`).
- **OQ-G — empty `archive-style/` rmdir.** Folded in as a one-line opportunistic addition to `apply_migration` (M4 carry-over); pairs naturally with item #2's `.docs.toml` writer.
- **OQ-I — playbook restructure.** Items #2 (auto `.docs.toml`) and #3 (`--quiet`) collapse the playbook's current 6-step + IMPORTANT-ordering-note shape into a clean 4-step flow. The playbook rewrite is Phase 7 scope, but the restructure intent is recorded here so the Phase 7 author has a concrete target.

### Test results

N/A — Phase 1 has no code change. 369 tests still GREEN (M9 baseline preserved); ruff / format / mypy / `docs check docs/` all clean.

### Exit criteria

- [x] `docs/m10-adoption-polish.md` created via `docs new`; lifecycle flipped `draft` → `active` once pairing landed.
- [x] `docs/m10-adoption-polish-impl.md` created via `docs new`; lifecycle `active`.
- [x] OPEN QUESTIONS block surfaced in milestone doc; 9 items A-I with recommendations.
- [x] `Related:` typed edges in place both directions (milestone `parent-of` log, `child-of` plan.md, `implements` charter.md, `pairs-with` status.md; log `child-of` + `pairs-with` milestone, `pairs-with` status).
- [x] `docs/plan.md` M10 row added; parked `[vocabulary] add_fields` Open question moved to "Scheduled in M10".
- [x] `docs/status.md` "Current milestone" rewritten to point at M10; M10 row appended to the milestone progress table; `Related:` pairs-with extended.
- [x] `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` regenerated in lockstep.
- [x] Quality gate green: pytest 369 passed, ruff / ruff format --check / mypy clean tree-wide, `docs check docs --stale 14` exit 0.
- [x] OPERATOR CONFIRMED 2026-05-26 — OQ-A through OQ-I resolved per recommendations; recorded as Decisions in the milestone doc.

## Phase 2 — Write Tests (RED) (Complete 2026-05-26)

### Objective

Express every M10 deliverable as a failing test on `m10/phases-1-4` before any
implementation lands. Each deliverable maps to a specific contract anchor; the
test names + assertions become the precise target for Phase 5/6.

### Files changed

| File | Action | Notes |
|---|---|---|
| `tests/test_cli_touch.py` | Modify | +5 tests — multi-file happy path, INDEX-refresh-and-idempotency observation (per SF5: pins INDEX content idempotence on a same-day re-touch, not mtime equality; "exactly once" deferred per SF4), atomic-failure body preservation, atomic-failure INDEX preservation, multi-file `--dry-run`. Inline `tmp_path` multi-file tree builder. |
| `tests/test_cli_migrate.py` | Modify | +6 tests — `--apply` writes `.docs.toml` when absent (OQ-A); `--apply` extends sidecar without overwriting `[project]` (OQ-L); `--apply` does NOT overwrite existing `[project]` (OQ-A safety-net); `--apply --quiet` suppresses per-file output (OQ-B); `--quiet` does NOT suppress dry-run/`--summary`/`--json` outputs (OQ-B scope); empty-archive-parent rmdir (OQ-G + OQ-Q). |
| `tests/test_check.py` | Modify | +5 tests — `unknown-field` rule clean-when-no-allowlist (OQ-H); `unknown-field` warning shape (OQ-F); allowlist-match clean (OQ-H); case-sensitivity (OQ-H exact match); OQ-O Related-never-flagged regression-lock. |
| `tests/test_cli_check.py` | Modify | +2 tests — CLI `unknown-field` mismatch exits 1; CLI allowlist-match exits 0. |
| `tests/test_config.py` | Modify | +3 tests — `add_fields` parses into `Config.fields`; default empty frozenset; case preserved verbatim. |
| `tests/test_migrate.py` | Modify | +5 tests — `Confidence` enum identity for HIGH/MEDIUM/LOW returns; `FileMigration.confidence` accepts enum + invariant; JSON wire format still emits strings (regression lock). +1 test — `MigrationPlan.excluded_count` removal (`not hasattr`). |
| `tests/test_cli_touch.py` | Modify (review-fix tighten) | **SF5** swap mtime-equality → content-equality on the second-run pin (the contract is idempotent INDEX bytes, not a content-aware-skip in `_refresh_index`); **N4** cosmetic — annotate the intentional `_c` placeholder on the atomic-failure test. |
| `tests/test_cli_migrate.py` | Modify (review-fix tighten) | **SF1** add `[exclude]` to the pre-existing sidecar so the M8 OQ1 carve-out actually waives the refusal — the no-overwrite body assertions now fire (and the `if proc.returncode == 0:` guard becomes a hard assert); **SF2** tighten OQ-A byte ordering via "split on header → next non-blank line == `[project]`"; **SF6** add stderr "migrated" suppression check to `--apply --quiet`; **SF7** new sibling `test_migrate_apply_quiet_keeps_summary_and_json_outputs` pinning OQ-B "summary/JSON survive `--apply --quiet`"; **N1** new sibling `test_migrate_apply_keeps_archive_parent_with_remaining_siblings` pinning the OQ-G `OSError`-swallow arm; **N3** add `name = "proj"` resolved-name assertion to the absent-sidecar test. |
| `tests/test_check.py` | Modify (review-fix tighten) | **SF3** replace the OQ-F substring checks with an exact `f.message == "metadata field 'Owner:' not in [vocabulary] add_fields allowlist"` + `f.path == doc_path` pin; **N2** new sibling `test_check_doc_archived_reason_is_never_flagged_by_unknown_field` pinning the built-in-allowlist `Archived-reason:` carve-out. |
| `tests/test_migrate.py` | Modify (review-fix tighten) | **N6** new sibling `test_infer_role_confidence_enum_for_medium_via_pass4_non_role_suffix_strip` pinning the Pass-4 `_v\d+`-strip Confidence.MEDIUM path (the existing MEDIUM test exercises Pass-3 `_M\d+` only). |
| `docs/m10-adoption-polish-impl.md` | Modify (N5) | Soften "single-INDEX-refresh observation" narrative to "INDEX-refresh-and-idempotency observation" matching what the test actually pins post-SF5. |

### Actions taken

- Authored the 27 new test items per the planning agent's per-deliverable contract anchors. Each maps 1:1 to a Deliverable in the milestone doc (D1-D6); one additional regression-lock for OQ-O (Related: never flagged) added during the same-instance audit pass.
- Built per-test setup inline via `tmp_path` rather than committing new fixtures (per the Phase 3 recommendation in the planning plan). The multi-file touch tree, the vocab trees for `unknown-field`, and the OQ-G rmdir tree are all constructed from primitives in the test body.
- Used `# type: ignore[call-arg]` ONE place (`tests/test_check.py::_config_with_fields`) to keep mypy clean at the RED baseline while the `fields` kwarg doesn't exist yet on `Config`. The ignore will be removed at Phase 5 once `Config.fields` lands.
- Held the line on identity (`is`) for Confidence enum assertions, not equality — the enum's value matches the existing string literal, so equality would still pass against the pre-enum implementation and not catch the regression.

### Issues / decisions

- **Regression-lock count drift.** The planning agent expected ~24 RED + 2 GREEN regression-locks. Actual at baseline: 23 RED + 4 GREEN regression-locks (the 2 extra GREEN locks are #8 — defensive sidecar-with-`[project]` behavior already locked by current carve-out matrix; and #10 — `--quiet` already not suppressing dry-run/`--summary`/`--json`). Both are intended GREEN-from-baseline locks; the RED count drift (one extra RED, for the audit-added OQ-O Related-never-flagged anchor) is an artefact of the contract being narrower than expected at points where M8 already enforced the behavior + one audit-added regression-lock.
- **`test_check_doc_unknown_field_with_no_allowlist_is_clean` baseline status.** The planning agent expected this test to be GREEN at baseline (an empty allowlist implies "no rule emits, suite is clean"). Actually it is RED at baseline because the test passes `fields=` to `Config(...)`, which TypeErrors today. This is RED for the intended reason — the contract anchor is "once `fields` exists, an empty allowlist must not emit `unknown-field` findings" — Phase 5 lands the kwarg, Phase 6 lands the rule, and both this test + #14 turn GREEN.

### Test results

- pytest (initial Phase 2/4 baseline): **23 failed, 373 passed (396 collected)** — M9's 369 GREEN preserved + 4 new GREEN regression-locks.
- pytest (post-review-fix tighten, 2026-05-26): **25 failed, 375 passed (400 collected)** — net +2 REDs (N2, N6), +2 GREEN-locks (N1 sibling, SF7 sibling). M9's 369 baseline still GREEN.
- ruff / ruff format --check / mypy / `docs check docs --stale 14`: all clean (both baseline and post-review-fix).

### Exit criteria

- [x] 27 new test items collected (initial Phase 2). Post-review-fix tighten: 31 new items (added: N1 sibling, N2 sibling, N6, SF7 sibling).
- [x] 23 RED at baseline / 25 RED post-review-fix — all for intended reasons (no import errors outside documented `Confidence` ImportError; no fixture FNF; every failure traces to a Phase-5/6 deliverable surface).
- [x] 4 GREEN regression-locks at baseline (#8, #10, #17, #25); post-review-fix: 6 (added N1 sibling OQ-G `OSError`-swallow + SF7 sibling `--apply --quiet --summary`/`--json`).
- [x] M9's 369 GREEN preserved.
- [x] Quality gate clean tree-wide.

## Phase 3 — Create Data/Fixtures (No-op, signed off with Phase 4)

Per the planning agent's Phase 3 recommendation: every M10 RED test that
needs a multi-file tree on disk builds it inline via `tmp_path` (the
multi-file `touch` tree builder, the `[vocabulary] add_fields` vocab
trees, the OQ-G rmdir tree). No new on-disk fixtures landed for M10.

This is a deliberate choice over staging new `tests/fixtures/` subdirs:

- The contract anchors are tiny (2–3 files per scenario) and self-explanatory
  in the test bodies.
- Inline construction keeps the per-test setup honest about exactly what
  goes into the tree (especially for the rmdir test, where the OQ-Q
  blast-radius guard is exact-control of the parent-dir contents).
- No sanitisation-grep risk; nothing to commit; nothing to maintain.

## Phase 4 — Run Tests (RED Baseline) (Complete 2026-05-26)

### Objective

Capture the verbatim RED baseline before any implementation. Confirm
every new RED traces to its intended unimplemented Phase-5/6 surface;
surface the 4 GREEN-at-baseline regression-locks; pin M9's 369 GREEN
baseline + the full quality gate.

### Verbatim pytest output

```text
$ .venv/bin/python -m pytest -q tests/
... (396 items collected) ...
23 failed, 373 passed in 10.80s
```

Captured verbatim at `/tmp/m10-phase-4-baseline.txt`.

### Per-deliverable attribution table

| Deliverable | Source file(s) | RED count | GREEN-at-baseline (regression-lock) | Failure mode → root cause |
|---|---|---:|---:|---|
| D1 — `docs touch` multi-file + atomic + single-INDEX | `test_cli_touch.py` | 5 | 0 | argparse rejects positional `nargs="+"` today (single `file` only); rest of contract follows once nargs lands. |
| D2 — `migrate --apply` writes/extends `.docs.toml` + `--quiet` + OQ-G rmdir | `test_cli_migrate.py` | 4 | 2 | `apply_migration` never writes `.docs.toml`; `--quiet` only suppresses success line (not per-file plan); `archived/` parent never `rmdir`'d. Locks: #8 (existing `[project]` not overwritten — refused today by carve-out matrix); #10 (`--quiet` doesn't touch dry-run/`--summary`/`--json` today — desired contract). |
| D3 — `unknown-field` rule (unit) | `test_check.py` | 5 | 0 | `Config` has no `fields` kwarg → TypeError at construction time (#13, #14, #15, audit-add OQ-O lock); the rule itself does not exist (#12 also TypeErrors). All five turn GREEN once Phase 5 lands `Config.fields` + Phase 6 wires the rule. |
| D3 — `unknown-field` rule (CLI) | `test_cli_check.py` | 1 | 1 | CLI mismatch test exits 0 today (no rule emits the warning). Lock: #17 (allowlist-match → exit 0 trivially today). |
| D4 — `Config.fields` + `add_fields` TOML | `test_config.py` | 3 | 0 | `Config` instance has no `fields` attribute → AttributeError; `load_config` doesn't read `add_fields` from `[vocabulary]`. |
| D5 — `Confidence` enum | `test_migrate.py` | 4 | 1 | `from docs import Confidence` raises ImportError → 4 enum-identity tests fail at import; identity assertions (`is Confidence.X`) are the intended target. Lock: #25 (JSON wire format strings — already strings today, stays GREEN after the enum lands via `enum.value`). |
| D6 — `MigrationPlan.excluded_count` removal | `test_migrate.py` | 1 | 0 | `hasattr(plan, "excluded_count") == True` today; Phase 5 removes the field. |
| **TOTAL** |  | **23** | **4** | — |

Function totals: 5 + 6 + 5 + 2 + 3 + 5 + 1 = 27 new test functions / 27 collected items
(none parametrised). 23 RED + 4 GREEN regression-locks.

### Review-fix delta (2026-05-26)

A fresh-eyes review of Phases 1-4 surfaced 6 in-place test tightenings
(SF1-SF3, SF5-SF7) and 3 contract-coverage additions (N1 sibling, N2
sibling, N6 Pass-4 derived MEDIUM). SF4 (the "exactly once" INDEX-refresh
pin) is deferred to the Phase 9 dogfood per reviewer judgment; N4 is
cosmetic (kept in-place with an explanatory comment); N5 softens this
log's narrative ("INDEX-refresh-and-idempotency" replaces
"single-INDEX-refresh observation").

Post-review pytest partition (verbatim):

```text
$ .venv/bin/python -m pytest -q tests/ --tb=no
... (400 items collected) ...
25 failed, 375 passed in 10.82s
```

Per-deliverable delta:

| Deliverable | RED Δ | GREEN-lock Δ | Notes |
|---|---:|---:|---|
| D1 — `docs touch` | 0 | 0 | SF5 swap (mtime→content idempotence) keeps the RED; N4 cosmetic only. |
| D2 — `migrate --apply` | 0 | +2 | N1 sibling OQ-G `OSError`-swallow (GREEN-lock: impl doesn't rmdir today, so the sibling-survives invariant holds vacuously); SF7 new `test_migrate_apply_quiet_keeps_summary_and_json_outputs` (GREEN-lock: today's `_print_migration_plan` ignores `args.quiet`, so summary/JSON already land). SF1 (now GREEN-lock with [exclude]-waiver), SF2 (tightened ordering), SF6 (added stderr-token check) all still RED for the same root cause. N3 (resolved name pin) still RED for the same root cause. |
| D3 — `unknown-field` (unit) | +1 | 0 | N2 sibling `Archived-reason:` RED at baseline via `Config.fields` TypeError — flips GREEN once Phase 5 lands the kwarg. SF3 tightens existing #13 to exact message + path; still RED for the same root cause. |
| D5 — `Confidence` enum | +1 | 0 | N6 Pass-4 derived MEDIUM RED via `ImportError: Confidence` — flips GREEN once Phase 5 lands the enum. |
| **TOTAL Δ** | **+2** | **+2** | 25 RED + 6 GREEN-locks; 31 total new items. |

### Quality gate (verbatim)

```text
$ .venv/bin/ruff check .
All checks passed!

$ .venv/bin/ruff format --check .
33 files already formatted

$ .venv/bin/mypy
Success: no issues found in 34 source files

$ .venv/bin/docs check docs --stale 14
docs: no violations found
```

### Attestation — no RED-for-wrong-reason

Every RED test was inspected via `--tb=line` against
`/tmp/m10-phase-4-baseline.txt`:

- **No `FileNotFoundError`** / no fixture-not-found failures. Every
  test that needed an on-disk tree built it inline via `tmp_path`;
  the only on-disk fixture path consulted is `tests/fixtures/trees/foreign/`
  (already staged at M4), used by the JSON wire-format regression lock.
- **One intended `ImportError`** — `from docs import Confidence` —
  scoped to the 4 D5 enum-identity tests. Phase 5 lands the enum at
  module scope and converts those to assertion REDs (the enum-identity
  contract becomes the actual surface). The 5th D5 test
  (`test_filemigration_confidence_field_accepts_enum`) also triggers
  this ImportError at function scope; it'll flip the same way.
- **TypeError / AttributeError on `Config.fields`** is the intended
  RED surface for D3 + D4 — `Config` doesn't yet accept / expose
  `fields`. Phase 5 lands the kwarg + attribute, then the assertion
  contracts become the real RED.
- **argparse "unrecognized arguments" on `docs touch a b c`** is the
  intended D1 RED — `nargs="+"` not wired today.
- **`apply_migration` behavioural REDs** (no `.docs.toml` written, no
  rmdir, `--quiet` still emits per-file output) all hit assertion
  failures naming the exact contract Phase 6 will satisfy.
- **No flaky / time-sensitive assertion** — date-relative checks
  use `date.today().isoformat()` which is stable within a test run.

The 23 REDs partition cleanly: 5 D1 + 4 D2 + 5 D3-unit + 1 D3-CLI +
3 D4 + 4 D5 + 1 D6 = 23 (matches the attribution table); the 4
baseline-GREEN regression locks are pinned in the same table.

### Exit criteria

- [x] Verbatim RED baseline captured at `/tmp/m10-phase-4-baseline.txt`.
- [x] Per-deliverable attribution table written (mirrors the M8 Phase 4
      pattern at `docs/m8-adoption-workflow-log.md`).
- [x] Quality gate clean tree-wide: pytest 22F/373P, ruff / ruff format /
      mypy / `docs check docs --stale 14` all clean.
- [x] Attestation that no RED is for the wrong reason.
- [x] Tests #12 (with-no-allowlist clean), #25 (JSON wire format strings),
      and #26 (`hasattr` removal) baseline status confirmed: #12 is RED
      at baseline (TypeError on `fields=`) — intended for #12 to flip
      to GREEN once Phase 5 lands the kwarg; #25 already GREEN
      (regression-lock); #26 RED (the field exists today). Planning
      agent's "possibly #26" guess was inverted — RED at baseline,
      GREEN after Phase 5 removal.

## Phase 5 — Update Base Interfaces (Complete 2026-05-27)

### Objective

Land the M10 schema + argparse scaffolding so the Phase-2 REDs that
trace to interface gaps flip green by construction, leaving only the
behaviour-side REDs (multi-file atomic touch, `.docs.toml` writer,
`--apply --quiet` suppression body, `unknown-field` rule body) for
Phase 6.

### Files changed

| File | Action | Notes |
|---|---|---|
| `src/docs_cli/cli.py` | Modify | Add `import enum`; introduce `Confidence(enum.Enum)` with `HIGH`/`MEDIUM`/`LOW` string values that match the JSON wire format (`enum.value`); introduce `_BUILTIN_METADATA_FIELDS = frozenset({"Lifecycle","Role","Project","Updated","Related","Archived-reason"})` (OQ-O + OQ-P); add `Config.fields: frozenset[str] = frozenset()` with case-sensitive docstring (OQ-H); thread `fields = frozenset(vocab_section.get("add_fields", []))` through `load_config`; retype `FileMigration.confidence: Confidence` + rewrite `__post_init__` per OQ-N (isinstance check; LOW requires non-empty ambiguities; HIGH/MEDIUM require empty); drop `MigrationPlan.excluded_count` + local counter; retype `infer_role -> tuple[str, Confidence]` and replace tri-value literals (`True | "medium" | False`) with `Confidence.HIGH/MEDIUM/LOW` at every call site (inference passes, plan_migration tri-value dispatch + notes-fallback-medium upgrade + collision pass); cross enum→string at JSON boundary in `migration_to_json` via `fm.confidence.value`; rewrite `_print_migration_plan`'s `confidence_counts` to `dict[Confidence, int]` + stringify for display; add `quiet: bool = False` kwarg with early-return at the top of `_print_migration_plan`; rewrite `_cmd_migrate` dispatch matrix to thread `quiet=(args.apply and args.quiet)` only into the default branch (JSON / summary are requested outputs); switch `touch_p` argparse to `nargs="+"` + update help/description; scaffold `_cmd_touch` to read `args.files[0]` (Phase 6 rewrites the full multi-file flow). |
| `tests/_typing/docs.pyi` | Modify | Re-export `Confidence as Confidence` so mypy sees it. |
| `tests/test_check.py` | Modify | Remove the `# type: ignore[call-arg]` in `_config_with_fields` now that `Config.fields` exists. |
| `tests/test_migrate.py` | Modify | Update existing M9 infer_role tests + plan_migration confidence assertions from bool/string tri-value to `Confidence` enum identity comparisons (`is Confidence.HIGH` etc.). Add `Confidence` import. |
| `tests/test_inference.py` | Modify | Convert `_CONFIDENCE_OK` from `("medium","high",True)` strings to `(Confidence.HIGH, Confidence.MEDIUM)` enum tuple; convert every `== "medium"`, `in ("low", False)` assertion to enum identity. Add `Confidence` import. |
| `tests/test_lifecycle_rename.py` | Modify | `test_file_migration_accepts_medium_confidence` now constructs with `Confidence.MEDIUM` + asserts `is Confidence.MEDIUM`. |

### Actions taken

- Audited every Phase-2 RED test for the "scaffolding-flips" attribution
  in the planning plan; confirmed the partial-GREEN target (16 RED →
  GREEN by Phase 5 scaffolding; 9 RED remain for Phase 6).
- Updated the M9-baseline `infer_role` + `plan_migration` tests that
  asserted on the legacy `bool | str` tri-value confidence. The change
  is forced by the OQ-E enum replacement: those tests still pin the
  same semantics, just expressed against the new return type. The
  M9 GREEN baseline (369 tests) was preserved through the rewrite —
  no test was deleted or weakened, only re-expressed.
- Kept the `_print_migration_plan(quiet=False)` body untouched in
  every other respect — only the early-return guard at the top is new
  scaffolding. Phase 6 lands the dispatch matrix in `_cmd_migrate`
  that actually computes `quiet=True` from the args.
- `Confidence` is now exported from `docs_cli.cli` directly; the
  `pyi` re-export keeps mypy happy. The runtime import works from
  `from docs import Confidence` through the conftest `sys.modules`
  alias and from `from docs_cli.cli import Confidence` directly.

### Issues / decisions

- **Existing M9 tests forced an update.** The planning agent noted
  "M9 baseline + several Phase-2 GREENs flip green by scaffolding".
  Strictly, 30+ existing tests asserted on the `bool | str` tri-value
  shape of `infer_role`'s second return — those are testing the
  contract Phase 5 just rewrote. The choice is: weaken the existing
  tests (lose contract coverage) OR retarget them at the enum
  (preserve coverage at the new shape). I chose retargeting. The
  edits are mechanical (`is True` → `is Confidence.HIGH`; `is False`
  → `is Confidence.LOW`; `== "medium"` → `is Confidence.MEDIUM`).
- **`infer_lifecycle` / `infer_updated` kept their `bool` returns.**
  Their tests still assert `is True/False`. The OQ-E enum replacement
  is scoped to `infer_role` (the only inference call site that has
  a three-level confidence; the other two only need a binary
  "confident vs. fell-back" signal). No regression.

### Test results

After Phase 5:

```text
$ .venv/bin/python -m pytest tests/ -q --tb=no
... (400 items collected) ...
9 failed, 391 passed in 10.80s
```

Failing tests (intentional — all Phase 6 behaviour-side surfaces):

- `tests/test_cli_touch.py::test_touch_multi_file_bumps_all_three_to_today` — multi-file atomic body not written yet.
- `tests/test_cli_touch.py::test_touch_atomic_failure_leaves_every_file_unchanged` — atomic validate-all-first not implemented yet.
- `tests/test_cli_touch.py::test_touch_atomic_failure_does_not_write_index` — same.
- `tests/test_cli_migrate.py::test_migrate_apply_writes_docs_toml_when_absent` — `_ensure_docs_toml` writer not implemented yet.
- `tests/test_cli_migrate.py::test_migrate_apply_extends_sidecar_without_overwriting_project` — same writer not extending sidecar yet.
- `tests/test_cli_migrate.py::test_migrate_apply_removes_empty_archive_parent_directory` — `_opportunistic_rmdir` not implemented yet.
- `tests/test_check.py::test_check_doc_unknown_field_warning_when_allowlist_set` — `unknown-field` rule body not implemented yet.
- `tests/test_check.py::test_check_doc_allowlist_is_case_sensitive` — same.
- `tests/test_cli_check.py::test_check_cli_unknown_field_exits_1` — same.

Net Phase 5 scaffolding flips: 25 RED → 9 RED (16 flipped to GREEN).
M9 369 baseline preserved (re-expressed; no contract weakened).

### Quality gate (verbatim)

```text
$ .venv/bin/ruff check .
All checks passed!

$ .venv/bin/ruff format --check .
33 files already formatted

$ .venv/bin/mypy
Success: no issues found in 34 source files

$ .venv/bin/docs check docs --stale 14
docs: no violations found
```

### Exit criteria

- [x] `Confidence(enum.Enum)` lands with HIGH/MEDIUM/LOW string values matching JSON wire format.
- [x] `Config.fields: frozenset[str] = frozenset()` field added; `load_config` reads `[vocabulary] add_fields` into it.
- [x] `MigrationPlan.excluded_count` removed (field + local counter + constructor).
- [x] `FileMigration.confidence: Confidence` + validator rewritten per OQ-N.
- [x] `infer_role` retypes to `tuple[str, Confidence]`; every tri-value call site uses the enum.
- [x] `migration_to_json` crosses enum→string at the JSON boundary via `fm.confidence.value` — JSON wire format byte-stable.
- [x] `_print_migration_plan` accepts `quiet: bool = False`; early-return guards the body; `_cmd_migrate` dispatch threads quiet only into the default branch.
- [x] `touch` argparse `nargs="+"`; `_cmd_touch` scaffolded to `args.files[0]`.
- [x] `tests/_typing/docs.pyi` re-exports `Confidence`.
- [x] `# type: ignore[call-arg]` removed from `tests/test_check.py`.
- [x] M9 369-baseline tests re-expressed against the enum; no contract weakened.
- [x] Quality gate clean tree-wide; 9 RED remain for Phase 6 (all behaviour-side).
