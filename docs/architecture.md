# docs — Architecture

Lifecycle: active
Role: reference
Project: docs
Updated: 2026-08-16

Related:
- implements: charter.md
- pairs-with: convention.md
- pairs-with: cli.md
- pairs-with: test-strategy.md
- pairs-with: archive/2026-05-23/m5-claude-code-skill.md

## Shape

Single Python module at `src/docs_cli/cli.py`, exposed as the
`docs` console-script via the `docs_cli.cli:main` entry point declared
in `pyproject.toml`. The `docs_cli/` package ships as a wheel on PyPI
(distribution name `docs-cli`); the bundled Claude Code skill rides
inside the same wheel as package data.

```
src/docs_cli/                            (Python 3.11+, stdlib only)
├── __init__.py                          ─ lazy re-export of `main`
├── cli.py                               ─ the CLI module (~9k lines)
│   ├── dunder version                   (__version__ = importlib.metadata.version("docs-cli"))
│   ├── config        — TOML load, Vocab merging, archive-dir resolution,
│   │                   `[migrate]` per-tree overrides (M7),
│   │                   `[exclude]` + `.docsignore` (M8)
│   ├── model         — Doc dataclass; metadata block parser + editors
│   ├── walker        — directory traversal, filter, archive detection
│   ├── index         — INDEX.md render with marker-block preservation
│   ├── archive       — atomic move + lifecycle edit (M2; M7 rename;
│   │                   M12 referring-edge rewrite; M26 plan/pre-flight/
│   │                   apply + `--json` operation record; M28a
│   │                   `Archived:` witness on every member)
│   ├── mv            — rename + Related: rewrite across tree (M2;
│   │                   M28 plan-before-move + body-link rebase;
│   │                   M28a cross-dated archive refusal)
│   ├── new           — scaffolded doc creation (M2)
│   ├── touch         — Updated: bump (M2; M12 outside-root refusal)
│   ├── check         — validation rules + exit-code matrix (M3;
│   │                   M25 reciprocity; M27 body-link scanner;
│   │                   M28a archive-date corroboration)
│   ├── list          — query view, human + --json (M3)
│   ├── migrate       — foreign-tree inference + plan/apply (M4)
│   ├── project       — rename verb (M12)
│   ├── install-skill — materialise the bundled skill onto a host (M6)
│   └── cli           — argparse dispatch, exit codes, --root resolution
└── skill/                               ─ bundled Claude Code skill (M5)
    ├── SKILL.md                          (frontmatter + trigger surface)
    └── references/
        ├── convention.md                 (byte-identical mirror)
        ├── cli.md                        (byte-identical mirror)
        ├── use-cases.md                  (M5; bundle-only, no `docs/` mirror)
        ├── adoption-playbook.md          (M8 F8; bundle-only, no mirror)
        └── docs-toml-template.toml       (M8 F8; bundle-only starter)
```

> Pinned by `tests/test_packaging.py` A3 to the bumping-target literal;
> runtime read goes through stdlib `importlib.metadata` so a single
> `pyproject.toml` version bump propagates to `docs --version`
> automatically (M12). Fallback to `0.0.0+local` (M12 — OQ-4) if
> `importlib.metadata.PackageNotFoundError` is raised — protects
> fresh-clone runs without `pip install -e .`.

**Sibling artifact: the Claude Code skill.** The Claude Code skill at
`src/docs_cli/skill/` (M5) is **not** a `cli.py` module and adds no
Python — it is a standalone Markdown artifact that *drives* the verbs
above: its `description` triggers an agent doing documentation work in
a `docs`-managed tree, and its body redirects to the right `docs` verb.
Alongside `SKILL.md` sit two bundled reference files at
`src/docs_cli/skill/references/` — byte-identical mirrors of
`docs/convention.md` and `docs/cli.md` — so an agent reading the skill
on any installed host has the spec on hand without needing the docs
repo checked out. Lockstep between the source specs and the bundle is
enforced by `tests/test_skill_refs.py`. The skill is authored and
version-controlled here, **ships as package data inside the
`docs-cli` wheel**, and is materialised onto a host via
`docs install-skill` (M6).

## Module responsibilities

### `model`

- `Doc` dataclass (frozen): `path`, `title`, `lifecycle` (M7-renamed from `status`), `role`, `project`, `updated`, `related: tuple[(verb, path), ...]`, `extra: Mapping[str, str | tuple[str, ...]]`, `body`, `archived`.
- `parse(text: str, path: Path, root: Path) -> Doc` — H1 + metadata block parser, layered on `parse_metadata_block` / `_metadata_line_span`.
- `parse` is pure (no I/O). M2 writes metadata back with surgical, minimal-diff line edits (`set_metadata_field`, `rewrite_related_refs`, `scaffold_doc`) rather than a full re-serializer — see the M2 milestone Decisions. M25 adds three more editors on the same contract: `add_related_edge` / `remove_related_edge` (one typed `Related:` bullet each way, creating the group when absent and dropping it when it empties, matching targets canonically) and `append_revision_entry` (one bullet into the repeatable `Revision:` audit group at the end of the metadata block). All three share `_bare_label_run` for group location — one label-parameterised scan serving both the `Related:` and `Revision:` groups — and `_metadata_line_span` for block boundaries, so no editor has its own notion of where the block or a group is.

