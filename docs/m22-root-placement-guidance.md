# M22 — Doc-tree root placement guidance (project ≠ directory)

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-06-24

Related:
- parent-of: m22-root-placement-guidance-impl.md
- child-of: plan.md
- implements: charter.md
- pairs-with: convention.md

## Overview

- Milestone: M22
- Title: Doc-tree root placement guidance (project ≠ directory)
- Surface: documentation-only — the docs convention spec (`docs/convention.md`) and the bundled docs skill (`src/docs_cli/skill/SKILL.md` plus the byte-identical `references/convention.md`). No CLI behavior, no new verb or flag.
- Progress: Planned   (prose — Lifecycle: in the metadata block is the controlled vocab)

### Goal

Teach authors and agents where to put `.docs.toml` so a single project's docs are not needlessly nested beneath a parent root. Make explicit that `Project:` is a metadata slug, not a directory, and that because `Related:` paths are root-relative a redundant parent root prefixes every intra-project sibling reference. Default a single project's docs root to the project's own directory; reserve per-project subdirectories under one shared root for genuinely multi-project trees.

### Background / motivation

Observed agent behavior (the motivating report): create `.docs.toml` at a top-level parent (e.g. `specs/`), create a single project subdirectory, `docs project set` it as the default project, then author docs into the subdir. Because `Related:` paths are root-relative (`cli.py` `_root_relative`), every intra-project sibling edge then carries a redundant `<subdir>/` prefix, and the parent root wraps exactly one project. This repo's own `docs/` tree already models the clean shape (`.docs.toml` at `docs/`, `Project: docs`, files flat, refs like `pairs-with: cli.md`), and the M3 resolved question (INDEX groups by `Project`, not directory — metadata-driven) is direct supporting precedent.

### Requirements

- `docs/convention.md` §Subdirectories gains a "project ≠ directory / where to put `.docs.toml`" clarification covering: project-is-metadata; root-relative refs ⇒ redundant prefix when a lone project is nested; the single-project default (root = project dir, flat, clean refs); the multi-project case (one root + `Project:` metadata; per-project subdirs optional); and an explicit "do not nest a lone project under a parent root."
- `src/docs_cli/skill/references/convention.md` updated byte-identically (parity gate; `tests/test_skill_refs.py`).
- `SKILL.md` gains a concise "Where to put `.docs.toml`" note pointing at convention.md §Subdirectories, respecting SKILL.md invariants (<= 500 lines, names no non-existent verbs, relative links resolve, no parent-relative links).
- A pinning test (M16 precedent — `tests/test_skill_quality_artifacts.py`) asserts the guidance phrases exist in both surfaces, written RED before the edits.
- No CLI/code change; no version bump (M21 owns the 1.7.0 build). CHANGELOG staged under `## 1.7.0 — UNRELEASED` as a Documentation entry (see Decisions OQ-1).

### Deliverables

- [x] Contract: exact guidance claims + pin-phrases (Phase 1)
- [x] RED test: `tests/test_skill_root_placement.py` (Phase 2)
- [x] convention.md guidance + byte-identical references mirror (Phase 6)
- [x] SKILL.md "Where to put .docs.toml" note (Phase 7)
- [x] GREEN suite + parity (Phase 8)
- [x] Dogfood: `docs check docs/` exit 0; layout sanity (Phase 9)
- [x] CHANGELOG entry + completion summaries (Phase 10)

## Current State Analysis

- Existing code/docs: convention.md §Subdirectories says the tree is directory-agnostic and subdirs are free-form/opaque, but never states project ≠ directory nor warns about the redundant-prefix consequence of nesting a lone project. SKILL.md's bootstrap bullet says "touch .docs.toml at the intended root" with no guidance on choosing that root.
- Missing: the explicit placement default + the project-is-metadata clarification + the root-relative-prefix consequence.
- Known issues: agents produce the nested-parent anti-pattern in real use (the motivating report for this milestone).

## TDD Implementation Plan

Phases follow the canonical 10-phase TDD methodology. Documentation-only — several phases are light or repurposed (M16 precedent).

### Phase 1: Define Contract
- Objective: freeze the guidance claims + the exact pin-phrases the test asserts; resolve the CHANGELOG-handling decision.
- Files: this milestone doc (Decisions).
- Exit: pin-phrases enumerated; OQ-1 resolved.

### Phase 2: Write Tests (RED)
- Objective: `tests/test_skill_root_placement.py` asserting the pin-phrases in SKILL.md + convention.md (both copies) and a parity assertion.
- Files: `tests/test_skill_root_placement.py`.
- Exit: test imports cleanly; fails because the guidance phrases are absent.

### Phase 3: Create Data/Fixtures
- Objective: none — no fixtures needed.
- Files: —.
- Exit: N/A recorded.

### Phase 4: Run Tests (RED Baseline)
- Objective: capture the RED baseline verbatim.
- Files: —.
- Exit: failures trace to absent guidance, not misconfiguration.

### Phase 5: Update Base Interfaces
- Objective: no code interfaces; repurposed to finalize the exact guidance wording draft.
- Files: impl log (wording draft).
- Exit: wording drafted and reviewed.

