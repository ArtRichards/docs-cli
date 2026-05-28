# M12 — Project rename verb + M11 wart fixes + version SoT (v1.5.0)

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-05-28

Related:
- parent-of: m12-project-rename-impl.md
- child-of: plan.md
- pairs-with: status.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: architecture.md
- pairs-with: release-runbook.md
- pairs-with: archive/2026-05-27/m11-pypi-publish.md
- pairs-with: archive/2026-05-27/m10-adoption-polish.md

## Overview

> **Stub-drafted 2026-05-28** following M11 closeout. M12 bundles
> one operator-facing headline feature (`docs project rename`)
> with two M11-surfaced wart fixes (`docs touch` non-root refusal;
> `docs archive` referring-edge rewrite) and a small packaging
> refactor (`importlib.metadata` for version single-source-of-truth).
> The kitchen-sink scope was the operator's explicit M12 choice
> (answer 2026-05-28) over a focused project-rename-only milestone,
> on the reasoning that the M11 warts are cheap to land in the same
> TDD cycle and shouldn't be left to rot.

- Milestone: M12 (v1.5.0)
- Title: Project rename verb + M11 wart fixes + version SoT
- Surface: one new verb (`docs project rename <new-name>`); two
  hardening fixes (`docs touch` outside-docs-root refusal; `docs
  archive` rewrites referring `Related:` edges atomically); one
  packaging refactor (`__version__` sourced from `importlib.metadata`
  with `pyproject.toml` `version` as single source of truth);
  CHANGELOG `## 1.5.0` entry authored with publish-survival
  wording per the M11 lesson; version bumps `pyproject.toml` +
  `tests/test_packaging.py` to 1.5.0.
- Status: Active (scope frozen 2026-05-28; OQ-A through OQ-D
  promoted to Decisions; Phase 1 opens in the next session
  via `/ship-milestone M12`)

### Goal

M11 shipped 1.4.0 and surfaced two warts in the doc-management
verbs (`docs touch` modifies non-docs-root files; `docs archive`
leaves dangling `Related:` edges in referring docs). M10
explicitly deferred the operator-facing `docs project rename`
verb. M6 parked the dual-version-hardcode (pyproject.toml +
`__version__`) on `importlib.metadata` as a future-iteration
note. M12 burns all four down in one TDD cycle.

The headline contract is genuinely useful: a docs root whose
`[project] name` was chosen poorly at adoption time today
requires the operator to hand-edit every `Project:` line + the
sidecar. `docs project rename <new>` makes that an atomic
single-command operation that mirrors how `docs migrate --apply`
and `docs touch` already behave.

The M11 wart fixes lower future agent-driven adoption friction
(`docs touch <random-file>` no longer silently corrupts) and
make milestone closeout cleaner (`docs archive` does not leave
dangling references the operator has to find and fix by hand).

