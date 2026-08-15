# docs — CLI Spec

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-08-15

Related:
- pairs-with: convention.md

## Scope

This spec defines the `docs` command-line surface: subcommands, flags, output formats, and exit codes. The on-disk convention it operates on is defined in `convention.md`.

## Invocation

```
docs <subcommand> [args] [flags]
```

The binary expects to find a docs root by walking up from the current directory until it finds either `.docs.toml` or the directory passed via `--root`. If neither is present, the **read** verbs (`index`, `list`, `check`) operate on the current directory with defaults (project name = directory name, archive subdir = `archive/`).

**Create/mutate refusal (M14 — A2; M12 — OQ-C).** The verbs that *create* a doc (`docs new`) or stamp/rename in place (`docs touch`, `docs project rename`) refuse the cwd-as-root fallback: if no `.docs.toml` is found up the ancestor chain and no `--root` is given, they exit 2 and write nothing rather than silently scaffolding into an unmanaged directory with default config. (The read verbs above keep the silent cwd-fallback — surfacing the wrong tree on a read is recoverable; writing into it is not.) See each verb's Exits paragraph for the exact message.

Global flags:

- `--root DIR` — explicit docs root.
- `--json` — emit machine-readable JSON output where applicable.
- `--quiet` — suppress non-error output.
- `--dry-run` — show what would change; make no edits.
- `--version` — print `docs <version>` and exit 0.

## Subcommands

### `docs new <role> <slug> [--project NAME] [--title "…"] [--body-from PATH|-]`

Scaffold a new doc in the active tree.

