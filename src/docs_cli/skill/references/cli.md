# docs — CLI Spec

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-06-12

Related:
- pairs-with: convention.md

## Scope

This spec defines the `docs` command-line surface: subcommands, flags, output formats, and exit codes. The on-disk convention it operates on is defined in `convention.md`.

## Invocation

```
docs <subcommand> [args] [flags]
```

The binary expects to find a docs root by walking up from the current directory until it finds either `.docs.toml` or the directory passed via `--root`. If neither is present, the **read** verbs (`index`, `list`, `check`) operate on the current directory with defaults (project name = directory name, archive subdir = `archive/`).

**Create/mutate refusal (M14 — A2; M12 — OQ-C).** The verbs that *create* a doc (`docs new`) or stamp/rename in place (`docs touch`, `docs project rename`) refuse the cwd-as-root fallback: if no `.docs.toml` is found up the ancestor chain and no `--root` is given, they exit 2 and write nothing rather than silently scaffolding into an unmanaged directory with default config. (The read verbs above keep the silent cwd-fallback — surfacing the wrong tree on a read is recoverable; writing into it is not.) See each verb's Exits paragraph for the exact message.

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
- `<slug>` becomes the filename (`<slug>.md`), created in the resolved docs root. A trailing `.md` on the slug is stripped. The slug may name a subdirectory (`sub/feature` → `sub/feature.md`); missing intermediate directories are created. The slug may **not** be an absolute path, contain a `..` component, or resolve under the archive subtree — those are rejected. The slug's **final path segment may not be empty** (M14 — A3): `foo/` or `foo/.md` would write an invisible `foo/.md` dotfile (skipped by every read verb), so it is rejected with exit 2 `docs: invalid slug <slug>`. To create a doc in the archive subtree use `docs archive`; to relocate an existing doc use `docs mv`.
- `--title` overrides the inferred H1 (default: the slug's last path segment, title-cased, with `-` and `_` treated as word separators).
- Writes the metadata block with `Lifecycle: draft`, `Role: <role>`, `Project: <inferred>`, `Updated: <today>`.
- Does not refresh INDEX (the new doc is empty; the user is expected to fill it, then run `docs index` or let another verb trigger it).
- `--body-from PATH` (M8 — F9) reads body content from `PATH` (or `-` for stdin) and appends it under the scaffolded frontmatter. Closes the read-before-write friction in agent flows — one atomic Bash call writes the complete file. The body text is appended verbatim (the file ends byte-equal with the body).
  - **Refusal heuristic (OQ-E; M15 — C4).** The supplied body is refused
    **only when it carries an actual metadata block**, not whenever any line is
    `Label:`-shaped. Two signals trip the refusal:
    - **(a) a leading `---` YAML fence** — the first non-blank line of the body
      is `---`, the footgun of pasting a whole front-matter-fenced document as a
      body; or
    - **(b) a required-field cluster** — within the first ~20 lines (after an
      optional leading `# H1`), a **contiguous run** of metadata-shaped lines
      carries **≥ 2** of the required-field labels `{Lifecycle, Role, Updated}`
      on adjacent lines. This is the shape of a real convention metadata block
      (the footgun of pasting a whole doc-with-frontmatter as a body).

    A **lone** prose required-field line (a single `Updated:`/`Reason:`/`Plan:`
    line in spec/test-matrix prose) no longer trips the refusal — it is
    accepted and appended verbatim. (`Reason:`/`Plan:` are not even required-
    field labels, so they never contribute to the cluster; this is exactly the
    dogfood body — a test-matrix section opening `## Risk level` / `Reason: …` —
    that the old any-`Label:` heuristic wrongly refused. `edge-case-keyword.md`,
    whose only metadata-shaped line is a prose `Plan:` line, now **passes**.)

    On a refusal `docs new` exits 2 with the message `--body-from content
    appears to contain a metadata block. Pass body content only — docs new owns
    the frontmatter.` plus the first five body lines as preview (the stable
    error tokens are unchanged from M8).

**Strict-root refusal (M14 — A2).** `docs new` refuses the silent
cwd-as-root fallback (which once misfired by scaffolding a doc at a repo
root with default config). Resolution mirrors `docs touch` /
`docs project rename` (M12 — OQ-C):

- If `--root` is **not** given and no `.docs.toml` exists in the cwd's
  ancestor chain, `docs new` exits 2 + stderr
  `docs: new: <cwd> is not under a docs root with .docs.toml; refusing`
  and writes nothing.
- An explicit `--root <dir>` bypasses the up-walk **only when**
  `<dir>/.docs.toml` exists; if `--root` is set but its `.docs.toml` is
  missing, `docs new` refuses with
  `docs: new: --root <root> does not contain .docs.toml; refusing`
  (exit 2).

Exits 2 on invalid role, invalid slug, missing `--body-from` path, a body that trips the metadata-block refusal (a leading `---` fence or a ≥ 2 required-field cluster — M15 C4), or the strict-root refusal; 1 on existing file.

### `docs index [DIR] [--exclude PATTERN]`

Regenerate `INDEX.md` in the docs root.

- Walks the tree, parses every `.md` file's metadata.
- Rewrites only the content between `<!-- docs:generated start -->` and `<!-- docs:generated end -->` markers.
- Creates the markers if INDEX.md exists but lacks them; creates the whole file if it doesn't exist.
- Idempotent: running twice with no changes produces no diff.
- `--exclude PATTERN` (M8 — F3, repeatable) skips paths matching `PATTERN`. Layered on top of `.docs.toml [exclude]` and a root `.docsignore` — see [Common: exclusion](#common-exclusion) below.

Exits 0 always (warnings printed to stderr; use `docs check` for hard validation).

### `docs archive <file> [--reason "…"] [--date YYYY-MM-DD] [--cascade | --cascade-dry-run | --cascade-only GLOB | --interactive]`

Atomically archive a doc.

1. Reads `<file>`, validates it has required metadata.
2. Writes `Lifecycle: archived` and bumps `Updated:` to today (or `--date`).
3. Moves the file to `<archive_dir>/<YYYY-MM-DD>/<basename>`.
4. Regenerates INDEX.md.

`--reason` is appended as a free-form `Archived-reason:` metadata line (harvested but uninterpreted).

**Invariant: `docs` never prompts unless `--interactive` (M14 — B1).**
Every verb runs to completion (or refuses with a non-zero exit) without
ever blocking on stdin, so an autonomous agent never stalls. The
cascade surface below is the canonical example: bare `--cascade`
archives the whole one-hop set with no prompt; the legacy `[y/N]`
prompt is opt-in behind `--interactive`.

The cascade follows `Related: pairs-with` and `Related: child-of`
edges. **One hop only — no transitive cascade.** Without any cascade
flag, related docs are left in place (potential drift surfaced by
`docs check`). Four mutually-exclusive flags shape the cascade
(M14 — B1):

- **`--cascade`** archives *every* one-hop `pairs-with` / `child-of`
  relation that still exists on disk, to the same dated directory, with
  **no prompt**. A loud stderr footer names the cascaded set so the
  operator (or an agent reading stderr) sees exactly what moved:
  `docs: cascade archived N related doc(s): <rel1>, <rel2>, …`. When the
  set is empty the footer is `docs: cascade: no one-hop relations to archive`.
- **`--cascade-dry-run`** prints the would-be cascade set (one
  `docs: cascade would archive <rel>` line per related doc, on stderr)
  and the footer, then **writes nothing** and exits 0. The primary doc
  is not archived either — `--cascade-dry-run` is a preview of the whole
  cascade operation, equivalent to `--cascade --dry-run`.
- **`--cascade-only GLOB`** archives the *subset* of the one-hop set
  whose related-doc **root-relative POSIX target path** matches `GLOB`.
  `GLOB` is compiled by the same matcher `compile_exclude_predicate`
  uses (gitignore-flavoured: `**`, `*`, `?`; bare patterns match any
  path segment at any depth). The primary doc is always archived;
  related docs outside the glob are left in place and named in the
  footer. Composes with `--cascade-dry-run` (preview the filtered
  subset, write nothing).
- **`--interactive`** restores the legacy behaviour: each one-hop
  relation prompts `docs: also archive <rel>? [y/N] ` on stderr and is
  archived only on a `y`/`yes` answer. This is the **only** way to make
  `docs archive` read stdin.

**Combination matrix.** `--cascade`, `--cascade-only`, and
`--interactive` are mutually exclusive (argparse rejects any pair with
exit 2). `--cascade-dry-run` composes with `--cascade-only` (preview the
filtered subset) but is **rejected together with `--interactive`** via
an argparse mutually-exclusive group (a dry-run that prompts is
incoherent). `--cascade-dry-run` alone is shorthand for
`--cascade --dry-run`. The global `--dry-run` applied to any cascade
mode previews without writing.

Atomicity: the metadata edit happens in a tmp file, fsync'd, renamed; the move happens only after the edit succeeds; the index regen runs last. A failure leaves the original file untouched.

**Referring-edge rewrite (M12).** After the move, `docs archive`
rewrites every `Related: <verb>: <old-rel>` bullet across the active
tree to point at `archive/<YYYY-MM-DD>/<basename>`. Mirrors `docs mv`'s
walker (`rewrite_related_refs`) — only the `Related:` field is
considered; prose markdown references are deliberately left alone.
The rewrite is part of the same atomic batch as the move + lifecycle
edit: a single end-of-batch INDEX refresh covers everything. That
refresh honours `[exclude]` / `.docsignore` (M14 — A6) — a malformed
*excluded* file never fails the post-move reindex (same threading as
`docs touch`, above).

**Archive-subtree edge integrity (M18).** The referring-edge rewrite
now repoints **two** edge classes to the new
`archive/<YYYY-MM-DD>/<basename>` path, so that archiving interrelated
docs into the archive subtree never orphans their `Related:` edges:

1. **The moved doc's OWN `Related:` bullets** whose target is *itself* a
   doc moving in the same archive operation. Under `--cascade` a
   pair/trio lands with every intra-archive edge resolved (e.g. a plan
   and its log archived together each end up pointing at the other's new
   archive path); a *solo* archive of a doc whose co-moving target set is
   empty changes none of its own edges.
2. **Already-archived referrers** whose bullet points at a doc moving
   into the archive in this op — repointed to the doc's new archive path
   (previously left dangling, since the rewriter skipped archived docs).

The "targets that moved" set is defined precisely as exactly the batch's
`moves`: the primary archive target plus every cascaded relation, each
carried as an `(old_rel, new_rel)` pair. An edge is rewritten **iff** its
current target equals some `old_rel` in that batch — never any other
archived-doc content. Both classes are handled by the same
`rewrite_related_refs` matcher and land in the same atomic batch as the
move (one end-of-batch INDEX refresh).

This **narrows** the prior "archive subtree is read-only" stance (M3):
archive-subtree docs are read-only **except** `Related:` bullets pointing
at a doc moving in the same archive operation, which are repointed to the
new archive path. All other archived-doc content — prose, other metadata,
and edges to docs that did *not* move — is left byte-identical.

The cascade flags (M12 — OQ-D; M14 — B1) extend this — when the cascade
archives related docs B, C, …, the referring-edge rewrites for every
moved doc run as a single atomic batch with one INDEX refresh at the
end. Per-doc cascade-archive failures still surface but only docs that
actually moved get their referring edges rewritten. Cascade remains
one-hop only (M2 decision unchanged).

Exits 1 on metadata-edit failure; 2 on archive-dir creation failure, an
`OSError` raised while rewriting a referring edge after the move
(M14 — A4), or an invalid cascade-flag combination. `--cascade-dry-run`
exits 0 and writes nothing.

### `docs mv <old> <new>`

Move/rename a doc and rewrite every `Related:` reference that points at `<old>` across the tree.

- `<new>` may be a new filename in the same directory, or a different directory under the docs root.
- All matching `Related: <verb>: <old>` entries are rewritten to `<verb>: <new>`.
- INDEX regenerated. The end-of-batch refresh honours `[exclude]` /
  `.docsignore` (M14 — A6) — a malformed *excluded* file never fails the
  post-move reindex (same threading as `docs touch`).

**Atomic — all-or-nothing (M14 — A1).** A validate-all-first pre-flight
walk runs *before* the move: if any (non-excluded) doc in the tree is
malformed, `docs mv` aborts with **exit 2** *before* moving anything,
leaving the source in place, the destination absent, and every referring
`Related:` edge untouched (no dangling edge, no stray INDEX). An `OSError`
raised while rewriting a referring doc *after* the move (e.g. a referrer
in a read-only directory) is mapped to a clean **exit 2** rather than an
uncaught traceback (M14 — A4).

**Moved-doc own-edge rewrite (M18 — D3).** Like `docs archive`'s D1,
`docs mv` repoints the MOVED doc's OWN `Related:` bullets when their
target is the doc being moved — via the same shared `rewrite_related_refs`
walker that already rewrites referrers tree-wide. So moving a doc whose
`Related:` target already lives under `archive/` (or self-referential
bullets the move touches) lands the moved doc with its own edges
resolving, not dangling. `docs mv` already rewrites already-archived
referrers (its walk carries no `doc.archived` skip), so this completes
the own-edge half and gives `mv` the same edge-integrity contract as
`archive`.

Exits 1 on collision (`<new>` exists); 2 on a malformed tree caught by the
pre-flight walk (A1) or an `OSError` mid edge-rewrite (A4).

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

> **`[check] stale_days` does NOT affect `docs list --stale` (M19 — Q6).**
> The `.docs.toml [check] stale_days` config key is scoped to **check**
> semantics only. `docs list` keeps `--stale` as an explicit filter: bare
> `docs list` (no `--stale`) lists everything regardless of any configured
> `stale_days`, and an explicit `docs list --stale N` filters by N as always.

Exits 0.

### `docs check [DIR] [--stale N] [--json] [--exclude PATTERN]`

Validate the tree. Reports (and exits nonzero on) any of:

- Missing or empty required metadata fields (`Lifecycle`, `Role`, `Updated`).
- `Lifecycle` or `Role` not in the (built-in ∪ configured) vocab.
- `Updated:` not parseable as `YYYY-MM-DD`.
- Structural breakage: a missing H1. (A malformed line inside the metadata block ends the block early rather than raising; its effect surfaces as a missing required field, not as a separate finding.)
- Lifecycle/location mismatch (`Lifecycle: archived` outside archive subtree, or any other lifecycle inside) — rule `status-drift` (stable rule id from M3).
- `Related:` paths that don't resolve to a file under the docs root.
- (With a stale window — see **Stale-window resolution** below) `Lifecycle: active` docs with `Updated:` more than N days ago.
- (M7 — F1) A missing `Role:` line whose value is resolvable from an H1
  trailing-word signal or a section-header pattern produces a
  medium-confidence inference — `severity: warning`, rule
  `medium-confidence-inference`, exit code 1.
- (M10 — OQ-F + OQ-H) An extra metadata label that is neither on the
  built-in always-allowed set (`Lifecycle` / `Role` / `Project` /
  `Updated` / `Related` / `Archived-reason`) NOR on the
  `[vocabulary] add_fields = [...]` allowlist in `.docs.toml`
  produces `severity: warning`, rule `unknown-field`, exit code 1.
  The rule is **opt-in**: an absent or empty `add_fields` switches
  it off entirely (trees without the allowlist see no change).
  Matching is case-sensitive exact match — `add_fields = ["Owner"]`
  allows `Owner:` but not `owner:`.

Output is grouped by file; one line per finding. `--json` emits an array of records, one per finding. Schema — **stable from M3 onward**:

| Field | Type | Notes |
|---|---|---|
| `path` | string | Root-relative POSIX path of the doc. |
| `severity` | string | `error` or `warning`. |
| `rule` | string | Stable rule id: `missing-field`, `bad-vocab`, `bad-date`, `malformed`, `status-drift`, `broken-ref`, `stale`, `medium-confidence-inference` (M7), or `unknown-field` (M10). |
| `message` | string | Human-readable description of the finding. |

Exit codes:
- 0 — clean.
- 1 — warnings only (stale docs; medium-confidence inferences; unknown-field warnings).
- 2 — errors (missing required fields, invalid vocab, malformed structure, lifecycle/location drift, broken refs).

**Stale-window resolution (M19 — D2).** The stale window the `stale` rule
applies is resolved as **CLI `--stale` > `[check] stale_days` > unset**:

- An explicit CLI `--stale N` always wins — including `--stale 0`, which is
  honoured as given (flag every active doc not updated *today*), not treated
  as "unset".
- When `--stale` is absent and the docs root's `.docs.toml` carries a
  `[check] stale_days = N` (see `convention.md` › *Per-tree `[check]`
  config*), that value supplies the window. A configured `stale_days`
  therefore makes **bare `docs check`** (with no `--stale` flag) apply the
  stale rule — setting the key is the operator's explicit per-tree opt-in.
- When neither is present, behaviour is exactly today's: no stale window, so
  the `stale` rule never fires. Trees with no `[check]` section are
  byte-for-byte unchanged.

This resolution is shared by `docs check` and `docs touch --check`;
`docs list --stale` is **not** a consumer (see `docs list` below).

**Threshold provenance.** The `stale` finding's message names where the
threshold came from, so the operator knows which knob to turn. The
parenthetical extends as follows (the rule id `stale`, severity `warning`,
and exit code 1 are unchanged — only the message text):

- config-sourced (the window came from `[check] stale_days`):
  `(stale threshold N, set in .docs.toml [check] stale_days)`;
- CLI-sourced (the window came from `--stale N`):
  `(stale threshold N, via --stale)`.

(`docs touch --check` inherits this resolution and provenance: config-sourced
when no `--stale` is forwarded, CLI-sourced when `--stale N` is.) Internally,
a `stale_source` (`"config"` / `"cli"` / `None`) is threaded alongside the
resolved window — a small `resolve_stale(cli_stale, config.stale_days)`
helper, shared by both consumers, returns the `(window, source)` pair so the
message is assembled in one place.

### `docs touch <file>... [--check [--stale N]]`

Bump `Updated:` to today in one or more docs. Accepts one or more
positional file paths. INDEX regenerated **exactly once** at end of
batch, not once per file.

The batch is **atomic** (M10 — OQ-C). `touch` validates every input
path first — if any path is missing, isn't a regular file, or resolves
outside the resolved docs root, the command exits 1 + a named-bad-path
message on stderr and writes nothing. Otherwise every rewrite is
prepared in memory (any `MetadataError` aborts the batch before any
disk write), then `atomic_write` is run per file followed by a single
end-of-batch INDEX refresh. A failure during the validate-or-prepare
phase leaves every file byte-identical to its pre-call state.

**End-of-batch reindex honours `[exclude]` / `.docsignore` (M14 — A6).**
The single end-of-batch INDEX refresh walks the tree through the same
layered exclusion predicate `docs index` builds (persistent
`.docs.toml [exclude]` + a root `.docsignore`; `touch` has no
`--exclude` flag of its own). A file the operator has excluded — e.g. a
bundled plugin `README.md` with no metadata block, parked under an
`[exclude] dirs = [...]` directory — is therefore never read by the
reindex. Because the dates are stamped *before* the reindex, an
unfiltered walk that hit such a malformed excluded file would raise
*after* the stamps landed, leaving a partial, non-atomic result (dates
written, INDEX stale). Threading the predicate closes that gap: the
touched files' `Updated:` lines land, the INDEX refreshes **without**
the excluded file, and the command exits 0. (A malformed file that is
**not** excluded is still a hard error — the reindex maps it to exit 2,
unchanged.) This same exclude-predicate threading applies to every
end-of-batch reindex — `docs archive`, `docs mv`, and `docs project
rename` (M14 — A6, four-site).

`--dry-run` prints one `docs: would touch <path>` per file on stderr
(gated on `not --quiet`) and writes nothing. The success run prints
one `docs: touched <path>` per file on stderr (gated on `not
--quiet`).

**`--check [--stale N]` — touch-then-validate in one invocation (M19 — D1).**
`--check` folds the existing `docs check` machinery into `docs touch` so
the common post-edit loop (`docs touch <files>` → `docs index .` →
`docs check . --stale N`) collapses to a single command. When `--check`
is set, *after* `touch`'s end-of-batch INDEX refresh runs, `touch`
invokes the same **tree-wide** `check_tree` over the resolved docs root
that bare `docs check` runs — it *replaces* the `docs check .` step of
the loop, not a touched-files-only subset.

- **Combined exit code = `max(touch, check)` with a touch-fail
  short-circuit (M19 — Q1).** Touch runs first. If touch itself fails
  (exit 1 — missing/bad path; or exit 2 — outside-root refusal /
  INDEX-refresh failure) the check does **not** run and touch's code is
  returned (a failed touch left nothing meaningful to validate). If touch
  succeeds (0), the check runs and its 0/1/2 (clean / warnings-only /
  errors) becomes the command's exit code.
- **`--stale N` is forwarded to the check (M19 — Q3 / D2).** With
  `--check`, `--stale N` supplies the check's stale window; when `--stale`
  is absent, the `[check] stale_days` config default applies (see
  `docs check` below for the resolution rule). `--stale` **without**
  `--check` is a hard error — exit 2 with
  `docs: touch: --stale requires --check` on stderr; the file is left
  byte-unchanged and no reindex runs.
- **`--dry-run --check` previews the touch and checks the un-mutated tree
  (M19 — Q4).** Under `--dry-run` nothing is written and no INDEX refresh
  runs, so the check walks the **on-disk (un-mutated)** tree directly. A
  doc the dry-run *would* refresh may therefore still read as stale, since
  dry-run did not bump its `Updated:`.
- **`--quiet` gates only `touch`'s own stderr lines (M19 — Q-E).** The
  `would touch` / `touched` success/preview lines are suppressed under
  `--quiet`; the check's findings, which print on **stdout**, are **never**
  suppressed by `--quiet`.
- **The check honours the same `[exclude]` / `.docsignore` predicate as
  `touch`'s reindex (M19 — Q-F).** The tree-wide check applies the
  persistent layered exclusion predicate (`.docs.toml [exclude]` + a root
  `.docsignore`) — the same one `touch`'s end-of-batch reindex and bare
  `docs check` use. `touch` has no `--exclude` flag of its own. A malformed
  *excluded* file therefore never fails the check (just as it never fails
  the reindex).

Multi-root invocation (`docs touch a.md b.md` where `a.md` and `b.md`
resolve to different docs roots) is **undefined behaviour and out of
M10 scope** — the validate-all-first pass refuses with exit 1 + an
"outside the resolved docs root" message.

**Outside-docs-root refusal (M12 — OQ-C).** If `--root` is not given
and no `.docs.toml` exists in the cwd's ancestor chain, `docs touch`
refuses with exit 2 + stderr message
`docs: touch: <path> is not under a docs root with .docs.toml; refusing`.
The file is left unchanged and no INDEX refresh runs (avoiding the M11
cascade-crash where a downstream walk failed on the first non-managed
sibling). An explicit `--root <dir>` bypasses the refusal **only when**
`<dir>/.docs.toml` exists; if `--root` is set but its `.docs.toml` is
missing, `touch` refuses with
`docs: touch: --root <root> does not contain .docs.toml; refusing`
(exit 2) (M12 — OQ-11).

### `docs project rename <new-name>`

Rename the docs root's project (M12). Rewrites `.docs.toml`'s
`[project] name = "<old>"` to `name = "<new>"` **and** every
conformant `Project: <old>` line in every active doc, atomically, with
a single end-of-batch INDEX refresh.

```
docs project rename <new-name> [--dry-run] [--quiet] [--root DIR]
```

`<new-name>` is required. A missing positional triggers argparse's
default exit 2.

**Resolution.** Operates on the docs root resolved from cwd via the
standard upward `.docs.toml` walk, unless `--root` overrides it
(M12 — OQ-1). If the resolved root has no `.docs.toml`, exits 2 with
stderr `docs: project rename: <cwd> is not under a docs root with .docs.toml; refusing`.

**Auto-normalisation (M12 — OQ-A).** The operator-supplied `<new-name>`
is run through M7's `normalise_project_name()` (the same machinery
`docs migrate` already uses). When the normalised form differs from
the input, stderr carries one line (gated on `not --quiet`):

```
docs: project rename: normalised "<input>" to "<normalised>"
```

before the rewrite proceeds with the normalised value. The current
`.docs.toml` `[project] name` value is read **as written** for the
no-op comparison — no double-normalisation (M12 — OQ-3).

**Empty-name rejection (M12 — OQ-9).** If post-normalisation
`<new-name>` is empty or whitespace-only, refuses with exit 2 + stderr
`docs: project rename: <input> normalises to empty string; project name must be non-empty`.

**What gets rewritten** (success path):

- `.docs.toml`'s `[project] name = "<old>"` line → `name = "<new>"`.
- Every conformant `Project: <old>` line in every **active-tree** doc
  → `Project: <new>`.
- Docs that have no explicit `Project:` line implicitly resolve to the
  docs-root project; on rename, a `Project: <new>` line is inserted
  into those docs (consistent with M2's `set_metadata_field` behaviour
  for missing-field cases).
- `INDEX.md` regenerated once at end of batch.

**Multi-project tolerance (M12 — OQ-B).** A tree whose active docs
carry mixed `Project:` values (the M7-tolerated multi-project shape)
is walked completely: docs whose `Project:` matches `<old>` are
rewritten; docs with a non-matching `Project:` are reported in the
success footer but never mutated.

**Archive-subtree skip.** Docs under the configured `archive_dir` are
read-only by convention (M3); `project rename` skips them and reports
the count in the footer.

**Atomic semantics.** Validate-all-first: parse every active doc,
build the rewrite tuple + the sidecar plan; if any step in
validate-and-prepare raises, exits 1 (or 2 for a malformed
`.docs.toml`) with the offending path named on stderr and no on-disk
mutation. After validation passes, every rewrite is committed via
`atomic_write`, then `.docs.toml` is rewritten, then `INDEX.md` is
refreshed exactly once. That end-of-batch refresh honours `[exclude]` /
`.docsignore` (M14 — A6) — a malformed *excluded* file never fails the
reindex (same exclude-predicate threading as `docs touch`).

**`--dry-run`.** Prints one `docs: would rewrite Project: in <rel-path>`
line per matching doc, plus
`docs: would rewrite [project] name in .docs.toml: "<old>" -> "<new>"`,
plus the footer. Exits 0; writes nothing.

**No-op.** When the normalised `<new-name>` equals the sidecar's
current `[project] name`, the verb is a no-op regardless of whether
the active tree carries non-matching `Project:` docs (the rename has
nothing to rewrite — non-matching docs hold a different project name
and remain untouched). Prints (gated on `not --quiet`):

```
docs: project rename: <new> already current — no rewrites needed
```

to stderr; exits 0; no disk mutation; no INDEX refresh.

**Success output (M12 — OQ-2).** A single human-readable stderr line
(gated on `not --quiet`):

```
docs: project rename: <old> -> <new> (rewrote .docs.toml + <N> doc(s); <M> archived skipped; <K> non-matching project(s) untouched: <list>)
```

When `K == 0` **and** `M == 0`, the empty clauses are dropped to:

```
docs: project rename: <old> -> <new> (rewrote .docs.toml + <N> doc(s))
```

No `--json` mode in M12 (M12 — OQ-7).

**What does NOT change.**

- Prose markdown text mentioning the old name. Only the metadata
  `Project:` field is rewritten — never `Related:` edges (which carry
  no project signal) and never body prose. (Consistent with M2's
  `docs mv` "Related: only, not prose" stance.)
- Files outside the docs root.
- Archive-subtree docs.

**Exit codes.** 0 success / no-op / dry-run; 1 recoverable error
(e.g. a doc with no editable metadata block); 2 hard error (malformed
`.docs.toml`, no `.docs.toml` ancestor, empty post-normalised
`<new-name>`).

### `docs project set <doc>... <new-project>`

Reassign one or more docs' `Project:` field to `<new-project>` (M15 — B2,
proposal §5E). The **single-doc counterpart** to `project rename`: where
`rename` rewrites the *whole root* (`.docs.toml` `[project] name` + every
matching `Project:` line), `set` rewrites the `Project:` line of *just the
named docs* and regroups them in the INDEX. It does **not** touch
`.docs.toml`, non-named docs, or `Related:` edges.

