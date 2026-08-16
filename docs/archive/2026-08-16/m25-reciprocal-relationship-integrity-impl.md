# M25 — Implementation Log

Lifecycle: archived
Role: log
Project: docs
Updated: 2026-08-16
Archived: 2026-08-16

Related:
- child-of: archive/2026-08-16/m25-reciprocal-relationship-integrity.md
- pairs-with: archive/2026-08-16/m25-reciprocal-relationship-integrity.md
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
- Progress: **All ten TDD phases complete (Step 2, 2026-08-12), plus the
  fresh-eyes review fold-in and its operator-approved **D7
  `duplicate-field`** addition. M25 is implementation-complete and stays
  `Lifecycle: active` until the M29 publish closeout. 777 passed.**
- Source: the operator-confirmed relationship, repair, archive-audit, and
  release-ordering decisions in `feedback-log.md` (2026-08-09/10).
- Branch: `m25-m29/milestone-setup` for setup; `m25/phases-1-4` for the Step-1
  implementation walk (Phases 1–4); `m25/phases-5-10` for the Step-2
  implementation walk (Phases 5–10).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-08-11 | Inverse map, `missing-inverse`, `docs relate` grammar/output, archive audit, D5 failure contract, version staging frozen. Q1–Q5 + OQ-A/B/D resolved. Zero `cli.py` edits (logged deviation). |
| 2. Write Tests (RED) | Complete | 2026-08-11 (amended 2026-08-12) | +121 items across 6 edited + 2 new files (88 first pass, +4 same-instance audit, +29 fresh-eyes review fold-in). 757 collected, zero collection errors; ruff/format/mypy clean. |
| 3. Create Data/Fixtures | Complete | 2026-08-11 (amended 2026-08-12) | 10 committed `reciprocal-*` trees + 3 inline builders. Each hand-verified to yield only its intended findings. |
| 4. Run Tests (RED Baseline) | Complete | 2026-08-11 (re-baselined 2026-08-12) | 757 collected, **87 failed, 670 passed**. Every RED matches its classified reason; zero collection errors, zero tracebacks, zero xfails; pre-existing 636 all still GREEN. |
| 5. Update Base Interfaces | Complete | 2026-08-12 | Vocabulary, `inverse_verb`, three editors, `RelateEdit`/`RelatePlan`/`CoordinatedWriteError`, `Revision` built-in label, canonical-path + lenient-pairs helpers, `relate_plan_to_json`; three behaviour seams stubbed. **71 failed, 686 passed.** |
| 6. Implement Offline/Core Path | Complete | 2026-08-12 | `reciprocity_findings`, `check_tree` interleave, `plan_relate`/`_plan_relate_edit`, `apply_relate_plan` + `_rollback_relate`. **44 failed, 713 passed** — every remaining RED is a `docs relate` subprocess test (43) or the SKILL.md lock (1). |
| 7. Update Tool/Wrapper Layer | Complete | 2026-08-12 | `relate` namespace + `add`/`remove` subverbs, `_resolve_relate_endpoint`, `_print_relate_lines`, `_cmd_relate`, dispatch; SKILL.md row + description; `UNRELEASED` CHANGELOG (no version bump); eight spec corrections to `cli.md` + mirror re-sync; tracker docs. **756 passed, 1 failed** — the single RED is an unsatisfiable assertion in a Step-1 test (see *Blocker* below), not missing behaviour. |
| 8. Run Tests (GREEN) | Complete | 2026-08-12 | **757 passed, 0 failed** (757 collected, zero collection errors). All 636 pre-existing test ids proven still present and GREEN by `comm`. One defective Step-1 assertion corrected under operator approval; `cli.py` byte-unchanged by that commit. |
| 9. Integrate / Accept / Dogfood | Complete | 2026-08-12 | Eight flows on a throwaway `cp -r docs` copy: detect → repair → re-check, remove/restore/idempotency, audited archived repair (refusal then repair then a second `Revision:` bullet), blast radius (1 of 46 archived files changed), dry-run/JSON, real tree untouched. |
| 10. Quality, Docs, Refactor | Complete | 2026-08-12 | Placeholder sweep clean; `Finding`'s rule-id list corrected; `architecture.md` + `test-strategy.md` closed; use-case catalog gained the upgrade-and-repair flow; completion summaries written. Later extended by the post-review fold-in: two editor defects fixed, four locks added, and the operator-approved **D7 `duplicate-field`** mini-cycle. **777 passed**, gate clean, version still 1.8.0. |

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

### Tests written (+121 collected items, final)

| File | New items | Covers |
|---|---|---|
| `tests/test_check.py` | +46 | inverse map exactness/symmetry/case-sensitivity; frozen `missing-inverse` message + source attribution; all three pairs in both directions (parametrized); the free-form / `supersedes` trap; the four applicability exemptions (broken target, excluded, malformed, non-Markdown); parseability-only independence from `bad-vocab`; archived-in-scope; per-triple dedupe; per-doc grouping order; exit code 2; the `Revision` `unknown-field` lock; legacy-fixture no-new-findings (parametrized) |
| `tests/test_cli_check.py` | +4 | subprocess exit 2 + repair text; JSON record key set unchanged; clean reciprocal tree exits 0; archived one-sided pair exits 2 |
| `tests/test_edit.py` | +14 | `add_related_edge` (append / create group / no-op / minimal diff / insert before a trailing `Revision:` group / trailing-newline state); `remove_related_edge` (exact bullet only / drop the emptied label / no-op); `append_revision_entry` (create after `Related:` / chronological append under one group / `parse()` round-trip into `Doc.extra` / minimal diff) |
| `tests/test_relate_plan.py` (new) | +10 | `plan_relate` purity, `present_before`/`present_after`, the archived three-item byte delta, active-side has no `Revision:`; `apply_relate_plan` publish; **rollback on injected second-write failure**; **rollback-failure is reported, not swallowed**; `relate_plan_to_json` exact shape |
| `tests/test_cli_relate.py` (new) | +43 | help/grammar; happy paths incl. `add`→`check` clean and `remove`→`check` clean; symmetric-invocation byte identity; idempotency (add/remove twice, INDEX included); `--dry-run`; `--json` shape for apply / dry-run / **no-op**, + stdout cleanliness; `--quiet` gating (success suppressed, refusals never); **eleven** refusals; **both** endpoint-resolution interpretations (OQ-A); six archived cases incl. the no-op-still-needs-`--reason` lock; the writability pre-flight; the **no-whole-tree-pre-flight** lock; one-reindex and no-reindex-on-no-op |
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

- `.venv/bin/python -m pytest tests/ -q --co` — **757 tests collected**
  (636 baseline + 121), **zero collection errors**.
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
| `reciprocal-self-edge/` (added 2026-08-12) | `a.md` declares `precedes: a.md` **and** `depends-on: ./a.md` | post-review amendment A: a self-referential recognized edge is exempt — and the exemption survives path normalization (amendment B) |

`reciprocal-self-edge/` landed with the fresh-eyes fold-in (see that section
below). `reciprocal-broken/` and `reciprocal-archived-complete/` are
additions beyond the Phase-1 fixture list: the first proves `broken-ref` ownership with a
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
| `reciprocal-self-edge` | no violations | 0 |

- The `reciprocal-excluded` predicate was verified to actually fire:
  `_iter_doc_texts` with the compiled predicate yields `['a.md']`, without it
  `['a.md', 'vendor/b.md']`. The fixture tests the exclusion, not an accident.
- All dates are static (`2026-05-20` active, `2026-01-01` archived) and **no
  stale window is ever passed** to these trees, so no committed date rots.
- One semantic per tree; `git status` showed exactly the intended new
  fixture files and nothing else (30 at Phase 3, +2 with `reciprocal-self-edge/`).

## Phase 4 — Run Tests (RED Baseline) — 2026-08-11

### Objective

Prove the new tests fail for the intended missing behaviour, and only for
that — with every RED traced to a classified reason and every
GREEN-at-baseline lock named.

### Headline

```
.venv/bin/python -m pytest tests/ -q
87 failed, 670 passed in 30.39s

.venv/bin/python -m pytest tests/ -q --co
757 tests collected
```

- **757 collected** (636 pre-M25 + 121 new).
- **87 failed** — every one of them a new M25 test.
- **670 passed** = the **636 pre-existing tests, all still GREEN**, plus the
  34 new GREEN-at-baseline locks.  (Every one of the 121 new items is either
  an intended RED or a named GREEN-at-baseline lock: 87 + 34 = 121.)
- **Zero collection errors, zero tracebacks, zero xfails/xpasses**
  (`grep -c "Traceback (most recent call last)"` → 0;
  `grep -ci "xfail\|xpass"` → 0). Note the plain `grep -c Traceback` used
  on the first pass is a false-positive trap — it matches the literal
  `assert "Traceback" not in proc.stderr` echoed back in a failure listing.
- Pre-existing regressions: **0**. Verified mechanically by collecting the
  test-id list from a throwaway worktree at the Phase-1 commit (`3dca105`,
  636 ids) and intersecting it with the failing ids —
  `comm -12 failed.txt old-tests.txt | wc -l` → **0**.

### RED classification (87 = 25 + 43 + 19)

