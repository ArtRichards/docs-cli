# docs — CLI Spec

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-05-25

Related:
- pairs-with: convention.md

## Scope

This spec defines the `docs` command-line surface: subcommands, flags, output formats, and exit codes. The on-disk convention it operates on is defined in `convention.md`.

## Invocation

```
docs <subcommand> [args] [flags]
```

The binary expects to find a docs root by walking up from the current directory until it finds either `.docs.toml` or the directory passed via `--root`. If neither is present, `docs` operates on the current directory with defaults (project name = directory name, archive subdir = `archive/`).

Global flags:

- `--root DIR` — explicit docs root.
- `--json` — emit machine-readable JSON output where applicable.
- `--quiet` — suppress non-error output.
- `--dry-run` — show what would change; make no edits.
- `--version` — print `docs <version>` and exit 0.

## Subcommands

### `docs new <role> <slug> [--project NAME] [--title "…"] [--body-from PATH|-]`

Scaffold a new doc in the active tree.

- `<role>` must be in the built-in or configured Role vocabulary.
- `<slug>` becomes the filename (`<slug>.md`), created in the resolved docs root. A trailing `.md` on the slug is stripped. The slug may name a subdirectory (`sub/feature` → `sub/feature.md`); missing intermediate directories are created. The slug may **not** be an absolute path, contain a `..` component, or resolve under the archive subtree — those are rejected. To create a doc in the archive subtree use `docs archive`; to relocate an existing doc use `docs mv`.
- `--title` overrides the inferred H1 (default: the slug's last path segment, title-cased, with `-` and `_` treated as word separators).
- Writes the metadata block with `Lifecycle: draft`, `Role: <role>`, `Project: <inferred>`, `Updated: <today>`.
- Does not refresh INDEX (the new doc is empty; the user is expected to fill it, then run `docs index` or let another verb trigger it).
- `--body-from PATH` (M8 — F9) reads body content from `PATH` (or `-` for stdin) and appends it under the scaffolded frontmatter. Closes the read-before-write friction in agent flows — one atomic Bash call writes the complete file. The body text is appended verbatim (the file ends byte-equal with the body).
  - **Refusal heuristic (OQ-E).** The first 20 lines of the supplied body are scanned for `^[A-Z][A-Za-z-]+:\s`; if any line matches, `docs new` exits 2 with the message `--body-from content appears to contain a metadata block. Pass body content only — docs new owns the frontmatter.` plus the first five body lines as preview. The conservative regex catches accidental frontmatter dumps; a body line like `Plan: stage one then stage two` will trip the heuristic — pass content only.

Exits 2 on invalid role, invalid slug, missing `--body-from` path, or a body that trips the metadata-block refusal; 1 on existing file.

### `docs index [DIR] [--exclude PATTERN]`

Regenerate `INDEX.md` in the docs root.

- Walks the tree, parses every `.md` file's metadata.
- Rewrites only the content between `<!-- docs:generated start -->` and `<!-- docs:generated end -->` markers.
- Creates the markers if INDEX.md exists but lacks them; creates the whole file if it doesn't exist.
- Idempotent: running twice with no changes produces no diff.
- `--exclude PATTERN` (M8 — F3, repeatable) skips paths matching `PATTERN`. Layered on top of `.docs.toml [exclude]` and a root `.docsignore` — see [Common: exclusion](#common-exclusion) below.

Exits 0 always (warnings printed to stderr; use `docs check` for hard validation).

### `docs archive <file> [--reason "…"] [--date YYYY-MM-DD] [--cascade]`

Atomically archive a doc.

1. Reads `<file>`, validates it has required metadata.
2. Writes `Lifecycle: archived` and bumps `Updated:` to today (or `--date`).
3. Moves the file to `<archive_dir>/<YYYY-MM-DD>/<basename>`.
4. Regenerates INDEX.md.

`--reason` is appended as a free-form `Archived-reason:` metadata line (harvested but uninterpreted).

`--cascade` walks `Related: pairs-with` and `Related: child-of` and prompts to archive each related doc to the same dated directory. One hop only — no transitive cascade. Without `--cascade`, related docs are left in place (potential drift surfaced by `docs check`).

Atomicity: the metadata edit happens in a tmp file, fsync'd, renamed; the move happens only after the edit succeeds; the index regen runs last. A failure leaves the original file untouched.

Exits 1 on metadata-edit failure; 2 on archive-dir creation failure.

### `docs mv <old> <new>`

Move/rename a doc and rewrite every `Related:` reference that points at `<old>` across the tree.

- `<new>` may be a new filename in the same directory, or a different directory under the docs root.
- All matching `Related: <verb>: <old>` entries are rewritten to `<verb>: <new>`.
- INDEX regenerated.

Exits 1 on collision (`<new>` exists).

### `docs list [--lifecycle L] [--role R] [--project P] [--stale N] [--json] [--exclude PATTERN]`

Query view.

- Filters: `--lifecycle` (e.g., `active`), `--role` (e.g., `spec`), `--project` (slug), `--stale N` (Updated more than N days ago). Filters are AND-combined.
- Default human output: a table grouped by Lifecycle, then Role, sorted by Updated descending.
- `--json` emits an array of records, one per doc. Schema — **breaking change at M7 (1.2)** since the M3-pinned `status` field is renamed `lifecycle`:

  | Field | Type | Notes |
  |---|---|---|
  | `path` | string | Root-relative POSIX path of the doc. |
  | `title` | string | The H1 title. |
  | `lifecycle` | string | The `Lifecycle:` value. (M7 — was named `status` in v1.1 and earlier; renamed without alias per OQ-D.) |
  | `role` | string | The `Role:` value. |
  | `project` | string | The resolved project — the doc's `Project:` value, or the docs root's configured default when the doc has no `Project:` line. Never null. |
  | `updated` | string | The `Updated:` date as ISO `YYYY-MM-DD`, regardless of the configured `date_format`. |
  | `related` | array | Each entry an object `{verb, target}`; `target` is a root-relative path. Empty array when the doc has no `Related:` block. |
  | `extra_fields` | object | Maps each non-standard metadata label to its value: a string, or an array of strings for a bullet-list field. A free-form `Status:` prose line (M7 — F0) surfaces here. Empty object when there are none. |

> **`docs list --status` was renamed `docs list --lifecycle` at
> M7. The breaking-rename has no backward-compat alias.**

Exits 0.

### `docs check [DIR] [--stale N] [--json] [--exclude PATTERN]`

Validate the tree. Reports (and exits nonzero on) any of:

- Missing or empty required metadata fields (`Lifecycle`, `Role`, `Updated`).
- `Lifecycle` or `Role` not in the (built-in ∪ configured) vocab.
- `Updated:` not parseable as `YYYY-MM-DD`.
- Structural breakage: a missing H1. (A malformed line inside the metadata block ends the block early rather than raising; its effect surfaces as a missing required field, not as a separate finding.)
- Lifecycle/location mismatch (`Lifecycle: archived` outside archive subtree, or any other lifecycle inside) — rule `status-drift` (stable rule id from M3).
- `Related:` paths that don't resolve to a file under the docs root.
- (With `--stale N`) `Lifecycle: active` docs with `Updated:` more than N days ago.
- (M7 — F1) A missing `Role:` line whose value is resolvable from an H1
  trailing-word signal or a section-header pattern produces a
  medium-confidence inference — `severity: warning`, rule
  `medium-confidence-inference`, exit code 1.

Output is grouped by file; one line per finding. `--json` emits an array of records, one per finding. Schema — **stable from M3 onward**:

| Field | Type | Notes |
|---|---|---|
| `path` | string | Root-relative POSIX path of the doc. |
| `severity` | string | `error` or `warning`. |
| `rule` | string | Stable rule id: `missing-field`, `bad-vocab`, `bad-date`, `malformed`, `status-drift`, `broken-ref`, `stale`, or `medium-confidence-inference` (M7). |
| `message` | string | Human-readable description of the finding. |

Exit codes:
- 0 — clean.
- 1 — warnings only (stale docs; medium-confidence inferences).
- 2 — errors (missing required fields, invalid vocab, malformed structure, lifecycle/location drift, broken refs).

### `docs touch <file>`

Bump `Updated:` to today in `<file>`. No other changes. INDEX regenerated.

### `docs install-skill [--dest DIR] [--copy|--symlink] [--force] [--quiet]`

Materialise the bundled Claude Code skill onto the host.

Synopsis. The `docs-cli` wheel carries a `docs_cli/skill/` directory (the
[SKILL.md](../src/docs_cli/skill/SKILL.md) plus its bundled spec
references). `install-skill` copies (or symlinks) that directory to a
host-side location an agent driving Claude Code can read.

Flags:

- `--dest DIR` — destination directory. Default: `~/.claude/skills/docs/`.
- `--copy` — copy the bundled files (default).
- `--symlink` — symlink the destination to the in-tree source directory.
  Rejected when running from a wheel install (the bundled skill lives
  under `site-packages` and a future `pip install --upgrade docs-cli`
  could replace it from under the symlink). Editable installs only.
- `--force` — overwrite a non-identical existing destination.
- `--quiet` — suppress success messages on stderr.

Idempotency. If `<dest>` already exists and every bundled file matches
byte-for-byte, `install-skill` prints a no-op message and exits 0
without writing.

Refusals. Exits 2 if (a) `<dest>` exists with non-identical content
and `--force` was not supplied — the existing tree is preserved
unchanged in this case; or (b) `--symlink` was requested from a wheel
install. In both cases the message describes the recovery path
(`--force`, `--dest <DIR>`, or an editable install).

Windows note. `--symlink` may require developer-mode or elevated
privileges depending on the user's Windows-side configuration; the
default `--copy` is the recommended cross-platform path.

Exit codes:

- `0` — success (copy/symlink performed, or destination already matched
  byte-for-byte and the call was a no-op).
- `2` — refusal (non-identical dest without `--force`; or `--symlink`
  from a wheel install).

### `docs migrate <dir> [--apply] [--json | --summary] [--only ambiguous] [--group-by role|confidence] [--exclude PATTERN] [--exclude-ext EXTS] [--quiet] [--date YYYY-MM-DD] [--config-project NAME]`

Adopt a non-conforming foreign directory into the convention.

> **Breaking change since 1.1 (M7).** The controlled-vocab field
> on the metadata block is now `Lifecycle:` (was `Status:` in
> v1.1 and earlier). A free-form `Status:` line on a foreign doc
> is preserved verbatim under the `## Migrated metadata` body
> section (as `Migrated-Status:`); the inserted canonical block
> writes `Lifecycle:`. See `convention.md` for the operator
> rationale.

`migrate` walks `<dir>` recursively, inspects every `.md` file, infers the
metadata the convention requires, and produces a **migration plan** — one
decision per file, every ambiguity flagged. It is **dry-run by default**: it
only reports unless `--apply` is given. (This inverts the polarity of the other
mutating verbs, which write by default and take `--dry-run` to opt out — a bulk
inference-driven rewrite of a foreign tree is exactly the operation a user must
see before it runs.)

- `<dir>` is a required **positional** argument — the foreign directory to
  migrate. `migrate` takes **no `--root`**: a foreign tree carries no
  `.docs.toml` for an up-walk to resolve against.
- `migrate` refuses a directory whose `.docs.toml` carries the
  managed-root marker sections (`[project]`, `[archive]`,
  `[vocabulary]`). M7 (OQ5) narrows this: a `.docs.toml`
  containing ONLY a `[migrate]` section is a foreign-tree
  migration sidecar (e.g. `[migrate] project_name = "foo"`) and
  is read without refusing. M8 (OQ1) widens the carve-out
  further: when `[exclude]` is present in the `.docs.toml`, the
  refusal is waived even alongside the managed markers — the
  operator's explicit signal "use migrate to triage / re-migrate
  this managed tree but skip the listed paths".
- Without `--apply`, `migrate` writes nothing — it prints the plan (human, or
  `--json`) and exits.
- With `--apply`, `migrate` inserts the inferred metadata block into each file
  atomically and performs any archive-normalising moves. The result is a tree
  `docs check` accepts.
- `--date YYYY-MM-DD` sets the archive date used when normalising
  archive-style subdirectories into `archive/<date>/`. When set, the
  flag overrides every per-file date globally (M4 semantics
  retained). When absent, M7 (F4) uses each file's own
  `Updated:` (or mtime fall-back) per file, so a tree's mixed
  archival history maps to mixed `archive/<date>/` buckets.
- `--config-project NAME` (M7 — F5) pins the project name for
  every plan record. Bypasses project-name normalisation
  (F11). The persistent equivalent is a `[migrate]
  project_name = "NAME"` entry in the tree's `.docs.toml`.
  Precedence: CLI `--config-project` > sidecar > inferred-and-
  normalised.
- `--exclude PATTERN` (M8 — F3, repeatable) skips paths matching
  `PATTERN`. Layered on top of `.docs.toml [exclude]` and a
  root `.docsignore` — see [Common: exclusion](#common-exclusion)
  below.
- `--exclude-ext EXTS` (M8 — F3, comma-separated) suppresses
  files with the listed extensions from the non-Markdown
  sibling footer (and from any exclude-predicate evaluation).
  Use to silence binaries the operator's already aware of
  (`--exclude-ext html,xlsx,odt`).

**Triage flags (M8 — F6).** For a directory with > 20 files,
the default per-file plan scrolls past usefulness. Three flags
shape the output for rapid triage:

- `--summary` swaps the verbose per-file block for one
  tabular line per file (`path<60> role<12> conf<8> notes`).
  Mutually exclusive with `--json` (argparse rejects the
  combination with `--summary: not allowed with --json`).
- `--only ambiguous` filters the per-file plan to records
  with at least one ambiguity. Composes with `--summary` and
  `--group-by`.
- `--group-by role` / `--group-by confidence` sorts the
  per-file plan. `role` groups by Role alphabetically;
  `confidence` orders `high → medium → low`.

**Plan footer (M8 — F3/F5/F6/F7).** Every dry-run plan
(default or `--summary` mode) emits a footer block AFTER the
per-file output, in this order:

1. One line per excluded prefix bucket:
   `<N> files excluded under <prefix>` (per `[exclude]` /
   `.docsignore` / `--exclude` match).
2. One line surfacing non-Markdown root-level siblings (M8
   F7): `<N> non-Markdown siblings at root not considered:
   <names>`. Suppressed entirely when the displayed list is
   empty (after `--exclude-ext` filtering).
3. Multi-project hints (M7 F5; one line per detected subdir).
4. The default summary block (four lines, tokens always
   present so an agent parser can rely on them):
   ```
   summary: <N> files; <M> ambiguous (low=<x>, medium=<y>, high=<z>)
   roles: spec=<n1> plan=<n2> ...
   confidence: high=<n> medium=<n> low=<n>
   ambiguities: notes-fallback=<n1> synthesised-h1=<n2> ...
   ```
   The four tokens — `summary:`, `roles:`, `confidence:`,
   `ambiguities:` — are stable and always appear (even on an
   empty plan: `ambiguities: none` when no file has any).

**Inference rules.** For each file `migrate` infers the four required fields:

- **Role** — multi-pass:
  1. An in-file `Role:` line carrying a built-in role wins (high
     confidence).
  2. The filename's trailing token (split on `-`/`_`/whitespace
     AND case-transition so `MyPlan` → tokens `[My, Plan]`) is
     matched against the built-in suffix map (`-spec` → `spec`,
     `-plan` → `plan`, `-adr` → `decision`, `-log` → `log`,
     `-status`, `-charter`, `-guide`, `-runbook`, `-reference`,
     and the 7 M7 additions `-implementation`, `-sketch`,
     `-outline`, `-memo`, `-brief`, `-template`, `-example`).
     Per-tree custom mappings via `.docs.toml [migrate]
     role_suffixes` extend the built-in map. A trailing token
     that is itself a built-in role (`-decision`,
     `-milestone`, …) resolves directly. (high confidence.)
  3. A trailing `_M\d+` (case-insensitive, leading zeros OK)
     resolves to `milestone` — M7 F12 (medium confidence).
  4. Stripping a non-role suffix `_v\d+` / `_Draft` / `_Ready`
     and re-trying pass 2 — M7 F10 (medium confidence).
  5. Beyond filename: the H1 trailing word (`# Foo Plan` reads
     as `plan`); a section-header pattern (`## Goal` +
     `## Scope` + `## Requirements` reads as plan; the ADR
     pattern `Context`/`Decision`/`Consequences`; the log
     pattern of ≥ 2 dated `## YYYY-MM-DD` sections); and the
     sibling-set default — files in the same immediate subdir
     when ≥ 60% of ≥ 5 same-subdir suffix-confident siblings
     share one role — M7 F1 (medium confidence).
  6. Otherwise falls back to `notes` (low confidence, flagged
     as an ambiguity).
- **Project** — the longest common prefix shared by every `.md`
  basename, trimmed back to the last `-`/`_` separator; used
  only when it is ≥ 2 characters after trimming **and** shared
  by every file. Otherwise falls back to the directory name.
  M7 (F11) then **normalises** the result to lowercase-kebab
  via OQ-B: TitleCase boundaries (`FooBar` → `foo-bar`),
  letter↔digit boundaries (`Abc5Mig` → `abc-5-mig`), SNAKE_UPPER
  (`FOO_BAR` → `foo-bar`); digit-after-digit is NOT a split
  point so `bugs-2026-01-26` survives intact. When the
  normalisation changes the value, the human plan shows
  `project: <final> (normalised from "<original>")` once at
  the top of the output. A `--config-project NAME` CLI flag or
  a `.docs.toml [migrate] project_name = "NAME"` sidecar
  short-circuits normalisation entirely (precedence: CLI >
  sidecar > inferred-and-normalised).
- **Lifecycle** (M7-renamed; was `Status` in v1.1 and earlier)
  — from an in-file `Lifecycle:` line carrying a built-in
  value, else a default: `archived` for a file under a detected
  archive-style subdirectory, `active` otherwise. An out-of-
  vocabulary in-file value is rejected (the default is used)
  and the file is flagged low-confidence. A free-form `Status:`
  prose line carries no controlled-vocab signal and is
  preserved as an extra field (see "Preserving extra metadata"
  below).
- **Updated** — from an in-file `Updated:` line that parses in
  the configured date format, else the file's mtime, normalised
  to `YYYY-MM-DD`. M7 (F4) additionally uses each file's
  resolved `Updated:` (or mtime fall-back) as the **per-file
  archive-move date** when `--date` is absent.

`migrate` inserts the metadata block immediately under the H1, preserving the
body verbatim. If the file has no H1, one is synthesised from the filename.
Pre-existing metadata-shaped lines are reconciled into the block, not
duplicated. `Lifecycle`/`Role` are always written from the built-in vocabulary,
so an applied tree passes `docs check` by construction.

**Multi-project hints (M7 — F5).** When the inferred project
name covers the parent root but an immediate subdir's `.md`
files share a distinct common filename prefix AND cover ≥ 5
files, `migrate` surfaces a single advisory hint line in the
plan footer (suppressed when `--config-project` is set):

```text
hint: subdir 'foo-tools/' looks like a separate project
(common prefix 'foo_tools_', 6 .md files). Migrate it
independently: docs migrate foo-tools/ --config-project
foo-tools
```

The hint is informational — it does not block `--apply`. The
operator chooses one of three responses: ignore (let `foo-tools/`
inherit the parent project), exclude (skip the subdir) +
re-run on it, or `--config-project foo-tools` to pin the
sub-project name.

**Preserving extra metadata.** A foreign doc may carry metadata-shaped lines
beyond the four the convention requires — an `Owner:`, a `Tags:`, a `Related:`
block, a free-form `Status:` prose line (M7 — F0), any other
`Label: value` line. The four required fields
(`Lifecycle`/`Role`/`Project`/`Updated`) are superseded by the
inferred values, but every *other* field is **preserved**, never
dropped. `migrate` parks the preserved fields in a
`## Migrated metadata` body section, placed immediately below
the canonical metadata block and above the rest of the body,
and renames each label with a `Migrated-` prefix (`Owner:` →
`Migrated-Owner:`, `Status:` → `Migrated-Status:`, `Related:` →
`Migrated-Related:`, keeping any bullet sub-items beneath it
unchanged). A foreign doc with no extra fields gets no such
section. Because the preserved fields live in the body — under
a `## ` heading — `docs check` does not validate them, so a
stale foreign `Related:` path cannot fail the applied tree's
check. The dry-run plan reports how many extra fields each
file preserves.

**Archive-move collisions.** When two foreign files with the same basename
live in different archive-style subdirectories, both normalise to the same
`archive/<date>/<basename>` destination. `migrate` flags every such file as a
low-confidence ambiguity in the dry-run plan, and `--apply` refuses the run
(exit 2) rather than silently overwriting — resolve the collision before
re-running.

Every per-file decision records a **confidence** (`high`,
`medium`, or `low`) and, when the inference is not unambiguous,
one or more **ambiguity** notes — so the plan is *complete*:
every file has either a confident decision or a flagged
question. `medium` (M7 — OQ-D) is reserved for derived signals
(post-strip, `_M\d+`, H1 trailing word, section-header pattern,
sibling-set defaulting) and carries no ambiguity by contract.

`--json` emits the plan as an array of records, one per file. Schema —
**breaking change at M7 (1.2)** — the `status` key was renamed `lifecycle`,
and `confidence` widens to a three-level vocabulary:

| Field | Type | Notes |
|---|---|---|
| `path` | string | Root-relative POSIX path of the file. |
| `role` | string | Inferred `Role:` — always a built-in role. |
| `project` | string | Inferred (and F11-normalised, unless a CLI/sidecar override is set) `Project:` value. |
| `lifecycle` | string | Inferred `Lifecycle:` — always a built-in lifecycle vocab value. (M7 — was `status` in v1.1 and earlier; renamed without alias per OQ-D.) |
| `updated` | string | Inferred `Updated:` date as ISO `YYYY-MM-DD`. |
| `confidence` | string | `high`, `medium`, or `low`. `low` iff `ambiguities` is non-empty; `medium` is reserved for derived signals (OQ-D). |
| `ambiguities` | array | Human-readable note strings; empty when `confidence` is `high` or `medium`. |
| `archive_move` | string \| null | Root-relative destination when the file is moved into `archive/<date>/`, else null. The date is per-file (file's `Updated:`/mtime) when `--date` is absent; the explicit `--date` overrides globally. |
| `synthesized_h1` | boolean | True when the file had no H1 and one is synthesised. |
| `reconciled_metadata` | boolean | True when pre-existing metadata-shaped lines are reconciled into the block. |

> The F11 `(normalised from "<original>")` annotation and F5
> multi-project hints are **human-output only** — the `--json`
> record schema is intentionally flat. An agent reading `--json`
> already has every per-record value it needs to compute its
> own multi-project candidates, so the hint surface is not
> duplicated into machine output.

Exits 2 when `<dir>` is a managed docs root (`.docs.toml` carries
`[project]`/`[archive]`/`[vocabulary]`) or does not exist; 0 on
a successful dry-run or `--apply`.

## Common: exclusion

Four of the verbs (`migrate` / `index` / `check` / `list`) walk
a tree. M8 (F3) introduces a single layered exclusion surface
they all consult. The four sources combine **additively** — no
source replaces another:

1. **`.docs.toml [exclude]`** (persistent, per-tree). Three
   keys:
   - `dirs = ["build", "generated", "node_modules"]` —
     directory-name matches at any depth.
   - `globs = ["**/*.draft.md"]` — gitignore-flavoured glob
     patterns.
   - `exts = ["html", "xlsx"]` — extension matches.
2. **`.docsignore`** at the tree root (persistent, per-tree;
   one file only — nested files are NOT consulted, per OQ-B).
   One pattern per line, gitignore-flavoured syntax (subset):
   - `# comment` and blank lines are no-ops.
   - Trailing `/` → directory match.
   - Leading `/` → root-anchored (no nested match).
   - `**` → any segments; `*` → any chunk; `?` → one char.
   - Leading `!` → re-include (last match wins).
   - Bare pattern (no `/`) → match any path segment at any
     depth.
3. **`--exclude PATTERN`** on the CLI (ephemeral, one-off,
   repeatable). Same glob syntax as `.docsignore`.
4. **`--exclude-ext EXTS`** on `migrate` (one-off, csv).
   Extension matches; also suppresses the non-Markdown
   sibling footer.

The four sources are layered before the walk; an excluded
path is never read, parsed, or considered for INDEX / check /
list / migrate output. `migrate`'s plan footer surfaces the
total excluded count per top-level dir prefix
(`5 files excluded under build/`).

## Output conventions

- Human output goes to stdout; errors and progress to stderr.
- `--json` switches stdout to machine-readable; stderr unaffected.
- Color is off when stdout is not a TTY.
- All timestamps use the docs root's configured `[archive] date_format` (default `%Y-%m-%d`).

## Exit codes (summary)

| Code | Meaning |
|---|---|
| 0 | Success (or warnings-only on `check`) |
| 1 | Recoverable error (file conflict, validation warning, missing input) |
| 2 | Hard error (invalid vocab, atomic operation failure, validation errors) |

CI integration: `docs check` returning 2 should fail the build.