### `config`

- `Config` dataclass (frozen): `project`, `archive_dir`, `date_format`,
  `lifecycles: frozenset[str]` (M7-renamed from `statuses`), `roles:
  frozenset[str]`, `index_filename`, plus M7's two `[migrate]` per-tree
  overrides: `role_suffixes: dict[str, str]` (custom filename-suffix →
  role mapping) and `project_name: str | None` (per-tree project override,
  equivalent to the `--config-project NAME` CLI flag), plus M8's four
  exclude fields: `exclude_dirs: tuple[str, ...]`, `exclude_globs:
  tuple[str, ...]`, `exclude_exts: tuple[str, ...]` from the `[exclude]`
  table, and `docsignore_patterns: tuple[str, ...]` carrying the raw
  line contents of a root-level `.docsignore` file.
- `load_config(root) -> Config` reads `.docs.toml` (or returns defaults
  when absent). M7: the `[vocabulary] add_statuses` TOML key was renamed
  `add_lifecycles` without a backward-compat alias; the new `[migrate]`
  section is optional. M8: also reads the optional `[exclude]` table
  and a root-level `.docsignore` file (raw line contents — compilation
  to regex is deferred to `compile_exclude_predicate`).
- `validate_lifecycle` / `validate_role` are the two vocab-checks (M7:
  `validate_status` was renamed `validate_lifecycle`).
- `compile_exclude_predicate(config, cli_excludes=(), cli_exts=()) ->
  Callable[[str], bool]` (M8 F3) returns a single layered predicate
  the walker consults. Combines `[exclude]` config, the root
  `.docsignore` file, and CLI overrides additively. Stdlib-only
  (`re`; uses an internal `_compile_docsignore_pattern` helper).

### `walker`

- `walk(root: Path, config: Config, predicate=None) -> Iterator[Doc]`
  — yields parsed Docs. M8 (F3) adds the optional `predicate`
  keyword for layered exclusion (see `config.compile_exclude_predicate`).
- Skips non-`.md`, hidden files, the root-level `INDEX.md`, and
  (when `predicate` is set) any path the predicate flags. The
  sibling `_iter_doc_texts` (lenient counterpart used by `check`,
  `list`, `migrate`) carries the same `predicate` keyword.
- Distinguishes active tree from archive subtree (via configured `archive_dir`).

### `index`

- `render_index(docs: list[Doc], config: Config, existing: str | None, root: Path) -> str`.
- If `existing` contains the marker block, preserves everything outside the markers.
- If `existing` is None or has no markers, creates a minimal file with markers.
- Active docs are grouped by `Project`, then by `Role` within each project;
  archived docs share one section.
- Deterministic: same inputs produce byte-identical output.

**Display order within Lifecycle: active.** The top level is one section per
`Project` — the docs root's own project first, then the rest in ascending
lexicographic order. Within a project, Roles follow the canonical convention
order (charter, plan, spec, milestone, log, status, decision, guide, runbook,
reference, postmortem, idea, implementation, sketch, outline, memo, brief,
template, example, notes — M7 adds the 7 core roles between `idea` and
`notes`), **except `status` is pinned to the top**
— it's the "you are here" pin and the entry point for most navigation. Within
each Role section, entries are sorted by `Updated:` descending, then by path
ascending as a deterministic tiebreaker.

**INDEX.md is excluded from walking** by name. The file is read once for
marker-block preservation, then ignored as a traversal target. The exclusion
is **root-level only** — a nested file named `INDEX.md` deeper in the tree
IS a walkable doc and is treated like any other Markdown file.

### INDEX renderer format

The renderer's output between the markers has a fixed shape so that
`docs index` is byte-deterministic and reviewable in diffs:

- **Summary line.** First line inside the marker block:
  ```
  _Generated YYYY-MM-DD. N docs active, M archived._
  ```
- **Section headings.** Active docs are grouped two levels deep — a
  level-2 heading per `Project`, then a level-3 heading per Role group:
  ```
  ## Project — <name>

  ### Active — <Role-titlecased>
  ```
  A doc with no `Project:` line is bucketed under the docs root's
  configured default project. Archived docs share one level-2 heading,
  `## Archived` — flat, not project-grouped.
- **Project group order.** The docs root's own project (the configured
  `project`) comes first; the remaining projects follow in ascending
  lexicographic order. Projects with zero active docs are omitted.