### Phase 6: Implement Offline/Core Path
- Objective: add the convention.md §Subdirectories guidance; mirror byte-identically to references/convention.md; bump convention.md Updated via `docs touch`, then re-sync the mirror.
- Files: `docs/convention.md`, `src/docs_cli/skill/references/convention.md`.
- Exit: convention pin-phrases present; parity holds.

### Phase 7: Update Tool/Wrapper Layer
- Objective: add the SKILL.md "Where to put .docs.toml" note (the user-facing surface layer).
- Files: `src/docs_cli/skill/SKILL.md`.
- Exit: SKILL pin-phrases present; SKILL.md invariants hold.

### Phase 8: Run Tests (GREEN)
- Objective: full suite green including the new test + the parity test; ruff/mypy clean.
- Files: —.
- Exit: all green.

### Phase 9: Implement Online/Integration
- Objective: no online surface — dogfood. `docs check docs/` exit 0; read the rendered guidance for clarity; optionally demonstrate recommended vs anti-pattern layout in a throwaway tree.
- Files: —.
- Exit: dogfood pass recorded with notes.

### Phase 10: Quality, Docs, Refactor
- Objective: full gate; CHANGELOG `## 1.7.0 — UNRELEASED` Documentation entry; surface-parity reconciliation; completion summaries on both docs.
- Files: `CHANGELOG.md`, both milestone docs.
- Exit: gate green; ready to archive.

## Phase Checklist

- [x] Phase 1 — Define Contract
- [x] Phase 2 — Write Tests (RED)
- [x] Phase 3 — Create Data/Fixtures
- [x] Phase 4 — Run Tests (RED Baseline)
- [x] Phase 5 — Update Base Interfaces
- [x] Phase 6 — Implement Offline/Core Path
- [x] Phase 7 — Update Tool/Wrapper Layer
- [x] Phase 8 — Run Tests (GREEN)
- [x] Phase 9 — Implement Online/Integration
- [x] Phase 10 — Quality, Docs, Refactor

## Decisions

- Documentation-only, M16-shaped: no CLI/code change, no new verb or flag.
- Surfaces change in lockstep (the plan.md "Ongoing conventions" surface-parity gate); `references/convention.md` stays byte-identical to `docs/convention.md`.
- OQ-1 (CHANGELOG handling): stage M22 under a new `## 1.7.0 — UNRELEASED` CHANGELOG section as a Documentation entry; do NOT bump the pyproject version (M21 owns the actual 1.7.0 build, and the version is sourced from `importlib.metadata`). Recommended default; confirm at Phase 10.
- Out of scope: the matching root-placement note in the `project-foundation` skill (lives in the `agent-playbook-suite` repo, its own release cycle) — companion follow-on, tracked separately (related to the already-logged workflow-skill drift-lint follow-on).

## Success Criteria

- convention.md + SKILL.md carry the placement guidance; the bundled references mirror is byte-identical.
- New pinning test GREEN; full suite GREEN; ruff + mypy clean; `docs check docs/` exit 0.
- No CLI surface change; no version bump.

## Milestone-completion summary

**M22 — Doc-tree root placement guidance (project ≠ directory)** is
implementation-complete (2026-06-24), all ten TDD phases done. A
documentation-only milestone (M16-shaped): no CLI surface, no new verb/flag,
no version bump.

**What shipped (in-repo):**
- `docs/convention.md` §Subdirectories — new `### Where to put .docs.toml
  (project ≠ directory)` subsection: project is a metadata field not a
  directory; root-relative `Related:` ⇒ redundant `<subdir>/` prefix when a
  lone project is nested; single-project default (root = project dir, flat,
  clean refs); multi-project (one root + `Project:` metadata, subdirs
  optional); explicit "don't nest a lone project under a parent root."
- `src/docs_cli/skill/references/convention.md` — byte-identical mirror
  (parity gate, `tests/test_skill_refs.py`).
- `src/docs_cli/skill/SKILL.md` — concise "Where to put `.docs.toml`" note
  pointing at convention.md §Subdirectories.
- `tests/test_skill_root_placement.py` — 3 pinning tests (written RED first).
- `tests/fixtures/expected/docs-INDEX.md` — dogfood-snapshot refresh for the
  added M22 pair.
- `CHANGELOG.md` — `## 1.7.0 — UNRELEASED` Documentation entry.

**Verification:** full suite 543 GREEN; ruff/format/mypy clean; `docs check
docs/` exit 0; surface-parity (convention) byte-identical. Phase-9 dogfood
empirically reproduced the redundant-prefix consequence in throwaway trees
(anti-pattern clean sibling ref → exit 2 broken-ref, needs `demo/` prefix;
recommended root-at-project → exit 0).

**Out of scope (companion follow-on):** the matching root-placement note in
the `project-foundation` skill lives in the `agent-playbook-suite` repo (its
own release cycle); tracked alongside the workflow-skill drift-lint follow-on.

**Ships to users** at the next PyPI publish (the bundled skill rides the
wheel) — folds into the M21 → publish train; M22 does not publish on its own.
