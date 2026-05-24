# M8 — Adoption workflow (agent-driveable)

Status: draft
Role: milestone
Project: docs
Updated: 2026-05-24

Related:
- child-of: plan.md
- implements: charter.md
- pairs-with: cli.md
- pairs-with: m7-migration-accuracy.md
- pairs-with: m5-claude-code-skill.md
- pairs-with: m6-pypi-distribution.md

## Overview

- Milestone: M8 (v1.1)
- Title: Adoption workflow — agent-driveable
- Surface: new CLI flags + verbs (`--exclude`, `--summary`,
  `--only ambiguous`, `--group-by`, `docs new --body-from`, optional
  `docs scaffold`), a new `[exclude]` section in `.docs.toml`
  applied **tree-wide**, an optional `.docsignore` file, and a
  substantial rewrite of the bundled Claude Code skill's reference
  files to cover the adoption flow. SKILL.md gets only a single
  pointer line; the substance lives in `references/`.
- Status: **DRAFT** — captured 2026-05-24. Depends on M7
  shipping first (M7's accurate plan is the substrate M8 makes
  driveable).

### Goal

M7 makes `docs migrate`'s plan accurate. M8 makes the workflow
around that plan agent-driveable end-to-end: an agent walks into a
foreign tree, runs migrate, triages the plan, decides on excludes,
iterates, applies, and verifies — without operator intervention
beyond the OQs the playbook explicitly flags as human-only.

The verb stays dry-run by default. M8 adds flags + verb modes that
make triage cheap, plus skill references that teach the procedure.

### Why this is M8 (and not part of M7 or M6)

- It's not M7 because the triage flags + skill references only pay
  off once the plan is accurate. An agent trying to triage a noisy
  M6-era plan would stall on the noise, not on the workflow.
- It's not M6 because M6 was packaging — the skill ships in the
  M6 wheel, but the *content* of the skill's adoption guidance
  belongs to whichever milestone delivers the matching CLI
  surface. That's M8.

## Findings (the M8 backlog)

### F3 — No way to exclude generated-data subdirectories

Trial 1's primary data subdir is 185 LLM-output files. It's data,
not documentation. Migrate today walks it and emits 185 low-
confidence plan entries, drowning the signal. Trial 2 has similar
patterns at smaller scale.

**M8 proposes (multiple complementary forms):**

1. **`docs migrate <dir> --exclude <subdir>/ --exclude <other>/`**
   — flag, repeatable, glob-supporting.
2. **`[exclude] dirs = ["<subdir>", "<other-subdir>"]` in
   `.docs.toml`** — persistent. **Applies tree-wide** (`migrate`
   + `index` + `check` + `list` all honour the same list).
   Operator decision 2026-05-24: single source of truth.
3. **Glob patterns:** `--exclude '**/generated/**'`,
   `--exclude '*memo*'`, `--exclude-ext xlsx,html`.
4. **`.docsignore` file** at the tree root, gitignore-style
   syntax.
5. **Auto-detection mode:** `docs migrate --propose-excludes
   <dir>` runs a heuristic pass first (subdirs with >N files
   sharing a common suffix; subdirs with mostly non-md content;
   subdirs matching common "data" / "extractions" / "generated" /
   "build" names). Prints suggested exclude list. Lower priority.
6. **Honor `.gitignore`** if present at tree root. Most real data
   dirs are already gitignored. Free signal.
7. **Surface excluded counts** in plan footer:
   `185 files excluded under <subdir>/; 47 files in plan`.

Each verb may still take a per-invocation `--exclude` to override
or extend the `.docs.toml` baseline; the default is "use the same
exclude list everywhere".

### F6 — Plan output is firehose-shaped; no triage view

Trial 1's plan was 1,376 lines. Today `--quiet` only suppresses
success messages on stderr; there's no flag to summarise, filter,
or group the plan for triage.

**M8 proposes:**

- **`--summary`** — one line per file: `path  role  conf  notes`.
  Pipes cleanly to `sort`, `uniq`, `awk`.
- **`--only ambiguous`** — hide high-confidence rows; show only
  the ones a human needs to look at.
- **`--group-by role`** / **`--group-by confidence`** — reorder
  for triage.
- **Default plan-footer summary**: counts by role, by confidence,
  by ambiguity type. Gives a 30-second read of "is this plan good
  enough to `--apply`?".

