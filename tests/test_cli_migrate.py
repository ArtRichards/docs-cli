"""CLI end-to-end tests for `docs migrate` (Phase 2 — written RED).

Invokes the executable as a subprocess, per the M1-M3 convention. `migrate`
mutates files only under `--apply`, so every test that runs `--apply` first
`copytree`s the fixture into `tmp_path` — the committed fixtures are never
mutated.

Every non-`--help` test asserts `"NotImplementedError" not in` the combined
output: a stub raising `NotImplementedError` exits 1, and the false-pass guard
ensures a stub cannot accidentally satisfy an assertion.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from docs import parse  # loaded via conftest's module registration

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


def _foreign_copy(fixtures_dir: Path, tmp_path: Path) -> Path:
    """Copy the foreign fixture tree into tmp_path; return its root."""
    root = tmp_path / "foreign"
    shutil.copytree(fixtures_dir / "trees" / "foreign", root)
    return root


def _snapshot(root: Path) -> dict[str, str]:
    """Map every file's root-relative path to its text content."""
    return {
        p.relative_to(root).as_posix(): p.read_text()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


# --- --help (legitimate RED pass) ------------------------------------------


def test_migrate_help(docs_script):
    proc = _run(docs_script, "migrate", "--help")
    assert proc.returncode == 0
    assert "migrate" in proc.stdout.lower()
    assert "--apply" in proc.stdout


# --- dry-run is the default ------------------------------------------------


def test_migrate_dry_run_is_default_and_writes_nothing(docs_script, fixtures_dir, tmp_path):
    root = _foreign_copy(fixtures_dir, tmp_path)
    before = _snapshot(root)
    proc = _run(docs_script, "migrate", str(root))
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    after = _snapshot(root)
    assert before == after, "dry-run must not modify any file"


def test_migrate_dry_run_reports_every_file(docs_script, fixtures_dir, tmp_path):
    root = _foreign_copy(fixtures_dir, tmp_path)
    md_count = sum(1 for _ in root.rglob("*.md"))
    proc = _run(docs_script, "migrate", str(root))
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The plan names every .md file by its basename.
    for md in root.rglob("*.md"):
        assert md.name in proc.stdout, f"{md.name} missing from the plan"
    assert md_count > 0


# --- --json schema ---------------------------------------------------------


def test_migrate_json_emits_pinned_record_schema(docs_script, fixtures_dir, tmp_path):
    root = _foreign_copy(fixtures_dir, tmp_path)
    proc = _run(docs_script, "migrate", str(root), "--json")
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    data = json.loads(proc.stdout)
    assert isinstance(data, list) and data
    expected_keys = {
        "path",
        "role",
        "project",
        "lifecycle",
        "updated",
        "confidence",
        "ambiguities",
        "archive_move",
        "synthesized_h1",
        "reconciled_metadata",
    }
    for rec in data:
        assert set(rec) == expected_keys
        # path is a root-relative POSIX string — never absolute.
        assert isinstance(rec["path"], str)
        assert not rec["path"].startswith("/"), f"path must be root-relative: {rec['path']!r}"
        assert rec["role"] and isinstance(rec["role"], str)
        assert rec["project"] and isinstance(rec["project"], str)
        assert rec["lifecycle"] and isinstance(rec["lifecycle"], str)
        # updated is an ISO YYYY-MM-DD string.
        assert isinstance(rec["updated"], str)
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", rec["updated"]), (
            f"updated must be ISO YYYY-MM-DD: {rec['updated']!r}"
        )
        assert rec["confidence"] in ("high", "medium", "low")
        assert isinstance(rec["ambiguities"], list)
        assert isinstance(rec["synthesized_h1"], bool)
        assert isinstance(rec["reconciled_metadata"], bool)
        assert rec["archive_move"] is None or isinstance(rec["archive_move"], str)


# --- --apply writes convention-correct blocks ------------------------------


def test_migrate_apply_writes_metadata_blocks(docs_script, fixtures_dir, tmp_path):
    root = _foreign_copy(fixtures_dir, tmp_path)
    proc = _run(docs_script, "migrate", str(root), "--apply")
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # Every .md file now parses with the four required fields.
    for md in root.rglob("*.md"):
        doc = parse(md.read_text(), md, root)
        assert doc.lifecycle
        assert doc.role
        assert doc.project
        assert doc.updated is not None


def test_migrate_apply_normalises_archive_style_subdir(docs_script, fixtures_dir, tmp_path):
    root = _foreign_copy(fixtures_dir, tmp_path)
    assert (root / "archived").is_dir(), "fixture must have an archive-style subdir"
    proc = _run(docs_script, "migrate", str(root), "--apply", "--date", "2026-05-22")
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The archive-style subdir's docs moved into archive/<date>/.
    moved = list((root / "archive" / "2026-05-22").glob("*.md"))
    assert moved, "archive-style docs must be relocated into archive/<date>/"
    for md in moved:
        doc = parse(md.read_text(), md, root)
        assert doc.lifecycle == "archived"


def test_migrate_apply_leaves_active_layout_unchanged(docs_script, fixtures_dir, tmp_path):
    root = _foreign_copy(fixtures_dir, tmp_path)
    active_before = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*.md")
        if "archived" not in p.relative_to(root).parts
    }
    proc = _run(docs_script, "migrate", str(root), "--apply")
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    active_after = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*.md")
        if not p.relative_to(root).as_posix().startswith("archive/")
    }
    # Active-tree files keep their paths — migrate adds metadata in place.
    assert active_before == active_after


