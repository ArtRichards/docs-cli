# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.4.0 — UNRELEASED

M10: adoption-flow polish + 1.3.0 carry-overs. Bundles two
agent-driveability features (multi-file atomic `docs touch`;
`docs migrate --apply` writes the `.docs.toml` sidecar
automatically) with the carry-overs from M3
(`[vocabulary] add_fields` allowlist + `unknown-field` check
warning), M7 (`Confidence` enum replacing the `bool | str`
tri-value), and M8 (`--apply --quiet` per-file output
suppression, `MigrationPlan.excluded_count` removal,
adoption-playbook restructure). 1.4.0 is ready locally; the
PyPI publish is deferred to M11.

### Added

- **`docs touch <file>...`** (M10 — OQ-C) — multi-file atomic
  touch. Accepts one or more positional file paths. Validates
  every path first (existence + same-docs-root); aborts the
  whole batch on any failure (named-bad-path on stderr, exit
  1, no on-disk mutation); refreshes the INDEX exactly once
  at end-of-batch.
- **`docs migrate --apply` writes `.docs.toml` automatically**
  (M10 — OQ-A / OQ-L / OQ-M). Absent sidecar gets a minimal
  `[project] name = "<resolved>"` + `[archive] date_format`
  block. Existing sidecar without `[project]` gets the new
  block appended under a `# Added by docs migrate --apply`
  provenance comment header. Existing `[project]` is never
  overwritten. No `dir = "archive"` line is emitted (the
  default is stable).
- **Opportunistic empty-parent rmdir after archive-move**
  (M10 — OQ-G / OQ-Q). After `--apply` moves a foreign
  archive-style file into `archive/<date>/`, the now-empty
  source parent dir is removed. `OSError(ENOTEMPTY)` is
  swallowed so non-migrating siblings survive.
- **`[vocabulary] add_fields` allowlist + `unknown-field`
  check rule** (M10 — OQ-F / OQ-H / OQ-O / OQ-P). Opt-in
  warning (exit 1) for extra metadata labels not on the
  built-in always-allowed set
  (`Lifecycle` / `Role` / `Project` / `Updated` / `Related` /
  `Archived-reason`) and not on `add_fields`. The rule is
  OFF by default — trees without the allowlist see no
  change. Matching is case-sensitive exact match.
- **`Confidence` enum** (M10 — OQ-E / OQ-N) replacing the
  M4-era `bool | str` tri-value for `infer_role` and
  `FileMigration.confidence`. The enum's `value` strings
  (`"high"` / `"medium"` / `"low"`) match the M4 JSON wire
  format byte-for-byte; `migration_to_json` crosses
  enum→string via `enum.value` at the boundary.

### Changed

- **`docs migrate --apply --quiet`** (M10 — OQ-B) now
  suppresses the per-file plan block on stdout in addition
  to the trailing `docs: migrated <N> file(s) ...` success
  line on stderr. Empty stdout + empty stderr on a clean
  `--apply --quiet` run. `--dry-run` / `--summary` /
  `--json` are requested outputs and never suppressed.
- **`docs touch <file>` is now `docs touch <file>...`**
  (M10 — OQ-C). Single-file invocation continues to work;
  the argparse spec is `nargs="+"`.
- **Adoption playbook restructured to 4 steps** (M10 — OQ-I)
  — plan / triage / apply / verify. The three-pattern
  ordering note in Step 3 (about when to write `.docs.toml`
  before vs. after `--apply`) is gone now that `--apply`
  writes the sidecar automatically. The worked example runs
  end-to-end with `--apply --quiet` and immediately runs
  `docs check`.
- **`MigrationPlan.excluded_count` removed** (M10 — OQ-D)
  as a breaking change. The field was set in
  `plan_migration` but never read in shipped code. The
  human plan footer iterates `excluded_breakdown` directly;
  `migration_to_json` omitted the field already. Consumers
  who need the total compute `sum(c for _, c in
  excluded_breakdown)`. No known external consumer.

### Notes

- **Version bump.** 1.4.0 (minor); SemVer-compliant since
  the only breaking surface (`MigrationPlan.excluded_count`)
  has no known external consumer.
- **JSON wire format byte-stable.** Despite the internal
  `Confidence` enum replacement, every JSON record's
  `confidence` field still emits a string
  (`"high"|"medium"|"low"`) via `Confidence.value`. No
  consumer should break.
