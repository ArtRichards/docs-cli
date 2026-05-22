# M5 — Implementation Log

Status: active
Role: log
Project: docs
Updated: 2026-05-22

Related:
- child-of: m5-claude-code-skill.md
- pairs-with: status.md

## Implementation metadata

- Project: docs
- Milestone: M5 — Claude Code skill
- Started: 2026-05-22
- Progress: Milestone activated 2026-05-22 — task plan and this log created on
  `m5/milestone-setup`. All four milestone-setup OPEN QUESTIONS (OQ1–OQ4) are
  resolved (operator-confirmed 2026-05-22, see below) and recorded as Decisions
  in the task plan. Phases 1–10 not yet started; Phase 1 (Define Contract) is
  the next action.

(Note: doc-lifecycle status is in the front-matter `Status:` field above. This
section tracks milestone progress, which is distinct.)

## Milestone-setup open questions — resolved (2026-05-22)

Four questions were surfaced while authoring the task plan; all four were
triaged against [plan.md](plan.md) and the M1–M4 precedent and operator-
confirmed on 2026-05-22. Each is recorded in full — question, why it matters,
recommendation, and a **RESOLVED** verdict — under "OPEN QUESTIONS — resolved"
in [m5-claude-code-skill.md](m5-claude-code-skill.md), and as a Decision
(OQ1–OQ4) in that file's Decisions section. They are summarised here:

1. **TDD-cycle mapping for an artifact milestone (OQ1) — RESOLVED, approved as
   recommended.** Keep all ten phases; "tests" is a two-part oracle —
   `tests/test_skill.py` (structural, automatable, RED→GREEN in CI) plus the
   behavioural trigger-scenario checklist walked at the Phase 9 dogfood with
   negative rows for over-triggering. No phase marked N/A; Phase 3 records a
   conscious "nothing to stage".
2. **Skill install path (OQ2) — RESOLVED, approved as recommended.** Author the
   skill in-repo at `skills/docs/`; document a manual copy/symlink into
   `~/.claude/skills/docs/` parallel to the `bin/docs` install — no installer
   script, no `$HOME` write in the milestone.
3. **`plan.md` open questions (OQ3) — RESOLVED, approved as recommended.** M5
   opens no new `plan.md` question; the parked extra-field allowlist question
   stays parked as post-v1 work; Phase 10 notes v1 completion. (Conductor
   auto-resolved — conventional, follows the M4 precedent.)
4. **Skill `name` (OQ4) — RESOLVED: use `docs`.** Consistent with
   [plan.md](plan.md)'s `~/.claude/skills/docs/` path; no host collision
   exists; over-triggering is handled by the `description`, not the name.
   (Conductor auto-resolved — naming with an obvious default.)

## Summary

Author the project's final deliverable — a Claude Code skill at
`skills/docs/SKILL.md` — that makes an agent reach for the `docs` verbs
automatically when doing documentation work in a `docs`-managed tree. The
skill adds no CLI surface and changes no verb behaviour: it is a markdown
artifact whose `description` triggers on the right contexts and whose body
redirects to the appropriate `docs` verb (`new`, `archive`, `index`, `check`,
`list`, `mv`, `touch`, `migrate`) instead of hand-editing metadata,
hand-curating `INDEX.md`, or hand-moving an archived doc. The convention
itself is not re-taught — the body points at `convention.md` and `cli.md`.
M5's exit criterion is behavioural: the agent stops hand-editing `INDEX.md` in
this repo and runs `docs index`.

## TDD Phase Progress

