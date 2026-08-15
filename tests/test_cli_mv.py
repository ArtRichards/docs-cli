"""CLI end-to-end tests for `docs mv` (Phase 2 — written RED)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def _run(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


def _crossrefs_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    """Copy the cross-refs fixture tree into tmp_path; return its root."""
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "cross-refs", root)
    return root


def test_mv_help(docs_script):
    proc = _run(docs_script, "mv", "--help")
    assert proc.returncode == 0
    assert "old" in proc.stdout.lower()
    assert "new" in proc.stdout.lower()


def test_mv_renames_in_place(docs_script, fixtures_dir, tmp_path):
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "mv", str(root / "core.md"), str(root / "core-engine.md"))
    assert proc.returncode == 0, proc.stderr
    assert (root / "core-engine.md").is_file()
    assert not (root / "core.md").exists()


def test_mv_into_a_subdirectory(docs_script, fixtures_dir, tmp_path):
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "mv", str(root / "core.md"), str(root / "sub" / "core.md"))
    assert proc.returncode == 0, proc.stderr
    assert (root / "sub" / "core.md").is_file()
    assert not (root / "core.md").exists()


def test_mv_rewrites_related_refs_across_the_tree(docs_script, fixtures_dir, tmp_path):
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "mv", str(root / "core.md"), str(root / "core-engine.md"))
    assert proc.returncode == 0, proc.stderr
    helper = (root / "helper.md").read_text()
    overview = (root / "overview.md").read_text()
    assert "pairs-with: core-engine.md" in helper
    assert "references: core-engine.md" in overview
    assert "pairs-with: core.md" not in helper
    assert "references: core.md" not in overview


def test_mv_collision_exits_1(docs_script, fixtures_dir, tmp_path):
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "mv", str(root / "core.md"), str(root / "helper.md"))
    assert proc.returncode == 1
    assert "exist" in proc.stderr.lower()


def test_mv_regenerates_index(docs_script, fixtures_dir, tmp_path):
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "mv", str(root / "core.md"), str(root / "core-engine.md"))
    assert proc.returncode == 0, proc.stderr
    assert (root / "INDEX.md").is_file()


def test_mv_dry_run_makes_no_change(docs_script, fixtures_dir, tmp_path):
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "mv", str(root / "core.md"), str(root / "core-engine.md"), "--dry-run")
    assert proc.returncode == 0, proc.stderr
    assert (root / "core.md").is_file()
    assert not (root / "core-engine.md").exists()
    assert "pairs-with: core.md" in (root / "helper.md").read_text()


# --- M14 A1 — mv is all-or-nothing (validate-all-first pre-flight) ----------


def _mv_malformed_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    """Copy the mv-with-malformed fixture tree into tmp_path; return its root.

    The tree carries `good-a.md` (the mv source), `referrer.md`
    (`pairs-with: good-a.md`), and `broken.md` (no H1 → `walk()` raises
    `MetadataError`). `docs mv good-a.md good-b.md` must abort BEFORE the
    move because the post-move rewrite walk would raise on `broken.md`.
    """
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "mv-with-malformed", root)
    return root


def test_mv_malformed_sibling_aborts_atomically(docs_script, fixtures_dir, tmp_path):
    """A malformed sibling must abort `docs mv` with exit 2, leaving the
    source in place, the destination absent, and the referrer byte-identical.

    RED reason: `_cmd_mv` does `old_path.replace(new_path)` (cli.py:3558)
    BEFORE the rewrite walk (cli.py:3560) that raises on `broken.md`. So
    today the source is already moved when the walk fails — the move is
    NOT all-or-nothing. Step 2 ports the archive validate-all-first
    pre-flight walk ahead of the move.
    """
    root = _mv_malformed_tree(fixtures_dir, tmp_path)
    source = root / "good-a.md"
    dest = root / "good-b.md"
    referrer = root / "referrer.md"
    source_before = source.read_text()
    referrer_before = referrer.read_text()

    proc = _run(docs_script, "mv", str(source), str(dest))

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    # The source is still at its old path, byte-identical.
    assert source.is_file(), "mv must not move the source when a sibling is malformed"
    assert source.read_text() == source_before
    # The destination was never created.
    assert not dest.exists(), "mv must not create the destination on an aborted move"
    # The referrer's Related: edge is untouched.
    assert referrer.read_text() == referrer_before
    assert "pairs-with: good-a.md" in referrer.read_text()


def test_mv_malformed_sibling_does_not_dangle_referring_edge(docs_script, fixtures_dir, tmp_path):
    """An aborted `docs mv` must not leave a dangling referring edge or a
    stray INDEX.

    The milestone's stated A1 harm is "dangling edges + INDEX never
    refreshed": today the move happens, then the rewrite walk raises on
    `broken.md` BEFORE rewriting `referrer.md`, so the referrer's
    `pairs-with: good-a.md` edge is left pointing at a path that no longer
    exists (good-a.md was moved to good-b.md). After the Step-2 pre-flight
    walk the abort precedes the move, so the edge still resolves.

    RED reason: today good-a.md is moved away, so the referrer's
    `pairs-with: good-a.md` target no longer exists on disk → the edge
    dangles. (No INDEX is pre-built: a non-excluded malformed sibling
    makes `docs index` itself fail, so this test pins the resolvability of
    the edge target instead of INDEX byte-identity.)
    """
    root = _mv_malformed_tree(fixtures_dir, tmp_path)
    index = root / "INDEX.md"
    assert not index.exists()  # no INDEX exists before the call

    proc = _run(docs_script, "mv", str(root / "good-a.md"), str(root / "good-b.md"))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)

    referrer_text = (root / "referrer.md").read_text()
    assert "pairs-with: good-a.md" in referrer_text, "referrer edge must be unchanged"
    # The edge must not dangle: its target (good-a.md) must still exist.
    assert (root / "good-a.md").is_file(), (
        "an aborted mv must leave the referring edge's target in place (no dangling edge)"
    )
    # The aborted mv must not have written a stray INDEX.
    assert not index.exists(), "an aborted mv must not create/refresh INDEX"


# --- M14 A4 — uncaught OSError mid-rewrite → clean exit 2 -------------------


def _readonly_referrer_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Build a docs root where the referrer lives in a read-only subdir.

    Returns (root, source, locked_dir). `source.md` (at root) is the mv
    target; `locked/referrer.md` carries `pairs-with: source.md`, so the
    rewrite walk tries to `atomic_write` it — which raises `OSError`
    (PermissionError) when the `.docs-tmp` tmpfile cannot be created in
    the `0o555` `locked/` directory. (A bare `chmod 0o444` on the file is
    NOT a reliable trigger: POSIX `rename()` onto a read-only target
    succeeds when the directory is writable; a read-only *directory* is
    the portable trigger.) The contract under test is observable: exit 2
    + no Traceback. Phase 6 may adjust the trigger for portability.
    """
    root = tmp_path / "ro"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "ro"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: ro\n"
    source = root / "source.md"
    source.write_text(f"# Source\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\nThe mv source.\n")
    locked = root / "locked"
    locked.mkdir()
    (locked / "referrer.md").write_text(
        f"# Referrer\n\n{hdr}Updated: 2026-01-02\n\n"
        "Related:\n- pairs-with: source.md\n\n## Body\n\nReferences the source.\n"
    )
    # Read-only directory: walk can still read referrer.md, but the
    # atomic_write tmpfile creation during the rewrite raises OSError.
    os.chmod(locked, 0o555)
    return root, source, locked


@pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="root bypasses 0o555 directory write protection; the OSError trigger does not fire",
)
def test_mv_oserror_mid_rewrite_exits_2(docs_script, tmp_path):
    """An OSError raised mid-rewrite must surface as a clean exit 2 with no
    Traceback on stderr (the observable contract; RQ#9).

    RED reason: the `_cmd_mv` rewrite loop (cli.py:3560-3567) catches only
    `(MetadataError, VocabularyError)`; an `OSError` from `atomic_write`
    against a referrer in a read-only directory escapes as an uncaught
    traceback after the move. Step 2 widens the except to map `OSError`
    → exit 2.
    """
    root, source, locked = _readonly_referrer_tree(tmp_path)
    try:
        proc = _run(docs_script, "mv", str(source), str(root / "renamed.md"))
        assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
        assert "Traceback" not in proc.stderr, (
            "an OSError mid-rewrite must be mapped to a clean exit 2, not a "
            f"traceback:\n{proc.stderr}"
        )
    finally:
        os.chmod(locked, 0o755)  # restore so tmp_path teardown can clean up


# --- M14 A6 — mv end-of-batch reindex honours [exclude] --------------------


def _mv_excluded_malformed_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Build a docs root with an `[exclude] dirs = ["vendor"]` and a
    malformed `vendor/README.md`, plus two conformant docs to mv between.

    Returns (root, source, dest_path). The malformed vendor file must NOT
    fail the post-move reindex because it is excluded.
    """
    root = tmp_path / "mv-excl"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "mv-excl"\n\n[archive]\ndir = "archive"\n\n'
        '[exclude]\ndirs = ["vendor"]\n'
    )
    hdr = "Lifecycle: active\nRole: notes\nProject: mv-excl\n"
    source = root / "source.md"
    source.write_text(f"# Source\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\nThe mv source.\n")
    (root / "other.md").write_text(
        f"# Other\n\n{hdr}Updated: 2026-01-02\n\n## Body\n\nA second conformant doc.\n"
    )
    vendor = root / "vendor"
    vendor.mkdir()
    # Malformed: no H1, then an H1 — parse() raises MetadataError on it.
    (vendor / "README.md").write_text("no metadata\n# H1\n")
    return root, source, root / "dest.md"


def test_mv_excluded_malformed_file_reindexes(docs_script, tmp_path):
    """`docs mv` over a tree whose `[exclude]` set holds a malformed file
    must succeed (exit 0): the end-of-batch reindex skips the excluded
    file, the move lands, and the malformed file is byte-unchanged.

    RED reason: `_cmd_mv` calls `_refresh_index(root, config)` with NO
    predicate (cli.py:3567), so the post-move walk reads the excluded
    malformed `vendor/README.md` and raises → exit 2. Step 2 threads
    `compile_exclude_predicate(config, [])` into the reindex.
    """
    root, source, dest = _mv_excluded_malformed_tree(tmp_path)
    vendor_readme = root / "vendor" / "README.md"
    vendor_before = vendor_readme.read_text()

    proc = _run(docs_script, "mv", str(source), str(dest))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The move landed.
    assert dest.is_file()
    assert not source.exists()
    # The excluded malformed file is byte-unchanged and not in the INDEX.
    assert vendor_readme.read_text() == vendor_before
    index = (root / "INDEX.md").read_text()
    assert "vendor/README.md" not in index, "the excluded file must not appear in INDEX"
    # The conformant doc IS indexed — pins a FULL walk (excluding only
    # vendor/), not a fix that swallows the walk error and drops docs.
    assert "other.md" in index, "the conformant doc must still be indexed"


# --- M18 — mv own-edge parity (D3, operator Q1=INCLUDE) --------------------


def _self_edge_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Build a docs root with a single doc that carries a self-referential
    `Related:` edge (`references: <itself>`), plus an archive dir to move
    it into.

    Returns (root, source, dest). The self-edge is the only own-edge a
    single-doc move can touch (a single `mv` relocates exactly one doc, so
    the only "moved-doc target that moved" is the doc itself).
    """
    root = tmp_path / "mv-self"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "mv-self"\n\n[archive]\ndir = "archive"\n')
    source = root / "feature.md"
    source.write_text(
        "# Feature\n\n"
        "Lifecycle: active\nRole: notes\nProject: mv-self\nUpdated: 2026-01-01\n\n"
        "Related:\n- references: feature.md\n\n"
        "## Body\n\n"
        "A doc whose Related: edge points at itself; moving it must repoint "
        "that own edge via the shared rewrite_related_refs walker.\n"
    )
    dest = root / "archive" / "2026-05-28" / "feature.md"
    return root, source, dest


