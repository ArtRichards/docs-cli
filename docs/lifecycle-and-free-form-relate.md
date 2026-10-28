# M30 — Lifecycle verb and free-form `docs relate`

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-10-28

Related:
- child-of: milestone-plan.md
- implements: charter.md
- pairs-with: lifecycle-and-free-form-relate-impl.md
- pairs-with: lifecycle-and-free-form-relate-test-matrix.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: test-strategy.md
- pairs-with: status.md
- references: feedback-log.md

## Overview

- Milestone: M30 (first post-2.0 milestone; first under the canonical tracker)
- Slug: `lifecycle-and-free-form-relate` — tracker identity and branch root
  (`lifecycle-and-free-form-relate/milestone-setup`, …)
- Title: Lifecycle verb and free-form `docs relate`
- Surface: a new `docs lifecycle` verb for top-level lifecycle transitions,
  and `docs relate add|remove` widened to free-form verbs, written one-sided;
  and `parse()` made to honour the tree's config — vocabulary extensions and
  `date_format` — so both work on every configured tree (D10).
- Test Matrix:
  [lifecycle-and-free-form-relate-test-matrix.md](lifecycle-and-free-form-relate-test-matrix.md)
- Implementation log:
  [lifecycle-and-free-form-relate-impl.md](lifecycle-and-free-form-relate-impl.md)
- Progress: setup complete and Step 0 reviewed; Step 1 (Phases 1–4)
  complete, reviewed and synced — the contract is frozen in *Decisions
  (Phase 1 — BINDING)* and the RED baseline recorded; Step 2 (Phases 5–10)
  in progress — Phases 5–9 complete. The narrative, evidence headline and
  per-phase results live in the implementation log.

### Identity note

The tracker identity is the semantic slug `lifecycle-and-free-form-relate`;
`M30` is a prose label only, continuing the M1–M29 history so that
cross-references into the archive stay readable. Files, branches and the
tracker cell use the slug, and execution order lives in the tracker's
`Order` column (100), not in the label. The tracker has a single row with no
dependencies and no adjacent cohort, so this milestone carries no
`precedes` / `follows` or `depends-on` / `required-by` edges — verified at
setup, not assumed.

### Goal

Every metadata edit a suite workflow prescribes has a verb, so an agent holding
the bundled `docs` skill never meets a step it can complete only by
hand-editing a metadata block or asking the operator for an exception.

### Primary use-case acceptance

An agent running `create-milestones` against a downstream tree scaffolds a
milestone with `docs new`, links its impl log and test matrix with
`docs relate add <milestone> pairs-with <companion>`, promotes it with
`docs lifecycle <milestone> active`, and passes `docs check`. It never
hand-edits the metadata block and never stops to ask the operator.

Measured against the activation this very setup performed, the use case
removes **five operator-approved hand-edits** — three `Lifecycle: draft` →
`active` flips and two `Related:` bullets added to this document — plus the
four companion bullets that could only be written at creation time through
the `--body-from` route (*Implementation log* › *Setup record*). The
acceptance flows, each run unattended with no stdin:

- **Promote, in one call.** `docs lifecycle <milestone> <matrix> <log>
  active` sets all three to `active`, bumps `Updated:` on each document that
  changed, reindexes once, and exits 0. Run again, it writes zero bytes and
  does not reindex.
- **Link, one edge per call.** `docs relate add <milestone> pairs-with
  <companion>` writes exactly one bullet into `<milestone>`, rewrites no
  other managed document, and refreshes the generated INDEX once. The companion's back-edge is its own call, because free-form
  edges carry no inverse obligation.
- **Never into, never out of, the archive.** `docs lifecycle <doc> archived`
  refuses and names `docs archive`; `docs lifecycle archive/<date>/<doc>
  active` refuses before any byte moves. Lifecycle and location keep moving
  together, through `docs archive` alone.
- **Close out unchanged.** A milestone trio whose `pairs-with` / `child-of`
  edges were written by `docs relate` previews and archives exactly as one
  whose edges were written by hand — same candidates, same selection, same
  strand refusal.
- **The suite's guard flips.** Against a build carrying this milestone,
  the Agent Playbook Suite's *Validate verbless-metadata stopgap matches the
  pinned docs-cli* probes report `lifecycle verb: True` and `free-form
  relate: True`, which is the signal that retires the stopgap (D9).
- **Any configured tree.** The same flow works unchanged on a tree with
  `add_lifecycles` / `add_roles` extensions or a non-default
  `[archive] date_format`: an extension state round-trips through
  `docs lifecycle`, and every walking verb reads the result (D10).

## Risk Level

**Standard** — proposed at setup and **confirmed by the operator** (Q8,
2026-10-27).

Reason: an ordinary, **additive** change to a published CLI. No existing tree
changes behaviour — `docs check` gains no rule and every record it emits is
unchanged — and the one refusal that turns into a success (`docs relate` on a
free-form verb) has no legitimate dependants beyond the suite guard that is
waiting for it. Every write path reuses a proven editor (`set_metadata_field`,
`add_related_edge` / `remove_related_edge`, `atomic_write`) and the M25
plan/apply machinery. The integrity-sensitive behaviour is narrow and
enumerable — no lifecycle transition into or out of `archived`, recognized-verb
`relate` byte-for-byte unchanged, and the archive candidate set unchanged — and
each is pinned by a named lock. Two High-list triggers were considered and are
not proposed: *public APIs* (the change is additive to the CLI surface, and its
one external consumer is locked by product tests) and *data integrity* (the
verbs write metadata, but only through guarded editors with zero-byte
refusals). The operator's answer to Q7 brings `parse()` — the core read
path every verb uses — into scope (D10), together with the two places that
follow from it: `render_index`, which must render the extension-role groups a
config-aware `parse()` admits (E13), and `docs stamp`, which must refuse
rather than destructively re-stamp a block that fails the tree's config
(E12, operator Packet A). The level stays Standard with that known: the
vocabulary half only widens what parses on a tree `docs check` already passes
(the configured vocabulary is a superset of the built-ins by construction,
and on a default-format tree the configured `date_format` is the ISO format
`parse()` hardcodes today); the outcomes that change are on documents that
already fail `docs check` (E11, and the stamp refusal) or on a 2.0.0 data-loss
path (E12); and the regression surface is the full 1504-test suite plus this
repository's own tree.

Selected gates (Standard):

- Lite: contract; visible product tests for every changed behaviour; `ruff
  check`, `ruff format --check`, `mypy src/ tests/`; `docs check` from the docs
  root; reference byte-identity; the live-INDEX snapshot.
- Coverage report: **not configured** in this project (no coverage tool in
  `[project.optional-dependencies] dev`); recorded as not applicable rather
  than skipped.
- Hidden/generalization smoke: **not configured** as a held-out suite; the
  repository is fully visible to the implementer, so generalization is carried
  by the categories in the test matrix and by property-style checks.
- Property/stateful smoke: **selected** — the contract is invariant-heavy
  (idempotence, add-then-remove from an absent edge restoring the bytes, no
  transition yielding `status-drift`, a free-form write rewriting exactly one
  managed document plus one INDEX refresh).
- Mock audit: **selected** — no new mocks are expected; any failure-injection
  monkeypatch follows the existing `atomic_write` pattern and is audited.
- Reviewer signoff: the ship-milestone Claude-family and GPT-family reviews at
  the end of Steps 0–2.

## Binding scope

The ten decisions below are binding for this milestone. Each names the setup
question it resolves; the reasoning is in *Setup questions (Q1–Q9)*, and the
three setup findings that change something already written down are restated
in *Decisions recorded at setup (BINDING)*. **All nine setup questions are
resolved** — Q3, Q7 and Q8 by the operator on 2026-10-27 — so nothing here is
pending. Phase 1 makes the decisions exact and does not re-open them; D10
in particular is frozen as amended by the Step 0 review (its `render_index`
placement and its `docs stamp` clause included). The matrix ids each
decision maps to are in the test matrix's *Decision ↔ clause crosswalk*.

The registered stub's binding bullets are carried forward verbatim inside the
decisions they belong to and marked *(registered)*.

### D1 — `docs lifecycle <file>... <state>`: a flat verb with `docs project set`'s grammar

*(Q1, conductor.)* `docs lifecycle` is a **top-level verb**, not a namespace.
A single positional run is split as `*files, <state>` — the **last** token is
the target state, every earlier token is a document path — exactly the grammar
`docs project set <doc>... <new-project>` already ships, including its
two-token minimum (a single token is ambiguous and refuses at exit 2). The
batch is validate-all-first and atomic in the `docs touch` / `docs project set`
sense: every named document is resolved and checked before the first write,
and any refusal leaves every document byte-identical.

*(registered)* `--root`, `--dry-run`, `--json`, `--quiet` behave as on the
other mutating verbs.

No `set` subcommand and no `--date` flag: a namespace earns its keep only when
it carries a second operation (`relate` and `project` each carry two), and the
registered scope names no date override. The suite's CI guard reads the brace
list of `docs --help` for a top-level `lifecycle` entry (E2), which this shape
satisfies and which a product test pins.

### D2 — Top-level states only: `archived` is never a target, and an archived document is never a source

*(registered)* `docs lifecycle FILE STATE` sets `Lifecycle:` to any
**top-level** state (`draft`, `active`, `blocked`, `done`, `superseded`, plus
any `add_lifecycles` extension), bumps `Updated:`, and reindexes once.

*(registered)* It refuses `archived` as a target and refuses a document under
the archive subtree as a source: `docs archive` keeps sole ownership of
lifecycle and location moving together.

The top-level set is the tree's configured lifecycle vocabulary minus
`archived` — the same set `status-drift` already accepts in the active tree —
so the verb can never produce a `status-drift` finding. A state outside that
set refuses at exit 2 and names the states the tree accepts; `archived`
refuses with a pointer to `docs archive`. Matching is case-sensitive exact, the
`validate_lifecycle` rule, so `Archived` is an unknown state, not a spelling of
`archived`.

**A source whose current `Lifecycle:` is `archived` refuses too, wherever it
sits** *(Step 0 review, conductor-resolved)*. A document outside the archive
subtree that already reads `Lifecycle: archived` is in `status-drift`, and
flipping it to a top-level state would silently "unarchive" it by hand. The
verb refuses it at exit 2 with zero bytes written, naming the `status-drift`
and `docs archive` — the same whole-batch refusal as a source under the
archive subtree.

**The extension-state clause holds** *(Q7, operator: A)*. Setup measured
that a document carrying an `add_lifecycles` state makes every reindexing verb
exit 2 on 2.0.0 (E7), so "plus any `add_lifecycles` extension … and reindexes
once" could not both hold. The operator kept the clause and brought the cause
into scope: D10 makes `parse()` honour the tree's configured vocabulary, so an
extension state written by `docs lifecycle` is read back by the reindex, by
`docs list`, by `docs relate` and by every other walking verb. The top-level
set is therefore exactly `config.lifecycles` minus `archived`.

No coupling to `Related:`: `blocked` neither requires nor implies a
`blocked-by` edge (`convention.md`, Lifecycle table), and `superseded`'s
"pair with `superseded-by`" is advice the verb does not enforce.

### D3 — Idempotent, validate-all-first, one reindex; `Updated:` moves only where `Lifecycle:` moved

*(registered)* Idempotent: a document already in STATE writes zero bytes,
bumps no `Updated:`, and does not reindex (the `docs relate` precedent).

Per document, the edit is applied and only a document whose `Lifecycle:`
actually changed gets its `Updated:` bumped — the `_plan_relate_edit`
ordering, not `docs touch`'s bump-everything rule. A batch in which every
document is already in STATE is a whole-batch no-op: exit 0, zero bytes, no
INDEX refresh. A mixed batch writes only the documents that change and
refreshes the INDEX exactly once at the end, honouring `[exclude]` /
`.docsignore` (M14 — A6). An INDEX-refresh failure after a successful write is
exit 2 with the documents already correct (the `touch` / `relate` precedent).

### D4 — `docs relate` writes a free-form edge one-sided; recognized verbs are byte-for-byte unchanged

*(registered)* `docs relate add|remove SOURCE VERB TARGET` accepts any
free-form verb (anything other than the six recognized reciprocal verbs) and
writes **SOURCE's bullet only**, with no inverse obligation. Recognized verbs
keep M25 — D3's two-endpoint behaviour byte-for-byte.

*(registered)* Free-form edges stay outside reciprocal validation; `child-of`
/ `parent-of` remain deliberately unvalidated (`convention.md`).

"Any free-form verb" is qualified by D6's grammar. A free-form invocation reads
and writes **one** file: SOURCE gains (or loses) `- <verb>: <target>`, matched
on the canonical target exactly as `add_related_edge` / `remove_related_edge`
already match, with its `Related:` group created when absent and dropped when
empty. TARGET is resolved and checked, never read for writing and never
written. Idempotence, `--dry-run`, `--quiet`, the single end-of-run reindex,
and the zero-byte no-op are M25's, unchanged.

Byte-for-byte for recognized verbs means: the same refusals and messages, the
same exit codes, the same two-record `--json` operation plan, the same
`Revision:` behaviour, and the same coordinated-write failure contract. The
free-form record's shape — expected to be the same object with `"inverse":
null` and exactly one `edits` record — is frozen in Phase 1 without changing
one byte of the recognized-verb record.

The one qualification is D10's, in both directions. On a tree with
vocabulary extensions or a non-default `date_format`, an endpoint that 2.0.0
refused at exit 1 because `parse()` misread its metadata now resolves, and
the pair is then written exactly as on any other tree. Conversely, on the E11
shape — a non-default `date_format` tree whose endpoint still carries a date
in another spelling, a tree that already fails `docs check` with `bad-date` —
an endpoint 2.0.0 accepted now refuses at exit 1 with that same `bad-date`
diagnosis (Phase 1 resolution OQ-6). On every tree `docs check` passes,
recognized-verb behaviour is byte-for-byte unchanged.

### D5 — Free-form endpoints: an archived SOURCE refuses; an archived TARGET is never written; any existing file may be a TARGET

*(Q2 and Q6, conductor.)*

- **An archived SOURCE refuses** — for `add` and `remove`, at exit 2, in the
  validate-all-first pass and therefore even when the invocation would change
  nothing, before any planning. `convention.md` grants exactly three narrow
  exceptions to archived-document immutability and calls M27 — D6's *"the last
  one this convention grants"*; M25 — D4 exists only because reciprocity
  checking reaches archived documents and would otherwise leave an unfixable
  error. A free-form edge carries no such obligation, so no exception is
  needed and none is granted. M25 — D4 stays limited to the recognized bullet.
- **An archived TARGET is fine** because it is never written. `--reason` is
  therefore **not required** for a free-form edge whose TARGET is archived, no
  `Revision:` bullet is ever written by a free-form operation, and `--reason`
  stays accepted-but-unused and echoed in the record, exactly as M25 already
  treats an all-active pair.
- **TARGET may be any existing file under the root** — a Markdown document or
  not, parseable or not — `broken-ref`'s existence test plus containment
  under the root (`convention.md`: *the target file does not need to be a `.md`
  doc*). A missing TARGET, a directory, or one outside the root — including
  through a symlink that escapes it — keeps today's exit-1 refusals. Recognized verbs keep the rule that both endpoints parse, because
  both are written. Without this, `docs relate add <matrix> references
  coverage.xml` — the edge the bundled skill's quality-artifact guidance
  prescribes — would still refuse (E9), and the hand-edit gap would survive
  for a prescribed edit.
- **SOURCE must parse**, as today, because it is written. The self-edge
  refusal, endpoint resolution (root-relative first, then cwd), and the
  excluded-endpoint allowance are unchanged.

### D6 — The free-form verb grammar: a lowercase kebab token

*(Q3, operator: option (c), 2026-10-27.)* A free-form `VERB` must match
`[a-z][a-z0-9-]*` in full — a lowercase letter, then lowercase letters,
digits and hyphens. Anything else refuses at **exit 2 with zero bytes
written**, before any planning, for `add` and `remove` alike: an empty verb, a
verb containing `:` or a newline, leading or trailing whitespace, an internal
space, punctuation, a leading digit or hyphen, and **any uppercase letter**.
Every verb the grammar admits is written as typed and read back by `parse()`
as the identical verb, so `relate` can never write a bullet `docs check`
rejects or reads differently.

- **Case variants of the recognized verbs refuse with no special case.**
  `Precedes`, `Pairs-With` and every other spelling with an uppercase letter
  fall outside the grammar, so E5's silent-wrong-edge hazard is closed by the
  grammar itself, and `test_relate_case_variant_verb_refuses` keeps refusing
  (its expected message follows Phase 1's catalogue).
- **The six recognized verbs are inside the grammar** and keep their
  exact-match, two-endpoint semantics (D4); only a grammar-valid verb that
  `inverse_verb` does not recognize takes the free-form path.
- **The grammar binds `relate`, not the convention.** `docs check` keeps
  accepting any verb text before the first colon (E4); a hand-written verb
  outside the grammar stays valid in a tree, and `relate` simply will not
  write or remove it. Every verb measured in this tree, the fixtures, the
  bundled skill and the suite's prescriptions is inside it (E3).
- **A leading hyphen reaches argparse first.** `docs relate add a.md -x
  b.md` is parsed as an option before the grammar ever sees `-x`. Phase 1's
  message catalogue freezes exactly what that invocation does, and whether a
  `--` separator passes such a verb through to the grammar refusal; either
  way nothing is written.
- **Widening later is additive.** A later milestone may admit more verbs
  without breaking any caller, whereas narrowing would break automation —
  which is why the grammar starts at the strict end. Recorded as *Follow-ups*
  item 3.

### D7 — Archive-candidate selection and the strand refusal are unchanged, and locked

`pairs-with` and `child-of` feed `docs archive`'s one-hop candidate set
(`_CASCADE_VERBS`, M26 — D1 / D3) and M28's leg-1 `child-of` strand refusal.
Making them easier to write must not change either, so the milestone proves it
rather than asserting it: a tree whose edges were written by `docs relate`
is byte-identical to the canonical hand-written tree, its
`--cascade-dry-run --json` candidate records are identical, and leg 1 refuses
a live `child-of` child written by `relate` exactly as it refuses a
hand-written one. The candidate code reads parsed `Doc.related`, so
byte-identity of the written bullet is the whole of the invariance (E10).

### D8 — `--body-from`'s leading `Related:` group is a supported creation-time route — locked and documented

*(Q5, conductor.)* A body whose first block is a bare-label multi-value group
— `Related:` on its own line, then `- <verb>: <target>` bullets — becomes part
of the metadata block: a consequence of `convention.md`'s block grammar, not
of `docs new`'s code. The bundled skill has prescribed linking a non-Markdown
sidecar's binary through `Related:` since M8, but its two examples spell it in
the **inline** form `Related: artifact-of: <binary>`, which the grammar reads
as body text: an inline `Label: value` line after a blank line is never
metadata (E6, corrected by the Step 0 review). The route is therefore
supported in its group form, not an accident: M30 adds the regression lock it
never had, states the consequence in `cli.md`'s `--body-from` paragraph, keeps
M15 — C4's refusal heuristic unchanged, and has the skill name both routes —
`--body-from` with a leading `Related:` group at creation time, `docs relate
add` on an existing document. Phase 7 rewrites both skill examples
(`references/use-cases.md`, `references/adoption-playbook.md`) to the group
form or to `docs relate add <sidecar> artifact-of <binary>`, and the C14 lock
runs the skill's literal example. The wider observation setup made — that
*any* leading bare-label group lands as metadata, including a `Revision:`
group on an active document — is recorded as *Follow-ups* item 1, not fixed
here.

### D9 — Compatibility, 2.1.0, surface parity, the external consumer, and the stopgap hand-off

*(Q4 and Q9, conductor.)*

- **Version.** Additive, so **2.1.0**. Following the single-milestone pattern
  (M19 → 1.6.5, M21 → 1.7.0, M23 → 1.8.0), this milestone bumps
  `pyproject.toml` and the packaging version-pin test in lockstep and opens a
  `## 2.1.0 — UNRELEASED` CHANGELOG section; M25 — D6's "the publish
  performs the bump" applied to a multi-milestone train and does not apply
  here. A separate publish milestone ships it — the M19 → M20 pattern — and is
  not yet registered in the tracker; registering it is a tracker operation for
  when the operator schedules it.
