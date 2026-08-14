# M5 — Implementation Log

Lifecycle: archived
Role: log
Project: docs
Updated: 2026-08-14

Related:
- child-of: archive/2026-05-23/m5-claude-code-skill.md
- pairs-with: status.md

Revision:
- 2026-08-14: M27 one-time body-link migration; body-link destinations repaired (destination tokens only)

## Implementation metadata

- Project: docs
- Milestone: M5 — Claude Code skill
- Started: 2026-05-22
- Progress: **M5 complete — shipped 2026-05-22 across all ten TDD phases.** The
  milestone is the project's final v1 deliverable; **v1 is complete** (M1-M5 all
  shipped). All four milestone-setup OPEN QUESTIONS (OQ1-OQ4) and the Step-2
  author-guidance questions (OQ-A/-B/-C/-E/-F/-G/-H) are resolved and honoured
  in the authored artifact. The Claude Code skill is authored at
  `skills/docs/SKILL.md`; `tests/test_skill.py`'s eight structural checks are
  GREEN and the 11-row trigger-scenario checklist is walked and satisfied. See
  the Milestone-completion summary at the bottom of this log.

(Note: doc-lifecycle status is in the front-matter `Status:` field above. This
section tracks milestone progress, which is distinct.)

## Milestone-setup open questions — resolved (2026-05-22)

Four questions were surfaced while authoring the task plan; all four were
triaged against [plan.md](../../plan.md) and the M1–M4 precedent and operator-
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
   [plan.md](../../plan.md)'s `~/.claude/skills/docs/` path; no host collision
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
| 3. Create Data/Fixtures | Complete | 2026-05-22 | No new fixture tree — a conscious "nothing to stage". Structural checks read the real `SKILL.md` + `bin/docs`; the malformed-frontmatter samples are inline strings in `test_skill.py`. Every Phase-2 input verified to resolve. |
| 4. Run Tests (RED Baseline) | Complete | 2026-05-22 | `pytest tests/` — 3 failed / 241 passed (244 collected). The 3 content-driven `test_skill.py` checks RED against the stub body; M1–M4's 236 tests green; ruff/format/mypy clean; `docs check docs/` exit 0. Session pauses here. |
| 5. Update Base Interfaces | Complete | 2026-05-22 | `description:` authored as one physical line (OQ-E): names the action, the positive triggers, and the scoping limiter. Checks #1/#2/#3/#8 GREEN; #4/#5 still RED (body untouched). |
| 6. Implement Offline/Core Path | Complete | 2026-05-22 | Body authored — H1 + orientation, the never-hand-edit guardrail, binary/root location, a prose verb-redirection list (one sub-heading per verb), the prose-only-edit carve-out (OQ-H), and the convention pointer. 112 non-blank lines. All 8 `test_skill.py` checks GREEN. |
| 7. Update Tool/Wrapper Layer | Complete | 2026-05-22 | No `references/` added — the 143-line body is well under the 250-line trigger. Verification pass: `architecture.md`'s skill/install note and `cli.md`'s skill subsection re-read and confirmed accurate against the authored body — no reconciliation needed. `skills/docs/` holds only `SKILL.md`; check #7 GREEN. |
| 8. Run Tests (GREEN) | Complete | 2026-05-22 | Full GREEN gate: `pytest tests/` → 244 passed (236 M1-M4 + 8 M5); `ruff check` / `ruff format --check` / `mypy` clean tree-wide; `docs check docs/` exit 0; `docs index --root docs/ --dry-run` idempotent, exit 0. |
| 9. Implement Online/Integration | Complete | 2026-05-22 | Dogfood: all 11 trigger-checklist rows walked against the authored `SKILL.md` — 8 positive rows trigger and redirect to the right verb; 3 negative rows handled correctly (row 10 annotated per OQ-H). `docs index --root docs/` regenerated `INDEX.md` (no diff); `docs check docs/` exit 0. |
| 10. Quality, Docs, Refactor | Complete | 2026-05-22 | Closed out M5 and v1: `status.md` → M5 Complete + project v1-complete; `definition-of-ready.md` risk annotated resolved; `plan.md` v1-completion note; completion summaries appended; all Phase Checklist / Deliverables / Success Criteria boxes ticked; `INDEX.md` + snapshot regenerated; full gate green. |

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
  already shipped, specified in [cli.md](../../cli.md), and tested.
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
- **Open risk M5 closes:** [definition-of-ready.md](../../definition-of-ready.md)'s
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
| 10 | Agent makes a pure prose edit (wording, a typo fix) to a doc body with no metadata, INDEX, or lifecycle concern. | No verb | The `description` may load the skill — the file is in a `.docs.toml`-marked tree and a `description` cannot discriminate edit-intent before loading (resolved OQ-H). The body then correctly redirects to **no `docs` verb**: its prose-only carve-out tells the agent a prose edit not touching metadata / `INDEX.md` / archiving / lifecycle needs no verb — proceed normally. The skill is harmless on this row, not triggering-and-misredirecting. |
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
   ≤ 500 lines, carries no `TODO`, has **≥ 40 non-blank lines** (a genuine
   lower bound so a one-line stub cannot pass), and contains the
   **never-hand-edit guardrail language** (a case-insensitive `hand-edit` /
   `hand edit` phrase — M5's central instruction). _(Lower-bound and guardrail
   assertions added by the fresh-eyes review, 2026-05-22 — see finding 1.)_
5. `test_every_named_verb_is_a_real_subcommand` — derives the real verb set
   from `_build_parser()` (the `argparse._SubParsersAction` with
   `dest == "command"`), extracts verb candidates from `` `docs <verb>` ``
   inline-code spans, asserts every named verb is real **and that every one of
   the eight real verbs is named** (`real_verbs ⊆ named` — not merely "≥ 5
   distinct"). _(Completeness guard strengthened from "≥ 5" to "all eight" by
   the fresh-eyes review, 2026-05-22 — see finding 2.)_
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
  code spans matching `` `docs <verb>` `` (verb = `[a-z]+`); bare prose
  mentions of a verb are ignored. **The Step 2 Phase-6 author must write every
  `docs` verb the body names as inline code** (e.g. `` `docs index` ``), and
  **each verb must appear at least once as a PLAIN `` `docs <verb>` `` span
  with no global flag before the verb** — a span like `` `docs --root <dir>
  index` `` does not register `index` as named, because the regex anchors the
  verb immediately after `docs `. The completeness guard (`real_verbs ⊆
  named`) will not be satisfied otherwise. _(Fresh-eyes review, 2026-05-22 —
  finding 4: the verb class was tightened from `[a-z-]+` to `[a-z]+` so a
  span's `--root` flag can no longer be captured as a bogus verb; all eight
  real verbs are plain lowercase with no hyphen.)_
