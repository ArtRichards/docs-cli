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
> (`be7f809`), straight after M30 merged to `main` (`bf09748`). M30 is the only
> milestone this release ships, and it is complete and archived, so the publish
> itself is all that is outstanding. The operative checklist is
> [release-runbook.md](release-runbook.md). This document maps that runbook
> onto ship-milestone's steps, freezes the decisions setup made, and gives the
> publish exit criteria. The per-phase record lives in
> [pypi-publish-2-1-0-impl.md](pypi-publish-2-1-0-impl.md).

## Overview

- Milestone: M31 — the second milestone under the canonical tracker, and the
  first publish mapped onto ship-milestone's step and phase structure. M13 ran
  under `/ship-milestone` too, but walked the runbook directly.
- Slug: `pypi-publish-2-1-0` — tracker identity and branch root
  (`pypi-publish-2-1-0/milestone-setup`, `…/phases-1-4`, `…/phases-5-10`,
  `…/simplify`)
- Title: Publish docs-cli 2.1.0 to PyPI
- Surface: publish M30 as `docs-cli==2.1.0` by the runbook. M30 is
  `docs lifecycle`, one-sided free-form `docs relate`, and `parse()` honouring
  the tree's configured vocabulary and `date_format`. Then refresh the host
  binary and the host skill, sweep the workflow skills, and record the Agent
  Playbook Suite hand-off. **No product code changes** (D1).
- Test Matrix:
  [pypi-publish-2-1-0-test-matrix.md](pypi-publish-2-1-0-test-matrix.md)
- Implementation log:
  [pypi-publish-2-1-0-impl.md](pypi-publish-2-1-0-impl.md)
