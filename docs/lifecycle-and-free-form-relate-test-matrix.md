# M30 — Lifecycle verb and free-form `docs relate` — Test Matrix

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-10-28

Related:
- pairs-with: lifecycle-and-free-form-relate.md
- pairs-with: lifecycle-and-free-form-relate-impl.md

## Risk level

Standard

Reason: proposed at setup and **confirmed by the operator** on 2026-10-27
(setup question Q8 in [the task plan](lifecycle-and-free-form-relate.md)),
and unchanged by the Step 0 review. An additive change to the published CLI:
one new verb, one widened verb, and `parse()` made to honour the tree's config
(D10), with no `docs check` rule change and no verb starting to refuse a
document `docs check` accepts. Every write reuses a proven editor, and the
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
- the Phase 4 / Phase 8 mechanical proof — test ids collected at the
  pre-Phase-1 commit `e48adb9` and at HEAD, compared with `comm`. Phase 4
  collected from a throwaway `git worktree`; Phase 8 used a `git archive`
  extraction, which is equivalent and leaves `.git/worktrees` untouched.
  The proof adds an AST function-body diff of every pre-existing
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
`docs lifecycle` catalogue, P1.1) and `R1`–`R4` (free-form `relate`, P1.2;
R4 added by the Step 1 review)
below refer to it.

| Id | Clause | Source |
|---|---|---|
| C1 | `docs lifecycle <file>... <state>`: the last token is the state; a single token refuses (exit 2, L1); a relative path resolves against the root (OQ-1); outside-root, missing and unparseable documents exit 1 (L8–L10); the strict-root refusals (L2–L4); the batch is validate-all-first | D1 |
| C2 | The target state must be in the tree's lifecycle vocabulary minus `archived`, matched case-sensitively; `archived` refuses with a pointer to `docs archive` (L5); any other unknown state — `Archived` included — refuses naming the allowed states (L6) | D2 |
| C3 | A named document under the archive subtree refuses the whole batch (exit 2, L7) before any per-document check, whatever its position, nothing written | D2 |
| C4 | Extension states (`add_lifecycles`) are valid `docs lifecycle` targets and round-trip through every walking verb (Q7 → A) | D2, D10, A1 |
| C5 | Only a document whose `Lifecycle:` changes is rewritten and gets its `Updated:` bumped; an all-current batch or a `--dry-run` writes nothing at all, INDEX included; a real change is followed by one INDEX refresh (honouring exclusions); a path named twice is planned, listed and written once (OQ-3); the frozen success lines; an INDEX-refresh failure exits 2 with the documents written (L12) | D3 |
| C6 | A free-form `relate add` / `relate remove` rewrites SOURCE's bullet only; TARGET is never written; canonical-target matching; group created/dropped; idempotent; one INDEX refresh after a real change | D4 |
| C7 | Recognized-verb `relate` is byte-for-byte unchanged on every tree `docs check` passes — messages, exits, two-record `--json`, `Revision:`, coordinated-write contract — with D4's two D10 qualifications: on an extension-vocabulary or non-default-date tree an endpoint 2.0.0 refused at exit 1 now resolves; and an endpoint whose `Updated:` is spelled outside a non-default `date_format` (already a `docs check` `bad-date`) — which 2.0.0 accepted — now refuses at exit 1 with that diagnosis (E11) | D4, D10 |
| C8 | A free-form SOURCE under the archive subtree refuses (exit 2, R2) for `add` and `remove`, even when nothing would change | D5 |
| C9 | A free-form TARGET under the archive subtree is allowed, never written, needs no `--reason`, and no `Revision:` is written | D5 |
| C10 | A free-form TARGET may be any existing file under the root, Markdown or not — `broken-ref`'s existence test plus containment; missing / directory / outside-root (including through an escaping symlink) keep exit 1; a symlink inside the tree is resolved to the file it points at; a resolved path holding a line break or leading or trailing whitespace refuses at exit 2 (R4) | D5 |
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
| C22 | A bare `parse(text, path, root)` keeps the built-in defaults; no verb starts refusing a document `docs check` accepts — the alignment covers `Lifecycle:`, `Role:` and `Updated:` only, so a structural fault `docs check` tolerates still fails the verbs that parse the document; D10's three changed outcomes are exactly E11 (walking verbs report the `bad-date` diagnosis `docs check` gives), E12 (C24) and E13 (C25) | D10 |
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

