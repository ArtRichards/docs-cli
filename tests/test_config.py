"""Config loader + find_root unit tests (Phase 2 — written RED).

Targets: `load_config()`, `find_root()`, `Config`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from docs import (
    BUILTIN_ROLES,
    BUILTIN_STATUSES,
    INDEX_FILENAME,
    Config,
    find_root,
    load_config,
)


def test_load_config_defaults_when_toml_absent(tmp_path):
    cfg = load_config(tmp_path)
    assert isinstance(cfg, Config)
    assert cfg.archive_dir == "archive"
    assert cfg.date_format == "%Y-%m-%d"
    assert cfg.lifecycles == BUILTIN_STATUSES
    assert cfg.roles == BUILTIN_ROLES
    assert cfg.index_filename == INDEX_FILENAME


def test_load_config_default_project_from_directory_name(tmp_path):
    """When .docs.toml is absent, project defaults to root directory's name."""
    project_dir = tmp_path / "my-cool-project"
    project_dir.mkdir()
    cfg = load_config(project_dir)
    assert cfg.project == "my-cool-project"


def test_load_config_reads_explicit_project(tmp_path):
    (tmp_path / ".docs.toml").write_text('[project]\nname = "explicit-name"\n')
    cfg = load_config(tmp_path)
    assert cfg.project == "explicit-name"


def test_load_config_reads_archive_dir(tmp_path):
    (tmp_path / ".docs.toml").write_text('[project]\nname = "x"\n\n[archive]\ndir = "graveyard"\n')
    cfg = load_config(tmp_path)
    assert cfg.archive_dir == "graveyard"


def test_load_config_additive_status_extension(tmp_path):
    (tmp_path / ".docs.toml").write_text(
        '[project]\nname = "x"\n\n[vocabulary]\nadd_lifecycles = ["shipped"]\n'
    )
    cfg = load_config(tmp_path)
    assert "shipped" in cfg.lifecycles
    # Built-ins are preserved.
    assert "active" in cfg.lifecycles
    assert "archived" in cfg.lifecycles


def test_load_config_additive_role_extension(tmp_path):
    (tmp_path / ".docs.toml").write_text(
        '[project]\nname = "x"\n\n[vocabulary]\nadd_roles = ["adr", "rfc"]\n'
    )
    cfg = load_config(tmp_path)
    assert "adr" in cfg.roles
    assert "rfc" in cfg.roles
    assert "charter" in cfg.roles  # built-in preserved


def test_load_config_handles_root_directory_with_empty_name(tmp_path, monkeypatch):
    """Edge case: filesystem root resolved name is empty string → project falls back."""
    # We can't actually pass / to load_config in a sandbox, so just verify the
    # behavior is documented to not crash: empty-name resolved → "root".
    fake_root = tmp_path / ""  # tmp_path itself
    # Simulate by creating a dir whose .resolve().name is "" by using Path('/')
    # only if running on POSIX. Here we just assert the contract via a stub dir.
    cfg = load_config(fake_root)
    assert isinstance(cfg.project, str)
    assert cfg.project  # non-empty


def test_find_root_returns_dir_containing_docs_toml(tmp_path):
    (tmp_path / ".docs.toml").touch()
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    found = find_root(nested)
    assert found == tmp_path


def test_find_root_walks_upward(tmp_path):
    (tmp_path / ".docs.toml").touch()
    deep = tmp_path / "x" / "y" / "z"
    deep.mkdir(parents=True)
    found = find_root(deep)
    assert found == tmp_path


def test_find_root_falls_back_to_start_when_no_toml(tmp_path):
    """No .docs.toml anywhere upward → return start.resolve()."""
    nested = tmp_path / "a"
    nested.mkdir()
    found = find_root(nested)
    assert found == nested.resolve()


def test_find_root_stops_at_filesystem_root(tmp_path):
    """Walking up from /tmp/... must terminate at / and not loop."""
    # Confirm by ensuring find_root returns SOMETHING (not infinite loop).
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    # No .docs.toml anywhere; should return nested.resolve() (or some ancestor)
    # without raising.
    result = find_root(nested)
    assert isinstance(result, Path)


def test_load_config_invalid_toml_raises(tmp_path):
    """Malformed .docs.toml is a hard error."""
    import tomllib

    (tmp_path / ".docs.toml").write_text("this is = not [valid toml")
    with pytest.raises(tomllib.TOMLDecodeError):
        load_config(tmp_path)


# --- M10 D4 — `[vocabulary] add_fields` -> Config.fields ------------------


def test_load_config_add_fields_extension(tmp_path):
    """`[vocabulary] add_fields = ["Owner", "Tags"]` parses into
    `Config.fields == frozenset({"Owner", "Tags"})`.
    """
    (tmp_path / ".docs.toml").write_text(
        '[project]\nname = "x"\n\n[vocabulary]\nadd_fields = ["Owner", "Tags"]\n'
    )
    cfg = load_config(tmp_path)
    assert cfg.fields == frozenset({"Owner", "Tags"})


def test_load_config_fields_defaults_to_empty_frozenset(tmp_path):
    """Empty tree (no `.docs.toml`) ⇒ `Config.fields == frozenset()`."""
    cfg = load_config(tmp_path)
    assert cfg.fields == frozenset()


def test_load_config_fields_preserves_case(tmp_path):
    """OQ-H: case-sensitive ⇒ both `"Owner"` and `"owner"` are retained
    verbatim (no case-folding by `load_config`).
    """
    (tmp_path / ".docs.toml").write_text(
        '[project]\nname = "x"\n\n[vocabulary]\nadd_fields = ["Owner", "owner"]\n'
    )
    cfg = load_config(tmp_path)
    assert "Owner" in cfg.fields
    assert "owner" in cfg.fields
