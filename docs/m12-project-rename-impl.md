# M12 — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-05-28

Related:
- child-of: m12-project-rename.md
- pairs-with: m12-project-rename.md
- pairs-with: status.md

## Overview

Chronological log of work on M12 — Project rename verb + M11
wart fixes + version SoT (v1.5.0). Append a section per TDD
phase (Contract → Tests → Fixtures → RED → Base interfaces →
Core path → Tool/Wrapper → GREEN → Dogfood → Quality/Docs/
Refactor) with objective, actions, results, decisions.

## Implementation metadata

- Project: docs
- Milestone: M12 — Project rename verb + M11 wart fixes +
  version SoT (v1.5.0)
- Started: 2026-05-28
- Progress: **Scope frozen 2026-05-28** (OQ-A through OQ-D
  promoted to Decisions per operator recommendations). Phase 1
  (Contract) opens in the next session via
  `/ship-milestone M12`.

(Note: doc-lifecycle status is in the front-matter `Lifecycle:`
field above. This section tracks milestone-implementation
progress, which is distinct.)

## TDD Phase Progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-05-28 | cli.md / convention.md / architecture.md pinned for `docs project rename`, `docs touch` outside-root refusal, `docs archive` referring-edge rewrite, and `importlib.metadata` version SoT. |
| 2. Write Tests (RED) | Complete | 2026-05-28 | 17 project-rename + 5 touch + 6 archive + 3 version-SoT tests; test_packaging A3/B1/B2/C2 bumped to 1.5.0. |
| 3. Create Data/Fixtures | Complete | 2026-05-28 | 4 new fixture trees (multi-project-alpha-sidecar, rename-with-archive, rename-with-malformed, archive-with-incoming-refs); first three pass `docs check`, fourth is deliberately malformed. |
| 4. Run Tests (RED Baseline) | Complete | 2026-05-28 | 32 RED / 400 GREEN; categorised across 6 expected M12-feature buckets + 2 lockstep buckets (skill_refs drift + a fresh-eyes snapshot bump from the touched-cli/convention/architecture dates). |
| 5. Update Base Interfaces | Complete | 2026-05-28 | importlib.metadata version SoT (with PackageNotFoundError fallback to `0.0.0+local`); `_find_root_strict` helper; `_resolve_touch_root` + `_resolve_project_root` refusal helpers (OQ-η split); `project` argparse namespace + `rename` sub-parser; main() dispatch; `_cmd_project_rename` stub. SKILL.md table row added for `docs project rename` to keep `test_every_named_verb_is_a_real_subcommand` GREEN. 29 RED / 403 GREEN. |
| 6. Implement Offline/Core Path | Complete | 2026-05-28 | `_cmd_project_rename` core (validate-all-first walk → sidecar+doc rewrite → INDEX); `_rewrite_sidecar_project_name` regex helper (`[ \t]*` boundary, not `\s*` — `\s` eats the trailing blank line in MULTILINE mode); `_print_project_rename_footer` with empty-clause drop; `_rewrite_referring_edges` shared walker (skips archived); `_find_malformed_doc` rescan helper to surface offending path when `parse_metadata_block` raises bare; `_cmd_touch` outside-root refusal inserted AFTER first-pass existence check (OQ-β); `_cmd_archive` adds pre-flight `walk()` validate + post-move `_rewrite_referring_edges` + cascade-batched moves; `_cascade_archive` returns `list[tuple[str, str]]` of moves (OQ-γ / OQ-δ). All 32 originally-RED M12 feature tests GREEN. 7 RED remain (Phase 7 targets: 4 packaging + 2 skill_refs + 1 version_matches_pyproject). |
| 7. Update Tool/Wrapper Layer | Complete | 2026-05-28 | pyproject.toml 1.4.0 → 1.5.0 (OQ-α: `pip install -e . --no-deps --force-reinstall --quiet` refreshed the editable install so `importlib.metadata.version("docs-cli")` reports 1.5.0); CHANGELOG.md `## 1.5.0 — UNRELEASED` entry (OQ-ζ format: em-dash + literal UNRELEASED, no parens; no "ready locally" / "deferred to M13" wording per the M11 lesson); skill refs cli.md / convention.md resynced from docs/ (OQ-8); spec drift sweep — every stderr message matches cli.md pins. All 432 tests GREEN. |
| 8. Run Tests (GREEN) + quality gate | Pending | — | |
| 9. Dogfood | Pending | — | |
| 10. Quality, Docs, Refactor | Pending | — | |

