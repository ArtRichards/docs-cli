# M30 — Lifecycle verb and free-form `docs relate` — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-10-28

Related:
- pairs-with: lifecycle-and-free-form-relate.md
- pairs-with: lifecycle-and-free-form-relate-test-matrix.md

## Overview

Chronological implementation log for M30 — Lifecycle verb and free-form
`docs relate` (semantic slug `lifecycle-and-free-form-relate`). Append one
evidence-backed section per TDD phase; keep the progress table, the milestone
checklist and the test matrix synchronized.

## Implementation metadata

- Project: docs
- Milestone: `lifecycle-and-free-form-relate` — M30, Lifecycle verb and
  free-form `docs relate`
- Tracker: order 100, `active` since the claim commit `2ad941e`, no
  dependencies ([milestone-plan.md](milestone-plan.md))
- Started: 2026-10-26 (milestone setup); Step 1 (Phases 1–4) started
  2026-10-27 on `lifecycle-and-free-form-relate/phases-1-4`
- Step 1: **complete (2026-10-27)** — Phases 1–4 done, the same-instance
  audit folded in, and `Step 1 review-pass-001` closed: both providers
  returned, both blockers and every accepted should-fix, nit and taste
  finding fixed in `9b8c83e` (one taste finding waived), re-review not
  required. The contract is frozen in the task plan's *Decisions (Phase 1 —
  BINDING)*, with R4 added by the review; the RED baseline stands at **1656
  collected, 150 failed, 1506 passed** (classified in *Phase 4* and its
  restatements). Details: the phase sections below, *Step 1 same-instance
  audit*, and *Step 1 review-pass-001*.
- Step 2 (Phases 5–10): **in progress** on
  `lifecycle-and-free-form-relate/phases-5-10` from base `3e2c3ca`.
  Phases 5–7 are complete. Step 2 was interrupted after Phase 7 and resumed
  on 2026-10-28; Phases 8–10 are complete and implementation is done. The
  Step 2 review is pending (*Step 2 review-pass-001*). See the phase sections
  below and the *Milestone completion summary*.
- Progress: **Milestone setup complete (2026-10-27); all nine setup
  questions RESOLVED — Q3, Q7 and Q8 by operator decision on 2026-10-27, each
  as recommended; Q1, Q2, Q4, Q5, Q6 and Q9 conductor-resolved. Step 0
  review-pass-001 is **closed**: both providers returned, every blocker,
  should-fix and nit is dispositioned (one nit waived), the targeted re-review
  confirmed both original blockers fixed, and the one blocker it raised
  (claude-RR-B1) is fixed in the sync commit that closes the pass. Phase 1 —
  Define Contract follows and does not re-open any of the nine questions or
  D10.**
  This bullet is the milestone's progress narrative; the task plan's
  *Overview* points here. Setup measured this repository read-only and
  reproduced every behaviour on throwaway trees in the session scratchpad,
  producing evidence **E1–E11**; the Step 0 review added **E12** and **E13**.
  - **E7 / E8** — a vocabulary extension (the `add_lifecycles` states the
    registered scope promises `docs lifecycle` will write) or a non-default
    `date_format` already breaks every verb except `docs check`, because
    `parse()` ignores the tree's config. The operator answered **Q7** by
    bringing the cause into scope: **D10** makes `parse()` honour the tree's
    config at every call site, and **E11** bounds the date half's changed
    outcome to a tree that already fails `docs check`.
  - **E12 / E13** (Step 0 review) — the two places a config-aware `parse()`
    reaches: `docs stamp` destroys a valid extension-state document on 2.0.0,
    so by operator decision (Packet A) it now refuses a full block that fails
    the tree's config; and `render_index` would silently drop extension-role
    documents, so they now render after the built-in roles, alphabetically.
    Both are frozen into D10.
  - **E4 / E5** — `docs check` parses no token grammar for a `Related:` verb,
    so a mistyped `Precedes` would become a silent one-sided edge; the
    operator answered **Q3** with the lowercase kebab token
    `[a-z][a-z0-9-]*` (**D6**).
  - **E6** — writing `Related:` edges through `--body-from` has been the
    bundled skill's documented intent since M8, with no test, and in an
    inline spelling that the grammar reads as body text (corrected by the
    review); the group form is the supported route (**Q5**, D8).
  - **E2** — the one external consumer, the Agent Playbook Suite's CI guard,
    whose two probes become product tests.
  - Risk is **Standard**, operator-confirmed (**Q8**) and unchanged by the
    review.
- Source: `feedback-log.md`, 2026-10-26 — *No verb for draft→active or
  free-form `Related:` edges; suite and bundled skill disagree on the
  hand-edit fallback*, promoted to this milestone the same day with three
  operator decisions.
- Branch: `lifecycle-and-free-form-relate/milestone-setup` for setup;
  implementation branches follow the ship-milestone stack
  (`lifecycle-and-free-form-relate/phases-1-4`, `…/phases-5-10`,
  `…/simplify`).

## Risk / Adequacy Tracking

- Risk level: **Standard** — proposed at setup and confirmed by the operator
  (Q8, 2026-10-27), with D10's core-read-path fix in scope.
- Test matrix:
  [lifecycle-and-free-form-relate-test-matrix.md](lifecycle-and-free-form-relate-test-matrix.md)
- High-risk RED approval: not applicable — Standard risk, no Phase-4
  operator checkpoint.
- Hidden/generalization handling: categories only (repository fully visible);
  exercised by property checks and the Phase-9 dogfood.
- Mock audit: **complete (Phase 8)**, 0 new or expanded mocks.
- Adequacy results (Phase 8):
  - `visible_pass_rate` 1656/1656;
  - hand-applied mutation smoke 45/45 killed (43 planned plus 2
    message-preserving variants), after one authored-test fixture correction
    (DEF-2);
  - property / stateful 16 passed and fuzz 24 passed (seed `20261027`);
  - schema and security locks passed;
  - hidden suite and coverage not configured.
