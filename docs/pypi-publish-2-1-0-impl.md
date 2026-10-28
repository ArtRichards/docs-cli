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
  by the operator, each as recommended. Step 0 review-pass-001 is open, and
  Phase 1 — Define Contract follows the Step 0 review.**
  - Setup measured the publish surface read-only, recording thirteen pieces of
    evidence (**E1–E13**, below). It built, uploaded, installed and published
    nothing, and touched neither `~/.claude/skills` nor `~/.pypirc`.
  - The release is ready to run. Both registry slots are free, the TestPyPI
    detour still applies, the credentials are present and well formed, and
    `twine` is 7.0.0. The gate is GREEN at **1671**, and the version is
    already 2.1.0.
  - Three findings change the runbook's default path:
    - **E4:** the build backend is unpinned, and a new `hatchling` was
      published today (→ D4).
    - **E9:** this host has no recorded skill destination (→ D10, Q2).
    - **E10:** every `install-skill` run records its destination, so smoke
      runs must be isolated (→ D6).
  - The operator decided three things on 2026-10-28:
    - automatic release (D2), extended by Q1 → (A) to the `v2.1.0` tag push
      and the GitHub release in Step 2 (D13);
    - the ship-milestone mapping (D3);
    - the host refresh, by Q2: `pipx upgrade` plus
      `install-skill --force --dest ~/.claude/skills/docs`, with the backup
      symlink untouched (D10).
  - The conductor accepted the Standard risk level and every item settled
    without a question.
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
| 2. Write Tests (RED) | Pending | — | `tests/manual/release_readiness.py` and `tests/manual/release_probe.py`. Readiness is RED for exactly two reasons: the `UNRELEASED` heading and the publish-state sentence. The probe is GREEN on the editable build and fails the 2.1-only checks on the host 2.0.0 control. A hand-applied mutation smoke covers six targets. |
| 3. Create Data/Fixtures | Pending | — | The CHANGELOG is dated and its sentence removed (D7). The three README synopses are reconciled (D8). Probe trees are built inline or copied to scratch. Readiness turns GREEN. |
| 4. Run Tests (RED Baseline) | Pending | — | A pre-publish GREEN baseline (D3): the gate, then a clean build with its backend version recorded, the shas, `twine check` and the manifests. Then the local smoke and the probe on wheel (a). Then the TestPyPI rehearsal under `docs-cli-rehearsal`, with the probe run on the served wheel; the rename reverted; the canonical rebuild (b) matching (a). GO recorded. |
| 5. Update Base Interfaces | Pending | — | The pre-upload gate: Step 1's review closed, GO on record, no input changed since the rehearsal (D9), the slot free, credentials and toolchain unchanged, a clean tree. The CHANGELOG is re-dated if the day rolled. The tag-target build (c): `twine check`, sha (c) equal to (a), and the sdist members compared (D4). |
| 6. Implement Offline/Core Path | Pending | — | `twine upload --non-interactive dist/*` under D2. The per-version JSON's digests equal the local ones. |
| 7. Update Tool/Wrapper Layer | Pending | — | Install from PyPI. Download the served wheel and sdist, and compare them bit-perfect against (c). `docs --version` prints `docs 2.1.0`. Then, under D2 and D13, push the annotated `v2.1.0` tag at the tag-target commit and run `gh release create v2.1.0`. |
| 8. Run Tests (GREEN) | Pending | — | The probe's third identical run, on the PyPI-served wheel. The suite's capability probes, run verbatim, read True / True; the full guard's expected failure is recorded. Readiness at the tag-target commit. The full fast gate. |
| 9. Integrate / Accept / Dogfood | Pending | — | The update notice from a 2.0.0 install. `pipx upgrade docs-cli` to 2.1.0. `docs install-skill --force --dest ~/.claude/skills/docs` with the published binary, verified byte-identical and recorded as the destination. The backup symlink left untouched (D10). The read-only workflow-skill sweep (D10). A dogfood `docs check`. The liveness walk. |
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
| **E3** | **Credentials, shape only.**<br>- `~/.pypirc`: mode `600`, mtime 2026-10-28 16:57 (operator-copied from robbie.local today).<br>- Sections: `[distutils]` (`index-servers` = `pypi`, `testpypi`), `[pypi]` and `[testpypi]`.<br>- Both have `username = __token__` and a `password` that starts `pypi-` and is longer than 100 characters. `[testpypi]` has `repository = https://test.pypi.org/legacy/`.<br>- **No value was printed.**<br>- `gh auth status`: logged in as `ArtRichards` over SSH, with the `repo` scope. | Upload and tag/release access are in place. The PyPI token's validity is proven only by use (M11), at Phase 6. | D2, D6, Phase 6 assumption |
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

- **The operator decisions of 2026-10-28** are each recorded once in the task
  plan:
  - D2 — automatic release, extended to the tag and the release by Q1;
  - D3 — the ship-milestone mapping;
  - D6 — the credential facts;
  - D10 — the host refresh, from Q2;
  - D13 — the tag and the release in Step 2, from Q1.
- **Risk is Standard**, proposed and not raised as a question. The
  conductor's brief asked for a question only if High were warranted. The
  conductor accepted it on 2026-10-28.
- **Three findings re-shape the runbook's default path:**
  - E4, an unpinned backend published today (→ D4);
  - E9, no recorded destination (→ Q2, D10);
  - E10, smoke runs recording destinations (→ D6).
