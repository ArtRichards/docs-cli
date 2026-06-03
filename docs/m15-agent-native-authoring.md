# M15 — Agent-native doc authoring (v1.6.0)

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-06-03

Related:
- child-of: plan.md
- parent-of: m15-agent-native-authoring-impl.md
- pairs-with: m14-robustness-agent-native.md
- pairs-with: agent-native-invocation.md
- pairs-with: cli.md
- pairs-with: status.md

## Overview

- Milestone: M15 (v1.6.0, part 2 of 2)
- Title: Agent-native doc authoring
- Surface: the agent-native *authoring* set carved out of M14 — a new
  `docs project set` verb (B2), a new single-file `docs stamp`
  write-then-stamp verb (B3), a fix to the `--body-from` refusal heuristic
  so it detects real frontmatter rather than any `Label:` line (C4), and
  the bundled-skill / `cli.md` docs for all of it (C2). No publish — M15
  builds on M14's local 1.6.0; the publish milestone (**M17**) ships both.
- Progress: Draft (carved from M14 on 2026-06-02 — see M14 Decisions).

### Goal

An agent's natural authoring move is to *write the whole document* with
ordinary tools and then bring it under convention. Today `docs new
--body-from` owns the frontmatter and fights bodies that contain
`Label:`-shaped prose, and there is no single-file adopt path. M15 closes
that gap: `docs stamp` stamps metadata onto a file the agent already wrote,
the `--body-from` detector stops refusing legitimate prose, and `docs
project set` lets an agent reassign one doc's `Project:` without recreating
it. Together they make doc authoring a first-class agent operation.

This milestone was carved out of M14 (2026-06-02, operator-confirmed) when
the post-1.5.0 contract was widened past M12 scale. M14 ships the
robustness/atomicity hardening (Thread A) + the autonomous-archive
affordance (B1) + packaging hygiene (C1/C3); M15 ships the authoring
surface. **M15 depends on M14** (shared `cli.py` mutating-verb surface,
the `--body-from` scaffold path, the 1.6.0 CHANGELOG section M14 opens) and
should be implemented after it. Both land 1.6.0 locally; **M17** publishes.

### Scope — the authoring set

- **B2 — `docs project set <doc>... <new-project>`** (proposal §5E). The
  single-doc counterpart to `project rename`; closes the gap that forced
  recreating a doc to change its `Project:`. Atomic batch + one
  end-of-batch INDEX refresh; `normalise_project_name()` validation;
  archived docs read-only; **no `Related:`-edge rewrite** (no path
  change); `--dry-run`/`--quiet`/`--root`; a `--new-project` typo guard
  that refuses a project value new to the tree (with a did-you-mean)
  rather than prompting. Composes with `rename` (which already leaves
  non-matching-project docs untouched).
- **B3 — single-file write-then-stamp (`docs stamp <file>`).** The friction
  the M16 bundled-skill dogfood hit: an agent's natural move is to *write
  the whole document* with ordinary tools, then bring it under convention —
  but `docs new --body-from` owns the frontmatter and fights bodies that
  contain `Label:`-shaped prose (see C4). `docs migrate` already
  infers/inserts a metadata block, but only tree-wide; the gap is the
  single file. Add `docs stamp <file>...` (alias/extension of `migrate`):
  infer `# H1` → title, take `--role`/`--project` (else fall back to
  `.docs.toml`), insert a valid metadata block on top, idempotently
  (re-stamping a doc that already has a block is a no-op bar an `Updated:`
  refresh). Removes the body-content restriction *class* rather than
  tuning the heuristic. Verb name + migrate-vs-new-verb shape is an Open Q.
- **C4 — `--body-from` refuses real prose, not just frontmatter.** The
  OQ-E heuristic (`cli.py:3336-3347`) rejects a body if *any* of its first
  20 lines matches `^[A-Z][A-Za-z-]+:\s` — so a legitimate spec/test-matrix
  body line like `Reason: …` or `Plan: …` is refused (this is exactly the
  dogfood failure: a test-matrix body starting `## Risk level` was rejected
  on its `Reason:` line). Replace the any-`Label:` match with detection of
  an *actual* metadata block: a leading `---` YAML fence, or a contiguous
  run carrying the required-field cluster (`Lifecycle`/`Role`/`Updated`)
  at/near the top (after an optional `# H1`). Preserves the footgun guard
  (a whole doc-with-frontmatter pasted as a body still refuses) while
  letting prose through. NB: this flips the pinned `edge-case-keyword.md`
  expectation in `tests/test_body_from.py` (the `Plan:` body now passes) —
  update that fixture/assertion as part of the change.
- **C2 — bundled-skill + `cli.md` docs for the authoring surface.**
  Document `--body-from` (corrected behavior), `docs project set`, and
  `docs stamp` in `SKILL.md`'s verb table (`SKILL.md:46`) and in `cli.md`;
  refresh the `SKILL.md` frontmatter `description` verb list (`SKILL.md:3`
  — add `project set`, `stamp`, `project rename`, `install-skill`). Keep
  the bundled-vs-`docs/` byte-identity invariant (`tests/test_skill_refs.py`).

## Deliverables

- [ ] B2 `docs project set` verb shipped + spec'd in `cli.md` + skill.
- [ ] B3 single-file `docs stamp <file>` (write-then-stamp) shipped +
      spec'd in `cli.md` + skill; idempotent re-stamp.
