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

- Plain `Label: value` lines under the H1; a bare-label list group (like `Related:`) may follow after a blank line.
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
docs migrate <dir> [--apply]              Adopt a foreign Markdown directory into the convention (dry-run by default).
```

See [`docs/cli.md`](docs/cli.md) for full surface and exit codes.

## Install

```sh
git clone https://github.com/<you>/docs.git ~/opt/docs
ln -s ~/opt/docs/bin/docs ~/bin/docs                 # CLI on $PATH
ln -s ~/opt/docs/skills/docs ~/.claude/skills/docs   # Claude Code skill (optional)
```

Requires Python 3.11+ (for stdlib `tomllib`). No third-party dependencies.

## Status

**v1 complete.** All five milestones shipped 2026-05-20 through 2026-05-22:

- M1 — Parser and `docs index`
- M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`)
- M3 — Validation and query (`check`, `list`)
- M4 — Migration helper (`docs migrate`)
- M5 — Claude Code skill at [`skills/docs/`](skills/docs/) — drives the verbs above automatically when an agent does documentation work in a `docs`-managed tree, with self-contained convention and CLI references bundled at `skills/docs/references/`.

See [`docs/status.md`](docs/status.md) for per-milestone summaries and [`docs/plan.md`](docs/plan.md) for the v1.1 backlog.

## License

MIT — see [LICENSE](LICENSE).
