"""CLI end-to-end tests for `docs project rename` (M12 Phase 2 — written RED)."""

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


def _minimal_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "minimal", root)
    return root


def _multi_project_alpha_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "multi-project-alpha-sidecar", root)
    return root


def _rename_with_archive_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "rename-with-archive", root)
    return root


def _rename_with_malformed_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "rename-with-malformed", root)
    return root


# --- Help / registration ----------------------------------------------------


def test_project_rename_help(docs_script):
    proc = _run(docs_script, "project", "rename", "--help")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "new-name" in proc.stdout or "new_name" in proc.stdout


def test_project_rename_subcommand_registered(docs_script):
    proc = _run(docs_script, "project", "--help")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "rename" in proc.stdout


# --- Happy path -------------------------------------------------------------


def test_project_rename_rewrites_docs_toml(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    sidecar_before = (root / ".docs.toml").read_text()
    proc = _run(docs_script, "project", "rename", "foo", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    sidecar_after = (root / ".docs.toml").read_text()
    assert 'name = "foo"' in sidecar_after
    assert 'name = "minimal"' not in sidecar_after
    # Lines other than the project-name line are byte-identical.
    before_lines = [ln for ln in sidecar_before.splitlines() if not ln.startswith("name =")]
    after_lines = [ln for ln in sidecar_after.splitlines() if not ln.startswith("name =")]
    assert before_lines == after_lines


def test_project_rename_rewrites_every_matching_project_line(docs_script, fixtures_dir, tmp_path):
    # Three docs all named Project: minimal. After rename, all three read
    # Project: foo.
    root = _minimal_tree(fixtures_dir, tmp_path)
    # Add two more docs alongside lone-doc.md to make this three-deep.
    (root / "extra1.md").write_text(
        "# Extra 1\n\nLifecycle: active\nRole: notes\nProject: minimal\n"
        "Updated: 2026-05-20\n\nBody.\n"
    )
    (root / "extra2.md").write_text(
        "# Extra 2\n\nLifecycle: active\nRole: notes\nProject: minimal\n"
        "Updated: 2026-05-20\n\nBody.\n"
    )

    proc = _run(docs_script, "project", "rename", "foo", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    for name in ("lone-doc.md", "extra1.md", "extra2.md"):
        text = (root / name).read_text()
        assert "Project: foo" in text, f"{name} missing rewrite"
        assert "Project: minimal" not in text, f"{name} still references old project"


def test_project_rename_skips_non_matching_project(docs_script, fixtures_dir, tmp_path):
    # multi-project-alpha-sidecar has [project] name = "alpha" but carries
    # docs from both alpha and beta projects. A rename of alpha → gamma
    # must rewrite ONLY the alpha docs.
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "project", "rename", "gamma", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    for name in ("alpha-charter.md", "alpha-plan.md", "alpha-spec.md", "alpha-old-spec.md"):
        text = (root / name).read_text()
        assert "Project: gamma" in text, f"{name} alpha rewrite missing"
    for name in ("beta-status.md", "beta-notes.md", "beta-done.md"):
        text = (root / name).read_text()
        assert "Project: beta" in text, f"{name} non-matching project mutated"
        assert "Project: gamma" not in text


# --- Refusals ---------------------------------------------------------------


def test_project_rename_refuses_when_no_docs_toml(docs_script, tmp_path):
    bad = tmp_path / "no_docs_toml"
    bad.mkdir()
    proc = _run(docs_script, "project", "rename", "foo", cwd=bad)
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    # The stderr names the cwd (or some identifier of the missing-root).
    assert "is not under a docs root" in proc.stderr
    assert "refusing" in proc.stderr


def test_project_rename_rejects_empty_input(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "project", "rename", "", "--root", str(root))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    # cli.md OQ-9 pins the full message:
    #   "docs: project rename: <input> normalises to empty string;
    #    project name must be non-empty"
    assert "normalises to empty string; project name must be non-empty" in proc.stderr


def test_project_rename_rejects_whitespace_only_input(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "project", "rename", "   ", "--root", str(root))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    # Same full-message pin as the empty-string test (cli.md OQ-9).
    assert "normalises to empty string; project name must be non-empty" in proc.stderr


# --- Dry-run / normalisation / quiet ----------------------------------------


def test_project_rename_dry_run_makes_no_change(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    before = {
        ".docs.toml": (root / ".docs.toml").read_text(),
        "lone-doc.md": (root / "lone-doc.md").read_text(),
    }
    proc = _run(docs_script, "project", "rename", "foo", "--root", str(root), "--dry-run")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (root / ".docs.toml").read_text() == before[".docs.toml"]
    assert (root / "lone-doc.md").read_text() == before["lone-doc.md"]
    # cli.md pins two dry-run line shapes:
    #   per-doc: "docs: would rewrite Project: in <rel-path>"
    #   sidecar: 'docs: would rewrite [project] name in .docs.toml: "<old>" -> "<new>"'
    assert "would rewrite Project: in" in proc.stderr, proc.stderr
    assert "would rewrite [project] name in .docs.toml" in proc.stderr, proc.stderr
    # The sidecar line carries the old + new quoted names.
    assert '"minimal" -> "foo"' in proc.stderr, proc.stderr


def test_project_rename_normalises_input(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "project", "rename", "FooBarBaz", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    sidecar = (root / ".docs.toml").read_text()
    assert 'name = "foo-bar-baz"' in sidecar
    assert "Project: foo-bar-baz" in (root / "lone-doc.md").read_text()
    assert 'normalised "FooBarBaz" to "foo-bar-baz"' in proc.stderr


def test_project_rename_normalisation_quiet_under_quiet(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "project", "rename", "FooBarBaz", "--root", str(root), "--quiet")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "normalised" not in proc.stderr


# --- Atomicity --------------------------------------------------------------


def test_project_rename_atomic_validate_failure_leaves_tree_unchanged(
    docs_script, fixtures_dir, tmp_path
):
    root = _rename_with_malformed_tree(fixtures_dir, tmp_path)
    before = {
        ".docs.toml": (root / ".docs.toml").read_text(),
        "good-a.md": (root / "good-a.md").read_text(),
        "good-b.md": (root / "good-b.md").read_text(),
        "broken.md": (root / "broken.md").read_text(),
    }
    proc = _run(docs_script, "project", "rename", "foo", "--root", str(root))
    # The malformed doc raises a MetadataError -> exit 1 (recoverable).
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    # The offending path is named in stderr.
    assert "broken.md" in proc.stderr
    # Every other doc + sidecar is byte-identical.
    for name, content in before.items():
        assert (root / name).read_text() == content, f"{name} mutated on validation failure"
    # No INDEX written.
    assert not (root / "INDEX.md").exists()


# --- No-op ------------------------------------------------------------------


def test_project_rename_no_op_when_new_equals_old(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    sidecar_before = (root / ".docs.toml").read_text()
    doc_before = (root / "lone-doc.md").read_text()
    proc = _run(docs_script, "project", "rename", "minimal", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "already current" in proc.stderr
    assert "no rewrites needed" in proc.stderr
    assert (root / ".docs.toml").read_text() == sidecar_before
    assert (root / "lone-doc.md").read_text() == doc_before
    # No INDEX refresh on a no-op.
    assert not (root / "INDEX.md").exists()


# --- INDEX refresh ---------------------------------------------------------


def test_project_rename_refreshes_index_once(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    # Pre-build the INDEX so the rename refreshes (not creates) it.
    pre = _run(docs_script, "index", "--root", str(root))
    assert pre.returncode == 0, pre.stderr
    index = root / "INDEX.md"
    assert index.is_file()
    mtime_before = index.stat().st_mtime_ns

    proc = _run(docs_script, "project", "rename", "foo", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    mtime_after = index.stat().st_mtime_ns
    assert mtime_after > mtime_before, "INDEX must be refreshed after a rename"
    # The new project name is in the INDEX body.
    assert "foo" in index.read_text()

    # Byte-identity idempotency check: a follow-up `docs index` must be a
    # no-op if the rename refreshed INDEX correctly at end-of-batch.
    # Equivalent to "exactly one refresh, correctly placed" — cheaper than
    # mtime equality with sleep and robust on fast filesystems.
    index_after_rename = index.read_bytes()
    noop = _run(docs_script, "index", "--root", str(root))
    assert noop.returncode == 0, noop.stderr
    assert index.read_bytes() == index_after_rename, (
        "INDEX changed on a follow-up `docs index` — the rename did not "
        "leave INDEX in a fully-refreshed state."
    )


# --- Archive subtree --------------------------------------------------------


def test_project_rename_skips_archive_subtree(docs_script, fixtures_dir, tmp_path):
    root = _rename_with_archive_tree(fixtures_dir, tmp_path)
    archived = root / "archive" / "2026-04-01" / "old.md"
    archived_before = archived.read_text()

    proc = _run(docs_script, "project", "rename", "renamed-target", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)

    # The active doc was rewritten.
    assert "Project: renamed-target" in (root / "live.md").read_text()
    # The archived doc still references the original project name and is
    # byte-identical to its pre-call state.
    assert archived.read_text() == archived_before
    assert "Project: rename-target" in archived.read_text()
    # cli.md OQ-2 pins the footer clause "<M> archived skipped".
    assert "1 archived skipped" in proc.stderr


# --- Multi-project footer ---------------------------------------------------


def test_project_rename_footer_reports_non_matching_count(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "project", "rename", "gamma", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # cli.md OQ-2 pins the success footer literal:
    #   "<K> non-matching project(s) untouched: <list>"
    # The multi-project-alpha-sidecar fixture has three beta-named docs in
    # the active subtree (beta-status.md Lifecycle:active,
    # beta-notes.md Lifecycle:draft, beta-done.md Lifecycle:done — all
    # outside archive/, so all three are walked).
    marker = "non-matching project(s) untouched:"
    assert marker in proc.stderr, proc.stderr
    after_marker = proc.stderr.split(marker, 1)[1]
    assert "beta" in after_marker, proc.stderr
    # The count number (3) appears in the footer.
    assert "3 non-matching project(s) untouched:" in proc.stderr, proc.stderr


# --- Implicit Project: line insertion (OQ-γ-bis) ----------------------------


def test_project_rename_inserts_project_line_when_absent(docs_script, fixtures_dir, tmp_path):
    # Docs with no explicit `Project:` line implicitly resolve to the docs-root
    # project; on rename, a `Project: <new>` line must be inserted (consistent
    # with M2's set_metadata_field behaviour for missing-field cases).
    #
    # The multi-project-alpha-sidecar fixture has `topics/orphan.md` with no
    # `Project:` line in its metadata block; after `docs project rename alpha
    # -> alpha-renamed`, that doc must carry `Project: alpha-renamed`.
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    orphan = root / "topics" / "orphan.md"

    # Pre-state: no Project: line in the orphan doc.
    pre_text = orphan.read_text()
    assert not any(line.startswith("Project:") for line in pre_text.splitlines()), (
        "fixture invariant: topics/orphan.md must carry no Project: line"
    )

    proc = _run(docs_script, "project", "rename", "alpha-renamed", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)

    # Post-state: a Project: alpha-renamed line was inserted.
    post_text = orphan.read_text()
    assert "Project: alpha-renamed" in post_text, post_text

    # The alpha-named docs were rewritten in the usual way.
    for name in ("alpha-charter.md", "alpha-plan.md", "alpha-spec.md", "alpha-old-spec.md"):
        text = (root / name).read_text()
        assert "Project: alpha-renamed" in text, f"{name} alpha rewrite missing"

    # The sidecar was renamed.
    assert 'name = "alpha-renamed"' in (root / ".docs.toml").read_text()


# --- Prose is not touched ---------------------------------------------------


def test_project_rename_does_not_touch_prose(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(fixtures_dir, tmp_path)
    # Add a doc whose prose mentions the old project name.
    prose_doc = root / "prose.md"
    body = (
        "# Prose doc\n\n"
        "Lifecycle: active\nRole: notes\nProject: minimal\nUpdated: 2026-05-20\n\n"
        "## Body\n\n"
        "This doc's body mentions minimal in prose and links to minimal-page.\n"
    )
    prose_doc.write_text(body)
    proc = _run(docs_script, "project", "rename", "foo", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    text = prose_doc.read_text()
    # The Project: line is rewritten.
    assert "Project: foo" in text
    # The prose body is byte-identical (it still says "minimal" twice).
    assert "This doc's body mentions minimal in prose and links to minimal-page.\n" in text


# --- M14 A6 — project rename end-of-batch reindex honours [exclude] ---------


def _rename_excluded_malformed_tree(tmp_path: Path) -> Path:
    """Build a docs root with `[exclude] dirs = ["vendor"]`, conformant docs
    carrying `Project: old`, and a malformed `vendor/README.md`.

    Returns the root. The malformed vendor file must NOT fail the
    validate-all-first walk nor the end-of-batch reindex (it is excluded).
    """
    root = tmp_path / "rename-excl"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "old"\n\n[archive]\ndir = "archive"\n\n[exclude]\ndirs = ["vendor"]\n'
    )
    (root / "spec.md").write_text(
        "# Spec\n\nLifecycle: active\nRole: spec\nProject: old\n"
        "Updated: 2026-01-01\n\n## Body\n\nA conformant doc naming the old project.\n"
    )
    vendor = root / "vendor"
    vendor.mkdir()
    (vendor / "README.md").write_text("no metadata\n# H1\n")
    return root


def test_project_rename_with_malformed_excluded_file_succeeds(docs_script, tmp_path):
    """`docs project rename` over a tree whose `[exclude]` set holds a
    malformed file must rewrite the project name AND refresh the INDEX
    cleanly (exit 0).

    RED reason: `_cmd_project_rename` runs its validate-all-first walk
    (`for doc in walk(root, config)`, cli.py:3768) and its end-of-batch
    `_refresh_index(root, load_config(root))` (cli.py:3846) with NO
    predicate, so the excluded malformed `vendor/README.md` makes the
    validate walk raise → exit 1. Step 2 threads
    `compile_exclude_predicate(config, [])` into both.
    """
    root = _rename_excluded_malformed_tree(tmp_path)
    vendor_readme = root / "vendor" / "README.md"
    vendor_before = vendor_readme.read_text()

    proc = _run(docs_script, "project", "rename", "new", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The sidecar + the conformant doc were rewritten.
    assert 'name = "new"' in (root / ".docs.toml").read_text()
    assert "Project: new" in (root / "spec.md").read_text()
    # The excluded malformed file is byte-unchanged and not in the INDEX.
    assert vendor_readme.read_text() == vendor_before
    index = (root / "INDEX.md").read_text()
    assert "vendor/README.md" not in index, "the excluded file must not appear in INDEX"