- `<role>` must be in the built-in or configured Role vocabulary.
- `<slug>` becomes the filename (`<slug>.md`), created in the resolved docs root. A trailing `.md` on the slug is stripped. The slug may name a subdirectory (`sub/feature` → `sub/feature.md`); missing intermediate directories are created. The slug may **not** be an absolute path, contain a `..` component, or resolve under the archive subtree — those are rejected. The slug's **final path segment may not be empty** (M14 — A3): `foo/` or `foo/.md` would write an invisible `foo/.md` dotfile (skipped by every read verb), so it is rejected with exit 2 `docs: invalid slug <slug>`. To create a doc in the archive subtree use `docs archive`; to relocate an existing doc use `docs mv`.
- `--title` overrides the inferred H1 (default: the slug's last path segment, title-cased, with `-` and `_` treated as word separators).
- Writes the metadata block with `Lifecycle: draft`, `Role: <role>`, `Project: <inferred>`, `Updated: <today>`.
- Does not refresh INDEX (the new doc is empty; the user is expected to fill it, then run `docs index` or let another verb trigger it).
- `--body-from PATH` (M8 — F9) reads body content from `PATH` (or `-` for stdin) and appends it under the scaffolded frontmatter. Closes the read-before-write friction in agent flows — one atomic Bash call writes the complete file. The body text is appended verbatim (the file ends byte-equal with the body).
  - **Refusal heuristic (OQ-E; M15 — C4).** The supplied body is refused
    **only when it carries an actual metadata block**, not whenever any line is
    `Label:`-shaped. Two signals trip the refusal:
    - **(a) a leading `---` YAML fence** — the first non-blank line of the body
      is `---`, the footgun of pasting a whole front-matter-fenced document as a
      body; or
    - **(b) a required-field cluster** — within the first ~20 lines (after an
      optional leading `# H1`), a **contiguous run** of metadata-shaped lines
      carries **≥ 2** of the required-field labels `{Lifecycle, Role, Updated}`
      on adjacent lines. This is the shape of a real convention metadata block
      (the footgun of pasting a whole doc-with-frontmatter as a body).

    A **lone** prose required-field line (a single `Updated:`/`Reason:`/`Plan:`
    line in spec/test-matrix prose) no longer trips the refusal — it is
    accepted and appended verbatim. (`Reason:`/`Plan:` are not even required-
    field labels, so they never contribute to the cluster; this is exactly the
    dogfood body — a test-matrix section opening `## Risk level` / `Reason: …` —
    that the old any-`Label:` heuristic wrongly refused. `edge-case-keyword.md`,
    whose only metadata-shaped line is a prose `Plan:` line, now **passes**.)

    On a refusal `docs new` exits 2 with the message `--body-from content
    appears to contain a metadata block. Pass body content only — docs new owns
    the frontmatter.` plus the first five body lines as preview (the stable
    error tokens are unchanged from M8).

**Strict-root refusal (M14 — A2).** `docs new` refuses the silent
cwd-as-root fallback (which once misfired by scaffolding a doc at a repo
root with default config). Resolution mirrors `docs touch` /
`docs project rename` (M12 — OQ-C):

- If `--root` is **not** given and no `.docs.toml` exists in the cwd's
  ancestor chain, `docs new` exits 2 + stderr
  `docs: new: <cwd> is not under a docs root with .docs.toml; refusing`
  and writes nothing.
- An explicit `--root <dir>` bypasses the up-walk **only when**
  `<dir>/.docs.toml` exists; if `--root` is set but its `.docs.toml` is
  missing, `docs new` refuses with
  `docs: new: --root <root> does not contain .docs.toml; refusing`
  (exit 2).

Exits 2 on invalid role, invalid slug, missing `--body-from` path, a body that trips the metadata-block refusal (a leading `---` fence or a ≥ 2 required-field cluster — M15 C4), or the strict-root refusal; 1 on existing file.

### `docs index [DIR] [--exclude PATTERN]`

Regenerate `INDEX.md` in the docs root.

- Walks the tree, parses every `.md` file's metadata.
- Rewrites only the content between `<!-- docs:generated start -->` and `<!-- docs:generated end -->` markers.
- Creates the markers if INDEX.md exists but lacks them; creates the whole file if it doesn't exist.
- Idempotent: running twice with no changes produces no diff.
- `--exclude PATTERN` (M8 — F3, repeatable) skips paths matching `PATTERN`. Layered on top of `.docs.toml [exclude]` and a root `.docsignore` — see [Common: exclusion](#common-exclusion) below.

Exits 0 always (warnings printed to stderr; use `docs check` for hard validation).

### `docs archive <file> [--reason "…"] [--date YYYY-MM-DD] [--cascade-dry-run] [--cascade-only GLOB] [--json] [--dry-run] [--quiet]`

Atomically archive a doc.

1. Reads `<file>`, validates it has required metadata.
2. Writes `Lifecycle: archived` and bumps `Updated:` to today (or `--date`).
3. Moves the file to `<archive_dir>/<YYYY-MM-DD>/<basename>`.
4. Regenerates INDEX.md.

`--reason` is appended as a free-form `Archived-reason:` metadata line
(harvested but uninterpreted). It applies to the **primary document
only** (M26 — D1): a cascaded candidate never receives an
`Archived-reason:` line, because the reason explains why *this* archive
was requested, not why each neighbour moved.

**Invariant: `docs archive` never prompts on stdin at all (M26 — D2).**
Retiring `--interactive` removed this verb's only stdin-reading path, so
the M14 (B1) invariant is now unconditional — no flag, and no
combination of flags, makes `docs archive` read stdin. Every invocation
runs to completion, or refuses with a non-zero exit, without ever
blocking. An autonomous agent never stalls.

#### Safe explicit archive selection (M26 — D1)

Relationship verbs supply the **candidate set**; they never grant
**authorization**. Exactly three shapes exist, and no other invocation
writes a related document:

| Invocation | Writes | Exit |
|---|---|---|
| `docs archive FILE` | `FILE` only | 0 |
| `docs archive FILE --cascade-dry-run [--cascade-only GLOB]` | nothing (preview) | 0 |
| `docs archive FILE --cascade-only GLOB` | `FILE` plus exactly the one-hop candidates matching `GLOB` | 0 |

`docs archive FILE` stays **quiet** on stderr about the candidates it
leaves in place: that is the correct safe behaviour, and a notice on
every single-document archive would be noise. `--cascade-dry-run` is
where candidates are named in prose; `--json` carries the whole
candidate set in **every** mode, including a plain `docs archive FILE`.

`--cascade-only GLOB` composes with the global `--dry-run`, producing
byte-for-byte the same preview as
`--cascade-dry-run --cascade-only GLOB`.

##### Retired flags (M26 — D2)

`--cascade` and `--interactive` are **retired in docs 2.0**. They stay
**registered** in argparse — so an obsolete script or workflow skill
gets a legible, actionable refusal rather than argparse's generic
`unrecognized arguments` error — and they refuse unconditionally:

```
docs: archive: --cascade is retired in docs 2.0 and writes nothing; preview with `docs archive <file> --cascade-dry-run`, then write an explicit scope with `docs archive <file> --cascade-only '<glob>'`
docs: archive: --interactive is retired in docs 2.0 and writes nothing; preview with `docs archive <file> --cascade-dry-run`, then write an explicit scope with `docs archive <file> --cascade-only '<glob>'`
```

The check runs **first** — immediately after argument parsing, before
any filesystem access — so it wins over a missing file, a malformed
`--date`, and a malformed primary. It is independent of `--dry-run`,
`--cascade-dry-run`, `--cascade-only`, `--json`, `--date`, `--reason`,
and `--quiet`, so the combination matrix contains no "it depends" cell,
and it prints **even under `--quiet`**. Exit **2**, **zero bytes
written**, no `--json` record. When both retired flags are passed,
`--cascade` is the one reported (declaration order). Neither flag is in
an argparse mutually-exclusive group any more: the single unconditional
refusal covers every combination.

A later major version may delete the flags outright.

**Upgrading from 1.x.** `docs archive <slug>.md --cascade` becomes:

```sh
docs archive <slug>.md --cascade-dry-run          # see the whole neighbourhood
docs archive <slug>.md --cascade-only '<slug>*'   # write exactly that scope
```

`--interactive` has no direct replacement — preview, then scope.

##### Candidate discovery (M26 — D3)

A **candidate** is a one-hop `Related: pairs-with` or `Related: child-of`
edge of the primary document. **One hop only — no transitive cascade**
(the M2 decision is unchanged). No other verb is ever a candidate; in
particular M25's six reciprocal verbs (`precedes`/`follows`,
`depends-on`/`required-by`, `blocks`/`blocked-by`) are not, because
sequence, dependency, and blocking do not imply archive membership.

- The set is **deduplicated on the canonical root-relative POSIX path**
  (`posixpath.normpath` of the declared target), so `./b.md`,
  `sub/../b.md`, and `b.md` are one candidate. **First declaration
  wins** — it supplies the reported verb — and the surviving order is
  `Related:` declaration order.
- `--cascade-only GLOB` is matched against that same **canonical**
  path, so an unusual spelling can neither dodge nor defeat a scope.
  `GLOB` is compiled by the matcher `compile_exclude_predicate` uses
  (gitignore-flavoured: `**`, `*`, `?`). A pattern with no `/` is matched
  against the path's **final segment** at any depth, so `'b.md'` selects
  `sub/b.md` but `'sub'` selects nothing — use `'sub/'` for "everything
  under `sub/`", or `'sub/**'`.
- A **self-edge** — a candidate whose canonical path equals the
  primary's — is silently excluded. It is not a candidate and is not
  reported as ineligible.
- The candidate scan deliberately does **not** consult `[exclude]` /
  `.docsignore`. Those govern the tree walks (pre-flight validation and
  the reindex), not the primary document's own declared edges.

Three conditions make a candidate **ineligible**. An ineligible
candidate is never written, is named in the preview, and carries a
machine-stable `exclusion_reason` in the `--json` record (named to keep
it distinct from the record's top-level `reason`, which carries
`--reason`):

| `exclusion_reason` | Condition |
|---|---|
| `already-archived` | The canonical path is the archive subtree itself or lies under it (per `[archive] dir`). Archiving an archived document is meaningless, and doing it silently relocates and re-dates history. |
| `unresolved-target` | The target does not resolve to a file. `docs check`'s `broken-ref` still owns that finding. |
| `outside-root` | The canonical path escapes the docs root (e.g. `../escape.md`). |

Two of those conditions can hold at once (`../ghost.md` both escapes the
root and does not exist), so the reported reason is fixed by
**precedence: `outside-root`, then `already-archived`, then
`unresolved-target`** — the more structural fact wins, and the answer is
deterministic.

The fourth `exclusion_reason`, `not-selected`, is not an ineligibility: it marks
an eligible candidate that the scope did not select (or that had no
scope to select it). Ineligibility always wins over it — an
already-archived candidate reports `already-archived` whether or not a
scope was given.

##### Preview (M26 — D6)

`--cascade-dry-run`, with or without `--cascade-only`, writes nothing,
exits 0, and names the primary's destination plus **every** one-hop
candidate — selected, not selected, or ineligible. A filtered preview
still names what the scope is leaving behind, because that is exactly
the judgement the preview exists to support.

Human output goes to **stderr**, gated on `not --quiet`, so `--json`
stdout stays byte-clean:

```
docs: archive: would archive <primary-rel> -> <dest-rel>
docs: archive: candidate <rel> — selected -> <dest-rel>
docs: archive: candidate <rel> — not selected (outside --cascade-only '<glob>')
docs: archive: candidate <rel> — not selected (no --cascade-only scope)
docs: archive: candidate <rel> — ineligible (already archived)
docs: archive: candidate <rel> — ineligible (target does not resolve to a file)
docs: archive: candidate <rel> — ineligible (target resolves outside the docs root)
docs: archive: --cascade-only '<glob>' matched none of the <N> one-hop candidate(s)
docs: archive: <N> candidate(s): <S> selected, <U> not selected, <I> ineligible
docs: archive: preview only — nothing was written
```

Every path is the **canonical root-relative POSIX** form. The `candidate`
lines and the counts footer are printed only when a cascade flag is
present (`--cascade-dry-run` or `--cascade-only`); a plain
`docs archive FILE [--dry-run]` prints just its own line (D1's quiet
rule). The `matched none` line appears only under a preview whose
`--cascade-only` selected nothing.

**A preview is never a write, so it never fails.** A `--cascade-only`
that selects nothing still exits **0** under `--cascade-dry-run` (or the
global `--dry-run`); the miss stays visible as the `matched none` line
and as every candidate reported `"selected": false` in the `--json`
record. The exit-2 refusal below
governs the **write** path only.

That carve-out is about a **valid glob that selects nothing** — a
selection outcome. An empty, comment-only, or negated (`!`)
`--cascade-only` is a **malformed invocation**, not a selection outcome,
and is refused in **every** mode, a preview included: it is rejected at
check-order step 2, before any candidate work, like any other bad
argument.

A real apply prints the same lines, with two differences: the primary's
line reads `docs: archive: archived <primary-rel> -> <dest-rel>`, and
the `preview only` line is absent. The `candidate` lines are identical
in both modes — the plan is what happened, because a scoped write is
all-or-nothing.

##### The scoped write and its pre-flight (M26 — D4)

`--cascade-only GLOB` builds and validates **one complete plan** before
mutating anything. The plan covers the primary and every selected
candidate, and the pre-flight proves, for each member:

- the document has an editable metadata block — an H1 followed by a
  metadata block `parse_metadata_block` can rewrite. This proof is
  deliberately narrower than a full `parse()`: a member with an H1 but a
  missing or out-of-vocabulary `Lifecycle:` is caught by the whole-tree
  validation walk at step 8 instead, also at exit 1 and also before any
  write, with a less specific message;
- the document is **not** already under the archive subtree — an
  already-archived **primary** is a refusal (see below), not a
  re-dating;
- its archive destination is computed and is not already occupied;
- no two members resolve to the **same** destination (the basename
  collision that silently dropped a document in 1.x);
- the source file and the destination directory are writable — checked
  with an explicit access test, because an atomic write succeeds on a
  read-only file inside a writable directory. When the dated
  destination directory does not exist yet, the nearest existing
  ancestor is checked instead.

**Check order.** Every check runs before any write, in this fixed order,
so the message an operator sees always names the most specific cause:

1. the retired flags (`--cascade` / `--interactive`) — before any
   filesystem access at all;
2. an empty, comment-only, or negated (`!`) `--cascade-only` — purely
   lexical;
3. root resolution, `.docs.toml`, `--date`, the primary exists, resolves
   **inside** the root, and parses;
4. the primary is not already under the archive subtree;
5. the plan is built (pure) — and a preview stops here, prints, and
   exits 0;
   - since M28 a preview first runs the whole-tree walk (step 8) and
     builds the rewrite plan and the strand analysis from it, so that it
     can print them. That is why a preview now **adopts a malformed
     tree's exit 1** — see *A preview adopts plan-construction failures*
     below;
6. the empty-selection refusal (D5);
7. **the plan pre-flight** — the five per-member proofs above;
8. the whole-tree validation walk (M12 / M14 — A6), which still honours
   `[exclude]` / `.docsignore` and still exits 1;
   - the rewrite plan and the strand analysis are built from this walk
     (M28 — D1 / D6);
   - **the rewrite-plan pre-flight** (M28 — D4): every document the plan
     will write is writable, every recorded destination span still
     matches the text it was scanned from, and no two spans in one
     document overlap — exit **2**;
   - **the strand-check's leg-1 refusal** (M28 — D6) — exit **2**;
9. execution.

The plan pre-flight deliberately precedes the whole-tree walk: both can
be triggered by the same malformed file, and naming the document the
operator actually asked for is strictly more actionable than naming an
unrelated referring doc. M28 inserts its steps **around** that ordering,
never through it — the write path's walk stays at step 8 — so every
message precedence this order froze is unchanged.

Any **handled** failure refuses the whole operation: non-zero exit,
**zero bytes written**, including the primary, and no `--json` record.
Only after the plan validates does execution begin.

Pre-flight refusals, each printed even under `--quiet`:

```
docs: archive: <rel> is already under the archive subtree; refusing before any write
docs: archive: <path> is outside the resolved docs root (<root>); refusing before any write
docs: archive: <relA> and <relB> would both archive to <dest-rel>; refusing before any write
docs: archive: <rel> is not writable; refusing before any write
docs: archive: <dest-dir-rel> is not writable; refusing before any write
docs: archive: <rel> has no editable metadata block; refusing before any write
docs: archive: archive destination already exists: <dest-rel> (for <rel>); refusing before any write
```

The archived-primary refusal is unconditional across all three D1
shapes — `docs archive F`, `docs archive F --cascade-dry-run`, and
`docs archive F --cascade-only GLOB`. D1's table describes
authorization, not an exemption from validity checks.

**Residual boundary, stated plainly.** Every failure the tool can
foresee is handled by the pre-flight. An unexpected `OSError` *during*
execution is reported as an exact **partial-state admission** — naming
which documents moved and which remain at their original paths — and is
**not** rolled back:

```
docs: archive: write failed for <rel>: <err>; PARTIAL ARCHIVE — not rolled back. Archived: <relA> -> <newA>, <relB> -> <newB>. Still at their original paths: <relC>, <relD>. Repair manually.
```

When nothing had moved yet the archived list is rendered as the literal
word `none` (`Archived: none.`), never as a blank. Exit 2, no `--json`
record. Extending M25 — D5's staged-publish-plus-rollback contract from
two documents to N was considered and explicitly declined for M26.

##### An empty selection is a refusal (M26 — D5)

A `--cascade-only GLOB` **write** that selects nothing refuses with exit
**2** and zero bytes written — the primary is **not** archived — and
says which case it is:

```
docs: archive: --cascade-only '<glob>' matched none of the <N> one-hop candidate(s); refusing before any write
docs: archive: <rel> has no one-hop pairs-with / child-of candidates; refusing before any write (use `docs archive <file>` to archive it alone)
```

"Matched" means **selected**: eligible *and* in scope. `<N>` is the size
of the whole deduplicated candidate set, ineligible members included, so
a glob that only hits an already-archived neighbour reports the first
message and the preview explains why.

An empty or comment-only pattern, and a **negated** (`!`-prefixed) one,
are their own refusals, before any candidate work:

```
docs: archive: --cascade-only must not be empty
docs: archive: --cascade-only does not support negated ('!') patterns; state the exact bounded selection
```

A negated pattern means "everything except X" — an unbounded selection,
which is precisely what D1 exists to prevent. `--cascade-only` states
the exact bounded set to write, so `!` is refused rather than silently
ignored (1.x compiled the flag and discarded the negation bit).

Primary-only archive already has an unambiguous spelling —
`docs archive FILE` — so a scope that selects nothing is always a
mistake, and in 1.x it was indistinguishable from success.

##### `docs archive --json` (M26 — D7)

`--json` is declared locally on the `archive` subparser (as `check`,
`list`, `migrate`, and `relate` do) and emits **one** operation-plan
record on stdout, with an **identical shape** for a preview and for a
real apply, so the two are diffable:

```json
{
  "primary": {
    "source": "docs/m25.md",
    "path": "m25.md",
    "destination": "archive/2026-08-12/m25.md"
  },
  "date": "2026-08-12",
  "scope": "m25-*",
  "reason": "milestone closed out",
  "candidates": [
    {"path": "m25-impl.md", "verb": "pairs-with", "selected": true,
     "destination": "archive/2026-08-12/m25-impl.md", "exclusion_reason": null},
    {"path": "cli.md", "verb": "pairs-with", "selected": false,
     "destination": null, "exclusion_reason": "not-selected"},
    {"path": "archive/2026-01-01/old.md", "verb": "pairs-with",
     "selected": false, "destination": null, "exclusion_reason": "already-archived"}
  ],
  "rewrites": [
    {"path": "status.md", "line": 42, "column": 12,
     "old": "m25.md", "new": "archive/2026-08-12/m25.md"}
  ],
  "strands": [
    {"path": "status.md", "target": "m25.md",
     "kind": "related", "verb": "pairs-with", "line": null},
    {"path": "plan.md", "target": "m25.md",
     "kind": "body-link", "verb": null, "line": 118}
  ],
  "dry_run": true,
  "applied": false,
  "index_refreshed": false
}
```

| Field | Type | Notes |
|---|---|---|
| `primary` | object | `source` is the `FILE` argument **exactly as typed** — a relative argument stays relative; `path` is its canonical root-relative POSIX path; `destination` is the planned archive path, non-null in every mode (the primary is always selected). |
| `date` | string | The archive date actually used (`--date` or today). |
| `scope` | string \| null | The `--cascade-only` value as typed, or null. |
| `reason` | string \| null | The `--reason` value, or null. It applies to the primary only. |
| `candidates` | array | The whole deduplicated one-hop set, in `Related:` declaration order. Present in **every** mode, including a plain `docs archive FILE`. |
| `rewrites` | array | Every planned body-link destination rewrite, in walk order and, within a document, ascending `(line, column)` (M28 — D7). Present and `[]` when the move makes no destination stale, never missing. |
| `strands` | array | The strand-check's leg-2 report — every still-active inbound reference into the newly-archived set (M28 — D6). Present and `[]` when the neighbourhood is empty, never missing. |
| `dry_run` | bool | True under `--dry-run` or `--cascade-dry-run`. |
| `applied` | bool | True iff bytes were written. |
| `index_refreshed` | bool | True iff the end-of-batch reindex ran and succeeded. |

Each `candidates` record: `path` (canonical root-relative POSIX),
`verb` (the discovering verb — `pairs-with` or `child-of`, first
declaration winning), `selected` (bool), `destination` (canonical
root-relative POSIX, non-null **iff** `selected`), and
`exclusion_reason` (null **iff** `selected`, otherwise one of
`not-selected`, `already-archived`, `unresolved-target`,
`outside-root`).

Each `rewrites` record: `path` (the referrer's **old** canonical
root-relative POSIX path — the identity it had when the plan was
computed, and the one `line` indexes into), `line` and `column` (1-based,
of the destination token's first character in the text the plan was
computed from), `old` (the destination token **exactly as written**,
angle brackets and escapes included) and `new` (the replacement token,
delimiters included). The key set is closed and ordered as shown. This
is the **same** section `docs mv --json` emits, byte-comparable between
the two verbs and between a preview and an apply (M28 — D7).

Each `strands` record: `path` (the still-active referrer),
`target` (the document it will be left pointing at, at its **old**
canonical path — the one the referrer names today), `kind` (`related` or
`body-link`), `verb` (the `Related:` verb, null **iff** `kind` is
`body-link`) and `line` (1-based, null **iff** `kind` is `related` —
a `Related:` bullet carries no line in the parsed record). The key set
is closed and ordered as shown.

The top-level key set is **closed** and ordered as shown. Under a plain
`docs archive FILE` every candidate is reported with
`"selected": false, "exclusion_reason": "not-selected"` — the stderr
quiet rule (D1) governs prose, not the record, and the record exists for
the agent deciding whether a selection is correct.

**No `--json` record on a refusal.** Every refusal above exits non-zero
with empty stdout; the exit code plus the stderr message is the
contract. That includes M28's two new refusals — the rewrite-plan
pre-flight and the strand-check's leg 1 — so the `strands` array of a
plan that leg 1 would refuse is observed in its **preview**, which exits
0 and emits the record. An **INDEX-refresh** failure is different — it is
a post-write failure with every document already moved correctly — so the
record **is** emitted there, with `"applied": true,
"index_refreshed": false`, and the run exits 2.

Atomicity: the metadata edit happens in a tmp file, fsync'd, renamed; the move happens only after the edit succeeds; the index regen runs last. A failure leaves the original file untouched.

**Referring-edge rewrite (M12).** After the move, `docs archive`
rewrites every `Related: <verb>: <old-rel>` bullet across the active
tree to point at `archive/<YYYY-MM-DD>/<basename>`. Mirrors `docs mv`'s
walker (`rewrite_related_refs`) — only the `Related:` field is
considered; prose markdown references are deliberately left alone.
The rewrite is part of the same atomic batch as the move + lifecycle
edit: a single end-of-batch INDEX refresh covers everything. That
refresh honours `[exclude]` / `.docsignore` (M14 — A6) — a malformed
*excluded* file never fails the post-move reindex (same threading as
`docs touch`, above). Because a candidate is deduplicated on its
canonical path, the rewrite is fed **one pair per declared spelling**,
so a `./b.md` bullet is repointed exactly like a `b.md` one.

**Archive-subtree edge integrity (M18).** The referring-edge rewrite
now repoints **two** edge classes to the new
`archive/<YYYY-MM-DD>/<basename>` path, so that archiving interrelated
docs into the archive subtree never orphans their `Related:` edges:

1. **The moved doc's OWN `Related:` bullets** whose target is *itself* a
   doc moving in the same archive operation. Under `--cascade-only` a
   pair/trio lands with every intra-archive edge resolved (e.g. a plan
   and its log archived together each end up pointing at the other's new
   archive path); a *solo* archive of a doc whose co-moving target set is
   empty changes none of its own edges.
2. **Already-archived referrers** whose bullet points at a doc moving
   into the archive in this op — repointed to the doc's new archive path
   (previously left dangling, since the rewriter skipped archived docs).

The "targets that moved" set is defined precisely as exactly the batch's
`moves`: the primary archive target plus every selected candidate, each
carried as an `(old_rel, new_rel)` pair. An edge is rewritten **iff** its
current target equals some `old_rel` in that batch — never any other
archived-doc content. Both classes are handled by the same
`rewrite_related_refs` matcher and land in the same atomic batch as the
move (one end-of-batch INDEX refresh).

This **narrows** the prior "archive subtree is read-only" stance (M3):
archive-subtree docs are read-only **except** `Related:` bullets pointing
at a doc moving in the same archive operation, which are repointed to the
new archive path. All other archived-doc content — prose, other metadata,
and edges to docs that did *not* move — is left byte-identical.

The scoped cascade (M12 — OQ-D; M14 — B1; M26 — D1) extends this — when
the write archives selected candidates B, C, …, the referring-edge
rewrites for every moved doc run as a single atomic batch with one INDEX
refresh at the end. A scoped write is all-or-nothing, so there is no
per-candidate failure to surface. Cascade remains one-hop only (M2
decision unchanged).

##### `docs archive` exit codes (M26 — D2 / D4 / D5; M28 — D4 / D6)

Exit **1** is reserved for the conditions 1.x already assigned it; every
**new** M26 and M28 refusal exits **2**.

| Exit | Condition |
|---|---|
| 0 | Success; any preview (`--dry-run` / `--cascade-dry-run`), including one whose `--cascade-only` selected nothing, and including one whose plan the strand-check's leg 1 would refuse — the preview **reports** that verdict (M28 — D6) |
| 1 | The primary is missing, does not parse, or resolves **outside** the docs root (a symlink out of the tree, or a `--root` naming a different tree); a plan member has no editable metadata block; the archive destination slot is already occupied; the whole-tree pre-flight walk finds a malformed referring doc (move aborts) — since M28 **also under `--dry-run` / `--cascade-dry-run`**, because a preview cannot describe a tree it cannot read |
| 2 | `--cascade` or `--interactive` (retired, M26 — D2); an already-archived primary; an empty, comment-only, or negated `--cascade-only`; a `--cascade-only` **write** that selects nothing; an intra-plan destination collision; an unwritable source or destination directory; malformed `.docs.toml` or `--date`; an unreadable primary, plan member, or referring doc; a planned referrer that is not writable, or whose recorded destination span no longer matches its text, or that carries two overlapping planned spans (M28 — D4); a still-active document outside the plan declaring itself `child-of` a plan member (M28 — D6, leg 1); `OSError` mid edge-rewrite (M14 — A4); the mid-execution partial-state admission; INDEX-refresh failure |

#### Move-safe body-link rewrites (M28 — D1–D7)

Since M28 a coordinated move rebases the local Markdown body links the
move makes stale, in the same operation, in the same per-document write,
and under the same all-or-nothing contract as the `Related:` rewrite
above. Everything in this section governs **both** `docs archive` (all
three shapes of *Safe explicit archive selection*) and `docs mv` — except
the strand-check, which is `archive`-only because only `archive` produces
a newly-archived set.

M27 validates body links; M28 is the only writer of them. The scanner,
the recognised grammar and the destination-token span are M27's,
**unwidened**: images, autolinks, raw HTML, reference *uses*, and
4-space-indented code stay out, so a move never rewrites them. See
*Markdown body-link validation (M27 — D1–D4b)*.

##### The formula (M28 — D1)

A move set maps each moving document's canonical root-relative **old**
path to its **new** one. For every recognised destination occurrence in
every walked document `D`, in this fixed order:

1. classify the token **as written**; anything but `local` is copied
   byte-for-byte and the occurrence ends here;
2. resolve the destination from `D`'s **old** directory, giving a
   canonical root-relative target;
3. a target that leaves the root is copied byte-for-byte and the
   occurrence ends here — M28 never rebases an escape, and never repairs
   pre-existing damage;
4. map that target through the move set, leaving it unchanged when it is
   not a key;
5. **the no-op test** — re-resolve the token *as written* from `D`'s
   **new** directory; when that reproduces the mapped target the existing
   spelling still means the right thing, so the token is copied
   byte-for-byte and the occurrence ends here;
6. otherwise the new destination is the `posixpath.relpath` form of the
   mapped target against `D`'s new directory, with the fragment
   reattached verbatim after a single `#`.

Two independent breakages fall out of one formula, never two code paths.
**Incoming** — the target moved, so step 4 fires and `D` stays put.
**Moved referrer** — `D` itself moved, so step 6's base differs from step
2's. A document can suffer both at once. A **co-moving pair** suffers
neither: step 5 leaves a sibling link that still resolves byte-identical,
which is why archiving a plan and its log together produces a zero-byte
diff in their links to each other.

**The mapping is by canonical target, not by string.** Every spelling
that normalises to a moving document is rewritten — `plan.md`,
`./plan.md`, `sub/../plan.md` and `../plan.md` alike — because step 2
normalises before step 4 looks anything up. This differs from the
`Related:` rewriter, whose targets are root-relative and matched by exact
string.

##### What the tool writes (M28 — D3)

The emitted destination is the `posixpath.relpath` form — no leading
`./`, `..` segments where the path really does go up — which is the
spelling this convention already uses everywhere. The **delimiter form is
invariant**: an angle-wrapped destination stays angle-wrapped, a plain
one stays plain. A plain destination that cannot carry a character is
**percent-encoded**, never promoted to angle brackets. One strategy, no
"it depends" cell.

The encode set is derived from the grammar rather than guessed — a plain
destination ends at the first unescaped whitespace or unescaped `)`,
an angle destination at the first unescaped `>`, `#` opens the fragment,
`\` escapes, and `%` introduces an escape — and `%` is always encoded
**first**, so the introducer can never be double-encoded:

| Form | Encoded | Left literal |
|---|---|---|
| plain | `%`→`%25` (first), space→`%20`, tab→`%09`, `(`→`%28`, `)`→`%29`, `#`→`%23`, `<`→`%3C`, `>`→`%3E`, `\`→`%5C` | everything else, non-ASCII included |
| angle | `%`→`%25` (first), `<`→`%3C`, `>`→`%3E`, `#`→`%23`, `\`→`%5C` | everything else, **a space included** — carrying a space is what the angle form is for |

There is deliberately no blanket URL quoting: an accented or CJK filename
is emitted literally, exactly as an author would write it.

**The round-trip invariant.** Decoding an emitted token reproduces the
path and fragment it was built from, by the same decode the scanner uses.
Reattaching the fragment cannot break the token, and the proof is one
line: the fragment came out of a token that already parsed inside the
*same* delimiter form, so it contains no character that terminates that
form.

**A rewritten token is minimally encoded.** An author's redundant escape
is not reproduced — the tool renders from the decoded path and applies
only the encodings the grammar requires. A **no-op** token keeps every
byte it had, redundant escapes included, because it is copied rather than
rendered.

**M28 can never create an `outside-root-body-link`.** Both endpoints of
every rewrite are canonical in-root paths, so the relative form always
normalises back inside the root — the containment property is preserved
exactly, not re-argued.

##### What a move never touches (M28 — D2 / D3)

- **Every non-`local` destination.** `empty`, `fragment`, `scheme`,
  `protocol-relative` and `root-absolute` tokens are copied byte-for-byte,
  always.
- **A destination that was already broken, or already escaping, before
  the move.** It keeps its M27 finding; `docs check` owns pre-existing
  damage, and an unrelated repair is never a precondition for a rename.
- **Labels, titles, quoting style, fragments, and every other byte.**
  The edit is the destination token's span and nothing else.
- **Plain-text mentions, fenced code, inline code spans, and external
  URLs.** A bare filename in a sentence is prose, not a link.
- **`INDEX.md` at the root of the tree**, which is generated and is
  refreshed once at the end as it already is.

**A named limitation: excluded documents are outside the strand-check and
outside the rewrite.** `[exclude]` and `.docsignore` decide which
documents are walked, and therefore which are rewritten and which can
report a strand — exactly as they already decide which `Related:` bullets
the referring-edge rewrite repoints. They never decide what a destination
may point at. So a body link inside an excluded document is neither
rebased nor reported, and this is a knowable gap rather than an oversight.

##### Archived referrers (M28 — D5)

An archived document is written by a move **iff** a `Related:` target
**or a local body-link destination** of its resolves to a document moving
in **this** operation — and then only that bullet and those destination
tokens change. No `Updated:` bump, no `Revision:` bullet, no other byte.

This is M18's move-driven exception widened along its own axis, not a
fourth exception: same trigger, same operation, same single write. The
same uniformity governs an **active** referrer, which has never had its
`Updated:` bumped by somebody else's move either. An archived document
that is itself moved by `docs mv` has its own destinations rebased under
the same move-driven licence. See `convention.md` › *Archive subtree*.

##### Validate-all-first (M28 — D4)

The complete rewrite plan is built from one whole-tree walk, and proven,
**before the first byte moves** — for `docs mv` this inverts the historic
ordering, which moved the file and rewrote afterwards. Over exactly the
documents the plan will write, the pre-flight proves: the document parses
(the walk already proved it); it is writable by an explicit access test;
every recorded destination span still matches the text it was scanned
from; and no two planned spans in one document overlap.

Any **handled** failure refuses the whole operation — non-zero exit,
**zero bytes written**, including the moved document, and no `--json`
record. Only a residual unexpected `OSError` *during* execution produces
a partial state, and it is admitted exactly, naming what was moved, what
was rewritten and what was not written. There is no rollback.

Within one document the splices are applied in **descending start
offset**, so earlier offsets stay valid, and the `Related:` rewrite and
the archive metadata edits are applied to the same in-memory text
afterwards. One `atomic_write` per document, never two.

##### The strand-check (M28 — D6) — `archive` only

Over the completed plan, before any write, `docs archive` examines every
walked document that is **not** a plan member and **not** already under
the archive subtree — a document being archived cannot be stranded, and
an already-archived one is not still active.

**Leg 1 — refuse.** When such a document declares itself `child-of` a
document the plan would archive, that is a parent archived out from under
a live child. The write refuses at exit **2**, before any byte moves,
with one line per orphaned pair naming both ends, then a count. Leg 1
applies to all three archive shapes, including a plain `docs archive
FILE`.

**Leg 2 — report, refuse nothing.** Every other still-active inbound
reference into the newly-archived set — any other `Related:` verb,
free-form verbs included, and every body link — is named with both ends
on stderr and in the record's `strands` array.

**Leg 2 is not a damage report.** Those references are *repaired* by the
same operation; what is reported is the post-plan consequence — an active
document still points at a document that is now archived. A milestone
closeout is supposed to leave the tracker and the plan pointing at the
completed work, so leg 2 firing is the normal case, and refusing on it
would refuse the workflow the tool exists for.

**Ordering is deterministic:** referrer walk order; within a referrer,
`Related:` bullets in declaration order, then body links in `(line,
column)` order.

**A preview reports leg 1 and exits 0.** It does not adopt the verdict.

Frozen lines, each printed unless `--quiet`, except the leg-1 refusal
lines, which print even under `--quiet` as every refusal does:

```
docs: archive: rewrite <doc-rel>:<line> <old-token> -> <new-token>
docs: archive: <R> destination(s) in <D> document(s) rebased
docs: archive: strand <src-rel> — still active, '<verb>: <dst-rel>'
docs: archive: strand <src-rel>:<line> — still active, links to <dst-rel>
docs: archive: <N> still-active inbound reference(s) into the archived set
docs: archive: <child-rel> is still active and declares 'child-of: <parent-rel>', which this operation would archive; refusing before any write
docs: archive: <N> still-active child(ren) would be stranded; zero bytes written
docs: archive: would strand <child-rel> — still active, declares 'child-of: <parent-rel>'; a write would refuse
docs: archive: <N> still-active child(ren) would be stranded
```

The last two are the preview's leg-1 pair; the two before them are the
write path's. `<doc-rel>` is the referrer's **old** canonical
root-relative path and `<line>` indexes into the text the plan was
computed from. Every interpolated author token is rendered on one line,
as M27's findings are.

##### A preview adopts plan-construction failures (M28 — D6)

M26's compatibility matrix said a preview writes nothing and exits 0,
full stop. M28 amends exactly one class of that: **a preview adopts
failures of plan *construction* — it cannot describe what it cannot read
— and reports-but-does-not-adopt *consequence* verdicts.** So a malformed
tree makes `docs archive --cascade-dry-run` exit **1** and
`docs mv --dry-run` exit **2**, the same codes their write paths use,
while a leg-1 strand verdict is reported at exit 0. This closes
M26's own follow-up that the frozen check order let a preview miss a
pre-flight refusal.

### `docs mv <old> <new> [--json] [--dry-run] [--quiet]`

Move/rename a doc, rewrite every `Related:` reference that points at
`<old>` across the tree, and — since M28 — rebase every local Markdown
body-link destination the move makes stale.

- `<new>` may be a new filename in the same directory, or a different directory under the docs root.
- All matching `Related: <verb>: <old>` entries are rewritten to `<verb>: <new>`.
- INDEX regenerated. The end-of-batch refresh honours `[exclude]` /
  `.docsignore` (M14 — A6) — a malformed *excluded* file never fails the
  post-move reindex (same threading as `docs touch`).

**Body-link rewrites (M28).** The formula, the emitted spelling and its
encode sets, the no-op rule, the archived-referrer policy and the
rewrite-plan pre-flight are identical for both verbs and are specified
once, in *Move-safe body-link rewrites (M28 — D1–D7)* above. The
strand-check is **not** part of `docs mv`: it reports what an operation
leaves pointing at a **newly-archived** document, and a rename produces no
newly-archived set.

**Atomic — all-or-nothing (M14 — A1; M28 — D4).** A validate-all-first
pre-flight runs *before* the move: if any (non-excluded) doc in the tree
is malformed, `docs mv` aborts with **exit 2** *before* moving anything,
leaving the source in place, the destination absent, and every referring
`Related:` edge and body link untouched (no dangling edge, no stray
INDEX). M28 extends that guarantee to the rewrite plan — an unwritable
planned referrer, a recorded span that no longer matches its text, or two
overlapping planned spans in one document each refuse at **exit 2** with
**zero bytes written, the moved document included**. Execution then
writes the moved document's rebased text to its old path, renames it,
writes every other planned document, and refreshes INDEX once.

An `OSError` raised *during* execution is mapped to a clean **exit 2**
rather than an uncaught traceback (M14 — A4), and since M28 it carries
the exact partial-state admission:

```
docs: mv: write failed for <rel>: <err>; PARTIAL MOVE — not rolled back. Moved: <old-rel> -> <new-rel>. Rewritten: <rel>, <rel>. Not written: <rel>. Repair manually.
```

Each of the three clauses renders the literal word `none` when its list
is empty, never a blank. There is no rollback — M26 — D4's boundary,
unchanged.

**Moved-doc own-edge rewrite (M18 — D3).** Like `docs archive`'s D1,
`docs mv` repoints the MOVED doc's OWN `Related:` bullets when their
target is the doc being moved — via the same shared `rewrite_related_refs`
walker that already rewrites referrers tree-wide. So moving a doc whose
`Related:` target already lives under `archive/` (or self-referential
bullets the move touches) lands the moved doc with its own edges
resolving, not dangling. `docs mv` already rewrites already-archived
referrers (its walk carries no `doc.archived` skip), so this completes
the own-edge half and gives `mv` the same edge-integrity contract as
`archive`. M28's class-2 rebasing is the body-link half of the same
guarantee.

##### `docs mv` preview and `--json` (M28 — D7)

`--dry-run` is a real preview: it walks the tree, builds the whole
rewrite plan, and names every planned rewrite instead of a single line.
Every line prints unless `--quiet`:

```
docs: mv: would move <old-rel> -> <new-rel>
docs: mv: moved <old-rel> -> <new-rel>
docs: mv: rewrite <doc-rel>:<line> <old-token> -> <new-token>
docs: mv: <R> destination(s) in <D> document(s), <E> Related: bullet(s)
docs: mv: preview only — nothing was written
docs: mv: <rel> is not writable; refusing before any write
```

`--json` emits **one** record on stdout, with an **identical shape** for a
preview and for a real apply, so the two are diffable:

```json
{
  "old": {"source": "docs/plan.md", "path": "plan.md"},
  "new": {"source": "docs/milestone-plan.md", "path": "milestone-plan.md"},
  "rewrites": [
    {"path": "status.md", "line": 42, "column": 12,
     "old": "plan.md", "new": "milestone-plan.md"}
  ],
  "dry_run": true,
  "applied": false,
  "index_refreshed": false
}
```

| Field | Type | Notes |
|---|---|---|
| `old` | object | `source` is the `<old>` argument **exactly as typed**; `path` is its canonical root-relative POSIX path. |
| `new` | object | The same two fields for `<new>`. |
| `rewrites` | array | Every planned body-link destination rewrite. **The same section, with the same record shape, that `docs archive --json` emits** — see its field table above. Present and `[]` when the move makes no destination stale, never missing. |
| `dry_run` | bool | True under `--dry-run`. |
| `applied` | bool | True iff bytes were written. |
| `index_refreshed` | bool | True iff the end-of-move reindex ran and succeeded. |

The top-level key set is **closed** and ordered as shown. There is
deliberately **no `strands` key**: `docs mv` produces no newly-archived
set, and a permanently-empty key would be a schema wart. There is
deliberately no rewrite-count key either — the count lives in the stderr
footer, and a consumer that wants it counts `rewrites`.

**No `--json` record on a refusal**, exactly as `docs archive` has it: a
refusal is a non-zero exit plus a stderr message, with empty stdout.

##### `docs mv` exit codes (M14 — A1 / A4; M28 — D4)

| Exit | Condition |
|---|---|
| 0 | Success; `--dry-run` preview |
| 1 | `<old>` is not a file; collision — `<new>` already exists |
| 2 | Malformed `.docs.toml`; either path outside the docs root; a malformed tree caught by the validate-all-first pre-flight walk (A1) — since M28 **also under `--dry-run`**, because a preview cannot describe a tree it cannot read; a planned referrer that is not writable, or whose recorded destination span no longer matches its text, or that carries two overlapping planned spans (M28 — D4); `OSError` during execution → the partial-state admission (A4) |

### `docs list [--lifecycle L] [--role R] [--project P] [--stale N] [--json] [--exclude PATTERN]`

Query view.

- Filters: `--lifecycle` (e.g., `active`), `--role` (e.g., `spec`), `--project` (slug), `--stale N` (Updated more than N days ago). Filters are AND-combined.
- Default human output: a table grouped by Lifecycle, then Role, sorted by Updated descending.
- `--json` emits an array of records, one per doc. Schema — **breaking change at M7 (1.2)** since the M3-pinned `status` field is renamed `lifecycle`:

  | Field | Type | Notes |
  |---|---|---|
  | `path` | string | Root-relative POSIX path of the doc. |
  | `title` | string | The H1 title. |
  | `lifecycle` | string | The `Lifecycle:` value. (M7 — was named `status` in v1.1 and earlier; renamed without alias per OQ-D.) |
  | `role` | string | The `Role:` value. |
  | `project` | string | The resolved project — the doc's `Project:` value, or the docs root's configured default when the doc has no `Project:` line. Never null. |
  | `updated` | string | The `Updated:` date as ISO `YYYY-MM-DD`, regardless of the configured `date_format`. |
  | `related` | array | Each entry an object `{verb, target}`; `target` is a root-relative path. Empty array when the doc has no `Related:` block. |
  | `extra_fields` | object | Maps each non-standard metadata label to its value: a string, or an array of strings for a bullet-list field. A free-form `Status:` prose line (M7 — F0) surfaces here. Empty object when there are none. |

> **`docs list --status` was renamed `docs list --lifecycle` at
> M7. The breaking-rename has no backward-compat alias.**

> **`[check] stale_days` does NOT affect `docs list --stale` (M19 — Q6).**
> The `.docs.toml [check] stale_days` config key is scoped to **check**
> semantics only. `docs list` keeps `--stale` as an explicit filter: bare
> `docs list` (no `--stale`) lists everything regardless of any configured
> `stale_days`, and an explicit `docs list --stale N` filters by N as always.

Exits 0.

### `docs check [DIR] [--stale N] [--json] [--exclude PATTERN]`

Validate the tree. Reports (and exits nonzero on) any of:

- Missing or empty required metadata fields (`Lifecycle`, `Role`, `Updated`).
- `Lifecycle` or `Role` not in the (built-in ∪ configured) vocab.
- `Updated:` not parseable as `YYYY-MM-DD`.
- Structural breakage: a missing H1. (A malformed line inside the metadata block ends the block early rather than raising; its effect surfaces as a missing required field, not as a separate finding.)
- Lifecycle/location mismatch (`Lifecycle: archived` outside archive subtree, or any other lifecycle inside) — rule `status-drift` (stable rule id from M3).
- `Related:` paths that don't resolve to a file under the docs root.
- (With a stale window — see **Stale-window resolution** below) `Lifecycle: active` docs with `Updated:` more than N days ago.
- (M7 — F1) A missing `Role:` line whose value is resolvable from an H1
  trailing-word signal or a section-header pattern produces a
  medium-confidence inference — `severity: warning`, rule
  `medium-confidence-inference`, exit code 1.
- (M10 — OQ-F + OQ-H) An extra metadata label that is neither on the
  built-in always-allowed set (`Lifecycle` / `Role` / `Project` /
  `Updated` / `Related` / `Archived-reason` / `Revision`) NOR on the
  `[vocabulary] add_fields = [...]` allowlist in `.docs.toml`
  produces `severity: warning`, rule `unknown-field`, exit code 1.
  The rule is **opt-in**: an absent or empty `add_fields` switches
  it off entirely (trees without the allowlist see no change).
  Matching is case-sensitive exact match — `add_fields = ["Owner"]`
  allows `Owner:` but not `owner:`. `Revision:` joins the built-in
  set in M25 because `docs relate` itself writes that label onto an
  archived endpoint (see `docs relate` below) — a label the tool
  writes must never trip the tool's own allowlist warning.
- (M25 — D7) A **metadata label that appears more than once** in one
  document's metadata block — `severity: error`, rule `duplicate-field`,
  exit code 2, one finding per repeated label. See *Duplicate metadata
  labels* below.
- (M25 — D2) A **recognized reciprocal `Related:` edge that lacks its
  exact inverse** — `severity: error`, rule `missing-inverse`, exit
  code 2. The six recognized verbs and their inverses are pinned in
  `convention.md` › *Reciprocal relationship verbs*:
  `precedes`↔`follows`, `depends-on`↔`required-by`,
  `blocks`↔`blocked-by`. Verb matching is **case-sensitive exact
  match** (`Precedes:` is a free-form verb, not a recognized one).
- (M27 — D4) A **local Markdown body link whose destination names no
  existing path inside the tree** — `severity: error`, rule
  `broken-body-link`, exit code 2, one finding per occurrence. See
  *Markdown body-link validation* below.
- (M27 — D4b) A **local Markdown body link whose destination leaves the
  docs root** — `severity: error`, rule `outside-root-body-link`, exit
  code 2, one finding per occurrence, decided by path arithmetic alone
  with no filesystem access outside the root. See *Markdown body-link
  validation* below.

Output is grouped by file; one line per finding. `--json` emits an array of records, one per finding. Schema — **stable from M3 onward**:

| Field | Type | Notes |
|---|---|---|
| `path` | string | Root-relative POSIX path of the doc. |
| `severity` | string | `error` or `warning`. |
| `rule` | string | Stable rule id: `missing-field`, `bad-vocab`, `bad-date`, `malformed`, `status-drift`, `broken-ref`, `stale`, `medium-confidence-inference` (M7), `unknown-field` (M10), `duplicate-field` (M25), `missing-inverse` (M25), `broken-body-link` (M27), or `outside-root-body-link` (M27). |
| `message` | string | Human-readable description of the finding. |

The record's **key set is closed** and unchanged by M25 or M27:
`missing-inverse`, `broken-body-link`, and `outside-root-body-link` each add
**no** new JSON field. Everything an agent needs to repair the edge — source,
verb, target, and the exact missing inverse — is carried in `message`, and
everything it needs to repair a body link — the 1-based line, the raw
destination as written, and the path the destination normalises to — is
carried there too. A new rule adds a value to `rule`, never a field to the
record.

Exit codes:
- 0 — clean.
- 1 — warnings only (stale docs; medium-confidence inferences; unknown-field warnings).
- 2 — errors (missing required fields, invalid vocab, malformed structure, lifecycle/location drift, broken refs, duplicate metadata labels, missing inverses, broken body links, body links that leave the docs root).

**Duplicate metadata labels (M25 — D7).** A metadata label may appear
**at most once** per document. Repeatability lives in the **bullets** under
a bare label — `Related:` and `Revision:` are repeatable in exactly that
way — never in a second copy of the label itself. A repeated label is an
error, rule `duplicate-field`, exit code 2, attached to the offending doc,
**one finding per repeated label** (a label appearing three times still
yields one finding). The message names the label and states what the parser
does with it:

```
metadata field 'Related:' appears 2 times; only the last occurrence is read
```

This is a **data-loss** rule, not a tidiness rule. The metadata parser
builds a dict, so a second `Related:` label silently **replaces** the first
— every bullet under the earlier label is discarded before any other rule,
the INDEX renderer, or `Related:`-resolution ever sees it. Nothing else in
`docs check` can surface that, precisely because the evidence is already
gone by the time the parsed metadata exists; the rule is therefore
evaluated against the metadata block's raw label lines.

The check is purely structural: it counts label lines inside the metadata
block and does not care whether a label is inline (`Updated:`) or bare
(`Related:`), known or unknown, or on the `add_fields` allowlist. Many
bullets under **one** label are always fine.

The repair is manual and deliberate — merge the bullets under a single
label, keeping the ones you want. `docs relate` will not do it: its editors
operate on the *first* matching label while the parser reads the *last*, so
on a duplicated tree a repair can appear to succeed and leave the finding
in place. Fixing the duplicate first makes the tree diagnosable again.

**Reciprocal-edge validation (M25 — D2).** A recognized edge
`<verb>: <target>` in a doc obliges the target doc to carry the exact
inverse edge back. The finding attaches to the **source** doc — the one
declaring the un-reciprocated edge — mirroring `broken-ref`, which blames
the referrer. The message is a single line:

```
Related: '<verb>: <target-rel>' has no inverse; <target-rel> must declare '<inverse>: <source-rel>' (or remove the edge)
```

Worked instance:

```
Related: 'precedes: m26.md' has no inverse; m26.md must declare 'follows: m25.md' (or remove the edge)
```

Both repairs are named and neither is chosen: the agent decides whether the
source edge is true (add the inverse) or wrong (remove the edge). Paths are
root-relative POSIX.

*Applicability — all six conditions must hold, else no `missing-inverse`
finding is produced:*

1. Source **and** target are both yielded by the walk under the effective
   exclusion predicate (`[exclude]` / `.docsignore` / `--exclude`).
2. The target resolves to a file under the root. If it does not,
   `broken-ref` owns the case and no inverse finding is emitted.
3. The target is a managed Markdown doc in the walked set. A recognized
   edge pointing at a non-Markdown artifact (`depends-on: data.yaml`) or
   at an excluded path yields nothing — the convention deliberately allows
   `Related:` targets that are not docs.
4. **Both** endpoint texts parse as metadata blocks. A `malformed`
   endpoint owns its own case. Reciprocity depends on metadata-block
   parseability **only** — a source that also trips `bad-vocab`,
   `bad-date`, or `status-drift` is still reciprocity-checked.
5. The target is **not the source itself**. A recognized edge whose target
   resolves to the declaring document is **exempt**: `docs check` must
   never name a repair `docs relate` refuses to perform (`relate` rejects a
   self-edge outright, see below), and a self-referential edge carries no
   navigational meaning to complete. This is the same boundary as the
   milestone's "no cycle or conflict detection" non-goal.
6. The inverse bullet is genuinely absent from the target.

**Path matching is normalized, not textual.** Both the source's edge target
and each candidate inverse bullet in the target doc are resolved to their
**canonical root-relative POSIX** form before comparison — the same
resolution `broken-ref` already performs via `(root / target)`. So
`precedes: ./b.md`, `precedes: sub/../b.md`, and `precedes: b.md` are the
same edge, and an inverse written as `follows: ./a.md` satisfies
`precedes: b.md` just as `follows: a.md` does. A genuinely reciprocal tree
must not fail `docs check` over a `./` prefix. (Note the finding's message
still quotes the **canonical** form of both edges, so the repair it names is
the one `docs relate` would write.)

Archived endpoints **are** in scope: they are walked, so archived↔active
and archived↔archived one-sided edges are hard errors. `docs relate`'s
audited archive exception exists precisely so these are repairable.

Exactly **one** finding is emitted per distinct `(source, verb, target)`
triple — compared on the canonical target path — even when the source
repeats the bullet. There is **no** cycle detection and **no** conflict
detection: a doc may declare both `precedes: b.md` and `follows: b.md` and,
if `b.md` reciprocates both, the tree is clean.

There is **no opt-out knob** for this rule — no `[check] reciprocal =
false`. Missing inverses are errors, not compatibility warnings.
`--exclude` / `.docsignore` remain the only (coarse) escape.

**Upgrading from 1.x.** A tree that predates M25 may carry one-sided
recognized edges and will begin failing `docs check` after the upgrade. No
automatic conversion occurs. The most likely legacy offender is a bare
`blocked-by:` — pre-M25 `convention.md` recommended pairing
`Lifecycle: blocked` with a one-sided `Related: blocked-by: …`, and that
recommendation is withdrawn in M25. The repair loop is:

```sh
docs check                                  # read the missing-inverse findings
docs relate add blocked.md blocked-by upstream.md      # the edge is true → complete it
docs relate remove blocked.md blocked-by upstream.md   # the edge is stale → drop it
docs check                                  # clean
```

When either endpoint is archived, the same commands need `--reason` (see
`docs relate` below).

#### Markdown body-link validation (M27 — D1–D4b)

From M27 `docs check` also reads the **body** of every walked document and
validates the local Markdown links it finds there. Two rules come out of it —
`broken-body-link` and `outside-root-body-link` — and both are hard errors
(exit 2). They are emitted **immediately after** the document's `broken-ref`
group, keeping the two reference-resolution rules adjacent, and within that
block in source order (line, then column).

`docs touch --check` inherits both rules: it runs the same `check_tree` over
the same root. There is **no new flag, no new verb, and no opt-out knob** —
no `[check] body_links = false`. A missing file is a fact, not a style
preference.

**What is scanned.** Every document `docs check` walks, in full — the raw
text of the file, metadata block included, not just the prose after it. A
`Related:` bullet cannot be link-shaped, so scanning the whole text costs
nothing and gives M28 a single offset base. Two exclusions:

- **The root-level generated `INDEX.md` is never scanned.** The walk already
  skips it for every rule, and its links are regenerated from the tree rather
  than authored. This is stated here rather than left as an accident of the
  walker. A **nested** `INDEX.md` (one inside a subdirectory, e.g. an adopted
  tree's own per-folder index) is an ordinary document and **is** scanned —
  `convention.md` › *INDEX file* already scopes the special case to the file
  at the docs root.
- **A `malformed` document is never body-link checked.** The existing early
  return on a missing H1 stands, so a document with no H1 gets its `malformed`
  finding and no body-link pile-on — mirroring how reciprocity validation
  skips unparseable documents.

##### The supported grammar (M27 — D1)

The scanner recognises a **deliberately bounded, CommonMark-*shaped* subset**.
It is not a CommonMark parser and this spec claims no conformance; what it
recognises is exactly the table below and nothing else.

| Form | Example | Recognised |
|---|---|---|
| Inline link, plain destination | `[label](plan.md)` | **yes** — `kind: "inline"` |
| Inline link, angle destination | `[label](<my plan.md>)` | **yes** — `kind: "inline"` |
| Inline link with a title | `[label](plan.md "The plan")` | **yes** (`"…"`, `'…'`, `(…)`) |
| Reference definition | `[plan]: plan.md "The plan"` | **yes** — `kind: "reference-definition"`, 0–3 leading spaces, line-anchored |
| Shortcut / collapsed / full reference **use** | `[plan]`, `[plan][]`, `[x][plan]` | **no** — a use carries no destination; the *definition* is what gets validated |
| Image | `![diagram](d.png)` | **no** (M27 — Q2, a scoped exclusion) |
| Autolink | `<https://x>`, `<plan.md>` | **no** |
| Raw HTML | `<a href="plan.md">` | **no** |

Exactness, pinned rather than implied:

1. **Label.** Opens at an unescaped `[` and ends at the **first unescaped
   `]`**. It may span newlines but **never a blank line** — the scan for the
   closing `]` is bounded at the first blank line. The label is never
   validated and never resolved. Balanced brackets *inside* a label
   (`[a [b] c](x.md)`) are **not** supported: the label ends at that first
   `]`, so the span is not a recognised link. Escape the inner brackets to
   write one.

   A **blank line** is a line whose content is whitespace-only (CommonMark),
   and that first blank line bounds the **whole candidate** — label,
   destination and title alike, not just the label. Phase 1 stated the bound
   only for the label scan, which left the destination parser free to run to
   the end of the document on an unterminated candidate; one bound for the
   whole candidate is what keeps the scanner linear.
2. **Image exclusion.** An otherwise-recognised inline link whose `[` is
   immediately preceded by an unescaped `!` is an image and is skipped. What
   is skipped is the **image**, not whatever its label contains: in
   `![a [b](c.md)](d.png)` the inner `[` is preceded by a space, so
   `[b](c.md)` is an ordinary recognised link and **is** reported. Stated
   because the scanner's natural resume-after-a-failed-candidate step would
   swallow it, and a span M27 cannot see is a destination M28 will never
   rewrite.

   **A nested image consumes one `]` — an amendment to rule 1.** An image
   inside a label carries its own `]`, so rule 1's "first unescaped `]`" is
   not the label's own: a label ends at the first unescaped `]` **that is not
   the closer of an image opened inside it**, one skipped `]` per unescaped
   `![`. Without this, `[![diagram](diagram.png)](full-size.md)` — the
   ordinary badge / thumbnail idiom — ends its label at the image's `]`,
   which makes `(diagram.png)` the destination. That is wrong twice over: it
   reports **the image** as `broken-body-link`, contradicting both "images …
   produce no finding" and Q2's decision that a broken image deserves its own
   wording rather than being folded into this rule; and it never emits
   `full-size.md` at all, so M28 would never rewrite the real destination.
   The rule stays bounded — the exception applies only to `![`, so
   `[a [b] c](x.md)` is still not a recognised link.
3. **Plain destination.** Optional whitespace is permitted on **both** sides of
   the destination — between the `(` and the destination, and between the
   destination (or its title) and the closing `)`. So `[a]( plan.md)`,
   `[a](plan.md )`, and `[a](plan.md "T" )` are all recognised links, and none
   of that whitespace is part of the destination token. The destination itself
   begins at the first non-whitespace character after the `(` and ends at the
   first **unescaped whitespace** or at an unescaped `)` at nesting depth 0.
   Unescaped `(` and `)` inside it nest; the destination is recognised only
   when they are **balanced** and never nest deeper than
   `MAX_DESTINATION_PAREN_DEPTH = 3`. Beyond that depth, or left unbalanced,
   the span is not a recognised link. A newline is whitespace, so a plain
   destination never spans lines.

   Two points Phase 1 left silent, settled because they change what
   `scan_body_links` hands M28 even where no finding moves. **A newline is
   ordinary whitespace on both sides of the destination**, so a destination
   written on its own line between the `(` and the `)` is a recognised link —
   the candidate is bounded by rule 1's blank line, not by the line the `(`
   opened on. And an **empty inline destination is recognised**: `[a]()` is a
   link whose destination token is **zero-width**, positioned at the first
   non-whitespace character after the `(`, classified `empty` and therefore
   silent. That has to be said, because rule 6 disqualifies the empty
   *reference-definition* form as an explicit exception — which only reads as
   an exception if the inline form is recognised — and the classification
   table below already gives `[a]()` as its `empty` example.
4. **Angle destination.** `<…>`: whitespace is allowed inside, a literal `>`
   must be backslash-escaped, and a newline inside the brackets terminates the
   candidate (not a link). The **angle brackets are part of the destination
   token** — see *The destination-token span* below.
5. **Title.** After at least one whitespace character following the
   destination: `"…"`, `'…'`, or `(…)`. An unterminated title means the span
   is **not** a recognised link. The title is never part of the destination
   token and is never validated. **Whitespace is what disambiguates**:
   `[a](foo(bar).md)` is a balanced-paren destination, `[a](foo.md (title))`
   is a destination plus a parenthesised title. Between the destination and
   the closing `)` only whitespace and at most one title may appear (per
   rule 3, trailing whitespace is fine); any **non-whitespace, non-title**
   content there means the span is not a recognised link, so
   `[a](plan.md extra)` is prose. A title stays inside rule 1's blank-line
   bound like the rest of the candidate, and the `(…)` form is scanned to its
   **first unescaped `)` with no nesting** — the simplest rule that keeps this
   whitespace-based disambiguation honest, and one Phase 1 did not state.

   The "at least one whitespace character" is **load-bearing and easy to
   miss**, because only an *angle* destination can reach it: a plain
   destination ends *at* whitespace or at the closing `)`, so `[a](plan.md"T")`
   is just a destination spelled `plan.md"T"`. After `<…>` the clause bites —
   `[a](<x.md>"T")` and `[plan]: <x.md>"T"` are **not** recognised links,
   while `[a](<x.md> "T")` is. Spelled out because the difference is invisible
   in the finding set and visible only in what the scanner hands M28.
6. **Reference definition.** Line-anchored: 0–3 leading spaces, `[label]:`,
   optional whitespace, the destination, then an optional title to end of
   line. The destination is the same plain-or-angle token as in an inline
   link, except that there is no enclosing `)` to close it: a plain
   destination here ends at the first unescaped whitespace or at the end of
   the line. Three points are settled rather than left to the implementation,
   because `scan_body_links`' output is M28's handoff and they change it even
   where the finding set is unchanged:
   - the destination must **begin on the same line as the label**. The
     "optional whitespace" above never spans a newline, so a definition whose
     destination sits on the following line is not recognised. The rule stays
     line-anchored end to end and the scanner stays bounded.
   - a **trailing non-title remainder disqualifies** the definition, exactly
     as in rule 5 for the inline form: after the destination only whitespace
     and at most one title may appear before the end of the line, so
     `[plan]: plan.md and more` is prose.
   - an **empty destination is not a recognised reference definition** at all
     — `[plan]:` with nothing after it yields no `BodyLink`, rather than a
     `BodyLink` with an empty `raw`.

   "Line-anchored end to end" means the **label itself opens and closes on one
   line** as well: a `[label]:` whose `]` sits on a later line is not a
   definition. And an unescaped `)` at nesting depth 0 terminates a
   reference-definition destination exactly as it terminates an inline one —
   it is "the same plain-or-angle token" — after which rule 6's
   trailing-remainder clause disqualifies the definition. Both were left
   implicit in Phase 1 and both are settled here, because they are M28's
   input.

   `kind` is `"reference-definition"`; both rules and both message
   templates are otherwise identical — the kind lives on the scanner's record,
   never in the finding.
7. **Backslash escapes.** A `\` followed by any ASCII punctuation character
   **or a space** yields that character literally; a `\` before anything else
   is a literal backslash. The space leg follows from rule 3 (a destination
   ends at the first *unescaped* whitespace). An escape therefore always lets
   an author opt a span out: `\[x](y.md)` is not a link.
8. **Percent-escapes.** Decoded before resolution, invalid sequences passing
   through unchanged. The **raw** spelling is what the finding reports.
9. **Fragments.** The destination is split on the **first** `#`; the left side
   is the path, the right side is the fragment. The fragment is preserved and
   **never validated** — `docs check` does not check whether the heading
   exists.

**Order of operations on a destination token — BINDING.** Strip a surrounding
`<…>` pair → split on the first `#` → backslash-unescape → percent-decode →
join to the referring document's directory → normalise. Three consequences
follow from that order and are stated so they are specified rather than
emergent:

- a percent-encoded `%23` is **not** a fragment delimiter (the split already
  happened), while a percent-encoded `%2F` **is** a path separator;
- a backslash cannot escape a `#` out of being the fragment delimiter, for the
  same reason — the split precedes unescaping;
- the fragment is carried **verbatim**, neither unescaped nor decoded, because
  nothing ever resolves it.

##### The destination-token span (M27 — D5)

Each recognised occurrence is recorded with the exact character offsets of its
**destination token** in the *original* document text, alongside the 1-based
line and column of that token's first character. Two properties are frozen
here because **M28** — which rewrites destinations when a document moves —
depends on them, and because they are what stops this project ever growing a
second Markdown parser:

- **`raw` is reported; the decoded path is resolved.** The finding always
  names the destination exactly as written; resolution happens on the
  unescaped, decoded, fragment-stripped path.
- **The span is exactly the destination token** — `text[start:end] == raw`.
  It **includes** the `<…>` angle brackets when the destination has them and
  **excludes** any title. Splicing a replacement into that span and copying
  every other byte is how a rewrite preserves labels, titles, quoting form,
  fragments, and surrounding prose.

M27 itself writes nothing. Validation is read-only; the rewrite is M28's
milestone.

##### What the scanner never sees (M27 — D2)

Before any matching, the document text passes through a **length-preserving**
mask that replaces the *contents* of code with spaces:

- **fenced code blocks** — ``` and `~~~`, 3+ markers, 0–3 leading spaces,
  closed by a fence of the **same character** and **equal or greater** length
  with **only whitespace after the marker** (CommonMark — a marker followed by
  an info string opens, it never closes). A fence line is **never treated as
  the block's content**: the marker and its info string survive this pass
  intact, and only the lines between the fences are blanked. (Being an
  ordinary line thereafter, a fence line still goes through the inline-span
  pass below — the two passes are ordered, not scoped — and its **info string
  is ordinary text that IS scanned**, so a link written there is recognised
  like any other. Surviving pass 1 means "not the block's content", never "not
  prose".) An **unclosed** fence masks to the **end of the document**,
  matching CommonMark;
- **inline code spans** — matched backtick runs of equal length. An inline
  span **never crosses a line boundary**, so one unpaired backtick cannot mask
  the rest of a document.

**The order is part of the contract:** fences are masked first (line-based),
then inline spans over the already-masked text, so a stray backtick inside a
fenced block cannot open a phantom span.

**The two unterminated cases deliberately differ, and the reason is what a
reader actually sees.** The masker's job is to model what renders as a link,
not to be maximally cautious: every renderer these documents pass through
takes an unclosed fence to the end of the file, so reporting a "broken link"
inside one would flag something no reader ever sees as a link — a false
positive of exactly the kind M27 exists to avoid. A lone backtick is the
opposite case: it is a common, invisible accident in ordinary prose, so
letting it mask the remainder of a 112 KB document would buy unbounded false
*negatives*. An unclosed fence is rare, line-anchored, three or more
characters wide and visually obvious; bounding the damage is warranted for one
and not the other.

**Nothing else is code.** In particular there is **no 4-space
indented-code rule** (M27 — Q3): a link indented four spaces inside a
blockquote or a list continuation is a real link and **is** scanned. The
author-facing consequence is a `convention.md` rule — *fence code samples that
contain link syntax* — plus the backslash escape as an always-available
opt-out.

**Length preservation is a guarantee, not an implementation detail.** The mask
has the same length as the input and a newline at every offset the input has
one, so every character offset the scanner reports is an offset into the
**original** text. That is what makes the span contract above usable by M28.

##### Destination classification (M27 — D2)

Every recognised destination is classified before any resolution happens.
Only `local` destinations are ever resolved or reported; the other five kinds
produce **no finding of any kind, ever**.

| Kind | Test (on the token, angle brackets stripped) | Example |
|---|---|---|
| `empty` | the destination is the empty string | `[a]()` |
| `fragment` | starts with `#` | `[a](#section)` |
| `protocol-relative` | starts with `//` | `[a](//host/x)` |
| `root-absolute` | starts with `/` | `[a](/path.md)` |
| `scheme` | matches `^[A-Za-z][A-Za-z0-9+.-]*:` (case-insensitive) | `[a](https://x)`, `[a](mailto:x@y)` |
| `local` | anything else | `[a](plan.md)` |

The tests run in that order, so `//host/x` is `protocol-relative` rather than
`root-absolute`. A **root-absolute** destination names a web-server root, not
a filesystem path, and is out of scope for a tree-relative tool. Note that a
Windows-style `C:\docs\plan.md` is **scheme**-shaped and therefore silent —
deliberate, and stated so it is not mistaken for a gap.

Classification runs on the token **as written**: escapes are not decoded
first, so a percent-encoded `%23` at the front does not make a destination
fragment-only.

##### Resolution and containment (M27 — D3 / D4b)

A body-link destination is resolved **from the directory of the document that
contains it** — the single most important difference from a `Related:` target,
which is root-relative. `../` is therefore normal and expected in a body link
and never appears in a `Related:` bullet.

The containment test is **pure path arithmetic**, POSIX on every platform, in
this fixed order, with **no filesystem access at all**:

1. take the referring document's root-relative POSIX path and drop its last
   segment, giving the document's directory (empty for a root-level doc);
2. join the unescaped, decoded destination path to it and normalise it
   lexically — `..` segments are collapsed textually, symlinks are not
   followed and `resolve()` is never called;
3. the destination is **contained** when the result is neither `..`, nor
   prefixed by `../`, nor **absolute** (prefixed by `/`).

The absolute leg is not redundant with the `root-absolute` classification
above, and the Step-2 audit found it the hard way. Classification runs on the
token **as written**, so `%2Fetc/passwd` and `\/etc/passwd` are `local`, not
`root-absolute`; the BINDING decode order then turns both into
`/etc/passwd`, and joining an absolute path to a directory yields the
absolute path. Without this leg such a destination reads as contained and
gets **stat'd outside the docs root** — precisely what the boundary below
forbids. Both are now reported as `outside-root-body-link`, while a slash the
author wrote *literally* is still silenced one step earlier, by
classification. The predicate is therefore byte-for-byte the one
`docs archive` uses for its own `outside-root` ineligibility.

Three cases the contract answers outright:

- **Escape-then-return.** `../sub/../back-inside.md` from `sub/deep.md`
  normalises back under the root, so it is **contained** and validated
  normally. The verdict is a function of two strings and cannot vary with
  filesystem state.
- **Symlinks.** `Path.resolve()` is **not** used. This deliberately differs
  from the `resolve()`-based test `docs check` uses to decide whether a file
  sits in the archive subtree: that test asks *where does this file physically
  live*, and this one asks *what did the author write*. Following links would
  let filesystem layout decide whether a rule fires, and could push an in-root
  destination out or the reverse.
- **The root itself.** `sub/..` normalises to `.`, which is contained and,
  being an existing directory, satisfied. `.` therefore never appears in
  either message.

**Any existing filesystem entry satisfies a contained destination** — file
**or directory**, any extension (M27 — Q7). `convention.md` already states
that non-Markdown files may be referenced from prose and that `Related:`
checks existence regardless of extension; body links inherit that, and a link
to a directory is a legitimate Markdown link. `[exclude]` / `.docsignore` /
`--exclude` govern which documents are **walked**, never what a destination
may point at, so a link to an excluded-but-existing file resolves. Existence
is tested with `Path.exists()`, which **follows symlinks**, so a link to a
symlink inside the root whose target is missing is `broken-body-link` — the
destination really is unreachable from the reader's point of view, and that is
what the rule is for. (This is existence, not containment: containment stays
purely lexical and follows nothing, per the *Symlinks* case above.)

**The out-of-root boundary is specified behaviour, not an implementation
detail.** `docs check` never stats, opens, or follows a **destination** that
leaves the docs root. The boundary is drawn around what the *author wrote*:
a destination whose lexical form escapes is reported without being probed. It
is not a claim that no syscall ever names a path outside the root — a symlink
**inside** the tree is part of the tree, and the existence probe follows it
exactly as the walk already follows a directory symlink, so `[a](link/x.md)`
where `link` is an in-tree symlink resolves through it. Both halves are
deliberate: containment is lexical so the *verdict* cannot vary with
filesystem layout, and existence follows links so the verdict matches what a
reader can actually reach. A check has to be a **function of the tree alone**: a destination
that resolves only because of what happens to sit beside the checkout would
give one verdict in a git clone, another in a container, and a third in a
vendored subtree — and a result that varies with the tree's surroundings
cannot gate CI. So an escaping destination is detected by path arithmetic and
**reported**, never probed. Whether its target exists is deliberately not
knowable to `docs check`. Checking the same bytes from a different location
yields the identical result.

##### Evaluation order — BINDING (M27 — D4b)

The containment test runs **before** the existence test, so the two rules
never double-report. Per link occurrence, in this order:

```
1. classify the destination   → not `local`?   → silence, stop
2. containment (lexical only) → escapes?       → outside-root-body-link, stop
3. existence (inside the root) → missing?      → broken-body-link
```

A destination that leaves the root yields `outside-root-body-link` **only**
and is *never* additionally reported as `broken-body-link` — deciding whether
it is broken would require precisely the stat the boundary forbids. This is a
fixed evaluation order, not an artefact of the order two conditions happen to
be written in.

##### The two findings (M27 — D4 / D4b)

Both are `severity: error`, exit code **2**, **one finding per occurrence**
(three broken `[x](plan.md)` links on three lines are three repairs), and
attached to the **referring** document — blaming the referrer, exactly as
`broken-ref` and `missing-inverse` do. Both message templates are single
lines and both are frozen:

```
body link at line <N> does not resolve to an existing path: <raw> (resolves to <candidate>)
body link at line <N> leaves the docs root: <raw> (normalises to <candidate>); links outside the tree must be URLs
```

Worked instances:

```
body link at line 12 does not resolve to an existing path: plan.md (resolves to archive/2026-01-01/plan.md)
body link at line 52 leaves the docs root: ../shared/glossary.md (normalises to ../shared/glossary.md); links outside the tree must be URLs
```

- `<N>` is the **1-based line** of the destination token's first character.
- `<raw>` is the destination token **exactly as written** — angle brackets,
  percent-escapes, backslash escapes and all. The finding reports what the
  author typed, so the author can find it.
- `<candidate>` for `broken-body-link` is the canonical **root-relative**
  POSIX path the destination normalises to; for `outside-root-body-link` it is
  the lexically normalised path that leaves the tree — `../`-prefixed for the
  ordinary case, absolute for a destination that *decodes* to a leading slash.
  It is printed **unconditionally**, even when it is identical to `<raw>` —
  there is no "it depends" cell.

The rule ids are `broken-body-link` and `outside-root-body-link`. The second
reuses the `outside-root` token `docs archive` already uses for exactly this
condition, so the tool has one name for one idea, and shares the `-body-link`
suffix so the pair reads as a family.

##### Upgrading from 1.x

A tree that has carried unnoticed prose damage starts failing `docs check`.
That is deliberate, and it is what the 2.0 major version exists to carry. No
automatic conversion occurs and there is **no repair verb** — `docs` will not
guess whether a link should be rebased, repointed, or deleted.

The overwhelmingly common cause of `broken-body-link` is a relative link in a
document an **older `docs` archived**: the destination was correct at the
document's original location and no version of the tool has ever rebased it,
so it now needs the `../../` that the move into `archive/YYYY-MM-DD/` should
have added. The fix for `outside-root-body-link` is different in kind: the
destination names something the tree does not own, so it becomes a **URL**.

```sh
docs check                # read the findings: line, raw destination, candidate
                          # broken-body-link  → rebase the destination
                          # outside-root-body-link → replace it with a URL
docs check                # clean
```

**Stale-window resolution (M19 — D2).** The stale window the `stale` rule
applies is resolved as **CLI `--stale` > `[check] stale_days` > unset**:

- An explicit CLI `--stale N` always wins — including `--stale 0`, which is
  honoured as given (flag every active doc not updated *today*), not treated
  as "unset".
- When `--stale` is absent and the docs root's `.docs.toml` carries a
  `[check] stale_days = N` (see `convention.md` › *Per-tree `[check]`
  config*), that value supplies the window. A configured `stale_days`
  therefore makes **bare `docs check`** (with no `--stale` flag) apply the
  stale rule — setting the key is the operator's explicit per-tree opt-in.
- When neither is present, behaviour is exactly today's: no stale window, so
  the `stale` rule never fires. Trees with no `[check]` section are
  byte-for-byte unchanged.

This resolution is shared by `docs check` and `docs touch --check`;
`docs list --stale` is **not** a consumer (see `docs list` below).

**Threshold provenance.** The `stale` finding's message names where the
threshold came from, so the operator knows which knob to turn. The
parenthetical extends as follows (the rule id `stale`, severity `warning`,
and exit code 1 are unchanged — only the message text):

- config-sourced (the window came from `[check] stale_days`):
  `(stale threshold N, set in .docs.toml [check] stale_days)`;
- CLI-sourced (the window came from `--stale N`):
  `(stale threshold N, via --stale)`.

(`docs touch --check` inherits this resolution and provenance: config-sourced
when no `--stale` is forwarded, CLI-sourced when `--stale N` is.) Internally,
a `stale_source` (`"config"` / `"cli"` / `None`) is threaded alongside the
resolved window — a small `resolve_stale(cli_stale, config.stale_days)`
helper, shared by both consumers, returns the `(window, source)` pair so the
message is assembled in one place.

### `docs touch <file>... [--check [--stale N]]`

Bump `Updated:` to today in one or more docs. Accepts one or more
positional file paths. INDEX regenerated **exactly once** at end of
batch, not once per file.

The batch is **atomic** (M10 — OQ-C). `touch` validates every input
path first — if any path is missing, isn't a regular file, or resolves
outside the resolved docs root, the command exits 1 + a named-bad-path
message on stderr and writes nothing. Otherwise every rewrite is
prepared in memory (any `MetadataError` aborts the batch before any
disk write), then `atomic_write` is run per file followed by a single
end-of-batch INDEX refresh. A failure during the validate-or-prepare
phase leaves every file byte-identical to its pre-call state.

**End-of-batch reindex honours `[exclude]` / `.docsignore` (M14 — A6).**
The single end-of-batch INDEX refresh walks the tree through the same
layered exclusion predicate `docs index` builds (persistent
`.docs.toml [exclude]` + a root `.docsignore`; `touch` has no
`--exclude` flag of its own). A file the operator has excluded — e.g. a
bundled plugin `README.md` with no metadata block, parked under an
`[exclude] dirs = [...]` directory — is therefore never read by the
reindex. Because the dates are stamped *before* the reindex, an
unfiltered walk that hit such a malformed excluded file would raise
*after* the stamps landed, leaving a partial, non-atomic result (dates
written, INDEX stale). Threading the predicate closes that gap: the
touched files' `Updated:` lines land, the INDEX refreshes **without**
the excluded file, and the command exits 0. (A malformed file that is
**not** excluded is still a hard error — the reindex maps it to exit 2,
unchanged.) This same exclude-predicate threading applies to every
end-of-batch reindex — `docs archive`, `docs mv`, and `docs project
rename` (M14 — A6, four-site).

`--dry-run` prints one `docs: would touch <path>` per file on stderr
(gated on `not --quiet`) and writes nothing. The success run prints
one `docs: touched <path>` per file on stderr (gated on `not
--quiet`).

**`--check [--stale N]` — touch-then-validate in one invocation (M19 — D1).**
`--check` folds the existing `docs check` machinery into `docs touch` so
the common post-edit loop (`docs touch <files>` → `docs index .` →
`docs check . --stale N`) collapses to a single command. When `--check`
is set, *after* `touch`'s end-of-batch INDEX refresh runs, `touch`
invokes the same **tree-wide** `check_tree` over the resolved docs root
that bare `docs check` runs — it *replaces* the `docs check .` step of
the loop, not a touched-files-only subset.

- **Combined exit code = `max(touch, check)` with a touch-fail
  short-circuit (M19 — Q1).** Touch runs first. If touch itself fails
  (exit 1 — missing/bad path; or exit 2 — outside-root refusal /
  INDEX-refresh failure) the check does **not** run and touch's code is
  returned (a failed touch left nothing meaningful to validate). If touch
  succeeds (0), the check runs and its 0/1/2 (clean / warnings-only /
  errors) becomes the command's exit code.
- **`--stale N` is forwarded to the check (M19 — Q3 / D2).** With
  `--check`, `--stale N` supplies the check's stale window; when `--stale`
  is absent, the `[check] stale_days` config default applies (see
  `docs check` below for the resolution rule). `--stale` **without**
  `--check` is a hard error — exit 2 with
  `docs: touch: --stale requires --check` on stderr; the file is left
  byte-unchanged and no reindex runs.
- **`--dry-run --check` previews the touch and checks the un-mutated tree
  (M19 — Q4).** Under `--dry-run` nothing is written and no INDEX refresh
  runs, so the check walks the **on-disk (un-mutated)** tree directly. A
  doc the dry-run *would* refresh may therefore still read as stale, since
  dry-run did not bump its `Updated:`.
- **`--quiet` gates only `touch`'s own stderr lines (M19 — Q-E).** The
  `would touch` / `touched` success/preview lines are suppressed under
  `--quiet`; the check's findings, which print on **stdout**, are **never**
  suppressed by `--quiet`.
- **The check honours the same `[exclude]` / `.docsignore` predicate as
  `touch`'s reindex (M19 — Q-F).** The tree-wide check applies the
  persistent layered exclusion predicate (`.docs.toml [exclude]` + a root
  `.docsignore`) — the same one `touch`'s end-of-batch reindex and bare
  `docs check` use. `touch` has no `--exclude` flag of its own. A malformed
  *excluded* file therefore never fails the check (just as it never fails
  the reindex).

Multi-root invocation (`docs touch a.md b.md` where `a.md` and `b.md`
resolve to different docs roots) is **undefined behaviour and out of
M10 scope** — the validate-all-first pass refuses with exit 1 + an
"outside the resolved docs root" message.

**Outside-docs-root refusal (M12 — OQ-C).** If `--root` is not given
and no `.docs.toml` exists in the cwd's ancestor chain, `docs touch`
refuses with exit 2 + stderr message
`docs: touch: <path> is not under a docs root with .docs.toml; refusing`.
The file is left unchanged and no INDEX refresh runs (avoiding the M11
cascade-crash where a downstream walk failed on the first non-managed
sibling). An explicit `--root <dir>` bypasses the refusal **only when**
`<dir>/.docs.toml` exists; if `--root` is set but its `.docs.toml` is
missing, `touch` refuses with
`docs: touch: --root <root> does not contain .docs.toml; refusing`
(exit 2) (M12 — OQ-11).

### `docs project rename <new-name>`

Rename the docs root's project (M12). Rewrites `.docs.toml`'s
`[project] name = "<old>"` to `name = "<new>"` **and** every
conformant `Project: <old>` line in every active doc, atomically, with
a single end-of-batch INDEX refresh.

```
docs project rename <new-name> [--dry-run] [--quiet] [--root DIR]
```

`<new-name>` is required. A missing positional triggers argparse's
default exit 2.

**Resolution.** Operates on the docs root resolved from cwd via the
standard upward `.docs.toml` walk, unless `--root` overrides it
(M12 — OQ-1). If the resolved root has no `.docs.toml`, exits 2 with
stderr `docs: project rename: <cwd> is not under a docs root with .docs.toml; refusing`.

**Auto-normalisation (M12 — OQ-A).** The operator-supplied `<new-name>`
is run through M7's `normalise_project_name()` (the same machinery
`docs migrate` already uses). When the normalised form differs from
the input, stderr carries one line (gated on `not --quiet`):

