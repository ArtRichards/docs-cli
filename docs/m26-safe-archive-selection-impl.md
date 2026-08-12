# M26 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-08-13

Related:
- child-of: m26-safe-archive-selection.md
- pairs-with: m26-safe-archive-selection.md
- pairs-with: status.md
- references: feedback-log.md

## Overview

Chronological implementation log for M26 — Safe explicit archive selection.
Append one evidence-backed section per TDD phase; keep the progress table and
the milestone checklist synchronized.

## Implementation metadata

- Project: docs
- Milestone: M26 — Safe explicit archive selection
- Started: 2026-08-12 (milestone setup; no TDD phase started)
- Progress: **Phases 1–2 complete (2026-08-12 / 2026-08-13).** All seven
  setup questions were RESOLVED before Phase 1 (Q1/Q5/Q6 by the operator;
  Q2/Q3/Q4/Q7 conductor-resolved) and Phase 1 did not re-open them; it froze
  the exact surface against them, plus the seventeen Step-1 planning
  questions. Phase 2 wrote the RED suite (863 collected) and closed two
  Phase-1 gaps. Phase 3 — Create Data/Fixtures is next.
- Source: the operator-confirmed cascade-safety decision in `feedback-log.md`
  (2026-08-09/10) and the M26 registration in `plan.md` (2026-08-10).
- Branch: `m26/milestone-setup` for setup; `m26/phases-1-4` for Step 1
  (Phases 1–4).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | **Done** | 2026-08-12 | Froze the compatibility matrix, the message catalog (refusals, preview/apply lines, partial-state admission), the exit-code split, the `--json` schema and field table, and the Phase-5 signatures. Seventeen Step-1 planning questions recorded as BINDING. No `cli.py` edit (logged deviation). |
| 2. Write Tests (RED) | **Done** | 2026-08-13 | +89 items (863 collected): new `tests/test_archive_plan.py` (32), `tests/test_cli_archive.py` (+34, 6 pre-existing ids deliberately changed and 3 deleted/replaced), `tests/test_skill.py` (+2), `tests/test_cli_check.py` (+1). Two Phase-1 gaps closed: ineligibility-reason precedence and the nine-step check order. |
| 3. Create Data/Fixtures | Pending | — | One-semantic-per-tree candidate (E1), duplicate (E2), collision (E3), and archived-neighbour (E4) trees. |
| 4. Run Tests (RED Baseline) | Pending | — | Capture the classified failure set; prove no unrelated regression. |
| 5. Update Base Interfaces | Pending | — | Archive plan/move models, candidate-planning helpers, pre-flight validators, `archive_plan_to_json`; no behaviour change. |
| 6. Implement Offline/Core Path | Pending | — | Validate-all-first planning, deduplication, archived exclusion, collision detection, safe refusal, partial-state admission. |
| 7. Update Tool/Wrapper Layer | Pending | — | argparse surface (refusing flags + local `--json`), human output, JSON record, docs, bundled skill, CHANGELOG (no version bump). |
| 8. Run Tests (GREEN) | Pending | — | Full product and quality gates with exact counts. |
| 9. Integrate / Accept / Dogfood | Pending | — | Preview + scoped archive of a real milestone pair on a throwaway tree copy. |
| 10. Quality, Docs, Refactor | Pending | — | Simplify, close docs, completion summaries, hand off to M27. |

## Setup record — 2026-08-12

### Objective

Bring the registered M26 draft stub up to full milestone-task-plan depth and
create this log, without starting Phase 1. M25 is implementation-complete and
merged to `main`, so M26 is the next implementation milestone in the v2.0
train.

### Actions taken

- Re-derived the stub's four Phase-1 open questions against the real v1.8.0
  implementation (`_cascade_set`, `_cascade_archive`, `_archive_one`,
  `_cmd_archive`) and against `cli.md`, `convention.md`, and `feedback-log.md`.
