# M30 — Lifecycle verb and free-form `docs relate` — Test Matrix

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-10-27

Related:
- pairs-with: lifecycle-and-free-form-relate.md
- pairs-with: lifecycle-and-free-form-relate-impl.md

## Risk level

Standard

Reason: proposed at setup and **confirmed by the operator** on 2026-10-27
(setup question Q8 in [the task plan](lifecycle-and-free-form-relate.md)). An
additive change to the published CLI: one new verb, one widened verb, and
`parse()` made to honour the tree's config (D10), with no `docs check` rule
change and no tree that `docs check` passes today changing outcome. Every write reuses a proven
editor, and the integrity-sensitive invariants — no transition into or out of
`archived`, recognized-verb `relate` unchanged, the archive candidate set
unchanged — are each pinned by a named lock below. D10 reaches the core read
path, but only widens what parses on a check-clean tree; the one changed
outcome is a tree that already fails `docs check` (E11). No Phase-4 operator
checkpoint.

## Check classification

Product tests belong in default test discovery (`.venv/bin/python -m pytest
-q`). Non-product checks run only when selected as explicit workflow gates;
this milestone adds none — `docs check` from the docs root and the existing
live-INDEX snapshot test remain the documentation gates.

## Contract clauses

Clause ids are local to this matrix; each cites the task plan's binding
decision (D1–D10) it traces to. Every setup question is resolved, so no
clause is pending; Phase 1 freezes the exact messages and records.

| Id | Clause | Source |
|---|---|---|
| C1 | `docs lifecycle <file>... <state>`: the last token is the state; a single token refuses (exit 2); the batch is validate-all-first | D1 |
| C2 | The target state must be in the tree's lifecycle vocabulary minus `archived`; `archived` refuses with a pointer to `docs archive`; any other unknown state refuses naming the allowed states | D2 |
| C3 | A named document under the archive subtree refuses the whole batch (exit 2), nothing written | D2 |
| C4 | Extension states (`add_lifecycles`) are valid `docs lifecycle` targets and round-trip through every walking verb (Q7 → A) | D2, D10, A1 |
| C5 | Only a document whose `Lifecycle:` changes is written and gets its `Updated:` bumped; an all-current batch writes zero bytes and does not reindex; a write reindexes exactly once | D3 |
| C6 | A free-form `relate add` / `relate remove` writes SOURCE's bullet only; TARGET is never written; canonical-target matching; group created/dropped; idempotent | D4 |
| C7 | Recognized-verb `relate` is byte-for-byte unchanged — messages, exits, two-record `--json`, `Revision:`, coordinated-write contract | D4 |
| C8 | A free-form SOURCE under the archive subtree refuses (exit 2) for `add` and `remove`, even when nothing would change | D5 |
| C9 | A free-form TARGET under the archive subtree is allowed, never written, needs no `--reason`, and no `Revision:` is written | D5 |
| C10 | A free-form TARGET may be any existing file under the root, Markdown or not; missing / directory / outside-root keep exit 1 | D5 |
| C11 | A verb containing `:` or a newline, an empty verb, or a padded verb refuses (exit 2) with zero bytes written | D6 |
| C12 | A free-form verb must match `[a-z][a-z0-9-]*` in full (Q3 → c); case variants of recognized verbs and every other out-of-grammar verb refuse at exit 2 with zero bytes written; widening later is additive | D6, A2 |
| C13 | Edges written by `relate` produce byte-identical files, an identical `--cascade-dry-run --json` candidate set, and the same leg-1 strand refusal as hand-written edges | D7 |
| C14 | A `docs new --body-from` body opening with a `Related:` group yields those edges as metadata | D8 |
| C15 | `--json` records: `docs lifecycle`'s key set is closed; the free-form `relate` record's key set is closed (one edit, no inverse); preview and apply share one shape | D3, D4 |
| C16 | The Agent Playbook Suite CI probes pass: `lifecycle` in the `docs --help` brace list; `docs relate add a.md pairs-with b.md --dry-run` exits 0 in a fresh two-document tree | D1, D9 |
| C17 | Surface parity: argparse help, `cli.md`, `convention.md`, byte-identical skill references, the skill body and *Three things never to hand-edit*, the README verb list, the CHANGELOG | D9 |
| C18 | Version 2.1.0 in `pyproject.toml` and the packaging pin; `## 2.1.0 — UNRELEASED` CHANGELOG section | D9 |
| C19 | The primary use case completes on a throwaway tree with zero hand-edits and zero prompts, ending `docs check` clean | Goal |
| C20 | `parse()` validates `Lifecycle:` / `Role:` against the tree's configured vocabulary at every call site (seven existing, plus the new verbs'), so extension lifecycles and roles work in every verb | D10 |
| C21 | `parse()` reads `Updated:` in the tree's `[archive] date_format` at every call site — one spelling, never two — so a non-default format works in every verb | D10 |
| C22 | A bare `parse(text, path, root)` keeps the built-in defaults; no tree that `docs check` passes today fails any verb after the upgrade; the one changed outcome (E11) reports the same `bad-date` diagnosis `docs check` gives | D10 |

