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
- Progress: **Implementation-complete (2026-08-14).** All ten phases done
  across `m27/phases-1-4` (Step 1) and `m27/phases-5-10` (Step 2); every
  deliverable met; **1079 passed / 0 failed**; `docs check --root docs` at
  exit 0 over the repaired tree; the `BodyLink` span contract handed to M28.
  The milestone stays `Lifecycle: active` until the M29 publish closeout. All seven setup questions were RESOLVED at setup
  (Q1/Q2/Q5 by the operator; Q3/Q4/Q6/Q7 conductor-resolved) and Phase 1 did
  not re-open them. Q5 was resolved **against** the setup recommendation and
  then **amended** — the hermetic boundary is kept, and an escaping
  destination is reported by path arithmetic as a second rule,
  `outside-root-body-link`, rather than skipped.
- Source: the operator-confirmed body-link decisions in `feedback-log.md`
  (2026-08-09/10) and the M27 registration in `plan.md` (2026-08-10).
- Branch: `m27/milestone-setup` for setup; `m27/phases-1-4` for Step 1
  (Phases 1–4); `m27/phases-5-10` for Step 2 (Phases 5–10).

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | **Done** | 2026-08-14 | Froze the supported Markdown grammar subset, the masking rules, destination classification/normalisation/resolution, **the containment test and its precedence over existence**, both findings (`broken-body-link`, `outside-root-body-link`) with severity / message template / exit code / ordering, the `BodyLink` span contract M28 consumes, and the legacy-tree policy — against the resolved Q1–Q7. |
| 2. Write Tests (RED) | **Done** | 2026-08-14 | Scanner unit tests over every supported and every excluded form; both rules' integration + subprocess/JSON locks; the no-double-report precedence lock and the never-stat-outside-the-root lock; the E5/E6 false-positive and false-negative locks; the pathological-input runtime lock. |
| 3. Create Data/Fixtures | **Done** | 2026-08-14 | `bodylink-*` trees, one semantic each, including `-outside-root` (escape aimed at a path that cannot exist) and the `../sub/../back-inside.md` normalise-back case; exotic grammar as inline strings (the M25 rule). |
| 4. Run Tests (RED Baseline) | **Done** | 2026-08-14 | Classified failure set; the transitional classification of `test_check_dogfood_repo_docs_is_clean`. |
| 5. Update Base Interfaces | **Done** | 2026-08-14 | The whole pure scanner in one banner section — `BodyLink`, length-preserving `_mask_code`, `scan_body_links`, `classify_destination`, the containment/resolution helpers and `body_link_findings` — with **no** rule wired, so the 18 rule/CLI/skill tests stay honestly RED at the `check_doc` seam. 119 cleared; both quadratic shapes avoided; `raw` sliced from the ORIGINAL text. Seven grammar points the contract left silent (S1–S6, S9) settled in `cli.md` and its mirror. |
| 6. Implement Offline/Core Path | **Done** | 2026-08-14 | Both rules wired into `check_doc` (three lines, after the `broken-ref` group and before `stale`) **and** the D6 live-tree repair in the same commit: 140 occurrences over 30 documents, split 132 root-rebase / 5 move-map / 2 playbook-URL / 1 escape-URL, driven by the Phase-5 scanner and spliced by offset. Six independent checks prove no other byte moved; re-census 0 broken / 0 escapes with the span count still 393. |
| 7. Update Tool/Wrapper Layer | **Done** | 2026-08-14 | `docs check`'s argparse description now names both rules' conditions; the bundled `SKILL.md` check row and `references/use-cases.md` (the *Validate in CI* row plus a new M27 upgrade section) name both rule ids and **both** repairs; `CHANGELOG.md` gains one `Added` entry per rule, a BREAKING `Changed` entry, and the adopter upgrade recipe. No spec edit was needed — `cli.md` and `convention.md` were already current, so both mirrors stayed byte-identical. No version bump. Suite fully GREEN. |
| 8. Run Tests (GREEN) | **Done** | 2026-08-14 | **1079 collected, 1079 passed, 0 failed**, zero xfail/xpass, zero tracebacks; all gates clean; the `comm` proof against **both** anchors shows 0 ids removed since `d61da1d` and since `ddf0a45`, and **0 added by Step 2** — `git diff ddf0a45 -- tests/*.py` is empty, so no test was touched to reach GREEN. |
| 9. Integrate / Accept / Dogfood | **Done** | 2026-08-14 | Pre-repair damage replayed through the CLI (140 findings, 139 + 1, exit 2); the documented recipe walked from `--json` alone reaches exit 0 with **0 destination-token mismatches** against the repaired tree; identical stdout and exit code from a with-sibling and a bare location, 0 stats outside the root under a spy; all 39 fixture trees + the bundled skill sweep clean bar M27's three damaged ones; runtimes recorded (183 ms live tree, 61 ms for the 303 KB adversarial set — 33× under the 2.0 s bound). |
| 10. Quality, Docs, Refactor | **Done** | 2026-08-14 | `/simplify` pass with every candidate recorded (four applied, six considered and rejected); `architecture.md` › `check` and `test-strategy.md` › *What we don't test* closed, README's one-line summary extended; the Phase-9 quality item folded in (live-tree scan 183 ms → 81 ms, `docs check` 0.16 s end to end); completion summaries written. |

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

**`tests/test_body_links.py`** (new, **105** items at this commit; **106**
after the Step-1 audit and **119** after the review fold-in) — the pure
scanner seam,
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
  (Counts as of this commit. The Step-1 audit below added two locks; the
  restated totals are in the Phase-4 entry.)
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
  errors. (Counts as of this commit; restated in the Phase-4 entry after the
  Step-1 audit.)
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

## Phase 4 — Run Tests (RED Baseline) — 2026-08-14

### Objective

Prove the new tests fail for the intended missing behaviour and for nothing
else, and prove **mechanically** — not by assertion — that every pre-existing
test is still present and still passing.

### Baseline

```
.venv/bin/python -m pytest tests/ -q --co   →  1079 collected, 0 collection errors
.venv/bin/python -m pytest tests/ -q        →  137 failed, 942 passed
```

(Counts **restated twice**: after the Step-1 same-instance audit recorded
below, which added 2 locks, and after the fresh-eyes review fold-in, which
added 13 more. At the Phase-4 commit itself the figures were 1064 collected,
122 failed, 942 passed. The classification, the arithmetic and every
conclusion below are unchanged, because all 15 added locks join named RED
families and none is GREEN at baseline — the GREEN-at-baseline set is still
exactly 47.)

Zero collection errors, zero xfail, zero xpass, **zero tracebacks**
(`grep -c "Traceback (most recent call last)"` → **0**). Note the M26
false-positive trap: several tests assert `"Traceback" not in proc.stderr`,
which a failure listing echoes, so the bare word is not a usable probe — here
both probes read 0, which is the honest way to say it.

Exception-class census over `--tb=line`, one line per failure: **119
`AttributeError`, 18 `AssertionError`, nothing else** (119 + 18 = 137).

### Mechanical no-regression proof

Test-id lists collected from a throwaway `git worktree` at the pre-M27 commit
`d61da1d` and from HEAD, then intersected with the failing set:

```
pre-existing ids at d61da1d                        895
  deliberately removed at M27 (comm -23)             0
  carried over to HEAD (comm -12)                  895
carried-over ids failing (comm -12 failed old)       0
new ids added by M27 (comm -13)                    184      895 + 184 = 1079 ✓
```

**M27's claim is cleaner than M26's, and it is stated rather than implied:**
`comm -23` is **0** and `comm -12 failed old` is **0**, because M27 removes
and modifies **no** pre-existing test. Phase-1 amendment 3 is what buys that —
adding a sibling lock instead of narrowing `_legacy_tree_names()` — and it is
corroborated file by file: `git diff d61da1d -- tests/test_cli_check.py` and
`… -- tests/test_check.py` show **zero** deleted lines each (the only edit to
an existing file is an added `import shutil`, which ruff's import sorter
placed above `from datetime import date`). So
`test_check_tree_legacy_fixtures_gain_no_new_findings`, `_legacy_tree_names()`,
and the two closed-record pins
(`test_check_json_emits_finding_array`,
`test_check_missing_inverse_json_record_keys_unchanged`) are byte-identical to
the baseline. M26's log rightly calls hiding a moved id the failure mode this
check exists to catch; for M27 the honest number really is zero.

### RED classification — all 137 traced to a reason

| Count | Family | RED reason |
|---|---|---|
| 119 | `tests/test_body_links.py` (the whole module) | `AttributeError` through the `_m27()` getattr indirection on `BodyLink`, `_mask_code`, `scan_body_links`, `classify_destination`, `normalise_body_link_target`, `_body_link_is_contained`, `body_link_findings`, `BODY_LINK_KINDS`, `DESTINATION_KINDS`, `MAX_DESTINATION_PAREN_DEPTH` — all landing in Phase 5 |
| 10 | `tests/test_check.py` M27 rule tests | plain assertion — neither rule exists, so `check_doc` returns no body-link finding and `check_tree` returns `[]` for `bodylink-broken`, `bodylink-archived` and `bodylink-outside-root`. Covers both frozen messages, the `broken-ref` → body-link → `stale` ordering, `exit_code_for` == 2, E7's does-exist escape, E6's indented blockquote link, and the nested-vs-root `INDEX.md` split |
| 5 | `tests/test_cli_check.py` M27 tests | plain assertion — the fixture trees exit **0** today. Each also asserts its frozen message, so none is falsely GREEN |
| 1 | `tests/test_cli_touch.py` | plain assertion — `docs touch --check` inherits the rules, and there are none yet |
| 2 | `tests/test_skill.py` | plain assertion — the bundled skill's `docs check` row names neither rule id. Phase 7 |