| Class | Count | Verified RED reason |
|---|---|---|
| `inverse_verb` / `RECIPROCAL_INVERSES` / `RECIPROCAL_VERBS` | 1 | `AttributeError: module 'docs_cli.cli' has no attribute …` via `_m25()` — interfaces land Phase 5 (the documented-honest-RED pattern M19 used for `Config.stale_days`) |
| editor primitives (`add_related_edge`, `remove_related_edge`, `append_revision_entry`) | 14 | `AttributeError` |
| `plan_relate` / `apply_relate_plan` / `relate_plan_to_json` / `CoordinatedWriteError` | 10 | `AttributeError` (includes both `remove`-direction plan tests) |
| every `docs relate …` subprocess test | 43 | argparse `invalid choice: 'relate'` → exit 2 + usage banner. **30** fail on the returncode assertion; the **13 intended-exit-2 tests** pass the returncode assertion (argparse also exits 2) and then fail on their **contract stderr assertion** — so none of them is falsely GREEN. Confirmed one-by-one: `unknown verb 'pairs-with'`, `unknown verb 'Precedes'`, `is not under a docs root with .docs.toml; refusing`, `--root <dir> does not contain .docs.toml; refusing`, `SOURCE and TARGET must be different documents`, `--date:`, `--reason must be a single line`, `--reason must not be empty`, `--reason is required`, `is under the archive subtree`, `is not writable; refusing before any write`, `write failed for sub/b.md:`, `docs: INDEX refresh failed:` |
| check-side reciprocity behaviour | 17 | plain assertion — no `missing-inverse` finding is produced (14 in `test_check.py`, 3 in `tests/test_cli_check.py`) |
| `Revision` `unknown-field` lock | 1 | plain assertion — the warning fires because `_BUILTIN_METADATA_FIELDS` lacks `"Revision"` |
| `SKILL.md` relate row | 1 | plain assertion — Phase 7 |

Exception-type totals from `pytest --tb=line`: **25 `AttributeError`**, the
rest `AssertionError` / bare `assert` — no other exception class appears.

**Accepted coverage boundary — corrected 2026-08-12 after the fresh-eyes
review.** The first Phase-4 pass claimed *both* D5 CLI-level rollback
strings were unreachable from a subprocess test. That was **wrong for the
successful-rollback half**, and the review supplied the clean injection:
put the target in a subdirectory, `chmod 555` the **directory** and leave
the file's own mode alone — `os.access(file, W_OK)` still returns True so
the stage-4 pre-flight passes, then `atomic_write` fails creating
`b.md.docs-tmp` inside the unwritable directory, which is exactly the
stage-5 path. `test_relate_second_write_failure_rolls_back_and_says_so` now
pins `docs: relate: write failed for <rel>: <err>; rolled back <rel> — the
tree is unchanged` end-to-end plus tree byte-identity (same non-root
assumption `test_archive_oserror_mid_rewrite_exits_2` already makes).

What remains genuinely unreachable is the **`ROLLBACK FAILED`** half: it
needs the *restore* to fail after the publish already succeeded, which no
static filesystem permission arrangement produces. Its semantics stay
pinned at the unit seam
(`test_apply_relate_plan_rollback_failure_is_reported_not_swallowed`
asserts `rolled_back is False` and `published`), and the string is frozen
in `cli.md` for Phase 7 to render from those fields. Likewise
`relate remove --dry-run`'s `would remove …` line is covered only by the
`add` direction's dry-run test plus the `remove` end-to-end test.

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
   (88 → 92 new items; 724 → 728 collected; 73 → 77 failed). *(Superseded by
   the fresh-eyes fold-in below: the final Step-1 figures are 121 new items,
   757 collected, 87 failed.)*

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

## Fresh-eyes review fold-in — Step 1 — 2026-08-12

Independent review of Step 1 returned **no blockers**: the contract is
coherent, the RED suite is honest, all five binding operator decisions are
respected, and the reviewer reproduced the gate. Everything below is
test-coverage hardening or doc tightening, plus two operator-binding
contract amendments. **+29 test items** (92 → 121); nothing was relaxed and
no test was deleted.

### Post-review contract amendments (operator-binding)

These are genuine contract changes, so each landed as a **Phase-1 spec
edit + Phase-2 test (+ Phase-3 fixture for A)**, with the mirrors re-synced
byte-identically.

**Amendment A — a self-referential recognized edge is EXEMPT.** New
applicability condition 5: an edge whose target resolves to the declaring
document is not reciprocity-checked. *Reasoning:* `docs relate` refuses a
self-edge outright (`SOURCE and TARGET must be different documents`), so
without the exemption `docs check` would emit an **unfixable** finding —
naming a repair the repair verb declines to perform. A self-edge also has
no second document whose context could be completed, which is the rule's
entire purpose. Sits on the same boundary as the "no cycle or conflict
detection" non-goal. Landed in `cli.md` (applicability list),
`convention.md`, the milestone's D2, the new
`tests/fixtures/trees/reciprocal-self-edge/` tree (whose second bullet
spells the self-edge non-canonically, so A and B are pinned together), and
`test_check_tree_self_edge_is_exempt`.

**Amendment B — reciprocity matches on CANONICAL paths.** Both the source
edge's target and each candidate inverse bullet are resolved to their
root-relative POSIX form before comparison — the same resolution
`broken-ref` already performs via `(root / target)`. *Reasoning:* a
**hard** rule with no opt-out must not fail a genuinely reciprocal tree
over a `./` prefix; a purely textual match would turn a cosmetic spelling
into an exit-2 error. The finding's message still quotes the canonical
form, so the repair it names is the one `docs relate` writes, and the
per-triple dedupe key uses the canonical target. Landed in `cli.md`
(a dedicated *Path matching is normalized* paragraph + the dedupe
sentence), `convention.md`, the milestone's D2, and three tests
(`…non_canonical_target_path…`, `…non_canonical_inverse_path…`,
`…dotdot_target_path…`).

### should-fix findings

1. **Endpoint-resolution PRECEDENCE was not pinned** — both existing tests
   were unambiguous cases, so a cwd-relative-**first** implementation would
   have passed them while violating binding decision OQ-A.
   `test_relate_endpoint_resolution_prefers_root_relative_over_cwd` now
   builds a tree where `<root>/x.md` **and** `<cwd>/x.md` both exist and
   differ, and asserts the edge lands in the root-relative one while the
   decoy stays byte-identical.
   `test_relate_absolute_endpoint_inside_root_reports_root_relative` covers
   the untested absolute-inside-root happy path and asserts no absolute
   path leaks into the output.
2. **The rule could have ignored the inverse bullet's TARGET.** Every
   fixture had the target declaring the wrong *verb* or no `Related:` group
   at all, so "does the target declare `follows` at all?" satisfied the
   whole suite while under-reporting real one-sided edges.
   `test_check_tree_inverse_pointing_elsewhere_is_still_missing` has
   `b.md` declare `follows: c.md` with `c.md` reciprocating `b.md`, so the
   b↔c pair is complete and exactly one finding — against `a.md` — is
   isolated.
3. **The archived idempotent no-op *with* `--reason` was untested.** Only
   the refusal-when-absent case existed, so nothing stopped Step 2 from
   appending a `Revision:` bullet and bumping `Updated:` on an
   already-satisfied archived endpoint on every re-run — contradicting D4
   ("one bullet per real mutation") and D3 ("zero bytes").
   `test_relate_archived_no_op_with_reason_writes_nothing` asserts exit 0,
   whole-tree byte-identity, no `Revision:`, and no INDEX.
4. **The self-declared CLI rollback gap was avoidable.** See the corrected
   *Accepted coverage boundary* note in the Phase-4 record above — the
   read-only-**directory** injection closes the successful-rollback half
   end-to-end; only `ROLLBACK FAILED` remains unit-seam-only, and the log
   now says that accurately instead of over-claiming.

### nits

5. One stale "73 failing ids" survived the earlier restatement — fixed (and
   the whole record re-baselined to 87).
6. `test_check_missing_inverse_exits_2_and_names_repair` asserted
   `"a.md" in proc.stdout`, which cannot fail: `a.md` also occurs inside
   the message body. Now asserts `"a.md" in proc.stdout.splitlines()` — the
   bare **grouping header** line, which is what the assertion message
   claims to test.
7. The happy-path `Updated:` assertion only checked the old value was gone
   (deleting the field would have passed). Now asserts
   `Updated: <today>` positively, matching the archived test's rigor.
8. Four spec strings had no lock; all four added —
   `--root <dir> does not contain .docs.toml; refusing`
   (`test_relate_root_without_docs_toml_refuses`), the parser's
   self-locating malformed-endpoint message (folded into
   `test_relate_malformed_endpoint_exits_1`, which distinguishes a clean
   refusal from a lucky exit 1), the non-null `reason` echo in `--json`
   (`test_relate_json_echoes_a_non_null_reason`), and the reindex honouring
   `[exclude]` / `.docsignore` (`test_relate_reindex_honours_exclusion`).
9. The legacy-regression lock parametrized 4 of the fixture trees; it now
   derives the list from `tests/fixtures/trees/` (every directory not
   prefixed `reciprocal-`), so **18** trees are covered and any tree added
   later is covered for free. Its docstring, which over-claimed "must not
   change any pre-existing tree's finding multiset" while the body filtered
   only `missing-inverse`, was narrowed to match the body.
10. The "no conflict detection" statement had no lock — a plausible
    over-fire trap for a naive per-doc implementation.
    `test_check_tree_no_conflict_detection` has `a.md` declare **both**
    `precedes: b.md` and `follows: b.md` with `b.md` reciprocating both,
    and asserts a clean tree.
11. `tests/test_relate_plan.py` implicitly required the rollback to go
    through the module-global `cli.atomic_write`, which no spec stated.
    Rather than relax the injection, this is now **stated in D5**: the
    rollback must inherit the same tmpfile + fsync + rename durability as
    the publish it undoes (a restore torn by a crash is the very failure
    the rollback exists to prevent), and keeping the seam monkeypatchable
    is the only way the failure path is testable at all.
12. The `remove` direction was untested at the plan seam. Added
    `test_plan_relate_remove_marks_both_halves_removed` (both halves
    `present_before=True` / `present_after=False`, `change == "removed"`,
    `updated_bumped`, no `Revision:` on active endpoints) and
    `test_plan_relate_remove_of_an_absent_edge_is_unchanged`.

### Post-fold-in gate

- `pytest tests/ -q` — **87 failed, 670 passed**; `--co` — **757
  collected** (636 + 121). Zero collection errors, **zero real tracebacks**
  (`grep -c "Traceback (most recent call last)"` → 0), zero xfails.