# --- refuse-on-.docs.toml guard --------------------------------------------


def test_migrate_refuses_a_docs_root(docs_script, fixtures_dir, tmp_path):
    # minimal/ carries a .docs.toml — it is already a managed docs root.
    managed = tmp_path / "managed"
    shutil.copytree(fixtures_dir / "trees" / "minimal", managed)
    before = _snapshot(managed)
    proc = _run(docs_script, "migrate", str(managed))
    # cli.md pins exit 2 for a directory that is already a docs root.
    assert proc.returncode == 2
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert ".docs.toml" in (proc.stdout + proc.stderr) or "docs root" in (proc.stdout + proc.stderr)
    assert _snapshot(managed) == before, "a refused migrate must not touch the tree"


# --- applied tree passes check ---------------------------------------------


def test_migrate_apply_yields_a_tree_check_accepts(docs_script, fixtures_dir, tmp_path):
    root = _foreign_copy(fixtures_dir, tmp_path)
    apply = _run(docs_script, "migrate", str(root), "--apply", "--date", "2026-05-22")
    assert "NotImplementedError" not in (apply.stdout + apply.stderr)
    assert apply.returncode == 0, (apply.stdout, apply.stderr)
    # An applied tree is a conforming tree — `docs check` must accept it.
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


# --- --quiet ---------------------------------------------------------------


def test_migrate_apply_quiet_suppresses_the_summary_line(docs_script, fixtures_dir, tmp_path):
    root = _foreign_copy(fixtures_dir, tmp_path)
    loud = _run(docs_script, "migrate", str(root), "--apply", "--date", "2026-05-22")
    assert "migrated" in loud.stderr, "non-quiet --apply prints a summary to stderr"

    root2 = tmp_path / "foreign2"
    shutil.copytree(fixtures_dir / "trees" / "foreign", root2)
    quiet = _run(docs_script, "migrate", str(root2), "--apply", "--quiet", "--date", "2026-05-22")
    assert "NotImplementedError" not in (quiet.stdout + quiet.stderr)
    assert quiet.returncode == 0, (quiet.stdout, quiet.stderr)
    assert "migrated" not in quiet.stderr, "--quiet must suppress the summary line"


# --- --date validation -----------------------------------------------------


def test_migrate_rejects_a_malformed_date_with_a_date_label(docs_script, fixtures_dir, tmp_path):
    root = _foreign_copy(fixtures_dir, tmp_path)
    proc = _run(docs_script, "migrate", str(root), "--date", "not-a-date")
    assert proc.returncode == 2
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    # The error names the --date flag the user actually supplied — matching
    # `docs archive --date` (review finding #2).
    assert "docs: --date:" in proc.stderr


# --- extra-metadata preservation (review finding #3) -----------------------


def test_migrate_apply_preserves_extra_metadata_in_a_section(docs_script, fixtures_dir, tmp_path):
    root = _foreign_copy(fixtures_dir, tmp_path)
    extra = root / "proj-extra-metadata.md"
    assert extra.is_file(), "fixture must carry a file with extra metadata"
    proc = _run(docs_script, "migrate", str(root), "--apply", "--date", "2026-05-22")
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    migrated = extra.read_text()
    # The non-required fields are preserved under `## Migrated metadata`.
    assert "## Migrated metadata" in migrated
    assert "Migrated-Owner: alice" in migrated
    assert "Migrated-Tags:" in migrated
    assert "Migrated-Related:" in migrated
    # The applied file still parses and carries the four required fields.
    doc = parse(migrated, extra, root)
    assert doc.lifecycle and doc.role and doc.project and doc.updated is not None
    # The applied tree still passes `docs check`.
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


def test_migrate_dry_run_reports_preserved_extra_fields(docs_script, fixtures_dir, tmp_path):
    root = _foreign_copy(fixtures_dir, tmp_path)
    proc = _run(docs_script, "migrate", str(root))
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The dry-run human plan notes how many extra fields are preserved.
    assert "extra field(s) preserved" in proc.stdout


# --- archive-move collision (review finding #1) ----------------------------


def test_migrate_flags_archive_move_collision_in_dry_run(docs_script, tmp_path):
    # Two foreign files with the same basename in different archive-style
    # subdirs both normalise to one archive/<date>/ destination.
    root = tmp_path / "collide"
    (root / "archived").mkdir(parents=True)
    (root / "project-history").mkdir(parents=True)
    (root / "archived" / "dup.md").write_text("# One\n\nFirst.\n")
    (root / "project-history" / "dup.md").write_text("# Two\n\nSecond.\n")
    proc = _run(docs_script, "migrate", str(root), "--date", "2026-05-22")
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The dry-run plan surfaces the collision as an ambiguity.
    assert "collision" in proc.stdout


def test_migrate_apply_refuses_an_archive_move_collision(docs_script, tmp_path):
    root = tmp_path / "collide"
    (root / "archived").mkdir(parents=True)
    (root / "project-history").mkdir(parents=True)
    (root / "archived" / "dup.md").write_text("# One\n\nFirst.\n")
    (root / "project-history" / "dup.md").write_text("# Two\n\nSecond.\n")
    proc = _run(docs_script, "migrate", str(root), "--apply", "--date", "2026-05-22")
    # A colliding --apply must fail (exit 2) rather than silently overwrite.
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
