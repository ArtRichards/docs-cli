# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## UNRELEASED

_The v2.0 train (M25–M28a) accumulates here; M29 names and dates this
heading at publish time. The package version deliberately stays `1.8.0`
until then._

### Added

- **`missing-inverse` check rule** (M25). `docs check` now validates
  **reciprocal relationship edges**. Six `Related:` verbs are recognized in
  three symmetric pairs — `precedes`/`follows`, `depends-on`/`required-by`,
  `blocks`/`blocked-by` — and a recognized edge whose target does not
  declare the exact inverse pointing back is an **error** (exit 2) with an
  actionable one-line finding:

  ```console
  $ docs check
  m25.md
    error: [missing-inverse] Related: 'precedes: m26.md' has no inverse; m26.md must declare 'follows: m25.md' (or remove the edge)
  ```

  The finding blames the **source** — the doc declaring the un-reciprocated
  edge — one per distinct `(source, verb, target)` triple. The `--json`
  record's key set is unchanged (`path`, `severity`, `rule`, `message`); the
  repair lives in `message`. Matching is case-sensitive on the verb and
  **canonical** on the path, so a `./` prefix cannot fail the check. Edges
  are only checked when both endpoints are walked and parseable; `broken-ref`,
  exclusion, and `malformed` keep ownership of their cases, and a
  self-referential edge is exempt. Every other `Related:` verb
  (`pairs-with`, `child-of`/`parent-of`, `supersedes`/`superseded-by`, your
  own) stays free-form with no reciprocal validation.

- **`docs relate add|remove SOURCE VERB TARGET`** (M25) — the repair verb for
  the finding above. Writes (or unwrites) **both halves** of one reciprocal
  pair as a single coordinated operation, inferring the inverse. Idempotent:
  a fully-satisfied invocation writes zero bytes, bumps no `Updated:`, and
  does not reindex. `--dry-run` previews without writing; `--json` emits one
  operation-plan record with the same shape for a preview and a real apply;
  `--quiet` suppresses the success lines but never a refusal. `INDEX.md` is
  refreshed exactly once, at the end, only when something changed. Unlike
  `archive` / `mv`, `relate` validates only its two named endpoints — a
  whole-tree gate would make repair impossible in exactly the broken tree
  the verb exists to repair.

- **`duplicate-field` check rule** (M25). A metadata label may now appear
  **at most once** per document. A repeated label is an error (exit 2), one
  finding per repeated label:

  ```console
  $ docs check
  a.md
    error: [duplicate-field] metadata field 'Related:' appears 2 times; only the last occurrence is read
  ```

  This is a **data-loss** rule, not a tidiness rule. The metadata parser
  builds a dict, so a second copy of a label silently **replaces** the first
  — every value under the earlier one is discarded before validation, INDEX
  generation, or `Related:` resolution can see it. Repeatability lives in
  the **bullets** under a bare label (`Related:`, `Revision:`), never in a
  second copy of the label; many bullets under one label are always fine.

- **Audited archived-endpoint repair** (M25). An endpoint under the archive
  subtree may be repaired, but only with an explicit `--reason` (a single
  non-empty line). The **only** bytes that may change are the one recognized
  `Related:` bullet, the `Updated:` value, and a new dated `Revision:` audit
  bullet; lifecycle, `Archived-reason:`, role, project, other edges, the H1,
  and the prose are byte-identical. `Revision:` is a repeatable bare-label
  group at the end of the metadata block and is a **built-in always-allowed
  metadata label**, so a tree with a `[vocabulary] add_fields` allowlist
  never sees `unknown-field` on a label the tool itself writes.

- **Safe explicit archive selection** (M26). `docs archive` now separates
  relationship *context* from archive *authorization*. Relationship verbs
  supply the candidate set; they never grant permission to move a document.
  Exactly three shapes exist, and no other invocation writes a related doc:

  ```console
  $ docs archive m25.md                              # m25.md alone
  $ docs archive m25.md --cascade-dry-run            # preview, writes nothing
  $ docs archive m25.md --cascade-only 'm25-*'       # m25.md + exactly that scope
  ```