- RED split re-verified: 25 `AttributeError`, 43 `docs relate` subprocess
  (30 returncode + **13** contract-string — every intended-exit-2 test
  still fails on its message, none falsely GREEN), 17 check-side, 1
  `Revision`, 1 SKILL.md.
- GREEN-at-baseline locks grew 15 → **34** (7 check-side degenerate + 18
  legacy-tree parametrizations + 1 self-edge + 3 canonical-path + 1
  conflict + 1 clean-reciprocal CLI + 3 mv/archive).
- `src/docs_cli/cli.py`, `pyproject.toml`, and `tests/test_packaging.py`
  are **byte-untouched** across the entire step (`git diff bf8f273..HEAD`
  on each → empty).
- `docs/cli.md` ↔ `src/docs_cli/skill/references/cli.md` and the
  `convention.md` pair byte-identical; `docs/INDEX.md` ↔
  `tests/fixtures/expected/docs-INDEX.md` in lockstep.
- `ruff check` / `ruff format --check` / `mypy src/ tests/` /
  `docs check --root docs` — all clean.

## Phase 5 — Update Base Interfaces — 2026-08-12

### Objective

Land the vocabulary, the three text editors, the planning models, and the
`Revision` built-in label — every interface the Phase-1 *Frozen Phase-5
signatures* block names — without completing any behaviour. Interfaces
typecheck; the tests stay honestly RED at the behaviour seam.

### Actions taken (all in `src/docs_cli/cli.py`)

- **`import posixpath`** — the one new import, used by amendment B's
  canonicalisation. `os.path.normpath` would flip separators on Windows;
  `Related:` targets are POSIX on every platform.
- **`RECIPROCAL_INVERSES` / `RECIPROCAL_VERBS`** beside `BUILTIN_ROLES`:
  six entries, three symmetric pairs, with the case-sensitivity and
  deliberate-non-membership rationale in the comment.
- **`_BUILTIN_METADATA_FIELDS` gains `"Revision"`**, with the D4 rationale
  recorded above it: a label `docs relate` itself writes must never trip the
  tool's own `unknown-field` allowlist warning.
- **`inverse_verb`** beside `validate_lifecycle` / `validate_role` — the
  single "this verb gains no reciprocal validation" signal shared by the
  check pass (skip) and the CLI (refuse).
- **`CoordinatedWriteError(OSError)`** beside `MetadataError` /
  `VocabularyError`, carrying `rolled_back` + `published`. `str(exc)` is the
  fully-rendered operator message (the single-arg `OSError` form), so
  `_cmd_relate` can print `docs: relate: {exc}` exactly — the
  `MetadataError(f"{path}: {exc}")` precedent.
- **`RelateEdit` / `RelatePlan`** after `MigrationPlan`, in exactly the
  frozen shape. No derived helpers: `edit.change != "unchanged"` is the
  "did this endpoint move" predicate everywhere.
- **The three editors** immediately after `rewrite_related_refs`, on the M2
  surgical minimal-diff contract (`_metadata_line_span` +
  `splitlines(keepends=True)`): `add_related_edge`, `remove_related_edge`,
  `append_revision_entry`. Two small shared helpers keep them honest —
  `_related_run` (the one place that locates the `Related:` bare-label group
  and its bullet run) and `_bullet_matches` (canonical target comparison).
- **`_canonical_related_target`** and **`_related_pairs`** beside
  `_root_relative`.
- **`relate_plan_to_json`** fully implemented (pure field mapping); its test
  stays RED because it needs a real `plan_relate`.
- **Three behaviour seams stubbed** with real signatures + full docstrings
  and `raise NotImplementedError("M25 Phase 6")` bodies:
  `reciprocity_findings` (between `check_doc` and `check_tree`),
  `plan_relate` and `apply_relate_plan` (in a new *Relationship repair —
  `docs relate` (M25)* section before the `# CLI` banner). `check_tree` is
  NOT touched in Phase 5, so no stub is ever called.

### Decisions / issues

- **The editors compare targets CANONICALLY (conductor resolution R1).**
  Both `add_related_edge` and `remove_related_edge` route through
  `_bullet_matches`, which normalises via `_canonical_related_target`.
  Without it, `docs relate add a.md precedes b.md` against an existing
  bullet reading `- precedes: ./b.md` would APPEND A DUPLICATE — `relate`
  would stop being idempotent on exactly the loosely-spelled trees
  amendment B exists to tolerate. `rewrite_related_refs` is deliberately
  left alone: it is `mv`'s tool and M28's territory.
- **Stubs, not omissions (conductor resolution R8).** The phase objective is
  "planning models/helpers … without completing behaviour" and its exit
  criterion is "interfaces typecheck; tests remain honestly RED at the
  behaviour seam", so the three functions land with signatures and
  docstrings now and bodies in Phase 6. This makes the Phase-5 commit a
  reviewable contract-in-code.
- **RED-reason change to record against the Phase-4 classification table.**
  Of the 27 tests that stay RED for Phase 6, the **10** plan/apply/JSON ones
  (classified `AttributeError` in that table) now fail with
  `NotImplementedError` instead — the symbols exist, the bodies do not. The
  other **17** (check-side) were classified as plain assertions and still
  are, because `check_tree` deliberately does not yet call
  `reciprocity_findings`. The Phase-4 table is a record of the Phase-4
  baseline, not a claim about later phases; this note keeps it from being
  read as stale.

### Verification

- `.venv/bin/python -m pytest tests/ -q` — **71 failed, 686 passed**
  (exactly the planned Phase-5 ledger: 16 flipped GREEN — 1 inverse-map +
  14 editor + 1 `Revision` field).
- `.venv/bin/python -m pytest tests/test_edit.py tests/test_check.py -q` —
  the 14 editor tests and the `Revision` `unknown-field` lock are GREEN.
- `.venv/bin/ruff check .` — All checks passed.
  `.venv/bin/ruff format --check .` — clean.
  `.venv/bin/mypy src/ tests/` — no issues in 46 source files.
- `docs relate --help` still exits 2 (`invalid choice`) — the verb is not
  wired, as intended.
- `git diff --stat pyproject.toml tests/test_packaging.py` — **empty**; the
  version stays 1.8.0 (D6).

## Phase 6 — Implement Offline/Core Path — 2026-08-12

### Objective

Implement the cross-document reciprocity pass and the validate-all-first,
idempotent coordinated edit — including the archived audit boundary and the
D5 publish/rollback contract — with no CLI surface yet.

### Actions taken (all in `src/docs_cli/cli.py`)

- **`reciprocity_findings`** — two passes over the materialised walk. Pass 1
  indexes every doc whose metadata block parses, keyed by root-relative
  path; a `MetadataError` doc is skipped (as source AND as target —
  `malformed` owns it). Pass 2 walks each indexed source's `Related:` pairs:
  a free-form verb is skipped, a self-edge is skipped (amendment A), and a
  target missing from the index is skipped. **That single `index.get`
  implements four of the five applicability conditions at once** —
  excluded, unresolvable, and non-Markdown targets were never walked, and
  malformed ones were dropped in pass 1. Deliberately NOT five branches: per
  condition special-casing would be dead code Phase 10 would remove.
- Satisfaction requires the inverse to **point back at the source**
  (`v == inverse and canonical(t) == source_rel`), not merely to exist —
  `test_check_tree_inverse_pointing_elsewhere_is_still_missing` exists to
  catch a "does the target declare `follows` at all?" implementation.
  Dedupe is on `(verb, canonical target)` per source.
- **`check_tree`** now materialises the walk once, runs the reciprocity pass
  over it, and interleaves `recip.get(path, ())` after each doc's
  `check_doc` findings. Its docstring's "errors before warnings" sentence
  was corrected to the real rule — `check_doc`'s findings first in its own
  order, then any `missing-inverse` — rather than adding a resort;
  `test_check_tree_findings_grouped_by_path` pins the ordered rule list.
- **Free reuse taken:** `check_doc`'s broken-ref loop was `_related_pairs`
  inlined, so it now calls `_related_pairs`. One `Related:`-bullet parser in
  the module. Behaviour-preserving line for line;
  `test_check_doc_broken_related_ref` is its lock.
- **`plan_relate` + `_plan_relate_edit`** — pure w.r.t. writes; reads both
  endpoints; `edits` is always `(source, target)`. Per endpoint: apply the
  edit, and **if nothing changed, return immediately** with
  `new_text is original`, `change="unchanged"`, no `Updated:` bump and no
  `Revision:` bullet. That early return is the whole of D3's idempotency and
  D4's "one bullet per REAL mutation" — the lock is
  `test_relate_archived_no_op_with_reason_writes_nothing`. Only after a real
  change: bump `Updated:`, then append the `Revision:` bullet for an
  archived endpoint.
- **`apply_relate_plan` + `_rollback_relate`** — stage 3 re-validates each
  staged text, stage 4 pre-flights writability, stage 5 publishes in plan
  order and rolls back on a later failure. Both the publish and the restore
  call the module-global `atomic_write` by bare name (binding per D5, and
  the only reason the injected-failure tests can reach the path at all).

### Decisions / issues

- **Stage 4 is `os.access` on the FILE and nothing else.** Two tests bracket
  it exactly: `test_relate_unwritable_endpoint_refuses_before_any_write`
  (mode-0400 file → stage 4 must fire) and
  `test_relate_second_write_failure_rolls_back_and_says_so` (mode-555
  *directory*, mode-644 file → stage 4 must NOT fire, so stage 5 can).
  Adding a parent-directory check "for robustness" would break the second
  and silently delete the rollback's only end-to-end coverage. The code
  carries that reasoning as a comment so it is not "helpfully" added later.
- **R3 — the nothing-published rollback branch.** When the FIRST publish
  fails, the frozen `rolled back <rel>` list is empty and the message
  degenerates to `rolled back  — the tree is unchanged`. A third branch now
  renders `write failed for <rel>: <err>; nothing was published — the tree
  is unchanged` (still exit 2, still `rolled_back=True`). Pinned in `cli.md`
  in Phase 7. This is a bug fix to a frozen string, not a scope change.
