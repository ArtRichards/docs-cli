# M31 — Publish docs-cli 2.1.0 to PyPI

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-10-29

Related:
- child-of: milestone-plan.md
- implements: charter.md
- pairs-with: pypi-publish-2-1-0-impl.md
- pairs-with: pypi-publish-2-1-0-test-matrix.md
- pairs-with: release-runbook.md
- pairs-with: status.md
- references: feedback-log.md
- follows: archive/2026-10-28/lifecycle-and-free-form-relate.md
- depends-on: archive/2026-10-28/lifecycle-and-free-form-relate.md

> **Registered 2026-10-28** (`193fc71`) and claimed `active` the same day
> (`be7f809`), straight after M30 merged to `main` (`bf09748`). The operative
> checklist is [release-runbook.md](release-runbook.md). This document maps it
> onto ship-milestone's steps and records the decisions setup froze. The
> per-phase record lives in
> [pypi-publish-2-1-0-impl.md](pypi-publish-2-1-0-impl.md).

## Overview

- Milestone: M31. It is the second milestone under the canonical tracker,
  and the first publish mapped onto ship-milestone's step and phase
  structure; M13 ran under `/ship-milestone` too, but walked the runbook
  directly.
- Slug: `pypi-publish-2-1-0` — tracker identity and branch root
  (`pypi-publish-2-1-0/milestone-setup`, `…/phases-1-4`, `…/phases-5-10`,
  `…/simplify`)
- Title: Publish docs-cli 2.1.0 to PyPI
- Surface: M30 published as `docs-cli==2.1.0` by the runbook (D1), then the
  host refresh (D10) and the suite hand-off (D12). No product code changes.
- Test Matrix:
  [pypi-publish-2-1-0-test-matrix.md](pypi-publish-2-1-0-test-matrix.md)
- Implementation log:
  [pypi-publish-2-1-0-impl.md](pypi-publish-2-1-0-impl.md)
- Progress: **Step 2 is complete (2026-10-29): `docs-cli==2.1.0` is on
  PyPI, tagged `v2.1.0` and released, and this host runs it.** Step 3
  (2026-10-29) ran `/simplify` (three behaviour-preserving readiness
  simplifications; the probe unchanged) and the explicit-scope archive
  closeout whose frozen values the log's *Step 3 — Simplify and closeout*
  names. The log's *Milestone completion summary* carries the record, and
  its *Step 2 review-pass-001* is closed with `final-sync` `ready`.
  - Step 1 (Phases 1–4) is complete (2026-10-28), its review pass closed with
    `final-sync` `ready`; Step 0 likewise.

### Identity note

`M31` is a prose label that continues the M1–M30 history. The tracker identity
is the semantic slug. The row sits at order 200 and depends on
`lifecycle-and-free-form-relate` (order 100, `complete`, archived under
`archive/2026-10-28/`).

The tracker contract therefore requires two recognized pairs with that
archived document, `precedes` / `follows` and `depends-on` / `required-by`.
Setup wrote both with `docs relate add … --reason`. That command appends an
audited `Revision:` bullet to the archived endpoint and leaves its lifecycle,
`Archived:` and prose unchanged (M25 — D4).

### Goal

`pip install -U docs-cli` delivers 2.1.0, byte for byte the wheel this
milestone built, smoke-tested and rehearsed. With that release:
- an agent on any host can promote a document with `docs lifecycle` and link
  it with free-form `docs relate`;
- the Agent Playbook Suite can pin a published release that retires its
  verbless-metadata stopgap.

### Primary use-case acceptance

Against the **PyPI-served** wheel, installed fresh with no repository on the
path:
- **M30's primary use case runs.** A milestone trio is scaffolded with
  `docs new`, linked with `docs relate add … pairs-with …`, and promoted with
  one `docs lifecycle … active`. It needs zero hand-edits, and `docs check`
  passes. The probe's contract group (D5) exercises it.
- **The suite's guard flips.** The Agent Playbook Suite's CI capability probes,
  run verbatim, read `lifecycle verb: True` and `free-form relate: True`. This
  is M30 hand-off item 2.
- **A 2.0.0 install learns about 2.1.0.** M21's update notice names
  `2.0.0 -> 2.1.0` once on stderr and leaves the exit code unchanged.
- **This host follows the release** (D10).

## Risk Level

**Standard.** Proposed at setup and accepted by the conductor's triage on
2026-10-28. It was not raised as an operator question, because the evidence
does not support High.

**Why Standard.** The milestone ships M30 and adds no product code. M30 was
built, reviewed and accepted at an operator-confirmed Standard level:
dual-provider reviews at Steps 0–2, 1671 tests GREEN, and a 47/47 mutation
smoke.

**The milestone's own risk is release integrity.** The PyPI upload is
irreversible: the index is append-only, a file can be yanked but never
replaced, and the version number is burned. Process gates control that risk,
and here they are cheaper and stronger than High's defaults:
- the TestPyPI rehearsal and `twine check`;
- the chain-of-custody rule (D4);
- the stop conditions (*Contract* › *Error cases*);
- Step 1's dual-provider review, before anything irreversible (D2).

**High-list triggers considered:**
- *Public APIs:* the CLI surface was judged additive at Standard in M30, and
  this milestone cannot change it.
- *Data integrity:* no user data is written.
- *Security:* the uploads use entire-account tokens. D6 contains that:
  - shape-only credential checks;
  - `--non-interactive` uploads that name their files explicitly;
  - single-index installs;
  - a token search of every staged diff.

High's distinctive gates do not fit a publish: there is no product behaviour
to mutation-test or benchmark. Its post-Phase-4 pause would also contradict
the operator's automatic-upload decision (D2).

**Selected gates (Standard):**
- **Lite:**
  - the contract;
  - an explicit check for every artifact this milestone changes or ships
    (D5);
  - `ruff check`, `ruff format --check` and `mypy src/ tests/`;
  - `docs check .`;
  - the live-INDEX snapshot and the reference byte identity.
- **Coverage report:** not configured in this project, so not applicable.
- **Hidden/generalization smoke:** selected, as its publish analogue. The same
  distribution probe runs against three wheel installs, plus a 2.0.0 control.
- **Property/stateful smoke:** selected. It covers the idempotent re-runs and
  the sha-equality chain (D4).
- **Mock audit:** selected. There are no mocks.
- **Reviewer signoff:** the Step 1 and Step 2 dual-provider reviews.

## Binding decisions (setup)

Each binding decision's operative wording lives **only** here, under its
D-id. Every other section refers to it by id and keeps only phase-specific
commands, evidence or verification duties. This follows the feedback log's
candidate convention, adopted here as a trial. The setup-question packets
stay below as the audit trail.

Sources:
- **Operator decisions of 2026-10-28:** D2, D3, the credential facts in D6,
  D10 (from Q2) and D13 (from Q1).
- **Everything else** comes from the runbook, the tracker contract,
  `CLAUDE.md`, operator policy and precedent.

### D1 — What ships, and what this milestone may change

**What ships.** Exactly M30, merged as `bf09748`:
- `docs lifecycle`;
- one-sided free-form `docs relate`;
- the config-aware `parse()`;
- `docs stamp`'s config refusal.

This is the one-to-one shape of M10 → M11, M12 → M13 and M19 → M20. M29, by
contrast, batched the v2.0 train. 2.1.0 is a SemVer minor, because M30 is
additive (M30 — D9). M30 Phase 7 already made the bump: `pyproject.toml`
reads 2.1.0, and the A3/B1/B2/C2 pins in `tests/test_packaging.py` match.

**What this milestone may change.** Its source-tree edits are limited to:
- the CHANGELOG (D7);
- the README (D8);
- two new scripts under `tests/manual/` (D5);
- the generated INDEX snapshot `tests/fixtures/expected/docs-INDEX.md`,
  refreshed in lockstep whenever `docs/INDEX.md` changes;
- documents under `docs/`.

Nothing under `src/` and no product test changes.

### D2 — Release authorization (operator, 2026-10-28, in this session)

This is the equivalent of M29's D2: **release automatically.** Once the Step 1
review pass is closed and the TestPyPI rehearsal is recorded GO, Step 2 goes
ahead without a further operator go. It runs three actions:
- the PyPI upload of the two canonical 2.1.0 artifacts (Phase 6);
- the `v2.1.0` tag push (D13; Phase 7);
- the GitHub release (D13; Phase 7).

The tag push and the release were added by the operator's answer to Q1.

**When the authorization holds.** Only while every precondition in
*Contract* › *Error cases* is true at the moment of each action. If one
fails, the authorization is void: nothing further is published, and the
milestone stops for the operator.

**A recorded exception.** ship-milestone pushes only milestone branches, and
only through sync-and-commit. The `v2.1.0` tag push is the single push outside
that rule. This milestone never pushes `main`.

**After the upload, a Step 2 review blocker is triaged by what it hits:**
- A finding against the shipped bytes goes to the operator, who decides
  between a yank and a patch milestone.
- A finding against documents is fixed normally.

### D3 — The runbook runs through ship-milestone (operator, 2026-10-28)

M9–M29 walked [release-runbook.md](release-runbook.md) directly, with no TDD
phases. The operator chose to run this publish through ship-milestone. The
accepted mapping is:
- **Step 1, Phases 1–4:** everything before the irreversible upload, reviewed
  by both providers.
- **Step 2, Phases 5–10:** the upload, served verification, tag and release,
  host work, and lessons.
- **Step 3:** simplify, then the explicit-scope archive.

*TDD implementation plan* has the details. Phase 2's "tests" are release
checks (D5).

Phase 4's baseline is a pre-publish **GREEN** baseline: a publish ships no
new behaviour, so the quality model's GREEN-baseline allowance applies. The
RED evidence comes from Phase 2's controls instead.

### D4 — Builds and chain of custody

**Building:**
- Every build starts from an empty `dist/` (`rm -rf dist/`).
- Every build runs on a clean tree. The one exception is a rehearsal build:
  its only diff is the temporary name and version edit in `pyproject.toml`
  (D9).
- Every build records its build-backend version and the sha256 of each
  artifact.

**Uploading:**
- Every `twine upload` names its two files explicitly, never a glob.
- Before each upload, `dist/` must hold exactly those two files.

**The release inputs.** These are the files whose change alters the shipped
artifacts: `src/`, `pyproject.toml`, `README.md`, `LICENSE` and `.gitignore`.

**The wheel is the anchor.** Four wheels must share one sha256:
- (a) Phase 4's canonical build;
- (b) the post-rehearsal canonical rebuild;
- (c) the Step 2 tag-target build;
- (d) the PyPI-served wheel.

If (b) or (c) differs from (a), stop. The one automatic remedy is to rebuild
with the build backend pinned to (a)'s version. It counts only if it
reproduces sha (a).

**The rehearsal wheel is checked byte for byte too**, not only by behaviour:
- the TestPyPI-served rehearsal wheel equals the uploaded rehearsal build by
  sha;
- its `docs_cli/` payload is byte-identical to (a)'s.

Only the dist-info may differ, by name, and by version under D9.

**The sdist.** It moves between builds by design, because it captures `docs/`
(M13, M20, M29):
- It is anchored at (c) and must be bit-perfect against the PyPI-served
  sdist.
- Its members outside `docs/` and `tests/` must match (a)'s sdist. Phase 4
  records (a)'s per-member sha256 manifest in the implementation log for that
  comparison.

Both served artifacts are also checked against PyPI's per-version JSON
digests.

### D5 — The release checks

There are two stdlib-only scripts under `tests/manual/`, outside pytest's
discovery; `tests/manual/m7_success_criteria.py` is the precedent. Each exits
0 on PASS and 1 on FAIL, prints one line per check, and records its git blob
sha with every run.

**`release_readiness.py`** checks the source tree:
- the `pyproject.toml` version;
- the CHANGELOG release section (D7);
- the README (D8):
  - every `docs --help` verb is listed;
  - each verb's synopsis matches its `--help` usage, at least for `touch`,
    `stamp`, `project set`, `lifecycle` and `relate`;
  - no "Claude Code";
  - every `blob/main/` link resolves;
- the bundled references are byte-identical to `docs/`.

