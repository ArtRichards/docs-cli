# M14 — Robustness + agent-native surface

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-05-29

Related:
- child-of: plan.md
- parent-of: m14-robustness-agent-native-impl.md
- pairs-with: agent-native-invocation.md
- pairs-with: cli.md
- pairs-with: status.md

## Overview

- Milestone: M14 (v1.6)
- Title: Robustness + agent-native surface
- Surface: hardening fixes to existing verbs + two new agent-facing
  affordances (`docs project set`, non-interactive `archive --cascade`)
  + agent-skill/packaging corrections. No publish — M14 builds 1.6.0
  locally; a separate publish milestone (M15) ships it, per the
  M12→M13 / M10→M11 / M8→M9 cadence.
- Status: Draft (scaffolded 2026-05-29 from the post-1.5.0 multi-agent
  code+docs review and the [agent-native-invocation.md](agent-native-invocation.md)
  proposal).

### Goal

The post-1.5.0 review (three Opus reviewers, 2026-05-29) surfaced one
latent correctness blocker, several agent-ergonomics gaps, and a set of
bundled-skill/packaging defects. M14 burns them down in one TDD cycle
and lands the highest-leverage subset of the agent-native proposal —
the items that are concrete CLI behavior, not harness wiring.

This milestone deliberately **defers** the broader agent-native surface
(global `--json`, `docs context`, `docs capabilities`,
`install-skill --with-hooks`, the MCP server) — see Decisions. Those
want their own milestone(s); M14 takes the parts with a clear contract
and immediate payoff.

### Scope — three threads

**Thread A — robustness (from the review; correctness first).**

- **A1 (blocker) — `docs mv` is not all-or-nothing.** `cli.py:3557-3570`
  does `old_path.replace(new_path)` *before* walking the tree to rewrite
  `Related:` edges; a single malformed sibling makes `walk()` raise
  *after* the move → dangling edges + INDEX never refreshed. Fix: port
  the validate-all-first pre-flight walk `archive` already has
  (`cli.py:3488-3492`) into `_cmd_mv`, before any move. Add the
  malformed-sibling test the `mv` suite is missing.
- **A2 — `docs new` cwd-fallback footgun.** `cli.py:3277` /
  `find_root` `cli.py:996-1012`: with no upward `.docs.toml` and no
  `--root`, `new` silently writes to cwd with default config (this
  misfired creating the agent-native doc at the repo root). Make `new`
  refuse like `touch`/`project rename` do via the strict resolver
  (`_resolve_touch_root` / `_find_root_strict`). Decide whether to
  extend strict resolution to `index`/`list`/`check` too (Open Q).
- **A3 — empty-segment slug.** `cli.py:3299-3306`: `docs new spec foo/`
  writes an invisible `foo/.md` (dotfile, skipped by every read verb).
  Reject empty final segment.
- **A4 — uncaught `OSError` post-mutation.** `_rewrite_referring_edges`
  (`cli.py:3696-3714`) and the `mv` rewrite loop only catch
  `MetadataError`/`VocabularyError`; an `OSError` mid-rewrite escapes as
  a traceback after the move. Widen to map `OSError` → clean exit 2,
  matching `_archive_one` (`cli.py:3505-3507`).
- **A5 — spec reconciliation (nits).** `cli.md:72` claims `atomic_write`
  is "fsync'd" — it isn't (`cli.py:584-592`). Either add `os.fsync`
  before `replace` or drop the claim. Tighten `_archive_one`'s
  atomicity docstring (`cli.py:3382-3399`).

**Thread B — agent-native surface (from agent-native-invocation.md).**

- **B1 — non-interactive `archive --cascade`** (proposal P0-1). The
  `--cascade` prompt (`cli.py:3427-3428`) stalls an autonomous agent.
  Establish the invariant *docs never prompts unless asked*; replace the
  prompt with pre-answerable flags: `--cascade` (take all one-hop
  `pairs-with`/`child-of`, no prompt), `--cascade-dry-run` (print the
  set, write nothing), `--cascade-only <glob>` (filtered subset);
  `--interactive` opts back into the prompt.
- **B2 — `docs project set <doc>... <new-project>`** (proposal §5E). The
  single-doc counterpart to `project rename`; closes the gap that forced
  recreating a doc to change its `Project:`. Atomic batch + one
  end-of-batch INDEX refresh; `normalise_project_name()` validation;
  archived docs read-only; **no `Related:`-edge rewrite** (no path
  change); `--dry-run`/`--quiet`/`--root`; a `--new-project` typo guard
  that refuses a project value new to the tree (with a did-you-mean)
  rather than prompting. Composes with `rename` (which already leaves
  non-matching-project docs untouched).

**Thread C — agent skill + packaging (from the review).**

- **C1 — broken bundled-reference links.**
  `src/docs_cli/skill/references/use-cases.md:5`
  (`../../../../docs/charter.md`) and `references/cli.md:318`
  (`../src/docs_cli/skill/SKILL.md`) are repo-relative and dangle once
  installed on a host. Repoint to host-resolvable siblings; keep the
  bundled-vs-`docs/` byte-identity invariant in mind (decide canonical).
- **C2 — `SKILL.md` table omits `--body-from`** (`SKILL.md:46`), the
  highest-value agent flag (atomic doc authoring in one call). Add it;
  also refresh the frontmatter `description` verb list (`SKILL.md:3` —
  add `project rename`, `install-skill`).
- **C3 — `test_a6` is a false-confidence test**
  (`tests/test_packaging.py:141-172`): it greps for the literal `"skill"`
  which only matches a pyproject *comment*, not a real directive.
  Replace with an assertion on the actual `packages` glob, or fold into
  the real guard `test_b3` (`tests/test_packaging.py:239`).

