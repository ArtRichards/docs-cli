---
name: docs
description: Use whenever the user asks to create a spec, archive or rename a doc, list docs, regenerate INDEX.md, or check a docs tree (a directory with a .docs.toml file at its root), or to adopt a foreign Markdown directory into the convention. Always run the docs CLI verb (docs new / index / archive / mv / list / touch / check / migrate) — never hand-edit INDEX.md, metadata blocks, or files into archive/. Not for ordinary Markdown outside a .docs.toml-marked tree.
---

# docs — drive the CLI, do not hand-edit

Use the `docs` CLI for managing a tree of structured Markdown documents —
specs, runbooks, references, design notes — where each file is
self-describing (a metadata block under its H1) and `INDEX.md` is a
generated view of the docs, not a hand-maintained list. **Run a `docs`
verb for every metadata, index, archive, or lifecycle action; never
hand-edit those parts.** The verb keeps the tree internally consistent —
a hand edit silently drifts it out of sync. The sections below name which
verb to run for which task and how to read its output.

A `docs`-managed tree is such a directory, marked by a `.docs.toml` file
at its root. This skill only applies to such trees; outside one, edit
Markdown normally.

## Never hand-edit these — run the verb

Three things in a `docs`-managed tree must never be hand-edited. Editing them
by hand produces a tree that looks fine in the diff but fails `docs check`:

- **`INDEX.md`** — it is generated. The content between the
  `<!-- docs:generated start -->` and `<!-- docs:generated end -->` markers is
  rewritten from doc metadata. Never append a bullet or fix a line inside the
  markers by hand — run `docs index` to regenerate it.
- **A doc's location relative to `archive/`** — never move a file into or out
  of `archive/<date>/` with `mv`/`git mv`, and never hand-flip a `Status:`
  line to or from `archived`. The `Status:` value and the on-disk location
  must agree; run `docs archive` so they move together.
- **A metadata block** — the `Status: / Role: / Project: / Updated:` lines
  (and the `Related:` block) under a doc's H1. Do not hand-write a block for
  a new doc — run `docs new` to scaffold it. Do not hand-edit the `Updated:`
  date — run `docs touch` to bump it.

If a task does **not** touch metadata, `INDEX.md`, archiving, or a doc's
lifecycle — for example fixing a typo, rewording a sentence, or adding a
paragraph to a doc's body — then no `docs` verb applies. Make the prose edit
normally. (Bump the edited doc's `Updated:` with `docs touch` if the change
is substantive; a trivial typo fix does not need it.) This skill only
redirects the metadata/index/lifecycle operations below — it does not gate
ordinary editing.

## Finding the binary and the root

The CLI is `docs`. Resolve it host-agnostically — do not assume an absolute
path:

- Prefer an installed `docs` on `$PATH`.
- Otherwise run `bin/docs` from the repository root (the executable lives at
  `bin/docs` in a checkout).

`docs` finds the tree by walking up from the current directory until it sees
a `.docs.toml` file. To be explicit — or when the current directory is
elsewhere — pass `--root DIR` (it goes after the verb, e.g.
`docs index --root DIR`). If no `.docs.toml` exists anywhere up the tree,
the directory is **not** a `docs`-managed tree and this skill does not apply
— edit the Markdown normally.

## Which verb for which task

Each documentation task maps to one verb. Run the verb; do not reproduce its
effect by hand.

### Creating a doc — `docs new`

