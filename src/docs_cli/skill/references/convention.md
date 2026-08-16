# docs — Convention Spec

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-08-16

Related:
- pairs-with: cli.md

## Scope

This spec defines the on-disk convention that `docs` reads and writes. It is the portable, tool-independent part: any directory following this convention is navigable with `grep` and `ls` alone. The `docs` CLI is convenience over this convention, not a prerequisite for it.

## Document shape

Every `.md` file managed by `docs` has this structure:

```markdown
# <Title>

<metadata-block>

## <first content section>
...
```

### H1 title

The first non-empty line of the file MUST be a single `#` H1. This is the doc's display title in indexes and `docs list` output.

### Metadata block

Lines immediately after the H1 (separated by a blank line) form the **metadata block**.

Within the block, two line shapes are allowed:

```
Label: inline value
Label:
- value
- value
```

The first form is for single values. The second form is for multi-valued labels (used by `Related:` and any other label that takes a list).

The metadata block may be split into groups separated by blank lines, provided each group after the first is a bare `Label:` followed by `- value` bullets (a multi-value group). This permits the common style of grouping inline metadata above and `Related:` (or any other list-valued label) below, with a visual blank line between them:

```
Lifecycle: active
Role: spec
Updated: 2026-05-20

Related:
- pairs-with: convention.md
- implements: charter.md
```

The block terminates at the first blank line whose next non-empty line is *not* a bare-label multi-value group. An inline `Label: value` line after a blank line is body content, not metadata — this preserves the rule that anything looking like an isolated `Label: value` outside the block is opaque to the parser.

**Each label appears at most once (M25 — D7).** A metadata block must not
repeat a label. Repeatability lives in the **bullets** under a bare label,
never in a second copy of the label: `Related:` carries any number of
`- <verb>: <path>` bullets and `Revision:` any number of dated entries, but
each of those labels may occur only **once** in the block. The same holds
for every inline label — one `Updated:`, one `Role:`, one `Owner:`.

This is structural, not stylistic. The parser builds a dict from the block,
so a second copy of a label **replaces** the first and every value under the
earlier one is silently discarded — before any validation, INDEX
generation, or `Related:` resolution can see it. `docs check` therefore
treats a repeated label as a hard error (rule `duplicate-field`, exit 2);
see `cli.md` › `docs check` › *Duplicate metadata labels*. The repair is to
merge the entries under one label by hand.

### Required fields

| Field | Type | Meaning |
|---|---|---|
| `Lifecycle` | controlled vocab | doc's lifecycle state |
| `Role` | controlled vocab | what kind of doc this is |
| `Updated` | `YYYY-MM-DD` | last meaningful update |

> **Lifecycle (M7 — F0) — breaking change since 1.1.**
> Before 1.2 the lifecycle field was named `Status:`. M7 renamed
> the controlled-vocab key to `Lifecycle:` because the 2026-05-24
> multi-tree trial found that almost every real-world foreign doc
> uses `Status:` as a free-form progress line ("Implemented;
> retained as design record", "Draft normative companion spec",
> etc.). A free-form `Status:` line in a doc is now treated as an
> ordinary extra field: preserved verbatim by `docs migrate` (into
> the `## Migrated metadata` body section as
> `Migrated-Status:`), surfaced through `docs list --json` under
> `extra_fields`, and ignored by `docs check`'s vocabulary
> validator. See `dual-status-adr.md` for the operator decision
> trail.

### Optional fields

| Field | Type | Meaning |
|---|---|---|
| `Project` | kebab-case slug | project this doc belongs to; defaults to `project.name` in `.docs.toml` if absent. The CLI surface `docs project rename` rewrites this slug in lockstep across the sidecar and every doc that names it (M12). |
| `Related` | list of `<verb>: <path>` | typed cross-references to other docs |
| `Archived` | date, in the tree's `[archive] date_format` | the archive-date witness (M28a — D1). Written by `docs archive` to **every** document the operation moves, carrying the same date that names the dated archive directory. `docs check` corroborates it against the document's location (rule `archive-date-drift`); see *Archive subtree*. Never written by any other verb, and never backfilled. |
| `Archived-reason` | free-form | why *this* archive was requested. Written by `docs archive --reason` to the named **primary only**, never to a cascaded candidate (M26 — D1). Harvested but uninterpreted. |
| `Revision` | list of `<YYYY-MM-DD>: <one-line entry>` | repeatable dated audit record. Written by `docs relate` on an **archived** endpoint only, one bullet per real mutation, appended chronologically at the end of the metadata block (M25 — D4). Never written to an active doc — its history is the repository's. |
| `Owner` | free-form | the human or team accountable for this doc |
| `Tags` | comma-separated | free-form tags for filtering |
| `Status` | free-form | a human-readable progress sentence (M7 — preserved, not vocab-checked) |

