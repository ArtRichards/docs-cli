# M31 — Publish docs-cli 2.1.0 to PyPI — Implementation Log

Lifecycle: active
Role: log
Project: docs
Updated: 2026-10-29

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
- Started: 2026-10-28 (milestone setup); Phase 1 started 2026-10-28.
- Progress: **Step 1 is complete (2026-10-28) on
  `pypi-publish-2-1-0/phases-1-4`.**
  - Phases 1–4 are done, and the TestPyPI rehearsal is recorded GO.
  - Step 1 review-pass-001 is closed with `final-sync` `ready`. Both
    providers and the targeted re-review returned, and every finding is
    fixed in `e6ac159` or `7867a42`, or waived with a reason.
  - The RED-baseline checkpoint passed under Standard: no unresolved
    contract or test-adequacy blocker, and every accepted should-fix is
    resolved.
  - **Step 2 (Phases 5–10, on `pypi-publish-2-1-0/phases-5-10`) is
    authorized under D2**, subject to every *Error cases* precondition at the
    moment of each action.
  - Step 0 is complete: Q1 and Q2 are RESOLVED by the operator, and Step 0
    review-pass-001 is closed with `final-sync` `ready` (`8515f1c`).
  - Setup measured the publish surface read-only (**E1–E13**, below); Phase 1
    re-verified E1–E4 and froze *Decisions (Phase 1 — BINDING)* in the task
    plan.
  - The only upload is Phase 4's TestPyPI rehearsal under
    `docs-cli-rehearsal`; nothing has reached PyPI, and neither
    `~/.claude/skills` nor `~/.pypirc` has been touched.
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
- Adequacy results: recorded in the matrix's *Adequacy results* through
  Phase 4; the served-wheel results are Step 2's.
- Taste triage: Step 0 review-pass-001 is triaged. gpt-B4 / claude-B1, a
  gating anchor violation, and Claude's subjective finding on documentation
  fit and minimality are both fixed by the dedupe. GPT had no other
  subjective findings. See the pass entry below.
- Taste triage, Step 1: review-pass-001's T1–T3 are fixed. T4 (G6/G9 mirror
  product-test goldens) is waived and carried to Step 3's `/simplify`, as is
  the scripts' patch bloat (1033 lines against the 300–500 anchor). See that
  pass's *Taste triage*.

## TDD phase progress

| Phase | Progress | Date | Notes |
|---|---|---|---|
| 1. Define Contract | Complete | 2026-10-28 | *Decisions (Phase 1 — BINDING)* P1.1–P1.6 frozen: 23 readiness lines, 25 probe checks with the 2.0.0 control column, the scratch layout, Step 1 and Step 2 command lines, the settled items and the runbook correction list. The stop table gained the transport, host-state and suite-criterion rows. E1–E4 re-verified with no drift; E7 corrected (four synopses lag). OQ-1–OQ-5 conductor-resolved. 1671 passed. |
| 2. Write Tests (RED) | Complete | 2026-10-28 | Both scripts written (blobs `b1f739e3…`, `55d5e33a…`). Readiness RED for exactly the reasons in the task plan's *Acceptance examples* › *Readiness*; its green control passes. Mutants 1–6, 1b and 5b each killed by exactly the intended check. The probe passes 21/21 on the editable build; the 2.0.0 control fails exactly the 13 release-bound checks. 1671 collected. |
| 3. Create Data/Fixtures | Complete | 2026-10-28 | The CHANGELOG dated `2.1.0 — 2026-10-28` with its sentence removed (D7); the four lagging README synopses reconciled (D8); the diff equals the Phase 2 green control's. Probe trees confirmed scratch-only. Readiness GREEN, 23/23. 1671 passed. This commit is `X`. |
| 4. Run Tests (RED Baseline) | Complete | 2026-10-28 | GREEN baseline at `X` (`a25cb5d`): the gate (1671), readiness 23/23, the stale-wording grep 0. Build (a) `2c5fa0b3…`/`1d327a97…`, hatchling 1.33.0, `twine check` and the dependency oracle pass. (a) probe 25/25; the guard step reads True / True. The TestPyPI rehearsal served = local = JSON, payloads equal, probe 24 + W1 SKIP. (b) = (a). Mutants 8, 8b, 8c behave. **GO.** |
| 5. Update Base Interfaces | Complete | 2026-10-28 – 2026-10-29 | G2 calibrated (OQ-S2-1) with its D9 script re-run (`f7f8f62`); CHANGELOG re-dated 2026-10-29 under D7 (`33c936f`, the tag target); P1.5's Phase 5 block all as expected, 1671 passed; build (c): wheel = (a), manifest = (a)'s, `twine check` passed, `dist/` exactly two files. Nothing uploaded. |
| 6. Implement Offline/Core Path | Complete | 2026-10-29 | The re-checks passed at 00:03:59 CET; one `twine upload` naming both files, exit 0 at 00:04:04 CET (23:04 UTC on 2026-10-28). The per-version JSON listed both files after about a minute, with digests equal to (c)'s. Nothing re-sent. |
| 7. Update Tool/Wrapper Layer | Complete | 2026-10-29 | Chain of custody bit-perfect for wheel and sdist; the served install's payload = (c); the probe 25/25 on the served wheel, lines identical to (a)'s; the guard step True / True. Then `v2.1.0` annotated at `33c936f`, pushed, peeled remote = the tag target; the GitHub release created with `--verify-tag`, *Latest*. |
| 8. Run Tests (GREEN) | Complete | 2026-10-29 | At the tag target `33c936f`: ruff, the formatter and mypy clean; 1671 passed and collected; both replicas pass; `docs check .` 0; snapshot and mirrors identical; INDEX idempotent (stamp normalised); readiness 25/25. One result set across the three wheel installs. The suite's full guard fails with exactly the ten lines frozen before the run. |
| 9. Integrate / Accept / Dogfood | Complete | 2026-10-29 | The 2.0.0 notice observed on the first attempt; `pipx upgrade` to 2.1.0 (served payload; pipx also touched its shared-libs pip marker, recorded); the skill refreshed byte-identical at `~/.claude/skills/docs`, now the recorded destination; the sweep census hit every oracle site, suite and cache untouched; dogfood `docs check` 0; liveness walked. |
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
- Status: `closed`.
  - Both provider attempts are terminal, and both returned.
  - Every finding is dispositioned **fixed** in the correcting checkpoint
    `b127fd1bbfbfaaa1ac3ce0b5726098911d48668a`, with evidence.
  - Re-review was recorded `not required`, with its reason.
  - `final-sync` is `ready`.
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

Line references are to `caa8f1b`, and every disposition is **fixed**. The
**correcting commit** for every row is `b127fd1bbfbfaaa1ac3ce0b5726098911d48668a`
(`pypi-publish-2-1-0(setup): resolve Step 0 review-pass-001 findings`).
"Plan" is `pypi-publish-2-1-0.md`; "matrix" is the test matrix.

| # | Source ids | Severity | Finding | Fix and evidence |
|---|---|---|---|---|
| 1 | gpt-B1, claude-S2 | blocker — **fixed** in `b127fd1` | The "no `Requires-Dist`" oracle is wrong (plan :579-581, :816, :972; matrix :58, :98, :180). The served 2.0.0 METADATA carries `Provides-Extra: dev` and five `Requires-Dist: …; extra == 'dev'`. | Plan *Facts* records the served 2.0.0 metadata, re-fetched read-only from PyPI's `.metadata` file. *Non-functional constraints* › *Compatibility* holds the dependency oracle: every `Requires-Dist` carries `extra ==`, plus `Provides-Extra: dev` and `Requires-Python: >=3.11`. Matrix C6 and *Benchmark/security/schema* use it. No "no `Requires-Dist`" text remains (grep: 0). |
| 2 | gpt-B2, claude-S3 | blocker — **fixed** in `b127fd1` | The probe cannot pass on the editable build: the `--symlink` refusal is wheel-only (`cli.md` :2978; `src/docs_cli/cli.py` :9364). | D5 splits `release_probe.py` into a **contract group** (any executable) and a **distribution group** (wheel installs only). The editable build runs the contract group only (Phase 2). The three wheel installs run both groups identically. The matrix's *Visible tests* and Matrix rows agree. |
| 3 | gpt-B3, claude-S5 | blocker — **fixed** in `b127fd1` | The tag and the release preceded served-wheel verification (D13 :423-425; Phase 7 :1044-1046 against the probe at :1055-1060; runbook :426-429). | In D13 and Phase 7, served verification comes first: the shas, both probe groups, and the suite's capability probes. Only then the tag and the release. The stop table's probe-failure row says "stop before the tag and release". Matrix C11 and C12 read "before the tag", and C13 follows them. Phase 8 is now the GREEN record. |
| 4 | gpt-B4, claude-B1 | blocker, gating taste — **fixed** in `b127fd1` | The plan broke its own "state each binding decision once" anchor (:644-646), while `feedback-log.md` :50 claimed it held. D10 was restated about 10 times, plus C15; D13's merge rule about 5 times, plus C13; and the E4/E9/E10 → D mapping twice. | **Option A, dedupe** (a conductor decision). Each operative statement now lives only in its D-id. Other sections reference the id and keep only phase-specific duties. Phase 9 keeps its command lines, and the Q1/Q2 packets stay as the audit trail. Also collapsed: the Overview progress against *Current state*, *Also settled* (now ids only), the Q resolutions (now pointers), and this log's progress, phase notes, decisions, questions table and *Finalization*. `feedback-log.md` :50 now describes the dedupe accurately. Grep counts below. |
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

Confirmed at finalization: **no re-review was run.** The conductor
spot-checked `b127fd1`, and this writer re-verified each point
independently:
- the tree is clean;
- `git grep robbie` is empty;
- no `dist/*` upload glob exists outside the finding text;
- `gh release create v2.1.0 --verify-tag --title "docs-cli 2.1.0"` is present
  in D13;
- `docs check .` exits 0.

### Closure check

- **The predecessor chain is unbroken.** This is the first entry in the
  sequence, with predecessor none, and there is no earlier entry or frozen
  packet to alter.
- **One frozen packet.** Base `be7f809…`, review HEAD `caa8f1b…`.
- **Both provider slots are terminal**, and both returned from different
  families, with the effective identities recorded above.
- **Every reviewer-labeled blocker has a completed disposition with
  evidence:** gpt-B1, gpt-B2, gpt-B3, gpt-B4 and claude-B1 are all fixed in
  `b127fd1bbfbfaaa1ac3ce0b5726098911d48668a`.
- **Every taste finding is fixed.**
- **Re-review is recorded `not required`**, with an evidence-based reason.
- **The tracker row is unchanged and still `active`**:
  `200 | [pypi-publish-2-1-0](pypi-publish-2-1-0.md) | active |
  lifecycle-and-free-form-relate | M31 — …`.

### Verification report (sync-and-commit, ship-milestone Step 0)