- Reproduced the current cascade behaviour on throwaway trees and on a
  read-only preview of this repo's own docs tree; the evidence is tabulated
  below and drives the milestone's *Current state and risks* section.
- Expanded *Binding scope* into seven decisions (D1–D7), added *Out of scope*,
  the ten-phase TDD plan with per-phase objective/files/exit, the phase
  checklist, the testing gate, and evidence-anchored success criteria.
- Kept the reciprocal `follows`/`precedes` and `required-by` edges intact and
  added the milestone↔log pair edges.
- Raised seven setup questions with recommendations rather than deciding any
  of them silently, and then **resolved all seven before Phase 1** — Q1
  (`--interactive` retirement), Q5 (atomicity boundary), and Q6
  (`docs archive --json`) by operator decision; Q2 (refusing-flag retention),
  Q3 (candidate verb set), Q4 (already-archived documents), and Q7
  (primary-only notice) conductor-resolved from the specs, `plan.md`,
  `CLAUDE.md`, and the M14/M18/M25 precedent. Every resolution is recorded in
  the milestone doc's *Resolved setup questions (Q1–Q7, BINDING)* and folded
  into the binding scope D1–D8.
- Scaffolded this log with `docs new log m26-safe-archive-selection-impl`,
  bumped dates and validated with
  `docs touch … --check` (exit 0), and refreshed the frozen dogfood INDEX
  snapshot `tests/fixtures/expected/docs-INDEX.md` for the new log entry
  (22 → 23 active docs) — the same snapshot refresh the M25 setup performed.
- Updated the trackers: `status.md` (current milestone, train listing, next
  action, milestone-progress row) and `plan.md` (v2.0 narrative and the M26
  row) now describe M26 as in flight with its plan and log linked.

### Current-behaviour evidence (docs-cli 1.8.0, reproduced during setup)

| Evidence | Invocation | Observed today | Why it matters | Fixed by |
|---|---|---|---|---|
| **E1** | `docs archive m25-reciprocal-relationship-integrity.md --cascade-dry-run` on this repo | Would archive **6** related docs: `plan.md`, the impl log, `cli.md`, `convention.md`, `test-strategy.md`, `status.md` | Bare `--cascade` on a completed milestone would move this project's entire spec spine into the archive | D2 refusal |
| **E2** | `--cascade` where one doc is reachable by two edges (`pairs-with` + `child-of`) | `docs: could not archive b.md: [Errno 2] No such file or directory`, then `cascade archived 1 related doc(s)`, **exit 0** | A successful operation prints a false failure; no deduplication exists | D3 dedup |
| **E3** | `--cascade` where two candidates share a basename (`x/dup.md`, `y/dup.md`) | `x/dup.md` archived, `y/dup.md` left behind, bare-path error message, **exit 0**, and `docs check` afterwards reports **no violations** | A partial multi-document write reports success and leaves no detectable drift | D4 pre-flight |
| **E4** | `--cascade` where a candidate is already archived (`archive/2026-01-01/old.md`) | Silently relocated to `archive/2026-08-12/old.md` with `Updated:` rewritten from `2026-01-01` to `2026-08-12` | History is rewritten; on this tree `status.md` carries 20+ archive-subtree `pairs-with` edges | D3 exclusion + D4 primary refusal |
| **E5** | `--cascade-only 'typo-*'` where candidates exist but none match | `docs: cascade: no one-hop relations to archive`, primary archived, **exit 0** | A typo'd scope is indistinguishable from a deliberate primary-only archive | D5 empty-selection refusal |

E1 was produced with `--cascade-dry-run` against the live tree (writes
nothing); E2–E5 were produced on disposable trees outside the repository. No
repository file was mutated during setup.

### Verification

- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 45 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 46 source files.
- `.venv/bin/python -m pytest -q` — 777 passed.
- `.venv/bin/docs check --root docs` — no violations found.