```
docs project set <doc>... <new-project> [--new-project] [--dry-run] [--quiet] [--root DIR]
```

**Grammar.** A single `nargs="+"` positional run is split as
`*docs, <new-project>` — the **last** token is the new project name, every
earlier token is a doc path. At least **two** tokens are required: a
single-token invocation (`docs project set foo`) is ambiguous (is `foo` a doc
or a project?) and is refused with exit 2 + stderr
`docs: project set: need at least one <doc> and a <new-project>` (writes
nothing).

**Resolution.** Operates on the docs root resolved from cwd via the standard
upward `.docs.toml` walk, unless `--root` overrides it. If the resolved root
has no `.docs.toml`, exits 2 with stderr
`docs: project set: <cwd> is not under a docs root with .docs.toml; refusing`
(mirrors `project rename` / `touch` strict-root resolution — a write into an
unmanaged tree is the footgun this closes). An explicit `--root <dir>` bypasses
the up-walk **only when** `<dir>/.docs.toml` exists; otherwise refuses with
`docs: project set: --root <root> does not contain .docs.toml; refusing`
(exit 2).

**Auto-normalisation.** `<new-project>` is run through M7's
`normalise_project_name()` (same as `rename` / `migrate`). When the normalised
form differs from the input, stderr carries one line (gated on `not --quiet`):

