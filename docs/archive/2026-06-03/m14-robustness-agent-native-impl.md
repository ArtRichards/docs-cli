# M14 — Implementation Log

Lifecycle: archived
Role: log
Project: docs
Updated: 2026-08-14
Archived-reason: Milestone M14 complete; docs-cli==1.6.0 shipped to PyPI via M17 2026-06-03

Related:
- child-of: archive/2026-06-03/m14-robustness-agent-native.md
- pairs-with: archive/2026-06-03/m14-robustness-agent-native.md
- pairs-with: status.md

Revision:
- 2026-08-14: M27 one-time body-link migration; body-link destinations repaired (destination tokens only)

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
  [agent-native-invocation.md](../../agent-native-invocation.md) proposal
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
| 4. Run Tests (RED) | Done | 2026-06-02 | Initial baseline **454 collected, 17 failed, 437 passed**. Fresh-eyes review fixes (2026-06-02) → **458 collected, 18 failed, 440 passed**: +1 RED composition test, +3 GREEN-by-argparse mutex params, A5 fsync test tightened (still RED). See Phase 4 section. No collateral, no import/fixture errors, no skips (non-root). |
| 5. Update Interfaces | Done | 2026-06-02 | argparse cascade flag set (`--cascade` / `--cascade-only GLOB` / `--interactive` in one mutex group + `--cascade-dry-run` outside it); declared `_resolve_new_root` + `_cascade_set`. `archive --help` shows 4 flags; suite collects 458; 3-param mutex test GREEN by real mutex. |
| 6. Implement Core | Done | 2026-06-02 | A5 fsync (tmpfile + parent dir), A1 mv pre-flight (exit 2), A4 OSError→2, A2 strict-root `new`, A3 empty-slug guard, A6 four-verb exclude predicate (every walk/reindex incl. `_rewrite_referring_edges`), B1 non-interactive cascade + footer/preview helpers. All 18 RED → GREEN; **458 passed**. `test_body_from._minimal_tree` gained a `.docs.toml` (A2 lockstep — see Phase-6 section). |
| 7. Update Wrappers | Done | 2026-06-02 | pyproject 1.5.0→1.6.0 (`pip install -e .`); CHANGELOG `## 1.6.0 — UNRELEASED`; 4 packaging version-string assertions to 1.6.0 in lockstep (+`_1_6_0` renames). Bundled refs unchanged (no cli.md/convention.md edits in 6/7). |
| 8. Run Tests (GREEN) + gate | Done | 2026-06-02 | **458 passed, 0 failed.** ruff / ruff format --check / mypy clean tree-wide after the separate M16 import-sort autofix commit. `docs check docs/` exit 0; `docs index --root docs/ --dry-run` no diff. |
| 9. Integrate | Done | 2026-06-02 | Dogfood on throwaway copies (see Phase-9 section): `archive --cascade` / `--cascade-dry-run`, `new` outside-root refusal, `touch` over a malformed-excluded tree, `docs check docs/`. All four behave per Success Criteria. |
| 10. Quality, Docs, Refactor | Done | 2026-06-02 | Closeout summaries; milestone + success-criteria boxes ticked; status.md / plan.md flipped to implementation-complete (1.6.0 built locally; M17 publishes); INDEX + frozen snapshot in lockstep; cascade dry-run dead-branch removed (behaviour-preserving). |

## Provenance — where the scope came from

- **Threads A + C** — the 2026-05-29 post-1.5.0 multi-agent review
  (three Opus reviewers: core code, docs tree, agent skill + packaging).
  Verbatim findings with `cli.py` / test line refs are in the milestone
  doc's Scope section.
- **Thread B** — [agent-native-invocation.md](../../agent-native-invocation.md)
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
- A4 (`test_cli_mv` + `test_cli_archive`):
  `test_mv_oserror_mid_rewrite_exits_2` (mv) and
  `test_archive_oserror_mid_rewrite_exits_2` (archive, added in the
  post-Step-2 review) — BOTH halves of the A4 contract (mv AND archive →
  clean exit 2, no `Traceback`) now have a regression guard. Both use the
  identical observable contract (exit 2 + no `Traceback`) and the shared
  read-only-DIRECTORY trigger (a bare `chmod 0o444` file is NOT reliable —
  POSIX `rename()` onto a read-only target succeeds when the dir is
  writable; a `0o555` referrer dir makes `atomic_write`'s
  `os.open(tmp, O_CREAT)` raise `PermissionError`), and the same `skipif`
  root guard (root bypasses `0o555`, so the OSError trigger does not fire).
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
not a file M14 touches. **Deferred to Step 2's quality phase (Phase 10):**
M14's "quality gate clean tree-wide" Success Criterion is met there with a
clearly-labeled mechanical ruff autofix. Intentionally NOT fixed in Step 1
to keep the Step-1 commits clean and the RED baseline pure (it is not part
of the RED behavior set).

