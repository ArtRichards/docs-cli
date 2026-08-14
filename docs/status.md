# docs — Status

Lifecycle: active
Role: status
Project: docs
Updated: 2026-08-14

Related:
- pairs-with: plan.md
- pairs-with: archive/2026-05-24/m6-pypi-distribution.md
- pairs-with: archive/2026-05-25/m7-migration-accuracy.md
- pairs-with: archive/2026-05-25/m8-adoption-workflow.md
- pairs-with: archive/2026-05-25/m9-pypi-publish.md
- pairs-with: archive/2026-05-27/m10-adoption-polish.md
- pairs-with: archive/2026-05-27/m11-pypi-publish.md
- pairs-with: archive/2026-05-28/m12-project-rename.md
- pairs-with: archive/2026-05-29/m13-pypi-publish.md
- pairs-with: release-runbook.md
- pairs-with: archive/2026-06-03/m14-robustness-agent-native.md
- pairs-with: archive/2026-06-03/m15-agent-native-authoring.md
- pairs-with: archive/2026-06-01/m16-bundled-docs-skill-quality.md
- pairs-with: archive/2026-06-03/m17-pypi-publish.md
- pairs-with: m17-pypi-publish-impl.md
- pairs-with: archive/2026-06-12/m18-archive-edge-integrity.md
- pairs-with: archive/2026-06-12/m19-post-edit-validation.md
- pairs-with: archive/2026-06-12/m20-pypi-publish.md
- pairs-with: m20-pypi-publish-impl.md
- pairs-with: archive/2026-07-03/m21-update-check.md
- pairs-with: archive/2026-07-03/m21-update-check-impl.md
- pairs-with: archive/2026-07-03/m23-agent-aware-install-skill.md
- pairs-with: archive/2026-07-03/m23-agent-aware-install-skill-impl.md
- pairs-with: archive/2026-07-03/m24-pypi-publish.md
- pairs-with: m24-pypi-publish-impl.md
- pairs-with: m25-reciprocal-relationship-integrity.md
- pairs-with: m25-reciprocal-relationship-integrity-impl.md
- pairs-with: m26-safe-archive-selection.md
- pairs-with: m26-safe-archive-selection-impl.md
- pairs-with: m27-markdown-body-link-validation.md
- pairs-with: m27-markdown-body-link-validation-impl.md
- pairs-with: m28-move-safe-body-link-rewrites.md
- pairs-with: m29-pypi-publish-2-0-0.md

**This is the single source of truth for project progress. Update only this file when milestones complete or phases advance.**

## Current milestone