```
docs: project rename: normalised "<input>" to "<normalised>"
```

before the rewrite proceeds with the normalised value. The current
`.docs.toml` `[project] name` value is read **as written** for the
no-op comparison — no double-normalisation (M12 — OQ-3).

**Empty-name rejection (M12 — OQ-9).** If post-normalisation
`<new-name>` is empty or whitespace-only, refuses with exit 2 + stderr
`docs: project rename: <input> normalises to empty string; project name must be non-empty`.

**What gets rewritten** (success path):

- `.docs.toml`'s `[project] name = "<old>"` line → `name = "<new>"`.
- Every conformant `Project: <old>` line in every **active-tree** doc
  → `Project: <new>`.
- Docs that have no explicit `Project:` line implicitly resolve to the
  docs-root project; on rename, a `Project: <new>` line is inserted
  into those docs (consistent with M2's `set_metadata_field` behaviour
  for missing-field cases).
- `INDEX.md` regenerated once at end of batch.

**Multi-project tolerance (M12 — OQ-B).** A tree whose active docs
carry mixed `Project:` values (the M7-tolerated multi-project shape)
is walked completely: docs whose `Project:` matches `<old>` are
rewritten; docs with a non-matching `Project:` are reported in the
success footer but never mutated.

**Archive-subtree skip.** Docs under the configured `archive_dir` are
read-only by convention (M3); `project rename` skips them and reports
the count in the footer.

