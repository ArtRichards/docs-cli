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
    bytes_after_first = index.read_bytes()
    assert mtime_after_first > mtime_before, (
        "INDEX must be refreshed at least once across the batch"
    )

    # Second run is idempotent — same-day touch ⇒ same body bytes ⇒
    # INDEX content unchanged. We pin CONTENT idempotence (the contract),
    # not mtime equality: an mtime check would force the impl to
    # content-skip on identical bytes (out of OQ-C scope), but a contract
    # of "the second pass produces the same INDEX as the first" is exactly
    # what idempotent touch promises.
    proc2 = _run(docs_script, "touch", str(a), str(b), str(c))
    assert proc2.returncode == 0, proc2.stderr
    assert index.read_bytes() == bytes_after_first, (
        "a same-day re-touch must be idempotent — INDEX bytes unchanged"
    )


def test_touch_atomic_failure_leaves_every_file_unchanged(docs_script, tmp_path):
    # `_c` is the third file built by `_multi_file_tree`; this test only
    # verifies the two batched-and-untouched files plus the bad path, so
    # the unused name is intentional (kept to share the helper signature
    # with the multi-file happy-path tests).
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


# --- M12 — outside-docs-root refusal (OQ-C) ---------------------------------


def _orphan_doc(tmp_path: Path) -> tuple[Path, Path]:
    """Build `tmp_path/no_docs_toml/random.md` with valid metadata but NO
    `.docs.toml` anywhere on the upward chain.

    Returns `(parent_dir, doc_path)`. The parent dir is suitable for use as
    `cwd=...` in `_run` so the upward `.docs.toml` walk surfaces nothing.
    """
    parent = tmp_path / "no_docs_toml"
    parent.mkdir()
    doc = parent / "random.md"
    doc.write_text(
        "# Random\n\nLifecycle: active\nRole: notes\nProject: random\n"
        "Updated: 2026-01-01\n\nBody.\n"
    )
    return parent, doc


def test_touch_outside_docs_root_exits_2(docs_script, tmp_path):
    parent, doc = _orphan_doc(tmp_path)
    before = doc.read_text()
    proc = _run(docs_script, "touch", str(doc), cwd=parent)
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "is not under a docs root with .docs.toml" in proc.stderr
    assert "refusing" in proc.stderr
    # File byte-identical to its pre-call state.
    assert doc.read_text() == before


def test_touch_outside_docs_root_no_index_refresh(docs_script, tmp_path):
    parent, doc = _orphan_doc(tmp_path)
    proc = _run(docs_script, "touch", str(doc), cwd=parent)
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    # No INDEX.md created in the orphan directory.
    assert not (parent / "INDEX.md").exists()


def test_touch_outside_docs_root_names_the_path(docs_script, tmp_path):
    parent, doc = _orphan_doc(tmp_path)
    proc = _run(docs_script, "touch", str(doc), cwd=parent)
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    # The doc path appears verbatim somewhere in stderr.
    assert str(doc) in proc.stderr or "random.md" in proc.stderr


def test_touch_outside_docs_root_explicit_root_bypasses_refusal(docs_script, tmp_path):
    """`docs touch --root <valid-root> <file>` succeeds when <root>/.docs.toml
    exists, even if the file resolution would otherwise have triggered the
    outside-root refusal."""
    valid_root, _doc = _multi_file_tree(tmp_path)[:2]
    # Use one of the multi_file_tree docs (already inside the valid root)
    # with an explicit --root.
    a = valid_root / "a.md"
    proc = _run(docs_script, "touch", "--root", str(valid_root), str(a))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


def test_touch_root_without_docs_toml_refuses(docs_script, tmp_path):
    """`docs touch --root <dir>` with <dir>/.docs.toml missing refuses with
    exit 2 + the `--root` refusal message."""
    parent, doc = _orphan_doc(tmp_path)
    proc = _run(docs_script, "touch", "--root", str(parent), str(doc))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "--root" in proc.stderr
    assert "does not contain .docs.toml" in proc.stderr
    assert "refusing" in proc.stderr
