# docs — Charter

Status: active
Role: charter
Project: docs
Updated: 2026-05-20

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
