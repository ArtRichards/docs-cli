# M9 — PyPI publish 1.3.0

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-05-25

Related:
- parent-of: m9-pypi-publish-log.md
- child-of: plan.md
- pairs-with: release-runbook.md
- pairs-with: m6-pypi-distribution.md
- pairs-with: m7-migration-accuracy.md
- pairs-with: m8-adoption-workflow.md

## Overview

> **Stub-drafted 2026-05-24, post M6 scope reframe.** M9 enters
> active state once M8 ships. The operative checklist is
> [release-runbook.md](release-runbook.md); this milestone doc
> exists to give the publish work a named home, exit criteria,
> and a log to record what actually happened.

- Milestone: M9 (the v1.1 publish milestone)
- Title: PyPI publish `docs-cli` 1.3.0
- Surface: an operator-driven release of the post-M8 tree to PyPI
  as `docs-cli==1.3.0`, plus the public-flip of the GitHub repo,
  the v1.3.0 tag + GitHub release, and the post-publish doc
  closeouts that turn M6 / M7 / M8 / M9 rows in `status.md` and
  `plan.md` into `Complete (DATE)`.
- Status: **Complete (2026-05-25)** — `docs-cli==1.3.0` live at https://pypi.org/project/docs-cli/1.3.0/

### Goal

M6 delivered the packaging machinery — wheel build, entry point,
`install-skill` verb, runbook scaffold, GitHub repo. It did **not**
publish. The 2026-05-24 scope reframe split the publish out of M6
and parked it here so M6 could close cleanly rather than hang for
the M7 + M8 weeks at "implementation done, publish pending".

M9 is the publish. It is operator-driven by design: register PyPI
+ TestPyPI accounts, mint API tokens, bump versions, restructure
the CHANGELOG to cover M6 + M7 + M8, rebuild fresh artifacts,
TestPyPI rehearsal, real PyPI publish, post-release closeouts.
No code work; no new verbs; no TDD phases. The success criterion
is concrete: a fresh venv on a clean host can `pip install
docs-cli==1.3.0`, `docs --version` prints `docs 1.3.0`, `docs
install-skill` materialises a working bundled skill, and the
public GitHub repo carries the matching `v1.3.0` tag + release.

### Requirements

- **Version is `1.3.0`.** The batched M6 + M7 + M8 ship — one
  bump per implementation milestone — landing at 1.3.0. Intermediate
  versions `1.1.0` and `1.2.0` are never published (no public
  release exists to break continuity with). Recorded as a Decision
  in M6 and reaffirmed here.
- **Pre-publish operator prep** (account registration, 2FA, API
  tokens, `~/.pypirc`) is done in parallel with M7 / M8 so the
  publish window itself is purely `twine upload`. The runbook
  carries the per-step checklist.
- **Pre-publish tree state** (`pyproject.toml` version bump,
  `__version__` bump in `src/docs_cli/cli.py`, CHANGELOG
  restructure to add M7 + M8 sections under a `## 1.3.0 —
  UNRELEASED` header, `docs/INDEX.md` + fixture lockstep) is
  operator-executed at M9 start. The runbook carries the per-step
  checklist.
- **Quality gate green tree-wide** before any upload: pytest
  (≥ 271, raised by M7 + M8 — the actual count gets recorded into
  the runbook checklist at the moment of run), ruff, ruff format,
  mypy, `docs check docs/`, `docs index --root docs/ --dry-run`.
- **Fresh artifact build.** The May 23 M6 wheel + sdist sitting in
  local `dist/` are **not** uploaded. M9 rebuilds from the post-M8
  tree (`rm -rf dist/ && python -m build`), runs `twine check`,
  and exercises every install-skill code path in a throwaway
  local venv.
- **TestPyPI rehearsal is non-optional.** Upload to TestPyPI,
  install from TestPyPI into a fresh `/tmp/docs-test-venv`,
  exercise the smoke set. If anything fails, bump to `1.3.1`
  (TestPyPI also rejects re-uploads of the same version) and
  rerun from artifact build.