def test_mv_rewrites_moved_docs_own_archive_edge(docs_script, tmp_path):
    """`docs mv` repoints the MOVED doc's OWN `Related:` bullet when its
    target is the doc being moved — the D3 own-edge contract (operator
    Q1=INCLUDE), via the shared `rewrite_related_refs` walker. Moving a doc
    with a self-referential `references: feature.md` edge into the archive
    leaves that edge repointed to `archive/<date>/feature.md`, not dangling.

    Classification: GREEN at the Phase-4 baseline — a regression LOCK, not a
    behaviour RED. `_cmd_mv` already walks the WHOLE tree post-move and
    applies `rewrite_related_refs(text, old_rel, new_rel)` to every doc
    INCLUDING the moved doc at its new path (cli.py:3856-3860), so a
    single-move own-edge (only ever the self-edge, since exactly one doc
    moves) is already repointed. Unlike archive's D1, mv has no `--cascade`,
    so there is no multi-move own-edge gap to fix; this test pins that the
    D3 contract holds and stays held through Phase 6 (no mv code change
    expected — SURFACED to the operator as a scope finding).
    """
    root, source, dest = _self_edge_tree(tmp_path)
    proc = _run(docs_script, "mv", str(source), str(dest))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert dest.is_file()
    after = dest.read_text()
    assert "references: archive/2026-05-28/feature.md" in after, after
    assert "references: feature.md\n" not in after, after


