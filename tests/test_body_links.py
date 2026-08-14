"""M27 — the pure Markdown body-link scanner seam: masking, grammar, spans,
classification, containment, and the two findings.

Phase 2 (written RED). Every symbol under test lands in Phase 5/6:
`BodyLink`, `_mask_code`, `scan_body_links`, `classify_destination`,
`normalise_body_link_target`, `_body_link_is_contained`,
`body_link_findings`, `BODY_LINK_KINDS`, `DESTINATION_KINDS`, and
`MAX_DESTINATION_PAREN_DEPTH`. They are reached through `getattr(cli, ...)`
rather than a module-level import, so collection stays clean, the RED reason
is a single honest `AttributeError`, and `mypy src/ tests/` stays green at
baseline (getattr yields `Any`).

The contract under test is the milestone's *Decisions (Phase 1 — BINDING)*
and `cli.md` › *Markdown body-link validation (M27 — D1–D4b)*.

Exotic grammar lives here as **inline strings**, not as committed fixture
trees (the M25 rule): every case below asserts on parse output, not on a tree
walk. The `bodylink-*` fixture trees Phase 3 authors cover the tree-walk half.
"""

from __future__ import annotations

import dataclasses
import os
import time
from pathlib import Path

import pytest

from docs import Finding
from docs_cli import cli


def _m27(name: str):
    """Fetch an M27 symbol that does not exist yet.

    The indirection is deliberate: a module-level import of a missing name
    would be a COLLECTION error (the Phase-4 exit criterion forbids those),
    and a literal `getattr(cli, "…")` trips ruff's B009. This keeps the RED
    reason a single clean `AttributeError` and keeps mypy green.
    """
    return getattr(cli, name)


def _scan(text: str):
    return _m27("scan_body_links")(text)


def _mask(text: str) -> str:
    return _m27("_mask_code")(text)


def _raws(text: str) -> list[str]:
    return [link.raw for link in _scan(text)]


# --- masking (D2) ---------------------------------------------------------
#
# Intended RED for this whole section: `_mask_code` lands in Phase 5
# (`AttributeError` via `_m27`).


_LENGTH_CASES = [
    "plain prose with no code at all\n",
    "before\n```\nfenced [a](x.md)\n```\nafter\n",
    "before\n~~~\nfenced [a](x.md)\n~~~\nafter\n",
    "an inline `span with [a](x.md)` and prose\n",
    "trailing fence never closed\n```\nstill open [a](x.md)\n",
    "unpaired ` backtick on a line\n",
    "",
    "\n\n\n",
]


@pytest.mark.parametrize("text", _LENGTH_CASES)
def test_mask_code_is_length_preserving(text: str) -> None:
    """D2: the mask has the same length AND a newline at every same offset.

    Length preservation is what keeps every `(start, end)` span an offset
    into the ORIGINAL text — the whole handoff to M28. Newline parity is the
    stronger half: an implementation that replaced a fenced block with a
    single space run of the right total length would satisfy `len` alone and
    silently move every subsequent line number.
    """
    masked = _mask(text)
    assert len(masked) == len(text), "the mask must be the same length as its input"
    assert [i for i, c in enumerate(masked) if c == "\n"] == [
        i for i, c in enumerate(text) if c == "\n"
    ], "every newline must survive at its original offset"


def test_mask_code_blanks_a_backtick_fenced_block() -> None:
    """A ``` fence's CONTENT is blanked; the fence lines themselves stay."""
    text = "intro\n```\n[a](gone.md)\n```\noutro [b](kept.md)\n"
    masked = _mask(text)
    assert "gone.md" not in masked
    assert "kept.md" in masked
    assert "```" in masked, "the fence marker lines are not themselves content"


def test_mask_code_blanks_a_tilde_fenced_block() -> None:
    """A ~~~ fence masks exactly like a ``` fence (D2 names both)."""
    text = "intro\n~~~\n[a](gone.md)\n~~~\noutro [b](kept.md)\n"
    masked = _mask(text)
    assert "gone.md" not in masked
    assert "kept.md" in masked


def test_mask_code_honours_a_longer_closing_fence() -> None:
    """D2: a fence is closed by the same character at EQUAL OR GREATER length.

    Both directions are asserted in one case: the inner three-backtick line
    does NOT close a four-backtick fence (shorter), and the four-backtick line
    does. Getting this wrong reopens the block early and unmasks code.
    """
    text = "````\n```\n[a](gone.md)\n````\nafter [b](kept.md)\n"
    masked = _mask(text)
    assert "gone.md" not in masked, "a shorter inner fence must not close the block"
    assert "kept.md" in masked, "the equal-or-longer fence must close the block"


def test_mask_code_accepts_up_to_three_leading_spaces_on_a_fence() -> None:
    """D2 / E5: the exact two-space-indented fence shape in `architecture.md`.

    `architecture.md`'s *Entry format* bullet indents its fence by two spaces
    and the fenced sample is literally `- [<path>](<path>) — …`. A fence rule
    anchored at column 0 would leave that sample unmasked — one of E5's four
    measured false positives.
    """
    text = (
        "- **Entry format.** One bullet per doc:\n"
        "  ```\n"
        "  - [<path>](<path>) — _role_ — <description>. Updated YYYY-MM-DD.\n"
        "  ```\n"
        "Both the link text and the href are the doc's path.\n"
    )
    assert "<path>" not in _mask(text)
    assert _scan(text) == ()


def test_mask_code_blanks_inline_code_spans() -> None:
    """D2: matched backtick runs of EQUAL length blank their contents."""
    text = "prose `[a](gone.md)` and ``[b](also-gone.md)`` and [c](kept.md)\n"
    masked = _mask(text)
    assert "gone.md" not in masked
    assert "also-gone.md" not in masked
    assert "kept.md" in masked


def test_mask_code_inline_span_does_not_cross_a_line() -> None:
    """A span never crosses a line boundary (Phase-1 contract point 3).

    Otherwise one unpaired backtick masks the remainder of a 112 KB `cli.md`
    — unbounded false negatives, the exact failure mode E6 exists to prevent.
    """
    text = "an unpaired ` backtick here\nand [a](kept.md) on the next line\n"
    masked = _mask(text)
    assert "kept.md" in masked
    assert _raws(text) == ["kept.md"]


def test_mask_code_leaves_every_unmasked_byte_untouched() -> None:
    """Only code CONTENT is replaced; every other byte is identical.

    Asserted as the EXACT expected mask rather than as substring probes: this
    is the one test that pins what "replaces the contents of code with spaces"
    means character by character — the fence marker lines survive, the fenced
    content and the inline span's interior become spaces of the same width,
    and nothing else moves.
    """
    text = "alpha [a](x.md)\n```\nsecret\n```\nomega `q` end\n"
    expected = "alpha [a](x.md)\n```\n      \n```\nomega ` ` end\n"
    assert _mask(text) == expected


