# M31 — Publish docs-cli 2.1.0 to PyPI — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-10-28

Related:
- pairs-with: pypi-publish-2-1-0.md
- pairs-with: pypi-publish-2-1-0-test-matrix.md

## Overview

This is the chronological implementation log for M31 — Publish docs-cli 2.1.0
to PyPI (semantic slug `pypi-publish-2-1-0`). Each TDD phase gets one
evidence-backed section, and the progress table, the milestone checklist and
the test matrix stay synchronized with it. The phases are the
[release-runbook.md](release-runbook.md) mapped onto ship-milestone's steps
(task plan D3). No phase changes product code (D1).

## Implementation metadata

- Project: docs
- Milestone: `pypi-publish-2-1-0` — M31, Publish docs-cli 2.1.0 to PyPI
- Tracker: order 200, `active` since the claim commit `be7f809`. It depends on
  `lifecycle-and-free-form-relate` (order 100, `complete`, archived
  2026-10-28). See [milestone-plan.md](milestone-plan.md).
- Started: 2026-10-28 (milestone setup; no TDD phase started)
- Progress: **Milestone setup complete (2026-10-28). Q1 and Q2 are RESOLVED
  by the operator. The four blockers of Step 0 review-pass-001 and all of its
  other findings are fixed; the pass closes at final sync. Phase 1 — Define
  Contract is next.**
  - Setup measured the publish surface read-only, recording thirteen pieces of
    evidence (**E1–E13**, below). It built, uploaded, installed and published
    nothing, and touched neither `~/.claude/skills` nor `~/.pypirc`.
  - The task plan holds the operator decisions (D2, D3, D10 and D13), and its
    *Current state and evidence* names the three findings that reshape the
    runbook.
- Source: the canonical tracker row (`193fc71`), and M30's hand-off in
  [feedback-log.md](feedback-log.md) (2026-10-26 entry, *Hand-off*).
- Branch: `pypi-publish-2-1-0/milestone-setup` for setup. Implementation
  follows the ship-milestone stack: `pypi-publish-2-1-0/phases-1-4`,
  `…/phases-5-10` and `…/simplify`.

## Risk / Adequacy Tracking

- Risk level: **Standard**, proposed at setup and accepted by the conductor's
  triage (2026-10-28). The task plan's *Risk Level* records the reasoning and
  why High is not proposed.
- Test matrix:
  [pypi-publish-2-1-0-test-matrix.md](pypi-publish-2-1-0-test-matrix.md)
- High-risk RED approval: not applicable. Standard risk has no Phase-4
  operator checkpoint; Step 1's dual-provider review is the gate before the
  upload (D2).
- Hidden/generalization handling: categories only, since the repository is
  fully visible. They are exercised by the three-build probe replay and the
  2.0.0 control.
- Mock audit: no mocks planned. Every check is real-path.
- Adequacy results: pending.
- Taste triage: pending. Each review finding is fixed, or waived with a logged
  reason.

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Pending | — | Release contract frozen against D1–D13, which carry the answers to Q1 and Q2: each script's check list and expected values (from `cli.md`, the CHANGELOG, M30's and M29's contracts); the scratch layout; the command lines; the stop table; the sdist download method; the backend-pin mechanism; the runbook correction list. The per-release re-verification of E1–E4 is re-run the same day. |
| 2. Write Tests (RED) | Pending | — | `tests/manual/release_readiness.py` and `tests/manual/release_probe.py`. Readiness is RED for exactly five reasons: the `UNRELEASED` heading, the publish-state sentence, and the `touch`, `stamp` and `project set` synopses. The probe's contract group is GREEN on the editable build. The host 2.0.0 control behaves as Phase 1 froze it. A hand-applied mutation smoke covers eight targets. |
| 3. Create Data/Fixtures | Pending | — | The CHANGELOG is dated and its sentence removed (D7). The three README synopses are reconciled (D8). Probe trees are built inline or copied to scratch. Readiness turns GREEN. |
| 4. Run Tests (RED Baseline) | Pending | — | A pre-publish GREEN baseline (D3). The gate; then build (a) per D4, with its sdist member manifest recorded; then `twine check` and the manifests. Both probe groups run on (a). The rehearsal follows, with D4's byte checks and both probe groups, and ends with (b) = (a). GO recorded. |
| 5. Update Base Interfaces | Pending | — | The stop-table preconditions; a re-date per D7 if needed; build (c) per D4; `twine check`; (c) = (a); the sdist members against the Phase 4 manifest; `dist/` holding exactly two files. |
| 6. Implement Offline/Core Path | Pending | — | The upload under D2, naming both files explicitly. The per-version JSON's digests equal (c)'s. |
| 7. Update Tool/Wrapper Layer | Pending | — | Served verification first: the shas against (c), both probe groups, and the suite's capability probes. Only then the tag and the release (D13), with the peeled-tag check. |
| 8. Run Tests (GREEN) | Pending | — | The GREEN record: readiness and the full fast gate at the tag-target commit; the three-wheel probe results in the matrix; the suite full guard's expected failure. |
| 9. Integrate / Accept / Dogfood | Pending | — | Host integration per D10, with the task plan's Phase 9 commands: the update notice from the 2.0.0 binary, then the binary, the skill, the sweep, a dogfood `docs check`, and the liveness walk. |
| 10. Quality, Docs, Refactor | Pending | — | The runbook's *From M31* lessons and its corrections (D11). The feedback-log hand-off update (D12). The status narrative. The final matrix results. Taste triage and the boundary sweep. Scratch cleanup. The completion summaries. |