## Current state analysis (snapshot at milestone kickoff, 2026-05-28)

_Captured before Phase 1; historical._

- **Codebase (1.4.0 shipped on PyPI):** `src/docs_cli/cli.py`
  post-M11; 401 passing tests across 24 files; ruff / format /
  mypy clean tree-wide; `docs check docs/` exit 0.
- **What M12 inherits:**
  - `docs-cli==1.4.0` live at
    https://pypi.org/project/docs-cli/1.4.0/.
  - `pyproject.toml` `version = "1.4.0"`, `src/docs_cli/cli.py`
    `__version__ = "1.4.0"` (hardcoded literal — M12 replaces
    with `importlib.metadata.version("docs-cli")`),
    `tests/test_packaging.py` A3 pinned at `1.4.0`.
  - `docs touch <file>` outside any docs root currently
    inserts an unwanted `Updated:` line and crashes the
    downstream INDEX refresh on whatever sibling first fails
    its Lifecycle check. The M11 Phase 5 closeout caught this
    by accident.
  - `docs archive <doc>` moves the doc to `archive/<date>/`
    and sets `Lifecycle: archived` but does **not** rewrite
    referring `Related:` edges in other docs. Operator runs
    a manual `Related:` cleanup post-archive (M11 Phase 5
    did this for `status.md` + impl log).
  - `docs project rename` does not exist; renaming a `docs`
    root's `[project] name` requires hand-editing every
    conformant `Project:` line + the `.docs.toml` sidecar +
    regenerating INDEX. The M10 follow-on TODO captured the
    full target spec at
    [archive/2026-05-27/m10-adoption-polish.md](archive/2026-05-27/m10-adoption-polish.md)
    lines 261-268.
- **What M12 produces:**
  - `docs project rename <new-name>` verb (new namespace).
  - `docs touch` outside-docs-root graceful refusal (exit 2).
  - `docs archive` referring-edge rewrite (atomic with move).
  - `__version__` sourced from `importlib.metadata`.
  - `pyproject.toml` `version = "1.5.0"`,
    `test_packaging.py` A3 → `1.5.0`,
    `CHANGELOG.md ## 1.5.0 — UNRELEASED` entry authored with
    publish-survival wording (M11 lesson).
  - `dist/docs_cli-1.5.0-*` built locally; `twine check` PASS.
  - NO PyPI publish — that's M13's scope.

## Phase 1 — Define Contract

**Completed 2026-05-28.**

### Spec edits

- **`docs/cli.md`** — added a new `### docs project rename <new-name>`
  section (between `docs touch` and `docs install-skill`) pinning:
  syntax, resolution (cwd up-walk; `--root` override; refusal when no
  `.docs.toml`), auto-normalisation via `normalise_project_name()`,
  empty-name rejection, multi-project tolerance, archive-subtree skip,
  atomic semantics, `--dry-run`, no-op, success-output wording, the
  M12-specific exit-code matrix, and what does NOT change. Appended
  the M12 outside-docs-root refusal paragraph to `### docs touch <file>...`
  (including the `--root` bypass semantics). Appended the M12
  referring-edge-rewrite paragraph (plus `--cascade` extension) to
  `### docs archive <file>`. Added an M12 row to the exit-codes summary
  table near the bottom.
- **`docs/convention.md`** — added one sentence to the `Project` row
  in the Optional fields table referencing `docs project rename` as
  the in-lockstep rewriter.
