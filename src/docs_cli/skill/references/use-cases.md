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
| Archive a completed doc | `docs archive <file>` | Atomic: edits `Lifecycle:` (`Status:` pre-M7), moves to `archive/YYYY-MM-DD/`, regenerates INDEX. Archives that ONE doc; to take related docs too, preview the one-hop neighbourhood with `--cascade-dry-run` and then write the exact set with `--cascade-only GLOB` (M26). `--json` emits the whole operation plan. |
| Regenerate INDEX | `docs index` | The hand-written preamble is preserved; only the marker-block content is rewritten. |
| Query the tree | `docs list [filters]` | Human table by default; `--json` for piping. Filter by role, lifecycle, project, stale-after-N-days. |
| Validate in CI | `docs check` | Reports drift, broken refs, lifecycle/location mismatches, malformed metadata, one-sided reciprocal edges, and — from 2.0 — local Markdown body links whose destination is missing or leaves the tree root. Exit codes 0/1/2 distinguishable for CI gates. |
| Repair a one-sided relationship | `docs relate add\|remove SOURCE VERB TARGET` | Writes both halves of a reciprocal pair as one operation. Idempotent; `--dry-run` previews; `--json` for piping; `--reason` required for an archived endpoint (M25). |

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

## Upgrade: repair reciprocal relationships (M25)

Six `Related:` verbs are **reciprocal** — `precedes`/`follows`,
`depends-on`/`required-by`, `blocks`/`blocked-by`. A recognized edge
whose target does not declare the exact inverse back is a hard
`docs check` error, so a tree that passed before the upgrade can
start failing. The repair is explicit, never automatic: `docs` will
not guess whether the edge should be completed or deleted.

| Scenario | Verb | Detail |
|---|---|---|
| Fix duplicated metadata labels FIRST | `docs check` → hand-merge | A label may appear at most once; a second copy silently replaces the first. `duplicate-field` names it. Merge the bullets under one label by hand — `docs relate` will not, and on a duplicated doc a repair can report success while the finding survives. |
| Find the one-sided edges | `docs check` | Each finding names the source, the verb, the target, and the exact missing inverse. `--json` for a machine list; the record keys are unchanged (`path`, `severity`, `rule`, `message`). |
| The edge is right — complete it | `docs relate add <source> <verb> <target>` | Copy the paths straight out of the finding; relative endpoints resolve root-relative first. Only the missing half is written; INDEX refreshes once. |
| The edge is wrong — delete the pair | `docs relate remove <source> <verb> <target>` | Removes whichever halves exist. Equally valid; `check` is clean either way. |
| Preview before touching anything | `docs relate add … --dry-run` | Writes nothing at all, INDEX included. The `--json` record has the same shape as a real apply, so a preview and an apply are diffable. |
| Repair an archived endpoint | `docs relate add … --reason "…"` | Required whenever either endpoint is under `archive/`. Only the one `Related:` bullet, `Updated:`, and a dated `Revision:` audit bullet may change; lifecycle, `Archived-reason:`, and prose are byte-identical. |
| Re-run safely | any of the above | Fully idempotent: an already-satisfied invocation writes zero bytes, bumps no `Updated:`, adds no `Revision:` bullet, and does not reindex. |

The loop is `check → relate add|remove → check` until clean. Free-form
verbs (`pairs-with`, `child-of`/`parent-of`,
`supersedes`/`superseded-by`, your own) are untouched by all of this —
they gain no reciprocal validation and `relate` refuses to edit them.

## Upgrade: repair body links (M27)

From 2.0 `docs check` also reads each document's **body** and validates the
local Markdown links it finds there, so a tree carrying unnoticed prose damage
starts failing. A body-link destination resolves **relative to the document
that contains it** — not root-relative like a `Related:` target — which is why
`../` is normal in prose and never appears in a `Related:` bullet. Code
(fenced and inline), images, autolinks, raw HTML, reference *uses*, external
and schemed URLs, root-absolute and protocol-relative destinations, and
fragment-only links produce nothing at all; a fragment is preserved and never
validated. There is no repair verb and no opt-out knob: `docs` will not guess
whether a link should be rebased, repointed, or deleted.

| Scenario | Verb | Detail |
|---|---|---|
| Find the damage | `docs check` | Each finding names the 1-based line, the destination exactly as written, and the path it resolves to. `--json` for a machine list; the record keys are unchanged (`path`, `severity`, `rule`, `message`). |
| The destination is missing — rebase it | `docs check` → edit the destination | `broken-body-link`. The overwhelmingly common cause is a document an older `docs` archived: the link was correct at the document's original location and no version of the tool has ever rebased it, so it needs the `../../` that the move into the archive should have added. The finding prints the candidate path it probed, which is what makes the missing prefix obvious. |
| The destination leaves the tree — use a URL | `docs check` → replace with a URL | `outside-root-body-link`. The destination names something the tree does not own, and `docs check` never stats outside its own root — the escape is detected by path arithmetic alone, so the verdict is identical from a git clone, a container, or a vendored subtree. Replace it with a **URL**. |
| Opt a span out deliberately | edit the prose | Fence a code sample that contains link syntax, put it in an inline code span, or backslash-escape the opening bracket. Any of the three makes the span invisible to the scanner. |
| Re-check | `docs check` | Clean. |

The loop is `check → rebase or URL → check` until clean.

## Distribution: install + share

| Scenario | Verb | Detail |
|---|---|---|
| Install for users | `pip install docs-cli` | Stdlib-only; Python 3.11+. The `docs` console-script lands on PATH. |
| Install the agent skill | `docs install-skill` | Materialises this bundled skill (default: `~/.claude/skills/docs/`). `--symlink` for editable contributor installs. |
| Develop on the tool itself | `pip install -e ".[dev]"` | Editable install; `docs` on PATH points at the local source. |