- Risk level: Standard (accepted by the conductor's triage).
- Fast gate commands run:
  - `.venv/bin/ruff check .`;
  - `.venv/bin/ruff format --check .`;
  - `.venv/bin/mypy src/ tests/`;
  - `.venv/bin/python -m pytest -q`;
  - from the docs root: `docs index .`, `docs check .` and
    `docs check . --stale 14`;
  - `cmp` of `docs/INDEX.md` with its snapshot, and of both bundled
    references with `docs/`;
  - the D6 token search of the staged diff.
- Deep gate commands run: none. Step 0 changes documentation only.
- Deferred or not configured:
  - coverage, the hidden suite and mutation tooling are not configured in
    this project;
  - the release checks, the property checks and the hand-applied mutation
    smoke are planned for Phases 2–8, and have nothing to run against at
    Step 0.
- Visible test result: GREEN — 1671 passed, the expected state for a
  documentation-only step.
- Hidden/generalization, coverage, mutation, property/stateful, fuzz, and
  benchmark/security/schema/migration: not applicable at Step 0, since no
  product code changed.
- Mock audit: no mocks added.
- Taste triage: complete. Everything was fixed, and nothing is untriaged.
- Ship-milestone Step 0 review ledger: this pass is closed, and `final-sync`
  is `ready`.
- Semantic tracker row and branch identity:
  - row `200 | pypi-publish-2-1-0 | active | lifecycle-and-free-form-relate`,
    with its Notes unchanged;
  - project `docs`, project path empty, artifact stem `pypi-publish-2-1-0`;
  - the task plan, log and matrix at the three derived paths;
  - branch `pypi-publish-2-1-0/milestone-setup`, under root
    `pypi-publish-2-1-0/`;
  - both recognized pairs with
    `archive/2026-10-28/lifecycle-and-free-form-relate.md` present;
  - `status.md` links the tracker without copying rows or naming next work.
- Contract/test matrix status: current, with C1–C19 and the decision ↔
  clause crosswalk.
- Docs check: exit 0. `--stale 14` exits 1 with the five pre-existing
  stale warnings on long-unchanged reference docs, reviewed.
- Diff scope: the milestone trio, `status.md` and `feedback-log.md`, plus the
  INDEX and its snapshot if they change — documentation only.
- Operator approvals: D2, D3, Q1 → (A) and Q2 → refresh-and-upgrade, all
  2026-10-28.
- High-risk RED-baseline approval: not applicable (Standard).
- Remaining risks: none open at Step 0. The Phase 6 assumption that the
  token is validated by use, and the D4 drift guard, are carried in the
  contract.

- final-sync: `ready`.

## Phase 1 — Define Contract

Date: 2026-10-28. Branch `pypi-publish-2-1-0/phases-1-4`, from the closed
Step 0 sync `8515f1c`. Phase 1 changed documents only.

### Restatement before work

- **Contract invariants.**
  - D1's change boundary: nothing under `src/`, no product test, only the
    INDEX snapshot among the fixtures.
  - D4's build and custody rules; D5's rule that no expected value comes
    from a build's own output; D6's isolation and secrets.
  - In Step 1, the TestPyPI rehearsal under `docs-cli-rehearsal` is the
    only upload; real PyPI, the tag, the release, pipx and host skills
    belong to Step 2 (D2, D3, D10).
  - The tracker row stays `active`.
- **Forbidden shortcuts.** From the quality model: no special-casing of
  visible examples, literals or fixture names; no weakening, skipping or
  deleting a valid check; visible GREEN is not sufficient where deeper
  gates are selected; no silent loss of adequacy. From the task plan's
  *Forbidden shortcuts*: no expected value from a build's output, no
  artifact compared with itself, no skipped rehearsal, no upload glob or
  `--skip-existing`, no unisolated host state, and no re-dating, renaming
  or re-versioning to get past a stop.
- **Visible drivers:** the two release-check scripts (RED in Phase 2, GREEN
  from Phase 3) and the 1671-test product suite as regression evidence.
- **Explicit workflow gates**, none in default discovery: `twine check`;
  the D4 comparisons; the D9 diff; the D6 token search; the D1 scope check;
  `docs check .`, the INDEX dry-run, the snapshot and the mirrors; the
  stale-wording grep; the collected count; the host check; the twine
  newest-version check; the transport check.
- **Risk and gates:** Standard. Lite gates, plus the hidden/generalization
  smoke (the three-wheel replay and the 2.0.0 control), the
  property/stateful smoke, the mock audit and the Step 1 dual review.
  Coverage is not configured.
- **Mock policy:** no mocks; every check runs real executables.
- **Taste anchors:** M29's voice and sha tables; the runbook's append-only
  lessons; M30's trio shape; `tests/manual/m7_success_criteria.py` and the
  replicas' probe code; the standard library and committed fixture trees
  only. Under the state-once trial, each decision's operative wording lives
  only in its D-id, and P1 holds commands and catalogues.

### Re-verification of E1–E4, the transport and the host (read-only)

| Item | 2026-10-28, Phase 1 | Against setup |
|---|---|---|
| E1 | `pypi.org/simple/docs-cli/` 200; latest 2.0.0, releases `1.3.0 … 2.0.0`; `/pypi/docs-cli/2.1.0/json` **404**. Served 2.0.0: wheel `bcd8aa453415dfe66868f22830fce318c7149d6642935d6167d4de9b2cdaab23`, sdist `c62f22d35067cb42a8c241e1d36e161f60ac533b33658ab41f804a2a2c862b66`, uploaded 2026-08-16T09:21Z | unchanged |
| E2 | TestPyPI bare `docs-cli`: `0.1.0` only, author `None`, the same Portuguese summary. `docs-cli-rehearsal` releases `1.3.0 … 2.0.0`; its `2.1.0` and `2.1.0.post1` per-version endpoints **404** | unchanged; `.post1` newly measured |
| New | `https://pypi.org/pypi/docs-cli-rehearsal/json` **404**: the rehearsal name is unclaimed on real PyPI, so D6's single-index install guards a real hazard | new |
| E3 | `~/.pypirc` mode `600`, mtime 2026-10-28 16:57. Sections `distutils` (`index-servers` = `pypi`, `testpypi`), `pypi` and `testpypi`; both index sections `username = __token__`, `password` prefixed `pypi-` and longer than 100 characters; `testpypi` `repository = https://test.pypi.org/legacy/`. No value printed. `gh auth status`: `ArtRichards`, protocol SSH, scopes include `repo`. No `TWINE_*` or `PIP_*` variable and no pip config file on the host | unchanged |
| E4 | `.venv`: twine 7.0.0, build 1.5.0, pip 24.0, Python 3.12.3. Newest on PyPI: twine **7.0.0** (2026-07-27), hatchling **1.33.0** (2026-10-28T02:27Z), build 1.6.1. The twine check (P1.6) passes | unchanged |
| Transport | `git ls-remote origin refs/heads/main` → `193fc718439c39facfa7b3b60066c61d925314f7`, **exit 0**, with `Tunnel device open failed.` / `Could not request tunnel forwarding.` on stderr — noise under the stop table's transport row | new (OQ-3) |
| E8 | `gh api …/branches/main` → `193fc71…`; `matching-refs/tags/v2` → only `refs/tags/v2.0.0` (tag object `af3bdb5…`); `gh release view v2.1.0` → "release not found"; latest release "docs-cli 2.0.0" | unchanged |
| Host | Recorded destination `~/.local/state/docs-cli/install-skill.json` **absent**. Update cache `~/.cache/docs-cli/update-check.json` sha256 **`39739c2975454ebf10a673cf5de786966254edb3b90636613066b045ed28253d`**, mtime 2026-10-28 08:29 — the baseline for every later host check | unchanged |
| Gate | ruff clean; 50 files formatted; mypy no issues in 51 files; **1671 passed**, 1671 collected; `docs check .` exit 0; the index dry-run, snapshot and both mirrors identical | unchanged |

One host-binary call ran without isolation during this table:
`~/.local/bin/docs --version`, after the cache sha was taken. Re-measured
at once, the cache sha and mtime were unchanged and the recorded
destination was still absent. Every later host-binary call ran under P1.3's
environment and the probe's own.

**Control pre-check.** Before freezing P1.2's control column, two
classifications were probed cheaply against the host 2.0.0 binary in a
scratch tree with `HOME` and XDG redirected: on a `%d-%m-%Y` tree, `relate
add a.md precedes b.md` exits 1 with `malformed date '20-05-2026'` (N8
FAIL); `stamp` on a complete block reading `Lifecycle: activ` exits 0 and
rewrites it to `draft` (N9 FAIL). The host check was unchanged afterwards.
Phase 2's control run is the authoritative record.

### E7 correction

Setup's E7 found three lagging synopses; there are four. README line 56
reads `docs project rename <old> <new>`, while `docs project rename --help`
ends `[--dry-run] new-name`, `cli.md` titles the section `docs project
rename <new-name>`, and the parser declares `metavar="new-name"`. A reader
who copies the PyPI page's synopsis gets an argparse usage error. E7 stays
as setup measured it; the correction lives here and in *Acceptance
examples* › *Readiness*.

**Trial data point (state-once convention).** Setup restated E7's count in
nine places outside E7: in the task plan, D8, *Facts*, the acceptance
example, *Test Strategy* and the Phase 2 objective; the matrix's *Visible
tests*; this log's progress rows 2 and 3; and `status.md`. Phase 1 changed
each one: the acceptance example now states the count once, the other
trio sites point at it, and `status.md`'s narrative reads "four". Phase 10
consumes this for the trial's outcome.

### Planning questions — conductor-resolved, Step 1 planning

| # | Question | Resolution | Where it lands |
|---|---|---|---|
| OQ-1 | Is readiness RED for six reasons, with a fourth synopsis fix? | **(A)**: every README synopsis line is checked against `--help`; RED has six reasons; Phase 3 fixes four synopses under D8's drift clause; the counts are corrected by reference | P1.1; *Acceptance examples*; D8; footprint 4–8 lines |
| OQ-2 | What counts as a rehearsal failure when TestPyPI fails transiently? | **(B)**: classify by cause — one retry of the same command for a connection error, timeout or 5xx with nothing accepted; one by-name re-send of a missing file; polling (at most 10 × 30 s) for index lag; any 4xx, sha or payload mismatch, or probe FAIL stops | *Error cases* (the rehearsal and partial-upload rows) |
| OQ-3 | Should the transport be checked before the upload? | **(A)**: `git ls-remote origin refs/heads/main` and `gh auth status` must both exit 0 at Phase 5, else stop with nothing uploaded; stderr noise on exit 0 is not a failure; today's result is recorded above | *Error cases*; P1.5 |
| OQ-4 | How does Step 2 discharge the suite-probe obligation? | **(A)**: three pieces — the replicas in the full suite at the tag-target commit; S1 and S2 against the served executable; the guard step's `run:` script extracted byte for byte from `validate.yml` at `a997954` and run from a fresh empty directory, passing on exit 0 with `lifecycle verb: True, free-form relate: True`. Phase 4 rehearses the third piece against (a). The suite repository is read only | P1.5; *Error cases* (the suite-probe row) |
| OQ-5 | Where do M29's tree-dependent expected values come from? | **(A)**: committed fixture trees copied to scratch, quoting the product tests that pin them; the docs-tree copy carries only tree-independent assertions | P1.2 (G1–G10); *Ambiguities* |

### Phase 1 calibrations of the planning catalogue

These refine the planning agent's draft while freezing it; none changes a
decision or the milestone's scope.
- **W1–W4.** The draft named the distribution checks D1–D4, which collides
  with the binding-decision ids.
- **G3** asserts exactly one `missing-inverse` record with its frozen
  message, as `tests/test_check.py` pins it (filtered by rule), rather than
  exactly one record of any rule.
- **G6** asserts all five stderr lines `tests/test_cli_mv.py` freezes; the
  draft said four.
- **G7** uses `movelink-closeout` with `--date 2026-08-15`, where the strand
  test pins N = 5.
- **G8** uses `archive-trio` with `--date 2026-03-04`, the fixture and date
  of the test that pins "every member carries the date"; the draft named
  `archive-pair`.
- **N7** takes a fresh copy of `vocab-extension`, so it does not depend on
  N6's edit.
- **W3 and W4** assert the fragments `cli.md` states (`no-op`, `wheel
  install`), not longer source literals.
- **The stale-wording grep** covers 19 surfaces: M30 recorded 17, but named
  only three of its five `--help` outputs, so P1.4 reads all seven that M30's
  surface-parity reconciliation read. This is a strict superset.
- **P1.5** compares served payloads with (c)'s extraction, because Step 2
  cannot read Step 1's scratch and (c) equals (a) by sha; and it runs the
  full suite at Phase 5, so OQ-4's first piece holds before the upload.

### Edits

- Task plan: *Decisions (Phase 1 — BINDING)* P1.1–P1.6 added; in-place
  corrections to the Overview progress, D8, *Contract*'s intro, *Facts* E7,
  *Ambiguities*, the stop table (four rows), the readiness acceptance
  example, the footprint, *Test Strategy*, the Phase 2, 6 and 7 objectives,
  and the gate block's arguments.
- Matrix: clauses and rows point at P1 ids; C3 covers every synopsis line;
  the planned-names caveat and the restated count are gone.
- This log: metadata, progress rows 1–3, this section.
- `status.md`: "four synopsis fixes", and the Step 1 narrative.

### Verification

Recorded under *Re-verification* above for the gate before the edits. After
the edits: `docs touch` on each edited document, `docs index .`, the
snapshot refreshed, `docs check .` exit 0, the index dry-run identical, and
a grep of the trio and `status.md` for "five reasons", "three synopses" and
"three synopsis" finding only this section and the Step 0 audit trail.
`git diff --name-only 8515f1c..HEAD` names only `docs/` files (the INDEX
and its snapshot did not change), and the token search of the staged diff
is empty.

## Phase 2 — Write Tests (RED)

Date: 2026-10-28. Both release checks written to P1.1 and P1.2, and every
Phase 2 run in P1.4 executed. The repository was never mutated: the green
control and the mutants ran on scratch clones.

### The two scripts

| Script | Blob sha (`git hash-object`; the header prints the same) | Lines (SLOC) |
|---|---|---|
| `tests/manual/release_readiness.py` | `b1f739e3dd352f63b9286d77feae175da56c9fb5` | 345 (262) |
| `tests/manual/release_probe.py` | `55d5e33a5573ea5d58cc7809b4f47fea7cb7d024` | 651 (509) |

- **Shape** follows `tests/manual/m7_success_criteria.py`: a module
  docstring saying what runs, why it lives outside discovery and what the
  exit codes mean; `main()` returning 0 or 1; `sys.exit(main(...))`.
- **Stdlib only**: both print `--help` under `python3 -I` with the system
  interpreter; neither imports `docs_cli`; neither holds a `/home/` or
  `/tmp/` path.
- **One decision logged:** each script carries its own `git_blob_sha` and
  `isolated_env` (about 15 lines together). A shared module would need a
  `sys.path` edit or a package under `tests/manual/`, and each script must
  run standalone, `python3 -I`, from a checkout or an unpacked sdist.
- **Failure messages mask the probe's run directory** as `<run>`, so result
  lines copied into this log, which ships in the sdist, carry no host path.
- **Footprint:** 996 lines (771 SLOC) against the anchor's "roughly
  300–500". The bulk is the probe's 25 checks with their frozen strings,
  and ruff's one-argument-per-line layout of the name table. Recorded for
  the reviewers and for Step 3's `/simplify`; nothing outside the P1
  catalogue was built.

### Readiness RED on the base tree

`READY --repo . --release-date 2026-10-28` at `ef9ae84`: **exit 1, 17
passed, 6 failed** — exactly *Acceptance examples* › *Readiness*:

```
FAIL  The newest CHANGELOG section is the release, dated 2026-10-28 — first heading '## 2.1.0 — UNRELEASED', expected '## 2.1.0 — 2026-10-28'
FAIL  The release's CHANGELOG section makes no publish-state claim — still says 'A separate publish milestone ships it.'
FAIL  README.md synopsis for `docs touch` matches `docs touch --help` — README ['S'] vs `docs touch` usage ['V']
FAIL  README.md synopsis for `docs stamp` matches `docs stamp --help` — README ['S'] vs `docs stamp` usage ['V']
FAIL  README.md synopsis for `docs project rename` matches `docs project rename --help` — README ['S', 'S'] vs `docs project rename` usage ['S']
FAIL  README.md synopsis for `docs project set` matches `docs project set --help` — README ['S', 'S'] vs `docs project set` usage ['V', 'S']
```

R1, R4, R5, R7, R8, both R9 lines and the other ten R6 lines passed.

### Readiness GREEN control and mutation smoke

A `git clone --no-hardlinks` of `ef9ae84` in scratch took exactly Phase 3's
edits, applied by one scratch edit script that Phase 3 reuses: **exit 0,
23 passed**. Each mutant then ran on its own `cp -a` copy of that clone.

| Mutant | Applied | Result | Killed by |
|---|---|---|---|
| 1 | Heading back to `## 2.1.0 — UNRELEASED` | 22 passed, 1 failed | R2 only |
| 2 | The dated heading kept, the sentence restored | 22 passed, 1 failed | R3 only |
| 3 | `validate-all-first` → `validate-everything-first` in the section | 22 passed, 1 failed | R4 only, quoting both lines |
| 4 | The `docs mv` synopsis line deleted | 21 passed, 1 failed | R5 only ("no synopsis for: mv"); the R6 line for `mv` is gone, not failed |
| 5 | The `touch` synopsis back to `<file>` | 22 passed, 1 failed | R6 for `touch` only |
| 6 | One byte appended to the bundled `references/cli.md` | 22 passed, 1 failed | R9 for `cli.md` only |
| 1b | `pyproject.toml` name `docs-cli-rehearsal` | 22 passed, 1 failed | R1 only |
| 5b | `[--json]` → `[--force]` in the `docs mv` synopsis | 22 passed, 1 failed | R6 for `mv` only ("flags not in usage: ['--force']") |

All eight are killed, each by exactly its intended check.

### Probe sanity on the editable build

`PROBE --docs .venv/bin/docs --group contract`: **exit 0, 21 passed**.

### Mutant 7 — the 2.0.0 control

`PROBE --docs ~/.local/bin/docs --group all --expect-version 2.1.0` (pipx
2.0.0): **exit 1, 12 passed, 13 failed**, matching P1.2's control column
line for line.

| Id | Result | Observed |
|---|---|---|
| N1 | FAIL | `relate add m.md pairs-with m-impl.md`: exit 2, `unknown verb 'pairs-with'` |
| N2 | FAIL | exit 2, argparse `invalid choice: 'lifecycle'` |
| N3 | FAIL | exit 2, `unknown verb 'references'` |
| N4 | FAIL | exit 2 from argparse, without the frozen message — the case the message assertion exists for |
| N5 | FAIL | exit 2, `unknown verb 'Pairs-With'` without the grammar |
| N6 | FAIL | `docs lifecycle`: exit 2, `invalid choice` |
| N7 | FAIL | `docs index`: exit 2, `Role: 'adr' not in vocabulary` |
| N8 | FAIL | exit 1, `Updated: malformed date '20-05-2026' (expected %Y-%m-%d)` |
| N9 | FAIL | exit 0, `docs: stamped f.md` — it re-stamped the block |
| S1 | FAIL | the verb list lacks `lifecycle` |
| S2 | FAIL | exit 2, `unknown verb 'pairs-with'` |
| G1–G10 | PASS | all ten 2.0 contracts hold on 2.0.0 |
| W1 | FAIL | printed `docs 2.0.0` |
| W2 | FAIL | six of the seven files differ from this tree's bundled skill — the comparison rejects a wrong bundle |
| W3, W4 | PASS | the no-op re-run and the wheel `--symlink` refusal |

### Cleanliness and isolation

After every run, `git status --porcelain --untracked-files=all` listed only
the two new scripts, so no probe tree touched the repository. The host
check was unchanged each time (recorded destination absent; update cache
`39739c29…`), and no file in the pipx venv was newer than the session's
`env.sh`.

### Verification

- `ruff check .` clean; `ruff format --check .` — 52 files formatted;
  `mypy src/ tests/` — no issues in 53 source files.
- `pytest --collect-only -q` — **1671 tests collected**: neither script is
  discovered.
- The D1 scope check prints nothing; the token search of the staged diff is
  empty.

### Deferred to Phase 4

Mutants 8, 8b and 8c need Phase 4's artifacts (P1.4).

## Phase 3 — Create Data/Fixtures

Date: 2026-10-28 (21:46 CET). The release inputs took exactly D7's and
D8's edits, applied by the scratch edit script the Phase 2 green control
used; `git diff -- CHANGELOG.md README.md` is byte-identical to that
control's diff.

| File | Line | Before | After |
|---|---|---|---|
| `CHANGELOG.md` | 8 | `## 2.1.0 — UNRELEASED` | `## 2.1.0 — 2026-10-28` |
| `CHANGELOG.md` | 13 | `release. A separate publish milestone ships it._` | `release._` |
| `README.md` | 53 | `docs touch <file> [--check]` | `docs touch <file>... [--check]` |
| `README.md` | 54 | `docs stamp <file>` | `docs stamp <file>...` |
| `README.md` | 56 | `docs project rename <old> <new>` | `docs project rename <new-name>` |
| `README.md` | 57 | `docs project set <file> <name>`, "Reassign a single doc to another project." | `docs project set <file>... <name>`, "Reassign one or more docs to another project." |

The README keeps its 42-column description alignment. Only `project set`'s
description changed, because "a single doc" is false for a verb that takes
several (`cli.md` › `docs project set`); every other description was
already accurate. The footprint is 2 CHANGELOG lines and 4 README lines.

**The release date `D` is 2026-10-28**, the local date when the heading was
written. Phase 4's readiness runs use `--release-date 2026-10-28`. Step 2
re-dates under D7 if its upload falls on a later day.

**Probe trees.** Every tree is built inline or copied under `--scratch`
(P1.2). A contract-group run on the editable build after the edits (21
passed) left `git status` showing only the two edited release inputs; the
host check was unchanged.

### Verification

- `READY --repo . --release-date 2026-10-28` (readiness blob `b1f739e3…`):
  **exit 0, 23 passed, 0 failed**.
- `.venv/bin/python -m pytest -q` — **1671 passed**; `docs check .` exit 0.
- The D1 scope check prints nothing; the token search of the staged diff is
  empty.
- This commit is **`X`**, the commit Phase 4 builds (a), the rehearsal and
  (b) from. Its full sha is in Phase 4's *Release anchors (current)*.

## Phase 4 — Run Tests (RED Baseline)

Date: 2026-10-28, 21:48–21:55 CET. A pre-publish **GREEN** baseline (D3):
the gate, build (a), the schema, the local wheel, the TestPyPI rehearsal and
build (b), all at `X` = `a25cb5d07b24f00a81834ed6f7f8aa46d5e49a45` with a
clean tree, except the rehearsal's own `pyproject.toml` edit (D4). Evidence
collected in `$S/notes/` and was written here only after build (b). Every
command is P1.4's.

### 4.0–4.1 Preconditions and the gate

- `git status --porcelain` empty; `HEAD` = `X`; the host check unchanged.
- Toolchain: twine **7.0.0**, build **1.5.0**, pip **24.0**, Python
  **3.12.3** (`.venv`; the throwaway venvs use the system `python3` 3.12.3).
  The twine check passes: 7.0.0 is PyPI's newest and at least 7.0.0. PyPI's
  newest hatchling was 1.33.0.
- ruff clean; 52 files formatted; mypy no issues in 53 files; **1671
  passed**; **1671 collected**; `docs check .` exit 0; the index dry-run,
  the snapshot and both mirrors identical.
- Readiness `--release-date 2026-10-28`: **exit 0, 23 passed**.
- The stale-wording grep over P1.4's 19 surfaces (12 files, 7 `--help`
  outputs): **0**.
