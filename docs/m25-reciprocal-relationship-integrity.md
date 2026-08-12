# M25 — Reciprocal relationship integrity and docs relate

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-08-12

Related:
- child-of: plan.md
- parent-of: m25-reciprocal-relationship-integrity-impl.md
- implements: charter.md
- pairs-with: m25-reciprocal-relationship-integrity-impl.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: test-strategy.md
- pairs-with: status.md
- references: feedback-log.md
- precedes: m26-safe-archive-selection.md
- required-by: m29-pypi-publish-2-0-0.md

## Overview

- Milestone: M25 (v2.0 train)
- Title: Reciprocal relationship integrity and `docs relate`
- Surface: define three useful reciprocal relationship pairs, make missing
  inverses a hard `docs check` error, and add a narrow two-document
  `docs relate add/remove` mutation for explicit repair. The mutation works on
  active docs and, with a reasoned audit record, on archived endpoints.
- Progress: **Active / implementation-complete — all ten TDD phases done
  (Phases 1–4 2026-08-11 amended 2026-08-12 on `m25/phases-1-4`; Phases
  5–10 2026-08-12 on `m25/phases-5-10`). Stays `Lifecycle: active` until
  the M29 publish closeout.** The contract is
  frozen in *Decisions (Phase 1 — BINDING)* below and in `cli.md` /
  `convention.md`; all five open questions are RESOLVED. The RED suite is
  written (+121 items) over ten committed `reciprocal-*` fixture trees, and
  the RED baseline is captured: **757 collected, 87 failed, 670 passed**,
  every RED matching its classified reason and the pre-existing 636 all still
  GREEN. Step 1 has been through a same-instance audit and an independent
  fresh-eyes review (**no blockers**); the review's two operator-binding
  contract amendments — the **self-edge exemption** and **canonical path
  matching** — are folded into D2 below. **Step 2 (Phases 5–10) is
  complete on `m25/phases-5-10`:** the implementation, the
  `docs relate add|remove` CLI, the bundled-skill row and use-case catalog,
  the `UNRELEASED` CHANGELOG (**no version bump** — the package stays
  1.8.0), and eight conductor-resolved `cli.md` corrections all landed; the
  full suite is **757 passed, 0 failed** with every pre-existing test id
  proven still GREEN by `comm`; and the eight-flow dogfood ran unattended on
  a throwaway copy of this tree (detect → repair → re-check, audited
  archived repair, 1 of 46 archived files touched). One Step-1 test
  assertion was corrected under operator approval — it was unsatisfiable
  alongside another test in the same file; the replacement is stronger and
  the shipped behaviour was not changed to accommodate it. **M26 is ready to
  prepare; a Step-3 `/simplify` pass runs against this implementation
  next.**

### Goal

Make the `Related:` graph useful to the agent working in a document without
turning relationships into archive authorization. From any milestone, an agent
should be able to see adjacent execution order, durable prerequisites, and
current blockers. `docs check` should identify an incomplete reciprocal edge
precisely, and `docs relate` should let the agent repair or remove the intended
pair without hand-editing either endpoint.

### Primary use-case acceptance

- **Navigate the work locally.** A reader of one milestone can follow
  `precedes`/`follows`, distinguish a durable `depends-on` relationship from a
  transient `blocked-by` relationship, and reach the reciprocal context.
- **Upgrade and repair an existing tree.** `docs check` names the source,
  verb, target, and exact missing inverse. The agent judges whether the source
  edge is valid, then explicitly adds the inverse or removes the invalid pair.
- **Repair history without rewriting history.** When an endpoint is archived,
  only the exact recognized `Related:` bullets and the audit metadata required
  for the repair change; lifecycle, archive location, original
  `Archived-reason:`, unrelated metadata, and prose remain intact.

## Binding scope

### D1 — Reciprocal relationship vocabulary

The recognized inverse map is:

| Forward | Reverse | Meaning |
|---|---|---|
| `precedes` | `follows` | Adjacent execution order |
| `depends-on` | `required-by` | Durable planned prerequisite |
| `blocks` | `blocked-by` | Current inability to proceed |