- **Real PyPI publish.** `twine upload dist/*` to PyPI, install
  from PyPI into a fresh `/tmp/docs-real-venv`, re-run the smoke
  subset against the real artifact.
- **Post-release sequence.** `gh repo edit ... --visibility
  public`, `git tag v1.3.0 && git push origin v1.3.0`, `gh release
  create v1.3.0`, re-scope PyPI API tokens from entire-account to
  project-`docs-cli`-scoped, doc closeouts (M6 / M7 / M8 / M9 rows
  in `status.md` and `plan.md` → Complete; `docs/INDEX.md` +
  `tests/fixtures/expected/docs-INDEX.md` regenerated in lockstep).

### Deliverables

- [ ] PyPI release `docs-cli` 1.3.0 published; project page live
      at `https://pypi.org/project/docs-cli/1.3.0/`.
- [ ] TestPyPI release `docs-cli` 1.3.0 published as the
      rehearsal artifact at `https://test.pypi.org/project/docs-cli/1.3.0/`.
- [ ] `pyproject.toml` `version` and `src/docs_cli/cli.py`
      `__version__` bumped from `1.1.0` to `1.3.0`.
- [ ] `CHANGELOG.md` carries a `## 1.3.0 — <DATE>` section
      describing the M6 + M7 + M8 surface.
- [ ] GitHub repo `ArtRichards/docs-cli` flipped from private to
      public.
- [ ] `v1.3.0` git tag pushed; GitHub release created with notes
      sourced from the CHANGELOG section.
- [ ] PyPI + TestPyPI API tokens re-scoped to project
      `docs-cli`; entire-account bootstrap tokens revoked.
- [ ] `docs/status.md`: M6 / M7 / M8 / M9 rows → Complete (DATE);
      "Current milestone" + "Next action" rewritten; v1.1
      declared shipped (or pointing at the v1.2 roadmap if one
      exists by then).
- [ ] `docs/plan.md`: M6 / M7 / M8 / M9 rows → shipped.
- [ ] `docs/m9-pypi-publish.md` (this file): Phase Checklist
      ticked; milestone-completion summary appended.
- [ ] `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md`
      regenerated in lockstep.

## Phase Checklist

M9 has no TDD code phases — it is an operational milestone. The
runbook's sections are the phases:

- [x] Operator one-time prep — accounts + 2FA + API tokens +
      `~/.pypirc` (token re-scope deferred to post-publish — see
      summary below)
- [x] Pre-publish prep — versions verified `1.3.0` (pre-bumped
      at M8 Phase 7), CHANGELOG already dated (M8 Phase 10),
      tree state clean, quality gate green (pytest 369 passed),
      fresh artifact build, local smoke
- [x] TestPyPI rehearsal — ran under disambiguated dist name
      `docs-cli-rehearsal==1.3.0` because the bare `docs-cli`
      name was parked on TestPyPI by an unrelated user
- [x] Real PyPI publish — `docs-cli==1.3.0` live; sha256
      chain-of-custody from build → upload → PyPI-served wheel
      verified bit-perfect
- [x] Post-release — repo public, `v1.3.0` tag + GitHub release,
      doc closeouts; token re-scope handed back to the operator
      as out-of-band account-UI work

Each ticks as the runbook's corresponding section completes.

## Decisions

- **Version is 1.3.0** (reaffirms M6 + plan.md decision). One
  bump per implementation milestone: M6 = 1.1.0, M7 = 1.2.0,
  M8 = 1.3.0; only the M8-ship version reaches PyPI.
- **Manual `twine`, not Trusted Publishing.** Continues the M6
  stance. OIDC / GitHub-Actions Trusted Publishing is a
  future-iteration follow-up if the manual flow proves cumbersome
  at v1.4 / v2.
- **TestPyPI rehearsal is mandatory**, not a "nice to have."
  PyPI is append-only; a bad upload burns the version number.
- **Fresh artifacts at M9, not the May 23 M6 build.** The M6
  artifacts predate M7 + M8 code changes and the version bump.
