# docs — Documentation

This directory is the docs root for the `docs` CLI itself. We eat our own dog food: once the tool is built, running `docs index` here should reproduce the auto-generated section below.

The hand-written preamble (this paragraph, and anything outside the marker block) is preserved by the tool. Only content between `<!-- docs:generated start -->` and `<!-- docs:generated end -->` is rewritten.

<!-- docs:generated start -->
_Generated 2026-08-16. 17 docs active, 57 archived._

## Project — docs

### Active — Status

- [status.md](status.md) — _status_ — **This is the single source of truth for project progress. Update only this file when milestones complete or phases…. Updated 2026-08-16.

### Active — Charter

- [charter.md](charter.md) — _charter_ — A small, opinionated CLI (`docs`) that manages a tree of Markdown documentation by treating each file as a…. Updated 2026-08-14.

### Active — Plan

- [plan.md](plan.md) — _plan_ — Three milestones to v1, then a migration helper, then a Claude Code skill wrapper. v1.1 picks up with packaging, then…. Updated 2026-08-16.

### Active — Spec

- [cli.md](cli.md) — _spec_ — This spec defines the `docs` command-line surface: subcommands, flags, output formats, and exit codes. The on-disk…. Updated 2026-08-16.
- [convention.md](convention.md) — _spec_ — This spec defines the on-disk convention that `docs` reads and writes. It is the portable, tool-independent part: any…. Updated 2026-08-16.

### Active — Log

