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

The verbs cluster into three workflows. If your task doesn't fit
one of these, `docs` is probably the wrong tool — see Non-goals.

### Greenfield: start and maintain a docs tree

You own the convention from day one.

| Scenario | Verb | Detail |
|---|---|---|
| Bootstrap a new docs tree | (touch `.docs.toml`) | One `[project] name = "…"` line is enough; see `convention.md`. |
| Author a new spec / plan / charter / log / runbook / decision | `docs new <role> <slug>` | Scaffolds the metadata block + H1. Agents author the full body in one Bash call via `docs new <role> <slug> --body-from -` (M8). |
| Bump a doc's `Updated:` after edit | `docs touch <file>` | Required after any body or metadata edit. |
| Rename or relocate a doc | `docs mv <old> <new>` | Rewrites every `Related:` reference tree-wide. Prose markdown links in bodies are not rewritten — that's a deliberate scope cut. |
| Archive a completed doc | `docs archive <file>` | Atomic: edits `Lifecycle:` (`Status:` pre-M7), moves to `archive/YYYY-MM-DD/`, regenerates INDEX. `--cascade` opt-in for one-hop dependents. |
| Regenerate INDEX | `docs index` | The hand-written preamble is preserved; only the marker-block content is rewritten. |
| Query the tree | `docs list [filters]` | Human table by default; `--json` for piping. Filter by role, lifecycle, project, stale-after-N-days. |
| Validate in CI | `docs check` | Reports drift, broken refs, lifecycle/location mismatches, malformed metadata. Exit codes 0/1/2 distinguishable for CI gates. |

### Adoption: bring a non-conforming tree under the convention

You walked into an existing Markdown directory (yours, a colleague's, a
foreign project's) and want to put it under `docs`.

| Scenario | Verb | Detail |
|---|---|---|
| Inspect what would change | `docs migrate <dir>` | Dry-run by default; produces a plan with one decision per file. Read the footer first — it summarises confidence, excluded counts, multi-project hints (M7), and non-md siblings (M8). |
| Triage the plan | `docs migrate <dir> --summary --only ambiguous` | Compact one-line-per-file view; filter to ambiguous-only entries needing attention. (M8.) |
| Exclude data subdirs from migration | `docs migrate <dir> --exclude <subdir>/` | Repeatable; glob-supporting. Persistent via `[exclude] dirs` in `.docs.toml` or a `.docsignore` file at the tree root (M8). Same exclude list applies tree-wide (`index`, `check`, `list`). |
| Apply the migration | `docs migrate <dir> --apply` | Writes the inferred metadata blocks; normalises archive-style subdirs into `archive/YYYY-MM-DD/`. |
| Adopt a multi-project parent tree | `docs migrate <subdir> --config-project <name>` (per subdir) | The parent's dry-run emits hints like *"subdir 'foo-tools/' looks like a separate project"*; the agent decides to ignore, exclude+recurse, or override (M7 F5). |
| Sidecar a non-md artifact | `docs new <role> <slug> --body-from -` with `Related: artifact-of: <binary>` | When an HTML / XLSX / ODT is referenced from prose and warrants tracking, author a `.md` sidecar; the original binary stays where it is. No new verb — uses the M8 `--body-from` flag. |
| Verify the adopted tree | `docs check <dir>` | Same gate used in greenfield CI. |

The deeper "agent driving an adoption end-to-end" procedure lives in
the bundled skill at `src/docs_cli/skill/references/adoption-playbook.md`
(M8). The skill triggers on phrases like *"adopt this directory"*,
*"migrate this folder"*, and *"bring this into docs convention"*.

### Distribution: install + share

| Scenario | Verb | Detail |
|---|---|---|
| Install for users | `pip install docs-cli` | Stdlib-only; Python 3.11+. The `docs` console-script lands on PATH. |
| Install the agent skill | `docs install-skill` | Materialises the bundled Claude Code skill (default: `~/.claude/skills/docs/`). `--symlink` for editable contributor installs. |
| Develop on the tool itself | `pip install -e ".[dev]"` | Editable install; `docs` on PATH points at the local source. |

## Distribution

`docs` ships as the `docs-cli` distribution on PyPI (v1.1 onward) —
`pip install docs-cli` lands the `docs` console-script on PATH and
ships the bundled Claude Code skill inside the wheel as package data.
A one-shot `docs install-skill` materialises that skill onto the host
(default destination `~/.claude/skills/docs/`). The convention itself
is unchanged — `Project: docs` stays `docs`; only the distribution
name and the installation path differ. The release runbook at
[release-runbook.md](release-runbook.md) governs publishing.