## Deliverables

- [ ] A1 `docs mv` validate-all-first; malformed-sibling test added.
- [ ] A2 `docs new` strict-root refusal (no silent cwd write).
- [ ] A3 empty-segment slug rejected.
- [ ] A4 `OSError` in mv/archive edge-rewrite → clean exit 2.
- [ ] A5 `atomic_write` fsync claim reconciled; archive docstring fixed.
- [ ] B1 `archive --cascade` non-interactive flag set; prompt removed
      (or behind `--interactive`); `cli.md` updated.
- [ ] B2 `docs project set` verb shipped + spec'd in `cli.md` + skill.
- [ ] C1 bundled reference links host-resolvable.
- [ ] C2 `--body-from` in SKILL table; frontmatter description refreshed.
- [ ] C3 `test_a6` replaced with a real package-data assertion.
- [ ] `pyproject.toml` `version` → `1.6.0`; `CHANGELOG.md`
      `## 1.6.0 — UNRELEASED` authored (publish-survival wording).
- [ ] `docs/cli.md` + `convention.md` reflect every behavior change;
      bundled skill refs resynced; INDEX + frozen snapshot in lockstep.
- [ ] Full suite GREEN; ruff / ruff format / mypy / `docs check` clean.

## Phase Checklist (10-phase TDD)

- [ ] 1. Define Contract — `cli.md` deltas for `project set`, the
      `--cascade` flag set, the `new` strict-refusal exit codes.
- [ ] 2. Write Tests (RED) — pin every A/B/C behavior, incl. the
      mv malformed-sibling atomicity test and the cascade-no-prompt test.
- [ ] 3. Create Fixtures — multi-project tree for `project set`; a tree
      with a malformed sibling for the mv pre-flight.
- [ ] 4. Run Tests (RED) — confirm the intended red baseline.
- [ ] 5. Update Interfaces — argparse: `project set`, `--cascade*`,
      strict-resolver wiring.
- [ ] 6. Implement Core — the pre-flight walk, `project set`, cascade
      set computation, slug/OSError guards.
- [ ] 7. Update Wrappers — `pyproject.toml` 1.6.0; CHANGELOG entry;
      skill refs resync.
- [ ] 8. Run Tests (GREEN) + quality gate.
- [ ] 9. Integrate — dogfood on this repo's `docs/` tree.
- [ ] 10. Quality, Docs, Refactor — closeout summaries; INDEX + snapshot
      lockstep; status/plan updated.

## Decisions

- **Version 1.6.0; publish is a separate milestone (M15).** Mirrors the
  M12→M13 cadence. M14 lands the bump + CHANGELOG inline (Phase 7/10)
  but does not touch PyPI.
- **Deferred to a later agent-native milestone (not M14):** global
  `--json` + `changed` across all verbs; `docs context`;
  `docs capabilities`; `install-skill --with-hooks` + SessionStart /
  PreToolUse / PostToolUse hooks; the MCP server; the
  "tree-as-memory" advisory `check` rules. Rationale: these are larger,
  some couple `docs` to a harness schema, and several depend on settling
  a shared `Result` JSON schema first — see
  [agent-native-invocation.md](agent-native-invocation.md) Layers 1–5.
- **`mv`-into-archive permissiveness (review N4) left as-is** — drift is
  surfaced by `docs check`; the spec frames archive as read-only by
  convention. Not in scope.
- **The 432→433 review finding was a false positive** — the M12 log is
  historically accurate (the count grew at the M12 simplify commit); no
  edit. Recorded so it isn't "re-fixed" later.

## Testing / Quality Gate

The standard tree-wide gate plus the new behavior tests:

```sh
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
.venv/bin/docs check docs/
.venv/bin/docs index --root docs/ --dry-run
```

Dogfood at Phase 9: exercise `docs project set` + non-interactive
`archive --cascade` on a copied fixture tree, and confirm `docs new`
refuses outside a root.

## Success Criteria

- [ ] `docs mv` is atomic: a malformed sibling aborts with exit 2 and
      leaves the source in place + INDEX untouched.
- [ ] `docs new` outside any `.docs.toml` root (no `--root`) refuses
      with exit 2; never writes to cwd.
- [ ] `docs project set <doc> <name>` reassigns one doc's project
      atomically; `--new-project` guards typos; archived docs untouched.
- [ ] `docs archive --cascade` runs without prompting; `--cascade-dry-run`
      previews the set.
- [ ] `docs install-skill` on a clean host produces bundled references
      whose internal links resolve.
- [ ] `pip`-relevant packaging guard actually fails if the skill glob
      breaks (C3).
- [ ] Full suite GREEN; quality gate clean tree-wide; `docs check` exit 0.

## OPEN QUESTIONS

- **Strict resolution scope (A2):** refuse only on `new`, or extend the
  strict resolver to `index`/`list`/`check` too? (Read verbs silently
  defaulting to cwd is less harmful but still surprising.) Recommend:
  `new` in M14; evaluate the read verbs as a fast-follow.
- **`--cascade` default (B1):** does bare `--cascade` taking *all*
  one-hop relations surprise anyone, or is `--cascade-dry-run`-first a
  sufficient guard? Recommend: take-all + loud footer summary.
- **Bundled-refs canonical source (C1):** are `docs/cli.md` /
  `convention.md` the source and the skill copies generated, or are they
  independently maintained? The link fix must not break the
  `_trees_byte_identical` no-op detection. Recommend: declare `docs/`
  canonical, generate the bundled copies, fix links in the generator.
- **Milestone size:** A+B+C is large (≈M12 scale). Split B2/`project set`
  into its own milestone if Step-1 planning judges the cycle too wide?
