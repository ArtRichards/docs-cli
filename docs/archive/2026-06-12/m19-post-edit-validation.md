# M19 — Post-edit validation ergonomics (touch --check + configurable stale window)

Lifecycle: archived
Role: milestone
Project: docs
Updated: 2026-06-12

Related:
- child-of: plan.md
- parent-of: archive/2026-06-12/m19-post-edit-validation-impl.md
- pairs-with: archive/2026-06-12/m19-post-edit-validation-impl.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: status.md

## Overview

- Milestone: M19 (v1.6.5)
- Title: Post-edit validation ergonomics (touch --check + configurable
  stale window)
- Surface: two operator-ergonomics features on the post-edit loop plus one
  cosmetic help-string fix. (a) **`docs touch --check [--stale N]`** — fold
  the existing `docs check` machinery into `docs touch` so the common
  three-command post-edit workflow (`docs touch <files>` → `docs index .`
  → `docs check . --stale 14`) collapses to a single invocation; (b)
  **configurable per-tree stale window** — a `.docs.toml [check] stale_days =
  N` default that bare `docs check` and (a)'s combined `touch --check` path
  honour, with an explicit CLI `--stale` overriding it (Q6: the key is
  scoped to **check** semantics — it does NOT change `docs list --stale`,
  which stays an explicit filter); (c)
  the cosmetic `docs new --body-from` argparse help-string fix (closes the
  rolled-forward follow-on). Local build only — ships as **v1.6.5**; the
  PyPI publish is a later operator-driven milestone (the M12→M13,
  M14+M15→M17 pattern).
- Progress: **Implementation-complete (2026-06-12).** Scaffolded 2026-06-12
  from the status.md "Single-step 'update metadata + validate' loop +
  configurable stale window" follow-on (operator feedback 2026-06-12,
  retargeted from v1.7 to v1.6.5). All ten TDD phases done across two steps
  (Step 1 — Contract + RED baseline on `m19/phases-1-4`; Step 2 — implement &
  ship on `m19/phases-5-10`); full suite 533/533 GREEN, gate clean,
  `docs --version` → `docs 1.6.5` (built locally; publish is a later
  operator-driven milestone). Depends on nothing; no new verb (a flag on an
  existing verb + a config key + a help string). Stays LIVE at root; lifecycle
  `draft`. M18 (archive edge integrity) is the only other live milestone and
  is independent.

### Goal

The common post-edit workflow an agent runs after changing a doc body is
three commands:

```sh
docs touch <files>        # bump Updated:
docs index .              # regenerate INDEX.md
docs check . --stale 14   # validate the tree
```

Two papercuts make this clumsier than it should be, and the operator
(2026-06-12) asked for both fixed:

1. **The loop is three steps when it could be one.** `docs touch` already
   runs the end-of-batch INDEX refresh (M10 — OQ-C), so the explicit
   `docs index .` is *already* redundant — but nothing on the surface says
   so, and agent workflows run it anyway. The real gap is that **validation
   is not bundled**: there is no way to touch-and-check in one invocation.
   M19 adds `docs touch --check [--stale N]`, which runs the existing
   `check_tree` machinery after `touch`'s end-of-batch reindex and folds the
   result into `touch`'s exit code.

2. **The stale window is hard-coded at the call site.** A fixed `--stale 14`
   is too short for multi-week projects: an active doc can be legitimately
   untouched for weeks while its milestone is in flight, so a hard-coded 14
   mis-flags healthy trees, and every agent workflow / skill that runs
   `docs check --stale 14` re-hard-codes the same number. M19 adds a
   `.docs.toml [check] stale_days = N` per-tree default so the window is
   tuned **per project** instead of at every call site, with an explicit CLI
   `--stale` still overriding it.

Both are pure ergonomics over existing machinery — `check_tree` already
takes a `stale: int | None`; `Config` already reads `.docs.toml` sections;
`docs touch` already runs an end-of-batch reindex. M19 wires them together;
it introduces no new verb and no new check rule.

A third, cosmetic item rides along: the `docs new --body-from` argparse
**help string** (`src/docs_cli/cli.py:2900-2905`) shipped in 1.6.0 still
describes the **pre-M15-C4** "first 20 lines looks like a metadata block"
heuristic. The runtime detector (`_body_has_metadata_block`) and the refusal
message are correct — only the help text drifted. M19 corrects the one line,
closing the follow-on tracked in status.md + the
[m17-pypi-publish-impl.md](m17-pypi-publish-impl.md) Open follow-on note.

### Scope — three deliverables

