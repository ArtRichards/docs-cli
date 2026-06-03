# docs — Status

Lifecycle: active
Role: status
Project: docs
Updated: 2026-06-03

Related:
- pairs-with: plan.md
- pairs-with: m6-pypi-distribution.md
- pairs-with: m7-migration-accuracy.md
- pairs-with: m8-adoption-workflow.md
- pairs-with: m9-pypi-publish.md
- pairs-with: archive/2026-05-27/m10-adoption-polish.md
- pairs-with: archive/2026-05-27/m11-pypi-publish.md
- pairs-with: m12-project-rename.md
- pairs-with: archive/2026-05-29/m13-pypi-publish.md
- pairs-with: release-runbook.md
- pairs-with: m14-robustness-agent-native.md
- pairs-with: m15-agent-native-authoring.md
- pairs-with: m16-bundled-docs-skill-quality.md
- pairs-with: m18-archive-edge-integrity.md

**This is the single source of truth for project progress. Update only this file when milestones complete or phases advance.**

## Current milestone

**M16 — Bundled docs skill quality artifacts** is
**implementation-complete (2026-06-01)** for the Agent Playbook
Suite risk-aware quality upgrade, pending operator commit/archive.
Scope is limited to the bundled `docs` skill under `src/docs_cli/skill/`:
document test matrices, quality logs, generated report artifacts, and
the mechanical limits of `docs check`. The milestone pair is
[m16-bundled-docs-skill-quality.md](m16-bundled-docs-skill-quality.md)
+ [m16-bundled-docs-skill-quality-impl.md](m16-bundled-docs-skill-quality-impl.md).

**Completed-milestone doc archival is DEFERRED pending M18.** The
completed milestones M1–M9 + M12 (plan/log pairs), the M16 trio (plan +
impl + test-matrix), and the three stray impl-logs
(`m10-adoption-polish-impl.md`, `m11-pypi-publish-impl.md`,
`m13-pypi-publish-impl.md`) remain in the LIVE `docs/` tree rather than
under `archive/<date>/`. This is intentional: archiving interrelated docs
into the archive subtree today orphans their `Related:` edges (a milestone
plan↔log pair, or sweeping a log in beside its already-archived plan), which
makes `docs check docs/` exit 2 — the
[M18 — Archive edge integrity](m18-archive-edge-integrity.md) bug. Performing
that archival is M18's Phase 9 integrate/dogfood payoff; M14/M15 stay live
until the M17 publish regardless. Until M18 lands, the live tree keeps the
completed-milestone docs in place so `docs check docs/` stays clean.

The **v1.6 implementation train**: **M14 — Robustness + autonomous
archive** is now **implementation-complete (2026-06-02)** —
`docs-cli==1.6.0` built locally (pyproject bump + CHANGELOG section), 458
tests GREEN, quality gate clean tree-wide, pending operator
commit/archive; the **PyPI publish is M17's** (mirrors the M12→M13
local-build-then-publish-later cadence). **M15 — Agent-native doc
authoring** (**depends on M14**) is now **implementation-complete** —
Phases 1–4 (contract + RED baseline: 41 intended reds, 459 GREEN) on
`m15/phases-1-4`; Phases 5–10 (implementation + dogfood + closeout: all
41 RED → GREEN, 501 total, gate clean tree-wide) on `m15/phases-5-10`,
both 2026-06-03. It builds 1.6.0 locally; the publish is M17's. Then
**M17** publishes M14 + M15 together as `docs-cli==1.6.0`.
M14 was re-scoped 2026-06-02 and M15 carved out of it (it had outgrown
M12 scale) — see the *Next action* block below for per-milestone scope.

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
[m13-pypi-publish-impl.md](m13-pypi-publish-impl.md); the
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
[m10-adoption-polish-impl.md](m10-adoption-polish-impl.md)
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
[m9-pypi-publish.md](m9-pypi-publish.md)'s
milestone-completion summary for the published version, wheel
+ sdist sha256, publish timestamp, and the deviations from the
runbook recorded for v1.4+ releases. The release-runbook stays
the operative reference for future publishes.

**Next action:** the v1.6 train is two implementation
milestones then a publish.

- **M14 — Robustness + autonomous archive (v1.6.0)** —
  **implementation-complete (2026-06-02)** on branch
  `m14/phases-5-10`, pending operator commit/archive: `docs mv`
  atomicity, `docs new` strict-root refusal, `docs touch`/`archive`/`mv`/
  `project rename` exclude-predicate fix, slug/`OSError`/`atomic_write`
  fsync guards, non-interactive `archive --cascade`, bundled-ref +
  packaging fixes. `docs-cli==1.6.0` built locally (pyproject + CHANGELOG);
  **publish is M17's.** 458 tests GREEN; quality gate clean tree-wide.
  Pair: [m14-robustness-agent-native.md](m14-robustness-agent-native.md)
  + [impl](m14-robustness-agent-native-impl.md).
