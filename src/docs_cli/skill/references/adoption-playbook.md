# Adoption playbook

Lifecycle: active
Role: guide
Project: docs
Updated: 2026-05-27

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

> **Since 1.4 (M10).** `docs migrate --apply` now writes (or
> extends) the root `.docs.toml` sidecar automatically — an
> absent sidecar gets a minimal `[project] name = "<resolved>"`
> + `[archive] date_format` block; an existing sidecar without
> `[project]` gets the new block appended under a
> `# Added by docs migrate --apply` provenance comment header;
> an existing `[project]` is never overwritten. The old "decide
> when to write `.docs.toml`" ordering note is gone. `--apply
> --quiet` now suppresses the per-file plan block on stdout in
> addition to the trailing success line on stderr.

## Step 1 — Plan (`docs migrate <dir>`)

Run the migration helper in **dry-run mode** (the default) to
inspect every per-file decision before changing anything. Start
with the verbose plan to understand the tree, then switch to the
triage views for larger trees:

```
docs migrate path/to/dir                       # full per-file plan + footer
docs migrate path/to/dir --summary             # path  role  conf  notes per file
docs migrate path/to/dir --json | jq '. | length'           # how many files
docs migrate path/to/dir --json | jq '[.[] | .role] | unique'
docs migrate path/to/dir --json | jq '[.[] | select(.confidence == "low")]'
```

Each JSON record carries `path` / `role` / `project` /
`lifecycle` / `updated` / `confidence` / `ambiguities` /
`archive_move` / `synthesized_h1` / `reconciled_metadata`. The
schema is pinned by [`references/cli.md`](cli.md) (`docs migrate
--json` section).

The default plan footer carries a four-line summary block:

```
summary: <N> files; <M> ambiguous (low=<x>, medium=<y>, high=<z>)
roles: spec=<n1> plan=<n2> ...
confidence: high=<n> medium=<n> low=<n>
ambiguities: notes-fallback=<n1> synthesised-h1=<n2> out-of-vocab=<n3> collision=<n4>
```

Read it as a 30-second snapshot. The four tokens (`summary:`,
`roles:`, `confidence:`, `ambiguities:`) are stable so an agent
parser can rely on them.

Sanity checks:

- The `project` field on every record matches the directory's
  intended slug (kebab-case). If not, plan for the
  `--config-project NAME` flag in Step 3 or a `[migrate]
  project_name = "..."` sidecar in Step 2.
- The set of unique roles is a subset of the configured
  vocabulary. Unknown roles surface as `notes` with a
  low-confidence ambiguity flag.
- The count of low-confidence records is small relative to the
  total. A large low-confidence pile usually means the suffix
  convention isn't being recognised — plan for a `[migrate]
  role_suffixes = { ... }` mapping in Step 2.
- If `ambiguities` shows `collision=N>0`, two foreign files
  would normalise to the same `archive/<date>/` destination —
  fix in Step 2 (rename one before `--apply`) or accept that
  `--apply` will exit 2 to refuse the run.

## Step 2 — Triage (optional — only if Step 1 surfaced friction)

Reach for this step only when Step 1 surfaced friction worth
fixing before `--apply`. For a clean tree (high-confidence
everywhere, no collisions, no spurious non-Markdown siblings,
no project-name override needed), skip directly to Step 3.

Triage flags drive iteration on the dry-run plan:

```
docs migrate path/to/dir --summary --only ambiguous          # only rows needing attention
docs migrate path/to/dir --summary --group-by confidence     # high → medium → low
docs migrate path/to/dir --summary --group-by role           # cluster by role
```

Persistent tuning lives in a sidecar `.docs.toml` at the
migration root. The bundled template at
[`references/docs-toml-template.toml`](docs-toml-template.toml)
carries every section with examples commented out:

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
  values outside the built-in set, or extra metadata labels
  beyond the required four:
  ```toml
  [vocabulary]
  add_roles      = ["explainer"]
  add_lifecycles = ["experimental"]
  add_fields     = ["Owner", "Tags"]   # M10: opt-in unknown-field allowlist
  ```

A root-level `.docsignore` file (one pattern per line,
gitignore-flavoured) is consulted at the same layer as
`[exclude]`. Useful when the operator wants to keep
ignore-pattern data outside the TOML file or compose it with
existing `.gitignore`-style tooling.

One-off excludes (a single migration run) skip the sidecar
entirely and pass `--exclude PATTERN` / `--exclude-ext EXTS` on
the `--apply` command line. The persistent vs. one-off choice is
the operator's; both work.

Re-run `docs migrate <dir> --summary` after each `.docs.toml`
edit. The loop is bounded — every iteration changes only the
sidecar / CLI flags, not the source files. Three to five rounds
is typical for a 100-file tree; iterate until `--only ambiguous`
shows only the rows that are *intentionally* ambiguous (files
the operator really does want to land as `notes`).

## Step 3 — Apply (`docs migrate --apply --quiet <dir>`)

Once the dry-run plan is clean:

```
docs migrate path/to/dir --apply --quiet
```

`--apply` writes the inferred metadata block into every file the
plan covers (atomic edit — never partial), moves any
archive-style subdirs into `archive/<date>/<name>` per the M7
detection, opportunistically removes the now-empty source parent
dirs (M10 — OQ-G; non-migrating siblings survive), and writes (or
extends) the root `.docs.toml` sidecar (M10 — OQ-A):

- Absent sidecar → minimal `[project] name = "<resolved>"` +
  `[archive] date_format = "%Y-%m-%d"` block.
- Existing sidecar without `[project]` → new block appended at
  the bottom under a `# Added by docs migrate --apply`
  provenance comment header.
