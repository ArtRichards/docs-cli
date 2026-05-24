# M7 — Migration plan accuracy

Status: draft
Role: milestone
Project: docs
Updated: 2026-05-24

Related:
- child-of: plan.md
- implements: charter.md
- pairs-with: convention.md
- pairs-with: m4-migration-helper.md
- pairs-with: m8-adoption-workflow.md

## Overview

- Milestone: M7 (v1.1)
- Title: Migration plan accuracy
- Surface: extensions to `docs migrate`'s inference (`infer_role`,
  `infer_project`, `infer_status`, `migrate_plan`), a breaking
  rename of the controlled-vocab field from `Status:` to
  `Lifecycle:`, vocab additions, and archive-subdir normalisation.
  No new top-level verbs. M8 owns the operator/agent ergonomics
  side (flags, skill references).
- Status: **DRAFT** — captured 2026-05-24 from a multi-tree trial
  (501 files across 25 real-world sibling trees).

### Goal

M4 shipped `docs migrate` against a synthetic happy-path fixture.
Trial runs against real foreign trees showed the plan that migrate
produces is too lossy and too low-confidence to drive end-to-end:

- Free-form `Status:` lines (the dominant real-world use of that
  key) are silently coerced and dropped.
- 73% of files fall back to `role: notes` because the inferred
  signals are too narrow.
- Already-archived subdirs are detected but not normalised to the
  convention's `archive/YYYY-MM-DD/` shape.
- Project-name inference inherits raw directory casing
  (TitleCase / SNAKE_UPPER / digit-glued names) instead of
  normalising to the convention's lowercase-kebab shape.

M7 makes the plan accurate. M8 makes the workflow around the plan
agent-driveable. The two ship sequentially: M7 first (the plan
substrate), M8 second (the verbs and skill references that build
on it).

The verb stays dry-run by default; M7 adds NO new flags. All M7
changes are in inference + convention + the existing `--apply`
mutation set.

### Why this is M7 (and not part of M4 or M8)

- It's not M4 because M4 already shipped — M7 is hardening, not
  initial implementation. The verb contract is unchanged.
- It's not M8 because M8 depends on M7's accurate plan being
  available before the workflow improvements (triage flags, agent
  skill references) become useful. An agent driving a noisy plan
  can't triage its way out.

## Trial-run evidence (2026-05-24)

Two trials informed M7. Outputs at `/tmp/m7-migrate-full.txt`,
`/tmp/m7-migrate.json`, and `/tmp/m7-trial2/*.json`.

| Trial | Files | High-conf | Notes fallback | Unique projects |
|---|---|---|---|---|
| 1 (single tree) | 235 | 1.7% | 87% | 1 (correct) |
| 2 (25 trees) | 501 | 25.3% | 73% | 25 (one per dir — correct) |

Trial 2 corrected one assumption: the suffix matcher already
handles snake_case TitleCase tokens (`_Plan.md`, `_Log.md`,
`_Status.md`, `_Charter.md`) case-insensitively. Trial 1's
near-zero high-confidence rate was inflated by a single 185-file
generated-data subdir that masked the matcher's actual behaviour.

What Trial 2 surfaced instead is the per-tree variance: confidence
ranges 0% (`ideas/`) to 100% (`ph-django-agent-consistency`) based
on the shape of doc names in each tree. Trees with consistent
suffix discipline score 60–100%; trees with prefix-only naming
score 0–25%.

## Findings (the M7 backlog)

### F0 — `Status:` is a real-world status line; the controlled vocab needs a different key

The strongest finding. Almost every real-world doc uses `Status:`
as a natural-language progress update:

- "Implemented; retained as design record"
- "P0 domain/legal-trigger split implemented and validated;
  2026-05-11 P1/P2/P4 follow-on"
- "Draft normative companion spec"
- "Planning only"

The convention currently uses `Status:` for a controlled lifecycle
vocab (`active`/`draft`/`superseded`/`archived` + `add_statuses`).
The collision is total; the convention's use is the rarer one in
the wild. Today migrate "wins" by overwriting the prose with
`active`, dropping the original.

**Decision (operator, 2026-05-24):** rename the controlled-vocab
field to `Lifecycle:`. **Breaking change — no backward-compat
window.** Operator explicitly opted for a clean break; the only
existing trees on the new key are this project's own docs-cli
tree (mechanical sweep at Phase 5), and an agent migrating a
foreign tree was already going to need a docs update.

**Migration strategy:**

- Parser accepts ONLY `Lifecycle:` for the controlled-vocab field.
  `Status:` is treated as a free-form prose line and preserved
  through migrate into `## Migrated metadata` like any other extra
  metadata field.
- `docs migrate` writes `Lifecycle:` in new metadata blocks.
- `docs check` errors (not warns) on docs still carrying `Status:`
  as the controlled-vocab key.