# --- M25 — reciprocity survives `docs mv` (GREEN at baseline) --------------


def _reciprocal_tree(tmp_path: Path, name: str) -> Path:
    """A complete `precedes`/`follows` pair in a managed root."""
    root = tmp_path / name
    root.mkdir()
    (root / ".docs.toml").write_text(f'[project]\nname = "{name}"\n')
    (root / "a.md").write_text(
        f"# A\n\nLifecycle: active\nRole: notes\nProject: {name}\nUpdated: 2026-05-20\n"
        "\nRelated:\n- precedes: b.md\n\n## Body\n\nProse.\n"
    )
    (root / "b.md").write_text(
        f"# B\n\nLifecycle: active\nRole: notes\nProject: {name}\nUpdated: 2026-05-20\n"
        "\nRelated:\n- follows: a.md\n\n## Body\n\nProse.\n"
    )
    return root


def test_mv_preserves_reciprocal_pair(docs_script, tmp_path):
    """M25 lock: `mv` rewrites BOTH halves of a recognized pair, so the tree
    stays reciprocity-clean after a move.

    GREEN at baseline — `_cmd_mv` already rewrites every referring edge
    tree-wide. It must STAY green once M25's hard `missing-inverse` rule
    lands: a move that repointed only one half would start failing
    `docs check`.
    """
    root = _reciprocal_tree(tmp_path, "mvrecip")
    proc = _run(docs_script, "mv", str(root / "b.md"), str(root / "sub" / "b.md"))
    assert proc.returncode == 0, proc.stderr

    assert "- precedes: sub/b.md" in (root / "a.md").read_text()
    assert "- follows: a.md" in (root / "sub" / "b.md").read_text()

    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


_SKIP_AS_ROOT_MV = pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="root bypasses 0o444 write protection; the unwritable trigger does not fire",
)


# --- M28 — move-safe body-link rewrites ------------------------------------
#
# The contract under test is the milestone's *Decisions (Phase 1 — BINDING)*
# and `cli.md` › *Move-safe body-link rewrites (M28 — D1–D7)* / *`docs mv`*.
# Every subprocess test below asserts a frozen contract string as well as an
# exit code, so an unrelated failure with the same code cannot satisfy it
# (M26's falsely-GREEN lesson).


def _movelink_tree(fixtures_dir: Path, tmp_path: Path, name: str) -> Path:
    """Copy a `movelink-*` fixture tree into tmp_path; return its root.

    Asserts the SOURCE tree exists, so between Phase 2 and Phase 3 these tests
    are honestly RED on a missing fixture rather than vacuously green on an
    empty copy (M27's Phase-2 catch).
    """
    source = fixtures_dir / "trees" / name
    assert source.is_dir(), f"Phase 3 must author the `{name}` fixture tree"
    root = tmp_path / "tree"
    shutil.copytree(source, root)
    return root