- **`docs archive --cascade-dry-run`** (M26) previews the **whole** one-hop
  neighbourhood — every `pairs-with` / `child-of` candidate marked selected,
  not selected, or ineligible — writes nothing, and exits 0, so an operator
  can see what a scope is leaving behind. A filtered preview no longer hides
  the unselected remainder, and a scope that selects nothing still exits 0
  with a loud `matched none of the <N> one-hop candidate(s)` line.

  ```console
  $ docs archive m25.md --cascade-dry-run --cascade-only 'm25-*'
  docs: archive: would archive m25.md -> archive/2026-08-13/m25.md
  docs: archive: candidate m25-impl.md — selected -> archive/2026-08-13/m25-impl.md
  docs: archive: candidate cli.md — not selected (outside --cascade-only 'm25-*')
  docs: archive: candidate convention.md — not selected (outside --cascade-only 'm25-*')
  docs: archive: candidate archive/2026-01-01/old.md — ineligible (already archived)
  docs: archive: 4 candidate(s): 1 selected, 2 not selected, 1 ineligible
  docs: archive: preview only — nothing was written
  ```

- **`docs archive --cascade-only GLOB`** (M26) is now the **only** way to
  archive a related document, and it is validate-all-first: the complete
  plan — the primary plus every selected candidate — is built and proved
  before the first byte moves. The pre-flight refuses, with **zero bytes
  written**, when a member has no editable metadata block, is already under
  the archive subtree, has an occupied destination slot, collides with
  another member's destination, or is not writable. The candidate set is
  deduplicated on the **canonical** root-relative path (so a `./b.md`
  spelling can neither dodge nor defeat a scope), already-archived
  neighbours are excluded rather than silently relocated and re-dated, and a
  scope that selects nothing on a write **refuses** (exit 2) instead of
  quietly archiving the primary alone. An unexpected `OSError` during
  execution is reported as an exact partial-state admission naming what
  moved and what did not.

- **`docs archive --json`** (M26) emits one operation-plan record on stdout,
  with an identical shape for a preview and a real apply, so the two are
  diffable: the primary (source / canonical path / destination), the date,
  the scope, the `--reason`, and the whole deduplicated candidate set with
  each member's `selected` state, destination, and machine-stable
  `exclusion_reason` (`not-selected`, `already-archived`,
  `unresolved-target`, `outside-root`). The candidate set is present in
  **every** mode, including a plain `docs archive FILE`.

- **`broken-body-link` check rule** (M27). `docs check` now reads each
  document's **body** and validates the local Markdown links it finds there.
  A destination that names no existing path under the docs root is an
  **error** (exit 2), one finding per occurrence:

  ```console
  $ docs check
  archive/2026-01-01/old-log.md
    error: [broken-body-link] body link at line 12 does not resolve to an existing path: plan.md (resolves to archive/2026-01-01/plan.md)
  ```

  A body-link destination resolves **relative to the document that contains
  it** — not root-relative like a `Related:` target — which is why `../` is
  normal in prose and never appears in a `Related:` bullet. The message
  carries the 1-based line, the destination **exactly as written**, and the
  candidate path the tool probed; the `--json` record's key set is unchanged
  (`path`, `severity`, `rule`, `message`). **Any** existing filesystem entry
  satisfies a destination — file or directory, any extension. Fragments are
  preserved and never validated: `docs check` does not check whether the
  heading exists.

  The scanner recognises a deliberately bounded, CommonMark-*shaped* subset —
  inline links with plain or `<…>` destinations and an optional title in any
  of the three quotings, plus reference *definitions*. Images, autolinks, raw
  HTML, and reference *uses* are out of the grammar. Fenced and inline code
  are masked before any matching, so a link-shaped example inside a code
  sample is silent, and a backslash escape (`\[x](y.md)`) always opts a span
  out. External and schemed URLs, root-absolute and protocol-relative
  destinations, empty destinations, and fragment-only links produce nothing
  at all.