## Setup record — 2026-10-28

### Objective

Create the task plan, this log and the test matrix for the claimed row, link
them, and promote them to `active`, without starting Phase 1. The setup
measures the publish surface read-only, maps the runbook onto ship-milestone
as the operator chose (D3), and records the operator's upload authorization
(D2). Nothing irreversible happens, and no host or credential file is
written.

### Actions taken

- **Read the inputs end to end:**
  - `CLAUDE.md` (*Skill update flow*);
  - the `create-milestones` skill, with its playbook and phase reference;
  - ship-milestone and its prompts;
  - the shared quality model, the tracker contract and the
    operator-interaction policy;
  - [milestone-plan.md](milestone-plan.md): its tracker row and *Ongoing
    conventions*;
  - [release-runbook.md](release-runbook.md) in full, *Cumulative lessons*
    included;
  - [feedback-log.md](feedback-log.md): every open entry, and especially the
    2026-10-26 hand-off;
  - `CHANGELOG.md`, `README.md` and `pyproject.toml`;
  - [charter.md](charter.md) and
    [definition-of-ready.md](definition-of-ready.md);
  - [status.md](status.md).
- **Read the precedents:**
  - M29's [task plan](archive/2026-08-16/m29-pypi-publish-2-0-0.md) and
    [log](archive/2026-10-26/m29-pypi-publish-2-0-0-impl.md);
  - M30's trio, both [as finally archived](archive/2026-10-28/lifecycle-and-free-form-relate.md)
    and at its setup commits `f8ec7f0` and `e48adb9`.
- **Ran read-only probes** of:
  - the PyPI and TestPyPI JSON APIs;
  - the shape of `~/.pypirc` — mode, sections, `username`, `password` prefix
    and length only; **no value printed**;
  - the release toolchain;
  - the full quality gate;
  - the CHANGELOG and README release inputs;
  - git, the remote tags and the GitHub releases and issues;
  - the host binary, the host skills directory (listing only, no content
    read) and docs-cli's own state file;
  - the Agent Playbook Suite's repository and installed plugin (E1–E13).
- **Validated the physical identity.** No live or archived basename uses
  `pypi-publish-2-1-0.md`, `-impl.md` or `-test-matrix.md`, and the only
  branch under `pypi-publish-2-1-0/` is `milestone-setup`.
- **Rehearsed the two archived-endpoint pairs on a throwaway copy** of
  `docs/` in the session scratchpad first. `docs relate` without `--reason`
  refused at exit 2. With `--reason`, it wrote the recognized bullets and two
  audited `Revision:` bullets on the archived M30 document, with lifecycle,
  `Archived:`, `Archived-reason:` and prose byte-identical, and `docs check`
  was clean.
- **Scaffolded the three documents.** Each was made with `docs new`
  (`milestone`, `log`, `spec`) and `--body-from`. Edges were linked with
  `docs relate add`, and all three were promoted with one `docs lifecycle …
  active` (see the next section).
- **Synchronized the tracker relationships** with `docs relate add … --reason
  "Synchronize pypi-publish-2-1-0 with milestone tracker"`:
  - `archive/2026-10-28/lifecycle-and-free-form-relate.md` `precedes`
    `pypi-publish-2-1-0.md` (100 → 200);
  - `pypi-publish-2-1-0.md` `depends-on` the same document.
- **Replaced the tracker row's plain Milestone cell** with
  `[pypi-publish-2-1-0](pypi-publish-2-1-0.md)`. Order, state (`active`),
  dependency and Notes are preserved.
- **Recorded two feedback-log notes:**
  - the 2026-10-26 hand-off now names this milestone as the owner of its
    items 1–3;
  - the 2026-10-28 candidate convention records that it was offered here and
    adopted as a taste-anchor trial.
- **Updated the narrative and the INDEX.** Added a short setup paragraph to
  `status.md`. Regenerated the INDEX with `docs index .` and refreshed the
  snapshot `tests/fixtures/expected/docs-INDEX.md` in lockstep.

### Metadata edits and the route used for each

