# M2 — Implementation Log

Lifecycle: archived
Role: log
Project: docs
Updated: 2026-05-21

Related:
- child-of: archive/2026-05-21/m2-mutating-verbs.md
- pairs-with: status.md

## Implementation metadata

- Project: docs
- Milestone: M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`)
- Started: 2026-05-21
- Progress: Phases 1–10 complete — **M2 shipped 2026-05-21**. Full suite green
  (112 passed); the verbs are dogfooded drift-free.

(Note: doc-lifecycle status is in the front-matter `Status:` field above. This
section tracks milestone progress, which is distinct.)

## Summary

Add the four mutating verbs — `new`, `archive`, `mv`, `touch` — so metadata is
written by the tool, never hand-edited. Every write is atomic. Reuses the M1
core (`atomic_write`, `parse`, `walk`, `render_index`); adds surgical
metadata-editing helpers and a renderer fix for nested-doc links.

## TDD Phase Progress

| Phase | Status | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-05-21 | 4 subparsers + 4 stub handlers + 3 editing-helper stubs in `bin/docs`; spec clarifications (`convention.md` subdirs, `cli.md` `new` semantics); date-fragile snapshot test repaired. |
| 2. Write Tests (RED) | Complete | 2026-05-21 | 52 M2 tests: 5 new test files + 1 renderer regression test. Collect cleanly. |
| 3. Create Data/Fixtures | Complete | 2026-05-21 | Two fixture trees: `cross-refs/` (3 docs, cross-`Related:`), `nested/` (active doc in a subdir). |
| 4. Run Tests (RED Baseline) | Complete | 2026-05-21 | 48 failed / 62 passed. Every M2 failure traces to `NotImplementedError` or a stub exit code. **Session paused here by request.** |
| 5. Update Base Interfaces | Complete | 2026-05-21 | Editing helpers + `_metadata_line_span` + renderer root-relative fix + `_refresh_index`. 77 passed / 33 failed (verb cores remain). |
| 6. Implement Offline/Core Path | Complete | 2026-05-21 | `_cmd_new` / `_cmd_touch` / `_cmd_archive` / `_cmd_mv` on the Phase 5 helpers. Full suite green: 110 passed. |
| 7. Update Tool/Wrapper Layer | Complete | 2026-05-21 | `archive --cascade` one-hop prompt (`_archive_one` / `_cascade_archive`) + 2 cascade tests. Exit codes & `--dry-run` parity already covered by Phase 6. 112 passed. |
| 8. Run Tests (GREEN) | Complete | 2026-05-21 | 112 passed; `ruff check`, `ruff format --check`, `mypy` all clean tree-wide. |
| 9. Implement Online/Integration | Complete | 2026-05-21 | Dogfooded `new` / `touch` / `mv` / `archive` against a copy of `docs/`; correct, drift-free, idempotent. |
| 10. Quality, Docs, Refactor | Pending | — | Close out: status.md, plan.md, completion summaries. |

## Current State Analysis (snapshot at milestone kickoff, 2026-05-21)

_Captured before Phase 1; historical. Post-milestone state lives in the
Milestone-completion summary at the bottom of this log._

- **Codebase:** `bin/docs` (~750 lines) shipped at M1 — parser, walker,
  renderer, `docs index`, config. 58 passing tests across 5 files.
- **Reuse available:** `atomic_write`, `parse`, `parse_metadata_block`, `walk`,
  `render_index`, `load_config`, `find_root` — all tested. The `argparse`
  harness in `_build_parser()` / `main()` extends with one subparser per verb.
- **Gap:** M1 only *reads* metadata. There is no serializer / metadata editor.
- **Pre-existing fragility:** `test_index_output_matches_frozen_snapshot` fails
  on any day but 2026-05-20 (the snapshot bakes `date.today()`).

## Files to Create / Modify

| File | Action | Phase | Notes |
|---|---|---|---|
| `bin/docs` | Modify | 1, 5, 6, 7 | M2 subparsers + stub handlers + helper stubs (P1); editing helpers + renderer fix + `_refresh_index` (P5); verb cores (P6); CLI wiring (P7). |
| `docs/m2-mutating-verbs.md` | Create | 1 | This milestone's task plan. |
| `docs/m2-mutating-verbs-log.md` | Create | 1 | This log. |
| `docs/convention.md` | Modify | 1 | New "Subdirectories" section; `Updated` bumped. |
| `docs/cli.md` | Modify | 1 | `docs new` slug/placement semantics pinned; `Updated` bumped. |
| `docs/status.md` | Modify | 1, …, 10 | M2 phase tracking; M2 → Complete at Phase 10. |
| `docs/INDEX.md` | Regenerate | 1, 9 | Picks up the two new M2 docs. |
| `docs/architecture.md` | Modify | 5 | INDEX renderer-format subspec: entry link is the root-relative path. |
| `docs/plan.md` | Modify | 10 | Record the `--cascade` decision + INDEX-grouping deferral. |
| `tests/test_cli_index.py` | Modify | 1, 2 | Date-fragile snapshot test repaired (P1); nested-doc link regression test (P2). |
| `tests/fixtures/expected/docs-INDEX.md` | Modify | 1 | Re-synced after the two M2 docs were added to `docs/`. |
| `tests/test_edit.py` | Create | 2 | Editing-helper unit tests (14). |
| `tests/test_cli_new.py` | Create | 2 | `docs new` CLI tests (13). |
| `tests/test_cli_touch.py` | Create | 2 | `docs touch` CLI tests (7). |
| `tests/test_cli_archive.py` | Create | 2 | `docs archive` CLI tests (10). |
| `tests/test_cli_mv.py` | Create | 2 | `docs mv` CLI tests (7). |
| `tests/fixtures/trees/cross-refs/` | Create | 3 | Three docs with cross-`Related:` refs, for `mv`. |
| `tests/fixtures/trees/nested/` | Create | 3 | An active doc in a subdir, for the renderer link regression test. |

## Pre-Phase-1 design note (subdirectories, a renderer bug, scope)

M2 kicked off with a design conversation that reshaped the milestone. Recorded
here because the conclusions drive several Phase 1 decisions.

**Question raised:** `cli.md` said `docs new` writes `<slug>.md` "in the active
tree" but never named *which directory*. Flat root, or current directory, or
nested? And: would a flat tree be hard for humans to navigate?

**Survey of the host's real docs trees:**

- This project's `docs/` — 14 files, completely flat.
- `~/validaitor/langfuse-data/docs/` — mostly flat, plus `brainstorms/` and
  `plans/` role-bucket subdirs.
- `~/validaitor/ValidaitorLLM/backend/agents/docs/` — `specs/` holds one
  effort's docs flat; `project-history/<effort>/` is one subdir per past
  effort (~25 of them).

**Conclusions:**

1. Subdirectories serve three real purposes — the machine-managed
   `archive/<date>/`; role bucketing (which the convention's `Role:` metadata
   + grouped INDEX deliberately *replaces*); and per-effort bundling (better
   modeled as separate roots). None is something `docs new` must target — but
   the tool already walks subdirs (`walk` recurses) and `docs mv` already
   targets them, so `docs new` forbidding nested slugs would be the
   inconsistent choice. **Decision: `docs new` allows nested slugs, flat into
   the resolved root by default, with guardrails** (reject `..`/absolute,
   reject under `archive_dir`).

2. **A real renderer bug surfaced.** `_format_entry` links docs by
   `doc.path.name` (basename). A dry-run against the `with-archive` fixture
   showed `archive/2026-01-01/old-plan.md` rendered as `[old-plan.md](old-plan.md)`
   — a broken link. Every archived doc, every doc in a subdir, gets a broken
   INDEX link. `docs archive` (this milestone) *creates* `archive/<date>/`
   subdirs and regenerates the INDEX as its last step, so it would emit broken
   links on first use. **The fix (root-relative paths) is therefore in M2
   scope — Phase 5.**

3. **Human navigation at scale** is a real gap, but it is an INDEX *view*
   concern (grouping by directory or `Project:`), not a mutating-verb concern.
   **Deferred to M3** — recorded for `plan.md` at Phase 10.

The convention's silence on non-archive subdirectories caused the original
ambiguity; Phase 1 closes it with a new `convention.md` section.

## Phase logs

### Phase 1 — Define Contract

**Completed:** 2026-05-21

#### Objective
Declare the full M2 surface in `bin/docs` — four subparsers, four stub command
handlers, three editing-helper stubs — with no business logic. Land the spec
clarifications the pre-Phase-1 discussion called for. Repair the pre-existing
date-fragile snapshot test so the RED baseline starts from a green M1 suite.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `bin/docs` | Modify | `__version__` → `0.2.0-m2`; module docstring refreshed. New "Doc-editing helpers (M2)" section with `set_metadata_field`, `rewrite_related_refs`, `scaffold_doc` (signatures + docstrings; `NotImplementedError` bodies). `_build_parser()` gains a shared `common` parent parser (`--root`, `--quiet`, `--dry-run`) and four subparsers. Four `_cmd_*` stub handlers. `main()` dispatch extended. |
| `docs/convention.md` | Modify | New "Subdirectories" section; `Updated` → 2026-05-21. |
| `docs/cli.md` | Modify | `docs new` slug/placement semantics pinned (flat into root, nested slugs allowed, guardrails, `.md`-suffix stripping); `Updated` → 2026-05-21. |
| `docs/m2-mutating-verbs.md` | Create | Milestone task plan (ten phases). |
| `docs/m2-mutating-verbs-log.md` | Create | This log. |
| `tests/test_cli_index.py` | Modify | `_normalize_generated_date` helper; snapshot test compares date-normalized text. |

#### Actions taken

- Added the four subparsers via a shared `common` parent parser
  (`add_help=False`) for `--root` / `--quiet` / `--dry-run`. The M1 `index`
  subparser keeps its own copies — folding it into `common` is a Phase 7
  cleanup, explicitly out of scope for a contract phase.
- Each verb's positionals and verb-specific flags are declared per `cli.md`:
  `new` (`role`, `slug`, `--project`, `--title`); `archive` (`file`,
  `--reason`, `--date`, `--cascade`); `mv` (`old`, `new`); `touch` (`file`).
- Stub handlers raise `NotImplementedError("_cmd_X() — Phase 6")`; the editing
  helpers raise `NotImplementedError("… — Phase 5")`.
- Spec edits per the pre-Phase-1 design note.
- Verified `docs --help` lists all five subcommands; each verb parses its args
  and then exits non-zero on the stub.

#### Issues / decisions

- **Shared `common` parent parser.** M1's Phase 7 log anticipated this ("When
  M2 adds more subcommands, refactor to a parent parser if they share flags").
  Done for the four new verbs; `index` left untouched to keep Phase 1 a pure
  contract change.
- **`--cascade` declared as a plain `store_true`.** `plan.md`'s open question
  (cascade-as-default vs opt-in) is unresolved; a plain boolean flag keeps the
  polarity a one-line change if Phase 6 flips it.
- **Date-fragile snapshot test.** `test_index_output_matches_frozen_snapshot`
  byte-compared a committed snapshot whose `_Generated YYYY-MM-DD._` summary
  line is stamped with `date.today()` — so it failed every day but 2026-05-20.
  M1's Phase 6 log flagged this as "acceptable risk … sensitive on day
  boundaries"; M2 makes it robust. The fix normalizes only that one line
  (`_normalize_generated_date`), so the test still asserts the full INDEX
  structure — just not the wall clock. Repairing it in Phase 1 means the
  Phase 4 RED baseline starts from a genuinely green M1 suite.
- **Spec `Updated` bumps.** `convention.md` and `cli.md` were meaningfully
  edited, so their `Updated:` moved to 2026-05-21. This (plus the two new M2
  docs) changes the generated INDEX, so `docs/INDEX.md` and the dogfood
  snapshot were regenerated in lockstep (see Phase 4).

#### Exit criteria

- [x] Four subparsers + four stub handlers + three helper stubs in `bin/docs`.
- [x] `docs --help` lists all five subcommands; each verb is reachable.
- [x] `ruff check` / `ruff format --check` / `mypy` clean on `bin/docs`.
- [x] Spec clarifications landed in `convention.md` and `cli.md`.
- [x] Date-fragile snapshot test repaired.
- [x] Ready for Phase 2 to write failing tests against the contract.

### Phase 2 — Write Tests (RED)

**Completed:** 2026-05-21

#### Objective
Express every M2 behavior as a failing test, before any implementation.

#### Files changed

| File | Action | Tests |
|---|---|---|
| `tests/test_edit.py` | Create | 14 — `set_metadata_field` (replace, insert-if-missing, body-line non-match, trailing-newline preservation, raises without a block); `rewrite_related_refs` (rewrite, verb preserved, no-op, multi-match); `scaffold_doc` (round-trips through `parse`, omits `Project` when None, single trailing newline). |
| `tests/test_cli_new.py` | Create | 13 — file creation, metadata scaffold, title default vs `--title`, `--project`, invalid role (exit 2), existing file (exit 1), no INDEX refresh, `--dry-run`, nested slug, root-escape rejection. |
| `tests/test_cli_touch.py` | Create | 7 — bumps `Updated:`, preserves other bytes, regenerates INDEX, idempotent, missing file (exit 1), `--dry-run`. |
| `tests/test_cli_archive.py` | Create | 10 — move to `archive/<date>/`, original removed, `Status: archived`, `Updated` bumped, `--reason`, `--date`, INDEX regen, `--dry-run`, missing file. |
| `tests/test_cli_mv.py` | Create | 7 — rename in place, move into a subdir, tree-wide `Related:` rewrite, collision (exit 1), INDEX regen, `--dry-run`. |
| `tests/test_cli_index.py` | Modify | +1 — `test_index_nested_doc_link_is_root_relative` (renderer regression). |

Total: 52 new M2 tests (110 in the suite).

#### Actions taken

- Unit tests in `test_edit.py` use inline-string fixtures and call the helpers
  directly, asserting the byte-preservation contract.
- CLI tests follow the M1 pattern exactly: a local `_run()` subprocess helper
  (`sys.executable` + script path) and `shutil.copytree` of a fixture tree
  into `tmp_path`.
- The renderer regression test is a CLI test (in `test_cli_index.py`) rather
  than a `render_index` unit test — that keeps it from pre-committing the
  Phase 5 internal API (thread `root` vs add a `Doc.relpath` field).

#### Issues / decisions

- **False-pass avoidance.** Tests asserting a *specific* non-zero exit code
  (`new` existing-file → 1, `mv` collision → 1, `touch`/`archive` missing-file)
  would pass against a stub that exits 1 via `NotImplementedError`. Each such
  test additionally asserts a stderr substring the real implementation will
  emit ("exist", "not found") and the stub's traceback will not — so they
  RED-fail honestly. Verified in Phase 4.
- **`mv` reference assertions check the `Related:` line, not the bare
  filename.** A fixture body may legitimately mention a filename in prose;
  `rewrite_related_refs` only touches the metadata block. The assertions check
  `pairs-with: core.md` is gone / `pairs-with: core-engine.md` is present,
  not that the substring `core.md` never appears.
- **`--help` tests pass at the RED baseline.** Because Phase 1 declared the CLI
  surface, `docs <verb> --help` works. The four help tests are contract
  tests — a legitimate pass, not a false pass (see Phase 4).

#### Exit criteria

- [x] 110 tests collect without import or fixture-path errors.
- [x] Every M2 test fails with `NotImplementedError` or a stub exit code.
- [x] Tests reuse the conftest-loaded `docs` module and the M1 subprocess idiom.
- [x] Ready for Phase 3 (fixtures) → Phase 4 (RED baseline).

### Phase 3 — Create Data/Fixtures

**Completed:** 2026-05-21

#### Objective
Build the fixture trees the Phase 2 tests reference, so the only cause of
failure at Phase 4 is missing implementation.

#### Files changed

| File | Action | Notes |
|---|---|---|
| `tests/fixtures/trees/cross-refs/.docs.toml` | Create | Root marker, project `cross-refs`. |
| `tests/fixtures/trees/cross-refs/core.md` | Create | Active spec — the doc `mv` tests rename. |
| `tests/fixtures/trees/cross-refs/helper.md` | Create | Active spec with `Related: pairs-with: core.md`. |
| `tests/fixtures/trees/cross-refs/overview.md` | Create | Active notes with `Related: references: core.md` and `references: helper.md` — confirms `mv` rewrites every match and leaves non-matches alone. |
| `tests/fixtures/trees/nested/.docs.toml` | Create | Root marker, project `nested`. |
| `tests/fixtures/trees/nested/root-doc.md` | Create | Active doc at the root. |
| `tests/fixtures/trees/nested/topics/deep-dive.md` | Create | Active doc in a subdirectory — exercises the renderer root-relative-link fix. |

Existing `trees/minimal/` and `trees/with-archive/` are reused for
`new`/`touch`/`archive` tests; helper unit tests use inline strings only.

#### Issues / decisions

- **`cross-refs/` has two inbound references to `core.md`** (from `helper.md`
  and `overview.md`), one of three different verbs, so the `mv` rewrite test
  proves the rewrite is tree-wide and verb-agnostic. `overview.md`'s second
  reference (`references: helper.md`) stays put — a negative control.

#### Exit criteria

- [x] Every fixture path referenced by a Phase 2 test exists.
- [x] Fixtures follow the M1 fixture format (`.docs.toml` + well-formed docs).
- [x] Ready for Phase 4: run pytest and capture the RED baseline.

### Phase 4 — Run Tests (RED Baseline)

**Completed:** 2026-05-21

#### Objective
Confirm every M2 test fails for the right reason — missing implementation, not
misconfiguration. Log-only; no implementation. **The milestone pauses here for
this session by request; Phase 5 resumes implementation.**

#### Command + summary

```
.venv/bin/python -m pytest tests/ -q
=========================== 48 failed, 62 passed in ~1.7s ===========================
```

110 tests collected, no collection / import / fixture-path errors.

#### Failure attribution

- **`test_edit.py` (14)** — all fail with `NotImplementedError` from the
  helper stubs.
- **CLI verb tests (44 of 48)** — the `_cmd_*` stub raises `NotImplementedError`
  inside the subprocess → exit 1 → the test's exit-code/stderr assertions fail.
- **`test_index_nested_doc_link_is_root_relative`** — fails because the M1
  renderer still links by basename (`(deep-dive.md)`, not
  `(topics/deep-dive.md)`). Goes green when Phase 5 lands the renderer fix.

No failure traces to an import error, a fixture-path error, or a misconfigured
test.

#### The 62 baseline passes

- **58 — M1's suite**, all green. The Phase 1 snapshot-test repair removed the
  date fragility; `docs/INDEX.md` and `tests/fixtures/expected/docs-INDEX.md`
  were regenerated in lockstep so the snapshot reflects `docs/` with the two
  new M2 docs added.
- **4 — the M2 `--help` tests** (`new`/`archive`/`mv`/`touch`). These pass
  because Phase 1 declared the CLI surface; they are contract tests, a
  legitimate pass. (M1's Phase 4 had an analogous set of baseline passes.)

The exit-code tests that could have *false*-passed against a stub that exits 1
(`new` existing-file, `mv` collision, `touch`/`archive` missing-file) were
confirmed to fail on their stderr-substring assertions — no false passes.

#### Exit criteria

- [x] All M2 failures attributable to missing implementation.
- [x] No false passes among the exit-code tests.
- [x] M1's 58 tests green (snapshot repaired + regenerated in lockstep).
- [x] No code implemented (contract/tests/fixtures only).
- [x] Ready for Phase 5: implement the editing helpers and the renderer fix.

### Phase 5 — Update Base Interfaces

**Completed:** 2026-05-21

#### Objective
Implement the shared pure helpers the mutating verbs compose, and fix the
renderer so docs in subdirectories get working INDEX links. Logic only — the
four `_cmd_*` handlers stay stubbed until Phase 6.

#### Files changed
- `bin/docs` — `_metadata_line_span` (new), `parse_metadata_block` (refactored
  to consume it), `set_metadata_field` / `rewrite_related_refs` / `scaffold_doc`
  (implemented), `_format_entry` / `render_index` (thread `root`),
  `_refresh_index` (new), `_cmd_index` (restructured).
- `tests/test_index.py` — thread `root` through the 15 `render_index` calls.
- `architecture.md` — INDEX "Entry format" subspec now specifies the
  root-relative POSIX path; `Updated:` bumped to 2026-05-21.
- `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md` — regenerated in
  lockstep (only `architecture.md`'s `Updated` line moved).

#### Actions taken
- Extracted `_metadata_line_span` as the single source of metadata-block
  boundary detection; `parse_metadata_block` now layers the dict + body on
  top of it, so the parser and the editing helpers cannot drift.
- The editing helpers do surgical, minimal-diff edits: they splice
  `splitlines(keepends=True)` so line endings and the trailing-newline state
  survive byte-for-byte. `set_metadata_field` replaces an inline value in
  place or inserts a line at the end of the inline run; `rewrite_related_refs`
  rewrites matching `Related:` bullet targets and preserves the verb;
  `scaffold_doc` is a pure builder that round-trips through `parse()`.
- The renderer threads the docs `root` through `render_index` →
  `_format_entry`, emitting the root-relative POSIX path for both the link
  text and the href. The within-section sort tiebreaker was aligned to the
  same root-relative path (`architecture.md` already specified it).
- `_refresh_index(root, config)` was extracted from `_cmd_index`'s write path
  for the verbs to reuse; `_cmd_index` keeps its `--dry-run` branch inline.

#### Issues / decisions
- `render_index` takes `root` as a required parameter (not optional with a
  basename fallback) — a renderer that needs `root` to be correct should
  require it. Cost: the 15 `test_index.py` call sites got a mechanical
  `root=_ROOT`.
- `architecture.md`'s `Updated:` was bumped and both INDEX snapshots
  regenerated within this phase, so the Phase 5 commit leaves the tree
  convention-consistent rather than deferring reconciliation to Phase 9.

#### Exit criteria
- [x] `test_edit.py` green (14).
- [x] `test_index_nested_doc_link_is_root_relative` green.
- [x] The seven other `test_cli_index.py` tests green after the renderer refactor.
- [x] `test_index.py` (15) and all M1 tests green.
- [x] Tree-wide gates clean: `ruff check`, `ruff format --check`, `mypy`.
- [x] Suite: 77 passed / 33 failed — the 33 are the verb-core CLI tests
      (Phases 6–7); 15 tests flipped green vs. the Phase 4 baseline.

### Phase 6 — Implement Offline/Core Path

**Completed:** 2026-05-21

#### Objective
Implement the four verb cores on top of the Phase 5 helpers.

#### Files changed
- `bin/docs` — `_cmd_new`, `_cmd_touch`, `_cmd_archive`, `_cmd_mv` implemented;
  `_slug_to_title` helper added.

#### Actions taken
- `_cmd_new` — resolves the root, validates the role against the config
  vocabulary (exit 2), resolves the slug to a path under the root (strips a
  trailing `.md`; rejects absolute paths, `..`, and the archive subtree —
  exit 2), rejects an existing file (exit 1), scaffolds via `scaffold_doc`,
  and creates any intermediate directories. Does not refresh the INDEX.
- `_cmd_touch` — bumps `Updated:` via `set_metadata_field` (surgical, so the
  body and every other line survive byte-for-byte), then `_refresh_index`.
- `_cmd_archive` — validates required metadata via `parse`, edits `Status` →
  archived and bumps `Updated:` (plus optional `Archived-reason:`), then moves
  the doc to `<archive_dir>/<date>/` and refreshes the INDEX. The edit lands
  before the move, so a failure leaves the original untouched. `--date`
  controls both the bumped date and the dated directory.
- `_cmd_mv` — rejects a collision (exit 1), moves the doc (creating any
  intermediate directory), rewrites every matching `Related:` bullet target
  across the tree via `rewrite_related_refs`, then refreshes the INDEX.
- `--dry-run` short-circuits all four verbs after validation, before any
  write or move.

#### Issues / decisions
- `archive --cascade` (the one-hop pairs-with / child-of prompt) is declared
  but left as a no-op for Phase 6 — the interactive prompt is Phase 7 scope.
  It has no test, so the suite is green without it.
- `touch` / `archive` / `mv` resolve the docs root by walking up from the
  target file (`find_root`), since the CLI tests invoke them without `--root`.

#### Exit criteria
- [x] `test_cli_new.py`, `test_cli_touch.py`, `test_cli_archive.py`,
      `test_cli_mv.py`, `test_edit.py` green.
- [x] Full suite green: 110 passed (was 77 passed / 33 failed after Phase 5).
- [x] Tree-wide gates clean: `ruff check`, `ruff format --check`, `mypy`.

### Phase 7 — Update Tool/Wrapper Layer

**Completed:** 2026-05-21

#### Objective
Finalize the CLI: the `archive --cascade` interactive prompt. Exit-code
mapping, `--dry-run` parity, and error messages were already implemented and
tested in Phase 6.

#### Files changed
- `bin/docs` — `_archive_one` and `_cascade_archive` helpers (new);
  `_cmd_archive` refactored to use them; `_CASCADE_VERBS` constant.
- `tests/test_cli_archive.py` — `_run` gains a `stdin_text` parameter;
  `_crossrefs_tree` helper + two `--cascade` tests (prompt yes / no).

#### Actions taken
- `_archive_one` factors out the single-doc archive (edit `Status` / `Updated`
  / optional `Archived-reason`, write atomically, move into the dated dir) so
  the main doc and every cascaded doc share one code path.
- `_cascade_archive` walks the archived doc's `pairs-with` / `child-of`
  relations (one hop only), prompts `also archive <target>? [y/N]` on stderr,
  reads the answer from stdin, and archives each confirmed doc into the same
  dated directory. Declined or failing docs are left in place.
- The Phase 2 test plan listed a `--cascade` test that was never written;
  Phase 7 adds it — two subprocess tests feeding `y\n` / `n\n` on stdin.

#### Issues / decisions
- A declined or unreadable related doc is skipped, not fatal — cascade is
  best-effort, and the resulting drift is what `docs check` (M3) is for.
- On EOF / empty stdin the prompt defaults to "no", so a non-interactive
  `--cascade` invocation never blocks and never archives unconfirmed docs.

#### Exit criteria
- [x] `docs <verb> --help` works for all four verbs.
- [x] Every CLI test green, including the two new `--cascade` tests.
- [x] Full suite green: 112 passed. Tree-wide gates clean (ruff, mypy).

### Phase 8 — Run Tests (GREEN)

**Completed:** 2026-05-21

#### Objective
Confirm the full suite passes and the quality gates are clean tree-wide.

#### Command + summary

```
.venv/bin/pytest -q             -> 112 passed
.venv/bin/ruff check .          -> All checks passed!
.venv/bin/ruff format --check . -> 12 files already formatted
.venv/bin/mypy                  -> Success: no issues found in 12 source files
```

#### Exit criteria
- [x] 112 passed, 0 failed — the four verbs and the shared helpers all green.
- [x] `ruff check`, `ruff format --check`, and `mypy` clean tree-wide.

### Phase 9 — Implement Online/Integration (dogfood pass)

**Completed:** 2026-05-21

#### Objective
Exercise the four verbs end-to-end against a copy of this repo's own `docs/`
tree and confirm the result is correct, drift-free, and idempotent.

#### Actions taken
Copied `docs/` to a scratch directory and ran:
- `docs new spec dogfood-throwaway --title …` — flat doc created with
  `Status: draft` and today's `Updated:`; `docs new notes topics/sub-note`
  created the nested doc and its directory; `docs new spec charter` (an
  existing slug) exited 1.
- `docs touch charter.md` — `Updated:` bumped to today, every other line
  byte-identical; a second `touch` produced no change (idempotent).
- `docs mv cli.md cli-spec.md` — file renamed; all 7 `Related:` bullets that
  pointed at `cli.md` rewritten to `cli-spec.md` across the tree, 0 stale
  `Related:` bullets left.
- `docs archive dogfood-throwaway.md --reason …` — moved into
  `archive/2026-05-21/`, `Status: archived`, `Archived-reason:` recorded; the
  regenerated INDEX links it by its root-relative path
  (`archive/2026-05-21/dogfood-throwaway.md`).
- `docs index` run twice — byte-identical output (idempotent).

#### Issues / decisions
- `docs mv` rewrites `Related:` metadata bullets only — prose markdown links
  such as `[cli.md](cli.md)` in doc bodies are left untouched. This is the
  documented contract (cli.md: "rewrite every `Related:` reference"): the
  `Related:` block is the machine-tracked edge; prose mentions are not.
  Stale prose links after a rename are drift that `docs check` (M3) surfaces.
  Recorded here as the intentional, documented surviving diff for Phase 9.
- The dogfood ran against a scratch copy; the repo's own `docs/` tree was
  untouched (`git status` clean).

#### Exit criteria
- [x] All four verbs produce correct, drift-free state on a real tree.
- [x] Idempotency confirmed for `touch` and `index`.
- [x] The one surviving diff (prose links after `mv`) documented as intentional.

### Phase 10 — Quality, Docs, Refactor

**Completed:** 2026-05-21

#### Objective
Close out M2: final quality gate, record the deferred decisions, write the
milestone-completion summaries.

#### Files changed
- `docs/plan.md` — resolved the `--cascade` and INDEX-excerpt open questions;
  added the directory- / `Project`-grouped INDEX deferral as a new M3 open
  question.
- `docs/status.md` — M2 → Complete; M3 set as the next milestone.
- `docs/m2-mutating-verbs.md` — Deliverables, Phase Checklist, and Success
  Criteria all ticked; milestone-completion summary filled in.
- `docs/m2-mutating-verbs-log.md` — this entry and the summary below.
- `docs/INDEX.md`, `tests/fixtures/expected/docs-INDEX.md` — regenerated in
  lockstep (`plan.md`'s `Updated:` moved 2026-05-20 → 2026-05-21).

#### Issues / decisions
- **`--cascade` stays opt-in.** Phase 6 left it as a `store_true`; Phase 7
  implemented the prompt. Making it default-on would archive a doc's
  neighbours as a surprise side effect. Recorded in `plan.md`.
- **`bin/docs` stays single-file.** It is ~1.3k lines — large, but sectioned
  with header comments and clean under `ruff` / `mypy`. The milestone's
  Decisions deferred the split to M3 "unless it becomes unworkable"; it has
  not, so no split this milestone.
- **M3 is "Next", not "ACTIVE".** The plan said "M3 → ACTIVE", but M3 has no
  plan doc yet and the project gates implementation on a ready milestone doc.
  `status.md` marks M2 Complete and M3 as the next milestone to be planned.

#### Exit criteria
- [x] Quality gate green: 112 passed; `ruff` + `mypy` clean.
- [x] `plan.md` records the `--cascade` decision and the INDEX-grouping deferral.
- [x] `status.md` reflects M2 → Complete, M3 → Next.
- [x] Milestone-completion summaries written here and in the plan.

## Milestone-completion summary

M2 shipped 2026-05-21. Ten TDD phases, committed per phase on `main` (Phases
1–4 batched at kickoff, 8–9 combined, the rest individually). Final state: 112
tests passing, `ruff` and `mypy` clean tree-wide, the four verbs dogfooded
drift-free against a copy of `docs/`.

Per-phase detail is in the phase logs above; the milestone summary and the
recorded decisions live in [m2-mutating-verbs.md](m2-mutating-verbs.md) and
[plan.md](plan.md). Next milestone: M3 — Validation and query (`check`,
`list`).