- [feedback-log.md](feedback-log.md) — _log_ — This log records operator and downstream-consumer feedback that may become a future docs-cli milestone. Entries…. Updated 2026-08-16.
- [m29-pypi-publish-2-0-0-impl.md](m29-pypi-publish-2-0-0-impl.md) — _log_ — Chronological log of work on **M29 — PyPI publish 2.0.0**. Append a section per runbook phase (operator prep →…. Updated 2026-08-16.
- [m24-pypi-publish-impl.md](m24-pypi-publish-impl.md) — _log_ — Chronological log of work on **M24 — PyPI publish 1.8.0**. Append a section per runbook phase (operator prep →…. Updated 2026-07-03.
- [m20-pypi-publish-impl.md](m20-pypi-publish-impl.md) — _log_ — Chronological log of work on M20 — PyPI publish 1.6.5. Append a section per runbook phase (operator prep → pre-publish…. Updated 2026-06-12.
- [m17-pypi-publish-impl.md](m17-pypi-publish-impl.md) — _log_ — Chronological log of work on M17 — PyPI publish 1.6.0. Append a section per runbook phase (operator prep → pre-publish…. Updated 2026-06-03.

### Active — Decision

- [dual-status-adr.md](dual-status-adr.md) — _decision_ — A doc's lifecycle state could be expressed by:. Updated 2026-05-20.
- [vocab-adr.md](vocab-adr.md) — _decision_ — The convention requires controlled vocabularies for `Status` and `Role`. Too small a set fails to express common…. Updated 2026-05-20.

### Active — Runbook

- [release-runbook.md](release-runbook.md) — _runbook_ — The operator-driven checklist for shipping `docs-cli` to PyPI. This runbook drove **M9 — `docs-cli==1.3.0`** (shipped…. Updated 2026-08-16.

### Active — Reference

- [architecture.md](architecture.md) — _reference_ — Single Python module at `src/docs_cli/cli.py`, exposed as the `docs` console-script via the `docs_cli.cli:main` entry…. Updated 2026-08-16.
- [test-strategy.md](test-strategy.md) — _reference_ — | Layer | Tool | Scope | |---|---|---| | Unit | pytest | Parser, walker, render, vocab loading. Pure-function focus. |…. Updated 2026-08-16.
- [definition-of-ready.md](definition-of-ready.md) — _reference_ — Gate-check before implementation begins. Implementation does not start until every item is green.. Updated 2026-05-22.

## Project — ideas

### Active — Plan

- [agent-native-invocation.md](agent-native-invocation.md) — _plan_ — > **Source.** Prompted by ["I read the Claude Code source >…. Updated 2026-08-13.

## Archived

- [archive/2026-08-16/m25-reciprocal-relationship-integrity-impl.md](archive/2026-08-16/m25-reciprocal-relationship-integrity-impl.md) — _log_ — Chronological implementation log for M25 — Reciprocal relationship integrity and `docs relate`. Append one…. Updated 2026-08-16.
- [archive/2026-08-16/m25-reciprocal-relationship-integrity.md](archive/2026-08-16/m25-reciprocal-relationship-integrity.md) — _milestone_ — - Milestone: M25 (v2.0 train) - Title: Reciprocal relationship integrity and `docs relate` - Surface: define three…. Updated 2026-08-16.
- [archive/2026-08-16/m26-safe-archive-selection-impl.md](archive/2026-08-16/m26-safe-archive-selection-impl.md) — _log_ — Chronological implementation log for M26 — Safe explicit archive selection. Append one evidence-backed section per TDD…. Updated 2026-08-16.
- [archive/2026-08-16/m26-safe-archive-selection.md](archive/2026-08-16/m26-safe-archive-selection.md) — _milestone_ — - Milestone: M26 (v2.0 train) - Title: Safe explicit archive selection - Surface: decouple relationship context from…. Updated 2026-08-16.
- [archive/2026-08-16/m27-markdown-body-link-validation-impl.md](archive/2026-08-16/m27-markdown-body-link-validation-impl.md) — _log_ — Chronological implementation log for M27 — Markdown body-link validation. Append one evidence-backed section per TDD…. Updated 2026-08-16.
- [archive/2026-08-16/m27-markdown-body-link-validation.md](archive/2026-08-16/m27-markdown-body-link-validation.md) — _milestone_ — - Milestone: M27 (v2.0 train) - Title: Markdown body-link validation - Surface: parse a deliberately bounded set of…. Updated 2026-08-16.
- [archive/2026-08-16/m28-move-safe-body-link-rewrites-impl.md](archive/2026-08-16/m28-move-safe-body-link-rewrites-impl.md) — _log_ — Chronological implementation log for M28 — Move-safe Markdown body-link rewrites. Append one evidence-backed section…. Updated 2026-08-16.
- [archive/2026-08-16/m28-move-safe-body-link-rewrites.md](archive/2026-08-16/m28-move-safe-body-link-rewrites.md) — _milestone_ — - Milestone: M28 (v2.0 train) - Title: Move-safe Markdown body-link rewrites - Surface: extend `docs mv` and `docs…. Updated 2026-08-16.
- [archive/2026-08-16/m28a-archive-date-witness-impl.md](archive/2026-08-16/m28a-archive-date-witness-impl.md) — _log_ — Chronological implementation log for M28a — Structured archive-date witness. Append one evidence-backed section per TDD…. Updated 2026-08-16.
- [archive/2026-08-16/m28a-archive-date-witness.md](archive/2026-08-16/m28a-archive-date-witness.md) — _milestone_ — - Milestone: M28a (v2.0 train) - Title: Structured archive-date witness - Surface: **two legs.** `docs archive` records…. Updated 2026-08-16.
- [archive/2026-08-16/m29-pypi-publish-2-0-0.md](archive/2026-08-16/m29-pypi-publish-2-0-0.md) — _milestone_ — > **Activated 2026-08-16**, immediately after M28a merged to `main` > (merge commit `91cc839`). Every milestone M29…. Updated 2026-08-16.
- [archive/2026-05-20/m1-parser-and-index.md](archive/2026-05-20/m1-parser-and-index.md) — _milestone_ — - Milestone: M1 - Title: Parser and `docs index` - Surface: Python module `docs`, CLI subcommand `docs index` - Status:…. Updated 2026-08-14.
- [archive/2026-05-21/m2-mutating-verbs-log.md](archive/2026-05-21/m2-mutating-verbs-log.md) — _log_ — - Project: docs - Milestone: M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) - Started: 2026-05-21 - Progress:…. Updated 2026-08-14.
- [archive/2026-05-21/m2-mutating-verbs.md](archive/2026-05-21/m2-mutating-verbs.md) — _milestone_ — - Milestone: M2 - Title: Mutating verbs (`new`, `archive`, `mv`, `touch`) - Surface: four new CLI subcommands on the…. Updated 2026-08-14.
- [archive/2026-05-22/m3-validation-and-query-log.md](archive/2026-05-22/m3-validation-and-query-log.md) — _log_ — - Project: docs - Milestone: M3 — Validation and query (`check`, `list`) - Started: 2026-05-22 - Progress: Complete —…. Updated 2026-08-14.
- [archive/2026-05-22/m3-validation-and-query.md](archive/2026-05-22/m3-validation-and-query.md) — _milestone_ — - Milestone: M3 - Title: Validation and query (`check`, `list`) - Surface: two new read-only CLI subcommands on the…. Updated 2026-08-14.
- [archive/2026-05-22/m4-migration-helper-log.md](archive/2026-05-22/m4-migration-helper-log.md) — _log_ — - Project: docs - Milestone: M4 — Migration helper (`docs migrate`) - Started: 2026-05-22 - Completed: 2026-05-22 -…. Updated 2026-08-14.
- [archive/2026-05-22/m4-migration-helper.md](archive/2026-05-22/m4-migration-helper.md) — _milestone_ — - Milestone: M4 - Title: Migration helper (`docs migrate`) - Surface: one new CLI subcommand on the `docs` executable…. Updated 2026-08-14.
- [archive/2026-05-23/m5-claude-code-skill-log.md](archive/2026-05-23/m5-claude-code-skill-log.md) — _log_ — - Project: docs - Milestone: M5 — Claude Code skill - Started: 2026-05-22 - Progress: **M5 complete — shipped…. Updated 2026-08-14.
- [archive/2026-05-23/m5-claude-code-skill.md](archive/2026-05-23/m5-claude-code-skill.md) — _milestone_ — - Milestone: M5 - Title: Claude Code skill - Surface: a Claude Code **skill** — a `SKILL.md` artifact (plus, if needed,…. Updated 2026-08-14.
- [archive/2026-05-24/m6-pypi-distribution-log.md](archive/2026-05-24/m6-pypi-distribution-log.md) — _log_ — - Project: docs - Milestone: M6 — PyPI distribution as `docs-cli` - Started: 2026-05-23 - Progress: **Milestone-setup…. Updated 2026-08-14.
- [archive/2026-05-24/m6-pypi-distribution.md](archive/2026-05-24/m6-pypi-distribution.md) — _milestone_ — > **Scope reframe 2026-05-24 (operator decision).** M6 is now > **preparation only** — the milestone delivered the…. Updated 2026-08-14.
- [archive/2026-05-25/m7-migration-accuracy.md](archive/2026-05-25/m7-migration-accuracy.md) — _milestone_ — - Milestone: M7 (v1.1) - Title: Migration plan accuracy - Surface: extensions to `docs migrate`'s inference…. Updated 2026-08-14.
- [archive/2026-05-25/m8-adoption-workflow.md](archive/2026-05-25/m8-adoption-workflow.md) — _milestone_ — - Milestone: M8 (v1.1) - Title: Adoption workflow — agent-driveable - Surface: new CLI flags + verbs (`--exclude`,…. Updated 2026-08-14.
- [archive/2026-05-25/m9-pypi-publish-log.md](archive/2026-05-25/m9-pypi-publish-log.md) — _log_ — Per-phase log for M9. Entries appended as the operator walked [release-runbook.md](../../release-runbook.md) post-M8.. Updated 2026-08-14.
- [archive/2026-05-25/m9-pypi-publish.md](archive/2026-05-25/m9-pypi-publish.md) — _milestone_ — > **Stub-drafted 2026-05-24, post M6 scope reframe.** M9 enters > active state once M8 ships. The operative checklist…. Updated 2026-08-14.
- [archive/2026-05-27/m11-pypi-publish-impl.md](archive/2026-05-27/m11-pypi-publish-impl.md) — _log_ — Chronological log of work on M11 — PyPI publish `docs-cli` 1.4.0. Append a section per phase (Operator prep →…. Updated 2026-08-14.
- [archive/2026-05-27/m11-pypi-publish.md](archive/2026-05-27/m11-pypi-publish.md) — _milestone_ — > **Stub-drafted 2026-05-27, post M10 closeout.** M11 enters > active state immediately — the M10 wheel + sdist already…. Updated 2026-08-14.
- [archive/2026-05-28/m12-project-rename-impl.md](archive/2026-05-28/m12-project-rename-impl.md) — _log_ — Chronological log of work on M12 — Project rename verb + M11 wart fixes + version SoT (v1.5.0). Append a section per…. Updated 2026-08-14.
- [archive/2026-05-28/m12-project-rename.md](archive/2026-05-28/m12-project-rename.md) — _milestone_ — > **Stub-drafted 2026-05-28** following M11 closeout. M12 bundles > one operator-facing headline feature (`docs project…. Updated 2026-08-14.
- [archive/2026-05-29/m13-pypi-publish-impl.md](archive/2026-05-29/m13-pypi-publish-impl.md) — _log_ — Chronological log of work on M13 — PyPI publish 1.5.0. Append a section per runbook phase (operator prep → pre-publish…. Updated 2026-08-14.
- [archive/2026-05-29/m13-pypi-publish.md](archive/2026-05-29/m13-pypi-publish.md) — _milestone_ — > **Stub-drafted 2026-05-29, post M12 closeout.** M13 enters > active state immediately — the M12 wheel + sdist already…. Updated 2026-08-14.
- [archive/2026-06-03/m14-robustness-agent-native-impl.md](archive/2026-06-03/m14-robustness-agent-native-impl.md) — _log_ — Chronological log of work on M14 — Robustness + agent-native surface. Append a section per TDD phase with objective,…. Updated 2026-08-14.
- [archive/2026-06-03/m14-robustness-agent-native.md](archive/2026-06-03/m14-robustness-agent-native.md) — _milestone_ — - Milestone: M14 (v1.6.0, part 1 of 2) - Title: Robustness + autonomous archive - Surface: correctness/atomicity…. Updated 2026-08-14.
- [archive/2026-06-03/m15-agent-native-authoring-impl.md](archive/2026-06-03/m15-agent-native-authoring-impl.md) — _log_ — Chronological log of work on M15 — Agent-native doc authoring. Append a section per TDD phase with objective, files…. Updated 2026-08-14.
- [archive/2026-06-03/m17-pypi-publish.md](archive/2026-06-03/m17-pypi-publish.md) — _milestone_ — > **Stub-drafted 2026-06-03, post M14 + M15 closeout.** M17 > enters active state immediately — M14 and M15 are both >…. Updated 2026-08-14.
- [archive/2026-06-12/m19-post-edit-validation-impl.md](archive/2026-06-12/m19-post-edit-validation-impl.md) — _log_ — Chronological log of work on M19 — Post-edit validation ergonomics (`docs touch --check` + configurable stale window).…. Updated 2026-08-14.
- [archive/2026-06-12/m19-post-edit-validation.md](archive/2026-06-12/m19-post-edit-validation.md) — _milestone_ — - Milestone: M19 (v1.6.5) - Title: Post-edit validation ergonomics (touch --check + configurable stale window) -…. Updated 2026-08-14.
- [archive/2026-06-12/m20-pypi-publish.md](archive/2026-06-12/m20-pypi-publish.md) — _milestone_ — > **Stub-drafted 2026-06-12, post M19 implementation-complete.** M20 > enters active state immediately — M19 is…. Updated 2026-08-14.
- [archive/2026-07-03/m24-pypi-publish.md](archive/2026-07-03/m24-pypi-publish.md) — _milestone_ — > **Stub-drafted 2026-07-03**, immediately after M23 was merged to `main` > (merge commit `839daef`). M24 enters active…. Updated 2026-08-14.
- [archive/2026-07-03/m21-update-check-impl.md](archive/2026-07-03/m21-update-check-impl.md) — _log_ — Chronological log of work on M21 — Update-check notification (PyPI new-version notice). Append a section per TDD phase…. Updated 2026-07-03.
- [archive/2026-07-03/m21-update-check.md](archive/2026-07-03/m21-update-check.md) — _milestone_ — - Milestone: M21 (v1.7.0) - Title: Update-check notification (PyPI new-version notice) - Surface: docs-cli's **first…. Updated 2026-07-03.
- [archive/2026-07-03/m22-root-placement-guidance-impl.md](archive/2026-07-03/m22-root-placement-guidance-impl.md) — _log_ — Chronological log of work on M22 (Doc-tree root placement guidance). Append a section per phase with objective, files…. Updated 2026-07-03.
- [archive/2026-07-03/m22-root-placement-guidance.md](archive/2026-07-03/m22-root-placement-guidance.md) — _milestone_ — - Milestone: M22 - Title: Doc-tree root placement guidance (project ≠ directory) - Surface: documentation-only — the…. Updated 2026-07-03.
- [archive/2026-07-03/m23-agent-aware-install-skill-impl.md](archive/2026-07-03/m23-agent-aware-install-skill-impl.md) — _log_ — Chronological log of work on M23 — Agent-aware install-skill + recorded-dest skill-refresh hint. Append a section per…. Updated 2026-07-03.
- [archive/2026-07-03/m23-agent-aware-install-skill.md](archive/2026-07-03/m23-agent-aware-install-skill.md) — _milestone_ — - Milestone: M23 (v1.8.0) - Title: Agent-aware install-skill + recorded-dest skill-refresh hint - Surface: `docs…. Updated 2026-07-03.
- [archive/2026-06-12/m18-archive-edge-integrity-impl.md](archive/2026-06-12/m18-archive-edge-integrity-impl.md) — _log_ — Chronological log of work on M18 — Archive edge integrity (intra-archive `Related:` rewriting). Append a section per…. Updated 2026-06-12.
- [archive/2026-06-12/m18-archive-edge-integrity.md](archive/2026-06-12/m18-archive-edge-integrity.md) — _milestone_ — - Milestone: M18 - Title: Archive edge integrity (intra-archive Related: rewriting) - Surface: a correctness fix to…. Updated 2026-06-12.
- [archive/2026-06-03/m15-agent-native-authoring.md](archive/2026-06-03/m15-agent-native-authoring.md) — _milestone_ — - Milestone: M15 (v1.6.0, part 2 of 2) - Title: Agent-native doc authoring - Surface: the agent-native *authoring* set…. Updated 2026-06-03.
- [archive/2026-06-01/m16-bundled-docs-skill-quality-impl.md](archive/2026-06-01/m16-bundled-docs-skill-quality-impl.md) — _log_ — Chronological log for M16. This milestone records the docs-cli bundled `docs` skill changes required by the Agent…. Updated 2026-06-01.
- [archive/2026-06-01/m16-bundled-docs-skill-quality-test-matrix.md](archive/2026-06-01/m16-bundled-docs-skill-quality-test-matrix.md) — _spec_ — Lite. Updated 2026-06-01.
- [archive/2026-06-01/m16-bundled-docs-skill-quality.md](archive/2026-06-01/m16-bundled-docs-skill-quality.md) — _milestone_ — - Milestone: M16 - Title: Bundled docs skill quality artifacts - Surface: bundled `docs` skill guidance under…. Updated 2026-06-01.
- [archive/2026-05-27/m10-adoption-polish-impl.md](archive/2026-05-27/m10-adoption-polish-impl.md) — _log_ — Chronological log of work on M10 — Adoption-flow polish + 1.3.0 carry-overs. Append a section per phase with objective,…. Updated 2026-05-27.
- [archive/2026-05-27/m10-adoption-polish.md](archive/2026-05-27/m10-adoption-polish.md) — _milestone_ — - Milestone: M10 (v1.4.0) - Title: Adoption-flow polish + 1.3.0 carry-overs - Surface: two new CLI features (`docs…. Updated 2026-05-27.
- [archive/2026-05-25/m7-migration-accuracy-log.md](archive/2026-05-25/m7-migration-accuracy-log.md) — _log_ — - Project: docs - Milestone: M7 — Migration plan accuracy - Started: 2026-05-24 - Progress: **Phase 1 complete; Phase 2…. Updated 2026-05-25.
- [archive/2026-05-25/m8-adoption-workflow-log.md](archive/2026-05-25/m8-adoption-workflow-log.md) — _log_ — - Project: docs - Milestone: M8 — Adoption workflow (agent-driveable) - Started: 2026-05-24 - Progress: **All 10 TDD…. Updated 2026-05-25.
- [archive/2026-05-20/m1-parser-and-index-log.md](archive/2026-05-20/m1-parser-and-index-log.md) — _log_ — - Project: docs - Milestone: M1 — Parser and `docs index` - Started: 2026-05-20 - Shipped: 2026-05-20 - Progress: Phase…. Updated 2026-05-20.
<!-- docs:generated end -->
