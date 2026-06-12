# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.6.5 — UNRELEASED

Post-edit validation ergonomics (M19). Two additive, backward-compatible
affordances on the post-edit loop plus one cosmetic help-string fix. Built
locally; a later operator-driven milestone publishes to PyPI.

### Added

- **`docs touch <files> --check [--stale N]`** (M19 — D1). Folds the existing
  `docs check` machinery into `docs touch` so the common post-edit loop
  (`docs touch <files>` → `docs index .` → `docs check . --stale N`) collapses
  to a single invocation. After `touch`'s end-of-batch INDEX refresh, the same
  tree-wide `check_tree` bare `docs check` runs validates the resolved root and
  its result folds into the exit code as `max(touch, check)` — touch runs
  first and a failed touch (exit 1/2) short-circuits the check. `--stale N` is
  forwarded as the check's stale window; `--stale` **without** `--check` is a
  hard error (exit 2, `docs: touch: --stale requires --check`). `--dry-run
  --check` previews the touch and checks the un-mutated on-disk tree. The check
  honours the same `[exclude]` / `.docsignore` predicate as the reindex, and
  its findings print on stdout regardless of `--quiet`.
- **`.docs.toml [check] stale_days = N`** (M19 — D2). A per-tree default stale
  window for validation. Consumed by both bare `docs check` and `docs touch
  --check`: when no CLI `--stale` is given, a configured `stale_days` supplies
  the window — a configured key therefore arms the `stale` rule on **bare
  `docs check`** (the operator's per-tree opt-in). An explicit CLI `--stale N`
  always overrides it; a tree with no `[check]` section is byte-for-byte
  unchanged. The stale finding's message names the threshold's provenance —
  config-sourced appends `, set in .docs.toml [check] stale_days`, CLI-sourced
  appends `, via --stale` — so the operator knows which knob to turn. This
  provenance suffix rides on the stale finding's message text in both the human
  and `--json` output (the rule id `stale` and severity `warning` are
  unchanged). A non-integer `stale_days` (e.g. the TOML string `"14"`) is
  refused at config load — exit 2, `malformed .docs.toml: [check] stale_days
  must be an integer` — rather than crashing; negative integers are honoured.
  The key is check-scoped: it does **not** affect `docs list --stale`, which
  stays an explicit filter.

### Fixed

- **`docs new --body-from` help-string drift** (M19 — D3). The argparse help
  still described the pre-M15-C4 "first 20 lines looks like a metadata block"
  heuristic; corrected to the real detector (a leading `---` fence or ≥ 2
  adjacent `{Lifecycle, Role, Updated}` lines). The runtime detector and
  refusal message were already correct — only the help text drifted.

## 1.6.0 — 2026-06-03

Robustness + autonomous archival (M14) and agent-native doc authoring
(M15), shipped together as one release.

M14: robustness + autonomous archive. Burns down the post-1.5.0
multi-agent-review correctness/atomicity findings (Thread A), lands the
non-interactive `docs archive --cascade` agent affordance (B1), and
corrects a packaging guard (C3). The bundled-skill reference links were
already fixed by M16 (C1) — M14 adds a regression guard.

M15: agent-native doc authoring. Adds the single-doc `docs project set`
(B2) and the write-then-stamp `docs stamp` (B3), and replaces the
`docs new --body-from` refusal heuristic with a real-metadata-block
detector (C4) so legitimate prose bodies are no longer wrongly refused.

### Added

- **Non-interactive `docs archive --cascade` flag set** (M14 — B1).
  Establishes the invariant *`docs` never prompts unless `--interactive`*.
  Bare `--cascade` archives every one-hop `pairs-with` / `child-of`
  relation that exists on disk to the same dated directory with **no
  prompt**, and prints a loud stderr footer naming the set
  (`docs: cascade archived N related doc(s): …`). `--cascade-dry-run`
  previews the would-be cascade set and writes nothing (exit 0; the
  primary is not archived either — equivalent to `--cascade --dry-run`).
  `--cascade-only GLOB` archives only the subset whose related-doc
  root-relative POSIX target matches `GLOB` (compiled by the same matcher
  `compile_exclude_predicate` uses); composes with `--cascade-dry-run`.
  `--interactive` restores the legacy `[y/N]` prompt and is the only path
  that reads stdin. `--cascade`/`--cascade-only`/`--interactive` are
  mutually exclusive; `--cascade-dry-run` is rejected with `--interactive`.
- **`docs project set <doc>... <new-project>`** (M15 — B2). The single-doc
  counterpart to `project rename`: reassigns the `Project:` field of just
  the named docs (inserting the line when absent) and regenerates `INDEX.md`
  once at end of batch — never touching `.docs.toml`, non-named docs, or
  `Related:` edges. Validate-all-first atomic semantics (no write until every
  named doc passes). `<new-project>` is auto-normalised; a value new to the
  tree is **refused** (exit 2) unless `--new-project` is passed — the typo
  guard that stops an agent silently fragmenting the INDEX (`idea` vs
  `ideas`). The refusal carries a `difflib`-derived `did you mean '<closest>'?`
  prefix when a known project is close, and **always** prints the
  `to create a new project group, pass --new-project` recovery hint. A named
  archived doc refuses the whole batch (exit 2); a missing/malformed/outside
  named doc aborts before any write (exit 1). `--dry-run` previews.
- **`docs stamp <file>... [--role] [--project] [--title]`** (M15 — B3). The
  write-then-stamp counterpart to `docs new --body-from`: inserts a
  convention-correct metadata block onto one or more files an agent already
  wrote, preserving the body verbatim. `Lifecycle: draft`; role from `--role`
  else the default `notes` (there is **no** H1-role inference — a file whose
  H1 reads like a plan still gets `notes`); project from `--project` else the
  root's configured project; title from the file's H1, `--title`, or a
  filename-derived synthesis. Re-stamping a file that already carries a valid
  block is idempotent — only `Updated:` is refreshed. Foreign metadata-shaped
  lines are parked under a `## Migrated metadata` body section. Atomic
  multi-file batch (a bad/missing file aborts before any write, exit 1); one
  end-of-batch INDEX refresh; invalid `--role` exits 2; `--dry-run` previews.

### Changed

- **`docs new` refuses the cwd-as-root fallback** (M14 — A2). With no
  `--root` and no `.docs.toml` ancestor, `docs new` now exits 2 with
  `docs: new: <path> is not under a docs root with .docs.toml; refusing`
  rather than silently scaffolding into the unmanaged cwd with default
  config. `--root <dir>` without `<dir>/.docs.toml` likewise refuses
  (`docs: new: --root <dir> does not contain .docs.toml; refusing`). The
  read verbs (`index`/`list`/`check`) keep the cwd-fallback — a wrong-tree
  read is recoverable; a write is not.
- **`atomic_write` now fsyncs before publishing** (M14 — A5). The tmpfile
  is `os.fsync`'d before the rename and the parent directory is fsync'd
  after, so the durability the `cli.md` §archive "fsync'd" claim promises
  is real. The published bytes are unchanged.
- **The end-of-batch reindex of every mutating verb honours `[exclude]` /
  `.docsignore`** (M14 — A6). `docs touch`, `docs archive`, `docs mv`, and
  `docs project rename` thread the persistent exclude predicate into every
  tree walk and INDEX refresh, so a malformed *excluded* file (e.g. a
  bundled plugin `README.md`) never fails a post-mutation walk. No new
  `--exclude` flag is added to the mutating verbs.

### Fixed

- **`docs mv` is now all-or-nothing** (M14 — A1). A validate-all-first
  pre-flight walk runs before the move, so a malformed sibling aborts the
  move with exit 2, leaving the source in place, the destination absent,
  and every referring `Related:` edge untouched (no dangling edge, no
  stray INDEX). Previously the move happened first and the rewrite walk
  raised afterwards, leaving a half-moved tree.
- **An `OSError` mid edge-rewrite maps to a clean exit 2** (M14 — A4).
  `docs mv` and `docs archive` no longer leak an uncaught traceback when a
  referring doc cannot be written (e.g. a read-only directory) after the
  move.
- **`docs new <role> "foo/"` is rejected** (M14 — A3). A slug with an
  empty final segment (`foo/`, `foo/.md`) exits 2 with
  `docs: invalid slug …` instead of writing an invisible `.md` dotfile
  that every read verb skips.
- **The packaging skill-data guard actually fails on a broken glob**
  (M14 — C3). The false-confidence `test_a6` (which grepped a pyproject
  *comment*) was removed; `test_b3_wheel_contains_cli_and_skill` asserts
  the built wheel carries the real skill package-data.
- **Bundled-skill reference links resolve on a clean host** (M14 — C1,
  done by M16). M14 adds a regression guard
  (`test_bundled_skill_has_no_repo_relative_links`) that fails if any
  bundled reference reintroduces a repo-relative `../` link.
- **`docs new --body-from` no longer refuses legitimate prose bodies**
  (M15 — C4). The old refusal heuristic flagged any body whose first 20
  lines contained a `Label:`-shaped line, so a test-matrix section opening
  `## Risk level` / `Reason: …` or a prose `Plan:` line was wrongly refused.
  The detector now refuses **only** on a real metadata block: a leading
  `---` YAML fence, or a contiguous run of **≥ 2** of the required-field
  labels `{Lifecycle, Role, Updated}` on adjacent lines (a non-required
  `Label:` line or any blank/prose line resets the run). A lone prose
  required-field line is accepted and appended verbatim. The refusal error
  tokens are unchanged.
- **Archiving interrelated docs no longer orphans `Related:` edges**
  (M18). When a milestone plan and its log (or a `--cascade` pair/trio) are
  archived into the same `archive/<date>/` folder, each moved doc's OWN
  intra-archive `Related:` edges are now repointed to the new
  root-relative archive path, and an ALREADY-archived referrer whose target
  sweeps into the archive is likewise repointed — so `docs check` stays
  clean instead of reporting `broken-ref` (exit 2). This narrows the M3
  "archive subtree is read-only" stance to move-driven `Related:` rewrites
  ONLY (an edge is rewritten iff its target equals a doc moving in the same
  archival; prose and non-moving edges stay byte-identical). `docs mv`
  already carried the moved-doc own-edge rewrite and is unchanged.

## 1.5.0 — 2026-05-29

M12: project rename verb + M11 wart fixes + version SoT.
Bundles the operator-facing `docs project rename` headline
deferred from M10 with burn-down of two M11-surfaced warts
(`docs touch` outside-root refusal; `docs archive` referring-
edge rewrite) and a small packaging refactor
(`__version__` sourced from `importlib.metadata`).

### Added

- **`docs project rename <new-name>`** (M12) — new operator
  verb in the `docs project` namespace. Rewrites
  `.docs.toml`'s `[project] name` and every conformant
  `Project: <old>` line in every active doc, atomically,
  with a single end-of-batch INDEX refresh. Validates the
  whole batch up-front; any malformed doc aborts before any
  write. The operator-supplied `<new-name>` is auto-
  normalised via M7's `normalise_project_name()`; empty
  post-normalised input exits 2. `--dry-run` prints the
  plan without writing. Multi-project trees are tolerated:
  docs whose `Project:` does not match the old name are
  reported in the success footer but not mutated. The
  archive subtree is read-only (skipped + reported).

### Changed

- **`docs touch <file>` outside a docs root now refuses
  cleanly** (M12 — OQ-C). When no `.docs.toml` exists in
  the resolved ancestor chain, `docs touch` exits 2 with
  `docs: touch: <path> is not under a docs root with
  .docs.toml; refusing` and leaves the file unchanged. No
  downstream INDEX refresh runs (closes the M11 cascade-
  crash where a sibling failed its Lifecycle check). An
  explicit `--root <dir>` bypasses the refusal only when
  `<dir>/.docs.toml` exists; otherwise exit 2 with
  `docs: touch: --root <root> does not contain .docs.toml;
  refusing` (M12 — OQ-11).
- **`docs archive <doc>` now rewrites referring `Related:`
  edges** (M12). After the move, every `Related: <verb>:
  <old-rel>` bullet across the active tree is rewritten to
  point at `archive/<YYYY-MM-DD>/<basename>`, atomically
  with the move and lifecycle edit. `--cascade` extends
  this to all docs moved by the cascade in a single atomic
  batch with one end-of-batch INDEX refresh. Prose
  markdown references to the old path are deliberately left
  alone (consistent with M2's `docs mv` "Related: only, not
  prose" stance).
- **`__version__` sourced from `importlib.metadata`** (M12).
  `pyproject.toml`'s `[project] version` is the single
  source of truth; `docs_cli.cli.__version__` reads via
  `importlib.metadata.version("docs-cli")` at import time
  with a `PackageNotFoundError` fallback to `0.0.0+local`
  for fresh-clone runs that haven't `pip install -e`'d yet
  (M12 — OQ-4). The hardcoded `__version__ = "1.4.0"`
  literal in `src/docs_cli/cli.py` is gone.

### Notes

- **Version bump.** 1.5.0 (minor) — SemVer-compliant: the
  new verb is additive; the M11 wart fixes are bug fixes;
  the `importlib.metadata` refactor has no API change.
- **`Project:` row of `convention.md` updated** to mention
  `docs project rename` as the in-lockstep rewriter.

## 1.4.0 — 2026-05-27

M10: adoption-flow polish + 1.3.0 carry-overs. Bundles two
agent-driveability features (multi-file atomic `docs touch`;
`docs migrate --apply` writes the `.docs.toml` sidecar
automatically) with the carry-overs from M3
(`[vocabulary] add_fields` allowlist + `unknown-field` check
warning), M7 (`Confidence` enum replacing the `bool | str`
tri-value), and M8 (`--apply --quiet` per-file output
suppression, `MigrationPlan.excluded_count` removal,
adoption-playbook restructure). Published to PyPI 2026-05-27
via M11 (operator-driven publish milestone mirroring M9's
relationship to M8).

### Added

- **`docs touch <file>...`** (M10 — OQ-C) — multi-file atomic
  touch. Accepts one or more positional file paths. Validates
  every path first (existence + same-docs-root); aborts the
  whole batch on any failure (named-bad-path on stderr, exit
  1, no on-disk mutation); refreshes the INDEX exactly once
  at end-of-batch.
- **`docs migrate --apply` writes `.docs.toml` automatically**
  (M10 — OQ-A / OQ-L / OQ-M). Absent sidecar gets a minimal
  `[project] name = "<resolved>"` + `[archive] date_format`
  block. Existing sidecar without `[project]` gets the new
  block appended under a `# Added by docs migrate --apply`
  provenance comment header. Existing `[project]` is never
  overwritten. No `dir = "archive"` line is emitted (the
  default is stable).
- **Opportunistic empty-parent rmdir after archive-move**
  (M10 — OQ-G / OQ-Q). After `--apply` moves a foreign
  archive-style file into `archive/<date>/`, the now-empty
  source parent dir is removed. `OSError(ENOTEMPTY)` is
  swallowed so non-migrating siblings survive.
- **`[vocabulary] add_fields` allowlist + `unknown-field`
  check rule** (M10 — OQ-F / OQ-H / OQ-O / OQ-P). Opt-in
  warning (exit 1) for extra metadata labels not on the
  built-in always-allowed set
  (`Lifecycle` / `Role` / `Project` / `Updated` / `Related` /
  `Archived-reason`) and not on `add_fields`. The rule is
  OFF by default — trees without the allowlist see no
  change. Matching is case-sensitive exact match.
- **`Confidence` enum** (M10 — OQ-E / OQ-N) replacing the
  M4-era `bool | str` tri-value for `infer_role` and
  `FileMigration.confidence`. The enum's `value` strings
  (`"high"` / `"medium"` / `"low"`) match the M4 JSON wire
  format byte-for-byte; `migration_to_json` crosses
  enum→string via `enum.value` at the boundary.

### Changed

- **`docs migrate --apply --quiet`** (M10 — OQ-B) now
  suppresses the per-file plan block on stdout in addition
  to the trailing `docs: migrated <N> file(s) ...` success
  line on stderr. Empty stdout + empty stderr on a clean
  `--apply --quiet` run. `--dry-run` / `--summary` /
  `--json` are requested outputs and never suppressed.
- **`docs touch <file>` is now `docs touch <file>...`**
  (M10 — OQ-C). Single-file invocation continues to work;
  the argparse spec is `nargs="+"`.
- **Adoption playbook restructured to 4 steps** (M10 — OQ-I)
  — plan / triage / apply / verify. The three-pattern
  ordering note in Step 3 (about when to write `.docs.toml`
  before vs. after `--apply`) is gone now that `--apply`
  writes the sidecar automatically. The worked example runs
  end-to-end with `--apply --quiet` and immediately runs
  `docs check`.
- **`MigrationPlan.excluded_count` removed** (M10 — OQ-D)
  as a breaking change. The field was set in
  `plan_migration` but never read in shipped code. The
  human plan footer iterates `excluded_breakdown` directly;
  `migration_to_json` omitted the field already. Consumers
  who need the total compute `sum(c for _, c in
  excluded_breakdown)`. No known external consumer.

### Notes

- **Version bump.** 1.4.0 (minor); SemVer-compliant since
  the only breaking surface (`MigrationPlan.excluded_count`)
  has no known external consumer.
- **JSON wire format byte-stable.** Despite the internal
  `Confidence` enum replacement, every JSON record's
  `confidence` field still emits a string
  (`"high"|"medium"|"low"`) via `Confidence.value`. No
  consumer should break.
- **`docs touch` exit-code semantics unchanged.** Atomic
  multi-file failure exits 1 (any bad path) or 2 (malformed
  `.docs.toml`); a successful multi-file batch exits 0. The
  single-file behaviour is unchanged from 1.3.0 — the
  new contract surface is purely additive for multi-file
  invocations.

## 1.3.0 — 2026-05-25

M8: the adoption workflow becomes agent-driveable. A single
layered exclusion surface (`--exclude` / `[exclude]` /
`.docsignore`) replaces the M7 "everything walks" semantic;
the migrate plan grows triage flags (`--summary`,
`--only ambiguous`, `--group-by`) and a default footer
summary; non-Markdown root siblings surface in the plan; and
`docs new --body-from` closes the read-before-write friction
in agent flows. The bundled skill gains a substantial
adoption playbook + a starter `.docs.toml` template.

Per the post-M8 batched publish (M9), 1.3.0 ships locally
only — the public PyPI release is the same 1.3.0 number,
batching the M6 + M7 + M8 surface into one publish event.

### Added

- **`--exclude PATTERN`** (M8 — F3) on `docs migrate`, `docs
  index`, `docs check`, `docs list`. Repeatable; supports
  gitignore-flavoured globs (`*` / `**` / trailing-`/` /
  leading-`/`). Layered on top of `[exclude]` config and
  `.docsignore`.
- **`[exclude]` table in `.docs.toml`** (M8 — F3). Three
  keys: `dirs = [...]` (directory-name matches at any
  depth), `globs = [...]` (gitignore-flavoured patterns),
  `exts = [...]` (extension matches).
- **`.docsignore`** at the tree root (M8 — F3). One file
  only — nested files are NOT consulted (OQ-B). One
  pattern per line; gitignore-flavoured syntax subset
  (comments, blanks, `**`, `*`, `?`, trailing-`/`,
  leading-`/`, `!` negation, bare-pattern any-depth match).
- **`--exclude-ext EXTS`** (M8 — F3) on `docs migrate`.
  Comma-separated list of extensions to suppress from the
  non-Markdown sibling footer and from any exclude-predicate
  evaluation.
- **`--summary` triage mode** (M8 — F6) on `docs migrate`.
  One tabular line per file (`path  role  conf  notes`).
  Mutually exclusive with `--json` (argparse-enforced).
- **`--only ambiguous` filter** (M8 — F6) on `docs migrate`.
  Drops the high-confidence-no-ambiguity rows from the
  per-file plan. Composes with `--summary` and `--group-by`.
- **`--group-by role|confidence`** (M8 — F6) on `docs migrate`.
  Sorts the per-file plan by role (alphabetical) or by
  confidence (`high → medium → low`).
- **Default plan-footer summary** (M8 — F6). Every
  `docs migrate` dry-run emits four anchored tokens after
  the per-file block: `summary:`, `roles:`, `confidence:`,
  `ambiguities:`. Always present, even on an empty plan.
- **Non-Markdown root-sibling surfacing** (M8 — F7). The
  `docs migrate` dry-run footer surfaces non-`.md` siblings
  at the migration root as `<N> non-Markdown siblings at
  root not considered: <names>` so an adopting agent sees
  binaries referenced from prose. Suppressed entirely when
  `--exclude-ext` filters the list to empty.
- **`docs new --body-from <PATH|->`** (M8 — F9). Reads body
  content from a file or stdin and appends it under the
  scaffolded frontmatter. Atomic, one Bash call.
  Conservative refusal heuristic (OQ-E): the first 20 body
  lines are scanned for `^[A-Z][A-Za-z-]+:\s` and the call
  exits 2 if any match — agents must pass body content
  only; `docs new` owns the frontmatter.
- **Adoption playbook** at
  `src/docs_cli/skill/references/adoption-playbook.md` (M8
  — F8). Six-step procedural deep-dive: dry-run → triage →
  `.docs.toml` → iterate → apply → verify. Includes a
  worked example and a pitfalls subsection.
- **`.docs.toml` template** at
  `src/docs_cli/skill/references/docs-toml-template.toml`
  (M8 — F8). Commented starter for `[exclude]`,
  `[migrate]`, `[vocabulary]` (+ `[project]` /
  `[archive]`); every example line commented out.
- **SKILL.md adoption pointer + trigger phrases** (M8 — F8).
  Description gains four adoption-flow phrases ("adopt this
  directory", "migrate this folder", "bring this into docs
  convention", "import existing markdown specs"). A new
  one-line pointer block redirects to
  `references/adoption-playbook.md` near the verb table.

### Changed

- **Migrate carve-out widened** (M8 — OQ1). A `.docs.toml`
  carrying `[exclude]` is accepted by `docs migrate` even
  alongside the M7 managed-marker sections (`[project]` /
  `[archive]` / `[vocabulary]`). The operator's explicit
  signal "use migrate to triage / re-migrate this managed
  tree but skip the listed paths".
- **`_SKILL_RELATIVE_FILES` extended** to include
  `use-cases.md` (a pre-existing bundle file `install-skill
  --copy` previously missed because it walked the bundle
  via this very tuple) plus the two M8 new references.

### Notes

- M6 + M7 + M8 are batched into a single PyPI publish event
  in M9 (per operator OQ-C). The on-disk Markdown
  convention is otherwise stable; the M7 `Lifecycle:`
  rename is a one-time keyword change with no backward-
  compat alias.
- `MigrationPlan` grows three optional human-output-only
  fields (`excluded_count`, `excluded_breakdown`,
  `suppressed_exts`) per OQ1 — OMITTED from
  `migration_to_json` so the JSON schema stays flat,
  mirroring the M7 `multi_project_hints` precedent.

## 1.2.0 — 2026-05-25

The first breaking convention-schema release. Renames the
controlled-vocab lifecycle key from `Status:` to `Lifecycle:`;
broadens role inference; normalises project names and archive
moves. Per the post-M8 batched publish (M9), 1.2.0 ships
locally only — the public PyPI release is 1.3.0, batching the
M6 + M7 + M8 surface together.

### Changed (breaking)

- **Controlled-vocab field rename (M7 — F0).** `Status:` →
  `Lifecycle:` in the metadata block. A pre-existing
  `Status:` line is now a free-form extra field, preserved
  through `docs migrate` into the `## Migrated metadata` body
  section as `Migrated-Status:`. The `[vocabulary] add_statuses`
  config key is renamed `add_lifecycles`. `docs list --status`
  is renamed `docs list --lifecycle`. The `--json` schema field
  `status` is renamed `lifecycle` in both `docs list` and
  `docs migrate`. No backward-compat alias.

### Added

- **Medium confidence (M7 — OQ-D).**
  `FileMigration.confidence` adds a third value `"medium"`
  between `"high"` and `"low"`. Derived inference signals
  (H1 content, section-header patterns, sibling-set
  defaulting, non-role-suffix stripping, the `_M\d+`
  milestone-number pattern) return medium. `docs check`
  treats medium-confidence inferences as warnings (exit 1),
  not errors. New `docs check` rule key
  `medium-confidence-inference`.
- **Role vocab additions (M7 — F10 / OQ-A).** 7 new core
  roles: `implementation`, `sketch`, `outline`, `memo`,
  `brief`, `template`, `example`. The INDEX renderer
  positions them between `idea` and `notes`.
- **Project-name normalisation (M7 — F11).** `docs migrate`
  now normalises inferred project values to lowercase-kebab
  (TitleCase / SNAKE_UPPER / letter-to-digit / mixed
  underscore all rejoin with `-`); digit-after-digit is
  preserved so `bugs-2026-01-26` survives intact. The
  original is surfaced inline as `project: foo-bar-baz
  (normalised from "FooBarBaz")` once at the top of the
  human plan when normalisation changed the value.
- **Per-file archive-move dates (M7 — F4).** `docs migrate`
  proposes archive normalisations using each file's
  `Updated:` (or mtime fall-back) per file instead of a
  single migration-run default. `--date` continues to
  override globally.
- **Multi-project hints (M7 — F5).** `docs migrate` surfaces
  a `hint: …` line in the plan footer when an immediate
  subdir's longest-common filename prefix differs from the
  parent project and the subdir holds ≥ 5 `.md` files.
- **`--config-project NAME` (M7 — F5).** New CLI flag on
  `docs migrate`; overrides the inferred project for the
  run, bypasses normalisation, suppresses hint emission. The
  persistent equivalent is `[migrate] project_name = "…"` in
  `.docs.toml`.
- **`[migrate] role_suffixes` (M7 — F1).** New `.docs.toml`
  map letting an operator teach `docs migrate` a custom
  per-tree suffix → role mapping (extends the built-in map).
- **Broadened role inference (M7 — F1 / F10 / F12).**
  `infer_role` now tokenises on case-transition boundaries
  (`MyPlan` → suffix `plan`), recognises a trailing
  `_M\d+` pattern as `milestone` (medium), strips
  `_v\d+`/`_Draft`/`_Ready` non-role suffixes and re-tries
  (medium), and at the plan layer infers from H1
  trailing-word, section-header patterns, and sibling-set
  defaulting at ≥ 60% / ≥ 5 (medium).

### Notes

- The 2026-05-24 multi-tree trial (501 .md files across
  25 trees) measured 25.3% high-confidence under the M4
  inference. M7's broadened inference brings the sanitised
  `snake-medium` fixture to ~88% high+medium.
- `docs migrate` now narrows the refusal of a `.docs.toml`
  to managed-root markers (`[project]`, `[archive]`,
  `[vocabulary]`). A `.docs.toml` containing only a
  `[migrate]` section (e.g. `project_name = "foo"`) is read
  without refusing — the foreign-tree migration-sidecar
  shape.

## 1.1.0 — UNRELEASED

The first PyPI release. Distribution name is `docs-cli`; the console-script
remains `docs`. No on-disk-convention changes.

### Added

- **PyPI distribution.** The CLI now ships as `docs-cli` on PyPI:
  `pip install docs-cli` lands `docs` on PATH via the
  `[project.scripts] docs = "docs_cli.cli:main"` entry point. The
  bundled Claude Code skill rides inside the wheel as package data
  under `docs_cli/skill/`, removing the previous requirement to clone
  the repo to use the skill.
- **`docs install-skill` verb (M6).** New subcommand that materialises
  the bundled skill onto a host. Flags: `--dest DIR` (default
  `~/.claude/skills/docs/`), `--copy` (default) / `--symlink`,
  `--force`, `--quiet`. Idempotent: a no-op when the destination is
  already byte-identical to the bundled source. Refuses `--symlink`
  on a wheel install (where the bundled skill lives under
  `site-packages` and could be replaced by a `pip install --upgrade`).
- **Global `--version` flag.** `docs --version` prints `docs 1.1.0`
  and exits 0.

### Changed

- **Package layout.** The single-file CLI moved from `bin/docs` to
  `src/docs_cli/cli.py`. The bundled skill moved from `skills/docs/`
  to `src/docs_cli/skill/`. Tests import the CLI via
  `from docs_cli import cli` (or `from docs import …` via the
  conftest's `sys.modules` alias).
- **Repository identity.** The local checkout and the GitHub repo
  both moved to `docs-cli` (was `docs`); the on-disk Markdown
  convention is unchanged (`Project: docs` stays `docs`).
- **Build backend.** `pyproject.toml` declares hatchling as the build
  backend; classifiers bumped from Alpha to Beta and now list Python
  3.11 / 3.12 / 3.13.

### Removed

- `bin/docs` — replaced by the editable-install / wheel entry point.
- Top-level `skills/docs/` — replaced by `src/docs_cli/skill/` (the
  in-tree source of truth shipped as wheel package data).
- `[tool.ruff] extend-include = ["bin/docs"]` and
  `[tool.mypy] scripts_are_modules = true` — no longer needed; the
  CLI is a regular package module.

## 1.0.0 — 2026-05-22

v1 complete: M1-M5 shipped across 2026-05-20 → 2026-05-22.

### Added

- M1 — Parser, walker, INDEX renderer, `docs index`, config loading.
- M2 — Mutating verbs `new`, `archive`, `mv`, `touch`.
- M3 — Validation (`check`) and query (`list`); INDEX regrouped by
  Project then Role.
- M4 — Migration helper `docs migrate` for adopting foreign Markdown
  trees into the convention (dry-run by default).
- M5 — Claude Code skill that drives the verbs automatically when an
  agent does documentation work in a `docs`-managed tree; bundled
  spec references (`convention.md`, `cli.md`) ship alongside.
