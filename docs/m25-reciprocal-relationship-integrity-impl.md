# M25 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-08-11

Related:
- child-of: m25-reciprocal-relationship-integrity.md
- pairs-with: m25-reciprocal-relationship-integrity.md
- pairs-with: status.md
- references: feedback-log.md

## Overview

Chronological implementation log for M25 — Reciprocal relationship integrity
and `docs relate`. Append one evidence-backed section per TDD phase; keep the
progress table and milestone checklist synchronized.

## Implementation metadata

- Project: docs
- Milestone: M25 — Reciprocal relationship integrity and `docs relate`
- Started: 2026-08-10 (milestone setup); Phase 1 started 2026-08-11.
- Progress: **Phases 1–2 complete. Phase 3 — Create Data/Fixtures is next.**
- Source: the operator-confirmed relationship, repair, archive-audit, and
  release-ordering decisions in `feedback-log.md` (2026-08-09/10).
- Branch: `m25-m29/milestone-setup` for setup; `m25/phases-1-4` for the Step-1
  implementation walk (Phases 1–4).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-08-11 | Inverse map, `missing-inverse`, `docs relate` grammar/output, archive audit, D5 failure contract, version staging frozen. Q1–Q5 + OQ-A/B/D resolved. Zero `cli.py` edits (logged deviation). |
| 2. Write Tests (RED) | Complete | 2026-08-11 | +88 items across 6 edited + 2 new files. 724 collected, zero collection errors; ruff/format/mypy clean. |
| 3. Create Data/Fixtures | Pending | — | Reciprocal, missing, excluded, malformed, archived pairs. |
| 4. Run Tests (RED Baseline) | Pending | — | Capture intended failure set. |
| 5. Update Base Interfaces | Pending | — | Inverse/edit/audit planning primitives. |
| 6. Implement Offline/Core Path | Pending | — | Checker + coordinated idempotent edits. |
| 7. Update Tool/Wrapper Layer | Pending | — | CLI, JSON/dry-run, docs, bundled skill, version. |
| 8. Run Tests (GREEN) | Pending | — | Full product and quality gates. |
| 9. Integrate / Accept / Dogfood | Pending | — | Real upgrade/repair flows on a throwaway tree. |
| 10. Quality, Docs, Refactor | Pending | — | Simplify, close docs, completion summary. |

## Setup record — 2026-08-10

### Objective

Promote completed relationship-model discovery into a risk-bounded v2.0
milestone train and prepare the first implementation milestone without starting
Phase 1.

### Actions taken

- Registered M25–M29 in execution order using reciprocal sequence edges.
- Kept durable dependency edges distinct: M28 depends on M27; M29 depends on
  all four implementation milestones.
- Scoped M25 to the confirmed first boundary: semantics, hard validation,
  explicit two-endpoint repair, and narrowly audited archived repair.
- Recorded remaining command/output/audit/failure/version choices for Phase 1.
- Mapped acceptance to real agent workflows: local navigation, upgrade repair,
  and audited historical repair.

### Verification

- `.venv/bin/ruff check .` — passed.
- `.venv/bin/ruff format --check .` — 43 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 44 source files.
- `.venv/bin/python -m pytest -q` — 636 passed.
- `.venv/bin/docs check --root docs` — no violations.

### Decisions / issues

- No bulk repair: the agent must decide whether an edge should be completed or
  removed.
- M26 owns archive authorization, M27/M28 own body links, and M29 owns release.
- The shipped bundle-only use-case catalog remains the project source of truth;
  M25 Phase 10 updates it only when the behavior exists.

## Phase 1 — Define Contract — 2026-08-11

### Objective

Freeze every byte of surface Phase 2 will assert against: the inverse map, the
`missing-inverse` finding schema and message, the `docs relate` grammar and
output modes, idempotency, the two-file failure behaviour, the `Revision:`
encoding, the archived reason/date rules, and v2.0 version staging. No
business logic lands.

### Actions taken

**`docs/cli.md`**

- `docs check`: added the `missing-inverse` rule bullet (error, exit 2,
  case-sensitive verb matching); added `missing-inverse` to the `rule` id
  table and a note that the JSON record's key set is **closed** and unchanged
  (no new field); added `Revision` to the built-in always-allowed label list in
  the `unknown-field` bullet; extended the exit-2 line.
