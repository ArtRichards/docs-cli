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
(setup question Q8 in [the task plan](lifecycle-and-free-form-relate.md)),
and unchanged by the Step 0 review. An additive change to the published CLI:
one new verb, one widened verb, and `parse()` made to honour the tree's config
(D10), with no `docs check` rule change and no tree that `docs check` passes
today failing any verb. Every write reuses a proven editor, and the
integrity-sensitive invariants — no transition into or out of `archived`,
recognized-verb `relate` unchanged, the archive candidate set unchanged, no
document destroyed by `docs stamp` — are each pinned by a named lock below.
D10 reaches the core read path; its three changed outcomes are a tree that
already fails `docs check` (E11), `docs stamp`'s refusal of a block that fails
the configured vocabulary or format instead of a destructive re-stamp (E12),
and extension-role documents appearing in the INDEX (E13). No Phase-4
operator checkpoint.

## Check classification

Product tests belong in default test discovery (`.venv/bin/python -m pytest
-q`) — including the reference byte-identity and stale-wording checks, because
the bundled skill and the `--help` text ship. Non-product checks run only when
selected as explicit workflow gates, never in default discovery:

- `docs check .` from the docs root;
- the live-INDEX snapshot: `cmp docs/INDEX.md tests/fixtures/expected/docs-INDEX.md`;
- the Phase 4 / Phase 8 mechanical proof — test ids collected in a throwaway
  `git worktree` at the pre-Phase-1 commit `e48adb9` and at HEAD, compared
  with `comm`, plus an AST function-body diff of every pre-existing
  `tests/*.py` function (only the authoritative list's tests, `_attic_tree`
  and the stamp fixture's prose may differ); scratchpad scripts, results in
  the implementation log;
- a naming lint over the new test names (no `m30`, decision, clause, phase,
  step or review identifiers);
- the Phase 8 hand-applied mutation smoke.

## Contract clauses

Clause ids are local to this matrix; each cites the task plan's binding
decision (D1–D10) it traces to. Every setup question is resolved, so no
clause is pending. Phase 1 froze the exact messages and records in the task
plan's *Decisions (Phase 1 — BINDING)*: the ids `L1`–`L12` (the
`docs lifecycle` catalogue, P1.1) and `R1`–`R3` (free-form `relate`, P1.2)
below refer to it.

