# M10 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-05-27

Related:
- child-of: archive/2026-05-27/m10-adoption-polish.md
- pairs-with: archive/2026-05-27/m10-adoption-polish.md
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
| 6. Implement Offline/Core Path | Complete | 2026-05-27 | `_cmd_touch` rewritten with atomic multi-file semantics + single-root sanity check + single end-of-batch INDEX refresh; `apply_migration` augmented with `_opportunistic_rmdir` (post-move) + `_ensure_docs_toml` (post-file-loop); `check_doc` `unknown-field` rule lands as opt-in (fires only when `config.fields` is non-empty). 400/400 GREEN; quality gate clean tree-wide. |
| 7. Update Tool/Wrapper Layer | Complete | 2026-05-27 | Spec sweep across cli.md / convention.md / architecture.md / README.md / CHANGELOG.md + adoption-playbook restructure (OQ-I, 4 steps) + skill-references resync (byte-equal); 1.3.0 → 1.4.0 bump in pyproject.toml, `__version__`, `tests/test_packaging.py`. Wheel + sdist built at 1.4.0; twine check PASSED. 400/400 GREEN; quality gate clean tree-wide. |
| 8. Run Tests (GREEN) | Complete | 2026-05-27 | Verbatim GREEN gate at `/tmp/m10-phase-8-green.txt`: 400 passed (pytest), ruff / ruff format / mypy / `docs check docs --stale 14` clean, `docs --version` prints `docs 1.4.0`, `twine check` PASSED on `dist/docs_cli-1.4.0-{py3-none-any.whl,tar.gz}`. |
| 9. Implement Online/Integration | Complete | 2026-05-27 | kebab-tiny dogfood PASS — 1.4.0 wheel installed in /tmp/docs-m10-venv; adoption playbook (Plan → Apply → Verify, Step 2 triage skipped on a clean plan) reads end-to-end with `--apply --quiet` truly silent (empty stdout AND empty stderr) + auto-emitted `.docs.toml` (OQ-A) + `docs check` exit 0 immediately. Adopted-state fixture updated in lockstep for the M10 auto-emitted shape (`[archive] date_format` block + provenance header). |
| 10. Quality, Docs, Refactor | Complete | 2026-05-27 | Closeout. CHANGELOG dated; milestone-completion summary on milestone doc; status.md + plan.md M10 → Complete; dist/ rebuilt from closeout state + twine check PASS; milestone doc archived (impl log stays active per M8/M9 pattern). Publish deferred to M11. |

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

## Phase 6 — Implement Offline/Core Path (Complete 2026-05-27)

### Objective

Write the business-logic body for every Phase-5-scaffolded surface so
the suite reaches 400/400 GREEN. No new public surface added — only
the bodies behind the Phase-5 schema land here.

### Files changed

| File | Action | Notes |
|---|---|---|
| `src/docs_cli/cli.py` | Modify | Rewrite `_cmd_touch` per OQ-C atomic semantics (validate every path is a real file, then validate every path resolves under the same docs root, then build every rewrite in memory catching `MetadataError` before any write, then write atomically + a single end-of-batch `_refresh_index`; named-bad-path messaging on each fail). Add `_DOCS_TOML_HEADER` module-level constant for the OQ-A provenance comment. Add `_opportunistic_rmdir(old_parent, root)` with the OQ-Q safety guards (never the plan root; never under the conformant `archive/` subtree; swallow `OSError` for the ENOTEMPTY-sibling-arm via `contextlib.suppress`). Add `_ensure_docs_toml(plan)` per OQ-A — absent sidecar gets a minimal `[project] name = "<resolved>"` + `[archive] date_format` (OQ-M: no `dir =` line); existing sidecar with `[project]` is a no-op; existing sidecar without `[project]` gets the new block appended at the bottom under the provenance header with separator logic guaranteeing exactly one blank line. Rewrite `apply_migration` to capture `old_parent` BEFORE the archive-move, call `_opportunistic_rmdir(old_parent, plan.root)` AFTER, and call `_ensure_docs_toml(plan)` after the file loop. Implement the `check_doc` `unknown-field` rule: opt-in (fires only when `config.fields` is non-empty); `allowed = _BUILTIN_METADATA_FIELDS | config.fields`; emits a `warning` `Finding` with the OQ-F exact message shape for every label not on the allowed set. |

