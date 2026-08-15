"""Parser unit tests (Phase 2 — written RED).

Targets: `parse()`, `Doc`, `MetadataError`, `VocabularyError`.
"""

from __future__ import annotations

import textwrap
from datetime import date

import pytest

from docs import (
    BUILTIN_ROLES,
    BUILTIN_STATUSES,
    MetadataError,
    VocabularyError,
    doc_to_json,
    load_config,
    parse,
)

WELL_FORMED = """\
# Title

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-05-20

Related:
- pairs-with: other.md
- implements: charter.md

## First section

First paragraph of body.
"""


def _write_text(metadata_lines: str, body: str = "body") -> str:
    return f"# Title\n\n{metadata_lines}\n\n{body}\n"


def test_builtin_vocab_sizes():
    assert len(BUILTIN_STATUSES) == 6
    # M7 (F10/OQ-A) adds 7 new core roles: implementation, sketch, outline,
    # memo, brief, template, example. Total: 13 + 7 = 20.
    assert len(BUILTIN_ROLES) == 20


def test_parse_happy_path(tmp_path):
    path = tmp_path / "doc.md"
    doc = parse(WELL_FORMED, path, tmp_path)
    assert doc.path == path
    assert doc.title == "Title"
    assert doc.lifecycle == "active"
    assert doc.role == "spec"
    assert doc.project == "docs"
    assert doc.updated == date(2026, 5, 20)
    assert doc.related == (
        ("pairs-with", "other.md"),
        ("implements", "charter.md"),
    )
    assert doc.archived is False
    assert "First paragraph of body." in doc.body


def test_parse_body_starts_after_metadata_block(tmp_path):
    doc = parse(WELL_FORMED, tmp_path / "doc.md", tmp_path)
    assert doc.body.lstrip().startswith("## First section")


def test_parse_no_related_block(tmp_path):
    text = _write_text("Lifecycle: active\nRole: spec\nUpdated: 2026-05-20")
    doc = parse(text, tmp_path / "doc.md", tmp_path)
    assert doc.related == ()


def test_parse_no_project_field(tmp_path):
    """Project is optional; absence yields project=None."""
    text = _write_text("Lifecycle: active\nRole: spec\nUpdated: 2026-05-20")
    doc = parse(text, tmp_path / "doc.md", tmp_path)
    assert doc.project is None


def test_parse_extra_labels_harvested(tmp_path):
    text = textwrap.dedent("""\
        # Title

        Lifecycle: active
        Role: spec
        Updated: 2026-05-20
        Owner: art
        Tags:
        - alpha
        - beta

        body
        """)
    doc = parse(text, tmp_path / "extra.md", tmp_path)
    assert doc.extra["Owner"] == "art"
    assert doc.extra["Tags"] == ("alpha", "beta")


def test_parse_missing_h1(tmp_path):
    text = "Lifecycle: active\nRole: spec\nUpdated: 2026-05-20\n\nbody\n"
    with pytest.raises(MetadataError, match="H1"):
        parse(text, tmp_path / "no-h1.md", tmp_path)


def test_parse_missing_status(tmp_path):
    text = _write_text("Role: spec\nUpdated: 2026-05-20")
    with pytest.raises(MetadataError, match=r"Lifecycle"):
        parse(text, tmp_path / "no-status.md", tmp_path)


def test_parse_missing_role(tmp_path):
    text = _write_text("Lifecycle: active\nUpdated: 2026-05-20")
    with pytest.raises(MetadataError, match=r"Role"):
        parse(text, tmp_path / "no-role.md", tmp_path)


def test_parse_missing_updated(tmp_path):
    text = _write_text("Lifecycle: active\nRole: spec")
    with pytest.raises(MetadataError, match=r"Updated"):
        parse(text, tmp_path / "no-updated.md", tmp_path)


