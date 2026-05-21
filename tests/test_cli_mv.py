"""CLI end-to-end tests for `docs mv` (Phase 2 — written RED)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _run(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


def _crossrefs_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    """Copy the cross-refs fixture tree into tmp_path; return its root."""
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "cross-refs", root)
    return root


def test_mv_help(docs_script):
    proc = _run(docs_script, "mv", "--help")
    assert proc.returncode == 0
    assert "old" in proc.stdout.lower()
    assert "new" in proc.stdout.lower()


def test_mv_renames_in_place(docs_script, fixtures_dir, tmp_path):
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "mv", str(root / "core.md"), str(root / "core-engine.md"))
    assert proc.returncode == 0, proc.stderr
    assert (root / "core-engine.md").is_file()
    assert not (root / "core.md").exists()


def test_mv_into_a_subdirectory(docs_script, fixtures_dir, tmp_path):
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "mv", str(root / "core.md"), str(root / "sub" / "core.md"))
    assert proc.returncode == 0, proc.stderr
    assert (root / "sub" / "core.md").is_file()
    assert not (root / "core.md").exists()


def test_mv_rewrites_related_refs_across_the_tree(docs_script, fixtures_dir, tmp_path):
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "mv", str(root / "core.md"), str(root / "core-engine.md"))
    assert proc.returncode == 0, proc.stderr
    helper = (root / "helper.md").read_text()
    overview = (root / "overview.md").read_text()
    assert "pairs-with: core-engine.md" in helper
    assert "references: core-engine.md" in overview
    assert "pairs-with: core.md" not in helper
    assert "references: core.md" not in overview


def test_mv_collision_exits_1(docs_script, fixtures_dir, tmp_path):
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "mv", str(root / "core.md"), str(root / "helper.md"))
    assert proc.returncode == 1
    assert "exist" in proc.stderr.lower()


def test_mv_regenerates_index(docs_script, fixtures_dir, tmp_path):
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "mv", str(root / "core.md"), str(root / "core-engine.md"))
    assert proc.returncode == 0, proc.stderr
    assert (root / "INDEX.md").is_file()


def test_mv_dry_run_makes_no_change(docs_script, fixtures_dir, tmp_path):
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "mv", str(root / "core.md"), str(root / "core-engine.md"), "--dry-run")
    assert proc.returncode == 0, proc.stderr
    assert (root / "core.md").is_file()
    assert not (root / "core-engine.md").exists()
    assert "pairs-with: core.md" in (root / "helper.md").read_text()
