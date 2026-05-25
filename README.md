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
- `Status` and `Role` come from controlled vocabularies (extensible per-project, additive only).
- `Related:` is followed by bullets in `<verb>: <path>` form.
- No YAML frontmatter, no parser dependency, readable in any Markdown viewer.

See [`docs/convention.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/convention.md) for the full spec.

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
docs install-skill [--dest DIR]           Materialise the bundled Claude Code skill onto this host.
```

See [`docs/cli.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/cli.md) for full surface and exit codes.

## Install

```sh
pip install docs-cli                      # lands `docs` on PATH
docs install-skill                        # materialise the bundled Claude Code skill at ~/.claude/skills/docs/
```

Requires Python 3.11+ (for stdlib `tomllib`). No third-party runtime dependencies.

For development:

```sh
git clone https://github.com/ArtRichards/docs-cli.git ~/opt/docs-cli
cd ~/opt/docs-cli
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest -q
```

## Status

**v1 complete; v1.1 in flight (M6 — PyPI distribution).** Milestone history:

- M1 — Parser and `docs index` (shipped 2026-05-20)
- M2 — Mutating verbs `new`, `archive`, `mv`, `touch` (shipped 2026-05-21)
- M3 — Validation and query `check`, `list` (shipped 2026-05-22)
- M4 — Migration helper `docs migrate` (shipped 2026-05-22)
- M5 — Claude Code skill — drives the verbs automatically when an agent does documentation work in a `docs`-managed tree, with self-contained convention and CLI references bundled alongside (shipped 2026-05-22)
- M6 — PyPI distribution as `docs-cli`; relocates the CLI to a proper package at `src/docs_cli/`, ships the skill inside the wheel as package data, and adds `docs install-skill` for one-shot host materialisation (in flight 2026-05-23)

**v1.1 release notes.** v1.1.0 is the first PyPI release: same eight v1 verbs, plus the new `install-skill` verb, plus packaging surface. The on-disk Markdown convention is unchanged; only the distribution name (`docs-cli`) and the install path (`pip install`) differ.

See [`docs/status.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/status.md) for per-milestone summaries and [`docs/plan.md`](https://github.com/ArtRichards/docs-cli/blob/main/docs/plan.md) for the v1.1 backlog. The [CHANGELOG](https://github.com/ArtRichards/docs-cli/blob/main/CHANGELOG.md) tracks every release.

## License

MIT — see [LICENSE](https://github.com/ArtRichards/docs-cli/blob/main/LICENSE).