The inverse is symmetric in both directions. Sequence, dependency, and
blocking stay distinct. None implies archive membership. Other `Related:`
verbs remain free-form and do not gain reciprocal validation.

### D2 — Hard `missing-inverse` validation

`docs check` emits an error when a recognized edge lacks its exact inverse.
The rule applies only when both endpoints are included by the effective tree
predicate, successfully parsed managed Markdown docs, and the target already
passes existing resolution checks. Existing `broken-ref`, exclusion,
malformed-doc, lifecycle, and vocabulary rules retain ownership of their
cases. The finding must be actionable in both human and JSON output and must
not invent whether the correct repair is add or remove.

### D3 — Explicit two-endpoint `docs relate add/remove`

Add a narrow relationship mutation namespace. The setup recommendation to
freeze in Phase 1 is:

```text
docs relate add SOURCE VERB TARGET [--reason TEXT] [--date YYYY-MM-DD]
docs relate remove SOURCE VERB TARGET [--reason TEXT] [--date YYYY-MM-DD]
```

The command accepts only the six recognized verbs, infers the inverse, edits
both endpoints as one coordinated operation, is idempotent, supports
`--dry-run`, refreshes `INDEX.md` once, and has machine-readable output. It is
not a generic `Related:` editor and does not bulk-repair a tree.

### D4 — Controlled archived-endpoint repair

An add/remove touching an archived endpoint requires an explicit reason. The
only permitted archived changes are the exact reciprocal relationship bullets,
`Updated:`, and a dated/reasoned repeatable `Revision:` audit record. The
original `Archived-reason:` remains the explanation for entry into the archive.
Lifecycle, role, project, location, unrelated edges/metadata, and prose are
byte-identical. Active endpoints receive the relationship edit and normal
`Updated:` bump without an archive revision record unless Phase 1 deliberately
pins one common audit shape.

### D5 — Compatibility and upgrade guidance

Document that trees with one-sided recognized edges can begin failing
`docs check` after upgrade. Human and JSON findings carry enough information
for an agent to choose add-vs-remove. CLI help, `cli.md`, `convention.md`, the
bundled skill, CHANGELOG, and upgrade examples stay in surface parity. No
automatic conversion of free-form edges occurs.

## Out of scope

- Bulk auto-repair or automatic choice of which edge is true.
- A graph database, graph query/rendering command, or `archives-with` verb.
- Cycle detection, sequence cardinality, tracker-order agreement, or deriving
  one relationship class from another.
- Coupling `blocks`/`blocked-by` to `Lifecycle: blocked`.
- General archived-document editing.
- Archive-selection behavior (M26) and Markdown body links (M27/M28).
- Agent Playbook Suite changes; that repository consumes the released v2.0
  behavior after M29.

## Current state analysis

- `Doc.related` already preserves ordered `(verb, target)` pairs and
  `parse_metadata_block` understands the `Related:` bullet group.
- `check_doc` owns target-level `broken-ref` validation, while `check_tree`
  currently validates documents independently and has no cross-document
  reciprocal pass.
- `rewrite_related_refs` can rewrite targets but cannot add/remove a typed edge.
- `set_metadata_field` edits scalar metadata; repeatable `Revision:` history
  needs a minimal group editor rather than lossy full serialization.
- `atomic_write` provides per-file durability. M25 must define and test the
  two-file failure contract before claiming coordinated atomicity.
- Archived docs are normally immutable except narrow move-driven `Related:`
  rewrites from M18. M25 adds a second, explicitly requested and audited,
  relationship-only exception.
- The live docs tree already uses reciprocal `precedes/follows` and
  `depends-on/required-by` edges for M25–M29, providing Phase-9 dogfood data.

## Deliverables

- [x] D1 inverse vocabulary and semantics documented (Phase 1, 2026-08-11 —
      `convention.md` › *Reciprocal relationship verbs*).
- [x] D2 hard `missing-inverse` rule in human and JSON `docs check` output
      (Phase 6, 2026-08-12 — `reciprocity_findings` interleaved into
      `check_tree`; no new JSON field).