### F7 — Non-Markdown siblings are silently ignored

Trial 1's tree has 3 .html, 1 .xlsx, 1 .odt at root, all
referenced from .md files. Migrate doesn't surface them. The
convention says docs are Markdown — skipping is correct — but
surfacing is useful for adopters.

**M8 proposes:** add a plan-footer line "5 non-Markdown siblings at
root not considered: <name>, <name>, …". Surfacing only; no
action. Defer sidecar metadata to a later milestone.

### F9 — `docs new` → Write friction breaks the agent flow

**Observed in the M7 stub-authoring session.** The default agent
workflow for authoring a new doc is:

1. `docs new milestone foo` — creates `docs/foo.md` with the
   frontmatter scaffold.
2. Agent calls `Write(docs/foo.md, <full content>)` to overwrite.

Step 2 fails: the Claude Code harness requires `Read` before
`Write` on any existing file. The agent has to insert an avoidable
`Read` round trip just to satisfy the harness.

Friction is small per file but compounds across an adoption
session where an agent might author 5–10 new docs.

**M8 proposes (docs-side fixes — the harness rule is out of our
control):**

1. **`docs new <role> <slug> --body-from <path|->`** (preferred).
   docs new takes body content from a file or stdin and writes
   the complete file atomically. One Bash call:
   ```sh
   docs new milestone foo --root docs/ --body-from - <<'EOF'
   ## Overview
   ...
   EOF
   ```
   No Write, no Read-before-Write, no round trips.
2. **`docs scaffold <role> <slug>`** — sibling verb that PRINTS
   the template to stdout without creating a file. Agent uses
   Write (file doesn't exist yet, so Read isn't required) with
   the printed template + body composed together.
3. **Skill guidance** in `references/adoption-playbook.md`
   teaches the agent-native pattern.

Recommendation: ship #1 + #3. #2 is optional belt-and-braces.

Out of scope for M8 to fix the harness side. Docs' job is to
give agents a one-call shape that doesn't trip the rule.

### F8 — Skill references don't cover the adoption flow

The bundled skill (M5, polished in M6) targets greenfield use:
"you want to create a new spec — run `docs new`". The adoption
flow ("you just arrived at a foreign tree — what do you do?") is
absent from `SKILL.md` and `references/`.

**Skill design rule (operator, 2026-05-24): keep `SKILL.md`
clean.** SKILL.md's job is to trigger reliably on the right
contexts and hand off to a reference; substantive procedure
lives in `references/`. Adoption guidance is BIG — playbook +
worked example + .docs.toml template + role-vocab hints — so it
goes entirely into `references/adoption-playbook.md`, with
SKILL.md carrying only a short trigger line + a single link.

**M8 proposes:**

- **`SKILL.md` — minimal additions** (one or two lines):
  - Extend the description with adoption trigger phrases:
    "adopt this directory", "migrate this folder", "bring this
    into docs convention", "import existing markdown specs".
  - Add a single sentence near the verb table:
    > **Adopting an existing Markdown directory?** Read
    > [references/adoption-playbook.md](references/adoption-playbook.md)
    > first.

  Nothing else. SKILL.md stays short.

