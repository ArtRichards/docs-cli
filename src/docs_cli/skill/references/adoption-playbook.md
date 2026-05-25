# Adoption playbook

Lifecycle: active
Role: guide
Project: docs
Updated: 2026-05-25

Related:
- child-of: SKILL.md
- references: cli.md
- references: convention.md

## When this applies

The user has a directory of foreign Markdown specs — a `specs/`
checkout from a sibling repo, a SharePoint export, a `.md` dump
from a planning tool — and wants the agent to adopt it into the
`docs` convention.

Signals:

- "adopt this directory"
- "migrate this folder"
- "bring this into docs convention"
- "import existing markdown specs"
- The directory has no `.docs.toml`, or has one carrying only
  `[migrate]` / `[exclude]`.

Skip this playbook when:

- The directory is already a managed `docs` tree (`.docs.toml`
  with `[project]` / `[archive]` / `[vocabulary]` and no
  `[exclude]`). Run `docs check` / `docs index` directly.
- The user wants only a one-off file rename or metadata bump.
  Use `docs new` / `docs touch` / `docs archive` directly.

## Step 1 — Dry-run plan (`docs migrate --json <dir>`)

Run the migration helper in **dry-run JSON mode** to inspect
every per-file decision before changing anything:

```
docs migrate path/to/dir --json | jq '. | length'      # how many files
docs migrate path/to/dir --json | jq '[.[] | .role] | unique'
docs migrate path/to/dir --json | jq '[.[] | select(.confidence == "low")]'
```

Each record carries `path` / `role` / `project` / `lifecycle` /
`updated` / `confidence` / `ambiguities` / `archive_move` /
`synthesized_h1` / `reconciled_metadata`. The schema is pinned by
[`references/cli.md`](cli.md) (`docs migrate --json` section).

Sanity checks:

- The `project` field on every record matches the directory's
  intended slug (kebab-case). If not, plan for the
  `--config-project NAME` flag in Step 4 or a `[migrate]
  project_name = "..."` sidecar.
- The set of unique roles is a subset of the configured
  vocabulary. Unknown roles surface as `notes` with a low-
  confidence ambiguity flag.
- The count of low-confidence records is small relative to the
  total. A large low-confidence pile usually means the suffix
  convention isn't being recognised — plan for a
  `[migrate] role_suffixes = { ... }` mapping in Step 3.

## Step 2 — Triage the plan (`--summary`, `--only ambiguous`, `--group-by`)

For a directory with > 20 files, the verbose per-file plan
scrolls past usefulness. Drive triage with M8's triage flags:

```
docs migrate path/to/dir --summary                       # path  role  conf  notes
docs migrate path/to/dir --summary --only ambiguous      # only the rows needing attention
docs migrate path/to/dir --summary --group-by confidence # high → medium → low
docs migrate path/to/dir --summary --group-by role       # cluster by role
```

The default plan footer (`docs migrate path/to/dir` with no
flags) carries a four-line summary block:

```
summary: <N> files; <M> ambiguous (low=<x>, medium=<y>, high=<z>)
roles: spec=<n1> plan=<n2> ...
confidence: high=<n> medium=<n> low=<n>
ambiguities: notes-fallback=<n1> synthesised-h1=<n2> out-of-vocab=<n3> collision=<n4>
```

Read it as a 30-second snapshot. If `ambiguities` shows
`collision=N>0`, two foreign files would normalise to the same
`archive/<date>/` destination — fix in Step 3 / Step 4 before
running `--apply`.

If the footer also surfaces a `N non-Markdown siblings at root
not considered: ...` line, the migration root has non-`.md` files
(HTML / XLSX / ODT / etc.). Decide:

