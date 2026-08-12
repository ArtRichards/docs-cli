# M26 — Safe explicit archive selection

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-08-13

Related:
- child-of: plan.md
- parent-of: m26-safe-archive-selection-impl.md
- implements: charter.md
- pairs-with: m26-safe-archive-selection-impl.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: test-strategy.md
- pairs-with: status.md
- references: feedback-log.md
- follows: m25-reciprocal-relationship-integrity.md
- precedes: m27-markdown-body-link-validation.md
- required-by: m28-move-safe-body-link-rewrites.md
- required-by: m29-pypi-publish-2-0-0.md

## Overview

- Milestone: M26 (v2.0 train)
- Title: Safe explicit archive selection
- Surface: decouple relationship context from archive authorization. A named
  archive with no cascade option moves only the named document; preview remains
  available; every multi-document write requires an explicit
  `--cascade-only GLOB` scope, planned in full before the first byte moves; and
  the whole operation plan is available as one machine-readable record.
- Progress: **Active / Phase 1 — Define Contract complete (2026-08-12).**
  M25 is implementation-complete and merged to `main`, so this is the next
  implementation milestone. **All seven setup questions are RESOLVED** — Q1,
  Q5, and Q6 by the operator; Q2, Q3, Q4, and Q7 conductor-resolved — and are
  recorded in *Resolved setup questions (Q1–Q7, BINDING)* below. Phase 1 did
  not re-open them: it froze the exact refusal messages, the preview and apply
  lines, the exit-code split, and the `--json` schema against them, plus the
  seventeen Step-1 planning questions, in *Decisions (Phase 1 — BINDING)*.

### Goal

Make it impossible for an agent to archive a useful neighborhood merely
because the documents are related. Previewing candidates should be effortless,
but a write must state the exact bounded selection the operator intends — and
the tool must either perform that selection completely or refuse it completely,
loudly, before anything moves.

### Primary use-case acceptance

- **Preview before deciding.** An agent preparing to archive a completed
  milestone previews the one-hop candidates and sees the upcoming, paused, and
  long-lived context documents named without any of them moving — in prose on
  stderr, or as one JSON operation-plan record.
- **Write exactly the intended set.** The agent then archives only the named
  milestone artifacts through an explicit path scope, and the command reports
  the same set it previewed, in the same record shape.
- **Fail loudly, not quietly.** A typo, an obsolete unscoped command, a
  duplicate edge, a destination collision, or an already-archived neighbour
  fails before any document moves — never as a partial write that exits 0.

## Binding scope

The eight decisions below are binding for M26. Each carries the setup question
it resolves; the reasoning for those resolutions is in *Resolved setup
questions (Q1–Q7, BINDING)*.

### D1 — Authorization is explicit, never relational

Exactly three archive shapes exist, and no other invocation writes a related
document:

| Invocation | Writes | Exit |
|---|---|---|
| `docs archive FILE` | `FILE` only | 0 |
| `docs archive FILE --cascade-dry-run [--cascade-only GLOB]` | nothing (preview) | 0 |
| `docs archive FILE --cascade-only GLOB` | `FILE` plus exactly the one-hop candidates matching `GLOB` | 0 |

Relationship verbs supply the candidate set for preview and for glob matching.
They never grant authorization. This is the milestone's whole point and the
operator's confirmed decision in `feedback-log.md` (2026-08-10).

`docs archive FILE` stays **quiet** about candidates it leaves in place
(Q7): that is the correct safe behavior, and a notice on every single-document
archive would be noise. `--cascade-dry-run` is where candidates are named **in
prose**; the `--json` record carries the whole candidate set in every mode,
because its consumer is the agent deciding whether a selection is correct
(Phase-1 Q14).

The table describes **authorization**, not an exemption from validity checks:
an already-archived primary is refused in all three shapes (Phase-1 Q1). And
`--reason` writes `Archived-reason:` on the **primary only** (Phase-1 Q10) —
the reason explains why *this* archive was requested, not why each neighbour
moved.

### D2 — Bare `--cascade` and `--interactive` refuse before any write

