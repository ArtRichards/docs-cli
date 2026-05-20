# docs

A prescriptive, lightweight CLI for managing trees of structured markdown documentation.

Treats each Markdown file as a small, self-describing record. A short metadata block under the H1 captures the doc's status, role, and relationships; the `docs` CLI uses that metadata to derive an index, archive completed work, validate consistency, and answer queries — without forcing you to maintain cross-references by hand.

## Why

Documentation directories rot. Hand-maintained `INDEX.md` files drift from reality. Descriptions get duplicated and lose sync. Plans pile up alongside completed work with no clear lifecycle.

`docs` makes each file self-describing and treats the index as a derived view. The doc itself is the source of truth; the index is generated.

## Convention at a glance

```markdown
# Title

Status: active
Role: spec
Project: docs
Updated: 2026-05-20

Related:
- pairs-with: convention.md
- implements: charter.md

## …
```

- Plain `Label: value` lines under the H1, ending at the first blank line.
- `Status` and `Role` come from controlled vocabularies (extensible per-project, additive only).
- `Related:` is followed by bullets in `<verb>: <path>` form.
- No YAML frontmatter, no parser dependency, readable in any Markdown viewer.

See [`docs/convention.md`](docs/convention.md) for the full spec.

## Commands

```
docs new <role> <slug> [--project NAME]   Scaffold a doc with the right metadata.
docs index [DIR]                          Regenerate INDEX.md from metadata in DIR.
docs archive <file> [--reason "…"]        Archive: edit Status, move to archive/<date>/, refresh index.
docs mv <old> <new>                       Move + rewrite Related: references across the tree.
docs list [filters] [--json]              Query view of the tree.
docs check [DIR]                          Validate metadata, refs, status/location drift.
docs touch <file>                         Bump Updated: to today.
```

See [`docs/cli.md`](docs/cli.md) for full surface and exit codes.

## Install

```sh
git clone https://github.com/<you>/docs.git ~/opt/docs
ln -s ~/opt/docs/docs.py ~/bin/docs   # or wherever your $PATH wants it
```

Requires Python 3.11+ (for stdlib `tomllib`). No third-party dependencies.

## Status

Pre-implementation. The convention and CLI surface are designed; the binary is being built. See [`docs/plan.md`](docs/plan.md) for milestones.

## License

MIT — see [LICENSE](LICENSE).
