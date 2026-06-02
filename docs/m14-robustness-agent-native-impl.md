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
| 1. Define Contract | Done | 2026-06-02 | cli.md + convention.md deltas; bundled refs resynced byte-identical; A5/A6 Decisions recorded; `docs check docs/` clean. |
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

**Objective.** Write every M14 behavior delta into `docs/cli.md` +
`docs/convention.md`, mirror byte-for-byte into the bundled
`src/docs_cli/skill/references/`, and record the two operator Decisions
(A6 four-site, A5 fsync) before any code or test changes.

**Actions.**

- **B1 (`cli.md` §archive).** Rewrote the synopsis to
  `[--cascade | --cascade-dry-run | --cascade-only GLOB | --interactive]`;
  established the invariant *docs never prompts unless `--interactive`*;
  defined each flag (bare `--cascade` = all one-hop, no prompt, loud
  stderr footer naming the set; `--cascade-dry-run` = preview + write
  nothing + exit 0; `--cascade-only GLOB` = subset whose related-doc
  root-relative POSIX target path matches `GLOB` via the
  `compile_exclude_predicate` matcher; `--interactive` = legacy `[y/N]`).
  Wrote the combination matrix (mutually-exclusive
  `--cascade`/`--cascade-only`/`--interactive`; `--cascade-dry-run`
  composes with `--cascade-only`, rejected with `--interactive`).
  Reconciled the M12-extension paragraph (no longer says "prompt").
- **A2 (`cli.md` Invocation + §new Exits).** Invocation now states the
  read verbs (`index`/`list`/`check`) keep the cwd-fallback while
  `new`/`touch`/`project rename` refuse it (RQ#2 — `new` only is the M14
  change). §new gained the strict-root refusal paragraph with the exact
  messages (mirroring `touch`'s wording).
- **A3 (`cli.md` §new).** Added empty-final-segment slug rejection
  (`foo/`, `foo/.md` → exit 2 `docs: invalid slug <slug>`).
- **A6 (`cli.md` §touch/§archive/§mv/§project rename + "Common:
  exclusion"; `convention.md` §Exclusion).** Documented that the
  end-of-batch reindex of all FOUR mutating verbs honours `[exclude]` /
  `.docsignore` (persistent sources only; no new `--exclude` flag), so a
  malformed *excluded* file never fails the post-mutation reindex (exit 0
  on the excluded-malformed case; a non-excluded malformed file is still
  exit 2). Widened per operator decision (RQ#6).
- **A5 (`cli.md` stays; `cli.py` docstring).** Per the operator decision
  to ADD `os.fsync`, the `cli.md` §archive "fsync'd" claim STAYS (becomes
  true in Phase 6). Tightened the `_archive_one` docstring to describe
  the edit-before-move ordering accurately.
- **Exit-code matrix.** Added `new` (strict-root + slug) and
  `archive --cascade-dry-run` rows to the M12/M14 exit-code table.
- **Milestone doc.** Recorded the A6-four-site, A5-fsync, B1-shape,
  A2-scope, and C1-verification Decisions; marked C1 done-by-M16;
  resolved the Step-1 OQs; checked off the Phase-1 checklist item.
- **Bundled refs.** `cp docs/cli.md` + `docs/convention.md` into
  `src/docs_cli/skill/references/` (byte-identical;
  `test_skill_refs.py` GREEN).

**Results.** `docs check docs/` exit 0; `diff docs/cli.md
src/docs_cli/skill/references/cli.md` empty; same for `convention.md`.
INDEX + frozen snapshot regenerated in lockstep.

**Decisions.** See the milestone doc's Decisions section (A6 four-site;
A5 ADD fsync + keep claim; B1 cascade shape; A2 `new`-only; C1
verification-only). No new OQs surfaced at Phase 1.

> **Pre-existing baseline note (surfaced 2026-06-02).** On checkout,
> `tests/test_cli_index.py::test_index_output_matches_frozen_snapshot`
> was already RED: the M14-setup commits added the M14/M15/M16 milestone
> docs and regenerated `docs/INDEX.md` (42 active) but never refreshed
> the frozen snapshot fixture `tests/fixtures/expected/docs-INDEX.md`
> (still 37 active, dated 2026-05-29). `docs/INDEX.md` itself is in sync
> with the tree. Per the durable lockstep gotcha, Phase 1 regenerates
> the snapshot alongside the INDEX so the dogfood guard is GREEN again.
