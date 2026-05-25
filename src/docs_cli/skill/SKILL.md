---
name: docs
description: Use whenever the user asks to create a spec, archive or rename a doc, list docs, regenerate INDEX.md, or check a docs tree (a directory with a .docs.toml file at its root), or to adopt a foreign Markdown directory into the convention (e.g. "adopt this directory", "migrate this folder", "bring this into docs convention", "import existing markdown specs"). Always run the docs CLI verb (docs new / index / archive / mv / list / touch / check / migrate) — never hand-edit INDEX.md, metadata blocks, or files into archive/. Not for ordinary Markdown outside a .docs.toml-marked tree.
---

# docs — run the verb, never hand-edit

`docs` is a CLI for managing trees of structured Markdown documents —
specs, runbooks, references, design notes — where each file is
self-describing (a metadata block under its H1) and `INDEX.md` is a
generated view of the docs, not a hand-maintained list. **Run a `docs`
verb for every metadata, index, archive, or lifecycle action; never
hand-edit those parts.** A hand edit silently drifts the tree out of
sync.

## When this skill applies

A `docs`-managed tree is a directory with `.docs.toml` at its root. Use
this skill when:

- The directory has `.docs.toml` and the user's request maps to a verb
  below.
- The user wants to start managing a directory as docs — bootstrap with
  `touch .docs.toml` at the intended root, then use `docs new` and
  `docs index`.
- The user wants to adopt an existing tree of foreign Markdown into the
  convention — run `docs migrate <dir>` (dry-run first).
- The user is about to hand-edit `INDEX.md`, a metadata block, or move
  a file into `archive/`.

Do **not** apply when:

- Editing ordinary Markdown in a non-docs project (e.g. a `README.md`
  in a code repo).
- A prose-only edit that does not touch metadata, `INDEX.md`,
  archiving, or lifecycle — make the edit normally.

If no `.docs.toml` exists up-tree, `docs` silently falls back to the
current directory as the implicit root. That cwd-fallback is convenient
but easy to misuse — confirm with the user before any verb that writes.

## The verbs

| Task | Verb | Key flags / behaviour |
|---|---|---|
| Create a doc | `docs new <role> <slug>` | `--project`, `--title`; scaffolds metadata |
| Regenerate the index | `docs index` | idempotent; rewrites only the marker block |
| Archive a finished doc | `docs archive <file>` | `--reason`, `--date`, `--cascade` |
| Rename or move a doc | `docs mv <old> <new>` | rewrites `Related:` tree-wide |
| List or query docs | `docs list` | `--lifecycle`, `--role`, `--project`, `--stale`, `--json` |
| Bump a doc's `Updated:` | `docs touch <file>` | reindexes |
| Validate the tree | `docs check` | exit `0` clean / `1` warnings / `2` errors |
| Adopt a foreign tree | `docs migrate <dir>` | dry-run by default; `--apply` to write |
| Install this skill on a host | `docs install-skill` | `--dest`, `--copy` (default), `--symlink`, `--force` |

`docs` walks up from the current directory to find `.docs.toml`. Use
`docs <verb> --root DIR` to point at a specific tree explicitly. For
full flag and exit-code detail, read
[`references/cli.md`](references/cli.md) or run `docs <verb> --help`.

**Adopting an existing Markdown directory?** Read
[references/adoption-playbook.md](references/adoption-playbook.md)
first — it walks the dry-run → triage → exclude → iterate → apply →
verify loop end-to-end and points at the starter
[`references/docs-toml-template.toml`](references/docs-toml-template.toml).

## Three things never to hand-edit

- **`INDEX.md`** — generated between `<!-- docs:generated -->` markers.
  Run `docs index` to regenerate.
- **A file's location relative to `archive/`** — never `mv`/`git mv` a
  file into or out of `archive/<date>/`, and never hand-flip
  `Lifecycle:` to or from `archived`. Run `docs archive` so lifecycle
  and location move together.
- **A metadata block** — `Lifecycle:` / `Role:` / `Project:` /
  `Updated:` / `Related:`. Use `docs new` to scaffold a new block;
  `docs touch` to bump the date. Never hand-write or hand-edit.

## Reference

The on-disk format and vocabulary (Role / Status values, metadata-block
grammar, archive layout):
[`references/convention.md`](references/convention.md).

The full flag and exit-code reference of every verb:
[`references/cli.md`](references/cli.md).

When a task needs a convention or flag detail this skill does not give,
open the reference rather than guessing.