- Progress: **Milestone setup complete (2026-10-28). Both setup questions are
  RESOLVED by the operator — Q1 → (A), the tag and the release in Step 2; Q2 →
  refresh the host skill and upgrade the host binary. The conductor accepted
  the Standard risk level and every item settled without a question. Phase 1 —
  Define Contract is next.** Setup
  re-measured the publish surface read-only and recorded thirteen pieces of
  evidence (**E1–E13**, in the implementation log's setup record). Nothing was
  built, uploaded, installed or published.
  - The registries are ready: PyPI's `2.1.0` slot is free, and the bare
    TestPyPI name is still squatted, so the `docs-cli-rehearsal` detour
    continues with its `2.1.0` slot free.
  - The credentials the operator copied today from robbie.local are present
    and well formed (shape only). `twine` is 7.0.0, the full gate is GREEN at
    **1671**, and the version is already 2.1.0, because M30 bumped it.
  - Only two release inputs need editing. The CHANGELOG needs its date and one
    sentence removed (D7), and the README has three synopses that lag the
    CLI (D8).
  - Setup also found three facts the runbook does not anticipate:
    - The build backend (`hatchling` 1.33.0) was published today, and
      `[build-system]` does not pin it. So a Step 2 rebuild can drift from
      what Step 1 rehearsed. D4 guards this.
    - This host has **no recorded skill destination**. So the host refresh
      needed the operator to name one: `~/.claude/skills/docs` (Q2, D10).
    - `docs install-skill` records its destination on every success. So an
      unisolated smoke run overwrites host state, as M29's did. D6 guards
      this.

### Identity note

The tracker identity is the semantic slug `pypi-publish-2-1-0`. `M31` is a
prose label only, continuing the M1–M30 history. The row is at order 200 and
depends on `lifecycle-and-free-form-relate` (order 100, `complete`, archived
under `archive/2026-10-28/`). The tracker contract therefore requires two
recognized pairs with that archived document:
- the 100 → 200 sequence pair, `precedes` / `follows`;
- the dependency pair, `depends-on` / `required-by`.

Both were written at setup with `docs relate add … --reason`, which appends an
audited `Revision:` bullet to the archived endpoint and leaves its lifecycle,
`Archived:` and prose untouched (M25 — D4's audited repair). The setup record
shows the exact commands.

### Goal

`pip install -U docs-cli` delivers 2.1.0, byte for byte the wheel this
milestone built, smoke-tested and rehearsed. An agent on any host can then
promote a document with `docs lifecycle` and link it with free-form
`docs relate`. The Agent Playbook Suite can then pin a published release that
retires its verbless-metadata stopgap.

### Primary use-case acceptance

Against the **PyPI-served** wheel, installed fresh with no repository on the
path:

- **M30's primary use case runs.** A milestone trio is scaffolded with
  `docs new`, linked with `docs relate add … pairs-with …` and promoted with
  one `docs lifecycle … active`, with zero hand-edits and `docs check` clean.
  `release_probe.py` (D5) exercises it.
- **The suite's guard flips.** The Agent Playbook Suite's CI capability probes,
  run verbatim, read `lifecycle verb: True` and `free-form relate: True`. This
  is M30 hand-off item 2.
- **A 2.0.0 install learns about 2.1.0.** M21's update notice, run from a
  2.0.0 binary, names `2.0.0 -> 2.1.0` once on stderr and leaves the exit code
  unchanged.
- **This host follows the release.** Its binary reports `docs 2.1.0`, and its
  `docs` skill at `~/.claude/skills/docs` is byte-identical to the bundle the
  served wheel carries (D10).

## Risk Level

**Standard** — proposed at setup and **accepted by the conductor's triage**
(2026-10-28). It was not raised as an operator question, because the evidence
does not support High. The operator chose automatic upload (D2) knowing the
upload is irreversible; High would pause after Step 1 instead.

Reason: the milestone ships code that M30 already built, reviewed and accepted
at Standard risk. That level was operator-confirmed (Q8). M30 then passed
dual-provider reviews at Steps 0–2, 1671 tests GREEN, and a 47/47 mutation
smoke. This milestone adds no product code. Its own risk is **release
integrity**. The PyPI upload is irreversible: the index is append-only, a bad
file can be yanked but never replaced, and the version number is burned.

That risk is handled by process gates that are cheaper and stronger here than
High's defaults:
- the TestPyPI rehearsal;
- `twine check`;
- the chain-of-custody rule, which refuses to upload bytes that were not
  rehearsed (D4);
- the stop conditions (*Contract* › *Error cases*);
- Step 1's dual-provider review, before anything irreversible.

High's distinctive gates do not fit. There is no product behaviour to
mutation-test or benchmark. Its post-Phase-4 operator checkpoint would
contradict D2.

Two High-list triggers were considered:
- *Public APIs.* M30 judged the published CLI surface additive and Standard,
  and this milestone cannot change it.
- *Data integrity.* No user data is written, and D6 covers credentials.

Precedent: M13, M17 and M20 published fully autonomously under up-front
authorization.

Selected gates (Standard):

- Lite:
  - the contract;
  - an explicit check for every artifact this milestone changes or ships
    (D5);
  - `ruff check`, `ruff format --check` and `mypy src/ tests/`;
  - `docs check .` from the docs root;
  - the live-INDEX snapshot and the reference byte identity.
- Coverage report: **not configured** in this project; recorded as not
  applicable.
- Hidden/generalization smoke: **selected**, as its publish analogue. The same
  probe runs against three builds — local, TestPyPI-served and PyPI-served —
  plus a 2.0.0 control that must fail the 2.1-only checks.
- Property/stateful smoke: **selected**:
  - idempotence (an `install-skill` re-run, a `docs lifecycle` re-run);
  - the sha-equality chain across builds (D4).
- Mock audit: **selected** — no mocks. Every check runs against real
  registries, real installs and real trees.
- Reviewer signoff: the Step 1 and Step 2 dual-provider reviews. Step 1's
  review is a precondition of the upload (D2).

## Binding decisions (setup)

Each binding decision is stated **once**, here. Every other section refers to
it by id. This adopts the candidate convention the feedback log offered to
this setup (2026-10-28, *State a binding decision once*). D2, D3 and the
credential facts in D6 are operator decisions of 2026-10-28. The rest are
derived from the runbook, the tracker contract, `CLAUDE.md`, operator policy
and precedent, as each cites.

### D1 — What ships: M30, one-to-one, as `docs-cli==2.1.0`

The release carries exactly M30, merged to `main` as `bf09748`:
- `docs lifecycle`;
- one-sided free-form `docs relate`;
- `parse()` honouring the tree's configured vocabulary and `date_format`;
- `docs stamp`'s config refusal.

This is the one-to-one shape of M10 → M11, M12 → M13 and M19 → M20; M29
instead batched the five-milestone v2.0 train. 2.1.0 is a SemVer
minor because M30 is additive (M30 — D9). M30 Phase 7 already made the bump:
`pyproject.toml` reads `2.1.0`, and `tests/test_packaging.py` pins it in A3,
B1, B2 and C2. So this milestone changes no version literal, no file under
`src/`, and no product test. Its only source-tree edits are:
- the CHANGELOG dating (D7);
- the README reconciliation (D8);
- the two release-check scripts (D5).

### D2 — Release authorization (operator, 2026-10-28, in this session)

This is the equivalent of M29's D2. **Upload automatically.** Step 2 uploads
to PyPI without pausing for a further operator go, once two things hold:
- the Step 1 review pass is closed;
- the TestPyPI rehearsal has passed, with GO recorded.

The authorization covers three actions, all in Step 2:
- `twine upload` of the two canonical 2.1.0 artifacts to PyPI (Phase 6);
- pushing the annotated `v2.1.0` tag, right after the PyPI-served
  verification (Phase 7, D13);
- creating the GitHub release with `gh release create` (Phase 7, D13).

The operator extended it to the last two by answering Q1 with (A). It holds
only while every precondition in *Contract* › *Error cases* holds at the moment
of each action. If one fails, the authorization is void: nothing further is
published, and the milestone stops for the operator.

**A recorded exception.** ship-milestone pushes only through sync-and-commit,
and only milestone branches. The `v2.1.0` tag push is the one push outside
that rule, and it is authorized here. Branch pushes still go through
sync-and-commit, and this milestone never pushes `main`.

**Merging the branch stack into `main`** is not a milestone step. The conductor
merges the stack after Step 3; D13 records the merge shape this release
depends on.

### D3 — The runbook runs through ship-milestone (operator, 2026-10-28)

M9–M29 walked [release-runbook.md](release-runbook.md) directly, with no TDD
phases. The operator chose to run this publish through ship-milestone, and
accepted the conductor's mapping:

- **Step 1** — Phases 1–4. Readiness, release inputs, the gate, the build, the
  local smoke and the TestPyPI rehearsal: everything before the irreversible
  upload. Both providers review it.
- **Step 2** — Phases 5–10. The upload, served verification, the post-release
  work, the runbook lessons and the closeout docs.
- **Step 3** — simplify, then the explicit-scope archive closeout.

*TDD implementation plan* gives the phase-by-phase detail. The mapping has two
consequences:
- Phase 2's "tests" are release checks (D5).
- Phase 4's baseline is a **pre-publish GREEN baseline**: the gate plus the
  rehearsal evidence. A publish ships no new behaviour, so the quality model's
  GREEN-baseline allowance for behaviour-preserving work applies. The RED
  evidence comes from Phase 2's controls instead.

### D4 — Chain of custody: the wheel is the anchor

Four wheels must share **one sha256**:
- (a) Phase 4's canonical build — the wheel the local smoke and probe
  exercised;
- (b) the post-rehearsal canonical rebuild;
- (c) the Step 2 tag-target build;
- (d) the PyPI-served wheel.

The TestPyPI wheel differs from (a) only by the detour name, so it is checked
behaviourally, not by sha.

If (b) or (c) does not match (a), stop. The one automatic remedy is to rebuild
with the build backend pinned to the version (a) used; every build records its
backend version. The remedy counts only if it reproduces sha (a). Anything else
is a stop.

The sdist captures `docs/`, so by design it moves between builds (M13, M20,
M29). Its rules:
- It is anchored at (c).
- It must be bit-perfect against the PyPI-served sdist.
- Every member outside `docs/` and `tests/` must be byte-identical to the
  members of (a)'s sdist. That means `src/`, `README.md`, `LICENSE`,
  `pyproject.toml` and `PKG-INFO`.

Both served artifacts are also compared against the sha256 digests in PyPI's
per-version JSON.

### D5 — The release checks are committed, non-product scripts

There are two scripts. Both are stdlib-only and live under `tests/manual/`,
outside pytest's default discovery; the precedent is
`tests/manual/m7_success_criteria.py`. Each exits 0 on PASS and 1 on FAIL,
with one line per check.

**`release_readiness.py`** checks the source tree:
- the `pyproject.toml` version equals the release version (the packaging
  pins are product tests, already in the gate);
- the CHANGELOG release heading is dated and free of publish-state wording;
- the README lists every verb in the `docs --help` brace group;
- the README contains no "Claude Code";
- every README `blob/main/` link resolves to a tracked file;
- the bundled references are byte-identical to `docs/`.

**`release_probe.py`** checks an artifact. It runs unchanged against any
`docs` executable:
- M30's headline contracts;
- both Agent Playbook Suite probes, exactly as the suite's CI runs them;
- M29's nine 2.0 contracts, as regression;
- the distribution contracts — `install-skill` byte identity, the no-op
  re-run, and the `--symlink` refusal.

`docs --version` is asserted except under the rehearsal name, the M13 caveat.

Names state behaviour, not milestone ids. Phase 1 freezes each check list and
its expected values. Those values come from `cli.md`, the CHANGELOG's 2.1.0
section, M30's binding decisions and M29's contracts — never from a build's
output. Existing product tests are reused unchanged, in particular the 2.1.0
pins and the two suite-probe replicas.

### D6 — Isolation and secrets

**Throwaway runs.** Every smoke, probe, rehearsal install and download runs
in a throwaway venv and throwaway trees outside the repository, with:
- `XDG_STATE_HOME` and `XDG_CACHE_HOME` pointed at scratch;
- `DOCS_CLI_NO_UPDATE_CHECK=1`, except where the notice is under test, which
  still uses a scratch cache.

The reason: `docs install-skill` records its destination on every success
(E10), so an unisolated smoke run overwrites this host's recorded destination.
M29's smoke runs did exactly that. Downloads land in fresh empty directories
and nothing is executed from inside them. Only Phase 9 writes host state.

**Credentials.** The operator copied `~/.pypirc` today from robbie.local (mode
`600`; `[distutils]`, `[pypi]`, `[testpypi]`; `username = __token__`; both
passwords `pypi-` prefixed). Twine alone reads it:
- No token value is ever printed, logged or committed. Checks report shape
  only.
- `twine upload` runs with `--non-interactive`.
- Before every commit, a search of the staged diff for token-shaped strings
  returns nothing.

### D7 — CHANGELOG dating

The heading becomes `## 2.1.0 — <YYYY-MM-DD>`, with the local calendar date of
the PyPI upload. The sentence "A separate publish milestone ships it." is
removed. Nothing else in the section changes, because M30 wrote it to survive
publication (E6).

Phase 3 dates it with the expected day. If the day has rolled by Phase 5, a
one-line commit re-dates it before the tag-target build. CHANGELOG ships in
neither artifact (M13, M20), so re-dating moves no sha.

### D8 — The README is a Phase-3 artifact

The README is the PyPI long description (M29 lesson). Phase 3 reconciles the
three synopses that lag the CLI (E7): `docs touch`, `docs stamp` and
`docs project set` each take several files. It keeps 13 of 13 verbs and zero
"Claude Code" mentions, and changes nothing else unless the readiness check
finds drift. The `blob/main/` links are re-verified after the Step 3 archive.

### D9 — Re-rehearsal

The rehearsal certifies the artifact inputs as they stood when it ran. A later
change to any of these invalidates Phase 4's build, smoke, probe and
rehearsal, including a change made by a Step 1 review fix:
- `src/`;
- `pyproject.toml`;
- `README.md`;
- `LICENSE`.

The build, smoke, probe and rehearsal are then re-run before Step 1 closes.
TestPyPI refuses to reuse a version,
so a re-rehearsal uploads `docs-cli-rehearsal` as `2.1.0.post1`, then
`.post2`, and so on. That rehearsal-only version goes in the same temporary
`pyproject.toml` edit as the name detour and is reverted with it. Canonical
`2.1.0` never changes.

A rehearsal **failure** is different from a re-run: it is a stop. The
runbook's remedy for a failure is a version bump, which would change what this
milestone ships. Changes confined to `docs/` invalidate nothing.

### D10 — Post-release host work (`CLAUDE.md`; agent-agnostic)

After served verification:

- (a) **The host binary is upgraded first** (operator, Q2):
  `pipx upgrade docs-cli` to 2.1.0. It is verified by the host binary reporting
  `docs 2.1.0`, installed from the PyPI index.
- (b) **The host `docs` skill is then refreshed with that published binary**
  (operator, Q2): `docs install-skill --force --dest ~/.claude/skills/docs`.
  The operator named the destination because no recorded destination exists
  on this host (E9). The refresh makes it the recorded destination. The
  refreshed copy is verified byte-identical to the served wheel's bundle.
- (c) **The backup symlink
  `~/.claude/skills/docs-local-source-backup-20260525-134621` stays
  untouched** (operator, Q2).
- (d) The workflow-skill sweep is a **read-only** census. It looks for
  docs-cli prescriptions that the 2.1.0 surface supersedes, in the installed
  Agent Playbook Suite and its source repository. The findings go into the
  feedback-log hand-off. Neither the suite repository nor the plugin cache is
  changed; the suite rides its own release cycle.

No step guesses the agent. Nothing inspects or judges an installed skill,
beyond verifying the copy this milestone has just installed.

### D11 — Closeout follows the canonical tracker

Step 3 archives the three artifacts together, with
`docs archive pypi-publish-2-1-0.md --cascade-only 'pypi-publish-2-1-0-*'`.
The implementation log does **not** stay at the root as M17's, M20's, M24's
and M29's did. The 2026-10-26 tracker migration archived those four logs, and
the tracker contract archives the trio.

Anything that must outlive the archive lives in a live document:
- the suite hand-off, in [feedback-log.md](feedback-log.md);
- the narrative, in [status.md](status.md);
- the procedure, in [release-runbook.md](release-runbook.md).

Phase 10 corrects the runbook's post-release block to match.

### D12 — The suite hand-off stays open

M30's hand-off, the 2026-10-26 entry in [feedback-log.md](feedback-log.md),
splits in two:
- **Items 1–3 are this milestone's** and close here with evidence: the
  publish, the served-wheel probe replay, and the host refresh.
- **The suite pin-bump PR items stay open** until that suite release ships.

Setup adds two facts the PR needs (E11):
- The stopgap commits sit on an unmerged suite branch.
- The suite's own procedure re-vendors `skills/docs` with
  `docs install-skill --force` in the same change as the pin bump.

### D13 — Tag and GitHub release in Step 2 (operator, 2026-10-28: Q1 → A)

- Right after the PyPI-served verification (Phase 7), annotate `v2.1.0` at the
  tag-target commit on `pypi-publish-2-1-0/phases-5-10`. That is the exact
  commit the uploaded artifacts were built from. Push the tag.
- Create the GitHub release with `gh release create v2.1.0`. Its notes are the
  dated `## 2.1.0` CHANGELOG section.
- Both run under D2's authorization, and the tag push is D2's recorded
  exception.

**A recorded dependency.** Until the stack is merged, the tag points at a
branch commit. The conductor merges stacks with a history-preserving merge
commit, as M30's `bf09748` did, which keeps the tagged commit an ancestor of
`main`. A squash or rebase merge would orphan the tag, so this stack's merge
must preserve history.

## Contract

This is the setup draft. Phase 1 freezes the exact check lists, command lines
and scratch layout under *Decisions (Phase 1 — BINDING)* in this document, as
M25–M30 did.

### Facts

The evidence ids refer to the implementation log's setup record.

- **E1** — PyPI's latest release is `2.0.0`, and the `2.1.0` slot is free. The
  served 2.0.0 shas equal M29's chain-of-custody anchors.
- **E2** — the bare TestPyPI name is still the unrelated `0.1.0` squatter, so
  the detour continues. `docs-cli-rehearsal`'s `2.1.0` slot is free.
- **E3** — the credentials are present and well formed, and `gh` holds `repo`.
- **E4** — `twine` is 7.0.0, the newest release, which satisfies M29 — D1.
  `[build-system]` does not pin `hatchling`, and 1.33.0 was published today.
- **E5** — the full gate is GREEN at `be7f809`: **1671 passed**.
- **E6** — the version is already 2.1.0 everywhere, with one CHANGELOG
  sentence to remove.
- **E7** — the README covers 13 of 13 verbs, has 8 of 8 links resolving and
  no "Claude Code", but three synopses lag the CLI.
- **E8** — `main` equals `origin/main` (`193fc71`) and already carries M30.
  No `v2.1.0` tag or GitHub release exists.
- **E9** — the host binary is pipx `docs-cli` 2.0.0. `~/.claude/skills/docs`
  is a directory from M29's refresh, the backup entry is a symlink to this
  repository's `src/docs_cli/skill`, and no recorded destination exists.
- **E10** — `docs install-skill` records its destination on every success,
  including a scratch smoke run.
- **E11** — the suite's CI probes match M30's replicas, and its pin is 2.0.0.
  The stopgap sits on an unmerged branch, and the installed 0.8.3 still
  prescribes hand-edits.
- **E12** — the open feedback-log entries that ship unchanged all predate the
  2.1.0 decision or were deferred by M30's decisions. None is a release
  blocker.
- **E13** — no open GitHub issue is addressed by 2.1.0. The only issue, #1,
  closed on 2026-08-16.

### Assumptions

- **The copied PyPI token is valid for upload.** Owner: Phase 6. Validation:
  by use, as M11 recorded ("tokens validated by use"). A 401 or 403 is a stop
  with nothing uploaded. There is no non-mutating probe, and the TestPyPI
  upload proves only the TestPyPI token.
- **Step 2's build reproduces Step 1's wheel**, or can be pinned to do so.
  Owner: Phase 5 (D4).
- **The suite guard's probes are still as measured.** Re-confirmed today
  (E11). Owner: Phase 8, against the served wheel.
- **The stack is merged with a history-preserving merge commit**, so the
  branch-commit tag stays on `main`'s history (D13). Owner: the conductor, at
  the merge after Step 3.

### Ambiguities

- **Resolved by the operator (2026-10-28):**
  - Q1 → (A): the tag and the release happen in Step 2 (D2, D13).
  - Q2 → refresh and upgrade at `~/.claude/skills/docs`, leaving the backup
    symlink untouched (D10).

  See *Setup questions*.
- **Phase-1 freeze items (not operator questions):**
  - each script's exact check list and expected values;
  - the scratch layout and environment;
  - the exact build, rehearsal, upload, download and comparison command lines;
  - the sdist download method — `pip download --no-binary :all:` as in M20,
    or the per-version JSON URL;
  - the backend-pin mechanism for D4's remedy;
  - the runbook correction list for Phase 10.

### Inputs

- The repository at the Step 1 base: M30 merged, plus the tracker
  registration and claim.
- `~/.pypirc` (D6), PyPI and TestPyPI, and `gh`, authenticated as
  `ArtRichards`.
- This host's pipx install and `~/.claude/skills/docs`, touched only in
  Phase 9, as D10 lists.

### Outputs

- `docs_cli-2.1.0-py3-none-any.whl` and `docs_cli-2.1.0.tar.gz` on PyPI, with
  their sha256 values recorded.
- The `v2.1.0` tag and the GitHub release (D13).
- Edits to `CHANGELOG.md` (D7) and `README.md` (D8), and the two
  `tests/manual/` scripts (D5).
- In the docs tree: the runbook's *From M31* lessons and its corrections; the
  feedback-log hand-off update; the status narrative; this trio's evidence.
- On the host (D10): the pipx binary at 2.1.0, and the `docs` skill at
  `~/.claude/skills/docs`, which is now also the recorded destination.

### Invariants

- Must always:
  - build from a clean tree;
  - record the sha256 of every artifact built, uploaded or downloaded, and
    the backend version of every build;
  - run the **same** probe script against every build;
  - verify the state before and after each irreversible action.
- Must never:
  - change product code or a product test — `src/`, and `tests/` outside
    `tests/manual/`;
  - upload a wheel whose sha differs from the rehearsed canonical wheel (D4);
  - reuse a version on either index;
  - print, log or commit a credential (D6);
  - write host state outside Phase 9 (D6);
  - edit the Agent Playbook Suite repository or the plugin cache (D10);
  - edit an archived document, except through `docs relate --reason`'s audited
    path;
  - hand-edit a metadata block (`docs lifecycle` and `docs relate` cover every
    edit the workflow prescribes).
- If any D2 precondition fails, nothing is uploaded and the milestone stops
  for the operator.

### Error cases

These are the stop conditions. Each one voids D2 until the operator decides.

| Condition | Expected behaviour | Observability |
|---|---|---|
| The `2.1.0` slot is taken on PyPI at Phase 5 | Stop; nothing uploaded | The per-version JSON returns 200; the `releases` array |
| The Step 1 review pass is not closed, or a blocker is undispositioned | Step 2 does not start | The review ledger |
| The rehearsal is not GO, or failed (D9) | Stop; Step 1 does not close | The implementation log, Phase 4 |
| An artifact input changed after the rehearsal with no re-rehearsal (D9) | Stop; nothing uploaded | `git diff <rehearsal-commit>..HEAD -- src pyproject.toml README.md LICENSE` is non-empty |
| `twine check` fails on any artifact | Stop before upload | twine's output |
| Wheel sha (b) or (c) ≠ (a), and the backend pin does not cure it (D4) | Stop; nothing uploaded | The sha table |
| An sdist member outside `docs/` or `tests/` differs from (a)'s sdist (D4) | Stop; nothing uploaded | The member diff |
| The tree is dirty at a build | Stop | `git status --porcelain` |
| `~/.pypirc` is missing or its shape changed | Stop | The shape check (D6) |
| The upload is refused for authentication (401/403) | Stop; nothing uploaded | twine's exit and message |
| A partial upload — one file accepted, the other refused | Retry **only** the missing file, once; a second failure stops. Never re-send an accepted file. | The per-version JSON file list |
| A served sha ≠ the local sha | Stop and investigate; the operator decides (yank or not) | The chain-of-custody table |
| The probe fails against the PyPI-served wheel | Stop; record; the operator decides (yank, or patch through a new milestone) | The probe output |
| The `v2.1.0` tag push or `gh release create` fails | Stop that step; the PyPI release stands; record it and ask | git's or gh's exit and message |
| `pipx upgrade` fails, or the host binary does not report `docs 2.1.0` | Stop the host step before the skill refresh; the PyPI release stands | pipx's output; `docs --version` |
| `install-skill --force` at the host destination fails | Stop the host step; the published release stands | The command's exit and stderr |

### Non-functional constraints

- **Performance:** no budget. Elapsed times are recorded.
- **Security and privacy:** D6. `twine upload --non-interactive` is used, so
  an authentication problem can never block on a prompt in an agent session.
- **Compatibility:** 2.1.0 is additive (M30 — D9). No tree that 2.0.0's
  `docs check` passes fails any verb (M30 — D10). `Requires-Python >=3.11`,
  and there are zero runtime dependencies: the wheel metadata carries no
  `Requires-Dist`, as the charter requires.
- **Reliability:** every irreversible step is verified after the fact. The
  aggregate JSON's 60–120 s lag is tolerated (M11, M20), and the simple index
  and the per-version endpoint are authoritative.

### Acceptance examples

- **Local wheel.** Given the Phase 4 canonical wheel in a fresh venv with
  scratch XDG directories, when `release_probe.py` runs, then every check
  passes, and the host's recorded-destination file is still absent.
- **The 2.0.0 control.** Given the host's 2.0.0 binary, when the probe runs,
  then every 2.1-only check fails and every 2.0 regression check passes.
- **Readiness, before and after.** Given today's CHANGELOG, when
  `release_readiness.py` runs, then it fails, naming the `UNRELEASED` heading
  and the publish-state sentence. After Phase 3, it passes.
- **The rehearsal.** Given `docs-cli-rehearsal==2.1.0` installed from
  TestPyPI, when the probe runs with the version check skipped, then every
  other check passes. Given the post-rehearsal canonical rebuild, its wheel
  sha equals (a).
- **The pre-upload check.** Given the Step 2 tag-target build, when its wheel
  sha is compared with (a), then they are equal. Otherwise nothing is
  uploaded.
- **The served wheel.** Given `docs-cli==2.1.0` installed from PyPI:
  - when the probe and the suite's capability probes run, then everything
    passes;
  - `docs --version` prints `docs 2.1.0`;
  - the guard reads `lifecycle verb: True` and `free-form relate: True`.
- **The update notice.** Given a 2.0.0 binary with a scratch update-check
  cache and the check enabled on a non-TTY, when it runs a read-only verb
  after the publish, then it prints
  `docs: update available 2.0.0 -> 2.1.0 — run: pip install -U docs-cli`
  once on stderr, and its exit code is unchanged.
- **The host skill.** Given the refreshed host skill, when it is compared
  with the served wheel's `docs_cli/skill/`, then `diff -r` is empty, and the
  recorded destination names the refreshed directory.

### Taste anchors

- **Reference documents and code this work should read like:**
  - M29's [task plan](archive/2026-08-16/m29-pypi-publish-2-0-0.md) and
    [log](archive/2026-10-26/m29-pypi-publish-2-0-0-impl.md): the phase
    narrative, the chain-of-custody tables and the lessons voice;
  - the runbook's *Cumulative lessons* entries, appended to and never
    rewritten;
  - M30's [trio](archive/2026-10-28/lifecycle-and-free-form-relate.md): the
    ledgers and the matrix shape;
  - for the scripts, `tests/manual/m7_success_criteria.py` (a stdlib-only
    script with a usage docstring, exit 0 or 1) and the exact probe code of
    the two suite-probe replica tests.
- **In-project libraries to reuse:**
  - the standard library only (`subprocess`, `tempfile`, `hashlib`, `json`,
    `re`, `shutil`, `pathlib`, `tomllib`);
  - committed fixture trees such as `tests/fixtures/trees/minimal/`, and
    throwaway copies of this docs tree, rather than new committed fixtures;
  - the runbook's commands, verbatim where they are still right.
- **Established patterns to follow:**
  - the runbook's walked-top-to-bottom checklist;
  - sha256 tables;
  - credential checks that print prefixes and shape only;
  - "squatter still parked" style re-checks;
  - `docs touch` after body edits, and `docs lifecycle` / `docs relate` for
    every metadata edit;
  - behaviour-first check names with no milestone or decision ids;
  - **each binding decision stated once, in *Binding decisions*, and
    referenced by id elsewhere.** This is the 2026-10-28 candidate convention,
    adopted here as a trial.
- **Expected diff footprint:**
  - `src/`: 0 lines;
  - `CHANGELOG.md`: about 2 lines;
  - `README.md`: about 3–6 lines;
  - `tests/manual/`: two new scripts, roughly 250–450 lines together;
  - docs: this trio, about 40–90 lines of runbook lessons and corrections,
    about 15–30 lines of feedback-log hand-off update, a status paragraph, and
    the INDEX plus its snapshot.

  A product-code diff of any size triggers a scope review.
- **Dependency policy:** no runtime or development dependency changes.
  `twine>=7.0.0` is already in `[dev]`. No build-backend pin is added to
  `pyproject.toml`; D4's remedy is a per-build constraint, logged if it is
  used.

### Forbidden shortcuts

- Do not compare an artifact against itself, or take an expected value from
  a build's own output. Expected values come from the contract (D5).
- Do not skip the rehearsal or the served-wheel probe because "the code did
  not change". The bytes and the index are what are under test.
- Do not upload with `--skip-existing`. It would mask a partial or repeated
  upload. The partial-upload retry names the one missing file explicitly.
- Do not run any smoke run against the host's real XDG state (D6).
- Do not weaken a valid check, or delete a failing one, to reach GREEN.
  Correct an erroneous expectation under the quality model's *Check
  calibration* rule, and log it.
- Do not re-date, rename or re-version anything to get past a stop condition.

### Test hooks

- Visible tests to generate: **none in default discovery**. The 1671-test
  suite is the regression evidence, including the 2.1.0 pins in
  `tests/test_packaging.py` and the suite-probe replicas
  `tests/test_cli_lifecycle.py::test_help_verb_list_names_lifecycle_for_the_playbook_guard`
  and
  `tests/test_cli_relate.py::test_playbook_guard_free_form_dry_run_probe_exits_0`.
- Explicit non-product checks, outside default discovery: the D5 scripts,
  `twine check`, the D4 sha and member comparisons, the D9 input diff, the D6
  credential-hygiene search, `docs check .`, the INDEX snapshot and the
  reference byte identity.
- Hidden/generalization categories: see *Test Strategy*.
- Property/stateful invariants: idempotence of the `install-skill` and
  `docs lifecycle` re-runs; the D4 sha-equality chain; identical probe results
  across the three builds, apart from the rehearsal's version line.
- Mutation-sensitive logic: the probe's 2.0-versus-2.1 discriminators; the
  readiness check's publish-state wording classes; the sha comparator.
- Fuzz targets: not applicable. There is no new parsing surface, and M30's
  grammar fuzz lives in the product suite.
- Benchmark/security/schema checks: `twine check`; the recorded
  `Metadata-Version`; the wheel and sdist manifests; the credential-hygiene
  search. Benchmark is not applicable.

## Out of scope

- **Any change to product code or product tests.** That includes the open
  feedback-log items: CRLF normalisation, the duplicated-label edit, the
  recognized-verb TARGET injection, the `--body-from` bare-label leak, the
  dangling free-form edge, vocabulary validation at load, the
  out-of-vocabulary repair route, and the "validate-all-first atomic" wording.
  Each ships as it stands (E12).
- **The Agent Playbook Suite pin-bump PR**, and any edit to the suite
  repository or the plugin cache (D10, D12).
- **Merging the branch stack into `main`.** The conductor does it after
  Step 3, with a history-preserving merge (D13).
- **Re-scoping the PyPI and TestPyPI tokens to project `docs-cli`.** It is
  operator UI work and rolls forward.
- **Trusted Publishing**, or a CI release workflow (the runbook's *Notes*).
- **Pinning `hatchling` in `[build-system]`.** D4 handles drift per release;
  see *Follow-ups*.
- **The "Claude Code" wording that survives** in a `pyproject.toml` comment
  and in `charter.md`. Neither is a shipped surface: a comment is not
  metadata, and the charter is a planning document. The README and `src/`
  carry none (E7).
- **Managing other host skills.** The
  `docs-local-source-backup-20260525-134621` symlink stays untouched (D10).
- **An in-repo drift lint for workflow-skill prescriptions.** See *Follow-ups*.

## Current state and evidence

The setup record in the [implementation log](pypi-publish-2-1-0-impl.md)
carries E1–E13 with their measurements. Those measurements are read-only
probes of the registries, the credentials' shape, the toolchain, the gate,
the release inputs, git and GitHub, the host and the suite. One throwaway-tree
rehearsal of the archived-endpoint `docs relate` pairs was also run. Every
item feeds a decision above or a clause in the
[test matrix](pypi-publish-2-1-0-test-matrix.md). The three that change the
runbook's default path are these:
- the unpinned backend, published today (E4 → D4);
- the absent recorded destination (E9 → D10, Q2);
- the destination-recording side effect of every `install-skill` run (E10 →
  D6).

## Test Strategy For This Milestone

### Visible tests

No product test is added or changed (D1). The full suite is re-run at the
Phase 4 baseline, at the Step 2 tag-target commit and at closeout, and it must
report **1671 passed** each time: the count can move only if a product test
changes, and none does. The suite already pins two things:
- the 2.1.0 version, in four places in `tests/test_packaging.py`;
- the two suite probes, as replica tests run from source.

### Non-product checks

These are explicit workflow gates, run outside pytest's discovery:

- `tests/manual/release_readiness.py`. RED in Phase 2, for exactly the
  `UNRELEASED` heading and the publish-state sentence. GREEN from Phase 3 on.
- `tests/manual/release_probe.py`, run against the following builds:
  - the editable build (sanity);
  - the host 2.0.0 binary, as a control — the 2.1-only checks must fail;
  - the Phase 4 local wheel;
  - the TestPyPI-served wheel, with the version check skipped;
  - the PyPI-served wheel.
- `twine check dist/*` on every build.
- The sha256 and sdist-member comparisons (D4), the input diff since the
  rehearsal (D9), and the credential-hygiene search (D6).
- `docs check .` from the docs root, the INDEX snapshot, and the reference
  byte identity.

### Hidden/generalization categories

The repository is fully visible, so no private cases exist. These are the
generalization targets:
- artifacts served by an index, not built locally — one from TestPyPI, one
  from PyPI;
- the rehearsal-name build, under the M13 and M24 caveats;
- a fresh venv per run, with no repository on the path;
- probe trees outside the repository, including a throwaway copy of this docs
  tree;
- extension-vocabulary trees and a tree with a non-default `date_format`;
- a real 2.0.0 install, for the update notice;
- the host's pipx install path, as opposed to a throwaway venv.

### Property/stateful invariants

- Applying an `install-skill` twice equals applying it once: the re-run is a
  no-op at exit 0. The same holds for a `docs lifecycle` re-run, which writes
  zero bytes.
- The sha relation is transitive across builds: (a) = (b) = (c) = (d) (D4).
- The probe's results are identical across the three builds, apart from the
  rehearsal's version line.

### Mutation-sensitive logic

Mutation tooling is not configured. Phase 2 runs a hand-applied mutation smoke
over the release checks' discriminators, following the M28a and M30
precedent, and records which check kills each mutant:
1. a CHANGELOG copy still headed `UNRELEASED`;
2. a dated heading that keeps the publish-state sentence;
3. a README missing one verb;
4. a 2.0.0 binary, which must fail every 2.1-only probe;
5. a bundled reference copy one byte off its `docs/` spec;
6. a pair of different files fed to the sha comparator, such as the rehearsal
   wheel against the canonical wheel.

### Fuzz targets

Not applicable. There is no new parsing surface, and M30's verb-grammar fuzz
stays in the product suite.

### Benchmark/security/schema checks

- Schema: `twine check`; the `Metadata-Version` recorded (2.5 is expected);
  wheel and sdist manifests checked for the following:
  - no `CHANGELOG.md` in either;
  - the seven skill files in the wheel;
  - no `Requires-Dist`.
- Security: D6's credential hygiene; `twine upload --non-interactive`; the
  served-versus-local sha comparison is the tamper check.
- Benchmark: not applicable.

### Mock policy

- New or expanded mocks: none.
- Justification: not applicable. Every check runs against real artifacts,
  real indexes and real installs.
- Real-path test covering the same behavior: every check is real-path.

## Test Matrix

Link: [pypi-publish-2-1-0-test-matrix.md](pypi-publish-2-1-0-test-matrix.md).
Its *Decision ↔ clause crosswalk* maps each D-id here to the matrix's C-ids.

## Deliverables

Each deliverable names its consumer. The end consumers are users and agents
running `pip install -U docs-cli`, and the Agent Playbook Suite release that
pins 2.1.0.

- [ ] **The release contract, frozen in Phase 1** as *Decisions (Phase 1 —
      BINDING)*: check lists, expected values, command lines, scratch layout
      and stop table. Consumer: Phases 2–10 and the Step reviewers.
- [ ] **`tests/manual/release_readiness.py` and
      `tests/manual/release_probe.py`**, with their RED and control evidence
      and a hand-applied mutation smoke (D5). Consumer: Phases 2, 4, 5 and 8;
      the next publish, through the runbook.
- [ ] **The release inputs:** the CHANGELOG dated with its sentence removed
      (D7), and the README synopses reconciled (D8). Consumer: readers of
      PyPI's long description, the GitHub release notes and the repository.
- [ ] **The pre-publish evidence:**
      - the gate counts;
      - the build and its backend version;
      - the shas;
      - `twine check`;
      - the manifests;
      - the local smoke and probe;
      - the TestPyPI rehearsal and its probe;
      - the canonical-rebuild sha match;
      - GO.

      Consumer: the Step 1 reviewers, and the D2 precondition.
- [ ] **`docs-cli==2.1.0` live on PyPI, with a bit-perfect chain of custody**
      for the wheel and the sdist (D4). Consumer: end users and agents; 2.0.0
      installs, through the update notice; the suite pin bump.
- [ ] **The `v2.1.0` tag and the GitHub release** (D13). Consumer:
      repository readers, and GitHub's *Latest release*.
- [ ] **The served-wheel verification:** the probe's third run, and the suite's
      capability probes reading True / True. Consumer: the suite pin-bump PR's
      guard, and M30's assumption about the probes.
- [ ] **Host integration:**
      - the update notice observed;
      - the host binary at 2.1.0 (D10);
      - the host skill refreshed at `~/.claude/skills/docs`, byte-identical,
        with that destination recorded and the backup symlink untouched;
      - the workflow-skill sweep table (D10).

      Consumer: agents on this host, and the suite PR.
- [ ] **The runbook's *From M31* lessons, plus its body corrections** (D11).
      Consumer: the next publish milestone.
- [ ] **The feedback-log hand-off updated** (D12): items 1–3 discharged with
      evidence, and the suite items left open with the E11 facts and the sweep
      table. Consumer: the suite pin-bump PR and the operator.
- [ ] **Test matrix and adequacy results; completion summaries; the status
      narrative.** Consumer: closeout review and Step 3.

## TDD implementation plan

This is the runbook mapped onto ship-milestone's steps (D3). Each phase keeps
its canonical name, followed by its publish meaning. No phase changes product
code.

**Step 1 — Contract and pre-publish baseline (Phases 1–4).** Branch
`pypi-publish-2-1-0/phases-1-4`. Both providers review it before anything
irreversible.

### Phase 1 — Define Contract — release contract and per-release re-verification

- Objective:
  - Freeze the release contract against D1–D13, which carry the answers to
    Q1 and Q2:
    - each script's check list and expected values, taken from `cli.md`, the
      CHANGELOG's 2.1.0 section, M30's binding decisions and M29's nine
      contracts;
    - the scratch layout and environment (D6);
    - the exact command lines for the build, `twine check`, the rehearsal
      upload and install, the real upload (`--non-interactive`), the downloads
      and the comparisons (D4);
    - the stop table;
    - the sdist download method and the backend-pin mechanism;
    - the Phase 10 runbook correction list.
  - Re-run the runbook's *Per-release re-verification* as a same-day
    re-confirmation of E1–E4.
- Files: this document (*Decisions (Phase 1 — BINDING)*), the implementation
  log and the test matrix.
- Exit:
  - the contract is internally consistent;
  - the re-verification matches setup, or the differences are recorded;
  - no source-tree change;
  - the suite is 1671 GREEN, and `docs check .` exits 0.

### Phase 2 — Write Tests (RED) — release checks and their controls

- Objective: write the two D5 scripts, and prove each one can reject a wrong
  answer before anything is prepared:
  - `release_readiness.py` fails on today's tree for exactly two reasons: the
    `UNRELEASED` heading and the publish-state sentence.
  - `release_probe.py` passes on the editable 2.1.0 build. As a control, run
    against the host 2.0.0 binary, it fails every 2.1-only check and passes
    the 2.0 regression set.
  - The hand-applied mutation smoke (*Test Strategy*) records which check
    kills each of the six mutants.
- Files: `tests/manual/release_readiness.py` and
  `tests/manual/release_probe.py` (both new), the implementation log and the
  test matrix.
- Exit:
  - both scripts are clean under ruff, the formatter and mypy, are
    stdlib-only, and sit outside discovery (the collected count stays 1671);
  - the RED reasons are exactly the intended ones;
  - the control and the mutation smoke are recorded;
  - no product file is touched.

### Phase 3 — Create Data/Fixtures — release inputs and probe trees

- Objective:
  - Prepare what the checks gate: date the CHANGELOG and remove the sentence
    (D7), and reconcile the three README synopses (D8).
  - Confirm that every probe tree is built inline, or copied from committed
    fixtures or this docs tree into scratch, and is never the live tree.
  - Re-run `release_readiness.py`; it is now GREEN.
- Files: `CHANGELOG.md`, `README.md`, the scripts (fixture builders only), and
  the implementation log.
- Exit:
  - readiness is GREEN;
  - the branch's diff touches only `CHANGELOG.md`, `README.md`,
    `tests/manual/` and `docs/`;
  - no version literal moved;
  - the suite is 1671 GREEN.

### Phase 4 — Run Tests (RED Baseline) — pre-publish GREEN baseline: gate, build, smoke, rehearsal

- Objective: produce the evidence Step 1's reviewers judge and D2 requires.
  1. **The gate.** The runbook's *Quality gate*, plus:
     - *Surface parity* — `--help` reconciled with the CHANGELOG surface, and
       the M30 stale-wording grep returning 0;
     - the INDEX snapshot;
     - the reference byte identity;
     - the readiness check.
  2. **The build.** `rm -rf dist/ && .venv/bin/python -m build`, on a clean
     tree, recording the backend version. Record the sha256 of both
     artifacts; that wheel is (a).
  3. **`twine check`** on both artifacts.
  4. **The manifests.** No CHANGELOG in either artifact; the seven skill files
     in the wheel; no `Requires-Dist`; `Metadata-Version` recorded.
  5. **The local smoke.** Install the canonical wheel into a throwaway venv
     (D6), run the runbook's smoke, then `release_probe.py`.
  6. **The TestPyPI rehearsal** under `docs-cli-rehearsal`:
     1. rename `[project] name` and rebuild;
     2. run `twine check`;
     3. `twine upload --repository testpypi --non-interactive`;
     4. install from TestPyPI with `--extra-index-url`;
     5. run `release_probe.py` with the version check skipped;
     6. revert the rename, and confirm `git diff pyproject.toml` is empty;
     7. rebuild canonically and confirm the wheel sha equals (a); this
        rebuild is (b).
  7. **GO or NO-GO**, recorded.
- Files: the implementation log and the test matrix (results). `dist/` is
  git-ignored.
- Exit:
  - every gate is GREEN, with exact counts;
  - the shas and the backend version are recorded;
  - the probe is GREEN on both the local and the TestPyPI-served wheels;
  - the rename is reverted;
  - GO is recorded.

  There is no Phase 4 operator checkpoint, because the risk is Standard. The
  Step 1 dual-provider review is the gate before Step 2 (D2). A review fix
  that touches an artifact input re-runs items 2–7 (D9).

**Step 2 — Publish and post-release (Phases 5–10).** Branch
`pypi-publish-2-1-0/phases-5-10`. It starts only after Step 1's review pass
closes with `final-sync: ready`.

### Phase 5 — Update Base Interfaces — pre-upload gate and tag-target build

- Objective: confirm every D2 precondition at the moment of upload, then build
  the bytes that ship.
  - Re-check:
    - Step 1's review pass is closed;
    - GO is on record;
    - no artifact input has changed since the rehearsal commit (D9);
    - PyPI's `2.1.0` slot is still free;
    - the `~/.pypirc` shape and the toolchain are unchanged;
    - the tree is clean.
  - Re-date the CHANGELOG if the day has rolled (D7).
  - Rebuild canonically at the clean `HEAD`. That commit is the **tag-target
    commit**, and this build is (c).
  - Run `twine check`.
  - Confirm the wheel sha equals (a), using the backend-pin remedy only if it
    reproduces (a).
  - Confirm the sdist members outside `docs/` and `tests/` equal (a)'s sdist
    (D4).
- Files: the implementation log, and `CHANGELOG.md` only if it is re-dated.
- Exit: every precondition is true and recorded. Otherwise, stop with nothing
  uploaded.

### Phase 6 — Implement Offline/Core Path — the real PyPI upload

- Objective:
  - Run `.venv/bin/twine upload --non-interactive dist/*` under D2.
  - Confirm the release is served: the per-version JSON returns 200 and lists
    both filenames, with sha256 digests equal to the local ones. The aggregate
    JSON may lag (M11, M20).
- Files: the implementation log.
- Exit: both files are live with matching digests, or a stop is recorded per
  the error table.

### Phase 7 — Update Tool/Wrapper Layer — served verification and the public release surfaces

- Objective:
  - Install `docs-cli==2.1.0` from PyPI into a fresh venv.
  - Download the served wheel and sdist into fresh empty directories, and
    compare their sha256 values against build (c). Both must be bit-perfect
    (D4).
  - Check that `docs --version` prints `docs 2.1.0`.
  - Then, under D2 and D13: annotate `v2.1.0` at the tag-target commit, push
    the tag, and run `gh release create v2.1.0` with the dated section as its
    notes. That section is extracted with the runbook's `awk`.
- Files: the implementation log.
- Exit:
  - the chain-of-custody table is complete and bit-perfect;
  - `git ls-remote --tags origin v2.1.0` resolves to the tag-target commit;
  - `gh release view v2.1.0` shows the release.

### Phase 8 — Run Tests (GREEN) — the served wheel, end to end

- Objective:
  - Run `release_probe.py` for the third identical time, against the
    PyPI-served wheel, with the version check on.
  - Run the Agent Playbook Suite's capability probes verbatim from its CI
    step, with `PATH` set to the served venv: `lifecycle verb: True` and
    `free-form relate: True`.

    The suite's full guard is **expected to fail** against 2.1.0 until the
    suite retires its stopgap. That failure is the guard working (E11), and
    it is recorded, not treated as a regression.
  - Run `release_readiness.py` at the tag-target commit.
  - Run the full fast gate.
- Files: the implementation log and the test matrix.
- Exit: everything is GREEN, with exact counts, and M30's probe assumption is
  validated against the served wheel.

### Phase 9 — Integrate / Accept / Dogfood — host integration

- Objective:
  1. **Show the update notice reaching a 2.0.0 install.** Run the host 2.0.0
     binary with a scratch `XDG_CACHE_HOME` and the update check enabled. It
     prints the 2.1.0 notice once on stderr, with its exit code unchanged.
     Run this once the aggregate JSON reports 2.1.0.
  2. **Upgrade the host binary** (D10): `pipx upgrade docs-cli`. Verify that
     the host binary prints `docs 2.1.0`, installed from the PyPI index.
  3. **Refresh the host `docs` skill** (D10) with the upgraded binary:
     `docs install-skill --force --dest ~/.claude/skills/docs`. Verify all
     three:
     - `diff -r` against the served wheel's bundle is empty;
     - the recorded destination now names `~/.claude/skills/docs`;
     - the backup symlink is unchanged.
  4. **Run the workflow-skill sweep** (D10). Census the installed suite and
     its source repository for prescriptions 2.1.0 supersedes — hand-edited
     `Lifecycle:` or `Related:`, stopgap references, and any assumption that
     `docs relate` refuses free-form verbs — with counts per file.
  5. **Dogfood:** run `docs check .` on this tree with the upgraded host
     binary.
  6. **Walk the liveness chain:** every artifact, record and check this
     milestone produced has a named consumer.
- Files: the implementation log. Host state outside the repository changes
  only as D10 lists.
- Exit:
  - the notice is observed;
  - the host binary and skill are at 2.1.0, and the backup symlink is
    untouched (D10);
  - the sweep table is recorded;
  - no suite file has changed;
  - no orphan output remains.

### Phase 10 — Quality, Docs, Refactor — runbook lessons, hand-off, closeout docs

- Objective:
  - Write the runbook's *From M31* lessons.
  - Correct the runbook's obsolete body steps, from the list Phase 1 freezes
    (D11). The candidates are:
    - the post-release "impl log stays at root" instruction;
    - the "merge and push `main`" step under ship-milestone;
    - the *Tree state* block's `plan.md` and M6–M9 wording;
    - a missing host step: binary upgrade, skill refresh and sweep;
    - XDG isolation for smoke runs;
    - the release-check scripts as the standing headline probe;
    - D4's backend rule and D9's re-rehearsal rule.
  - Update the feedback-log hand-off (D12), and record the outcome of the
    candidate-convention trial on its entry.
  - Update the status narrative.
  - Write the matrix's final results.
  - Triage taste findings and run the boundary sweep.
  - Clean up scratch.
  - Write the completion summaries in this document and the log.
- Files: `docs/release-runbook.md`, `docs/feedback-log.md`, `docs/status.md`,
  this document, the log, the matrix, and the INDEX with its snapshot.
- Exit:
  - the full gate is GREEN, and `docs check .` exits 0;
  - no placeholders remain;
  - everything that must outlive the archive is in a live document;
  - the milestone is ready for Step 3.

### Step 3 — Simplify and close (post-Phase 10)

Branch `pypi-publish-2-1-0/simplify`.

- `/simplify` covers the only code this milestone adds: the two release-check
  scripts. It is likely a no-op.
- Prove GREEN, then take a clean pre-archive checkpoint.
- Preview the closeout, then apply exactly the same scope:
  `docs archive pypi-publish-2-1-0.md --cascade-dry-run --cascade-only
  'pypi-publish-2-1-0-*'`. The preview must select exactly the two
  companions.
- Run `docs check .`, move the tracker row to `complete`, and update the
  status narrative.
- Re-verify the README's `blob/main/` links after the archive (D8).

## Phase checklist

- [ ] Phase 1 — Define Contract — release contract; per-release re-verification
- [ ] Phase 2 — Write Tests (RED) — release checks; controls; mutation smoke
- [ ] Phase 3 — Create Data/Fixtures — CHANGELOG dated; README reconciled
- [ ] Phase 4 — Run Tests (RED Baseline) — pre-publish GREEN baseline: gate, build, smoke, TestPyPI rehearsal
- [ ] Phase 5 — Update Base Interfaces — pre-upload gate; tag-target build
- [ ] Phase 6 — Implement Offline/Core Path — real PyPI upload
- [ ] Phase 7 — Update Tool/Wrapper Layer — served chain of custody; tag and release
- [ ] Phase 8 — Run Tests (GREEN) — probe and suite probes against the PyPI wheel
- [ ] Phase 9 — Integrate / Accept / Dogfood — update notice; host binary and skill; sweep
- [ ] Phase 10 — Quality, Docs, Refactor — runbook lessons; hand-off; summaries

## Decisions carried from discovery

- **2.1.0 ships through a separate, one-to-one publish milestone** (M30 — D9,
  Q4; M30 *Follow-ups* item 4, registered by the operator as this row).
- **The suite stopgap retires only in the suite release that pins a docs-cli
  carrying M30**, not at this publish (operator, 2026-10-26; M30 *Success
  criteria*).
- **Skill channels** (`CLAUDE.md`). The bundled skill moves with every CLI
  change. Host skills move only at a production ship, with
  `docs install-skill --force` from the published version and a sweep of the
  workflow skills' docs-cli prescriptions.
- **docs-cli is agent-agnostic** (operator, 2026-06-29). Install where the
  operator says, through `--dest` or the recorded destination. Never guess the
  agent, and never inspect or judge an installed skill.
- **The Agent Playbook Suite rides its own release cycle** and is never
  changed ad hoc from a docs-cli milestone (operator policy).
- **`twine>=7.0.0`** (M29 — D1), already in `[dev]`.
- **Runbook lessons this milestone applies:**
  - JSON lag, and tokens validated by use (M11);
  - the rehearsal wheel prints `0.0.0+local` (M13);
  - CHANGELOG ships in neither artifact, and the sdist chain of custody
    (M20);
  - the update notice cannot fire on the rehearsal wheel (M24);
  - the README is a Phase-2-class artifact, and one scripted probe runs
    across all builds (M29);
  - the binary is upgraded together with the skill (M29 *Post-closeout*).
- **Archived endpoints in recognized pairs need `--reason`**, and get an
  audited `Revision:` bullet (M25 — D4; tracker contract).

## Setup questions (Q1–Q2)

Both are **RESOLVED** by the operator (2026-10-28, in this session), each as
recommended. The packets stay as the audit trail. The answers are folded into
D2, D10 and D13, and Phase 1 does not re-open them.

### Q1 — Tag and GitHub release: inside Step 2 under D2, or later?

- **Origin.** The runbook's *Post-release* tags the commit whose tree matches
  PyPI, pushes the tag and creates the release. M29's D2 listed the tag and
  the release among the irreversible actions that needed authorization. The
  operator's 2026-10-28 answer names only the upload. ship-milestone pushes
  only milestone branches, through sync-and-commit, and leaves the merge to
  `main` to the operator. `main` is already public with M30 (E8). `v2.0.0`
  sits at `408ef6c` on `main`, and M30's stack was merged with a merge commit
  (`bf09748`).
- **Why now.** Phase 1 freezes Step 2's action list. An ambiguity here would
  stall Step 2 just after the irreversible upload.
- **Options.**
  - **(A)** Step 2 annotates `v2.1.0` at the tag-target commit on the
    `phases-5-10` branch, pushes it, and creates the release, all under D2.
    The release is complete in one run. The tag points at a branch commit
    until the operator merges; a squash or rebase merge would orphan it.
  - **(B)** Tag locally in Step 2, and push the tag and create the release
    only after the operator merges into `main`. The tag is then always on
    `main`, but GitHub keeps showing 2.0.0 as *Latest* while PyPI serves
    2.1.0.
  - **(C)** Stop after served verification for an explicit go on the tag and
    the release. That is one more round-trip — M24's gated mode, for these two
    actions only.
- **Example.** M29 annotated `v2.0.0` at `408ef6c`, the chain-of-custody
  commit, and pushed it with the release in the same session (M29 Phase 5).
- **Recommendation:** **(A).** It keeps the tag on the exact bytes' commit,
  completes the runbook in one run, and matches the M29 precedent. The only
  cost is that the operator's merge must preserve history.
- **Question.** Does D2's automatic authorization also cover pushing an
  annotated `v2.1.0` tag at the uploaded artifacts' build commit, and creating
  the GitHub release, in Step 2? Or should they wait for your merge (B), or
  for a separate go (C)?
- **Resolution (operator, 2026-10-28): (A), in Step 2.**
  - Right after the PyPI-served verification, push an annotated `v2.1.0` tag
    at the exact commit the uploaded artifacts were built from, and create
    the GitHub release.
  - Both are covered by the automatic authorization. The tag push is a
    recorded exception to pushing only through sync-and-commit.
  - The conductor merges stacks with a history-preserving merge commit, which
    keeps the tag on `main`.

  Folded into D2 and D13.

### Q2 — The host refresh: destination, binary upgrade, backup symlink

- **Origin.**
  - `CLAUDE.md` says to refresh host skills at the production ship, running
    `docs install-skill --force` from the published version.
  - Operator policy says to install where the operator says (`--dest`, or the
    recorded destination) and never to guess the agent.
  - On this host (E9):
    - no recorded-destination file exists;
    - `~/.claude/skills/docs` is a directory, last refreshed by M29;
    - the binary is pipx `docs-cli` 2.0.0;
    - `docs-local-source-backup-20260525-134621` is a symlink to this
      repository's `src/docs_cli/skill`.
  - M29's *Post-closeout* recorded a window in which the host carried a 2.0
    skill and a 1.x binary. Its lesson: upgrade the binary in the same step as
    the skill.
- **Why now.** Phase 9 writes outside the repository, and the destination
  cannot be inferred under the never-guess rule. Phase 1 must freeze it before
  Step 2's planner runs.
- **Options.**
  - **(a) Destination:** `~/.claude/skills/docs`, the existing host install;
    or another directory you name; or skip the skill refresh.
  - **(b) Binary:** upgrade the pipx `docs-cli` to 2.1.0 before the skill
    refresh; or leave the binary to you.
  - **(c) Backup symlink:** leave it untouched; or remove it.
- **Example.** M29 refreshed `~/.claude/skills/docs` from the published wheel
  and pointed the recorded destination at it, while the binary stayed at
  1.8.0. Until the operator upgraded it, the host skill prescribed
  `--cascade-only` to a binary that did not have it. The same gap would recur
  here: the 2.1.0 skill prescribes `docs lifecycle`, which the 2.0.0 binary
  refuses.
- **Recommendation:**
  - **(a)** `~/.claude/skills/docs`. It is the host install M29 refreshed,
    and the directory `CLAUDE.md` names. The refresh also writes it as the
    recorded destination, so M23's update hint can replay it.
  - **(b)** Upgrade, per M29's lesson.
  - **(c)** Leave the symlink. It is operator-owned, docs-cli must not manage
    installed skills, and it resolves to whatever this checkout holds. That
    is the 2.1.0 bundle once the stack is merged.
- **Question.** Should Phase 9 refresh the host skill at
  `--dest ~/.claude/skills/docs`, upgrade the pipx `docs-cli` to 2.1.0 in the
  same phase, and leave the backup symlink alone? Or name a different
  destination, or keep either step for yourself.
- **Resolution (operator, 2026-10-28): refresh and upgrade.** In Phase 9:
  1. `pipx upgrade docs-cli` to 2.1.0, verified as served from PyPI;
  2. `docs install-skill --force --dest ~/.claude/skills/docs`, run with the
     published binary. That directory becomes the recorded destination.

  The backup symlink stays untouched, and the workflow-skill sweep stays
  read-only. Folded into D10.

### Also settled, without a question

These are resolved from the runbook, the tracker contract, operator policy and
precedent, and recorded so that Phase 1 does not re-open them. The conductor
accepted every item below, and the Standard risk level, on 2026-10-28:

- **The risk level is Standard** (see *Risk Level*). High is not proposed.
- **No version bump is needed** (D1, E6), so the M29 editable-reinstall lesson
  does not apply. The editable install already reports 2.1.0.
- **The release checks are committed under `tests/manual/`** (D5). Step 1's
  reviewers must see them, and the runbook asks every release for a probe.
- **Re-rehearsal uses `2.1.0.postN` on the detour project only** (D9).
- **The backend-drift remedy is a per-build pin**, accepted only on a
  reproduced sha (D4).
- **The implementation log archives with the trio** (D11).
- **The suite is untouched**, the sweep is read-only, and the hand-off stays
  open (D10, D12). There is no evidence the operator wants the suite PR done
  here.
- **The candidate convention is adopted as a taste anchor** for this
  milestone's documents. It is a trial, and the feedback-log entry stays open.
- **Both recognized pairs with the archived M30 document are written through
  `docs relate --reason`**, as the tracker contract requires.
- **There is no GitHub issue to answer** (E13), and **`main` does not move at
  publish** (E8).

## Follow-ups recorded for later milestones

| # | Follow-up | Home |
|---|---|---|
| 1 | **The Agent Playbook Suite pin bump to 2.1.0.** Its items:<br>- re-vendor `skills/docs`;<br>- bump `DOCS_CLI_VERSION`;<br>- replace the hand-edit prescriptions with `docs lifecycle` and `docs relate`;<br>- retire the stopgap, whose branch is unmerged;<br>- drop ship-milestone Step 0's up-front approval.<br><br>Its CI guard must then read True / True. | Agent Playbook Suite; the feedback-log 2026-10-26 entry stays open (D12) |
| 2 | **Re-scope the PyPI and TestPyPI tokens to project `docs-cli`.** It rolls forward from M9, now seven releases old. The tokens were copied to this host today. | Operator |
| 3 | **An in-repo drift lint** that diffs the workflow skills' docs-cli prescriptions against the bundled `references/`. It rolls forward from M20, M24 and M29. | Later |
| 4 | **Pin the build backend in `[build-system]`.** Worth doing only if D4's remedy is ever needed: a release whose rebuild drifted would be the evidence. | Later; record in the runbook's lessons if exercised |

## Testing and quality gate

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q
(cd docs && ../.venv/bin/docs check .)
.venv/bin/python tests/manual/release_readiness.py      # Phase 1 freezes the arguments
.venv/bin/python tests/manual/release_probe.py --docs <venv>/bin/docs   # per build (D5)
```

Additional gates:
- the live-INDEX snapshot: `tests/fixtures/expected/docs-INDEX.md` stays
  byte-identical to `docs/INDEX.md`;
- the byte identity of the bundled `references/cli.md` and
  `references/convention.md`;
- the release gate — `twine check`, the D4 comparisons, the D9 input diff and
  the D6 credential-hygiene search.

## Success criteria

- **The release is live and bit-perfect.** `docs-cli==2.1.0` is served by
  PyPI. The chain of custody is bit-perfect for the wheel **and** the sdist,
  and the wheel sha is one value across (a), (b), (c) and the served bytes
  (D4).
- **One probe passes three builds.** The same `release_probe.py` passes the
  local wheel, the TestPyPI-served wheel (version line excepted) and the
  PyPI-served wheel. It fails the 2.1-only checks against the 2.0.0 control.
- **The suite's guard flips.** Against the PyPI-served wheel, the suite's
  capability probes read `lifecycle verb: True` and `free-form relate: True`,
  and both replica tests pass in the suite. This discharges M30 hand-off
  item 2.
- **The release inputs are correct.** The CHANGELOG reads
  `## 2.1.0 — <upload date>`, with no publish-state wording. The README
  matches the shipped surface. `release_readiness.py` passes at the
  tag-target commit.
- **The gate is GREEN.** The full gate passes at the tag-target commit and at
  closeout, with 1671 passed, clean ruff, formatter and mypy runs,
  `docs check .` at exit 0, the INDEX snapshot in lockstep and the mirrors
  byte-identical.
- **Credentials and host state stay clean.** No credential is printed, logged
  or committed, and no smoke run wrote host state (D6).
- **The tag and the release are live** (D13). The annotated `v2.1.0` is on
  the remote at the tag-target commit, and the GitHub release carries the
  dated `## 2.1.0` notes.
- **The host follows the release** (D10):
  - the update notice is observed from a 2.0.0 install;
  - the pipx host binary reports `docs 2.1.0`;
  - the host skill at `~/.claude/skills/docs` is byte-identical to the
    published bundle and is the recorded destination;
  - the backup symlink is untouched.

  This discharges M30 hand-off item 3.
- **The sweep and the hand-off are recorded.** The workflow-skill sweep table
  sits in the feedback-log hand-off, the suite is untouched, and the hand-off
  stays open for the suite release (D12).
- **The runbook carries the *From M31* lessons and its corrections** (D11).
- **The closeout is exact.** The archive selected exactly the trio,
  `docs check .` exits 0 after it, the tracker row is `complete`, and the
  README's `blob/main/` links resolve.