- **Role group order.** Within each project, `status` is pinned to the
  top. The remaining Roles follow `CANONICAL_ROLE_ORDER` (defined in
  `src/docs_cli/cli.py`) — charter, plan, spec, milestone, log,
  decision, guide, runbook, reference, postmortem, idea,
  implementation, sketch, outline, memo, brief, template, example,
  notes (M7 — F10 adds the 7 core roles between `idea` and `notes`).
  Role groups with zero entries are omitted. `## Archived` appears last,
  after every project.
- **Within-section sort.** Primary key: `Updated:` descending. Tiebreaker:
  path ascending (lexicographic on the root-relative path).
- **Entry format.** One bullet per doc:
  ```
  - [<path>](<path>) — _role_ — <description>. Updated YYYY-MM-DD.
  ```
  Both the link text and the href are the doc's **root-relative POSIX
  path** (e.g. `topics/deep-dive.md` for a doc in a subdirectory) — not the
  bare basename, which would break links for any doc outside the root.
  Description source: the first non-empty paragraph of the doc body
  (after the metadata block), with internal newlines collapsed to spaces
  and trimmed to ~120 characters (cut at the last whitespace before the
  limit; suffix with `…` if truncated).
- **Markers verbatim.** `<!-- docs:generated start -->` and
  `<!-- docs:generated end -->` — exact strings, including the spacing.
  The renderer matches them as literal substrings; no regex with variant
  whitespace.

Preservation rule: everything outside the markers (preamble before
`<!-- docs:generated start -->` and trailer after `<!-- docs:generated end -->`)
is copied verbatim into the regenerated file. If the existing INDEX
contains no markers, the renderer creates a minimal file containing only
the marker block and the derived content.

### `migrate`

- `migrate` adopts a *non-conforming* foreign directory into the convention.
  It is read-only by default (a dry-run plan); `--apply` performs the edits.
- **Inference helpers** — pure functions, no I/O:
  - `infer_role(filename, metadata, config=None) -> (role, confidence)` —
    multi-pass: in-file `Role:` (high) → filename-suffix match (high) →
    `_M\d+` milestone pattern (medium) → non-role-suffix strip
    (`_v\d+`/`_Draft`/`_Ready`) + re-match (medium) → `notes` fallback
    (low). Word-boundary tolerance: tokeniser splits on `-`/`_`/whitespace
    AND case-transition (`MyPlan` → suffix `plan`). Optional `config`
    extends the built-in suffix map with `config.role_suffixes`.
    Confidence is a `Confidence(enum.Enum)` member (`HIGH | MEDIUM |
    LOW`) — M10 replaces the legacy `True | "medium" | False` tri-value.
    The enum's `value` strings (`"high"`/`"medium"`/`"low"`) match the
    M4 JSON wire format byte-for-byte; `migration_to_json` crosses
    enum→string via `fm.confidence.value` at the boundary.
  - `infer_project(filenames, dir_name) -> str` — the longest common
    `-`/`_`-delimited filename prefix, or the directory name.
  - `normalise_project_name(name) -> str` (M7 — F11) — splits on case
    boundaries (`FooBar`), letter↔digit (`Abc5Mig`), underscores;
    lowercases; trims; collapses repeats. Preserves digit-after-digit so
    `2026-01-26` survives intact.
  - `infer_lifecycle(metadata, in_archive) -> (lifecycle, confident)` —
    in-file `Lifecycle:` line, else `archived` (in an archive subdir)
    or `active`. (Renamed from `infer_status` at M7 Phase 10 simplify.)
  - `infer_updated(metadata, mtime, date_format) -> (updated, confident)` —
    in-file `Updated:` line, else the file mtime.
  - `detect_archive_layout(rel_path, archive_date) -> str | None` — maps a
    non-conformant archive-style path (`archived/`, `project-history/`, a
    bare `archive/file.md`) to `archive/<date>/<basename>`; returns `None`
    for an active-tree file or one already at `archive/<valid-date>/`.
  - `_infer_role_from_h1(text) -> str | None` (M7 — F1) — H1 trailing-word
    match; longest match wins; word-boundary required.
  - `_infer_role_from_sections(text) -> str | None` (M7 — F1) — top-level
    `## ` heading pattern match (plan / status / decision / log shapes).
  - `_sibling_default(rel, sibling_roles) -> str | None` (M7 — F1 / OQ-C)
    — modal sibling role at ≥ 60% over ≥ 5 same-subdir suffix-confident
    files.
  - `_multi_project_hints(root, parent_project, threshold=5) -> tuple[str, ...]`
    (M7 — F5) — emits one `"hint: …"` line per immediate subdir whose
    `.md` common-filename-prefix differs from `parent_project` and
    covers ≥ `threshold` files. Candidate name is the file-prefix
    (per OQ6).