## Phase 4 — fresh-eyes review fixes (2026-06-02)

A fresh-eyes review of Step 1 returned SOUND / no blockers with four
clear (no-operator-decision) fixes. All applied as `m14(review): …`:

1. **Cascade mutual-exclusion contract pinned (should-fix).** The
   combination matrix says `--cascade` / `--cascade-only` / `--interactive`
   are mutually exclusive, but only the `--cascade-dry-run --interactive`
   rejection was pinned. Added the parametrized test
   `test_archive_mutually_exclusive_cascade_flags_rejected` (3 cases:
   `--cascade --interactive`, `--cascade-only <glob> --interactive`,
   `--cascade --cascade-only <glob>`) asserting exit 2 + nothing written.
   GREEN-by-argparse-accident now (the flags don't exist → "unrecognized
   arguments" exit 2), exactly like the existing dry-run-rejects-interactive
   test; will correctly catch a missing/incomplete argparse
   mutually-exclusive group in Step 2.
2. **`--cascade-dry-run` + `--cascade-only` composition pinned
   (should-fix).** The documented filtered-preview-write-nothing
   composition had no test. Added
   `test_archive_cascade_dry_run_composes_with_cascade_only` on the
   two-relation tree (`--cascade-only "sub/**"` matches only
   `sub/alpha.md`, not root-level `beta.md`): preview names alpha but not
   beta, nothing moves, exit 0. RED now (argparse rejects the unknown
   flags → exit 2, test expects 0) — **+1 to the RED count**.
3. **Garbled exit-code cell fixed (nit, clear doc bug).** `cli.md` §exit
   codes `archive --cascade-dry-run` success cell `preview written
   nothing` → `preview only; writes nothing (exit 0)`. Bundled mirror
   `src/docs_cli/skill/references/cli.md` resynced byte-identical (`cp`);
   INDEX + frozen snapshot regenerated in lockstep.
4. **A5 fsync test tightened to match the contract (nit, consistency).**
   The A5 Decision says `atomic_write` fsyncs "the tmpfile (and its parent
   directory)". `test_atomic_write_fsyncs_before_rename` previously
   asserted only "fsync called at least once"; now it classifies each
   fsynced fd (via `os.fstat` + `stat.S_ISDIR`/`S_ISREG`) and pins that
   the set includes BOTH a regular file and a directory (≥ 2 calls).
   Parent-directory fsync is the correct durable-rename pattern. Stays RED
   until Step 2 implements the fsync.

**New RED baseline: 458 collected, 18 failed, 440 passed, 0 errors, 0
skips.** The 18 RED are the original 17 (A1×2, A2×2, A3×1, A4×1, A5×1,
A6×5, B1×5) plus the new composition test (item 2). The 3 mutex params
(item 1) are GREEN-by-argparse-accident. No collateral GREEN broke:
`test_skill_refs` byte-identity GREEN after the `cli.md` edit;
`test_index_output_matches_frozen_snapshot` GREEN (snapshot in lockstep).

## Phase 5 — Update Base Interfaces

**Objective.** Wire the argparse surface for the M14 (B1) cascade flag
set and declare the Phase-6 helpers, with no behaviour change beyond what
argparse pins.

**Actions.**

- Replaced the lone `archive --cascade` (store_true) with the four-flag
  set: a single `add_mutually_exclusive_group()` holding `--cascade`
  (store_true), `--cascade-only GLOB`, and `--interactive` (store_true);
  `--cascade-dry-run` (store_true) sits OUTSIDE the group so it can
  compose with `--cascade-only`. The `--cascade-dry-run + --interactive`
  rejection is an imperative guard in `_cmd_archive` (Phase 6).
- Declared `_resolve_new_root(args, start)` (A2 — a `docs: new:`-prefixed
  mirror of `_resolve_touch_root`) and `_cascade_set(doc, root)` (the pure
  one-hop `pairs-with`/`child-of` on-disk candidate set, no prompt).