- **D1 — `docs touch --check [--stale N]`.** Add a `--check` flag to
  `docs touch`. When set, after `touch`'s end-of-batch INDEX refresh runs,
  `touch` invokes the existing `check_tree(root, config, stale, today,
  predicate=…)` over the resolved root and folds its findings into the exit
  code. The surface is fixed by the resolved Q1–Q4 (Decisions): `--check`
  runs the **tree-wide** check (the same surface bare `docs check` validates,
  *replacing* the `docs check .` step of the loop — Q2); the combined exit
  code is `max(touch, check)` — touch runs first and if it fails (exit 1/2)
  the check does NOT run and touch's code is returned, otherwise the check's
  0/1/2 becomes the command's exit code (Q1); `--stale N` on `touch` is
  forwarded to the check (absent → the D2 config default applies), and
  `--stale` **without** `--check` is a hard exit 2 (`--stale requires
  --check` — Q3); `--dry-run --check` previews the touch and runs the check
  against the **un-mutated** on-disk tree (Q4 — a doc the dry-run would
  refresh may still read as stale).
- **D2 — configurable per-tree stale window (`.docs.toml [check]
  stale_days = N`).** Add a `[check]` section to the `.docs.toml` schema
  with a single key `stale_days` (a non-negative integer; absent → no
  default stale window, preserving today's behaviour). `Config` grows a
  `stale_days: int | None = None` field populated by `load_config`. The
  resolution rule across the two **check-path** consumers — bare `docs check`
  and D1's combined `touch --check` path — is: an explicit CLI `--stale N`
  **always wins**; when `--stale` is absent, the config `stale_days` (if set)
  supplies the window. Per the resolved Q5, a configured `stale_days` makes
  **bare `docs check`** (with no `--stale` flag at all) apply the stale rule
  with window N — setting the key is the operator's explicit per-tree opt-in,
  the headline D2 contract; trees with no `[check]` section are byte-for-byte
  unchanged. Per the resolved Q6, the key is scoped to **check** semantics —
  it does NOT feed `docs list --stale`, which stays an explicit filter (bare
  `docs list` lists everything; an explicit `docs list --stale N` is
  unaffected).
  **Threshold provenance (operator feedback 2026-06-12 — folded into D2):**
  the stale finding's message names where the threshold came from — config-
  sourced thresholds append `set in .docs.toml [check] stale_days`, CLI-
  sourced thresholds append `via --stale` — wherever the stale rule fires
  (bare `docs check`, `docs check --stale`, and `docs touch --check`). See
  the threshold-provenance Decision for the exact wording contract.
- **D3 — `docs new --body-from` help-string fix (cosmetic, follow-on
  close).** Replace the stale argparse help string at
  `src/docs_cli/cli.py:2900-2905` (which still says "Refused (exit 2) if any
  of the body's first 20 lines looks like a metadata block") with wording
  that matches the actual M15-C4 detector. The turnkey replacement is the
  one drafted in the [m17-pypi-publish-impl.md](m17-pypi-publish-impl.md)
  Open follow-on note:

  > Read body content from PATH (or `-` for stdin) and append it under the
  > scaffold's frontmatter. Refused (exit 2) only if the body itself contains
  > a metadata block — a leading `---` fence or ≥2 adjacent
  > `{Lifecycle, Role, Updated}` lines (lone prose like a `Plan:` line is
  > fine). Pass body content only; `docs new` owns the frontmatter.

  Doc-only, one line in `cli.py`; the prose `docs/cli.md` §`docs new` and the
  bundled `references/cli.md` already carry the correct wording (verified at
  M17), so no spec edit is needed for D3 — only the argparse string. This is
  the **surface-parity gate** (plan.md "Ongoing conventions") catching its
  own motivating miss.

- **D4 — `cli.md` / `convention.md` + version bump + bundled-ref docs.**
  Document `docs touch --check` (and its `--stale` forwarding) in `cli.md`
  §`docs touch`; document the `[check] stale_days` config + the threshold-
  provenance message wording in `cli.md` §`docs check` and `convention.md`
  (the `.docs.toml` schema / `[check]` section), and note in `cli.md`
  §`docs list` that `[check] stale_days` does NOT change `docs list --stale`
  (Q6 — the key is check-scoped); bump `pyproject.toml` `version` → `1.6.5`
  and the `tests/test_packaging.py` version-pin assertion in lockstep; open
  a `## 1.6.5 — UNRELEASED` CHANGELOG section (the 1.6.0 section is already
  dated/published, so M19 starts a fresh line, unlike M18 which folded into
  the then-open 1.6.0 — see Decisions). Resync the bundled skill references
  byte-identical (M14 — C1: `docs/` is canonical), and honour the
  surface-parity gate (the new `--help` strings for `touch --check` +
  `[check]` config, plus D3's corrected `--body-from` string, reconciled
  against the bundled skill). The byte-identity invariant
  (`tests/test_skill_refs.py`) and the INDEX/dogfood-snapshot lockstep
  (`tests/fixtures/expected/docs-INDEX.md`) hold throughout.

## Deliverables

- [x] D1 `docs touch --check [--stale N]` runs `check_tree` after the
      end-of-batch reindex and folds its result into `touch`'s exit code
      (tree-wide check — Q2; combined exit = max(touch, check), touch-fail
      short-circuits the check — Q1). Pinned by Phase-2 tests (touch+check
      clean → 0; touch+check on a stale tree → 1; touch+check on a broken-ref
      tree → 2; `--stale` without `--check` → exit 2 — Q3; `--dry-run --check`
      writes nothing and checks the un-mutated tree — Q4). **DONE (Phase 6).**
- [x] D2 `.docs.toml [check] stale_days = N` parsed into `Config.stale_days`;
      consumed by bare `docs check` and D1's combined `touch --check` path
      (NOT `docs list --stale` — Q6); explicit CLI `--stale` overrides;
      absent config preserves today's "no stale window unless `--stale`"
      behaviour (Q5: a configured key opts bare `docs check` into the stale
      rule). The stale finding's message names the threshold's provenance —
      config-sourced → `set in .docs.toml [check] stale_days`, CLI-sourced →
      `via --stale`. Pinned by Phase-2 tests (config default applies to bare
      `check`; CLI `--stale` overrides config; no `[check]` section →
      unchanged; config-sourced provenance string; CLI-sourced provenance
      string). **DONE (Phases 5-6).**
- [x] D3 `docs new --body-from` argparse help string corrected to the M15-C4
      detector wording; `docs new --help` no longer says "first 20 lines".
      Closes the rolled-forward follow-on. Pinned by a help-string assertion
      (no "first 20 lines"; mentions the real `---` fence / `{Lifecycle,
      Role, Updated}` cluster shape). **DONE (Phase 6).**
- [x] D4 `cli.md` (§touch + §check + §list) + `convention.md` (`[check]`
      schema) document the behaviour; `pyproject.toml` 1.6.5 + packaging
      version-pin test in lockstep; `## 1.6.5 — UNRELEASED` CHANGELOG section
      authored (publish-survival wording); bundled skill refs byte-identical
      (`test_skill_refs` GREEN); INDEX + frozen snapshot in lockstep. **DONE
      (Phase 1 specs frozen; Phase 7 version + CHANGELOG).**
- [x] Surface-parity gate (Phase 10, plan.md "Ongoing conventions"): run
      `docs touch --help`, `docs check --help`, `docs new --help`; reconcile
      against the CHANGELOG surface; confirm the bundled skill documents the
      new flag + config; grep for stale wording describing any replaced
      behaviour (the `--body-from` "first 20 lines" string is the named
      target). **DONE (Phase 10): `--help` reconciled; SKILL.md verb table +
      `[check] stale_days` note updated (OQ-4); `grep "first 20 lines" src/`
      → zero source hits.**
- [x] Full suite GREEN (current 510 + the new M19 tests); ruff / ruff format
      / mypy / `docs check docs/` clean tree-wide; bundled cli.md /
      convention.md byte-identical; `docs --version` prints `docs 1.6.5`.
      **DONE (Phase 8): 533/533 GREEN; gate clean; `docs 1.6.5`.**

## Phase Checklist (10-phase TDD)

- [ ] 1. Define Contract — `cli.md` §touch `--check` block (exit-code
      folding = max(touch, check) with touch-fail short-circuit — Q1; tree-wide
      check — Q2; `--stale` without `--check` → exit 2 — Q3; `--dry-run
      --check` against the un-mutated tree — Q4; `--quiet` interaction);
      `cli.md` §check `[check] stale_days` resolution rule (CLI `--stale` >
      config > unset; Q5 makes bare `check` apply the rule) + the threshold-
      provenance message wording (config-sourced names the file+key,
      CLI-sourced names `--stale`); `cli.md` §list note that `[check]
      stale_days` does NOT feed `docs list --stale` (Q6); `convention.md`
      `.docs.toml [check]` schema entry; the D3 help-string correction noted;
      Q1–Q6 already resolved to Decisions (operator 2026-06-12); bundled refs
      resynced byte-identical; CHANGELOG version decision recorded (new 1.6.5
      line, NOT a fold-in — 1.6.0 is published).
- [ ] 2. Write Tests (RED) — `touch --check` clean/stale/broken-ref exit
      codes; touch-fail short-circuits the check (Q1); `--stale` without
      `--check` → exit 2 (Q3); `--dry-run --check` un-mutated-tree check (Q4);
      `--stale N` forwarding; `[check] stale_days` applies to bare `check`
      (Q5); CLI `--stale` overrides config; absent `[check]` unchanged;
      `docs list --stale` is UNAFFECTED by `[check] stale_days` (Q6 —
      regression lock that bare `docs list` still lists everything and the
      config does not filter it); the **threshold-provenance** assertions —
      a config-sourced stale finding contains `set in .docs.toml [check]
      stale_days`, a CLI-sourced (`--stale N`) stale finding contains `via
      --stale`; the D3 help-string assertion; the packaging version-pin bump
      to 1.6.5.
- [ ] 3. Create Fixtures — a small tree with a `.docs.toml [check] stale_days`
      key + a deliberately-stale active doc (for the config-default and
      override tests) under `tests/fixtures/trees/`; the `touch --check`
      broken-ref / stale cases are inline `tmp_path` helpers where small.
- [ ] 4. Run Tests (RED Baseline) — confirm the intended red set are all
      clean assertion failures (no tracebacks / argparse-exit-2 / collection
      errors); classify each new test RED vs GREEN-at-baseline (the D3
      help-string test is RED today; an absent-config regression lock is
      GREEN). Capture the baseline count.
- [x] 5. Update Base Interfaces — `Config.stale_days: int | None = None`
      field + `load_config` `[check]` read; the `touch` argparse `--check`
      + `--stale` flags declared (with the `--stale`-requires-`--check`
      guard — Q3); the `_cmd_check` + `touch --check` check-path call sites
      threaded to consult the config default (interface declared; behaviour
      may stay unchanged this phase per the honest split). `_cmd_list` /
      `query_docs` are deliberately NOT threaded (Q6 — `docs list` is not a
      consumer).
- [x] 6. Implement Core — the stale-window resolution helper (CLI `--stale`
      > `config.stale_days` > None) wired into `_cmd_check` and the
      `touch --check` path (NOT `_cmd_list` — Q6); the resolution carries
      the threshold's **source** (config vs CLI) so the stale finding's
      message can name the provenance — config-sourced appends `set in
      .docs.toml [check] stale_days`, CLI-sourced appends `via --stale`; the
      `touch --check` post-reindex `check_tree` call + exit-code fold (Q1);
      the `--stale`-without-`--check` exit-2 guard (Q3); the D3 help string.
      All RED → GREEN.
- [x] 7. Update Wrappers — `pyproject.toml` `version` → `1.6.5`;
      `## 1.6.5 — UNRELEASED` CHANGELOG section (Added: `touch --check`,
      `[check] stale_days`; Fixed: `--body-from` help drift); packaging
      version-pin test updated; bundled cli.md / convention.md resynced
      byte-identical (`test_skill_refs` GREEN).
- [x] 8. Run Tests (GREEN) + quality gate — full suite GREEN; ruff / format
      / mypy / `docs check docs/` / index dry-run clean; bundled refs
      byte-identical; INDEX == frozen snapshot; `docs --version` →
      `docs 1.6.5`.
- [x] 9. Integrate — dogfood the post-edit loop on a throwaway copy
      (`docs touch <file> --check` against a clean tree → exit 0; against a
      tree with a stale doc + a `[check] stale_days` shorter than the doc's
      age → exit 1; with a broken ref → exit 2), and the bare-`check` config
      default, on the real `docs/` tree read-only where safe; confirm the
      INDEX refresh + check run in one invocation.
- [x] 10. Quality, Docs, Refactor — closeout summaries (checklist +
      Deliverables + Success Criteria ticked, impl-log rows); INDEX + frozen
      snapshot lockstep; status/plan updated; surface-parity gate run
      (`--help` reconciliation + stale-wording grep); lifecycle left `draft`
      matching the M14/M15/M18 completed-but-live precedent (M19 stays live
      until a later milestone sweeps it in; the PyPI publish is a separate
      future milestone). Simplify pass over the new wiring.

## Decisions

- **Ships as v1.6.5, local build only (operator-directed 2026-06-12 —
  BINDING).** M19 is an explicit **1.6.5** patch-line release, NOT 1.7.0. It
  builds 1.6.5 locally; the PyPI publish is a later operator-driven milestone
  (the M12→M13, M14+M15→M17 cadence). `pyproject.toml` `version` and the
  `tests/test_packaging.py` version-pin assertion bump to `1.6.5` at Phase 7;
  `importlib.metadata` remains the version SoT (M12), so `docs --version`
  reads `1.6.5` after an editable reinstall. Patch-level (1.6.x, not 1.7.0)
  is the right SemVer bucket: `touch --check` and `[check] stale_days` are
  additive, backward-compatible affordances (no flag removed, no default
  changed for trees without a `[check]` section), and the `--body-from` fix
  is doc-only.
- **CHANGELOG: a NEW `## 1.6.5 — UNRELEASED` section (NOT a fold-in).**
  Unlike M18 — which appended to the then-**open** `## 1.6.0 — UNRELEASED`
  because 1.6.0 had not yet published (M18's Q2) — the `## 1.6.0` section is
  now **dated and published** (M17, 2026-06-03). So M19 opens a fresh
  `## 1.6.5 — UNRELEASED` section above it with publish-survival wording, and
  the eventual publish milestone dates it (the M14-opens-section pattern).
- **No new verb, no new check rule.** `--check` is a flag on the existing
  `docs touch`; `[check] stale_days` is a config key feeding the existing
  `stale` rule. The stale rule's id (`stale`), severity (warning, exit 1),
  and the `check_tree` signature (`stale: int | None`) are unchanged — D2
  only changes *where the `stale` value comes from* when the CLI flag is
  absent. The one exception is the **stale-finding message text**, which D2
  extends to name the threshold's provenance (see the threshold-provenance
  Decision below); the rule id and severity are untouched, so CI hooks that
  branch on the `stale` rule id or exit code are unaffected.
- **Stale-window resolution precedence — CLI `--stale` > `[check]
  stale_days` > unset.** Across the two **check-path** consumers (`docs
  check` and `docs touch --check`); `docs list --stale` is NOT a consumer
  (Q6 — it stays an explicit filter). An explicit CLI `--stale N` always wins
  (including `--stale 0`, which means "flag every active doc not updated
  today" — a real, if aggressive, value, so it is honoured as given, not
  treated as "unset"). When `--stale` is absent and `[check] stale_days` is
  set, the config value applies (Q5: this makes bare `docs check` apply the
  stale rule). When neither is present, behaviour is exactly today's (no
  stale window). This keeps trees without a `[check]` section byte-for-byte
  unchanged. (Distinguishing "flag absent" from "`--stale 0`" requires the
  argparse default to be `None`, which it already is — `type=int` with no
  `default=` yields `None` when the flag is omitted.)
- **Stale-warning message names the threshold's provenance (operator
  feedback 2026-06-12 — BINDING; folded into D2).** Today the stale finding
  reads `Lifecycle: active but not updated in N days (stale threshold 14)`,
  which tells the operator the value but not *where it is set*, so they
  cannot tell which knob to turn. M19 extends the parenthetical to name the
  source of the threshold:
  - when the window came from `.docs.toml [check] stale_days`, the message
    appends the config provenance, e.g. `(stale threshold 14, set in
    .docs.toml [check] stale_days)`;
  - when the window came from the CLI flag, the message names the flag, e.g.
    `(stale threshold 14, via --stale)`.

  The requirement is that a **config-sourced** threshold name the config
  file + key so the operator knows where to change it; the CLI-sourced
  variant names the flag for symmetry. This applies to the stale rule
  **wherever it fires** — bare `docs check` (config-sourced), `docs check
  --stale N` (CLI-sourced), and D1's `docs touch --check` path (which
  inherits the same resolution: config-sourced when no `--stale`, CLI-sourced
  when `--stale N` is forwarded). The exact wording above is the contract; it
  is the only behavioural change to the stale finding (id + severity + exit
  code unchanged). D2's Success Criteria and the Phase-2 test surface cover
  both provenance variants.