Any additional `Label:` fields are harvested and exposed under `docs list --json` but not interpreted by the tool.

## Vocabularies

### Lifecycle (built-in)

| Lifecycle | When |
|---|---|
| `draft` | Being written, not ready for use. |
| `active` | Current, in use, source of truth. |
| `blocked` | Paused, waiting on something external. A `Related: blocked-by: …` edge is a natural companion, but from M25 `blocks`/`blocked-by` is a **validated reciprocal pair** — writing `blocked-by` obliges the other doc to carry `blocks` back (use `docs relate add`, never a hand-edit of one side). The two are otherwise **uncoupled**: `Lifecycle: blocked` neither requires nor is implied by a `blocked-by` edge, and `docs check` never derives one from the other. |
| `done` | Complete; intentionally kept in the active tree (evergreen reference). |
| `archived` | Complete and moved to the archive subtree. |
| `superseded` | Replaced by another doc. Pair with `Related: superseded-by: …`. |

### Role (built-in)

| Role | What |
|---|---|
| `charter` | What we're building and why. |
| `plan` | How we'll get there (sequencing, milestones). |
| `spec` | Detailed design or contract. |
| `milestone` | A specific milestone definition. |
| `log` | A chronological record where entries accumulate over time — implementation log tied to a milestone, decision log accumulating reviewer choices, or operational log of recurring work. The distinguishing feature is that the doc grows over time rather than being rewritten. |
| `status` | Living status document. |
| `decision` | ADR-style: one decision, alternatives, rationale. |
| `guide` | Instructional / how-to. |
| `runbook` | Operational procedure. |
| `reference` | Evergreen technical reference. |
| `postmortem` | Incident retrospective. |
| `idea` | Pre-decision exploration. |
| `implementation` | A focused implementation note tied to a plan or milestone (M7). |
| `sketch` | An exploratory sketch, pre-formalisation (M7). |
| `outline` | A skeletal pre-write of a plan or spec (M7). |
| `memo` | A short prose note; less structured than `notes` (M7). |
| `brief` | A condensed summary of a larger surface (M7). |
| `template` | A reusable doc template (M7). |
| `example` | A worked example used as reference (M7). |
| `notes` | Catch-all. |

> **Role vocab additions (M7 — F10 / OQ-A).** M7 promotes 7
> previously-extension-only roles to the core vocab — Trial 2
> (2026-05-24) found these are common enough in real-world docs
> that the built-in set should cover them.

### Extending vocabularies

`.docs.toml` may **add** lifecycles, roles, and extra-metadata-label
allowlist entries via `[vocabulary]` — never remove or rename built-ins.
Additions are local to that docs root. Cross-project queries collapse
to the built-in set; per-project queries see the union.

```toml
[vocabulary]
add_lifecycles = ["shipped"]            # M7: renamed from `add_statuses` (no alias)
add_roles      = ["adr", "rfc"]
add_fields     = ["Owner", "Tags"]      # M10: opt-in extra-field allowlist
```

`add_fields` (M10) widens the `docs check` `unknown-field` rule's
allowlist. Matching is **case-sensitive exact match** — `add_fields =
["Owner"]` allows `Owner:` but not `owner:` (mirroring how
`add_lifecycles` and `add_roles` already work; the on-disk convention
is `Capital:`, so `owner:` is malformed and rejected by the parser
upstream). The rule is opt-in: an absent or empty `add_fields`
switches the `unknown-field` warning OFF entirely. The built-in
always-allowed metadata labels (`Lifecycle`, `Role`, `Project`,
`Updated`, `Related`, `Archived`, `Archived-reason`, `Revision`) are
never affected by `add_fields` — they are always permitted.
(`Revision` joins the set in M25 and `Archived` in M28a, for one
reason: `docs relate` and `docs archive` write those labels
themselves, and a label the tool writes must never trip the tool's
own allowlist warning.)

Scope: `add_fields` widens the `unknown-field` check's allowlist
only; it does **not** change `docs list --json` or INDEX rendering
of extra fields. Those continue to surface every extra field
verbatim (`extra_fields` in JSON; opaque to the human INDEX).

### Inference and confidence (M7 — F1 / F10 / F12 / OQ-D)

