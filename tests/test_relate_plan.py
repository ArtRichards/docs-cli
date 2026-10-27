"""M25 — `docs relate` core seam: planning, applying, rollback, JSON.

Phase 2 (written RED). Every symbol under test lands in Phase 5/6:
`plan_relate`, `apply_relate_plan`, `relate_plan_to_json`,
`CoordinatedWriteError`. They are reached through `getattr(cli, ...)` rather
than a module-level import, so collection stays clean, the RED reason is a
single honest `AttributeError`, and `mypy src/ tests/` stays green at
baseline (getattr yields `Any`).

The contract under test is D3 (planning / idempotency), D4 (archived audit
boundary), and D5 (staged publish + rollback) of the milestone's
*Decisions (Phase 1 — BINDING)* section.
"""

from __future__ import annotations

import random
import string
from pathlib import Path
from typing import Any

import pytest

from docs_cli import cli

_DATE = "2026-08-11"


def _two_doc_root(tmp_path: Path, *, source_edge: str | None = None) -> Path:
    """A minimal two-doc root: `a.md` and `b.md`, both active.

    Inline builder rather than a committed tree — every test here writes and
    then byte-compares, so a `shutil.copytree` of a static tree would be pure
    overhead. Static `Updated:` dates; no stale window is ever applied.
    """
    root = tmp_path / "relateprobe"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "relateprobe"\n')

    def _doc(title: str, edge: str | None) -> str:
        text = (
            f"# {title}\n\nLifecycle: active\nRole: notes\n"
            f"Project: relateprobe\nUpdated: 2026-05-20\n"
        )
        if edge is not None:
            text += f"\nRelated:\n- {edge}\n"
        return text + "\n## Body\n\nProse.\n"

    (root / "a.md").write_text(_doc("A", source_edge))
    (root / "b.md").write_text(_doc("B", None))
    return root


def _archived_pair_root(tmp_path: Path) -> Path:
    """An active `a.md` and an archived `archive/2026-01-01/old.md`."""
    root = tmp_path / "archiveprobe"
    (root / "archive" / "2026-01-01").mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "archiveprobe"\n')
    (root / "a.md").write_text(
        "# A\n\nLifecycle: active\nRole: notes\nProject: archiveprobe\n"
        "Updated: 2026-05-20\n\nRelated:\n- depends-on: archive/2026-01-01/old.md\n"
        "\n## Body\n\nProse.\n"
    )
    (root / "archive" / "2026-01-01" / "old.md").write_text(
        "# Old\n\nLifecycle: archived\nRole: plan\nProject: archiveprobe\n"
        "Updated: 2026-01-01\nArchived-reason: completed\n\n"
        "Related:\n- references: a.md\n\n## Body\n\nHistorical prose.\n"
    )
    return root


def _m25(name: str):
    """Fetch an M25 symbol that does not exist yet.

    The indirection is deliberate: a module-level import of a missing name
    would be a COLLECTION error (the Phase-4 exit criterion forbids those),
    and a literal `getattr(cli, "…")` trips ruff's B009. This keeps the RED
    reason a single clean `AttributeError` and keeps mypy green.
    """
    return getattr(cli, name)


def _plan(root: Path, **kwargs):
    config = cli.load_config(root)
    return _m25("plan_relate")(root, config, **kwargs)


def test_plan_relate_stages_both_texts_without_writing(tmp_path):
    """D5 stage 2: planning is pure — neither endpoint is touched on disk."""
    root = _two_doc_root(tmp_path)
    before = {p: p.read_bytes() for p in sorted(root.glob("*.md"))}

    plan = _plan(
        root,
        action="add",
        source=root / "a.md",
        verb="precedes",
        target=root / "b.md",
        reason=None,
        date_str=_DATE,
    )

    assert {p: p.read_bytes() for p in sorted(root.glob("*.md"))} == before
    assert plan.action == "add"
    assert plan.verb == "precedes"
    assert plan.inverse == "follows"
    assert plan.source_rel == "a.md"
    assert plan.target_rel == "b.md"
    assert len(plan.edits) == 2
    assert [e.rel for e in plan.edits] == ["a.md", "b.md"], "edits are always (source, target)"
    assert plan.edits[0].edge == "precedes: b.md"
    assert plan.edits[1].edge == "follows: a.md"


