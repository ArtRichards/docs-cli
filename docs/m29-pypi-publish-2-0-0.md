# M29 — PyPI publish 2.0.0

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-08-15

Related:
- child-of: plan.md
- implements: charter.md
- pairs-with: release-runbook.md
- pairs-with: status.md
- references: feedback-log.md
- depends-on: m25-reciprocal-relationship-integrity.md
- depends-on: m26-safe-archive-selection.md
- depends-on: m27-markdown-body-link-validation.md
- depends-on: m28-move-safe-body-link-rewrites.md
- follows: m28a-archive-date-witness.md
- depends-on: m28a-archive-date-witness.md

## Overview

- Milestone: M29
- Title: PyPI publish 2.0.0
- Surface: runbook-driven publication of the complete M25–M28 relationship and
  link-integrity train as `docs-cli==2.0.0`, followed by host-skill refresh and
  milestone closeout.
- Progress: **Registered release stub (2026-08-10).** Scheduled after durable
  prerequisites M25–M28 and intentionally not marked with a transient
  `blocked-by` edge: the work is planned, not unexpectedly unable to proceed.
  No implementation log or runbook phase has started.

### Goal

Ship the v2.0 safety contract with a verified upgrade path: users can diagnose
and repair reciprocal edges, archive only explicit selections, detect broken
local body links, and move/archive without recreating that damage.

## Planned release scope

- M25 — reciprocal semantics, hard validation, `docs relate`, archived audit.
- M26 — safe preview + explicit archive selection and batch preflight.
- M27 — local Markdown body-link validation and legacy upgrade handling.
- M28 — move/archive-safe body-link rewrites.
- Breaking-change and migration guide for new check failures and retired unsafe
  cascade behavior.
- Served-wheel contract verification for every headline workflow.
- Published bundled skill/reference parity and host-machine skill refresh.

## Why 2.0.0

The train intentionally changes existing automation: previously one-sided
recognized edges can become hard check failures, and bare `--cascade` no longer
writes related documents. These safety improvements are compatibility breaks
for a public 1.8.0 CLI, so the release is planned as a SemVer major rather than
an additive 1.9.0.

## Runbook shape

M29 is operational, not a normal ten-phase code milestone. Once M25–M28 are
implementation-complete, scaffold the implementation log and run the current
`release-runbook.md`: operator prep, pre-publish gate, TestPyPI rehearsal,
authorized production publish/tag/release, served-artifact acceptance, skill
refresh, and docs closeout.

## Closeout intent

- Archive M25–M28 plan/log pairs plus the M29 milestone doc only after the
  production release and served-artifact acceptance succeed.
- Keep the M29 implementation log, release runbook, and project status active,
  following M17/M20/M24 precedent.
- Update Agent Playbook Suite only after `docs-cli==2.0.0` is available; that
  cross-repository implementation is not part of M29.

## Open questions before activation

1. Whether intermediate local versions are used during M25–M28 or the tree
   moves directly to `2.0.0` in one implementation milestone.
2. Exact operator authorization cadence for irreversible upload/push/tag/release
   actions; default to the M24 “author now, confirm at the gate” pattern.
3. Final archive manifest and any historical active publish logs intentionally
   retained at the root.

## Success criteria

- M25–M28 full gates are GREEN and their completion summaries are accurate.
- Migration guidance is tested on legacy relationship/body-link fixtures.
- Local, TestPyPI, and PyPI artifacts pass integrity and headline acceptance.
- Version/tag/release/CHANGELOG and served bytes agree.
- Published and host-installed skills match the 2.0.0 bundled skill.
- Docs closeout is edge-clean and `docs check` passes.