### Decisions / issues

- The v1.8.0 defects in the evidence table are **not** separate bug fixes; they
  are exactly the behaviour M26's planning model replaces, so they are fixed as
  a consequence of D2–D5 rather than as standalone patches. They are carried in
  the milestone doc as **E1–E5** and each maps to named regression coverage in
  its *Evidence → regression coverage* table.
- **E4 is data corruption, not just over-reach**, and is squarely in M26's
  remit (Q4): bare `--cascade` relocates and re-dates an already-archived
  document. It is load-bearing on the live tree, where `status.md` carries 20+
  archive-subtree edges. Archived documents are excluded from the candidate
  set with a named ineligibility reason, and an already-archived **primary**
  is refused.
- **`docs archive --json` is in scope** (Q6): one operation-plan record, the
  same shape for preview and apply, reusing M25's `relate --json` pattern —
  primary, candidates, selected, excluded-with-reason, destinations, and
  whether anything was written. It gets its own tests and its own `cli.md` /
  bundled-skill surface-parity rows.
- **Atomicity boundary settled at pre-flight** (Q5): every handled error
  refuses with zero mutation; a residual mid-execution `OSError` is reported
  as an exact partial-state admission and is **not** rolled back. Extending
  M25 — D5's staged-publish-plus-rollback to N documents was considered and
  **explicitly declined** for M26; it is recorded in the milestone doc so a
  later milestone can pick it up.
- Version staging is already settled by M25 — D6: the package stays `1.8.0`
  through M25–M28 and M29 performs the single bump to `2.0.0`. M26 touches
  neither `pyproject.toml` nor the packaging version pins; its CHANGELOG
  entries accumulate under the existing `UNRELEASED` heading.
- Host-machine workflow skills (notably `create-milestones`, which prescribes
  `docs archive <slug>.md --cascade` at milestone completion) are **not**
  updated by this milestone. Per `CLAUDE.md`, host skills refresh only at a
  production ship, and `plan.md` records the Agent Playbook Suite update as a
  post-M29 cross-repository follow-up. The bundled skill inside
  `src/docs_cli/skill/` **is** updated in lockstep, in Phase 7.
- **No OPEN QUESTIONS remain.** All seven are resolved and recorded as binding
  in the milestone doc; Phase 1 freezes exact messages, exit codes, and the
  `--json` schema against them rather than re-litigating scope.

## Phase 1 — Define Contract — 2026-08-12

### Objective

Freeze every byte of surface Phase 2 will assert against: the compatibility
matrix (no "it depends" cell), the refusal / preview / apply / partial-state
message catalog, the exit-code split, the candidate discovery, dedup,
canonicalization and ineligibility rules, the `--json` operation-plan schema
and its field table, and the Phase-5 signatures. No business logic lands, and
the seven setup questions are not re-opened.

### Actions taken

**`docs/cli.md`** — the whole `docs archive` section rewritten (the heading's
flag list now reads `[--cascade-dry-run] [--cascade-only GLOB] [--json]
[--dry-run] [--quiet]`), with new subsections:

- *Safe explicit archive selection (M26 — D1)* — the three-shape
  authorization table, the quiet-stderr rule with its `--json` exception, and
  the `--cascade-only GLOB --dry-run` ≡ `--cascade-dry-run --cascade-only GLOB`
  equivalence.
- *Retired flags (M26 — D2)* — both verbatim refusal lines, the
  runs-first / independent-of-every-flag / prints-under-`--quiet` /
  no-argparse-mutex statements, the `--cascade`-wins tie-break, and an
  **Upgrading from 1.x** block with the two replacement invocations.
- *Candidate discovery (M26 — D3)* — one hop, the never-candidate reciprocal
  verbs, canonical dedup with first-declaration-wins, canonical scope
  matching, the silent self-edge exclusion, the explicit
  no-`[exclude]`-consultation statement, and the three-row ineligibility table
  (`already-archived`, `unresolved-target`, `outside-root`) plus the
  `not-selected` non-ineligibility.
