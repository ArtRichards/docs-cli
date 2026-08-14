# M4 — Migration helper (`docs migrate`)

Lifecycle: archived
Role: milestone
Project: docs
Updated: 2026-08-14

Related:
- parent-of: archive/2026-05-22/m4-migration-helper-log.md
- child-of: plan.md
- implements: charter.md
- pairs-with: convention.md
- pairs-with: cli.md
- pairs-with: architecture.md
- pairs-with: test-strategy.md

Revision:
- 2026-08-14: M27 one-time body-link migration; body-link destinations repaired (destination tokens only)

## Overview

- Milestone: M4
- Title: Migration helper (`docs migrate`)
- Surface: one new CLI subcommand on the `docs` executable (`docs migrate`),
  plus the inference + planning helpers it is built on. Dry-run by default;
  `--apply` performs the edits.
- Status: ACTIVE (started 2026-05-22)

### Goal

M1–M3 made a *conforming* tree readable, writable, and enforceable. M4 lets
the tool *adopt a non-conforming one*. `docs migrate <dir>` walks a foreign
directory, inspects each `.md` file, infers the metadata the convention
requires (`Status`, `Role`, `Project`, `Updated`), and produces a migration
plan — one decision per file, with every ambiguity surfaced. By default it
only reports; `--apply` performs the edits. This is the verb that lets an
agent point at an existing doc tree and bring it into the convention without
manual labour: the tool surfaces ambiguities, an agent (or human) resolves
them, the tool applies the decisions.

### Requirements

- `docs migrate <dir> [--apply] [--json] [--quiet] [--date YYYY-MM-DD]` walks
  a *foreign* directory (no `.docs.toml` assumed) and inspects every `.md`
  file's structure. It is read-only by default — a dry-run plan; `--apply`
  performs the edits. `--date` sets the archive date for normalised moves
  (default: today), parallel to `docs archive --date`.
- For each file, infer the metadata the convention requires:
  - **Role** — from filename suffix / token patterns (`-spec`, `-status`,
    `-plan`, `-adr`, `-log`, …) and from any already-present metadata-shaped
    lines; fall back to `notes` when nothing matches.
  - **Project** — from a common filename prefix shared across the tree (or
    the directory name when there is no usable common prefix).
  - **Status** — from any already-present `Status:`-shaped line, else a
    default (`active` for an active-tree doc, `archived` for one already
    under a detected archive-style subdir).
  - **Updated** — from any already-present `Updated:`-shaped line, else the
    file's mtime, normalised to `YYYY-MM-DD`.
- Insert a convention-correct metadata block immediately under the H1. If the
  file has no H1, synthesise one from the filename (reusing `_slug_to_title`).
  If the file already carries metadata-shaped lines, reconcile the four
  required fields into the block; preserve any *other* metadata-shaped field
  (`Owner:`, `Tags:`, `Related:`, …) into a `## Migrated metadata` body
  section under a `Migrated-` prefix rather than dropping it (branch-review
  decision — see Decisions).
- Detect existing archive-style subdirectories (`archived/`,
  `project-history/`, `archive/YYYY-MM-DD/`, …) and normalise them to the
  convention's `archive/YYYY-MM-DD/` layout with `Status: archived`.
- Every per-file decision records a **confidence** and, when the inference is
  not unambiguous, an explicit **ambiguity** note — so the plan is complete:
  every file has either a confident decision or a flagged question.
- The dry-run plan (`--json` or human) is the contract surface an agent
  consumes; `--apply` writes the decided block into each file atomically
  (`atomic_write`) and performs any archive-normalising moves.
- `migrate` never runs on a directory it would corrupt: it refuses to migrate
  a directory that is *already* a docs root (`.docs.toml` present) — that tree
  is for `index` / `check`, not `migrate`.

### Deliverables

- [x] One subcommand functional on `bin/docs`: `migrate`, taking a positional
      `<dir>` (no `--root`), dry-run by default, `--apply` to write.