**Results.** `docs archive --help` shows all four flags with the mutex
group rendered `--cascade | --cascade-only GLOB | --interactive`. Suite
still collects 458. The 3-param `test_archive_mutually_exclusive_cascade_flags_rejected`
goes GREEN by the real argparse mutex; the two dry-run/compose tests stay
RED pending the Phase-6 imperative guard + dry-run path.

## Phase 6 — Implement Core

**Objective.** Turn all 18 RED tests GREEN by implementing the contract.

**Actions (A5 first — every verb calls `atomic_write`).**

- **A5 `atomic_write`.** Writes the tmpfile via `os.open`/`os.write`,
  `os.fsync(fd)`'s it, closes, `tmp.replace(path)`, then `os.open` the
  parent dir `O_RDONLY` + `os.fsync(dir_fd)` wrapped in `try/except
  OSError: pass` (Windows portability — RQ#2). Content is `.encode()`'d
  UTF-8 so the golden byte-equality tests stay GREEN. The A5 test patches
  `cli.os.fsync` and classifies each fd via `os.fstat` — both a regular
  file and a directory are flushed.
- **A1 `_cmd_mv`.** Inserted a validate-all-first pre-flight
  `list(walk(root, config, predicate=...))` BEFORE `old_path.replace`. On
  `(MetadataError, VocabularyError)` → `docs: {exc}` + **exit 2** (NOT
  archive's 1 — RQ#8; the A1 test asserts 2).
- **A4.** Widened mv's rewrite-loop+reindex `except` and archive's
  edge-rewrite `except` to map `OSError` → exit 2 (`docs: mv:` /
  `docs: archive:` prefix; no traceback).
- **A2 `_cmd_new`.** Replaced the `find_root` cwd-fallback + `is_dir`
  check with `_resolve_new_root`; the exact refusal messages the tests
  assert (no `--root` & no ancestor → `… is not under a docs root with
  .docs.toml; refusing`; `--root` without `.docs.toml` → `--root … does
  not contain .docs.toml; refusing`). Bad-root exit becomes 2 (RQ#6).
- **A3 slug guard.** Reject an empty final segment: split the slug on the
  last `/` WITHOUT stripping a trailing slash, so `foo/` (final segment
  `""`) and `foo/.md` (slug `foo/.` → final segment `.`) are both caught.
  (The planning note's `rstrip("/")` would have missed `foo/`; the
  no-rstrip split is the correct robust check and the A3 test confirms
  it.)
- **A6 (four verbs, every walk/reindex — RQ#1).** `predicate =
  compile_exclude_predicate(config, [])` per verb threaded into: touch
  reindex; archive pre-flight walk + `_rewrite_referring_edges` +
  reindex; mv pre-flight + rewrite-loop + reindex; project-rename
  validate walk + reindex. `_rewrite_referring_edges` gained an optional
  `predicate` param (the plan's "four sites" needed this fifth thread —
  the archive A6 test failed until the referring-edge walk also honoured
  the predicate). No other signature changes.
- **B1 non-interactive cascade.** `_cascade_set` (pure, one-hop, on-disk)
  + `_filter_cascade_set` (`--cascade-only` GLOB via
  `_compile_docsignore_pattern`, matched against the root-relative POSIX
  target — RQ#3) + `_print_cascade_footer` (success / dry-run / empty
  wording, STDERR — RQ#4). Imperative guard rejects `--cascade-dry-run +
  --interactive` (RQ#5) → 2. Dry-run path computes the filtered set,
  prints the preview + footer, writes nothing (primary NOT archived),
  exit 0. Mutate path: `_archive_one` the primary, then `--interactive` →
  legacy `_cascade_archive` (untouched), elif a cascade flag → `_archive_one`
  each filtered member + footer (no prompt, no stdin), else nothing; then
  `_rewrite_referring_edges` + reindex.

**Collateral fixed (not in the plan).** `tests/test_body_from.py`'s inline
`_minimal_tree` helper created a bare directory with NO `.docs.toml` and
passed it via `--root`. The A2 contract (correctly) now refuses a `--root`
that lacks `.docs.toml`, so all 7 body_from tests went RED. They exercise
`--body-from` semantics, not root resolution, so the helper gained a
minimal valid `.docs.toml` — a fixture lockstep update (same category as
the Phase-7 packaging version-string lockstep), preserving every
`--body-from` assertion. Surfaced for the audit.

**Results.** Targeted run (mv/new/archive/touch/project-rename/atomic_write)
all GREEN; full suite **458 passed, 0 failed** — all 18 prior RED now
GREEN, no regressions.

## Phase 7 — Update Wrappers

`pyproject.toml` version 1.5.0 → 1.6.0 (the single version source;
`__version__` reads it via `importlib.metadata`); `pip install -e .` so
the dev venv reports 1.6.0. `CHANGELOG.md` `## 1.6.0 — UNRELEASED`
section authored (Added: B1; Changed: A2/A5/A6; Fixed: A1/A4/A3/C3/C1
guard) — M15 appends its authoring entries to this same section; M17
publishes. `tests/test_packaging.py`: the four version-string assertions
(`test_a3`/`test_b1`/`test_b2`/`test_c2`) moved to 1.6.0 in lockstep with
the bump, with the `_1_6_0` function-name renames; `test_b3` (C3
wheel-contents guard) untouched. Bundled skill refs needed NO resync (no
`cli.md`/`convention.md` edits in Phase 6/7) — `test_skill_refs`
byte-identity GREEN. Full suite **458 passed**.

## Phase 8 — Run Tests GREEN + tree-wide quality gate

`.venv/bin/python -m pytest tests/ -q` → **458 collected, 0 failed.**
Tree-wide gate clean: `ruff check .`, `ruff format --check .`, `mypy` all
pass. The pre-existing M16 ruff failure
(`tests/test_skill_quality_artifacts.py`, I001 + format, from commit
9ceb113) was fixed with a mechanical `ruff check --fix` + `ruff format`
in a **separate, clearly-labelled commit** (`m14(phase 8): ruff autofix
…`); no assertions changed (only an import-block blank line and
call/assertion line-wrapping), M16 tests still GREEN.
`docs check docs/` exit 0; `docs index --root docs/ --dry-run` no diff.

## Phase 9 — Integrate / dogfood (throwaway copies)

All four scenarios on `mktemp -d` copies (the repo's real `docs/` only
read-only via `docs check`):

1. **`archive --cascade`** on a copy of `tests/fixtures/trees/cross-refs`
   (`helper.md --cascade --date 2026-05-28`, NO stdin): exit 0, no `[y/N]`
   prompt, footer `docs: cascade archived 1 related doc(s): core.md`, both
   `helper.md` + `core.md` under `archive/2026-05-28/`. Repeat with
   `--cascade-dry-run`: nothing moved (no `archive/` dir), preview named
   `core.md`, exit 0.
2. **`docs new spec my-feature`** from an orphan dir (no `.docs.toml`
   ancestor, no `--root`): exit 2, `docs: new: … is not under a docs root
   with .docs.toml; refusing`, no `my-feature.md` written.
3. **`docs touch spec.md`** over a tree with `[exclude] dirs = ["vendor"]`
   + malformed `vendor/README.md`: exit 0, `spec.md` `Updated:` bumped to
   2026-06-02, INDEX refreshed, `vendor/README.md` absent from INDEX +
   byte-unchanged, `spec.md` indexed.
4. **`docs check docs/`** exit 0.

No code commit (dogfood is verification).

## Phase 10 — Quality, Docs, Refactor

Closeout. `/simplify`-style review of the cascade refactor: `_cascade_set`
/ `_filter_cascade_set` / `_print_cascade_footer` earn their keep (shared
by the dry-run preview and the mutate path, keeping the no-prompt logic
DRY and obvious). Removed a dead dry-run branch (`elif args.cascade and
args.interactive` — unreachable because `--cascade`/`--interactive` are
argparse-mutex; no test/doc referenced its `--interactive would prompt
for …` string) — behaviour-preserving; archive tests stay GREEN.
Milestone + impl-log + status.md + plan.md flipped to
implementation-complete; INDEX + frozen snapshot regenerated in lockstep;
edited docs' `Updated:` bumped via `docs touch`.

Second `/simplify` pass (`m14/simplify`): `_cascade_set` and
`_filter_cascade_set` were always invoked as the pair
`_filter_cascade_set(_cascade_set(doc, root), cascade_only)` (two call
sites, dry-run preview + mutate path) and `_cascade_set` was never used
standalone — an abstraction layer that did not earn its keep. Merged into
one `_cascade_set(doc, root, cascade_only)` that compiles the
`--cascade-only` glob once up front and skips non-matching targets inside
the same edge walk. Same result set (glob ∩ on-disk-exists is order-
independent), same iteration order; two call sites drop from a nested
two-call composition to a single call. `_print_cascade_footer` kept (genuine
two-site sharing of three message variants). Behaviour-preserving: full
suite 459 passed / 0 failed; ruff / ruff format / mypy clean; `docs check
docs/` exit 0.

## Milestone completion summary

**M14 — Robustness + autonomous archive — implementation complete
(2026-06-02).**

**Shipped:**

- **Thread A (robustness):** A1 atomic `docs mv` (validate-all-first
  pre-flight, exit 2); A2 `docs new` strict-root refusal (no silent cwd
  write); A3 empty-segment slug rejection; A4 `OSError` in mv/archive
  edge-rewrite → clean exit 2; A5 `atomic_write` fsyncs the tmpfile + the
  parent directory before/after the rename (the `cli.md` "fsync'd" claim
  is now true); A6 the persistent `[exclude]` / `.docsignore` predicate
  threaded into EVERY walk / `_refresh_index` of all four mutating verbs
  (`touch`, `archive`, `mv`, `project rename`).
- **Thread B (autonomous archive):** B1 non-interactive
  `docs archive --cascade` flag set (`--cascade` / `--cascade-dry-run` /
  `--cascade-only GLOB` / `--interactive`); the invariant *`docs` never
  prompts unless `--interactive`* established; the legacy `[y/N]` prompt
  moved behind `--interactive`.
- **Thread C (packaging hygiene):** C3 — the false-confidence `test_a6`
  (pyproject-comment grep) removed; `test_b3` strengthened to assert the
  built wheel carries real skill package-data. C1 was already fixed by
  M16 (bundled reference links host-resolvable); M14 added the GREEN
  regression guard `test_bundled_skill_has_no_repo_relative_links` only.
- **C1 / `docs install-skill`** Success Criterion: satisfied by M16's
  self-contained references + the M14 GREEN guard (no repo-relative
  `../` links remain).

**Build / quality:** `docs-cli==1.6.0` **BUILT LOCALLY** (pyproject bump +
CHANGELOG section) — **NOT published**; the PyPI publish is **M17**
(mirrors the M12→M13 cadence). M15 appends its agent-native authoring
entries to the same 1.6.0 CHANGELOG section before M17 publishes. Full
suite **458 passed, 0 failed**; ruff / ruff format / mypy clean
tree-wide (incl. the mechanical M16 import-sort fix); `docs check docs/`
exit 0; INDEX + frozen snapshot in lockstep.

## Post-Step-2 review (2026-06-02)

A fresh-eyes review of Step 2 returned SOUND / no blockers / all Success
Criteria met, with two findings addressed here.

- **Finding 1 (should-fix) — archive A4 regression guard.** The archive
  half of the A4 contract ("`OSError` mid edge-rewrite in mv AND archive
  → clean exit 2, no traceback") shipped correctly and is documented
  (`cli.md` §archive + the exit-code matrix) but had ZERO test coverage —
  only the mv guard existed. Added
  `tests/test_cli_archive.py::test_archive_oserror_mid_rewrite_exits_2`,
  the archive analogue of
  `test_cli_mv.py::test_mv_oserror_mid_rewrite_exits_2`: a `0o555`
  read-only `locked/` dir holds `referrer.md` (`pairs-with: source.md`),
  so the post-move referring-edge rewrite's `atomic_write` raises
  `PermissionError` when it cannot create its `.docs-tmp` file. Asserts
  exit 2 + no `Traceback`, reusing the shared read-only-DIRECTORY trigger
  and `skipif (geteuid == 0)` idiom. GREEN immediately against shipped
  code (NOT a RED→GREEN cycle). Non-vacuousness verified: temporarily
  reverting the `_cmd_archive` `except OSError → return 2` clause makes
  the test go RED (uncaught `PermissionError` traceback, exit 1) at
  `_rewrite_referring_edges → atomic_write`; the clause was restored
  byte-exact. Suite now **459 passed, 0 failed** (the new test RAN —
  non-root).
- **Finding 2 (nit) — `atomic_write` write-all loop.** Hardened the core
  write primitive: replaced the single `os.write(fd, data)` with a
  write-all loop (`while written < len(data): written += os.write(fd,
  data[written:])`) so a short write cannot truncate (PEP 475 handles
  EINTR retries). The change is clean and keeps EVERY test GREEN —
  notably the A5 fsync test (`tests/test_atomic_write.py`, which patches
  `cli.os.fsync` and inspects fsync'd fds; the loop does not perturb it)
  and the golden byte-equality / INDEX frozen-snapshot tests.
