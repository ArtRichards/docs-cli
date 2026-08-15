"""M28 — the pure move-rewrite seam: the formula, the renderer, the splicer,
the plan, the pre-flight, both strand legs, and the shared JSON section.

Phase 2 (written RED). Every symbol under test lands in Phase 5/6:
`LinkRewrite`, `DocRewrite`, `Strand`, `MovePlan`, `MOVE_STRAND_KINDS`,
`plan_body_link_rewrites`, `render_destination_token`, `splice_body_links`,
`plan_move`, `preflight_move_plan`, `apply_move_plan` and
`move_plan_to_json`. They are reached through `getattr(cli, ...)` rather than
a module-level import, so collection stays clean, the RED reason is a single
honest `AttributeError`, and `mypy src/ tests/` stays green at baseline
(getattr yields `Any`).

The contract under test is the milestone's *Decisions (Phase 1 — BINDING)* —
items (A) through (M) — and `cli.md` ›
*Move-safe body-link rewrites (M28 — D1–D7)*.

Exotic grammar lives here as **inline strings**, not as committed fixture
trees (the M25 rule): every case below asserts on plan output or on written
bytes, not on a tree walk. The `movelink-*` fixture trees Phase 3 authors
cover the tree-walk half, and no committed fixture filename carries a space
or a parenthesis — the re-encoding cases are built in `tmp_path` or passed
straight to the renderer.
"""

from __future__ import annotations

import dataclasses
import os
import posixpath
from pathlib import Path

import pytest

from docs_cli import cli

_DATED = "archive/2026-08-15"

_SKIP_AS_ROOT = pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="root bypasses 0o444 write protection; the unwritable trigger does not fire",
)


def _m28(name: str):
    """Fetch an M28 symbol that does not exist yet.

    The indirection is deliberate: a module-level import of a missing name
    would be a COLLECTION error (the Phase-4 exit criterion forbids those),
    and a literal `getattr(cli, "…")` trips ruff's B009. This keeps the RED
    reason a single clean `AttributeError` and keeps mypy green.
    """
    return getattr(cli, name)


def _plan_links(rel: str, new_rel: str, text: str, moves: dict[str, str]):
    return _m28("plan_body_link_rewrites")(rel, new_rel, text, moves)


def _render(raw: str, new_path: str, fragment: str | None) -> str:
    return _m28("render_destination_token")(raw, new_path, fragment)


def _splice(text: str, rewrites) -> str:
    return _m28("splice_body_links")(text, rewrites)


def _raws(rewrites) -> list[str]:
    return [r.new_raw for r in rewrites]


def _doc(
    title: str,
    body: str,
    *,
    lifecycle: str = "active",
    role: str = "spec",
    related: tuple[str, ...] = (),
    updated: str = "2026-05-20",
    archived_reason: str | None = None,
) -> str:
    """One structure-only document. Static dates; never today-sensitive."""
    lines = [
        f"# {title}",
        "",
        f"Lifecycle: {lifecycle}",
        f"Role: {role}",
        "Project: probe",
        f"Updated: {updated}",
    ]
    if archived_reason is not None:
        lines.append(f"Archived-reason: {archived_reason}")
    if related:
        lines += ["", "Related:"] + [f"- {entry}" for entry in related]
    lines += ["", "## Body", "", body.rstrip("\n"), ""]
    return "\n".join(lines)


def _tree(tmp_path: Path, files: dict[str, str]) -> Path:
    root = tmp_path / "tree"
    root.mkdir(parents=True)
    (root / ".docs.toml").write_text(
        '[project]\nname = "probe"\n\n[archive]\ndir = "archive"\ndate_format = "%Y-%m-%d"\n'
    )
    for rel, text in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    return root


def _entries(root: Path):
    """`(config, [(Doc, text), …])` in walk order — what `plan_move` consumes."""
    config = cli.load_config(root)
    return config, [(doc, doc.path.read_text()) for doc in cli.walk(root, config)]


def _plan(root: Path, moves: dict[str, str], *, strand_check: bool = True, related_pairs=None):
    config, entries = _entries(root)
    kwargs = {"entries": entries, "moves": moves, "strand_check": strand_check}
    if related_pairs is not None:
        kwargs["related_pairs"] = related_pairs
    return _m28("plan_move")(root, config, **kwargs)


def _rewrite_for(plan, rel: str):
    for rewrite in plan.rewrites:
        if rewrite.rel == rel:
            return rewrite
    return None


# --- (B) the formula: the two classes, one code path ----------------------
#
# Intended RED for this whole file: every M28 symbol lands in Phase 5/6
# (`AttributeError` via `_m28`).


def test_class_1_incoming_target_moved() -> None:
    """The referrer stays put; its destination is repointed (D1 class 1)."""
    text = "# Note\n\nSee [the plan](plan.md) for context.\n"
    rewrites = _plan_links("note.md", "note.md", text, {"plan.md": f"{_DATED}/plan.md"})

    assert len(rewrites) == 1, f"exactly one occurrence is planned, got {rewrites!r}"
    rewrite = rewrites[0]
    assert rewrite.link.raw == "plan.md", "the M27 record is carried verbatim, never re-derived"
    assert rewrite.old_target == "plan.md"
    assert rewrite.new_target == f"{_DATED}/plan.md"
    assert rewrite.new_raw == f"{_DATED}/plan.md"


