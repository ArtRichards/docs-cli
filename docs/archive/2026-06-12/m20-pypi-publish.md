# M20 — PyPI publish 1.6.5

Lifecycle: archived
Role: milestone
Project: docs
Updated: 2026-06-12
Archived-reason: Milestone M20 complete; docs-cli==1.6.5 shipped to PyPI 2026-06-12

Related:
- parent-of: m20-pypi-publish-impl.md
- child-of: plan.md
- pairs-with: release-runbook.md
- pairs-with: status.md
- pairs-with: archive/2026-06-12/m18-archive-edge-integrity.md
- pairs-with: archive/2026-06-12/m19-post-edit-validation.md

## Overview

> **Stub-drafted 2026-06-12, post M19 implementation-complete.** M20
> enters active state immediately — M19 is implementation-complete
> (all ten TDD phases done, merged to `main` at `2a270b0`), building
> `docs-cli==1.6.5` locally (M19 owns the `pyproject.toml` bump → `1.6.5`,
> the `tests/test_packaging.py` version-pin flip, and the
> `## 1.6.5 — UNRELEASED` CHANGELOG section). The operative checklist is
> [release-runbook.md](release-runbook.md); this milestone doc exists to
> give the publish work a named home, exit criteria, and a log to record
> what actually happened.

- Milestone: M20 (the v1.6.5 publish milestone)
- Title: PyPI publish `docs-cli` 1.6.5
- Surface: an operator-driven release of the post-M19 tree to PyPI as
  `docs-cli==1.6.5`, plus the `v1.6.5` git tag, the GitHub release with notes
  sourced from the CHANGELOG, the post-publish doc closeouts that turn the
  M18 + M19 + M20 rows in `status.md` and `plan.md` into the post-publish
  narrative, and — NEW vs the M17 publish — a **host-machine skill refresh**
  per the CLAUDE.md skill-update-flow policy (production ship is when the
  `~/.claude/skills/` copies are re-materialised from the published version).
- Status: **Setup complete (milestone-setup phase) — publish pending.** The
  runbook walk runs after this commit. The success criterion is concrete: a
  fresh venv on a clean host can `pip install docs-cli==1.6.5`,
  `docs --version` prints `docs 1.6.5`, the M19 headline contracts hold
  against the PyPI-served wheel (see Success Criteria below), `docs check
  <tree>` exits 0, and the public GitHub repo carries the matching `v1.6.5`
  tag + release.

### Goal