**`release_probe.py`** checks one `docs` executable, in two groups:
- **The contract group** is valid for any executable:
  - M30's headline contracts;
  - both Agent Playbook Suite probes, exactly as the suite's CI runs them;
  - M29's nine 2.0 contracts, as regression.
- **The distribution group** is valid only for a wheel install:
  - `docs --version`, skipped under the rehearsal name (the M13 caveat);
  - `install-skill` byte identity;
  - the no-op re-run;
  - the `--symlink` refusal. That refusal is wheel-only; an editable install
    may symlink (`cli.md`, *install-skill*).

**Where each group runs:**
- Every wheel install runs both groups identically: (a), the TestPyPI-served
  wheel and the PyPI-served wheel.
- The editable build runs the contract group only, as Phase 2's sanity run.

**Expected values** come from `cli.md`, the CHANGELOG's 2.1.0 section, M30's
binding decisions and M29's contracts — never from a build's output. Existing
product tests are reused unchanged.

### D6 — Isolation and secrets

**Throwaway runs.** Every smoke, probe, rehearsal install and download runs in
a throwaway venv and in throwaway trees outside the repository. The
environment is:
- `XDG_STATE_HOME` and `XDG_CACHE_HOME` set to scratch;
- `DOCS_CLI_NO_UPDATE_CHECK=1`, except where the notice is under test, which
  still uses a scratch cache.

The reason is that `docs install-skill` records its destination on every
success (E10). Only Phase 9 writes host state (D10).

**Index installs** name exactly one index and pass `--no-deps`:
- The rehearsal installs with
  `--index-url https://test.pypi.org/simple/ --no-deps`, never with an extra
  PyPI index. A `docs-cli-rehearsal` claimed on PyPI would otherwise run on
  this token-bearing host.
- Downloads land in fresh empty directories, and nothing is executed from
  inside them.

**Credentials.** The operator copied `~/.pypirc` today from the operator's
other host. It is mode `600` and has three sections, `[distutils]`, `[pypi]`
and `[testpypi]`. Both index sections use `username = __token__` and
`pypi-`-prefixed passwords. Only twine reads the file:
- checks report its shape, never a value;
- every `twine upload` runs with `--non-interactive`;
- before every commit, the staged diff is searched for token-shaped strings,
  and the search must find none.

### D7 — CHANGELOG dating

The heading becomes `## 2.1.0 — <YYYY-MM-DD>`, using the local calendar date of
the PyPI upload. The sentence "A separate publish milestone ships it." is
removed. Nothing else in the section changes. The readiness check diffs the
section against M30's text at `bf09748`.

Phase 3 dates the heading with the expected day. If the day has rolled by
Phase 5, a one-line commit re-dates it before build (c). CHANGELOG ships in
neither artifact (M13, M20), so re-dating moves no sha.

### D8 — README

The README is the PyPI long description (M29 lesson). Phase 3 corrects the
synopses that readiness finds lagging the CLI (*Acceptance examples* ›
*Readiness*), and changes nothing else unless readiness finds drift. The
`blob/main/` links are re-verified after the Step 3 archive.

### D9 — Re-rehearsal and re-runs

**A release-input change.** Any change to a release input (D4) after the
rehearsal invalidates Phase 4's build, smoke, probe and rehearsal. That
includes a change made by a Step 1 review fix. All four are re-run before Step
1 closes, and the re-run's canonical build becomes (a).

**The rehearsal version.** TestPyPI refuses to reuse a version, so a
re-rehearsal uploads `docs-cli-rehearsal` as `2.1.0.post1`, then `.post2`, and
so on. This rehearsal-only version is part of the temporary `pyproject.toml`
edit and is reverted with it. Canonical `2.1.0` never changes.

**A release-check script change.** If either D5 script changes after its
Phase 4 run, it is re-run before Step 1 closes against two targets:
- wheel (a);
- a fresh install of the already-served rehearsal.

*2026-10-28 (Step 2, OQ-S2-1): the G2 calibration changed the probe after
Step 1 closed; the same re-run ran in Step 2's Phase 5, before build (c).*

**A rehearsal failure is a stop**, not a re-run. The runbook's remedy, a
version bump, would change what this milestone ships.

**Documents.** Changes confined to `docs/` invalidate nothing.

### D10 — Host work (operator, 2026-10-28: Q2 → refresh and upgrade)

**The decision.** After served verification and the release (D13), Phase 9
does three things, in order:
1. **Upgrade the binary.** The host's pipx `docs-cli` is upgraded to 2.1.0
   from PyPI.
2. **Refresh the skill.** The host `docs` skill is refreshed with that
   published binary, at `~/.claude/skills/docs`. That directory becomes the
   recorded destination. No destination was recorded before (E9).
3. **Sweep the workflow skills.** The sweep is a read-only census of the
   installed Agent Playbook Suite and its source repository. Its findings go
   to the hand-off (D12).

**Left alone:**
- the backup symlink `~/.claude/skills/docs-local-source-backup-20260525-134621`;
- the suite repository and the plugin cache, which ride their own release
  cycle.

**Host state written.** After the update-notice step, every host-binary run
sets `DOCS_CLI_NO_UPDATE_CHECK=1`. So the only host state this milestone
writes is:
- the pipx venv;
- `~/.claude/skills/docs`;
- the recorded-destination file.

No step guesses the agent. Nothing inspects or judges an installed skill
beyond verifying the copy just installed.

### D11 — Closeout follows the canonical tracker

Step 3 archives the three artifacts together with
`docs archive pypi-publish-2-1-0.md --cascade-only 'pypi-publish-2-1-0-*'`.
The implementation log does **not** stay at the root, as M17's, M20's, M24's
and M29's did; the 2026-10-26 migration archived those four logs.

Anything that must outlive the archive lives in a live document:
- the hand-off, in [feedback-log.md](feedback-log.md);
- the narrative, in [status.md](status.md);
- the procedure, in [release-runbook.md](release-runbook.md).

### D12 — The suite hand-off stays open

M30's hand-off is the 2026-10-26 entry in [feedback-log.md](feedback-log.md).
It splits in two:
- **Items 1–3 close here, with evidence:** the publish, the served-wheel probe
  replay, and the host refresh.
- **The suite pin-bump PR items stay open** until that suite release ships.

The PR also needs two facts from E11:
- the stopgap is on an unmerged suite branch;
- the suite re-vendors `skills/docs` in the same change as its pin bump.

### D13 — Tag and GitHub release (operator, 2026-10-28: Q1 → A)

**When.** In Phase 7, only after the PyPI-served wheel has passed served
verification:
- the sha comparison;
- `release_probe.py` with both groups;
- the suite's capability probes.

A failure in any of them stops the milestone before anything public beyond
the upload.

**What.**
1. Annotate `v2.1.0` at the tag-target commit: the exact commit build (c)
   came from, on `pypi-publish-2-1-0/phases-5-10`.
2. Push the tag.
3. Check that `git ls-remote origin 'refs/tags/v2.1.0^{}'` equals that
   commit. The peeled object matters: the plain tag ref returns the annotated
   tag object, not the commit. For `v2.0.0` those are `af3bdb5` and
   `408ef6c`.
4. Run `gh release create v2.1.0 --verify-tag --title "docs-cli 2.1.0"`, with
   the dated `## 2.1.0` CHANGELOG section as its notes.

**A recorded dependency: the merge.** Merging the stack into `main` happens
outside ship-milestone, at the operator's direction. M30's stack, for
example, was merged by the conductor as `bf09748` on the operator's
instruction.

The merge must be a history-preserving merge commit. A squash or rebase
would leave the tagged commit off `main`. It should also follow promptly: the
PyPI page's README links `blob/main/CHANGELOG.md`, which reads `UNRELEASED`
until the stack reaches `main`. The milestone's final report says so
explicitly: *merge promptly, with a merge commit, not squash or rebase — the
PyPI page links `main`'s CHANGELOG; `v2.1.0` is at `<sha>`*.

## Contract

Phase 1 froze the exact check lists, command lines and scratch layout as
*Decisions (Phase 1 — BINDING)* in this document, as M25–M30 did.

### Facts

The evidence lives in the implementation log's setup record:
- **E1** — PyPI's latest is 2.0.0, and the 2.1.0 slot is free.
- **E2** — the TestPyPI squatter is unchanged, and `docs-cli-rehearsal`'s
  2.1.0 slot is free.
- **E3** — the credentials are present and well formed, and `gh` has `repo`
  scope.
- **E4** — the toolchain:
  - `twine` is 7.0.0;
  - `hatchling` is unpinned, and 1.33.0 was published today.
- **E5** — the gate is GREEN at 1671.
- **E6** — the version is already 2.1.0, and one CHANGELOG sentence must go.
- **E7** — the README covers 13 of 13 verbs, but synopses lag the CLI. The
  log's Phase 1 section corrects setup's count.
- **E8** — `main` already carries M30, and there is no `v2.1.0` tag or
  release yet.
- **E9** — the host:
  - the binary is pipx 2.0.0;
  - there is no recorded destination;
  - the backup symlink exists.
- **E10** — `install-skill` records its destination on every success.
- **E11** — the suite:
  - its probes match M30's replicas;
  - its pin is 2.0.0;
  - the stopgap is unmerged;
  - the installed 0.8.3 still prescribes hand-edits.
- **E12** — the open feedback-log items ship unchanged, and none blocks the
  release.
- **E13** — there is no open GitHub issue to answer.

The served 2.0.0 wheel's metadata is the reference for the dependency oracle
under *Non-functional constraints*:
- `Requires-Python: >=3.11`;
- `Provides-Extra: dev`;
- five `Requires-Dist: …; extra == 'dev'` lines.

### Assumptions

- **The copied PyPI token is valid.** Owner: Phase 6. It is validated by use
  (M11): a 401 or 403 stops under *Error cases*' PyPI-upload row.
- **Build (c) reproduces wheel (a)**, or can be pinned to (D4). Owner:
  Phase 5.
- **The suite's probes are as measured** (E11). Owner: Phase 7, against the
  served wheel.
- **The stack is merged with a merge commit** (D13). Owner: the operator's
  merge instruction.

### Ambiguities

**Resolved by the operator:** Q1 (→ D2, D13) and Q2 (→ D10).

**Phase-1 freeze items — frozen** in *Decisions (Phase 1 — BINDING)*, none
needing the operator:
- each script's exact checks and expected values (P1.1, P1.2);
- the scratch layout (P1.3);
- the exact command lines (P1.4, P1.5);
- the sdist download method, the backend-pin mechanism (D4) and the runbook
  correction list for Phase 10 (P1.6).

**Also settled by Phase 1** (P1.6): whether the runbook's twine upgrade step
runs; how the 2.0.0 control classifies `install-skill` byte identity; and
where M29's tree-dependent expected values come from — committed fixture
trees copied to scratch, quoting the product tests that pin them, rather
than a count re-derived on this docs tree.

### Inputs

- The repository at the Step 1 base: M30 merged, plus the tracker
  registration and the claim.
- `~/.pypirc` (D6).
- PyPI and TestPyPI.
- `gh`, authenticated as `ArtRichards`.
- This host's pipx install and `~/.claude/skills/`. Only Phase 9 touches them
  (D10).

### Outputs

- The two 2.1.0 artifacts on PyPI, with their sha256 values recorded (D4).
- The `v2.1.0` tag and the GitHub release (D13).
- Edits allowed by D1.
- The runbook's *From M31* lessons and corrections, and the feedback-log
  hand-off (D11, D12).
- The host binary and skill (D10).

### Invariants

**Must always:**
- build per D4;
- run the same distribution probe against every wheel install (D5);
- verify state before and after each irreversible action.

**Must never:**
- change anything D1 excludes;
- upload anything D4 does not admit;
- reuse a version on either index;
- print, log or commit a credential (D6);
- write host state that D10 does not list;
- edit the suite or the plugin cache;
- edit an archived document, except through `docs relate --reason`'s audited
  path;
- hand-edit a metadata block. `docs lifecycle` and `docs relate` cover every
  edit the workflow prescribes.

### Error cases

These are the stop conditions. Each one voids D2 until the operator decides.