- **`docs touch` exit-code semantics unchanged.** Atomic
  multi-file failure exits 1 (any bad path) or 2 (malformed
  `.docs.toml`); a successful multi-file batch exits 0. The
  single-file behaviour is unchanged from 1.3.0 — the
  new contract surface is purely additive for multi-file
  invocations.

## 1.3.0 — 2026-05-25

M8: the adoption workflow becomes agent-driveable. A single
layered exclusion surface (`--exclude` / `[exclude]` /
`.docsignore`) replaces the M7 "everything walks" semantic;
the migrate plan grows triage flags (`--summary`,
`--only ambiguous`, `--group-by`) and a default footer
summary; non-Markdown root siblings surface in the plan; and
`docs new --body-from` closes the read-before-write friction
in agent flows. The bundled skill gains a substantial
adoption playbook + a starter `.docs.toml` template.

Per the post-M8 batched publish (M9), 1.3.0 ships locally
only — the public PyPI release is the same 1.3.0 number,
batching the M6 + M7 + M8 surface into one publish event.

### Added

- **`--exclude PATTERN`** (M8 — F3) on `docs migrate`, `docs
  index`, `docs check`, `docs list`. Repeatable; supports
  gitignore-flavoured globs (`*` / `**` / trailing-`/` /
  leading-`/`). Layered on top of `[exclude]` config and
  `.docsignore`.
- **`[exclude]` table in `.docs.toml`** (M8 — F3). Three
  keys: `dirs = [...]` (directory-name matches at any
  depth), `globs = [...]` (gitignore-flavoured patterns),
  `exts = [...]` (extension matches).
- **`.docsignore`** at the tree root (M8 — F3). One file
  only — nested files are NOT consulted (OQ-B). One
  pattern per line; gitignore-flavoured syntax subset
  (comments, blanks, `**`, `*`, `?`, trailing-`/`,
  leading-`/`, `!` negation, bare-pattern any-depth match).
- **`--exclude-ext EXTS`** (M8 — F3) on `docs migrate`.
  Comma-separated list of extensions to suppress from the
  non-Markdown sibling footer and from any exclude-predicate
  evaluation.
- **`--summary` triage mode** (M8 — F6) on `docs migrate`.
  One tabular line per file (`path  role  conf  notes`).
  Mutually exclusive with `--json` (argparse-enforced).
- **`--only ambiguous` filter** (M8 — F6) on `docs migrate`.
  Drops the high-confidence-no-ambiguity rows from the
  per-file plan. Composes with `--summary` and `--group-by`.
- **`--group-by role|confidence`** (M8 — F6) on `docs migrate`.
  Sorts the per-file plan by role (alphabetical) or by
  confidence (`high → medium → low`).
- **Default plan-footer summary** (M8 — F6). Every
  `docs migrate` dry-run emits four anchored tokens after
  the per-file block: `summary:`, `roles:`, `confidence:`,
  `ambiguities:`. Always present, even on an empty plan.
- **Non-Markdown root-sibling surfacing** (M8 — F7). The
  `docs migrate` dry-run footer surfaces non-`.md` siblings
  at the migration root as `<N> non-Markdown siblings at
  root not considered: <names>` so an adopting agent sees
  binaries referenced from prose. Suppressed entirely when
  `--exclude-ext` filters the list to empty.
- **`docs new --body-from <PATH|->`** (M8 — F9). Reads body
  content from a file or stdin and appends it under the
  scaffolded frontmatter. Atomic, one Bash call.
  Conservative refusal heuristic (OQ-E): the first 20 body
  lines are scanned for `^[A-Z][A-Za-z-]+:\s` and the call
  exits 2 if any match — agents must pass body content
  only; `docs new` owns the frontmatter.
- **Adoption playbook** at
  `src/docs_cli/skill/references/adoption-playbook.md` (M8
  — F8). Six-step procedural deep-dive: dry-run → triage →
  `.docs.toml` → iterate → apply → verify. Includes a
  worked example and a pitfalls subsection.
- **`.docs.toml` template** at
  `src/docs_cli/skill/references/docs-toml-template.toml`
  (M8 — F8). Commented starter for `[exclude]`,
  `[migrate]`, `[vocabulary]` (+ `[project]` /
  `[archive]`); every example line commented out.
