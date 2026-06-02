# docs — Use cases

When to reach for `docs`. The verbs cluster into three workflows.
If your task doesn't fit one of these, `docs` is probably the
wrong tool. The project charter's non-goals section explains the
boundary in the source repository.

This file is part of the bundled `docs` agent skill at
`src/docs_cli/skill/references/`. It is also the single source of
truth for what `docs` is for — the charter links here for the
concrete use-case catalog; `cli.md` is the verb-level reference;
`adoption-playbook.md` (when shipped at M8) is the procedural
deep-dive for the adoption workflow specifically.

## Greenfield: start and maintain a docs tree

You own the convention from day one.

| Scenario | Verb | Detail |
|---|---|---|
| Bootstrap a new docs tree | (touch `.docs.toml`) | One `[project] name = "…"` line is enough; see `convention.md`. |
| Author a new spec / plan / charter / log / runbook / decision | `docs new <role> <slug>` | Scaffolds the metadata block + H1. Agents author the full body in one Bash call via `docs new <role> <slug> --body-from -` (M8). |
| Bump a doc's `Updated:` after edit | `docs touch <file>...` | Required after any body or metadata edit. Accepts one or more files; the batch is atomic and the INDEX refreshes exactly once at end (M10). |
| Rename or relocate a doc | `docs mv <old> <new>` | Rewrites every `Related:` reference tree-wide. Prose markdown links in bodies are not rewritten — that's a deliberate scope cut. |
| Archive a completed doc | `docs archive <file>` | Atomic: edits `Lifecycle:` (`Status:` pre-M7), moves to `archive/YYYY-MM-DD/`, regenerates INDEX. `--cascade` opt-in for one-hop dependents. |
| Regenerate INDEX | `docs index` | The hand-written preamble is preserved; only the marker-block content is rewritten. |
| Query the tree | `docs list [filters]` | Human table by default; `--json` for piping. Filter by role, lifecycle, project, stale-after-N-days. |
| Validate in CI | `docs check` | Reports drift, broken refs, lifecycle/location mismatches, malformed metadata. Exit codes 0/1/2 distinguishable for CI gates. |

## Adoption: bring a non-conforming tree under the convention

You walked into an existing Markdown directory (yours, a
colleague's, a foreign project's) and want to put it under
`docs`.

| Scenario | Verb | Detail |
|---|---|---|
| Inspect what would change | `docs migrate <dir>` | Dry-run by default; produces a plan with one decision per file. Read the footer first — it summarises confidence, excluded counts, multi-project hints (M7), and non-md siblings (M8). |
| Triage the plan | `docs migrate <dir> --summary --only ambiguous` | Compact one-line-per-file view; filter to ambiguous-only entries needing attention. (M8.) |
| Exclude data subdirs from migration | `docs migrate <dir> --exclude <subdir>/` | Repeatable; glob-supporting. Persistent via `[exclude] dirs` in `.docs.toml` or a `.docsignore` file at the tree root (M8). Same exclude list applies tree-wide (`index`, `check`, `list`). |
| Apply the migration | `docs migrate <dir> --apply` | Writes the inferred metadata blocks; normalises archive-style subdirs into `archive/YYYY-MM-DD/`. |
| Adopt a multi-project parent tree | `docs migrate <subdir> --config-project <name>` (per subdir) | The parent's dry-run emits hints like *"subdir 'foo-tools/' looks like a separate project"*; the agent decides ignore / exclude+recurse / override (M7 F5). |
| Sidecar a non-md artifact | `docs new <role> <slug> --body-from -` with `Related: artifact-of: <binary>` | When an HTML / XLSX / ODT is referenced from prose and warrants tracking, author a `.md` sidecar; the original binary stays where it is. No new verb — uses the M8 `--body-from` flag. |
| Verify the adopted tree | `docs check <dir>` | Same gate used in greenfield CI. |

The deeper "agent driving an adoption end-to-end" procedure
lives in `adoption-playbook.md` (M8 — the playbook is a
sibling reference in this same `references/` directory). The
skill triggers on phrases like *"adopt this directory"*,
*"migrate this folder"*, and *"bring this into docs
convention"*.

## Distribution: install + share

| Scenario | Verb | Detail |
|---|---|---|
| Install for users | `pip install docs-cli` | Stdlib-only; Python 3.11+. The `docs` console-script lands on PATH. |
| Install the agent skill | `docs install-skill` | Materialises this bundled skill (default: `~/.claude/skills/docs/`). `--symlink` for editable contributor installs. |
| Develop on the tool itself | `pip install -e ".[dev]"` | Editable install; `docs` on PATH points at the local source. |