| Condition | Expected behaviour | Observability |
|---|---|---|
| The 2.1.0 slot is taken on PyPI at Phase 5, or at the re-check just before the Phase 6 upload | Stop; nothing uploaded | The per-version JSON returns 200 |
| The Step 1 review pass is not closed, or a blocker is undispositioned | Step 2 does not start | The review ledger |
| The rehearsal is not GO, or failed (D9) | Stop; Step 1 does not close. On TestPyPI only (OQ-2), in this order: any 4xx rejection, any sha or payload mismatch, or any probe FAIL is a failure and stops, whichever file it hits; a connection error, timeout or 5xx with no file accepted gets one retry of the same command; with one file accepted and the other failed transiently, the missing file is re-sent once by name; a version not yet on the simple index is polled (at most 10 × 30 s) | Implementation log, Phase 4; twine's output; the per-version JSON |
| The served rehearsal wheel ≠ the uploaded rehearsal build, or its payload ≠ (a)'s (D4) | Stop; Step 1 does not close | The rehearsal sha and payload comparison |
| A release input changed after the rehearsal, or a D5 script changed after its Phase 4 run, with no re-run (D9) | Stop; nothing uploaded | `git diff --quiet "$X"..HEAD -- src pyproject.toml README.md LICENSE .gitignore`; each script's `git hash-object` against its blob in *Release anchors (current)* |
| `twine check` fails | Stop before upload | twine's output |
| Wheel (b) or (c) ≠ (a) and the backend pin does not cure it, or an sdist member outside `docs/`/`tests/` differs from (a)'s recorded manifest (D4) | Stop; nothing uploaded | The sha table; the member manifest |
| `dist/` does not hold exactly the two canonical files with build (c)'s shas (D4) | Stop; nothing uploaded | `ls dist/`; `sha256sum` |
| The tree is dirty at a build, beyond D4's rehearsal exception | Stop | `git status --porcelain` |
| `~/.pypirc` is missing, or its shape changed | Stop | P1.5's shape command (D6) |
| The remote or `gh` is unusable at Phase 5: `git ls-remote origin refs/heads/main` or `gh auth status` exits non-zero | Stop; nothing uploaded. Stderr noise from a command that exits 0 is not a failure | Both commands' exit status |
| A P1.5 Phase 5–7 command's result differs from the expectation P1.5 states for it — readiness failing on anything but D7's date, `pytest` other than 1671 passed (*amended 2026-10-28, Step 2, OQ-S2-2:* when the sole non-pass is `tests/test_packaging.py::test_d4_install_skill_is_idempotent` crashing with a negative return code, one full re-run is allowed; it must report 1671 passed, both runs are recorded, and anything else stops), the 404 probe answering 200, the guard step's sha differing from the anchor, empty release notes, or a toolchain difference beyond a patch level. This row never governs the upload's own outcome: from `twine upload` until the per-version JSON lists both files, only the PyPI-upload row below decides | Stop; nothing further is published | The command's output, recorded in the log |
| The PyPI upload (Phase 6) does not end with twine exit 0 and both files in the per-version JSON | First poll the per-version JSON (at most 10 × 30 s) and record exactly which files PyPI publishes. Then the first case that applies decides: (1) any hard refusal — a 4xx, including a 400 metadata error, 401/403 authentication, and 409 or a reused filename — stops, with the publication recorded as it stands (none, or one file); (2) one file confirmed published and the other failed transiently (connection error, timeout, 5xx) gets one re-send of the missing file by explicit name — if the re-send exits 0 and the JSON then lists both files, the upload has succeeded; otherwise stop; (3) any other error, including a transient fault with no file confirmed published, stops for the operator with no automatic retry; (4) anything else — publication still uncertain after polling, or twine exiting 0 while the JSON lists fewer than both files — stops. A published file is never re-sent, and "nothing uploaded" is recorded only when the poll lists no file | twine's exit and message; the per-version JSON file list |
| A served sha ≠ the local sha | Stop before the tag; the operator decides (yank or not) | The chain-of-custody table |
| The served-wheel probe or the suite capability probes fail | Stop before the tag and release; the operator decides (yank, or a patch milestone). The suite probes pass only when the extracted guard step (P1.5) exits 0 and prints `lifecycle verb: True, free-form relate: True`; the CI step's exit inside the suite checkout is not the criterion | The probe output; the guard step's output |
| A run changed host state D10 does not authorize: the recorded-destination file differs from what the last authorized step left (absent until Phase 9's skill step, then naming `~/.claude/skills/docs`), or the update cache's sha moved across that run (P1.3's host check) | Stop; the operator decides | The host before/after check (P1.3) |
| The peeled remote tag ≠ the build commit, or `gh release create` fails | Stop; record; the PyPI release stands | `git ls-remote`; gh's exit |
| `pipx upgrade` fails, or the host binary does not report `docs 2.1.0` | Stop the host step before the skill refresh | pipx's output; `docs --version` |
| `install-skill --force` at the host destination fails | Stop the host step; the release stands | The command's exit and stderr |

### Non-functional constraints

- **Performance:** no budget. Elapsed times are recorded.
- **Security and privacy:** D6.
- **Compatibility:**
  - 2.1.0 is additive (M30 — D9). No tree that 2.0.0's `docs check` passes
    fails any verb (M30 — D10).
  - **The dependency oracle:** the wheel declares no runtime dependency.
    Every `Requires-Dist` carries an `extra ==` marker, and the metadata
    declares `Provides-Extra: dev` and `Requires-Python: >=3.11` — as the
    served 2.0.0 metadata does.
- **Reliability:** every irreversible step is verified after the fact. The
  aggregate JSON can lag 60–120 s (M11, M20); the simple index and the
  per-version endpoint are authoritative.

### Acceptance examples

- **The local wheel.** Given wheel (a) in a fresh venv with scratch XDG
  directories, both probe groups pass, and the host's recorded-destination
  file stays absent.
- **The 2.0.0 control.** Given the host's 2.0.0 binary, every 2.1-only check
  fails, and every 2.0 regression check passes.
- **Readiness.** Given the tree at the Step 1 base, readiness fails for
  exactly six reasons:
  - the `UNRELEASED` heading;
  - the publish-state sentence;
  - the `touch`, `stamp`, `project rename` and `project set` synopses.

  After Phase 3, it passes. The trio and `status.md` point here rather than
  restating the reasons; the log records measured results.
- **The rehearsal.** Given the TestPyPI-served rehearsal wheel:
  - its sha equals the uploaded rehearsal build;
  - its `docs_cli/` payload equals (a)'s;
  - both probe groups pass, with the version check skipped.
- **Upload eligibility.** Given build (c), its wheel sha equals (a), or
  nothing is uploaded.
- **The served wheel.** Given `docs-cli==2.1.0` from PyPI, these hold
  **before** the tag exists:
  - the sha matches;
  - `docs --version` prints `docs 2.1.0`;
  - both probe groups pass;
  - the suite's guard reads True / True.
- **The update notice.** Given a 2.0.0 binary with a scratch cache, run after
  the publish, it prints
  `docs: update available 2.0.0 -> 2.1.0 — run: pip install -U docs-cli`
  once on stderr, and its exit code is unchanged.

### Taste anchors

**Reference material to read like:**
- M29's [task plan](archive/2026-08-16/m29-pypi-publish-2-0-0.md) and
  [log](archive/2026-10-26/m29-pypi-publish-2-0-0-impl.md): the phase
  narrative, sha tables and lessons voice.
- The runbook's *Cumulative lessons*, appended to and never rewritten.
- M30's [trio](archive/2026-10-28/lifecycle-and-free-form-relate.md): the
  ledgers and the matrix shape.
- For the scripts: `tests/manual/m7_success_criteria.py`, and the exact probe
  code of the two suite-probe replica tests.

**In-project resources to reuse:**
- the standard library only;
- committed fixture trees, and throwaway copies of this docs tree, rather
  than new committed fixtures;
- the runbook's commands, verbatim where they are still right.

**Established patterns:**
- the runbook's walked checklist and sha tables;
- shape-only credential checks;
- `docs touch` after body edits, and `docs lifecycle` / `docs relate` for
  every metadata edit;
- behaviour-first check names, with no milestone or decision ids;
- **each binding decision's operative wording only in its D-id**, which is
  the trial convention.

**Expected diff footprint:**
- `src/`: 0 lines;
- `CHANGELOG.md`: about 2 lines;
- `README.md`: about 4–8 lines;
- `tests/manual/`: two scripts, roughly 300–500 lines;
- docs: this trio, about 50–100 lines of runbook lessons and corrections,
  about 15–30 lines of hand-off update, a status paragraph, and the INDEX
  plus its snapshot.

Any `src/` diff triggers a scope review.

**Dependency policy:** no runtime or development dependency changes. The
`twine>=7.0.0` floor is already in `[dev]`. No backend pin goes into
`pyproject.toml`.

### Forbidden shortcuts

- Do not take an expected value from a build's own output, and do not compare
  an artifact against itself (D5).
- Do not skip the rehearsal, or the served-wheel probe, because "the code did
  not change". The bytes and the index are what is under test.
- Do not upload with a glob or with `--skip-existing` (D4).
- Do not run anything against the host's real XDG state outside Phase 9 (D6,
  D10).
- Do not weaken or delete a valid check to reach GREEN. Correct erroneous
  expectations under *Check calibration*, and log them.
- Do not re-date, rename or re-version anything to get past a stop condition.

### Test hooks

- **Visible tests:** none in default discovery. The 1671-test suite is
  regression evidence, including:
  - the 2.1.0 pins in `tests/test_packaging.py`;
  - `tests/test_cli_lifecycle.py::test_help_verb_list_names_lifecycle_for_the_playbook_guard`;
  - `tests/test_cli_relate.py::test_playbook_guard_free_form_dry_run_probe_exits_0`.
- **Explicit non-product checks:**
  - the D5 scripts;
  - `twine check`;
  - the D4 comparisons;
  - the D9 diff;
  - the D6 token search;
  - `docs check .`, the INDEX snapshot and the reference byte identity.
- **Hidden/generalization, property, mutation, fuzz and schema:** see *Test
  Strategy*.

## Out of scope

- **Changes D1 excludes,** including fixes for the open feedback-log items
  (E12), which ship as they stand.
- **The Agent Playbook Suite pin-bump PR,** and any suite or plugin-cache edit
  (D10, D12).
- **Merging the stack into `main`** (D13).
- **Re-scoping the PyPI and TestPyPI tokens.** That is operator UI work and
  rolls forward.
- **Trusted Publishing,** or a CI release workflow.
- **Pinning `hatchling` in `[build-system]`** (see *Follow-ups*).
- **The surviving "Claude Code" wording** in a `pyproject.toml` comment and in
  `charter.md`. Neither is a shipped surface, and the README and `src/` carry
  none (E7).
- **Other host skills** (D10).
- **An in-repo drift lint for workflow-skill prescriptions** (see
  *Follow-ups*).

## Current state and evidence

The setup record in the [implementation log](pypi-publish-2-1-0-impl.md) has
E1–E13, every one measured read-only. A throwaway-tree rehearsal of the
archived-endpoint `docs relate` pairs was also run.

Three findings change the runbook's default path:
- **E4 → D4.** The backend is unpinned, and a new version was published today.
- **E9 → D10.** No destination is recorded on this host.
- **E10 → D6.** Every `install-skill` run records its destination.

## Test Strategy For This Milestone

### Visible tests

No product test is added or changed (D1). The full suite must report
**1671 passed** at three points: the Phase 4 baseline, the tag-target commit,
and closeout.

### Non-product checks

- **`release_readiness.py`:**
  - RED in Phase 2, for the reasons in *Acceptance examples*;
  - GREEN from Phase 3 on;
  - re-run at the tag-target commit.
- **`release_probe.py`** (D5):
  - the contract group, against the editable build, in Phase 2;
  - both groups, against the 2.0.0 control, in Phase 2;
  - both groups, against wheel (a) in Phase 4, the TestPyPI-served wheel in
    Phase 4, and the PyPI-served wheel in Phase 7.
- **`twine check`** on every build.
- **The D4 comparisons:**
  - the wheel shas;
  - the rehearsal sha and payload;
  - the sdist member manifest;
  - the per-version JSON digests;
  - `dist/` holding exactly two files.
- **The D9 diff**, and the D6 token search.
- **`docs check .`**, the INDEX snapshot and the reference byte identity.

### Hidden/generalization categories

The repository is fully visible, so there are no private cases. The
generalization targets are:
- index-served artifacts, rather than local builds;
- the rehearsal-name build (`0.0.0+local`, M13; no update notice, M24);
- an editable build, against wheel installs;
- a fresh venv per run;
- probe trees outside the repository, including a throwaway copy of this
  docs tree;
- extension-vocabulary trees, and a tree with a non-default `date_format`;
- a real 2.0.0 install;
- the host's pipx install.

### Property/stateful invariants

- **Idempotence:**
  - an `install-skill` re-run is a no-op at exit 0;
  - a `docs lifecycle` re-run writes zero bytes.
- **The sha chain:** (a) = (b) = (c) = served (D4).
- **One result set:** the distribution probe gives identical results on the
  three wheel installs, apart from the rehearsal's version line.

### Mutation-sensitive logic

Mutation tooling is not configured. Phase 2 runs a hand-applied smoke, as
M28a and M30 did, over these mutants:
1. a CHANGELOG copy still headed `UNRELEASED`;
2. a dated heading that keeps the publish-state sentence;
3. a 2.1.0 section with one other line edited;
4. a README missing one verb;
5. a README with one lagging synopsis;
6. a bundled reference one byte off its `docs/` spec;
7. the host's 2.0.0 binary, which must fail every 2.1-only check;
8. the sha comparator, fed the rehearsal wheel against (a).

### Fuzz targets

Not applicable. There is no new parsing surface.

### Benchmark/security/schema checks

- **Schema:**
  - `twine check`;
  - `Metadata-Version` recorded;
  - the dependency oracle (*Non-functional constraints*);
  - no CHANGELOG in either artifact;
  - the seven skill files in the wheel.
- **Security:** D6, and the served-versus-local sha comparison as a tamper
  check.
- **Benchmark:** not applicable.

### Mock policy

- New or expanded mocks: none.
- Justification: not applicable.
- Real-path test covering the same behaviour: every check runs against real
  artifacts, indexes and installs.

## Test Matrix

Link: [pypi-publish-2-1-0-test-matrix.md](pypi-publish-2-1-0-test-matrix.md).
Its crosswalk maps each D-id to clauses.

## Deliverables

Each deliverable names its consumer. The end consumers are users and agents
running `pip install -U docs-cli`, and the suite release that pins 2.1.0.

- [x] **The release contract, frozen in Phase 1.** Consumer: Phases 2–10 and
      the Step reviewers.
- [x] **The two D5 scripts**, with their RED evidence, control and mutation
      smoke. Consumer: Phases 2, 4, 5 and 7, and the next publish, through
      the runbook.
- [x] **The release inputs** (D7, D8). Consumer: readers of the PyPI long
      description, the GitHub release and the repository.
- [x] **The pre-publish evidence:** the gate, build (a) and its manifest,
      `twine check`, the local probe, the rehearsal with its byte checks, (b),
      and GO. Consumer: the Step 1 reviewers, and D2.
- [x] **`docs-cli==2.1.0` on PyPI**, with a bit-perfect chain of custody (D4).
      Consumer: users and agents, 2.0.0 installs through the update notice,
      and the suite pin bump.
- [x] **Served verification, then the tag and the release** (D13). Consumer:
      the suite PR's guard, repository readers, and GitHub's *Latest
      release*.
- [x] **Host integration** (D10): the notice observed, and the sweep table.
      Consumer: agents on this host, and the suite PR.
- [x] **The runbook's *From M31* lessons and corrections** (D11). Consumer:
      the next publish.
- [x] **The feedback-log hand-off update** (D12). Consumer: the suite PR, and
      the operator.
- [x] **The test matrix with adequacy results, the completion summaries and
      the status narrative.** Consumer: closeout review, and Step 3.

## TDD implementation plan

This is the runbook mapped onto ship-milestone's steps (D3). Each phase keeps
its canonical name, followed by its publish meaning.

**Step 1 — Contract and pre-publish baseline (Phases 1–4).** Branch
`pypi-publish-2-1-0/phases-1-4`. Both providers review it before anything
irreversible.

### Phase 1 — Define Contract — release contract and per-release re-verification

- Objective:
  - Freeze, as *Decisions (Phase 1 — BINDING)*:
    - the D5 check lists and expected values;
    - the scratch layout;
    - every command line;
    - the stop table;
    - the items listed under *Ambiguities*.
  - Re-run the runbook's per-release re-verification of E1–E4.
- Files: this document, the log and the matrix.
- Exit:
  - the contract is internally consistent;
  - the re-verification matches setup, or the differences are recorded;
  - there is no source-tree change;
  - the suite is at 1671, and `docs check .` exits 0.

### Phase 2 — Write Tests (RED) — release checks and their controls

- Objective: write the two D5 scripts and prove that each can reject a wrong
  answer.
  - Readiness fails on the base tree for exactly the reasons in
    *Acceptance examples*.
  - The probe's contract group passes on the editable build.
  - Against the host's 2.0.0 binary, both groups behave as Phase 1 froze for
    the control.
  - The mutation smoke (*Test Strategy*) records which check kills each
    mutant.
- Files: `tests/manual/release_readiness.py` and
  `tests/manual/release_probe.py`; the log; the matrix.
- Exit:
  - both scripts are clean under ruff, the formatter and mypy, and are
    stdlib-only;
  - both stay outside discovery: the collected count stays 1671;
  - the RED reasons are exactly the intended ones;
  - the control and the smoke are recorded;
  - nothing outside D1 changed.

### Phase 3 — Create Data/Fixtures — release inputs and probe trees

- Objective:
  - Make the D7 and D8 edits.
  - Confirm that every probe tree is built inline or copied to scratch,
    never the live tree.
  - Re-run readiness until it is GREEN.
- Files: `CHANGELOG.md`, `README.md`, the scripts' fixture builders only, and
  the log.
- Exit:
  - readiness is GREEN;
  - the branch diff is within D1;
  - the suite is at 1671.

### Phase 4 — Run Tests (RED Baseline) — pre-publish GREEN baseline: gate, build, smoke, rehearsal

- Objective: produce the evidence Step 1's reviewers judge and D2 requires,
  by P1.4's Phase 4.0–4.8: the gate, build (a), `twine check` and the
  schema, the local wheel, the rehearsal under `docs-cli-rehearsal`, build
  (b), the comparators, and GO or NO-GO.
- Files: the log and the matrix (results). `dist/` is git-ignored.
- Exit:
  - every P1.4 Phase 4 item is GREEN, with exact counts and shas recorded;
  - GO is recorded with the log's *Release anchors (current)*.

  Standard risk: there is no operator checkpoint here. A later change to a
  release input or a script triggers the D9 re-runs.

**Step 2 — Publish and post-release (Phases 5–10).** Branch
`pypi-publish-2-1-0/phases-5-10`. It starts only after Step 1's review pass
closes with `final-sync: ready`.

### Phase 5 — Update Base Interfaces — pre-upload gate and tag-target build

- Objective: P1.5's Phase 5 block — the stop table's pre-upload
  preconditions, a D7 re-date if the day has rolled, and build (c) at the
  clean `HEAD`, the tag-target commit.
- Files: the log, and `CHANGELOG.md` only if re-dated. *2026-10-28 (Step 2,
  OQ-S2-1): also `tests/manual/release_probe.py` (the G2 calibration), and
  this plan's rows amended by OQ-S2-1–5.*
- Exit: every precondition is true and recorded. Otherwise, stop with nothing
  uploaded.

### Phase 6 — Implement Offline/Core Path — the real PyPI upload

- Objective: under D2, P1.5's Phase 6 block — the pre-upload re-checks, the
  upload, and the per-version JSON's digests against (c)'s.
- Files: the log.
- Exit: both files are live with matching digests, or a stop is recorded.

### Phase 7 — Update Tool/Wrapper Layer — served verification, then tag and release

- Objective: P1.5's Phase 7 block — served verification (D4, D5, OQ-4),
  and only then the tag and the release (D13).
- Files: the log.
- Exit:
  - the chain-of-custody table is bit-perfect;
  - the probes are GREEN on the served wheel;
  - the peeled `v2.1.0` equals the tag-target commit;
  - `gh release view v2.1.0` shows the release.

### Phase 8 — Run Tests (GREEN) — the GREEN record

- Objective:
  - Run `release_readiness.py` and the full fast gate at the tag-target
    commit.
  - Record the three-build probe results in the matrix.
  - Record the suite's full guard. It is **expected to fail** against 2.1.0
    until the suite retires its stopgap (E11); that failure is the guard
    working, not a regression.
- Files: the log and the matrix.
- Exit: everything is GREEN with exact counts, and M30's probe assumption is
  validated against the served wheel.

### Phase 9 — Integrate / Accept / Dogfood — host integration (D10)

- Objective:
  1. **The update notice.** Before the upgrade, run the host's 2.0.0 binary
     with a scratch `XDG_CACHE_HOME`, with the update check enabled, once the
     aggregate JSON reports 2.1.0. P1.3's `env.sh` exports
     `DOCS_CLI_NO_UPDATE_CHECK=1`, so this one run is prefixed `env -u
     DOCS_CLI_NO_UPDATE_CHECK -u CI -u DO_NOT_TRACK`. Expect one notice line
     on stderr and an unchanged exit code. *Amended 2026-10-28 (Step 2,
     OQ-S2-5):* the command is `~/.local/bin/docs check .` in a fresh scratch
     tree with an empty `.docs.toml`, against a control run with the check
     suppressed, because 2.0.0's hook runs only after dispatch (not for
     `--version` or `-h`). Up to three attempts, each with a fresh scratch
     cache; if none prints the line, the same retries on P1.6's sha-checked
     scratch 2.0.0 install; if the line is still not observed, C16 is
     recorded unmet and Phase 9 continues — the release stands.
  2. **The binary.** After P1.5 Phase 7's simple-index poll, run `pipx
     upgrade docs-cli`. Verify that
     `~/.local/bin/docs --version` prints `docs 2.1.0`, installed from the
     PyPI index.
  3. **The skill.** This step leaves P1.3's scratch state on purpose, so the
     destination is recorded where D10 wants it: run `env -u XDG_STATE_HOME
     -u XDG_CACHE_HOME DOCS_CLI_NO_UPDATE_CHECK=1 ~/.local/bin/docs
     install-skill --force --dest ~/.claude/skills/docs`. Then verify all
     three:
     - `diff -r` against the served wheel's `docs_cli/skill/` is empty;
     - the host's `~/.local/state/docs-cli/install-skill.json` names the
       expanded `~/.claude/skills/docs`, and no `install-skill.json` appeared
       under `$S/xdg/state`;
     - the backup symlink is unchanged.
  4. **The sweep.** Run the read-only census of prescriptions 2.1.0
     supersedes, in the installed suite and its source repository:
     - hand-edited `Lifecycle:` or `Related:`;
     - stopgap references;
     - any assumption that `relate` refuses free-form verbs.

     Record counts per file.
  5. **Dogfood:** `DOCS_CLI_NO_UPDATE_CHECK=1 ~/.local/bin/docs check .` on
     this tree.
  6. **The liveness walk.**
- Files: the log. Host state changes only as D10 lists.
- Exit:
  - the notice is observed;
  - the D10 state is verified;
  - the sweep table is recorded;
  - no suite file changed;
  - no orphan output remains.

### Phase 10 — Quality, Docs, Refactor — runbook lessons, hand-off, closeout docs

- Objective:
  - Write the runbook's *From M31* lessons.
  - Correct the runbook's body, from Phase 1's list. The candidates:
    - the "impl log stays at root" instruction (D11), and the "merge and push
      `main`" step;
    - the *Tree state* block's `plan.md` and M6–M9 wording;
    - a host step for the binary, the skill and the sweep (D10);
    - XDG isolation and single-index `--no-deps` installs (D6);
    - `rm -rf dist/` before every build, and explicit filenames in every
      upload (D4);
    - the rehearsal byte checks (D4);
    - the peeled-tag check, `--verify-tag` and `--title` (D13);
    - the dependency oracle;
    - the D5 scripts as the standing probe;
    - D4's backend rule and D9's re-run rules.
  - Update the feedback-log hand-off (D12), and the outcome of the
    candidate-convention trial.
  - Update the status narrative.
  - Write the matrix's final results.
  - Run taste triage and the boundary sweep.
  - Clean up scratch.
  - Write the completion summaries.
- Files: `docs/release-runbook.md`, `docs/feedback-log.md`, `docs/status.md`,
  this trio, and the INDEX with its snapshot.
- Exit:
  - the gate is GREEN, and `docs check .` exits 0;
  - no placeholders remain;
  - everything that must outlive the archive is in a live document.

### Step 3 — Simplify and close (post-Phase 10)

Branch `pypi-publish-2-1-0/simplify`.
1. Run `/simplify` over the two scripts, the only code this milestone adds.
2. Prove GREEN, and take a clean pre-archive checkpoint.
3. Preview the archive, then apply the same scope (D11). The preview must
   select exactly the two companions.
4. Run `docs check .`, move the tracker row to `complete`, and update the
   status narrative.
5. Re-verify the README's `blob/main/` links (D8).

## Phase checklist

- [x] Phase 1 — Define Contract — release contract; per-release re-verification
- [x] Phase 2 — Write Tests (RED) — release checks; controls; mutation smoke
- [x] Phase 3 — Create Data/Fixtures — CHANGELOG dated; README reconciled
- [x] Phase 4 — Run Tests (RED Baseline) — pre-publish GREEN baseline: gate, build, smoke, TestPyPI rehearsal
- [x] Phase 5 — Update Base Interfaces — pre-upload gate; tag-target build
- [x] Phase 6 — Implement Offline/Core Path — real PyPI upload
- [x] Phase 7 — Update Tool/Wrapper Layer — served verification; then tag and release
- [x] Phase 8 — Run Tests (GREEN) — GREEN record at the tag-target commit
- [x] Phase 9 — Integrate / Accept / Dogfood — update notice; host binary and skill; sweep
- [x] Phase 10 — Quality, Docs, Refactor — runbook lessons; hand-off; summaries

## Decisions carried from discovery

- **2.1.0 ships through a separate one-to-one publish milestone** (M30 — D9,
  Q4; this row was registered by the operator).
- **The suite stopgap retires only in the suite release that pins a docs-cli
  carrying M30** (operator, 2026-10-26).
- **Skill channels** (`CLAUDE.md`): the bundled skill moves with every CLI
  change, and host skills move only at a production ship.
- **docs-cli is agent-agnostic** (operator, 2026-06-29): it installs where the
  operator says, never guesses the agent, and never judges an installed
  skill.
- **The Agent Playbook Suite rides its own release cycle** (operator policy).
- **`twine>=7.0.0`** (M29 — D1).
- **Runbook lessons applied:**
  - JSON lag, and tokens validated by use (M11);
  - the rehearsal prints `0.0.0+local` (M13);
  - CHANGELOG ships in neither artifact, and the sdist chain (M20);
  - no update notice on the rehearsal wheel (M24);
  - the README as a release artifact, and one scripted probe across builds
    (M29);
  - the binary upgraded together with the skill (M29 *Post-closeout*).
- **Archived endpoints need `--reason`** (M25 — D4; the tracker contract).

## Decisions (Phase 1 — BINDING)

Frozen 2026-10-28. This section holds Phase 1's catalogues and command lines
only. Each binding decision's operative wording stays in its D-id, and the
stop conditions stay in *Contract* › *Error cases* (the trial convention).
The five Step 1 planning questions (OQ-1–OQ-5) were conductor-resolved; the
log's Phase 1 section records them with their evidence.

**Common to both scripts** (D5):
- Stdlib only. Neither imports `docs_cli`: every `docs` call is a
  subprocess. Neither name matches `test_*.py`, so pytest never collects
  them. Neither carries a host-specific path, because `tests/` ships in the
  sdist.
- Every `docs` subprocess gets an environment the script builds: `HOME`,
  `XDG_STATE_HOME` and `XDG_CACHE_HOME` under a fresh temporary directory,
  `PYTHONPATH` and `PYTHONHOME` removed, `DOCS_CLI_NO_UPDATE_CHECK=1`,
  `PYTHONDONTWRITEBYTECODE=1`, stdin from
  `/dev/null`, and a 120 s timeout. The script enforces D6 even when its
  caller forgets (E10).
- Output: a header naming the script's git blob sha (`git hash-object`'s
  value), the repository `HEAD` and the `docs` path; then one line per
  check — `PASS  <name>`, `FAIL  <name> — <observed vs expected>` or
  `SKIP  <name> — <reason>` — and a summary line. Exit 0 when nothing
  failed, 1 otherwise, 2 on a usage error.
- Display names state the behaviour. The ids below (R…, N…, S…, G…, W…)
  live only in the milestone's documents, never in a display name.

### P1.1 — `release_readiness.py`

```
release_readiness.py --repo DIR --docs PATH --version 2.1.0 --release-date YYYY-MM-DD \
    --changelog-base bf09748 --drop-sentence "A separate publish milestone ships it."
