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
docs archive <file> [--reason "…"] [--cascade-only GLOB] [--cascade-dry-run] [--json]
                                          Archive: edit Lifecycle, record Archived:, move to archive/<date>/,
                                          rebase stale body links, refresh index. Related docs need an explicit scope.
docs mv <old> <new> [--dry-run] [--json]  Move + rewrite Related: references AND stale body links across the tree.
docs relate add|remove SOURCE VERB TARGET Add or remove a reciprocal relationship pair across both endpoints.
docs list [filters] [--json] [--exclude PATTERN]
                                          Query view of the tree.
docs check [DIR] [--exclude PATTERN]      Validate metadata, refs, status/location drift, reciprocal edges,
                                          body links, and archive-date drift.
docs touch <file> [--check]               Bump Updated: to today; --check re-validates the tree afterwards.
docs stamp <file>                         Stamp a metadata block onto a file that was written by hand.
docs project rename <old> <new>           Rename a project across the tree.
docs project set <file> <name>            Reassign a single doc to another project.
docs migrate <dir> [--apply] [--summary] [--only ambiguous] [--exclude PATTERN]
                                          Adopt a foreign Markdown directory into the convention (dry-run by default).
docs install-skill [--dest DIR]           Materialise the bundled agent skill onto this host.
```

See [`docs/cli.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/cli.md) for full surface and exit codes.

## What 2.0 enforces

The 2.0 train turned four classes of silent documentation rot into hard errors,
and stopped the tool from causing two of them itself:

- **Reciprocal edges.** `precedes`/`follows`, `depends-on`/`required-by` and
  `blocks`/`blocked-by` must point both ways. A one-sided edge is a
  `missing-inverse` error; `docs relate add|remove` writes or removes both ends
  in one call.
- **Body links.** Local Markdown links in prose are validated. A destination
  that does not exist is `broken-body-link`; one that escapes the tree is
  `outside-root-body-link`.
- **Move-safe rewrites.** `docs mv` and `docs archive` rebase the body-link
  destinations a move makes stale — not just `Related:` references — so an
  archive or rename no longer leaves a tree that fails `docs check`. Both verbs
  build and validate the whole plan before the first byte moves.
- **Archive dates.** `docs archive` records an `Archived:` field on every
  document it moves, and `docs check` reports `archive-date-drift` when a
  document's recorded date disagrees with the dated directory it sits in.
  `docs mv` refuses a move between two different dated archive directories.
- **Explicit archive scope.** Bare `--cascade` is retired: it refuses and writes
  nothing. Use `--cascade-dry-run` to preview, then `--cascade-only GLOB` to
  write an explicit scope.

Upgrading a 1.x tree surfaces pre-existing damage as errors on the first
`docs check`. That is intentional, and the
[CHANGELOG](https://github.com/ArtRichards/docs-cli/blob/main/CHANGELOG.md)'s
*Upgrading from 1.x* section carries the repair recipe for each rule.

## Install

```sh
pip install docs-cli                      # lands `docs` on PATH
docs install-skill [--dest DIR]           # materialise the bundled agent skill (default: ~/.claude/skills/docs/)
```

Requires Python 3.11+ (for stdlib `tomllib`). No third-party runtime dependencies.

## Adopting an existing tree

Have a directory of foreign Markdown specs? `docs install-skill` materialises an agent skill that walks an agent through `docs migrate <dir>` → triage → `docs migrate --apply`. See [`docs/archive/2026-05-25/m8-adoption-workflow.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/archive/2026-05-25/m8-adoption-workflow.md) for the full agent-driveable workflow, the bundled [adoption playbook](https://github.com/ArtRichards/docs-cli/blob/main/src/docs_cli/skill/references/adoption-playbook.md) for the procedural deep-dive, or run `docs migrate <dir>` directly for a dry-run plan.

For development:

```sh
git clone https://github.com/ArtRichards/docs-cli.git ~/opt/docs-cli
cd ~/opt/docs-cli
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest -q
```

## Status

Released on PyPI — `pip install docs-cli`. The on-disk Markdown convention is stable and backward-compatible: 2.0 **adds** the `Archived:` field but never rewrites existing files on upgrade, and the only breaking keyword change to date remains the one-time `Status:` → `Lifecycle:` rename (no backward-compat alias). What 2.0 breaks is *automation*, not *data* — new hard `docs check` rules and the retired bare `--cascade`.

For current state, see the canonical sources — kept in sync by the tooling rather than duplicated here:

- [CHANGELOG](https://github.com/ArtRichards/docs-cli/blob/main/CHANGELOG.md) — the current version and full release history.
- [`docs/status.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/status.md) — development progress.
- [`docs/plan.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/plan.md) — the roadmap.

## License

MIT — see [LICENSE](https://github.com/ArtRichards/docs-cli/blob/main/LICENSE).