- **`--body-from` help fix is doc-only and closes the follow-on.** The
  runtime detector and refusal message are already correct (verified at
  M17); only the argparse help string drifted, and `docs/cli.md` + the
  bundled `references/cli.md` already carry the right wording. D3 is one
  line in `cli.py`; it needs no spec edit, only the surface-parity-gate
  reconciliation. It is folded into M19 because it is the gate's own
  motivating miss and the operator named it for this milestone.
- **Lifecycle stays `draft` (M14/M15/M18 precedent).** A milestone flips to
  `archived` only when physically moved to the archive subtree by a later
  milestone's sweep (convention.md); M19 stays live at root through
  implementation-complete. The plan forbids self-archiving the M19 pair.
- **Resolved questions (Q1-Q6, BINDING — operator decisions 2026-06-12).**
  The six OPEN QUESTIONS are resolved as follows; each takes the recommended
  default the draft was written against, so no Scope, Deliverable, or
  Phase-Checklist text moves:
  - **Q1 (`touch --check` exit-code folding) → combined exit = `max(touch,
    check)`.** Touch runs first; if touch itself fails (exit 1 or 2) the
    check does **not** run and touch's code is returned (a failed touch left
    nothing meaningful to validate). If touch succeeds (0), the check runs
    and its 0/1/2 becomes the command's exit code.
  - **Q2 (check scope) → TREE-WIDE.** `--check` runs the same
    `check_tree(root, …)` bare `docs check` runs — it *replaces* the
    `docs check .` step of the three-command loop. A touched-files-only mode
    is explicitly out of M19 scope.
  - **Q3 (`--stale` without `--check`) → hard exit 2.** Passing `--stale`
    without `--check` is a hard refusal (exit 2, `--stale requires --check`),
    matching the project's fail-loud-on-incoherent-flags stance — not a
    silent no-op.
  - **Q4 (`--dry-run --check` semantics) → check runs against the
    un-mutated tree.** `--dry-run --check` previews the touch and runs the
    check against the on-disk (un-mutated) tree; document explicitly that a
    doc the dry-run *would* refresh may still show as stale, since dry-run
    did not bump its `Updated:`.
  - **Q5 (does `[check] stale_days` make bare `docs check` apply the stale
    rule?) → YES.** A configured `[check] stale_days = N` makes bare
    `docs check` (no `--stale` flag) apply the stale rule with window N.
    Setting the key is the operator's explicit per-tree opt-in; trees with
    no `[check]` section are byte-for-byte unchanged. This is the headline
    D2 contract (the per-tree window replacing the hardcoded per-call 14).
  - **Q6 (does `[check] stale_days` also feed `docs list --stale`?) → NO.**
    The key is scoped to **check** semantics only; `docs list --stale` stays
    an explicit filter (bare `docs list` lists everything). An explicit
    `docs list --stale N` is unaffected.