**Atomic semantics.** Validate-all-first: parse every active doc,
build the rewrite tuple + the sidecar plan; if any step in
validate-and-prepare raises, exits 1 (or 2 for a malformed
`.docs.toml`) with the offending path named on stderr and no on-disk
mutation. After validation passes, every rewrite is committed via
`atomic_write`, then `.docs.toml` is rewritten, then `INDEX.md` is
refreshed exactly once. That end-of-batch refresh honours `[exclude]` /
`.docsignore` (M14 — A6) — a malformed *excluded* file never fails the
reindex (same exclude-predicate threading as `docs touch`).

**`--dry-run`.** Prints one `docs: would rewrite Project: in <rel-path>`
line per matching doc, plus
`docs: would rewrite [project] name in .docs.toml: "<old>" -> "<new>"`,
plus the footer. Exits 0; writes nothing.

**No-op.** When the normalised `<new-name>` equals the sidecar's
current `[project] name`, the verb is a no-op regardless of whether
the active tree carries non-matching `Project:` docs (the rename has
nothing to rewrite — non-matching docs hold a different project name
and remain untouched). Prints (gated on `not --quiet`):

```
docs: project rename: <new> already current — no rewrites needed
```

to stderr; exits 0; no disk mutation; no INDEX refresh.

**Success output (M12 — OQ-2).** A single human-readable stderr line
(gated on `not --quiet`):