```

`--repo` is the tree under test and defaults to the script's repository;
`--help` output always comes from `--docs`. The references are the
arguments (D1, D7), `git show <base>:CHANGELOG.md` (M30's reviewed text)
and that `--help`; nothing under test is its own reference. *Amended
2026-10-29 (Step 2 review, gpt-S3): an empty `--drop-sentence` means the
release drops nothing — R3 then checks only the publish-state patterns, and
R4 compares the two bodies unchanged.*

| Id | Check | Rule |
|---|---|---|
| R1 | pyproject.toml declares docs-cli at the release version | `[project]` `name == "docs-cli"` and `version == --version` |
| R2 | The newest CHANGELOG section is the release, dated `<D>` | The first `## ` heading is exactly `## <version> — <release-date>`, and the date parses |
| R3 | The release's CHANGELOG section makes no publish-state claim | The body of the first heading starting `## <version>` (heading excluded) does not contain `--drop-sentence`, and no line matches `unreleased`, `ready locally`, `not on pypi`, `publish milestone` or `deferred to m`, case-insensitively |
| R4 | The release's CHANGELOG section matches its reviewed text apart from the heading and the dropped sentence | `body.replace(" " + drop, "")` equals the same transform of `<base>`'s section body, so R3 and R4 stay independent |
| R5 | README.md lists every docs verb and sub-verb | The first `\{([a-z0-9,\-]+)\}` group of `docs --help`, plus the bare `{…}` group of each verb that has one (`project`, `relate`), is a subset of the verbs and sub-verbs on the README's synopsis lines |
| R6 ×14 | README.md synopsis for `docs <verb>` matches `docs <verb> --help` | One line per README synopsis line, by the rule below. `relate add\|remove` passes only if both sub-verbs' usages match |
| R7 | README.md does not mention Claude Code | Zero occurrences |
| R8a | Every README.md GitHub file link points at the pyproject Repository on main | Each `https://github.com/<owner>/<repo>/(blob\|tree)/<ref>/<path>` link has the `<owner>/<repo>` of `pyproject.toml`'s `[project.urls] Repository` (today `ArtRichards/docs-cli`) and `<ref>` `main` |
| R8b | Every README.md GitHub file link names a file tracked at HEAD | `git cat-file -e HEAD:<path>` for each distinct path (8 today) |
| R8c | Every README.md GitHub file link names a file on origin/main | `git cat-file -e origin/main:<path>`, against the local `origin/main` ref; P1.5 confirms that ref equals GitHub's `main` first |
| R9 ×2 | Bundled references/cli.md (and convention.md) is byte-identical to docs/ | Byte comparison |

