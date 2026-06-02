# M14 — Robustness + autonomous archive

Lifecycle: draft
Role: milestone
Project: docs
Updated: 2026-06-02

Related:
- child-of: plan.md
- parent-of: m14-robustness-agent-native-impl.md
- pairs-with: m15-agent-native-authoring.md
- pairs-with: agent-native-invocation.md
- pairs-with: cli.md
- pairs-with: status.md

## Overview

- Milestone: M14 (v1.6.0, part 1 of 2)
- Title: Robustness + autonomous archive
- Surface: correctness/atomicity hardening of existing verbs
  (`mv`, `new`, `touch`, edge-rewrite) + one autonomous-agent affordance
  (non-interactive `archive --cascade`) + bundled-skill/packaging
  corrections. The agent-native *authoring* set (`docs project set`,
  `docs stamp`, the `--body-from` detector) split out to **M15** once
  this milestone outgrew M12 scale. No publish — M14 + M15 build 1.6.0
  locally; the publish milestone (**M17**) ships it, per the
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

**Split (2026-06-02, operator-confirmed):** when the post-1.5.0 contract
was widened with A6/B3/C4, M14 outgrew a single TDD cycle. The
agent-native *authoring* set — B2 `docs project set`, B3 `docs stamp`,
C4 the `--body-from` detector, plus their skill/cli docs (C2) — moved to
**M15 — Agent-native doc authoring**. M14 keeps the correctness/atomicity
hardening (Thread A), the autonomous-archive affordance (B1), and the
packaging hygiene (C1, C3). Both land 1.6.0 locally; **M17** publishes.

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
- **A6 — `docs touch` reindex ignores excludes (same family as A1/A4).**
  `_cmd_touch` (`cli.py:3648`) calls `_refresh_index(root, config)` with
  no predicate, so the end-of-batch reindex walks the *whole* tree —
  including `[exclude]`-d files. The dates are written first, so a single
  malformed excluded file (e.g. a bundled plugin `README.md`) makes the
  post-mutation walk raise: dates land but the INDEX refresh fails →
  partial, non-atomic. `_refresh_index` already accepts a `predicate`
  and `_cmd_index` (`cli.py:3248`) builds one via
  `compile_exclude_predicate`; thread it into `touch` too. Add a test:
  `touch` over a tree whose `[exclude]` set holds a malformed file leaves
  that file out of the INDEX and the refresh succeeds. (Surfaced by the
  M16 bundled-skill dogfood — see impl-log provenance.)

**Thread B — autonomous archive (from agent-native-invocation.md).**

- **B1 — non-interactive `archive --cascade`** (proposal P0-1). The
  `--cascade` prompt (`cli.py:3427-3428`) stalls an autonomous agent.
  Establish the invariant *docs never prompts unless asked*; replace the
  prompt with pre-answerable flags: `--cascade` (take all one-hop
  `pairs-with`/`child-of`, no prompt), `--cascade-dry-run` (print the
  set, write nothing), `--cascade-only <glob>` (filtered subset);
  `--interactive` opts back into the prompt.

> B2 `docs project set` and B3 `docs stamp` moved to **M15** — see the
> split note under Goal.

**Thread C — bundled skill + packaging (from the review).**

- **C1 — broken bundled-reference links.**
  `src/docs_cli/skill/references/use-cases.md:5`
  (`../../../../docs/charter.md`) and `references/cli.md:318`
  (`../src/docs_cli/skill/SKILL.md`) are repo-relative and dangle once
  installed on a host. Repoint to host-resolvable siblings; keep the
  bundled-vs-`docs/` byte-identity invariant in mind (decide canonical).
- **C3 — `test_a6` is a false-confidence test**
  (`tests/test_packaging.py:141-172`): it greps for the literal `"skill"`
  which only matches a pyproject *comment*, not a real directive.
  Replace with an assertion on the actual `packages` glob, or fold into
  the real guard `test_b3` (`tests/test_packaging.py:239`).

> C2 (`--body-from` in the SKILL table + frontmatter verb list) and C4
> (the `--body-from` real-frontmatter detector) moved to **M15** — they
> belong with the authoring surface they document and fix.

## Deliverables

- [ ] A1 `docs mv` validate-all-first; malformed-sibling test added.
- [ ] A2 `docs new` strict-root refusal (no silent cwd write).
- [ ] A3 empty-segment slug rejected.
- [ ] A4 `OSError` in mv/archive edge-rewrite → clean exit 2.
- [ ] A5 `atomic_write` fsync claim reconciled; archive docstring fixed.
- [ ] A6 `docs touch` reindex threads the exclude predicate; malformed-
      excluded-file atomicity test added.