def test_class_2_referrer_moved_rebases_from_the_new_directory() -> None:
    """The target did not move; the destination is rebased from the referrer's
    NEW directory (D1 class 2). Two directories deeper means exactly `../../`.
    """
    text = "# Plan\n\nSee [the note](note.md).\n"
    rewrites = _plan_links("plan.md", f"{_DATED}/plan.md", text, {"plan.md": f"{_DATED}/plan.md"})

    assert _raws(rewrites) == ["../../note.md"]
    assert rewrites[0].old_target == "note.md", "step 2 resolves from the OLD directory"
    assert rewrites[0].new_target == "note.md", "the target itself did not move"


def test_a_document_that_moves_and_links_to_a_co_moving_document() -> None:
    """Both classes at once: `D` moves AND its target moves, to a different
    directory, so neither the map lookup nor the rebase may be skipped.
    """
    text = "# A\n\nSee [b](b.md).\n"
    moves = {"sub/a.md": "a.md", "sub/b.md": "deep/b.md"}
    rewrites = _plan_links("sub/a.md", "a.md", text, moves)

    assert [(r.old_target, r.new_target) for r in rewrites] == [("sub/b.md", "deep/b.md")]
    assert _raws(rewrites) == ["deep/b.md"]


@pytest.mark.parametrize(
    ("referrer", "spelling"),
    [
        ("a.md", "x.md"),
        ("b.md", "./x.md"),
        ("c.md", "sub/../x.md"),
        ("sub/deep.md", "../x.md"),
    ],
)
def test_move_map_is_keyed_by_canonical_target_not_by_string(referrer, spelling) -> None:
    """E6: one target spelled four ways is rewritten in all four, with NO alias
    list — step 2 normalises before step 4 looks anything up.

    This is the property the `Related:` rewriter does not have (M26 — Q5 needed
    a per-alias pair list to catch a `./b.md` bullet).
    """
    text = f"# R\n\nSee [x]({spelling}).\n"
    rewrites = _plan_links(referrer, referrer, text, {"x.md": f"{_DATED}/x.md"})

    assert len(rewrites) == 1, f"{spelling!r} from {referrer!r} must be recognised as x.md"
    assert rewrites[0].old_target == "x.md"
    assert rewrites[0].new_target == f"{_DATED}/x.md"


# --- (B) step 5 — the no-op rule -------------------------------------------


def test_unchanged_meaning_keeps_the_original_bytes() -> None:
    """Neither the referrer nor the target moved: nothing is planned at all."""
    text = "# Note\n\nSee [the plan](plan.md) and [other](other.md).\n"
    assert _plan_links("note.md", "note.md", text, {"far.md": f"{_DATED}/far.md"}) == ()


def test_dot_slash_spelling_is_never_normalised() -> None:
    """`./x.md` is not rewritten to `x.md` — the diff of a move contains only
    what the move made stale (Q5a).
    """
    text = "# Note\n\nSee [x](./x.md) and [y](sub/../y.md).\n"
    rewrites = _plan_links("note.md", "note.md", text, {"far.md": f"{_DATED}/far.md"})

    assert rewrites == (), "a spelling whose meaning did not change keeps its bytes"


def test_a_co_moving_pair_keeps_its_sibling_link_byte_identical() -> None:
    """A plan and its log archived into the SAME dated directory produce a
    zero-byte diff in their links to each other — the no-op test is what makes
    this true, and it only works because step 5 runs AFTER step 4.
    """
    text = "# Feature\n\nSee [the log](feature-log.md).\n"
    moves = {
        "feature.md": f"{_DATED}/feature.md",
        "feature-log.md": f"{_DATED}/feature-log.md",
    }
    rewrites = _plan_links("feature.md", f"{_DATED}/feature.md", text, moves)

    assert rewrites == ()
    assert _splice(text, rewrites) == text


def test_second_equivalent_move_plans_nothing() -> None:
    """Idempotence: re-planning the SAME move over already-rewritten text is a
    no-op, because the rewritten spelling already resolves to the new target.
    """
    text = "# Note\n\nSee [the plan](plan.md).\n"
    moves = {"plan.md": f"{_DATED}/plan.md"}
    once = _splice(text, _plan_links("note.md", "note.md", text, moves))

    assert once != text
    assert _plan_links("note.md", "note.md", once, moves) == ()


# --- (B) steps 1 and 3 — out of reach (Q4) ---------------------------------


@pytest.mark.parametrize(
    ("kind", "destination"),
    [
        ("empty", ""),
        ("fragment", "#plan.md"),
        ("scheme", "https://example.test/plan.md"),
        ("protocol-relative", "//example.test/plan.md"),
        ("root-absolute", "/plan.md"),
    ],
)
def test_every_non_local_kind_is_copied_byte_for_byte(kind, destination) -> None:
    """Only `local` destinations are ever touched (D2/Q4), even when a
    same-named local target IS moving in this operation.
    """
    text = f"# Note\n\nSee [x]({destination}).\n"
    assert cli.classify_destination(destination) == kind, "the fixture must exercise `kind`"

    rewrites = _plan_links("note.md", f"{_DATED}/note.md", text, {"plan.md": f"{_DATED}/plan.md"})
    assert rewrites == ()