- New **Reciprocal-edge validation (M25 — D2)** block: the frozen message
  template plus a worked instance, the five applicability conditions, the
  archived-in-scope statement, the one-finding-per-triple dedupe rule, the
  no-cycle/no-conflict-detection statement, the no-opt-out-knob statement, and
  an **Upgrading from 1.x** paragraph naming a bare `blocked-by:` as the likely
  legacy offender with the `check → relate add|remove → check` repair loop.
- New **`docs relate add|remove SOURCE VERB TARGET …`** section, placed in the
  mutating-verb cluster between `docs project set` and `docs stamp`: grammar,
  the six-verb table, root resolution, root-relative-first endpoint resolution,
  self-edge refusal, what gets written, the `Updated:` policy, idempotency, the
  one reindex, the no-whole-tree-pre-flight rationale, the archived-endpoint
  rules (`--reason` requirement + single-line shape + the exact three-item
  allowed byte set + the `Revision:` encoding + audit asymmetry), human output,
  the `--json` operation-plan record with a field table, `--dry-run`, the
  five-stage coordinated-write failure contract, a worked upgrade example, the
  exit codes, and the non-goals.
- `## Exit codes (summary)`: new `relate add|remove` row; `relate` added to the
  cross-verb no-root-vs-outside-root convention's verb list.

**`docs/convention.md`**

- New `### Reciprocal relationship verbs (M25)` subsection under
  `## Relationship verbs`: the three-pair table, the symmetry and
  case-sensitivity statements, the hard-error rule with its applicability
  summary, the explicit **non**-membership of `supersedes`/`superseded-by` and
  `child-of`/`parent-of` with the rationale, the `docs relate` repair pointer,
  and the upgrade paragraph.
- `### Optional fields`: new `Revision` row.
- Lifecycle table `blocked` row: the pre-M25 "pair with a one-sided
  `blocked-by`" recommendation is **withdrawn** and replaced with the
  reciprocal-pair rule, plus an explicit statement that `Lifecycle: blocked`
  and the `blocks`/`blocked-by` edge stay **uncoupled** (milestone non-goal).
- `### Extending vocabularies`: `Revision` added to the built-in
  always-allowed label list with its rationale.
- `## Archive subtree`: new **Audited relationship repair (M25 — D4)**
  paragraph beside the M18 edge-integrity paragraph, naming the second narrow
  exception and the exact allowed byte set.
- `## What docs does not promise`: "No link-graph traversal" amended — one-hop
  reciprocity of six verbs is now validated; still no graph query, multi-hop
  traversal, cycle/conflict detection, or rendering.

**Milestone doc** — new `## Decisions (Phase 1 — BINDING)` section carrying
D1–D6, the frozen Phase-5 signatures, the `check_tree` shape change, and the
logged Phase-1 deviation; `## Open questions for Phase 1` replaced by
`## Resolved questions (Q1–Q5, BINDING)`. Phase-1 checklist ticked; D1
deliverable ticked; Progress line updated.

**Lockstep chores** — `cp docs/{cli,convention}.md
src/docs_cli/skill/references/`; `docs touch` on the five edited docs (implicit
reindex); `tests/fixtures/expected/docs-INDEX.md` re-synced from the
regenerated `docs/INDEX.md`.

### Decisions / issues

