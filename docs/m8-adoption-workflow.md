# M8 — Adoption workflow (agent-driveable)

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-05-25

Related:
- parent-of: m8-adoption-workflow-log.md
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
- Status: ACTIVE (started 2026-05-24, milestone-setup complete).
  Depends on M7 shipping first (M7's accurate plan is the
  substrate M8 makes driveable).

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

### F7 — Non-Markdown siblings (sidecars) — surface + agent-authored, no new verb

Trial 1's tree has 3 .html, 1 .xlsx, 1 .odt at root, all
referenced from .md files. Migrate doesn't surface them today.
The convention says docs are Markdown only, so skipping is
correct — but adopting agents lose the signal that the binary
is part of the tree's content surface.

**Handling — surface + sidecar-via-existing-surface, NO new
verb (lean for agent):**

1. **Surface in plan footer.** One line at the migrate plan's
   end:
   ```
   non-md siblings at root not considered:
     report-2026-05-21.html, ceo-review.xlsx, source-pack.odt
   ```
   Suppressible per-extension via `--exclude-ext xlsx,html`
   (per F3).

2. **Agent authors a sidecar when warranted**, using the
   already-shipping `docs new <role> <slug> --body-from -`
   (per F9). A sidecar is a normal Markdown doc with a
   `Related: artifact-of:` line pointing at the binary:

   ```sh
   docs new reference report-2026-05-21 --body-from - <<'EOF'
   Related:
   - artifact-of: report-2026-05-21.html

   # Report 2026-05-21

   Companion to `report-2026-05-21.html`. The HTML is the
   primary artifact; this sidecar carries the metadata
   (Lifecycle, Project, Related) the convention needs.

   See [report-2026-05-21.html](report-2026-05-21.html) for
   the rendered content.
   EOF
   ```

   The `artifact-of:` is a standard `Related:` qualifier
   shape — no new field, no schema change.

3. **Playbook teaches the decision (per F8 below).** Which
   binaries warrant a sidecar (referenced from prose;
   long-lived; would be missed if untracked) vs. which are
   noise (one-off exports; build artifacts; exclude via
   `--exclude-ext`).

**No new verb. No new flag** beyond F3's `--exclude-ext`. The
sidecar pattern is "an authoring pattern the playbook
teaches", not a tooling feature with its own implementation,
tests, and surface area.

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