- The D1 scope check prints nothing.

**Surface parity.** Each bullet of the CHANGELOG's 2.1.0 section, against
the `--help` text that states it:

| CHANGELOG bullet | `--help` statement |
|---|---|
| *Added* — `docs lifecycle <file>... <state>` | `docs --help` lists `lifecycle`; `docs lifecycle --help` states the states (any `add_lifecycles` extension included), the `*files, <state>` split, the one `Updated:` bump and one reindex, idempotence, `archived` never a target, the archive-subtree source refusal, validate-all-first, and `--dry-run`, `--json`, `--quiet`, `--root` |
| *Changed* — free-form `docs relate add\|remove` | `docs relate --help` and `docs relate add --help`: a verb matching `[a-z][a-z0-9-]*` writes SOURCE's bullet alone; TARGET is never read or written and may be any existing file; never written to an archived SOURCE; an archived TARGET needs no `--reason` |
| *Changed* — non-default `date_format` trees judge dates as `docs check` does | No flag: a parse fix. Its home is `cli.md` › *Invocation*; no `--help` text contradicts it |
| *Changed* — `docs stamp` refuses a block failing the configured vocabulary or date format | `docs stamp --help`: "is refused (exit 1, nothing written) rather than re-stamped" |
| *Fixed* — extensions and date formats in every verb; extension roles in `INDEX.md` | No flag: a parse fix. `docs lifecycle --help` names `add_lifecycles`; the rest lives in `cli.md` |

### 4.2–4.3 Build (a), `twine check` and the schema

- `rm -rf dist/ && .venv/bin/python -m build`: `dist/` held exactly
  `docs_cli-2.1.0-py3-none-any.whl` and `docs_cli-2.1.0.tar.gz`.
- `WHEEL`: `Generator: hatchling 1.33.0`.
- `twine check` on both files by name: **PASSED**, PASSED.
- METADATA: `Metadata-Version: 2.5`, `Requires-Python: >=3.11`,
  `Provides-Extra: dev`, and five `Requires-Dist` lines (build, mypy,
  pytest, ruff, twine), each `; extra == 'dev'`. **The dependency oracle
  holds.**
- `CHANGELOG` entries: 0 in the wheel, 0 in the sdist. The wheel's
  `docs_cli/skill/` entries equal the seven files of `src/docs_cli/skill`,
  and it has no entry outside `docs_cli/` and `docs_cli-2.1.0.dist-info/`.

### 4.4 The local wheel

- Installed into a fresh venv with `--no-deps --no-index`. Before anything
  ran, `diff -r -x __pycache__` against (a)'s extraction was empty.
- `PROBE --docs $S/venv-a/bin/docs --group all --expect-version 2.1.0`:
  **exit 0, 25 passed** (the lines are in the anchors below).
- **The guard-step rehearsal (OQ-4, piece 3).** P1.5's extraction of
  `validate.yml@a997954` lines 1210–1293 (84 lines, sha256 in the anchors),
  run with `bash -e` from a fresh empty directory with `PATH` on the venv
  (`docs` and `python3` both resolved there): **exit 0**, printing
  `verbless-metadata stopgap consistent with docs-cli pin (lifecycle verb:
  True, free-form relate: True)`.
- **A negative control** of that pass rule: the same script with the host's
  2.0.0 `docs` first on `PATH` exits **1**, reporting that the pinned
  docs-cli can perform neither edit. The suite checkout was not touched
  (`git status` empty).

### 4.5 The rehearsal under `docs-cli-rehearsal`

| Step | Result |
|---|---|
| 1. The temporary edit | `pyproject.toml` line 6 → `name = "docs-cli-rehearsal"`; `git diff --stat` named only `pyproject.toml` |
| 2. Build | `dist/` held exactly the two rehearsal files; wheel `fd2f787c…`, sdist `0241b9eb…`; `Generator: hatchling 1.33.0`, equal to (a)'s |
| 3. `twine check` | both PASSED |
| 4. Upload | the `2.1.0` per-version JSON returned 404 and `dist/` held exactly the two files; then `twine upload --repository testpypi --non-interactive` with both filenames: **exit 0** at 21:52:25–29 CET. TestPyPI shows `https://test.pypi.org/project/docs-cli-rehearsal/2.1.0/` |
| 5. Served bytes | The per-version JSON listed 0 files at the first two polls and both at the third (about a minute of index lag: polling, not a failure, under the stop table). Each JSON `url` was fetched into a fresh empty directory; both served shas equal the local build and the JSON digests. The served wheel's `docs_cli/` equals (a)'s byte for byte, and its only other entries are `docs_cli_rehearsal-2.1.0.dist-info/` |
| 6. Install | `pip install --no-cache-dir --no-deps --index-url https://test.pypi.org/simple/ docs-cli-rehearsal==2.1.0` succeeded at the first attempt; the installed `docs_cli/` equals (a)'s extraction before anything ran. `docs --version` prints `docs 0.0.0+local` (M13) |
| 7. Probe | `--group all --no-version-check`: **exit 0, 24 passed, 1 skipped**. Its result lines equal (a)'s except W1, now `SKIP … rehearsal-name install reports 0.0.0+local` |
| 8. Revert | `git restore pyproject.toml`; `git diff --exit-code pyproject.toml` exit 0; `git status --porcelain` empty; `HEAD` = `X` |
| 9. Build (b) | wheel and sdist shas **equal (a)'s**, `Generator: hatchling 1.33.0`; D4's remedy was not needed |

No retry was needed, and no OQ-2 transient-fault rule fired.

### 4.6 The comparators

| Mutant | Planted difference | The comparator reported |
|---|---|---|
| 8 | (a)'s wheel against the rehearsal wheel | `cmp` exit 1; the shas differ |
| 8b | One byte appended to `cli.py` in a scratch copy of (a)'s payload | `diff -rq`: `docs_cli/cli.py` differs, and nothing else |
| 8c | (a)'s sdist manifest against the rehearsal sdist's | exactly `./PKG-INFO` and `./pyproject.toml` differ, as constructed |

### 4.7 Host isolation

Unchanged after every block: the recorded destination absent, the update
cache sha `39739c29…`, no file in the pipx venv newer than this session's
`env.sh`. `~/.claude/skills/docs` keeps its 2026-08-16 mtime, and the backup
symlink is untouched. Nothing was installed with pipx, and nothing touched
real PyPI.

### 4.8 GO record

**GO, 2026-10-28 21:55 CET.** Each item of P1.4's GO list holds:
- [x] the gate, with 1671 passed and collected;
- [x] readiness, 23 passed;
- [x] (a) built clean, with its shas, `Generator`, manifest and schema
      items recorded, and `twine check` passed;
- [x] the (a) probe, 25 passed;
- [x] the rehearsal uploaded by explicit filename;
- [x] the served shas equal the local build and the JSON digests;
- [x] the payloads identical, both downloaded and installed;
- [x] the rehearsal's result set equal to (a)'s apart from W1;
- [x] the revert proven;
- [x] (b) equal to (a);
- [x] mutants 8, 8b and 8c behave as stated;
- [x] host state unchanged;
- [x] the anchors table below complete.

### Release anchors (current)

Step 2 reads only this table and the two blocks under it. A D9 re-run
replaces this section's values and says so.