- **Upgrade note.** Three behaviour changes, each stated plainly: `docs
  relate` writes a grammar-valid free-form verb it used to refuse (case
  variants and other out-of-grammar verbs still refuse, now by grammar); on a
  non-default `date_format` tree whose dates already fail `docs check`, every
  verb that reads metadata now refuses those documents with the same
  `bad-date` diagnosis (`docs list` silently omits them) instead of
  disagreeing with the gate (D10, E11); and `docs stamp` refuses, at exit 1
  with zero bytes written, a file whose full metadata block fails the tree's
  configured vocabulary or date format — where 2.0.0 silently re-stamped it,
  discarding its lifecycle, role and `Related:` edges (D10, E12). Vocabulary
  extensions and non-default date formats start working, and extension-role
  documents appear in the INDEX (E13). `docs check`, every existing record,
  and every other refusal are unchanged.
- *(registered)* CLI help, `cli.md`, `convention.md`, the bundled `docs` skill
  and its references, and CHANGELOG describe the same surface (surface-parity
  gate). The bundled skill's *Three things never to hand-edit* names the two
  new verbs as the route for lifecycle and free-form `Related:` edits.
  `references/cli.md` and `references/convention.md` stay byte-identical to
  `docs/cli.md` and `docs/convention.md` (`CLAUDE.md`; `milestone-plan.md` ›
  *Ongoing conventions*), and the README's verb list gains the new verb.
- **The external consumer.** Both Agent Playbook Suite CI probes (E2) are
  replicated as product tests, so the guard's flip is proven here rather than
  discovered at the suite pin bump.
- **Skill channels.** The bundled skill updates in the same change as the
  surface; host-machine skills under `~/.claude/skills/` refresh only at the
  production ship (`CLAUDE.md`), in the publish milestone.
- **The stopgap hand-off.** M30 discharges its part of the stopgap success
  criterion at its own closeout: both verbs ship with the suite's two probes
  locked, and a hand-off note naming the exact suite change lands in a live
  document that outlives this milestone's archive (the publish milestone's
  stub if it is registered by Phase 10, otherwise the 2026-10-26
  `feedback-log.md` entry). The retirement itself happens in the suite release
  that pins the version carrying M30, as the success criterion requires.

### D10 — `parse()` honours the tree's config: vocabulary extensions and `date_format`, in every verb

*(Q7, operator: option (A), 2026-10-27; amended by the Step 0 review —
B1, B2 and operator Packet A. Frozen: Phase 1 does not re-open D10.)*
`parse()` validates `Lifecycle:` and `Role:` against the tree's configured
vocabulary (`config.lifecycles`, `config.roles` — the built-ins plus
`[vocabulary] add_lifecycles` / `add_roles`) and parses `Updated:` in the
tree's `[archive] date_format`, exactly as `check_doc` already does. The
tree's config is passed at **every** call site — the seven that exist today
(`walk()`, `query_docs`, `_cmd_archive`, `_known_projects`,
`_cmd_project_set`, `_resolve_relate_endpoint`, `_cmd_stamp`) and every site
the two new verbs add. A bare `parse(text, path, root)` with no config keeps
today's built-in defaults, so direct callers and the existing unit tests are
unaffected. Two further sites are named, because a config-aware `parse()`
reaches them:

- **`render_index` renders extension roles** (B1, E13). Its role order is
  built from `CANONICAL_ROLE_ORDER` alone, so an extension-role document that
  now parses would be counted in the summary line and silently left out of
  the body. Frozen placement: within each project, the built-in groups render
  first in today's order (`status` pinned first, then
  `CANONICAL_ROLE_ORDER`), and every extension-role group renders **after**
  them, sorted alphabetically by role, each with the usual `### Active —
  <Role>` heading; no new `Config` field. Every active document the summary
  counts is rendered.
- **`docs stamp` refuses a full block that fails the tree's config** (B2,
  E12; operator decision, Packet A). `_cmd_stamp` treats "a clean `parse()`"
  as "already stamped" and re-stamps anything else — which on 2.0.0
  destroys a valid extension-state document. When `docs stamp` meets a file
  whose metadata block carries all the required fields but fails the tree's
  configured vocabulary or date format, it **refuses with zero bytes written,
  exit 1**, naming the failing field and pointing at `docs check` and `docs
  touch`. Accepted consequence: a typo'd lifecycle — or an invalid `Role:` —
  on a default tree is refused too, instead of being re-stamped, which changes
  the pre-existing `test_stamp_supersedes_invalid_existing_block` as listed in
  *Test Strategy* › *Pre-existing tests that change* (Step 0 re-review,
  claude-RR-B1). A file in a configured extension state is "already stamped"
  and gets only the `Updated:` refresh. Files with no block, or a block
  missing required fields, keep today's stamping. **A full block that fails
  `parse()` for a reason unrelated to the tree's configured vocabulary or date
  format — a malformed `Related:` bullet, for example — also keeps today's
  stamping**: the operator's Packet A decision covers only vocabulary and
  date-format failures (conductor-resolved at the Step 0 re-review), and
  Phase 1 does not re-open it.

Consequences, stated as contract:

- **No tree that passes today starts failing.** `Config` already guarantees
  `lifecycles ⊇ BUILTIN_STATUSES` and `roles ⊇ BUILTIN_ROLES`, so the
  vocabulary half only widens what parses; on a default-format tree the
  configured `date_format` *is* the ISO format `parse()` hardcodes, so the
  date half changes nothing there.
- **D10 changes three outcomes, all named in the upgrade note (D9):** a
  non-default `date_format` tree carrying dates in another spelling — which
  already fails `docs check` with `bad-date` at exit 2 (E11) — now fails its
  walking verbs with the same diagnosis instead of disagreeing with the gate;
  `docs stamp` refuses a full block that fails the configured vocabulary or
  date format, where 2.0.0 destructively re-stamped it (E12); and
  extension-role documents appear in the INDEX (E13).
- **One spelling, never two.** `parse()` does not learn to accept both the ISO
  and the configured spelling — the 2026-08-15 feedback entry's reasoning, and
  M25's when it wrote `Revision:`: a second accepted spelling reintroduces the
  ambiguity the convention refuses.
- **Locked across every verb that reads the tree** — `index`, `touch`,
  `list`, `relate`, `lifecycle`, `archive`, `mv`, `project set`, `project
  rename` and `stamp` — as test-matrix clauses C20–C22, C24 and C25.
- **`docs migrate` is unchanged.** Its inference deliberately adopts foreign
  trees against the built-in sets, and it stays out of scope.
- **Both feedback entries are owned here.** The 2026-08-15 `date_format`
  entry and the 2026-10-26 vocabulary entry name this milestone as owner and
  close at Phase 7.

## Contract

The contract below is the setup draft; Phase 1 froze its exact messages,
records and signatures in *Decisions (Phase 1 — BINDING)* below, following
the M25–M28a precedent. Where this draft and that section differ, that
section — and the specs it points at — win.

### Facts

- docs-cli **2.0.0** is published and installed; this branch sits at
  `2ad941e`, four commits ahead of `main` (`7767f24`), with **1504** tests
  passing, `ruff`, `ruff format` and `mypy` clean, and `docs check` exit 0.
- The only post-creation writer of `Lifecycle:` is `_archive_one`, which sets
  `archived` through `set_metadata_field` (E1). The editor `docs lifecycle`
  needs already exists and is already exercised by every archive.
- `docs relate` refuses every verb outside the six recognized ones at exit 2
  (E2), resolves **both** endpoints through `parse()` (E9), and plans exactly
  two edits (`plan_relate` raises `ValueError` on an unrecognized verb).
- `docs project set <doc>... <new-project>` already ships the grammar,
  validate-all-first batch, archived-target refusal, no-op and single-reindex
  behaviour D1–D3 adopt.
- 94% of this tree's `Related:` edges (391 of 417) are free-form, and every
  verb in this tree, every fixture and the bundled skill is a lowercase
  kebab token (E3).
- `docs check` accepts any verb text before the first colon (E4) and any
  existing file as a target.
- `docs --help` renders the verb list as one brace group, which the suite
  guard parses (E2).
- A vocabulary extension or a non-default `date_format` breaks every walking
  verb except `docs check`, because `parse()` validates against built-ins and
  the ISO default instead of the tree's config (E7, E8). `Config` guarantees
  that its vocabulary is a superset of the built-ins, and the one tree shape
  whose verb outcome a fix would change already fails `docs check` (E11).
- Two consumers sit downstream of `parse()`'s verdict: `render_index` renders
  only the built-in roles (E13), and `_cmd_stamp` reads "a clean `parse()`" as
  "already stamped" and re-stamps everything else (E12).

### Assumptions

- **No one depends on `relate`'s free-form refusal** beyond the suite guard
  waiting for it to lift. Owner: Phase 7's upgrade note. Validation: the
  CHANGELOG names the change; the census found no consumer in this repository
  or the suite.
- **The suite guard's probes stay as measured on 2026-10-26** (`a997954`).
  Owner: the publish milestone's closeout. Validation: the product-test
  replicas are re-run against the published wheel.
- **One file per free-form invocation suffices for the prescribed
  workflows.** The `create-milestones` setup issues one `relate add` per edge.
  Bulk edge writing stays out (M25's one-pair-per-invocation non-goal).

### Ambiguities

- **Resolved by the operator (2026-10-27):** the free-form verb grammar
  (Q3 → `[a-z][a-z0-9-]*`, D6); the extension-state scope (Q7 → fix
  `parse()`'s config-blindness, both halves, D10); the risk level (Q8 →
  Standard).
- **Phase-1 freeze items — frozen** in *Decisions (Phase 1 — BINDING)*: the
  `docs lifecycle` message catalogue and `--json` record (P1.1); the
  free-form `relate` record shape and its grammar-refusal message (P1.2);
  the multi-file `docs lifecycle` write — sequential, the `project set`
  precedent (P1.1, OQ-2); D10's exact `parse()` signature and how each call
  site obtains its config (P1.4); argparse's handling of a leading-hyphen
  verb (P1.2, R3); and the `cli.md` / `convention.md` wording, with the skill
  wording frozen where a test extracts it (P1.3) and listed for Phase 7
  otherwise (P1.8).

### Inputs

- CLI inputs: `docs lifecycle <file>... <state> [--root DIR] [--dry-run]
  [--json] [--quiet]`; `docs relate add|remove SOURCE VERB TARGET [--reason
  TEXT] [--date YYYY-MM-DD] [--json] [--dry-run] [--quiet] [--root DIR]` with
  `VERB` now any recognized verb or a free-form verb within D6's grammar;
  `docs new … --body-from PATH|-` (unchanged surface, newly locked behaviour).
- Data/state preconditions: a `.docs.toml` docs root (strict-root
  resolution); named documents that parse; the tree's
  `[vocabulary] add_lifecycles` and `[archive] dir` / `date_format`.

### Outputs

- Return values / responses: exit 0 / 1 / 2 under the cross-verb convention
  (1 for a named path that is missing, malformed or outside the root; 2 for
  hard refusals); human lines on stderr gated on `--quiet` except refusals;
  one `--json` object on stdout with an identical shape for `--dry-run` and
  apply.
- Files/side effects: `docs lifecycle` rewrites `Lifecycle:` and `Updated:` in
  each changed document and nothing else; free-form `relate` rewrites one
  `Related:` bullet and `Updated:` in SOURCE and nothing else; `INDEX.md` is
  refreshed once, only when something changed and not under `--dry-run`.

### Invariants

- Must always: write through the existing surgical editors and
  `atomic_write`; leave every byte outside the edited lines, the H1, the body
  and the trailing-newline state untouched; refresh INDEX at most once.
- Must never: write `Lifecycle: archived`; write any byte of a document under
  the archive subtree through `docs lifecycle` or a free-form `relate`; write
  a free-form bullet into TARGET; write a bullet `docs check` would reject or
  re-read differently; change the recognized-verb `relate` behaviour or the
  archive candidate set; leave out of the INDEX body an active document its
  summary counts; let `docs stamp` rewrite a document whose full block fails
  the tree's config.
- If a named document is already in the requested state (or already carries /
  lacks the edge), then it is not written at all — no `Updated:` bump, no
  `Revision:`, and, when nothing in the run changed, no reindex.
- No verb starts refusing a document `docs check` accepts, and every verb
  that reads metadata judges `Lifecycle:`, `Role:` and `Updated:` exactly as
  `docs check` does under the tree's config (D10). The alignment covers those
  three fields only: a structural fault `docs check` tolerates — a malformed
  `Related:` bullet, a multi-valued `Project:` — keeps failing every verb that
  parses the document, exactly as on 2.0.0.

### Error cases

| Condition | Expected behaviour | Observability |
|---|---|---|
| No `.docs.toml` ancestor, or `--root` without one | exit 2, nothing written | the strict-root message in the verb's voice |
| `docs lifecycle` given a single token | exit 2, nothing written | grammar message (the `project set` shape) |
| State outside the tree's top-level vocabulary | exit 2, nothing written | names the allowed states |
| State `archived` | exit 2, nothing written | points at `docs archive` |
| A named document under the archive subtree | exit 2, whole batch refused | names the path |
| A named document outside the archive subtree whose current `Lifecycle:` is `archived` | exit 2, whole batch refused, nothing written | names the `status-drift` and points at `docs archive` |
| A named document missing, malformed, or outside the root | exit 1, nothing written | names the path (validate-all-first) |
| Free-form verb outside D6's grammar | exit 2, nothing written | names the verb and the grammar |
| Free-form SOURCE under the archive subtree | exit 2, nothing written, even if a no-op | names the path |
| Free-form TARGET missing, a directory, or outside the root (including through an escaping symlink) | exit 1, nothing written | today's messages |
| `docs stamp` on a file whose full metadata block fails the tree's configured vocabulary or date format | exit 1, zero bytes written | names the failing field; points at `docs check` and `docs touch` |
| INDEX refresh fails after a successful write | exit 2; documents already correct | `docs: INDEX refresh failed: …`; the `--json` record still emitted with `"index_refreshed": false` |
| A walked document whose `Lifecycle:`, `Role:` or `Updated:` does not parse under the tree's config | the walking verb fails as today's walk errors do (e.g. `docs index` exit 2), now judged by the same config `docs check` uses | the self-locating `docs: <path>: …` message — the same message `docs check` gives as `bad-vocab` / `bad-date` (Phase 1 resolution OQ-6: messages unchanged) |

### Non-functional constraints

- Performance budget: no whole-tree pre-flight (the `relate` precedent) — one
  parse per named file plus the single reindex; the added runtime over this
  tree is measured in Phase 9 and recorded.
- Security/privacy constraints: TARGET containment under the root is
  unchanged; a verb containing `:` or a newline is refused because it would
  corrupt the metadata block — the metadata-injection guard.
- Compatibility/migration constraints: no verb starts refusing a document
  `docs check` accepts; D10's three changed outcomes (E11,
  E12, E13) are named in the upgrade note; no `docs check` rule, finding or
  record key changes; the recognized-verb `relate` record is byte-identical;
  stdlib only on Python 3.11+ (charter).
