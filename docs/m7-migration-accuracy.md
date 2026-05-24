# M7 — Migration plan accuracy

Status: active
Role: milestone
Project: docs
Updated: 2026-05-24

Related:
- parent-of: m7-migration-accuracy-log.md
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
  `Lifecycle:`, vocab additions, archive-subdir normalisation,
  and **one new CLI flag** `--config-project <name>` to support
  the multi-project agent workflow. No new verbs. M8 owns the
  operator/agent ergonomics side (broader flags, skill
  references).
- Status: ACTIVE (started 2026-05-24, milestone-setup complete).
  Captured 2026-05-24 from a multi-tree trial (501 files across 25
  real-world sibling trees).

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
- **No user-facing rename helper.** The only existing tree on
  the old key is this project's own `docs/` — swept manually
  at M7 Phase 5 (one-off `sed`-equivalent edit, not a shipped
  feature). External adopters of M7+ never encounter the old
  key (a fresh `pip install docs-cli` ≥ 1.2.0 only knows
  `Lifecycle:`), so no user need exists. (Operator decision
  2026-05-24 — drop the verb; consider only functionalities a
  user would need.)

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

(Per F5: agents can override the inferred project for a single
migrate run via `--config-project <name>`; persistent override
via `.docs.toml [migrate] project_name`.)



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

### F5 — Multi-project trees: surface as inference hint; agent drives

Every file in Trial 1 (235) and every file per-tree in Trial 2
got a single project value inferred once from the root dir name
and applied uniformly. Multi-project trees — a parent dir with
multiple semantic projects underneath, common in monorepo doc
roots — are a real-world shape the tool should help an agent
adopt.

**The tooling can't decide** whether a subdir is "a data dir we
should exclude" vs. "a separate project we should treat
distinctly" — that's a semantic call. But it **can surface
candidates** and let the agent decide. Per the operator
direction (2026-05-24): give the agent hints, don't bake the
decision into the verb.

**Detection heuristic.** For each immediate subdir of the
migrated tree, compute the longest common filename prefix among
the .md files inside. If that prefix differs meaningfully from
the parent's inferred project AND covers ≥ N files (N=5), emit
one advisory line in the plan footer:

```
hint: subdir 'foo-tools/' looks like a separate project
      (common prefix 'foo_tools_', 17 .md files). To migrate it
      independently:  docs migrate <tree>/foo-tools/
                      --config-project foo-tools
```

That is the entire feature surface. The verb doesn't split the
plan, doesn't recurse, doesn't pre-materialise anything. The
agent reads the hint and decides:

- **(a) Ignore** — the parent project is the right grouping;
  proceed with the default plan.
- **(b) Exclude + recurse** — `--exclude foo-tools/` on the
  parent migrate; then `docs migrate <subdir> --config-project
  foo-tools` separately. M8's adoption playbook (F8) carries
  the worked example.
- **(c) Override the parent project** — pass `--config-project
  <name>` to the single parent migrate. Useful when the
  inferred name is wrong but the structure is correct.

**Why this is enough.** The trial revealed a *signal-to-noise*
problem (185-file data subdir muddying the plan) not a
*correctness* problem. F3 excludes (M8) clear noise; F5 hints
flag legitimate sub-project boundaries. The agent, armed with
both + the playbook, resolves multi-project trees in one or two
iterations of the dry-run loop.

**M7 proposes:**

- `migrate_plan` runs the per-subdir-prefix heuristic; emits
  one hint line per candidate in the plan footer.
- **`--config-project <name>` flag** on `docs migrate` — the
  one new M7 CLI surface, overrides the inferred project for
  the run. Persisting the override via `.docs.toml` `[migrate]
  project_name` (per F11) is the alternative for trees the
  agent owns.
- Hints are advisory only; no behaviour change beyond the
  extra footer lines.

## Generalisation note

The trial trees informed M7; they are evidence, not the target.
The goal is to make `docs migrate` produce accurate plans on any
real-world tree — not to overfit to the 25 trees that surfaced
these findings. Concrete test: the new inference signals should
score equally well on fresh trees the M7 author hasn't seen
(the fresh-subagent integration gate in M8 exercises this).

