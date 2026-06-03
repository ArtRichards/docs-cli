# docs — Convention Spec

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-06-03

Related:
- pairs-with: cli.md

## Scope

This spec defines the on-disk convention that `docs` reads and writes. It is the portable, tool-independent part: any directory following this convention is navigable with `grep` and `ls` alone. The `docs` CLI is convenience over this convention, not a prerequisite for it.

## Document shape

Every `.md` file managed by `docs` has this structure:

```markdown
# <Title>

<metadata-block>

## <first content section>
...
```

### H1 title

The first non-empty line of the file MUST be a single `#` H1. This is the doc's display title in indexes and `docs list` output.

### Metadata block

Lines immediately after the H1 (separated by a blank line) form the **metadata block**.

Within the block, two line shapes are allowed:

```
Label: inline value
Label:
- value
- value
```

The first form is for single values. The second form is for multi-valued labels (used by `Related:` and any other label that takes a list).

The metadata block may be split into groups separated by blank lines, provided each group after the first is a bare `Label:` followed by `- value` bullets (a multi-value group). This permits the common style of grouping inline metadata above and `Related:` (or any other list-valued label) below, with a visual blank line between them:

```
Lifecycle: active
Role: spec
Updated: 2026-05-20

Related:
- pairs-with: convention.md
- implements: charter.md
```

The block terminates at the first blank line whose next non-empty line is *not* a bare-label multi-value group. An inline `Label: value` line after a blank line is body content, not metadata — this preserves the rule that anything looking like an isolated `Label: value` outside the block is opaque to the parser.

### Required fields

| Field | Type | Meaning |
|---|---|---|
| `Lifecycle` | controlled vocab | doc's lifecycle state |
| `Role` | controlled vocab | what kind of doc this is |
| `Updated` | `YYYY-MM-DD` | last meaningful update |

> **Lifecycle (M7 — F0) — breaking change since 1.1.**
> Before 1.2 the lifecycle field was named `Status:`. M7 renamed
> the controlled-vocab key to `Lifecycle:` because the 2026-05-24
> multi-tree trial found that almost every real-world foreign doc
> uses `Status:` as a free-form progress line ("Implemented;
> retained as design record", "Draft normative companion spec",
> etc.). A free-form `Status:` line in a doc is now treated as an
> ordinary extra field: preserved verbatim by `docs migrate` (into
> the `## Migrated metadata` body section as
> `Migrated-Status:`), surfaced through `docs list --json` under
> `extra_fields`, and ignored by `docs check`'s vocabulary
> validator. See `dual-status-adr.md` for the operator decision
> trail.

### Optional fields

| Field | Type | Meaning |
|---|---|---|
| `Project` | kebab-case slug | project this doc belongs to; defaults to `project.name` in `.docs.toml` if absent. The CLI surface `docs project rename` rewrites this slug in lockstep across the sidecar and every doc that names it (M12). |
| `Related` | list of `<verb>: <path>` | typed cross-references to other docs |
| `Owner` | free-form | the human or team accountable for this doc |
| `Tags` | comma-separated | free-form tags for filtering |
| `Status` | free-form | a human-readable progress sentence (M7 — preserved, not vocab-checked) |

Any additional `Label:` fields are harvested and exposed under `docs list --json` but not interpreted by the tool.

## Vocabularies

### Lifecycle (built-in)

| Lifecycle | When |
|---|---|
| `draft` | Being written, not ready for use. |
| `active` | Current, in use, source of truth. |
| `blocked` | Paused, waiting on something external. Pair with `Related: blocked-by: …`. |
| `done` | Complete; intentionally kept in the active tree (evergreen reference). |
| `archived` | Complete and moved to the archive subtree. |
| `superseded` | Replaced by another doc. Pair with `Related: superseded-by: …`. |

### Role (built-in)