- Reliability/observability needs: every refusal is zero-byte and prints even
  under `--quiet`; every write is atomic per file.

### Acceptance examples

- Given a draft `m.md` in the active tree, when `docs lifecycle m.md active`
  runs, then `m.md` reads `Lifecycle: active` with today's `Updated:`, INDEX is
  refreshed once, and exit is 0; run again, nothing is written at all —
  neither `m.md` nor the INDEX.
- Given `m.md`, when `docs lifecycle m.md archived` runs, then exit is 2, the
  message names `docs archive`, and the tree is byte-identical.
- Given `archive/2026-08-16/x.md`, when `docs lifecycle
  archive/2026-08-16/x.md active` runs, then exit is 2 and nothing is written.
- Given `stray.md` in the active tree reading `Lifecycle: archived`, when
  `docs lifecycle stray.md active` runs, then exit is 2, the message names
  the `status-drift` and `docs archive`, and nothing is written.
- Given `m.md` and `m-impl.md`, when `docs relate add m.md pairs-with
  m-impl.md` runs, then `m.md` is the only managed document rewritten — it
  gains `- pairs-with: m-impl.md` and today's `Updated:` — the INDEX is
  refreshed once, and `docs check` is clean.
- Given an archived `archive/2026-08-16/old.md`, when `docs relate add m.md
  references archive/2026-08-16/old.md` runs without `--reason`, then exit is
  0 and `m.md` is the only managed document rewritten; when `docs relate add archive/2026-08-16/old.md
  references m.md` runs, then exit is 2 and nothing is written.
- Given a tree with `[vocabulary] add_lifecycles = ["shipped"]`, when
  `docs lifecycle m.md shipped` runs, then exit is 0, the INDEX is refreshed,
  and `docs list`, `docs relate` and `docs index` all read `m.md` afterwards.
- Given `m.md` and `n.md`, when `docs relate add m.md Pairs-With n.md` runs,
  then exit is 2 and nothing is written.
- Given a tree with `add_lifecycles = ["shipped"]` and `a.md` at `Lifecycle:
  shipped` carrying `Related:` edges, when `docs stamp a.md` runs, then only
  its `Updated:` changes; given `a.md` at a lifecycle outside the configured
  set, `docs stamp a.md` exits 1, names `Lifecycle:`, and writes nothing.
- Given a tree with `add_roles = ["adr"]` and an `adr` document, when `docs
  index` runs, then the document is rendered under `### Active — Adr` after
  every built-in role group.
- Given the primary use case, when it runs end to end on a throwaway tree, then
  no file is edited outside a verb and `docs check` exits 0.

### Taste anchors

- Reference modules this change should read like: **`_cmd_project_set`** for
  `docs lifecycle` (the `*docs, <value>` split, validate-all-first, the
  archived-batch refusal, the no-op and the single reindex); **`_cmd_relate`,
  `plan_relate`, `_plan_relate_edit`, `relate_plan_to_json` and
  `_print_relate_lines`** for the free-form path; **`_cmd_touch`** for the
  write loop and its INDEX-refresh tail; **`check_doc`** for D10 — the
  config-aware validation `parse()` must match; **`render_index`**'s existing
  role grouping, extended rather than replaced, for the extension-role groups;
  and `_cmd_stamp`'s validate-all-first abort for its new refusal.
- In-project libraries to reuse: `set_metadata_field`, `add_related_edge` /
  `remove_related_edge`, `_canonical_related_target`, `atomic_write`,
  `_refresh_index` with `compile_exclude_predicate`, `_resolve_managed_root`,
  `_resolve_relate_endpoint`, `_is_archived_rel`, `validate_lifecycle`,
  `inverse_verb`, `load_config`, `parse_date`, and the `RelatePlan` /
  `RelateEdit` records. A hand-rolled equivalent of any of them is a logged
  decision.
- Established patterns to follow: the `docs: <verb>: …` stderr voice;
  validate-all-first then write; refusals that print under `--quiet`; one
  `--json` object whose preview and apply shapes match; frozen dataclass plan
  records with pure planners and a separate apply; contracts frozen in the
  milestone's *Decisions (Phase 1 — BINDING)* rather than stubbed in
  `cli.py`, so Phase-4 RED reasons stay honest; behaviour-first test names
  with no milestone or decision identifiers.
- Expected diff footprint: `src/docs_cli/cli.py` roughly +250 to +400 lines
  (one new verb, its parser entry and plan record, and a one-sided branch in
  the relate planner and CLI), plus about +60 to +110 for D10 — config
  threading across seven call sites, `render_index`'s extension-role groups,
  and `docs stamp`'s refusal; tests roughly +900 to +1,300 lines across one
  new and about a dozen existing modules;
  documentation — one new `cli.md` section, edits to its `relate` and
  `--body-from` sections and its `docs stamp` idempotence paragraph, two
  `convention.md` sections, the skill's verb table, *Three things never to
  hand-edit*, use-case rows and the two sidecar examples, the README verb
  list, and one CHANGELOG section. A diff several times larger triggers a
  minimality look.
- Dependency policy: stdlib only at runtime (charter); no new development
  dependency without a logged decision.

### Forbidden shortcuts

- Do not special-case visible examples — in particular `pairs-with`, the verb
  the suite guard probes; the free-form path must be the grammar, not a list.
- Do not branch on test literals or fixture names.
- Do not weaken valid tests or configured explicit checks merely to obtain
  GREEN. Correct erroneous expectations under the shared quality model's Check
  calibration rule; preserve the agreed behavior and meaningful coverage. The
  pre-existing tests that pin today's behaviour change only as listed in
  *Test Strategy* › *Pre-existing tests that change*, each with its reason.
- Do not implement `docs lifecycle` by shelling out to, or re-entering,
  another verb's command function; do not let any spelling reach `archived`.
- Do not write TARGET in a free-form operation, even to "normalise" it.
- Do not relax `docs check` to make a written edge pass.

### Test hooks

- Visible tests to generate: a new `tests/test_cli_lifecycle.py`; additions to
  `tests/test_cli_relate.py` and `tests/test_relate_plan.py`; invariance locks
  in `tests/test_cli_archive.py`; the `--body-from` lock in
  `tests/test_body_from.py`; skill parity in `tests/test_skill.py`; the version
  pins in `tests/test_packaging.py`; D10's vocabulary, date-format,
  `render_index` and `docs stamp` locks across the verbs that read the tree;
  and the `_attic_tree` correction in `tests/test_cli_mv.py`.
- Explicit non-product checks, outside default product-test discovery:
  listed in *Test Strategy* › *Non-product checks*.
- Hidden/generalization categories to hold back: listed in *Test Strategy*.
- Property/stateful invariants: idempotence; add-then-remove from an
  initially absent edge restores the original bytes apart from `Updated:`; no
  transition yields `status-drift`; a free-form operation rewrites exactly
  one managed document and refreshes the INDEX once.
- Mutation-sensitive logic: the `archived` target guard; the archive-subtree
  source guard; the current-`archived` source guard; the
  recognized-versus-free-form branch; the `if changed` idempotence guard; the
  no-reindex-on-a-no-op guard; the verb grammar (`fullmatch` versus `match`
  with `$`, `[0-9]` versus `\d`); the config passed to `parse()`;
  `render_index`'s extension-role placement; `docs stamp`'s block
  classification.
- Fuzz targets: the verb grammar — valid and invalid inputs generated
  independently from D6's grammar; valid ones succeed and round-trip, invalid
  ones refuse with zero writes.
- Benchmark/security/schema checks: both `--json` key sets asserted closed;
  the metadata-injection refusals; runtime recorded, not budgeted.

## Out of scope

- **A symmetric `pairs-with`, or any new reciprocal pair.** Declined by the
  operator at promotion (feedback-log 2026-10-26), so `missing-inverse`
  reports nothing new on any existing tree.
- **Guidance-only alternatives** — a second sanctioned hand-edit exception for
  `Lifecycle:` or for free-form bullets. Both declined at promotion.
- **Any transition into or out of `archived`, and any write to an archived
  document by the new paths.** `docs archive` owns entry; nothing owns exit.
- **Removing a dangling free-form edge** whose TARGET no longer exists.
  TARGET must still resolve; repairing a `broken-ref` stays a move-driven or
  manual operation (*Follow-ups* item 2).