When asked to create a new doc — a spec, a runbook, a reference, a design
note, or any other structured Markdown record — run `docs new <role> <slug>`.
It scaffolds the file with a correct metadata block (`Status: draft` and
today's `Updated:`) under an H1 — never hand-write that block. `<role>` must
be a real role in the convention's vocabulary; `<slug>` becomes `<slug>.md`
and may name a subdirectory (`sub/feature`). Use `--project NAME` to override
the inferred project and `--title "…"` to set the H1. `new` does not refresh
`INDEX.md` (the doc is still empty) — run `docs index` once the doc has
content.

### Regenerating the index — `docs index`

When `INDEX.md` is stale — a doc was added, removed, archived, or its first
paragraph changed — run `docs index`. It rewrites only the marked block and
is idempotent: running it twice with no changes produces no diff. This is
the verb that replaces every hand-edit of `INDEX.md`. Use
`docs index --root DIR` to target a specific tree, and `--dry-run` to
preview the regenerated file without writing it.

### Archiving a doc — `docs archive`

When a doc is finished or superseded — a retired spec, a closed plan, a
draft replaced by another — run `docs archive <file>`. It sets
`Status: archived`, bumps `Updated:`, moves the file into `archive/<date>/`,
and regenerates `INDEX.md` — in that order; the metadata edit itself is
atomic, so a failed run leaves the original file untouched. Never hand-move
a doc into `archive/`. Use `--reason "…"` to record why,
`--date YYYY-MM-DD` to override the archive date, and `--cascade` to also
archive one-hop `pairs-with` / `child-of` relations (it prompts per file).

### Renaming or moving a doc — `docs mv`

When asked to rename or relocate a doc within the tree, run
`docs mv <old> <new>`. It moves the file and rewrites every `Related:`
entry across the whole tree that pointed at `<old>` — so references do not
break. Never hand-edit those `Related:` lines yourself; you will miss some.
`<new>` may be a new name in the same directory or a path into another
directory under the root. `mv` regenerates `INDEX.md`. (It rewrites
`Related:` metadata only, not prose links in doc bodies.)

### Listing docs — `docs list`

When asked which docs exist, or to list docs by status, role, project, or
staleness, run `docs list`. Filters AND-combine: `--status S`, `--role R`,
`--project P`, and `--stale N` (docs whose `Updated:` is more than N days
old). Add `--json` for a machine-readable array — one record per doc —
when the result feeds another step. The default output is a human table
grouped by status then role.

### Recording an edit date — `docs touch`

When a doc's body has been edited and the change should be dated, run
`docs touch <file>`. It bumps that doc's `Updated:` field to today and
regenerates `INDEX.md` — nothing else. Do not hand-edit the `Updated:`
line; use this verb so the date and the index stay in step.

### Checking the tree — `docs check`

Before a commit, in CI, or whenever the tree's health is in question, run
`docs check`. It validates every doc — required metadata present,
vocabulary valid, dates parseable, `Status:` matching on-disk location,
`Related:` paths resolving — and reports findings grouped by file.
**Read the exit code**: `0` means clean, `1` means warnings only (stale
docs), `2` means errors that must be fixed. In CI, exit `2` should fail the
build. Pass a directory (`docs check DIR`) to check a specific tree; add
`--json` for machine-readable findings and `--stale N` to also flag stale
active docs.

### Adopting a foreign directory — `docs migrate`

When asked to bring an existing, non-conforming directory of Markdown into
the convention, run `docs migrate <dir>`. It is **dry-run by default**: it
walks the directory, infers the required metadata for every file, and
prints a plan — one decision per file, every ambiguity flagged — without
writing anything. Review that plan first. Re-run with `--apply` to insert
the metadata blocks and normalise archive-style subdirectories. Add
`--json` to consume the plan programmatically. `migrate` refuses a
directory that is already a docs root.

## Where the convention itself lives

This skill teaches **which verb to run**, not the on-disk format. It does
not restate the metadata-block grammar, the `Status:` / `Role:` vocabulary,
or the archive layout — those have a single source of truth. For the format
and vocabulary, read the convention spec `convention.md`; for the full flag
and exit-code reference of every verb, read the CLI spec `cli.md`. (Both
are named here as plain references, not links — a docs-managed tree keeps
them at its own root, not inside this skill.) If a task needs a convention
detail this skill does not give, consult `convention.md` rather than
guessing.
