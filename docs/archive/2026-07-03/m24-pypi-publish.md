# M24 — PyPI publish 1.8.0

Lifecycle: archived
Role: milestone
Project: docs
Updated: 2026-08-14
Archived-reason: Milestone M24 complete; docs-cli==1.8.0 shipped to PyPI 2026-07-03

Related:
- parent-of: m24-pypi-publish-impl.md
- child-of: plan.md
- pairs-with: release-runbook.md
- pairs-with: status.md
- pairs-with: archive/2026-07-03/m21-update-check.md
- pairs-with: archive/2026-07-03/m22-root-placement-guidance.md
- pairs-with: archive/2026-07-03/m23-agent-aware-install-skill.md

Revision:
- 2026-08-14: M27 one-time body-link migration; body-link destinations repaired (destination tokens only)

## Overview

> **Stub-drafted 2026-07-03**, immediately after M23 was merged to `main`
> (merge commit `839daef`). M24 enters active state at once — the three
> milestones it ships are all implementation-complete and building
> `docs-cli==1.8.0` locally (M23 owns the `pyproject.toml` bump → `1.8.0`,
> the `tests/test_packaging.py` version-pin flip, and the CHANGELOG
> sections). The operative checklist is
> [release-runbook.md](../../release-runbook.md); this milestone doc exists to
> give the publish work a named home, exit criteria, and a log to record
> what actually happened.

- Milestone: M24 (the v1.8.0 publish milestone)
- Title: PyPI publish `docs-cli` 1.8.0
- Surface: an operator-driven release of the post-M23 `main` tree to PyPI as
  `docs-cli==1.8.0`, plus the `v1.8.0` git tag, the GitHub release with notes
  sourced from the CHANGELOG, the post-publish doc closeouts that turn the
  M21 + M22 + M23 + M24 rows in `status.md` and `plan.md` into the
  post-publish narrative, and — per the CLAUDE.md skill-update-flow policy
  (established at M20) — a **host-machine skill refresh** (production ship is
  when the `~/.claude/skills/` copies are re-materialised from the published
  version).
- Status: **COMPLETE (2026-07-03) — `docs-cli==1.8.0` shipped to PyPI.** All
  five runbook phases done; chain-of-custody bit-perfect for both wheel
  (`29ac3ced…`) and sdist (`62a29285…`); `v1.8.0` annotated tag at `1a01f74` +
  GitHub release; host skills refreshed. See the milestone-completion summary
  below and [m24-pypi-publish-impl.md](../../m24-pypi-publish-impl.md) for the full
  per-phase record.

### Goal

The train since the last publish (**1.6.5 via M20, 2026-06-12**) delivered
three milestones locally, none yet on PyPI. M24 publishes them **batched** as
one public release — `docs-cli==1.8.0` — mirroring the batched shapes M17
(shipped M14+M15 as 1.6.0) and M9 (shipped M6+M7+M8 as 1.3.0):

- **M21 — Update-check notification** (built as 1.7.0): docs-cli's **first
  network surface** — a once-per-24h, fail-silent PyPI version check (stdlib
  `urllib`, 1.0s timeout, 24h-cache-gated under
  `${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json`, zero-dependency
  wheel preserved) that emits ONE STDERR line
  (`docs: update available <current> -> <latest> — run: pip install -U
  docs-cli`). STDERR-only, never alters the exit code, suppressed under
  `--quiet` / `--json` / `CI` / `DOCS_CLI_NO_UPDATE_CHECK` / `DO_NOT_TRACK`,
  deliberately shown on non-TTY (the agent is the actor).
- **M22 — Doc-tree root placement guidance** (documentation-only, no version
  bump, no code): `convention.md` §Subdirectories + the bundled `SKILL.md`
  gained "where to put `.docs.toml`" guidance (project = metadata slug, not a
  directory; nesting a lone project under a parent root prefixes every
  intra-project `Related:` reference with a redundant `<subdir>/`).
- **M23 — Agent-aware install-skill + recorded-dest skill-refresh hint**
  (built as 1.8.0): `docs install-skill` becomes agent-aware (`--dest` is the
  agent-agnostic source of truth; TTY-aware resolution never blocks a non-TTY
  agent on a prompt; the resolved dest is **recorded** — a path only — to
  `${XDG_STATE_HOME:-~/.local/state}/docs-cli/install-skill.json`); the
  "Claude Code skill" framing is neutralised to "agent skill"; and M21's
  update notice gains a second STDERR line — a skill-refresh hint pointed at
  the recorded dest, riding M21's same suppression matrix + 24h throttle.