- **`src/docs_cli/skill/references/adoption-playbook.md`**
  (new) — the substantial doc. Sections:
  - When this applies (you're standing in a non-conforming dir).
  - Step 1 — `docs migrate --json <dir>` to get the dry-run
    plan. **Read the footer first** — it summarises counts by
    role / confidence / ambiguity, excluded counts, M7 F5
    multi-project hints, and F7 non-md siblings.
  - Step 2 — triage the plan (`--summary`,
    `--only ambiguous`, `--group-by`); decide on `--exclude`
    patterns.
  - Step 3 — create `.docs.toml` (template at
    `references/docs-toml-template.toml`): `[exclude] dirs`
    / `globs` / `exts`, `[vocabulary] add_roles` /
    `add_lifecycles`, `[migrate] role_suffixes`,
    `[migrate] project_name` (if the inferred project name
    needs overriding).
  - Step 4 — re-run migrate dry-run; iterate until clean.
  - Step 5 — `docs migrate --apply <dir>`.
  - Step 6 — verify with `docs check <dir>` exit 0.
  - Worked example: a realistic ~200-file tree end-to-end.
    Generic sanitised content — NO third-party product /
    customer / feature names.
  - **Multi-project trees (handling M7 F5 hints).** A
    subsection walking the "this subdir looks like a separate
    project" hint. Decision tree:
    1. **Ignore** — parent project is correct.
    2. **Exclude + recurse** — `--exclude <subdir>/` on the
       parent; then `docs migrate <tree>/<subdir>
       --config-project <name>` separately, producing two
       plans the agent applies independently.
    3. **Override parent project** — `docs migrate
       --config-project <name>` for the single run when the
       inferred name is wrong but the structure is right.

    Worked sub-example showing the recurse pattern across 2
    sub-projects in one parent tree.
  - **Sidecars for non-md siblings (handling F7).**
    Subsection walking: when a binary referenced from prose
    warrants a sidecar (long-lived, meaningfully tracked,
    needs Lifecycle / Project / Related metadata); how to
    author one with `docs new <role> <slug> --body-from -`
    (per F9); the `Related: artifact-of: <binary>` shape
    that ties the sidecar to its artifact. When NOT to
    author one (one-off exports, build artifacts —
    `--exclude-ext` them instead).
  - Pitfalls: prose-`Status:` → `Lifecycle:` (per M7 F0);
    `_v2` / `_Draft` non-role suffixes (per M7 F10);
    inferred project name needs override (per M7 F5 + F11);
    generated-data dirs need `--exclude` (per F3).
  - The agent-native `docs new --body-from -` pattern (per
    F9) — single Bash call to author a full doc, no Read
    round trip.

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

## Decisions (carried forward + resolved at milestone-setup, 2026-05-24)

### Carried forward

- **M7 must ship first.** M8 builds on M7's accurate plan; M8
  Phase 9 (the fresh-subagent gate) only meaningfully passes
  once M7's confidence-distribution improvements have landed.
- M6 has merged to `main` (2026-05-24); not yet published. M8
  builds on M6's package layout + skill bundling.
- **Tree-wide single source of truth for excludes.** `[exclude]
  dirs` in `.docs.toml` applies to `migrate` + `index` + `check`
  + `list`. Operator decision 2026-05-24.
- **SKILL.md stays clean; growth goes into `references/`.**
  Operator decision 2026-05-24.

### OQ-A resolved — `--propose-excludes` heuristic

**Deferred.** Out of M8 scope. Explicit `--exclude` flag +
`[exclude] dirs` in `.docs.toml` + `.docsignore` file cover the
immediate need. Auto-detection of generated-data subdirs
(heuristic: subdirs with >N files sharing a suffix pattern;
subdirs with mostly non-md content; subdirs matching common
"data" / "extractions" / "generated" / "build" names) is a
plausible follow-up milestone — surface as a parked question
in plan.md if it survives M8 fresh-subagent runs as a
recurring pain point.

### OQ-B resolved — `.docsignore` syntax

**Subset of gitignore syntax.** Familiar to every developer;
implementations exist (the convention can lean on the existing
`pathspec`-style logic without adding a dependency — implement
the minimal subset directly in stdlib). Specifically:

- One pattern per line.
- `#` starts a comment (rest of line ignored).
- Blank lines ignored.
- `**` matches any number of path segments.
- `*` matches anything except `/`.
- Trailing `/` means directory-only match.
- Leading `/` anchors at the tree root.
- `!` for negation (re-include) — supported but rare in
  practice.

Full gitignore semantics (e.g. nested `.gitignore` files,
the directory-walk-pruning optimization) are NOT replicated —
docs trees are small enough that walking everything and
filtering is fine.

### OQ-C resolved — Publish timing (operator decision, 2026-05-24)

**Publish is deferred until after M8 — possibly further,
pending review cycles.** No per-milestone publish. The first
PyPI publish ships the M6 + M7 + M8 surface as one artifact
(version `1.3.0` — the M8 bump), via the existing
`release-runbook.md` manual `twine upload` flow.

Implications for M8:

1. M8 Phase 9 (the fresh-subagent gate) tests against a
   **locally-installed** wheel, not `pip install docs-cli`
   from PyPI. Subagents do
   `pip install /home/user/opt/docs-cli/dist/docs_cli-1.3.0-py3-none-any.whl`
   into a throwaway venv (equivalent UX; same artifact).
2. M8 Phase 10's publish step is **deferred** rather than
   executed. The Phase 10 log entry records "ready to
   publish; awaiting operator review cycle".

Practical sequence (revised): **M7 ship → M8 ship → operator
review → (eventually) batched publish of 1.3.0.** Skipping
1.1.0 and 1.2.0 on PyPI is a no-op because there's no prior
public release — the first published version simply IS 1.3.0.

### OQ-D resolved — `.docs.toml.example` ship form

**Static file in the skill bundle.** Ships as
`src/docs_cli/skill/references/docs-toml-template.toml`.
Operators `cp` it into place at adoption time. The skill's
`adoption-playbook.md` points at it explicitly.

A `docs init --template` verb that materialises it
programmatically is plausible but adds permanent CLI surface
for a one-shot operation — defer to a later milestone unless
the fresh-subagent runs surface a real pain point with `cp`.

### OQ-E resolved — `docs new --body-from` body-with-frontmatter behavior

**Refuse with a clear error.** If the body content piped to
`--body-from -` (or read from `--body-from <path>`) starts
with what looks like a metadata block (any line in the first
20 lines matching `^[A-Z][A-Za-z-]+:\s`), exit with:

```
docs: --body-from content appears to contain a metadata block.
      Pass body content only — `docs new` owns the frontmatter.
      Stripped first 5 lines: <preview>
```

Exit code 2 (operator-correctable input error, parallel to
existing CLI conventions).

Rationale: stripping would mask agent bugs; refusing forces
the agent to learn the correct shape. The clear error message
lets the agent self-correct in the next call.

### OQ-F resolved — `docs scaffold` sibling verb: skip

`--body-from` covers the need. No new verb. If a Phase 9
subagent run surfaces a genuine `--body-from` gap, document
it in the Phase 9 log and revisit post-M8.

### OQ-G resolved — Fresh-subagent integration gate threshold

**3 trees minimum; 5 trees ideal. At least 2 of 3 must
complete without operator intervention.** Trees selected to
span size + style:

- 1 small kebab-case tree (~5 files) — quick sanity check.
- 1 medium snake_case TitleCase tree (~30 files) — dominant
  real-world shape.
- 1 large mixed tree (~70+ files, possibly with an
  `archived/` subdir) — scale + edge-case stress.

The third may surface a genuine OQ the playbook tells the
agent to escalate (acceptable — that's the playbook working
as designed). If a subagent stalls on something the playbook
doesn't anticipate, that's a fail: iterate F8 / F9 / the
playbook / SKILL.md before re-running. **The skill and the
verb are the unit under test, not the LLM.**

If runs against 5 trees are practical (cost / time
permitting), run 5 — broader coverage of edge cases. The
floor is 3.

## Open questions

_All seven milestone-setup OPEN QUESTIONS are resolved
2026-05-24, recorded as Decisions above. No new questions
surfaced during setup._

## TDD Implementation Plan

The ten phases follow the methodology in
[status.md](status.md). Because M8's load-bearing test is the
**fresh-subagent integration gate at Phase 9** — not the unit
suite — the earlier phases bias toward making the unit surface
small and the skill references rich.

### Phase 1: Define Contract

- **Objective:** Promote this milestone from `draft` to `active`
  (already done at milestone-setup, 2026-05-24); create the log
  skeleton; record OQ A–G resolutions as Decisions (done);
  refresh status.md's "Current milestone" and "Next action" to
  point at Phase 2. No code change; no convention edits yet
  (those land at Phase 5 / Phase 7 to keep the contract phase
  reviewable in isolation).
- **Files (text/docs work):**
  - `docs/m8-adoption-workflow.md` — `Status: draft` → `active`
    (done); `Updated:` bumped; Decisions populated with OQ A–G
    resolutions (done).
  - `docs/m8-adoption-workflow-log.md` — created with the
    M5/M6/M7 log skeleton.
  - `docs/status.md` — "Current milestone" rewritten to note
    M8 setup complete + Phase 2 next; M8 row flipped from
    "stub drafted" to "in flight (Phase 1 complete, blocked on
    M7 ship)".
  - `docs/plan.md` — already lists M8 (committed `1df6ec6`); no
    further edit beyond the touch.
  - `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
    regenerated in lockstep so the new log appears.
- **Exit:** M8 is `active`; log exists; status.md reflects
  Phase 1 complete; tests still GREEN (M7's count, whatever it
  is at the time); ruff/format/mypy clean; `docs check docs/`
  exit 0; INDEX snapshot matches. No code change. No convention
  change.

### Phase 2: Write Tests (RED)

- **Objective:** Express every M8 requirement (F3/F6/F7/F8/F9)
  as a failing check before any implementation. Tests collect
  cleanly; every new assertion fails for the intended reason.
- **New test files:**
  - `tests/test_exclude.py` (F3). Asserts:
    1. `docs migrate --exclude <subdir>/` skips files under that
       subdir in the migration plan.
    2. `--exclude` is repeatable: `--exclude a --exclude b`
       skips both.
    3. `--exclude` accepts glob patterns: `--exclude '**/data/**'`,
       `--exclude '*memo*'`.
    4. `docs migrate --exclude-ext xlsx,html` skips files with
       those extensions (when surfaced — see F7).
    5. `[exclude] dirs = [...]` in `.docs.toml` applies
       **tree-wide**: `docs index`, `docs check`, `docs list`
       all honour it. One test per verb (4 tests).
    6. `[exclude] globs = [...]` in `.docs.toml` also honoured
       tree-wide.
    7. `.docsignore` at the tree root is parsed with the
       gitignore-subset syntax from OQ-B; honoured tree-wide.
       Specific cases: pattern `*.tmp`, pattern `data/`,
       pattern `/specific.md`, pattern `**/build/**`, comment
       lines, blank lines, negation `!keep-me.md`.
    8. CLI `--exclude` flag layers ON TOP of `.docs.toml` +
       `.docsignore` baseline (doesn't replace).
    9. Plan footer surfaces excluded count:
       `"185 files excluded under <subdir>/"`.
  - `tests/test_triage_flags.py` (F6). Asserts:
    1. `--summary` produces one line per file with
       `path  role  conf  notes` shape.
    2. `--only ambiguous` returns only files with at least one
       ambiguity in the JSON output; diffable against an
       unflagged run.
    3. `--group-by role` orders the plan output by role.
    4. `--group-by confidence` orders by confidence (high →
       medium → low).
    5. Default plan footer (no flag) shows counts by role +
       confidence + ambiguity type.
    6. `--summary` and `--only ambiguous` compose:
       `--summary --only ambiguous` works.
  - `tests/test_non_md_surfacing.py` (F7). Asserts:
    1. A tree with N non-md siblings at root surfaces a footer
       line listing them: `"5 non-Markdown siblings at root not
       considered: <names>"`.
    2. The footer line appears only when N > 0.
    3. `--exclude-ext` (from test_exclude.py) suppresses the
       footer line for those extensions.
  - `tests/test_body_from.py` (F9). Asserts:
    1. `docs new milestone foo --body-from -` reads stdin and
       writes the complete file in one call.
    2. `docs new milestone foo --body-from <path>` reads from a
       file.
    3. Output file matches the same shape as the
       scaffold-then-Write pattern (golden comparison).
    4. **OQ-E enforcement**: body content containing what looks
       like a metadata block (any line in first 20 matching
       `^[A-Z][A-Za-z-]+:\s`) → exit 2 with the documented
       error message + preview.
    5. `--body-from` without a value → argparse error.
    6. `--body-from <nonexistent-path>` → exit 2 with a
       file-not-found error.
    7. Idempotency: running twice with the same body content
       and the same slug → second call exits 2 (file exists),
       no overwrite. Same as current `docs new` semantics.
  - `tests/test_skill_adoption.py` (F8). Asserts:
    1. `src/docs_cli/skill/SKILL.md` description contains at
       least 3 of the adoption trigger phrases ("adopt this
       directory", "migrate this folder", "bring this into
       docs convention", "import existing markdown specs").
    2. `SKILL.md` contains the literal one-line pointer:
       `"**Adopting an existing Markdown directory?** Read"`
       + a link to `references/adoption-playbook.md`.
    3. `src/docs_cli/skill/references/adoption-playbook.md`
       exists with required H2 sections: "When this applies",
       "Step 1", through "Step 6", "Worked example",
       "Pitfalls".
    4. `src/docs_cli/skill/references/docs-toml-template.toml`
       exists and parses as valid TOML.
    5. The template contains `[exclude]`, `[migrate]`,
       `[vocabulary]` sections with at least one commented
       example each.
    6. M5's existing lockstep test
       (`tests/test_skill_refs.py`) still passes — the
       references/{convention,cli}.md byte-identity holds.
- **Extensions:**
  - `tests/test_migrate.py` — keep, extend. Add a test that
    `--summary --json` is rejected (mutually exclusive).
- **Exit:** every new test file collects cleanly; every new
  test fails or errors on the intended unimplemented surface.
  M7's full suite stays GREEN.

### Phase 3: Create Data/Fixtures

- **Objective:** Stage the fixtures the new tests reference.
  Reuse M7's sanitised real-trees fixtures heavily; new
  fixtures only for body-from edge cases and exclude tests.
- **Fixtures to add:**
  - `tests/fixtures/body-from/with-frontmatter.txt` — body
    content starting with `Owner: Foo` and similar lines (the
    OQ-E refusal case).
  - `tests/fixtures/body-from/clean-body.md` — body content
    with no metadata-shaped lines (the happy path).
  - `tests/fixtures/body-from/edge-case-keyword.md` — body
    containing a line like `Plan: stage one then stage two`
    (false-positive risk for the metadata-block detector).
    This test verifies the heuristic doesn't over-trigger.
  - `.docsignore` syntax cases and small synthetic
    `[exclude]`-bearing trees are written **inline via
    `tmp_path`** by the Phase-2 tests themselves (see the
    `_write(root / ".docsignore", ...)` pattern in
    `tests/test_exclude.py`). No on-disk fixture directory is
    staged for these — the inline tmp_path approach is the
    established convention in this codebase and was the
    delivered shape at Phase 3 close-out.
- **Reuse from M7:**
  - All 5 real-trees fixtures (kebab-tiny, snake-medium,
    snake-large, archive-subdir, mixed-naming) for the
    triage-flag tests and the Phase 9 fresh-subagent gate.
- **Exit:** every fixture path the new tests reference exists;
  RED baseline (Phase 4) failures trace to unimplemented
  surface, not missing fixtures.

### Phase 4: Run Tests (RED Baseline)

- **Objective:** Confirm the new RED tests fail for intended
  reasons; pin failure modes in the log.
- **Actions:**
  ```sh
  .venv/bin/python -m pytest tests/ -q --tb=short 2>&1 | tee /tmp/m8-phase-4-baseline.txt
  .venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
  .venv/bin/docs check docs/
  ```
- **Expected RED matrix:**

  | Test group | Failure mode | Root cause |
  |---|---|---|
  | F3 exclude (9 tests) | `argparse` errors on `--exclude`; KeyError on `[exclude]`; FileNotFoundError on `.docsignore` parse | Flag + config + ignore-file unimplemented |
  | F6 triage flags (6 tests) | argparse errors on `--summary` / `--only` / `--group-by`; default footer absent | Flags unimplemented |
  | F7 non-md surfacing (3 tests) | Plan footer doesn't include the non-md line | Surfacing logic unimplemented |
  | F9 body-from (7 tests) | argparse errors on `--body-from` | Flag unimplemented |
  | F8 skill adoption (6 tests) | AssertionError on SKILL.md content; FileNotFoundError on adoption-playbook.md / docs-toml-template.toml | Skill references not written yet |

- **Aggregate expected:** M7's full suite + ~31 new RED.
  M7's quality gate stays clean.
- **Exit:** Phase-4 log entry captures the verbatim baseline;
  every RED traces to the intended unimplemented surface.

### Phase 5: Update Base Interfaces

- **Objective:** Schema + argparse + config plumbing changes.
  No business logic yet (that's Phase 6).
- **`src/docs_cli/cli.py` changes:**
  - `Config` schema extension:
    - Add `Config.exclude_dirs: tuple[str, ...]`.
    - Add `Config.exclude_globs: tuple[str, ...]`.
    - Add `Config.exclude_exts: tuple[str, ...]`.
    - Add `Config.docsignore_patterns: tuple[Pattern, ...]`
      (parsed at load time from `.docsignore` if present).
  - `load_config` reads `[exclude]` table from `.docs.toml`:
    `dirs`, `globs`, `exts`. Reads `.docsignore` from the tree
    root if present; parses with the OQ-B subset.
  - New helper `compile_exclude_predicate(config, cli_excludes)
    -> Callable[[Path], bool]` returns a single predicate
    combining config + CLI overrides. The predicate is the
    one place every verb consults; no duplicated logic.
  - Argparse — add identical `--exclude` action to each of
    `migrate`, `index`, `check`, `list` subparsers
    (repeatable, glob-supporting). Add `--exclude-ext` to
    `migrate` (per F7's interaction).
  - Argparse — add `--summary`, `--only` (with choices
    `ambiguous`), `--group-by` (with choices `role`,
    `confidence`) to `migrate`.
  - Argparse — add `--body-from <path|->` to `new`. Mutually
    exclusive with positional body args (currently there are
    none, so just additive).
  - Argparse — `--summary` and `--json` on `migrate` are
    mutually exclusive (argparse enforces).
- **Exit:** type-check passes; `docs migrate --help`,
  `docs index --help`, etc. show the new flags; tests still
  RED for behaviour but argparse errors gone (a few tests
  flip from argparse-error RED to assertion RED — which is
  forward progress).

### Phase 6: Implement Offline/Core Path

- **Objective:** Make every F3/F6/F7/F9 test GREEN. F8 lands
  at Phase 7 (skill references are tool/wrapper layer).
- **`src/docs_cli/cli.py` changes:**
  - `_iter_doc_paths` (the tree walker used by every verb)
    consults the exclude predicate. Honours config + CLI
    overrides + `.docsignore`. Counts excluded files for the
    footer.
  - `migrate_plan` honours the exclude predicate; emits the
    excluded-count + non-md-sibling footer lines.
  - `_render_migrate_plan` (human output):
    - `--summary` mode: one line per file
      (`path  role  conf  notes` formatted columns).
    - `--only ambiguous` mode: filter out entries with no
      ambiguities.
    - `--group-by role` / `--group-by confidence`: sort
      entries before render.
    - Default footer: counts by role + confidence + top
      ambiguity types (re-uses M7's confidence enum).
  - Non-md sibling surfacing: at the root of the migrated
    tree (and root only, not recursive), enumerate non-md
    files; emit footer line if any. Suppressed by
    `--exclude-ext` for the suppressed extensions.
  - `_cmd_new` handles `--body-from`:
    - `-` reads stdin to EOF.
    - `<path>` reads the file (exit 2 if missing).
    - Apply OQ-E heuristic: scan first 20 lines; if any
      matches `^[A-Z][A-Za-z-]+:\s` → exit 2 with the
      documented error + preview of first 5 lines.
    - Otherwise: scaffold the frontmatter as usual, then
      append the body content under the H1. Single
      atomic write.
  - `.docsignore` parser: minimal OQ-B subset. ~60 lines
    of code. Unit tests in `test_exclude.py` cover every
    syntax case.
- **Exit:** F3/F6/F7/F9 tests all GREEN; M7 quality gate
  stays clean; `docs check docs/` exit 0; ruff/format/mypy
  clean tree-wide.

### Phase 7: Update Tool/Wrapper Layer (the skill rewrite)

- **Objective:** The F8 work — write the adoption playbook
  + `.docs.toml` template; minimal SKILL.md additions;
  resync references; bump version; CHANGELOG.
- **`src/docs_cli/skill/SKILL.md`** (minimal additions only):
  - Description extension: add adoption triggers ("adopt
    this directory", "migrate this folder", "bring this
    into docs convention", "import existing markdown
    specs"). Append to existing description; don't replace.
  - Single new sentence near the verb table:
    > **Adopting an existing Markdown directory?** Read
    > [references/adoption-playbook.md](references/adoption-playbook.md)
    > first.

  Nothing else. SKILL.md must stay short (the F8 rule).
  The test_skill_adoption.py assertions enforce this — if
  SKILL.md balloons, the test fails on size or shape.
- **`src/docs_cli/skill/references/adoption-playbook.md`**
  (new — the substantial doc):
  - Frontmatter (Status / Role / Project / Updated /
    Related).
  - `## When this applies` — you're standing in a
    non-conforming dir.
  - `## Step 1 — `docs migrate --json <dir>`` — get the
    dry-run plan; pipe to `jq` for inspection.
  - `## Step 2 — Triage the plan` — `--summary`,
    `--only ambiguous`, `--group-by`. Decide on
    `--exclude` patterns.
  - `## Step 3 — Create `.docs.toml`` — point at
    `references/docs-toml-template.toml`. Fill in
    `[exclude] dirs`, `[vocabulary] add_roles`,
    `[migrate] role_suffixes` per the tree's shape.
  - `## Step 4 — Iterate` — re-run migrate dry-run; tune
    excludes / config; repeat until plan is clean.
  - `## Step 5 — `docs migrate --apply <dir>``.
  - `## Step 6 — Verify` — `docs check <dir>` exit 0.
  - `## Worked example` — a realistic ~200-file tree
    end-to-end. Generic sanitised content — NO third-party
    product / customer / feature names. Sourced from the
    M7 fixtures.
  - `## Pitfalls`:
    - The `Status:` → `Lifecycle:` rename (M7 F0).
    - `_v2` / `_Draft` non-role suffixes (M7 F10).
    - When a subdir is actually a separate project (defer
      to a future milestone).
    - The agent-native `docs new --body-from -` pattern
      (this milestone's F9).
- **`src/docs_cli/skill/references/docs-toml-template.toml`**
  (new — the operator template):
  ```toml
  # Project identity
  # [project]
  # name = "my-project"

  # File exclusion (tree-wide — applies to migrate, index,
  # check, list). Each verb may extend with --exclude on
  # the command line.
  [exclude]
  dirs = [
      # "generated",
      # "build",
      # "node_modules",
  ]
  globs = [
      # "**/*.draft.md",
  ]
  exts = [
      # "xlsx",
      # "html",
  ]

  # Migration-time role inference extensions
  [migrate]
  role_suffixes = {
      # "-rubric" = "template",
      # "-memo" = "notes",
  }
  # project_name = "my-project"  # override the inferred name

  # Controlled-vocab extensions
  [vocabulary]
  add_roles = [
      # "explainer",
  ]
  add_lifecycles = [
      # "experimental",
  ]
  ```
  Heavy comments; every block has at least one commented
  example so an operator can keep / strip / extend each.
- **Spec updates:**
  - `docs/cli.md` — add `--exclude`, `--summary`, `--only`,
    `--group-by`, `--exclude-ext`, `--body-from` synopses
    + examples. The plan-footer shape documented.
  - `docs/convention.md` — `[exclude]` table documented;
    `.docsignore` syntax subset documented; pointer to the
    adoption playbook.
  - `docs/architecture.md` — `Config` schema illustration
    updated with the new exclude fields.
  - `README.md` — adoption-flow section near the top:
    `pip install docs-cli && docs install-skill`,
    then point at the skill (which points at the
    playbook). 5-line addition.
  - `CHANGELOG.md` — new `## 1.3.0 — UNRELEASED` section
    with M8 deliverables called out.
  - `pyproject.toml` + `cli.py` `__version__` bump
    `1.2.0` → `1.3.0`.