- Keep referenced via a Markdown sidecar? Write the sidecar via
  `docs new <role> <slug> --body-from -` (see Step 5; this is
  M8's F9 ergonomics) and link the binary via
  `Related: artifact-of: <binary>`.
- Suppress noise via `--exclude-ext html,xlsx,odt` (one-off) or
  `[exclude] exts = [...]` (persistent).

## Step 3 — Decide on excludes (write a sidecar `.docs.toml` ONLY if persistent)

> **IMPORTANT ordering note.** `docs migrate --apply` refuses a
> tree whose `.docs.toml` carries `[project]` / `[archive]` /
> `[vocabulary]` **unless** that `.docs.toml` also carries an
> `[exclude]` section. The M8 carve-out (OQ1) is the operator's
> explicit signal "use migrate on this managed tree but skip
> the listed paths". The practical consequence:
>
> - **If the tree needs NO persistent excludes** (small kebab-
>   tiny-style trees), DO NOT write a `.docs.toml` before
>   `--apply`. Run `--apply` first; write the `.docs.toml`
>   carrying `[project]` (and any other managed-marker config)
>   AFTER `--apply`. See Step 5 / Step 6 below.
> - **If the tree needs persistent excludes** (build dirs,
>   draft files, etc.), write a sidecar `.docs.toml` with ONLY
>   `[exclude]` (no `[project]`/`[archive]`/`[vocabulary]`) and
>   run `--apply`. After `--apply`, extend the same `.docs.toml`
>   with `[project]` etc. for the persistent managed state.
> - **If the tree needs one-off excludes** (a single migration
>   run), skip writing `.docs.toml` here entirely; pass
>   `--exclude PATTERN` and/or `--exclude-ext EXTS` on the
>   `--apply` command line.

The bundled template at
[`references/docs-toml-template.toml`](docs-toml-template.toml)
carries every section M8 reads — `[exclude]`, `[migrate]`,
`[vocabulary]`, plus the M7 `[project]` / `[archive]` defaults
— with every example line commented out. Read it once, then
copy the relevant snippets into a `.docs.toml` at the migration
root:

```
cat references/docs-toml-template.toml > path/to/dir/.docs.toml
$EDITOR path/to/dir/.docs.toml
```

The four sections most likely to need tuning during adoption:

- **`[exclude]`** for generated-data dirs, draft-only files, and
  binary-extension noise:
  ```toml
  [exclude]
  dirs   = ["build", "generated", ".cache"]
  globs  = ["**/*.draft.md"]
  exts   = ["html", "xlsx", "odt"]
  ```
- **`[migrate] role_suffixes`** when the source tree uses
  filename suffixes the built-in mapping doesn't recognise:
  ```toml
  [migrate]
  role_suffixes = { "-rubric" = "template", "-memo" = "notes" }
  ```
- **`[migrate] project_name`** when the directory name doesn't
  match the intended project slug:
  ```toml
  [migrate]
  project_name = "foo-bar"
  ```
- **`[vocabulary]`** when the tree carries Role or Lifecycle
  values outside the built-in set:
  ```toml
  [vocabulary]
  add_roles      = ["explainer"]
  add_lifecycles = ["experimental"]
  ```

A root-level `.docsignore` file (one pattern per line,
gitignore-flavoured) is consulted at the same layer as
`[exclude]`. Useful when the operator wants to keep
ignore-pattern data outside the TOML file or compose it with
existing `.gitignore`-style tooling.

## Step 4 — Iterate (re-run migrate; tune excludes + config)

Re-run `docs migrate <dir> --summary` after each `.docs.toml`
edit. The triage loop:

1. Add / remove `[exclude]` entries until the per-file count
   matches the operator's expectation.
2. Inspect `--only ambiguous` until every remaining low-
   confidence record is *intentionally* ambiguous (e.g. files
   the operator really does want to land as `notes`).
3. Decide on `--config-project NAME` if the inferred project
   slug isn't right and a sidecar `[migrate] project_name`
   isn't what you want for this run.
4. Check the `multi_project_hints` footer lines. Each hint
   surfaces a subdir whose `.md` files look like a separate
   project (≥ 5 files with a distinct shared prefix). Migrate
   each subdir independently with its own `--config-project`.

The loop is bounded — every iteration changes only the
`.docs.toml` / CLI flags, not the source files. Repeat until the
plan reads cleanly. Three to five rounds is typical for a 100-
file tree.

## Step 5 — Apply (`docs migrate --apply <dir>`)

Once the dry-run plan is clean:

```
docs migrate path/to/dir --apply
```

`--apply` writes the inferred metadata block into every file
the plan covers (atomic edit — never partial), then moves any
archive-style subdirs into `archive/<date>/<name>` per the M7
detection. Already-conformant files are left untouched.

(`--quiet` is available but only suppresses the trailing
stderr success line — per-file edit output still prints.)

**Ordering reminder (per Step 3).** If you authored a
`.docs.toml` carrying `[project]`/`[archive]`/`[vocabulary]`
WITHOUT also adding `[exclude]`, `--apply` will refuse with:

```
docs: <dir> is already a docs root (.docs.toml has [...]) —
migrate is for foreign trees; use index / check / list instead.
```

The fix: either remove the managed-marker sections from the
sidecar `.docs.toml` (keeping ONLY `[exclude]` + `[migrate]`),
or add an `[exclude]` section (even an empty one — `[exclude]`
on its own line is enough to waive the refusal). The
recommended pattern for trees that don't need persistent
excludes is to write the `[project]`-bearing `.docs.toml` AFTER
`--apply` (Step 6).

## Step 6 — Verify (`docs check <dir>` exit 0; write final `.docs.toml`; commit)

The acceptance gate is `docs check` exit 0 on the adopted tree:

```
docs check path/to/dir       # exit 0 clean / 1 warnings / 2 errors
```

If the tree has no `.docs.toml` yet (because Step 3 deferred
writing one), this is the moment to author it. The simplest
form for a project that needs no persistent excludes:

```toml
[project]
name = "my-project"
```

(Per Step 3's note, writing this BEFORE `--apply` would have
triggered the carve-out refusal; writing it AFTER `--apply` is
fine because the metadata is already in place and `check` /
`index` consult `.docs.toml` without the refusal logic.)

If `check` surfaces warnings (most commonly `stale` on docs the
tree hasn't touched in > 90 days), decide whether to age them
out via `docs touch` per file or accept the warnings and ship.

Smoke the index regeneration:

```
docs index --root path/to/dir
git -C path/to/dir diff INDEX.md
```

The diff should be small and non-surprising. If you see large
blocks of churn, an `[exclude]` entry is probably missing — go
back to Step 3.

## Worked example

Adopting `~/old-specs/` — a 22-file directory with `Foo_Plan.md`,
`Foo_Spec.md`, `Foo_Strategy_v2.md`, a `build/` subdir holding 5
generated HTML-extracted Markdown files, and a top-level
`Foo-2024-deck.xlsx` slide deck.

```
$ docs migrate ~/old-specs --summary
Foo_Architecture.md                                       notes        low      Role inferred as 'notes' fallback ...
Foo_Plan.md                                               plan         high     -
Foo_Spec.md                                               spec         high     -
Foo_Status.md                                             status       high     -
Foo_Strategy_v2.md                                        notes        low      Role inferred as 'notes' fallback ...
build/extracted_1.md                                      notes        low      Role inferred as 'notes' fallback ...
build/extracted_2.md                                      notes        low      Role inferred as 'notes' fallback ...
...

summary: 22 files; 7 ambiguous (low=7, medium=0, high=15)
roles: notes=7 plan=4 spec=6 status=5
confidence: high=15 medium=0 low=7
ambiguities: notes-fallback=7
1 non-Markdown siblings at root not considered: Foo-2024-deck.xlsx
```

Decision: the `build/` subdir is generated data; the
`Foo-2024-deck.xlsx` is a referenced binary; the `_v2` suffix on
`Foo_Strategy_v2.md` looks like a draft revision marker, not a
role suffix. Adopt as follows:

```
cat > ~/old-specs/.docs.toml <<'EOF'
[project]
name = "foo"

[exclude]
dirs = ["build"]
exts = ["xlsx"]
EOF
```

Re-run:

```
$ docs migrate ~/old-specs --summary
Foo_Architecture.md                                       notes        low      Role inferred as 'notes' fallback ...
Foo_Plan.md                                               plan         high     -
Foo_Spec.md                                               spec         high     -
Foo_Status.md                                             status       high     -
Foo_Strategy_v2.md                                        notes        low      Role inferred as 'notes' fallback ...
...

summary: 17 files; 2 ambiguous (low=2, medium=0, high=15)
roles: notes=2 plan=4 spec=6 status=5
confidence: high=15 medium=0 low=2
ambiguities: notes-fallback=2
5 files excluded under build/
```

Five `build/*` files excluded; the xlsx is silently dropped from
the non-md sibling footer. Two genuine ambiguities remain (the
`Foo_Architecture` + `Foo_Strategy_v2` files inferring as `notes`
fallback) — acceptable; the operator confirms those should land
as `notes` and runs:

```
docs migrate ~/old-specs --apply
docs check ~/old-specs
git -C ~/old-specs add -A && git commit -m "adopt foo specs"
```

Done in three commands + one config edit. `docs check` exit 0.

## Pitfalls

- **`Status:` vs `Lifecycle:` (M7 F0).** The convention's
  in-file field is `Lifecycle:`, not `Status:`. A foreign tree
  with `Status: active` lines will have those lines preserved
  via the extra-field pathway; the `migrate` helper inserts a
  fresh `Lifecycle:` line in the metadata block. Do NOT hand-
  rename `Status:` to `Lifecycle:` — let `migrate` do it.
- **`_v2` / `_Draft` non-role suffixes (M7 F10).** `Foo_v2.md`
  is treated as a `notes` fallback, not a role-suffixed file.
  This is intentional — `_v2` is a revision marker, not a role.
  Decide per-file whether the file's *real* role can be
  recovered from an H1 sweep + add a `[migrate] role_suffixes`
  entry, or accept the `notes` landing.
- **Inferred project name needs override (M7 F5 + F11).** When
  the directory name doesn't normalise cleanly (e.g. `FooBar`),
  the inferred project will be `foo-bar`. Override via
  `--config-project NAME` (one-off) or `[migrate] project_name`
  (persistent). The original-name annotation surfaces ONCE at
  the top of the dry-run plan as
  `project: foo-bar (normalised from "FooBar")`.
- **Generated-data dirs need `--exclude` (M8 F3).** Files under
  `build/`, `generated/`, `.cache/`, `node_modules/`, etc. will
  parse cleanly and land in the plan. Use `[exclude] dirs = [
  ... ]` to keep them out of the convention permanently.
- **Sidecars for non-md binaries (M8 F7 + F9).** When a non-md
  file (a slide deck, a spreadsheet) is referenced from prose,
  author a Markdown sidecar via `docs new <role> <slug>
  --body-from -` — single Bash call, atomic; the sidecar carries
  the convention's metadata, then links the binary via
  `Related: artifact-of: <binary>`. The OQ-E refusal heuristic
  catches bodies that accidentally contain a metadata-shaped
  block (`^[A-Z][A-Za-z-]+:\s`) — pass body content only;
  `docs new` owns the frontmatter.
- **Multi-project subdir (F5 hint).** If `multi_project_hints`
  surfaces a subdir that looks like a separate project (≥ 5
  files with a shared prefix distinct from the parent's), do
  NOT force-migrate the whole tree under one project — migrate
  the subdir independently with its own `--config-project`.