**1.7.0 is a version number skipped on PyPI.** M21 bumped `pyproject` to
1.7.0; M23 bumped it to 1.8.0. Only 1.8.0 reaches PyPI. Per the operator
decision (2026-07-03) the CHANGELOG's `## 1.7.0 — UNRELEASED` section is
**folded up into the single dated `## 1.8.0` section** at Phase 4 (no 1.7.0
header survives) — one published version, one CHANGELOG section.

M24 is operator-driven by design: re-confirm pre-publish prep, rebuild fresh
artefacts from the post-M23-merge `main` tree, TestPyPI rehearsal under the
disambiguated dist name `docs-cli-rehearsal==1.8.0` (continuing the
M9/M11/M13/M17/M20 TestPyPI-squatter detour), real PyPI publish, tag + GitHub
release, host-skill refresh, post-release closeouts. No code work; no new
verbs; no TDD code phases.

### Requirements

- **Version is `1.8.0`.** Already bumped at M23 Phase 7 (`pyproject.toml`
  `version = "1.8.0"`; `tests/test_packaging.py` version pins flipped;
  `__version__` reads through `importlib.metadata.version("docs-cli")` per the
  M12 SoT refactor). M24 publishes that version verbatim. **1.7.0 is skipped
  on PyPI** (the M21 bump; its CHANGELOG entries fold into 1.8.0).
