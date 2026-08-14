# M9 — PyPI publish 1.3.0 (log)

Lifecycle: archived
Role: log
Project: docs
Updated: 2026-08-14

Related:
- child-of: archive/2026-05-25/m9-pypi-publish.md
- pairs-with: release-runbook.md

Revision:
- 2026-08-14: M27 one-time body-link migration; body-link destinations repaired (destination tokens only)

Per-phase log for M9. Entries appended as the operator walked
[release-runbook.md](../../release-runbook.md) post-M8.

## Phase progress

| Phase | Status | Notes |
|---|---|---|
| Operator one-time prep | Complete (2026-05-25) | accounts + 2FA + tokens + `~/.pypirc` (scaffolded by Claude with placeholder tokens, operator pasted real tokens, chmod 600 re-applied after editor reset perms to 764) |
| Pre-publish prep | Complete (2026-05-25) | versions verified `1.3.0` (M8 Phase 7 had pre-bumped), CHANGELOG already dated `2026-05-25` (M8 Phase 10), tree state clean, quality gate green (pytest 369 passed; ruff/format/mypy/`docs check`/`docs index --dry-run` all clean), fresh artifact build, `twine check` PASSED, local-install smoke clean |
| TestPyPI rehearsal | Complete (2026-05-25) | bare name `docs-cli` was parked on TestPyPI by another user (Portuguese docs toolkit, v0.1.0) — used disambiguated dist name `docs-cli-rehearsal==1.3.0`; smoke install + `docs --version` + `install-skill` (byte-identical) + `--symlink` exit 2 + `docs check` exit 0 all green; reverted pyproject for real publish |
| Real PyPI publish | Complete (2026-05-25 ~11:20Z) | `twine upload dist/*` → two 200 OKs; smoke install from PyPI confirmed `docs 1.3.0` and byte-identical bundled-skill output; downloaded-from-PyPI wheel sha256 matches uploaded sha256 (`27afbde…21898da`) |
| Post-release | Complete (2026-05-25) | repo public via `gh repo edit --visibility public` (the runbook's `--accept-visibility-change-consequences` flag was stale in the installed `gh` 2.x — runbook patched in lockstep), `v1.3.0` tag pushed, GitHub release created with hand-augmented notes (preamble calling out first-public-release + M6/M7/M8 batching + body from the `## 1.3.0` CHANGELOG section), token re-scope handled by operator (out-of-band UI work), doc closeouts landed in lockstep |

## Entries

### 2026-05-24 — stub created

M9 stub-drafted as part of the M6 scope reframe. The milestone
exists; activates once M8 ships. No prep work has started.

### 2026-05-25 — activated (M8 shipped locally)

M8 closed at Phase 10 with `dist/docs_cli-1.3.0-*` built locally
+ `twine check` PASS; per OQ-C the publish flip was deferred to
this milestone. M9 row in `status.md` flipped from
`stub-drafted` to `Activated`.

### 2026-05-25 — executed end-to-end via `/ship-milestone` interactive walk

The publish session ran under `/ship-milestone M9 for docs-cli`.
The skill's TDD-conductor pattern doesn't fit a publish
milestone (no code phases, no fresh-eyes review, several
operator-credentialed steps); the operator chose the "walk the
runbook interactively" path. Two participants:

- **Claude** drove the agent-doable blocks: state
  verifications + tree-wide quality gate, fresh artifact
  build + `twine check` + local-install smoke, TestPyPI smoke
  install (after operator upload), real PyPI smoke install
  (after operator upload), `v1.3.0` tag + push + GitHub
  release, doc closeouts.
- **Operator** drove the credentialed steps: account
  registration / 2FA / token minting (one-time prep);
  `~/.pypirc` token paste (Claude scaffolded the file
  structure); `twine upload --repository testpypi dist/*`;
  `twine upload dist/*`; `gh repo edit --visibility public`;
  PyPI + TestPyPI API token re-scope (account-UI work).

#### Block A — verifications + quality gate (Claude)

Versions verified: `pyproject.toml` `version = "1.3.0"`,
`src/docs_cli/cli.py` `__version__ = "1.3.0"` — pre-bumped at
M8 Phase 7. CHANGELOG already carried
`## 1.3.0 — 2026-05-25` (dated at M8 Phase 10), so the
runbook's "replace UNRELEASED with today's date" step at the
real-publish block was a no-op. Quality gate: **pytest 369
passed** (vs M6's 271 baseline; M7+M8 added 98), ruff clean,
ruff format clean (33 files), mypy clean (34 source files),
`docs check docs/` exit 0, `docs index --root docs/ --dry-run`
exit 0. PyPI name `docs-cli` confirmed 404 (available).

#### Block B — fresh artifact build + local smoke (Claude)

`rm -rf dist/ build/ src/docs_cli.egg-info && python -m build`
produced fresh `docs_cli-1.3.0-py3-none-any.whl` (76.4 KB) +
`docs_cli-1.3.0.tar.gz` (428.8 KB). `twine check`: both
PASSED. sha256 of built artifacts:

- wheel: `27afbde7d1e2452c6c9e52b8a1a0e01f1ff876fcaa0543e2e1b1a34ea21898da`
- sdist: `59d36ef2851141aaa92da691e22d602df56b47f3febb7ac74583ea72fa16d2dd`

Local install smoke in `/tmp/docs-local-smoke`: install OK,
`docs --version` → `docs 1.3.0`, `docs --help` listed every
M7/M8 verb addition (`install-skill`, `migrate`, etc.),
`docs install-skill --dest /tmp/skill-smoke` exit 0 with
byte-identical-to-bundled diff, idempotent re-run exit 0 with
"already matches" message, `--symlink` exit 2 with the
documented wheel-install refusal, `docs check
tests/fixtures/trees/minimal/` exit 0.

#### Hand-off 1 — operator one-time prep (operator)

TestPyPI + PyPI accounts pre-registered with 2FA + API
tokens. Claude scaffolded `~/.pypirc` (chmod 600) with
clearly-flagged placeholder slots; operator pasted real
tokens. Editor save reset perms to 764 (world-readable);
Claude re-applied `chmod 600` after the operator confirmed
the token paste was complete. Sanity check (without exposing
tokens): 2 `password = pypi-…` lines, 0 `REPLACE_ME` slots, 3
sections (`[distutils]` / `[pypi]` / `[testpypi]`).

#### Hand-off 2 — TestPyPI upload (operator)

First attempt: `twine upload --repository testpypi dist/*` →
**HTTP 403** "The user 'ArtRichards' isn't allowed to upload
to project 'docs-cli'". TestPyPI confirmed via JSON API that
the bare name `docs-cli` is parked by another user (Paulo
Guilherme Pilott, Portuguese-language "Um toolkit para
processamento e avaliação de documentação", v0.1.0). Real
PyPI was still 404 (clean) — TestPyPI and PyPI have separate
namespaces. Standard PyPA workaround applied: temporary
disambiguated dist name on TestPyPI only, real PyPI publish
unchanged.

Operator picked `docs-cli-rehearsal` (free on both indexes).

**Block B' (Claude)** — edited `pyproject.toml` `[project]
name` from `docs-cli` to `docs-cli-rehearsal` (uncommitted);
wiped + rebuilt; produced
`docs_cli_rehearsal-1.3.0-py3-none-any.whl` (76.5 KB) +
`docs_cli_rehearsal-1.3.0.tar.gz` (429.4 KB); `twine check`
PASSED on both. Wheel METADATA confirmed only the dist Name
field changed (`Name: docs-cli-rehearsal`); contents
unchanged — same `docs_cli/cli.py`, same 6 bundled-skill
entries.

Operator retried TestPyPI upload — two 200 OKs at
`https://test.pypi.org/project/docs-cli-rehearsal/1.3.0/`.

#### Block C — TestPyPI install smoke (Claude)

`/tmp/docs-test-venv`,
`pip install --index-url https://test.pypi.org/simple/
--extra-index-url https://pypi.org/simple/
docs-cli-rehearsal==1.3.0`. `docs --version` →
`docs 1.3.0` (the entry-point name `docs` is decoupled from
the dist name). `docs install-skill --dest /tmp/docs-test-skill`
exit 0 + byte-identical diff. `--symlink` exit 2.
`docs check tests/fixtures/trees/minimal/` exit 0.
`docs index --root docs/ --dry-run` exit 0.

#### Block B'' — revert pyproject + rebuild real docs-cli artifacts (Claude)

Reverted `[project] name` to `docs-cli`. Wiped + rebuilt:
fresh `docs_cli-1.3.0-*` artifacts. **sha256 byte-identical
to the Block B build** (`27afbde…` wheel + `59d36ef…` sdist) —
confirms the rehearsal-name change was a clean inverse and the
real PyPI bytes match what the Block B local smoke already
validated. `twine check` PASSED. `git status -s` empty.

#### Hand-off 3 — real PyPI upload (operator)

`twine upload dist/*` → two 200 OKs.
`https://pypi.org/project/docs-cli/1.3.0/` is live.

#### Block D — real PyPI install smoke (Claude)

`/tmp/docs-real-venv`, `pip install docs-cli==1.3.0` (no
TestPyPI index needed — real publish). `docs --version` →
`docs 1.3.0`. `docs install-skill --dest /tmp/docs-real-skill`
exit 0 + byte-identical diff.
`docs check tests/fixtures/trees/minimal/` exit 0. UTC
timestamp at PyPI install: **2026-05-25T11:20:24Z**.

Bit-perfect chain-of-custody check: re-downloaded the wheel
from PyPI via `pip download --no-deps`; sha256 of the
PyPI-served wheel matched the uploaded sha256 exactly
(`27afbde7d1e2452c6c9e52b8a1a0e01f1ff876fcaa0543e2e1b1a34ea21898da`).

#### Hand-off 4 part 1 — public flip (operator)

`gh repo edit ArtRichards/docs-cli
--accept-visibility-change-consequences --visibility public`
**rejected the unknown flag** — that flag is not present in
the installed `gh` 2.x. Drop the flag; the bare
`gh repo edit ArtRichards/docs-cli --visibility public`
prompts interactively for confirmation. Operator confirmed,
repo flipped public. Runbook patched in lockstep (Block F).

#### Block E — v1.3.0 tag + GitHub release (Claude)

Lightweight `v1.3.0` tag at HEAD (the M8 simplify commit
`6e84906`); `git push origin v1.3.0` succeeded.
`gh release create v1.3.0 --title "docs-cli 1.3.0"
--notes-file /tmp/release-notes.md`. Release notes
hand-authored: a short preamble calling out first-public-release
+ M6/M7/M8 batching with explicit pointers to the
`## 1.2.0` and `## 1.1.0` sections of `CHANGELOG.md` (M7 + M6
detail is in those sections; the `## 1.3.0` section is
M8-focused with a Notes block on batching). Body sourced via
the runbook's awk extraction of the `## 1.3.0` section (104
lines). Release at
`https://github.com/ArtRichards/docs-cli/releases/tag/v1.3.0`.

#### Hand-off 4 part 2 — token re-scope (operator, async)

The PyPI + TestPyPI re-scope-to-project + bootstrap-revoke is
account-UI work; operator handles out-of-band post-publish.
Not blocking Block F. **Reminder for the operator if not yet
done:** the `pypi-AgEI…` (PyPI) and `pypi-AgEN…` (TestPyPI)
tokens currently in `~/.pypirc` are entire-account-scoped;
re-mint as project-scoped now that the projects exist on each
index, swap into `~/.pypirc`, `chmod 600` after the editor
save, revoke the originals.

#### Block F — doc closeouts (Claude)

- `docs/status.md`: "Current milestone" + "Next action" +
  "Publish is M9" callout + outdated reading-order section
  + `pytest` count rewritten to reflect M9 shipped; M9 row in
  the Milestone progress table flipped to **Complete
  (2026-05-25, `docs-cli==1.3.0` on PyPI)**; "v1.1 is in
  flight" rewritten to "docs-cli 1.3.0 shipped 2026-05-25"
  (release version is 1.3.0; "v1.1" was the internal backlog
  grouping name, not the published version).
- `docs/plan.md`: v1.1 intro paragraph past-tense; M9 row →
  Complete; "**M9** is the publish milestone" paragraph
  rewritten past-tense with the published URL.
- `docs/m9-pypi-publish.md`: `Lifecycle:` stays `active`
  per convention (completed milestones keep `active` while
  the doc lives in the active tree — confirmed against M6,
  M7, M8 logs); Phase Checklist boxes ticked; **Milestone-
  completion summary** appended with published version,
  wheel/sdist sha256, publish timestamp, deviations
  (`docs-cli-rehearsal` TestPyPI rehearsal name, stale
  `gh` flag, token re-scope deferred).
- `docs/m9-pypi-publish-log.md` (this file): per-phase
  entries appended; `Lifecycle:` stays `active` per
  convention.
- `docs/m7-migration-accuracy.md`: appended **M9 publish
  flip** section with the published URL + artifact sha256.
- `docs/m8-adoption-workflow.md`: same publish-flip section
  noting M8's 1.3.0 is the version-source-of-truth for the
  batched publish.
- `docs/release-runbook.md`: intro flipped to past-tense
  ("drove M9 — `docs-cli==1.3.0` shipped 2026-05-25");
  TestPyPI rehearsal-name caveat added; stale
  `--accept-visibility-change-consequences` flag removed;
  remains the operative reference for v1.4+.
- `docs/INDEX.md` regenerated via `docs index --root docs/`;
  `tests/fixtures/expected/docs-INDEX.md` lockstep-updated
  (the snapshot test `test_cli_index.py` exercises this).
- Final tree-wide gate re-run: pytest, ruff, ruff format,
  mypy, `docs check docs/` all clean.
- `/tmp/docs-*-venv` + `/tmp/docs-*-skill` + `/tmp/skill-smoke`
  + `/tmp/docs-real-download` + `/tmp/release-notes.md`
  cleanup.
- Single commit on `main`.

### 2026-05-25 — M9 complete

All five phases complete; `docs-cli==1.3.0` published, repo
public, `v1.3.0` tag + GitHub release live, doc closeouts
landed. **docs-cli 1.3.0 is live** — the first public release;
closes the M6 → M9 backlog grouping internally tracked as
"v1.1".
