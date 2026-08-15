# docs — Implementation Plan

Lifecycle: active
Role: plan
Project: docs
Updated: 2026-08-16

Related:
- implements: charter.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: status.md
- parent-of: archive/2026-05-20/m1-parser-and-index.md
- parent-of: archive/2026-05-25/m7-migration-accuracy.md
- parent-of: archive/2026-05-25/m8-adoption-workflow.md
- parent-of: archive/2026-05-25/m9-pypi-publish.md
- parent-of: archive/2026-05-28/m12-project-rename.md
- parent-of: archive/2026-05-29/m13-pypi-publish.md
- parent-of: archive/2026-06-03/m14-robustness-agent-native.md
- parent-of: archive/2026-06-03/m15-agent-native-authoring.md
- parent-of: archive/2026-06-01/m16-bundled-docs-skill-quality.md
- parent-of: archive/2026-06-03/m17-pypi-publish.md
- parent-of: archive/2026-06-12/m18-archive-edge-integrity.md
- parent-of: archive/2026-06-12/m19-post-edit-validation.md
- parent-of: archive/2026-06-12/m20-pypi-publish.md
- parent-of: archive/2026-07-03/m21-update-check.md
- parent-of: archive/2026-07-03/m22-root-placement-guidance.md
- parent-of: archive/2026-07-03/m23-agent-aware-install-skill.md
- parent-of: archive/2026-07-03/m24-pypi-publish.md
- parent-of: m25-reciprocal-relationship-integrity.md
- parent-of: m26-safe-archive-selection.md
- parent-of: m27-markdown-body-link-validation.md
- parent-of: m28-move-safe-body-link-rewrites.md
- parent-of: m28a-archive-date-witness.md
- parent-of: m29-pypi-publish-2-0-0.md

## Sequencing

Three milestones to v1, then a migration helper, then a Claude Code
skill wrapper. v1.1 picks up with packaging, then migration
hardening + adoption workflow. v1.4 adds adoption-flow polish +
1.3.0 carry-overs (M10) and ships them as a publish-only
milestone (M11). v1.5 adds the operator-facing `docs project
rename` verb plus burn-down of the M11 warts and a packaging
SoT refactor (M12), then a publish milestone (M13). v1.6 splits
the post-1.5.0 robustness + agent-native work into two
implementation milestones — M14 (robustness + autonomous
archive) and M15 (agent-native doc authoring) — then ships both
via the publish milestone M17 (**docs-cli 1.6.0 shipped to PyPI
2026-06-03**, batching M14 + M15 as M9 batched M6+M7+M8). M16 is
an orthogonal bundled-skill quality upgrade on a separate track
(already implementation-complete).
M18 is a standalone archive-edge-integrity correctness fix that unblocked
archiving the completed-milestone backlog (implementation-complete
2026-06-03, including its Phase-9 archival payoff); it depended on nothing
and is independent of the M17 publish.
M19 (v1.6.5) is a post-edit-ergonomics feature milestone: `docs touch
--check` folds validation into the touch loop, a `.docs.toml [check]
stale_days` key makes the stale window per-tree configurable, and the stale
`docs new --body-from` help string is corrected. It built 1.6.5 locally;
the publish was a later operator-driven milestone (the M14+M15→M17 pattern).
M20 was that publish milestone — the publish-only counterpart to M19,
shipping **docs-cli 1.6.5 to PyPI 2026-06-12 one-to-one** (as M13 shipped M12
and M11 shipped M10; M9 and M17 were the batched shapes). It ran the
release-runbook on `main` (M17 precedent — a publish milestone has no TDD
code phases), and its closeout NEWLY refreshed the host-machine skills
(`docs install-skill --force` + a workflow-skill sweep that caught + fixed one
stale `--body-from` reference in `project-foundation`) per the CLAUDE.md
skill-update-flow policy (production ship is when `~/.claude/skills/`
refreshes) and swept the M18 + M19 milestone-doc pairs (plus M20's own
milestone doc) into `archive/2026-06-12/`.
M21 (v1.7.0) is the feature milestone — lifecycle **`draft`**,
**implementation-complete (all 10 TDD phases done, 2026-06-29; 1.7.0 built
locally — publish is a later milestone)** on branches `m21/phases-1-4` (RED
baseline) + `m21/phases-5-10` (implementation) (scaffolded 2026-06-12,
**re-scoped to CLI-only 2026-06-29**; full suite **604 GREEN** (+4 Step-2 review
fold-in), gate clean,
`docs --version` = `docs 1.7.0`). It
adds docs-cli's **first network surface**: a once-per-24h,
fail-silent PyPI version check (stdlib `urllib` only, 1.0s timeout,
24h-cache-gated under a three-key `{last_check, latest_version, last_notified}`
cache, zero-dependency wheel preserved) that emits ONE STDERR line nudging the
user/agent to update **the CLI** (`pip install -U docs-cli`; wording
`docs: update available <current> -> <latest> — run: pip install -U docs-cli`).
The notice is STDERR-only, never alters the exit code, suppressed under
`--quiet`/`--json`/`CI`/`DOCS_CLI_NO_UPDATE_CHECK`/`DO_NOT_TRACK` (a user-level
config opt-out is DEFERRED out of v1.7.0 — OQ-5/5a), but **deliberately shows on
non-TTY** (inverting gh's TTY rule — the agent is the actor who performs the
update). The former skill-drift notice (D5) + the dual-action `docs
install-skill --force` half are **CUT** (the re-scope — docs-cli must not
inspect/manage the user's installed skills nor assume Claude Code); the skill
story moves to the follow-on **M23 (agent-aware install-skill + recorded-dest
skill-refresh hint)**. It builds **1.7.0** locally (minor bump — additive; 1.6.5
was the operator-decreed patch exception); the publish is a later
operator-driven milestone (the M19→M20, M14+M15→M17 pattern). Depends on
nothing. **OPEN QUESTIONS netted out — none outstanding** (OQ-1..OQ-9 RESOLVED
2026-06-12; OQ-6 "ship D5" REVERSED by the re-scope); milestone-setup is
complete and Phase 1 (Define Contract) is next.

M23 (v1.8.0) is the follow-on that restores the skill-refresh nudge cut from
M21 — **implementation-complete (all 10 TDD phases done 2026-07-02; 1.8.0 built
locally — publish is a later milestone), lifecycle `draft`** on branches
`m23/phases-1-4` (RED baseline) + `m23/phases-5-10` (implementation → dogfood →
closeout); full suite **636 GREEN**, gate clean, `docs --version` = `docs
1.8.0`. It makes `docs install-skill` **agent-aware** via `--dest` (the source
of truth, agent-agnostically), **records** the resolved dest to a small
per-user state file so future runs / M21's update notice can **replay** it
(replay/remember is allowed; content-inspection is NOT), neutralises the
"Claude Code skill" framing → "agent skill", and then extends M21's update
notice with an agent-appropriate skill-refresh hint pointed at the recorded
dest. Non-TTY runs never block on a prompt. Out of scope: multi-agent skill
formats and agent auto-detection (don't guess the agent — ask on a TTY or take
`--dest`). Depends on M21 (extends its notice channel). **The four OPEN
QUESTIONS are resolved** (OQ-1 non-TTY default; OQ-2 separate `XDG_STATE` state
file; OQ-3 last-write-wins single dest; OQ-4 1.8.0) — OQ-1/OQ-2 resolved
**provisionally while the operator was away**, flagged for confirmation at
branch review.

The next train is **v2.0**, registered 2026-08-10 from the completed
relationship/archive/link-integrity discovery in `feedback-log.md`. M25 adds
strict reciprocal semantics plus explicit `docs relate` repair. M26 makes
archive selection safe and explicit. M27 introduces bounded local Markdown
body-link validation and the controlled legacy-repair policy; M28 reuses that
scanner to keep `mv`/archive operations link-safe. M28a, inserted 2026-08-15
from issue #1, gives an archived document a structured witness for its own
archive date so a relocated one is detectable rather than invisible. M29
publishes the implementation milestones together as **docs-cli 2.0.0**. The
major version is
intentional: new hard check failures and refusal of unsafe bare `--cascade`
change existing automation. M25 is **implementation-complete and merged to
`main`** (2026-08-12) — Phases 1–4 (contract + RED baseline, 2026-08-11) and
Phases 5–10 (interfaces, core, CLI/docs/skill surface, GREEN gate, dogfood,
closeout) plus the Step-3 `/simplify` pass, **777 GREEN**. It stays
`Lifecycle: active` until M29 publishes the train. **M26 is
implementation-complete** (2026-08-13) — milestone setup 2026-08-12 on
`m26/milestone-setup`, with a full ten-phase task plan, an implementation log,
and **all seven setup questions resolved** before Phase 1. Step 1
(Phases 1–4, `m26/phases-1-4`) froze the contract in `cli.md`,
`convention.md`, and the milestone's *Decisions (Phase 1 — BINDING)* section,
wrote the RED suite over four new `archive-*` fixture trees, and captured the
classified baseline of **884 collected, 104 failed, 780 passed** with 769 of
the 777 pre-existing ids mechanically proven still GREEN, after a
same-instance audit and an independent fresh-eyes review whose blocker and six
should-fixes are folded in. Step 2 (Phases 5–10, `m26/phases-5-10`) landed the
models, the planner and its validate-all-first pre-flight, the CLI in the
frozen nine-step check order, every parallel surface, the GREEN gate
(**888 passed**, 774 of the 777 pre-existing ids proven present and passing,
3 deliberately removed, 114 new at that gate), the dogfood on a throwaway copy of this
tree, and the simplify-and-close pass; the same-instance audit and the
fresh-eyes review fold-in added seven more locks — including the fix for the
review's one blocker, a primary resolving outside the docs root being archived
into the tree — so the suite stands at **895**. It stays `Lifecycle: active` until the
M29 closeout. **M27 is implementation-complete (2026-08-14)** — milestone setup completed 2026-08-14
on `m27/milestone-setup`, with a full ten-phase task plan, an implementation
log, eight pieces of read-only tree evidence (E1–E8), and **all seven setup
questions resolved** before Phase 1. Two of them shaped the milestone: **Q1**
keeps the rule uniform across archived and active documents and repairs the
tree's 139 archived breaks once, because the breakage class is produced by
`docs archive` itself and `docs/` ships in every sdist; and **Q5**, resolved
against the setup recommendation and then amended, keeps `docs check`
hermetic — it never stats outside its own root — while still **reporting** a
destination that leaves the tree, via a second rule
`outside-root-body-link` decided by path arithmetic. **Step 1 (Phases 1–4)
is complete** on `m27/phases-1-4` (2026-08-14): the contract is frozen in
`cli.md`, `convention.md` and the milestone's *Decisions (Phase 1 —
BINDING)*, the RED suite is written, six `bodylink-*` fixture trees are
committed, and the classified RED baseline stands at **1079 collected, 137
failed, 942 passed** — after a same-instance audit and an independent
fresh-eyes review that found no blockers, whose fixes are recorded in the
log — with all 895 pre-existing ids mechanically proven present and passing.
**Step 2 (Phases 5–10) is complete** on `m27/phases-5-10` (2026-08-14): the
pure scanner landed with no rule wired, then both rules were wired into
`check_doc` **in the same commit as** the D6 live-tree repair — 140
occurrences across 30 documents, spliced by offset and proven by six
independent checks — every parallel surface was reconciled, the suite went
**fully GREEN at 1079 passed / 0 failed with no test touched to get there**
(**1087** after the Step-2 audit and the fresh-eyes review added eight locks alongside the seven real defects they found),
the documented upgrade recipe was walked from `docs check --json` alone on a
throwaway pre-repair copy and reached the same destination tokens, and the
`/simplify` pass closed `architecture.md` and `test-strategy.md`. `docs check
--root docs` now exits 0 over a tree that carried 139 broken body links and
one escaping link when the milestone opened. No version bump; **M28** inherits
the `BodyLink` span contract plus the guarantee that a clean tree
contains no escaping destination.
**M28 is implementation-complete — all ten TDD phases done (2026-08-15)**,
Step 1 (Phases 1–4) on `m28/phases-1-4` and Step 2 (Phases 5–10) on
`m28/phases-5-10`. Step 2 landed the pure planner seam as three insertions
into `cli.py` with no verb wired (Phase 5), inverted `_cmd_mv` to
plan-before-move, added `docs archive`'s steps 5b / 8b / 8c / 8d, threaded each
moving member's planned text into `_archive_one` so the contract stays at one
`atomic_write` per document, and **deleted** `_rewrite_referring_edges` as
superseded by `apply_move_plan` (Phase 6); reconciled every parallel surface
including the bundled skill's now-false "prose links are not rewritten"
sentence (Phase 7); proved the gate at **1333 passed / 0 failed** with **0**
test ids removed and exactly 11 deleted test lines, both test edits named and
justified as strengthenings (Phase 8); dogfooded nine flows on throwaway
copies — E1's **42** findings, E2's **13** and E3's **6** all to **0**, plan A
completing with its leg-2 report naming exactly the **16** references the setup
census measured, plans B and C refusing with zero bytes and empty stdout, and a
there-and-back move leaving the tree **byte-identical** (Phase 9); and ran
`/simplify` plus the documentation closure (Phase 10). The move costs +80 ms
and a solo archive +113 ms over this 73-document tree. M28 is **merged to
`main`** (2026-08-15, `b1ec74b`) and stays `Lifecycle: active` until M29
publishes the train. **M28a is the current milestone — milestone setup
completed 2026-08-15** on `m28a/milestone-setup`, with a full ten-phase task
plan, an implementation log, nine pieces of measured evidence (E1–E9), and
**all seven setup questions RESOLVED** — **Q4** by operator decision, **Q1**
auto-resolved, the rest conductor-resolved. **Step 1 — Phases 1–4 —
completed** on `m28a/phases-1-4` (contract 2026-08-15; RED tests, fixtures and
the classified baseline 2026-08-16), freezing both legs as items (A)–(H) of
*Decisions (Phase 1 — BINDING)* with six amendments to setup-frozen material
and nine Step-1 resolutions (OQ-1 … OQ-9, OQ-7 an operator decision), then
authoring 149 test ids and six `archivedate-*` fixture trees against it — 1502
collected, 71 RED and 90 GREEN, no pre-existing id removed or failing, plus a
same-instance audit and a no-blocker fresh-eyes review that between them fixed
eleven issues, added eighteen locks and escalated nothing. Step 2
(Phases 5–10) is next. Setup's
headline is that **exactly one of the four ways a document can move relative
to the archive subtree is silent**, that it is reachable through `docs mv` in
one command at exit 0 with `docs check` clean, and that **M28 removed the
tree's only accidental alarm for it**: the same relocation left 13
`broken-body-link` errors at exit 2 under pre-M28 `main` and leaves zero
findings at exit 0 today. M28a is therefore a consequence of M28 rather than an
independent idea, and that is why it **blocks M29** — shipping M28 in 2.0.0
without it would leave the release strictly quieter about archived-document
relocation than 1.8.0 was. **Q4's answer made M28a a two-leg milestone**: the
`Archived:` witness plus a narrow `docs mv` refusal of a cross-dated archived
relocation, so the tool's own path is closed for every archived document and
not only for those carrying the field. **M29** remains a registered draft
stub.
**M28's Step 1 (Phases 1–4) was complete (2026-08-15)** on `m28/phases-1-4`,
on top of the milestone setup completed the same day on `m28/milestone-setup`
with a full ten-phase task plan, an implementation log, eight pieces of
measured evidence (E1–E8), and **all seven setup questions RESOLVED** —
Q1/Q2/Q3 by the operator, Q4–Q7 conductor-resolved; Phase 1 did not re-open
them. Phase 1 froze the whole machine-facing contract as *Decisions (Phase 1 —
BINDING)* items (A)–(M), amended three setup-frozen items in place — M26's
compatibility matrix (a preview adopts plan-**construction** failures and
reports-but-does-not-adopt **consequence** verdicts), the E7 leg-2 observation
point, and the E3 fixture contradiction — and recorded eleven Step-1
resolutions. Phase 2 wrote 182 RED ids with zero deleted test lines; Phase 3
authored the seven `movelink-*` fixture trees, each `docs check`-clean and each
proven by a read-only prototype census; Phase 4 captured the baseline at
**1332 collected, 229 failed, 1103 passed** (after the Step-1 audit and the
fresh-eyes fold-in, which returned no blockers) with exactly two exception
classes
and all 1087 pre-existing ids mechanically proven present, 0 removed, 0 test
lines deleted, and exactly one deliberately RED by operator decision
(`test_mv_help`). No product code was touched across Phases 1–4. Setup's headline finding is that both
verbs now produce trees that fail the tool's own gate: one
`docs mv plan.md milestone-plan.md` exits 0 and leaves 42 `broken-body-link`
errors across 14 documents, one `docs archive m17-pypi-publish-impl.md` exits 0
and leaves 13 spanning **both** move classes, and the real closeout
`--cascade-only 'm25-*'` leaves 6 in `status.md` and `plan.md`. 131 body links
in 27 archived documents point at active documents, which makes the
archived-referrer rewrite a blocker resolved by widening M18's move-driven
exception rather than granting a fourth — **Q2, resolved against the stub's
own recommendation (A2)**. **Q1 amended the 2026-08-15 routing entry (A1)**:
the routed strand-check predicate was measured to refuse this repository's own
standard milestone closeout, so it is split into a narrow refusal (a
still-active document outside the plan declaring itself `child-of` a document
the plan would archive — 0 hits on a legitimate closeout, 6 on both harm
plans) and a **report** of every other still-active inbound reference, which
is the half that answers issue #1's actual complaint. **Q3 (A3)** gives
`docs mv` a real preview and a `--json` rewrite-plan record and `archive
--json` a `strands` array, and answers issue #1 finding 4 by declining
`--report-links` as a design while adopting its output — and Phase 7 wrote
both answers back onto the issue #1 entry, so the feedback trail is closed
rather than silently absorbed. M28a is in flight (Step 1, Phases 1–4,
complete 2026-08-16) and M29 remains a registered draft stub.
Execution order is expressed by reciprocal
`precedes`/`follows`; durable prerequisites use
`depends-on`/`required-by`; no transient blocker exists at setup.

