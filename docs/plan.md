# docs — Implementation Plan

Lifecycle: active
Role: plan
Project: docs
Updated: 2026-05-27

Related:
- implements: charter.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: status.md
- parent-of: m1-parser-and-index.md
- parent-of: m7-migration-accuracy.md
- parent-of: m8-adoption-workflow.md
- parent-of: m9-pypi-publish.md

## Sequencing

Three milestones to v1, then a migration helper, then a Claude Code
skill wrapper. v1.1 picks up with packaging, then migration
hardening + adoption workflow.

```
v1:    M1 (parser + index)  →  M2 (mutating verbs)  →  M3 (validation + JSON)  →  M4 (migrate)  →  M5 (skill)
v1.1:  M6 (PyPI distribution prep)  →  M7 (migration accuracy)  →  M8 (adoption workflow)  →  M9 (PyPI publish 1.3.0)
```

## M1 — Parser, walker, and `docs index`

Goal: read the convention reliably and produce a usable INDEX.md.

- Parse a single Markdown file into `{title, status, role, project, updated, related, extra_fields, body}`.
- Walk a docs root, skipping anything that isn't `.md` and isn't under a configured ignore pattern.
- Implement `docs index` with the marker-block strategy. Idempotent output.
- `.docs.toml` loading (TOML via stdlib `tomllib`, Python 3.11+).
- Smoke test against `~/opt/docs/docs/` itself — running `docs index` here should reproduce the hand-written INDEX.md byte-for-byte (or close enough that the diff is review-able).

Exit criteria: hand-written INDEX.md matches generated output on this repo. M1 unblocks every later milestone because they all need the parser.

## M2 — Mutating verbs: `new`, `archive`, `mv`, `touch`

Goal: stop hand-editing metadata.

- `docs new <role> <slug>` writes a scaffolded file with correct metadata block.
- `docs archive <file>` does the dual-status dance atomically (edit, move, reindex).
- `docs mv <old> <new>` rewrites `Related:` references across the tree.
- `docs touch <file>` bumps `Updated:`.
- Atomicity: tmp file + rename for every write; never leave a partially-edited doc.
- `--dry-run` works on all of these.

Exit criteria: archiving and renaming this repo's own docs through M2 produces correct, drift-free state.

## M3 — Validation and query: `check`, `list`

Goal: make the convention enforceable and queryable.

- `docs check` reports all violations defined in `cli.md`. Exit code semantics matter: 0/1/2 must be distinguishable so CI hooks can rely on them.
- `docs list` with all filters and JSON output. JSON schema documented in `cli.md` and stable from this point.
- Stale detection (`--stale N`).

Exit criteria: `docs check` on this repo's `docs/` returns exit 0. `docs list --json` output validates against the documented schema.

## M4 — Migration helper: `docs migrate <dir>`

Goal: import an existing non-conforming directory into the convention.

- Walks a foreign directory, inspects each `.md` file's structure.
- Infers `Role` from filename suffix patterns (`-spec`, `-status`, `-plan`, etc.) and from any existing metadata-shaped lines.
- Infers `Project` from common filename prefix.
- Inserts a metadata block under the H1 (or creates an H1 from the filename if missing).
- Detects existing archive-style subdirs (`archived/`, `project-history/`, `archive/YYYY-MM-DD/`) and normalizes them.
- Produces a dry-run report by default; `--apply` performs the edits.
- Intended to be agent-driven: the migration tool surfaces ambiguities, an LLM resolves them, the tool applies the decisions.

