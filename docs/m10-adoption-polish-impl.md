# M10 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-05-26

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
| 2. Write Tests (RED) | Complete | 2026-05-26 | 27 new test items added across `tests/test_cli_touch.py` (5 multi-file/atomic/single-INDEX), `tests/test_cli_migrate.py` (6 `--apply` writes/extends `.docs.toml` + `--quiet` + OQ-G rmdir), `tests/test_check.py` (5 `unknown-field` rule incl. OQ-O Related-never-flagged lock), `tests/test_cli_check.py` (2 CLI `unknown-field`), `tests/test_config.py` (3 `add_fields` schema), `tests/test_migrate.py` (5 `Confidence` enum + 1 `excluded_count` removal). 23 RED + 4 GREEN regression-locks; M9's 369 GREEN preserved (no existing test regressed). Test count: 396 collected (369 + 27). |
| 3. Create Data/Fixtures | Complete | 2026-05-26 | No-op per the Phase-3 recommendation in the milestone plan: every Phase-2 test that needed a real tree on disk built it inline via `tmp_path` (multi-file touch trees, vocab trees, OQ-G rmdir tree) so the test files own their setup and Phase 3 had no fixtures to stage. Sign-off folded into the Phase 4 commit. |
| 4. Run Tests (RED Baseline) | Complete | 2026-05-26 | Verbatim baseline captured at `/tmp/m10-phase-4-baseline.txt`: **23 failed, 373 passed (396 collected)**. Per-deliverable attribution table below; every RED traces to an intended unimplemented Phase-5/6 surface (no fixture FNF, no unintended ImportError outside the documented `Confidence` import, no flaky assertion). M9's 369 GREEN baseline preserved + 4 GREEN regression-locks added. Quality gate clean. |
| 5. Update Base Interfaces | Pending | — | |
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
| `tests/test_cli_touch.py` | Modify | +5 tests — multi-file happy path, single-INDEX-refresh observation, atomic-failure body preservation, atomic-failure INDEX preservation, multi-file `--dry-run`. Inline `tmp_path` multi-file tree builder. |
| `tests/test_cli_migrate.py` | Modify | +6 tests — `--apply` writes `.docs.toml` when absent (OQ-A); `--apply` extends sidecar without overwriting `[project]` (OQ-L); `--apply` does NOT overwrite existing `[project]` (OQ-A safety-net); `--apply --quiet` suppresses per-file output (OQ-B); `--quiet` does NOT suppress dry-run/`--summary`/`--json` outputs (OQ-B scope); empty-archive-parent rmdir (OQ-G + OQ-Q). |
| `tests/test_check.py` | Modify | +5 tests — `unknown-field` rule clean-when-no-allowlist (OQ-H); `unknown-field` warning shape (OQ-F); allowlist-match clean (OQ-H); case-sensitivity (OQ-H exact match); OQ-O Related-never-flagged regression-lock. |
| `tests/test_cli_check.py` | Modify | +2 tests — CLI `unknown-field` mismatch exits 1; CLI allowlist-match exits 0. |
| `tests/test_config.py` | Modify | +3 tests — `add_fields` parses into `Config.fields`; default empty frozenset; case preserved verbatim. |
| `tests/test_migrate.py` | Modify | +5 tests — `Confidence` enum identity for HIGH/MEDIUM/LOW returns; `FileMigration.confidence` accepts enum + invariant; JSON wire format still emits strings (regression lock). +1 test — `MigrationPlan.excluded_count` removal (`not hasattr`). |

### Actions taken

- Authored the 27 new test items per the planning agent's per-deliverable contract anchors. Each maps 1:1 to a Deliverable in the milestone doc (D1-D6); one additional regression-lock for OQ-O (Related: never flagged) added during the same-instance audit pass.
- Built per-test setup inline via `tmp_path` rather than committing new fixtures (per the Phase 3 recommendation in the planning plan). The multi-file touch tree, the vocab trees for `unknown-field`, and the OQ-G rmdir tree are all constructed from primitives in the test body.
- Used `# type: ignore[call-arg]` ONE place (`tests/test_check.py::_config_with_fields`) to keep mypy clean at the RED baseline while the `fields` kwarg doesn't exist yet on `Config`. The ignore will be removed at Phase 5 once `Config.fields` lands.
- Held the line on identity (`is`) for Confidence enum assertions, not equality — the enum's value matches the existing string literal, so equality would still pass against the pre-enum implementation and not catch the regression.

### Issues / decisions

- **Regression-lock count drift.** The planning agent expected ~24 RED + 2 GREEN regression-locks. Actual at baseline: 23 RED + 4 GREEN regression-locks (the 2 extra GREEN locks are #8 — defensive sidecar-with-`[project]` behavior already locked by current carve-out matrix; and #10 — `--quiet` already not suppressing dry-run/`--summary`/`--json`). Both are intended GREEN-from-baseline locks; the RED count drift (one extra RED, for the audit-added OQ-O Related-never-flagged anchor) is an artefact of the contract being narrower than expected at points where M8 already enforced the behavior + one audit-added regression-lock.
- **`test_check_doc_unknown_field_with_no_allowlist_is_clean` baseline status.** The planning agent expected this test to be GREEN at baseline (an empty allowlist implies "no rule emits, suite is clean"). Actually it is RED at baseline because the test passes `fields=` to `Config(...)`, which TypeErrors today. This is RED for the intended reason — the contract anchor is "once `fields` exists, an empty allowlist must not emit `unknown-field` findings" — Phase 5 lands the kwarg, Phase 6 lands the rule, and both this test + #14 turn GREEN.

### Test results

- pytest: **23 failed, 373 passed (396 collected)** — RED count for Phase 4 baseline; M9's 369 GREEN preserved + 4 new GREEN regression-locks.
- ruff / ruff format --check / mypy / `docs check docs --stale 14`: all clean.

### Exit criteria

- [x] 27 new test items collected.
- [x] 23 RED for intended reasons (no import errors, no fixture FNF, every failure traces to a Phase-5/6 deliverable surface).
- [x] 4 GREEN regression-locks pinned at baseline (#8, #10, #17, #25).
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