- **`docs/architecture.md`** — changed the `cli.py` module-list dunder
  version line from `__version__ = "1.4.0"` to
  `__version__ = importlib.metadata.version("docs-cli")`; added an
  inline note describing the M12 SoT change + `OQ-4` PackageNotFoundError
  fallback; added a new `project — rename verb (M12)` bullet under the
  cli.py top-level module list.

### Pinned stderr-message strings

- Success (full):
  `docs: project rename: <old> -> <new> (rewrote .docs.toml + <N> doc(s); <M> archived skipped; <K> non-matching project(s) untouched: <list>)`
- Success (no extras):
  `docs: project rename: <old> -> <new> (rewrote .docs.toml + <N> doc(s))`
- Normalisation note: `docs: project rename: normalised "<input>" to "<normalised>"`
- No-op: `docs: project rename: <new> already current — no rewrites needed`
- No-`.docs.toml`: `docs: project rename: <cwd> is not under a docs root with .docs.toml; refusing`
- Empty post-normalised name: `docs: project rename: <input> normalises to empty string; project name must be non-empty`
- Dry-run per-doc: `docs: would rewrite Project: in <rel-path>`
- Dry-run sidecar: `docs: would rewrite [project] name in .docs.toml: "<old>" -> "<new>"`
- `docs touch` outside-root: `docs: touch: <path> is not under a docs root with .docs.toml; refusing`
- `docs touch --root` without `.docs.toml`: `docs: touch: --root <root> does not contain .docs.toml; refusing`

### Four-feature exit-code matrix

| Verb | 0 | 1 | 2 |
|---|---|---|---|
| `project rename` | success / no-op / dry-run | doc lacks editable metadata block | malformed `.docs.toml`; no `.docs.toml` ancestor; empty post-normalised `<new-name>` |
| `touch` (outside-root refusal) | — | — | no `.docs.toml` ancestor (cwd-resolved); `--root` without `.docs.toml` |
| `archive` (referring-edge) | success | referring doc has malformed metadata (move aborts) | archive-dir creation failure |
| `importlib.metadata` SoT | runtime read; PackageNotFoundError → `0.0.0+local` | — | — |

### OQ-1 through OQ-11 auto-resolutions (per operator recommendation)

- **OQ-1** — No-`.docs.toml` refusal on `docs project rename`: exit 2 + `docs: project rename: <cwd> is not under a docs root with .docs.toml; refusing`.
- **OQ-2** — Single human-readable stderr success line; drop empty clauses when their counts are 0; suppressed under `--quiet`; no `--json` mode in M12.
- **OQ-3** — Normalise the operator's `<new-name>` input once; compare normalised-new against the sidecar's `[project] name` as written. No double-normalisation.
- **OQ-4** — `importlib.metadata.PackageNotFoundError` falls back to `"0.0.0+local"`.
- **OQ-5** — No additional decision; the existing INDEX renderer handles the new project name automatically.
- **OQ-6** — Cascade-archive per-doc forgiveness preserved; only docs that actually moved get their referring edges rewritten.
- **OQ-7** — No `--json` mode in M12.
- **OQ-8** — Skill bundle resync deferred to Phase 7.
- **OQ-9** — Empty / whitespace-only post-normalised `<new-name>` → exit 2 + `docs: project rename: <input> normalises to empty string; project name must be non-empty`.
- **OQ-10** — Cascade INDEX-refresh timing unchanged (one end-of-batch refresh; already correct today).
- **OQ-11** — `docs touch --root <dir>` bypasses the outside-root refusal only when `<dir>/.docs.toml` exists; otherwise exit 2 + `docs: touch: --root <root> does not contain .docs.toml; refusing`.

### Notes

- `tests/test_skill_refs.py` will go RED on the cli.md / convention.md
  edits because the bundled mirrors at
  `src/docs_cli/skill/references/{cli,convention}.md` are not yet
  resynced. This is the **expected** Phase-4-baseline RED; Phase 7
  resyncs the bundle.