| Id | Clause | Source |
|---|---|---|
| C1 | `docs lifecycle <file>... <state>`: the last token is the state; a single token refuses (exit 2, L1); a relative path resolves against the root (OQ-1); outside-root, missing and unparseable documents exit 1 (L8–L10); the strict-root refusals (L2–L4); the batch is validate-all-first | D1 |
| C2 | The target state must be in the tree's lifecycle vocabulary minus `archived`, matched case-sensitively; `archived` refuses with a pointer to `docs archive` (L5); any other unknown state — `Archived` included — refuses naming the allowed states (L6) | D2 |
| C3 | A named document under the archive subtree refuses the whole batch (exit 2, L7) before any per-document check, whatever its position, nothing written | D2 |
| C4 | Extension states (`add_lifecycles`) are valid `docs lifecycle` targets and round-trip through every walking verb (Q7 → A) | D2, D10, A1 |
| C5 | Only a document whose `Lifecycle:` changes is rewritten and gets its `Updated:` bumped; an all-current batch or a `--dry-run` writes nothing at all, INDEX included; a real change is followed by one INDEX refresh (honouring exclusions); a path named twice is planned, listed and written once (OQ-3); the frozen success lines; an INDEX-refresh failure exits 2 with the documents written (L12) | D3 |
| C6 | A free-form `relate add` / `relate remove` rewrites SOURCE's bullet only; TARGET is never written; canonical-target matching; group created/dropped; idempotent; one INDEX refresh after a real change | D4 |
| C7 | Recognized-verb `relate` is byte-for-byte unchanged on every tree 2.0.0 could read — messages, exits, two-record `--json`, `Revision:`, coordinated-write contract; on an extension-vocabulary or non-default-date tree an endpoint 2.0.0 refused at exit 1 now resolves (D10) | D4, D10 |
| C8 | A free-form SOURCE under the archive subtree refuses (exit 2, R2) for `add` and `remove`, even when nothing would change | D5 |
| C9 | A free-form TARGET under the archive subtree is allowed, never written, needs no `--reason`, and no `Revision:` is written | D5 |
| C10 | A free-form TARGET may be any existing file under the root, Markdown or not — `broken-ref`'s existence test plus containment; missing / directory / outside-root (including through an escaping symlink) keep exit 1 | D5 |
| C11 | A verb containing `:` or a newline, an empty verb, or a padded verb refuses (exit 2, R1) with zero bytes written; a leading-hyphen verb is consumed by argparse — exit 2, usage error, nothing written — and after `--` reaches R1 (R3) | D6 |
| C12 | A free-form verb must match `[a-z][a-z0-9-]*` in full (Q3 → c; ASCII only, `fullmatch`); case variants of recognized verbs and every other out-of-grammar verb refuse at exit 2 with the R1 message and zero bytes written; widening later is additive | D6, A2 |
| C13 | For edges written by `relate`: each written bullet line and the parsed `Related:` list match the hand-written edges; the `--cascade-dry-run --json` candidate records are identical; leg 1's strand refusal fires identically; full-file byte identity only for the `archive-neighborhood` copy, `relate` run under `--date` equal to the fixture's `Updated:` | D7 |
| C14 | A `docs new --body-from` body opening with a `Related:` group (label alone on its line, then bullets) yields those edges as metadata; the skill's literal sidecar example, as rewritten in Phase 7, does too; the inline `Related: x: y` form stays body text | D8 |
| C15 | `--json` records: `docs lifecycle`'s key set is closed (P1.1: `state`, `date`, `dry_run`, `applied`, `index_refreshed`, `edits[path, before, change]`); the free-form `relate` record is the recognized record's eleven keys with `inverse: null` and one edit (P1.2); preview and apply share one shape | D3, D4 |
| C16 | The Agent Playbook Suite CI probes pass: `lifecycle` in the `docs --help` brace list; `docs relate add a.md pairs-with b.md --dry-run` exits 0 in a fresh two-document tree | D1, D9 |
| C17 | Surface parity: argparse help, `cli.md`, `convention.md`, byte-identical skill references, the skill body and *Three things never to hand-edit*, the two skill sidecar examples, the README verb list, the CHANGELOG | D9 |
| C18 | Version 2.1.0 in `pyproject.toml` and the packaging pins; `## 2.1.0 — UNRELEASED` CHANGELOG section | D9 |
| C19 | The primary use case completes on a throwaway tree with zero hand-edits and zero prompts, ending `docs check` clean | Goal |
| C20 | `parse()` validates `Lifecycle:` / `Role:` against the tree's configured vocabulary at every call site (seven existing, plus the new verbs'), so extension lifecycles and roles work in every verb — `index`, `touch`, `list`, `relate`, `lifecycle`, `archive`, `mv`, `project set`, `project rename`, `stamp` | D10 |
| C21 | `parse()` reads `Updated:` in the tree's `[archive] date_format` at every call site — one spelling, never two — so a non-default format works in every verb | D10 |
| C22 | A bare `parse(text, path, root)` keeps the built-in defaults; no tree that `docs check` passes today fails any verb after the upgrade; D10's three changed outcomes are exactly E11 (walking verbs report the `bad-date` diagnosis `docs check` gives), E12 (C24) and E13 (C25) | D10 |
| C23 | `docs lifecycle` refuses (exit 2, zero bytes, whole batch, L11) a source outside the archive subtree whose current `Lifecycle:` is `archived`, naming the `status-drift` and `docs archive` | D2 |
| C24 | `docs stamp` on a file whose full metadata block fails the tree's configured vocabulary or date format refuses with zero bytes written, exit 1, naming the failing field and pointing at `docs check` / `docs touch` (the P1.5 message) — on a default tree too (an invalid `Role:` or a typo'd lifecycle); a block in a configured extension state is "already stamped" (`Updated:` refresh only); a full block failing `parse()` for a reason unrelated to the configured vocabulary or date format (e.g. a malformed `Related:` bullet) keeps today's stamping | D10 |
| C25 | `render_index` renders every active document its summary counts: extension-role groups after the built-in role order, sorted alphabetically, each under `### Active — <Role>`; no new `Config` field | D10 |