- Existing `[project]` → no-op (operator-authored config wins).

`--quiet` (M10 — OQ-B) suppresses the per-file plan block on
stdout in addition to the trailing
`docs: migrated <N> file(s) ...` success line on stderr. A clean
`--apply --quiet` run produces empty stdout + empty stderr —
ideal for unattended adoption. Drop `--quiet` if you want the
per-file plan echoed for debug visibility.

If the operator authored a `.docs.toml` in Step 2 with
`[project]` / `[archive]` / `[vocabulary]` but no `[exclude]`,
`--apply` refuses with the carve-out message:

```
docs: <dir> is already a docs root (.docs.toml has [...]) —
migrate is for foreign trees; use index / check / list instead.
```

The fix: either remove the managed-marker sections from the
sidecar (keeping ONLY `[exclude]` and/or `[migrate]`), or add an
`[exclude]` section (even an empty one — `[exclude]` on its own
line is enough to waive the refusal). Step 2's sidecar template
already exhibits the right shape (`[exclude]` + `[migrate]`
only); the managed `[project]` block is the M10 auto-write's
responsibility.

## Step 4 — Verify (`docs check <dir>`; commit)

The acceptance gate is `docs check` exit 0 on the adopted tree:

```
docs check path/to/dir       # exit 0 clean / 1 warnings / 2 errors
```

If `check` surfaces warnings (most commonly `stale` on docs the
tree hasn't touched in > 90 days, or `medium-confidence-inference`
on derived-signal Role: inferences), decide whether to age them
out via `docs touch <file> <file>...` per file or accept the
warnings and ship.

Smoke the INDEX regeneration:

```
docs index --root path/to/dir
git -C path/to/dir diff INDEX.md
```

The diff should be small and non-surprising. If you see large
blocks of churn, an `[exclude]` entry is probably missing — go
back to Step 2.

Commit:

```
git -C path/to/dir add -A && git commit -m "adopt <project> specs"
```

## Worked example

Adopting `~/old-specs/` — a 22-file directory with `Foo_Plan.md`,
`Foo_Spec.md`, `Foo_Strategy_v2.md`, a `build/` subdir holding 5
generated HTML-extracted Markdown files, and a top-level
`Foo-2024-deck.xlsx` slide deck.

**Step 1 — Plan:**

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
role suffix.

**Step 2 — Triage (write a sidecar `.docs.toml` for the excludes):**

```
cat > ~/old-specs/.docs.toml <<'EOF'
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
as `notes`.

**Step 3 — Apply:**

```
$ docs migrate ~/old-specs --apply --quiet
$ echo $?
0
```

Empty stdout + empty stderr — the apply landed cleanly. The
sidecar `.docs.toml` is now extended with the auto-emitted
`[project] name = "foo"` + `[archive] date_format` block under a
`# Added by docs migrate --apply` header; the operator's
`[exclude]` block is preserved verbatim.

**Step 4 — Verify + commit:**

```
$ docs check ~/old-specs
docs: no violations found
$ git -C ~/old-specs add -A && git commit -m "adopt foo specs"
```

Done in four commands + one config edit. `docs check` exit 0.

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
- **`[vocabulary] add_fields` is opt-in (M10 — OQ-H).** The
  `unknown-field` check rule fires only when the tree's
  `.docs.toml` carries `[vocabulary] add_fields = [...]` with
  at least one entry. Trees without the allowlist see no change
  — extra metadata labels are opaque to the rule. Matching is
  case-sensitive exact match (`add_fields = ["Owner"]` allows
  `Owner:` but not `owner:`).