- **Implementation-phase open questions (OQ-1..OQ-5, BINDING — conductor
  decisions, resolved for Step 2 — phases 5-10).** The Step-2 planning agent
  surfaced five implementation forks; the conductor resolved each, and they
  are recorded here for the same reason Q1-Q6 are:
  - **OQ-1 (config-value validation for `[check] stale_days`) → REFUSE a
    non-integer value (amended by the Step-2 fresh-eyes review; the original
    "leniency parity" rationale was disproved).** The original decision read
    `stale_days` raw "like `add_roles` / `project_name`", expecting leniency
    parity. The review proved that rationale factually wrong: the sibling reads
    coerce via `frozenset()` / `tuple()` and so never crash, whereas
    `stale_days` is stored raw and flows straight into `check_doc`'s
    `(today - updated).days > stale` comparison — where a non-int (e.g. the
    TOML string `stale_days = "14"`) raises an **uncaught `TypeError`
    traceback** (reproduced by the reviewer). A traceback on malformed config
    is a bug, so `load_config` now refuses it: a present-but-non-int
    `stale_days` fails the config load the same way any other malformed
    `.docs.toml` condition does — it raises `tomllib.TOMLDecodeError`, which
    every caller already catches → **exit 2** with `docs: malformed .docs.toml:
    [check] stale_days must be an integer`. `bool` is excluded explicitly
    (`isinstance(x, int) and not isinstance(x, bool)`), since `isinstance(True,
    int)` is True in Python and TOML `stale_days = true` would otherwise slip
    through. **Negative ints stay honoured** (aggressive-but-graceful,
    mirroring the `--stale 0` precedent — a negative window simply flags every
    active doc). Pinned by `test_check_malformed_stale_days_refused_cleanly`
    (`tests/test_cli_check.py`: clean exit 2 + message, no traceback). (A
    broader cross-key config-validation pass, if ever wanted, is still a
    separate change — this fix is scoped to the one key that detonates.)
  - **OQ-2 (CLI-sourced provenance suffix risks regressing existing
    `docs check --stale N` message assertions) → audit-then-green (mandatory,
    in-phase).** Before declaring Phase 6 GREEN, `grep -rn "stale threshold"
    tests/` + audit every hit. Result: only the 3 new M19 provenance tests pin
    the threshold-message text; all pre-existing stale assertions are
    rule/severity-based or loose substrings (`test_check_stale_only_tree_exits_1`
    asserts `"stale" in stdout.lower()`, which `via --stale` satisfies). Zero
    regression — the highest-risk item in the milestone, cleared.
  - **OQ-3 (does the repo's own `docs/.docs.toml` adopt `[check] stale_days`
    in M19?) → NO.** The repo tree does not adopt the key in M19. The config
    path is dogfooded on a throwaway `cp -r` copy of `docs/` instead, so the
    repo's tree stays byte-unchanged and `docs check docs/` keeps its current
    no-stale-window behaviour. (Adopting the key for this repo is a separate,
    later operator choice.)
  - **OQ-4 (update the bundled `SKILL.md` verb table for `touch --check`?) →
    YES.** The `SKILL.md` touch row gains `[--check [--stale N]]` + a
    "--check folds in docs check" note, plus a brief `[check] stale_days`
    paragraph. `SKILL.md` has no byte-identity test counterpart (unlike the
    `references/` bundled refs), so there is no lockstep cost.
  - **OQ-5 (does `docs touch --check` get a `--json` mode in M19?) → NO
    (deliberate non-goal).** `touch --check` prints grouped human findings
    only; `--json` is out of M19 scope and is a candidate follow-on. (Bare
    `docs check --json` is unchanged.)

