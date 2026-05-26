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


def test_migrate_allows_a_migrate_only_sidecar_and_honours_project_name(
    docs_script, fixtures_dir, tmp_path
):
    """OQ5 positive contract: a `.docs.toml` carrying ONLY a `[migrate]`
    section (no `[project]`, no `[archive]`, no `[vocabulary]`) is a
    foreign-tree migration sidecar — it must NOT trigger the
    docs-root refusal, and its `project_name` must override the inferred
    project for every plan record.

    Companion to ``test_migrate_refuses_a_docs_root`` — locks the narrowing
    introduced in M7 (cli.py: `managed_sections & data.keys()`).
    """
    root = _foreign_copy(fixtures_dir, tmp_path)
    (root / ".docs.toml").write_text('[migrate]\nproject_name = "foo"\n')

    proc = _run(docs_script, "migrate", str(root), "--json")
    assert proc.returncode == 0, (
        f"a [migrate]-only sidecar must NOT trigger the docs-root refusal; "
        f"got exit {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)

    data = json.loads(proc.stdout)
    assert data, "expected at least one plan record"
    for rec in data:
        assert rec["project"] == "foo", (
            f"[migrate] project_name must override inferred project for every record; got: {rec!r}"
        )


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


# --- M10 D2 — `docs migrate --apply` writes/extends `.docs.toml` -----------


def test_migrate_apply_writes_docs_toml_when_absent(docs_script, fixtures_dir, tmp_path):
    """OQ-A + OQ-M: `--apply` on a tree without `.docs.toml` writes a
    minimal one carrying `[project] name = "<resolved>"` and `[archive]
    date_format`. Per OQ-M, the `[archive]` block emits ONLY
    `date_format` (no redundant `dir = "archive"` — that's the default).
    """
    root = _foreign_copy(fixtures_dir, tmp_path)
    assert not (root / ".docs.toml").exists(), "fixture must not have a pre-existing sidecar"
    proc = _run(docs_script, "migrate", str(root), "--apply", "--date", "2026-05-22")
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    sidecar = root / ".docs.toml"
    assert sidecar.is_file(), "migrate --apply must write a .docs.toml when absent"
    text = sidecar.read_text()
    assert "[project]" in text, ".docs.toml must declare a [project] block"
    # OQ-A: the resolved project name lands verbatim under [project]. The
    # foreign fixture's files all share the `proj-` prefix (per
    # tests/fixtures/trees/foreign/proj-*.md), so `infer_project` resolves
    # to `"proj"`. This pins the "name = <resolved-project>" half of OQ-A.
    assert 'name = "proj"' in text, (
        f"[project] must carry the resolved project name verbatim; got:\n{text}"
    )
    assert "[archive]" in text, ".docs.toml must declare an [archive] block"
    assert 'date_format = "%Y-%m-%d"' in text, "[archive] must carry date_format"
    # OQ-M: only date_format under [archive]; dir is omitted (default is stable).
    assert "dir =" not in text, "OQ-M: [archive] dir must NOT be emitted (default is stable)"


def test_migrate_apply_extends_sidecar_without_overwriting_project(
    docs_script, fixtures_dir, tmp_path
):
    """OQ-A + OQ-L: a pre-existing sidecar carrying ONLY `[migrate]` (or
    `[exclude]`) gets `[project]` appended at the bottom under a
    `# Added by docs migrate --apply` comment header; existing sections
    survive verbatim.
    """
    root = _foreign_copy(fixtures_dir, tmp_path)
    sidecar = root / ".docs.toml"
    pre_existing = '[migrate]\nproject_name = "from-sidecar"\n\n[exclude]\ndirs = ["vendor"]\n'
    sidecar.write_text(pre_existing)
    proc = _run(docs_script, "migrate", str(root), "--apply", "--date", "2026-05-22")
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    text = sidecar.read_text()
    # Existing sections preserved.
    assert "[migrate]" in text
    assert 'project_name = "from-sidecar"' in text
    assert "[exclude]" in text
    assert 'dirs = ["vendor"]' in text
    # New [project] appended at the bottom under a provenance comment header.
    assert "# Added by docs migrate --apply" in text
    assert "[project]" in text
    project_idx = text.index("[project]")
    header_idx = text.index("# Added by docs migrate --apply")
    migrate_idx = text.index("[migrate]")
    exclude_idx = text.index("[exclude]")
    assert migrate_idx < project_idx, "existing [migrate] must precede appended [project]"
    assert exclude_idx < project_idx, "existing [exclude] must precede appended [project]"
    assert header_idx < project_idx, "comment header must sit above appended [project]"
    # OQ-A: the comment header sits IMMEDIATELY above `[project]` — split
    # on the header, take the next non-blank line of the tail, assert it
    # is exactly `[project]`. This pins ordering byte-tight, not loosely.
    _before, _, after_header = text.partition("# Added by docs migrate --apply")
    after_lines = [ln for ln in after_header.splitlines() if ln.strip()]
    assert after_lines, "expected at least one non-blank line after the provenance header"
    assert after_lines[0] == "[project]", (
        f"provenance header must sit immediately above [project]; got next non-blank "
        f"line: {after_lines[0]!r}"
    )


def test_migrate_apply_does_not_overwrite_existing_project_block(
    docs_script, fixtures_dir, tmp_path
):
    """OQ-A: a sidecar that already carries `[project]` is left alone —
    no new `[project]` block, no `# Added by docs migrate --apply` line.

    The pre-existing sidecar carries `[exclude]` so the M8 OQ1 carve-out
    waives the managed-tree refusal and `--apply` actually runs (without
    `[exclude]` the carve-out matrix refuses with exit 2 before any
    .docs.toml editing is attempted, and the body assertions would be
    silently skipped).
    """
    root = _foreign_copy(fixtures_dir, tmp_path)
    sidecar = root / ".docs.toml"
    pre_existing = (
        '[project]\nname = "preserve-me"\n\n'
        '[migrate]\nproject_name = "ignored"\n\n'
        '[exclude]\ndirs = ["build"]\n'
    )
    sidecar.write_text(pre_existing)
    proc = _run(docs_script, "migrate", str(root), "--apply", "--date", "2026-05-22")
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, proc.stderr
    text = sidecar.read_text()
    assert 'name = "preserve-me"' in text, "existing [project] name must be preserved verbatim"
    assert text.count("[project]") == 1, "must not append a duplicate [project] block"
    assert "# Added by docs migrate --apply" not in text, (
        "no provenance header when [project] already exists"
    )


def test_migrate_apply_quiet_suppresses_per_file_output(docs_script, fixtures_dir, tmp_path):
    """OQ-B: `--apply --quiet` produces empty stdout (per-file plan block
    suppressed) AND empties the trailing success-line token on stderr.

    The success line `_cmd_migrate` writes on `--apply` non-quiet is
    `docs: migrated <N> file(s) under <target> (<M> archive move(s))` —
    its grep token is `"migrated"`.
    """
    root = _foreign_copy(fixtures_dir, tmp_path)
    loud = _run(docs_script, "migrate", str(root), "--apply", "--date", "2026-05-22")
    assert "NotImplementedError" not in (loud.stdout + loud.stderr)
    assert loud.returncode == 0, (loud.stdout, loud.stderr)
    assert loud.stdout.strip(), "--apply alone must print the per-file plan to stdout"
    assert "migrated" in loud.stderr, "non-quiet --apply prints the success line to stderr"

    root2 = tmp_path / "foreign2"
    shutil.copytree(fixtures_dir / "trees" / "foreign", root2)
    quiet = _run(docs_script, "migrate", str(root2), "--apply", "--quiet", "--date", "2026-05-22")
    assert "NotImplementedError" not in (quiet.stdout + quiet.stderr)
    assert quiet.returncode == 0, (quiet.stdout, quiet.stderr)
    assert quiet.stdout == "", f"--apply --quiet must produce empty stdout, got {quiet.stdout!r}"
    assert "migrated" not in quiet.stderr, (
        f"--apply --quiet must suppress the trailing success-line token, "
        f"got stderr: {quiet.stderr!r}"
    )


def test_migrate_apply_quiet_suppresses_f11_normalisation_announcement(docs_script, tmp_path):
    """OQ-B regression-lock for the F11 normalisation path: `--apply
    --quiet` against a tree whose `infer_project` raw output normalises
    (`FooBar` -> `foo-bar`) must NOT leak the `project: <final>
    (normalised from "<original>")` announcement onto stdout.

    Pre-fix, `_print_migration_plan` printed the F11 annotation BEFORE
    the `if quiet: return` guard, leaking the announcement + a trailing
    blank line on `--apply --quiet`. This test pins the OQ-B contract
    against the F11 codepath specifically, so future refactors cannot
    silently re-introduce the leak.
    """
    # FooBar-{plan,spec,status}.md -> infer_project basename "FooBar"
    # -> normalise_project_name -> "foo-bar" (distinct from the raw
    # value, so the F11 announcement fires on the non-quiet branch).
    root = tmp_path / "foo-bar-foreign"
    root.mkdir()
    (root / "FooBar-plan.md").write_text("# Plan\n\nBody.\n")
    (root / "FooBar-spec.md").write_text("# Spec\n\nBody.\n")
    (root / "FooBar-status.md").write_text("# Status\n\nBody.\n")

    proc = _run(docs_script, "migrate", str(root), "--apply", "--quiet", "--date", "2026-05-27")
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert proc.stdout == "", (
        f"--apply --quiet must produce empty stdout even when F11 "
        f"normalisation fires; got stdout: {proc.stdout!r}"
    )
    assert proc.stderr == "", (
        f"--apply --quiet must produce empty stderr even when F11 "
        f"normalisation fires; got stderr: {proc.stderr!r}"
    )


def test_migrate_apply_quiet_does_not_suppress_dry_run_or_summary_or_json(
    docs_script, fixtures_dir, tmp_path
):
    """OQ-B: `--quiet` is scoped to `--apply` chatter only. Dry-run
    (`--quiet` alone), `--quiet --summary`, and `--quiet --json` all keep
    their requested outputs.
    """
    # Dry-run + --quiet — the dry-run plan IS the requested output.
    root1 = _foreign_copy(fixtures_dir, tmp_path)
    dry_quiet = _run(docs_script, "migrate", str(root1), "--quiet")
    assert "NotImplementedError" not in (dry_quiet.stdout + dry_quiet.stderr)
    assert dry_quiet.returncode == 0, (dry_quiet.stdout, dry_quiet.stderr)
    assert dry_quiet.stdout.strip(), "--quiet alone (dry-run) must keep the plan on stdout"

    # --quiet --summary — summary IS the requested output.
    root2 = tmp_path / "foreign2"
    shutil.copytree(fixtures_dir / "trees" / "foreign", root2)
    summary_quiet = _run(docs_script, "migrate", str(root2), "--quiet", "--summary")
    assert "NotImplementedError" not in (summary_quiet.stdout + summary_quiet.stderr)
    assert summary_quiet.returncode == 0, (summary_quiet.stdout, summary_quiet.stderr)
    assert summary_quiet.stdout.strip(), "--quiet --summary must keep the summary on stdout"

    # --quiet --json — JSON IS the requested output.
    root3 = tmp_path / "foreign3"
    shutil.copytree(fixtures_dir / "trees" / "foreign", root3)
    json_quiet = _run(docs_script, "migrate", str(root3), "--quiet", "--json")
    assert "NotImplementedError" not in (json_quiet.stdout + json_quiet.stderr)
    assert json_quiet.returncode == 0, (json_quiet.stdout, json_quiet.stderr)
    parsed = json.loads(json_quiet.stdout)
    assert isinstance(parsed, list) and parsed, "--quiet --json must keep the JSON array on stdout"


def test_migrate_apply_quiet_keeps_summary_and_json_outputs(docs_script, fixtures_dir, tmp_path):
    """OQ-B (apply-mode coverage): `--apply --quiet --summary` and
    `--apply --quiet --json` are both "operator asked for this output" —
    only the per-file plan and the trailing success line are chatter.
    The summary block / JSON record array must still land on stdout.

    The single-arg `--apply --quiet` case (empty stdout AND no `migrated`
    token on stderr) is pinned by
    `test_migrate_apply_quiet_suppresses_per_file_output` (SF6).
    """
    # --apply --quiet --summary — summary block is requested output.
    root1 = tmp_path / "apply-quiet-summary"
    shutil.copytree(fixtures_dir / "trees" / "foreign", root1)
    sq = _run(
        docs_script,
        "migrate",
        str(root1),
        "--apply",
        "--quiet",
        "--summary",
        "--date",
        "2026-05-22",
    )
    assert "NotImplementedError" not in (sq.stdout + sq.stderr)
    assert sq.returncode == 0, (sq.stdout, sq.stderr)
    assert sq.stdout.strip(), "--apply --quiet --summary must keep the summary block on stdout"
    assert "summary:" in sq.stdout, "--summary footer block must carry the `summary:` token"

    # --apply --quiet --json — JSON record array is requested output.
    root2 = tmp_path / "apply-quiet-json"
    shutil.copytree(fixtures_dir / "trees" / "foreign", root2)
    jq = _run(
        docs_script,
        "migrate",
        str(root2),
        "--apply",
        "--quiet",
        "--json",
        "--date",
        "2026-05-22",
    )
    assert "NotImplementedError" not in (jq.stdout + jq.stderr)
    assert jq.returncode == 0, (jq.stdout, jq.stderr)
    parsed = json.loads(jq.stdout)
    assert isinstance(parsed, list) and parsed, (
        "--apply --quiet --json must keep the JSON record array on stdout"
    )


def test_migrate_apply_removes_empty_archive_parent_directory(docs_script, tmp_path):
    """OQ-G + OQ-Q: after `--apply`, the now-empty archive-style parent
    directory is removed; the file is at archive/<date>/<basename>.
    Built inline (not on-disk fixture) per the planning agent's call —
    full control over what lives under archived/ so the rmdir guard
    blast radius is exact.
    """
    root = tmp_path / "rmdir-tree"
    archived = root / "archived"
    archived.mkdir(parents=True)
    (archived / "old.md").write_text("# Old\n\nBody.\n")
    proc = _run(docs_script, "migrate", str(root), "--apply", "--date", "2026-05-22")
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The file moved to archive/2026-05-22/old.md
    moved = root / "archive" / "2026-05-22" / "old.md"
    assert moved.is_file(), f"file did not land at the conformant archive destination: {moved}"
    # The empty archive-style parent is gone (OQ-G).
    assert not archived.exists(), "now-empty archived/ parent must be removed after --apply"


def test_migrate_apply_keeps_archive_parent_with_remaining_siblings(docs_script, tmp_path):
    """OQ-G + OQ-Q: the `OSError`-swallow arm. When the archive-style
    parent has a non-migrating sibling (e.g. a stray .txt file or
    anything that's not a planned move), the parent's `rmdir` must
    raise `OSError(ENOTEMPTY)` — the implementation must swallow it
    rather than nuke the sibling. Sibling lives.
    """
    root = tmp_path / "keep-parent-tree"
    archived = root / "archived"
    archived.mkdir(parents=True)
    (archived / "old.md").write_text("# Old\n\nBody.\n")
    sibling = archived / "sibling.txt"
    sibling.write_text("not-a-markdown sibling — must survive --apply\n")
    proc = _run(docs_script, "migrate", str(root), "--apply", "--date", "2026-05-22")
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The .md moved into archive/<date>/.
    assert (root / "archive" / "2026-05-22" / "old.md").is_file()
    # The archive-style parent stays — rmdir swallowed the ENOTEMPTY because
    # the sibling is still there.
    assert archived.is_dir(), "archived/ must remain when a sibling file is still present"
    assert sibling.is_file(), "non-migrating sibling must survive --apply"