- [x] D3 idempotent, validate-all-first `docs relate add/remove` for active
      docs (Phases 6–7, 2026-08-12).
- [x] D4 reasoned, narrowly audited archived-endpoint repair (Phases 6–7,
      2026-08-12 — `Revision:` group, three-item allowed byte set, audit
      asymmetry).
- [x] D5 upgrade guidance, CLI/bundled-skill parity, and release notes
      (Phase 7, 2026-08-12 — `cli.md` / `convention.md` / bundled mirrors /
      `SKILL.md` / `CHANGELOG.md` `UNRELEASED`).
- [x] RED/GREEN unit, integration, CLI, failure-injection, and dogfood coverage
      (RED half — Phases 2–4, 2026-08-11; GREEN half — Phase 8, 2026-08-12,
      757 passed with zero pre-existing regressions; dogfood — Phase 9,
      2026-08-12, eight flows on a throwaway tree copy).

## TDD implementation plan

### Phase 1 — Define Contract

- Objective: freeze the inverse map, finding schema/message, command grammar,
  output modes, idempotency, two-file failure behavior, `Revision:` encoding,
  archived reason/date rules, and v2.0 compatibility language.
- Files: `docs/cli.md`, `docs/convention.md`, this milestone, and the bundled
  reference mirrors. Contract-level function signatures are frozen in
  *Decisions* below rather than stubbed in `src/docs_cli/cli.py` — see the
  logged deviation there; Phase 1 makes **zero** `cli.py` edits.
- Exit: every remaining open question below is resolved; specs and signatures
  are internally consistent; no business logic lands.

### Phase 2 — Write Tests (RED)

- Objective: express inverse validation and two-endpoint mutation behavior
  before implementation.
- Files: `tests/test_check.py`, `tests/test_cli_check.py`, new
  `tests/test_cli_relate.py`, plus focused parser/editor tests as needed.
- Exit: happy, idempotent, missing-inverse, malformed, excluded, unknown-verb,
  dry-run/JSON, active/archive, and injected-second-write-failure cases are RED
  only for missing M25 behavior.

### Phase 3 — Create Data/Fixtures

- Objective: provide small trees for every relationship direction and archived
  repair boundary.
- Files: new fixtures under `tests/fixtures/trees/` for clean reciprocal,
  missing inverse, excluded/malformed endpoint, and active↔archived pairs.
- Exit: fixtures parse deterministically and isolate one semantic per case.

### Phase 4 — Run Tests (RED Baseline)

- Objective: prove the new tests fail for the intended missing behavior.
- Files: implementation log only.
- Exit: full baseline captured; no collection errors, tracebacks, or unrelated
  regressions; GREEN-at-baseline locks classified explicitly.

### Phase 5 — Update Base Interfaces

- Objective: add inverse lookup, relationship-edit planning models/helpers,
  finding context, and revision-audit primitives without completing behavior.
- Files: `src/docs_cli/cli.py` and unit tests.
- Exit: interfaces typecheck; tests remain honestly RED at the behavior seam.

### Phase 6 — Implement Offline/Core Path

- Objective: implement reciprocal tree validation and validate-all-first,
  idempotent paired edits including the archived audit boundary.
- Files: `src/docs_cli/cli.py`, core/editor/check tests.
- Exit: core tests GREEN; injected failures satisfy the Phase-1 contract; no
  unrelated bytes change.

### Phase 7 — Update Tool/Wrapper Layer

- Objective: wire `docs relate add/remove`, help, human/JSON/dry-run output,
  exit codes, one final reindex, version/CHANGELOG, and bundled skill surface.
- Files: CLI parser/dispatch, `docs/cli.md`, `docs/convention.md`,
  `src/docs_cli/skill/`, `CHANGELOG.md`, packaging/version pins.
- Exit: subprocess tests and surface-parity checks GREEN.

### Phase 8 — Run Tests (GREEN)

- Objective: run focused and full suites plus lint, format, types, reference
  byte-identity, and docs integrity.
- Files: implementation log only unless a real defect is found.
- Exit: all gates GREEN with exact counts recorded.

### Phase 9 — Integrate / Accept / Dogfood