### GREEN-at-baseline locks, classified by name

47 of the 184 new ids are GREEN at baseline (184 − 137). Every one is
classified, and the arithmetic closes: 1 + 3 + 2 + 1 + 1 + 33 + 6 = 47.

| Lock | Honest status |
|---|---|
| `test_check_dogfood_repo_docs_is_clean` (pre-existing, untouched) | **TRANSITIONAL** — genuine today; would be RED between wiring the rules and repairing the tree; restored inside Phase 6's own commit (E4/D6). The single reason the 140-occurrence repair cannot slip to Phase 9, and the one lock whose meaning changes across a phase boundary |
| `test_check_doc_malformed_doc_gets_no_body_link_findings` | **degenerate** ×1 — genuine once `check_doc`'s early return is load-bearing |
| `test_check_tree_bodylink_clean_is_clean`, `…_excluded_forms_is_silent`, `…_nested_resolves_up_and_down` | **degenerate** ×3 — the over-fire guard from Phase 6 |
| `test_check_bodylink_clean_tree_exits_0`, `…_excluded_forms_tree_exits_0` | **degenerate** ×2 — the same guard at the subprocess surface |
| `test_check_verdict_is_identical_from_a_relocated_copy` | **degenerate** ×1 — the hermeticity lock from Phase 6 |
| `test_check_tree_bodylink_archived_repaired_copy_is_clean` | **degenerate** ×1 — becomes the proof that the documented repair recipe works, and that its blast radius really is one destination token |
| `test_check_tree_pre_m27_fixtures_gain_no_body_link_findings[…]` ×33 | **degenerate** ×33 — the genuine regression lock from Phase 6, and the one that delivers the milestone's "all 33 pre-M27 trees" coverage |
| `test_check_tree_legacy_fixtures_gain_no_new_findings[bodylink-*]` ×6 | **genuine** ×6 — the six new trees must add no `missing-inverse`, which constrains what Phase 3 could put in them |
| `test_check_json_emits_finding_array`, `test_check_missing_inverse_json_record_keys_unchanged` | **genuine**, untouched — the closed-key-set pins |
| `test_bundled_ref_matches_source[cli.md\|convention.md]`, `test_bundled_skill_has_no_repo_relative_links`, `test_installed_skill_references_do_not_depend_on_source_checkout` | **genuine** — Phase 1's spec edits must not break byte identity, introduce `](../`, or name `../src/docs_cli/` |
| `test_a3_project_version_is_1_8_0`, `test_c2_docs_version_is_1_8_0` | **genuine** — no version bump in M27 (M25 — D6) |

### Falsely-GREEN check at this gate

No falsely-GREEN test was found, and the family that would have been one was
already caught and fixed **in Phase 2**: `load_config` tolerates a missing
directory and `check_tree` then walks nothing, so the three silent-tree locks
and the two exit-0 subprocess locks would have passed on fixture trees that
were never written. Routing every `bodylink-*` tree through an
existence-asserting helper made them honestly RED until Phase 3, and their
flip to GREEN when Phase 3 landed is recorded evidence that the guard worked —
**7** locks flipped, exactly the set Phase 2 predicted, and not one more.

Each of the 5 subprocess RED tests was re-checked one by one against the M26
lesson: every one asserts a frozen contract string in addition to its exit
code, so none can be satisfied later by an unrelated exit 2. The
`bodylink-*` trees exit **0** today, so the returncode half is honest RED on
its own — but the message half is what keeps it honest afterwards.

### Phase-5/6/7 follow-through (carried from Phase 1, restated so it cannot be lost)

1. `Finding`'s docstring rule enumeration gains both ids (Phase 5/6).
2. `docs check`'s argparse `description` — currently "and broken `Related:`
   references" — must name body links (Phase 7 surface-parity gate).
3. The bundled `SKILL.md` `docs check` row (Phase 7) — locked by
   `test_skill_md_teaches_body_link_validation`.
4. The bundled `references/use-cases.md` validate row and the 2.0 upgrade
   block (Phase 7) — locked by `test_bundled_use_cases_teaches_body_link_repair`.
5. `CHANGELOG.md` under the existing `UNRELEASED` heading, with the adopter
   recipe for both rules. **No** version bump (M25 — D6).
6. `docs/test-strategy.md` › *What we don't test* — "the body content is
   opaque" (Phase 10). `convention.md`'s twin statement was corrected in
   Phase 1 because it is on the byte-parity gate.
6b. **`tests/fixtures/expected/docs-INDEX.md` must be regenerated inside
   Phase 6's own commit** (added by the fresh-eyes review). The D6 repair bumps
   `Updated:` on 29 archived documents plus `charter.md`;
   `tests/test_cli_index.py::test_index_output_matches_frozen_snapshot`
   compares the regenerated index against that snapshot, and
   `_normalize_generated_date` blanks **only** the
   `_Generated <date>._` line — every per-entry `Updated YYYY-MM-DD.` is
   compared literally, so all 30 bumps land in the diff. It rides with the
   `test_check_dogfood_repo_docs_is_clean` restoration, for the same E4
   reason.
7. The Phase-5 linearity note in the milestone's *Decisions (Phase 1 —
   BINDING)*: precompute the blank-line bounds, and resume a failed candidate
   at its closing `]` rather than at the opening `[` — with the cached
   position reused after the image (`!`) rejection, which is the one case that
   depends on the opening bracket.

### Verification

- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 47 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 48 source files.
- `.venv/bin/docs check --root docs` — no violations (exit 0).
- `cmp docs/{cli,convention}.md src/docs_cli/skill/references/` — identical.
- `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.
- `git diff --stat d61da1d -- src/docs_cli/cli.py` — **empty**. Phases 1–4
  changed no product code, by design.

## Step-1 same-instance audit — 2026-08-14

Consistency / completeness / accuracy audit over Phases 1–4, run by the
implementing instance before handing back. **Six findings, all fixed; nothing
needed an operator decision.** Two items are surfaced for the operator /
reviewer without being auto-decided (below).

### Accuracy — tests vs the frozen spec

The audit's central check was mechanical: extract every string constant
containing `body link at line` from the four test modules (via `ast`, so
implicit concatenations are folded exactly as Python folds them), and check
each against the two templates frozen in `docs/cli.md`. **Five asserted
messages, all conforming**, with only `<N>`, `<raw>` and `<candidate>`
substituted:

```
body link at line 8  does not resolve to an existing path: plan.md (resolves to plan.md)
body link at line 12 does not resolve to an existing path: plan.md (resolves to archive/2026-01-01/plan.md)
body link at line 8  leaves the docs root: ../shared/glossary.md (normalises to ../shared/glossary.md); links outside the tree must be URLs
body link at line 10 leaves the docs root: ../shared/glossary.md (normalises to ../shared/glossary.md); links outside the tree must be URLs
```

The line-12 instance is `cli.md`'s worked instance byte for byte. No test
asserts a string the spec does not carry, and no frozen string in the spec is
left unasserted.

### Findings and fixes

| # | Finding | Fix |
|---|---|---|
| 1 | **`docs/plan.md` still said M27 had started no TDD phase** — two places: the v2.0 narrative and the M27 milestone row, both frozen at "milestone-setup complete; Phase 1 next". `status.md` and the milestone doc had moved on; `plan.md` had not. | Both updated to Step 1 complete with the baseline figures. |
| 2 | **The E5 coverage claim was wider than the test.** The milestone's *Evidence → regression coverage* promises the E5 lock is asserted on "the exact `[<path>](<path>)` and `` `[cli.md](cli.md)` `` shapes taken from this tree", but the test carried only `[<path>](<path>)` and `[name](name)`. There are **three** measured inline-span shapes, not one. | `test_mask_code_e5_shapes_from_this_repository` now carries all three verbatim, each cited to the archived log and line it was measured at: `[name](name)` (`m1-parser-and-index-log.md:359`), `[old-plan.md](old-plan.md)` (`m2-mutating-verbs-log.md:114`), `[cli.md](cli.md)` (`:523`). |
| 3 | **The ordering lock pinned only half of R7.** It asserted `["broken-ref", "broken-body-link"]`, which proves the findings follow the `broken-ref` group but says nothing about their coming **before** the `stale` block — and appending a new rule at the end of `check_doc` is the likeliest way to get that wrong. | The doc now also trips the stale window, and the assertion is the full three-element sequence `["broken-ref", "broken-body-link", "stale"]`. |
| 4 | **The nested-vs-root `INDEX.md` split was specified but unlocked.** `cli.md` states both halves — the root-level generated index is never scanned, a nested one is an ordinary document and **is** — and no test covered either. A rule that skipped every file named `INDEX.md` at any depth would have passed the whole suite. | New `test_check_tree_root_index_is_not_scanned_but_a_nested_one_is`: a tmp tree with a broken link in each, asserting exactly one finding and that it belongs to the nested one. |
| 5 | **`test_mask_code_leaves_every_unmasked_byte_untouched` under-constrained the mask.** Its per-character loop allowed any character that happened to appear in the code regions to be masked anywhere in the document, so it would have passed an implementation that blanked stray letters outside code. | Replaced with an exact expected-mask assertion — the one test that pins "replaces the contents of code with spaces" character by character. |
| 6 | **`BodyLink`'s immutability was in the frozen signature but not in a test**, and it is load-bearing for M28: a mutable record invites an in-place edit of `raw` or `start` between collecting spans and splicing replacements, after which every remaining span in the same document is silently wrong. | New `test_body_link_record_is_immutable`, asserting `dataclasses.FrozenInstanceError`. Also hardened the never-stat lock to spy on **both** `Path.exists` and `Path.is_file`, so it does not depend on which the existence test happens to call. |

Two consistency edits went with them: the milestone's *Testing and quality
gate* said the 33-tree lock was `test_check_tree_legacy_fixtures_gain_no_new_findings`
"extended", which Phase-1 amendment 3 makes false — it is a **sibling** and
the original stays byte-identical — and
`test_body_link_findings_frozen_broken_message`'s docstring now names what its
line **12** actually locks: contract point 10, that the scan runs over the
whole document text. A scanner fed `parse_metadata_block`'s body would report
that same link at line 4 and hand M28 spans off by the height of every
metadata block.

### Completeness — E1–E8 walked row by row

Every row of the milestone's *Evidence → regression coverage* table was checked
against a named test, for the parts that fall inside Phases 1–4:

- **E1/E2** — `bodylink-archived` yields exactly one `broken-body-link` with
  candidate `archive/2026-01-01/plan.md`; the repaired copy yields none and is
  byte-identical everywhere else. The live-tree half is Phase 6/8.
- **E3** — `test_check_broken_body_link_exits_2_and_names_the_line` plus the
  JSON record lock.
- **E4** — `test_check_dogfood_repo_docs_is_clean` classified TRANSITIONAL at
  Phase 4, untouched.
- **E5** — finding 2 above; now all four measured shapes.
- **E6** — `test_mask_code_does_not_mask_four_space_indented_prose` and
  `test_check_tree_indented_link_in_a_blockquote_is_scanned`.
- **E7** — `bodylink-outside-root`'s two escapes (one impossible, one provably
  existing), the no-double-report lock at both seams, the `Path.exists` spy,
  and the escape-then-return case. The `charter.md` conversion is Phase 6.
- **E8** — every supported form and every excluded form has a named lock; the
  33-tree sibling covers both rules across every pre-M27 fixture.

### Surfaced for the operator / reviewer — NOT auto-decided

1. **`broken-body-link`'s message does not name its repair in words.** The
   conductor resolution that specified the escaping message also asserted
   "both templates name the repair, mirroring `missing-inverse`'s
   `(or remove the edge)`" — but only `outside-root-body-link`'s frozen
   literal does so (`; links outside the tree must be URLs`). Phase 1
   implemented the frozen literals exactly as given rather than extending one
   of them with a clause nobody froze; `broken-body-link` names its repair
   implicitly, by printing the candidate path the tool probed, which is what
   lets an agent choose between fixing the link and creating the file. If the
   reviewer wants the symmetry made explicit, it is a one-line template change
   in Phase 7 plus the five test strings above.
2. **The specs now describe behaviour the shipped code does not have.**
   `docs/cli.md` and `docs/convention.md` — which ship in the sdist and are
   mirrored into the bundled skill — document both rules as of Phase 1, while
   the rules themselves land in Phase 6. This is the M25/M26 precedent applied
   unchanged (M26's Phase 1 rewrote the whole `docs archive` section before
   Phase 6/7 implemented it) and the window closes inside this milestone, well
   before the M29 publish. Recorded rather than assumed.

### Verification after the fixes

- `.venv/bin/python -m pytest tests/ -q --co` — **1066 collected, zero
  collection errors** at the audit commit (**1079** after the review fold-in).
- `.venv/bin/python -m pytest -q` — **124 failed, 942 passed**; census **106
  `AttributeError` + 18 `AssertionError`**, nothing else; zero tracebacks.
- Mechanical no-regression proof re-run against `d61da1d`: 895 carried over,
  **0** removed, **0** pre-existing failing, **171** added; 895 + 171 = 1066.
- `.venv/bin/ruff check .`, `ruff format --check .`, `mypy src/ tests/` —
  clean. `docs check --root docs` — exit 0. Bundled refs byte-identical.
  INDEX snapshot identical.
- Read-only prototype census over `docs/` after every Phase-1–4 doc edit —
  still **139** unresolved and **1** escape, i.e. the milestone's own
  documentation added no new body-link damage and removed none (the repair is
  Phase 6's).
- `git diff --stat d61da1d -- src/docs_cli/cli.py` — **empty**.

## Step-1 fresh-eyes review fold-in — 2026-08-14

An independent fresh-eyes review of Step 1 found **no blockers** and
independently reproduced the whole baseline — collection, failure counts,
exception census, the `comm` proof, both byte-parity `cmp`s, the INDEX
snapshot, the empty `cli.py` diff, all six fixture trees exiting 0, and the
33 / 29 parametrization counts — and re-scanned the Phase-1 spec edits to
confirm they add zero new scannable spans. It returned nine should-fix items
and four nits, **all conductor-resolved**; every one is folded in below.

**The unifying theme is one failure mode: a wrong-but-plausible Phase-5
implementation passing the suite.** That is exactly what Step 1 exists to
prevent, so these are contract-integrity fixes rather than polish.

### Spec corrections (`docs/cli.md`, mirrored byte-identically)

| # | Correction |
|---|---|
| SF3 | **Whitespace is permitted on BOTH sides of the destination.** Rule 3 explicitly allowed *leading* whitespace while rule 5's disqualifier ("anything other than a title between the destination and the closing `)`") read as forbidding *trailing* whitespace — a self-contradiction. Conductor-resolved to permit both, matching the Step-1 plan's own `optional-ws` grammar and CommonMark; rule 5's disqualifier is now scoped to **non-whitespace, non-title** content. |
| SF4 | **An unclosed fence masks to the end of the document** (CommonMark). Previously unspecified, and `_LENGTH_CASES[4]` is literally that shape while asserting only length and newline offsets. The rationale is recorded, including the **deliberate divergence** from the single-line inline-span rule: the masker models what actually renders as a link, and every renderer these documents pass through takes an unterminated fence to EOF — so flagging a link inside one would report something no reader ever sees. A lone backtick is the opposite case: a common, invisible accident in prose, where running to EOF would buy unbounded false negatives. An unclosed fence is rare, line-anchored, 3+ characters and visually obvious; bounding the damage is warranted for one and not the other. |
| SF5 | **The `outside-root-body-link` worked instance contradicted its own template six lines above**, dropping the mandated `; links outside the tree must be URLs` clause that the template and every test carry. Inherited from the Step-1 plan's §1.1(e) rather than introduced. Fixed in both files, byte parity preserved. Distinct from the repair-clause asymmetry surfaced by the audit, which the operator has now settled as intentional and unchanged. |
| SF9 | **Three open questions in the reference-definition rule, all settled** — and they matter beyond the finding set, because `scan_body_links`' output is M28's handoff: **(a)** the destination must **begin on the same line as the label** (the "optional whitespace" never spans a newline), keeping the rule line-anchored end to end and the scanner bounded; **(b)** a **trailing non-title remainder disqualifies** it, the same rule the inline form applies, stated once and referenced rather than duplicated; **(c)** an **empty destination is not a recognised reference definition at all**, so `[plan]:` yields no `BodyLink` rather than one carrying a zero-width span for M28 to splice into. |

### Test hardening

| # | Gap | Lock added |
|---|---|---|
| SF1 | **A wrong decode order passed the entire suite.** All three BINDING consequences were untested, mechanically confirmed: no destination in the module contained both a `%` and a `#`. The *natural* implementation — `unquote()` then `split("#", 1)` — inverts the frozen order and went GREEN. | Three tests plus a classification sibling: `plan%23x.md` → `path == "plan#x.md"`, `fragment is None`; `sub%2Fx.md` → `path == "sub/x.md"` and its normalised join; `plan\#x.md` → `fragment == "x.md"`, `path == "plan\"`; and `classify_destination("%23x") == "local"`. The highest-value item in the review. |
| SF2 | **The ordering lock never mixed the two rules.** Its three destinations were all `broken-body-link`, and every test that *does* mix them happened to put the escaping link first — so an implementation grouping by rule id rather than by source position passed everything. | `test_body_link_findings_source_order_interleaves_the_two_rules`: a broken destination **preceding** an escaping one on the same line, asserting `["broken-body-link", "outside-root-body-link"]`. |
| SF3 | The three whitespace shapes were unrecognised as cases. | `[a]( plan.md)`, `[a](plan.md )`, `[a](plan.md "T" )` added to `_SPAN_CASES`, each asserting the span excludes the surrounding whitespace. |
| SF4 | Nothing pinned which way an unclosed fence went. | `test_mask_code_unclosed_fence_masks_to_end_of_document`, on the `_LENGTH_CASES[4]` shape extended with a link on a *later* line. |
| SF6 | **The never-stat spy's containment test was lexically weaker than its docstring claimed.** `Path.is_relative_to` is a pure prefix comparison, so `Path("/a/b/../../etc/passwd").is_relative_to(Path("/a/b"))` is `True` — the very probe the lock forbids would have been classified as inside the root. Its real lock today was the rule-sequence assertion beside it. | Probed paths are `os.path.normpath`-normalised before comparison; the `assert probed` guard against a vacuous pass is kept. |
| SF8 | **The angle-destination newline rule had no test**, so an implementation letting `<…>` span lines passed. (The pathological case is an unterminated `<` with no newline — a different failure mode.) | `test_scan_angle_destination_does_not_cross_a_newline`, including a mixed document where the terminated destination survives and the newline-crossing one does not. |
| SF9 | The three settled points had no locks. | One test each: destination on the following line, trailing remainder, and empty destination. |
| nit | `test_check_tree_bodylink_archived_reproduces_the_unrebased_shape` used a rule-filtered helper while its three siblings used the unfiltered one, so an unexpected extra finding in that tree would have slipped through. | Switched to `_bodylink_findings`; the now-unused filtered helper is deleted. |
| nit | **No test asserted a span or a line number for a link FOLLOWING a masked region** — `_SPAN_CASES`' prefix was fence-free and the line/column test had no code in it. Length-preserving masking exists precisely so offsets survive it, so an implementation reporting offsets into the *masked* string passed every case (the two strings agree wherever nothing is masked). | The `_SPAN_CASES` prefix now carries **both** a fenced block and an inline span, and asserts `line`/`column` derived from the offset; `test_scan_line_and_column_are_one_based` moved its link to line 7, behind a fence and a span. |
| nit | `_contained("..foo.md")` was untested, so a predicate written `startswith("..")` — the obvious near-miss — would over-fire on an ordinary in-root file whose name begins with two dots. | Added, with `sub/..foo.md`. |