def test_plan_relate_marks_present_before_after(tmp_path):
    """Idempotency is visible in the plan: the satisfied half is `unchanged`."""
    root = _two_doc_root(tmp_path, source_edge="precedes: b.md")
    plan = _plan(
        root,
        action="add",
        source=root / "a.md",
        verb="precedes",
        target=root / "b.md",
        reason=None,
        date_str=_DATE,
    )

    source_edit, target_edit = plan.edits
    assert (source_edit.present_before, source_edit.present_after) == (True, True)
    assert source_edit.change == "unchanged"
    assert source_edit.updated_bumped is False
    assert source_edit.new_text == source_edit.original

    assert (target_edit.present_before, target_edit.present_after) == (False, True)
    assert target_edit.change == "added"
    assert target_edit.updated_bumped is True, "only an endpoint whose bytes change is bumped"


def test_plan_relate_active_edit_has_no_revision(tmp_path):
    """D4 audit asymmetry: an active endpoint never gets a `Revision:` bullet."""
    root = _two_doc_root(tmp_path)
    plan = _plan(
        root,
        action="add",
        source=root / "a.md",
        verb="precedes",
        target=root / "b.md",
        reason="because",
        date_str=_DATE,
    )
    for edit in plan.edits:
        assert edit.archived is False
        assert edit.revision_appended is False
        assert "Revision:" not in edit.new_text


def test_plan_relate_archived_edit_appends_revision_and_bumps_updated(tmp_path):
    """D4: the archived endpoint changes EXACTLY three things and nothing else.

    Pins the allowed byte delta line-by-line: the recognized `Related:`
    bullet, the `Updated:` value, and the `Revision:` group.
    """
    root = _archived_pair_root(tmp_path)
    archived = root / "archive" / "2026-01-01" / "old.md"
    plan = _plan(
        root,
        action="add",
        source=root / "a.md",
        verb="depends-on",
        target=archived,
        reason="complete the pair",
        date_str=_DATE,
    )

    source_edit, target_edit = plan.edits
    assert source_edit.change == "unchanged"
    assert target_edit.archived is True
    assert target_edit.change == "added"
    assert target_edit.updated_bumped is True
    assert target_edit.revision_appended is True

    before = target_edit.original.splitlines()
    after = target_edit.new_text.splitlines()
    added = [line for line in after if line not in before]
    removed = [line for line in before if line not in after]

    assert removed == ["Updated: 2026-01-01"]
    assert added == [
        f"Updated: {_DATE}",
        "- required-by: a.md",
        "Revision:",
        f"- {_DATE}: relate add 'required-by: a.md'; reason: complete the pair",
    ]
    # Nothing else about the archived doc moved.
    for untouched in (
        "Lifecycle: archived",
        "Archived-reason: completed",
        "Role: plan",
        "Project: archiveprobe",
        "- references: a.md",
        "# Old",
        "Historical prose.",
    ):
        assert untouched in target_edit.new_text


def test_plan_relate_remove_marks_both_halves_removed(tmp_path):
    """The `remove` direction at the plan seam — the mirror of the `add` test.

    Nothing else pins `present_before`/`present_after` or
    `change == "removed"` for a removal; the CLI end-to-end test only
    inspects the resulting file text.
    """
    root = _two_doc_root(tmp_path, source_edge="precedes: b.md")
    (root / "b.md").write_text(
        "# B\n\nLifecycle: active\nRole: notes\nProject: relateprobe\n"
        "Updated: 2026-05-20\n\nRelated:\n- follows: a.md\n\n## Body\n\nProse.\n"
    )
    plan = _plan(
        root,
        action="remove",
        source=root / "a.md",
        verb="precedes",
        target=root / "b.md",
        reason=None,
        date_str=_DATE,
    )

    assert plan.action == "remove"
    assert plan.inverse == "follows"
    source_edit, target_edit = plan.edits
    for edit, edge in ((source_edit, "precedes: b.md"), (target_edit, "follows: a.md")):
        assert edit.edge == edge
        assert (edit.present_before, edit.present_after) == (True, False)
        assert edit.change == "removed"
        assert edit.updated_bumped is True
        assert edit.revision_appended is False, "both endpoints are active"
        assert f"- {edge}" not in edit.new_text


def test_plan_relate_remove_of_an_absent_edge_is_unchanged(tmp_path):
    """Idempotent `remove`: nothing present, nothing planned, nothing bumped."""
    root = _two_doc_root(tmp_path)
    plan = _plan(
        root,
        action="remove",
        source=root / "a.md",
        verb="precedes",
        target=root / "b.md",
        reason=None,
        date_str=_DATE,
    )
    for edit in plan.edits:
        assert (edit.present_before, edit.present_after) == (False, False)
        assert edit.change == "unchanged"
        assert edit.updated_bumped is False
        assert edit.new_text == edit.original