- **R4 — the ROLLBACK FAILED message was add-shaped.** After a failed
  rollback of a `remove`, the file no longer carries the edge, so the frozen
  wording handed the operator a factually inverted repair instruction.
  `_rollback_relate` now renders `still carries` for `add` and `no longer
  carries` for `remove`; the literal `ROLLBACK FAILED` token that Phase 1
  grep-verified is preserved either way. Both variants pinned in `cli.md` in
  Phase 7.
- **R7 — `Revision:` uses the tree's `date_format`.** `date_str` (already
  rendered by the CLI in `config.date_format`) is used for both `Updated:`
  and the `Revision:` bullet. Two date spellings in one file would be a
  defect; "ISO-dated" in D4 describes the *default* format.

### Verification

- `.venv/bin/python -m pytest tests/ -q` — **44 failed, 713 passed**
  (exactly the planned Phase-6 ledger: 27 flipped GREEN — 17 check-side +
  10 plan-seam).
- **Verified by name, not by count:** all 44 remaining failures are
  `tests/test_cli_relate.py` (43) and
  `tests/test_skill.py::test_skill_md_documents_relate_verb` (1) — both
  Phase-7 surfaces.
- `.venv/bin/docs check --root docs` — no violations, exit 0. The live
  tree's 10 complete recognized pairs now pass a rule that actually runs;
  `test_check_dogfood_repo_docs_is_clean` stops being degenerate.
- `.venv/bin/ruff check .` / `ruff format --check .` / `mypy src/ tests/` —
  all clean.
- `git diff --stat pyproject.toml tests/test_packaging.py` — **empty**.

## Phase 7 — Update Tool/Wrapper Layer — 2026-08-12

### Objective

Wire `docs relate add|remove` — parser, endpoint resolution, human/JSON/
dry-run output, exit codes, the one end-of-run reindex — and bring every
shipped surface into parity: the bundled skill, the CHANGELOG, the specs,
and the tracker docs.

### Actions taken

**`src/docs_cli/cli.py`**

- `_add_relate_subverb` beside `_add_exclude_flag`, registering `add` and
  `remove` with `parents=[common]` (`--root` / `--quiet` / `--dry-run`) plus
  `SOURCE VERB TARGET`, `--reason`, `--date`, `--json`. **`VERB` uses no
  argparse `choices=`**: argparse's own "invalid choice" message would
  replace the frozen `docs: relate: unknown verb '<verb>'; expected one of:
  …` refusal that eight tests assert.
- The `relate` namespace registered after the `project` block, shaped
  identically (`add_subparsers(dest="relate_command", required=True)`).
- `_resolve_relate_endpoint` — absolute as given, otherwise root-relative
  first with a cwd-relative fallback; then not-a-file → exit 1, outside the
  resolved root → exit 1, unparseable → exit 1 with the parser's own
  self-locating message. It parses through `root / rel` (not the resolved
  path) so that message names the file the way the tree does.
- `_print_relate_lines` renders all nine human forms; the caller gates it on
  `not --quiet` **alone** — not on `--json`, since the lines go to stderr
  and `--json` stdout stays byte-clean either way.
- `_cmd_relate` in the D5 stage-1 order: managed root → config → verb →
  SOURCE → TARGET → self-edge → `--reason` shape (only when the flag is
  present) → the archived `--reason` requirement (only when it is absent) →
  `--date` → plan → dry-run/no-op → apply → announce → one reindex → JSON →
  exit. `return 0 if index_refreshed else 2`.
- `_dispatch` gained the `relate` branch; `main`'s docstring and the module
  docstring name the verb.

**`src/docs_cli/skill/SKILL.md`** — front-matter `description:` verb run
gains `relate add` / `relate remove`; the verb table gains a
`docs relate add` / `docs relate remove` row; the `docs check` row now says
a one-sided reciprocal edge is a hard error and names `docs relate` as its
repair. Both edits land in the same change as the CLI surface, per the
project's surface-parity gate.

**`CHANGELOG.md`** — a new `## UNRELEASED` section at the top carrying **no
invented version number** (D6; M29 renames and dates it): `### Added` (the
`missing-inverse` rule, `docs relate add|remove`, audited archived repair +
the `Revision` built-in label), `### Changed` (**BREAKING** — a one-sided
recognized edge now exits 2; the withdrawn `Lifecycle: blocked` +
one-sided-`blocked-by` recommendation), and an `### Upgrading from 1.x`
worked `check → relate → check` loop. `pyproject.toml` untouched.

**`docs/cli.md` (+ byte-identical mirror re-sync)** — eight conductor-resolved
spec corrections, listed under *Decisions* below.

**Tracker docs** — `docs/plan.md` (v2.0-train prose + the M25 row),
`docs/status.md` (the Current-milestone narrative, the *Next action*
paragraph, and the milestone-history row), this log, and the milestone doc.

### Decisions / issues — the eight spec corrections (conductor resolutions)

Each fixes a string the tests do not pin and that would otherwise ship
wrong or degenerate. None changes milestone scope or behaviour intent.

- **R2 — the stage-3 refusal string is now pinned.** `cli.md`'s stage-3
  bullet carries `docs: relate: staged text for <rel> would not parse
  (<detail>); refusing before any write`, plus an explicit statement that it
  is defensive-only and unreachable in practice. Deliberately **no test**
  fakes it: a spec the implementation can outrun is what the Step-1 audit
  caught twice, but a test that fakes an unreachable path pins the fake.
- **R3 — a third rollback branch.** When the FIRST publish fails there is
  nothing to roll back and the frozen line degenerated to
  `rolled back  — the tree is unchanged`. `nothing was published — the tree
  is unchanged` is now rendered and pinned. Still exit 2, still
  `rolled_back=True`.
- **R4 — the `ROLLBACK FAILED` message was add-shaped.** After a failed
  rollback of a `remove` the file *no longer* carries the edge, so the
  frozen wording handed the operator a factually inverted repair
  instruction. Both variants (`still carries` / `no longer carries`) are now
  rendered and pinned; the literal `ROLLBACK FAILED` token is preserved.
- **R5 — the root-relative promise is scoped to RESOLVED endpoints.** A
  pre-resolution refusal cannot name a root-relative form it has not
  computed. `cli.md` now says so, and `file not found:` names the
  **root-relative candidate** (`<root>/<arg>`) for a relative argument,
  since root-relative is the primary interpretation.
- **R6 — `--json` on failure paths.** No record on a coordinated-write
  failure (the operation aborted; after a `ROLLBACK FAILED` the `applied`
  bit is genuinely undefined). A record **is** emitted on an INDEX-refresh
  failure, `applied: true, index_refreshed: false` — `cli.md` already framed
  that as a *post-repair* failure with a consistent tree.
- **R7 — `Revision:` uses the tree's `date_format`.** The same `date_str` as
  `Updated:`. `cli.md` now says the ISO spelling in its example is the
  **default** format, not a second hardcoded one.
- **R1 / R9 (no code change beyond Phase 5) —** `cli.md` › *What gets
  written* records that bullets are matched on their **canonical** target
  (else `relate` stops being idempotent on loosely-spelled trees), and
  *Endpoint resolution* records that `relate` deliberately **allows** an
  excluded endpoint: an explicitly named endpoint beats a coarse exclusion,
  and refusing would make the pair unrepairable. The silence is now
  deliberate rather than accidental.

Also recorded: **R10** — the Step-1 consistency audit fixed only the first
occurrence of the "Phase 1 next" claim in `status.md`, leaving the *Next
action* paragraph and the milestone-history row stale. Both are corrected
here. The lesson for the next audit: check **every** occurrence of a stale
claim, not just the first one grep finds.

### One Step-1 test carried a defective assertion (raised here, resolved in Phase 8)

Phase 7 ended at **756 passed, 1 failed**, one short of the planned 757.
The single RED was not missing behaviour: a Step-1 contract test carried an
assertion no implementation could satisfy. It was raised for an operator
decision rather than edited — a Step-1 test is the contract, and changing
one is not this step's call. The full evidence, the operator's binding
resolution, and the process observation are recorded in the **Phase 8**
record below.

### Verification

- `.venv/bin/python -m pytest tests/ -q` — **756 passed, 1 failed** (the
  defective assertion noted above; 42 of the 43 `docs relate` CLI tests and
  both SKILL.md tests are GREEN).
- `.venv/bin/docs relate --help` / `docs relate add --help` — exit 0,
  documenting `SOURCE`, `VERB`, `TARGET`, `--reason`, `--date`, `--json`,
  `--dry-run`. `docs --help` lists `relate`.
- `diff docs/cli.md src/docs_cli/skill/references/cli.md` and the
  `convention.md` pair — identical (`tests/test_skill_refs.py` 3 passed).
- `.venv/bin/docs check --root docs` — no violations, exit 0.
- `.venv/bin/ruff check .` / `ruff format --check .` / `mypy src/ tests/` —
  all clean.
- `git diff --stat bf8f273..HEAD -- pyproject.toml tests/test_packaging.py`
  — **empty** across the whole step.

## Phase 8 — Run Tests (GREEN) — 2026-08-12

### Objective

Run the focused and full suites plus lint, format, types, reference
byte-identity, and docs integrity; prove the pre-existing suite did not
regress rather than asserting it.

### The one test correction (operator-approved)

Phase 7 ended one test short of GREEN. The RED was **not** missing
behaviour:
`tests/test_cli_relate.py::test_relate_repeat_archived_repair_appends_a_second_revision_bullet`
carried an assertion no implementation could satisfy.

**The defect.** Its final line compared substring offsets across the
**whole archived file**:

```python
assert text.index("2026-08-11") < text.index("2026-08-12"), "chronological"
```

The second invocation passes `--date 2026-08-12`, and D4 requires
`Updated:` to be bumped on every endpoint whose bytes change — so
`Updated: 2026-08-12` sits on line 6, **above** the `Revision:` group.
`text.index("2026-08-12")` therefore resolved to that line at **offset 62**,
while `text.index("2026-08-11")` resolved to the first `Revision:` bullet at
**offset 142**. `142 < 62` is false for every possible implementation.

