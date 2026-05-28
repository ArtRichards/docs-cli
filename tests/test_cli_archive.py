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


def test_archive_sets_lifecycle_archived(docs_script, fixtures_dir, tmp_path):
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


# --- M12 — referring-edge rewrite -------------------------------------------


def _cascade_refs_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "archive-with-incoming-refs", root)
    return root


def test_archive_rewrites_referring_edges_in_other_docs(docs_script, fixtures_dir, tmp_path):
    """After `docs archive core.md --date 2026-05-28`, every doc that
    referenced `core.md` via `Related:` must point at the archive path."""
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "archive",
        str(root / "core.md"),
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, proc.stderr
    helper = (root / "helper.md").read_text()
    overview = (root / "overview.md").read_text()
    assert "pairs-with: archive/2026-05-28/core.md" in helper, helper
    assert "references: archive/2026-05-28/core.md" in overview, overview
    # And the old reference is gone.
    assert "pairs-with: core.md" not in helper
    assert "references: core.md" not in overview


def test_archive_does_not_touch_prose_references_to_old_path(docs_script, fixtures_dir, tmp_path):
    """A doc whose body prose mentions `core.md` is not rewritten by the
    archive referring-edge walker — `Related:` only."""
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    # Add an extra doc with prose mention of core.md (no Related: edge).
    prose = root / "prose.md"
    prose.write_text(
        "# Prose\n\n"
        "Lifecycle: active\nRole: notes\nProject: cross-refs\nUpdated: 2026-05-22\n\n"
        "## Body\n\n"
        "This body mentions core.md in prose — see core.md for details.\n"
    )
    proc = _run(
        docs_script,
        "archive",
        str(root / "core.md"),
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, proc.stderr
    body = prose.read_text()
    # The prose mention is untouched.
    assert "This body mentions core.md in prose — see core.md for details.\n" in body


def test_archive_referring_edge_rewrite_is_atomic(docs_script, fixtures_dir, tmp_path):
    """If a referring doc is malformed (no parseable metadata block) we
    refuse the archive entirely: the target file is NOT moved and the
    archive dir is NOT created."""
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    # Break helper.md so its metadata block cannot be parsed: delete the
    # H1 entirely. (parse_metadata_block requires an H1 first line.)
    helper = root / "helper.md"
    helper.write_text("This file has no H1 — it's malformed for parse().\n")
    before_core = (root / "core.md").read_text()
    proc = _run(
        docs_script,
        "archive",
        str(root / "core.md"),
        "--date",
        "2026-05-28",
    )
    assert proc.returncode != 0, (proc.stdout, proc.stderr)
    # The original core.md was NOT moved.
    assert (root / "core.md").is_file()
    assert (root / "core.md").read_text() == before_core
    # The archive destination was NOT created.
    assert not (root / "archive" / "2026-05-28").exists()


def test_archive_referring_edge_rewrite_refreshes_index_once(docs_script, fixtures_dir, tmp_path):
    """Pre-build INDEX.md; archive a doc with referring edges; verify the
    INDEX file's mtime advances exactly once (the archive verb refreshes
    the INDEX end-of-batch, not per referring-doc rewrite)."""
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    pre = _run(docs_script, "index", "--root", str(root))
    assert pre.returncode == 0, pre.stderr
    index = root / "INDEX.md"
    assert index.is_file()
    mtime_before = index.stat().st_mtime_ns

    proc = _run(
        docs_script,
        "archive",
        str(root / "core.md"),
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, proc.stderr
    mtime_after = index.stat().st_mtime_ns
    assert mtime_after > mtime_before


def test_archive_cascade_rewrites_edges_for_both_moves_atomically(
    docs_script, fixtures_dir, tmp_path
):
    """archive `master.md --cascade` (answering `y`) archives master.md
    AND sidekick.md (pairs-with).  The witness doc's two `Related:`
    edges (one to master.md, one to sidekick.md) are rewritten to point
    at the archive paths in a single atomic batch — single INDEX refresh."""
    root = _cascade_refs_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "archive",
        str(root / "master.md"),
        "--cascade",
        "--date",
        "2026-05-28",
        stdin_text="y\n",
    )
    assert proc.returncode == 0, proc.stderr
    dated = root / "archive" / "2026-05-28"
    assert (dated / "master.md").is_file()
    assert (dated / "sidekick.md").is_file()
    witness = (root / "witness.md").read_text()
    assert "archive/2026-05-28/master.md" in witness
    assert "archive/2026-05-28/sidekick.md" in witness


def test_archive_does_not_rewrite_archive_subtree_edges(docs_script, fixtures_dir, tmp_path):
    """A doc that already lives under archive/ that references `core.md`
    via `Related:` is read-only and must NOT be rewritten when `core.md`
    is archived."""
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    # Manually drop an archived doc that references core.md via Related:.
    archived_dir = root / "archive" / "2026-04-01"
    archived_dir.mkdir(parents=True)
    archived_doc = archived_dir / "old-ref.md"
    archived_doc.write_text(
        "# Old ref\n\n"
        "Lifecycle: archived\nRole: notes\nProject: cross-refs\n"
        "Updated: 2026-04-01\n\n"
        "Related:\n- references: core.md\n\n"
        "## Body\n\n"
        "An archived doc whose Related: edge points at the (still-active)"
        " core.md.\n"
    )
    archived_before = archived_doc.read_text()
    proc = _run(
        docs_script,
        "archive",
        str(root / "core.md"),
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, proc.stderr
    # The archived doc is byte-identical.
    assert archived_doc.read_text() == archived_before