def test_mask_code_does_not_mask_four_space_indented_prose() -> None:
    """E6 / Q3: there is deliberately NO 4-space indented-code rule.

    All nine 4-space-indented link-shaped spans in this repository are real
    links inside blockquote and list continuations, six of them genuinely
    broken. An indented-code rule would buy false negatives on live damage.
    """
    text = "> A quoted paragraph:\n>\n    See [the plan](plan.md) for context.\n"
    masked = _mask(text)
    assert masked == text, "4-space indentation is not code"
    assert _raws(text) == ["plan.md"]


def test_mask_code_unclosed_fence_masks_to_end_of_document() -> None:
    """D2: an UNCLOSED fence masks to the end of the document (CommonMark).

    The masker's job is to model what actually renders as a link. Every
    renderer these documents pass through takes an unterminated fence to EOF,
    so reporting a broken link inside one would flag something no reader ever
    sees as a link.

    This deliberately differs from the inline-span rule, which is bounded at a
    line: a lone backtick is a common, invisible accident in prose, so letting
    it run would buy unbounded false NEGATIVES, while an unclosed fence is
    rare, line-anchored, three or more characters wide and visually obvious.
    `_LENGTH_CASES[4]` is this exact shape and asserts only length and newline
    offsets, so without this test nothing pins which way it goes.
    """
    text = "trailing fence never closed\n```\nstill open [a](x.md)\nand [b](y.md) later\n"
    masked = _mask(text)
    assert "x.md" not in masked
    assert "y.md" not in masked, "the mask runs to the end of the document, not to the next line"
    assert masked.startswith("trailing fence never closed\n```\n")
    assert _scan(text) == ()


def test_mask_code_masks_fences_before_inline_spans() -> None:
    """D2: the ORDER is part of the contract — fences first, spans second.

    A stray unpaired backtick inside a fenced block must not open a span that
    swallows real prose after the block. This discriminates against the one
    wrong shape that would otherwise pass every other masking lock: multi-line
    inline spans evaluated BEFORE the fences, which would mask everything
    between the fence's stray backtick and the next backtick in the prose.
    """
    text = "```\ncode with a stray ` backtick\n```\nprose [a](kept.md) and a `span` after\n"
    masked = _mask(text)
    assert "kept.md" in masked
    assert _raws(text) == ["kept.md"]


def test_mask_code_e5_shapes_from_this_repository() -> None:
    """E5: every measured false-positive shape in this repository, verbatim.

    Without masking, the scan gains **4** false positives inside fenced code —
    `architecture.md:182`'s `[<path>](<path>)` — and **3** inside inline code
    spans. All three inline shapes are taken from the archived logs the setup
    census measured: `_format_entry`'s `[name](name)` output sample
    (`m1-parser-and-index-log.md:359`), the `[old-plan.md](old-plan.md)`
    broken-link diagnosis (`m2-mutating-verbs-log.md:114`), and the
    `[cli.md](cli.md)` prose-link example (`:523`). Every one must be silent.
    """
    fenced = "```\n- [<path>](<path>) — _role_ — <description>.\n```\n"
    inline_format_entry = "emits `- [name](name) — _role_ — desc. Updated YYYY-MM-DD.`.\n"
    inline_old_plan = "rendered as `[old-plan.md](old-plan.md)`\n— a broken link.\n"
    inline_cli = "such as `[cli.md](cli.md)` in doc bodies are left untouched.\n"
    assert _scan(fenced) == ()
    assert _scan(inline_format_entry) == ()
    assert _scan(inline_old_plan) == ()
    assert _scan(inline_cli) == ()


# --- grammar (D1) ---------------------------------------------------------
#
# Intended RED for this whole section: `scan_body_links` / `BodyLink` /
# `BODY_LINK_KINDS` land in Phase 5 (`AttributeError` via `_m27`).


def test_scan_finds_a_plain_inline_link() -> None:
    """The base case: one inline link, kind `inline`, raw + path + no fragment."""
    (link,) = _scan("See [the plan](plan.md) for context.\n")
    assert link.kind == "inline"
    assert link.raw == "plan.md"
    assert link.path == "plan.md"
    assert link.fragment is None


_SPAN_CASES = [
    ("plain", "[a](plan.md)", "plan.md"),
    ("angle", "[a](<my plan.md>)", "<my plan.md>"),
    ("double-quoted title", '[a](plan.md "The plan")', "plan.md"),
    ("single-quoted title", "[a](plan.md 'The plan')", "plan.md"),
    ("parenthesised title", "[a](plan.md (The plan))", "plan.md"),
    ("angle plus title", '[a](<my plan.md> "The plan")', "<my plan.md>"),
    ("balanced parens", "[a](a(b).md)", "a(b).md"),
    ("percent escape", "[a](my%20doc.md)", "my%20doc.md"),
    ("backslash escape", "[a](my\\ doc.md)", "my\\ doc.md"),
    ("fragment", "[a](plan.md#a-heading)", "plan.md#a-heading"),
    ("reference definition", "[plan]: plan.md\n", "plan.md"),
    ("reference definition, title", '[plan]: plan.md "The plan"\n', "plan.md"),
    ("reference definition, angle", "[plan]: <my plan.md>\n", "<my plan.md>"),
    ("leading whitespace", "[a]( plan.md)", "plan.md"),
    ("trailing whitespace", "[a](plan.md )", "plan.md"),
    ("title then trailing whitespace", '[a](plan.md "T" )', "plan.md"),
]


@pytest.mark.parametrize(
    ("label", "text", "expected"), _SPAN_CASES, ids=[c[0] for c in _SPAN_CASES]
)
def test_scan_span_is_exactly_the_destination_token(label: str, text: str, expected: str) -> None:
    """D5 — THE M28 handoff invariant: `text[link.start:link.end] == link.raw`.

    The span INCLUDES the `<…>` angle brackets, EXCLUDES any title, and
    excludes the optional whitespace either side of the destination (rule 3).
    Excluding the brackets would break M28 the moment it splices a
    destination containing a space: the replacement would land outside the
    delimiters and the link would stop parsing. This is the single
    highest-leverage assertion in the milestone.

    The prefix deliberately carries **both** kinds of masked region. Masking is
    length-preserving precisely so that offsets stay offsets into the ORIGINAL
    text; a prefix of plain prose would let an implementation that reported
    offsets into the *masked* string pass every case here, since the two
    strings agree wherever nothing is masked.
    """
    prefix = "intro\n\n```\nfenced [x](masked.md)\n```\n\nan `inline [y](span.md)` too\n\n"
    body = prefix + text
    (link,) = _scan(body)
    assert link.raw == expected, label
    assert body[link.start : link.end] == link.raw, "the span must BE the destination token"
    assert link.end > link.start
    assert link.line == body[: link.start].count("\n") + 1
    assert link.column == link.start - (body.rfind("\n", 0, link.start) + 1) + 1