## Testing / Quality Gate

The standard tree-wide gate plus the new behaviour tests:

```sh
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
.venv/bin/docs check docs/
.venv/bin/docs index --root docs/ --dry-run
.venv/bin/docs --version            # must print `docs 1.6.5` after Phase 7 + reinstall
```

Dogfood at Phase 9: on a throwaway copy, run `docs touch <file> --check`
against (1) a clean tree → exit 0, (2) a tree with a stale active doc and a
`.docs.toml [check] stale_days` shorter than the doc's age → exit 1, (3) a
tree with a broken `Related:` ref → exit 2; confirm `docs touch --stale 14`
(no `--check`) → exit 2 (Q3); and confirm bare `docs check` (no `--stale`)
honours a configured `stale_days` and that its stale finding names the
provenance (`set in .docs.toml [check] stale_days`), while `docs check
--stale N` names `via --stale`. Confirm the single invocation performs both
the INDEX refresh and the check.

## Success Criteria

- [x] `docs touch <files> --check` runs the tree-wide check after the reindex
      in one invocation; its exit code is `max(touch, check)` with a
      touch-fail short-circuit (clean → 0; stale-only → 1; errors → 2).
      `--stale` without `--check` → exit 2 (Q3). `--dry-run --check` writes
      nothing and checks the un-mutated tree. **MET — Phase 6 impl + Phase 9
      dogfood (exercises 1-4).**
