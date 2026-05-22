# docs — Implementation Plan

Status: active
Role: plan
Project: docs
Updated: 2026-05-22

Related:
- implements: charter.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: status.md
- parent-of: m1-parser-and-index.md

## Sequencing

Three milestones to v1, then a migration helper, then a Claude Code skill wrapper.

```
M1 (parser + index)  →  M2 (mutating verbs)  →  M3 (validation + JSON)  →  M4 (migrate)  →  M5 (skill)
```

## M1 — Parser, walker, and `docs index`

Goal: read the convention reliably and produce a usable INDEX.md.

- Parse a single Markdown file into `{title, status, role, project, updated, related, extra_fields, body}`.
- Walk a docs root, skipping anything that isn't `.md` and isn't under a configured ignore pattern.
- Implement `docs index` with the marker-block strategy. Idempotent output.
- `.docs.toml` loading (TOML via stdlib `tomllib`, Python 3.11+).
- Smoke test against `~/opt/docs/docs/` itself — running `docs index` here should reproduce the hand-written INDEX.md byte-for-byte (or close enough that the diff is review-able).

Exit criteria: hand-written INDEX.md matches generated output on this repo. M1 unblocks every later milestone because they all need the parser.

## M2 — Mutating verbs: `new`, `archive`, `mv`, `touch`

Goal: stop hand-editing metadata.

- `docs new <role> <slug>` writes a scaffolded file with correct metadata block.
- `docs archive <file>` does the dual-status dance atomically (edit, move, reindex).
- `docs mv <old> <new>` rewrites `Related:` references across the tree.
- `docs touch <file>` bumps `Updated:`.
- Atomicity: tmp file + rename for every write; never leave a partially-edited doc.
- `--dry-run` works on all of these.

Exit criteria: archiving and renaming this repo's own docs through M2 produces correct, drift-free state.

## M3 — Validation and query: `check`, `list`

Goal: make the convention enforceable and queryable.

- `docs check` reports all violations defined in `cli.md`. Exit code semantics matter: 0/1/2 must be distinguishable so CI hooks can rely on them.
- `docs list` with all filters and JSON output. JSON schema documented in `cli.md` and stable from this point.
- Stale detection (`--stale N`).

Exit criteria: `docs check` on this repo's `docs/` returns exit 0. `docs list --json` output validates against the documented schema.

## M4 — Migration helper: `docs migrate <dir>`

Goal: import an existing non-conforming directory into the convention.

- Walks a foreign directory, inspects each `.md` file's structure.
- Infers `Role` from filename suffix patterns (`-spec`, `-status`, `-plan`, etc.) and from any existing metadata-shaped lines.
- Infers `Project` from common filename prefix.
- Inserts a metadata block under the H1 (or creates an H1 from the filename if missing).
- Detects existing archive-style subdirs (`archived/`, `project-history/`, `archive/YYYY-MM-DD/`) and normalizes them.
- Produces a dry-run report by default; `--apply` performs the edits.
- Intended to be agent-driven: the migration tool surfaces ambiguities, an LLM resolves them, the tool applies the decisions.

This is the verb that lets us point an agent at an existing doc tree (the validaitor specs, the risk-register dir, anyone's `docs/`) and bring it into the convention without manual labor.

Exit criteria: a dry-run against one of the example directories produces a complete migration plan with explicit decisions for every ambiguous case.

## M5 — Claude Code skill

Goal: agents use `docs` automatically when working in a docs root.

- SKILL.md at `~/.claude/skills/docs/` (or wherever the install convention lands).
- Triggers on: editing a `.md` file under a `.docs.toml`-marked root; user requests to "archive", "list docs", "create a plan/spec/charter"; before agent appends to a hand-curated INDEX.
- Skill body redirects to the appropriate `docs` verb instead of hand-editing.
- Documents the trigger conditions and the verbs without re-teaching the convention (that lives in `convention.md`).

Exit criteria: the agent stops hand-editing INDEX.md in this repo and uses `docs index`.

## Out of scope for v1

- Link-graph queries / `docs graph`.
- HTML or static-site rendering.
- Watch mode.
- Full-text search.
- Per-doc revisions / history (git owns this).
- Cross-root federation.

## Resolved questions

- **`docs archive --cascade` stays opt-in** (M2, 2026-05-21). Archiving a doc must not silently pull its neighbours along — cascading is a deliberate per-invocation choice. `--cascade` is a plain `store_true` flag; it prompts (`y/N`, defaulting to no) before archiving each one-hop `pairs-with` / `child-of` relation. No `--no-cascade` is needed.
- **INDEX carries a one-paragraph description per doc** (M1). The renderer emits title + description + Status + Updated; the description is the doc's first body paragraph, trimmed to ~120 characters.

## Open questions

- Should the INDEX be grouped by directory or `Project` instead of (or alongside) `Role`? M2's renderer fix made nested-doc links correct, but a large tree navigates better grouped by location. Deferred to M3 together with `docs list --project` — both are query/view concerns, not mutating-verb concerns.
- Should `docs check` validate **extra metadata fields**? The convention harvests every non-standard `Label: value` line into `Doc.extra` (`Owner:`, `Tags:`, `Archived-reason:`, …) but defines no notion of a *known* extra field, so `check` leaves them all unflagged (decided in M3, 2026-05-22 — `cli.md`'s earlier "unknown extra fields" warning was unimplementable as written and was removed). A future change could add an opt-in allowlist: a `[vocabulary] add_fields = [...]` key in `.docs.toml`, merged into a new `Config.fields` set exactly as `add_statuses` / `add_roles` already extend the vocabulary; `check_doc` would then emit an `unknown-field` **warning** (exit 1 — never an error) for any extra label outside that set. Scope is small — one rule in `check_doc`, one `Config` field, one `load_config` branch, one `cli.md` schema note — but it is not tied to a milestone. Revisit post-v1 if real trees accumulate typo'd field labels worth catching.