### Documentation

- **SF7 — a Phase-6 trap that would have surfaced as a mystery failure.** The
  D6 repair bumps `Updated:` on 29 archived documents plus `charter.md`, and
  `tests/test_cli_index.py::test_index_output_matches_frozen_snapshot`
  compares the regenerated index against
  `tests/fixtures/expected/docs-INDEX.md`. Its
  `_normalize_generated_date` helper blanks **only** the `_Generated <date>._`
  line — every per-entry `Updated YYYY-MM-DD.` is compared **literally**, so
  all 30 bumps land in the diff. The snapshot must be regenerated **inside
  Phase 6's own commit**, alongside the `test_check_dogfood_repo_docs_is_clean`
  restoration and for the same E4 reason. Recorded as row 7 of the milestone's
  follow-through table and as item 6b here, worded so Phase 6 cannot miss it.
- The milestone's amendment preamble said "**Two** frozen items … **Both** are
  recorded" above a **three**-row table (the impl log already said three).
- **Deliverable 4 stays unticked, and now says why.** Everything it names
  exists in the suite, but a RED lock is not yet locking; it is ticked at
  Phase 8 when the suite goes GREEN. The checklist row carries a parenthetical
  so the empty box reads as deliberate rather than as an oversight.

### The two audit-surfaced items, settled by the operator

1. **The repair-clause asymmetry between the two messages is intentional and
   stays.** The clause earns its place in `outside-root-body-link`, where the
   repair is non-obvious; `broken-body-link` already prints the raw
   destination and the resolved candidate, which is what an agent needs to
   choose between fixing the link and creating the file.
2. **The specs describing Phase-6 behaviour ahead of the code is accepted**,
   per the M26 precedent.

### Verification after the fold-in

- Every new expected value was first checked against a read-only prototype of
  the **amended** contract — **33/33** assertions reproduce, so the contract
  the tests pin is demonstrably implementable rather than merely plausible.
  The prototype's census over `docs/` is unchanged at **139** unresolved and
  **1** escape after the reference-definition rules (a)/(b)/(c) landed, so the
  three settled points move nothing on real data.
- `.venv/bin/python -m pytest tests/ -q --co` — **1079 collected, zero
  collection errors**.
- `.venv/bin/python -m pytest -q` — **137 failed, 942 passed**; census **119
  `AttributeError` + 18 `AssertionError`**, nothing else; zero tracebacks,
  zero xfails.
- Mechanical no-regression proof re-run against `d61da1d`: **895** carried
  over, **0** removed, **0** pre-existing failing, **184** added;
  895 + 184 = 1079. The GREEN-at-baseline set is still exactly **47**, so the
  Phase-4 classification table needs no re-classification — all 13 review
  locks are RED and join named families.
- `.venv/bin/ruff check .`, `ruff format --check .`, `mypy src/ tests/` —
  clean. `docs check --root docs` — exit 0.
- `cmp docs/{cli,convention}.md src/docs_cli/skill/references/` — identical.
  `](../` still **0** in both specs and all six bundled skill files;
  `../src/docs_cli/` still absent. INDEX snapshot identical.
- `git diff --stat d61da1d -- src/docs_cli/cli.py` — **empty**.

## Phase 5 — Update Base Interfaces — 2026-08-14

### Objective

Land the whole pure scanner — the `BodyLink` record, the length-preserving
`_mask_code`, the `scan_body_links` grammar, `classify_destination`, the
resolution/containment helpers, **and `body_link_findings`** — while wiring
**no** rule, so the 18 rule/CLI/skill tests stay honestly RED at the seam.

`body_link_findings` lands here rather than in Phase 6 because
`tests/test_body_links.py` calls it directly in 12 tests; `check_doc` is the
seam, and it is untouched.

### Actions taken

One product file, `src/docs_cli/cli.py`, plus the spec amendments below.
**No test file was edited** — Step 1 wrote all 184 of M27's ids and Step 2
needs none of them changed.

1. **Imports and docstring.** `string` and `urllib.parse` join the stdlib
   block (`posixpath` was already there); the module docstring gains one M27
   sentence beside the M25/M26 ones. Still stdlib-only.
2. **Vocabulary.** `BODY_LINK_KINDS`, `DESTINATION_KINDS` and
   `MAX_DESTINATION_PAREN_DEPTH` next to `ARCHIVE_EXCLUSION_REASONS`.
3. **Model.** `BodyLink` — a frozen dataclass — after `ArchivePlan`, with a
   docstring naming M28 as the second consumer and stating why the record is
   frozen and why the span includes the angle brackets.
4. **A new banner section**, *Markdown body links — the shared scanner
   (M27 — D1/D2/D5)*, between `_related_pairs` and `check_doc`; `check_doc`
   and everything after it now sit under a *Check rules, query, and JSON
   records (M3)* banner. Contents, in order: `_FENCE_RE`, `_SCHEME_RE`,
   `_ESCAPABLE`, `_mask_inline_spans`, `_mask_code`, `_escape_flags`,
   `_line_starts`, `_blank_line_starts`, `_unescape_backslashes`,
   `_split_destination`, `_scan_destination`, `_scan_title`, `_skip_spaces`,
   `_close_inline`, `_close_reference_definition`, `scan_body_links`,
   `classify_destination`, `normalise_body_link_target`,
   `_body_link_is_contained`, `body_link_findings`.
5. **`Finding`'s docstring rule enumeration** gains `broken-body-link` and
   `outside-root-body-link` (Phase-1 follow-through item 1, done here rather
   than in Phase 6 so the enumeration never lags the vocabulary).
6. **`docs/cli.md` + its byte-identical mirror** gain the seven grammar
   resolutions below.

The six frozen signatures landed verbatim. Three implementation points are
load-bearing and easy to lose, so they are recorded here as well as in the
code's docstrings:

- **`raw` is sliced from the ORIGINAL text** (`raw = text[start:stop]`), never
  from the mask. That is what makes `text[start:end] == raw` true *by
  construction* rather than by coincidence. An implementation that builds
  `raw` from the masked string passes 15 of the 16 `_SPAN_CASES` — every case
  whose destination contains no masked byte — and hands M28 a subtly wrong
  record.
- **Both quadratic shapes the Phase-1 linearity note names are avoided.** The
  blank-line bound comes from a monotonic cursor into a precomputed
  `_blank_line_starts` list, never from a fresh `find("\n\n", i)` per
  candidate; and the outer scan resumes at the candidate's `]` (or, when no
  `]` exists before the bound, at the bound itself), never at the opening
  `[` + 1. The image rejection is the one case that depends on the opening
  bracket, and it reuses the cached closing position rather than rescanning.
  Two further bounds do the same job inside the destination parser: the
  depth-4 early return, and the newline bound on an angle destination.