```
docs: project rename: <old> -> <new> (rewrote .docs.toml + <N> doc(s); <M> archived skipped; <K> non-matching project(s) untouched: <list>)
```

When `K == 0` **and** `M == 0`, the empty clauses are dropped to:

```
docs: project rename: <old> -> <new> (rewrote .docs.toml + <N> doc(s))
```

No `--json` mode in M12 (M12 — OQ-7).

**What does NOT change.**

- Prose markdown text mentioning the old name. Only the metadata
  `Project:` field is rewritten — never `Related:` edges (which carry
  no project signal) and never body prose. (Consistent with M2's
  `docs mv` "Related: only, not prose" stance.)
- Files outside the docs root.
- Archive-subtree docs.

**Exit codes.** 0 success / no-op / dry-run; 1 recoverable error
(e.g. a doc with no editable metadata block); 2 hard error (malformed
`.docs.toml`, no `.docs.toml` ancestor, empty post-normalised
`<new-name>`).

### `docs project set <doc>... <new-project>`

Reassign one or more docs' `Project:` field to `<new-project>` (M15 — B2,
proposal §5E). The **single-doc counterpart** to `project rename`: where
`rename` rewrites the *whole root* (`.docs.toml` `[project] name` + every
matching `Project:` line), `set` rewrites the `Project:` line of *just the
named docs* and regroups them in the INDEX. It does **not** touch
`.docs.toml`, non-named docs, or `Related:` edges.

```
docs project set <doc>... <new-project> [--new-project] [--dry-run] [--quiet] [--root DIR]
```

**Grammar.** A single `nargs="+"` positional run is split as
`*docs, <new-project>` — the **last** token is the new project name, every
earlier token is a doc path. At least **two** tokens are required: a
single-token invocation (`docs project set foo`) is ambiguous (is `foo` a doc
or a project?) and is refused with exit 2 + stderr
`docs: project set: need at least one <doc> and a <new-project>` (writes
nothing).