- **SKILL.md adoption pointer + trigger phrases** (M8 — F8).
  Description gains four adoption-flow phrases ("adopt this
  directory", "migrate this folder", "bring this into docs
  convention", "import existing markdown specs"). A new
  one-line pointer block redirects to
  `references/adoption-playbook.md` near the verb table.

### Changed

- **Migrate carve-out widened** (M8 — OQ1). A `.docs.toml`
  carrying `[exclude]` is accepted by `docs migrate` even
  alongside the M7 managed-marker sections (`[project]` /
  `[archive]` / `[vocabulary]`). The operator's explicit
  signal "use migrate to triage / re-migrate this managed
  tree but skip the listed paths".
- **`_SKILL_RELATIVE_FILES` extended** to include
  `use-cases.md` (a pre-existing bundle file `install-skill
  --copy` previously missed because it walked the bundle
  via this very tuple) plus the two M8 new references.

### Notes

- M6 + M7 + M8 are batched into a single PyPI publish event
  in M9 (per operator OQ-C). The on-disk Markdown
  convention is otherwise stable; the M7 `Lifecycle:`
  rename is a one-time keyword change with no backward-
  compat alias.
- `MigrationPlan` grows three optional human-output-only
  fields (`excluded_count`, `excluded_breakdown`,
  `suppressed_exts`) per OQ1 — OMITTED from
  `migration_to_json` so the JSON schema stays flat,
  mirroring the M7 `multi_project_hints` precedent.

## 1.2.0 — 2026-05-25

The first breaking convention-schema release. Renames the
controlled-vocab lifecycle key from `Status:` to `Lifecycle:`;
broadens role inference; normalises project names and archive
moves. Per the post-M8 batched publish (M9), 1.2.0 ships
locally only — the public PyPI release is 1.3.0, batching the
M6 + M7 + M8 surface together.

### Changed (breaking)

- **Controlled-vocab field rename (M7 — F0).** `Status:` →
  `Lifecycle:` in the metadata block. A pre-existing
  `Status:` line is now a free-form extra field, preserved
  through `docs migrate` into the `## Migrated metadata` body
  section as `Migrated-Status:`. The `[vocabulary] add_statuses`
  config key is renamed `add_lifecycles`. `docs list --status`
  is renamed `docs list --lifecycle`. The `--json` schema field
  `status` is renamed `lifecycle` in both `docs list` and
  `docs migrate`. No backward-compat alias.

### Added

- **Medium confidence (M7 — OQ-D).**
  `FileMigration.confidence` adds a third value `"medium"`
  between `"high"` and `"low"`. Derived inference signals
  (H1 content, section-header patterns, sibling-set
  defaulting, non-role-suffix stripping, the `_M\d+`
  milestone-number pattern) return medium. `docs check`
  treats medium-confidence inferences as warnings (exit 1),
  not errors. New `docs check` rule key
  `medium-confidence-inference`.
- **Role vocab additions (M7 — F10 / OQ-A).** 7 new core
  roles: `implementation`, `sketch`, `outline`, `memo`,
  `brief`, `template`, `example`. The INDEX renderer
  positions them between `idea` and `notes`.
- **Project-name normalisation (M7 — F11).** `docs migrate`
  now normalises inferred project values to lowercase-kebab
  (TitleCase / SNAKE_UPPER / letter-to-digit / mixed
  underscore all rejoin with `-`); digit-after-digit is
  preserved so `bugs-2026-01-26` survives intact. The
  original is surfaced inline as `project: foo-bar-baz
  (normalised from "FooBarBaz")` once at the top of the
  human plan when normalisation changed the value.
- **Per-file archive-move dates (M7 — F4).** `docs migrate`
  proposes archive normalisations using each file's
  `Updated:` (or mtime fall-back) per file instead of a
  single migration-run default. `--date` continues to
  override globally.
- **Multi-project hints (M7 — F5).** `docs migrate` surfaces
  a `hint: …` line in the plan footer when an immediate
  subdir's longest-common filename prefix differs from the
  parent project and the subdir holds ≥ 5 `.md` files.
- **`--config-project NAME` (M7 — F5).** New CLI flag on
  `docs migrate`; overrides the inferred project for the
  run, bypasses normalisation, suppresses hint emission. The
  persistent equivalent is `[migrate] project_name = "…"` in
  `.docs.toml`.
- **`[migrate] role_suffixes` (M7 — F1).** New `.docs.toml`
  map letting an operator teach `docs migrate` a custom
  per-tree suffix → role mapping (extends the built-in map).
- **Broadened role inference (M7 — F1 / F10 / F12).**
  `infer_role` now tokenises on case-transition boundaries
  (`MyPlan` → suffix `plan`), recognises a trailing
  `_M\d+` pattern as `milestone` (medium), strips
  `_v\d+`/`_Draft`/`_Ready` non-role suffixes and re-tries
  (medium), and at the plan layer infers from H1
  trailing-word, section-header patterns, and sibling-set
  defaulting at ≥ 60% / ≥ 5 (medium).

### Notes

- The 2026-05-24 multi-tree trial (501 .md files across
  25 trees) measured 25.3% high-confidence under the M4
  inference. M7's broadened inference brings the sanitised
  `snake-medium` fixture to ~88% high+medium.
- `docs migrate` now narrows the refusal of a `.docs.toml`
  to managed-root markers (`[project]`, `[archive]`,
  `[vocabulary]`). A `.docs.toml` containing only a
  `[migrate]` section (e.g. `project_name = "foo"`) is read
  without refusing — the foreign-tree migration-sidecar
  shape.

## 1.1.0 — UNRELEASED

The first PyPI release. Distribution name is `docs-cli`; the console-script
remains `docs`. No on-disk-convention changes.

### Added

- **PyPI distribution.** The CLI now ships as `docs-cli` on PyPI:
  `pip install docs-cli` lands `docs` on PATH via the
  `[project.scripts] docs = "docs_cli.cli:main"` entry point. The
  bundled Claude Code skill rides inside the wheel as package data
  under `docs_cli/skill/`, removing the previous requirement to clone
  the repo to use the skill.
- **`docs install-skill` verb (M6).** New subcommand that materialises
  the bundled skill onto a host. Flags: `--dest DIR` (default
  `~/.claude/skills/docs/`), `--copy` (default) / `--symlink`,
  `--force`, `--quiet`. Idempotent: a no-op when the destination is
  already byte-identical to the bundled source. Refuses `--symlink`
  on a wheel install (where the bundled skill lives under
  `site-packages` and could be replaced by a `pip install --upgrade`).
- **Global `--version` flag.** `docs --version` prints `docs 1.1.0`
  and exits 0.

### Changed

- **Package layout.** The single-file CLI moved from `bin/docs` to
  `src/docs_cli/cli.py`. The bundled skill moved from `skills/docs/`
  to `src/docs_cli/skill/`. Tests import the CLI via
  `from docs_cli import cli` (or `from docs import …` via the
  conftest's `sys.modules` alias).
- **Repository identity.** The local checkout and the GitHub repo
  both moved to `docs-cli` (was `docs`); the on-disk Markdown
  convention is unchanged (`Project: docs` stays `docs`).
- **Build backend.** `pyproject.toml` declares hatchling as the build
  backend; classifiers bumped from Alpha to Beta and now list Python
  3.11 / 3.12 / 3.13.

### Removed

- `bin/docs` — replaced by the editable-install / wheel entry point.
- Top-level `skills/docs/` — replaced by `src/docs_cli/skill/` (the
  in-tree source of truth shipped as wheel package data).
- `[tool.ruff] extend-include = ["bin/docs"]` and
  `[tool.mypy] scripts_are_modules = true` — no longer needed; the
  CLI is a regular package module.

## 1.0.0 — 2026-05-22

v1 complete: M1-M5 shipped across 2026-05-20 → 2026-05-22.

### Added

- M1 — Parser, walker, INDEX renderer, `docs index`, config loading.
- M2 — Mutating verbs `new`, `archive`, `mv`, `touch`.
- M3 — Validation (`check`) and query (`list`); INDEX regrouped by
  Project then Role.
- M4 — Migration helper `docs migrate` for adopting foreign Markdown
  trees into the convention (dry-run by default).
- M5 — Claude Code skill that drives the verbs automatically when an
  agent does documentation work in a `docs`-managed tree; bundled
  spec references (`convention.md`, `cli.md`) ship alongside.