- Taste triage: Step 0 review-pass-001 triaged — GPT: sound, no subjective
  findings; claude-T1 partially fixed and the remainder waived with reason;
  claude-T2 and claude-T3 fixed; patch bloat in line with precedent (see the
  pass entry below). Step 1 review-pass-001 triaged — GPT: sound, no
  subjective findings; claude-T1, T2 and T3 fixed; claude-T4 waived with
  reason (*Follow-ups* item 10). Step 2 self-triage (Phase 10): every row is
  fixed, kept or waived with a reason — see *Phase 10* › *Taste triage*.

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-10-27 | Freeze against the answered Q1–Q9: `docs lifecycle`'s `*files, <state>` grammar, state vocabulary (built-ins plus `add_lifecycles` extensions, minus `archived`), refusal set and order, idempotence and single-reindex rules, output lines and `--json` record; free-form `relate`'s grammar (`[a-z][a-z0-9-]*`, D6), endpoint rules (archived SOURCE refused, archived TARGET never written, any existing file as TARGET), one-sided write and record; recognized-verb byte stability; the `--body-from` sentence; D10's config-aware `parse()` signature and how its sites obtain the config (D10's behaviour, `render_index` placement and `docs stamp` refusal are frozen); the stamp refusal's message; argparse's leading-hyphen handling; the upgrade note's three D10 changes; the surface list; the Phase-5 signatures. |
| 2. Write Tests (RED) | Complete | 2026-10-27 | New `tests/test_cli_lifecycle.py`; free-form additions to `tests/test_cli_relate.py` and `tests/test_relate_plan.py`; archive-invariance locks; the `--body-from` lock; skill parity; the 2.1.0 pin; both suite-probe replicas; D10's vocabulary, date-format, `render_index` and `docs stamp` locks; the pre-existing tests edited exactly as the task plan's *Pre-existing tests that change* lists. |
| 3. Create Data/Fixtures | Complete | 2026-10-27 | Inline `tmp_path` builders for every write-then-compare case; archive invariance by copying `archive-neighborhood` / `movelink-strand` and re-linking through `relate`; for D10, one `vocab-extension/` tree with the sweep registration updated, inline builders for every non-default `date_format` case, and the `tests/test_cli_mv.py` `_attic_tree` correction. |
| 4. Run Tests (RED Baseline) | Complete | 2026-10-27 | Classified failure set against the 1504-test baseline; every GREEN-at-baseline lock named; every pre-existing id accounted for through the plan's explicit old → new mapping. No operator checkpoint (Standard). |
| 5. Update Base Interfaces | Complete | 2026-10-27 | `relate_verb_in_grammar` / `_RELATE_VERB_RE`; `parse(..., *, config=None)`; `RelatePlan.inverse: str \| None` and `plan_relate`'s one-sided branch; `LifecycleEdit`, `LifecyclePlan`, `plan_lifecycle`, `apply_lifecycle_plan`, `lifecycle_plan_to_json` — wired nowhere. 126 failed / 1530 passed: exactly the 24 Phase-5 ids flipped. |
| 6. Implement Offline/Core Path | Complete | 2026-10-27 | `docs lifecycle` registered (final help) over the planner; free-form `relate` with R1, R2, R4 and the never-parsed TARGET; the config at the seven `parse()` sites; `render_index`'s extension groups; the stamp refusal. 9 failed / 1647 passed: the 8 Phase-7 ids plus the expected transient skill-completeness guard. |
| 7. Update Tool/Wrapper Layer | Complete | 2026-10-27 | Help text for `relate`, `stamp`, `--body-from` and `main()`; specs reconciled (no change needed); the skill body, *Three things never to hand-edit*, *Quality artifacts*, `use-cases.md` (frozen P1.3 row + two new rows), the adoption playbook (frozen P1.3 bullet), *Linking reports*; README; 2.1.0 and `## 2.1.0 — UNRELEASED`; feedback-log closures, the promotion note, follow-ups 1, 2, 3, 7, 8, 9 registered. 1656 passed; stale-wording grep empty. |
| 8. Run Tests (GREEN) | Complete | 2026-10-28 | 1656 passed; ruff, format, mypy, `docs check`, mirrors and snapshot clean. Id/AST proof against `e48adb9` is exactly the authoritative mapping (1504 → 1656, the 4 renamed ids removed, 156 added). Property 16, fuzz 24, schema and security passed. Mutation smoke 45/45 killed: 43 planned plus 2 message-preserving variants, after correcting DEF-2's fixture (M05). 0 mocks. DEF-1 (a help assertion that depended on terminal width) fixed. |
| 9. Integrate / Accept / Dogfood | Complete | 2026-10-28 | F1–F10 on throwaway trees, unattended. The primary use case needed zero hand-edits and a repeat was a zero-byte no-op. Both suite probes pass on the editable build and a local wheel and fail on 2.0.0. Closeout records are identical for the dogfood trio (with a byte-identical `--body-from` twin) and for the real M30 trio rewritten through verbs. The leg-1 refusal and the archive-boundary refusals hold. The D10 extension and date-format trees work, with the E11 and E12 contrasts. This tree reindexes identically to v2.0.0. Runtime recorded; real tree and host untouched. |
| 10. Quality, Docs, Refactor | Complete | 2026-10-28 | Light `/simplify`: S1 taken (`_stamp_config_failure`'s completeness test made explicit; M40–M43 re-proven), S2–S7 rejected with reasons. `architecture.md`: the `lifecycle` and `relate` module map, a `### lifecycle (M30)` section and the one-sided relate path, plus accuracy fixes. `test-strategy.md`: two critical paths and `vocab-extension/`. The D9 hand-off in `feedback-log.md`. Follow-ups 6 (declined) and 10 (a candidate convention) decided. Taste triage, boundary sweep, surface parity and the archive-readiness preview done. |

## Setup record — 2026-10-26

### Objective

Bring the registered intentional stub up to full milestone-task-plan depth,
create this log and the test matrix, link the three artifacts, and promote them
to `active` — without starting Phase 1. The tracker row was claimed `active`
at order 100 in `2ad941e`. The stub's goal, binding scope, discovery decisions,
open questions and success criteria — including the suite-stopgap retirement
criterion — are carried forward rather than replaced; its four "Open questions
for M30 Phase 1" are carried as Q1–Q4, and the feedback log's `--body-from`
observation as Q5.

### Actions taken

- Read the inputs end to end: `CLAUDE.md` (skill update channels), the
  `create-milestones` skill with its playbook and phase reference, the shared
  quality model, tracker contract and operator-interaction policy;
  [milestone-plan.md](milestone-plan.md)'s canonical tracker and *Ongoing
  conventions*; [charter.md](charter.md); the pinned specs
  ([cli.md](cli.md), [convention.md](convention.md),
  [architecture.md](architecture.md), [test-strategy.md](test-strategy.md));
  [status.md](status.md); and the 2026-10-26, 2026-08-15 and 2026-08-09
  entries of [feedback-log.md](feedback-log.md). Read the closest precedents
  at their setup commits — M28a's plan and log as committed in `7f7853b`, and
  M16's test matrix, the project's only earlier one.
- Read the code the milestone extends: `RECIPROCAL_INVERSES` /
  `inverse_verb`; `_cmd_relate`, `_resolve_relate_endpoint`, `plan_relate`,
  `_plan_relate_edit`, `apply_relate_plan`; `add_related_edge` /
  `remove_related_edge`; `set_metadata_field` and its one `Lifecycle:` call
  site in `_archive_one`; `parse()`, `parse_metadata_block`,
  `_metadata_line_span`; `validate_lifecycle` and the `Config` vocabulary
  merge; `_cmd_touch`; `_cmd_project_set`'s spec; `_body_has_metadata_block`;
  `_CASCADE_VERBS`; and the tests pinning today's `relate` refusals and the
  skill's verb-completeness guard.
- Read the external consumer: the Agent Playbook Suite's
  `_shared/references/verbless-metadata-edits.md` and its CI step *Validate
  verbless-metadata stopgap matches the pinned docs-cli* (suite `a997954`,
  pinned `DOCS_CLI_VERSION: "2.0.0"`).
- Ran a **read-only** census of every `Related:` verb across `docs/` (live and
  archive), all committed fixture trees, the bundled skill and the suite's
  prescriptions (E3).
- Reproduced every behaviour on **throwaway trees** in the session scratchpad:
  the parser's verb grammar (E4), today's `relate` refusals including the
  suite probe (E2, E5), the `--body-from` route with `Related:` and `Revision:`
  groups (E6), extension lifecycles and roles across every walking verb (E7),
  a non-default `date_format` across `new` / `index` / `touch` / `check` (E8),
  and a non-Markdown `relate` target (E9). No repository file was mutated by a
  probe.
- Verified the tracker relationships rather than assuming them: one row, order
  100, no dependencies, no other cohort — the desired recognized edge set is
  empty, and `docs list --json` shows no `precedes` / `follows` /
  `depends-on` / `required-by` / `blocks` / `blocked-by` edge touching the
  milestone. No `docs relate` operation was needed.
- Validated the physical identity: no live or archived basename uses
  `lifecycle-and-free-form-relate.md`, `-impl.md` or `-test-matrix.md` other
  than the stub itself.
- Expanded the stub in place under its unchanged metadata block: *Risk Level*;
  *Binding scope* as D1–D9 with the registered bullets carried verbatim and
  marked; *Contract* with taste anchors; *Out of scope*; E1–E10 with an
  *Evidence → regression coverage* table; *Test Strategy*; per-phase
  objective / files / exit for all ten phases; the checklist; *Decisions
  recorded at setup* (A1–A3); *Setup questions (Q1–Q9)*; follow-ups; the
  gate; and the success criteria — the registered five verbatim, plus
  evidence-anchored ones.
- Scaffolded this log with `docs new log lifecycle-and-free-form-relate-impl`
  and the matrix with `docs new spec
  lifecycle-and-free-form-relate-test-matrix`, both through `--body-from`.
- Registered the vocabulary-extension defect (E7) as a dated
  `feedback-log.md` entry and added the measured wider blast radius (E8) to the
  open 2026-08-15 `date_format` entry.
- Updated the `status.md` narrative; regenerated the INDEX and refreshed the
  frozen dogfood snapshot `tests/fixtures/expected/docs-INDEX.md`, as every
  earlier setup did.

### Metadata edits and the route used for each

docs-cli 2.0 has no verb for a non-archived `Lifecycle:` transition or for
adding a free-form `Related:` bullet to an existing document — the gap this
milestone closes. The operator approved, for this ship run, exactly the edits
the `create-milestones` precedent prescribes on this milestone's own three
artifacts. Each was applied as listed, nothing else in any metadata block was
changed by hand, and `docs touch` followed each hand-edit.

| Document | Edit | Route |
|---|---|---|
| `lifecycle-and-free-form-relate-impl.md` | `pairs-with` the task plan and the test matrix | `docs new --body-from` — the body's leading `Related:` group (no hand-edit) |
| `lifecycle-and-free-form-relate-test-matrix.md` | `pairs-with` the task plan and the implementation log | `docs new --body-from` — the body's leading `Related:` group (no hand-edit) |
| `lifecycle-and-free-form-relate.md` | add `pairs-with` the implementation log and the test matrix | operator-approved hand-edit, then `docs touch` |
| `lifecycle-and-free-form-relate.md` | `Lifecycle: draft` → `active` | operator-approved hand-edit, then `docs touch` |
| `lifecycle-and-free-form-relate-test-matrix.md` | `Lifecycle: draft` → `active` | operator-approved hand-edit, then `docs touch` |
| `lifecycle-and-free-form-relate-impl.md` | `Lifecycle: draft` → `active` | operator-approved hand-edit, then `docs touch` |

The task plan's existing `child-of: milestone-plan.md`, `implements:
charter.md` and context `pairs-with` / `references` bullets were written when
the stub was registered and were left untouched. Two edges the M28a log
carried were deliberately **not** added, because the approval covers
`pairs-with` among the three artifacts, `child-of: milestone-plan.md`, and
context edges to the pinned specs, and neither of these is one of those:
a `child-of` / `parent-of` pair between the log and the task plan, and the
log's `pairs-with: status.md` / `references: feedback-log.md`. Both can be
written with free-form `docs relate add` once this milestone ships.

### Current-tree evidence (docs-cli 2.0.0 at `2ad941e`)

| Evidence | Measurement | Why it matters | Bears on |
|---|---|---|---|
| **E1** | `_archive_one` is the only post-creation writer of `Lifecycle:` — `set_metadata_field(…, "Lifecycle", "archived")`. `docs new` and `docs stamp` write `draft`; `docs touch` writes `Updated:` only. | The editor the lifecycle verb needs exists and is exercised by every archive; the verb is a thin wrapper with `docs project set` as its template. | D1–D3 |
| **E2** | In a fresh tree of two `docs new spec` documents, `docs relate add a.md pairs-with b.md --dry-run` exits 2: `unknown verb 'pairs-with'; expected one of: blocked-by, blocks, depends-on, follows, precedes, required-by`. `docs --help` renders its verbs as one brace group with no `lifecycle`. The suite's CI step runs exactly that probe and parses exactly that group. | The suite guard is an external contract consumer: it reads `lifecycle verb: False`, `free-form relate: False` against 2.0.0, and it is the signal that retires the stopgap. Both probes become product tests. | D1, D9 |
| **E3** | `docs/` (live and archive): **417** `Related:` edges in 74 documents — **391** free-form across 7 verbs (`pairs-with` 238, `child-of` 59, `parent-of` 52, `implements` 21, `references` 17, `decision` 2, `spec-of` 2) and **26** recognized. Fixtures: 96 edges, 13 verbs (adds `see-also`, `supersedes`, `superseded-by`, `blocks`, `blocked-by`). Bundled skill: 5 edges, 3 verbs. Suite prescriptions: `pairs-with`, `child-of`, `implements`, `references`. **Every verb matches `[a-z][a-z0-9-]*`.** | Free-form is 94% of the real graph, and a strict lowercase token loses nothing measured anywhere. | D6, Q3 |
| **E4** | Hand-written bullets on a throwaway tree: `- : target.md`, `- see also: target.md`, `- @#!$: target.md`, `- Precedes: target.md` and `- pairs-with  : target.md` all pass `docs check` with no finding; `docs list --json` reads their verbs as `""`, `"see also"`, `"@#!$"`, `"Precedes"`, `"pairs-with"`. Only a missing colon / empty target (`malformed`) or an unresolvable target (`broken-ref`, e.g. `.`) fails. *(Corrected at the Step 1 review resolution: a missing colon (`- no-colon-here`) and an empty target (`- verb:`) both pass `docs check` at exit 0 — only the unresolvable target fails — while every verb that parses the document refuses it with `malformed Related entry`.)* | `docs check` parses no token grammar — it accepts anything before the first colon. The registered recommendation "accept exactly the token grammar `docs check` already parses" therefore does not pin a grammar. | D6, Q3, A2 |
| **E5** | `docs relate add a.md Precedes b.md --dry-run` exits 2 (`unknown verb 'Precedes'`), pinned by `test_relate_case_variant_verb_refuses`. | Under a parser-mirroring grammar this refusal becomes an exit-0 one-sided `Precedes:` edge that reciprocity ignores — a silently wrong edge. | D6, Q3 |
| **E6** | `docs new spec a --body-from body.md`, body opening `Related:` / `- pairs-with: b.md` / `- references: b.md`: the group lands in the metadata block; `docs list --json` lists both edges; `docs check` clean. A body opening with a `Revision:` group lands in the block of an **active** document the same way. A lone `Lifecycle: active` line after the blank line stays body. `references/use-cases.md` row *Sidecar a non-md artifact* prescribes `--body-from -` with `Related: artifact-of: <binary>` ("No new verb — uses the M8 `--body-from` flag"); `references/adoption-playbook.md` repeats it and describes the refusal heuristic as `^[A-Z][A-Za-z-]+:\s` — the pre-M15 — C4 wording. No test in `tests/test_body_from.py` or `tests/test_cli_new.py` mentions `Related`. | The route is the skill's documented intent — supported, not an accident — and it is untested. **Corrected by the Step 0 review (claude-S2):** both skill examples spell `Related:` inline, and `printf 'Related: artifact-of: deck.html\n\n## Body\n' \| docs new notes inline --body-from -` yields no edge (`docs list --json`: `[]`), while the group form yields `artifact-of: deck.html`; Phase 7 rewrites both examples. Its generality (any bare-label group) is a separate leak; the playbook line is stale bundled guidance. | D8, Q5, A3 |
| **E7** | `.docs.toml` with `[vocabulary] add_lifecycles = ["shipped"]`, one document hand-set to `Lifecycle: shipped`: `docs index` exit 2 (`Lifecycle: 'shipped' not in vocabulary`); `docs touch b.md` (another document) writes, then exit 2 `INDEX refresh failed`; `docs list` and `docs list --json` omit the document, exit 0 — silently (corrected at the Step 1 review resolution, claude-N7: setup said "printing the error on stderr"; re-measured, stderr is empty); `docs relate add a.md precedes b.md` exit 1; `docs archive a.md --dry-run` exit 1; `docs mv b.md c.md --dry-run` exit 2; `docs check` **no violations, exit 0**. With `add_roles = ["adr"]`: `docs new adr x` exit 0, then `docs index` exit 2. Cause: `parse()` calls `validate_lifecycle(lifecycle, BUILTIN_STATUSES)` and `validate_role(role, BUILTIN_ROLES)` rather than the tree's merged vocabulary, and `walk()`, `query_docs`, `_cmd_archive`, `_known_projects`, `_cmd_project_set`, `_resolve_relate_endpoint` and `_cmd_stamp` all go through it. Five fixture sidecars carry `add_roles = []`; none exercises a non-empty extension through a walk. This repository's `.docs.toml` and the bundled template advertise the feature. | The registered clause "any `add_lifecycles` extension … and reindexes once" cannot hold on 2.0.0: the verb would write a state that its own reindex rejects. Both new verbs validate endpoints through `parse()`, so the answer decides whether they work on such trees at all. | D2, Q7, A1 |
| **E8** | `.docs.toml` with `[archive] date_format = "%d-%m-%Y"`: `docs new spec a` writes `Updated: 26-10-2026`; the next `docs index` exits 2 (`Updated: malformed date '26-10-2026' (expected %Y-%m-%d)`); `docs touch a.md` writes, then exits 2 the same way; `docs check` exit 0. | The same config-blindness, in the date half — wider than the 2026-08-15 entry recorded (it named `docs archive`). Bears on whether Q7 fixes both halves. | Q7 |
| **E9** | `docs relate add a.md precedes coverage.xml` exits 1 (`coverage.xml: missing H1`); a hand-written `- references: coverage.xml` passes `docs check` at exit 0. | `relate` parses both endpoints because both are written for a recognized pair; a free-form TARGET is never written, and the convention and the bundled skill's quality-artifact guidance allow non-Markdown targets. | D5, Q6 |
| **E10** | Three pre-existing ids pin the free-form refusal: `test_relate_unknown_verb_refuses`, `test_relate_quiet_suppresses_success_but_never_a_refusal` (both `pairs-with`), `test_relate_case_variant_verb_refuses` (`Precedes`). `test_every_named_verb_is_a_real_subcommand` derives the real verb set from the parser, so registering `lifecycle` without the skill naming it fails the suite. Archive candidates come from `_CASCADE_VERBS = ("pairs-with", "child-of")` over parsed `Doc.related`. | The behaviour change is visible in exactly three ids; the parity gate self-enforces; archive invariance reduces to byte-identity of the written bullet. | D4, D7, D9 |
| **E11** | *Measured 2026-10-27, after the operator's Q7 answer.* A tree created with the default format, whose sidecar is then switched to `[archive] date_format = "%d-%m-%Y"` while its document keeps `Updated: 2026-10-27`: `docs check` reports `bad-date` (`expected %d-%m-%Y`) at exit 2; `docs index` exits 0. No committed fixture sidecar sets a non-default `date_format`. `Config.__post_init__` refuses a vocabulary that is not a superset of the built-ins. `test_archive_renders_the_witness_in_the_trees_date_format` pins today's exit-2 tail on purpose, and its docstring names its successor: "a later milestone that FIXES E8 will break this test, deliberately — its expected exit code becomes 0". | Bounds D10's date-half change to a tree that already fails `docs check`; the vocabulary half only widens what parses — so no check-clean tree starts failing. **Corrected by the Step 0 review (claude-S1):** the shape *does* appear in this repository's tests — `tests/test_cli_mv.py`'s `_attic_tree` writes ISO `Updated:` lines on a `%d-%m-%Y` tree — so it and the archive test are corrected in the same change, both listed in the task plan's *Pre-existing tests that change*. | D10, Q7 |
| **E12** | *Step 0 review, claude-B2; reproduced by the conductor and here (2026-10-27).* Tree with `add_lifecycles = ["shipped"]`; a `docs check`-clean `a.md` at `Lifecycle: shipped`, `Role: spec`, `Related: - pairs-with: b.md`. `docs stamp a.md` exits 0 (`stamped a.md`) and rewrites it to `Lifecycle: draft`, `Role: notes`, `Updated: 2026-10-27`, moving the group into `## Migrated metadata` as `Migrated-Related:`; `docs list --json` then shows `a.md draft notes []` and `docs check` still exits 0. With a `precedes` pair written by `docs relate`, the same stamp leaves `b.md`'s `follows: a.md` dangling and `docs check` exits 2 (`missing-inverse`). On a default tree, `Lifecycle: activ` is re-stamped to `draft` and its `Project: t` replaced by the root's. | 2.0.0 data loss on a check-clean document. D10's config-aware `parse()` fixes the extension case; operator Packet A turns every remaining full-block failure into a zero-byte refusal (exit 1). | D10, B2 |
| **E13** | *Step 0 review, gpt-B1 and claude-B1 independently; reproduced here.* `render_index` (`src/docs_cli/cli.py`, `role_order = ["status"] + [r for r in CANONICAL_ROLE_ORDER if r != "status"]`) renders only roles in that list. A direct probe — `parse()` of a `spec` document plus the same document with its role replaced by the configured extension `adr`, rendered under `add_roles = ["adr"]` — produces `_Generated 2026-10-27. 2 docs active, 0 archived._` and a body containing only `spec.md`; `adr.md rendered: False`. `docs list`'s grouping has no such list. | Masked today by E7; D10 would expose it as a silent INDEX omission. Fixed by naming `render_index` in D10 with a frozen placement: extension-role groups after the built-in order, alphabetical, no new `Config` field. | D10, B1 |

### Verification

- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 48 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues found in 49 source files.
- `.venv/bin/python -m pytest -q` — 1504 passed (before and after the setup
  edits; the INDEX snapshot refreshed).
- `docs check .` from the docs root — no violations found (exit 0).
- `docs check . --stale 14` — exit 1, nine `stale` warnings on evergreen
  active documents untouched since 2026-05 to 2026-08 (`architecture.md`,
  `charter.md`, `cli.md`, `convention.md`, `definition-of-ready.md`,
  `dual-status-adr.md`, `release-runbook.md`, `test-strategy.md`,
  `vocab-adr.md`); reviewed — pre-existing, and bumping their `Updated:`
  without a content change would falsify it.

### Decisions / issues

- **One registered binding clause could not hold as written (E7, A1).** A
  document in an `add_lifecycles` state already breaks `docs index`, every
  reindexing verb, `docs list`, `docs relate`, `docs archive` and `docs mv`,
  while `docs check` stays clean. The cause is `parse()` validating against
  built-ins rather than the tree's config — the same function that parses
  `Updated:` with the ISO default (E8). Surfaced as **Q7**; the operator chose
  **(A)** on 2026-10-27, so the clause stands and **D10** — `parse()` honours
  the configured vocabulary and `date_format` at every call site — is a new
  binding decision with its own deliverable, clauses C20–C22 and locks. E11,
  measured after the answer, bounds the date half's changed outcome to a tree
  that already fails `docs check` (the Step 0 review later added the two
  outcomes E12 and E13 name). Both feedback entries now name this milestone.
- **The registered verb-syntax recommendation did not pin a grammar (E4,
  A2).** `docs check` accepts anything before the first colon. Surfaced as
  **Q3**; the operator chose **(c)**, the lowercase kebab token
  `[a-z][a-z0-9-]*` (**D6**): every measured verb is inside it, case variants
  and every other out-of-grammar verb refuse at exit 2 with zero bytes
  written, and widening it later is recorded as additive.
- **The `--body-from` question was answered in M8 (E6, A3).** Resolved as
  **Q5**: supported, locked by a new test, stated in `cli.md`. The generic leak
  (a forged `Revision:` group lands on an active document) is follow-up item 1,
  not fixed here.
- **The free-form path must not reuse the archived-endpoint branch blindly.**
  `_cmd_relate` requires `--reason` and `_plan_relate_edit` appends `Revision:`
  for any archived endpoint; D5 refuses an archived SOURCE in the
  validate-all-first pass and never requires `--reason` for an archived TARGET
  that is not written.
- **`docs project set` is the lifecycle verb's template**, not `docs touch`:
  its `*docs, <value>` split, two-token minimum, archived-batch refusal, no-op
  and single reindex are exactly D1–D3 (**Q1**).
- **The release vehicle follows the single-milestone pattern (Q4).** Bump to
  2.1.0 here, publish in a separate milestone not yet in the tracker.
- **The stopgap criterion is discharged by hand-off (Q9).** Both verbs, both
  suite probes locked, and a hand-off note in a live home; the retirement
  itself is verified in the suite release that pins this version.
- **Risk is Standard (Q8)** — proposed at setup because no earlier milestone
  in this project recorded a level except M16 (Lite), and confirmed by the
  operator on 2026-10-27 with D10 in scope.
- Host-machine skills are **not** touched by this milestone (`CLAUDE.md`):
  they refresh at the production ship. The bundled skill updates in Phase 7.
- **No OPEN QUESTIONS remain.** Q3, Q7 and Q8 went to the operator with
  decision packets and were answered on 2026-10-27, each as recommended; the
  milestone doc's *Setup questions* carries the full reasoning and the
  resolutions.

### Setup questions — summary

Full reasoning in the milestone doc's *Setup questions (Q1–Q9)*.

| # | Question | Resolution |
|---|---|---|
| Q1 | Verb shape *(stub Open question 1)* | **RESOLVED (conductor, as recommended) → D1.** Flat `docs lifecycle <file>... <state>` with `docs project set`'s `*docs, <value>` grammar and batch semantics; no namespace, no `--date`. |
| Q2 | Free-form edge with an archived SOURCE *(stub Open question 2)* | **RESOLVED (conductor, as recommended) → D5.** Refused in the validate-all-first pass, even for a no-op; M25 — D4 stays recognized-only; an archived TARGET is never written and needs no `--reason`. |
| Q3 | Free-form verb syntax *(stub Open question 3)* | **RESOLVED (operator, 2026-10-27) → D6.** Option (c), as recommended: `[a-z][a-z0-9-]*`; case variants and every out-of-grammar verb refuse at exit 2 with zero bytes written; widening later is additive. |
| Q4 | Release vehicle *(stub Open question 4)* | **RESOLVED (conductor, as recommended) → D9.** 2.1.0, bumped here with an `UNRELEASED` section (M19/M21/M23 pattern); separate publish milestone. |
| Q5 | `--body-from` leading `Related:` — supported or accident? *(feedback observation)* | **RESOLVED (conductor) → D8.** Supported and documented since M8; locked and stated in `cli.md`; the generic leak is a follow-up. |
| Q6 | Must a free-form TARGET parse? | **RESOLVED (conductor) → D5.** No — any existing file under the root, the `broken-ref` test. |
| Q7 | Extension states versus `parse()`'s config-blindness | **RESOLVED (operator, 2026-10-27) → D10.** Option (A), as recommended: both halves fixed in M30 — vocabulary extensions and `date_format` honoured at every `parse()` call site; no check-clean tree starts failing (E11); both feedback entries owned here. |
| Q8 | Risk level | **RESOLVED (operator, 2026-10-27).** Standard, as proposed. |
| Q9 | Discharging the stopgap success criterion | **RESOLVED (conductor) → D9.** By hand-off at closeout, from the stub's own deliverable and TDD summary; retirement verified in the suite release. |

### Finalization — 2026-10-27

The operator answered the three open setup questions through the conductor,
each as recommended: **Q3 → (c)**, the lowercase kebab token
`[a-z][a-z0-9-]*`, with widening later recorded as additive; **Q7 → (A)**,
fix both halves of `parse()`'s config-blindness inside M30 as an explicit
deliverable and contract clauses, with no tree that passes today allowed to
start failing, and both config-blindness feedback entries owned by this
milestone; **Q8 → Standard**, confirmed. The conductor-resolved Q1, Q2, Q4, Q5,
Q6 and Q9 stand as recorded; on Q4 the operator did not register the 2.1.0
publish milestone in this run, so it stays a recorded follow-up and hand-off,
and no tracker row was added.

- Folded the answers into the task plan: *Overview*, *Risk Level*, D2, D6, a
  new **D10**, the D9 upgrade note (two behaviour changes), *Contract*,
  *Out of scope*, E11 and its structural risk, the evidence table, *Test
  Strategy*, *Deliverables*, Phases 1–9, A1 and A2, the Q3 / Q7 / Q8
  resolutions, follow-ups 3 and 4, and the success criteria.
- Measured **E11** on a throwaway tree to bound D10's behaviour change, and
  found the one pre-existing test that pins today's date-format defect on
  purpose (`test_archive_renders_the_witness_in_the_trees_date_format`); it is
  listed in the task plan's *Pre-existing tests that change*, the one
  authoritative list the Step 0 review introduced.
- Updated the test matrix: risk confirmed, C4 and C12 settled, C20–C22 added
  for D10, the date-format row, a seventh mutation target.
- Updated `feedback-log.md`: the 2026-08-15 `date_format` entry and the
  2026-10-26 vocabulary entry now name this milestone as owner.
- Re-verified the tracker row (`active`, order 100, no dependencies, Notes and
  slug unchanged, link to this milestone's task plan) and the derived
  relationships: one row, no adjacent cohort, no dependency — the desired
  recognized edge set is still empty and no recognized edge touches the three
  artifacts, so no `docs relate` operation was needed.
- Updated the `status.md` narrative, `docs touch`ed every edited document
  (the clock had rolled to 2026-10-27; `Updated:` was never hand-edited),
  regenerated the INDEX with `docs index .`, and refreshed the frozen snapshot
  `tests/fixtures/expected/docs-INDEX.md`.

Verification after finalization:

- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 48 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues found in 49 source files.
- `.venv/bin/python -m pytest -q` — 1504 passed.
- `docs check .` from the docs root — no violations found (exit 0).
- `docs check . --stale 14` — exit 1, the same nine pre-existing `stale`
  warnings on evergreen documents, reviewed.

## Step 0 review-pass-001

- Pass id: `Step 0 review-pass-001`.
- Ledger location: `lifecycle-and-free-form-relate-impl.md#step-0-review-pass-001`
  (docs root `/home/user/opt/docs-cli/docs`; repository path
  `docs/lifecycle-and-free-form-relate-impl.md#step-0-review-pass-001`).
- Predecessor: none — the first entry in this milestone's review sequence.
- Status: `closed` — both provider attempts are terminal, every finding is
  dispositioned with evidence, the required targeted re-review is complete,
  and `final-sync` is `ready`.
- Frozen packet: slug `lifecycle-and-free-form-relate`; step 0; branch
  `lifecycle-and-free-form-relate/milestone-setup`; base
  `2ad941e269339f5a125856f5bcda9339cd9f5b15` (the claim checkpoint);
  review HEAD `f8ec7f0a4d3a444265dff43ec9ef9793b3f35c20`
  (`lifecycle-and-free-form-relate(setup): expand M30 into a full plan, open
  its log and test matrix`); project `docs`; project path `""`; artifact stem
  `lifecycle-and-free-form-relate`; tracker `docs/milestone-plan.md` row
  `100 | lifecycle-and-free-form-relate | active | —`; claim checkpoint
  `2ad941e`; branch root `lifecycle-and-free-form-relate/`; risk Standard;
  checks at the review HEAD: `ruff check`, `ruff format --check`, `mypy`,
  pytest 1504 passed, `docs check` exit 0. Both reviewers received the
  identical provider-neutral prompt (the Step 0 test-quality clause),
  isolated from each other.
- Tracker: `milestone-plan.md` in the docs root; owning project `docs`;
  project path empty (dedicated docs root); artifact stem
  `lifecycle-and-free-form-relate`; active semantic slug
  `lifecycle-and-free-form-relate`; claim checkpoint `2ad941e`; semantic
  branch root `lifecycle-and-free-form-relate/`.
- Claude slot: `returned` — Anthropic Claude family, Claude Opus 5.5
  (`claude-opus-5-5`), host-reported; run as a fresh Claude Code sub-agent at
  xhigh effort.
- GPT slot: `returned` — OpenAI GPT family; Codex CLI 0.160.0, `codex exec -m
  gpt-6-astra -c model_reasoning_effort=xhigh -s read-only`; the Codex session
  log reports `model: gpt-6-astra` (the reviewer self-reported "GPT-6
  (Codex)").

**Findings and dispositions.**

Source finding ids are the reviewers' own; gpt-B1 and claude-B1 are one
defect found independently. **Correcting commit** for every row below except
claude-RR-B1: `3fed1f6d6d02303cfbcac267e88b806898789a27` (`lifecycle-and-free-form-relate(setup): resolve Step 0
review-pass-001 findings`). claude-RR-B1, raised by the targeted re-review, is
fixed in the `sync-and-commit` commit that closes this pass; a commit cannot
carry its own hash, so its evidence below is the changed artifacts.

| Id | Severity | Disposition | Evidence |
|---|---|---|---|
| gpt-B1 / claude-B1 | blocker | **fixed** in `3fed1f6d6d02303cfbcac267e88b806898789a27`; re-review: resolved | `render_index` builds its role order from `CANONICAL_ROLE_ORDER` only, so an extension-role document a config-aware `parse()` admits would be counted and not rendered — reproduced here (E13). The task plan's D10 now names `render_index` beside the seven `parse()` call sites with a **frozen** placement (extension-role groups after the built-in order, alphabetical, no new `Config` field; Phase 1 may not re-open D10); evidence E13 added to the plan and this log; D10's footprint estimate (+60 to +110 lines) and taste anchors revised; matrix clause C25, crosswalk row, mutation target 10; the C20/C25 index lock `test_index_renders_an_extension_role_group_after_the_built_in_roles` asserts the entry is **rendered** under `### Active — Adr` after every built-in group with the summary count equal to rendered entries, plus the pure `test_render_index_orders_extension_roles_alphabetically_after_built_ins`. |
| claude-B2 | blocker | **fixed** (operator decision, Packet A) in `3fed1f6d6d02303cfbcac267e88b806898789a27`; re-review: resolved in substance | On 2.0.0 `docs stamp` destructively re-stamps a valid extension-state document — reproduced here three ways (E12). D10 gains the stamp clause: a full block failing the configured vocabulary or date format refuses with zero bytes written, exit 1, naming the field and pointing at `docs check` / `docs touch`, accepting that a typo'd lifecycle on a default tree is refused too; a configured extension state is "already stamped". Evidence E12; matrix clause C24 with byte-level zero-write locks in `tests/test_cli_stamp.py` for the extension-vocabulary tree and the E11 date shape; mutation target 11; the "only behaviour change D10 makes" claim, the D9 upgrade note (now three changes), the Risk Level wording and the Phase 7 `cli.md` `docs stamp` idempotence paragraph corrected or scheduled; a dated bullet on the M30-owned vocabulary entry in `feedback-log.md`. Risk stays Standard. |
| claude-S1 (+ gpt-N1) | should-fix | **fixed** in `3fed1f6d6d02303cfbcac267e88b806898789a27` | One authoritative old → new list, *Test Strategy* › *Pre-existing tests that change*, replaces every "four named edits" count in the plan, the matrix and this log: the three `relate` refusal ids (one renamed), the archive date-format test (correctly formatted success input; malformed-date behaviour moved to a new refusal test — gpt-N1), the `_attic_tree` correction covering two `test_cli_mv.py` ids, and the four 2.1.0 packaging pins (two renamed). Phases 4 and 8 gate on the explicit mapping; `tests/test_cli_mv.py` added to Phases 2–3 and the matrix; E11 reworded. |
| claude-S2 | should-fix | **fixed** | The skill's sidecar examples use the inline `Related: artifact-of: x` form, which `--body-from` does not parse as metadata — reproduced (E6 row). E6, A3, D8 and Q5 corrected; Phase 7 rewrites both lines to the group form or `docs relate add <sidecar> artifact-of <binary>`; C14 now locks the skill's literal example and the inline form's body-text reading. |
| claude-S3 | should-fix | **fixed** (conductor-resolved, Packet C) | D2: `docs lifecycle` refuses, exit 2 and zero bytes, a source whose current `Lifecycle:` is `archived` wherever it sits, naming the `status-drift` and `docs archive`; matrix C23, visible test `test_lifecycle_refuses_an_active_tree_document_already_marked_archived`, mutation target 3, an error-table row and an acceptance example. |
| claude-S4 | should-fix | **fixed** | Planned visible tests added: TARGET outside the root, a directory, missing, and a symlink escaping the root; the `docs lifecycle` INDEX-refresh-failure tail; its strict-root refusal; an archived document mixed into a batch (moved from the hidden categories to a visible test). |
| gpt-S1 | should-fix | **fixed** | The write-footprint invariant now counts editable documents separately from the generated INDEX — zero writes for a no-op or `--dry-run`, one INDEX refresh after a real change — in the plan's acceptance flow and examples, property list, risk gates and success criteria, and the matrix's C5, C6, rows and property list. |
| gpt-S2 | should-fix | **fixed** | Add-then-remove byte restoration is conditioned on an initially absent edge, with or without an existing `Related:` group; from an arbitrary initial state the assertion is the contractual edge set plus preservation of unrelated content. |
| gpt-S3 | should-fix | **fixed** | The fuzz generates valid and invalid categories independently from D6's grammar (valid must succeed and round-trip; invalid must refuse with zero writes), including newlines, non-ASCII letters and digits, and trailing and doubled hyphens; mutation targets `re.fullmatch` versus `re.match` + `$` and `[0-9]` versus `\d` added; "reindexes exactly once" reworded as no reindex on a no-op through a sentinel INDEX, with the refreshed INDEX reflecting the final state. |
| claude-N1 | nit | **fixed** | C13 / D7 evidence row scoped to the written bullet line, the parsed `Related:` list, the candidate JSON and the strand refusal; full-file identity only for the `archive-neighborhood` copy, with `relate` run under `--date`. |
| claude-N2 | nit | **fixed** | `docs project rename` added to D10's lock list, the evidence row, C20 and the Phase 2 files. |
| claude-N3 | nit | **fixed** | D6 and the Phase 1 freeze items now name argparse's leading-hyphen behaviour (and any `--` pass-through) as a message-catalogue item. |
| claude-N4 | nit | **fixed** | D5, Q6 and C10 say "`broken-ref`'s existence test plus containment". |
| claude-N5 | nit | **fixed** | D4, C7 and a success criterion qualify "byte-for-byte unchanged": on extension-vocabulary or non-default-date trees D10 turns 2.0.0's exit-1 endpoint refusal into success. |
| claude-N6 | nit | **fixed** | The planned test is renamed `test_relate_recognized_pair_still_writes_both_halves_unchanged`, without release provenance. |
| claude-N7 | nit | **fixed** | D10 now says C20–C22, C24 and C25 are test-matrix clause ids. |
| claude-N8 | nit | **fixed** | The phase-progress sentence is removed from `status.md`; phase lives in this log. |
| claude-N9 | nit | **fixed** | In `feedback-log.md`'s 2026-08-15 `date_format` entry, `Status:` is the last bullet again; the new stamp bullet on the vocabulary entry is placed before its `Status:`. |
| claude-N10 | nit | **fixed** | The Phase 7 stale-wording grep covers the output of `docs relate --help`, `docs relate add --help` and `docs relate remove --help`, and adds "Only the six recognized verbs". |
| claude-RR-B1 | blocker (raised by the targeted re-review) | **fixed** in the `sync-and-commit` commit that closes this pass | The B2 stamp refusal breaks the pre-existing `tests/test_cli_stamp.py::test_stamp_supersedes_invalid_existing_block` (fixture `tests/fixtures/stamp/raw-invalid-block.md`: a full block with `Role: not-a-real-role` on a default tree), which the authoritative list omitted; the reviewer's D10 + stamp simulation gave 3 failed / 1501 passed (two listed, this one unlisted). Confirmed by reading the test and fixture. Fix: a row in the plan's *Test Strategy* › *Pre-existing tests that change* renames it to `test_stamp_refuses_a_full_block_with_an_invalid_role_with_zero_bytes`, expecting exit 1, zero bytes written and `Role:` named (reason: D10 / Packet A / E12); the list's renamed-row count, D10's stamp clause, the E12 evidence row and Phase 3's file list (fixture prose updated in Phase 2/3) reference it; the matrix moves the default-tree invalid-vocabulary case from the hidden column into C24's visible locks. The conductor's non-blocking note is recorded in D10 and C24: a full block failing `parse()` for a reason unrelated to the configured vocabulary or date format keeps today's stamping. |
| claude-N11 | nit | **waived** | Adding `parent-of: lifecycle-and-free-form-relate.md` to `milestone-plan.md` is a free-form hand-edit to a document outside the operator-approved set (this milestone's own three artifacts) and is not required by the tracker contract — the milestone's `child-of: milestone-plan.md` already gives navigation. Recorded as the plan's *Follow-ups* item 6; the waiver lifts once free-form `docs relate` exists. |

**Taste triage.**

- GPT: approach judged sound; no subjective findings.
- claude-T1 (the story retold in about eight places; the "four edits" count
  in seven): **partially fixed** by claude-S1's single authoritative list;
  the remainder **waived** (Standard risk, conductor authority) — the M28a
  precedent records evidence in plan, log and feedback log by design, and one
  authoritative list per drift-prone count is the fix that matters.
- claude-T2 (the 27-line *Overview* progress bullet): **fixed** — the
  narrative moved to this log's *Implementation metadata*; the plan keeps a
  one-line pointer.
- claude-T3 (no D-id ↔ C-id crosswalk): **fixed** — the test matrix gains a
  *Decision ↔ clause crosswalk*, linked from the plan's *Binding scope* and
  *Test Matrix* sections.
- Patch bloat: both reviewers judged it in line with precedent; no action.

**Re-review.**

**Required** (conductor decision): B1's fix changes D10's binding contract,
and B2 adds a new operator-decided clause, so the correction could not be
proved objectively by the checks alone. **Complete.**

- Packet: correcting commit `3fed1f6d6d02303cfbcac267e88b806898789a27` against the reviewed HEAD
  `f8ec7f0a4d3a444265dff43ec9ef9793b3f35c20`, each reviewer re-checking only
  its own blockers, inside this review-pass-001. Line references below are to
  the documents at `3fed1f6d6d02303cfbcac267e88b806898789a27`.
- GPT reviewer — Codex CLI, model `gpt-6-astra` per the session log
  (self-reported "GPT-6, exact variant not exposed"): **gpt-B1 resolved**
  (plan :425, :659, :676; log :393; matrix :104). New blockers introduced:
  none.
- Claude reviewer — the same Claude Opus 5.5 sub-agent (`claude-opus-5-5`):
  **claude-B1 resolved** (plan :425–433; matrix C25 :70, row :104, mutation
  target 10 :192); **claude-B2 resolved in substance** (plan :434–444,
  :453–459, :378–387; matrix C24 :69, row :106, mutation target 11). It
  raised **one new blocker introduced by the correction, claude-RR-B1** —
  dispositioned `fixed` above — and a non-blocking note, conductor-resolved
  and recorded in D10: a full block failing `parse()` for an unrelated reason
  keeps today's stamp behaviour.
- Re-review of claude-RR-B1's fix: **not required** (conductor decision) — the
  correction is objectively verifiable: one named row in the authoritative
  list plus a matrix row move, checkable by inspection and by the Phase 4/8
  mechanical old → new id-mapping gate; it changes neither the contract nor
  the approach.

**Closure check.** Predecessor chain: this is the first entry in the
sequence (predecessor none), and no earlier entry or frozen packet exists to
alter. One frozen packet is named (base `2ad941e…`, review HEAD `f8ec7f0…`).
Both provider slots are terminal and both returned, from different families,
with host-reported identities. Every reviewer-labeled blocker — gpt-B1 /
claude-B1, claude-B2, claude-RR-B1 — has a completed disposition with
evidence. Every taste finding is fixed or waived with a reason. The required
re-review is complete with packet, reviewers and result.

**Verification report (sync-and-commit, ship-milestone Step 0).**

- Risk level: Standard (operator-confirmed).
- Fast gate commands run: `.venv/bin/ruff check .`; `.venv/bin/ruff format
  --check .`; `.venv/bin/mypy src/ tests/`; `.venv/bin/python -m pytest -q`;
  from the docs root `docs index .`, `docs check .` and `docs check . --stale
  14`; `docs/INDEX.md` compared with `tests/fixtures/expected/docs-INDEX.md`.
- Deep gate commands run: none — Step 0 changes documentation only.
- Deferred / not configured gates: coverage, hidden suite and mutation tooling
  are not configured in this project; property/stateful, fuzz and the
  hand-applied mutation smoke are planned for Phases 2–8 and have no code to
  run against at Step 0.
- Visible test result: GREEN — 1504 passed, the expected state for a
  documentation-only step.
- Hidden/generalization, coverage, mutation, property/stateful, fuzz,
  benchmark/security/schema/migration: not applicable at Step 0 (no product
  code changed).
- Mock audit: no mocks added.
- Taste triage: complete — fixed or waived with reasons, none untriaged.
- Ship-milestone Step 0 review ledger: this pass, closed; `final-sync` ready.
- Semantic tracker row / branch identity: `milestone-plan.md` row `100 |
  lifecycle-and-free-form-relate | active | — |` with its Notes unchanged;
  project `docs`, project path empty, artifact stem
  `lifecycle-and-free-form-relate`, task plan / log / matrix at the three
  derived paths, branch `lifecycle-and-free-form-relate/milestone-setup` under
  root `lifecycle-and-free-form-relate/`; no recognized relationship applies;
  `status.md` links the tracker without copying rows or naming next work.
- Contract/test matrix status: current, with C1–C25 and the decision ↔ clause
  crosswalk.
- Docs check: exit 0; `--stale 14` exit 1 with the nine pre-existing
  evergreen-document stale warnings, reviewed.
- Diff scope: the milestone's task plan, implementation log and test matrix,
  plus the regenerated INDEX if it changes — documentation only.
- Operator approvals: Q3, Q7, Q8 and Packet A, as recorded above.
- High-risk RED-baseline approval: not applicable (Standard).
- Remaining risks: none open at Step 0.

- final-sync: `ready`.

## Phase 1 — Define Contract — 2026-10-27

### Objective

Freeze, against the answered Q1–Q9, operator Packet A and the Step 1
planning pass's fifteen open questions (all conductor-resolved), everything
Phase 2 will assert against: `docs lifecycle`'s grammar, path rule, refusal
order, message catalogue (L1–L12), success lines, `--json` record, edits and
write strategy; free-form `relate`'s grammar, check order, messages (R1–R3),
`TARGET` rule, archived-endpoint rules and record; the `--body-from`
sentence and the skill's two sidecar examples with their extraction
contract; D10's `parse()` signature and how each call site obtains its
config; the `docs stamp` refusal's classification and message; the upgrade
note; the full surface list; and the Phase-5 signatures. **No product code
and no test changes** — the M25–M28a precedent.

### Working contract, restated before any code

- **Invariants.** No transition into or out of `archived` through
  `docs lifecycle` (an `archived` target, a source under the archive subtree,
  and a source already reading `Lifecycle: archived` all refuse); a free-form
  `relate` writes `SOURCE` alone and never reads or writes `TARGET`, and
  never writes an archived document; recognized-verb `relate` and the archive
  candidate set and strand refusal are byte-for-byte unchanged on every tree
  `docs check` passes; a no-op or `--dry-run` writes nothing, INDEX included,
  and a real change refreshes the INDEX once; every refusal is zero-byte and
  prints under `--quiet`; `docs check`'s rules, findings and records are
  unchanged; a bare `parse()` keeps the built-in defaults and a
  config-aware one agrees with `docs check`, with unchanged messages and one
  date spelling per tree; `render_index` renders every document it counts;
  `docs stamp` never destroys a document.
- **Forbidden shortcuts.** No special-casing of visible examples
  (`pairs-with`, fixture names, test literals) or test-only branches — the
  free-form path is the grammar, not a list; no weakening, skipping,
  deleting or rewriting of tests to obtain GREEN, and pre-existing test edits
  limited to the authoritative list; `docs lifecycle` never re-enters another
  verb's command function and no spelling reaches `archived`; a free-form
  operation never writes `TARGET`; `docs check` is never relaxed; no new
  dependency and no hand-rolled equivalent of an in-project library without a
  logged decision; green visible tests are not sufficient on their own where
  the risk level selects deeper gates.
- **Visible product tests that drive the implementation.** The Phase 2 set:
  the new `tests/test_cli_lifecycle.py` and `tests/test_lifecycle_plan.py`,
  and additions to the `relate`, relate-plan, `archive`, `--body-from`,
  `stamp`, index (pure and CLI), `list`, `touch`, walker, `project set`,
  `project rename`, `mv`, model and skill test modules — plus the
  pre-existing tests on the authoritative list.
- **Explicit non-product workflow gates.** `docs check .` from the docs root;
  the live-INDEX snapshot comparison; the Phase 4 / Phase 8 mechanical id and
  AST-diff proof; the naming lint over new test names; the Phase 8 mutation
  smoke.
- **Risk and gates.** Standard (operator, Q8). Selected: contract; visible
  product tests; `ruff check`, `ruff format --check`, `mypy src/ tests/`;
  `docs check`; reference byte-identity; the live-INDEX snapshot;
  property/stateful smoke; mock audit; the end-of-step reviews. Coverage,
  hidden suite and mutation tooling are not configured. No Phase-4 operator
  checkpoint.
- **Mock policy.** No new mocks: the INDEX-refresh failure uses a real
  malformed sibling, the no-reindex check a sentinel INDEX, and the fuzz runs
  through in-process `cli.main` (a real path). Phase 8 audits.
- **Taste anchors.** `_cmd_project_set` (lifecycle), `_cmd_relate` /
  `plan_relate` / `_plan_relate_edit` / `relate_plan_to_json` /
  `_print_relate_lines` (free-form), `_cmd_touch` (write-and-reindex tail),
  `check_doc` (the `parse()` fix), `render_index` extended rather than
  replaced, `_cmd_stamp`'s validate-all-first abort; reuse
  `set_metadata_field`, `add_related_edge` / `remove_related_edge`,
  `atomic_write`, `_refresh_index` + `compile_exclude_predicate`,
  `_resolve_managed_root`, `_resolve_relate_endpoint`, `_is_archived_rel`,
  `validate_lifecycle` / `validate_role`, `inverse_verb`, `load_config`,
  `parse_date`, `RelatePlan` / `RelateEdit`; the `docs: <verb>:` voice,
  validate-all-first, one JSON shape for preview and apply, frozen dataclass
  plans; `cli.py` +310 to +510 lines, tests +900 to +1,300; stdlib only.

### Actions taken

- Wrote **Decisions (Phase 1 — BINDING)** in the task plan: P1.1
  `docs lifecycle` (argparse, paths, an eleven-step refusal order, the
  L1–L12 catalogue, success lines, the record, edits, sequential writes,
  deduplication); P1.2 free-form `relate` (the grammar, an eleven-step check
  order, R1–R3, the never-read `TARGET`, archived endpoints, the record, byte
  stability in both D10 directions); P1.3 the `--body-from` route plus the
  **frozen** Phase-7 text of both skill sidecar examples and the extraction
  contract the C14 test follows; P1.4 the `parse()` signature and the
  per-site config table; P1.5 the stamp classification and message; P1.6
  `render_index`; P1.7 the upgrade note; P1.8 the full surface list; P1.9
  the Phase-5 signatures and the pull-style interface map; the fifteen
  resolved questions; and three logged deviations.
- Landed the author-facing halves in `docs/cli.md`: *Invocation* gains the
  configured-vocabulary-and-date-format paragraph (D10, every verb that
  reads metadata); `docs new`'s `--body-from` gains the leading-`Related:`
  bullet (D8); `docs index` gains the extension-role placement and its real
  exit codes (OQ-10 — it said "Exits 0 always", but it exits 1 on a missing
  root and 2 on a malformed `.docs.toml` or document); a new **`docs
  lifecycle`** section carries every catalogue message, the record and the
  exits; `docs relate` is rewritten for the two kinds of verb — intro, the
  free-form grammar with R1 and R3, *What must parse*, *What gets written*,
  idempotency, *Archived endpoints* with R2, the record table and a
  free-form example, stage 1 and 2 of the coordinated-write contract,
  *Exits* and *Non-goals*; `docs stamp` gains the refusal and its exit row,
  its "four required fields" becomes three plus `Project:` (OQ-10), and its
  exit 2 now names the INDEX-refresh failure the code already returned; the
  exit-code summary gains a `lifecycle` row and updated `relate` / `stamp`
  rows; the cross-verb convention names `lifecycle`.
- Landed the convention halves in `docs/convention.md`: `Updated:`'s type is
  the tree's `date_format`; *Changing lifecycle* under the Lifecycle table;
  *Every verb honours the additions* under *Extending vocabularies*;
  *Writing an edge* under *Relationship verbs* (the grammar binds `relate`,
  not the convention); the reciprocal *Repair with `docs relate`* paragraph;
  the active-tree lifecycle rule now names `add_lifecycles` extensions (what
  `status-drift` already accepts) and `date_format` governs every `Updated:`
  in every verb; the audited-repair exception is stated recognized-only; the
  *What `docs` does not promise* graph line names one edge per invocation.
- Applied the task plan's wording fixes, none re-opening D10: the duplicate
  `## Contract` heading removed; D4 (and the matrix's C7) gain the E11
  direction and the D9 upgrade note says "every verb that reads metadata"
  (OQ-6); the error table says "the same message `docs check` gives"
  (OQ-6); the Phase 2 objective's locks corrected (OQ-9) and
  `tests/test_lifecycle_plan.py` added to its files (OQ-12); Phase 7 gains
  `references/quality-artifacts.md` and `SKILL.md`'s *Quality artifacts*
  paragraph (OQ-14); *Ambiguities* points at the frozen items; *Non-product
  checks* names the QUALITY PLAN's explicit gates; the authoritative list's
  three `relate` rows name their exact verbs; *Follow-ups* gains items 7 and
  8 and records homes for 2, 3 and 6 (OQ-5, OQ-11).
- Aligned the test matrix: clauses cite the catalogue ids (`L1`–`L12`,
  `R1`–`R3`), deduplication (OQ-3) and the closed record keys; *Check
  classification* lists the explicit non-product gates.
- Mirrored both specs byte-identically into `src/docs_cli/skill/references/`
  and regenerated `docs/INDEX.md` and its frozen snapshot after `docs touch`.

### Contract decisions worth calling out

- **The archive-subtree pre-pass runs before every per-document check, and
  the status-drift guard after.** L7 is decidable from paths alone, so — as
  in `project set` — a batch naming an archived document refuses at exit 2
  even when another named document is missing; L11 needs a parsed
  `Lifecycle:`, so it can only run once every document has parsed, and a
  missing sibling therefore exits 1 first. Either way nothing is written.
- **`archived` is tested before membership.** It is a member of
  `config.lifecycles`, so a membership-only test would let it through; L5
  names `docs archive` rather than listing it as merely unknown.
- **A leading-hyphen verb is argparse's, frozen loosely.** Measured on
  Python 3.12.3: `relate add a.md -x b.md` and `-1x` exit 2 with argparse's
  *the following arguments are required: TARGET*; after `--` (in either
  position) or as a bare `-`, the verb reaches the command. R3 freezes
  "exit 2, usage error, zero bytes" and leaves argparse's wording free.
- **The free-form record keeps all eleven keys.** `inverse: null` and a
  one-element `edits` let a consumer read both kinds of record with one
  parser; `_print_relate_lines` needs no change because it already iterates
  the edits.
- **The skill's sidecar wording is frozen now, not in Phase 7.** C14 runs
  "the skill's literal example", so the example a Phase 2 test extracts has
  to exist as frozen text before the test is written (OQ-7).

### Verification

- `git diff e48adb9 -- src/docs_cli/cli.py tests/` — empty except the
  regenerated `tests/fixtures/expected/docs-INDEX.md` snapshot.
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 48 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues found in 49 source files.
- `.venv/bin/python -m pytest -q` — **1504 passed** (unchanged).
- `docs check .` from the docs root — no violations found (exit 0).
- `cmp` of both mirrors against `docs/cli.md` / `docs/convention.md`, and
  of `docs/INDEX.md` against the frozen snapshot — identical.

## Phase 2 — Write Tests (RED) — 2026-10-27

### Objective

Express every clause of the frozen contract as a test before any
implementation, with RED tests for the missing behaviour, GREEN-at-baseline
locks for the behaviour that must survive, and the pre-existing tests edited
exactly as the task plan's authoritative list says — no more.

### Actions taken

- **184 new test ids** across two new and fourteen existing modules (the
  matrix's *Visible tests* has the per-module counts and names), plus the
  four renamed ids on the authoritative list.
- `tests/test_cli_lifecycle.py` (new, 32 ids) and `tests/test_lifecycle_plan.py`
  (new, 10 ids): every L-catalogue message asserted verbatim; every write
  asserted on bytes through a `_promoted` helper that derives the expected
  text from the contract (exactly two lines change) rather than from an
  implementation; "not rewritten" observed through an unchanged inode; "no
  reindex on a no-op" through a sentinel `INDEX.md`; the INDEX-refresh
  failure through a real malformed sibling. No mock anywhere.
- `tests/test_cli_relate.py` (+48): one-sided `add` / `remove` with exact
  bytes, idempotence, the add-then-remove round trip with and without an
  existing group under `--date`, the write footprint, the closed record, the
  archived-source (R2) and archived-target rules, a non-UTF-8 binary target,
  the four TARGET refusals, the 22-case grammar boundary, the injection
  refusals, both R3 cases, a 70-verb fixed-seed fuzz through in-process
  `cli.main`, the recognized-pair byte lock, an extension-state endpoint, and
  the suite's probe replicated exactly.
- `tests/test_relate_plan.py` (+11): the one-sided plan through
  `_plan_one_sided`, which turns today's `ValueError` into an assertion
  naming the missing behaviour; the grammar guard; a 600-verb pure-predicate
  fuzz with independent valid and invalid generators.
- `tests/test_cli_archive.py` (+4), `tests/test_body_from.py` (+4),
  `tests/test_cli_stamp.py` (+6), `tests/test_index.py` (+1),
  `tests/test_cli_index.py` (+2), `tests/test_cli_list.py` (+1),
  `tests/test_cli_touch.py` (+2), `tests/test_walker.py` (+1),
  `tests/test_cli_project_set.py` (+2), `tests/test_cli_project_rename.py`
  (+1), `tests/test_cli_mv.py` (+1), `tests/test_model.py` (+56),
  `tests/test_skill.py` (+2).
- **Pre-existing edits, exactly the authoritative list:**
  `test_relate_unknown_verb_refuses` → `test_relate_verb_outside_the_free_form_grammar_refuses`
  (verb `see also`, the full R1 message); `test_relate_quiet_suppresses_success_but_never_a_refusal`
  (verb `Pairs-With`); `test_relate_case_variant_verb_refuses` (docstring
  only — R1 keeps the stem, OQ-4); `test_archive_renders_the_witness_in_the_trees_date_format`
  (input `Updated: 20-05-2026`, exit 0, the two INDEX assertions dropped, the
  three witness assertions kept, the docstring pointing at the new walking-verb
  test); `test_stamp_supersedes_invalid_existing_block` →
  `test_stamp_refuses_a_full_block_with_an_invalid_role_with_zero_bytes`;
  the four packaging pins at 2.1.0 (`test_a3_project_version_is_2_1_0`,
  `test_c2_docs_version_is_2_1_0` renamed; `test_b1_wheel_builds`,
  `test_b2_sdist_builds` in place). The `_attic_tree` builder and the stamp
  fixture's prose are Phase 3's.
- Updated the test matrix's table with the final ids.

### Decisions / issues

- **Three planned names corrected so they claim only what a test can
  observe** (Check calibration — the behaviour asserted is unchanged):
  `…_then_one_state_and_reindexes_once` became `…_and_refreshes_the_index`,
  and `test_lifecycle_names_a_duplicated_path_once_and_writes_it_once` became
  `test_lifecycle_plans_and_reports_a_duplicated_path_once` — a reindex or
  write *count* is unobservable without a mock, which the mock policy rules
  out; `test_project_set_knows_a_project_carried_only_by_an_extension_state_doc`
  became `…_by_an_extension_vocabulary_doc`, because in the planned tree the
  document carrying `Project: beta` is the extension-*role* one.
- **Two planner tests added beyond the plan's list**, both pinning the P1.9
  contract: `test_plan_lifecycle_refuses_an_unknown_state` (P1.9 names the
  `ValueError` for an unknown state) and
  `test_apply_lifecycle_plan_writes_only_the_changed_documents` (the planner
  module otherwise never exercised `apply_lifecycle_plan`).
- **Planner tests kept honest.** `plan_relate` already raises `ValueError` for
  every unrecognized verb, so a bare `pytest.raises(ValueError)` would be
  falsely GREEN for "refuses an out-of-grammar verb" and "refuses an archived
  free-form source". Each of those tests first plans a grammar-valid
  free-form edge (RED today) and then asserts the refusal, so it pins that the
  guard is the grammar, and the source, rather than the recognized list.
- **One planned RED test is GREEN at baseline, and is recorded as a lock:**
  `test_relate_leading_hyphen_verb_is_consumed_by_argparse_and_writes_nothing`.
  argparse already consumes `-x` before any command runs, and R3 freezes that
  behaviour; the test rejects a later change (a `parse_known_args`, a
  `prefix_chars` tweak) that would let a hyphen-led verb reach a write.
- **The grammar boundary does not repeat the separator case.** The planned
  `-x` after `--` boundary case is covered, in both separator positions and
  for a bare `-`, by the dedicated
  `test_relate_leading_hyphen_verb_after_a_separator_is_refused_by_the_grammar`.
- **The parse-agreement sweep selects trees by configuration, not by name**
  (OQ-8): `_trees_with_default_vocabulary_and_date_format()` keeps every tree
  whose `.docs.toml` adds no vocabulary and keeps the ISO date format, so the
  vocabulary-extension tree Phase 3 adds is excluded because of what it
  configures; the parametrized ids do not change when it lands.
- **The C14 extraction was proven against the frozen text.** A scratchpad copy
  of the skill references with the P1.3 row and bullet substituted yields
  `relate add deck.md artifact-of deck.html` and a group-form body that
  `docs new` turns into the `artifact-of: deck.html` edge today.
- **RED reasons are assertions.** New symbols are fetched through a
  module-local `_symbol(name)`; `parse(..., config=)` asserts the keyword on
  `inspect.signature` first; in-process walk failures are re-raised as
  assertions naming the missing behaviour. Three failures that first printed
  as bare `assert` lines gained messages.

### Verification

- `.venv/bin/python -m pytest --co -q` — **1688 collected**, 0 errors.
- `.venv/bin/python -m pytest -q` — **185 failed, 1503 passed**. Of the 184
  new ids plus the 4 renamed ids, 182 are RED and 6 GREEN (the five planned
  locks and the argparse lock above); the 3 other failures are pre-existing
  ids on the authoritative list (the archive date-format test, `test_b1`,
  `test_b2`).
- `comm` against the ids collected at `e48adb9`: exactly the four renamed ids
  removed; 188 added.
- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean.
- `git diff e48adb9 --stat -- src/docs_cli/cli.py` — empty.

## Phase 3 — Create Data/Fixtures — 2026-10-27

### Objective

Provide the data the Phase 2 tests point at — one semantic per fixture,
structure-only, with fixed past dates — and make the two pre-existing fixture
edits the authoritative list names.

### Actions taken

- **One committed tree, `tests/fixtures/trees/vocab-extension/`** (OQ-8):
  `.docs.toml` with `[project] name = "vocab-extension"`, the explicit
  default `[archive]` pair, and `[vocabulary] add_lifecycles = ["shipped"]`,
  `add_roles = ["adr"]`;
  - `shipped-spec.md` — `shipped` / `spec`, `Project: vocab-extension`,
    carrying `precedes: draft-note.md` and the free-form
    `pairs-with: decision-record.md`;
  - `decision-record.md` — `active` / `adr`, `Project: beta` — the only
    document in project `beta`, so `beta` is a known project only when this
    document is read with the tree's configuration;
  - `draft-note.md` — `draft` / `notes`, `Project: vocab-extension`, carrying
    the reciprocal `follows: shipped-spec.md`, so the pair is complete and the
    two extension documents are the only reason a walk could fail.
  Every `Updated:` is the fixed `2026-06-01`; no body carries a Markdown link;
  no filename carries a space or a parenthesis.
- **`_attic_tree`** (`tests/test_cli_mv.py`): its four `Updated:` lines move
  from ISO to the tree's `%d-%m-%Y` (`20-05-2026`), and its docstring's
  defect paragraph is replaced by one sentence stating that every date is in
  the tree's own format.
- **`tests/fixtures/stamp/raw-invalid-block.md`**: prose only — the
  BODYMARKER paragraph's second line and the `## Section` paragraph now
  describe the refusal its renamed test expects; the block (lines 1–6) and
  the BODYMARKER line are unchanged.
- Every non-default `date_format` case stays an inline `tmp_path` builder
  (the M25 rule): each asserts on written bytes or needs its own sidecar.

### Decisions / issues

- **Sweep bookkeeping, verified rather than assumed.** The tree joins the
  three directory-derived sweeps in `tests/test_check.py` as **+3 ids**, all
  GREEN — it uses one complete recognized pair (no `missing-inverse`), no body
  link, and no archive-date field. The parse-agreement sweep in
  `tests/test_model.py` selects trees by configuration, so it excludes this
  tree because it configures extensions and its 53 ids do not move. *(Step 1
  review, claude-N9: the swept ids of the pre-M27 and pre-M28a sweeps now
  include this later fixture — harmless, since each asserts only that its own
  rule stays silent, and their names are not changed. The review resolution
  also consolidated the 53-id agreement sweep into one test, claude-T1.)*
- **The planned RED flip happened.** With `_attic_tree` corrected,
  `test_mv_does_not_refuse_inside_an_ordinary_archive_named_subdirectory`
  goes RED — `docs mv`'s walk still reads `20-05-2026` with the ISO default —
  exactly as the plan predicted; `test_mv_refuses_a_cross_dated_relocation_on_a_non_default_archive_tree`
  stays GREEN because the refusal fires before the walk.
- **The vocabulary-dependent tests now fail for the behaviour, not the
  fixture.** Before this phase they failed on "the committed
  `vocab-extension` fixture tree must exist"; now each fails on the real 2.0.0
  refusal (`Role: 'adr' not in vocabulary`, `Lifecycle: 'shipped' not in
  vocabulary`, the `beta` typo-guard refusal).

### Verification

- `docs check tests/fixtures/trees/vocab-extension` — no violations (exit 0).
- `git diff --name-status e48adb9 -- tests/fixtures` — `M` for
  `stamp/raw-invalid-block.md` (prose lines only) and the INDEX snapshot,
  plus the four added `vocab-extension/` files; every pre-existing fixture
  tree is byte-identical.
- `.venv/bin/python -m pytest --co -q` — **1691 collected** (1688 + the 3
  swept ids), 0 errors.
- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean; `git diff e48adb9 --stat --
  src/docs_cli/cli.py` — empty.

## Phase 4 — Run Tests (RED Baseline) — 2026-10-27

### Objective

Prove the new tests fail for the intended missing behaviour and for nothing
else, prove mechanically that every pre-existing test id is present, and
classify every GREEN-at-baseline lock. Risk is Standard (Q8): no operator
checkpoint; the evidence below feeds the end-of-Step-1 reviews.

### The baseline

```
.venv/bin/python -m pytest --co -q              ->  1691 tests collected
.venv/bin/python -m pytest -q --tb=line -rfxXE  ->  186 failed, 1505 passed in 65.42s
```

The arithmetic closes: **1504** pre-existing ids (1500 under their own id +
the 4 renamed) + **184** authored ids + **3** swept ids
(`vocab-extension` in the three `tests/test_check.py` sweeps) = **1691**.

*(Restated after the Step-1 same-instance audit, which added five RED tests
pinning frozen clauses no test covered — see that section: **1696
collected, 191 failed, 1505 passed**; 189 authored ids, 183 of them RED;
`AssertionError` 180, `AttributeError` 11; Phase 6's count becomes 106. The
figures in this section are the measurement taken at the Phase 4 commit and
stay true of it.)*

*(Restated again after the Step 1 review resolution: **1656 collected, 150
failed, 1506 passed**; `AssertionError` 139, `AttributeError` 11; 149
authored ids — 142 RED, 7 GREEN — plus the 3 swept; landing 24 at Phase 5,
117 at Phase 6, 9 at Phase 7. The deltas: twelve new ids from the blockers
and should-fixes (Phase 6, all RED, except
`test_stamp_freshly_stamps_an_incomplete_block_even_with_an_out_of_vocabulary_value`,
a new GREEN lock that rejects a stamp refusal ignoring the completeness
test); the 53-id parse-agreement sweep consolidated into one test (Phase 5:
55 → 3); and `test_stamp_keeps_todays_behaviour_for_a_block_failing_for_an_unrelated_reason`
renamed `test_stamp_restamps_a_complete_block_whose_related_bullet_is_malformed`.
The pass entry below records each finding.)*

| Population | Ids | RED | GREEN |
|---|---|---|---|
| pre-existing, own id | 1500 | 4 — all on the authoritative list | 1496 |
| pre-existing, renamed | 4 | 4 — all on the authoritative list | 0 |
| authored | 184 | 178 | 6 — the locks below |
| swept | 3 | 0 | 3 — the locks below |
| **total** | **1691** | **186** | **1505** |

### Probes

- **Collection errors: 0.**
- **xfail / xpass / errors: 0** — `-rfxXE` emits no `XFAIL`, `XPASS` or
  `ERROR` line, and no warnings summary.
- **Tracebacks: 0, INTERNALERROR: 0** — counted over the `--tb=line` output,
  which prints no test source (M28's false-positive lesson: several tests
  assert `"Traceback" not in proc.stderr` in their own source).

### Exception-class census (`--tb=line`)

| Class | Count | Where | Why |
|---|---|---|---|
| `AttributeError` | 11 | `tests/test_lifecycle_plan.py` (10, on `plan_lifecycle`) and the pure grammar fuzz in `tests/test_relate_plan.py` (1, on `relate_verb_in_grammar`) | the Phase-5 symbols are fetched through `_symbol(name)`, so the RED reason is one clean missing attribute, never a collection error |
| `AssertionError` | 175 | everything else | the behaviour is absent, not the symbol |

No `TypeError` (the `parse(..., config=)` callers assert the keyword on
`inspect.signature` first), no `ValueError` (`_plan_one_sided` reports
`plan_relate`'s refusal of a free-form verb as an assertion), no domain error
escaping a test (in-process walks re-raise as assertions), and no bare
`assert` line.

### Mechanical no-regression proof

Ids collected in a throwaway `git worktree` at the pre-Phase-1 commit
`e48adb9` and at HEAD, compared with `comm`; failing ids from `-rf`:

| Measure | Result |
|---|---|
| ids at `e48adb9` | **1504** |
| ids at HEAD | **1691** |
| `comm -23` — removed | **4**, exactly the renamed rows: `test_relate_unknown_verb_refuses`, `test_stamp_supersedes_invalid_existing_block`, `test_a3_project_version_is_2_0_0`, `test_c2_docs_version_is_2_0_0` — each present under its new id |
| `comm -13` — added | **191** (184 authored + 3 swept + the 4 new ids of the renamed rows) |
| pre-existing own ids failing | **4** — `test_archive_renders_the_witness_in_the_trees_date_format`, `test_mv_does_not_refuse_inside_an_ordinary_archive_named_subdirectory`, `test_b1_wheel_builds`, `test_b2_sdist_builds` |
| AST function-body diff of every pre-existing `tests/*.py` function (`ast.dump` without positions) | changed: exactly the archive date-format test, `_attic_tree`, the quiet and case-variant `relate` tests, `test_b1`, `test_b2`; removed: exactly the four renamed functions. Nothing else |
| `git diff --numstat e48adb9 -- tests/fixtures` | `stamp/raw-invalid-block.md` (prose only) and the INDEX snapshot modified; `trees/vocab-extension/` added; every other fixture byte-identical |
| `git diff --stat e48adb9 -- src/docs_cli/cli.py` | **empty** |

Every expected-RED pre-existing id is on the authoritative list — the renamed
grammar refusal, the archive date-format test, the second `_attic_tree` test,
the four packaging pins, the renamed stamp test — and every other
pre-existing id is GREEN, including the edited quiet and case-variant `relate`
tests and `test_mv_refuses_a_cross_dated_relocation_on_a_non_default_archive_tree`
(its refusal fires before the walk).

### RED classification — every failure traced to a family and a landing point

| # | Family | Landing |
|---|---|---|
| 10 | **The lifecycle planner** (`tests/test_lifecycle_plan.py`): staging, the `Updated:` rule, the four guards, deduplication, an extension state, apply, the record | **Phase 5** — `LifecycleEdit`, `LifecyclePlan`, `plan_lifecycle`, `apply_lifecycle_plan`, `lifecycle_plan_to_json` |
| 11 | **The one-sided relate planner** (`tests/test_relate_plan.py`): one edit, no inverse, TARGET never read, the archived-source and grammar guards, the record, apply, the pure fuzz | **Phase 5** — `relate_verb_in_grammar`, `RelatePlan.inverse: str \| None`, the free-form branch of `plan_relate` |
| 55 | **`parse()` honours a config** (`tests/test_model.py`): accepts extensions and the date format, rejects the ISO spelling on a `%d-%m-%Y` tree, and agrees with the bare call on all 53 default-configuration trees | **Phase 5** — `parse(..., *, config=None)` |
| 31 | **`docs lifecycle` at the CLI** (`tests/test_cli_lifecycle.py`, all but the help test) | **Phase 6** — register the verb, `_cmd_lifecycle` |
| 47 | **Free-form `relate` at the CLI** (`tests/test_cli_relate.py`: the renamed grammar refusal and 46 authored ids — R1, R2, the TARGET rules, the boundary, the fuzz, the probe, an extension-state endpoint) | **Phase 6** — `_cmd_relate`'s grammar check and free-form route, `_resolve_relate_endpoint(..., config, parse_endpoint=)` |
| 6 | **The stamp refusal** (`tests/test_cli_stamp.py`: the renamed test and 5 authored) | **Phase 6** — `_stamp_config_failure` and its use in `_cmd_stamp` |
| 2 | **Archive invariance for relate-written edges** (`tests/test_cli_archive.py`) | **Phase 6** — they rebuild their trees with free-form `relate` |
| 15 | **The config passed at every walking site** — `test_walker.py` (1), `test_cli_list.py` (1), `test_cli_touch.py` (2), `test_cli_index.py` (2), `test_index.py` (1, `render_index`), `test_cli_project_set.py` (2), `test_cli_project_rename.py` (1), `test_cli_mv.py` (1 + the pre-existing `_attic_tree` test), `test_cli_archive.py` (the walking-verb `bad-date` lock, an extension-state primary, and the pre-existing date-format test) | **Phase 6** — config at the seven `parse()` sites; `render_index`'s extension groups |
| 1 | **`docs lifecycle --help` wording** (`test_lifecycle_help_documents_the_grammar_and_flags`) | **Phase 7** (help strings), or Phase 6 if the registration lands its final description |
| 2 | **The skill's sidecar examples, run literally** (`tests/test_body_from.py`) | **Phase 7** — the frozen P1.3 text (the relate form also needs Phase 6) |
| 2 | **Skill routing and stale wording** (`tests/test_skill.py`) | **Phase 7** |
| 4 | **The 2.1.0 pins** (`tests/test_packaging.py`) | **Phase 7** |

The arithmetic closes: 10 + 11 + 55 = **76 at Phase 5**; 31 + 47 + 6 + 2 + 15
= **101 at Phase 6**; 1 + 2 + 2 + 4 = **9 at Phase 7** — 186 in total.

### GREEN at baseline — every lock classified, with the wrong answer it rejects

| Lock | Classification |
|---|---|
| `test_relate_recognized_pair_still_writes_both_halves_unchanged` | **genuine** — exact files, exact two-record plan, exact lines; rejects any free-form branch that perturbs the recognized path (D4's byte-for-byte promise) |
| `test_relate_leading_hyphen_verb_is_consumed_by_argparse_and_writes_nothing` | **genuine** — rejects a change (`parse_known_args`, `prefix_chars`) that lets a hyphen-led verb reach the command and write (R3) |
| `test_bare_parse_keeps_the_built_in_defaults` | **genuine** — rejects a `parse()` whose bare call picks up configuration from ambient state or changes its defaults |
| `test_stamp_keeps_todays_behaviour_for_a_block_failing_for_an_unrelated_reason` | **genuine** — rejects an over-broad stamp refusal that refuses every complete block failing `parse()`, which the operator's decision excludes |
| `test_body_opening_with_a_related_group_becomes_metadata` | **genuine** — rejects a change to `docs new` or the C4 heuristic that drops the creation-time route the skill relies on |
| `test_inline_related_line_stays_body_text` | **genuine** — rejects a parser change that starts reading an inline `Label: value` after the blank line as metadata, silently rewriting bodies |
| the three `[vocab-extension]` sweep ids in `tests/test_check.py` | **genuine** fixture-shape locks — the new tree trips no `missing-inverse`, body-link or archive-date rule, so every assertion against it measures the vocabulary |

Pre-existing locks worth naming, all GREEN: every recognized-verb
`test_cli_relate.py` / `test_relate_plan.py` id; the edited quiet and
case-variant tests (R1 keeps the stem); the reference byte-identity tests
(Phase 1 kept both mirrors identical); the live-INDEX snapshot; the dogfood
`docs check` test.

### Falsely-GREEN check at this gate

- **Every intended-exit-2 test asserts a frozen string**, because argparse's
  `invalid choice: 'lifecycle'` and today's `unknown verb` both already exit
  2. Every intended-exit-0 test asserts bytes, a record, or a listed edge,
  never a bare exit code.
- **The planner refusals cannot pass for the wrong reason.** "Refuses an
  out-of-grammar verb" and "refuses an archived free-form source" first plan
  a grammar-valid free-form edge (RED today) before asserting the
  `ValueError`; a bare `pytest.raises` would have been GREEN on today's
  recognized-only guard.
- **Fixture-backed tests assert their tree exists**, so between Phase 2 and
  Phase 3 they failed on the missing tree rather than passing on an empty
  copy; after Phase 3 each fails on the real 2.0.0 refusal.
- **Two parametrizations were given readable ids at this gate** — the
  injection refusals (`[a-colon]`, `[a-newline]`, `[a-carriage-return]`) and
  the planner's grammar guard (`[an-empty-verb]` instead of `[]`); no
  assertion changed.
- **Naming lint** (token-based, over the 191 added ids): no milestone,
  decision, clause, phase, step or review token. Two tokens were examined and
  kept: `milestone` in `test_milestone_setup_needs_no_hand_edit` is the
  scenario's domain word (setting up a milestone is the primary use case),
  and `c2` in `test_c2_docs_version_is_2_1_0` is `tests/test_packaging.py`'s
  own check-number scheme (OQ-15).

### Phase-5/6/7 follow-through, carried from Phase 1

1. Phase 5: `parse(..., *, config=None)`; `_RELATE_VERB_RE` /
   `relate_verb_in_grammar`; `RelatePlan.inverse: str | None` and
   `plan_relate`'s one-sided branch (source only, never reads TARGET,
   `ValueError` on an out-of-grammar verb or an archived free-form source);
   the lifecycle records, planner, apply and record; `_stamp_config_failure`
   — wired nowhere, so the CLI tests stay honestly RED at the seam.
2. Phase 6: register `lifecycle`; `_cmd_lifecycle` per P1.1's order;
   `_cmd_relate`'s grammar check, free-form route and R2;
   `_resolve_relate_endpoint`'s `config` and `parse_endpoint`; the config at
   the seven `parse()` sites; `render_index`'s extension groups; the stamp
   refusal.
3. Phase 7: every surface in P1.8, the frozen P1.3 text, the 2.1.0 pins and
   the editable reinstall `tests/test_version_metadata.py` needs, the
   CHANGELOG (P1.7), and `feedback-log.md` — the three owned entries closed or
   noted and follow-ups 2, 3, 7 and 8 registered (OQ-11).
4. In-code prose no test polices, named so Phases 5–7 do not miss it:
   `parse()`'s docstring (its *Raises* paragraph still says validation "uses
   BUILTIN_STATUSES and BUILTIN_ROLES"), `RelatePlan`'s docstring ("`inverse`:
   `verb`'s recognized inverse", "`edits`: Always exactly two"),
   `plan_relate`'s docstring ("`verb`: A recognized reciprocal verb"),
   `inverse_verb`'s docstring (`_cmd_relate` "refuse it"),
   `_add_relate_subverb`'s docstring, `render_index`'s *Format details*, and
   `_cmd_stamp`'s classification comment.

### Verification

- `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
  `.venv/bin/mypy src/ tests/` — clean.
- `docs check .` from the docs root — no violations found (exit 0).
- `cmp` of both mirrors against the specs, and of `docs/INDEX.md` against
  the frozen snapshot — identical.
- `git diff --stat e48adb9 -- src/docs_cli/cli.py` — **empty**. Phases 1–4
  change no product code, by design.

## Step 1 same-instance audit — 2026-10-27

Run against Phases 1–4 after the last phase and before returning, per
ship-milestone's *consistency / completeness / accuracy audit*. Every item was
worked; findings were fixed in the audit commit, and nothing needs an
operator decision.

### Issues found and fixed

1. **Catalogue message L4 had no `docs lifecycle` test.** Every other
   L-message was asserted; a malformed `.docs.toml` was not, so an
   implementation that forgot to catch `TOMLDecodeError` would have shipped a
   traceback. Added `test_lifecycle_malformed_sidecar_exits_2_and_writes_nothing`
   (RED).
2. **OQ-1's path rule was not pinned.** Every `docs lifecycle` test passes
   `--root` with a path that exists only root-relative, which a cwd-first or
   root-then-cwd rule would also satisfy. Added
   `test_lifecycle_resolves_a_relative_path_against_the_docs_root_not_the_cwd`
   (RED): from `sub/`, `x.md` refuses and `sub/x.md` succeeds.
3. **P1.2's "`--reason` is still shape-checked when given" had no free-form
   test.** Added `test_relate_free_form_still_shape_checks_a_given_reason`
   (RED): empty and multi-line reasons refuse with the unchanged messages.
4. **No test killed a free-form path that skips parsing SOURCE.** The
   existing malformed-endpoint test covers a recognized verb's TARGET, so a
   `parse_endpoint=False` leaking to SOURCE would have reached the editor and
   raised. Added `test_relate_free_form_source_must_parse_and_exits_1_when_malformed`
   (RED).
5. **D4 / C7's E11 direction for `relate` had no test** — the Phase 1 wording
   fix (OQ-6) named it, nothing asserted it. Added
   `test_relate_refuses_an_endpoint_dated_outside_the_trees_date_format`
   (RED); at baseline it fails the instructive way — 2.0.0 refuses the
   correctly dated endpoint and accepts the mis-spelled one.
6. **`cli.md` said "one line per named document"** for `docs lifecycle`'s
   human output, where P1.1 freezes one line per *distinct* named document in
   first-seen order. Corrected; mirror re-synced.
7. **The progress lines lagged.** The task plan's *Overview* and this log's
   *Implementation metadata* still said Step 1 was in progress; both now say
   Phases 1–4 are complete and the review is pending.
8. **The baseline is restated** (Phase 4 carries the note): **1696
   collected, 191 failed, 1505 passed**; `AssertionError` 180,
   `AttributeError` 11; 0 tracebacks, xfails or errors; the five new RED ids
   land at Phase 6 (76 / 106 / 9); `comm` still removes exactly the four
   renamed ids, and the AST diff is unchanged. The matrix carries the new ids.

### Checked clean

- **Completeness.** The one Deliverable in range — the frozen flag / exit /
  message matrix, records and Phase-5 signatures — is met; every phase in
  range has a log section and a dated row; no placeholder, TODO or
  commented-out code was added.
- **Accuracy.** No product code changed (`git diff e48adb9 --
  src/docs_cli/cli.py` is empty), so the only code-versus-spec divergence is
  the deliberate one the M25–M28a precedent accepts: `cli.md` and
  `convention.md` describe the frozen 2.1 surface ahead of its Phase 5–7
  implementation. The specs' statements about *existing* behaviour were
  re-read against the code; the three that were wrong are fixed (`docs index`
  exits, `docs stamp`'s required fields, `docs stamp`'s INDEX-refresh exit 2).
- **Tracker and identity.** `milestone-plan.md` row `100 |
  lifecycle-and-free-form-relate | active | — |`, Notes unchanged; slug, stem
  and branch root `lifecycle-and-free-form-relate/` agree; the three
  artifacts resolve; no recognized relationship applies; `status.md` stays
  narrative-only with no phase progress (nothing in its narrative changed).
- **Documentation.** Every edited document was `docs touch`ed (no hand-set
  `Updated:`); `docs check .` exits 0; both mirrors are byte-identical; the
  INDEX snapshot matches. Follow-ups 7 and 8 live only in the task plan for
  now because OQ-11 — a binding conductor resolution — schedules their
  `feedback-log.md` registration (with 2 and 3) at Phase 7; the archive that
  could lose them is Step 3's, so nothing is at risk.
- **Codebase.** Tests reuse every planned helper unmodified (`_pair_tree`,
  `_archived_pair_tree`, `_snapshot`, `_tree`, `_m28_tree`, `_m28_snapshot`,
  `_minimal_tree`, `_stamp_tree`, `_two_doc_root`, `_archived_pair_root`,
  `_plan`, `_m25`); new helpers are module-local; stdlib only; no mock.
- **Patch bloat — noted for the reviewers, not hidden.** The test diff is
  **+2,826 / −96 lines** at the review `HEAD` `6f94a0a` (corrected at the
  review, claude-N8: the first figure here, +2,723, was measured before the
  five audit tests landed) against the plan's +900 to +1,300 for the whole
  milestone. It traces to the authored id count (189 against the ~120
  planned: the 22-case boundary, the five-state round trip, the 53-id
  agreement sweep, the planner modules) and to `ruff format`'s
  one-argument-per-line layout of subprocess argv lists and literal JSON
  records; every id traces to a clause and a planned or audit-added name, and
  no helper or fixture exists for a single assertion.
- **Tests pin the contract** without over-constraining it: exact bytes, exact
  records and exact messages appear only where the contract freezes them (the
  surgical-edit promise, D4's byte-for-byte promise, the L/R catalogues, the
  stamp message); write counts and reindex counts are never claimed, because
  they are unobservable without a mock.
- **Adequacy and mocks.** Every clause C1–C25 maps to named tests;
  hidden/generalization categories are recorded without cases; the property
  checks and both fuzzers are written (RED, results at Phase 8); the mutation
  smoke is Phase 8's; no mock was added.
- **Metrics.** `visible_pass_rate` at a RED baseline is not meaningful
  (1505 / 1696); hidden suite, coverage and mutation tooling are not
  configured.
- **A transient interpreter crash, recorded.** One full run showed
  `tests/test_packaging.py::test_d4_install_skill_is_idempotent` failing with
  the wheel venv's `docs` exiting −11 (SIGSEGV) on its second invocation. It
  passed three times in isolation, the whole packaging module showed only the
  four listed pins failing, and the next full run was the clean restated
  baseline above. No product code is involved; noted in case it recurs.

## Step 1 review-pass-001

- Pass id: `Step 1 review-pass-001`.
- Ledger location: `lifecycle-and-free-form-relate-impl.md#step-1-review-pass-001`
  (docs root `/home/user/opt/docs-cli/docs`; repository path
  `docs/lifecycle-and-free-form-relate-impl.md#step-1-review-pass-001`).
- Predecessor: `Step 0 review-pass-001`
  (`lifecycle-and-free-form-relate-impl.md#step-0-review-pass-001`), closed,
  with `final-sync: ready` in `e48adb9f9bddaf6169e2387280907e66d531c71b`. No
  `contract-rework` entry exists between them.
- Status: `closed` — both provider attempts are terminal (both returned),
  every finding is dispositioned with evidence, the correcting commit
  `9b8c83eb69c11cf3aeab3b69989e64f998d95c38` is recorded, the conditional re-review is
  recorded `not required` with the conductor's evidence, and `final-sync` is
  `ready`.
- Frozen packet (conductor): slug `lifecycle-and-free-form-relate`; step 1,
  Phases 1–4; branch `lifecycle-and-free-form-relate/phases-1-4`; base
  `e48adb9f9bddaf6169e2387280907e66d531c71b`; review `HEAD`
  `6f94a0addca41140e1dff32b87d3bc6d2e91507f` (`…(review-ready): open Step 1
  review-pass-001`); predecessor `Step 0 review-pass-001` (closed); project
  `docs`, path `""`, stem `lifecycle-and-free-form-relate`; tracker row 100
  `active`; claim `2ad941e`; branch root `lifecycle-and-free-form-relate/`;
  risk Standard. Gates the conductor re-ran at the review `HEAD`: `ruff`,
  `ruff format`, `mypy` clean; pytest 1696 collected / 191 failed (the
  intended RED) / 1505 passed, with one extra intermittent failure seen once
  — the known `test_d4_install_skill_is_idempotent` flake; `docs check` exit
  0; mirrors and the INDEX snapshot byte-identical. Both reviewers received
  the identical provider-neutral prompt with the Step 1 test-quality clause,
  isolated from each other.
- Packet inputs as handed off: content `HEAD`
  `c9e913e8f3b252bad7e249f7ecfc10fb012da614` (the audit commit); Phase
  commits `d3c216c` (1), `03e0cdb` (2), `0e8c756` (3), `90cea8e` (4); the
  review-ready commit added only this entry.
- Tracker: `milestone-plan.md` in the docs root; owning project `docs`;
  project path empty (dedicated docs root); artifact stem
  `lifecycle-and-free-form-relate`; row `100 | lifecycle-and-free-form-relate
  | active | — |`, Notes unchanged; claim checkpoint
  `2ad941e269339f5a125856f5bcda9339cd9f5b15`; semantic branch root
  `lifecycle-and-free-form-relate/`.
- Claude slot: `returned` — Anthropic Claude family, Claude Opus 5.5
  (`claude-opus-5-5`), host-reported; a fresh Claude Code sub-agent at xhigh
  effort.
- GPT slot: `returned` — OpenAI GPT family; Codex CLI 0.160.0, `codex exec -m
  gpt-6-astra -c model_reasoning_effort=xhigh -s read-only`; the session log
  reports `model: gpt-6-astra` (the reviewer self-reported "GPT-6 (Codex)").

**Findings and dispositions.**

Source ids are the reviewers' own; gpt-B1 and claude-B1 are one gap found
independently, and gpt-B2 and claude-S3 were merged and treated as a
blocker by the conductor. **Correcting commit** for every row:
`9b8c83eb69c11cf3aeab3b69989e64f998d95c38` (`lifecycle-and-free-form-relate(phase 1-4):
resolve Step 1 review-pass-001 findings`), written here at finalization — a
commit never carries its own hash. Every new test's RED reason was
checked by running it at the checkpoint; the counts are in *Verification*
below.

| Id | Severity | Disposition | Evidence |
|---|---|---|---|
| gpt-B1 / claude-B1 | blocker | **fixed** in `9b8c83eb69c11cf3aeab3b69989e64f998d95c38`; re-review: not required | Nothing pinned `docs lifecycle` on a non-default `date_format` tree or with a named source already in an extension state. Added `tests/test_cli_lifecycle.py::test_lifecycle_promotes_an_extension_state_on_a_non_default_date_format_tree`: a `%d-%m-%Y` tree with `add_lifecycles = ["shipped"]`, source `shipped` / `20-05-2026`; `docs lifecycle m.md active --json` must exit 0 with the promoted bytes and today in `%d-%m-%Y` (file and record `date`), refresh the INDEX, leave `docs check` clean, and make a repeated call a zero-byte no-op. RED (`invalid choice: 'lifecycle'` → `AssertionError`); lands at Phase 6; in the matrix's *Boundary — date format* row. |
| gpt-B2 + claude-S3 | blocker | **fixed** in `9b8c83eb69c11cf3aeab3b69989e64f998d95c38`; re-review: not required | The stamp "complete block" boundary (`Lifecycle`, `Role`, `Updated` required, `Project` not) was unprotected. Added `tests/test_cli_stamp.py::test_stamp_refuses_a_complete_block_without_a_project_line_with_zero_bytes` (RED — 2.0.0 re-stamps at exit 0; the frozen message naming `Role:` and zero bytes asserted) and the GREEN lock `::test_stamp_freshly_stamps_an_incomplete_block_even_with_an_out_of_vocabulary_value` (`Lifecycle: activ`, no `Updated:` → `docs: stamped …`, exit 0), which rejects a refusal that ignores the completeness test. Together they kill both directions of mutation target 11's completeness check. |
| claude-S4 | should-fix | **fixed** | The date half of E12 had no lock. Added `tests/test_cli_stamp.py::test_stamp_keeps_a_correctly_dated_document_on_a_non_default_date_format_tree`: only `Updated:` changes, rendered `%d-%m-%Y`. RED (2.0.0's reindex refuses the tree's own spelling). |
| gpt-S1 | should-fix | **fixed** | Added `tests/test_cli_relate.py::test_relate_free_form_accepts_a_malformed_markdown_target_without_reading_it`: a `.md` TARGET that does not parse is accepted under `--dry-run` (zero bytes) and written when excluded (so the reindex never walks it) — an extension-based "parse the `.md` targets" rule fails it. RED. |
| gpt-S2 | should-fix | **fixed** | `tests/test_model.py::test_bare_parse_keeps_the_built_in_defaults` now writes a sidecar extending the vocabulary AND the date format at the very root it passes, and still sees the built-ins and ISO — so it rejects a `parse()` that picks up ambient config. The explicit-config half shares the same sidecar (`_EXTENDED_SIDECAR`) in `::test_parse_with_a_config_accepts_its_extensions_and_date_format` (RED until Phase 5); the two are kept separate so the lock still guards at baseline. |
| gpt-S3 + claude-S1 | should-fix | **fixed** | D10 aligns the vocabulary and date judgement only. Measured: a malformed `Related:` bullet and a multi-valued `Project:` pass `docs check` (exit 0) and fail `docs index` (exit 2); `docs list` omits such a document with nothing on stderr. Scoped every copy of the claim: `cli.md` *Invocation*, `convention.md` *Archive subtree*, the P1.7 upgrade note, D9's upgrade note, the *Contract* invariant and compatibility line, the D10 deliverable, A1's resolution and a success criterion ("no verb starts refusing a document `docs check` accepts"), and the matrix's risk line, C7 (now carrying both D10 directions) and C22. E7's "with a stderr error" corrected in the task plan and in this log's setup row (claude-N7). Found while measuring: E4's "a missing colon or empty target fails as `malformed`" was also wrong — both pass `docs check` — corrected in both places. Mirrors re-synced. |
| claude-S2 (JC1) | should-fix | **fixed — conductor decision JC1, option (a)** | Free-form `relate` now refuses (frozen) a TARGET whose root-relative path holds a line break or leading or trailing whitespace: **R4**, exit 2, zero bytes — added to P1.2's catalogue (with its predicate), the check order (step 5a, after TARGET resolves, before the self-edge check), a post-review amendment paragraph, `cli.md` (*What must parse*, stage 1, *Exits*, the exit summary) and `convention.md` (*Writing an edge*); mirrors re-synced; matrix C10. Tests: `tests/test_cli_relate.py::test_relate_free_form_refuses_a_target_path_a_bullet_cannot_carry[a-line-break \| a-carriage-return \| a-leading-space \| a-trailing-space]`, RED. Recognized verbs stay byte-for-byte unchanged (D4); their injection — re-measured: `docs relate add a.md precedes $'b\nLifecycle: archived\nx.md'` exits 0 and writes a `Lifecycle: archived` line into `a.md` — is *Follow-ups* item 9, with no lock freezing it. Option (b) would override D4 and was not taken. |
| gpt-N1 | nit | **fixed** | `test_stamp_keeps_todays_behaviour_for_a_block_failing_for_an_unrelated_reason` → `test_stamp_restamps_a_complete_block_whose_related_bullet_is_malformed`. |
| claude-N1 | nit | **fixed** | `tests/test_cli_lifecycle.py` computes today inside each test (`_promoted` defaults at call time); no import-time `_TODAY`. |
| claude-N2 | nit | **fixed** | `test_plan_lifecycle_lists_a_duplicated_document_once` creates `sub/`, so `sub/../a.md` is a real second spelling. |
| claude-N3 (+ claude-T3) | nit | **fixed** | `tests/test_relate_plan.py` reuses `_m25`; its `_symbol` is removed. |
| claude-N4 | nit | **fixed** | `cli.md`'s `docs lifecycle` *Resolution*: "every success line and JSON field names the root-relative POSIX form" (refusals L8–L9 name the path as checked). |
| claude-N5 | nit | **fixed** | `tests/test_cli_lifecycle.py::test_lifecycle_refusals_follow_the_frozen_order_and_emit_no_record` (L5 before L7; L9 before an earlier-named L11; no stdout record on a refused `--json`) and `tests/test_cli_relate.py::test_relate_free_form_refusals_follow_the_frozen_order` (R1 before endpoint resolution; R2 before the `--reason` shape check). Both RED. |
| claude-N6 | nit | **fixed** | A symlinked TARGET inside the tree resolves to the file it points at — stated in `cli.md` *What must parse* and P1.2's TARGET rules, pinned by `tests/test_cli_relate.py::test_relate_free_form_symlinked_target_is_written_as_the_file_it_points_at` (RED). |
| claude-N7 | nit | **fixed** | The list test's misleading `stderr == ""` assertion is replaced by a comment (`docs list` omits silently; the complete listed set is the check); E7 corrected (row gpt-S3 + claude-S1). |
| claude-N8 | nit | **fixed** | The audit's footprint is corrected to **+2,826 / −96** at the review `HEAD` (its +2,723 predated the five audit tests); after this resolution **+3,100 / −96**. |
| claude-N9 | nit | **fixed** | A note in *Phase 3*: the pre-M27 and pre-M28a sweeps' swept ids include the later `vocab-extension` fixture — harmless; no rename. |

**Taste triage** (conductor decisions, binding at Standard risk).

- GPT: approach sound; no subjective findings.
- claude-T1 (the 53-id parse-agreement sweep was close to a tautology per
  id): **fixed** — one test,
  `test_config_aware_parse_agrees_with_bare_parse_on_every_pre_existing_tree`,
  loops over the configuration-selected trees and `docs/` and reports each
  disagreement by file; 53 ids become 1 (Phase 5's count 55 → 3).
- claude-T2 (the CLI fuzz duplicated the pure-predicate fuzz's invalid
  generation): **fixed** — the in-process CLI fuzz keeps its 30 generated
  valid verbs and takes a fixed set of 11 invalid verbs, one per refused
  category; exhaustive invalid generation stays with the 600-case
  pure-predicate fuzz and the 22-case boundary table.
- claude-T3 (`_symbol` beside `_m25`): **fixed** through claude-N3.
- claude-T4 (the task plan restates D10 six or more times): **waived** by the
  conductor — the gpt-S3 / claude-S1 fix corrected every restated copy now,
  and collapsing the document's structure mid-milestone would churn reviewed
  text; recorded as a candidate project convention, *Follow-ups* item 10.
- Patch bloat: both reviewers judged it explained (authored-id breadth plus
  formatting); T1 and T2 reduce the id count.

**Re-review.** **Not required** (conductor decision). Both blocker
resolutions are additive tests whose correctness is objectively verifiable by
inspection and by their recorded RED reason, and they do not change the
reviewed contract; JC1 (R4) is a should-fix resolved by a narrow new refusal
on new surface only, consistent with D6's injection rationale. The conductor
verified the correction directly at `9b8c83eb69c11cf3aeab3b69989e64f998d95c38`:

- `test_lifecycle_promotes_an_extension_state_on_a_non_default_date_format_tree`
  is RED with an `AssertionError` at `tests/test_cli_lifecycle.py:295`,
  because `lifecycle` is not a registered subcommand (argparse usage) — the
  correct reason;
- `test_stamp_refuses_a_complete_block_without_a_project_line_with_zero_bytes`
  is RED at `tests/test_cli_stamp.py:564`, because 2.0.0 re-stamps the file
  (`docs: stamped …`) — the correct reason;
- `test_stamp_freshly_stamps_an_incomplete_block_even_with_an_out_of_vocabulary_value`
  passes, as the intended GREEN lock;
- R4 is present at `docs/cli.md:2478` and mirrored;
- `src/docs_cli/cli.py` is unchanged against `6f94a0a`;
- the full suite is 1656 collected / 150 failed / 1506 passed, and
  `docs check` exits 0.

No re-review packet was frozen and no reviewer was re-engaged.

**Closure check.** Predecessor chain: this entry follows `Step 0
review-pass-001` (closed, `final-sync: ready` in `e48adb9`), whose text and
frozen packet are byte-identical to their state at `e48adb9`; no
`contract-rework` entry intervenes. One frozen packet is named for this pass
(base `e48adb9…`, review `HEAD` `6f94a0a…`). Both provider slots are
terminal and both returned, from different families, with host-reported
identities. Both reviewer-labeled blockers — gpt-B1 / claude-B1 and gpt-B2 +
claude-S3 — are `fixed` with the correcting commit and test evidence. Every
taste finding is fixed (claude-T1, T2, T3) or waived with a reason
(claude-T4); GPT raised none. The conditional re-review is recorded `not
required` with the conductor's evidence. The tracker row is still `100 |
lifecycle-and-free-form-relate | active | — |` under its frozen identity.

**Verification at the review-resolution checkpoint.**

- `.venv/bin/ruff check .` — clean; `.venv/bin/ruff format --check .` — 50
  files formatted; `.venv/bin/mypy src/ tests/` — no issues in 51 files.
- `.venv/bin/python -m pytest -q --tb=line -rfxXE` — **1656 collected, 150
  failed, 1506 passed**; 0 collection errors, tracebacks, INTERNALERRORs,
  xfails, xpasses or errors; census `AssertionError` 139, `AttributeError`
  11. RED: 142 authored ids and the 8 pre-existing ids on the authoritative
  list; GREEN: 7 authored locks and 3 swept ids.
- Id proof against `e48adb9`: removed exactly the four renamed ids
  (`test_relate_unknown_verb_refuses`, `test_stamp_supersedes_invalid_existing_block`,
  `test_a3_project_version_is_2_0_0`, `test_c2_docs_version_is_2_0_0`); 156
  added; the four pre-existing own ids failing are the listed ones. The AST
  diff of pre-existing test functions is unchanged: exactly the authoritative
  list plus `_attic_tree`.
- `docs check .` from the docs root — exit 0; both mirrors and the INDEX
  snapshot byte-identical; `git diff e48adb9 -- src/docs_cli/cli.py` empty.


**Verification report (sync-and-commit, ship-milestone Step 1).**

- Risk level: Standard (operator-confirmed, Q8).
- Fast gate commands run: `.venv/bin/ruff check .`; `.venv/bin/ruff format
  --check .`; `.venv/bin/mypy src/ tests/`; `.venv/bin/python -m pytest -q
  --tb=line -rfxXE`; from the docs root `docs touch` (task plan, this log,
  `status.md`), `docs index .`, `docs check .` and `docs check . --stale 14`;
  `cmp` of both mirrors against the specs and of `docs/INDEX.md` against
  `tests/fixtures/expected/docs-INDEX.md`.
- Deep gate commands run: none — no deep gate is configured; the mechanical
  `comm` / AST-diff id proof against `e48adb9` ran at the resolution
  checkpoint (exactly the four renamed ids removed; the AST diff exactly the
  authoritative list plus `_attic_tree`).
- Deferred / not configured gates: coverage, hidden suite and mutation tooling
  — not configured; the hand-applied mutation smoke and the property / fuzz
  results — Phase 8, per the milestone.
- Visible test result: **1656 collected, 150 failed, 1506 passed**; 0
  collection errors, tracebacks, INTERNALERRORs, xfails, xpasses or errors;
  `AssertionError` 139, `AttributeError` 11; the failing set is identical to
  the one the conductor verified at `9b8c83e`.
- Expected visible-test state: **intentional Step 1 RED** — 142 authored ids
  and the 8 pre-existing ids on the authoritative list fail for the missing
  milestone behaviour (classified in *Phase 4* and its restatements); 7
  authored locks and 3 swept ids pass; no unexpected pass, no unrelated
  failure.
- Hidden/generalization: categories only (repository fully visible); not
  applicable at Step 1.
- Coverage: not configured. Mutation: not configured (hand-applied smoke at
  Phase 8).
- Property/stateful and fuzz: written and RED at baseline; results at Phase 8.
- Benchmark/security/schema/migration: schema and injection refusals written
  (RED); benchmark not applicable; migration not applicable.
- Mock audit: no mocks added.
- Taste triage: complete — claude-T1, T2, T3 fixed; claude-T4 waived with a
  reason; GPT raised none.
- Ship-milestone Step 1 review ledger: this pass — predecessor chain intact,
  both slots returned, blockers fixed with evidence, re-review `not required`
  with the conductor's evidence; `final-sync: ready` below.
- Semantic tracker row / branch identity: `milestone-plan.md` row `100 |
  lifecycle-and-free-form-relate | active | — |`, Notes unchanged; project
  `docs`, project path empty, artifact stem `lifecycle-and-free-form-relate`,
  the three artifacts at their derived paths; branch
  `lifecycle-and-free-form-relate/phases-1-4` under root
  `lifecycle-and-free-form-relate/`; no recognized relationship applies;
  `status.md` links the tracker as narrative only (its narrative did not
  change, so its body was not edited).
- Contract/test matrix status: current — C1–C25 with the crosswalk, the
  final Phase 2 ids, and the review's additions (R4; the new tests).
- Docs check: exit 0; `--stale 14` exit 1 with seven pre-existing `stale`
  warnings on evergreen documents (`architecture.md`, `charter.md`,
  `definition-of-ready.md`, `dual-status-adr.md`, `release-runbook.md`,
  `test-strategy.md`, `vocab-adr.md`), reviewed — two fewer than at Step 0,
  because Phase 1 updated `cli.md` and `convention.md`.
- Diff scope: specs and mirrors, the milestone trio, the INDEX and its
  snapshot, the new `vocab-extension` fixture tree, one stamp fixture's
  prose, and test modules; `src/docs_cli/cli.py` unchanged since `e48adb9`.
- Operator approvals: Q3, Q7, Q8 and Packet A (setup); none new — JC1 is a
  conductor decision under Standard-risk authority.
- High-risk RED-baseline approval: not applicable (Standard).
- Remaining risks: the intermittent `test_d4_install_skill_is_idempotent`
  segfault (seen twice in full runs, never in isolation; no product code
  involved); follow-ups 7–10 await their Phase 7 / Phase 10 homes.

- final-sync: `ready`.

## Phase 5 — Update Base Interfaces — 2026-10-27

Step 2 (Phases 5–10) runs on `lifecycle-and-free-form-relate/phases-5-10`
from base `3e2c3caad4e2d2e48a5894f0d8ef888dcb4d2226` (the closed Step 1
sync commit). The baseline re-measured there before any edit:
**1656 collected, 150 failed, 1506 passed** — identical to the recorded RED
baseline.

### Objective

Land the pure pieces P1.9 froze, wired into no verb: the free-form verb
grammar, the one-sided relate plan, the lifecycle records and pure planner,
and `parse()`'s keyword-only `config`. `_cmd_relate` and `_build_parser`
stay untouched, so every CLI test stays honestly RED at the seam.

### Working contract, restated before any code (Step 2)

- **Invariants.** `docs lifecycle` never writes `Lifecycle: archived`; no byte
  of an archive-subtree document is written by `lifecycle` or a free-form
  `relate`; TARGET is never written by a free-form edge; no bullet `docs
  check` would reject or re-read differently is written (D6 + R4);
  recognized-verb `relate` is byte-for-byte unchanged; the archive
  candidate set is unchanged; every active document the INDEX summary
  counts is rendered; `docs stamp` never rewrites a complete block that
  fails the config. Writes go through the surgical editors and
  `atomic_write`; one reindex at most, none on a no-op or dry-run;
  refusals are zero-byte and print under `--quiet`; one `--json` shape for
  preview and apply, none on a refusal; a bare `parse()` keeps the
  built-ins; no verb starts refusing a document `docs check` accepts;
  `docs check` itself is unchanged.
- **Forbidden shortcuts.** Special-casing `pairs-with`, a literal or a
  fixture; test-only branches; weakening a test or gate; re-entering another
  verb's command function; any spelling reaching `archived`; writing TARGET;
  relaxing `docs check`; a new dependency or a hand-rolled equivalent of an
  in-project helper; speculative output; fixing *Follow-ups* item 9.
- **Visible product drivers.** Phase 5: `tests/test_lifecycle_plan.py`, the
  free-form section of `tests/test_relate_plan.py`, `tests/test_model.py`.
  Phase 6: `tests/test_cli_lifecycle.py`, the free-form section of
  `tests/test_cli_relate.py`, the D10 locks across the walking verbs and
  `docs stamp`. Phase 7: `tests/test_body_from.py`, `tests/test_skill.py`,
  `tests/test_packaging.py` and the lifecycle help test.
- **Explicit non-product gates.** `docs check .` from the docs root; the
  INDEX snapshot `cmp`; Phase 8's `comm` / AST proof against `e48adb9`, the
  naming lint and the hand-applied mutation smoke; Phase 7's scoped
  stale-wording grep; Phase 9's dogfood, wheel probe replay and
  real-tree-untouched check; Phase 10's `--help` / `cli.md` / CHANGELOG
  parity.
- **Risk and gates.** Standard: ruff, ruff format, mypy, the full suite,
  `docs check`, mirror and snapshot `cmp`; property, fuzz and mutation smoke
  selected; coverage and a hidden suite not configured.
- **Mock policy.** No new mock; failure paths use a real malformed sibling, a
  sentinel INDEX and inode checks.
- **Taste anchors.** `_cmd_project_set` for `docs lifecycle`; the relate
  plan / apply family for the free-form path; `check_doc` for D10;
  `render_index` extended, not replaced; `_cmd_stamp`'s validate-all-first
  loop; reuse of `set_metadata_field`, `atomic_write`, `_refresh_index`,
  `_is_archived_rel`, `validate_lifecycle` / `validate_role`, `parse_date`;
  stdlib only; `cli.py` +310 to +510 lines.

### Actions taken

All in `src/docs_cli/cli.py`; no test or fixture changed
(`git diff 3e2c3ca -- tests/` is empty).

1. **Grammar.** `_RELATE_VERB_RE = re.compile(r"[a-z][a-z0-9-]*")` and
   `relate_verb_in_grammar(verb)` (`fullmatch`, `[0-9]`), beside
   `inverse_verb`, whose docstring now says `_cmd_relate` writes a
   free-form verb one-sided instead of refusing it.
2. **`parse(text, path, root, *, config=None)`.** With a config it
   validates against `config.lifecycles` / `config.roles` and parses
   `Updated:` in `config.date_format`; with None, the built-ins and ISO.
   The same `validate_lifecycle`, `validate_role` and `parse_date` calls, so
   messages are byte-identical. The stale *Raises* paragraph ("uses
   BUILTIN_STATUSES and BUILTIN_ROLES … callers should re-validate via the
   walker") is rewritten. No call site changed — that is Phase 6.
3. **One-sided relate plan.** `RelatePlan.inverse: str | None` (docstring:
   None for a free-form verb; `edits` is `(source,)` then). `plan_relate`
   keeps its signature: a verb neither recognized nor in the grammar raises
   `ValueError`; a free-form edge whose SOURCE is archived raises explicitly
   — not left to `_plan_relate_edit`, which never fires with a reason given
   and the edge already present; SOURCE is staged through the existing
   `_plan_relate_edit`, and TARGET only when `inverse` is not None, so a
   free-form plan never reads TARGET. `relate_plan_to_json`'s docstring now
   describes both record shapes; `apply_relate_plan`, `_rollback_relate`
   and `_print_relate_lines` needed no change (they iterate `plan.edits`).
4. **Lifecycle records and planner.** `LifecycleEdit` / `LifecyclePlan`
   (frozen, `RelateEdit`-style docstrings) after `RelatePlan`;
   `plan_lifecycle`, `apply_lifecycle_plan` and `lifecycle_plan_to_json`
   after `relate_plan_to_json`. The planner dedupes on `rel` (first
   occurrence), refuses the four programming-error states, reads and parses
   `root / rel` with the config, and stages `Lifecycle:` then `Updated:`
   through `set_metadata_field`; apply writes only `set` edits,
   sequentially, with `atomic_write`; the record's keys follow P1.1's order.

### Decisions / issues

- **Deferred to Phase 6, as planned** (pressure-test item 1):
  `_resolve_relate_endpoint`'s `config` / `parse_endpoint` parameters,
  `_stamp_config_failure`, `_print_lifecycle_lines` and `_cmd_lifecycle`.
  Changing the endpoint resolver's signature now would force an edit to
  `_cmd_relate`, which this phase's exit forbids, and each of the others has
  no Phase-5 consumer. The Phase 4 follow-through listed
  `_stamp_config_failure` under Phase 5 as sequencing, not contract.
- `plan_relate`'s programming-error `ValueError` text changed with the guard
  (it now names the grammar); no test or caller reads it — the CLI refuses
  first.

### Verification

- `.venv/bin/ruff check .` clean; `.venv/bin/ruff format --check .` — 50
  files formatted; `.venv/bin/mypy src/ tests/` — no issues in 51 files.
- `.venv/bin/python -m pytest -q` — **1656 collected, 126 failed, 1530
  passed** (the exit criterion). The 24 ids that flipped are exactly the
  Phase-5 family — 10 in `tests/test_lifecycle_plan.py`, 11 in
  `tests/test_relate_plan.py` (the 5 grammar-guard parametrizations, the
  pure fuzz, the five plan / apply / record tests), 3 in
  `tests/test_model.py` — and no id outside the baseline's failing set
  fails. `pytest tests/test_lifecycle_plan.py tests/test_relate_plan.py
  tests/test_model.py` — 54 passed.
- `git diff 3e2c3ca -- tests/` empty; the `cli.py` diff has no hunk in
  `_cmd_relate` or `_build_parser` (`lifecycle` is not a subcommand). Diff:
  `cli.py` +235 / −55 so far.
- `docs check .` exit 0; mirrors and the INDEX snapshot byte-identical.

## Phase 6 — Implement Offline/Core Path — 2026-10-27

### Objective

Wire both verbs and D10: register `docs lifecycle` over the Phase-5
planner; route `_cmd_relate`'s free-form verbs to the one-sided path with
D5's endpoint rules, D6's grammar and R4; pass the tree's config at the seven
existing `parse()` sites; render extension-role groups; and make `docs
stamp` refuse a complete block that fails the config.

### Actions taken

All in `src/docs_cli/cli.py`; no test or fixture changed.

1. **D10 at the seven sites.** `config=config` at `walk`, `query_docs`,
   `_cmd_archive`'s primary, `_known_projects` and `_cmd_project_set`;
   `_resolve_relate_endpoint(raw, root, root_resolved, config, *,
   parse_endpoint=True)` parses with the config unless told not to (the
   missing / directory / outside-root checks are unchanged); `_cmd_stamp`
   (item 3). Docstrings of `walk`, `query_docs` and `_known_projects` say
   so, and `archive_dir_date`'s note that `parse()` hardcoded the ISO date
   now says D10 ended that.
2. **`render_index`** iterates `role_order + sorted(set(role_groups) -
   set(role_order))` — the built-in order untouched, extension groups after
   it, alphabetically; *Format details* updated. No `Config` field.
3. **Stamp refusal.** `_stamp_config_failure(text, config)` beside
   `_cmd_stamp`: `None` unless `parse_metadata_block` succeeds and
   `Lifecycle`, `Role`, `Updated` are each one non-empty value (`Project`
   not required); then `validate_lifecycle`, `validate_role`, `parse_date`
   in `parse()`'s order, returning the first failure's message. `_cmd_stamp`
   parses with the config and, on a failure, refuses with the P1.5 message
   inside the validate-all-first loop — before `--dry-run` and before any
   write of the batch. Its classification comment now names the three
   outcomes.
4. **Free-form `relate`.** R1 replaces the recognized-only check with
   `relate_verb_in_grammar` (the recognized verbs are inside the grammar, so
   a recognized verb never reaches it) and sets `free_form = inverse_verb(…)
   is None`; SOURCE resolves with the config, TARGET with
   `parse_endpoint=not free_form`; R4 (free-form only) runs after TARGET
   resolves and before the self-edge check; R2 (free-form only) runs after
   the self-edge check and before the `--reason` shape check; the
   archived-endpoint `--reason` rule became `elif not free_form:`. Date,
   plan, apply, print, reindex and record are unchanged — they already
   iterate `plan.edits`. Recognized-verb paths and messages are untouched,
   and *Follow-ups* item 9 stays unfixed.
5. **`docs lifecycle`.** A `lifecycle` subparser (after `stamp`, before
   `project`; `parents=[common]`, `args` `nargs="+"` with metavar `file ...
   state`, a local `--json` with relate's wording) carrying its **final**
   description — `archived` is never a target and `docs archive` owns that
   move — so `test_lifecycle_help_documents_the_grammar_and_flags` flipped
   here, as the Phase-4 log allowed. `_dispatch` routes it.
   `_print_lifecycle_lines` prints P1.1's three lines. `_cmd_lifecycle`
   follows `_cmd_project_set` and `_cmd_relate`'s tail in P1.1's order:
   L1 → strict root (L2/L3) → config (L4) → L5 before L6 → the L7
   archive-subtree pre-pass over every target → L8–L10 in argument order,
   parsing `root / rel` with the config → L11 → plan → dry-run or
   all-unchanged returns 0 after the lines and the `applied: false` record →
   otherwise sequential writes, the lines, one reindex with the exclusion
   predicate (L12 on failure, record still emitted).

### Decisions / issues

- **Transient RED, expected and named** (pressure-test item 2): registering
  `lifecycle` turns the pre-existing
  `tests/test_skill.py::test_every_named_verb_is_a_real_subcommand` RED
  ("skill body fails to name every real docs verb — missing
  ['lifecycle']") until Phase 7 adds the skill row — the surface-parity gate
  enforcing itself.
- **Two parses per named lifecycle document — accepted** (pressure-test
  item 4). `_cmd_lifecycle` parses every named document for L10 before it
  can judge L11, and the frozen `plan_lifecycle` signature reads and parses
  again. The constraint's intent — no whole-tree pre-flight, cost bounded by
  the named files — holds.
- **Uncaught `OSError`** on a lifecycle read or write raises a traceback,
  as in `project set` and `touch` (pressure-test item 11; OQ-2's sequential
  writes add no new surface). An accepted limitation.
- **A wrap-sensitive help assertion, recorded.**
  `test_lifecycle_help_documents_the_grammar_and_flags` asserts the phrase
  `docs archive` in `docs lifecycle --help`, which argparse wraps to the
  terminal width. Not edited here — it passes at the pipe default (78),
  and no width-pinning workaround was added to the help text; noted for
  the reviewers. *(Corrected at Phase 8: this note first said the phrase
  stays whole "at every width tried except 140". Re-measured, it splits at
  50, 119, 120 and 145 and stays whole at 60–100, 140, 160 and 200, so the
  test failed in a wide terminal. Phase 8 fixed the assertion — DEF-1.)*
- Help text cites its provenance (`(M30 — D1–D3)`), as `stamp`, `project
  set` and `relate` cite theirs.

### Verification

- ruff, ruff format, mypy clean.
- `.venv/bin/python -m pytest -q` — **1656 collected, 9 failed, 1647
  passed** (the exit criterion), verified by name: the eight Phase-7 ids —
  `tests/test_body_from.py::test_skill_sidecar_example_yields_its_edge[relate-add-on-an-existing-sidecar]`
  and `[body-from-group-at-creation]`,
  `tests/test_skill.py::test_skill_routes_lifecycle_and_free_form_edges_through_verbs`,
  `::test_shipped_surface_no_longer_says_free_form_verbs_are_hand_edited`,
  and the four packaging pins (`test_a3_project_version_is_2_1_0`,
  `test_b1_wheel_builds`, `test_b2_sdist_builds`,
  `test_c2_docs_version_is_2_1_0`) — plus the transient guard above. No
  other id outside the baseline's failing set fails.
- `test_relate_recognized_pair_still_writes_both_halves_unchanged`, every
  pre-existing relate id, and the archive invariance locks
  (`test_cascade_candidates_match_when_edges_were_written_by_relate`,
  `test_strand_refusal_fires_on_a_child_of_written_by_relate`) — GREEN.
- `git diff 3e2c3ca -- tests/` empty; `cli.py` +568 / −84 against
  `3e2c3ca`.
- `docs check .` exit 0 on this tree; mirrors and the INDEX snapshot
  byte-identical.

## Phase 7 — Update Tool/Wrapper Layer — 2026-10-27

### Objective

Reconcile every parallel surface with the shipped behaviour — help text,
specs, the bundled skill and its references, README, version, CHANGELOG —
and record the milestone's outcomes and follow-ups in `feedback-log.md`.

### Actions taken

1. **Help text** (`src/docs_cli/cli.py`, strings and docstrings only).
   The `relate` namespace and `relate add` / `relate remove` describe both
   kinds of verb — "free-form verbs stay hand-edited" and "Only the six
   recognized verbs are accepted" are gone; `VERB`'s help names the literal
   grammar `[a-z][a-z0-9-]*`; `TARGET`'s says "for a free-form verb, any
   existing file under the root; never read"; `--reason` is "REQUIRED for a
   recognized pair with an endpoint under the archive subtree". The comment
   above the namespace and `_add_relate_subverb`'s docstring (R1's text, no
   stale "eight tests" count) are updated. `docs stamp`'s description gains
   the refusal; the `--body-from` help gains one clause for the leading
   `Related:` group (it fit); `main()`'s verb list gains `lifecycle` and the
   free-form half of `relate`.
2. **Specs.** `docs/cli.md` and `docs/convention.md` already carried the
   frozen 2.1 text from Phase 1. Reconciled against `docs lifecycle --help`,
   `docs relate [add|remove] --help` and `docs stamp --help`: no divergence,
   so neither spec nor its mirror changed in this phase.
3. **Bundled skill** (`src/docs_cli/skill/`). `SKILL.md`: the description
   gains "change a doc's lifecycle, link docs with a Related: edge" and
   `lifecycle` in its verb list (743 → 813 of 1024 characters); a `docs
   lifecycle <file>... <state>` verb-table row; the relate row now "Link
   docs, or repair a reciprocal pair", covering free-form edges and the
   grammar; *Three things never to hand-edit* routes `Lifecycle:` to `docs
   lifecycle` (keeping to-or-from `archived` with `docs archive`) and
   `Related:` edges to `docs relate add` / `remove`; *Quality artifacts*
   links a report with `docs relate add <companion> references <report>`.
   `references/use-cases.md`: the sidecar row is the **frozen P1.3 text,
   verbatim** (checked byte-for-byte against the task plan); new Greenfield
   rows *Promote or change a doc's lifecycle* and *Link related docs with a
   free-form edge*; the "`relate` refuses to edit them" sentence now says
   `relate` writes them one-sided. `references/adoption-playbook.md`: the
   sidecar bullet is the **frozen P1.3 bullet, verbatim**, including its
   fenced `sh` group form and the M15 — C4 heuristic description.
   `references/quality-artifacts.md` *Linking reports* names `docs relate
   add`. The M16-pinned phrases are untouched.
4. **README** *Commands*: a `docs lifecycle <file>... <state>` line; the
   `docs relate` line covers free-form edges.
5. **Version and CHANGELOG.** `pyproject.toml` → `version = "2.1.0"`, then
   `.venv/bin/pip install -e ".[dev]"` (the runbook form; `docs --version`
   and `importlib.metadata` both report 2.1.0 — the host's
   `~/.local/bin/docs` stays 2.0.0, untouched). CHANGELOG gains `## 2.1.0 —
   UNRELEASED` above `## 2.0.0` with P1.7's Added / Changed ×3 / Fixed
   bullets and the closing "unchanged" sentence — **UNRELEASED** per D9 (the
   M19 → M20 practice), superseding the runbook's "date it at Phase 10"
   (pressure-test item 6). The packaging pins were edited in Phase 2.
6. **`feedback-log.md`.** The 2026-10-26 vocabulary entry and the 2026-08-15
   `date_format` entry are **CLOSED at M30 Phase 7** (implemented,
   unreleased, pending the 2.1.0 publish), each with a dated closure note;
   the vocabulary entry's reproduction claimed `docs list` prints the error
   on stderr — the closure note corrects it (it prints nothing, as Step 1
   measured). The 2026-10-26 promotion entry gains a dated note recording
   the Q1–Q9 / D1–D10 answers and the implemented-unreleased status; it
   stays **open** until the suite pin moves. Follow-ups **1, 2, 3, 7, 8 and
   9** are registered as six separate open, unowned 2026-10-27 entries
   (Step 2 planning OQ-1, conductor-resolved: item 1 too), and the task
   plan's *Follow-ups* rows point at them. Item 9 was re-measured against
   the 2.1.0 development build on a throwaway tree: the recognized verb
   still plans the injecting bullet (`--dry-run` exit 0), the free-form
   verb refuses it with R4 (exit 2).

### Decisions / issues

- **The transient RED closed.**
  `tests/test_skill.py::test_every_named_verb_is_a_real_subcommand` is GREEN
  again now that the skill names `docs lifecycle`.
- **Stale-wording grep — empty.** Scoped to the shipped and live surfaces
  (pressure-test item 5): every `src/docs_cli/skill/**/*.md`,
  `docs/cli.md`, `docs/convention.md`, `README.md`, `CHANGELOG.md`
  (whitespace-normalised, so a phrase broken across lines still counts) and
  the output of `docs relate --help`, `docs relate add --help` and `docs
  relate remove --help`, for "free-form verbs stay hand-edited", "refuses
  to edit them" and "Only the six recognized verbs" — no match. The
  milestone trio and `archive/` quote the phrases on purpose and are out
  of scope.
- **Observation for the operator — a host skill tracks this repository.**
  `~/.claude/skills/docs-local-source-backup-20260525-134621` is a
  pre-existing symlink (dated 2026-05-23) to this repository's
  `src/docs_cli/skill`, so the bundled-skill edits above are visible to
  agents on this host at once, while the host binary `~/.local/bin/docs`
  is still 2.0.0 and has no `docs lifecycle`. Not touched (hard boundary:
  `~/.claude/skills` is read-only to this run); surfaced in the Step 2
  return for the operator.

### Verification

- ruff, ruff format, mypy clean.
- `.venv/bin/python -m pytest -q` — **1656 passed**, 0 failed (the exit
  criterion; the known `test_d4_install_skill_is_idempotent` flake did not
  recur).
- Both mirrors byte-identical to the specs; the INDEX snapshot identical;
  `docs check .` exit 0.
- `docs lifecycle --help`, `docs relate --help`, `docs relate add|remove
  --help`, `docs stamp --help` and `cli.md` agree (read side by side).

## Phase 8 — Run Tests (GREEN) — 2026-10-28

Step 2 was interrupted after Phase 7 and resumed here from `1683116`. A
fresh planner re-verified Phases 5–7 first: 1656 passed; ruff, format and
mypy clean; `docs check` exit 0; mirrors and the INDEX snapshot
byte-identical; `git diff 3e2c3ca HEAD -- tests/` empty. Every P1.9 symbol
exists, and every `parse()` call site passes `config`.

### Objective

Run every product and quality gate with exact counts. Prove mechanically,
against `e48adb9`, that every pre-existing test id is present and GREEN.
Record the property, fuzz, schema and security results, the hand-applied
mutation smoke and the mock audit.

### Working contract, restated at the resume (Phases 8–10)

- **Invariants.** These are unchanged from Phase 5:
  - `docs lifecycle` never writes `Lifecycle: archived` and never takes a
    source under the archive subtree or one already reading `archived`;
  - a free-form `relate` writes only SOURCE, never TARGET, and never a bullet
    `docs check` would re-read differently (D6, R4);
  - recognized-verb `relate` and the archive candidate set are byte-for-byte
    unchanged;
  - a no-op or `--dry-run` writes nothing, INDEX included, and a real change
    reindexes once;
  - refusals are zero-byte and print under `--quiet`;
  - a bare `parse()` keeps the built-ins, and no verb starts refusing a
    document `docs check` accepts;
  - `docs stamp` never rewrites a complete block that fails the config;
  - `docs check` itself does not change.
- **Forbidden shortcuts.**
  - Special-casing `pairs-with`, a test literal or a fixture name.
  - Test-only branches, or weakening a test or a selected check to reach
    GREEN; erroneous expectations are corrected under Check calibration
    instead.
  - Re-entering another verb's command function.
  - Writing TARGET, relaxing `docs check`, or adding a dependency.
  - Fixing *Follow-ups* item 9 (D4).
  - Simplification that silently reduces adequacy (QUALITY PLAN).
- **Visible product drivers.** The full suite of 1656 ids. Its behavioural
  core is `tests/test_cli_lifecycle.py`, `tests/test_lifecycle_plan.py`,
  `tests/test_cli_relate.py`, `tests/test_relate_plan.py`,
  `tests/test_cli_stamp.py`, `tests/test_index.py`,
  `tests/test_cli_index.py`, `tests/test_model.py`, `tests/test_walker.py`,
  the D10 locks in the other walking-verb modules, `tests/test_body_from.py`,
  `tests/test_skill.py`, `tests/test_skill_refs.py` and
  `tests/test_packaging.py`.
- **Explicit non-product gates.**
  - `docs check .` from the docs root, and the INDEX snapshot `cmp`.
  - The id `comm` and AST proof against `e48adb9`, the naming lint and the
    43-mutant hand-applied smoke.
  - The docs-wide stale-wording grep.
  - The Phase-9 flows F1–F10: the wheel build and probe replay, the closeout
    comparison, the D10 trees, the reindex identity and the runtime table.
  - The Phase-10 surface-parity reconciliation, placeholder grep and
    archive-readiness preview (on a copy).
- **Risk and gates.** Standard, operator-confirmed (Q8). Selected gates:
  - ruff, ruff format, mypy and the full suite;
  - `docs check`, and `cmp` of both mirrors and the INDEX snapshot;
  - property and fuzz smoke, the mutation smoke and the mock audit.
  - Coverage, a hidden suite and mutation tooling are **not configured**.
- **Mock policy.** No new or expanded mock. Failure paths use a real
  malformed sibling, a sentinel INDEX and inode checks. Mutation runs use
  extracted copies, not mocks.
- **Taste anchors.** Unchanged:
  - `_cmd_project_set` for `docs lifecycle`;
  - the relate plan/apply family for the free-form path;
  - `check_doc` for D10;
  - `render_index` extended, not replaced;
  - `_cmd_stamp`'s validate-all-first loop;
  - reuse of the in-project editors and validators, and stdlib only.

### Resume decisions (conductor-resolved, Step 2 resume planning)

The resume planner raised six questions. The conductor resolved all six under
Standard-risk authority; each is binding for Phases 8–10.

| Id | Question | Decision |
|---|---|---|
| S2R-OQ-1 | *Follow-ups* item 6: write a `parent-of` back-edge on `milestone-plan.md`? | **(b) Decline and close.** Nothing consumes the edge: it is free-form, not a cascade verb, and unvalidated. The tracker cell plus `child-of: milestone-plan.md` already give two-way navigation, and the `parent-of` list is a superseded convention. *Home* cell updated at Phase 10. |
| S2R-OQ-2 | *Follow-ups* item 10 ("state a binding decision once"): where does it live? | **(c)** An open, unowned candidate-convention entry in `feedback-log.md`, offered as a taste anchor at the next milestone's setup. `CLAUDE.md` is not edited. *Home* cell updated at Phase 10. |
| S2R-OQ-3 | A non-equivalent mutation survivor in an authored test | **(a)** Correct the authored test's fixture so it exercises the guard its docstring claims, keep the same id, and re-prove the kill. A survivor that only a contract change could kill would be a STOP condition. |
| S2R-OQ-4 | DEF-1, the help assertion that depends on terminal width | **(a)** Normalise whitespace in the assertion (precedent: `tests/test_skill.py`'s stale-wording test), keep the behaviour asserted, and correct the Phase 6 note. |
| S2R-OQ-5 | Phase 9 oracles | Use a same-interpreter v2.0.0 extraction for reindex identity and for runtime (`git diff v2.0.0 e48adb9 -- src/ pyproject.toml` is empty). Build the hand-linked twin with `--body-from` `Related:` groups, plus a verb-only rewrite of the real trio. No metadata hand-edits. |
| S2R-OQ-6 | Phase 10 doc accuracy beyond the two named items | **(a)** Fix every listed stale item in `architecture.md` and `test-strategy.md`. Record the M25-era `relate` module-map omission as an in-passing correction. Add no `stamp` or `project set` module-map line and no D10 critical path. |

### Gates

| Gate | Result |
|---|---|
| `git status --porcelain` at `1683116` | empty |
| `.venv/bin/ruff check .` | All checks passed |
| `.venv/bin/ruff format --check .` | 50 files already formatted |
| `.venv/bin/mypy src/ tests/` | no issues in 51 source files |
| `.venv/bin/python -m pytest -q --tb=line -rfxXEs` at `1683116` | **1656 passed**, 0 failed / skipped / xfailed / xpassed / errors, 82.7 s |
| the same after the two test corrections below | **1656 passed**, 0 otherwise, 82.6 s; ruff, format and mypy clean again |
| `docs check .` from the docs root | no violations, exit 0 |
| `cmp` of both mirrors and of the INDEX snapshot | byte-identical |

The known `test_d4_install_skill_is_idempotent` flake did not recur.

### Mechanical no-regression proof against `e48adb9`

The ids were collected from a `git archive e48adb9` extraction instead of a
worktree, so `.git/worktrees` was not touched (M28a nit F8). Conftest puts the
extracted `src/` ahead of the editable path, so this is equivalent. The
pytest runs used `-p no:cacheprovider`.

| Measure | Result |
|---|---|
| ids at `e48adb9` / at HEAD | **1504** / **1656** |
| removed (`comm -23`) | exactly the four renamed ids: `test_relate_unknown_verb_refuses`, `test_stamp_supersedes_invalid_existing_block`, `test_a3_project_version_is_2_0_0`, `test_c2_docs_version_is_2_0_0` |
| their new ids | all four collected |
| added (`comm -13`) | **156** |
| pre-existing ids failing | **0**, because the suite has no failures |
| AST diff of the 1345 pre-existing `tests/*.py` functions, nested ones included | CHANGED: exactly the authoritative list — `test_archive_renders_the_witness_in_the_trees_date_format`, `_attic_tree` and its nested `_attic_tree._doc`, the quiet and case-variant relate tests, `test_b1_wheel_builds`, `test_b2_sdist_builds`. REMOVED: the four renamed ids. |
| `git diff --numstat e48adb9 -- tests/fixtures` | the INDEX snapshot, `stamp/raw-invalid-block.md`, and the four `vocab-extension/` files only |

With 0 failures, every pre-existing id is GREEN, under its own id or its new
one. The two Phase-8 corrections below change authored tests only, so they
do not appear in the AST diff.

### Naming lint

The lint splits each of the 156 added ids into tokens and flags milestone,
decision, clause, phase, step and review tokens. It flags three ids, and all
three were already accounted for:

- `c2` in `test_c2_docs_version_is_2_1_0`: `tests/test_packaging.py`'s own
  check-number scheme (OQ-15).
- `m27` and `m28a` in the `[vocab-extension]` ids of two pre-existing sweeps
  (`test_check_tree_pre_m27_…`, `test_check_tree_pre_m28a_…`). These tokens
  come from the pre-existing function names, not from a name written here.
  Step 1 judged them harmless (claude-N9) and did not rename them.

`milestone` in `test_milestone_setup_needs_no_hand_edit` is a domain word.

### Property, fuzz, schema and security results

All of these are tests already in the suite; nothing was added.

- **Property / stateful — 16 passed.**
  - *Idempotence:* the five-state round trip (applying twice equals applying
    once), `test_lifecycle_already_in_state_writes_zero_bytes_and_skips_reindex`
    (a sentinel INDEX stays byte-identical) and
    `test_relate_free_form_is_idempotent`.
  - *Round trip:*
    `test_relate_free_form_add_then_remove_restores_the_original_bytes`,
    both with and without an existing `Related:` group.
  - *No `status-drift`:*
    `test_lifecycle_round_trips_every_top_level_state_without_status_drift`
    for draft, active, blocked, done and superseded.
  - *Write footprint:*
    - a free-form operation writes one managed document;
    - a mixed lifecycle batch writes only the changed documents (checked by
      inode);
    - the two lifecycle and relate dry-run tests write nothing;
    - a stamp refusal in a batch writes no file;
    - a recognized pair still writes both halves.
- **Fuzz — 24 passed, seed `20261027`.**
  - The pure predicate: 300 generated valid verbs, 300 generated invalid
    verbs and `""`.
  - The in-process CLI fuzz: 30 generated valid verbs plus one invalid verb
    for each of 11 refused categories.
  - The 22-case boundary table.
- **Schema — passed.** Both lifecycle key-set locks (CLI and planner) are
  closed. Both free-form records have `inverse: null` and one edit. The
  recognized-pair record is locked value for value.
- **Security — passed.**
  - The verb-injection refusals `[a-colon | a-newline | a-carriage-return]`.
  - R4 `[a-line-break | a-carriage-return | a-leading-space |
    a-trailing-space]`.
  - TARGET outside the root, and a TARGET symlink escaping the root.

### Hand-applied mutation smoke — 45 / 45 killed (43 planned, plus 2 variants)

Mutation tooling is not configured, so this follows the M28a precedent:
- Each of 6 workers had its own `git archive HEAD` extraction. The runner is
  `p8/mutate.py` in the session scratchpad, run with `-I`.
- For each mutant it asserted the old text on the addressed line of pristine
  `1683116`, rewrote that one line, and ran the subset without `-x` and with
  `DOCS_CLI_NO_UPDATE_CHECK=1`. It then restored the file.
- A control run of every unmutated subset passed first:
  - LC 46 and RL 128;
  - IX 28 and ST 27;
  - D10 514.
- `tests/test_packaging.py` is in no subset, because its symlink test cannot
  pass from a copy.
- The D10 subset also includes `tests/test_lifecycle_plan.py`, where M34's
  expected killer lives; the plan's subset left that file out.
- The repository was never mutated.

| Id | Target | Mutation (line at `1683116`) | Killed by (first killers; count) |
|---|---|---|---|
| M01 | 1 | `if state == "archived":` → `if False:` (8557) | `test_lifecycle_refuses_archived_as_a_target_state`, the refusal-order test, the quiet test (3) |
| M02 | 1 | `allowed = config.lifecycles - {"archived"}` → `config.lifecycles` (8564) | `test_lifecycle_treats_a_capitalised_archived_as_an_unknown_state`, `test_lifecycle_unknown_state_names_the_allowed_states` (2) |
| M03 | 1 | planner state guard drops `state == "archived" or` (5463) | `test_plan_lifecycle_refuses_archived_as_a_state` (1) |
| M04 | 2 | CLI L7 pre-pass `_is_archived_rel` → `False` (8586) | `test_lifecycle_refuses_a_document_under_the_archive_subtree`, `test_lifecycle_batch_with_one_archived_document_writes_nothing` (2) |
| M05 | 2 | planner archive-subtree guard → `False` (5474) | **survived at `1683116` (DEF-2)**; after the fixture correction: `test_plan_lifecycle_refuses_a_source_under_the_archive_subtree` (1) |
| M06 | 3 | CLI L11 `lifecycle == "archived"` → `False` (8621) | `test_lifecycle_refuses_an_active_tree_document_already_marked_archived` (1) |
| M07 | 3 | planner current-`archived` guard → `False` (5479) | `test_plan_lifecycle_refuses_a_source_already_marked_archived` (1) |
| M08 | 4 | `free_form = …` → `False` (8379) | the archived-SOURCE, archived-TARGET, non-Markdown and malformed-Markdown TARGET tests, … (9) |
| M09 | 4 | `free_form = …` → `True` (8379) | `test_relate_malformed_endpoint_exits_1`, `test_relate_archived_endpoint_without_reason_refuses`, `test_relate_archived_no_op_still_requires_reason`, the E11-direction test (4) |
| M10 | 4 | planner `if inverse is not None:` → `True` (5193) | `test_relate_free_form_add_writes_only_the_source_bullet`, `…_is_idempotent`, `…_write_rewrites_exactly_one_managed_document`, … (15) |
| M11 | 5 | planner `doc.lifecycle == state` → `False` (5481) | the mixed batch (inode), the sentinel no-op, the dry-run, the closed-key record, … (9) |
| M12 | 5 | `if changed:` → `True` (5254) | `test_relate_add_twice_is_a_no_op`, `test_relate_remove_twice_is_a_no_op`, `test_relate_add_completes_only_the_missing_half`, … (14) |
| M13 | 6 | lifecycle no-op guard → `if args.dry_run:` (8646) | `test_lifecycle_already_in_state_writes_zero_bytes_and_skips_reindex` (1) |
| M14 | 6 | relate no-op guard → `if args.dry_run:` (8480) | `test_relate_no_op_does_not_reindex`, `test_relate_add_is_a_no_op_against_a_non_canonical_bullet`, `test_relate_free_form_matches_a_non_canonical_existing_bullet`, … (5) |
| M15 | 7 | `fullmatch` → `re.match(r"[a-z][a-z0-9-]*$", …)` (1032) | boundary `[refuses-a-trailing-newline]`, both fuzzers, the planner guard `[a-trailing-newline]` (4) |
| M16 | 8 | `[a-z0-9-]` → `[a-z\d-]` in `_RELATE_VERB_RE` (1021) | 24 — mostly through the message: R1 prints `_RELATE_VERB_RE.pattern`, so every full-message assertion fails. See M16b. |
| M16b | 8 | message-preserving variant: the matcher (1032) → `re.fullmatch(r"[a-z][a-z\d-]*", verb)` | boundary `[refuses-an-arabic-indic-digit]` and `[refuses-a-fullwidth-digit]`, both fuzzers (4) — the semantic kill |
| M17 | 7 | first class `[a-z]` → `[a-z0-9]` in `_RELATE_VERB_RE` (1021) | 24, through the message as for M16. See M17b. |
| M17b | 7 | message-preserving variant: the matcher (1032) → `re.fullmatch(r"[a-z0-9][a-z0-9-]*", verb)` | boundary `[refuses-a-leading-digit]`, both fuzzers (3) — the semantic kill |
| M18 | 7 | R1 guard → `False` (8371) | `test_relate_verb_outside_the_free_form_grammar_refuses`, the case-variant and quiet tests, the boundary, … (25) |
| M19 | 2 | CLI R2 → `False` (8412) | `test_relate_free_form_refuses_an_archived_source_even_when_nothing_would_change`, the refusal-order test (2) |
| M20 | 2 | planner free-form archived-SOURCE guard → `False` (5178) | `test_plan_relate_free_form_refuses_an_archived_source` (1) |
| M21 | R4 anchors | R4 predicate → `"\n" in target_rel` (8396) | R4 `[a-carriage-return]`, `[a-leading-space]`, `[a-trailing-space]` (3) |
| M22 | `parse_endpoint` | `parse_endpoint=not free_form` → `True` (8387) | the non-Markdown and malformed-Markdown TARGET tests, R4 cases (6) |
| M23 | `--reason` branch | `elif not free_form:` → `else:` (8431) | `test_relate_free_form_archived_target_needs_no_reason_and_is_untouched` (1) |
| M24 | dedupe | `if rel in seen:` → `False` (5471) | both duplicate-path tests (2) |
| M25 | 9 | `parse()` config vocabulary → built-ins (1273) | the `test_model` config tests, the walker, index, list and touch locks, … (15) |
| M26 | 9 | `parse()` config date format → ISO (1273) | `test_parse_with_a_config_rejects_the_iso_spelling_on_a_non_default_tree`, the date-format index lock, … (12) |
| M27 | 9 | `walk` drops `config=` (1367) | the walker, index and touch locks, … (18) |
| M28 | 9 | `query_docs` drops `config=` (4026) | `test_list_includes_a_doc_in_an_extension_lifecycle`, … (2) |
| M29 | 9 | `_cmd_archive` primary drops `config=` (7260) | `test_archive_accepts_a_primary_in_an_extension_state`, the witness and walking-verb `bad-date` tests (3) |
| M30 | 9 | `_known_projects` drops `config=` (8082) | `test_project_set_knows_a_project_carried_only_by_an_extension_vocabulary_doc` (1) |
| M31 | 9 | `_cmd_project_set` drops `config=` (8206) | `test_project_set_rewrites_a_doc_in_an_extension_state` (1) |
| M32 | 9 | `_resolve_relate_endpoint` drops `config=` (8309) | `test_relate_accepts_an_endpoint_in_an_extension_lifecycle`, `test_relate_refuses_an_endpoint_dated_outside_the_trees_date_format`, … (3) |
| M33 | 9 | `_cmd_lifecycle` drops `config=` (8611) | `test_lifecycle_promotes_an_extension_state_on_a_non_default_date_format_tree` (1) |
| M34 | 9 | `plan_lifecycle` drops `config=` (5478) | the same CLI test, `test_plan_lifecycle_accepts_a_configured_extension_state` (2) |
| M35 | 9 | `_cmd_stamp` drops `config=` (8798) | `test_stamp_keeps_a_document_in_a_configured_extension_state`, both date-format stamp tests (3) |
| M36 | 9 | lifecycle `Updated:` → `date.today().isoformat()` (8634) | `test_lifecycle_promotes_an_extension_state_on_a_non_default_date_format_tree` (1) |
| M37 | 10 | role loop → `role_order` only (1434) | `test_render_index_orders_extension_roles_alphabetically_after_built_ins`, `test_index_renders_an_extension_role_group_after_the_built_in_roles` (2) |
| M38 | 10 | extension groups before the built-ins (1434) | the same two (2) |
| M39 | 10 | extension groups in first-seen order (1434) | `test_render_index_orders_extension_roles_alphabetically_after_built_ins` (1) |
| M40 | 11 | completeness test → `if True:` (8713) | every stamp refusal test (6) |
| M41 | 11 | completeness test → `if False:` (8713) | `test_stamp_freshly_stamps_an_incomplete_block_even_with_an_out_of_vocabulary_value` and the pre-existing fresh-stamp tests (12) |
| M42 | 11 | completeness also requires `Project:` (8713) | `test_stamp_refuses_a_complete_block_without_a_project_line_with_zero_bytes` (1) |
| M43 | 11 | final `return None` → `return "complete block"` (8721) | `test_stamp_restamps_a_complete_block_whose_related_bullet_is_malformed` (1) |

All eleven matrix targets are covered, as are the four extra points the
QUALITY PLAN named: the R4 anchors, `parse_endpoint`, the recognized-only
`--reason` branch, and dedupe. No mutant is equivalent.

**Why M16b and M17b were added.** M16 and M17 had identical 24-test killer
sets, including cases neither mutation changes in meaning, such as
`[refuses-an-empty-verb]`. The cause is that the R1 refusal interpolates
`_RELATE_VERB_RE.pattern`, so any edit to the pattern changes the message.
For M16 and M17, then, only the pure-predicate fuzz was clean evidence. The
two variants change only the matcher and leave the message alone. Each is
killed by exactly the semantic boundary cases and both fuzzers, so the
grammar's character classes are guarded independently of the message text.

### Mock audit

- `git diff e48adb9 -- tests/ | grep '^+'` for `monkeypatch`, `mock`,
  `patch(`, `setattr` or `setenv` matched two docstrings only. Both say "no
  mock": `tests/test_cli_lifecycle.py`'s L12 test and the in-process CLI
  fuzz.
- `capsys` in the fuzz is output capture on the real `cli.main` path.
- **0 new or expanded mocks.**
- Failure paths use a real malformed sibling (L12), a sentinel INDEX and
  inode checks.

### Defects found and corrected (Check calibration)

Two authored Phase-2 tests were wrong in how they checked, not in what they
expected. Each fix keeps the behaviour asserted and the id. No pre-existing
test was edited, and `src/` did not change.

- **DEF-1 — a help assertion that depended on terminal width.**
  - **Where:** `tests/test_cli_lifecycle.py::test_lifecycle_help_documents_the_grammar_and_flags`
    asserted the two-word phrase `docs archive` against raw `docs lifecycle
    --help` output, which argparse wraps to `COLUMNS`.
  - **Measured:**
    - it failed at widths 50, 119, 120 and 145, and passed at 60–100, 140,
      160, 200 and the 78-column pipe default (shown on an unedited HEAD
      extraction: `COLUMNS=120` fails, `COLUMNS=78` passes);
    - so it pinned incidental layout.
  - **Fix (S2R-OQ-4):**
    - assert against `" ".join(proc.stdout.split())`, the precedent in
      `tests/test_skill.py`'s stale-wording test;
    - a comment explains why;
    - it now passes at 50, 78, 119, 120 and 145, and still fails if the
      phrase is missing.
  - The Phase 6 note's width claim is corrected in place.
- **DEF-2 — a planner guard masked by another.**
  - **Where:** `tests/test_lifecycle_plan.py::test_plan_lifecycle_refuses_a_source_under_the_archive_subtree`
    built its archive-subtree source with `Lifecycle: archived`.
  - **Problem:** with the subtree guard removed (M05), the current-`archived`
    guard still raised `ValueError`, so the test passed. Its docstring
    claimed "the guard behind L7".
  - **Fix (S2R-OQ-3 (a)):**
    - the fixture now reads `done`: a status-drifted document under
      `archive/`, which only the location guard can refuse;
    - the docstring says so;
    - M05 was re-run on an extraction carrying the corrected test and is
      **KILLED** by exactly this test (1 failed / 45 passed). Both runs are in
      the table above.
  - No contract change was needed.

### Verification

- The full gate is re-run at the commit: ruff, format, mypy, **1656
  passed**, `docs check .` exit 0, both mirrors and the INDEX snapshot
  byte-identical.
- `git diff 1683116 -- src/` is empty. The only test changes are the two
  corrections above.

## Phase 9 — Integrate / Accept / Dogfood — 2026-10-28

### Objective

Run the primary use case and every acceptance flow unattended, on throwaway
trees only.

### Setup and safety

- **Where it ran.** Every flow ran on a `cp -a` copy of `docs/` or on a tree
  built from scratch, all under the session scratchpad's `p9/`. Before every
  command, a guarded `cd` asserted that the working directory was under that
  folder and was neither the repository nor its `docs/`. This guards against
  M28a's Phase-9 incident.
- **Environment.**
  - Every docs-cli call ran with `DOCS_CLI_NO_UPDATE_CHECK=1`, with
    `XDG_CACHE_HOME` and `XDG_STATE_HOME` pointing into the scratch folder,
    and with stdin from `/dev/null`. No prompt was possible.
  - The editable build is `.venv/bin/docs` (2.1.0).
- **The oracle (S2R-OQ-5).** It is a `git archive v2.0.0 src` extraction,
  run by the same interpreter. `git diff v2.0.0 e48adb9 -- src/
  pyproject.toml` is empty, so this is exactly the product code before M30.
  - Its `--version` prints the venv's installed metadata (2.1.0), so the
    label is not evidence of which code ran.
  - Its behaviour is: `lifecycle` is an "invalid choice", and its `docs_cli`
    imports resolve to the extraction.
- **Before starting.** `git status --porcelain` was empty, and HEAD was
  `42f9eae`.

### Flows and results

**F1 — the primary use case, on a copy of this tree.** These are the
`create-milestones` setup steps, run through verbs only:
1. `docs new milestone dogfood-probe` and `docs new log dogfood-probe-impl`,
   then `docs new spec dogfood-probe-test-matrix`;
2. six `docs relate add … pairs-with …` calls, linking each companion both
   ways;
3. `docs relate add dogfood-probe.md child-of milestone-plan.md`, then
   `… implements charter.md`;
4. `docs lifecycle dogfood-probe.md dogfood-probe-test-matrix.md
   dogfood-probe-impl.md active --json`;
5. `docs check .`.

Results:
- **Every call exited 0**, with zero hand-edits and zero prompts.
- `docs check .` reported "no violations found".
- The before/after manifest shows exactly the three added documents plus a
  changed `INDEX.md`. `milestone-plan.md` and `charter.md` are byte-identical,
  because a free-form TARGET is never written.
- The record was `applied: true`, `index_refreshed: true`, with three `set`
  edits from `draft`.
- **Run again**, the same `docs lifecycle` call printed "no change — … is
  already active" three times and returned `applied: false` and
  `index_refreshed: false`. The manifest, INDEX included, was unchanged.

**F2 — both Agent Playbook Suite probes against three builds.** These are
exact replicas of the product-test probes:
- the help probe matches `\{([a-z0-9,\-]+)\}` on `docs --help` and looks for
  `lifecycle`;
- the relate probe uses an empty `.docs.toml` and two `docs new spec` files,
  then runs `docs relate add a.md pairs-with b.md --dry-run` from the tree's
  cwd with no `--root`; it must exit 0 with an unchanged manifest.

| Build | help probe | relate probe |
|---|---|---|
| editable `.venv/bin/docs` (2.1.0) | **True** | **True** (exit 0, unchanged) |
| local wheel `docs_cli-2.1.0-py3-none-any.whl` in a fresh venv (`python -m build`, `pip install --no-index`; `docs --version` → `docs 2.1.0`) | **True** | **True** (exit 0, unchanged) |
| control: host `~/.local/bin/docs` (2.0.0) | False | False (exit 2, `unknown verb 'pairs-with'`) |

The control shows each probe can reject a wrong build. The wheel venv's
`docs install-skill --dest <scratch>/skill`, with XDG redirected, installed
a skill identical to the bundled one (`diff -ru` against
`src/docs_cli/skill` is empty). Its state file landed in the redirected
`XDG_STATE_HOME`, not on the host.

**F3a — closeout invariance, `relate`-linked vs hand-linked (D7).**
- **The twin.** A twin copy built the same trio through the supported D8
  route: `docs new … --body-from -`, each body opening with a `Related:`
  group carrying the same edges. It was then promoted with the same `docs
  lifecycle` call, and `docs check` was clean.
- **Byte identity.** The three twin files are **byte-identical** to the
  `relate`-linked ones, which is stronger than the record identity required.
- **Preview records.** Both `docs archive dogfood-probe.md --cascade-dry-run
  --json` and the scoped `--cascade-only 'dogfood-probe-*'` preview give
  records that are identical across the two trees (`json.load` equality).
  - The unscoped preview lists three candidates: both companions
    (`pairs-with`) and `milestone-plan.md` (`child-of`).
  - The scoped preview selects exactly the two companions.
- **Applied closeout.** Applying `--cascade-only 'dogfood-probe-*' --reason
  dogfood` on both exited 0. The run reported "3 candidate(s): 2 selected, 1
  not selected", and `docs check` was clean. Afterwards `diff -r` of the two
  trees is **empty**.

**F3b — the real M30 trio**, the "real milestone trio" generalization
category.
- **Setup.** Copies A and B. In B, verbs only: read each trio document's
  edges and `Updated:` through `parse()` (read-only), then:
  - `docs relate remove` every `Related:` bullet, 13 across the three
    documents, which drops each group;
  - then `docs relate add` each one back in its original order with
    `--date` equal to the document's `Updated:`.
- **The rewrite.** All 26 calls exited 0. Each trio file in A and B is
  byte-identical, and so is the whole tree (`diff -rq` empty, INDEX
  included).
  - The trio's `Updated:` was today, because Phase 8 touched it, so `--date`
    matched the default here.
  - The byte identity shows that dropping and re-creating a group restores
    it exactly.
- **Preview records.** Both previews are identical across A and B:
  `--cascade-dry-run` and `--cascade-only 'lifecycle-and-free-form-relate-*'`.
  - The unscoped preview's candidates are `milestone-plan.md` (`child-of`),
    both companions, `cli.md`, `convention.md`, `test-strategy.md` and
    `status.md` (`pairs-with`).
  - The scoped preview selects exactly the two companions.
  - The leg-2 strands are body links only, in `feedback-log.md` (3),
    `milestone-plan.md` (1) and `status.md`.
- **Applied closeout.** Applying the scoped closeout on both exited 0, with
  `docs check` clean. `diff -r A B` is **empty** afterwards.

**F3c — leg 1 (strand refusal).**
- On a fresh copy, `docs relate add status.md child-of
  lifecycle-and-free-form-relate.md` exited 0.
- The scoped closeout then exited 2 with: "status.md is still active and
  declares 'child-of: lifecycle-and-free-form-relate.md', which this
  operation would archive; refusing before any write … zero bytes written".
- The manifest is unchanged.

**F4 — the archive boundary**, on a copy of the post-F1 tree. A manifest
was compared around every refusal, and each refusal left the tree
byte-identical.

| Call | Exit | Message (abridged) |
|---|---|---|
| `docs lifecycle dogfood-probe.md archived` | 2 | L5: "'archived' is not a lifecycle target — docs archive <file> moves lifecycle and location together" |
| `docs lifecycle dogfood-probe.md Archived` | 2 | L6: "unknown state 'Archived'; expected one of: active, blocked, done, draft, superseded" |
| `docs lifecycle archive/2026-08-16/m29-pypi-publish-2-0-0.md active` | 2 | L7: "… is under the archive subtree (read-only)" |
| `docs lifecycle stray.md active` (setup write: a stray active-tree file reading `Lifecycle: archived`, removed afterwards) | 2 | L11: "… (status-drift); refusing — only docs archive sets archived" |
| `docs relate add archive/2026-08-16/m29-pypi-publish-2-0-0.md references charter.md` | 2 | R2: "a free-form edge is never written to an archived document" |
| `docs relate add dogfood-probe.md references archive/2026-08-16/m29-pypi-publish-2-0-0.md` (no `--reason`) | **0** | bullet added; the archived TARGET is byte-identical; `docs check` clean |

**F5a — an extension-vocabulary tree**, built from scratch. Its config is
`add_lifecycles = ["shipped"]`, `add_roles = ["adr"]` and `[exclude] dirs =
["drafts"]`.
- **The E7 replay — every call exited 0:**
  - `docs lifecycle a.md shipped`, `docs index .` and `docs touch b.md`;
  - `docs list --json`, which lists `a.md` as `shipped`;
  - `docs relate add b.md precedes a.md`, which parses both endpoints and
    writes `follows: b.md` into `a.md`;
  - `docs archive a.md --cascade-dry-run --json` and `docs mv a.md a2.md
    --dry-run`.
- **The primary use case with state `shipped`** (trio, six `pairs-with`
  calls, one `docs lifecycle … shipped`): every call exited 0.
- **The extension role.** After `docs new adr decision-x` and `docs index .`,
  the INDEX renders `### Active — Adr` after the Spec, Milestone and Log
  groups.
- **Stamp.** `docs stamp a.md`, on the `shipped` document carrying a
  `Related:` edge, printed "already stamped — refreshed Updated:", and the
  file is byte-identical because `Updated:` was already today.
- **Contrast.** The v2.0.0 oracle's `stamp a.md` on a twin reproduces E12:
  - `shipped` → `draft` and `spec` → `notes`;
  - `Related:` is demoted to a body `Migrated-Related:` group;
  - then it exits 2 on its own reindex.
- `docs check .` exited 0.

**F5b — a non-default `date_format` tree**, built from scratch with
`[archive] dir = "attic"` and `date_format = "%d-%m-%Y"`.
- `docs new` writes `Updated: 28-10-2026`.
- The trio, six `relate add` calls, `docs lifecycle … active`, `docs index
  .` and `docs touch` all exited 0, so E8 is fixed. The lifecycle record's
  `date` is `28-10-2026`.
- `docs archive old.md --reason dogfood` exited 0, writing
  `attic/28-10-2026/old.md` with `Updated:` and `Archived:` both
  `28-10-2026`.
- `docs check .` exited 0.

**F5c — the E11 shape**, on the same tree. A setup write added `iso.md`
with `Updated: 2026-10-27`, which is ISO on a `%d-%m-%Y` tree.
- `docs check .` exited 2 with `[bad-date] Updated: malformed date
  '2026-10-27' (expected %d-%m-%Y)`.
- `docs index .` exited 2 with the same diagnosis, prefixed by the path.
- `docs list --json` omits `iso.md`.
- `docs stamp iso.md` exited 1 with the P1.5 refusal, naming `Updated:`.
- The manifest is unchanged across all four.

**F6 — the remaining generalization categories**, on the extension tree.
Every call exited 0 except the two refusals, and `docs check` ended clean.
- **Nested:** `docs new spec sub/deep`.
- **Duplicate spellings in one batch:** `docs lifecycle sub/deep.md
  ./sub/deep.md sub/../sub/deep.md active --json` gives one edit.
- **Non-canonical TARGET:** `./b.md` and then `sub/../b.md` give one
  canonical bullet, `references: b.md`; the second call is a no-op.
- **Non-Markdown TARGET:** `coverage.xml` (setup write) is accepted and left
  untouched.
- **Excluded TARGET:** `drafts/scratch.md` is accepted and left untouched.
- **Boundary verbs:** `a`, `x--y`, `a1b` and `v-` are accepted.
- **Refused verbs:** `Pairs-With` and `see also` exit 2 with the R1 message
  and zero bytes.

**F7 — this tree reindexes byte-identically.** On twin copies, on the same
day, under the same interpreter:
- `NEW index .` and `OLD index .` give identical `INDEX.md` files, and both
  are identical to the committed INDEX;
- `list --json` is identical, and `check --json` is identical (`[]`);
- `diff -rq` of the two trees is empty.

The tree has 16 active and 61 archived documents.
`tests/test_cli_index.py::test_index_output_matches_frozen_snapshot` pins
the same fact in the suite.

**F8 — runtime** (recorded, not budgeted). Median of 5 runs, each series on
its own fresh copy of this tree, same interpreter, update check off.

| Command | v2.0.0 | 2.1.0 |
|---|---|---|
| `check .` | 257 ms | 277 ms |
| `index .` | 120 ms | 119 ms |
| `list --json` | 108 ms | 112 ms |
| `touch a b c` (three documents plus a reindex, the nearest analogue) | 125 ms | 129 ms |
| `lifecycle a b c draft\|active`, alternating | — | 131 ms |
| `relate add\|remove … precedes …` (recognized, two documents) | 121 ms | 124 ms |
| `relate add\|remove … references …` (free-form, one document) | — | 121 ms |

- **`docs lifecycle`** costs about `touch` plus 2 ms, even though it parses
  each named document twice (accepted at Phase 6).
- **Free-form `relate`** is no slower than a recognized pair.
- **`check .`** was re-measured over two 15-run rounds: v2.0.0 263 / 275 ms
  and 2.1.0 280 / 281 ms. That is +6 to +17 ms, while v2.0.0's own spread
  between rounds is 12 ms.
  - `check`'s path (`check_tree` → `_iter_doc_texts` → `check_doc`) has no
    M30 change, and its output is byte-identical (F7).
  - Process start-up (`--version`) is +1 to +4 ms for the larger module.
  - The remainder was not isolated, and is recorded as measured.

**F9 — the real tree and the host stayed untouched.**
- After the flows, `git status --porcelain` is empty and HEAD is still
  `42f9eae`.
- `~/.cache/docs-cli` is unchanged (mtime and size), and
  `~/.local/state/docs-cli` is absent before and after.
- Nothing under `~/.claude/skills` changed.

**F10 — backward liveness walk.** Starting from each observable output and
working back through the P1.9 map:
- **`docs lifecycle` record and lines.** Each `LifecyclePlan` /
  `LifecycleEdit` field has a reader:
  - `state` and `date_str` feed the record and lines;
  - `rel`, `before` and `change` feed the record and lines; `change` also
    filters `apply` and the no-op check;
  - `path` and `new_text` feed `apply_lifecycle_plan`.
- **The free-form record.** `RelatePlan.inverse` drives `plan_relate`'s
  branch and is read by `relate_plan_to_json`.
- **Grammar.** `relate_verb_in_grammar` is read by `plan_relate` and R1.
  `_RELATE_VERB_RE` is read by the predicate and by R1's message.
- **TARGET resolution.** `parse_endpoint` is passed `not free_form` for
  TARGET and keeps its default for SOURCE.
- **Config.** `parse(config=)` is read at nine sites.
- **Stamp.** `_stamp_config_failure` is read by `_cmd_stamp`'s refusal.
- **INDEX.** The extension role groups appear in `INDEX.md`.

Nothing is produced but unconsumed.

### Decisions / issues

- **Setup writes, named as such.** These were deliberate fixture writes on
  throwaway trees, never part of the use case:
  - `stray.md` (F4, L11);
  - `iso.md` (F5c);
  - `coverage.xml` and `drafts/scratch.md` (F6);
  - each `.docs.toml` of the from-scratch trees.
  No metadata block was hand-edited in any flow.
- **The F3 twin needed no hand-edit (S2R-OQ-5).** The D8 `--body-from` route
  built it, and it came out byte-identical to the `relate`-linked trio.
- **The F3b real-trio leg-2 strands** are body links that the closeout
  reports and does not refuse. Step 3's own preview is the authoritative
  one, and Phase 10 re-runs this preview on the final tree.

### Verification

- Every flow ran unattended with no stdin, on throwaway trees, and every exit
  code is recorded above.
- The real tree is untouched: porcelain empty, HEAD `42f9eae`.
- Both probes pass on the editable build and on the local wheel, and fail on
  2.0.0.
- The closeout records are identical in F3a and F3b.
- The runtime is recorded.

## Phase 10 — Quality, Docs, Refactor — 2026-10-28

### Objective

- Run a light `/simplify` pass over the milestone's `cli.py` diff; Step 3
  runs the second pass.
- Close `architecture.md` and `test-strategy.md`.
- Write the D9 hand-off note into its live home and decide *Follow-ups*
  items 6 and 10.
- Complete the taste triage and the boundary sweep, reconcile the shipped
  surface, and write the completion summaries.

### `/simplify` — light pass, scoped to `git diff 3e2c3ca -- src/docs_cli/cli.py`

**Why it runs now.** At Standard risk, Step 3's code changes get no
dual-provider review. Anything material therefore lands before the Step 2
review, so the reviewers see the code that ships. The pass is light because
the new code already reads like its anchors.

**Baseline** at `53bd069`:
- 1656 passed;
- mutation smoke 45/45, property 16, fuzz 24;
- 0 mocks;
- Standard-risk gate set.

**Taken — S1: `_stamp_config_failure`'s completeness test, from clever to
obvious.**
- **Before.** The three fields were unpacked from a generator over a
  generator, which turned every non-`str` value into `""`, followed by a
  truthiness test:

  ```python
  lifecycle, role, updated_raw = (
      value if isinstance(value, str) else ""
      for value in (metadata.get(label) for label in ("Lifecycle", "Role", "Updated"))
  )
  if not (lifecycle and role and updated_raw):
  ```

- **After.** Three named `.get`s and one explicit
  `isinstance(…, str) and …` test.
- **Why the truthiness test could go.** Measured first:
  `parse_metadata_block` stores an inline value only when it is non-empty
  (`if rest_stripped:`). A label with an empty value is parsed as a bare
  label, `()`, exactly as a multi-valued group is a tuple. So "complete" is
  exactly "each of the three is a `str`".
- **Behaviour.** Identical: the same three outcomes for every block shape.
  mypy narrows all three to `str` without a cast, and the diff is +6 / −6.
- **Re-proof.** M40–M43 were re-applied to the simplified code on an
  extraction:
  - M40 (`if True:`) is killed by 6 tests;
  - M41 (`if False:`) by 12;
  - M42 (also requiring `Project:`) by 1;
  - M43 (a final `return "complete block"`) by 1.
  These are the same counts as Phase 8, so no adequacy was lost. The stamp
  suite (27) passed before and after.

**Evaluated and rejected:**

| Candidate | Rejected because |
|---|---|
| S2 — collapse `_cmd_lifecycle`'s two `resolve().relative_to()` passes (the L7 pre-pass and the L8–L10 loop) | It is verbatim parity with the `_cmd_project_set` anchor, which has the same pre-pass and per-target resolution. The separate pre-pass is what makes L7 independent of argument order, so that it outranks a missing or malformed sibling (pinned by the refusal-order test). |
| S3 — a shared dry-run / no-op / apply / reindex / emit tail for `relate` and `lifecycle` | There are only two sites, and their plan and printer types differ. A helper taking callables would add indirection to read two exit paths. |
| S4 — factor the `index_refreshed` capture block | It appears twice, and the pre-existing verbs keep their own return-2 tail inline. |
| S5 / S6 — drop `plan_lifecycle`'s second parse, or its `ValueError` guards | Both are frozen by P1.9 and pinned by the planner tests. The guards are what M03, M05 and M07 kill, and the second parse was accepted at Phase 6, with its runtime recorded in Phase 9 F8. |
| S7 — rewrite the R4 predicate `len((rel + "x").splitlines()) != 1 or rel != rel.strip()` | Its literal text is frozen in P1.2, and its semantics ("any boundary `str.splitlines()` recognises") are stated in `cli.md`. |

### Documentation closed

- **`architecture.md`** — demanded by the milestone:
  - the module map gains `relate` and `lifecycle` lines;
  - a new **`### lifecycle (M30)`** section covers the planner, the
    sequential apply with no rollback (the `project set` precedent), the
    L1–L12 order and "never `archived`";
  - **`### relate (M25)`** gains the one-sided free-form path: the grammar,
    `inverse=None` with SOURCE staged alone, TARGET never read via
    `parse_endpoint=False`, R4, R2, and no `--reason` or `Revision:` for an
    archived TARGET.
- **`architecture.md`** — accuracy fixes (S2R-OQ-6):
  - `model` gives the real signature, `parse(text, path, root, *,
    config=None)`, with one sentence on D10;
  - `walker` says each document is parsed with the tree's config;
  - *Display order* and *INDEX renderer format* › *Role group order* both
    say extension-role groups follow the built-ins, alphabetically;
  - the module-map size is `~9.5k` lines (9,498).
- **In-passing correction (the M28a precedent).** The module map had lacked
  a `relate` line since M25. The new line covers both M25 and M30. No
  `stamp` or `project set` line was added, because nothing demands one.
- **`test-strategy.md`:**
  - *Critical paths* gains two entries: "no `docs lifecycle` transition
    reaches `archived`" (target, archive-subtree source and active-tree
    `archived` source) and "a free-form `relate` rewrites exactly one managed
    document";
  - *Fixture sources* gains `vocab-extension/` (OQ-8), with its contents and
    the six walking-verb modules that copy it.
- **D9 hand-off note.** It lives in the open 2026-10-26 `feedback-log.md`
  entry, which is outside the archive scope.
  - Re-checked at Phase 10 start: the tracker has one row (100,
    `lifecycle-and-free-form-relate`, `active`), so no publish milestone is
    registered (*Follow-ups* item 4).
  - The dated `Hand-off (2026-10-28, M30 Phase 10)` bullet gives the
    publish milestone three tasks:
    1. publish per `release-runbook.md`, dating `## 2.1.0` and stripping
       its "A separate publish milestone ships it." sentence;
    2. re-run both probe replicas and the raw probes against the
       PyPI-served wheel;
    3. refresh the host skills per `CLAUDE.md`, noting the host symlink
       `~/.claude/skills/docs-local-source-backup-20260525-134621`.
  - It also names what the suite pin-bump PR must do: bump
    `DOCS_CLI_VERSION`, replace the hand-edit prescriptions, delete
    `verbless-metadata-edits.md`, and drop Step 0's up-front approval. After
    that, the CI guard must read `lifecycle verb: True` / `free-form relate:
    True`.
  - The entry stays open until that suite release ships.
- ***Follow-ups* item 6 — declined and closed** (S2R-OQ-1): no `parent-of`
  edge is written on `milestone-plan.md`. The *Home* cell gives the reason.
- ***Follow-ups* item 10 — registered** (S2R-OQ-2) as the open, unowned
  2026-10-28 *Candidate project convention: state a binding decision once*
  entry in `feedback-log.md`. It will be offered as a taste anchor at the
  next milestone's setup; `CLAUDE.md` is untouched. Item 4's *Home* cell
  now points at the hand-off.

### Surface-parity reconciliation

- **Read side by side.** These agree with the CHANGELOG `## 2.1.0 —
  UNRELEASED` section and with `cli.md`:
  - `docs --help` (the brace list holds `lifecycle`);
  - `docs lifecycle --help`;
  - `docs relate --help`, `docs relate add --help` and `docs relate remove
    --help`;
  - `docs stamp --help` (the refusal);
  - `docs new --help` (the leading `Related:` group).
- **One wording checked.** `docs lifecycle --help` says "Validate-all-first
  atomic semantics", but the writes are sequential with no rollback. The
  phrase matches `docs project set --help` verbatim, and `cli.md` states the
  exact contract (validate everything, then an atomic tmpfile + fsync +
  rename per document, in argument order). It is kept for anchor parity.
- **Stale-wording grep — empty.** It checked 17 surfaces, whitespace-
  normalised: every skill `.md`, `cli.md`, `convention.md`, README,
  CHANGELOG, `architecture.md`, `test-strategy.md`, and five `--help`
  outputs.
- The CHANGELOG stays **UNRELEASED** (D9).
- Neither `cli.md` nor `convention.md` changed in Phase 10, so the mirrors
  needed no re-copy.

### Taste triage

| Source | Finding | State | Reason |
|---|---|---|---|
| Step 0 review | claude-T1 | partially fixed, remainder waived | as recorded in *Step 0 review-pass-001* |
| Step 0 review | claude-T2, claude-T3 | fixed | *Step 0 review-pass-001* |
| Step 1 review | claude-T1, T2, T3 | fixed | *Step 1 review-pass-001* (the agreement sweep 53 → 1 id; CLI fuzz invalid set fixed at 11; `_symbol` removed) |
| Step 1 review | claude-T4 (D10 restated six or more times) | waived for M30 | the restated copies were all corrected; registered as a candidate convention (*Follow-ups* item 10, `feedback-log.md` 2026-10-28) |
| Step 2 self-triage | provenance tags in help text (`(M30 — D1–D3)`) | kept (not a finding) | pattern adherence: `stamp`, `project set` and `relate` cite their milestone the same way |
| Step 2 self-triage | two parses per named lifecycle document | waived | frozen `plan_lifecycle` signature (P1.9); cost bounded by the named files; measured in Phase 9 F8 (`lifecycle` 131 ms against `touch` 129 ms) |
| Step 2 self-triage | uncaught `OSError` on a lifecycle read or write | waived | the `project set` / `touch` precedent; OQ-2's sequential writes add no new surface |
| Step 2 self-triage | DEF-1, a help assertion that depended on terminal width | fixed | Phase 8 |
| Step 2 self-triage | DEF-2, a planner-guard test masked by another guard | fixed | Phase 8 (M05 re-proven) |
| Step 2 self-triage | the R1 message interpolates `_RELATE_VERB_RE.pattern`, so the grammar's character-class mutants are killed mostly through the message | kept, with evidence | the message is frozen to name the grammar, and deriving it from the one pattern keeps the two from drifting; the message-preserving variants M16b and M17b show the semantic cases kill independently |
| Step 2 self-triage | S1, the completeness test written as a nested generator | fixed | `/simplify`, above |
| Step 2 self-triage | patch bloat | explained | `cli.py` is +629 / −116, net **+513**, against the anchor's +310 to +510 — at the top of the range, for one verb, one widened verb, D10 at nine sites, the stamp refusal and the frozen docstrings. Tests are +3,105 / −96 against the anchor's +900 to +1,300, driven by authored-id breadth (156 ids), as both Step 1 reviewers judged. |

Every taste finding is fixed, kept with a reason, or waived with a reason.
None is untriaged.

### Boundary sweep (liveness, P1.9 outputs → consumers)

| Output | Consumer(s) |
|---|---|
| `parse(..., *, config=None)` | the nine call sites (`walk`, `query_docs`, `plan_lifecycle`, `_cmd_archive`, `_known_projects`, `_cmd_project_set`, `_resolve_relate_endpoint`, `_cmd_lifecycle`, `_cmd_stamp`). Every production call passes `config`. The `None` default is contractual — the D10 deliverable requires "a bare call keeping the built-in defaults" (C22), pinned by `test_bare_parse_keeps_the_built_in_defaults`, and the pre-existing parser tests call it bare. |
| `_RELATE_VERB_RE`, `relate_verb_in_grammar` | `plan_relate`'s guard; `_cmd_relate`'s R1 test and message |
| `RelatePlan.inverse: str \| None` | `plan_relate`'s one-sided branch; `relate_plan_to_json`'s `inverse` (C15) |
| `_resolve_relate_endpoint(..., config, *, parse_endpoint=True)` | `_cmd_relate`: SOURCE with the default, TARGET with `not free_form` |
| `LifecycleEdit.path` / `.new_text` | `apply_lifecycle_plan` |
| `LifecycleEdit.rel` / `.before` / `.change` | the `--json` record and the human lines; `.change` also drives `apply`'s filter and the all-unchanged no-op |
| `LifecyclePlan.state` / `.date_str` / `.edits` | the record (`state`, `date`, `edits`) and the lines |
| `lifecycle_plan_to_json`, `_print_lifecycle_lines` | `_cmd_lifecycle` (C15, P1.1) |
| `_stamp_config_failure` | `_cmd_stamp`'s P1.5 refusal |
| `render_index`'s extension groups | `INDEX.md` (C25) |
| doc sections written this step | the `architecture.md` and `test-strategy.md` sections are demanded by the milestone's Phase 10 or by accuracy (S2R-OQ-6); the hand-off by D9; the candidate entry by S2R-OQ-2 |

No speculative output is left, so no ledger entry is needed.

### Archive-readiness preview

On a fresh copy of the final docs tree, `docs archive
lifecycle-and-free-form-relate.md --cascade-dry-run --cascade-only
'lifecycle-and-free-form-relate-*' --json` exited 0 and wrote nothing.
- **Selected:** exactly the two companions,
  `lifecycle-and-free-form-relate-impl.md` and
  `lifecycle-and-free-form-relate-test-matrix.md`.
- **Not selected:** `milestone-plan.md` (`child-of`), and `cli.md`,
  `convention.md`, `test-strategy.md` and `status.md` (`pairs-with`).
- **No leg-1 refusal.**
- **Leg-2 strands:** body links only — `feedback-log.md` 3,
  `milestone-plan.md` 1 (the tracker cell) and `status.md` 6.

Phase 9 F3b applied the same scoped closeout to a copy and ended `docs check`
clean. Step 3's own preview remains the authoritative one.

### Verification

| Gate | Result |
|---|---|
| `.venv/bin/ruff check .` / `ruff format --check .` / `mypy src/ tests/` | clean (50 files formatted; no issues in 51) |
| `.venv/bin/python -m pytest -q --tb=line -rfxXEs` | **1656 passed**, 0 failed / skipped / xfailed / errors, both before S1 and after the Phase 10 edits |
| `tests/test_cli_stamp.py`, and M40–M43 on the simplified code | 27 passed; 4/4 killed |
| `docs check .` from the docs root | no violations, exit 0 |
| `docs check . --stale 14` (information only) | exit 1, with five `stale` warnings on evergreen documents (`charter.md`, `definition-of-ready.md`, `dual-status-adr.md`, `release-runbook.md`, `vocab-adr.md`) — two fewer than at Step 1, because `architecture.md` and `test-strategy.md` were updated |
| `cmp` of both mirrors and of the INDEX snapshot | byte-identical |
| stale-wording grep (17 surfaces) | empty |

## Milestone completion summary

**Implementation complete (2026-10-28) — Phases 1–10 done.** The tracker row
stays `active`. The Step 2 review (*Step 2 review-pass-001*) and the Step 3
second simplify pass and archive closeout remain. 2.1.0 is **unreleased**;
publishing is a separate milestone (*Follow-ups* item 4; the hand-off is in
`feedback-log.md`).

- **What shipped** (branch `lifecycle-and-free-form-relate/phases-5-10` on top
  of Step 1):
  - `docs lifecycle <file>... <state>` (D1–D3), which never reaches
    `archived` (D2);
  - one-sided free-form `docs relate add|remove` within `[a-z][a-z0-9-]*`
    (D4–D6, R1–R4), with recognized verbs byte-for-byte unchanged;
  - archive-candidate and strand invariance, locked (D7);
  - the `--body-from` leading-`Related:` route, locked and documented (D8);
  - `parse()` honouring the tree's vocabulary and `date_format` at every
    call site, extension-role INDEX groups, and the `docs stamp` refusal
    (D10);
  - surface parity across the help text, `cli.md`, `convention.md`, the
    bundled skill and its byte-identical references, README and CHANGELOG
    (D9);
  - version 2.1.0, with `## 2.1.0 — UNRELEASED`.
- **Evidence headline:**
  - **1656 passed**, 0 failed, with ruff, format, mypy and `docs check`
    clean. Mirrors and the INDEX snapshot are byte-identical.
  - Every pre-existing id is present and GREEN under the authoritative old →
    new mapping (the id and AST proof against `e48adb9`).
  - Mutation smoke **45/45 killed**. Property 16 and fuzz 24 passed. 0 mocks.
  - The primary use case was dogfooded with zero hand-edits, and both suite
    probes pass on a locally built wheel.
  - Closeout records are identical for `relate`-linked and hand-linked
    trios, including the real M30 trio.
  - This tree reindexes byte-identically to v2.0.0.
- **Corrections and decisions in Step 2:**
  - DEF-1 and DEF-2 (authored checks corrected under Check calibration,
    Phase 8);
  - the message-preserving grammar mutants M16b and M17b (Phase 8);
  - S1 (`/simplify`, Phase 10);
  - S2R-OQ-1 … 6 (conductor-resolved at the Step 2 resume planning, Phase 8).
- **Open follow-ups**, all in `feedback-log.md` and none blocking:
  - the 2026-10-26 promotion entry, open until the suite pin moves, which
    carries the hand-off;
  - six 2026-10-27 entries (*Follow-ups* items 1, 2, 3, 7, 8, 9);
  - the 2026-10-28 candidate convention (item 10).
- **Remaining risks:**
  - the intermittent `test_d4_install_skill_is_idempotent` segfault (not
    seen in Step 2; no product code involved);
  - the host symlink `~/.claude/skills/docs-local-source-backup-20260525-134621`
    → this repository's skill, which shows the 2.1 skill beside the 2.0.0
    host binary until the publish milestone refreshes the host (Phase 7
    observation, in the hand-off).