- `docs check docs/` passes with the edits applied (no metadata block
  drift; `Updated:` dates bumped via `docs touch`).

## Phase 2 — Write Tests (RED)

**Completed 2026-05-28.**

- **`tests/test_cli_project_rename.py`** — created (17 tests).
  Covers: help / sub-command registration, `.docs.toml` rewrite, every-
  matching-Project-line rewrite, non-matching-project skip, no-`.docs.toml`
  refusal, empty + whitespace-only input rejection, `--dry-run`,
  normalisation, normalisation `--quiet` suppression, atomic validate-
  failure leaves tree unchanged, no-op, single end-of-batch INDEX
  refresh, archive-subtree skip, non-matching-count footer, prose-not-
  touched.
- **`tests/test_cli_touch.py`** — appended 5 tests (M12 OQ-C + OQ-11):
  outside-docs-root refusal exits 2; no INDEX refresh; path-named in
  stderr; `--root <valid-root>` bypass succeeds; `--root <dir-without-
  toml>` refuses.
- **`tests/test_cli_archive.py`** — appended 6 tests (M12 referring-
  edge rewrite + cascade-atomicity + archive-subtree-read-only).
- **`tests/test_packaging.py`** — renamed `test_a3_project_version_is_
  1_4_0` → `_1_5_0`, `test_c2_docs_version_is_1_4_0` → `_1_5_0`; bumped
  every `1.4.0` literal in A3 / B1 / B2 / C2 to `1.5.0`.
- **`tests/test_version_metadata.py`** — created (3 tests): version
  sourced from `importlib.metadata`; matches pyproject.toml; cli.py has
  no hardcoded `__version__ = "<digit>...` literal.

55 new + edited tests; collection clean.

## Phase 3 — Create Data/Fixtures

**Completed 2026-05-28.**

Four new fixture trees under `tests/fixtures/trees/`:

- **`multi-project-alpha-sidecar/`** — copy of `multi-project/` with
  `.docs.toml` `[project] name` patched from `multi-project` to `alpha`
  (so a rename of alpha → gamma rewrites only the alpha-named docs and
  reports the beta docs in the non-matching footer).
- **`rename-with-archive/`** — `[project] name = "rename-target"`;
  one active `live.md` and one archived `archive/2026-04-01/old.md`,
  both carrying `Project: rename-target`. Exercises the archive-
  subtree skip + footer count.
- **`rename-with-malformed/`** — `[project] name = "minimal"`; two
  well-formed `good-{a,b}.md` docs + one `broken.md` with no H1.
  Exercises the atomic validate-all-first abort path.
- **`archive-with-incoming-refs/`** — three docs (`master.md`,
  `sidekick.md`, `witness.md`); master ↔ sidekick are
  `pairs-with`, and witness carries two `references:` edges.
  Exercises cascade-archive's atomic referring-edge rewrite.

`docs check` is clean on all three well-formed trees; the malformed
tree intentionally reports the `[malformed]` error on `broken.md` (the
condition the atomic-validate-failure test exercises).

## Phase 4 — Run Tests (RED Baseline)

**Completed 2026-05-28.**

Full suite: **32 failed, 400 passed**. Quality gate
(ruff check / ruff format --check / mypy / `docs check docs/`)
GREEN tree-wide.

### RED categorisation (32 total)

1. **`docs project rename` not yet a verb (17 tests in
   `test_cli_project_rename.py`)** — argparse rejects `project` as an
   invalid choice:
   > `argument {…,migrate,install-skill}: invalid choice: 'project' (choose from 'index', 'new', 'archive', 'mv', 'touch', 'check', 'list', 'migrate', 'install-skill')`
2. **`docs touch` outside-root refusal not implemented (4 tests in
   `test_cli_touch.py`)** — `docs touch` against an orphan file
   currently succeeds (corrupting it), exit 0:
   > `AssertionError: ('', 'docs: touched /tmp/.../no_docs_toml/random.md\n') / assert 0 == 2`