- *Preview (M26 — D6)* — the ten verbatim stderr lines, the
  cascade-flag-gating of the `candidate` lines, the "a preview is never a
  write, so it never fails" exit-0 rule, and the two differences an apply
  shows.
- *The scoped write and its pre-flight (M26 — D4)* — the five per-member
  proofs (including the explicit writability access test and the
  nearest-existing-ancestor rule), the six verbatim pre-flight refusals, the
  all-three-shapes archived-primary statement, and the residual partial-state
  admission with its `Archived: none` branch.
- *An empty selection is a refusal (M26 — D5)* — the two write-path refusals,
  the definition of "matched" as *selected*, `<N>` counted over the whole
  deduplicated set, and the empty-pattern refusal.
- *`docs archive --json` (M26 — D7)* — the worked record, the seven-row field
  table in the `relate --json` style, the per-candidate key set, the closed
  key set, the always-present candidate list, and the
  no-record-on-refusal / record-on-INDEX-refresh-failure boundary.
- *`docs archive` exit codes* — the Q4 split as its own table.
- The M12 referring-edge and M18 archive-subtree-edge blocks kept, with
  `--cascade` prose updated to `--cascade-only`, the per-candidate-failure
  sentence replaced by the all-or-nothing statement, and a new sentence
  pinning the one-`(alias, new_rel)`-pair-per-declared-spelling rule.
- Deleted as now-false: the four-mutually-exclusive-flags paragraph, the
  `--cascade` / `--interactive` bullets, the "`--cascade-dry-run` alone is
  shorthand for `--cascade --dry-run`" sentence, the two legacy footer
  strings, and the old *Invariant: `docs` never prompts unless
  `--interactive`* paragraph (replaced by the unconditional
  **`docs archive` never prompts on stdin at all**).
- `## Exit codes (summary)`: both archive rows rewritten against the Q4 split.

**`docs/convention.md`** — new *Safe explicit archive selection (M26 — D1)*
paragraph in `## Archive subtree`, beside the M18 and M25 — D4 exceptions:
entry into the archive is authorized explicitly, never by relationship; the
three shapes; and the two author-facing rules (an archived doc is never
re-archived, in either role; `Archived-reason:` is primary-only).

**Milestone doc** — new `## Decisions (Phase 1 — BINDING)` carrying the
compatibility matrix, the Q4 exit split, the frozen message catalog, the
`--json` schema, the frozen Phase-5 signatures with their reuse list, the
seventeen resolved Step-1 planning questions, and the logged Phase-1
deviation. D1, D2, D3, D5, D6, and D7 amended in place so the binding scope
and the frozen contract cannot disagree — in particular **the D5/D6
contradiction is removed, not papered over** (D5 now says "a `--cascade-only`
**write** that selects nothing"; D6 states the exit-0 preview rule and both
cross-reference each other). Phase-1 checklist row and deliverable 1 ticked;
Progress line updated.

**Lockstep chores** — `cp docs/{cli,convention}.md
src/docs_cli/skill/references/`; `docs touch` on the four edited docs
(implicit reindex); `tests/fixtures/expected/docs-INDEX.md` re-synced from the
regenerated `docs/INDEX.md`.

### Decisions / issues