- **OQ-E — the frontmatter `description` is a single physical line.** The
  hand-rolled `_parse_frontmatter` splits the fenced frontmatter on physical
  newlines and treats each non-blank line as its own `key: value` pair: it
  cannot parse a YAML-folded (`>-` / `|`) or wrapped multi-line `description`.
  Resolution (fresh-eyes review, 2026-05-22 — finding 3; operator-binding):
  do **not** harden the parser — instead constrain the artifact. **The Step 2
  Phase-5 author must write `description:` as exactly one physical line — no
  YAML folding, no continuation lines.** This is behaviour-neutral (a long
  one-physical-line description is valid YAML and valid for Claude Code) and is
  the same author-guidance shape as OQ-B/OQ-C. Recorded as a Decision in
  [m5-claude-code-skill.md](m5-claude-code-skill.md).
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
| 4 `..._within_size_budget` | **FAIL** | `skill body still carries the Phase-1 TODO stub` (the `TODO` check is first; the new ≥ 40 non-blank-line floor would also fail — the 3-line stub is far under it). |
| 5 `..._is_a_real_subcommand` | **FAIL** | `skill body fails to name every real docs verb — missing all eight` (the stub names zero verbs). |
| 6 `..._relative_link_resolves` | PASS | The stub body has no relative links — vacuously legitimate. |
| 7 `..._has_no_clutter` | PASS | `skills/docs/` holds only `SKILL.md` — legitimate. |
| 8 `..._parser_rejects_extra_keys` | PASS | Tests the parser against inline strings — independent of the stub. |

_Note (fresh-eyes review, 2026-05-22): checks #4 and #5 were strengthened
after this table was first written. #4 gained a ≥ 40 non-blank-line floor and
a never-hand-edit guardrail-phrase assertion (findings 1a/1b); #5's
completeness guard moved from "≥ 5 distinct verbs" to "all eight real verbs
named" (finding 2). The strengthened assertions live inside the already-RED
checks #4 and #5 — the 3-RED/5-GREEN split is unchanged, and the failures
remain content `AssertionError`s against the stub. (The guardrail-phrase
assertion happens to be satisfied by the stub, whose TODO text mentions "the
never-hand-edit guardrail" — #4 still fails RED via the `TODO` check and the
line floor; the guardrail assertion is a contract pin for the GREEN side.)_

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

### Phase 3 — Create Data/Fixtures

**Completed:** 2026-05-22

#### Objective

Provide whatever fixture the structural checks need — and, for an artifact
milestone, consciously record that there is nothing to stage (resolved OQ1).
**No file changes except this log entry.**

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/m5-claude-code-skill-log.md` | Modify | Phase 3 row → Complete; this log entry. **No other file changed.** |

#### Why there is nothing to stage

M1–M4 each staged a synthetic `tests/fixtures/trees/` directory because each
milestone's tests walked a sample docs tree. M5's structural checks have no
such input:

- **The artifact under test is real.** `tests/test_skill.py` reads the real
  `skills/docs/SKILL.md` — the very file the milestone authors. There is no
  synthetic copy to stage.
- **The verb set is real.** Check #5 derives the real verb list from
  `_build_parser()` in `bin/docs` via `conftest.py`'s module registration —
  no fixture parser.
- **The malformed-frontmatter samples are inline.** Check #8 proves the
  parser is non-vacuous by feeding it a fence-less string and a three-key
  frontmatter — both are tiny inline string literals in `test_skill.py`, not
  files. A `tests/fixtures/` directory for two short strings would be
  overkill (recorded in the milestone Decisions as "No new
  `tests/fixtures/trees/` directory").
- **The dogfood input is this repo's own `docs/`.** The Phase 9 dogfood walks
  the live `docs/` tree — already present, not a fixture.

#### Verification — every Phase-2 input resolves

- `skills/docs/SKILL.md` exists (created at Phase 1).
- `from docs import _build_parser` succeeds via `conftest.py`'s `importlib`
  module load — confirmed importable.
- `skills/docs/` contains only `SKILL.md` — the no-clutter check's allowlist
  input is in the expected state.
- No `tests/fixtures/` addition is required or made.

#### Issues / decisions

- **Phase 3 is a conscious "nothing to stage", not a skipped phase.** Per the
  resolved OQ1 mapping, no M5 phase is marked N/A. Phase 3 genuinely shrinks
  for an artifact milestone — there is no foreign data to stage — and that
  outcome is recorded deliberately here rather than silently omitted.

#### Exit criteria

- [x] Every input a Phase-2 check references is available and resolves.
- [x] No new fixture tree was needed — recorded as a deliberate, documented
      difference from M1–M4.
- [x] Ready for Phase 4: run the suite and capture the RED baseline.

### Phase 4 — Run Tests (RED Baseline)

**Completed:** 2026-05-22

#### Objective

Run the full quality gate and confirm every `tests/test_skill.py` failure
traces to the *unwritten skill body* — not to an `ImportError`, a missing
file, or a misconfiguration. Log-only; no skill body authored. **This session
(Step 1, phases 1–4) pauses here.**

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/m5-claude-code-skill-log.md` | Modify | Phase 4 row → Complete; this log entry. **No other file changed.** |

#### Captured command output

_Re-captured 2026-05-22 after the fresh-eyes review strengthened checks #4 and
#5 (see "Fresh-eyes review" below); the baseline is unchanged — still
3-RED / 5-GREEN._

