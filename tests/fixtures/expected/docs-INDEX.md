# docs — Documentation

This directory is the docs root for the `docs` CLI itself. We eat our own dog food: once the tool is built, running `docs index` here should reproduce the auto-generated section below.

The hand-written preamble (this paragraph, and anything outside the marker block) is preserved by the tool. Only content between `<!-- docs:generated start -->` and `<!-- docs:generated end -->` is rewritten.

<!-- docs:generated start -->
_Generated 2026-05-27. 30 docs active, 1 archived._

## Project — docs

### Active — Status

- [status.md](status.md) — _status_ — **This is the single source of truth for project progress. Update only this file when milestones complete or phases…. Updated 2026-05-27.

### Active — Charter

- [charter.md](charter.md) — _charter_ — A small, opinionated CLI (`docs`) that manages a tree of Markdown documentation by treating each file as a…. Updated 2026-05-24.

### Active — Plan

- [plan.md](plan.md) — _plan_ — Three milestones to v1, then a migration helper, then a Claude Code skill wrapper. v1.1 picks up with packaging, then…. Updated 2026-05-27.

### Active — Spec

- [cli.md](cli.md) — _spec_ — This spec defines the `docs` command-line surface: subcommands, flags, output formats, and exit codes. The on-disk…. Updated 2026-05-27.
- [convention.md](convention.md) — _spec_ — This spec defines the on-disk convention that `docs` reads and writes. It is the portable, tool-independent part: any…. Updated 2026-05-27.

### Active — Milestone