**Synopsis rule.** It compares positional shape and flag names, never
positional names (*Check calibration*).
- *README side.* Only lines starting `docs ` inside the first fenced block
  after `## Commands` count; README line 98's `docs install-skill` is
  outside it. Tokens: `\[[^\]]*\]|<[^>]+>(?:\.\.\.)?|\S+`. After `docs` and
  the verb — and, for a verb whose usage has a bare `{…}` group, the
  sub-verb token (`a|b` names two) — the synopsis runs while tokens match
  `^\[.*\]$|^<[^>]+>(\.\.\.)?$|^[A-Z][A-Z0-9_-]*$|^\.\.\.$`. The first other
  token starts the description. `<x>` and an ALLCAPS metavar are one slot
  (S); `<x>...` is variadic (V); a bracket group is optional and
  contributes only its `--flag` names.
- *Help side.* The usage block from `usage:` to the first blank line,
  whitespace-normalised so terminal width cannot matter, minus
  `usage: docs <verb> [<sub>]`; the same tokens. A bare token is S; one
  followed by `...` is V. A bracket group `[M ...]` right after a bare run
  ending in `M` marks `nargs="+"`: a one-token `M` becomes V, and an `M`
  that already contains `...` (`file ... state`, `doc ... new-project`)
  keeps its own shape. Every other bracket group is optional.
- *PASS* when the slot sequences are equal and the README's flags are a
  subset of the usage's flags.