def test_an_escaping_destination_is_never_rebased() -> None:
    """A destination that climbs out of the root is copied byte-for-byte, even
    when the referrer itself moves — M28 never rebases an escape (Q4).
    """
    text = "# Deep\n\nSee [out](../../outside.md).\n"
    assert not cli._body_link_is_contained(
        cli.normalise_body_link_target("sub/deep.md", "../../outside.md")
    ), "the fixture must actually escape"

    assert _plan_links("sub/deep.md", "deep.md", text, {"sub/deep.md": "deep.md"}) == ()


def test_an_already_broken_destination_is_left_as_written() -> None:
    """Pre-existing damage keeps its M27 finding and is not repaired (Q4): a
    contained-but-missing destination in a document neither end of which moves
    is not planned at all.
    """
    text = "# Note\n\nSee [gone](does-not-exist.md).\n"
    assert _plan_links("note.md", "note.md", text, {"plan.md": f"{_DATED}/plan.md"}) == ()


def test_a_moving_referrer_rebases_a_broken_destination_without_repairing_it() -> None:
    """A moving referrer DOES rebase a broken destination — to the same target,
    still broken. The planner never stats, so it cannot know, and rebasing keeps
    the link pointing where its author aimed it rather than guessing a repair.
    """
    text = "# Note\n\nSee [gone](does-not-exist.md).\n"
    rewrites = _plan_links("note.md", f"{_DATED}/note.md", text, {"note.md": f"{_DATED}/note.md"})

    assert [(r.old_target, r.new_target) for r in rewrites] == [
        ("does-not-exist.md", "does-not-exist.md")
    ]
    assert _raws(rewrites) == ["../../does-not-exist.md"]


# --- (D) the never-creates-an-escape invariant ----------------------------


@pytest.mark.parametrize(
    "referrer_new", ["note.md", "sub/note.md", "a/b/c/note.md", f"{_DATED}/note.md"]
)
@pytest.mark.parametrize("target_new", ["x.md", "sub/x.md", "a/b/c/x.md", f"{_DATED}/x.md"])
def test_a_rewrite_can_never_create_an_outside_root_destination(referrer_new, target_new) -> None:
    """(D) with its proof, exercised over depths and directions: whatever the
    tool emits normalises back to the intended in-root target.
    """
    text = "# Note\n\nSee [x](x.md).\n"
    rewrites = _plan_links("note.md", referrer_new, text, {"x.md": target_new})
    if not rewrites:
        assert posixpath.dirname(referrer_new) == posixpath.dirname(target_new), (
            "the ONLY no-op combinations are the ones where the two land in the "
            "same directory, so the existing spelling still means the right thing"
        )
        return

    emitted = rewrites[0].new_raw
    path, fragment = cli._split_destination(emitted)
    assert fragment is None
    resolved = cli.normalise_body_link_target(referrer_new, path)
    assert cli._body_link_is_contained(resolved), f"{emitted!r} escapes the root"
    assert resolved == target_new, "the emitted spelling must denote the intended target"


# --- (C) the emitted spelling ---------------------------------------------


def test_emitted_form_is_relpath_without_a_leading_dot_slash() -> None:
    text = "# Sub\n\nSee [x](../x.md).\n"
    rewrites = _plan_links("sub/note.md", "note.md", text, {"sub/note.md": "note.md"})

    assert _raws(rewrites) == ["x.md"], "no leading `./` is ever emitted"


def test_fragment_is_reattached_verbatim_after_one_hash() -> None:
    """The fragment is neither decoded, re-encoded, nor validated (D3/M27 — D3)."""
    text = "# Note\n\nSee [x](plan.md#a%20section).\n"
    rewrites = _plan_links("note.md", "note.md", text, {"plan.md": f"{_DATED}/plan.md"})

    assert _raws(rewrites) == [f"{_DATED}/plan.md#a%20section"]
    assert rewrites[0].link.fragment == "a%20section"


def test_angle_destination_stays_angle_wrapped() -> None:
    text = "# Note\n\nSee [x](<plan.md>).\n"
    rewrites = _plan_links("note.md", "note.md", text, {"plan.md": f"{_DATED}/plan.md"})

    assert _raws(rewrites) == [f"<{_DATED}/plan.md>"]


def test_plain_destination_stays_plain() -> None:
    """A plain destination that must carry a space is percent-encoded, NEVER
    promoted to angle brackets — one strategy, no "it depends" cell (D3).
    """
    text = "# Note\n\nSee [x](plan.md).\n"
    rewrites = _plan_links("note.md", "note.md", text, {"plan.md": "the plan.md"})

    assert _raws(rewrites) == ["the%20plan.md"]


def test_emitted_spelling_is_independent_of_the_process_cwd(tmp_path, monkeypatch) -> None:
    """The planner is a pure function of two strings; `relpath` must never be
    handed a cwd-relative base (`posixpath.relpath("a.md", "")` is the shape
    that makes this true).
    """
    text = "# Note\n\nSee [x](x.md).\n"
    moves = {"x.md": f"{_DATED}/x.md"}
    here = _raws(_plan_links("note.md", "note.md", text, moves))

    monkeypatch.chdir(tmp_path)
    assert _raws(_plan_links("note.md", "note.md", text, moves)) == here == [f"{_DATED}/x.md"]


# --- (C) the renderer and its encode sets (E8 — authored, not measured) ----


