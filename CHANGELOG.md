# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.2.0 — UNRELEASED

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