def test_apply_relate_plan_writes_both(tmp_path):
    """D5 stage 5: publish source then target; the tree then reads back clean."""
    root = _two_doc_root(tmp_path)
    plan = _plan(
        root,
        action="add",
        source=root / "a.md",
        verb="precedes",
        target=root / "b.md",
        reason=None,
        date_str=_DATE,
    )
    _m25("apply_relate_plan")(plan)

    a_doc = cli.parse((root / "a.md").read_text(), root / "a.md", root)
    b_doc = cli.parse((root / "b.md").read_text(), root / "b.md", root)
    assert ("precedes", "b.md") in a_doc.related
    assert ("follows", "a.md") in b_doc.related


def test_apply_relate_plan_rolls_back_when_second_write_fails(tmp_path):
    """D5: a failed second write leaves NO deliberate half-pair behind.

    Failure injection via `monkeypatch.setattr(cli, "atomic_write", ...)`
    (the `test_atomic_write.py` precedent): the first publish succeeds, the
    second raises `OSError`, and the already-published endpoint must be
    restored byte-for-byte.
    """
    root = _two_doc_root(tmp_path)
    original = {p.name: p.read_bytes() for p in sorted(root.glob("*.md"))}
    plan = _plan(
        root,
        action="add",
        source=root / "a.md",
        verb="precedes",
        target=root / "b.md",
        reason=None,
        date_str=_DATE,
    )

    real_write = cli.atomic_write
    calls: list[Path] = []

    def _failing_write(path: Path, content: str) -> None:
        calls.append(path)
        if len(calls) == 2:
            raise OSError("disk full")
        real_write(path, content)

    error_cls = _m25("CoordinatedWriteError")
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(cli, "atomic_write", _failing_write)
        with pytest.raises(error_cls) as excinfo:
            _m25("apply_relate_plan")(plan)

    assert excinfo.value.rolled_back is True
    assert {p.name: p.read_bytes() for p in sorted(root.glob("*.md"))} == original, (
        "after a handled second-write failure the tree is byte-identical"
    )


def test_apply_relate_plan_rollback_failure_is_reported_not_swallowed(tmp_path):
    """D5: when the restore ALSO fails, say so — never claim atomicity falsely."""
    root = _two_doc_root(tmp_path)
    plan = _plan(
        root,
        action="add",
        source=root / "a.md",
        verb="precedes",
        target=root / "b.md",
        reason=None,
        date_str=_DATE,
    )

    real_write = cli.atomic_write
    calls: list[Path] = []

    def _failing_write(path: Path, content: str) -> None:
        calls.append(path)
        if len(calls) == 1:
            real_write(path, content)
            return
        raise OSError("disk full")

    error_cls = _m25("CoordinatedWriteError")
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(cli, "atomic_write", _failing_write)
        with pytest.raises(error_cls) as excinfo:
            _m25("apply_relate_plan")(plan)

    assert excinfo.value.rolled_back is False
    assert "a.md" in excinfo.value.published, (
        "the admission names every endpoint left carrying the new edge"
    )
    # The MESSAGE is the operator-facing contract, not just the two flags:
    # `_cmd_relate` prints `docs: relate: {exc}` verbatim.
    assert str(excinfo.value) == (
        "write failed for b.md: disk full; ROLLBACK FAILED for a.md — "
        "repair manually: a.md still carries 'precedes: b.md'"
    )


def test_apply_relate_plan_rollback_failure_of_a_remove_says_no_longer_carries(tmp_path):
    """M25 — R4: the ROLLBACK FAILED admission is action-shaped.

    After a failed rollback of a `remove`, the published file NO LONGER
    carries the edge. The add-shaped wording (`still carries`) would hand
    the operator a factually inverted repair instruction — it would tell
    them to delete a bullet that is already gone. Nothing else pins this
    half, so R4's entire point rests here.
    """
    root = _two_doc_root(tmp_path, source_edge="precedes: b.md")
    (root / "b.md").write_text(
        "# B\n\nLifecycle: active\nRole: notes\nProject: relateprobe\n"
        "Updated: 2026-05-20\n\nRelated:\n- follows: a.md\n\n## Body\n\nProse.\n"
    )
    plan = _plan(
        root,
        action="remove",
        source=root / "a.md",
        verb="precedes",
        target=root / "b.md",
        reason=None,
        date_str=_DATE,
    )

    real_write = cli.atomic_write
    calls: list[Path] = []

    def _failing_write(path: Path, content: str) -> None:
        calls.append(path)
        if len(calls) == 1:
            real_write(path, content)
            return
        raise OSError("disk full")

    error_cls = _m25("CoordinatedWriteError")
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(cli, "atomic_write", _failing_write)
        with pytest.raises(error_cls) as excinfo:
            _m25("apply_relate_plan")(plan)

    assert excinfo.value.rolled_back is False
    assert excinfo.value.published == ("a.md",)
    assert str(excinfo.value) == (
        "write failed for b.md: disk full; ROLLBACK FAILED for a.md — "
        "repair manually: a.md no longer carries 'precedes: b.md'"
    )