3. **`docs archive` referring-edge rewrite not implemented (3 tests in
   `test_cli_archive.py`)** — referring docs still carry the
   pre-archive path:
   > `AssertionError: assert 'pairs-with: archive/2026-05-28/core.md' in '<helper.md text still naming core.md>'`
4. **Packaging A3 / B1 / B2 / C2 still pinned to 1.4.0 (4 tests in
   `test_packaging.py`)** — pyproject still reads `1.4.0`:
   > `AssertionError: [project].version must be '1.5.0'; got '1.4.0'`
5. **`__version__` still hardcoded (2 tests in `test_version_metadata.py`)** —
   `importlib.metadata.version("docs-cli")` returns the installed
   editable distribution's version (`1.1.0` on this venv), while the
   hardcoded literal says `1.4.0`:
   > `AssertionError: assert '1.4.0' == '1.1.0'`
   The hardcoded-literal-refusal test trips on:
   > `AssertionError: cli.py contains a hardcoded \`__version__ = "<literal>"\` line; M12 sources the dunder from importlib.metadata.version('docs-cli')`
6. **Skill-bundle drift expected (2 tests in `test_skill_refs.py`)** —
   per the Phase-1 plan, the bundled mirrors at
   `src/docs_cli/skill/references/{cli,convention}.md` were NOT resynced
   in Phase 1; Phase 7 resyncs the bundle:
   > `AssertionError: src/docs_cli/skill/references/cli.md has drifted from docs/cli.md`

### `test_version_matches_pyproject` (1 test) is GREEN

The third version_metadata test currently passes because both
`__version__` (hardcoded `1.4.0` in cli.py) and `pyproject.toml`'s
`version` (also `1.4.0`) currently match. After Phase 6 swaps cli.py to
the `importlib.metadata` runtime lookup, the test temporarily flips RED
on a fresh editable-install venv (where `importlib.metadata.version` may
yield a different installed version), then flips back GREEN at Phase 7
once `pyproject.toml` is bumped to `1.5.0` and the editable install is
refreshed.

### Audit fix (frozen-snapshot regeneration)

The Phase 1 `Updated: 2026-05-28` bumps on cli.md / convention.md /
architecture.md caused `tests/test_cli_index.py::test_index_output_matches_frozen_snapshot`
to RED on the new dates. The snapshot at
`tests/fixtures/expected/docs-INDEX.md` is a dogfood guard — when the
real docs evolve, the snapshot is regenerated lockstep. Done by copying
`docs/` to a tmpdir, running `docs index --root <tmpdir>`, and
overwriting the expected file with the result. Re-run of the snapshot
test is GREEN; no contract change.

### Post-review tightening (fresh-eyes review, 2026-05-28)

A fresh-eyes review of the Phase-2 RED tests surfaced six contract-pinning
assertions that hedged with `or` or substring fragments where cli.md
pinned an exact literal. All six tightenings are test-only (no source
edit) and kept the suite at 32 RED / 400 GREEN.

- **Fix 1 — footer non-matching count (`test_project_rename_footer_reports_non_matching_count`).**
  Replaced `"non-matching" in proc.stderr and "beta" in proc.stderr` with
  literal `"non-matching project(s) untouched:"` + `"beta" appears after
  the marker"` + count assertion `"3 non-matching project(s) untouched:"`
  (the multi-project-alpha-sidecar fixture has 3 beta docs in the active
  subtree). Matches cli.md OQ-2.
- **Fix 2 — empty/whitespace-name (`test_project_rename_rejects_empty_input`, `_rejects_whitespace_only_input`).**
  Replaced `"normalises to empty string" or "must be non-empty"` with the
  full-message literal `"normalises to empty string; project name must
  be non-empty"`. Matches cli.md OQ-9.
- **Fix 3 — dry-run sidecar (`test_project_rename_dry_run_makes_no_change`).**
  Added the per-doc literal `"would rewrite Project: in"` plus the
  sidecar literal `"would rewrite [project] name in .docs.toml"` plus the
  quoted-name pair `'"minimal" -> "foo"'`. Matches cli.md dry-run pins.