- [x] `.docs.toml [check] stale_days = N` supplies the stale window to bare
      `docs check` and `docs touch --check` when no CLI `--stale` is given
      (Q5); an explicit `--stale` overrides it; a tree with no `[check]`
      section is unchanged; `docs list --stale` is NOT affected by the config
      key (Q6 — it stays an explicit filter). The stale finding names the
      threshold's provenance — config-sourced → `set in .docs.toml [check]
      stale_days`; CLI-sourced → `via --stale`. **MET — Phases 5-6 impl +
      Phase 9 dogfood (exercises 2, 5).**
- [x] `docs new --help` no longer describes the "first 20 lines" heuristic;
      the rolled-forward `--body-from` help-drift follow-on is closed. **MET —
      Phase 6 D3 help fix; `grep "first 20 lines" src/` → zero source hits.**
- [x] `cli.md` / `convention.md` document both features; bundled refs
      byte-identical (`tests/test_skill_refs.py` GREEN); INDEX + frozen
      snapshot in lockstep. **MET — Phase 1 specs frozen; `test_skill_refs`
      GREEN; INDEX == snapshot.**
- [x] `pyproject.toml` + packaging version-pin at `1.6.5`;
      `## 1.6.5 — UNRELEASED` CHANGELOG section authored; `docs --version`
      prints `docs 1.6.5`. NO publish, NO tag, NO GitHub release (a later
      milestone publishes). **MET — Phase 7; standalone `python -m build` +
      `twine check` both PASSED (local verification only, dist/ gitignored).**
