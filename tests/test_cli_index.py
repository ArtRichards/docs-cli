"""CLI end-to-end tests for `docs index` (Phase 2 — written RED).

Invokes the executable as a subprocess. The script is invoked via
`python3 <path-to-script>` so we don't depend on the file being chmod +x
or on `PATH` configuration.
"""

from __future__ import annotations

import re
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


def _normalize_generated_date(text: str) -> str:
    """Blank the wall-clock date in the INDEX `_Generated …_` summary line.

    `render_index` stamps `date.today()` into the summary, so a snapshot frozen
    on one day can never byte-match on another. Normalizing that single line
    keeps the test asserting structure, not the calendar.
    """
    return re.sub(r"_Generated \d{4}-\d{2}-\d{2}\.", "_Generated <date>.", text)


def test_help_prints_usage(docs_script):
    proc = _run(docs_script, "index", "--help")
    assert proc.returncode == 0
    assert "index" in proc.stdout.lower()


def test_index_minimal_tree_exits_zero(docs_script, fixtures_dir, tmp_path):
    src = fixtures_dir / "trees" / "minimal"
    root = tmp_path / "tree"
    shutil.copytree(src, root)
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
    assert proc.stderr
    assert "not found" in proc.stderr.lower()


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
    assert _normalize_generated_date(generated) == _normalize_generated_date(expected)


def test_index_nested_doc_link_is_root_relative(docs_script, fixtures_dir, tmp_path):
    """A doc in a subdirectory must get a root-relative INDEX link.

    M1's `_format_entry` links by `doc.path.name` (basename), so any doc
    outside the root — every archived doc, every doc in a subdir — gets a
    broken link. M2's renderer fix (Phase 5) makes the link the root-relative
    POSIX path. RED until then.
    """
    src = fixtures_dir / "trees" / "nested"
    dst = tmp_path / "tree"
    shutil.copytree(src, dst)
    proc = _run(docs_script, "index", "--root", str(dst))
    assert proc.returncode == 0, proc.stderr
    index = (dst / "INDEX.md").read_text()
    assert "(topics/deep-dive.md)" in index


def _configured_tree(tmp_path: Path, sidecar_extra: str, docs: dict[str, str]) -> Path:
    root = tmp_path / "tree"
    root.mkdir()
    (root / ".docs.toml").write_text(f'[project]\nname = "tree"\n{sidecar_extra}')
    for name, text in docs.items():
        (root / name).write_text(text)
    return root


def _doc(title: str, role: str, updated: str) -> str:
    return (
        f"# {title}\n\nLifecycle: active\nRole: {role}\nProject: tree\nUpdated: {updated}\n\n"
        f"## Body\n\nThe {title} document.\n"
    )


def test_index_renders_an_extension_role_group_after_the_built_in_roles(docs_script, tmp_path):
    """A document in a configured `add_roles` role is RENDERED, under its own
    `### Active — Adr` heading after every built-in group, and the summary
    counts exactly the entries rendered (milestone
    `lifecycle-and-free-form-relate` — D10; 2.0.0 exits 2 on this tree, and a
    config-aware parse alone would count the document without rendering it)."""
    root = _configured_tree(
        tmp_path,
        '\n[vocabulary]\nadd_roles = ["adr"]\n',
        {
            "decision.md": _doc("Decision", "adr", "2026-05-20"),
            "spec.md": _doc("Spec", "spec", "2026-05-20"),
            "notes.md": _doc("Notes", "notes", "2026-05-20"),
        },
    )

    proc = _run(docs_script, "index", "--root", str(root))

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    lines = (root / "INDEX.md").read_text().splitlines()
    headings = [line for line in lines if line.startswith("### Active — ")]
    assert headings == ["### Active — Spec", "### Active — Notes", "### Active — Adr"]
    adr_at = lines.index("### Active — Adr")
    assert any(line.startswith("- [decision.md](decision.md)") for line in lines[adr_at:])
    entries = [line for line in lines if line.startswith("- [")]
    assert len(entries) == 3
    assert any("3 docs active" in line for line in lines)


def test_index_reads_a_non_default_date_format_tree(docs_script, tmp_path):
    """On a `%d-%m-%Y` tree, `Updated:` is read in the tree's format: the INDEX
    renders, entries carry the tree's spelling, and they sort by DATE (1 June
    before 31 May, which a string sort would reverse)."""
    root = _configured_tree(
        tmp_path,
        '\n[archive]\ndate_format = "%d-%m-%Y"\n',
        {
            "may.md": _doc("May", "spec", "31-05-2026"),
            "june.md": _doc("June", "spec", "01-06-2026"),
        },
    )

    proc = _run(docs_script, "index", "--root", str(root))

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    entries = [ln for ln in (root / "INDEX.md").read_text().splitlines() if ln.startswith("- [")]
    assert [entry.split("]")[0] for entry in entries] == ["- [june.md", "- [may.md"]
    assert entries[0].endswith("Updated 01-06-2026.")
    assert entries[1].endswith("Updated 31-05-2026.")
