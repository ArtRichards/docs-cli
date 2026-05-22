# M5 — Claude Code skill

Status: active
Role: milestone
Project: docs
Updated: 2026-05-22

Related:
- parent-of: m5-claude-code-skill-log.md
- child-of: plan.md
- implements: charter.md
- pairs-with: convention.md
- pairs-with: cli.md
- pairs-with: architecture.md
- pairs-with: test-strategy.md

## Overview

- Milestone: M5
- Title: Claude Code skill
- Surface: a Claude Code **skill** — a `SKILL.md` artifact (plus, if needed,
  small bundled reference files) authored at `skills/docs/` in this repo. Not a
  new `docs` CLI verb or Python code surface: M5 ships a markdown artifact that
  *drives* the verbs M1–M4 already shipped.
- Status: ACTIVE (started 2026-05-22)

### Goal

M1–M4 built the whole `docs` command surface: a tree is now readable
(`index`), writable (`new`, `archive`, `mv`, `touch`), enforceable and
queryable (`check`, `list`), and a foreign tree can be adopted (`migrate`).
M5 is the last milestone — it makes an **agent** reach for those verbs
automatically. It ships a Claude Code skill: a `SKILL.md` whose `description`
triggers when an agent is about to do documentation work in a `docs`-managed
tree, and whose body redirects the agent to the right `docs` verb instead of
hand-editing metadata, hand-curating `INDEX.md`, or hand-moving a completed
plan. The convention itself is **not** re-taught in the skill — that lives in
`convention.md`; the skill teaches *which verb to run when* and *how to read
its output*. M5's exit criterion is behavioural and dogfooded: the agent
working in this very repo stops hand-editing `INDEX.md` and runs `docs index`.

### Requirements