def test_relate_plan_to_json_shape(tmp_path):
    """D3: one operation-plan record; `edits` is always `[source, target]`."""
    root = _two_doc_root(tmp_path)
    plan = _plan(
        root,
        action="add",
        source=root / "a.md",
        verb="precedes",
        target=root / "b.md",
        reason=None,
        date_str=_DATE,
    )
    record = _m25("relate_plan_to_json")(plan, dry_run=False, applied=True, index_refreshed=True)

    assert set(record) == {
        "action",
        "verb",
        "inverse",
        "source",
        "target",
        "reason",
        "date",
        "dry_run",
        "applied",
        "index_refreshed",
        "edits",
    }
    assert record["action"] == "add"
    assert record["verb"] == "precedes"
    assert record["inverse"] == "follows"
    assert record["source"] == "a.md"
    assert record["target"] == "b.md"
    assert record["reason"] is None
    assert record["date"] == _DATE
    assert record["dry_run"] is False
    assert record["applied"] is True
    assert record["index_refreshed"] is True

    edits = record["edits"]
    assert [e["path"] for e in edits] == ["a.md", "b.md"]
    for edit in edits:
        assert set(edit) == {
            "path",
            "archived",
            "edge",
            "present_before",
            "present_after",
            "change",
            "updated_bumped",
            "revision_appended",
        }
        assert edit["change"] in {"added", "removed", "unchanged"}


# ===========================================================================
# Free-form edges at the seam (milestone `lifecycle-and-free-form-relate` —
# D4–D6; *Decisions (Phase 1 — BINDING)* › P1.2 and the P1.9 signatures).
# Today `plan_relate` raises `ValueError` for every verb outside the six
# recognized ones; `_plan_one_sided` reports that refusal as the missing
# behaviour, so these tests are RED on an assertion, not on a stray error.
# ===========================================================================


def _symbol(name: str) -> Any:
    """Fetch a seam symbol that may not exist yet — a clean `AttributeError`,
    never a collection error (ruff's B009 forbids a literal `getattr`)."""
    return getattr(cli, name)


def _plan_one_sided(root: Path, **kwargs: Any) -> Any:
    """Plan a free-form edge; a refusal to plan one is the behaviour under test."""
    try:
        return _plan(root, **kwargs)
    except ValueError as exc:
        raise AssertionError(f"plan_relate must plan a free-form edge one-sided: {exc}") from exc


def test_plan_relate_free_form_stages_only_the_source(tmp_path):
    """D4: one edit — SOURCE's — and no inverse; planning stays pure."""
    root = _two_doc_root(tmp_path)
    before = {p: p.read_bytes() for p in sorted(root.glob("*.md"))}

    plan = _plan_one_sided(
        root,
        action="add",
        source=root / "a.md",
        verb="pairs-with",
        target=root / "b.md",
        reason=None,
        date_str=_DATE,
    )

    assert {p: p.read_bytes() for p in sorted(root.glob("*.md"))} == before
    assert plan.inverse is None
    assert (plan.verb, plan.source_rel, plan.target_rel) == ("pairs-with", "a.md", "b.md")
    assert [(e.rel, e.edge, e.change) for e in plan.edits] == [
        ("a.md", "pairs-with: b.md", "added")
    ]
    assert plan.edits[0].updated_bumped is True
    assert plan.edits[0].revision_appended is False


def test_plan_relate_free_form_never_reads_the_target(tmp_path):
    """D5: TARGET is never read — a non-UTF-8 binary target would raise
    `UnicodeDecodeError` the moment anything tried."""
    root = _two_doc_root(tmp_path)
    (root / "deck.bin").write_bytes(b"\xff\xfe\x00 not utf-8 \x80\x81")

    plan = _plan_one_sided(
        root,
        action="add",
        source=root / "a.md",
        verb="artifact-of",
        target=root / "deck.bin",
        reason=None,
        date_str=_DATE,
    )

    assert [(e.rel, e.edge) for e in plan.edits] == [("a.md", "artifact-of: deck.bin")]


