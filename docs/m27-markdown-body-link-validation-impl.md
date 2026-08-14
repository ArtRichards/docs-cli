# M27 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-08-14

Related:
- child-of: m27-markdown-body-link-validation.md
- pairs-with: m27-markdown-body-link-validation.md
- pairs-with: status.md
- references: feedback-log.md

## Overview

Chronological implementation log for M27 — Markdown body-link validation.
Append one evidence-backed section per TDD phase; keep the progress table and
the milestone checklist synchronized.

## Implementation metadata

- Project: docs
- Milestone: M27 — Markdown body-link validation
- Started: 2026-08-14 (milestone setup; no TDD phase started)
- Progress: **Step 1 in flight on `m27/phases-1-4`. Phase 1 — Define Contract
  complete (2026-08-14).** All seven setup questions were RESOLVED at setup
  (Q1/Q2/Q5 by the operator; Q3/Q4/Q6/Q7 conductor-resolved) and Phase 1 did
  not re-open them. Q5 was resolved **against** the setup recommendation and
  then **amended** — the hermetic boundary is kept, and an escaping
  destination is reported by path arithmetic as a second rule,
  `outside-root-body-link`, rather than skipped.
- Source: the operator-confirmed body-link decisions in `feedback-log.md`
  (2026-08-09/10) and the M27 registration in `plan.md` (2026-08-10).
- Branch: `m27/milestone-setup` for setup; `m27/phases-1-4` for Step 1
  (Phases 1–4).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | **Done** | 2026-08-14 | Froze the supported Markdown grammar subset, the masking rules, destination classification/normalisation/resolution, **the containment test and its precedence over existence**, both findings (`broken-body-link`, `outside-root-body-link`) with severity / message template / exit code / ordering, the `BodyLink` span contract M28 consumes, and the legacy-tree policy — against the resolved Q1–Q7. |
| 2. Write Tests (RED) | **Done** | 2026-08-14 | Scanner unit tests over every supported and every excluded form; both rules' integration + subprocess/JSON locks; the no-double-report precedence lock and the never-stat-outside-the-root lock; the E5/E6 false-positive and false-negative locks; the pathological-input runtime lock. |
| 3. Create Data/Fixtures | **Done** | 2026-08-14 | `bodylink-*` trees, one semantic each, including `-outside-root` (escape aimed at a path that cannot exist) and the `../sub/../back-inside.md` normalise-back case; exotic grammar as inline strings (the M25 rule). |
| 4. Run Tests (RED Baseline) | Pending | — | Classified failure set; the transitional classification of `test_check_dogfood_repo_docs_is_clean`. |
| 5. Update Base Interfaces | Pending | — | `BodyLink` model, length-preserving `_mask_code`, `scan_body_links`, `classify_destination`, the containment/resolution helpers; no rule wired yet. The scanner reports every local destination — containment is the rule's job. |
| 6. Implement Offline/Core Path | Pending | — | Wire both rules into `check_doc`, containment before existence; land the live-tree repair — 139 archived rebases plus `charter.md:52`'s URL conversion — in the same phase so the dogfood gate never sits knowingly RED. |
| 7. Update Tool/Wrapper Layer | Pending | — | `cli.md` (rule list, exit codes, the explicitly stated out-of-root boundary) / `convention.md` (the inside-the-root invariant, fence-your-samples, the third archived exception) / bundled skill / `UNRELEASED` CHANGELOG and the adopter upgrade recipe. No version bump. |
| 8. Run Tests (GREEN) | Pending | — | Full product and quality gates with exact counts; mechanical no-regression proof. |
| 9. Integrate / Accept / Dogfood | Pending | — | Replay the pre-repair damage on a throwaway copy and walk the documented upgrade recipe; prove hermeticity by re-checking the copy where no sibling `src/` exists; false-positive sweep; measured scan runtime. |
| 10. Quality, Docs, Refactor | Pending | — | Simplify, close `architecture.md` / `test-strategy.md`, completion summaries, hand the scanner to M28. |

## Setup record — 2026-08-14

### Objective

Bring the registered M27 draft stub up to full milestone-task-plan depth and
create this log, without starting Phase 1. M26 is implementation-complete and
merged to `main` (`393fb53`), so M27 is the next implementation milestone in
the v2.0 train.

### Actions taken

- Re-derived the stub's four Phase-1 open questions against the real v1.8.0
  implementation (`check_doc`, `_iter_doc_texts`, `Finding`,
  `finding_to_json`, `exit_code_for`) and against `cli.md`, `convention.md`,
  `test-strategy.md`, and `feedback-log.md`.
- Built a throwaway prototype scanner (bounded grammar, length-preserving
  code masking) and ran it **read-only** over this repository's `docs/` tree,
  all 33 committed fixture trees, and the bundled `src/docs_cli/skill/` tree.
  The measurements are tabulated below and drive the milestone's *Current
  state and risks* section. No repository file was mutated during setup.
- Expanded *Binding scope* into eight decisions (D1–D7 plus the amendment's
  **D4b**), added *Out of scope*, the ten-phase TDD plan with per-phase
  objective/files/exit, the phase checklist, the testing gate,
  evidence-anchored success criteria, and *Follow-ups recorded for later
  milestones*.
- Kept the reciprocal `follows`/`precedes` and `required-by` edges intact and
  added the milestone↔log pair edges.
- Raised seven setup questions (Q1–Q7) with recommendations rather than
  deciding any of them silently, and then **resolved all seven before
  Phase 1** — Q1 (legacy-damage policy), Q2 (supported syntax set), and Q5
  (destinations leaving the root) by operator decision; Q3 (what counts as
  code), Q4 (finding shape), Q6 (no opt-out knob), and Q7 (destination target
  kinds) conductor-resolved from the specs, the measured evidence, and the
  M25/M26 precedent. Every resolution is recorded in the milestone doc's
  *Resolved setup questions (Q1–Q7, BINDING)* and folded into D1–D7.