- **Fix 4 — exit code 1 on referring-doc malformed (`test_archive_referring_edge_rewrite_is_atomic`).**
  Replaced `proc.returncode != 0` with `proc.returncode == 1` per the
  M12 archive exit-code row in cli.md (`MetadataError → return 1`,
  consistent with existing cli.py:3346 branch).
- **Fix 5 — byte-identity INDEX idempotency (`test_project_rename_refreshes_index_once`, `test_archive_referring_edge_rewrite_refreshes_index_once`).**
  Replaced "exactly one refresh" mtime-only check with a follow-up
  `docs index` no-op + byte-identical INDEX assertion — proves the verb
  left INDEX fully refreshed at end-of-batch (more robust on fast
  filesystems than mtime-equality with sleep).
- **Fix 6 (nit) — archive-subtree footer (`test_project_rename_skips_archive_subtree`).**
  Replaced `"1 archived" or "archived skipped"` with literal
  `"1 archived skipped"` per cli.md OQ-2.

### Post-review skipped findings (recorded as decisions, no test changes)

- **Skipped (nit-6, archive-subtree-not-rewritten second direction):** the
  M12 rewrite walker only targets the moved doc's old path; a `Related:`
  edge from a separately-archived doc never matches the rewrite target.
  Existing test coverage is sufficient.
- **Skipped (nit-8, help-test smoke):** `test_project_rename_help` /
  `test_project_rename_subcommand_registered` are intentional
  registration guards (not contract-shape assertions). Keep as-is.
- **Skipped (nit-9, `alpha-old-spec.md` Lifecycle: active naming):**
  fixture intent — an old-but-still-active spec exercises the within-
  group `Updated:` sort. No fixture rename.
- **Skipped (nit-10, legacy `add_statuses` TOML key in multi-project
  trees):** pre-existing in the `multi-project/` fixture; out of M12
  scope.

## Phase 5 — Update Base Interfaces

**Completed 2026-05-28.**

### Code edits (cli.py)

- **`__version__` is now sourced from `importlib.metadata`.** Removed
  the hardcoded `__version__ = "1.4.0"` literal at the top of cli.py;
  imports moved (`importlib.metadata` joined `importlib.resources` in
  the stdlib block); `__version__ = importlib.metadata.version("docs-cli")`
  wrapped in a `try` / `except importlib.metadata.PackageNotFoundError`
  block that falls back to `"0.0.0+local"` (M12 — OQ-4). The
  `^__version__\s*=\s*["\']\d` literal-refusal regex stays anchored at
  line start with no leading whitespace, so the indented fallback
  inside the `except` block does not match.
- **`_find_root_strict(start: Path) -> Path | None`** added next to
  `find_root`. Same walk-up loop, but returns `None` when no
  `.docs.toml` ancestor is found. Used by M12 verbs that must refuse
  rather than silently treat a non-managed dir as a docs root.
- **`_resolve_touch_root(args, start)`** + **`_resolve_project_root(args, start)`**
  free helpers, both returning `Path | int` (the int is an exit code
  with the refusal message already printed to stderr). Both honour
  the OQ-η split — `--root` named in stderr when set; the start path
  named when not.
- **`project` argparse sub-parser added between `touch_p` and
  `check_p`** with a required `project_command` subparsers dest.
  `project rename` carries `parents=[common]`, a positional `new_name`
  (metavar `new-name`), and inherits `--root`, `--quiet`, `--dry-run`.
- **`main()` dispatch** extended with an `if args.command == "project"`
  branch routing `project rename` to `_cmd_project_rename`.
- **`_cmd_project_rename` Phase-5 stub** (`return 2`) so `--help` works
  but behaviour tests stay RED.

### Skill bundle (one-line edit)