**Why it is a test defect and not unmet behaviour.** Three independent
proofs:

1. The test's stated intent — the two `Revision:` bullets are appended
   chronologically — *is* satisfied. The same test's three preceding
   assertions (exactly one `Revision:` label; both exact bullet strings
   present) pass against the shipped code.
2. Suppressing the `Updated:` bump is impossible: it would break
   `test_relate_archived_repair_writes_only_the_allowed_bytes`, which
   positively requires `Updated: 2026-01-01` to be removed and
   `Updated: 2026-08-11` added. **The two tests are mutually exclusive as
   written** — no implementation satisfies both.
3. Moving the `Revision:` group above `Updated:` would break D4 ("at the
   END of the metadata block, after `Related:`") and
   `test_append_revision_entry_creates_the_group_after_related`.

**Resolution.** Raised for an operator decision rather than edited in
Phase 7 — a Step-1 test is the contract, and changing one is not the
implementation step's call. The **operator approved** narrowing the
assertion to what its own failure message claims:

```python
bullets = [line for line in text.splitlines() if line.startswith("- 2026-")]
assert bullets == [
    "- 2026-08-11: relate add 'required-by: a.md'; reason: complete the pair",
    "- 2026-08-12: relate remove 'required-by: a.md'; reason: edge was wrong",
], "chronological"
```

The replacement is **stronger, not weaker**: it pins both bullet texts
*and* their order, where the original pinned two substring offsets (one of
which was matching an unrelated line). **The shipped behaviour was NOT
changed to satisfy it** — `git diff src/docs_cli/cli.py` for the correcting
commit (`7e4feb1`) is empty, and the test passed on the first run against
the unmodified Phase-7 code, which is the confirmation that the diagnosis
was complete rather than partial.

**Process observation.** Both the Step-1 same-instance audit and the
independent fresh-eyes review read this test and neither caught it. The
failure mode to add to the checklist: **a whole-file substring-offset
comparison** (`text.index(a) < text.index(b)`) silently matches the first
occurrence anywhere in the file, so it can assert something quite different
from what its message claims — and, unlike the Step-1 audit's finding #6
(an assertion that could never *fail*), this one could never *pass*. Scope
such comparisons to the lines actually under test.

### Headline

```
.venv/bin/python -m pytest tests/ -q
757 passed in 32.17s

.venv/bin/python -m pytest tests/ -q --co
757 tests collected
```

### No-regression proof (mechanical, not asserted)

Repeating the Phase-4 technique with `--co -q` id lists against a throwaway
worktree at the Phase-1 commit `3dca105`:

| Set | Count |
|---|---|
| pre-existing ids at `3dca105` | **636** |
| ids collected today | **757** |
| `comm -12` (pre-existing ids still present) | **636** |
| `comm -23` (pre-existing ids missing today) | **0** |
| `comm -13` (ids added by M25) | **121** |

No pre-existing id was removed or renamed, and the full run reports
**0 failures**, so all 636 pre-existing tests are GREEN. 636 + 121 = 757.

### Other gates

- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 45 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 46 source files.
- `.venv/bin/docs check --root docs` — no violations, exit 0.
- `.venv/bin/docs check --root docs --json` — `[]` (asserted programmatically).
- `git diff --stat bf8f273..HEAD -- pyproject.toml tests/test_packaging.py`
  — **empty** across the whole step. `docs --version` → `docs 1.8.0`;
  `pyproject.toml` `version = "1.8.0"` (D6).
- `docs --help` lists `relate`; `docs relate --help` and
  `docs relate add --help` exit 0.

### Surface evidence recorded

`docs check tests/fixtures/trees/reciprocal-missing` — exit 2, human:

```
a.md
  error: [missing-inverse] Related: 'precedes: b.md' has no inverse; b.md must declare 'follows: a.md' (or remove the edge)
```

`--json` — exit 2, exactly one record, and the key set is the unchanged
closed four:

```json
[
  {
    "path": "a.md",
    "severity": "error",
    "rule": "missing-inverse",
    "message": "Related: 'precedes: b.md' has no inverse; b.md must declare 'follows: a.md' (or remove the edge)"
  }
]
```

## Phase 9 — Integrate / Accept / Dogfood — 2026-08-12

### Objective

Exercise the real upgrade workflow — detect a deliberately removed inverse,
repair it, remove an invalid pair, and repair an archived endpoint with an
audit reason — on a **throwaway copy** of this repo's own docs tree. The
real `docs/` tree is never the subject.

Setup: `cp -r docs "$T"` into the session scratchpad; every command below
runs with `--root "$T"`. The copy was deleted at the end.

### Flow 1 — baseline

`docs check --root "$T"` → `docs: no violations found`, exit 0. The live
tree's recognized pairs are all complete, so the new hard rule is satisfied
out of the box. Archive baseline captured:
`find "$T/archive" -type f -name '*.md' | xargs sha256sum | sort` → **46
files**.

### Flow 2 — detect

Hand-deleted `- follows: m25-reciprocal-relationship-integrity.md` from
`m26-safe-archive-selection.md` (a plain `grep -v`, not a `docs` verb — this
simulates the legacy one-sided edge an upgrading tree would have).

`docs check --root "$T"` → **exit 2**, exactly one finding:

```
m25-reciprocal-relationship-integrity.md
  error: [missing-inverse] Related: 'precedes: m26-safe-archive-selection.md' has no inverse; m26-safe-archive-selection.md must declare 'follows: m25-reciprocal-relationship-integrity.md' (or remove the edge)
```

It blames the **source**, and names the source, the verb, the target, and
the exact missing inverse. `--json`: total findings **1**, `missing-inverse`
records **1**, key set exactly `['message', 'path', 'rule', 'severity']` —
M25 adds no JSON field.

### Flow 3 — repair (add)

Paths copied **verbatim out of the finding**, with the invocation run from
the repo root rather than inside the tree — the root-relative-first
resolution (OQ-A) is what makes that work without translation:

```console
$ docs relate add m25-reciprocal-relationship-integrity.md precedes m26-safe-archive-selection.md --root "$T"
docs: relate: no change — 'precedes: m26-safe-archive-selection.md' already present in m25-reciprocal-relationship-integrity.md
docs: relate: added 'follows: m25-reciprocal-relationship-integrity.md' to m26-safe-archive-selection.md
```

exit 0; only the missing half was written. `INDEX.md` was refreshed, and a
following `docs index --root "$T"` is a **byte no-op** (sha256 before ==
after) — proving the one end-of-run reindex was complete, not partial.
`docs check --root "$T"` → exit 0.

### Flow 4 — repair (remove), restore, and idempotency

`docs relate remove …` dropped **both** halves (`grep -c` → 0 in each
endpoint) and `docs check` stayed at exit 0 — the other valid repair for the
same finding. `relate add` restored the pair (check exit 0). A **second**
`relate add` printed two `no change — … already present in …` lines, exit 0,
and the sha256 manifest of every top-level doc was **identical** before and
after: a fully-satisfied invocation writes zero bytes.

### Flow 5 — archived repair

**5a — without `--reason`:**

```console
$ docs relate add status.md depends-on archive/2026-07-03/m24-pypi-publish.md --root "$T"
docs: relate: archive/2026-07-03/m24-pypi-publish.md is under the archive subtree; --reason is required
```

exit 2, and the sha256 of **both** endpoints was unchanged — the rule fires
before planning, so nothing is written.

**5b — with `--reason`:** exit 0, with `recorded revision in
archive/2026-07-03/m24-pypi-publish.md`. The complete diff of the archived
doc is exactly the three permitted changes:

```diff
6c6
< Updated: 2026-07-03
---
> Updated: 2026-08-12
16a17,20
> - required-by: status.md
>
> Revision:
> - 2026-08-12: relate add 'required-by: status.md'; reason: M25 Phase-9 dogfood
```

`Lifecycle: archived`, `Archived-reason:`, `Role: milestone`,
`Project: docs`, and the H1 each still occur exactly once, and the entire
body from the first `##` heading down is **byte-identical**
(sha256 `0d68f196…` before and after).

**5c — `relate remove … --reason "dogfood cleanup"`:** exit 0. The archived
doc now carries **one** `Revision:` label with two bullets, chronologically:

```
- 2026-08-12: relate add 'required-by: status.md'; reason: M25 Phase-9 dogfood
- 2026-08-12: relate remove 'required-by: status.md'; reason: dogfood cleanup
```

`docs check --root "$T"` → exit 0 throughout.

### Flow 6 — blast radius

Re-hashed the whole archive subtree and joined it against the baseline: the
file **set** is unchanged (no adds, no removes) and **exactly one** of the
46 archived files differs —
`archive/2026-07-03/m24-pypi-publish.md`, the one deliberately repaired.
The other 45 are byte-identical. The narrow archived exception is narrow in
practice, not just in the spec.

### Flow 7 — preview and machine output

`--dry-run` on a fresh pair printed the two `would add …` lines and changed
**zero bytes anywhere in the tree, `INDEX.md` included** (sha256 manifest of
every `*.md` identical before and after).

`--json` stdout parses standalone while the two human lines go to stderr.
The preview and the apply records have **identical key sets**
(`action, applied, date, dry_run, edits, index_refreshed, inverse, reason,
source, target, verb`), differing only in the three status bits —
preview `dry_run=True applied=False index_refreshed=False`, apply
`dry_run=False applied=True index_refreshed=True` — so a preview and an
apply are diffable, as D3 requires.

### Flow 8 — the real tree is untouched

`git status --short docs/` and `git diff HEAD -- docs/` are both **empty**
(the Phase-7/8 tracker edits were already committed), and
`docs check --root docs` exits 0. The throwaway copy was removed.

### Decisions / issues

- Nothing failed and nothing needed a workaround; all eight flows ran
  unattended.
- The dogfood confirms the upgrade story end-to-end in the order the
  CHANGELOG's *Upgrading from 1.x* section prescribes: `check` names the
  incomplete edge → the agent chooses `relate add` or `relate remove` → the
  paths copy across without translation → `check` is clean.

## Phase 10 — Quality, Docs, Refactor — 2026-08-12

### Objective

Closure only. A separate `/simplify` pass runs afterwards as Step 3, so
this phase deliberately does **no** speculative refactoring, abstraction
hunting, or helper-collapsing sweeps.

### Actions taken

1. **Placeholder sweep.** `grep -n "TODO\|FIXME\|NotImplementedError\|XXX"
   src/docs_cli/cli.py` → **no matches**. All three Phase-5 stubs have real
   bodies.
2. **Docstring accuracy.** `Finding.rule` listed only the seven M3 rule ids
   and had silently fallen three behind — it now names `unknown-field`
   (M10), `medium-confidence-inference` (`docs migrate --triage`), and
   `missing-inverse` (M25), plus an explicit statement that the JSON
   record's key set is **closed** at `{path, severity, rule, message}` and
   a new rule adds a value here rather than a field there.
   (`check_tree`'s ordering sentence and the module docstring's milestone
   paragraph were already corrected in Phases 6 and 7.)
3. **Spec closure.** `docs/architecture.md` — the `model` section now names
   the three M25 editors beside `set_metadata_field` /
   `rewrite_related_refs` / `scaffold_doc` and records that they share
   `_related_run` and `_metadata_line_span`; two **new** sections, `check`
   and `relate`, describe the cross-document reciprocity pass (and why the
   applicability conditions collapse into one index lookup) and the
   plan/apply split with its best-effort-publish-plus-rollback contract.
   The file previously had no `check` section at all.
   `docs/test-strategy.md` — the enumerated fixture-tree list now carries
   the `reciprocal-*` family with its one-semantic-per-tree rule, the
   no-dates-so-nothing-rots note, and the reason mutation-shaped cases use
   inline `tmp_path` builders instead.
4. **Use-case catalog.** `src/docs_cli/skill/references/use-cases.md` — a
   new **Upgrade: repair reciprocal relationships (M25)** section with the
   six-row scenario table and the `check → relate add|remove → check` loop,
   plus a `docs relate` row in the greenfield table and the `docs check`
   row extended to mention one-sided edges. The setup record deferred this
   to "only when the behavior exists"; it now does.
5. **Completion summaries.** This log's *Milestone completion summary* and
   the milestone doc's *Success criteria* filled with evidence; Phases 8–10
   ticked; `docs touch` + INDEX snapshot re-synced.

### Deliberately NOT done (Step 3 owns it)

No helper was collapsed, no abstraction removed, no "clever code replaced
with obvious code" sweep. `_related_run`, `_bullet_matches`,
`_plan_relate_edit`, `_rollback_relate`, and `_print_relate_lines` are all
single-purpose extractions that already earn their keep; whether any of
them should fold back into a caller is `/simplify`'s judgement, not this
phase's.

### Verification

- `.venv/bin/python -m pytest tests/ -q` — **757 passed** at the time this
  phase closed. The fresh-eyes fold-in below later took it to **777**.
- `.venv/bin/ruff check .` / `ruff format --check .` / `mypy src/ tests/` —
  all clean.
- `.venv/bin/docs check --root docs` — no violations, exit 0.
- `pyproject.toml` and `tests/test_packaging.py` byte-untouched across the
  whole step; `docs --version` → `docs 1.8.0`; CHANGELOG still under
  `## UNRELEASED`.

### Hand-off

M25 is **implementation-complete** and stays `Lifecycle: active` until the
M29 publish closeout — it ships as part of the batched 2.0.0 release, not
on its own. **M26 — Safe explicit archive selection is ready to prepare.**
Host-machine skills are deliberately **not** refreshed here: per the
project's CLAUDE.md skill-update policy that happens only at a production
ship (M29), and `docs install-skill --force` from an unpublished tree would
put pre-release guidance on the host.

## Fresh-eyes review fold-in — Step 2 — 2026-08-12

Independent review of Step 2 returned **no blockers**: the reviewer re-ran
the full gate, confirmed every parity and version invariant, and reproduced
the modified-assertion justification end-to-end (unsatisfiable, stronger,
`cli.py` byte-unchanged in `7e4feb1`). Everything below is defect repair,
coverage hardening, or one operator-approved scope addition.

### Operator-approved scope addition — D7 `duplicate-field`

**This arrived after the contract froze and after fresh-eyes review.** It is
not part of the Phase-1 frozen contract and is deliberately not backdated
into it; see the milestone doc's **D7 (BINDING — added 2026-08-12,
POST-FREEZE)**.