- **GitHub repo flip to public happens at M9 post-release**,
  not earlier — keeps the repo private until the artifact is
  live and verified working.

## Testing / Quality Gate

The same tree-wide gate the other v1.1 milestones run, plus the
publish-specific smokes the runbook details:

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

Plus the M9-specific dogfood: walk [release-runbook.md](release-runbook.md)
end-to-end against TestPyPI then real PyPI.

## Success Criteria

M9 is complete when:

- [ ] `pip install docs-cli==1.3.0` works from PyPI on a clean
      host with Python 3.11+ and produces a working `docs` command.
- [ ] `docs install-skill` from the PyPI-installed wheel places a
      host-correct skill that drives the verbs identically to the
      in-repo install.
- [ ] The GitHub repo `ArtRichards/docs-cli` is public; the
      `v1.3.0` tag and release exist.
- [ ] All Phase Checklist items above are ticked.
- [ ] `docs/status.md` reflects M6 / M7 / M8 / M9 as Complete
      with the actual publish date.
- [ ] `docs/m9-pypi-publish-log.md` carries a
      milestone-completion summary describing what actually
      happened (which `1.3.x` shipped — if TestPyPI surfaced a
      bug forcing a `1.3.1` rebuild, the published version, the
      sha256 of the published wheel + sdist, the publish
      timestamp, any deviations from the runbook).

## OPEN QUESTIONS

_None at draft time. Open questions surfaced during the
2026-05-25 walk (TestPyPI name parked → disambiguated rehearsal
name; stale `gh repo edit` flag) are recorded in the
Milestone-completion summary below._

## Milestone-completion summary

**Shipped 2026-05-25** — `docs-cli==1.3.0` is the first public
release of docs-cli; the v1.1 line ships.

### Published artefact

- **PyPI:** https://pypi.org/project/docs-cli/1.3.0/
- **Version:** `1.3.0` (the M8 version number; M6=1.1.0 and
  M7=1.2.0 never reached PyPI by design)
- **Wheel sha256:**
  `27afbde7d1e2452c6c9e52b8a1a0e01f1ff876fcaa0543e2e1b1a34ea21898da`
  (`docs_cli-1.3.0-py3-none-any.whl`, 76.4 KB)
- **Sdist sha256:**
  `59d36ef2851141aaa92da691e22d602df56b47f3febb7ac74583ea72fa16d2dd`
  (`docs_cli-1.3.0.tar.gz`, 428.8 KB)
- **PyPI install timestamp (UTC):** 2026-05-25T11:20:24Z (from
  the post-publish smoke install)
- **Source tag:**
  https://github.com/ArtRichards/docs-cli/releases/tag/v1.3.0
  (lightweight tag at HEAD, M8 simplify commit `6e84906`)
- **Chain-of-custody:** the wheel pip-downloaded from PyPI
  post-publish has sha256 byte-identical to the uploaded
  wheel; no rebuild between TestPyPI rehearsal and real PyPI
  publish was needed (rehearsal ran under a temporary dist
  name, see below).

### What shipped (the M6 + M7 + M8 surface)

- **M6 (was 1.1.0 internal).** PyPI distribution as `docs-cli`,
  `docs install-skill` verb, the bundled Claude Code skill as
  package data, the `src/docs_cli/` package layout. Stays the
  default install path; `pip install docs-cli` lands `docs` on
  PATH via the `[project.scripts] docs = "docs_cli.cli:main"`
  entry point.
- **M7 (was 1.2.0 internal, breaking).** Controlled-vocab
  field rename `Status:` → `Lifecycle:` (no backward-compat
  alias), `docs list --status` → `--lifecycle`, JSON schema
  field rename, `add_statuses` → `add_lifecycles`, broadened
  role inference (suffix + H1 + section-header + sibling-set
  defaulting, 7 new core role vocab additions, `_v\d+` /
  `_Draft` / `_Ready` non-role suffix stripping, `_M\d+`
  milestone-pattern), `--config-project` migrate flag, project-
  name normalisation to lowercase-kebab, per-file mtime archive
  moves, medium-confidence level with `docs check` exit-1
  warnings.
