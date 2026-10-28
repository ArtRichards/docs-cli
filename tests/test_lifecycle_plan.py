"""The pure `docs lifecycle` planner: `plan_lifecycle`, `apply_lifecycle_plan`
and `lifecycle_plan_to_json`.

The contract under test is the task plan's *Decisions (Phase 1 — BINDING)*
› P1.1 and the frozen signatures in P1.9, for milestone
`lifecycle-and-free-form-relate` (D1–D3). A separate module from the CLI
tests, as `test_relate_plan.py` and `test_archive_plan.py` are (P1, OQ-12).

Every symbol under test lands in Phase 5. They are fetched through
`_symbol(name)` rather than imported, so collection stays clean, the RED
reason is a single honest `AttributeError`, and `mypy src/ tests/` stays
green at baseline (`getattr` yields `Any`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from docs_cli import cli

_DATE = "2026-10-27"


def _symbol(name: str) -> Any:
    """Fetch a planner symbol that may not exist yet (a missing one is a clean
    `AttributeError`, not a collection error; a literal `getattr(cli, "…")`
    would trip ruff's B009)."""
    return getattr(cli, name)


def _doc(title: str, lifecycle: str, *, updated: str = "2026-05-20") -> str:
    return (
        f"# {title}\n\nLifecycle: {lifecycle}\nRole: notes\nProject: plantree\n"
        f"Updated: {updated}\n\nRelated:\n- pairs-with: other.md\n\n## Body\n\nProse.\n"
    )


def _root(tmp_path: Path, docs: dict[str, str], *, sidecar_extra: str = "") -> Path:
    root = tmp_path / "plantree"
    root.mkdir()
    (root / ".docs.toml").write_text(f'[project]\nname = "plantree"\n{sidecar_extra}')
    (root / "other.md").write_text(_doc("Other", "active"))
    for rel, text in docs.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


def _plan(root: Path, names: list[str], state: str) -> Any:
    config = cli.load_config(root)
    return _symbol("plan_lifecycle")(
        root, config, files=[root / name for name in names], state=state, date_str=_DATE
    )


def test_plan_lifecycle_stages_only_the_documents_whose_state_differs(tmp_path):
    """Planning is pure and per document: the draft is staged as `set`, the
    document already in the state as `unchanged` with its text as read."""
    draft, active = _doc("A", "draft"), _doc("B", "active")
    root = _root(tmp_path, {"a.md": draft, "b.md": active})
    before = {p: p.read_bytes() for p in sorted(root.glob("*.md"))}

    plan = _plan(root, ["a.md", "b.md"], "active")

    assert {p: p.read_bytes() for p in sorted(root.glob("*.md"))} == before, "planning is pure"
    assert (plan.state, plan.date_str) == ("active", _DATE)
    assert [(e.rel, e.before, e.change) for e in plan.edits] == [
        ("a.md", "draft", "set"),
        ("b.md", "active", "unchanged"),
    ]
    assert plan.edits[1].new_text == active


def test_plan_lifecycle_bumps_updated_only_where_lifecycle_moved(tmp_path):
    """D3: the edit is `Lifecycle:` then `Updated:`, and only on a document
    whose lifecycle actually changed — every other byte is preserved."""
    draft, active = _doc("A", "draft"), _doc("B", "active")
    root = _root(tmp_path, {"a.md": draft, "b.md": active})

    plan = _plan(root, ["a.md", "b.md"], "active")

    expected = draft.replace("Lifecycle: draft", "Lifecycle: active").replace(
        "Updated: 2026-05-20", f"Updated: {_DATE}"
    )
    assert plan.edits[0].new_text == expected
    assert "Updated: 2026-05-20" in plan.edits[1].new_text


def test_plan_lifecycle_refuses_archived_as_a_state(tmp_path):
    """A programming-error guard behind L5: no spelling reaches `archived`."""
    root = _root(tmp_path, {"a.md": _doc("A", "done")})
    with pytest.raises(ValueError):
        _plan(root, ["a.md"], "archived")


def test_plan_lifecycle_refuses_an_unknown_state(tmp_path):
    """The guard behind L6: a state outside the configured vocabulary."""
    root = _root(tmp_path, {"a.md": _doc("A", "draft")})
    with pytest.raises(ValueError):
        _plan(root, ["a.md"], "Archived")


def test_plan_lifecycle_refuses_a_source_under_the_archive_subtree(tmp_path):
    """The guard behind L7: an archived document is never a source. The
    document reads `done`, not `archived`, so its location alone must refuse
    it — the guard on its current `Lifecycle:` cannot."""
    root = _root(tmp_path, {"archive/2026-01-01/old.md": _doc("Old", "done")})
    with pytest.raises(ValueError):
        _plan(root, ["archive/2026-01-01/old.md"], "active")


def test_plan_lifecycle_refuses_a_source_already_marked_archived(tmp_path):
    """The guard behind L11: an active-tree document reading `archived`."""
    root = _root(tmp_path, {"stray.md": _doc("Stray", "archived")})
    with pytest.raises(ValueError):
        _plan(root, ["stray.md"], "active")


def test_plan_lifecycle_lists_a_duplicated_document_once(tmp_path):
    """Deduplicated on the root-relative path, first occurrence kept (OQ-3)."""
    root = _root(tmp_path, {"a.md": _doc("A", "draft"), "b.md": _doc("B", "draft")})
    (root / "sub").mkdir()  # so `sub/../a.md` is a real second spelling, not a dangling one

    plan = _plan(root, ["a.md", "b.md", "./a.md", "sub/../a.md"], "active")

    assert [e.rel for e in plan.edits] == ["a.md", "b.md"]


def test_plan_lifecycle_accepts_a_configured_extension_state(tmp_path):
    """D2 through D10: an `add_lifecycles` state is a valid target, and a
    document already in it parses as a source."""
    root = _root(
        tmp_path,
        {"a.md": _doc("A", "draft"), "b.md": _doc("B", "shipped")},
        sidecar_extra='\n[vocabulary]\nadd_lifecycles = ["shipped"]\n',
    )

    plan = _plan(root, ["a.md", "b.md"], "shipped")

    assert [(e.rel, e.before, e.change) for e in plan.edits] == [
        ("a.md", "draft", "set"),
        ("b.md", "shipped", "unchanged"),
    ]
    assert "Lifecycle: shipped" in plan.edits[0].new_text


def test_apply_lifecycle_plan_writes_only_the_changed_documents(tmp_path):
    """Apply writes each `set` edit and leaves an `unchanged` document's file
    alone — not merely its bytes: its inode survives, so it was not rewritten."""
    draft, active = _doc("A", "draft"), _doc("B", "active")
    root = _root(tmp_path, {"a.md": draft, "b.md": active})
    untouched_inode = (root / "b.md").stat().st_ino

    plan = _plan(root, ["a.md", "b.md"], "active")
    _symbol("apply_lifecycle_plan")(plan)

    assert (root / "a.md").read_text() == plan.edits[0].new_text
    assert "Lifecycle: active" in (root / "a.md").read_text()
    assert (root / "b.md").read_text() == active
    assert (root / "b.md").stat().st_ino == untouched_inode


def test_lifecycle_plan_to_json_has_a_closed_key_set(tmp_path):
    """C15: the record and each edit carry exactly the frozen keys."""
    root = _root(tmp_path, {"a.md": _doc("A", "draft"), "b.md": _doc("B", "active")})
    plan = _plan(root, ["a.md", "b.md"], "active")

    record = _symbol("lifecycle_plan_to_json")(
        plan, dry_run=False, applied=True, index_refreshed=True
    )

    assert set(record) == {"state", "date", "dry_run", "applied", "index_refreshed", "edits"}
    assert (record["state"], record["date"]) == ("active", _DATE)
    assert (record["dry_run"], record["applied"], record["index_refreshed"]) == (
        False,
        True,
        True,
    )
    assert record["edits"] == [
        {"path": "a.md", "before": "draft", "change": "set"},
        {"path": "b.md", "before": "active", "change": "unchanged"},
    ]
