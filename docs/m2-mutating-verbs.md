# M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`)

Status: active
Role: milestone
Project: docs
Updated: 2026-05-21

Related:
- parent-of: m2-mutating-verbs-log.md
- child-of: plan.md
- implements: charter.md
- pairs-with: convention.md
- pairs-with: cli.md
- pairs-with: architecture.md
- pairs-with: test-strategy.md

## Overview

- Milestone: M2
- Title: Mutating verbs (`new`, `archive`, `mv`, `touch`)
- Surface: four new CLI subcommands on the `docs` executable
- Status: ACTIVE (started 2026-05-21)

### Goal

Stop hand-editing metadata. M1 made the tree *readable*; M2 makes it *writable*
under the convention — scaffolding new docs, archiving completed ones, renaming
docs without breaking cross-references, and bumping timestamps. Every mutation
is atomic: a failure never leaves a partially-edited doc.

### Requirements

- `docs new <role> <slug>` scaffolds a file with a correct metadata block
  (`Status: draft`, `Role`, `Project`, `Updated`). Exit 2 on invalid role,
  1 on existing file. Does not refresh INDEX.
- `docs archive <file>` performs the dual-status dance atomically: edit
  (`Status: archived` + bump `Updated:`), move to `<archive_dir>/<date>/`,
  regenerate INDEX. `--reason`, `--date`, `--cascade` per [cli.md](cli.md).
- `docs mv <old> <new>` moves/renames a doc and rewrites every `Related:`
  reference that points at `<old>` across the whole tree. Exit 1 on collision.
- `docs touch <file>` bumps `Updated:` to today; regenerates INDEX.
- Atomicity: tmp file + rename for every write; archive moves only after the
  edit succeeds; INDEX regen runs last.
- `--dry-run` works on all four verbs.
- Exit codes per [cli.md](cli.md).

### Deliverables

- [ ] Four subcommands functional on `bin/docs`: `new`, `archive`, `mv`, `touch`.
- [ ] Shared editing helpers (`set_metadata_field`, `rewrite_related_refs`,
      `scaffold_doc`) — pure, unit-tested, reused across verbs.
- [ ] Renderer fix: `_format_entry` emits root-relative paths so nested docs
      (every archived doc, every doc in a subdir) get working INDEX links.
- [ ] `tests/test_edit.py`, `tests/test_cli_new.py`, `tests/test_cli_touch.py`,
      `tests/test_cli_archive.py`, `tests/test_cli_mv.py`.
- [ ] Fixture trees for cross-reference rewriting and archive moves.
- [ ] Dogfood: archiving and renaming this repo's own docs through M2 produces
      correct, drift-free state.
- [ ] All quality gates green tree-wide: `ruff check .`, `ruff format --check .`,
      `mypy`, `pytest -q`.
- [ ] `docs/status.md` updated to M2 complete + M3 active.

## Current state analysis (snapshot at milestone kickoff, 2026-05-21)

_Captured before Phase 1; historical. Post-milestone state lives in the
Milestone-completion summary at the bottom of this file._

- **Existing code:** `bin/docs` (~750 lines) shipped at M1 — parser, walker,
  renderer, `docs index`, config loading. `atomic_write`, `parse`,
  `parse_metadata_block`, `walk`, `render_index`, `load_config`, `find_root`
  are all available and tested.
- **Existing tests:** 58 (M1). One — `test_index_output_matches_frozen_snapshot`
  — fails on any day other than 2026-05-20 because the frozen snapshot bakes
  `date.today()` into the summary line. Pre-existing M1 fragility; M2 Phase 1
  repairs it (see Decisions).
- **Reuse map:** all four verbs reuse `atomic_write` (Phase 5 of M1) and
  `parse`/`walk` (Phase 6 of M1). `touch`/`archive`/`mv` reuse `render_index`
  for the INDEX refresh; the `argparse` harness in `_build_parser()` /
  `main()` extends with one subparser per verb.
- **Gap M1 left:** M1 only *reads* metadata. M2 must *write* it back. There is
  no doc serializer / metadata-editor yet — `parse_metadata_block` returns a
  lossy `dict`. M2 adds surgical line-editing helpers instead (see Decisions).