def _snapshot(root: Path) -> dict[str, bytes]:
    """Every file under `root`, by root-relative POSIX path."""
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def test_mv_dry_run_names_every_planned_rewrite(docs_script, fixtures_dir, tmp_path):
    """D7/Q3: `--dry-run` is a real preview — every planned destination
    rewrite, with document, line, old spelling and new spelling — instead of
    today's single `would move` line.

    Line numbers are part of the `movelink-incoming` fixture contract: the
    destination tokens live at `note.md:13` and `sub/deep.md:10`.

    RED reason: `_cmd_mv` returns at its `args.dry_run` branch before it walks
    anything, so it prints one line and knows of no rewrites (Phase 6).
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-incoming")
    proc = _run(docs_script, "mv", "plan.md", "milestone-plan.md", "--dry-run", cwd=root)

    assert proc.returncode == 0, proc.stderr
    assert "docs: mv: would move plan.md -> milestone-plan.md" in proc.stderr
    assert "docs: mv: rewrite note.md:13 plan.md -> milestone-plan.md" in proc.stderr
    assert "docs: mv: rewrite sub/deep.md:10 ../plan.md -> ../milestone-plan.md" in proc.stderr
    assert "docs: mv: 2 destination(s) in 2 document(s), 1 Related: bullet(s)" in proc.stderr
    assert "docs: mv: preview only — nothing was written" in proc.stderr
    assert (root / "plan.md").is_file() and not (root / "milestone-plan.md").exists()


def test_mv_json_record_shape(docs_script, fixtures_dir, tmp_path):
    """D7: `docs mv --json` emits ONE record with the closed, ordered key set
    `cli.md` pins — and no `strands` key, because a rename produces no
    newly-archived set (R4).

    RED reason: the `mv` subparser has no `--json` flag at all (Phase 7).
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-incoming")
    proc = _run(docs_script, "mv", "plan.md", "milestone-plan.md", "--json", cwd=root)

    assert proc.returncode == 0, proc.stderr
    record = json.loads(proc.stdout)
    assert list(record) == ["old", "new", "rewrites", "dry_run", "applied", "index_refreshed"]
    assert record["old"] == {"source": "plan.md", "path": "plan.md"}
    assert record["new"] == {"source": "milestone-plan.md", "path": "milestone-plan.md"}
    assert record["dry_run"] is False
    assert record["applied"] is True
    assert record["index_refreshed"] is True

    assert [(r["path"], r["line"], r["old"], r["new"]) for r in record["rewrites"]] == [
        ("note.md", 13, "plan.md", "milestone-plan.md"),
        ("sub/deep.md", 10, "../plan.md", "../milestone-plan.md"),
    ]
    for rewrite in record["rewrites"]:
        assert list(rewrite) == ["path", "line", "column", "old", "new"]


def test_mv_preview_record_equals_apply_record(docs_script, fixtures_dir, tmp_path):
    """One schema shared by preview and apply, so the two are diffable — only
    the three mode flags differ (D7, M26 — D7's precedent).
    """
    preview_root = _movelink_tree(fixtures_dir, tmp_path / "a", "movelink-incoming")
    apply_root = _movelink_tree(fixtures_dir, tmp_path / "b", "movelink-incoming")

    preview = _run(
        docs_script, "mv", "plan.md", "milestone-plan.md", "--json", "--dry-run", cwd=preview_root
    )
    applied = _run(docs_script, "mv", "plan.md", "milestone-plan.md", "--json", cwd=apply_root)
    assert preview.returncode == 0, preview.stderr
    assert applied.returncode == 0, applied.stderr

    preview_record = json.loads(preview.stdout)
    apply_record = json.loads(applied.stdout)
    assert list(preview_record) == list(apply_record)
    assert preview_record["rewrites"] == apply_record["rewrites"]
    assert (preview_record["dry_run"], preview_record["applied"]) == (True, False)
    assert (apply_record["dry_run"], apply_record["applied"]) == (False, True)