- **Block-insertion** — `insert_metadata_block(text, *, title, status, role,
  project, updated, date_format)` places (or synthesises) the H1, inserts the
  required metadata block (M7 — writes `Lifecycle:`), preserves the body
  verbatim, and reconciles any pre-existing metadata-shaped lines into the
  block instead of duplicating them; non-required pre-existing lines (a
  free-form `Status:`, `Owner:`, `Tags:`, `Related:`, etc.) are preserved
  into a `## Migrated metadata` body section with each label `Migrated-`
  prefixed. Distinct from `set_metadata_field` (edits an existing
  block) and `scaffold_doc` (builds from nothing) — see the M4 Decisions.
  The function-signature parameter is still named `status` for back-
  compat (Phase 10 simplify candidate).
- **Plan / apply** — `plan_migration(root, archive_date=None, *,
  cli_config_project=None) -> MigrationPlan` walks the tree (via
  `_iter_doc_texts` with a default `Config`), runs the inference helpers,
  and assembles one `FileMigration` per `.md` file with a confidence and
  every ambiguity flagged. M7 (F11) consults the precedence chain
  CLI `--config-project` > `.docs.toml [migrate] project_name` >
  F11-normalised(inferred); the pre-normalisation name flows onto
  `MigrationPlan.project_original` when normalisation changed it. M7 (F4)
  uses each file's `Updated:`/mtime as the archive-move date when
  `archive_date` is `None`. A medium-confidence upgrade pass over
  `notes`-fallback files runs H1 → section → sibling-set in order. M7
  (F5) emits `MigrationPlan.multi_project_hints` via
  `_multi_project_hints` unless `cli_config_project` is set.
  `apply_migration(plan)` executes it: `insert_metadata_block` +
  `atomic_write` per file, plus the archive moves. After each
  archive-move it calls `_opportunistic_rmdir(old_parent, plan.root)`
  to clear the now-empty source dir (M10 — OQ-G; swallows OSError on
  a non-empty parent so non-migrating siblings survive). After the
  file loop it calls `_ensure_docs_toml(plan)` which writes (or
  extends) the root `.docs.toml` sidecar so the adopted tree is
  immediately self-describing — absent sidecar gets a minimal
  `[project] name = "<resolved>"` + `[archive] date_format` block;
  existing sidecar without `[project]` gets the new block appended
  under a `# Added by docs migrate --apply` provenance comment;
  existing `[project]` is never overwritten (M10 — OQ-A).
  `migration_to_json(plan)` serialises the whole plan to the `--json`
  schema pinned in [cli.md](cli.md).
- **Models** — `FileMigration` (frozen) carries one per-file decision: the
  inferred `role`/`project`/`lifecycle` (M7-renamed)/`updated`,
  `confidence: Confidence` (a `Confidence` enum member — M10 replaces
  the M7 tri-string with the enum; `Confidence.MEDIUM` requires empty
  `ambiguities`), `ambiguities`, `synthesized_h1`,
  `reconciled_metadata`, and an optional `archive_move` destination.
  `MigrationPlan` (frozen) holds the `root`, the tuple of
  `FileMigration`s in root-relative path order, `project_original:
  str | None` (M7 — the pre-normalisation project name when F11
  changed the value, else `None`), and `multi_project_hints:
  tuple[str, ...]` (M7 — F5 advisory hints, empty when none apply or
  when the CLI override is in force). M10 — OQ-D — drops the unused
  `excluded_count: int` field (set in `plan_migration` but read
  nowhere in shipped code); consumers that need the total compute it
  from `excluded_breakdown`.
- **Config** — `Config` (frozen) carries the resolved configuration
  for a docs root. M10 — OQ-H — adds `fields: frozenset[str]` (sourced
  from `[vocabulary] add_fields`, case-sensitive exact match;
  defaults to the empty set) which widens the `unknown-field` check's
  allowlist on top of the built-in always-allowed metadata labels
  (`_BUILTIN_METADATA_FIELDS`). The rule is opt-in: an empty
  `Config.fields` switches the warning OFF entirely.
- **Scope boundary** — the active-tree directory layout is left untouched;
  `--apply` adds metadata in place and only ever moves docs out of detected
  archive-style subdirs. No role-bucket flattening or project re-foldering.

### `check`

- `check_doc(path, text, root, config, stale, today, stale_source) -> list[Finding]`
  — every **single-document** rule (`missing-field`, `bad-vocab`,
  `bad-date`, `status-drift`, `broken-ref`, `stale`, `malformed`,
  `unknown-field`, `duplicate-field`, `broken-body-link`,
  `outside-root-body-link`, `archive-date-drift`). Never raises: a
  validator must describe malformed input, not blow up on it.
- M25 (D7) adds `duplicate-field` via `_duplicate_labels(text)`, which
  counts the metadata block's **raw label lines** rather than reading
  `parse_metadata_block`'s output. It has to: that function assigns
  `metadata[label] = tuple(values)`, so a repeated label has already
  overwritten the earlier one — and discarded its values — by the time the
  parsed mapping exists. This is the one rule whose evidence is destroyed
  by parsing.
