"""Unit tests for the M2 doc-editing helpers (Phase 2 — written RED).

`set_metadata_field`, `rewrite_related_refs`, and `scaffold_doc` do the
surgical, minimal-diff metadata writes the mutating verbs rely on. These
tests pin the byte-preservation contract before Phase 5 implements them.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from docs import (
    MetadataError,
    parse,
    rewrite_related_refs,
    scaffold_doc,
    set_metadata_field,
)

_ROOT = Path("/docs")
_PATH = _ROOT / "sample.md"

WELL_FORMED = """\
# Sample Doc

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-05-20
Owner: art

Related:
- pairs-with: other.md
- implements: charter.md

## Body

First paragraph.
"""


# --- set_metadata_field -----------------------------------------------------


def test_set_metadata_field_replaces_existing_value():
    out = set_metadata_field(WELL_FORMED, "Updated", "2026-05-21")
    assert "Updated: 2026-05-21" in out
    assert "Updated: 2026-05-20" not in out


def test_set_metadata_field_preserves_every_other_line():
    out = set_metadata_field(WELL_FORMED, "Updated", "2026-05-21")
    before = WELL_FORMED.splitlines()
    after = out.splitlines()
    assert len(before) == len(after)
    diffs = [(b, a) for b, a in zip(before, after, strict=True) if b != a]
    assert diffs == [("Updated: 2026-05-20", "Updated: 2026-05-21")]


def test_set_metadata_field_replaces_lifecycle_without_disturbing_related():
    out = set_metadata_field(WELL_FORMED, "Lifecycle", "archived")
    assert "Lifecycle: archived" in out
    assert "Lifecycle: active" not in out
    # The blank line before Related: and the Related block survive intact.
    assert "\nRelated:\n- pairs-with: other.md\n- implements: charter.md\n" in out


def test_set_metadata_field_inserts_missing_label_inside_block():
    out = set_metadata_field(WELL_FORMED, "Archived-reason", "superseded by v2")
    assert "Archived-reason: superseded by v2" in out
    # Inserted within the inline metadata run, ahead of the Related: group.
    assert out.index("Archived-reason:") < out.index("Related:")
    doc = parse(out, _PATH, _ROOT)
    assert doc.extra["Archived-reason"] == "superseded by v2"


def test_set_metadata_field_ignores_label_shaped_lines_in_body():
    text = (
        "# T\n\nLifecycle: active\nRole: notes\nUpdated: 2026-05-20\n\n"
        "## Body\n\nUpdated: this line is prose, not metadata.\n"
    )
    out = set_metadata_field(text, "Updated", "2026-05-21")
    assert "Updated: 2026-05-21" in out
    assert "Updated: this line is prose, not metadata." in out


def test_set_metadata_field_preserves_trailing_newline_state():
    with_nl = "# T\n\nLifecycle: active\nRole: notes\nUpdated: 2026-05-20\n"
    without_nl = "# T\n\nLifecycle: active\nRole: notes\nUpdated: 2026-05-20"
    assert set_metadata_field(with_nl, "Updated", "2026-05-21").endswith("\n")
    assert not set_metadata_field(without_nl, "Updated", "2026-05-21").endswith("\n")


def test_set_metadata_field_raises_without_metadata_block():
    with pytest.raises(MetadataError):
        set_metadata_field("plain text, no H1 at all\n", "Updated", "2026-05-21")


# --- rewrite_related_refs ---------------------------------------------------


def test_rewrite_related_refs_rewrites_matching_target():
    out, n = rewrite_related_refs(WELL_FORMED, "other.md", "renamed.md")
    assert n == 1
    assert "- pairs-with: renamed.md" in out
    assert "other.md" not in out


def test_rewrite_related_refs_preserves_the_verb():
    out, n = rewrite_related_refs(WELL_FORMED, "other.md", "renamed.md")
    assert n == 1
    assert out.count("pairs-with: renamed.md") == 1


def test_rewrite_related_refs_is_noop_when_nothing_matches():
    out, n = rewrite_related_refs(WELL_FORMED, "absent.md", "x.md")
    assert n == 0
    assert out == WELL_FORMED


def test_rewrite_related_refs_rewrites_multiple_bullets():
    text = (
        "# T\n\nLifecycle: active\nRole: notes\nUpdated: 2026-05-20\n\n"
        "Related:\n- child-of: dup.md\n- references: dup.md\n"
    )
    out, n = rewrite_related_refs(text, "dup.md", "moved.md")
    assert n == 2
    assert "dup.md" not in out
    assert "- child-of: moved.md" in out
    assert "- references: moved.md" in out


# --- scaffold_doc -----------------------------------------------------------


def test_scaffold_doc_round_trips_through_parse():
    text = scaffold_doc("My Feature", "spec", "docs", date(2026, 5, 21))
    doc = parse(text, _PATH, _ROOT)
    assert doc.title == "My Feature"
    assert doc.lifecycle == "draft"
    assert doc.role == "spec"
    assert doc.project == "docs"
    assert doc.updated == date(2026, 5, 21)


def test_scaffold_doc_omits_project_line_when_none():
    text = scaffold_doc("Untitled", "notes", None, date(2026, 5, 21))
    assert "Project:" not in text
    doc = parse(text, _PATH, _ROOT)
    assert doc.project is None


def test_scaffold_doc_ends_with_single_trailing_newline():
    text = scaffold_doc("T", "notes", "docs", date(2026, 5, 21))
    assert text.endswith("\n")
    assert not text.endswith("\n\n")