- [x] Full suite GREEN; quality gate clean tree-wide. **MET — Phase 8:
      533/533 GREEN; ruff / format / mypy / `docs check docs/` clean.**

## OPEN QUESTIONS

**None outstanding.** All six (Q1–Q6) are RESOLVED — operator decisions
2026-06-12, each per the recommended default — and recorded in Decisions ›
"Resolved questions (Q1-Q6, BINDING)" above: Q1 (exit-code folding) →
`max(touch, check)` with a touch-fail short-circuit; Q2 (check scope) →
tree-wide (replaces the `docs check .` loop step); Q3 (`--stale` without
`--check`) → hard exit 2; Q4 (`--dry-run --check`) → check runs against the
un-mutated tree; Q5 (configured `[check] stale_days` makes bare `docs check`
apply the stale rule) → YES; Q6 (does it feed `docs list --stale`) → NO
(check-scoped). The analysis below is retained as the historical record of
the forks and why each was decided.

Genuine scope/contract forks for the operator. Each: question, why it
matters, recommended answer.

- **Q1 — `touch --check` exit-code folding.** *Why it matters:* `docs touch`
  today exits 0 (success), 1 (missing/bad path), or 2 (outside-root refusal /
  INDEX-refresh failure); `docs check` exits 0/1/2 on its own ladder. When
  `--check` runs both, the combined code must be unambiguous and not mask a
  touch failure behind a clean check (or vice versa). *Recommendation:* the
  combined exit code is **`max(touch_result, check_result)`**. Touch runs
  first; if touch itself fails (1 or 2) the check never runs and that code is
  returned (a failed touch left nothing meaningful to validate). If touch
  succeeds (0), the check runs and its 0/1/2 becomes the command's exit code.
  This makes `--check` strictly more informative than `touch` alone and
  matches the intuition "the loop failed if either step failed, at the worse
  severity."
