# M30 — Lifecycle verb and free-form `docs relate` — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-10-27

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
- Mock audit: no mocks planned.
- Adequacy results: pending.
- Taste triage: Step 0 review-pass-001 triaged — GPT: sound, no subjective
  findings; claude-T1 partially fixed and the remainder waived with reason;
  claude-T2 and claude-T3 fixed; patch bloat in line with precedent (see the
  pass entry below). Step 1 review-pass-001 triaged — GPT: sound, no
  subjective findings; claude-T1, T2 and T3 fixed; claude-T4 waived with
  reason (*Follow-ups* item 10).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-10-27 | Freeze against the answered Q1–Q9: `docs lifecycle`'s `*files, <state>` grammar, state vocabulary (built-ins plus `add_lifecycles` extensions, minus `archived`), refusal set and order, idempotence and single-reindex rules, output lines and `--json` record; free-form `relate`'s grammar (`[a-z][a-z0-9-]*`, D6), endpoint rules (archived SOURCE refused, archived TARGET never written, any existing file as TARGET), one-sided write and record; recognized-verb byte stability; the `--body-from` sentence; D10's config-aware `parse()` signature and how its sites obtain the config (D10's behaviour, `render_index` placement and `docs stamp` refusal are frozen); the stamp refusal's message; argparse's leading-hyphen handling; the upgrade note's three D10 changes; the surface list; the Phase-5 signatures. |
| 2. Write Tests (RED) | Complete | 2026-10-27 | New `tests/test_cli_lifecycle.py`; free-form additions to `tests/test_cli_relate.py` and `tests/test_relate_plan.py`; archive-invariance locks; the `--body-from` lock; skill parity; the 2.1.0 pin; both suite-probe replicas; D10's vocabulary, date-format, `render_index` and `docs stamp` locks; the pre-existing tests edited exactly as the task plan's *Pre-existing tests that change* lists. |
| 3. Create Data/Fixtures | Complete | 2026-10-27 | Inline `tmp_path` builders for every write-then-compare case; archive invariance by copying `archive-neighborhood` / `movelink-strand` and re-linking through `relate`; for D10, one `vocab-extension/` tree with the sweep registration updated, inline builders for every non-default `date_format` case, and the `tests/test_cli_mv.py` `_attic_tree` correction. |
| 4. Run Tests (RED Baseline) | Complete | 2026-10-27 | Classified failure set against the 1504-test baseline; every GREEN-at-baseline lock named; every pre-existing id accounted for through the plan's explicit old → new mapping. No operator checkpoint (Standard). |
| 5. Update Base Interfaces | Pending | — | Free-form verb validator; one-sided relate planning; lifecycle plan record and pure planner; D10's config-aware `parse()` signature with a built-in default — wired nowhere. |
| 6. Implement Offline/Core Path | Pending | — | Register `docs lifecycle`; route free-form verbs in `_cmd_relate` with D5's endpoint rules and D6's grammar; pass the tree's config at the seven `parse()` call sites and the new verbs' sites (D10). |
| 7. Update Tool/Wrapper Layer | Pending | — | Argparse help; `cli.md` / `convention.md`; the skill body, *Three things never to hand-edit*, `use-cases.md`, the adoption playbook's stale heuristic line; both mirrors; README verb list; 2.1.0 pin and `## 2.1.0 — UNRELEASED` with both behaviour changes in the upgrade note; dated notes on the 2026-10-26 promotion entry and on the two config-blindness entries D10 closes. |
| 8. Run Tests (GREEN) | Pending | — | Full gate with exact counts; mechanical no-regression proof against the 1504 pre-existing ids; property checks, grammar fuzz, hand-applied mutation smoke; mock audit. |
| 9. Integrate / Accept / Dogfood | Pending | — | The primary use case on a throwaway copy of this tree with zero hand-edits; both suite probes against the editable build and a local wheel; closeout-plan identity for a `relate`-linked trio; the extension-vocabulary and non-default-`date_format` trees (D10); this tree reindexing byte-identically; runtime recorded. |
| 10. Quality, Docs, Refactor | Pending | — | `/simplify`; close `architecture.md` and `test-strategy.md`; hand-off note to a live home; taste triage and boundary sweep; completion summaries. |

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

## Milestone completion summary

_Not complete._