- `check_tree(...)` materialises the `_iter_doc_texts` walk **once**, so
  the one rule that needs more than one document can see the whole set.
- M25 adds that rule: `reciprocity_findings(entries, root) ->
  dict[Path, list[Finding]]` is a **cross-document pass** that indexes
  every parseable walked doc by root-relative path and then requires each
  recognized reciprocal edge (`inverse_verb(verb) is not None`) to have its
  exact inverse pointing back. Its results are keyed by source path and
  interleaved into `check_tree`'s existing per-doc grouping — `check_doc`'s
  findings first, then any `missing-inverse` — rather than appended as a
  tail block. A target that is excluded, unresolvable, non-Markdown, or
  malformed is simply absent from the index, so those four applicability
  conditions collapse into a single lookup and the owning rules keep their
  cases.
- M27 (D1/D2/D5) adds `broken-body-link` and `outside-root-body-link` as
  **per-document** rules inside `check_doc` — deliberately *unlike*
  `reciprocity_findings`, and the contrast is the design point: both rules
  need only the referring document's own text and its own directory, so
  there is **no** second `check_tree` pass and `docs touch --check` inherits
  them for free through `_run_touch_check` → `check_tree`.
- M28a (D3/D4) adds `archive-date-drift` the same way — one
  `findings.extend(archive_date_findings(path, metadata, root, config))`
  inside `check_doc`, placed immediately after the lifecycle/location
  `status-drift` block so the two location-versus-metadata rules stay
  adjacent. It rests on **two pure helpers**, and their relationship is the
  design point:
  - `archive_dir_date(rel, config) -> date | None` — the date of the dated
    archive directory `rel` sits in. It is **shared by both legs**:
    `archive_date_findings` (Leg 1, in `check`) and
    `cross_dated_archive_move` (Leg 2, in `mv`) both read it, so the two can
    never disagree about what a dated archive directory is. It is also the
    **config-aware sibling `detect_archive_layout` is not** — that one
    hardcodes the literal `"archive"` and `"%Y-%m-%d"`, takes no `Config` at
    all, and lives in the migrate half; this one honours `config.archive_dir`
    (through `_is_archived_rel`) and parses the segment with
    `config.date_format` through the same `parse_date` path `check_doc`
    already uses for `Updated:`.
  - `archive_date_findings(path, metadata, root, config) -> list[Finding]` —
    the rule itself, shaped exactly after `body_link_findings`: per-document,
    **no filesystem access of any kind** (it uses `_root_relative`, never
    `path.resolve()`), and therefore no second `check_tree` pass. It is
    **present-only** — a document with no `Archived:` line produces nothing,
    ever — which is what lets a hard error be additive on every existing
    tree.
- The pipeline behind them is pure and stdlib-only: `_mask_code(text)` →
  `scan_body_links(text) -> tuple[BodyLink, ...]` →
  `classify_destination(raw)` → `normalise_body_link_target(doc_rel, path)` →
  `_body_link_is_contained(candidate)` → one `.exists()`. Only
  `body_link_findings` touches the filesystem, and only on a candidate
  containment has already proved to be neither a `..`-escape nor **absolute**
  — the absolute leg matters because a percent- or backslash-encoded leading
  slash reaches containment classified `local`, and `posixpath.join` lets it
  win the join.
- **`_mask_code` is length-preserving, and that is what makes the whole
  thing work.** It blanks the *contents* of fenced blocks and inline code
  spans with spaces, leaving the mask the same length as the input with a
  newline at every offset the input has one. Every offset the scanner
  reports is therefore an offset into the **original** text — which is what
  lets `BodyLink` carry an exact destination-token span
  (`text[start:end] == raw`) that **M28** splices a replacement into. One
  scanner, never a second Markdown parser.