- [x] Inference helpers — `infer_role`, `infer_project`, `infer_status`,
      `infer_updated`, `detect_archive_layout` — pure and unit-tested.
- [x] Scope boundary held: the **active-tree directory layout is left
      untouched** — `--apply` adds metadata in place and only ever moves docs
      out of detected archive-style subdirs into `archive/YYYY-MM-DD/`. No
      role-bucket flattening or project/role re-foldering of the active tree.
- [x] A `MigrationPlan` / `FileMigration` model carrying per-file decisions,
      confidence, and ambiguity notes; `plan_migration` builds it,
      `apply_migration` executes it.
- [x] `--json` plan schema pinned in [cli.md](../../cli.md), stable from M4 on. The
      record is one flat object per file: `path`, `role`, `project`, `status`,
      `updated` (ISO `YYYY-MM-DD`), `confidence`, `ambiguities`, `archive_move`
      (path or null), `synthesized_h1`, `reconciled_metadata`.
- [x] `tests/test_migrate.py` (inference + planning units) and
      `tests/test_cli_migrate.py` (CLI dry-run / `--apply` / `--json`).
- [x] Fixture tree(s) of non-conforming docs under
      `tests/fixtures/trees/foreign/` (per [test-strategy.md](../../test-strategy.md))
      — including `proj-extra-metadata.md`, which carries non-required
      metadata fields to exercise the extra-field preservation path.
- [x] Dogfood: a dry-run against a foreign example directory produces a
      complete plan — an explicit decision for every file, every ambiguity
      flagged; `--apply` on a copy yields a tree `docs check` accepts.
- [x] All quality gates green tree-wide: `ruff check .`, `ruff format --check
      .`, `mypy`, `pytest -q`.
- [x] `docs/status.md` updated; M4 → Complete, M5 → next. (`docs/plan.md`
      opens no M4 question — operator-confirmed; its M4 section reads as
      shipped.)

## Current state analysis (snapshot at milestone kickoff, 2026-05-22)

_Captured before Phase 1; historical. Post-milestone state lives in the
Milestone-completion summary at the bottom of this file._

- **Existing code:** `bin/docs` shipped M1+M2+M3 (~1,790 lines) — parser,
  walker, renderer, seven verbs, config loading, surgical metadata editors,
  validation, query. The reuse surface for M4 is broad:
  - **Writing the inferred block:** `scaffold_doc` (`bin/docs:825`) builds a
    full doc from scratch; `set_metadata_field` (`bin/docs:743`) inserts a
    single metadata line surgically. M4 inserts a *block* into an
    *existing* body — see the Gap below.
  - **Lenient traversal:** `_iter_doc_texts` (`bin/docs:858`) already walks a
    tree yielding raw `(path, text)` without parsing — exactly what `migrate`
    needs to inspect non-conforming files. (Note: it skips dotfiles /
    dotdirs; a foreign `archived/` subdir is *not* a dotdir, so it is walked.)
  - **Block detection:** `parse_metadata_block` / `_metadata_line_span`
    (`bin/docs:314` / `bin/docs:244`) locate an H1 + metadata block when one
    exists — used to tell "already has metadata" from "needs a block".
  - **Validation:** `check_doc` (`bin/docs:907`) is the post-migration
    acceptance oracle — an applied migration must produce docs `check_doc`
    finds clean.
  - **Verb plumbing:** `_slug_to_title` (`bin/docs:1403`) for the missing-H1
    case; `atomic_write` (`bin/docs:372`) for `--apply` writes;
    `_archive_one`'s edit-then-move pattern (`bin/docs:1468`) for the
    archive-normalising moves; `_build_parser` / `main` (`bin/docs:1175` /
    `bin/docs:1755`) for the subcommand wiring.