- **M23 OQ-1/OQ-2 confirmed as-shipped (2026-07-03).** M23 resolved OQ-1
  (non-TTY → fall back to the default dest, never refuse) and OQ-2 (a
  **separate** state file at `${XDG_STATE_HOME}/docs-cli/install-skill.json`;
  M21's 3-key update-check cache stays frozen) provisionally while the
  operator was away, flagged for confirmation at branch review. **This publish
  is that gate; both stand as shipped** — no code change, no re-bump. The flag
  is cleared (see Decisions).
- **Pre-publish operator state already current** from M20 — PyPI + TestPyPI
  accounts registered, 2FA active, API tokens in `~/.pypirc` (mode 600). The
  M9-era "token re-scope to project-`docs-cli`" remains async operator-side
  work; M24 publishes with whatever scope the tokens currently carry
  (M11/M13/M17/M20 posture).
- **CHANGELOG fold + date.** Two `— UNRELEASED` sections exist (`## 1.8.0`
  for M22+M23, `## 1.7.0` for M21). M24's Phase-4 runbook step **folds 1.7.0's
  entries up into 1.8.0** and dates the merged section `## 1.8.0 —
  <publish-date>`; the `## 1.7.0` header is removed. Verify publish-survival
  wording (no "UNRELEASED" / "built locally" residue) before upload.
- **Quality gate green tree-wide** before any upload: pytest (636 at M23
  implementation-complete — the exact count recorded into the runbook
  checklist at the moment of M24 run), ruff, ruff format, mypy,
  `docs check docs/`, `docs index --root docs/ --dry-run` idempotent, and
  `docs/INDEX.md` byte-identical to `tests/fixtures/expected/docs-INDEX.md`.
- **Surface-parity gate** (the CLAUDE.md skill-update-flow policy): the
  bundled skill's `references/cli.md` + `references/convention.md` are
  byte-identical to `docs/cli.md` + `docs/convention.md`, and the argparse
  `--help` strings match the shipped surface — verified before upload.
- **Fresh artifact build at M24 start.** Rebuild from the post-merge `main`
  tree (which carries the M21+M22+M23 stack + the Phase-4 folded/dated
  CHANGELOG). Never reuse an implementation milestone's local `dist/`; the
  repo `dist/` is gitignored, so `rm -rf dist/` at build start clears it.
- **TestPyPI rehearsal is non-optional** (mirrors M9/M11/M13/M17/M20). Upload
  under `docs-cli-rehearsal==1.8.0` (re-check the bare-`docs-cli` squatter at
  M24 start in case it lapsed), install from TestPyPI into a fresh
  `/tmp/docs-test-venv`, exercise the smoke set including the M21 + M23
  headline contracts. **Known-expected (carried from M13):** the rehearsal
  wheel prints `docs 0.0.0+local`, not `docs 1.8.0`, because the rehearsal
  installs the distribution as `docs-cli-rehearsal` and the
  `importlib.metadata` lookup misses. Verify the version-string contract
  against the canonical-name local wheel + the PyPI wheel, never the rehearsal
  wheel. If anything else fails, bump to `1.8.1` and rerun from artifact build.
- **Real PyPI publish.** `twine upload dist/*` to PyPI, install from PyPI into
  a fresh `/tmp/docs-real-venv`, re-run the smoke subset against the real
  artefact; chain-of-custody via `pip download` + `sha256sum` (PyPI-served
  wheel **and sdist** sha256 byte-identical to the local Phase-4 build —
  bit-perfect since M11/M13/M17/M20).
- **Host-machine skill refresh (CLAUDE.md policy, established M20).** M24's
  closeout runs `docs install-skill --force` from the published 1.8.0 surface
  and sweeps the workflow skills' docs-cli prescriptions for the new surface
  (M21 update-check, M23 agent-aware install-skill + recorded-dest). This is
  the bundled-skill → host-skill channel firing — distinct from the
  per-CLI-update bundled-skill resync M21/M23 already did in-repo
  (`src/docs_cli/skill/`).
- **Post-release sequence.** Push the Phase-4 commit to `main`, `git tag -a
  v1.8.0 && git push origin v1.8.0` at that commit, `gh release create v1.8.0`
  with notes sourced from the CHANGELOG `## 1.8.0` section, doc closeouts
  (M21 + M22 + M23 + M24 rows in `status.md` and `plan.md` finalised;
  `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` regenerated in
  lockstep). No repo-visibility flip — public since M9. **M21 + M22 + M23
  milestone-doc archival** is part of the closeout — all three are LIVE at
  root awaiting a sweep; M24's Phase-5 closeout archives the M21 pair + the
  M22 pair + the M23 pair + M24's own milestone doc per the M17/M20 Q2
  precedent (the M24 impl log + runbook + status stay active).

### Deliverables

- [x] PyPI release `docs-cli` 1.8.0 published; project page live at
      `https://pypi.org/project/docs-cli/1.8.0/`.
- [x] TestPyPI release `docs-cli-rehearsal` 1.8.0 published as the rehearsal
      artifact (continues the M9/M11/M13/M17/M20 disambiguated dist-name
      detour).
- [x] `pyproject.toml` `version` confirmed at `1.8.0` (landed at M23 Phase 7;
      `__version__` flows through `importlib.metadata` per M12 SoT refactor).
- [x] `CHANGELOG.md`: `## 1.7.0` entries folded up into `## 1.8.0`; the merged
      section dated `## 1.8.0 — <publish-date>`; no `UNRELEASED` / 1.7.0
      header survives.
- [x] `v1.8.0` git tag pushed; GitHub release created with notes sourced from
      the CHANGELOG `## 1.8.0` section.
- [x] **Host-machine skills refreshed:** `docs install-skill --force`
      re-materialises `~/.claude/skills/` from the published 1.8.0 surface;
      the workflow skills' docs-cli prescriptions swept for the new surface
      (M21 update-check, M23 agent-aware install-skill + recorded-dest).
- [x] `docs/status.md`: M21 + M22 + M23 + M24 rows finalised; "Current
      milestone" + "Next action" rewritten post-publish.
- [x] `docs/plan.md`: M21 + M22 + M23 + M24 rows finalised; Sequencing
      timeline grew the publish line.
- [x] `docs/m24-pypi-publish.md` (this file): Phase Checklist ticked;
      milestone-completion summary appended; lifecycle archived via
      `docs archive` to `archive/<publish-date>/`.
- [x] `docs/m24-pypi-publish-impl.md`: per-phase log entries + final
      milestone-completion summary; stays `Lifecycle: active` after
      milestone-doc archive (per the M8/M9/M10/M11/M13/M17/M20 pattern).
- [x] `docs/m21-update-check.md` + `docs/m22-root-placement-guidance.md` +
      `docs/m23-agent-aware-install-skill.md` (and their impl logs) archived
      as part of the M24 closeout to `archive/<publish-date>/` — all three
      left LIVE at root awaiting a sweep (M17/M20 Q2 precedent; see Decisions).
- [x] `docs/INDEX.md` + `tests/fixtures/expected/docs-INDEX.md` regenerated in
      lockstep.

## Phase Checklist

M24 has no TDD code phases — it is an operational milestone. The runbook's
sections are the phases (mirrors M9/M11/M13/M17/M20 exactly):

- [x] Operator one-time prep — session-verifiable state captured at M24 start
      (`~/.pypirc` intact mode 600; PyPI `docs-cli` at 1.6.5, 1.8.0 slot free;
      TestPyPI `docs-cli` squatter unchanged; TestPyPI
      `docs-cli-rehearsal` 1.8.0 slot free; twine 6.2.0 + build 1.5.0 ready).
- [x] Pre-publish prep — version verified `1.8.0`, CHANGELOG fold deferred to
      Phase 4, tree at the M24 setup commit `d9b4458`, quality + surface-parity
      gate green tree-wide (636 passed; wheel `29ac3ced…`, sdist `295ba009…`),
      fresh artefacts rebuilt, local-install smoke + the M21 + M23 headline
      contracts verified against the wheel.
- [x] TestPyPI rehearsal — uploaded as `docs-cli-rehearsal==1.8.0`
      (test.pypi.org/project/docs-cli-rehearsal/1.8.0/); throwaway-venv install
      from TestPyPI succeeded first try; M23 install-skill contracts passed
      against the served wheel; `docs --version` → `0.0.0+local` and the M21
      notice correctly did not fire (both known-expected under the rehearsal
      name — verified against the canonical local wheel instead). Rename
      reverted clean; canonical wheel `29ac3ced…` byte-identical to Phase 2.
      **GO.**
- [x] Real PyPI publish — `docs-cli==1.8.0` LIVE on PyPI; both artefacts
      twine-check PASS; upload PASS; chain-of-custody **bit-perfect** (PyPI-served
      wheel `29ac3ced…` **and sdist** `62a29285…` byte-identical to local
      Phase-4 build); throwaway-venv install from PyPI succeeded (`docs 1.8.0`);
      full smoke + the M21 + M23 headline contracts PASS against the PyPI-served
      wheel. Tag-target commit `1a01f74`.
- [x] Post-release — annotated `v1.8.0` tag at `1a01f74` pushed to `origin`;
      GitHub release live with notes sourced from `## 1.8.0`; **host skills
      refreshed** (`docs install-skill --force` → host `docs` byte-identical;
      workflow-skill sweep found no docs-cli drift); doc closeouts
      (plan/status/INDEX + fixture) landed; `docs archive` ran (M21 + M22 + M23
      pairs **and** the M24 milestone doc archived to `archive/2026-07-03/`; M24
      impl log + release-runbook + status stay `Lifecycle: active`). Token
      re-scope continues to roll forward as the M9 open follow-on.

Each ticks as the runbook's corresponding section completes.

## Decisions

- **D1 — Batched publish as 1.8.0 (2026-07-03).** M24 ships M21 + M22 + M23
  together as one public release, `docs-cli==1.8.0` — the batched shape
  (M17 = M14+M15 → 1.6.0; M9 = M6+M7+M8 → 1.3.0). The tree is already at 1.8.0
  (M23 Phase 7). Rationale: M22 is doc-only (no bump), M21's 1.7.0 never
  reached PyPI, and shipping the current `main` tree once is simpler than two
  sequential publishes.
- **D2 — Fold 1.7.0 into 1.8.0 in the CHANGELOG (operator decision,
  2026-07-03).** 1.7.0 is a PyPI-skipped version number. At Phase 4 the
  `## 1.7.0 — UNRELEASED` entries (M21) are merged up into the single dated
  `## 1.8.0 — <publish-date>` section and the 1.7.0 header is dropped. One
  published version → one CHANGELOG section. (Departs from the M19→M20 shape,
  where a single UNRELEASED section was simply dated; here two accrued
  sections collapse to one.)
- **D3 — "Author now, confirm at the gate" (operator decision, 2026-07-03).**
  M24 is set up (this milestone pair authored + active, status/plan updated)
  without executing the runbook. The runbook walk proceeds only after an
  explicit operator go-ahead, and pauses again for confirmation before every
  irreversible / outward-facing step (real PyPI upload, `main` push, `v1.8.0`
  tag, GitHub release). NOT the M20 "full-autonomous authorized up front"
  shape.
- **D4 — M23 OQ-1/OQ-2 confirmed as-shipped (operator decision, 2026-07-03).**
  OQ-1 (non-TTY → fall back to default dest, never refuse) and OQ-2 (a
  separate `${XDG_STATE_HOME}/docs-cli/install-skill.json` state file; M21's
  update-check cache frozen) stand exactly as M23 shipped them. The M23
  "confirm at branch review" flag is **cleared**. No code change, no re-bump —
  1.8.0 publishes as built.
- **D5 — Milestone-doc archival at closeout (M17/M20 Q2 precedent).** M21,
  M22, and M23 are LIVE at root awaiting a sweep; M24's Phase-5 closeout
  archives all three pairs + M24's own milestone doc to
  `archive/<publish-date>/`. The M24 impl log, release-runbook, and status doc
  stay `Lifecycle: active`.

## Testing / Quality Gate

No new code, so no new tests. The gate M24 enforces before upload:

- **pytest** green tree-wide (636 at M23 implementation-complete; the exact
  count recorded at the moment of the M24 run).
- **ruff check** / **ruff format --check** / **mypy** clean tree-wide.
- **`docs check docs/`** exit 0; **`docs index --root docs/ --dry-run`**
  idempotent; `docs/INDEX.md` byte-identical to
  `tests/fixtures/expected/docs-INDEX.md`.
- **Surface parity** — bundled `references/cli.md` + `convention.md`
  byte-identical to `docs/cli.md` + `docs/convention.md`; argparse `--help`
  strings match the shipped surface.
- **twine check dist/*** PASS on both wheel + sdist.
- **The M21 + M23 headline contracts** (see Success Criteria) PASS against
  the local canonical wheel, then the TestPyPI-served wheel, then the
  PyPI-served wheel.

## Success Criteria

M24 is complete when:

- `docs-cli==1.8.0` is installable from PyPI; a fresh venv `pip install
  docs-cli==1.8.0` → `docs --version` prints `docs 1.8.0`.
- Chain-of-custody bit-perfect: PyPI-served wheel **and** sdist sha256
  byte-identical to the local Phase-4 build.
- **M21 headline contracts** hold against the PyPI-served wheel: the
  update-check notice fires once/24h to STDERR (`docs: update available … —
  run: pip install -U docs-cli`), never alters exit code or stdout, is
  suppressed under `--quiet` / `--json` / `CI` / `DOCS_CLI_NO_UPDATE_CHECK` /
  `DO_NOT_TRACK`, shows on non-TTY, and degrades fail-silent (offline / timeout
  / non-200 / malformed JSON / corrupt cache).
- **M23 headline contracts** hold against the PyPI-served wheel:
  `install-skill --dest <d>` records the resolved path to
  `${XDG_STATE_HOME}/docs-cli/install-skill.json` (path only, never content);
  a non-TTY caller falls back to the default and exits 0 (never blocks on a
  prompt); the help/description read "agent skill" not "Claude Code skill"; and
  when a dest has been recorded the update notice appends the skill-refresh
  hint (`docs: refresh the agent skill at <dest> — run: docs install-skill
  --dest <dest> --force`) under the same suppression matrix + throttle, absent
  when no dest recorded.
- `docs check <tree>` exits 0 against the PyPI-served wheel; installed skill
  references carry no repo-relative `](../` links.
- The public GitHub repo carries the `v1.8.0` annotated tag + a GitHub release
  with notes sourced from the CHANGELOG `## 1.8.0` section.
- Doc closeouts landed: status/plan/INDEX finalised; the M21 + M22 + M23 pairs
  + the M24 milestone doc archived to `archive/<publish-date>/`.

## Milestone-completion summary

**M24 complete — `docs-cli==1.8.0` shipped to PyPI 2026-07-03.** The batched
publish of the post-1.6.5 train — **M21** (update-check notice) + **M22**
(doc-tree root-placement guidance) + **M23** (agent-aware install-skill +
recorded-dest skill-refresh hint) — as one public release (M17 batched
M14+M15; M9 batched M6+M7+M8). Driven under D3 ("author now, confirm at the
gate"): the operator authorized the irreversible PyPI upload + `main` push +
tag + release at the Phase-4 gate. **1.7.0 was skipped on PyPI** — its CHANGELOG
entries folded into the dated `## 1.8.0` section (D2).

- **PyPI** https://pypi.org/project/docs-cli/1.8.0/ · **GitHub release**
  https://github.com/ArtRichards/docs-cli/releases/tag/v1.8.0 · **TestPyPI
  rehearsal** https://test.pypi.org/project/docs-cli-rehearsal/1.8.0/
- **Published sha256 (chain-of-custody, BIT-PERFECT wheel AND sdist):** wheel
  `29ac3ced37843dd422cd10f6d6b1689124ca0f19eac8a2063322cda440374f70`; sdist
  `62a29285bf80326cfdba6154a757ddb33e91e0ad69c31b9a0c3861c50023a17b`. Sixth
  release running (M11 + M13 + M17 + M20 + M24).
- **Gate at publish:** 636 passed; ruff / format / mypy clean; `docs check
  docs/` exit 0; surface parity clean; both `twine check` PASS.
- **Contracts:** all M21 + M23 headline contracts hold against the PyPI-served
  wheel (see the impl log Phase 4).
- **Host skills refreshed:** `~/.claude/skills/docs` byte-identical to the
  published bundle; workflow-skill sweep found no docs-cli drift.
- **D4 cleared:** M23 OQ-1/OQ-2 confirmed as-shipped — 1.8.0 published as built,
  no re-bump.

Full per-phase record + deviations (carried to v1.9+) live in
[m24-pypi-publish-impl.md](../../m24-pypi-publish-impl.md).
