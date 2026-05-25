"""Index renderer unit tests (Phase 2 — written RED).

Targets: `render_index()`. Constructs `Doc` instances directly rather than
parsing — these tests exercise the renderer in isolation.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from docs import (
    BUILTIN_ROLES,
    BUILTIN_STATUSES,
    MARKER_END,
    MARKER_START,
    Config,
    Doc,
    render_index,
)

# The docs root these synthetic Docs hang off of — `_doc` builds
# `/fake/<name>` paths, so root-relative POSIX paths equal the basenames.
_ROOT = Path("/fake")


def _config() -> Config:
    return Config(
        project="test",
        archive_dir="archive",
        date_format="%Y-%m-%d",
        lifecycles=BUILTIN_STATUSES,
        roles=BUILTIN_ROLES,
    )


def _doc(
    name: str,
    role: str = "spec",
    lifecycle: str = "active",
    updated: date = date(2026, 5, 20),
    body: str = "Body paragraph one.\n\nBody paragraph two.",
    archived: bool = False,
    project: str | None = "test",
) -> Doc:
    return Doc(
        path=Path(f"/fake/{name}"),
        title=name.replace(".md", "").replace("-", " ").title(),
        lifecycle=lifecycle,
        role=role,
        project=project,
        updated=updated,
        related=(),
        extra={},
        body=body,
        archived=archived,
    )


def test_render_creates_minimal_index_when_existing_is_none():
    """No prior INDEX → output contains only the marker block."""
    out = render_index([_doc("a.md")], _config(), existing=None, root=_ROOT)
    assert MARKER_START in out
    assert MARKER_END in out
    # Nothing before the start marker (or only whitespace).
    pre = out.split(MARKER_START, 1)[0]
    assert pre.strip() == ""


def test_render_preserves_preamble_and_trailer():
    """Content outside the markers is preserved verbatim."""
    preamble = "# My docs\n\nHand-written preamble paragraph.\n\n"
    trailer = "\n\nHand-written trailer paragraph.\n"
    existing = f"{preamble}{MARKER_START}\nOLD CONTENT\n{MARKER_END}{trailer}"
    out = render_index([_doc("a.md")], _config(), existing=existing, root=_ROOT)
    assert out.startswith(preamble)
    assert out.endswith(trailer)
    assert "OLD CONTENT" not in out


def test_render_ignores_marker_mentions_inside_prose():
    """A preamble that mentions the marker text in prose must not false-match.

    The dogfood `docs/INDEX.md` documents the marker convention by quoting
    `<!-- docs:generated start -->` inside backticks. A naive substring split
    on the marker would treat that mention as the real marker and corrupt the
    output. Markers are recognized only when they appear as standalone lines.
    """
    preamble = (
        f"# Docs\n\nOnly content between `{MARKER_START}` and `{MARKER_END}` is rewritten.\n\n"
    )
    trailer = "\n\nTrailer paragraph.\n"
    existing = f"{preamble}{MARKER_START}\nOLD CONTENT\n{MARKER_END}{trailer}"
    out = render_index([_doc("a.md")], _config(), existing=existing, root=_ROOT)
    # The preamble (including its backtick-quoted marker mentions) must survive.
    assert out.startswith(preamble)
    # The trailer (after the real end marker) must survive.
    assert out.endswith(trailer)
    # The previous derived content must be gone.
    assert "OLD CONTENT" not in out
    # The real marker block appears exactly once (the prose mentions are in
    # backticks, the real marker is on its own line).
    assert out.count(f"\n{MARKER_START}\n") == 1
    assert out.count(f"\n{MARKER_END}") == 1


def test_render_is_idempotent():
    docs = [
        _doc("alpha.md", role="spec"),
        _doc("beta.md", role="charter"),
    ]
    first = render_index(docs, _config(), existing=None, root=_ROOT)
    second = render_index(docs, _config(), existing=first, root=_ROOT)
    assert first == second


def test_render_includes_summary_line():
    out = render_index([_doc("a.md")], _config(), existing=None, root=_ROOT)
    assert "_Generated " in out
    assert "1 docs active, 0 archived" in out


def test_render_summary_counts_active_and_archived():
    docs = [
        _doc("a.md"),
        _doc("b.md"),
        _doc("old.md", lifecycle="archived", archived=True),
    ]
    out = render_index(docs, _config(), existing=None, root=_ROOT)
    assert "2 docs active, 1 archived" in out


def test_render_status_role_pinned_to_top():
    """A status-role doc appears before charter, plan, etc."""
    docs = [
        _doc("plan.md", role="plan"),
        _doc("charter.md", role="charter"),
        _doc("status.md", role="status"),
    ]
    out = render_index(docs, _config(), existing=None, root=_ROOT)
    body = out.split(MARKER_START, 1)[1].split(MARKER_END, 1)[0]
    status_pos = body.find("### Active — Status")
    charter_pos = body.find("### Active — Charter")
    plan_pos = body.find("### Active — Plan")
    assert 0 <= status_pos < charter_pos < plan_pos


def test_render_role_order_after_status_is_canonical():
    """Charter precedes Plan precedes Spec, etc., per CANONICAL_ROLE_ORDER."""
    docs = [
        _doc("c.md", role="charter"),
        _doc("p.md", role="plan"),
        _doc("s.md", role="spec"),
        _doc("m.md", role="milestone"),
    ]
    out = render_index(docs, _config(), existing=None, root=_ROOT)
    body = out.split(MARKER_START, 1)[1].split(MARKER_END, 1)[0]
    positions = [
        body.find("### Active — Charter"),
        body.find("### Active — Plan"),
        body.find("### Active — Spec"),
        body.find("### Active — Milestone"),
    ]
    assert positions == sorted(positions)
    assert all(p >= 0 for p in positions)


def test_render_empty_role_sections_omitted():
    """Roles with zero docs do not produce empty headings."""
    docs = [_doc("a.md", role="charter")]
    out = render_index(docs, _config(), existing=None, root=_ROOT)
    body = out.split(MARKER_START, 1)[1].split(MARKER_END, 1)[0]
    # Only Charter section should appear.
    assert "### Active — Charter" in body
    assert "### Active — Plan" not in body
    assert "### Active — Spec" not in body


def test_render_within_section_sorts_by_updated_desc_then_path_asc():
    """Newer first; same date → path ascending."""
    docs = [
        _doc("zzz.md", role="spec", updated=date(2026, 5, 20)),
        _doc("aaa.md", role="spec", updated=date(2026, 5, 20)),
        _doc("mid.md", role="spec", updated=date(2026, 5, 21)),
    ]
    out = render_index(docs, _config(), existing=None, root=_ROOT)
    body = out.split(MARKER_START, 1)[1].split(MARKER_END, 1)[0]
    # Section contains entries in order: mid (newer), aaa, zzz (alpha tiebreaker).
    assert "### Active — Spec" in body
    spec_section = body.split("### Active — Spec", 1)[1]
    mid_pos = spec_section.find("mid.md")
    aaa_pos = spec_section.find("aaa.md")
    zzz_pos = spec_section.find("zzz.md")
    assert 0 <= mid_pos < aaa_pos < zzz_pos


def test_render_archived_section_appears_last_with_archived_heading():
    docs = [
        _doc("a.md"),
        _doc("old.md", lifecycle="archived", archived=True),
    ]
    out = render_index(docs, _config(), existing=None, root=_ROOT)
    body = out.split(MARKER_START, 1)[1].split(MARKER_END, 1)[0]
    archived_pos = body.find("## Archived")
    active_spec_pos = body.find("### Active — Spec")
    assert active_spec_pos >= 0
    assert archived_pos > active_spec_pos


def test_render_entry_format():
    """Each entry is `- [name](name) — _role_ — <desc>. Updated YYYY-MM-DD.`."""
    docs = [_doc("alpha.md", role="spec", body="The first paragraph is the description.")]
    out = render_index(docs, _config(), existing=None, root=_ROOT)
    assert "- [alpha.md](alpha.md) — _spec_" in out
    assert "The first paragraph is the description." in out
    assert "Updated 2026-05-20" in out


def test_render_description_uses_first_paragraph_skipping_headers():
    """Headers (`## …`) and blank lines are skipped when finding the first paragraph."""
    body = "## Some section\n\nFirst real paragraph here."
    docs = [_doc("a.md", role="spec", body=body)]
    out = render_index(docs, _config(), existing=None, root=_ROOT)
    assert "First real paragraph here." in out


def test_render_long_description_truncated():
    """Descriptions longer than ~120 chars are truncated with an ellipsis."""
    long_para = "word " * 80  # ~400 chars
    docs = [_doc("a.md", role="spec", body=long_para.strip())]
    out = render_index(docs, _config(), existing=None, root=_ROOT)
    # The full 400-char paragraph should not appear verbatim.
    assert long_para.strip() not in out
    # An ellipsis character or "..." should appear somewhere in the entry line.
    assert "…" in out or "..." in out


# --- M3: two-level Project → Role grouping --------------------------------


def test_render_groups_active_docs_by_project():
    """Active docs are grouped under `## Project — <name>` sections."""
    docs = [
        _doc("a.md", role="spec", project="test"),
        _doc("b.md", role="spec", project="alpha"),
    ]
    out = render_index(docs, _config(), existing=None, root=_ROOT)
    body = out.split(MARKER_START, 1)[1].split(MARKER_END, 1)[0]
    assert "## Project — test" in body
    assert "## Project — alpha" in body


def test_render_home_project_first_then_alphabetical():
    """The docs-root project leads; remaining projects follow alphabetically."""
    docs = [
        _doc("z.md", role="spec", project="zebra"),
        _doc("a.md", role="spec", project="alpha"),
        _doc("t.md", role="spec", project="test"),
    ]
    out = render_index(docs, _config(), existing=None, root=_ROOT)
    body = out.split(MARKER_START, 1)[1].split(MARKER_END, 1)[0]
    test_pos = body.find("## Project — test")
    alpha_pos = body.find("## Project — alpha")
    zebra_pos = body.find("## Project — zebra")
    assert 0 <= test_pos < alpha_pos < zebra_pos


def test_render_project_less_doc_falls_back_to_config_project():
    """A Doc with project=None is bucketed under the config's project."""
    docs = [_doc("orphan.md", role="spec", project=None)]
    out = render_index(docs, _config(), existing=None, root=_ROOT)
    body = out.split(MARKER_START, 1)[1].split(MARKER_END, 1)[0]
    assert "## Project — test" in body
    assert "orphan.md" in body