- **M15 — Agent-native doc authoring (v1.6.0)** (**implementation-complete**
  2026-06-03, Phases 1–10) — `docs project set`, single-file `docs stamp`
  (write-then-stamp), the `--body-from` real-frontmatter detector, and the
  skill/cli docs. Carved out of M14 on 2026-06-02 (it outgrew M12 scale);
  **depends on M14**; builds 1.6.0 locally, publish is M17's. Pair:
  [m15-agent-native-authoring.md](m15-agent-native-authoring.md)
  + [impl](m15-agent-native-authoring-impl.md).

**M17 — PyPI publish 1.6.0** ships both (M12→M13 cadence). The
broader agent-native surface (global `--json`,
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
[m6-pypi-distribution.md](m6-pypi-distribution.md)'s top
"Scope reframe" callout and the
[release-runbook.md](release-runbook.md) for the operative
checklist.

### M9 — PyPI publish 1.3.0 (Complete 2026-05-25)

[m9-pypi-publish.md](m9-pypi-publish.md) walked top-to-bottom
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
  at [m7-migration-accuracy.md](m7-migration-accuracy.md).
- **M8 — Adoption workflow** (after M7): `--exclude` tree-wide
  (in `migrate` + `index` + `check` + `list` via `.docs.toml`'s
  new `[exclude]` section), triage flags
  (`--summary`, `--only ambiguous`), `docs new --body-from <-|path>`
  (closes Read-before-Write friction), and a substantial rewrite
  of the bundled skill's references for the adoption flow
  (SKILL.md stays slim — one pointer line). Stub at
  [m8-adoption-workflow.md](m8-adoption-workflow.md). Load-bearing
  ship gate: **fresh-subagent dogfooding** of the adoption loop
  end-to-end against trees the M8 author hasn't tuned for.

### M6 milestone-setup history (kept for context)

**M6 — PyPI distribution as `docs-cli` is in flight (milestone-setup
phase complete, 2026-05-23).** The task plan
[m6-pypi-distribution.md](m6-pypi-distribution.md) is promoted from
`draft` to `active`; the log
[m6-pypi-distribution-log.md](m6-pypi-distribution-log.md) is created.
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
[m5-claude-code-skill-log.md](m5-claude-code-skill-log.md) for the
per-phase history (and the post-ship section appended to it) and
[m5-claude-code-skill.md](m5-claude-code-skill.md) for the milestone
summary.

M4 — Migration helper (`docs migrate`) shipped 2026-05-22 across ten TDD
phases. It added one verb — `docs migrate <dir>` — that adopts a
non-conforming directory into the convention: it walks a foreign tree, infers
the required metadata per file, and produces a migration plan (dry-run by
default; `--apply` writes the metadata blocks and normalises archive-style
subdirectories). See [m4-migration-helper-log.md](m4-migration-helper-log.md)
for the per-phase history and [m4-migration-helper.md](m4-migration-helper.md)
for the milestone summary.

M3 — Validation and query (`check`, `list`) shipped 2026-05-22 across ten TDD
phases. It added two read-only verbs — `docs check` (validate the tree, with
CI-usable exit codes) and `docs list` (filterable query view with a stable
JSON schema) — and regrouped `INDEX.md` by `Project` then `Role`. See
[m3-validation-and-query-log.md](m3-validation-and-query-log.md) for the
per-phase history and [m3-validation-and-query.md](m3-validation-and-query.md)
for the milestone summary.

M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) shipped 2026-05-21
across ten TDD phases. See [m2-mutating-verbs-log.md](m2-mutating-verbs-log.md)
for the per-phase history and [m2-mutating-verbs.md](m2-mutating-verbs.md)
for the milestone summary.

M1 — Parser and `docs index` shipped 2026-05-20 across ten TDD phases.
See [m1-parser-and-index-log.md](m1-parser-and-index-log.md) for the
per-phase history and [m1-parser-and-index.md](m1-parser-and-index.md)
for the milestone summary.

## Milestone progress

