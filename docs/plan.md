# docs — Implementation Plan

Lifecycle: active
Role: plan
Project: docs
Updated: 2026-08-11

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
scanner to keep `mv`/archive operations link-safe. M29 publishes the four
implementation milestones together as **docs-cli 2.0.0**. The major version is
intentional: new hard check failures and refusal of unsafe bare `--cascade`
change existing automation. M25 is **in implementation** — Phases 1–4
(contract + RED baseline) are complete (2026-08-11); M26–M29 are registered
draft stubs. Execution order is expressed by reciprocal
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
v2.0:  M25 (reciprocal integrity + relate)  →  M26 (safe archive selection)  →  M27 (body-link validation)  →  M28 (move-safe rewrites)  →  M29 (PyPI publish 2.0.0)
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
| M25 — Reciprocal relationship integrity and `docs relate` | **Active / Phases 1–4 complete** (2026-08-11 on `m25/phases-1-4`; Phase 5 next) — recognized reciprocal sequence/dependency/blocker pairs, hard `missing-inverse` check errors, explicit two-endpoint add/remove repair, and narrowly audited archived-endpoint mutation. First implementation milestone in the v2.0 train. Phase 1 froze the contract in `cli.md` / `convention.md` and RESOLVED all five open questions (**Q5: the package stays 1.8.0 through M25–M28; M29 does the single bump to 2.0.0**); Phases 2–4 added 92 test items over nine committed `reciprocal-*` fixture trees and captured the classified RED baseline (**728 collected, 77 failed, 651 passed**, zero collection errors, the 636 pre-existing tests all still GREEN). | [Plan](m25-reciprocal-relationship-integrity.md) | [Log](m25-reciprocal-relationship-integrity-impl.md) |
| M26 — Safe explicit archive selection | **Registered draft** (2026-08-10; no log/phase started) — bare cascade refuses, preview stays read-only, and every related-document write requires explicit `--cascade-only` scope with deduplicated preflight. Follows M25. | [Plan](m26-safe-archive-selection.md) | _not yet created_ |
| M27 — Markdown body-link validation | **Registered draft** (2026-08-10; no log/phase started) — bounded local Markdown scanner, hard missing-destination check rule, and controlled legacy-tree repair policy. Follows M26; required by M28. | [Plan](m27-markdown-body-link-validation.md) | _not yet created_ |
| M28 — Move-safe Markdown body-link rewrites | **Registered draft** (2026-08-10; no log/phase started) — reuse M27's scanner and M26's move planning to rebase incoming links and links inside moved referrers for `mv`/archive. Depends on M26 + M27. | [Plan](m28-move-safe-body-link-rewrites.md) | _not yet created_ |
| M29 — PyPI publish 2.0.0 | **Registered release stub** (2026-08-10; no log/runbook phase started) — publish M25–M28 as one breaking safety train, verify upgrade paths against served artifacts, refresh host skills, and archive the train at closeout. Depends on M25–M28. | [Plan](m29-pypi-publish-2-0-0.md) | _not yet created_ |

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
`references/cli.md` kept byte-identical to `docs/cli.md`). It is part of
Phase 10 (Quality/Docs) done: run `docs <verb> --help` for each new/changed
verb and reconcile against the milestone's CHANGELOG surface, confirm the
bundled skill documents the new verbs/flags, and grep for stale wording
describing any *replaced* behavior. (Motivating miss: the
`docs new --body-from` help shipped in 1.6.0 still describing the
pre-M15-C4 "first 20 lines" heuristic.)

## Resolved questions

- **`docs archive --cascade` stays opt-in** (M2, 2026-05-21). Archiving a doc must not silently pull its neighbours along — cascading is a deliberate per-invocation choice. `--cascade` is a plain `store_true` flag; it prompts (`y/N`, defaulting to no) before archiving each one-hop `pairs-with` / `child-of` relation. No `--no-cascade` is needed.
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
