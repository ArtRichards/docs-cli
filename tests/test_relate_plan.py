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

from pathlib import Path

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
