# docs — Definition of Ready

Lifecycle: active
Role: reference
Project: docs
Updated: 2026-05-22

Related:
- pairs-with: charter.md
- pairs-with: plan.md
- pairs-with: status.md

Gate-check before implementation begins. Implementation does not start until every item is green.

## Foundation checklist

- [x] **Charter** states problem, user, success metric, non-goals. → [charter.md](charter.md)
- [x] **Scope, assumptions, constraints captured.** Folded into charter's Non-goals + Audience + the convention's "What `docs` does not promise." → [charter.md](charter.md), [convention.md](convention.md)
- [x] **Stakeholders/interfaces noted with owners.** N/A — solo project, no external interfaces. Documented absence.
- [x] **Architecture option chosen; decision log updated.** Single-file Python, stdlib-only. → [architecture.md](architecture.md), [vocab-adr.md](vocab-adr.md), [dual-status-adr.md](dual-status-adr.md)
- [x] **Milestones and dependencies mapped; timeline feasible.** Five-milestone roadmap, M4 depends on M3, others sequential. → [plan.md](plan.md)
- [x] **Environment/tooling validated; access unblocked.** Python 3.11+ confirmed; no third-party deps; commands listed. → [architecture.md](architecture.md)
- [x] **Data plan set; compliance/privacy constraints clear.** Synthetic fixtures only; this repo's own `docs/` as real-world dogfood; no privacy considerations. → [test-strategy.md](test-strategy.md)
- [x] **Test strategy outline covers critical paths and fixtures.** Layers, fixture sources, critical paths, quality gates. → [test-strategy.md](test-strategy.md)
- [x] **Documentation plan set.** Self-evident — this repo's `docs/` IS the documentation plan; it manages itself once `docs` is built (dogfood).
- [x] **Open risks logged with owners; go/no-go recorded.** See "Residual risks" below.

## Residual risks

| Risk | Mitigation | Owner |
|---|---|---|
| Parser convention is too rigid in practice; real docs deviate | M4 (`docs migrate`) is built specifically to absorb deviation; dogfood will surface rough edges early | art |
| Single-file Python grows past readable size before package-split discipline kicks in | Hard cap mental budget at ~500 lines for M1; revisit at M3 | art |
| `Updated:` field rots when authors hand-edit without bumping | `docs check --stale N` surfaces it; `docs touch` makes the bump cheap | art |
| Marker-block strategy breaks if user hand-edits markers themselves | Documented; `docs check` reports missing markers | art |
| Cross-host portability of the script — paths embedded in skill files diverge from per-host install paths | **Resolved (M5, 2026-05-22).** Per resolved OQ2, the M5 skill is authored host-agnostic at `skills/docs/SKILL.md` — it bakes in no absolute path; the host-specific path lives only in the documented copy/symlink into `~/.claude/skills/docs/` (see `architecture.md`'s Install section). Row left as historical record. | art |

## Go/no-go

**Status: GO.** All foundation items green. M1 (Parser and `docs index`) is unblocked.

Recorded 2026-05-20 by art@bitholdersinc.com.