`docs migrate` infers each foreign doc's `Role:` from filename
suffixes, post-strip variants, the H1 title, the file's section
shape, and the modal sibling-set. Inferences carry a confidence:

- **high** — direct filename-suffix match (`my-feature-spec.md`,
  `my-feature_Plan.md`, `foo-decision.md`) or an in-file `Role:`
  metadata line that already names a built-in role.
- **medium** — a derived signal: stripping `_v\d+` / `_Draft` /
  `_Ready` and re-matching; the `_M\d+` milestone-number pattern;
  an H1 ending in a role word (`# Foo Plan`); a section-header
  pattern (e.g. `## Goal` + `## Scope` + `## Requirements`
  reads as a plan); a sibling-set modal default at ≥ 60% over
  ≥ 5 same-subdir files.
- **low** — every fall-through that didn't match a real signal;
  the role lands at `notes` and `confidence: low` is paired with
  one or more ambiguity notes.

`docs check` treats a medium-confidence inference as a warning
(exit 1), not an error (exit 2). `docs migrate --json` records
the level under `confidence` (string, one of
`high|medium|low`).

### Per-tree `[migrate]` config (M7 — F1 / F5 / F11)

A docs root's `.docs.toml` may also carry a `[migrate]` section
to teach `docs migrate` per-tree overrides. A `.docs.toml`
containing ONLY a `[migrate]` section (no `[project]`,
`[archive]`, or `[vocabulary]`) is treated as a foreign-tree
migration sidecar — `docs migrate` reads it without refusing:

```toml
[migrate]
project_name   = "foo-tools"             # F11: skip normalisation, use verbatim
role_suffixes  = { spec_v2 = "spec" }    # F1: per-tree custom suffix mapping
```

