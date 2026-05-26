# M10 — Adoption-flow polish + 1.3.0 carry-overs

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-05-26

Related:
- parent-of: m10-adoption-polish-impl.md
- child-of: plan.md
- implements: charter.md
- pairs-with: status.md

## Overview

- Milestone: M10 (v1.4.0)
- Title: Adoption-flow polish + 1.3.0 carry-overs
- Surface: two new CLI features (`docs touch <file...>`, `docs migrate --apply` writes `.docs.toml`), one behaviour fix (`migrate --apply --quiet` actually suppresses per-file output), one new check rule (`unknown-field` warning via `[vocabulary] add_fields`), one internal cleanup (`Confidence` enum replacing `bool | str`), one API tidy (`MigrationPlan.excluded_count` removal), and a sweep of the M8 adoption playbook to absorb the friction the fresh-subagent gate surfaced.
- Progress: Stub-drafted 2026-05-25; active once Phase 1 lands and OPEN QUESTIONS resolve.

### Goal

Close the highest-leverage follow-ons from M1-M9 so the M8 adoption loop ships truly hands-off. The two user-suggested features (`touch` multi-file + `migrate --apply` writes `.docs.toml`) collapse the M8 playbook's three-pattern ordering note and remove the last steps every fresh M8 subagent had to perform manually. The cleanup items (`Confidence` enum, `excluded_count` removal, `add_fields` allowlist) discharge M3/M7/M8 carry-overs that have accumulated in plan.md's Open questions.

### Requirements

- `docs touch` accepts one or more positional file paths; atomic semantics (all-or-nothing on errors); INDEX refreshes once at end, not per file.
- `docs migrate --apply` writes a minimal `.docs.toml` at the resolved root when one is absent, carrying `[project] name = "<resolved-project>"` + `[archive] date_format`. If a sidecar `.docs.toml` exists (M8 OQ1 carve-out: `[exclude]`-only or `[migrate]`-only), add `[project]` in place; never silently overwrite an existing `[project]` block.
- `docs migrate --apply --quiet` suppresses the per-file plan output (not just the trailing stderr success line). Dry-run / `--summary` / `--json` modes are requested outputs and stay unaffected.
- `docs check` learns a new `unknown-field` warning rule (exit 1, never 2) gated by an opt-in `[vocabulary] add_fields = [...]` allowlist in `.docs.toml`. Trees without the section see no change.
- Internal: `infer_role` returns a `Confidence` enum (`HIGH | MEDIUM | LOW`) instead of `bool | str`. JSON `--json confidence` field stays a string for wire-format stability.
- Internal: `MigrationPlan.excluded_count` removed; consumers (the human plan footer) use `sum(c for _, c in excluded_breakdown)`. CHANGELOG note; no known external consumer.
- Bundled `references/adoption-playbook.md` swept to reflect the new `--apply` semantics — the three-pattern ordering note in Step 3 collapses to "run `--apply`, then commit"; Steps 5/6 lose the manual `.docs.toml` authoring.
- `cli.md`, `convention.md`, `architecture.md`, README, CHANGELOG, bundled skill references all updated in lockstep.
- Version bumps: `pyproject.toml` + `__version__` 1.3.0 → 1.4.0.

### Deliverables

- [ ] `docs touch` accepts `file...` positional (`nargs="+"`); atomic semantics; single end-of-batch INDEX refresh.
- [ ] `docs migrate --apply` writes / extends `.docs.toml` at the resolved root.
- [ ] `docs migrate --apply --quiet` suppresses per-file plan output.
- [ ] `[vocabulary] add_fields` allowlist + `check_doc` `unknown-field` warning rule.
- [ ] `Confidence` enum + `infer_role` return-type tightening.
- [ ] `MigrationPlan.excluded_count` removed.
- [ ] `references/adoption-playbook.md` rewritten for the new `--apply` semantics.
- [ ] `cli.md`, `convention.md`, `architecture.md`, README updated; CHANGELOG `## 1.4.0` entry.
- [ ] Bundled skill references resynced.
- [ ] M10 dogfooded against the M7/M8 sanitised fixtures end-to-end (Phase 9) — confirm a fresh subagent adopts `kebab-tiny` without any manual `.docs.toml` write.