def test_scan_angle_bracket_destination() -> None:
    """D1: `<…>` allows whitespace; the brackets are part of `raw`, not `path`."""
    (link,) = _scan("See [it](<my plan.md>).\n")
    assert link.raw == "<my plan.md>"
    assert link.path == "my plan.md"


def test_scan_angle_destination_does_not_cross_a_newline() -> None:
    """D1 rule 4: a newline inside `<…>` TERMINATES the candidate.

    Without this bound an unclosed `<` swallows forward until the next `>`
    anywhere in the document, which is how a bounded scanner turns into an
    unbounded one. The rule is stated in `cli.md` and locked here; the
    pathological-input case covers the unterminated-with-no-newline shape,
    which is a different failure mode.
    """
    assert _scan("[a](<my\nplan.md>)\n") == ()
    assert _raws("[a](<my plan.md>)\n[b](<other\nplan.md>)\n") == ["<my plan.md>"], (
        "the terminated angle destination survives; the newline-crossing one does not"
    )


@pytest.mark.parametrize(
    "text",
    ['[a](plan.md "T")', "[a](plan.md 'T')", "[a](plan.md (T))"],
    ids=["double", "single", "paren"],
)
def test_scan_title_in_all_three_quotings(text: str) -> None:
    """D1: all three title quotings are recognised and none joins the span."""
    (link,) = _scan(text + "\n")
    assert link.raw == "plan.md"
    assert link.path == "plan.md"


def test_scan_title_requires_whitespace_after_the_destination() -> None:
    """D1 rule 5: a title needs **at least one whitespace character** after the
    destination.

    Only an angle destination can reach the question: a plain destination ends
    *at* whitespace or at the closing `)`, so `[a](plan.md"T")` is simply a
    destination spelled `plan.md"T"` and the clause is unobservable. After a
    `<…>` destination it is observable, and it changes the record M28
    consumes — `[a](<x.md>"T")` is not a recognised link at all, rather than a
    link whose title happens to be unseparated.

    Added by the Step-2 same-instance audit, which found the implementation
    accepting the unseparated form against the frozen rule. No occurrence
    exists in `docs/`, the 39 fixture trees, or the bundled skill, so the
    correction is behaviour-neutral on every real input — which is exactly why
    only reading the contract could catch it.
    """
    assert _scan('[a](<x.md>"T")\n') == ()
    assert _scan("[a](<x.md>'T')\n") == ()
    assert _scan("[a](<x.md>(T))\n") == ()
    assert _scan('[plan]: <x.md>"T"\n') == ()

    assert _raws('[a](<x.md> "T")\n') == ["<x.md>"], "one space is enough"
    assert _raws('[plan]: <x.md> "T"\n') == ["<x.md>"]
    assert _raws("[a](<x.md>)\n") == ["<x.md>"], "a bare angle destination still closes"
    assert _raws("[plan]: <x.md>\n") == ["<x.md>"]


def test_scan_destination_ends_at_first_unescaped_whitespace() -> None:
    """D1 rule 3 + rule 5: whitespace ends the destination, and what follows
    must be a title or nothing — a bare extra token is not a link at all.
    """
    (link,) = _scan('[a](plan.md "The plan")\n')
    assert link.raw == "plan.md"
    assert _scan("[a](plan.md extra)\n") == (), "a non-title trailer is not a recognised link"


def test_scan_balanced_parens_to_the_frozen_depth() -> None:
    """D1 rule 3: balanced parens nest to `MAX_DESTINATION_PAREN_DEPTH` = 3.

    The bound is a docs-cli bounded-scanner bound, NOT a CommonMark
    conformance claim.
    """
    assert _m27("MAX_DESTINATION_PAREN_DEPTH") == 3
    (link,) = _scan("[a](a(b(c(d))).md)\n")
    assert link.raw == "a(b(c(d))).md"


def test_scan_rejects_parens_beyond_the_frozen_depth() -> None:
    """One level past the bound is not a recognised link — silence, not a guess."""
    assert _scan("[a](a(b(c(d(e)))).md)\n") == ()


def test_scan_rejects_unbalanced_parens_in_a_plain_destination() -> None:
    """D1 rule 3: parentheses are honoured only when BALANCED."""
    assert _scan("[a](foo(bar.md)\n") == ()


def test_scan_backslash_escape_opts_a_span_out() -> None:
    """D1 rule 7 / Q3 mitigation: an escaped `[` always opts a span out.

    This is the author's inline alternative to fencing a code sample, and
    `convention.md` promises it.
    """
    assert _scan("Not a link: \\[x](y.md)\n") == ()


def test_scan_backslash_escapes_inside_the_destination() -> None:
    """D1 rule 7: `raw` keeps the escapes; `path` is unescaped.

    The space leg is what makes `\\ ` work at all — a destination ends at the
    first *unescaped* whitespace.
    """
    (spaced,) = _scan("[a](my\\ doc.md)\n")
    assert spaced.raw == "my\\ doc.md"
    assert spaced.path == "my doc.md"

    (parens,) = _scan("[a](weird\\(x\\).md)\n")
    assert parens.raw == "weird\\(x\\).md"
    assert parens.path == "weird(x).md"


def test_scan_percent_escape_is_decoded_in_path_not_in_raw() -> None:
    """D1 rule 8: the finding reports what the author wrote; resolution decodes."""
    (link,) = _scan("[a](my%20doc.md)\n")
    assert link.raw == "my%20doc.md", "the reported spelling is the raw one"
    assert link.path == "my doc.md", "resolution happens on the decoded path"


def test_scan_percent_escape_that_is_invalid_passes_through() -> None:
    """D1 rule 8: an invalid percent sequence is left alone rather than raising."""
    (link,) = _scan("[a](100%25-done.md)\n")
    assert link.path == "100%-done.md"
    (bad,) = _scan("[a](50%-off.md)\n")
    assert bad.path == "50%-off.md"


def test_scan_percent_encoded_hash_is_not_a_fragment_delimiter() -> None:
    """BINDING decode order, consequence 1: the `#` split happens on the RAW
    text, so a percent-encoded `%23` decodes into the PATH and never delimits
    a fragment.

    This is the highest-value lock on the frozen order. The natural
    implementation — `unquote()` first, then `split("#", 1)` — inverts it and
    would report this destination as `path == "plan"` with
    `fragment == "x.md"`, i.e. it would go looking for a file named `plan`.
    Every other percent-escape and fragment test in this module passes under
    both orders, because none of them contains a `%` and a `#` at once.
    """
    (link,) = _scan("[a](plan%23x.md)\n")
    assert link.raw == "plan%23x.md"
    assert link.path == "plan#x.md"
    assert link.fragment is None