- **Existing tests:** 164 (M1+M2+M3), all green at kickoff.
- **Gap M1–M3 left:** the tool can only *write* metadata into a doc that
  already conforms (`set_metadata_field` requires an existing block;
  `scaffold_doc` builds from nothing — there is no body to preserve). M4 must
  insert a metadata block *between an existing H1 and an existing body* (or
  synthesise the H1), and it must *infer* values the convention requires that
  a foreign doc simply does not carry. Neither inference nor block-insertion
  exists; both are M4.
- **Foreign-tree fixture:** [test-strategy.md](../../test-strategy.md) already
  reserves `tests/fixtures/trees/foreign/` "for `docs migrate` tests (M4)" —
  Phase 3 builds it.

## TDD Implementation Plan

The ten phases follow the fixed methodology in [status.md](../../status.md). Phases
1–4 establish the contract, tests, fixtures, and RED baseline with **no verb
implementation**; phases 5–10 implement and ship.

### Phase 1: Define Contract

- **Objective:** Declare the M4 surface. No business logic.
- **Files:**
  - `bin/docs` — `FileMigration` and `MigrationPlan` frozen dataclasses; stub
    signatures + docstrings for `infer_role`, `infer_project`,
    `infer_status`, `infer_updated`, `detect_archive_layout`,
    `insert_metadata_block`, `plan_migration`, `apply_migration`,
    `migration_to_json` (bodies raise `NotImplementedError("… — Phase N")`);
    `_cmd_migrate` stub handler; the `migrate` subparser in `_build_parser()`;
    `main()` dispatch extended; `__version__` → `0.4.0-m4`; module docstring
    refreshed.
  - `docs/cli.md` — add the `docs migrate` subcommand section (usage,
    inference rules summary, dry-run-by-default / `--apply` semantics, exit
    codes); pin the `--json` migration-plan record schema; remove `docs
    migrate` from the "What's deliberately not in v1" list.
  - `docs/architecture.md` — flesh out the `migrate` module bullet (currently
    a one-liner "foreign-tree import (M4)") with the inference + plan/apply
    responsibilities.
  - `docs/status.md` — M4 marked in flight.
  - `docs/m4-migration-helper.md`, `docs/m4-migration-helper-log.md` —
    created (this file and its log).
- **Exit:** `docs --help` lists eight subcommands; `migrate` parses its args
  then exits non-zero on the stub; `ruff` / `mypy` clean; `docs/INDEX.md` and
  the dogfood snapshot regenerated in lockstep so they pick up the two new M4
  docs.

### Phase 2: Write Tests (RED)

- **Objective:** Express every M4 behaviour as a failing test.
- **Files:**
  - `tests/test_migrate.py` — unit tests for each inference helper
    (`infer_role` per suffix pattern + the `notes` fallback; `infer_project`
    common-prefix vs directory-name fallback; `infer_status` /
    `infer_updated` from existing lines vs defaults/mtime;
    `detect_archive_layout` per archive-dir style), for `insert_metadata_block`
    (H1 present, H1 absent, metadata-shaped lines already present →
    reconciled not duplicated, body + trailing newline preserved), and for
    `plan_migration` (a confident decision per file; ambiguities flagged;
    archive-normalising moves planned).
  - `tests/test_cli_migrate.py` — `--help`; dry-run is the default and
    writes nothing; `--json` plan schema and field types; `--apply` writes
    convention-correct blocks and performs the archive moves; the
    refuse-on-`.docs.toml` guard; exit codes; an applied tree passes `docs
    check`.
  - Reuse `tests/conftest.py`'s `_run()` subprocess idiom for the CLI tests.
- **Exit:** all tests collect without import / fixture-path errors; every M4
  test fails for the right reason — `NotImplementedError` or a wrong stub
  exit code.

### Phase 3: Create Data/Fixtures

