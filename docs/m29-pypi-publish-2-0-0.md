# M29 — PyPI publish 2.0.0

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-08-16

Related:
- parent-of: m29-pypi-publish-2-0-0-impl.md
- child-of: plan.md
- implements: charter.md
- pairs-with: m29-pypi-publish-2-0-0-impl.md
- pairs-with: release-runbook.md
- pairs-with: status.md
- references: feedback-log.md
- depends-on: m25-reciprocal-relationship-integrity.md
- depends-on: m26-safe-archive-selection.md
- depends-on: m27-markdown-body-link-validation.md
- depends-on: m28-move-safe-body-link-rewrites.md
- follows: m28a-archive-date-witness.md
- depends-on: m28a-archive-date-witness.md

> **Activated 2026-08-16**, immediately after M28a merged to `main`
> (merge commit `91cc839`). Every milestone M29 ships is now merged — M25
> (`822e086`), M26 (`393fb53`), M27 (`58955ef`), M28 (`b1ec74b`), M28a
> (`91cc839`) — so the train's last dependency is discharged and nothing but
> the publish itself is outstanding. The operative checklist is
> [release-runbook.md](release-runbook.md); this milestone doc gives the
> publish work a named home, exit criteria, and the decisions setup froze. The
> per-phase record lives in
> [m29-pypi-publish-2-0-0-impl.md](m29-pypi-publish-2-0-0-impl.md).

## Overview

- Milestone: M29
- Title: PyPI publish 2.0.0
- Surface: runbook-driven publication of the complete M25–M28a relationship and
  link-integrity train as `docs-cli==2.0.0`, followed by host-skill refresh and
  milestone closeout.
- Progress: **Active — milestone setup complete 2026-08-16; no runbook phase
  started.** Setup ran the read-only half of the runbook's Phase 1 and Phase 2
  gates on the merged tree and recorded seven pieces of measured evidence
  (**E1–E7**) in the implementation log. Six say go: the `2.0.0` slot is free
  on both indexes, credentials and `gh` scopes are intact, the tree-wide gate
  is green at **1504 passed**, and all eight v2.0 headline contracts hold
  against a locally built wheel. **One is a blocker, and it is in the toolchain
  rather than the package** — `twine 6.2.0` rejects the `Metadata-Version: 2.5`
  artifacts this tree now builds, which **D1** resolves by upgrading to
  `twine>=7.0.0` at Phase 2. The three open questions this stub carried are
  **RESOLVED** as **D1–D4** below.

### Goal

Ship the v2.0 safety contract with a verified upgrade path: users can diagnose
and repair reciprocal edges, archive only explicit selections, detect broken
local body links, and move/archive without recreating that damage.

## Planned release scope

- M25 — reciprocal semantics, hard validation, `docs relate`, archived audit.
- M26 — safe preview + explicit archive selection and batch preflight.
- M27 — local Markdown body-link validation and legacy upgrade handling.
- M28 — move/archive-safe body-link rewrites, plus the post-plan strand-check.
- M28a — structured archive-date witness and its drift rule.
- Breaking-change and migration guide for new check failures and retired unsafe
  cascade behavior.
- Post the prepared reply to GitHub issue #1 and close it (see *Issue #1
  closeout* below).
- Served-wheel contract verification for every headline workflow.
- Published bundled skill/reference parity and host-machine skill refresh.

## Why 2.0.0

The train intentionally changes existing automation: previously one-sided
recognized edges can become hard check failures, and bare `--cascade` no longer
writes related documents. These safety improvements are compatibility breaks
for a public 1.8.0 CLI, so the release is planned as a SemVer major rather than
an additive 1.9.0.

## Runbook shape

M29 is operational, not a normal ten-phase code milestone. The sections of
[release-runbook.md](release-runbook.md) **are** the phases (the M9 / M11 /
M13 / M17 / M20 / M24 shape). Both prerequisites are now discharged: M25–M28a
are implementation-complete and merged, and the implementation log is
scaffolded.

### Phase plan

**Phase 1 — Operator one-time prep.** Re-verify rather than establish: the
accounts and tokens have shipped six releases. Setup already measured every
probe (E1, E2) and found nothing to fix, so this phase is a same-day
re-confirmation that the `2.0.0` slots are still free on PyPI and
`docs-cli-rehearsal`, `~/.pypirc` is still `600` with both token sections, and
`gh` still holds `repo`.
*Exit:* every probe re-confirmed on publish day; no token rot.

**Phase 2 — Pre-publish prep.** The only phase that changes the source tree,
and it carries three edits plus one toolchain fix:

1. **Upgrade `twine` to `>=7.0.0` first** (**D1**) — the current 6.2.0 cannot
   check this tree's artifacts at all (E3), so every later gate is blocked
   behind it.
2. **The single version bump** `1.8.0` → `2.0.0` in `pyproject.toml`, in
   lockstep with the `tests/test_packaging.py` A3 pin (E7). `__version__` needs
   no edit — it is read at import time via `importlib.metadata` (M12's version
   SoT).
3. **Date the CHANGELOG**: `## UNRELEASED` → `## 2.0.0 — <publish date>`,
   dropping the "package version deliberately stays 1.8.0" note, which is the
   M11 lesson about publish-survival wording applied to a heading that was
   authored knowing it would be renamed.
4. **The `README.md` refresh** (see below) — it is the PyPI project page, so it
   ships with the artifact and cannot wait for the closeout.

Then the full gate: pytest, ruff, ruff format, mypy, `docs check`, index
idempotence, INDEX-vs-fixture, surface parity, a clean rebuild into `dist/`,
`sha256sum` of both artifacts into the log as the chain-of-custody anchors, and
`twine check`.
*Exit:* gate green at the bumped version; both artifacts PASS `twine check`;
shas recorded; local-install smoke re-run against the 2.0.0 wheel with the
eight headline contracts of E5.

**Phase 3 — TestPyPI rehearsal.** Upload under the `docs-cli-rehearsal` detour
name (the bare name is still squatted — E2), install from TestPyPI, re-run the
headline contracts against the *served* wheel, revert the rename, rebuild
canonically, and confirm the wheel sha is byte-identical to Phase 2.
*Exit:* served-artifact smoke passes; rename reverted; `git diff pyproject.toml`
empty; **GO** recorded.

**Phase 4 — Real PyPI publish.** Irreversible, and gated on explicit operator
authorization (**D2**). Commit the dated CHANGELOG, push `main`, rebuild
canonically at the tag-target commit, `twine check`, upload, install from PyPI,
and verify **chain of custody**: the PyPI-served wheel and sdist must be
byte-identical to the local artifacts.
*Exit:* `docs-cli==2.0.0` live; chain of custody bit-perfect or the deviation
recorded; headline contracts pass against the PyPI-served wheel.

**Phase 5 — Post-release.** Annotated `v2.0.0` tag at the chain-of-custody
commit, GitHub release with the `## 2.0.0` notes, **host-machine skill
refresh** (`docs install-skill --force` from the published version, then sweep
the workflow skills for the new surface — the CLAUDE.md policy makes production
ship the only time host skills move), the **issue #1 reply** verified against
the shipped artifact and posted, then the docs closeout and the archive
manifest of **D3**.
*Exit:* tag + release live; host skills byte-identical to the published
bundle; issue #1 closed; `docs check` exit 0 after the closeout archive; the
README's `blob/main/…` links re-verified **after** that archive (D4).

## Phase checklist

