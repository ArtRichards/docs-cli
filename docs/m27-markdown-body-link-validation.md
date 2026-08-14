# M27 — Markdown body-link validation

Lifecycle: active
Role: milestone
Project: docs
Updated: 2026-08-14

Related:
- child-of: plan.md
- parent-of: m27-markdown-body-link-validation-impl.md
- implements: charter.md
- pairs-with: m27-markdown-body-link-validation-impl.md
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: test-strategy.md
- pairs-with: status.md
- references: feedback-log.md
- follows: m26-safe-archive-selection.md
- precedes: m28-move-safe-body-link-rewrites.md
- required-by: m28-move-safe-body-link-rewrites.md
- required-by: m29-pypi-publish-2-0-0.md

## Overview

- Milestone: M27 (v2.0 train)
- Title: Markdown body-link validation
- Surface: parse a deliberately bounded set of real local Markdown body links
  and make a missing destination a hard `docs check` error. This milestone
  detects damage and establishes the shared scanner; M28 owns mutation.
- Progress: **Active / Step 1 complete on `m27/phases-1-4` — Phases 1–4
  done (2026-08-14).** M26 is implementation-complete and merged to `main` (`393fb53`), so this is the
  next implementation milestone. **All seven setup
  questions are RESOLVED** — Q1, Q2, and Q5 by the operator; Q3, Q4, Q6, and
  Q7 conductor-resolved — and are recorded in *Resolved setup questions
  (Q1–Q7, BINDING)* below. **Q5 was resolved against the setup
  recommendation**: a destination resolving outside the docs root is skipped,
  not validated — then **amended**, so the escape is *reported* (D4b).
  Phase 1 did not re-open any of them; it froze the exact
  grammar, the masking contract, the resolution and containment rules and
  their precedence, **both** message templates, and the `BodyLink` span
  contract against them, in `cli.md`, `convention.md`, and *Decisions
  (Phase 1 — BINDING)* below. Three setup-frozen items were amended under
  conductor decision and recorded there. Phase 2 wrote the RED suite —
  **+163 test ids, zero removed** — against those frozen strings; Phase 3
  authored the six `bodylink-*` fixture trees, each yielding exactly its
  intended finding set with **no** pre-existing fixture edited. Phase 4
  captured the classified RED baseline. After the Step-1 same-instance
  audit's six fixes and the fresh-eyes review's thirteen further locks:
  **1079 collected, 137 failed, 942 passed**, zero collection errors, zero
  tracebacks, two exception classes, and **all 895** pre-existing ids
  mechanically proven present and passing (zero removed, zero regressed).
  The review found **no blockers**; its theme was that a wrong-but-plausible
  Phase-5 implementation could still pass the suite, and every gap it named
  is now locked. Phase 5 — Update Base Interfaces is next.
  The milestone stays `Lifecycle: active` until the M29 publish closeout.

### Goal

Let an agent trust `docs check` to catch both broken metadata relationships and
broken local navigation in prose, without flagging examples, code, external
URLs, or plain-text mentions.

### Primary use-case acceptance

- **Detect real damage.** After a manual edit or an upgrade, an agent runs
  `docs check` and receives an exact source location and destination for each
  real local Markdown link whose file is missing — in prose grouped by file, or
  as the existing four-key JSON record.
- **Never cry wolf.** Valid links with fragments pass without validating the
  heading; external links, code examples, images, raw HTML, and plain-text
  mentions produce nothing at all. A tree with no damage stays exit 0.
- **Upgrade deliberately.** A tree carrying pre-existing damage gets a
  documented, auditable path to clean — not a silent grandfather clause and not
  an unfixable hard failure.

## Binding scope

The seven decisions below are binding for M27. Each carries the setup question
it resolves; the reasoning for those resolutions is in *Resolved setup
questions (Q1–Q7, BINDING)*.

### D1 — The scanner recognises a named, frozen subset — never "Markdown"

M27 ships a pure, stdlib-only scanner over a **deliberately bounded grammar**,
pinned by name in `cli.md` and `convention.md`. It is a CommonMark-*shaped*
subset, and the specs say so rather than implying conformance (Q2):

| Form | Example | In v1 |
|---|---|---|
| Inline link, plain destination | `[label](plan.md)` | **yes** |
| Inline link, angle destination | `[label](<my plan.md>)` | **yes** |
| Inline link with a title | `[label](plan.md "The plan")` | **yes** (`"…"`, `'…'`, `(…)`) |
| Reference definition | `[plan]: plan.md "The plan"` | **yes** (0–3 leading spaces, line-anchored) |
| Shortcut / collapsed / full reference **use** | `[plan]`, `[plan][]`, `[x][plan]` | **no** — the *definition* carries the destination and is already validated |
| Image | `![diagram](d.png)` | **no** (Q2 — a *scoped* exclusion, see below) |
| Autolink | `<https://x>`, `<plan.md>` | **no** |
| Raw HTML | `<a href="plan.md">` | **no** |

**Images are excluded deliberately, not by oversight** (Q2). An image is the
same grammar minus the `!`, so including it would be a one-character change to
the matcher — which is precisely why the exclusion has to be a recorded
decision. Three reasons stand behind it: there are **zero** images anywhere in
this repository's documentation, its 33 fixture trees, or the bundled skill
(E8), so the rule would ship untested against real data; a broken image is a
different failure mode from broken navigation and deserves its own finding
wording rather than being folded into `broken-body-link`; and admitting images
here would widen **M28's** rewrite surface in the same stroke, since anything
M27 validates M28 must then keep valid across a move. Images are carried in
*Follow-ups recorded for later milestones* as a named candidate.

Grammar exactness is pinned, not implied:

- The destination ends at the first unescaped whitespace or the closing `)`,
  except inside `<…>` where whitespace is allowed and `>` must be escaped.
- Balanced parentheses inside a plain destination are honoured to a **fixed,
  stated nesting depth**; beyond it the span is not a recognised link.
- Backslash escapes (`\[`, `\]`, `\(`, `\)`, `\<`, `\>`) are honoured, so an
  author can always opt a span out.
- Percent-escapes are decoded (`my%20doc.md` → `my doc.md`) **before**
  filesystem resolution, and the **raw** spelling is what the finding reports.
- The label is not validated and never resolved; only the destination is.

### D2 — What the scanner never sees, and why the masking is length-preserving

Before any matching, the document text is passed through a **length-preserving**
mask that replaces the *contents* of code with spaces:

- **fenced code blocks** — ``` and `~~~`, 3+ markers, 0–3 leading spaces,
  closed by a matching or longer fence of the same character;
- **inline code spans** — matched backtick runs of equal length.

**Indented (4-space) code blocks are deliberately NOT recognised** (Q3). E6
measures the cost of the alternative: all nine 4-space-indented link-shaped
spans in this repository are **real links** inside blockquote and list
continuations, six of them among the 139 genuine breaks. An indented-code rule
would buy false negatives on live damage. `convention.md` gains the
corresponding author-facing rule: **fence code samples that contain link
syntax**, and the backslash escape is always available.

Length preservation is not a stylistic choice. Every `BodyLink` carries the
exact `(start, end)` character offsets of its **destination token** in the
*original* text; masking with equal-length spaces is what keeps those offsets
valid. That is the whole handoff to M28 (D5).

Also never a finding: an **empty** destination, a **fragment-only**
destination (`#section`), a **schemed** destination (any RFC-3986-shaped
`scheme:` prefix — `https:`, `mailto:`, `file:`), a **protocol-relative**
destination (`//host/path`), and a **root-absolute** destination (`/path`) —
which names a web-server root, not a filesystem path, and is out of scope for
a tree-relative tool.

The root-level generated `INDEX.md` is **never scanned**: `_iter_doc_texts`
already skips it for every rule, and its links are regenerated rather than
authored. This is stated in `cli.md` rather than left as an accident of the
walker.

### D3 — Resolution is relative to the referring document, not the docs root

Unlike `Related:` — whose targets are root-relative — a Markdown destination is
resolved **from the directory of the document that contains it**. `../` is
therefore normal and expected, and it is the single most important difference
between the two surfaces.

- The destination is split on the **first** `#`; the left side is the path, the
  right side is the fragment.
- The fragment is **preserved conceptually and never validated** — M27 does not
  check whether the heading exists (`feedback-log.md`, 2026-08-10).
- The path is percent- and backslash-unescaped, then joined to the referring
  document's parent and normalised.
- **A destination that leaves the docs root is never stat-ed — and is
  reported** (Q5, operator, amended). The tool does not touch the filesystem
  outside the tree it was pointed at; the escape is detected by **path
  arithmetic alone** and raised as its own finding (D4b). Not silence:
  *visibility without a stat*.
- **Any existing filesystem entry satisfies the link** — file or directory, any
  extension (Q7). `convention.md` already states that non-`.md` files may be
  referenced from prose and that `Related:` checks existence "regardless of its
  extension"; body links inherit that. Q7 applies **within** the root; Q5
  decides membership first.