- Objective: exercise the upgrade workflow on a throwaway copy of this docs
  tree: detect a deliberately removed inverse, repair it with `docs relate`,
  remove an invalid pair, and repair an archived endpoint with an audit reason.
- Files: throwaway tree only; committed docs record evidence.
- Exit: use-case flows pass unattended, `docs check` returns clean afterward,
  and unrelated archived bytes remain identical.

### Phase 10 — Quality, Docs, Refactor

- Objective: simplify the implementation, close surface/upgrade docs, update
  the shipped use-case catalog, and write milestone completion summaries.
- Files: code/docs as justified, milestone and implementation log.
- Exit: full gate GREEN; no placeholders; M25 implementation-complete and ready
  to hand off to M26 while remaining live until the M29 publish closeout.

## Phase checklist

- [x] Phase 1 — Define Contract
- [x] Phase 2 — Write Tests (RED)
- [x] Phase 3 — Create Data/Fixtures
- [x] Phase 4 — Run Tests (RED Baseline)
- [x] Phase 5 — Update Base Interfaces
- [x] Phase 6 — Implement Offline/Core Path
- [x] Phase 7 — Update Tool/Wrapper Layer
- [x] Phase 8 — Run Tests (GREEN)
- [x] Phase 9 — Integrate / Accept / Dogfood
- [x] Phase 10 — Quality, Docs, Refactor

## Decisions carried from discovery

- The tracker remains the complete authoritative view; individual docs provide
  direct local context.
- The three inverse pairs and their distinct meanings are binding.
- Missing inverses are errors, not compatibility warnings, only when both
  endpoints are included and parseable.
- The repair is an explicit two-document add/remove operation; bulk repair is
  deferred.
- Archived relationship repair is permitted only through the narrow audited
  exception described in D4.
- Relationships never grant archive authorization.

## Decisions (Phase 1 — BINDING)

Frozen 2026-08-11. The authoritative surface lives in `cli.md` (`docs check`
› *Reciprocal-edge validation*, and the `docs relate` section) and
`convention.md` (*Reciprocal relationship verbs*, *Optional fields*,
*Archive subtree* › *Audited relationship repair*). This section records the
decisions and their rationale; where the two disagree, the specs win.

### D1 — Inverse map (BINDING)

`precedes`↔`follows`, `depends-on`↔`required-by`, `blocks`↔`blocked-by`.
Symmetric in both directions; exactly six recognized verbs. Matching is
**case-sensitive exact match**, mirroring the `add_fields` precedent.

Every other verb stays free-form with **no** reciprocal validation.
`supersedes`/`superseded-by` and `child-of`/`parent-of` are named
explicitly as deliberate **non**-members so no reader infers symmetry from
a verb's shape: promoting them would retroactively break existing trees for
no navigational gain.

### D2 — `missing-inverse` finding (BINDING)

- Rule id `missing-inverse`, severity `error`, exit code 2.
- The finding attaches to the **source** doc — the one declaring the
  un-reciprocated edge — consistent with `broken-ref` blaming the referrer.
  (Resolution of OQ-B.)
- Frozen single-line message:
  `Related: '<verb>: <target-rel>' has no inverse; <target-rel> must declare '<inverse>: <source-rel>' (or remove the edge)`.
  It names source, verb, target, and the exact missing inverse, and offers
  both repairs without choosing between them.
- **No new JSON fields.** The record stays exactly
  `{path, severity, rule, message}` — the key set `tests/test_cli_check.py`
  already pins for every record.
- Applicability (all six must hold): both endpoints walked under the
  effective predicate; the target resolves to a file (else `broken-ref`
  owns it); the target is a managed `.md` doc in the walked set; **both**
  texts survive `parse_metadata_block` (else `malformed` owns it); the
  target is **not the source itself**; the inverse bullet is absent.
  Reciprocity depends on metadata-block parseability **only** — a source
  that also trips `bad-vocab` or `bad-date` is still reciprocity-checked.