- **`outside-root-body-link` check rule** (M27). A body-link destination that
  resolves outside the docs root is its own **error** (exit 2), with a
  different repair:

  ```console
  $ docs check
  notes.md
    error: [outside-root-body-link] body link at line 52 leaves the docs root: ../shared/glossary.md (normalises to ../shared/glossary.md); links outside the tree must be URLs
  ```

  `docs check` **never stats, opens, or follows anything outside its own
  root**. The escape is decided by path arithmetic alone — lexical
  normalisation, no `resolve()`, no symlink following — so the same bytes
  yield the identical verdict from a git clone, a container, or a vendored
  subtree, which is what makes `docs check` usable as a CI gate. Containment
  is tested **before** existence, so the two rules never double-report: an
  escaping destination is reported once, as `outside-root-body-link`, and
  never additionally as broken. A `../`-escape that normalises back under the
  root (`../sub/../back-inside.md`) is contained and validated normally.

- **Move-safe body-link rewrites** (M28). `docs mv` and `docs archive` now
  rebase the local Markdown body links a move makes stale, in the same
  operation, in the same per-document write, and under the same
  all-or-nothing contract as the `Related:` rewrite. Two breakages, one
  formula: a link whose **target** moved, and a link **inside** a document
  that itself moved. Resolve each destination from the referrer's old
  directory, map the resolved target through the move set, relativise against
  the referrer's new directory. Because the mapping is by **normalised
  target**, every spelling of the same file is rewritten — `plan.md`,
  `./plan.md`, `sub/../plan.md`, `../plan.md` alike.

  ```console
  $ docs mv plan.md milestone-plan.md
  docs: mv: moved plan.md -> milestone-plan.md
  docs: mv: rewrite note.md:13 plan.md -> milestone-plan.md
  docs: mv: rewrite sub/deep.md:10 ../plan.md -> ../milestone-plan.md
  docs: mv: 2 destination(s) in 2 document(s), 1 Related: bullet(s)
  ```

  Only destination **tokens** change. Labels, titles, quoting form,
  fragments, plain-text mentions, fenced and inline code, images, autolinks,
  raw HTML, reference *uses*, and every non-`local` destination are
  byte-identical afterwards, and a destination whose meaning the move did not
  change keeps the spelling its author gave it — so archiving a plan and its
  log together produces a **zero-byte** diff in their links to each other.
  Already-archived referrers are repaired too, under M18's move-driven
  exception widened along its own axis: destination tokens only, no
  `Updated:` bump and no `Revision:` bullet.

- **`docs mv --dry-run` is a real preview, and `docs mv --json` is new**
  (M28). `--dry-run` walks the tree, builds the whole rewrite plan, and names
  every planned rewrite — document, line, old spelling, new spelling —
  instead of 1.x's single line. `--json` emits **one** record with an
  identical shape for a preview and for a real apply, so the two are
  diffable:

  ```json
  {"old": {"source": "docs/plan.md", "path": "plan.md"},
   "new": {"source": "docs/milestone-plan.md", "path": "milestone-plan.md"},
   "rewrites": [{"path": "note.md", "line": 13, "column": 16,
                 "old": "plan.md", "new": "milestone-plan.md"}],
   "dry_run": false, "applied": true, "index_refreshed": true}
  ```

  The top-level key set is closed and ordered as shown. No record is emitted
  on a refusal, exactly as `docs archive` has it.

- **`docs archive --json` gains `rewrites` and `strands`** (M28). The closed
  top-level key set widens by exactly those two, inserted after `candidates`,
  and both are **present and `[]`** when empty rather than missing.
  `rewrites` is the same section, produced by the same serializer, that
  `docs mv --json` emits, so the two verbs' plans are byte-comparable.
  `strands` carries the new strand-check's report — every still-active
  inbound reference into the newly-archived set, `Related:` bullets and body
  links alike, with both ends named.