- **Bulk edge writing** — several targets or several edges per invocation
  (M25's one-pair-per-invocation non-goal).
- **Narrowing `--body-from`'s refusal heuristic** to reject a leading
  bare-label group (*Follow-ups* item 1).
- **Coupling lifecycle to `Related:`** — `blocked` ↔ `blocked-by`,
  `superseded` ↔ `superseded-by`.
- **A `--date` flag on `docs lifecycle`**, a `docs lifecycle` namespace, and a
  lifecycle *history* — git owns history (charter).
- **Widening the free-form verb grammar** beyond `[a-z][a-z0-9-]*` —
  additive whenever a real tree needs it (D6; *Follow-ups* item 3).
- **`docs migrate`'s built-in-vocabulary inference**, which deliberately
  adopts foreign trees against the built-in sets (D10).
- **Accepting two date spellings** in `parse()` (D10).
- **The publish itself, the host-skill refresh, and the suite PR** — the
  publish milestone and the Agent Playbook Suite (D9).

## Current state and risks

Measured against this repository at docs-cli 2.0.0 (`2ad941e`, 1504 passed,
`docs check` exit 0) during setup. Census runs were **read-only** against the
live tree; every mutation was performed on a throwaway tree in the session
scratchpad, outside the repository. The full evidence table lives in the
implementation log's setup record; each item below grounds a decision and maps
to named coverage in *Evidence → regression coverage*.

The registered stub's four statements, carried forward:

- 2.0.0 has no verb that writes a non-archived `Lifecycle:` and none that
  writes a free-form `Related:` bullet (feedback-log 2026-10-26, findings 1–2).
  Setup sharpens the second half: none that writes one **on an existing
  document** — a creation-time route exists and is documented (E6, *A3*).
- `create-milestones` rule 3 sanctioned exactly those two hand-edits while the
  bundled skill forbade them. The stopgap (operator decision 2026-10-26) drops
  the suite's carve-outs in favour of an operator ask; M30 removes the need
  for the ask.
- `pairs-with` / `child-of` feed the archive cascade candidate set (M26 — D1)
  and M28's leg-1 `child-of` strand refusal. Making them easier to write must
  not change either; tests must pin that.
- Widening `relate` to free-form verbs touches M25 — D4's audited
  archived-endpoint exception, which today names only the recognized bullet.
  Resolved by D5: the exception is not widened.

The measurements:

- **E1 — the editor exists; only the verb is missing.** `_archive_one` is the
  only post-creation writer of `Lifecycle:` (`set_metadata_field(…,
  "Lifecycle", "archived")`); `docs new` and `docs stamp` write `draft`,
  `docs touch` writes `Updated:` alone. The lifecycle verb is a thin,
  well-precedented wrapper, not new machinery.
- **E2 — the suite's guard is an external contract consumer.** In a fresh
  two-document tree, `docs relate add a.md pairs-with b.md --dry-run` exits 2
  with `unknown verb 'pairs-with'` — exactly the behavioural probe in the Agent
  Playbook Suite's *Validate verbless-metadata stopgap matches the pinned
  docs-cli* step, which also parses the `{…}` verb list of `docs --help` for a
  `lifecycle` entry. Against 2.0.0 the guard reads `lifecycle verb: False`,
  `free-form relate: False`.
- **E3 — free-form is the common case, and its vocabulary is tiny.** 417
  `Related:` edges in this tree (391 free-form across 7 verbs, 26
  recognized); 96 in the fixtures (13 verbs); 5 in the bundled skill; and the
  suite prescribes only `pairs-with`, `child-of`, `implements` and
  `references`. **Every** verb measured matches `[a-z][a-z0-9-]*`.
- **E4 — the parser's verb grammar is "anything before the first colon".**
  `- : target.md`, `- see also: target.md`, `- @#!$: target.md` and
  `- Precedes: target.md` all pass `docs check` at exit 0, and `docs list
  --json` reports their verbs as `""`, `"see also"`, `"@#!$"` and `"Precedes"`;
  `- pairs-with  : target.md` is read back as `pairs-with`. Of the bullet
  shapes measured, only an unresolvable target (`broken-ref`) fails the gate.
  *(Corrected at the Step 1 review resolution: setup also listed "a missing
  colon or empty target (`malformed`)", but `- no-colon-here` and `- verb:`
  both pass `docs check` at exit 0 — while every verb that parses the
  document refuses it with `malformed Related entry`.)*
- **E5 — a case variant is a silent-wrong-edge hazard.** Today `docs relate
  add a.md Precedes b.md` refuses at exit 2 (pinned by
  `test_relate_case_variant_verb_refuses`). Under a grammar that mirrors the
  parser it would succeed and write a one-sided `Precedes:` edge that
  reciprocity ignores — an agent that mistyped a recognized verb would get
  neither the pair nor an error.
- **E6 — the `--body-from` route is a documented intent with no test, and
  the skill's spelling of it does not work.** A body opening with a
  `Related:` group — the label alone on its line, then bullets — lands in the
  metadata block (`docs list --json` lists the edges; `docs check` clean). The
  bundled skill's `references/use-cases.md` row *Sidecar a non-md artifact*
  prescribes `docs new <role> <slug> --body-from -` with `Related:
  artifact-of: <binary>` ("No new verb — uses the M8 `--body-from` flag"), and
  `references/adoption-playbook.md` says the same — but both spell it in the
  **inline** form, and an inline `Related: artifact-of: deck.html` line is
  read as body text: `docs list --json` shows no edge (measured by the Step 0
  review, claude-S2, and reproduced). No test covers either form. The
  behaviour is generic: a leading `Revision:` group also lands as metadata on
  an active document. And the adoption playbook's description of the refusal
  heuristic (`^[A-Z][A-Za-z-]+:\s`) is the pre-M15 — C4 wording.
- **E7 — vocabulary extensions break every verb except `docs check`.** With
  `[vocabulary] add_lifecycles = ["shipped"]` and one document at `Lifecycle:
  shipped`: `docs index` exits 2; `docs touch` of **another** document writes
  and then exits 2 (`INDEX refresh failed`); `docs list` silently drops the
  document from human and `--json` output, exit 0 (corrected at the Step 1
  review resolution: setup said "with a stderr error"; it prints nothing);
  `docs relate`
  refuses it as an endpoint (exit 1); `docs archive --dry-run` exits 1;
  `docs mv --dry-run` exits 2 — and `docs check` reports no violations. With
  `add_roles = ["adr"]`, `docs new adr x` succeeds and the next `docs index`
  exits 2. Cause: `parse()` validates against `BUILTIN_STATUSES` /
  `BUILTIN_ROLES`, and every walking verb goes through it. No fixture
  exercises a non-empty extension through a walk, while this repository's own
  `.docs.toml` and the bundled template advertise the feature.
- **E8 — the date-format half of the same cause is wider than recorded.**
  With `[archive] date_format = "%d-%m-%Y"`, `docs new` writes `Updated:
  26-10-2026` and the next `docs index` and `docs touch` exit 2 (`malformed
  date … (expected %Y-%m-%d)`); `docs check` exits 0. The 2026-08-15
  feedback entry recorded the population correctly but named `docs archive`
  only.
- **E9 — `relate` refuses a target the convention allows.** `docs relate add
  a.md precedes coverage.xml` exits 1 (`missing H1`) because both endpoints
  are parsed, while `references: coverage.xml` passes `docs check`, and the
  bundled skill's quality-artifact guidance tells agents to link generated
  reports from `Related:`.
- **E10 — what the suite pins today.** Three pre-existing test ids pin the
  free-form refusal: `test_relate_unknown_verb_refuses` and
  `test_relate_quiet_suppresses_success_but_never_a_refusal` (both refuse
  `pairs-with`), and `test_relate_case_variant_verb_refuses` (`Precedes`). The
  first two become deliberate behaviour-change edits; the third keeps
  refusing under D6's grammar.
  `test_every_named_verb_is_a_real_subcommand` fails the moment `lifecycle` is
  registered without the skill naming it, so the parity gate enforces itself.
  Archive candidates come from `_CASCADE_VERBS = ("pairs-with", "child-of")`
  over parsed `Doc.related`, so D7's invariance reduces to byte-identity of the
  written bullet.
- **E11 — the one tree shape whose verb outcome D10 changes already fails the
  gate** (measured 2026-10-27, after the operator's Q7 answer). A tree whose
  sidecar sets `[archive] date_format = "%d-%m-%Y"` while a document still
  carries an ISO `Updated: 2026-10-27`: `docs check` reports `bad-date` at
  exit 2 today, while `docs index` exits 0. After D10 the walking verbs agree
  with the gate. No committed fixture sidecar sets a non-default
  `date_format` and this repository uses the default, but two inline test
  builders carry the shape: `tests/test_cli_mv.py`'s `_attic_tree` writes ISO
  `Updated:` lines on a `%d-%m-%Y` tree (its docstring cites this very defect
  as the reason), and
  `test_archive_renders_the_witness_in_the_trees_date_format` pins today's
  exit-2 INDEX-refresh tail on purpose, its docstring naming its own
  successor. Both are corrected in the same change; they are listed in *Test
  Strategy* › *Pre-existing tests that change*.
- **E12 — `docs stamp` destroys a valid extension-state document on 2.0.0**
  (found by the Step 0 review, claude-B2; reproduced by the conductor and
  again here). On a tree with `add_lifecycles = ["shipped"]`, a `docs
  check`-clean document at `Lifecycle: shipped`, `Role: spec`, with a
  `Related:` edge: `docs stamp a.md` exits 0 and rewrites it to `Lifecycle:
  draft`, `Role: notes`, today's `Updated:`, and moves its `Related:` group
  into a `## Migrated metadata` body section as `Migrated-Related:`. With a
  free-form edge, `docs check` afterwards still exits 0 — the edge is simply
  gone from the metadata; with a recognized `precedes` pair, the partner's
  `follows` is left dangling and `docs check` exits 2 (`missing-inverse`). A
  typo'd `Lifecycle: activ` on a default tree is re-stamped the same way, its
  `Project:` replaced by the root's. Cause: `_cmd_stamp` reads "a clean
  `parse()`" as "already stamped", and `parse()` rejects every extension value.
  D10's config-aware `parse()` fixes the extension case; operator Packet A
  turns every remaining full-block failure into a zero-byte refusal.
- **E13 — `render_index` would silently drop extension-role documents once
  they parse** (found independently by both Step 0 reviewers, gpt-B1 and
  claude-B1; reproduced here). `render_index` builds its role order from
  `["status"] + CANONICAL_ROLE_ORDER` and renders only roles in that list. A
  direct probe — one `spec` document and one document whose role is the
  configured extension `adr` — renders `_Generated …. 2 docs active, 0
  archived._` and a body containing only the `spec` entry. Today the defect is
  masked by E7 (the `adr` document never parses); D10 would expose it.

Structural risks:

- **A verb that writes and then fails its own reindex.** E7 is the exact
  shape `test-strategy.md`'s critical paths forbid — the tool must never leave
  a tree that fails its own gate — and a lifecycle verb that writes an
  extension state reproduces it on purpose. Closed by D10: the verb, its
  reindex and every walking verb read the same configured vocabulary.
- **A silently wrong edge.** A free-form path that accepts what the parser
  accepts turns a mistyped recognized verb into a one-sided free-form edge with
  exit 0 (E5). Closed by D6: every verb with an uppercase letter is outside
  the grammar.
- **A widened archived exception by accident.** The free-form path shares
  `_cmd_relate`'s archived-endpoint code; reusing it unmodified would write a
  `Revision:` into an archived SOURCE. Mitigated by D5's refusal running in
  the validate-all-first pass, before planning, with a lock.
- **Recognized-verb drift.** Branching the planner for one-sided edits can
  perturb the two-endpoint path. Mitigated by byte-level locks on the
  recognized-verb record, messages and files, and by the existing 2.0 relate
  suite staying GREEN unedited apart from the listed pre-existing changes.
- **A change on the core read path.** D10 reaches the function every verb
  uses. Mitigated by a backward-compatible signature (a bare call keeps the
  built-in defaults), by `Config`'s superset guarantee, by E11's proof that
  the changed outcomes are on documents that already fail the gate or on a
  data-loss path, by naming `render_index` and `docs stamp` as sites of their
  own (E12, E13), and by the full suite plus this repository's own tree.
- **Surface sprawl.** The change reaches argparse, two specs, their mirrors,
  the skill body, two skill references, the README and the CHANGELOG. Phase 1
  enumerates every surface, and the skill completeness guard catches the
  verb-name half automatically.

Mitigating existing strengths: every editor needed already exists and is
surgical; `docs project set` is a near-exact behavioural template for the new
verb; the relate plan/apply split already separates staging from writing; and
this repository is a 75-document dogfood corpus carrying 417 real edges.

### Evidence → regression coverage

| Evidence | Addressed by | Named coverage (Phases 2–3) |
|---|---|---|
| E1 no lifecycle verb | D1–D3 | `docs lifecycle` promotes, demotes and re-promotes across every top-level state; a mixed batch writes only the changed documents and reindexes once; an already-satisfied batch writes zero bytes and does not reindex |
| E1 the archive boundary | D2 | `archived` as a target, a document under the archive subtree as a source, and an active-tree source already reading `Lifecycle: archived` each refuse at exit 2 with the tree byte-identical, including in a batch where every other document is valid |
| E2 the suite guard | D1, D9 | the brace list of `docs --help` contains `lifecycle`; `docs relate add a.md pairs-with b.md --dry-run` in a fresh two-document `docs new spec` tree exits 0 and writes nothing |
| E3 / E4 / E5 the verb grammar | D6 | `[a-z][a-z0-9-]*` pinned at its boundary — every measured verb accepted; empty, `:`, newline, padded, spaced, punctuated, digit-first and uppercase verbs refused at exit 2 with zero bytes written, `Precedes` and `Pairs-With` included; the fuzz check round-trips every accepted verb through `parse()` unchanged |
| E4 one-sided write | D4 | a free-form `add` changes SOURCE only (TARGET byte-identical); `remove` drops only SOURCE's bullet; both are idempotent; the free-form `--json` record shape is pinned |
| E5 recognized verbs unchanged | D4 | every pre-existing `test_cli_relate.py` / `test_relate_plan.py` id stays GREEN unedited except those listed under *Pre-existing tests that change*; a byte-level lock on the recognized-verb record and files |
| E6 `--body-from` route | D8 | a body opening with a `Related:` group yields those edges in `docs list --json` and a clean `docs check`; the skill's literal sidecar example, as rewritten in Phase 7, yields its edge; the inline form stays body text; the C4 refusal heuristic's existing locks unchanged |
| E7 / E8 config-blindness | D2, D10 | extension-lifecycle, extension-role and non-default-`date_format` locks across `index`, `touch`, `list`, `relate`, `lifecycle`, `archive`, `mv`, `project set`, `project rename` and `stamp`; a bare `parse()` call keeps the built-in defaults |
| E9 non-Markdown target | D5 | `docs relate add <doc> references coverage.xml` succeeds and `docs check` is clean; a missing target, a directory target and an outside-root target keep exit 1 |
| E10 archive invariance | D7 | for a trio linked by `relate`: each written bullet line and the parsed `Related:` list match the hand-written trio, its `--cascade-dry-run --json` candidate records are identical, and leg 1 refuses a `relate`-written live `child-of` child; full-file byte identity is asserted only for the `archive-neighborhood` copy, with `relate` run under `--date` set to the fixture's own `Updated:` |
| E11 the one changed outcome | D10 | a non-default-`date_format` tree carrying an ISO `Updated:` fails the walking verbs with the `bad-date` diagnosis `docs check` already gives; a correctly dated non-default tree archives at exit 0 (`test_archive_renders_the_witness_in_the_trees_date_format` rewritten as its docstring foresees); every pre-existing fixture tree and this repository's tree reindex byte-identically |
| E12 `docs stamp` data loss | D10 | on an extension-vocabulary tree, stamping a document in a configured extension state changes only `Updated:` (lifecycle, role and `Related:` byte-identical); a full block outside the configured vocabulary — on an extension tree and on a default tree (the renamed `test_stamp_refuses_a_full_block_with_an_invalid_role_with_zero_bytes`) — and the E11 non-default-date shape each refuse at exit 1 with zero bytes written; a block failing for an unrelated reason keeps today's stamping |
| E13 extension roles dropped from the INDEX | D10 | an extension-role document is rendered under its own `### Active — <Role>` heading after every built-in group, extension groups sorted alphabetically, and the summary count equals the rendered entries |
| Q2 archived SOURCE | D5 | free-form `add` and `remove` on an archived SOURCE refuse at exit 2 even when nothing would change; an archived TARGET needs no `--reason` and is never written |

## Test Strategy For This Milestone

### Visible tests

Subprocess tests (`docs_script`, `--root` on a `tmp_path` tree) drive the
behaviour, one per acceptance flow and error row in *Contract*, plus pure
planner tests for the one-sided relate plan and the lifecycle plan. Names state
the scenario and the observable outcome; provenance stays in this document and
the test matrix. See the matrix for the planned names per clause.

### Pre-existing tests that change (authoritative list)

This is the only list of pre-existing tests the milestone edits; every other
count or mention defers to it. Phases 4 and 8 prove mechanically that each of
the 1504 pre-existing ids is present — under its own id, or, for the four
renamed rows below, under its new id — and that no pre-existing test body is
edited unless it appears here. The Step 0 re-review added the
`test_cli_stamp.py` row (claude-RR-B1).

| Old id | New id | Change | Reason |
|---|---|---|---|
| `tests/test_cli_relate.py::test_relate_unknown_verb_refuses` | `tests/test_cli_relate.py::test_relate_verb_outside_the_free_form_grammar_refuses` | renamed; refuses the out-of-grammar verb `see also` instead of `pairs-with`, asserting the full R1 message | `pairs-with` becomes a valid free-form verb (D4, D6) |
| `tests/test_cli_relate.py::test_relate_quiet_suppresses_success_but_never_a_refusal` | unchanged | its refused verb changes from `pairs-with` to the out-of-grammar `Pairs-With` | same |
| `tests/test_cli_relate.py::test_relate_case_variant_verb_refuses` | unchanged | still refuses at exit 2 with zero bytes; its assertion is unchanged because R1 keeps the `unknown verb` stem (Phase 1 resolution OQ-4), and only its docstring's "free-form verb" becomes "outside the grammar" | D6 |
| `tests/test_cli_archive.py::test_archive_renders_the_witness_in_the_trees_date_format` | unchanged | its fixture's input `Updated:` is written in the tree's `%d-%m-%Y`; expected exit 0; the two INDEX-refresh assertions are dropped and the three witness assertions kept; the malformed-date behaviour moves to the new `test_walking_verbs_report_bad_date_on_a_mis_spelled_non_default_tree` | D10 fixes the defect it pinned, as its docstring foresees (E11) |
| `tests/test_cli_mv.py::test_mv_refuses_a_cross_dated_relocation_on_a_non_default_archive_tree` | unchanged | through the shared `_attic_tree` builder: `Updated:` lines move from ISO to `%d-%m-%Y`, and the builder's docstring drops its defect sentence | D10 reads `Updated:` in the tree's format (E11) |
| `tests/test_cli_mv.py::test_mv_does_not_refuse_inside_an_ordinary_archive_named_subdirectory` | unchanged | the same `_attic_tree` correction | same |
| `tests/test_packaging.py::test_a3_project_version_is_2_0_0` | `tests/test_packaging.py::test_a3_project_version_is_2_1_0` | renamed; expects 2.1.0 | the 2.1.0 bump (D9); the M23 / M29 rename precedent |
| `tests/test_packaging.py::test_c2_docs_version_is_2_0_0` | `tests/test_packaging.py::test_c2_docs_version_is_2_1_0` | renamed; expects 2.1.0 | same |
| `tests/test_packaging.py::test_b1_wheel_builds` | unchanged | expects a `docs_cli-2.1.0-*` wheel | same |
| `tests/test_packaging.py::test_b2_sdist_builds` | unchanged | expects `docs_cli-2.1.0.tar.gz` | same |
| `tests/test_cli_stamp.py::test_stamp_supersedes_invalid_existing_block` | `tests/test_cli_stamp.py::test_stamp_refuses_a_full_block_with_an_invalid_role_with_zero_bytes` | renamed; on the same default-tree fixture (`tests/fixtures/stamp/raw-invalid-block.md`, a full block with `Role: not-a-real-role`) it now expects exit 1, zero bytes written, and the failing field `Role:` named, instead of the supersede; the fixture's prose is updated in Phase 2/3 | D10's stamp clause — operator Packet A, E12 |

### Non-product checks

Run deliberately as explicit workflow gates, never in default test discovery
(the test matrix's *Check classification* lists them): `docs check .` from
the docs root; the live-INDEX snapshot comparison; the Phase 4 / Phase 8
mechanical proof (the `comm` of collected test ids against the pre-Phase-1
commit plus an AST function-body diff of every pre-existing test function —
scratchpad scripts, results in the implementation log); a naming lint over
the new test names; and the Phase 8 hand-applied mutation smoke. The
reference byte-identity and stale-wording checks are product tests, because
the skill and the `--help` text ship.

### Hidden/generalization categories

The repository is fully visible to the implementer, so no private cases exist;
these categories are held as generalization targets, exercised in Phase 9's
dogfood and the property checks rather than enumerated as visible fixtures:
extension vocabularies; non-default `date_format` and `[archive] dir`; nested
subdirectory documents; non-canonical target spellings (`./b.md`,
`sub/../b.md`); non-Markdown and excluded targets; duplicate paths inside one
`docs lifecycle` batch; grammar-boundary verbs; and a real milestone trio in
this repository's own tree. (An archived document mixed into a `docs
lifecycle` batch is a visible test, not a held-back category.)

### Property/stateful invariants

- Applying the same `docs lifecycle` or `relate` invocation twice equals
  applying it once, byte for byte.
- `relate add` then `relate remove` of a free-form edge that was initially
  **absent** restores the original bytes except `Updated:` — whether SOURCE
  started with no `Related:` group (created, then dropped) or a non-empty one.
  From an arbitrary initial state the assertion is the contractual one: the
  edge set afterwards is the initial set minus the edge, and every unrelated
  byte is preserved.
- For every active-tree document and every allowed state, the post-state tree
  has no `status-drift` finding.
- Write footprint, counting editable documents separately from the generated
  INDEX: a no-op or `--dry-run` writes nothing at all, INDEX included; a real
  free-form operation rewrites exactly one managed document, a recognized one
  at most two, and a lifecycle batch exactly the documents whose state
  differed — each followed by one INDEX refresh.

### Mutation-sensitive logic

The `archived` target guard; the archive-subtree source guard; the
current-`archived` source guard; the recognized-versus-free-form branch; the
`if changed` idempotence guard; the no-reindex-on-a-no-op guard, observed
through a sentinel INDEX that must stay byte-identical, with the refreshed
INDEX asserted to reflect the final state (a call counter needs a justified
entry under *Mock policy*); the grammar — `re.fullmatch` versus `re.match`
with `$` (which accepts a trailing newline) and `[0-9]` versus `\d` (which
accepts non-ASCII digits); the config passed to `parse()`; `render_index`'s
extension-role placement; and `docs stamp`'s block classification. Mutation
testing is **not configured** in this project; Phase 8 runs a hand-applied
mutation smoke over these points, the M28a precedent, and records which test
kills each.

### Fuzz targets

The free-form verb grammar, with **valid and invalid inputs generated
independently** from D6's grammar by a fixed-seed, stdlib-only generator:
valid inputs (including trailing and doubled hyphens, digits after the first
letter, and length extremes) must succeed and be read back by `parse()` as the
identical verb; invalid inputs (uppercase letters, a leading digit or hyphen,
spaces, `:`, embedded and trailing newlines, punctuation, and non-ASCII
letters and digits) must refuse with zero bytes written. A generator that only
fed printable strings and checked "refuses or round-trips" could not tell an
over-accepting grammar from a correct one.

### Benchmark/security/schema checks

- Schema: the `docs lifecycle --json` key set and the free-form `relate
  --json` key set are asserted closed; the recognized-verb record is asserted
  unchanged.
- Security: the metadata-injection refusals (`:` and newline in a verb) and
  TARGET containment.
- Benchmark: not applicable; Phase 9 records runtime over this tree.

### Mock policy

- New or expanded mocks: none. Phase 1 (OQ-2) made the multi-file
  `docs lifecycle` write sequential, as `project set` does, with no staged
  publish or rollback, so no write-failure injection was needed. The Phase 8
  audit found 0 new or expanded mocks.
- Justification: not applicable. L12's INDEX-refresh failure uses a real
  malformed sibling.
- Real-path test covering the same behavior: every success and refusal path is
  covered by subprocess tests on real trees.

## Test Matrix

Link: [lifecycle-and-free-form-relate-test-matrix.md](lifecycle-and-free-form-relate-test-matrix.md)
— its *Decision ↔ clause crosswalk* maps each D-id here to the matrix's C-ids.

## Deliverables

Each deliverable names its consumer. The end consumer of the whole milestone is
an agent running a suite workflow — first the Agent Playbook Suite's
`create-milestones` setup, through the suite release that pins this version.

- [ ] Flag/exit/message matrix for `docs lifecycle` and free-form `relate`
      frozen in Phase 1 — against the answered Q1–Q9, including the verb
      grammar (Q3), the state vocabulary and D10's `parse()` signature (Q7),
      the two `--json` records and the Phase-5 signatures. Consumer: Phases 2–7.
- [ ] `docs lifecycle` with refusal, idempotence and reindex tests. Consumer:
      the agent promoting a scaffold; the suite's lifecycle probe.
- [ ] One-sided free-form `relate add|remove` with recognized-verb
      regression coverage — archived SOURCE refused, archived TARGET never
      written, any existing file as TARGET. Consumer: the agent linking
      companions; the suite's relate probe.
- [ ] Cascade-candidate and strand-check regression locks. Consumer: every
      later milestone closeout.
- [ ] The `--body-from` leading-`Related:` route locked by test and stated in
      `cli.md`, and the skill's two sidecar examples rewritten to a form that
      works. Consumer: the bundled skill's sidecar use case.
- [ ] `parse()` honours the tree's config (D10): vocabulary extensions and
      `date_format` at all seven existing call sites and in both new verbs,
      with locks across every verb that reads the tree, a bare call keeping
      the built-in defaults, and no verb starting to refuse a document
      `docs check` accepts; `render_index` rendering extension-role groups after the
      built-in ones; and `docs stamp` refusing a full block that fails the
      configured vocabulary or date format.
      Closes the 2026-08-15 `date_format` and 2026-10-26 vocabulary entries in
      `feedback-log.md`. Consumer: adopters with extension vocabularies or a
      non-default date format, and both new verbs.
- [ ] Surface parity: argparse help, `cli.md`, `convention.md`, bundled
      skill + byte-identical references, CHANGELOG — plus the skill's *Three
      things never to hand-edit*, `references/use-cases.md`, the adoption
      playbook's stale heuristic description, and the README verb list.
      Consumer: every agent and adopter reading the shipped surface.
- [ ] `pyproject.toml` and the packaging version pin at **2.1.0**, and a
      `## 2.1.0 — UNRELEASED` CHANGELOG section with the upgrade note.
      Consumer: the publish milestone.
- [ ] Dogfood the primary use case on a throwaway copy of this tree.
      Consumer: acceptance.
- [ ] Hand-off note for the publish milestone: its closeout sweep must
      retire the Agent Playbook Suite verbless-metadata stopgap (below),
      written to a live home that outlives this milestone's archive (D9).
      Consumer: the publish milestone and the suite pin-bump PR.
- [ ] Test matrix and adequacy results. Consumer: closeout review.

## TDD implementation plan

### Phase 1 — Define Contract

- Objective: freeze — against the answered Q1–Q9 — `docs lifecycle`'s
  grammar, state vocabulary, refusal set and order, idempotence and reindex
  rules, output lines and `--json` record; free-form `relate`'s grammar, its
  endpoint rules (archived SOURCE, archived TARGET, non-Markdown TARGET), its
  one-sided write, its `--json` record and its messages; the statement that
  recognized-verb `relate` is byte-for-byte unchanged; the `--body-from`
  sentence; D10's config-aware `parse()` signature and how its sites obtain
  the config (D10's behaviour, `render_index` placement and `docs stamp`
  refusal are frozen already); the stamp refusal's message; argparse's
  handling of a leading-hyphen verb; the upgrade note's three D10 changes;
  the full surface list; and the Phase-5 signatures. No business
  logic lands, and Phase 1 does not re-open the setup decisions.
- Files: `docs/cli.md` (a new `docs lifecycle` section; the `relate`
  section's verb paragraph, *Archived endpoints*, *Output*, *Exits* and
  *Non-goals*; the `--body-from` paragraph; the exit-code summary),
  `docs/convention.md` (the Lifecycle table's route for changing lifecycle;
  *Extending vocabularies* and *Archive subtree*, which gain the statement that
  every verb honours the configured vocabulary and `date_format`;
  *Relationship verbs* and *Reciprocal relationship verbs*' "repair with
  `docs relate`" paragraph), the two byte-identical mirrors under
  `src/docs_cli/skill/references/`, and this milestone's *Decisions (Phase 1
  — BINDING)*. Signatures are frozen here rather than stubbed in `cli.py`,
  following the M25–M28a precedent.
- Exit: specs, messages and frozen signatures internally consistent; no
  behaviour change; the suite still **1504** GREEN; `docs check` exit 0.

### Phase 2 — Write Tests (RED)

- Objective: express every clause of the frozen contract as a failing test
  before implementation, including the locks that must stay GREEN at
  baseline (recognized-verb `relate` byte-for-byte, the `--body-from` route,
  a bare `parse()` keeping the built-in defaults, and `docs stamp`'s
  unrelated-failure path). The archive invariance tests and both suite-probe
  replicas need free-form `relate` to build or pass their trees, so they are
  RED at baseline, not locks (Phase 1 resolution OQ-9).
- Files: `tests/test_cli_lifecycle.py` (new), `tests/test_lifecycle_plan.py`
  (new — the pure planner, Phase 1 resolution OQ-12), `tests/test_cli_relate.py`,
  `tests/test_relate_plan.py`, `tests/test_cli_archive.py`,
  `tests/test_body_from.py`, `tests/test_skill.py`, `tests/test_packaging.py`,
  and, for D10, `tests/test_cli_index.py`, `tests/test_cli_list.py`,
  `tests/test_cli_touch.py`, `tests/test_walker.py`, `tests/test_model.py`,
  `tests/test_cli_project_set.py`, `tests/test_cli_project_rename.py`,
  `tests/test_cli_stamp.py` (byte-level zero-write locks for the
  extension-vocabulary and E11 tree shapes), `tests/test_index.py` and
  `tests/test_cli_mv.py`.
- Exit: the new tests are RED **only** for missing M30 behaviour; the
  pre-existing tests in *Test Strategy* › *Pre-existing tests that change*
  are edited exactly as listed, with their reason recorded; every other
  pre-existing id is untouched; no collection errors.

### Phase 3 — Create Data/Fixtures

- Objective: provide the trees the tests need, one semantic each.
- Files: inline `tmp_path` builders for every write-then-byte-compare case
  (the M25 rule — a committed tree would be copy overhead); the archive
  invariance locks copy the existing `archive-neighborhood` and
  `movelink-strand` trees and rewrite their edges through `relate` rather
  than committing duplicates; for D10, one committed `vocab-extension/` tree
  (extension lifecycles and roles) if a walk-level assertion needs it, with
  the fixture-sweep registration updated in the same change; every
  non-default `date_format` case as an inline builder; and the
  `tests/test_cli_mv.py` `_attic_tree` builder corrected to the tree's own
  date format; and the prose of `tests/fixtures/stamp/raw-invalid-block.md`
  updated to describe the refusal its renamed test now expects.
- Exit: fixtures parse deterministically, are structure-only (never
  date-sensitive at run time), and every pre-M30 fixture tree stays
  byte-identical with zero new findings.

### Phase 4 — Run Tests (RED Baseline)

- Objective: prove the new tests fail for the intended missing behaviour and
  for nothing else.
- Files: implementation log only.
- Exit: full baseline with exact counts; zero collection errors, tracebacks
  and xfails; every one of the **1504** pre-existing ids mechanically proven
  present through the explicit old → new mapping in *Pre-existing tests
  that change*; every GREEN-at-baseline lock classified. Risk is Standard (Q8), so there is no operator checkpoint
  here; Phase 5 starts once these exit criteria hold.

### Phase 5 — Update Base Interfaces

- Objective: add the pure pieces without wiring a verb — the free-form verb
  validator; the one-sided planning path (`RelatePlan` carrying
  `inverse: str | None` and one edit, or a sibling planner, as Phase 1
  froze); the lifecycle plan record and pure planner; and D10's config-aware
  `parse()` signature with a backward-compatible default.
- Files: `src/docs_cli/cli.py`, `tests/test_relate_plan.py`, and the pure
  lifecycle-plan tests.
- Exit: interfaces typecheck and are unit-tested; `_cmd_relate` is unchanged
  and `docs lifecycle` is unregistered, so the CLI tests stay honestly RED at
  the seam; `docs check` exit 0.

### Phase 6 — Implement Offline/Core Path

- Objective: wire both verbs — register `docs lifecycle` and implement its
  command over the planner; route `_cmd_relate`'s free-form verbs to the
  one-sided path with D5's endpoint rules and D6's grammar; pass the tree's
  config at all seven `parse()` call sites and the new verbs' sites (D10).
- Files: `src/docs_cli/cli.py` and the CLI test modules.
- Exit: core and integration tests GREEN; recognized-verb behaviour
  byte-stable; the archive invariance locks GREEN; `docs check` exit 0 on this
  tree.

### Phase 7 — Update Tool/Wrapper Layer

- Objective: reconcile every parallel surface — argparse descriptions (the
  `relate` namespace's "free-form verbs stay hand-edited" sentence, the `relate
  add` / `relate remove` help, the new `lifecycle` help); `cli.md` and
  `convention.md` final wording; the bundled `SKILL.md` (description verb list,
  verb table rows, *Three things never to hand-edit* naming `docs lifecycle`
  and free-form `docs relate`); `references/use-cases.md` (new rows; its "and
  `relate` refuses to edit them" sentence; the sidecar row naming both routes);
  `references/adoption-playbook.md`'s stale heuristic description; both
  skill sidecar examples rewritten from the inline `Related: artifact-of:`
  form to the frozen text in *Decisions (Phase 1 — BINDING)* › P1.3;
  `references/quality-artifacts.md` *Linking reports* and `SKILL.md`'s
  *Quality artifacts* paragraph, which today hedge on whether a
  non-Markdown `Related:` target is accepted and now name `docs relate add
  <companion> references <report>` (Phase 1 resolution OQ-14); `cli.md`'s
  `docs stamp` idempotence paragraph and exit codes (written in Phase 1);
  both
  byte-identical mirrors; the README verb list; `pyproject.toml` and the
  packaging pin at 2.1.0; the `## 2.1.0 — UNRELEASED` CHANGELOG section with
  its upgrade note (all three behaviour changes, D9); and dated notes on
  `feedback-log.md` — the 2026-10-26 promotion entry recording the answers,
  and the 2026-08-15 `date_format` and 2026-10-26 vocabulary entries recording
  their closure by D10 — as M28 and M28a closed issue #1.
- Files: `src/docs_cli/cli.py` (help strings only), `docs/cli.md`,
  `docs/convention.md`, `src/docs_cli/skill/` (`SKILL.md`,
  `references/use-cases.md`, `references/adoption-playbook.md`,
  `references/quality-artifacts.md`, both mirrors),
  `README.md`, `CHANGELOG.md`, `pyproject.toml`, `tests/test_packaging.py`,
  `docs/feedback-log.md`.
- Exit: subprocess, reference byte-identity and skill-parity tests GREEN;
  `docs lifecycle --help`, `docs relate --help` and `cli.md` agree; a grep for
  wording describing the replaced behaviour ("free-form verbs stay
  hand-edited", "refuses to edit them", "Only the six recognized verbs") over
  the docs, the skill and the output of `docs relate --help`, `docs relate
  add --help` and `docs relate remove --help` finds nothing.

### Phase 8 — Run Tests (GREEN)

- Objective: run the focused and full suites plus lint, format, types,
  reference byte identity and docs integrity, and the Standard-risk gates.
- Files: implementation log only unless a real defect is found.
- Exit: all gates GREEN with exact counts; every pre-existing id mechanically
  proven present and GREEN through the old → new mapping in *Pre-existing
  tests that change*; property checks, the
  grammar fuzz and the hand-applied mutation smoke recorded; mock audit
  complete.

### Phase 9 — Integrate / Accept / Dogfood

- Objective: on a throwaway copy of this docs tree, run the primary use case
  end to end — scaffold a milestone trio with `docs new`, link it with `docs
  relate add` (companion `pairs-with` both ways, `child-of:
  milestone-plan.md`, `implements: charter.md`), promote all three with one
  `docs lifecycle … active`, and pass `docs check` with zero hand-edits and
  zero prompts. Replay both suite CI probes against the editable build and a
  locally built wheel. Preview and apply a closeout of the `relate`-linked trio
  and compare its plan with a hand-linked twin. Confirm the archive refusals.
  Repeat the use case on an extension-vocabulary tree and a
  non-default-`date_format` tree (D10) — including a `docs stamp` of an
  extension-state document, which must change only `Updated:`, and an
  extension-role document, which must appear in the INDEX — and confirm this
  repository's tree reindexes byte-identically. Measure the added runtime. The real tree is
  never written to.
- Files: throwaway trees only; the committed docs record the evidence.
- Exit: every flow runs unattended; the use case needs no hand-edit; both
  probes pass; the closeout plans are identical; runtime recorded; the real
  tree untouched.

### Phase 10 — Quality, Docs, Refactor

- Objective: `/simplify` over the new verb and the relate branch; close
  `architecture.md` (a `lifecycle` module entry and the `relate` section's
  one-sided path) and `test-strategy.md` (critical paths: no lifecycle
  transition reaches `archived`; a free-form operation writes one file);
  write the hand-off note to its live home; complete the taste triage and the
  boundary sweep; write the completion summaries.
- Files: code and docs as justified, this milestone and the implementation
  log.
- Exit: full gate GREEN; no placeholders; the hand-off note lives outside the
  archive scope; ready for the explicit-scope closeout
  `docs archive lifecycle-and-free-form-relate.md --cascade-only
  'lifecycle-and-free-form-relate-*'`.

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
- [ ] Phase 10 — Quality, Docs, Refactor

## Decisions carried from discovery

- Lifecycle gets a verb, not a second sanctioned hand-edit exception
  (operator, 2026-10-26).
- Free-form edges are written one-sided by `docs relate`; no new symmetric
  pair, so `missing-inverse` reports nothing new on any existing tree
  (operator, 2026-10-26).
- Stopgap: the Agent Playbook Suite drops its hand-edit carve-outs and asks
  the operator until this ships (operator, 2026-10-26).
- The charter's *run the verb* principle weakens with every carve-out, and a
  verb lets `docs check` stay the only arbiter (`feedback-log.md`, 2026-10-26,
  *Candidate, finding 1*).
- `child-of` / `parent-of` were deliberately kept out of reciprocal
  validation, and `pairs-with` / `child-of` feed the archive candidate set and
  the strand refusal; any change must respect both (`feedback-log.md`,
  2026-10-26, *Open design question, finding 2*).
- The tool refuses what it can prove is wrong and asks only about what it
  genuinely cannot determine; a check that fires on correct trees is one
  operators route around (`feedback-log.md`, *Underlying principle*; the
  charter's *never cry wolf* criterion as applied in M28 and M28a).
- Archived documents are immutable except through the three named, narrow
  exceptions `convention.md` enumerates.
- The bundled skill updates in the same change as the surface; host skills
  refresh only at a production ship (`CLAUDE.md`, *Skill update flow*).

## Decisions recorded at setup (BINDING)

Three setup findings change something already written down — one registered
binding clause, one registered recommendation, and one registered statement of
the current state. They are restated here so a Phase-1 agent with none of the
setup conversation can reconstruct what was decided, what it replaced, and why.

### A1 — The extension-state clause meets a pre-existing defect

The registered binding scope says `docs lifecycle` sets "any top-level state
(`draft`, `active`, `blocked`, `done`, `superseded`, plus any `add_lifecycles`
extension), bumps `Updated:`, and reindexes once".

**On 2.0.0 those two promises cannot both hold.** E7 measured that one
document carrying an `add_lifecycles` state makes `docs index` exit 2, makes
every reindexing verb exit 2 after it has written, drops the document from
`docs list`, and makes `docs relate` refuse it as an endpoint — while `docs
check` exits 0. A verb that writes such a state and then reindexes reproduces
that failure deliberately, on every call. The cause is not in anything M30
adds: `parse()` validates `Lifecycle:` and `Role:` against the built-in sets
rather than the tree's config, and E8 shows the same function parsing
`Updated:` with the ISO default rather than the tree's `date_format`.

**Resolved by the operator (Q7 → A, 2026-10-27).** The clause stands as
registered, and the cause comes into scope as **D10**: `parse()` honours the
tree's configured vocabulary and `date_format` at every call site, so the
verb never writes a state its own reindex then rejects, and no verb starts
refusing a document `docs check` accepts (E11).

### A2 — The registered verb-syntax recommendation rests on a premise the parser does not satisfy

The registered Open question 3 recommends: *accept exactly the token grammar
`docs check` already parses for `Related:` bullets, and refuse anything
`docs check` would reject.*

**`docs check` parses no token grammar.** E4 measured that it accepts any text
before the first colon, stripped: an empty verb, `see also`, `@#!$` and
`Precedes` all pass at exit 0. Taken literally, the recommendation would let
`relate` write `- : target.md`, and E5 shows it would turn today's refusal of a
mistyped `Precedes` into a silent one-sided edge. The registered binding
bullet's "any free-form verb (anything other than the six recognized
reciprocal verbs)" has the same reach.

**Resolved by the operator (Q3 → option (c), 2026-10-27).** The half of the
recommendation that holds — never write a bullet `docs check` would reject or
re-read differently — is subsumed by **D6**'s strict grammar,
`[a-z][a-z0-9-]*`, which admits only verbs that round-trip unchanged and
refuses every case variant of a recognized verb without a special case. The
registered bullet's "any free-form verb" is read as "any free-form verb the
grammar admits".

### A3 — A creation-time route for free-form edges already exists, and is documented

The registered *Current state and risks* says 2.0.0 has no verb that writes a
free-form `Related:` bullet, and the feedback log's promotion observation asks
whether the `--body-from` route is *"a supported path to document or an
accident to pin"*.

**The bundled skill answered that in M8 — in intent.** E6 found the route
prescribed in `references/use-cases.md` (*Sidecar a non-md artifact* — "No new
verb — uses the M8 `--body-from` flag") and in `references/adoption-playbook.md`,
with no test behind it. The Step 0 review then found that both examples spell
`Related:` inline, which the grammar reads as body text; only the group form
works. The current-state statement is therefore narrowed to *on an existing
document*, and the observation is resolved as D8: supported in its group form,
locked, stated in `cli.md`, and with both skill examples corrected in Phase 7.

## Decisions (Phase 1 — BINDING)

Frozen 2026-10-27. The authoritative surface lives in `cli.md` — *Invocation*
› *The tree's configured vocabulary and date format*; `docs new` ›
`--body-from`; `docs index`; the new `docs lifecycle` section; `docs relate`;
`docs stamp`; *Exit codes (summary)* — and in `convention.md` — *Required
fields*; *Lifecycle* › *Changing lifecycle*; *Extending vocabularies*;
*Relationship verbs* › *Writing an edge*; *Reciprocal relationship verbs*;
*Archive subtree*. This section records what Phase 1 decided, why, and the
Phase-5 signatures; where it and the specs disagree, the specs win. Nothing
here re-opens D1–D10, Q1–Q9, operator Packet A or the Step 0 resolutions.
The fifteen Phase-1 questions and their conductor resolutions close the
section.

### P1.1 — `docs lifecycle` (D1–D3)

**Argparse.** A top-level subparser with `parents=[common]` (`--root`,
`--quiet`, `--dry-run`), one positional `"args", nargs="+", metavar="file ...
state"` and a local `--json`, registered after `stamp` and before `project`,
and dispatched in `_dispatch`. A single `nargs="+"` run split as
`*files, state` inside the command — `docs project set`'s shape, because
argparse cannot split a variadic run from a trailing positional.

**Paths (OQ-1, OQ-13).** A relative `<file>` resolves against the resolved
docs root; an absolute one is used as given (`_cmd_project_set`'s rule). The
root-relative path `rel` is computed from the resolved location, and the
document is read, parsed and written through `root / rel` (`relate`'s
precedent), so a named symlink inside the tree edits the file it points at
and every message after resolution names `rel`.

**Refusal order** — `_cmd_project_set`'s, with D2's two archive guards:

| Step | Check | Exit |
|---|---|---|
| L1 | fewer than two positional tokens | 2 |
| L2 / L3 | strict root: `_resolve_managed_root(args, Path.cwd(), verb="lifecycle")` | 2 |
| L4 | `.docs.toml` does not parse | 2 |
| L5 | `state == "archived"` — tested explicitly **before** membership, because `archived` is in `config.lifecycles` | 2 |
| L6 | `state` not in `config.lifecycles - {"archived"}` — exact, case-sensitive, so `Archived` is an unknown state | 2 |
| L7 | archive-subtree pre-pass over **every** named document, independent of argument order (`_is_archived_rel` on the resolved path; a path outside the root is skipped here and refused at L8) | 2 |
| L8–L10 | per document, in argument order: outside the root, missing, fails `parse(..., config=config)` | 1 |
| L11 | any parsed document whose current `Lifecycle:` is `archived` — refused naming the first in argument order | 2 |

Then: deduplicate on `rel` keeping the first occurrence (OQ-3); plan; a
whole-batch no-op or `--dry-run` returns 0 after printing; otherwise write
each changed document, print the lines, reindex once, emit the record.

**Message catalogue** (stderr; every refusal prints even under `--quiet`):

| Id | Exit | Message |
|---|---|---|
| L1 | 2 | `docs: lifecycle: need at least one <file> and a <state>` |
| L2 | 2 | `docs: lifecycle: <cwd> is not under a docs root with .docs.toml; refusing` |
| L3 | 2 | `docs: lifecycle: --root <dir> does not contain .docs.toml; refusing` |
| L4 | 2 | `docs: malformed .docs.toml: <detail>` |
| L5 | 2 | `docs: lifecycle: 'archived' is not a lifecycle target — docs archive <file> moves lifecycle and location together; refusing` |
| L6 | 2 | `docs: lifecycle: unknown state '<state>'; expected one of: <states>` — `<state>` rendered with `!r`; `<states>` the configured vocabulary minus `archived`, sorted, `", "`-joined |
| L7 | 2 | `docs: lifecycle: <rel> is under the archive subtree (read-only); refusing` |
| L8 | 1 | `docs: lifecycle: <path> is outside the resolved docs root (<root>)` |
| L9 | 1 | `docs: lifecycle: file not found: <path>` |
| L10 | 1 | `docs: <path>: <parser detail>` — the parser's self-locating message |
| L11 | 2 | `docs: lifecycle: <rel> reads 'Lifecycle: archived' outside the archive subtree (status-drift); refusing — only docs archive sets archived` |
| L12 | 2 | `docs: INDEX refresh failed: <detail>` — after the documents were written |

`<path>` in L8–L9 is the path as resolved for the check (`root / <given>`,
or the absolute path given); `<root>` is the resolved root.

**Success lines** (stderr, suppressed by `--quiet`; one per distinct named
document in first-seen order; printed after the writes and before the
reindex — `relate`'s order, so a reindex failure follows the record of what
landed):

- `docs: lifecycle: set <rel> from <before> to <state>`
- `docs: lifecycle: would set <rel> from <before> to <state>` (under `--dry-run`)
- `docs: lifecycle: no change — <rel> is already <state>`

**`--json` record.** One object, the same shape for preview and apply,
emitted whenever validation passed (never on a refusal):

```
{"state", "date", "dry_run", "applied", "index_refreshed",
 "edits": [{"path", "before", "change"}]}
```

`change` is `"set"` or `"unchanged"`; `edits` follow first-seen argument
order, deduplicated; `date` is the value written to each changed document;
`applied` is false for a dry run and for a whole-batch no-op; on an
INDEX-refresh failure the record is still emitted, with `"applied": true,
"index_refreshed": false`. The redundant `updated_bumped` (it equals
`change == "set"`) and `after` (it equals `state`) keys are deliberately not
in the record — no consumer needs them.

**Edits.** Only documents whose state differs are edited:
`set_metadata_field(text, "Lifecycle", state)`, then
`set_metadata_field(…, "Updated", date_str)` — `_archive_one`'s order — with
`date_str = date.today().strftime(config.date_format)` computed once.

**Writes (OQ-2).** Sequential `atomic_write` per changed document, in
first-seen order — `_cmd_project_set`'s precedent; no staged publish and no
new failure-injection mock. One reindex:
`_refresh_index(root, config, predicate=compile_exclude_predicate(config, []))`.

**Also frozen.** An excluded document may be named and is written; the
reindex still honours the exclusion. No `--date` flag; no coupling to
`Related:`; `docs lifecycle` never calls another verb's command function.

### P1.2 — free-form `docs relate` (D4–D6)

**Grammar.** `relate_verb_in_grammar(verb)` is
`_RELATE_VERB_RE.fullmatch(verb) is not None` with
`_RELATE_VERB_RE = re.compile(r"[a-z][a-z0-9-]*")`. `fullmatch`, never
`match` with `$` (which accepts a trailing newline); `[0-9]`, never `\d`
(which accepts non-ASCII digits). The six recognized verbs are inside the
grammar.

**Order in `_cmd_relate`** — every step before planning writes nothing:

1. root (`_resolve_managed_root`), 2. config, 3. **grammar** → R1, exit 2;
4. resolve `SOURCE`, parsed with the config → exit 1;
5. resolve `TARGET` — parsed only for a recognized verb → exit 1;
   5a. **free-form only:** a `TARGET` path a bullet cannot carry → R4, exit 2
   (added by the Step 1 review — conductor decision JC1, below);
6. self-edge → exit 2, unchanged message;
7. **free-form only:** an archived `SOURCE` → R2, exit 2 — in the slot where
   today's archived-endpoint `--reason` rule sits and before planning, so a
   no-op refuses too;
8. `--reason` shape, when the flag is present (unchanged messages);
9. **recognized only:** an archived endpoint without `--reason` (unchanged);
10. `--date`; 11. plan, apply, print, reindex, emit.

For a recognized verb the sequence is exactly today's: R1 replaces the old
`unknown verb` refusal, which a recognized verb never reaches.

**Messages.**

| Id | Exit | Message |
|---|---|---|
| R1 | 2 | `docs: relate: unknown verb '<verb>'; expected a reciprocal verb (blocked-by, blocks, depends-on, follows, precedes, required-by) or a free-form verb matching [a-z][a-z0-9-]*` — `<verb>` rendered with `!r`, so a verb carrying a newline stays on one line |
| R2 | 2 | `docs: relate: <rel> is under the archive subtree; a free-form edge is never written to an archived document` |
| R3 | 2 | a verb starting with `-` is consumed by argparse as an option: an argparse usage error (measured on Python 3.12: `docs relate add a.md -x b.md` → *the following arguments are required: TARGET*; `-1x` the same), nothing written. After `--`, or as a bare `-`, the verb reaches the command and refuses with R1. The usage text is argparse's and is not frozen beyond "exit 2, usage error, zero bytes". |
| R4 | 2 | `docs: relate: TARGET '<rel>' cannot be written into a Related: bullet — it contains a line break or leading or trailing whitespace; refusing` — `<rel>` (the free-form TARGET's root-relative path) rendered with `!r`; fires when `len((rel + "x").splitlines()) != 1` (any boundary `str.splitlines()` recognises) or `rel != rel.strip()`. Added by the Step 1 review (conductor decision JC1, below) |

**TARGET rules.** For a free-form verb `TARGET` is resolved exactly as
today — root-relative first, then cwd — and must be `candidate.is_file()`
with its resolved path contained in the root; it is **never read**. A binary
or non-Markdown file is fine; a directory, a missing file, or a path outside
the root (including through an escaping symlink) keeps today's exit-1
messages. A symlink inside the tree is resolved, as for every endpoint: the
bullet names the root-relative file it points at. A resolved path a bullet
cannot carry refuses with R4. `SOURCE` always parses (with the config); for a
recognized verb both endpoints parse.

**Post-review amendment — R4 (Step 1 review-pass-001, claude-S2; conductor
decision JC1, under Standard-risk authority).** A free-form TARGET's
root-relative path is written verbatim into SOURCE's bullet, so a path
holding a line break would end the metadata block (the injection D6 closes
for the verb), and leading or trailing whitespace would be read back
stripped — a different target. Free-form `relate` therefore refuses such a
TARGET (R4) after resolving it and before the self-edge check. Recognized
verbs stay byte-for-byte unchanged, as D4 binds: the same injection through a
recognized verb (measured: `docs relate add a.md precedes $'b\nLifecycle:
archived\nx.md'` exits 0 and corrupts `a.md`) is recorded as *Follow-ups*
item 9, not fixed here, and no lock freezes it. The alternative — extending
the refusal to recognized verbs — would override D4 and was not taken.

**Archived endpoints.** An archived free-form `TARGET` needs no `--reason`
and never gets a `Revision:` bullet; `--reason` is still shape-checked when
given and echoed in the record. M25 — D4's exception stays recognized-only.

**Record.** The same eleven keys as today, with `"inverse": null` and
`edits` holding exactly one entry, the source's. `_print_relate_lines` is
unchanged (it prints one line per edit, so a free-form run prints one).
The recognized-verb record is unchanged byte for byte.

**Byte stability (OQ-6).** Recognized verbs are byte-for-byte unchanged on
every tree `docs check` passes. Two D10 qualifications, both stated in D4 and
C7: on a tree with vocabulary extensions or a non-default date format, an
endpoint 2.0.0 refused at exit 1 now resolves; on the E11 shape — a tree that
already fails `docs check` with `bad-date` — an endpoint 2.0.0 accepted now
refuses at exit 1 with that same diagnosis.

### P1.3 — the `--body-from` route and the skill's sidecar examples (D8, OQ-7)

**`cli.md`** (written): a body whose first block is `Related:` alone on its
line, immediately followed by `- <verb>: <target>` bullets, becomes part of
the metadata block; an inline `Related: verb: target` line stays body text; a
recognized reciprocal verb written this way is one-sided until
`docs relate add` completes the pair; the C4 refusal heuristic is unchanged.

**The skill's two examples — frozen text for Phase 7.** In
`references/use-cases.md` the *Sidecar a non-md artifact* row becomes:

````markdown
| Sidecar a non-md artifact | `docs new <role> <slug> --body-from -`, then `docs relate add <sidecar> artifact-of <binary>` | When an HTML / XLSX / ODT is referenced from prose and warrants tracking, author a `.md` sidecar; the original binary stays where it is. `docs relate add <sidecar> artifact-of <binary>` writes the one-sided free-form edge on the sidecar alone — the binary is never read or written. To write the edge at creation time instead, open the `--body-from` body with a `Related:` group (`adoption-playbook.md` shows it); an inline `Related: artifact-of: <binary>` line is body text, not an edge. |
````

In `references/adoption-playbook.md` the *Sidecars for non-md binaries*
bullet becomes (its stale `^[A-Z][A-Za-z-]+:\s` heuristic line replaced by
the M15 — C4 description):

````markdown
- **Sidecars for non-md binaries (M8 F7 + F9).** When a non-md
  file (a slide deck, a spreadsheet) is referenced from prose,
  author a Markdown sidecar that carries the convention's
  metadata and links the binary. Write the edge at creation
  time by opening the `--body-from` body with a `Related:`
  group — the label alone on its line, then the bullet:

  ```sh
  docs new <role> <slug> --body-from - <<'EOF'
  Related:
  - artifact-of: <binary>

  ## Summary

  What the artifact is and why it is tracked.
  EOF
  ```

  On a sidecar that already exists, run
  `docs relate add <sidecar> artifact-of <binary>` instead. An
  inline `Related: artifact-of: <binary>` line is body text, not
  an edge. `docs new` refuses a body only when it carries a real
  metadata block — a leading `---` fence, or two or more of
  `Lifecycle:` / `Role:` / `Updated:` on adjacent lines — so pass
  body content only; `docs new` owns the frontmatter.
````

**Extraction contract** (`tests/test_body_from.py`, one id per form). The
relate form: the `use-cases.md` line beginning `| Sidecar a non-md artifact
|` carries the inline code span `` `docs relate add <sidecar> artifact-of
<binary>` ``; the test takes that span, substitutes `<sidecar>` → `deck.md`
and `<binary>` → `deck.html`, and runs it against a tree holding a scaffolded
`deck.md` and a `deck.html`. The group form: after the playbook line
beginning `- **Sidecars for non-md binaries`, the first fenced `sh` block,
dedented, opens with `docs new <role> <slug> --body-from - <<'EOF'`; its body
is every following line up to the line `EOF`; the test substitutes `<role>`
→ `notes`, `<slug>` → `deck`, `<binary>` → `deck.html` and runs the command
with that body on stdin. Both must leave `deck.md` carrying
`artifact-of: deck.html` in `docs list --json` and `docs check` exiting 0.
The wording around the two extracted spans is Phase 7's to polish; the two
spans and the row and bullet they sit in are frozen.

### P1.4 — `parse()` honours the tree's config: signature and call sites (D10)

`parse(text, path, root, *, config: Config | None = None) -> Doc` —
keyword-only, following `parse_date`'s `label` precedent, so no positional
caller can be silently re-bound. With `None` it keeps the built-in
vocabulary and the ISO format (every bare call and existing unit test is
unaffected); with a config it validates against `config.lifecycles` and
`config.roles` and parses `Updated:` in `config.date_format`. `archived`
stays `False` inside `parse()` (callers set it). Error messages are
unchanged, so a vocabulary or date failure stays byte-identical to
`check_doc`'s `bad-vocab` / `bad-date` text (OQ-6).

| Site | Where its config comes from |
|---|---|
| `walk` (`index`, `touch`, `archive`, `mv`, `project rename`, every end-of-run reindex) | its existing `config` parameter — every caller already passes one |
| `query_docs` (`list`) | its existing parameter |
| `_cmd_archive` (the primary) | already loaded |
| `_known_projects` (`project set`'s typo guard) | its existing parameter |
| `_cmd_project_set` | already loaded |
| `_cmd_stamp` | already loaded |
| `_resolve_relate_endpoint` | a **new** `config` parameter, passed by `_cmd_relate` |
| `_cmd_lifecycle`, `plan_lifecycle` | loaded / passed in |

No new `load_config` call is needed anywhere.

### P1.5 — `docs stamp` refuses a complete block that fails the tree's config (D10, Packet A)

Classification, per named file, inside the existing validate-all-first loop:

1. `parse(text, fp, root, config=config)` succeeds → **already stamped**:
   refresh `Updated:` only (an extension-state document lands here).
2. Otherwise `_stamp_config_failure(text, config)`: when the block is
   **complete** — `parse_metadata_block` succeeds and `Lifecycle`, `Role`
   and `Updated` are each present as a single non-empty string (`Project` is
   not required, matching `parse()`) — it validates them in `parse()`'s
   order (`Lifecycle`, `Role`, `Updated`) against the config and returns the
   first failure's message; otherwise `None`.
3. A message → refuse: exit 1, before any write of the batch, `--dry-run`
   included. `None` → today's fresh stamping (no block, a block missing a
   field, or a complete block failing `parse()` for an unrelated reason such
   as a malformed `Related:` bullet).

Message: `docs: stamp: <path>: <failure>; the file already carries a
complete metadata block — refusing to re-stamp it (run docs check, correct
the field, then docs touch)`, `<path>` as `stamp`'s other messages print it.
`cli.md`'s pre-existing "four required fields" is corrected to three plus
`Project:` (OQ-10), and its exit rows gain the refusal (and the INDEX-refresh
exit 2 the code already had).

### P1.6 — `render_index` (D10, frozen at Step 0)

Per project: iterate `role_order + sorted(set(role_groups) - set(role_order))`,
headings `role.title()`, no new `Config` field. Invariant: the rendered
entries equal the active count in the summary line.

### P1.7 — the upgrade note (D9) — Phase 7's CHANGELOG draft

Under `## 2.1.0 — UNRELEASED`:

- **Added:** `docs lifecycle <file>... <state>` — sets a top-level lifecycle
  state, bumps `Updated:` where it changed, reindexes once; never `archived`.
- **Changed:** `docs relate add|remove` writes a free-form verb within
  `[a-z][a-z0-9-]*` one-sided, on `SOURCE` alone, where 2.0.0 refused every
  verb outside the six reciprocal ones; case variants and other out-of-grammar
  verbs still refuse at exit 2, now by grammar, and the `unknown verb`
  refusal's tail names the grammar; a free-form `TARGET` may be any existing
  file whose path a bullet can carry.
- **Changed:** on a non-default `date_format` tree whose documents still carry
  dates in another spelling — a tree `docs check` already fails with
  `bad-date` — every verb that reads metadata refuses those documents with
  the same `bad-date` diagnosis (`docs list` silently omits them) instead of
  disagreeing with the gate; a recognized-verb endpoint 2.0.0 accepted is
  among them.
- **Changed:** `docs stamp` refuses (exit 1, zero bytes) a file whose complete
  metadata block fails the tree's configured vocabulary or date format, where
  2.0.0 re-stamped it and discarded its lifecycle, role and `Related:` edges.
- **Fixed:** vocabulary extensions and non-default date formats work in every
  verb — on `Lifecycle:`, `Role:` and `Updated:` every verb now judges a
  document exactly as `docs check` does — and extension-role documents appear
  in `INDEX.md`. Structural faults `docs check` tolerates (a malformed
  `Related:` bullet, a multi-valued `Project:`) still fail the verbs that
  parse the document, as before.

`docs check`, every existing record, and every pre-existing refusal other
than the `unknown verb` tail are unchanged.

### P1.8 — the full surface list

Phase 1 writes the two specs (above) and their byte-identical mirrors; the
rest lands in Phase 7 (`architecture.md` and `test-strategy.md` in Phase 10):

- **argparse:** the new `lifecycle` parser and help; the `relate` namespace
  description ("free-form verbs stay hand-edited"); `_add_relate_subverb`'s
  description ("Only the six recognized verbs are accepted") and `VERB` help;
  the `stamp` description (the refusal); optionally the `--body-from` help;
  the `main()` docstring's verb list.
- **`cli.md` / `convention.md`:** written in Phase 1 — the sections listed at
  the top of this section, including the two pre-existing inaccuracies fixed
  here (OQ-10: `docs index`'s "Exits 0 always"; `docs stamp`'s "four required
  fields").
- **`SKILL.md`:** the description gains `lifecycle` (743 of the 1024
  characters the frontmatter test allows are used today); verb-table rows for `docs lifecycle` and free-form
  `docs relate`; *Three things never to hand-edit* names both verbs as the
  route for lifecycle and free-form `Related:` edits; the *Quality artifacts*
  paragraph names `docs relate add` for linking a report (OQ-14).
- **`references/use-cases.md`:** a lifecycle row and a free-form-edge row;
  the "`relate` refuses to edit them" sentence; the sidecar row (P1.3).
- **`references/adoption-playbook.md`:** the sidecar bullet and its stale
  heuristic description (P1.3).
- **`references/quality-artifacts.md`:** *Linking reports* names
  `docs relate add <companion> references <report>` instead of hedging on
  whether a non-Markdown target is accepted (OQ-14).
- README verb list; CHANGELOG (P1.7); `pyproject.toml` and the packaging pins
  at 2.1.0; `feedback-log.md` (the three owned entries, and follow-ups 2, 3,
  7, 8 — OQ-11).

### P1.9 — frozen Phase-5 signatures (contract only — no code lands in Phase 1)

```python
_RELATE_VERB_RE: re.Pattern[str]          # re.compile(r"[a-z][a-z0-9-]*")
def relate_verb_in_grammar(verb: str) -> bool

def parse(text: str, path: Path, root: Path, *, config: Config | None = None) -> Doc

class RelatePlan:  inverse: str | None    # None <=> free-form; then edits == (source,)
def plan_relate(...)                      # signature unchanged; the free-form branch stages
                                          # the source only and never reads TARGET; ValueError
                                          # on an out-of-grammar verb or an archived free-form
                                          # source (programming errors — the CLI refuses first)
def _resolve_relate_endpoint(raw: str, root: Path, root_resolved: Path, config: Config,
                             *, parse_endpoint: bool = True) -> str | int

@dataclass(frozen=True)
class LifecycleEdit:  path: Path; rel: str; before: str; new_text: str; change: str
@dataclass(frozen=True)
class LifecyclePlan:  state: str; date_str: str; edits: tuple[LifecycleEdit, ...]

def plan_lifecycle(root: Path, config: Config, *, files: Sequence[Path], state: str,
                   date_str: str) -> LifecyclePlan
    # reads and parses root / rel with the config; dedupes on rel (first occurrence);
    # an unchanged edit carries new_text equal to the text read; ValueError on an
    # archived or unknown state, a source under the archive subtree, or a source
    # already reading `Lifecycle: archived` (programming errors — the CLI refuses first)
def apply_lifecycle_plan(plan: LifecyclePlan) -> None      # writes only change == "set"
def lifecycle_plan_to_json(plan: LifecyclePlan, *, dry_run: bool, applied: bool,
                           index_refreshed: bool) -> dict[str, object]
def _print_lifecycle_lines(plan: LifecyclePlan, *, dry_run: bool) -> None
def _cmd_lifecycle(args: argparse.Namespace) -> int

def _stamp_config_failure(text: str, config: Config) -> str | None
def render_index(...)                     # signature unchanged
```

**Pull-style interface map** — every output names its consumer:

| Output | Consumer |
|---|---|
| `parse(config=)` | the seven existing call sites, `_cmd_lifecycle`, `plan_lifecycle`; clauses C20–C22 |
| `relate_verb_in_grammar` | R1, the `plan_relate` guard, the grammar fuzz |
| `RelatePlan.inverse = None` | the record's `"inverse": null` (C15) |
| `parse_endpoint` | D5's never-read `TARGET` rule (C10) |
| `LifecycleEdit.path` / `.new_text` | `apply_lifecycle_plan` |
| `LifecycleEdit.rel` / `.before` / `.change` | the success lines and the record |
| `LifecyclePlan.state` / `.date_str` | the record's `state` and `date` |
| `_stamp_config_failure` | C24 |

No speculative output: nothing above lacks a consumer in a clause or a
planned test.

### Resolved Phase-1 questions (OQ-1 … OQ-15)

Raised by the Step 1 planning pass, all conductor-resolved under the
operator's earlier binding decisions; none re-opens D10 or an operator
decision.

1. **OQ-1 — relative paths for `docs lifecycle`.** RESOLVED → P1.1: relative
   to the resolved root, absolute as given — `_cmd_project_set`'s rule.
2. **OQ-2 — multi-file writes.** RESOLVED → P1.1: sequential `atomic_write`
   per changed document (the `project set` precedent); no staged publish, no
   new mocks.
3. **OQ-3 — a path named twice.** RESOLVED → P1.1: deduplicated on the
   root-relative path, first occurrence kept; written once, listed once.
4. **OQ-4 — the grammar refusal's stem.** RESOLVED → R1 keeps
   `docs: relate: unknown verb '<v>'`, so `test_relate_case_variant_verb_refuses`
   keeps its assertion and existing prefix matchers keep working; naming the
   six recognized verbs lets `Precedes` self-correct.
5. **OQ-5 — no repair route for an out-of-vocabulary current value.**
   RESOLVED: `docs lifecycle` keeps exit 1 for a source failing `parse()`; the
   skill sanctions no new hand-edit; *Follow-ups* items 7 and 8 record the
   demand (no verb repairs an out-of-vocabulary `Lifecycle:` / `Role:`;
   `[vocabulary]` entries unvalidated at config load).
6. **OQ-6 — wording that disagreed with D10.** RESOLVED: D4 and C7 state the
   E11 direction; the error table says "the same message `docs check` gives";
   the D9 upgrade note says "every verb that reads metadata". Messages stay
   unchanged.
7. **OQ-7 — what "the skill's literal sidecar example" means for C14.**
   RESOLVED → P1.3: the frozen row and bullet text, and the extraction
   contract.
8. **OQ-8 — a committed `vocab-extension/` tree or inline builders.**
   RESOLVED: one committed `tests/fixtures/trees/vocab-extension/` for the
   vocabulary half (it joins the three directory-derived sweeps in
   `tests/test_check.py` as new ids; no existing id moves), excluded from the
   parse-agreement sweep by a module-local helper named for its behaviour —
   `_trees_without_vocabulary_extensions()` — not for its provenance; every
   non-default `date_format` case stays an inline builder.
9. **OQ-9 — mislabelled locks in the Phase 2 objective.** RESOLVED: the
   relate-written archive-invariance tests and both suite-probe replicas are
   RED at baseline; the objective is corrected.
10. **OQ-10 — two pre-existing `cli.md` inaccuracies.** RESOLVED: both fixed
    in Phase 1 (`docs index` exits; `docs stamp`'s three required fields).
11. **OQ-11 — ledger homes.** RESOLVED: follow-ups 2, 3, 7 and 8 are
    registered in `feedback-log.md` at Phase 7; item 6 is decided at Phase 10.
12. **OQ-12 — a separate `tests/test_lifecycle_plan.py`.** RESOLVED: yes, the
    `test_relate_plan.py` / `test_archive_plan.py` precedent; logged below as
    a deviation from the plan's "one new module".
13. **OQ-13 — symlinked named documents.** RESOLVED → P1.1: `docs lifecycle`
    writes `root / rel`, so a symlink inside the tree edits its real file
    (`relate`'s behaviour), never replaces the link with a regular file.
14. **OQ-14 — missing surface.** RESOLVED → P1.8: `references/quality-artifacts.md`
    *Linking reports* and `SKILL.md`'s *Quality artifacts* paragraph join
    Phase 7's list.
15. **OQ-15 — the renamed packaging ids.** RESOLVED: `test_a3_…` and
    `test_c2_…` keep the a/b/c check-number scheme every neighbour in
    `tests/test_packaging.py` uses, as on the authoritative list.

### Deviations from the plan's file lists (deliberate, logged)

- **Phase 1 makes zero `cli.py` edits** (the M25–M28a precedent): stubs would
  change the Phase-4 subprocess RED reasons. The signatures are frozen in
  P1.9 and land as code in Phase 5.
- **Two new test modules, not one** (OQ-12): `tests/test_cli_lifecycle.py`
  for the CLI and `tests/test_lifecycle_plan.py` for the pure planner.
- **One committed fixture tree** (OQ-8), where *Phase 3* allowed one "if a
  walk-level assertion needs it": about eight modules assert walk-level
  vocabulary behaviour, and `project set` / `project rename` already copy
  committed trees.

## Setup questions (Q1–Q9)

Nine questions were raised at setup, and **all nine are resolved**. **Six**
are conductor decisions determined by the convention, the specs, the measured
evidence, or precedent: **Q1, Q2 and Q4** are the registered stub's Open
questions 1, 2 and 4, resolved as the stub recommended; **Q5** is the feedback
log's `--body-from` observation; **Q6** and **Q9** were surfaced by reading the
specs against the registered scope. **Three** are operator decisions, made on
2026-10-27, each as recommended: **Q3** (the stub's Open question 3, whose
premise E4 contradicts), **Q7** (surfaced by E7/E8), and **Q8** (the risk
level, which the quality model requires the operator to confirm). Phase 1
freezes the contract against all nine answers and does not re-litigate scope.

### Q1 — Verb shape: `docs lifecycle FILE... STATE` or `docs lifecycle set FILE STATE`?

*(The registered stub's Open question 1. Its recommendation: flat verb
accepting one or more files, like `docs touch`; no subcommand until a second
lifecycle operation exists.)*
**RESOLVED → D1 (conductor), as recommended.**

The precedent is closer than `docs touch`: `docs project set <doc>...
<new-project>` already splits one positional run as `*docs, <value>`, refuses
a single token as ambiguous, validates the whole batch first, refuses an
archived named document for the whole batch, treats an all-current batch as a
no-op without a reindex, and reindexes once — every property D1–D3 need. A
namespace is how this CLI groups **several** operations (`relate add|remove`,
`project rename|set`); with one operation it adds a word to every call and
nothing else. The suite guard needs `lifecycle` in the top-level verb list
(E2), which both shapes would satisfy, so the guard does not decide it;
precedent does.

### Q2 — A free-form edge whose SOURCE is archived?

*(The registered stub's Open question 2. Its recommendation: refuse, keeping
M25 — D4 limited to recognized bullets; an archived TARGET is fine because it
is never written.)*
**RESOLVED → D5 (conductor), as recommended.**

`convention.md` states archived-document immutability as a closed list of
three exceptions and calls the third *"the last one this convention grants"*.
M25 — D4 was granted because reciprocity checking reaches archived documents,
so a one-sided recognized edge with an archived endpoint would otherwise be an
unfixable `docs check` error. A free-form edge creates no obligation and no
error, so the motive for an exception is absent, and writing one would be the
fourth exception the convention says it does not grant. `docs project set`'s
archived-batch refusal is the matching verb precedent. Two consequences are
pinned rather than left implicit: the refusal runs in the validate-all-first
pass, so even a no-op invocation refuses (M25's *predictable rather than
plan-dependent* rule); and because an archived TARGET is never written, a
free-form operation never requires `--reason` and never writes `Revision:`.

### Q3 — Free-form verb syntax

*(The registered stub's Open question 3. Its recommendation: accept exactly the
token grammar `docs check` already parses for `Related:` bullets, and refuse
anything `docs check` would reject.)*
**RESOLVED → D6 (operator, 2026-10-27): option (c), as recommended.**

**Why it matters.** The grammar is permanent public surface: once 2.1.0 ships,
loosening it later is additive, but tightening it breaks automation that
relied on the looser form. It also decides what happens to a mistyped
recognized verb. And the registered recommendation does not pin it down,
because `docs check` parses no token grammar (E4, *A2*).

**The options.**

- **(a) Mirror the parser.** Accept any verb that round-trips through
  `parse()` unchanged — non-empty, no `:`, no newline, no leading or trailing
  whitespace. `relate` can then write every edge a hand-edit could, including
  `see also` and `@#!$`; `Precedes` becomes a silent one-sided free-form edge
  (E5) unless a separate case-variant guard is added, which then refuses
  something `docs check` accepts.
- **(b) The metadata-label token** `[A-Za-z][A-Za-z0-9_-]*` — the shape
  `_LABEL_RE` already uses for metadata labels. Accepts every verb measured;
  refuses spaces, punctuation and the empty verb. Case variants of recognized
  verbs pass, so the E5 hazard needs the same separate guard.
- **(c) A lowercase kebab token** `[a-z][a-z0-9-]*`. Accepts every one of the
  417 + 96 + 5 edges measured and every verb the suite prescribes (E3);
  refuses spaces, punctuation, the empty verb and — with no special case —
  every case variant of a recognized verb, because those contain an
  uppercase letter. `test_relate_case_variant_verb_refuses` keeps refusing;
  only its expected message may follow Phase 1's catalogue. A hand-written
  exotic verb stays valid in a tree; `relate` simply will not write or remove
  it, so such an edge stays a hand-edit.

**Grounded example.** `docs relate add lifecycle-and-free-form-relate.md
Pairs-With lifecycle-and-free-form-relate-impl.md`: under (a) or (b) without a
guard it exits 0 and writes `- Pairs-With: …`, which no archive cascade
follows (`_CASCADE_VERBS` matches `pairs-with` exactly), so a later closeout
would silently leave the impl log behind; under (c) it refuses with zero bytes
written and the agent retypes it.

**The recommendation, as put to the operator: (c).** It is the only option
that needs no special case to keep the E5 hazard closed, it loses nothing that
has been measured anywhere, and it starts at the strict end of a one-way door.

**The resolution.** The operator adopted (c): `[a-z][a-z0-9-]*`. Case variants
and anything else outside the grammar refuse at exit 2 with zero bytes
written, and widening the grammar later is recorded as additive (D6;
*Follow-ups* item 3).

### Q4 — Release vehicle

*(The registered stub's Open question 4. Its recommendation: additive, so
**2.1.0** through a separate publish milestone (the M19 → M20 pattern), at
which point host skills and the suite prescriptions are refreshed per
`CLAUDE.md`.)*
**RESOLVED → D9 (conductor), as recommended.**

Every single-milestone release followed one pattern: the feature milestone
bumps `pyproject.toml` and the packaging version pin, opens an
`UNRELEASED` CHANGELOG section, and builds locally (M19 → 1.6.5, M21 → 1.7.0,
M23 → 1.8.0), and a separate publish milestone ships it. M25 — D6's
"the publish performs the single bump" was an operator decision for a
five-milestone train and does not transfer to one milestone. The change is
additive (one new verb; one refusal becomes a success; no check rule), so
semver gives a minor bump — and the D10 fix (Q7) is a bug fix that rides
along. The publish milestone is not yet a tracker row; inserting it is a
tracker operation for the operator.

### Q5 — Is the `--body-from` leading-`Related:` route a supported path or an accident?

*(The feedback log's promotion observation: "M30 Phase 1 should decide whether
that is a supported path to document or an accident to pin.")*
**RESOLVED → D8 (conductor).**

It is supported, and its intent was documented before anyone asked: the
bundled skill has prescribed `docs new … --body-from -` with `Related:
artifact-of: <binary>` since M8 (E6) — though in an inline spelling the
grammar reads as body text, which Phase 7 corrects to the group form. The convention's block grammar is what makes a body's
leading bare-label group metadata, and `cli.md` refuses a body "only when it
carries an actual metadata block" by a closed two-signal heuristic that M15 —
C4 deliberately narrowed. Refusing the route now would break a documented use
case in a minor release; leaving it untested would let it change silently. So:
lock it, state it in `cli.md`, and let the skill name both routes. The broader
leak — any leading bare-label group, a forged `Revision:` included — is a
separate question nobody has asked yet, recorded as *Follow-ups* item 1.

### Q6 — Must a free-form TARGET parse as a managed Markdown document?

**RESOLVED → D5 (conductor).** No — any existing file under the root:
`broken-ref`'s existence test plus containment.

`relate` parses both endpoints because, for a recognized pair, both are
written. A free-form TARGET is never written, and `convention.md` allows a
`Related:` target to be *any file*, which `docs check` honours (E9). The
registered principle *refuse anything `docs check` would reject* has a mirror
half the stub did not need to state: do not refuse what it accepts when nothing
is written. Without it the bundled skill's own prescription — link generated
reports from `Related:` — still needs a hand-edit, and the milestone's goal is
missed for a prescribed edit.

### Q7 — The extension-state clause versus `parse()`'s config-blindness

**RESOLVED → D10 (operator, 2026-10-27): option (A), as recommended.**
Surfaced by E7 and E8; recorded as *A1*.

**Why it matters now.** The registered clause promises extension states and a
single reindex; E7 shows a document in an extension state breaks every
reindex. Phase 1 cannot freeze `docs lifecycle`'s vocabulary, and Phase 2
cannot write its extension-state tests, until the scope is decided. Both new
verbs also validate their endpoints through `parse()`, so the answer decides
whether they work at all on such trees.

**The options.**

- **(A) Fix the root cause in M30.** Make `parse()` honour the tree's config
  for both the vocabulary and the date format, passing it at each of the seven
  call sites with a built-in default for bare calls. Extension lifecycles and
  roles, and non-default date formats, then work in every verb; no tree that
  passes today can start failing; the unowned 2026-08-15 feedback entry closes
  with it. Cost: one more deliverable, regression locks across every walking
  verb, and a change that reaches the core read path.
- **(B) Fix only the vocabulary half.** The registered clause holds and both
  new verbs work on extension vocabularies; non-default date formats stay
  broken for every verb, the new ones included, and `parse()` is left
  honouring half of the config.
- **(C) Descope extension states.** `docs lifecycle` accepts the five built-in
  top-level states and refuses an extension state before writing, naming the
  defect; the registered clause is amended; the vocabulary defect is
  registered in `feedback-log.md` beside the date-format one for a later
  correctness milestone. M30 stays tight, but adopters with an extension
  vocabulary keep a lifecycle step the verb refuses — and their trees stay
  broken on every reindex regardless.

**Grounded example.** This repository's own `.docs.toml` advertises
`# add_lifecycles = ["shipped"]`, and the bundled template suggests
`"experimental"` and `"deprecated"`. An adopter who uncomments it and runs
`docs lifecycle spec.md shipped` gets, under (A) or (B), exit 0 and a
refreshed INDEX; under (C), exit 2 with nothing written; and today, with any
hand-edit, a tree whose next `docs touch` exits 2.

**The recommendation, as put to the operator: (A).** One cause, one
function, seven call sites; both new verbs route through it for validation and
for the reindex; the date-format half is the open item its own feedback entry
already slated for "a post-2.0.0 correctness milestone" with the same fix; and
(B) would leave a function that honours half of the tree's config.

**The resolution.** The operator adopted (A): both halves are fixed inside
M30, with the tree's config — vocabulary extensions and `[archive]
date_format` — passed into `parse()` at every call site, so extension
lifecycles and roles and non-default date formats work in every verb,
including the two new ones. It is an explicit deliverable and contract
clauses (D10), no tree that passes today may start failing (E11 bounds the
one changed outcome to a tree that already fails `docs check`), and both
feedback entries now name this milestone as owner.

### Q8 — Risk level

**RESOLVED (operator, 2026-10-27): Standard, as proposed** (*Risk Level*
above).

**Why it matters.** The level selects the gates: High adds an operator
checkpoint after the Phase-4 RED baseline before any implementation, a
mutation baseline where configured, and explicit approval for any skipped deep
gate; Standard relies on the selected property, fuzz, mutation-smoke and
review gates without the checkpoint. No earlier milestone in this project
recorded a level except M16 (Lite), so precedent does not settle it.

**Grounded example.** The v2.0 milestones closest in shape — M25's
two-document `relate` writer and M28a's archive-date witness — ran without a
recorded level, yet M28a's fresh-eyes review still killed 19 of 19
hand-applied mutations. Under Standard this milestone keeps that kind of
review (ship-milestone runs one at the end of each of Steps 0–2) and the
hand-applied mutation smoke, and drops only the Phase-4 checkpoint.

**The resolution.** The operator confirmed **Standard**, for the reasons in
*Risk Level* — additive surface, proven editors, enumerable integrity
invariants each pinned by a lock, and independent reviews already in the flow
— with Q7's core-read-path fix in scope. There is no Phase-4 operator
checkpoint; the selected property, fuzz, mutation-smoke and review gates
stand.

### Q9 — How does M30 discharge the stopgap success criterion?

**RESOLVED → D9 (conductor).**

The criterion, preserved verbatim under *Success criteria*, places the
retirement "in the suite release that pins the docs-cli version carrying M30 —
not at M30's merge or at the PyPI publish alone". The registered stub also
places the trigger: its deliverable is a *hand-off note for the publish
milestone*, whose closeout sweep must retire the stopgap, and its TDD summary
ends "hand off to the publish milestone". Read together, M30 discharges its
part at its own closeout — both verbs shipped, both suite probes locked, and
the hand-off note written to a live document that outlives this milestone's
archive — and then archives normally under the tracker contract. The
retirement itself is verified in the suite release, as the criterion says.

### Also settled, without a question

- **No `docs check` change.** No rule, finding or record key is added; free-form
  edges stay unvalidated.
- **Recognized-verb `relate` unchanged**, record and messages included (D4).
- **The self-edge refusal stays** for free-form verbs: a document relating to
  itself is never a prescribed edge, and keeping one rule is simpler than
  splitting it.
- **Excluded endpoints stay allowed**, as M25 decided.
- **`INDEX.md` does not render lifecycle**; a lifecycle change moves the INDEX
  only through the `Updated:` bump, which is why the reindex stays.
- **The two suite probes are locked as product tests** — they are the
  external contract this milestone exists to satisfy.
- **No new dependency**, runtime or development.
- **Skill channels.** Bundled skill in the same change; host skills at the
  production ship (`CLAUDE.md`).

## Follow-ups recorded for later milestones

Raised during setup, judged out of this milestone's scope, and deliberately
**not** implemented here.

| # | Follow-up | Home |
|---|---|---|
| 1 | **`--body-from` admits any leading bare-label group as metadata**, not only `Related:` — measured with a `Revision:` group landing on an active document, which the convention says the tool never writes (E6). Whether to narrow the C4 heuristic is a behaviour change nobody has asked for. | Registered 2026-10-27 (Phase 7) as an open, unowned `feedback-log.md` entry (Step 2 planning question OQ-1, conductor-resolved: register it with items 2, 3, 7, 8 and 9) |
| 2 | **Removing a dangling free-form edge** whose TARGET no longer exists. `relate` still requires TARGET to resolve, so a `broken-ref` repair stays move-driven or manual. | Registered 2026-10-27 (Phase 7) as an open, unowned `feedback-log.md` entry (OQ-11) |
| 3 | **Widening the free-form verb grammar** beyond `[a-z][a-z0-9-]*`, if a real tree needs an exotic verb `relate` should write. Additive — no caller breaks (D6, Q3). | Registered 2026-10-27 (Phase 7) as an open, unowned `feedback-log.md` entry (OQ-11) |
| 4 | **Registering the publish milestone** that ships 2.1.0, refreshes host skills, and carries the stopgap hand-off. Not registered in this run (operator, 2026-10-27); the hand-off note names it. | Operator (tracker) |
| 5 | **The suite pin-bump PR** that retires the verbless-metadata stopgap (*Success criteria*). | Agent Playbook Suite |
| 6 | **A `parent-of` back-edge on `milestone-plan.md`** pointing at this milestone (Step 0 review claude-N11, waived): a free-form hand-edit to a document outside the operator-approved set, and not required by the tracker contract, since this milestone's `child-of: milestone-plan.md` already gives navigation. The waiver lifts once free-form `docs relate` exists. | Later (decided at Phase 10 — OQ-11) |
| 7 | **No verb repairs an out-of-vocabulary `Lifecycle:` or `Role:`.** `docs lifecycle` exits 1 on a source that fails `parse()` (`Lifecycle: activ`, or `shipped` after its extension was removed from `.docs.toml`), and `docs stamp`'s refusal points at "correct the field, then `docs touch`" — while the bundled skill forbids hand-editing a metadata block. Raised at Phase 1 (OQ-5); the skill sanctions no new hand-edit. | Registered 2026-10-27 (Phase 7) as an open, unowned `feedback-log.md` entry (OQ-11) |
| 8 | **`[vocabulary]` entries are not validated at config load.** `load_config` merges `add_lifecycles` / `add_roles` with an unchecked `frozenset()`: an empty or padded entry is accepted silently, and a bare string (`add_lifecycles = "shipped"`) becomes its single letters. D10 makes every verb honour the configured vocabulary, so such an entry now reaches every walk, not only `docs check`. Raised at Phase 1 (OQ-5). | Registered 2026-10-27 (Phase 7) as an open, unowned `feedback-log.md` entry (OQ-11) |
| 9 | **A recognized-verb TARGET path can inject metadata.** `docs relate add a.md precedes $'b\nLifecycle: archived\nx.md'` exits 0 and writes a bullet that ends `a.md`'s `Related:` group and adds a `Lifecycle: archived` line (measured at the Step 1 review). Free-form `relate` refuses such a TARGET (R4); recognized verbs stay byte-for-byte unchanged under D4, so the fix — a refusal, or path validation shared by both kinds — is a later, deliberate behaviour change (Step 1 review claude-S2, conductor decision JC1). | Registered 2026-10-27 (Phase 7) as an open, unowned `feedback-log.md` entry (OQ-11) |
| 10 | **Candidate project convention: state a binding decision once.** This task plan restates D10 in six or more places, so every wording correction must touch every copy (Step 1 review claude-T4, waived for this milestone). A convention for later milestone docs — one authoritative statement, pointers elsewhere — would make such drift impossible. | Phase 10 (taste triage and compounding), or the project's agent context |

## Testing and quality gate

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q
(cd docs && ../.venv/bin/docs check .)
```

Additional gates: the live-INDEX snapshot (`tests/fixtures/expected/docs-INDEX.md`
refreshed after every `docs index` that changes `docs/INDEX.md`); bundled
`references/cli.md` and `references/convention.md` byte identity; the skill
completeness guard; both suite-probe replicas; the closed `--json` key sets;
the archive invariance locks; the property checks, the grammar fuzz and the
hand-applied mutation smoke; and `docs lifecycle --help` / `docs relate --help`
/ `cli.md` surface parity.

## Success criteria

- The primary use case completes with zero hand-edits and zero operator asks.
- No transition into or out of `archived` is possible through `docs lifecycle`.
- Recognized-verb `relate` behaviour and the archive cascade set are
  byte-for-byte unchanged.
- Full quality, compatibility, and dogfood gates are GREEN.
- **The suite stopgap is retired in the suite release that pins the docs-cli
  version carrying M30** — not at M30's merge or at the PyPI publish alone,
  because downstream projects follow the suite's pin and keep the 2.0 surface
  until it moves. That one suite PR bumps `DOCS_CLI_VERSION`, replaces every
  operator-approved hand-edit prescription with `docs lifecycle` / free-form
  `docs relate`, deletes `_shared/references/verbless-metadata-edits.md`, and
  drops ship-milestone Step 0's up-front approval. The suite CI guard
  *Validate verbless-metadata stopgap matches the pinned docs-cli* enforces
  it: it fails while the stopgap still covers an edit the pinned binary can
  perform. If Phase 1 descopes either verb, only that half of the stopgap
  retires.

Evidence-anchored criteria added at setup:

- Both Agent Playbook Suite probes pass against this milestone's build: the
  `docs --help` brace list contains `lifecycle`, and `docs relate add a.md
  pairs-with b.md --dry-run` exits 0 in a fresh two-document tree (E2).
- A free-form operation rewrites exactly one managed document and refreshes
  the INDEX once (a no-op or `--dry-run` writes nothing); an archived SOURCE
  refuses with zero bytes written; an archived TARGET is never written and needs no
  `--reason`; a non-Markdown TARGET is accepted (D5, E9).
- The free-form verb grammar `[a-z][a-z0-9-]*` is pinned at its boundary:
  every accepted verb round-trips through `parse()` unchanged, and case
  variants and every other out-of-grammar verb refuse at exit 2 with zero
  bytes written (D6, E4, E5).
- Extension lifecycles and roles, and a non-default `date_format`, work in
  every verb: an extension state round-trips through `docs lifecycle`,
  `docs index`, `docs list` and `docs relate` with exit 0, and no verb
  starts refusing a document `docs check` accepts (D2, D10, E7, E8, E11).
- `docs lifecycle` refuses, with zero bytes written, an `archived` target, a
  source under the archive subtree, and an active-tree source already reading
  `Lifecycle: archived` (D2).
- `docs stamp` never destroys a document: a configured extension state is
  "already stamped", and a full block that fails the configured vocabulary or
  date format refuses at exit 1 with zero bytes written (D10, E12).
- Every active document the INDEX summary counts is rendered, extension-role
  groups after the built-in ones in alphabetical order (D10, E13).
- Recognized-verb `relate` is byte-for-byte unchanged on every tree 2.0.0
  could read; on an extension-vocabulary or non-default-date tree, an endpoint
  2.0.0 refused at exit 1 now resolves (D4, D10).
- The `--body-from` leading-`Related:` route is locked by test and stated in
  `cli.md`, and the skill's sidecar examples use a form that works (D8, E6).
- `docs check`'s rules, findings and record keys are unchanged, and every
  pre-existing test id is present and GREEN under the explicit old → new
  mapping in *Test Strategy* › *Pre-existing tests that change*.
- Specs and bundled mirrors are byte-identical, the skill's *Three things never
  to hand-edit* names both verbs, and the hand-off note lives outside the
  archive scope.
