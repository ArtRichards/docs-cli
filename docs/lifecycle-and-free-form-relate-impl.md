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
  as recommended; Q1, Q2, Q4, Q5, Q6 and Q9 conductor-resolved. Phase 1 —
  Define Contract is next and does not re-open any of the nine.** Setup
  measured this repository read-only and reproduced every behaviour on
  throwaway trees in the session scratchpad, producing eleven pieces of
  evidence (**E1–E11**). The headline is **E7**: a vocabulary extension — the
  `add_lifecycles` states the registered scope promises `docs lifecycle` will
  write — already breaks every verb except `docs check`, and **E8** shows a
  non-default `date_format` doing the same. The operator answered **Q7** by
  bringing the cause into scope: **D10** makes `parse()` honour the tree's
  config at every call site, and **E11** bounds the one changed outcome to a
  tree that already fails `docs check`. **E4** showed `docs check` parses no
  token grammar for a `Related:` verb; the operator answered **Q3** with the
  lowercase kebab token `[a-z][a-z0-9-]*` (**D6**). **E6** found the
  `--body-from` route for `Related:` edges documented in the bundled skill
  since M8 with no test behind it (**Q5**). **E2** names the one external
  consumer, the Agent Playbook Suite's CI guard, whose two probes become
  product tests. Risk is **Standard**, operator-confirmed (**Q8**).
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
- Taste triage: pending — each review finding fixed or waived with a logged
  reason.

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Pending | — | Freeze against the answered Q1–Q9: `docs lifecycle`'s `*files, <state>` grammar, state vocabulary (built-ins plus `add_lifecycles` extensions, minus `archived`), refusal set and order, idempotence and single-reindex rules, output lines and `--json` record; free-form `relate`'s grammar (`[a-z][a-z0-9-]*`, D6), endpoint rules (archived SOURCE refused, archived TARGET never written, any existing file as TARGET), one-sided write and record; recognized-verb byte stability; the `--body-from` sentence; D10's config-aware `parse()` signature, its seven call sites and the E11 upgrade sentence; the surface list; the Phase-5 signatures. |
| 2. Write Tests (RED) | Pending | — | New `tests/test_cli_lifecycle.py`; free-form additions to `tests/test_cli_relate.py` and `tests/test_relate_plan.py`; archive-invariance locks; the `--body-from` lock; skill parity; the 2.1.0 pin; both suite-probe replicas; D10's vocabulary and date-format locks across every walking verb; the E10 refusal ids and E11's date-format pin rewritten as named behaviour-change edits. |
| 3. Create Data/Fixtures | Pending | — | Inline `tmp_path` builders for every write-then-compare case; archive invariance by copying `archive-neighborhood` / `movelink-strand` and re-linking through `relate`; for D10, one `vocab-extension/` tree with the sweep registration updated, and inline builders for every non-default `date_format` case. |
| 4. Run Tests (RED Baseline) | Pending | — | Classified failure set against the 1504-test baseline; every GREEN-at-baseline lock named; the four behaviour-change ids (E10, E11) accounted for. No operator checkpoint (Standard). |
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
| **E6** | `docs new spec a --body-from body.md`, body opening `Related:` / `- pairs-with: b.md` / `- references: b.md`: the group lands in the metadata block; `docs list --json` lists both edges; `docs check` clean. A body opening with a `Revision:` group lands in the block of an **active** document the same way. A lone `Lifecycle: active` line after the blank line stays body. `references/use-cases.md` row *Sidecar a non-md artifact* prescribes `--body-from -` with `Related: artifact-of: <binary>` ("No new verb — uses the M8 `--body-from` flag"); `references/adoption-playbook.md` repeats it and describes the refusal heuristic as `^[A-Z][A-Za-z-]+:\s` — the pre-M15 — C4 wording. No test in `tests/test_body_from.py` or `tests/test_cli_new.py` mentions `Related`. | The route is a documented, shipped use case — supported, not an accident — and it is untested. Its generality (any bare-label group) is a separate leak; the playbook line is stale bundled guidance. | D8, Q5, A3 |
| **E7** | `.docs.toml` with `[vocabulary] add_lifecycles = ["shipped"]`, one document hand-set to `Lifecycle: shipped`: `docs index` exit 2 (`Lifecycle: 'shipped' not in vocabulary`); `docs touch b.md` (another document) writes, then exit 2 `INDEX refresh failed`; `docs list` and `docs list --json` omit the document, printing the error on stderr, exit 0; `docs relate add a.md precedes b.md` exit 1; `docs archive a.md --dry-run` exit 1; `docs mv b.md c.md --dry-run` exit 2; `docs check` **no violations, exit 0**. With `add_roles = ["adr"]`: `docs new adr x` exit 0, then `docs index` exit 2. Cause: `parse()` calls `validate_lifecycle(lifecycle, BUILTIN_STATUSES)` and `validate_role(role, BUILTIN_ROLES)` rather than the tree's merged vocabulary, and `walk()`, `query_docs`, `_cmd_archive`, `_known_projects`, `_cmd_project_set`, `_resolve_relate_endpoint` and `_cmd_stamp` all go through it. Five fixture sidecars carry `add_roles = []`; none exercises a non-empty extension through a walk. This repository's `.docs.toml` and the bundled template advertise the feature. | The registered clause "any `add_lifecycles` extension … and reindexes once" cannot hold on 2.0.0: the verb would write a state that its own reindex rejects. Both new verbs validate endpoints through `parse()`, so the answer decides whether they work on such trees at all. | D2, Q7, A1 |
| **E8** | `.docs.toml` with `[archive] date_format = "%d-%m-%Y"`: `docs new spec a` writes `Updated: 26-10-2026`; the next `docs index` exits 2 (`Updated: malformed date '26-10-2026' (expected %Y-%m-%d)`); `docs touch a.md` writes, then exits 2 the same way; `docs check` exit 0. | The same config-blindness, in the date half — wider than the 2026-08-15 entry recorded (it named `docs archive`). Bears on whether Q7 fixes both halves. | Q7 |
| **E9** | `docs relate add a.md precedes coverage.xml` exits 1 (`coverage.xml: missing H1`); a hand-written `- references: coverage.xml` passes `docs check` at exit 0. | `relate` parses both endpoints because both are written for a recognized pair; a free-form TARGET is never written, and the convention and the bundled skill's quality-artifact guidance allow non-Markdown targets. | D5, Q6 |
| **E10** | Three pre-existing ids pin the free-form refusal: `test_relate_unknown_verb_refuses`, `test_relate_quiet_suppresses_success_but_never_a_refusal` (both `pairs-with`), `test_relate_case_variant_verb_refuses` (`Precedes`). `test_every_named_verb_is_a_real_subcommand` derives the real verb set from the parser, so registering `lifecycle` without the skill naming it fails the suite. Archive candidates come from `_CASCADE_VERBS = ("pairs-with", "child-of")` over parsed `Doc.related`. | The behaviour change is visible in exactly three ids; the parity gate self-enforces; archive invariance reduces to byte-identity of the written bullet. | D4, D7, D9 |
| **E11** | *Measured 2026-10-27, after the operator's Q7 answer.* A tree created with the default format, whose sidecar is then switched to `[archive] date_format = "%d-%m-%Y"` while its document keeps `Updated: 2026-10-27`: `docs check` reports `bad-date` (`expected %d-%m-%Y`) at exit 2; `docs index` exits 0. No committed fixture sidecar sets a non-default `date_format`. `Config.__post_init__` refuses a vocabulary that is not a superset of the built-ins. `test_archive_renders_the_witness_in_the_trees_date_format` pins today's exit-2 tail on purpose, and its docstring names its successor: "a later milestone that FIXES E8 will break this test, deliberately — its expected exit code becomes 0". | Bounds D10's behaviour change: the vocabulary half only widens what parses, and the date half changes an outcome only on a tree that already fails `docs check` — so no check-clean tree starts failing. The archive test becomes the fourth named behaviour-change edit. | D10, Q7 |

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
  measured after the answer, bounds the one changed outcome to a tree that
  already fails `docs check`. Both feedback entries now name this milestone.
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
  recorded as the fourth named behaviour-change edit.
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
- Status: `open`.
- Frozen packet: base `2ad941e269339f5a125856f5bcda9339cd9f5b15` (the claim
  checkpoint, `lifecycle-and-free-form-relate(claim): activate the tracker
  row`); review commit — the Step 0 review-ready checkpoint commit that
  introduces this entry, whose SHA is returned in the hand-off and recorded
  here when the packet is frozen (a commit cannot carry its own SHA).
- Tracker: `milestone-plan.md` in the docs root; owning project `docs`;
  project path empty (dedicated docs root); artifact stem
  `lifecycle-and-free-form-relate`; active semantic slug
  `lifecycle-and-free-form-relate`; claim checkpoint `2ad941e`; semantic
  branch root `lifecycle-and-free-form-relate/`.
- Claude slot: `pending`.
- GPT slot: `pending`.
- Findings: none recorded yet.
- Taste triage: pending.
- Re-review: pending — decided after the provider outcomes.
- final-sync: `pending`.

## Phase 1 — Define Contract

_Not started._

## Milestone completion summary

_Not complete._