```
docs: project set: normalised "<input>" to "<normalised>"
```

before the rewrite proceeds with the normalised value. If post-normalisation
`<new-project>` is empty or whitespace-only, refuses with exit 2 + stderr
`docs: project set: <input> normalises to empty string; project name must be non-empty`.

**Typo guard (the §5E design decision).** The way an agent silently fragments
the INDEX is a typo (`idea` vs `ideas` → two project groups). Rather than
prompt (the non-interactive invariant), `set` **refuses a `<new-project>` value
that is new to the tree** unless `--new-project` is passed. The set of known
projects is the resolved `Project:` of every **active** doc (a doc's explicit
`Project:`, or the docs-root project for a doc with none) **plus** the
`.docs.toml` `[project] name`. When the normalised value is not in that set and
`--new-project` is absent, refuses with exit 2 + stderr (the did-you-mean shape
from agent-native-invocation.md §5E):

```
docs: project set: '<value>' is not a project in this tree; refusing
  → did you mean '<closest>'? to create a new project group, pass --new-project
```

`<closest>` is the nearest known project via `difflib.get_close_matches`. The
**`→ … to create a new project group, pass --new-project` recovery hint always
prints** — only the `did you mean '<closest>'?` prefix is conditional: when no
known project is close, the prefix is dropped and the `→` line reads
`→ to create a new project group, pass --new-project`. An **existing** project
value needs no flag. Passing `--new-project` acknowledges the deliberate act of
creating a new project group and succeeds for any (non-empty, normalised)
value.

