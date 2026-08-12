"""Unit tests for the M2 doc-editing helpers (Phase 2 — written RED).

`set_metadata_field`, `rewrite_related_refs`, and `scaffold_doc` do the
surgical, minimal-diff metadata writes the mutating verbs rely on. These
tests pin the byte-preservation contract before Phase 5 implements them.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

import docs as _cli
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


# --- M25 (D3 / D4) — reciprocal edge + revision editors ---------------------
#
# Phase 2 (written RED). Every test here fails with a clean `AttributeError`
# from `getattr(_cli, ...)` until Phase 5 lands the three editors. Accessing
# them via getattr (rather than a module-level import of a missing name)
# keeps collection clean and keeps mypy honest — the result is `Any`.

NO_RELATED = """\
# Solo Doc

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-05-20

## Body

First paragraph.
"""

ARCHIVED_WITH_REVISION = """\
# Old Doc

Lifecycle: archived
Role: plan
Project: docs
Updated: 2026-01-01
Archived-reason: completed

Related:
- required-by: a.md

Revision:
- 2026-08-11: relate add 'required-by: a.md'; reason: complete the M25 pair

## Body

Prose.
"""


NO_BODY = """\
# Tail Doc

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-05-20

Related:
- pairs-with: other.md
- implements: charter.md
"""

NO_BODY_SINGLE_EDGE = """\
# Solo Doc

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-05-20

Related:
- blocks: b.md
"""

REVISION_NO_RELATED = """\
# Stripped Doc

Lifecycle: archived
Role: plan
Project: docs
Updated: 2026-01-01
Archived-reason: completed

Revision:
- 2026-08-11: relate remove 'follows: a.md'; reason: wrong

## Body

Prose.
"""


def _m25(name: str):
    """Fetch an M25 editor that does not exist yet.

    The indirection is deliberate: a module-level import of a missing name
    would be a COLLECTION error, and a literal `getattr(_cli, "…")` trips
    ruff's B009. This keeps the RED reason a single clean `AttributeError`
    and keeps mypy green (the result is `Any`).
    """
    return getattr(_cli, name)


def _add_related_edge(*args, **kwargs):
    return _m25("add_related_edge")(*args, **kwargs)


def _remove_related_edge(*args, **kwargs):
    return _m25("remove_related_edge")(*args, **kwargs)


def _append_revision_entry(*args, **kwargs):
    return _m25("append_revision_entry")(*args, **kwargs)


def test_add_related_edge_appends_to_existing_group():
    """The new bullet lands at the end of the existing `Related:` run."""
    out, changed = _add_related_edge(WELL_FORMED, "precedes", "next.md")
    assert changed is True
    assert (
        "\nRelated:\n- pairs-with: other.md\n- implements: charter.md\n- precedes: next.md\n" in out
    )


def test_add_related_edge_changes_no_other_byte():
    """M2 surgical minimal-diff contract: exactly one line is inserted."""
    out, _changed = _add_related_edge(WELL_FORMED, "precedes", "next.md")
    before = WELL_FORMED.splitlines()
    after = out.splitlines()
    assert len(after) == len(before) + 1
    assert [line for line in after if line != "- precedes: next.md"] == before


def test_add_related_edge_creates_the_group_when_absent():
    """A doc with no `Related:` group gets one, correctly blank-line separated."""
    out, changed = _add_related_edge(NO_RELATED, "blocks", "other.md")
    assert changed is True
    assert "\nRelated:\n- blocks: other.md\n" in out
    doc = parse(out, _PATH, _ROOT)
    assert ("blocks", "other.md") in doc.related
    assert doc.title == "Solo Doc"
    assert doc.body.strip().startswith("## Body")


def test_add_related_edge_result_reparses_and_yields_the_edge():
    out, _changed = _add_related_edge(WELL_FORMED, "depends-on", "dep.md")
    doc = parse(out, _PATH, _ROOT)
    assert ("depends-on", "dep.md") in doc.related
    # The pre-existing free-form edges survive untouched, in order.
    assert doc.related[:2] == (("pairs-with", "other.md"), ("implements", "charter.md"))


def test_add_related_edge_is_a_no_op_when_present():
    """Idempotency at the editor seam: unchanged text, `False`."""
    out, changed = _add_related_edge(WELL_FORMED, "pairs-with", "other.md")
    assert changed is False
    assert out == WELL_FORMED


def test_add_related_edge_inserts_at_end_of_related_run_not_after_revision():
    """With a trailing `Revision:` group, the bullet joins the `Related:` run."""
    out, changed = _add_related_edge(ARCHIVED_WITH_REVISION, "blocks", "b.md")
    assert changed is True
    assert "\nRelated:\n- required-by: a.md\n- blocks: b.md\n\nRevision:\n" in out
    doc = parse(out, _PATH, _ROOT)
    assert ("blocks", "b.md") in doc.related
    assert doc.extra["Revision"] == (
        "2026-08-11: relate add 'required-by: a.md'; reason: complete the M25 pair",
    )


def test_add_related_edge_preserves_absent_trailing_newline():
    out, _changed = _add_related_edge(WELL_FORMED.rstrip("\n"), "precedes", "next.md")
    assert not out.endswith("\n")
    # The mid-file case above cannot catch the real defect: the insertion
    # point is far from EOF, so the file's tail is never touched. NO_BODY's
    # metadata block runs to EOF, which is where an appended
    # newline-terminated line silently adds a trailing newline.
    out, _changed = _add_related_edge(NO_BODY.rstrip("\n"), "precedes", "next.md")
    assert not out.endswith("\n"), "a metadata block that runs to EOF must not gain a newline"
    assert out.endswith("- precedes: next.md")


def test_remove_related_edge_preserves_absent_trailing_newline():
    """The deleted line can BE the file's unterminated final line."""
    out, changed = _remove_related_edge(NO_BODY.rstrip("\n"), "implements", "charter.md")
    assert changed is True
    assert not out.endswith("\n")
    assert out.endswith("- pairs-with: other.md")


