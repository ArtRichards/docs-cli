"""Walker unit tests (Phase 2 — written RED).

Targets: `walk()`. Uses fixture trees under tests/fixtures/trees/.
"""

from __future__ import annotations

from docs import BUILTIN_ROLES, BUILTIN_STATUSES, Config, walk


def _default_config(project: str = "test") -> Config:
    return Config(
        project=project,
        archive_dir="archive",
        date_format="%Y-%m-%d",
        lifecycles=BUILTIN_STATUSES,
        roles=BUILTIN_ROLES,
    )


def test_walk_minimal_tree_yields_one_doc(fixtures_dir):
    root = fixtures_dir / "trees" / "minimal"
    docs = list(walk(root, _default_config()))
    assert len(docs) == 1
    assert docs[0].title  # non-empty


def test_walk_excludes_root_level_INDEX(fixtures_dir):
    """The root-level INDEX.md is a generated view; walker skips it."""
    root = fixtures_dir / "trees" / "marker-preservation"
    docs = list(walk(root, _default_config()))
    paths = [d.path.name for d in docs]
    assert "INDEX.md" not in paths
    # But other docs ARE walked.
    assert len(docs) >= 1


def test_walk_includes_nested_INDEX(fixtures_dir):
    """A nested INDEX.md (deeper than root) IS a regular doc and IS walked."""
    root = fixtures_dir / "trees" / "with-archive"
    docs = list(walk(root, _default_config()))
    nested_names = [d.path.relative_to(root).as_posix() for d in docs]
    # The fixture must include a nested INDEX.md somewhere (Phase 3 builds it).
    assert any("INDEX.md" in n for n in nested_names if n != "INDEX.md")


def test_walk_excludes_non_markdown(fixtures_dir):
    root = fixtures_dir / "trees" / "with-archive"
    docs = list(walk(root, _default_config()))
    for d in docs:
        assert d.path.suffix == ".md"


def test_walk_excludes_dotfiles(fixtures_dir):
    """`.docs.toml` and other dotfiles/dotdirs are not yielded."""
    root = fixtures_dir / "trees" / "with-archive"
    docs = list(walk(root, _default_config()))
    for d in docs:
        for part in d.path.relative_to(root).parts:
            assert not part.startswith(".")


def test_walk_deterministic_order(fixtures_dir):
    """Two walks produce the same sequence of paths."""
    root = fixtures_dir / "trees" / "with-archive"
    first = [d.path for d in walk(root, _default_config())]
    second = [d.path for d in walk(root, _default_config())]
    assert first == second


def test_walk_sort_order_is_path_ascending(fixtures_dir):
    """Yielded docs are sorted by root-relative POSIX path, lexicographic."""
    root = fixtures_dir / "trees" / "with-archive"
    docs = list(walk(root, _default_config()))
    rel_paths = [d.path.relative_to(root).as_posix() for d in docs]
    assert rel_paths == sorted(rel_paths)


def test_walk_archived_flag_set_for_archive_subtree(fixtures_dir):
    """Docs under archive_dir have archived=True; others have archived=False."""
    root = fixtures_dir / "trees" / "with-archive"
    docs = list(walk(root, _default_config()))
    for d in docs:
        rel = d.path.relative_to(root).as_posix()
        if rel.startswith("archive/"):
            assert d.archived is True, f"{rel} should be archived"
        else:
            assert d.archived is False, f"{rel} should not be archived"


def test_walk_yields_active_and_archived_in_with_archive_fixture(fixtures_dir):
    """The with-archive fixture intentionally contains both groups."""
    root = fixtures_dir / "trees" / "with-archive"
    docs = list(walk(root, _default_config()))
    active = [d for d in docs if not d.archived]
    archived = [d for d in docs if d.archived]
    assert len(active) >= 1
    assert len(archived) >= 1