- **`src/docs_cli/skill/SKILL.md`** — added a `Rename the project`
  row to "The verbs" table:
  `Rename the project | docs project rename <new-name> | rewrites .docs.toml + every Project: line; --dry-run`.
  Keeps `test_every_named_verb_is_a_real_subcommand` GREEN now that
  `project` exists as a real subcommand. The bundled cli.md /
  convention.md mirrors are NOT resynced here — Phase 7 does that
  (OQ-8).

### Test results

- `test_project_rename_help`, `test_project_rename_subcommand_registered`,
  `test_cli_py_has_no_hardcoded_version_literal`,
  `test_version_is_sourced_from_importlib_metadata` all flipped GREEN.
- Suite: **29 failed, 403 passed.** Phase-4 baseline was 32 RED / 400
  GREEN; Phase 5 flipped 4 tests GREEN, and `test_version_matches_pyproject`
  flipped GREEN-to-RED (pyproject still 1.4.0 but `__version__` now
  reports the editable-install version) — net (-2 RED, +0 GREEN-to-RED for
  the version_matches test that was already counted differently).
- The 29 remaining RED are: 17 project-rename, 4 touch outside-root, 3
  archive referring-edge, 4 packaging (A3 / B1 / B2 / C2), 2 skill_refs
  drift, 1 version_matches_pyproject.
- `ruff check .` / `ruff format --check .` / `mypy` / `docs check docs/`
  all clean.

## Phase 6 — Implement Offline/Core Path

**Completed 2026-05-28.**

### Code edits

- **`_cmd_touch` outside-root refusal** inserted between the
  first-pass file-existence check (which preserves the
  missing-file → exit-1 contract — OQ-β) and the existing
  `load_config(root)` call. Calls `_resolve_touch_root(args,
  start)` where `start` is the FIRST FILE'S PATH (not its parent
  dir) so the refusal stderr names the offending doc per cli.md's
  pin. `_find_root_strict` walks up from a file path; the
  `.is_file()` check on `<file>/.docs.toml` fails as expected, so
  the walk moves to the file's parent on the next iteration.
- **`_cmd_project_rename`** replaces the Phase-5 stub with the
  full validate-then-commit-then-INDEX-once flow:
  1. OQ-1 refusal via `_resolve_project_root(args, Path.cwd())`.
  2. `load_config(root)` wrapped in `try / except
     tomllib.TOMLDecodeError → exit 2`.
  3. Auto-normalise via `normalise_project_name` (OQ-A); empty
     post-normalisation → exit 2 with the OQ-9 wording. Normalisation
     note gated on `not args.quiet`.
  4. `old_name = config.project` (no double-normalisation — OQ-3).
  5. Validate-all-first walk: drives `walk()` with `next(walker)`
     in a `while True` loop so we can re-raise the offending path
     via `_find_malformed_doc` when `parse_metadata_block` raises
     a bare `MetadataError`. Buckets each doc into `matching`
     (resolved-project == old) or `non_matching[resolved] += 1`;
     `doc.archived` increments `archived_count`. OQ-γ-bis: docs
     without an explicit `Project:` line resolve to `config.project`
     via `_resolved_project`, so they implicitly match (and
     `set_metadata_field` will INSERT a `Project:` line).
  6. No-op test: `new_name == old_name` emits the cli.md no-op
     stderr (gated on `not args.quiet`); exit 0; no writes.
  7. Build doc-rewrite plan: `set_metadata_field(path.read_text(),
     "Project", new_name)` per matching path.
  8. Build sidecar rewrite via `_rewrite_sidecar_project_name`;
     no-change result → exit 2 with the
     "malformed .docs.toml: missing or unparseable name = "<old>" line"
     wording.
  9. `--dry-run` branch: per-doc `would rewrite Project: in <rel>`
     + sidecar `would rewrite [project] name in .docs.toml:
     "<old>" -> "<new>"` + footer.
  10. Commit phase: every doc, then the sidecar (`atomic_write`).
  11. INDEX refresh with reloaded config (so the new project name
      renders).
  12. Footer emission.