- `[exclude]` / `.docsignore` / `--exclude` govern which documents are
  **walked**, not what a destination may point at. A link to an excluded but
  existing file resolves. (The M26 — Q8 shape, restated for this surface.)

**Why hermetic (Q5, the settled principle).** A check must be a function of the
tree alone. `charter.md:52` resolves today only because `docs/` happens to sit
beside `src/` in a git checkout — the identical bytes copied into a container,
vendored as a subtree, or dropped into an adopter's repository would produce a
different verdict, and a result that depends on the tree's surroundings cannot
gate CI. The codebase already draws this boundary in exactly this place:
`src/docs_cli/cli.py:5216`'s `if not primary.is_relative_to(root)` — M26's
outside-root refusal (`31bdc59`). Staying inside also keeps the contract
decidable (no symlink, `..`-escape-then-return, or case-folding questions
about foreign filesystems) and avoids billing M28 for rewrites into territory
the tool does not own.

**The under-root test is a specified behaviour, not an implementation
detail.** `cli.md` states it explicitly, so an adopter can *predict* what
happens rather than assume a destination was checked and trusted.
`convention.md` carries the matching authoring rule as an invariant (D4b).

Phase 1 must make "leaves the root" **decidable**, in this fixed order:
**(1)** join the unescaped path to the referring document's parent; **(2)**
canonicalise; **(3)** test containment under the root. Two cases are answered
in the frozen contract rather than left to the implementation:

- **`..`-escaping-then-returning** (`../docs/plan.md` from inside `docs/`).
  Judged on the **lexically** normalised path (`os.path.normpath`-style,
  collapsing `..` without touching the filesystem), so such a destination lands
  back under the root and is treated as contained. The test is then a pure
  function of two strings and cannot vary with filesystem state.
- **Symlinks.** `Path.resolve()` is **not** used for the containment test —
  following links would let filesystem layout decide whether a rule fires, and
  could push an in-root path out or the reverse. The lexical form decides the
  boundary; only a contained destination is then probed for existence. Phase 1
  must note that this deliberately differs from `check_doc`'s existing
  `resolve()`-based archive-subtree test, and say why.

### D4 — One hard finding: `broken-body-link`

- **Rule id** `broken-body-link` — distinct from `broken-ref`, which keeps
  ownership of `Related:` targets. A document can carry both; neither
  suppresses the other.
- **Severity `error`, exit code 2** (Q4). `feedback-log.md` (2026-08-10)
  records the operator decision that this is a hard error, and the v2.0 major
  version exists to carry exactly this kind of new hard failure
  (`plan.md` › *Sequencing*).
- **One finding per occurrence**, not per distinct destination: the line number
  is what makes it actionable, and three broken `[x](plan.md)` links on three
  lines are three repairs.
- **Attached to the referring document**, mirroring `broken-ref` and
  `missing-inverse` — blame the referrer.
- **Ordering is deterministic**: within a document, body-link findings follow
  the `Related:` `broken-ref` group and are emitted in source order (line, then
  column).
- **The `--json` record's key set stays closed** at
  `{path, severity, rule, message}` (Q4). `Finding`'s docstring, `cli.md`'s
  field table, and `tests/test_cli_check.py`'s
  `set(rec) == {"path", "severity", "rule", "message"}` all pin it; M25 added
  `missing-inverse` without opening it and M27 does the same. Everything an
  agent needs — 1-based line, raw destination as written, and the resolved
  candidate — is carried in `message`, in a single line frozen in Phase 1.
  The shape proposed at setup was

  ```
  body link at line <N> does not resolve to a file: <raw-dest> (resolves to <candidate>)
  ```

  and Phase 1 **amended it** — see *Decisions (Phase 1 — BINDING)* ›
  *Amendments to the setup-frozen material*. "to a file" contradicts the
  operator-binding Q7 (a **directory** also satisfies a destination), so the
  frozen form reads `does not resolve to an existing path:`. `<candidate>` is
  the contained, root-relative POSIX path the destination normalises to.
- **The rule lives in `check_doc`**, not in a second `check_tree` pass. Unlike
  `missing-inverse` it is purely per-document: it needs only the referring
  document's text and its own directory. `check_doc`'s existing early return on
  a `MetadataError` (missing H1) is kept, so a `malformed` document gets only
  its `malformed` finding and no body-link pile-on.
- **No new verb, no new flag, no opt-out knob** (Q6). The rule is always on for
  `docs check` and for `docs touch --check`, which shares the same path.

### D4b — A second finding: `outside-root-body-link` (Q5, post-draft addition)

**Operator-approved scope addition, 2026-08-14**, following the precedent M25
set with its post-freeze `duplicate-field` rule (M25 — D7): a deliberate
widening with a stated rationale, recorded as such rather than allowed to drift
in. The setup draft had Q5 skipping escaping destinations silently; that was
rejected because `charter.md:52` is a working, load-bearing link that would then
rot unnoticed. The hermetic boundary is kept and the *response* changes.

- **The invariant, stated in `convention.md`:** *a local Markdown body link
  stays inside the tree root; anything outside the tree is a URL.* It is a
  convention rule with its own rationale — a tree must be portable, and a link
  that only resolves because of what happens to sit beside the checkout is not
  portable — not an implementation note.
- **Rule id `outside-root-body-link`.** Severity `error`, exit code 2, one
  finding per occurrence, attached to the referring document, JSON key set
  **closed**, same ordering discipline as `broken-body-link`.
- **Decided by path arithmetic alone.** Join, canonicalise lexically, test
  containment. The scanner and the rule **never** stat, open, or otherwise
  touch anything outside the root — that is the whole point of the boundary.
  An escape becomes *visible* rather than *unchecked*.

**Precedence — the two rules must not double-report (BINDING).** The
containment test runs **before** the existence test. A destination that leaves
the root yields `outside-root-body-link` **only**, and is *never* additionally
reported as `broken-body-link` — deciding whether it is broken would require
precisely the stat the boundary forbids. Phase 1 states this ordering in the
contract so it is specified behaviour rather than an artefact of the order two
`if`s happen to appear in.