- **The `Archived:` archive-date witness** (M28a). `docs archive` now records
  the archive date as a structured metadata field on **every** document the
  operation moves — the named primary *and* each selected cascade member, so a
  closeout's own metadata records the event that created it rather than only
  the directory it happens to sit in. This deliberately does **not** follow
  `Archived-reason:`'s primary-only rule: a reason explains why one operation
  was requested, while a date is a fact about each document's own move. The
  value is the **same** date string that names the dated archive directory —
  one value, one source, rendered once in the tree's `[archive] date_format` —
  and its position in the block is pinned:

  ```
  Lifecycle: archived
  Role: <role>
  Project: <project>
  Updated: <date>
  Archived: <date>
  Archived-reason: <reason>
  ```

  The label joins the built-in always-allowed metadata set, so it never trips
  `unknown-field` and needs no `[vocabulary] add_fields` entry. It stays out of
  the parsed field set, so it surfaces through `docs list --json` under
  `extra_fields` exactly as `Archived-reason:` and `Revision:` already do — no
  JSON record gains a key. No other verb writes it: `docs new`, `docs stamp`,
  `docs touch`, `docs relate` and `docs migrate` never do, there is no
  backfill, and a document that already carries the label has it replaced in
  place by the archive event's own date.

- **`archive-date-drift` check rule** (M28a). `docs check` reports an archived
  document whose location does not corroborate the archive date it records — a
  hard **error** (exit 2), **one finding per document**, on the existing closed
  four-key `Finding` record (`path`, `severity`, `rule`, `message`), with no
  new flag, no new JSON key and no opt-out. Corroboration is decided by path
  arithmetic and the tree's own config alone — no filesystem probe, no graph
  traversal, no second pass: the first path segment is the configured
  `[archive] dir`, the segment after it parses in the tree's `date_format`, and
  that date equals the recorded one. Comparison is on **parsed** dates, never
  raw strings, so `archive/2026-1-1/` corroborates `Archived: 2026-01-01`.
  Two message forms, one for each non-corroborating shape:

  ```
  error: [archive-date-drift] Archived: 2026-01-01 but the file is in archive/2026-03-04/ (move it back, or correct the recorded date)
  error: [archive-date-drift] Archived: 2026-01-01 but the file is not under a dated archive/ directory (move it back, or remove the field)
  ```

  The rule fires **only when the field is present**. A document that does not
  carry it produces nothing, ever. `archive-date-drift` and `status-drift` are
  independent and may both fire on one document — they report different facts,
  and the case that motivates the rule (a document moved out of the archive
  whose `Lifecycle:` is then hand-edited) is precisely the one where
  `status-drift` is silent.

### Changed

- **BREAKING — a one-sided recognized reciprocal edge now exits 2.** Trees
  that pass `docs check` today can begin failing after upgrading. Nothing is
  converted automatically and there is deliberately **no opt-out knob**:
  `--exclude` / `.docsignore` remain the only coarse escape.
- **BREAKING — a repeated metadata label now exits 2.** A tree carrying a
  duplicate label passed `docs check` before this release, while silently
  losing every value under the earlier copy. It now fails. There is no
  automatic merge: `docs` will not guess which entries you meant to keep.
- **BREAKING — `docs mv` between two dated archive directories now refuses**
  (M28a). A move whose source and destination are both under the configured
  `[archive] dir` and whose first segments under it parse, in the tree's
  `date_format`, to **different** dates used to complete at exit 0, rewriting
  every stale reference so nothing dangled and leaving `docs check` clean. It
  now **refuses at exit 2 with zero bytes written**, in **every** mode —
  `--dry-run` and `--quiet` included, because a preview that says `would move`
  for an operation the apply refuses is a preview that lies — and it emits no
  `--json` record. The dated directory is the only record of when a document
  was archived, and this is the one relocation the tool itself performs that
  would silently falsify it. The predicate is decided from the two paths and
  the tree's config alone, so it protects **every** archived document, whether
  or not it carries the new `Archived:` field. Both lines print even under
  `--quiet`, and the escape ships in the same breath as the refusal:

  ```console
  $ docs mv archive/2026-01-01/x.md archive/2026-03-04/x.md
  docs: mv: archive/2026-01-01/x.md -> archive/2026-03-04/x.md crosses dated archive directories (2026-01-01 to 2026-03-04); refusing before any write
  docs: mv: the dated directory records when a document was archived; to correct a genuinely mis-dated archive, move the file by hand, correct its `Archived:` line, and re-run `docs check`
  ```

  The predicate is the narrowest one that closes the hole, and every
  neighbouring move still completes exactly as before: a rename **within** one
  dated directory, a move with one end **outside** the archive subtree
  (`status-drift` already owns both directions, and this leg does not
  double-report them), a move whose two segments do not **both** parse as
  dates, and two spellings of **one** date (`archive/2026-01-01/` to
  `archive/2026-1-1/`), because the comparison is on parsed dates.
  The two exit-1 argument errors still win: a cross-dated move onto an
  occupied destination exits 1 naming the collision.