- [ ] Phase 1 — Operator one-time prep
- [ ] Phase 2 — Pre-publish prep (twine upgrade, version bump, CHANGELOG date, README refresh, gate, build)
- [ ] Phase 3 — TestPyPI rehearsal
- [ ] Phase 4 — Real PyPI publish (operator-authorized)
- [ ] Phase 5 — Post-release (tag, release, skill refresh, issue #1, closeout)

## `README.md` refresh (routed here 2026-08-15 by M28's Step-2 review)

`README.md` is outside every milestone's surface-parity gate — it is not in
D8's list, it is not mirrored into the bundled skill, and no test reads it — so
nothing surfaces its staleness at any gate except this one. It is also the
first thing a PyPI visitor and a GitHub visitor see, which makes the publish
the right place to fix it. Known items, all verified 2026-08-15:

- **The `## Commands` block omits three shipped verbs**: `docs relate`
  (M25 — the repair verb for a rule that is a *hard error* at 2.0, so an
  adopter hitting `missing-inverse` finds no repair on the front page),
  `docs stamp` (M15) and `docs project rename|set` (M12).
- **Re-verify every `blob/main/…` link.** One was already dead —
  `docs/m8-adoption-workflow.md` has lived under `docs/archive/2026-05-25/`
  since M8's closeout — and it was fixed inside M28 rather than routed here,
  because M28's own subject is link integrity and shipping a 2.0.0 whose front
  page carries a dead documentation link would be self-refuting. Re-measured at
  setup: **all 8 resolve today**, M28's repair included; the M25–M28a closeout
  **archives more documents**, so they must be re-checked after that archive
  runs, not before (**D4**).
- **The feature summary predates the v2.0 train.** It describes neither the
  reciprocal-edge rules, the body-link rules, nor the move-safe rewrites — and
  it never says that bare `--cascade` is retired, which is the one change most
  likely to break an existing caller.
- **Added at setup (E6): the "Claude Code skill" wording survives here alone.**
  `README.md` says "Claude Code skill" in **three** places (lines 51, 60, 67)
  while `src/docs_cli/` carries **zero** — M23 neutralised the whole shipping
  surface to "agent skill" and README, being outside the gate, was never swept.
  This is not cosmetic: `readme = "README.md"` makes this file the **PyPI
  project page**, so 2.0.0 would publish a front page contradicting the tool's
  own agent-agnostic stance.

The `README.md` edits land in **Phase 2, not the closeout** — it ships inside
the artifact as the PyPI long description, so it must be correct *before* the
upload, not after it. Only the `blob/main/…` re-verification belongs to the
closeout, because the closeout's own archive step is what can break those links
again (D4).

## Issue #1 closeout

GitHub issue #1 (https://github.com/ArtRichards/docs-cli/issues/1) reported the
four defects that shaped the back half of this train. It was filed against
released 1.8.0, so **every fix is unreleased until this milestone ships** — the
reply is posted at publish, not before. Its verified per-finding analysis is in
`feedback-log.md` under the 2026-08-15 entry.

**Before posting, verify every claim against the artifact that actually
shipped.** This draft was written on 2026-08-15, when M28 and M28a were
registered stubs with no Phase 1. Any statement about their behaviour is an
intention, not a fact, until their contracts are frozen and GREEN. In
particular, finding 3's field name must match what M28a froze. Delete
or correct anything the implementation changed; do not post a claim the code
does not support.

**Finding 1's and finding 4's paragraphs were rewritten on 2026-08-15**, when
M28 went implementation-complete, because the draft as written stated the
pre-amendment predicate — a blanket refusal that M28's own measurements showed
refuses an ordinary milestone closeout — and claimed it "self-cancels for the
legitimate case", which is the exact sentence that measurement falsified.

**Finding 3's paragraph was rewritten at M29 setup (2026-08-16)**, when M28a
went implementation-complete and merged. It is no longer an intention: the
field M28a froze is **`Archived:`**, the rule is `archive-date-drift`, and the
milestone shipped a **second leg the draft never mentioned** — `docs mv`
refuses a move between two different dated archive directories, which is what
actually reaches the 46 documents this tree archived before the field existed.
A reply that described only the field would have understated the fix and left
the reporter's own scenario — a relocation, not a fresh archive — sounding
unaddressed for legacy trees. The revised paragraph is verified against the
built wheel (impl log E5), not against the plan.

Post it with `gh issue comment 1 --body-file <path>`, then close the issue.

````markdown
Closed by `docs-cli 2.0.0`. All four findings are addressed; one sub-request is
declined, with reasoning below.

Thanks for the dry-run discipline in the report — `--cascade-dry-run` before a
bare cascade is exactly what it exists for, and it is why this is a bug report
rather than a recovery.

## 1 — `--cascade` follows `child-of` upward and archives the live parent

Fixed, in two parts.

Bare `--cascade` is **retired**. It refuses at exit 2 before touching the
filesystem and writes nothing. A write that includes related documents now
requires an explicit `--cascade-only GLOB` scope, whose complete plan is
validated before the first byte moves.

Scope alone was not enough. A glob is a syntactic filter and cannot know what it
selects, so `--cascade-only '*'` would still have reached the live parent
through the target's outgoing `child-of` edge. 2.0.0 therefore also validates
the plan's **consequences**, before the first byte moves, in two parts:

- **It refuses** when a still-active document outside the plan declares itself
  `child-of` a document the plan would archive — a parent archived out from
  under a live child, which is exactly what you hit. Exit 2, both ends named,
  zero bytes written, in all three archive shapes including a plain
  `docs archive FILE`.
- **It reports, and does not refuse,** every *other* still-active inbound
  reference into the newly-archived set — any other `Related:` verb and every
  body link — on stderr and in a `strands` array in the `--json` record.

That split is deliberate, and measuring it is what produced it. The obvious
rule — refuse whenever the plan would leave *any* still-active document
pointing at a newly-archived one — was implemented and measured against a real
tree, and it refuses an ordinary milestone closeout: archiving one completed
milestone pair leaves 16 deliberate references behind, from the tracker, the
roadmap, and the neighbouring milestones, and every one of them is *supposed*
to survive. A check that fires on correct work is one people route around, so
only the `child-of` direction refuses and the rest is delivered to you as data.

Your suggested fix — follow *incoming* `child-of` edges rather than the
outgoing one — is an improvement, but it does not close the hole on its own:
`pairs-with` is symmetric, and milestone documents legitimately carry
cross-milestone `pairs-with` edges, so a live parent or sibling stays reachable
that way. Validating consequences is direction-agnostic and covers the
`child-of`, `pairs-with`, and body-link routes together, and it leaves the
candidate set itself untouched.

## 2 — `--cascade` re-archives already-archived docs and re-dates them

Fixed. An already-archived candidate is reported `ineligible (already
archived)` and stays excluded even under `--cascade-only '*'`. No archive
operation relocates an archived document.

## 3 — `docs check` exits 0 after both of the above

Fixed in two parts, with one sub-request declined.

**Links.** `docs check` now reads local Markdown body links. A live document
whose prose link points at a now-archived path is a hard `broken-body-link`
error at exit 2 — your exact scenario.

**Archive dates.** The root cause was that the dated directory is the *only*
record of when a document was archived: `Archived-reason:` is free text and
written to the primary only, and `Updated:` is bumped by the move itself, so a
relocated document destroys its own evidence — which is precisely why `check`
had nothing to compare against. 2.0.0 fixes that from both ends.

**It records the date.** `docs archive` now writes an `Archived:` field to
every document the operation moves — not just the primary, which matters
because your case was a cascaded trio split across two dated directories — and
`docs check` gains `archive-date-drift`: a hard error, exit 2, when a
document's recorded date disagrees with the dated directory it sits in. The
rule fires **only when the field is present**, so documents archived before
2.0.0 stay silent and a 1.x tree gains zero findings on upgrade.

**It also prevents the move.** A field can only witness for documents archived
after it existed, so `docs mv` now refuses outright when a move's source and
destination are different dated archive directories — decided from the two
paths alone, before any write, at exit 2 with both dates named. That leg needs
no field, so it protects documents archived long before 2.0.0 as well. To
correct a genuinely mis-dated archive, move the file by hand, fix its
`Archived:` line, and re-run `docs check`; the refusal message says so.

Worth naming plainly, since it was the sharpest thing your report surfaced: the
relocation you described completed at exit 0 with `docs check` clean right up
until this release.

**Declined:** warning when `pairs-with` partners sit in different dated archive
directories. Two documents archived months apart may legitimately carry an edge
between them, so that rule would fire on correct trees — measured on this
repository's own tree, it emits 7 findings, every one of them a deliberate
cross-milestone edge. A check that cries wolf is worse than no check, and the
drift it was reaching for is now detected directly by the date field and
prevented by the refusal.

**One divergence worth flagging.** You asked for the link check to be opt-in
(`docs check --links`), reasoning that some trees deliberately keep unrepaired
links inside `archive/` as dated records. It ships **on by default and uniform
across archived documents**. The reasoning: this damage class is produced by
`docs archive` itself, so exempting archives would leave the tool silent about
breakage it caused, in exactly the place it accumulates. If you have a tree with
deliberately stale archive links, it will fail `docs check` on upgrade — the
migration notes carry the repair recipe, and the repository's own tree needed
140 such repairs.

## 4 — link rewriting covers `Related:` but not body prose

Fixed. `docs mv` and `docs archive` now rebase local Markdown destinations for
both classes you identified: incoming links whose target moves, and links inside
a referring document that itself moves. Labels, titles, fragments, and quoting
form are preserved, and plain text and code are left alone.

Your lighter alternative — document the boundary and ship a `--report-links`
mode instead — was weighed and **declined as a design, while its output was
adopted**. Declining it was forced by the release itself: 2.0.0 makes a broken
prose link a hard `docs check` error, so "declare them out of scope" would mean
the tool knowingly shipping trees that fail its own gate — measured on this
project at 42, 13 and 6 findings for a rename, a single archive and a real
milestone closeout. A *report* also leaves the repair to the same caller whose
blind spot produced the problem.

What you actually wanted — visibility before and after — ships as a plan record
on **both** verbs rather than as a separate mode. `docs mv` gains a real
`--dry-run` that names every planned rewrite, and a `--json` record; `docs
archive --json` gains the same `rewrites` section plus the `strands` array
above. Both records have the same shape for a preview and a real apply, so you
can diff them.

## Upgrading

Both new check rules are hard errors, so a tree carrying pre-existing damage
will fail `docs check` immediately after upgrading. That is intentional: the
damage predates the upgrade, and the release notes carry the repair recipes for
each rule. Nothing repairs prose links automatically on upgrade — from 2.0.0
onward `mv` and `archive` keep them correct, but historical breakage is
reported, not fixed.

## What this report changed

Two things in the release came directly from this issue: the plan-consequence
strand-check in finding 1, and the structured archive-date field in finding 3.
Neither was in the plan before it was filed.
````

## Closeout intent

- Archive M25–M28a plan/log pairs plus the M29 milestone doc only after the
  production release and served-artifact acceptance succeed.
- Keep the M29 implementation log, release runbook, and project status active,
  following M17/M20/M24 precedent.
- Update Agent Playbook Suite only after `docs-cli==2.0.0` is available; that
  cross-repository implementation is not part of M29.

## Decisions recorded at setup (BINDING)

The three questions this stub carried into activation are **RESOLVED**. Two
were settled by what actually happened during the train; one is a new decision
forced by a measurement.

**D1 — the release toolchain upgrades to `twine>=7.0.0` before the Phase 2
gate.** New at setup, and the only blocker found. `twine 6.2.0` monkeypatches
`packaging.metadata._VALID_METADATA_VERSIONS` to a list capped at `2.4`
(`twine/package.py:32`), so it rejects the `Metadata-Version: 2.5` artifacts an
unpinned hatchling now builds — while the installed `packaging 26.2` accepts
`2.5`, PyPI accepts `2.5` (hatchling's own wheel, uploaded 2026-08-11, serves
it), and `twine 7.0.0` passes both of this tree's artifacts. Upgrading the
checker is therefore the correct fix; **pinning hatchling back to a `2.4`-era
release is explicitly rejected**, because it would freeze the build backend to
work around a stale checker and leave the real constraint undocumented. The
runbook's *Artifact build* note — that `twine 6.2.0` "was the version
smoke-tested at M6 ship and re-used unchanged through M11" — is superseded by
this decision, and the runbook gets both the corrected instruction and a
*Cumulative lessons* entry at Phase 5. Note the shape of the trap: the runbook
says to install twine "if not already present", and 6.2.0 **is** present, so
the default path skips the upgrade and hits the failure at the gate.

**D2 — irreversible actions follow M24's "author now, confirm at the gate"
pattern.** (Resolves stub question 2 at its own stated default.) Everything up
to and including the TestPyPI rehearsal proceeds unattended; the **upload to
PyPI, the `main` push, the `v2.0.0` tag, the GitHub release, and the issue #1
comment** each stop for explicit operator authorization at the Phase 4 / Phase
5 gate. Nothing irreversible is done on the strength of this document alone.

**D3 — the closeout archive manifest is the five plan/log pairs plus this
milestone doc; the M29 log stays active.** (Resolves stub question 3.) Eleven
documents move to `archive/<publish-date>/`: `m25-*`, `m26-*`, `m27-*`,
`m28-*`, `m28a-*` — plan and log for each — and
`m29-pypi-publish-2-0-0.md` itself. `m29-pypi-publish-2-0-0-impl.md` stays
`Lifecycle: active` at the root alongside `m17-`, `m20-` and
`m24-pypi-publish-impl.md`, which is the deliberate M17/M20/M24 precedent: the
publish record outlives the milestone that produced it. `release-runbook.md`,
`status.md`, `plan.md` and the specs stay active throughout. The archive runs
**only after** served-artifact acceptance passes.

**D4 — the README's `blob/main/…` links are re-verified after the closeout
archive, and the rest of the README refresh lands in Phase 2.** All 8 resolve
today, but D3's archive is exactly the operation that can break them, and M28's
rewriter does not reach `README.md` — it is outside the docs tree. The other
README items ship inside the artifact as the PyPI long description, so they
cannot wait for the closeout.

**Answered by the train itself (stub question 1): no intermediate versions.**
M25 — D6 fixed the package at `1.8.0` through M25, M26, M27, M28 and M28a, with
every CHANGELOG entry accumulating under `## UNRELEASED`. M29 performs the
single bump to `2.0.0`. This is now a fact about the merged tree rather than an
open choice.

## Success criteria

- M25–M28a full gates are GREEN and their completion summaries are accurate.
- `twine>=7.0.0` is in place and both artifacts PASS `twine check` (D1).
- Migration guidance is tested on legacy relationship/body-link fixtures.
- Local, TestPyPI, and PyPI artifacts pass integrity and headline acceptance —
  the eight contracts of the impl log's E5, re-run against each artifact.
- Version/tag/release/CHANGELOG and served bytes agree; chain of custody is
  verified against the PyPI-served wheel **and** sdist.
- `README.md` is refreshed before the upload and its links re-verified after the
  closeout archive (D4).
- Published and host-installed skills match the 2.0.0 bundled skill.
- Issue #1's prepared reply is verified against the shipped artifact, posted,
  and the issue closed.
- Docs closeout is edge-clean and `docs check` passes.