def test_scan_percent_encoded_slash_is_a_path_separator() -> None:
    """BINDING decode order, consequence 2: `%2F` decodes BEFORE the join, so
    it really is a path separator once resolution happens.

    Stated in `cli.md` alongside its `%23` sibling; the two are the same
    decision seen from opposite sides, and an implementation that decoded
    neither would pass the `%23` lock while failing this one.
    """
    (link,) = _scan("[a](sub%2Fx.md)\n")
    assert link.raw == "sub%2Fx.md"
    assert link.path == "sub/x.md"
    assert _normalise("doc.md", link.path) == "sub/x.md"


def test_scan_backslash_cannot_escape_the_fragment_delimiter() -> None:
    """BINDING decode order, consequence 3: the split precedes unescaping, so
    `\\#` does NOT keep the `#` out of the fragment.

    Surprising, deliberate, and stated in `cli.md` — the same mechanism as
    `%23`, seen from the escape side. The left half is then unescaped on its
    own, and a trailing `\\` before nothing is a literal backslash (rule 7).
    """
    (link,) = _scan("[a](plan\\#x.md)\n")
    assert link.raw == "plan\\#x.md"
    assert link.fragment == "x.md"
    assert link.path == "plan\\"


def test_scan_fragment_splits_on_the_first_hash() -> None:
    """D3: the split is on the FIRST `#`; everything after it is the fragment."""
    (link,) = _scan("[a](plan.md#a#b)\n")
    assert link.path == "plan.md"
    assert link.fragment == "a#b"


def test_scan_fragment_is_none_when_absent() -> None:
    """`None` when absent, and the empty string for a bare trailing `#`."""
    (none,) = _scan("[a](plan.md)\n")
    assert none.fragment is None
    (empty,) = _scan("[a](plan.md#)\n")
    assert empty.fragment == ""
    assert empty.path == "plan.md"


def test_scan_reference_definition() -> None:
    """D1 rule 6 / Q2: a reference DEFINITION carries a destination, so it is
    validated; its `kind` distinguishes it and nothing else does.
    """
    (link,) = _scan('intro\n\n[plan]: plan.md "The plan"\n')
    assert link.kind == "reference-definition"
    assert link.raw == "plan.md"
    assert link.path == "plan.md"


@pytest.mark.parametrize(
    "text",
    [
        "prose then [plan]: plan.md\n",
        "     [plan]: plan.md\n",
    ],
    ids=["not-at-line-start", "four-leading-spaces"],
)
def test_scan_reference_definition_requires_the_line_anchor(text: str) -> None:
    """D1 rule 6: line-anchored, 0–3 leading spaces. Anything else is prose."""
    assert _scan(text) == ()


def test_scan_reference_definition_destination_must_start_on_the_label_line() -> None:
    """D1 rule 6(a): the "optional whitespace" after `[label]:` never spans a
    newline.

    The rule is line-anchored end to end, which is what keeps the scanner
    bounded — otherwise a bare `[label]:` at the end of a document would send
    the scan hunting forward for a destination. M28 consumes this output, so
    the answer matters even where the finding set does not change.
    """
    assert _scan("[plan]:\nplan.md\n") == ()


def test_scan_reference_definition_trailing_remainder_disqualifies() -> None:
    """D1 rule 6(b): after the destination only whitespace and at most one
    title may appear before the end of the line — the same rule the inline
    form applies (rule 5), stated once and referenced rather than duplicated.
    """
    assert _scan("[plan]: plan.md and more\n") == ()
    assert _raws('[plan]: plan.md "The plan"   \n') == ["plan.md"]


def test_scan_reference_definition_with_an_empty_destination_is_not_recognised() -> None:
    """D1 rule 6(c): `[plan]:` with nothing after it yields NO `BodyLink`.

    Not a `BodyLink` carrying an empty `raw`, which would hand M28 a
    zero-width span to splice into. `classify_destination("")` exists for the
    inline `[a]()` form, which is a real link with an empty destination; a
    reference definition with no destination is simply not one.
    """
    assert _scan("[plan]:\n") == ()
    assert _scan("[plan]:   \n") == ()


def test_scan_ignores_an_image() -> None:
    """D1 / Q2: images are a SCOPED exclusion — one character, one decision."""
    assert _scan("![diagram](d.png)\n") == ()


def test_scan_ignores_an_image_but_still_finds_a_following_link() -> None:
    """The `!` rejection must not swallow a real link later on the same line."""
    assert _raws("![diagram](d.png) and [a](plan.md)\n") == ["plan.md"]


def test_scan_finds_a_link_nested_inside_an_image_label() -> None:
    """D1 rule 2 skips the IMAGE, not whatever its label contains.

    In `![a [b](c.md)](d.png)` the inner `[` is preceded by a space, not by an
    unescaped `!`, so by rules 1 and 2 `[b](c.md)` is an otherwise-recognised
    inline link and must be reported. Resuming the outer scan at the rejected
    image's `]` swallows it silently — which is exactly the one case the
    Phase-1 linearity note carves out ("the image (`!`) rejection … does
    depend on the opening `[`"), and it is the case where a missed span means
    **M28 never rewrites that destination**.

    Added by the Step-2 same-instance audit; the fix resumes at `i + 1` while
    reusing the cached closing bracket, so the bound stays linear.
    """
    assert _raws("![a [b](c.md)](d.png)\n") == ["c.md"]
    assert _scan("![a b](d.png)\n") == (), "a plain image is still skipped"


def test_scan_ignores_an_autolink() -> None:
    """D1: autolinks are out of the grammar — both URL and path shaped."""
    assert _scan("See <https://example.com> and <plan.md>.\n") == ()


def test_scan_ignores_a_raw_html_anchor() -> None:
    """D1: raw HTML is out of the grammar (a stdlib-only tool parses no HTML)."""
    assert _scan('<a href="plan.md">the plan</a>\n') == ()


@pytest.mark.parametrize(
    "text",
    ["a [plan] use\n", "a [plan][] use\n", "a [x][plan] use\n"],
    ids=["shortcut", "collapsed", "full"],
)
def test_scan_ignores_reference_uses(text: str) -> None:
    """D1 / Q2: a reference USE carries no destination; the definition is what
    gets validated, so validating the use would double-report or invent a path.
    """
    assert _scan(text) == ()


def test_scan_multi_line_label() -> None:
    """Phase-1 contract point 1: a label may wrap, but never across a blank line.

    This is the exact shape `convention.md` uses for its exclusion
    cross-reference — a real, resolving, load-bearing link. Excluding wrapped
    labels would make M27 blind to a link **M28 must rewrite**, so when
    `cli.md` later moves, M28 would silently leave it broken while M27
    reported damage its sibling caused but could not see.
    """
    text = (
        'see [`cli.md`\'s "Common: exclusion"\nsection](cli.md#common-exclusion) for the shape.\n'
    )
    (link,) = _scan(text)
    assert link.raw == "cli.md#common-exclusion"
    assert link.path == "cli.md"
    assert link.fragment == "common-exclusion"
    assert link.line == 2, "the position is the DESTINATION token's, not the label's"


