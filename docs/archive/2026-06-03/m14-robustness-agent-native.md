# M14 — Robustness + autonomous archive

Lifecycle: archived
Role: milestone
Project: docs
Updated: 2026-06-03

Related:
- child-of: plan.md
- parent-of: archive/2026-06-03/m14-robustness-agent-native-impl.md
- pairs-with: archive/2026-06-03/m15-agent-native-authoring.md
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
- Status: **Implementation complete (2026-06-02)** — `docs-cli==1.6.0`
  built locally; PyPI publish is M17's. Scaffolded 2026-05-29 from the
  post-1.5.0 multi-agent code+docs review and the
  [agent-native-invocation.md](agent-native-invocation.md) proposal.

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

- [x] A1 `docs mv` validate-all-first; malformed-sibling test added.
- [x] A2 `docs new` strict-root refusal (no silent cwd write).
- [x] A3 empty-segment slug rejected.
- [x] A4 `OSError` in mv/archive edge-rewrite → clean exit 2.
- [x] A5 `atomic_write` gains `os.fsync` before the rename (operator
      decision 2026-06-02 — ADD fsync, the `cli.md` "fsync'd" claim
      STAYS and becomes true); `_archive_one` docstring tightened.
- [x] A6 the end-of-batch reindex threads the exclude predicate at
      **all four** mutating-verb call sites (operator decision
      2026-06-02 — `docs touch`, `docs archive`, `docs mv`,
      `docs project rename`); malformed-excluded-file atomicity test
      added for each. (Implementation also threads the predicate through
      `archive`'s `_rewrite_referring_edges` walk — the per-verb "every
      walk/reindex" reading.)
- [x] B1 `archive --cascade` non-interactive flag set (`--cascade` /
      `--cascade-dry-run` / `--cascade-only GLOB` / `--interactive`);
      the legacy prompt moves behind `--interactive`; the invariant
      *docs never prompts unless `--interactive`* established; `cli.md`
      updated.
- [x] C1 bundled reference links host-resolvable — **done by M16**
      (2026-06-02 verification). M16 rewrote the bundled references
      self-contained; the cited dangling links
      (`use-cases.md:5`, `references/cli.md:318`) no longer exist
      (`grep -rn '](\.\./' src/docs_cli/skill/` returns zero matches).
      M14 adds a GREEN regression guard
      (`test_bundled_skill_has_no_repo_relative_links`) only. C1's own
      OQ is answered below: `docs/` is canonical and the bundled copies
      are byte-identical mirrors maintained by `cp` and enforced by
      `tests/test_skill_refs.py` (NOT script-generated).
- [x] C3 `test_a6` (false-confidence pyproject-comment grep) removed;
      `test_b3_wheel_contains_cli_and_skill` strengthened to assert the
      built wheel carries real skill package-data so a broken
      `packages` glob actually fails.
- [x] `pyproject.toml` `version` → `1.6.0`; `CHANGELOG.md`
      `## 1.6.0 — UNRELEASED` section authored (publish-survival wording).
      M14 owns the bump + section; **M15 appends its authoring entries to
      the same 1.6.0 section** before M17 publishes. (Built locally; M17
      publishes.)
- [x] `docs/cli.md` + `convention.md` reflect every behavior change
      (authored Phase 1); bundled skill refs resynced byte-identical;
      INDEX + frozen snapshot in lockstep.
- [x] Full suite GREEN (458 passed); ruff / ruff format / mypy /
      `docs check` clean tree-wide.

## Phase Checklist (10-phase TDD)

- [x] 1. Define Contract — `cli.md` deltas for the `--cascade` flag set
      (+ `--cascade-dry-run` / `--cascade-only` / `--interactive` + the
      no-prompt invariant), the `new` strict-refusal exit codes + empty-
      segment slug, the four-site `touch`/`archive`/`mv`/`project rename`
      exclude semantics; `convention.md` §Exclusion reconciled; bundled
      refs resynced byte-identical; A5/A6 Decisions recorded.
- [x] 2. Write Tests (RED) — pinned every A/B/C behavior: the
      mv malformed-sibling atomicity tests, the cascade-no-prompt /
      dry-run / cascade-only tests, the four-site touch/archive/mv/project-
      rename excludes-reindex tests, the A5 fsync test, the A2/A3 new
      guards; migrated the 2 legacy cascade prompt tests to `--interactive`;
      C1 GREEN guard added; C3 false-confidence test removed + `test_b3`
      strengthened.
- [x] 3. Create Fixtures — `tests/fixtures/trees/mv-with-malformed/` for
      the mv pre-flight; the `[exclude]`-with-malformed trees for the four
      reindex tests are inline `tmp_path` helpers in the Phase-2 test files.
- [x] 4. Run Tests (RED) — confirmed the intended red baseline (454
      collected, 17 failed = exactly the new behavior set + the 2 migrated
      cascade tests, 437 passed). See the impl-log Phase-4 table.
- [x] 5. Update Interfaces — argparse: the `--cascade*` flag set
      (mutex group + `--cascade-dry-run` outside it), `_resolve_new_root`
      + `_cascade_set` declared.
- [x] 6. Implement Core — the mv pre-flight walk, cascade set
      computation, the four-verb exclude-predicate fix, slug/OSError/A5
      fsync guards. All 18 RED → GREEN.
- [x] 7. Update Wrappers — `pyproject.toml` 1.6.0; CHANGELOG section;
      packaging version-string lockstep (skill refs unchanged).
- [x] 8. Run Tests (GREEN) + quality gate — 458 passed; ruff / format /
      mypy clean tree-wide (incl. the mechanical M16 import-sort fix).
- [x] 9. Integrate — dogfood on throwaway copies; `docs check docs/`
      read-only on this repo's tree (exit 0).
- [x] 10. Quality, Docs, Refactor — closeout summaries; INDEX + snapshot
      lockstep; status/plan updated; cascade dead-branch removed.

## Decisions

- **A6 widened to four reindex sites (operator decision, 2026-06-02).**
  The exclude predicate is threaded into the end-of-batch
  `_refresh_index` for `docs touch`, `docs archive`, `docs mv`, AND
  `docs project rename` — not `touch` alone. Rationale: all four share
  the identical post-mutation reindex-walk shape; a malformed excluded
  file would non-atomically fail any of them after the verb had already
  stamped/moved/renamed on disk. No new `--exclude` flag is added to the
  mutating verbs (Step-1 RQ#8): each wires
  `compile_exclude_predicate(config, [])` so only the persistent
  `[exclude]` / `.docsignore` sources apply. The contract is written
  into `cli.md` (per-verb notes + the "Common: exclusion" intro) and
  `convention.md` §Exclusion; Phase-2 tests cover all four verbs.
- **A5 — ADD `os.fsync`, keep the "fsync'd" claim (operator decision,
  2026-06-02).** Rather than dropping the `cli.md` §archive "fsync'd"
  claim, `atomic_write` gains an `os.fsync` of the tmpfile (and its
  parent directory) before the rename, so the durability claim becomes
  true. The fsync **code** lands in Step 2 (Phase 6); Step 1 keeps the
  claim in the spec (now accurate-by-intent) and writes the RED test
  that pins *fsync-is-called* during an `atomic_write`-backed mutation.
  The `_archive_one` docstring is tightened for accuracy now. (This is
  NOT a "claim dropped" reconciliation — the claim stays.)
- **B1 cascade shape (operator decision, 2026-06-02).** Bare
  `--cascade` archives ALL one-hop `pairs-with`/`child-of` relations
  with NO prompt + a loud stderr footer naming the set;
  `--cascade-dry-run` previews and writes nothing (exit 0);
  `--cascade-only GLOB` archives the subset whose related-doc
  root-relative POSIX target path matches `GLOB` (compiled by the same
  matcher `compile_exclude_predicate` uses); `--interactive` restores
  the legacy `[y/N]` prompt and is the ONLY path that reads stdin.
  `--cascade`/`--cascade-only`/`--interactive` are mutually exclusive;
  `--cascade-dry-run` composes with `--cascade-only` but is rejected
  with `--interactive`. The invariant *docs never prompts unless
  `--interactive`* is established in the spec.
- **A2 strict resolution scope — `new` ONLY (operator decision,
  2026-06-02; answers the OQ below).** `docs new` refuses the
  cwd-as-root fallback like `touch` / `project rename` already do. The
  read verbs `index` / `list` / `check` KEEP the silent cwd-fallback
  (a wrong-tree read is recoverable; a write is not). The Invocation
  edit must not claim all verbs refuse.
- **C1 — done by M16; verification only (operator decision,
  2026-06-02).** The cited dangling bundled-reference links no longer
  exist (M16 rewrote the references self-contained;
  `tests/test_skill_refs.py` enforces byte-identity with `docs/`). M14
  adds a GREEN regression guard only. Canonical source: `docs/`; the
  bundled copies are byte-identical mirrors maintained by `cp`, NOT
  script-generated.
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

- [x] `docs mv` is atomic: a malformed sibling aborts with exit 2 and
      leaves the source in place + INDEX untouched.
- [x] `docs new` outside any `.docs.toml` root (no `--root`) refuses
      with exit 2; never writes to cwd.
- [x] `docs archive --cascade` runs without prompting; `--cascade-dry-run`
      previews the set.
- [x] `docs install-skill` on a clean host produces bundled references
      whose internal links resolve. (Satisfied by M16's self-contained
      references + the M14 GREEN guard
      `test_bundled_skill_has_no_repo_relative_links` — no repo-relative
      `../` links remain; `test_skill_refs.py` enforces byte-identity
      with `docs/`.)
- [x] `pip`-relevant packaging guard actually fails if the skill glob
      breaks (C3) — `test_b3_wheel_contains_cli_and_skill` asserts the
      built wheel carries real skill package-data.
- [x] Full suite GREEN (458 passed); quality gate clean tree-wide;
      `docs check` exit 0.
- [x] `docs touch` over a tree with a malformed *excluded* file stamps the
      dates *and* refreshes the INDEX cleanly (excluded file never indexed).

## OPEN QUESTIONS

All Step-1 OQs are RESOLVED (operator decisions 2026-06-02 — recorded in
Decisions above). Kept here for the audit trail:

- **Strict resolution scope (A2) — RESOLVED:** refuse on `new` ONLY;
  `index`/`list`/`check` keep the cwd-fallback. (Was: "evaluate the read
  verbs as a fast-follow.")
- **`--cascade` default (B1) — RESOLVED:** bare `--cascade` takes ALL
  one-hop relations, no prompt, loud stderr footer naming the set;
  `--cascade-dry-run` previews; `--interactive` restores the prompt.
- **Bundled-refs canonical source (C1) — RESOLVED:** `docs/` is
  canonical; the bundled copies are byte-identical mirrors maintained by
  `cp` and enforced by `tests/test_skill_refs.py` (NOT script-generated).
  M16 already fixed the dangling links; M14 adds a GREEN guard only.
- **Milestone size — resolved (2026-06-02):** the A6/B3/C4 widening pushed
  M14 past M12 scale, so the agent-native authoring set was carved into
  **M15** (see Decisions). The `docs stamp` verb-shape and `--body-from`
  detector open questions moved with it to the M15 doc.