## Decisions (carried forward + resolved at milestone-setup, 2026-05-24)

### Carried forward from M4 / M6

- `docs migrate` stays dry-run by default. `--apply` semantics
  unchanged. **M7 adds exactly one new CLI flag**:
  `--config-project <name>` on `docs migrate`, the override
  knob the multi-project-hint workflow (F5) tells the agent
  about. No other new flags; no new verbs. The in-project
  `Status:` → `Lifecycle:` sweep is a one-off manual edit, not
  a shipped feature.
- The convention's archive shape (`archive/YYYY-MM-DD/<file>`)
  stays as-is. M7 adds normalisation TO it; doesn't change it.
- M6 has merged to `main` (2026-05-24, considered reviewed; not
  yet published to PyPI). M7 builds on M6's `src/docs_cli/`
  layout.

### Resolved at trial-time + milestone-setup

- **F0 controlled-vocab rename.** `Lifecycle:` replaces `Status:`
  for the controlled-vocab field. Breaking change — no
  backward-compat window. Free-form `Status:` lines are
  preserved through migrate as `## Migrated metadata`. (Operator,
  2026-05-24.)
- **Tree-wide single source of truth for excludes.** Decision
  recorded in M8's stub; M7 is unaffected — M7 adds no exclude
  surface. (For consistency: noted here so M7 setup confirms it
  has no dependency to satisfy.)

### OQ-A resolved — Role vocab additions

Add to **core controlled-role vocab**: `template`, `example`,
`implementation`, `sketch`, `outline`, `memo`, `brief`. These are
common across multiple unrelated trees in Trial 2 (the largest
group, `_Implementation`, accounted for 54 of 367 snake_case
files — 15%). Leave `explainer` to `[vocabulary] add_roles` (more
niche; appeared in only one tree). Convention.md gets a single
sentence per new role in the role-vocabulary section.

### OQ-B resolved — Project-name normalisation for digit-glued names

Split on case boundaries AND letter-to-digit boundaries. So:

- `FooBarBaz` → `foo-bar-baz`
- `Abc5Migration` → `abc-5-migration` (digit isolated)
- `FOO_BAR_BAZ` → `foo-bar-baz` (snake_upper)
- `Foo_Bar_Baz` → `foo-bar-baz` (mixed)
- `bugs-2026-01-26` → `bugs-2026-01-26` (already kebab; dates
  preserved — digit-after-digit doesn't trigger a split)

Surface the normalisation inline in the migrate plan output:
`project: foo-bar-baz (normalised from "FooBarBaz")` so the
operator can spot mis-normalisations. The
`[migrate] project_name` override in `.docs.toml` lets the
operator pin the project value explicitly.

### OQ-C resolved — Sibling-set defaulting threshold

A file with no matching suffix defaults to the modal sibling role
when **both** conditions hold:

- ≥ 60% of sibling files share the same role (60% majority).
- The subdir has ≥ 5 sibling files total (minimum sample).

Below either threshold, the file falls to `notes` at low
confidence (today's behaviour). When sibling defaulting fires,
confidence is **medium** (the new third level — see OQ-D).

### OQ-D resolved — Confidence levels: introduce "medium"

Add a third confidence level **`medium`** between `high` and
`low`. Used by:

- Sibling-set defaulting (OQ-C).
- H1-content-based inference (F1).
- Section-header-pattern inference (F1).
- Non-role suffix stripping that then matches (F10): `MyPlan_v2.md`
  strips to `MyPlan` and matches `_Plan` — but with `medium`
  confidence to reflect the strip.

**`docs check` treats medium as warning** (exit 1), not error
(exit 2). Rationale: medium-confidence inferences are good-enough
defaults that don't need operator attention but should be
surfaced for review. `docs list --confidence` filter (M7
extension) takes `high`, `medium`, `low`. Trial 2 confidence
metric becomes `(high + medium) / total` for the success
criterion.

## Open questions

_All four milestone-setup OPEN QUESTIONS are resolved 2026-05-24,
recorded as Decisions above. No new questions surfaced during
setup._

## TDD Implementation Plan

The ten phases follow the methodology in
[status.md](status.md). Because M7 is **breaking the convention
schema** (F0 rename) AND **broadening inference** AND **sweeping
this project's own docs over to the new key**, the phases bias
toward landing F0 first as a stable substrate before the
inference work touches the parser.

### Phase 1: Define Contract

- **Objective:** Promote this milestone from `draft` to `active`
  (already done at milestone-setup, 2026-05-24); create the log
  skeleton; record OQ A–D resolutions as Decisions (done); refresh
  status.md's "Current milestone" and "Next action" to point at
  Phase 2. No code change; no convention edits yet (those land at
  Phase 5 / Phase 7 to keep the contract phase reviewable in
  isolation).
- **Files (text/docs work):**
  - `docs/m7-migration-accuracy.md` — Status: draft → active
    (done); Updated: bumped; Decisions section populated with
    OQ A–D resolutions (done).
  - `docs/m7-migration-accuracy-log.md` — created with the M5/M6
    log skeleton (frontmatter, metadata, OQ summaries, phase
    table, files-to-modify table, phase-logs placeholder).
  - `docs/status.md` — "Current milestone" rewritten to mark M7
    setup complete + Phase 2 next; M7 row in the milestone table
    flipped from "stub drafted" to "in flight (Phase 1 complete,
    Phase 2 next)".
  - `docs/plan.md` — already lists M7 (committed `1df6ec6`); no
    further edit beyond the touch.
  - `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
    regenerated in lockstep so the new log appears.
- **Exit:** M7 is `active`; log exists; status.md reflects
  Phase 1 complete; 271 tests still GREEN; ruff/format/mypy
  clean; `docs check docs/` exit 0; INDEX snapshot matches.
  No code change has happened. No convention change has happened.

### Phase 2: Write Tests (RED)

- **Objective:** Express every M7 requirement (F0/F1/F4/F10/F11/
  F12) as a failing check before any implementation. Tests
  collect cleanly; every new assertion fails for the **intended**
  reason (the unimplemented surface, not misconfiguration).
- **New test files:**
  - `tests/test_lifecycle_rename.py` (F0). Asserts:
    1. Parser accepts `Lifecycle: active` as the controlled-vocab
       key (today: parser only accepts `Status:`).
    2. Parser rejects `Status: active` as the controlled-vocab
       key — a `Status:` line is now a free-form prose extra
       field, not the lifecycle.
    3. `docs check` errors (exit 2) on a doc with `Status: <vocab
       value>` and no `Lifecycle:` line.
    4. `docs check` accepts a doc with `Lifecycle: active` and a
       free-form `Status: Implementation in progress` line.
    5. `docs migrate` preserves a foreign tree's `Status: <prose>`
       line as an entry under `## Migrated metadata` rather than
       coercing.
  - `tests/test_inference.py` (F1, F10, F12). Asserts:
    1. Word-boundary suffix tolerance:
       `Project Name - Database Population Plan.md` →
       `role: plan`.
    2. Non-role suffix stripping: `MyPlan_v2.md` and
       `MyPlan_Draft.md` strip to `MyPlan` → `role: plan` at
       confidence `medium`; `MyPlan_Draft.md` also surfaces
       `Lifecycle: draft` hint.
    3. New core vocab roles match: `*_Implementation.md`,
       `*_Sketch.md`, `*_Outline.md`, `*_Memo.md`, `*_Brief.md`,
       `*_Template.md`, `*_Example.md` → respective role at
       high confidence.
    4. `_M\d+` suffix detection: `Foo_M1.md`, `Foo_M2.md`,
       `Foo_M10.md` → `role: milestone` at medium confidence.
    5. H1-content inference: `# Foo Plan` → `role: plan` at
       medium confidence when the suffix doesn't match.
    6. Section-header pattern inference: a file with
       `## Goal` + `## Scope` + `## Requirements` →
       `role: plan` at medium confidence.
    7. Sibling-set defaulting: in a 10-file subdir where 7 are
       `spec`, an 8th unrecognised-suffix file gets
       `role: spec` at medium confidence (OQ-C: 60% threshold,
       ≥ 5 sibling minimum).
    8. Sibling-set NOT defaulting when subdir has < 5 files
       (below sample threshold).
    9. Sibling-set NOT defaulting when no role hits 60% (below
       majority threshold).
  - `tests/test_project_normalisation.py` (F11). Asserts the
    OQ-B normalisation rules — TitleCase, snake_upper,
    digit-glued, mixed — all produce expected kebab-case.
    Includes a regression case for kebab-case input
    (`embedded-ai-discovery-parallel`) passing through unchanged.
    Includes a test that the `[migrate] project_name` override
    in `.docs.toml` wins over normalisation.
    Includes a test that the migrate plan's human output surfaces
    `(normalised from "<original>")` when normalisation changed
    the value.
  - `tests/test_archive_normalisation.py` (F4). Asserts:
    1. A foreign tree with `archived/<file>.md` at root generates
       a proposed move to `archive/YYYY-MM-DD/<file>.md` in the
       migration plan, with date taken per-file from mtime or
       `Updated:`.
    2. A foreign tree with `archive/<file>.md` (no `d`) also
       triggers normalisation.
    3. `--date YYYY-MM-DD` overrides per-file dates with a global
       date.
    4. A file already at `archive/YYYY-MM-DD/<file>.md`
       (correctly placed) is NOT proposed for any move.
- **Extensions to existing test files:**
  - `tests/test_migrate.py` — keep, extend. Add a confidence-
    distribution test: against a representative fixture, confirm
    `(high + medium) / total ≥ 0.5`. (The success-criterion
    measure, codified.)
- **Quality discipline:**
  - All new tests use the existing fixture-loading helpers from
    `tests/conftest.py`.
  - No fixture authoring in this phase — that's Phase 3.
  - `ruff` / `mypy` / `format` clean tree-wide.
- **Exit:** every new test file collects cleanly; every new
  test fails or errors on the intended unimplemented surface.
  M6's 271 tests stay GREEN. Phase 4 captures the verbatim
  baseline.

### Phase 3: Create Data/Fixtures

- **Objective:** Stage the fixtures the new tests reference.
  This is the load-bearing data-engineering phase — promote
  selected Trial 2 trees from `/tmp/m7-trial2/` to
  `tests/fixtures/trees/real-trees/` with **aggressive
  sanitisation**: no third-party product / customer / feature
  names; file shapes / sizes / metadata patterns preserved.
- **Fixture set to promote (5 trees, spanning size + style):**

  | Fixture slug | Original | Files | Style | Notes |
  |---|---|---|---|---|
  | `kebab-tiny/` | one of the `ph-langfuse*` trees | ~3 | kebab-case | smallest size class |
  | `snake-medium/` | one of the medium `ph-*` trees | ~30 | snake_TitleCase | dominant real-world shape |
  | `snake-large/` | one of the `ph-embedded-*` trees | ~70–90 | snake_TitleCase | scale stress |
  | `archive-subdir/` | derived from Trial 1's tree | ~10 + `archived/` | mixed | F4 archive normalisation test |
  | `mixed-naming/` | a tree with multiple style families | ~15 | TitleCase + space + kebab | F1 word-boundary stress |

- **Per-finding extra fixtures (small, focused):**
  - `tests/fixtures/status-prose/` — 6 single-file fixtures
    with various `Status: <prose>` shapes, for F0 + F2.
  - `tests/fixtures/project-names/` — 7 single-file fixtures
    with TitleCase / snake_upper / digit-glued / mixed
    directory shells, for F11.
  - `tests/fixtures/sibling-defaulting/` — 3 subdirs:
    `majority-met/` (10 files, 7 spec + 3 mixed),
    `majority-not-met/` (10 files, 4 spec + 6 mixed),
    `sample-too-small/` (4 files, 4 spec + 0 mixed).
- **Sanitisation rules (enforced before commit):**
  - Replace product / customer / company names with `Foo`,
    `Bar`, `Baz`, `Acme`, generic placeholders.
  - Replace feature / module names with semantically-equivalent
    generic versions (`embedded-ai-discovery-parallel` →
    `feature-discovery-parallel`).
  - Truncate file bodies aggressively — the metadata block + H1
    + first paragraph is enough for every inference test.
    Preserve file size buckets if a test depends on them.
  - Strip dates that could fingerprint the original tree.
- **`docs check` must remain clean on the docs root** — fixture
  files live under `tests/fixtures/trees/` which is not a docs
  root (no `.docs.toml`), so they don't interfere.
- **Exit:** every fixture path the new tests reference exists;
  sanitisation review passes (a manual grep for product/customer
  names returns clean); RED baseline failures (Phase 4) trace to
  the unimplemented surface, not to missing fixtures.

### Phase 4: Run Tests (RED Baseline)

- **Objective:** Confirm the new RED tests fail for the
  intended reasons; pin the failure modes in the log.
- **Actions:**
  ```sh
  .venv/bin/python -m pytest tests/ -q --tb=short 2>&1 | tee /tmp/m7-phase-4-baseline.txt
  .venv/bin/ruff check .
  .venv/bin/ruff format --check .
  .venv/bin/mypy
  .venv/bin/docs check docs/
  ```
- **Expected RED matrix:**

  | Test group | Failure mode | Root cause |
  |---|---|---|
  | F0 lifecycle rename (5 tests) | `KeyError` / `AssertionError` on `Lifecycle:` parsing | Parser only knows `Status:` today |
  | F1/F10/F12 inference (9 tests) | Wrong role inferred (mostly `notes`) | Inference broadening unimplemented |
  | F11 project normalisation (per fixture, ~5 tests) | `AssertionError: 'OrgInfo' != 'org-info'` | No normalisation today |
  | F4 archive normalisation (4 tests) | `AssertionError: no move_to in plan` | Archive normalisation unimplemented |
  | F5 multi-project hints (3 tests) | `AssertionError: no hint in plan footer`; `argparse` error on `--config-project` | Hint emission + flag unimplemented |
  | confidence-distribution test | `(high + medium) / total ≈ 0.25` < 0.50 | Inference broadening unimplemented |

- **Aggregate expected:** M6's 271 + ~27 new RED = ~298
  collected, ~27 RED. M6's 271 stay GREEN. (Adjustments from
  the original ~25-test plan: -1 for the dropped rename-
  helper test, +3 for the new F5 multi-project hint tests
  added 2026-05-24.)