- [ ] B1 `archive --cascade` non-interactive flag set; prompt removed
      (or behind `--interactive`); `cli.md` updated.
- [ ] C1 bundled reference links host-resolvable.
- [ ] C3 `test_a6` replaced with a real package-data assertion.
- [ ] `pyproject.toml` `version` → `1.6.0`; `CHANGELOG.md`
      `## 1.6.0 — UNRELEASED` section authored (publish-survival wording).
      M14 owns the bump + section; **M15 appends its authoring entries to
      the same 1.6.0 section** before M17 publishes.
- [ ] `docs/cli.md` + `convention.md` reflect every behavior change;
      bundled skill refs resynced; INDEX + frozen snapshot in lockstep.
- [ ] Full suite GREEN; ruff / ruff format / mypy / `docs check` clean.

## Phase Checklist (10-phase TDD)

- [ ] 1. Define Contract — `cli.md` deltas for the `--cascade` flag set,
      the `new` strict-refusal exit codes, the `touch` exclude semantics.
- [ ] 2. Write Tests (RED) — pin every A/B/C behavior, incl. the
      mv malformed-sibling atomicity test, the cascade-no-prompt test, and
      the touch-excludes reindex test.
- [ ] 3. Create Fixtures — a tree with a malformed sibling for the mv
      pre-flight; a tree whose `[exclude]` set holds a malformed file for
      the touch reindex.
- [ ] 4. Run Tests (RED) — confirm the intended red baseline.
- [ ] 5. Update Interfaces — argparse: the `--cascade*` flag set,
      strict-resolver wiring for `new`.
- [ ] 6. Implement Core — the mv pre-flight walk, cascade set
      computation, the touch exclude-predicate fix, slug/OSError guards.
- [ ] 7. Update Wrappers — `pyproject.toml` 1.6.0; CHANGELOG entry;
      skill refs resync.
- [ ] 8. Run Tests (GREEN) + quality gate.
- [ ] 9. Integrate — dogfood on this repo's `docs/` tree.
- [ ] 10. Quality, Docs, Refactor — closeout summaries; INDEX + snapshot
      lockstep; status/plan updated.

## Decisions

- **Version 1.6.0; publish is a separate milestone (M17).** Mirrors the
  M12→M13 cadence. M14 lands the bump + CHANGELOG section inline
  (Phase 7/10) but does not touch PyPI; M15 appends to the same section.
- **M14 split into M14 + M15 (2026-06-02, operator-confirmed).** The
  A6/B3/C4 widening pushed the contract past M12 scale. The agent-native
  authoring set (B2 `project set`, B3 `stamp`, C4 `--body-from` detector,
  C2 docs) carved into **M15 — Agent-native doc authoring**; M14 keeps
  Thread A + B1 + C1/C3. Monotonic numbering: M14 → M15 → (M16 skill,
  already done) → M17 publish.
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

Dogfood at Phase 9: exercise non-interactive `archive --cascade` on a
copied fixture tree, confirm `docs new` refuses outside a root, and
confirm `docs touch` over a tree with a malformed excluded file stamps
dates *and* refreshes the INDEX cleanly.

## Success Criteria

- [ ] `docs mv` is atomic: a malformed sibling aborts with exit 2 and
      leaves the source in place + INDEX untouched.
- [ ] `docs new` outside any `.docs.toml` root (no `--root`) refuses
      with exit 2; never writes to cwd.
- [ ] `docs archive --cascade` runs without prompting; `--cascade-dry-run`
      previews the set.
- [ ] `docs install-skill` on a clean host produces bundled references
      whose internal links resolve.
- [ ] `pip`-relevant packaging guard actually fails if the skill glob
      breaks (C3).
- [ ] Full suite GREEN; quality gate clean tree-wide; `docs check` exit 0.
- [ ] `docs touch` over a tree with a malformed *excluded* file stamps the
      dates *and* refreshes the INDEX cleanly (excluded file never indexed).

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
- **Milestone size — resolved (2026-06-02):** the A6/B3/C4 widening pushed
  M14 past M12 scale, so the agent-native authoring set was carved into
  **M15** (see Decisions). The `docs stamp` verb-shape and `--body-from`
  detector open questions moved with it to the M15 doc.
