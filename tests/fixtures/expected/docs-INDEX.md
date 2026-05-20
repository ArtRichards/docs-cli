# docs — Documentation

This directory is the docs root for the `docs` CLI itself. We eat our own dog food: once the tool is built, running `docs index` here should reproduce the auto-generated section below.

The hand-written preamble (this paragraph, and anything outside the marker block) is preserved by the tool. Only content between `<!-- docs:generated start -->` and `<!-- docs:generated end -->` is rewritten.

<!-- docs:generated start -->
_Generated 2026-05-20. 12 docs active, 0 archived._

## Active — Status

- [status.md](status.md) — _status_ — Single source of truth for milestone and phase. Currently M1 active, Phase 1 (Define Contract) not yet started. Updated 2026-05-20.

## Active — Charter

- [charter.md](charter.md) — _charter_ — What we're building, why, success criteria, non-goals, audience. Updated 2026-05-20.

## Active — Plan

- [plan.md](plan.md) — _plan_ — Five-milestone roadmap: M1 parser+index, M2 mutating verbs, M3 validation+query, M4 migration helper, M5 Claude Code skill. Updated 2026-05-20.

## Active — Milestone

- [m1-parser-and-index.md](m1-parser-and-index.md) — _milestone_ — M1 task plan: parser, walker, `docs index` subcommand. Ten TDD phases mapped to concrete deliverables. Updated 2026-05-20.

## Active — Log

- [m1-parser-and-index-log.md](m1-parser-and-index-log.md) — _log_ — M1 implementation log. Phase progress table and per-phase entries appended as work proceeds. Updated 2026-05-20.

## Active — Spec

- [convention.md](convention.md) — _spec_ — The on-disk Markdown convention `docs` reads and writes: metadata block shape, vocabularies, relationship verbs, archive subtree rules, INDEX format. Updated 2026-05-20.
- [cli.md](cli.md) — _spec_ — The `docs` command-line surface: subcommands, flags, output formats, exit codes. Updated 2026-05-20.

## Active — Reference

- [architecture.md](architecture.md) — _reference_ — Module sketch for the single-file CLI; data flow for `docs index`; atomic-write pattern; dependencies. Updated 2026-05-20.
- [test-strategy.md](test-strategy.md) — _reference_ — Test layers, fixture sources, critical paths, quality gates, data plan. Updated 2026-05-20.
- [definition-of-ready.md](definition-of-ready.md) — _reference_ — Gate checklist verifying foundations are green. Go/no-go recorded 2026-05-20. Currently GO. Updated 2026-05-20.

## Active — Decision

- [vocab-adr.md](vocab-adr.md) — _decision_ — Status (6 values) and Role (13 values) vocabularies; rationale, alternatives, extension rules. Updated 2026-05-20.
- [dual-status-adr.md](dual-status-adr.md) — _decision_ — Why doc lifecycle is expressed both in path location and in-doc `Status:` field, with the tool maintaining consistency. Updated 2026-05-20.

## Archived

_None._

<!-- docs:generated end -->