- **Objective:** Build the foreign fixture tree(s) the Phase 2 tests reference.
- **Files:**
  - `tests/fixtures/trees/foreign/` — a non-conforming directory: `.md` files
    with **no** metadata block, files whose names carry inferable role
    suffixes (`auth-spec.md`, `release-plan.md`, `db-adr.md`, …), at least
    one file with **no H1**, at least one with pre-existing
    metadata-shaped lines to reconcile, a shared filename prefix for the
    project-inference case, and an archive-style subdir (`archived/` or
    `project-history/`) to exercise `detect_archive_layout`. **No
    `.docs.toml`** — it is a foreign tree, and the refuse-guard test needs an
    un-marked directory.
  - A second small tree (or a `.docs.toml`-bearing variant) for the
    refuse-on-already-a-docs-root guard test.
- **Exit:** every fixture path a Phase 2 test references exists; `foreign/`
  is genuinely non-conforming (a bare `walk()` / `check` over it would
  report violations — that is the point).

### Phase 4: Run Tests (RED Baseline)

- **Objective:** Confirm every failure traces to missing implementation, not
  misconfiguration. Log-only; no implementation. **This session pauses here.**
- **Actions:** `.venv/bin/python -m pytest tests/` — capture full output.
- **Exit:** every M4 failure traces to `NotImplementedError` or a wrong stub
  exit code; no `ImportError`, no fixture-path error; M1/M2/M3's 164 tests
  stay green.

### Phase 5: Update Base Interfaces

- **Objective:** Implement the pure inference helpers and the
  block-insertion helper.
- **Files:** `bin/docs` — `infer_role`, `infer_project`, `infer_status`,
  `infer_updated`, `detect_archive_layout`, `insert_metadata_block`.
- **Exit:** `test_migrate.py`'s inference + `insert_metadata_block` units
  green; `ruff` / `mypy` clean.

### Phase 6: Implement Offline/Core Path

- **Objective:** `plan_migration` and the dry-run path of the verb.
- **Files:** `bin/docs` — `plan_migration` (assemble a `FileMigration` per
  file, set confidence, flag ambiguities, plan archive moves); `_cmd_migrate`
  dry-run human output (the plan, grouped by file, ambiguities called out).
- **Exit:** `test_migrate.py` planning units green; the dry-run CLI tests
  green; `ruff` / `mypy` clean.

### Phase 7: Update Tool/Wrapper Layer

- **Objective:** Finalise the CLI — `--apply` (atomic writes + archive
  moves), `--json` plan output, the refuse-on-`.docs.toml` guard, exit-code
  mapping, errors to stderr.
- **Files:** `bin/docs` — `apply_migration`, `migration_to_json`, the
  `--apply` / `--json` branches of `_cmd_migrate`.
- **Exit:** every CLI test green; exit codes match the [cli.md](../../cli.md) matrix.

### Phase 8: Run Tests (GREEN)

- **Objective:** Full suite passing; quality gates clean tree-wide.
- **Actions:** `pytest -q`; `ruff check .`; `ruff format --check .`; `mypy`.
- **Exit:** all green.

### Phase 9: Implement Online/Integration (dogfood pass)

- **Objective:** Exercise `migrate` against a real foreign directory.
- **Actions:** `docs migrate <foreign-dir>` produces a complete dry-run plan
  (an explicit decision for every file, every ambiguity flagged); `docs
  migrate <foreign-dir> --apply` on a *copy* yields a tree that `docs check`
  accepts (exit 0) and `docs index` renders cleanly.
- **Exit:** the dry-run plan is complete; the applied copy passes `docs check`.

### Phase 10: Quality, Docs, Refactor

- **Objective:** Close out M4.
- **Actions:** full quality gate; update [status.md](../../status.md) (M4 →
  Complete, M5 → next). M4 carries **no `plan.md` open question** — the
  operator confirmed (2026-05-22) that none is opened for this milestone, so
  Phase 10 only verifies `plan.md`'s M4 section reads as shipped (and that
  `docs migrate` was removed from cli.md's "not in v1" list back at Phase 1);
  the parked extra-field allowlist question is left untouched. Append
  milestone-completion summaries here and in the log; consider the
  single-file-vs-package split once more (see Decisions).
- **Exit:** quality gate green; docs updated; ready to start M5.

## Phase Checklist