- [ ] C4 `--body-from` refusal detects a real metadata block (`---` fence
      or required-field cluster), not any `Label:` line; the
      `edge-case-keyword` expectation flipped.
- [ ] C2 `--body-from`/`project set`/`stamp` documented in SKILL table +
      `cli.md`; frontmatter verb list refreshed; skill refs byte-identical.
- [ ] `CHANGELOG.md`: append M15's authoring entries to the
      `## 1.6.0 — UNRELEASED` section M14 opened.
- [ ] `docs/cli.md` + `convention.md` reflect every behavior change;
      bundled skill refs resynced; INDEX + frozen snapshot in lockstep.
- [ ] Full suite GREEN; ruff / ruff format / mypy / `docs check` clean.

## Phase Checklist (10-phase TDD)

- [x] 1. Define Contract — `cli.md` deltas for `project set`, `stamp`, and
      the corrected `--body-from` refusal exit codes. (2026-06-03; bundled
      ref resynced byte-identical.)
- [ ] 2. Write Tests (RED) — `project set` atomic batch + typo guard;
      `stamp` insert + idempotent re-stamp; `--body-from` real-frontmatter
      cases incl. the `edge-case-keyword` flip and a `Reason:`-in-body pass.
- [ ] 3. Create Fixtures — multi-project tree for `project set`; a raw
      no-frontmatter file + an already-stamped file for `stamp`; prose and
      real-frontmatter bodies for `--body-from`.
- [ ] 4. Run Tests (RED) — confirm the intended red baseline.
- [ ] 5. Update Interfaces — argparse: `project set`, `stamp`
      (or `migrate`'s single-file path), the `--body-from` detector hook.
- [ ] 6. Implement Core — `project set`, `stamp`, the `--body-from` block
      detector.
- [ ] 7. Update Wrappers — CHANGELOG 1.6.0 authoring entries; `cli.md` +
      SKILL.md + skill refs resync.
- [ ] 8. Run Tests (GREEN) + quality gate.
- [ ] 9. Integrate — dogfood `stamp` + `project set` + `--body-from` on a
      copied fixture tree (and ideally on this repo's own `docs/`).
- [ ] 10. Quality, Docs, Refactor — closeout summaries; INDEX + snapshot
      lockstep; status/plan updated.

## Decisions

- **Carved from M14 (2026-06-02, operator-confirmed).** M14 outgrew M12
  scale after the A6/B3/C4 widening; the authoring set (B2/B3/C4/C2) is
  M15. See [m14-robustness-agent-native.md](m14-robustness-agent-native.md)
  Decisions for the full split rationale and monotonic numbering
  (M14 → M15 → M16 skill (done) → M17 publish).
- **Depends on M14.** Implement after M14: M15 shares the mutating-verb
  surface M14 hardens, and appends to the `## 1.6.0 — UNRELEASED`
  CHANGELOG section M14 opens. No publish here — M17 ships both.

## Testing / Quality Gate

The standard tree-wide gate plus the new behavior tests:

```sh
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
.venv/bin/docs check docs/
.venv/bin/docs index --root docs/ --dry-run
```

Dogfood at Phase 9: `docs stamp` a raw file under a copied tree and confirm
the metadata block + idempotent re-stamp; `docs project set` one doc and
confirm the atomic batch + typo guard; `docs new --body-from` a body whose
prose contains `Reason:`/`Plan:` lines and confirm it is accepted while a
whole doc-with-frontmatter body is still refused.

## Success Criteria

- [ ] `docs project set <doc> <name>` reassigns one doc's project
      atomically; `--new-project` guards typos; archived docs untouched.
- [ ] `docs stamp <raw.md>` inserts a valid metadata block (title from H1,
      role/project from flags or `.docs.toml`); re-running is a no-op bar
      `Updated:`.
- [ ] `docs new --body-from` accepts a body whose prose contains `Reason:`/
      `Plan:` lines, yet still refuses a whole doc-with-frontmatter body;
      the `edge-case-keyword` fixture expectation is flipped.
- [ ] SKILL table + `cli.md` document `--body-from`/`project set`/`stamp`;
      bundled skill refs byte-identical (`tests/test_skill_refs.py` GREEN).
- [ ] Full suite GREEN; quality gate clean tree-wide; `docs check` exit 0.

## OPEN QUESTIONS

- **`docs stamp` shape (B3):** a new top-level `docs stamp <file>` verb, or
  teach `docs migrate` to accept a single file (and alias `stamp` to it)?
  Recommend: extend `migrate`'s single-file path and expose `docs stamp` as
  the agent-facing name. How is metadata supplied — flags only, or infer
  `role`/`project` defaults from `.docs.toml`? Recommend: `--role`/`--project`
  flags, default `role: notes`, project from config.
- **`--body-from` detector boundary (C4):** is "a contiguous
  `Lifecycle`/`Role`/`Updated` cluster at/near the top" the right signal,
  or should it require all three? A body could legitimately open with a
  single `Updated:` prose line. Recommend: require the *cluster* (≥2 of the
  required fields adjacent) or a `---` fence; pin the boundary in tests.
- **C2 canonical source:** are `docs/cli.md` / `convention.md` the source
  and the skill copies generated, or independently maintained? The doc
  additions must not break `_trees_byte_identical`. Recommend: inherit
  M14's C1 decision (declare `docs/` canonical).