### Actions taken

- Authored `_cmd_touch`, `_opportunistic_rmdir`, `_ensure_docs_toml`,
  `apply_migration` overhaul, and `check_doc` `unknown-field` rule
  per the planning agent's 6.1-6.4 spec exactly.
- Discovered + fixed an opt-in semantic delta in 6.4: the planning
  agent's example body emits a finding for every non-allowed label,
  but the OQ-H + milestone-doc Deliverable wording is "trees without
  the section see no change" — the rule must NOT fire when
  `config.fields` is empty (the "no allowlist" GREEN regression-
  lock #12 pins this). Gated the rule behind `if config.fields:` —
  flipped both #12 and the M9-baseline
  `test_check_accepts_lifecycle_with_freeform_status_line` to
  GREEN (the latter relied on `Status:` being opaque to checks
  when no `add_fields` is configured).
- The `_ensure_docs_toml` resolved-project-name pin uses
  `plan.files[0].project` (which is the plan's `project` — already
  normalised + override-aware per F11). Falls back to
  `plan.root.resolve().name` only on a zero-file plan (the
  degenerate "no .md files to migrate" case).

### Issues / decisions

- **`unknown-field` rule is opt-in, not opt-out.** Per the milestone
  doc wording "Trees without the section see no change" and the
  Phase-2 test contract `test_check_doc_unknown_field_with_no_allowlist_is_clean`,
  the rule is gated on `config.fields` being non-empty. This is
  also what kept the M9-baseline `Status:`-as-prose test GREEN
  through the rule landing.
- **OQ-Q swallow gates.** `_opportunistic_rmdir`'s two early-return
  guards (root identity + already-under-`archive/`) are above the
  OSError-swallow so the ENOTEMPTY-sibling test's `archived/`
  parent survives even on systems where `Path.rmdir` quirks
  differ — the OSError catch is the third gate, not the only one.

### Test results

```text
$ .venv/bin/python -m pytest tests/ -q --tb=no
... (400 items collected) ...
400 passed in 10.99s
```

Every Phase-2 RED now GREEN; every M9 baseline test still GREEN.

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

- [x] `_cmd_touch` atomic multi-file body lands with OQ-C semantics + single-root sanity check (Step-2 follow-on #4).
- [x] `_ensure_docs_toml` writes when absent + extends when present + never overwrites `[project]` (OQ-A) + emits no `dir =` line (OQ-M) + uses provenance header immediately above `[project]` (OQ-L).
- [x] `_opportunistic_rmdir` runs after every archive-move; never tree-walks; swallows `OSError` on a non-empty parent (OQ-G + OQ-Q).
- [x] `_print_migration_plan(quiet=True)` early-returns; `_cmd_migrate` dispatch wires `quiet=(args.apply and args.quiet)` only on the default branch.
- [x] `check_doc` `unknown-field` rule fires only when `config.fields` is non-empty; emits the OQ-F exact-message shape; built-in always-allowed set + `add_fields` allowlist cover the expected vocabulary.
- [x] 400/400 GREEN; quality gate clean tree-wide.

## Phase 7 — Update Tool/Wrapper Layer (Complete 2026-05-27)

### Objective

Spec sweep + 1.4.0 version bump + adoption-playbook restructure
(OQ-I) + skill-references resync + CHANGELOG entry. The shipped
test suite stays at 400/400 GREEN; the packaging tests now pin
1.4.0 (full wheel rebuild required because of the version bump).

### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/cli.md` | Modify | Rename `docs touch <file>` heading to `docs touch <file>...`; rewrite body for multi-file + atomic + single-INDEX-refresh + multi-root sanity check; extend `docs migrate --apply` bullet to call out the `.docs.toml` write (OQ-A) + opportunistic-rmdir (OQ-G); add `--apply --quiet` paragraph (OQ-B); add `unknown-field` row to `docs check` rule list + JSON schema rule-id table; bump `Updated:`. |
| `docs/convention.md` | Modify | Add `add_fields = ["Owner", "Tags"]` to the `[vocabulary]` TOML example; document case-sensitive exact match + the built-in always-allowed set + the opt-in semantic; add the scope-narrowness sentence (Step-2 follow-on #2). Bump `Updated:`. |
| `docs/architecture.md` | Modify | Mention `apply_migration`'s `.docs.toml` writer + opportunistic-rmdir; update the `FileMigration.confidence` annotation to `Confidence`; drop `MigrationPlan.excluded_count` from the field list; add `Config.fields`. Update the package-tree dunder version to 1.4.0. Bump `Updated:`. |
| `pyproject.toml` | Modify | `version = "1.4.0"`. |
| `src/docs_cli/cli.py` | Modify | `__version__ = "1.4.0"`. |
| `tests/test_packaging.py` | Modify | Bump all 1.3.0 pins to 1.4.0 (A3 project-version assert; B1/B2 wheel/sdist filename pins; C2 CLI `--version` token). |
| `src/docs_cli/skill/references/adoption-playbook.md` | Rewrite | OQ-I restructure to 4 steps (plan / triage / apply / verify); drop the three-pattern ordering note; drop the manual `.docs.toml` authoring step (`--apply` writes it now); worked example uses `--apply --quiet` and immediately runs `docs check`. Bump `Updated:`. |
| `src/docs_cli/skill/references/cli.md` | Sync | `cp docs/cli.md` — byte-equal mirror (enforced by `tests/test_skill_refs.py`). |
| `src/docs_cli/skill/references/convention.md` | Sync | `cp docs/convention.md` — byte-equal mirror. |
| `README.md` | Modify | Bump version mentions; add M10 milestone row to the Status section. |
| `CHANGELOG.md` | Modify | Insert `## 1.4.0 — UNRELEASED` with Added / Changed / Notes structure per the planning plan. |
| `docs/plan.md` | Modify | Flip M10 row to "Phases 1-7 complete 2026-05-27; 400/400 GREEN at 1.4.0; Phase 8 next". Bump `Updated:`. |
| `tests/test_skill_adoption.py` | Modify | Drop the `## Step 5` / `## Step 6` required-headings entries to match the M10 4-step restructure. |
| `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Lockstep refresh after the doc bumps. |
| `dist/docs_cli-1.4.0-py3-none-any.whl` + `dist/docs_cli-1.4.0.tar.gz` | Build | `python -m build` produced both artefacts; `twine check` PASSED on both. The 1.3.0 wheel + sdist remain in `dist/` from M9 (no cleanup needed; M11 will rebuild from the closeout-commit state anyway). |

### Actions taken

- Authored the new `docs touch <file>...` section in cli.md with
  the OQ-C atomic semantics + the multi-root sanity check
  (Step-2 follow-on #4). The "M11+ work" note in the playbook /
  cli.md draws the scope boundary explicitly.
- Restructured the adoption playbook to 4 steps. Eliminated the
  Step 3 three-pattern ordering note (Step 3 in the new
  numbering is now just "Apply"); the worked example reads
  end-to-end with `--apply --quiet` followed by `docs check`.
  Added a `Since 1.4 (M10)` callout at the top explaining the
  new `--apply` behaviour for operators familiar with the M8
  playbook.
- Re-ran `cp` on `cli.md` + `convention.md` into the bundled
  skill references; `tests/test_skill_refs.py` (2 tests) passes
  byte-equality.
- Bumped the test_skill_adoption.py expectations: it pinned the
  6-step playbook shape, which was the M8 surface; the M10 OQ-I
  restructure necessarily updates that contract.
- Built 1.4.0 wheel + sdist via `python -m build`; both
  artefacts pass `twine check`. The 1.4.0 wheel/sdist sit
  alongside the 1.3.0 release artefacts in `dist/`.
- Verified `docs --version` prints `docs 1.4.0` after the
  in-tree version bump (no wheel-install indirection needed
  for this check).

### Issues / decisions

- **Adoption-playbook 4-step restructure necessarily updates
  the test contract.** `tests/test_skill_adoption.py` pinned
  `## Step 1` through `## Step 6`; OQ-I drops to 4 steps. The
  test now pins steps 1-4 only; the M8 6-step contract is
  retired as M10 ships.
- **`README.md` adds an M10 row + flips the lead sentence**
  from "docs-cli 1.3.0 shipped 2026-05-25" to "**docs-cli 1.4.0
  is ready locally** (M10 adoption-flow polish); the M11
  publish milestone will lift it onto PyPI." The 1.3.0
  shipped-on-PyPI line stays as historical context.
- **CHANGELOG `## 1.4.0 — UNRELEASED`** uses the Phase-10-dated
  closeout pattern from M8/M9. Phase 10 dates the heading.

### Test results

```text
$ .venv/bin/python -m pytest tests/ -q --tb=no
... (400 items collected) ...
400 passed in 10.82s
```

`tests/test_packaging.py` (25 tests, includes wheel rebuild +
twine check on the in-tree 1.4.0 build) is fully GREEN.
`tests/test_skill_refs.py` (2 tests) confirms byte-equality.

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

$ .venv/bin/docs --version
docs 1.4.0

$ .venv/bin/python -m twine check dist/docs_cli-1.4.0-py3-none-any.whl dist/docs_cli-1.4.0.tar.gz
Checking dist/docs_cli-1.4.0-py3-none-any.whl: PASSED
Checking dist/docs_cli-1.4.0.tar.gz: PASSED
```

### Exit criteria

- [x] All 400 pytest tests GREEN at 1.4.0.
- [x] ruff / ruff format / mypy / `docs check docs --stale 14` clean tree-wide.
- [x] `docs --version` prints `docs 1.4.0`.
- [x] Skill references at `src/docs_cli/skill/references/{cli,convention}.md` byte-equal to source via `tests/test_skill_refs.py`.
- [x] Adoption playbook restructured to 4 steps per OQ-I.
- [x] `pyproject.toml` + `__version__` at 1.4.0; `dist/docs_cli-1.4.0-*` artefacts built; `twine check` PASSED.
- [x] `CHANGELOG.md` `## 1.4.0 — UNRELEASED` block landed.

## Phase 8 — Run Tests (GREEN gate captured) (Complete 2026-05-27)

### Objective

Verbatim capture of the full M10 GREEN gate at
`/tmp/m10-phase-8-green.txt`: pytest, ruff, ruff format --check,
mypy, `docs check`, `docs index --dry-run`, `docs --version`,
wheel/sdist build state, `twine check`.

### Verbatim output (excerpt)

```text
=== pytest -q tests/ ===
... (400 items, no failures) ...
400 passed in 10.91s

=== ruff check . ===
All checks passed!

=== ruff format --check . ===
33 files already formatted

=== mypy ===
Success: no issues found in 34 source files

=== docs check docs --stale 14 ===
docs: no violations found

=== docs index --root docs/ --dry-run ===
# docs — Documentation
...
<!-- docs:generated start -->
_Generated 2026-05-27. 31 docs active, 0 archived._
...

=== docs --version ===
docs 1.4.0

=== twine check (1.4.0 wheel + sdist) ===
Checking dist/docs_cli-1.4.0-py3-none-any.whl: PASSED
Checking dist/docs_cli-1.4.0.tar.gz: PASSED
```

Full log at `/tmp/m10-phase-8-green.txt`.

### Test results

- pytest: **400 passed, 0 failed (400 collected)** — full M10
  contract surface GREEN at 1.4.0.
- ruff: all checks passed.
- ruff format --check: 33 files already formatted.
- mypy: clean (34 source files).
- `docs check docs --stale 14`: clean (no violations).
- `docs index --root docs/ --dry-run`: regenerates cleanly
  (31 docs active, 0 archived; matches the in-tree
  `docs/INDEX.md` byte-for-byte through the dogfood snapshot
  at `tests/fixtures/expected/docs-INDEX.md`).
- `docs --version`: `docs 1.4.0`.
- `twine check` on both `dist/docs_cli-1.4.0-py3-none-any.whl`
  and `dist/docs_cli-1.4.0.tar.gz`: PASSED.

### Exit criteria

- [x] Verbatim GREEN gate captured at `/tmp/m10-phase-8-green.txt`.
- [x] 400/400 pytest GREEN at 1.4.0.
- [x] ruff / ruff format --check / mypy / `docs check` clean tree-wide.
- [x] `docs --version` prints `docs 1.4.0`.
- [x] `dist/docs_cli-1.4.0-*` built locally; `twine check` PASSED on both artefacts.

## Phase 9 — Implement Online/Integration (kebab-tiny dogfood) (Complete 2026-05-27)

### Objective

Re-run the M8 fresh-subagent gate's kebab-tiny scenario against
the freshly-built 1.4.0 wheel. Confirm the adoption playbook
reads end-to-end with zero manual operator action — empty
`--apply --quiet` output AND auto-emitted `.docs.toml` AND
`docs check` exit 0 AND single INDEX regen.

### Actions taken

Per the M8 precedent at `docs/m8-adoption-workflow-log.md`,
Phase 9 cannot spawn a fresh Agent — same-instance role-play
runs the playbook end-to-end:

```text
$ rm -rf /tmp/docs-m10-venv /tmp/m10-dogfood
$ /home/user/opt/docs-cli/.venv/bin/python -m venv /tmp/docs-m10-venv
$ /tmp/docs-m10-venv/bin/pip install --quiet \
    /home/user/opt/docs-cli/dist/docs_cli-1.4.0-py3-none-any.whl
$ /tmp/docs-m10-venv/bin/docs --version
docs 1.4.0

$ cp -r tests/fixtures/trees/real-trees/kebab-tiny /tmp/m10-dogfood
$ ls /tmp/m10-dogfood/
foo-bar-plan.md  foo-bar-spec.md  foo-bar-status.md

# Step 1 — Plan
$ /tmp/docs-m10-venv/bin/docs migrate /tmp/m10-dogfood
foo-bar-plan.md
  role: plan    project: foo-bar    lifecycle: active
  updated: 2026-05-27    confidence: high
... (3 files; all high-confidence; ambiguities: none)

# Step 2 — Triage: skipped (clean plan).

# Step 3 — Apply
$ /tmp/docs-m10-venv/bin/docs migrate /tmp/m10-dogfood --apply --quiet
$ echo $?
0
# stdout: (empty), stderr: (empty)

$ cat /tmp/m10-dogfood/.docs.toml
# Added by docs migrate --apply
[project]
name = "foo-bar"

[archive]
date_format = "%Y-%m-%d"

# Step 4 — Verify
$ /tmp/docs-m10-venv/bin/docs check /tmp/m10-dogfood
docs: no violations found
$ /tmp/docs-m10-venv/bin/docs index --root /tmp/m10-dogfood
docs: wrote /tmp/m10-dogfood/INDEX.md
```

Every M10 deliverable surfaces on the dogfooded tree:

- `--apply --quiet` is **truly silent**: exit 0, empty stdout,
  empty stderr.
- The auto-emitted `.docs.toml` carries the OQ-A provenance
  header + `[project] name = "foo-bar"` (the `infer_project`
  output) + `[archive] date_format = "%Y-%m-%d"`. No
  `dir = "archive"` line (OQ-M compliant).
- `docs check` exit 0 immediately after `--apply` — zero
  manual operator steps between apply and a clean check.
- One INDEX regen (the operator's `docs index` after the
  apply; `--apply` itself doesn't refresh the INDEX because
  the migration root may not yet be the docs root in
  general).

### Adopted-fixture delta

The `tests/fixtures/trees/real-trees-adopted/kebab-tiny/`
fixture pre-dated M10's auto-emitted `.docs.toml`. Pre-M10
the fixture carried a hand-authored `[project] name = "foo-bar"`
sidecar (the M8-era subagent's manual Step-5 write). M10's
auto-emitted version differs in three small ways:

- `# Added by docs migrate --apply` provenance header
- Trailing `[archive] date_format = "%Y-%m-%d"` block
- (date metadata is always current-run-relative)

Updated the fixture (`.docs.toml`, the three `.md` files, and
`INDEX.md`) to the M10 auto-emitted shape. No tests consume the
fixture directly (`grep -rln real-trees-adopted tests/` is
empty), so the fixture update is purely a snapshot refresh.
The source fixture
(`tests/fixtures/trees/real-trees/kebab-tiny/`) is unchanged.

### Test results

Pytest after the fixture refresh: **400/400 GREEN.**

### Exit criteria

- [x] 1.4.0 wheel installed in /tmp/docs-m10-venv; `docs --version` prints `docs 1.4.0`.
- [x] Adoption playbook reads end-to-end on /tmp/m10-dogfood: plan → apply → verify.
- [x] `--apply --quiet` produces empty stdout AND empty stderr.
- [x] `.docs.toml` auto-written with `[project] name = "foo-bar"` + `[archive] date_format`; no `dir =` line; provenance header present (OQ-A + OQ-L + OQ-M).
- [x] `docs check /tmp/m10-dogfood` exit 0 after `--apply` with zero manual operator action.
- [x] One INDEX regen (operator's `docs index`).
- [x] Adopted-state fixture updated in lockstep for the M10 auto-emitted shape; behaviour-delta noted above.
- [x] 400/400 pytest GREEN after the fixture refresh.

## Phase 10 — Quality, Docs, Refactor (closeout) (Complete 2026-05-27)

### Objective

Close M10 out: tick the Phase Checklist 5-10, append the
milestone-completion summary to the milestone doc, date the
CHANGELOG, rebuild final 1.4.0 dist artefacts, regen INDEX +
snapshot, archive the milestone doc only (impl log stays
Lifecycle: active per the M8/M9 pattern). No PyPI publish —
deferred to M11.

### Files changed

| File | Action | Notes |
|---|---|---|
| `CHANGELOG.md` | Modify | `## 1.4.0 — UNRELEASED` → `## 1.4.0 — 2026-05-27 (LOCAL; not on PyPI)`. |
| `docs/m10-adoption-polish.md` | Modify | Phase Checklist 5-10 all ticked; milestone-completion summary appended. |
| `docs/m10-adoption-polish-impl.md` | Modify | Phase 10 entry (this section). |
| `docs/status.md` | Modify | M10 row → Complete; Current milestone block updated; Next action → M11 (PyPI publish). |
| `docs/plan.md` | Modify | M10 row → Complete. |
| `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Lockstep refresh after the closeout edits + the milestone-doc archive. |
| `dist/docs_cli-1.4.0-*` | Rebuild | Rebuilt from the closeout-commit state; `twine check` PASSED. |

### Actions taken

- Dated the CHANGELOG entry.
- Wrote the milestone-completion summary on the milestone doc.
- Archived `docs/m10-adoption-polish.md` via
  `docs archive` (impl log stays active per the M8/M9 pattern;
  it remains the operational record of what shipped).
- Rebuilt the wheel + sdist from the closeout-commit state and
  re-ran `twine check`: both PASSED.
- Regenerated `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
  in lockstep.

### Milestone-completion summary

- **Version**: 1.4.0 (ready locally; not on PyPI — publish
  deferred to M11).
- **Surface delivered**: multi-file atomic `docs touch
  <file>...`; `docs migrate --apply` writes/extends `.docs.toml`
  + opportunistic-rmdir; `docs migrate --apply --quiet`
  suppresses per-file output; `[vocabulary] add_fields`
  allowlist + `docs check` `unknown-field` warning rule;
  `Confidence` enum (M4 wire-format byte-stable);
  `MigrationPlan.excluded_count` removed; adoption playbook
  restructured to 4 steps.
- **Test count**: 400 passing (369 M9 baseline + 31 M10
  additions + 0 deletions).
- **Quality gate at closeout**: ruff / ruff format / mypy /
  `docs check docs --stale 14` all clean tree-wide.
- **Dogfood result**: kebab-tiny end-to-end on the 1.4.0
  wheel — `--apply --quiet` truly silent; auto-emitted
  `.docs.toml` carries the OQ-A `[project]` + OQ-M
  `[archive]` blocks; `docs check` exit 0 immediately.
- **Carry-overs absorbed**: M3 (`[vocabulary] add_fields` —
  the long-parked Open question), M7 NIT 1 (`Confidence`
  enum), M8 (`MigrationPlan.excluded_count` removal,
  `--quiet` per-file output suppression, playbook polish),
  M4 (empty-archive-parent rmdir).
- **Deferred** (not in M10 scope): PyPI publish (M11);
  `docs project rename` verb (the project-rename TODO at the
  bottom of the milestone doc).

### Exit criteria

- [x] CHANGELOG dated.
- [x] Milestone-completion summary on the milestone doc.
- [x] Phase Checklist 5-10 ticked.
- [x] status.md M10 → Complete; Next action → M11.
- [x] docs/plan.md M10 → Complete.
- [x] dist/docs_cli-1.4.0-* rebuilt from closeout state; twine check PASSED.
- [x] INDEX + snapshot lockstep refresh.
- [x] Milestone doc archived via `docs archive`; impl log stays Lifecycle: active.
- [x] 400/400 GREEN at closeout.