The v1.6.5 implementation train delivered one milestone locally. **M19 —
Post-edit validation ergonomics** added two operator-ergonomics affordances
on the post-edit loop plus one cosmetic help-string fix: (D1) `docs touch
--check [--stale N]` folds the existing `check_tree` machinery into
`docs touch` after its end-of-batch reindex, so the three-command post-edit
loop (`docs touch <files>` → `docs index .` → `docs check . --stale N`)
collapses to a single invocation (combined exit `max(touch, check)` with a
touch-fail short-circuit); (D2) a `.docs.toml [check] stale_days = N`
per-tree default the stale window reads from when no CLI `--stale` is given
(CLI `--stale` overrides; absent config preserves today's behaviour; the
stale finding names the threshold's provenance — `set in .docs.toml [check]
stale_days` config-sourced, `via --stale` CLI-sourced; a non-integer value is
refused cleanly at config load); (D3) the cosmetic `docs new --body-from`
argparse help-string fix closing the rolled-forward follow-on. M19 didn't
publish. Per the M8/M10/M12/M14+M15 → M9/M11/M13/M17 cadence (build locally
+ publish in a separate operator-driven milestone), M20 is the publish — and
it ships **M19 alone** as one public release, one-to-one (as M13 shipped M12
and M11 shipped M10; M9 and M17 were the batched shapes).

M20 is operator-driven by design: re-confirm pre-publish prep, rebuild fresh
artefacts from the post-M19-merge `main` tree (M19 built 1.6.5 locally, but a
fresh rebuild at M20 start is the discipline — M11 set the precedent and
M13/M17 confirmed it), TestPyPI rehearsal under the disambiguated dist name
`docs-cli-rehearsal==1.6.5` (continuing the M9/M11/M13/M17 TestPyPI-squatter
detour), real PyPI publish, tag + GitHub release, host-skill refresh,
post-release closeouts. No code work; no new verbs; no TDD code phases. The
success criterion is concrete: a fresh venv on a clean host can `pip install
docs-cli==1.6.5`, `docs --version` prints `docs 1.6.5`, the M19 headline
contracts hold against the PyPI-served wheel (see Success Criteria below),
`docs check <tree>` exits 0, and the public GitHub repo carries the matching
`v1.6.5` tag + release.

### Requirements

- **Version is `1.6.5`.** Already bumped at M19 Phase 7 (`pyproject.toml`
  `version = "1.6.5"`; `tests/test_packaging.py` A3/B1/B2/C2 pinned to
  `1.6.5`; `__version__` reads through `importlib.metadata.version("docs-cli")`
  per the M12 SoT refactor — so the version comes from `pyproject.toml`'s
  `[project] version` automatically). M20 publishes that version verbatim.
  Mirrors the M9/M11/M13/M17 cadence (one bump per implementation milestone;
  only the implementation milestone's version reaches PyPI — here M19 owns the
  bump).
- **Pre-publish operator state already current** from M17 — PyPI + TestPyPI
  accounts registered, 2FA active, API tokens in `~/.pypirc` (mode 600). The
  M9-era follow-on "token re-scope from entire-account to project-`docs-cli`"
  remains operator-side async work; M20 publishes with whatever scope the
  tokens currently carry (consistent with the M11/M13/M17 posture). If
  re-scoping landed between M17 and M20, the runbook step is a no-op; if not,
  the publish proceeds with the existing tokens and the re-scope follow-on
  rolls forward.
- **CHANGELOG `## 1.6.5 — UNRELEASED`** is already authored with
  publish-survival wording (M11 lesson — no "ready locally" / "deferred to
  MX" suffixes). M19 Phase 7 opened the fresh `## 1.6.5 — UNRELEASED`
  section above the dated `## 1.6.0` (a NEW section, not a fold-in — the
  1.6.0 section is published, M19's binding Decision). M20's runbook step is
  to drop `UNRELEASED` and replace with the publish date — verify the
  surrounding body (including the "Built locally; a later operator-driven
  milestone publishes to PyPI." lead-in) still reads accurately at publish
  time and rewrite the lead-in if it would read stale.
- **Quality gate green tree-wide** before any upload: pytest (540 at M19
  implementation-complete after the Step-2 review +7 — the exact count gets
  recorded into the runbook checklist at the moment of M20 run), ruff, ruff
  format, mypy, `docs check docs/`, `docs index --root docs/ --dry-run`.
- **Fresh artifact build at M20 start.** M19 built 1.6.5 locally during its
  own phases; M20 rebuilds from the post-merge-to-main tree (which carries
  the M19 stack + any M20-only edits — the dated CHANGELOG at Phase 4) so the
  artefact bytes line up with what `git log --oneline main` will show at the
  moment of publish. Never reuse the implementation milestone's local
  `dist/` — and note the repo `dist/` is gitignored; the `rm -rf dist/` at
  build start clears whatever is there.
- **TestPyPI rehearsal is non-optional** (mirrors M9/M11/M13/M17). Upload to
  TestPyPI under `docs-cli-rehearsal==1.6.5` (the bare `docs-cli` is parked
  on TestPyPI per the M9 open follow-on; re-check ownership at M20 start in
  case the squatter project lapsed), install from TestPyPI into a fresh
  `/tmp/docs-test-venv`, exercise the smoke set including the M19 headline
  contracts. **Known-expected (carried from M13):** the rehearsal wheel
  prints `docs 0.0.0+local`, not `docs 1.6.5`, because `__version__` reads
  `importlib.metadata.version("docs-cli")` and the rehearsal installs the
  distribution as `docs-cli-rehearsal` — the lookup misses and falls back to
  the documented `0.0.0+local`. Verify the version-string contract against the
  canonical-name local wheel (pre-publish smoke) and the PyPI wheel (Phase 4),
  never the rehearsal wheel. If anything else fails, bump to `1.6.6` (TestPyPI
  also rejects re-uploads of the same version) and rerun from artifact build.
- **Real PyPI publish.** `twine upload dist/*` to PyPI, install from PyPI into
  a fresh `/tmp/docs-real-venv`, re-run the smoke subset against the real
  artefact; chain-of-custody check via `pip download` + `sha256sum`
  (PyPI-served wheel sha256 byte-identical to the local Phase 4 build —
  bit-perfect at M11/M13/M17).
- **Host-machine skill refresh (NEW vs M17 — CLAUDE.md policy).** Per the
  CLAUDE.md "Skill update flow" policy (2026-06-12), host skills in
  `~/.claude/skills/` are refreshed ONLY at production ship. M20's closeout
  runs `docs install-skill --force` from the published 1.6.5 surface and
  sweeps the workflow skills' docs-cli prescriptions for the new surface
  (`touch --check`, `[check] stale_days`) at that point. This is the
  bundled-skill → host-skill channel firing — distinct from the per-CLI-update
  bundled-skill resync that M19 already did in-repo (`src/docs_cli/skill/`).
  See the "M20 closeout refreshes host skills" Decision.
- **Post-release sequence.** `git tag -a v1.6.5 && git push origin v1.6.5` at
  the Phase 4 commit, `gh release create v1.6.5` with notes sourced from the
  CHANGELOG `## 1.6.5` section, doc closeouts (M18 + M19 + M20 rows in
  `status.md` and `plan.md` finalised; `docs/INDEX.md` +
  `tests/fixtures/expected/docs-INDEX.md` regenerated in lockstep). No
  repo-visibility flip — repo is already public from M9. **M18 + M19
  milestone-doc archival** is part of the closeout — they are deliberately
  LIVE at root awaiting a sweep (M18 is implementation-complete since
  2026-06-03; M19 is implementation-complete since 2026-06-12; both "await
  the sweep"). M20's Phase-5 closeout archives the M18 pair + the M19 pair +
  M20's own milestone doc per the M17 Q2 precedent (the impl log + runbook +
  status stay active).

### Deliverables

- [x] PyPI release `docs-cli` 1.6.5 published; project page live at
      `https://pypi.org/project/docs-cli/1.6.5/`.
- [x] TestPyPI release `docs-cli-rehearsal` 1.6.5 published as the rehearsal
      artifact at
      `https://test.pypi.org/project/docs-cli-rehearsal/1.6.5/` (continues the
      M9/M11/M13/M17 disambiguated dist-name detour).
- [x] `pyproject.toml` `version` confirmed at `1.6.5` (landed at M19 Phase 7;
      `__version__` flows through `importlib.metadata` per M12 SoT refactor —
      verified at Phase 2).
- [x] `CHANGELOG.md` `## 1.6.5 — UNRELEASED` section dated to `## 1.6.5 —
      <publish-date>`; surrounding body re-verified accurate (stale "built
      locally" lead-in re-read / dropped at Phase 4 if it reads stale).
- [x] `v1.6.5` git tag pushed; GitHub release created with notes sourced from
      the CHANGELOG `## 1.6.5` section.
- [x] **Host-machine skills refreshed (NEW vs M17):** `docs install-skill
      --force` re-materialises `~/.claude/skills/` from the published 1.6.5
      surface; the workflow skills' docs-cli prescriptions swept for the new
      surface (`touch --check`, `[check] stale_days`).
- [x] `docs/status.md`: M18 + M19 + M20 rows finalised; "Current milestone" +
      "Next action" rewritten post-publish.
- [x] `docs/plan.md`: M18 + M19 + M20 rows finalised; Sequencing timeline grew
      the publish line.
- [x] `docs/m20-pypi-publish.md` (this file): Phase Checklist ticked;
      milestone-completion summary appended; lifecycle archived via
      `docs archive` to `archive/<publish-date>/`.
- [x] `docs/m20-pypi-publish-impl.md`: per-phase log entries + final
      milestone-completion summary; stays `Lifecycle: active` after
      milestone-doc archive (per the M8/M9/M10/M11/M13/M17 pattern).
- [x] `docs/m18-archive-edge-integrity.md` +
      `docs/m19-post-edit-validation.md` (and their impl logs) archived as
      part of the M20 closeout to `archive/<publish-date>/` — they were left
      LIVE at root awaiting a sweep (M17 Q2 precedent; see Decisions).
- [x] `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` regenerated in
      lockstep.

## Phase Checklist

M20 has no TDD code phases — it is an operational milestone. The runbook's
sections are the phases (mirrors M9/M11/M13/M17 exactly):

- [x] Operator one-time prep — session-verifiable state captured at M20 start
      (`~/.pypirc` intact mode 600; PyPI `docs-cli` at 1.6.0, 1.6.5 slot free;
      TestPyPI `docs-cli` squatter status re-checked; TestPyPI
      `docs-cli-rehearsal` 1.6.5 slot free; twine + build tool versions ready).
- [x] Pre-publish prep — versions verified `1.6.5` (M19 Phase 7 landed
      `pyproject.toml`; M12 SoT refactor flows `__version__` through
      `importlib.metadata`), CHANGELOG header `## 1.6.5 — UNRELEASED`, tree at
      the M20 setup commit, quality gate green tree-wide (540 passed), fresh
      artefacts rebuilt, local-install smoke + the M19 headline contracts
      verified against the wheel.
- [x] TestPyPI rehearsal — uploaded as `docs-cli-rehearsal==1.6.5`;
      throwaway-venv install from TestPyPI succeeded; full smoke including the
      M19 headline contracts passed against the TestPyPI-served wheel (with the
      known-expected `docs --version` → `0.0.0+local` rehearsal-name caveat).
- [x] Real PyPI publish — `docs-cli==1.6.5` LIVE on PyPI; both artefacts
      twine-check PASS; upload PASS; chain-of-custody bit-perfect (PyPI-served
      wheel **and sdist** sha256 byte-identical to local Phase 4 build);
      throwaway-venv install from PyPI succeeded (`docs 1.6.5`); full smoke +
      the M19 headline contracts PASS against the PyPI-served wheel.
- [x] Post-release — annotated `v1.6.5` tag at the Phase-4 commit `0855466`
      pushed to `origin`; GitHub release live with notes sourced from
      `## 1.6.5`; **host skills refreshed** (`docs install-skill --force` +
      workflow-skill sweep — NEW vs M17; the sweep caught + fixed one stale
      `--body-from` reference in `project-foundation`); doc closeouts (plan/
      status/INDEX + dogfood snapshot + the M18 + M19 milestone-doc archival —
      both plan + impl pairs, four docs) landed; `docs archive` /
      `--cascade-only` ran (M18 + M19 both pairs **and** the M20 milestone doc
      archived to `archive/2026-06-12/`; M20 impl log stays `Lifecycle:
      active`; release-runbook + status declined). Token re-scope continues to
      roll forward as the M9 open follow-on.

Each ticks as the runbook's corresponding section completes.

## Decisions

- **Version is 1.6.5.** Already bumped at M19 Phase 7 across `pyproject.toml`
  and `tests/test_packaging.py` (A3/B1/B2/C2); `__version__` reads through
  `importlib.metadata.version("docs-cli")` per the M12 SoT refactor — so the
  version comes from `pyproject.toml`'s `[project] version` automatically. M20
  publishes that version verbatim. Mirrors the M9/M11/M13/M17 cadence (one
  bump per implementation milestone; only the implementation milestone's
  version reaches PyPI).
- **M20 ships M19 alone as one 1.6.5 release (one-to-one).** M19 is the only
  implementation milestone built on the `## 1.6.5` CHANGELOG section; the
  publish ships it alone, exactly as M13 shipped M12 and M11 shipped M10
  (one-to-one). M9 (M6+M7+M8 → 1.3.0) and M17 (M14+M15 → 1.6.0) were the
  batched shapes; M20→M19 is the one-to-one shape again. M18 is a
  correctness-fix milestone whose code already shipped to users inside 1.6.0
  (it rode along in the M17 tree as an already-merged archive-edge fix); its
  milestone-doc archival rides M20's closeout sweep but it adds no new public
  surface to 1.6.5.
- **Runs on main (M17 precedent).** A publish milestone has no TDD code
  phases, so it runs directly on `main` — the milestone-setup commit and the
  runbook-phase commits all land on `main` (M17 precedent:
  `m17(setup)`/`m17(phase 2-3)`/`m17(phase 4)`/`m17(phase 5)` were all on
  `main`). No feature branch; the conductor walks the runbook on `main` after
  this setup commit.
- **M20 closeout refreshes the host-machine skills (NEW scope vs M17 —
  CLAUDE.md policy).** The CLAUDE.md "Skill update flow" policy (operator,
  2026-06-12) draws a hard line: the **bundled** skill (`src/docs_cli/skill/`)
  refreshes in the SAME change as every CLI surface update (M19 did this
  in-repo — the surface-parity gate), but the **host-machine** skills
  (`~/.claude/skills/`) refresh ONLY at production ship. M20 IS that
  production ship, so its Phase-5 closeout runs `docs install-skill --force`
  from the published 1.6.5 to re-materialise the host `docs` skill, then
  sweeps the workflow skills' docs-cli prescriptions for the new surface
  (`touch --check`, `[check] stale_days`) and verifies they match the
  now-published behaviour. This is NEW scope vs M17 (the policy postdates the
  M17 publish), and it is the only structural difference between the M20 and
  M17 runs.
- **Manual `twine`, not Trusted Publishing.** Continues the
  M6 + M9 + M11 + M13 + M17 stance. OIDC / GitHub-Actions Trusted Publishing
  remains a future iteration; manual `twine` is acceptable at v1.6.5. Revisit
  at v2 if the manual flow proves cumbersome.
- **TestPyPI rehearsal under disambiguated dist name.** Continues the
  M9/M11/M13/M17 detour while the TestPyPI `docs-cli` squatter project is
  still parked. M20 re-checks ownership at the operator-prep step; if the
  squatter project ever lapses, M20 (or a later release) drops the
  rehearsal-name detour.
- **Fresh artifacts at M20, not the M19 local build.** The M19 `dist/`
  predates any merge-to-main commits and the Phase-4 dated CHANGELOG. M20
  rebuilds from post-merge-to-main HEAD at publish time. (The repo `dist/` is
  gitignored; `rm -rf dist/` clears whatever is there.)
- **Repo visibility flip is N/A.** Repo is already public from M9's
  post-release sequence.
- **No feature work in M20.** No new verbs, no scope additions. M20 is a
  publish-only milestone mirroring M9's/M11's/M13's/M17's discipline; mixing
  release-event work with feature work is rejected by design.
- **CHANGELOG publish-survival wording already locked.** The `## 1.6.5 —
  UNRELEASED` entry was authored conservatively by M19 per the M11 lesson — no
  "ready locally" / "deferred to MX" sentences (the lead-in "Built locally; a
  later operator-driven milestone publishes to PyPI." describes state, not a
  deferral, and is dropped/rewritten as part of the Phase-4 date edit if it
  would read stale). M20's runbook step is mechanical: drop `UNRELEASED`,
  replace with publish date, re-verify body reads accurately. No
  `gh release edit` amend post-publish expected (the M11 deviation should not
  recur).
- **M13's two deviations carry forward as known-expected at M20.** (1) The
  TestPyPI rehearsal wheel prints `docs 0.0.0+local` under the rename detour
  (the `importlib.metadata` SoT can't resolve the renamed
  `docs-cli-rehearsal` distribution) — verify the version string against the
  canonical-name local + PyPI wheels, never the rehearsal wheel. (2)
  `CHANGELOG.md` is not shipped inside the sdist (hatchling captures `src/`,
  `docs/`, `tests/`, `README.md`, `LICENSE`, `pyproject.toml`). Both are
  already folded into the runbook's Cumulative-lessons + TestPyPI +
  Artifact-build sections, so M20 inherits them automatically; they are
  recorded here only so the Phase-3 `0.0.0+local` print and any Phase-2 ≡
  Phase-4 sdist sha movement are not mistaken for regressions.
- **Fully-autonomous publish authorization (Q1) — see OPEN QUESTIONS.** The
  M13 + M17 operators each authorized a fully-autonomous publish run
  including the irreversible real-PyPI upload + `main` push + tag + GitHub
  release up front. M20 carries the same question to the operator; the
  recommended default is the M17 posture (full autonomous, walk the runbook
  end-to-end in one pass). Recorded as Q1 until the operator confirms.
- **M20 closeout archives M18 + M19 + its own milestone doc (Q2 — see OPEN
  QUESTIONS).** M18 and M19 are both implementation-complete and deliberately
  LIVE at root awaiting a sweep (a milestone flips to `archived` only when a
  later milestone physically moves it into the archive subtree). The M17 Q2
  precedent put that sweep at the publish milestone's Phase-5 closeout: it
  archives M18 + M19 (both plan + impl pairs, four docs) **plus** M20's own
  milestone doc to `archive/<publish-date>/` via `docs archive --cascade` /
  `--cascade-only` (the M12 + M18 edge machinery repoints referring `Related:`
  edges atomically), and flips the M18 + M19 `status.md` / `plan.md` rows to
  Complete/archived with the publish date. The M20 impl log, the
  release-runbook, and `status.md` stay `Lifecycle: active` per the
  M8/M9/M10/M11/M13/M17 pattern. Recommended default matches M17; recorded as
  Q2 until the operator confirms.

## Testing / Quality Gate

The same tree-wide gate the M19 implementation ran, plus the
publish-specific smokes the runbook details:

```sh
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/docs check docs/
.venv/bin/docs index --root docs/ --dry-run
rm -rf dist/ && .venv/bin/python -m build
.venv/bin/twine check dist/*
```

Plus the M20-specific dogfood: walk [release-runbook.md](release-runbook.md)
end-to-end against TestPyPI then real PyPI, with the smoke set covering the
M19 headline contracts (see Success Criteria), and the NEW host-skill-refresh
step (`docs install-skill --force` from the published wheel + the workflow-skill
sweep).

## Success Criteria

M20 is complete when:

- [x] `pip install docs-cli==1.6.5` works from PyPI on a clean host with
      Python 3.11+ and produces a working `docs` command.
- [x] `docs --version` from the PyPI-installed wheel prints `docs 1.6.5`.
- [x] **M19 contract — `docs touch --check` exit fold:** `docs touch <files>
      --check` runs the tree-wide check after the end-of-batch reindex in one
      invocation; its exit code is `max(touch, check)` with a touch-fail
      short-circuit (clean → 0; stale-only → 1; broken-ref/errors → 2)
      (verified against the PyPI-served wheel, not just the local build).
- [x] **M19 contract — `--stale` requires `--check` refusal:** `docs touch
      --stale N` without `--check` is a hard exit 2 (`docs: touch: --stale
      requires --check`); the file is byte-unchanged and no INDEX refresh runs
      (re-verified against the PyPI-served wheel).
- [x] **M19 contract — `[check] stale_days` bare-check arming + CLI override:**
      a `.docs.toml [check] stale_days = N` arms the stale rule on bare
      `docs check` (no `--stale`); an explicit CLI `--stale` overrides it; a
      tree with no `[check]` section is unchanged; a non-integer value is
      refused cleanly (exit 2, `malformed .docs.toml: [check] stale_days must
      be an integer`, no traceback); `docs list --stale` is unaffected (Q6)
      (re-verified against the PyPI-served wheel).
- [x] **M19 contract — both provenance message variants:** the stale finding
      names the threshold's provenance — config-sourced appends `set in
      .docs.toml [check] stale_days`, CLI-sourced appends `via --stale`
      (re-verified against the PyPI-served wheel).
- [x] **M19 contract — `--body-from` help fixed:** `docs new --help` no longer
      describes the "first 20 lines" heuristic; the corrected wording names the
      real detector (a leading `---` fence or ≥ 2 adjacent `{Lifecycle, Role,
      Updated}` lines) (re-verified against the PyPI-served wheel).
- [x] `docs install-skill` from the PyPI-installed wheel places a host-correct
      skill that drives the verbs identically to the in-repo install; bundled
      references carry no repo-relative `../` links; byte-identical to
      `src/docs_cli/skill`, re-run no-op exit 0, `--symlink` exit 2 (verified
      against the PyPI-served wheel).
- [x] **Host skills refreshed (NEW vs M17):** `docs install-skill --force`
      re-materialised `~/.claude/skills/` from the published 1.6.5 surface; the
      workflow skills' docs-cli prescriptions swept and confirmed to match the
      now-published `touch --check` + `[check] stale_days` surface.
- [x] The `v1.6.5` tag and GitHub release exist at
      `https://github.com/ArtRichards/docs-cli/releases/tag/v1.6.5` (annotated
      `v1.6.5` tag at the Phase-4 dated-CHANGELOG commit whose tree matches
      PyPI + the GitHub release are the closeout git sequence).
- [x] All Phase Checklist items above are ticked.
- [x] `docs/status.md` reflects M18 + M19 + M20 as Complete/archived with the
      actual publish date.
- [x] `docs/m20-pypi-publish-impl.md` carries a milestone-completion summary
      with the published version (`1.6.5` — assuming no TestPyPI-surfaced
      regression forces a `1.6.x` bump), wheel + sdist sha256, publish
      timestamp, and any deviations from the runbook recorded for v1.7+
      reference.

## Milestone-completion summary

**M20 complete — `docs-cli==1.6.5` shipped to PyPI 2026-06-12**, the
publish-only counterpart to **M19**, one-to-one (as M13 shipped M12 and M11
shipped M10; M9 and M17 were the batched shapes). Driven end-to-end as a
fully-autonomous run walking [release-runbook.md](release-runbook.md) directly
(no TDD code phases); the operator authorized the irreversible PyPI upload +
`main` push + `v1.6.5` tag + GitHub release up front (Q1 → FULL AUTONOMOUS).
**NEW vs M17:** the closeout refreshed the host-machine skills per the CLAUDE.md
skill-update-flow policy.

- **PyPI:** https://pypi.org/project/docs-cli/1.6.5/ · **TestPyPI rehearsal:**
  https://test.pypi.org/project/docs-cli-rehearsal/1.6.5/ · **GitHub release:**
  https://github.com/ArtRichards/docs-cli/releases/tag/v1.6.5
- **Published artefact sha256:**
  - wheel `docs_cli-1.6.5-py3-none-any.whl`:
    `aba36e92d92363958f0b9e91e52a769e2f10f69d92437a44c83cebeef396b4e0`
  - sdist `docs_cli-1.6.5.tar.gz`:
    `f9de1eb49ff84271969c6b4b7e0faef93a138bea0813cb1effd1d1314eff12be`
- **Chain-of-custody — BIT-PERFECT (wheel AND sdist).** Both PyPI-served
  sha256s byte-identical to the local Phase-4 build (M20 extended the M17
  wheel-only check to the sdist too). Fifth release running (M11 + M13 + M17 +
  M20).
- **Quality gate at publish:** 540 passed; ruff / format / mypy clean; `docs
  check docs/` exit 0; index dry-run idempotent.
- **All M19 headline contracts PASS against the PyPI-served wheel** (`docs
  --version` → `docs 1.6.5`; `touch --check` clean/stale-fold; `--stale`
  requires `--check`; `[check] stale_days` arms bare check + CLI override +
  non-integer refusal; both provenance variants; `--body-from` help = real
  detector; `install-skill` byte-identical / no-op / `--symlink` exit 2).
- **`v1.6.5`** annotated tag at the Phase-4 commit `0855466`; GitHub release
  with `## 1.6.5` notes.
- **Host-machine skills refreshed (NEW vs M17):** `~/.claude/skills/docs`
  byte-identical to the published wheel's bundled skill; the workflow-skill
  sweep caught + fixed one stale `--body-from` "first 20 lines" reference in
  `project-foundation`.
- **Deviations:** the two M13 known-expected (TestPyPI rehearsal `0.0.0+local`;
  CHANGELOG not in sdist/wheel → the sdist sha moved from the GO-report build
  only because `docs/` evolved, not the date edit). No forced `1.6.x` bump. Full
  deviation prose in
  [m20-pypi-publish-impl.md](m20-pypi-publish-impl.md)'s milestone-completion
  summary, including the new M20 host-skill-drift finding.

## OPEN QUESTIONS

Two genuine release-event decisions for the operator. Each: question, why it
matters, recommended answer (the four-prior-publish precedent is thick — both
recommend the M17 posture).

- **Q1 — Publish-execution authorization & mode.** *Why it matters:* the real
  PyPI `twine upload` of `docs-cli==1.6.5`, the `main` push, the `v1.6.5` tag
  push, and the GitHub release are all irreversible; the conductor needs the
  operator's authorization to walk the runbook end-to-end in one pass rather
  than stopping at the pre-publish-prep / TestPyPI-rehearsal boundary.
  *Recommendation:* **FULL AUTONOMOUS** — mirror the M13 + M17 operator
  authorizations (each explicitly authorized the irreversible upload + push +
  tag + release up front). M20 does not stop at the TestPyPI-rehearsal
  boundary; the conductor walks the release-runbook end-to-end. Fold into
  Decisions ("Fully-autonomous publish authorized") at Step 0 once confirmed.
- **Q2 — M18 + M19 milestone-doc archival at the M20 closeout.** *Why it
  matters:* M18 and M19 are both implementation-complete and LIVE at root;
  archiving a milestone is what marks it shipped/swept, and the M20 closeout is
  the natural sweep point. *Recommendation:* **ARCHIVE AT M20 CLOSEOUT** —
  M20's Phase-5 closeout archives M18 + M19 (both plan + impl pairs, four docs)
  **plus** M20's own milestone doc to `archive/<publish-date>/` via
  `docs archive --cascade` / `--cascade-only`, flipping the M18 + M19
  `status.md` / `plan.md` rows to Complete/archived with the publish date. The
  M20 impl log, release-runbook, and `status.md` stay `Lifecycle: active`.
  Mirrors the M17 Q2 resolution. Fold into Decisions ("M20 closeout archives
  M18 + M19 + its own milestone doc") once confirmed.

OPEN QUESTIONS: Q1 + Q2 above are the only outstanding decisions; both carry a
recommended default (the M17 posture). All publish-mechanics questions are
already settled by the four-prior-publish precedent folded into the runbook.