- **`_rewrite_sidecar_project_name(text, old, new)`** —
  regex-surgical, minimal-diff sidecar rewrite. Initial draft used
  `\s*$` for the trailing-whitespace anchor, but `\s` matches
  newlines in MULTILINE mode — the regex was eating the blank
  line between `[project]` and `[archive]` sections. Switched to
  `[ \t]*$`. If no match: returns text unchanged; caller treats
  that as a malformed sidecar.
- **`_print_project_rename_footer`** — single human-readable
  stderr line (OQ-2 wording); empty clauses are dropped when
  their counts are 0.
- **`_find_malformed_doc(root, config)`** — re-scans the active
  subtree file-by-file to recover the offending path when
  `walk()` raises a bare `MetadataError` from
  `parse_metadata_block` (which raises without the path prefix
  that `parse()` would add). Mirrors `walk`'s skip rules
  (dotfiles, `INDEX.md`, archive subtree).
- **`_cascade_archive`** widened to return `list[tuple[str, str]]`
  — `(old_rel, dest_rel)` per successful cascade-archive (OQ-γ /
  OQ-δ). Failed / declined archives contribute nothing.
- **`_rewrite_referring_edges(root, config, moves)`** — single
  active-tree walk; per `(old_rel, new_rel)` pair, applies
  `rewrite_related_refs`; atomic-writes touched docs only.
  Archive subtree is read-only (skipped).
- **`_cmd_archive`** now (a) does a pre-flight `list(walk(root,
  config))` validate-all-first BEFORE the move, mapping
  `MetadataError`/`VocabularyError` to exit 1 (so a broken
  referring doc no longer leaves a half-archived tree); (b)
  captures `old_rel` BEFORE `_archive_one` runs (post-move
  the source file no longer exists); (c) initial `moves =
  [(old_rel, dest_rel)]`, extended by the cascade list; (d)
  calls `_rewrite_referring_edges(root, config, moves)` before
  `_refresh_index`. INDEX still refreshes exactly once at
  end-of-batch.

### Test results

- All 17 project-rename + 4 touch outside-root + 6 archive
  referring-edge tests GREEN.
- Pre-existing touch, archive, mv tests still GREEN.
- 7 RED remain: 4 packaging (`A3` / `B1` / `B2` / `C2`) + 2
  skill_refs drift + 1 `test_version_matches_pyproject` — all
  Phase 7 targets.
- ruff / ruff format --check / mypy / `docs check docs/` clean.

## Phase 7 — Update Tool/Wrapper Layer

**Completed 2026-05-28.**

### Edits

- **`pyproject.toml`** — `version = "1.4.0"` → `"1.5.0"`.
- **Editable install refresh (OQ-α)** —
  `.venv/bin/pip install -e . --no-deps --force-reinstall --quiet`
  so `importlib.metadata.version("docs-cli")` reports 1.5.0 in the
  Python session pytest spawns.
- **`CHANGELOG.md`** — prepended `## 1.5.0 — UNRELEASED` entry
  (OQ-ζ format: em-dash + literal UNRELEASED, no parens) with
  Added / Changed / Notes sections describing the four M12
  features. NO `(LOCAL; not on PyPI)` suffix; NO "ready locally"
  / "deferred to M13" wording (M11 lesson). Date stays UNRELEASED
  until M13 publish.
- **Skill refs resynced (OQ-8)** —
  `cp docs/cli.md src/docs_cli/skill/references/cli.md` and
  `cp docs/convention.md src/docs_cli/skill/references/convention.md`.
  `test_skill_refs.py` flipped GREEN.
- **Spec drift sweep** — re-read cli.md's `### docs project
  rename`, `### docs touch`, `### docs archive` sections; every
  Phase 6 stderr message matches the pinned wording.

### Test results

- All 432 tests GREEN.
- ruff / ruff format --check / mypy / `docs check docs/` clean.

## Phase 8 — Run Tests (GREEN) + quality gate

_Not started._

## Phase 9 — Dogfood

_Not started._

## Phase 10 — Quality, Docs, Refactor

_Not started._
