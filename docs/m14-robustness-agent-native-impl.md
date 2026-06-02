# M14 — Implementation Log

Lifecycle: draft
Role: log
Project: docs
Updated: 2026-06-02

Related:
- child-of: m14-robustness-agent-native.md
- pairs-with: m14-robustness-agent-native.md
- pairs-with: status.md

## Overview

Chronological log of work on M14 — Robustness + agent-native surface.
Append a section per TDD phase with objective, actions, results,
decisions.

## Implementation metadata

- Project: docs
- Milestone: M14 — Robustness + agent-native surface (v1.6)
- Started: 2026-05-29 (scaffolded)
- Progress: **Milestone pair scaffolded 2026-05-29** on
  `m14/milestone-setup`, off `main` at the post-1.5.0 review. Scope
  folds the multi-agent review findings (threads A + C) and the
  [agent-native-invocation.md](agent-native-invocation.md) proposal
  (thread B). Phase 1 (Define Contract) opens via
  `/ship-milestone M14`.

(Note: doc-lifecycle status is the front-matter `Lifecycle:` field.
This section tracks implementation progress, which is distinct.)

## Phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Pending | — | |
| 2. Write Tests (RED) | Pending | — | |
| 3. Create Fixtures | Pending | — | |
| 4. Run Tests (RED) | Pending | — | |
| 5. Update Interfaces | Pending | — | |
| 6. Implement Core | Pending | — | |
| 7. Update Wrappers | Pending | — | |
| 8. Run Tests (GREEN) + gate | Pending | — | |
| 9. Integrate | Pending | — | |
| 10. Quality, Docs, Refactor | Pending | — | |

## Provenance — where the scope came from

- **Threads A + C** — the 2026-05-29 post-1.5.0 multi-agent review
  (three Opus reviewers: core code, docs tree, agent skill + packaging).
  Verbatim findings with `cli.py` / test line refs are in the milestone
  doc's Scope section.
- **Thread B** — [agent-native-invocation.md](agent-native-invocation.md)
  (the `ideas`-project proposal): P0-1 non-interactive `--cascade` and
  §5E `docs project set`. The broader agent-native surface in that doc
  is explicitly deferred (see the milestone doc's Decisions).
- **A6 added; B3/C4 carved to M15 (2026-06-02)** — the M16
  bundled-docs-skill dogfood (run ahead of M14) hit two live defects:
  `docs new --body-from` refused a test-matrix body on its `Reason:` line,
  and `docs touch` failed its post-mutation reindex on a malformed
  *excluded* plugin `README.md`. The touch fix landed here as **A6** (same
  atomicity family as A1/A4). The `--body-from` detector (C4) and the
  `docs stamp` write-then-stamp verb (B3) — plus B2 `project set` and the
  C2 skill docs — were carved into **M15 — Agent-native doc authoring**
  when the widened contract outgrew M12 scale (operator-confirmed
  2026-06-02). M14 retains Thread A + B1 + C1/C3.

## Phase 1 — Define Contract

_Not started._