The reviewer found that a doc with two `Related:` labels yields a
`missing-inverse` no `docs relate` invocation can clear — the parser is
**last-wins**, the editors are **find-first**. The conductor traced it to a
deeper defect: `parse_metadata_block` does
`metadata[label] = tuple(values)`, so a second copy of ANY label overwrites
the first and silently discards every value under it, before `docs check`,
INDEX generation, or `Related:` resolution ever runs. It predates M25; the
unfixable finding is only the symptom that exposed it.

**Operator-required pre-flight, run BEFORE implementing.** The live `docs/`
tree (69 docs) and **all 28** committed fixture trees (~300 docs) were
scanned with the block-aware label counter: **zero duplicate labels**. No
existing tree needed editing to suit the new rule — the standing
instruction was to stop and report rather than edit a fixture to fit.

Implemented as a self-contained **test-first mini-cycle** inside Phase 10:

1. **Contract** — `cli.md` gained a rule bullet, a *Duplicate metadata
   labels* subsection (frozen message, one-per-label dedupe, the data-loss
   rationale, the manual repair, and why `docs relate` will not do it), the
   rule-id table entry, and the exit-code-2 list. `convention.md` gained
   *Each label appears at most once* under *Metadata block*. Mirrors
   re-synced byte-identically.
2. **Tests (RED first)** — 8 RED across `tests/test_check.py` (duplicated
   bare-label group; duplicated scalar; one of each yielding two findings in
   block order; a thrice-repeated label yielding ONE finding; the committed
   tree) and `tests/test_cli_check.py` (subprocess exit 2 + message; the
   `--json` record's closed key set). Plus two negative locks that were
   GREEN from the start and must stay so: a long `Related:` run beside a
   `Revision:` run — the exact shape `docs relate` writes — must never fire,
   and a clean doc must not either. A rule that counted bullets instead of
   labels would fire on every real doc in the tree.
3. **Implement** — `_duplicate_labels(text)` beside `_related_pairs`,
   consumed by **`check_doc`** (a per-doc rule; deliberately NOT in
   `reciprocity_findings`). It scans the metadata block's raw label lines
   via `_metadata_line_span` + `_LABEL_RE`, skipping each bare label's
   bullet run wholesale, and returns `{label: count}` for counts > 1 in
   first-appearance order. Detecting it from `parse_metadata_block`'s output
   is impossible — the duplicate is already gone by then.
4. **GREEN, and the interaction confirmed.** New committed fixture
   `tests/fixtures/trees/duplicate-field/` isolates the pure case (one
   semantic per tree, so it emits `duplicate-field` and nothing else — a
   committed tree that also emitted `missing-inverse` would trip the
   `test_check_tree_legacy_fixtures_gain_no_new_findings` lock). The
   co-occurrence is pinned inline by
   `test_check_tree_duplicate_field_diagnoses_the_unfixable_missing_inverse`,
   which builds the reviewer's exact shape (first label free-form, last
   label carrying the un-reciprocated edge), asserts the rules are
   `["duplicate-field", "missing-inverse"]`, and then asserts that
   `remove_related_edge` returns `changed is False` — i.e. that the repair
   `missing-inverse` names really is a no-op there. Verified live too:
   `docs relate remove` prints `no change — 'precedes: b.md' already absent
   from a.md` and exits 0 while the finding survives. **The previously
   silent, unfixable state is now named.**

### should-fix — two real defects in the M25 editors

1. **Trailing-newline state was NOT preserved when the metadata block runs
   to EOF.** All three editors insert/delete newline-terminated lines, so a
   doc with no body silently **gained** a trailing newline on
   `add_related_edge` / `append_revision_entry`, and kept one on a
   `remove_related_edge` that deleted the unterminated final line. This
   contradicted `cli.md` › *What gets written*, `convention.md`, and — most
   seriously — **D4's allowed-byte set**, the milestone's strongest claim.
   **Fixed in the code, not by narrowing the spec:** a shared
   `_preserve_tail(original, edited)` strips exactly one trailing newline
   when the original lacked it.
   The existing coverage was **falsely reassuring**:
   `test_add_related_edge_preserves_absent_trailing_newline` used
   `WELL_FORMED.rstrip("\n")`, which still has a body, so the insertion
   point was mid-file and the tail was never touched. A `NO_BODY` fixture
   plus three new tests now exercise the real case for all three editors.
2. **A re-created `Related:` group landed AFTER a trailing `Revision:`
   group.** Reachable in a plausible archived sequence: `relate remove`
   drops the last recognized edge and its emptied label, then `relate add`
   re-creates the group at the end of the block — past `Revision:`. D4,
   `cli.md` › *`Revision:` encoding*, `convention.md`, and
   `append_revision_entry`'s own docstring all place `Revision:` at the END.
   Shape drift, not corruption (the doc still parsed, `docs check` stayed
   clean), but the spec said otherwise. The creation branch now inserts
   before a bare `Revision:` label, at its preceding blank line.

### nits

3. **`--dry-run` never previewed the `Revision:` bullet** — an archived
   repair's most consequential effect was invisible in the human preview,
   though `--json` always carried `revision_appended`. Now emits
   `docs: relate: would record revision in <rel>`; the form is added to
   `cli.md` › *Output* and locked by a test.