- **Skill-refs lockstep:**
  - `src/docs_cli/skill/references/convention.md` and
    `references/cli.md` — resynced from `docs/` via the
    M5/M6 mechanism. The new `adoption-playbook.md` and
    `docs-toml-template.toml` are NOT mirrored from `docs/`
    — they live only in the skill bundle.
- **INDEX regenerated; fixture snapshot updated.**
- **Exit:** F8 tests GREEN; `test_skill_refs.py` still
  passes; SKILL.md stays ≤ ~90 lines (M5/M6 baseline +
  ~5 line adoption pointer); ruff/format/mypy clean;
  `docs check docs/` exit 0.

### Phase 8: Run Tests (GREEN)

- **Objective:** Capture the full GREEN gate verbatim. M7's
  count + M8's ~31 new tests.
- **Actions:**
  ```sh
  .venv/bin/python -m pytest tests/ -q
  .venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
  .venv/bin/docs check docs/
  .venv/bin/docs index --root docs/ --dry-run
  .venv/bin/python -m build --outdir /tmp/m8-phase-8-build
  ```
- **Exit:** every command exit 0; Phase 8 log captures
  verbatim output. STOP if anything RED.

### Phase 9: Implement Online/Integration — **FRESH-SUBAGENT GATE**

- **Objective:** The load-bearing test of M8. M8 doesn't
  ship until fresh subagents demonstrably drive the
  adoption loop end-to-end against trees they haven't seen.
  This is more demanding than per-feature unit tests; it's
  the integration gate per OQ-G.