**What gets rewritten** (success path):

- Every named doc's `Project: <old>` line → `Project: <new-project>`. A doc
  with no explicit `Project:` line implicitly resolves to the docs-root
  project; on `set`, a `Project: <new-project>` line is **inserted** (M2's
  `set_metadata_field` missing-field behaviour, consistent with
  `project rename`).
- `INDEX.md` regenerated **once** at end of batch.

**What does NOT change.**

- `.docs.toml` — `set` never rewrites the `[project] name` (that is `rename`'s
  whole-root job).
- `Related:` edges — `set` changes no path, so unlike `rename` / `archive` /
  `mv` it performs **no** referring-edge rewrite. Strictly simpler than those.
- Body prose and docs not named on the command line.
- Files outside the docs root.

**Atomic semantics — validate-all-first.** Every named doc is resolved and
parsed *before* any write: if any named path is missing or malformed, or any
named doc resolves outside the docs root, the batch aborts **before any disk
mutation** and the offending path is named on stderr; every doc is left
byte-identical and no INDEX refresh runs. A missing/malformed named doc, or a
named doc that resolves **outside the resolved docs root**, exits 1 — matching
`docs touch`'s precedent that a named target outside an *already-resolved* root
is an explicit-path error, not a no-root refusal (the cross-verb exit-code
convention; see the Exit codes summary). An archived / typo / empty-name /
single-token failure exits 2. After validation passes, every rewrite is
committed via `atomic_write`, then `INDEX.md` is refreshed exactly once
(honouring `[exclude]` / `.docsignore`, M14 — A6).