- **Q5 / D6 — version staging (operator decision, supersedes the planning
  agent's recommendation).** The package stays **`1.8.0` for all of M25**.
  `pyproject.toml` is not bumped and the packaging version pins
  (`test_a3_project_version_is_1_8_0`, `test_b1`, `test_b2`, `test_c2`) are
  neither renamed nor re-pinned — they stay exactly as they are and stay GREEN.
  M25–M28 are version-neutral; **M29 performs the single bump to `2.0.0`** at
  publish. CHANGELOG: M25's Phase-7 entries go under an `UNRELEASED` heading
  carrying **no invented version number**, which M29 renames and dates — the
  `release-runbook.md` M9 pattern, minus the speculative version.
- **OQ-A — endpoint path precedence (operator-confirmed).** Relative
  `SOURCE`/`TARGET` resolve **root-relative first**, falling back to
  cwd-relative when the root-relative form is not a file; absolute paths as-is;
  all output names the root-relative POSIX form. Phase 2 must test **both**
  interpretations. Note this is a deliberate *superset* of `project set`'s
  behaviour (which is root-relative only) — chosen so a path copied out of a
  `missing-inverse` finding resolves without translation, while a cwd-relative
  path still works from inside the tree.
- **OQ-C — archived `--reason` (operator-confirmed).** Required whenever
  **either** named endpoint is under the archive subtree, checked in the
  validate-all-first pass **before** planning. An idempotent no-op naming an
  archived endpoint still requires it and still writes nothing.
- **OQ-B — finding attribution.** The `missing-inverse` finding blames the
  **source** doc, one per distinct `(source, verb, target)` triple —
  consistent with `broken-ref` blaming the referrer.
- **OQ-D — no opt-out knob.** No `[check] reciprocal = false`. Compensated by
  the mandatory upgrade guidance in both specs (and, at Phase 7, the CHANGELOG)
  and by the withdrawal of the `convention.md` recommendation that generates
  the most likely legacy offender.
- **Deviation (approved).** The milestone's Phase-1 file list names
  "contract-level function signatures in `src/docs_cli/cli.py`". Phase 1 made
  **zero** `cli.py` edits: stubs would change the Phase-4 subprocess RED
  reasons and risk baseline behaviour, and the phase's own exit criterion is
  "no business logic lands". The signatures are frozen in the milestone doc's
  Decisions instead and land as real code in Phase 5.
- **Free dogfood lock confirmed.** The live `docs/` tree's 20 recognized-verb
  bullets already form 10 complete pairs (verified by grep), so M25's hard rule
  will not break the existing `test_check_dogfood_repo_docs_is_clean` gate —
  that test becomes a genuine (currently degenerate) M25 lock.
- **`Revision` must join `_BUILTIN_METADATA_FIELDS` in Phase 5**, otherwise a
  tree with `[vocabulary] add_fields` set gets an `unknown-field` warning on a
  label `docs relate` itself writes. Specs already state it; the code change is
  Phase-5 work and Phase 2 writes the RED lock for it.
- **Phase-7 follow-through recorded by exact name:** `src/docs_cli/skill/SKILL.md`
  verb table + front-matter `description:` verb list must gain `docs relate`.
  **No** version-pin follow-through — the version does not move in M25.

### Verification

- `grep` for every Phase-2 verbatim string in `docs/cli.md` — all present
  (`has no inverse;`, `unknown verb 'pairs-with'`, `--reason is required`,
  `--reason must be a single line`, `rolled back`, `ROLLBACK FAILED`,
  `is not writable; refusing before any write`,
  `must be different documents`, `no change — `, `recorded revision in`).
- `.venv/bin/python -m pytest tests/test_skill_refs.py tests/test_cli_index.py
  tests/test_cli_check.py -q` — 30 passed (bundled refs byte-identical; INDEX
  snapshot re-synced).
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 43 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 44 source files.
- `.venv/bin/python -m pytest -q` — **636 passed** (unchanged from baseline; no
  test file was touched in Phase 1).
- `.venv/bin/docs check --root docs` — no violations (exit 0).
- `git diff --stat src/docs_cli/cli.py` — **empty**, per the logged deviation.
- `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.

## Phase 2 — Write Tests (RED) — 2026-08-11

### Objective

Express inverse validation and two-endpoint mutation behaviour before any
implementation exists, so every Phase-5/6/7 change is answering a written
test rather than the other way round.

### Authoring rules applied

- **No module-level import of a not-yet-existing symbol.** That is a
  collection error, which the Phase-4 exit criterion forbids. Every new
  symbol is reached through a one-line `_m25(name)` helper wrapping
  `getattr` — runtime gives a clean `AttributeError` (the honest RED), mypy
  sees `Any` (so `mypy src/ tests/` stays green at baseline), and the
  variable argument keeps ruff's `B009` quiet.
- **Every intended-exit-2 test also asserts its contract stderr string.**
  Argparse already exits 2 on `invalid choice: 'relate'`, so a
  returncode-only assertion would be *falsely GREEN* for the whole refusal
  family. Each such test additionally asserts on-disk byte-identity.
- Each test carries a docstring naming its intended RED reason, and the
  GREEN-at-baseline locks say so explicitly — including which of them are
  **degenerate** (passing today only because the rule does not exist).

### Tests written (+88 collected items)

| File | New items | Covers |
|---|---|---|
| `tests/test_check.py` | +26 | inverse map exactness/symmetry/case-sensitivity; frozen `missing-inverse` message + source attribution; all three pairs in both directions (parametrized); the free-form / `supersedes` trap; the four applicability exemptions (broken target, excluded, malformed, non-Markdown); parseability-only independence from `bad-vocab`; archived-in-scope; per-triple dedupe; per-doc grouping order; exit code 2; the `Revision` `unknown-field` lock; legacy-fixture no-new-findings (parametrized) |
| `tests/test_cli_check.py` | +4 | subprocess exit 2 + repair text; JSON record key set unchanged; clean reciprocal tree exits 0; archived one-sided pair exits 2 |
| `tests/test_edit.py` | +14 | `add_related_edge` (append / create group / no-op / minimal diff / insert before a trailing `Revision:` group / trailing-newline state); `remove_related_edge` (exact bullet only / drop the emptied label / no-op); `append_revision_entry` (create after `Related:` / chronological append under one group / `parse()` round-trip into `Doc.extra` / minimal diff) |
| `tests/test_relate_plan.py` (new) | +8 | `plan_relate` purity, `present_before`/`present_after`, the archived three-item byte delta, active-side has no `Revision:`; `apply_relate_plan` publish; **rollback on injected second-write failure**; **rollback-failure is reported, not swallowed**; `relate_plan_to_json` exact shape |
| `tests/test_cli_relate.py` (new) | +32 | help/grammar; happy paths incl. `add`→`check` clean and `remove`→`check` clean; symmetric-invocation byte identity; idempotency (add/remove twice, INDEX included); `--dry-run`; `--json` shape + stdout cleanliness; nine refusals; **both** endpoint-resolution interpretations (OQ-A); five archived cases incl. the no-op-still-needs-`--reason` lock; the writability pre-flight; one-reindex and no-reindex-on-no-op |
| `tests/test_cli_mv.py` | +1 | `mv` preserves a reciprocal pair (GREEN at baseline) |
| `tests/test_cli_archive.py` | +2 | archive one endpoint / `--cascade` both endpoints preserve the pair (GREEN at baseline) |
| `tests/test_skill.py` | +1 | `SKILL.md` verb table + front-matter `description:` name `relate` |

### Decisions / issues

- **`test_relate_symmetric_invocations_produce_identical_trees` builds both
  trees under the SAME name in different parent dirs.** A first pass named
  them `forward`/`reverse`, which made the comparison unsatisfiable — the
  project slug, root title, and INDEX entries all embed the tree name. Same
  name, different parent, is the only shape in which "byte-identical tree"
  is a meaningful assertion.
- **The unwritable-endpoint test is why D5 stage 4 exists.** `atomic_write`
  publishes via tmpfile + rename, which *succeeds* on a read-only file in a
  writable directory. Only an explicit `os.access(..., W_OK)` pre-flight
  honours a read-only archive, so the test pins the pre-flight rather than
  the write.
- **Two committed fixture trees were added to the Phase-3 list beyond the
  Phase-1 plan:** `reciprocal-broken/` (an unresolvable recognized target,
  proving `broken-ref` keeps ownership) and `reciprocal-archived-complete/`
  (the reciprocated active↔archived pair, the clean counterpart to
  `reciprocal-archived-missing/`).
- The check-side fixture trees land in **Phase 3**, so between this commit
  and the next the fixture-backed tests fail on an absent directory. That
  is the intended phase ordering; the classified RED baseline is captured in
  Phase 4, after the fixtures exist.

### Verification

- `.venv/bin/python -m pytest tests/ -q --co` — **724 tests collected**
  (636 baseline + 88), **zero collection errors**.
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 45 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 46 source files (the `getattr`
  indirection keeps every new symbol `Any`).
- The three GREEN-at-baseline mv/archive reciprocity-survival locks run
  green already: `pytest tests/test_cli_mv.py::test_mv_preserves_reciprocal_pair
  tests/test_cli_archive.py::test_archive_one_endpoint_preserves_reciprocal_pair
  tests/test_cli_archive.py::test_archive_cascade_preserves_reciprocal_pair -q`
  — 3 passed.
- `git diff --stat src/docs_cli/cli.py` — still empty; no product code moved.

## Milestone completion summary

_Not complete._