| Phase | Status | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-05-22 | `skills/docs/SKILL.md` created with valid frontmatter + stub body; `tests/test_skill.py` created with 8 check signatures; `cli.md` skill pointer + `architecture.md` skill/install note; `status.md` refreshed. |
| 2. Write Tests (RED) | Complete | 2026-05-22 | `tests/test_skill.py` — the 8 structural checks implemented; the 11-row trigger-scenario checklist written into this log. RED: 3 content-driven checks fail on the stub body / TODO tokens; 5 shape/clutter checks legitimately pass. |
| 3. Create Data/Fixtures | Pending | — | No new fixture tree — structural checks read the real artifact + `bin/docs`; the dogfood reads this repo's `docs/`. A conscious "nothing to stage" outcome. |
| 4. Run Tests (RED Baseline) | Pending | — | `pytest tests/` — every `test_skill.py` check RED against the stub body; M1–M4's 236 tests green; the trigger checklist fully unsatisfied. Session pauses here. |
| 5. Update Base Interfaces | Pending | — | Author the skill frontmatter — `name` + the trigger-scoped `description`. |
| 6. Implement Offline/Core Path | Pending | — | Author the skill body — per-trigger verb redirection, the no-hand-edit guardrail, binary/root-location guidance. |
| 7. Update Tool/Wrapper Layer | Pending | — | Any minimal bundled reference file; finalise the `architecture.md` install note and the `cli.md` skill pointer; no-clutter check. |
| 8. Run Tests (GREEN) | Pending | — | Full suite green incl. `test_skill.py`; `ruff` / `mypy` clean tree-wide. |
| 9. Implement Online/Integration | Pending | — | Dogfood: walk the trigger-scenario checklist against the authored skill; `INDEX.md` regenerated only via `docs index`; `docs check docs/` exit 0. |
| 10. Quality, Docs, Refactor | Pending | — | Close out: `status.md` → M5 Complete + project v1-complete; completion summaries; INDEX + snapshot regenerated. |

## Current State Analysis (snapshot at milestone kickoff, 2026-05-22)

_Captured before Phase 1; historical. Post-milestone state lives in the
Milestone-completion summary at the bottom of this log._

- **Codebase:** `bin/docs` shipped at M1+M2+M3+M4 (~2,200 lines) — parser,
  walker, renderer, eight verbs (`index`, `new`, `archive`, `mv`, `touch`,
  `check`, `list`, `migrate`), config loading, surgical metadata editors,
  validation, query, and the foreign-tree importer. 236 passing tests across
  17 files; `ruff` / `mypy` clean tree-wide; `docs check docs/` exits 0.
- **What M5 adds:** **no code.** M5 ships a `SKILL.md` markdown artifact at
  `skills/docs/` plus one new test file (`tests/test_skill.py`) that checks
  the artifact's structural properties. Every `docs` verb the skill names is
  already shipped, specified in [cli.md](cli.md), and tested.
- **Reuse available:** `conftest.py` already loads `bin/docs` as the `docs`
  module — `tests/test_skill.py` reuses that to assert the skill names only
  real subcommands (against `_build_parser()` / the verb list). No new test
  harness is needed.
- **Skill-authoring guidance:** the `skill-creator` skill on this host
  defines the rules M5 follows — a required `SKILL.md` with `name` +
  `description` frontmatter; a concise body (≤ ~500 lines, imperative voice);
  no auxiliary documentation files; progressive disclosure into a
  `references/` file only if the body grows.
- **Gap M1–M4 left:** the verbs exist but nothing makes an agent *use* them —
  an agent working in a docs tree will still hand-edit `INDEX.md` or
  hand-write a metadata block unless a skill redirects it. M5 closes that gap.
- **Open risk M5 closes:** [definition-of-ready.md](definition-of-ready.md)'s
  risk register parks "cross-host portability … paths embedded in skill files
  diverge from per-host install paths" explicitly for this milestone. M5
  addresses it by keeping the committed artifact host-agnostic and making the
  host-specific path a documented install step (see OQ2 and the milestone
  Decisions).

## Files to Create / Modify

