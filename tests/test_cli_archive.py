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


def test_archive_interactive_yes_also_archives_related(docs_script, fixtures_dir, tmp_path):
    """`--interactive` + a `y` answer archives a pairs-with relation to the
    same dir (the legacy prompt path; M14 — B1).

    MIGRATED from `--cascade` to `--interactive` at M14: bare `--cascade`
    no longer prompts (it takes all one-hop relations non-interactively),
    so the prompt path is now exercised only under `--interactive`.

    RED reason: `--interactive` is not yet a recognised flag (argparse
    rejects it with exit 2). Step 2 adds the flag and routes it to the
    prompt.
    """
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    # helper.md carries `- pairs-with: core.md`.
    proc = _run(docs_script, "archive", str(root / "helper.md"), "--interactive", stdin_text="y\n")
    assert proc.returncode == 0, proc.stderr
    dated = root / "archive" / date.today().isoformat()
    assert (dated / "helper.md").is_file()
    assert (dated / "core.md").is_file()
    assert not (root / "core.md").exists()


def test_archive_interactive_no_leaves_related_in_place(docs_script, fixtures_dir, tmp_path):
    """`--interactive` + an `n` answer leaves the related doc untouched.

    MIGRATED from `--cascade` to `--interactive` at M14 (see above).

    RED reason: `--interactive` is not yet a recognised flag.
    """
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "archive", str(root / "helper.md"), "--interactive", stdin_text="n\n")
    assert proc.returncode == 0, proc.stderr
    dated = root / "archive" / date.today().isoformat()
    assert (dated / "helper.md").is_file()
    assert not (dated / "core.md").exists()
    assert (root / "core.md").is_file()


# --- M14 B1 — non-interactive archive --cascade flag set --------------------


def _two_relation_tree(tmp_path: Path) -> Path:
    """Build a docs root where `root.md` has two one-hop cascade relations.

    `root.md` carries `pairs-with: sub/alpha.md` and `child-of: beta.md`,
    plus a non-cascade `references: gamma.md`. Used to test `--cascade`
    (takes both alpha + beta, NOT gamma) and `--cascade-only` (glob filter
    on the related-doc root-relative POSIX path).
    """
    root = tmp_path / "two-rel"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "two-rel"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: two-rel\n"
    (root / "sub").mkdir()
    (root / "sub" / "alpha.md").write_text(
        f"# Alpha\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\nalpha.\n"
    )
    (root / "beta.md").write_text(f"# Beta\n\n{hdr}Updated: 2026-01-02\n\n## Body\n\nbeta.\n")
    (root / "gamma.md").write_text(f"# Gamma\n\n{hdr}Updated: 2026-01-03\n\n## Body\n\ngamma.\n")
    (root / "root.md").write_text(
        f"# Root\n\n{hdr}Updated: 2026-01-04\n\n"
        "Related:\n- pairs-with: sub/alpha.md\n- child-of: beta.md\n"
        "- references: gamma.md\n\n## Body\n\nthe root doc.\n"
    )
    return root


def test_archive_cascade_no_prompt_archives_all_relations(docs_script, tmp_path):
    """Bare `--cascade` archives ALL one-hop pairs-with/child-of relations
    with NO prompt, and prints a loud stderr footer naming the set.

    No stdin is supplied: if the implementation still prompts, the read
    blocks on EOF and the relations are NOT archived. The contract is
    no-prompt + take-all + footer (M14 — B1).

    RED reason: today `--cascade` calls `_cascade_archive`, which prompts
    `[y/N]` on stderr and reads stdin (cli.py:3427-3428). With no stdin,
    `readline()` returns '' → declines → `sub/alpha.md` / `beta.md` are
    left in place, and the stderr carries the `[y/N]` prompt. Step 2
    replaces the prompt with the non-interactive take-all + footer.
    """
    root = _two_relation_tree(tmp_path)
    # (intentionally no stdin_text — a prompting impl would stall/decline)
    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        "--cascade",
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    dated = root / "archive" / "2026-05-28"
    # The primary and BOTH cascade relations were archived.
    assert (dated / "root.md").is_file()
    assert (dated / "alpha.md").is_file(), "pairs-with relation not cascaded"
    assert (dated / "beta.md").is_file(), "child-of relation not cascaded"
    # The non-cascade `references` relation is left in place.
    assert (root / "gamma.md").is_file(), "references is not a cascade verb"
    # No interactive prompt was emitted.
    assert "[y/N]" not in proc.stderr, "bare --cascade must not prompt"
    # A loud footer names the cascaded set.
    assert "cascade" in proc.stderr.lower()
    assert "alpha.md" in proc.stderr and "beta.md" in proc.stderr


def test_archive_cascade_dry_run_previews_and_writes_nothing(docs_script, tmp_path):
    """`--cascade-dry-run` previews the cascade set on stderr and writes
    nothing (exit 0) — the primary doc is NOT archived either.

    RED reason: `--cascade-dry-run` is not yet a recognised flag (argparse
    rejects it with exit 2). Step 2 adds it as a preview of the whole
    cascade operation.
    """
    root = _two_relation_tree(tmp_path)
    before = {p.name: p.read_text() for p in root.glob("*.md")}
    before["alpha.md"] = (root / "sub" / "alpha.md").read_text()

    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        "--cascade-dry-run",
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # Nothing moved — no archive dir, every doc still in place + unchanged.
    assert not (root / "archive").exists(), "--cascade-dry-run must write nothing"
    assert (root / "root.md").read_text() == before["root.md"]
    assert (root / "sub" / "alpha.md").read_text() == before["alpha.md"]
    assert (root / "beta.md").read_text() == before["beta.md"]
    # The preview names the would-be cascade set.
    assert "alpha.md" in proc.stderr and "beta.md" in proc.stderr