- A one-shot `docs migrate --rename-status-to-lifecycle <tree>`
  helper sweeps an existing docs tree. The docs-cli project itself
  is the first customer (M7 Phase 5 ports our own `docs/` over).

This finding subsumes the original "free-form `Status:` is dropped"
issue — once `Status:` is no longer a special key, the existing
"preserve every metadata-shaped line that isn't a controlled-vocab
field" code path catches it automatically.

### F1 — Role inference is too narrow

`infer_role` matches a fixed set of suffix tokens. Trial 2 showed
the matcher handles snake_case TitleCase well, but a long tail of
real-world suffixes go unrecognised. Beyond suffix-matching, the
inference has no other signal source.

**Additional inference signals to add:**

- **H1 content.** `# … Plan`, `# … Specification`, `# … Status`,
  `# … Architecture` — strong role hint.
- **Section header pattern.** `## Goal` + `## Scope` +
  `## Requirements` + `## Exit criteria` → plan or spec.
  `## Current state` + `## Progress` + `## Updates` → status.
  `## ADR` + `## Context` + `## Decision` + `## Consequences` →
  decision (ADR pattern). Dated `## YYYY-MM-DD` sections → log.
- **Cross-ref shape.** A file mostly composed of `Related: <name>`,
  `Parent of: <name>` lines with little prose → reference. Lots of
  prose, few links → guide or notes.
- **Filename token-anywhere.** `eu-ai-act-section-reference-plan.md`
  ends in `-plan`, but inference should also catch `-reference-`
  mid-token and use both signals.
- **Sibling-set defaulting.** If 14 of 20 sibling files in the same
  subdir are `spec`, default a no-match file to `spec` at "medium"
  confidence rather than `notes`. Introduces a third confidence
  level between `high` and `low`.
- **`.docs.toml`-taught mappings:**
  `[migrate] role_suffixes = { "-rubric" = "template",
  "-memo" = "notes" }`.
- **Word-boundary tolerance.** Title-case files separated by spaces
  (`Project Name - Database Population Plan.md`) — the matcher
  should pick up `Plan` as a final word, not just `-plan`.

LLM-assisted classification is explicitly deferred; docs is
stdlib-only.

### F4 — Already-archived subdirs aren't normalised

Trial 1's `archived/` subdir was correctly inferred as
`Lifecycle: archived` per-file, but NO move was proposed to
`archive/YYYY-MM-DD/`. The convention's archive shape is
`archive/` (no `d`) + date subdir; the trial tree had `archived/`
(with `d`) flat. Both name shapes should be detected. Trial 2
confirmed: **0 of 25 trees** generated archive move proposals.

**M7 proposes:**

- Detect any root-level `archive/` or `archived/` subdir; propose
  moves for every file beneath into `archive/YYYY-MM-DD/<file>`,
  per-file date from mtime or `Updated:` field (NOT a global
  default).
- Surface as a single grouped action in the plan, not per-file
  moves.
- The existing `--date` flag overrides per-file dates when the
  operator wants a single date.

### F10 — Common real-world suffixes aren't in the vocab

Trial 2 surfaced a long tail of suffix tokens that real trees use
heavily but the convention doesn't recognise. Counts across 367
snake_case files in Trial 2:

| Suffix | Count | Proposed role mapping |
|---|---|---|
| `_Implementation` | 54 | new role `implementation`, OR alias → `notes` at medium confidence |
| `_v2` / `_v3` | 25 | version suffix — strip and re-match what's before it |
| `_Draft` | 12 | NOT a role — it's a Lifecycle hint (`Lifecycle: draft`) |
| `_Cards` | 8 | domain-specific — needs `add_roles` |
| `_Sketch` | 5 | new role `sketch` or alias → `notes` at medium |
| `_Ready` | 5 | NOT a role — Lifecycle hint |
| `_Constraints` | 5 | role `reference` |
| `_Handoff` | 5 | role `notes` at medium |
| `_Outline` | 4 | role `plan` at medium |
| `_Architecture` | 3 | role `reference` (architecture is already a known role) |
| `_Decision_Tree` | 2 | role `decision` at medium |

**M7 proposes:**

- Expand the core role vocab with `implementation`, `sketch`,
  `outline`, `memo`, `brief`. These are common across multiple
  unrelated trees in Trial 2, not domain-specific.
- Treat `_Draft` / `_Ready` / `_v1` / `_v2` as **non-role signals**:
  strip them and re-match the remaining stem. `MyPlan_v2.md` → `_Plan`
  after strip → `role: plan`. `MyPlan_Draft.md` → same role +
  `Lifecycle: draft` hint.
- Domain-specific suffixes (`_Cards`, `_Handoff`) get the
  `add_roles` treatment via `.docs.toml`.
