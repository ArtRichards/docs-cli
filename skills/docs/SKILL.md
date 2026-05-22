---
name: docs
description: Use the docs CLI for documentation work in a docs-managed tree (a directory with a .docs.toml file) — creating a plan/spec/charter/milestone, archiving or renaming a doc, listing docs, checking the tree, regenerating INDEX.md, or adopting a foreign Markdown directory. Run the docs verb instead of hand-editing metadata, INDEX.md, or archive/. Not for Markdown outside a docs-managed tree.
---

# docs — drive the CLI, do not hand-edit

A `docs`-managed tree is a directory of structured Markdown with a `.docs.toml`
file at its root. Such a tree has machine-maintained parts — a generated
`INDEX.md`, a metadata block on every doc, an `archive/<date>/` subtree. When
doing documentation work inside that tree, run the matching `docs` verb instead
of editing those parts by hand. The verb keeps the tree internally consistent;
a hand edit silently drifts it out of sync. This skill names which verb to run
for which task and how to read its output.

## Never hand-edit these — run the verb

Three things in a `docs`-managed tree must never be hand-edited. Editing them by
hand produces a tree that looks fine in the diff but fails `docs check`:

- **`INDEX.md`** — it is generated. The content between the
  `<!-- docs:generated start -->` and `<!-- docs:generated end -->` markers is
  rewritten from doc metadata. Never append a bullet or fix a line inside the
  markers by hand — run `docs index` to regenerate it.
- **A doc's location relative to `archive/`** — never move a file into or out of
  `archive/<date>/` with `mv`/`git mv`, and never hand-flip a `Status:` line to
  or from `archived`. The `Status:` value and the on-disk location must agree;
  run `docs archive` so they move together.
- **A metadata block** — the `Status: / Role: / Project: / Updated:` lines (and
  the `Related:` block) under a doc's H1. Do not hand-write a block for a new
  doc — run `docs new` to scaffold it. Do not hand-edit the `Updated:` date —
  run `docs touch` to bump it.

If a task does **not** touch metadata, `INDEX.md`, archiving, or a doc's
lifecycle — for example fixing a typo, rewording a sentence, or adding a
paragraph to a doc's body — then no `docs` verb applies. Make the prose edit
normally. (Bump the edited doc's `Updated:` with `docs touch` if the change is
substantive; a trivial typo fix does not need it.) This skill only redirects the
metadata/index/lifecycle operations below — it does not gate ordinary editing.

## Finding the binary and the root

The CLI is `docs`. Resolve it host-agnostically — do not assume an absolute
path:

- Prefer an installed `docs` on `$PATH`.
- Otherwise run `bin/docs` from the repository root (the executable lives at
  `bin/docs` in a checkout).

`docs` finds the tree by walking up from the current directory until it sees a
`.docs.toml` file. To be explicit — or when the current directory is elsewhere —
pass `--root DIR` (it goes after the verb, e.g. `docs index --root DIR`). If no
`.docs.toml` exists anywhere up the tree, the directory is **not** a
`docs`-managed tree and this skill does not apply — edit the Markdown normally.

## Which verb for which task

Each documentation task maps to one verb. Run the verb; do not reproduce its
effect by hand.

### Creating a doc — `docs new`

When asked to create a new plan, spec, charter, milestone, or any other doc,
run `docs new <role> <slug>`. It scaffolds the file with a correct metadata
block (`Status: draft` and today's `Updated:`) under an H1 — never hand-write
that block. `<role>` must be a real role in the convention's vocabulary;
`<slug>` becomes `<slug>.md` and may name a subdirectory (`sub/feature`). Use
`--project NAME` to override the inferred project and `--title "…"` to set the
H1. `new` does not refresh `INDEX.md` (the doc is still empty) — run
`docs index` once the doc has content.

### Regenerating the index — `docs index`

When `INDEX.md` is stale — a doc was added, removed, archived, or its first
paragraph changed — run `docs index`. It rewrites only the marked block and is
idempotent: running it twice with no changes produces no diff. This is the verb
that replaces every hand-edit of `INDEX.md`. Use `docs index --root DIR` to
target a specific tree, and `--dry-run` to preview the regenerated file without
writing it.

### Archiving a doc — `docs archive`

When a doc is finished or superseded (a completed milestone, a closed plan),
run `docs archive <file>`. It sets `Status: archived`, bumps `Updated:`, moves
the file into `archive/<date>/`, and regenerates `INDEX.md` — atomically, in
that order. Never hand-move a doc into `archive/`. Use `--reason "…"` to record
why, `--date YYYY-MM-DD` to override the archive date, and `--cascade` to also
archive one-hop `pairs-with` / `child-of` relations (it prompts per file).

### Renaming or moving a doc — `docs mv`

When asked to rename or relocate a doc within the tree, run
`docs mv <old> <new>`. It moves the file and rewrites every `Related:` entry
across the whole tree that pointed at `<old>` — so references do not break.
Never hand-edit those `Related:` lines yourself; you will miss some. `<new>`
may be a new name in the same directory or a path into another directory under
the root. `mv` regenerates `INDEX.md`. (It rewrites `Related:` metadata only,
not prose links in doc bodies.)

### Listing docs — `docs list`

When asked which docs exist, or to list docs by status, role, project, or
staleness, run `docs list`. Filters AND-combine: `--status S`, `--role R`,
`--project P`, and `--stale N` (docs whose `Updated:` is more than N days old).
Add `--json` for a machine-readable array — one record per doc — when the
result feeds another step. The default output is a human table grouped by
status then role.

### Recording an edit date — `docs touch`

When a doc's body has been edited and the change should be dated, run
`docs touch <file>`. It bumps that doc's `Updated:` field to today and
regenerates `INDEX.md` — nothing else. Do not hand-edit the `Updated:` line;
use this verb so the date and the index stay in step.

### Checking the tree — `docs check`

Before a commit, in CI, or whenever the tree's health is in question, run
`docs check`. It validates every doc — required metadata present, vocabulary
valid, dates parseable, `Status:` matching on-disk location, `Related:` paths
resolving — and reports findings grouped by file. **Read the exit code**: `0`
means clean, `1` means warnings only (stale docs), `2` means errors that must
be fixed. In CI, exit `2` should fail the build. Pass a directory
(`docs check DIR`) to check a specific tree; add `--json` for machine-readable
findings and `--stale N` to also flag stale active docs.

### Adopting a foreign directory — `docs migrate`

When asked to bring an existing, non-conforming directory of Markdown into the
convention, run `docs migrate <dir>`. It is **dry-run by default**: it walks
the directory, infers the required metadata for every file, and prints a plan —
one decision per file, every ambiguity flagged — without writing anything.
Review that plan first. Re-run with `--apply` to insert the metadata blocks and
normalise archive-style subdirectories. Add `--json` to consume the plan
programmatically. `migrate` refuses a directory that is already a docs root.

## Where the convention itself lives

This skill teaches **which verb to run**, not the on-disk format. It does not
restate the metadata-block grammar, the `Status:` / `Role:` vocabulary, or the
archive layout — those have a single source of truth. For the format and
vocabulary, read the convention spec `convention.md`; for the full flag and
exit-code reference of every verb, read the CLI spec `cli.md`. (Both are named
here as plain references, not links — a doc-managed tree keeps them at its own
root, not inside this skill.) If a task needs a convention detail this skill
does not give, consult `convention.md` rather than guessing.