def test_remove_related_edge_dropping_the_group_preserves_absent_trailing_newline():
    """Dropping the emptied label removes the file's last three lines."""
    out, changed = _remove_related_edge(NO_BODY_SINGLE_EDGE.rstrip("\n"), "blocks", "b.md")
    assert changed is True
    assert "Related:" not in out
    assert not out.endswith("\n")
    assert out.endswith("Updated: 2026-05-20")


def test_append_revision_entry_preserves_absent_trailing_newline():
    out = _append_revision_entry(NO_BODY.rstrip("\n"), "2026-08-12: probe")
    assert not out.endswith("\n"), "a metadata block that runs to EOF must not gain a newline"
    assert out.endswith("- 2026-08-12: probe")


def test_add_related_edge_creates_the_group_before_a_trailing_revision():
    """D4: `Revision:` is defined to sit at the END of the metadata block.

    Reachable in a plausible archived sequence: `relate remove` drops the
    last recognized edge (correctly dropping the emptied `Related:` label),
    then `relate add` re-creates the group for a different pair. Appending
    at the end of the block would put `Related:` AFTER `Revision:`.
    """
    out, changed = _add_related_edge(REVISION_NO_RELATED, "blocks", "b.md")
    assert changed is True
    assert out.index("Related:") < out.index("Revision:"), (
        "a re-created Related: group belongs BEFORE the trailing Revision: group"
    )
    doc = parse(out, _PATH, _ROOT)
    assert ("blocks", "b.md") in doc.related
    assert doc.extra["Revision"] == ("2026-08-11: relate remove 'follows: a.md'; reason: wrong",)
    assert doc.lifecycle == "archived"
    assert doc.body.strip().startswith("## Body")


def test_remove_related_edge_removes_only_the_exact_bullet():
    """Same verb + different target, and same target + different verb, survive."""
    text = WELL_FORMED.replace(
        "- implements: charter.md",
        "- implements: charter.md\n- precedes: next.md\n- precedes: other.md\n- follows: next.md",
    )
    out, changed = _remove_related_edge(text, "precedes", "next.md")
    assert changed is True
    assert "- precedes: next.md" not in out
    assert "- precedes: other.md" in out
    assert "- follows: next.md" in out
    assert "- pairs-with: other.md" in out


def test_remove_related_edge_drops_the_emptied_label():
    """Removing the last bullet removes the now-empty `Related:` label too."""
    text = NO_RELATED.replace(
        "Updated: 2026-05-20\n", "Updated: 2026-05-20\n\nRelated:\n- blocks: b.md\n"
    )
    out, changed = _remove_related_edge(text, "blocks", "b.md")
    assert changed is True
    assert "Related:" not in out
    doc = parse(out, _PATH, _ROOT)
    assert doc.related == ()
    assert doc.body.strip().startswith("## Body")


def test_remove_related_edge_is_a_no_op_when_absent():
    out, changed = _remove_related_edge(WELL_FORMED, "precedes", "nowhere.md")
    assert changed is False
    assert out == WELL_FORMED


def test_append_revision_entry_creates_the_group_after_related():
    """D4: `Revision:` is a bare-label group at the END of the metadata block."""
    entry = "2026-08-11: relate add 'follows: a.md'; reason: complete the pair"
    out = _append_revision_entry(WELL_FORMED, entry)
    assert f"\nRevision:\n- {entry}\n" in out
    assert out.index("Related:") < out.index("Revision:")
    assert out.index("Revision:") < out.index("## Body")


def test_append_revision_entry_appends_chronologically_under_one_group():
    entry = "2026-08-12: relate remove 'blocked-by: m30.md'; reason: blocker retired"
    out = _append_revision_entry(ARCHIVED_WITH_REVISION, entry)
    assert out.count("Revision:") == 1, "one group, two bullets — never a second label"
    assert out.index("2026-08-11") < out.index("2026-08-12")


def test_append_revision_entry_round_trips_through_parse():
    entry = "2026-08-12: relate remove 'blocked-by: m30.md'; reason: blocker retired"
    out = _append_revision_entry(ARCHIVED_WITH_REVISION, entry)
    doc = parse(out, _PATH, _ROOT)
    assert doc.extra["Revision"] == (
        "2026-08-11: relate add 'required-by: a.md'; reason: complete the M25 pair",
        entry,
    )
    # Nothing else about the archived doc moved.
    assert doc.lifecycle == "archived"
    assert doc.extra["Archived-reason"] == "completed"
    assert doc.related == (("required-by", "a.md"),)


def test_append_revision_entry_changes_no_other_byte():
    entry = "2026-08-12: relate remove 'blocked-by: m30.md'; reason: blocker retired"
    out = _append_revision_entry(ARCHIVED_WITH_REVISION, entry)
    before = ARCHIVED_WITH_REVISION.splitlines()
    after = out.splitlines()
    assert len(after) == len(before) + 1
    assert [line for line in after if line != f"- {entry}"] == before