- **Post-review contract amendment A (2026-08-12, operator-binding) — the
  self-edge exemption.** Condition 5 above is new. A recognized edge whose
  target resolves to the declaring document is exempt from the rule.
  Rationale: `docs relate` refuses a self-edge outright (exit 2,
  `SOURCE and TARGET must be different documents`), so without the
  exemption `docs check` would name a repair the repair verb declines to
  perform — an unfixable finding. A self-referential edge also has no
  second document whose context could be completed, which is the whole
  point of the rule. Consistent with the "no cycle or conflict detection"
  non-goal.
- **Post-review contract amendment B (2026-08-12, operator-binding) —
  canonical path matching.** Both the source edge's target and each
  candidate inverse bullet are resolved to their canonical root-relative
  POSIX form **before** comparison, matching how `broken-ref` already
  resolves via `(root / target).is_file()`. `precedes: ./b.md`,
  `precedes: sub/../b.md`, and `precedes: b.md` are one edge; an inverse
  spelled `follows: ./a.md` satisfies `precedes: b.md`. Rationale: a
  genuinely reciprocal tree must not fail a *hard* check over a `./`
  prefix — a purely textual match would turn a cosmetic spelling into an
  exit-2 error with no opt-out. The finding's message still quotes the
  canonical form, so the repair it names is the one `docs relate` writes.
  The per-triple dedupe key uses the canonical target too.
- Archived endpoints are in scope (they are walked). This is precisely why
  D4 exists.
- One finding per distinct `(source, verb, target)` triple, even when the
  bullet is duplicated.
- **No opt-out knob** (no `[check] reciprocal = false`): the milestone binds
  "errors, not compatibility warnings". `--exclude` / `.docsignore` remain
  the only coarse escape. Instead, `cli.md`, `convention.md`, and the
  CHANGELOG carry an explicit "upgrading from 1.x" paragraph naming a bare
  `blocked-by:` as the most likely legacy offender — and the pre-M25
  `convention.md` recommendation that produced it (pair `Lifecycle: blocked`
  with a one-sided `blocked-by`) is **withdrawn in the same edit**.
  (Resolution of OQ-D.)
- No cycle detection and no conflict detection: `A precedes B` together with
  `A follows B` is accepted (out of scope per this milestone).

### D3 — `docs relate` grammar and output (BINDING)

`docs relate add|remove SOURCE VERB TARGET [--reason TEXT] [--date YYYY-MM-DD] [--json] [--dry-run] [--quiet] [--root DIR]`.

- A **verb namespace** with nested subverbs, shaped like `docs project`.
  `add`/`remove` inherit the shared `--root`/`--quiet`/`--dry-run` parent
  and declare `--json` locally (as `check`/`list`/`migrate` do).
- Positional order `SOURCE VERB TARGET` reads as a sentence and is
  symmetric: `relate add b.md follows a.md` produces a tree byte-identical
  to `relate add a.md precedes b.md`.
- **Endpoint resolution (OQ-A, operator-confirmed).** An absolute path is
  used as-is. A relative path resolves **root-relative first**, falling back
  to **cwd-relative** only when the root-relative form is not a file. Both
  endpoints must resolve under the root. Every message and every JSON field
  about a **resolved** endpoint names the **root-relative POSIX** form; a
  *pre-resolution* refusal necessarily names the path it was still working
  with (R5, Phase 7 — `file not found:` names the root-relative candidate
  for a relative argument, the outside-root refusal the resolved path).
  Root-relative-first is chosen so the path an agent copies out of a
  `missing-inverse` finding resolves without translation. An **excluded**
  endpoint is deliberately allowed: `relate` runs no whole-tree pre-flight
  and an explicitly named endpoint beats a coarse exclusion (R9, Phase 7).
- **Idempotency.** `add` writes only the missing half (or nothing); `remove`
  removes only the present half (or nothing). A fully-satisfied invocation
  writes zero bytes: no `Updated:` bump, no `Revision:` entry, no reindex,
  exit 0.
- **One reindex**, at end, only when something changed and not `--dry-run`,
  honouring `[exclude]`/`.docsignore` (the M14 — A6 shape).