- Per-`.docs.toml` `[migrate] role_suffixes` map (from F1) carries
  the long-tail mappings.

### F11 — Project-name casing inherited verbatim from dir name

Trial 2 produced 25 distinct project values — one per dir, perfect
matching. But the casing is a free-for-all inherited from
directory names. The casing-shape buckets:

- TitleCase no-separator (e.g. `FooBarBaz`) — 4 trees.
- TitleCase with digit-glued lowercase (e.g. `Abc5Migration`) —
  2 trees.
- SNAKE_UPPER (e.g. `FOO_BAR_BAZ`) — 1 tree.
- Mixed underscore TitleCase (e.g. `Foo_Bar_Baz`) — 2 trees.
- Bare TitleCase single word (e.g. `Plan`) — 2 trees.
- kebab-case (correct shape) — 9 trees.
- Other (e.g. a numeric-heavy prefix that gets parsed as the
  project) — 5 trees.

The convention's project vocab is implicitly lowercase-kebab.
`docs check` against an adopted tree would either error or warn
on the 16 non-conforming values.

**M7 proposes:**

- Normalise inferred project names to lowercase-kebab.
  Heuristic: split on case boundaries + underscores +
  digits-as-separators; rejoin with `-`; lowercase. So
  `FooBarBaz` → `foo-bar-baz`, `Abc5Migration` →
  `abc-5-migration`, `FOO_BAR_BAZ` → `foo-bar-baz`,
  `Foo_Bar_Baz` → `foo-bar-baz`.
- Surface the normalisation in the migrate plan: `project:
  foo-bar-baz (normalised from "FooBarBaz")` so the operator
  can override.
- A `[migrate] project_name` override in `.docs.toml` lets the
  operator pin the project value explicitly when normalisation
  is wrong.

### F12 — Milestone-number suffixes (`_M1`, `_M2`, ...) aren't recognised

12+ files in Trial 2 are named `<prefix>_M1.md`, `<prefix>_M2.md`,
or `<prefix>_M1_Implementation_Log.md`. The `_Log` suffix
correctly matches (role: log), but bare `_M1` / `_M2` files fall
to `notes`. These are clearly milestone-task-plan docs (this
project's own milestone files are `m1-parser-and-index.md`,
`m2-mutating-verbs.md`, etc.).

**M7 proposes:**

- Pattern: filename matches `_M\d+(?:_|\.md$)` at the end of the
  stem → `role: milestone` at medium confidence. H1-content
  inference (per F1) confirms (`# … Milestone …` → high
  confidence).
- This project's own milestone files use the `m\d+-` *prefix*
  pattern (which the convention already detects). F12 generalises
  to the *suffix* shape.

## Generalisation note

The trial trees informed M7; they are evidence, not the target.
The goal is to make `docs migrate` produce accurate plans on any
real-world tree — not to overfit to the 25 trees that surfaced
these findings. Concrete test: the new inference signals should
score equally well on fresh trees the M7 author hasn't seen
(the fresh-subagent integration gate in M8 exercises this).

## Decisions (carried forward + resolved at trial-time)

- `docs migrate` stays dry-run by default. `--apply` semantics
  unchanged. M7 adds NO new flags.
- The convention's archive shape (`archive/YYYY-MM-DD/<file>`)
  stays as-is. M7 adds normalisation TO it; doesn't change it.
- M6 has merged to main (2026-05-24, considered reviewed; not yet
  published to PyPI). M7 builds on M6's `src/docs_cli/` layout.
- **F0 controlled-vocab rename.** `Lifecycle:` replaces `Status:`
  for the controlled-vocab field. Breaking change — no
  backward-compat window.

## Open questions (for milestone-setup)

1. **OQ-A — Vocab additions for role.** Add `template`, `example`,
   `explainer`, `implementation`, `sketch`, `outline`, `memo`,
   `brief` to controlled-role vocab? Or expose via
   `[vocabulary] add_roles`? Recommendation: add `template`,
   `example`, `implementation`, `sketch`, `outline`, `memo`,
   `brief` to core (common across multiple trees). Leave
   `explainer` to `add_roles` (more niche).
2. **OQ-B — Project-name normalisation rules for ambiguous splits.**
   `Abc5Migration` → `abc-5-migration` or `abc5-migration`? Digit
   handling is the trickiest case. Recommendation: split on
   case-boundary AND letter-to-digit boundary (so `Abc5Migration`
   → `abc-5-migration`). Surface in plan with the original for
   operator override.
3. **OQ-C — Sibling-set defaulting threshold.** What fraction of
   siblings must share a role before defaulting a no-match file?
   Recommendation: 60% majority + minimum sample of 5 siblings.
4. **OQ-D — Confidence levels.** Today there are 2 (high, low).
   M7 introduces "medium" for sibling-set / H1-content / section-
   header matches. Should `docs check` treat medium as warning or
   error? Recommendation: warning.