docs-cli 2.1.0's development build (`.venv/bin/docs`) now has a verb for every
metadata edit the workflow prescribes, so **no metadata block was hand-edited**.
This is M30's primary use case, run for real.

| Document | Edit | Route |
|---|---|---|
| all three artifacts | the metadata block (`Lifecycle: draft`, `Role`, `Project: docs`, `Updated`) | `docs new <role> <stem> --project docs --title … --body-from <file>` |
| `pypi-publish-2-1-0.md` | `child-of: milestone-plan.md`, `implements: charter.md`, `pairs-with:` the log, the matrix, `release-runbook.md` and `status.md`, and `references: feedback-log.md` | `docs relate add` (free-form, one-sided) |
| `pypi-publish-2-1-0-impl.md` | `pairs-with:` the task plan and the matrix | `docs relate add` |
| `pypi-publish-2-1-0-test-matrix.md` | `pairs-with:` the task plan and the log | `docs relate add` |
| `pypi-publish-2-1-0.md` ↔ `archive/2026-10-28/lifecycle-and-free-form-relate.md` | `follows` / `precedes` and `depends-on` / `required-by` | `docs relate add … --reason …` (recognized pairs, with an audited `Revision:` bullet on the archived endpoint) |
| all three artifacts | `Lifecycle: draft` → `active` | one `docs lifecycle <plan> <log> <matrix> active` |

M30's *Follow-ups* item 6 declined a `parent-of` back-edge on
`milestone-plan.md`, so none is written.

### Readiness evidence (measured 2026-10-28, at `be7f809`)