| Role | What |
|---|---|
| `charter` | What we're building and why. |
| `plan` | How we'll get there (sequencing, milestones). |
| `spec` | Detailed design or contract. |
| `milestone` | A specific milestone definition. |
| `log` | A chronological record where entries accumulate over time — implementation log tied to a milestone, decision log accumulating reviewer choices, or operational log of recurring work. The distinguishing feature is that the doc grows over time rather than being rewritten. |
| `status` | Living status document. |
| `decision` | ADR-style: one decision, alternatives, rationale. |
| `guide` | Instructional / how-to. |
| `runbook` | Operational procedure. |
| `reference` | Evergreen technical reference. |
| `postmortem` | Incident retrospective. |
| `idea` | Pre-decision exploration. |
| `implementation` | A focused implementation note tied to a plan or milestone (M7). |
| `sketch` | An exploratory sketch, pre-formalisation (M7). |
| `outline` | A skeletal pre-write of a plan or spec (M7). |
| `memo` | A short prose note; less structured than `notes` (M7). |
| `brief` | A condensed summary of a larger surface (M7). |
| `template` | A reusable doc template (M7). |
| `example` | A worked example used as reference (M7). |
| `notes` | Catch-all. |

> **Role vocab additions (M7 — F10 / OQ-A).** M7 promotes 7
> previously-extension-only roles to the core vocab — Trial 2
> (2026-05-24) found these are common enough in real-world docs
> that the built-in set should cover them.

### Extending vocabularies

`.docs.toml` may **add** lifecycles, roles, and extra-metadata-label
allowlist entries via `[vocabulary]` — never remove or rename built-ins.
Additions are local to that docs root. Cross-project queries collapse
to the built-in set; per-project queries see the union.

```toml
[vocabulary]
add_lifecycles = ["shipped"]            # M7: renamed from `add_statuses` (no alias)
add_roles      = ["adr", "rfc"]
add_fields     = ["Owner", "Tags"]      # M10: opt-in extra-field allowlist
```

`add_fields` (M10) widens the `docs check` `unknown-field` rule's
allowlist. Matching is **case-sensitive exact match** — `add_fields =
["Owner"]` allows `Owner:` but not `owner:` (mirroring how
`add_lifecycles` and `add_roles` already work; the on-disk convention
is `Capital:`, so `owner:` is malformed and rejected by the parser
upstream). The rule is opt-in: an absent or empty `add_fields`
switches the `unknown-field` warning OFF entirely. The built-in
always-allowed metadata labels (`Lifecycle`, `Role`, `Project`,
`Updated`, `Related`, `Archived-reason`) are never affected by
`add_fields` — they are always permitted.

Scope: `add_fields` widens the `unknown-field` check's allowlist
only; it does **not** change `docs list --json` or INDEX rendering
of extra fields. Those continue to surface every extra field
verbatim (`extra_fields` in JSON; opaque to the human INDEX).

### Inference and confidence (M7 — F1 / F10 / F12 / OQ-D)

`docs migrate` infers each foreign doc's `Role:` from filename
suffixes, post-strip variants, the H1 title, the file's section
shape, and the modal sibling-set. Inferences carry a confidence:

- **high** — direct filename-suffix match (`my-feature-spec.md`,
  `my-feature_Plan.md`, `foo-decision.md`) or an in-file `Role:`
  metadata line that already names a built-in role.
- **medium** — a derived signal: stripping `_v\d+` / `_Draft` /
  `_Ready` and re-matching; the `_M\d+` milestone-number pattern;
  an H1 ending in a role word (`# Foo Plan`); a section-header
  pattern (e.g. `## Goal` + `## Scope` + `## Requirements`
  reads as a plan); a sibling-set modal default at ≥ 60% over
  ≥ 5 same-subdir files.
- **low** — every fall-through that didn't match a real signal;
  the role lands at `notes` and `confidence: low` is paired with
  one or more ambiguity notes.

`docs check` treats a medium-confidence inference as a warning
(exit 1), not an error (exit 2). `docs migrate --json` records
the level under `confidence` (string, one of
`high|medium|low`).

### Per-tree `[migrate]` config (M7 — F1 / F5 / F11)

A docs root's `.docs.toml` may also carry a `[migrate]` section
to teach `docs migrate` per-tree overrides. A `.docs.toml`
containing ONLY a `[migrate]` section (no `[project]`,
`[archive]`, or `[vocabulary]`) is treated as a foreign-tree
migration sidecar — `docs migrate` reads it without refusing:

```toml
[migrate]
project_name   = "foo-tools"             # F11: skip normalisation, use verbatim
role_suffixes  = { spec_v2 = "spec" }    # F1: per-tree custom suffix mapping
```