def test_scan_label_scan_stops_at_a_blank_line() -> None:
    """Phase-1 contract point 1: the closing `]` scan is bounded at a blank line."""
    assert _scan("an unclosed [label\n\nsection](plan.md)\n") == ()


def test_scan_label_ends_at_its_first_unescaped_bracket() -> None:
    """Phase-1 contract point 2: balanced brackets inside a label are an
    explicit, escapable exclusion — a bounded grammar, stated as such.
    Verified zero occurrences across `docs/`, the 33 fixture trees, and the
    bundled skill, so it costs nothing today.
    """
    assert _scan("[a [b] c](x.md)\n") == ()
    assert _raws("[a \\[b\\] c](x.md)\n") == ["x.md"]


def test_scan_two_links_on_one_line_get_distinct_columns() -> None:
    """One finding per OCCURRENCE means occurrences must be distinguishable."""
    first, second = _scan("[a](one.md) then [b](two.md)\n")
    assert (first.raw, second.raw) == ("one.md", "two.md")
    assert first.line == second.line == 1
    assert first.column < second.column


def test_scan_line_and_column_are_one_based() -> None:
    """`line` / `column` locate the destination token's FIRST character, 1-based.

    The document deliberately carries a fenced block and an inline span BEFORE
    the link, because masking is length-preserving precisely so positions
    survive it: an implementation that dropped or collapsed masked regions
    before scanning would report line 3 here instead of line 7, and would hand
    M28 spans that no longer index the original text.
    """
    text = (
        "# Title\n"  # 1
        "\n"  # 2
        "```\n"  # 3
        "[x](masked.md)\n"  # 4
        "```\n"  # 5
        "\n"  # 6
        "See `[y](span.md)` and [the plan](plan.md).\n"  # 7
    )
    (link,) = _scan(text)
    assert link.line == 7
    assert link.column == len("See `[y](span.md)` and [the plan](") + 1
    lines = text.split("\n")
    assert lines[link.line - 1][link.column - 1 :].startswith(link.raw)
    assert text[link.start : link.end] == link.raw


def test_scan_is_deterministic() -> None:
    """The scanner is a pure function of the text — same input, same tuple."""
    text = "[a](one.md)\n\n```\n[b](masked.md)\n```\n\n[c](two.md#f)\n"
    assert _scan(text) == _scan(text)


def test_scan_masks_code_before_matching() -> None:
    """D2: masking is not a post-filter — the scanner never sees code at all."""
    assert _scan("```\n[a](inside.md)\n```\n") == ()


def test_scan_reports_every_local_destination_including_escapes() -> None:
    """D5: the scanner reports EVERY recognised occurrence, in-root or not.

    Containment is the rule's job, not the scanner's — that split is what
    lets `outside-root-body-link` exist at all, and what M28 consumes.
    """
    assert _raws("[a](../outside.md) and [b](https://x) and [c](in.md)\n") == [
        "../outside.md",
        "https://x",
        "in.md",
    ]


def test_body_link_kinds_are_frozen() -> None:
    """Exactly two kinds; a third would mean a grammar change, not a tweak."""
    assert _m27("BODY_LINK_KINDS") == frozenset({"inline", "reference-definition"})


def test_body_link_record_is_immutable() -> None:
    """D5: `BodyLink` is a FROZEN dataclass, and that is part of the handoff.

    M28 collects spans, then splices replacements into the original text. A
    mutable record invites an in-place edit of `raw` or `start` between those
    two steps, after which every remaining span in the same document is
    silently wrong. `frozen=True` makes that a `TypeError` at the moment of
    the mistake instead of a corrupted rewrite.
    """
    (link,) = _scan("[a](plan.md)\n")
    assert isinstance(link, _m27("BodyLink"))
    with pytest.raises(dataclasses.FrozenInstanceError):
        link.raw = "other.md"


# --- destination classification (D2) --------------------------------------


def test_destination_kinds_are_frozen() -> None:
    """The six kinds are closed; only `local` is ever resolved or reported."""
    assert _m27("DESTINATION_KINDS") == frozenset(
        {"local", "empty", "fragment", "scheme", "protocol-relative", "root-absolute"}
    )


def _classify(raw: str) -> str:
    return _m27("classify_destination")(raw)


@pytest.mark.parametrize(
    "raw",
    ["a.md", "./a.md", "../a.md", "sub/a.md", "a.md#f", "a", "data.yaml", "sub/", "<my a.md>"],
)
def test_classify_local(raw: str) -> None:
    """Everything that is not one of the five named exclusions is `local` —
    including a `../` escape, which the RULE (not the scanner) then rejects.
    """
    assert _classify(raw) == "local"


def test_classify_empty() -> None:
    assert _classify("") == "empty"


def test_classify_fragment_only() -> None:
    """A `#section` link is same-document navigation; there is no path to check."""
    assert _classify("#section") == "fragment"
    assert _classify("<#section>") == "fragment", "the angle pair is stripped first"


def test_classify_runs_on_the_token_as_written_not_decoded() -> None:
    """Classification never decodes first, so `%23x` is `local`, not `fragment`.

    Stated in `cli.md` beside the BINDING decode order, and the same decision
    as `test_scan_percent_encoded_hash_is_not_a_fragment_delimiter` seen at
    the classification seam: an implementation that ran `unquote()` before
    classifying would silence this destination entirely instead of resolving
    it against a file named `#x`.
    """
    assert _classify("%23x") == "local"
    assert _classify("%2Fabs.md") == "local", "a decoded leading slash is not root-absolute either"


@pytest.mark.parametrize(
    "raw",
    ["https://x", "mailto:a@b", "file:///tmp/x", "HTTPS://X", "C:\\docs\\plan.md", "<https://x>"],
)
def test_classify_schemed(raw: str) -> None:
    """Any RFC-3986-shaped `scheme:` prefix, case-insensitive.

    `C:\\…` is therefore scheme-shaped and silent — deliberate, and stated in
    `cli.md` so it is not mistaken for a gap. `<https://x>` is the autolink
    *shape* written as a destination: the angle pair is stripped BEFORE
    classification, or it would classify as `local` and be resolved as a path.
    """
    assert _classify(raw) == "scheme"


def test_classify_protocol_relative() -> None:
    """`//host/path` is tested BEFORE `/path`, or it would read as root-absolute."""
    assert _classify("//host/x") == "protocol-relative"


def test_classify_root_absolute() -> None:
    """`/path` names a web-server root, not a filesystem path."""
    assert _classify("/root-absolute.md") == "root-absolute"


# --- resolution and containment (D3 / D4b) --------------------------------