- The scan is a single linear forward pass in which **every inner scan is
  O(1) amortised**. Two precomputed tables read through monotone cursors do
  most of it — `_blank_line_starts` for the candidate bound and
  `_label_closers` for the label's closing `]` — plus resumption at the failed
  candidate's `]`, an early return past `MAX_DESTINATION_PAREN_DEPTH`, and
  `_seek_unescaped`'s memo for an unterminated `>` / `"` / `'` / `)`. The
  newline bound on an angle destination and the blank-line bound on a `(…)`
  title are **grammar** rules and bound nothing inside one long paragraph, so
  they are not what keeps the scan linear; the memo is. The
  pathological-input runtime lock carries a case for each of these, including
  the two many-unterminated-delimiter shapes the Step-2 review measured at
  3.27 s and 5.96 s before the memo existed.
  Resume-at-`]` has **two** exceptions, both correctness requirements rather
  than bounds, and both O(1) because `_label_closers` answers them from a
  table: a rejected **image** resumes at `[` + 1, so a link inside the image's
  label is still seen; and a label that does not close before the candidate's
  bound resumes at `[` + 1 too, because rule 2's nested-image exception means
  a later `[` in the same paragraph may still close at a different nesting
  level.
- Reuse rather than new machinery: `_root_relative` for the referring
  document's path, `_canonical_related_target`'s `posixpath.normpath` idiom
  for lexical normalisation, and `_candidate_exclusion_reason`'s
  `outside-root` predicate — all three legs — for containment.
  `_iter_doc_texts`, `exit_code_for`, `finding_to_json` and
  `_print_check_findings` are all unchanged. The stdlib-only pin holds:
  `urllib.parse`, `posixpath`, `string`, `re`.

#### Move-safe body-link rewrites (M28)

M27 validates body links; **M28 is the only writer of them**, and it consumes
exactly the span contract above. The whole planner is one banner section
between `body_link_findings` and the M3 check rules, and every function in it
is pure except two named boundaries:

```
plan_body_link_rewrites(rel, new_rel, text, moves)   pure — the 8-step formula,
        │  -> tuple[LinkRewrite, ...]                per occurrence, no I/O
        ▼
render_destination_token(raw, new_path, fragment)    pure — delimiter form
        │                                            invariant, minimal encode
        ▼
splice_body_links(text, rewrites)                    descending `start`, so
        │                                            earlier offsets stay valid
        ▼
plan_move(root, config, entries=…, moves=…,          pure — the caller's walk,
        │  related_pairs=…, strand_check=…)          both strand legs
        │  -> MovePlan
        ▼
preflight_move_plan(plan)                            writable / span-consistent /
        │                                            non-overlapping; raises
        ▼                                            before any write
apply_move_plan(plan)                                one atomic_write per changed
                                                     NON-moving document
```

- **Four frozen records**, shaped after `RelateEdit` / `RelatePlan` and
  `ArchiveMove` / `ArchivePlan`: `LinkRewrite` (one occurrence, carrying M27's
  `BodyLink` verbatim), `DocRewrite` (one document's whole planned edit,
  carrying both the text the plan was computed from and the text it would
  write), `Strand` (one still-active inbound reference, both ends named), and
  `MovePlan`.
- **`plan_move` takes `entries` rather than a root to walk**, which is what
  makes the plan a pure function of the tree: each verb feeds it the walk it
  already runs, and the planner opens nothing.
- **One formula, not two code paths.** Class 1 (the target moved) is the case
  where the move-map lookup fires; class 2 (the referrer moved) is the case
  where the relativisation base differs from the resolution base. The
  semantic no-op test between them is what makes a co-moving pair a zero-byte
  diff.
- **The move map is canonical; the `Related:` pairs are alias-expanded.** Two
  arguments, because the two halves match differently — the body planner
  matches on the normalised target and needs no alias list at all, while
  `rewrite_related_refs` matches a bullet by exact string.
  `_archive_move_map` and `_archive_related_pairs` build them from an
  `ArchivePlan`; `docs mv` passes one pair and lets `related_pairs` default.
- **The strand-check is `archive`-only** and lives inside `plan_move` because
  it is a property of the finished plan, not of the CLI: leg 1 fills
  `MovePlan.orphans` (the `child-of` refusal set), leg 2 fills
  `MovePlan.strands` (everything else). The two legs partition the graph by
  **edge**, so one document can contribute to both.
- **`move_plan_to_json` returns the shared section only** — `{"rewrites": …,
  "strands": …}` — and each verb splices what it carries into its own record.
  One serializer is what makes `docs mv --json` and `docs archive --json`
  byte-comparable by construction rather than by discipline.

### `relate` (M25)

- `plan_relate(...) -> RelatePlan` reads both endpoints and stages both
  complete texts in memory; `apply_relate_plan(plan)` publishes them.
  The `plan_migration` / `apply_migration` split, applied to a two-file
  edit.
- `apply_relate_plan` implements the D5 contract: re-validate the staged
  texts, `os.access` writability pre-flight on each changed **file**, then
  publish source-then-target through the module-global `atomic_write`,
  rolling every already-published endpoint back through the same
  `atomic_write` on a later failure. Best-effort staged publish + rollback,
  not a filesystem transaction — two files cannot be renamed atomically as
  a unit on POSIX, and the spec says so rather than implying otherwise.

### `archive` (M26, extended by M28 and M28a)

The same plan/apply split as `relate`, one stage longer and with a
deliberately different failure boundary:

```
archive_candidates(doc, root, config, scope)   pure — one-hop pairs-with /
        │                                      child-of edges, deduplicated on
        ▼                                      the canonical rel, scope matched
plan_archive(...) -> ArchivePlan               pure — destinations for the
        │                                      SELECTED members only
        ▼
preflight_archive_plan(plan)                   proves all five per-member
        │                                      properties; raises before any write
        ▼
walk(root, config, predicate) -> entries       M12 / M14 (A6), step 8
        │
        ▼
plan_move(root, config, entries=…, …)          M28, step 8b — the rewrite plan
        │  -> MovePlan                         and both strand legs
        ▼
preflight_move_plan(move_plan)                 M28, step 8c
        │
        ▼
(leg-1 refusal on move_plan.orphans)           M28, step 8d — exit 2, no record
        │
        ▼
apply_archive_plan(plan, texts=…)              drives `_archive_one` in
        │  -> [(old, new), ...]                plan.moves order, primary first,
        │                                      each member's PLANNED text
        ▼
apply_move_plan(move_plan)                     M28 — one write per changed
        │                                      non-moving document
        ▼
_refresh_index(root, config)                   exactly once, at the end
```

The preview runs the same walk / `plan_move` pair at step **5b** instead, and
stops there at exit 0 — so it adopts a failure of plan *construction* (a
malformed tree it cannot read) and only *reports* a plan *consequence* (leg 1's
verdict). The write path's walk stays at step 8 so that every message
precedence M26 froze at step 7 is unchanged.

- **Validate-all-first with a residual admission**, in contrast to M25's
  staged publish plus rollback. Every failure the tool can foresee is a
  pre-flight refusal with **zero** bytes written — the primary included.
  There is no rollback: an unexpected `OSError` mid-execution produces an
  exact partial-state admission naming what moved and what did not.
  Extending D5's rollback from two documents to N was considered and
  explicitly declined (M26 — D4), because each undo must reverse both a move
  and a metadata edit and the referring-edge rewrite runs afterwards.
- The two exceptions share one carrier. `CoordinatedWriteError` now spans
  both verbs; `exit_code` on the exception carries M26's exit-1/exit-2 split
  so `preflight_archive_plan` can stay `-> None`.
- `_archive_one` is the one place per-member metadata is written —
  `apply_archive_plan` is only its ordered driver, and the edit-then-move
  atomicity lives where it always did. **M28a adds exactly one
  `set_metadata_field` call there**, writing `Archived: <date_str>` between
  the `Updated:` bump and the conditional `Archived-reason:`. Two properties
  come free from that placement rather than from new code: the value is the
  **same `date_str`** `_cmd_archive` computed once and threaded to every
  member, the one that also names the dated directory (never a second
  `strftime`, never a `date.today()` re-read); and the field's **position in
  the block is decided only by this call order**, because
  `set_metadata_field` appends a new inline label at the end of the inline
  run and inserts before the first bare-label group. There is no field-order
  rule anywhere in the tool, which is why the order of these calls *is* the
  contract. `apply_archive_plan`'s `plan.reason if index == 0 else None`
  special case is untouched: the **reason** stays primary-only (M26 — D1),
  the **date** reaches every member (M28a — D2).
- **Authorization is a CLI-layer concept, discovery is not.**
  `archive_candidates` reports the whole neighborhood with each member's
  state; `_cmd_archive` decides what that means for the exit code. That is
  why `--json` can carry the full candidate set in every mode while the
  stderr prose stays quiet under a plain `docs archive FILE`.
- **M28 threads each moving member's planned text into `_archive_one`**
  (`apply_archive_plan(plan, texts=…)`) rather than letting it re-read the
  file. That is what keeps the contract at **one `atomic_write` per document,
  never two**: the member's body-link splices, its `Related:` rewrites and its
  archive metadata edits are all applied to one in-memory text. Both
  parameters default to the pre-M28 behaviour, so a direct caller with no
  rewrite plan is unaffected.

### `mv` (M14, inverted by M28, refusing cross-dated relocations since M28a)

`docs mv` had no plan/apply split before M28 — it renamed the file and rewrote
references afterwards. A class-2 rebase needs the moved document's own text
*and* both of its paths, and an all-or-nothing contract needs the plan
complete before the move, so the order is inverted:

```
(cross-dated archived refusal)               M28a — exit 2, zero bytes,
        │                                    BEFORE the walk and the preview
        ▼
walk(root, config, predicate) -> entries     M14 (A1)'s pre-flight walk, now
        │                                    doubling as M28's plan walk
        ▼
plan_move(root, config, entries=…,           strand_check=False — a rename
        │  moves={old_rel: new_rel})         produces no newly-archived set
        ▼  -> MovePlan
(preview branch: print + --json; exit 0)     step 5b
        │
        ▼
preflight_move_plan(plan)                    step 6 — zero bytes on any refusal
        │
        ▼
atomic_write(old_path, moved.new_text)       the moved document's planned text,
        │                                    to its OLD path
        ▼
old_path.replace(new_path)                   the rename
        │
        ▼
apply_move_plan(plan)                        every other planned document
        │
        ▼
_refresh_index(root, config)                 exactly once, at the end
```

Writing the member before the rename is what makes the partial-state admission
exact: a `replace` that raises leaves the old path holding text rebased for a
directory the file is not in, so `_mv_partial_state` reports the moved document
under `Moved:` **iff the rename succeeded** and under `Rewritten:` otherwise.
`moved` is absent from the plan only when `[exclude]` / `.docsignore` hid the
document from the walk (R11), in which case the file is simply renamed.

**M28a's refusal sits above the whole pipeline, not inside it.**
`cross_dated_archive_move(old_rel, new_rel, config)` is decidable from the two
root-relative paths and the tree's config alone, so it is evaluated the moment
those two strings exist — after the two exit-1 argument guards (`<old>` is not
a file, `<new>` already exists, which are wrong in a way that must be fixed
first) and **before** the `--dry-run` branch and the validate-all-first walk.
Three consequences follow from that position and none of them is incidental:
the refusal reaches **every** mode, so a preview cannot print `would move …`
for an operation the apply refuses; it names the document the operator asked
for rather than an unrelated malformed sibling the walk would have hit first;
and it is unreachable by `[exclude]` / `.docsignore`, which govern the walk and
never the predicate. It is deliberately **not** inside `preflight_move_plan` —
`_cmd_mv` returns at `--dry-run` before that call, and `_cmd_archive` calls the
same pre-flight, where the predicate would be dead code because archive never
moves an already-archived member. The predicate delegates to the same
`archive_dir_date` the `check` rule uses, which is what makes "the two legs
can never disagree about what a dated archive directory is" structural rather
than a promise.

### `cli`

- `argparse` subparsers per verb.
- Resolves docs root by walking up from cwd, looking for `.docs.toml`; falls back to cwd.
- Exit codes per [cli.md](cli.md).
- Top-level `main()` is what the shebang executes.

## Data flow (M1 happy path: `docs index`)

```
cwd ──► find_root() ──► load_config(.docs.toml) ──┐
                                                  ▼
                                          walk(root, config)
                                                  │
                                                  ▼
                                          [Doc, Doc, ...]
                                                  │
                                                  ▼
                  read INDEX.md (if exists) ──► render(docs, config, existing)
                                                  │
                                                  ▼
                                          write INDEX.md atomically
```

## Atomic write pattern

Used everywhere the tool mutates a file:

```python
tmp = path.with_suffix(path.suffix + ".docs-tmp")
tmp.write_text(new_content)
tmp.replace(path)   # POSIX-atomic on same filesystem
```

For archive operations (M2): edit in-place first (atomic write), then move with `Path.replace` (atomic within the docs root's filesystem). The move happens after the edit, so a failure during the edit leaves the original untouched.

## What's deliberately not architected

- No plugin system. Verbs are functions; adding one is editing this file.
- No abstract base classes. Dataclasses + free functions only.
- No async. Single-threaded; the largest expected tree is in low thousands of files.
- No caching layer. Re-parse on every command; profiling will tell us if this matters.
- No logging framework. `print(..., file=sys.stderr)` is sufficient.

## Dependencies

- Python 3.11+ (for `tomllib` in stdlib).
- No third-party runtime dependencies.
- Test-time: `pytest`. Development: `ruff` and `mypy`. All declared under `[project.optional-dependencies] dev` in `pyproject.toml`.

## Install (end users)

```sh
pip install docs-cli                           # lands `docs` on PATH
docs install-skill                             # materialise the bundled skill at ~/.claude/skills/docs/
```

`docs-cli` is published on PyPI; the wheel carries the bundled Claude
Code skill inside as package data, so a single `pip install` plus the
one-shot `docs install-skill` is enough to use the CLI and to make the
skill discoverable by Claude Code. No git clone required for runtime
use. The committed skill artifact is host-agnostic; the host-specific
path lives only in the `install-skill` invocation.

`install-skill --dest <DIR>` overrides the default destination; `--force`
overwrites a non-identical existing directory; `--symlink` is supported
only for editable installs. The release runbook at
[release-runbook.md](release-runbook.md) covers the publishing side.

## Development setup

```sh
git clone https://github.com/ArtRichards/docs-cli.git ~/opt/docs-cli
cd ~/opt/docs-cli
python3 -m venv .venv                          # Python 3.11+; needs python3-venv on Debian/Ubuntu
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"              # editable install + pytest/ruff/mypy/build
```

The editable install lands `.venv/bin/docs` on PATH pointing at the
in-tree `src/docs_cli/cli.py`. `.venv/` is gitignored; recreate it
from scratch in a fresh clone.

## Commands (development)

```sh
.venv/bin/python -m pytest -q                  # run tests
.venv/bin/ruff check .                         # lint
.venv/bin/ruff format --check .                # format check
.venv/bin/mypy                                 # type-check (tree-wide, per pyproject)
.venv/bin/docs check docs/                     # dogfood smoke
.venv/bin/docs index --root docs/ --dry-run    # smoke: idempotent dogfood
.venv/bin/python -m build                      # produces dist/docs_cli-<v>-*.whl + .tar.gz
```