- **`_mask_inline_spans` builds its partner index in one backward pass.** The
  obvious "scan forward from every opener" is quadratic on a line of
  unmatched backtick runs.

### Grammar resolutions recorded in `cli.md` (S1–S6, S9)

Seven points the frozen contract left silent had to be settled for the
scanner to exist. Every one of them changes either what `scan_body_links`
returns — M28's input — or which links the masker lets through, so all seven
are **adopter-visible grammar** and are recorded in `docs/cli.md` (mirrored
byte-identically into `src/docs_cli/skill/references/cli.md`), not only here.
`cli.md` is the contract that ships in the sdist and that M28 will be
implemented against; a grammar point settled only in an implementation log is
a point where the next implementer silently diverges, and "zero occurrences
today" is precisely the reasoning that produced 139 broken links.

| # | Resolution | Why the frozen form could not stand | Where |
|---|---|---|---|
| S1 | **`[a]()` IS a recognised inline link**, with a **zero-width** destination token at the first non-whitespace character after the `(`, classified `empty` and therefore silent. | Rule 6(c) disqualifies the empty *reference-definition* form as an explicit **exception**, which only reads as one if the inline form is recognised — and `cli.md`'s classification table already gives `[a]()` as the `empty` example. `bodylink-excluded-forms` goes from 5 recognised spans to 6; **zero findings change**. | `cli.md` rule 3 |
| S2 | **A newline is ordinary whitespace on both sides of an inline destination**, so a destination on its own line between the `(` and the `)` is a link. | Rule 3 permits "optional whitespace on both sides" and rule 3 itself calls a newline whitespace, but never says whether the two sentences compose. Matches CommonMark and keeps one bound for the whole candidate. Measured behaviour-neutral: **zero occurrences** in `docs/`, the 39 fixture trees, or the bundled skill. | `cli.md` rule 3 |
| S3 | **A blank line is a whitespace-only line** (CommonMark), and **one bound covers the whole candidate** — label, destination and title alike. | Phase 1 stated the bound only for the label scan. Bounding only the label leaves the destination parser free to run to EOF on an unterminated candidate, which is exactly the linearity the runtime lock measures. | `cli.md` rule 1 |
| S4 | **A closing fence is the same character, length ≥ the opening marker, and only whitespace after the marker**; the **entire opening fence line is preserved verbatim**, info string included. | "Closed by a fence of the same character and equal or greater length" says nothing about an info string on the closing line, and nothing about whether the marker line is content. The second half was already pinned by `test_mask_code_leaves_every_unmasked_byte_untouched`'s exact expected mask, so recording it documents locked behaviour rather than choosing it. | `cli.md` › *What the scanner never sees* |
| S5 | **A reference definition's label opens and closes on ONE line**, and an unescaped `)` at depth 0 terminates a refdef destination exactly as it does an inline one (the trailing-remainder rule then disqualifies the definition). | "Line-anchored end to end" is what rule 6(a) already claims, but the label half was never said; and rule 6 defines the destination as "the same plain-or-angle token", which leaves the `)` question open. **Zero occurrences either way** — the repository contains no reference definitions at all. | `cli.md` rule 6 |
| S6 | **A title stays inside the candidate's blank-line bound, and a `(…)` title is scanned to its first unescaped `)` with NO nesting.** | Rule 5 names the three quotings and the disambiguation rule but not the `(…)` form's own nesting behaviour. No nesting is the simplest rule that keeps rule 5's whitespace-based destination/title split honest. | `cli.md` rule 5 |
| S9 | **`Path.exists()` is kept, so a dangling symlink inside the root is `broken-body-link`.** | Q7 says "any existing filesystem entry", which is silent on a link whose target is missing. `.exists()` follows symlinks, and reporting is correct: the destination is unreachable from the reader's point of view, which is what the rule is for. Switching to `os.path.lexists` would also weaken the `Path.exists` / `Path.is_file` spy lock. This is **existence**, not containment — containment stays lexical and follows nothing. | `cli.md` › *Resolution and containment* |

### Decisions / issues

- **The rule is deliberately not wired.** `check_doc` is byte-identical to
  `d61da1d`, so `docs check --root docs` still exits **0** on a tree that the
  scanner says carries **139 broken destinations and 1 escape**. That gap is
  the honest state of Phase 5 and it closes inside Phase 6's own commit,
  which is why the repair and the wiring are one change.
- **A census re-run against the Phase-5 scanner reproduces every published
  number exactly**: `docs/` → **393 recognised spans, 139 broken, 1 escape,
  30 damaged documents**; the three deliberately damaged `bodylink-*` trees →
  1, 1 and 2 findings of exactly the intended rules; **all 33 pre-M27 trees,
  the three clean `bodylink-*` trees and the bundled skill → 0 broken /
  0 escapes**. The real implementation agrees with the read-only prototype
  the contract was validated against, which is the point of measuring twice.
- **The `cli.md` edits add no scannable span.** The span count over `docs/`
  is **393** both before and after them (authoring trap 3 — every
  link-shaped example is inside an inline code span, and nothing became a
  line-anchored reference definition).
- **No test edit was needed.** `git diff ddf0a45 -- tests/` is empty.

### Verification

- `.venv/bin/python -m pytest tests/test_body_links.py -q` — **119 passed**
  (the whole pure-scanner module, first run).
- `.venv/bin/python -m pytest tests/test_check.py tests/test_cli_check.py
  tests/test_cli_touch.py tests/test_skill.py -q` — **18 failed, 203
  passed**; the exception census over `--tb=line` is **18 `AssertionError`,
  zero `AttributeError`**, which is the Phase-5 exit criterion: every
  remaining RED is now a missing *rule*, not a missing *symbol*.
- `.venv/bin/python -m pytest -q` — **18 failed, 1061 passed** (was 137 /
  942); 119 cleared, exactly the predicted split.
- `.venv/bin/ruff check .` — All checks passed. `ruff format --check .` —
  47 files already formatted. `.venv/bin/mypy src/ tests/` — no issues in 48
  source files.
- `.venv/bin/docs touch docs/cli.md --check` — touched, **no violations**
  (exit 0). `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` —
  identical (every `Updated:` in the tree was already 2026-08-14).
- `cmp docs/{cli,convention}.md src/docs_cli/skill/references/` — identical.
  `](../` still **0** across both specs and all six bundled skill files;
  `../src/docs_cli/` still absent from the bundled references.
- `git diff --stat ddf0a45` touches `src/docs_cli/cli.py`, `docs/cli.md`,
  `src/docs_cli/skill/references/cli.md` and the two milestone documents —
  and nothing else.

## Phase 6 — Implement Offline/Core Path (+ the D6 live-tree repair) — 2026-08-14

### Objective

Wire both rules into `check_doc` — containment before existence, source
order, per-occurrence granularity, the frozen messages — and, **in the same
commit**, perform the D6 live-tree repair, because
`test_check_dogfood_repo_docs_is_clean` and
`tests/test_cli_index.py::test_index_output_matches_frozen_snapshot` both flip
RED the instant the rule is wired. Splitting the two would leave the
repository's own dogfood gate knowingly RED across a commit boundary.

### Actions taken

**1. The wiring — three lines of code.** `findings.extend(body_link_findings(
path, text, root))` in `check_doc`, between the `Related:` loop and the
`stale` block, plus the docstring's rule list. Nothing else changed:
`check_tree`, `exit_code_for`, `finding_to_json`, `_print_check_findings`,
`_run_touch_check`, `_iter_doc_texts` and the argparse are untouched, exactly
as the contract's reuse list says. The `malformed` early return already sits
above the insertion point, so a document with no H1 gets no body-link pile-on
for free.

`check_tree` appends `missing-inverse` after `check_doc`'s list, so the
per-document order is now
`… → broken-ref → body-links → stale → unknown-field → missing-inverse`.
That satisfies "immediately after the `broken-ref` group and before the
`stale` block", and no test constrains the `missing-inverse` tail.