- **Q2 (operator) forced a real amendment, not a footnote.** The setup text
  had D5 ("an empty selection refuses, exit 2") and D6 ("a preview writes
  nothing and exits 0") both claiming
  `archive F --cascade-dry-run --cascade-only <no-match>`. D5 is now scoped to
  the **write** path in its own heading sentence, and D6 carries the exit-0
  rule explicitly with the `matched none` line and `"selected": []` named. The
  compatibility matrix has a dedicated row for the case.
- **Q4 (operator) — the exit-code split is a table, not prose.** Exit 1 stays
  for a plan member with no editable metadata block, an occupied destination
  slot, and the whole-tree pre-flight walk; the five new M26 refusals exit 2.
  The pre-existing pins (`cli.md`'s matrix row and
  `test_archive_referring_edge_rewrite_is_atomic`) therefore keep their exact
  meaning.
- **The `matched none` preview line is gated on `not --quiet`.** The operator's
  answer calls it "loud", which it is — it is on stderr and explicit — but
  making it the one preview line that ignores `--quiet` would add an
  it-depends rule to the very matrix D2 exists to flatten. `--quiet` plus a
  preview is already a contradiction in intent, and the `--json` record
  carries `"selected": []` for the machine consumer. Refusals, by contrast,
  **do** print under `--quiet` — they are failures, not output.
- **The `candidate` lines are identical in preview and apply.** Only the
  primary's verb (`would archive` / `archived`) and the presence of the
  `preview only — nothing was written` line distinguish the modes. A scoped
  write is all-or-nothing, so the plan is literally what happened; one form
  means one string to keep in parity, and it makes a preview/apply stderr diff
  as small and readable as the `--json` diff.
- **`docs: archive: <rel> has no editable metadata block; refusing before any
  write` was added to the catalog.** The Step-1 plan's catalog listed no
  message for the exit-1 metadata-block pre-flight refusal that its own test
  #17 (`test_preflight_refuses_a_candidate_without_a_metadata_block`)
  requires. Added in the same family and the same shape as its neighbours. The
  **primary**'s malformed case is unchanged — it is still caught by the
  existing `parse()` call before the plan exists, and still prints
  `docs: <exc>` at exit 1.
- **The frozen `--json` key set carries no `reason` field**, so `--reason` is
  observable only in the archived primary's `Archived-reason:` line, not in
  the operation-plan record — unlike `relate --json`, which does carry
  `reason`. The Step-1 plan froze the top-level key set as closed and ordered,
  so Phase 1 implemented it verbatim rather than widening the contract
  unilaterally. **Surfaced for the fresh-eyes review**; a Phase-7 addition
  would be a one-line schema change if the reviewer wants the symmetry.
- **Deviation (approved, same as M25).** Phase 1 made **zero** `cli.py` edits.
  Stubs would change the Phase-4 subprocess RED reasons and risk baseline
  behaviour, and the phase's own exit criterion is "no behavior changes". The
  signatures are frozen in the milestone doc's Decisions and land in Phase 5.
- **Phase-7 follow-through recorded by exact name:** `plan.md:454`'s stale
  resolved-question bullet (still claims `--cascade` prompts `y/N`);
  `src/docs_cli/skill/SKILL.md:62`'s archive row (lists `--cascade`);
  `src/docs_cli/skill/references/use-cases.md:25` ("`--cascade` opt-in for
  one-hop dependents"); `CHANGELOG.md` under `UNRELEASED`. Also noted, and
  **not** in the Phase-7 list: `docs/agent-native-invocation.md:250`, a
  `Lifecycle: draft`, `Project: ideas` proposal doc from 2026-06-03 whose
  Layer-5 bullet still names `--cascade` as a pre-answerable replacement for
  the prompt. It is a historical proposal record, not a spec on the
  surface-parity gate; left for the operator to decide.

### Verification

- `grep` for every verbatim string Phase 2 will assert, in `docs/cli.md` — all
  present (`is retired in docs 2.0 and writes nothing`,
  `is already under the archive subtree`, `--cascade-only must not be empty`,
  `matched none of the`, `has no one-hop pairs-with / child-of candidates`,
  `would both archive to`, `has no editable metadata block`,
  `archive destination already exists`, `is not writable; refusing before any
  write`, `candidate `, `— selected -> `, `not selected (outside
  --cascade-only`, `not selected (no --cascade-only scope)`,
  `ineligible (already archived)`, `ineligible (target does not resolve to a
  file)`, `ineligible (target resolves outside the docs root)`,
  `candidate(s): `, `preview only — nothing was written`,
  `PARTIAL ARCHIVE — not rolled back`, `Archived: none`, `not-selected`,
  `already-archived`, `unresolved-target`, `outside-root`).
- `.venv/bin/python -m pytest tests/test_skill_refs.py tests/test_cli_index.py
  tests/test_cli_check.py -q` — passed (bundled refs byte-identical; INDEX
  snapshot re-synced).
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 45 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 46 source files.
- `.venv/bin/python -m pytest -q` — **777 passed** (unchanged from the Phase-0
  baseline; no test file and no source file was touched in Phase 1).
- `.venv/bin/docs check --root docs` — no violations (exit 0).
- `git diff --stat src/docs_cli/cli.py` — **empty**, per the logged deviation.
- `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.


## Phase 2 — Write Tests (RED) — 2026-08-13

### Objective

Express the retirement, preview, scoped-write, pre-flight, and `--json`
behaviour before any implementation exists, including every failure path the
1.8.0 code silently swallows, so each Phase-5/6/7 change answers a written
test rather than the reverse.

### Authoring rules applied (carried from M25)

- **No module-level import of a Phase-5 symbol.** Each is reached through a
  one-line `_m26(name)` wrapper over `getattr(cli, name)` — a clean
  `AttributeError` at run time (never a collection error, which the Phase-4
  exit criterion forbids), `Any` for mypy, and no ruff `B009`.
- **Every intended-exit-2 test also asserts its contract stderr string.**
  Argparse already exits 2 on `unrecognized arguments: --json` and on the
  mutex group, so a returncode-only assertion would be falsely GREEN for the
  entire refusal family.
- **Every refusal test asserts whole-tree byte identity** through a shared
  `_snapshot(root) -> dict[str, bytes]` over `sorted(root.rglob("*"))`,
  `INDEX.md` and `.docs.toml` included. That is what makes "zero bytes
  written" a real assertion instead of a `not (root / "archive").exists()`
  proxy.
- Each docstring names its intended RED reason; every GREEN-at-baseline lock
  says so and says whether it is **degenerate** or **genuine**.

### Pre-existing tests M26 deliberately changes

The complete list — nothing else in the 777 moves. All in
`tests/test_cli_archive.py`.

| Test | Action | Baseline after edit |
|---|---|---|
| `test_archive_interactive_yes_also_archives_related` | **deleted** — the prompt path it pins no longer exists | — |
| `test_archive_interactive_no_leaves_related_in_place` | **deleted** — same | — |
| `test_archive_cascade_no_prompt_archives_all_relations` | **replaced** by `test_archive_bare_cascade_refuses_and_writes_nothing`; its take-all/exit-0 contract is exactly what D2 reverses | RED |
| `test_archive_cascade_dry_run_composes_with_cascade_only` | `assert "beta.md" not in stderr` **inverted** — D6 requires the unselected candidate to be named | RED |
| `test_archive_cascade_dry_run_rejects_interactive` | retirement-message assertion added; the bespoke "incoherent pair" message is retired | RED |
| `test_archive_mutually_exclusive_cascade_flags_rejected` (×3) | retirement-message assertion added per case, plus `not allowed with` asserted **absent**; docstring corrected (the mutex group is no longer what produces exit 2 — Phase-1 Q12) | RED |
| `test_archive_cascade_rewrites_edges_for_both_moves_atomically` | `--cascade` → `--cascade-only "sidekick.md"`, `stdin_text` dropped | GREEN |
| `test_archive_cascade_rewrites_moved_docs_own_edges` | same | GREEN |
| `test_archive_cascade_trio_lands_edge_clean` | `--cascade` → `--cascade-only "feature-*.md"`, `stdin_text` dropped | GREEN |
| `test_archive_cascade_preserves_reciprocal_pair` | `--cascade` → `--cascade-only "b.md"` | GREEN |

`test_archive_cascade_dry_run_previews_and_writes_nothing`,
`test_archive_cascade_only_filters_by_glob`, and
`test_archive_pair_leaves_check_clean` need **no** edit and stay GREEN — the
last one only gained a docstring note that M18 — Q3's "never bare `--cascade`
on the plan" advice has since become a hard refusal.

The bare `sidekick.md` / `b.md` / `feature-*.md` scopes work because
`_compile_docsignore_pattern` gives a no-slash pattern gitignore semantics:
match any path segment at any depth.

### New tests

**`tests/test_archive_plan.py`** (new, 32 items) — the core seam, modelled on
`tests/test_relate_plan.py`, every tree an inline `tmp_path` builder because
every test writes and byte-compares:

- **D3 candidate discovery (13):** the two-verb candidate set against all six
  M25 reciprocal verbs plus `references`/`implements`/`parent-of`;
  declaration order; dedup across two verbs (E2) and across two spellings,
  with `aliases` preserved; canonical scope matching (`./b.md` selected by
  `'b.md'`); the silent self-edge exclusion; `already-archived` (E4),
  `unresolved-target`, and `outside-root` ineligibility; the reason-precedence
  parametrization; `not-selected`; and the frozen
  `ARCHIVE_EXCLUSION_REASONS` token set.
- **D4 planning purity and pre-flight (13):** `plan_archive` writes nothing;
  the six refusals each asserting their **exact** message — intra-plan
  collision (E3), occupied destination, unwritable source, unwritable
  destination directory, archived primary (E4), member with no metadata
  block — plus a parametrization over all six asserting
  `rolled_back is True`, `published == ()`, and whole-tree byte identity.
- **D4 execution (3):** `apply_archive_plan` returns one `(old_rel, new_rel)`
  pair per declared spelling; the injected-`OSError` partial-state admission
  with its exact string, `rolled_back is False` and `published == (…)`,
  cross-checked against the disk; and the `Archived: none` branch.
- **D7 serializer (3):** the exact preview record, preview/apply shape
  identity, and the no-scope record carrying the whole candidate set.

**`tests/test_cli_archive.py`** (+34 items) — the subprocess surface:

- **Retirement / E1 (7 functions, 25 items):** bare `--cascade` refuses and
  writes nothing; the refusal names both replacement invocations;
  `--interactive` refuses; `--interactive` refuses **without reading stdin**
  (no `stdin_text` supplied — today EOF declines the prompt and the primary
  still archives at exit 0); the 2 × 8 flag matrix that makes "no it-depends
  cell" real and simultaneously pins refusal-under-`--quiet` and
  no-record-on-refusal; `--help` still registering both flags with the word
  `retired` (the **only** lock on the retention shape — without it Phase 7
  could legally delete the flags and every other retirement test would still
  pass on argparse's own exit 2); and the three D1 shapes never prompting.
- **Preview / D6 (6):** the unfiltered preview naming all six candidates; the
  filtered preview still naming the five spine docs (E1, on the committed
  fixture per Q13); an ineligible archived candidate named; the primary-only
  preview naming none (Q7); `--cascade-only … --dry-run` ≡
  `--cascade-dry-run --cascade-only …`; and the Q2 exit-0 non-matching
  preview.
- **Scoped write (8 functions, 12 items):** E2 dedup with no false failure;
  E3 collision refusing before any write; E4 archived neighbour excluded
  byte-for-byte; the archived **primary** refused in all three D1 shapes
  (Q1); E5 none-matched; the distinct no-candidates message; the empty and
  comment-only scope refusals (Q9); the dotted-edge `docs check` guard; and
  `--reason` on the primary only (Q10).
- **The Q4 exit-code split at the CLI (3):** malformed member → 1, occupied
  destination → 1, unwritable member → 2.
- **`--json` / D7 (7 functions, 9 items):** preview shape, preview/apply key
  identity, per-candidate `selected` + `reason`, exactly-one-object stdout,
  no record on three different refusals (Q3), the no-scope candidate list
  (Q14), and `index_refreshed`.

**`tests/test_skill.py`** (+2) — the archive row of `SKILL.md` and of
`references/use-cases.md` must teach `--cascade-dry-run` / `--cascade-only`
and must not prescribe bare `--cascade`. The "not bare" half is a
`--cascade(?![-\w])` regex, so `--cascade-only` cannot satisfy it by
accident. RED until Phase 7.

**`tests/test_cli_check.py`** (+1) — a scoped archive of the neighborhood
fixture's milestone pair leaves `docs check` at exit 0 and the five spine docs
in the active tree: the M12/M18 no-regression proof restated for the
invocation that replaces bare `--cascade`.

### Decisions / issues

- **Two Phase-1 gaps were found by writing the tests, and closed in the specs
  in this phase** (recorded in the milestone's *Decisions (Phase 1 —
  BINDING)*, in `cli.md`, and mirrored into the bundled refs):
  1. **Ineligibility reason precedence.** `../ghost.md` is *both*
     `outside-root` and `unresolved-target`; `archive/…/ghost.md` is both
     `already-archived` and `unresolved-target`. Phase 1 named the four tokens
     but left the overlap undetermined, so
     `test_ineligibility_reason_precedence_is_pinned` had no answer to assert.
     Fixed order: **`outside-root`, then `already-archived`, then
     `unresolved-target`** — the more structural fact wins.
  2. **Check order.** Q11 fixed only the retirement check's position. The
     malformed-candidate case exposed the rest: today's whole-tree validation
     walk raises on the same file the M26 plan pre-flight would name, so
     without an order the exit-1 message is undetermined. Pinned as a
     nine-step list, with the **plan pre-flight before the whole-tree walk** —
     both can fire on one malformed file, and naming the document the operator
     asked for is strictly more actionable than naming an unrelated referring
     doc.
- **`primary.source` wording corrected** from "the `FILE` argument exactly as
  typed" to "as given on the command line": `plan_archive` receives a `Path`,
  so `Path("./a.md")` serialises as `a.md`. The looser wording is the one the
  code can actually honour.
- **`test_archive_never_prompts_on_stdin` is GREEN-degenerate today** — none
  of the three D1 shapes reads stdin at baseline either. It is kept because it
  becomes the load-bearing lock the moment Phase 7 deletes `_cascade_archive`,
  the verb's last stdin reader.
- **The four migrated cascade tests are the deliberate GREEN half.** They are
  the M12 referring-edge and M18 archive-subtree-edge no-regression proof;
  migrating them to `--cascade-only` (rather than deleting them) is what keeps
  that proof alive across the D2 retirement.
- **`tests/test_check.py` needs no edit**, but Phase 3's four new trees
  automatically add four parametrizations to
  `test_check_tree_legacy_fixtures_gain_no_new_findings`, whose list is
  derived from `_TREES.iterdir()`. Those must pass — which constrains the
  fixtures: no recognized reciprocal verb unless the pair is complete.
- **No `src/docs_cli/cli.py` change.** `git diff --stat` against the Phase-1
  commit is empty.

### Verification

- `.venv/bin/python -m pytest tests/ -q --co` — **863 collected, zero
  collection errors** (777 → 863: −3 deleted/replaced ids, +89 new).
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — all files formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 47 source files.
- `.venv/bin/docs check --root docs` — no violations (exit 0).
- `cmp docs/{cli,convention}.md src/docs_cli/skill/references/` — identical.
- The full RED census is Phase 4's; at the end of Phase 2 the fixture-backed
  tests still fail on a missing `tests/fixtures/trees/archive-*` directory,
  which Phase 3 supplies.

## Milestone completion summary

_Not complete._
