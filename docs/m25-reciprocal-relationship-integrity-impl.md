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
- Progress: **Phases 1–4 complete (Step 1). Phase 5 — Update Base Interfaces is next.**
- Source: the operator-confirmed relationship, repair, archive-audit, and
  release-ordering decisions in `feedback-log.md` (2026-08-09/10).
- Branch: `m25-m29/milestone-setup` for setup; `m25/phases-1-4` for the Step-1
  implementation walk (Phases 1–4).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-08-11 | Inverse map, `missing-inverse`, `docs relate` grammar/output, archive audit, D5 failure contract, version staging frozen. Q1–Q5 + OQ-A/B/D resolved. Zero `cli.py` edits (logged deviation). |
| 2. Write Tests (RED) | Complete | 2026-08-11 | +92 items across 6 edited + 2 new files (88 at first pass, +4 from the same-instance audit). 728 collected, zero collection errors; ruff/format/mypy clean. |
| 3. Create Data/Fixtures | Complete | 2026-08-11 | 9 committed `reciprocal-*` trees + 3 inline builders. Each hand-verified to yield only its intended findings. |
| 4. Run Tests (RED Baseline) | Complete | 2026-08-11 | 728 collected, **77 failed, 651 passed**. Every RED matches its classified reason; zero collection errors, zero tracebacks, zero xfails; pre-existing 636 all still GREEN. |
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

### Tests written (+92 collected items)

| File | New items | Covers |
|---|---|---|
| `tests/test_check.py` | +26 | inverse map exactness/symmetry/case-sensitivity; frozen `missing-inverse` message + source attribution; all three pairs in both directions (parametrized); the free-form / `supersedes` trap; the four applicability exemptions (broken target, excluded, malformed, non-Markdown); parseability-only independence from `bad-vocab`; archived-in-scope; per-triple dedupe; per-doc grouping order; exit code 2; the `Revision` `unknown-field` lock; legacy-fixture no-new-findings (parametrized) |
| `tests/test_cli_check.py` | +4 | subprocess exit 2 + repair text; JSON record key set unchanged; clean reciprocal tree exits 0; archived one-sided pair exits 2 |
| `tests/test_edit.py` | +14 | `add_related_edge` (append / create group / no-op / minimal diff / insert before a trailing `Revision:` group / trailing-newline state); `remove_related_edge` (exact bullet only / drop the emptied label / no-op); `append_revision_entry` (create after `Related:` / chronological append under one group / `parse()` round-trip into `Doc.extra` / minimal diff) |
| `tests/test_relate_plan.py` (new) | +8 | `plan_relate` purity, `present_before`/`present_after`, the archived three-item byte delta, active-side has no `Revision:`; `apply_relate_plan` publish; **rollback on injected second-write failure**; **rollback-failure is reported, not swallowed**; `relate_plan_to_json` exact shape |
| `tests/test_cli_relate.py` (new) | +36 | help/grammar; happy paths incl. `add`→`check` clean and `remove`→`check` clean; symmetric-invocation byte identity; idempotency (add/remove twice, INDEX included); `--dry-run`; `--json` shape for apply / dry-run / **no-op**, + stdout cleanliness; `--quiet` gating (success suppressed, refusals never); **eleven** refusals; **both** endpoint-resolution interpretations (OQ-A); six archived cases incl. the no-op-still-needs-`--reason` lock; the writability pre-flight; the **no-whole-tree-pre-flight** lock; one-reindex and no-reindex-on-no-op |
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

- `.venv/bin/python -m pytest tests/ -q --co` — **728 tests collected**
  (636 baseline + 92), **zero collection errors**.
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

## Phase 3 — Create Data/Fixtures — 2026-08-11

### Objective

Provide small, deterministic trees covering every relationship direction and
every archived-repair boundary, one semantic per tree.

### Decision — split fixtures

