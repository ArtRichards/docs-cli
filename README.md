# docs-cli

A prescriptive, lightweight CLI (`docs`) for managing trees of structured markdown documentation.

Treats each Markdown file as a small, self-describing record. A short metadata block under the H1 captures the doc's status, role, and relationships; the `docs` CLI uses that metadata to derive an index, archive completed work, validate consistency, and answer queries — without forcing you to maintain cross-references by hand.

## Why

Documentation directories rot. Hand-maintained `INDEX.md` files drift from reality. Descriptions get duplicated and lose sync. Plans pile up alongside completed work with no clear lifecycle.

`docs` makes each file self-describing and treats the index as a derived view. The doc itself is the source of truth; the index is generated.

## Convention at a glance

```markdown
# Title

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-05-23

Related:
- pairs-with: convention.md
- implements: charter.md

## …
```

- Plain `Label: value` lines under the H1; a bare-label list group (like `Related:`) may follow after a blank line.
- `Lifecycle` and `Role` come from controlled vocabularies (extensible per-project, additive only).
- `Related:` is followed by bullets in `<verb>: <path>` form.
- No YAML frontmatter, no parser dependency, readable in any Markdown viewer.

See [`docs/convention.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/convention.md) for the full spec.

## Commands

```
docs new <role> <slug> [--project NAME] [--body-from PATH|-]
                                          Scaffold a doc with the right metadata; --body-from writes the body atomically.
docs index [DIR] [--exclude PATTERN]      Regenerate INDEX.md from metadata in DIR.
docs archive <file> [--reason "…"]        Archive: edit Lifecycle, move to archive/<date>/, refresh index.
docs mv <old> <new>                       Move + rewrite Related: references across the tree.
docs list [filters] [--json] [--exclude PATTERN]
                                          Query view of the tree.
docs check [DIR] [--exclude PATTERN]      Validate metadata, refs, status/location drift.
docs touch <file>                         Bump Updated: to today.
docs migrate <dir> [--apply] [--summary] [--only ambiguous] [--exclude PATTERN]
                                          Adopt a foreign Markdown directory into the convention (dry-run by default).
docs install-skill [--dest DIR]           Materialise the bundled Claude Code skill onto this host.
```

See [`docs/cli.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/cli.md) for full surface and exit codes.

## Install

```sh
pip install docs-cli                      # lands `docs` on PATH
docs install-skill                        # materialise the bundled Claude Code skill at ~/.claude/skills/docs/
```

Requires Python 3.11+ (for stdlib `tomllib`). No third-party runtime dependencies.

## Adopting an existing tree

Have a directory of foreign Markdown specs? `docs install-skill` materialises a Claude Code skill that walks an agent through `docs migrate <dir>` → triage → `docs migrate --apply`. See [`docs/m8-adoption-workflow.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/m8-adoption-workflow.md) for the full agent-driveable workflow, the bundled [adoption playbook](https://github.com/ArtRichards/docs-cli/blob/main/src/docs_cli/skill/references/adoption-playbook.md) for the procedural deep-dive, or run `docs migrate <dir>` directly for a dry-run plan.

For development:

```sh
git clone https://github.com/ArtRichards/docs-cli.git ~/opt/docs-cli
cd ~/opt/docs-cli
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest -q
```

## Status

**v1 complete; M8 shipped locally as 1.3.0 (publish DEFERRED to M9 batched 1.3.0).** Milestone history:

- M1 — Parser and `docs index` (shipped 2026-05-20)
- M2 — Mutating verbs `new`, `archive`, `mv`, `touch` (shipped 2026-05-21)
- M3 — Validation and query `check`, `list` (shipped 2026-05-22)
- M4 — Migration helper `docs migrate` (shipped 2026-05-22)
- M5 — Claude Code skill — drives the verbs automatically when an agent does documentation work in a `docs`-managed tree, with self-contained convention and CLI references bundled alongside (shipped 2026-05-22)
- M6 — PyPI distribution preparation as `docs-cli`; relocates the CLI to a proper package at `src/docs_cli/`, ships the skill inside the wheel as package data, and adds `docs install-skill` for one-shot host materialisation (closed 2026-05-24 as preparation-only — no publish)
- M7 — Migration accuracy: `Status:` → `Lifecycle:` controlled-vocab rename, broadened role inference (H1 / section-header / sibling-set / word-boundary / `_M\d+` / non-role-suffix strip), `medium` confidence level, project-name normalisation, per-file mtime archive dates, multi-project hints, `--config-project` override, `[migrate]`-only sidecar (closed 2026-05-25 as 1.2.0 locally; publish DEFERRED to M9)
- M8 — Adoption workflow agent-driveable: tree-wide `--exclude` + `[exclude]` + `.docsignore`; migrate triage flags (`--summary`, `--only ambiguous`, `--group-by`); default plan footer summary; non-md sibling surfacing; `docs new --body-from` for one-call atomic doc authoring; substantial skill-reference rewrite (adoption playbook + `.docs.toml` template) (closed 2026-05-25 as 1.3.0 locally; publish DEFERRED to M9)

**Publish strategy.** v1.1.0, v1.2.0, and v1.3.0 were never published to PyPI. M9 batches the post-M8 tree into the first PyPI release as 1.3.0 — one publish event covering M6 + M7 + M8 surface together (per operator OQ-C). The on-disk Markdown convention is otherwise stable; the M7 `Lifecycle:` rename is a one-time keyword change with no backward-compat alias.

See [`docs/status.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/status.md) for per-milestone summaries and [`docs/plan.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/plan.md) for the v1.x backlog. The [CHANGELOG](https://github.com/ArtRichards/docs-cli/blob/main/CHANGELOG.md) tracks every release.

## License

MIT — see [LICENSE](https://github.com/ArtRichards/docs-cli/blob/main/LICENSE).