- **`relate` does not gate on whole-tree health.** Unlike `archive`/`mv`, it
  validates only its two endpoints — a whole-tree pre-flight would make
  repair impossible in exactly the broken tree the verb exists to repair. A
  malformed *sibling* can still fail the end-of-run reindex (exit 2 after
  the repair landed), matching `touch`/`project set`.
- **Machine output (Q1).** One stable operation-plan record on stdout, the
  **same shape** for `--dry-run` and for a real apply, so preview and apply
  are diffable. `edits` is always `[source, target]` in that order and
  carries `present_before`/`present_after` — the "before and after edges"
  the open question asked for.
- Exit codes: 0 success / no-op / dry-run; 1 endpoint missing, malformed, or
  outside the root; 2 for every hard refusal (see `cli.md`).

### D4 — Archived-endpoint repair (BINDING)

- **`--reason` is required whenever either named endpoint lies under the
  archive subtree** (OQ-C, operator-confirmed), evaluated in the
  validate-all-first pass **before** any planning — predictable rather than
  plan-dependent. An idempotent no-op naming an archived endpoint still
  requires it, and still writes nothing.
- `--reason` must be a single non-empty line after stripping. A newline is
  refused (`--reason must be a single line`): structurally, a multi-line
  reason would terminate the metadata block and corrupt the archived doc. An
  empty/whitespace-only value is refused separately
  (`--reason must not be empty`) — an empty audit record is indistinguishable
  from no record. `--reason` is accepted but unused on an all-active pair.
- The **only** bytes an archived endpoint may change: the one recognized
  `Related:` bullet, the `Updated:` value, and the `Revision:` group.
  Everything else — `Lifecycle: archived`, `Archived-reason:`, `Role:`,
  `Project:`, other edges, other metadata, H1, prose, location, and the
  trailing-newline state — is byte-identical.
- **`Revision:` encoding (Q2).** A repeatable bare-label bullet group at the
  end of the metadata block (after `Related:`, separated by one blank line —
  the shape the parser already accepts). One dated single-line bullet per
  real mutation, describing **this document's own** change, appended
  chronologically. The date is the SAME value written into `Updated:` —
  `--date` or today, rendered in the tree's `date_format`; "ISO-dated" here
  describes the **default** format, not a second hardcoded one (R7,
  Phase 7). Two date spellings in one file would be a defect:
  `- 2026-08-11: relate add 'follows: m26.md'; reason: complete the M25/M26 sequence pair`.
- `"Revision"` is added to the built-in always-allowed metadata label set in
  Phase 5. Otherwise any tree with `[vocabulary] add_fields` set would get
  an `unknown-field` warning on a label `docs relate` itself writes.
- **Audit asymmetry (Q4).** `Revision:` is appended **only** to archived
  endpoints; an active endpoint gets the edge plus the `Updated:` bump and
  nothing else — its history is the repository's. `Updated:` is bumped (to
  `--date`, default today, in the tree's `date_format`) on **every** endpoint
  whose bytes change and on **none** that do not.

### D5 — Coordinated-write failure contract (Q3, BINDING)

Five ordered stages; the first four write nothing: **validate all** →
**stage both complete texts in memory** → **re-validate the staged texts**
(a staged text that would not parse aborts before publishing) →
**writability pre-flight** on each changed endpoint (a read-only archive
refuses cleanly before any write, the common real failure, needing no
rollback) → **publish** source-then-target atomically, rolling every
already-published endpoint back on a later failure. A failed rollback is
reported as an explicit non-atomic admission naming the file and the edge
left behind, never swallowed.

Stated plainly in the spec: this is **best-effort staged publish +
rollback**, not a filesystem-wide transaction — two files cannot be renamed
atomically as a unit on POSIX. The contract is pinned by failure injection
rather than asserted.

**Both the publish and the rollback go through the module-level
`atomic_write`.** This is a binding part of D5, not an accident of the
tests: the rollback must inherit exactly the same tmpfile + fsync + rename
durability as the publish it is undoing — a restore written with a plain
`Path.write_text` could itself be torn by a crash, which is the failure the
rollback exists to prevent. It also keeps the seam monkeypatchable, which is
the only way the failure path is testable at all
(`tests/test_relate_plan.py` injects there).