| Milestone | Status | Task plan | Log |
|---|---|---|---|
| M1 — Parser and `docs index` | **Complete** (2026-05-20) | [Plan](m1-parser-and-index.md) | [Log](m1-parser-and-index-log.md) |
| M2 — Mutating verbs (`new`, `archive`, `mv`, `touch`) | **Complete** (2026-05-21) | [Plan](m2-mutating-verbs.md) | [Log](m2-mutating-verbs-log.md) |
| M3 — Validation and query (`check`, `list`) | **Complete** (2026-05-22) | [Plan](m3-validation-and-query.md) | [Log](m3-validation-and-query-log.md) |
| M4 — Migration helper (`docs migrate`) | **Complete** (2026-05-22) | [Plan](m4-migration-helper.md) | [Log](m4-migration-helper-log.md) |
| M5 — Claude Code skill | **Complete** (2026-05-22) | [Plan](m5-claude-code-skill.md) | [Log](m5-claude-code-skill-log.md) |
| M6 — PyPI distribution preparation as `docs-cli` | **Complete** (2026-05-24, preparation only; publish moved to M9) | [Plan](m6-pypi-distribution.md) | [Log](m6-pypi-distribution-log.md) |
| M7 — Migration plan accuracy | **Complete** (2026-05-25; ship-ready locally, publish DEFERRED to M9 batched 1.3.0 per OQ-C) | [Plan](m7-migration-accuracy.md) | [Log](m7-migration-accuracy-log.md) |
| M8 — Adoption workflow (agent-driveable) | **Complete** (2026-05-25; ship-ready locally as 1.3.0, publish DEFERRED to M9 batched 1.3.0 per OQ-C) | [Plan](m8-adoption-workflow.md) | [Log](m8-adoption-workflow-log.md) |
| M9 — PyPI publish 1.3.0 | **Complete** (2026-05-25; `docs-cli==1.3.0` on PyPI; repo public; `v1.3.0` tag + GitHub release) | [Plan](m9-pypi-publish.md) | [Log](m9-pypi-publish-log.md) |
| M10 — Adoption-flow polish + 1.3.0 carry-overs (v1.4.0) | **Complete** (2026-05-27; shipped to PyPI via M11; 400/400 GREEN at M10 close; kebab-tiny dogfood PASS) | [Plan](archive/2026-05-27/m10-adoption-polish.md) | [Log](m10-adoption-polish-impl.md) |
| M11 — PyPI publish 1.4.0 | **Complete** (2026-05-27; `docs-cli==1.4.0` on PyPI; `v1.4.0` tag + GitHub release; chain-of-custody bit-perfect; headline M10 contract holds against PyPI-served wheel) | [Plan](archive/2026-05-27/m11-pypi-publish.md) | [Log](m11-pypi-publish-impl.md) |
| M12 — Project rename + M11 wart fixes + version SoT (v1.5.0) | **Complete** (2026-05-28; `dist/docs_cli-1.5.0-*` built locally, twine check PASS, 433/433 pytest GREEN at simplify close; shipped to PyPI as 1.5.0 via M13 on 2026-05-29) | [Plan](m12-project-rename.md) | [Log](m12-project-rename-impl.md) |
| M13 — PyPI publish 1.5.0 | **Complete** (2026-05-29; `docs-cli==1.5.0` on PyPI; `v1.5.0` annotated tag + GitHub release; chain-of-custody bit-perfect; all four M12 headline contracts hold against the PyPI-served wheel) | [Plan](archive/2026-05-29/m13-pypi-publish.md) | [Log](m13-pypi-publish-impl.md) |
| M14 — Robustness + autonomous archive (v1.6.0) | **Implementation-complete** (2026-06-02; re-scoped 2026-06-02 — authoring set split to M15; `mv` atomicity, `new` strict-root, four-verb `touch`/`archive`/`mv`/`project rename` excludes, slug/`OSError`/`atomic_write`-fsync guards, non-interactive `--cascade`, bundled-ref guard + packaging fix; 458 GREEN, gate clean; `docs-cli==1.6.0` built locally — publish is M17's) | [Plan](m14-robustness-agent-native.md) | [Log](m14-robustness-agent-native-impl.md) |
| M15 — Agent-native doc authoring (v1.6.0) | **Implementation-complete** — Phases 1–10 (carved from M14 — `docs project set`, single-file `docs stamp`, `--body-from` real-frontmatter detector, skill/cli docs; depends on M14; builds 1.6.0 locally, publish is M17). Phases 1–4 (contract + RED baseline: 41 intended reds, 459 GREEN) on `m15/phases-1-4`; Phases 5–10 (impl + dogfood + closeout: all 41 RED → GREEN, 501 total, gate clean tree-wide, `docs check docs/` 0, bundled refs byte-identical) on `m15/phases-5-10` — both 2026-06-03. | [Plan](m15-agent-native-authoring.md) | [Log](m15-agent-native-authoring-impl.md) |
| M16 — Bundled docs skill quality artifacts | **Implementation complete** (2026-06-01; documentation-only bundled `docs` skill guidance; code on `main` as `9ceb113`; doc archival of the M16 trio DEFERRED to M18 — see the deferred-archival note below) | [Plan](m16-bundled-docs-skill-quality.md) | [Log](m16-bundled-docs-skill-quality-impl.md) |
| M17 — PyPI publish 1.6.0 | **Planned** (publish-only; ships M14 + M15 as `docs-cli==1.6.0` via the release-runbook, mirroring M13 → M12) | _not yet created_ | — |
| M18 — Archive edge integrity (intra-archive Related: rewriting) | **In progress** (Phase 1 done 2026-06-03; correctness fix to `docs archive` — rewrite the moved doc's own archive-subtree `Related:` edges + repoint already-archived referrers; deliberately flips the pinned `test_archive_does_not_rewrite_archive_subtree_edges`. Open Q1 RESOLVED: `docs mv` own-edge parity INCLUDED (operator). Depends on nothing; unblocks the completed-milestone archival backlog) | [Plan](m18-archive-edge-integrity.md) | [Log](m18-archive-edge-integrity-impl.md) |

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
[m9-pypi-publish.md](m9-pypi-publish.md)'s milestone-completion
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