**2. The repair — 140 occurrences across 30 documents.** Performed by a
throwaway script kept **outside the repository** (D6: "no CLI verb performs
it") that imports the Phase-5 scanner, so the repair is driven by the same
grammar the rule uses. It collects every offending `(path, start, end, raw)`
through the `body_link_findings` decision procedure, **asserts the collected
set is exactly 140 occurrences / 30 documents / 132-5-2-1 and aborts
otherwise**, then splices only `text[start:end]` per file **by offset,
right-to-left** — literally the M28 operation, which makes this the first
live proof that the span contract works. `set_metadata_field` bumps
`Updated:` on all 30; `append_revision_entry` adds the uniform bullet to the
**29 archived** documents only (`charter.md` is active — M25 — D4 makes
`Revision:` archived-only); everything is published through `atomic_write`.

| Class | N | Rule |
|---|---|---|
| **Root rebase** | 132 | the destination resolves from the root, so the new token is `"../" * depth + raw` — `depth` is the segment count of the document's directory, always **2** (`archive/YYYY-MM-DD/`) |
| **Move-map** | 5 | the target itself later moved, so a rebase would still dangle: `m9-pypi-publish.md` → `../2026-05-25/…` ×4 in `archive/2026-05-24/m6-pypi-distribution.md`, and `m2-mutating-verbs.md` → `../2026-05-21/…` ×1 in `archive/2026-05-28/m12-project-rename.md` |
| **Playbook URL** | 2 | `references/adoption-playbook.md` ×2 in `archive/2026-05-25/m8-adoption-workflow.md` → the canonical GitHub blob URL, `convention.md`'s existing spelling |
| **Escape URL** | 1 | `charter.md:52` → the sibling GitHub blob URL (Q5's `outside-root-body-link`, the only active-tree edit) |

The four classes are disjoint by construction and the script refuses to guess:
an occurrence that matches none of them raises rather than being rebased. Two
traps a naive "rebase everything" pass gets wrong were both handled correctly:
`archive/2026-05-28/m12-project-rename-impl.md:80` names
`archive/2026-05-27/m10-adoption-polish.md`, which **is** a pure root rebase
and must not be mistaken for a move; and the two playbook links sit inside a
4-space-indented blockquote — E6 in the wild — where the link *text* stays
untouched and only the parenthesised token moves.

The **uniform** `Revision:` bullet, on all 29 (S8 — per-document detail
belongs in this table, not in 29 near-identical bullets):

```
- 2026-08-14: M27 one-time body-link migration; body-link destinations repaired (destination tokens only)
```

**3. `convention.md`'s promised date is now real (S7).** "repaired once, on a
stated date" became "was repaired once, on **2026-08-14**" — the actual
commit date, the same date carried by all 30 `Updated:` bumps and all 29
`Revision:` bullets. `convention.md` is the document *granting* the third
archived-editing exception and it ships in the sdist; until now the date it
promised was stated nowhere an adopter reading that file could reach. Mirrored
byte-identically in the same commit.

**4. `docs index --root docs` + `tests/fixtures/expected/docs-INDEX.md`
re-synced**, in this commit (Phase-1 follow-through 7).

### Predicted INDEX churn — mechanical, not a defect

`render_index` sorts every group by `Updated` descending then path ascending.
Bumping 29 of the 46 archived documents to 2026-08-14 moves all 29 to the
**top** of `## Archived`, ordered by path, so the snapshot diff is **30
changed lines** (29 relocated archived entries plus `charter.md`'s
`Updated 2026-05-24.` → `Updated 2026-08-14.`) and is entirely mechanical. It
follows from the operator-confirmed Q1 sub-decision that the `Updated:` bump
is wanted alongside `Revision:`; it is not re-openable and it is not a bug.

### Proving no other byte moved — six independent checks, all run

| # | Check | Result |
|---|---|---|
| 1 | **Round-trip reconstruction.** For each of the 30: delete the inserted `Revision:` group, restore the pre-repair `Updated:` value, undo every destination splice at its recorded offset, compare with the pre-repair bytes. | **30/30 byte-identical** |
| 2 | **Character-level diff classification.** `difflib.SequenceMatcher` old↔new per changed line; every non-`equal` opcode must lie inside a recorded destination span, or the line is the `Updated:` line, or the change is the inserted `Revision:` group. | **166 changed lines, 140 span-covered, 0 unexplained** |
| 3 | **Line-count arithmetic.** `git diff --numstat -- docs/`: `+3` net for each of the 29 archived documents, `+0` for `charter.md`, and no other file under `docs/` touched besides `INDEX.md` and `convention.md`. | **pass** |
| 4 | **Metadata invariants.** `parse_metadata_block` before/after on all 30: H1, `Lifecycle`, `Role`, `Project`, `Archived-reason` and the whole `Related` tuple identical; `Updated` bumped on all 30; `Revision` newly present on exactly the 29 and carrying exactly the one uniform bullet; trailing-newline state preserved. | **pass**; **zero** of the 29 carried a `Revision:` label before, so each got the 3-line group-creation shape and `duplicate-field` cannot fire |
| 5 | **Re-census.** Scanner over the repaired `docs/`. | **0 broken, 0 escapes**, and the total recognised span count **stays 393** — the sharp invariant: a destination-token rewrite must not change how many spans the grammar sees, and the 3 URL conversions stay recognised inline links that merely reclassify `local` → `scheme` |
| 6 | **Gates.** `docs check --root docs` with both rules live; `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md`. | **exit 0**; **identical** |

Check 2 needed one honest allowance: `difflib` sometimes aligns the inserted
group's blank separator with an adjacent existing blank line and reports the
three inserted lines rotated. The rotation is accepted only when the inserted
multiset is exactly the three expected lines **and** the resulting text
contains exactly one `Revision:` label preceded by a blank line — checks 1 and
3 pin the same fact independently.

### Decisions / issues

- **The 7 degenerate GREEN locks are now genuine**, by name:
  `test_check_doc_malformed_doc_gets_no_body_link_findings`,
  `test_check_tree_bodylink_clean_is_clean`,
  `test_check_tree_bodylink_excluded_forms_is_silent`,
  `test_check_tree_bodylink_nested_resolves_up_and_down`,
  `test_check_bodylink_clean_tree_exits_0`,
  `test_check_bodylink_excluded_forms_tree_exits_0`,
  `test_check_verdict_is_identical_from_a_relocated_copy` — plus
  `test_check_tree_bodylink_archived_repaired_copy_is_clean`, which is now the
  proof that the documented recipe works and that its blast radius really is
  one destination token, and
  `test_check_tree_pre_m27_fixtures_gain_no_body_link_findings[…]` **×33**,
  which is now the genuine regression lock across every pre-M27 tree.
- **The TRANSITIONAL lock closed inside this commit**, as Phase 4 classified
  it: `test_check_dogfood_repo_docs_is_clean` was GREEN before the wiring,
  would have been RED between the wiring and the repair, and is GREEN again at
  the commit boundary. It was never knowingly RED across one.
- **From this commit the repository's own prose is under the rule.** Every
  later doc edit must keep the live-tree census at 0 broken / 0 escapes, and
  every link-shaped example must stay fenced, inline-coded, backslash-escaped
  or genuinely resolving.
- **No test edit was needed.** `git diff ddf0a45 -- tests/` still shows only
  the regenerated `tests/fixtures/expected/docs-INDEX.md`, which is a fixture,
  not a test.

### Verification

- `.venv/bin/python -m pytest tests/test_check.py tests/test_cli_check.py
  tests/test_cli_touch.py tests/test_cli_index.py -q` — **216 passed**, 0
  failed (the 16 Phase-6 REDs cleared).
- `.venv/bin/python -m pytest -q` — **2 failed, 1077 passed**; the only
  remaining REDs are `tests/test_skill.py`'s two Phase-7 surface locks.
- `.venv/bin/ruff check .`, `ruff format --check .`, `mypy src/ tests/` —
  clean.
- `.venv/bin/docs check --root docs` — **no violations (exit 0)** with both
  rules in force.
- `cmp docs/{cli,convention}.md src/docs_cli/skill/references/` — identical.
- `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.

## Phase 7 — Update Tool/Wrapper Layer — 2026-08-14

### Objective

Reconcile every parallel surface with the two new rules. Only 2 RED tests
remained (`tests/test_skill.py`), but the surface-parity gate is broader than
the RED set — the whole point of the gate is that a surface can drift without
a test noticing.

### Actions taken

1. **`docs check`'s argparse `description`** (`src/docs_cli/cli.py`). It ended
   `"…and broken Related: references."`; it now reads `"…broken Related:
   references, and local Markdown body links that name no existing path or
   that leave the docs root."` The word **violations** is retained, because
   `tests/test_cli_check.py::test_check_help` asserts
   `"violation" in stdout.lower()`. Phase-1 follow-through item 2, closed.
2. **`src/docs_cli/skill/SKILL.md`** — the `Validate the tree` row now names
   both rule ids **and both repairs**, because the flags column of that table
   is read by an agent as a prescription: `broken-body-link` → rebase the
   destination (and the row says the destination resolves from the linking
   document's own directory, which is the fact that makes the rebase
   obvious); `outside-root-body-link` → replace it with a URL. Body still
   ~148 lines, far under the 500-line cap; no new `` `docs <verb>` `` span
   naming a non-verb; no new relative link; no `](../`.
3. **`src/docs_cli/skill/references/use-cases.md`** — the *Validate in CI* row
   now says body links are checked, and a new
   `## Upgrade: repair body links (M27)` section sits after the M25 upgrade
   section with the adopter's whole loop: find the damage, rebase a
   `broken-body-link`, use a **URL** for an `outside-root-body-link`, opt a
   code sample out by fencing / inline-coding / backslash-escaping it,
   re-check. The document-relative resolution base is stated up front,
   because it is the one thing an adopter has to internalise before the
   rebase makes sense.
4. **`CHANGELOG.md`**, under the existing `UNRELEASED` heading: one `### Added`
   entry per rule, each with a `console` block showing a real finding, the
   closed-key-set statement, and the surrounding grammar/masking scope; one
   BREAKING `### Changed` entry naming the no-repair-verb and no-opt-out-knob
   decisions; and an `### Upgrading from 1.x` recipe covering both repairs
   plus the three ways to opt a code sample out. **No version bump** —
   `pyproject.toml` stays `1.8.0` (M25 — D6), pinned by
   `test_a3_project_version_is_1_8_0` and `test_c2_docs_version_is_1_8_0`.
5. **No spec edit was needed in this phase.** `cli.md` already carries the
   rule list, the closed-record note, the exit-code prose and the explicitly
   stated out-of-root boundary (Phase 1, extended in Phase 5 by S1–S6/S9), and
   `convention.md`'s dated exception landed with the repair in Phase 6. Both
   mirrors were therefore already byte-identical and needed no re-copy, and
   the INDEX snapshot needed no regeneration.

### Decisions / issues

- **The third authoring trap is now live and was exercised.** Every
  link-shaped example added in this phase lives inside a fenced block or an
  inline code span, and nothing became a line-anchored reference definition.
  The census over the repaired `docs/` after this phase's edits still reads
  **393 spans, 0 broken, 0 escapes** — unchanged, so no new scannable span was
  authored.
- **The suite went fully GREEN one phase early.** That is expected: Phase 8 is
  a log-and-prove phase, and its exit criterion is the mechanical
  no-regression proof rather than the flip itself.

### Verification

- `.venv/bin/python -m pytest -q` — **1079 passed, 0 failed**.
- `.venv/bin/ruff check .`, `ruff format --check .`, `mypy src/ tests/` —
  clean.
- `.venv/bin/docs check --root docs` — no violations (exit 0).
- `docs check --help` and `cli.md` agree; the help text names both rules'
  conditions and keeps the word "violations".
- `cmp docs/{cli,convention}.md src/docs_cli/skill/references/` — identical;
  `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.
- `](../` still **0** across both specs and all six bundled skill `.md` files;
  `../src/docs_cli/` and `../../../../docs/` still absent from every bundled
  reference.

## Phase 8 — Run Tests (GREEN) — 2026-08-14

### Objective

Run the full suite and every quality gate, and prove **mechanically** — not
by assertion — that no pre-existing test id was removed, and that Step 2
added none either.

### GREEN

```
.venv/bin/python -m pytest tests/ -q --co   →  1079 collected, 0 collection errors
.venv/bin/python -m pytest -q               →  1079 passed, 0 failed
```

Zero xfail, zero xpass, **zero tracebacks**
(`grep -c "Traceback (most recent call last)"` → **0**; the M26 caveat holds —
several tests assert `"Traceback" not in proc.stderr`, which a failure listing
echoes, so the bare word is not a usable probe and the exact phrase is what
was counted).

The RED baseline's 137 failures cleared in exactly the predicted split:

| Phase | Cleared | Remaining RED |
|---|---|---|
| 5 | 119 (`tests/test_body_links.py`, all `AttributeError`) | 18 |
| 6 | 16 (10 `test_check.py` + 5 `test_cli_check.py` + 1 `test_cli_touch.py`) | 2 |
| 7 | 2 (`tests/test_skill.py`) | **0** |

### Mechanical no-regression proof

Test-id lists collected from throwaway `git worktree`s at **both** anchors —
the pre-M27 commit `d61da1d` and the Step-1 head `ddf0a45` — and from HEAD:

```
base.ids   (d61da1d)   895
step1.ids  (ddf0a45)  1079
head.ids   (HEAD)     1079

comm -23 base.ids  head.ids  →  0   ids removed since pre-M27
comm -23 step1.ids head.ids  →  0   ids removed since Step 1
comm -13 step1.ids head.ids  →  0   ids ADDED by Step 2
comm -13 base.ids  head.ids  →  184 ids added by M27 as a whole
895 + 184 = 1079 ✓
```

**Step 2 changed no test.** `git diff ddf0a45 -- tests/*.py` is **empty**;
the only change under `tests/` is `tests/fixtures/expected/docs-INDEX.md`,
which is a fixture regenerated inside Phase 6's own commit as Phase-1
follow-through 7 requires. No test was relaxed, weakened, deleted or
rewritten to reach GREEN, and none needed to be — which is the whole point of
having written them first.

### Gates

- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 47 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues in 48 source files.
- `.venv/bin/docs check --root docs` — no violations (exit 0), with **both**
  new rules in force over the repaired tree.
- `cmp docs/{cli,convention}.md src/docs_cli/skill/references/` — identical.
- `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.
- Live-tree census — **393 spans, 0 broken, 0 escapes**.

Milestone deliverables 2, 3, 4 and 5 are ticked here. Deliverable 4 (the test
coverage) was deliberately parked at this gate by the Step-1 conductor
decision, because a RED lock is not yet locking.

## Phase 9 — Integrate / Accept / Dogfood — 2026-08-14

### Objective

Replay the pre-repair damage on throwaway copies, walk the **documented**
upgrade recipe an adopter is handed rather than the Phase-6 script, prove
hermeticity end to end, sweep for false positives, and measure runtime. The
real tree is not touched at any point.

### 1. The pre-repair damage, replayed

`docs/` reconstructed from `ddf0a45` into a throwaway copy and checked with
the **new** `docs check` from HEAD:

```
exit 2 — 140 findings across 30 documents
Counter({'broken-body-link': 139, 'outside-root-body-link': 1})
```

Exactly the census E1/E5/E7 predicted, reproduced through the CLI rather than
through the scanner API.

### 2. The documented recipe, walked

Walked by a script that consumes **only `docs check --json`** — `path`,
`severity`, `rule`, `message` — and never imports the scanner. It follows
`cli.md` › *Upgrading from 1.x* literally: `broken-body-link` → rebase the
destination the way the spec describes it (prefix the `../` the move into
`archive/YYYY-MM-DD/` should have added); if the rebased destination still
does not resolve, the target itself moved, so look it up by basename inside
the tree; if it is not in the tree at all it is not the tree's to own, so it
becomes a URL. `outside-root-body-link` → a URL, per the message's own
trailing clause.

```
before: exit 2, 140 findings
applied: {'rebase': 132, 'moved': 5, 'url': 3}
after:  exit 0 — docs: no violations found
```

**The split it derives is the Phase-6 split**, and comparing the walked copy
against the repository's repaired `docs/` across all 30 documents — audit
lines (`Updated:`, the `Revision:` group) ignored — gives **0
destination-token mismatches**. The recipe an adopter is handed reaches
exactly the place the milestone did, and it reaches it from the finding text
alone.

### 3. Hermeticity, end to end, on the pre-repair copy

The pre-repair copy is the only one where the escaping link still exists, so
it is the only one that can prove anything. The identical bytes were checked
from two locations:

- `with-sibling/docs`, which has a real
  `src/docs_cli/skill/references/use-cases.md` beside it, so `charter.md:52`
  **would** resolve;
- `bare/docs`, with nothing beside it at all.

```
with-sibling: exit 2   |  bare: exit 2   |  cmp stdout -> IDENTICAL
```

Re-run in-process under a `Path.exists` / `Path.is_file` spy: **140 findings
and 756 stats in both, and 0 probes outside the root in either** — each probed
path lexically normalised before the containment comparison, because
`Path.is_relative_to` is a pure prefix test. The verdict is a function of the
tree and nothing else.

### 4. False-positive sweep

`docs check` over **all 39** committed fixture trees: every tree exits 0 with
zero body-link findings **except** M27's three deliberately damaged ones,
which yield exactly their intended sets —

```
bodylink-archived      exit 2  {'broken-body-link': 1}
bodylink-broken        exit 2  {'broken-body-link': 1}
bodylink-outside-root  exit 2  {'outside-root-body-link': 2}
```

The bundled skill sweeps clean too: **18 recognised spans, 0 broken, 0
escapes**.

### 5. Runtime

| Input | Size | Time |
|---|---|---|
| the live tree (70 docs, 393 spans) | 2.5 MB | **183 ms** |
| `cli.md` alone | 132 KB | **9.5 ms** |
| `"[" * 50_000 + "](x)"` | 49 KB | **4.0 ms** |
| `"[a](" * 40_000` | 156 KB | **49.4 ms** |
| `"[a](<" + "x" * 100_000` | 98 KB | **7.9 ms** |
| all three adversarial cases (the runtime lock's input) | 303 KB | **61 ms — 33× under the 2.0 s bound** |

Linear, with no sign of backtracking: the adversarial inputs cost about what
their size predicts, which is the property the lock exists to check.

**One quality item carried to Phase 10.** The live-tree figure is 183 ms, not
the single-digit milliseconds the Step-2 plan guessed — the plan's estimate
was anchored on `cli.md`'s 132 KB and the tree is 2.5 MB. A stage profile
puts 92 ms in `_mask_code` and 80 ms in `_escape_flags`, both of which walk
every character in Python. Nothing bounds this and no test is at risk, but
two obvious early-outs remove most of it, and they make the code read better
rather than worse, so they belong in the Phase-10 quality pass rather than
here.

### Verification

- Every artefact above lives outside the repository. `git status` is **clean**
  after the dogfood; the real tree was never written to.
- Both throwaway `git worktree`s (`d61da1d`, `ddf0a45`) removed;
  `git worktree list` shows only the checkout.

## Phase 10 — Quality, Docs, Refactor — 2026-08-14

### Objective

Simplify the scanner, close the two specs that still described a pre-M27
world, and write the completion summaries.

### The `/simplify` pass — every candidate recorded

**Applied — four changes, all net simplifications:**

| Change | Why it simplifies |
|---|---|
| `_scan_destination`'s own leading-whitespace loop → `_skip_spaces(...)`, and `_skip_spaces` moved above its first user | The three-line loop was a verbatim copy of a helper that already existed four lines away. One statement of "skip whitespace", not two |
| `_strip_angle_pair(raw)` extracted; `_split_destination` and `classify_destination` both route through it | The same `raw[1:-1] if … startswith("<") …` expression appeared in both, and it is a **contract rule** ("strip a surrounding `<…>` pair first"), not an incidental detail. Stated once, it cannot drift; the two long conditional expressions become two short calls |
| `scan_body_links`' `span` / `kind` / `resume` trio collapsed into one `parsed: tuple[str, int, int, int] \| None` | Removes a dead `resume = close + 1` initializer and a `kind = ""` sentinel that was a lie — the empty string is not a `BODY_LINK_KINDS` member. One "did a form match?" variable instead of three that had to be kept in step |
| `_mask_inline_spans` gains `if "\`" not in line: return line`; `_escape_flags` steps between backslashes with `str.find` instead of over every character | Both state the common case up front — most lines carry no backtick, most documents are not backslashes — and both were the whole of the Phase-9 runtime finding |

**Considered and rejected — with the reason, so a later pass need not
re-derive it:**

| Candidate | Why it stays |
|---|---|
| Fold `_mask_inline_spans` into `_mask_code` | `_mask_code` is contractually **two passes in a fixed order**, and the named call is what makes "fences first, spans second" visible in one line. Inlining a per-line char loop into the fence walker would bury that |
| Collapse `_split_destination` into `scan_body_links` (it is single-use) | It is the **BINDING decode order** — the most subtle contract in the file, with three specified consequences in its docstring. Inlining it would put that in the middle of a loop body, where no one will find it |
| Replace `_escape_flags`' `bytearray` with an `is_escaped` closure | The array is O(n) once and O(1) per lookup; a closure would have to walk backwards from each query, which is quadratic on the exact adversarial input the runtime lock exists to catch. The array earns its keep |
| Merge `_close_inline` and `_close_reference_definition` behind a `closer: str \| None` parameter | Saves ~8 lines and costs more than it saves: the reader would have to carry "None means end-of-line" through both branches, where today each function states its own rule linearly |
| Hoist `_scan_title`'s three-entry `closers` dict to a module constant | It would separate the definition from its only use for no gain; titles are rare, so nothing is rebuilt hot |
| Pre-filter `_FENCE_RE` with a cheap `line[:4]` test | It would state what a fence looks like a **second** time, next to the regex that already states it — a real correctness risk if the regex ever changes — for a few milliseconds on a run that is already 0.16 s end to end |

**The Phase-9 quality item, closed and re-measured:**

| | before | after |
|---|---|---|
| `_escape_flags` over the live tree | 80.0 ms | **0.3 ms** |
| `_mask_code` over the live tree | 92.1 ms | **69.6 ms** |
| `scan_body_links` over the live tree (2.5 MB) | 182.7 ms | **80.7 ms** |
| the 303 KB adversarial set (2.0 s lock) | 61 ms | **43 ms — 47× headroom** |
| `docs check --root docs`, end to end | — | **0.16 s** |

Stopped there deliberately: at 0.16 s for the whole tree the remaining
`_mask_code` cost is not worth a second statement of the fence grammar.

### Documentation closed

- **`docs/architecture.md` › `check`** gains the M27 bullets after the M25
  reciprocity bullet: the pure pipeline (`_mask_code` → `scan_body_links` →
  `classify_destination` → `normalise_body_link_target` →
  `_body_link_is_contained` → one `.exists()`); the fact that these are
  **per-document** rules inside `check_doc` with **no** second `check_tree`
  pass — the deliberate contrast with `reciprocity_findings`, and the reason
  `docs touch --check` inherits them for free; the length-preserving mask as
  the reason offsets stay offsets into the original text, and therefore as
  the reason `BodyLink`'s span is usable by M28; the four bounds that keep
  the scan linear; and the reuse list. The stdlib-only pin is noted intact
  (`urllib.parse`, `posixpath`, `string`, `re`). `check_doc`'s rule
  enumeration in the same section gains both ids.
- **`docs/test-strategy.md` › *What we don't test*** said "Markdown
  rendering. The tool reads metadata; the body content is opaque." — false
  the moment M27 landed. It now scopes the exclusion honestly: rendering,
  headings and anchors, prose style and document structure stay untested, and
  the body is read for exactly **one** purpose, resolving the destinations of
  a bounded set of local links. (`convention.md`'s twin sentence was already
  corrected in Phase 1, because it is on the byte-parity gate.)
- **Use-case catalogs swept.** `src/docs_cli/skill/references/use-cases.md`
  was updated in Phase 7. `docs/agent-native-invocation.md` names `docs check`
  three times but never enumerates its report, so it needed no change. The
  only other surface listing what `docs check` validates is `README.md`'s
  one-line CLI table, which now ends "…status/location drift, body links."

### Verification

- `.venv/bin/python -m pytest -q` — **1079 passed, 0 failed**, before and
  after every simplification step.
- `.venv/bin/ruff check .`, `ruff format --check .`, `mypy src/ tests/` —
  clean.
- `.venv/bin/docs check --root docs` — no violations (exit 0).
- Live-tree census — **393 spans, 0 broken, 0 escapes** after this phase's
  doc edits.
- `cmp docs/{cli,convention}.md src/docs_cli/skill/references/` — identical;
  `diff docs/INDEX.md tests/fixtures/expected/docs-INDEX.md` — identical.

## Milestone completion summary

**M27 — Markdown body-link validation is implementation-complete
(2026-08-14).** All ten TDD phases are done across two steps
(`m27/phases-1-4`, `m27/phases-5-10`); every deliverable is met; the suite is
**1079 passed / 0 failed**; and `docs check --root docs` exits 0 over a tree
that carried 139 broken body links and one escaping link when the milestone
opened.

**What shipped.** A pure, stdlib-only, linear scanner over a deliberately
bounded, CommonMark-*shaped* grammar — inline links with plain and `<…>`
destinations and an optional title in all three quotings, plus reference
definitions — behind a **length-preserving** fenced- and inline-code mask.
Destinations resolve **relative to the referring document**, the opposite of
a `Related:` target. Two hard errors come out of it: `broken-body-link` for a
destination that names no existing path inside the root, and
`outside-root-body-link` for one that leaves it, decided by path arithmetic
alone. Containment is tested **before** existence, so the two never
double-report. Both are `severity: error`, exit 2, one finding per
occurrence, attached to the referring document, with the JSON record's key
set left **closed** at `{path, severity, rule, message}`.

**Three properties are the milestone's real output.**

1. **`text[start:end] == raw`, by construction.** `BodyLink` carries the exact
   character span of each destination token in the *original* text, which is
   what lets **M28** rewrite destinations by splicing and copying every other
   byte — and what stops this project ever growing a second Markdown parser.
   Phase 6 used that operation on 140 live occurrences, so the contract is
   proven rather than promised.
2. **The check is a function of the tree alone.** `docs check` never stats,
   opens, or follows anything outside its own root. Proven end to end: the
   same bytes checked from a location where the escaping link *would* resolve
   and from a bare one produce byte-identical output, with zero probes
   outside the root under a `Path.exists` / `Path.is_file` spy.
3. **The upgrade path is real, not asserted.** The pre-repair damage was
   replayed on a throwaway copy and repaired by walking the documented recipe
   from `docs check --json` alone — never the scanner API — reaching exit 0
   with **0 destination-token mismatches** against the tree the milestone
   itself repaired.

**The live-tree repair (D6)** was 140 occurrences across 30 documents — 132
root rebases, 5 moved targets, 2 playbook URLs, 1 escape URL — landed in the
same commit as the wiring so the dogfood gate was never knowingly RED across
a commit boundary, audited with an `Updated:` bump on all 30 and one uniform
dated `Revision:` bullet on the 29 archived ones, and proven by six
independent checks including 30/30 byte-identical round-trip reconstructions.
`convention.md` carries the third — and last — archived-document exception,
with its blast radius and its real date.

**Numbers.** 184 new test ids, **zero** pre-existing ids removed or modified
across the whole milestone; 1079 collected, 1079 passed; 393 recognised spans
over `docs/` before and after the repair; 81 ms to scan the 2.5 MB tree and
43 ms for the 303 KB adversarial set, 47× under the runtime lock. No version
bump: `pyproject.toml` stays `1.8.0`; **M29** performs the single bump to
`2.0.0` (M25 — D6).

**Handed to M28**, as simplifications rather than questions: the `BodyLink`
span contract; the guarantee that a clean tree contains **no** escaping
destination, so M28 never has to rewrite one; and one scanner, shared.

The milestone stays `Lifecycle: active` until the M29 publish closeout.