def test_space_in_a_plain_destination_is_percent_encoded() -> None:
    assert _render("plan.md", "a b.md", None) == "a%20b.md"


def test_angle_form_keeps_a_literal_space() -> None:
    """Carrying a space is what the angle form is for; encoding it there would
    be gratuitous.
    """
    assert _render("<plan.md>", "a b.md", None) == "<a b.md>"


def test_parenthesis_is_percent_encoded_in_a_plain_destination() -> None:
    """A plain destination ends at an unescaped `)` at depth 0, and `(` beyond
    `MAX_DESTINATION_PAREN_DEPTH` kills the link outright — so both go.
    """
    assert _render("plan.md", "a(b).md", None) == "a%28b%29.md"
    assert _render("<plan.md>", "a(b).md", None) == "<a(b).md>", (
        "the angle form does not terminate at a parenthesis"
    )


def test_percent_is_encoded_before_every_other_character() -> None:
    """Order matters: encoding `%` last would double-encode the escapes the
    tool itself just wrote.
    """
    assert _render("plan.md", "a%20b.md", None) == "a%2520b.md"
    assert _render("<plan.md>", "a%20b.md", None) == "<a%2520b.md>"


def test_backslash_and_hash_are_encoded() -> None:
    """`\\` escapes and `#` opens the fragment, in both delimiter forms."""
    assert _render("plan.md", "a\\b#c.md", None) == "a%5Cb%23c.md"
    assert _render("<plan.md>", "a\\b#c.md", None) == "<a%5Cb%23c.md>"


def test_greater_than_is_encoded_inside_an_angle_destination() -> None:
    """An angle destination ends at the first unescaped `>`."""
    assert _render("<plan.md>", "a>b<c.md", None) == "<a%3Eb%3Cc.md>"
    assert _render("plan.md", "a>b<c.md", None) == "a%3Eb%3Cc.md"


def test_a_leading_hash_is_encoded_so_the_token_stays_local() -> None:
    """`#tricky.md` would re-classify as `fragment` and stop being a link at
    all. Encoding it keeps `classify_destination` at `local`.
    """
    emitted = _render("plan.md", "#tricky.md", None)
    assert emitted == "%23tricky.md"
    assert cli.classify_destination(emitted) == "local"


def test_non_ascii_passes_through_literally() -> None:
    """No blanket `urllib.parse.quote`: an accented or CJK filename is emitted
    exactly as an author would write it (R8).
    """
    assert _render("plan.md", "café.md", None) == "café.md"
    assert _render("plan.md", "計画.md", None) == "計画.md"


@pytest.mark.parametrize(
    "path",
    [
        "plan.md",
        "a b.md",
        "a\tb.md",
        "a(b).md",
        "a%20b.md",
        "a\\b.md",
        "a#b.md",
        "a<b>.md",
        "café.md",
        "計画.md",
        f"{_DATED}/plan.md",
        "../../plan.md",
    ],
)
@pytest.mark.parametrize("raw", ["plan.md", "<plan.md>"])
@pytest.mark.parametrize("fragment", [None, "section", "a%20b"])
def test_decoding_the_emitted_token_reproduces_the_intended_path(path, raw, fragment) -> None:
    """The lock on the whole encode strategy: the scanner's OWN decoder, run on
    the emitted token, reproduces exactly what the token was built from.
    """
    emitted = _render(raw, path, fragment)
    assert cli._split_destination(emitted) == (path, fragment)
    assert emitted.startswith("<") == raw.startswith("<"), "the delimiter form is invariant"


def test_a_rewritten_token_is_minimally_encoded() -> None:
    """An author's redundant escape is not reproduced: the renderer works from
    the DECODED path and applies only what the grammar requires.
    """
    text = "# Note\n\nSee [x](plan%2Ex.md).\n"
    rewrites = _plan_links("note.md", "note.md", text, {"plan.x.md": f"{_DATED}/plan.x.md"})

    assert _raws(rewrites) == [f"{_DATED}/plan.x.md"], "no `%2E` survives into the new token"


def test_a_no_op_token_keeps_its_redundant_escapes() -> None:
    """The other half of the same rule: a token that is COPIED keeps every byte,
    redundant escapes included, because it is never re-rendered.
    """
    text = "# Note\n\nSee [x](plan%2Ex.md).\n"
    rewrites = _plan_links("note.md", "note.md", text, {"far.md": f"{_DATED}/far.md"})

    assert rewrites == ()
    assert _splice(text, rewrites) == text


# --- (E) step 1 — the splicer ---------------------------------------------


def test_splices_are_applied_right_to_left() -> None:
    """Descending `start`, so an earlier span's offsets stay valid after a
    later span's replacement changes length (M27's Phase-6 technique).
    """
    text = "# Note\n\n[a](a.md) then [b](b.md) then [c](c.md).\n"
    moves = {
        "a.md": f"{_DATED}/a.md",
        "b.md": f"{_DATED}/b.md",
        "c.md": f"{_DATED}/c.md",
    }
    rewrites = _plan_links("note.md", "note.md", text, moves)

    assert [r.link.start for r in rewrites] == sorted(r.link.start for r in rewrites), (
        "the plan is stored ascending; the SPLICER is what reverses"
    )
    assert _splice(text, rewrites) == (
        f"# Note\n\n[a]({_DATED}/a.md) then [b]({_DATED}/b.md) then [c]({_DATED}/c.md).\n"
    )