```
$ .venv/bin/python -m pytest tests/ -q
...
FAILED tests/test_skill.py::test_name_and_description_values_are_sane
FAILED tests/test_skill.py::test_body_is_present_and_within_size_budget
FAILED tests/test_skill.py::test_every_named_verb_is_a_real_subcommand
3 failed, 241 passed in ~3.5s

$ .venv/bin/ruff check .
All checks passed!

$ .venv/bin/ruff format --check .
19 files already formatted

$ .venv/bin/mypy
Success: no issues found in 19 source files

$ ./bin/docs check docs/
docs: no violations found          # exit 0
```

244 tests collected (236 M1–M4 + 8 new M5 structural checks); no collection /
import / fixture-path errors. Run in isolation, M1–M4's suite is **236
passed** — confirming the new file adds 8 and breaks none.

#### Per-check RED / GREEN breakdown

The plan calls for an honest baseline: an artifact-shape milestone has some
checks that are *already* green at Phase 4 by design (the frontmatter was
authored final-shaped at Phase 1; `skills/docs/` has only `SKILL.md`). Each
of the eight checks, with its Phase-4 state and why:

| # | Check | State | Why |
|---|---|---|---|
| 1 | `test_skill_md_exists_and_has_frontmatter` | **GREEN** | The Phase-1 stub has a valid `---`-fenced frontmatter — final-shaped on purpose so Phase 2 fails on content, not parse errors. A legitimate, intended pass. |
| 2 | `test_frontmatter_has_exactly_name_and_description` | **GREEN** | The stub frontmatter carries exactly `name` then `description` — the final shape. Legitimate pass. |
| 3 | `test_name_and_description_values_are_sane` | **RED** | `AssertionError: description still carries the Phase-1 TODO placeholder` — the stub `description` carries the `TODO` token by design (OQ-A). Turns GREEN at Phase 5. |
| 4 | `test_body_is_present_and_within_size_budget` | **RED** | `AssertionError: skill body still carries the Phase-1 TODO stub` — the stub body carries the `TODO` token by design (OQ-A); the strengthened ≥ 40 non-blank-line floor (finding 1a) would also fail (the stub has 3 non-blank lines). Turns GREEN at Phase 6. |
| 5 | `test_every_named_verb_is_a_real_subcommand` | **RED** | `AssertionError: skill body fails to name every real docs verb — missing ['archive', 'check', 'index', 'list', 'migrate', 'mv', 'new', 'touch']` — the stub body names no `docs` verbs; the strengthened guard (finding 2) now requires all eight real verbs to be named. Turns GREEN at Phase 6. |
| 6 | `test_every_relative_link_resolves` | **GREEN** | The stub body has no markdown links — the check is vacuously satisfied. It is a *guard* that only bites once a body with links exists; honest to report it green now. |
| 7 | `test_skill_dir_has_no_clutter` | **GREEN** | `skills/docs/` holds only `SKILL.md` (Phase 1 created nothing else). Legitimate pass; bites only if Phase 7 adds a stray file. |
| 8 | `test_frontmatter_parser_rejects_extra_keys` | **GREEN** | Tests the parse helpers against inline strings, independent of the artifact. Proves checks #1/#2 are non-vacuous; correctly green from the moment the helpers exist. |