- [x] Phase 1: Define Contract
- [x] Phase 2: Write Tests (RED)
- [x] Phase 3: Create Data/Fixtures
- [x] Phase 4: Run Tests (RED Baseline)
- [x] Phase 5: Update Base Interfaces
- [x] Phase 6: Implement Offline/Core Path
- [x] Phase 7: Update Tool/Wrapper Layer
- [x] Phase 8: Run Tests (GREEN)
- [x] Phase 9: Implement Online/Integration (dogfood pass)
- [x] Phase 10: Quality, Docs, Refactor

## Decisions

Key choices applying to this milestone (broader decisions live in `vocab-adr.md`
and `dual-status-adr.md`):

- **`migrate` is dry-run by default; `--apply` is the opt-in to write.**
  (Operator-confirmed, 2026-05-22.) Every other mutating verb (`new`,
  `archive`, `mv`, `touch`) writes by default and takes `--dry-run` to opt
  *out*. `migrate` inverts that polarity deliberately: [plan.md](../../plan.md)'s M4
  section specifies "produces a dry-run report by default; `--apply` performs
  the edits", and a bulk
  inference-driven rewrite of a foreign tree is exactly the operation a user
  must see before it runs. `migrate` therefore does **not** use the `common`
  parent parser (which carries `--dry-run`); it declares its own `--apply`
  `store_true`. Its exit-criterion in [plan.md](../../plan.md) is about the
  *dry-run plan*, reinforcing dry-run as the primary mode.
- **`migrate` needs a new block-inserting editor.** `set_metadata_field`
  edits an *existing* block; `scaffold_doc` builds a doc from *nothing*.
  Neither inserts a metadata block between an existing H1 and an existing
  body — which is the core foreign-doc edit. M4 adds `insert_metadata_block`:
  it places (or synthesises) the H1, inserts the required block beneath it,
  preserves the existing body verbatim, and reconciles any pre-existing
  metadata-shaped lines into the block rather than leaving duplicates. It
  reuses `_metadata_line_span`'s block-boundary rules so the inserted block
  round-trips through `parse()`.
- **Inference is best-effort and always records confidence.** A foreign doc
  carries none of `Status` / `Role` / `Project` / `Updated` reliably. M4's
  inference is heuristic — filename suffixes for `Role`, common prefix for
  `Project`, mtime for `Updated`, archive-subdir membership for `Status`.
  Every `FileMigration` therefore carries a confidence and, when inference
  is not unambiguous, an explicit ambiguity note. That is the milestone's
  exit criterion: the plan is *complete* — every file has a confident
  decision or a flagged question — not necessarily *correct*. Correctness is
  the agent's (or human's) job, working from the surfaced ambiguities. This
  realises the charter's "agents … author and maintain docs" audience and
  [plan.md](../../plan.md)'s "intended to be agent-driven" note.