- **Setup:**
  - Per OQ-G: spawn 3 subagents minimum, 5 ideal.
  - Each subagent is fresh Opus with no prior conversation
    context.
  - Each gets a different M7 fixture tree:
    - Subagent 1: `tests/fixtures/trees/real-trees/kebab-tiny/`
    - Subagent 2: `tests/fixtures/trees/real-trees/snake-medium/`
    - Subagent 3: `tests/fixtures/trees/real-trees/snake-large/`
      (or `mixed-naming/`).
  - Each is invoked with the bundled skill installed
    (`docs install-skill --dest <agent-skill-dir>`).
  - The conductor (this session, when actually executing
    M8) hands each subagent the prompt:
    > "I want to adopt the directory at <fixture-path> into
    > the docs convention. Walk the workflow end-to-end and
    > commit the result."

    Nothing else. No hints, no `.docs.toml` pre-filled, no
    walkthrough. The subagent reads SKILL.md, follows the
    pointer to `references/adoption-playbook.md`, drives
    the loop.
- **Pass criteria (per OQ-G):**
  - At least 2 of 3 subagents complete the full loop
    (dry-run → triage → exclude → iterate → apply →
    `docs check` exit 0 → commit) without operator
    intervention.
  - The third may escalate ONE OQ to the operator (the
    playbook tells the agent which OQs are operator-only;
    that's the playbook working as designed).
  - If a subagent stalls on something the playbook doesn't
    anticipate — that's a fail. **Iterate F8 / F9 / the
    playbook / SKILL.md until subagents drive it.** The
    skill and the verb are the unit under test, not the
    LLM.
- **Documentation:**
  - Each subagent run logged in the Phase 9 log entry:
    invocation, transcript summary (the conductor's view
    of the subagent's tool calls), pass/fail, time-to-
    completion, any unexpected behaviour.
  - If a run fails, the playbook iteration is also
    recorded — what was missing, what was added, did a
    re-run pass.
- **Out-of-scope (operator-driven, not part of the gate):**
  - Network publishes (PyPI). M8 ships as 1.3.0 with the
    same manual-twine flow as M6.
- **Exit:** OQ-G threshold met (≥ 2 of 3 unattended); each
  fixture has a committed adopted state under
  `tests/fixtures/trees/real-trees-adopted/` (separate
  directory; doesn't overwrite the unadopted fixtures); the
  Phase 9 log records every run with full attribution.

### Phase 10: Quality, Docs, Refactor

- **Objective:** Polish + ship. Sweep dogfood consistency;
  append milestone-completion summary; tag `v1.3.0`;
  (operator-driven) publish.
- **Actions:**
  - Sweep this project's own `docs/` for any stale
    references to M8-era APIs that didn't match the final
    shape.
  - Append "Milestone-completion summary" to
    `docs/m8-adoption-workflow.md` (mirror M6/M7 summary
    shape).
  - Update `docs/status.md`: M8 → Complete (DATE);
    milestone table row flipped; "Next action" rewritten.
  - Update `CHANGELOG.md`: replace `## 1.3.0 — UNRELEASED`
    with the actual ship date.
  - `docs index --root docs/`; copy onto fixture.
  - Final quality gate: pytest GREEN; ruff/format/mypy
    clean; `docs check docs/` exit 0.
  - **Publish: STILL DEFERRED** per OQ-C, pending operator
    review cycles. M8 Phase 10 builds the artifact locally
    (`python -m build` → `dist/docs_cli-1.3.0-*`) and runs
    `twine check` to confirm it's PyPI-clean, but does NOT
    upload, does NOT tag, does NOT create a GitHub release.
    The Phase 10 log entry records "ready; awaiting operator
    review → batched publish".
  - The first PyPI publish ships **1.3.0** (the M8 version —
    M6 set 1.1.0, M7 bumped to 1.2.0, M8 to 1.3.0; the
    intermediate versions never see PyPI, which is fine —
    no prior public release exists). Flow when the operator
    decides to publish: `gh repo edit ArtRichards/docs-cli
    --visibility public --accept-visibility-change-consequences`
    → `twine upload --repository testpypi dist/*` + smoke →
    `twine upload dist/*` → `git tag v1.3.0 && git push
    origin v1.3.0` → `gh release create v1.3.0`. Runbook at
    `docs/release-runbook.md` is the operator's reference.
- **Exit:** M8 task plan + log carry completion summaries;
  status.md reflects M8 → Complete + "ready for operator
  review → batched publish"; CHANGELOG dated;
  `dist/docs_cli-1.3.0-*` built locally + `twine check`
  clean; **no publish, no tag, no GitHub release**; the
  Phase 9 gate is the load-bearing record that adoption is
  agent-driveable.

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

- [x] Phase 1 — Define Contract
- [x] Phase 2 — Write Tests (RED)
- [x] Phase 3 — Create Data/Fixtures
- [x] Phase 4 — Run Tests (RED Baseline)
- [x] Phase 5 — Update Base Interfaces
- [x] Phase 6 — Implement Core
- [x] Phase 7 — Update Wrappers
- [x] Phase 8 — Run Tests (GREEN)
- [x] Phase 9 — Integrate (FRESH-SUBAGENT GATE) — with caveat
      (same-instance dogfood substitution; see Phase 9 log)
- [x] Phase 10 — Quality, Docs, Refactor

## Trial-run artefacts (shared with M7)

Captured 2026-05-24:

- `/tmp/m7-migrate-full.txt` — Trial 1 human-readable dry-run.
- `/tmp/m7-migrate.json` — Trial 1 JSON (235 entries).
- `/tmp/m7-trial2/ph-*.json` — Trial 2 per-tree JSON dry-runs.
- `/tmp/m7-trial2/{ideas,agents,specs}.json` — Trial 2 sibling
  dirs.

Promote to `tests/fixtures/trees/real-trees/` at M7's
milestone-setup (M8 reuses the same fixtures).

## Milestone-completion summary

**Shipped:** 2026-05-25 (locally as 1.3.0; PyPI publish
DEFERRED to M9 batched 1.3.0 per OQ-C).

**Surface delivered:**

- **F3 — tree-wide exclusion.** `--exclude PATTERN`
  (repeatable, gitignore-flavoured) on `migrate` / `index` /
  `check` / `list`; `[exclude]` table in `.docs.toml` (dirs /
  globs / exts); root `.docsignore` parser (OQ-B subset);
  layered additively, single `compile_exclude_predicate`
  consulted by every walker. Plan footer surfaces excluded
  counts per top-level dir prefix.
- **F6 — triage flags.** `--summary` (one tabular line per
  file; mutually exclusive with `--json`), `--only ambiguous`,
  `--group-by role|confidence`. Default plan footer summary
  with four anchored tokens (`summary:` / `roles:` /
  `confidence:` / `ambiguities:`) always present.
- **F7 — non-md sibling surfacing.** Plan footer line
  `<N> non-Markdown siblings at root not considered: <names>`
  for the migration root; suppressed entirely when the
  displayed list is empty (after `--exclude-ext` filtering).
- **F8 — substantial skill-reference rewrite.** New
  `references/adoption-playbook.md` (343 lines; six-step
  procedural deep-dive + worked example + pitfalls); new
  `references/docs-toml-template.toml` (~90 lines; commented
  starter for `[exclude]` / `[migrate]` / `[vocabulary]`);
  minimal SKILL.md additions (4 adoption-trigger phrases + a
  one-line pointer block, M7 misses swept).
  `_SKILL_RELATIVE_FILES` extended with `use-cases.md` +
  the two new files; this closes a pre-existing packaging
  gap where `use-cases.md` shipped in the wheel but
  `install-skill --copy` never landed it on a host.
- **F9 — `docs new --body-from <PATH|->`.** Reads body
  content from a file or stdin and appends it under the
  scaffolded frontmatter. Atomic, one Bash call. OQ-E
  conservative refusal heuristic: first 20 body lines
  scanned for `^[A-Z][A-Za-z-]+:\s`; refused with exit 2
  + documented error message when any line matches.
- **Carve-out widening (OQ1).** `docs migrate` accepts a
  managed-marker `.docs.toml` when `[exclude]` is also
  present — the operator's explicit signal "use migrate to
  triage / re-migrate this tree but skip the listed paths".

**Tests:** Started at 324 M7 GREEN; 45 new collected items at
Phase 2 (41 RED + 4 baseline-GREEN regression locks). **369
GREEN at Phase 8 (all M8 RED flipped GREEN).** Quality gate
clean: ruff / ruff-format / mypy / `docs check docs/` / `docs
index --dry-run` / `python -m build` / `twine check` all exit
0.

**Fresh-subagent gate (Phase 9):** **3/3 PASS — but as a
same-instance dogfood pass rather than fresh subagents (the
agent-spawning tool the plan specified is not available in
this execution environment).** Run 1 (kebab-tiny, 3 files)
failed on the first pass and surfaced a real playbook bug
(Step 3 / Step 5 / Step 6 ordering); iterated the playbook
and re-ran cleanly. Run 2 (snake-medium, 17 files) and Run 3
(snake-large, 72 files) passed unattended. Adopted state
committed to `tests/fixtures/trees/real-trees-adopted/
{kebab-tiny,snake-medium,snake-large}/`. **OPERATOR REVIEW
POINT** — the same-instance vs fresh-subagent distinction is
documented in detail in the Phase 9 log entry.

**Ship surface:** Local artefacts in `dist/`
(`docs_cli-1.3.0-py3-none-any.whl` +
`docs_cli-1.3.0.tar.gz`; `twine check` PASSED on both).
**NO publish, NO git tag, NO GitHub release** — per OQ-C the
PyPI publish is M9's scope.

**Open follow-ons:**

- The true fresh-subagent Phase 9 verification (if the
  operator chooses option 2 from the Phase 9 log's OPERATOR
  REVIEW POINT).
- Auto-`--propose-excludes` heuristic (OQ-A); the playbook
  steps the operator through hand-authoring `[exclude]`
  today, but a future enhancement could surface candidate
  dirs/globs from the dry-run itself.
- `docs scaffold` sibling verb (OQ-F) if a later use case
  surfaces a `--body-from` gap.
- Per-tree `.docsignore` nesting (rejected at M8 per OQ-B);
  reopen only if a real-tree adoption demands it.
