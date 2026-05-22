# docs — CLI Spec

Status: active
Role: spec
Project: docs
Updated: 2026-05-22

Related:
- implements: charter.md
- pairs-with: convention.md
- pairs-with: plan.md

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

## Subcommands

### `docs new <role> <slug> [--project NAME] [--title "…"]`

Scaffold a new doc in the active tree.

- `<role>` must be in the built-in or configured Role vocabulary.
- `<slug>` becomes the filename (`<slug>.md`), created in the resolved docs root. A trailing `.md` on the slug is stripped. The slug may name a subdirectory (`sub/feature` → `sub/feature.md`); missing intermediate directories are created. The slug may **not** be an absolute path, contain a `..` component, or resolve under the archive subtree — those are rejected. To create a doc in the archive subtree use `docs archive`; to relocate an existing doc use `docs mv`.
- `--title` overrides the inferred H1 (default: the slug's last path segment, title-cased, with `-` and `_` treated as word separators).
- Writes the metadata block with `Status: draft`, `Role: <role>`, `Project: <inferred>`, `Updated: <today>`.
- Does not refresh INDEX (the new doc is empty; the user is expected to fill it, then run `docs index` or let another verb trigger it).

Exits 2 on invalid role or invalid slug; 1 on existing file.

### `docs index [DIR]`

Regenerate `INDEX.md` in the docs root.

- Walks the tree, parses every `.md` file's metadata.
- Rewrites only the content between `<!-- docs:generated start -->` and `<!-- docs:generated end -->` markers.
- Creates the markers if INDEX.md exists but lacks them; creates the whole file if it doesn't exist.
- Idempotent: running twice with no changes produces no diff.

Exits 0 always (warnings printed to stderr; use `docs check` for hard validation).

### `docs archive <file> [--reason "…"] [--date YYYY-MM-DD] [--cascade]`

Atomically archive a doc.

1. Reads `<file>`, validates it has required metadata.
2. Writes `Status: archived` and bumps `Updated:` to today (or `--date`).
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

### `docs list [--status S] [--role R] [--project P] [--stale N] [--json]`

Query view.

- Filters: `--status` (e.g., `active`), `--role` (e.g., `spec`), `--project` (slug), `--stale N` (Updated more than N days ago). Filters are AND-combined.
- Default human output: a table grouped by Status, then Role, sorted by Updated descending.
- `--json` emits an array of records, one per doc. Schema — **stable from M3 onward**:

  | Field | Type | Notes |
  |---|---|---|
  | `path` | string | Root-relative POSIX path of the doc. |
  | `title` | string | The H1 title. |
  | `status` | string | The `Status:` value. |
  | `role` | string | The `Role:` value. |
  | `project` | string | The resolved project — the doc's `Project:` value, or the docs root's configured default when the doc has no `Project:` line. Never null. |
  | `updated` | string | The `Updated:` date as ISO `YYYY-MM-DD`, regardless of the configured `date_format`. |
  | `related` | array | Each entry an object `{verb, target}`; `target` is a root-relative path. Empty array when the doc has no `Related:` block. |
  | `extra_fields` | object | Maps each non-standard metadata label to its value: a string, or an array of strings for a bullet-list field. Empty object when there are none. |

Exits 0.

### `docs check [DIR] [--stale N] [--json]`

Validate the tree. Reports (and exits nonzero on) any of:

- Missing or empty required metadata fields (`Status`, `Role`, `Updated`).
- `Status` or `Role` not in the (built-in ∪ configured) vocab.
- `Updated:` not parseable as `YYYY-MM-DD`.
- Structural breakage: a missing H1. (A malformed line inside the metadata block ends the block early rather than raising; its effect surfaces as a missing required field, not as a separate finding.)
- Status/location mismatch (`Status: archived` outside archive subtree, or any other status inside).
- `Related:` paths that don't resolve to a file under the docs root.
- (With `--stale N`) `Status: active` docs with `Updated:` more than N days ago.

Output is grouped by file; one line per finding. `--json` emits an array of records, one per finding. Schema — **stable from M3 onward**:

| Field | Type | Notes |
|---|---|---|
| `path` | string | Root-relative POSIX path of the doc. |
| `severity` | string | `error` or `warning`. |
| `rule` | string | Stable rule id: `missing-field`, `bad-vocab`, `bad-date`, `malformed`, `status-drift`, `broken-ref`, or `stale`. |
| `message` | string | Human-readable description of the finding. |

Exit codes:
- 0 — clean.
- 1 — warnings only (stale docs).
- 2 — errors (missing required fields, invalid vocab, malformed structure, status drift, broken refs).

### `docs touch <file>`

Bump `Updated:` to today in `<file>`. No other changes. INDEX regenerated.

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

## What's deliberately not in v1

- `docs migrate <foreign-dir>` — import an existing non-conforming directory. Deferred to a later milestone; see `plan.md`.
- `docs graph` — traverse `Related:` edges. Out of scope.
- Watch mode / file-system observers. Run on demand.
- Templates beyond `docs new` defaults. If users want richer scaffolds, they hand-edit after creation.
