# M29 — PyPI publish 2.0.0

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-08-15

Related:
- child-of: plan.md
- implements: charter.md
- pairs-with: release-runbook.md
- pairs-with: status.md
- references: feedback-log.md
- depends-on: m25-reciprocal-relationship-integrity.md
- depends-on: m26-safe-archive-selection.md
- depends-on: m27-markdown-body-link-validation.md
- depends-on: m28-move-safe-body-link-rewrites.md
- follows: m28a-archive-date-witness.md
- depends-on: m28a-archive-date-witness.md

## Overview

- Milestone: M29
- Title: PyPI publish 2.0.0
- Surface: runbook-driven publication of the complete M25–M28a relationship and
  link-integrity train as `docs-cli==2.0.0`, followed by host-skill refresh and
  milestone closeout.
- Progress: **Registered release stub (2026-08-10).** Scheduled after durable
  prerequisites M25–M28a and intentionally not marked with a transient
  `blocked-by` edge: the work is planned, not unexpectedly unable to proceed.
  No implementation log or runbook phase has started.

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

M29 is operational, not a normal ten-phase code milestone. Once M25–M28a are
implementation-complete, scaffold the implementation log and run the current
`release-runbook.md`: operator prep, pre-publish gate, TestPyPI rehearsal,
authorized production publish/tag/release, served-artifact acceptance, skill
refresh, and docs closeout.

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
Finding 3's paragraph is still an intention: M28a has no Phase 1.

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
`Updated:` is bumped by the move itself, so a relocated document destroys its
own evidence — which is precisely why `check` had nothing to compare against.
2.0.0 records the archive date as a structured metadata field, making
location-versus-record disagreement a hard error. It fires only when the field
is present, so documents archived before 2.0.0 stay silent rather than failing
on upgrade.

**Declined:** warning when `pairs-with` partners sit in different dated archive
directories. Two documents archived months apart may legitimately carry an edge
between them, so that rule would fire on correct trees. A check that cries wolf
is worse than no check, and the drift it was reaching for is now detected
directly by the date field.

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

## Open questions before activation

1. Whether intermediate local versions are used during M25–M28a or the tree
   moves directly to `2.0.0` in one implementation milestone.
2. Exact operator authorization cadence for irreversible upload/push/tag/release
   actions; default to the M24 “author now, confirm at the gate” pattern.
3. Final archive manifest and any historical active publish logs intentionally
   retained at the root.

## Success criteria

- M25–M28a full gates are GREEN and their completion summaries are accurate.
- Migration guidance is tested on legacy relationship/body-link fixtures.
- Local, TestPyPI, and PyPI artifacts pass integrity and headline acceptance.
- Version/tag/release/CHANGELOG and served bytes agree.
- Published and host-installed skills match the 2.0.0 bundled skill.
- Issue #1's prepared reply is verified against the shipped artifact, posted,
  and the issue closed.
- Docs closeout is edge-clean and `docs check` passes.
