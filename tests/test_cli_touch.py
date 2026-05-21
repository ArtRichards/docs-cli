"""CLI end-to-end tests for `docs touch` (Phase 2 — written RED)."""

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
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "minimal", root)
    return root


def test_touch_help(docs_script):
    proc = _run(docs_script, "touch", "--help")
    assert proc.returncode == 0
    assert "updated" in proc.stdout.lower()


def test_touch_bumps_updated_to_today(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    doc = root / "lone-doc.md"
    proc = _run(docs_script, "touch", str(doc))
    assert proc.returncode == 0, proc.stderr
    assert f"Updated: {date.today().isoformat()}" in doc.read_text()


def test_touch_preserves_body_and_other_metadata(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    doc = root / "lone-doc.md"
    before = doc.read_text()
    proc = _run(docs_script, "touch", str(doc))
    assert proc.returncode == 0, proc.stderr
    after = doc.read_text()
    # Everything except the Updated: line is byte-identical.
    before_lines = [ln for ln in before.splitlines() if not ln.startswith("Updated:")]
    after_lines = [ln for ln in after.splitlines() if not ln.startswith("Updated:")]
    assert before_lines == after_lines


def test_touch_regenerates_index(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "touch", str(root / "lone-doc.md"))
    assert proc.returncode == 0, proc.stderr
    assert (root / "INDEX.md").is_file()


def test_touch_is_idempotent(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    doc = root / "lone-doc.md"
    first = _run(docs_script, "touch", str(doc))
    assert first.returncode == 0, first.stderr
    after_first = doc.read_text()
    second = _run(docs_script, "touch", str(doc))
    assert second.returncode == 0, second.stderr
    assert doc.read_text() == after_first


def test_touch_missing_file_exits_1(docs_script, tmp_path):
    proc = _run(docs_script, "touch", str(tmp_path / "no-such-doc.md"))
    assert proc.returncode == 1
    assert "not found" in proc.stderr.lower()


def test_touch_dry_run_makes_no_change(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    doc = root / "lone-doc.md"
    before = doc.read_text()
    proc = _run(docs_script, "touch", str(doc), "--dry-run")
    assert proc.returncode == 0, proc.stderr
    assert doc.read_text() == before