def test_only_the_destination_token_changes() -> None:
    """Label, title, quoting form, surrounding prose and the trailing newline
    are byte-identical afterwards.
    """
    text = (
        "# Note\n\nBefore. [The **plan**](plan.md 'A title with (parens)') after.\n"
        "A bare plan.md mention, and `[x](plan.md)` in code.\n"
    )
    rewrites = _plan_links("note.md", "note.md", text, {"plan.md": f"{_DATED}/plan.md"})

    assert _splice(text, rewrites) == (
        f"# Note\n\nBefore. [The **plan**]({_DATED}/plan.md 'A title with (parens)') after.\n"
        "A bare plan.md mention, and `[x](plan.md)` in code.\n"
    )


def test_two_links_on_one_line_are_both_rewritten() -> None:
    text = "# Note\n\n[a](a.md) and [a again](./a.md).\n"
    rewrites = _plan_links("note.md", "note.md", text, {"a.md": f"{_DATED}/a.md"})

    assert len(rewrites) == 2
    assert _splice(text, rewrites) == (
        f"# Note\n\n[a]({_DATED}/a.md) and [a again]({_DATED}/a.md).\n"
    )


def test_reference_definition_destination_is_spliced() -> None:
    """A reference DEFINITION carries a destination and is in the validated
    grammar; a reference USE is not, and must stay untouched.
    """
    text = '# Note\n\nSee [the plan].\n\n[the plan]: plan.md "The plan"\n'
    rewrites = _plan_links("note.md", "note.md", text, {"plan.md": f"{_DATED}/plan.md"})

    assert len(rewrites) == 1, "the use is not a destination; only the definition is"
    assert _splice(text, rewrites) == (
        f'# Note\n\nSee [the plan].\n\n[the plan]: {_DATED}/plan.md "The plan"\n'
    )


def test_titled_destination_keeps_its_title() -> None:
    text = '# Note\n\nSee [x](plan.md "The plan").\n'
    rewrites = _plan_links("note.md", "note.md", text, {"plan.md": f"{_DATED}/plan.md"})

    assert _splice(text, rewrites) == f'# Note\n\nSee [x]({_DATED}/plan.md "The plan").\n'


def test_directory_destination_keeps_its_trailing_slash() -> None:
    """R7: the `/` is reattached iff the original token's path part ended with
    one. `relpath` discards it, and dropping it would change what the author
    wrote for no reason.
    """
    text = "# A\n\nSee [the folder](sub/).\n"
    rewrites = _plan_links("a.md", "deep/a.md", text, {"a.md": "deep/a.md"})

    assert _raws(rewrites) == ["../sub/"]
    assert _splice(text, rewrites) == "# A\n\nSee [the folder](../sub/).\n"


# --- (E) the pipeline order -----------------------------------------------


def test_body_splices_precede_the_related_bullet_rewrite(tmp_path) -> None:
    """(E) is forced, not stylistic: body-link spans are offsets into the text
    they were scanned from, and `rewrite_related_refs` changes LENGTHS. Running
    the bullet rewrite first would land every later splice at the wrong offset.

    The fixture is built so the two edits differ in length and the bullet
    precedes the body link in the file — the exact shape that corrupts.
    """
    root = _tree(
        tmp_path,
        {
            "status.md": _doc(
                "Status",
                "Tracking [the plan](plan.md) closely.",
                related=("pairs-with: plan.md",),
            ),
            "plan.md": _doc("Plan", "The plan."),
        },
    )
    plan = _plan(root, {"plan.md": f"{_DATED}/plan.md"}, strand_check=False)
    rewrite = _rewrite_for(plan, "status.md")

    assert rewrite is not None
    assert f"- pairs-with: {_DATED}/plan.md" in rewrite.new_text
    assert f"Tracking [the plan]({_DATED}/plan.md) closely." in rewrite.new_text
    assert rewrite.related_rewrites == 1
    assert rewrite.original == (root / "status.md").read_text()


def test_a_related_bullet_is_never_treated_as_a_body_link(tmp_path) -> None:
    """A `Related:` bullet is not link syntax; the two halves never overlap."""
    root = _tree(
        tmp_path,
        {
            "status.md": _doc("Status", "No links here.", related=("pairs-with: plan.md",)),
            "plan.md": _doc("Plan", "The plan."),
        },
    )
    plan = _plan(root, {"plan.md": f"{_DATED}/plan.md"}, strand_check=False)
    rewrite = _rewrite_for(plan, "status.md")

    assert rewrite is not None
    assert rewrite.links == (), "the bullet is metadata, never a destination token"
    assert rewrite.related_rewrites == 1


# --- purity ----------------------------------------------------------------