def _normalise(doc_rel: str, dest_path: str) -> str:
    return _m27("normalise_body_link_target")(doc_rel, dest_path)


def _contained(candidate: str) -> bool:
    return _m27("_body_link_is_contained")(candidate)


def test_normalise_joins_against_the_referring_documents_directory() -> None:
    """D3: the resolution base is the referring DOCUMENT's directory.

    The single most important difference from `Related:`, whose targets are
    root-relative. The helper takes the document's root-relative path and
    drops the last segment itself, so callers never pre-compute a directory.
    """
    assert _normalise("doc.md", "plan.md") == "plan.md"
    assert _normalise("sub/deep.md", "plan.md") == "sub/plan.md"
    assert _normalise("sub/deep.md", "../plan.md") == "plan.md"
    assert _normalise("archive/2026-01-01/old-log.md", "plan.md") == "archive/2026-01-01/plan.md"
    assert _normalise("archive/2026-01-01/old-log.md", "../../plan.md") == "plan.md"
    assert _normalise("doc.md", "./plan.md") == "plan.md"


def test_normalise_is_lexical_and_never_touches_the_filesystem() -> None:
    """D4b: containment is decided by path arithmetic ALONE.

    Sentinels over `Path.exists` / `Path.is_file` / `Path.resolve` raise if
    the helper reaches for the filesystem. This is the hermeticity property
    stated as a unit test: the verdict must be a function of two strings.
    """

    def _boom(*args: object, **kwargs: object) -> object:
        raise AssertionError("normalisation must not touch the filesystem")

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(Path, "exists", _boom)
        mp.setattr(Path, "is_file", _boom)
        mp.setattr(Path, "resolve", _boom)
        assert _normalise("sub/deep.md", "../plan.md") == "plan.md"
        assert _contained("plan.md") is True
        assert _contained("../plan.md") is False


def test_dotdot_escape_then_return_normalises_back_under_the_root() -> None:
    """D3: `../sub/../back-inside.md` lands back under the root — CONTAINED.

    Judged on the lexically normalised path, so the answer cannot vary with
    filesystem state.
    """
    candidate = _normalise("sub/deep.md", "../sub/../back-inside.md")
    assert candidate == "back-inside.md"
    assert _contained(candidate) is True


def test_containment_ignores_symlinks_and_uses_the_lexical_form(tmp_path: Path) -> None:
    """D3: `Path.resolve()` is NOT used, and this arrangement proves it.

    `root/sub` is a symlink to a directory OUTSIDE the root. Lexically,
    `sub/deep.md`'s `../inside.md` is `inside.md` — contained and resolving.
    Under a `resolve()`-based test the document would live at
    `elsewhere/deep.md`, so `../inside.md` would land outside the root and be
    reported. The two answers are opposite, which is what makes this a lock
    rather than a restatement.
    """
    root = tmp_path / "tree"
    elsewhere = tmp_path / "elsewhere"
    root.mkdir()
    elsewhere.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "tree"\n')
    (root / "inside.md").write_text("# Inside\n\nLifecycle: active\nRole: notes\n")
    (root / "sub").symlink_to(elsewhere, target_is_directory=True)
    doc = root / "sub" / "deep.md"
    text = (
        "# Deep\n\nLifecycle: active\nRole: notes\nProject: tree\n"
        "Updated: 2026-01-01\n\nSee [inside](../inside.md).\n"
    )
    doc.write_text(text)

    assert _m27("body_link_findings")(doc, text, root) == []


def test_containment_treats_the_root_itself_as_contained() -> None:
    """Phase-1 contract point 11: `sub/..` normalises to `.`, which is the root
    directory — an existing entry (Q7), so contained and satisfied. `.`
    therefore never appears in either message.
    """
    assert _normalise("sub/deep.md", "..") == "."
    assert _contained(".") is True


def test_containment_rejects_dotdot_and_dotdot_prefix() -> None:
    """The predicate is byte-for-byte `docs archive`'s `outside-root` test:
    the candidate escapes iff it IS `..` or starts with `../`.

    `..foo.md` is the discriminating case. A predicate written
    `startswith("..")` — the obvious near-miss — would report a perfectly
    ordinary in-root file whose name happens to begin with two dots as leaving
    the tree, which is an over-fire with no repair available to the author.
    """
    assert _contained("..") is False
    assert _contained("../plan.md") is False
    assert _contained("../../src/x.py") is False
    assert _contained("a/b.md") is True
    assert _contained("..foo.md") is True, "a filename starting with '..' is not an escape"
    assert _contained("sub/..foo.md") is True


# --- body_link_findings (D4 / D4b) ----------------------------------------


def _findings(path: Path, text: str, root: Path) -> list[Finding]:
    return _m27("body_link_findings")(path, text, root)


def _tiny_root(tmp_path: Path, name: str = "bodyprobe") -> Path:
    root = tmp_path / name
    root.mkdir()
    (root / ".docs.toml").write_text(f'[project]\nname = "{name}"\n')
    return root


_ARCHIVED_TEXT = (
    "# Old Log\n"  # 1
    "\n"  # 2
    "Lifecycle: archived\n"  # 3
    "Role: log\n"  # 4
    "Project: bodyprobe\n"  # 5
    "Updated: 2026-01-01\n"  # 6
    "Archived-reason: completed\n"  # 7
    "\n"  # 8
    "## Body\n"  # 9
    "\n"  # 10
    "Historical prose.\n"  # 11
    "See [the plan](plan.md) for context.\n"  # 12
)


def test_body_link_findings_one_finding_per_occurrence(tmp_path: Path) -> None:
    """D4: per OCCURRENCE, not per distinct destination.

    Three broken `[x](plan.md)` links on three lines are three repairs, and
    the line number is what makes each one actionable.
    """
    root = _tiny_root(tmp_path)
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\nUpdated: 2026-01-01\n\n"
        "[a](plan.md)\n[b](plan.md)\n[c](plan.md)\n"
    )
    findings = _findings(root / "doc.md", text, root)
    assert len(findings) == 3
    assert {f.rule for f in findings} == {"broken-body-link"}
    assert [f.severity for f in findings] == ["error"] * 3
    assert [f.path for f in findings] == [root / "doc.md"] * 3
    assert [f.message.split()[4] for f in findings] == ["8", "9", "10"]