## OPEN QUESTIONS

Surfaced 2026-05-25 while drafting M10. Operator-resolution requested before Phase 2 starts; recommendations in brackets.

1. **OQ-A — `migrate --apply` and existing `.docs.toml` shape.** When `--apply` finds a sidecar with `[migrate]` or `[exclude]` but no `[project]`, options: (a) add `[project]` in place (preserving the sidecar), (b) leave the file untouched and print a hint, (c) refuse with exit 2. **[Recommendation: (a)]** — append a `[project]` block after any existing sections; use a comment header `# Added by docs migrate --apply` so the provenance is visible. Preserving `[migrate]` / `[exclude]` honours the M8 OQ1 carve-out (operator-explicit "use migrate on this tree" signal).

2. **OQ-B — `--quiet` scope.** Today `--quiet` only suppresses the trailing stderr success line. **[Recommendation: extend to suppress the per-file plan block on `--apply` only; keep dry-run / `--summary` / `--json` outputs unchanged]** since those are explicitly requested outputs, not status chatter.

3. **OQ-C — `docs touch` error semantics on a missing/unreadable file.** Options: (a) atomic — exit nonzero, write nothing; (b) best-effort — skip and continue, report skipped count. **[Recommendation: (a) atomic]** — mirrors `migrate --apply`'s edit-then-move atomicity and the project's atomic-write discipline. Validate all paths first; refuse with exit 1 + named-bad-path if any fail validation; then mutate.

4. **OQ-D — `MigrationPlan.excluded_count` removal as 1.4.0 breaking note.** The field is set in `plan_migration` but read nowhere in shipped code (the human footer iterates `excluded_breakdown` directly; `migration_to_json` omits it). No known external consumer. **[Recommendation: remove in 1.4.0 with CHANGELOG entry under Changed]**; deferring to a 2.0 buys nothing.

5. **OQ-E — `Confidence` enum and the JSON wire format.** `migration_to_json` currently emits `"confidence": "high" | "medium" | "low"` (strings). **[Recommendation: keep emitting strings via `enum.value`]** so the wire format is byte-identical and no JSON consumer breaks. Internal code switches to the enum; serialisation crosses back to strings at the boundary.

6. **OQ-F — `unknown-field` rule message shape.** Allowlist source (`[vocabulary] add_fields`) is the canonical example; the warning should name the field name encountered and the doc path. **[Recommendation: `Finding(severity="warning", rule="unknown-field", message="metadata field '<Label>:' not in [vocabulary] add_fields allowlist", path=<rel>)`]** — mirrors M3's existing rule-message shape. Exit 1 only (warning), never exit 2.

7. **OQ-G — Empty `archive-style/` subdir cleanup after `migrate --apply`.** M4 left this deferred: `archived/old-doc.md` moves to `archive/<date>/old-doc.md` but the now-empty `archived/` stays. Adding `rmdir` is one line. **[Recommendation: include in M10 — `apply_migration` `try: parent.rmdir(); except OSError: pass`]** after each archive move. Opportunistic, behaviour-neutral.

8. **OQ-H — `[vocabulary] add_fields` field-name canonicalisation.** Should the allowlist values be matched case-sensitively or case-insensitively against doc metadata labels? **[Recommendation: case-sensitive — exact match]**, matching how `add_lifecycles` and `add_roles` already work. The on-disk convention is `Capital:` (`Owner:`, `Tags:`); `owner:` is malformed (the parser already rejects it).

9. **OQ-I — Playbook scope for the `references/adoption-playbook.md` rewrite.** Items #1-#3 collapse Steps 3/5/6 substantially. Options: (a) minimal edit — keep the playbook structure, drop the obsolete patterns; (b) restructure into "Step 1 plan → Step 2 triage → Step 3 apply → Step 4 verify" (4 steps not 6). **[Recommendation: (b) restructure]** — the playbook gets shorter and clearer; the M8 fresh-subagent gate's friction items dissolve into the simpler structure.