**Expected on the base tree** (`--release-date` = Phase 2's local date):
exit 1, failing exactly the reasons *Acceptance examples* › *Readiness*
names, as R2, R3 and R6 lines; every other line passes. After Phase 3,
every line passes.

### P1.2 — `release_probe.py`

```
release_probe.py --docs PATH --group {contract,all} --repo DIR --scratch DIR \
    [--expect-version 2.1.0 | --no-version-check]
```

- `--repo` defaults to the script's repository, as in P1.1.
- `--group all` requires exactly one of `--expect-version` and
  `--no-version-check`; the latter skips W1 with "rehearsal-name install
  reports 0.0.0+local" (M13).
- Each tree is built inline, or copied from `<repo>/tests/fixtures/trees/`
  or `<repo>/docs`, into a fresh directory under `--scratch`, which must lie
  outside `--repo`. No verb runs inside the repository.
- A snapshot is every file, `INDEX.md` and `.docs.toml` included
  (`tests/test_cli_lifecycle.py`'s `_snapshot`).
- Each 2.1-only exit-2 refusal also asserts its frozen message, because
  2.0.0's argparse `invalid choice` and `unknown verb` exit 2 as well.
- Expected values are quoted from `cli.md`, the CHANGELOG, and the product
  tests that pin each fixture (OQ-5). The docs-tree copy carries only
  tree-independent assertions (G1, G2).

**Contract group: new in 2.1.** The 2.0.0 control must fail every one.
Together they cover every bullet of the CHANGELOG's 2.1.0 section.

| Id | Check | Tree and assertion | Source |
|---|---|---|---|
| N1 | A milestone trio scaffolded with docs new is linked with free-form edges and promoted to active in one call, and docs check passes | Inline tree. From its directory: `new milestone m`, `new log m-impl`, `new spec m-test-matrix`; `relate add m.md pairs-with` each companion; `lifecycle m.md m-impl.md m-test-matrix.md active`; `check .`. Every call exits 0; all three read `Lifecycle: active`; `m.md` carries both bullets | *Primary use-case acceptance*; CHANGELOG *Added*, *Changed* |
| N2 | Re-running the same promotion changes no file | N1's tree: the same `lifecycle` call, with `--json`, exits 0; its record reads `applied: false`, `index_refreshed: false` and `change: unchanged` for every document; every file's bytes **and mtime** are unchanged, so an identical-content rewrite fails | CHANGELOG *Added* ("Idempotent"); `cli.md` › `docs lifecycle` (*Idempotency*, `--json`) |
| N3 | A free-form edge to an archived document needs no --reason and rewrites only its source | Inline tree with an archived `archive/2026-08-16/old.md`. `relate add m.md references archive/2026-08-16/old.md` exits 0; `m.md` gains the bullet; nothing but `m.md` and `INDEX.md` changes | CHANGELOG *Changed* ("never read or written") |
| N4 | docs lifecycle refuses archived as a target, points at docs archive, and changes nothing | Exit 2; stderr contains `docs archive <file> moves lifecycle and location together`; snapshot unchanged | `cli.md` › `docs lifecycle` |
| N5 | An out-of-grammar relate verb is refused with the grammar named, and nothing changes | `relate add a.md Pairs-With b.md`: exit 2; stderr contains `a free-form verb matching [a-z][a-z0-9-]*`; snapshot unchanged | `cli.md` › `docs relate`; CHANGELOG *Changed* |
| N6 | An extension lifecycle state set by docs lifecycle is read back by docs list and docs index | Copy of `vocab-extension`: `lifecycle draft-note.md shipped` exits 0; `list --json` reports `draft-note.md` as `shipped`; `index` exits 0 and `INDEX.md` contains the entry `- [draft-note.md](draft-note.md)` | CHANGELOG *Added*, *Fixed*; `tests/test_cli_list.py`; the entry fragment `tests/test_cli_touch.py` pins on this fixture |
| N7 | An extension-role document appears in INDEX.md | A fresh copy of `vocab-extension`: `index` exits 0, and `INDEX.md` lists `decision-record.md` under `### Active — Adr` | CHANGELOG *Fixed*; `tests/test_cli_index.py` |
| N8 | On a tree with a non-default date_format, relate links documents dated in that format | Inline `%d-%m-%Y` tree: `relate add a.md precedes b.md` exits 0, writing `precedes: b.md` on `a.md` and `follows: a.md` on `b.md`; `check .` exits 0 | CHANGELOG *Fixed* |
| N9 | docs stamp refuses a file whose complete block fails the configured vocabulary, writing nothing | A complete block reading `Lifecycle: activ`: exit 1; stderr contains `refusing to re-stamp it`; bytes unchanged | `cli.md` › `docs stamp`; CHANGELOG *Changed* |

**Contract group: the Agent Playbook Suite's guard probes.** The control
must fail both. Source: the guard step of the suite's `validate.yml` at
`a997954`, and its replicas
`tests/test_cli_lifecycle.py::test_help_verb_list_names_lifecycle_for_the_playbook_guard`
and `tests/test_cli_relate.py::test_playbook_guard_free_form_dry_run_probe_exits_0`.

| Id | Check | Assertion |
|---|---|---|
| S1 | The docs --help verb list names lifecycle, as the Agent Playbook Suite guard parses it | The first `\{([a-z0-9,\-]+)\}` match, split on commas, contains `lifecycle` |
| S2 | A free-form dry-run relate on a fresh tree exits 0 and writes nothing, as the Agent Playbook Suite guard probes it | Empty `.docs.toml`; `new spec a --quiet` and `new spec b --quiet` from the tree with no `--root`; then `relate add a.md pairs-with b.md --dry-run` exits 0 and the snapshot is unchanged |

**Contract group: carried from 2.0.** The control must pass all ten: M29's
contracts plus the runbook's index smoke.

| Id | Check | Tree and expected value | Source |
|---|---|---|---|
| G1 | docs check passes on a throwaway copy of this repository's docs tree | Copy of `<repo>/docs`: `check .` exits 0 | runbook *Quality gate* |
| G2 | docs index --dry-run on a copy of this docs tree reproduces its INDEX.md and writes nothing | The same copy: stdout equals its `INDEX.md` byte for byte, apart from the `_Generated YYYY-MM-DD.` summary date, which is normalised on both sides as `tests/test_cli_index.py` does; snapshot unchanged. *Calibrated 2026-10-28 (Step 2, OQ-S2-1): `render_index` stamps today's date, so the byte-exact form failed on any day after the tree was indexed — a check defect, not a contract change* | runbook *Quality gate*; `tests/test_cli_index.py` |
| G3 | A one-sided recognized edge is reported as missing-inverse | `reciprocal-missing`: `check --json` exits 2, with exactly one `missing-inverse` record, on `a.md`, carrying the frozen message | `tests/test_check.py` (frozen message; exit code) |
| G4 | Bare --cascade is refused and nothing changes | `archive-pair`: `archive feature.md --cascade` exits 2; stderr contains `--cascade is retired in docs 2.0 and writes nothing`; snapshot unchanged | `cli.md` › `docs archive` |
| G5 | A dead prose link is reported as broken-body-link | `bodylink-broken`: `check --json` exits 2 with exactly one record, `broken-body-link` on `doc.md`, naming `plan.md` | `tests/test_check.py` |
| G6 | mv --dry-run names every planned reference rewrite and writes nothing | `movelink-incoming`: `mv plan.md milestone-plan.md --dry-run` exits 0; stderr has the five lines the test freezes, including `2 destination(s) in 2 document(s), 1 Related: bullet(s)`; snapshot unchanged | `tests/test_cli_mv.py` (dry-run preview) |
| G7 | Archiving reports the still-active inbound references into the archived set | `movelink-closeout`: `archive feature.md --cascade-only 'feature-*' --date 2026-08-15` exits 0; stderr contains `docs: archive: 5 still-active inbound reference(s) into the archived set` | `tests/test_cli_archive.py` (strand report); `cli.md` › `docs archive` |
| G8 | docs archive records the Archived: date on every moved member | `archive-trio`: `archive feature.md --cascade-only 'feature-*.md' --reason 'trio closed out' --date 2026-03-04` exits 0; each of the three members sits under `archive/2026-03-04/` reading `Archived: 2026-03-04` | `tests/test_cli_archive.py` (cascaded trio) |
| G9 | docs mv refuses a move between two dated archive directories and changes nothing | `archivedate-two-dated-dirs`: `mv archive/2026-01-01/with-witness.md archive/2026-03-04/with-witness.md` exits 2; stderr has both frozen lines; snapshot unchanged | `tests/test_cli_mv.py` (cross-dated refusal) |
| G10 | A hand-relocated archived document is reported as archive-date-drift | `archivedate-drifted`: `check --json` exits 2 with exactly one `archive-date-drift` record, on `archive/2026-03-04/moved.md`, carrying the frozen message | `tests/test_cli_check.py` |

**Distribution group** (wheel installs, `--group all` only):

| Id | Check | Assertion | Source | 2.0.0 control |
|---|---|---|---|---|
| W1 | docs --version names the expected release | exit 0 and stdout exactly `docs <expect-version>`; SKIP under `--no-version-check` | M12; runbook smoke | FAIL |
| W2 | install-skill materialises a skill byte-identical to the repository's bundled skill | `install-skill --dest <tmp>/skill` exits 0; its file set and every byte equal `<repo>/src/docs_cli/skill` (seven files) | runbook smoke; `cli.md` › `install-skill` | FAIL — its bundle differs in six files, which also shows the comparison rejects a wrong bundle |
| W3 | Re-running install-skill on an identical destination is a no-op | The same `--dest`: exit 0; stderr contains `no-op`; bytes and mtimes unchanged | `cli.md` › `install-skill` (*Idempotency*) | PASS |
| W4 | install-skill --symlink is refused from a wheel install, leaving the destination absent | A new `--dest` with `--symlink`: exit 2; stderr contains `wheel install`; the destination is not created | `cli.md` › `install-skill` (*Refusals*) | PASS |

**Totals.** 21 contract checks and 4 distribution checks. The editable
build runs the contract group: 21 PASS. The 2.0.0 control (`--group all
--expect-version 2.1.0`) must FAIL exactly N1–N9, S1, S2, W1 and W2 (13) and
PASS G1–G10, W3 and W4 (12), exiting 1. Every wheel install must PASS all
25, with W1 skipped for the rehearsal.

### P1.3 — Scratch layout and environment

`$S` is a step-scoped directory in the running session's scratchpad. Step 2
runs in another session, so it creates its own `$S`; no Step 2 command reads
Step 1's scratch, and every value Step 2 needs is in the log. Committed
documents name `$S` only symbolically, because `docs/` ships in the sdist.

```
$S/env.sh     sourced before every manual command:
              export XDG_STATE_HOME=$S/xdg/state XDG_CACHE_HOME=$S/xdg/cache
              export DOCS_CLI_NO_UPDATE_CHECK=1 PYTHONDONTWRITEBYTECODE=1 PIP_CONFIG_FILE=/dev/null
              unset PIP_INDEX_URL PIP_EXTRA_INDEX_URL TWINE_REPOSITORY TWINE_REPOSITORY_URL TWINE_USERNAME TWINE_PASSWORD
              unset SOURCE_DATE_EPOCH     (it would move hatchling's fixed mtimes, and with them every sha)
              HOME stays: twine reads ~/.pypirc. The probe redirects HOME for its own subprocesses.
$S/notes/     captured outputs, copied into the log after build (b)
$S/a/  $S/r/  copies of (a)'s and the rehearsal's artifacts (dist/ is wiped between builds)
$S/x/<name>/  extractions (python3 -I -m zipfile -e …; tar -xzf … -C …); nothing runs from inside them
$S/dl-<name>/ fresh, empty download directories
$S/venv-<name>/  $S/probe/  $S/mut/  $S/backend-pin.txt (only if D4's remedy runs)
$S/tools/     the Phase 3 edit script and the readiness mutant script (Step 1 only)
$S/guard-step.sh  the suite guard step extracted per P1.5
```

**The host check**, before and after every block that runs a `docs`
executable: `sha256sum ~/.cache/docs-cli/update-check.json` is unchanged
across the block, and the recorded destination
`~/.local/state/docs-cli/install-skill.json` is as the last authorized step
left it — absent (`test ! -e`) until Phase 9's skill step (D10), naming the
expanded `~/.claude/skills/docs` from then on. *Amended 2026-10-28 (Step 2,
OQ-S2-3): the cache comparison is pairwise — each block's after-sha against
that block's before-sha — rather than against the Phase 1 baseline, which
the log keeps as the record. The cache's 24-hour throttle lets any
unisolated `docs` run on this host rewrite it; a change between blocks is
recorded with its mtime and is not attributed to the milestone.*

**Recording discipline.** Builds (a), the rehearsal and (b) all run on the
Phase 3 commit `X` with a clean tree, except for the rehearsal's own
`pyproject.toml` edit (D4). Evidence collects in `$S/notes/` until build
(b) is done; only then are the Phase 4 log and matrix written and committed.

### P1.4 — Step 1 command lines (Phases 2–4)

Run from the repository root after `. "$S/env.sh"`. `READY` abbreviates
`.venv/bin/python tests/manual/release_readiness.py --docs .venv/bin/docs
--version 2.1.0 --changelog-base bf09748 --drop-sentence "A separate publish
milestone ships it."`, and `PROBE` abbreviates `.venv/bin/python
tests/manual/release_probe.py --repo . --scratch "$S/probe"`.

**Every commit** (D1, D6):
```
TOKEN_RE='pypi-[A-Za-z0-9_-]{50,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}'
names=$(git diff --cached --text --name-only -G"$TOKEN_RE") \
  || { echo "STOP: the token search itself failed; do not commit"; exit 1; }
[ -z "$names" ] \
  || { printf 'STOP: a token-shaped string is staged (contents not shown) in:\n%s\n' "$names"; exit 1; }
echo "token search: clean"
git diff --name-only 8515f1c..HEAD | grep -vE \
  '^(docs/|CHANGELOG\.md$|README\.md$|tests/manual/release_(readiness|probe)\.py$|tests/fixtures/expected/docs-INDEX\.md$)'   # prints nothing
```

The token search runs as a script. It asks git's own pickaxe (`-G`, with
`--text` so binary files count) for the names of staged files whose diff
matches, so no matched text is ever printed. It never pipes a diff into
`grep -q`: that exits at the first match, the producer then dies of
SIGPIPE, and under `pipefail` the pipeline reads as "no match". A failing
search stops the commit exactly as a match does.

**Phase 2:**
```
$READY --repo . --release-date "$(date +%F)"              # exit 1, the acceptance example's RED lines
git clone --quiet --no-hardlinks . "$S/mut/green"           # apply Phase 3's edits there, uncommitted
$READY --repo "$S/mut/green" --release-date "$(date +%F)"   # exit 0: the GREEN control
cp -a "$S/mut/green" "$S/mut/<mutant>"                      # one fresh copy per mutant below
$PROBE --docs .venv/bin/docs --group contract               # exit 0, 21 PASS
$PROBE --docs ~/.local/bin/docs --group all --expect-version 2.1.0   # the control column
git status --porcelain --untracked-files=all                # empty after every run; then the host check
```

| Mutant | Applied to its copy | Killed by exactly |
|---|---|---|
| 1 | The heading back to `UNRELEASED` | R2 |
| 2 | Dated heading, sentence kept | R3 |
| 3 | One other line of the section edited | R4 |
| 4 | The `docs mv` synopsis line deleted | R5 |
| 5 | The `touch` synopsis back to `<file>` | R6 for `touch` |
| 6 | One byte appended to `src/docs_cli/skill/references/cli.md` | R9 for `cli.md` |
| 1b | `pyproject.toml` name `docs-cli-rehearsal` | R1 — the guard Phase 5 relies on |
| 5b | A synopsis naming a flag its verb lacks | R6 for that verb |
| 7 | The host's 2.0.0 binary | The control column (P1.2) |
| 8, 8b, 8c | The comparators | Phase 4, below |

Every other line stays PASS. The repository itself is never mutated.

**Phase 3:** `CHANGELOG.md` line 8 becomes `## 2.1.0 — <D>` with `D` the
local date (`date +%F`), and line 13 drops ` A separate publish milestone
ships it.`; README lines 53, 54, 56 and 57 take the four `--help` shapes.
Then `$READY --repo . --release-date <D>` exits 0. That commit is `X`.

**Phase 4.0 — preconditions.** `git status --porcelain` is empty; `X=$(git
rev-parse HEAD)`; the host check; the toolchain versions (`twine --version`,
`python -m build --version`, `pip --version`, `python --version`); the twine
check of P1.6.

**Phase 4.1 — the gate:**
```
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q                                  # 1671 passed
.venv/bin/python -m pytest --collect-only -q | tail -1         # 1671 tests collected
(cd docs && ../.venv/bin/docs check . && ../.venv/bin/docs index . --dry-run | cmp - INDEX.md)
cmp docs/INDEX.md tests/fixtures/expected/docs-INDEX.md
$READY --repo . --release-date <D>                             # exit 0
{ cat src/docs_cli/skill/SKILL.md src/docs_cli/skill/references/*.md docs/cli.md docs/convention.md \
      README.md CHANGELOG.md docs/architecture.md docs/test-strategy.md
  for v in "" lifecycle relate "relate add" "relate remove" stamp new; do .venv/bin/docs $v --help; done
} | tr -s '[:space:]' ' ' \
  | grep -oE 'free-form verbs stay hand-edited|refuses to edit them|Only the six recognized verbs' | wc -l   # 0
```
Then surface parity: each bullet of the CHANGELOG's 2.1.0 section is mapped
to the `--help` string that states it.

**Phase 4.2 — build (a):**
```
rm -rf dist/ && .venv/bin/python -m build
ls -A dist/                    # exactly docs_cli-2.1.0-py3-none-any.whl and docs_cli-2.1.0.tar.gz
sha256sum dist/docs_cli-2.1.0-py3-none-any.whl dist/docs_cli-2.1.0.tar.gz
unzip -p dist/docs_cli-2.1.0-py3-none-any.whl docs_cli-2.1.0.dist-info/WHEEL    # the Generator: line
cp dist/docs_cli-2.1.0-py3-none-any.whl dist/docs_cli-2.1.0.tar.gz "$S/a/"
python3 -I -m zipfile -e "$S/a/docs_cli-2.1.0-py3-none-any.whl" "$S/x/a-wheel"
tar -xzf "$S/a/docs_cli-2.1.0.tar.gz" -C "$S/x/a-sdist"
( cd "$S/x/a-sdist/docs_cli-2.1.0" && find . -type f ! -path './docs/*' ! -path './tests/*' -print0 \
    | LC_ALL=C sort -z | xargs -0 sha256sum )                 # (a)'s manifest, into the log verbatim
```

**Phase 4.3 — `twine check` and the schema:**
```
.venv/bin/twine check dist/docs_cli-2.1.0-py3-none-any.whl dist/docs_cli-2.1.0.tar.gz
unzip -p "$S/a/docs_cli-2.1.0-py3-none-any.whl" docs_cli-2.1.0.dist-info/METADATA \
    | grep -E '^(Metadata-Version|Requires-Python|Provides-Extra|Requires-Dist):'
unzip -l "$S/a/docs_cli-2.1.0-py3-none-any.whl" | grep -c CHANGELOG     # 0
tar -tzf "$S/a/docs_cli-2.1.0.tar.gz" | grep -c CHANGELOG               # 0
```
The dependency oracle (*Non-functional constraints*) must hold, and the
wheel's `docs_cli/skill/` entries must equal the seven files under
`src/docs_cli/skill`.

**Phase 4.4 — the local wheel:**
```
python3 -m venv "$S/venv-a"
"$S/venv-a/bin/pip" install --no-deps --no-index "$S/a/docs_cli-2.1.0-py3-none-any.whl"
diff -r -x __pycache__ "$S/x/a-wheel/docs_cli" "$S"/venv-a/lib/python3.*/site-packages/docs_cli   # empty
$PROBE --docs "$S/venv-a/bin/docs" --group all --expect-version 2.1.0    # 25 PASS
```
Then rehearse P1.5's suite guard-step run against `$S/venv-a`.

**Phase 4.5 — the rehearsal** under `docs-cli-rehearsal`:
1. Edit `pyproject.toml` line 6 to `name = "docs-cli-rehearsal"`; the
   version stays 2.1.0 (`.postN` only under D9). `git diff --stat` names
   only `pyproject.toml`.
2. `rm -rf dist/ && .venv/bin/python -m build`; `ls -A dist/` shows exactly
   the two rehearsal files; record both shas; copy them to `$S/r/`. The
   `Generator:` line must equal (a)'s.
3. `.venv/bin/twine check dist/docs_cli_rehearsal-2.1.0-py3-none-any.whl
   dist/docs_cli_rehearsal-2.1.0.tar.gz`.
4. Confirm `https://test.pypi.org/pypi/docs-cli-rehearsal/2.1.0/json` still
   returns 404 and `dist/` holds exactly the two files, then:
   ```
   .venv/bin/twine upload --repository testpypi --non-interactive \
       dist/docs_cli_rehearsal-2.1.0-py3-none-any.whl dist/docs_cli_rehearsal-2.1.0.tar.gz
   ```
5. Before anything executes: poll the per-version JSON (at most 10 × 30 s)
   until it lists both files; `curl -sSf -o` each listed `url` into a fresh
   `$S/dl-rehearsal/`; each sha must equal both the local build and the JSON
   digest. Extract the served wheel to `$S/x/r-wheel`: `diff -r
   "$S/x/a-wheel/docs_cli" "$S/x/r-wheel/docs_cli"` is empty, and every
   other entry sits under `docs_cli_rehearsal-2.1.0.dist-info/`.
6. Install from TestPyPI alone, then compare before running it:
   ```
   python3 -m venv "$S/venv-rehearsal"
   "$S/venv-rehearsal/bin/pip" install --no-cache-dir --no-deps \
       --index-url https://test.pypi.org/simple/ docs-cli-rehearsal==2.1.0
   diff -r -x __pycache__ "$S/x/a-wheel/docs_cli" "$S"/venv-rehearsal/lib/python3.*/site-packages/docs_cli
   ```
7. `$PROBE --docs "$S/venv-rehearsal/bin/docs" --group all
   --no-version-check`: the result lines equal (a)'s, except W1 is SKIP.
8. `git restore pyproject.toml && git diff --exit-code pyproject.toml`;
   `git status --porcelain` is empty.
9. Build (b) with 4.2's commands: the wheel sha equals (a)'s; the sdist is
   expected to equal (a)'s as well (same `X`). A differing wheel gets D4's
   remedy (P1.6), which counts only if it reproduces (a).

**Phase 4.6 — the comparators**, each of which must report a difference:
mutant 8, `cmp` of (a)'s wheel against the rehearsal wheel; 8b, `diff -r` of
(a)'s payload against a scratch copy with one byte appended to `cli.py`; 8c,
(a)'s manifest against the rehearsal sdist's (top directory stripped), which
differ in exactly `./PKG-INFO` and `./pyproject.toml`.

**Phase 4.7–4.8.** The host check; then GO, only if every Phase 4 item
above holds and the log's *Release anchors (current)* table is complete.
Anything else is NO-GO, a stop (*Error cases*).

### P1.5 — Step 2 command lines (Phases 5–7)

Frozen now so the Step 1 reviewers see the irreversible commands first (D2,
D3). `X`, (a)'s shas, the `Generator` version, (a)'s manifest and the
guard-step sha come from the log's *Release anchors (current)*.

**Phase 5 — preconditions, then build (c)** at the clean `HEAD`:
```
curl -s -o /dev/null -w '%{http_code}' https://pypi.org/pypi/docs-cli/2.1.0/json   # 404
git diff --quiet "$X"..HEAD -- src pyproject.toml README.md LICENSE .gitignore   # release inputs unchanged
git hash-object tests/manual/release_readiness.py tests/manual/release_probe.py
    # each equals its blob in Release anchors (current), whose D9 re-run covers any change since X
[ "$(git rev-parse origin/main)" = "$(gh api repos/ArtRichards/docs-cli/branches/main --jq .commit.sha)" ] \
    || git fetch origin main                      # R8c reads origin/main; record whether a fetch ran
$READY --repo . --release-date "$(date +%F)"     # exit 0; if R2 alone fails on the date: D7's re-date commit, re-run
.venv/bin/python -m pytest -q                     # 1671 passed, the two suite-probe replicas included
git ls-remote origin refs/heads/main && gh auth status    # both exit 0
python3 -I -c 'import configparser, os, stat, sys
try:
    p = os.path.expanduser("~/.pypirc")
    lines = ["mode " + oct(stat.S_IMODE(os.stat(p).st_mode))]
    c = configparser.ConfigParser(interpolation=None)
    c.read(p, encoding="utf-8")
    lines.append("sections-are-distutils,pypi,testpypi %s" % (c.sections() == ["distutils", "pypi", "testpypi"]))
    for s in ("pypi", "testpypi"):
        pw = c[s]["password"]
        lines.append("%s username==__token__ %s password-starts-pypi- %s password-len>100 %s"
                     % (s, c[s]["username"] == "__token__", pw.startswith("pypi-"), len(pw) > 100))
except BaseException:
    print("pypirc shape check failed: unreadable, malformed or incomplete (details suppressed)")
    sys.exit(1)
print("\n".join(lines))'
                                                  # the shape command: prints only fixed text and booleans; output = the log's record
git status --porcelain                            # empty
```
The shape command catches every error from reading, parsing or field
access and prints only its fixed failure line: a parser's error message
would quote the offending line, which may hold a token. It never prints a
section name or a field value. The toolchain versions are recorded with
P1.4's Phase 4.0 commands; a
patch-level difference from Phase 4's is recorded only, because (c) = (a)
by sha is the byte guard. Then build (c) with Phase 4.2's commands into `$S/c/` and `$S/x/c-wheel`,
`twine check` both files by name, and confirm: the (c) wheel sha equals (a)'s
(else D4's remedy); the (c) manifest equals (a)'s recorded manifest; `ls -A
dist/` shows exactly the two canonical files. `HEAD` is the tag-target
commit: `TAG_TARGET=$(git rev-parse HEAD)`, recorded in the log.

**Phase 6 — the upload**, immediately after these re-checks:
```
[ "$(date +%F)" = "$(sed -n 's/^## 2\.1\.0 — //p' CHANGELOG.md)" ]   # else back to Phase 5: D7's re-date, then (c) again
curl -s -o /dev/null -w '%{http_code}' https://pypi.org/pypi/docs-cli/2.1.0/json   # still 404
ls -A dist/                                       # exactly the two canonical files
sha256sum dist/docs_cli-2.1.0-py3-none-any.whl dist/docs_cli-2.1.0.tar.gz   # = (c)'s; the wheel = the anchor's (a)
env -u TWINE_REPOSITORY -u TWINE_REPOSITORY_URL -u TWINE_USERNAME -u TWINE_PASSWORD \
    .venv/bin/twine upload --repository pypi --non-interactive \
    dist/docs_cli-2.1.0-py3-none-any.whl dist/docs_cli-2.1.0.tar.gz
```
Any outcome but exit 0 follows *Error cases*' PyPI-upload row. On exit 0,
the per-version JSON's two digests equal (c)'s (polled, at most 10 × 30 s).

**Phase 7 — served verification, then the tag and the release:**
```
git worktree add --detach "$S/tag-tree" "$TAG_TARGET"      # immutable fixtures, docs and skill for the probe
mkdir "$S/dl-served"       # fresh and empty; curl -sSf -o each per-version JSON url into it
sha256sum "$S"/dl-served/*                                  # = (c) and = the JSON digests
python3 -m venv "$S/venv-served"
"$S/venv-served/bin/pip" install --no-cache-dir --no-deps --index-url https://pypi.org/simple/ docs-cli==2.1.0
diff -r -x __pycache__ "$S/x/c-wheel/docs_cli" "$S"/venv-served/lib/python3.*/site-packages/docs_cli   # empty
.venv/bin/python "$S/tag-tree/tests/manual/release_probe.py" --docs "$S/venv-served/bin/docs" \
    --group all --expect-version 2.1.0 --repo "$S/tag-tree" --scratch "$S/probe"   # result lines = (a)'s
git worktree remove "$S/tag-tree"
git -C ~/opt/agent-playbook-suite show a997954:.github/workflows/validate.yml \
    | sed -n '1210,1293p' | sed 's/^          //' > "$S/guard-step.sh"   # sha256 = the recorded value
G=$(mktemp -d -p "$S") && (cd "$G" && PATH="$S/venv-served/bin:$PATH" bash -e "$S/guard-step.sh")
    # exit 0, printing "lifecycle verb: True, free-form relate: True"
```
The probe reads its fixture trees, the docs copy (G1, G2) and the bundled
skill (W2) from the worktree, so they are the tag target's bytes, whatever
the working tree holds. The guard step's lines 1210–1293 are the step's
`run:` block, dedented by its ten-space indent. From an empty directory the suite's policy file and
skills tree are absent, so it exits 0 exactly when both capabilities read
True (OQ-4). *Amended 2026-10-28 (Step 2, OQ-S2-4):* before the `pip
install` above, and before Phase 9's `pipx upgrade`, poll PyPI's PEP 691
simple JSON (`https://pypi.org/simple/docs-cli/`, at most 10 × 30 s) until
both 2.1.0 files are listed with sha256 equal to (c)'s; the poll is
read-only and absorbs index lag. Only then:
```
git tag -a v2.1.0 -m "docs-cli 2.1.0 — docs lifecycle and free-form docs relate" "$TAG_TARGET"
git push origin v2.1.0
git ls-remote origin 'refs/tags/v2.1.0^{}'                  # = the tag-target commit
gh release create v2.1.0 --verify-tag --title "docs-cli 2.1.0" \
    --notes "$(awk '/^## 2.1.0 —/{flag=1; next} /^## /{flag=0} flag' CHANGELOG.md)"   # non-empty notes
gh release view v2.1.0
```

### P1.6 — Settled items

- **The twine step.** The runbook's `pip install --upgrade 'twine>=7.0.0'`
  becomes a read-only check: the installed twine equals PyPI's newest and is
  at least 7.0.0, at Phase 1 and Phase 4. An upgrade would be a toolchain
  change, allowed only before build (a) and only if the check fails; Step 2
  never upgrades.
- **The 2.0.0 control.** Phase 2 used the host's pipx binary, run by the
  probe with its redirected `HOME` and XDG, so it wrote nothing to the pipx
  venv or host state. A D9 re-run uses a scratch install instead: `pip
  download --no-deps --only-binary :all: --index-url https://pypi.org/simple/
  docs-cli==2.0.0` into a fresh directory, its sha checked against M29's
  served digest (E1) before anything runs, then `pip install --no-deps
  --no-index` of that file into a fresh venv. W2 is expected FAIL, as P1.2
  records. Phase 9's update notice still runs the host binary, by design.
- **M29's tree-dependent values** come from committed fixture trees (P1.2,
  OQ-5).
- **The sdist download** uses the per-version JSON `url` with `curl` and a
  digest check, not `pip download --no-binary :all:`, which runs the build
  backend on downloaded code on a host holding tokens.
- **The backend pin.** (a)'s `Generator:` line and a build environment that
  reproduces (a) byte for byte — hatchling and each of its resolved
  dependencies — are recorded in *Release anchors (current)*. D4's remedy is
  `.venv/bin/python -m build --dependency-constraints-txt
  "$S/backend-pin.txt"`, the file pinning that whole environment, one
  `name==version` per line. `pyproject.toml` stays unpinned (*Taste anchors*
  › *Dependency policy*).
- **The runbook correction list for Phase 10** (Step 1 does not edit the
  runbook): the items in Phase 10's objective, plus — `twine check` with
  explicit filenames; the twine newest-version check; the sdist download via
  the JSON URL; `PIP_CONFIG_FILE=/dev/null` and the `env -u TWINE_*` guard;
  D9 superseding the rehearsal's "fix, bump patch, rerun"; the stale *Notes*
  line "version is hardcoded in two places" (obsolete since M12); the stale
  *Quality gate* counts (271/369/401); README synopsis arity, now checked by
  readiness (M29 lesson 4); the verbatim guard-step run; the non-disclosing
  token search; the upload-outcome precedence; and `unset SOURCE_DATE_EPOCH`
  with the recorded build environment.

## Setup questions (Q1–Q2)

Both are **RESOLVED** by the operator (2026-10-28, in this session), each as
recommended. The packets stay as the audit trail. The operative wording lives
in the D-ids each resolution names.

### Q1 — Tag and GitHub release: inside Step 2 under D2, or later?

- **Origin.**
  - The runbook's *Post-release* tags the commit PyPI serves, pushes the tag
    and creates the release.
  - M29's D2 listed the tag and the release as irreversible actions needing
    authorization.
  - The operator's first 2026-10-28 answer named only the upload.
  - ship-milestone pushes only milestone branches, through sync-and-commit.
  - `main` is already public with M30 (E8). `v2.0.0` sits at `408ef6c`, and
    M30's stack was merged with a merge commit (`bf09748`).
- **Why now.** Phase 1 freezes Step 2's action list.
- **Options:**
  - **(A)** tag and release in Step 2, under D2;
  - **(B)** tag locally, and push and release after the merge — GitHub would
    keep showing 2.0.0 as *Latest* in the meantime;
  - **(C)** a separate go after served verification.
- **Example.** M29 pushed `v2.0.0` at its chain-of-custody commit, together
  with the release, in its Phase 5.
- **Recommendation:** (A).
- **Question.** Does the automatic authorization also cover the tag push and
  the GitHub release in Step 2?
- **Resolution (operator, 2026-10-28): (A).** See D2 and D13.

### Q2 — The host refresh: destination, binary upgrade, backup symlink

- **Origin.**
  - `CLAUDE.md`'s production-ship refresh.
  - The operator rule: install where the operator says, never guess.
  - E9: no recorded destination; a pipx 2.0.0 binary; the backup symlink.
  - M29's *Post-closeout* binary/skill gap.
- **Why now.** Phase 9 writes outside the repository, and the destination
  cannot be inferred.
- **Options:**
  - **(a) destination:** `~/.claude/skills/docs`, another directory, or skip;
  - **(b) binary:** upgrade it, or leave it to the operator;
  - **(c) symlink:** leave it, or remove it.
- **Example.** M29 refreshed the skill while the binary stayed at 1.8.0.
  Until the operator upgraded it, the host skill prescribed `--cascade-only`
  to a binary that did not have it.
- **Recommendation:** `~/.claude/skills/docs`; upgrade the binary; leave the
  symlink.
- **Question.** Should Phase 9 refresh at that destination, upgrade the
  binary in the same phase, and leave the symlink alone?
- **Resolution (operator, 2026-10-28): refresh and upgrade, as recommended.**
  See D10.

### Also settled, without a question

The conductor accepted these on 2026-10-28, and Phase 1 does not re-open them:
- Standard risk;
- no version bump (D1);
- the committed release checks (D5);
- the `.postN` re-rehearsal and the re-run rules (D9);
- the backend-pin remedy (D4);
- the trio archiving together (D11);
- the untouched suite and the read-only sweep (D10, D12);
- the trial taste anchor;
- the archived-endpoint pairs written through `docs relate --reason`;
- no GitHub issue to answer (E13);
- `main` does not move at publish (E8).

## Follow-ups recorded for later milestones

| # | Follow-up | Home |
|---|---|---|
| 1 | **The Agent Playbook Suite pin bump to 2.1.0.** It re-vendors `skills/docs`, bumps `DOCS_CLI_VERSION`, swaps hand-edit prescriptions for `docs lifecycle` / `docs relate`, retires the unmerged stopgap, and drops ship-milestone Step 0's up-front approval. Afterwards its CI guard reads True / True. | Agent Playbook Suite; the feedback-log 2026-10-26 entry stays open (D12) |
| 2 | **Re-scope the PyPI and TestPyPI tokens to project `docs-cli`.** Rolled forward from M9, now seven releases old. | Operator |
| 3 | **An in-repo drift lint** comparing the workflow skills' docs-cli prescriptions with the bundled `references/`. Rolled forward from M20, M24 and M29. | Later |
| 4 | **Pin the build backend in `[build-system]`.** Only if D4's remedy is ever needed. | Later; record in the runbook's lessons if it is exercised |

## Testing and quality gate

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q
(cd docs && ../.venv/bin/docs check .)
.venv/bin/python tests/manual/release_readiness.py …                     # arguments: P1.4
.venv/bin/python tests/manual/release_probe.py --docs <venv>/bin/docs …  # per D5; arguments: P1.4, P1.5
```

Additional gates:
- the INDEX snapshot in lockstep with `docs/INDEX.md`;
- the reference byte identity;
- `twine check`, and the D4, D9 and D6 checks.

## Success criteria

- **The release.** `docs-cli==2.1.0` is served by PyPI. The chain of custody
  holds per D4, bit-perfect for the wheel and the sdist.
- **One probe passes three builds.** The same distribution probe passes on
  wheel (a), the TestPyPI-served wheel (version line excepted) and the
  PyPI-served wheel. The 2.0.0 control fails the 2.1-only checks.
- **The suite's guard flips.** Before the tag, the suite's capability probes
  read True / True against the PyPI-served wheel, and both replica tests
  pass. This discharges M30 hand-off item 2.
- **The release inputs.** Readiness passes at the tag-target commit (D7, D8).
- **The gate.** At the tag-target commit and at closeout:
  - 1671 passed;
  - ruff, the formatter and mypy clean;
  - `docs check .` exits 0;
  - the INDEX snapshot and the mirrors identical.
- **Hygiene.** D6 holds throughout: no credential leaks, and no stray host
  state.
- **The tag and the release** exist and are verified per D13.
- **The host follows the release.** Phase 9 verifies the D10 state, and the
  update notice is observed. This discharges M30 hand-off item 3.
- **The hand-off.** The sweep table is in the feedback-log hand-off, the suite
  is untouched, and the hand-off stays open (D12).
- **The runbook** carries the *From M31* lessons and its corrections.
- **The closeout.** The archive selects exactly the trio, `docs check .` exits
  0, the tracker row is `complete`, the README's links resolve, and the final
  report states D13's merge instruction.

## Completion summary (Step 2)

Step 2 ran 2026-10-28 to 2026-10-29 under D2 with no stop row firing:
`docs-cli==2.1.0` was uploaded once from the tag-target build `33c936f`,
proven bit-perfect against PyPI's bytes, verified by the release probe and
the suite's guard step, then tagged and released (D13). The host binary and
skill follow it (D10), the runbook carries the lessons, and the suite
hand-off stays open (D12). The record, with every sha, time and deviation,
is the [implementation log](pypi-publish-2-1-0-impl.md)'s *Milestone
completion summary*. Step 3 (2026-10-29) ran `/simplify` and the
explicit-scope archive closeout (the log's *Step 3 — Simplify and
closeout*); the operator's merge remains (D13).