def test_mv_rename_leaves_check_clean(docs_script, fixtures_dir, tmp_path):
    """E1, the headline defect: today a rename leaves a tree that fails the
    tool's own gate. Afterwards `docs check` must exit 0.
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-incoming")
    moved = _run(docs_script, "mv", "plan.md", "milestone-plan.md", cwd=root)
    assert moved.returncode == 0, moved.stderr

    checked = _run(docs_script, "check", str(root))
    assert checked.returncode == 0, checked.stdout + checked.stderr
    assert "broken-body-link" not in checked.stdout


def test_mv_rebases_the_moved_documents_own_links(docs_script, fixtures_dir, tmp_path):
    """Class 2: the destinations INSIDE the moved document are rebased from its
    new directory, in both directions at once.
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-moved-referrer")
    proc = _run(docs_script, "mv", "guide.md", "sub/guide.md", cwd=root)
    assert proc.returncode == 0, proc.stderr

    moved = (root / "sub" / "guide.md").read_text()
    assert "[the target](../target.md)" in moved
    assert "[the sub reference](ref.md)" in moved
    assert _run(docs_script, "check", str(root)).returncode == 0


def test_mv_into_a_subdirectory_rebases_both_directions(docs_script, fixtures_dir, tmp_path):
    """E4's nested path math: a document moved out of a deep subdirectory has
    its `../../` links flattened and its downward links deepened, and every
    incoming reference is repointed in the same operation.
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-nested")
    proc = _run(docs_script, "mv", "sub/deep/x.md", "x.md", cwd=root)
    assert proc.returncode == 0, proc.stderr

    moved = (root / "x.md").read_text()
    assert "[the root](root.md)" in moved
    assert "[the nested note](sub/deep/nested/y.md)" in moved
    assert "[again](root.md)" in moved
    assert _run(docs_script, "check", str(root)).returncode == 0


def test_mv_rewrites_an_archived_referrers_destination_and_nothing_else(
    docs_script, fixtures_dir, tmp_path
):
    """E5 / D5: the archived referrer's stale destination is repointed and
    NOTHING else in that document changes — `Lifecycle:`, `Archived-reason:`,
    `Updated:`, the H1, the prose, and every non-moving reference are
    byte-identical.
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-archived-referrer")
    archived = root / "archive" / "2026-01-01" / "old-log.md"
    before = archived.read_text()

    proc = _run(docs_script, "mv", "plan.md", "renamed-plan.md", cwd=root)
    assert proc.returncode == 0, proc.stderr

    after = archived.read_text()
    assert after != before, "the stale destination must be repaired at all"
    assert "[the plan](../../renamed-plan.md)" in after
    assert "../../plan.md" not in after
    assert "- references: renamed-plan.md" in after

    expected = before.replace("(../../plan.md)", "(../../renamed-plan.md)").replace(
        "- references: plan.md", "- references: renamed-plan.md"
    )
    assert after == expected, "only the moving destination and its bullet may change"
    assert _run(docs_script, "check", str(root)).returncode == 0