def test_body_link_findings_frozen_broken_message(tmp_path: Path) -> None:
    """The frozen `broken-body-link` template, asserted verbatim.

    This is `cli.md`'s worked instance byte for byte, including the E1/E2
    un-rebased archive shape it was drawn from. Phase-1 amendment 1: D4's
    `does not resolve to a file:` was retired because it contradicts the
    operator-binding Q7 — a DIRECTORY satisfies a destination too.

    Line **12** is also the lock on Phase-1 contract point 10: the scan runs
    over the WHOLE document text, with offsets into the original. A scanner
    fed `parse_metadata_block`'s body instead would report this same link at
    line 4, and every span it handed M28 would be off by the height of the
    metadata block.
    """
    root = _tiny_root(tmp_path)
    doc = root / "archive" / "2026-01-01" / "old-log.md"
    doc.parent.mkdir(parents=True)
    doc.write_text(_ARCHIVED_TEXT)

    (finding,) = _findings(doc, _ARCHIVED_TEXT, root)
    assert finding.rule == "broken-body-link"
    assert finding.severity == "error"
    assert finding.path == doc
    assert finding.message == (
        "body link at line 12 does not resolve to an existing path: plan.md "
        "(resolves to archive/2026-01-01/plan.md)"
    )


def test_body_link_findings_frozen_outside_root_message(tmp_path: Path) -> None:
    """The frozen `outside-root-body-link` template, asserted verbatim.

    Phase-1 amendment 2: D4b named the rule, its severity, exit code,
    granularity and precedence but gave NO message, so this template is
    specified in Phase 1 and asserted here. The trailing clause names the
    repair, mirroring `missing-inverse`'s `(or remove the edge)`.
    """
    root = _tiny_root(tmp_path)
    text = (
        "# Doc\n"  # 1
        "\n"  # 2
        "Lifecycle: active\n"  # 3
        "Role: notes\n"  # 4
        "Project: bodyprobe\n"  # 5
        "Updated: 2026-01-01\n"  # 6
        "\n"  # 7
        "## Body\n"  # 8
        "\n"  # 9
        "See [the glossary](../shared/glossary.md).\n"  # 10
    )
    (finding,) = _findings(root / "doc.md", text, root)
    assert finding.rule == "outside-root-body-link"
    assert finding.severity == "error"
    assert finding.message == (
        "body link at line 10 leaves the docs root: ../shared/glossary.md "
        "(normalises to ../shared/glossary.md); links outside the tree must be URLs"
    )


def test_body_link_findings_candidate_prints_even_when_it_equals_raw(tmp_path: Path) -> None:
    """`<candidate>` prints UNCONDITIONALLY — no "it depends" cell (M26's rule).

    A root-level document's `plan.md` normalises to `plan.md`, so the
    parenthetical is redundant on exactly the commonest case. It stays,
    because a template with a conditional tail is a template two things can
    drift apart in.
    """
    root = _tiny_root(tmp_path)
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\n"
        "Updated: 2026-01-01\n\n[a](plan.md)\n"
    )
    (finding,) = _findings(root / "doc.md", text, root)
    assert finding.message.endswith("plan.md (resolves to plan.md)")


def test_body_link_findings_containment_wins_over_existence(tmp_path: Path) -> None:
    """BINDING: containment is tested BEFORE existence, so the two rules never
    double-report.

    The escaping destination here names a path that genuinely EXISTS on disk
    (the sibling tree's own file), and the in-root one names a path that does
    not. Exactly one finding is produced for each, and the escaping one is
    `outside-root-body-link` ONLY — deciding whether it is broken would need
    precisely the stat the boundary forbids.
    """
    sibling = tmp_path / "sibling"
    sibling.mkdir()
    (sibling / "real.md").write_text("# Real\n")
    root = _tiny_root(tmp_path)
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\nUpdated: 2026-01-01\n\n"
        "[a](../sibling/real.md)\n[b](missing.md)\n"
    )
    findings = _findings(root / "doc.md", text, root)
    assert [f.rule for f in findings] == ["outside-root-body-link", "broken-body-link"]
    assert len([f for f in findings if f.rule == "broken-body-link"]) == 1


def test_body_link_findings_never_stats_outside_the_root(tmp_path: Path) -> None:
    """D4b: the rule never stats, opens, or follows anything outside the root.

    A `Path.exists` SPY records every probed path; every one must be under the
    root. This is the real "never stat" lock — the `bodylink-outside-root`
    fixture's by-construction version (a destination that cannot exist) is its
    complement, not its substitute: a fixture cannot prove the absence of a
    probe, only that a probe would have failed.

    Both `Path.exists` and `Path.is_file` are spied, so the lock does not
    depend on which of the two the existence test happens to call, and
    `assert probed` is what stops it passing vacuously on an implementation
    that never probes at all.

    Each probed path is **lexically normalised before** the containment
    comparison. `Path.is_relative_to` is a pure prefix test, so
    `Path("/root/../../etc/passwd").is_relative_to(Path("/root"))` is `True` —
    exactly the probe this lock exists to forbid would have been classified as
    inside the root.
    """
    root = _tiny_root(tmp_path)
    (root / "here.md").write_text("# Here\n")
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\nUpdated: 2026-01-01\n\n"
        "[a](../../../etc/passwd) [b](../sibling/real.md) [c](here.md) [d](gone.md)\n"
    )
    probed: list[Path] = []
    real_exists = Path.exists
    real_is_file = Path.is_file

    def _spy_exists(self: Path, *args: object, **kwargs: object) -> bool:
        probed.append(self)
        return real_exists(self)

    def _spy_is_file(self: Path, *args: object, **kwargs: object) -> bool:
        probed.append(self)
        return real_is_file(self)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(Path, "exists", _spy_exists)
        mp.setattr(Path, "is_file", _spy_is_file)
        findings = _findings(root / "doc.md", text, root)

    assert [f.rule for f in findings] == [
        "outside-root-body-link",
        "outside-root-body-link",
        "broken-body-link",
    ]
    assert probed, "the in-root destinations must actually be probed"
    outside = [p for p in probed if not Path(os.path.normpath(p)).is_relative_to(root)]
    assert outside == [], f"docs check must never stat outside its own root, got {outside!r}"