| Anchor | Value |
|---|---|
| `X`, the build commit | `a25cb5d07b24f00a81834ed6f7f8aa46d5e49a45` |
| CHANGELOG release date `D` | `2026-10-29` — *re-dated 2026-10-29 under D7 by `33c936f` (Phase 5), the day having rolled; `X` carries `2026-10-28`* |
| Tag-target commit (Step 2) | `33c936f447dfb31078dc0c07c9e4fd2297ed747d` — the commit build (c) came from (Phase 5) |
| Wheel (c) | `docs_cli-2.1.0-py3-none-any.whl` `2c5fa0b3e3c3db05e4f452bc900b31fa7a7acb5b3f330cd8d52a9bd80c19a185` — equal to (a) |
| Sdist (c) | `docs_cli-2.1.0.tar.gz` `c120fc1db71db08306ec1e002dedb1adcd95dc08bd5a8c1f775cda772696404d` — the sdist's anchor (D4); its manifest equals (a)'s |
| Wheel (a) = (b) | `docs_cli-2.1.0-py3-none-any.whl` `2c5fa0b3e3c3db05e4f452bc900b31fa7a7acb5b3f330cd8d52a9bd80c19a185` |
| Sdist (a) = (b) | `docs_cli-2.1.0.tar.gz` `1d327a97912ab70ac53829e2af2d568c119d8ce555e9032264e744ba1d6d07d4` |
| Build backend (D4) | `Generator: hatchling 1.33.0` |
| Build environment reproducing (a) | `hatchling==1.33.0`, `packaging==26.3`, `pathspec==1.1.1`, `pluggy==1.7.0`, `tomlkit==0.15.2`, `trove-classifiers==2026.9.21.13` — resolved by a verbose scratch rebuild from `X` (2026-10-28, `SOURCE_DATE_EPOCH` unset) that reproduced both (a) shas; (a)'s own log did not print them. D4's remedy pins exactly these |
| `Metadata-Version` | `2.5` |
| Rehearsal (TestPyPI) | `docs-cli-rehearsal` `2.1.0`, uploaded 2026-10-28T20:52:26Z (wheel) and 20:52:27Z (sdist) |
| Rehearsal wheel, served = local = JSON | `docs_cli_rehearsal-2.1.0-py3-none-any.whl` `fd2f787c85d95d3ace8944f0f00846f0644ebca4f69e3feb422dbff910b7b318` |
| Rehearsal sdist, served = local = JSON | `docs_cli_rehearsal-2.1.0.tar.gz` `0241b9eb0ad906f3136b886f4ef08b83ef37ee723d3ec51db4036c4b1ecc3d1a` |
| The next rehearsal version under D9 | `2.1.0.post1` (404 at Phase 1) |
| `release_readiness.py` blob | `cb542802bba447d4fb7ee72eaf1b454b2773653f` — 25 lines (R8 split into R8a–R8c). Earlier: Phase 4 ran `b1f739e3dd352f63b9286d77feae175da56c9fb5`; the audit's D9 re-run `a90ab8c6eb0dd67f3421dbb16dcbce21d4bf4d48` |
| `release_probe.py` blob | `763b7dd7c22c7305f8215b1415b1ff67eb2d3fb1` — *replaced 2026-10-28 by Step 2's G2 calibration (Phase 5 › D9 re-run for the G2 calibration)*. Earlier: Phase 4 ran `55d5e33a5573ea5d58cc7809b4f47fea7cb7d024`; the audit's D9 re-run `88043c87b4eff5c8dcc164b06e4160c6d1ea444d`; Step 1's review `2d6a0c31b1cac8ee25ef858671002e3b7f9d7830` |
| D9 re-runs | Three, all 2026-10-28: after the audit's docstring change (*Step 1 audit*), after the review's strengthened checks (*Step 1 review-pass-001* › *D9 re-run*), and after Step 2's G2 calibration (*Phase 5* › *D9 re-run for the G2 calibration*). Every probe result line equals the Phase 4 record below |
| Toolchain (`.venv`) | twine 7.0.0, build 1.5.0, pip 24.0, Python 3.12.3 |
| Suite guard step | `validate.yml@a997954` lines 1210–1293, dedented by ten spaces: 84 lines, sha256 `2e2fc83d9b6fb4eb0108cbadc5222a786218e87dfe41f6f613a30f67236253ca` |
| Host baseline | recorded destination absent; update cache sha256 `39739c2975454ebf10a673cf5de786966254edb3b90636613066b045ed28253d` |
| `~/.pypirc` shape (P1.5's command, as fixed by the re-review) | `mode 0o600`; `sections-are-distutils,pypi,testpypi True`; `pypi username==__token__ True password-starts-pypi- True password-len>100 True`; the same line for `testpypi` |
| `origin/main` (R8c's reference) | `193fc718439c39facfa7b3b60066c61d925314f7`, equal to GitHub's `main` via `gh api`; no fetch was needed |

**(a)'s sdist manifest** — every member outside `docs/` and `tests/`, from
the top directory `docs_cli-2.1.0/`, 15 lines:

```
70956ac96bc5029ca8d7243e4aabb10708442050d59d4255f84b64e714110f37  ./.gitignore
47382a3bb2a61d731fdaecb56630e15b51ddb77233340ee005d9208015fa82bd  ./LICENSE
3f2d9f3c2dc7645b806cbfe09b97af5be6fbcd06824a19de29c386081decde91  ./PKG-INFO
0d44c82d63fc09ca96e6b35b7bc3f44aa4136c1c3c213b3e1d039e5eb542ae84  ./README.md
06437edb1be3b5bf2133bb2d9b9bde951107def7024fc07781f73f958a53280a  ./pyproject.toml
72262e5c30d632bee9ea8dcb8ea75335fc3672f49b2da825d83e242f41f534cc  ./src/docs_cli/__init__.py
a1097ee33a232efa4d26186ca57178d75768692c7a71561c92efc2743054bce1  ./src/docs_cli/cli.py
b88aadf3787f1655a2581d6ea0f5b389bbda6e72efe15e04d3a43d29747e42c5  ./src/docs_cli/skill/SKILL.md
f2ac0b7fb243bd034c29241a0a9e8e3d740acb7f6787c2f5608f80585c5b42cf  ./src/docs_cli/skill/references/adoption-playbook.md
44e7c81aa46430f98108ae7a9784e20809629297a12fc0f7ae3d256cff4af644  ./src/docs_cli/skill/references/cli.md
9e07a6d34a7c6835d783be54bcdb1da86576d763fdb7ea77d92014ebc2fc1b00  ./src/docs_cli/skill/references/convention.md
f9bc06a9f1ef164b202f8a85dc7f69e8907d1f0519058848a1d7dc289fe733a0  ./src/docs_cli/skill/references/docs-toml-template.toml
9170c1d08d7f1076baa6e81ac4402df7d06317182f0867f7a282d94751af2d6d  ./src/docs_cli/skill/references/quality-artifacts.md
a3d1c257ed198c1df10492a65906547d819d703a58ee72a48d2eca0bafb8e14f  ./src/docs_cli/skill/references/use-cases.md
5b659f914bd13d81ec5f8a87b4e4fc3c9a37b06de4c29ed82f10e745a7704e74  ./src/docs_cli/update_check.py
```

**(a)'s probe result lines** (`--group all --expect-version 2.1.0`; exit 0,
25 passed). The rehearsal's are identical except line 22, which reads `SKIP
docs --version names the expected release — rehearsal-name install reports
0.0.0+local`. The served wheel's must equal these.

```
PASS  A milestone trio scaffolded with docs new is linked with free-form edges and promoted to active in one call, and docs check passes
PASS  Re-running the same promotion changes no file
PASS  A free-form edge to an archived document needs no --reason and rewrites only its source
PASS  docs lifecycle refuses archived as a target, points at docs archive, and changes nothing
PASS  An out-of-grammar relate verb is refused with the grammar named, and nothing changes
PASS  An extension lifecycle state set by docs lifecycle is read back by docs list and docs index
PASS  An extension-role document appears in INDEX.md
PASS  On a tree with a non-default date_format, relate links documents dated in that format
PASS  docs stamp refuses a file whose complete block fails the configured vocabulary, writing nothing
PASS  The docs --help verb list names lifecycle, as the Agent Playbook Suite guard parses it
PASS  A free-form dry-run relate on a fresh tree exits 0 and writes nothing, as the Agent Playbook Suite guard probes it
PASS  docs check passes on a throwaway copy of this repository's docs tree
PASS  docs index --dry-run on a copy of this docs tree reproduces its INDEX.md and writes nothing
PASS  A one-sided recognized edge is reported as missing-inverse
PASS  Bare --cascade is refused and nothing changes
PASS  A dead prose link is reported as broken-body-link
PASS  mv --dry-run names every planned reference rewrite and writes nothing
PASS  Archiving reports the still-active inbound references into the archived set
PASS  docs archive records the Archived: date on every moved member
PASS  docs mv refuses a move between two dated archive directories and changes nothing
PASS  A hand-relocated archived document is reported as archive-date-drift
PASS  docs --version names the expected release
PASS  install-skill materialises a skill byte-identical to the repository's bundled skill
PASS  Re-running install-skill on an identical destination is a no-op
PASS  install-skill --symlink is refused from a wheel install, leaving the destination absent
```

**D9 freshness.** This section was written after build (b), in a commit
that changed only `docs/`. The Step 1 audit later changed both scripts'
docstrings; the release inputs (`src pyproject.toml README.md LICENSE
.gitignore`) are unchanged since `X`, and each later script change's D9
re-run is listed in the *D9 re-runs* row above, with the blob shas.

## Step 1 audit — consistency, completeness and accuracy

Date: 2026-10-28. The same-instance audit of Phases 1–4, run item by item
against ship-milestone's consistency check, after the Phase 4 commit
`f03cb31`.

### Findings and fixes

| # | Finding | Fix |
|---|---|---|
| A1 | `release_readiness.py`'s docstring said README "names no particular agent", while R7 checks only for "Claude Code"; it also omitted `--help` as a reference | Reworded to what R7 checks, and to "the references are the arguments, the reviewed CHANGELOG text and the `--help` of `--docs`" |
| A2 | Both scripts' docstrings said the release runbook runs them; the runbook names neither until Phase 10 (P1.6), and both scripts ship in the sdist | Reworded to the scripts' role, with no claim about the runbook |
| A3 | A1 and A2 changed both scripts after their Phase 4 runs, which D9 makes a re-run trigger | The D9 re-run below; the anchors table carries the new blobs |
| A4 | P1.5's Phase 5 diff required `tests/manual` unchanged since `X`, leaving no route for a recorded D9 re-run, which the plan intended to admit | Split: the release inputs must be unchanged, and each script's `git hash-object` must equal its blob in *Release anchors (current)* |
| A5 | P1.5's tag command used `$TAG_TARGET`, which nothing assigned | Phase 5 now records `TAG_TARGET=$(git rev-parse HEAD)` |
| A6 | P1.2 did not state the probe's `--repo` default | Stated, as in P1.1 |
| A7 | P1's preamble said the check ids live "only here and in the matrix" (this log uses them too) | "only in the milestone's documents, never in a display name"; P1.1's references sentence matches the docstring |
| A8 | This log's Phase 1 verification said the scope check named "the snapshot", and Phase 4's D9 paragraph said its commit changed "the INDEX snapshot"; neither changed | Corrected |
| A9 | P1.3's layout omitted `$S/tools/` and `$S/guard-step.sh` | Added |

None changes scope, a decision or a check's behaviour, so nothing needs
the operator.

### D9 re-run for the script change

Both scripts' docstrings changed; no code did. Re-run at blobs
`a90ab8c6…` (readiness) and `88043c87…` (probe):

| Run | Result | Against the Phase 4 record |
|---|---|---|
| Readiness, `--docs .venv/bin/docs` | exit 0, 23 passed | equal |
| Readiness, `--docs $S/venv-a/bin/docs` (wheel (a)) | exit 0, 23 passed | — |
| Readiness, `--docs` a fresh install of the served rehearsal | exit 0, 23 passed | — |
| Probe on wheel (a), `--group all --expect-version 2.1.0` | exit 0, 25 passed | result lines identical |
| Probe on a fresh TestPyPI install of `docs-cli-rehearsal==2.1.0` (single index, `--no-deps`; its `docs_cli/` equal to (a)'s before running) | exit 0, 24 passed, 1 skipped | result lines identical |
| Probe on the editable build, contract group | exit 0, 21 passed | equal |
| Probe on the 2.0.0 control | exit 1, 12 passed, 13 failed | statuses identical |

The host check was unchanged, and `git status` showed only the two edited
scripts.

### Checked and clean

- **Completeness.** The four Step 1 deliverables are ticked with evidence;
  Phases 1–4 have log sections, dated progress rows and ticked checklist
  items. No TODO, placeholder or commented-out code.
- **Code against spec.** Every R, N, S, G and W check implements its P1.1
  or P1.2 row, with the frozen fragments and fixtures; the outputs, exit
  codes and isolation match P1's common rules.
- **Documents.** The tracker row is unchanged and `active`
  (`milestone-plan.md` has no diff since `8515f1c`); `status.md` narrates
  without restating rows; the trio agree on progress, counts, dates and
  the OQ resolutions; edited documents were touched; the INDEX equals its
  dry-run and the snapshot; `docs check .` exits 0.
- **Codebase.** No new dependency; stdlib only; no `docs_cli` import; no
  host path. Every produced output has a consumer in P1 or the log.
- **Tests and adequacy.** Every check was shown to reject a wrong answer:
  the six RED lines, mutants 1–6, 1b, 5b and 8–8c, and the 2.0.0 control.
  Exact-string assertions quote messages that `cli.md` or the product tests
  freeze, and the 2.0.0 control passes the G checks, so those strings held
  across 2.0 → 2.1. Display names carry no provenance. No mocks. Nothing
  was weakened.
- **Footprint, for the reviewers.** The scripts are 996 lines (771 SLOC)
  against the anchor's "roughly 300–500"; the README and CHANGELOG diffs
  are within it. Phase 2 records why; Step 3's `/simplify` owns any
  reduction.

### Verification

After the fixes: ruff clean; 52 files formatted; mypy no issues in 53
files; **1671 passed**, 1671 collected; `docs check .` exit 0; the INDEX
dry-run, the snapshot and both mirrors identical; readiness 23/23; the D1
scope check and the token search clean; `git diff --quiet a25cb5d..HEAD --
src pyproject.toml README.md LICENSE .gitignore` holds.

## Step 1 review-pass-001

- Pass id: `Step 1 review-pass-001`.
- Ledger location: `pypi-publish-2-1-0-impl.md#step-1-review-pass-001`
  (docs root `docs/`; repository path
  `docs/pypi-publish-2-1-0-impl.md#step-1-review-pass-001`).
- Predecessor: `Step 0 review-pass-001` — closed, `final-sync` `ready`,
  synced in `8515f1c`. That entry and its frozen packet are unchanged.
- Status: **`closed`** (2026-10-28).
  - Both provider slots are terminal, and both returned.
  - Every finding is dispositioned **fixed**, in two correcting checkpoints:
    `e6ac15930019bafff9c5cf42899558f43f461aa2` (`pypi-publish-2-1-0(phase 1-4): resolve Step 1 review-pass-001
    findings`) and `7867a428621786c949b133ce01b844f7c455a1ca` (`pypi-publish-2-1-0(phase 1-4): resolve the Step 1
    re-review findings`). The one exception is claude-T4, waived with a
    reason.
  - The required targeted re-review is complete, and its three remaining
    blockers were closed by the conductor's objective verification.
  - `final-sync` is `ready`.
- Frozen packet (recorded by the conductor):
  - slug `pypi-publish-2-1-0`, step 1, branch
    `pypi-publish-2-1-0/phases-1-4`;
  - base `8515f1c09b89811073d68c85c241869b3fdcbdaf` (the closed Step 0
    sync);
  - review HEAD **`b1f31b40bc16526ae4275c7c6753503e8bc96251`**, the
    review-ready commit; Step 1 commits `ef9ae84` (Phase 1), `d6f62f4`
    (Phase 2), `a25cb5d` (Phase 3, `X`), `f03cb31` (Phase 4), `eec64ff` (the
    audit fixes) and `b1f31b4`;
  - changed paths: `CHANGELOG.md`, `README.md`,
    `docs/pypi-publish-2-1-0.md`, `docs/pypi-publish-2-1-0-impl.md`,
    `docs/pypi-publish-2-1-0-test-matrix.md`, `docs/status.md`,
    `tests/manual/release_readiness.py`, `tests/manual/release_probe.py`;
  - project `docs`, project path `""`, artifact stem `pypi-publish-2-1-0`;
    tracker row 200 `active`, claim `be7f809`, branch root
    `pypi-publish-2-1-0/`; risk Standard, under the Step 1 test-quality
    clause;
  - both reviewers received the identical provider-neutral prompt and
    packet, isolated from each other.

  At `b1f31b4` the conductor re-ran: ruff, the formatter and mypy clean (53
  files); `pytest -q` 1671 passed; `docs check .` exit 0; the INDEX snapshot
  identical; the TestPyPI rehearsal's digests equal the anchors; PyPI's
  `docs-cli/2.1.0` per-version JSON returns 404.
- Tracker: `milestone-plan.md` in the docs root; owning project `docs`;
  project path empty; artifact stem `pypi-publish-2-1-0`; active semantic
  slug `pypi-publish-2-1-0`; row
  `200 | pypi-publish-2-1-0 | active | lifecycle-and-free-form-relate`;
  claim checkpoint `be7f809`; semantic branch root `pypi-publish-2-1-0/`.
- Results at the review-ready state `b1f31b4`, as submitted: ruff clean; 52
  files formatted; mypy no issues in 53 files; 1671 passed and collected;
  `docs check .` exit 0 with the INDEX, snapshot and mirrors identical;
  readiness 23/23; the probe 25/25 on wheel (a), 24 + W1 SKIP on the
  rehearsal, 21/21 on the editable build, and the 2.0.0 control failing
  exactly the 13 release-bound checks; the rehearsal GO.
- Claude slot: `returned`.
  - Identity: Anthropic Claude family, Claude Opus 5.5 (`claude-opus-5-5`),
    host-reported; a fresh `milestone-reviewer` sub-agent at xhigh effort.
  - What it re-ran independently: `pytest` 1671 passed; readiness 23/23 at
    `b1f31b4` and the six frozen failures at `8515f1c`; a fresh-clone build
    with hatchling 1.33.0 that reproduced wheel (a)'s sha `2c5fa0b3…` and
    the 15-line sdist manifest; the rehearsal wheel through `pip download`,
    sha `fd2f787c…`, its `docs_cli/` byte-equal; the probe 25/25 on its own
    wheel; a scratch 2.0.0 control at 12 PASS / 13 FAIL; an extra 1.8.0
    control failing G3–G10; the guard-step sha `2e2fc83d…` equal to the
    anchor; host state unchanged.
  - Disclosed: it briefly wrote a scratch copy of this log into the shared
    review directory, then moved it into its own subdirectory; it read no
    other reviewer's files.
  - Risk-gate decision: continue automatically, strongly recommending
    claude-S1–S4 before the pass closes.
- GPT slot: `returned`.
  - Identity: OpenAI GPT family; Codex CLI 0.164.0, run as `codex exec -m
    gpt-6-astra -c model_reasoning_effort=xhigh -s read-only`. Both
    identities are recorded: the session log reports `model: gpt-6-astra`,
    while the reviewer self-described as "GPT-5 … Codex; no finer
    identifier".
  - What it re-ran: ruff, the formatter and mypy; the 1671-test collection;
    `docs check .` and the INDEX parity; readiness's functions, 23 PASS; the
    blob anchors; the 14 source-backed sdist entries against `X`. Its
    filesystem was read-only, so it could not repeat the suite, the builds
    or the installs, and TestPyPI did not resolve from its sandbox.
  - Risk-gate decision: block until fixed.

### Findings and dispositions

Line references are to `b1f31b4`. "Plan" is `pypi-publish-2-1-0.md`. Every
disposition below is **fixed** in the correcting checkpoint
**`e6ac15930019bafff9c5cf42899558f43f461aa2`**, except where a waiver is stated under *Taste triage*. Rows 1 and
2 were completed in **`7867a428621786c949b133ce01b844f7c455a1ca`**, after the re-review found that the first fix
was insufficient (see *Re-review*).

| # | Source ids | Severity | Finding | Fix and evidence |
|---|---|---|---|---|
| 1 | gpt-B1, claude-N2 | blocker (gating hygiene) | The token search (plan :1341) was `grep -nE`, which prints the matched line — a caught token would be copied into the session log (D6). Its pattern also missed `github_pat_` tokens | P1.4's gate is now `grep -qE` (no output); on a match it prints `STOP …` and `git diff --cached --name-only -G"$TOKEN_RE"` — file names only — and exits 1. The pattern adds `github_pat_[A-Za-z0-9_]{20,}`. **Proof:** in a scratch repository, synthetic `pypi-`, `gho_` and `github_pat_` strings each made the gate exit 1 naming only `secret.txt`; the synthetic value appeared in its output **0** times, and the gate's text extracted verbatim from the plan behaved the same. A clean stage exits 0. Every earlier run of the old search printed nothing, so nothing leaked |
| 2 | gpt-B2, claude-DP-1 | blocker | The stop table (plan :581, :589–591) gave conflicting rules for a mixed accept/refuse upload and for transient faults, and could say "nothing uploaded" when one file was published | **Conductor decision (DP-1, option A, Standard authority; narrows D2 in the safe direction, does not reopen it).** The authentication and partial-upload rows are replaced by one *PyPI upload (Phase 6)* row, stated once: poll the per-version JSON (at most 10 × 30 s) and record exactly what is published; then (1) any hard refusal — any 4xx, including 400 metadata, 401/403 and 409 or a reused filename — stops; (2) one file confirmed published and the other failed transiently → one by-name re-send of the missing file; (3) any other error, including a transient fault with nothing confirmed, stops for the operator with no automatic retry; (4) publication still uncertain stops. "Nothing uploaded" is recorded only when the poll lists no file. The rehearsal row keeps OQ-2 for TestPyPI only, with its own order explicit (a 4xx stops whichever file it hits). P1.5 Phase 6 and *Assumptions* reference the row |
| 3 | claude-S1 | should-fix | The stop table's D9 row (plan :583) and matrix :100 still described the pre-audit `tests/manual` diff | Both now read `git diff --quiet "$X"..HEAD -- src pyproject.toml README.md LICENSE .gitignore` plus each script's `git hash-object` against *Release anchors (current)* |
| 4 | claude-S2 | should-fix | Stop-table coverage gaps against P1.5 | P1.5 Phase 6 re-checks, immediately before `twine upload`: the date (item 16), the 404, `ls -A dist/` (exactly the two files), and both shas against (c) and the anchor. A new stop row covers any P1.5 Phase 5–7 result that differs from its stated expectation (readiness failing on anything but D7's date, `pytest` not 1671, the 404 probe answering 200, the JSON never listing both files, a guard-step sha mismatch, empty release notes). A patch-level toolchain difference is record-only, because (c) = (a) by sha is the byte guard; anything larger stops. The 404 row also covers the Phase 6 re-check |
| 5 | claude-S3 | should-fix | The credential-shape command was never frozen | P1.5 Phase 5 freezes a `python3 -I -c` configparser command that prints only the mode, the section names and three booleans per index. Run verbatim from the plan: `mode 0o600`, `sections ['distutils', 'pypi', 'testpypi']`, and `True True True` for both `pypi` and `testpypi` — recorded in the anchors as the comparison record |
| 6 | claude-S4 | should-fix | Phase 7's served-wheel probe read the mutable working tree (`--repo .`: G1/G2's docs copy, W2's skill reference) | P1.5 Phase 7 runs the probe from `git worktree add --detach "$S/tag-tree" "$TAG_TARGET"` with `--repo "$S/tag-tree"`, then removes the worktree. Mechanism checked: a worktree at `b1f31b4` ran the probe 25/25 on wheel (a), and its removal left `git worktree list` with one entry |
| 7 | gpt-S1 | should-fix | Phase 9 would inherit `env.sh`'s scratch `XDG_STATE_HOME`, recording the host refresh under scratch; the universal "destination absent" check had no Phase 9 exception | Phase 9's skill step runs `env -u XDG_STATE_HOME -u XDG_CACHE_HOME …` and verifies the host's `~/.local/state/docs-cli/install-skill.json` names the expanded `~/.claude/skills/docs`, with no record under `$S/xdg/state`. The notice step unsets `DOCS_CLI_NO_UPDATE_CHECK`, `CI` and `DO_NOT_TRACK`, which `env.sh` would otherwise leave suppressing it. P1.3's host check and the host-state stop row are phase-specific: absent until Phase 9's skill step, then naming `~/.claude/skills/docs` |
| 8 | gpt-S2 | should-fix | `version_is()` (probe :450) ignored the exit code | W1 now requires exit 0 and the expected stdout. **Negative control:** a wrapper printing `docs 2.1.0` and exiting 3 fails exactly W1 ("exit 3, printed 'docs 2.1.0'"); the pre-review probe passed it 25/25 |
| 9 | gpt-S3 | should-fix | N6 (probe :228) required only `docs index` exit 0 | N6 now requires `INDEX.md` to contain `- [draft-note.md](draft-note.md)`, the entry fragment `tests/test_cli_touch.py` pins on this fixture — not a whole-file golden. **Negative control:** an `index` that drops that entry fails exactly N6; the pre-review probe passed it |
| 10 | gpt-S4 | should-fix | N2 (probe :181) compared contents only, so an identical-byte rewrite passed | N2 re-runs the promotion with `--json` and requires `applied: false`, `index_refreshed: false` and `change: unchanged` for every document (`cli.md` › `docs lifecycle`), plus unchanged bytes **and mtimes** for every file. **Negative control:** a `lifecycle` that rewrites every `.md` with identical bytes fails exactly N2 ("rewrote ['INDEX.md', 'm-impl.md', 'm-test-matrix.md', 'm.md']"); the pre-review probe passed it |
| 11 | gpt-S5, claude-N6 | should-fix | R8 (readiness :286) dropped the link's owner/repository and checked only local `HEAD` | R8 is now three lines. R8a: every GitHub file link's `<owner>/<repo>` equals `pyproject.toml`'s `[project.urls] Repository` (`ArtRichards/docs-cli`), and its ref is `main`. R8b: each path is tracked at HEAD. R8c: each path exists at `origin/main`. The local ref is used without a fetch: `origin/main` = `193fc71…` = GitHub's `main` per `gh api`, so no fetch was needed; P1.5 Phase 5 compares the two and fetches only if they differ, recording which. **Negative controls** on scratch clones: a foreign owner (9a) and a `dev` ref (9b) fail exactly R8a; a path tracked at HEAD but absent from `origin/main` (9c) fails exactly R8c. Readiness has 25 lines |
| 12 | claude-N1 | nit | (a)'s resolved build environment was not recorded; `SOURCE_DATE_EPOCH` was not guarded | A verbose scratch rebuild from `X` reproduced both (a) shas and resolved hatchling 1.33.0, packaging 26.3, pathspec 1.1.1, pluggy 1.7.0, tomlkit 0.15.2 and trove-classifiers 2026.9.21.13. That set is in the anchors, and D4's remedy pins all of it (P1.6). `env.sh` now unsets `SOURCE_DATE_EPOCH` |
| 13 | claude-N3 | nit | `lib/python3.12/site-packages` was hard-coded (plan :1428, :1459, :1518) | All three use `lib/python3.*/site-packages`, globbed by the shell; nothing imports the package to find it |
| 14 | claude-N4 | nit | `status.md` :75–80 had the wrong tense, and the synopsis count was misattributed | Rewritten in the past tense: setup found three, Phase 1 a fourth, and Phase 3 fixed all four |
| 15 | claude-N5 | nit | The PyPI page links `blob/main/CHANGELOG.md`, which reads `UNRELEASED` until the stack is merged | D13 says the merge should follow promptly, for that reason, and the final-report wording says so |
| 16 | claude-N7 | nit | The CHANGELOG is dated at Phase 5, but the upload could fall after midnight | Phase 6 re-checks `date +%F` against the CHANGELOG heading immediately before the upload; a mismatch returns to Phase 5 for D7's re-date and a new build (c) |
| 17 | claude-N8 | nit | The D9 re-run control used the host pipx binary | P1.6: D9 re-runs use a scratch 2.0.0 — `pip download --only-binary :all: --no-deps`, the sha checked against M29's served `bcd8aa45…` before anything runs, then a `--no-index` install. This pass's D9 re-run used it |
| 18 | claude-N9 | nit | Plan :355 was not wrapped | Rewrapped |
| 19 | claude (hidden-test note) | nit | The probe's `isolated_env` passed `PYTHONPATH` and `PYTHONHOME` through | Both are dropped in both scripts' `isolated_env`, so the executable under test loads only its own installation |

### D9 re-run for the strengthened checks

Items 8–11 and 19 changed both scripts after Phase 4 — readiness now at
blob `cb542802bba447d4fb7ee72eaf1b454b2773653f` (25 lines), the probe at
`2d6a0c31b1cac8ee25ef858671002e3b7f9d7830`. No release input changed, so `X`
stands and there is no re-rehearsal.

| Run | Result |
|---|---|
| Rebuild from `X` in a scratch clone (verbose, `SOURCE_DATE_EPOCH` unset) | wheel `2c5fa0b3…` and sdist `1d327a97…` — equal to (a); `Generator: hatchling 1.33.0`; its extraction equals (a)'s |
| Probe on a fresh venv of that wheel, `--group all --expect-version 2.1.0` | exit 0, 25 passed; result lines **identical** to the Phase 4 record |
| Probe on a fresh `--index-url https://test.pypi.org/simple/ --no-deps` install of `docs-cli-rehearsal==2.1.0` (its `docs_cli/` equal to (a)'s before running) | exit 0, 24 passed, 1 skipped; lines **identical** to the Phase 4 record |
| Probe on the scratch 2.0.0 control (wheel sha `bcd8aa45…` = E1, checked before running) | exit 1, 12 passed, 13 failed; statuses identical to Phase 2's |
| Probe on the editable build, contract group | exit 0, 21 passed |
| Readiness on the tree, `--docs` the editable build, wheel (a) and the fresh rehearsal | exit 0, 25 passed, each |
| Readiness on a clone of the base `8515f1c` | exit 1, 19 passed, 6 failed — exactly the reasons *Acceptance examples* › *Readiness* names |
| Readiness mutants 1–6, 1b, 5b, 9a, 9b, 9c on clones of `b1f31b4` | each killed by exactly its intended check; every other line PASS |
| The host check, after every block | unchanged; no pipx-venv file newer than this session's `env.sh` |

### Taste triage

These are conductor decisions, binding under Standard authority:
- **gpt-B1** (gating hygiene): **fixed** (item 1).
- **claude-T1** (state-once: the readiness reason count was restated in
  P1.1, the matrix and `status.md`, despite the acceptance example's "one
  statement" claim): **fixed**. P1.1 and the matrix point at the acceptance
  example, `status.md` no longer gives the number, and the claim now reads
  "the trio and `status.md` point here; the log records measured results".
  **Trial data point for Phase 10:** a second drift of the same count, after
  Phase 1's sweep of nine sites. Restated counts drift even under the
  convention, and the review caught them.
- **claude-T2** (Phase 4–7 objectives re-listed P1.4/P1.5's sequences):
  **fixed**. Each objective now points at its P1 block and keeps only its
  exit criteria.
- **claude-T3** (P1.6 restated the dependency policy): **fixed**. It refers
  to *Taste anchors* › *Dependency policy*.
- **claude-T4** (G6 and G9 mirror product-test golden strings, which is
  brittle for the next release): **waived for Step 1**. The strings are
  frozen by product tests and held across 2.0 → 2.1, as the 2.0.0 control's
  G passes show. Carried to Step 3's `/simplify` as an unresolved taste
  finding.
- **Patch bloat** (the scripts at about 997 lines against the 300–500
  anchor; now 1033): logged and carried to Step 3's `/simplify`; no
  action now.
- **GPT:** no other subjective findings.

### Re-review

**Required — targeted** (conductor decision). Trigger: item 2 changes the
frozen stop logic at the irreversible step, and items 8–11 change the
release checks. The conductor freezes a new packet at the
review-resolution checkpoint and sends it to the GPT reviewer only, scoped
to the resolutions of gpt-B1, gpt-B2 and gpt-S1–S5.

**Result — returned.** The reviewer was Codex CLI 0.164.0, run as `codex
exec -m gpt-6-astra -c model_reasoning_effort=xhigh -s read-only`; its
session log reports `model: gpt-6-astra`, and it self-described as "GPT,
Codex, based on GPT-5". Its packet was `b1f31b4..e6ac159`, and its risk-gate
decision was block until fixed.
- **gpt-S1, gpt-S2, gpt-S3, gpt-S4 and gpt-S5: resolved**, each confirmed by
  the reviewer's own in-memory counterexamples.
- **gpt-B1 and gpt-B2: not resolved**, and one new blocker, **gpt-RR-B1**.
  All three are **fixed** in the correcting checkpoint **`7867a428621786c949b133ce01b844f7c455a1ca`**, below.

The conductor decided on **no second re-review round**, since the protocol
forbids an automatic loop. Instead, the conductor re-runs the synthetic
controls below, verbatim, against the committed text before closing the
pass.

| # | Source ids | Severity | Finding | Fix and evidence |
|---|---|---|---|---|
| 1 (re-opened) | gpt-B1 | blocker | `e6ac159`'s gate piped `git diff` into `grep -qE`. `grep` exits at its first match, `git` then dies of SIGPIPE, and under `set -euo pipefail` the `if` reads the failed pipeline as "no match" — a fail-open. **Reproduced at `e6ac159`:** on a 6.2 MB staged diff with a synthetic token on line 1, the frozen gate printed `token search: clean` and exited 0 in 5 of 5 trials | P1.4's gate pipes nothing into `grep -q`. `names=$(git diff --cached --text --name-only -G"$TOKEN_RE")` uses git's own pickaxe, with `--text` so binary files count. If the search fails, the gate stops with "the token search itself failed"; if `$names` is non-empty, it prints only the file names and exits 1. **Controls (all PASS):** the 6 MB diff with the token on line 1, run 5 times under `set -euo pipefail`, gave exit 1 each time, naming `big.txt`; `pypi-`, `gho_` and `github_pat_` tokens in a small file each gave exit 1; a token inside a staged binary file gave exit 1; a clean stage gave exit 0 (`token search: clean`); with no repository (`GIT_DIR` missing) the search failed and the gate stopped, exit 1. The synthetic value appeared **0** times in stdout+stderr in every run |
| 2 (re-opened) | gpt-B2 | blocker | `e6ac159`'s general "P1.5 expectation" stop row listed "the per-version JSON not listing both files", which collided with the upload row's re-send for one confirmed file plus a transient failure | The general row no longer lists that item. It states once that it never governs the upload's own outcome: from `twine upload` until the JSON lists both files, only the PyPI-upload row decides. That row now says "the first case that applies decides", gives case (2) an explicit success and failure, and gives case (4) the exit-0-but-incomplete shape. The walk below shows each shape has exactly one outcome |
| 20 | gpt-RR-B1 | blocker (new) | `e6ac159`'s frozen shape command had no exception handling. A malformed `~/.pypirc` line raised `configparser.ParsingError`, whose traceback quotes the whole line. **Reproduced at `e6ac159`** on a synthetic file with a password line missing its `=`: exit 1, a traceback, and the synthetic value in the output once | The command now wraps all reading, parsing and field access in `try … except BaseException`, prints only `pypirc shape check failed: unreadable, malformed or incomplete (details suppressed)`, and exits 1. It reads the file as UTF-8, requires `password` and `username` to be present, and prints no section name: section membership is reported as one boolean. **Controls** (synthetic files only, `HOME` pointed at scratch, all PASS): a malformed password line, a missing `[testpypi]`, a missing password key, binary garbage, a duplicate password key and a missing file each gave exit 1 with only the fixed message; a token used as a section name gave exit 0 with `sections-are-distutils,pypi,testpypi False`; a well-formed synthetic file printed only the four shape lines. The synthetic value appeared **0** times in every output. One run on the real file printed the four shape lines now recorded in *Release anchors (current)* |

**Every upload shape has exactly one outcome.** The general row excludes
the upload, and the upload row's cases are tried in order:

| Shape after polling | First applicable rule | Outcome |
|---|---|---|
| twine exit 0; the JSON lists both files | none: the upload row's condition is false | proceed to the digest check; a digest that differs from (c)'s falls to the served-sha row |
| both files refused with a 4xx | case (1) | stop; nothing published |
| one accepted, the other refused with a 4xx | case (1) | stop; one file published, recorded as such |
| one accepted, the other failed transiently | case (2) | one re-send of the missing file, by name |
| — the re-send exits 0 and the JSON lists both | case (2), success | proceed |
| — the re-send fails, or the JSON still lacks the file | case (2), otherwise | stop; one file published |
| nothing accepted, transient failure | case (3) — (1) needs a 4xx, (2) a confirmed file | stop for the operator; no retry |
| any non-4xx error, publication uncertain after polling | case (3) | stop for the operator |
| twine exit 0, yet the JSON lists fewer than both after polling | case (4) | stop |

**Re-running the controls.** The controls are one scratch script,
`$S/tools/rereview-controls.sh`; the return report gives its full path.
`bash "$S/tools/rereview-controls.sh" <repo> HEAD` extracts both frozen
commands verbatim from the committed plan, prints their sha256, and runs
the 19 controls above in a fresh temporary directory. Synthetic values are
generated inside the script and never printed; it reads no real credential
file. It prints `ALL CONTROLS PASS` and exits 0 only if every control
passes. The defect reproductions at `e6ac159` used the same synthetic
inputs against that revision's text.

No release input or release-check script changed for these fixes: the
blobs stay `cb542802…` and `2d6a0c31…`, and `X` stands. D9 is not triggered.

### Verification at the review-resolution checkpoint

- ruff clean; 52 files formatted; mypy no issues in 53 files.
- `pytest -q` **1671 passed**; 1671 collected.
- `docs check .` exit 0; the INDEX dry-run, the snapshot and both mirrors
  identical.
- Readiness **25/25** (`--release-date 2026-10-28`).
- The non-disclosing token search: clean on the staged diff.
- The D1 scope check prints nothing; `git diff --quiet a25cb5d -- src
  pyproject.toml README.md LICENSE .gitignore` holds; both scripts run
  under `python3 -I`, import no `docs_cli`, and hold no host path.

### Verification at the second review-resolution checkpoint

- ruff clean; 52 files formatted; mypy no issues in 53 files.
- `pytest -q` **1671 passed**; 1671 collected.
- `docs check .` exit 0; the INDEX dry-run, the snapshot and both mirrors
  identical.
- Readiness **25/25**.
- The new token search: clean on the staged diff.
- `$S/tools/rereview-controls.sh`: `ALL CONTROLS PASS` (19 of 19) against
  the working-tree text staged for this checkpoint, and again against the
  committed `HEAD` `7867a42`, run by the writer and then by the conductor.
- The script blobs are unchanged (`cb542802…`, `2d6a0c31…`); the release
  inputs are unchanged since `X`.

### Conductor closing evidence (2026-10-28)

The protocol forbids an automatic review loop, so the conductor closed the
re-review's three remaining blockers by independent objective verification
of `7867a428621786c949b133ce01b844f7c455a1ca`, not by a second re-review round:
- It ran `bash "$S/tools/rereview-controls.sh" <repo> HEAD` at `7867a42`:
  **ALL CONTROLS PASS, 19/19**. The synthetic value appeared 0 times in the
  output of every control. Both commands were extracted verbatim from the
  committed plan, with gate sha256 `e8ab40bbbd164cca…` and shape sha256
  `938bf270134cb597…`. **gpt-B1 → fixed** in `7867a428621786c949b133ce01b844f7c455a1ca`; **gpt-RR-B1 → fixed**
  in `7867a428621786c949b133ce01b844f7c455a1ca`.
- It read the plan's stop table at `7867a42` (lines 593–594). The general
  row states that it never governs the upload's own outcome. The
  PyPI-upload row applies "the first case that applies decides" over cases
  (1)–(4), with an explicit success and failure for the re-send and "a
  published file is never re-sent". **gpt-B2 → fixed** in `7867a428621786c949b133ce01b844f7c455a1ca`.
- It verified `git diff --quiet a25cb5d 7867a42 -- src pyproject.toml
  README.md LICENSE .gitignore` (the release inputs are unchanged since
  `X`) and a clean tree.

### Closure check

- **The predecessor chain is unbroken.** The predecessor is
  `Step 0 review-pass-001` (closed, `ready` in `8515f1c`), byte-identical to
  its `8515f1c` text with its frozen packet. No other sequence entry
  exists, and no `contract-rework` entry was needed.
- **One frozen packet for the original pass.** Base `8515f1c…`, review HEAD
  `b1f31b4…`. The targeted re-review's packet (`b1f31b4..e6ac159`) is
  nested in this pass.
- **Both provider slots are terminal.** Both returned, from different
  families, with their effective identities recorded above.
- **Every reviewer-labeled blocker is dispositioned with evidence.**
  gpt-B1, gpt-B2 and gpt-RR-B1 are fixed in `7867a428621786c949b133ce01b844f7c455a1ca`, with the parts of
  gpt-B1 and gpt-B2 that `e6ac159` already carried fixed in `e6ac15930019bafff9c5cf42899558f43f461aa2`.
  claude-DP-1 was an operator-shaped choice that the conductor decided
  under Standard authority (option A) and applied in `e6ac15930019bafff9c5cf42899558f43f461aa2`, then completed
  in `7867a428621786c949b133ce01b844f7c455a1ca`.
- **Every accepted should-fix and nit is fixed** in `e6ac15930019bafff9c5cf42899558f43f461aa2`.
- **Every taste finding is fixed or waived with a reason.** T1–T3 are fixed
  in `e6ac15930019bafff9c5cf42899558f43f461aa2`. T4 is waived to Step 3's `/simplify`, with its reason; the
  patch bloat is logged and carried to Step 3.
- **The required re-review is complete.** Its packet, reviewer and result
  are recorded above, and the conductor's closing evidence covers the three
  findings it left.
- **The tracker row is unchanged and still `active`:**
  `200 | [pypi-publish-2-1-0](pypi-publish-2-1-0.md) | active |
  lifecycle-and-free-form-relate | M31 — …`. `milestone-plan.md` has no
  diff since `8515f1c`.
- **The RED-baseline checkpoint (Standard) holds.** No returned review
  leaves an unresolved contract or test-adequacy blocker. Every accepted
  should-fix is resolved. Phase 4's GO stands, with the release inputs
  unchanged since `X` and D9 re-runs recorded for every script change.

### Verification report (sync-and-commit, ship-milestone Step 1)

- Risk level: Standard (accepted at setup).
- Fast gate commands run: `ruff check .`; `ruff format --check .`;
  `mypy src/ tests/`; `pytest -q` and `--collect-only`; from the docs root,
  `docs index .`, `docs check .` and `docs check . --stale 14`; `cmp` of
  `INDEX.md` with its snapshot and of both bundled references with `docs/`;
  readiness (P1.4's arguments); the non-disclosing token search (P1.4) on
  the staged diff.
- Deep gate commands run: Phase 4's builds, schema, probes, TestPyPI
  rehearsal and comparators (recorded in Phase 4); the D9 re-runs (the
  audit's, and this pass's); `$S/tools/rereview-controls.sh` (19/19).
- Deferred or not configured: coverage, the hidden suite and mutation
  tooling are not configured. The served-wheel checks are Step 2's.
- Visible test result: 1671 passed, 1671 collected.
- Expected visible-test state: an adequate GREEN baseline under D3 — a
  publish ships no new behaviour. The RED evidence is Phase 2's: readiness
  failed exactly the contract reasons, and the 2.0.0 control failed exactly
  the 13 release-bound checks.
- Hidden/generalization result: one result set across wheel (a) and the
  TestPyPI-served rehearsal (W1 aside); the 2.0.0 control behaved as
  frozen.
- Coverage: not configured.
- Mutation: 17/17 hand-applied mutants and negative controls detected, each
  by its intended check.
- Property/stateful: N2 and W3 are write-sensitive and pass; (a) = (b) by
  sha; the rehearsal payloads equal (a)'s.
- Fuzz: not applicable.
- Benchmark/security/schema/migration: schema and security pass (Phase 4,
  and this pass's synthetic controls); benchmark and migration not
  applicable.
- Mock audit: no mocks; the negative controls are scratch wrapper
  executables, never committed.
- Taste triage: complete — T1–T3 fixed, T4 waived with a reason, patch
  bloat carried to Step 3; none untriaged.
- Ship-milestone Step 1 review ledger: this pass is closed, and
  `final-sync` is `ready`.
- Semantic tracker row and branch identity: row
  `200 | pypi-publish-2-1-0 | active | lifecycle-and-free-form-relate`;
  project `docs`, project path empty, artifact stem `pypi-publish-2-1-0`;
  branch `pypi-publish-2-1-0/phases-1-4` under root `pypi-publish-2-1-0/`;
  `status.md` links the tracker without copying rows or naming next work.
- Contract/test matrix status: current — C1–C19, P1 ids, results through
  Phase 4 and this pass.
- Docs check: `docs check .` exit 0. `--stale 14` exits 1, with only the
  pre-existing `stale` warnings on long-unchanged reference documents (as
  at Step 0), reviewed.
- Diff scope: `8515f1c..HEAD` touches only D1's allowed paths —
  `CHANGELOG.md`, `README.md`, the two `tests/manual/` scripts, and
  `docs/`. `src/`, `pyproject.toml`, `LICENSE` and `.gitignore` are
  unchanged since `X`.
- Operator approvals: D2, D3, D10 and D13 (setup). No new operator question;
  DP-1 was the conductor's decision under Standard authority.
- High-risk RED-baseline approval: not applicable (Standard).
- Remaining risks: the PyPI token is validated only by use (Phase 6);
  backend drift is guarded by D4 and the recorded build environment; Step
  2 will almost certainly re-date the CHANGELOG under D7.
- Ship-milestone Step 3 evidence: not applicable (Step 1).
- Commit: the sync commit that records this report; the return report gives
  its sha.
- Push: `git push -u origin pypi-publish-2-1-0/phases-1-4` (the milestone
  branch's first push; never `main`, no tags); the return report gives the
  result.

- final-sync: `ready`.

## Phase 5 — Update Base Interfaces

Date: 2026-10-28 (23:24 CET) onward. Branch
`pypi-publish-2-1-0/phases-5-10`, from the closed Step 1 sync `d5a23ef`.
Step 2 runs in a new session with its own `$S`; every value it needs is read
from this log. Shell state does not persist between tool calls, so `$S/env.sh`
carries P1.3's environment plus `X`, `TAG_TARGET` (once recorded) and
`READY`/`PROBE` as shell functions, and every command sources it first.

### Restatement before work

- **Contract invariants.** D1's boundary: nothing under `src/`, no product
  test, only the INDEX snapshot among fixtures. D4's chain of custody: wheel
  (c) = (a) by sha or nothing is uploaded; explicit filenames; `dist/` holds
  exactly the two files. D2 holds only while every *Error cases*
  precondition is true at the moment of each action; any stop row voids it.
  At most one upload, and no file is ever re-sent once published. The tag is
  annotated at the tag-target commit, and only after served verification
  (D13). Host state moves only as D10 lists, and only in Phase 9. No
  credential value is printed, logged or committed (D6).
- **Forbidden shortcuts.** No expected value from a build's own output; no
  artifact compared with itself; no glob or `--skip-existing`; no re-dating,
  renaming or re-versioning past a stop; no weakened or skipped check to reach
  GREEN (the G2 change below is a *Check calibration* correction that keeps
  every INDEX byte pinned except the generated date stamp, as the product test
  does); no special-casing of visible examples; no unisolated host run outside
  Phase 9.
- **Visible drivers vs explicit workflow gates.** Visible: the 1671-test
  product suite, regression evidence only. Explicit gates, none in default
  discovery: readiness, the probe, `twine check`, the D4 comparisons, the D9
  diff and blobs, the token search, the D1 scope check, `docs check .` with
  the snapshot and mirrors, the paired host checks, the guard step, the
  peeled-tag check and `gh release view`.
- **Risk and gates.** Standard (carried). Lite gates plus the
  hidden/generalization smoke (the served wheel as the third wheel install),
  the property/stateful smoke (the sha chain, N2/W3), the mock audit and the
  Step 2 dual review, which runs after the irreversible actions (D2's
  post-upload triage).
- **Mock policy.** No mocks. Negative controls are scratch clones and the
  old probe blob, never committed.
- **Taste anchors.** M29's phase narrative and sha tables; the runbook's
  append-only lessons; M30's trio shape; `tests/test_cli_index.py`'s
  `_normalize_generated_date` for the G2 fix (stdlib, a few lines, display
  name unchanged). **State-once:** each new decision lands once — in its
  D-id, P1 row or stop-table row, amended in place with a dated note — and
  measured values live only in this log; `status.md` carries no counts.

### Planning questions — conductor-resolved, Step 2

Step 2's planning found one defect in the frozen commands and four
false-stop risks. The conductor resolved all five under Standard authority
(2026-10-28). Each operative rule lives only where the last column says.

| # | Question | Resolution | Where it lands |
|---|---|---|---|
| OQ-S2-1 | G2 compares `docs index --dry-run` with the copy's `INDEX.md` byte for byte, but `render_index` stamps today's date; on any day after `d5a23ef`'s `_Generated 2026-10-28.`, Phase 7's probe would fail G2 after the upload | **(A)**: calibrate G2 before build (c) — normalise only the `_Generated YYYY-MM-DD.` stamp on both sides with the product test's regex; reproduce first; run D9's script re-run set plus a cross-day control and an edited-entry mutant. Not a release input, so no `.postN` | P1.2 (G2 row); *Release anchors (current)*; the record below |
| OQ-S2-2 | The known intermittent `test_d4_install_skill_is_idempotent` segfault (M30's log) would trip "pytest other than 1671 passed" at the upload gate | **(B)**: one full re-run, only when that test crashing is the sole non-pass; the re-run must report 1671 passed; both runs recorded; anything else stops | *Error cases*, the general P1.5 expectation row |
| OQ-S2-3 | The update cache's 24-hour throttle lets any unisolated host `docs` run move its sha against the Phase 1 baseline | **(B)**: pairwise — each block's after-sha against its before-sha; a change between blocks is recorded with its mtime, not attributed to the milestone | P1.3 (*The host check*); the host-state stop row points there |
| OQ-S2-4 | Phase 7's `pip install` and Phase 9's `pipx upgrade` had no index-lag poll; a lagging index would hit a stop row after the upload | **(A)**: poll the PEP 691 simple JSON (at most 10 × 30 s) until both 2.1.0 files are listed with sha256 = (c)'s | P1.5 Phase 7; the Phase 9 objective points there |
| OQ-S2-5 | The notice step named no command; 2.0.0's hook runs only after dispatch and fetches with a 1 s timeout | **(A)**: `~/.local/bin/docs check .` in a fresh scratch tree, up to three attempts with a fresh scratch cache each; then the same on P1.6's sha-checked scratch 2.0.0; else C16 unmet and Phase 9 continues | The Phase 9 objective, item 1 |

### 5.1 Read-only preflight (before any edit)

At 23:24–23:26 CET, at `d5a23ef` with a clean tree:
- **Resume state:** no Step 2 commit; per-version JSON
  `docs-cli/2.1.0` **404**; the PEP 691 simple JSON lists versions `1.3.0 …
  2.0.0` and no 2.1.0 file; no local or remote `v2.1.0`; `gh release view
  v2.1.0` → "release not found"; one worktree. A fresh start.
- **D9:** `git diff --quiet "$X"..HEAD -- src pyproject.toml README.md
  LICENSE .gitignore` holds; the blobs were `cb542802…` and `2d6a0c31…`, the
  anchors.
- **Transport:** `git ls-remote origin refs/heads/main` → `193fc71…`, exit 0
  (the tunnel noise on stderr again); `gh auth status` exit 0, `ArtRichards`.
  Local `origin/main` = GitHub's `main` = `193fc71…`; no fetch was needed.
- **`~/.pypirc`:** P1.5's shape command printed exactly the anchors' four
  lines.
- **Toolchain:** twine 7.0.0 (PyPI's newest), build 1.5.0, pip 24.0, Python
  3.12.3 — Phase 4's. PyPI's newest hatchling and its dependencies still
  equal the anchors' build environment.
- **Host:** recorded destination absent; update cache `39739c29…` (mtime
  2026-10-28 08:29), the baseline.

### 5.2 G2 calibration (OQ-S2-1)

**Reproduced first.** A scratch clone of `d5a23ef` with its `INDEX.md`
summary re-dated to `_Generated 2026-10-27.` — the shape of a tree indexed
the day before — made the anchored probe (`2d6a0c31…`, `--group contract`,
the editable build, `--repo` the clone) report exactly one failure: `FAIL
docs index --dry-run on a copy of this docs tree reproduces its INDEX.md and
writes nothing — stdout differs from the copy's INDEX.md`.

**The change.** `release_probe.py` gains `without_generated_date()`, which
blanks the first `_Generated \d{4}-\d{2}-\d{2}\.` match — the regex and
rationale of `tests/test_cli_index.py`'s `_normalize_generated_date` — and
G2 compares both sides through it. Every other INDEX byte is still pinned,
the write check (`p.unchanged`) stays, and the display name is unchanged.
+11/−1 lines; stdlib only; ruff, the formatter and mypy clean. The new blob is
`763b7dd7c22c7305f8215b1415b1ff67eb2d3fb1`.

### D9 re-run for the G2 calibration

The probe changed after its Phase 4 run, so D9's script re-run applies. No
release input changed, so `X` stands and there is no `.postN`. Every run used
a fresh venv and scratch XDG; the host check was unchanged across the block.

| # | Run | Result |
|---|---|---|
| 1 | Rebuild from `X` in a scratch clone, `--outdir` in scratch, `SOURCE_DATE_EPOCH` unset | wheel `2c5fa0b3…`, sdist `1d327a97…` — equal to (a); `Generator: hatchling 1.33.0`; the isolated build env resolved `hatchling-1.33.0 packaging-26.3 pathspec-1.1.1 …`, the anchors' set |
| 2 | Probe, new blob, on a fresh venv of that wheel, `--group all --expect-version 2.1.0` | exit 0, 25 passed; result lines **identical** to the anchors' block |
| 3 | Probe on a fresh `--index-url https://test.pypi.org/simple/ --no-deps` install of `docs-cli-rehearsal==2.1.0` (its `docs_cli/` equal to (a)'s extraction before running), `--no-version-check` | exit 0, 24 passed, 1 skipped; lines **identical** to the anchors' block with W1 SKIP |
| 4 | Probe on the editable build, contract group | exit 0, 21 passed; lines equal the anchors' first 21 |
| 5 | Probe on P1.6's scratch 2.0.0 (downloaded wheel sha `bcd8aa45…` = E1, checked before running) | exit 1, 12 passed, 13 failed; statuses identical to Phase 2's control column |
| 6 | Cross-day control: the re-dated clone above, old blob vs new | old: FAIL G2 only (20 passed); new: 21 passed; the two outputs differ in the G2 line alone |
| 7 | Mutant: a same-day clone with one `INDEX.md` entry line edited (` (edited)` appended to the `milestone-plan.md` entry) | FAIL G2 only, under both the old and the new blob — the normalisation masks nothing but the date stamp |

Then the fast gate: ruff clean, 52 files formatted, mypy no issues in 53
files, **1671 passed**, 1671 collected, readiness 25/25 (`--release-date
2026-10-28`), `docs check .` exit 0, the snapshot and both mirrors
identical. Committed as `f7f8f62`.

### 5.3 Date gate (D7)

`f7f8f62` landed at 23:33 CET, after the plan's 23:30 midnight guard, so
5.4 waited for the local date to roll rather than race it. At 00:00 CET on
2026-10-29, `date +%F` no longer equalled the heading, so `33c936f` re-dated
`CHANGELOG.md` line 8 from `## 2.1.0 — 2026-10-28` to `## 2.1.0 —
2026-10-29` — one line, no other file, no `docs touch` (the runbook's M11
lesson). The token search and the D1 scope check were clean.

### 5.4 P1.5's Phase 5 block, at `33c936f` (00:00–00:02 CET)

| Command | Result |
|---|---|
| The 404 probe | `404` |
| `git diff --quiet "$X"..HEAD -- src pyproject.toml README.md LICENSE .gitignore` | exit 0: the release inputs are unchanged since `X` |
| `git hash-object` of both scripts | `cb542802…` and `763b7dd7…`, the anchors |
| `origin/main` against GitHub's `main` | both `193fc71…`; no fetch ran |
| `READY --repo . --release-date 2026-10-29` | exit 0, 25 passed |
| `pytest -q` | **1671 passed** in 82 s, first run (OQ-S2-2's re-run was not needed); 1671 collected |
| `git ls-remote origin refs/heads/main && gh auth status` | both exit 0 (the tunnel noise on stderr) |
| P1.5's `~/.pypirc` shape command | exactly the anchors' four lines |
| Toolchain | twine 7.0.0, build 1.5.0, pip 24.0, Python 3.12.3 — Phase 4's |
| `git status --porcelain` | empty |

The host check was unchanged across the block (update cache `39739c29…`,
recorded destination absent).

### 5.5 Build (c), at `33c936f`

| Check | Result |
|---|---|
| `rm -rf dist/ && .venv/bin/python -m build`, `SOURCE_DATE_EPOCH` unset, clean tree | exit 0; `ls -A dist/` shows exactly `docs_cli-2.1.0-py3-none-any.whl` and `docs_cli-2.1.0.tar.gz` |
| Wheel (c) | `2c5fa0b3e3c3db05e4f452bc900b31fa7a7acb5b3f330cd8d52a9bd80c19a185` — **equal to (a)**; D4's remedy was not needed |
| Sdist (c) | `c120fc1db71db08306ec1e002dedb1adcd95dc08bd5a8c1f775cda772696404d` — it moved from (a)'s with `docs/` and `tests/manual/`, as D4 expects |
| `Generator:` | `hatchling 1.33.0` |
| The (c) manifest against (a)'s 15-line block, extracted mechanically from this log | identical |
| `twine check` on both files by name | PASSED, PASSED |
| Schema | `Metadata-Version: 2.5`, `Requires-Python: >=3.11`, `Provides-Extra: dev`, five `Requires-Dist … extra == 'dev'`; `CHANGELOG` in neither artifact |

**`TAG_TARGET` = `33c936f447dfb31078dc0c07c9e4fd2297ed747d`**, recorded in
*Release anchors (current)* with (c)'s shas. This checkpoint commit is a
child of the tag target and changes documents only, so the release inputs
still diff empty against `X`. Every Phase 5 exit criterion holds; nothing
has been uploaded.

## Phase 6 — Implement Offline/Core Path

Date: 2026-10-29, 00:03–00:05 CET. The PyPI upload under D2, after the
pre-upload checkpoint `2e04d43` made `TAG_TARGET` and (c)'s shas durable.

**6.0 Resume check.** HEAD `2e04d43`; the per-version JSON 404; no local
or remote `v2.1.0`; `TAG_TARGET` in scratch equal to the committed anchor.
A fresh upload, not a resume.

**6.1 P1.5's re-checks**, run by one script that reaches `twine` only if
every one passes, at 00:03:59 CET (23:03:59 UTC):
- `date +%F` = `2026-10-29` = the CHANGELOG heading;
- the per-version JSON: `404`;
- `ls -A dist/`: exactly `docs_cli-2.1.0-py3-none-any.whl` and
  `docs_cli-2.1.0.tar.gz`;
- `sha256sum`: `2c5fa0b3…` and `c120fc1d…` — (c)'s, the wheel equal to the
  anchor (a).

**6.2 The upload.** `env -u TWINE_REPOSITORY -u TWINE_REPOSITORY_URL -u
TWINE_USERNAME -u TWINE_PASSWORD .venv/bin/twine upload --repository pypi
--non-interactive dist/docs_cli-2.1.0-py3-none-any.whl
dist/docs_cli-2.1.0.tar.gz` — **exit 0** at 00:04:04 CET (23:04:04 UTC),
after uploading both files to `https://upload.pypi.org/legacy/` and printing
`View at: https://pypi.org/project/docs-cli/2.1.0/`. Its captured output
was searched for token-shaped strings by count before anyone read it: 0.
The `~/.pypirc` token is therefore valid (*Assumptions*, validated by use).

**6.3 The outcome.** Twine exited 0, so the PyPI-upload stop row did not
apply. The per-version JSON returned 404 at 00:04:12, 00:04:19 and 00:04:49
(about a minute of lag, as in Phase 4) and listed both files at 00:05:19:

| File | JSON sha256 | = (c) | `upload_time` (UTC) | Size | Yanked |
|---|---|---|---|---|---|
| `docs_cli-2.1.0-py3-none-any.whl` | `2c5fa0b3e3c3db05e4f452bc900b31fa7a7acb5b3f330cd8d52a9bd80c19a185` | yes | 2026-10-28T23:04:01Z | 231029 | no |
| `docs_cli-2.1.0.tar.gz` | `c120fc1db71db08306ec1e002dedb1adcd95dc08bd5a8c1f775cda772696404d` | yes | 2026-10-28T23:04:03Z | 1901359 | no |

**D7 and the two calendars.** The upload ran at 00:04 CET on 2026-10-29,
which is 23:04 UTC on 2026-10-28, so PyPI's `upload_time` carries the
previous UTC day. D7 dates the heading by the local calendar date of the
upload, so `## 2.1.0 — 2026-10-29` is correct; both are recorded here.

Exactly one upload ran; no file was re-sent. `docs-cli==2.1.0` is live on
PyPI at <https://pypi.org/project/docs-cli/2.1.0/>.

## Phase 7 — Update Tool/Wrapper Layer

Date: 2026-10-29, 00:06–00:08 CET. Served verification first, then the tag
and the release (D13). Every command is P1.5's Phase 7 block, with the plan's
two additions: the simple-index poll (OQ-S2-4) and the served wheel's
extraction kept for Phase 9.

**7.0 Resume check.** No local or remote `v2.1.0`; `gh release view
v2.1.0` → "release not found". Nothing to skip.

**7.1 Simple-index poll (OQ-S2-4).** The PEP 691 JSON at
`https://pypi.org/simple/docs-cli/` listed no 2.1.0 file at 00:06:11 and
both at 00:06:17, each with sha256 equal to (c)'s.

### 7.2 Served verification

**The chain of custody**, wheel and sdist:

| Build | Wheel sha256 | Sdist sha256 |
|---|---|---|
| (a) Phase 4, at `X` | `2c5fa0b3e3c3db05e4f452bc900b31fa7a7acb5b3f330cd8d52a9bd80c19a185` | `1d327a97912ab70ac53829e2af2d568c119d8ce555e9032264e744ba1d6d07d4` |
| (b) post-rehearsal rebuild, at `X` | `2c5fa0b3…` (= a) | `1d327a97…` (= a) |
| (c) Phase 5, at the tag target `33c936f` | `2c5fa0b3…` (= a) | `c120fc1db71db08306ec1e002dedb1adcd95dc08bd5a8c1f775cda772696404d` (moved with `docs/`; manifest = (a)'s) |
| PyPI per-version JSON digest | `2c5fa0b3…` (= c) | `c120fc1d…` (= c) |
| PyPI-served bytes, downloaded | `2c5fa0b3…` (= c) | `c120fc1d…` (= c) |

**Bit-perfect for both artifacts.** The wheel sha is one value across (a),
(b), (c), the JSON and the served bytes; the sdist is anchored at (c) and
equal to both served forms.

| Step | Result |
|---|---|
| `git worktree add --detach "$S/tag-tree" "$TAG_TARGET"` | at `33c936f` |
| Each per-version JSON `url` fetched with `curl -sSf` into a fresh empty `$S/dl-served/` | both files; each sha equals (c)'s and the JSON digest |
| The served wheel extracted to `$S/x/served-wheel` | `diff -r` against (c)'s extraction: empty — Phase 9's reference |
| `pip install --no-cache-dir --no-deps --index-url https://pypi.org/simple/ docs-cli==2.1.0` into a fresh venv | exit 0; the installed `docs_cli/` equals (c)'s extraction before anything ran; `INSTALLER` reads `pip` |
| The probe from the worktree (`--repo "$S/tag-tree"`, blob `763b7dd7…`), `--group all --expect-version 2.1.0` | **exit 0, 25 passed**; result lines **identical** to the anchors' block |
| `git worktree remove "$S/tag-tree"` | its status was clean; removed without `--force`; one worktree left |
| The guard step: `validate.yml@a997954` lines 1210–1293, dedented | 84 lines, sha256 `2e2fc83d…` = the anchor |
| The guard step from a fresh empty directory, `PATH` on the served venv (`docs` and `python3` both resolved there) | **exit 0**, printing `verbless-metadata stopgap consistent with docs-cli pin (lifecycle verb: True, free-form relate: True)` |
| The host check, across the install, the probe and the guard step | unchanged |
| The suite checkout | `status --porcelain` empty, HEAD `a997954` |

**G2 on the calendar it was fixed for.** The probe ran on 2026-10-29
against the tag target's `INDEX.md`, generated `_Generated 2026-10-28.`, and
passed — the run that the byte-exact form would have failed after the
upload (OQ-S2-1).

### 7.3 Tag and release

| Step | Result |
|---|---|
| `TAG_TARGET` against `2e04d43`'s committed anchor | equal: `33c936f447dfb31078dc0c07c9e4fd2297ed747d` |
| `git merge-base --is-ancestor "$TAG_TARGET" HEAD` | yes |
| `git tag -a v2.1.0 -m "docs-cli 2.1.0 — docs lifecycle and free-form docs relate" "$TAG_TARGET"` | tag object `c2ce8fe615dd00d6394e2e816428766cc79f2dd8`, unsigned (`tag.gpgSign` unset) |
| `git push origin v2.1.0` — Step 2's only push (D2) | exit 0, `[new tag] v2.1.0 -> v2.1.0` |
| `git ls-remote origin 'refs/tags/v2.1.0^{}'` | **`33c936f447dfb31078dc0c07c9e4fd2297ed747d` = the tag target**; the plain ref is the tag object `c2ce8fe…` |
| The notes: the tag target's `CHANGELOG.md` through P1.5's `awk` | 2668 bytes, non-empty; equal to the working tree's extraction; `git diff --quiet "$TAG_TARGET" -- CHANGELOG.md` holds |
| `gh release create v2.1.0 --verify-tag --title "docs-cli 2.1.0" --notes "$NOTES"` | exit 0 |
| `gh release view v2.1.0` | <https://github.com/ArtRichards/docs-cli/releases/tag/v2.1.0>, "docs-cli 2.1.0", not a draft or prerelease, published 2026-10-28T23:07:28Z, **Latest** (`gh release list`) |

GitHub reports the release's `targetCommitish` as `main`, its default for a
release made from an existing tag; the tag itself pins the commit, as the
peeled check shows. Nothing else was pushed: no branch, no other tag.

## Phase 8 — Run Tests (GREEN)

Date: 2026-10-29, 00:08–00:12 CET.

### 8.1 The fast gate at the tag target

In a detached worktree `$S/t8` at `33c936f`, with the main `.venv`'s
binaries by absolute path. The editable install resolves `docs_cli` from the
main tree's `src/`, which is byte-identical to the tag target's (`git diff
--quiet 33c936f HEAD -- src`), so the suite tests the tag target's code.

| Check | Result |
|---|---|
| `ruff check .`; `ruff format --check .`; `mypy src/ tests/` | clean; 52 files formatted; no issues in 53 files |
| `pytest -q` | **1671 passed** (84 s); `--collect-only`: 1671 |
| The two suite-probe replicas, by node id | 2 passed |
| `docs check .` from `docs/` | exit 0 |
| `INDEX.md` against the snapshot; both bundled references against `docs/` | identical |
| `docs index . --dry-run` against `INDEX.md`, the `_Generated` stamp normalised on both sides | identical (the tree's stamp reads 2026-10-28; a raw compare is calendar-sensitive at a past commit) |
| `READY --repo "$S/t8" --release-date 2026-10-29` (`D`, the tag target's CHANGELOG date) | exit 0, 25 passed |
| The host check across the block; the worktree's status, then `git worktree remove` | unchanged; clean; removed, one worktree left |

### 8.2 One probe, three wheel installs

The matrix's *Results summary* carries the table: every wheel install gave
the same result set, with only W1 skipped on the rehearsal.

### 8.3 The suite's full guard — expected to fail

**Frozen before the run** (2026-10-29 00:10 CET). Against 2.1.0, the full
guard step run inside the suite's tree at `a997954` must exit 1 with
exactly these ten lines on stderr, because the suite still carries the
stopgap that 2.1.0 retires (E11). A different signature — for example a
"cannot perform" line — would contradict Phase 7 and stop the milestone.

```
pinned docs-cli performs non-archived Lifecycle: transitions (docs lifecycle); retire that half of plugins/agent-playbook-suite/skills/_shared/references/verbless-metadata-edits.md and prescribe the verb instead
pinned docs-cli performs free-form Related: edits (free-form docs relate); retire that half of plugins/agent-playbook-suite/skills/_shared/references/verbless-metadata-edits.md and prescribe the verb instead
both verbs are available; delete plugins/agent-playbook-suite/skills/_shared/references/verbless-metadata-edits.md
plugins/agent-playbook-suite/skills/_shared/references/milestone-tracker.md: still references the retired stopgap
plugins/agent-playbook-suite/skills/create-milestones/SKILL.md: still references the retired stopgap
plugins/agent-playbook-suite/skills/create-milestones/references/milestone-playbook.md: still references the retired stopgap
plugins/agent-playbook-suite/skills/manage-milestone-tracker/SKILL.md: still references the retired stopgap
plugins/agent-playbook-suite/skills/project-foundation/SKILL.md: still references the retired stopgap
plugins/agent-playbook-suite/skills/project-foundation/references/foundation-playbook.md: still references the retired stopgap
plugins/agent-playbook-suite/skills/ship-milestone/SKILL.md: still references the retired stopgap
```

**Result** (00:10:47 CET). Run in a read-only export (`git -C
~/opt/agent-playbook-suite archive a997954 | tar -x -C "$S/suite-a997954"`),
not in the live checkout, with `PATH` on the served venv: **exit 1**, stdout
empty, and stderr **equal, line for line, to the frozen block**. The guard is
working: the served 2.1.0 performs both edits, so the suite's stopgap must
retire in its pin-bump PR, and these ten lines are that PR's checklist (the
feedback-log hand-off). The suite checkout's `status --porcelain` stayed
empty and its HEAD `a997954`; the host check was unchanged.

M30's probe assumption is validated against the served wheel: the replicas
pass at the tag target (8.1), S1 and S2 pass on the served executable, and
the extracted guard step reads True / True (Phase 7).

## Phase 9 — Integrate / Accept / Dogfood

Date: 2026-10-29, from 00:11 CET. Host work per D10, in its order.

### 9.1 The update notice (OQ-S2-5)

The aggregate JSON (`https://pypi.org/pypi/docs-cli/json`) already read
`info.version` 2.1.0 at 00:11:22. In a fresh scratch tree with an empty
`.docs.toml`, the host's pipx 2.0.0 binary ran `~/.local/bin/docs check .`
twice:

| Run | Environment | Exit | stdout | stderr |
|---|---|---|---|---|
| Control | `env.sh` as is (`DOCS_CLI_NO_UPDATE_CHECK=1`) | 0 | `docs: no violations found` | empty |
| Notice, attempt 1 | `env -u DOCS_CLI_NO_UPDATE_CHECK -u CI -u DO_NOT_TRACK XDG_CACHE_HOME="$S/xdg/notice-1"` | 0 | identical | exactly `docs: update available 2.0.0 -> 2.1.0 — run: pip install -U docs-cli` |

**C16 is met on the first attempt**: one notice line, last on stderr, with
the exit code and stdout unchanged. The scratch `XDG_STATE_HOME` holds no
recorded destination, so no skill-hint line could follow. The cache the run
wrote is under `$S/xdg/notice-1`; the host's update cache sha and the
absent recorded destination were unchanged across the block. No retry or
fallback was needed.

### 9.2 The binary

At 00:11:54 the PEP 691 simple JSON listed both 2.1.0 files with (c)'s
sha256 (OQ-S2-4). Then, under `env.sh` (`PIP_CONFIG_FILE=/dev/null`; pipx's
log and cache and pip's cache land under the scratch XDG directories; pipx's
home stays `~/.local/share/pipx`), `pipx upgrade docs-cli` at 00:12:05:
exit 0, "upgraded package docs-cli from 2.0.0 to 2.1.0".

| Check | Result |
|---|---|
| `~/.local/bin/docs --version` | `docs 2.1.0`, exit 0 |
| `docs_cli-2.1.0.dist-info` in the pipx venv | no `direct_url.json`; `INSTALLER` reads `pip` — an index install |
| `pipx_metadata.json` | `package_or_url` `docs-cli`, `package_version` `2.1.0`, `pip_args` `[]` |
| `diff -r -x __pycache__ "$S/x/served-wheel/docs_cli"` against the pipx venv's `docs_cli` | empty: the host runs the served bytes |
| `ls --time-style=full-iso -la ~/.local/share/pipx/shared` | unchanged |
| The host check across the block | update cache unchanged; recorded destination still absent |

**A correction to the plan's assumption.** Step 2's planning expected pipx
not to touch its shared libraries, because they were updated on 2026-10-26
and pipx's 30-day rule had not expired. pipx printed "upgrading shared
libraries…": its `upgrade` command always runs `pip install -q --upgrade
"pip >= 23.1"` in `~/.local/share/pipx/shared` and then touches
`shared/bin/pip` (`pipx/shared_libs.py`, `upgrade`); the 30-day rule gates
other commands only. A deeper look than the frozen listing check: the only
path under `shared/` newer than this session's start is `bin/pip`, its mtime
now 00:12:05; pip stays 26.2.2 with its `dist-info` dated 2026-10-26, so no
package changed. That marker touch is part of the authorized `pipx upgrade`
(D10), not a separate host write, and neither stop-row observable moved. The
runbook records the behaviour.

### 9.3 The skill

Recorded first: the sha256 of the seven files under `~/.claude/skills/docs`
(M29's refresh, directory mtime 2026-08-16), the backup symlink's `stat`
(`→ /home/user/opt/docs-cli/src/docs_cli/skill`, 2026-10-28 11:55:37), and a
full-time listing of `~/.claude/skills`. Then, at 00:13:12, with the
published binary and the host's real XDG state, so the destination is
recorded where D10 wants it:

```
env -u XDG_STATE_HOME -u XDG_CACHE_HOME DOCS_CLI_NO_UPDATE_CHECK=1 ~/.local/bin/docs install-skill --force --dest ~/.claude/skills/docs
```

Exit 0, `docs: install-skill: copied bundled skill to
/home/user/.claude/skills/docs`.

| Check | Result |
|---|---|
| `diff -r "$S/x/served-wheel/docs_cli/skill" ~/.claude/skills/docs` | empty — seven files, byte-identical to the served wheel |
| `~/.local/state/docs-cli/install-skill.json` | exactly `{"dest": "/home/user/.claude/skills/docs"}` |
| `test ! -e "$S/xdg/state/docs-cli/install-skill.json"` | holds |
| The backup symlink's `stat` | unchanged |
| The `~/.claude/skills` listing | only `docs` changed, and the directory's own mtime, which replacing an entry moves; `synced`, `.trash` and the other entries untouched |
| The host check | the update cache sha unchanged; the recorded destination moved from absent to `~/.claude/skills/docs` — D10's one authorized transition. From here on the host check expects it present |

### 9.4 The sweep — a read-only census

**Frozen before the run** (2026-10-29 00:14 CET), as `grep -E` patterns:

| | Pattern | Looks for |
|---|---|---|
| A | ``(Edit\|edit\|Flip\|flip\|Promote\|promote\|Change\|change\|Set\|set)[^\|]{0,40}`?Lifecycle: ?`?(draft\|active\|done)`` | a hand-edited `Lifecycle:` |
| B | ``careful Edit on the metadata block\|Related:`? typed edges\|Related:[^\|]{0,60}(by hand\|hand-edit\|directly)\|direct \*\*metadata\*\* edits`` | a hand-edited `Related:` |
| C | `verbless-metadata\|stopgap` | stopgap references |
| D | `free-form verbs stay hand-edited\|refuses to edit them\|six recognized\|recognized (reciprocal )?verbs only\|only the (six\|three) recognized\|unknown verb` | an assumption that `relate` refuses free-form verbs |

Targets: the installed plugin cache
(`~/.claude/plugins/cache/agent-playbook-suite/agent-playbook-suite/0.8.3/skills`,
`skills/docs` excluded) with `grep -rnE`; and `git -C
~/opt/agent-playbook-suite grep -nE <pattern> <rev> -- plugins/` at `554ebf2`
(`main`, v0.8.3) and at `a997954` (the stopgap branch). **Oracle:** the
census must hit E11's known sites — `create-milestones/SKILL.md:117` (rule
3), `milestone-playbook.md:513` (§2d) and `:600` (§2f), and
`foundation-playbook.md:180` — or the patterns are rejected.

**Result** (00:14 CET). 60 matched lines: 10 in the installed cache, 18 on
`main`, 32 on `a997954`. **The oracle holds**: all four E11 sites are hit in
the cache and on `main`; on `a997954`, §2d (`:513`) and the foundation
playbook (`:180`) are hit, while rule 3 and §2f were rewritten by the
stopgap and now match C instead. `main` matches the cache line for line, as
v0.8.3 should. The suite's `status --porcelain` stayed empty with HEAD
`a997954`, and nothing under the plugin cache is newer than this session's
`env.sh`, before and after.

Paths are under `plugins/agent-playbook-suite/skills/`; "rx" is a
prescription 2.1.0 supersedes, "ok" a statement still true under 2.1.0.

| File | Cache = `main` (0.8.3) | `a997954` (stopgap) | Class |
|---|---|---|---|
| `create-milestones/SKILL.md` | B `:117` rule 3 — direct metadata edits limited to `Lifecycle:` and free-form `Related:` | C `:55`, `:125` (rule 3 now cites the stopgap) | rx |
| `create-milestones/references/milestone-playbook.md` | B `:513` §2d (`Related:` by careful Edit); A `:600` §2f, `:953` (flip `Lifecycle:`) | B `:513`; A `:602`, `:956`; C `:601` | rx |
| `project-foundation/references/foundation-playbook.md` | B `:180` (careful Edit to add edges) | B `:180`; C `:650` | rx |
| `project-foundation/SKILL.md` | D `:81` — recognized verbs through `docs relate` | B `:84` (free-form `Related:` as hand-edits); C `:58`, `:86`; D `:87` | ok at 0.8.3; rx at `a997954` (`:84`, `:86`) |
| `_shared/references/milestone-tracker.md` | A `:212` (promote the status doc to `Lifecycle: active`); D `:192` | A `:215`; C `:210`; D `:192` | A rx; D ok (recognized-verb operands) |
| `manage-milestone-tracker/SKILL.md` | A `:114` (same promotion) | A `:119`; C `:21`, `:115` | rx |
| `use-cases/references/use-cases-playbook.md` | A `:109` (flip `Lifecycle: draft` to `active`) | A `:109` | rx |
| `ship-milestone/SKILL.md` | — | C `:55`, `:214` (Step 0's up-front approval) | rx (stopgap only) |
| `_shared/references/verbless-metadata-edits.md` | — (absent) | C `:4`; D `:16`, `:17` | the stopgap policy itself |
| `docs/references/cli.md`, `convention.md`, `use-cases.md` (the vendored skill; the cache target excludes it) | 8 D lines on `main` — 2.0.0's "six recognized verbs" and `unknown verb` text | the same 8 | superseded by the 2.1.0 re-vendor |

The C hits on `a997954` name exactly the policy file and the seven files
the full guard lists (Phase 8). Under 2.1.0 every "rx" line becomes `docs
lifecycle <files> active` or `docs relate add <src> pairs-with|child-of
<dst>`; the feedback-log hand-off carries the list for the suite PR.

### 9.5 Dogfood

From `docs/`, `DOCS_CLI_NO_UPDATE_CHECK=1 ~/.local/bin/docs check .` — the
host's pipx binary, now `docs 2.1.0` — exit 0, "no violations found". The
host check was unchanged across it, the recorded destination present as
9.3 left it.

### 9.6 Liveness walk

Each output Step 2 produced, walked back from its consumer (the plan's
pull-style table):

| Output | Consumed by | State |
|---|---|---|
| The G2 calibration and its D9 record | Phase 7's served probe (G2 passed on 2026-10-29 against a 2026-10-28 INDEX); the runbook's standing probe; the Step 2 review | consumed; runbook in Phase 10 |
| `TAG_TARGET` in `2e04d43` | the Phase 7 worktree and tag, the release notes, the Phase 8 worktree; the D13 merge sentence | consumed; the merge sentence goes to the final report |
| (c)'s shas, manifest and `dist/` listing | the Phase 6 re-checks; the Phase 7 custody table; matrix C10 | consumed |
| The upload record | Phase 7; hand-off item 1; the completion summary | consumed; Phase 10 |
| `$S/x/served-wheel` | the 9.2 payload diff and the 9.3 skill diff | consumed |
| The served probe lines; the guard step True / True | matrix C11, C12 and the three-build table; hand-off item 2 | consumed; Phase 10 |
| The full guard's ten lines | the suite PR's checklist in the hand-off | Phase 10 |
| The tag's peeled sha; the release URL | matrix C13; `status.md`; the final report | consumed |
| The notice evidence; the host state record | matrix C15, C16; hand-off item 3 | Phase 10 |
| The sweep table | the hand-off; matrix C17 | Phase 10 |

Nothing is produced without a consumer. `git worktree prune` left one
worktree (the repository's own); the scratch venvs and `dist/` are removed
at Phase 10's cleanup.

## Milestone completion summary

_Not complete._