## Matrix

Visible test names are **planned** at setup; Phase 2 writes them, and this
table is updated with the final ids.

| Contract clause | Visible test | Hidden/generalization check | Property/stateful check | Mutation target | Fuzz/benchmark/security/schema note |
|---|---|---|---|---|---|
| Success path — lifecycle (C1, C5) | `test_cli_lifecycle.py::test_lifecycle_promotes_a_draft_to_active_and_bumps_updated`; `::test_lifecycle_accepts_several_files_then_one_state_and_reindexes_once` | nested subdirectory docs; non-canonical path spellings; duplicate paths in one batch | applying twice equals applying once, byte for byte | the `if changed` guard; the reindex-once guard | `--json` key set closed (C15) |
| Success path — free-form relate (C6) | `test_cli_relate.py::test_relate_free_form_add_writes_only_the_source_bullet`; `::test_relate_free_form_remove_drops_only_the_source_bullet` | non-canonical target spellings; a SOURCE with no `Related:` group | add then remove restores the bytes except `Updated:`; exactly one file changes | the recognized-versus-free-form branch | free-form `--json` key set closed (C15) |
| Error path — archive boundary (C2, C3, C8) | `test_cli_lifecycle.py::test_lifecycle_refuses_archived_as_a_target_state`; `::test_lifecycle_refuses_a_document_under_the_archive_subtree`; `test_cli_relate.py::test_relate_free_form_refuses_an_archived_source_even_when_nothing_would_change` | `[archive] dir = "attic"`; an archived document named alongside valid ones | no allowed transition ever yields `status-drift` | the `archived` target guard; the archive-subtree source guard | — |
| Error path — grammar and resolution (C1, C2, C10, C11) | `test_cli_lifecycle.py::test_lifecycle_single_token_is_refused_as_ambiguous`; `::test_lifecycle_unknown_state_names_the_allowed_states`; `::test_lifecycle_missing_or_outside_root_file_exits_1_unchanged`; `test_cli_relate.py::test_relate_verb_that_would_corrupt_the_block_is_refused` | grammar-boundary verbs | every refusal leaves the tree byte-identical | the grammar's anchors | security: `:` / newline injection refused |
| Boundary — free-form verb grammar (C12) | `test_cli_relate.py::test_relate_free_form_verb_grammar_boundary`; `::test_relate_case_variant_verb_refuses` (existing id; keeps refusing, message per Phase 1) | exotic verbs at the boundary; `Pairs-With`, `see-Also`, `pairs_with`, `9to5`, `-x` | — | the grammar's anchors | fuzz: every generated string refuses or round-trips through `parse()` unchanged |
| Boundary — endpoints (C9, C10) | `test_cli_relate.py::test_relate_free_form_archived_target_needs_no_reason_and_is_untouched`; `::test_relate_free_form_accepts_a_non_markdown_target` | excluded targets; non-Markdown targets of several types | the archived TARGET is byte-identical after the run | the archived-endpoint `--reason` rule's branch | — |
| Boundary — extension states (C4, C20) | `test_cli_lifecycle.py::test_lifecycle_writes_an_extension_state_and_the_tree_reindexes`; walking-verb locks — `test_cli_index.py::test_index_reads_a_doc_in_an_extension_lifecycle_and_role`, `test_cli_list.py::test_list_includes_a_doc_in_an_extension_lifecycle`, `test_cli_touch.py::test_touch_reindexes_a_tree_with_extension_vocabulary`, `test_cli_relate.py::test_relate_accepts_an_endpoint_in_an_extension_lifecycle`, plus `archive`, `mv`, `project set` and `stamp` | extension vocabularies of several sizes | the post-state tree reindexes and `docs check` stays clean | the vocabulary passed to `parse()` | — |
| Boundary — date format (C21, C22) | `test_cli_index.py::test_index_reads_a_non_default_date_format_tree`; `test_cli_touch.py::test_touch_reindexes_a_non_default_date_format_tree`; `test_cli_archive.py::test_archive_renders_the_witness_in_the_trees_date_format` (existing id, rewritten as its docstring foresees: exit 0); `::test_walking_verbs_report_bad_date_on_a_mis_spelled_non_default_tree`; `test_model.py::test_bare_parse_keeps_the_built_in_defaults` | `[archive] dir = "attic"` with `%d-%m-%Y`; other formats | every pre-existing fixture tree and this repository's tree reindex byte-identically | the `date_format` passed to `parse()` | — |
| Idempotency/retry/state (C5, C6) | `test_cli_lifecycle.py::test_lifecycle_already_in_state_writes_zero_bytes_and_skips_reindex`; `test_cli_relate.py::test_relate_free_form_is_idempotent` | — | idempotence over every top-level state | the `if changed` guard | — |
| Regression — recognized verbs (C7) | every pre-existing `test_cli_relate.py` / `test_relate_plan.py` id except the E10 refusals, unedited; `test_cli_relate.py::test_relate_recognized_pair_is_byte_identical_to_2_0` | — | a recognized operation changes at most two files | the recognized-versus-free-form branch | recognized `--json` record asserted unchanged |
| Regression — archive invariance (C13) | `test_cli_archive.py::test_cascade_candidates_match_when_edges_were_written_by_relate`; `::test_strand_refusal_fires_on_a_child_of_written_by_relate` | a real milestone trio from this tree (Phase 9) | — | — | — |
| Regression — `--body-from` route (C14) | `test_body_from.py::test_body_opening_with_a_related_group_becomes_metadata` | a non-Markdown sidecar target | — | — | — |
| External consumer (C16) | `test_cli_lifecycle.py::test_help_verb_list_names_lifecycle_for_the_playbook_guard`; `test_cli_relate.py::test_playbook_guard_free_form_dry_run_probe_exits_0` | the same probes against a locally built wheel (Phase 9) | — | — | — |
| Surface parity (C17, C18) | `test_skill.py::test_every_named_verb_is_a_real_subcommand` (existing); `::test_skill_routes_lifecycle_and_free_form_edges_through_verbs`; `test_skill_refs.py` (existing byte identity); `test_packaging.py` version pin at 2.1.0 | — | — | — | — |
| Acceptance — primary use case (C19) | `test_cli_lifecycle.py::test_milestone_setup_needs_no_hand_edit` | the same flow on this repository's own tree copy (Phase 9) | no file changes outside a verb invocation | — | runtime recorded in Phase 9 |
| Security/privacy/perf | covered above: block-corruption refusals (C11), TARGET containment (C10) | — | — | — | benchmark: not applicable; runtime recorded, not budgeted |

