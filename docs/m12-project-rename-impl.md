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
| 4. Run Tests (RED Baseline) | Pending | — | |
| 5. Update Base Interfaces | Pending | — | |
| 6. Implement Offline/Core Path | Pending | — | |
| 7. Update Tool/Wrapper Layer | Pending | — | |
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

_Not started._

## Phase 5 — Update Base Interfaces

_Not started._

## Phase 6 — Implement Offline/Core Path

_Not started._

## Phase 7 — Update Tool/Wrapper Layer

_Not started._

## Phase 8 — Run Tests (GREEN) + quality gate

_Not started._

## Phase 9 — Dogfood

_Not started._

## Phase 10 — Quality, Docs, Refactor

_Not started._