def test_parse_malformed_updated(tmp_path):
    text = _write_text("Lifecycle: active\nRole: spec\nUpdated: not-a-date")
    with pytest.raises(MetadataError, match=r"Updated"):
        parse(text, tmp_path / "bad-date.md", tmp_path)


def test_parse_unknown_status(tmp_path):
    text = _write_text("Lifecycle: in-progress\nRole: spec\nUpdated: 2026-05-20")
    with pytest.raises(VocabularyError, match=r"Lifecycle"):
        parse(text, tmp_path / "bad-status.md", tmp_path)


def test_parse_unknown_role(tmp_path):
    text = _write_text("Lifecycle: active\nRole: nonsense\nUpdated: 2026-05-20")
    with pytest.raises(VocabularyError, match=r"Role"):
        parse(text, tmp_path / "bad-role.md", tmp_path)


def test_parse_metadata_block_terminates_at_blank_line(tmp_path):
    """Lines that look like `Label: value` AFTER the blank line are body, not metadata."""
    text = textwrap.dedent("""\
        # Title

        Lifecycle: active
        Role: spec
        Updated: 2026-05-20

        FakeLabel: this is body, not metadata.

        Real body paragraph.
        """)
    doc = parse(text, tmp_path / "doc.md", tmp_path)
    # FakeLabel: line is in body, not in extra.
    assert "FakeLabel" not in doc.extra
    assert "FakeLabel: this is body" in doc.body


def test_parse_archived_flag_is_false_by_default(tmp_path):
    """parse() always sets archived=False; the walker overrides based on path location."""
    doc = parse(WELL_FORMED, tmp_path / "doc.md", tmp_path)
    assert doc.archived is False


def test_parse_fixture_well_formed(fixtures_dir):
    """Real fixture file (created in Phase 3)."""
    path = fixtures_dir / "parser" / "well-formed.md"
    text = path.read_text()
    doc = parse(text, path, fixtures_dir / "parser")
    assert doc.title  # non-empty
    assert doc.lifecycle in BUILTIN_STATUSES
    assert doc.role in BUILTIN_ROLES


# --- M28a (B) — `Archived:` stays OUT of `parse()`'s `known` set -----------


def test_parse_harvests_archived_into_extra(tmp_path):
    """Item (B)'s deliberate NON-change: `Archived:` is not promoted to a
    first-class `Doc` attribute, so it surfaces through `Doc.extra` exactly as
    `Archived-reason:` and `Revision:` already do.

    GREEN at baseline and a genuine lock: a Phase-5 implementer adding the
    label to `known` would silently drop it from `docs list --json`'s
    `extra_fields`, widening a record M28a promises not to touch.
    """
    text = (
        "# Old\n\nLifecycle: archived\nRole: spec\nProject: docs\n"
        "Updated: 2026-01-01\nArchived: 2026-01-01\nArchived-reason: closed out\n\nbody\n"
    )
    doc = parse(text, tmp_path / "old.md", tmp_path)
    assert doc.extra["Archived"] == "2026-01-01"
    assert doc.extra["Archived-reason"] == "closed out"


def test_doc_to_json_surfaces_archived_under_extra_fields(tmp_path):
    """*Also settled*: M28a adds no field to any JSON record. The witness
    travels in `extra_fields`, and `docs list --json`'s top-level key set is
    unchanged."""
    (tmp_path / ".docs.toml").write_text('[project]\nname = "docs"\n')
    text = (
        "# Old\n\nLifecycle: archived\nRole: spec\nProject: docs\n"
        "Updated: 2026-01-01\nArchived: 2026-01-01\n\nbody\n"
    )
    path = tmp_path / "old.md"
    path.write_text(text)
    record = doc_to_json(parse(text, path, tmp_path), load_config(tmp_path), tmp_path)
    assert set(record) == {
        "path",
        "title",
        "lifecycle",
        "role",
        "project",
        "updated",
        "related",
        "extra_fields",
    }
    assert record["extra_fields"]["Archived"] == "2026-01-01"