- **BREAKING — a broken or escaping local Markdown body link now exits 2.**
  A tree that has carried unnoticed prose damage starts failing `docs check`.
  That is deliberate, and it is what the 2.0 major version exists to carry.
  Nothing is converted automatically, there is **no repair verb** (`docs`
  will not guess whether a link should be rebased, repointed, or deleted),
  and there is deliberately **no opt-out knob** — no `[check] body_links =
  false`. A missing file is a fact, not a style preference. `docs touch
  --check` inherits both rules; the root-level generated `INDEX.md` is never
  scanned, and a `malformed` document keeps sole ownership of its case.
- **BREAKING — `docs archive --cascade` and `--interactive` are retired.**
  Both stay **registered** in argparse — so an obsolete script or workflow
  skill gets a legible, actionable refusal instead of `unrecognized
  arguments` — and both now refuse **unconditionally**, exit 2, writing
  nothing:

  ```console
  $ docs archive m25.md --cascade
  docs: archive: --cascade is retired in docs 2.0 and writes nothing; preview with `docs archive <file> --cascade-dry-run`, then write an explicit scope with `docs archive <file> --cascade-only '<glob>'`
  ```

  The refusal runs before any filesystem access, so it wins over a missing
  file or a malformed `--date`, and it prints even under `--quiet`. Retiring
  `--interactive` removes `docs archive`'s only stdin-reading path: the verb
  now **never prompts on stdin at all**, under any flag combination.
- `docs archive` now **refuses a primary that resolves outside the docs
  root** — a symlink pointing out of the tree, or a `--root` naming a
  different tree — before any write, at exit 1 and in the same words `touch`,
  `stamp`, `project set`, and `relate` already use:

  ```console
  $ docs archive link.md
  docs: archive: /elsewhere/real.md is outside the resolved docs root (/docs); refusing before any write
  ```

  1.x raised an uncaught `ValueError` here, which also stopped before any
  write; the refusal is the legible form of the same guarantee.
- **An unreadable file is now a clean refusal, not a traceback.** An
  unreadable primary, plan member, or referring doc exits 2 with
  `docs: archive: <error>`. A *malformed* referring doc keeps its exit 1
  (unchanged).
- `docs archive`'s human output moved to the M26 vocabulary:
  `docs: archive: archived <rel> -> <dest-rel>` and the candidate / counts
  lines replace 1.x's `docs: archived <name> -> <abs-path>` and the
  `cascade would archive N related doc(s)` footer. Every path is canonical
  root-relative POSIX.
- The `convention.md` recommendation to pair `Lifecycle: blocked` with a
  one-sided `blocked-by:` edge is **withdrawn** — it is the most likely
  source of a legacy one-sided edge. `Lifecycle: blocked` and the
  `blocks`/`blocked-by` edge stay explicitly **uncoupled**: a blocked
  lifecycle does not require an edge, and an edge does not set a lifecycle.
- **BREAKING — `docs archive` now refuses where it used to complete** (M28).
  When a still-active document **outside the plan** declares itself
  `child-of` a document the plan would archive, the write refuses at exit 2
  before any byte moves — a parent archived out from under a live child:

  ```console
  $ docs archive plan.md
  docs: archive: live-child.md is still active and declares 'child-of: plan.md', which this operation would archive; refusing before any write
  docs: archive: 1 still-active child(ren) would be stranded; zero bytes written
  ```

  The refusal names both ends, one line per orphaned pair, prints even under
  `--quiet`, and applies to all three archive shapes including a plain
  `docs archive FILE`. Every **other** still-active inbound reference — any
  other `Related:` verb, free-form verbs included, and every body link — is
  **reported and not refused**, because a milestone closeout is supposed to
  leave the tracker and the plan pointing at the completed work. Repair by
  archiving the child first, or by widening the scope to include it.