**Archived target → refuse the whole batch (exit 2).** Archive-subtree docs are
read-only by convention (M3). Unlike `project rename` (which *skips + reports*
archived docs found incidentally during its tree walk), `set` operates on docs
the operator **named explicitly** — naming an archived doc is an error, not an
incidental skip. If any named doc resolves under the configured `archive_dir`,
the **whole batch** is refused with exit 2 + stderr naming the path:
`docs: project set: <path> is under the archive subtree (read-only); refusing`.
Nothing is written.

**`--dry-run`.** Prints one `docs: would rewrite Project: in <rel-path>` line
per named doc (gated on `not --quiet`); exits 0; writes nothing; no INDEX
refresh.

**No-op.** When **every** named doc already carries the normalised
`<new-project>` (the resolved value already equals the target), the verb is a
no-op: prints (gated on `not --quiet`)

```
docs: project set: <new-project> already current — no rewrites needed
```

to stderr; exits 0; no disk mutation; **no INDEX refresh**.

**Success output.** A single human-readable stderr line (gated on
`not --quiet`):

```
docs: project set: set <new-project> on <N> doc(s)
```

**Exit codes.** 0 success / no-op / dry-run; 1 a named doc is missing or
malformed, or a named doc resolves outside the docs root (validate-all-first
abort, byte-identical tree — matching `docs touch`'s "named target outside the
resolved root" precedent); 2 hard error (no `.docs.toml` ancestor or `--root`
without `.docs.toml`; a named archived doc; empty post-normalised
`<new-project>`; an unknown `<new-project>` without `--new-project`; a
single-token grammar error).