- `project_name` — pin the project name for every plan record
  (the same effect as `--config-project NAME`, persisted in the
  tree's config). Bypasses F11 lowercase-kebab normalisation
  entirely.
- `role_suffixes` — extends the built-in filename-suffix → role
  map with per-tree entries.

## Relationship verbs

`Related:` entries use the form `<verb>: <path>`. Verbs are free-form, but a small set is conventional:

- `pairs-with` — bidirectional sibling (spec ↔ status, milestone ↔ log).
- `child-of` / `parent-of` — hierarchical.
- `implements` — this doc realizes that spec/charter.
- `spec-of` — this doc specifies that thing.
- `supersedes` / `superseded-by` — replacement.
- `blocked-by` — pause causation.
- `decision` — points at a decision doc that justifies this one.
- `references` — weakest form, "see also."

`docs check` does not validate verbs (free-form), but it does validate that every `Related:` path resolves to a file under the docs root. The target file does **not** need to be a `.md` doc — it may be any file (YAML data, HTML report, spreadsheet, generated artifact). The tool checks existence, not file type. This lets specs cross-reference canonical data files, reviewer worksheets, or other artifacts that live in the same tree without forcing them through `docs`'s Markdown convention.

## Archive subtree

Completed work moves to an archive subtree. Default subdir name: `archive/`. Convention: `archive/YYYY-MM-DD/` per archive event. Configurable via `[archive] dir` in `.docs.toml`.

Lifecycle/location consistency rules:

- A doc at the top level (active tree) MUST have `Lifecycle:` in `{draft, active, blocked, done, superseded}`.
- A doc under the archive subtree MUST have `Lifecycle: archived`.
- `docs check` reports any mismatch with nonzero exit (rule `status-drift`).

`done` vs `archived`: `done` stays in the active tree (evergreen reference); `archived` is moved to the archive subtree. Use `done` when the doc is finished but still referenced day-to-day.

**Archive-subtree edge integrity (M18).** Archive-subtree `Related:` edges are maintained across moves. When a doc moves into the archive, both its OWN intra-archive edges (bullets pointing at another doc moving in the same operation) and any already-archived referrers' edges to it are repointed to the new `archive/YYYY-MM-DD/` paths, so they keep resolving. The M3 "archive is read-only" stance is preserved for everything else — only these move-driven edge rewrites touch archived docs; prose, other metadata, and edges to docs that did not move are left byte-identical.

## Subdirectories

A docs root is not required to be flat. Beyond the machine-managed archive subtree, authors may organize docs into free-form subdirectories — grouping a body of work, a set of brainstorms, or a sub-project under its own folder. The tool is directory-agnostic:

- `docs index` walks the whole tree recursively and lists every doc by its root-relative path. A subdirectory imposes no constraint on a doc's metadata.
- The only directory the tool treats specially is the configured `archive_dir` — docs under it form the archive subtree (see above). Every other subdirectory is opaque to `docs`.
- The status/location consistency rule applies *only* to the archive subtree. A doc in any other subdirectory may carry any active-tree status.

Whether to keep a tree flat or nest it is the author's call. The metadata block and the generated `INDEX.md` — not the directory layout — are the primary navigation surface; subdirectories are a convenience for humans browsing with `ls` or an editor file-tree. `docs new` can create a doc directly into a subdirectory (`docs new spec sub/feature`); `docs mv` can relocate one between directories.

## Exclusion

M8 introduces a single layered exclusion surface every walker
consults — `docs migrate`, `docs index`, `docs check`,
`docs list`. M14 (A6) extends it to the **end-of-batch INDEX
reindex** the four mutating verbs run — `docs touch`,
`docs archive`, `docs mv`, and `docs project rename` — so a
malformed *excluded* file (e.g. a bundled plugin `README.md`
under an `[exclude]` dir) cannot fail the post-mutation reindex
after the verb has already stamped/moved on disk. The four
sources combine **additively** (no source replaces another);
see [`cli.md`'s "Common: exclusion"
section](cli.md#common-exclusion) for the per-verb shape. The
mutating verbs consult only the **persistent** sources
(`[exclude]` + `.docsignore`) — they expose no `--exclude` flag
of their own.

- **`[exclude]` table in `.docs.toml`** (persistent, per-tree).
  Three keys — `dirs = [...]` for directory-name matches at
  any depth, `globs = [...]` for gitignore-flavoured glob
  patterns, `exts = [...]` for extension matches. The
  bundled adoption skill's `references/docs-toml-template.toml`
  carries a commented starter.
- **`.docsignore` at the tree root** (persistent, per-tree).
  Single file only — nested `.docsignore` files are NOT
  consulted (OQ-B). One pattern per line. Syntax subset:
  - `# comment` and blank lines are no-ops.
  - Trailing `/` → directory match.
  - Leading `/` → root-anchored (no nested match).
  - `**` → any number of segments; `*` → any non-slash chunk;
    `?` → one non-slash character.
  - Leading `!` → re-include (last match wins, matching
    gitignore).
  - Bare pattern (no `/`) → matches any path segment at any
    depth.
- **`--exclude PATTERN`** on the CLI (ephemeral, repeatable;
  same glob syntax as `.docsignore`). Layered on top of the
  two persistent sources.
- **`--exclude-ext EXTS`** on `migrate` (one-off, csv).
  Extension matches; also suppresses the matching binaries
  from the non-Markdown sibling footer.

For the procedural deep-dive — when to use `[exclude]` vs
`.docsignore` vs CLI overrides, and the dry-run → triage →
iterate → apply loop — see the bundled
[adoption playbook](https://github.com/ArtRichards/docs-cli/blob/main/src/docs_cli/skill/references/adoption-playbook.md)
(also materialised on a host via `docs install-skill`).

## INDEX file

The `INDEX.md` file at the root of the docs tree is a **generated view, not a managed doc**. It does not require a metadata block, and `docs` excludes it from traversal by filename. (Specifically: any file at the docs root literally named `INDEX.md` is read as the existing index for marker-block preservation and skipped during walking; it never appears as an entry in itself.)

The docs root contains an `INDEX.md` with this structure:

```markdown
# <Root title>

<optional hand-edited preamble>

<!-- docs:generated start -->
... derived content ...
<!-- docs:generated end -->

<optional hand-edited trailer>
```

`docs` only rewrites content between the markers. Everything outside is preserved verbatim. The derived section groups by project and role, lists every `.md` file in the tree with its title and a one-line excerpt, and separates the active tree from the archive subtree.

## Non-Markdown files in the tree

A docs root frequently contains files that aren't Markdown — HTML review packets, spreadsheet workbooks, YAML data files, generated validation artifacts, exported PDFs, screenshots, and so on. These are not docs in the sense `docs` cares about; they are **silently ignored** by `docs index`, `docs check`, and every other verb that walks the tree.

- They do not need a metadata block.
- They do not appear as entries in `INDEX.md`.
- Their absence of metadata is not an error.
- They may be referenced from `.md` docs via `Related:` (see "Relationship verbs") or via prose links in the body. `Related:` will check that the referenced file exists, regardless of its extension.

This keeps `docs` focused on the Markdown navigation layer while letting authors keep canonical data, presentation artifacts, and generated outputs co-located with the specs that describe them. The Markdown layer is the navigable map; everything else lives alongside it.

If you want a non-Markdown artifact to appear *prominently* in `INDEX.md` (e.g., a key reviewer packet that needs to be the first thing readers see), describe it in a short companion `.md` doc that points at it via `Related:` — the companion doc carries the metadata and appears in the index; the artifact stays as the canonical file. A future v1.1 may add a first-class `Attachments:` field; for v1 the companion-doc pattern is the recommendation.

**Migration-time surfacing (M8 — F7).** `docs migrate <dir>` now
surfaces non-Markdown root-level siblings in the dry-run plan
footer as `<N> non-Markdown siblings at root not considered:
<names>` so an adopting agent sees the binaries that prose
references but the walker (markdown-only) skips. Use
`--exclude-ext EXTS` (csv) or the `[exclude] exts = [...]`
config to drop the noise once the operator's reviewed the list.

## File naming

Names are free-form. The metadata block carries the load; the filename is for humans. Kebab-case is recommended (`vocab-adr.md`, not `Vocab_ADR.md`), but not enforced.

## What `docs` does not promise

- No automatic `Updated:` bumping on every write. Use `docs touch` or hand-edit.
- No link-graph traversal. `Related:` is metadata, not a query target in v1.
- No content validation beyond metadata. The body of a doc is opaque to the tool.