- **M8 (was 1.3.0 internal, additive).** Tree-wide `--exclude`
  on `migrate` + `index` + `check` + `list`, `[exclude]`
  table in `.docs.toml` (`dirs` / `globs` / `exts`), root
  `.docsignore` parser, `--summary` / `--only ambiguous` /
  `--group-by` triage flags on `migrate`, default plan-footer
  summary, non-md sibling surfacing, `docs new --body-from
  <PATH|->`, substantial bundled-skill rewrite for adoption
  (new `references/adoption-playbook.md` + commented
  `references/docs-toml-template.toml`).

### Deviations from the runbook (recorded for v1.4+)

1. **CHANGELOG date-stamp at Hand-off 3 was a no-op.** The
   runbook expected the operator to replace
   `## 1.3.0 — UNRELEASED` with the publish date during the
   real-PyPI block; M8 Phase 10 had already dated it at
   `2026-05-25`. The runbook's "replace UNRELEASED with today's
   date" step still applies if a future release hits M9 with an
   UNRELEASED header.
2. **TestPyPI dist-name detour.** The bare project name
   `docs-cli` was parked on TestPyPI by an unrelated user
   (Paulo Guilherme Pilott, "Um toolkit para processamento e
   avaliação de documentação", v0.1.0). The TestPyPI rehearsal
   ran under the disambiguated dist name
   `docs-cli-rehearsal==1.3.0`; `pyproject.toml`'s
   `[project] name` was temporarily renamed for the rehearsal
   build and reverted before the real PyPI build (resulting
   real-PyPI artefacts byte-identical to the original Block B
   build). The runbook's `## Notes` block now carries this
   caveat for future operators.
3. **`gh repo edit` flag `--accept-visibility-change-consequences`
   does not exist** in the installed `gh` 2.x; `gh` prompts
   interactively instead. Runbook patched in lockstep.
4. **GitHub release notes are hand-augmented**, not bare-awk.
   The CHANGELOG's `## 1.3.0` section is M8-centric (the M7 and
   M6 detail lives in `## 1.2.0` and `## 1.1.0` respectively,
   neither of which was published as a separate PyPI release).
   The release-notes file at
   `https://github.com/ArtRichards/docs-cli/releases/tag/v1.3.0`
   prefixes the awk-extracted body with a short preamble
   calling out first-public-release status and pointing readers
   at the earlier CHANGELOG sections.
5. **Token re-scope was deferred** as out-of-band operator UI
   work. The PyPI + TestPyPI tokens currently in `~/.pypirc`
   remain entire-account-scoped at the moment of this
   summary's writing. Operator re-scopes to
   project-`docs-cli` + project-`docs-cli-rehearsal` and
   revokes the bootstrap tokens at their convenience.

### Quality gate at publish

- pytest **369 passed** (M6 baseline 271 + M7/M8 additions
  98); no skipped tests, no warnings beyond pytest defaults.
- ruff `check .`, ruff `format --check .`, mypy (34 source
  files), `docs check docs/`, `docs index --root docs/
  --dry-run` — all clean.
- `twine check dist/*` PASSED on both the real and rehearsal
  artefacts.

### Open follow-ons

- **Token re-scope** (operator, async).
- **Trusted Publishing / OIDC** still parked as a future
  iteration. Manual `twine` proved fine at v1.1; revisit at
  v1.4 / v2 if the manual flow proves cumbersome.
- **Re-check TestPyPI `docs-cli` ownership** at future
  release windows. If the squatter project ever lapses, drop
  the rehearsal-name detour. Until then, future releases
  continue under a disambiguated TestPyPI dist name.
- **Single-source-of-truth versioning.** Version is still
  hardcoded in `pyproject.toml` + `src/docs_cli/cli.py`'s
  `__version__`. Migrating to `importlib.metadata` is parked
  as a future-iteration note (M6 plan's "What's deliberately
  deferred").

The release-runbook stays the operative reference for the
next release (v1.4+).