| Evidence | Measurement | Why it matters | Bears on |
|---|---|---|---|
| **E1** | **PyPI.**<br>- `curl -sI https://pypi.org/simple/docs-cli/` returns `HTTP/2 200`.<br>- The JSON lists `info.version` `2.0.0` and the releases `1.3.0, 1.4.0, 1.5.0, 1.6.0, 1.6.5, 1.8.0, 2.0.0`.<br>- `https://pypi.org/pypi/docs-cli/2.1.0/json` returns **404**.<br>- The served 2.0.0 digests are `bcd8aa45…` (wheel) and `c62f22d3…` (sdist), uploaded 2026-08-16T09:21Z — exactly M29's chain-of-custody anchors. | The `2.1.0` slot is free. The registry still serves exactly what M29 verified. | D2 preconditions; Phase 1 re-check |
| **E2** | **TestPyPI.**<br>- Bare `docs-cli` is still the unrelated project: `0.1.0` only, `author` `None`, summary "Um toolkit para processamento e avaliação de documentação." — unchanged since M9.<br>- `docs-cli-rehearsal` lists `1.3.0 … 2.0.0`, and its `2.1.0` per-version endpoint returns **404**. | The rehearsal-name detour continues, and its `2.1.0` slot is free. D9's `.postN` versions are free too. | Phase 4, D9 |
| **E3** | **Credentials, shape only.**<br>- `~/.pypirc`: mode `600`, mtime 2026-10-28 16:57 (operator-copied today from the operator's other host).<br>- Sections: `[distutils]` (`index-servers` = `pypi`, `testpypi`), `[pypi]` and `[testpypi]`.<br>- Both have `username = __token__` and a `password` that starts `pypi-` and is longer than 100 characters. `[testpypi]` has `repository = https://test.pypi.org/legacy/`.<br>- **No value was printed.**<br>- `gh auth status`: logged in as `ArtRichards` over SSH, with the `repo` scope. | Upload and tag/release access are in place. The PyPI token's validity is proven only by use (M11), at Phase 6. | D2, D6, Phase 6 assumption |
| **E4** | **Toolchain.**<br>- `.venv`: `twine` 7.0.0 (the newest on PyPI; satisfies M29 — D1, and `[dev]` carries `twine>=7.0.0`), `build` 1.5.0, `packaging` 26.2, `readme_renderer` 44.0, Python 3.12.3.<br>- `[build-system] requires = ["hatchling"]` is **unpinned**. PyPI's newest `hatchling` is **1.33.0, uploaded 2026-10-28T02:27Z — today**. Its own wheel serves `Metadata-Version: 2.5`, which twine 7.0.0 accepts (M29 — E3/D1).<br>- Nothing was built at setup. | The first build resolves a backend published hours ago, and a later one may resolve a newer one. Step 2's rebuild can therefore drift from the wheel Step 1 rehearsed, which motivates D4's sha rule and its pin remedy. No metadata-version trap is indicated. | D4, Phase 4 |
| **E5** | **The gate at `be7f809`.**<br>- `pytest -q`: **1671 passed**.<br>- `ruff check .`: clean. `ruff format --check .`: 50 files formatted. `mypy src/ tests/`: no issues in 51 files.<br>- `docs check .`: exit 0.<br>- `docs check . --stale 14`: exit 1, with five `stale` warnings on evergreen documents (`charter.md`, `definition-of-ready.md`, `dual-status-adr.md`, `release-runbook.md`, `vocab-adr.md`). Reviewed: they predate this milestone.<br>- `docs index . --dry-run` is byte-identical to `INDEX.md`.<br>- `INDEX.md` equals its snapshot.<br>- Both bundled references are byte-identical to `docs/`.<br>- The M30 stale-wording grep over the `relate` / `lifecycle` help, the skill, the specs and the README returns **0**. | This is the baseline every later gate is compared with. | Phases 4, 8, 10 |
| **E6** | **Version and CHANGELOG.**<br>- `pyproject.toml` is `2.1.0`.<br>- `tests/test_packaging.py` pins 2.1.0 in A3, B1, B2 and C2.<br>- `__version__` comes from `importlib.metadata`, and the editable install prints `docs 2.1.0`. There is no runtime `dependencies` key.<br>- `CHANGELOG.md`'s section is `## 2.1.0 — UNRELEASED`. A sweep for `unreleased`, `ready locally`, `not on PyPI`, `deferred`, `publish milestone` and `pending` finds only the heading and one sentence: "A separate publish milestone ships it."<br>- The runbook's `awk` release-notes extractor matches the dated heading form. | M30 already made the bump, so there is no version edit and no editable reinstall (M29's lesson does not apply). D7 is a two-line edit. | D1, D7 |
| **E7** | **README, the PyPI long description.**<br>- It lists 13 of 13 verbs in the `docs --help` brace group, `lifecycle` and the free-form `relate` line included (M30 Phase 7).<br>- It contains **0** "Claude Code".<br>- **8 of 8** `blob/main/` links resolve to tracked files.<br>- **Three synopses lag `--help`:** `docs touch <file>` (the CLI takes `files [files ...]`), `docs stamp <file>` (`files [files ...]`), and `docs project set <file> <name>`, described as "Reassign a single doc" (the CLI takes `doc ... new-project`). | The README sits outside every parity gate (M29 lesson 4) and ships inside the artifact. The fix belongs in Phase 3. | D8 |
| **E8** | **Git and GitHub.**<br>- `main` equals `origin/main` at `193fc71`: the M30 merge `bf09748` plus the tracker registration are already public.<br>- The remote tags include `v2.0.0` at `408ef6c`; there is no `v2.1.0`, locally or remotely.<br>- `gh release view v2.1.0` returns "release not found", and the latest release is "docs-cli 2.0.0".<br>- This branch is at the claim commit `be7f809`. | Unlike M29, `main` does not move at publish. The tag and release question is Q1. | D13, Q1 |
| **E9** | **Host.**<br>- `~/.local/bin/docs` → the pipx venv `~/.local/share/pipx/venvs/docs-cli`, printing `docs 2.0.0`.<br>- `~/.claude/skills/` lists a `docs` directory (mtime 2026-08-16, M29's refresh), a symlink `docs-local-source-backup-20260525-134621` → `/home/user/opt/docs-cli/src/docs_cli/skill` (mtime 2026-10-28 11:55), and unrelated entries. Listing only; no skill content was read.<br>- **No recorded destination exists**: `${XDG_STATE_HOME:-~/.local/state}/docs-cli/install-skill.json` is absent, and `XDG_STATE_HOME` is unset.<br>- `~/.cache/docs-cli/update-check.json` exists. | No recorded destination exists to replay, so the refresh needs an operator-named `--dest`. The binary lags the skill the refresh will install, the M29 *Post-closeout* gap. | D10, Q2 |
| **E10** | **`_cmd_install_skill` records its destination on every success** (`update_check.write_recorded_dest`), the no-op included. M29's Phase 5 found that its own scratch smoke runs had left the recorded destination pointing at scratch. M30's Phase 9 avoided this by redirecting XDG. | Any unisolated smoke run writes host state. Every throwaway run redirects `XDG_STATE_HOME` and `XDG_CACHE_HOME`. | D6 |
| **E11** | **Agent Playbook Suite, read-only.**<br>- `~/opt/agent-playbook-suite` is on branch `stopgap/verbless-metadata-edits` at `a997954`, **two commits ahead of `main` (`554ebf2`), unmerged and unreleased**.<br>- `validate.yml` pins `DOCS_CLI_VERSION: "2.0.0"`. Its step *Validate verbless-metadata stopgap matches the pinned docs-cli* probes `docs --help` with `\{([a-z0-9,\-]+)\}` and runs `docs relate add a.md pairs-with b.md --dry-run` in a temporary tree with an empty `.docs.toml` and two `docs new spec` documents — exactly what M30's replica tests encode.<br>- The installed plugin is **0.8.3**, which predates the stopgap. It still sanctions or prescribes hand-edits in `create-milestones/SKILL.md` (invariant 3), `create-milestones/references/milestone-playbook.md` (§2d, §2f) and `project-foundation/references/foundation-playbook.md`.<br>- The suite vendors `skills/docs` with `docs install-skill --dest plugins/agent-playbook-suite/skills/docs --force` and bumps the pin in the same change (`marketplace-publishing-guide.md`). | M30's assumption that the probes are unchanged holds today. The sweep's baseline is in hand. The suite PR needs these facts; this milestone changes none of them. | D10, D12, Phase 8 |
| **E12** | **Open feedback-log entries that ship unchanged:** CRLF normalisation, the duplicated-label edit, the "validate-all-first atomic" wording, the `--body-from` bare-label leak, the dangling free-form edge, grammar widening, out-of-vocabulary repair, `[vocabulary]` validation at load, and the recognized-verb TARGET injection. Each either predates 2.1.0 (it is present in 2.0.0) or was deferred by an M30 decision. The 2026-10-28 candidate convention names *the next milestone's setup* as its owner. | None blocks a release. The candidate convention is offered here, as a taste anchor. | Out of scope; taste anchors |
| **E13** | `gh issue list --state all`: only #1, CLOSED 2026-08-16. No open pull requests. | There is no issue reply in scope, unlike M29. | — |

### Verification

Recorded before the setup edits:
- `.venv/bin/python -m pytest -q` — 1671 passed;
- `ruff check .` — All checks passed;
- `ruff format --check .` — 50 files already formatted;
- `mypy src/ tests/` — no issues found in 51 source files;
- `docs check .` from the docs root — no violations found (exit 0).

The post-edit results are recorded under *Finalization — 2026-10-28* below.

### Decisions / issues

- **The operator decisions of 2026-10-28** live only in the task plan: D2,
  D3, the credential facts in D6, D10 and D13.
- **Risk is Standard**, proposed and not raised as a question. The
  conductor's brief asked for a question only if High were warranted. The
  conductor accepted it on 2026-10-28.
- **Three findings reshape the runbook's default path.** They are E4, E9 and
  E10; the task plan's *Current state and evidence* maps them to decisions.
- **The recognized pairs with the archived M30 document are required.** The
  tracker contract counts an archived document as materialized and asks for
  `--reason`. They were rehearsed on a throwaway tree before the real write.
- **The candidate convention was taken up as a trial.** Its feedback-log
  entry names this setup as owner. The first draft did not hold to it; the
  Step 0 review caught that (gpt-B4 / claude-B1), and the revision fixes it.
  The entry stays open.
- **No OPEN QUESTION remains.** Q1 and Q2 went to the operator and were
  answered. Everything else is settled in the task plan's *Also settled,
  without a question*, which the conductor accepted.

### Setup questions — summary

The full packets are in the task plan's *Setup questions (Q1–Q2)*.

| # | Question | Recommendation | Status |
|---|---|---|---|
| Q1 | Do the `v2.1.0` tag push and the GitHub release happen in Step 2 under D2's automatic authorization? Or after the operator merges into `main` (B), or at a separate go (C)? | **(A)** in Step 2 | **RESOLVED (operator, 2026-10-28) → (A).** See D2 and D13. |
| Q2 | Where does the host skill refresh go, is the pipx binary upgraded in the same phase, and is the backup symlink left alone? | Refresh and upgrade; leave the symlink | **RESOLVED (operator, 2026-10-28) → as recommended.** See D10. |

### Finalization — 2026-10-28

The operator answered both setup questions through the conductor, each as
recommended:
- **Q1 → (A).** Folded into D2 and D13.
- **Q2 → refresh and upgrade.** Folded into D10.

The conductor also accepted the Standard risk level and every item the task
plan lists under *Also settled, without a question*.

What changed:
- **The trio.** The answers went into the task plan's D-ids, and the matrix
  and this log now point to them.
- **Tracker:** re-verified, with nothing to change:
  - row `200 | [pypi-publish-2-1-0](pypi-publish-2-1-0.md) | active |
    lifecycle-and-free-form-relate | M31 — …`, with slug, order, state,
    dependency and Notes unchanged;
  - the recognized pairs with
    `archive/2026-10-28/lifecycle-and-free-form-relate.md` (`precedes` /
    `follows`, `depends-on` / `required-by`) present.
- **`status.md`:** the narrative now records the answers.
- **Every edited document was touched with `docs touch`**, the INDEX was
  regenerated with `docs index .`, and the snapshot
  `tests/fixtures/expected/docs-INDEX.md` was refreshed in lockstep.

Verification after finalization, at the review-ready checkpoint `caa8f1b`:
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/ruff format --check .` — 50 files already formatted.
- `.venv/bin/mypy src/ tests/` — no issues found in 51 source files.
- `.venv/bin/python -m pytest -q` — 1671 passed.
- `docs check .` from the docs root — no violations found (exit 0).
- `docs check . --stale 14` — exit 1. The same five pre-existing `stale`
  warnings on evergreen documents remain, reviewed.
- Three `cmp` checks report identical:
  - `docs/INDEX.md` against `tests/fixtures/expected/docs-INDEX.md`;
  - `src/docs_cli/skill/references/cli.md` against `docs/cli.md`;
  - `src/docs_cli/skill/references/convention.md` against
    `docs/convention.md`.
- `docs index . --dry-run` is byte-identical to `INDEX.md`.
- The credential-hygiene search (D6) of the staged diff finds no token-shaped
  string.

## Step 0 review-pass-001

- Pass id: `Step 0 review-pass-001`.
- Ledger location: `pypi-publish-2-1-0-impl.md#step-0-review-pass-001`
  (docs root `/home/user/opt/docs-cli/docs`; repository path
  `docs/pypi-publish-2-1-0-impl.md#step-0-review-pass-001`).
- Predecessor: none — the first entry in this milestone's review sequence.
- Status: `open`.
  - Both provider attempts are terminal.
  - Every finding is dispositioned **fixed**, in the review-resolution
    checkpoint commit that introduces this record. A commit cannot carry its
    own SHA, so that commit's SHA is returned in the hand-off and written here
    at finalization.
  - Re-review is not required (see *Re-review*).
  - The pass closes at final sync.
- Frozen packet:
  - slug `pypi-publish-2-1-0`, step 0, branch
    `pypi-publish-2-1-0/milestone-setup`;
  - base `be7f80965dee0e17bf41f8018699391f751dde5c` (the claim checkpoint);
  - review HEAD `caa8f1b739a0a0ad01c7a2d587a0ed19f6f9d653`
    (`pypi-publish-2-1-0(setup): plan M31, open its log and test matrix`);
  - project `docs`, project path `""`, artifact stem `pypi-publish-2-1-0`;
  - tracker row `200 | pypi-publish-2-1-0 | active |
    lifecycle-and-free-form-relate`, claim checkpoint `be7f809`, branch root
    `pypi-publish-2-1-0/`;
  - risk Standard, under the Step 0 test-quality clause.

  At the review HEAD the conductor confirmed a clean tree and `docs check .`
  at exit 0. The two reviewers received the identical provider-neutral prompt
  and packet, isolated from each other.
- Tracker: `milestone-plan.md` in the docs root; owning project `docs`; project
  path empty (a dedicated docs root); artifact stem `pypi-publish-2-1-0`;
  active semantic slug `pypi-publish-2-1-0`; row
  `200 | pypi-publish-2-1-0 | active | lifecycle-and-free-form-relate`; claim
  checkpoint `be7f809`; semantic branch root `pypi-publish-2-1-0/`.
- Claude slot: `returned`.
  - Identity: Anthropic Claude family, Claude Opus 5.5 (`claude-opus-5-5`),
    host-reported. It ran as a fresh Claude Code `milestone-reviewer`
    sub-agent at xhigh effort.
  - What it re-ran:
    - ruff, the formatter and mypy, all clean;
    - pytest, 1671 passed;
    - `docs check .` at exit 0, on a `git archive` copy;
    - the INDEX and mirror identity;
    - read-only registry and GitHub probes, which confirmed E1–E13.
  - Risk-gate decision: block until fixed. The fixes are doc-only; continue
    after the checkpoint; no re-review needed.
- GPT slot: `returned`.
  - Identity: OpenAI GPT family; Codex CLI 0.164.0, run as
    `codex exec -m gpt-6-astra -c model_reasoning_effort=xhigh -s read-only`.
    Both identities are recorded: the session log reports
    `model: gpt-6-astra`, while the reviewer self-described as "GPT-5 …
    Codex; no more specific model ID is exposed".
  - What it re-ran: ruff, the formatter, mypy, the mirrors and the INDEX
    identity. It did not re-run pytest, because the packaging fixtures build
    and install artifacts.
  - Risk-gate decision: block until fixed.

### Findings and dispositions

Line references are to `caa8f1b`, and every disposition is **fixed**. "Plan"
is `pypi-publish-2-1-0.md`; "matrix" is the test matrix.

| # | Source ids | Severity | Finding | Fix and evidence |
|---|---|---|---|---|
| 1 | gpt-B1, claude-S2 | blocker | The "no `Requires-Dist`" oracle is wrong (plan :579-581, :816, :972; matrix :58, :98, :180). The served 2.0.0 METADATA carries `Provides-Extra: dev` and five `Requires-Dist: …; extra == 'dev'`. | Plan *Facts* records the served 2.0.0 metadata, re-fetched read-only from PyPI's `.metadata` file. *Non-functional constraints* › *Compatibility* holds the dependency oracle: every `Requires-Dist` carries `extra ==`, plus `Provides-Extra: dev` and `Requires-Python: >=3.11`. Matrix C6 and *Benchmark/security/schema* use it. No "no `Requires-Dist`" text remains (grep: 0). |
| 2 | gpt-B2, claude-S3 | blocker | The probe cannot pass on the editable build: the `--symlink` refusal is wheel-only (`cli.md` :2978; `src/docs_cli/cli.py` :9364). | D5 splits `release_probe.py` into a **contract group** (any executable) and a **distribution group** (wheel installs only). The editable build runs the contract group only (Phase 2). The three wheel installs run both groups identically. The matrix's *Visible tests* and Matrix rows agree. |
| 3 | gpt-B3, claude-S5 | blocker | The tag and the release preceded served-wheel verification (D13 :423-425; Phase 7 :1044-1046 against the probe at :1055-1060; runbook :426-429). | In D13 and Phase 7, served verification comes first: the shas, both probe groups, and the suite's capability probes. Only then the tag and the release. The stop table's probe-failure row says "stop before the tag and release". Matrix C11 and C12 read "before the tag", and C13 follows them. Phase 8 is now the GREEN record. |
| 4 | gpt-B4, claude-B1 | blocker, gating taste | The plan broke its own "state each binding decision once" anchor (:644-646), while `feedback-log.md` :50 claimed it held. D10 was restated about 10 times, plus C15; D13's merge rule about 5 times, plus C13; and the E4/E9/E10 → D mapping twice. | **Option A, dedupe** (a conductor decision). Each operative statement now lives only in its D-id. Other sections reference the id and keep only phase-specific duties. Phase 9 keeps its command lines, and the Q1/Q2 packets stay as the audit trail. Also collapsed: the Overview progress against *Current state*, *Also settled* (now ids only), the Q resolutions (now pointers), and this log's progress, phase notes, decisions, questions table and *Finalization*. `feedback-log.md` :50 now describes the dedupe accurately. Grep counts below. |
| 5 | claude-S1 | should-fix, high priority | A `dist/*` upload glob, and no `dist/` wipe between builds: a leftover rehearsal artifact could reach real PyPI. | D4: `rm -rf dist/` before every build; explicit filenames in every upload; `dist/` must hold exactly the two files. The stop table gains a row for `dist/` contents not holding the two canonical files with (c)'s shas. Phases 4 and 6 name both files; Forbidden shortcuts forbids globs. |
| 6 | gpt-S1, claude-N4 | should-fix | The rehearsal artifact sat outside the byte chain, and `--extra-index-url https://pypi.org/simple/` could execute a claimed `docs-cli-rehearsal`. | D6: single-index installs, `--index-url https://test.pypi.org/simple/ --no-deps`. D4: the served rehearsal wheel must equal the uploaded build by sha, and its `docs_cli/` payload must equal (a)'s. Added to the stop table, to matrix C8, and to Phase 10's correction list. |
| 7 | gpt-S2, claude-N2 | should-fix | The remote-tag check compared the annotated tag object, not the commit (`v2.0.0`: `af3bdb5` against peeled `408ef6c`). | D13 compares `git ls-remote origin 'refs/tags/v2.1.0^{}'` with the tag-target commit, and runs `gh release create v2.1.0 --verify-tag --title "docs-cli 2.1.0"`. Matrix C13 and the Public release surfaces row agree. |
| 8 | gpt-S3 | should-fix | The protected-path rule forbade the required `tests/fixtures/expected/docs-INDEX.md` update. | D1 permits that one generated snapshot, refreshed in lockstep, and keeps the product-test prohibition. *Invariants* refers to D1. |
| 9 | gpt-S4, claude-S6 | should-fix | C3's README synopsis defects had no rejecting check. | D5: readiness checks each README synopsis against its verb's `--help` usage, at least for `touch`, `stamp`, `project set`, `lifecycle` and `relate`. Phase 2 now expects five RED reasons. Mutant 5, a lagging synopsis, is added; matrix C3 agrees. |
| 10 | claude-S4 | should-fix | (a)'s sdist would not exist when Phase 5 compares against it. | D4 and Phase 4 record (a)'s per-member sdist sha256 manifest (members outside `docs/` and `tests/`) in this log. Phase 5 compares against that record; matrix C10 agrees. |
| 11 | claude-S7 | should-fix | D9 did not cover a change to a release-check script after Phase 4. | D9: a changed script is re-run against (a) and a fresh install of the already-served rehearsal before Step 1 closes. D5: every run records the script's git blob sha. The stop table's D9 row diffs `tests/manual` too; new matrix clause C19. |
| 12 | claude-N1 | nit | The clean-tree rule conflicted with the deliberately dirty rehearsal build. | D4's carve-out: the rehearsal build's only diff is the temporary name and version edit in `pyproject.toml`. The stop row says "beyond D4's rehearsal exception". |
| 13 | claude-N3 | nit | `.gitignore` was missing from the release inputs. | D4's release-input list includes `.gitignore`, and the stop table's D9 diff names it. |
| 14 | claude-N5 | nit | Phase 9's host-binary runs write `~/.cache/docs-cli/update-check.json`, which D10 did not list. | D10: after the notice step, every host-binary run sets `DOCS_CLI_NO_UPDATE_CHECK=1`, so the host state written is exactly three items. Phase 9's commands carry the variable. |
| 15 | claude-N6 | nit | The other host's name would ship in the immutable sdist. | Replaced with "the operator's other host" in every committed file (grep: 0). |
| 16 | claude-N7 | nit | The risk rationale lacked the security trigger. | *Risk Level* now considers *Security* (entire-account tokens) and names D6's containment. Standard stands. |
| 17 | claude-N8 | nit | It did not say what a Step 2 review blocker means after publishing. | D2: a finding against the shipped bytes goes to an operator yank-or-patch decision; a finding against documents is fixed normally. |
| 18 | claude-N9 | nit | The matrix's "precondition guard" mutation target had no mechanism. | Dropped. The upload-gate row's mutation cell is "—", and the mutant list has eight mechanisms. |
| 19 | claude-N10 | nit | Merge ownership was inconsistent. | D13: the merge happens outside ship-milestone, at the operator's direction (M30 was merged as `bf09748` on that instruction). The final report must state "merge with a merge commit, not squash or rebase; `v2.1.0` is at `<sha>`". |
| 20 | claude-N11 | nit | Phase 1 left several items unsettled. | *Ambiguities* lists three for Phase 1: whether the runbook's twine upgrade runs, given Phase 5's unchanged-toolchain precondition; how the 2.0.0 control classifies `install-skill` byte identity; and that M29's tree-dependent counts are re-derived, not copied. D9 re-anchors (a) when the re-runs happen. |
| 21 | claude-N12 | nit | The `status.md` :63 sentence was garbled and omitted the sentence removal. | Rewritten: the CHANGELOG needs its date and the removal of one sentence, and the README needs three synopsis fixes. |
| 22 | claude test-adequacy | adequacy | C2's "nothing else in the section changes" was unchecked. | D7: readiness diffs the section against M30's text at `bf09748`. Mutant 3, another line edited, is added; matrix C2 agrees. |

### Taste triage

These are conductor decisions, binding under Standard authority:
- **gpt-B4 / claude-B1** (gating, an anchor violation): **fixed**, through
  item 4's dedupe.
- **The claude subjective finding** (documentation fit and minimality — the
  plan at 1384 lines and about 10.5k words, against M29's 530 and about 4.4k,
  with restatement bulk): **fixed** by the same dedupe, with no new scope.
- **Patch bloat** (+2071 / −3 lines, the trio about 2025 lines; M30's setup
  was +2143): addressed by the dedupe. The before/after size is below.
- **GPT:** no other subjective findings, recorded as such.

### Dedupe evidence (item 4)

Sizes and grep counts (lines matching) were measured at `caa8f1b` and after
the fix. For the log, this section is excluded, since it necessarily names
the patterns.

| Measure | Plan before → after | Log before → after | Matrix before → after |
|---|---|---|---|
| lines / words | 1384 / 10507 → 1252 / 8436 | 331 / 3928 → 270 / 3336 | 278 / 2673 → 276 / 2432 |
| `skills/docs` | 20 → 9 | 6 → 1 | 2 → 0 |
| `pipx upgrade` | 4 → 2 | 6 → 0 | 1 → 0 |
| `history-preserving` | 4 → 1 | 2 → 0 | 0 → 0 |
| `backup symlink` | 8 → 5 | 3 → 1 | 2 → 0 |
| `recorded destination` | 14 → 3 | 5 → 2 | 4 → 2 |
| the other host's name | 2 → 0 | 1 → 0 | 0 → 0 |

The plan's nine remaining `skills/docs` lines, and its other remaining
mentions, are in these places only:
- D10 (operative);
- D12 and follow-up 1, where it is the suite's own `skills/docs` path;
- *Facts* (E9);
- one stop-table row;
- Phase 9's command lines, which are kept by decision;
- the Q2 audit packet.

D13's merge rule appears only in D13. The whole trio went from 17,108 to
14,204 words, even with the review's fixes added.

### Re-review

**Not required** (conductor decision). Every correction can be checked
objectively against the cited lines:
- grep counts, for the dedupe;
- explicit command text, for the upload, the tag and the probe ordering;
- the corrected metadata oracle, against the served 2.0.0 METADATA.

None changes an operator decision or the milestone's scope. Step 1's own dual
review judges the frozen Phase-1 contract before anything irreversible.

### Open items

- Correcting commit: the review-resolution checkpoint that introduces this
  record. Its SHA is written here at finalization.
- final-sync: `pending`.

## Phase 1 — Define Contract

_Not started._

## Milestone completion summary

_Not complete._