def test_planner_never_touches_the_filesystem() -> None:
    """The planner is a pure function of `(rel, new_rel, text, moves)`;
    existence checks and writes are the caller's job. Sentinels on the doors it
    could use (M27's `test_normalise_is_lexical_…` precedent).

    `pytest.MonkeyPatch.context()` rather than the `monkeypatch` fixture, and
    that is not a style choice: the fixture reverts at TEARDOWN, so a failure
    inside the block would leave `Path.exists` poisoned while pytest renders
    the traceback — an INTERNALERROR instead of a readable RED reason. The
    context manager reverts as the exception unwinds.
    """

    def _boom(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("the planner touched the filesystem")

    text = "# Note\n\nSee [x](x.md) and [gone](nope.md).\n"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(Path, "exists", _boom)
        mp.setattr(Path, "is_file", _boom)
        mp.setattr(Path, "resolve", _boom)
        mp.setattr(Path, "read_text", _boom)
        rewrites = _plan_links("note.md", "note.md", text, {"x.md": f"{_DATED}/x.md"})

    assert _raws(rewrites) == [f"{_DATED}/x.md"]


# --- (H) the strand-check, leg 1 -------------------------------------------


def _strand_tree(tmp_path: Path) -> Path:
    """The issue #1 shape: a live child outside the plan, plus a legitimate
    closeout neighbourhood that must NOT trip leg 1.
    """
    return _tree(
        tmp_path,
        {
            "plan.md": _doc(
                "Roadmap",
                "The long-lived roadmap.",
                role="plan",
                related=("parent-of: milestone.md", "parent-of: live-child.md"),
            ),
            "live-child.md": _doc(
                "Live child",
                "A live document whose parent must not vanish.",
                role="milestone",
                related=("child-of: plan.md",),
            ),
            "milestone.md": _doc(
                "Milestone",
                "See [the impl log](milestone-impl.md).",
                role="milestone",
                related=("child-of: plan.md", "pairs-with: milestone-impl.md"),
            ),
            "milestone-impl.md": _doc(
                "Milestone log",
                "See [the milestone](milestone.md).",
                role="log",
                related=("child-of: milestone.md", "pairs-with: milestone.md"),
            ),
            "status.md": _doc(
                "Status",
                "Tracking [the milestone](milestone.md) and [the plan](plan.md).",
                role="status",
                related=("pairs-with: milestone.md", "precedes: plan.md"),
            ),
            "archive/2026-01-01/old.md": _doc(
                "Old",
                "Superseded; see [the milestone](../../milestone.md).",
                lifecycle="archived",
                role="log",
                archived_reason="superseded",
                related=("child-of: milestone.md",),
            ),
        },
    )


def _closeout_moves() -> dict[str, str]:
    return {
        "milestone.md": f"{_DATED}/milestone.md",
        "milestone-impl.md": f"{_DATED}/milestone-impl.md",
    }


def test_leg_1_fires_on_a_still_active_child_of_into_the_plan(tmp_path) -> None:
    """The reported harm: a parent archived out from under its live children.
    Both ends are named, one `Strand` per orphaned pair.
    """
    plan = _plan(_strand_tree(tmp_path), {"plan.md": f"{_DATED}/plan.md"})

    assert [(o.path, o.target) for o in plan.orphans] == [
        ("live-child.md", "plan.md"),
        ("milestone.md", "plan.md"),
    ], "walk order, one record per orphaned pair"
    assert {o.verb for o in plan.orphans} == {"child-of"}
    assert {o.kind for o in plan.orphans} == {"related"}
    assert {o.line for o in plan.orphans} == {None}


def test_leg_1_ignores_a_child_of_declared_by_a_plan_member(tmp_path) -> None:
    """A document being archived cannot be stranded — `milestone-impl.md`
    declares `child-of: milestone.md` and moves in the same operation.
    """
    plan = _plan(_strand_tree(tmp_path), _closeout_moves())

    assert plan.orphans == ()


def test_leg_1_ignores_an_archived_child(tmp_path) -> None:
    """An already-archived document is not "still active" — the archived
    `old.md` declares `child-of: milestone.md` and must trip neither leg.
    """
    plan = _plan(_strand_tree(tmp_path), _closeout_moves())

    assert plan.orphans == ()
    assert "archive/2026-01-01/old.md" not in {s.path for s in plan.strands}


def test_leg_1_does_not_fire_on_pairs_with_precedes_depends_on_or_body_links(tmp_path) -> None:
    """The over-fire lock the setup decisions require (A1): a legitimate
    closeout whose only still-active inbound references are `pairs-with`,
    `precedes`, `parent-of` and body links COMPLETES.

    E7 measured this predicate at 0 occurrences on plan A and 6 on plans B and
    C; a check that fires on a correct closeout is one operators route around.
    """
    plan = _plan(_strand_tree(tmp_path), _closeout_moves())

    assert plan.orphans == ()
    assert {s.verb for s in plan.strands if s.kind == "related"} == {"parent-of", "pairs-with"}, (
        "every one of these is deliberate and repaired by the operation itself"
    )


def test_the_strand_check_is_off_for_mv(tmp_path) -> None:
    """R4: `docs mv` produces no newly-archived set, so it runs neither leg —
    even on a tree that would refuse under `docs archive`.
    """
    plan = _plan(_strand_tree(tmp_path), {"plan.md": f"{_DATED}/plan.md"}, strand_check=False)

    assert plan.orphans == ()
    assert plan.strands == ()


# --- (H) the strand-check, leg 2 -------------------------------------------


def test_leg_2_reports_every_other_related_verb_and_every_body_link(tmp_path) -> None:
    plan = _plan(_strand_tree(tmp_path), _closeout_moves())
    observed = {(s.path, s.target, s.kind, s.verb) for s in plan.strands}

    assert ("plan.md", "milestone.md", "related", "parent-of") in observed
    assert ("status.md", "milestone.md", "related", "pairs-with") in observed
    assert ("status.md", "milestone.md", "body-link", None) in observed


def test_leg_2_excludes_the_child_of_edges_leg_1_owns(tmp_path) -> None:
    """The two legs partition the graph; nothing is reported twice."""
    plan = _plan(_strand_tree(tmp_path), {"plan.md": f"{_DATED}/plan.md"})

    assert plan.orphans, "the fixture must produce orphans for this to mean anything"
    overlap = {(s.path, s.target, s.verb) for s in plan.strands} & {
        (o.path, o.target, o.verb) for o in plan.orphans
    }
    assert overlap == set()
    assert all(not (s.kind == "related" and s.verb == "child-of") for s in plan.strands)


def test_leg_2_excludes_plan_members_and_archived_referrers(tmp_path) -> None:
    moves = _closeout_moves()
    plan = _plan(_strand_tree(tmp_path), moves)

    assert not ({s.path for s in plan.strands} & set(moves)), "a plan member cannot be stranded"
    assert all(not s.path.startswith("archive/") for s in plan.strands)


def test_leg_2_report_is_deterministically_ordered(tmp_path) -> None:
    """Referrer walk order; within a referrer, `Related:` bullets in
    declaration order, then body links by `(line, column)`.
    """
    plan = _plan(_strand_tree(tmp_path), _closeout_moves())
    again = _plan(_strand_tree(tmp_path / "second"), _closeout_moves())

    assert [(s.path, s.target, s.kind, s.verb, s.line) for s in plan.strands] == [
        (s.path, s.target, s.kind, s.verb, s.line) for s in again.strands
    ]
    assert [s.path for s in plan.strands] == sorted(s.path for s in plan.strands)

    status = [s for s in plan.strands if s.path == "status.md"]
    assert [s.kind for s in status] == ["related", "body-link"], (
        "bullets before body links, within one referrer"
    )


def test_leg_2_reports_references_the_operation_repairs(tmp_path) -> None:
    """The semantics lock. Leg 2 is NOT a damage report: `status.md`'s body
    link is REWRITTEN by this same operation and is still reported, because
    what is reported is the post-plan consequence "active X still points at
    newly-archived Y".
    """
    plan = _plan(_strand_tree(tmp_path), _closeout_moves())

    rewrite = _rewrite_for(plan, "status.md")
    assert rewrite is not None and rewrite.links, "the operation repairs this link"
    assert ("status.md", "milestone.md", "body-link") in {
        (s.path, s.target, s.kind) for s in plan.strands
    }


def test_empty_neighbourhood_yields_an_empty_tuple_never_none(tmp_path) -> None:
    root = _tree(
        tmp_path,
        {
            "lonely.md": _doc("Lonely", "Nothing points here."),
            "other.md": _doc("Other", "Unrelated prose."),
        },
    )
    plan = _plan(root, {"lonely.md": f"{_DATED}/lonely.md"})

    assert plan.strands == ()
    assert plan.orphans == ()
    assert _m28("move_plan_to_json")(plan)["strands"] == []


# --- (F) the rewrite-plan pre-flight --------------------------------------


def test_preflight_accepts_a_clean_plan(tmp_path) -> None:
    root = _tree(
        tmp_path,
        {
            "note.md": _doc("Note", "See [the plan](plan.md)."),
            "plan.md": _doc("Plan", "The plan."),
        },
    )
    plan = _plan(root, {"plan.md": f"{_DATED}/plan.md"})

    assert _m28("preflight_move_plan")(plan) is None


def test_a_span_that_no_longer_matches_its_text_refuses(tmp_path) -> None:
    """(F): `text[link.start:link.end] == link.raw` is proven for every planned
    span. A refusal, never an `assert` — exit 2, zero bytes written.
    """
    root = _tree(
        tmp_path,
        {
            "note.md": _doc("Note", "See [the plan](plan.md)."),
            "plan.md": _doc("Plan", "The plan."),
        },
    )
    plan = _plan(root, {"plan.md": f"{_DATED}/plan.md"})
    corrupted = dataclasses.replace(
        _rewrite_for(plan, "note.md"), original="# Note\n\nnothing here\n"
    )
    poisoned = dataclasses.replace(plan, rewrites=(corrupted,))

    with pytest.raises(cli.CoordinatedWriteError) as excinfo:
        _m28("preflight_move_plan")(poisoned)
    assert excinfo.value.exit_code == 2
    assert excinfo.value.rolled_back is True
    assert excinfo.value.published == ()


def test_overlapping_spans_refuse_rather_than_corrupt(tmp_path) -> None:
    """Two planned spans in one document may not overlap: splicing them would
    silently corrupt the file rather than fail.
    """
    root = _tree(
        tmp_path,
        {
            "note.md": _doc("Note", "See [a](a.md) and [b](b.md)."),
            "a.md": _doc("A", "A."),
            "b.md": _doc("B", "B."),
        },
    )
    plan = _plan(root, {"a.md": f"{_DATED}/a.md", "b.md": f"{_DATED}/b.md"})
    rewrite = _rewrite_for(plan, "note.md")
    assert rewrite is not None and len(rewrite.links) == 2

    first, second = rewrite.links
    widened = dataclasses.replace(first, link=dataclasses.replace(first.link, end=second.link.end))
    poisoned = dataclasses.replace(
        plan, rewrites=(dataclasses.replace(rewrite, links=(widened, second)),)
    )

    with pytest.raises(cli.CoordinatedWriteError) as excinfo:
        _m28("preflight_move_plan")(poisoned)
    assert excinfo.value.exit_code == 2


@_SKIP_AS_ROOT
def test_preflight_refuses_an_unwritable_planned_referrer(tmp_path) -> None:
    """The message is frozen (J) and names the document, so an operator can act
    on it without re-deriving anything.
    """
    root = _tree(
        tmp_path,
        {
            "note.md": _doc("Note", "See [the plan](plan.md)."),
            "plan.md": _doc("Plan", "The plan."),
        },
    )
    plan = _plan(root, {"plan.md": f"{_DATED}/plan.md"})
    (root / "note.md").chmod(0o444)
    try:
        with pytest.raises(cli.CoordinatedWriteError) as excinfo:
            _m28("preflight_move_plan")(plan)
    finally:
        (root / "note.md").chmod(0o644)

    assert str(excinfo.value) == "note.md is not writable; refusing before any write"
    assert excinfo.value.exit_code == 2


def test_apply_writes_only_the_documents_whose_bytes_change(tmp_path) -> None:
    """`MovePlan.rewrites` carries ONLY documents whose bytes change, and
    `apply_move_plan` writes the non-moving ones with one `atomic_write` each.
    """
    root = _tree(
        tmp_path,
        {
            "note.md": _doc("Note", "See [the plan](plan.md)."),
            "bystander.md": _doc("Bystander", "A bare plan.md mention only."),
            "plan.md": _doc("Plan", "The plan."),
        },
    )
    before = (root / "bystander.md").read_text()
    plan = _plan(root, {"plan.md": f"{_DATED}/plan.md"})

    assert "bystander.md" not in {r.rel for r in plan.rewrites}
    _m28("apply_move_plan")(plan)

    assert (root / "bystander.md").read_text() == before
    assert f"[the plan]({_DATED}/plan.md)" in (root / "note.md").read_text()


# --- (K) the shared record -------------------------------------------------


def test_move_plan_json_is_exactly_the_shared_rewrites_and_strands_section(tmp_path) -> None:
    """One serializer, spliced into both verbs' records — which is what makes
    them byte-comparable by construction rather than by discipline (R10).
    """
    plan = _plan(_strand_tree(tmp_path), _closeout_moves())
    payload = _m28("move_plan_to_json")(plan)

    assert list(payload) == ["rewrites", "strands"]


def test_move_plan_json_rewrite_record_keys_are_closed(tmp_path) -> None:
    plan = _plan(_strand_tree(tmp_path), _closeout_moves())
    records = _m28("move_plan_to_json")(plan)["rewrites"]

    assert records, "the closeout fixture must plan at least one rewrite"
    for record in records:
        assert list(record) == ["path", "line", "column", "old", "new"]
        assert isinstance(record["line"], int) and record["line"] >= 1
        assert isinstance(record["column"], int) and record["column"] >= 1

    assert records == sorted(records, key=lambda r: (r["path"], r["line"], r["column"]))
    status = [r for r in records if r["path"] == "status.md"]
    assert status and status[0]["old"] == "milestone.md"
    assert status[0]["new"] == f"{_DATED}/milestone.md"


def test_strand_record_keys_are_closed(tmp_path) -> None:
    plan = _plan(_strand_tree(tmp_path), _closeout_moves())
    records = _m28("move_plan_to_json")(plan)["strands"]

    assert records, "the closeout fixture must report leg-2 strands"
    for record in records:
        assert list(record) == ["path", "target", "kind", "verb", "line"]
        assert (record["verb"] is None) == (record["kind"] == "body-link")
        assert (record["line"] is None) == (record["kind"] == "related")


def test_strand_kinds_are_frozen(tmp_path) -> None:
    assert _m28("MOVE_STRAND_KINDS") == frozenset({"related", "body-link"})

    plan = _plan(_strand_tree(tmp_path), _closeout_moves())
    assert {s.kind for s in plan.strands} <= _m28("MOVE_STRAND_KINDS")
    assert {o.kind for o in plan.orphans} <= _m28("MOVE_STRAND_KINDS")


def test_the_records_are_frozen_dataclasses() -> None:
    """M28 collects spans and then splices; an in-place edit between those two
    steps would silently invalidate every remaining span in the document, so
    mutation must be a `FrozenInstanceError` at the moment of the mistake.
    """
    for name in ("LinkRewrite", "DocRewrite", "Strand", "MovePlan"):
        record = _m28(name)
        assert dataclasses.is_dataclass(record), f"{name} must be a dataclass"
        assert vars(record)["__dataclass_params__"].frozen, f"{name} must be frozen"


def test_relpath_of_a_root_level_target_needs_no_special_case() -> None:
    """The ground-truth measurement (B) step 6 relies on: `posixpath` cancels
    the empty base rather than producing a cwd-relative answer. Pinned here so
    a Phase-5 implementation cannot "fix" it with an `or '.'` that changes the
    emitted spelling.
    """
    assert posixpath.relpath("a.md", "") == "a.md"
    assert posixpath.relpath("a.md", posixpath.dirname("note.md")) == "a.md"