```
v1:    M1 (parser + index)  →  M2 (mutating verbs)  →  M3 (validation + JSON)  →  M4 (migrate)  →  M5 (skill)
v1.1:  M6 (PyPI distribution prep)  →  M7 (migration accuracy)  →  M8 (adoption workflow)  →  M9 (PyPI publish 1.3.0)
v1.4:  M10 (adoption-flow polish + 1.3.0 carry-overs)  →  M11 (PyPI publish 1.4.0)
v1.5:  M12 (project rename + M11 wart fixes + version SoT)  →  M13 (PyPI publish 1.5.0)
v1.6:  M14 (robustness + autonomous archive)  →  M15 (agent-native doc authoring)  →  M17 (PyPI publish 1.6.0)
v1.6.5: M19 (post-edit validation ergonomics — touch --check + configurable stale window)  →  M20 (PyPI publish 1.6.5)
v1.8:  M21 (update-check notification — CLI new-version notice) + M22 (root-placement guidance, doc-only) + M23 (agent-aware install-skill + recorded-dest skill-refresh hint)  →  M24 (PyPI publish 1.8.0, batched)   [1.7.0 skipped on PyPI; its CHANGELOG folds into 1.8.0]
v2.0:  M25 (reciprocal integrity + relate)  →  M26 (safe archive selection)  →  M27 (body-link validation)  →  M28 (move-safe rewrites)  →  M28a (archive-date witness)  →  M29 (PyPI publish 2.0.0)
skill: M16 (bundled docs skill quality artifacts)
fix:   M18 (archive edge integrity — intra-archive Related: rewriting)
```

## M1 — Parser, walker, and `docs index`

Goal: read the convention reliably and produce a usable INDEX.md.