## Visible tests

Planned modules (Phase 2 finalizes names; names state scenario and outcome,
with no milestone or decision identifiers):

- `tests/test_cli_lifecycle.py` — **new**: C1–C5, C15, C16 (help probe), C19.
- `tests/test_cli_relate.py` — C6–C12, C15, C16 (relate probe). Three
  existing ids pin today's free-form refusal (`test_relate_unknown_verb_refuses`,
  `test_relate_quiet_suppresses_success_but_never_a_refusal`,
  `test_relate_case_variant_verb_refuses`); the first two become named
  behaviour-change edits, the third keeps refusing under the grammar.
- `tests/test_relate_plan.py` — the one-sided plan: one edit, no inverse,
  nothing staged for TARGET.
- `tests/test_cli_archive.py` — C13; and C21 through the existing
  `test_archive_renders_the_witness_in_the_trees_date_format`, which pins
  today's date-format defect on purpose and is rewritten as its docstring
  foresees — the fourth named behaviour-change edit.
- `tests/test_body_from.py` — C14.
- `tests/test_skill.py`, `tests/test_skill_refs.py` — C17.
- `tests/test_packaging.py` — C18.
- For D10 (C20–C22): `tests/test_cli_index.py`, `tests/test_cli_list.py`,
  `tests/test_cli_touch.py`, `tests/test_walker.py`, `tests/test_model.py`,
  `tests/test_cli_project_set.py`, `tests/test_cli_stamp.py`.

## Hidden/generalization categories

The repository is fully visible to the implementer, so no private cases exist
and none are recorded here. Generalization targets, exercised through
property checks and the Phase-9 dogfood rather than enumerated fixtures:

- extension lifecycle and role vocabularies;
- non-default `[archive] date_format` and `[archive] dir`;
- documents in nested subdirectories;
- non-canonical target spellings (`./b.md`, `sub/../b.md`);
- non-Markdown and excluded targets;
- duplicate paths inside one `docs lifecycle` batch;
- verbs at the grammar boundary;
- a real milestone trio in this repository's own tree.

## Property/stateful checks

- Idempotence: the same `docs lifecycle` or `relate` invocation applied twice
  equals one application, byte for byte.