## Current State Analysis

- **Existing code (1.3.0):**
  - `_cmd_touch` (`src/docs_cli/cli.py:3238`) — single positional `file`; refreshes INDEX per call.
  - `apply_migration` (`src/docs_cli/cli.py:2471`) — writes metadata blocks + archives; does NOT write `.docs.toml`.
  - `_cmd_migrate --quiet` — only suppresses success line, not per-file plan output (M8 simplify deferred).
  - `infer_role` returns `tuple[str, bool | str]` where `True | "medium" | False` encodes confidence.
  - `MigrationPlan.excluded_count: int` — set, never read.
  - `check_doc` rules: `missing-field`, `malformed`, `bad-vocab`, `bad-date`, `status-drift`, `broken-ref`, `medium-confidence-inference`. No `unknown-field`.
  - `Config.fields` does not exist; `load_config` knows `add_lifecycles` / `add_roles`, not `add_fields`.
- **Missing for M10:**
  - Multi-file touch surface + atomic batching.
  - `apply_migration` `.docs.toml` writer (honouring M8 OQ1 sidecar carve-out).
  - `--quiet` plan-output suppression.
  - `Confidence` enum + JSON-boundary string serialisation.
  - `MigrationPlan.excluded_count` removal + footer code update.
  - `[vocabulary] add_fields` schema + `Config.fields` + `load_config` branch + `unknown-field` `check_doc` rule.
  - Empty-archive-subdir `rmdir` in `apply_migration` (OQ-G).
- **Known gotchas:**
  - Bundled skill references at `src/docs_cli/skill/references/{cli,convention}.md` enforce byte-equality with `docs/{cli,convention}.md` via `tests/test_skill_refs.py`. Spec edits must be mirrored in the same commit.
  - The dogfood snapshot at `tests/fixtures/expected/docs-INDEX.md` must stay in lockstep with `docs/INDEX.md`.
  - `MigrationPlan` is part of the importable surface (`from docs import MigrationPlan` via the M6 conftest alias); removing `excluded_count` is technically breaking even without known consumers.

## Files to Create / Modify

| File | Action | Phase | Notes |
|---|---|---|---|
| `docs/m10-adoption-polish.md` | Create | 1 | This task plan. |
| `docs/m10-adoption-polish-impl.md` | Create | 1 | This milestone's impl log. |
| `docs/plan.md` | Modify | 1 | Add M10 row; flip the parked `[vocabulary] add_fields` Open question to "Scheduled in M10". |
| `docs/status.md` | Modify | 1, …, 10 | Phase 1: "Current milestone" → M10. Phase 10: M10 → Complete. |
| `tests/test_cli_touch.py` | Modify | 2 | Multi-file happy path, atomic-failure semantics, single-INDEX-refresh observation. |
| `tests/test_cli_migrate.py` | Modify | 2 | `--apply` writes `.docs.toml`; `--apply` extends existing sidecar; `--apply` does NOT overwrite existing `[project]`; `--apply --quiet` suppresses per-file output; empty `archived/` rmdir (OQ-G). |
| `tests/test_check.py` + `tests/test_cli_check.py` | Modify | 2 | `unknown-field` warning rule; `[vocabulary] add_fields` allowlist suppresses it; exit-1 wiring. |
| `tests/test_config.py` | Modify | 2 | `add_fields` TOML key parses; `Config.fields` defaults to empty frozenset. |
| `tests/test_migrate.py` | Modify | 2 | `Confidence` enum return; identity assertions widened. |
| `tests/test_packaging.py` | Modify | 7 | Version 1.3.0 → 1.4.0 (3 spots: A3 + B1/B2 wheel-name + C2 `--version`). |
| `src/docs_cli/cli.py` | Modify | 5, 6, 7 | Phase 5: `Confidence` enum, `Config.fields`, `MigrationPlan.excluded_count` removed, `touch` argparse `nargs="+"`, `unknown-field` rule scaffolding, `--quiet` argparse plumbed to `_print_migration_plan`. Phase 6: implementation — multi-file `_cmd_touch` (atomic), `apply_migration` writes `.docs.toml` + OQ-G rmdir, `_cmd_migrate --quiet` suppression, `check_doc` `unknown-field` rule. Phase 7: `__version__` → 1.4.0. |
| `docs/cli.md` | Modify | 7 | `docs touch` synopsis: `<file>...`. `docs migrate --apply` documents `.docs.toml` write + `--quiet` semantics. `docs check` rule list gains `unknown-field`. `[vocabulary]` section gains `add_fields`. |
| `docs/convention.md` | Modify | 7 | `[vocabulary] add_fields` documented in the Per-tree `[migrate]` config section neighbour. |
| `docs/architecture.md` | Modify | 7 | `Confidence` enum + `MigrationPlan` field-list update + `check_doc` rule list update + `apply_migration` `.docs.toml` writer note. |
| `README.md` | Modify | 7 | Status section gains M10 row + 1.4.0 narrative. |
| `CHANGELOG.md` | Modify | 7, 10 | Phase 7: `## 1.4.0 — UNRELEASED` (Added / Changed / Notes). Phase 10: dated. |
| `pyproject.toml` | Modify | 7 | `version = "1.4.0"`. |
| `src/docs_cli/skill/references/adoption-playbook.md` | Rewrite | 7 | OQ-I — restructure to 4 steps (plan / triage / apply / verify); remove the three-pattern ordering note. |
| `src/docs_cli/skill/references/cli.md` + `convention.md` | Resync | 7 | Byte-identical mirrors after `docs/{cli,convention}.md` edits. |
| `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` | Regenerate | 1, 5, 7, 10 | Lockstep after every doc-touching phase. |