The visible test ids below are final as of Phase 2 (2026-10-27). Pre-existing tests that change are
listed only in the task plan's *Test Strategy* › *Pre-existing tests that
change*.

| Contract clause | Visible test | Hidden/generalization check | Property/stateful check | Mutation target | Fuzz/benchmark/security/schema note |
|---|---|---|---|---|---|
| Success path — lifecycle (C1, C5) | `test_cli_lifecycle.py::test_lifecycle_promotes_a_draft_to_active_and_bumps_updated`; `::test_lifecycle_accepts_several_files_then_one_state_and_refreshes_the_index`; `::test_lifecycle_mixed_batch_rewrites_only_the_documents_that_change`; `::test_lifecycle_leaves_every_other_byte_unchanged`; `test_lifecycle_plan.py::test_plan_lifecycle_stages_only_the_documents_whose_state_differs`; `::test_plan_lifecycle_bumps_updated_only_where_lifecycle_moved`; `::test_apply_lifecycle_plan_writes_only_the_changed_documents` | nested subdirectory docs; non-canonical path spellings | applying twice equals applying once, byte for byte; the batch rewrites exactly the documents whose state differed (an unchanged document keeps its inode), then one INDEX refresh | the `if changed` guard | `--json` key set closed (C15) |
| Duplicate paths (C5, OQ-3) | `test_cli_lifecycle.py::test_lifecycle_plans_and_reports_a_duplicated_path_once`; `test_lifecycle_plan.py::test_plan_lifecycle_lists_a_duplicated_document_once` | other spellings of one path; symlinked named documents | one edit, one line, one record entry | the dedupe on `rel` | — |
| Success path — free-form relate (C6) | `test_cli_relate.py::test_relate_free_form_add_writes_only_the_source_bullet`; `::test_relate_free_form_remove_drops_only_the_source_bullet`; `::test_relate_free_form_matches_a_non_canonical_existing_bullet`; `test_relate_plan.py::test_plan_relate_free_form_stages_only_the_source`; `::test_apply_relate_plan_writes_only_the_source_for_a_free_form_edge` | non-canonical target spellings; a SOURCE with no `Related:` group | `::test_relate_free_form_add_then_remove_restores_the_original_bytes` (with and without an existing group); `::test_relate_free_form_write_rewrites_exactly_one_managed_document` | the recognized-versus-free-form branch | free-form `--json` record (C15): `::test_relate_free_form_json_record_has_null_inverse_and_one_edit`; `test_relate_plan.py::test_relate_plan_to_json_free_form_record_has_null_inverse_and_one_edit` |
| Error path — archive boundary (C2, C3, C8, C23) | `test_cli_lifecycle.py::test_lifecycle_refuses_archived_as_a_target_state`; `::test_lifecycle_treats_a_capitalised_archived_as_an_unknown_state`; `::test_lifecycle_refuses_a_document_under_the_archive_subtree`; `::test_lifecycle_refuses_an_active_tree_document_already_marked_archived`; `::test_lifecycle_batch_with_one_archived_document_writes_nothing`; `test_lifecycle_plan.py::test_plan_lifecycle_refuses_archived_as_a_state`; `::test_plan_lifecycle_refuses_a_source_under_the_archive_subtree`; `::test_plan_lifecycle_refuses_a_source_already_marked_archived`; `test_cli_relate.py::test_relate_free_form_refuses_an_archived_source_even_when_nothing_would_change`; `test_relate_plan.py::test_plan_relate_free_form_refuses_an_archived_source` | `[archive] dir = "attic"` | no allowed transition ever yields `status-drift` (`::test_lifecycle_round_trips_every_top_level_state_without_status_drift`, all five states) | the `archived` target guard; the archive-subtree source guard; the current-`archived` source guard | — |
| Error path — grammar, resolution, root (C1, C2, C10, C11) | `test_cli_lifecycle.py::test_lifecycle_single_token_is_refused_as_ambiguous`; `::test_lifecycle_unknown_state_names_the_allowed_states`; `::test_lifecycle_missing_or_outside_root_file_exits_1_unchanged`; `::test_lifecycle_malformed_document_exits_1_with_the_parser_message`; `::test_lifecycle_refuses_outside_a_docs_root`; `::test_lifecycle_malformed_sidecar_exits_2_and_writes_nothing`; `::test_lifecycle_resolves_a_relative_path_against_the_docs_root_not_the_cwd`; `test_lifecycle_plan.py::test_plan_lifecycle_refuses_an_unknown_state`; `test_cli_relate.py::test_relate_verb_that_would_corrupt_the_block_is_refused`; `::test_relate_leading_hyphen_verb_is_consumed_by_argparse_and_writes_nothing`; `::test_relate_leading_hyphen_verb_after_a_separator_is_refused_by_the_grammar`; `::test_relate_free_form_self_edge_is_refused`; `::test_relate_free_form_still_shape_checks_a_given_reason`; `::test_relate_free_form_source_must_parse_and_exits_1_when_malformed`; `::test_relate_free_form_target_outside_the_root_exits_1`; `::test_relate_free_form_target_that_is_a_directory_exits_1`; `::test_relate_free_form_missing_target_exits_1`; `::test_relate_free_form_target_symlink_escaping_the_root_exits_1`; `::test_relate_free_form_refuses_a_target_path_a_bullet_cannot_carry` (R4: line break, carriage return, leading and trailing space, and — added at Step 3 — a trailing line break); `::test_relate_free_form_refusals_follow_the_frozen_order`; `test_cli_lifecycle.py::test_lifecycle_refusals_follow_the_frozen_order_and_emit_no_record` | grammar-boundary verbs; other line-boundary characters | every refusal leaves the tree byte-identical, INDEX included | the grammar's anchors | security: `:` / newline / carriage-return injection refused; TARGET containment, an escaping symlink included |
| Error path — post-write tail (C5, L12) | `test_cli_lifecycle.py::test_lifecycle_index_refresh_failure_exits_2_with_documents_written` | — | the documents carry the new state; the record reports `index_refreshed: false` | — | — |
| Boundary — free-form verb grammar (C12) | `test_cli_relate.py::test_relate_free_form_verb_grammar_boundary` (22 named cases); `::test_relate_verb_outside_the_free_form_grammar_refuses`; `::test_relate_case_variant_verb_refuses`; `::test_relate_quiet_suppresses_success_but_never_a_refusal` (the last three pre-existing; see the task plan's list); `test_relate_plan.py::test_plan_relate_refuses_a_verb_outside_the_grammar` | `see-Also`, other case mixes, long verbs | valid generated verbs succeed and round-trip through `parse()`; invalid ones refuse with zero writes | `re.fullmatch` vs `re.match` + `$` (`pairs-with\n`); `[0-9]` vs `\d` (`a٣`, `a１`) | fuzz: `test_cli_relate.py::test_relate_free_form_verb_fuzz_round_trips_valid_and_refuses_invalid` (in-process `cli.main`: 30 generated valid verbs, one invalid verb per refused category); `test_relate_plan.py::test_relate_verb_grammar_accepts_and_rejects_generated_verbs` (pure predicate) |
| Boundary — endpoints (C9, C10) | `test_cli_relate.py::test_relate_free_form_archived_target_needs_no_reason_and_is_untouched`; `::test_relate_free_form_accepts_a_non_markdown_target`; `::test_relate_free_form_accepts_a_malformed_markdown_target_without_reading_it`; `::test_relate_free_form_symlinked_target_is_written_as_the_file_it_points_at`; `test_relate_plan.py::test_plan_relate_free_form_never_reads_the_target` | excluded targets; non-Markdown targets of several types | the archived TARGET and the binary TARGET are byte-identical after the run | the archived-endpoint `--reason` rule's branch; `parse_endpoint` | — |
| Boundary — extension vocabulary (C4, C20, C25) | `test_cli_lifecycle.py::test_lifecycle_writes_an_extension_state_and_the_tree_reindexes`; `test_lifecycle_plan.py::test_plan_lifecycle_accepts_a_configured_extension_state`; `test_cli_index.py::test_index_renders_an_extension_role_group_after_the_built_in_roles`; `test_index.py::test_render_index_orders_extension_roles_alphabetically_after_built_ins`; `test_cli_list.py::test_list_includes_a_doc_in_an_extension_lifecycle`; `test_cli_touch.py::test_touch_reindexes_a_tree_with_extension_vocabulary`; `test_walker.py::test_walk_yields_docs_in_extension_vocabulary_and_the_trees_date_format`; `test_cli_relate.py::test_relate_accepts_an_endpoint_in_an_extension_lifecycle`; `test_cli_archive.py::test_archive_accepts_a_primary_in_an_extension_state`; `test_cli_mv.py::test_mv_moves_a_doc_in_a_tree_with_extension_vocabulary`; `test_cli_project_set.py::test_project_set_rewrites_a_doc_in_an_extension_state`; `::test_project_set_knows_a_project_carried_only_by_an_extension_vocabulary_doc`; `test_cli_project_rename.py::test_project_rename_walks_a_tree_with_extension_vocabulary`; `test_cli_stamp.py::test_stamp_keeps_a_document_in_a_configured_extension_state`; `test_model.py::test_parse_with_a_config_accepts_its_extensions_and_date_format` | extension vocabularies of several sizes; hyphenated extension roles | the post-state tree reindexes and `docs check` stays clean | the vocabulary passed to `parse()` at each site; `render_index`'s extension-role placement | — |
| Boundary — date format (C21, C22) | `test_cli_lifecycle.py::test_lifecycle_promotes_an_extension_state_on_a_non_default_date_format_tree`; `test_cli_index.py::test_index_reads_a_non_default_date_format_tree`; `test_cli_touch.py::test_touch_reindexes_a_non_default_date_format_tree`; `test_cli_stamp.py::test_stamp_keeps_a_correctly_dated_document_on_a_non_default_date_format_tree`; `test_cli_archive.py::test_walking_verbs_report_bad_date_on_a_mis_spelled_non_default_tree`; `test_model.py::test_parse_with_a_config_rejects_the_iso_spelling_on_a_non_default_tree`; `::test_bare_parse_keeps_the_built_in_defaults`; `test_cli_relate.py::test_relate_refuses_an_endpoint_dated_outside_the_trees_date_format` (the E11 direction, C7); the corrected `test_cli_archive.py` / `test_cli_mv.py` tests in the task plan's list | `[archive] dir = "attic"` with `%d-%m-%Y`; other formats | `test_model.py::test_config_aware_parse_agrees_with_bare_parse_on_every_pre_existing_tree` — every default-configuration fixture tree and this repository's `docs/` parse identically with and without the config | the `date_format` passed to `parse()` | — |
| Boundary — `docs stamp` (C24) | `test_cli_stamp.py::test_stamp_keeps_a_document_in_a_configured_extension_state`; `::test_stamp_refuses_a_block_outside_the_configured_vocabulary_with_zero_bytes`; `::test_stamp_refuses_a_full_block_with_an_invalid_role_with_zero_bytes` (pre-existing, renamed — see the task plan's list); `::test_stamp_refuses_a_typod_lifecycle_on_a_default_tree_with_zero_bytes` (`--dry-run` too); `::test_stamp_refuses_a_block_dated_outside_the_trees_date_format_with_zero_bytes`; `::test_stamp_refusal_in_a_batch_writes_no_file`; `::test_stamp_refuses_a_complete_block_without_a_project_line_with_zero_bytes`; `::test_stamp_freshly_stamps_an_incomplete_block_even_with_an_out_of_vocabulary_value` (the completeness boundary's other side); `::test_stamp_restamps_a_complete_block_whose_related_bullet_is_malformed`; `::test_stamp_keeps_a_correctly_dated_document_on_a_non_default_date_format_tree`; `::test_stamp_restamps_an_extension_vocabulary_block_whose_related_bullet_is_malformed` and `::test_stamp_refuses_an_extension_state_block_for_its_invalid_role_with_zero_bytes` (the vocabulary source, added by the Step 2 review) | — | the refused file, every other file and the INDEX are byte-identical | `docs stamp`'s block classification | — |
| Idempotency/retry/state (C5, C6) | `test_cli_lifecycle.py::test_lifecycle_already_in_state_writes_zero_bytes_and_skips_reindex`; `test_cli_relate.py::test_relate_free_form_is_idempotent` | — | idempotence over every top-level state; a no-op leaves a sentinel INDEX byte-identical | the `if changed` guard; the no-reindex-on-a-no-op guard | — |
| Preview, output, record (C5, C15) | `test_cli_lifecycle.py::test_lifecycle_dry_run_writes_nothing_and_previews_each_change`; `::test_lifecycle_json_record_has_a_closed_key_set`; `::test_lifecycle_dry_run_json_has_the_apply_shape`; `::test_lifecycle_quiet_suppresses_success_but_never_a_refusal`; `::test_lifecycle_reindex_honours_exclusion`; `test_lifecycle_plan.py::test_lifecycle_plan_to_json_has_a_closed_key_set`; `test_cli_relate.py::test_relate_free_form_dry_run_writes_nothing` | — | a preview writes nothing, INDEX included | — | schema: both records closed |
| Regression — recognized verbs (C7) | every pre-existing `test_cli_relate.py` / `test_relate_plan.py` id, unedited except as the task plan's list says; `test_cli_relate.py::test_relate_recognized_pair_still_writes_both_halves_unchanged` | — | a recognized operation rewrites at most two managed documents plus one INDEX refresh | the recognized-versus-free-form branch | recognized `--json` record asserted value for value |
| Regression — archive invariance (C13) | `test_cli_archive.py::test_cascade_candidates_match_when_edges_were_written_by_relate`; `::test_strand_refusal_fires_on_a_child_of_written_by_relate` | a real milestone trio from this tree (Phase 9) | — | — | — |
| Regression — `--body-from` route (C14) | `test_body_from.py::test_body_opening_with_a_related_group_becomes_metadata`; `::test_inline_related_line_stays_body_text`; `::test_skill_sidecar_example_yields_its_edge` (both frozen forms) | a non-Markdown sidecar target | — | — | — |
| External consumer (C16) | `test_cli_lifecycle.py::test_help_verb_list_names_lifecycle_for_the_playbook_guard`; `test_cli_relate.py::test_playbook_guard_free_form_dry_run_probe_exits_0` | the same probes against a locally built wheel (Phase 9) | — | — | — |
| Surface parity (C17, C18) | `test_skill.py::test_every_named_verb_is_a_real_subcommand` (existing); `::test_skill_routes_lifecycle_and_free_form_edges_through_verbs`; `::test_shipped_surface_no_longer_says_free_form_verbs_are_hand_edited`; `test_cli_lifecycle.py::test_lifecycle_help_documents_the_grammar_and_flags`; `test_skill_refs.py` (existing byte identity); `test_skill.py::test_frontmatter_values_are_scalars_yaml_reads_back_verbatim` and `::test_yaml_scalar_check_rejects_exactly_what_a_yaml_loader_would_break` (the skill's frontmatter loads as YAML; added by the Step 2 review); the 2.1.0 packaging pins in the task plan's list | — | — | — | — |
| Acceptance — primary use case (C19) | `test_cli_lifecycle.py::test_milestone_setup_needs_no_hand_edit` | the same flow on this repository's own tree copy (Phase 9) | no managed document changes outside a verb invocation; a repeated promotion writes nothing | — | runtime recorded in Phase 9 |
| Security/privacy/perf | covered above: block-corruption refusals (C11), TARGET containment (C10) | — | — | — | benchmark: not applicable; runtime recorded, not budgeted |

## Visible tests

The modules and their new ids as written in Phase 2 (names state scenario and
outcome, with no milestone, decision or release identifiers). Every
pre-existing test the milestone edits is in the task plan's authoritative
list, not here.

- `tests/test_cli_lifecycle.py` — **new**, 36 ids: C1–C5, C15, C16 (help
  probe), C19, C23, the strict-root and malformed-sidecar refusals, the
  root-relative path rule (OQ-1), the refusal order, an extension state on a
  non-default date tree, deduplication and the INDEX-refresh-failure tail.
- `tests/test_lifecycle_plan.py` — **new**, 10 ids: the pure planner, apply
  and record (OQ-12).
- `tests/test_cli_relate.py` — 58 new ids: C6–C12, C15, C16 (relate probe),
  TARGET containment (outside the root, a directory, missing, an escaping
  symlink), a malformed SOURCE, a malformed-Markdown and a symlinked TARGET,
  R4, the refusal order, the `--reason` shape check, the E11 direction for an
  endpoint, the 22-case grammar boundary, the in-process fuzz, and the
  recognized-pair byte lock.
- `tests/test_relate_plan.py` — 11 new ids: the one-sided plan (one edit, no
  inverse, TARGET never read), the grammar guard, and the pure-predicate fuzz.
- `tests/test_cli_archive.py` — 4 new ids: C13, C21's walking-verb `bad-date`
  lock, and an extension-state primary.
- `tests/test_body_from.py` — 4 new ids: C14.
- `tests/test_cli_stamp.py` — 9 new ids: C24, including both sides of the
  complete-block boundary and the date half of E12. The Step 2 review added
  2 more, which pin the refusal's vocabulary source on an extension tree.
- `tests/test_index.py`, `tests/test_cli_index.py` — 1 + 2 new ids: C25, C21.
- `tests/test_skill.py` — 2 new ids: C17. The Step 2 review added 12 more:
  the frontmatter YAML lock and its 11-case non-vacuity table.
- `tests/test_model.py` — 4 new ids: C20–C22, including one parse-agreement
  sweep over the 52 default-configuration fixture trees plus this
  repository's `docs/`, reporting each disagreement by file.
- For D10 (C20–C22) elsewhere: `tests/test_cli_list.py` (1),
  `tests/test_cli_touch.py` (2), `tests/test_walker.py` (1),
  `tests/test_cli_project_set.py` (2), `tests/test_cli_project_rename.py`
  (1), `tests/test_cli_mv.py` (1).

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
  non-empty one — for a document with LF line endings (every editing verb
  normalises CRLF to LF; the task plan's *Contract* › *Invariants* and
  *Follow-ups* item 11). From an arbitrary initial state the assertion is the
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

- New mocks: none. The Phase 8 audit found 0 new or expanded mocks.
- Justification: not applicable. Phase 1 (OQ-2) made the multi-file
  `docs lifecycle` write sequential, as `project set` does, with no staged
  publish or rollback, so no write-failure injection was needed. L12's
  INDEX-refresh failure uses a real malformed sibling.
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

- Visible tests: RED baseline (Phase 4, 2026-10-27; restated after the
  Step-1 audit and the Step 1 review resolution) — 1656 collected, 150
  failed, 1506 passed: 142 authored ids and the 8 pre-existing ids on the
  task plan's authoritative list RED for missing behaviour; 7 authored locks
  and 3 swept ids GREEN (classified in the implementation log's Phase 4).
- Visible tests, GREEN (Phase 8, 2026-10-28): **1656 passed**, 0 failed,
  skipped, xfailed or errored. After the Step 2 review resolution: **1670
  passed**. The 14 added ids are the skill frontmatter YAML lock with its
  11-case table, and two stamp tests for the stamp check's vocabulary
  source. After Step 3's `/simplify` pass: **1671 passed**. The one added id
  is the R4 row `a-trailing-line-break`. It pins the case the simplified
  predicate now refuses through its strip test alone, and it passes on the
  pre-simplify code too.
  - Every pre-existing id is present and GREEN under the authoritative old →
    new mapping (the `comm` / AST proof against `e48adb9`).
  - Two authored tests were corrected under Check calibration: DEF-1, a help
    assertion that depended on terminal width, and DEF-2, a planner-guard
    fixture that a second guard masked. Both are in the implementation log's
    Phase 8.
- Hidden/generalization: categories only (the repository is fully visible).
  Phase 9 (2026-10-28) exercised every category on throwaway trees, all as
  the contract says (implementation log, *Phase 9*):
  - extension vocabularies (F5a);
  - non-default `date_format` and `[archive] dir = "attic"` (F5b, F5c);
  - nested subdirectory documents, duplicate spellings in one batch,
    non-canonical TARGETs (`./b.md`, `sub/../b.md`), non-Markdown and
    excluded TARGETs, and grammar-boundary verbs (F6);
  - the real M30 trio from this tree, rewritten through verbs, with closeout
    records identical to the hand-written edges (F3b).
- External consumer (Phase 9 F2): both suite probes return True / True on
  the editable build and on a locally built 2.1.0 wheel in a fresh venv. The
  host 2.0.0 control returns False / False.
- Runtime (Phase 9 F8, recorded, not budgeted; median of 5 on this tree of 16
  active and 61 archived documents):
  - `docs lifecycle` on three documents: 131 ms, against `touch` at 129 ms;
  - free-form `relate`: 121 ms, against recognized at 124 ms;
  - `index` and `list`: within 4 ms of v2.0.0;
  - `check`: +6 to +17 ms, with no M30 change on its path.
- Reindex identity (Phase 9 F7): `INDEX.md`, `list --json` and
  `check --json` over this tree are byte-identical under 2.1.0 and v2.0.0.
- Property/stateful (Phase 8): **16 passed**, covering idempotence, the
  add-then-remove round trip, no `status-drift`, and write footprint.
- Mutation (Phase 8, extended by the Step 2 review): hand-applied smoke
  **47/47 killed**, covering all
  eleven targets.
  - 43 planned mutants plus 2 message-preserving variants of the grammar
    mutants.
  - M05 survived at first; correcting the authored fixture (DEF-2) killed it.
  - M44 and M45 judge the stamp refusal's vocabulary against the built-ins.
    Both survived at the Step 2 review (claude-S1), and the two stamp tests
    added by its resolution kill them.
  - Phase 10's `/simplify` (S1) rewrote `docs stamp`'s completeness test.
    M40–M43 were re-proven on the simplified code with the same kill counts
    (6, 12, 1, 1), so adequacy is unchanged.
  - Step 3's `/simplify` (S7, claude-T1) rewrote the R4 predicate. M21 was
    re-proven on the new code with the same three killers. Three
    term-isolating variants were run before and after, and a fourth, the
    new line-count threshold (M21t), after. Dropping either term is killed in
    both. Weakening the strip test to spaces (M21w) survived before but is
    killed after, by the added row. Adequacy is unchanged for the smoke and
    stronger for R4.
- Fuzz (Phase 8): **24 passed**, seed `20261027`.
  - The pure predicate: 300 valid, 300 invalid and `""`.
  - The CLI: 30 valid verbs plus 11 invalid categories.
  - The 22-case boundary table.
- Benchmark/security/schema (Phase 8): the schema locks (both records closed;
  the recognized record value for value) and the security locks (verb
  injection, R4, TARGET containment) passed. Benchmark not applicable;
  runtime is recorded at Phase 9.
- Coverage: not configured.
- Mock audit (Phase 8): **0 new or expanded mocks**. Instead the tests use a
  sentinel INDEX, a real malformed sibling, inode checks and in-process
  `cli.main`.
- Open risks: none outstanding at setup — Q3, Q7 and Q8 answered by the
  operator on 2026-10-27; the Step 0 review's blockers are fixed, the
  targeted re-review confirmed B1 and B2, and the one blocker it raised
  (claude-RR-B1, an unlisted pre-existing stamp test) is fixed.

## Adequacy results

- visible_pass_rate: 1671/1671 (1656/1656 at Phase 8; 14 ids added by the
  Step 2 review resolution; 1 R4 row added by Step 3's `/simplify`)
- hidden_pass_rate: not applicable (no hidden suite)
- hidden_generalization_gap: not applicable
- changed-lines coverage: not configured
- changed-files branch coverage: not configured
- mutation score on touched modules: 47/47 killed by the hand-applied smoke
  on `src/docs_cli/cli.py` (43 planned, 2 message-preserving variants, and
  M44/M45 from the Step 2 review),
  after one authored-fixture correction (DEF-2); M21 re-proven after Step 3's
  R4 rewrite, with four term-isolating R4 variants also killed (5/5)
- property/stateful result: 16 passed
- fuzz result: 24 passed (seed `20261027`)
- benchmark delta: not applicable; runtime recorded in Phase 9
- security/schema/migration result: security and schema locks passed;
  migration not applicable
- skipped deep gates and follow-up: none skipped; coverage and mutation tooling
  are not configured in this project