- **Q2 — check scope: tree-wide vs touched-files-only.** *Why it matters:*
  the operator's stated workflow ends in `docs check . --stale 14` — a
  **tree-wide** validation — so a touched-files-only check would not actually
  replace the three-command loop. But a tree-wide check on every `touch`
  could surface findings in files the operator did not edit. *Recommendation:*
  **tree-wide** — `--check` runs the same `check_tree(root, …)` bare
  `docs check` runs, because (i) it is what the loop being replaced does, and
  (ii) `docs check` is already cheap (one tree walk) and the touch already
  walked the tree for its reindex. A touched-files-only mode would be a
  different, narrower feature; if wanted later it is `--check-touched` or
  similar, out of M19 scope.
- **Q3 — `--stale` on `touch` when `--check` is absent.** *Why it matters:*
  `--stale N` is only meaningful alongside `--check` (touch itself has no
  stale concept). Passing `--stale` without `--check` is either a no-op or a
  user error. *Recommendation:* argparse-allow `--stale` only to **feed**
  `--check`; if `--stale` is given without `--check`, **exit 2** with a clear
  message (`docs: touch: --stale requires --check`) rather than silently
  ignoring it. (Alternatively a softer "warn and ignore" — but a hard refusal
  matches the project's fail-loud-on-incoherent-flags stance, e.g. the
  cascade mutually-exclusive group.) When `--check` is given without
  `--stale`, the D2 config default (Q5) supplies the window.
- **Q4 — `--dry-run --check` semantics.** *Why it matters:* `docs touch
  --dry-run` writes nothing and prints `docs: would touch <path>`. Combined
  with `--check`, does the check run, and against which tree state?
  *Recommendation:* **yes, the check runs, against the un-mutated tree** —
  `--dry-run --check` is a useful "preview the touch AND tell me if the tree
  currently validates" probe. The check observes the tree as-is (the dry-run
  made no edits), so stale findings reflect the *pre-touch* `Updated:` dates;
  document this explicitly (a doc that the dry-run *would* refresh may still
  show as stale, since dry-run did not bump it). No INDEX refresh runs under
  `--dry-run`, so the check walks the on-disk tree directly.
- **Q5 — does a configured `[check] stale_days` make bare `docs check`
  apply the stale rule?** *Why it matters:* today `docs check` with no
  `--stale` flag does **not** run the stale rule at all. If a configured
  `stale_days` only took effect when `--stale` was *also* passed, the config
  key would be nearly useless (you would still type `--stale` every time).
  But making bare `docs check` suddenly start flagging stale docs is a
  behaviour change for any tree that adds the key. *Recommendation:* **YES —
  a configured `[check] stale_days = N` makes bare `docs check` apply the
  stale rule with window N** (CLI `--stale` still overrides). Setting the key
  is the operator's explicit, per-tree opt-in to stale-checking; that is the
  entire point of the feature (tune the window per project, then stop typing
  `--stale`). Trees with no `[check]` section see no change. This is the
  headline D2 contract — flag it prominently for operator confirmation.
- **Q6 — does `[check] stale_days` also feed `docs list --stale`?** *Why it
  matters:* `docs list --stale N` filters to docs older than N days. It is a
  *query*, not a validation, and `--stale` there is the filter predicate, not
  a warning threshold — so a config default is less obviously wanted.
  *Recommendation:* **NO — `docs list` keeps `--stale` as an explicit,
  required-to-filter flag; `[check] stale_days` does NOT change `list`'s
  default** (bare `docs list` with no `--stale` still lists everything). The
  config key is named `[check] stale_days`, scoped to the **check** semantics;
  bleeding it into `list`'s filter would conflate "validation window" with
  "query filter." (If the operator wants the config to feed `list` too, that
  is a one-line change — but the recommended default keeps the key's scope
  honest to its name. This narrows the broader "how does it interact with
  `docs list --stale`" question in the follow-on.) An explicit
  `docs list --stale N` is of course unaffected — it filters by N as always.

OPEN QUESTIONS: none outstanding — Q1–Q6 above are all RESOLVED (operator
decisions 2026-06-12, recorded in Decisions).