- **`src/docs_cli/skill/references/adoption-playbook.md`** (new) —
  the substantial doc. Sections:
  - When this applies (you're standing in a non-conforming dir).
  - Step 1 — `docs migrate --json <dir>` to get the dry-run plan.
  - Step 2 — triage the plan (`--summary`, `--only ambiguous`),
    decide on `--exclude` patterns.
  - Step 3 — create `.docs.toml` (template at
    `references/docs-toml-template.toml`), with `[exclude] dirs`,
    `[vocabulary] add_roles`, `[migrate] role_suffixes`.
  - Step 4 — re-run migrate dry-run; iterate until clean.
  - Step 5 — `docs migrate --apply <dir>`.
  - Step 6 — verify with `docs check <dir>`.
  - Worked example: a realistic ~200-file tree end-to-end.
    Generic sanitised content — NO third-party product /
    customer / feature names.
  - Pitfalls: the prose-`Status:` → `Lifecycle:` change (per M7
    F0); the `_v2` / `_Draft` non-role suffixes (per M7 F10);
    when a subdir is actually a separate project (deferred).
  - The agent-native `docs new --body-from -` pattern (per F9).

- **`src/docs_cli/skill/references/docs-toml-template.toml`**
  (new) — pre-filled with `[exclude] dirs`, `[migrate]
  role_suffixes`, `[vocabulary] add_roles`, `[vocabulary]
  add_lifecycles`. Heavily commented so an operator can
  keep / strip / extend each block.

- **`src/docs_cli/skill/references/cli.md`** (existing) — adds
  the M8 verb sections (`docs new --body-from`, `--exclude`,
  `--summary`, `--only`, `--group-by`).

Pattern: `SKILL.md` says *when* to migrate; the playbook says
*how*. Keep growth in `references/`, not in `SKILL.md`.

## Generalisation note

The trial trees informed M8's findings; they are evidence, not
the target. The goal is agent-driveable adoption of any
real-world tree — not to overfit to the specific 25 trees that
surfaced these findings. The fresh-subagent integration gate
(Success Criteria below) tests this by handing subagents trees
the M8 author has not specifically tuned for.

## Decisions (carried forward + resolved at trial-time)

- M7 must ship first. M8 builds on M7's accurate plan.
- M6 has merged to main (2026-05-24); not yet published. M8
  builds on M6's package layout + skill bundling.
- **Tree-wide single source of truth for excludes.** `[exclude]
  dirs` in `.docs.toml` applies to `migrate` + `index` + `check`
  + `list`. Operator decision 2026-05-24.
- **SKILL.md stays clean; growth goes into `references/`.**
  Operator decision 2026-05-24.

## Open questions (for milestone-setup)

1. **OQ-A — `--propose-excludes` heuristic.** In M8 scope, or
   deferred? Recommendation: deferred. Explicit `--exclude` and
   `.docsignore` cover the immediate need.
2. **OQ-B — `.docsignore` syntax.** Subset of gitignore
   (recommended — familiar), or simpler glob list?
3. **OQ-C — M8 ship before or after M6 PyPI publish?**
   Recommendation: after. M8's skill reference updates benefit
   from landing on a shipped M6 baseline.
4. **OQ-D — Should the skill `.docs.toml.example` ship as a
   static file** (operators `cp` it into place), **or as a
   `docs init --template`** verb that materialises it? Latter is
   more agent-native but adds a new verb. Recommendation: ship
   as static file in the skill bundle; defer the verb.
5. **OQ-E — `docs new --body-from -` exit-code semantics.** If
   the body content already contains a frontmatter-shaped block,
   strip it? Refuse? Recommendation: refuse with a clear error;
   the agent should pass body-below-H1 only, since `docs new`
   owns the frontmatter.
6. **OQ-F — `docs scaffold` (F9 alt #2) — ship it or not?**
   Recommendation: skip for M8 unless the `--body-from` form
   surfaces an edge case during the fresh-subagent integration
   gate. Adding a verb is permanent surface area; defer.
7. **OQ-G — How many fresh-subagent integration runs is enough
   for the M8 ship gate?** Recommendation: 3 trees minimum
   (small / medium / large), 5 trees ideal. At least 2 of 3
   must complete without operator intervention.

## TDD Implementation Plan

Not yet expanded. Drafted at milestone-setup once OQs are
resolved.

Estimated phase shape:

- **Phase 1 — Define Contract.** Activate milestone; cli.md gets
  the new flags + `--body-from` documented; convention.md gets
  the `[exclude]` section.
- **Phase 2 — Write Tests (RED).** New
  `tests/test_exclude.py` (tree-wide application across verbs),
  `tests/test_triage_flags.py`, `tests/test_body_from.py`,
  `tests/test_skill_adoption.py` (references content + SKILL.md
  trigger discoverability).
- **Phase 3 — Create Data/Fixtures.** Reuse M7's sanitised
  Trial 2 fixtures for the exclude + triage tests. New tiny
  fixtures for body-from edge cases.
- **Phase 4 — Run Tests (RED Baseline).**
- **Phase 5 — Update Base Interfaces.** Argparse subparser
  updates; `.docs.toml` schema extension in `load_config`.
- **Phase 6 — Implement Core.** `--exclude` everywhere;
  triage flags in migrate output; `docs new --body-from`;
  the `[exclude]` config plumb-through.
- **Phase 7 — Update Wrappers.** SKILL.md one-line update; new
  `references/adoption-playbook.md`; new
  `references/docs-toml-template.toml`; cli.md sections.
- **Phase 8 — Run Tests (GREEN).** All M1–M7 + new M8 tests pass.
- **Phase 9 — Integrate (FRESH-SUBAGENT GATE).** Spawn fresh
  Opus subagents (no prior context, fresh checkout, M8-bundled
  skill only). Hand each one a different real foreign tree from
  M7's fixtures. Each must complete the adoption loop end-to-end.
  See Success Criteria for the bar.
- **Phase 10 — Quality, Docs, Refactor.** Sweep + tag M8.

## Deliverables (provisional — finalised at milestone-setup)

- `--exclude` flag on `migrate` + `index` + `check` + `list`.
- `[exclude]` section in `.docs.toml` schema + `load_config`.
- `.docsignore` parser.
- `--summary`, `--only ambiguous`, `--group-by` triage flags on
  `migrate`.
- Default plan-footer summary on `migrate`.
- Non-md sibling surface line in `migrate` footer.
- `docs new --body-from <path|->` flag.
- New `src/docs_cli/skill/references/adoption-playbook.md`.
- New `src/docs_cli/skill/references/docs-toml-template.toml`.
- One-line SKILL.md adoption pointer + trigger-phrase additions.
- Updated `src/docs_cli/skill/references/cli.md` for the new
  flags / verbs.
- New tests for each of the above.

## Success Criteria

**Quantitative — measurable from the M7 fixtures:**

- `docs migrate --exclude <data-subdir>` on Trial 1's tree
  produces ≤ 50 plan entries instead of 235.
- `docs migrate --summary` on any Trial 2 tree fits in ≤ 100
  lines.
- `docs migrate --only ambiguous` on any Trial 2 tree returns
  only files with ambiguities listed (verifiable by re-running
  without the flag and diffing).
- `docs new milestone foo --body-from -` creates a valid file
  matching `docs check`'s expectations in a single call.
- `docs check`, `docs index`, `docs list` all honour `[exclude]
  dirs` from `.docs.toml`.

**Workflow validation — dogfooded by a fresh subagent (the
load-bearing M8 success criterion):**

The ergonomic changes (F3/F6/F7/F9 + F8 skill references) are
expected to make adoption agent-driveable. **Validating that
with a fresh subagent** is the test:

1. Spawn a fresh Opus subagent — no prior conversation context,
   fresh repo checkout, only the bundled skill + the new verbs.
2. Hand it ONE foreign tree from
   `tests/fixtures/trees/real-trees/` (sanitised) and the
   prompt: "adopt this directory into the docs convention;
   commit the result".
3. The subagent should — driven solely by SKILL.md's adoption
   trigger and `references/adoption-playbook.md` — complete the
   dry-run → triage → exclude → iterate → apply → check loop
   and land a clean commit. Without operator intervention
   except for OQs the playbook tells the agent to escalate.
4. Repeat across **at least 3 of the 5–8 Trial 2 fixtures**,
   covering a range of sizes (small / medium / large) and styles
   (snake_case-heavy / kebab-case-heavy / mixed).
5. **At least 2 of 3 runs must complete without operator
   intervention.** The third may surface a genuine OQ that the
   playbook tells the agent to escalate (acceptable).
6. If a subagent stalls, that's a fail — iterate F8 / F9 / the
   playbook / SKILL.md until subagents drive it. **The skill
   and the verb are the unit under test, not the LLM.** An
   agent that can't drive the workflow is a docs-side bug.

This is more demanding than per-feature unit tests; it's the
integration gate. M8 doesn't ship until it passes.

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
- [ ] Phase 9 — Integrate (FRESH-SUBAGENT GATE)
- [ ] Phase 10 — Quality, Docs, Refactor

## Trial-run artefacts (shared with M7)

Captured 2026-05-24:

- `/tmp/m7-migrate-full.txt` — Trial 1 human-readable dry-run.
- `/tmp/m7-migrate.json` — Trial 1 JSON (235 entries).
- `/tmp/m7-trial2/ph-*.json` — Trial 2 per-tree JSON dry-runs.
- `/tmp/m7-trial2/{ideas,agents,specs}.json` — Trial 2 sibling
  dirs.

Promote to `tests/fixtures/trees/real-trees/` at M7's
milestone-setup (M8 reuses the same fixtures).