### `docs stamp <file>... [--role ROLE] [--project NAME] [--title "…"] [--dry-run] [--quiet] [--root DIR]`

Stamp a convention-correct metadata block onto one or more files an agent has
already written (M15 — B3). The **write-then-stamp** counterpart to
`docs new --body-from`: where `new` owns the frontmatter and appends a body,
`stamp` takes a file that *already has a body* (authored with ordinary tools)
and inserts the metadata block on top, preserving the body verbatim. It is a
**standalone top-level verb** with mutating-verb polarity (writes by default;
`--dry-run` to opt out) — it reuses the `docs migrate` metadata-block insertion
internally but is **not** routed through or aliased to `migrate` (a precise
single-file stamp, not a foreign-tree import).

```
docs stamp <file>... [--role ROLE] [--project NAME] [--title "…"] [--dry-run] [--quiet] [--root DIR]
```

**What it writes.** For each file, `stamp` inserts a metadata block via the
same `insert_metadata_block` machinery `migrate --apply` uses — placed
immediately under the H1, body preserved verbatim, with foreign metadata-shaped
lines parked under a `## Migrated metadata` body section (each label
`Migrated-`-prefixed; see `migrate`). The four required fields are filled:

- **Lifecycle:** always `draft` (a freshly-stamped doc is a draft).
- **Role:** `--role ROLE` if given, else the default `notes`. There is **no**
  H1-role inference — a file whose H1 reads like a plan still gets `notes`
  unless `--role plan` is passed. (`--role` must be in the built-in or
  configured Role vocabulary; an invalid role exits 2.)