| File | Action | Phase | Notes |
|---|---|---|---|
| `skills/docs/SKILL.md` | Create | 1, 5, 6, 7 | Stub frontmatter + body (P1); finalised `description` (P5); the verb-redirecting body (P6); any bundled reference + final edges (P7). |
| `docs/m5-claude-code-skill.md` | Create | 1 | This milestone's task plan. |
| `docs/m5-claude-code-skill-log.md` | Create | 1 | This log. |
| `tests/test_skill.py` | Create | 1, 2 | Check signatures (P1); structural checks implemented (P2). |
| `docs/cli.md` | Modify | 1, 7 | "Using `docs` from a Claude Code skill" pointer subsection; `Updated` bumped. |
| `docs/architecture.md` | Modify | 1, 7 | `skill` artifact note in the Shape/module list; the `skills/docs/` install note; `Updated` bumped. |
| `docs/status.md` | Modify | 1, …, 10 | M5 phase tracking; M5 → Complete + project v1-complete at Phase 10. |
| `docs/plan.md` | Modify | 10 | Optional one-line v1-completion note (M5 opens no open question — see OQ3). |
| `docs/INDEX.md` | Regenerate | 1, 10 | Picks up the two new M5 docs (P1); the log's description bump (P10). |
| `tests/fixtures/expected/docs-INDEX.md` | Modify | 1, 10 | Re-synced with `docs/INDEX.md` in lockstep. |

## Trigger-scenario checklist

_Authored at Phase 2; the behavioural half of the RED/GREEN oracle (see the
milestone Decisions and OQ1). It is **RED now** — no skill body satisfies it
yet; it is walked at the Phase 9 dogfood pass against the authored
`skills/docs/SKILL.md`. Each row: a scenario, whether the skill's
`description` should trigger, and the `docs` verb (or "no trigger") the body
should redirect to. Eight positive rows — one per `docs` verb — and three
negative rows that exercise the "must not over-trigger" scoping._

| # | Scenario | Should trigger? | Expected redirect |
|---|---|---|---|
| 1 | Agent is asked to create a new plan / spec / charter / milestone doc in a `docs`-managed tree. | Yes | `docs new <role> <slug>` — scaffold with a correct metadata block; do not hand-write the block. |
| 2 | Agent is about to append a bullet to a hand-curated `INDEX.md`, or has edited a doc body and the INDEX is stale. | Yes | `docs index` — regenerate the marker block; never hand-edit `INDEX.md`. |
| 3 | Agent is asked to archive a finished milestone / completed plan doc. | Yes | `docs archive <file>` — sets `Status: archived`, moves into `archive/<date>/`, reindexes; never hand-move into `archive/`. |
| 4 | Agent is asked to rename or relocate a doc within the tree. | Yes | `docs mv <old> <new>` — moves and rewrites every `Related:` reference tree-wide; do not hand-edit references. |
| 5 | Agent is asked which docs exist, or to list docs by status / role / project / staleness. | Yes | `docs list [--status …] [--role …] [--project …] [--stale N] [--json]`. |
| 6 | Agent has edited a doc's body and needs to record the change date. | Yes | `docs touch <file>` — bumps `Updated:` to today and reindexes; do not hand-edit the date. |
| 7 | Agent wants to confirm the tree is convention-clean (e.g. before a commit, or in CI). | Yes | `docs check [DIR]` — reports violations with exit 0/1/2; read the exit code. |
| 8 | Agent is asked to adopt a foreign / non-conforming directory of Markdown into the convention. | Yes | `docs migrate <dir>` — dry-run plan by default; `--apply` writes the metadata blocks. |
| 9 | Agent edits a `README.md` in a repo that has **no `.docs.toml`** anywhere up the tree. | No | No trigger — the skill is scoped to `docs`-managed trees only. |
| 10 | Agent makes a pure prose edit (wording, a typo fix) to a doc body with no metadata, INDEX, or lifecycle concern. | No | No trigger — no `docs` verb applies to a prose-only edit. |
| 11 | Agent edits a code or config file (`.py`, `.toml`, `.json`) — not Markdown documentation. | No | No trigger — the skill governs documentation work, not code or config edits. |

## Phase logs

_Phase logs are appended here as each phase completes — one `### Phase N`
section per phase, following the M1–M4 log format (Objective, Files changed,
Actions taken, Issues / decisions, Exit criteria)._

### Phase 1 — Define Contract

**Completed:** 2026-05-22

#### Objective