- **Exit:** Phase-4 log entry captures the verbatim baseline
  output; every RED traces to its intended unimplemented
  surface; M6's quality gate stays clean.

### Phase 5: Update Base Interfaces

- **Objective:** The F0 controlled-vocab rename. **This is the
  load-bearing structural change.** Sweep this project's own
  `docs/` tree from `Status:` to `Lifecycle:` (manual one-off
  edit — no shipped helper); update the parser to accept only
  `Lifecycle:` for the controlled-vocab key. Add the third
  confidence level. No inference-broadening work yet (that's
  Phase 6).
- **Parser + writer changes:**
  - `src/docs_cli/cli.py` — rename `STATUS_KEY` constant to
    `LIFECYCLE_KEY` (or equivalent); parse only `Lifecycle:`
    as the controlled-vocab key; treat `Status:` as a free-form
    extra field (handled by the existing extra-field
    preservation path).
  - Add `Confidence` enum / sentinel: `HIGH`, `MEDIUM`, `LOW`
    (today: just `high` / `low` strings). Update every emit
    site to use the enum.
  - Rename `Config.add_statuses` → `Config.add_lifecycles`
    and the `.docs.toml [vocabulary] add_statuses` key →
    `[vocabulary] add_lifecycles`. Same mechanical breaking
    rename as the field itself.
  - Add `Config.role_suffixes: dict[str, str]` for F1's
    per-`.docs.toml` `[migrate] role_suffixes` map (set up
    at Phase 5; consumed at Phase 6).
  - Add `Config.project_name: str | None` for F11's per-tree
    override (set up at Phase 5; consumed at Phase 6).
  - Argparse: add `--config-project <name>` to `docs migrate`
    (the one new M7 flag, per F5). Overrides inferred
    project for the run.