- **Project:** `--project NAME` if given, else the docs root's configured
  `[project] name`.
- **Updated:** today (in the configured `date_format`).

**Title.** Inferred from the file's `# H1` when present. When the file has no
H1, one is synthesised as `# <title>` where `<title>` is `--title` if given,
else the filename's last path segment, title-cased (`-`/`_` as word
separators) — the same `_slug_to_title` derivation `docs new` uses. `--title`
overrides the inferred/synthesised H1.

**Idempotent re-stamp.** Re-stamping a file that already carries a valid
metadata block (all four required fields present and valid — detected by a
clean `parse()` of the file) is a **no-op bar an `Updated:` refresh**: only the
`Updated:` line is bumped to today (via `set_metadata_field`); `Lifecycle`,
`Role`, `Project`, the title, and the body are left byte-identical. Reports
(gated on `not --quiet`) that the file was already stamped:

```
docs: stamp: <path> already stamped — refreshed Updated:
```

**Strict-root resolution.** Mirrors `docs new` / `docs touch`: resolved from
cwd via the upward `.docs.toml` walk, or `--root` (which must contain
`.docs.toml`). No `.docs.toml` ancestor (and no valid `--root`) refuses with
exit 2 + stderr
`docs: stamp: <path> is not under a docs root with .docs.toml; refusing`
(or the `--root … does not contain .docs.toml; refusing` variant). The
`Project:` default reads the resolved root's `[project] name`.