- **`docs mv` and `docs archive` now write prose bytes**, including into
  already-archived documents whose destinations a move makes stale. Both were
  previously metadata-only writers. The blast radius is the move-driven
  exception's, unchanged: a document is written iff a `Related:` target or a
  local body-link destination of its resolves to a document moving in **this**
  operation, and then only that bullet and those destination tokens change.
- **`docs mv` plans before it moves.** 1.x renamed the file and rewrote
  references afterwards; a class-2 rebase needs the moved document's own text
  and both of its paths, and an all-or-nothing contract needs the plan
  complete before the move. A handled failure — an unwritable planned
  referrer, a stale recorded span, two overlapping planned spans — now
  refuses at exit 2 with **zero bytes written, the moved document included**.
  A residual `OSError` during execution carries the exact partial-state
  admission (`Moved:` / `Rewritten:` / `Not written:`), replacing 1.x's bare
  `docs: mv: <OSError>`.
- **A preview now adopts failures of plan *construction*.** Both previews
  walk the tree to build the plan they print, so a **malformed** tree makes
  `docs mv --dry-run` exit 2 and `docs archive --cascade-dry-run` exit 1 —
  the same codes their write paths already use. Plan *consequences* are still
  only reported: a preview whose plan the strand-check's leg 1 would refuse
  prints that verdict and exits **0**.

### Fixed

- **An over-long path segment no longer crashes `docs check`.** A `Related:`
  target or a body-link destination with a path segment longer than the
  filesystem allows made the existence probe raise
  `OSError [Errno 36] File name too long` instead of returning False, so
  `docs check` exited with a traceback rather than a finding. Both probes now
  treat an unusable path as "does not exist" and report `broken-ref` /
  `broken-body-link` as they should. The `broken-ref` half is a 1.x bug; it is
  fixed here because M27's body links widen the same exposure by roughly 400x.

### Upgrading from 1.x

Run the repair loop until `docs check` is clean:

```console
$ docs check
m25.md
  error: [missing-inverse] Related: 'precedes: m26.md' has no inverse; m26.md must declare 'follows: m25.md' (or remove the edge)
$ docs relate add m25.md precedes m26.md      # the edge is right — complete it
docs: relate: no change — 'precedes: m26.md' already present in m25.md
docs: relate: added 'follows: m25.md' to m26.md
$ docs check
docs: no violations found
```

The finding never chooses for you. If the edge is **wrong**, delete the pair
instead — `docs relate remove m25.md precedes m26.md`. Paths can be copied
straight out of the finding: relative endpoints resolve root-relative first.
An archived endpoint additionally needs `--reason "…"`.

**Replace every bare `--cascade` archive.** The most common real-world
caller is a milestone-completion step, so `docs archive <slug>.md --cascade`
becomes a preview and then an explicit scope:

```console
$ docs archive <slug>.md --cascade-dry-run          # see the whole neighbourhood
$ docs archive <slug>.md --cascade-only '<slug>*'   # write exactly that scope
```

`--interactive` has no direct replacement — preview, then scope. A scope
that matches nothing now refuses instead of quietly archiving the primary
alone, so a typo fails loudly rather than looking like success.

**Fix `duplicate-field` findings first.** They are repaired by hand — open
the doc and merge the entries under a single label, keeping the ones you
want:

```markdown
Related:                     Related:
- precedes: m26.md           - precedes: m26.md
                       →     - references: notes.md
Related:
- references: notes.md
```

Do this before working through `missing-inverse`. On a duplicated doc the
two rules disagree by construction: the parser reads the **last** copy of a
label while `docs relate`'s editors act on the **first**, so a repair can
report success and leave the finding in place. Merging the labels makes the
tree diagnosable again.

**Repair the body links.** The two findings ask for different things, and
the message tells you which:

```console
$ docs check                  # read the findings: line, raw destination, candidate
                              # broken-body-link       -> rebase the destination
                              # outside-root-body-link -> replace it with a URL
$ docs check                  # clean
```