4. **Four missing locks added.** The `nothing was published` branch
   end-to-end (a half-satisfied `add` whose only write fails, via a
   `chmod 555` parent dir — a *realistic* path, not a contrived one); BOTH
   `ROLLBACK FAILED` message variants asserted verbatim (the existing test
   reached the branch but asserted only `rolled_back`/`published`, so
   **R4's entire point — the `remove`-shaped `no longer carries` wording —
   was unpinned**); `relate`'s canonical-target idempotency at the CLI seam
   (R1 was pinned for the check rule only); and R9's
   excluded-endpoint-allowed. Stage-3's `staged text … would not parse`
   stays deliberately **untested** per R2 — the reviewer agrees a test there
   would pin a fake.
5. **Two CHANGELOG examples carried the defect this step's own audit had
   already fixed in `cli.md`** — a finding line without its file-grouping
   line or two-space indent, and a `docs relate add` shown producing no
   output when it always prints two stderr lines. Both now mirror `cli.md`'s
   worked example verbatim.

### Observation, not a fix

`set_metadata_field` (M2) has the same latent trailing-newline behaviour on
its *insert* path. It is **not reachable from `relate`**: `plan_relate` only
calls it for `Updated:`, which is a required field that `parse()` has
already validated as present, so the replace path — which preserves the
line ending exactly — always wins. Left alone as out-of-scope M2 code rather
than widening this step's blast radius; recorded here so it is not
rediscovered as a surprise.

## Same-instance consistency audit — Step 2 (Phases 5–10) — 2026-08-12

Run against this step's own work per the ship-milestone consistency-check
reference, after Phase 10 and before handing back. Findings and fixes:

### Accuracy — code vs. spec

1. **A worked example showed a `docs check` output format the tool does not
   produce.** `cli.md` › *Worked upgrade example* and both CHANGELOG
   examples rendered the finding as
   `  error  missing-inverse  <message>` (two spaces, no colon, no
   brackets). `_print_check_findings` has emitted
   `  <severity>: [<rule>] <message>` since M19, and does so today —
   verified live against `tests/fixtures/trees/reciprocal-missing` and in
   the Phase-9 dogfood. **Fixed** in `docs/cli.md`, the bundled mirror, and
   `CHANGELOG.md` (three occurrences). The code was right; the docs were
   wrong. The defect entered in Phase 1 and was copied forward in Phase 7 —
   a reminder that an *illustrative* block still has to be executed once.
2. **The same example was internally inconsistent.** Its `docs check` header
   read `docs/m25.md` while the following `docs relate add` used bare
   `m25.md`. That quietly undercuts the very property OQ-A exists to
   deliver — a path copied out of a finding resolving without translation.
   **Fixed:** the header now reads `m25.md`, matching the invocation.