## TDD Implementation Plan

Not yet expanded. M7 follows the same 10-phase TDD shape as
M1–M6. Drafted at milestone-setup once OQs are resolved.

Estimated phase shape:

- **Phase 1 — Define Contract.** Activate milestone; cli.md
  unchanged (no new flags); convention.md gets the F0 rename;
  status.md row added.
- **Phase 2 — Write Tests (RED).** New `tests/test_inference.py`
  + extension to `tests/test_migrate.py` for F0/F4/F10/F11/F12.
  H1 + section-header inference test cases derived from Trial 2
  trees (sanitised).
- **Phase 3 — Create Data/Fixtures.** Promote Trial 2 trees to
  `tests/fixtures/trees/real-trees/<tree-name>/` — sanitised
  aggressively (no third-party product / customer / feature
  names). Aim for 5–8 fixtures spanning size + style.
- **Phase 4 — Run Tests (RED Baseline).** Capture failures; pin
  to F0/F4/F10/F11/F12 root causes.
- **Phase 5 — Update Base Interfaces.** F0 rename across the
  parser + writer + this project's own `docs/` tree
  (mechanical). Sweep `Status:` → `Lifecycle:` in every
  in-project file; regenerate INDEX.
- **Phase 6 — Implement Core.** F1/F4/F10/F11/F12 in
  `migrate_plan` / `infer_role` / `infer_project`.
- **Phase 7 — Update Wrappers.** convention.md / cli.md / README
  reflect the new field name + the expanded vocab.
- **Phase 8 — Run Tests (GREEN).** 271 + N tests pass (M6's 271
  + M7's new ones).
- **Phase 9 — Integrate.** Re-run migrate on the Trial 2
  fixtures; confirm the headline-numbers success criteria.
- **Phase 10 — Quality, Docs, Refactor.** Sweep dogfood
  consistency; tag the M7 changeset.

## Deliverables (provisional — finalised at milestone-setup)

- F0 rename in parser + writer; convention.md spec change;
  `--rename-status-to-lifecycle` one-shot helper.
- F1 inference broadening: H1, section-header, sibling-set,
  word-boundary, `[migrate] role_suffixes` config.
- F4 archive normalisation in `migrate_plan`.
- F10 vocab additions + non-role suffix stripping.
- F11 project-name normalisation + `[migrate] project_name`
  override.
- F12 `_M\d+` suffix pattern.
- Sweep this project's own `docs/` from `Status:` to
  `Lifecycle:`.
- New tests under `tests/test_migrate.py` + new
  `tests/test_inference.py`.
- 5–8 sanitised real-tree fixtures under
  `tests/fixtures/trees/real-trees/`.
- Convention.md + cli.md updates for the rename + vocab additions.

## Success Criteria (provisional)

Re-running `docs migrate` against Trial 2's 25-tree corpus:

- Confidence high: ≥ 50% (today: 25.3%).
- Role `notes` fallback rate: ≤ 30% (today: 73.3%).
- Out-of-vocab `Status:` values: 100% preserved as free-form prose
  (today: 100% coerced and dropped).
- Archive moves proposed: ≥ 80% of trees that have an `archived/`
  subdir (today: 0/25 — including trees that did have one).
- Project-name normalisation hits ≥ 90% of Trial 2's 25 distinct
  values (today: 9/25 already conform).

(The agent-driveable integration gate lives in M8 — M7 only owns
the plan quality.)

## Phase Checklist

(Stub — finalised at milestone-setup.)

- [ ] Phase 1 — Define Contract
- [ ] Phase 2 — Write Tests (RED)
- [ ] Phase 3 — Create Data/Fixtures
- [ ] Phase 4 — Run Tests (RED Baseline)
- [ ] Phase 5 — Update Base Interfaces
- [ ] Phase 6 — Implement Core
- [ ] Phase 7 — Update Wrappers
- [ ] Phase 8 — Run Tests (GREEN)
- [ ] Phase 9 — Integrate
- [ ] Phase 10 — Quality, Docs, Refactor

## Trial-run artefacts

Captured 2026-05-24:

- `/tmp/m7-migrate-full.txt` — Trial 1 human-readable dry-run
  (1,376 lines, single tree, 235 files).
- `/tmp/m7-migrate.json` — Trial 1 JSON (235 entries).
- `/tmp/m7-trial2/ph-*.json` — Trial 2 per-tree JSON dry-runs
  (22 project-history trees).
- `/tmp/m7-trial2/{ideas,agents,specs}.json` — Trial 2 sibling
  dirs.

Promote to `tests/fixtures/trees/real-trees/` at milestone-setup.
Sanitise aggressively: NO third-party product / customer /
feature names. File shapes / sizes / metadata patterns are what
matter, not prose content.