- [m7-migration-accuracy.md](m7-migration-accuracy.md) — _milestone_ — - Milestone: M7 (v1.1) - Title: Migration plan accuracy - Surface: extensions to `docs migrate`'s inference…. Updated 2026-05-25.
- [m8-adoption-workflow.md](m8-adoption-workflow.md) — _milestone_ — - Milestone: M8 (v1.1) - Title: Adoption workflow — agent-driveable - Surface: new CLI flags + verbs (`--exclude`,…. Updated 2026-05-25.
- [m9-pypi-publish.md](m9-pypi-publish.md) — _milestone_ — > **Stub-drafted 2026-05-24, post M6 scope reframe.** M9 enters > active state once M8 ships. The operative checklist…. Updated 2026-05-25.
- [m6-pypi-distribution.md](m6-pypi-distribution.md) — _milestone_ — > **Scope reframe 2026-05-24 (operator decision).** M6 is now > **preparation only** — the milestone delivered the…. Updated 2026-05-24.
- [m5-claude-code-skill.md](m5-claude-code-skill.md) — _milestone_ — - Milestone: M5 - Title: Claude Code skill - Surface: a Claude Code **skill** — a `SKILL.md` artifact (plus, if needed,…. Updated 2026-05-23.
- [m3-validation-and-query.md](m3-validation-and-query.md) — _milestone_ — - Milestone: M3 - Title: Validation and query (`check`, `list`) - Surface: two new read-only CLI subcommands on the…. Updated 2026-05-22.
- [m4-migration-helper.md](m4-migration-helper.md) — _milestone_ — - Milestone: M4 - Title: Migration helper (`docs migrate`) - Surface: one new CLI subcommand on the `docs` executable…. Updated 2026-05-22.
- [m2-mutating-verbs.md](m2-mutating-verbs.md) — _milestone_ — - Milestone: M2 - Title: Mutating verbs (`new`, `archive`, `mv`, `touch`) - Surface: four new CLI subcommands on the…. Updated 2026-05-21.
- [m1-parser-and-index.md](m1-parser-and-index.md) — _milestone_ — - Milestone: M1 - Title: Parser and `docs index` - Surface: Python module `docs`, CLI subcommand `docs index` - Status:…. Updated 2026-05-20.

### Active — Log

- [m10-adoption-polish-impl.md](m10-adoption-polish-impl.md) — _log_ — Chronological log of work on M10 — Adoption-flow polish + 1.3.0 carry-overs. Append a section per phase with objective,…. Updated 2026-05-27.
- [m7-migration-accuracy-log.md](m7-migration-accuracy-log.md) — _log_ — - Project: docs - Milestone: M7 — Migration plan accuracy - Started: 2026-05-24 - Progress: **Phase 1 complete; Phase 2…. Updated 2026-05-25.
- [m8-adoption-workflow-log.md](m8-adoption-workflow-log.md) — _log_ — - Project: docs - Milestone: M8 — Adoption workflow (agent-driveable) - Started: 2026-05-24 - Progress: **All 10 TDD…. Updated 2026-05-25.
- [m9-pypi-publish-log.md](m9-pypi-publish-log.md) — _log_ — Per-phase log for M9. Entries appended as the operator walked [release-runbook.md](release-runbook.md) post-M8.. Updated 2026-05-25.
- [m5-claude-code-skill-log.md](m5-claude-code-skill-log.md) — _log_ — - Project: docs - Milestone: M5 — Claude Code skill - Started: 2026-05-22 - Progress: **M5 complete — shipped…. Updated 2026-05-23.
- [m6-pypi-distribution-log.md](m6-pypi-distribution-log.md) — _log_ — - Project: docs - Milestone: M6 — PyPI distribution as `docs-cli` - Started: 2026-05-23 - Progress: **Milestone-setup…. Updated 2026-05-23.
- [m3-validation-and-query-log.md](m3-validation-and-query-log.md) — _log_ — - Project: docs - Milestone: M3 — Validation and query (`check`, `list`) - Started: 2026-05-22 - Progress: Complete —…. Updated 2026-05-22.
- [m4-migration-helper-log.md](m4-migration-helper-log.md) — _log_ — - Project: docs - Milestone: M4 — Migration helper (`docs migrate`) - Started: 2026-05-22 - Completed: 2026-05-22 -…. Updated 2026-05-22.
- [m2-mutating-verbs-log.md](m2-mutating-verbs-log.md) — _log_ — - Project: docs - Milestone: M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) - Started: 2026-05-21 - Progress:…. Updated 2026-05-21.
- [m1-parser-and-index-log.md](m1-parser-and-index-log.md) — _log_ — - Project: docs - Milestone: M1 — Parser and `docs index` - Started: 2026-05-20 - Shipped: 2026-05-20 - Progress: Phase…. Updated 2026-05-20.

### Active — Decision

- [dual-status-adr.md](dual-status-adr.md) — _decision_ — A doc's lifecycle state could be expressed by:. Updated 2026-05-20.
- [vocab-adr.md](vocab-adr.md) — _decision_ — The convention requires controlled vocabularies for `Status` and `Role`. Too small a set fails to express common…. Updated 2026-05-20.

### Active — Runbook

- [release-runbook.md](release-runbook.md) — _runbook_ — The operator-driven checklist for shipping `docs-cli` to PyPI. This runbook drove **M9 — `docs-cli==1.3.0`** (shipped…. Updated 2026-05-25.

### Active — Reference

- [architecture.md](architecture.md) — _reference_ — Single Python module at `src/docs_cli/cli.py`, exposed as the `docs` console-script via the `docs_cli.cli:main` entry…. Updated 2026-05-27.
- [definition-of-ready.md](definition-of-ready.md) — _reference_ — Gate-check before implementation begins. Implementation does not start until every item is green.. Updated 2026-05-22.
- [test-strategy.md](test-strategy.md) — _reference_ — | Layer | Tool | Scope | |---|---|---| | Unit | pytest | Parser, walker, render, vocab loading. Pure-function focus. |…. Updated 2026-05-20.

## Archived

- [archive/2026-05-27/m10-adoption-polish.md](archive/2026-05-27/m10-adoption-polish.md) — _milestone_ — - Milestone: M10 (v1.4.0) - Title: Adoption-flow polish + 1.3.0 carry-overs - Surface: two new CLI features (`docs…. Updated 2026-05-27.
<!-- docs:generated end -->
