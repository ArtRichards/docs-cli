"""CLI end-to-end tests for `docs archive` (Phase 2 — written RED)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


def _run(
    script: Path,
    *args: str,
    cwd: Path | None = None,
    stdin_text: str | None = None,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        input=stdin_text,
    )


def _minimal_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "minimal", root)
    return root


def _crossrefs_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    """Copy the cross-refs fixture (helper.md `pairs-with` core.md) into tmp_path."""
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "cross-refs", root)
    return root


def test_archive_help(docs_script):
    proc = _run(docs_script, "archive", "--help")
    assert proc.returncode == 0
    assert "archive" in proc.stdout.lower()


def test_archive_moves_file_to_dated_directory(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "archive", str(root / "lone-doc.md"))
    assert proc.returncode == 0, proc.stderr
    moved = root / "archive" / date.today().isoformat() / "lone-doc.md"
    assert moved.is_file()


def test_archive_removes_the_original(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "archive", str(root / "lone-doc.md"))
    assert proc.returncode == 0, proc.stderr
    assert not (root / "lone-doc.md").exists()


def test_archive_sets_status_archived(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "archive", str(root / "lone-doc.md"))
    assert proc.returncode == 0, proc.stderr
    moved = root / "archive" / date.today().isoformat() / "lone-doc.md"
    text = moved.read_text()
    assert "Lifecycle: archived" in text
    assert "Lifecycle: active" not in text


def test_archive_bumps_updated(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "archive", str(root / "lone-doc.md"))
    assert proc.returncode == 0, proc.stderr
    moved = root / "archive" / date.today().isoformat() / "lone-doc.md"
    assert f"Updated: {date.today().isoformat()}" in moved.read_text()


def test_archive_reason_flag_appends_metadata_line(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "archive",
        str(root / "lone-doc.md"),
        "--reason",
        "superseded by the v2 design",
    )
    assert proc.returncode == 0, proc.stderr
    moved = root / "archive" / date.today().isoformat() / "lone-doc.md"
    assert "Archived-reason: superseded by the v2 design" in moved.read_text()


def test_archive_date_flag_controls_the_directory(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "archive", str(root / "lone-doc.md"), "--date", "2026-01-15")
    assert proc.returncode == 0, proc.stderr
    assert (root / "archive" / "2026-01-15" / "lone-doc.md").is_file()


def test_archive_regenerates_index(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "archive", str(root / "lone-doc.md"))
    assert proc.returncode == 0, proc.stderr
    assert (root / "INDEX.md").is_file()


def test_archive_dry_run_does_not_move(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "archive", str(root / "lone-doc.md"), "--dry-run")
    assert proc.returncode == 0, proc.stderr
    assert (root / "lone-doc.md").is_file()
    assert not (root / "archive").exists()


def test_archive_missing_file_exits_nonzero(docs_script, tmp_path):
    proc = _run(docs_script, "archive", str(tmp_path / "no-such-doc.md"))
    assert proc.returncode != 0
    assert "not found" in proc.stderr.lower()


def test_archive_cascade_yes_also_archives_related(docs_script, fixtures_dir, tmp_path):
    """`--cascade` + a `y` answer archives a pairs-with relation to the same dir."""
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    # helper.md carries `- pairs-with: core.md`.
    proc = _run(docs_script, "archive", str(root / "helper.md"), "--cascade", stdin_text="y\n")
    assert proc.returncode == 0, proc.stderr
    dated = root / "archive" / date.today().isoformat()
    assert (dated / "helper.md").is_file()
    assert (dated / "core.md").is_file()
    assert not (root / "core.md").exists()


def test_archive_cascade_no_leaves_related_in_place(docs_script, fixtures_dir, tmp_path):
    """`--cascade` + an `n` answer leaves the related doc untouched."""
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "archive", str(root / "helper.md"), "--cascade", stdin_text="n\n")
    assert proc.returncode == 0, proc.stderr
    dated = root / "archive" / date.today().isoformat()
    assert (dated / "helper.md").is_file()
    assert not (dated / "core.md").exists()
    assert (root / "core.md").is_file()