def test_body_link_findings_never_stats_an_encoded_absolute_path(tmp_path: Path) -> None:
    """D4b: an ENCODED leading slash must not smuggle a probe outside the root.

    The hole this closes, in order: classification runs on the token **as
    written** (D2), so `%2Fetc/passwd` and `\\/etc/passwd` are `local`, not
    `root-absolute`; the BINDING decode order then turns both into
    `/etc/passwd`; `posixpath.join` lets an absolute right-hand side win, so
    the candidate IS `/etc/passwd`; and a containment predicate testing only
    `..` / `../` calls that contained. `root / "/etc/passwd"` is
    `/etc/passwd`, so `docs check` stats a path outside the tree it was
    pointed at — the single thing D4b exists to forbid, and a verdict that
    varies with what happens to sit beside the checkout.

    M27's Phase-1 point 9 dropped `_candidate_exclusion_reason`'s leading-`/`
    leg on the reasoning that classification silences root-absolute
    destinations first. That is true only of a slash written literally, which
    is why the literal case below stays silent while the two encoded ones are
    now reported. Found and fixed by the Step-2 same-instance audit.
    """
    root = _tiny_root(tmp_path)
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\nUpdated: 2026-01-01\n\n"
        "[a](%2Fetc/passwd)\n[b](\\/etc/passwd)\n[c](/etc/passwd)\n"
    )
    probed: list[Path] = []
    real_exists = Path.exists
    real_is_file = Path.is_file

    def _spy_exists(self: Path, *args: object, **kwargs: object) -> bool:
        probed.append(self)
        return real_exists(self)

    def _spy_is_file(self: Path, *args: object, **kwargs: object) -> bool:
        probed.append(self)
        return real_is_file(self)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(Path, "exists", _spy_exists)
        mp.setattr(Path, "is_file", _spy_is_file)
        findings = _findings(root / "doc.md", text, root)

    assert [f.rule for f in findings] == ["outside-root-body-link"] * 2, (
        "both encoded spellings escape the root and must be REPORTED, never probed"
    )
    assert [f.message.split(": ", 1)[1].split(" ")[0] for f in findings] == [
        "%2Fetc/passwd",
        "\\/etc/passwd",
    ], "the finding names the destination exactly as written"
    outside = [p for p in probed if not Path(os.path.normpath(p)).is_relative_to(root)]
    assert outside == [], f"docs check must never stat outside its own root, got {outside!r}"
    assert _contained("/etc/passwd") is False
    assert _contained("/") is False


def test_body_link_findings_source_order_is_line_then_column(tmp_path: Path) -> None:
    """D4: within the block, findings are emitted in source order."""
    root = _tiny_root(tmp_path)
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\nUpdated: 2026-01-01\n\n"
        "[b](two.md) and [a](one.md)\n[c](three.md)\n"
    )
    findings = _findings(root / "doc.md", text, root)
    assert [f.message.split(": ")[1].split(" ")[0] for f in findings] == [
        "two.md",
        "one.md",
        "three.md",
    ]


def test_body_link_findings_source_order_interleaves_the_two_rules(tmp_path: Path) -> None:
    """D4: source order means SOURCE order — not grouped by rule.

    The broken destination comes FIRST here and the escaping one second, which
    is the case no other test covers: every other mixed-rule fixture and unit
    case happens to put the escape first, so an implementation that emitted
    every `outside-root-body-link` and then every `broken-body-link` would
    satisfy all of them. `cli.md` freezes source order (line, then column), and
    an agent walking a document top to bottom to repair it needs exactly that.
    """
    root = _tiny_root(tmp_path)
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\nUpdated: 2026-01-01\n\n"
        "[a](missing.md) then [b](../escapes.md)\n"
    )
    findings = _findings(root / "doc.md", text, root)
    assert [f.rule for f in findings] == ["broken-body-link", "outside-root-body-link"], (
        "findings follow the source, not the rule id"
    )
    assert "missing.md" in findings[0].message
    assert "../escapes.md" in findings[1].message


def test_body_link_findings_directory_destination_resolves(tmp_path: Path) -> None:
    """Q7: any existing filesystem entry satisfies a destination — including a
    DIRECTORY. A strict `is_file()`, for exact parity with `broken-ref`, would
    report a correct directory link as broken.
    """
    root = _tiny_root(tmp_path)
    (root / "sub").mkdir()
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\n"
        "Updated: 2026-01-01\n\n[a](sub/) and [b](sub)\n"
    )
    assert _findings(root / "doc.md", text, root) == []


def test_body_link_findings_non_md_destination_resolves(tmp_path: Path) -> None:
    """Q7: any extension. `convention.md` already says non-Markdown files may be
    referenced from prose; body links inherit that.
    """
    root = _tiny_root(tmp_path)
    (root / "data.yaml").write_text("k: v\n")
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\n"
        "Updated: 2026-01-01\n\n[a](data.yaml)\n"
    )
    assert _findings(root / "doc.md", text, root) == []


def test_body_link_findings_excluded_but_existing_destination_resolves(tmp_path: Path) -> None:
    """M26 — Q8's shape, restated: exclusion predicates govern the WALK, never
    what a destination may point at. A link to an excluded-but-existing file
    resolves.
    """
    root = _tiny_root(tmp_path)
    (root / ".docsignore").write_text("notes/\n")
    (root / "notes").mkdir()
    (root / "notes" / "scratch.md").write_text("# Scratch\n")
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\n"
        "Updated: 2026-01-01\n\n[a](notes/scratch.md)\n"
    )
    assert _findings(root / "doc.md", text, root) == []


def test_body_link_findings_fragment_is_never_validated(tmp_path: Path) -> None:
    """D3: fragments are preserved and never validated — no heading check, in
    this milestone or the next (the 2026-08-10 operator decision).
    """
    root = _tiny_root(tmp_path)
    (root / "plan.md").write_text("# Plan\n\nNo such heading here.\n")
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\n"
        "Updated: 2026-01-01\n\n[a](plan.md#no-such-heading) and [b](#same-doc)\n"
    )
    assert _findings(root / "doc.md", text, root) == []


def test_body_link_findings_percent_escape_resolves_after_decoding(tmp_path: Path) -> None:
    """D1 rule 8: `my%20doc.md` resolves against a file literally named
    `my doc.md`.

    Built inline rather than committed: no fixture filename may contain a
    space, because `tests/` ships in every sdist.
    """
    root = _tiny_root(tmp_path)
    (root / "my doc.md").write_text("# My Doc\n")
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\n"
        "Updated: 2026-01-01\n\n[a](my%20doc.md)\n"
    )
    assert _findings(root / "doc.md", text, root) == []


def test_body_link_findings_silent_for_every_non_local_kind(tmp_path: Path) -> None:
    """Step 1 of the evaluation order: a non-`local` destination is silence."""
    root = _tiny_root(tmp_path)
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: bodyprobe\nUpdated: 2026-01-01\n\n"
        "[a]() [b](#f) [c](//host/x) [d](/abs.md) [e](https://x) [f](mailto:a@b)\n"
    )
    assert _findings(root / "doc.md", text, root) == []


# --- runtime (structural risk) --------------------------------------------


def test_scan_pathological_input_is_linear() -> None:
    """The scanner must not backtrack catastrophically on adversarial input.

    Three shapes, 310 KB in total, under a 2.0 s wall-clock bound — roughly
    50x the expected cost, so the bound catches a quadratic or exponential
    implementation without being flaky on a loaded CI box. The trade-off is
    deliberate: a tight bound would flake, and a bound this loose still fails
    instantly on the failure mode it exists to catch. `cli.md` is 112 KB and
    the live tree scans in milliseconds.
    """
    cases = [
        "[" * 50_000 + "](x)",
        "[a](" * 40_000,
        "[a](<" + "x" * 100_000,
    ]
    assert sum(len(c) for c in cases) >= 200_000
    start = time.perf_counter()
    for case in cases:
        _scan(case)
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"pathological scan took {elapsed:.3f}s; expected well under 2.0s"
