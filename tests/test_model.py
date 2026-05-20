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
    parse,
)

WELL_FORMED = """\
# Title

Status: active
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
    assert len(BUILTIN_ROLES) == 13


def test_parse_happy_path(tmp_path):
    path = tmp_path / "doc.md"
    doc = parse(WELL_FORMED, path, tmp_path)
    assert doc.path == path
    assert doc.title == "Title"
    assert doc.status == "active"
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
    text = _write_text("Status: active\nRole: spec\nUpdated: 2026-05-20")
    doc = parse(text, tmp_path / "doc.md", tmp_path)
    assert doc.related == ()


def test_parse_no_project_field(tmp_path):
    """Project is optional; absence yields project=None."""
    text = _write_text("Status: active\nRole: spec\nUpdated: 2026-05-20")
    doc = parse(text, tmp_path / "doc.md", tmp_path)
    assert doc.project is None


def test_parse_extra_labels_harvested(tmp_path):
    text = textwrap.dedent("""\
        # Title

        Status: active
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
    text = "Status: active\nRole: spec\nUpdated: 2026-05-20\n\nbody\n"
    with pytest.raises(MetadataError, match="H1"):
        parse(text, tmp_path / "no-h1.md", tmp_path)


def test_parse_missing_status(tmp_path):
    text = _write_text("Role: spec\nUpdated: 2026-05-20")
    with pytest.raises(MetadataError, match=r"Status"):
        parse(text, tmp_path / "no-status.md", tmp_path)


def test_parse_missing_role(tmp_path):
    text = _write_text("Status: active\nUpdated: 2026-05-20")
    with pytest.raises(MetadataError, match=r"Role"):
        parse(text, tmp_path / "no-role.md", tmp_path)


def test_parse_missing_updated(tmp_path):
    text = _write_text("Status: active\nRole: spec")
    with pytest.raises(MetadataError, match=r"Updated"):
        parse(text, tmp_path / "no-updated.md", tmp_path)


def test_parse_malformed_updated(tmp_path):
    text = _write_text("Status: active\nRole: spec\nUpdated: not-a-date")
    with pytest.raises(MetadataError, match=r"Updated"):
        parse(text, tmp_path / "bad-date.md", tmp_path)


def test_parse_unknown_status(tmp_path):
    text = _write_text("Status: in-progress\nRole: spec\nUpdated: 2026-05-20")
    with pytest.raises(VocabularyError, match=r"Status"):
        parse(text, tmp_path / "bad-status.md", tmp_path)


def test_parse_unknown_role(tmp_path):
    text = _write_text("Status: active\nRole: nonsense\nUpdated: 2026-05-20")
    with pytest.raises(VocabularyError, match=r"Role"):
        parse(text, tmp_path / "bad-role.md", tmp_path)


def test_parse_metadata_block_terminates_at_blank_line(tmp_path):
    """Lines that look like `Label: value` AFTER the blank line are body, not metadata."""
    text = textwrap.dedent("""\
        # Title

        Status: active
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
    assert doc.status in BUILTIN_STATUSES
    assert doc.role in BUILTIN_ROLES