Committed **static trees** for the check-side *semantic* cases (structure, not
dates: nothing rots, and it matches the existing `archive-pair` / `cross-refs`
precedent). **Inline `tmp_path` builders** for every mutation-shaped case,
because those tests write and then byte-compare — a `shutil.copytree` of a
static tree would be pure overhead, and the parametrised cases vary one edge
at a time.

### Committed trees — `tests/fixtures/trees/`

| Tree | Contents | Isolates |
|---|---|---|
| `reciprocal-clean/` | `a↔b` (`precedes`/`follows`), `c↔d` (`depends-on`/`required-by`), `e↔f` (`blocks`/`blocked-by`) | all three pairs complete → exit 0 |
| `reciprocal-missing/` | `a.md` declares `precedes: b.md`; `b.md` has a `Related:` group (`references: a.md`) but no `follows` | exactly one `missing-inverse`, against the SOURCE — and the group's presence isolates the missing *inverse* from a missing *group* |
| `reciprocal-freeform/` | one-sided `pairs-with`, `child-of`, `supersedes`, `superseded-by`, `references` | the supersedes trap: free-form verbs are never flagged |
| `reciprocal-broken/` | `a.md` declares `precedes: ghost.md` (no such file) | `broken-ref` keeps sole ownership |
| `reciprocal-excluded/` | `[exclude] dirs = ["vendor"]`; `a.md` declares `precedes: vendor/b.md`; the target file exists | an excluded endpoint yields no finding (and no `broken-ref`, since the file is real) |
| `reciprocal-malformed/` | `b.md` has no H1 | `malformed` keeps sole ownership |
| `reciprocal-nonmd/` | `a.md` declares `depends-on: data.yaml`; the YAML file exists | a non-Markdown target cannot declare an inverse → no finding |
| `reciprocal-archived-missing/` | active `a.md` → `archive/2026-01-01/old.md`; the archived doc has `Lifecycle: archived`, `Archived-reason:`, prose, and **no** `required-by` | the archived RED case **and** the `docs relate --reason` repair target |
| `reciprocal-archived-complete/` | the same pair, reciprocated | an archived endpoint is not inherently a finding |

`reciprocal-broken/` and `reciprocal-archived-complete/` are additions beyond
the Phase-1 fixture list: the first proves `broken-ref` ownership with a
committed tree rather than an inline one, the second is the clean counterpart
that stops `reciprocal-archived-missing/` from being the only archived
evidence.

### Inline builders (authored in the Phase-2 commit; recorded here as the Phase-3 surface)

- `tests/test_check.py` — `_pair_root(tmp_path, *, source_edge, target_edge, source_role)`.
- `tests/test_cli_relate.py` — `_pair_tree(...)` and `_archived_pair_tree(...)`.
- `tests/test_relate_plan.py` — `_two_doc_root(...)` and `_archived_pair_root(...)`.

### Verification

Each tree was checked **by hand** with the installed 1.8.0 binary — the
findings below are the complete pre-M25 output, and each is exactly the
intended one:

| Tree | `docs check` today | exit |
|---|---|---|
| `reciprocal-clean` | no violations | 0 |
| `reciprocal-missing` | no violations (the `missing-inverse` is the Phase-4 RED) | 0 |
| `reciprocal-freeform` | no violations | 0 |
| `reciprocal-broken` | `a.md error [broken-ref] … ghost.md` | 2 |
| `reciprocal-excluded` | no violations | 0 |
| `reciprocal-malformed` | `b.md error [malformed] missing H1` | 2 |
| `reciprocal-nonmd` | no violations | 0 |
| `reciprocal-archived-missing` | no violations (the `missing-inverse` is the Phase-4 RED) | 0 |
| `reciprocal-archived-complete` | no violations | 0 |

- The `reciprocal-excluded` predicate was verified to actually fire:
  `_iter_doc_texts` with the compiled predicate yields `['a.md']`, without it
  `['a.md', 'vendor/b.md']`. The fixture tests the exclusion, not an accident.
- All dates are static (`2026-05-20` active, `2026-01-01` archived) and **no
  stale window is ever passed** to these trees, so no committed date rots.