def test_plan_relate_free_form_refuses_an_archived_source(tmp_path):
    """D5: the planner plans a free-form edge from an active SOURCE to an
    archived TARGET, and refuses the same verb from the archived SOURCE — the
    guard behind R2, specific to the source, not to the verb."""
    root = _archived_pair_root(tmp_path)
    archived = root / "archive" / "2026-01-01" / "old.md"

    toward = _plan_one_sided(
        root,
        action="add",
        source=root / "a.md",
        verb="references",
        target=archived,
        reason=None,
        date_str=_DATE,
    )
    assert [e.rel for e in toward.edits] == ["a.md"], "an archived TARGET is fine"

    with pytest.raises(ValueError):
        _plan(
            root,
            action="add",
            source=archived,
            verb="references",
            target=root / "a.md",
            reason="context",
            date_str=_DATE,
        )


@pytest.mark.parametrize(
    "verb",
    ["see also", "Pairs-With", "pairs:with", "pairs-with\n", ""],
    ids=["an-internal-space", "uppercase", "a-colon", "a-trailing-newline", "an-empty-verb"],
)
def test_plan_relate_refuses_a_verb_outside_the_grammar(tmp_path, verb):
    """The planner's guard is the grammar, not the recognized list: it plans a
    grammar-valid free-form verb and refuses an out-of-grammar one."""
    root = _two_doc_root(tmp_path)
    kwargs: dict[str, Any] = {
        "action": "add",
        "source": root / "a.md",
        "target": root / "b.md",
        "reason": None,
        "date_str": _DATE,
    }
    _plan_one_sided(root, verb="pairs-with", **kwargs)

    with pytest.raises(ValueError):
        _plan(root, verb=verb, **kwargs)


def test_relate_plan_to_json_free_form_record_has_null_inverse_and_one_edit(tmp_path):
    """C15: the recognized record's eleven keys, `inverse: null`, one edit."""
    root = _two_doc_root(tmp_path)
    plan = _plan_one_sided(
        root,
        action="add",
        source=root / "a.md",
        verb="pairs-with",
        target=root / "b.md",
        reason=None,
        date_str=_DATE,
    )

    record = _m25("relate_plan_to_json")(plan, dry_run=False, applied=True, index_refreshed=True)

    assert record["inverse"] is None
    assert len(record["edits"]) == 1
    assert record["edits"][0]["path"] == "a.md"
    assert set(record) == {
        "action",
        "verb",
        "inverse",
        "source",
        "target",
        "reason",
        "date",
        "dry_run",
        "applied",
        "index_refreshed",
        "edits",
    }


def test_apply_relate_plan_writes_only_the_source_for_a_free_form_edge(tmp_path):
    """Apply publishes SOURCE and leaves TARGET's file alone — its bytes and
    its inode, so it was not rewritten either."""
    root = _two_doc_root(tmp_path)
    target = root / "b.md"
    target_bytes, target_inode = target.read_bytes(), target.stat().st_ino
    plan = _plan_one_sided(
        root,
        action="add",
        source=root / "a.md",
        verb="pairs-with",
        target=target,
        reason=None,
        date_str=_DATE,
    )

    _m25("apply_relate_plan")(plan)

    assert "- pairs-with: b.md" in (root / "a.md").read_text()
    assert (target.read_bytes(), target.stat().st_ino) == (target_bytes, target_inode)


def test_relate_verb_grammar_accepts_and_rejects_generated_verbs():
    """D6 at the pure predicate, with independently generated valid and
    invalid verbs (fixed seed): over-acceptance and over-refusal both fail."""
    in_grammar = _symbol("relate_verb_in_grammar")
    rng = random.Random(20261027)
    tail = string.ascii_lowercase + string.digits + "-"

    for _ in range(300):
        length = rng.choice([0, 1, 2, 3, 8, 30, 80])
        verb = rng.choice(string.ascii_lowercase) + "".join(rng.choice(tail) for _ in range(length))
        assert in_grammar(verb) is True, verb

    defects = [
        string.ascii_uppercase,
        string.digits,
        "-",
        " \t",
        ":",
        "\n\r",
        "_.@#!$/,;'\"",
        "éßøΩж",
        "٣१１",
    ]
    for _ in range(300):
        base = rng.choice(string.ascii_lowercase) + "".join(
            rng.choice(tail) for _ in range(rng.randrange(6))
        )
        pool = rng.choice(defects)
        if pool in (string.digits, "-"):
            verb = rng.choice(pool) + base  # a leading digit or hyphen
        else:
            cut = rng.randrange(len(base) + 1)
            verb = base[:cut] + rng.choice(pool) + base[cut:]
        assert in_grammar(verb) is False, repr(verb)
    assert in_grammar("") is False
