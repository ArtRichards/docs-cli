# M31 — Publish docs-cli 2.1.0 to PyPI

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-10-28

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
- Progress: **Milestone setup complete (2026-10-28), and Phase 1 — Define
  Contract is next.**
  - Both setup questions are resolved by the operator (*Setup questions*).
  - Step 0 review-pass-001 returned four blockers. All are fixed in
    `b127fd1`, along with every should-fix and nit, and the pass is closed:
    Step 0 is complete.
  - Setup measured the publish surface read-only (E1–E13, in the
    implementation log); *Current state and evidence* lists the three
    findings that reshape the runbook. Nothing was built, uploaded, installed
    or published.

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
three synopses that lag the CLI (E7), and changes nothing else unless
readiness finds drift. The `blob/main/` links are re-verified after the Step 3
archive.

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
would leave the tagged commit off `main`. The milestone's final report says
so explicitly: *merge with a merge commit, not squash or rebase; `v2.1.0` is
at `<sha>`*.

## Contract

This is the setup draft. Phase 1 freezes the exact check lists, command lines
and scratch layout as *Decisions (Phase 1 — BINDING)* in this document, as
M25–M30 did.

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
- **E7** — the README covers 13 of 13 verbs, but three synopses lag the CLI.
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
  (M11): a 401 or 403 stops with nothing uploaded.
- **Build (c) reproduces wheel (a)**, or can be pinned to (D4). Owner:
  Phase 5.
- **The suite's probes are as measured** (E11). Owner: Phase 7, against the
  served wheel.
- **The stack is merged with a merge commit** (D13). Owner: the operator's
  merge instruction.

### Ambiguities

**Resolved by the operator:** Q1 (→ D2, D13) and Q2 (→ D10).

**Phase-1 freeze items (none needs the operator):**
- each script's exact checks and expected values;
- the scratch layout;
- the exact command lines;
- the sdist download method — `pip download --no-binary :all:` (M20), or the
  per-version JSON URL;
- the backend-pin mechanism (D4);
- the runbook correction list (Phase 10).

**Also settled by Phase 1:**
- **The runbook's `pip install --upgrade 'twine>=7.0.0'` step.** Phase 1
  decides whether it runs, given that Phase 5 requires an unchanged toolchain.
  Twine is already the newest release (E4).
- **The 2.0.0 control.** Phase 1 decides how the control classifies
  `install-skill` byte identity, since its bundle cannot match 2.1's.
- **M29's tree-dependent expected values**, such as the `mv --dry-run` rewrite
  count. They are re-derived on today's throwaway tree, not copied.

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
| The 2.1.0 slot is taken on PyPI at Phase 5 | Stop; nothing uploaded | The per-version JSON returns 200 |
| The Step 1 review pass is not closed, or a blocker is undispositioned | Step 2 does not start | The review ledger |
| The rehearsal is not GO, or failed (D9) | Stop; Step 1 does not close | Implementation log, Phase 4 |
| The served rehearsal wheel ≠ the uploaded rehearsal build, or its payload ≠ (a)'s (D4) | Stop; Step 1 does not close | The rehearsal sha and payload comparison |
| A release input changed after the rehearsal, or a D5 script changed after its Phase 4 run, with no re-run (D9) | Stop; nothing uploaded | `git diff <rehearsal-commit>..HEAD -- src pyproject.toml README.md LICENSE .gitignore tests/manual` |
| `twine check` fails | Stop before upload | twine's output |
| Wheel (b) or (c) ≠ (a) and the backend pin does not cure it, or an sdist member outside `docs/`/`tests/` differs from (a)'s recorded manifest (D4) | Stop; nothing uploaded | The sha table; the member manifest |
| `dist/` does not hold exactly the two canonical files with build (c)'s shas (D4) | Stop; nothing uploaded | `ls dist/`; `sha256sum` |
| The tree is dirty at a build, beyond D4's rehearsal exception | Stop | `git status --porcelain` |
| `~/.pypirc` is missing, or its shape changed | Stop | The shape check (D6) |
| The upload is refused for authentication (401/403) | Stop; nothing uploaded | twine's exit and message |
| A partial upload: one file accepted, the other refused | Retry only the missing file, by name, once; a second failure stops. Never re-send an accepted file | The per-version JSON file list |
| A served sha ≠ the local sha | Stop before the tag; the operator decides (yank or not) | The chain-of-custody table |
| The served-wheel probe or the suite capability probes fail | Stop before the tag and release; the operator decides (yank, or a patch milestone) | The probe output |
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
- **Readiness.** Given today's tree, readiness fails for exactly five reasons:
  - the `UNRELEASED` heading;
  - the publish-state sentence;
  - the `touch`, `stamp` and `project set` synopses.

  After Phase 3, it passes.
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
- `README.md`: about 3–6 lines;
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
  - RED in Phase 2, for the five reasons in *Acceptance examples*;
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