## TDD Implementation Plan

### Phase 1 — Define Contract
- Objective: Land the milestone-doc + log skeleton, register M10 in plan.md, flip status.md "Current milestone" to M10. No code change. Surface the OPEN QUESTIONS for operator review before Phase 2 starts.
- Files: `docs/m10-adoption-polish.md`, `docs/m10-adoption-polish-impl.md`, `docs/plan.md`, `docs/status.md`, `docs/INDEX.md` + snapshot.
- Exit: M10 docs created, lifecycle `active`; `docs check docs --stale 14` exit 0; 369 tests still GREEN.

### Phase 2 — Write Tests (RED)
- Objective: Express every M10 deliverable as a failing test before any implementation.
- Files: `tests/test_cli_touch.py` (multi-file + atomic), `tests/test_cli_migrate.py` (apply-writes-toml + apply-extends-sidecar + apply-quiet-suppresses + empty-archive-rmdir), `tests/test_check.py` + `tests/test_cli_check.py` (unknown-field rule), `tests/test_config.py` (add_fields), `tests/test_migrate.py` (Confidence enum); minor regression-lock additions for `excluded_count` removal and JSON wire-format stability.
- Exit: Suite collects cleanly; RED count matches deliverable count; M9's 369 GREEN preserved.

### Phase 3 — Create Data/Fixtures
- Objective: Stage fixtures the Phase-2 tests reference. Reuse M8's `body-from/` + M7's `real-trees/` heavily; new fixtures only for `add_fields` (1-2 small `.docs.toml` + doc pairs).
- Files: `tests/fixtures/add-fields/{allowlist-empty,allowlist-populated}/`.
- Exit: Every Phase-2 fixture path resolves; sanitisation grep zero hits.

### Phase 4 — Run Tests (RED Baseline)
- Objective: Capture verbatim RED baseline; confirm every failure traces to its intended unimplemented surface.
- Files: log only (`/tmp/m10-phase-4-baseline.txt`).
- Exit: Per-test attribution table in impl log; no RED-for-wrong-reason; quality gate clean.

### Phase 5 — Update Base Interfaces
- Objective: Schema + argparse + scaffolding. `Confidence` enum; `Config.fields`; `MigrationPlan.excluded_count` removed; `touch` argparse `nargs="+"`; `migrate --quiet` plumbed; `_cmd_check` wiring for `unknown-field`.
- Files: `src/docs_cli/cli.py`; possibly `tests/_typing/docs.pyi` re-export adjustments.
- Exit: M9 + Phase 5 GREEN where the bare scaffolding flips REDs without implementation; remaining REDs all behaviour-side for Phase 6.

