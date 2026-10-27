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
- Started: 2026-10-26 (milestone setup; no TDD phase started)
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
  pass entry below).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Pending | — | Freeze against the answered Q1–Q9: `docs lifecycle`'s `*files, <state>` grammar, state vocabulary (built-ins plus `add_lifecycles` extensions, minus `archived`), refusal set and order, idempotence and single-reindex rules, output lines and `--json` record; free-form `relate`'s grammar (`[a-z][a-z0-9-]*`, D6), endpoint rules (archived SOURCE refused, archived TARGET never written, any existing file as TARGET), one-sided write and record; recognized-verb byte stability; the `--body-from` sentence; D10's config-aware `parse()` signature and how its sites obtain the config (D10's behaviour, `render_index` placement and `docs stamp` refusal are frozen); the stamp refusal's message; argparse's leading-hyphen handling; the upgrade note's three D10 changes; the surface list; the Phase-5 signatures. |
| 2. Write Tests (RED) | Pending | — | New `tests/test_cli_lifecycle.py`; free-form additions to `tests/test_cli_relate.py` and `tests/test_relate_plan.py`; archive-invariance locks; the `--body-from` lock; skill parity; the 2.1.0 pin; both suite-probe replicas; D10's vocabulary, date-format, `render_index` and `docs stamp` locks; the pre-existing tests edited exactly as the task plan's *Pre-existing tests that change* lists. |
| 3. Create Data/Fixtures | Pending | — | Inline `tmp_path` builders for every write-then-compare case; archive invariance by copying `archive-neighborhood` / `movelink-strand` and re-linking through `relate`; for D10, one `vocab-extension/` tree with the sweep registration updated, inline builders for every non-default `date_format` case, and the `tests/test_cli_mv.py` `_attic_tree` correction. |
| 4. Run Tests (RED Baseline) | Pending | — | Classified failure set against the 1504-test baseline; every GREEN-at-baseline lock named; every pre-existing id accounted for through the plan's explicit old → new mapping. No operator checkpoint (Standard). |
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
| **E4** | Hand-written bullets on a throwaway tree: `- : target.md`, `- see also: target.md`, `- @#!$: target.md`, `- Precedes: target.md` and `- pairs-with  : target.md` all pass `docs check` with no finding; `docs list --json` reads their verbs as `""`, `"see also"`, `"@#!$"`, `"Precedes"`, `"pairs-with"`. Only a missing colon / empty target (`malformed`) or an unresolvable target (`broken-ref`, e.g. `.`) fails. | `docs check` parses no token grammar — it accepts anything before the first colon. The registered recommendation "accept exactly the token grammar `docs check` already parses" therefore does not pin a grammar. | D6, Q3, A2 |
| **E5** | `docs relate add a.md Precedes b.md --dry-run` exits 2 (`unknown verb 'Precedes'`), pinned by `test_relate_case_variant_verb_refuses`. | Under a parser-mirroring grammar this refusal becomes an exit-0 one-sided `Precedes:` edge that reciprocity ignores — a silently wrong edge. | D6, Q3 |
| **E6** | `docs new spec a --body-from body.md`, body opening `Related:` / `- pairs-with: b.md` / `- references: b.md`: the group lands in the metadata block; `docs list --json` lists both edges; `docs check` clean. A body opening with a `Revision:` group lands in the block of an **active** document the same way. A lone `Lifecycle: active` line after the blank line stays body. `references/use-cases.md` row *Sidecar a non-md artifact* prescribes `--body-from -` with `Related: artifact-of: <binary>` ("No new verb — uses the M8 `--body-from` flag"); `references/adoption-playbook.md` repeats it and describes the refusal heuristic as `^[A-Z][A-Za-z-]+:\s` — the pre-M15 — C4 wording. No test in `tests/test_body_from.py` or `tests/test_cli_new.py` mentions `Related`. | The route is the skill's documented intent — supported, not an accident — and it is untested. **Corrected by the Step 0 review (claude-S2):** both skill examples spell `Related:` inline, and `printf 'Related: artifact-of: deck.html\n\n## Body\n' \| docs new notes inline --body-from -` yields no edge (`docs list --json`: `[]`), while the group form yields `artifact-of: deck.html`; Phase 7 rewrites both examples. Its generality (any bare-label group) is a separate leak; the playbook line is stale bundled guidance. | D8, Q5, A3 |
| **E7** | `.docs.toml` with `[vocabulary] add_lifecycles = ["shipped"]`, one document hand-set to `Lifecycle: shipped`: `docs index` exit 2 (`Lifecycle: 'shipped' not in vocabulary`); `docs touch b.md` (another document) writes, then exit 2 `INDEX refresh failed`; `docs list` and `docs list --json` omit the document, printing the error on stderr, exit 0; `docs relate add a.md precedes b.md` exit 1; `docs archive a.md --dry-run` exit 1; `docs mv b.md c.md --dry-run` exit 2; `docs check` **no violations, exit 0**. With `add_roles = ["adr"]`: `docs new adr x` exit 0, then `docs index` exit 2. Cause: `parse()` calls `validate_lifecycle(lifecycle, BUILTIN_STATUSES)` and `validate_role(role, BUILTIN_ROLES)` rather than the tree's merged vocabulary, and `walk()`, `query_docs`, `_cmd_archive`, `_known_projects`, `_cmd_project_set`, `_resolve_relate_endpoint` and `_cmd_stamp` all go through it. Five fixture sidecars carry `add_roles = []`; none exercises a non-empty extension through a walk. This repository's `.docs.toml` and the bundled template advertise the feature. | The registered clause "any `add_lifecycles` extension … and reindexes once" cannot hold on 2.0.0: the verb would write a state that its own reindex rejects. Both new verbs validate endpoints through `parse()`, so the answer decides whether they work on such trees at all. | D2, Q7, A1 |
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

## Phase 1 — Define Contract

_Not started._

## Milestone completion summary

_Not complete._