- One semantic per tree; `git status` showed exactly the 30 intended new
  fixture files and nothing else.

## Phase 4 — Run Tests (RED Baseline) — 2026-08-11

### Objective

Prove the new tests fail for the intended missing behaviour, and only for
that — with every RED traced to a classified reason and every
GREEN-at-baseline lock named.

### Headline

```
.venv/bin/python -m pytest tests/ -q
77 failed, 651 passed in 29.38s

.venv/bin/python -m pytest tests/ -q --co
728 tests collected
```

- **728 collected** (636 pre-M25 + 92 new).
- **77 failed** — every one of them a new M25 test.
- **651 passed** = the **636 pre-existing tests, all still GREEN**, plus the
  15 new GREEN-at-baseline locks.  (Every one of the 92 new items is either
  an intended RED or a named GREEN-at-baseline lock: 77 + 15 = 92.)
- **Zero collection errors, zero tracebacks, zero xfails/xpasses**
  (`grep -c Traceback` → 0; `grep -ci "xfail\|xpass"` → 0).
- Pre-existing regressions: **0**. Verified mechanically by collecting the
  test-id list from a throwaway worktree at the Phase-1 commit (`3dca105`,
  636 ids) and intersecting it with the 73 failing ids —
  `comm -12 failed.txt old-tests.txt | wc -l` → **0**.

### RED classification (77 = 23 + 36 + 18)

| Class | Count | Verified RED reason |
|---|---|---|
| `inverse_verb` / `RECIPROCAL_INVERSES` / `RECIPROCAL_VERBS` | 1 | `AttributeError: module 'docs_cli.cli' has no attribute …` via `_m25()` — interfaces land Phase 5 (the documented-honest-RED pattern M19 used for `Config.stale_days`) |
| editor primitives (`add_related_edge`, `remove_related_edge`, `append_revision_entry`) | 14 | `AttributeError` |
| `plan_relate` / `apply_relate_plan` / `relate_plan_to_json` / `CoordinatedWriteError` | 8 | `AttributeError` |
| every `docs relate …` subprocess test | 36 | argparse `invalid choice: 'relate'` → exit 2 + usage banner. **25** fail on the returncode assertion; the **11 intended-exit-2 tests** pass the returncode assertion (argparse also exits 2) and then fail on their **contract stderr assertion** — so none of them is falsely GREEN. Confirmed one-by-one: `unknown verb 'pairs-with'`, `unknown verb 'Precedes'`, `is not under a docs root with .docs.toml; refusing`, `SOURCE and TARGET must be different documents`, `--date:`, `--reason must be a single line`, `--reason must not be empty`, `--reason is required`, `is under the archive subtree`, `is not writable; refusing before any write`, `docs: INDEX refresh failed:` |
| check-side reciprocity behaviour | 16 | plain assertion — no `missing-inverse` finding is produced (13 in `test_check.py`, 3 in `tests/test_cli_check.py`) |
| `Revision` `unknown-field` lock | 1 | plain assertion — the warning fires because `_BUILTIN_METADATA_FIELDS` lacks `"Revision"` |
| `SKILL.md` relate row | 1 | plain assertion — Phase 7 |

Exception-type totals from `pytest --tb=line`: **23 `AttributeError`**, the
rest `AssertionError` / bare `assert` — no other exception class appears.

**Accepted coverage boundary (recorded, not a gap to fix in this step).** The
two D5 *CLI-level* rollback strings (`…; rolled back <rel> — the tree is
unchanged` and `…; ROLLBACK FAILED for <rel> — repair manually: …`) are not
pinned by a subprocess test: injecting a mid-write `OSError` across a
`subprocess.run` boundary would need a fragile filesystem trick. The
**semantics** are pinned at the unit seam
(`test_apply_relate_plan_rolls_back_when_second_write_fails` and
`test_apply_relate_plan_rollback_failure_is_reported_not_swallowed` assert
`CoordinatedWriteError.rolled_back` / `.published` and byte-identity), and
the strings are frozen in `cli.md`; Phase 7 renders them from those fields.
Likewise `relate remove --dry-run`'s `would remove …` line is covered only
by the `add` direction's dry-run test plus the `remove` end-to-end test.