The `importlib.metadata` refactor lets the next release bump a
single value (`pyproject.toml`'s `version`) instead of remembering
to touch two files in lockstep.

### Requirements

- **`docs project rename <new-name>`** verb. Sub-command of
  `docs project`; `project` becomes the first nested verb group
  (see Decisions for the syntax rationale). Atomic semantics
  mirroring `docs touch` + `docs migrate --apply`: validate
  *every* writable target up-front, fail the whole batch on any
  validation error (named-bad-path on stderr, exit 1, no on-disk
  mutation), commit all writes only after the validation pass,
  refresh INDEX exactly once at end-of-batch.
- **What `project rename` rewrites:**
  - `.docs.toml` `[project] name = "<old>"` → `name = "<new>"`.
  - Every conformant `Project: <old>` line in every doc under
    the docs root → `Project: <new>`.
  - INDEX.md regenerated end-of-batch (single write).
- **What `project rename` does NOT touch:**
  - Prose markdown references to the old project name (M2's
    "Related: bullets only, not prose" decision applies — see
    [m2-mutating-verbs.md](m2-mutating-verbs.md) Phase 9 log).
  - Files outside the docs root (anything excluded via the
    M8 layered exclusion surface; anything that doesn't carry
    a `Project:` line).
  - Archive subtree contents (archived docs are read-only;
    M3 decision; `project rename` skips them but reports the
    count).
- **`docs project rename --dry-run`** prints the planned set of
  rewrites without touching disk; exit 0 if any rewrites
  planned, exit 0 if none (printing "no rewrites needed" — not
  an error, just an idempotent no-op).
- **`docs touch <path>` outside any docs root**: refuse cleanly
  with exit 2 (config error), stderr message naming the path
  and the absence of an ancestor `.docs.toml`. **Must not**
  modify the file. **Must not** trigger a downstream INDEX
  refresh (the M11 cascade-crash on `README.md: missing
  Lifecycle`).
- **`docs archive <doc> [--cascade]`** rewrites every referring
  `Related: <type>: <doc>` bullet across the tree to point at
  the new `archive/<date>/<doc>` path, atomically with the
  archive move. Mirrors the existing `docs mv` referring-edge
  rewrite (M2 Phase 6). Continues to NOT touch prose markdown
  links.
- **`importlib.metadata` version SoT.** `src/docs_cli/cli.py`:
  `__version__ = importlib.metadata.version("docs-cli")`.
  Removes the hardcoded literal string. `pyproject.toml`
  `[project] version` is the single source of truth. The
  packaging test (`tests/test_packaging.py` A3) continues to
  pin the about-to-publish version as a literal — the test
  asserts "package metadata reports `1.5.0`", which is exactly
  what `importlib.metadata.version` reports.
- **CHANGELOG entry shape.** `## 1.5.0 — UNRELEASED` at top;
  body describes the four features with no "ready locally" /
  "deferred to MX" markers (M11 lesson). Date the entry at
  Phase 10. Drop `UNRELEASED` at the publish milestone (M13).
- **Quality gate green tree-wide** at every phase boundary:
  pytest (current baseline 401; M12 will land additional
  tests for each of the four features — exact count TBD),
  ruff / ruff format --check / mypy / `docs check docs/` /
  `docs index --root docs/ --dry-run`.
- **No publish.** Mirrors the M7/M8/M10 cadence: M12 builds
  and locally smoke-tests 1.5.0; the public PyPI release ships
  via M13 (the next publish-only milestone).

### Deliverables

- [ ] `docs project rename <new-name>` verb landed; rewrites
      `.docs.toml` `[project] name` + every `Project:` line in
      every active doc; atomic semantics; `--dry-run` supported;
      INDEX refresh once at end.
- [ ] `docs touch <path>` outside a docs root refuses with
      exit 2 + clear stderr; file not modified; no downstream
      INDEX refresh.
- [ ] `docs archive <doc>` rewrites referring `Related:` edges
      across the tree atomically with the move. `--cascade`
      semantics unchanged.
- [ ] `src/docs_cli/cli.py`: `__version__ =
      importlib.metadata.version("docs-cli")`. Hardcoded
      version string removed.
- [ ] `pyproject.toml` `version` bumped to `1.5.0`.
- [ ] `tests/test_packaging.py` A3 expected version updated to
      `1.5.0`.
- [ ] `CHANGELOG.md` `## 1.5.0 — UNRELEASED` entry added,
      authored with publish-survival wording (no "ready
      locally" / "deferred" markers per the M11 lesson).
- [ ] `dist/docs_cli-1.5.0-py3-none-any.whl` + `dist/docs_cli-1.5.0.tar.gz`
      built locally; `twine check` PASS.
- [ ] Phase 9 dogfood: run `docs project rename` against a
      throwaway dogfood tree (e.g. a copy of `kebab-tiny` under
      `/tmp/m12-dogfood`); verify atomic semantics + INDEX
      consistency.
- [ ] `docs/cli.md` documents `docs project rename` + the
      updated `touch` + `archive` semantics.
- [ ] `docs/convention.md` updated if the convention's wording
      on `Project:` needs clarification post-rename verb.
- [ ] `docs/architecture.md` notes the `importlib.metadata`
      version-SoT decision + the new `project` verb namespace.
- [ ] Bundled skill references resynced
      (`src/docs_cli/skill/references/{cli,convention}.md` ↔
      `docs/{cli,convention}.md`); `tests/test_skill_refs.py`
      GREEN.
- [ ] `docs/status.md` + `docs/plan.md` finalised: M12 row
      Complete; M11 row stays Complete; "Current milestone"
      → "v1.5.0 ready locally, M13 next"; INDEX + dogfood
      snapshot regenerated lockstep.
- [ ] Milestone-completion summary appended to
      `m12-project-rename.md` + `m12-project-rename-impl.md`.

## Phase Checklist

Standard 10-phase TDD cycle (no operational phases — M12 is an
implementation milestone, M13 is the publish):

- [x] Phase 1 — Define Contract (the four-feature contract +
      OPEN-QUESTION resolution into Decisions)
- [ ] Phase 2 — Write Tests (RED)
- [ ] Phase 3 — Create Data/Fixtures (project-rename test
      trees + touch-outside-root fixtures + archive
      referring-edge fixtures)
- [ ] Phase 4 — Run Tests (RED Baseline)
- [ ] Phase 5 — Update Base Interfaces (parser / dataclass /
      validator additions; importlib.metadata wire-up)
- [ ] Phase 6 — Implement Offline/Core Path (project-rename
      walker + writer; touch-outside-root refusal; archive
      referring-edge rewrite walker)
- [ ] Phase 7 — Update Tool/Wrapper Layer (argparse: new
      `project rename` sub-command; updated touch / archive
      messages; CHANGELOG.md `## 1.5.0 — UNRELEASED` entry;
      cli.md / convention.md / architecture.md updates; skill
      ref resync; pyproject.toml `version = "1.5.0"`;
      test_packaging.py A3 pin)
- [ ] Phase 8 — Run Tests (GREEN) + tree-wide quality gate
- [ ] Phase 9 — Dogfood (project rename against a throwaway
      kebab-tiny copy; touch outside-root in a synthetic
      no-`.docs.toml` directory; archive of a fixture milestone
      with referring docs)
- [ ] Phase 10 — Quality, Docs, Refactor (1.5.0 artefact build
      + `twine check` PASS; CHANGELOG date; milestone-completion
      summaries; status + plan finalisation; INDEX lockstep)

## Decisions

- **Verb syntax: `docs project rename <new-name>`** —
  sub-command form, with `project` as the first nested verb
  group. The M10 spec wording explicitly used this shape;
  preserves room for `docs project <other>` verbs in the
  future (e.g. `docs project show`, `docs project validate`).
  Rejected: `docs rename-project` (flat hyphenated form;
  closes off the namespace).
- **Atomic semantics across the four features.** All four
  honour the existing "validate up-front, fail the whole
  batch on any error, commit only after validation pass,
  refresh INDEX once at end" invariant established by `docs
  touch` (M2) + `docs migrate --apply` (M10).
- **`Related:` edges only, not prose markdown links.** The
  M2 Phase 9 decision on `docs mv` applies to `project
  rename` + `archive` referring-edge rewrite. Prose markdown
  references to the old project name / archived-doc path
  are deliberately left alone — operators who want them
  rewritten can grep/sed.
- **Archive subtree is read-only for `project rename`.**
  Consistent with M3's archive-is-read-only stance; the verb
  walks active docs only. The plan footer reports
  `archive: <N> docs untouched`.
- **CHANGELOG publish-survival wording (M11 lesson).** The
  M12 `## 1.5.0 — UNRELEASED` entry will describe what 1.5.0
  *contains*, not whether it's published. No `(LOCAL; not
  on PyPI)` suffix; no "ready locally" / "deferred to MX"
  sentences. M13 simply dates the entry at publish time.
- **`importlib.metadata` lookup at import time, not at
  `docs --version` call time.** `__version__ =
  importlib.metadata.version("docs-cli")` runs once at module
  import; subsequent reads are cheap. Tests that import
  `__version__` keep their existing import surface.
- **Version is 1.5.0** (minor bump). New verb is additive;
  the M11 warts are bug fixes; `importlib.metadata` is a
  refactor with no API change. SemVer-compliant.
- **No publish in M12.** Mirrors M7/M8/M10 → M9/M11/M13
  cadence. M13 is the publish-only milestone.
- **OQ-A — New-name validation in `project rename`:
  auto-normalise** (operator decision 2026-05-28). The verb
  invokes M7's `normalise_project_name()` (the same machinery
  `docs migrate` already uses) and emits a stderr note when
  the operator-supplied name differs from the normalised
  form: `docs: project rename: normalised "<input>" to
  "<output>"`. Consistent with `docs migrate`'s tolerance —
  rejected (a) would create false friction for operators who
  pass a mixed-case or underscored name; (c) would let
  non-conformant `Project:` lines back into the tree the
  rename verb is supposed to make consistent.
- **OQ-B — Multi-project tree behaviour: rewrite only
  matches, report others** (operator decision 2026-05-28).
  `docs project rename A → B` rewrites *only* docs whose
  `Project: A` matches; docs with `Project: <other>` are
  reported in a footer line (`<N> doc(s) with non-matching
  Project: left untouched: <project-name-list>`) but not
  modified. Atomic semantics still hold for the matching
  subset. Operator can resolve the cross-project
  inconsistency separately (or accept it as a multi-project
  docs root — M7 tolerates this shape). Rejected: (b) refuse
  is too aggressive for tolerated-but-non-uniform trees; (c)
  rewrite-all would silently swallow distinct project
  identifiers.
- **OQ-C — `docs touch` outside-docs-root error wording**
  (operator decision 2026-05-28). Exit 2 (config error) with
  stderr message
  `docs: touch: <path> is not under a docs root with .docs.toml; refusing`.
  Names the path *and* the underlying reason; mirrors the
  existing `docs check` error-message style. File must not
  be modified; no downstream INDEX refresh.
- **OQ-D — `docs archive --cascade` referring-edge rewrite:
  single atomic batch** (operator decision 2026-05-28). When
  `docs archive A --cascade` cascades into archiving B
  (because B `pairs-with: A`), the referring-edge rewrite
  step rewrites edges-pointing-at-A *and* edges-pointing-at-B
  in the same atomic batch, with a single INDEX refresh at
  end. The cascade already happens in one operator
  invocation; splitting the referring-edge rewrite would
  surface inconsistent intermediate state (referring docs
  briefly pointing at half-archived destinations).

## OPEN QUESTIONS

_None outstanding — OQ-A through OQ-D were triaged and
promoted to the Decisions block above on 2026-05-28; the
seven additional sub-decisions auto-resolved at draft time
are also there. Scope is frozen; Phase 1 (Contract) opens
in the next session via `/ship-milestone M12`._

## Testing / Quality Gate

```sh
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/docs check docs/
.venv/bin/docs index --root docs/ --dry-run
rm -rf dist/ && .venv/bin/python -m build
.venv/bin/twine check dist/*
```

Plus the M12-specific dogfood at Phase 9:
- Project rename: copy `tests/fixtures/trees/real-trees-adopted/kebab-tiny/`
  to `/tmp/m12-dogfood-rename/`; run `docs project rename
  kebab-tiny gizmo`; verify every `Project:` line + the
  sidecar + INDEX consistent; second invocation
  (`docs project rename gizmo kebab-tiny`) returns the tree
  to its original state byte-for-byte (idempotency check).
- Touch outside root: create `/tmp/m12-dogfood-touch/random.md`
  (no `.docs.toml` ancestor); run `docs touch
  /tmp/m12-dogfood-touch/random.md`; assert exit 2 + file
  unchanged.
- Archive referring-edge rewrite: create a synthetic milestone
  trio in a throwaway docs root (`milestone.md`, `impl.md`,
  `status.md`), each with `Related:` edges to the others; run
  `docs archive milestone.md`; assert `impl.md` + `status.md`
  now reference the archive path.

## Success Criteria

M12 is complete when:

- [ ] `docs project rename <new>` works against the repo's own
      docs root: rename docs → docs-renamed → docs round-trips
      to byte-identical state; INDEX + dogfood snapshot
      regenerated in lockstep.
- [ ] `docs touch /tmp/no-docs-root/random.md` exits 2 + leaves
      `random.md` unchanged.
- [ ] `docs archive` of a doc with referring `Related:` edges
      rewrites the referring docs atomically (one INDEX refresh,
      no dangling edges).
- [ ] `python -c "from docs_cli.cli import __version__; print(__version__)"`
      prints `1.5.0` via `importlib.metadata`.
- [ ] `tests/test_packaging.py` A3 asserts and PASSES against
      the literal `"1.5.0"`.
- [ ] Full quality gate green tree-wide.
- [ ] `dist/docs_cli-1.5.0-*` built; `twine check` PASS.
- [ ] All Phase Checklist items above ticked.
- [ ] `docs/status.md` reflects M12 Complete + M13 next.
- [ ] `docs/m12-project-rename-impl.md` carries a
      milestone-completion summary describing what shipped,
      which OPEN QUESTIONS resolved which way, and any new
      open follow-ons surfaced during implementation.