def test_archive_cascade_only_filters_by_glob(docs_script, tmp_path):
    """`--cascade-only GLOB` archives only the subset of one-hop relations
    whose root-relative POSIX target path matches GLOB; the primary is
    always archived; non-matching relations stay in place.

    RED reason: `--cascade-only` is not yet a recognised flag (argparse
    rejects it with exit 2). Step 2 adds it with the
    `compile_exclude_predicate`-style glob matcher.
    """
    root = _two_relation_tree(tmp_path)
    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        "--cascade-only",
        "sub/**",
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    dated = root / "archive" / "2026-05-28"
    # The primary is archived...
    assert (dated / "root.md").is_file()
    # ...and the glob-matching relation (sub/alpha.md)...
    assert (dated / "alpha.md").is_file(), "sub/** should cascade sub/alpha.md"
    # ...but NOT the non-matching relation (beta.md at root).
    assert (root / "beta.md").is_file(), "beta.md is outside sub/** — must stay in place"
    assert not (dated / "beta.md").exists()
    assert "[y/N]" not in proc.stderr, "--cascade-only must not prompt"


def test_archive_cascade_dry_run_rejects_interactive(docs_script, tmp_path):
    """`--cascade-dry-run --interactive` is an incoherent combination and is
    rejected by argparse (exit 2) — a dry-run that prompts makes no sense.

    RED reason: neither flag is recognised yet (argparse rejects on the
    first unknown flag, also exit 2 — so this test is GREEN-by-accident
    today on the exit code). It is pinned so Step 2's argparse
    mutually-exclusive group is exercised; the assertion on the
    *combination* message tightens once both flags exist. We assert exit 2
    AND that nothing was written.
    """
    root = _two_relation_tree(tmp_path)
    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        "--cascade-dry-run",
        "--interactive",
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert not (root / "archive").exists()


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
    # cli.md's M12 exit-code matrix pins exit 1 for "referring doc has
    # malformed metadata (move aborts)". Matches the existing
    # _cmd_archive MetadataError -> return 1 branch (cli.py:3346).
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    # The original core.md was NOT moved.
    assert (root / "core.md").is_file()
    assert (root / "core.md").read_text() == before_core
    # The archive destination was NOT created.
    assert not (root / "archive" / "2026-05-28").exists()


def test_archive_referring_edge_rewrite_refreshes_index_once(docs_script, fixtures_dir, tmp_path):
    """Pre-build INDEX.md; archive a doc with referring edges; verify the
    INDEX file's mtime advances and that a follow-up `docs index` is a
    no-op (byte-identity idempotency) — proves the archive verb refreshed
    INDEX once, correctly, at end-of-batch (not per referring-doc rewrite
    nor missing the refresh)."""
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

    # Byte-identity idempotency check: a follow-up `docs index` must be a
    # no-op if the archive refreshed INDEX correctly at end-of-batch.
    index_after_archive = index.read_bytes()
    noop = _run(docs_script, "index", "--root", str(root))
    assert noop.returncode == 0, noop.stderr
    assert index.read_bytes() == index_after_archive, (
        "INDEX changed on a follow-up `docs index` — the archive did not "
        "leave INDEX in a fully-refreshed state."
    )


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


# --- M14 A6 — archive end-of-batch reindex honours [exclude] ---------------


def _archive_excluded_malformed_tree(tmp_path: Path) -> tuple[Path, Path]:
    """Build a docs root with `[exclude] dirs = ["vendor"]`, a conformant
    doc to archive, and a malformed `vendor/README.md`.

    Returns (root, target). The malformed vendor file must NOT fail the
    archive's pre-flight validation walk nor the end-of-batch reindex,
    because it is excluded.
    """
    root = tmp_path / "arch-excl"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "arch-excl"\n\n[archive]\ndir = "archive"\n\n'
        '[exclude]\ndirs = ["vendor"]\n'
    )
    target = root / "doomed.md"
    target.write_text(
        "# Doomed\n\nLifecycle: active\nRole: notes\nProject: arch-excl\n"
        "Updated: 2026-01-01\n\n## Body\n\nA doc destined for the archive.\n"
    )
    vendor = root / "vendor"
    vendor.mkdir()
    (vendor / "README.md").write_text("no metadata\n# H1\n")
    return root, target


def test_archive_with_malformed_excluded_file_succeeds_and_reindexes(docs_script, tmp_path):
    """`docs archive` over a tree whose `[exclude]` set holds a malformed
    file must archive the target AND refresh the INDEX cleanly (exit 0).

    RED reason: `_cmd_archive` runs its pre-flight validation walk
    (`list(walk(root, config))`, cli.py:3489) and its end-of-batch
    `_refresh_index(root, config)` (cli.py:3518) with NO predicate, so the
    excluded malformed `vendor/README.md` makes the pre-flight walk raise
    → exit 1. Step 2 threads `compile_exclude_predicate(config, [])` into
    both the pre-flight walk and the reindex.
    """
    root, target = _archive_excluded_malformed_tree(tmp_path)
    vendor_readme = root / "vendor" / "README.md"
    vendor_before = vendor_readme.read_text()

    proc = _run(docs_script, "archive", str(target), "--date", "2026-05-28")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The target was archived.
    assert (root / "archive" / "2026-05-28" / "doomed.md").is_file()
    assert not target.exists()
    # The excluded malformed file is byte-unchanged and not in the INDEX.
    assert vendor_readme.read_text() == vendor_before
    index = (root / "INDEX.md").read_text()
    assert "vendor/README.md" not in index, "the excluded file must not appear in INDEX"


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