### GREEN-at-baseline locks (must pass now AND after Phase 6)

Verified together in one run — **17 passed**:

| Lock | Honest status today |
|---|---|
| `test_check_tree_complete_pair_clean` | **DEGENERATE** — passes only because the rule does not exist |
| `test_check_tree_freeform_verbs_never_flagged` | **DEGENERATE** (the supersedes trap; the real over-fire guard after Phase 6) |
| `test_check_tree_broken_target_owns_the_case` | **DEGENERATE** |
| `test_check_tree_excluded_endpoint_no_inverse_finding` | **DEGENERATE** |
| `test_check_tree_malformed_endpoint_no_inverse_finding` | **DEGENERATE** |
| `test_check_tree_non_markdown_target_no_inverse_finding` | **DEGENERATE** |
| `test_check_tree_archived_pair_complete_is_clean` | **DEGENERATE** |
| `test_check_tree_legacy_fixtures_gain_no_new_findings` ×4 (`drift`, `invalid`, `with-archive`, `cross-refs`) | **DEGENERATE** |
| `test_check_clean_reciprocal_tree_exits_0` | **DEGENERATE** |
| `test_check_dogfood_repo_docs_is_clean` (pre-existing, `tests/test_cli_check.py`) | **DEGENERATE as an M25 lock**, but a genuine one after Phase 6 — reclassified here: the live `docs/` tree's 20 recognized-verb bullets already form 10 complete pairs, so M25's hard rule keeps this gate green for free |
| `test_check_json_emits_finding_array` (pre-existing) | **GENUINE** — it already pins `set(rec) == {path,severity,rule,message}` for every record, which is what forces `missing-inverse` to add no JSON field |
| `test_mv_preserves_reciprocal_pair` | **GENUINE** on the edge-rewrite assertions (`_cmd_mv` already rewrites tree-wide); the trailing `docs check` clean assertion is degenerate |
| `test_archive_one_endpoint_preserves_reciprocal_pair` | **GENUINE** on the edge-rewrite assertions (M14 — A4) |
| `test_archive_cascade_preserves_reciprocal_pair` | **GENUINE** on the edge-rewrite assertions (M18 archive-subtree edge integrity) |
| `test_a3_project_version_is_1_8_0`, `test_b1_wheel_builds`, `test_b2_sdist_builds`, `test_c2_docs_version_is_1_8_0` | **GENUINE** — untouched by M25 and still pinned at `1.8.0` per D6; 4 passed |

### Phase-7 follow-through to record by exact name

- `src/docs_cli/skill/SKILL.md` — the verb table needs a `docs relate` row and
  the front-matter `description:` verb list needs `relate`
  (`test_skill_md_documents_relate_verb` is its RED lock, and the existing
  `test_every_named_verb_is_a_real_subcommand` completeness guard will fail
  the moment `relate` is registered without this edit).
- `CHANGELOG.md` — M25's entries under an `UNRELEASED` heading with **no**
  invented version number (D6); M29 renames and dates it.
- **No version-pin follow-through.** The version does not move in M25.

### Other gates at the RED baseline

- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 45 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 46 source files (the `_m25()`
  getattr indirection keeps every not-yet-existing symbol `Any`).
- `.venv/bin/docs check --root docs` — no violations, exit 0.
- `git diff --stat 3dca105 -- src/docs_cli/cli.py` — **empty**. Phases 1–4
  moved zero product code, exactly as the logged Phase-1 deviation intends.

## Same-instance consistency audit — Step 1 (Phases 1–4) — 2026-08-11

Run against this step's own work per the ship-milestone consistency-check
reference, after Phase 4 and before handing back. Findings and fixes:

### Accuracy — tests vs. spec

