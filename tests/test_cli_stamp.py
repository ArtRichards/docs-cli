"""CLI end-to-end tests for `docs stamp` (M15 — B3; Phase 2, written RED).

`docs stamp <file>...` stamps a convention-correct metadata block onto a
file an agent already wrote (write-then-stamp). These tests pin the cli.md
contract authored in Phase 1:

- inserts a metadata block (Lifecycle: draft, Role, Project, Updated) and
  preserves the body verbatim (parses cleanly afterwards);
- title from H1; synthesise `# <title-cased-filename>` when absent;
- role from --role else default `notes` (NO H1-role inference);
- project from --project else config.project;
- idempotent re-stamp = no-op bar an Updated: refresh;
- preserves foreign metadata under `## Migrated metadata`;
- --dry-run writes nothing;
- atomic multi-file batch (a bad/missing file aborts before any write,
  exit 1);
- invalid --role → exit 2; outside-root → exit 2.

RED until Phase 5 wires the `stamp` subparser + Phase 6 implements
`_cmd_stamp`. The verb tests fail today with argparse exit 2
("invalid choice: 'stamp'") — the verb is not registered.
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


def _stamp_tree(fixtures_dir: Path, tmp_path: Path, *fixture_names: str) -> Path:
    """Build a docs root with a minimal .docs.toml and copy stamp fixtures in.

    Mirrors the `_minimal_tree` helper pattern from `test_body_from.py`: the
    tree carries a valid `.docs.toml` (project name = "tree") so strict-root
    resolution succeeds and the `Project:` default reads "tree".
    """
    root = tmp_path / "tree"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "tree"\n\n[archive]\ndir = "archive"\n')
    for name in fixture_names:
        shutil.copy(fixtures_dir / "stamp" / name, root / name)
    return root


# --- Help / registration ----------------------------------------------------


def test_stamp_help(docs_script):
    proc = _run(docs_script, "stamp", "--help")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "--role" in proc.stdout
    assert "--project" in proc.stdout
    assert "--title" in proc.stdout


def test_stamp_subcommand_registered(docs_script):
    proc = _run(docs_script, "--help")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "stamp" in proc.stdout


# --- Inserts a valid metadata block (body preserved) ------------------------


def test_stamp_inserts_metadata_block(docs_script, fixtures_dir, tmp_path):
    root = _stamp_tree(fixtures_dir, tmp_path, "raw-no-frontmatter.md")
    target = root / "raw-no-frontmatter.md"
    body_before = target.read_text()
    proc = _run(docs_script, "stamp", "raw-no-frontmatter.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    text = target.read_text()
    assert "Lifecycle: draft" in text, text
    assert "Role: notes" in text, text
    assert "Project: tree" in text, text
    assert f"Updated: {date.today():%Y-%m-%d}" in text, text
    # The body content is preserved verbatim somewhere after the block.
    # (the fixture's distinctive body line survives the stamp).
    assert "BODYMARKER" in text, text
    # cli.md pins the fresh-stamp success line: "docs: stamped <path>".
    assert "stamped" in proc.stderr and "raw-no-frontmatter.md" in proc.stderr, proc.stderr
    # The stamped doc parses + passes check.
    chk = _run(docs_script, "check", "--root", str(root))
    assert chk.returncode == 0, (chk.stdout, chk.stderr)
    assert body_before != text


# --- Title from H1 ----------------------------------------------------------


def test_stamp_title_from_h1(docs_script, fixtures_dir, tmp_path):
    root = _stamp_tree(fixtures_dir, tmp_path, "raw-no-frontmatter.md")
    proc = _run(docs_script, "stamp", "raw-no-frontmatter.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    text = (root / "raw-no-frontmatter.md").read_text()
    # The fixture's H1 is `# Raw Title` — it is preserved as the title.
    assert text.lstrip().startswith("# Raw Title"), text


# --- Synthesise H1 when absent ----------------------------------------------


def test_stamp_synthesises_h1_when_absent(docs_script, fixtures_dir, tmp_path):
    root = _stamp_tree(fixtures_dir, tmp_path, "raw-no-h1.md")
    proc = _run(docs_script, "stamp", "raw-no-h1.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    text = (root / "raw-no-h1.md").read_text()
    # No H1 in the fixture → one synthesised from the filename, title-cased.
    # Assert the H1 LINE equals exactly the expected title (not a prefix): a
    # `startswith` would accept a leaked `.md`/`.Md` extension
    # (`# Raw No H1.Md`.startswith(`# Raw No H1`) is True). Pin the whole line.
    h1_lines = [ln for ln in text.splitlines() if ln.startswith("# ")]
    assert h1_lines, text
    assert h1_lines[0] == "# Raw No H1", h1_lines[0]
    assert ".md" not in h1_lines[0].lower(), h1_lines[0]


# --- Title from --title overrides the existing/synthesised H1 ---------------


def test_stamp_title_flag_overrides_existing_h1(docs_script, fixtures_dir, tmp_path):
    # raw-no-frontmatter.md has the H1 `# Raw Title`; --title with a DIFFERENT
    # value must override it so the doc title/H1 becomes `# Custom Title`.
    root = _stamp_tree(fixtures_dir, tmp_path, "raw-no-frontmatter.md")
    proc = _run(
        docs_script,
        "stamp",
        "raw-no-frontmatter.md",
        "--title",
        "Custom Title",
        "--root",
        str(root),
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    text = (root / "raw-no-frontmatter.md").read_text()
    h1_lines = [ln for ln in text.splitlines() if ln.startswith("# ")]
    assert h1_lines, text
    # The --title value wins over the fixture's `# Raw Title`.
    assert h1_lines[0] == "# Custom Title", h1_lines[0]
    assert "# Raw Title" not in text, text
    # The stamped doc still parses + passes check.
    chk = _run(docs_script, "check", "--root", str(root))
    assert chk.returncode == 0, (chk.stdout, chk.stderr)


# --- Role from flag ---------------------------------------------------------


def test_stamp_role_from_flag(docs_script, fixtures_dir, tmp_path):
    root = _stamp_tree(fixtures_dir, tmp_path, "raw-no-frontmatter.md")
    proc = _run(
        docs_script, "stamp", "raw-no-frontmatter.md", "--role", "spec", "--root", str(root)
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "Role: spec" in (root / "raw-no-frontmatter.md").read_text()


# --- Role default notes — NO H1-role inference ------------------------------


def test_stamp_role_default_notes_no_h1_inference(docs_script, fixtures_dir, tmp_path):
    # The contract is explicit: stamp does NO role inference. The
    # `raw-h1-suggests-role.md` fixture's H1 ends with the word "Plan",
    # which migrate's H1 inference would read as Role: plan; stamp must
    # NOT infer it — a file whose H1 reads like a plan still gets the
    # default `notes` unless --role is passed.
    root = _stamp_tree(fixtures_dir, tmp_path, "raw-h1-suggests-role.md")
    proc = _run(docs_script, "stamp", "raw-h1-suggests-role.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    text = (root / "raw-h1-suggests-role.md").read_text()
    # The H1 trailing word is "Plan" — but stamp does NOT infer it. Assert on
    # the metadata-block `Role:` LINE, not a substring-anywhere match: the
    # fixture's prose body literally contains the phrase `Role: plan` (it
    # documents what migrate's inference WOULD do), so a `"Role: plan" not in
    # text` whole-file check would spuriously fail on legitimate prose. The
    # contract is about the metadata line the block carries.
    role_lines = [ln for ln in text.splitlines() if ln.startswith("Role:")]
    assert role_lines == ["Role: notes"], role_lines


# --- Project from flag / from config ----------------------------------------


def test_stamp_project_from_flag(docs_script, fixtures_dir, tmp_path):
    root = _stamp_tree(fixtures_dir, tmp_path, "raw-no-frontmatter.md")
    proc = _run(
        docs_script,
        "stamp",
        "raw-no-frontmatter.md",
        "--project",
        "myproj",
        "--root",
        str(root),
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "Project: myproj" in (root / "raw-no-frontmatter.md").read_text()


def test_stamp_project_from_config(docs_script, fixtures_dir, tmp_path):
    root = _stamp_tree(fixtures_dir, tmp_path, "raw-no-frontmatter.md")
    proc = _run(docs_script, "stamp", "raw-no-frontmatter.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # No --project → the .docs.toml [project] name "tree".
    assert "Project: tree" in (root / "raw-no-frontmatter.md").read_text()


# --- Idempotent re-stamp refreshes Updated only -----------------------------


def test_stamp_idempotent_re_stamp_refreshes_updated_only(docs_script, fixtures_dir, tmp_path):
    root = _stamp_tree(fixtures_dir, tmp_path, "already-stamped.md")
    target = root / "already-stamped.md"
    before = target.read_text()
    proc = _run(docs_script, "stamp", "already-stamped.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    after = target.read_text()
    # Reports already-stamped.
    assert "already stamped" in proc.stderr, proc.stderr
    # Updated: refreshed to today.
    assert f"Updated: {date.today():%Y-%m-%d}" in after, after
    # Everything else is byte-identical: diff only the Updated: line.
    before_lines = [ln for ln in before.splitlines() if not ln.startswith("Updated:")]
    after_lines = [ln for ln in after.splitlines() if not ln.startswith("Updated:")]
    assert before_lines == after_lines, (before_lines, after_lines)


# --- Preserves foreign metadata under ## Migrated metadata ------------------


def test_stamp_preserves_foreign_metadata(docs_script, fixtures_dir, tmp_path):
    root = _stamp_tree(fixtures_dir, tmp_path, "raw-with-foreign-meta.md")
    proc = _run(docs_script, "stamp", "raw-with-foreign-meta.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    text = (root / "raw-with-foreign-meta.md").read_text()
    # The foreign Owner: line is parked under ## Migrated metadata, renamed.
    assert "## Migrated metadata" in text, text
    assert "Migrated-Owner: alice" in text, text
    # The required block is still valid.
    chk = _run(docs_script, "check", "--root", str(root))
    assert chk.returncode == 0, (chk.stdout, chk.stderr)


# --- Dry-run writes nothing -------------------------------------------------


def test_stamp_dry_run_no_write(docs_script, fixtures_dir, tmp_path):
    root = _stamp_tree(fixtures_dir, tmp_path, "raw-no-frontmatter.md")
    target = root / "raw-no-frontmatter.md"
    before = target.read_text()
    proc = _run(docs_script, "stamp", "raw-no-frontmatter.md", "--root", str(root), "--dry-run")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert target.read_text() == before
    assert "would stamp" in proc.stderr, proc.stderr
    assert not (root / "INDEX.md").exists()


# --- Multi-file atomic (bad file aborts before any write, exit 1) -----------


def test_stamp_multi_file_atomic_bad_file_aborts(docs_script, fixtures_dir, tmp_path):
    root = _stamp_tree(fixtures_dir, tmp_path, "raw-no-frontmatter.md")
    good = root / "raw-no-frontmatter.md"
    good_before = good.read_text()
    # One good file + one missing file: the batch must abort before ANY
    # write (the good file stays byte-identical), exit 1.
    proc = _run(
        docs_script,
        "stamp",
        "raw-no-frontmatter.md",
        "missing.md",
        "--root",
        str(root),
    )
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "missing.md" in proc.stderr, proc.stderr
    assert good.read_text() == good_before, "good file mutated despite atomic abort"
    assert not (root / "INDEX.md").exists()


# --- Invalid --role → exit 2 ------------------------------------------------


def test_stamp_invalid_role_exit_2(docs_script, fixtures_dir, tmp_path):
    root = _stamp_tree(fixtures_dir, tmp_path, "raw-no-frontmatter.md")
    target = root / "raw-no-frontmatter.md"
    before = target.read_text()
    proc = _run(
        docs_script,
        "stamp",
        "raw-no-frontmatter.md",
        "--role",
        "not-a-role",
        "--root",
        str(root),
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    # The refusal must be the ROLE-vocabulary error naming the bad value —
    # NOT argparse's unregistered-verb "invalid choice: 'stamp'". This pins
    # that the `stamp` verb itself rejects the role (mirrors `docs new`'s
    # `docs: invalid role '<value>' (not in the Role vocabulary)`), so the
    # test does not pass merely because the verb is unregistered.
    assert "role" in proc.stderr.lower(), proc.stderr
    assert "not-a-role" in proc.stderr, proc.stderr
    assert "invalid choice" not in proc.stderr, proc.stderr
    # No write on an invalid role.
    assert target.read_text() == before


# --- Outside-root refusal (exit 2) ------------------------------------------


def test_stamp_refuses_when_no_docs_toml(docs_script, tmp_path):
    bad = tmp_path / "no_docs_toml"
    bad.mkdir()
    (bad / "raw.md").write_text("# Raw\n\nBODYMARKER body.\n")
    proc = _run(docs_script, "stamp", "raw.md", cwd=bad)
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    # The refusal must carry the verb-specific prefix `docs: stamp:`.
    assert "docs: stamp:" in proc.stderr, proc.stderr
    assert "is not under a docs root" in proc.stderr, proc.stderr
    assert "refusing" in proc.stderr, proc.stderr