**Resolution.** Operates on the docs root resolved from cwd via the standard
upward `.docs.toml` walk, unless `--root` overrides it. If the resolved root
has no `.docs.toml`, exits 2 with stderr
`docs: project set: <cwd> is not under a docs root with .docs.toml; refusing`
(mirrors `project rename` / `touch` strict-root resolution — a write into an
unmanaged tree is the footgun this closes). An explicit `--root <dir>` bypasses
the up-walk **only when** `<dir>/.docs.toml` exists; otherwise refuses with
`docs: project set: --root <root> does not contain .docs.toml; refusing`
(exit 2).

**Auto-normalisation.** `<new-project>` is run through M7's
`normalise_project_name()` (same as `rename` / `migrate`). When the normalised
form differs from the input, stderr carries one line (gated on `not --quiet`):

```
docs: project set: normalised "<input>" to "<normalised>"
```

before the rewrite proceeds with the normalised value. If post-normalisation
`<new-project>` is empty or whitespace-only, refuses with exit 2 + stderr
`docs: project set: <input> normalises to empty string; project name must be non-empty`.

**Typo guard (the §5E design decision).** The way an agent silently fragments
the INDEX is a typo (`idea` vs `ideas` → two project groups). Rather than
prompt (the non-interactive invariant), `set` **refuses a `<new-project>` value
that is new to the tree** unless `--new-project` is passed. The set of known
projects is the resolved `Project:` of every **active** doc (a doc's explicit
`Project:`, or the docs-root project for a doc with none) **plus** the
`.docs.toml` `[project] name`. When the normalised value is not in that set and
`--new-project` is absent, refuses with exit 2 + stderr (the did-you-mean shape
from agent-native-invocation.md §5E):

```
docs: project set: '<value>' is not a project in this tree; refusing
  → did you mean '<closest>'? to create a new project group, pass --new-project
```

`<closest>` is the nearest known project via `difflib.get_close_matches`. The
**`→ … to create a new project group, pass --new-project` recovery hint always
prints** — only the `did you mean '<closest>'?` prefix is conditional: when no
known project is close, the prefix is dropped and the `→` line reads
`→ to create a new project group, pass --new-project`. An **existing** project
value needs no flag. Passing `--new-project` acknowledges the deliberate act of
creating a new project group and succeeds for any (non-empty, normalised)
value.

**What gets rewritten** (success path):

- Every named doc's `Project: <old>` line → `Project: <new-project>`. A doc
  with no explicit `Project:` line implicitly resolves to the docs-root
  project; on `set`, a `Project: <new-project>` line is **inserted** (M2's
  `set_metadata_field` missing-field behaviour, consistent with
  `project rename`).
- `INDEX.md` regenerated **once** at end of batch.

**What does NOT change.**

- `.docs.toml` — `set` never rewrites the `[project] name` (that is `rename`'s
  whole-root job).
- `Related:` edges — `set` changes no path, so unlike `rename` / `archive` /
  `mv` it performs **no** referring-edge rewrite. Strictly simpler than those.
- Body prose and docs not named on the command line.
- Files outside the docs root.

**Atomic semantics — validate-all-first.** Every named doc is resolved and
parsed *before* any write: if any named path is missing or malformed, or any
named doc resolves outside the docs root, the batch aborts **before any disk
mutation** and the offending path is named on stderr; every doc is left
byte-identical and no INDEX refresh runs. A missing/malformed named doc, or a
named doc that resolves **outside the resolved docs root**, exits 1 — matching
`docs touch`'s precedent that a named target outside an *already-resolved* root
is an explicit-path error, not a no-root refusal (the cross-verb exit-code
convention; see the Exit codes summary). An archived / typo / empty-name /
single-token failure exits 2. After validation passes, every rewrite is
committed via `atomic_write`, then `INDEX.md` is refreshed exactly once
(honouring `[exclude]` / `.docsignore`, M14 — A6).

**Archived target → refuse the whole batch (exit 2).** Archive-subtree docs are
read-only by convention (M3). Unlike `project rename` (which *skips + reports*
archived docs found incidentally during its tree walk), `set` operates on docs
the operator **named explicitly** — naming an archived doc is an error, not an
incidental skip. If any named doc resolves under the configured `archive_dir`,
the **whole batch** is refused with exit 2 + stderr naming the path:
`docs: project set: <path> is under the archive subtree (read-only); refusing`.
Nothing is written.

**`--dry-run`.** Prints one `docs: would rewrite Project: in <rel-path>` line
per named doc (gated on `not --quiet`); exits 0; writes nothing; no INDEX
refresh.

**No-op.** When **every** named doc already carries the normalised
`<new-project>` (the resolved value already equals the target), the verb is a
no-op: prints (gated on `not --quiet`)

```
docs: project set: <new-project> already current — no rewrites needed
```

to stderr; exits 0; no disk mutation; **no INDEX refresh**.

**Success output.** A single human-readable stderr line (gated on
`not --quiet`):

```
docs: project set: set <new-project> on <N> doc(s)
```

**Exit codes.** 0 success / no-op / dry-run; 1 a named doc is missing or
malformed, or a named doc resolves outside the docs root (validate-all-first
abort, byte-identical tree — matching `docs touch`'s "named target outside the
resolved root" precedent); 2 hard error (no `.docs.toml` ancestor or `--root`
without `.docs.toml`; a named archived doc; empty post-normalised
`<new-project>`; an unknown `<new-project>` without `--new-project`; a
single-token grammar error).

### `docs relate add|remove SOURCE VERB TARGET [--reason TEXT] [--date YYYY-MM-DD] [--json] [--dry-run] [--quiet] [--root DIR]`

Add or remove **one reciprocal relationship pair** across exactly two
documents (M25 — D3). The repair verb for the `missing-inverse` finding
above: `docs check` names the incomplete edge, the agent decides whether it
should exist, and `relate` writes (or unwrites) **both halves** as one
coordinated operation.

```
docs relate add    SOURCE VERB TARGET [--reason TEXT] [--date YYYY-MM-DD] [--json] [--dry-run] [--quiet] [--root DIR]
docs relate remove SOURCE VERB TARGET [--reason TEXT] [--date YYYY-MM-DD] [--json] [--dry-run] [--quiet] [--root DIR]
```

`relate` is a **verb namespace** with nested subverbs (`add`, `remove`),
shaped like `docs project`. It is deliberately narrow. It is **not** a
generic `Related:` editor: it edits only the six recognized verbs, only two
documents, and only one pair per invocation. It does **not** bulk-repair a
tree, does not choose add-vs-remove for you, and does not touch free-form
verbs.

**The six recognized verbs.** `VERB` must be one of:

| Forward | Inverse |
|---|---|
| `precedes` | `follows` |
| `depends-on` | `required-by` |
| `blocks` | `blocked-by` |

The map is symmetric and matched **case-sensitively**: either member of a
pair is a legal `VERB`, and `docs relate add b.md follows a.md` produces a
tree byte-identical to `docs relate add a.md precedes b.md`. Any other verb
(`pairs-with`, `child-of` / `parent-of`, `supersedes` / `superseded-by`,
`implements`, `references`, a user's own verb) is **rejected** — those stay
free-form and hand-edited, and gain no reciprocal validation:

```
docs: relate: unknown verb 'pairs-with'; expected one of: blocked-by, blocks, depends-on, follows, precedes, required-by
```

(exit 2, nothing written).

**Root resolution.** The standard upward `.docs.toml` walk from the cwd,
unless `--root` overrides it — the strict-root mutating-verb rule. No
`.docs.toml` ancestor exits 2 with
`docs: relate: <cwd> is not under a docs root with .docs.toml; refusing`;
a `--root` without one exits 2 with
`docs: relate: --root <dir> does not contain .docs.toml; refusing`.

**Endpoint resolution (M25 — OQ-A).** An **absolute** `SOURCE` / `TARGET`
is used as given. A **relative** one is resolved **root-relative first**,
falling back to **cwd-relative** only when the root-relative form is not a
file:

1. `<root>/<arg>` — if that is a file, it is the endpoint.
2. otherwise `<cwd>/<arg>` — if that is a file, it is the endpoint.
3. otherwise: not found — exit 1 with
   `docs: relate: file not found: <path>`.

An endpoint that resolves **outside** the resolved root exits 1 with
`docs: relate: <path> is outside the resolved docs root (<root>)`, and one
that does not parse exits 1 with the parser's own self-locating message,
`docs: <path>: <detail>` (the `project set` precedent). All three are
validate-all-first aborts: nothing is written and no INDEX refresh runs.

Root-relative-first matches how `Related:` paths are written on disk, so
the argument an agent copies out of a `missing-inverse` finding resolves
without translation. Both endpoints must resolve **under** the root. Every
human message and every JSON field about a **resolved** endpoint names it
by its **root-relative POSIX** form, whichever spelling was typed. A
*pre-resolution* refusal necessarily names the path it was still working
with: `file not found:` names the **root-relative candidate**
(`<root>/<arg>`, the primary interpretation) for a relative argument and
the path as given for an absolute one, and the outside-the-root refusal
names the resolved path.

**An excluded endpoint is allowed.** `relate` runs no whole-tree
pre-flight and consults no exclusion predicate when resolving its two
endpoints, so naming a doc under `[exclude]` / `.docsignore` works
normally. This is deliberate, not an oversight: an explicitly named
endpoint beats a coarse exclusion, and refusing would make the pair
unrepairable. (`docs check` still says nothing about such a pair — an
excluded doc is never walked, so the `missing-inverse` rule cannot see
it.) The end-of-run reindex continues to honour the exclusion.

`SOURCE` and `TARGET` must be different documents; a self-edge is refused
with exit 2 and
`docs: relate: SOURCE and TARGET must be different documents`.

**What gets written.** `add` ensures `SOURCE` carries `- <VERB>: <target>`
and `TARGET` carries `- <inverse>: <source>`; `remove` ensures neither is
present. Each endpoint's `Related:` group is created when absent and
dropped when it becomes empty; every other byte of the metadata block, the
H1, the body, and the file's trailing-newline state are preserved (the M2
surgical minimal-diff contract).

An existing bullet is matched on its **canonical** target, the same
normalisation the `missing-inverse` rule uses: a doc already carrying
`- precedes: ./b.md` is not given a second `- precedes: b.md` bullet, and
`relate remove … precedes b.md` drops it. Without this, `relate` would
stop being idempotent on exactly the loosely-spelled trees canonical
matching exists to tolerate. Newly written bullets always use the
canonical root-relative POSIX spelling.

**`Updated:` policy.** Every endpoint **whose bytes change** gets its
`Updated:` bumped to `--date` (default: today, rendered with the tree's
`date_format`). An endpoint that does not change is not touched at all. A
`--date` that does not parse in the tree's `date_format` exits 2 with
`docs: relate: --date: <detail>`, before anything is written.

**Idempotency.** `add` writes only the missing half — or nothing. `remove`
removes only the present half — or nothing. A fully-satisfied invocation
writes **zero bytes**: no `Updated:` bump, no `Revision:` entry, **no
INDEX refresh**, exit 0.

**Reindex.** `INDEX.md` is refreshed **exactly once**, at the end, and only
when something actually changed and `--dry-run` is absent (honouring
`[exclude]` / `.docsignore`, M14 — A6).

**No whole-tree pre-flight.** Unlike `archive` / `mv` — which rewrite
tree-wide and therefore validate the whole tree first — `relate` validates
only its **two named endpoints**. A whole-tree gate would make repair
impossible in exactly the broken tree this verb exists to repair. A
malformed *sibling* can still fail the end-of-run reindex: the repair has
already landed correctly and the run exits 2 with
`docs: INDEX refresh failed: <detail>` (the accepted `touch` /
`project set` behaviour).

#### Archived endpoints (M25 — D4)

Archive-subtree docs are read-only by convention. M25 opens a **second
narrow exception** beside M18's move-driven edge repointing: an explicitly
requested, explicitly reasoned, and permanently audited relationship
repair.

`--reason` is **required whenever either named endpoint lies under the
archive subtree**. The rule is evaluated in the validate-all-first pass,
**before** any planning, so it is predictable rather than plan-dependent:
an invocation that would be an idempotent no-op still requires `--reason`
(and still writes nothing).

```
docs: relate: archive/2026-01-01/old.md is under the archive subtree; --reason is required
```

(exit 2, nothing written.)

`--reason` must be a **single non-empty line** after stripping. A value
containing a newline is refused with exit 2 and
`docs: relate: --reason must be a single line`; a value that is empty or
whitespace-only is refused with exit 2 and
`docs: relate: --reason must not be empty`. The first is structural, not
cosmetic: a multi-line reason would terminate the metadata block and
corrupt the archived doc. The second keeps the audit record meaningful —
an empty reason is indistinguishable from no reason at all.

`--reason` is **accepted but unused** when both endpoints are active: no
`Revision:` bullet is written, and the value is still echoed in the
`--json` record's `reason` field. It is only ever *required* by the
archive rule above.

**The only bytes an archived endpoint may change** are:

1. the one recognized `Related:` bullet added or removed;
2. the `Updated:` line's value;
3. the `Revision:` group — created, or one bullet appended.

`Lifecycle: archived`, the original `Archived-reason:`, `Role:`,
`Project:`, every other `Related:` bullet, every other metadata field, the
H1, the prose body, the file's location, and its trailing-newline state
are **byte-identical**. Archived-reason keeps its original meaning: it
explains entry into the archive, never a later repair.

**`Revision:` encoding.** A repeatable bare-label bullet group at the
**end** of the metadata block (after `Related:`, separated by one blank
line — the shape the parser already accepts for multi-value groups). One
dated, single-line bullet per real mutation, describing **this document's
own** change, appended chronologically. The date is the same value written
into `Updated:` — `--date` or today, rendered in the tree's
`date_format`; the ISO spelling below is the default format, not a second
hardcoded one (two date spellings in one file would be a defect):

```markdown
Revision:
- 2026-08-11: relate add 'follows: m25-reciprocal-relationship-integrity.md'; reason: complete the M25/M26 sequence pair
- 2026-08-12: relate remove 'blocked-by: m30.md'; reason: blocker retired
```

`Revision` is a built-in always-allowed metadata label (see `docs check` ›
`unknown-field` above) and is documented in `convention.md` › *Optional
fields*.

**Audit asymmetry.** `Revision:` is appended **only to archived
endpoints**. An active endpoint receives the relationship edit and the
`Updated:` bump and nothing else — its history is the repository's. A
mixed active↔archived repair therefore writes a `Revision:` bullet to one
side only.

#### Output

**Human** (stderr, gated on `not --quiet`; refusals always print):

```
docs: relate: added 'precedes: m26.md' to m25.md
docs: relate: added 'follows: m25.md' to m26.md
docs: relate: removed 'precedes: m26.md' from m25.md
docs: relate: removed 'follows: m25.md' from m26.md
docs: relate: no change — 'precedes: m26.md' already present in m25.md
docs: relate: no change — 'follows: m25.md' already absent from m26.md
docs: relate: would add 'follows: m25.md' to m26.md
docs: relate: would remove 'follows: m25.md' from m26.md
docs: relate: recorded revision in archive/2026-01-01/old.md
docs: relate: would record revision in archive/2026-01-01/old.md
```

The last two are emitted once per archived endpoint that gains an audit
bullet — `would record …` under `--dry-run`, so a preview shows the audit
record it is about to write, not just the edge.

**`--json`** (stdout) emits **one** object — the operation plan — with an
identical shape for `--dry-run` and for a real apply, so a preview and an
apply are diffable:

```json
{
  "action": "add",
  "verb": "precedes",
  "inverse": "follows",
  "source": "m25.md",
  "target": "m26.md",
  "reason": null,
  "date": "2026-08-11",
  "dry_run": false,
  "applied": true,
  "index_refreshed": true,
  "edits": [
    {"path": "m25.md", "archived": false, "edge": "precedes: m26.md",
     "present_before": true,  "present_after": true,  "change": "unchanged",
     "updated_bumped": false, "revision_appended": false},
    {"path": "m26.md", "archived": false, "edge": "follows: m25.md",
     "present_before": false, "present_after": true,  "change": "added",
     "updated_bumped": true,  "revision_appended": false}
  ]
}
```

| Field | Type | Notes |
|---|---|---|
| `action` | string | `add` or `remove`. |
| `verb` | string | The recognized verb as typed. |
| `inverse` | string | Its inverse. |
| `source` / `target` | string | Root-relative POSIX paths. |
| `reason` | string \| null | The `--reason` value, or null. |
| `date` | string | The `Updated:` / `Revision:` date actually used. |
| `dry_run` | bool | True under `--dry-run`. |
| `applied` | bool | True iff bytes were written. False for a dry-run **and** for an idempotent no-op. |
| `index_refreshed` | bool | True iff the end-of-run reindex ran. |
| `edits` | array | Always exactly two records, **`[source, target]`** in that order. |

Each `edits` record: `path` (root-relative POSIX), `archived` (bool),
`edge` (the `<verb>: <path>` bullet body for *that* document),
`present_before` / `present_after` (bool), `change`
(`added` / `removed` / `unchanged`), `updated_bumped` (bool),
`revision_appended` (bool).

**`--dry-run`** writes nothing at all — neither endpoint, no INDEX — and
exits 0.

**No `--json` record on a coordinated-write failure.** When stage 3, 4, or
5 below refuses or fails, the run exits 2 with the stderr admission and
emits **no** JSON: the operation aborted, and after a `ROLLBACK FAILED`
the `applied` bit is genuinely undefined. An **INDEX-refresh** failure is
different — it is a *post-repair* failure with both endpoints already
written correctly — so the record **is** emitted there, with
`"applied": true, "index_refreshed": false`.

#### Coordinated-write failure contract (M25 — D5)

Five ordered stages; the first four write **nothing**:

1. **Validate all.** Root resolution; verb recognized; both endpoints
   resolve, exist, lie under the root, are distinct, and parse; the
   archived-`--reason` rule; `--reason` shape; `--date` parse.
2. **Stage.** Both complete new texts are computed in memory (pure — no
   I/O beyond the two reads).
3. **Re-validate the staged texts.** Each must itself parse. A staged text
   that would not parse aborts with exit 2 before anything is published:

   ```
   docs: relate: staged text for <rel> would not parse (<detail>); refusing before any write
   ```

   Defensive only — the editors cannot remove an H1 or otherwise break the
   block, so this is unreachable in practice. It exists so that a future
   editor bug aborts *before* publishing rather than after.
