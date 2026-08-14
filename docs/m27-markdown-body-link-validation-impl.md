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
- Progress: **Milestone setup complete, with all seven setup questions
  RESOLVED (Q1/Q2/Q5 by the operator; Q3/Q4/Q6/Q7 conductor-resolved).
  Phase 1 — Define Contract is next and does not re-open them.** Q5 was
  resolved **against** the setup recommendation and then **amended** — the
  hermetic boundary is kept, and an escaping destination is reported by path
  arithmetic as a second rule, `outside-root-body-link`, rather than skipped.
- Source: the operator-confirmed body-link decisions in `feedback-log.md`
  (2026-08-09/10) and the M27 registration in `plan.md` (2026-08-10).
- Branch: `m27/milestone-setup` for setup; implementation branches are chosen
  when Phase 1 begins.

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Pending | — | Freeze the supported Markdown grammar subset, the masking rules, destination classification/normalisation/resolution, **the containment test and its precedence over existence**, both findings (`broken-body-link`, `outside-root-body-link`) with severity / message template / exit code / ordering, the `BodyLink` span contract M28 consumes, and the legacy-tree policy — against the resolved Q1–Q7. |
| 2. Write Tests (RED) | Pending | — | Scanner unit tests over every supported and every excluded form; both rules' integration + subprocess/JSON locks; the no-double-report precedence lock and the never-stat-outside-the-root lock; the E5/E6 false-positive and false-negative locks; the pathological-input runtime lock. |
| 3. Create Data/Fixtures | Pending | — | `bodylink-*` trees, one semantic each, including `-outside-root` (escape aimed at a path that cannot exist) and the `../sub/../back-inside.md` normalise-back case; exotic grammar as inline strings (the M25 rule). |
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

## Phase 1 — Define Contract

_Not started._

## Milestone completion summary

_Not complete._