def test_mv_archived_referrer_gains_no_revision_bullet(docs_script, fixtures_dir, tmp_path):
    """The A2/Q2 lock, stated separately because it reverses the registered
    stub's own recommendation: M18's shape, not M25 — D4's. No `Revision:`
    group, and `Updated:` unmoved.

    The first assertion is what keeps this honest: without it the test is
    GREEN at baseline for the wrong reason — today no `Revision:` appears
    because no body-link write happens at all. It must observe the M28 write
    AND the absence of audit metadata in the same document.
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-archived-referrer")
    archived = root / "archive" / "2026-01-01" / "old-log.md"

    proc = _run(docs_script, "mv", "plan.md", "renamed-plan.md", cwd=root)
    assert proc.returncode == 0, proc.stderr

    after = archived.read_text()
    assert "[the plan](../../renamed-plan.md)" in after, (
        "the move-driven destination rewrite must have happened at all"
    )
    assert "Revision:" not in after
    assert "Updated: 2026-01-01" in after
    assert "Lifecycle: archived" in after
    assert "Archived-reason:" in after


def test_mv_leaves_plain_text_mentions_and_fenced_code_untouched(
    docs_script, fixtures_dir, tmp_path
):
    """ "Never rewrite prose": a bare filename in a sentence and link syntax
    inside a code span are not destinations and must survive byte-identical.
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-incoming")
    note = root / "note.md"
    before = note.read_text()
    assert "A bare plan.md" in before, "the fixture must carry a prose mention"
    assert "`[the plan](plan.md)`" in before, "the fixture must carry a code span"

    proc = _run(docs_script, "mv", "plan.md", "milestone-plan.md", cwd=root)
    assert proc.returncode == 0, proc.stderr

    after = note.read_text()
    assert "A bare plan.md" in after
    assert "`[the plan](plan.md)`" in after
    assert "[the plan](milestone-plan.md)" in after


@_SKIP_AS_ROOT_MV
def test_mv_refuses_before_the_move_when_a_planned_referrer_is_unwritable(
    docs_script, fixtures_dir, tmp_path
):
    """D4 extended to `mv`: a handled failure refuses the WHOLE operation with
    zero mutation — the source still at its old path, the destination absent,
    and the referrer byte-identical.

    RED reason: `_cmd_mv` moves first and rewrites afterwards, so today the
    source is already at its new path when the unwritable referrer is met, and
    the failure is an `OSError` mapped after the move (Phase 6 inverts it).
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-incoming")
    before = _snapshot(root)
    (root / "note.md").chmod(0o444)
    try:
        proc = _run(docs_script, "mv", "plan.md", "milestone-plan.md", cwd=root)
    finally:
        (root / "note.md").chmod(0o644)

    assert proc.returncode == 2
    assert "docs: mv: note.md is not writable; refusing before any write" in proc.stderr
    assert proc.stdout == ""
    assert _snapshot(root) == before, "a refusal writes zero bytes"


def test_mv_dry_run_on_a_malformed_tree_exits_2_and_changes_nothing(
    docs_script, fixtures_dir, tmp_path
):
    """Amendment 1: a preview adopts failures of plan CONSTRUCTION — it cannot
    describe what it cannot read — so `mv --dry-run` on a malformed tree now
    exits 2 with the same message its write path uses.

    RED reason: today `--dry-run` returns before the pre-flight walk and exits
    0 (cli.py's `args.dry_run` branch precedes the walk).
    """
    root = _mv_malformed_tree(fixtures_dir, tmp_path)
    before = _snapshot(root)
    proc = _run(docs_script, "mv", "good-a.md", "good-b.md", "--dry-run", cwd=root)

    assert proc.returncode == 2
    assert "broken.md" in proc.stderr
    assert "Traceback" not in proc.stderr
    assert _snapshot(root) == before


def test_mv_second_equivalent_move_changes_nothing(docs_script, fixtures_dir, tmp_path):
    """Idempotence: moving back and forth returns the tree to its exact bytes,
    because a destination whose meaning is unchanged keeps its spelling.

    `INDEX.md` is excluded from the comparison and asserted separately: the
    fixture ships without one, and the FIRST move generates it. Everything
    else must be byte-identical, `Updated:` values included — a move has never
    bumped them and M28 does not start.
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-incoming")
    before = {rel: raw for rel, raw in _snapshot(root).items() if rel != "INDEX.md"}

    assert _run(docs_script, "mv", "plan.md", "milestone-plan.md", cwd=root).returncode == 0
    once = (root / "note.md").read_text()
    assert "[the plan](milestone-plan.md)" in once, "the first move must actually rewrite"

    assert _run(docs_script, "mv", "milestone-plan.md", "plan.md", cwd=root).returncode == 0

    after = _snapshot(root)
    assert {rel: raw for rel, raw in after.items() if rel != "INDEX.md"} == before
    assert "INDEX.md" in after
