"""CLI end-to-end tests for `docs new` (Phase 2 — written RED).

Invokes the executable as a subprocess, per the M1 convention.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


def _run(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


def _minimal_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    """Copy the minimal fixture tree into tmp_path; return its root."""
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "minimal", root)
    return root


def test_new_help_lists_role_and_slug(docs_script):
    proc = _run(docs_script, "new", "--help")
    assert proc.returncode == 0
    assert "role" in proc.stdout.lower()
    assert "slug" in proc.stdout.lower()


def test_new_creates_the_file(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "my-feature", "--root", str(root))
    assert proc.returncode == 0, proc.stderr
    assert (root / "my-feature.md").is_file()


def test_new_scaffolds_metadata_block(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "my-feature", "--root", str(root))
    assert proc.returncode == 0, proc.stderr
    text = (root / "my-feature.md").read_text()
    assert "Status: draft" in text
    assert "Role: spec" in text
    assert f"Updated: {date.today().isoformat()}" in text


def test_new_title_defaults_to_titlecased_slug(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "my-feature", "--root", str(root))
    assert proc.returncode == 0, proc.stderr
    assert (root / "my-feature.md").read_text().startswith("# My Feature\n")


def test_new_title_override(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "new",
        "spec",
        "my-feature",
        "--title",
        "A Custom Title",
        "--root",
        str(root),
    )
    assert proc.returncode == 0, proc.stderr
    assert (root / "my-feature.md").read_text().startswith("# A Custom Title\n")


def test_new_project_flag_sets_project(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "new",
        "spec",
        "my-feature",
        "--project",
        "otherproj",
        "--root",
        str(root),
    )
    assert proc.returncode == 0, proc.stderr
    assert "Project: otherproj" in (root / "my-feature.md").read_text()


def test_new_invalid_role_exits_2(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "bogusrole", "my-feature", "--root", str(root))
    assert proc.returncode == 2
    assert "role" in proc.stderr.lower()


def test_new_existing_file_exits_1(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    # lone-doc.md already exists in the minimal tree.
    proc = _run(docs_script, "new", "spec", "lone-doc", "--root", str(root))
    assert proc.returncode == 1
    assert "exist" in proc.stderr.lower()


def test_new_does_not_refresh_index(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    index = root / "INDEX.md"
    before = index.read_text() if index.exists() else None
    proc = _run(docs_script, "new", "spec", "my-feature", "--root", str(root))
    assert proc.returncode == 0, proc.stderr
    after = index.read_text() if index.exists() else None
    assert before == after


def test_new_dry_run_creates_nothing(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "my-feature", "--root", str(root), "--dry-run")
    assert proc.returncode == 0, proc.stderr
    assert not (root / "my-feature.md").exists()


def test_new_dry_run_invalid_role_still_exits_2(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "bogusrole", "my-feature", "--root", str(root), "--dry-run")
    assert proc.returncode == 2


def test_new_nested_slug_creates_subdirectory(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "topics/deep", "--root", str(root))
    assert proc.returncode == 0, proc.stderr
    assert (root / "topics" / "deep.md").is_file()


def test_new_slug_escaping_root_is_rejected(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "../escape", "--root", str(root))
    assert proc.returncode == 2
    assert not (tmp_path / "escape.md").exists()