- Parse a single Markdown file into `{title, status, role, project, updated, related, extra_fields, body}`.
- Walk a docs root, skipping anything that isn't `.md` and isn't under a configured ignore pattern.
- Implement `docs index` with the marker-block strategy. Idempotent output.
- `.docs.toml` loading (TOML via stdlib `tomllib`, Python 3.11+).
- Smoke test against `~/opt/docs/docs/` itself — running `docs index` here should reproduce the hand-written INDEX.md byte-for-byte (or close enough that the diff is review-able).

Exit criteria: hand-written INDEX.md matches generated output on this repo. M1 unblocks every later milestone because they all need the parser.

## M2 — Mutating verbs: `new`, `archive`, `mv`, `touch`

Goal: stop hand-editing metadata.

- `docs new <role> <slug>` writes a scaffolded file with correct metadata block.
- `docs archive <file>` does the dual-status dance atomically (edit, move, reindex).
- `docs mv <old> <new>` rewrites `Related:` references across the tree.
- `docs touch <file>` bumps `Updated:`.
- Atomicity: tmp file + rename for every write; never leave a partially-edited doc.
- `--dry-run` works on all of these.

Exit criteria: archiving and renaming this repo's own docs through M2 produces correct, drift-free state.

## M3 — Validation and query: `check`, `list`

Goal: make the convention enforceable and queryable.

- `docs check` reports all violations defined in `cli.md`. Exit code semantics matter: 0/1/2 must be distinguishable so CI hooks can rely on them.
- `docs list` with all filters and JSON output. JSON schema documented in `cli.md` and stable from this point.
- Stale detection (`--stale N`).

Exit criteria: `docs check` on this repo's `docs/` returns exit 0. `docs list --json` output validates against the documented schema.

## M4 — Migration helper: `docs migrate <dir>`

Goal: import an existing non-conforming directory into the convention.

- Walks a foreign directory, inspects each `.md` file's structure.
- Infers `Role` from filename suffix patterns (`-spec`, `-status`, `-plan`, etc.) and from any existing metadata-shaped lines.
- Infers `Project` from common filename prefix.
- Inserts a metadata block under the H1 (or creates an H1 from the filename if missing).
- Detects existing archive-style subdirs (`archived/`, `project-history/`, `archive/YYYY-MM-DD/`) and normalizes them.
- Produces a dry-run report by default; `--apply` performs the edits.
- Intended to be agent-driven: the migration tool surfaces ambiguities, an LLM resolves them, the tool applies the decisions.

