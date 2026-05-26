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


# --- M10 D1 — `docs touch <file...>` multi-file + atomic + single-INDEX ----


def _multi_file_tree(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    """Build a docs-managed tree with three .md files under tmp_path.

    Returns (root, a, b, c). Each file carries an old `Updated:` so a touch
    visibly bumps it to today. The `.docs.toml` makes the dir a docs root
    (so the multi-file batch picks up a real INDEX.md refresh).
    """
    root = tmp_path / "multi"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "multi"\n')
    _hdr = "Lifecycle: active\nRole: notes\nProject: multi\n"
    bodies = [
        ("a.md", f"# A\n\n{_hdr}Updated: 2026-01-01\n\nBody A.\n"),
        ("b.md", f"# B\n\n{_hdr}Updated: 2026-01-02\n\nBody B.\n"),
        ("c.md", f"# C\n\n{_hdr}Updated: 2026-01-03\n\nBody C.\n"),
    ]
    paths: list[Path] = []
    for name, body in bodies:
        p = root / name
        p.write_text(body)
        paths.append(p)
    return root, paths[0], paths[1], paths[2]


def test_touch_multi_file_bumps_all_three_to_today(docs_script, tmp_path):
    root, a, b, c = _multi_file_tree(tmp_path)
    proc = _run(docs_script, "touch", str(a), str(b), str(c))
    assert proc.returncode == 0, proc.stderr
    today = date.today().isoformat()
    for p in (a, b, c):
        assert f"Updated: {today}" in p.read_text(), f"{p.name} not bumped"


def test_touch_multi_file_refreshes_index_once(docs_script, tmp_path):
    root, a, b, c = _multi_file_tree(tmp_path)
    # Pre-build the INDEX so the multi-file batch will refresh, not create.
    pre = _run(docs_script, "index", "--root", str(root))
    assert pre.returncode == 0, pre.stderr
    index = root / "INDEX.md"
    assert index.is_file()

    mtime_before = index.stat().st_mtime_ns
    proc = _run(docs_script, "touch", str(a), str(b), str(c))
    assert proc.returncode == 0, proc.stderr
    mtime_after_first = index.stat().st_mtime_ns
    assert mtime_after_first > mtime_before, (
        "INDEX must be refreshed at least once across the batch"
    )

    # Second run is idempotent — same-day touch ⇒ same body bytes; an
    # idempotent INDEX writer must not rewrite an unchanged file (its
    # mtime stays put).
    proc2 = _run(docs_script, "touch", str(a), str(b), str(c))
    assert proc2.returncode == 0, proc2.stderr
    assert index.stat().st_mtime_ns == mtime_after_first, (
        "a same-day re-touch must be idempotent — INDEX bytes unchanged ⇒ no rewrite"
    )


def test_touch_atomic_failure_leaves_every_file_unchanged(docs_script, tmp_path):
    root, a, b, _c = _multi_file_tree(tmp_path)
    bad = root / "no-such.md"
    before_a = a.read_text()
    before_b = b.read_text()
    proc = _run(docs_script, "touch", str(a), str(b), str(bad))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    # The offending path is named in stderr.
    assert str(bad) in proc.stderr or "no-such.md" in proc.stderr
    # The two good files are byte-identical to their pre-call state.
    _msg = "atomic touch: good file must not be mutated on partial failure"
    assert a.read_text() == before_a, _msg
    assert b.read_text() == before_b, _msg


def test_touch_atomic_failure_does_not_write_index(docs_script, tmp_path):
    root, a, b, _c = _multi_file_tree(tmp_path)
    pre = _run(docs_script, "index", "--root", str(root))
    assert pre.returncode == 0, pre.stderr
    index = root / "INDEX.md"
    before = index.read_bytes()
    bad = root / "no-such.md"
    proc = _run(docs_script, "touch", str(a), str(b), str(bad))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert index.read_bytes() == before, "atomic touch failure must not refresh INDEX"


def test_touch_multi_file_dry_run_modifies_nothing(docs_script, tmp_path):
    root, a, b, c = _multi_file_tree(tmp_path)
    pre = _run(docs_script, "index", "--root", str(root))
    assert pre.returncode == 0, pre.stderr
    index = root / "INDEX.md"
    index_before = index.read_bytes()
    before = {p.name: p.read_text() for p in (a, b, c)}
    proc = _run(docs_script, "touch", str(a), str(b), str(c), "--dry-run")
    assert proc.returncode == 0, proc.stderr
    for p in (a, b, c):
        assert p.read_text() == before[p.name], f"{p.name} body changed on --dry-run"
    assert index.read_bytes() == index_before, "INDEX must not refresh on --dry-run"