3. **The milestone doc's D3 still carried the pre-R5 unscoped promise**
   ("Every message and every JSON field names the root-relative POSIX
   form"), which `cli.md` had already corrected to apply to **resolved**
   endpoints only. **Fixed** — D3 now matches `cli.md` and additionally
   records R9 (an excluded endpoint is deliberately allowed).
4. **The milestone doc's D4 and resolved-question 2 still said
   "ISO-dated"** where R7 had established that the `Revision:` bullet uses
   the tree's `date_format` and ISO is merely the default. **Fixed** in both
   places.

### Accuracy — the two failure branches no test exercises end-to-end

Both were reproduced live during the audit rather than trusted:

- **R3 (`nothing was published`)** is reachable in a *realistic* scenario,
  not just a theoretical one: a half-satisfied `add` where only the target
  changes and that single write fails. Reproduced with a `chmod 555`
  parent directory:
  `docs: relate: write failed for sub/b.md: [Errno 13] Permission denied: '…/sub/b.md.docs-tmp'; nothing was published — the tree is unchanged`
  (exit 2). Without R3 this would have read `rolled back  — the tree is
  unchanged`, with a double space and an empty list.
- **R4 (both `ROLLBACK FAILED` variants)** reproduced at the unit seam by
  injecting a failing `atomic_write`:
  `… ROLLBACK FAILED for a.md — repair manually: a.md still carries 'precedes: b.md'` for `add`, and
  `… no longer carries 'precedes: b.md'` for `remove`, both with
  `rolled_back=False` and `published=('a.md',)`. The pre-R4 wording would
  have told an operator recovering from a failed `remove` that the file
  *still carries* an edge it no longer has.

### Verified clean (no fix needed)

- **All nine human output forms** in `cli.md` › *Output* were executed live
  and match the spec block **byte-for-byte**, including the `would remove`
  form that no test covers end-to-end.
- Every literal message string `cli.md` pins for `relate` is present in both
  the spec and `src/docs_cli/cli.py` (23 strings checked pairwise).
- The exit-code summary row, the `missing-inverse` rule-table entry, the
  closed JSON key set, the six applicability conditions, the canonical
  path-matching paragraph, and `convention.md`'s *Reciprocal relationship
  verbs* / *Audited relationship repair* sections all describe the shipped
  behaviour accurately.
- No `TODO`/`FIXME`/`NotImplementedError`/commented-out code in `cli.py`.
- `git diff --name-only d26086d..HEAD` touches only `docs/`,
  `src/docs_cli/`, `tests/`, and `CHANGELOG.md`; within `tests/` only the
  frozen INDEX snapshot and the one operator-approved assertion.
- Bundled mirrors byte-identical; `docs/INDEX.md` ↔
  `tests/fixtures/expected/docs-INDEX.md` in lockstep; `docs check --root
  docs` exit 0, so every `Related:` edge resolves.
- Every doc edited in this step had `Updated:` bumped via `docs touch`.
- One commit per phase on `m25/phases-5-10` with `m25(phase N): …`
  messages; no secrets staged.
- `pyproject.toml` and `tests/test_packaging.py` byte-untouched across the
  entire step.

### Fixed during the audit — internal consistency

5. The Phase-7 record said "**six** conductor-resolved spec corrections"
   while it enumerated eight (R1–R7 plus R9) and the milestone doc, plan,
   and status all said eight. **Fixed** to eight in all three places in
   this log.
6. The Phase-5 record's RED-reason note read as though all 27 Phase-6 tests
   had been classified `AttributeError`; only the 10 plan/apply/JSON ones
   were, and only those changed to `NotImplementedError`. **Fixed** to say
   so precisely.

### Surfaced for an operator decision

Nothing changed milestone scope or behaviour intent, so nothing is blocked
on an operator. One **non-blocking** style note is handed to the Step-3
`/simplify` pass rather than churned here: `_print_relate_lines` picks its
verb with a nested conditional expression
(`("would add" if dry_run else "added") if adding else (…)`). It is correct
and covered, but a small mapping would read better — and readability
refactoring is explicitly `/simplify`'s job, not Phase 10's.

## Same-instance consistency audit — post-review fold-in — 2026-08-12

A second pass of the consistency-check reference, scoped to the fold-in work
(the two editor fixes, the four added locks, and D7).

### Accuracy — code vs. spec

1. **Verified, not assumed:** the `duplicate-field` message rendered live by
   `docs check tests/fixtures/trees/duplicate-field` is byte-identical to
   the string frozen in `cli.md` (`metadata field 'Related:' appears 2
   times; only the last occurrence is read`), and the `--json` record's key
   set is still the closed four. The `would record revision in <rel>` form
   is present in both the code and `cli.md` › *Output*.
2. `convention.md`'s *Each label appears at most once* and `cli.md`'s
   *Duplicate metadata labels* agree with each other and with the
   implementation: structural counting, inline and bare alike, one finding
   per repeated label, bullets-under-one-label exempt.

### Consistency — documentation (fixed)

3. **Five stale `757` counts.** The milestone doc's Progress line, its
   RED/GREEN deliverable, and its final Success-criteria line, plus
   `status.md`'s Step-2 sentence and its *Next action* paragraph, all still
   claimed 757 after the fold-in took the suite to 777. **Fixed.**
4. **`status.md` framed the Step-1 figures as the current total** ("M25 so
   far contributes 121 test items: 757 collected…"). **Fixed** to state
   them as Step 1's contribution and the RED baseline, which is what they
   are.
5. **The Phase-10 record's verification said 757 while the Phase-10 phase-
   table row said 777.** Rather than rewrite a dated phase record, the
   verification line now reads "**757 passed** at the time this phase
   closed. The fresh-eyes fold-in below later took it to **777**." Dated
   records stay historical; only forward-looking claims were updated. The
   Phase-4 and Phase-8 records keep their own figures untouched for the
   same reason.

### Verified clean (no fix needed)

- No `TODO`/`FIXME`/`NotImplementedError`/commented-out code in `cli.py`.
- Diff scope is still confined to `docs/`, `src/docs_cli/`, `tests/`, and
  `CHANGELOG.md`.
- Mirrors byte-identical; `docs/INDEX.md` ↔
  `tests/fixtures/expected/docs-INDEX.md` in lockstep; `docs check --root
  docs` exit 0.
- `pyproject.toml` and `tests/test_packaging.py` byte-untouched across the
  entire milestone; `docs --version` → `docs 1.8.0`; CHANGELOG still under
  `## UNRELEASED`.
- **No-regression re-proven after D7**, which is exactly the kind of new
  rule that could disturb a pre-existing fixture: 636 ids at `3dca105`,
  `comm -12` → 636, `comm -23` → **0**, `comm -13` → 141, 777 collected,
  0 failures.

### Surfaced for an operator decision

Nothing. The one open style note is unchanged and still belongs to the
Step-3 `/simplify` pass: `_print_relate_lines`'s nested conditional.

## Milestone completion summary

**M25 — Reciprocal relationship integrity and `docs relate` is
implementation-complete (2026-08-12).** All ten TDD phases are done across
two branches: Phases 1–4 (contract + RED baseline) on `m25/phases-1-4`,
Phases 5–10 (implementation → dogfood → closeout) on `m25/phases-5-10`.

### What shipped

- **Six recognized reciprocal verbs** in three symmetric pairs
  (`precedes`/`follows`, `depends-on`/`required-by`,
  `blocks`/`blocked-by`), matched case-sensitively. Every other `Related:`
  verb stays free-form with no reciprocal validation.
- **A hard `missing-inverse` `docs check` rule** — error, exit 2, attached
  to the source, one per distinct `(source, verb, canonical target)`
  triple, with a frozen single-line message that names both possible
  repairs without choosing. No new JSON field. Excluded, unresolvable,
  non-Markdown, malformed, and self-referential targets are exempt; the
  owning rules keep their cases.
- **`docs relate add|remove SOURCE VERB TARGET`** — idempotent,
  validate-all-first, two-document coordinated edit with `--dry-run`,
  `--json`, `--quiet`, `--reason`, `--date`, `--root`; one end-of-run
  reindex; no whole-tree pre-flight; staged publish with rollback and an
  explicit non-atomic admission when a rollback itself fails.
- **Audited archived-endpoint repair** — `--reason` required whenever
  either endpoint is archived (checked before planning), with the change
  limited to one `Related:` bullet, `Updated:`, and a dated `Revision:`
  audit bullet.
- **A hard `duplicate-field` rule** (D7, added post-freeze) — a metadata
  label appears at most once; repeatability lives in the bullets under a
  bare label. Error, exit 2, one finding per repeated label, detected on the
  raw block because the parser has already discarded the evidence. Closes a
  **silent data-loss** defect that predates M25.
- **Full surface parity** — `cli.md`, `convention.md`, the byte-identical
  bundled mirrors, `SKILL.md`, the use-case catalog, and a CHANGELOG
  `UNRELEASED` section carrying **two** BREAKING notices and an *Upgrading
  from 1.x* worked loop covering both rules.

### Final ledger

| Gate | Result |
|---|---|
| `pytest tests/ -q` | **777 passed, 0 failed** (636 pre-existing + 141 M25) |
| Pre-existing regressions | **0**, proven by `comm` against `3dca105`'s 636 ids |
| `ruff check` / `ruff format --check` | clean / 45 files formatted |
| `mypy src/ tests/` | no issues in 46 source files |
| `docs check --root docs` | exit 0; `--json` → `[]` |
| Bundled mirrors | byte-identical to `docs/cli.md` / `docs/convention.md` |
| INDEX snapshot | `docs/INDEX.md` ↔ `tests/fixtures/expected/docs-INDEX.md` in lockstep |
| Version | **1.8.0, unmoved** — `pyproject.toml` and `tests/test_packaging.py` byte-untouched across the entire milestone (D6) |
| Dogfood | eight flows, unattended, on a throwaway tree copy; 1 of 46 archived files touched |

### Deviations from the plan, and why

- **Phase 1 made zero `cli.py` edits** despite its file list naming
  contract-level signatures (logged and approved at the time); the
  signatures were frozen in the milestone Decisions and landed in Phase 5.
- **Eight spec corrections landed in Phase 7** (conductor resolutions
  R1–R7, R9) that Phase 1 had frozen wrong or left unpinned — most
  materially a third rollback branch for a first-publish failure (the
  frozen string degenerated to `rolled back  — …` with an empty list) and a
  remove-shaped `ROLLBACK FAILED` admission (the frozen wording was
  add-shaped and would have handed the operator an inverted repair
  instruction).
- **One Step-1 test assertion was corrected under operator approval** in
  Phase 8 — it was unsatisfiable in conjunction with another test in the
  same file. The replacement is stronger, and the shipped behaviour was not
  changed to accommodate it. Full evidence in the Phase-8 record.
- **D7 `duplicate-field` was added POST-FREEZE**, after Phase 10 and after
  fresh-eyes review, as an operator-approved response to a review finding —
  it widens the frozen contract and is breaking for existing trees. It is
  recorded as its own decision rather than folded into D1–D6, so the
  contract history is not retroactively rewritten. Implemented test-first
  as a mini-cycle inside Phase 10, after verifying the live tree and all 28
  fixture trees were duplicate-free.

### Follow-ons

- **M29** renames and dates the `UNRELEASED` CHANGELOG heading and performs
  the single bump to `2.0.0`; host-machine skills are refreshed there, not
  here.
- **M26 — Safe explicit archive selection** is ready to prepare.
- A **Step-3 `/simplify` pass** runs against this implementation next;
  Phase 10 deliberately left that work to it.

## `/simplify` pass — Step 3 — 2026-08-12

Post-implementation simplify mode against M25's `src/docs_cli/cli.py` diff
(`bf8f273...44daab0`). Baseline established first and preserved exactly:
**777 passed** before and after, `ruff` / `ruff format --check` / `mypy` /
`docs check --root docs` clean at both ends. Net **-17 lines** in `cli.py`;
no other source file touched.

**Not a single shipped byte of behaviour moved.** Every string literal in
the diff appears an even number of times (removed once, re-added once) —
audited mechanically, not by eye. No test was relaxed, rewritten, or
deleted; no exit code, JSON field, or output format changed;
`pyproject.toml` and `tests/test_packaging.py` are byte-untouched and the
version stays **1.8.0**.

### 1. Three hand-rolled bare-label scans collapsed to one

`_related_run` located the `Related:` group, and the *identical* scan —
match `_LABEL_RE`, require a bare label, walk the `- ` bullet run — was
written out twice more by hand for `Revision:`: once in
`add_related_edge`'s group-creation path (which needs the label index) and
once in `append_revision_entry` (which needs the run end).

Renamed to **`_bare_label_run(lines, start, end, label)`** — one new
parameter, no new layer — and the two open-coded copies now call it. The
helper's docstring already claimed the M25 editors "agree on where the
group is"; with three separate scans that was aspirational, and it is now
structurally true. `append_revision_entry`'s twelve-line loop becomes four.

`docs/architecture.md`'s `model` section named `_related_run` as the shared
group locator; updated to `_bare_label_run` with the label-parameterised
note. **Not** a mirrored reference — only `cli.md` and `convention.md` are
byte-mirrored into `src/docs_cli/skill/references/`, and neither changed,
so `tests/test_skill_refs.py` is untouched.

### 2. `_plan_relate_edit`: one `RelateEdit` construction, not two

The `unchanged` early return built the full eleven-field `RelateEdit` and
then the changed path built it again, duplicating eight identical field
values — a shape where adding a twelfth field means remembering to edit two
places. The early return is now an `if changed:` guard that computes
`change` / `new_text` / `revision_appended` in place, followed by a single
constructor. `updated_bumped=changed` states the invariant the two literals
(`False` / `True`) previously only implied. The contractual ordering the
archived byte-delta assertion pins — edge, then `Updated:`, then the
`Revision:` bullet — is unchanged; the docstring's "that single early
return" now reads "that single `if changed:` guard".

### 3. `_print_relate_lines`: word choices hoisted out of the loop

The handover's candidate. The nested conditional expression

```
verb = ("would add" if dry_run else "added") if adding
       else ("would remove" if dry_run else "removed")
```

was not the real problem — the real problem was that `state`, `verb`,
`preposition`, and `recorded` are all fixed by `plan.action` and `dry_run`,
yet three of them were re-derived on every iteration, which is what forced
the branching into the loop body in the first place. A **mapping was
considered and rejected**: keying on `(action, dry_run)` adds a lookup
concept to save nothing. Instead all four are chosen once, in a flat
`if/else` before the loop, where a reader can see the four add-words and
the four remove-words side by side and check them against `cli.md` in one
glance. The loop body is now two straight `print`s and the `continue`
disappears.

### 4. `_duplicate_labels`: one cursor advance, not two

`idx += 1` appeared on both the no-match and the matched path — two places
to keep in sync in a hand-driven `while` cursor. Advancing once,
immediately after the match attempt, leaves the bullet-run skip as the only
other place the cursor moves.

### Considered and deliberately left alone

- **`apply_relate_plan`'s three rollback branches.** `unrestored` /
  `published` / neither produce three genuinely different frozen strings
  with three different operator meanings (R3 and R4 exist precisely because
  collapsing them was wrong). Any merge re-introduces the degenerate
  `rolled back  — …` R3 was written to kill.
- **`atomic_write` call sites.** Left as bare module-global calls in both
  `apply_relate_plan` and `_rollback_relate` — the D5 binding. Inlining or
  aliasing would silently delete the rollback tests' only injection point.
- **The stage-4 writability pre-flight.** Still `os.access` on the **file**
  only. Adding the "obvious" parent-directory check would convert a
  stage-5-with-rollback into a stage-4 refusal and break R3's coverage.
- **`_cmd_relate`'s validate-all-first sequence.** Long, but it is a flat
  run of guard clauses in refusal order — already the linear form
  `/simplify` asks for. Any extraction would hide the ordering that makes
  "every refusal leaves the tree byte-identical" checkable by reading top
  to bottom.
- **`_preserve_tail`, `_bullet_matches`, `_related_pairs`,
  `reciprocity_findings`.** Single-purpose and already minimal;
  `reciprocity_findings`'s two passes are the reason the five applicability
  conditions are one index lookup rather than five branches.
- **The archived-path predicate** (`rel == config.archive_dir or
  rel.startswith(config.archive_dir + "/")`), which M25 writes twice. A
  shared helper would have to serve the four *pre-existing* copies too, and
  rewriting those is out of this pass's scope; a two-site, one-line
  predicate does not earn a helper on its own.

### Verification

| Gate | Result |
|---|---|
| `.venv/bin/python -m pytest tests/ -q` | **777 passed, 0 failed** — identical to the baseline |
| `.venv/bin/ruff check .` | All checks passed |
| `.venv/bin/ruff format --check .` | 45 files already formatted |
| `.venv/bin/mypy src/ tests/` | no issues in 46 source files |
| `.venv/bin/docs check --root docs` | no violations, exit 0 |
| Shipped strings | unchanged — every literal in the diff balanced -/+ |
| Version | **1.8.0**; `pyproject.toml` / `tests/test_packaging.py` byte-untouched |
