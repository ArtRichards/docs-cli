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
docs check [DIR] [--exclude PATTERN]      Validate metadata, refs, status/location drift, body links.
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

Released on PyPI — `pip install docs-cli`. The on-disk Markdown convention is stable; the only breaking keyword change to date is the one-time `Status:` → `Lifecycle:` rename (no backward-compat alias).

For current state, see the canonical sources — kept in sync by the tooling rather than duplicated here:

- [CHANGELOG](https://github.com/ArtRichards/docs-cli/blob/main/CHANGELOG.md) — the current version and full release history.
- [`docs/status.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/status.md) — development progress.
- [`docs/plan.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/plan.md) — the roadmap.

## License

MIT — see [LICENSE](https://github.com/ArtRichards/docs-cli/blob/main/LICENSE).