- [ ] **The release contract, frozen in Phase 1.** Consumer: Phases 2–10 and
      the Step reviewers.
- [ ] **The two D5 scripts**, with their RED evidence, control and mutation
      smoke. Consumer: Phases 2, 4, 5 and 7, and the next publish, through
      the runbook.
- [ ] **The release inputs** (D7, D8). Consumer: readers of the PyPI long
      description, the GitHub release and the repository.
- [ ] **The pre-publish evidence:** the gate, build (a) and its manifest,
      `twine check`, the local probe, the rehearsal with its byte checks, (b),
      and GO. Consumer: the Step 1 reviewers, and D2.
- [ ] **`docs-cli==2.1.0` on PyPI**, with a bit-perfect chain of custody (D4).
      Consumer: users and agents, 2.0.0 installs through the update notice,
      and the suite pin bump.
- [ ] **Served verification, then the tag and the release** (D13). Consumer:
      the suite PR's guard, repository readers, and GitHub's *Latest
      release*.
- [ ] **Host integration** (D10): the notice observed, and the sweep table.
      Consumer: agents on this host, and the suite PR.
- [ ] **The runbook's *From M31* lessons and corrections** (D11). Consumer:
      the next publish.
- [ ] **The feedback-log hand-off update** (D12). Consumer: the suite PR, and
      the operator.
- [ ] **The test matrix with adequacy results, the completion summaries and
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
  - Readiness fails on today's tree for exactly the five reasons in
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

- Objective: produce the evidence Step 1's reviewers judge and D2 requires.
  1. **The gate.** The runbook's *Quality gate* and *Surface parity*, with
     M30's stale-wording grep returning 0. Also readiness, the INDEX snapshot
     and the reference identity.
  2. **Build (a)** per D4. Record:
     - the backend version and both shas;
     - (a)'s per-member sdist sha256 manifest, for every member outside
       `docs/` and `tests/`.
  3. **`twine check`**, and the manifests: the schema items under *Test
     Strategy*.
  4. **The local wheel.** Install (a) in a throwaway venv (D6) and run both
     probe groups. Record each script's blob sha.
  5. **The rehearsal under `docs-cli-rehearsal`:**
     1. make the temporary `pyproject.toml` edit (D9);
     2. `rm -rf dist/`, then build;
     3. run `twine check`;
     4. `twine upload --repository testpypi --non-interactive
        dist/docs_cli_rehearsal-<version>-py3-none-any.whl
        dist/docs_cli_rehearsal-<version>.tar.gz`;
     5. install per D6;
     6. run D4's rehearsal byte checks;
     7. run both probe groups, with the version check skipped;
     8. revert the edit, and confirm `git diff pyproject.toml` is empty;
     9. build (b), and confirm it equals (a).
  6. **Record GO or NO-GO.**