- A skill directory at `skills/docs/` in this repo containing a `SKILL.md`
  (the only required file) plus any small bundled reference file the body
  needs. The skill is **authored and version-controlled in this repo**;
  installation onto a host (symlink / copy into `~/.claude/skills/`) is a
  documented step, parallel to how `bin/docs` itself is installed (see
  `architecture.md`'s "Install").
- **Valid skill frontmatter.** `SKILL.md` opens with YAML frontmatter carrying
  exactly `name` and `description` (the two fields Claude Code reads to decide
  when a skill triggers). No other frontmatter keys.
- **A `description` that triggers on the right contexts and only those.** It
  must name both *what the skill does* and the *specific triggers* — editing a
  `.md` file under a `.docs.toml`-marked root; a request to "archive a doc",
  "list the docs", "create a plan / spec / charter / milestone"; being about
  to append to a hand-curated `INDEX.md`. It must **not** over-trigger on
  unrelated markdown work (a `README` in a non-`docs` repo, a prose edit with
  no metadata concern).
- **A skill body that redirects to verbs, not convention.** For each trigger,
  the body states the `docs` verb to run (`docs new <role> <slug>`,
  `docs archive <file>`, `docs index`, `docs check`, `docs list`,
  `docs mv`, `docs touch`, `docs migrate <dir>`), the flags that matter
  (`--dry-run`, `--json`, `--root`, `--apply`), and how to read the result
  (exit codes for `check`; the dry-run plan for `migrate`). It does **not**
  restate the on-disk metadata format — it points at `convention.md` and
  `cli.md` instead. It is concise (well under the skill-authoring 500-line
  budget) and written in imperative form.
- **The skill locates the binary and the root correctly.** The body tells the
  agent how to find the `docs` executable (`bin/docs` in a checkout; an
  installed `docs` on `$PATH`) and how `docs` resolves a root (upward
  `.docs.toml` search; `--root`). The cross-host path concern flagged in
  `definition-of-ready.md`'s risk register is addressed here, not left open.
- **The skill is the "do not hand-edit" guardrail.** Its central instruction:
  when working in a `docs`-managed tree, never hand-edit `INDEX.md`, never
  hand-move a doc into `archive/`, never hand-write a metadata block — run the
  verb. This is the behaviour M5's exit criterion checks.
- **The skill is validated and exercised, not just written** — see the TDD
  Implementation Plan and the OQ1 resolution (in Decisions) for how the
  ten-phase cycle maps onto a markdown artifact.

### Deliverables

- [ ] `skills/docs/SKILL.md` — the skill artifact: valid `name` /
      `description` frontmatter and an imperative, verb-redirecting body.
- [ ] Any bundled reference file the body needs kept minimal (a verb
      cheat-sheet at most); no `README`/`CHANGELOG`/auxiliary clutter in the
      skill directory (per the skill-authoring guidance).
- [ ] `tests/test_skill.py` — automated checks over the skill artifact: the
      frontmatter parses and carries exactly `name` + `description`; the body
      stays within the size budget; every `docs` verb the body names is a real
      subcommand of `bin/docs`; every relative link the body makes resolves;
      no stray non-skill files in `skills/docs/`. (The structural half of the
      RED/GREEN cycle — see the OQ1 resolution in Decisions.)
- [ ] A **trigger-scenario checklist** in this milestone's log — a fixed set
      of "agent is about to do X" scenarios, each with the verb the skill
      should redirect to and whether the `description` should trigger. This is
      the behavioural half of the RED/GREEN cycle: it is RED before the skill
      is written (no skill, no redirect) and GREEN once the dogfood pass walks
      it (see Phase 9).
- [ ] `docs/cli.md` updated: the skill is no longer "deliberately not in v1"
      framing is N/A (cli.md never listed it); instead cli.md gains a short
      "Using `docs` from a Claude Code skill" pointer, and
      `architecture.md` gains the skill artifact + install note.
- [ ] Install path documented: how `skills/docs/` is linked/copied into a
      host's `~/.claude/skills/` — in `architecture.md`'s install section,
      parallel to the `bin/docs` symlink instruction.
- [ ] Dogfood: this repo's own `INDEX.md` is regenerated only with
      `docs index`; the skill is exercised against the trigger-scenario
      checklist; `docs check docs/` stays exit 0.
- [ ] All quality gates green tree-wide: `ruff check .`, `ruff format --check
      .`, `mypy`, `pytest -q` (the suite now includes `tests/test_skill.py`).
- [ ] `docs/status.md` updated; M5 → Complete, project v1 complete (M5 is the
      final milestone).

## Current state analysis (snapshot at milestone kickoff, 2026-05-22)

_Captured before Phase 1; historical. Post-milestone state lives in the
Milestone-completion summary at the bottom of this file._

- **The verb surface M5 wraps is complete.** `bin/docs` shipped M1–M4
  (~2,200 lines): eight subcommands — `index`, `new`, `archive`, `mv`,
  `touch`, `check`, `list`, `migrate` — config loading, the parser/walker/
  renderer, surgical metadata editors, validation, query, and the foreign-tree
  importer. 236 passing tests across 17 files. **M5 adds no verb and changes
  no verb behaviour** — every command the skill names already exists, is
  specified in [cli.md](cli.md), and is tested. M5's job is purely to author
  the artifact that makes an agent *use* them.
- **The skill format is a known quantity.** A Claude Code skill is a directory
  with a required `SKILL.md` — YAML frontmatter (`name`, `description`) plus a
  markdown body — and optional `scripts/` / `references/` / `assets/`
  subdirectories. The `description` is the trigger mechanism (always in the
  agent's context); the body loads only after the skill triggers. The
  authoring guidance (the `skill-creator` skill on this host) sets the rules
  M5 follows: concise body under ~500 lines, imperative voice, no auxiliary
  documentation files, progressive disclosure if the body grows.
- **What plan.md asks for.** [plan.md](plan.md)'s M5 section: a `SKILL.md`
  "at `~/.claude/skills/docs/` (or wherever the install convention lands)";
  triggers on editing a `.md` under a `.docs.toml` root, on archive/list/
  create-doc requests, and before an agent appends to a hand-curated INDEX;
  the body "redirects to the appropriate `docs` verb instead of hand-editing";
  it documents triggers and verbs "without re-teaching the convention (that
  lives in `convention.md`)". Exit criterion: "the agent stops hand-editing
  INDEX.md in this repo and uses `docs index`."
- **The open risk M5 closes.** [definition-of-ready.md](definition-of-ready.md)'s
  risk register parks one risk explicitly for this milestone: "Cross-host
  portability of the script — paths embedded in skill files diverge from
  per-host install paths … Skill is M5 and not authored yet; postpone the
  concern until then." M5 addresses it directly — see the Decisions below.
- **The methodology gap.** The ten-phase TDD cycle in [status.md](status.md)
  was written for a Python code surface — "Write Tests (RED)", "Implement
  Core", "Run Tests (GREEN)". M5's deliverable is a markdown artifact, not
  code. The phases still apply, but "tests" and "RED/GREEN" must be
  re-interpreted for an artifact. The mapping was the milestone's one genuine
  contract decision and was surfaced as a milestone-setup open question (OQ1);
  it is now resolved — see the OQ1 Decision.

## TDD Implementation Plan

The ten phases follow the fixed methodology in [status.md](status.md). Phases
1–4 establish the contract, the tests/checklist, the fixtures, and the RED
baseline with **no skill body written**; phases 5–10 author and ship.

**Phase mapping for an artifact milestone.** M5 ships a `SKILL.md`, not code.
The phases are interpreted (this is the resolved OQ1 mapping — see the OQ1
Decision):

- "Contract" (Phase 1) = the skill's *shape*: directory layout, frontmatter
  keys, the verb-trigger matrix the body must cover, and the stubs/checks that
  pin it.
- "Write Tests (RED)" (Phase 2) = (a) `tests/test_skill.py` — structural,
  automatable checks over the artifact; and (b) the **trigger-scenario
  checklist** — the behavioural oracle, a fixed list of "agent about to do X →
  expected verb" rows, walked by a human/agent at Phase 9.
- "RED baseline" (Phase 4) = `tests/test_skill.py` fails because `SKILL.md`
  has only a stub body; the trigger checklist is unsatisfiable (no skill).
- "Implement Core" (Phases 5–7) = author the frontmatter, then the body, then
  any bundled reference file and the install/doc wiring.
- "Run Tests (GREEN)" (Phase 8) = `tests/test_skill.py` passes; the full
  suite stays green.
- "Online/Integration" (Phase 9, the dogfood pass) = walk the trigger-scenario
  checklist against the authored skill and confirm the exit-criterion
  behaviour in this repo.

### Phase 1: Define Contract

- **Objective:** Declare the M5 surface. No skill body written.
- **Files:**
  - `skills/docs/SKILL.md` — created with valid frontmatter (`name: docs`,
    a first-draft `description`) and a **stub body** (a single TODO line, or
    a one-line placeholder) so the artifact exists and the structural tests
    have something to fail against.
  - `tests/test_skill.py` — created with the test *signatures* only (each
    test body a `pytest.fail("… — Phase 2")` or equivalent placeholder), so
    the file collects.
  - `docs/cli.md` — add a short "Using `docs` from a Claude Code skill"
    pointer subsection (the skill drives the verbs already specified here);
    `Updated` bumped.
  - `docs/architecture.md` — add a `skill` artifact note to the Shape /
    module list and an install note (`skills/docs/` linked into
    `~/.claude/skills/`); `Updated` bumped.
  - `docs/status.md` — M5 marked in flight.
  - `docs/m5-claude-code-skill.md`, `docs/m5-claude-code-skill-log.md` —
    created (this file and its log).
- **Exit:** `skills/docs/SKILL.md` exists with parseable frontmatter and a
  stub body; `tests/test_skill.py` collects; `ruff` / `mypy` clean;
  `docs/INDEX.md` and the dogfood snapshot regenerated in lockstep so they
  pick up the two new M5 docs.

### Phase 2: Write Tests (RED)

- **Objective:** Express every M5 requirement as a failing check — both the
  automatable structural checks and the behavioural trigger checklist.
- **Files:**
  - `tests/test_skill.py` — implement the checks: (1) `SKILL.md` exists and
    starts with `---` YAML frontmatter; (2) the frontmatter parses and carries
    *exactly* `name` and `description` — no other keys; (3) `name` is the
    expected slug and `description` is non-empty and within a sane length;
    (4) the body is non-empty and within the size budget (lines / characters);
    (5) every `docs <verb>` token the body names is a real subcommand of
    `bin/docs` (asserted against `_build_parser()` / `docs --help`, reusing
    `conftest.py`'s loaded `docs` module); (6) every relative markdown link in
    the body resolves to a real file; (7) `skills/docs/` contains no
    auxiliary clutter (`README.md`, `CHANGELOG.md`, …).
  - `docs/m5-claude-code-skill-log.md` — the **trigger-scenario checklist**
    table is written into the log: a fixed set of scenarios (e.g. "agent
    asked to create a plan", "agent about to append a line to `INDEX.md`",
    "agent asked to archive a finished milestone doc", "agent editing a
    `.md` in a non-`docs` repo — should NOT trigger"), each row naming the
    expected `docs` verb (or "no trigger"). It is RED now — no skill body
    satisfies it.
- **Exit:** `tests/test_skill.py` collects and every check fails for the
  right reason — the stub body, not a misconfiguration; the trigger checklist
  exists and is entirely unsatisfied.

### Phase 3: Create Data/Fixtures

- **Objective:** Provide whatever fixture the structural checks need.
- **Files:**
  - The structural checks read the real `skills/docs/SKILL.md` and the real
    `bin/docs` verb list — no synthetic fixture tree is required (unlike
    M1–M4, M5's "data" is the artifact under test itself plus the existing
    `docs/` tree used for the dogfood). If a check needs an isolated input
    (e.g. a malformed-frontmatter sample to prove the parser check is real),
    a tiny inline string in `tests/test_skill.py` suffices — no new
    `tests/fixtures/trees/` directory.
- **Exit:** every input a Phase 2 check references is available; no new
  fixture tree was needed (recorded as a deliberate, documented difference
  from M1–M4 — an artifact milestone has no foreign data to stage).

### Phase 4: Run Tests (RED Baseline)

- **Objective:** Confirm every failure traces to the unwritten skill body,
  not misconfiguration. Log-only; no body authored. **This session pauses
  here.**
- **Actions:** `.venv/bin/python -m pytest tests/` — capture full output.
- **Exit:** every `tests/test_skill.py` failure traces to the stub body
  (missing/short body, no verbs named, etc.), not an `ImportError` or path
  error; M1–M4's 236 tests stay green; the trigger-scenario checklist stands
  fully RED.

### Phase 5: Update Base Interfaces

- **Objective:** Author the skill's *frontmatter* — the trigger surface.
- **Files:** `skills/docs/SKILL.md` — finalise `name` and, in particular,
  the `description`: it must name what the skill does and the precise trigger
  contexts (editing a `.md` under a `.docs.toml` root; archive/list/create
  requests; about to hand-edit `INDEX.md`) and must not over-trigger. This is
  the "interface" of a skill — the only part always in an agent's context.
- **Exit:** the frontmatter checks in `tests/test_skill.py` (exists, parses,
  exactly `name`+`description`, sane values) are green; `ruff` / `mypy` stay
  clean (no Python changed).

### Phase 6: Implement Offline/Core Path

- **Objective:** Author the skill *body* — the verb-redirecting instructions.
- **Files:** `skills/docs/SKILL.md` — write the body: per trigger, the `docs`
  verb to run, the flags that matter, how to read the output; the central
  "never hand-edit `INDEX.md` / `archive/` / metadata — run the verb"
  guardrail; the binary/root-location guidance; pointers to `convention.md`
  and `cli.md` rather than restating the convention.
- **Exit:** the body checks in `tests/test_skill.py` (non-empty, within
  budget, every named verb real, every link resolves) are green.

### Phase 7: Update Tool/Wrapper Layer

- **Objective:** Finalise the artifact's edges — any bundled reference file,
  the install/doc wiring, and the clutter check.
- **Files:**
  - `skills/docs/` — add a minimal bundled reference file *only if* the body
    needs progressive disclosure (likely a single verb cheat-sheet, or
    nothing); ensure no auxiliary files remain.
  - `docs/architecture.md` — finalise the install note (`skills/docs/`
    symlinked/copied into `~/.claude/skills/docs/`).
  - `docs/cli.md` — finalise the skill pointer subsection.
- **Exit:** every `tests/test_skill.py` check green, including the
  no-clutter check; `ruff` / `mypy` clean.

### Phase 8: Run Tests (GREEN)

- **Objective:** Full suite passing; quality gates clean tree-wide.
- **Actions:** `pytest -q`; `ruff check .`; `ruff format --check .`; `mypy`.
- **Exit:** all green — `tests/test_skill.py` included.

### Phase 9: Implement Online/Integration (dogfood pass)

- **Objective:** Exercise the skill — the behavioural half of GREEN. This is
  the M5 equivalent of M1–M4's dogfood pass.
- **Actions:** Walk the **trigger-scenario checklist** from Phase 2 against
  the authored `SKILL.md`: for each scenario, confirm the `description` would
  trigger (or correctly not) and that the body redirects to the expected
  verb. Confirm the exit-criterion behaviour in this repo: regenerate this
  repo's `INDEX.md` only via `docs index`; confirm `docs check docs/` exits 0.
  Optionally install the skill into `~/.claude/skills/docs/` and confirm it is
  picked up.
- **Exit:** every checklist row is satisfied (the skill triggers and
  redirects as specified, and correctly does not trigger on the negative
  rows); `docs index` is the only thing that has touched `INDEX.md`.

### Phase 10: Quality, Docs, Refactor

- **Objective:** Close out M5 — and the project.
- **Actions:** full quality gate; update [status.md](status.md) (M5 →
  Complete; the project has reached v1 — all five milestones shipped); confirm
  [definition-of-ready.md](definition-of-ready.md)'s parked cross-host
  portability risk is now addressed (note it as resolved against the OQ2
  Decision; leave the risk table itself as historical record). Per the OQ3
  Decision, add a one-line note to [plan.md](plan.md) that v1 is complete and
  the parked extra-field allowlist question carries forward to v1.1 — without
  resolving it. Append milestone-completion summaries here and in the log;
  regenerate `docs/INDEX.md` + the snapshot in lockstep.
- **Exit:** quality gate green; docs updated; M5 — and the v1 roadmap — is
  complete.

## Phase Checklist

- [ ] Phase 1: Define Contract
- [ ] Phase 2: Write Tests (RED)
- [ ] Phase 3: Create Data/Fixtures
- [ ] Phase 4: Run Tests (RED Baseline)
- [ ] Phase 5: Update Base Interfaces
- [ ] Phase 6: Implement Offline/Core Path
- [ ] Phase 7: Update Tool/Wrapper Layer
- [ ] Phase 8: Run Tests (GREEN)
- [ ] Phase 9: Implement Online/Integration (dogfood pass)
- [ ] Phase 10: Quality, Docs, Refactor

## Decisions

Key choices applying to this milestone (broader decisions live in `vocab-adr.md`
and `dual-status-adr.md`). The first four record the milestone-setup OPEN
QUESTIONS as resolved (operator-confirmed 2026-05-22; the full
question / why-it-matters / recommendation text is preserved under "OPEN
QUESTIONS — resolved" below):

- **OQ1 — the ten-phase TDD cycle maps onto an artifact milestone via a
  two-part oracle (RESOLVED, approved as recommended).** M5 ships a `SKILL.md`
  artifact, not code; rather than skip the test phases, all ten phases are kept
  and "tests" is re-interpreted as a two-part oracle, both authored at Phase 2:
  (1) `tests/test_skill.py` — the structural, automatable half — runs RED→GREEN
  in CI and checks the deterministic properties of the artifact: valid
  frontmatter (exactly `name` + `description`), the size budget, every named
  `docs` verb is a real subcommand of `bin/docs`, every relative link resolves,
  and no auxiliary clutter; (2) the behavioural **trigger-scenario checklist**
  in [m5-claude-code-skill-log.md](m5-claude-code-skill-log.md) — a fixed table
  of "agent about to do X → expected verb (or 'no trigger')" rows including
  **negative rows for over-triggering** — walked at the Phase 9 dogfood pass.
  No phase is marked N/A; Phase 3 records a conscious "nothing to stage" rather
  than a skipped phase.
- **OQ2 — the skill is authored in-repo and installed by a documented manual
  step (RESOLVED, approved as recommended).** M5 authors the skill in-repo at
  `skills/docs/` and documents a manual copy/symlink into
  `~/.claude/skills/docs/`, exactly parallel to the `bin/docs` install. There
  is **no installer script and no `$HOME` write inside the milestone** — M5
  stays a pure artifact milestone. The committed artifact is host-agnostic; the
  host-specific path lives only in the documented install step. This is the
  resolution of `definition-of-ready.md`'s parked cross-host-portability risk.
- **OQ3 — M5 opens no new `plan.md` open question (RESOLVED, approved as
  recommended).** The skill's scope is fully determined by [plan.md](plan.md)'s
  M5 section and the skill-authoring conventions; nothing in M5 is undecided at
  the `plan.md` level. The parked extra-field allowlist question stays parked
  as **post-v1** work — M5 does not resolve it. Phase 10 adds a one-line note
  to `plan.md` that v1 is complete and the allowlist question carries forward
  to v1.1, but does not resolve it. (Follows the M4 precedent — a milestone
  need not open a `plan.md` question.)
- **OQ4 — the skill `name` is `docs` (RESOLVED).** The skill is named `docs` —
  the project's name, the binary's name, and the path [plan.md](plan.md)
  explicitly writes (`~/.claude/skills/docs/`). No host collision is known.
  The over-triggering concern is handled by the `description` text (and the
  checklist's negative rows), not by the `name`; a collision would be a
  host-install concern, mitigated by the documented install step.
- **M5 ships an artifact, not code — the ten-phase cycle is mapped, not
  abandoned.** M1–M4 each added a Python code surface; M5's deliverable is a
  `SKILL.md` markdown artifact. Rather than skip phases, M5 *re-interprets*
  them (see the TDD Implementation Plan's "Phase mapping" note and OQ1's
  resolution): "Contract" is the skill's shape; "tests" are the structural
  `tests/test_skill.py` checks plus a behavioural trigger-scenario checklist;
  "RED→GREEN" is the artifact moving from stub to authored. This keeps M5
  inside the project's methodology rather than treating the last milestone as
  an exception.
- **The skill lives in this repo at `skills/docs/`, installed from there.**
  [plan.md](plan.md) says "`~/.claude/skills/docs/` (or wherever the install
  convention lands)". The skill is *authored and version-controlled* in the
  repo at `skills/docs/` — it is a project deliverable and must be diffable,
  testable, and shipped with the code it drives. Installation onto a host is a
  documented copy/symlink into `~/.claude/skills/docs/`, exactly parallel to
  how `bin/docs` is itself installed via a symlink onto `$PATH`
  (`architecture.md`'s Install section). This is the resolution of
  `definition-of-ready.md`'s parked cross-host-portability risk: the artifact
  is host-agnostic; the host-specific path is the install step, not baked into
  the committed file.
- **The skill teaches verbs, not the convention.** [plan.md](plan.md) is
  explicit: the skill documents triggers and verbs "without re-teaching the
  convention (that lives in `convention.md`)". The body therefore points at
  `convention.md` and `cli.md` and never restates the metadata-block format,
  the vocabulary, or the archive layout. This keeps the skill small (within
  the ~500-line authoring budget), keeps a single source of truth for the
  convention, and means a convention change does not silently rot the skill.
- **The skill must not over-trigger.** A `description` that fires on every
  markdown edit anywhere would be worse than no skill — it would inject `docs`
  guidance into unrelated work. The `description` is scoped to documentation
  work *in a `docs`-managed tree* (a `.docs.toml`-marked root) and to explicit
  archive/list/create-doc requests. The trigger-scenario checklist includes
  **negative rows** — scenarios where the skill must *not* trigger — so the
  scoping is exercised, not just asserted.
- **Structural checks are automated; behavioural triggering is a checklist.**
  Whether a skill *body* makes a good agent decision cannot be unit-tested in
  pytest — that is a property of how an agent reads it. M5 splits the
  verification: the automatable, deterministic properties of the artifact
  (valid frontmatter, size budget, real verbs, resolving links, no clutter)
  go in `tests/test_skill.py` and run in CI with the rest of the suite; the
  judgement property (does the skill trigger and redirect correctly for a
  given scenario) is a fixed **trigger-scenario checklist** walked at the
  Phase 9 dogfood pass. Both are written at Phase 2 — the checklist is as much
  a "RED test" as the pytest file; it is simply executed by a human/agent
  rather than by `pytest`. This is the honest mapping of TDD onto an artifact
  whose correctness is partly a judgement call.
- **No new `tests/fixtures/trees/` directory.** M1–M4 each staged a synthetic
  fixture tree. M5's structural checks read the real artifact (`skills/docs/
  SKILL.md`) and the real verb list (`bin/docs`); its dogfood reads this
  repo's own `docs/`. The only synthetic data M5 might need is a tiny inline
  malformed-frontmatter string inside `tests/test_skill.py` to prove the
  frontmatter check is real. The absence of a fixture tree is a deliberate,
  documented consequence of an artifact milestone — recorded so Phase 3 is a
  conscious "nothing to stage" rather than an omission.
- **OQ-E — the SKILL.md frontmatter `description` is a single physical line
  (RESOLVED, fresh-eyes review 2026-05-22; operator-binding).** `test_skill.py`'s
  hand-rolled frontmatter parser (`_parse_frontmatter`) splits on physical
  newlines and treats every non-blank line as its own `key: value` pair — it
  cannot handle a YAML-folded (`>-` / `|`) or wrapped multi-line `description`.
  The resolution is **not** to harden the parser but to constrain the artifact:
  the `description` MUST be authored as a single physical line — no YAML
  folding, no wrapped continuation lines. This is behaviour-neutral (a long
  description on one physical line is valid YAML and valid for Claude Code) and
  is the same author-guidance shape as OQ-B/OQ-C. **The Step 2 Phase-5 author
  must honour this: write `description:` as exactly one physical line.**
- **`bin/docs` single-file vs package split — not in scope for M5.** M2–M4's
  Decisions tracked a possible package split; M4 deferred it to v1.1. M5 adds
  **no Python**, so the question is untouched here and remains deferred to
  v1.1. Recorded so Phase 10 does not re-open it.
- **M5 is the final v1 milestone.** Closing M5 completes the five-milestone
  roadmap in [plan.md](plan.md). Phase 10 marks the project v1-complete in
  [status.md](status.md), not merely "M5 done, M6 next".

## Testing / Quality Gate

Commands run at Phase 4 (RED baseline), Phase 8 (GREEN), and Phase 10:

```
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
./bin/docs check docs/                                 # repo still clean
./bin/docs index --root docs/ --dry-run                # INDEX idempotent
```

Plus the M5-specific behavioural gate at Phase 9: walk the trigger-scenario
checklist in [m5-claude-code-skill-log.md](m5-claude-code-skill-log.md)
against the authored `skills/docs/SKILL.md`.

Expected at Phase 4: M1–M4's 236 tests green; every new `tests/test_skill.py`
check RED against the stub body; the trigger checklist fully unsatisfied.
Expected at Phase 8/10: all commands green, `tests/test_skill.py` included;
the trigger checklist fully satisfied; `docs index` is the only thing that
edits `INDEX.md`.

## Success Criteria

M5 is complete when:

- [ ] All Phase Checklist items are checked.
- [ ] `skills/docs/SKILL.md` exists with valid frontmatter (exactly `name` +
      `description`) and an imperative, verb-redirecting body within the
      skill-authoring size budget.
- [ ] The `description` triggers on the contexts [plan.md](plan.md) names
      (editing a `.md` under a `.docs.toml` root; archive/list/create-doc
      requests; about to hand-edit `INDEX.md`) and does not over-trigger —
      verified against the trigger-scenario checklist's negative rows.
- [ ] The body redirects every covered trigger to a real `docs` verb and
      re-teaches none of the convention (points at `convention.md` / `cli.md`).
- [ ] `tests/test_skill.py` passes — frontmatter, size budget, real-verb,
      link-resolution, and no-clutter checks all green — as part of the full
      suite.
- [ ] The Phase 9 dogfood pass satisfies the whole trigger-scenario
      checklist; this repo's `INDEX.md` is regenerated only via `docs index`;
      `docs check docs/` exits 0.
- [ ] The skill's install path is documented in [architecture.md](architecture.md)
      and the cross-host portability risk in
      [definition-of-ready.md](definition-of-ready.md) is addressed.
- [ ] All Deliverables above are checked off.
- [ ] [status.md](status.md) reflects M5 → Complete and the project as
      v1-complete (all five milestones shipped).
- [ ] [m5-claude-code-skill-log.md](m5-claude-code-skill-log.md) contains a
      milestone-completion summary.

## OPEN QUESTIONS — resolved

_All four milestone-setup questions were triaged against [plan.md](plan.md) and
the M1–M4 precedent and operator-confirmed on 2026-05-22. Each resolution is
recorded as a Decision in the "Decisions" section above (OQ1–OQ4). The full
question, why-it-matters, and recommendation text is preserved here as the
historical record; a **RESOLVED** line at the head of each gives the verdict._

### OQ1 — How the ten-phase TDD cycle maps onto a skill-authoring milestone

**RESOLVED (operator-confirmed 2026-05-22) — approved as recommended.** Keep all
ten phases; use the two-part oracle — `tests/test_skill.py` for the automatable
structural checks (valid frontmatter, size budget, every named `docs` verb is
real, links resolve, no clutter) running RED→GREEN in CI, plus the behavioural
trigger-scenario checklist in the log, walked at the Phase 9 dogfood pass with
negative rows for over-triggering. Phase 3 records a conscious "nothing to
stage". See the OQ1 Decision above.


**Question.** M1–M4 each shipped a Python code surface, so "Write Tests
(RED)", "Implement Core", and "Run Tests (GREEN)" had a literal meaning:
pytest files that fail, then code, then the same files passing. M5's
deliverable is a `SKILL.md` markdown artifact. What do "tests", "RED", and
"GREEN" mean for it, and is `tests/test_skill.py` plus a manual checklist the
right shape — or should M5 explicitly mark some phases N/A?

**Why it matters.** It is the milestone's one genuine contract decision. Get
it wrong in one of two directions: (a) treat M5 as an exception and skip the
test phases — then the skill ships unverified, with stale verb names, broken
links, or an over-triggering `description` that nothing catches; or (b) force
a pytest "behavioural" test of the skill body — but whether a skill body makes
an agent take the right action is a judgement property that cannot be
asserted in `pytest` without re-implementing an agent. Either failure breaks
the project's methodology discipline on its last milestone.

**Recommended answer (drafted into the plan above).** Keep all ten phases;
re-interpret "tests" as a **two-part oracle**, both authored at Phase 2:

1. **`tests/test_skill.py` — the structural, automatable half.** The
   deterministic properties of the artifact *can* be unit-tested and *should*
   run in CI with the rest of the suite: frontmatter parses and carries
   exactly `name` + `description`; the body is non-empty and within the size
   budget; every `docs <verb>` the body names is a real subcommand of
   `bin/docs` (this is the high-value check — it catches the skill drifting
   out of sync with the CLI); every relative link resolves; no auxiliary
   clutter files. This is genuine RED→GREEN: RED at Phase 4 against the stub
   body, GREEN at Phase 8 against the authored one. It aligns with
   [test-strategy.md](test-strategy.md)'s "every code path … has a unit test"
   spirit applied to the artifact, and adds one file to the existing pytest
   suite.

2. **The trigger-scenario checklist — the behavioural half.** A fixed table
   of "agent is about to do X → expected `docs` verb (or 'no trigger')" rows,
   including negative rows, written into the milestone log at Phase 2. It is
   RED before the skill exists and walked at the Phase 9 dogfood pass — the
   direct analogue of M1–M4's "dogfood `docs` against a fixture tree" Phase 9.
   It is a *test* in the TDD sense (written before the implementation,
   defines done) even though a human/agent executes it rather than `pytest` —
   because the property it checks (good agent redirection) is a judgement
   call, not a deterministic computation.

No phase is marked N/A. Phase 3 ("Create Data/Fixtures") is the one phase
that genuinely shrinks — an artifact milestone has no foreign data to stage —
and the plan records that as a conscious "nothing to stage" outcome rather
than a skipped phase. This mapping keeps M5 honest to the methodology, gives
the skill real CI-enforced verification, and is the recommendation.

### OQ2 — Skill install path: documented step vs. committed `~/.claude/` write

**RESOLVED (operator-confirmed 2026-05-22) — approved as recommended.** Author
the skill in-repo at `skills/docs/`; document a manual copy/symlink into
`~/.claude/skills/docs/` parallel to the `bin/docs` install. No installer
script, no `$HOME` write inside the milestone. See the OQ2 Decision above.

**Question.** [plan.md](plan.md) says the skill lands "at
`~/.claude/skills/docs/` (or wherever the install convention lands)". Should
M5 (a) author the skill in-repo at `skills/docs/` and document a manual
install copy/symlink, or (b) additionally ship an installer that writes into
`~/.claude/skills/`?

**Why it matters.** It decides whether M5 has any host-mutating surface at
all. Option (b) would make M5 touch `$HOME`, need its own tests for the
install action, and risk the cross-host path problem
[definition-of-ready.md](definition-of-ready.md) flagged. Option (a) keeps M5
a pure artifact milestone.

**Recommended answer (drafted into the plan above).** Option (a). Author the
skill in-repo at `skills/docs/`; document the install as a one-line
copy/symlink into `~/.claude/skills/docs/` in
[architecture.md](architecture.md)'s Install section, exactly parallel to the
existing `ln -s …/bin/docs ~/bin/docs` instruction. No installer script, no
`$HOME` write inside the milestone. The committed artifact stays host-
agnostic; the host-specific path lives only in the documented install step.
This is the smallest surface that satisfies [plan.md](plan.md) and is the
recommendation. (Revisit an installer post-v1 only if manual install proves
a real friction point.)

### OQ3 — Does M5 open a new `plan.md` open question, and what happens to the
parked extra-field allowlist question?

**RESOLVED (operator-confirmed 2026-05-22) — approved as recommended.** M5 opens
no new `plan.md` open question; the parked extra-field allowlist question stays
parked as post-v1 work; Phase 10 notes v1 completion. (Conductor auto-resolved
— conventional, follows the M4 precedent.) See the OQ3 Decision above.

**Question.** [plan.md](plan.md) currently carries one Open question — the
post-v1 `[vocabulary] add_fields` allowlist. M5 is the final milestone. Does
M5 open any new `plan.md` question, and is the parked allowlist question
resolved, left parked, or moved to a "v1.1 backlog"?

**Why it matters.** Phase 10 must leave `plan.md` in a coherent end-of-v1
state. M4 set the precedent that a milestone need not open a `plan.md`
question (M4 opened none, operator-confirmed).

**Recommended answer.** M5 opens **no new `plan.md` open question** — the
skill's scope is fully determined by [plan.md](plan.md)'s M5 section and the
skill-authoring conventions; nothing in M5 is genuinely undecided at the
`plan.md` level. The parked extra-field allowlist question is explicitly
*post-v1* and is **left parked as-is** — M5 does not resolve it (it is
unrelated to the skill) and does not need to. Phase 10 may optionally add a
one-line note to `plan.md` that v1 is complete and the allowlist question
carries forward to v1.1, but it does not *resolve* it. Recommended:
M5 opens nothing; the allowlist question stays parked; Phase 10 notes v1
completion. Operator to confirm.

### OQ4 — Skill `name`: `docs` vs. a less collision-prone slug

**RESOLVED (operator-confirmed 2026-05-22) — use `docs`.** Consistent with
[plan.md](plan.md)'s `~/.claude/skills/docs/` path; no host collision exists.
(Conductor auto-resolved — naming with an obvious default.) See the OQ4
Decision above.

**Question.** The natural skill `name` is `docs`. But "docs" is an extremely
generic token; a host may already have a skill, command, or directory called
`docs`, and `~/.claude/skills/docs/` is a broad name to claim. Should the
skill be named `docs`, or something more specific like `docs-cli` or
`docs-tree`?

**Why it matters.** The `name` is the skill's identity and its install
directory. A collision on a host would be confusing; an over-generic trigger
name can also nudge the skill toward over-triggering.

**Recommended answer.** Name the skill **`docs`**. It is the project's name,
the binary's name, and [plan.md](plan.md) explicitly writes
`~/.claude/skills/docs/`. The over-triggering concern is handled by the
`description` text (OQ1's checklist has negative rows), not by the `name`.
A collision is a host-install concern, mitigated by the documented install
step (the installer/operator chooses the directory). Recommended: `docs`,
consistent with `plan.md`. Operator to confirm — if a host collision is known,
`docs-cli` is the fallback.