`--interactive` is **retired** (Q1) and bare `--cascade` refuses (the
operator's `feedback-log.md` decision). Both flags stay **registered** in
argparse (Q2) and refuse **unconditionally** — independent of `--dry-run`,
`--cascade-dry-run`, `--json`, and every other flag, so the combination matrix
contains no "it depends" cell. The refusal happens before the primary document
is touched, exits **2** (the code `cli.md` already assigns to an invalid
cascade-flag combination), and names the migration path: `--cascade-dry-run`
to preview, then `--cascade-only GLOB` to write.

The flags are kept registered, rather than deleted, precisely so an obsolete
script or workflow skill gets a legible, actionable refusal instead of
argparse's generic `unrecognized arguments` error. `--help` marks them as
removed and names the replacement. A later major version may delete them.

Two mechanics make "unconditional" real (Phase-1 Q11 / Q12). The retirement
check runs **first** — immediately after argument parsing, before any
filesystem access — so it wins over `file not found`, a bad `--date`, and a
malformed primary. And `--cascade` / `--interactive` leave the argparse
mutually-exclusive group, so no combination is intercepted by argparse's
"not allowed with" error: one message covers every cell. When both retired
flags are passed, `--cascade` is the one reported (declaration order).

Retiring `--interactive` removes the only stdin-reading path in `docs archive`,
so the M14 (B1) invariant strengthens: **`cli.md` may now state that
`docs archive` never prompts on stdin at all**, rather than "never prompts
unless `--interactive`". `docs install-skill` keeps its TTY-only,
never-blocking prompt (M23) and is unaffected.

### D3 — Candidate discovery: unchanged verbs, deduplicated, canonical, active-only

- The candidate set stays the existing one-hop `pairs-with` / `child-of`
  edges (Q3). **One hop only**; the M2 no-transitive-cascade decision is
  unchanged. Keeping the discovery set unchanged is defense in depth on top of
  the scope and preserves compatibility.
- The six M25 reciprocal verbs (`precedes`/`follows`, `depends-on`/
  `required-by`, `blocks`/`blocked-by`) are **never** candidates. Sequence,
  dependency, and blocking do not imply archive membership.
- A document reachable through more than one edge appears **once**. The set is
  deduplicated on the canonical root-relative POSIX path, first declaration
  wins, and the surviving order is `Related:` declaration order — deterministic
  and traceable back to the source document.
- `--cascade-only GLOB` matches against that same canonical root-relative
  path, so a `./name.md` or `sub/../name.md` spelling cannot dodge or defeat a
  scope. This mirrors M25's post-review canonical-path amendment.
- A **self-edge** — a candidate whose canonical path equals the primary's — is
  silently excluded: it is not a candidate and is not reported as ineligible
  (Phase-1 Q6).
- A candidate whose target does not resolve to a file is **excluded and named
  as ineligible** with a reason (`docs check`'s `broken-ref` still owns the
  finding), as is one whose canonical path escapes the docs root (Phase-1 Q7).
- The candidate scan deliberately does **not** consult `[exclude]` /
  `.docsignore` (Phase-1 Q8). Those govern the tree walks — the pre-flight
  validation walk and the reindex — not the primary's own declared edges.
- **A candidate already under the archive subtree is excluded** and named as
  ineligible with a reason (Q4). Archiving an archived document is meaningless,
  and today it silently relocates and re-dates history (evidence E4).

### D4 — Validate-all-first: one complete plan before the first write

The scoped write builds and validates a complete archive plan before mutating
anything (Q5). The plan covers the primary and every selected candidate, and
the pre-flight proves, for each:

- the document parses and has an editable metadata block;
- the document is **not** already under the archive subtree — a primary that
  is already archived is a **refusal** (Q4), not a re-dating;
- its archive destination is computed and is not already occupied;
- no two documents in the plan resolve to the same destination (the basename
  collision that today silently drops a document);
- the source file and destination directory are writable.

The existing whole-tree pre-flight walk (M12/M14 — A6) stays. Any **handled**
failure refuses the whole operation: exit non-zero, **zero bytes written**,
including the primary. Only after the plan validates does execution begin.

**The residual boundary is stated plainly, not papered over.** An unexpected
`OSError` *during* execution is reported as an exact **partial-state
admission** — naming which documents moved and which remain at their original
paths — and is **not** rolled back. Every failure the tool can foresee is
handled by the pre-flight; this is the honest description of what remains.

**Considered and declined:** extending M25 — D5's staged-publish-plus-rollback
contract from two documents to N. It would make an interrupted batch
recoverable by re-running, but each rollback must undo both a move and a
metadata edit, and the M12 referring-edge rewrite runs afterwards — a
materially larger lift than the safety this milestone is buying. Explicitly
declined for M26 and left available for a later milestone to pick up.

### D5 — An empty selection is a refusal, not a quiet primary-only archive

A `--cascade-only GLOB` **write** that selects nothing refuses (exit 2,
nothing written — the primary is not archived either) and says which case it
is: candidates existed but none was selected, or the document has no one-hop
candidates at all. An empty or comment-only pattern is its own third refusal
(Phase-1 Q9). Primary-only archive already has its own unambiguous spelling —
`docs archive FILE` — so a scope that selects nothing on a write is always a
mistake, and today it is indistinguishable from success (evidence E5).

**D5 governs the write path only.** A preview is never a write, so it never
fails — see D6. The two decisions do not overlap, and there is no invocation
for which both an exit-2 refusal and an exit-0 preview could be argued.

### D6 — Preview names the whole neighborhood, not just the selection

`--cascade-dry-run`, with or without `--cascade-only`, lists the primary's
destination and **every** one-hop candidate marked selected, not-selected, or
ineligible, writes nothing, and exits 0. Today a filtered preview prints only
the matching subset, so an operator cannot see what a scope is leaving
behind — which is exactly the judgement the preview exists to support.

**A preview always exits 0, including a scope that selects nothing**
(Phase-1 Q2). `docs archive F --cascade-dry-run --cascade-only 'typo-*'`
writes nothing, exits **0**, and keeps the typo loudly visible: a
`matched none of the <N> one-hop candidate(s)` line on stderr and
`"selected": []` in the `--json` record. The same holds for the equivalent
`--cascade-only GLOB --dry-run` spelling. D5's exit-2 refusal is reserved for
the invocation that would have written.

### D7 — One machine-readable operation-plan record (`docs archive --json`)

`docs archive` gains a local `--json` flag (Q6) emitting **one** operation-plan
record on stdout, reusing M25's `relate --json` pattern: the **same shape** for
a preview and for a real apply, so the two are diffable. The record carries at
least:

- the **primary** — source path, canonical root-relative path, destination;
- the full **candidate** set in deterministic order;
- which candidates are **selected**;
- which are **excluded**, each with a **reason** (did not match the scope,
  already archived, target does not resolve);
- each planned **destination**;
- whether anything was **written** (preview vs apply), and the reindex state.

The consumer this milestone exists for is an agent deciding whether a selection
is correct; parsing prose off stderr is precisely the fragility M25 removed.
`--json` is declared locally on the `archive` subparser (as `check` / `list` /
`migrate` / `relate` do), gets its own `cli.md` field table and exit-code row,
and is mirrored into the bundled skill in the same change.

Two boundaries, both following M25's `relate --json` precedent
(`cli.md` › *No `--json` record on a coordinated-write failure*):

- **No record on any refusal** (Phase-1 Q3). Stdout is empty; the exit code
  plus the stderr message is the contract. The one exception is an
  **INDEX-refresh** failure, a post-write failure with every document already
  moved correctly: the record **is** emitted there, with `"applied": true,
  "index_refreshed": false`, and the run exits 2.
- **The candidate set is always present** (Phase-1 Q14), including under a
  plain `docs archive FILE`, where every candidate is reported
  `"selected": false, "reason": "not-selected"`. D1's quiet rule governs
  stderr prose, not the record.

### D8 — Compatibility, upgrade guidance, and surface parity

- **Breaking, deliberately.** Bare `--cascade` and `--interactive` stop
  working. That is the point of the 2.0 major version, and the refusal is
  designed to be the loudest possible failure.
- **No version bump.** M25 — D6 binds the whole train: the package stays
  `1.8.0` through M25–M28 and **M29** performs the single bump to `2.0.0`.
  M26 touches neither `pyproject.toml` nor the packaging version pins; its
  CHANGELOG entries accumulate under the existing `UNRELEASED` heading.
- **Surface parity in the same change** (`plan.md` › *Ongoing conventions*;
  `CLAUDE.md` › *Skill update flow*): argparse `--help`, `docs/cli.md`,
  `docs/convention.md`, the bundled `src/docs_cli/skill/` (`SKILL.md`,
  `references/use-cases.md`, and `references/cli.md` /
  `references/convention.md` kept **byte-identical** to `docs/cli.md` /
  `docs/convention.md`), and `CHANGELOG.md` all describe the same safe flow,
  including the new `--json` surface.
- **Upgrade guidance names the replacement invocation**, because the most
  common real-world caller is a milestone-completion step:
  `docs archive <slug>.md --cascade` becomes
  `docs archive <slug>.md --cascade-only '<slug>*'`, previewed first with
  `--cascade-dry-run`.
- **Host-machine and Agent Playbook Suite skills are out of scope.** Per
  `CLAUDE.md`, host skills under `~/.claude/skills/` refresh only at a
  production ship, and `plan.md` records the Agent Playbook Suite workflow
  update (its `create-milestones` skill prescribes the now-refused bare
  `--cascade`) as a post-M29 cross-repository follow-up.

## Out of scope

- Transitive or multi-hop cascade (the M2 decision stands).
- Multiple positional `FILE` arguments or an explicit file-list selector as an
  alternative to globs — a plausible future ergonomic, deliberately not this
  milestone's contract.
- Rolling back an interrupted execution batch (M25 — D5's
  staged-publish-plus-rollback extended to N documents) — considered and
  explicitly **declined** for M26; see D4 and Q5.
- Unarchive / undo, or any repair of an archive performed under the old
  behavior.
- Changing the recognized relationship vocabulary or its reciprocity rules
  (M25 owns that surface).
- Markdown body links in moved documents (M27 detects, M28 rewrites).
- Generalizing the archive planner or the `--json` plan record to `docs mv` or
  `docs project set`.
- The `2.0.0` version bump, CHANGELOG dating, and release notes (M29).
- Agent Playbook Suite changes; that repository consumes the released v2.0
  behavior after M29.

## Current state and risks

Reproduced against docs-cli 1.8.0 during setup; the full evidence table lives
in the implementation log's setup record. Each numbered item is the grounding
evidence for a specific piece of this milestone and maps to named regression
coverage in *Evidence → regression coverage* below.

- **E1 — The over-cascade is real on this very tree.** `docs archive
  m25-reciprocal-relationship-integrity.md --cascade-dry-run` reports it would
  archive **six** related documents: `plan.md`, the milestone's impl log,
  `cli.md`, `convention.md`, `test-strategy.md`, and `status.md`. Bare
  `--cascade` at a milestone closeout would move this project's entire
  specification spine into the archive, with no prompt.
- **E2 — `_cascade_set` does not deduplicate.** A document reachable through
  both `pairs-with` and `child-of` is archived once and then reported as a
  failure (`could not archive b.md: [Errno 2] No such file or directory`) — a
  false error on a successful run.
- **E3 — Per-candidate failures do not affect the exit code.** A basename
  collision between two candidates leaves one document unarchived, prints a
  bare-path message, and exits **0**; `docs check` afterwards reports no
  violations, so the partial write leaves no detectable drift.
- **E4 — Already-archived neighbours are silently re-dated.** A `pairs-with`
  edge into the archive subtree makes `--cascade` relocate
  `archive/2026-01-01/old.md` to `archive/2026-08-12/old.md` and rewrite its
  `Updated:` field. This is data corruption, not merely over-reach, and it is
  load-bearing on the live tree: `status.md` carries more than twenty archive
  subtree `pairs-with` edges.
- **E5 — A typo'd scope looks like success.** `--cascade-only 'typo-*'`
  archives the primary, prints `cascade: no one-hop relations to archive`, and
  exits 0.
- **`--interactive` is a second unscoped multi-document write path** and it
  ignores `--cascade-only` entirely, which is why D2 retires it rather than
  trying to reconcile it with D1.
- **Structural risk from the ecosystem.** The `create-milestones` workflow
  skill prescribes bare `--cascade` at every milestone completion, so the
  over-cascade is not an unlucky invocation — it is the documented flow. The
  refusal is the mitigation; the skill update is a post-M29 follow-up.
- **Mitigating existing strengths.** `_archive_one` is already
  edit-then-move with `atomic_write`; the M12/M14 whole-tree pre-flight walk
  already exists; M18 already keeps archive-subtree edges resolvable across a
  batch; and M25 has just established the validate-all-first,
  refuse-before-writing, one-JSON-plan-record shape that D4 and D7 extend from
  two documents to N.

### Evidence → regression coverage

| Evidence | Fixed by | Named coverage (Phases 2–3) |
|---|---|---|
| E1 over-cascade | D2 refusal | bare `--cascade` refuses with exit 2 and zero bytes written; the same tree previews all six candidates under `--cascade-dry-run` |
| E2 duplicate edge | D3 dedup | a doc reachable by `pairs-with` **and** `child-of` appears once in preview, JSON, and the write; no false failure line |
| E3 basename collision | D4 pre-flight | two candidates mapping to one destination refuse before any write; both docs still at their original paths; exit non-zero |
| E4 archived neighbour | D3 exclusion + D4 primary refusal | an archive-subtree candidate is excluded and named ineligible; an already-archived **primary** refuses; the archived doc stays at its path with its `Lifecycle:`, `Updated:`, `Archived-reason:`, H1 and prose unchanged — while M18's edge integrity still repoints the one `Related:` bullet of its that points at a document moving in the same operation, and `docs check` is clean afterwards |
| E5 typo'd scope | D5 empty-selection refusal | a non-matching `--cascade-only` refuses with exit 2, the primary is not archived, and the message distinguishes "none matched" from "no candidates" |

## Deliverables

- [x] Exact flag / exit-code / message compatibility matrix and the `--json`
      schema frozen in Phase 1, against the resolved Q1–Q7 decisions.
- [ ] Bare `--cascade` and `--interactive` refuse before any write, registered
      and refusing, with actionable migration guidance.
- [ ] Deterministic preview naming every candidate as selected, not-selected,
      or ineligible, writing nothing.
- [ ] Deduplicated, canonical-path, collision-checked, writability-checked
      archive plan built before the first mutation, with archived documents
      excluded and an archived primary refused.
- [ ] Empty-selection refusal with distinct "none matched" / "no candidates"
      messages.
- [ ] `docs archive --json` operation-plan record, one shape for preview and
      apply, carrying primary / candidates / selected / excluded-with-reason /
      destinations / written state.
- [ ] Regression coverage for E1–E5 plus proof that primary-only archive, the
      M12 referring-edge rewrite, and M18 archive-subtree edge integrity are
      unchanged.
- [ ] Surface parity across `--help`, `cli.md`, `convention.md`, the bundled
      skill (byte-identical mirrors), and the `UNRELEASED` CHANGELOG, plus
      v2.0 migration guidance.

## TDD implementation plan

### Phase 1 — Define Contract

- Objective: freeze — against the already-resolved Q1–Q7 — the exact refusal
  messages and exit codes, the candidate discovery / deduplication /
  canonicalization rules, the ineligibility reasons, the empty-selection
  messages, the preview shape, the pre-flight boundary and the partial-state
  admission wording, the `--json` record schema and field table, and the
  compatibility language. No business logic lands. Phase 1 does **not**
  re-open the setup decisions.
- Files: `docs/cli.md`, `docs/convention.md`, this milestone, and the bundled
  reference mirrors. Interface signatures are frozen in a *Decisions
  (Phase 1 — BINDING)* section here rather than stubbed in
  `src/docs_cli/cli.py`, following the M25 precedent — stubs would perturb the
  Phase-4 subprocess RED reasons.
- Exit: specs, help strings, the `--json` schema, and the frozen signatures are
  internally consistent; no behavior changes.

### Phase 2 — Write Tests (RED)

- Objective: express refusal, preview, scoped-write, and JSON behavior before
  any implementation, including every failure path the current code silently
  swallows.
- Files: `tests/test_cli_archive.py`, a new focused planning-unit module
  (`tests/test_archive_plan.py`), and `tests/test_cli_check.py` /
  skill-parity tests where the surface moves.
- Exit: the E1–E5 locks in *Evidence → regression coverage*, plus
  `--interactive` refusal, unfiltered and filtered preview, scoped write,
  unwritable target, injected mid-execution `OSError` producing the
  partial-state admission, and the `--json` record (preview and apply having
  the same shape) are RED **only** for missing M26 behavior. The primary-only,
  M12 referring-edge, and M18 archive-edge locks stay GREEN throughout and are
  classified as such.

### Phase 3 — Create Data/Fixtures

- Objective: provide small committed trees isolating one semantic each, per
  `test-strategy.md`'s fixture policy.
- Files: new `tests/fixtures/trees/archive-*` trees for the candidate
  neighborhood (E1), the duplicate edge (E2), the basename collision (E3), and
  the archived neighbour (E4). Mutation-shaped cases that write and then
  byte-compare use inline `tmp_path` builders instead (the M25 rule).
- Exit: fixtures are structure-only (never date-sensitive), parse
  deterministically, and each yields exactly its intended finding set.

### Phase 4 — Run Tests (RED Baseline)

- Objective: prove the new tests fail for the intended missing behavior and
  for nothing else.
- Files: implementation log only.
- Exit: full baseline captured with exact counts; zero collection errors, zero
  tracebacks, zero xfails; every pre-existing test still GREEN; every
  GREEN-at-baseline lock classified explicitly.

### Phase 5 — Update Base Interfaces

- Objective: add the archive planning models and pure helpers without
  completing behavior — an immutable per-document move record and a whole
  operation plan (primary plus candidates, each carrying source path, canonical
  rel path, destination, selected/excluded state and reason), a candidate-set
  builder with deduplication and canonical matching, the pre-flight validators,
  and an `archive_plan_to_json` serializer. Shaped after M25's `RelateEdit` /
  `RelatePlan` / `plan_relate` / `apply_relate_plan` / `relate_plan_to_json`
  split, which the codebase already proves out.
- Files: `src/docs_cli/cli.py` and unit tests.
- Exit: interfaces typecheck and are unit-tested; behavior tests remain
  honestly RED at the seam.

### Phase 6 — Implement Offline/Core Path

- Objective: implement candidate planning, deduplication, archived-document
  exclusion, collision and writability pre-flight, the refusal paths, the
  all-or-nothing scoped execution, and the partial-state admission.
- Files: `src/docs_cli/cli.py`, planning/archive unit and integration tests.
- Exit: core and integration tests GREEN; every handled failure refuses before
  the first write; no unrelated bytes change; M12 and M18 behavior byte-stable.

### Phase 7 — Update Tool/Wrapper Layer

- Objective: reconcile the argparse surface (flag registration, the retired
  flags' refusal help text, the local `--json` flag, mutual exclusion), human
  stderr output, the JSON record on stdout, exit codes, the single
  end-of-batch reindex, `cli.md`, `convention.md`, the bundled skill, and the
  `UNRELEASED` CHANGELOG with upgrade guidance.
- Files: CLI parser/dispatch, `docs/cli.md` (the `archive` section, the
  `--json` field table, and the exit-code summary rows), `docs/convention.md`,
  `src/docs_cli/skill/` (`SKILL.md`, `references/use-cases.md`, and the
  byte-identical `cli.md` / `convention.md` mirrors), `CHANGELOG.md`.
  **Not** `pyproject.toml` or the version pins (M25 — D6).
- Exit: subprocess tests, the reference byte-identity tests, and the
  surface-parity grep are GREEN; `docs archive --help` and `cli.md` agree.

### Phase 8 — Run Tests (GREEN)

- Objective: run the focused and full suites plus lint, format, types,
  reference byte identity, and docs integrity.
- Files: implementation log only unless a real defect is found.
- Exit: all gates GREEN with exact counts recorded, and every pre-existing
  test id mechanically proven still present and GREEN.

### Phase 9 — Integrate / Accept / Dogfood

- Objective: on a throwaway copy of this docs tree, run the real closeout
  workflow end to end — preview the M25 pair's candidates (E1), confirm the
  spec spine is named but not selected, archive the pair with an explicit
  scope, and re-check. Then exercise each refusal (bare cascade,
  `--interactive`, typo'd scope, archived neighbour) and confirm the tree is
  byte-identical afterwards. Diff the `--json` preview record against the
  apply record.
- Files: throwaway tree only; the committed docs record the evidence.
- Exit: every flow runs unattended with no stdin, `docs check` is clean
  afterwards, the refusal flows change zero bytes, the preview and apply JSON
  records agree, and the real tree is untouched.

### Phase 10 — Quality, Docs, Refactor

- Objective: simplify the implementation, close the surface and upgrade docs,
  update the shipped use-case catalog, and write the completion summaries.
- Files: code/docs as justified, this milestone and the implementation log.
- Exit: full gate GREEN; no placeholders; M26 implementation-complete and
  ready to hand off to M27, staying `Lifecycle: active` until the M29 publish
  closeout.

## Phase checklist

- [x] Phase 1 — Define Contract
- [x] Phase 2 — Write Tests (RED)
- [x] Phase 3 — Create Data/Fixtures
- [x] Phase 4 — Run Tests (RED Baseline)
- [x] Phase 5 — Update Base Interfaces
- [x] Phase 6 — Implement Offline/Core Path
- [x] Phase 7 — Update Tool/Wrapper Layer
- [ ] Phase 8 — Run Tests (GREEN)
- [ ] Phase 9 — Integrate / Accept / Dogfood
- [ ] Phase 10 — Quality, Docs, Refactor

## Decisions carried from discovery

- Relationships provide context, never archive permission.
- Bare `--cascade` must not write.
- Preview remains supported.
- Explicit `--cascade-only` scope is required for a related-document write.
- Archive selection and relationship semantics are decoupled surfaces; M25
  owns the graph, M26 owns authorization.
- The package version stays `1.8.0`; M29 performs the single bump (M25 — D6).

## Decisions (Phase 1 — BINDING)

Phase 1 freezes the surface Phase 2 asserts against. Everything below is
binding for M26; Phases 5–7 implement it verbatim. The setup decisions
(D1–D8) are not re-opened — this section makes them exact.

### The compatibility matrix (BINDING)

Every cell is stated. D2 demands no "it depends".

| Invocation | Writes | stdout | Exit |
|---|---|---|---|
| `archive F` | `F` only | `--json` record if asked | 0 |
| `archive F --dry-run` | nothing | record | 0 |
| `archive F --cascade-dry-run` | nothing; full neighborhood preview | record | 0 |
| `archive F --cascade-dry-run --cascade-only G` | nothing; full neighborhood, `G`-selected marked | record | 0 |
| `archive F --cascade-only G --dry-run` | identical to the row above | record | 0 |
| `archive F --cascade-dry-run --cascade-only G` (G selects 0) | nothing; preview names the miss | record, `"selected": []` | 0 |
| `archive F --cascade-only G` (G selects ≥1) | `F` + exactly the selected set | record | 0 |
| `archive F --cascade-only G` (G selects 0, candidates exist) | nothing | none | 2 |
| `archive F --cascade-only G` (no candidates at all) | nothing | none | 2 |
| `archive F --cascade-only ''` / comment-only pattern | nothing | none | 2 |
| `archive F --cascade [+ any other flag]` | nothing | none | 2 |
| `archive F --interactive [+ any other flag]` | nothing | none | 2 |
| `archive <already-archived-F> [any flags]` | nothing | none | 2 |
| plan contains an intra-plan destination collision | nothing | none | 2 |
| plan contains an unwritable source or destination dir | nothing | none | 2 |
| plan member does not parse / has no metadata block | nothing | none | 1 |
| destination slot already occupied | nothing | none | 1 |
| whole-tree pre-flight walk fails (M12 / M14 — A6) | nothing | none | 1 |
| `OSError` mid-execution | partial; admission on stderr | none | 2 |
| `OSError` mid referring-edge rewrite (M14 — A4) | already moved | none | 2 |
| INDEX refresh failure | already moved | record with `"index_refreshed": false` | 2 |

**Exit-code split (Phase-1 Q4, operator).** Exit **1** is reserved for the
conditions 1.x already assigned it — a plan member with no editable metadata
block, an occupied destination slot, and the unchanged whole-tree pre-flight
walk — because `cli.md`'s exit-code matrix and a passing test pin them and
they must not silently change meaning. Every **new** M26 refusal exits **2**:
retired flag, archived primary, empty / none-selected / non-compiling scope,
intra-plan destination collision, unwritable source or destination directory.

### Frozen message catalog (BINDING)

Every new message is prefixed `docs: archive: ` (M25's `docs: relate: `
convention) and names every path in **canonical root-relative POSIX** form.
No test asserts any 1.x cascade string (verified by grep for `no one-hop`,
`cascade archived`, `cascade would archive`, `could not archive`,
`would archive`), so the legacy footer and the two legacy human lines are
replaced outright rather than carried (Phase-1 Q15 / Q16).

**Refusals** — exit per the matrix; every one prints **even under `--quiet`**:

```
docs: archive: --cascade is retired in docs 2.0 and writes nothing; preview with `docs archive <file> --cascade-dry-run`, then write an explicit scope with `docs archive <file> --cascade-only '<glob>'`
docs: archive: --interactive is retired in docs 2.0 and writes nothing; preview with `docs archive <file> --cascade-dry-run`, then write an explicit scope with `docs archive <file> --cascade-only '<glob>'`
docs: archive: <rel> is already under the archive subtree; refusing before any write
docs: archive: --cascade-only must not be empty
docs: archive: --cascade-only does not support negated ('!') patterns; state the exact bounded selection
docs: archive: --cascade-only '<glob>' matched none of the <N> one-hop candidate(s); refusing before any write
docs: archive: <rel> has no one-hop pairs-with / child-of candidates; refusing before any write (use `docs archive <file>` to archive it alone)
docs: archive: <relA> and <relB> would both archive to <dest-rel>; refusing before any write
docs: archive: <rel> has no editable metadata block; refusing before any write
docs: archive: archive destination already exists: <dest-rel> (for <rel>); refusing before any write
docs: archive: <rel> is not writable; refusing before any write
docs: archive: <dest-dir-rel> is not writable; refusing before any write
```

The two retirement lines render from **one** template keyed on the flag name,
so they cannot drift.

**Preview / apply lines** — stderr, gated on `not --quiet`:

```
docs: archive: would archive <primary-rel> -> <dest-rel>
docs: archive: archived <primary-rel> -> <dest-rel>
docs: archive: candidate <rel> — selected -> <dest-rel>
docs: archive: candidate <rel> — not selected (outside --cascade-only '<glob>')
docs: archive: candidate <rel> — not selected (no --cascade-only scope)
docs: archive: candidate <rel> — ineligible (already archived)
docs: archive: candidate <rel> — ineligible (target does not resolve to a file)
docs: archive: candidate <rel> — ineligible (target resolves outside the docs root)
docs: archive: --cascade-only '<glob>' matched none of the <N> one-hop candidate(s)
docs: archive: <N> candidate(s): <S> selected, <U> not selected, <I> ineligible
docs: archive: preview only — nothing was written
```

The `candidate` lines and the counts footer print **only** when a cascade flag
is present (`--cascade-dry-run` or `--cascade-only`); a plain
`docs archive FILE [--dry-run]` prints just its own line (D1's quiet rule).
The `candidate` lines are **identical** in preview and apply — a scoped write
is all-or-nothing, so the plan is what happened; the mode is carried by
`would archive` vs `archived` and by the presence of the `preview only` line.

**Partial-state admission** (D4 residual, exit 2):

```
docs: archive: write failed for <rel>: <err>; PARTIAL ARCHIVE — not rolled back. Archived: <relA> -> <newA>, <relB> -> <newB>. Still at their original paths: <relC>, <relD>. Repair manually.
```

When nothing had moved yet the archived list renders as the literal word
`none` (`Archived: none.`) — never as a blank, the M25 `_rollback_relate`
lesson.

**Ineligibility reason tokens** (machine-stable `--json` `reason` values):
`not-selected`, `already-archived`, `unresolved-target`, `outside-root`.
Ineligibility wins over `not-selected`: an already-archived candidate reports
`already-archived` whether or not a scope was given. Two ineligibility
conditions can hold at once (`../ghost.md` both escapes the root and does not
exist), so the reported reason is fixed by **precedence: `outside-root`, then
`already-archived`, then `unresolved-target`** (added in Phase 2 — the Phase-1
catalog named the four tokens but left the overlap undetermined, which
`test_ineligibility_reason_precedence_is_pinned` cannot tolerate).

**Check order** (also added in Phase 2, for the same reason — Q11 fixed only
the retirement check's position). Every check runs before any write, in this
fixed order: retired flags; empty / comment-only / negated `--cascade-only`;
root / `.docs.toml` / `--date` / primary parses; archived primary; plan built (a preview stops here
and exits 0); empty-selection refusal; **plan pre-flight**; whole-tree
validation walk; execution. The plan pre-flight precedes the whole-tree walk
deliberately: both can fire on the same malformed file, and naming the
document the operator asked for is strictly more actionable.

### `docs archive --json` schema (D7, BINDING)

One object on stdout, `json.dumps(..., indent=2)`, identical key set for
preview and apply (mirroring `relate_plan_to_json`):

```json
{
  "primary": {
    "source": "docs/m25.md",
    "path": "m25.md",
    "destination": "archive/2026-08-12/m25.md"
  },
  "date": "2026-08-12",
  "scope": "m25-*",
  "reason": "milestone closed out",
  "candidates": [
    {"path": "m25-impl.md", "verb": "pairs-with", "selected": true,
     "destination": "archive/2026-08-12/m25-impl.md", "exclusion_reason": null},
    {"path": "cli.md", "verb": "pairs-with", "selected": false,
     "destination": null, "exclusion_reason": "not-selected"},
    {"path": "archive/2026-01-01/old.md", "verb": "pairs-with",
     "selected": false, "destination": null, "exclusion_reason": "already-archived"}
  ],
  "dry_run": true,
  "applied": false,
  "index_refreshed": false
}
```

The top-level key set is **closed** and ordered as shown; `candidates` is in
`Related:` declaration order after dedup; `destination` is non-null **iff**
`selected`; `exclusion_reason` is null **iff** `selected`; `primary.source` is
the `FILE` argument **exactly as typed** (a relative argument stays relative)
and every other path is canonical root-relative POSIX. The field table lands
in `cli.md` in the `relate --json` style.

**Post-review amendments (2026-08-13, conductor-binding).** The top-level
`reason` field carrying `--reason` was **added**, mirroring `relate --json`;
to remove the name collision the candidate-level `reason` was **renamed**
`exclusion_reason`, matching the `ARCHIVE_EXCLUSION_REASONS` constant. The
`ArchiveMove` field is renamed in step with the JSON key. Doing this before
2.0 ships is cheap; afterwards it would be a breaking change.

### Frozen Phase-5 signatures (contract only — no code lands in Phase 1)

```python
ARCHIVE_EXCLUSION_REASONS: frozenset[str]  # not-selected, already-archived,
                                           # unresolved-target, outside-root

@dataclass(frozen=True)
class ArchiveMove:
    path: Path                 # absolute source
    rel: str                   # canonical root-relative POSIX
    aliases: tuple[str, ...]   # every declared Related: spelling resolving here
    verb: str | None           # discovering verb; None for the primary
    dest: Path | None          # absolute destination; None when not selected
    dest_rel: str | None
    selected: bool
    exclusion_reason: str | None   # None iff selected

@dataclass(frozen=True)
class ArchivePlan:
    root: Path
    config: Config
    primary: ArchiveMove
    candidates: tuple[ArchiveMove, ...]
    scope: str | None
    date_str: str
    reason: str | None         # --reason; applies to the primary only
    source: str                # the FILE argument EXACTLY as typed
    @property
    def moves(self) -> tuple[ArchiveMove, ...]   # primary + selected candidates

def archive_candidates(doc: Doc, root: Path, config: Config,
                       scope: str | None) -> tuple[ArchiveMove, ...]
def plan_archive(root: Path, config: Config, *, primary: Path, source: str,
                 doc: Doc, scope: str | None, date_str: str,
                 reason: str | None) -> ArchivePlan
def preflight_archive_plan(plan: ArchivePlan) -> None
def apply_archive_plan(plan: ArchivePlan) -> list[tuple[str, str]]
def archive_plan_to_json(plan: ArchivePlan, *, dry_run: bool, applied: bool,
                         index_refreshed: bool) -> dict[str, object]
def _print_archive_lines(plan: ArchivePlan, *, dry_run: bool, cascade: bool) -> None
def _cmd_archive(args: argparse.Namespace) -> int   # signature unchanged
```

`preflight_archive_plan` raises `CoordinatedWriteError(rolled_back=True,
published=())` for every refusal — the tree is trivially unchanged, which is
what that flag already means — and carries the Q4 exit-code split on the
exception (see *Step-2 amendments* below). `apply_archive_plan` returns the
`(old_rel, new_rel)` pairs `_rewrite_referring_edges` consumes, **one pair per
alias** plus the canonical one (Phase-1 Q5), and raises
`CoordinatedWriteError(rolled_back=False, published=(...))` carrying the
residual admission.

**Reuse — no new machinery is invented.** Scope matching:
`_compile_docsignore_pattern`, matched against the canonical rel from
`_canonical_related_target`. Archived test: the
`rel == config.archive_dir or rel.startswith(config.archive_dir + "/")` idiom
already used in `check_doc` and `_cmd_relate` — **not** `_in_archive_subdir`,
which hardcodes `archive`/`archived`/`project-history` and ignores
`[archive] dir`. Rel forms: `_root_relative`. Per-doc execution: `_archive_one`
verbatim, with `apply_archive_plan` as its ordered driver. Failure carrier:
`CoordinatedWriteError` — widen its docstring in Phase 5, do not add a second
exception class. Batch edge rewrite: `_rewrite_referring_edges` unchanged.
`_cascade_set`, `_print_cascade_footer`, and `_cascade_archive` are superseded
and deleted in Phase 6/7, not Phase 1.

### Step-2 amendments to the frozen signatures (conductor-binding)

Two frozen signatures could not be implemented literally. Both were
conductor-resolved before Phase 5 began; both are recorded here so the
contract and the code agree, and both are logged in the implementation log's
phase records.

| # | Amendment | Why the frozen form could not stand |
|---|---|---|
| 1 | **`CoordinatedWriteError` gains a keyword-only `exit_code: int = 2`** (Phase 5). | The Q4 split needs exit **1** for two conditions and **2** for four others, and `preflight_archive_plan(plan) -> None` raising one exception class has nowhere else to carry it. Matching on message text is the only alternative and is fragile. This is the widening the *Reuse* note above already sanctions ("widen its docstring; do not add a second exception class"); the default leaves every `docs relate` construction site byte-identical. |
| 2 | **`_print_archive_lines` gains a keyword-only `cascade: bool`** (Phase 7). | The plan carries `scope` but no "was a cascade flag present" bit, so `--cascade-dry-run` with no scope (candidate lines REQUIRED) and a plain `--dry-run` (candidate lines FORBIDDEN) are indistinguishable from the plan alone — D1's quiet rule is unimplementable without it. The helper is private, no test references it, and the rendered strings, which are what the contract actually froze, are unchanged. |

### Resolved Phase-1 plan questions (Q1–Q17, BINDING)

A **different series** from the setup Q1–Q7 below: these are Step 1's
planning questions, resolved by the operator and the conductor before Phase 1
began.

| # | Question | Resolution |
|---|---|---|
| Q1 | Does the archived-primary refusal apply to all three D1 shapes? | **Yes, unconditionally**, exit 2. D1's table describes authorization, not an exemption from validity checks. |
| Q2 | `--cascade-dry-run --cascade-only <no-match>` | **Exit 0** (operator). A preview is never a write, so it never fails; the typo stays visible as the `matched none` line and `"selected": []`. D5's refusal governs the write path only — D5/D6 amended above so the contradiction is gone. |
| Q3 | A `--json` record on a refusal? | **No.** Empty stdout; exit code + stderr is the contract (M25's precedent). **Do** emit it on an INDEX-refresh failure (`applied: true, index_refreshed: false`). |
| Q4 | Pre-flight exit codes | **Split**, pinned in a table in `cli.md` (operator). Exit 1 for the two pre-existing conditions and the whole-tree walk; exit 2 for the five new M26 refusals. |
| Q5 | Declared-spelling aliases | **`ArchiveMove.aliases`** carries every declared `Related:` spelling resolving to the canonical rel; `apply_archive_plan` returns one `(alias, new_rel)` pair per alias plus the canonical one, so `_rewrite_referring_edges`' exact-match matcher still rewrites a `./b.md` bullet. |
| Q6 | A self-edge | **Excluded** from candidates (canonical rel == the primary's); **not** reported as ineligible. |
| Q7 | A candidate escaping the root | A fourth ineligibility reason, **`outside-root`**. |
| Q8 | Does the candidate scan consult `[exclude]` / `.docsignore`? | **No** — unchanged, and stated explicitly in `cli.md`. |
| Q9 | `--cascade-only ''` or a comment-only pattern | Its own refusal, `docs: archive: --cascade-only must not be empty`, exit 2 (M25's `--reason must not be empty` precedent). |
| Q10 | `--reason` under a cascade | **Unchanged** — `Archived-reason:` on the primary only. Pinned in `cli.md` and a test. Post-review: it is also carried in the `--json` record as the top-level `reason` field. |
| Q11 | Ordering of the retirement check | **First**, immediately after argparse and before any filesystem access, so it wins over `file not found`, a bad `--date`, and a malformed primary. |
| Q12 | argparse mutual exclusion | **Remove `--cascade` and `--interactive` from the mutually-exclusive group** so the unconditional guard produces the single message for every combination. Both stay **registered** (setup Q2) so neither ever yields `unrecognized arguments`. |
| Q13 | Where E1 is pinned | On the committed `archive-neighborhood/` fixture, **not** the live `docs/` tree; the live-tree run is Phase-9 dogfood evidence only. |
| Q14 | `--json` with no scope | **Always carries the full candidate set**, each `selected: false, reason: "not-selected"`. Setup Q7's quiet rule governs stderr only. |
| Q15 | The two legacy human lines | **Moved to the new form** — `docs: archive: would archive <rel> -> <dest-rel>` and `docs: archive: archived <rel> -> <dest-rel>` (verb prefix, canonical root-relative paths). No test asserts either string today (grep-verified). |
| Q16 | The legacy cascade footer strings | **Replaced** by the D6 counts footer; the corresponding `cli.md` bullets are deleted. |
| Q17 | `plan.md`'s stale `--cascade` bullet | **Corrected in Phase 7** (it still claims `--cascade` prompts `y/N`, false since M14 and about to be doubly false); carried on the Phase-7 follow-through list recorded at Phase 4. |

### Post-review amendments (2026-08-13, conductor-binding)

The independent fresh-eyes review of Step 1 produced three contract decisions,
folded into the frozen material above and into `cli.md` / `convention.md`:

| # | Decision |
|---|---|
| A | **`--json` gains a top-level `reason`** carrying `--reason`, mirroring `relate --json`; the candidate-level `reason` is **renamed `exclusion_reason`** (and the `ArchiveMove` field with it) to remove the collision, matching `ARCHIVE_EXCLUSION_REASONS`. |
| B | `docs/agent-native-invocation.md`'s 2026-06-03 Layer-5 proposal keeps its text — rewriting it would falsify the record of what was proposed — and gains a short dated note so an agent reading it is not trapped. |
| C | **`--cascade-only` refuses a negated (`!`) pattern**: `docs: archive: --cascade-only does not support negated ('!') patterns; state the exact bounded selection`, exit 2. `_compile_docsignore_pattern` returns a `negate` flag that 1.x's `_cascade_set` discarded; a negated scope means "everything except X", the unbounded selection D1 exists to prevent. |

Two further corrections the review forced, recorded here because they change
what the specs assert rather than only what the tests check:

- **`primary.source` is the `FILE` argument EXACTLY as typed** (finding 6).
  Three places had said three different things, and no test distinguished
  them. `ArchivePlan` gains a `source: str` field carrying the raw argument;
  `plan_archive` takes it as a keyword. `str(plan.primary.path)` would always
  be absolute and could not honour either prose statement.
- **The M18 exception is stated in `convention.md`, not overclaimed away**
  (finding 2). The D1 paragraph had said an archived doc's "bytes are never
  rewritten by a later archive event", which contradicts `cli.md`'s M18 — D1
  leg 2 and made a Step-1 test unsatisfiable. Narrowed to name the one bullet
  M18 does repoint.

### Deviation from the Phase-1 file list (deliberate, logged)

The milestone's Phase-1 file list names "Interface signatures … frozen in a
*Decisions (Phase 1 — BINDING)* section here rather than stubbed in
`src/docs_cli/cli.py`". Phase 1 accordingly made **zero** `cli.py` edits:
stubs would change the Phase-4 subprocess RED reasons and risk baseline
behaviour, and the phase's own exit criterion is "no behavior changes". The
signatures above land as real code in Phase 5. This mirrors the M25 precedent.

## Resolved setup questions (Q1–Q7, BINDING)

Seven questions were raised at setup and **all seven are resolved before
Phase 1**. The originals are kept so the decision trail reads end-to-end. Three
were operator decisions; four were conductor-resolved as determined by the
specs, `plan.md`, `CLAUDE.md`, or the M14/M18/M25 precedent.

1. **`--interactive` disposition** — retire it, or require it to compose with
   an explicit scope? **RESOLVED → D2 (operator).** **Retire it.** It refuses
   with migration guidance pointing at `--cascade-dry-run` (preview) then
   `--cascade-only GLOB` (scoped write), exit 2. It was a second unscoped
   multi-document write path, it ignored `--cascade-only` entirely, and it was
   the only stdin-reading path in `docs archive`. Retiring it lets `cli.md`
   state the stronger invariant that **`docs archive` never prompts on
   stdin**.
2. **Retention shape of the refusing flags** — keep them registered, or delete
   them? **RESOLVED → D2 (conductor).** **Keep `--cascade` and `--interactive`
   registered and refusing** for the 2.x line, exit 2, with migration
   guidance. The value of this breaking change is a legible failure for the
   scripts and workflow skills still passing the old flag — not an
   `unrecognized arguments` traceback. A later major may delete them.
3. **Candidate verb set** — retain, or widen now that the scope grants
   authorization? **RESOLVED → D3 (conductor).** **Retain the one-hop
   `pairs-with` / `child-of` discovery set.** The scope, not the relationship,
   grants authorization; keeping the candidate set unchanged is defense in
   depth and preserves compatibility. M25's six reciprocal
   sequence/dependency/blocker verbs never become cascade candidates.
4. **Already-archived documents** — how are archived candidates and an
   archived primary handled? **RESOLVED → D3 + D4 (conductor).** **Exclude
   archived documents from the candidate set**, naming them as ineligible with
   a reason in the preview and in the `--json` excluded list; and **refuse
   when the primary itself is already archived.** Evidence E4 — bare
   `--cascade` relocating and re-dating `archive/2026-01-01/old.md` →
   `archive/2026-08-12/old.md` and rewriting `Updated:` — is data corruption,
   squarely in M26's remit, and load-bearing on the live tree, where
   `status.md` carries 20+ archive-subtree edges. It gets explicit regression
   coverage. (This was not one of the registered stub's four questions; it was
   found in the code during setup.)
5. **Handled-failure atomicity boundary** — how far does "all-or-nothing"
   reach? **RESOLVED → D4 (operator).** **Pre-flight everything.** Validate
   parse, metadata block, destination occupancy, intra-plan collision, and
   writability across the whole plan before the first write, so every handled
   error refuses with zero mutation. A residual mid-execution `OSError` is
   reported as an exact partial-state admission — which documents moved, which
   remain at their original paths — and is **not** rolled back. Extending
   M25 — D5's staged-publish-plus-rollback to N documents is **explicitly
   declined** for M26 and recorded as a considered alternative a later
   milestone may pick up.
6. **Machine-readable output** — does `docs archive` gain `--json`?
   **RESOLVED → D7 (operator).** **Yes.** One operation-plan record, the same
   shape for preview and apply, reusing M25's `relate --json` pattern, and
   carrying primary, candidates, selected, excluded (each with a reason),
   destinations, and whether anything was written. In M26 scope, with its own
   tests and its own `cli.md` / bundled-skill surface-parity rows.
7. **Primary-only archive notice** — should `docs archive FILE` name the
   candidates it leaves in place? **RESOLVED → D1 (conductor).** **No.** It is
   the correct safe behavior, and the line would be noise on every
   single-document archive. `--cascade-dry-run` is where candidates are named.

### Also settled, without a question

- **Version staging.** The package stays `1.8.0`; **M29** performs the single
  bump to `2.0.0`. CHANGELOG entries accumulate under `UNRELEASED`
  (M25 — D6).
- **Refusal exit code and conditionality.** Every M26 refusal exits **2** and
  is **unconditional** — independent of `--dry-run`, `--cascade-dry-run`, and
  `--json`.
- **Scope matching.** `--cascade-only` matches the **canonical** root-relative
  POSIX path (M25's post-review amendment-B shape).
- **Skill channels.** The bundled skill in `src/docs_cli/skill/` updates in the
  **same change** as the CLI surface, with `references/cli.md` and
  `references/convention.md` byte-identical to `docs/cli.md` and
  `docs/convention.md`. Host-machine skills — including `create-milestones`,
  which prescribes the now-refused bare `--cascade` — refresh only at the M29
  production ship, and the Agent Playbook Suite update is a post-M29
  cross-repository follow-up (`CLAUDE.md`; `plan.md`).

## Testing and quality gate

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q
.venv/bin/docs check --root docs
```

Additional gates: `docs archive --json` schema assertions (preview and apply
records identical in shape), `docs archive --help` / `cli.md` surface parity,
bundled `references/cli.md` and `references/convention.md` byte identity,
archive byte-identity checks on every refusal path, and the live INDEX
snapshot.

## Success criteria

- No unscoped flag or flag combination can archive a related document; bare
  `--cascade` and `--interactive` refuse before any write, exit 2, and name
  the replacement invocation.
- Preview and scoped output name the same deterministic, deduplicated
  candidate set, and the preview distinguishes selected, not-selected, and
  ineligible.
- `docs archive --json` emits one operation-plan record whose shape is
  identical for a preview and a real apply, carrying every candidate with its
  selected/excluded state and the reason for exclusion.
- An invalid, empty, or accidental scope causes zero mutation — verified
  byte-for-byte, including `INDEX.md`.
- A valid explicit scope archives exactly the intended documents, keeps every
  relationship resolvable (M12 and M18 behavior unchanged), refreshes `INDEX`
  once, and leaves `docs check` clean.
- E1–E5 each have named regression coverage: the over-cascade refuses, a
  duplicate edge appears once with no false failure, a destination collision
  refuses before any write, an already-archived neighbour is excluded and an
  archived primary refuses with the archived bytes untouched, and a typo'd
  scope refuses instead of looking successful.
- An unexpected mid-execution failure produces an exact partial-state
  admission naming what moved and what did not — never a silent partial write
  that exits 0.
- Full quality, compatibility, and dogfood gates are GREEN, leaving M27 ready
  to prepare next.