**Atomic multi-file batch.** Mirrors `docs touch`: every named path is checked
to exist and resolve under the docs root *before* any write; a missing file (or
one outside the root) aborts the batch with exit 1 + a named-bad-path message,
**before any write**. Each file's stamped text is then prepared in memory and
committed via `atomic_write`, followed by a **single** end-of-batch INDEX
refresh (honouring `[exclude]` / `.docsignore`).

**`--dry-run`.** Prints one `docs: would stamp <path>` line per file (gated on
`not --quiet`); exits 0; writes nothing; no INDEX refresh.

**Success output.** One `docs: stamped <path>` line per newly-stamped file
(gated on `not --quiet`); already-stamped files report the refresh line above.

**Exit codes.** 0 success / dry-run; 1 a named file is missing or resolves
outside the docs root (validate-all-first abort, byte-identical tree); 2 hard
error (invalid `--role`; no `.docs.toml` ancestor or `--root` without
`.docs.toml`).

### `docs install-skill [--dest DIR] [--copy|--symlink] [--force] [--quiet]`

Materialise the bundled `docs` agent skill onto the host.

Synopsis. The `docs-cli` wheel carries a `docs_cli/skill/` directory (the
`SKILL.md` file plus its bundled spec references). `install-skill` copies
(or symlinks) that directory to a host-side location an agent can read.

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
  atomically and performs any archive-normalising moves. After the file loop
  it also writes (or extends) the root `.docs.toml` sidecar (M10 — OQ-A): an
  absent sidecar gets a minimal `[project] name = "<resolved>"` + `[archive]
  date_format = "%Y-%m-%d"` block (no redundant `dir = "archive"`); a sidecar
  that already carries a `[migrate]` or `[exclude]` block but no `[project]`
  gets `[project]` appended at the bottom under a
  `# Added by docs migrate --apply` provenance comment header; a sidecar that
  already carries `[project]` is left untouched. After every archive-move the
  now-empty source parent directory is opportunistically removed (M10 — OQ-G;
  swallows `OSError(ENOTEMPTY)` so a non-migrating sibling survives). The
  result is a tree `docs check` accepts with no further operator action
  required.
- With `--apply --quiet` (M10 — OQ-B), the per-file plan block on stdout is
  suppressed in addition to the trailing `docs: migrated <N> file(s) …`
  success line on stderr. Empty stdout + empty stderr on a clean run. The
  dry-run plan, `--summary` output, and `--json` array are **requested
  outputs** and are NEVER suppressed — `--quiet` is scoped to chatter only.
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
a tree directly. M8 (F3) introduces a single layered exclusion
surface they all consult. M14 (A6) threads the same surface into
the **end-of-batch INDEX reindex** of the four mutating verbs
(`touch` / `archive` / `mv` / `project rename`) — those consult
only the two **persistent** sources (`[exclude]` + `.docsignore`),
having no `--exclude` flag of their own. The four sources combine
**additively** — no source replaces another:

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

M12 / M14 / M15-specific exit-code shape:

| Verb | 0 | 1 | 2 |
|---|---|---|---|
| `project rename` | success / no-op / dry-run | doc lacks editable metadata block | malformed `.docs.toml`; no `.docs.toml` ancestor; empty post-normalised `<new-name>` |
| `project set` (M15 — B2) | success / no-op / dry-run | a named doc is missing or malformed, or a named doc resolves outside the docs root (validate-all-first abort) | no `.docs.toml` ancestor or `--root` without `.docs.toml`; a named doc under the archive subtree; empty post-normalised `<new-project>`; unknown `<new-project>` without `--new-project`; single-token grammar error |
| `stamp` (M15 — B3) | success / dry-run | a named file is missing or outside the docs root (validate-all-first abort) | invalid `--role`; no `.docs.toml` ancestor or `--root` without `.docs.toml` |
| `touch` (outside-root refusal) | — | — | no `.docs.toml` ancestor (cwd-resolved) or `--root` without `.docs.toml` |
| `new` (strict-root refusal, M14 — A2) | success / dry-run | existing file | no `.docs.toml` ancestor (cwd-resolved) or `--root` without `.docs.toml`; invalid role / slug (incl. empty final segment, M14 — A3) |
| `archive` (referring-edge) | success | referring doc has malformed metadata (move aborts) | archive-dir creation failure; `OSError` mid edge-rewrite (M14 — A4); invalid cascade-flag combination (M14 — B1) |
| `archive --cascade-dry-run` | preview only; writes nothing (exit 0) | — | — |
| `mv` (M14 — A1 / A4) | success / dry-run | collision (`<new>` exists) | malformed tree caught by the validate-all-first pre-flight (A1); `OSError` mid edge-rewrite after the move (A4); both paths outside the docs root |

**Cross-verb exit-code convention (no-root vs outside-root).** Two distinct
"out of the tree" conditions map to *different* codes for the explicit-path
verbs (`touch`, `stamp`, `project set`):

- **No docs root** — the cwd has no `.docs.toml` ancestor, or `--root` names a
  directory without `.docs.toml`. This is a **hard refusal → exit 2** (the
  `_resolve_*_root` strict-root refusal; nothing can be resolved).
- **A named target resolves *outside* an already-resolved root** — the root was
  found, but an explicit doc/file argument lies outside it. This is a
  **recoverable explicit-path error → exit 1** (`docs touch`'s precedent: the
  argument is wrong, not the tree).

CI integration: `docs check` returning 2 should fail the build.