### Phase 6 — Implement Offline/Core Path
- Objective: All business logic for the M10 deliverables.
- Files: `src/docs_cli/cli.py` (`_cmd_touch`, `apply_migration`, `_print_migration_plan`, `check_doc`).
- Exit: Every M10 RED → GREEN; M9 baseline still GREEN.

### Phase 7 — Update Tool/Wrapper Layer
- Objective: Spec sweep + version bump + skill-references resync.
- Files: `docs/{cli,convention,architecture}.md`, `README.md`, `CHANGELOG.md`, `pyproject.toml`, `src/docs_cli/cli.py` (`__version__`), `tests/test_packaging.py` (version pins), `src/docs_cli/skill/references/{cli,convention,adoption-playbook}.md`.
- Exit: All 369 + M10 new tests GREEN at 1.4.0; bundled skill references byte-equal to source.

### Phase 8 — Run Tests (GREEN)
- Objective: Capture verbatim GREEN gate at `/tmp/m10-phase-8-green.txt`.
- Files: log only.
- Exit: pytest 0 RED; ruff / format / mypy / `docs check docs` / `docs index --dry-run` / `python -m build` / `twine check` all clean.

### Phase 9 — Implement Online/Integration (dogfood)
- Objective: Re-run the M8 fresh-subagent gate against the M10-built wheel on `kebab-tiny`. Confirm the agent adopts the tree end-to-end with NO manual `.docs.toml` write and NO `--apply --quiet` per-file output. Update `tests/fixtures/trees/real-trees-adopted/` if behaviour delta is observable.
- Files: log entry; possibly refreshed `real-trees-adopted/` fixtures.
- Exit: 1/1 PASS unattended (single tree is enough — M8 proved the loop; M10 proves the polish).

### Phase 10 — Quality, Docs, Refactor
- Objective: Milestone-completion summary on both docs; flip status.md M10 → Complete; date CHANGELOG; build artefacts locally. Per the M7/M8 pattern, NO publish at this phase — publish to PyPI deferred to a separate M11 milestone (or batched into a future release).
- Files: `docs/m10-adoption-polish.md`, `docs/m10-adoption-polish-impl.md`, `docs/status.md`, `CHANGELOG.md`, `dist/docs_cli-1.4.0-*`.
- Exit: Full gate green; milestone ready to archive.

## Phase Checklist

- [x] Phase 1 — Define Contract (2026-05-25)
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

_Recorded as the milestone progresses. Initial decisions inherited from the OPEN QUESTIONS block above will be promoted here as the operator confirms each one._

