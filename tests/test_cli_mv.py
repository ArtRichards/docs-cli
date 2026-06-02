"""CLI end-to-end tests for `docs mv` (Phase 2 — written RED)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


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


# --- M14 A1 — mv is all-or-nothing (validate-all-first pre-flight) ----------


def _mv_malformed_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    """Copy the mv-with-malformed fixture tree into tmp_path; return its root.

    The tree carries `good-a.md` (the mv source), `referrer.md`
    (`pairs-with: good-a.md`), and `broken.md` (no H1 → `walk()` raises
    `MetadataError`). `docs mv good-a.md good-b.md` must abort BEFORE the
    move because the post-move rewrite walk would raise on `broken.md`.
    """
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "mv-with-malformed", root)
    return root


def test_mv_malformed_sibling_aborts_atomically(docs_script, fixtures_dir, tmp_path):
    """A malformed sibling must abort `docs mv` with exit 2, leaving the
    source in place, the destination absent, and the referrer byte-identical.

    RED reason: `_cmd_mv` does `old_path.replace(new_path)` (cli.py:3558)
    BEFORE the rewrite walk (cli.py:3560) that raises on `broken.md`. So
    today the source is already moved when the walk fails — the move is
    NOT all-or-nothing. Step 2 ports the archive validate-all-first
    pre-flight walk ahead of the move.
    """
    root = _mv_malformed_tree(fixtures_dir, tmp_path)
    source = root / "good-a.md"
    dest = root / "good-b.md"
    referrer = root / "referrer.md"
    source_before = source.read_text()
    referrer_before = referrer.read_text()

    proc = _run(docs_script, "mv", str(source), str(dest))

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    # The source is still at its old path, byte-identical.
    assert source.is_file(), "mv must not move the source when a sibling is malformed"
    assert source.read_text() == source_before
    # The destination was never created.
    assert not dest.exists(), "mv must not create the destination on an aborted move"
    # The referrer's Related: edge is untouched.
    assert referrer.read_text() == referrer_before
    assert "pairs-with: good-a.md" in referrer.read_text()


def test_mv_malformed_sibling_leaves_index_untouched(docs_script, fixtures_dir, tmp_path):
    """A pre-built INDEX must be byte-identical after an aborted `docs mv`.

    RED reason: same as above — the move happens first, so even though the
    rewrite walk raises, the partial state is observable. With the
    pre-flight walk (Step 2) the abort happens before any disk write and
    the INDEX never changes.
    """
    root = _mv_malformed_tree(fixtures_dir, tmp_path)
    # Pre-build the INDEX so we can pin byte-identity across the aborted mv.
    pre = _run(docs_script, "index", "--root", str(root))
    assert pre.returncode == 0, pre.stderr
    index = root / "INDEX.md"
    assert index.is_file()
    index_before = index.read_bytes()

    proc = _run(docs_script, "mv", str(root / "good-a.md"), str(root / "good-b.md"))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert index.read_bytes() == index_before, (
        "an aborted mv (malformed sibling) must not refresh INDEX"
    )


# --- M14 A4 — uncaught OSError mid-rewrite → clean exit 2 -------------------


def _readonly_referrer_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Build a docs root where the referrer lives in a read-only subdir.

    Returns (root, source, locked_dir). `source.md` (at root) is the mv
    target; `locked/referrer.md` carries `pairs-with: source.md`, so the
    rewrite walk tries to `atomic_write` it — which raises `OSError`
    (PermissionError) when the `.docs-tmp` tmpfile cannot be created in
    the `0o555` `locked/` directory. (A bare `chmod 0o444` on the file is
    NOT a reliable trigger: POSIX `rename()` onto a read-only target
    succeeds when the directory is writable; a read-only *directory* is
    the portable trigger.) The contract under test is observable: exit 2
    + no Traceback. Phase 6 may adjust the trigger for portability.
    """
    root = tmp_path / "ro"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "ro"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: ro\n"
    source = root / "source.md"
    source.write_text(f"# Source\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\nThe mv source.\n")
    locked = root / "locked"
    locked.mkdir()
    (locked / "referrer.md").write_text(
        f"# Referrer\n\n{hdr}Updated: 2026-01-02\n\n"
        "Related:\n- pairs-with: source.md\n\n## Body\n\nReferences the source.\n"
    )
    # Read-only directory: walk can still read referrer.md, but the
    # atomic_write tmpfile creation during the rewrite raises OSError.
    os.chmod(locked, 0o555)
    return root, source, locked


@pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="root bypasses 0o555 directory write protection; the OSError trigger does not fire",
)
def test_mv_oserror_mid_rewrite_exits_2(docs_script, tmp_path):
    """An OSError raised mid-rewrite must surface as a clean exit 2 with no
    Traceback on stderr (the observable contract; RQ#9).

    RED reason: the `_cmd_mv` rewrite loop (cli.py:3560-3567) catches only
    `(MetadataError, VocabularyError)`; an `OSError` from `atomic_write`
    against a referrer in a read-only directory escapes as an uncaught
    traceback after the move. Step 2 widens the except to map `OSError`
    → exit 2.
    """
    root, source, locked = _readonly_referrer_tree(tmp_path)
    try:
        proc = _run(docs_script, "mv", str(source), str(root / "renamed.md"))
        assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
        assert "Traceback" not in proc.stderr, (
            "an OSError mid-rewrite must be mapped to a clean exit 2, not a "
            f"traceback:\n{proc.stderr}"
        )
    finally:
        os.chmod(locked, 0o755)  # restore so tmp_path teardown can clean up


# --- M14 A6 — mv end-of-batch reindex honours [exclude] --------------------


def _mv_excluded_malformed_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Build a docs root with an `[exclude] dirs = ["vendor"]` and a
    malformed `vendor/README.md`, plus two conformant docs to mv between.

    Returns (root, source, dest_path). The malformed vendor file must NOT
    fail the post-move reindex because it is excluded.
    """
    root = tmp_path / "mv-excl"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "mv-excl"\n\n[archive]\ndir = "archive"\n\n'
        '[exclude]\ndirs = ["vendor"]\n'
    )
    hdr = "Lifecycle: active\nRole: notes\nProject: mv-excl\n"
    source = root / "source.md"
    source.write_text(f"# Source\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\nThe mv source.\n")
    (root / "other.md").write_text(
        f"# Other\n\n{hdr}Updated: 2026-01-02\n\n## Body\n\nA second conformant doc.\n"
    )
    vendor = root / "vendor"
    vendor.mkdir()
    # Malformed: no H1, then an H1 — parse() raises MetadataError on it.
    (vendor / "README.md").write_text("no metadata\n# H1\n")
    return root, source, root / "dest.md"


def test_mv_excluded_malformed_file_reindexes(docs_script, tmp_path):
    """`docs mv` over a tree whose `[exclude]` set holds a malformed file
    must succeed (exit 0): the end-of-batch reindex skips the excluded
    file, the move lands, and the malformed file is byte-unchanged.

    RED reason: `_cmd_mv` calls `_refresh_index(root, config)` with NO
    predicate (cli.py:3567), so the post-move walk reads the excluded
    malformed `vendor/README.md` and raises → exit 2. Step 2 threads
    `compile_exclude_predicate(config, [])` into the reindex.
    """
    root, source, dest = _mv_excluded_malformed_tree(tmp_path)
    vendor_readme = root / "vendor" / "README.md"
    vendor_before = vendor_readme.read_text()

    proc = _run(docs_script, "mv", str(source), str(dest))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The move landed.
    assert dest.is_file()
    assert not source.exists()
    # The excluded malformed file is byte-unchanged and not in the INDEX.
    assert vendor_readme.read_text() == vendor_before
    index = (root / "INDEX.md").read_text()
    assert "vendor/README.md" not in index, "the excluded file must not appear in INDEX"