1. **Three contract strings were asserted by tests but not pinned in
   `cli.md`.** The `relate` exit-1 family (`file not found:`,
   `is outside the resolved docs root`, the parser's self-locating
   `docs: <path>: <detail>`) and the `--date` refusal
   (`docs: relate: --date: <detail>`) existed only as test expectations.
   **Fixed** — all four are now pinned in `cli.md`'s *Endpoint resolution*
   and *`Updated:` policy* paragraphs. A spec the tests can outrun is the
   exact failure mode this audit exists to catch.
2. **`--reason` had an unspecified empty case.** D4 says "single non-empty
   line" but only the multi-line refusal had a message. **Fixed** — `cli.md`
   and the milestone's D4 now pin
   `docs: relate: --reason must not be empty` as a *distinct* message
   (reusing the multi-line one would be actively misleading), plus an
   explicit statement that `--reason` is **accepted but unused** on an
   all-active pair.

### Tests genuinely pin the contract (the highest-leverage check)

3. **Two contract points had no test at all.** Added:
   - `test_relate_does_not_gate_on_whole_tree_health` — a malformed
     *sibling* must not block the repair; it may only fail the end-of-run
     reindex, **after** both endpoints are already correct. This is the
     whole rationale for `relate` skipping the `archive`/`mv` whole-tree
     pre-flight, and nothing was pinning it.
   - `test_relate_empty_reason_refuses` — the newly-pinned empty-reason
     message.
4. **Two contract points were under-constrained.** Added:
   - `test_relate_no_op_json_reports_not_applied` — `applied: false` was
     only pinned for `--dry-run`; the spec also requires it for an
     idempotent no-op, which is a different code path.
   - `test_relate_quiet_suppresses_success_but_never_a_refusal` — the
     "human output gated on `not --quiet`; refusals always print" rule had
     no lock in either direction.
5. **One assertion was weaker than the spec.**
   `test_check_tree_findings_grouped_by_path` asserted the *set* of a doc's
   rules; the spec pins the intra-doc **order** (`check_doc`'s findings,
   then any `missing-inverse`). **Fixed** — it now asserts the ordered rule
   list `["bad-vocab", "missing-inverse", "malformed"]`.

### Consistency — documentation

6. **`docs/plan.md` was stale.** Both the v2.0-train prose and the M25
   tracker row still read "milestone-setup complete; Phase 1 next".
   **Fixed** — both now record Phases 1–4 complete on `m25/phases-1-4`, the
   Q5 version-staging decision, and the RED-baseline counts.
7. Test counts were restated across `status.md`, the milestone doc, the
   phase table, and the Phase-2/Phase-4 records after the four added tests
   (88 → 92 new items; 724 → 728 collected; 73 → 77 failed).

### Verified clean (no fix needed)

- No `TODO`/`FIXME`/placeholder in any new test or fixture; no product code
  exists to stub.
- `git diff --stat bf8f273..HEAD` touches only `docs/`, `tests/`, and the two
  bundled `src/docs_cli/skill/references/` mirrors — no unrelated change.
- The bundled refs are byte-identical to the sources after the `cli.md` fix
  (`tests/test_skill_refs.py` — 3 passed); `docs/INDEX.md` and
  `tests/fixtures/expected/docs-INDEX.md` are in lockstep
  (`test_index_output_matches_frozen_snapshot` green).
- Every doc edited this step had `Updated:` bumped via `docs touch`, and
  `docs check --root docs` exits 0, so every `Related:` edge resolves.
- New test code follows the existing `_run(script, *args, cwd=…)` subprocess
  helper shape, `_TREES`/`fixtures_dir` conventions, and the per-file
  section-comment style.
- One commit per phase on `m25/phases-1-4`, `m25(phase N): …` messages, no
  secrets staged.

### Nothing surfaced for an operator decision

No finding changed milestone scope or behaviour intent. Every fix either
wrote down a contract the tests already assumed, or added a lock for a
contract the specs already stated.

## Milestone completion summary

_Not complete._