The overwhelmingly common cause of `broken-body-link` is a relative link in
a document an **older `docs` archived**: the destination was correct at the
document's original location and no version of the tool has ever rebased it,
so it now needs the `../../` that the move into `archive/YYYY-MM-DD/` should
have added. The finding prints the candidate path the tool probed, which is
what makes the missing prefix obvious. `outside-root-body-link` is different
in kind: the destination names something the tree does not own, so it becomes
a **URL**.

If a finding names a code sample rather than a real link, fence the sample
(every code sample in this project's own docs already is), put it in an
inline code span, or backslash-escape the opening bracket — any of the three
makes the span invisible to the scanner. There is deliberately **no 4-space
indented-code rule**: a link indented four spaces inside a blockquote or a
list continuation is a real link and **is** checked.

**Repair the body links once — then the moves keep them repaired.** M27
detects and M28 repairs, in that order, so between them there is one
upgrade chore and after them there is none: `docs mv` and `docs archive`
rebase what *they* make stale, and never repair damage they did not cause.
Three things change for existing automation:

1. **A move now edits prose**, in documents you did not name and in
   already-archived documents whose destinations point at what is moving.
   Diffs get larger and are no longer metadata-only. If you gate on "the move
   touched only `Related:` lines", that gate is now wrong.
2. **An archive now refuses in a case it previously completed** — a plan
   that would archive a document a still-active document declares itself
   `child-of`. It exits 2 and writes nothing. Archive the child first, or
   widen `--cascade-only` to include it. Preview with `--cascade-dry-run` (or
   plain `--dry-run`), which reports the verdict at exit 0 rather than
   adopting it, and read the `strands` array if you parse `--json`.
3. **stderr changes on both verbs.** No exit code changes and no test pins
   these, so they break **silently** for anyone parsing stderr:

   | 1.x | 2.0 |
   |---|---|
   | `docs: would move <old> -> <new>` | `docs: mv: would move <old> -> <new>` |
   | `docs: moved <old> -> <new> (<N> reference(s) rewritten)` | `docs: mv: moved <old> -> <new>` |
   | — | `docs: mv: <R> destination(s) in <D> document(s), <E> Related: bullet(s)` — **new, on every move** |
   | — | `docs: archive: <R> destination(s) in <D> document(s) rebased` — **new, on every archive** |
   | `docs: archive: preview only — nothing was written` on a **cascade** preview only | …now on **every** preview, including a plain `--dry-run`, and always the last line |

   The two `docs mv` lines gain the `mv: ` verb prefix that every other verb
   already carries, and the trailing count moves into the richer counts
   footer. The two footers are **unconditional** — a link-free tree still
   prints `0 destination(s) in 0 document(s) rebased`, because a zero is
   positive evidence the new rewrite phase ran rather than silently doing
   nothing. If you parse either verb's stderr, switch to `--json`: `docs mv`
   gains a record in this release precisely so nothing has to.

**The archive-date witness needs no upgrade work at all.** This is the one
change in the train with that property, and it is deliberate: the
`archive-date-drift` rule fires **only when a document carries the
`Archived:` field**, and nothing before 2.0.0 ever wrote one. A 1.x tree
therefore gains **zero** findings from it on upgrade — however large its
archive, and however it was organised. There is **no backfill**, no
`docs fix-dates`, and no sweep: no honest source exists for the archive date
of a document the tool never observed being archived, and inventing one is
precisely the falsification the rule exists to prevent. Coverage grows by
use — your **next** archive writes the witness for the documents it moves,
and the historical population stays silent forever. `docs migrate --apply`
likewise never writes it (its archive-directory dates come from `Updated:`
or the file's mtime, which on a fresh clone is *today*), and a foreign
`Archived:` line it finds is demoted into the `## Migrated metadata` body
section as `Migrated-Archived:` — preserved, never promoted.

Two things do change, and neither is a repair queue:

1. **`docs mv` between two dated archive directories now refuses** — see
   *Changed*. If you have automation that performs one, it now exits 2 and
   writes nothing. The by-hand escape is in the refusal's own second line.
2. **A hand-adopted tree that already carries an `Archived:` label whose
   value is not a date in the tree's `date_format` gains a new `bad-date`
   error** naming `Archived:` rather than `Updated:`. This is the one
   residual of the present-only contract, and it is narrow by measurement:
   there are zero such labels anywhere in this project's own tree or its
   fixture corpus, and a tree adopted through `docs migrate` cannot acquire
   one, because migrate demotes rather than promotes. Repair it by giving
   the field a real date in the tree's format, or by removing the line.

## 1.8.0 — 2026-07-03

### Added

- **PyPI update-check notice** (M21). `docs` now performs a best-effort,
  once-per-24h check for a newer `docs-cli` release on PyPI and, when one
  exists, emits a single advisory line to **STDERR**:
  `docs: update available <current> -> <latest> — run: pip install -U docs-cli`.
  This is the tool's first and only network surface — a stdlib-`urllib` HTTPS
  GET to `https://pypi.org/pypi/docs-cli/json` with a 1.0s timeout (the
  zero-dependency wheel is preserved). It is **fail-silent always** (offline /
  timeout / non-200 / malformed JSON / corrupt cache all degrade to
  byte-identical output and exit code, no traceback) and **never** touches
  stdout or changes the exit code. State is cached per-user at
  `${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json` with two independent
  24h throttles (one network attempt per day, one notice per day). Unlike `gh`
  / `npm`, the notice **shows on non-TTY too** — the primary consumer is an
  agent that is itself the actor who runs the update. Suppression: `--quiet` and
  `--json` silence the notice (but still warm the cache, keeping `--json` stdout
  byte-clean); `CI`, `DOCS_CLI_NO_UPDATE_CHECK`, and `DO_NOT_TRACK` (presence,
  any value) disable the feature entirely — no network, no notice.
- **Agent-aware `install-skill`** (M23). `docs install-skill` now treats
  `--dest` as the single, agent-agnostic source of truth for where the bundled
  skill lands. When `--dest` is omitted, resolution is **TTY-aware**: an
  interactive human is prompted (the `~/.claude/skills/docs/` default is
  offered; empty input accepts it); a non-TTY caller (an agent) is **never**
  blocked on a prompt — it falls back to the default and exits 0. The
  `install-skill` help/description are reworded from "Claude Code skill" to the
  agent-agnostic **"agent skill"** framing.
- **Recorded-dest state file** (M23). On any successful `install-skill` (copy,
  symlink, or already-identical no-op), the resolved destination **path** is
  recorded to `${XDG_STATE_HOME:-~/.local/state}/docs-cli/install-skill.json`
  (schema `{"dest": "<absolute-path>"}`, last-write-wins, fail-silent). It
  records a **path only** — never the installed skill's content or a hash — and
  a refusal records nothing.
- **Recorded-dest skill-refresh hint** (M23). M21's update-check notice gains a
  second STDERR line pointed at the recorded dest:
  `docs: refresh the agent skill at <dest> — run: docs install-skill --dest <dest> --force`.
  It is strictly coupled to the CLI notice — appended only when that notice
  actually prints, under the **same** suppression matrix (`--quiet` / `--json` /
  `CI` / `DOCS_CLI_NO_UPDATE_CHECK` / `DO_NOT_TRACK`) and 24h throttle — replays
  the recorded path verbatim (no filesystem check), and is absent when no dest
  has been recorded.

### Documentation

- **Doc-tree root placement guidance** (M22). The convention spec
  (`convention.md` §Subdirectories) and the bundled `docs` skill now teach
  where to put `.docs.toml`: a `Project:` is a metadata field, **not a
  directory**, so a single project needs no subdirectory of its own. Because
  `Related:` paths are root-relative, nesting a lone project beneath a parent
  root prefixes every intra-project sibling reference with a redundant
  `<subdir>/`. The recommended default is to make the project's own directory
  the docs root (docs flat, clean refs), reserving per-project subdirectories
  for genuinely multi-project trees (group by `Project:` metadata, not by
  folder). Documentation only — no CLI surface or behavior change.

## 1.6.5 — 2026-06-12

Post-edit validation ergonomics (M19). Two additive, backward-compatible
affordances on the post-edit loop plus one cosmetic help-string fix.

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