- **`Role` fallback is `notes`; never guess `Status`/`Role` outside the
  vocabulary.** When no suffix or in-file signal yields a role, inference
  falls back to the `notes` built-in (the convention's designated catch-all)
  and flags an ambiguity — it never invents an out-of-vocab role.
  `infer_status` likewise only ever produces a built-in status. This keeps
  an applied migration clean under `check_doc`'s `bad-vocab` rule by
  construction.
- **`migrate` refuses an already-managed tree.** Pointing `migrate` at a
  directory that already has a `.docs.toml` is almost always a mistake — that
  tree is for `index` / `check` / `list`, and re-inserting blocks could
  duplicate metadata. `_cmd_migrate` refuses with a clear message and a
  non-zero exit when `.docs.toml` is present at the target.
- **`migrate` takes a positional `<dir>`; no `--root`.** (Operator-confirmed,
  2026-05-22.) [plan.md](../../plan.md) notates the verb as `docs migrate <dir>`,
  and `--root` would have nothing to resolve against: a foreign tree by
  definition carries no `.docs.toml` for the up-walk to find. `migrate`
  therefore always takes its target directory as a required positional
  argument and does **not** accept the global `--root` flag — consistent with
  the refuse-on-`.docs.toml` guard above (a configured root is precisely the
  tree `migrate` declines to touch).
- **The `--json` plan record schema is pinned at Phase 1, stable from M4 on.**
  (Operator-confirmed, 2026-05-22.) One flat object per file — `path`, `role`,
  `project`, `status`, `updated` (ISO `YYYY-MM-DD`), `confidence`,
  `ambiguities`, `archive_move` (root-relative destination or null),
  `synthesized_h1`, `reconciled_metadata` — pinned in [cli.md](../../cli.md) as a
  table, mirroring M3's `doc_to_json` / `finding_to_json` flat-record style.
  The `FileMigration` dataclass field names are reconciled to these keys: the
  task plan's draft `has_h1` / `had_metadata` are the inverses of
  `synthesized_h1` / `reconciled_metadata`; the latter orientation is used
  consistently in both the dataclass and the JSON, so `migration_to_json` is a
  straight field-to-key copy.
- **`migrate` takes an optional `--date YYYY-MM-DD`.** (Operator-confirmed,
  2026-05-22.) Archive-style subdirs are normalised into `archive/<date>/`; the
  date is a single per-run value, defaulting to `date.today()`, set by an
  optional `--date` flag parallel to `docs archive --date`. A single archive
  date per run keeps the plan deterministic — every normalised move in one
  `migrate` invocation lands under the same dated directory.
- **Archive-subdir normalisation is in scope; active-tree restructuring is
  not.** (Operator-confirmed, 2026-05-22.) `detect_archive_layout` recognises
  common archive-style subdirs (`archive/`, `archived/`, `project-history/`,
  `archive/YYYY-MM-DD/`) and the plan moves their docs into the convention's
  `archive/YYYY-MM-DD/` layout with `Status: archived`. M4 does **not**
  reorganise the active tree into project/role subdirectories, and
  active-tree role-bucket flattening is explicitly **not** pulled into M4
  scope — the convention is metadata-driven and directory-agnostic (see
  `convention.md`'s "Subdirectories"), so a flat or arbitrarily-nested
  foreign active tree is left exactly as-is on disk; M4 adds metadata only.
  Only archive-style subdirs are normalised as a directory move.
- **Foreign extra metadata is preserved, not dropped.** (Operator-decided,
  branch review 2026-05-22.) A foreign doc may carry metadata-shaped lines
  beyond the four the convention requires (`Owner:`, `Tags:`, a `Related:`
  block, any other `Label: value` line). The four required fields
  (`Status`/`Role`/`Project`/`Updated`) are superseded by inferred values as
  before; every *other* field is now **preserved** into a `## Migrated
  metadata` body section, placed immediately below the canonical metadata
  block and above the rest of the body, with each label renamed under a
  `Migrated-` prefix (`Owner:` → `Migrated-Owner:`; a `Related:` block →
  `Migrated-Related:` with its bullet sub-items kept verbatim). A foreign doc
  with no extra fields gets no section. Because the preserved fields live in
  the body — under a `## ` heading, outside the metadata span
  `parse_metadata_block` anchors to the H1 — `docs check` does not validate
  them: this keeps the "applied tree passes `docs check`" Success Criterion
  intact and is precisely why a stale foreign `Related:` path can now be
  preserved safely. The operator chose "Section under front matter" and
  "rename"; the **`Migrated-` prefix is the conductor's default choice** for
  the rename rule (it was not specified by the operator and matches the
  preview the operator selected) — recorded here explicitly so the operator
  can adjust it on branch review. The preservation is deterministic and
  lossless, so it adds no plan ambiguity; the dry-run reports a preserved-
  field count per file.
- **Archive-move destination collisions are detected.** (Branch review
  2026-05-22.) Two foreign files with the same basename in different
  archive-style subdirs both normalise to one `archive/<date>/<basename>`
  destination. `plan_migration` now flags every colliding file as a
  low-confidence ambiguity so the dry-run surfaces it before `--apply`, and
  `apply_migration` raises `FileExistsError` (exit 2) rather than silently
  overwriting — mirroring the `_archive_one` guard.
- **`bin/docs` single-file vs package split — revisited at M4.** M2 and M3's
  Decisions both flagged a possible package split "at M3 / M4". After M3 the
  file is ~1,790 lines — large but sectioned with header comments and clean
  under `ruff` / `mypy`. M4 adds one verb plus a cluster of inference
  helpers. The split is re-evaluated at Phase 10: if the file crosses a
  threshold where the sectioning stops carrying it, the split happens then;
  otherwise it is deferred to v1.1. The default expectation, per M3's
  precedent, is **deferred** — recorded here so Phase 10 makes a conscious call.

## Testing / Quality Gate

Commands run at Phase 4 (RED baseline), Phase 8 (GREEN), and Phase 10:

```
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
./bin/docs migrate tests/fixtures/trees/foreign        # dogfood — dry-run plan
./bin/docs check docs/                                 # repo still clean
```

Expected at Phase 4: M1/M2/M3's 164 tests green; every new M4 test RED with
`NotImplementedError` or a wrong stub exit code. Expected at Phase 8/10: all
commands green; the `migrate` dry-run produces a complete plan and an applied
copy passes `docs check`.

## Success Criteria

M4 is complete when:

- [x] All Phase Checklist items are checked.
- [x] `docs migrate` works per [cli.md](../../cli.md): dry-run by default, `--apply`
      to write, `--json` plan output, the documented exit codes.
- [x] A dry-run against a foreign example directory produces a **complete**
      migration plan — an explicit decision for every `.md` file, every
      ambiguous case flagged (the [plan.md](../../plan.md) M4 exit criterion).
- [x] `docs migrate --apply` on a copy of that directory yields a tree that
      `docs check` accepts (exit 0) **with the active-tree directory layout
      unchanged** — the only directory moves are archive-style subdirs
      normalised to `archive/YYYY-MM-DD/`.
- [x] `docs migrate --json` output validates against the schema pinned in
      cli.md.
- [x] All Deliverables above are checked off.
- [x] [status.md](../../status.md) reflects M4 → Complete, M5 → next; [cli.md](../../cli.md)
      no longer lists `docs migrate` under "not in v1" (removed at Phase 1).
      No M4 open question is opened in [plan.md](../../plan.md) (operator-confirmed).
- [x] [m4-migration-helper-log.md](m4-migration-helper-log.md) contains a
      milestone-completion summary.

## Milestone-completion summary

**M4 — Migration helper (`docs migrate`) shipped 2026-05-22** across the ten
TDD phases. Phases 1-4 (contract, RED tests, the `foreign/` fixture tree, RED
baseline) landed on `m4/phases-1-4`; phases 5-10 (implement + ship) landed on
`m4/phases-5-10`.

**What shipped.** One new verb — `docs migrate <dir> [--apply] [--json]
[--quiet] [--date YYYY-MM-DD]` — that adopts a non-conforming foreign
directory into the convention. It walks the tree, infers the four required
fields per file, and produces a complete migration plan: a decision and a
confidence for every file, with every ambiguity surfaced. Dry-run by default;
`--apply` inserts the metadata blocks atomically and normalises archive-style
subdirectories. It refuses a directory that is already a docs root.

**Code surface added to `bin/docs`** (the surface M5 and any future work
reuse):

- `FileMigration` / `MigrationPlan` frozen dataclasses — the per-file decision
  and the whole plan; `FileMigration.__post_init__` enforces the
  confidence/ambiguities invariant.
- Five pure inference helpers — `infer_role` (filename suffix + in-file
  `Role:`, `notes` fallback), `infer_project` (longest common prefix, trimmed,
  else dir name), `infer_status` (in-file `Status:` else archive-membership
  default), `infer_updated` (in-file `Updated:` else mtime),
  `detect_archive_layout` (archive-style subdir → `archive/<ISO-date>/`).
- `insert_metadata_block` — inserts (or synthesises) the H1 and writes a
  convention-correct block, reconciling the four required pre-existing
  metadata fields and preserving any other field into a `## Migrated metadata`
  body section (`Migrated-` prefix); preserves the body verbatim. Supported by
  `_extra_metadata_fields` and `_render_migrated_metadata_section`.
- `plan_migration` (assembles the plan, applies the resolved
  ambiguity-flagging rule, and a cross-file pass flagging archive-move
  destination collisions), `apply_migration` (edit-then-move per file, with a
  `FileExistsError` guard against archive-move collisions),
  `migration_to_json` (the pinned 10-key flat record).
- `_cmd_migrate` + the `migrate` subparser; module-level `_ROLE_SUFFIXES`,
  `_ARCHIVE_SUBDIR_NAMES`, `_REQUIRED_METADATA_FIELDS`,
  `_MIGRATED_METADATA_HEADING`, and the `_in_archive_subdir` /
  `_print_migration_plan` / `_count_preserved_fields` helpers.

**Branch-review behaviour changes (2026-05-22).** A fresh-eyes review of
phases 5-10 drove three fixes, all on `m4/phases-5-10`: (1) `apply_migration`
+ `plan_migration` now detect archive-move destination collisions — a silent
data-loss hazard when two foreign files share a basename across archive-style
subdirs; (2) the `docs migrate --date` error now names the `--date` flag
rather than leaking an `Updated:` field label; (3) the operator-decided
extra-metadata-preservation behaviour — non-required foreign metadata fields
are preserved into a `## Migrated metadata` body section rather than dropped
(see Decisions). A new fixture `proj-extra-metadata.md` and 17 further tests
cover the changes.

**Tests.** 72 M4 tests — `tests/test_migrate.py` (57 inference + planning
units) and `tests/test_cli_migrate.py` (15 CLI tests). The full suite stands at
**236 passed, 0 failed**; `ruff check` / `ruff format --check` / `mypy` clean
tree-wide. (The original implementation shipped 55 M4 tests / 219 total; the
branch review added the extra-metadata-preservation and archive-collision
behaviours with 17 further tests.)

**Resolved questions (operator-confirmed 2026-05-22), all binding:**

- **Q1 — ambiguity-flagging rule.** `plan_migration` flags an ambiguity for
  exactly three sources: a `notes` role fallback, a synthesised H1, and an
  out-of-vocab in-file `Status:` substituted with a built-in. The plain
  active-tree status default and the mtime-derived `Updated:` fallback are
  expected best-effort defaults and are not flagged.
- **Q2 — archive-date validation.** The dated archive segment is validated
  against a fixed ISO `%Y-%m-%d`, and `migrate` always emits
  `archive/YYYY-MM-DD/` regardless of any `Config.date_format` — matching
  `convention.md`'s hard-coded archive layout. The `--date` flag is validated
  as ISO too.
- **Q3 — mtime fallback non-determinism.** Accepted as-is: mtime is a
  legitimate best-effort signal. A future `migrate --apply` snapshot test must
  pin `--date` and must not assert an mtime-derived `Updated:` value.
- **Q4 — `--apply` + `--json`.** `--json` is a pure output-format switch,
  orthogonal to `--apply` (consistent with `check` / `list`).
- **Q5 — benign nested subdir.** Confirmed in scope; `infer_role` is called
  with the basename so the suffix split works for nested files.

**`bin/docs` single-file vs package split — deferred to v1.1** (see Phase 10
log). After M4 the file is ~2,200 lines: large but still cleanly sectioned
with header comments and clean under `ruff` / `mypy`. The split did not earn
its keep at M4; it is re-evaluated at v1.1.

**Scope held.** The active-tree directory layout is left untouched — `--apply`
adds metadata in place and the only directory moves are archive-style subdirs
normalised to `archive/YYYY-MM-DD/`. No M4 `plan.md` open question was opened.