### D6 — Version staging (Q5, BINDING — operator decision)

**The package version stays `1.8.0` for the whole of M25.** `pyproject.toml`
is **not** bumped, and the packaging version pins are not re-pinned or
renamed — they stay exactly as they are and stay GREEN. M25–M28 are all
**version-neutral**; **M29 performs the single bump to `2.0.0`** at publish
time. This supersedes the setup-time recommendation to decide the local bump
inside an implementation milestone: a four-milestone breaking train that
bumps early would carry a misleading local version through three more
milestones and force repeated pin churn.

CHANGELOG handling follows the repo's own precedent for unreleased work (see
`release-runbook.md` › the M9 worked example): M25's entries accumulate under
an **`UNRELEASED` heading carrying no invented version number**, which M29
renames and dates at the moment of upload. Phase 7 owns that edit; no
`## 2.0.0` header is created in M25.

### Frozen Phase-5 signatures (contract only — no code lands in Phase 1)

```python
# vocabulary
RECIPROCAL_INVERSES: Mapping[str, str]          # 6 entries, symmetric
RECIPROCAL_VERBS: frozenset[str]                # frozenset(RECIPROCAL_INVERSES)
def inverse_verb(verb: str) -> str | None

# editors — beside rewrite_related_refs, same surgical minimal-diff contract
def add_related_edge(text: str, verb: str, target: str) -> tuple[str, bool]
def remove_related_edge(text: str, verb: str, target: str) -> tuple[str, bool]
def append_revision_entry(text: str, entry: str) -> str

# validation — beside check_tree
def reciprocity_findings(
    entries: Sequence[tuple[Path, str]], root: Path
) -> dict[Path, list[Finding]]

# planning / apply — mirrors MigrationPlan / plan_migration / apply_migration
@dataclass(frozen=True)
class RelateEdit:
    path: Path; rel: str; archived: bool; edge: str
    original: str; new_text: str
    change: str                       # "added" | "removed" | "unchanged"
    present_before: bool; present_after: bool
    updated_bumped: bool; revision_appended: bool

@dataclass(frozen=True)
class RelatePlan:
    action: str; verb: str; inverse: str
    source_rel: str; target_rel: str
    reason: str | None; date_str: str
    edits: tuple[RelateEdit, ...]     # always (source, target)

class CoordinatedWriteError(OSError):
    rolled_back: bool
    published: tuple[str, ...]

def plan_relate(root: Path, config: Config, *, action: str, source: Path,
                verb: str, target: Path, reason: str | None,
                date_str: str) -> RelatePlan
def apply_relate_plan(plan: RelatePlan) -> None      # publish + rollback
def relate_plan_to_json(plan: RelatePlan, *, dry_run: bool,
                        applied: bool, index_refreshed: bool) -> dict[str, object]

# CLI
def _cmd_relate(args: argparse.Namespace) -> int
```

`check_tree` changes shape in Phase 5/6 to materialise the walk once and
interleave the two passes:

```python
entries = list(_iter_doc_texts(root, config, predicate=predicate))
recip = reciprocity_findings(entries, root)
for path, text in entries:
    findings.extend(check_doc(path, text, root, config, stale, today, stale_source))
    findings.extend(recip.get(path, ()))
```

Per-doc order becomes "`check_doc`'s findings, then any `missing-inverse`";
`check_tree`'s "errors before warnings" docstring sentence is corrected
accordingly rather than adding a resort (simpler, and nothing asserts
intra-doc severity order).

### Deviation from the Phase-1 file list (deliberate, logged)

Phase 1 above lists "contract-level function signatures in
`src/docs_cli/cli.py`" among its files. **Phase 1 makes zero `cli.py`
edits.** Adding stubs would change the Phase-4 subprocess RED reasons and
risk baseline behaviour, while the phase's own exit criterion is "no
business logic lands". The signatures are frozen above and in `cli.md`, and
land as real code in Phase 5. Approved deviation.

## Resolved questions (Q1–Q5, BINDING)

All five Phase-1 open questions are resolved. The originals are kept so the
decision trail reads end-to-end.