Declare the M5 surface — the skill artifact's *shape* — with no skill body
written. Create `skills/docs/SKILL.md` with valid, final-shaped frontmatter and
a deliberate stub body; create `tests/test_skill.py` with the eight structural
check signatures so the file collects; wire the skill into `cli.md` /
`architecture.md` and refresh `status.md`.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `skills/docs/SKILL.md` | Create | New `skills/docs/` directory with one file. Frontmatter final-shaped now — exactly two keys, `name` then `description`, in that order, `---`-fenced so Phase 2 tests fail on content not parse errors. `name: docs`; `description` is a placeholder carrying the literal token `TODO` (resolved OQ-A). Body is a deliberate TODO stub. |
| `tests/test_skill.py` | Create | The eight structural check signatures (bodies are `pytest.fail("Not implemented — Phase 2")` placeholders) plus a header docstring explaining the two-part oracle. Module constants `REPO_ROOT` / `SKILL_DIR` / `SKILL_MD`; `from docs import _build_parser` via conftest's module registration. |
| `docs/cli.md` | Modify | New `## Using docs from a Claude Code skill` subsection before "What's deliberately not in v1", pointing at `skills/docs/SKILL.md`; `m5-claude-code-skill.md` added to `Related:`. |
| `docs/architecture.md` | Modify | "Sibling artifact" note after the module tree (the skill is **not** a `bin/docs` module); install note in "Install (end users)" — `skills/docs/` symlinked into `~/.claude/skills/docs/` parallel to the `bin/docs` symlink; `m5-claude-code-skill.md` added to `Related:`. |
| `docs/status.md` | Modify | "M5 in flight" paragraph refreshed — phases 1-4 underway on `m5/phases-1-4`. |
| `docs/m5-claude-code-skill-log.md` | Modify | Phase 1 row → Complete; this log entry. |
| `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Re-synced in lockstep via `./bin/docs index --root docs/` after the spec edits. |

#### Actions taken

- Created `skills/docs/SKILL.md`. The frontmatter is **final-shaped at Phase 1**
  — exactly `name` then `description`, `---`-fenced — so the Phase 2
  shape-checks fail (or pass) on *content*, never on a parse error. The
  `description` value carries the literal token `TODO`, and the body opens with
  `TODO`, by design (resolved OQ-A): the `"TODO" not in ...` content checks are
  the RED driver and give both the frontmatter and the body a genuine
  RED→GREEN arc — RED at Phase 4, GREEN once Phases 5/6 author the real text.
- Created `tests/test_skill.py` with eight check signatures collecting cleanly
  (mirrors the M4 Phase 1 `pytest.fail(... Phase 2)` pattern). The eighth,
  `test_frontmatter_parser_rejects_extra_keys`, exists so Phase 2's parser
  check is provably non-vacuous.
- `cli.md` gained the skill-pointer subsection; `architecture.md` gained the
  sibling-artifact note and the install step; `status.md`'s M5 paragraph now
  states phases 1-4 are underway.
- Regenerated `docs/INDEX.md` with `./bin/docs index --root docs/` and copied
  it onto `tests/fixtures/expected/docs-INDEX.md`. `skills/` is outside the
  `docs/` root, so the skill files never enter `INDEX.md` — only the `cli.md` /
  `architecture.md` / `status.md` body edits are reflected.

#### Issues / decisions

- **Decision (OQ-A) — the stub `description` and body carry the literal token
  `TODO`.** Operator-binding. Rather than a body that is merely short, the
  Phase-1 stub *names itself* a stub with the `TODO` token, and Phase 2's
  `test_name_and_description_values_are_sane` / `test_body_is_present_and_
  within_size_budget` assert `"TODO" not in ...`. This gives the content half
  of the oracle a real RED→GREEN transition instead of a vacuous pass.
- **`_build_parser` import kept clean under `ruff`.** The plan specifies
  `from docs import _build_parser` as a Phase-1 module-level import (Phase 2
  derives the real verb set from it). At Phase 1 nothing uses it yet, so a
  bare import trips `ruff` F401. The import is kept and pinned with an
  `assert _build_parser is not None` inside the still-stubbed
  `test_every_named_verb_is_a_real_subcommand` body — the conftest module-load
  contract is exercised at Phase 1 and `ruff` stays clean. Phase 2 replaces
  the assert with the real verb-extraction logic.
- **`Updated:` fields not bumped past 2026-05-22.** `cli.md`,
  `architecture.md`, and `status.md` already carried `Updated: 2026-05-22`
  (today) from the milestone-setup commit, so the Phase-1 body edits need no
  date bump — the convention is already satisfied.

#### Exit criteria

- [x] `skills/docs/SKILL.md` exists with parseable `---`-fenced frontmatter and
      a deliberate stub body.
- [x] `tests/test_skill.py` collects — 8 tests, no `ImportError`.
- [x] `ruff check` / `ruff format --check` / `mypy` clean tree-wide.
- [x] `docs/INDEX.md` and the dogfood snapshot regenerated in lockstep.
- [x] `./bin/docs check docs/` exit 0.
- [x] Ready for Phase 2 to implement the eight structural checks.

### Phase 2 — Write Tests (RED)

**Completed:** 2026-05-22

#### Objective

Express every M5 requirement as a failing check — both the automatable
structural half (`tests/test_skill.py`) and the behavioural half (the
trigger-scenario checklist). No skill body authored: the checks must fail on
*content* (the stub body, the `TODO` tokens, zero verbs named), never on an
`ImportError` or a `FileNotFoundError`.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `tests/test_skill.py` | Modify | The eight `pytest.fail(... Phase 2)` placeholders replaced with real check bodies. Module helpers added: `_read_skill()`, `_split_frontmatter()` (enforces the `---` fence), `_parse_frontmatter()` (the flat `key: value` splitter). |
| `docs/m5-claude-code-skill-log.md` | Modify | Trigger-scenario checklist placeholder replaced with the real 11-row table (8 positive + 3 negative); Phase 2 row → Complete; this log entry. |

#### The eight structural checks

1. `test_skill_md_exists_and_has_frontmatter` — `SKILL.md` exists, starts with
   a `---\n` fence, and has a closing `---` line.
2. `test_frontmatter_has_exactly_name_and_description` — the parsed key set is
   exactly `{name, description}`, in that order.
3. `test_name_and_description_values_are_sane` — `name == "docs"`;
   `description` is a non-empty string, carries no `TODO`, and is 20..1024
   characters.
4. `test_body_is_present_and_within_size_budget` — the body is non-empty,
   ≤ 500 lines, and carries no `TODO`.
5. `test_every_named_verb_is_a_real_subcommand` — derives the real verb set
   from `_build_parser()` (the `argparse._SubParsersAction` with
   `dest == "command"`), extracts verb candidates from `` `docs <verb>` ``
   inline-code spans, asserts every one is real and that ≥ 5 distinct real
   verbs are named.
6. `test_every_relative_link_resolves` — every `](target)` markdown link that
   is repo-relative (not `http`/`https`/`mailto`/absolute) resolves to a file
   under `skills/docs/`.
7. `test_skill_dir_has_no_clutter` — an ALLOWLIST: `skills/docs/` may contain
   only `SKILL.md` and an optional `references/` directory.
8. `test_frontmatter_parser_rejects_extra_keys` — feeds the parse helpers a
   fence-less string and a three-key frontmatter and asserts both are
   rejected, so checks #1/#2 are provably non-vacuous.

#### Issues / decisions

- **No `pyyaml` — a hand-rolled splitter.** The repo is stdlib-only
  (`pyproject.toml` declares no runtime dependencies). The skill frontmatter
  is exactly two flat `key: value` lines, so `_split_frontmatter`
  (fence-enforcing) + `_parse_frontmatter` (a first-`:` splitter) are enough.
  Adding a YAML dependency for two lines would violate the project's
  stdlib-only stance.
- **Decision record — OQ-A (`TODO` token as the RED driver).** Checks #3 and
  #4 assert `"TODO" not in ...` for the `description` and the body. The
  Phase-1 stub deliberately carries the `TODO` token in both, so these two
  checks have a genuine RED→GREEN arc: RED now, GREEN once Phases 5/6 author
  the real text. This is the operator-binding OQ-A decision.
- **OQ-B — link check governs only repo-internal links.** The skill body
  (authored at Phase 6) references cross-tree specs (`convention.md`,
  `cli.md`, …) **by name as inline code, not as markdown links**, because the
  committed artifact must be host-agnostic with no host-specific path
  (resolved OQ2). So `test_every_relative_link_resolves` governs only
  genuinely repo-internal links — likely none, or a link into a bundled
  `skills/docs/references/`. **The Step 2 Phase-6 author must honour this:
  write spec references as plain inline code, never as `](…)` links.**
- **OQ-C — verb-extraction regex contract.** `test_every_named_verb_is_a_real_
  subcommand` extracts verb candidates **only** from backtick-delimited inline
  code spans matching `` `docs <verb>` `` (verb = `[a-z-]+`); bare prose
  mentions of a verb are ignored. **The Step 2 Phase-6 author must write every
  `docs` verb the body names as inline code** (e.g. `` `docs index` ``), or
  the ≥ 5-real-verbs non-emptiness guard will not be satisfied.
- **`_build_parser` introspection.** The real verb set is read from the
  `argparse._SubParsersAction` in `parser._actions` whose `dest` is
  `"command"`, then `.choices.keys()`. This couples the test to the one
  source of truth — if `bin/docs` adds, renames, or removes a verb, the check
  catches a skill that has drifted out of sync.

#### RED baseline (captured here; re-run and fully attributed at Phase 4)

`pytest tests/test_skill.py -v` → **3 failed, 5 passed**. Every failure is a
CONTENT failure against the Phase-1 stub:

| Check | State | Reason |
|---|---|---|
| 1 `..._exists_and_has_frontmatter` | PASS | Frontmatter final-shaped at Phase 1 — a legitimate pass. |
| 2 `..._has_exactly_name_and_description` | PASS | Exactly `name` + `description`, in order — legitimate. |
| 3 `..._values_are_sane` | **FAIL** | `description still carries the Phase-1 TODO placeholder`. |
| 4 `..._within_size_budget` | **FAIL** | `skill body still carries the Phase-1 TODO stub`. |
| 5 `..._is_a_real_subcommand` | **FAIL** | `skill body names only 0 real verbs (expected >= 5)`. |
| 6 `..._relative_link_resolves` | PASS | The stub body has no relative links — vacuously legitimate. |
| 7 `..._has_no_clutter` | PASS | `skills/docs/` holds only `SKILL.md` — legitimate. |
| 8 `..._parser_rejects_extra_keys` | PASS | Tests the parser against inline strings — independent of the stub. |

The five passes are **honest** — the frontmatter is final-shaped and the
directory is clean from Phase 1 by design. The three failures are the content
half of the oracle and turn GREEN once Phases 5/6 author the real
`description` and body. No failure is an `ImportError` or path error.

#### Trigger-scenario checklist — RED

The 11-row checklist above is the behavioural half of the oracle. It is **RED
now**: no skill body exists to satisfy any row. It is walked at the Phase 9
dogfood pass. Eight positive rows map one-to-one onto the eight `docs` verbs
(`new`, `index`, `archive`, `mv`, `list`, `touch`, `check`, `migrate`); three
negative rows exercise the "must not over-trigger" scoping — a `README` in a
non-`docs` repo, a prose-only body edit, and a code/config file edit.

#### Exit criteria

- [x] `tests/test_skill.py` — the eight checks implemented; the content-driven
      checks (#3, #4, #5) FAIL for the right reason (stub body / `TODO` /
      zero verbs), not `ImportError` / `FileNotFoundError`.
- [x] The shape and clutter checks (#1, #2, #6, #7, #8) legitimately PASS —
      documented above so the baseline is honest.
- [x] `ruff check` / `ruff format --check` / `mypy` clean tree-wide.
- [x] The 11-row trigger-scenario checklist written into this log and RED.
- [x] Ready for Phase 3 (verify Phase-2 inputs) → Phase 4 (RED baseline).

## Milestone-completion summary

_Appended at Phase 10 when M5 — and the v1 roadmap — is complete._
