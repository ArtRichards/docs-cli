# docs — Documentation

This directory is the docs root for the `docs` CLI itself. We eat our own dog food: once the tool is built, running `docs index` here should reproduce the auto-generated section below.

The hand-written preamble (this paragraph, and anything outside the marker block) is preserved by the tool. Only content between `<!-- docs:generated start -->` and `<!-- docs:generated end -->` is rewritten.

<!-- docs:generated start -->
_Generated 2026-05-20. 12 docs active, 0 archived._

## Active — Status

- [status.md](status.md) — _status_ — **This is the single source of truth for project progress. Update only this file when milestones complete or phases…. Updated 2026-05-20.

## Active — Charter

- [charter.md](charter.md) — _charter_ — A small, opinionated CLI (`docs`) that manages a tree of Markdown documentation by treating each file as a…. Updated 2026-05-20.

## Active — Plan

- [plan.md](plan.md) — _plan_ — Three milestones to v1, then a migration helper, then a Claude Code skill wrapper.. Updated 2026-05-20.

## Active — Spec

- [cli.md](cli.md) — _spec_ — This spec defines the `docs` command-line surface: subcommands, flags, output formats, and exit codes. The on-disk…. Updated 2026-05-20.
- [convention.md](convention.md) — _spec_ — This spec defines the on-disk convention that `docs` reads and writes. It is the portable, tool-independent part: any…. Updated 2026-05-20.

## Active — Milestone

- [m1-parser-and-index.md](m1-parser-and-index.md) — _milestone_ — - Milestone: M1 - Title: Parser and `docs index` - Surface: Python module `docs`, CLI subcommand `docs index` - Status:…. Updated 2026-05-20.

## Active — Log

- [m1-parser-and-index-log.md](m1-parser-and-index-log.md) — _log_ — - Project: docs - Milestone: M1 — Parser and `docs index` - Started: 2026-05-20 - Progress: Phase 1 (Define Contract) —…. Updated 2026-05-20.

## Active — Decision

- [dual-status-adr.md](dual-status-adr.md) — _decision_ — A doc's lifecycle state could be expressed by:. Updated 2026-05-20.
- [vocab-adr.md](vocab-adr.md) — _decision_ — The convention requires controlled vocabularies for `Status` and `Role`. Too small a set fails to express common…. Updated 2026-05-20.

## Active — Reference

- [architecture.md](architecture.md) — _reference_ — Single Python file at `bin/docs`, executable, shebanged. (Not at repo root — the `docs/` documentation directory…. Updated 2026-05-20.
- [definition-of-ready.md](definition-of-ready.md) — _reference_ — Gate-check before implementation begins. Implementation does not start until every item is green.. Updated 2026-05-20.
- [test-strategy.md](test-strategy.md) — _reference_ — | Layer | Tool | Scope | |---|---|---| | Unit | pytest | Parser, walker, render, vocab loading. Pure-function focus. |…. Updated 2026-05-20.

## Archived

_None._
<!-- docs:generated end -->