This is the verb that lets us point an agent at an existing doc tree (the validaitor specs, the risk-register dir, anyone's `docs/`) and bring it into the convention without manual labor.

Exit criteria: a dry-run against one of the example directories produces a complete migration plan with explicit decisions for every ambiguous case.

## M5 — Claude Code skill

Goal: agents use `docs` automatically when working in a docs root.

- SKILL.md at `~/.claude/skills/docs/` (or wherever the install convention lands).
- Triggers on: editing a `.md` file under a `.docs.toml`-marked root; user requests to "archive", "list docs", "create a plan/spec/charter"; before agent appends to a hand-curated INDEX.
- Skill body redirects to the appropriate `docs` verb instead of hand-editing.
- Documents the trigger conditions and the verbs without re-teaching the convention (that lives in `convention.md`).

Exit criteria: the agent stops hand-editing INDEX.md in this repo and uses `docs index`.

## v1.1

**docs-cli 1.3.0 shipped 2026-05-25** (closes the M6 → M9 backlog grouping internally tracked as "v1.1"). M6 (PyPI
distribution preparation, closed 2026-05-24), M7 (migration
accuracy + breaking `Status:` → `Lifecycle:` rename, complete
2026-05-25), and M8 (adoption workflow, complete 2026-05-25)
all landed locally over a two-day stretch; M9 (operator-driven
PyPI publish, 2026-05-25) batched them into one public release
per the OQ-C split. The package is live at
https://pypi.org/project/docs-cli/1.3.0/ and the GitHub repo
is public with the `v1.3.0` tag + release. Intermediate
versions (1.1.0, 1.2.0) never reached PyPI by design — no
prior public release existed, no continuity to preserve.

| Milestone | Status | Task plan | Log |
|---|---|---|---|
| M6 — PyPI distribution preparation as `docs-cli` | **Complete** (2026-05-24, preparation only; publish moved to M9) | [m6-pypi-distribution.md](archive/2026-05-24/m6-pypi-distribution.md) | [Log](archive/2026-05-24/m6-pypi-distribution-log.md) |
| M7 — Migration plan accuracy | **Complete** (2026-05-25; ship-ready locally, publish deferred to M9 batched 1.3.0) | [m7-migration-accuracy.md](archive/2026-05-25/m7-migration-accuracy.md) | [Log](archive/2026-05-25/m7-migration-accuracy-log.md) |
| M8 — Adoption workflow (agent-driveable) | **Complete** (2026-05-25; ship-ready locally as 1.3.0, publish DEFERRED to M9 batched 1.3.0 per OQ-C) | [m8-adoption-workflow.md](archive/2026-05-25/m8-adoption-workflow.md) | [Log](archive/2026-05-25/m8-adoption-workflow-log.md) |
| M9 — PyPI publish 1.3.0 | **Complete** (2026-05-25; `docs-cli==1.3.0` on PyPI; repo public; `v1.3.0` tag + GitHub release) | [m9-pypi-publish.md](archive/2026-05-25/m9-pypi-publish.md) | [Log](archive/2026-05-25/m9-pypi-publish-log.md) |
| M10 — Adoption-flow polish + 1.3.0 carry-overs (v1.4.0) | **Complete** (2026-05-27; shipped to PyPI as 1.4.0 via M11) | [archive/2026-05-27/m10-adoption-polish.md](archive/2026-05-27/m10-adoption-polish.md) | [Log](archive/2026-05-27/m10-adoption-polish-impl.md) |
| M11 — PyPI publish 1.4.0 | **Complete** (2026-05-27; `docs-cli==1.4.0` on PyPI; `v1.4.0` tag + GitHub release; chain-of-custody bit-perfect; M10 headline contract holds against PyPI-served wheel) | [archive/2026-05-27/m11-pypi-publish.md](archive/2026-05-27/m11-pypi-publish.md) | [Log](archive/2026-05-27/m11-pypi-publish-impl.md) |
| M12 — Project rename + M11 wart fixes + version SoT (v1.5.0) | **Complete** (2026-05-28; `dist/docs_cli-1.5.0-*` built locally, twine check PASS, 433/433 pytest GREEN; shipped to PyPI as 1.5.0 via M13 on 2026-05-29) | [m12-project-rename.md](archive/2026-05-28/m12-project-rename.md) | [Log](archive/2026-05-28/m12-project-rename-impl.md) |
| M13 — PyPI publish 1.5.0 | **Complete** (2026-05-29; `docs-cli==1.5.0` on PyPI; `v1.5.0` annotated tag + GitHub release; chain-of-custody bit-perfect; all four M12 headline contracts hold against the PyPI-served wheel) | [archive/2026-05-29/m13-pypi-publish.md](archive/2026-05-29/m13-pypi-publish.md) | [Log](archive/2026-05-29/m13-pypi-publish-impl.md) |
| M14 — Robustness + autonomous archive (v1.6.0) | **Complete** (2026-06-02 impl-complete; **shipped to PyPI as `docs-cli==1.6.0` via M17 on 2026-06-03**, batched with M15; `docs mv` atomicity, `docs new` strict-root, four-verb `touch`/`archive`/`mv`/`project rename` excludes, slug/`OSError`/`atomic_write`-fsync guards, non-interactive `archive --cascade`, bundled-ref guard + packaging fix; pair archived to `archive/2026-06-03/` at the M17 closeout) | [archive/2026-06-03/m14-robustness-agent-native.md](archive/2026-06-03/m14-robustness-agent-native.md) | [Log](archive/2026-06-03/m14-robustness-agent-native-impl.md) |
| M15 — Agent-native doc authoring (v1.6.0) | **Complete** (2026-06-03 impl-complete, Phases 1–10; **shipped to PyPI as `docs-cli==1.6.0` via M17 on 2026-06-03**, batched with M14 — `docs project set`, single-file `docs stamp`, `--body-from` real-frontmatter detector, skill/cli docs; depended on M14; 501 GREEN at M15 close, gate clean tree-wide; pair archived to `archive/2026-06-03/` at the M17 closeout) | [archive/2026-06-03/m15-agent-native-authoring.md](archive/2026-06-03/m15-agent-native-authoring.md) | [Log](archive/2026-06-03/m15-agent-native-authoring-impl.md) |
| M16 — Bundled docs skill quality artifacts | **Implementation complete** (2026-06-01; documentation-only bundled `docs` skill guidance for quality artifacts, test matrices, generated reports, and `docs check` limits; pending operator commit/archive) | [m16-bundled-docs-skill-quality.md](archive/2026-06-01/m16-bundled-docs-skill-quality.md) | [Log](archive/2026-06-01/m16-bundled-docs-skill-quality-impl.md) |
| M17 — PyPI publish 1.6.0 | **Complete** (2026-06-03; `docs-cli==1.6.0` on PyPI, batching M14 + M15 as M9 batched M6+M7+M8; `v1.6.0` annotated tag at `95f23a6` + GitHub release; chain-of-custody bit-perfect; all seven M14 + M15 headline contracts hold against the PyPI-served wheel; milestone doc archived to `archive/2026-06-03/`, impl log stays `Lifecycle: active`) | [archive/2026-06-03/m17-pypi-publish.md](archive/2026-06-03/m17-pypi-publish.md) | [Log](m17-pypi-publish-impl.md) |
| M18 — Archive edge integrity (intra-archive Related: rewriting) | **Complete / archived** (2026-06-03 impl-complete; correctness fix to `docs archive` so archiving interrelated docs into the archive subtree no longer orphans their `Related:` edges — the conditioned archived-skip in `_rewrite_referring_edges` rewrites the moved doc's own archive-subtree edges + repoints already-archived referrers; flipped the pinned `test_archive_does_not_rewrite_archive_subtree_edges` → `test_archive_repoints_already_archived_referrer`; `docs mv` parity (D3, Open Q1) verified already satisfied — no code change. Phase-9 payoff archived the M1–M9/M12 pairs + M16 trio + 3 stray impl-logs; `docs check docs/` exit 0. 510 GREEN, gate clean. The M18 pair was archived to `archive/2026-06-12/` at the M20 closeout — it rode along in the 1.6.0 tree and added no new public surface to 1.6.5) | [archive/2026-06-12/m18-archive-edge-integrity.md](archive/2026-06-12/m18-archive-edge-integrity.md) | [Log](archive/2026-06-12/m18-archive-edge-integrity-impl.md) |
| M19 — Post-edit validation ergonomics (touch --check + configurable stale window) (v1.6.5) | **Complete** (2026-06-12; feature milestone — `docs touch --check [--stale N]` folds the existing `check_tree` into the touch loop after the end-of-batch reindex; `.docs.toml [check] stale_days = N` makes the stale window per-tree configurable (CLI `--stale` overrides); cosmetic `docs new --body-from` help-string fix closes the rolled-forward follow-on. No new verb, no new check rule; additive + backward-compatible. **Shipped to PyPI as `docs-cli==1.6.5` via M20 on 2026-06-12.** Q1–Q6 + OQ-1..OQ-5 RESOLVED; threshold-provenance folded into D2. Full suite 540/540 GREEN (533 + the Step-2 review +7), gate clean tree-wide, `docs 1.6.5`. The M19 pair was archived to `archive/2026-06-12/` at the M20 closeout) | [archive/2026-06-12/m19-post-edit-validation.md](archive/2026-06-12/m19-post-edit-validation.md) | [Log](archive/2026-06-12/m19-post-edit-validation-impl.md) |
| M20 — PyPI publish 1.6.5 | **Complete** (2026-06-12; `docs-cli==1.6.5` on PyPI, the publish-only counterpart to M19 one-to-one as M13 → M12; `v1.6.5` annotated tag at the Phase-4 commit `0855466` + GitHub release; chain-of-custody **bit-perfect for both wheel AND sdist** (wheel `aba36e92…`, sdist `f9de1eb4…`); all M19 headline contracts hold against the PyPI-served wheel; ran the [release-runbook.md](release-runbook.md) on `main`, M17 precedent (no TDD code phases). NEW vs M17: the closeout refreshed the host-machine skills (`docs install-skill --force` + a workflow-skill sweep that caught + fixed one stale `--body-from` reference in `project-foundation`) per the CLAUDE.md skill-update-flow policy. Q1 → FULL AUTONOMOUS, Q2 → archive the M18 + M19 pairs + M20's own milestone doc to `archive/2026-06-12/`; the M20 impl log stays `Lifecycle: active`) | [archive/2026-06-12/m20-pypi-publish.md](archive/2026-06-12/m20-pypi-publish.md) | [Log](m20-pypi-publish-impl.md) |
| M21 — Update-check notification (PyPI new-version notice) (v1.7.0) | **Complete** (shipped to PyPI as `docs-cli==1.8.0` batched via M24 2026-07-03; pair archived to `archive/2026-07-03/`; **1.7.0 skipped on PyPI**) — impl-complete 2026-06-29 (scaffolded 2026-06-12; re-scoped to CLI-only 2026-06-29; **all 10 TDD phases done 2026-06-29** — Phases 1–4 (RED baseline) on `m21/phases-1-4`, Phases 5–10 on `m21/phases-5-10`: full suite **604 GREEN** (+4 Step-2 review fold-in), gate clean tree-wide, `pyproject` at 1.7.0, `docs --version` = `docs 1.7.0`; the online path verified against live PyPI + dogfooded end-to-end, pytest 100% offline; 1.7.0 built locally — publish is a later milestone) — feature milestone introducing docs-cli's **first network surface**: a once-per-24h, fail-silent PyPI version check (stdlib `urllib` only, 1.0s timeout, 24h-cache-gated under `${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json` with a three-key `{last_check, latest_version, last_notified}` schema, zero-dependency wheel preserved) that emits ONE STDERR line nudging the user/agent to update **the CLI** (`pip install -U docs-cli`; wording `docs: update available <current> -> <latest> — run: pip install -U docs-cli`). STDERR-only, never alters the exit code, suppressed under `--quiet`/`--json`/`CI`/`DOCS_CLI_NO_UPDATE_CHECK`/`DO_NOT_TRACK` (the user-level config opt-out is DEFERRED out of v1.7.0 — OQ-5/5a), but **deliberately shows on non-TTY** (inverting gh's TTY rule — the agent is the actor). The former skill-drift notice (D5) + the dual-action `docs install-skill --force` half are **CUT** (re-scope — no skill inspection, no Claude-Code assumption); the skill story moves to follow-on **M23**. Ships as **1.7.0** (minor — additive; 1.6.5 was the operator-decreed patch exception); a later operator-driven milestone publishes (M19 to M20 pattern). Depends on nothing. **OPEN QUESTIONS netted out — none outstanding** (OQ-1..OQ-9 RESOLVED 2026-06-12; OQ-6 "ship D5" REVERSED by the re-scope); stays LIVE at root, lifecycle `draft`. | [m21-update-check.md](archive/2026-07-03/m21-update-check.md) | [Log](archive/2026-07-03/m21-update-check-impl.md) |
| M23 — Agent-aware install-skill + recorded-dest skill-refresh hint (v1.8.0) | **Complete** (shipped to PyPI as `docs-cli==1.8.0` batched via M24 2026-07-03; pair archived to `archive/2026-07-03/`) — impl-complete 2026-07-02 (Phases 1–4 (Contract & RED baseline) on `m23/phases-1-4`; Phases 5–10 (implementation → dogfood → closeout) on `m23/phases-5-10`: full suite **636 GREEN**, gate clean tree-wide, `pyproject` at 1.8.0, `docs --version` → `docs 1.8.0`; online path dogfooded against a seeded throwaway cache, pytest 100% offline) — follow-on to the M21 re-scope that restores the skill-refresh nudge cut from M21. Makes `docs install-skill` **agent-aware**: `--dest` is the agent-agnostic source of truth; TTY-aware resolution (human may be prompted; an agent [non-TTY] is **never** blocked on a prompt → falls back to the default); the resolved dest is **recorded** to a per-user state file (a *path* only — **never** the skill's content); the "Claude Code skill" framing in `install-skill`'s help/description/docstrings is neutralised to **"agent skill"** (reconciled with `cli.md`; the install-skill surface grep is clean); and M21's update notice gains a skill-refresh hint pointed at the **recorded** dest (riding M21's same suppression matrix + throttle). Replay/remember allowed; content-inspection + agent-guessing NOT (the line the cut D5 crossed). Out of scope: multi-agent skill *formats* + agent auto-detection. **Depends on M21** (extends its notice channel). Ships **1.8.0** (OQ-4). **The four OPEN QUESTIONS are resolved** (see the milestone doc Decisions): OQ-1 non-TTY **default** (never refuse), OQ-2 **separate** `${XDG_STATE_HOME:-~/.local/state}/docs-cli/install-skill.json` (M21's 3-key cache stays frozen), OQ-3 last-write-wins single dest, OQ-4 1.8.0 — OQ-1/OQ-2 resolved **provisionally while the operator was away**, **flagged for confirmation at branch review**. Stays LIVE at root, lifecycle `draft`. | [m23-agent-aware-install-skill.md](archive/2026-07-03/m23-agent-aware-install-skill.md) | [Log](archive/2026-07-03/m23-agent-aware-install-skill-impl.md) |
| M24 — PyPI publish 1.8.0 | **Complete** (2026-07-03; `docs-cli==1.8.0` on PyPI; `v1.8.0` tag at `1a01f74` + GitHub release; chain-of-custody bit-perfect wheel `29ac3ced…` + sdist `62a29285…`; M21+M23 contracts hold against the served wheel; host skills refreshed; M21+M22+M23 pairs + this doc archived to `archive/2026-07-03/`, impl log stays active) — operator-driven publish shipping the post-1.6.5 train **batched** as `docs-cli==1.8.0`: M21 (update-check, built 1.7.0) + M22 (doc-only, no bump) + M23 (agent-aware install-skill, 1.8.0), the batched shape (M17 = M14+M15 → 1.6.0; M9 = M6+M7+M8 → 1.3.0). Tree already at 1.8.0 (M23 Phase 7, merged to `main` at `839daef`); **1.7.0 is skipped on PyPI** — its CHANGELOG entries fold up into the dated `## 1.8.0` section (D2). Runbook-driven operational milestone — no TDD code phases; the [release-runbook.md](release-runbook.md) sections are the phases (M9/M11/M13/M17/M20 shape). Setup decisions (2026-07-03): D1 batched 1.8.0; D2 CHANGELOG fold; D3 "author now, confirm at the gate" (runbook starts only on explicit operator go-ahead, pauses before every irreversible / outward-facing step — real PyPI upload, `main` push, `v1.8.0` tag, GitHub release); D4 M23 OQ-1/OQ-2 confirmed as-shipped (branch-review flag cleared, no re-bump); D5 the Phase-5 closeout archives the M21 + M22 + M23 pairs + the M24 milestone doc to `archive/<publish-date>/` (M24 impl log + runbook + status stay active). **Runbook walk (Phases 1–5) not started.** | [m24-pypi-publish.md](archive/2026-07-03/m24-pypi-publish.md) | [Log](m24-pypi-publish-impl.md) |
| M25 — Reciprocal relationship integrity and `docs relate` | **Active / implementation-complete — all ten TDD phases, merged to `main` 2026-08-12 (`822e086`)** (Phases 1–4 2026-08-11 on `m25/phases-1-4`; Phases 5–10 2026-08-12 on `m25/phases-5-10`; `/simplify` on `m25/simplify`) — recognized reciprocal sequence/dependency/blocker pairs, hard `missing-inverse` check errors, explicit two-endpoint add/remove repair, and narrowly audited archived-endpoint mutation. First implementation milestone in the v2.0 train. Phase 1 froze the contract in `cli.md` / `convention.md` and RESOLVED all five open questions (**Q5: the package stays 1.8.0 through M25–M28; M29 does the single bump to 2.0.0**); Phases 2–4 added 121 test items over ten committed `reciprocal-*` fixture trees and captured the classified RED baseline (**757 collected, 87 failed, 670 passed**, zero collection errors, the 636 pre-existing tests all still GREEN). Step 1 passed a same-instance audit and an independent fresh-eyes review with **no blockers**; the review's two operator-binding contract amendments — a self-referential recognized edge is exempt from `missing-inverse`, and reciprocity matches on canonical root-relative paths — are folded into `cli.md`, `convention.md`, the milestone Decisions, and the tests. Step 2 landed the implementation: Phase 5 the vocabulary / three `Related:` editors / planning models, Phase 6 the cross-document reciprocity pass and the staged-publish-with-rollback coordinated edit, Phase 7 the `docs relate add|remove` CLI, the bundled skill row, the `UNRELEASED` CHANGELOG section (**no version bump**), and eight conductor-resolved spec corrections to `cli.md`; Phase 8 the GREEN gate (**757 passed**) with zero pre-existing regressions proven by `comm` against the Phase-1 commit, plus one operator-approved correction to a Step-1 assertion that was unsatisfiable alongside another test in the same file; Phase 9 the eight-flow dogfood on a throwaway tree copy; Phase 10 the closure of `architecture.md` / `test-strategy.md`, the shipped use-case catalog's upgrade-and-repair flow, and the completion summaries. The fresh-eyes review returned **no blockers**; its fold-in fixed two editor defects (EOF trailing-newline preservation — a D4 allowed-byte violation — and a re-created `Related:` group landing after `Revision:`), added four failure-path locks, and landed one **operator-approved post-freeze** addition: the **`duplicate-field`** rule (D7), closing a silent data-loss defect that predates M25. **777 GREEN.** | [Plan](m25-reciprocal-relationship-integrity.md) | [Log](m25-reciprocal-relationship-integrity-impl.md) |
| M26 — Safe explicit archive selection | **Active / implementation-complete — all ten TDD phases (2026-08-13)** (registered 2026-08-10; planned in depth 2026-08-12 on `m26/milestone-setup`; Phases 1–4 on `m26/phases-1-4` 2026-08-12 / 2026-08-13 — contract frozen, RED suite written, `archive-*` fixtures added, classified RED baseline 884 collected / 104 failed / 780 passed with 769 of 777 pre-existing ids mechanically proven still GREEN, audit + fresh-eyes review folded; Phases 5–10 on `m26/phases-5-10` 2026-08-13 — models and planner, the whole seam, the CLI and every parallel surface, **895 GREEN** with 774 of the 777 pre-existing ids proven present and passing, 3 deliberately removed and 121 new, the closeout workflow dogfooded on a throwaway copy of this tree, and the simplify-and-close pass) — bare `--cascade` refuses before any write and `--interactive` is **retired** under the same refusal (Q1) — both stay registered in argparse and refuse with exit 2 + migration guidance (Q2), so an obsolete script or workflow skill gets a legible failure rather than `unrecognized arguments`. `--cascade-dry-run` stays read-only and names every one-hop candidate as selected / not-selected / ineligible, and every related-document write requires an explicit `--cascade-only GLOB` whose complete plan is validated before the first byte moves: deduplicated on the canonical root-relative path, destination-collision and writability checked, already-archived neighbours excluded and an already-archived primary refused (Q4), empty selection refused. `docs archive` gains a `--json` operation-plan record — one shape for preview and apply, carrying primary / candidates / selected / excluded-with-reason / destinations / written state (Q6), reusing M25's `relate --json` pattern. Every handled error refuses with zero mutation; a residual mid-execution `OSError` is reported as an exact partial-state admission and is **not** rolled back (Q5) — extending M25 — D5's staged-publish-plus-rollback to N documents was considered and explicitly declined, and is recorded for a later milestone. The candidate verb set stays the one-hop `pairs-with`/`child-of` pair (Q3); M25's six reciprocal verbs never become candidates; `docs archive FILE` stays quiet about candidates it leaves in place (Q7). Setup reproduced five concrete v1.8.0 defects **E1–E5**, each mapped to named regression coverage — bare `--cascade` on the M25 pair proposing to archive `plan.md` + `cli.md` + `convention.md` + `test-strategy.md` + `status.md`; a duplicate edge printing a false failure; a basename collision leaving a partial archive at exit 0 with `docs check` clean; an archive-subtree edge silently relocating and re-dating an archived doc (data corruption, load-bearing on this tree where `status.md` carries 20+ archive-subtree edges); and a typo'd `--cascade-only` looking like success. **All seven setup questions are RESOLVED** — Q1/Q5/Q6 by operator decision, Q2/Q3/Q4/Q7 conductor-resolved — so Phase 1 froze exact messages, the exit-code split, and the JSON schema rather than re-opening scope, along with seventeen Step-1 planning questions. No version bump (M25 — D6). Follows M25. | [Plan](m26-safe-archive-selection.md) | [Log](m26-safe-archive-selection-impl.md) |
| M27 — Markdown body-link validation | **Implementation-complete — all ten phases done** (2026-08-14, `m27/phases-1-4` + `m27/phases-5-10`) — a pure stdlib-only scanner over a deliberately bounded, named Markdown subset (inline links with plain/angle destinations and optional titles, plus reference definitions; images, autolinks, raw HTML and reference uses excluded), length-preserving fenced- and inline-code masking, destinations resolved **relative to the referring document** with fragments preserved and never validated, and **two** hard errors: `broken-body-link` (a missing in-root destination) and `outside-root-body-link` (a destination that leaves the tree), both `severity: error`, exit 2, one finding per occurrence, JSON key set left **closed** with the location carried in `message`. The check **never stats outside its own root** — an escape is decided by path arithmetic, and containment is tested **before** existence so the two rules never double-report. The `BodyLink` record's exact destination-token span is the handoff to M28 — no second parser. Registered 2026-08-10, planned in depth 2026-08-14 on `m27/milestone-setup`; setup measured the tree read-only and produced eight pieces of evidence **E1–E8** — **139 unresolved local destinations across 29 documents, 100% of them under `archive/`** (132 a pure `../../` rebase, 5 a moved target, 2 a bundled-skill file that never lived in the docs tree); `docs check` exits **0** today with all 139 broken; `test_check_dogfood_repo_docs_is_clean` makes the legacy policy a hard gate inside the suite; code masking prevents 7 measured false positives (including `architecture.md:182`'s `[<path>](<path>)`) while a 4-space indented-code rule would mask 9 spans that are all real links; a containment census over `docs/`, all 33 fixture trees and the bundled skill finds **exactly one** escape (`charter.md:52`) and none in any fixture; and nothing in the repository exercises the exotic grammar, so Phase 3 must author it. **All seven setup questions RESOLVED** — Q1/Q2/Q5 operator, Q3/Q4/Q6/Q7 conductor. **Q1: repair, rule stays uniform** — the breakage class is produced by `docs archive` itself and `docs/` ships in every PyPI sdist and is public on GitHub, so exempting archived docs would leave the tool silent about the damage it causes; the one-time destination-token-only repair is `Updated:` + `Revision:` audited and lands in Phase 6, and `convention.md` gains a third archived-document exception with a stated blast radius. **Q5 was resolved against the setup recommendation and then amended**: the hermetic boundary is kept (a check must be a function of the tree alone) but the escape is **reported** rather than skipped — `outside-root-body-link` is an operator-approved post-draft scope addition following M25's `duplicate-field` precedent, and `charter.md:52` is converted to the canonical GitHub URL in Phase 6, the same treatment Q1 gives the two `adoption-playbook` links and doubly right since the relative alternative would itself have violated Q5. **Step 1 (Phases 1–4)** froze that contract in `cli.md` › *Markdown body-link validation*, `convention.md` › *Body links* and the milestone's *Decisions (Phase 1 — BINDING)* — amending three setup-frozen items under conductor decision — then wrote the RED suite (a 105-item pure-scanner module plus the rule, subprocess, `touch --check` and bundled-skill locks), authored the six `bodylink-*` fixture trees, and captured the classified baseline: **1079 collected, 137 failed, 942 passed** (after the same-instance audit's six fixes and the fresh-eyes review's thirteen further locks), zero collection errors, zero tracebacks, exactly two exception classes, and **all 895** pre-existing ids mechanically proven present and passing. **Step 2 (Phases 5–10)** landed the whole pure scanner with no rule wired (119 tests cleared, every remaining failure an `AssertionError`), then wired both rules into `check_doc` **in the same commit as** the D6 live-tree repair — 140 occurrences across 30 documents, split 132 root rebases / 5 moved targets / 2 playbook URLs / 1 escape URL, driven by the scanner itself, spliced by offset right-to-left (literally the M28 operation), audited with an `Updated:` bump on all 30 plus one uniform dated `Revision:` bullet on the 29 archived ones, and proven by six independent checks including 30/30 byte-identical round-trip reconstructions and a re-census at 0 broken / 0 escapes with the recognised-span count still 393. Every parallel surface was then reconciled (argparse, bundled `SKILL.md`, `references/use-cases.md`, `CHANGELOG.md` under `UNRELEASED`), the suite went **fully GREEN at 1079 passed / 0 failed** with `git diff -- tests/*.py` empty — **no test was relaxed, weakened, deleted or rewritten to get there** — the documented upgrade recipe was walked from `docs check --json` alone on a throwaway pre-repair copy and reached **0 destination-token mismatches** against the repaired tree, hermeticity was proven end to end (identical verdict from a with-sibling and a bare location, 0 probes outside the root under a spy), and the `/simplify` pass closed `architecture.md` and `test-strategy.md` while cutting the live-tree scan from 183 ms to 81 ms. The **Step-2 same-instance audit** then found **twelve** issues and fixed all twelve — **three of them real behavioural defects in the scanner** invisible to both the finding set and the suite, reachable only by reading the frozen contract as a specification. The critical one is a **hermeticity hole**: a percent- or backslash-encoded leading slash (`%2Fetc/passwd`) classifies `local`, decodes to `/etc/passwd`, wins the `posixpath.join`, and — because Phase-1 point 9 dropped the containment predicate's leading-`/` leg — read as *contained*, so `docs check` **stat'd a path outside its own root**, the single thing D4b exists to forbid. The leg is restored and **point 9 is amended in place, a BINDING Phase-1 decision flagged for the operator**. Also fixed: a link nested inside an image label was silently dropped (foreseen by the Phase-1 linearity note), rule 5's *at least one whitespace character* before a title was not enforced, and two docstrings asserted falsehoods. All three scanner fixes are behaviour-neutral on every real input, and the three reachable defects are **locked**, taking the suite to **1082 passed / 0 failed**. Three items are surfaced for the operator rather than auto-decided. An independent **fresh-eyes review** then reproduced all of that adversarially — a 40,000-case destination fuzz under a `Path.exists` spy (21,747 stats, 0 outside the root), an `strace` of a real `docs check`, its own round-trip of the 140-occurrence repair (30/30 byte-identical), a 20,000-input mask/span fuzz, and 40 grammar shapes walked clause by clause — and returned **one blocker plus eight further items**, every one folded in. The blocker was the mirror image of the audit's own A2: a link whose **label** is an image (`[![diagram](diagram.png)](full-size.md)`, the ordinary badge / thumbnail idiom) ended its label at the *image's* `]`, so `docs check` **reported the image** as `broken-body-link` — against the success criterion that images produce no finding, and against operator-binding Q2's own words — and never emitted the real destination, so M28 would never rewrite it. Rule 2 is amended (a nested image consumes one `]`) and implemented as a level table, because the accepted `]` depends on where the label started and a rescan is quadratic. The review also closed **two residual quadratics** — many unterminated `<` or `(…)` titles inside one paragraph, measured at 3.27 s and 5.96 s, now 6.7 ms and 10.8 ms — corrected three places that claimed a linearity which did not hold, had the dangling-symlink lock written rather than deferred, qualified a spec sentence that could not be true alongside S9, stopped a percent-decoded control character splitting a finding across two lines, and fixed a **pre-existing** `OSError` crash on an over-long path segment at **both** the body-link and `broken-ref` probes. Final: **1087 passed / 0 failed**, eight test ids added across the audit and the review, **zero removed** against both anchors, and no assertion loosened. No version bump (M25 — D6). Follows M26; required by M28. | [Plan](m27-markdown-body-link-validation.md) | [Log](m27-markdown-body-link-validation-impl.md) |
| M28 — Move-safe Markdown body-link rewrites | **Active / complete — all ten TDD phases done, merged to `main`** (registered 2026-08-10; planned in depth 2026-08-15 on `m28/milestone-setup`; Phases 1–4 2026-08-15 on `m28/phases-1-4`; Phases 5–10 2026-08-15 on `m28/phases-5-10`; Step 3 `/simplify` on `m28/simplify`; **merged 2026-08-15, `b1ec74b`, 1341 GREEN**; **all seven setup questions RESOLVED**; depends on M26 + M27) — `docs mv` and `docs archive` rebase the parsed local Markdown destination tokens a move makes stale, reusing M27's scanner and its exact destination spans (no second parser) and splicing right-to-left. The two move classes — a link whose *target* moved, and a link *inside* a document that itself moved — are one formula: resolve from the referrer's old location, map the resolved target through the move set, relativise against the referrer's new directory; mapping on the **normalised** target, so every spelling of one file is rewritten and no alias list is needed. The plan is built and validated before the first byte moves, inverting `_cmd_mv`'s move-then-rewrite ordering and giving `mv` M26 — D4's zero-mutation refusal for the first time, with the `Related:` rewrite and the body splices landing in one `atomic_write` per document. Setup produced **E1–E8** on read-only censuses and throwaway reproductions: `docs mv plan.md milestone-plan.md` rewrites 35 `Related:` bullets, exits 0, and leaves **42 `broken-body-link`** across 14 documents; `docs archive m17-pypi-publish-impl.md` exits 0 and leaves **13**, spanning both classes, 4 of them inside archived referrers; the real closeout `--cascade-only 'm25-*'` leaves **6** in `status.md` and `plan.md`; **131 body links in 27 archived documents point at active documents**, making the archived-referrer rewrite a blocker resolved by widening M18's move-driven exception along its own axis rather than granting the fourth exception `convention.md` says it will not grant; `rewrite_related_refs` cannot be reused because it matches by exact string while one target is spelled three ways here; and no `mv` / `archive` fixture carries a body link at all, so Phase 3 authors every form. Scope extended 2026-08-15 from `feedback-log.md` issue #1 finding 1: a post-plan **strand-check**. **Q1 amended the routing entry (A1)**: the literal predicate was measured over three plans and **refuses a textbook `--cascade-only 'm26-*'` closeout** (8 still-active edges + 8 body links from 7 deliberate referrers), so the routing note's self-cancelling claim does not hold, while the harm reproduces live (`--cascade-only '*'` marks `plan.md`, `cli.md`, `convention.md`, `test-strategy.md`, `status.md` selected). Resolved into two binding legs — refuse only on a still-active `child-of` into the plan (0 on the closeout, 6 on both harm plans), and **report** every other still-active inbound reference in the preview, the apply output and a `strands` array. **All seven setup questions are RESOLVED** (Q1/Q2/Q3 operator, Q4–Q7 conductor); issue #1 finding 4's `--report-links` is declined as a design and its output adopted as the plan record (Q3 / A3), and Phase 7 wrote both answers back onto the issue #1 entry. **Step 2 (Phases 5–10) landed it**: the pure planner seam as three insertions with no verb wired (Phase 5); `_cmd_mv` inverted to plan-before-move with the R9 partial-state admission, `docs archive`'s steps 5b / 8b / 8c / 8d, each moving member's planned text threaded into `_archive_one` so the contract stays at one `atomic_write` per document, and `_rewrite_referring_edges` **deleted** as superseded — its M18 archived-doc gate is unnecessary by construction, because an archived document's text now changes iff a `Related:` target or a body-link destination resolved into the move set, which is exactly rule (G) (Phase 6); every parallel surface reconciled, including the bundled catalog's now-false "prose links are not rewritten — a deliberate scope cut" sentence, and the upgrade note naming the two re-spelled `docs mv` stderr lines that no test pins and that therefore break silently (Phase 7); the gate at **1333 passed / 0 failed** with **0** ids removed against the pre-M28 commit and exactly 11 deleted test lines, both test edits named and re-verified as strengthenings rather than reported as "0 lines changed" (Phase 8); a nine-flow dogfood on throwaway copies — E1 42→**0**, E2 13→**0** including its four archived referrers, E3 6→**0**, plan A **completing** with its leg-2 report naming exactly the **16** references the setup census measured (8 `Related:` + 8 body links from 7 referrers), plans B and C **refusing** at exit 2 with zero bytes and empty stdout, the refusal surviving `--quiet`, and a there-and-back move leaving the tree byte-identical including `INDEX.md`; +80 ms on a move, +113 ms on a solo archive (Phase 9); and `/simplify` (net −18 lines, four collapses) plus the closure of `architecture.md`, `test-strategy.md`, `plan.md` and `status.md` (Phase 10). No version bump (M25 — D6). A **Step-2 same-instance audit** — three passes: code against contract, documents against each other and against measured ground truth, and an adversarial pass reproducing every contract claim on throwaway trees — then found **sixteen** issues and fixed all sixteen. The four that matter most: `convention.md` still carried Q4's PRE-amendment wording — that an already-**broken** destination is byte-identical after a move — which amendment 4 reversed and which the pinned planner test contradicts, and which matters because `convention.md` ships byte-identically inside the wheel (the amendment named `cli.md` and *Out of scope* but not `convention.md`, so it slipped); two shipped `docs mv` behaviours were undocumented (an unreadable document in the plan walk, and the INDEX-refresh failure's new message, record and exit); and **two locks the Step-2 resolutions explicitly required had shipped as promises** — `--quiet` over a PREVIEW whose plan has orphans (the only place item (L)'s report-vs-refusal split is observable) and `docs mv`'s INDEX-refresh record. Both new locks were **mutation-tested**: reverting the code to the shape each forbids fails that id and leaves every other test green. The renderer's two post-conditions and the never-creates-an-escape invariant were additionally **fuzzed** — 60,000 and 18,646 cases, zero failures over the reachable domain. Its largest single find was a **false claim in `cli.md`** — that a move never rewrites 4-space-indented code, which the same file has contradicted since M27 and which was reproduced live: D2's RULE was implemented exactly right, its ENUMERATION was wrong, and `cli.md` ships byte-identically inside the wheel, so an agent was being told a code sample is safe from a move that silently edits it (corrected in both places and recorded as **amendment 5**). It also pruned the directory a failed `docs mv` rename could leave behind while admitting it had moved nothing, normalised and pinned two undocumented refusal strings, and gave the overlap proof its first real witness — the test named after it could not reach it, because (F)'s order trips span-match first. One item is **surfaced, not implemented**: `docs archive` has no partial-state admission for its rewrite phase, now *Follow-ups* item 8. Final suite after the audit: **1338 passed / 0 failed**. A **fresh-eyes review** then returned **no blockers on the product code** — it re-ran the gate, reproduced the no-regression proof, and swept the pure seam exhaustively for zero contract violations — but eight findings, all folded in. The largest, by **operator decision**, closed the one item the audit had surfaced rather than fixed: `docs archive` now emits a **partial-state admission for its REWRITE phase** too (amendment 7 to item (J)), so both verbs behave the same and three shipped promises — `cli.md`'s *Residual boundary*, its *Validate-all-first* section (which opens "governs **both**" verbs), and the milestone's verb-agnostic success criterion — become true as written instead of false in a file that ships inside the wheel. Also by operator decision: `preview only — nothing was written` now closes **every** preview, not only a cascade one, because M26's "one line needs no disclaimer" rationale died when the block grew; and the unconditional zero footer **stays**, now pinned together with leg 2's deliberately conditional count line. The review also found the plan-B census number stale in four BINDING passages (**amendment 6**: plan B measures 5, not 6, because item (H) exempts its own primary — the code was right), and a **dead link on the project's front page** (`README.md` → `blob/main/docs/m8-adoption-workflow.md`, archived since M8), fixed here because shipping a 2.0.0 whose README carries a dead documentation link would be self-refuting in the milestone whose subject is link integrity. Final suite: **1341 passed / 0 failed**. A **second `/simplify` pass** on `m28/simplify` then re-read the whole M28 surface as the audit and the fold-in had left it and made three behaviour-preserving collapses (net **−11 lines**: a nested renderer call lifted out of a `LinkRewrite(…)` argument list the formatter had exploded across seven lines, a pure dict comprehension hoisted out of archive step 9a's `try` so the guarded block is the one call it guards, and `docs mv`'s admission computed before it is printed instead of concatenated inside the `print`). Four candidates were considered and **rejected with reasons** — chiefly a shared `_planned_writes` helper, which is net-zero on lines and moves a rule out of the two message-renderers whose whole value is that each clause is checkable where it is read — and Phase 10's archive `try`-block merge was deliberately **not** re-made, because F1's rewrite-phase admission means the two phases no longer fail identically. Suite unchanged at 1341. | [Plan](m28-move-safe-body-link-rewrites.md) | [Log](m28-move-safe-body-link-rewrites-impl.md) |
| M28a — Structured archive-date witness | **Active / Step 2 (Phases 5–10) in flight** (setup 2026-08-15 on `m28a/milestone-setup`; **Phases 1–4** on `m28a/phases-1-4`, contract 2026-08-15 and RED baseline 2026-08-16 at 1502 collected / 71 RED / 90 GREEN; **Phases 5–6** 2026-08-16 on `m28a/phases-5-10` — the vocabulary entry, `parse_date`'s keyword-only `label` and all three pure helpers wired nowhere (43 ids flipped to 28 failed / 1474 passed), then the three touch points (the witness write in `_archive_one`, the rule in `check_doc`, Leg 2's refusal in `_cmd_mv`) taking the suite to 2 failed / 1500 passed, then **Phase 7** reconciling every parallel surface — bundled skill, two argparse `description` clauses on a **confirmed-empty** flag delta, the `UNRELEASED` CHANGELOG, `feedback-log.md` issue #1 **CLOSED**, and two spec gaps verification found in `convention.md` — for a fully **GREEN 1502 passed / 0 failed**; **Phase 8** confirming every gate clean with 0 of the 1341 pre-existing ids removed or failing and 0 deleted test-source lines, Phase 9 next; **all seven setup questions RESOLVED** — Q4 operator, Q1 auto, Q2/Q3/Q5/Q6/Q7 conductor — and the contract frozen as items (A)–(H) with six amendments and nine Step-1 resolutions OQ-1 … OQ-9, OQ-7 an operator decision; depends on M26) — **two legs.** Detect: `docs archive` records the archive date as a structured **`Archived:`** field on **every** document the operation moves, and `docs check` gains one present-only rule, `archive-date-drift`, reporting a document whose recorded date its location does not corroborate. Prevent (**Q4, operator**): `docs mv` refuses a move whose source and destination are both under the archive dir with first segments parsing to **different** dates — path arithmetic only, in the plan-before-move window M28 already built (Phase-1 amendment 2 places it one step earlier, before the `--dry-run` branch, so it refuses in every mode), exit 2, both dates named, zero bytes written, with four enumerated permitted neighbours (Phase-1 amendment 6) and a by-hand escape documented in the same paragraph. That leg needs no field, so it reaches every archived document including the 46 archived before the witness existed. Hard error, exit 2, one finding per document, closed four-key `Finding` record, no new flag, no new JSON key, no opt-out; it fires only when the field is present, so every pre-2.0 archived document stays silent and a 1.x tree gains **zero** findings on upgrade. Promoted from `feedback-log.md` issue #1 finding 3 — the issue's last open item. Setup measured the tree read-only and reproduced the drift on throwaway copies (**E1–E9**), and two findings reshaped the milestone. **E1** enumerates all four relocation paths and finds exactly one silent: `docs archive` refuses an already-archived primary, `docs mv` out of and into the archive are both caught by `status-drift`, and `docs mv archive/<D1>/x.md archive/<D2>/x.md` completes at **exit 0** with `docs check` clean — correcting the registered stub's claim that the tool already prevents this (**A1**). **E2** replays that command against pre-M28 `main` (`58955ef`) and merged `main`: **13 `broken-body-link` errors at exit 2 before, 0 findings at exit 0 after**, so M28 removed the only alarm this class of damage had. Neither existing field can carry the witness — 29 of this tree's 46 archived documents have an `Updated:` that differs from their directory and `docs touch` bumps it again at exit 0 (E3), while `Archived-reason:` is primary-only and covers 13 of 46 (E4) — which is why the witness deliberately breaks that precedent (**A2**), the reported case being a cascaded trio split across two dated directories. The issue's literal request (warn when `pairs-with` partners sit in different dated directories) stays **declined**, now measured: it would emit **7** findings on this correct tree (E5). Comparison is on **parsed dates** in the tree's `date_format`, never raw strings, because a non-default-`date_format` tree already trips a pre-existing hardcoded-ISO parse (E8); and `docs migrate` never writes the witness, because its archive-directory dates come from `Updated:` or **mtime**, which on a fresh clone is today (E9). Setup also registered E8 in `feedback-log.md` as a separate, unowned, deliberately-unfixed defect. No new flag, no new JSON key, no version bump (M25 — D6). | [Plan](m28a-archive-date-witness.md) | [Log](m28a-archive-date-witness-impl.md) |
| M29 — PyPI publish 2.0.0 | **Registered release stub** (2026-08-10; no log/runbook phase started) — publish M25–M28a as one breaking safety train, verify upgrade paths against served artifacts, refresh host skills, and archive the train at closeout. Depends on M25–M28a. | [Plan](m29-pypi-publish-2-0-0.md) | _not yet created_ |

**M12 — Project rename + M11 wart fixes + version SoT (v1.5.0)**
is **Complete (2026-05-28)** — `dist/docs_cli-1.5.0-py3-none-any.whl`
+ `dist/docs_cli-1.5.0.tar.gz` built locally, `twine check` PASS,
433/433 pytest GREEN, full quality gate clean tree-wide. The
operator-chosen kitchen-sink scope landed all four threads in one
TDD cycle: (1) `docs project rename <new-name>` verb deferred
from M10 — atomic semantics matching `docs touch` +
`docs migrate --apply`, rewriting `.docs.toml` `[project] name`
+ every conformant `Project:` line across the tree, INDEX refresh
once at end, archive subtree skipped + reported, non-matching-
project docs reported in the footer; (2) `docs touch <path>`
outside any docs root refuses cleanly with exit 2 (M11 wart);
(3) `docs archive <doc>` atomically rewrites referring `Related:`
edges across the tree (M11 wart, cascade-aware); (4) `__version__`
sourced from `importlib.metadata.version("docs-cli")`. Phase 9
dogfood PASS on all four exercises (kebab-tiny round-trip
byte-identical; orphan-dir touch refused; archive referring-edge
rewrite atomic; repo's own docs/ round-tripped byte-identical).
OQ-1 through OQ-11 (scope decisions) + OQ-α through OQ-ι (Step 2
implementation decisions) all resolved per operator recommendation
— see [m12-project-rename-impl.md](archive/2026-05-28/m12-project-rename-impl.md)'s
milestone-completion summary for the full resolution log.
**Shipped to PyPI as `docs-cli==1.5.0` via M13 on 2026-05-29** —
mirrors the M10 → M11, M8 → M9 cadence.

**M17 — `docs-cli==1.6.0` shipped 2026-06-03.** The publish-only
milestone for the v1.6 train, batching **M14 + M15** into one
public release (as M9 batched M6+M7+M8; M11→M10 and M13→M12 were
one-to-one). M17 ran the [release-runbook.md](release-runbook.md)
end-to-end as a fully-autonomous pass: per-release re-verification
→ quality gate (510/510) → fresh artefact build → TestPyPI
rehearsal under `docs-cli-rehearsal==1.6.0` (squatter detour
continues) → real PyPI upload → chain-of-custody verified
bit-perfect (PyPI-served wheel sha256 `b0822709…` byte-identical
to the local Phase-4 build) → smoke + all seven M14 + M15 headline
contracts against the PyPI-served wheel → `v1.6.0` annotated tag
at the Phase-4 commit (`95f23a6`) + GitHub release → doc closeouts
(M14 + M15 + M17 milestone docs archived to `archive/2026-06-03/`;
the M17 impl log stays `Lifecycle: active`). Two M13 deviations
recurred as known-expected: the TestPyPI rehearsal wheel prints
`docs 0.0.0+local` under the rename detour, and `CHANGELOG.md` is
not in the sdist (so at M17 the wheel sha was byte-identical
Phase 2 ≡ Phase 4 while the sdist sha moved only because `docs/`
evolved between the builds). Full record in
[m17-pypi-publish-impl.md](m17-pypi-publish-impl.md)'s
milestone-completion summary.

**M20 — `docs-cli==1.6.5` shipped 2026-06-12.** The publish-only
counterpart to M19, shipped **one-to-one** (as M13 shipped M12 and
M11 shipped M10; M9 and M17 were the batched shapes). M20 ran the
[release-runbook.md](release-runbook.md) end-to-end as a
fully-autonomous pass: per-release re-verification → quality gate
(540/540) → fresh artefact build → TestPyPI rehearsal under
`docs-cli-rehearsal==1.6.5` (squatter detour continues) → real PyPI
upload → chain-of-custody verified **bit-perfect for both the wheel
(`aba36e92…`) AND the sdist (`f9de1eb4…`)** (M20 extended the M17
wheel-only check) → smoke + all M19 headline contracts against the
PyPI-served wheel → `v1.6.5` annotated tag at the Phase-4 commit
(`0855466`) + GitHub release → host-machine skill refresh (NEW vs
M17 — `docs install-skill --force` from the published wheel + a
workflow-skill sweep that caught + fixed one stale `--body-from`
reference in `project-foundation`) → doc closeouts (M18 + M19 + M20
milestone docs archived to `archive/2026-06-12/`; the M20 impl log
stays `Lifecycle: active`). The two M13 deviations recurred as
known-expected (TestPyPI rehearsal `0.0.0+local`; CHANGELOG in
neither sdist nor wheel — so the sdist sha moved from the GO-report
build only because `docs/` evolved). Full record in
[m20-pypi-publish-impl.md](m20-pypi-publish-impl.md)'s
milestone-completion summary.

**M24 — `docs-cli==1.8.0` (set up 2026-07-03, publish pending).** The
publish-only milestone shipping the post-1.6.5 train **batched** as
one public release — M21 (update-check, built 1.7.0) + M22 (doc-only,
no bump) + M23 (agent-aware install-skill, 1.8.0) — the batched shape
(M17 = M14+M15 → 1.6.0; M9 = M6+M7+M8 → 1.3.0). The tree is already at
1.8.0 (M23 Phase 7, merged to `main` at `839daef`); **1.7.0 is skipped
on PyPI** and its CHANGELOG entries fold up into the dated `## 1.8.0`
section (D2). M24 runs the [release-runbook.md](release-runbook.md)
(no TDD code phases). Unlike M20's fully-autonomous pass, M24 is driven
under the D3 "author now, confirm at the gate" decision — the runbook
walk starts only on an explicit operator go-ahead and pauses before
every irreversible / outward-facing step (real PyPI upload, `main`
push, `v1.8.0` tag, GitHub release). Closeout archives the M21 + M22 +
M23 pairs + the M24 milestone doc to `archive/<publish-date>/`; the M24
impl log, runbook, and status stay `Lifecycle: active`. Full record
will land in
[m24-pypi-publish-impl.md](m24-pypi-publish-impl.md)'s
milestone-completion summary.

**M13 — `docs-cli==1.5.0` shipped 2026-05-29.** The
publish-only counterpart to M12, mirroring M11 → M10. M13 ran
the [release-runbook.md](release-runbook.md) end-to-end:
per-release re-verification → quality gate (433/433) → fresh
artefact build → TestPyPI rehearsal under
`docs-cli-rehearsal==1.5.0` (squatter detour continues) → real
PyPI upload → chain-of-custody verified bit-perfect → smoke +
all four M12 headline contracts against the PyPI-served wheel →
`v1.5.0` annotated tag + GitHub release → doc closeouts. Two
M13 deviations recorded for v1.6+: the TestPyPI rehearsal wheel
prints `docs 0.0.0+local` (the M12 `importlib.metadata` SoT
can't resolve the renamed `docs-cli-rehearsal` distribution —
the version string is instead verified against the
canonical-name local + PyPI wheels), and `CHANGELOG.md` is not
shipped inside the sdist. Full record in
[m13-pypi-publish-impl.md](archive/2026-05-29/m13-pypi-publish-impl.md)'s
milestone-completion summary.

**M11 — `docs-cli==1.4.0` shipped 2026-05-27.** The publish-only
counterpart to M10, mirroring how M9 followed M8. M11 ran the
[release-runbook.md](release-runbook.md) end-to-end:
operator-state inventory (`~/.pypirc` intact, PyPI 1.4.0 slot
free, TestPyPI squatter unchanged) → fresh artefact rebuild under
canonical `name = "docs-cli"` (whl sha256 `7af7eb5c…`, tar.gz
sha256 `0b0dd2ce…`) → TestPyPI rehearsal under
`docs-cli-rehearsal==1.4.0` (squatter detour continues) → real
PyPI upload (chain-of-custody bit-perfect — PyPI-served wheel
sha256 byte-identical to local Phase 4 build) → smoke + headline
M10 contract against PyPI-served wheel → `v1.4.0` annotated tag
at the Phase 4 commit + GitHub release → doc closeouts. No code
work; no new verbs. The project-rename verb flagged as a
follow-on TODO at M10 closeout stays deferred to a later feature
milestone (leading candidate for v1.5). Full publish record +
deviations live in
[m11-pypi-publish.md](archive/2026-05-27/m11-pypi-publish.md)'s
milestone-completion summary.

**M10** bundles the two user-surfaced agent-driveability features
(`docs touch <file...>`, `docs migrate --apply` writes `.docs.toml`)
with the carry-overs from M3 (`[vocabulary] add_fields` allowlist —
moved out of Open questions below), M7 (`Confidence` enum), and M8
(`--quiet` per-file output suppression, `MigrationPlan.excluded_count`
removal, adoption-playbook restructure). Ships as 1.4.0. The M10
deliverable list and the 9 resolved Decisions (OQ-A through OQ-I,
operator-confirmed 2026-05-26) live in the milestone doc.

**M7** hardens `docs migrate`'s inference + introduces a breaking
controlled-vocab rename (`Status:` → `Lifecycle:`). It targets ≥50%
high-confidence plans on real trees (today: 25.3%) and surfaces
common real-world suffixes (`_Implementation`, `_Sketch`, etc.) +
project-name normalisation. Adds exactly **one new CLI flag** —
`docs migrate --config-project <name>` (the multi-project agent
override per F5); renames `docs list --status` → `--lifecycle`
in lockstep with the controlled-vocab field rename. Otherwise
pure inference + a convention change.

**M8** builds on M7's accurate plan with operator + agent
ergonomics: `--exclude` tree-wide (`.docs.toml` `[exclude]`
applies to `migrate` + `index` + `check` + `list`), triage flags
(`--summary`, `--only ambiguous`), `docs new --body-from` (closes
the harness's Read-before-Write friction), and a substantial
rewrite of the bundled skill's reference files to cover the
adoption flow. SKILL.md stays slim — one pointer line. Load-bearing
gate: fresh-subagent dogfooding of the adoption loop end-to-end.

**M9** — the publish milestone — shipped 2026-05-25. It
verified the pre-bumped `pyproject.toml` + `__version__` at
`1.3.0` (the bumps had pre-landed at M7 and M8 Phase 7;
CHANGELOG dated at M8 Phase 10), rebuilt fresh artefacts from
the post-M8 tree, rehearsed on TestPyPI under a disambiguated
dist name `docs-cli-rehearsal` (the bare `docs-cli` was parked
on TestPyPI by an unrelated user — real PyPI was clean),
published to real PyPI, flipped the GitHub repo to public,
tagged `v1.3.0` at the M8 simplify commit, and created the
GitHub release with hand-augmented notes. Doc closeouts ran
in lockstep. Token re-scope was deferred as out-of-band
operator UI work. Full record + deviations in
[m9-pypi-publish.md](archive/2026-05-25/m9-pypi-publish.md)'s milestone-completion
summary; the operative checklist
[release-runbook.md](release-runbook.md) stays the reference
for v1.4+ releases.

The parked `[vocabulary] add_fields` extra-field allowlist (see
_Open questions_ below) was scheduled into M10 as item #8 and is no
longer carried forward separately.

## Out of scope for v1

- Link-graph queries / `docs graph`.
- HTML or static-site rendering.
- Watch mode.
- Full-text search.
- Per-doc revisions / history (git owns this).
- Cross-root federation.
- Templates beyond `docs new` defaults. If users want richer scaffolds, they hand-edit after creation.

## Ongoing conventions

**Surface parity (CLI `--help` + bundled skill).** Any milestone that adds
or changes a CLI verb, flag, or user-visible behavior must land that change
in BOTH (a) the argparse `--help` strings in `src/docs_cli/cli.py` and (b)
the bundled skill `src/docs_cli/skill/` — `SKILL.md` and `references/` (with
`references/cli.md` and `references/convention.md` kept byte-identical to
`docs/cli.md` and `docs/convention.md`). It is part of
Phase 10 (Quality/Docs) done: run `docs <verb> --help` for each new/changed
verb and reconcile against the milestone's CHANGELOG surface, confirm the
bundled skill documents the new verbs/flags, and grep for stale wording
describing any *replaced* behavior. (Motivating miss: the
`docs new --body-from` help shipped in 1.6.0 still describing the
pre-M15-C4 "first 20 lines" heuristic.)

## Resolved questions

- **Archive selection is explicit, never relational** (M2, 2026-05-21; restated by M26, 2026-08-13). Archiving a doc must not silently pull its neighbours along. M2 made cascading a deliberate per-invocation choice; the original `--cascade` prompted `y/N`, and M14 (B1) replaced that prompt with pre-answerable flags. **M26 completes the decision:** relationship verbs supply the candidate set but never grant *authorization*, so bare `--cascade` and `--interactive` are retired and refuse (exit 2, nothing written), `--cascade-dry-run` previews the whole one-hop neighbourhood, and `--cascade-only GLOB` — validated as one complete plan before the first byte moves — is the only way to archive a related document. No `--no-cascade` is needed.
- **INDEX carries a one-paragraph description per doc** (M1). The renderer emits title + description + Status + Updated; the description is the doc's first body paragraph, trimmed to ~120 characters.
- **INDEX grouped by `Project` then `Role`** (M3, 2026-05-22). The renderer regroups active docs two levels deep — `## Project — <name>` (the docs-root project first, then alphabetical) then `### Active — <Role>` — with `## Archived` a single flat trailing section. Resolved by `Project`, not directory: it is metadata-driven, consistent with the convention's replacement of role-bucket subdirectories with `Role:` metadata, and parallel to `docs list --project`. Directory grouping was rejected for cutting against that convention.

## Open questions

_v1 (M1-M5) shipped 2026-05-20…2026-05-22 and v1.3.0 (M6-M9) shipped
2026-05-25. The previously-parked `[vocabulary] add_fields` extra-field
allowlist was scheduled into **M10** (v1.4.0) as item #8 — see the M10
milestone doc's Decisions section (OQ-F, OQ-H) for the final
rule-message shape and case-sensitivity decisions._

_No plan-level open questions are currently outstanding. M10's
milestone-scoped questions (OQ-A through OQ-I) were
operator-confirmed 2026-05-26 and promoted to the Decisions section
of [m10-adoption-polish.md](archive/2026-05-27/m10-adoption-polish.md)._