- **OQ-A — `migrate --apply` sidecar handling** (operator-confirmed 2026-05-26): append `[project]` in place after any existing sections; prefix with comment header `# Added by docs migrate --apply`; never overwrite an existing `[project]`.
- **OQ-B — `--quiet` scope** (operator-confirmed 2026-05-26): `migrate --apply --quiet` suppresses per-file plan block AND trailing success line. `--dry-run` / `--summary` / `--json` unaffected.
- **OQ-C — `docs touch` atomic semantics** (operator-confirmed 2026-05-26): validate all paths first, exit 1 + named-bad-path if any fail, then mutate; single end-of-batch INDEX refresh.
- **OQ-D — `MigrationPlan.excluded_count` removal** (operator-confirmed 2026-05-26): removed at 1.4.0; CHANGELOG entry under Changed.
- **OQ-E — `Confidence` enum + JSON wire format** (operator-confirmed 2026-05-26): `Confidence(HIGH, MEDIUM, LOW)` enum internally; JSON wire format keeps strings via `enum.value`.
- **OQ-F — `unknown-field` rule shape** (operator-confirmed 2026-05-26): `Finding(severity="warning", rule="unknown-field", message="metadata field '<Label>:' not in [vocabulary] add_fields allowlist", path=<rel>)`. Exit 1 only.
- **OQ-G — `apply_migration` empty-archive rmdir** (operator-confirmed 2026-05-26): opportunistically `rmdir`s the now-empty parent after each archive move.
- **OQ-H — `[vocabulary] add_fields` matching** (operator-confirmed 2026-05-26): case-sensitive exact match.
- **OQ-I — `references/adoption-playbook.md` rewrite** (operator-confirmed 2026-05-26): restructured to 4 steps (plan / triage / apply / verify); three-pattern ordering note dropped.
- **Carries from prior milestones:** M3 (`unknown-field` allowlist), M7 NIT 1 (`Confidence` enum), M8 (`--quiet` behaviour fix, `MigrationPlan.excluded_count` tidy, playbook polish), M4 (empty-archive-subdir rmdir under OQ-G).
- **Conscious deferrals (NOT in M10):** LLM-assisted classification (M7), `--propose-excludes` heuristic (M8 OQ-A), `docs init --template` verb (M8 OQ-D), per-verb file split (M2), Trusted Publishing OIDC (M6), `importlib.metadata` `__version__` (M6 Q1), mechanical test-file rewrite from `docs` alias (M6), multi-line `Status:` prose continuation (M7 OQ-3), `Migrated-<Label>` rename rule review (M4), mtime-derived `Updated:` snapshot test (M4), M3 `malformed` rule expansion, M1 `Vocab` dataclass, M1 empty-body description cosmetics, PyPI token re-scope (M9), `explainer`/`architecture` roles into core vocab (M7).
- **Version**: 1.4.0 — minor bump. `MigrationPlan.excluded_count` removal called out in CHANGELOG under Changed; no known external consumers.

## Success Criteria

- All Deliverables ticked.
- Quality gate green at every phase boundary (`pytest`, `ruff`, `ruff format`, `mypy`, `docs check docs`).
- `docs touch a.md b.md c.md` writes all three and refreshes the INDEX exactly once; failure on any path leaves all files untouched.
- `docs migrate --apply <foreign-tree>` (no pre-existing `.docs.toml`) produces a tree that `docs check` accepts without any additional operator action.
- `docs migrate --apply --quiet <foreign-tree>` produces no per-file plan output on stdout (errors still on stderr).
- `docs check <tree>` against a tree with an `Owner:` field and no `[vocabulary] add_fields` allowlist exits 0 (no warning); with `add_fields = ["Owner"]` exits 0 (allowed); with `add_fields = ["Tags"]` exits 1 (warning for unknown `Owner:`).
- M10's dogfood subagent (Phase 9) adopts `kebab-tiny` end-to-end with zero manual `.docs.toml` editing.
- `CHANGELOG.md` `## 1.4.0` entry covers every M10 surface change.
- All bundled skill references byte-equal to source after Phase 7.

## Follow-on TODOs

### Project rename (deferred — likely M11)

Surfaced 2026-05-26 while adopting an existing tree into the docs convention.

**Gap.** Renaming a docs-managed tree's `[project] name` today requires a re-`migrate` with a `[migrate] project_name = "..."` sidecar **plus** an `[exclude]` section in `.docs.toml` to waive the managed-tree refusal (the M8 carve-out). That is currently the only way to rewrite an already-conformant file's `Project:` line without hand-editing. Operators (and sub-agents) re-invent this sidecar dance each time.

**Recommendation.** Build a first-class `docs project rename <new-name>` verb (or equivalent) that:
- Rewrites `[project] name` in `.docs.toml`.
- Rewrites every conformant `Project:` line across the tree atomically.
- Refreshes the INDEX once at end.
- Does **not** require the operator to add an `[exclude]` carve-out or a `[migrate]` sidecar.
- Errors out cleanly if any path can't be rewritten (atomic semantics, mirroring `migrate --apply` and `touch`).

**Why deferred from M10:** M10 scope is locked on adoption-flow polish + 1.3.0 carry-overs; a `project rename` verb is new surface, not polish. Captured here so it does not get lost.