- **Renderer bug surfaced during M2 design:** `_format_entry` (`bin/docs:549`)
  links docs by basename (`doc.path.name`). Docs in subdirectories — every
  archived doc under `archive/<date>/` — therefore get broken INDEX links.
  `docs archive` (this milestone) creates exactly such subdirs, so the fix is
  in M2 scope (Phase 5).

## TDD Implementation Plan

The ten phases follow the fixed methodology in [status.md](status.md). Phases
1–4 establish the contract, tests, fixtures, and RED baseline with **no verb
implementation**; phases 5–10 implement and ship.

### Phase 1: Define Contract

- **Objective:** Declare the M2 surface. No business logic.
- **Files:**
  - `bin/docs` — four subparsers (`new`, `archive`, `mv`, `touch`) in
    `_build_parser()`; four stub handlers (`_cmd_new`, `_cmd_archive`,
    `_cmd_mv`, `_cmd_touch`) raising `NotImplementedError`; `main()` dispatch
    extended; stub signatures for `set_metadata_field`, `rewrite_related_refs`,
    `scaffold_doc`. Module docstring + `__version__` bumped to `0.2.0-m2`.
  - `docs/convention.md` — new "Subdirectories" subsection blessing free-form
    subdirs as a human organizing layer, distinct from the machine-managed
    `archive/`. (Spec clarification; the convention's silence on this caused a
    design ambiguity — see the milestone log's pre-Phase-1 design note.)
  - `docs/cli.md` — pin the `docs new` slug/placement semantics (writes flat
    into the resolved docs root; nested slugs allowed; guardrails).
  - `tests/test_cli_index.py` — repair the date-fragile snapshot test.
- **Exit:** Stubs import cleanly; `docs --help` lists all seven subcommands;
  each new verb parses its args then exits non-zero on `NotImplementedError`;
  pre-existing suite green (snapshot repair); spec edits committed.

### Phase 2: Write Tests (RED)

- **Objective:** Express every M2 behavior as a failing test.
- **Files:**
  - `tests/test_edit.py` — unit tests for `set_metadata_field` (replace,
    insert-if-missing, body-line non-match, trailing-newline preservation),
    `rewrite_related_refs` (rewrite, no-op, multi-match, verb preserved),
    `scaffold_doc` (round-trips through `parse`, omits `Project` when None).
  - `tests/test_cli_new.py` — role validation (exit 2), existing-file (exit 1),
    title default vs `--title`, project inference, nested slug, guardrails,
    `--dry-run`, no INDEX written.
  - `tests/test_cli_touch.py` — bumps `Updated:`, preserves other bytes,
    regenerates INDEX, idempotent, `--dry-run`, missing file.
  - `tests/test_cli_archive.py` — status edit + move to `archive/<date>/`,
    `--reason`, `--date`, atomicity (failure leaves original untouched),
    `--cascade` one-hop, `--dry-run`.
  - `tests/test_cli_mv.py` — rename, cross-dir move, tree-wide `Related:`
    rewrite, collision (exit 1), `--dry-run`.
  - `tests/test_cli_index.py` — one regression test: a nested active doc gets
    a root-relative INDEX link.
- **Exit:** All tests collect without import errors; fail with
  `NotImplementedError` (or wrong exit code / wrong link), not misconfiguration.

### Phase 3: Create Data/Fixtures

- **Objective:** Build the fixture trees referenced by Phase 2 tests.
- **Files:**
  - `tests/fixtures/trees/cross-refs/` — three docs that `Related:`-reference
    each other (for `mv`'s tree-wide rewrite), plus `.docs.toml`.
  - `tests/fixtures/trees/nested/` — an active doc in a subdirectory (for the
    renderer root-relative-link regression test).
  - Reuse `trees/minimal/` and `trees/with-archive/` for `new`/`touch`/`archive`.
- **Exit:** Every fixture path referenced by Phase 2 tests exists; `walk` over
  `cross-refs/` yields the expected docs with the expected `related` tuples.

### Phase 4: Run Tests (RED Baseline)

- **Objective:** Confirm every failure traces to missing implementation, not
  misconfiguration. Log-only; no commit. **This session pauses here.**
- **Actions:** `.venv/bin/python -m pytest tests/` — capture full output.
- **Exit:** Every M2 assertion failure traces to `NotImplementedError`, a
  wrong exit code from a stub, or the un-fixed renderer link. No `ImportError`,
  no fixture-path errors. M1's 58 tests (snapshot repaired) stay green.

### Phase 5: Update Base Interfaces

- **Objective:** Implement the shared pure helpers and the renderer fix.
- **Files:** `bin/docs`.
  - `set_metadata_field(text, label, value)` — surgical inline-line rewrite or
    insert; preserves every other byte.
  - `rewrite_related_refs(text, old_rel, new_rel)` — rewrite matching
    `Related:` bullet targets; returns `(text, count)`.
  - `scaffold_doc(title, role, project, updated, date_format)` — pure builder.
  - `_metadata_line_span(text)` — internal: locate the metadata block's line
    span, sharing `parse_metadata_block`'s detection rules.
  - `_format_entry` / `render_index` — thread `root` through so links are
    root-relative POSIX paths (fixes nested-doc links).
  - `_refresh_index(root, config)` — extracted from `_cmd_index`'s write path.
- **Exit:** `test_edit.py` green; renderer regression test green; the seven
  `test_cli_index.py` tests still green after the `render_index` refactor.

### Phase 6: Implement Offline/Core Path

- **Objective:** Implement the four verb cores on top of the Phase 5 helpers.
- **Files:** `bin/docs` — `_cmd_new`, `_cmd_touch`, `_cmd_archive`, `_cmd_mv`.
- **Exit:** `test_edit.py`, `test_cli_new.py`, `test_cli_touch.py`,
  `test_cli_archive.py`, `test_cli_mv.py` green.

### Phase 7: Update Tool/Wrapper Layer

- **Objective:** Finalize the CLI: exit-code mapping, `--dry-run` parity across
  all four verbs, `--cascade` interactive prompt, error messages to stderr.
- **Files:** `bin/docs` — `_build_parser()`, `main()`, the `_cmd_*` handlers.
- **Exit:** `docs <verb> --help` for all four; every CLI test green; exit codes
  match the [cli.md](cli.md) matrix.

### Phase 8: Run Tests (GREEN)

- **Objective:** Full suite passing; quality gates clean tree-wide.
- **Actions:** `pytest -q`; `ruff check .`; `ruff format --check .`; `mypy`.
- **Exit:** All four commands exit 0.

### Phase 9: Implement Online/Integration (dogfood pass)

- **Objective:** Exercise the verbs against a copy of this repo's own `docs/`.
- **Actions:** `docs new` a throwaway doc; `docs touch` a doc; `docs mv` a doc
  and confirm `Related:` rewrites; `docs archive` a doc and confirm the move +
  INDEX refresh. Reconcile `tests/fixtures/expected/` snapshots; verify
  idempotency.
- **Exit:** Archiving and renaming this repo's docs produces correct,
  drift-free state; any surviving diff is documented as intentional.

### Phase 10: Quality, Docs, Refactor

- **Objective:** Close out M2.
- **Actions:**
  - Full quality gate (Phase 8 commands).
  - Refactor any code grown past the readable budget; revisit the single-file
    decision if warranted (defer the split to M3 unless it becomes unworkable).
  - Update [status.md](status.md): M2 → Complete, M3 → ACTIVE.
  - Update [plan.md](plan.md): record the `--cascade` default decision and the
    INDEX directory/`Project` grouping deferral to M3.
  - Append milestone-completion summaries to this file and the log.
- **Exit:** Quality gate green; docs updated; ready to start M3.

## Phase Checklist

- [x] Phase 1: Define Contract
- [x] Phase 2: Write Tests (RED)
- [x] Phase 3: Create Data/Fixtures
- [x] Phase 4: Run Tests (RED Baseline)
- [x] Phase 5: Update Base Interfaces
- [x] Phase 6: Implement Offline/Core Path
- [ ] Phase 7: Update Tool/Wrapper Layer
- [ ] Phase 8: Run Tests (GREEN)
- [ ] Phase 9: Implement Online/Integration (dogfood pass)
- [ ] Phase 10: Quality, Docs, Refactor

## Decisions

Key choices applying to this milestone (broader decisions live in `vocab-adr.md`
and `dual-status-adr.md`):

- **Minimal-diff metadata editing, not re-serialization.** M1's
  `parse_metadata_block` returns a lossy `dict` — it drops line order, the
  inline-vs-bullet rendering choice, and in-block formatting. Re-serializing a
  whole block on every `touch` would churn diffs and risk byte-drift in
  untouched fields. M2's editors (`set_metadata_field`, `rewrite_related_refs`)
  instead do surgical line rewrites, preserving every byte outside the target
  line(s). `scaffold_doc` is the one builder — `new` creates text from scratch,
  so there is nothing to preserve.
- **`docs new` writes flat into the resolved docs root; nested slugs allowed.**
  A slug like `sub/foo` creates `sub/foo.md`, auto-creating `sub/`. Guardrails:
  reject `..` and absolute paths (no escaping the root); reject slugs that land
  under `archive_dir` (born-archived is `archive`'s job — statuses would
  mismatch). `new` reuses `index`'s root resolution (`--root` / positional /
  upward `.docs.toml` search). Rationale and the host-tree survey are in the
  milestone log's pre-Phase-1 design note.
- **Renderer root-relative-path fix is M2 scope.** `_format_entry` links by
  basename, breaking links for any doc in a subdirectory. `docs archive`
  creates `archive/<date>/` subdirs and regenerates the INDEX as its last step,
  so it would emit broken links on first use. The fix (thread `root` into
  `render_index`, emit root-relative POSIX paths) lands in Phase 5 as a
  prerequisite for `archive`. Directory-paths now show in the entry text too,
  which aids human navigation.
- **INDEX grouping by directory / `Project` is deferred to M3.** The real
  large-tree human-navigation improvement is grouping the INDEX by something
  other than `Role`. That is a view concern, not a mutating-verb concern; it is
  recorded as a [plan.md](plan.md) open question for M3 (`docs list --project`,
  directory-grouped INDEX). M2 keeps the INDEX Role-grouped; the renderer fix
  above ensures nested docs at least link correctly and show their path.
- **`--cascade` default deferred.** [plan.md](plan.md) asks whether
  `docs archive --cascade` should be the default with `--no-cascade` to opt
  out. Currently opt-in. Phase 1 declares `--cascade` as a plain `store_true`
  so the polarity is a one-line change if Phase 6 flips it. Decision recorded
  in plan.md at Phase 10.
- **Date-fragile snapshot test repaired.** `test_index_output_matches_frozen_snapshot`
  compares a generated INDEX against a committed snapshot that bakes
  `date.today()` into its `_Generated …_` summary line — so it fails on every
  day except the snapshot's. Phase 1 normalizes that one line before
  comparing, so the test checks structure, not the wall clock. (M1's Phase 6
  log flagged this as "acceptable risk … sensitive on day boundaries.")

## Testing / Quality Gate

Commands run at Phase 4 (RED baseline), Phase 8 (GREEN), and Phase 10:

```
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
./bin/docs index --root docs/ --dry-run   # dogfood smoke
```

Expected at Phase 4: M1's 58 tests green (snapshot repaired); every new M2 test
RED with `NotImplementedError` or a wrong exit code. Expected at Phase 8/10: all
commands exit 0.

## Success Criteria

M2 is complete when:

- [ ] All Phase Checklist items are checked.
- [ ] All four verbs (`new`, `archive`, `mv`, `touch`) work per [cli.md](cli.md),
      including `--dry-run` and the documented exit codes.
- [ ] Every write is atomic — a failure leaves the original doc untouched.
- [ ] Nested docs (archived docs especially) get working INDEX links.
- [ ] All Deliverables above are checked off.
- [ ] Dogfood: archiving and renaming this repo's own docs produces correct,
      drift-free state.
- [ ] [status.md](status.md) reflects M2 → Complete, M3 → ACTIVE.
- [ ] [m2-mutating-verbs-log.md](m2-mutating-verbs-log.md) contains a
      milestone-completion summary.

## Milestone-completion summary

_Appended at Phase 10._