- Round trip: free-form `relate add` then `remove` restores the original bytes
  except `Updated:`.
- Lifecycle safety: for every active-tree document and every allowed state,
  the post-state tree has no `status-drift` finding.
- Write footprint: a free-form operation changes exactly one file; a
  recognized one at most two; a lifecycle batch exactly the documents whose
  state differed.

## Mutation targets

Mutation testing is not configured in this project. Phase 8 runs a
hand-applied mutation smoke over these seven points (the M28a precedent) and
records which test kills each:

1. the `archived` target guard;
2. the archive-subtree source guard (`docs lifecycle` and free-form SOURCE);
3. the recognized-versus-free-form branch (`inverse_verb(verb) is None`);
4. the `if changed` idempotence guard;
5. the reindex-once guard;
6. the verb grammar's anchors;
7. the config passed to `parse()` (vocabulary and `date_format`).

## Fuzz

A fixed-seed, stdlib-only generator over printable strings feeds the
free-form verb validator: every input either refuses with zero bytes written
or is written and read back by `parse()` as the identical verb.

## Benchmark/security/schema

- Schema: `docs lifecycle --json` and free-form `relate --json` key sets
  asserted closed; the recognized-verb `relate --json` record asserted
  unchanged.
- Security: metadata-injection refusals (`:` and newline in a verb); TARGET
  containment under the root unchanged.
- Benchmark: not applicable — no performance budget; Phase 9 records the
  added runtime over this tree.

## Use-case mapping

Tests map to the use-case catalog shipped in the bundled skill
(`src/docs_cli/skill/references/use-cases.md`; this project keeps no separate
`use-cases.md` in the docs tree — `charter.md` › *Use cases*).

| Use case | Covered by |
|---|---|
| Greenfield — promote a scaffolded doc's lifecycle (new row, Phase 7) | C1–C5, C19 |
| Greenfield — extend the vocabulary or the date format in `.docs.toml` (existing template guidance) | C4, C20–C22 |
| Greenfield — link related docs with a free-form edge (new row, Phase 7) | C6, C9, C10, C12, C19 |
| Upgrade — repair a one-sided recognized pair (existing M25 rows) | C7 |
| Adoption — sidecar a non-Markdown artifact (`--body-from` with `Related:`) | C10, C14 |
| Greenfield — archive a completed doc, and close out a milestone with `--cascade-only` (existing rows) | C3, C13 |
| Agent Playbook Suite — `create-milestones` setup without operator asks | C16, C19 |

## Mock policy

- New mocks: none planned.
- Justification: not applicable. If Phase 1 adopts staged publish with rollback
  for a multi-file `docs lifecycle`, write-failure injection reuses the existing
  `atomic_write` monkeypatch pattern from the relate suite and is recorded
  here.
- Real-path test covering same behavior: every success and refusal path is a
  subprocess test over a real tree.

## Hidden-test handling

- Actual hidden cases are not written here; the implementation agent can read
  this repository.
- Categories: listed under *Hidden/generalization categories*.
- Owner: the milestone conductor.
- Commands or CI job names: none configured; generalization runs inside the
  default suite (property checks, fuzz) and the Phase-9 dogfood.

## Gate commands

### Fast PR gate

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q
(cd docs && ../.venv/bin/docs check .)
```

### Deep/nightly/release gate

```sh
not configured - no hidden suite, coverage tool or mutation tool in this
project; the Standard-risk property, fuzz and hand-applied mutation checks run
inside the fast gate and Phase 8, and the Phase-9 dogfood replays both
Agent Playbook Suite probes against a locally built wheel
```

## Results summary

- Visible tests: pending (setup baseline 1504 passed).
- Hidden/generalization: pending — categories only.
- Property/stateful: pending.
- Mutation: pending — hand-applied smoke, seven targets.
- Fuzz: pending.
- Benchmark/security/schema: pending; benchmark not applicable.
- Coverage: not configured.
- Mock audit: no mocks planned.
- Open risks: none outstanding at setup — Q3, Q7 and Q8 answered by the
  operator on 2026-10-27.

## Adequacy results

- visible_pass_rate: pending
- hidden_pass_rate: not applicable (no hidden suite)
- hidden_generalization_gap: not applicable
- changed-lines coverage: not configured
- changed-files branch coverage: not configured
- mutation score on touched modules: pending (hand-applied smoke)
- property/stateful result: pending
- fuzz result: pending
- benchmark delta: not applicable; runtime recorded in Phase 9
- security/schema/migration result: pending
- skipped deep gates and follow-up: none skipped; coverage and mutation tooling
  are not configured in this project
