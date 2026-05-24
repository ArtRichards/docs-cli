# docs — Charter

Status: active
Role: charter
Project: docs
Updated: 2026-05-24

Related:
- pairs-with: convention.md
- pairs-with: cli.md
- pairs-with: plan.md

## What we're building

A small, opinionated CLI (`docs`) that manages a tree of Markdown documentation by treating each file as a self-describing record. The CLI derives an index, archives completed work, validates consistency, and answers queries — letting authors focus on content instead of cross-references.

## Why

Three pain points in every documentation tree we've worked with:

1. **Hand-maintained index files drift.** Edits to a doc don't reach the index. The index slowly lies.
2. **Descriptions get duplicated** across the file, the index, and any parent doc that references it. Updating one rots the others.
3. **Lifecycle is invisible.** Active, blocked, completed, and abandoned work sit in the same directory with no machine-readable signal of which is which.

`docs` makes each file self-describing (one metadata block under the H1) and treats the index as a derived view. The doc is the truth; the index is generated.

## Success criteria

- A new doc can be authored with `docs new <role> <slug>`; metadata is correct without thought.
- Archiving a completed plan is one command (`docs archive`); status, location, and index all update atomically.
- `docs check` flags drift (broken refs, status/location mismatch, stale active docs) with nonzero exit, suitable for CI.
- The tool runs on any host with Python 3.11+ (for stdlib `tomllib`) and no third-party dependencies.
- The convention reads naturally without the tool — `head -10 file.md` shows the metadata as plain prose.

## Non-goals

- Not a static site generator. No HTML output, no themes.
- Not a wiki or note-taking app. No tags-as-database, no full-text search.
- Not a link-graph visualizer. Cross-references are validated, not traversed.
- Not a replacement for version control. Git owns history; `docs` owns lifecycle.
- Not a project management tool. Status conveys doc lifecycle, not work assignment.

## Audience

- Engineers who keep their docs in a repository and want lightweight structure.
- Agents (LLMs) that author and maintain docs; the JSON output and prescriptive convention give them a reliable surface to work against.

## Use cases

The concrete catalog — when to reach for `docs`, with the verbs
mapped to each scenario — lives in the bundled skill at
[src/docs_cli/skill/references/use-cases.md](../src/docs_cli/skill/references/use-cases.md).
Three workflow buckets: **greenfield** (start + maintain a tree),
**adoption** (bring a foreign tree under the convention), and
**distribution** (install + share). If your task doesn't fit one
of those, see Non-goals above.

Single source of truth — the skill bundle ships with the catalog
so an agent installing `docs install-skill` gets it on disk; a
developer reading this charter follows the link. The lockstep
references for `convention.md` and `cli.md` already work this
way; `use-cases.md` is skill-only (no `docs/` mirror).

## Distribution

`docs` ships as the `docs-cli` distribution on PyPI (v1.1 onward) —
`pip install docs-cli` lands the `docs` console-script on PATH and
ships the bundled Claude Code skill inside the wheel as package data.
A one-shot `docs install-skill` materialises that skill onto the host
(default destination `~/.claude/skills/docs/`). The convention itself
is unchanged — `Project: docs` stays `docs`; only the distribution
name and the installation path differ. The release runbook at
[release-runbook.md](release-runbook.md) governs publishing.