- Files: the log and the matrix (results). `dist/` is git-ignored.
- Exit:
  - every item above is GREEN, with exact counts and shas recorded;
  - GO is recorded.

  Standard risk: there is no operator checkpoint here. A later change to a
  release input or a script triggers the D9 re-runs.

**Step 2 — Publish and post-release (Phases 5–10).** Branch
`pypi-publish-2-1-0/phases-5-10`. It starts only after Step 1's review pass
closes with `final-sync: ready`.

### Phase 5 — Update Base Interfaces — pre-upload gate and tag-target build

- Objective:
  - Check every D2 precondition in the stop table, except those that need
    build (c).
  - Re-date per D7 if the day has rolled.
  - Build (c) at the clean `HEAD`, which is the tag-target commit, per D4.
  - Run `twine check`.
  - Confirm three things:
    - (c) = (a);
    - the sdist members match the Phase 4 manifest;
    - `dist/` holds exactly the two canonical files.
- Files: the log, and `CHANGELOG.md` only if re-dated.
- Exit: every precondition is true and recorded. Otherwise, stop with nothing
  uploaded.

### Phase 6 — Implement Offline/Core Path — the real PyPI upload

- Objective:
  - Under D2, run `.venv/bin/twine upload --non-interactive
    dist/docs_cli-2.1.0-py3-none-any.whl dist/docs_cli-2.1.0.tar.gz`.
  - Confirm that the per-version JSON lists both files, with sha256 digests
    equal to (c)'s.
- Files: the log.
- Exit: both files are live with matching digests, or a stop is recorded.

### Phase 7 — Update Tool/Wrapper Layer — served verification, then tag and release

- Objective:
  1. **Install** `docs-cli==2.1.0` from PyPI into a fresh venv, with
     `--no-deps` (D6).
  2. **Download** the served wheel and sdist into fresh empty directories, and
     confirm both equal (c) (D4).
  3. **Run `release_probe.py`**, both groups, with the version check on.
  4. **Run the suite's capability probes** verbatim from its CI step, with
     `PATH` set to the served venv.
  5. **Only then,** tag and release per D13, and verify the peeled tag.
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
     aggregate JSON reports 2.1.0. Expect one notice line on stderr and an
     unchanged exit code.
  2. **The binary.** Run `pipx upgrade docs-cli`. Verify that
     `~/.local/bin/docs --version` prints `docs 2.1.0`, installed from the
     PyPI index.
  3. **The skill.** Run `DOCS_CLI_NO_UPDATE_CHECK=1 ~/.local/bin/docs
     install-skill --force --dest ~/.claude/skills/docs`. Then verify all
     three:
     - `diff -r` against the served wheel's `docs_cli/skill/` is empty;
     - the recorded-destination file names `~/.claude/skills/docs`;
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

- [ ] Phase 1 — Define Contract — release contract; per-release re-verification
- [ ] Phase 2 — Write Tests (RED) — release checks; controls; mutation smoke
- [ ] Phase 3 — Create Data/Fixtures — CHANGELOG dated; README reconciled
- [ ] Phase 4 — Run Tests (RED Baseline) — pre-publish GREEN baseline: gate, build, smoke, TestPyPI rehearsal
- [ ] Phase 5 — Update Base Interfaces — pre-upload gate; tag-target build
- [ ] Phase 6 — Implement Offline/Core Path — real PyPI upload
- [ ] Phase 7 — Update Tool/Wrapper Layer — served verification; then tag and release
- [ ] Phase 8 — Run Tests (GREEN) — GREEN record at the tag-target commit
- [ ] Phase 9 — Integrate / Accept / Dogfood — update notice; host binary and skill; sweep
- [ ] Phase 10 — Quality, Docs, Refactor — runbook lessons; hand-off; summaries

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
.venv/bin/python tests/manual/release_readiness.py                       # Phase 1 freezes the arguments
.venv/bin/python tests/manual/release_probe.py --docs <venv>/bin/docs    # per D5
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