## Decision ↔ clause crosswalk

| Decision (task plan) | Matrix clauses |
|---|---|
| D1 — `docs lifecycle` grammar | C1, C16 |
| D2 — top-level states; the archive boundary | C2, C3, C4, C23 |
| D3 — idempotence, validate-all-first, one reindex | C5, C15 |
| D4 — one-sided free-form `relate`; recognized verbs unchanged | C6, C7, C15 |
| D5 — free-form endpoints | C8, C9, C10 |
| D6 — the free-form verb grammar | C11, C12 |
| D7 — archive-candidate and strand invariance | C13 |
| D8 — the `--body-from` route | C14 |
| D9 — compatibility, 2.1.0, parity, external consumer | C16, C17, C18 |
| D10 — `parse()` honours the tree's config; `render_index`; `docs stamp` | C4, C7, C20, C21, C22, C24, C25 |
| Goal — the primary use case | C19 |

## Matrix

Visible test names were planned at setup and aligned with the frozen
catalogue in Phase 1; Phase 2 writes them, and this table is updated with
the final ids. Pre-existing tests that change are
listed only in the task plan's *Test Strategy* › *Pre-existing tests that
change*.

| Contract clause | Visible test | Hidden/generalization check | Property/stateful check | Mutation target | Fuzz/benchmark/security/schema note |
|---|---|---|---|---|---|
| Success path — lifecycle (C1, C5) | `test_cli_lifecycle.py::test_lifecycle_promotes_a_draft_to_active_and_bumps_updated`; `::test_lifecycle_accepts_several_files_then_one_state_and_reindexes_once` | nested subdirectory docs; non-canonical path spellings; duplicate paths in one batch | applying twice equals applying once, byte for byte; the batch rewrites exactly the documents whose state differed, then one INDEX refresh | the `if changed` guard | `--json` key set closed (C15) |
| Success path — free-form relate (C6) | `test_cli_relate.py::test_relate_free_form_add_writes_only_the_source_bullet`; `::test_relate_free_form_remove_drops_only_the_source_bullet` | non-canonical target spellings; a SOURCE with no `Related:` group | add then remove of an initially absent edge restores the bytes except `Updated:`; one managed document rewritten plus one INDEX refresh | the recognized-versus-free-form branch | free-form `--json` key set closed (C15) |
| Error path — archive boundary (C2, C3, C8, C23) | `test_cli_lifecycle.py::test_lifecycle_refuses_archived_as_a_target_state`; `::test_lifecycle_refuses_a_document_under_the_archive_subtree`; `::test_lifecycle_refuses_an_active_tree_document_already_marked_archived`; `::test_lifecycle_batch_with_one_archived_document_writes_nothing`; `test_cli_relate.py::test_relate_free_form_refuses_an_archived_source_even_when_nothing_would_change` | `[archive] dir = "attic"` | no allowed transition ever yields `status-drift` | the `archived` target guard; the archive-subtree source guard; the current-`archived` source guard | — |
| Error path — grammar, resolution, root (C1, C2, C10, C11) | `test_cli_lifecycle.py::test_lifecycle_single_token_is_refused_as_ambiguous`; `::test_lifecycle_unknown_state_names_the_allowed_states`; `::test_lifecycle_missing_or_outside_root_file_exits_1_unchanged`; `::test_lifecycle_refuses_outside_a_docs_root`; `test_cli_relate.py::test_relate_verb_that_would_corrupt_the_block_is_refused`; `::test_relate_free_form_target_outside_the_root_exits_1`; `::test_relate_free_form_target_that_is_a_directory_exits_1`; `::test_relate_free_form_missing_target_exits_1`; `::test_relate_free_form_target_symlink_escaping_the_root_exits_1` | grammar-boundary verbs | every refusal leaves the tree byte-identical, INDEX included | the grammar's anchors | security: `:` / newline injection refused; TARGET containment |
| Error path — post-write tail (C5) | `test_cli_lifecycle.py::test_lifecycle_index_refresh_failure_exits_2_with_documents_written` | — | the documents carry the new state; the record reports `index_refreshed: false` | — | — |
| Boundary — free-form verb grammar (C12) | `test_cli_relate.py::test_relate_free_form_verb_grammar_boundary`; `::test_relate_case_variant_verb_refuses` (pre-existing; see the task plan's list) | `Pairs-With`, `see-Also`, `pairs_with`, `9to5`, `-x`, `a-`, `a--b` | valid generated verbs succeed and round-trip; invalid ones refuse with zero writes | `re.fullmatch` vs `re.match` + `$`; `[0-9]` vs `\d` | fuzz: valid and invalid categories generated independently (see *Fuzz*) |
| Boundary — endpoints (C9, C10) | `test_cli_relate.py::test_relate_free_form_archived_target_needs_no_reason_and_is_untouched`; `::test_relate_free_form_accepts_a_non_markdown_target` | excluded targets; non-Markdown targets of several types | the archived TARGET is byte-identical after the run | the archived-endpoint `--reason` rule's branch | — |
| Boundary — extension vocabulary (C4, C20, C25) | `test_cli_lifecycle.py::test_lifecycle_writes_an_extension_state_and_the_tree_reindexes`; `test_cli_index.py::test_index_renders_an_extension_role_group_after_the_built_in_roles` (asserts the entry is rendered under `### Active — Adr`, after every built-in group, extension groups alphabetical, summary count equal to rendered entries); `test_index.py::test_render_index_orders_extension_roles_alphabetically_after_built_ins`; `test_cli_list.py::test_list_includes_a_doc_in_an_extension_lifecycle`; `test_cli_touch.py::test_touch_reindexes_a_tree_with_extension_vocabulary`; `test_cli_relate.py::test_relate_accepts_an_endpoint_in_an_extension_lifecycle`; plus `archive`, `mv`, `project set`, `project rename` and `stamp` locks | extension vocabularies of several sizes | the post-state tree reindexes and `docs check` stays clean | the vocabulary passed to `parse()`; `render_index`'s extension-role placement | — |
| Boundary — date format (C21, C22) | `test_cli_index.py::test_index_reads_a_non_default_date_format_tree`; `test_cli_touch.py::test_touch_reindexes_a_non_default_date_format_tree`; `test_cli_archive.py::test_walking_verbs_report_bad_date_on_a_mis_spelled_non_default_tree`; `test_model.py::test_bare_parse_keeps_the_built_in_defaults`; the corrected `test_cli_archive.py` / `test_cli_mv.py` tests in the task plan's list | `[archive] dir = "attic"` with `%d-%m-%Y`; other formats | every pre-existing fixture tree and this repository's tree reindex byte-identically | the `date_format` passed to `parse()` | — |
| Boundary — `docs stamp` (C24) | `test_cli_stamp.py::test_stamp_keeps_a_document_in_a_configured_extension_state`; `::test_stamp_refuses_a_block_outside_the_configured_vocabulary_with_zero_bytes` (extension tree); `::test_stamp_refuses_a_full_block_with_an_invalid_role_with_zero_bytes` (default tree; pre-existing, renamed — see the task plan's list); `::test_stamp_refuses_a_typod_lifecycle_on_a_default_tree_with_zero_bytes`; `::test_stamp_refuses_a_block_dated_outside_the_trees_date_format_with_zero_bytes`; `::test_stamp_keeps_todays_behaviour_for_a_block_failing_for_an_unrelated_reason` | — | the refused file and the INDEX are byte-identical | `docs stamp`'s block classification | — |
| Idempotency/retry/state (C5, C6) | `test_cli_lifecycle.py::test_lifecycle_already_in_state_writes_zero_bytes_and_skips_reindex`; `test_cli_relate.py::test_relate_free_form_is_idempotent` | — | idempotence over every top-level state; a no-op leaves a sentinel INDEX byte-identical | the `if changed` guard; the no-reindex-on-a-no-op guard | — |
| Regression — recognized verbs (C7) | every pre-existing `test_cli_relate.py` / `test_relate_plan.py` id, unedited except as the task plan's list says; `test_cli_relate.py::test_relate_recognized_pair_still_writes_both_halves_unchanged` | — | a recognized operation rewrites at most two managed documents plus one INDEX refresh | the recognized-versus-free-form branch | recognized `--json` record asserted unchanged |
| Regression — archive invariance (C13) | `test_cli_archive.py::test_cascade_candidates_match_when_edges_were_written_by_relate`; `::test_strand_refusal_fires_on_a_child_of_written_by_relate` | a real milestone trio from this tree (Phase 9) | — | — | — |
| Regression — `--body-from` route (C14) | `test_body_from.py::test_body_opening_with_a_related_group_becomes_metadata`; `::test_skill_sidecar_example_yields_its_edge`; `::test_inline_related_line_stays_body_text` | a non-Markdown sidecar target | — | — | — |
| External consumer (C16) | `test_cli_lifecycle.py::test_help_verb_list_names_lifecycle_for_the_playbook_guard`; `test_cli_relate.py::test_playbook_guard_free_form_dry_run_probe_exits_0` | the same probes against a locally built wheel (Phase 9) | — | — | — |
| Surface parity (C17, C18) | `test_skill.py::test_every_named_verb_is_a_real_subcommand` (existing); `::test_skill_routes_lifecycle_and_free_form_edges_through_verbs`; `test_skill_refs.py` (existing byte identity); the 2.1.0 packaging pins in the task plan's list | — | — | — | — |
| Acceptance — primary use case (C19) | `test_cli_lifecycle.py::test_milestone_setup_needs_no_hand_edit` | the same flow on this repository's own tree copy (Phase 9) | no managed document changes outside a verb invocation | — | runtime recorded in Phase 9 |
| Security/privacy/perf | covered above: block-corruption refusals (C11), TARGET containment (C10) | — | — | — | benchmark: not applicable; runtime recorded, not budgeted |

## Visible tests

Planned modules (Phase 2 finalizes names; names state scenario and outcome,
with no milestone, decision or release identifiers). Every pre-existing test
the milestone edits is in the task plan's authoritative list, not here.

- `tests/test_cli_lifecycle.py` — **new**: C1–C5, C15, C16 (help probe), C19,
  C23, the strict-root refusal, and the INDEX-refresh-failure tail.
- `tests/test_cli_relate.py` — C6–C12, C15, C16 (relate probe), and TARGET
  containment (outside the root, a directory, missing, an escaping symlink).
- `tests/test_relate_plan.py` — the one-sided plan: one edit, no inverse,
  nothing staged for TARGET.
- `tests/test_cli_archive.py` — C13, and C21's walking-verb `bad-date` lock.
- `tests/test_body_from.py` — C14.
- `tests/test_cli_stamp.py` — C24, with byte-level zero-write locks for the
  extension-vocabulary tree and the E11 non-default-date shape.
- `tests/test_index.py`, `tests/test_cli_index.py` — C25.
- `tests/test_skill.py`, `tests/test_skill_refs.py` — C17.
- `tests/test_packaging.py` — C18.
- For D10 (C20–C22): `tests/test_cli_index.py`, `tests/test_cli_list.py`,
  `tests/test_cli_touch.py`, `tests/test_walker.py`, `tests/test_model.py`,
  `tests/test_cli_project_set.py`, `tests/test_cli_project_rename.py`,
  `tests/test_cli_stamp.py`, `tests/test_cli_mv.py`.

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
- Round trip: free-form `relate add` then `remove` of an edge that was
  initially **absent** restores the original bytes except `Updated:` —
  whether SOURCE started with no `Related:` group (created, then dropped) or a
  non-empty one. From an arbitrary initial state the assertion is the
  contractual one: the edge set afterwards is the initial set minus the edge,
  and every unrelated byte is preserved.
- Lifecycle safety: for every active-tree document and every allowed state,
  the post-state tree has no `status-drift` finding.
- Write footprint, counting editable documents separately from the generated
  INDEX: a no-op or `--dry-run` writes nothing at all, INDEX included; a real
  free-form operation rewrites exactly one managed document, a recognized one
  at most two, a lifecycle batch exactly the documents whose state differed —
  each followed by one INDEX refresh; a refused `docs stamp` writes nothing.

## Mutation targets

Mutation testing is not configured in this project. Phase 8 runs a
hand-applied mutation smoke over these points (the M28a precedent) and
records which test kills each:

1. the `archived` target guard;
2. the archive-subtree source guard (`docs lifecycle` and free-form SOURCE);
3. the current-`archived` source guard (`docs lifecycle`, C23);
4. the recognized-versus-free-form branch (`inverse_verb(verb) is None`);
5. the `if changed` idempotence guard;
6. no reindex on a no-op — observed through a sentinel INDEX that must stay
   byte-identical, with the refreshed INDEX asserted to reflect the final
   state (a call counter would need a justified entry under *Mock policy*);
7. the grammar's matcher: `re.fullmatch` versus `re.match` with `$`, which
   accepts a trailing newline;
8. the grammar's character class: `[0-9]` versus `\d`, which accepts
   non-ASCII digits;
9. the config passed to `parse()` (vocabulary and `date_format`);
10. `render_index`'s extension-role placement (C25);
11. `docs stamp`'s block classification — refuse versus re-stamp versus
    already stamped (C24).

## Fuzz

A fixed-seed, stdlib-only generator produces **valid and invalid verbs
independently** from D6's grammar. Valid inputs — including trailing and
doubled hyphens, digits after the first letter, and length extremes — must
succeed and be read back by `parse()` as the identical verb. Invalid inputs —
uppercase letters, a leading digit or hyphen, spaces, `:`, embedded and
trailing newlines, punctuation, and non-ASCII letters and digits — must refuse
with zero bytes written. A generator that only fed printable strings and
checked "refuses or round-trips" could not tell an over-accepting grammar from
a correct one.

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
| Greenfield — promote a scaffolded doc's lifecycle (new row, Phase 7) | C1–C5, C19, C23 |
| Greenfield — extend the vocabulary or the date format in `.docs.toml` (existing template guidance) | C4, C20–C22, C24, C25 |
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
- Mutation: pending — hand-applied smoke, eleven targets.
- Fuzz: pending.
- Benchmark/security/schema: pending; benchmark not applicable.
- Coverage: not configured.
- Mock audit: no mocks planned.
- Open risks: none outstanding at setup — Q3, Q7 and Q8 answered by the
  operator on 2026-10-27; the Step 0 review's blockers are fixed, the
  targeted re-review confirmed B1 and B2, and the one blocker it raised
  (claude-RR-B1, an unlisted pre-existing stamp test) is fixed.

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