- **The recognized pairs with the archived M30 document are required.** The
  tracker contract counts an archived document as materialized and asks for
  `--reason`. They were rehearsed on a throwaway tree before the real write.
- **The candidate convention was taken up.** Its feedback-log entry names this
  setup as owner. The task plan states each binding decision once and refers
  to it by id. The entry stays open: one milestone's use is a trial, not a
  proven rule.
- **No OPEN QUESTION remains.** Q1 and Q2 went to the operator and were
  answered. Everything else is settled in the task plan's *Also settled,
  without a question*, which the conductor accepted.

### Setup questions — summary

The full packets are in the task plan's *Setup questions (Q1–Q2)*.

| # | Question | Recommendation | Status |
|---|---|---|---|
| Q1 | Do the `v2.1.0` tag push and the GitHub release happen in Step 2 under D2's automatic authorization? Or after the operator merges into `main` (B), or at a separate go (C)? | **(A)** in Step 2, tagging the uploaded artifacts' build commit. The stack's merge must preserve history. | **RESOLVED (operator, 2026-10-28) → (A).** Both happen in Step 2, right after the PyPI-served verification. The tag push is a recorded exception to pushing only through sync-and-commit. The conductor's history-preserving merge keeps the tag on `main` (D2, D13). |
| Q2 | Where does the host skill refresh go, is the pipx binary upgraded in the same phase, and is the backup symlink left alone? | `--dest ~/.claude/skills/docs`; upgrade the binary; leave the symlink. | **RESOLVED (operator, 2026-10-28) → refresh and upgrade.** `pipx upgrade docs-cli` to 2.1.0, served from PyPI. Then `install-skill --force --dest ~/.claude/skills/docs` with the published binary, which makes it the recorded destination. The symlink is untouched and the sweep stays read-only (D10). |

### Finalization — 2026-10-28

The operator answered both setup questions through the conductor, each as
recommended.

**Q1 → (A).** Right after the PyPI-served verification, Step 2 pushes an
annotated `v2.1.0` tag at the exact commit the uploaded artifacts were built
from, on `pypi-publish-2-1-0/phases-5-10`, and creates the GitHub release.
- Both are covered by the automatic authorization.
- The tag push is a recorded exception to pushing only through
  sync-and-commit.
- The conductor merges stacks with a history-preserving merge commit, as
  M30's `bf09748`, which keeps the tag on `main`. That dependency is recorded.

**Q2 → refresh and upgrade.** In Phase 9:
1. `pipx upgrade docs-cli` to 2.1.0, verified as served from PyPI;
2. `docs install-skill --force --dest ~/.claude/skills/docs`, run with the
   published binary. That directory becomes the recorded destination.

The backup symlink `~/.claude/skills/docs-local-source-backup-20260525-134621`
stays untouched, and the workflow-skill sweep stays read-only.

**The conductor accepted** the Standard risk level and every item settled
without a question:
- the release checks under `tests/manual/`, outside pytest discovery;
- the `.postN` re-rehearsal rule, on `docs-cli-rehearsal` only;
- the build-backend pin remedy, used only if it reproduces the rehearsed sha,
  and otherwise a stop;
- the implementation log archiving with the trio;
- the suite left untouched;
- the trial taste anchor;
- no version bump;
- no GitHub issue to answer.

The answers were folded in as follows.

- **Task plan:**
  - D2 is renamed *Release authorization*. It now covers the upload, the tag
    push and the GitHub release, and records the tag-push exception and that
    the conductor merges the stack.
  - D10 names the pipx upgrade, the destination and the untouched symlink.
  - D13 is resolved, with the merge dependency.
  - Also updated: *Risk Level* (accepted), the Overview progress, the use-case
    acceptance, *Assumptions*, *Ambiguities*, *Inputs*, *Outputs*, two new
    stop rows (the tag or release step fails; the pipx upgrade fails),
    *Out of scope*, *Deliverables*, Phases 1, 7 and 9, *Setup questions*
    (both RESOLVED, with the answers recorded), *Also settled* (accepted) and
    the success criteria.
- **Test matrix:** risk accepted; C13 and C15 made concrete; the D2 and D13
  crosswalk rows updated; the host-integration row names the destination.
- **This log:** the progress line, the risk line, the Phase 1, 7 and 9 notes,
  *Decisions / issues*, and the questions summary.
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

Verification after finalization:
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
- Frozen packet: base `be7f80965dee0e17bf41f8018699391f751dde5c` (the claim
  checkpoint, `pypi-publish-2-1-0(claim): activate the tracker row`). The
  review commit is the Step 0 review-ready checkpoint commit that introduces
  this entry. Its SHA is returned in the hand-off and recorded here when the
  packet is frozen, because a commit cannot carry its own SHA.
- Tracker: `milestone-plan.md` in the docs root; owning project `docs`; project
  path empty (a dedicated docs root); artifact stem `pypi-publish-2-1-0`;
  active semantic slug `pypi-publish-2-1-0`; row
  `200 | pypi-publish-2-1-0 | active | lifecycle-and-free-form-relate`; claim
  checkpoint `be7f809`; semantic branch root `pypi-publish-2-1-0/`.
- Claude slot: `pending`.
- GPT slot: `pending`.
- Findings: none recorded yet.
- Taste triage: pending.
- Re-review: pending — decided after the provider outcomes.
- final-sync: `pending`.

## Phase 1 — Define Contract

_Not started._

## Milestone completion summary

_Not complete._