**M27 — Markdown body-link validation is the current milestone and is
implementation-complete: Step 1 on `m27/phases-1-4` and Step 2 on
`m27/phases-5-10`, all ten phases (2026-08-14). The live tree is repaired,
`docs check` is clean with both rules in force, and the suite is fully GREEN
at 1082 passed / 0 failed. The milestone stays `Lifecycle: active` until the
M29 publish closeout.** M27 adds a pure, stdlib-only, linear scanner over a
deliberately bounded Markdown grammar and makes a local body link whose
destination is missing a hard `docs check` error (`broken-body-link`, severity
`error`, exit 2), while producing nothing at all for code, examples, external
URLs, images, raw HTML, and plain-text mentions. Destinations resolve
**relative to the referring document** — the opposite of `Related:` —
fragments are preserved and never validated, and the scanner records the exact
character span of each destination token so **M28** can rewrite it without a
second parser. Setup measured the tree read-only and produced eight pieces of
evidence (**E1–E8**): **139 local destinations do not resolve, across 29
documents, and every one of them is under `archive/`** — the active tree is
clean; 132 of the 139 are a pure `../../` rebase that was never applied when
the document moved into the archive, 5 name a target that itself later moved,
and 2 name a bundled-skill file that never lived in the docs tree;
`docs check` exits **0** today with all 139 broken; and
`test_check_dogfood_repo_docs_is_clean` asserts this repository's own tree
exits 0, which makes the legacy-damage policy a **hard gate inside the suite**
rather than an aspiration. Setup also proved the parser risks are real on this
tree: without code masking the scan gains 4 false positives inside fenced code
(including `architecture.md:182`'s `[<path>](<path>)`) and 3 inside inline
code spans, while a 4-space indented-code rule would mask 9 spans that are
all **real links** in blockquote and list continuations — six of them
genuinely broken.

**All seven setup questions are RESOLVED** — Q1, Q2, and Q5 by the operator;
Q3, Q4, Q6, and Q7 conductor-resolved. **Q1: repair, and the rule stays
uniform** across archived and active documents. The deciding argument is
ownership rather than volume: this breakage class is produced by `docs archive`
itself — no version of the tool has ever rebased a moved document's body links,
and 8 of the 33 fixture trees already carry `archive/` directories — so a rule
exempting archived documents would leave the tool silent about the exact damage
it causes; and `docs/`, archive included, ships in every PyPI **sdist** and is
public on GitHub, where the worst-hit files (`plan.md`, `status.md`,
`release-runbook.md`, `cli.md`) are what a prospective adopter reads. The
one-time repair is destination-tokens-only, audited with an `Updated:` bump and
a dated `Revision:` bullet (M25 — D4's shape), and lands in **Phase 6** in the
same change that wires the rules; `convention.md` gains a third narrow
exception to archived-document immutability with a **stated blast radius**.
**Q5 was resolved against the setup recommendation and then amended**, and the
result is the milestone's second rule: `docs check` must never touch the
filesystem outside the tree it was pointed at — a check has to be a function of
the tree alone, since `charter.md:52` resolves today only because `docs/`
happens to sit beside `src/` in a checkout — but silently skipping such a link
would let a working link rot unnoticed. So an escaping destination is detected
by **path arithmetic alone** and reported as **`outside-root-body-link`**
(error, exit 2), an operator-approved post-draft scope addition following M25's
`duplicate-field` precedent. Containment is tested **before** existence so the
two rules never double-report, `convention.md` adopts the invariant *a local
Markdown body link stays inside the tree root; anything outside the tree is a
URL*, `cli.md` states the boundary explicitly, and `charter.md:52` is converted
to the canonical GitHub URL in Phase 6 — the same treatment Q1 gives the two
`adoption-playbook` links, and doubly right because the relative alternative
would itself have violated Q5. A containment census over `docs/`, all 33
fixture trees and the bundled skill confirms **exactly one** escape exists and
**no fixture needs updating**. **Phase 1 re-opened none of this**: it froze the
grammar and its exactness rules, the masking contract and its ordering,
destination classification, the containment test and **its precedence over
existence**, **both** message templates, and the `BodyLink` span record — in
`cli.md` › *Markdown body-link validation*, `convention.md` › *Body links*,
and the milestone's *Decisions (Phase 1 — BINDING)*. Three setup-frozen items
were amended under conductor decision and recorded as amendments:
`broken-body-link`'s message (D4's "to a file" contradicted the
operator-binding Q7, under which a **directory** also satisfies a
destination), `outside-root-body-link`'s message (D4b never gave one), and the
33-tree no-new-findings lock (a **new sibling** test, because the existing
one's list covers 23 trees and would fail on the damaged `bodylink-*`
fixtures). The package version stays **1.8.0**
(M25 — D6); CHANGELOG entries accumulate under `UNRELEASED` for M29. The
prepared pair is
[m27-markdown-body-link-validation.md](m27-markdown-body-link-validation.md)
and
[m27-markdown-body-link-validation-impl.md](m27-markdown-body-link-validation-impl.md).

**M26 — Safe explicit archive selection is
implementation-complete — all ten TDD phases done 2026-08-13 (Step 1 on
`m26/phases-1-4`, Step 2 on `m26/phases-5-10`). Full suite 895 GREEN, with
774 of the 777 pre-existing test ids mechanically proven present and passing
and 3 deliberately removed.** M26 decouples relationship context from archive
authorization: bare `docs archive FILE --cascade` refuses before any write,
`--interactive` is retired under the same refusal, `--cascade-dry-run` keeps
previewing every one-hop candidate (selected, not-selected, or ineligible),
and every write that includes a related document requires an explicit
`--cascade-only GLOB` scope whose full plan is validated — deduplicated,
canonical-path matched, collision- and writability-checked, archived
neighbours excluded — before the first byte moves. `docs archive` also gains a
`--json` operation-plan record, one shape for preview and apply, reusing
M25's `relate --json` pattern. Setup reproduced five concrete v1.8.0 defects
(**E1–E5**), each now mapped to named regression coverage: the headline is
that `docs archive m25-reciprocal-relationship-integrity.md --cascade` would
archive `plan.md`, `cli.md`, `convention.md`, `test-strategy.md`, and
`status.md` — this project's whole specification spine — with no prompt; a
basename collision or a typo'd scope leaves a partial archive that exits 0;
and an archive-subtree `pairs-with` edge makes `--cascade` silently relocate
and re-date an already-archived document (data corruption, load-bearing here
because `status.md` carries 20+ archive-subtree edges). **All seven setup
questions are RESOLVED** — Q1 retire `--interactive`, Q2 keep the refusing
flags registered, Q3 retain the `pairs-with`/`child-of` candidate set, Q4
exclude archived candidates and refuse an archived primary, Q5 pre-flight
everything with a partial-state admission instead of rollback (extending
M25 — D5's rollback to N docs explicitly declined), Q6 add
`docs archive --json`, Q7 no primary-only candidate notice. Phase 1 did not
re-open them: it froze the compatibility matrix (no "it depends" cell), the
refusal / preview / apply / partial-state message catalog, the exit-code split
(exit 1 stays for the three conditions 1.x already assigned it; the five new
M26 refusals exit 2), the `--json` schema and field table, and the Phase-5
signatures — in `cli.md`, `convention.md`, and the milestone's *Decisions
(Phase 1 — BINDING)* section, which also records seventeen resolved Step-1
planning questions. **A preview never fails**: a `--cascade-only` that selects
nothing exits 0 under `--cascade-dry-run` and 2 on a write, and the D5/D6
contradiction that allowed both readings is amended away. The package version
stays **1.8.0** (M25 — D6); CHANGELOG entries accumulate under `UNRELEASED`
for M29. The prepared pair is
[m26-safe-archive-selection.md](m26-safe-archive-selection.md) and
[m26-safe-archive-selection-impl.md](m26-safe-archive-selection-impl.md).

**M25 — Reciprocal relationship integrity and `docs relate` is
IMPLEMENTATION-COMPLETE — all ten TDD phases are done
(Phases 1–4 2026-08-11 amended 2026-08-12 on `m25/phases-1-4`; Phases 5–10
2026-08-12 on `m25/phases-5-10`). It stays `Lifecycle: active` until the
M29 publish closeout.** M25 defines three reciprocal relationship
pairs (`precedes`/`follows`, `depends-on`/`required-by`, and
`blocks`/`blocked-by`), makes a missing exact inverse a hard `docs check` error,
and adds explicit two-endpoint `docs relate add/remove` repair, including a
narrow reasoned/audited exception for archived endpoints. Phase 1 froze the
whole surface in the milestone's *Decisions (Phase 1 — BINDING)* section and in
`cli.md` / `convention.md`: the six-verb inverse map, the `missing-inverse`
finding and its exact message, the `relate` grammar / human / JSON / dry-run
output, root-relative-first endpoint resolution, the archived `--reason` +
`Revision:` audit rules, and the staged-publish-with-rollback failure contract.
All five Phase-1 open questions are RESOLVED. Phase 2 wrote the RED suite
across six edited and two new test files, Phase 3 added ten committed
`reciprocal-*` fixture trees, and Phase 4 captured the classified RED
baseline. Including the same-instance audit and the fresh-eyes review
fold-in, Step 1 contributed **121 test items** and the RED baseline was
**757 collected, 87 failed, 670 passed** — every RED matching its classified reason, zero
collection errors, and the 636 pre-existing tests all still GREEN. The
review returned **no blockers**; its two operator-binding contract
amendments (a self-referential recognized edge is **exempt** from
`missing-inverse`, and reciprocity matches on **canonical** root-relative
paths so a `./` prefix cannot fail a hard check) are folded into the
specs, the bundled mirrors, and the tests. **Step 2 (Phases 5–10) is
complete on `m25/phases-5-10`: the full suite is 777 passed / 0 failed,
every one of the 636 pre-existing test ids proven still GREEN by `comm`
against the Phase-1 commit, and the eight-flow dogfood ran unattended on a
throwaway copy of this tree.** Phase 5 landed the vocabulary, the three
`Related:`/`Revision:` editors, the planning models, and the `Revision`
built-in label; Phase 6 landed the cross-document reciprocity pass
(interleaved into `check_tree`'s per-doc grouping) and the
validate-all-first coordinated edit with its staged-publish-and-rollback
contract; Phase 7 wired `docs relate add|remove`, added the bundled
skill's verb row, opened an `UNRELEASED` CHANGELOG section, and folded
eight conductor-resolved spec corrections into `cli.md` (a
nothing-was-published rollback branch, a remove-shaped `ROLLBACK FAILED`
admission, the stage-3 refusal string, root-relative promises scoped to
*resolved* endpoints, the `--json`-on-failure rule, and `Revision:`
following the tree's `date_format`). Phase 8 proved the GREEN gate and zero
pre-existing regressions — and corrected, under operator approval, one
Step-1 assertion that was unsatisfiable alongside another test in the same
file (the replacement is stronger; the shipped behaviour did not move).
Phase 9 dogfooded detect → repair → re-check plus an audited archived
repair, touching 1 of 46 archived files. Phase 10 closed
`architecture.md` / `test-strategy.md`, added the upgrade-and-repair flow to
the shipped use-case catalog, and wrote the completion summaries. An
independent fresh-eyes review then returned **no blockers**; its fold-in
fixed two real editor defects (trailing-newline state was not preserved
when the metadata block runs to EOF — a D4 allowed-byte violation; and a
re-created `Related:` group landed after a trailing `Revision:` group),
added four missing failure-path locks, and carried one
**operator-approved post-freeze scope addition**: the **`duplicate-field`**
check rule (D7). A metadata label may now appear at most once — a second
copy silently replaced the first and discarded its values, a data-loss
defect predating M25 that also made one `missing-inverse` state unfixable.
The live tree and all 28 fixture trees were verified duplicate-free before
it landed. Suite: **777 passed**.
**Version staging (Q5):
`docs-cli` stays `1.8.0` through M25–M28; M29 performs the single bump to
`2.0.0` at publish.** The prepared pair is
[m25-reciprocal-relationship-integrity.md](m25-reciprocal-relationship-integrity.md)
and
[m25-reciprocal-relationship-integrity-impl.md](m25-reciprocal-relationship-integrity-impl.md).

The full breaking safety train is registered in execution order:

- **M26 — Safe explicit archive selection (IMPLEMENTATION-COMPLETE
  2026-08-13, all ten TDD phases, 895 GREEN):** unscoped related-document
  writes refuse; preview remains and names the whole neighborhood; explicit
  `--cascade-only` scope is required, planned in full before any write;
  `docs archive --json` emits the operation plan. Stays `Lifecycle: active`
  until the M29 publish closeout.
- **M27 — Markdown body-link validation (IMPLEMENTATION-COMPLETE
  2026-08-14, all ten phases, all seven setup questions RESOLVED):** a bounded stdlib-only
  scanner with exact destination spans; two hard errors —
  `broken-body-link` for a missing in-root destination and
  `outside-root-body-link` for one that leaves the tree, decided by path
  arithmetic so the check never stats outside its own root; and a one-time
  audited repair of the live tree's 139 archived breaks (all under `archive/`,
  132 of them a single un-rebased `../../`) plus the one escaping active
  link.
- **M28 — Move-safe body-link rewrites:** depends on M26 + M27; preserves both
  incoming links to moved targets and links inside moved referrers.
- **M29 — PyPI publish 2.0.0:** depends on M25–M28 and releases them together.

The five plans use reciprocal sequence edges and only real durable dependency
edges; no `blocks`/`blocked-by` edge exists because planned prerequisites are
not transient blockers. M26 and M27 both have full task plans and
implementation logs; M28–M29 remain draft stubs with no implementation logs or
phases started.
Because those edges are already complete in both directions,
this tree passes M25's new hard rule as-is — the existing dogfood
`docs check docs/` gate doubles as an M25 lock.

**docs-cli 1.8.0 shipped 2026-07-03 — the v1.8.0 train is complete.**
**M24 — PyPI publish 1.8.0** is **Complete (2026-07-03)**: `docs-cli==1.8.0`
is live at https://pypi.org/project/docs-cli/1.8.0/, the operator-driven
**batched** publish of the whole post-1.6.5 train — **M21** (update-check,
built as 1.7.0) + **M22** (doc-only root-placement guidance, no bump) + **M23**
(agent-aware install-skill, 1.8.0) — as one public release (mirroring M17 =
M14+M15 → 1.6.0 and M9 = M6+M7+M8 → 1.3.0). **1.7.0 was skipped on PyPI** — its
CHANGELOG entries were folded into the dated `## 1.8.0` section (D2). The
`v1.8.0` annotated tag points at the Phase-4 dated-CHANGELOG commit
(`1a01f74`); the GitHub release carries the `## 1.8.0` notes. Chain-of-custody
verified **bit-perfect for both wheel AND sdist** — PyPI-served wheel `29ac3ced…`
+ sdist `62a29285…` byte-identical to the local Phase-4 build; all M21 + M23
headline contracts hold against the PyPI-served wheel (update notice + M23
skill-refresh hint fire to STDERR under the seeded-cache probe, exit-parity,
full suppression matrix; install-skill `--dest` records path-only, non-TTY
falls back to default, "agent skill" wording). Ran the
[release-runbook.md](release-runbook.md) on `main` (no TDD code phases) —
driven under **D3** "author now, confirm at the gate": the operator authorized
the irreversible upload + `main` push + tag + release at the Phase-4 gate (not
M20's up-front full-autonomous authorization). **D4:** M23 OQ-1/OQ-2 confirmed
as-shipped (branch-review flag cleared, no re-bump). The closeout refreshed the
host-machine skills (`docs install-skill --force` → host `docs` byte-identical;
workflow-skill sweep found no docs-cli drift this release) per the CLAUDE.md
skill-update-flow policy, and archived the M21 + M22 + M23 pairs + M24's own
milestone doc to `archive/2026-07-03/`; the M24 impl log, release-runbook, and
this status doc stay `Lifecycle: active`. Full publish record + deviations live
in [m24-pypi-publish-impl.md](m24-pypi-publish-impl.md)'s milestone-completion
summary.

**M22 — Doc-tree root placement guidance (project ≠ directory)** is
**implementation-complete (2026-06-24)** — all ten TDD phases done; full
suite 543 GREEN, ruff/format/mypy clean, `docs check docs/` exit 0; Phase-9
dogfood empirically reproduced the redundant-prefix consequence. It **stays
LIVE at root, lifecycle `active`**, to be swept into the archive at the next
publish closeout (the M18/M19/M21 + M16 precedent — feature/skill milestones
ride live until a later milestone archives them). A documentation-only,
M16-shaped milestone (no CLI/code
change, no version bump): it adds "where to put `.docs.toml`" guidance to
`convention.md` §Subdirectories and the bundled `SKILL.md`, making explicit
that `Project:` is a metadata slug — **not** a directory — and that because
`Related:` paths are root-relative, nesting a lone project beneath a parent
root prefixes every intra-project sibling reference with a redundant
`<subdir>/`. Default: a single project's docs root is the project's own
directory (root = project, docs flat, clean refs); reserve per-project
subdirs under one shared root for genuinely multi-project trees. Scoped to
run **before** M21 (operator decision 2026-06-24 — run-order before M21, no
renumber; milestone numbers here are creation-order, not execution order, as
M14+M15→M17 / M18+M19→M20 already show). The matching `project-foundation`
note is a separate companion follow-on in the `agent-playbook-suite` repo
(tracked with the workflow-skill drift-lint follow-on). Pair:
[m22-root-placement-guidance.md](archive/2026-07-03/m22-root-placement-guidance.md) +
[m22-root-placement-guidance-impl.md](archive/2026-07-03/m22-root-placement-guidance-impl.md);
**shipped to PyPI as `docs-cli==1.8.0` (batched via M24) 2026-07-03; the pair is now archived to `archive/2026-07-03/`.**

**M21 — Update-check notification (PyPI new-version notice)** is
**Complete — shipped to PyPI as `docs-cli==1.8.0` (batched via M24) 2026-07-03;
pair archived to `archive/2026-07-03/`**: **all 10 TDD phases are complete (2026-06-29)** —
Phases 1–4 (RED baseline) on branch `m21/phases-1-4`, Phases 5–10 on
`m21/phases-5-10`. The `update_check.py` seam (cache I/O, numeric fail-closed
compare, injectable `urllib` fetch hook, suppression predicates, notice
formatter) + the `main()` post-dispatch hook are implemented; `pyproject` is at
**1.7.0** (editable reinstall → `docs --version` = `docs 1.7.0`); the full suite
is **604 GREEN** (+4 from the 2026-06-29 Step-2 fresh-eyes review fold-in) with
the gate clean tree-wide (ruff / ruff format --check /
mypy / `docs check docs/`). The Phase-9 online path was verified against live
PyPI (real `urllib`) and dogfooded end-to-end (notice / both 24h throttles /
the full suppression matrix / `--json` byte-clean stdout / exit-code parity);
pytest stays 100% offline. **Re-scoped to CLI-only 2026-06-29**
(was "PyPI version check + skill-refresh nudge"): the former offline skill-drift
notice (D5) and the dual-action `docs install-skill --force` half are **CUT**,
and the skill story moves to the new follow-on **M23**. Headline: `docs-cli`
checks PyPI for a newer release and, once per 24h and **fail-silent**, emits ONE
STDERR line nudging the user/agent to update **the CLI**
(`pip install -U docs-cli`). New reference wording:
`docs: update available <current> -> <latest> — run: pip install -U docs-cli`.
This is the tool's **first network surface** (stdlib `urllib` only, 1.0s
timeout, 24h-cache-gated under
`${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json` with a three-key
`{last_check, latest_version, last_notified}` schema, fail-silent always — the
zero-dependency wheel preserved). The notice is STDERR-only, **never** alters
the exit code, and is suppressed under `--quiet` / `--json` / `CI` /
`DOCS_CLI_NO_UPDATE_CHECK` / `DO_NOT_TRACK` (a user-level config opt-out is
DEFERRED out of v1.7.0 — OQ-5/5a) — but **deliberately shows on non-TTY**
(inverting gh's TTY rule) because the agent is the actor who performs the
update. Ships as **1.7.0** (minor bump — additive feature; 1.6.5 was the
operator-decreed patch exception); the PyPI publish is a later operator-driven
milestone (the M19→M20, M14+M15→M17 pattern). The milestone pair is
[m21-update-check.md](archive/2026-07-03/m21-update-check.md) +
[m21-update-check-impl.md](archive/2026-07-03/m21-update-check-impl.md); the pair was swept to `archive/2026-07-03/` at the M24 closeout (the
M14/M15/M18/M19 precedent). **OPEN QUESTIONS are netted out — none outstanding.** The original
OQ-1..OQ-9 are RESOLVED (conductor decisions 2026-06-12, each per the
recommended default) with one amendment by the re-scope: **OQ-6 (ship D5) is
REVERSED to NO** (D5 CUT; skill story → M23); the dual-notice ordering question
is moot (single notice now). Surviving resolved findings: the dedicated
`update_check.py` module stands (OQ-7; the B3 wheel-contents test tolerates it);
the suite sets `DOCS_CLI_NO_UPDATE_CHECK=1` in `tests/conftest.py` to stay
offline; cache timestamps are ISO-8601 UTC; the baseline test count is **543**.
**Shipped to PyPI as `docs-cli==1.8.0` (batched via M24) 2026-07-03.** See the
milestone doc's Decisions › "Re-scope to CLI-only".

**M23 — Agent-aware install-skill + recorded-dest skill-refresh hint** is
**Complete — shipped to PyPI as `docs-cli==1.8.0` (batched via M24) 2026-07-03;
pair archived to `archive/2026-07-03/`** — the follow-on that restores the
skill-refresh nudge cut from M21. **All ten TDD phases are done (2026-07-02)** — Phases 1–4
(Contract & RED baseline) on branch `m23/phases-1-4`, Phases 5–10 on
`m23/phases-5-10`: the full suite is **636 GREEN**, gate clean tree-wide
(ruff / format / mypy / `docs check docs/` all clean), `pyproject` at **1.8.0**
(editable reinstall → `docs --version` = `docs 1.8.0`), and the online path was
dogfooded end-to-end against a seeded throwaway cache (pytest stays 100%
offline). It
makes `docs install-skill` **agent-aware**: `--dest` is the agent-agnostic
source of truth, resolution is TTY-aware (a human may be prompted; an agent
[non-TTY] is **never** blocked on a prompt → falls back to the default), the
resolved dest is **recorded** to a small per-user state file (a *path* only —
**never** the skill's content), the "Claude Code skill" framing in
`install-skill`'s help/description/docstrings is neutralised to
**"agent skill"** (reconciled with `cli.md`; a stale-wording grep across the
install-skill surface is clean), and M21's update notice gains a
skill-refresh hint pointed at the **recorded** dest (riding M21's same
suppression matrix + throttle). Replay/remember is allowed; content-inspection
and agent-guessing are NOT (the exact line the cut D5 crossed). Out of scope:
multi-agent skill *formats* and agent auto-detection. **Depends on M21**
(extends its notice channel). Ships **1.8.0** (OQ-4). **The four OPEN
QUESTIONS are resolved** (see the milestone doc Decisions): OQ-1 = non-TTY
**default** (never refuse), OQ-2 = a **separate** `${XDG_STATE_HOME:-~/.local/state}/docs-cli/install-skill.json`
(M21's 3-key cache stays frozen), OQ-3 = last-write-wins single dest, OQ-4 =
**1.8.0** — OQ-1/OQ-2 were resolved **provisionally while the operator was
away** and were **confirmed as-shipped at the M24 publish gate (D4, 2026-07-03)** —
the branch-review flag is cleared. The pair is
[m23-agent-aware-install-skill.md](archive/2026-07-03/m23-agent-aware-install-skill.md) +
[m23-agent-aware-install-skill-impl.md](archive/2026-07-03/m23-agent-aware-install-skill-impl.md);
the pair was archived to `archive/2026-07-03/` at the M24 closeout.

**docs-cli 1.6.5 shipped 2026-06-12 — the v1.6.5 train is complete.**
**M20 — PyPI publish 1.6.5** is **Complete (2026-06-12)**:
`docs-cli==1.6.5` is live at https://pypi.org/project/docs-cli/1.6.5/, the
operator-driven publish-only counterpart to **M19**, shipped **one-to-one**
(as M13 shipped M12 and M11 shipped M10; M9 and M17 were the batched shapes).
The `v1.6.5` annotated tag points at the M20 Phase-4 dated-CHANGELOG commit
(`0855466`); the GitHub release carries the `## 1.6.5` CHANGELOG notes.
Chain-of-custody verified **bit-perfect for both the wheel AND the sdist**
(M20 extended the M17 wheel-only check) — PyPI-served wheel sha256
`aba36e92…` + sdist `f9de1eb4…` byte-identical to the local Phase-4 build;
all M19 headline contracts hold against the PyPI-served wheel (`touch
--check` exit fold clean/stale; `--stale` requires `--check`; `[check]
stale_days` arms bare check + CLI override + non-integer refusal; both
provenance variants; `--body-from` help = real detector). Ran the
[release-runbook.md](release-runbook.md) end-to-end as a fully-autonomous
pass (no TDD code phases — the runbook sections are the phases, on `main`).
**NEW vs M17:** the Phase-5 closeout refreshed the host-machine skills
(`docs install-skill --force` from the published 1.6.5 → host `docs` skill
byte-identical to the published bundled skill; a workflow-skill sweep that
caught + fixed one stale `--body-from` reference in `project-foundation`) per
the CLAUDE.md skill-update-flow policy. The M20 closeout archived the M18
pair + the M19 pair + M20's own milestone doc to `archive/2026-06-12/`; the
M20 impl log, release-runbook, and this status doc stay `Lifecycle: active`.
Full publish record + deviations live in
[m20-pypi-publish-impl.md](m20-pypi-publish-impl.md)'s milestone-completion
summary.

**M19 — Post-edit validation ergonomics (touch --check + configurable stale
window)** is **Complete (2026-06-12)** — **shipped to PyPI as
`docs-cli==1.6.5` via M20 on 2026-06-12** (operator decision 2026-06-12 —
1.6.5, not 1.7.0; M20 was the publish-only milestone, one-to-one). Three
deliverables: (D1) `docs touch --check [--stale N]` folds the existing
`check_tree` machinery into `docs touch` after its end-of-batch reindex, so
the three-command post-edit loop (`touch` → `index` → `check --stale 14`)
collapses to one invocation; (D2) a `.docs.toml [check] stale_days = N`
per-tree default the stale window reads from when no CLI `--stale` is given
(CLI `--stale` overrides; absent config preserves today's behaviour); (D3)
the cosmetic `docs new --body-from` help-string fix closing the rolled-forward
follow-on. No new verb, no new check rule — additive + backward-compatible.
A post-draft operator addition (2026-06-12) folds **threshold provenance** into
D2 — the stale finding names where the window is set (`set in .docs.toml
[check] stale_days` config-sourced, `via --stale` CLI-sourced). The milestone
pair is
[m19-post-edit-validation.md](archive/2026-06-12/m19-post-edit-validation.md)
+ [m19-post-edit-validation-impl.md](archive/2026-06-12/m19-post-edit-validation-impl.md);
it was archived to `archive/2026-06-12/` at the M20 closeout. The six questions (Q1–Q6 — exit-code folding, check
scope, `--stale`-without-`--check`, `--dry-run --check`, whether a configured
`stale_days` makes bare `docs check` apply the stale rule, and whether it
feeds `docs list --stale`) are **RESOLVED** (operator decisions 2026-06-12,
each per the recommended default — see the milestone doc's Decisions). **Step 1
(Phases 1-4 — Contract + RED baseline) complete on branch `m19/phases-1-4`**
(2026-06-12): contract specs frozen, 23 new tests written RED across 5 suites +
the version-pin flip to 1.6.5, inline today-relative fixtures, RED baseline
captured (533 collected, 19 RED, 514 GREEN). **Step 2 (implement & ship,
Phases 5-10) complete on branch `m19/phases-5-10`** (2026-06-12):
`Config.stale_days` + `load_config` `[check]` read, `resolve_stale`
precedence/provenance helper, `stale_source` threading, `touch --check`/`--stale`
flags (Phase 5); `check_doc` provenance suffix + `_cmd_touch` check-fold +
`_run_touch_check`/`_print_check_findings` + D3 help fix (Phase 6, after the
mandatory OQ-2 message-regression audit — zero regression); version 1.6.5 +
packaging lockstep + `## 1.6.5 — UNRELEASED` CHANGELOG (Phase 7); **full suite
533/533 GREEN, gate clean, `docs --version` → `docs 1.6.5`** (Phase 8); all 5
dogfood exercises GREEN + config path verified on a throwaway `docs/` copy
(OQ-3 — repo tree not adopted) (Phase 9); surface-parity gate + SKILL.md verb
table (OQ-4) + standalone `python -m build` & `twine check` both PASSED locally
(Phase 10). The full suite reached **540 GREEN** (533 + the Step-2 review +7).
**M20 published it to PyPI as `docs-cli==1.6.5` on 2026-06-12**; the M19 pair
was archived to `archive/2026-06-12/` at the M20 closeout.

**M18 — Archive edge integrity (intra-archive Related: rewriting)** is
**implementation-complete (2026-06-03)**. The correctness fix to
`docs archive` (rewrite the moved doc's own archive-subtree `Related:`
edges + repoint already-archived referrers, via the conditioned
archived-skip in `_rewrite_referring_edges`) landed, and its Phase-9 payoff
archived the completed-milestone backlog on the live tree — see the
*Completed-milestone doc archival is DONE* note below. **The M18 pair was
archived to `archive/2026-06-12/` at the M20 closeout** (it rode along in the
1.6.0 tree as an already-merged archive-edge fix and added no new public
surface to 1.6.5; the archival is a doc-lifecycle sweep, not a code ship).
Full suite 510 GREEN at M18 close, gate clean tree-wide.

**M16 — Bundled docs skill quality artifacts** was implementation-complete
2026-06-01 and is now **archived** (trio → `archive/2026-06-01/` by M18's
Phase-9 sweep): the Agent Playbook Suite risk-aware quality upgrade, scoped
to the bundled `docs` skill under `src/docs_cli/skill/` (document test
matrices, quality logs, generated report artifacts, and the mechanical
limits of `docs check`). The milestone pair is now
[archive/2026-06-01/m16-bundled-docs-skill-quality.md](archive/2026-06-01/m16-bundled-docs-skill-quality.md)
+ [archive/2026-06-01/m16-bundled-docs-skill-quality-impl.md](archive/2026-06-01/m16-bundled-docs-skill-quality-impl.md).

**Completed-milestone doc archival is DONE (2026-06-03), via M18.** The
[M18 — Archive edge integrity](archive/2026-06-12/m18-archive-edge-integrity.md) fix landed
(the conditioned archived-skip in `_rewrite_referring_edges`), and its
Phase-9 payoff archived the completed-milestone backlog on the live `docs/`
tree in strict completion-date order — `docs check docs/` exit 0 after every
op and at the end. Manifest:
- M1–M9 plan/log pairs → `archive/2026-05-{20,21,22,22,23,24,25,25,25}/`
  (each archived the LOG with `--cascade-only "<plan>"`; `child-of` pulls
  the plan, so both land together edge-clean);
- M12 plan/impl pair → `archive/2026-05-28/`;
- the three stray impl-logs swept into their plans' existing folders —
  `m10`/`m11` → `archive/2026-05-27/`, `m13` → `archive/2026-05-29/`
  (each repointed its already-archived plan's `parent-of` edge, the M18
  D2 flip);
- the M16 trio (plan + impl + test-matrix) → `archive/2026-06-01/`
  (`--cascade-only "m16-*"`).
Live referrers (architecture.md, plan.md, status.md, release-runbook.md)
were repointed automatically to the new archive paths. **M18 (both pairs)
is LEFT LIVE at root** — it is itself the in-flight milestone (a milestone
is not self-archived; it flips to `archived` only when a later milestone
sweeps it in). **M14 + M15 + M17 were archived to `archive/2026-06-03/` at
the M17 closeout** (see the v1.6-publish note below).

**docs-cli 1.6.0 shipped 2026-06-03 — the v1.6 train is complete.**
**M17 — PyPI publish 1.6.0** is **Complete (2026-06-03)**:
`docs-cli==1.6.0` is live at https://pypi.org/project/docs-cli/1.6.0/,
the operator-driven publish that shipped **M14 + M15 together** as one
public release (batched, as M9 shipped M6+M7+M8; M11→M10 and M13→M12 were
one-to-one). The `v1.6.0` annotated tag points at the M17 Phase-4
dated-CHANGELOG commit (`95f23a6`); the GitHub release carries the
`## 1.6.0` CHANGELOG notes. Chain-of-custody verified **bit-perfect**
(PyPI-served wheel sha256 `b0822709…` byte-identical to the local Phase-4
build); all seven M14 + M15 headline contracts hold against the
PyPI-served wheel (M14 `mv` all-or-nothing; M14 `new` strict-root refusal;
M14 non-interactive `archive --cascade` + `--cascade-dry-run`; M14
four-verb exclude-honouring reindex; M15 `project set` atomic + typo
guard; M15 single-file `stamp`; M15 `--body-from` real-frontmatter
detector). Ran the [release-runbook.md](release-runbook.md) end-to-end as
a fully-autonomous pass (no TDD code phases — the runbook sections are the
phases, mirroring M9/M11/M13). Full publish record + deviations live in
[m17-pypi-publish-impl.md](m17-pypi-publish-impl.md)'s
milestone-completion summary.

- **M14 — Robustness + autonomous archive** (impl-complete 2026-06-02):
  `docs mv` atomicity, `docs new` strict-root refusal, the four-verb
  `touch`/`archive`/`mv`/`project rename` exclude-predicate fix,
  slug/`OSError`/`atomic_write`-fsync guards, non-interactive
  `archive --cascade`, the bundled-ref guard + packaging fix.
- **M15 — Agent-native doc authoring** (impl-complete 2026-06-03, carved
  from M14): `docs project set`, single-file `docs stamp`
  (write-then-stamp), the `--body-from` real-frontmatter detector, and
  the skill/cli docs. **Depends on M14.**

Both built `docs-cli==1.6.0` locally against the same CHANGELOG section;
M17 published them together. Their milestone pairs (plan + impl, four
docs) **and** the M17 milestone doc were archived to `archive/2026-06-03/`
at the M17 closeout via `docs archive` (the Q2 decision); the M17 impl
log, release-runbook, and this status doc stay `Lifecycle: active` per the
M8/M9/M10/M11/M13 pattern. **M18 is untouched — a separate in-flight
milestone.**

**docs-cli 1.5.0 shipped 2026-05-29.** **M13 — PyPI publish
1.5.0** is **Complete (2026-05-29)** — `docs-cli==1.5.0` is
live at https://pypi.org/project/docs-cli/1.5.0/, the
publish-only counterpart to M12 (mirroring M11 → M10 and
M9 → M8). The `v1.5.0` annotated tag points at the M13 Phase 4
commit; the GitHub release carries the `## 1.5.0` CHANGELOG
notes. Chain-of-custody verified bit-perfect (PyPI-served
wheel sha256 byte-identical to the local Phase 4 build); all
four M12 headline contracts (project rename round-trip; touch
outside-root refusal; archive referring-edge rewrite;
`importlib.metadata` version SoT) hold against the PyPI-served
wheel. The milestone pair is
[m13-pypi-publish.md](archive/2026-05-29/m13-pypi-publish.md)
(archived at closeout) +
[m13-pypi-publish-impl.md](archive/2026-05-29/m13-pypi-publish-impl.md); the
operative checklist was
[release-runbook.md](release-runbook.md). Full publish record
+ deviations live in the impl log's milestone-completion
summary.

**M12 — Project rename + M11 wart fixes + version SoT (v1.5.0)**
is **Complete (2026-05-28)** — `dist/docs_cli-1.5.0-py3-none-any.whl`
+ `dist/docs_cli-1.5.0.tar.gz` built locally, twine check PASS,
433/433 pytest GREEN at simplify close; PyPI publish is M13's
scope (mirroring the M10 → M11, M8 → M9 cadence). M12 bundled four threads in
one TDD cycle:

1. **`docs project rename <new-name>`** — operator-facing
   headline; the M10 follow-on TODO captured at
   [archive/2026-05-27/m10-adoption-polish.md](archive/2026-05-27/m10-adoption-polish.md)
   lines 261-268. Atomic semantics (validate up-front, fail the
   whole batch on any error, commit only after validation pass,
   refresh INDEX once at end) mirroring `docs touch` (M2) +
   `docs migrate --apply` (M10). Rewrites `.docs.toml`
   `[project] name` + every conformant `Project:` line across
   active docs. Archive subtree is read-only (M3 stance).
2. **`docs touch <path>` outside any docs root → exit 2.**
   Burn-down of the M11 Phase 5 wart: `docs touch` on a file
   outside any `.docs.toml`-rooted tree currently inserts an
   unwanted `Updated:` line and then crashes the downstream
   INDEX refresh on whatever sibling first fails its Lifecycle
   check (M11 caught this when accidentally touching
   `CHANGELOG.md` from the repo root). M12 refuses cleanly with
   exit 2 + clear stderr; file unchanged; no INDEX refresh.
3. **`docs archive <doc>` rewrites referring `Related:` edges.**
   Burn-down of the M11 Phase 5 wart: archiving a doc moves
   the file but leaves referring `Related:` edges in other docs
   pointing at the pre-archive path (M11 Phase 5 ran a manual
   cleanup for `status.md` + impl log). M12 makes the rewrite
   atomic with the move — same machinery `docs mv` already
   uses (M2 Phase 6).
4. **`importlib.metadata` version single-source-of-truth.**
   Parked since M6. `src/docs_cli/cli.py` `__version__` becomes
   `importlib.metadata.version("docs-cli")`; `pyproject.toml`
   `version` is the single SoT. Eliminates the two-place version
   hardcode (and the corresponding lockstep-bump discipline) at
   every implementation milestone.

M12 shipped locally as 1.5.0 on 2026-05-28. The four features
(`docs project rename`, `docs touch` outside-root refusal,
`docs archive` referring-edge rewrite, `importlib.metadata`
version SoT) all landed atomically; the validate-all-first
pattern proved robust across the 17 project-rename + 4 touch +
6 archive new tests. Phase 9 dogfood PASS on all four
exercises (kebab-tiny round-trip byte-identical; orphan touch
refused; archive referring-edge rewrite atomic; repo's own
docs/ round-tripped byte-identical). OQ-1 through OQ-11
(Phase 1 scope decisions) + OQ-α through OQ-ι (Step 2
implementation decisions) all auto-resolved per operator
recommendation. M13 is the publish counterpart
(release-runbook-driven, mirrors M11 with the M11 lessons
already folded into the runbook).

**docs-cli 1.4.0 shipped 2026-05-27.** **M11 — PyPI publish
1.4.0** is complete: `docs-cli==1.4.0` is live at
https://pypi.org/project/docs-cli/1.4.0/, the publish-only
counterpart to M10 (mirroring M9's relationship to M8). The
`v1.4.0` tag points at the M11 Phase 4 commit; the GitHub
release lives at
https://github.com/ArtRichards/docs-cli/releases/tag/v1.4.0.
Chain-of-custody verified **bit-perfect** — the PyPI-served
wheel sha256 (`7af7eb5c…`) is byte-identical to the local
Phase 4 build. The headline M10 contract
(`docs migrate --apply --quiet` produces empty stdout + empty
stderr; `.docs.toml` auto-emitted with `[project]` +
`[archive]`) was re-verified against the PyPI-served wheel
during Phase 4 smoke against a synthetic foreign tree. The
TestPyPI rehearsal again ran under the disambiguated dist
name `docs-cli-rehearsal==1.4.0` (the bare `docs-cli` on
TestPyPI is still parked by the M9-era squatter at 0.1.0; the
detour rolls forward to v1.5+). See
[m11-pypi-publish.md](archive/2026-05-27/m11-pypi-publish.md)'s
milestone-completion summary for the full publish record +
deviations; the
[release-runbook.md](release-runbook.md) stays the operative
reference for future releases.

**M10 — Adoption-flow polish + 1.3.0 carry-overs** is
**Complete (2026-05-27)** — shipped to PyPI as 1.4.0 via M11
on 2026-05-27. The milestone bundled the two user-surfaced
agent-driveability features (`docs touch <file...>` with
multi-file atomic semantics, `docs migrate --apply` writes
`.docs.toml` automatically + opportunistic empty-archive-
parent rmdir) with the carry-overs from M3 (`[vocabulary]
add_fields` allowlist + `unknown-field` check rule), M7
(`Confidence` enum replacing the `bool | str` tri-value), and
M8 (`--apply --quiet` per-file output suppression,
`MigrationPlan.excluded_count` removal, adoption-playbook
restructured to 4 steps). 400/400 pytest GREEN at M10 close
(401/401 across M11 phases — Phase 1 added the `~/.pypirc`
+ ownership inventory). Phase 9 kebab-tiny dogfood (in
`/tmp/m10-dogfood` against the 1.4.0 wheel in
`/tmp/docs-m10-venv`) confirmed `--apply --quiet` produces
empty stdout + empty stderr, the auto-emitted `.docs.toml`
carries OQ-A's `[project]` + OQ-M's `[archive] date_format`
under the provenance header, and `docs check` exits 0
immediately. See
[m10-adoption-polish-impl.md](archive/2026-05-27/m10-adoption-polish-impl.md)
for the per-phase log; the milestone doc was archived at
Phase 10 closeout per the M8/M9 pattern (impl log stays
Lifecycle: active).

**docs-cli 1.3.0 shipped 2026-05-25.** **M9 — PyPI publish
1.3.0** is complete: `docs-cli==1.3.0` is live at
https://pypi.org/project/docs-cli/1.3.0/, batching the M6 + M7
+ M8 surface into one public release. (The release closes the
M6 → M9 backlog grouping internally tracked as "v1.1".) The GitHub repo
`ArtRichards/docs-cli` is public; source tag `v1.3.0` +
GitHub release exist. See
[m9-pypi-publish.md](archive/2026-05-25/m9-pypi-publish.md)'s
milestone-completion summary for the published version, wheel
+ sdist sha256, publish timestamp, and the deviations from the
runbook recorded for v1.4+ releases. The release-runbook stays
the operative reference for future publishes.

**Next action:** **prepare M28 — Move-safe Markdown body-link rewrites.**
M27's milestone setup completed 2026-08-14 on
`m27/milestone-setup` with **all seven setup questions resolved**;
**Step 1 (Phases 1–4) is complete on `m27/phases-1-4`**, and **Step 2
(Phases 5–10) is complete on `m27/phases-5-10`** — all ten phases
(2026-08-14). Phase 1 froze the
contract: the supported Markdown grammar subset and its exactness rules, the length-preserving code-masking
contract and its ordering, destination classification and document-relative
resolution, **the containment test** (join → lexical canonicalisation →
under-root membership, with the `..`-escape-then-return and symlink cases
decided) and **its precedence over the existence test** so
`broken-body-link` and `outside-root-body-link` never double-report, both
findings' exact message templates with the JSON record's key set left closed,
and the `BodyLink` destination-span contract M28 consumes are frozen in
`cli.md` › *Markdown body-link validation* (including the explicitly stated
out-of-root boundary), `convention.md` › *Body links* (the inside-the-root
invariant, fence-your-code-samples, and the third archived-document
exception), and the
[M27 plan](m27-markdown-body-link-validation.md)'s *Decisions (Phase 1 —
BINDING)*. Zero `cli.py` edits, 895 passed unchanged, `docs check --root docs`
exit 0. Phase 2 wrote the RED suite against those frozen strings — a new
105-item pure-scanner module plus the rule-level, subprocess, touch and
bundled-skill locks, **+163 test ids with zero removed and zero collection
errors** (1058 collected, 129 failed, 929 passed). Phase 3 authored the six
`bodylink-*` fixture trees — 17 files, each tree yielding exactly its intended
finding set, **no** pre-existing fixture edited, collection +6 for the
parametrizations they add (1064 collected, 122 failed, 942 passed as the seven
predicted degenerate locks flipped GREEN). Phase 4 captured the classified RED
baseline: **1079 collected, 137 failed, 942 passed** (restated after the
Step-1 same-instance audit and the fresh-eyes review fold-in), zero collection
errors, zero tracebacks, zero xfails, exactly two exception classes (119
`AttributeError` through the `_m27()` indirection, 18 `AssertionError`), and
**all 895** pre-existing ids mechanically proven still present and still
passing — `comm -23` and
`comm -12 failed old` both **zero**, because M27 removes and modifies no
pre-existing test. The audit found and fixed six issues, none needing an
operator decision: a stale `plan.md`, an E5 lock narrower than the coverage
the milestone claims, an ordering lock that pinned only half of the
findings' placement, a specified-but-unlocked nested-vs-root `INDEX.md` split,
an under-constrained mask assertion, and `BodyLink`'s immutability being
frozen in the signature but untested. An independent **fresh-eyes review**
then found **no blockers** and reproduced the whole baseline, returning nine
should-fix items and four nits — all conductor-resolved and folded in. Their
unifying theme was that a wrong-but-plausible Phase-5 implementation could
still pass the suite: the BINDING percent/backslash/`#` decode order had no
test at all (the natural `unquote()`-then-`split()` implementation violates
it and went GREEN), the ordering lock never mixed the two rules, the
angle-destination newline bound and the unclosed-fence case were unpinned,
and the never-stat spy's containment test was a prefix comparison that would
have admitted the very probe it forbids. The specs also gained three settled
reference-definition points, an explicit whitespace-both-sides rule, the
unclosed-fence rule with its deliberate divergence from the single-line
inline-span bound, and a corrected worked instance; and a Phase-6 trap is now
recorded — the D6 repair bumps 30 `Updated:` lines, so
`tests/fixtures/expected/docs-INDEX.md` must be regenerated inside Phase 6's
own commit. **Phase 5 (2026-08-14)** landed the whole pure scanner in one new
banner section of `src/docs_cli/cli.py` — `BodyLink`, the length-preserving
`_mask_code`, `scan_body_links`, `classify_destination`, the
resolution/containment helpers and `body_link_findings` — while wiring **no**
rule, so the 18 rule/CLI/skill tests stay honestly RED at the `check_doc`
seam: **18 failed, 1061 passed**, all 119 pure-scanner tests GREEN, every
remaining failure an `AssertionError` and none an `AttributeError`, and no
test file edited. The real scanner reproduces every published census number
exactly — 393 recognised spans, 139 broken and 1 escape across 30 documents in
`docs/`, and 0 broken / 0 escapes across all 33 pre-M27 fixture trees and the
bundled skill — which is the point of measuring twice. Seven grammar points
the frozen contract left silent (an empty inline destination is a recognised
link with a zero-width span; newlines are ordinary whitespace either side of
an inline destination; the blank-line bound covers the whole candidate; the
closing-fence and verbatim-fence-line rules; a reference definition's label
opens and closes on one line and its destination ends at an unescaped `)` at
depth 0; a `(…)` title does not nest; and `Path.exists()` is kept so a
dangling in-root symlink is `broken-body-link`) were settled in `cli.md` and
its byte-identical mirror rather than only in the log, because every one of
them changes what the scanner hands M28. **Phase 6 (2026-08-14)**
wired both rules into `check_doc` in three lines — after the `broken-ref`
group and before `stale`, with `check_tree`, `exit_code_for`,
`finding_to_json`, `_print_check_findings`, `_run_touch_check`,
`_iter_doc_texts` and the argparse all untouched — and, in the **same
commit**, performed the D6 live-tree repair: **140 occurrences across 30
documents**, split **132** root rebases / **5** move-map lookups / **2**
playbook URLs / **1** escape URL, driven by the Phase-5 scanner itself and
spliced by offset right-to-left, which is literally the M28 operation and the
first live proof the span contract works. All 30 got an `Updated:` bump and
the 29 archived ones a single uniform dated `Revision:` bullet;
`convention.md`'s promised repair date is now the real one. Six independent
checks prove no other byte moved — 30/30 round-trip reconstructions
byte-identical, 166 changed lines with every non-`equal` opcode inside a
recorded destination span, `+3`/`+0` net line arithmetic, every metadata
invariant held, a re-census at **0 broken / 0 escapes with the
recognised-span count still 393**, and both gates green. The `docs/INDEX.md`
churn (29 archived entries relocated to the top of the archived group plus
`charter.md`'s date, 30 changed lines) is the mechanical consequence of the
operator-confirmed `Updated:` bump and was regenerated with its frozen
snapshot inside the same commit. Suite: **2 failed, 1077 passed**, the only
REDs left being Phase 7's two surface locks. **Phase 7 (2026-08-14)**
reconciled every parallel surface — `docs check`'s argparse description, the
bundled `SKILL.md` check row and `references/use-cases.md` (the *Validate in
CI* row plus a new M27 upgrade section), and `CHANGELOG.md` under
`UNRELEASED` with one `Added` entry per rule, a BREAKING `Changed` entry, and
the adopter recipe for **both** repairs. No spec edit was needed, so both
mirrors stayed byte-identical and the INDEX snapshot needed no regeneration;
no version bump. The suite is now **fully GREEN at 1079 passed**, one phase
early. **Phase 8 (2026-08-14)** ran the formal gate: **1079 collected, 1079
passed, 0 failed**, zero xfail/xpass, zero tracebacks, every quality gate
clean, and the `comm` proof against **both** anchors — **0** ids removed
since the pre-M27 `d61da1d` and since the Step-1 head `ddf0a45`, **0 added by
Step 2**, and 895 + 184 = 1079. `git diff ddf0a45 -- tests/*.py` is empty:
no test was relaxed, weakened, deleted or rewritten to reach GREEN, and none
needed to be. **Phase 9 (2026-08-14)** replayed the pre-repair damage on
throwaway copies (140 findings, 139 + 1, exit 2, 30 documents) and walked the
**documented** recipe from `docs check --json` alone — never the scanner API
— reaching exit 0 with the same 132/5/3 split and **0 destination-token
mismatches** against the repaired tree. Hermeticity was proven end to end on
the pre-repair copy, the only one where the escaping link still exists:
identical stdout and exit code from a location with a resolving sibling `src/`
and from a bare one, with **0 probes outside the root** under a `Path.exists`
/ `Path.is_file` spy. All 39 fixture trees and the bundled skill sweep clean
bar M27's three deliberately damaged ones. Runtime: 183 ms over the 2.5 MB
live tree and 61 ms for the 303 KB adversarial set — **33× under the 2.0 s
lock**. The real tree was never written to. **Phase 10 (2026-08-14)** ran
the `/simplify` pass — four changes applied, six candidates considered and
rejected with the reason recorded — closed `architecture.md` › `check` and
`test-strategy.md` › *What we don't test* (which still claimed the body was
opaque), extended README's one-line `docs check` summary, and folded in the
Phase-9 quality item: the live-tree scan went from 183 ms to **81 ms**, with
`docs check` at **0.16 s** end to end. **M27 is implementation-complete** —
all ten phases, every deliverable met, and the `BodyLink` span contract
handed to M28. The **Step-2 same-instance audit** then found **twelve** issues and fixed all twelve — **three of them real behavioural defects in the scanner**, every one invisible to the finding set and to the suite, reachable only by reading the frozen contract as a specification. The critical one is a **hermeticity hole**: a percent- or backslash-encoded leading slash (`%2Fetc/passwd`) classifies `local` because classification runs on the token as written, decodes to `/etc/passwd`, wins the `posixpath.join`, and — because Phase-1 point 9 dropped the containment predicate's leading-`/` leg — read as *contained*, so `docs check` **stat'd a path outside its own root**, the single thing D4b exists to forbid. The leg is restored; point 9's stated intent survives (a literally-written `/path` is still silenced by classification) while its unsound mechanism does not, and **point 9 is amended in place — a BINDING Phase-1 decision, flagged for the operator**. The other two defects: a link nested inside an image label was silently dropped, which the Phase-1 linearity note had foreseen and which would have left M28 unable to rewrite that destination; rule 5's *at least one whitespace character* before a title was not enforced; and two docstrings asserted things that were false. All three scanner fixes are **behaviour-neutral on every real input** — the live-tree census (393/0/0), the pre-repair replay (139 + 1 across 30 documents) and the 39-tree fixture sweep are all unchanged — and the three reachable defects are now **locked**, taking the suite to **1082 passed / 0 failed**. The remaining findings were spec and documentation corrections: an `architecture.md` line-count and module-annotation drift, a Success criterion that called all 139 archived repairs "rebases" when only 132 are, a `convention.md` promise of *29 named archived documents* that no surface actually named, a `Progress:` line and an "in flight" claim that contradicted "all ten phases complete", a CHANGELOG example mixing a real filename with a synthetic destination, a self-contradictory fence-line clause, and runtime figures that had drifted. Three items are surfaced for the operator rather than auto-decided. Each phase is recorded in the
[M27 log](m27-markdown-body-link-validation-impl.md). M26 is
implementation-complete on `m26/phases-5-10` (2026-08-13) across all ten TDD
phases. Step 1 froze the contract — the compatibility matrix, the message
catalog, the exit-code split, the `--json` schema, and the Phase-5 signatures
in the [M26 plan](m26-safe-archive-selection.md)'s *Decisions (Phase 1 —
BINDING)* section and in `cli.md` / `convention.md` — wrote the RED suite over
four new `archive-*` fixture trees, and captured the classified baseline
(**884 collected, 104 failed, 780 passed**), passing a same-instance audit and
an independent fresh-eyes review whose blocker was an unsatisfiable
byte-identity assertion that collided with M18. Step 2 landed the
implementation: Phase 5 the `ArchiveMove` / `ArchivePlan` models, the two
pure helpers and the `--json` serializer; Phase 6 candidate discovery,
planning, the validate-all-first pre-flight, ordered execution and the
residual partial-state admission; Phase 7 the nine-step check order in
`_cmd_archive`, the retirement of bare `--cascade` and `--interactive`
(both still registered, refusing before any filesystem access), the deletion
of the three 1.x cascade helpers — and with them the verb's last stdin read —
and every parallel surface: `--help`, `cli.md`, the bundled skill, and the
`UNRELEASED` CHANGELOG; Phase 8 the GREEN gate (**888 passed**; 889 after the Step-2 audit's failure-path lock and 895 after the fresh-eyes review fold-in) with **774 of
777** pre-existing ids mechanically proven present and passing, 3 deliberately
removed and 114 new at that gate (121 after the audit and review fold-ins);
Phase 9 the dogfood, where the unfiltered preview of the
M25 pair reproduced **E1** exactly — all six spine documents named and none
authorized — and four refusals each changed zero bytes on a fresh copy;
Phase 10 the simplify-and-close pass. Two frozen signatures were amended
under conductor decision and are recorded in the milestone doc
(`CoordinatedWriteError.exit_code`, `_print_archive_lines(cascade=…)`), and
one defective Step-1 test helper — a `mkdir` missing `parents=True` that no
implementation could satisfy — was fixed in its own labelled commit with no
assertion changed. The same-instance audit then caught an unreadable plan
member producing a traceback, and the independent fresh-eyes review caught the
step's one **blocker**: a primary that resolves outside the docs root — through
a symlink, or a `--root` naming a different tree — was archived **into** the
tree, at exit 0 in one shape with `docs check` clean afterwards. It now refuses
at exit 1 before any write, in the cross-verb wording `touch` / `stamp` /
`project set` / `relate` already use. **The package version deliberately stays
1.8.0.** The Step-3 `/simplify` pass is **done** (2026-08-13, `m26/simplify`)
and made **no code changes**: Step 2's Phase-10 pass had already taken the one
real win (the `_is_archived_rel` dedup), and every remaining candidate —
the pre-flight's five per-check loops, the four read-failure handlers, the
`CoordinatedWriteError`-before-`OSError` clause order, the two-check
`os.access` pre-flight, and `_archive_one`'s verbatim body — was re-examined
against the post-review code and found load-bearing. 895 GREEN and the gate
clean before and after, with `src/` and `tests/` byte-identical; the rejected
candidates and their reasons are recorded in the log.
Each phase is recorded in the
[M26 log](m26-safe-archive-selection-impl.md), which carries the milestone
completion summary. M25 is
complete and **merged to `main`** (2026-08-12, merge `822e086`) across all ten
TDD phases (**777 GREEN**, gate clean, dogfood done, fresh-eyes review folded
in) and stays `Lifecycle: active` until
M29 publishes the train. The Step-3 `/simplify` pass is **done**
(2026-08-12, `m25/simplify`): three duplicated bare-label scans collapsed
onto one `_bare_label_run`, `_plan_relate_edit`'s doubled `RelateEdit`
construction merged, `_print_relate_lines`' per-iteration word choices
hoisted, and `_duplicate_labels`' split cursor advance unified — **-17
lines**, 777 GREEN before and after, no shipped string or contract moved.
The package version deliberately remains **1.8.0**;
M25's CHANGELOG entries sit under `## UNRELEASED` for M29 to name and date.
M27–M29 stay draft until their turn.
The [release-runbook.md](release-runbook.md) remains the operative M29
publication path. The PyPI token re-scope and workflow-skill drift-lint items
remain non-blocking follow-ons below.

**Open follow-ons (rolled forward):**
- **Token re-scope** to project-`docs-cli` — async operator UI work, not a
  release blocker; rolls forward from M9 → M11 → M13 → M17 → M20.
- **Workflow-skill / bundled-skill drift lint (NEW, v1.7+ candidate).** The M20
  host-skill sweep (the NEW publish-closeout step) caught a stale
  `docs new --body-from` "first 20 lines" reference in the
  `project-foundation` workflow skill — the pre-M19-D3 heuristic, fixed at the
  M20 closeout. The drift was only catchable at publish time. Candidate: an
  in-repo lint that diffs the workflow skills' docs-cli prescriptions against
  the bundled `references/` surface so this class of drift surfaces before a
  publish, not at it. Logged for v1.7+; not a release blocker. The lint is a
  repo-side CI artifact and stays a separate follow-on.
- **Runtime skill-refresh nudge now lives in M23 (NEW, 2026-06-29).** The
  *runtime* skill-refresh idea — when the user updates the CLI, also nudge them
  to refresh the installed skill — was originally M21's D5 (an offline
  skill-drift *notice* that inspected the host's installed skill). That premise
  (content-inspecting the user's skill; assuming Claude Code) was rejected this
  session; **D5 is CUT from M21**. The honest version — make `install-skill`
  agent-aware via `--dest`, **record** the resolved dest, then extend M21's
  notice channel with a skill-refresh hint pointed at the *recorded* dest — is
  the follow-on **M23** ([m23-agent-aware-install-skill.md](archive/2026-07-03/m23-agent-aware-install-skill.md)).
  Not a loose follow-on any more; it is a scoped (draft) milestone.

**Shipped (cleared follow-ons):**
- **Stale `docs new --body-from` help string → FIXED in M19 (D3), shipped to
  PyPI as `docs-cli==1.6.5` via M20 on 2026-06-12.** The argparse `--help` text
  shipped in 1.6.0 still described the pre-M15-C4 "first 20 lines" heuristic;
  M19 D3 replaced it with the real-detector wording (leading `---` fence or ≥2
  adjacent `{Lifecycle, Role, Updated}` lines), pinned by
  `test_new_body_from_help_no_first_20_lines` and re-verified against the
  PyPI-served 1.6.5 wheel at the M20 Phase-4 smoke. Closed.
- **Single-step "update metadata + validate" loop + configurable stale window →
  IMPLEMENTED in M19 (v1.6.5), shipped to PyPI via M20 on 2026-06-12.** (a) The
  three-command post-edit workflow collapses to one step via `docs touch
  --check [--stale N]` (D1). (b) The fixed `--stale 14` window becomes a
  `.docs.toml [check] stale_days = N` per-tree default (D2 — arms bare `docs
  check`, CLI `--stale` overrides, provenance-named messages); does not affect
  `docs list --stale` (Q6). Both verified against the PyPI-served 1.6.5 wheel at
  the M20 Phase-4 smoke. Closed.

- **M14 — Robustness + autonomous archive (v1.6.0)** — **Complete**;
  shipped to PyPI as `docs-cli==1.6.0` via M17 on 2026-06-03. `docs mv`
  atomicity, `docs new` strict-root refusal, the four-verb
  `touch`/`archive`/`mv`/`project rename` exclude-predicate fix,
  slug/`OSError`/`atomic_write`-fsync guards, non-interactive
  `archive --cascade`, bundled-ref + packaging fixes. Pair archived to
  `archive/2026-06-03/`.
- **M15 — Agent-native doc authoring (v1.6.0)** — **Complete**; shipped
  to PyPI as `docs-cli==1.6.0` via M17 on 2026-06-03. `docs project set`,
  single-file `docs stamp` (write-then-stamp), the `--body-from`
  real-frontmatter detector, and the skill/cli docs. Carved out of M14 on
  2026-06-02 (it outgrew M12 scale); **depended on M14**. Pair archived to
  `archive/2026-06-03/`.
- **M17 — PyPI publish 1.6.0** — **Complete (2026-06-03)**: the
  operator-driven publish that shipped M14 + M15 together (batched, as M9
  shipped M6+M7+M8). Ran the [release-runbook.md](release-runbook.md)
  end-to-end as a fully-autonomous pass; chain-of-custody bit-perfect;
  `v1.6.0` annotated tag at `95f23a6` + GitHub release. Milestone doc
  archived to `archive/2026-06-03/`; the
  [m17-pypi-publish-impl.md](m17-pypi-publish-impl.md) impl log stays
  `Lifecycle: active`.

The broader agent-native surface (global `--json`,
`docs context`/`capabilities`, hooks, MCP) is deferred — see
the M14 Decisions.

[release-runbook.md](release-runbook.md) remains the operative
publish reference, with M13's cumulative lessons folded in
(TestPyPI rehearsal prints `0.0.0+local` under the rename
detour because the M12 `importlib.metadata` SoT can't resolve
the renamed distribution — verify the version string against
the canonical-name local + PyPI wheels; and `CHANGELOG.md` is
not shipped inside the sdist).

### M6 — preparation complete (2026-05-24)

M6 was merged to `main` 2026-05-24 as commit `ff7f9d5` and
closed at Phase 10 as **preparation only** — packaging machinery
(build backend, package shape, `install-skill` verb, runbook
scaffold, GitHub repo) delivered; no PyPI upload was ever in
M6's scope after the 2026-05-24 reframe. The wheel + sdist in
local `dist/` from 2026-05-23 are not uploaded; M9 will rebuild
fresh from the post-M8 tree at publish time. See
[m6-pypi-distribution.md](archive/2026-05-24/m6-pypi-distribution.md)'s top
"Scope reframe" callout and the
[release-runbook.md](release-runbook.md) for the operative
checklist.

### M9 — PyPI publish 1.3.0 (Complete 2026-05-25)

[m9-pypi-publish.md](archive/2026-05-25/m9-pypi-publish.md) walked top-to-bottom
in one contiguous session 2026-05-25. Quality gate green
(pytest 369), artefacts rebuilt fresh from the post-M8 tree,
TestPyPI rehearsal ran under a disambiguated dist name
`docs-cli-rehearsal==1.3.0` (the bare `docs-cli` was parked
on TestPyPI by an unrelated user — real PyPI was clean), real
PyPI upload + smoke install confirmed bit-perfect
chain-of-custody, repo flipped public, `v1.3.0` tag pushed +
GitHub release created, doc closeouts in lockstep. Token
re-scope deferred as out-of-band operator UI work. Full
record (and deviations recorded for v1.4+) in M9's
milestone-completion summary.

### M7 + M8 — stubs drafted from the 2026-05-24 trial

The multi-tree trial against 25 real-world foreign trees (501 .md
files) surfaced 11 categorical findings. They cluster into two
milestones:

- **M7 — Migration plan accuracy** (Complete 2026-05-25):
  renamed the controlled-vocab field `Status:` → `Lifecycle:`
  (breaking, no backward compat), broadened role inference
  (suffix matching, H1 + section signals, sibling defaulting),
  normalised project names to lowercase-kebab, normalised
  `archived/` subdirs into `archive/YYYY-MM-DD/`, expanded the
  role vocab with 7 core additions (`implementation`, `sketch`,
  `outline`, `memo`, `brief`, `template`, `example`). One new
  CLI flag: `docs migrate --config-project NAME` (plus
  `--lifecycle` rename on `docs list`). Trial-2 dogfood: 88%
  high+medium against the sanitised real-tree fixtures. Plan
  at [m7-migration-accuracy.md](archive/2026-05-25/m7-migration-accuracy.md).
- **M8 — Adoption workflow** (after M7): `--exclude` tree-wide
  (in `migrate` + `index` + `check` + `list` via `.docs.toml`'s
  new `[exclude]` section), triage flags
  (`--summary`, `--only ambiguous`), `docs new --body-from <-|path>`
  (closes Read-before-Write friction), and a substantial rewrite
  of the bundled skill's references for the adoption flow
  (SKILL.md stays slim — one pointer line). Stub at
  [m8-adoption-workflow.md](archive/2026-05-25/m8-adoption-workflow.md). Load-bearing
  ship gate: **fresh-subagent dogfooding** of the adoption loop
  end-to-end against trees the M8 author hasn't tuned for.

### M6 milestone-setup history (kept for context)

**M6 — PyPI distribution as `docs-cli` is in flight (milestone-setup
phase complete, 2026-05-23).** The task plan
[m6-pypi-distribution.md](archive/2026-05-24/m6-pypi-distribution.md) is promoted from
`draft` to `active`; the log
[m6-pypi-distribution-log.md](archive/2026-05-24/m6-pypi-distribution-log.md) is created.
M6 is the first v1.1 milestone: it publishes the CLI as `docs-cli` on
PyPI, relocates `bin/docs` to an importable package at
`src/docs_cli/cli.py`, ships the Claude Code skill inside the wheel as
package data, and adds one new verb — `docs install-skill` — that
materialises the bundled skill onto a host. **All five milestone-setup
OPEN QUESTIONS are resolved 2026-05-23** (OQ1 command name stays
`docs`; OQ2 conftest aliases `docs_cli.cli` as `docs`; OQ3 repo
identity moves at Phase 1 with a new GitHub repo created since the
local repo has no remote yet — `ArtRichards/docs-cli` private until
v1.1 publishes; OQ4 skill source moves to `src/docs_cli/skill/`; OQ5
`bin/docs` is deleted). Phase 1's scope was expanded by the OQ3
override to carry the identity rename — new GitHub repo, local
checkout move `~/opt/docs` → `~/opt/docs-cli`, host-pointer updates —
in addition to the usual milestone-activation docs work. See the log
for the per-phase status table.

**Project v1 shipped 2026-05-22 — M1-M5 all complete.** M5 — Claude
Code skill closed the v1 roadmap on 2026-05-22 (post-ship polish on
2026-05-23; relocated under the package at M6 Phase 5). It is the
project's final v1 deliverable: a Claude Code skill — a `SKILL.md`
artifact at `src/docs_cli/skill/` (was `skills/docs/` at M5 ship) —
that makes an agent reach for the `docs` verbs automatically when
doing documentation work in a `docs`-managed tree. It adds no CLI
surface and changes no verb behaviour: it is a markdown artifact
whose `description` triggers on the right contexts (creating a
plan/spec/charter/milestone, archiving or renaming a doc, listing
docs, checking the tree, regenerating `INDEX.md`, adopting a foreign
Markdown directory) and whose body redirects to the appropriate `docs`
verb instead of hand-editing metadata, `INDEX.md`, or `archive/`. The
convention itself is not re-taught — the body links to the bundled
spec references at `src/docs_cli/skill/references/` (relocated from
`skills/docs/references/` at M6 Phase 5). The four M5 milestone-setup
OPEN QUESTIONS (OQ1-OQ4) were resolved and recorded as Decisions in
the task plan. **Post-ship polish (2026-05-23)** shortened `SKILL.md`
to a trigger surface (verb-task table + when-to-use scenarios +
never-hand-edit rule), bundled `convention.md` and `cli.md` as
references (byte-identical mirrors with a lockstep test), and
cleaned dev cross-refs out of the source specs. See
[m5-claude-code-skill-log.md](archive/2026-05-23/m5-claude-code-skill-log.md) for the
per-phase history (and the post-ship section appended to it) and
[m5-claude-code-skill.md](archive/2026-05-23/m5-claude-code-skill.md) for the milestone
summary.

M4 — Migration helper (`docs migrate`) shipped 2026-05-22 across ten TDD
phases. It added one verb — `docs migrate <dir>` — that adopts a
non-conforming directory into the convention: it walks a foreign tree, infers
the required metadata per file, and produces a migration plan (dry-run by
default; `--apply` writes the metadata blocks and normalises archive-style
subdirectories). See [m4-migration-helper-log.md](archive/2026-05-22/m4-migration-helper-log.md)
for the per-phase history and [m4-migration-helper.md](archive/2026-05-22/m4-migration-helper.md)
for the milestone summary.

M3 — Validation and query (`check`, `list`) shipped 2026-05-22 across ten TDD
phases. It added two read-only verbs — `docs check` (validate the tree, with
CI-usable exit codes) and `docs list` (filterable query view with a stable
JSON schema) — and regrouped `INDEX.md` by `Project` then `Role`. See
[m3-validation-and-query-log.md](archive/2026-05-22/m3-validation-and-query-log.md) for the
per-phase history and [m3-validation-and-query.md](archive/2026-05-22/m3-validation-and-query.md)
for the milestone summary.

M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) shipped 2026-05-21
across ten TDD phases. See [m2-mutating-verbs-log.md](archive/2026-05-21/m2-mutating-verbs-log.md)
for the per-phase history and [m2-mutating-verbs.md](archive/2026-05-21/m2-mutating-verbs.md)
for the milestone summary.

M1 — Parser and `docs index` shipped 2026-05-20 across ten TDD phases.
See [m1-parser-and-index-log.md](archive/2026-05-20/m1-parser-and-index-log.md) for the
per-phase history and [m1-parser-and-index.md](archive/2026-05-20/m1-parser-and-index.md)
for the milestone summary.

## Milestone progress

| Milestone | Status | Task plan | Log |
|---|---|---|---|
| M1 — Parser and `docs index` | **Complete** (2026-05-20) | [Plan](archive/2026-05-20/m1-parser-and-index.md) | [Log](archive/2026-05-20/m1-parser-and-index-log.md) |
| M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) | **Complete** (2026-05-21) | [Plan](archive/2026-05-21/m2-mutating-verbs.md) | [Log](archive/2026-05-21/m2-mutating-verbs-log.md) |
| M3 — Validation and query (`check`, `list`) | **Complete** (2026-05-22) | [Plan](archive/2026-05-22/m3-validation-and-query.md) | [Log](archive/2026-05-22/m3-validation-and-query-log.md) |
| M4 — Migration helper (`docs migrate`) | **Complete** (2026-05-22) | [Plan](archive/2026-05-22/m4-migration-helper.md) | [Log](archive/2026-05-22/m4-migration-helper-log.md) |
| M5 — Claude Code skill | **Complete** (2026-05-22) | [Plan](archive/2026-05-23/m5-claude-code-skill.md) | [Log](archive/2026-05-23/m5-claude-code-skill-log.md) |
| M6 — PyPI distribution preparation as `docs-cli` | **Complete** (2026-05-24, preparation only; publish moved to M9) | [Plan](archive/2026-05-24/m6-pypi-distribution.md) | [Log](archive/2026-05-24/m6-pypi-distribution-log.md) |
| M7 — Migration plan accuracy | **Complete** (2026-05-25; ship-ready locally, publish DEFERRED to M9 batched 1.3.0 per OQ-C) | [Plan](archive/2026-05-25/m7-migration-accuracy.md) | [Log](archive/2026-05-25/m7-migration-accuracy-log.md) |
| M8 — Adoption workflow (agent-driveable) | **Complete** (2026-05-25; ship-ready locally as 1.3.0, publish DEFERRED to M9 batched 1.3.0 per OQ-C) | [Plan](archive/2026-05-25/m8-adoption-workflow.md) | [Log](archive/2026-05-25/m8-adoption-workflow-log.md) |
| M9 — PyPI publish 1.3.0 | **Complete** (2026-05-25; `docs-cli==1.3.0` on PyPI; repo public; `v1.3.0` tag + GitHub release) | [Plan](archive/2026-05-25/m9-pypi-publish.md) | [Log](archive/2026-05-25/m9-pypi-publish-log.md) |
| M10 — Adoption-flow polish + 1.3.0 carry-overs (v1.4.0) | **Complete** (2026-05-27; shipped to PyPI via M11; 400/400 GREEN at M10 close; kebab-tiny dogfood PASS) | [Plan](archive/2026-05-27/m10-adoption-polish.md) | [Log](archive/2026-05-27/m10-adoption-polish-impl.md) |
| M11 — PyPI publish 1.4.0 | **Complete** (2026-05-27; `docs-cli==1.4.0` on PyPI; `v1.4.0` tag + GitHub release; chain-of-custody bit-perfect; headline M10 contract holds against PyPI-served wheel) | [Plan](archive/2026-05-27/m11-pypi-publish.md) | [Log](archive/2026-05-27/m11-pypi-publish-impl.md) |
| M12 — Project rename + M11 wart fixes + version SoT (v1.5.0) | **Complete** (2026-05-28; `dist/docs_cli-1.5.0-*` built locally, twine check PASS, 433/433 pytest GREEN at simplify close; shipped to PyPI as 1.5.0 via M13 on 2026-05-29) | [Plan](archive/2026-05-28/m12-project-rename.md) | [Log](archive/2026-05-28/m12-project-rename-impl.md) |
| M13 — PyPI publish 1.5.0 | **Complete** (2026-05-29; `docs-cli==1.5.0` on PyPI; `v1.5.0` annotated tag + GitHub release; chain-of-custody bit-perfect; all four M12 headline contracts hold against the PyPI-served wheel) | [Plan](archive/2026-05-29/m13-pypi-publish.md) | [Log](archive/2026-05-29/m13-pypi-publish-impl.md) |
| M14 — Robustness + autonomous archive (v1.6.0) | **Complete** (2026-06-02 impl-complete; **shipped to PyPI as `docs-cli==1.6.0` via M17 on 2026-06-03**, batched with M15; `mv` atomicity, `new` strict-root, four-verb `touch`/`archive`/`mv`/`project rename` excludes, slug/`OSError`/`atomic_write`-fsync guards, non-interactive `--cascade`, bundled-ref guard + packaging fix; the M14 pair was archived to `archive/2026-06-03/` at the M17 closeout) | [Plan](archive/2026-06-03/m14-robustness-agent-native.md) | [Log](archive/2026-06-03/m14-robustness-agent-native-impl.md) |
| M15 — Agent-native doc authoring (v1.6.0) | **Complete** (2026-06-03 impl-complete, Phases 1–10; **shipped to PyPI as `docs-cli==1.6.0` via M17 on 2026-06-03**, batched with M14 — `docs project set`, single-file `docs stamp`, `--body-from` real-frontmatter detector, skill/cli docs; 501 GREEN at M15 close, gate clean tree-wide; the M15 pair was archived to `archive/2026-06-03/` at the M17 closeout) | [Plan](archive/2026-06-03/m15-agent-native-authoring.md) | [Log](archive/2026-06-03/m15-agent-native-authoring-impl.md) |
| M16 — Bundled docs skill quality artifacts | **Complete / archived** (2026-06-01 impl-complete; documentation-only bundled `docs` skill guidance; code on `main` as `9ceb113`; the M16 trio was archived to `archive/2026-06-01/` by M18's Phase-9 sweep on 2026-06-03) | [Plan](archive/2026-06-01/m16-bundled-docs-skill-quality.md) | [Log](archive/2026-06-01/m16-bundled-docs-skill-quality-impl.md) |
| M17 — PyPI publish 1.6.0 | **Complete** (2026-06-03; `docs-cli==1.6.0` on PyPI, batching M14 + M15 as M9 batched M6+M7+M8; `v1.6.0` annotated tag at `95f23a6` + GitHub release; chain-of-custody bit-perfect; all seven M14 + M15 headline contracts hold against the PyPI-served wheel; milestone doc archived to `archive/2026-06-03/`, impl log stays `Lifecycle: active`) | [Plan](archive/2026-06-03/m17-pypi-publish.md) | [Log](m17-pypi-publish-impl.md) |
| M18 — Archive edge integrity (intra-archive Related: rewriting) | **Complete / archived** (2026-06-03 impl-complete; correctness fix to `docs archive` — the conditioned archived-skip in `_rewrite_referring_edges` rewrites the moved doc's own archive-subtree `Related:` edges + repoints already-archived referrers; flipped the pinned `test_archive_does_not_rewrite_archive_subtree_edges` → `test_archive_repoints_already_archived_referrer`. `docs mv` own-edge parity (Open Q1 INCLUDED) verified already satisfied — no code change. Phase-9 payoff archived the M1–M9/M12 pairs + M16 trio + 3 stray impl-logs; `docs check docs/` exit 0. 510 GREEN. The M18 pair was archived to `archive/2026-06-12/` at the M20 closeout — it rode along in the 1.6.0 tree as an already-merged fix and added no new public surface to 1.6.5) | [Plan](archive/2026-06-12/m18-archive-edge-integrity.md) | [Log](archive/2026-06-12/m18-archive-edge-integrity-impl.md) |
| M19 — Post-edit validation ergonomics (touch --check + configurable stale window) (v1.6.5) | **Complete** (2026-06-12; feature milestone — `docs touch --check [--stale N]` folds the existing `check_tree` into the touch loop after the end-of-batch reindex; `.docs.toml [check] stale_days = N` makes the stale window per-tree configurable (CLI `--stale` overrides); cosmetic `docs new --body-from` help-string fix closes the rolled-forward follow-on. No new verb, no new check rule; additive + backward-compatible. **Shipped to PyPI as `docs-cli==1.6.5` via M20 on 2026-06-12.** Q1–Q6 + OQ-1..OQ-5 RESOLVED; threshold-provenance folded into D2. Full suite 540/540 GREEN (533 + the Step-2 review +7), gate clean tree-wide, `docs --version` → `docs 1.6.5`. The M19 pair was archived to `archive/2026-06-12/` at the M20 closeout) | [Plan](archive/2026-06-12/m19-post-edit-validation.md) | [Log](archive/2026-06-12/m19-post-edit-validation-impl.md) |
| M20 — PyPI publish 1.6.5 | **Complete** (2026-06-12; `docs-cli==1.6.5` on PyPI, the publish-only counterpart to M19 one-to-one as M13 shipped M12; `v1.6.5` annotated tag at the Phase-4 commit `0855466` + GitHub release; chain-of-custody **bit-perfect for both wheel AND sdist** (wheel `aba36e92…`, sdist `f9de1eb4…`); all M19 headline contracts hold against the PyPI-served wheel; ran the [release-runbook.md](release-runbook.md) on `main` (M17 precedent — no TDD code phases). NEW vs M17: the Phase-5 closeout refreshed the host-machine skills (`docs install-skill --force` + a workflow-skill sweep that caught + fixed one stale `--body-from` reference in `project-foundation`) per the CLAUDE.md skill-update-flow policy. Q1 → FULL AUTONOMOUS, Q2 → archive the M18 + M19 pairs + M20's own milestone doc to `archive/2026-06-12/`; the M20 impl log stays `Lifecycle: active`) | [Plan](archive/2026-06-12/m20-pypi-publish.md) | [Log](m20-pypi-publish-impl.md) |
| M21 — Update-check notification (PyPI new-version notice) (v1.7.0) | **Complete** (shipped to PyPI as `docs-cli==1.8.0` **batched via M24** 2026-07-03; pair archived to `archive/2026-07-03/`; impl-complete 2026-06-29, all 10 TDD phases; **1.7.0 skipped on PyPI**) (scaffolded 2026-06-12; **re-scoped to CLI-only 2026-06-29**; **all 10 TDD phases done 2026-06-29** — Phases 1–4 (RED baseline) on `m21/phases-1-4`, Phases 5–10 on `m21/phases-5-10`: full suite **604 GREEN**, gate clean tree-wide, `pyproject` at 1.7.0, `docs --version` → `docs 1.7.0`; the online path verified against live PyPI + dogfooded end-to-end, pytest 100% offline) — feature milestone introducing docs-cli's **first network surface**: a once-per-24h, fail-silent PyPI version check (stdlib `urllib` only, 1.0s timeout, 24h-cache-gated under a three-key `{last_check, latest_version, last_notified}` cache, zero-dependency wheel preserved) that emits ONE STDERR line nudging the user/agent to update **the CLI** (`pip install -U docs-cli`; wording `docs: update available <current> -> <latest> — run: pip install -U docs-cli`). STDERR-only, never alters the exit code, suppressed under `--quiet`/`--json`/`CI`/`DOCS_CLI_NO_UPDATE_CHECK`/`DO_NOT_TRACK` (the user-level config opt-out is DEFERRED out of v1.7.0 — OQ-5/5a), but **deliberately shows on non-TTY** (inverting gh's TTY rule — the agent is the actor). The former skill-drift notice (D5) + the dual-action `docs install-skill --force` half are **CUT** (re-scope 2026-06-29 — no skill inspection, no Claude-Code assumption); the skill story moves to follow-on **M23**. Ships as **1.7.0** (minor — additive; 1.6.5 was the operator-decreed patch exception); a later milestone publishes (M19→M20 pattern). **OPEN QUESTIONS netted out — none outstanding** (OQ-1..OQ-9 RESOLVED 2026-06-12; OQ-6 "ship D5" REVERSED by the re-scope). Shipped batched as 1.8.0 via M24; archived 2026-07-03. | [Plan](archive/2026-07-03/m21-update-check.md) | [Log](archive/2026-07-03/m21-update-check-impl.md) |
| M22 — Doc-tree root placement guidance (project ≠ directory) | **Complete** (impl-complete 2026-06-24; shipped to PyPI as `docs-cli==1.8.0` **batched via M24** 2026-07-03, pair archived; all ten TDD phases; documentation-only, M16-shaped — no CLI/code change, no version bump; convention.md §Subdirectories + bundled SKILL.md "where to put `.docs.toml`" guidance: `Project:` is metadata not a directory, and root-relative `Related:` makes a nested lone project prefix every sibling ref; RED-first `tests/test_skill_root_placement.py`; bundled reference mirrored byte-identical; dogfood-snapshot refreshed; CHANGELOG staged under 1.7.0 UNRELEASED. Full suite 543 GREEN, gate clean, Phase-9 dogfood reproduced the redundant-prefix consequence. Ran **before** M21 per the operator's run-order decision 2026-06-24 — number = creation order, not execution order. Shipped batched as 1.8.0 via M24; archived 2026-07-03 (the publish closeout swept it, M18/M19/M21 + M16 precedent). Companion `project-foundation` note tracked separately in `agent-playbook-suite`) | [Plan](archive/2026-07-03/m22-root-placement-guidance.md) | [Log](archive/2026-07-03/m22-root-placement-guidance-impl.md) |
| M23 — Agent-aware install-skill + recorded-dest skill-refresh hint (v1.8.0) | **Complete** (shipped to PyPI as `docs-cli==1.8.0` **batched via M24** 2026-07-03; pair archived to `archive/2026-07-03/`; impl-complete 2026-07-02, all 10 TDD phases) (Phases 1–4 (Contract & RED baseline) on `m23/phases-1-4`; Phases 5–10 (implementation → dogfood → closeout) on `m23/phases-5-10`: full suite **636 GREEN**, gate clean tree-wide, `pyproject` at 1.8.0, `docs --version` → `docs 1.8.0`; online path dogfooded against a seeded throwaway cache, pytest 100% offline) — follow-on to the M21 re-scope that restores the skill-refresh nudge cut from M21. Makes `docs install-skill` **agent-aware**: `--dest` is the agent-agnostic source of truth; TTY-aware resolution (human may be prompted; an agent [non-TTY] is **never** blocked → falls back to the default, OQ-1); the resolved dest is **recorded** (path only — **never** content) to a separate `${XDG_STATE_HOME:-~/.local/state}/docs-cli/install-skill.json` (OQ-2; M21's 3-key cache stays frozen); the "Claude Code skill" framing in `install-skill`'s help is neutralised to **"agent skill"** (reconciling with `cli.md`); and M21's update notice gains a skill-refresh hint pointed at the **recorded** dest (riding M21's same suppression matrix + throttle). Replay/remember allowed; content-inspection + agent-guessing NOT. Out of scope: multi-agent skill *formats* + agent auto-detection. **Depends on M21.** Ships **1.8.0** (OQ-4). **The four OPEN QUESTIONS are resolved** (OQ-1 default / OQ-2 separate XDG_STATE file — **confirmed as-shipped at the M24 gate, D4**; OQ-3 last-write-wins single dest; OQ-4 1.8.0). Shipped batched as 1.8.0 via M24; archived 2026-07-03. | [Plan](archive/2026-07-03/m23-agent-aware-install-skill.md) | [Log](archive/2026-07-03/m23-agent-aware-install-skill-impl.md) |
| M24 — PyPI publish 1.8.0 | **Complete** (2026-07-03; `docs-cli==1.8.0` live on PyPI; `v1.8.0` tag at `1a01f74` + GitHub release; chain-of-custody bit-perfect wheel `29ac3ced…` + sdist `62a29285…`; all M21+M23 contracts hold against the served wheel; host skills refreshed) — operator-driven publish shipping the post-1.6.5 train **batched** as `docs-cli==1.8.0`: M21 (update-check, built 1.7.0) + M22 (doc-only, no bump) + M23 (agent-aware install-skill, 1.8.0), mirroring M17 (M14+M15→1.6.0) / M9 (M6+M7+M8→1.3.0). Tree at 1.8.0 (M23 Phase 7, merged `839daef`); **1.7.0 skipped on PyPI** (its CHANGELOG entries fold into 1.8.0, D2). Runbook-driven — no TDD code phases; the [release-runbook.md](release-runbook.md) sections are the phases. Setup decisions: D1 batched 1.8.0; D2 CHANGELOG fold; D3 "author now, confirm at the gate" (runbook starts on explicit go-ahead, pauses before every irreversible step); D4 M23 OQ-1/OQ-2 confirmed as-shipped (flag cleared); D5 closeout archived the M21+M22+M23 pairs + the M24 milestone doc to `archive/2026-07-03/` (impl log stays active). Ran the release-runbook end-to-end under D3 (operator go at the Phase-4 gate). | [Plan](archive/2026-07-03/m24-pypi-publish.md) | [Log](m24-pypi-publish-impl.md) |
| M25 — Reciprocal relationship integrity and `docs relate` | **Active / implementation-complete — all ten TDD phases** (Phases 1–4 2026-08-11 on `m25/phases-1-4`; Phases 5–10 2026-08-12 on `m25/phases-5-10`; **777 GREEN**, gate clean, dogfood done, fresh-eyes review folded in incl. the operator-approved post-freeze `duplicate-field` rule; Step-3 `/simplify` done 2026-08-12 on `m25/simplify` (-17 lines, 777 GREEN unchanged, no contract moved); stays `Lifecycle: active` until the M29 publish closeout) — hard inverse validation + explicit active/archived repair; first v2.0 implementation milestone. Six recognized verbs, the `missing-inverse` rule, and `docs relate add|remove` (idempotent, `--dry-run`/`--json`, one reindex, staged publish + rollback, audited archived repair) are implemented; the version deliberately stays 1.8.0 (D6) with CHANGELOG entries under `UNRELEASED` for M29 to name. | [Plan](m25-reciprocal-relationship-integrity.md) | [Log](m25-reciprocal-relationship-integrity-impl.md) |
| M26 — Safe explicit archive selection | **Active / implementation-complete — all ten TDD phases (2026-08-13); Step-3 `/simplify` done 2026-08-13 on `m26/simplify` — no code changes, 895 GREEN unchanged, every remaining candidate re-examined and found load-bearing** (Step 1 Phases 1–4 on `m26/phases-1-4` 2026-08-12 / 2026-08-13, classified RED baseline 884 collected / 104 failed / 780 passed with 769 of 777 pre-existing ids still GREEN, Step-1 audit and fresh-eyes review folded; Step 2 Phases 5–10 on `m26/phases-5-10` 2026-08-13 — **895 GREEN** (888 at the Phase-8 gate, 889 after the audit's lock, 895 after the fresh-eyes review fold-in), 774 of the 777 pre-existing ids mechanically proven present and passing, 3 deliberately removed, 121 new; the closeout workflow dogfooded on a throwaway copy of this tree, where the unfiltered preview reproduces E1 exactly; `pyproject.toml` untouched at 1.8.0) — bare `--cascade` and the retired `--interactive` refuse before any write (registered-and-refusing, exit 2, migration guidance), `--cascade-dry-run` previews every one-hop candidate as selected / not-selected / ineligible, a related-document write requires an explicit `--cascade-only GLOB` whose full plan is validated first (deduplicated, canonical-path matched, collision- and writability-checked, archived neighbours excluded, archived primary refused, empty selection refused), and `docs archive --json` emits one operation-plan record whose shape is identical for preview and apply. Registered 2026-08-10, planned in depth 2026-08-12 on `m26/milestone-setup`; setup reproduced five v1.8.0 defects **E1–E5**, each mapped to named regression coverage — bare `--cascade` on the M25 pair proposing to archive `plan.md` + `cli.md` + `convention.md` + `test-strategy.md` + `status.md`; a duplicate edge printing a false failure; a basename collision leaving a partial archive at exit 0 with `docs check` clean; an archive-subtree edge silently relocating and re-dating an archived doc; a typo'd scope looking like success. **All seven setup questions RESOLVED** (Q1/Q5/Q6 operator; Q2/Q3/Q4/Q7 conductor-resolved); extending M25 — D5's staged-publish-plus-rollback to N docs was considered and declined. Two frozen signatures were amended under conductor decision and recorded in the milestone doc (`CoordinatedWriteError.exit_code`, `_print_archive_lines(cascade=…)`), and one defective Step-1 test helper that no implementation could satisfy was fixed in its own labelled commit with no assertion changed. The same-instance audit and an independent fresh-eyes review then folded in eight more fixes, the review's **blocker** among them: a primary resolving outside the docs root — through a symlink, or a `--root` naming a different tree — was being archived INTO the tree (exit 0 in one shape, `docs check` clean afterwards); it now refuses at exit 1 before any write, in the cross-verb wording the other explicit-path verbs use. No version bump (M25 — D6); stays `Lifecycle: active` until the M29 publish closeout. | [Plan](m26-safe-archive-selection.md) | [Log](m26-safe-archive-selection-impl.md) |
| M27 — Markdown body-link validation | **Implementation-complete — all ten phases done** (2026-08-14, `m27/phases-1-4` + `m27/phases-5-10`; stays `Lifecycle: active` until the M29 closeout) — a pure stdlib-only scanner over a deliberately bounded, named Markdown subset (inline links with plain/angle destinations and optional titles, plus reference definitions; images, autolinks, raw HTML and reference uses excluded), length-preserving fenced- and inline-code masking, destinations resolved **relative to the referring document** with fragments preserved and never validated, and **two** hard errors: `broken-body-link` (a missing in-root destination) and `outside-root-body-link` (a destination that leaves the tree), both `severity: error`, exit 2, one finding per occurrence, JSON key set left **closed** with the location carried in `message`. The check **never stats outside its own root** — an escape is decided by path arithmetic, and containment is tested **before** existence so the two rules never double-report. The `BodyLink` record's exact destination-token span is the handoff to M28 — no second parser. Registered 2026-08-10, planned in depth 2026-08-14 on `m27/milestone-setup`; setup measured the tree read-only and produced eight pieces of evidence **E1–E8** — **139 unresolved local destinations across 29 documents, 100% of them under `archive/`** (132 a pure `../../` rebase, 5 a moved target, 2 a bundled-skill file that never lived in the docs tree); `docs check` exits **0** today with all 139 broken; `test_check_dogfood_repo_docs_is_clean` makes the legacy policy a hard gate inside the suite; code masking prevents 7 measured false positives (including `architecture.md:182`'s `[<path>](<path>)`) while a 4-space indented-code rule would mask 9 spans that are all real links; a containment census over `docs/`, all 33 fixture trees and the bundled skill finds **exactly one** escape (`charter.md:52`) and none in any fixture; and nothing in the repository exercises the exotic grammar, so Phase 3 must author it. **All seven setup questions RESOLVED** — Q1/Q2/Q5 operator, Q3/Q4/Q6/Q7 conductor. **Q1: repair, rule stays uniform** — the breakage class is produced by `docs archive` itself and `docs/` ships in every PyPI sdist and is public on GitHub, so exempting archived docs would leave the tool silent about the damage it causes; the one-time destination-token-only repair is `Updated:` + `Revision:` audited and lands in Phase 6, and `convention.md` gains a third archived-document exception with a stated blast radius. **Q5 was resolved against the setup recommendation and then amended**: the hermetic boundary is kept (a check must be a function of the tree alone) but the escape is **reported** rather than skipped — `outside-root-body-link` is an operator-approved post-draft scope addition following M25's `duplicate-field` precedent, and `charter.md:52` is converted to the canonical GitHub URL in Phase 6, the same treatment Q1 gives the two `adoption-playbook` links and doubly right since the relative alternative would itself have violated Q5. **Phase 1 (2026-08-14)** froze the grammar and its exactness rules, the masking contract and its ordering, destination classification, the containment test and its precedence over existence, **both** message templates, and the `BodyLink` span record — in `cli.md`, `convention.md` and the milestone's *Decisions (Phase 1 — BINDING)* — with **zero** `cli.py` edits, 895 passed unchanged and `docs check --root docs` at exit 0; three setup-frozen items were amended under conductor decision and recorded as amendments (`broken-body-link`'s message contradicted Q7's directory rule, `outside-root-body-link` had no message at all, and the 33-tree no-new-findings lock becomes a new sibling test rather than an extension that would cover only 23 trees and fail on the damaged `bodylink-*` fixtures), and a third bundled-skill authoring trap was found by tripping it (`test_installed_skill_references_do_not_depend_on_source_checkout` forbids the literal `../src/docs_cli/`, which is exactly E7's real escaping destination). **Phase 2 (2026-08-14)** wrote the RED suite — **+163 test ids, zero removed, zero collection errors** (1058 collected, 129 failed, 929 passed) — across a new 105-item pure-scanner module and the rule, subprocess, `touch --check` and bundled-skill locks; it closed one Phase-1 gap in the specs (a reference definition has no enclosing `)`, so its plain destination ends at whitespace or end of line) and caught a whole falsely-GREEN family before it existed, since `load_config` tolerates a missing directory and every "silent tree" lock would otherwise have passed on a fixture that was never written. **Phase 3 (2026-08-14)** authored six `bodylink-*` fixture trees (17 files, one semantic each, static dates, **no** pre-existing fixture edited): every supported form resolving, one unresolved link, every excluded form silent, nested up-and-down resolution including `../sub/../back-inside.md`, the un-rebased archive shape, and two escapes chosen so one cannot exist while the other provably does — the pair that makes E7's "whether or not it would have resolved" testable. **Phase 4 (2026-08-14)** captured the classified RED baseline — **1079 collected, 137 failed, 942 passed** after the Step-1 same-instance audit's six fixes and the fresh-eyes review's thirteen further locks — zero collection errors, zero tracebacks, zero xfails, exactly two exception classes, every RED in a named family and every one of the 47 GREEN-at-baseline locks classified degenerate / genuine / transitional — with **all 895** pre-existing ids mechanically proven present and passing (`comm -23` = 0 and `comm -12 failed old` = 0; M27 removes and modifies no pre-existing test, which is what Phase-1 amendment 3 bought). No product code was touched across Phases 1–4. The audit's six fixes were a stale `plan.md`, an E5 lock narrower than the coverage the milestone claims, an ordering lock pinning only half the findings' placement, a specified-but-unlocked nested-vs-root `INDEX.md` split, an under-constrained mask assertion, and `BodyLink`'s untested immutability; two items were surfaced for the reviewer and both came back settled (the repair-clause asymmetry between the two messages is intentional and stays; specs describing Phase-6 behaviour ahead of the code is accepted per M26). The independent **fresh-eyes review** found **no blockers**, reproduced the whole baseline, and returned nine should-fix items and four nits, all conductor-resolved and folded in — the headline being that the BINDING percent/backslash/`#` decode order had no test at all, so the natural `unquote()`-then-`split()` implementation violated the frozen contract and passed. **Phase 5 (2026-08-14)** landed the whole pure scanner in one new banner section of `src/docs_cli/cli.py` — `BodyLink`, the length-preserving `_mask_code`, `scan_body_links`, `classify_destination`, the resolution/containment helpers and `body_link_findings` — while wiring **no** rule, so the 18 rule/CLI/skill tests stay honestly RED at the `check_doc` seam (**18 failed, 1061 passed**; all 119 pure-scanner tests GREEN; every remaining failure an `AssertionError` and none an `AttributeError`; no test file edited). The real scanner reproduces every published census number exactly — 393 recognised spans, 139 broken and 1 escape across 30 documents in `docs/`, and 0/0 across all 33 pre-M27 fixture trees and the bundled skill. Seven grammar points the frozen contract left silent were settled in `cli.md` and its byte-identical mirror rather than only in the log, because each changes what the scanner hands M28: an empty inline destination is a recognised link with a zero-width span; newlines are ordinary whitespace either side of an inline destination; the blank-line bound covers the whole candidate rather than only the label; the closing fence needs the same character, equal-or-greater length and nothing but whitespace after the marker, and the whole fence line survives verbatim; a reference definition's label opens and closes on one line and its destination ends at an unescaped `)` at depth 0; a `(…)` title does not nest; and `Path.exists()` is kept, so a dangling symlink inside the root is `broken-body-link`. **Phase 6 (2026-08-14)** wired both rules into `check_doc` in three lines — after the `broken-ref` group and before `stale`, with `check_tree`, `exit_code_for`, `finding_to_json`, `_print_check_findings`, `_run_touch_check`, `_iter_doc_texts` and the argparse all untouched — and, in the **same commit**, performed the D6 live-tree repair: **140 occurrences across 30 documents**, split **132** root rebases / **5** move-map lookups / **2** playbook URLs / **1** escape URL, driven by the Phase-5 scanner itself and spliced by offset right-to-left (literally the M28 operation, and the first live proof the span contract works). All 30 got an `Updated:` bump and the 29 archived ones a single uniform dated `Revision:` bullet; `convention.md`'s promised repair date is now the real 2026-08-14. Six independent checks prove no other byte moved — 30/30 round-trip reconstructions byte-identical, 166 changed lines with every non-`equal` opcode inside a recorded destination span, `+3`/`+0` net line arithmetic, every metadata invariant held, a re-census at **0 broken / 0 escapes with the recognised-span count still 393**, `docs check --root docs` at exit 0 with both rules live, and the INDEX snapshot identical after its 30-line mechanical churn was regenerated in the same commit. Suite: **2 failed, 1077 passed**, the only REDs left being Phase 7's two surface locks. **Phase 7 (2026-08-14)** reconciled every parallel surface — `docs check`'s argparse description, the bundled `SKILL.md` check row and `references/use-cases.md` (the *Validate in CI* row plus a new M27 upgrade section), and `CHANGELOG.md` under `UNRELEASED` with one `Added` entry per rule, a BREAKING `Changed` entry, and the adopter recipe for **both** repairs; no spec edit was needed, so both mirrors stayed byte-identical and the INDEX snapshot needed no regeneration. The suite went **fully GREEN at 1079 passed**, one phase early (**1082** after the Step-2 audit's three locks). **Phase 8 (2026-08-14)** ran the formal gate — **1079 collected, 1079 passed, 0 failed**, zero xfail/xpass, zero tracebacks, all quality gates clean — plus the `comm` no-regression proof against **both** anchors: 0 ids removed since the pre-M27 `d61da1d` and since the Step-1 head `ddf0a45`, **0 added by Step 2**, 895 + 184 = 1079, and `git diff ddf0a45 -- tests/*.py` empty, so no test was relaxed, weakened, deleted or rewritten to reach GREEN. Deliverables 2–5 ticked. **Phase 9 (2026-08-14)** replayed the pre-repair damage on throwaway copies (140 findings, 139 + 1, exit 2, 30 documents) and walked the documented recipe from `docs check --json` alone — never the scanner API — reaching exit 0 with the same 132/5/3 split and **0 destination-token mismatches** against the repaired tree; hermeticity proven end to end on the pre-repair copy with identical stdout and exit code from a with-sibling and a bare location and **0 probes outside the root** under a spy; all 39 fixture trees and the bundled skill sweep clean bar M27's three damaged ones; runtime 183 ms over the 2.5 MB live tree and 61 ms for the 303 KB adversarial set, **33× under the 2.0 s lock**. **Phase 10 (2026-08-14)** ran the `/simplify` pass — four changes applied, six candidates considered and rejected with the reason recorded — closed `architecture.md` › `check` (the pure pipeline, the per-document-not-cross-document contrast with `reciprocity_findings`, the length-preserving mask as the reason offsets stay valid, and the span record as M28's input) and `test-strategy.md` › *What we don't test* (which still claimed the body was opaque), extended README's one-line `docs check` summary, and folded in the Phase-9 quality item: the live-tree scan went from 183 ms to **81 ms**, with `docs check` at **0.16 s** end to end. **M27 is implementation-complete**: all ten phases, every deliverable met, and the `BodyLink` span contract handed to M28. The **Step-2 same-instance audit** then found **twelve** issues and fixed all twelve — **three of them real behavioural defects in the scanner**, every one invisible to the finding set and to the suite, reachable only by reading the frozen contract as a specification. The critical one is a **hermeticity hole**: a percent- or backslash-encoded leading slash (`%2Fetc/passwd`) classifies `local` because classification runs on the token as written, decodes to `/etc/passwd`, wins the `posixpath.join`, and — because Phase-1 point 9 dropped the containment predicate's leading-`/` leg — read as *contained*, so `docs check` **stat'd a path outside its own root**, the single thing D4b exists to forbid. The leg is restored; point 9's stated intent survives (a literally-written `/path` is still silenced by classification) while its unsound mechanism does not, and **point 9 is amended in place — a BINDING Phase-1 decision, flagged for the operator**. The other two defects: a link nested inside an image label was silently dropped, which the Phase-1 linearity note had foreseen and which would have left M28 unable to rewrite that destination; rule 5's *at least one whitespace character* before a title was not enforced; and two docstrings asserted things that were false. All three scanner fixes are **behaviour-neutral on every real input** — the live-tree census (393/0/0), the pre-repair replay (139 + 1 across 30 documents) and the 39-tree fixture sweep are all unchanged — and the three reachable defects are now **locked**, taking the suite to **1082 passed / 0 failed**. The remaining findings were spec and documentation corrections: an `architecture.md` line-count and module-annotation drift, a Success criterion that called all 139 archived repairs "rebases" when only 132 are, a `convention.md` promise of *29 named archived documents* that no surface actually named, a `Progress:` line and an "in flight" claim that contradicted "all ten phases complete", a CHANGELOG example mixing a real filename with a synthetic destination, a self-contradictory fence-line clause, and runtime figures that had drifted. Three items are surfaced for the operator rather than auto-decided. No version bump (M25 — D6). | [Plan](m27-markdown-body-link-validation.md) | [Log](m27-markdown-body-link-validation-impl.md) |
| M28 — Move-safe Markdown body-link rewrites | **Registered draft** (2026-08-10; no log/phase started; depends on M26 + M27) — incoming-target and moved-referrer link rebasing. | [Plan](m28-move-safe-body-link-rewrites.md) | _not yet created_ |
| M29 — PyPI publish 2.0.0 | **Registered release stub** (2026-08-10; depends on M25–M28; no log/runbook phase started). | [Plan](m29-pypi-publish-2-0-0.md) | _not yet created_ |

v1 (M1-M5) shipped 2026-05-22. **docs-cli 1.3.0 shipped
2026-05-25** as the first public PyPI release — M6 (PyPI
distribution preparation), M7 (migration accuracy — breaking
`Status:` → `Lifecycle:` rename + inference broadening), M8
(adoption workflow — `--exclude` tree-wide, triage flags,
`docs new --body-from`, skill-reference rewrite for adoption)
all complete locally over 2026-05-24 to 2026-05-25; M9 (the
operator-driven publish) shipped them together as one batched
PyPI release on 2026-05-25, closing the M6 → M9 backlog
grouping internally tracked as "v1.1". The CLI is now installable via `pip install
docs-cli` on any Python 3.11+ host.

## TDD phase order (used per milestone)

1. Define Contract
2. Write Tests (RED)
3. Create Data/Fixtures
4. Run Tests (RED Baseline)
5. Update Base Interfaces
6. Implement Offline/Core Path
7. Update Tool/Wrapper Layer
8. Run Tests (GREEN)
9. Implement Online/Integration (mapped to dogfooding pass when no network surface)
10. Quality, Docs, Refactor

## Quick links

- [Charter](charter.md) — what + why
- [Convention spec](convention.md) — on-disk format
- [CLI spec](cli.md) — command surface
- [Architecture](architecture.md) — module sketch + dev setup commands
- [Plan](plan.md) — milestone roadmap (v1 + v1.1)
- [Definition of Ready](definition-of-ready.md) — gate to start

## Resuming this work (fresh session)

If you're starting a new Claude Code session against this repo:

**Reading order** (≤ 10 minutes):
1. `~/CLAUDE.md` — host-level guidance + memory pointers
2. `docs/status.md` — this file
3. `docs/plan.md` — the roadmap; v1 (M1-M5) shipped, v1.1 in
   flight (M6 merged + publish-pending; M7+M8 stub-drafted).
4. `docs/m6-pypi-distribution.md` — M6 task plan; "Decisions"
   records the five milestone-setup OQs resolved 2026-05-23.
5. `docs/m6-pypi-distribution-log.md` — M6 log with the per-phase
   status table.
6. `docs/m7-migration-accuracy.md` — M7 stub: the breaking
   `Status:` → `Lifecycle:` rename and inference broadening
   (findings F0–F12 from the 2026-05-24 trial).
7. `docs/m8-adoption-workflow.md` — M8 stub: the agent + operator
   ergonomics (tree-wide `--exclude`, triage flags,
   `docs new --body-from`, skill-reference rewrite).
7a. `docs/m9-pypi-publish.md` + `docs/release-runbook.md` — M9
   shipped 2026-05-25 as `docs-cli==1.3.0`; the milestone-
   completion summary in `m9-pypi-publish.md` is the canonical
   record of what shipped + deviations; the runbook is the
   operative reference for future releases.
8. `docs/cli.md` — the command spec; the full eight-verb `docs`
   surface.
9. `docs/convention.md`, `docs/architecture.md` — the on-disk
   format and the module sketch.
10. `docs/m5-claude-code-skill.md` — v1's final milestone; its
    **Milestone-completion summary** describes the skill that
    M6's `install-skill` verb delivers via the wheel.
11. `src/docs_cli/skill/SKILL.md` — the bundled skill (relocated
    under the package source at M6 Phase 5).
12. `docs/charter.md` — what + why.
13. `docs/definition-of-ready.md` — the gate cleared before
    implementation.

**Verify environment** before doing any work:
```sh
cd ~/opt/docs-cli
.venv/bin/python -m pytest tests/ -q          # 433 passed (current suite, as of 1.5.0 / M13)
.venv/bin/ruff check .                        # All checks passed!
.venv/bin/ruff format --check .               # all files formatted
.venv/bin/mypy                                # Success (tree-wide)
.venv/bin/docs check docs/                    # dogfood — exit 0
.venv/bin/docs index --root docs/ --dry-run   # smoke: idempotent dogfood
```
If `.venv/` is missing (fresh clone) or `.venv/bin/docs` is absent:
```sh
rm -rf .venv && python3 -m venv .venv         # needs python3-venv on Debian/Ubuntu
.venv/bin/pip install -e ".[dev]"             # lands `docs` on PATH via the entry point
```

**Next action:** none scoped — **M12 shipped to PyPI as
`docs-cli==1.5.0` via M13 on 2026-05-29** (M12 built the four
features locally; M13 published them, mirroring M11 → M10).
Both milestones are Complete. The next implementation
milestone (M14) is unscoped; pick it up via
`create-milestones` / `/ship-milestone next milestone`. The
authoritative current state lives in the "Current milestone"
and top "Next action" sections above; this resume-snapshot
block is historical.

**docs-cli 1.4.0 shipped 2026-05-27** as M11 — the
operator-driven publish milestone for the M10-built artefacts,
mirroring M9's relationship to M8. PyPI:
https://pypi.org/project/docs-cli/1.4.0/; source:
https://github.com/ArtRichards/docs-cli/releases/tag/v1.4.0;
`v1.4.0` annotated tag at the M11 Phase 4 commit. M11 ran the
[release-runbook.md](release-runbook.md) end-to-end:
operator-state inventory → fresh artefact build → TestPyPI
rehearsal under `docs-cli-rehearsal==1.4.0` (squatter detour
continues) → real PyPI upload → chain-of-custody verified
bit-perfect → smoke + M10 headline contract against the
PyPI-served wheel → tag + GitHub release → doc closeouts.
Full publish record + deviations in
[m11-pypi-publish.md](archive/2026-05-27/m11-pypi-publish.md)'s
milestone-completion summary.

**docs-cli 1.3.0 shipped 2026-05-25** — one batched PyPI
publish covering the M6 + M7 + M8 surface per the operator's
OQ-C split, closing the M6 → M9 backlog grouping internally
tracked as "v1.1". PyPI:
https://pypi.org/project/docs-cli/1.3.0/; source:
https://github.com/ArtRichards/docs-cli/releases/tag/v1.3.0;
GitHub repo public; `v1.3.0` lightweight tag at the M8 simplify
commit. Intermediate versions `1.1.0` and `1.2.0` never reached
PyPI (no prior public release existed; no continuity to
preserve). Full publish record + deviations recorded for
future releases in
[m9-pypi-publish.md](archive/2026-05-25/m9-pypi-publish.md)'s milestone-completion
summary. The [release-runbook.md](release-runbook.md) stays
the operative reference for the next release (v1.5+).

**M7 Phases 1-4 complete (2026-05-24; review-tightening 2026-05-25):**
task plan promoted to active, OQ A–D recorded as Decisions, log +
per-phase entries written, 44 new test items authored at Phase 2
(34 RED + 10 GREEN-at-baseline regression locks), sanitised
fixtures staged at
`tests/fixtures/{lifecycle,status-prose,project-names,sibling-defaulting}/`
+ `tests/fixtures/trees/real-trees/{kebab-tiny,snake-medium,snake-large,archive-subdir,mixed-naming}/`,
RED baseline captured at `/tmp/m7-phase-4-baseline.txt`
(34 failed, 281 passed; M6's 271 GREEN preserved + 10 new
regression locks). **Fresh-eyes review 2026-05-25** added 5
contract anchors (strict-medium pinning + parametric expansion
of status-prose preservation + `FileMigration(confidence="medium")`
constructor + `docs check` exit-1 medium anchor) for a post-fix
count of **39 RED + 281 passed (320 collected)**; M6's 271 still
GREEN. Quality gate clean tree-wide.

**M7 Phase 5 complete (2026-05-25):** the F0 controlled-vocab
rename landed across parser, dataclasses, writers, validators,
JSON serialisers, the `.docs.toml` reader, and argparse.
`Doc.lifecycle`, `FileMigration.lifecycle`, `Config.lifecycles`,
`validate_lifecycle`, `add_lifecycles` (TOML), `Lifecycle:` in
the on-disk block. `FileMigration.confidence` extended to
`high|medium|low`. `MigrationPlan` grows the
`project_original` + `multi_project_hints` fields with safe
defaults (populated at Phase 6). `Config` grows
`role_suffixes` + `project_name`. argparse:
`docs list --lifecycle` and `docs migrate --config-project NAME`.
29 docs/*.md files swept, 31 conformant fixture files swept,
existing-test fabrications updated. Skill refs resynced.
pytest: **290 passed, 30 failed (320 collected)** — every
failure on the Phase-6 surface (inference broadening,
project normalisation, per-file mtime archive, multi-project
hints, medium-confidence check wiring, snake-medium fixture
high+medium ratio). Quality gate clean.

**M7 Phase 6 complete (2026-05-25):** F1 / F10 / F11 / F12 /
F4 / F5 all landed. `infer_role` now does word-boundary +
case-transition splitting, recognises the 7 new core vocab
roles + `_M\d+` milestone pattern + `_v\d+`/`_Draft`/`_Ready`
strip with medium confidence. `normalise_project_name()`
produces lowercase-kebab and `plan_migration` honours CLI
> sidecar > inferred precedence with the `(normalised from
"X")` annotation. Per-file mtime drives archive moves when
`--date` is absent. Multi-project hints surface in the plan
footer. `check_doc` emits `medium-confidence-inference`
warnings (exit 1) when a missing `Role:` is resolvable via
H1 or section pattern. `.docs.toml` refusal narrowed so a
`[migrate]`-only sidecar is readable. **pytest: 320 / 320
GREEN.** Quality gate clean.

**M7 Phase 7 complete (2026-05-25):** convention.md, cli.md,
architecture.md, status.md, README.md, CHANGELOG.md all
updated to document M7's surface. New CHANGELOG entry
`## 1.2.0 — UNRELEASED` lists every breaking + additive
change (F0 rename, --lifecycle flag, JSON schema field
rename, add_lifecycles, 7 new core roles, medium
confidence, F11 normalisation, F4 per-file mtime, F5 hints,
--config-project, [migrate] sidecar). architecture.md gets
a new `config` module section. pyproject.toml +
`__version__` bumped to 1.2.0; `docs --version` prints
`docs 1.2.0`. Bundled skill refs resynced via byte-copy
(test_skill_refs.py GREEN). docs/INDEX.md regenerated;
fixture snapshot byte-equal. pytest: 320 / 320 GREEN.
Quality gate clean tree-wide.

**M7 Phase 8 complete (2026-05-25):** verbatim quality gate
captured at `/tmp/m7-phase-8-green.txt`. pytest 320 / 320
GREEN; ruff / format / mypy / docs check / docs index
--dry-run all clean; `docs --version` prints `docs 1.2.0`.

**M7 Phase 9 complete (2026-05-25):** all 5 quantitative
success criteria PASS. high+medium = 88.0% (103/117) ≥ 50%;
notes = 13.7% (16/117) ≤ 30%; free-form Status: preservation
= 4/4 = 100%; archive-subdir archive_move = 5/5 = 100% ≥ 80%;
project normalisation = 3/3 = 100% ≥ 90%.
`tests/manual/m7_success_criteria.py` aggregates; per-fixture
JSON dumps at `/tmp/m7-phase-9/*.json`.

**M7 Phase 10 complete (2026-05-25)**: milestone-completion
summary appended to `m7-migration-accuracy.md`; M7 row in
this file flipped to Complete; CHANGELOG `## 1.2.0 —
UNRELEASED` dated; local dist artefacts produced via
`python -m build` and verified with `twine check` (NO upload,
NO tag, NO GitHub release). M7 is ship-ready locally; the
public PyPI release ships as v1.3.0 batched with M6 + M8 at
the M9 milestone per the operator OQ-C split.

**M8 shipped locally as 1.3.0** (2026-05-25). All 10 TDD
phases complete; Phase 9 fresh-subagent gate **PASSED 3/3
unattended** on real fresh Opus subagents (operator-directed
re-run after the implementation agent's same-instance dogfood
substitution; both stages documented in the Phase 9 log).
Surface delivered: F3
(tree-wide `--exclude` + `[exclude]` + `.docsignore`), F6
(triage flags + default footer summary), F7 (non-md sibling
surfacing), F8 (substantial skill rewrite + adoption playbook
+ `.docs.toml` template), F9 (`docs new --body-from`). Tests:
**369 GREEN** (324 M7 + 45 new M8 items). Quality gate clean.
Local artefacts: `dist/docs_cli-1.3.0-py3-none-any.whl` +
`dist/docs_cli-1.3.0.tar.gz`; `twine check` PASSED on both.
**NO publish, NO tag, NO GitHub release** — per OQ-C the
publish is M9's scope.

**M8 Phases 1-4 complete (2026-05-25):** task plan promoted to
active and OQ A–G recorded as Decisions at milestone-setup; log +
per-phase Phase 1-4 entries written; 31 new test functions / 45
new collected items authored at Phase 2 across 5 new test files
+ 1 added test in `test_migrate.py`; new sanitised fixtures
staged at `tests/fixtures/body-from/` (3 files; the
`.docsignore` syntax cases and `[exclude]`-bearing trees are
written inline via `tmp_path` in the Phase 2 tests
themselves);
RED baseline captured at `/tmp/m8-phase-4-baseline.txt`
(**41 failed, 328 passed; 369 collected total** — M7's 324
GREEN preserved + 4 new baseline-GREEN regression locks + 41 RED
for intended reasons; the initial 40+5 baseline tightened to
41+4 in the fresh-eyes audit pass, which converted two weak
locks into proper REDs). Quality gate clean tree-wide.

**Watch out for** (durable gotchas, still current):
- The CLI module lives at `src/docs_cli/cli.py`. After Phase 6's
  editable install (`pip install -e ".[dev]"`), the `docs` command
  lands on PATH via the `[project.scripts]` entry-point — same binary
  the PyPI user gets. (Pre-Phase-6, invoke as
  `.venv/bin/python -m docs_cli.cli …`.)
- Quality gates run **tree-wide**: `ruff check .`, `ruff format --check .`, and `mypy` (no args — `pyproject.toml` scopes it to `src/` + `tests/`). Commit once per TDD phase on the active branch.
- The dogfood snapshot (`tests/fixtures/expected/docs-INDEX.md`) is spec-compliant, not hand-authored. If you change a `docs/*.md` body so its first paragraph or `Updated:` line changes, regenerate `docs/INDEX.md` and the snapshot in lockstep (`docs index --root docs`, then copy `docs/INDEX.md` onto the fixture). Editing a doc means bumping that doc's own `Updated:` per the convention.
- `docs mv` rewrites `Related:` metadata bullets only — prose markdown links in bodies are deliberately left alone (see the M2 Phase 9 log). `docs check` likewise validates `Related:` paths, not prose links.
- `docs check`'s `malformed` rule covers a **missing H1 only** — `parse_metadata_block` ends the metadata block at the first non-label line rather than raising, so a malformed in-block line is not separately detectable (M3 Phase 5 decision).
- INDEX markers quoted in a doc's preamble must be backtick-styled inline code, so the line-anchored detector (`_find_marker_lines`) does not false-match them.
- The metadata block may contain one blank line between the inline `Label: value` run and a trailing bare-label group (`Related:` + bullets). `_metadata_line_span` in `src/docs_cli/cli.py` is the single source of that block-boundary rule.
- Git author email for this repo is `art@bitholdersinc.com` (locally configured), not the `art@trucktech.in` default from `~/CLAUDE.md`.
- M7 (v1.2.0) renames the controlled-vocab field from `Status:` to `Lifecycle:` on disk — breaking, no backward-compat alias. References to `Status:` inside M1-M5 historical log narrative are deliberately preserved verbatim (the field-name swap is the only on-disk change). Bundled skill references at `src/docs_cli/skill/references/` must be resynced from `docs/{convention,cli}.md` in lockstep — `tests/test_skill_refs.py` enforces byte-equality.