4. **Writability pre-flight.** Each *changed* endpoint is checked for write
   permission. A read-only archive refuses cleanly before any write — the
   common real failure, and one that needs no rollback:
   `docs: relate: <rel> is not writable; refusing before any write` (exit 2).
5. **Publish** in fixed order (source, then target), each via the atomic
   tmpfile+fsync+rename write. If a later write fails, every
   already-published endpoint is **rolled back** to its original text and
   the run exits 2:

   ```
   docs: relate: write failed for <rel>: <err>; rolled back <rel> — the tree is unchanged
   ```

   When it is the **first** publish that fails there is nothing to roll
   back, and the message says so rather than naming an empty list:

   ```
   docs: relate: write failed for <rel>: <err>; nothing was published — the tree is unchanged
   ```

   If the rollback itself fails, the run exits 2 with an explicit
   non-atomic admission naming the file and the edge left behind. The
   admission describes what the file **actually carries now**, which is the
   opposite way round for the two actions:

   ```
   docs: relate: write failed for <rel>: <err>; ROLLBACK FAILED for <rel> — repair manually: <rel> still carries '<edge>'
   docs: relate: write failed for <rel>: <err>; ROLLBACK FAILED for <rel> — repair manually: <rel> no longer carries '<edge>'
   ```

   (`still carries` after a failed `add` rollback, `no longer carries`
   after a failed `remove` rollback — the wrong one would hand the
   operator a factually inverted repair instruction.)

This is **best-effort staged publish + rollback**, not a filesystem-wide
transaction. Two files cannot be renamed atomically as a unit on POSIX;
the contract above is what the tool actually guarantees, stated plainly,
and it is pinned by failure injection rather than asserted. What it *does*
guarantee: `relate` never leaves a deliberate half-pair behind a handled
failure without saying so on stderr.

#### Worked upgrade example

```console
$ docs check
m25.md
  error: [missing-inverse] Related: 'precedes: m26.md' has no inverse; m26.md must declare 'follows: m25.md' (or remove the edge)
$ docs relate add m25.md precedes m26.md
docs: relate: no change — 'precedes: m26.md' already present in m25.md
docs: relate: added 'follows: m25.md' to m26.md
$ docs check
docs: no violations found
```

#### Exits

- **0** — success; idempotent no-op; `--dry-run`.
- **1** — a named endpoint is missing, malformed, or resolves outside the
  resolved root (validate-all-first abort, nothing written) — the
  cross-verb explicit-path-error convention.
- **2** — no `.docs.toml` ancestor or `--root` without one; unknown verb;
  self-edge; malformed `--date`; empty or multi-line `--reason`; an
  archived endpoint without `--reason`; an unwritable endpoint; a
  coordinated-write failure; an INDEX-refresh failure. Note the last one is
  a *post-repair* failure: the two endpoints were written correctly and the
  tree is consistent — only the generated INDEX is stale, and
  `docs index` (or fixing the malformed sibling) resolves it.

#### Non-goals

`relate` does not fold into `docs check` (`check` never writes), does not
bulk-repair, does not accept a third endpoint, does not edit free-form
verbs, and performs no cycle or conflict detection.

### `docs stamp <file>... [--role ROLE] [--project NAME] [--title "…"] [--dry-run] [--quiet] [--root DIR]`

Stamp a convention-correct metadata block onto one or more files an agent has
already written (M15 — B3). The **write-then-stamp** counterpart to
`docs new --body-from`: where `new` owns the frontmatter and appends a body,
`stamp` takes a file that *already has a body* (authored with ordinary tools)
and inserts the metadata block on top, preserving the body verbatim. It is a
**standalone top-level verb** with mutating-verb polarity (writes by default;
`--dry-run` to opt out) — it reuses the `docs migrate` metadata-block insertion
internally but is **not** routed through or aliased to `migrate` (a precise
single-file stamp, not a foreign-tree import).

```
docs stamp <file>... [--role ROLE] [--project NAME] [--title "…"] [--dry-run] [--quiet] [--root DIR]
```

**What it writes.** For each file, `stamp` inserts a metadata block via the
same `insert_metadata_block` machinery `migrate --apply` uses — placed
immediately under the H1, body preserved verbatim, with foreign metadata-shaped
lines parked under a `## Migrated metadata` body section (each label
`Migrated-`-prefixed; see `migrate`). The four required fields are filled:

- **Lifecycle:** always `draft` (a freshly-stamped doc is a draft).
- **Role:** `--role ROLE` if given, else the default `notes`. There is **no**
  H1-role inference — a file whose H1 reads like a plan still gets `notes`
  unless `--role plan` is passed. (`--role` must be in the built-in or
  configured Role vocabulary; an invalid role exits 2.)
- **Project:** `--project NAME` if given, else the docs root's configured
  `[project] name`.
- **Updated:** today (in the configured `date_format`).

**Title.** Inferred from the file's `# H1` when present. When the file has no
H1, one is synthesised as `# <title>` where `<title>` is `--title` if given,
else the filename's last path segment, title-cased (`-`/`_` as word
separators) — the same `_slug_to_title` derivation `docs new` uses. `--title`
overrides the inferred/synthesised H1.

**Idempotent re-stamp.** Re-stamping a file that already carries a valid
metadata block (all four required fields present and valid — detected by a
clean `parse()` of the file) is a **no-op bar an `Updated:` refresh**: only the
`Updated:` line is bumped to today (via `set_metadata_field`); `Lifecycle`,
`Role`, `Project`, the title, and the body are left byte-identical. Reports
(gated on `not --quiet`) that the file was already stamped:

```
docs: stamp: <path> already stamped — refreshed Updated:
```

**Strict-root resolution.** Mirrors `docs new` / `docs touch`: resolved from
cwd via the upward `.docs.toml` walk, or `--root` (which must contain
`.docs.toml`). No `.docs.toml` ancestor (and no valid `--root`) refuses with
exit 2 + stderr
`docs: stamp: <path> is not under a docs root with .docs.toml; refusing`
(or the `--root … does not contain .docs.toml; refusing` variant). The
`Project:` default reads the resolved root's `[project] name`.

**Atomic multi-file batch.** Mirrors `docs touch`: every named path is checked
to exist and resolve under the docs root *before* any write; a missing file (or
one outside the root) aborts the batch with exit 1 + a named-bad-path message,
**before any write**. Each file's stamped text is then prepared in memory and
committed via `atomic_write`, followed by a **single** end-of-batch INDEX
refresh (honouring `[exclude]` / `.docsignore`).

**`--dry-run`.** Prints one `docs: would stamp <path>` line per file (gated on
`not --quiet`); exits 0; writes nothing; no INDEX refresh.

**Success output.** One `docs: stamped <path>` line per newly-stamped file
(gated on `not --quiet`); already-stamped files report the refresh line above.

**Exit codes.** 0 success / dry-run; 1 a named file is missing or resolves
outside the docs root (validate-all-first abort, byte-identical tree); 2 hard
error (invalid `--role`; no `.docs.toml` ancestor or `--root` without
`.docs.toml`).

### `docs install-skill [--dest DIR] [--copy|--symlink] [--force] [--quiet]`

Materialise the bundled `docs` agent skill onto the host.

Synopsis. The `docs-cli` wheel carries a `docs_cli/skill/` directory (the
`SKILL.md` file plus its bundled spec references). `install-skill` copies
(or symlinks) that directory to a host-side location an agent can read.

Flags:

- `--dest DIR` — destination directory. Default: `~/.claude/skills/docs/`.
- `--copy` — copy the bundled files (default).
- `--symlink` — symlink the destination to the in-tree source directory.
  Rejected when running from a wheel install (the bundled skill lives
  under `site-packages` and a future `pip install --upgrade docs-cli`
  could replace it from under the symlink). Editable installs only.
- `--force` — overwrite a non-identical existing destination.
- `--quiet` — suppress success messages on stderr.

Destination resolution. `--dest` is the single, agent-agnostic source of
truth for where the skill lands — there is no agent auto-detection and no
per-agent default map. When `--dest` is **omitted**, resolution is
TTY-aware: on an interactive TTY the command **may** prompt for the
destination, offering `~/.claude/skills/docs/` as the default (an empty
response accepts the default); on a non-TTY (an agent), it **never** blocks
on a prompt — it silently uses the default `~/.claude/skills/docs/` and
exits 0. Passing `--dest` explicitly skips the prompt entirely.

Idempotency. If `<dest>` already exists and every bundled file matches
byte-for-byte, `install-skill` prints a no-op message and exits 0
without writing.

Refusals. Exits 2 if (a) `<dest>` exists with non-identical content
and `--force` was not supplied — the existing tree is preserved
unchanged in this case; or (b) `--symlink` was requested from a wheel
install. In both cases the message describes the recovery path
(`--force`, `--dest <DIR>`, or an editable install).

