# M15 — Implementation Log

Lifecycle: draft
Role: log
Project: docs
Updated: 2026-06-02

Related:
- child-of: m15-agent-native-authoring.md
- pairs-with: m15-agent-native-authoring.md
- pairs-with: status.md

## Overview

Chronological log of work on M15 — Agent-native doc authoring. Append a
section per TDD phase with objective, files changed, actions, test
results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M15 — Agent-native doc authoring (v1.6.0)
- Started: 2026-06-02 (scaffolded; carved from M14)
- Progress: **Milestone pair scaffolded 2026-06-02.** Carved out of M14
  (operator-confirmed) when the post-1.5.0 contract outgrew M12 scale.
  Scope is the agent-native authoring set: B2 `docs project set`, B3
  `docs stamp`, C4 the `--body-from` real-frontmatter detector, C2 the
  skill/cli docs. **Depends on M14** — implement after it; M17 publishes
  both as 1.6.0. Phase 1 (Define Contract) opens via `/ship-milestone M15`.

(Note: doc-lifecycle status is the front-matter `Lifecycle:` field. This
section tracks implementation progress, which is distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Pending | — | |
| 2. Write Tests (RED) | Pending | — | |
| 3. Create Data/Fixtures | Pending | — | |
| 4. Run Tests (RED Baseline) | Pending | — | |
| 5. Update Base Interfaces | Pending | — | |
| 6. Implement Offline/Core Path | Pending | — | |
| 7. Update Tool/Wrapper Layer | Pending | — | |
| 8. Run Tests (GREEN) | Pending | — | |
| 9. Implement Online/Integration | Pending | — | |
| 10. Quality, Docs, Refactor | Pending | — | |

## Provenance — where the scope came from

The four items were carved out of M14 on 2026-06-02 (operator-confirmed)
when the A6/B3/C4 widening pushed M14 past M12 scale:

- **B2 `docs project set`** — [agent-native-invocation.md](agent-native-invocation.md)
  §5E (the single-doc counterpart to `docs project rename`).
- **B3 `docs stamp` + C4 `--body-from` detector** — surfaced by the M16
  bundled-docs-skill dogfood: an agent wrote a full test-matrix body and
  `docs new --body-from` refused it on a `Reason:` line. Write-then-stamp
  (B3) is the structural fix; the detector (C4) hardens the legacy path.
- **C2 skill/cli docs** — the bundled-skill + `cli.md` documentation for
  the above, kept with the surface it describes.

See [m14-robustness-agent-native.md](m14-robustness-agent-native.md)
Decisions for the split rationale and monotonic numbering.

## Phase 1 — Define Contract

_Not started._
