"""CLI end-to-end tests for `docs new` (Phase 2 — written RED).

Invokes the executable as a subprocess, per the M1 convention.
"""

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
    """Copy the minimal fixture tree into tmp_path; return its root."""
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "minimal", root)
    return root


def test_new_help_lists_role_and_slug(docs_script):
    proc = _run(docs_script, "new", "--help")
    assert proc.returncode == 0
    assert "role" in proc.stdout.lower()
    assert "slug" in proc.stdout.lower()


def test_new_creates_the_file(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "my-feature", "--root", str(root))
    assert proc.returncode == 0, proc.stderr
    assert (root / "my-feature.md").is_file()


def test_new_scaffolds_metadata_block(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "my-feature", "--root", str(root))
    assert proc.returncode == 0, proc.stderr
    text = (root / "my-feature.md").read_text()
    assert "Lifecycle: draft" in text
    assert "Role: spec" in text
    assert f"Updated: {date.today().isoformat()}" in text


def test_new_title_defaults_to_titlecased_slug(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "my-feature", "--root", str(root))
    assert proc.returncode == 0, proc.stderr
    assert (root / "my-feature.md").read_text().startswith("# My Feature\n")


def test_new_title_override(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "new",
        "spec",
        "my-feature",
        "--title",
        "A Custom Title",
        "--root",
        str(root),
    )
    assert proc.returncode == 0, proc.stderr
    assert (root / "my-feature.md").read_text().startswith("# A Custom Title\n")


def test_new_project_flag_sets_project(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "new",
        "spec",
        "my-feature",
        "--project",
        "otherproj",
        "--root",
        str(root),
    )
    assert proc.returncode == 0, proc.stderr
    assert "Project: otherproj" in (root / "my-feature.md").read_text()


def test_new_invalid_role_exits_2(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "bogusrole", "my-feature", "--root", str(root))
    assert proc.returncode == 2
    assert "role" in proc.stderr.lower()


def test_new_existing_file_exits_1(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    # lone-doc.md already exists in the minimal tree.
    proc = _run(docs_script, "new", "spec", "lone-doc", "--root", str(root))
    assert proc.returncode == 1
    assert "exist" in proc.stderr.lower()


def test_new_does_not_refresh_index(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    index = root / "INDEX.md"
    before = index.read_text() if index.exists() else None
    proc = _run(docs_script, "new", "spec", "my-feature", "--root", str(root))
    assert proc.returncode == 0, proc.stderr
    after = index.read_text() if index.exists() else None
    assert before == after


def test_new_dry_run_creates_nothing(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "my-feature", "--root", str(root), "--dry-run")
    assert proc.returncode == 0, proc.stderr
    assert not (root / "my-feature.md").exists()


def test_new_dry_run_invalid_role_still_exits_2(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "bogusrole", "my-feature", "--root", str(root), "--dry-run")
    assert proc.returncode == 2


def test_new_nested_slug_creates_subdirectory(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "topics/deep", "--root", str(root))
    assert proc.returncode == 0, proc.stderr
    assert (root / "topics" / "deep.md").is_file()


def test_new_slug_escaping_root_is_rejected(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "../escape", "--root", str(root))
    assert proc.returncode == 2
    assert not (tmp_path / "escape.md").exists()


# --- M14 A2 — new refuses the cwd-as-root fallback --------------------------


def _orphan_dir(tmp_path: Path) -> Path:
    """Make `tmp_path/orphan/` with NO `.docs.toml` on its upward chain.

    Suitable as `cwd=` for `_run` so the upward `.docs.toml` walk surfaces
    nothing — `docs new` (no `--root`) must refuse rather than scaffold
    into the unmanaged dir with default config.
    """
    orphan = tmp_path / "orphan"
    orphan.mkdir()
    return orphan


def test_new_outside_docs_root_exits_2(docs_script, tmp_path):
    """`docs new` from a cwd with no `.docs.toml` ancestor and no `--root`
    must refuse (exit 2) and write nothing.

    RED reason: `_cmd_new` resolves the root via `find_root(Path.cwd())`
    (cli.py:3278), whose fallback is `cwd.resolve()` — so today `docs new`
    silently scaffolds into the orphan dir (exit 0). Step 2 wires the
    strict resolver (`_find_root_strict` / a `_resolve_*_root` analogue)
    so it refuses.
    """
    orphan = _orphan_dir(tmp_path)
    proc = _run(docs_script, "new", "spec", "my-feature", cwd=orphan)
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "is not under a docs root with .docs.toml" in proc.stderr
    assert "refusing" in proc.stderr
    # Nothing was written into the orphan dir.
    assert not (orphan / "my-feature.md").exists()


def test_new_root_without_docs_toml_refuses(docs_script, tmp_path):
    """`docs new --root <dir>` with `<dir>/.docs.toml` missing must refuse
    (exit 2) with the `--root` refusal message, writing nothing.

    RED reason: `_cmd_new` only checks `root.is_dir()` (cli.py:3279), not
    `.docs.toml` presence, so an explicit `--root` to a plain directory
    scaffolds today (exit 0). Step 2 validates `.docs.toml` presence.
    """
    orphan = _orphan_dir(tmp_path)
    proc = _run(docs_script, "new", "spec", "my-feature", "--root", str(orphan))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "--root" in proc.stderr
    assert "does not contain .docs.toml" in proc.stderr
    assert "refusing" in proc.stderr
    assert not (orphan / "my-feature.md").exists()


def test_new_inside_root_still_works_without_root_flag(docs_script, fixtures_dir, tmp_path):
    """Guard against over-refusal: `docs new` from a cwd that IS inside a
    real docs root (no `--root` flag) must still succeed (exit 0).

    This is GREEN today and must STAY GREEN after Step 2 — the strict
    resolver refuses only when there is no `.docs.toml` ancestor.
    """
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "my-feature", cwd=root)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (root / "my-feature.md").is_file()


# --- M14 A3 — empty final-segment slug rejected -----------------------------


def test_new_empty_final_segment_slug_rejected(docs_script, fixtures_dir, tmp_path):
    """`docs new spec "foo/"` must be rejected (exit 2) and must NOT write
    an invisible `foo/.md` dotfile.

    RED reason: `_cmd_new`'s slug guard (cli.py:3299-3306) checks
    `not slug.strip()`, absolute, `..`, and archive-subtree, but a slug
    whose final segment is empty (`foo/` → target `foo/.md`) passes the
    guard and writes a `.md` dotfile. Step 2 rejects an empty final
    segment.
    """
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "new", "spec", "foo/", "--root", str(root))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "invalid slug" in proc.stderr.lower()
    # The invisible dotfile must not have been created.
    assert not (root / "foo" / ".md").exists()
    # Defensive: no stray dotfile anywhere under the (possibly created) foo/ dir.
    assert not list(root.glob("foo/.md"))
