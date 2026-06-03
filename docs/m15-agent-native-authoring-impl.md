# M15 — Implementation Log

Lifecycle: draft
Role: log
Project: docs
Updated: 2026-06-03

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
| 1. Define Contract | Done | 2026-06-03 | cli.md: `project set` + `stamp` sections; `--body-from` cluster/fence detector rewrite; per-verb exit-code rows; bundled ref resynced byte-identical. |
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

**Objective.** Pin the `cli.md` contract for the four M15 items (B2
`project set`, B3 `stamp`, C4 `--body-from` detector, C2 docs) so the
RED tests (Phase 2) and the implementation (Phases 5–6) have a single
source of truth. CONTRACT ONLY — no `_cmd_*`, no argparse wiring, no
detector rewrite this phase.

**Files changed.**

- `docs/cli.md` — (1) added a `### docs project set <doc>... <new-project>`
  section modeled on `project rename` (grammar split + ≥2-token guard;
  strict-root resolution; `normalise_project_name()` + empty-string
  rejection; the `--new-project` typo guard with the §5E did-you-mean
  shape via `difflib.get_close_matches`; per-doc `Project:` rewrite with
  insertion-when-absent and ONE end-of-batch INDEX refresh; NO
  `.docs.toml` / `Related:`-edge rewrite; archived-target → whole-batch
  exit 2; validate-all-first atomic semantics; `--dry-run` / no-op /
  success footer gated on `not --quiet`). (2) Added a
  `### docs stamp <file>...` section (write-then-stamp: Lifecycle:draft,
  role `--role` else `notes` with NO H1-role inference, project `--project`
  else config, title from H1 / synthesised, `insert_metadata_block`
  insertion preserving body + `## Migrated metadata`; idempotent re-stamp
  = Updated-only refresh; strict-root; atomic multi-file batch;
  `--dry-run`; one end-of-batch INDEX; invalid `--role` exit 2). (3)
  Rewrote the `--body-from` refusal heuristic paragraph + the `new` exit
  clause: refuse only on a leading `---` fence OR a ≥2 `{Lifecycle, Role,
  Updated}` adjacent cluster; lone prose `Reason:`/`Plan:`/`Updated:` now
  passes; error tokens unchanged; noted `edge-case-keyword.md` now passes.
  (4) Added `project set` + `stamp` rows to the per-verb exit-code table.
- `src/docs_cli/skill/references/cli.md` — resynced byte-identical to
  `docs/cli.md` (M14 C1: `docs/` canonical), keeping
  `tests/test_skill_refs.py` GREEN. SKILL.md verb table + frontmatter
  description deferred to Phase 7 (C2) per the plan.

**Actions.** Edited `docs/cli.md`; `docs touch docs/cli.md` (Updated →
2026-06-03); `cp docs/cli.md src/docs_cli/skill/references/cli.md`;
`docs index docs/` (INDEX regenerated in lockstep); `docs check docs/`
clean.

**Test results.** `tests/test_skill_refs.py` GREEN (3 passed) — bundled
ref byte-identical. No code touched, so the rest of the suite is
unchanged from the 459-passing pre-phase baseline.

**Decisions applied (conductor-resolved, binding).**

1. `stamp` is a STANDALONE top-level verb, mutating-verb polarity (writes
   by default; `--dry-run` to opt out), `parents=[common]`; reuses
   `insert_metadata_block` internally but is NOT routed through / aliased
   to `migrate`. (Wiring is Phase 5.)
2. `stamp` default `Lifecycle: draft`.
3. `stamp` role = `--role` else `notes` (NO H1-role inference);
   project = `--project` else `config.project`; title from H1 (synthesise
   from filename when absent).
4. `--body-from` detector: refuse on a leading `---` fence OR ≥2 adjacent
   `{Lifecycle, Role, Updated}` lines in the first ~20 lines (after an
   optional `# H1`); a lone prose required-field line passes.
5. C4 fixtures: add `real-frontmatter-body.md` + `yaml-fence-body.md`
   (refusal), `reason-in-body.md` (pass), flip `edge-case-keyword.md` to
   pass, demote `with-frontmatter.txt` from a refusal case. Refusal
   coverage is carried by the cluster/fence fixtures (load-bearing).
6. `docs/` canonical; Phase 1 edits `docs/cli.md` AND resyncs the bundled
   ref in the same commit; SKILL.md verb-table/description → Phase 7.
7. `project set` grammar: one `nargs="+"` positional split into
   `*docs, new_project`; ≥2 tokens required (exit 2 otherwise).
8. `project set` archived target: refuse the WHOLE batch (exit 2) naming
   the path — not an incidental skip (unlike `project rename`).