- **Q5 was resolved against the setup recommendation, then amended**, and both
  turns are recorded. The draft proposed validating destinations that resolve
  outside the docs root; the operator kept the **hermetic boundary** instead
  (`docs check` never touches the filesystem outside its own root, matching
  `src/docs_cli/cli.py:5216`'s `is_relative_to(root)` from M26 — `31bdc59`).
  Silently skipping such a destination was then rejected too, so the amendment
  adds a **second finding**, `outside-root-body-link`, decided by path
  arithmetic alone — an **operator-approved post-draft scope addition**
  following M25's `duplicate-field` precedent. `charter.md:52` is converted to
  the canonical GitHub URL in Phase 6 rather than left as an accepted gap.
- Ran a dedicated **containment census** for the amendment — path arithmetic
  only, counting escapes that would resolve and escapes that would not — over
  `docs/`, all 33 fixture trees, and the bundled skill. Exactly **one** escape
  exists (`charter.md:52`); **zero** fixture trees and the bundled skill carry
  any, so no fixture needs updating before Step 1.
- Scaffolded this log with `docs new log m27-markdown-body-link-validation-impl`,
  bumped dates and validated with `docs touch … --check` (exit 0), and
  refreshed the frozen dogfood INDEX snapshot
  `tests/fixtures/expected/docs-INDEX.md` for the new log entry
  (23 → 24 active docs) — the same snapshot refresh the M25 and M26 setups
  performed.
- Updated the trackers: `status.md` (current milestone, train listing, next
  action, milestone-progress row) and `plan.md` (v2.0 narrative and the M27
  row) now describe M27 as in flight with its plan and log linked.

### Current-tree evidence (docs-cli 1.8.0, measured read-only during setup)

| Evidence | Measurement | Why it matters | Bears on |
|---|---|---|---|
| **E1** | The prototype scan of `docs/` finds **455** link-shaped spans over the **70** documents the tree held at measurement time; **139** local destinations do not resolve, across **29** documents. **All 139 are under `archive/`; the active tree has zero** — and it still has zero after this setup's own edits (re-measured: 462 spans over 71 documents, same 139 unresolved). | The damage is real and it is exactly one shape: relative links that were never rebased when their document moved into `archive/YYYY-MM-DD/`. | D6, Q1 |
| **E2** | Of the 139: **132** resolve from the docs root (a pure `../../` rebase — `plan.md` ×38, `status.md` ×24, `release-runbook.md` ×23, `cli.md` ×20); **5** name a document that itself later moved (`m9-pypi-publish.md` → `archive/2026-05-25/m9-pypi-publish.md`; `m2-mutating-verbs.md` → `archive/2026-05-21/m2-mutating-verbs.md`); **2** name `references/adoption-playbook.md`, a file that never lived in the docs tree at all (it is the bundled skill's, at `src/docs_cli/skill/references/adoption-playbook.md`). | Every one of the 139 is repairable by a destination-token-only edit, and the repair is exactly the path math M28 will implement. The last 2 became a URL under Q1 — doubly right, since the relative alternative would itself have violated Q5. | D6, Q1 |
| **E3** | `docs check --root docs` exits **0** today with all 139 broken. `check_doc` validates metadata and `Related:` targets; the body is opaque (`test-strategy.md` › *What we don't test*: "the body content is opaque"). | The gap is total, not partial: there is no weaker existing signal to strengthen. | D4 |
| **E4** | `tests/test_cli_check.py::test_check_dogfood_repo_docs_is_clean` asserts `docs check <repo>/docs` returns **0**. | The legacy-tree policy is a **hard gate inside the suite**, not an aspiration: the moment either rule lands, that test is RED until the tree is repaired. It also fixes *when* the repair must land — no later than the phase that wires the rules (Phase 6). | D6, Q1, Q5 |
| **E5** | A scan without code masking gains **4** false positives inside fenced code — including `architecture.md:182`'s `[<path>](<path>)` — and **3** inside inline code spans (`archive/2026-05-20/m1-parser-and-index-log.md:359`, where an `_format_entry` output sample carries `[name](name)` inside a code span; and `archive/2026-05-21/m2-mutating-verbs-log.md:114` and `:523`). | Fenced-block and inline-code masking are load-bearing on this tree, not theoretical. A regex-only implementation flags the project's own documentation. | D2 |
| **E6** | Treating 4-space-indented lines as indented code blocks would mask **9** link-shaped spans in this tree — and **all 9 are real links** in blockquote / list continuations, 6 of them among the 139 genuine breaks (e.g. `archive/2026-05-25/m8-adoption-workflow.md:225`). | Indented-code support would buy false negatives on real damage. The tree's own code samples are all fenced. | D2, Q3 |
| **E7** | `charter.md:52` carries `[…](../src/docs_cli/skill/references/use-cases.md)` — a link in the **active** tree whose destination leaves the docs root. A dedicated **containment census** (path arithmetic only; escapes that would resolve *and* escapes that would not) over `docs/`, all **33** fixture trees and the bundled skill finds **exactly this one escape**, and **zero** in any fixture tree or in the bundled skill. | The boundary policy is load-bearing today, in the active tree, in the project's charter. It also demonstrates the hermeticity argument: the link resolves only because `docs/` happens to sit beside `src/` in a checkout, so the same bytes in a container or a vendored subtree would give a different verdict. Under Q5-as-amended it becomes one `outside-root-body-link` and is converted to a URL in Phase 6. No fixture needs updating. | D3, D4b, Q5 |
| **E8** | The whole corpus exercises **one** form. Across `docs/`, all 33 fixture trees and the bundled skill: **zero** images, autolinks, raw-HTML anchors, reference definitions, angle-bracket destinations, titled destinations, percent-escaped destinations, backslash-escaped destinations, whitespace-bearing destinations, and directory destinations. All 455 spans are plain inline links; every fixture tree and the bundled skill resolve cleanly. | Nothing in the repository pins the exotic grammar, so Phase 3 must author it deliberately — and no existing fixture tree will regress when either rule lands. | D1, D2, Phase 3 |

### Verification

- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 46 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 47 source files.
- `.venv/bin/python -m pytest -q` — 895 passed.
- `.venv/bin/docs check --root docs` — no violations found (exit 0).

### Decisions / issues

- **The damage is one shape, and it is M28's shape.** E1/E2 show the archived
  breakage is the move-time rebase M28 exists to prevent. That makes the
  legacy repair unusually cheap and unusually well-specified: 132 pure
  rebases, 5 move-map lookups, 2 that become a URL. It also means M27's repair
  is a rehearsal of M28's algorithm on real data.
- **Q1's decisive argument was ownership, not volume.** The breakage class is
  produced by `docs archive` itself and no version of the tool has ever
  rebased a moved document's body links, so adopters' archives are where it
  predominantly lives — 8 of the 33 committed fixture trees already carry
  `archive/` directories. A rule exempting archived documents would leave the
  tool silent about the exact damage it causes. Reinforcing it: `docs/`,
  archive included, ships in every PyPI **sdist**
  (`[tool.hatch.build.targets.sdist] include = [… "docs" …]`; the wheel carries
  only `src/docs_cli`) and is public on GitHub, so the worst-hit destinations —
  `plan.md` ×38, `status.md` ×24, `release-runbook.md` ×23, `cli.md` ×20 — are
  what a prospective adopter reads. Both facts were verified during setup.
- **The dogfood test fixes the phase ordering.** E4 means the live-tree
  repair cannot be deferred to Phase 9 without leaving Phase 6's and Phase 8's
  exit criteria knowingly false. The plan therefore lands the repair in the
  same phase that wires the rules (Phase 6) — including `charter.md:52`'s URL
  conversion — and repurposes Phase 9 to replay the pre-repair state on a
  throwaway copy so the adopter upgrade path is exercised rather than assumed.
- **Q5 turned twice, and the second turn is the interesting one.** The setup
  draft proposed validating out-of-root destinations by existence; that lost to
  the hermeticity argument — a check must be a function of the tree alone, and
  `charter.md:52` resolves today only because `docs/` sits beside `src/` in a
  checkout. But *silently skipping* the escape lost too, because a working,
  load-bearing link would then rot unnoticed. The amendment keeps the boundary
  and changes the response: an escape is detected by **path arithmetic alone**
  and reported as `outside-root-body-link`. The tool gains visibility without
  gaining a single stat outside its own root. Recorded as an
  **operator-approved post-draft scope addition** (M25's `duplicate-field`
  precedent) rather than as scope that drifted in.
- **Two rules mean a precedence question, and it is answered in the
  contract.** Containment is tested **before** existence, so an escaping
  destination yields `outside-root-body-link` **only** — never also
  `broken-body-link`, because deciding brokenness would need the forbidden
  stat. Phase 1 states the ordering so it is specified behaviour rather than
  an artefact of the order two `if`s happen to appear in.
- **Rule naming settled without a question, per instruction.**
  `outside-root-body-link` reuses M26's existing `outside-root` token for this
  exact condition, so the codebase has one name for one idea, and shares the
  `-body-link` suffix with `broken-body-link` so the pair is greppable and
  reads as a family in `cli.md`. Rejected: `escaping-body-link` (invents a
  second vocabulary), `external-body-link` ("external" already means *URL* in
  this project's prose), `unrooted-body-link` (obscures which root).
- **Q1 and Q5 converge on the same spelling, independently.** Routing the 2
  `references/adoption-playbook.md` links to the canonical GitHub URL was
  chosen under Q1 before Q5 was amended; the relative alternative,
  `../../../src/docs_cli/skill/references/adoption-playbook.md`, would have
  been an `outside-root-body-link` violation. Two decisions taken on separate
  grounds arriving at one answer is corroboration.
- **The span, not the string, is the handoff to M28.** `BodyLink` carries the
  exact `(start, end)` offsets of the *destination token* in the original
  text, and code masking is length-preserving so those offsets stay valid.
  That single property is what lets M28 splice a rewritten destination
  without re-parsing and without touching a single other byte — the concrete
  meaning of the stub's "reusable by M28 without duplicating parsing logic".
  The scanner reports **every** local destination and leaves containment to the
  rule, which is what lets `outside-root-body-link` exist at all.
- **M28 gains a simplification from Q5.** Because escaping links are now
  forbidden and reported, a clean tree contains none, so M28 never has to
  decide how to rebase a destination pointing outside the root. Under the
  rejected silent-skip reading, that question would have landed on M28.
- **The JSON record stays closed.** `Finding`'s docstring, `cli.md`'s field
  table, and two tests in `tests/test_cli_check.py` —
  `test_check_json_emits_finding_array` (line 95) and
  `test_check_missing_inverse_json_record_keys_unchanged` (line 311), both
  asserting `set(rec) == {"path", "severity", "rule", "message"}` — pin the
  four-key record. M25 added
  `missing-inverse` without opening it; **both** M27 rules do the same and
  carry line, raw destination, and resolved candidate in `message`.
- **No new pass is needed.** Unlike M25's `missing-inverse`, both rules are
  purely per-document: they need the referring document's own text and its own
  directory. They belong in `check_doc`, not in a second `check_tree` pass —
  cheaper and simpler than the M25 precedent.
- **`INDEX.md` is out of the walk.** `_iter_doc_texts` skips the root-level
  `INDEX.md`, so the generated index's links are never scanned. That is
  correct — they are regenerated, not authored — and it must be stated rather
  than left as an accident of the walker.
- Version staging is already settled by M25 — D6: the package stays `1.8.0`
  through M25–M28 and M29 performs the single bump to `2.0.0`. M27 touches
  neither `pyproject.toml` nor the packaging version pins; its CHANGELOG
  entries accumulate under the existing `UNRELEASED` heading.
- Host-machine workflow skills are **not** updated by this milestone. Per
  `CLAUDE.md`, host skills refresh only at a production ship; the bundled
  skill inside `src/docs_cli/skill/` **is** updated in lockstep, in Phase 7.
- **No OPEN QUESTIONS remain.** All seven are resolved and recorded as binding
  in the milestone doc; Phase 1 freezes the exact grammar, the masking and
  containment contracts, both message templates, and the `BodyLink` span
  record against them rather than re-litigating scope.

### Resolved setup questions — summary

Full reasoning in the milestone doc's *Resolved setup questions
(Q1–Q7, BINDING)*.

| # | Question | Resolution |
|---|---|---|
| Q1 | The live tree's 139 archived breaks: repair, or scope the rule away from archived documents? | **Repair; the rule stays uniform** (operator). One-time, destination-token-only, `Updated:` + dated `Revision:` audited, landed in Phase 6. `convention.md` gains a third archived-document exception with a stated blast radius. |
| Q2 | Which Markdown forms does the scanner recognise? | Inline links (plain and angle-bracket destinations, optional titles) **plus** reference definitions (operator). Images, autolinks, raw HTML, and reference *uses* excluded — images recorded as a named later candidate with rationale. |
| Q3 | What counts as code? | Fenced blocks + inline code spans **only**; no 4-space indented-code rule (conductor, on E6). |
| Q4 | Finding shape | `broken-body-link`, `severity: error`, exit 2, one per occurrence, JSON key set **closed**, location in `message` (conductor). |
| Q5 | Destinations that leave the docs root | **Hermetic boundary kept — and the escape is reported** (operator, amended). Never stat outside the root; detect by path arithmetic; new rule `outside-root-body-link`; containment tested before existence so the two never double-report; `charter.md:52` converted to a URL in Phase 6. |
| Q6 | A `.docs.toml` opt-out | **No knob** (conductor). The 2.0.0 bump is the migration signal. |
| Q7 | What satisfies a destination | Any existing filesystem entry — file **or** directory, any extension (conductor), applied within the root. |

## Phase 1 — Define Contract — 2026-08-14

### Objective

Freeze every byte of surface Phase 2 will assert against: the supported
grammar and its exactness rules, the length-preserving code-masking contract
and its ordering, destination classification, the resolution base, the
containment test and **its precedence over existence**, both findings'
message templates, the closed JSON record, and the `BodyLink` span contract
M28 consumes — against the resolved Q1–Q7, which are not re-opened. No
business logic lands.

### Actions taken

**`docs/cli.md`** — two new rule bullets in the `docs check` reports list, the
JSON field table's `rule` enumeration extended with both ids, the
closed-key-set paragraph and the exit-code prose extended, and a new
`#### Markdown body-link validation (M27 — D1–D4b)` block with seven
subsections:

- *(preamble)* — what is scanned (the whole document text of every walked
  doc), the never-scanned root-level `INDEX.md` **and the explicit statement
  that a nested `INDEX.md` IS scanned**, the `malformed` early-return, the
  `docs touch --check` inheritance, and the no-knob rule.
- *The supported grammar (M27 — D1)* — the eight-row recognised/excluded
  table plus nine numbered exactness rules and the BINDING
  strip-`<…>` → split-on-`#` → backslash-unescape → percent-decode → join →
  normalise order with its three stated consequences.
- *The destination-token span (M27 — D5)* — `text[start:end] == raw`, angle
  brackets in, title out, and why M28 depends on it.
- *What the scanner never sees (M27 — D2)* — fences and inline spans only,
  fences masked **first**, inline spans single-line, no 4-space
  indented-code rule, length preservation as a testable guarantee.
- *Destination classification (M27 — D2)* — the six kinds as a table with
  their test order, the `C:\…`-is-scheme-shaped note, and the
  classify-on-the-token-as-written rule.
- *Resolution and containment (M27 — D3 / D4b)* — the three-step pure
  `posixpath` test, escape-then-return, the deliberate divergence from the
  `resolve()`-based archive-subtree test, the root-itself case, Q7's
  any-entry rule, the exclusion-governs-the-walk rule, and the hermeticity
  argument stated as adopter-predictable behaviour.
- *Evaluation order — BINDING* and *The two findings* — the three-step
  fenced order, both frozen templates, both worked instances, and the
  `<N>` / `<raw>` / `<candidate>` definitions.
- *Upgrading from 1.x* — the adopter recipe for both rules, with the
  no-repair-verb statement.

**`docs/convention.md`** — a new `## Body links (M27)` section carrying the
invariant *a local Markdown body link stays inside the tree root; anything
outside the tree is a URL* with its **portability** rationale (not as an
implementation note), the *fence code samples that contain link syntax* rule
plus the backslash opt-out, the resolution-base contrast with `Related:`, and
the never-touched external forms. Plus three amendments in place:

- the **third narrow archived-document exception** (M27 — D6) beside M18's
  and M25 — D4's, with its stated blast radius — destination tokens,
  `Updated:`, one `Revision:` bullet, **29** archived documents, once, on a
  stated date; explicitly not a general licence; **no CLI verb performs it**;
- *Non-Markdown files in the tree* — `Related:` "checks existence regardless
  of its extension" now says body links inherit the same any-extension,
  any-kind rule, and names the one difference (resolution base);
- *What `docs` does not promise* — "No content validation beyond metadata.
  The body of a doc is opaque to the tool" was about to become **false**, so
  it is narrowed to metadata-plus-local-body-link-destinations with the
  remaining non-goals (rendering, anchors, style, structure, link-graph
  traversal) named. The milestone's Phase-10 list names `test-strategy.md`'s
  twin sentence but not this one; this one is on the byte-parity gate, so it
  belongs in Phase 1.

**Milestone doc** — new `## Decisions (Phase 1 — BINDING)` carrying the three
setup-frozen amendments, both frozen message templates, twelve contract
points that could not be read off the setup text, the `BodyLink` record and
the frozen Phase-5 signatures with their reuse list, a Phase-5 linearity
implementation note, the logged Phase-1 deviation, the Phase-7/10
follow-through table, and the three authoring traps. D4's proposed message
and the Phase-3 exit criterion are **amended in place** so the binding scope
and the frozen contract cannot disagree. Phase-1 checklist row and
deliverable 1 ticked; Progress line updated.

**Lockstep chores** — `cp docs/{cli,convention}.md
src/docs_cli/skill/references/`; `docs touch` on the four edited docs
(implicit reindex); `tests/fixtures/expected/docs-INDEX.md` re-synced from the
regenerated `docs/INDEX.md` (both spec `Updated:` values moved to
2026-08-14).

### Decisions / issues

- **Three setup-frozen items could not stand, and all three are recorded as
  amendments rather than quietly implemented.** (1) D4's
  `does not resolve to a file:` contradicts the operator-binding Q7 — a
  **directory** satisfies a destination too — so a correct directory link
  that later broke would have been reported with prose asserting the wrong
  test. Frozen as `does not resolve to an existing path:`. (2) D4b named
  `outside-root-body-link`'s severity, exit code, granularity and precedence
  but **no message**; Phase 2 asserts contract strings verbatim, so it is
  specified here. (3) The milestone's Phase-3 exit criterion says
  `test_check_tree_legacy_fixtures_gain_no_new_findings` is "extended … and
  passes for all 33 pre-M27 trees" — but that test's list **excludes**
  `reciprocal-*`, so it covers 23, and extending its assertion would make the
  three deliberately-damaged `bodylink-*` trees Phase 3 authors fail it. The
  coverage lands as a **new sibling** instead, which delivers what the
  milestone asked for and keeps M27's no-regression proof at a clean zero
  moved test ids.
- **The prose/literal tension in amendment 2 is recorded, not smoothed
  over.** The resolution that specified the escaping message also said "both
  templates name the repair". Only `outside-root-body-link`'s does so in
  words (`; links outside the tree must be URLs`); `broken-body-link`'s names
  its repair by **printing the candidate path the tool actually probed**,
  which is what an agent needs to decide between fixing the link and creating
  the file. The frozen literal is implemented exactly as given rather than
  extended with a repair clause nobody froze. **Surfaced for the fresh-eyes
  review** — adding a clause in Phase 7 would be a one-line change.
- **A third authoring trap exists and was found by tripping it.** The plan
  recorded two (`test_bundled_skill_has_no_repo_relative_links`'s raw-line
  `](../` scan, and Phase 1's own examples becoming scannable after Phase 6).
  There is a **third**:
  `tests/test_skill_quality_artifacts.py::test_installed_skill_references_do_not_depend_on_source_checkout`
  forbids the literal `../src/docs_cli/` in every bundled reference. The
  natural worked instance for the escaping rule is E7's real destination —
  `charter.md:52` — and writing it into `cli.md` turned the suite RED the
  moment the byte-identical mirror was copied. Fenced or not is irrelevant;
  the test scans raw text. The worked instance now uses a neutral escaping
  path; E7's real one is named in the milestone and in `charter.md`, neither
  of which is on that gate. Recorded in the milestone's trap list so Phases
  2–7 cannot rediscover it.
- **Several contract points had no answer in the setup text and were
  settled here**, because Phase 2 cannot assert what is undetermined. The
  full list is in the milestone's *Contract points that could not be read off
  the setup text*; the three with real behavioural weight are: a label ends
  at its **first unescaped `]`** (so balanced brackets inside a label are an
  explicit, escapable exclusion — verified zero occurrences in the corpus);
  `classify_destination` strips a surrounding `<…>` pair **before**
  classifying (otherwise `<https://x>` would classify as `local` and be
  resolved as a path); and the `#`-split happening on the **raw** text means
  a backslash cannot escape a `#` out of being the fragment delimiter — the
  same mechanism the resolution already states for `%23`, now stated for its
  sibling.
- **The frozen containment arithmetic reuses two existing idioms verbatim**
  and says so: `_canonical_related_target`'s `posixpath.normpath` (POSIX on
  every platform — `os.path` would make the verdict Windows-dependent and
  destroy the hermeticity property D4b exists to guarantee) and
  `_candidate_exclusion_reason`'s `rel == ".."` / `rel.startswith("../")`
  predicate. The one divergence — the `/` leg — is stated as deliberate: a
  root-absolute *body* destination is classified `root-absolute` and silenced
  before containment runs, while a root-absolute `Related:` target is
  `outside-root`.
- **A read-only prototype of the frozen contract was built and run before the
  contract was written**, and it reproduces the setup census **exactly**:
  `docs/` → 139 unresolved local destinations and **1** escape
  (`charter.md:52`); all **33** committed fixture trees → 0 and 0; the
  bundled skill → 0 and 0. That is the evidence that the grammar being frozen
  is the grammar the evidence was measured with, rather than a plausible
  restatement of it. The prototype lives outside the repository and no
  repository file was mutated by it.
- **The linearity risk is real and has a named shape.** The prototype ran the
  three adversarial inputs Phase 2 will lock (50 000 unmatched `[`, 40 000
  `[a](`, a 100 KB unterminated angle destination) in 0.004 s / 0.66 s /
  0.007 s, and the live 112 KB `cli.md` in 0.005 s — but the 0.66 s case
  exposed the two quadratic shapes a naive implementation falls into. Both
  are recorded in the milestone as a Phase-5 implementation note (not as a
  contract term): re-deriving the blank-line bound per candidate, and
  restarting the outer scan at `open + 1` after a failed candidate instead of
  at the failed candidate's closing `]`.
- **Deviation (approved, same as M25 and M26).** Phase 1 made **zero**
  `cli.py` edits. Stubs would change the Phase-4 subprocess RED reasons and
  risk baseline behaviour, and the phase's own exit criterion is "no behavior
  changes". The signatures are frozen in the milestone doc's Decisions and
  land in Phase 5.

### Verification

- `grep -F` in `docs/cli.md` for **every** verbatim string Phase 2 will
  assert — all present: `body link at line`,
  `does not resolve to an existing path:`, `leaves the docs root:`,
  `(resolves to `, `(normalises to `, `links outside the tree must be URLs`,
  `broken-body-link`, `outside-root-body-link`.
- `cmp docs/cli.md src/docs_cli/skill/references/cli.md` and the
  `convention.md` pair — identical.
- `grep -c '](\.\./'` over `docs/cli.md`, `docs/convention.md`, and all six
  bundled skill `.md` files — **0** in every one (trap 1 held).
- `grep -n '\.\./src/docs_cli/'` over both specs — none (trap 2 held, after
  the worked instance was corrected).
- Prototype scan of the edited `docs/cli.md` and `docs/convention.md` —
  the only recognised spans are the pre-existing ones (five fragment-only
  links in `cli.md`; `cli.md#common-exclusion` and the canonical GitHub URL
  in `convention.md`). Phase 1 added **zero** scannable spans, so trap 3
  held: every new example is inside a fence or an inline code span, and the
  repository still contains **zero** reference definitions.
- `.venv/bin/python -m pytest tests/test_skill_refs.py tests/test_cli_index.py
  tests/test_cli_check.py -q` — 37 passed.
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 46 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 47 source files.
- `.venv/bin/python -m pytest -q` — **895 passed**, unchanged from the
  baseline at `d61da1d`. (One intermediate RED —
  `test_installed_skill_references_do_not_depend_on_source_checkout` — is the
  third trap above; it was fixed inside this phase, not carried.)
- `.venv/bin/docs check --root docs` — no violations (exit 0).
- `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.
- `git diff --stat -- src/docs_cli/cli.py` — **empty**, per the logged
  deviation.

## Phase 2 — Write Tests (RED) — 2026-08-14

### Objective

Express scanning, masking, classification, resolution, containment and both
findings before any implementation exists — including every **exclusion**,
which must be GREEN at baseline and stay GREEN — so each Phase-5/6/7 change
answers a written test rather than the reverse.

### Authoring rules applied (carried from M25/M26)

- **No module-level import of a Phase-5 symbol.** Each is reached through a
  one-line `_m27(name)` wrapper over `getattr(cli, name)` — a clean
  `AttributeError` at run time (never a collection error, which the Phase-4
  exit criterion forbids), `Any` for mypy, and no ruff `B009`.
- **Every intended-exit-2 subprocess test also asserts its contract stdout
  string.** A `bodylink-*` tree exits 0 today, so a bare returncode assertion
  would be honest RED — but the message assertion is what stops the test
  being satisfiable later by an unrelated exit 2 (M26's falsely-GREEN lesson).
- **Every docstring names its intended RED reason**, and every
  GREEN-at-baseline lock says so **and** says whether it is *degenerate* or
  *genuine*.
- **No test asserts the live `docs/` tree's break count.** 139/1 is Phase-6
  evidence, not a lock: a test asserting it would have to be inverted in
  Phase 6.
- **No inline-built doc body carries accidental link syntax** outside the
  tests that are about link syntax.

### New tests

**`tests/test_body_links.py`** (new, **105** items) — the pure scanner seam,
modelled on `tests/test_relate_plan.py` / `tests/test_archive_plan.py`. Every
exotic case is an **inline string**, not a committed tree (the M25 rule):
these assert on parse output, not on a tree walk.

- **Masking, D2 (19 items):** length preservation parametrized over 8 texts,
  asserting `len` **and** identical newline offsets; backtick and tilde
  fences; the equal-or-longer closing-fence rule in both directions; the exact
  two-space-indented `architecture.md` fence shape; inline spans; the
  single-line span rule; unmasked bytes byte-identical; **no** 4-space
  indented-code rule (E6); fences-before-spans; and the two E5 shapes
  verbatim.
- **Grammar, D1 (48 items):** the plain base case; the **13-way parametrized
  `text[start:end] == raw` span invariant** — the M28 handoff, the single
  highest-leverage assertion in the milestone; angle destinations; all three
  title quotings; whitespace-terminated destinations and the non-title
  trailer; balanced parens at the frozen depth and rejected beyond it;
  unbalanced parens; the backslash opt-out and in-destination escapes;
  percent-decoding into `path` but not `raw`, including invalid sequences;
  first-`#` fragment splitting and the absent/empty cases; reference
  definitions and their line anchor; images, autolinks, raw HTML and all
  three reference *uses*; the multi-line label (the exact `convention.md`
  shape) and the blank-line bound; the first-unescaped-`]` label rule; column
  distinctness; 1-based line/column; determinism; mask-before-match; the
  scanner reporting escapes too (D5); and the frozen `BODY_LINK_KINDS`.
- **Classification, D2 (20 items):** the frozen `DESTINATION_KINDS`, `local`
  parametrized ×9 (including a `../` escape and an angle token), `empty`,
  fragment-only including `<#section>`, schemed ×6 (including `C:\…` and
  `<https://x>`), protocol-relative, root-absolute.
- **Containment, D3/D4b (6):** the resolution base; the **filesystem
  sentinel** (`Path.exists` / `is_file` / `resolve` raise if touched);
  escape-then-return; the **symlink lock**, a `tmp_path` arrangement where
  `resolve()` gives the OPPOSITE answer to the lexical form; the root itself;
  and the `..` / `../` predicate.
- **`body_link_findings`, D4/D4b (12):** one finding per occurrence; both
  frozen messages verbatim (the broken one is `cli.md`'s worked instance byte
  for byte); the unconditional candidate parenthetical; **containment wins
  over existence**, with the escaping destination pointed at a path that
  really exists; the **`Path.exists` spy** asserting every probe is under the
  root; source order; Q7's directory and non-Markdown destinations; the
  excluded-but-existing destination; fragments never validated; `%20`
  resolution against a `tmp_path`-built `my doc.md`; and silence for all six
  non-`local` kinds.
- **Runtime (1):** three adversarial inputs totalling 310 KB under a 2.0 s
  wall-clock bound, with the flakiness trade-off stated in the docstring.

**`tests/test_check.py`** (+47 items) — the rules as `check_doc` /
`check_tree` expose them: both messages at the unit seam; the **ordering**
lock on a doc carrying `broken-ref` **and** a broken body link; the
`malformed` early return; the `bodylink-broken` / `-archived` /
`-outside-root` fixture locks; `exit_code_for` == 2; E7's
"whether or not it would have resolved"; E6's indented blockquote link; the
three silent trees; the repaired-copy recipe proof with whole-tree byte
comparison; and the new **33-parametrization**
`test_check_tree_pre_m27_fixtures_gain_no_body_link_findings`.

**`tests/test_cli_check.py`** (+8) — the subprocess surface: both rules'
exit-2 + frozen-message locks using the grouping-header idiom
(`assert "doc.md" in proc.stdout.splitlines()`); both `--json` closed-key-set
locks; the CLI-level **no-double-report** lock; the two exit-0 trees; and
`test_check_verdict_is_identical_from_a_relocated_copy`, the hermeticity lock.

**`tests/test_cli_touch.py`** (+1) — `docs touch --check` inherits both rules
through `_run_touch_check` → `check_tree`; mirrors
`test_touch_check_broken_ref_tree_exits_2`.

**`tests/test_skill.py`** (+2) — the bundled `SKILL.md` `docs check` row and
`references/use-cases.md` must name **both** rule ids and both repairs. RED
until Phase 7, modelled on `test_skill_md_teaches_safe_archive_selection`.

### Pre-existing tests M27 changes

**None.** Nothing was deleted, renamed, or had an assertion altered. The only
edits to existing files are appended sections plus one added `import shutil`
in `tests/test_check.py`. In particular
`test_check_tree_legacy_fixtures_gain_no_new_findings` and
`_legacy_tree_names()` stay **byte-identical** (Phase-1 amendment 3), and the
two closed-record pins —
`tests/test_cli_check.py::test_check_json_emits_finding_array` and
`::test_check_missing_inverse_json_record_keys_unchanged` — are proven
unmoved by `git diff` showing **zero** deleted lines in that file.

### Decisions / issues

- **One Phase-1 gap was found by writing the tests, and closed in the specs in
  this phase** (M26's precedent). The grammar's rule 3 defines a plain
  destination as ending "at the first unescaped whitespace or at an unescaped
  `)` at nesting depth 0" — but a **reference definition** has no enclosing
  `)` to close it, so the rule was under-specified for exactly the one form
  that is not an inline link. Rule 6 in `cli.md` now says so explicitly: there
  the destination ends at the first unescaped whitespace or at the end of the
  line. Mirrored into `references/cli.md` in the same change.
- **A falsely-GREEN family was caught before it could exist.**
  `load_config` tolerates a missing directory and `check_tree` then walks
  nothing, so the three "silent tree" locks
  (`bodylink-clean`, `-excluded-forms`, `-nested`) and the two exit-0
  subprocess locks would all have **passed on fixture trees that were never
  written** — vacuously, for the wrong reason, and indistinguishably from
  success. Both files now route every `bodylink-*` tree through a helper that
  asserts the directory exists first (`_bodylink_findings` /
  `_bodylink_tree`), so between Phase 2 and Phase 3 they are honestly RED on
  the missing fixture and become degenerate-GREEN only once Phase 3 supplies
  it. This is the same trap M26 hit from the other direction, where argparse's
  own exit 2 satisfied a `--json` refusal test.
- **The symlink lock is a real discriminator, not a restatement.**
  `root/sub` is a symlink to a directory outside the root, so `sub/deep.md`'s
  `../inside.md` is **contained** lexically and **escaping** under
  `Path.resolve()`. The two answers are opposite, which is what makes the test
  a lock on the D3 decision rather than a description of it.
- **The never-stat lock is a spy, not a fixture.** The
  `bodylink-outside-root` tree's unreachable destination proves a probe
  *would have failed*; only a `Path.exists` spy recording every probed `self`
  proves **no probe happened**. Both are kept: the fixture is the
  by-construction complement, not a substitute.
- **The masking-order test states what it can honestly discriminate.** Given
  line-anchored fences and single-line inline spans, the two orders coincide
  on every input — so the test locks the one wrong shape that would otherwise
  slip through: multi-line inline spans evaluated *before* the fences, which
  would let a stray backtick inside a fenced block swallow real prose after
  it. The docstring says exactly that rather than implying a stronger claim.
- **No test asserts the live tree's 139/1.** That number is Phase-6 evidence
  and Phase-9 dogfood material; a lock on it would have to be inverted in
  Phase 6, which is the definition of a test that measures the wrong thing.
- **No `src/docs_cli/cli.py` change.** `git diff --stat` against the Phase-1
  commit is empty.

### Verification

- `.venv/bin/python -m pytest tests/ -q --co` — **1058 collected, zero
  collection errors** (895 → 1058: **+163** new ids, **0** removed).
- `.venv/bin/python -m pytest -q` — **129 failed, 929 passed**. Failures by
  file: `test_body_links.py` 105, `test_check.py` 13, `test_cli_check.py` 8,
  `test_cli_touch.py` 1, `test_skill.py` 2. The full classified RED census is
  Phase 4's.
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 47 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 48 source files.
- `.venv/bin/docs check --root docs` — no violations (exit 0).
- `cmp docs/{cli,convention}.md src/docs_cli/skill/references/` — identical.
- `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.
- `git diff --stat -- src/docs_cli/cli.py` — **empty**.
- At the end of Phase 2 the fixture-backed tests still fail on a missing
  `tests/fixtures/trees/bodylink-*` directory, which Phase 3 supplies.

## Phase 3 — Create Data/Fixtures — 2026-08-14

### Objective

Give Phase 2's E1–E8 locks committed trees to run against — one semantic per
tree, structure-only, static dates — per `test-strategy.md`'s fixture policy,
without editing a single pre-existing fixture.

### Trees added

17 files across six new directories under `tests/fixtures/trees/`, each with
its own `.docs.toml`.

| Tree | Contents | Isolates | Intended finding set |
|---|---|---|---|
| `bodylink-clean/` | `doc.md`, `target.md`, `data.yaml`, `sub/deep.md`. `doc.md` carries every supported form: plain, `./`, fragment, non-Markdown, **directory** (`sub/`), nested, angle, all three title quotings, and a reference definition | every supported form **resolving** | **none** |
| `bodylink-broken/` | `doc.md` with exactly one link, `[the plan](plan.md)`, on **line 8**; `plan.md` absent | E3 | exactly **one** `broken-body-link` |
| `bodylink-excluded-forms/` | one **valid** doc carrying an image, both autolink shapes, a raw-HTML anchor, all three reference *uses*, a backslash-escaped opt-out, empty / fragment-only / `https:` / `mailto:` / protocol-relative / root-absolute destinations, a fenced block with `[<path>](<path>)`, and an inline span containing a link | E5/E8/D2 — **silence** | **none** |
| `bodylink-nested/` | root `back-inside.md` + `sub/deep.md` linking `../back-inside.md`, `../sub/deep.md`, and **`../sub/../back-inside.md`** | D3 resolution base + escape-then-return | **none** |
| `bodylink-archived/` | `[archive] dir = "archive"`; `plan.md` at root; `archive/2026-01-01/old-log.md` (`Lifecycle: archived`, `Archived-reason:`, `Updated: 2026-01-01`) carrying the un-rebased `[the plan](plan.md)` on **line 12** | E1/E2 — the exact damage shape, 132/139 of it | exactly **one** `broken-body-link`, candidate `archive/2026-01-01/plan.md` |
| `bodylink-outside-root/` | one valid `doc.md` with **two** escaping destinations: `../__docs_cli_m27_no_such_dir__/ghost.md`, which cannot exist, and **`../bodylink-outside-root/doc.md`**, self-referential and therefore guaranteed to exist on disk | E7/D4b/Q5 | exactly **two** `outside-root-body-link`, **zero** `broken-body-link` |

### Decisions / issues

- **The two escapes in `bodylink-outside-root` are deliberately different, and
  the pair is the point.** The unreachable one makes "never stat outside the
  root" true *by construction* — there is nothing out there to stat. The
  self-referential one is the harder half of E7: it names a path that provably
  exists, so an implementation that decided the rule with a stat rather than
  with arithmetic would report it as resolving and the fixture would catch it.
  Self-reference is used rather than a sibling fixture so the lock cannot rot
  when a neighbouring tree is renamed.
- **No existing fixture was edited.** The setup census measured all 33
  read-only at zero unresolved destinations and zero escapes, and Phase 3
  re-confirmed it: `git status` shows exactly six new directories and nothing
  else. This is what keeps M27's no-regression proof at a clean zero moved
  ids.
- **The reciprocal-verb constraint is honoured.** None of the six uses
  `precedes`/`follows`, `depends-on`/`required-by`, or `blocks`/`blocked-by`
  — in fact none declares a `Related:` group at all — so the six
  parametrizations they add to
  `test_check_tree_legacy_fixtures_gain_no_new_findings` (23 → **29**) all
  pass, and `test_check_tree_pre_m27_fixtures_gain_no_body_link_findings`
  stays at exactly **33**.
- **Every doc is valid, on purpose.** A `malformed` doc early-returns from
  `check_doc` before any body-link rule, which would make the "silent" locks
  pass for entirely the wrong reason — especially
  `bodylink-excluded-forms`, whose whole job is to prove the *rules* are
  silent rather than that the *document* was skipped. `docs check` exits 0 on
  all six today, so each tree's finding set is exactly its intended one.
- **Line numbers are part of the fixture contract.** `bodylink-broken`'s link
  sits on line 8 and `bodylink-archived`'s on line 12 because Phase 2 asserts
  both frozen messages verbatim, and `<N>` is in them. The archived doc's
  line 12 makes its message `cli.md`'s worked instance byte for byte.
- **`](plan.md)` appears exactly once in `bodylink-archived`**, in the
  archived log. `test_check_tree_bodylink_archived_repaired_copy_is_clean`
  rewrites that one token to `](../../plan.md)` and then asserts the reverse
  substitution reproduces the original file byte for byte and that every other
  file in the tree is untouched — which only means anything while the token is
  unique.
- **Exotic grammar stays inline** (the M25 rule): angle destinations with
  whitespace, percent- and backslash-escapes, parens at and beyond the frozen
  depth, the reference-definition line anchor, multi-line labels, and every
  masking case live in `tests/test_body_links.py`, because they assert on
  parse output rather than on a tree walk. In particular **no committed
  fixture filename contains a space** — `tests/` ships in every sdist — so the
  `%20` end-to-end case is a `tmp_path` builder and only its *parsing* half is
  an inline string.
- **No `src/docs_cli/cli.py` change.**

### Verification

- `.venv/bin/docs check tests/fixtures/trees/bodylink-<each>` — **no
  violations found (exit 0)** for all six. Nothing fires until Phase 6, which
  is what makes each tree's intended finding set exactly its own.
- Read-only prototype census over the six trees, under the Phase-1 frozen
  contract: `bodylink-broken` 1 broken / 0 escapes; `bodylink-archived` 1
  broken (candidate `archive/2026-01-01/plan.md`) / 0; `bodylink-outside-root`
  **0 broken / 2 escapes**; `bodylink-clean`, `-excluded-forms` and `-nested`
  **0 / 0**. Exactly the intended sets.
- `.venv/bin/python -m pytest tests/ -q --co` — **1064 collected** (1058 →
  1064: exactly the **+6** parametrizations the new trees add to
  `test_check_tree_legacy_fixtures_gain_no_new_findings`), zero collection
  errors.
- `.venv/bin/python -m pytest -q` — **122 failed, 942 passed** (129 → 122).
  The **7** locks that flipped GREEN are exactly the ones Phase 2 classified
  degenerate and predicted: `test_check_tree_bodylink_clean_is_clean`,
  `…_excluded_forms_is_silent`, `…_nested_resolves_up_and_down`,
  `…_archived_repaired_copy_is_clean`, `test_check_bodylink_clean_tree_exits_0`,
  `…_excluded_forms_tree_exits_0`, and
  `test_check_verdict_is_identical_from_a_relocated_copy`.
- `test_check_tree_legacy_fixtures_gain_no_new_findings` — **29 passed**
  (23 + 6). `test_check_tree_pre_m27_fixtures_gain_no_body_link_findings` —
  **33 passed**.
- `git status` — exactly six new directories, **no** edit to any pre-existing
  fixture.
- `.venv/bin/ruff check .`, `ruff format --check .`, `mypy src/ tests/` —
  clean. `docs check --root docs` — exit 0. Bundled refs byte-identical;
  INDEX snapshot identical.
- `git diff --stat -- src/docs_cli/cli.py` — **empty**.

## Milestone completion summary

_Not complete._