This is the verb that lets us point an agent at an existing doc tree (the validaitor specs, the risk-register dir, anyone's `docs/`) and bring it into the convention without manual labor.

Exit criteria: a dry-run against one of the example directories produces a complete migration plan with explicit decisions for every ambiguous case.

## M5 — Claude Code skill

Goal: agents use `docs` automatically when working in a docs root.

- SKILL.md at `~/.claude/skills/docs/` (or wherever the install convention lands).
- Triggers on: editing a `.md` file under a `.docs.toml`-marked root; user requests to "archive", "list docs", "create a plan/spec/charter"; before agent appends to a hand-curated INDEX.
- Skill body redirects to the appropriate `docs` verb instead of hand-editing.
- Documents the trigger conditions and the verbs without re-teaching the convention (that lives in `convention.md`).

Exit criteria: the agent stops hand-editing INDEX.md in this repo and uses `docs index`.

## v1.1

**docs-cli 1.3.0 shipped 2026-05-25** (closes the M6 → M9 backlog grouping internally tracked as "v1.1"). M6 (PyPI
distribution preparation, closed 2026-05-24), M7 (migration
accuracy + breaking `Status:` → `Lifecycle:` rename, complete
2026-05-25), and M8 (adoption workflow, complete 2026-05-25)
all landed locally over a two-day stretch; M9 (operator-driven
PyPI publish, 2026-05-25) batched them into one public release
per the OQ-C split. The package is live at
https://pypi.org/project/docs-cli/1.3.0/ and the GitHub repo
is public with the `v1.3.0` tag + release. Intermediate
versions (1.1.0, 1.2.0) never reached PyPI by design — no
prior public release existed, no continuity to preserve.

| Milestone | Status | Task plan | Log |
|---|---|---|---|
| M6 — PyPI distribution preparation as `docs-cli` | **Complete** (2026-05-24, preparation only; publish moved to M9) | [m6-pypi-distribution.md](m6-pypi-distribution.md) | [Log](m6-pypi-distribution-log.md) |
| M7 — Migration plan accuracy | **Complete** (2026-05-25; ship-ready locally, publish deferred to M9 batched 1.3.0) | [m7-migration-accuracy.md](m7-migration-accuracy.md) | [Log](m7-migration-accuracy-log.md) |
| M8 — Adoption workflow (agent-driveable) | **Complete** (2026-05-25; ship-ready locally as 1.3.0, publish DEFERRED to M9 batched 1.3.0 per OQ-C) | [m8-adoption-workflow.md](m8-adoption-workflow.md) | [Log](m8-adoption-workflow-log.md) |
| M9 — PyPI publish 1.3.0 | **Complete** (2026-05-25; `docs-cli==1.3.0` on PyPI; repo public; `v1.3.0` tag + GitHub release) | [m9-pypi-publish.md](m9-pypi-publish.md) | [Log](m9-pypi-publish-log.md) |
| M10 — Adoption-flow polish + 1.3.0 carry-overs (v1.4.0) | **Active** (Phases 1-7 complete 2026-05-27; OQ-A through OQ-I resolved; 400/400 GREEN at 1.4.0; Phase 8 next) | [m10-adoption-polish.md](m10-adoption-polish.md) | [Log](m10-adoption-polish-impl.md) |

**M10** bundles the two user-surfaced agent-driveability features
(`docs touch <file...>`, `docs migrate --apply` writes `.docs.toml`)
with the carry-overs from M3 (`[vocabulary] add_fields` allowlist —
moved out of Open questions below), M7 (`Confidence` enum), and M8
(`--quiet` per-file output suppression, `MigrationPlan.excluded_count`
removal, adoption-playbook restructure). Ships as 1.4.0. The M10
deliverable list and the 9 resolved Decisions (OQ-A through OQ-I,
operator-confirmed 2026-05-26) live in the milestone doc.

**M7** hardens `docs migrate`'s inference + introduces a breaking
controlled-vocab rename (`Status:` → `Lifecycle:`). It targets ≥50%
high-confidence plans on real trees (today: 25.3%) and surfaces
common real-world suffixes (`_Implementation`, `_Sketch`, etc.) +
project-name normalisation. Adds exactly **one new CLI flag** —
`docs migrate --config-project <name>` (the multi-project agent
override per F5); renames `docs list --status` → `--lifecycle`
in lockstep with the controlled-vocab field rename. Otherwise
pure inference + a convention change.

**M8** builds on M7's accurate plan with operator + agent
ergonomics: `--exclude` tree-wide (`.docs.toml` `[exclude]`
applies to `migrate` + `index` + `check` + `list`), triage flags
(`--summary`, `--only ambiguous`), `docs new --body-from` (closes
the harness's Read-before-Write friction), and a substantial
rewrite of the bundled skill's reference files to cover the
adoption flow. SKILL.md stays slim — one pointer line. Load-bearing
gate: fresh-subagent dogfooding of the adoption loop end-to-end.

**M9** — the publish milestone — shipped 2026-05-25. It
verified the pre-bumped `pyproject.toml` + `__version__` at
`1.3.0` (the bumps had pre-landed at M7 and M8 Phase 7;
CHANGELOG dated at M8 Phase 10), rebuilt fresh artefacts from
the post-M8 tree, rehearsed on TestPyPI under a disambiguated
dist name `docs-cli-rehearsal` (the bare `docs-cli` was parked
on TestPyPI by an unrelated user — real PyPI was clean),
published to real PyPI, flipped the GitHub repo to public,
tagged `v1.3.0` at the M8 simplify commit, and created the
GitHub release with hand-augmented notes. Doc closeouts ran
in lockstep. Token re-scope was deferred as out-of-band
operator UI work. Full record + deviations in
[m9-pypi-publish.md](m9-pypi-publish.md)'s milestone-completion
summary; the operative checklist
[release-runbook.md](release-runbook.md) stays the reference
for v1.4+ releases.

The parked `[vocabulary] add_fields` extra-field allowlist (see
_Open questions_ below) was scheduled into M10 as item #8 and is no
longer carried forward separately.

## Out of scope for v1

- Link-graph queries / `docs graph`.
- HTML or static-site rendering.
- Watch mode.
- Full-text search.
- Per-doc revisions / history (git owns this).
- Cross-root federation.
- Templates beyond `docs new` defaults. If users want richer scaffolds, they hand-edit after creation.

## Resolved questions

- **`docs archive --cascade` stays opt-in** (M2, 2026-05-21). Archiving a doc must not silently pull its neighbours along — cascading is a deliberate per-invocation choice. `--cascade` is a plain `store_true` flag; it prompts (`y/N`, defaulting to no) before archiving each one-hop `pairs-with` / `child-of` relation. No `--no-cascade` is needed.
- **INDEX carries a one-paragraph description per doc** (M1). The renderer emits title + description + Status + Updated; the description is the doc's first body paragraph, trimmed to ~120 characters.
- **INDEX grouped by `Project` then `Role`** (M3, 2026-05-22). The renderer regroups active docs two levels deep — `## Project — <name>` (the docs-root project first, then alphabetical) then `### Active — <Role>` — with `## Archived` a single flat trailing section. Resolved by `Project`, not directory: it is metadata-driven, consistent with the convention's replacement of role-bucket subdirectories with `Role:` metadata, and parallel to `docs list --project`. Directory grouping was rejected for cutting against that convention.

## Open questions

_v1 (M1-M5) shipped 2026-05-20…2026-05-22 and v1.3.0 (M6-M9) shipped
2026-05-25. The previously-parked `[vocabulary] add_fields` extra-field
allowlist was scheduled into **M10** (v1.4.0) as item #8 — see the M10
milestone doc's Decisions section (OQ-F, OQ-H) for the final
rule-message shape and case-sensitivity decisions._

_No plan-level open questions are currently outstanding. M10's
milestone-scoped questions (OQ-A through OQ-I) were
operator-confirmed 2026-05-26 and promoted to the Decisions section
of [m10-adoption-polish.md](m10-adoption-polish.md)._