1. **Positional grammar and machine output.** RESOLVED → D3.
   `SOURCE VERB TARGET`; machine output is **one stable operation-plan
   record** shared by `--dry-run` and apply, naming both the before and
   after edges per endpoint (`present_before` / `present_after`).
2. **Repeatable `Revision:` representation.** RESOLVED → D4. A bare-label
   bullet group at the end of the metadata block, one dated single-line
   entry per real mutation carrying the action, the edge, and the operator's
   reason, in the tree's `date_format` (default ISO — see D4).
3. **Coordinated-write failure contract.** RESOLVED → D5. Stage and
   re-validate both complete texts, writability pre-flight, then publish
   with rollback; failure injection pins recovery; the spec states plainly
   that this is best-effort staged publish + rollback, not a
   filesystem-wide transaction.
4. **Active↔archived audit symmetry.** RESOLVED → D4. `--reason` required
   when **either** endpoint is archived (checked before planning, so a no-op
   still requires it); `Revision:` appended to archived endpoints only;
   `Updated:` bumped on every endpoint whose bytes change and on no other.
5. **Version staging.** RESOLVED → D6 (operator decision). The package
   **stays `1.8.0` through M25–M28**; **M29** performs the single bump to
   `2.0.0` at publish. M25 does not touch `pyproject.toml` or the packaging
   version pins.

Three further questions surfaced during Phase-1 planning and are resolved
in the same freeze: **OQ-A** endpoint-path precedence (→ D3,
operator-confirmed), **OQ-B** which doc a `missing-inverse` finding blames
(→ D2), and **OQ-D** whether the hard rule gets an opt-out knob (→ D2, it
does not).

## Testing and quality gate

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q
.venv/bin/docs check --root docs
```

Additional gates: `docs check --json` schema assertions, bundled
`cli.md`/`convention.md` byte identity, `docs --help`/`docs relate --help`
surface parity, archive byte-identity checks, and the live INDEX snapshot.

## Success criteria

All six are **met** as of 2026-08-12 (Phase 10). Evidence lives in the
implementation log's Phase-8/9/10 records.

- [x] **Every recognized relationship pair is locally navigable in both
      directions.** Six verbs in three symmetric pairs; `inverse_verb`
      applied twice is the identity, parametrized over all six directions
      (`test_check_tree_all_three_pairs_both_directions`).
- [x] **A one-sided recognized edge makes `docs check` exit 2 with one
      actionable `missing-inverse` finding; excluded/malformed/non-managed
      endpoints do not produce a misleading inverse finding.** Proven on
      committed fixture trees for each exemption, and dogfooded on a copy of
      this tree (Phase 9 flow 2: exactly one finding, naming source, verb,
      target, and the exact inverse). The inverse must point **back** at the
      source, not merely exist.
- [x] **`docs relate add/remove` changes exactly the intended pair, is
      idempotent, previews without writing, and never leaves a deliberate
      half-pair after a handled failure.** A repeat invocation is
      byte-neutral tree-wide; `--dry-run` changes zero bytes including
      `INDEX.md`; the rollback is pinned end-to-end by a read-only-directory
      injection and at the unit seam for the `ROLLBACK FAILED` half.
- [x] **Archived repair preserves lifecycle/history and produces a dated
      reason audit with no unrelated byte changes.** Phase-9 flow 5: the
      complete diff is the `Updated:` value, one `Related:` bullet, and the
      `Revision:` group; the body's sha256 is identical; a second reasoned
      repair appends under the **one** `Revision:` label. Flow 6: 1 of 46
      archived files differs.
- [x] **Existing free-form verbs and existing `broken-ref` ownership stay
      compatible.** The supersedes trap is locked; all 18 pre-M25 fixture
      trees gain no finding (derived from the directory, so future trees are
      covered for free); zero pre-existing regressions, proven by `comm`
      against the 636 ids at `3dca105`.
- [x] **Full quality and dogfood gates are GREEN, leaving M26 ready to
      prepare next.** 757 passed; ruff / format / mypy / `docs check --root
      docs` clean; mirrors and the INDEX snapshot in lockstep; version still
      1.8.0 per D6.
