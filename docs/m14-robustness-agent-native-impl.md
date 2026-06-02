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
| 2. Write Tests (RED) | Done | 2026-06-02 | 19 new tests + 1 removed (false-confidence test_a6); migrated 2 cascade prompt tests to `--interactive`. |
| 3. Create Fixtures | Done | 2026-06-02 | `tests/fixtures/trees/mv-with-malformed/`; inline tmp_path helpers for A4/A6/B1/A2/A3 live in their Phase-2 test files. |
| 4. Run Tests (RED) | Done | 2026-06-02 | **454 collected, 17 failed, 437 passed**; the 17 are exactly the intended RED set (see Phase 4 section). No collateral, no import/fixture errors, no skips (non-root). |
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

## Phase 2 — Write Tests (RED)

**Objective.** Pin every M14 A/B/C behavior with subprocess tests
(existing `_run([...], cwd=...)` + copytree/tmp_path idiom), RED for the
documented Step-2 reasons.

**Actions (19 new tests; 1 removed; 2 migrated).**

- A1 (`test_cli_mv`): `test_mv_malformed_sibling_aborts_atomically` +
  `test_mv_malformed_sibling_does_not_dangle_referring_edge`.
- A2 (`test_cli_new`): `test_new_outside_docs_root_exits_2`,
  `test_new_root_without_docs_toml_refuses`, and the over-refusal
  GREEN guard `test_new_inside_root_still_works_without_root_flag`.
- A3 (`test_cli_new`): `test_new_empty_final_segment_slug_rejected`.
- A4 (`test_cli_mv`): `test_mv_oserror_mid_rewrite_exits_2` — observable
  contract (exit 2 + no `Traceback`); read-only-DIRECTORY trigger (a bare
  `chmod 0o444` file is NOT a reliable trigger — POSIX `rename()` onto a
  read-only target succeeds when the dir is writable); `skipif` root.
- A5 (`test_atomic_write`, new file): `test_atomic_write_fsyncs_before_rename`
  (patched-`os.fsync` recording) + the `test_atomic_write_still_publishes_content`
  GREEN guard.
- A6 (four sites): `test_touch_with_malformed_excluded_file_stamps_and_reindexes`
  + `test_touch_excluded_malformed_file_not_in_index`;
  `test_archive_with_malformed_excluded_file_succeeds_and_reindexes`;
  `test_mv_excluded_malformed_file_reindexes`;
  `test_project_rename_with_malformed_excluded_file_succeeds`. Each inline
  tree carries `[exclude] dirs = ["vendor"]` + `vendor/README.md` =
  `"no metadata\n# H1\n"` (raises `MetadataError` in the walk).
- B1 (`test_cli_archive`): `test_archive_cascade_no_prompt_archives_all_relations`
  (no stdin; both relations archived; no `[y/N]`; footer present),
  `test_archive_cascade_dry_run_previews_and_writes_nothing`,
  `test_archive_cascade_only_filters_by_glob`, plus the
  `test_archive_cascade_dry_run_rejects_interactive` acceptance-state
  guard. MIGRATED the two legacy cascade prompt tests to `--interactive`
  (`test_archive_interactive_yes/no_*`).
- C1 (`test_skill_refs`): `test_bundled_skill_has_no_repo_relative_links`
  (GREEN guard — greps every bundled `.md` for `](../`).
- C3 (`test_packaging`): removed `test_a6_hatch_build_packages_the_skill`
  (false-confidence pyproject-comment grep); strengthened `test_b3` with
  a `>= 5` floor on bundled skill-reference files.

**Results.** 454 tests collect with no import errors. The new behavior
tests are RED; the GREEN guards pass.

## Phase 3 — Create Fixtures

**Objective.** Stage the one on-disk fixture the plan calls for; the rest
are inline `tmp_path` helpers in the Phase-2 test files.

**Actions.** Created `tests/fixtures/trees/mv-with-malformed/` (modeled on
`rename-with-malformed`): `.docs.toml`, `good-a.md` (mv source),
`referrer.md` (`pairs-with: good-a.md`), `broken.md` (no H1 →
`MetadataError`). Rewrote the second A1 test to pin edge-resolvability
rather than INDEX byte-identity: a non-excluded malformed sibling makes
`docs index` itself fail (exit 2), so a pre-built-INDEX assertion could
not be set up — the test instead asserts the referring edge's target
(`good-a.md`) still exists after the abort (no dangling edge) and no
stray INDEX is written.

## Phase 4 — Run Tests (RED Baseline)

**Command.** `.venv/bin/python -m pytest tests/ -q`

**Result. 454 collected · 17 failed · 437 passed · 0 errors · 0 skips**
(non-root, so the A4 `skipif` does not trigger and its OSError trigger
fires). The 17 RED are exactly the intended behavior set:

| Finding | RED tests |
|---|---|
| A1 | `test_mv_malformed_sibling_aborts_atomically`, `test_mv_malformed_sibling_does_not_dangle_referring_edge` |
| A2 | `test_new_outside_docs_root_exits_2`, `test_new_root_without_docs_toml_refuses` |
| A3 | `test_new_empty_final_segment_slug_rejected` |
| A4 | `test_mv_oserror_mid_rewrite_exits_2` |
| A5 | `test_atomic_write_fsyncs_before_rename` |
| A6 | `test_touch_with_malformed_excluded_file_stamps_and_reindexes`, `test_touch_excluded_malformed_file_not_in_index`, `test_archive_with_malformed_excluded_file_succeeds_and_reindexes`, `test_mv_excluded_malformed_file_reindexes`, `test_project_rename_with_malformed_excluded_file_succeeds` |
| B1 | `test_archive_interactive_yes_also_archives_related`, `test_archive_interactive_no_leaves_related_in_place`, `test_archive_cascade_no_prompt_archives_all_relations`, `test_archive_cascade_dry_run_previews_and_writes_nothing`, `test_archive_cascade_only_filters_by_glob` |

No collateral failures: `test_skill_refs` byte-identity GREEN; the
formerly-stale `test_index_output_matches_frozen_snapshot` GREEN
(snapshot regenerated in Phase 1). C1/C3 GREEN guards pass.

**Quality-gate note (surfaced, not fixed).**
`tests/test_skill_quality_artifacts.py` is RED under
`ruff check` (I001 import-sort) AND `ruff format --check` — but this is
**pre-existing**, committed in `9ceb113` ("Add bundled docs skill quality
artifacts", the M16 artifacts that landed on this branch's base). It is
not a file M14 touches. Surfaced for the operator; out of Step-1 scope to
fix here (belongs with the M16 artifacts).