- **In-project sweep (this project's own `docs/`):**
  - Every `docs/*.md` file's `Status: <vocab>` line becomes
    `Lifecycle: <vocab>`. Mechanical sweep with `sed` (or
    equivalent) — one-off edit, not a shipped feature. The
    regex covers the full `BUILTIN_STATUSES` set (`active`,
    `blocked`, `done`, `draft`, `superseded`, `archived`):
    `sed -i 's/^Status: \(active\|blocked\|done\|draft\|superseded\|archived\)$/Lifecycle: \1/' docs/*.md`
    Verify with `grep -l "^Status:" docs/` → empty after.
  - 27 docs files touched at the audit point this plan was
    written (audit 2026-05-24: 23 with `Status: active` + 4
    with `Status: done`). Count may drift before Phase 5
    actually runs; the sweep handles whatever's there.
    `Updated:` bumped per docs convention (`docs touch <file>`
    once per file, or batched).
  - `tests/fixtures/expected/docs-INDEX.md` regenerated after
    the sweep.
  - **`.docs.toml` sweep:** if this project's `docs/.docs.toml`
    has an `[vocabulary] add_statuses` key, rename it to
    `add_lifecycles` (currently absent — no edit needed). Any
    future project adopting M7+ uses the new key from day one.
- **Convention.md edit (single point of truth):**
  - The "Metadata block" section's `Status:` paragraph is
    rewritten as `Lifecycle:`. Free-form `Status:` is now
    documented as a common extra-field shape (preserved like
    `Owner:`, `Tags:`).
- **Test updates:**
  - Any existing M1–M6 test that asserts the literal string
    `Status:` in metadata gets updated to `Lifecycle:`.
    `grep -rn "Status:" tests/` to find them. (Distinct from
    the inference tests; this is just the schema rename.)
  - `tests/fixtures/expected/docs-INDEX.md` reflects the
    renamed key if it appears in the snapshot (it doesn't
    today — INDEX uses the role+project grouping not the
    lifecycle).
- **Exit:** F0 tests in `test_lifecycle_rename.py` flip from
  RED to GREEN; this project's own `docs/` parses + checks
  clean under the new key; `docs check docs/` exit 0; 271
  M6 tests + 6 F0 tests = 277 GREEN; inference tests
  (Phase 6's surface) still RED.

### Phase 6: Implement Offline/Core Path

- **Objective:** Implement F1 (broader inference), F10 (vocab
  + non-role stripping), F11 (project normalisation), F12
  (`_M\d+` milestone suffix), F4 (archive normalisation).
  All remaining M7 RED tests turn GREEN.
- **`src/docs_cli/cli.py` changes:**
  - `infer_role`:
    - Add new core vocab to the ROLES set: `template`,
      `example`, `implementation`, `sketch`, `outline`, `memo`,
      `brief`.
    - Word-boundary tolerance: also match `<token>` at end of
      filename (case-insensitive) separated by space or
      underscore, not just hyphen.
    - Non-role suffix stripping: strip `_Draft`, `_Ready`,
      `_v\d+` from the stem before matching; if the strip
      enables a match, return at **medium** confidence and
      (for `_Draft`) surface a `Lifecycle: draft` hint.
    - `_M\d+` suffix pattern → `role: milestone` at medium
      confidence.
    - H1-content inference: read the first H1 line; if it ends
      with a role-word (`Plan`, `Spec`, `Status`, `Charter`,
      `Architecture`, etc.), return that role at medium
      confidence (only when suffix matching didn't already
      hit).
    - Section-header inference: scan top-level `##` headers;
      apply pattern table (Goal+Scope+Requirements → plan;
      Context+Decision+Consequences → decision; dated headers
      → log). Medium confidence.
    - Sibling-set defaulting: when no signal hits, count
      sibling roles in the same subdir; if a single role
      reaches ≥ 60% AND the subdir has ≥ 5 files, return that
      role at medium confidence.
  - `infer_project`:
    - Add `normalise_project_name(name: str) -> str` helper.
      Splits on case boundaries + underscores + letter-to-digit
      boundaries; rejoins with `-`; lowercases. Preserves
      digit-after-digit (so `bugs-2026-01-26` stays intact).
    - Apply normalisation to the inferred project value.
    - Honour `[migrate] project_name = "..."` in `.docs.toml`
      as an override.
    - Surface `(normalised from "<original>")` in the migrate
      plan's human output when normalisation changed the
      value.
  - `migrate_plan`:
    - F4 archive normalisation. On detecting a root-level
      `archive/` or `archived/` subdir, generate `move_to`
      entries for each file beneath into
      `archive/YYYY-MM-DD/<file>`. Per-file date from mtime or
      `Updated:` field; `--date` overrides globally. Files
      already correctly placed under `archive/YYYY-MM-DD/`
      generate no move.
    - F5 multi-project hint emission. For each immediate
      subdir, compute longest-common-prefix of `.md`
      filenames; if it differs meaningfully from the parent
      project AND the subdir has ≥ 5 `.md` files, emit a hint
      line in the plan footer naming the candidate sub-project
      and the suggested `docs migrate <subdir> --config-project
      <name>` invocation.
    - Honour `--config-project <name>` CLI override when
      present (F5 hand-off).
  - `Config.role_suffixes` field — a `dict[str, str]` mapping
    custom suffix tokens to role names. Loaded from
    `[migrate.role_suffixes]` in `.docs.toml`. Merged into
    the suffix-matching list at inference time.
- **convention.md (touched at Phase 7 for the user-facing
  doc):** Phase 6 may add a brief inline comment in
  `_load_config` near the new key — actual user-facing prose
  comes at Phase 7.
- **Exit:** all M7 tests GREEN; `docs check docs/` exit 0;
  ruff / format / mypy clean tree-wide; the confidence-
  distribution test passes (`(high+medium)/total ≥ 0.5` on
  the medium-fixture).

### Phase 7: Update Tool/Wrapper Layer

- **Objective:** Update user-facing specs + skill references
  to reflect M7's surface changes. No code changes (those
  landed at Phase 5/6).
- **Files (text/docs work):**
  - `docs/convention.md`:
    - Replace every `Status:` reference (in the schema
      definition) with `Lifecycle:`.
    - Add a paragraph noting that `Status:` is now a common
      extra-field shape, preserved verbatim under
      `## Migrated metadata`.
    - Document the expanded role vocab (the 7 new core
      roles).
    - Document the new confidence level `medium`.
    - Document `[migrate.role_suffixes]` and
      `[migrate] project_name`.
    - Rename `[vocabulary] add_statuses` documentation →
      `[vocabulary] add_lifecycles` (consistent with the F0
      field rename).
  - `docs/cli.md`:
    - Note the F0 breaking change at the top of the migrate
      verb section.
    - `docs migrate --config-project <name>` synopsis +
      example (the one new M7 flag, per F5).
    - Document the project-name normalisation in the migrate
      plan's output shape.
    - Document the multi-project hint footer shape (per F5).
    - `docs check` exit codes: clarify that medium-confidence
      inferences emit warnings (exit 1), not errors (exit 2).
  - `docs/architecture.md`:
    - Update the `Config` schema illustration to include
      `role_suffixes` and `project_name`.
    - No structural diagram change.
  - `docs/status.md`:
    - "Watch out for" gets a new entry: the F0 rename was
      done in M7 Phase 5; anything still referencing
      `Status:` in M1–M5 docs is historical.
  - `README.md`:
    - Any installation / quick-start that mentions `Status:`
      → `Lifecycle:`.
    - One-line note in the "What's new in v1.1" section if
      it exists.
  - `CHANGELOG.md`:
    - New `## 1.2.0 — UNRELEASED` section with the M7
      breaking change called out. M6 (1.1.0) stays as the
      prior entry; M7 ships as 1.2.0 (per semver, breaking
      schema rename).
  - `src/docs_cli/skill/references/convention.md` and
    `references/cli.md` — resync from `docs/convention.md` +
    `docs/cli.md` (the existing lockstep mechanism).
  - `pyproject.toml` — bump version `1.1.0` → `1.2.0`
    (matches CHANGELOG); bump `__version__` in `cli.py`.
  - `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
    regenerated in lockstep.
- **Exit:** convention.md, cli.md, architecture.md, README.md,
  CHANGELOG.md all up to date with M7's surface; the bundled
  skill references mirror the source; INDEX matches snapshot;
  ruff / format / mypy clean; pytest still GREEN; the
  skill-refs lockstep test (`test_skill_refs.py`) still
  passes.

### Phase 8: Run Tests (GREEN)

- **Objective:** Capture the full GREEN gate verbatim. M6's
  271 + M7's ~25 = ~296 GREEN; ruff / format / mypy / docs
  check clean.
- **Actions:**
  ```sh
  .venv/bin/python -m pytest tests/ -q
  .venv/bin/ruff check .
  .venv/bin/ruff format --check .
  .venv/bin/mypy
  .venv/bin/docs check docs/
  .venv/bin/docs index --root docs/ --dry-run
  ```
- **Exit:** every command exit 0; verbatim output captured in
  the Phase 8 log entry; **STOP** here if anything is RED —
  fix the root cause, never relax a test.

### Phase 9: Implement Online/Integration

- **Objective:** Mapped to **dogfooding against the Trial 2
  fixtures** (M7 has no online surface). Confirm the
  quantitative success criteria:
  - Confidence high+medium ≥ 50% (target; today 25%).
  - Role `notes` fallback rate ≤ 30% (today 73%).
  - Out-of-vocab `Status:` values: 100% preserved.
  - Archive moves proposed: ≥ 80% of trees with an `archived/`
    subdir.
  - Project-name normalisation hits ≥ 90% of Trial 2's 25
    distinct values.
- **Actions:**
  ```sh
  for fixture in tests/fixtures/trees/real-trees/*/; do
    .venv/bin/docs migrate --json "$fixture" > "/tmp/m7-phase-9-$(basename $fixture).json"
  done
  .venv/bin/python tests/manual/m7_success_criteria.py /tmp/m7-phase-9-*.json
  ```
  (A small helper script under `tests/manual/` aggregates and
  reports the metrics. Not auto-run as part of the test suite
  because Trial 2 is fixture-derived; the success-criterion
  test in `test_migrate.py` is the per-fixture version.)
- **Exit:** all 5 quantitative success criteria met. If any
  is missed, surface the gap, decide whether to iterate
  Phase 6 or scope it out for a follow-up milestone.

### Phase 10: Quality, Docs, Refactor

- **Objective:** Polish + ship. Sweep dogfood consistency;
  append milestone-completion summary; merge M7 stack to
  `main`; tag `v1.2.0`; (optionally) publish to PyPI
  operator-side per the runbook.
- **Actions:**
  - Sweep this project's own `docs/`: every M1–M6 log file
    reviewed for stale `Status:` references (some legitimately
    historical — M5's log says "Status: active" because that
    was the field name when M5 shipped; preserve those as
    historical record).
  - Append "Milestone-completion summary" to
    `docs/m7-migration-accuracy.md` (mirror M6's summary
    shape).
  - Update `docs/status.md`: M7 → Complete (DATE); milestone
    table row flipped; "Next action" rewritten to M8 setup
    or M6 publish (whichever is operator-prioritised).
  - Update `CHANGELOG.md`: replace `## 1.2.0 — UNRELEASED`
    with the actual ship date.
  - `docs index --root docs/`; copy onto fixture.
  - Final quality gate: pytest GREEN; ruff / format / mypy
    clean; `docs check docs/` exit 0.
  - **Publish: DEFERRED.** Operator decision 2026-05-24 (M8
  OQ-C): no per-milestone publish. The first PyPI publish
  ships the M6 + M7 + M8 surface as one artifact after M8 (or
  later, pending review cycles). M7 Phase 10 stops at
  "ready to publish": `python -m build` produces
  `dist/docs_cli-1.2.0-*` artifacts locally; `twine check`
  PASS; no `twine upload`; no tag; no GitHub release. The
  Phase 10 log entry records "ready; deferred to post-M8
  batched publish".
- **Exit:** M7 task plan + log carry completion summaries;
  status.md reflects M7 → Complete; CHANGELOG entry dated;
  `dist/docs_cli-1.2.0-*` built locally and `twine check`
  clean; the project's own docs all on `Lifecycle:`; 296+
  tests GREEN. **No publish, no tag, no GitHub release** —
  those land at the batched post-M8 publish.

## Deliverables (provisional — finalised at milestone-setup)

- F0 rename in parser + writer; convention.md spec change.
  (No `--rename-status-to-lifecycle` helper — operator
  decision 2026-05-24 to drop it; this project's own sweep is
  a one-off manual `sed` edit, not a shipped feature.)
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