**RED: 3 checks (#3, #4, #5)** — every one a *content* `AssertionError`
against the stub body / the `TODO` tokens. **GREEN: 5 checks (#1, #2, #6, #7,
#8)** — every one a legitimate, intended pass, not a false pass. This is the
honest baseline: the milestone deliberately authored the frontmatter shape
and the clean directory at Phase 1, so the structural-shape half of the oracle
is green from the start; the *content* half (real `description`, real body,
real verbs) is the RED→GREEN arc Phases 5–6 will drive.

#### Failure attribution

No failure is an `ImportError`, a `FileNotFoundError`, or a path/collection
error. All three are `AssertionError`s raised inside the check bodies:

| Check | Failure | Turns GREEN in |
|---|---|---|
| `test_name_and_description_values_are_sane` | `description still carries the Phase-1 TODO placeholder` | Phase 5 (author the `description`). |
| `test_body_is_present_and_within_size_budget` | `skill body still carries the Phase-1 TODO stub` (and the strengthened ≥ 40 non-blank-line floor) | Phase 6 (author the body). |
| `test_every_named_verb_is_a_real_subcommand` | `skill body fails to name every real docs verb — missing all eight` | Phase 6 (the body names all eight verbs as plain `docs <verb>` inline code). |

#### Trigger-scenario checklist — still RED

The 11-row behavioural checklist stands fully unsatisfied: no skill body
exists, so no row's redirect can be confirmed. It is walked at the Phase 9
dogfood pass.

#### Issues / decisions

- **Five checks are legitimately GREEN at the RED baseline — and that is
  correct.** Unlike an M1–M4 code milestone (where every new test fails
  against a `NotImplementedError` stub), an artifact-shape milestone authors
  the artifact's *shape* at Phase 1. The frontmatter is final-shaped and the
  directory is clean from Phase 1, so the shape/clutter checks pass
  immediately. The plan explicitly anticipates this ("frontmatter-shape and
  no-clutter checks may legitimately PASS … document which checks are RED vs
  already-GREEN explicitly so the baseline is honest"). The RED→GREEN arc
  lives in the three *content* checks.
- **Every RED failure is a content `AssertionError`.** The deliberate `TODO`
  tokens (OQ-A) and the verb-free stub body are what fail checks #3/#4/#5 —
  exactly the intended drivers. Nothing fails for a structural/import reason.

#### Fresh-eyes review (2026-05-22) — structural oracle strengthened

A fresh-eyes review of Step 1 (phases 1–4) returned five findings; four were
applied to `tests/test_skill.py` before this step was finalised. The phase-2
tests are not yet frozen by a GREEN run, so strengthening them now is correct —
Step 2 authors the skill body against these tests, so they must genuinely pin
the contract. The strengthened assertions live **inside the already-RED checks
#4 and #5** — the baseline remains 3-RED / 5-GREEN and was re-run and
re-verified honest (every failure a content `AssertionError`, no `ImportError`
/ `FileNotFoundError`):

- **Finding 1 (check #4) — body lower bound + guardrail.** Added a ≥ 40
  non-blank-line floor (a one-line body can no longer pass) and an assertion
  that the never-hand-edit guardrail language is present (case-insensitive
  `hand-edit` / `hand edit`). The 3-line stub fails the floor; #4 stays RED.
- **Finding 2 (check #5) — all eight verbs.** The completeness guard moved
  from "≥ 5 distinct real verbs" to `real_verbs ⊆ named` — every one of the
  eight real verbs must be named in the body. The verb-free stub names zero,
  so #5 stays RED with a clearer "missing all eight" message.
- **Finding 3 — single-physical-line `description` (OQ-E).** The hand-rolled
  `_parse_frontmatter` cannot handle a YAML-folded / wrapped `description`.
  Resolution: do not harden the parser; record OQ-E (the `description` must be
  one physical line) as a binding author-guidance Decision in the milestone
  doc and this log's Phase-2 entry. Behaviour-neutral; no code change.
- **Finding 4 (check #5) — verb-extraction regex.** The verb class was
  tightened from `[a-z-]+` to `[a-z]+`, eliminating a false capture of a
  `--root` flag in a span like `` `docs --root <dir> index` ``. The OQ-C
  author-guidance note (Phase-2 log) was extended: each verb must appear at
  least once as a plain `` `docs <verb>` `` span with no global flag first.
- **Finding 5 — `test_every_relative_link_resolves` is vacuous.** No change
  (conductor decision): a defensible consequence of resolved OQ-B; the check
  regains teeth if a `references/` file is added in Step 2. Disclosed honestly
  in the Phase-4 per-check table above.

The operator also confirmed `status.md`'s "Commit once per TDD phase on
`main`" line is left unchanged — it predates M5 and is out of M5's scope.

#### Exit criteria

- [x] `pytest tests/` — 3 failed / 241 passed (244 collected); the 3 failures
      are the content-driven `test_skill.py` checks.
- [x] Every failure is a CONTENT `AssertionError` against the stub body —
      no `ImportError`, no `FileNotFoundError`, no collection error.
- [x] M1–M4's 236 tests stay green (verified in isolation).
- [x] `ruff check` / `ruff format --check` / `mypy` clean tree-wide.
- [x] `./bin/docs check docs/` exit 0.
- [x] Per-check RED/GREEN breakdown recorded — the baseline is honest.
- [x] The trigger-scenario checklist stands fully RED.
- [x] **Step 1 (phases 1–4) complete. The session pauses here — no skill body
      authored; no Phase 5+ work.**

### Phase 5 — Update Base Interfaces

**Completed:** 2026-05-22

#### Objective

Author the skill's *frontmatter* — the trigger surface. Replace the Phase-1
`TODO` placeholder `description:` line with the finalised, trigger-scoped
description. `name: docs` and the `---` fences are left as Phase 1 shaped them;
the body stub is left for Phase 6.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `skills/docs/SKILL.md` | Modify | The `description:` line only — Phase-1 `TODO` placeholder replaced with the finalised description. `name: docs`, the `---` fences, and the body stub untouched. |
| `docs/m5-claude-code-skill-log.md` | Modify | Phase 5 row → Complete; this log entry. |

#### Actions taken

- Authored the `description` as **exactly one physical line** (resolved OQ-E —
  the hand-rolled `_parse_frontmatter` cannot parse a YAML-folded or wrapped
  value). The line names: the **action** (use the `docs` CLI / run the verb
  instead of hand-editing); the **positive triggers** (creating a
  plan/spec/charter/milestone, archiving or renaming a doc, listing docs,
  checking the tree, regenerating `INDEX.md`, adopting a foreign Markdown
  directory; never hand-editing metadata, `INDEX.md`, or `archive/`); and the
  **scoping limiter** — "a docs-managed tree (a directory with a `.docs.toml`
  file)" with the closing clause "Not for Markdown outside a docs-managed
  tree". The limiter keeps the skill from over-triggering on unrelated
  Markdown (the trigger checklist's negative rows 9 and 11).
- ~330 characters, well inside the 20..1024 sane window check #3 enforces.

#### Issues / decisions

- **OQ-E honoured.** The `description` is one physical line — no `>-` / `|`
  folding, no continuation lines — so the stdlib-only `_parse_frontmatter`
  parses it as a single `key: value` pair.
- **Body stub left intact.** Phase 5 is scoped to the frontmatter only. The
  body's `TODO` token remains; checks #4/#5 stay RED until Phase 6.

#### Exit criteria

- [x] `description:` is one physical line, no `TODO`, names the action +
      triggers + scoping limiter.
- [x] Checks #1/#2/#3/#8 GREEN; #4/#5 still RED (body untouched).
- [x] `pytest tests/test_skill.py` → 2 failed / 6 passed — the two failures
      are the body-driven checks #4/#5.
- [x] Ready for Phase 6 to author the body.

### Phase 6 — Implement Offline/Core Path

**Completed:** 2026-05-22

#### Objective

Author the skill *body* — the verb-redirecting instructions. Replace the
Phase-1 three-line `TODO` stub (everything after the closing `---`) with the
real body: the never-hand-edit guardrail, binary/root location guidance, a
per-verb redirection section, and a pointer to the convention. Drive all eight
`test_skill.py` checks GREEN.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `skills/docs/SKILL.md` | Modify | The body — everything after the closing `---` — replaced with the authored verb-redirecting body (143 total lines, 112 non-blank). |
| `docs/m5-claude-code-skill-log.md` | Modify | Phase 6 row → Complete; this log entry. |

#### Body structure

1. **H1 + orientation paragraph** — defines a `docs`-managed tree and states the
   central guardrail up front: run the verb, do not hand-edit the
   machine-maintained parts.
2. **"Never hand-edit these — run the verb"** — the prominent guardrail section.
   Lists the three never-hand-edit things — `INDEX.md` (run `docs index`), a
   doc's location relative to `archive/` and its `Status:` line (run
   `docs archive`), a metadata block (run `docs new` to scaffold,
   `docs touch` to bump the date). Ends with the **OQ-H carve-out**: a
   prose-only edit that does not touch metadata / `INDEX.md` / archiving /
   lifecycle needs no verb — proceed normally.
3. **"Finding the binary and the root"** — host-agnostic: prefer an installed
   `docs` on `$PATH`, else `bin/docs` from the repo root; no absolute path is
   baked in. `docs` walks up for `.docs.toml`; `--root DIR` is explicit; no
   `.docs.toml` up-tree ⇒ not a docs-managed tree, the skill does not apply.
4. **"Which verb for which task"** — a **prose list with one sub-heading per
   verb** (resolved OQ-F — not a table). One `### ` entry per verb covering the
   trigger, the command, the flags that matter, and how to read the output. All
   eight verbs: `docs new`, `docs index`, `docs archive`, `docs mv`,
   `docs list`, `docs touch`, `docs check` (with the 0/1/2 exit-code reading),
   `docs migrate` (dry-run default, `--apply`). Each verb's first mention is a
   bare `` `docs <verb>` `` span — no flag before the verb (resolved OQ-C).
5. **"Where the convention itself lives"** — points at `convention.md` and
   `cli.md` **as inline code, never as markdown links** (resolved OQ-B);
   restates none of the convention grammar or vocabulary.

#### Issues / decisions

- **OQ-F honoured** — the verb-redirection section is a prose list, one `### `
  sub-heading per verb, not a markdown table.
- **OQ-C honoured** — every verb appears as a plain `` `docs <verb>` `` span
  with no global flag between `docs` and the verb; flag examples put the flag
  after the verb (`docs index --root DIR`). The verb-extraction check captures
  exactly the eight real verbs and no non-verb.
- **OQ-B honoured** — `convention.md` and `cli.md` are referenced as inline
  code, not links; `test_every_relative_link_resolves` stays vacuously green.
- **OQ-H honoured** — the body explicitly tells the agent that a prose-only
  edit (typo, rewording, adding a paragraph) needs no `docs` verb — proceed
  normally — so the skill is harmless when it loads on an ordinary `.md` edit.
- **OQ-A honoured** — zero literal `TODO` tokens anywhere in the artifact.

#### Exit criteria

- [x] The body replaces the Phase-1 stub; 112 non-blank lines (over the 40
      floor, well under the 500 cap; inside the ~90-140 target).
- [x] All 8 `tests/test_skill.py` checks GREEN.
- [x] Full suite 244 passed; `ruff` / `ruff format` / `mypy` clean tree-wide;
      `./bin/docs check docs/` exit 0.
- [x] Ready for Phase 7 (verification pass).

### Phase 7 — Update Tool/Wrapper Layer

**Completed:** 2026-05-22

#### Objective

Finalise the artifact's edges: decide on a bundled `references/` file, verify
the install/doc wiring (`architecture.md`, `cli.md`) is accurate against the
authored body, and confirm the no-clutter check.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/m5-claude-code-skill-log.md` | Modify | Phase 7 row → Complete; this log entry. **No other file changed — a clean verification pass.** |

#### Actions taken

- **No `references/` cheat-sheet added.** The Phase-6 body is 143 lines total
  (112 non-blank) — well under the ~250-line threshold the plan set for
  splitting per-verb detail into `skills/docs/references/verbs.md`. A
  `references/verbs.md` would duplicate `cli.md` (skill-creator guidance:
  information lives in `SKILL.md` *or* references, not both). Phase 7 is
  therefore a verification pass, not an authoring pass.
- **`architecture.md` re-read** — the "Sibling artifact: the Claude Code skill"
  note and the "Install (end users)" `ln -s …/skills/docs ~/.claude/skills/docs`
  step (both authored at Phase 1). Confirmed accurate: the authored body is a
  standalone markdown artifact that drives the verbs, host-agnostic, installed
  by the documented symlink. No edit needed.
- **`cli.md` re-read** — the "Using `docs` from a Claude Code skill" subsection
  (authored at Phase 1). Confirmed accurate: it describes a markdown artifact
  whose body redirects an agent to the `docs` verbs specified in `cli.md`,
  adding no command surface. Matches the authored body. Per resolved OQ-G, no
  further `cli.md` content edit is owed. No edit needed.
- **No-clutter check** — `skills/docs/` holds only `SKILL.md`; check #7 GREEN.

#### Issues / decisions

- **No `references/` directory (plan-conditional decision taken).** The plan
  made `references/` conditional on the body overrunning ~250 lines. It did
  not — so none is added, and `test_every_relative_link_resolves` stays
  vacuously green (a defensible consequence of resolved OQ-B, disclosed at
  Phase 4).
- **No reconciliation owed (OQ-G).** The Phase-1 `cli.md` / `architecture.md`
  skill wiring is accurate against the authored body; Phase 7 verifies, it does
  not churn.

#### Exit criteria

- [x] No `references/` added — body well under the 250-line trigger.
- [x] `architecture.md` install note and `cli.md` skill subsection verified
      accurate; no reconciliation needed.
- [x] `skills/docs/` holds only `SKILL.md`; check #7 GREEN.
- [x] All 8 `tests/test_skill.py` checks GREEN; `ruff` / `ruff format` / `mypy`
      clean tree-wide.
- [x] Ready for Phase 8 (the GREEN gate run).

### Phase 8 — Run Tests (GREEN)

**Completed:** 2026-05-22

#### Objective

Run the full quality gate and confirm the suite is fully GREEN — the structural
half of M5's oracle satisfied, M1-M4 unbroken.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/m5-claude-code-skill-log.md` | Modify | Phase 8 row → Complete; this log entry. **No other file changed.** |

#### Captured command output

```
$ .venv/bin/python -m pytest tests/ -q
............................................................ [ ... ]
244 passed in ~3.4s

$ .venv/bin/ruff check .
All checks passed!

$ .venv/bin/ruff format --check .
19 files already formatted

$ .venv/bin/mypy
Success: no issues found in 19 source files

$ ./bin/docs check docs/
docs: no violations found            # exit 0

$ ./bin/docs index --root docs/ --dry-run
# docs — Documentation
... <!-- docs:generated start --> ... <!-- docs:generated end -->
                                     # exit 0 — idempotent
```

**244 passed** — exactly the expected count: 236 M1-M4 tests + 8 M5
`tests/test_skill.py` structural checks. All eight M5 checks GREEN. No M1-M4
regression. The three Phase-4 RED checks (#3 `description`, #4 body, #5 verbs)
are now GREEN against the authored frontmatter and body.

#### Issues / decisions

- **No artifact defect.** Every M5 check passed on the first Phase-8 run — the
  Phase-5/6 authoring satisfied the frozen oracle directly; no `SKILL.md` fix
  was needed and no test was touched.

#### Exit criteria

- [x] `pytest tests/` → 244 passed (236 M1-M4 + 8 M5).
- [x] `ruff check` / `ruff format --check` / `mypy` clean tree-wide.
- [x] `./bin/docs check docs/` exit 0; `docs index --root docs/ --dry-run`
      idempotent, exit 0.
- [x] All 8 `tests/test_skill.py` checks GREEN — the structural oracle
      satisfied.
- [x] Ready for Phase 9 (the dogfood / trigger-checklist walk).

### Phase 9 — Implement Online/Integration (dogfood pass)

**Completed:** 2026-05-22

#### Objective

Exercise the skill — the behavioural half of GREEN. Walk all 11 rows of the
trigger-scenario checklist against the authored `skills/docs/SKILL.md`: confirm
the `description` triggers (or correctly does not) and the body redirects to the
expected verb. Regenerate this repo's `INDEX.md` only via `docs index`; confirm
`docs check docs/` exits 0.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/m5-claude-code-skill-log.md` | Modify | Trigger-checklist row 10's expected-behavior cell annotated per resolved OQ-H; Phase 9 row → Complete; this log entry. |

#### Trigger-scenario checklist — walked, per-row verdict

The `description` (the always-in-context trigger surface) and the authored body
were walked row by row. **Verdict: 11/11 satisfied.**

| # | Type | Verdict | Why |
|---|---|---|---|
| 1 | positive | **PASS** | `description` names "creating a plan/spec/charter/milestone" → triggers. Body "Creating a doc — `docs new`": `docs new <role> <slug>`, `--project` / `--title`, scaffolds the metadata block, run `docs index` once filled. |
| 2 | positive | **PASS** | `description` names "regenerating INDEX.md" and "hand-editing … INDEX.md" → triggers. Body guardrail + "Regenerating the index — `docs index`": rewrites the marker block, idempotent, `--root` / `--dry-run`. |
| 3 | positive | **PASS** | `description` names "archiving … a doc" → triggers. Body "Archiving a doc — `docs archive`": sets `Status: archived`, moves into `archive/<date>/`, reindexes; `--reason` / `--date` / `--cascade`. |
| 4 | positive | **PASS** | `description` names "renaming a doc" → triggers. Body "Renaming or moving a doc — `docs mv`": moves and rewrites every `Related:` reference tree-wide. |
| 5 | positive | **PASS** | `description` names "listing docs" → triggers. Body "Listing docs — `docs list`": `--status` / `--role` / `--project` / `--stale N` / `--json`, AND-combined. |
| 6 | positive | **PASS** | `description` covers documentation work in a docs-managed tree and "hand-editing metadata" (`Updated:` is metadata) → triggers. Body guardrail ("Do not hand-edit the `Updated:` date") + "Recording an edit date — `docs touch`": bumps `Updated:`, reindexes. |
| 7 | positive | **PASS** | `description` names "checking the tree" → triggers. Body "Checking the tree — `docs check`": validates the tree, **read the exit code** — 0 clean / 1 warnings / 2 errors; `--json` / `--stale N`. |
| 8 | positive | **PASS** | `description` names "adopting a foreign Markdown directory" → triggers. Body "Adopting a foreign directory — `docs migrate`": dry-run plan by default, `--apply` writes, `--json`; refuses an existing docs root. |
| 9 | negative | **PASS** | A `README` in a repo with no `.docs.toml` up-tree: the `description`'s scoping — "a directory with a .docs.toml file" + the closing "Not for Markdown outside a docs-managed tree" — excludes it. No trigger. |
| 10 | negative | **PASS (annotated)** | A pure prose edit inside a `.docs.toml`-marked tree. Per resolved OQ-H, a `description` cannot discriminate edit-intent before loading, so the skill **may** load (the tree matches). The body then correctly redirects to **no verb**: its prose-only carve-out tells the agent that an edit not touching metadata / `INDEX.md` / archiving / lifecycle needs no `docs` verb — proceed normally. Scored honestly as "skill may load; body correctly redirects to no verb"; checklist row 10's expected-behavior cell was annotated to reflect this rather than silently marked a plain "no trigger" pass. |
| 11 | negative | **PASS** | A `.py` / `.toml` / `.json` edit: the `description` scopes to Markdown documentation work in a docs-managed tree; a code/config file is not Markdown documentation. No trigger. |

No row failed; no `SKILL.md` fix or re-run of Phase 8 was needed.

#### Exit-criterion behaviour confirmed

- `./bin/docs index --root docs/` regenerated `docs/INDEX.md` — `docs index` is
  the only thing that touched it; the regenerated file is byte-identical to the
  committed one (no diff — the Phase 5-9 log edits did not change any indexed
  doc's first paragraph or `Updated:` line).
- `./bin/docs check docs/` → `no violations found`, exit 0.

#### Issues / decisions

- **Row 10 annotated, not silently passed (OQ-H).** The checklist's row 10
  expected-behavior cell now states the honest outcome — the skill may load on
  an ordinary prose edit, and that is acceptable because the body redirects to
  no verb. The skill is *harmless* on this row, which is the design intent of
  the OQ-H carve-out.
- **The behavioural oracle is GREEN.** Together with the 8 GREEN structural
  checks (Phase 8), both halves of M5's two-part oracle (resolved OQ1) are now
  satisfied.

#### Exit criteria

- [x] All 11 trigger-checklist rows walked against the authored `SKILL.md`;
      11/11 satisfied — 8 positive trigger-and-redirect, 3 negative handled.
- [x] Row 10's expected-behavior cell annotated per resolved OQ-H.
- [x] `docs/INDEX.md` regenerated only via `docs index` — no hand edit.
- [x] `./bin/docs check docs/` exit 0.
- [x] Ready for Phase 10 (close out M5 and v1).

### Phase 10 — Quality, Docs, Refactor

**Completed:** 2026-05-22

#### Objective

Close out M5 — and the project. Run the full quality gate, update `status.md`
(M5 → Complete, project v1-complete), annotate `definition-of-ready.md`'s parked
risk as resolved, add a one-line v1-completion note to `plan.md`, append the
milestone-completion summaries, tick every checklist box, and regenerate
`docs/INDEX.md` + the snapshot in lockstep.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `docs/status.md` | Modify | "Current milestone" rewritten — M5 shipped, project v1-complete; milestone table row M5 → **Complete**; "Resuming this work" reading order / verify-environment / next-action refreshed for a v1-complete repo. |
| `docs/definition-of-ready.md` | Modify | The cross-host-portability risk row annotated **Resolved (M5)** — left as historical record; `Updated:` bumped via `docs touch`. |
| `docs/plan.md` | Modify | One-line v1-completion note under "Open questions" — all five milestones shipped; the parked extra-field allowlist question carries to v1.1; M5 opened no new plan-level question (OQ3). |
| `docs/m5-claude-code-skill.md` | Modify | Every Phase Checklist, Deliverables, and Success Criteria box ticked; Milestone-completion summary appended. |
| `docs/m5-claude-code-skill-log.md` | Modify | `Progress:` field updated to "M5 complete"; Phase 10 row → Complete; this entry; Milestone-completion summary appended. |
| `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md` | Regenerate | Re-synced in lockstep via `./bin/docs index --root docs/` after the spec/status/plan/log edits. |

#### Actions taken

1. **Full quality gate** re-run after every Phase-10 edit — all green (see the
   captured output below).
2. **`status.md`** — the "Current milestone" section now states v1 is complete
   and summarises the shipped M5; the milestone table row M5 → **Complete
   (2026-05-22)**; the "Resuming this work" section's reading order, verify-
   environment block (244 passed), and next-action ("none — v1 is complete")
   refreshed.
3. **`definition-of-ready.md`** — the parked cross-host-portability risk row is
   annotated **Resolved (M5, 2026-05-22)** against OQ2: the skill artifact is
   host-agnostic, the host path is the documented install step. The risk table
   itself is left intact as historical record (per the plan). The body edit
   triggered an `Updated:` bump, applied via `./bin/docs touch`.
4. **`plan.md`** — a one-line v1-completion note added under "Open questions":
   v1 is complete, the `[vocabulary] add_fields` extra-field allowlist question
   is unresolved and carries to v1.1, M5 opened no new plan-level question
   (resolved OQ3). The allowlist question itself is **not** resolved.
5. **Milestone-completion summaries** appended to both `m5-claude-code-skill.md`
   and this log; every Phase Checklist, Deliverables, and Success Criteria box
   in `m5-claude-code-skill.md` ticked.
6. **`docs/INDEX.md`** regenerated via `./bin/docs index --root docs/` and the
   dogfood snapshot `tests/fixtures/expected/docs-INDEX.md` re-synced in
   lockstep; the snapshot test (`tests/test_dogfood*`) passes.
7. **No code refactor** — M5 added no Python, so the `/simplify` step has no
   target. The equivalent is a final concision read-through of `SKILL.md`: the
   body holds at 112 non-blank lines, each verb section 4-6 tight lines, no
   redundancy — no change made.

#### Captured command output

```
$ .venv/bin/python -m pytest tests/ -q
244 passed in ~3.4s

$ .venv/bin/ruff check .
All checks passed!

$ .venv/bin/ruff format --check .
19 files already formatted

$ .venv/bin/mypy
Success: no issues found in 19 source files

$ ./bin/docs check docs/
docs: no violations found            # exit 0
```

#### Issues / decisions

- **`/simplify` is a no-op for an artifact milestone.** M5 added no Python.
  Phase 10's refactor step is satisfied by a concision read-through of the
  authored `SKILL.md` (recorded above) — there is no code to simplify.
- **The cross-host-portability risk row is left in place.** Per the plan, the
  `definition-of-ready.md` risk table is historical record — the row is
  annotated resolved rather than deleted.

#### Exit criteria

- [x] Full quality gate green — `pytest tests/` 244 passed; `ruff` /
      `ruff format` / `mypy` clean tree-wide; `docs check docs/` exit 0.
- [x] `status.md` reflects M5 → Complete and the project v1-complete.
- [x] `definition-of-ready.md`'s parked risk annotated resolved.
- [x] `plan.md` carries the one-line v1-completion note; the allowlist question
      is left parked for v1.1.
- [x] Milestone-completion summaries appended to both M5 docs; every Phase
      Checklist / Deliverables / Success Criteria box ticked.
- [x] `docs/INDEX.md` + the snapshot regenerated in lockstep; the suite passes.
- [x] **M5 — and the v1 roadmap — is complete.**

## Milestone-completion summary

**M5 — Claude Code skill shipped 2026-05-22**, across all ten TDD phases. M5 is
the project's **final v1 milestone — v1 is complete**: M1-M5 are all shipped.

### What M5 delivered

M5 authored the project's last deliverable — a Claude Code skill at
`skills/docs/SKILL.md` — that makes an agent reach for the `docs` verbs
automatically when doing documentation work in a `docs`-managed tree. The skill
adds **no CLI surface and no Python**: it is a markdown artifact whose
`description` triggers on the right contexts and whose body redirects to the
matching `docs` verb instead of hand-editing metadata, hand-curating
`INDEX.md`, or hand-moving a doc into `archive/`.

- **`skills/docs/SKILL.md`** — frontmatter (`name: docs` + a single-physical-
  line trigger-scoped `description`) and a 143-line imperative body. The body
  carries a never-hand-edit guardrail, host-agnostic binary/root-location
  guidance, a prose verb-redirection section with one sub-heading per verb (all
  eight `docs` verbs), an explicit prose-only-edit carve-out (OQ-H), and a
  pointer to `convention.md` / `cli.md` as the convention's source of truth.
- **`tests/test_skill.py`** — eight structural checks, the automatable half of
  the two-part oracle (resolved OQ1). GREEN as part of the 244-test suite.
- **The 11-row trigger-scenario checklist** — the behavioural half, walked at
  Phase 9: 11/11 satisfied (8 positive trigger-and-redirect, 3 negative
  handled; row 10 annotated per OQ-H).
- **Doc wiring** — `cli.md`'s skill pointer and `architecture.md`'s
  sibling-artifact + install note (both authored at Phase 1, verified at
  Phase 7).

### Phase-by-phase

| Phase | Outcome |
|---|---|
| 1 Define Contract | `SKILL.md` stub + final-shaped frontmatter; `tests/test_skill.py` 8 check signatures; `cli.md` / `architecture.md` wiring. |
| 2 Write Tests (RED) | 8 structural checks implemented; 11-row trigger checklist authored. RED: 3 content checks fail the stub. |
| 3 Create Data/Fixtures | Conscious "nothing to stage" — an artifact milestone has no foreign data. |
| 4 Run Tests (RED Baseline) | 3 RED / 5 GREEN — every RED a content `AssertionError`; fresh-eyes review strengthened the oracle. |
| 5 Update Base Interfaces | `description` authored as one physical line (OQ-E). Checks #1/#2/#3/#8 GREEN. |
| 6 Implement Offline/Core Path | Body authored — guardrail + 8-verb prose redirection + OQ-H carve-out. All 8 checks GREEN. |
| 7 Update Tool/Wrapper Layer | No `references/` needed; `cli.md` / `architecture.md` verified accurate. |
| 8 Run Tests (GREEN) | Full suite 244 passed; gates clean tree-wide. |
| 9 Integrate (dogfood) | 11/11 trigger-checklist rows satisfied; `INDEX.md` regenerated only via `docs index`. |
| 10 Quality, Docs, Refactor | v1 closed out — `status.md` / `plan.md` / `definition-of-ready.md` updated; summaries appended; gate green. |

### Decisions of record

- **OQ1** — the ten-phase TDD cycle maps onto an artifact milestone via a
  two-part oracle (`tests/test_skill.py` + the trigger checklist).
- **OQ2** — the skill is authored in-repo, installed by a documented manual
  step; this resolves `definition-of-ready.md`'s cross-host-portability risk.
- **OQ3** — M5 opened no new `plan.md` open question; the parked extra-field
  allowlist question carries to v1.1.
- **OQ4** — the skill `name` is `docs`.
- **OQ-A/-B/-C/-E/-F/-G/-H** — Step-2 author-guidance decisions (no `TODO`
  tokens; spec references as inline code not links; verbs as plain
  `` `docs <verb>` `` spans; single-physical-line `description`; prose verb
  list not a table; no further `cli.md` churn; an explicit prose-only-edit
  carve-out in the body) — all honoured in the authored artifact.

### Closing state

- `pytest tests/` → **244 passed** (236 M1-M4 + 8 M5); `ruff` /
  `ruff format --check` / `mypy` clean tree-wide; `./bin/docs check docs/` exit
  0; `docs index --root docs/` idempotent.
- M5's exit criterion is met: an agent working in this repo is redirected to
  run `docs index` instead of hand-editing `INDEX.md`.
- **The five-milestone v1 roadmap is complete.**

## Post-ship adjustments (2026-05-23)

A fresh-tree test of the installed skill (`/tmp/test-docs-tree/` walked
through the full bootstrap → `docs new` / `index` / `archive` / `mv` /
`touch` / `check` / `migrate` flow) exposed two issues — diagnosis in the
milestone doc's Post-ship section. Four commits on branch
`m5/skill-generalize`, stacked on the M5 stack:

| Commit | What |
|---|---|
| `a817de6` | Generalize SKILL.md framing from project-management-specific wording ("plan/spec/charter/milestone") to general document-management ("specs, runbooks, references, design notes"); clarify the tool's purpose in the body's opening paragraph. |
| `beec302` | Reshape the `description` for reliable triggering — "Use whenever the user asks to <X>" with the verbs and user keywords the Claude Code harness actually matches against; flip the body opening from descriptive to imperative; bold the central rule. |
| `dab0a8a` | Bundle `docs/{convention,cli}.md` as `skills/docs/references/` (byte-identical mirrors) plus `tests/test_skill_refs.py` for lockstep. Clean `docs/cli.md` and `docs/convention.md` for the user-facing reference audience — `Related:` blocks pared to mutual `pairs-with` only; cli.md's two dev-only `##` sections removed; their substance moves to `architecture.md` (already covered) and `plan.md`'s "Out of scope for v1" (the one unique bullet — "Templates beyond `docs new` defaults"). |
| `5a8b4f6` | Shorten `SKILL.md` from 160 → 82 lines (129 → 60 non-blank body): trigger surface, "when to use / when not to use" with the honest cwd-fallback note, compact 8-row verb-task table, "never hand-edit" rule, and real markdown links to the bundled references. Per-verb prose detail relocated to `references/cli.md`. |

### Post-adjustment state

- `pytest tests/` → **246 passed** (236 M1-M4 + 8 M5 `test_skill.py` + 2 lockstep `test_skill_refs.py`); quality gate clean tree-wide; `docs check docs/` exit 0.
- The structural oracle (8 checks in `test_skill.py`) is unchanged; `test_every_relative_link_resolves` is no longer vacuous — the bundled references give it real targets.
- The four resolved milestone-setup decisions (OQ1-OQ4) and all Step-2 author-guidance decisions (OQ-A..OQ-H) still hold. OQ-B's *implementation* (spec references as inline-code names with zero markdown links) is refined — the bundled references resolve via relative markdown links that travel with the installed skill, satisfying both OQ-B's host-agnostic intent and the user-facing reachability the original implementation broke.
- Phase 7's "no `references/` needed" call is reversed: the body did fit under the size budget without progressive disclosure, but the body's pointer to the convention had no file to follow in the deployed install. Bundling resolves that.