**Naming — settled here, alternatives recorded.** `outside-root-body-link`
reuses M26's existing machine token for exactly this condition
(`ARCHIVE_EXCLUSION_REASONS`' `outside-root`), so the codebase has one name for
one idea, and it shares the `-body-link` suffix with `broken-body-link` so the
family is greppable and reads as a pair in `cli.md`'s rule list. Rejected:
`escaping-body-link` (vivid but invents a second vocabulary for a condition
already named), `external-body-link` ("external" already means *URL* in this
project's prose, so it would read as the opposite of what it flags), and
`unrooted-body-link` (obscures that the root in question is the tree's).
Length is not a concern — `medium-confidence-inference` is longer.

### D5 — Validation is read-only; the span is the handoff to M28

M27 writes nothing. `docs mv` / `docs archive` body-link rewriting is M28's
whole milestone, and this one deliberately stops at detection so the grammar
and the resolution rules are frozen and proven before any mutation depends on
them.

The public shape M28 consumes is the `BodyLink` record — kind, 1-based line and
column, raw destination, unescaped path, fragment, and the exact
`(start, end)` offsets of the destination token in the original text. M28
splices a new destination into that span and copies every other byte, which is
how `docs mv` can preserve labels, titles, quoting form, fragments, and
unrelated prose without a second parser. Freezing that record here is a
deliverable of M27, not a convenience.

**M27 hands M28 a simplification, not a question** (Q5 as amended). Because an
escaping destination is now a *reported and forbidden* condition rather than an
unvalidated one, the convention guarantees escaping links do not exist in a
clean tree — so **M28 never has to rewrite one**, and never has to decide how to
rebase a destination pointing at territory the tool does not own. Had Q5 landed
as a silent skip, that question would have fallen to M28. It is recorded in
*Follow-ups recorded for later milestones* as a named simplification.

`BodyLink` still carries **every** local destination, in-root or not: the
scanner reports what is written, and the containment test is applied by the
**rule**, not by the scanner. That split is what lets `outside-root-body-link`
exist at all, and it keeps the scanner a pure function of the text.

### D6 — The legacy-tree policy is explicit and auditable (Q1)

**Repair, do not scope** (Q1, operator). The rule applies uniformly to every
walked document, active and archived — the same reach `broken-ref` and
`missing-inverse` already have — and this repository's 139 archived breaks are
repaired once, deliberately, as part of the milestone.

**Why uniform, and why the repair is obligatory rather than optional.** Three
facts decided it, and each is verified:

1. **This damage class is produced by docs-cli itself.** `docs archive` is a
   core verb, 8 of the 33 committed fixture trees already carry `archive/`
   directories, and 132 of the 139 breaks are a pure un-rebased `../../` — the
   move-time rebase that no version of the tool has ever performed. Adopters'
   archives are therefore where this breakage predominantly lives. A rule that
   exempted archived documents would make the tool **silent about the exact
   breakage it causes** — the least defensible possible carve-out.
2. **This tree ships to the public.** `docs/` — archive included — is inside
   every PyPI **sdist** (`[tool.hatch.build.targets.sdist] include = [… "docs"
   …]`; the wheel carries only `src/docs_cli`), and the tree is public on
   GitHub. The four worst-hit destinations — `plan.md` ×38, `status.md` ×24,
   `release-runbook.md` ×23, `cli.md` ×20 — are precisely what a prospective
   adopter reads. The broken links are a shipped artifact, not a private mess.
3. **The alternative buys nothing here.** The active tree already has zero
   breaks, so scoping the rule would leave this repository passing while the
   tool stayed blind to 139 real failures in the bytes it publishes.

The repair itself:

- **Destination tokens only, 140 occurrences in 30 documents.** 132 are a pure
  rebase (the destination already resolves from the docs root — `../../<dest>`
  from an `archive/YYYY-MM-DD/` document); 5 are a move-map lookup where the
  target itself later moved; 2 name `references/adoption-playbook.md`, which
  never lived in the docs tree and becomes its canonical GitHub URL — the
  spelling `convention.md:417` already uses for that same file; and **1** is
  `charter.md:52`, converted to the canonical GitHub URL under the identical
  treatment for the identical reason (D4b).
- **Q5 and Q1 agree, which is a good sign.** Routing the 2 adoption-playbook
  links to a URL is now *doubly* right: the relative alternative,
  `../../../src/docs_cli/skill/references/adoption-playbook.md`, would have
  been an `outside-root-body-link` violation anyway. The two decisions were
  taken independently and converge on the same spelling.
- **Audited, and the audit differs by lifecycle.** Each repaired **archived**
  document gets its `Updated:` bumped **and** a dated `Revision:` bullet naming
  the v2.0 body-link migration — the shape M25 — D4 established. `charter.md`
  is **active**, so per that same decision it gets the destination change and
  its `Updated:` bump and **nothing more**: `Revision:` is written to archived
  documents only. Nothing else changes anywhere — `Lifecycle:`,
  `Archived-reason:`, `Role:`, `Project:`, every `Related:` bullet, the H1, and
  all other prose stay byte-identical.
- **A third narrow exception, named as one.** `convention.md` currently allows
  exactly two edits to an archived document — M18's move-driven edge integrity
  and M25 — D4's audited relationship repair. This one-time migration is
  written up beside them with a **stated blast radius** — destination tokens,
  `Updated:`, and one `Revision:` bullet, in 29 named documents, once, on a
  stated date — and explicitly **not** as a general licence to edit archived
  prose. No CLI verb performs it.
- **When it lands: Phase 6**, in the same change that wires the rules. E4 is
  the constraint: `test_check_dogfood_repo_docs_is_clean` asserts this
  repository's own tree exits 0, so deferring the repair to Phase 9 would leave
  Phase 6's and Phase 8's exit criteria knowingly false. The `charter.md:52`
  conversion folds into that same change, for the same reason.
- **Adopters get the recipe, not the migration.** `cli.md` and the `UNRELEASED`
  CHANGELOG carry the upgrade note: 2.0 adds hard `broken-body-link` and
  `outside-root-body-link` errors; the common cause of the first is relative
  links in documents an older `docs` archived, and the fix is to rebase the
  destination; the fix for the second is to use a URL. Phase 9 walks that
  recipe on a throwaway copy seeded with the pre-repair damage.

### D7 — Compatibility, upgrade guidance, and surface parity

- **Breaking, deliberately.** A tree that has carried unnoticed prose damage
  starts failing `docs check`. That is the point of the 2.0 major version
  (`plan.md`: "new hard check failures … change existing automation").
- **No version bump.** M25 — D6 binds the whole train: the package stays
  `1.8.0` through M25–M28 and **M29** performs the single bump to `2.0.0`.
  M27 touches neither `pyproject.toml` nor the packaging version pins; its
  CHANGELOG entries accumulate under the existing `UNRELEASED` heading.
- **Surface parity in the same change** (`plan.md` › *Ongoing conventions*;
  `CLAUDE.md` › *Skill update flow*): `docs/cli.md`, `docs/convention.md`, the
  bundled `src/docs_cli/skill/` (`SKILL.md`, `references/use-cases.md`, and
  `references/cli.md` / `references/convention.md` kept **byte-identical** to
  `docs/cli.md` / `docs/convention.md`), and `CHANGELOG.md` all describe the
  same rule. `docs check --help` gains no new option, so the argparse surface
  is unchanged — but the rule list in `cli.md` and the exit-code prose both
  move.
- **Host-machine and Agent Playbook Suite skills are out of scope.** Per
  `CLAUDE.md`, host skills under `~/.claude/skills/` refresh only at a
  production ship (M29).

## Out of scope

- **Any mutation.** Rewriting a destination when a document moves is M28; M27
  is read-only apart from its own one-time legacy migration (D6).
- **Heading/anchor validation.** Fragments are preserved and never checked
  (`feedback-log.md`, 2026-08-10). A `plan.md#no-such-heading` link passes as
  long as `plan.md` exists.
- **Images, autolinks, raw HTML, and reference *uses*** (D1). Each is a
  candidate for a later milestone; none is in this grammar.
- **Indented (4-space) code blocks** (D2/Q3).
- **Reference-definition/use consistency** — an undefined `[label][ref]` use,
  or a defined-but-unused definition. That is a different rule about Markdown
  well-formedness, not about a missing file.
- **Link text, titles, and duplicate-label hygiene.**
- **A full CommonMark parser or any third-party Markdown dependency.**
  `architecture.md` pins stdlib-only.
- **Non-`.md` source files.** Only documents the walk yields are scanned;
  `README.md` outside the docs root, source code, and templates are not.
- **A repair verb.** No `docs fix-links`; the D6 migration is performed once by
  the milestone, not shipped as a command.
- **Anything outside the tree root.** M27 never stats, opens, or follows a path
  beyond the docs root; an escaping destination is *reported* (D4b) and never
  *probed*. Whether such a link's target exists is deliberately not knowable to
  `docs check`.
- **The `2.0.0` version bump, CHANGELOG dating, and release notes** (M29).

## Current state and risks

Measured read-only against this repository at docs-cli 1.8.0 during setup; the
full evidence table lives in the implementation log's setup record. Each
numbered item grounds a specific decision and maps to named regression coverage
in *Evidence → regression coverage* below.

- **E1 — The damage is real, and it is entirely archived.** A bounded prototype
  scan of `docs/` finds 455 link-shaped spans over the 70 documents the tree
  held at measurement time; **139 local destinations do not resolve, across 29
  documents — all of them under `archive/`.** The active tree has zero, and it
  still has zero after this milestone's own setup edits.
- **E2 — And it is one shape: the un-rebased archive move.** 132 of the 139
  resolve from the docs root (`plan.md` ×38, `status.md` ×24,
  `release-runbook.md` ×23, `cli.md` ×20 — all needing `../../`); 5 name a
  document that itself later moved; 2 name `references/adoption-playbook.md`,
  a bundled-skill file that never lived in the docs tree. Every one is
  repairable by a destination-token-only edit.
- **E3 — `docs check` is blind to all of it.** The tree exits **0** today with
  139 broken links. `check_doc` validates metadata and `Related:`; the body is
  opaque, as `test-strategy.md` › *What we don't test* still says.
- **E4 — The legacy policy is a hard gate, not an aspiration.**
  `tests/test_cli_check.py::test_check_dogfood_repo_docs_is_clean` asserts this
  repository's own `docs/` exits 0. The moment either rule lands, that test is
  RED until the tree is repaired — which also fixes *when* the repair must
  land: no later than the phase that wires the rules (D6, Phase 6).
- **E5 — Code masking is load-bearing, not theoretical.** Without it the scan
  gains 4 false positives inside fenced code — including `architecture.md:182`'s
  `[<path>](<path>)` — and 3 inside inline code spans.
- **E6 — An indented-code rule would cause false negatives.** All 9
  4-space-indented link-shaped spans in this tree are real links in blockquote
  and list continuations; 6 are among the 139 genuine breaks.
- **E7 — Exactly one link escapes the tree root, and it is in the active
  tree.** `charter.md:52` links to
  `../src/docs_cli/skill/references/use-cases.md`. A dedicated **containment
  census** — path arithmetic only, counting both escapes that would resolve and
  escapes that would not — was run across `docs/`, **all 33** committed fixture
  trees, and the bundled skill: **1 escape in total**, this one, and **zero in
  any fixture tree or in the bundled skill**. No fixture needs updating before
  Step 1. The link resolves only because `docs/` happens to sit beside `src/`
  in a git checkout — the same bytes in a container or a vendored subtree would
  not resolve, which is the whole argument for the hermetic boundary (D4b).
  It is converted to the canonical GitHub URL in Phase 6.
- **E8 — Nothing in the repository exercises the exotic grammar.** Across
  `docs/`, all 33 committed fixture trees, and the bundled skill: zero images,
  autolinks, raw-HTML anchors, reference definitions, angle-bracket or titled
  or percent-escaped or backslash-escaped destinations, and zero directory
  destinations. All 455 spans are plain inline links, and every fixture tree
  and the bundled skill resolve cleanly — so no existing fixture regresses when
  the rule lands, and Phase 3 must author every exotic form deliberately.
- **Structural risk — the parser.** A regex-only implementation is the failure
  mode the stub named: E5 proves it flags this project's own documentation, and
  a naive nested-paren or unbounded-label pattern risks catastrophic
  backtracking on the tree's 112 KB `cli.md`. The mitigation is a linear,
  single-pass scanner with a pinned grammar and an explicit pathological-input
  runtime lock.
- **Structural risk — the convention.** Enabling a hard body-link rule while
  `convention.md` treats archived prose as immutable (two narrow exceptions
  only) is a genuine policy collision, not an implementation detail. D6/Q1
  resolves it explicitly, with a stated blast radius; nothing here is
  grandfathered by accident.
- **Structural risk — hermeticity.** A rule that stats outside the root makes
  `docs check`'s verdict a function of the tree's *surroundings*, so identical
  bytes gate CI differently in a checkout, a container, and a vendored subtree.
  D4b removes the risk at the source: containment is decided by path arithmetic
  and the tool never looks outside the root at all.
- **Mitigating existing strengths.** `check_doc` already returns findings
  rather than raising, `Finding`'s four-key record is already closed and
  tested, `_iter_doc_texts` already skips `INDEX.md` and honours the exclusion
  predicate, and M25/M26 have just established the pattern this milestone
  follows: a pure planning/scanning layer with frozen signatures, unit-tested
  first, then wired into a verb.

### Evidence → regression coverage

| Evidence | Addressed by | Named coverage (Phases 2–3) |
|---|---|---|
| E1/E2 legacy archived damage | D6 repair + D3 resolution | a `bodylink-archived` fixture reproduces the un-rebased archive shape and yields exactly one `broken-body-link`; a repaired copy yields none; the live-tree repair is proven by `test_check_dogfood_repo_docs_is_clean` staying GREEN at Phase 8 |
| E3 total blindness | D4 rule | a document with a broken inline link makes `docs check` exit 2 and emits one `broken-body-link` record with the line, raw destination, and resolved candidate in `message` |
| E4 dogfood gate | D6 phase ordering | the dogfood test is classified at Phase 4 as GREEN-at-baseline, transitional at Phase 6, and GREEN again from Phase 6's own commit onward — covering both rules and both repairs |
| E5 code false positives | D2 masking | link syntax inside a fenced block and inside an inline code span produces **no** finding — asserted on the exact `[<path>](<path>)` and `` `[cli.md](cli.md)` `` shapes taken from this tree |
| E6 indented-code false negatives | D2 (no indented-code rule) | a real link indented four spaces inside a blockquote/list continuation **is** scanned and **is** reported when broken |
| E7 escaping link | D4b (Q5) | a destination escaping the root yields exactly one `outside-root-body-link` and **no** `broken-body-link`, whether or not it would have resolved; the containment test fires without any stat outside the root (asserted by pointing a fixture at a path that cannot exist); `../sub/../back-inside.md` normalises back under the root and is validated normally; the live `charter.md` conversion is proven by the dogfood test |
| E8 unexercised grammar | D1 + Phase 3 | every supported form (angle destination, title in all three quotings, percent-escape, backslash escape, balanced parens, reference definition) and every excluded form (image, autolink, raw HTML, reference use, root-absolute, protocol-relative, fragment-only, schemed) has its own named lock; the pre-M27 fixture trees gain neither a `broken-body-link` nor an `outside-root-body-link` finding |

## Deliverables

- [x] Supported Markdown forms, masking rules, resolution and containment
      rules, the two findings, and their precedence frozen in Phase 1 against
      the resolved Q1–Q7.
- [ ] Pure, stdlib-only, linear scanner with exact destination-token spans and
      length-preserving code masking.
- [ ] `broken-body-link` and `outside-root-body-link` hard errors wired into
      `check_doc`, containment tested before existence, with the JSON record's
      key set unchanged.
- [ ] Unit, fixture, and subprocess coverage for every supported form and every
      excluded form, plus the E5/E6 false-positive and false-negative locks, the
      no-double-report precedence lock, the never-stat-outside-the-root lock,
      and a pathological-input runtime lock. *(Written and committed in Step 1;
      deliberately left unticked because a RED lock is not yet locking. Ticked
      at Phase 8, when the suite goes GREEN.)*
- [ ] Controlled, audited legacy-tree repair — 139 archived breaks plus the one
      escaping active link — with `convention.md` carrying both the
      inside-the-root invariant and the third archived-document exception with
      its stated blast radius.
- [ ] Live-tree dogfood clean, plus a replayed pre-repair upgrade walk and
      documented migration evidence.
- [ ] Surface parity across `cli.md`, `convention.md`, the bundled skill
      (byte-identical mirrors), and the `UNRELEASED` CHANGELOG.

## TDD implementation plan

### Phase 1 — Define Contract

- Objective: freeze — against the resolved Q1–Q7 — the supported grammar table
  and its exactness rules, the masking contract and its length-preservation
  guarantee, destination classification, the resolution base and the
  fragment/target-kind rules, **the containment test** (join → lexical
  canonicalisation → under-root membership, with the `..`-escape-then-return
  and symlink cases decided and the divergence from `check_doc`'s
  `resolve()`-based archive test explained), **the precedence of containment
  over existence so the two rules never double-report**, both findings
  (`broken-body-link`, `outside-root-body-link` — severity, exit code,
  per-occurrence granularity, ordering, exact message templates), the closed
  JSON record, the `BodyLink` span contract M28 consumes, and the legacy-tree
  policy. No business logic lands.
- Files: `docs/cli.md` (the rule list, the exit-code prose, the closed-record
  note, and the **explicitly stated** out-of-root boundary), `docs/convention.md`
  (the inside-the-root invariant, the fence-your-code-samples rule, and the
  third archived-document exception), this milestone. Interface signatures are
  frozen in a *Decisions (Phase 1 — BINDING)* section here rather than stubbed
  in `src/docs_cli/cli.py`, following the M25/M26 precedent — stubs would
  perturb the Phase-4 subprocess RED reasons.
- Exit: specs, the message template, and the frozen signatures are internally
  consistent; no behavior changes; `docs check --root docs` still exits 0.

### Phase 2 — Write Tests (RED)

- Objective: express scanning, classification, resolution, and finding
  behaviour before any implementation — including every exclusion, which must
  be GREEN at baseline and stay GREEN.
- Files: a new pure-scanner module `tests/test_body_links.py` (the
  `tests/test_relate_plan.py` / `tests/test_archive_plan.py` precedent),
  `tests/test_check.py` for the rule over fixture trees, and
  `tests/test_cli_check.py` for exit codes, human output, and the JSON record.
- Exit: the E1–E8 locks in *Evidence → regression coverage* are RED **only**
  for missing M27 behavior; every exclusion lock and every pre-M27 fixture-tree
  lock is GREEN at baseline and classified as such;
  the two tests that pin the closed record —
  `tests/test_cli_check.py::test_check_json_emits_finding_array` and
  `::test_check_missing_inverse_json_record_keys_unchanged` — are asserted
  unchanged.

### Phase 3 — Create Data/Fixtures

- Objective: provide small committed trees isolating one semantic each, per
  `test-strategy.md`'s fixture policy, plus inline strings for the grammar.
- Files: new `tests/fixtures/trees/bodylink-*` trees — `-clean` (every
  supported form resolving), `-broken` (one unresolved inline link, nothing
  else), `-excluded-forms` (image, autolink, raw HTML, fenced and inline code,
  fragment-only, schemed, root-absolute — all silent), `-nested` (a
  subdirectory document linking up and down, including
  `../sub/../back-inside.md`, which normalises back under the root and must be
  validated normally), `-archived` (the E1/E2 un-rebased archive shape), and
  `-outside-root` (E7 — an escaping destination pointed at a path that cannot
  exist, so the "never stat outside the root" property is asserted by
  construction rather than by mocking). Exotic grammar (angle destinations,
  titles, percent- and backslash-escapes, balanced parens, reference
  definitions) lives in inline strings against the pure scanner — the M25 rule,
  because those cases assert on parse output, not on a tree walk.
- Exit: fixtures are structure-only (never date-sensitive), parse
  deterministically, and each yields exactly its intended finding set; a
  **new sibling lock** (`test_check_tree_pre_m27_fixtures_gain_no_body_link_findings`,
  Phase-1 amendment 3) covers **both** new rules across all 33 pre-M27 trees —
  which the setup census already predicts, having found zero escapes and zero
  unresolved local destinations in every one of them — while
  `test_check_tree_legacy_fixtures_gain_no_new_findings` stays byte-identical
  and simply gains the six new trees as parametrizations.

### Phase 4 — Run Tests (RED Baseline)

- Objective: prove the new tests fail for the intended missing behavior and for
  nothing else.
- Files: implementation log only.
- Exit: full baseline captured with exact counts; zero collection errors, zero
  tracebacks, zero xfails; every pre-existing test id mechanically proven still
  present and GREEN; every GREEN-at-baseline lock classified by name —
  including the **transitional** classification of
  `test_check_dogfood_repo_docs_is_clean`, which is GREEN now, would be RED
  between wiring the rules and repairing the tree, and is restored inside
  Phase 6's own commit.

### Phase 5 — Update Base Interfaces

- Objective: add the scanner models and pure helpers without wiring any rule —
  an immutable `BodyLink` record (kind, 1-based line and column, raw
  destination, unescaped path, fragment, destination-token span), the
  length-preserving `_mask_code`, the `scan_body_links` grammar,
  `classify_destination`, and the containment/resolution helpers. Shaped after
  M25's `RelateEdit`/`plan_relate` and M26's `ArchiveMove`/`plan_archive` split,
  which the codebase already proves out. The scanner stays a pure function of
  the text and reports **every** local destination; containment is the rule's
  job, not the scanner's (D5).
- Files: `src/docs_cli/cli.py` and `tests/test_body_links.py`.
- Exit: interfaces typecheck and are unit-tested; `check_doc` is untouched, so
  the rule-level and CLI-level tests remain honestly RED at the seam;
  `docs check --root docs` still exits 0.

### Phase 6 — Implement Offline/Core Path

- Objective: wire `body_link_findings` into `check_doc` — containment before
  existence, both rules, ordering, per-occurrence granularity, the frozen
  messages — and, in the same change, perform the D6 live-tree repair so the
  repository's own dogfood gate is never knowingly RED across a commit
  boundary.
- Files: `src/docs_cli/cli.py`, the check unit/integration tests, the 29
  archived documents' destination tokens plus their `Updated:` / `Revision:`
  audit lines, and **`docs/charter.md`** — line 52's escaping destination
  becomes the canonical GitHub URL, with its `Updated:` bump and **no**
  `Revision:` bullet (M25 — D4: `Revision:` is archived-only). That single
  active-tree edit is the whole active-tree diff; the active tree has zero
  `broken-body-link` breaks (E1).
- Exit: core and integration tests GREEN; the repair diff touches only
  destination tokens and audit metadata, verified by a byte-level review of
  every changed line; `docs check --root docs` exits 0 with **both** rules in
  force, and a containment census over the repaired tree reports zero escapes.

### Phase 7 — Update Tool/Wrapper Layer

- Objective: reconcile every parallel surface — `cli.md`'s `docs check` rule
  list, exit-code prose, JSON field-table note, and the **explicitly stated**
  out-of-root boundary (an adopter must be able to predict it, D4b);
  `convention.md`'s body-link authoring rules, the *links stay inside the tree
  root* invariant, and the named archived-document exception with its stated
  blast radius; the bundled skill; and the `UNRELEASED` CHANGELOG with the
  adopter upgrade recipe for both rules.
- Files: `docs/cli.md`, `docs/convention.md`, `src/docs_cli/skill/`
  (`SKILL.md`, `references/use-cases.md`, and the byte-identical `cli.md` /
  `convention.md` mirrors), `CHANGELOG.md`. **Not** `pyproject.toml` or the
  version pins (M25 — D6). No argparse change is expected (D4/Q6).
- Exit: the reference byte-identity tests and the surface-parity checks are
  GREEN; `docs check --help` and `cli.md` agree.

### Phase 8 — Run Tests (GREEN)

- Objective: run the focused and full suites plus lint, format, types,
  reference byte identity, and docs integrity.
- Files: implementation log only unless a real defect is found.
- Exit: all gates GREEN with exact counts recorded, and every pre-existing test
  id mechanically proven still present and GREEN.

### Phase 9 — Integrate / Accept / Dogfood

- Objective: on a throwaway copy of this docs tree **seeded with the
  pre-repair damage** (reconstructed from git), walk the exact upgrade recipe
  an adopter faces: run `docs check`, read the 139 `broken-body-link` findings
  and the one `outside-root-body-link`, apply the documented rebase and the
  documented URL conversion, re-check clean. Then sweep for false positives
  across the bundled skill and every fixture tree, and measure scan runtime on
  the live tree (70 documents, 455 links, a 112 KB `cli.md`) plus a pathological
  input. Prove hermeticity end to end: the throwaway copy is checked from a
  location where the sibling `src/` does **not** exist, and produces the
  identical verdict.
- Files: throwaway tree only; the committed docs record the evidence.
- Exit: the upgrade walk reaches exit 0 with a destination-token-only diff;
  the false-positive sweep is empty; the relocated-copy verdict is identical;
  scan runtime is recorded and bounded; the real tree is untouched by the
  dogfood.

### Phase 10 — Quality, Docs, Refactor

- Objective: simplify the scanner, close `architecture.md` and
  `test-strategy.md` (whose *What we don't test* still says "the body content
  is opaque" — no longer true), update the shipped use-case catalog, and write
  the completion summaries.
- Files: code/docs as justified, this milestone and the implementation log.
- Exit: full gate GREEN; no placeholders; M27 implementation-complete with the
  `BodyLink` span contract handed to M28, staying `Lifecycle: active` until the
  M29 publish closeout.

## Phase checklist

- [x] Phase 1 — Define Contract
- [x] Phase 2 — Write Tests (RED)
- [x] Phase 3 — Create Data/Fixtures
- [x] Phase 4 — Run Tests (RED Baseline)
- [ ] Phase 5 — Update Base Interfaces
- [ ] Phase 6 — Implement Offline/Core Path
- [ ] Phase 7 — Update Tool/Wrapper Layer
- [ ] Phase 8 — Run Tests (GREEN)
- [ ] Phase 9 — Integrate / Accept / Dogfood
- [ ] Phase 10 — Quality, Docs, Refactor

## Decisions carried from discovery

- `docs check` emits a **hard error** when a parsed local Markdown body link
  points at a missing file, including damage introduced outside `docs mv` or
  `docs archive` (`feedback-log.md`, 2026-08-10).
- Links inside code and external URLs are **out of scope**; plain-text mentions
  are never touched.
- Move-time rewrites preserve fragments such as `#section`, and the first
  implementation does **not** validate whether the referenced heading exists.
- Detection (M27) and mutation (M28) are separate milestones sharing **one**
  scanner; there is never a second Markdown parser.
- The package version stays `1.8.0`; M29 performs the single bump (M25 — D6).

## Decisions (Phase 1 — BINDING)

Phase 1 freezes the surface Phase 2 asserts against. Everything below is
binding for M27; Phases 5–7 implement it verbatim. The setup decisions
(D1–D7 plus D4b) and the setup questions (Q1–Q7) are **not** re-opened — this
section makes them exact. The full author-facing statement lives in
`cli.md` › *Markdown body-link validation (M27 — D1–D4b)* and
`convention.md` › *Body links (M27)*; what follows is the machine-facing
contract plus the decisions that could not be read off the setup text.

### Amendments to the setup-frozen material (conductor-binding)

Three frozen items could not stand as written. All three are recorded here so
the binding scope and the frozen contract cannot disagree.

| # | Amendment | Why the frozen form could not stand |
|---|---|---|
| 1 | **`broken-body-link`'s message becomes `body link at line <N> does not resolve to an existing path: <raw> (resolves to <candidate>)`.** D4's proposed `does not resolve to a file:` is retired. | It contradicts the **operator-binding Q7**: any existing filesystem entry — file **or directory** — satisfies a destination. A correct link to a directory that later broke would have been reported with prose asserting the wrong test, and an agent reading it would look for a missing *file*. D4 is amended in place. |
| 2 | **`outside-root-body-link`'s message is specified** as `body link at line <N> leaves the docs root: <raw> (normalises to <candidate>); links outside the tree must be URLs`. | D4b named the rule, its severity, its exit code, its granularity and its precedence, but **never gave a message**. Phase 2 asserts contract strings verbatim, so leaving it to Phase 6 would have made the test unwritable. The trailing clause names the repair, mirroring `missing-inverse`'s `(or remove the edge)`; `broken-body-link` names its repair by printing the candidate path the tool probed. |
| 3 | **The 33-tree no-new-findings lock is a NEW sibling test, not an extension of `test_check_tree_legacy_fixtures_gain_no_new_findings`.** The Phase-3 exit criterion is amended in place below. | The existing test's tree list excludes `reciprocal-*`, so it covers **23** trees, not 33 — extending its assertion would not deliver the stated coverage, and would additionally make the three deliberately-damaged `bodylink-*` trees Phase 3 authors **fail** it. A sibling parametrized over the 33 non-`bodylink-*` trees delivers the coverage the milestone asked for **and** keeps M27's no-regression proof at a clean zero moved test ids. The existing test stays **byte-identical**; the six new trees are swept into it (23 → 29) and pass, because it asserts only `missing-inverse == []`. |

### Frozen message templates (BINDING)

```
body link at line <N> does not resolve to an existing path: <raw> (resolves to <candidate>)
body link at line <N> leaves the docs root: <raw> (normalises to <candidate>); links outside the tree must be URLs
```

`<N>` is the 1-based line of the destination token's first character; `<raw>`
is the destination token **exactly as written** (angle brackets, percent- and
backslash-escapes included); `<candidate>` is the canonical root-relative
POSIX path for `broken-body-link` and the lexically normalised `../`-prefixed
path for `outside-root-body-link`. `<candidate>` prints **unconditionally**,
even when it equals `<raw>` — no "it depends" cell (M26's rule).

Both rules: `severity: error`, exit **2** through the unchanged `exit_code_for`
(the rule adds a value to an enumeration, not a branch to a function); **one
finding per occurrence**; attached to the **referring** document; JSON key set
**closed** at `{path, severity, rule, message}`; emitted immediately after the
document's `broken-ref` group and before the `stale` block, in source order
(line, then column) within that block.

### Contract points that could not be read off the setup text

Each of these had to be settled for Phase 2's assertions to have an answer.
All are stated author-facing in `cli.md`; they are itemised here because they
are decisions, not restatements.

1. **A label may span newlines, but never a blank line.** The scan for the
   closing `]` is bounded at the first blank line. Forced by real data:
   `convention.md`'s exclusion cross-reference and `agent-native-invocation.md`'s
   source note are both real, resolving, load-bearing links whose label wraps.
   Excluding them would make M27 blind to a link **M28 must rewrite** — so
   when `cli.md` later moves, M28 would silently leave it broken while M27
   reported damage its sibling caused but could not see. Measured cost of
   allowing them: 2 extra spans, **0** extra findings.
2. **A label ends at its first unescaped `]`; balanced brackets inside a label
   are not supported.** Bounded grammar, stated as an exclusion with an escape
   hatch. Verified zero occurrences in `docs/`, the 33 fixture trees, and the
   bundled skill, so it costs nothing today.
3. **An inline code span never crosses a line boundary.** Otherwise a single
   unpaired backtick masks the remainder of a 112 KB `cli.md` — unbounded
   false negatives, the exact failure mode E6 exists to prevent. All three
   measured E5 inline-span cases are single-line, so the choice is
   behaviourally neutral on this tree.
4. **`MAX_DESTINATION_PAREN_DEPTH = 3`,** counted over parentheses *inside*
   the destination (the link's own delimiters do not count), and named as a
   docs-cli bounded-scanner bound — **not** a CommonMark conformance claim
   (D1 already licenses that framing).
5. **Backslash escapes cover `\` + any ASCII punctuation character *or a
   space*.** The space leg is forced by "the destination ends at the first
   *unescaped* whitespace"; D1's six named characters are a subset.
6. **Destination decoding order:** strip a surrounding `<…>` pair → split on
   the first `#` in the remaining **raw** text → backslash-unescape →
   percent-decode (`urllib.parse.unquote`; invalid sequences pass through) →
   join → normalise. Consequences, all specified: a decoded `%23` is **not** a
   fragment delimiter, a decoded `%2F` **is** a path separator, a backslash
   cannot escape a `#` out of being the fragment delimiter, and the fragment
   is carried verbatim because nothing resolves it.
7. **Classification runs on the token as written, with a surrounding `<…>`
   pair stripped first** — so an angle-wrapped autolink-shaped destination
   classifies as `scheme` rather than `local`. The six kinds are tested in the
   order `empty`, `fragment`, `protocol-relative`, `root-absolute`, `scheme`,
   `local`, which is why `//host/x` is protocol-relative rather than
   root-absolute.
8. **Containment uses `posixpath`, explicitly — never `os.path`.** D3's
   "`os.path.normpath`-style" is a defect: on Windows `os.path.normpath`
   rewrites `/` to `\` and treats `\` as a separator, making the containment
   verdict platform-dependent and destroying the exact hermeticity property
   D4b exists to guarantee. This reuses `_canonical_related_target`'s stated
   "POSIX paths on every platform" rationale.
9. **The containment predicate is byte-for-byte the one `docs archive`
   already uses** for its `outside-root` ineligibility (`rel == ".."` or
   `rel.startswith("../")`), minus the `/` leg — a root-absolute *body*
   destination is classified `root-absolute` and silenced **before**
   containment runs, whereas a root-absolute `Related:` target is
   `outside-root`. That divergence is deliberate: `/path` in prose names a web
   root, not a tree path.
10. **The whole document text is scanned, with offsets into the original
    text** — not the post-metadata body. A `Related:` bullet cannot be
    link-shaped (verified: zero reference definitions exist anywhere in the
    repository), and scanning the body instead would hand M28 a second offset
    base to reconcile.
11. **`.` never appears in either message.** `sub/..` normalises to `.`, which
    is contained and — being the root directory, an existing entry — satisfied.
12. **Pathological-input runtime bound: ≥200 KB of adversarial input in under
    2.0 s** (roughly 50× the expected cost), stated with its flakiness
    trade-off. The bound exists to catch catastrophic backtracking, not to
    benchmark.

### The `BodyLink` span record and the frozen Phase-5 signatures

Contract only — **no code lands in Phase 1**.

```python
BODY_LINK_KINDS: frozenset[str] = frozenset({"inline", "reference-definition"})
DESTINATION_KINDS: frozenset[str] = frozenset(
    {"local", "empty", "fragment", "scheme", "protocol-relative", "root-absolute"}
)
MAX_DESTINATION_PAREN_DEPTH: int = 3

@dataclass(frozen=True)
class BodyLink:
    kind: str            # a BODY_LINK_KINDS member
    line: int            # 1-based line of the destination token's first character
    column: int          # 1-based column of the same character
    raw: str             # destination token EXACTLY as written; == text[start:end]
    path: str            # backslash- then percent-unescaped path part, fragment removed
    fragment: str | None # text after the FIRST '#', without the '#'; None when absent
    start: int           # offset into the ORIGINAL text
    end: int             # one past the last character

def _mask_code(text: str) -> str
def scan_body_links(text: str) -> tuple[BodyLink, ...]
def classify_destination(raw: str) -> str                      # a DESTINATION_KINDS member
def normalise_body_link_target(doc_rel: str, dest_path: str) -> str   # pure posixpath
def _body_link_is_contained(candidate: str) -> bool
def body_link_findings(path: Path, text: str, root: Path) -> list[Finding]
```

- **`text[link.start:link.end] == link.raw` is a named invariant** with its own
  parametrized test over every supported form. This is *the* M28 handoff:
  excluding the `<…>` brackets from the span would break M28 the moment it
  splices a destination containing a space. The span **includes** the angle
  brackets and **excludes** the title.
- **`scan_body_links` is a pure function of the text** and reports *every*
  recognised occurrence, including non-`local` ones. Containment and existence
  are `body_link_findings`' job (D5). That split is what lets
  `outside-root-body-link` exist at all and what M28 consumes.
- **`normalise_body_link_target` takes the referring document's
  root-relative POSIX path** (e.g. `archive/2026-01-01/old-log.md`) and drops
  the last segment itself, so callers never pre-compute a directory.
- **`body_link_findings` is called from `check_doc`**, after the `broken-ref`
  loop and before the `stale` block. There is **no** second `check_tree` pass:
  both rules need only the referring document's own text and its own
  directory. `docs touch --check` inherits them for free through
  `_run_touch_check` → `check_tree`.

**Reuse — no new machinery is invented.** Root-relative rendering:
`_root_relative`. Lexical normalisation: the `posixpath.normpath` idiom of
`_canonical_related_target`. Containment: the predicate in
`_candidate_exclusion_reason`, minus the `/` leg (point 9 above). Walk and
`INDEX.md` skip: `_iter_doc_texts`, unchanged. Exit codes: `exit_code_for`,
unchanged. Human output: `_print_check_findings`, unchanged. Record
serialisation: `finding_to_json`, unchanged. No new exception class, no new
flag, no new verb.

**Phase-5 implementation note (not a contract term).** The scanner must stay
linear on adversarial input. Two shapes to avoid: re-deriving the blank-line
bound from scratch at every candidate (quadratic on a long fence-free
document), and restarting the outer scan at `open + 1` after a failed
candidate. Restarting at the failed candidate's closing `]` is equivalent for
this grammar — whether a candidate forms a link depends on what follows the
`]`, not on which `[` found it — except after the image (`!`) rejection, which
does depend on the opening `[` and therefore needs the cached closing position
rather than a rescan.

### Deviation from the Phase-1 file list (deliberate, logged)

The milestone's Phase-1 file list names "Interface signatures … frozen in a
*Decisions (Phase 1 — BINDING)* section here rather than stubbed in
`src/docs_cli/cli.py`". Phase 1 accordingly made **zero** `cli.py` edits:
stubs would change the Phase-4 subprocess RED reasons and risk baseline
behaviour, and the phase's own exit criterion is "no behavior changes". The
signatures above land as real code in Phase 5. This mirrors the M25 and M26
precedent.

### Follow-through recorded at Phase 1 (so it cannot be lost)

| # | Item | Phase |
|---|---|---|
| 1 | `Finding`'s docstring rule enumeration gains `broken-body-link` and `outside-root-body-link`. | 5 / 6 |
| 2 | `docs check`'s argparse `description` says "and broken `Related:` references"; it must also name body links (surface-parity gate). | 7 |
| 3 | The bundled `SKILL.md`'s `docs check` row names neither rule. | 7 |
| 4 | The bundled `references/use-cases.md` — the "Validate in CI" row and a 2.0 upgrade block. | 7 |
| 5 | `CHANGELOG.md` under the existing `UNRELEASED` heading, with the adopter upgrade recipe for **both** rules. **No** version bump (M25 — D6). | 7 |
| 6 | `test-strategy.md` › *What we don't test* still says "the body content is opaque" — false the moment M27 lands. (`convention.md`'s twin statement is on the byte-parity gate, so it was corrected in Phase 1.) | 10 |
| 7 | **`tests/fixtures/expected/docs-INDEX.md` must be regenerated inside Phase 6's own commit.** The D6 repair bumps `Updated:` on 29 archived documents plus `charter.md`, and `test_index_dogfood_repo_docs_snapshot` compares the regenerated index against that frozen snapshot. Its `_normalize_generated_date` helper blanks **only** the `_Generated <date>._` line — every per-entry `Updated YYYY-MM-DD.` is compared **literally**, so all 30 bumps land in the diff. Regenerate it alongside the `test_check_dogfood_repo_docs_is_clean` restoration, in the same commit that wires the rules; deferring it leaves Phase 6's exit criteria knowingly false for the same reason E4 does. | 6 |

### Authoring traps this contract creates (recorded so Phase 2–7 cannot trip them)

1. **`test_bundled_skill_has_no_repo_relative_links` scans raw lines.** It
   looks for the literal substring `](../` in every bundled skill `.md`,
   fences included — a fence does not protect you, because the test never
   masks anything. `references/cli.md` and `references/convention.md` are
   byte-identical copies of the Phase-1 edits, so **neither spec may ever
   write a full link whose destination starts with `../`**, even as an
   example. Both files are at zero occurrences today and Phase 1 keeps them
   there. Authoring rule: name an escaping destination as a bare path in
   inline code, never in link form.
2. **`test_installed_skill_references_do_not_depend_on_source_checkout`
   forbids the literal `../src/docs_cli/` in any bundled reference** — a
   **third** gate, found by tripping it. The natural worked instance for
   `outside-root-body-link` is E7's real destination, `charter.md:52`'s
   `../src/docs_cli/skill/references/use-cases.md`, and writing it into
   `cli.md` breaks that test the moment the byte-identical mirror is copied.
   Fenced or not makes no difference; the test scans raw text. The worked
   instance therefore uses a neutral escaping path, and the real one is named
   in E7 and in this milestone (neither is on the bundled-skill gate). The
   same test also forbids `../../../../docs/`.
3. **Every example this contract writes becomes scannable once Phase 6
   lands.** Every link-shaped example in `cli.md`, `convention.md`, and this
   milestone lives inside a fence or an inline code span — already the house
   style. Nothing may become a **real** reference definition either: a
   line-anchored `[plan]: plan.md` in unfenced prose would be one. Verified
   after the Phase-1 edits: `cli.md` and `convention.md` carry no new
   scannable span, and the repository still contains zero reference
   definitions.

## Resolved setup questions (Q1–Q7, BINDING)

Seven questions were raised at setup and **all seven are resolved before
Phase 1**. The originals are kept so the decision trail reads end-to-end. Three
were operator decisions (Q1, Q2, Q5); four were conductor-resolved (Q3, Q4, Q6,
Q7) as determined by the specs, the measured evidence, or the M25/M26
precedent. **Q5 was resolved against the setup recommendation, then amended
again** — both turns are recorded, because the reasoning is what makes the
final shape defensible.

### Q1 — Legacy archived damage: repair, or scope the rule?

**RESOLVED → D6 (operator). Repair; the rule stays uniform.** The rule applies
to archived and active documents alike — the reach `broken-ref` and
`missing-inverse` already have — and the 139 breaks are repaired once,
destination-tokens-only, audited with an `Updated:` bump **and** a dated
`Revision:` bullet (M25 — D4's shape), landing in **Phase 6** in the same change
that wires the rules.

Three verified facts decided it. **(a)** This damage class is *produced by
docs-cli itself*: `docs archive` is a core verb, 8 of the 33 committed fixture
trees already carry `archive/` directories, and 132 of the 139 breaks are the
pure un-rebased `../../` that no version of the tool has ever applied — so
adopters' archives are where this breakage predominantly lives, and an
archived-exempt rule would make the tool **silent about the exact breakage it
causes**. **(b)** This tree is *published*: `docs/` — archive included — ships
inside every PyPI **sdist** (`[tool.hatch.build.targets.sdist] include = […
"docs" …]`; the wheel carries only `src/docs_cli`) and is public on GitHub,
where the four worst-hit destinations — `plan.md` ×38, `status.md` ×24,
`release-runbook.md` ×23, `cli.md` ×20 — are exactly what a prospective adopter
reads. **(c)** Scoping would buy nothing here: the active tree already has zero
breaks, so the tool would pass while staying blind to 139 real failures in
bytes it publishes.

`convention.md` gains the **third** narrow exception to archived-document
immutability, beside M18's move-driven edge integrity and M25 — D4's audited
relationship repair — written with a **stated blast radius** (destination
tokens, `Updated:`, one `Revision:` bullet, 29 named documents, once, on a
stated date) and explicitly not as a general licence. No CLI verb performs it.

Both sub-decisions confirmed: the 2 `references/adoption-playbook.md`
occurrences become the **canonical GitHub URL** (`convention.md:417`'s existing
spelling), and the `Updated:` bump **is** wanted alongside `Revision:`.

### Q2 — Which Markdown forms does the scanner recognise in v1?

**RESOLVED → D1 (operator).** Inline links with plain **and** angle-bracket
destinations and optional titles in all three quotings, **plus** reference
definitions. Excluded from v1: images, autolinks, raw HTML, and
shortcut/collapsed/full reference *uses* — a reference use carries no
destination, so validating the definition covers it. Reference definitions are
included despite zero occurrences today because they are the one non-inline
form that carries a destination, and M28 must be able to rewrite them.

**Images are a scoped exclusion, recorded as such** (see D1): including them is
a one-character change, which is precisely why it must be a decision rather
than a default. Zero images exist anywhere in `docs/`, the 33 fixture trees, or
the bundled skill (E8), so the rule would ship untested against real data; a
broken image is a different failure mode deserving its own wording; and
admitting images would widen **M28's** rewrite surface in the same stroke.
Carried in *Follow-ups recorded for later milestones*.

### Q3 — What counts as code?

**RESOLVED → D2 (conductor).** Mask **fenced code blocks and inline code spans
only**; no 4-space indented-code rule. E6 is decisive: all nine
4-space-indented link-shaped spans in this tree are real links in blockquote and
list continuations, and six are genuinely broken — an indented-code rule would
buy false negatives on live damage. Two mitigations go into `convention.md` as
authoring rules: **fence code samples that contain link syntax** (every code
sample in this repository already is), and a backslash escape
(`\[x](y.md)`) always opts a span out.

### Q4 — The finding's shape

**RESOLVED → D4 (conductor).** Rule id `broken-body-link`; `severity: error`;
exit code 2; **one finding per occurrence**; attached to the referring
document; emitted after the `broken-ref` group in source order. The `--json`
record's **key set stays closed** at `{path, severity, rule, message}`, with the
1-based line, the raw destination as written, and the resolved candidate
carried in `message` — exactly what M25 did for `missing-inverse`. Opening the
record would break both tests that pin it —
`tests/test_cli_check.py::test_check_json_emits_finding_array` and
`::test_check_missing_inverse_json_record_keys_unchanged` — change the
wire format for one rule, and establish that any future rule may add fields.

### Q5 — Destinations that leave the docs root

**RESOLVED → D3 + D4b (operator, amended 2026-08-14).** Two turns, both
recorded:

- **First turn — resolved against the setup recommendation.** The setup draft
  proposed validating out-of-root destinations by existence. Rejected: the
  hermetic boundary wins. `docs check` must never touch the filesystem outside
  the tree it was pointed at, because a check has to be a **function of the
  tree alone**. `charter.md:52` resolves today only because `docs/` happens to
  sit beside `src/` in a git checkout; the identical bytes in a container, a
  vendored subtree, or an adopter's repository would produce a different
  verdict, and a result that varies with the tree's surroundings cannot gate
  CI. It also matches the codebase's own boundary in the same place —
  `src/docs_cli/cli.py:5216`'s `if not primary.is_relative_to(root)`, M26's
  outside-root refusal (`31bdc59`) — keeps the contract decidable (no symlink,
  `..`-escape-then-return, or case-folding questions), and avoids billing M28
  for rewrites into territory the tool does not own.
- **Second turn — the amendment.** Silently *skipping* an escaping destination
  was then rejected too: `charter.md:52` is a working, load-bearing link that
  would rot unnoticed, and a silent decline is the failure mode this milestone
  exists to remove. The boundary is kept and the **response** changes — the
  escape is detected by **path arithmetic alone** and reported as its own
  finding, `outside-root-body-link` (D4b), an **operator-approved post-draft
  scope addition** following M25's `duplicate-field` precedent.

Consequences, all carried through: `convention.md` adopts the invariant *a
local Markdown body link stays inside the tree root; anything outside the tree
is a URL*; `cli.md` states the boundary explicitly so an adopter can predict it;
Phase 1 pins containment **before** existence so the two rules never
double-report; and `charter.md:52` is converted to the canonical GitHub URL in
Phase 6 — the identical treatment Q1 gives the 2 adoption-playbook links.

**The two decisions converge, which is corroboration rather than coincidence.**
Routing those adoption-playbook links to a URL is now doubly right: the
relative alternative, `../../../src/docs_cli/skill/references/adoption-playbook.md`,
would itself have been an `outside-root-body-link` violation. Q1 and Q5 were
taken independently and arrive at the same spelling.

**Census re-verified under the containment test** (path arithmetic only,
counting escapes that would resolve *and* escapes that would not), across
`docs/`, all 33 committed fixture trees, and the bundled skill: **exactly one
escape in total** — `charter.md:52` — and **zero in any fixture tree or in the
bundled skill**. No fixture needs updating before Step 1.

**Handed to M28 as a simplification, not a question:** because an escaping link
is now a reported and forbidden condition, the convention guarantees escaping
links do not exist in a clean tree, so M28 never has to rewrite one. Under the
rejected silent-skip reading, that question would have fallen to M28.

### Q6 — A `.docs.toml` opt-out for the new rules?

**RESOLVED → D4 (conductor). No knob.** The 2.0.0 major bump is the migration
signal (`plan.md` › *Sequencing* says so explicitly), the upgrade recipe is
mechanical and documented (D6), and a knob would let real damage hide behind a
config line. `unknown-field` (M10) is opt-**in** only because it depends on a
per-tree vocabulary the tool cannot infer; that rationale does not transfer to
a rule about whether a file exists.

### Q7 — What satisfies a destination?

**RESOLVED → D3 (conductor). Any existing filesystem entry — file or directory,
any extension.** `convention.md` already states that non-`.md` files may be
referenced from prose and that `Related:` checks existence "regardless of its
extension"; body links inherit that, and a directory destination is a
legitimate Markdown link. A strict `is_file()`, for exact parity with
`broken-ref`, would report a correct directory link as broken. Q7 applies
**within** the root — Q5's containment test decides membership first.

### Also settled, without a question

- **Version staging.** The package stays `1.8.0`; **M29** performs the single
  bump to `2.0.0`. CHANGELOG entries accumulate under `UNRELEASED`
  (M25 — D6).
- **Where the rules live.** In `check_doc`, per-document, with no second
  `check_tree` pass — unlike M25's `missing-inverse`, they need nothing beyond
  the referring document's text and directory.
- **`INDEX.md` is never scanned.** `_iter_doc_texts` already skips the
  root-level generated index for every rule; M27 states it rather than
  inheriting it silently.
- **A `malformed` document is not also body-link checked.** `check_doc`'s
  existing early return on a missing H1 stands; `malformed` keeps sole
  ownership, mirroring how `reciprocity_findings` skips unparseable documents.
- **Exclusion predicates govern the walk, not the destination.** A link to an
  excluded-but-existing file resolves (M26 — Q8's shape, restated).
- **Fragments are preserved and never validated** — no heading existence check
  in this milestone or the next.
- **Skill channels.** The bundled skill in `src/docs_cli/skill/` updates in the
  **same change** as the surface, with `references/cli.md` and
  `references/convention.md` byte-identical to `docs/cli.md` and
  `docs/convention.md`. Host-machine skills refresh only at the M29 production
  ship (`CLAUDE.md`; `plan.md`).

## Follow-ups recorded for later milestones

Raised during setup, judged out of M27's frozen scope, and deliberately **not**
implemented here.

| # | Follow-up | Home |
|---|---|---|
| 1 | **Images (`![alt](dest)`) join the validated grammar.** A one-character change to the matcher, deliberately excluded from v1 (Q2): zero exist in `docs/`, the 33 fixture trees, or the bundled skill, so the rule would ship unexercised; a broken image deserves its own finding wording rather than being folded into `broken-body-link`; and admitting images widens M28's rewrite surface in the same stroke. | M28+ |
| 2 | **Autolinks, raw HTML anchors, and reference *uses*.** Same reasoning, lower value — a reference use carries no destination of its own, and raw HTML would drag an HTML parser into a stdlib-only tool. | Later |
| 3 | **Reference-definition/use consistency** — an undefined `[label][ref]`, or a definition nothing uses. A Markdown well-formedness rule, not a missing-file rule; it belongs to a different family from `broken-body-link`. | Later |
| 4 | **Heading/anchor validation for fragments.** Explicitly out of scope for M27 *and* M28 by the 2026-08-10 operator decision; recorded so a later milestone can pick it up knowingly rather than rediscover it. | Later |
| 5 | **M27 hands M28 a simplification, not a question** (Q5): escaping destinations are a *forbidden and reported* condition, so a clean tree contains none and **M28 never has to rewrite one**. Recorded so M28's scope can rely on it rather than re-derive it. | M28 (input) |
| 6 | **A 4-space indented-code rule**, if the convention's fence-your-samples guidance ever proves insufficient. E6 makes it a net loss today. | Later |
## Testing and quality gate

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q
.venv/bin/docs check --root docs
```

Additional gates: the `docs check --json` closed-key-set assertion (unchanged
by **both** new rules), `docs check --help` / `cli.md` surface parity, bundled
`references/cli.md` and `references/convention.md` byte identity, the pre-M27
fixture-tree no-new-findings lock covering `broken-body-link` **and**
`outside-root-body-link` across all 33 trees (a **sibling** test, per Phase-1
amendment 3 — `test_check_tree_legacy_fixtures_gain_no_new_findings` is not
extended and stays byte-identical), the no-double-report precedence lock, a
pathological-input runtime lock on the scanner, and the live INDEX snapshot.

## Success criteria

- Supported local links resolve correctly from root-level and nested
  documents, with `../` handled and fragments preserved.
- A missing destination inside the root makes `docs check` exit 2 with a stable
  human line and a stable four-key JSON record naming the 1-based line, the raw
  destination, and the resolved candidate.
- A destination that leaves the root makes `docs check` exit 2 with exactly one
  `outside-root-body-link` and **no** `broken-body-link`, decided by path
  arithmetic alone — the tool never stats, opens, or follows anything outside
  the root, so the verdict is a function of the tree and nothing else. Checking
  the same tree from a different location yields the identical result.
- Code (fenced and inline), examples, external and schemed URLs, images, raw
  HTML, autolinks, reference *uses*, root-absolute and protocol-relative
  destinations, and fragment-only links produce **no** finding — proven on the
  exact shapes taken from this repository (E5) as well as on authored fixtures.
- A real link indented four spaces inside a blockquote or list continuation is
  still scanned (E6) — the scanner buys no false negatives to avoid false
  positives.
- All 33 pre-M27 fixture trees and the bundled skill gain zero findings of
  either kind.
- The live tree has a documented, auditable path to a clean result — 139
  archived rebases plus one active-tree URL conversion — and the repository's
  own `docs check` is clean with both rules in force.
- The scanner is reusable by M28 without duplicating parsing logic: `BodyLink`
  carries exact destination-token spans into the original text, and code
  masking is length-preserving so those spans stay valid.
- Full quality, compatibility, and dogfood gates are GREEN, leaving M28 ready
  to prepare next.