Recorded destination. On any **successful** run — a copy, a symlink, or an
already-identical no-op (all exit 0) — the resolved destination path is
recorded to a small per-user state file at
`${XDG_STATE_HOME:-~/.local/state}/docs-cli/install-skill.json` with the
schema `{"dest": "<absolute-path>"}`. Only the **path** is recorded — never
the skill's content, never a hash or a diff. Writes are **last-write-wins**
and **fail-silent**: an unwritable or uncreatable state directory-or-file
never changes the exit code or the command's output. A **refusal** (exit 2)
records nothing. The recorded path is later **replayed verbatim** by the
update-check skill-refresh hint (see [Update check](#update-check)) — it is
never inspected, stat-ed, or diffed.

Windows note. `--symlink` may require developer-mode or elevated
privileges depending on the user's Windows-side configuration; the
default `--copy` is the recommended cross-platform path.

Exit codes:

- `0` — success (copy/symlink performed, or destination already matched
  byte-for-byte and the call was a no-op).
- `2` — refusal (non-identical dest without `--force`; or `--symlink`
  from a wheel install).

### `docs migrate <dir> [--apply] [--json | --summary] [--only ambiguous] [--group-by role|confidence] [--exclude PATTERN] [--exclude-ext EXTS] [--quiet] [--date YYYY-MM-DD] [--config-project NAME]`

Adopt a non-conforming foreign directory into the convention.

> **Breaking change since 1.1 (M7).** The controlled-vocab field
> on the metadata block is now `Lifecycle:` (was `Status:` in
> v1.1 and earlier). A free-form `Status:` line on a foreign doc
> is preserved verbatim under the `## Migrated metadata` body
> section (as `Migrated-Status:`); the inserted canonical block
> writes `Lifecycle:`. See `convention.md` for the operator
> rationale.

`migrate` walks `<dir>` recursively, inspects every `.md` file, infers the
metadata the convention requires, and produces a **migration plan** — one
decision per file, every ambiguity flagged. It is **dry-run by default**: it
only reports unless `--apply` is given. (This inverts the polarity of the other
mutating verbs, which write by default and take `--dry-run` to opt out — a bulk
inference-driven rewrite of a foreign tree is exactly the operation a user must
see before it runs.)

- `<dir>` is a required **positional** argument — the foreign directory to
  migrate. `migrate` takes **no `--root`**: a foreign tree carries no
  `.docs.toml` for an up-walk to resolve against.
- `migrate` refuses a directory whose `.docs.toml` carries the
  managed-root marker sections (`[project]`, `[archive]`,
  `[vocabulary]`). M7 (OQ5) narrows this: a `.docs.toml`
  containing ONLY a `[migrate]` section is a foreign-tree
  migration sidecar (e.g. `[migrate] project_name = "foo"`) and
  is read without refusing. M8 (OQ1) widens the carve-out
  further: when `[exclude]` is present in the `.docs.toml`, the
  refusal is waived even alongside the managed markers — the
  operator's explicit signal "use migrate to triage / re-migrate
  this managed tree but skip the listed paths".
- Without `--apply`, `migrate` writes nothing — it prints the plan (human, or
  `--json`) and exits.
- With `--apply`, `migrate` inserts the inferred metadata block into each file
  atomically and performs any archive-normalising moves. After the file loop
  it also writes (or extends) the root `.docs.toml` sidecar (M10 — OQ-A): an
  absent sidecar gets a minimal `[project] name = "<resolved>"` + `[archive]
  date_format = "%Y-%m-%d"` block (no redundant `dir = "archive"`); a sidecar
  that already carries a `[migrate]` or `[exclude]` block but no `[project]`
  gets `[project]` appended at the bottom under a
  `# Added by docs migrate --apply` provenance comment header; a sidecar that
  already carries `[project]` is left untouched. After every archive-move the
  now-empty source parent directory is opportunistically removed (M10 — OQ-G;
  swallows `OSError(ENOTEMPTY)` so a non-migrating sibling survives). The
  result is a tree `docs check` accepts with no further operator action
  required.
- With `--apply --quiet` (M10 — OQ-B), the per-file plan block on stdout is
  suppressed in addition to the trailing `docs: migrated <N> file(s) …`
  success line on stderr. Empty stdout + empty stderr on a clean run. The
  dry-run plan, `--summary` output, and `--json` array are **requested
  outputs** and are NEVER suppressed — `--quiet` is scoped to chatter only.
- `--date YYYY-MM-DD` sets the archive date used when normalising
  archive-style subdirectories into `archive/<date>/`. When set, the
  flag overrides every per-file date globally (M4 semantics
  retained). When absent, M7 (F4) uses each file's own
  `Updated:` (or mtime fall-back) per file, so a tree's mixed
  archival history maps to mixed `archive/<date>/` buckets.
- `--config-project NAME` (M7 — F5) pins the project name for
  every plan record. Bypasses project-name normalisation
  (F11). The persistent equivalent is a `[migrate]
  project_name = "NAME"` entry in the tree's `.docs.toml`.
  Precedence: CLI `--config-project` > sidecar > inferred-and-
  normalised.
- `--exclude PATTERN` (M8 — F3, repeatable) skips paths matching
  `PATTERN`. Layered on top of `.docs.toml [exclude]` and a
  root `.docsignore` — see [Common: exclusion](#common-exclusion)
  below.
- `--exclude-ext EXTS` (M8 — F3, comma-separated) suppresses
  files with the listed extensions from the non-Markdown
  sibling footer (and from any exclude-predicate evaluation).
  Use to silence binaries the operator's already aware of
  (`--exclude-ext html,xlsx,odt`).

**Triage flags (M8 — F6).** For a directory with > 20 files,
the default per-file plan scrolls past usefulness. Three flags
shape the output for rapid triage:

- `--summary` swaps the verbose per-file block for one
  tabular line per file (`path<60> role<12> conf<8> notes`).
  Mutually exclusive with `--json` (argparse rejects the
  combination with `--summary: not allowed with --json`).
- `--only ambiguous` filters the per-file plan to records
  with at least one ambiguity. Composes with `--summary` and
  `--group-by`.
- `--group-by role` / `--group-by confidence` sorts the
  per-file plan. `role` groups by Role alphabetically;
  `confidence` orders `high → medium → low`.

**Plan footer (M8 — F3/F5/F6/F7).** Every dry-run plan
(default or `--summary` mode) emits a footer block AFTER the
per-file output, in this order:

1. One line per excluded prefix bucket:
   `<N> files excluded under <prefix>` (per `[exclude]` /
   `.docsignore` / `--exclude` match).
2. One line surfacing non-Markdown root-level siblings (M8
   F7): `<N> non-Markdown siblings at root not considered:
   <names>`. Suppressed entirely when the displayed list is
   empty (after `--exclude-ext` filtering).
3. Multi-project hints (M7 F5; one line per detected subdir).
4. The default summary block (four lines, tokens always
   present so an agent parser can rely on them):
   ```
   summary: <N> files; <M> ambiguous (low=<x>, medium=<y>, high=<z>)
   roles: spec=<n1> plan=<n2> ...
   confidence: high=<n> medium=<n> low=<n>
   ambiguities: notes-fallback=<n1> synthesised-h1=<n2> ...
   ```
   The four tokens — `summary:`, `roles:`, `confidence:`,
   `ambiguities:` — are stable and always appear (even on an
   empty plan: `ambiguities: none` when no file has any).

**Inference rules.** For each file `migrate` infers the four required fields:

- **Role** — multi-pass:
  1. An in-file `Role:` line carrying a built-in role wins (high
     confidence).
  2. The filename's trailing token (split on `-`/`_`/whitespace
     AND case-transition so `MyPlan` → tokens `[My, Plan]`) is
     matched against the built-in suffix map (`-spec` → `spec`,
     `-plan` → `plan`, `-adr` → `decision`, `-log` → `log`,
     `-status`, `-charter`, `-guide`, `-runbook`, `-reference`,
     and the 7 M7 additions `-implementation`, `-sketch`,
     `-outline`, `-memo`, `-brief`, `-template`, `-example`).
     Per-tree custom mappings via `.docs.toml [migrate]
     role_suffixes` extend the built-in map. A trailing token
     that is itself a built-in role (`-decision`,
     `-milestone`, …) resolves directly. (high confidence.)
  3. A trailing `_M\d+` (case-insensitive, leading zeros OK)
     resolves to `milestone` — M7 F12 (medium confidence).
  4. Stripping a non-role suffix `_v\d+` / `_Draft` / `_Ready`
     and re-trying pass 2 — M7 F10 (medium confidence).
  5. Beyond filename: the H1 trailing word (`# Foo Plan` reads
     as `plan`); a section-header pattern (`## Goal` +
     `## Scope` + `## Requirements` reads as plan; the ADR
     pattern `Context`/`Decision`/`Consequences`; the log
     pattern of ≥ 2 dated `## YYYY-MM-DD` sections); and the
     sibling-set default — files in the same immediate subdir
     when ≥ 60% of ≥ 5 same-subdir suffix-confident siblings
     share one role — M7 F1 (medium confidence).
  6. Otherwise falls back to `notes` (low confidence, flagged
     as an ambiguity).
- **Project** — the longest common prefix shared by every `.md`
  basename, trimmed back to the last `-`/`_` separator; used
  only when it is ≥ 2 characters after trimming **and** shared
  by every file. Otherwise falls back to the directory name.
  M7 (F11) then **normalises** the result to lowercase-kebab
  via OQ-B: TitleCase boundaries (`FooBar` → `foo-bar`),
  letter↔digit boundaries (`Abc5Mig` → `abc-5-mig`), SNAKE_UPPER
  (`FOO_BAR` → `foo-bar`); digit-after-digit is NOT a split
  point so `bugs-2026-01-26` survives intact. When the
  normalisation changes the value, the human plan shows
  `project: <final> (normalised from "<original>")` once at
  the top of the output. A `--config-project NAME` CLI flag or
  a `.docs.toml [migrate] project_name = "NAME"` sidecar
  short-circuits normalisation entirely (precedence: CLI >
  sidecar > inferred-and-normalised).
- **Lifecycle** (M7-renamed; was `Status` in v1.1 and earlier)
  — from an in-file `Lifecycle:` line carrying a built-in
  value, else a default: `archived` for a file under a detected
  archive-style subdirectory, `active` otherwise. An out-of-
  vocabulary in-file value is rejected (the default is used)
  and the file is flagged low-confidence. A free-form `Status:`
  prose line carries no controlled-vocab signal and is
  preserved as an extra field (see "Preserving extra metadata"
  below).
- **Updated** — from an in-file `Updated:` line that parses in
  the configured date format, else the file's mtime, normalised
  to `YYYY-MM-DD`. M7 (F4) additionally uses each file's
  resolved `Updated:` (or mtime fall-back) as the **per-file
  archive-move date** when `--date` is absent.

`migrate` inserts the metadata block immediately under the H1, preserving the
body verbatim. If the file has no H1, one is synthesised from the filename.
Pre-existing metadata-shaped lines are reconciled into the block, not
duplicated. `Lifecycle`/`Role` are always written from the built-in vocabulary,
so an applied tree passes `docs check` by construction.

**Multi-project hints (M7 — F5).** When the inferred project
name covers the parent root but an immediate subdir's `.md`
files share a distinct common filename prefix AND cover ≥ 5
files, `migrate` surfaces a single advisory hint line in the
plan footer (suppressed when `--config-project` is set):

```text
hint: subdir 'foo-tools/' looks like a separate project
(common prefix 'foo_tools_', 6 .md files). Migrate it
independently: docs migrate foo-tools/ --config-project
foo-tools
```

The hint is informational — it does not block `--apply`. The
operator chooses one of three responses: ignore (let `foo-tools/`
inherit the parent project), exclude (skip the subdir) +
re-run on it, or `--config-project foo-tools` to pin the
sub-project name.

**Preserving extra metadata.** A foreign doc may carry metadata-shaped lines
beyond the four the convention requires — an `Owner:`, a `Tags:`, a `Related:`
block, a free-form `Status:` prose line (M7 — F0), any other
`Label: value` line. The four required fields
(`Lifecycle`/`Role`/`Project`/`Updated`) are superseded by the
inferred values, but every *other* field is **preserved**, never
dropped. `migrate` parks the preserved fields in a
`## Migrated metadata` body section, placed immediately below
the canonical metadata block and above the rest of the body,
and renames each label with a `Migrated-` prefix (`Owner:` →
`Migrated-Owner:`, `Status:` → `Migrated-Status:`, `Related:` →
`Migrated-Related:`, keeping any bullet sub-items beneath it
unchanged). A foreign doc with no extra fields gets no such
section. Because the preserved fields live in the body — under
a `## ` heading — `docs check` does not validate them, so a
stale foreign `Related:` path cannot fail the applied tree's
check. The dry-run plan reports how many extra fields each
file preserves.

**Archive-move collisions.** When two foreign files with the same basename
live in different archive-style subdirectories, both normalise to the same
`archive/<date>/<basename>` destination. `migrate` flags every such file as a
low-confidence ambiguity in the dry-run plan, and `--apply` refuses the run
(exit 2) rather than silently overwriting — resolve the collision before
re-running.

Every per-file decision records a **confidence** (`high`,
`medium`, or `low`) and, when the inference is not unambiguous,
one or more **ambiguity** notes — so the plan is *complete*:
every file has either a confident decision or a flagged
question. `medium` (M7 — OQ-D) is reserved for derived signals
(post-strip, `_M\d+`, H1 trailing word, section-header pattern,
sibling-set defaulting) and carries no ambiguity by contract.

`--json` emits the plan as an array of records, one per file. Schema —
**breaking change at M7 (1.2)** — the `status` key was renamed `lifecycle`,
and `confidence` widens to a three-level vocabulary:

| Field | Type | Notes |
|---|---|---|
| `path` | string | Root-relative POSIX path of the file. |
| `role` | string | Inferred `Role:` — always a built-in role. |
| `project` | string | Inferred (and F11-normalised, unless a CLI/sidecar override is set) `Project:` value. |
| `lifecycle` | string | Inferred `Lifecycle:` — always a built-in lifecycle vocab value. (M7 — was `status` in v1.1 and earlier; renamed without alias per OQ-D.) |
| `updated` | string | Inferred `Updated:` date as ISO `YYYY-MM-DD`. |
| `confidence` | string | `high`, `medium`, or `low`. `low` iff `ambiguities` is non-empty; `medium` is reserved for derived signals (OQ-D). |
| `ambiguities` | array | Human-readable note strings; empty when `confidence` is `high` or `medium`. |
| `archive_move` | string \| null | Root-relative destination when the file is moved into `archive/<date>/`, else null. The date is per-file (file's `Updated:`/mtime) when `--date` is absent; the explicit `--date` overrides globally. |
| `synthesized_h1` | boolean | True when the file had no H1 and one is synthesised. |
| `reconciled_metadata` | boolean | True when pre-existing metadata-shaped lines are reconciled into the block. |

> The F11 `(normalised from "<original>")` annotation and F5
> multi-project hints are **human-output only** — the `--json`
> record schema is intentionally flat. An agent reading `--json`
> already has every per-record value it needs to compute its
> own multi-project candidates, so the hint surface is not
> duplicated into machine output.

Exits 2 when `<dir>` is a managed docs root (`.docs.toml` carries
`[project]`/`[archive]`/`[vocabulary]`) or does not exist; 0 on
a successful dry-run or `--apply`.

## Common: exclusion

Four of the verbs (`migrate` / `index` / `check` / `list`) walk
a tree directly. M8 (F3) introduces a single layered exclusion
surface they all consult. M14 (A6) threads the same surface into
the **end-of-batch INDEX reindex** of the four mutating verbs
(`touch` / `archive` / `mv` / `project rename`) — those consult
only the two **persistent** sources (`[exclude]` + `.docsignore`),
having no `--exclude` flag of their own. The four sources combine
**additively** — no source replaces another:

1. **`.docs.toml [exclude]`** (persistent, per-tree). Three
   keys:
   - `dirs = ["build", "generated", "node_modules"]` —
     directory-name matches at any depth.
   - `globs = ["**/*.draft.md"]` — gitignore-flavoured glob
     patterns.
   - `exts = ["html", "xlsx"]` — extension matches.
2. **`.docsignore`** at the tree root (persistent, per-tree;
   one file only — nested files are NOT consulted, per OQ-B).
   One pattern per line, gitignore-flavoured syntax (subset):
   - `# comment` and blank lines are no-ops.
   - Trailing `/` → directory match.
   - Leading `/` → root-anchored (no nested match).
   - `**` → any segments; `*` → any chunk; `?` → one char.
   - Leading `!` → re-include (last match wins).
   - Bare pattern (no `/`) → match any path segment at any
     depth.
3. **`--exclude PATTERN`** on the CLI (ephemeral, one-off,
   repeatable). Same glob syntax as `.docsignore`.
4. **`--exclude-ext EXTS`** on `migrate` (one-off, csv).
   Extension matches; also suppresses the non-Markdown
   sibling footer.

The four sources are layered before the walk; an excluded
path is never read, parsed, or considered for INDEX / check /
list / migrate output. `migrate`'s plan footer surfaces the
total excluded count per top-level dir prefix
(`5 files excluded under build/`).

## Output conventions

- Human output goes to stdout; errors and progress to stderr.
- `--json` switches stdout to machine-readable; stderr unaffected.
- Color is off when stdout is not a TTY.
- All timestamps use the docs root's configured `[archive] date_format` (default `%Y-%m-%d`).
- A best-effort PyPI update-check may emit one advisory line to stderr; it
  never touches stdout and never changes the exit code (see
  [Update check](#update-check)).

## Update check

`docs` performs a best-effort check for a newer `docs-cli` release on PyPI and,
when one exists, emits a single advisory line nudging the user — or the agent
driving the CLI — to update. This is the tool's first and only network surface;
it is **fail-silent always** and **never** alters output or exit codes. The
check runs **after** the command dispatch returns, so it never runs for
`--version` or `-h` / `--help` (those exit inside argument parsing, before the
hook is reached).

**The notice.** When a strictly-newer released version is found, `docs` writes
**one** line to **STDERR**, as the command's **last** stderr line (after the
command's own stderr), newline-terminated, **at most once per 24h**:

```
docs: update available <current> -> <latest> — run: pip install -U docs-cli
```

(an em-dash `—` between `<latest>` and `run:`, an ASCII `->` between the two
versions). A concrete example:

```
docs: update available 1.7.0 -> 1.7.1 — run: pip install -U docs-cli
```

The notice **never** appears on stdout and **never** changes the exit code —
the `main()` hook returns the command's own exit code untouched (exit codes are
a load-bearing contract; see *Exit codes (summary)*).

**Network + cache.** The check performs one HTTPS GET to
`https://pypi.org/pypi/docs-cli/json` (stdlib `urllib` only — no third-party
dependency — with a **1.0s** timeout) and compares the response's
`info.version` against the running `__version__` (the `importlib.metadata`
source of truth). State is persisted to a per-user cache at
`${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json` with **exactly three
keys**:

| Key | Type | Meaning |
|---|---|---|
| `last_check` | ISO-8601 UTC timestamp | When the network was last consulted — gates the network. |
| `latest_version` | string | The most recent PyPI version seen. |
| `last_notified` | ISO-8601 UTC timestamp | When a notice was last emitted — gates the notice. |

Two **independent 24h throttles** gate the two effects: `last_check` gates the
**network** (at most one GET per 24h), and `last_notified` gates the **notice**
(at most one line per 24h). `last_notified` advances **only when a notice is
actually emitted** — a run that warms the cache but suppresses the notice (see
the suppression matrix) advances `last_check` but **not** `last_notified`.

**Version comparison.** The comparison is a stdlib **numeric tuple-compare** on
the dot-split release segments (no `packaging` dependency — the zero-dependency
wheel is preserved), so `1.9.0` < `1.10.0` numerically (not lexically). It
**fails closed** — emits no notice — whenever either side is a pre-release, a
local version (e.g. the `0.0.0+local` fallback of an uninstalled checkout), or
otherwise unparseable. Only a **strictly-greater released** version notifies.

**Fail-silent.** Every error path degrades to **no notice, no traceback, and
byte-identical output and exit code** vs the same invocation today: offline /
DNS failure / timeout / non-200 response / malformed JSON / an unparseable
version on either side / a corrupt or malformed cache file / an unwritable or
uncreatable cache directory-or-file. The check never raises out of `main()`.

**Non-TTY inversion.** Unlike `gh` / `npm` (which gate the notice on an
interactive TTY), `docs` **shows the notice on non-TTY too**. The primary
consumer is an agent that runs non-interactively and is itself the actor who
performs the update (`pip install -U docs-cli`); gating on TTY would hide the
nudge from the one consumer who can act on it. The stream-safety the TTY rule
normally buys is instead bought by emitting only to **STDERR**, by **`--json`
suppression** (so stdout stays byte-clean), and by the **env opt-outs** below —
not by a TTY gate.

**Suppression matrix.** Each row suppresses the notice; the rows marked *check
too* additionally **skip the network call entirely**:

| Trigger | Notice | Network | Notes |
|---|---|---|---|
| `--quiet` | suppressed | **still runs** (warms the cache) | only the notice is silenced |
| `--json` (any verb in JSON mode) | suppressed | **still runs** (warms the cache) | stdout stays byte-clean JSON |
| `CI` env set (any value) | suppressed | skipped *(check too)* | never nag in CI (npm / gh precedent) |
| `DOCS_CLI_NO_UPDATE_CHECK` env set | suppressed | skipped *(check too)* | the project kill switch |
| `DO_NOT_TRACK` env set | suppressed | skipped *(check too)* | the cross-tool convention (consoledonottrack.com) |

`--quiet` and `--json` suppress **only** the notice and **still warm the cache**
(advancing `last_check`, never `last_notified`); `CI`,
`DOCS_CLI_NO_UPDATE_CHECK`, and `DO_NOT_TRACK` disable the feature outright (no
network, no notice).

A user-level **config opt-out is NOT part of v1.7.0** — the two env vars plus
the `CI` skip cover every realistic per-user opt-out (OQ-5/5a). When a future
milestone adds one it will be a user-level
`${XDG_CONFIG_HOME:-~/.config}/docs-cli/config.toml`, never `.docs.toml`
(which is per-tree, while this check is per-user).

**Skill-refresh hint.** When a skill destination has been **recorded** by a
prior `install-skill` run (see the [`install-skill`](#docs-install-skill---dest-dir---copy--symlink---force---quiet)
recorded-destination note) **and** the CLI update notice above fires, a
**second** STDERR line is appended immediately **after** the CLI line,
pointing at the recorded destination:

```
docs: refresh the agent skill at <dest> — run: docs install-skill --dest <dest> --force
```

(an em-dash `—` before `run:`, parallel to the CLI notice; `--force` is
included because a bundled-skill bump makes the installed copy differ, so a
forceless re-run would refuse.) The hint rides the CLI notice's **exact**
channel — the **same** suppression matrix and the **same** 24h
`last_notified` throttle. It has **no independent trigger or throttle**: it
is appended **only** when the CLI notice actually prints, and is silenced by
every row of the suppression matrix along with the CLI line. The recorded
path is replayed **verbatim** — there is **no** filesystem or existence
check on it (record/replay a path; never inspect the installed skill). When
**no** destination has been recorded, only the CLI line is emitted (the M21
behaviour is unchanged).

## Exit codes (summary)

| Code | Meaning |
|---|---|
| 0 | Success (or warnings-only on `check`) |
| 1 | Recoverable error (file conflict, validation warning, missing input) |
| 2 | Hard error (invalid vocab, atomic operation failure, validation errors) |

M12 / M14 / M15 / M25-specific exit-code shape:

| Verb | 0 | 1 | 2 |
|---|---|---|---|
| `project rename` | success / no-op / dry-run | doc lacks editable metadata block | malformed `.docs.toml`; no `.docs.toml` ancestor; empty post-normalised `<new-name>` |
| `project set` (M15 — B2) | success / no-op / dry-run | a named doc is missing or malformed, or a named doc resolves outside the docs root (validate-all-first abort) | no `.docs.toml` ancestor or `--root` without `.docs.toml`; a named doc under the archive subtree; empty post-normalised `<new-project>`; unknown `<new-project>` without `--new-project`; single-token grammar error |
| `stamp` (M15 — B3) | success / dry-run | a named file is missing or outside the docs root (validate-all-first abort) | invalid `--role`; no `.docs.toml` ancestor or `--root` without `.docs.toml` |
| `touch` (outside-root refusal) | — | — | no `.docs.toml` ancestor (cwd-resolved) or `--root` without `.docs.toml` |
| `new` (strict-root refusal, M14 — A2) | success / dry-run | existing file | no `.docs.toml` ancestor (cwd-resolved) or `--root` without `.docs.toml`; invalid role / slug (incl. empty final segment, M14 — A3) |
| `archive` (M12 / M14 — A4 / M26 — D2 / D4 / D5 / M28 — D4 / D6) | success | the primary is missing, does not parse, or resolves outside the resolved docs root; a plan member has no editable metadata block; the archive destination slot is already occupied; a referring doc has malformed metadata (the whole-tree pre-flight walk aborts the move) | retired `--cascade` / `--interactive`; already-archived primary; empty, comment-only, or negated `--cascade-only`; a `--cascade-only` **write** that selects nothing; intra-plan destination collision; unwritable source or destination directory; malformed `.docs.toml` or `--date`; an unreadable primary, plan member, or referring doc; an unwritable planned referrer, a stale recorded span, or two overlapping planned spans (M28 — D4); a still-active document outside the plan declaring itself `child-of` a plan member (M28 — D6, leg 1); `OSError` mid edge-rewrite (M14 — A4); the mid-execution partial-state admission; INDEX-refresh failure |
| `archive --cascade-dry-run` / `--dry-run` (M26 — D6; M28 — D6) | preview only; writes nothing (exit 0), **including** a `--cascade-only` that selected nothing, and **including** a plan whose leg-1 strand verdict it reports rather than adopts | a referring doc has malformed metadata — the preview now walks the tree, so it adopts this plan-**construction** failure (M28) | — |
| `mv` (M14 — A1 / A4; M28 — D4) | success / dry-run preview | `<old>` is not a file; collision (`<new>` exists) | malformed tree caught by the validate-all-first pre-flight (A1), since M28 **also under `--dry-run`**; an unwritable planned referrer, a stale recorded span, or two overlapping planned spans (M28 — D4); `OSError` during execution → the partial-state admission (A4); both paths outside the docs root; malformed `.docs.toml` |
| `relate add\|remove` (M25 — D3 / D4 / D5) | success / idempotent no-op / dry-run | a named endpoint is missing, malformed, or resolves outside the resolved docs root (validate-all-first abort) | no `.docs.toml` ancestor or `--root` without `.docs.toml`; unknown verb; self-edge; malformed `--date`; empty or multi-line `--reason`; an archived endpoint without `--reason`; an unwritable endpoint; coordinated-write failure; INDEX-refresh failure |

**Cross-verb exit-code convention (no-root vs outside-root).** Two distinct
"out of the tree" conditions map to *different* codes for the explicit-path
verbs (`touch`, `stamp`, `project set`, `relate`, and — since M26 — `archive`):

- **No docs root** — the cwd has no `.docs.toml` ancestor, or `--root` names a
  directory without `.docs.toml`. This is a **hard refusal → exit 2** (the
  `_resolve_*_root` strict-root refusal; nothing can be resolved).
- **A named target resolves *outside* an already-resolved root** — the root was
  found, but an explicit doc/file argument lies outside it. This is a
  **recoverable explicit-path error → exit 1** (`docs touch`'s precedent: the
  argument is wrong, not the tree).

CI integration: `docs check` returning 2 should fail the build.
