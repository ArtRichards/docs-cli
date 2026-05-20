"""CLI end-to-end tests for `docs index` (Phase 2 — written RED).

Invokes the executable as a subprocess. The script is invoked via
`python3 <path-to-script>` so we don't depend on the file being chmod +x
or on `PATH` configuration.
"""

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


def test_help_prints_usage(docs_script):
    proc = _run(docs_script, "index", "--help")
    assert proc.returncode == 0
    assert "index" in proc.stdout.lower()


def test_index_minimal_tree_exits_zero(docs_script, fixtures_dir):
    root = fixtures_dir / "trees" / "minimal"
    proc = _run(docs_script, "index", "--root", str(root))
    assert proc.returncode == 0, proc.stderr


def test_index_writes_INDEX_md(docs_script, fixtures_dir, tmp_path):
    """Run against a copy of the minimal fixture; verify INDEX.md is (re)written."""
    src = fixtures_dir / "trees" / "minimal"
    dst = tmp_path / "tree"
    shutil.copytree(src, dst)
    proc = _run(docs_script, "index", "--root", str(dst))
    assert proc.returncode == 0, proc.stderr
    assert (dst / "INDEX.md").exists()


def test_index_dry_run_no_write(docs_script, fixtures_dir, tmp_path):
    """`--dry-run` reports what would change but doesn't touch INDEX.md."""
    src = fixtures_dir / "trees" / "minimal"
    dst = tmp_path / "tree"
    shutil.copytree(src, dst)
    before = (dst / "INDEX.md").read_text() if (dst / "INDEX.md").exists() else None
    proc = _run(docs_script, "index", "--root", str(dst), "--dry-run")
    assert proc.returncode == 0, proc.stderr
    after = (dst / "INDEX.md").read_text() if (dst / "INDEX.md").exists() else None
    assert before == after


def test_index_nonexistent_root_exits_nonzero(docs_script, tmp_path):
    bogus = tmp_path / "does-not-exist"
    proc = _run(docs_script, "index", "--root", str(bogus))
    assert proc.returncode != 0
    assert proc.stderr  # some error message on stderr


def test_index_marker_preservation_fixture(docs_script, fixtures_dir, tmp_path):
    """Running index against the marker-preservation tree keeps the hand-edited preamble."""
    src = fixtures_dir / "trees" / "marker-preservation"
    dst = tmp_path / "tree"
    shutil.copytree(src, dst)
    original = (dst / "INDEX.md").read_text()
    # Identify the preamble: everything before the start marker.
    pre = original.split("<!-- docs:generated start -->", 1)[0]
    proc = _run(docs_script, "index", "--root", str(dst))
    assert proc.returncode == 0, proc.stderr
    after = (dst / "INDEX.md").read_text()
    assert after.startswith(pre)


def test_index_output_matches_frozen_snapshot(docs_script, fixtures_dir, tmp_path):
    """Acceptance test: `docs index` on this repo's docs/ produces the frozen snapshot.

    This is the dogfood guard — without it, Phase 9's acceptance is circular
    (asserting the live docs/INDEX.md against itself after regeneration).
    """
    # Copy the real docs/ tree into a tmp dir so we can run index there without
    # mutating the source repo.
    repo_docs = Path(__file__).resolve().parent.parent / "docs"
    dst = tmp_path / "docs"
    shutil.copytree(repo_docs, dst)
    proc = _run(docs_script, "index", "--root", str(dst))
    assert proc.returncode == 0, proc.stderr
    generated = (dst / "INDEX.md").read_text()
    expected = (fixtures_dir / "expected" / "docs-INDEX.md").read_text()
    assert generated == expected