- `project_name` — pin the project name for every plan record
  (the same effect as `--config-project NAME`, persisted in the
  tree's config). Bypasses F11 lowercase-kebab normalisation
  entirely.
- `role_suffixes` — extends the built-in filename-suffix → role
  map with per-tree entries.

### Per-tree `[check]` config (M19 — D2)

A docs root's `.docs.toml` may carry a `[check]` section to set a
per-tree default stale window for validation:

```toml
[check]
stale_days = 30                          # M19: default --stale window for this tree
```

- `stale_days` — an **integer**. When set, it supplies the
  stale window to `docs check` and `docs touch --check` whenever no
  explicit CLI `--stale` is given — a configured `stale_days` makes bare
  `docs check` apply the `stale` rule with this window (the operator's
  per-tree opt-in). An explicit `--stale N` on the command line always
  overrides it. **Absent** → no default stale window (today's behaviour:
  the `stale` rule fires only under an explicit `--stale`). The key is
  scoped to **check** semantics — it does **not** feed `docs list --stale`,
  which stays an explicit filter. A **non-integer** value (e.g. the TOML
  string `stale_days = "14"`, or `stale_days = true`) is **refused** at
  config load — `docs` exits 2 with `malformed .docs.toml: [check]
  stale_days must be an integer`, rather than crashing in the stale
  comparison. Negative integers are honoured as given (a negative window
  flags every active doc, mirroring `--stale 0`).

## Relationship verbs

`Related:` entries use the form `<verb>: <path>`. Verbs are free-form, but a small set is conventional:

- `pairs-with` — bidirectional sibling (spec ↔ status, milestone ↔ log).
- `child-of` / `parent-of` — hierarchical.
- `implements` — this doc realizes that spec/charter.
- `spec-of` — this doc specifies that thing.
- `supersedes` / `superseded-by` — replacement.
- `blocked-by` — pause causation.
- `decision` — points at a decision doc that justifies this one.
- `references` — weakest form, "see also."

`docs check` does not validate verbs (free-form), but it does validate that every `Related:` path resolves to a file under the docs root. The target file does **not** need to be a `.md` doc — it may be any file (YAML data, HTML report, spreadsheet, generated artifact). The tool checks existence, not file type. This lets specs cross-reference canonical data files, reviewer worksheets, or other artifacts that live in the same tree without forcing them through `docs`'s Markdown convention.

### Reciprocal relationship verbs (M25)

Six of those verbs — and **only** these six — form three recognized
reciprocal pairs. Each carries a distinct meaning; none implies the other,
and none grants archive membership:

| Forward | Inverse | Meaning |
|---|---|---|
| `precedes` | `follows` | Adjacent execution order. |
| `depends-on` | `required-by` | A durable planned prerequisite. |
| `blocks` | `blocked-by` | A current inability to proceed. |

The map is **symmetric**: each member's inverse is the other, so either
spelling of a pair is equally primary. Matching is **case-sensitive exact
match** — `Precedes:` is a different, free-form verb.

**A recognized edge without its exact inverse is a hard `docs check`
error** (rule `missing-inverse`, exit 2), reported against the doc that
declares the un-reciprocated edge. It fires only when both endpoints are
included by the effective exclusion predicate, the target resolves to a
managed Markdown doc in the tree, both endpoint texts parse, and the target
is **not the declaring document itself** — a self-referential recognized
edge is exempt, because there is no second document to complete and
`docs relate` refuses to write one. The existing `broken-ref`, exclusion,
and `malformed` rules keep ownership of their own cases. See `cli.md` ›
`docs check` for the exact message and the full applicability list.

Paths are compared **canonically**, not textually: both the edge's target
and the candidate inverse bullet are resolved to their root-relative POSIX
form before matching (the same resolution the existing `Related:`
existence check performs). `precedes: ./b.md`, `precedes: sub/../b.md`, and
`precedes: b.md` are one edge, and an inverse written `follows: ./a.md`
satisfies it. Writing the plain root-relative form remains the
recommendation — `docs relate` always writes it — but a tree that spells a
path differently is not thereby broken.

Every other verb stays **free-form and unvalidated**: `pairs-with`,
`child-of` / `parent-of`, `supersedes` / `superseded-by`, `implements`,
`spec-of`, `decision`, `references`, and any verb a tree invents. Do not
infer symmetry from a verb's shape — `supersedes` / `superseded-by` and
`child-of` / `parent-of` *look* like inverse pairs and are deliberately
**not** members of the recognized set. Adding them would retroactively
break existing trees for no navigational gain; the recognized six were
chosen because an agent reading one milestone needs sequence, prerequisite,
and blocker context in both directions.

**Repair with `docs relate`, not by hand.** `docs relate add|remove SOURCE
VERB TARGET` writes or unwrites both halves of a pair as one coordinated,
idempotent operation, including — with an explicit `--reason` and a dated
`Revision:` audit bullet — when an endpoint is archived. See `cli.md` ›
`docs relate`.

**Upgrading from a pre-M25 tree.** Trees carrying one-sided recognized
edges begin failing `docs check` after the upgrade. There is **no**
automatic conversion and no opt-out knob: the finding names the source,
verb, target, and exact missing inverse, and the agent decides whether to
complete the pair or delete the edge. The most likely legacy offender is a
bare `blocked-by:` — this spec previously recommended pairing
`Lifecycle: blocked` with a one-sided `blocked-by` edge, and that
recommendation is withdrawn (see the Lifecycle table).

## Body links (M27)

Prose links are part of the navigation layer, not decoration. From M27 `docs`
validates the local Markdown links in a document's **body**, alongside the
`Related:` edges in its metadata block. Two rules follow for authors.

**Invariant: a local Markdown body link stays inside the tree root; anything
outside the tree is a URL.** A docs tree has to be **portable**. The same
bytes get read in a git clone, inside a container, vendored as a subtree, and
unpacked from a release archive — and a link that resolves only because of
what happens to sit *beside* the checkout resolves in one of those places and
dangles in the others. Worse, the tool cannot even tell you which: a check
whose answer depends on the tree's surroundings is not a check. So a body-link
destination that climbs out of the root with `..` is a convention violation
regardless of whether the file it names happens to exist on the machine
running the check, and the repair is to name the target by URL instead. This
is the same boundary the tool draws for itself: `docs check` never stats,
opens, or follows anything outside the root it was pointed at.

**Fence code samples that contain link syntax.** A body link is recognised
wherever it appears in prose, and the only code the tool recognises is a
**fenced** block (```` ``` ```` or `~~~`) or an **inline code span**
(backticks). There is deliberately no 4-space-indented-code rule, because in
real documents a four-space-indented link is almost always a genuine link
inside a blockquote or a list continuation, not a code sample. So: put link
syntax you do **not** want validated inside a fence or backticks — which is
already the house style — and use a backslash escape (`` `\[label](target.md)` ``)
when you need to opt a single span out inline.

Resolution differs from `Related:` in exactly one way, and it is the important
one: a `Related:` path is **root-relative**, while a body-link destination is
resolved **from the directory of the document that contains it**. So `..` is
normal and expected in a body link and never appears in a `Related:` bullet.
Beyond that the two agree: any existing filesystem entry satisfies a
destination — file **or** directory, any extension — and a `#fragment` is
preserved but never validated, since `docs` does not read headings.

External destinations are never touched: a URL, a `mailto:`, a
protocol-relative `//host/path`, a root-absolute `/path`, an image, an
autolink, and raw HTML all produce nothing at all. See `cli.md` ›
*Markdown body-link validation* for the exact recognised grammar and both
finding messages.

**A coordinated move keeps supported links resolving (M28).** From M28 the
two verbs that move a document — `docs mv` and `docs archive` — rebase the
supported body links that move makes stale, in the same operation that
moves the file, so a rename or a milestone closeout ends with `docs check`
clean rather than with prose links to repair by hand. Two rules follow for
authors.

**Write the link; do not work around it.** A destination whose target moved
is repointed. A destination inside a document that itself moved is rebased
from that document's new directory. A destination whose *meaning* the move
did not change keeps the spelling its author gave it, byte for byte —
`./x.md` is never normalised to `x.md`, and a legitimate `sub/../x.md` is
never re-spelled — so the diff of a move contains only what the move
actually made stale. What the tool cannot repair it never touches: an
external URL, an image, an autolink, raw HTML, a bare filename in a
sentence, anything inside a fence or backticks, and a destination that was
already **escaping** before the move are all byte-identical afterwards. A
destination that was already **broken** is never *repaired* and never
*re-aimed* either — but it is rebased like any other when its referrer
moves, to the same, still-broken target, because the tool resolves paths
without ever asking the filesystem what exists and rebasing is what keeps
the link pointing where its author aimed it. Either way the finding
survives the move: `docs check` owns pre-existing damage, and repairing it
is never a precondition for a rename. Documents that `[exclude]` or
`.docsignore` keeps out of the walk are not rewritten either — the
exclusion decides what is *read*, never what a destination may point at.

**A move can refuse, and it refuses before it writes.** Archiving a
document that a still-active document outside the operation declares itself
`child-of` refuses outright, naming both ends and changing zero bytes: a
parent is not archived out from under a live child. Every *other*
still-active reference into the newly-archived set — any other verb, and
every body link — is reported rather than refused, because a closeout is
supposed to leave the tracker and the plan pointing at the work it
completed. That report is the operation's consequence, not a defect list.

## Archive subtree

Completed work moves to an archive subtree. Default subdir name: `archive/`. Convention: `archive/YYYY-MM-DD/` per archive event. Configurable via `[archive] dir` in `.docs.toml`. `[archive] dir` must be a **single path segment**, and `[archive] date_format` must render as one too — a format containing `/` would make the dated directory two segments deep, which every archive-subtree rule in this convention reads as one.

Lifecycle/location consistency rules:

- A doc at the top level (active tree) MUST have `Lifecycle:` in `{draft, active, blocked, done, superseded}`.
- A doc under the archive subtree MUST have `Lifecycle: archived`.
- `docs check` reports any mismatch with nonzero exit (rule `status-drift`).

`done` vs `archived`: `done` stays in the active tree (evergreen reference); `archived` is moved to the archive subtree. Use `done` when the doc is finished but still referenced day-to-day.

**The archive-date witness (M28a — D1 / D3 / D6).** `docs archive` records the archive date as an `Archived:` metadata line on **every** document the operation moves, carrying the same date that names the dated directory. `docs check` then asks whether the document's location corroborates it: the first segment under the archive dir must parse, in the tree's `[archive] date_format`, to the recorded date. It does not, and the document is a hard error — rule `archive-date-drift`, exit 2, one finding per document. Three things bound the rule:

- **Present-only.** A document that carries no `Archived:` line produces nothing, ever. Every document archived before 2.0.0 stays silent forever, so a tree upgrading from 1.x gains zero findings from this rule. There is no backfill, and no CLI verb performs one.
- **The tool never requires a dated directory.** The rule reports a document whose *own recorded date* is not corroborated, never a tree whose layout it dislikes. An undated subdirectory under the archive subtree stays permitted, and a document sitting in one that carries no witness stays silent.
- **It is independent of `status-drift`.** The two report different facts — a lifecycle that disagrees with a location, and a recorded date that does — and both may fire on one document.

**Cross-dated archived relocations refuse (M28a — D5).** The dated directory is the only record of when a document was archived, so `docs mv` **refuses** a move whose source and destination are two *different* dated archive directories — decided from the two paths alone, before any byte is written, at exit 2, in every mode. It refuses for every archived document, whether or not it carries the witness, which is what protects the population archived before 2.0.0. Four neighbouring moves are permitted and unaffected: a rename within one dated directory, a move with one end outside the archive subtree, a move whose two segments do not both parse as dates, and two spellings of one date (`archive/2026-01-01/` to `archive/2026-1-1/`), because the comparison is on parsed dates rather than raw strings. **The escape stays open**: to correct a genuinely mis-dated archive, move the file by hand, correct its `Archived:` line to match its new directory, and re-run `docs check`, which then confirms the two agree. The refusal blocks the silent path, not the deliberate one.

**Archive-subtree edge integrity (M18, widened by M28 — D5).** Archive-subtree `Related:` edges **and local Markdown body-link destinations** are maintained across moves. When a doc moves into the archive, both its OWN intra-archive references (bullets and destinations pointing at another doc moving in the same operation) and any already-archived referrers' references to it are repointed to the new `archive/YYYY-MM-DD/` paths, so they keep resolving. The M3 "archive is read-only" stance is preserved for everything else — only these move-driven rewrites touch archived docs; prose, other metadata, and references to docs that did not move are left byte-identical. `Archived:` and `Archived-reason:` are named explicitly on that byte-identical side (M28a — D9): both record entry into the archive, and a move-driven rewrite of some *other* document's destination is not an archive event.

M28 **widens this one exception along its own axis** rather than granting a new one: the trigger is unchanged (a reference pointing at a doc moving in *this* operation), the operation is the same, the write is the same single atomic write, and the blast radius grows by exactly the destination token beside the bullet. In particular the widened exception carries **no audit metadata**: an archived referrer whose destination is repointed gets no `Updated:` bump and no `Revision:` bullet, because it still points at the same target in a different spelling and asserts nothing new — and because an `Updated:` value that recorded some *other* doc's move would be a lie about the doc that carries it. An active referrer is treated the same way, as it always has been.

**Audited relationship repair (M25 — D4).** A **second** narrow exception, beside M18's. Because archived docs are walked, they are reciprocity-checked too, so a one-sided recognized edge with an archived endpoint would otherwise be an unfixable `docs check` error. `docs relate add|remove` may therefore touch an archived endpoint — but only when the operator asks explicitly and says why: `--reason TEXT` (a single non-empty line) is **required** whenever either named endpoint is under the archive subtree, and an invocation that would change nothing still requires it. Exactly three things may change in an archived doc: **(1)** the one recognized `Related:` bullet added or removed, **(2)** the `Updated:` value, **(3)** the `Revision:` group — created, or one dated bullet appended recording that document's own change and the reason. `Lifecycle: archived`, the original `Archived:` and `Archived-reason:` (which record entry into the archive, never a later repair), `Role:`, `Project:`, every other `Related:` bullet, every other metadata field, the H1, the prose, the file's location, and its trailing-newline state stay byte-identical. `Revision:` is written to archived endpoints only; an active endpoint gets the edge and the `Updated:` bump and nothing more. This is not general archived-document editing — no other verb and no other field is in scope.

**One-time body-link migration (M27 — D6).** A **third** narrow exception, beside M18's and M25 — D4's, and the last one this convention grants — a count M28 leaves at three, because M28 — D5 widens M18's move-driven exception along its own axis instead of adding a fourth. Because body links are validated uniformly — in archived documents exactly as in active ones, the same reach `broken-ref` and `missing-inverse` already have — a document that an older `docs` moved into `archive/YYYY-MM-DD/` without rebasing its prose links carries damage that is now a hard `docs check` error and would otherwise be unrepairable. This repository's own archive was repaired once, on **2026-08-14**, with a **stated blast radius**: only **destination tokens**, the `Updated:` value, and one dated `Revision:` bullet may change, in **29** named archived documents; `Lifecycle:`, `Archived:`, `Archived-reason:`, `Role:`, `Project:`, every `Related:` bullet, the H1, and all other prose stay byte-identical. `Revision:` is written to archived documents only — an active document repaired in the same pass gets the destination change and its `Updated:` bump and nothing more (M25 — D4). This is **not** a general licence to edit archived prose, and **no CLI verb performs it**: there is no `docs fix-links`. An adopter upgrading to 2.0 gets the recipe (`cli.md` › *Upgrading from 1.x*), not the migration.

**Safe explicit archive selection (M26 — D1).** Entry into the archive subtree is authorized **explicitly**, never by relationship. A relationship verb supplies the *candidate set* a preview names; it never grants permission to move a document. `docs archive FILE` archives that one document. `docs archive FILE --cascade-dry-run` names every one-hop `pairs-with` / `child-of` candidate as selected, not selected, or ineligible and writes nothing. Only `docs archive FILE --cascade-only GLOB` writes a related document, and then exactly the candidates the glob selects — one complete plan, validated before the first byte moves, refusing outright rather than writing part of it. The 1.x bare `--cascade` and `--interactive` flags are retired and refuse. Two rules follow for authors: a document already under the archive subtree is **never** re-archived — neither as a candidate (it is reported ineligible) nor as the named primary (that is a refusal) — so a later archive event never changes an archived doc's location, `Updated:` value, `Lifecycle:`, `Archived:`, `Archived-reason:`, H1, or prose, and changes no `Related:` bullet of its except one pointing at a document moving in that same operation, which M18's edge integrity repoints so it keeps resolving; and an `Archived-reason:` line records why *that* document was archived, so it is written to the named primary only, never to a cascaded candidate.

## Subdirectories

A docs root is not required to be flat. Beyond the machine-managed archive subtree, authors may organize docs into free-form subdirectories — grouping a body of work, a set of brainstorms, or a sub-project under its own folder. The tool is directory-agnostic:

- `docs index` walks the whole tree recursively and lists every doc by its root-relative path. A subdirectory imposes no constraint on a doc's metadata.
- The only directory the tool treats specially is the configured `archive_dir` — docs under it form the archive subtree (see above). Every other subdirectory is opaque to `docs`.
- The status/location consistency rule applies *only* to the archive subtree. A doc in any other subdirectory may carry any active-tree status.

Whether to keep a tree flat or nest it is the author's call. The metadata block and the generated `INDEX.md` — not the directory layout — are the primary navigation surface; subdirectories are a convenience for humans browsing with `ls` or an editor file-tree. `docs new` can create a doc directly into a subdirectory (`docs new spec sub/feature`); `docs mv` can relocate one between directories.

### Where to put `.docs.toml` (project ≠ directory)

A `Project:` is a controlled **metadata field, not a directory** — one docs root can hold many projects (each doc names its own via the `Project:` slug), and a single project never requires a subdirectory of its own. Because `Related:` paths are root-relative (see "Relationship verbs"), nesting a lone project's docs in a subdirectory beneath a parent root makes every intra-project sibling reference carry a **redundant** `<subdir>/` prefix — `pairs-with: my-project/scope.md` instead of `pairs-with: scope.md` — while the parent root exists only to wrap that one project.

So choose the root deliberately:

- **One project:** put `.docs.toml` at the directory that holds the docs, so the docs **root is the project**. Docs sit flat at the root and cross-references stay clean. (This repo's own `docs/` tree is shaped this way: `.docs.toml` at `docs/`, `Project: docs`, files flat, `pairs-with: cli.md`.)
- **Several projects in one tree:** keep one root and separate the docs by `Project:` metadata. Per-project subdirectories are optional; only then do prefixed references reflect a genuine cross-folder path.

Do **not** create a parent root and nest a single project one level beneath it — that produces the redundant prefix above for no benefit. This mirrors how `INDEX.md` groups by `Project`, not by directory: the metadata, not the folder layout, is the navigation surface.

## Exclusion

M8 introduces a single layered exclusion surface every walker
consults — `docs migrate`, `docs index`, `docs check`,
`docs list`. M14 (A6) extends it to the **end-of-batch INDEX
reindex** the four mutating verbs run — `docs touch`,
`docs archive`, `docs mv`, and `docs project rename` — so a
malformed *excluded* file (e.g. a bundled plugin `README.md`
under an `[exclude]` dir) cannot fail the post-mutation reindex
after the verb has already stamped/moved on disk. The four
sources combine **additively** (no source replaces another);
see [`cli.md`'s "Common: exclusion"
section](cli.md#common-exclusion) for the per-verb shape. The
mutating verbs consult only the **persistent** sources
(`[exclude]` + `.docsignore`) — they expose no `--exclude` flag
of their own.

- **`[exclude]` table in `.docs.toml`** (persistent, per-tree).
  Three keys — `dirs = [...]` for directory-name matches at
  any depth, `globs = [...]` for gitignore-flavoured glob
  patterns, `exts = [...]` for extension matches. The
  bundled adoption skill's `references/docs-toml-template.toml`
  carries a commented starter.
- **`.docsignore` at the tree root** (persistent, per-tree).
  Single file only — nested `.docsignore` files are NOT
  consulted (OQ-B). One pattern per line. Syntax subset:
  - `# comment` and blank lines are no-ops.
  - Trailing `/` → directory match.
  - Leading `/` → root-anchored (no nested match).
  - `**` → any number of segments; `*` → any non-slash chunk;
    `?` → one non-slash character.
  - Leading `!` → re-include (last match wins, matching
    gitignore).
  - Bare pattern (no `/`) → matches any path segment at any
    depth.
- **`--exclude PATTERN`** on the CLI (ephemeral, repeatable;
  same glob syntax as `.docsignore`). Layered on top of the
  two persistent sources.
- **`--exclude-ext EXTS`** on `migrate` (one-off, csv).
  Extension matches; also suppresses the matching binaries
  from the non-Markdown sibling footer.

For the procedural deep-dive — when to use `[exclude]` vs
`.docsignore` vs CLI overrides, and the dry-run → triage →
iterate → apply loop — see the bundled
[adoption playbook](https://github.com/ArtRichards/docs-cli/blob/main/src/docs_cli/skill/references/adoption-playbook.md)
(also materialised on a host via `docs install-skill`).

## INDEX file

The `INDEX.md` file at the root of the docs tree is a **generated view, not a managed doc**. It does not require a metadata block, and `docs` excludes it from traversal by filename. (Specifically: any file at the docs root literally named `INDEX.md` is read as the existing index for marker-block preservation and skipped during walking; it never appears as an entry in itself.)

The docs root contains an `INDEX.md` with this structure:

```markdown
# <Root title>

<optional hand-edited preamble>

<!-- docs:generated start -->
... derived content ...
<!-- docs:generated end -->

<optional hand-edited trailer>
```

`docs` only rewrites content between the markers. Everything outside is preserved verbatim. The derived section groups by project and role, lists every `.md` file in the tree with its title and a one-line excerpt, and separates the active tree from the archive subtree.

## Non-Markdown files in the tree

A docs root frequently contains files that aren't Markdown — HTML review packets, spreadsheet workbooks, YAML data files, generated validation artifacts, exported PDFs, screenshots, and so on. These are not docs in the sense `docs` cares about; they are **silently ignored** by `docs index`, `docs check`, and every other verb that walks the tree.

- They do not need a metadata block.
- They do not appear as entries in `INDEX.md`.
- Their absence of metadata is not an error.
- They may be referenced from `.md` docs via `Related:` (see "Relationship verbs") or via prose links in the body. `Related:` will check that the referenced file exists, regardless of its extension — and from M27 a local **body link** is checked the same way, inheriting the same rule: any existing entry under the root satisfies it, file or directory, whatever the extension (see "Body links"). The two differ only in their resolution base — a `Related:` path is root-relative, a body-link destination is relative to the referring document.

This keeps `docs` focused on the Markdown navigation layer while letting authors keep canonical data, presentation artifacts, and generated outputs co-located with the specs that describe them. The Markdown layer is the navigable map; everything else lives alongside it.

If you want a non-Markdown artifact to appear *prominently* in `INDEX.md` (e.g., a key reviewer packet that needs to be the first thing readers see), describe it in a short companion `.md` doc that points at it via `Related:` — the companion doc carries the metadata and appears in the index; the artifact stays as the canonical file. A future v1.1 may add a first-class `Attachments:` field; for v1 the companion-doc pattern is the recommendation.

**Migration-time surfacing (M8 — F7).** `docs migrate <dir>` now
surfaces non-Markdown root-level siblings in the dry-run plan
footer as `<N> non-Markdown siblings at root not considered:
<names>` so an adopting agent sees the binaries that prose
references but the walker (markdown-only) skips. Use
`--exclude-ext EXTS` (csv) or the `[exclude] exts = [...]`
config to drop the noise once the operator's reviewed the list.

## File naming

Names are free-form. The metadata block carries the load; the filename is for humans. Kebab-case is recommended (`vocab-adr.md`, not `Vocab_ADR.md`), but not enforced.

## What `docs` does not promise

- No automatic `Updated:` bumping on every write. Use `docs touch` or hand-edit.
- No link-graph traversal. `Related:` is metadata, not a query target. From M25 the tool validates **one-hop reciprocity** of the six recognized verbs (and repairs a single pair via `docs relate`) — that is the whole of its graph awareness. There is still no graph query, no multi-hop traversal, no cycle or conflict detection, and no rendering.
- No content validation beyond metadata **and local body-link destinations** (M27). The tool reads a document's body for exactly one purpose — resolving the local Markdown links in it (see "Body links") — and is otherwise indifferent to it: no rendering, no heading or anchor validation, no style, spelling, structure, or well-formedness rules, and no link-graph traversal built out of body links.
