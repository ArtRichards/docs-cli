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
    # M28 — D7: `--json` is part of the frozen `docs mv` surface and `cli.md`
    # already advertises it, so the argparse half must land with it. Asserting
    # it here converts the Phase-7 follow-through from a promise into a lock —
    # RED until Phase 7, which is what a RED-baseline step is for.
    assert "--json" in proc.stdout, (
        "cli.md advertises `docs mv --json`; --help must agree (surface parity)"
    )


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
    before = _snapshot(root)
    proc = _run(docs_script, "mv", "plan.md", "milestone-plan.md", "--dry-run", cwd=root)

    assert proc.returncode == 0, proc.stderr
    assert "docs: mv: would move plan.md -> milestone-plan.md" in proc.stderr
    assert "docs: mv: rewrite note.md:13 plan.md -> milestone-plan.md" in proc.stderr
    assert "docs: mv: rewrite sub/deep.md:10 ../plan.md -> ../milestone-plan.md" in proc.stderr
    assert "docs: mv: 2 destination(s) in 2 document(s), 1 Related: bullet(s)" in proc.stderr
    assert "docs: mv: preview only — nothing was written" in proc.stderr
    assert (root / "plan.md").is_file() and not (root / "milestone-plan.md").exists()
    assert _snapshot(root) == before, (
        "a COMPLETING preview writes zero bytes — including no rewritten referrer "
        "and no stray INDEX; checking only the two move endpoints would admit a "
        "preview that applied the rewrite plan and then declined to rename"
    )


def test_mv_apply_names_every_rewrite_and_the_move(docs_script, fixtures_dir, tmp_path):
    """The apply path prints the SAME rewrite lines and footer as the preview,
    plus the `moved` line in place of `would move` — R3: everything prints
    unless `--quiet`, in preview and apply alike.

    Without this the frozen `docs: mv: moved …` line has no lock at all and a
    Phase-6 implementation could print anything on success.
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-incoming")
    proc = _run(docs_script, "mv", "plan.md", "milestone-plan.md", cwd=root)

    assert proc.returncode == 0, proc.stderr
    assert "docs: mv: moved plan.md -> milestone-plan.md" in proc.stderr
    assert "docs: mv: would move" not in proc.stderr
    assert "docs: mv: rewrite note.md:13 plan.md -> milestone-plan.md" in proc.stderr
    assert "docs: mv: rewrite sub/deep.md:10 ../plan.md -> ../milestone-plan.md" in proc.stderr
    assert "docs: mv: 2 destination(s) in 2 document(s), 1 Related: bullet(s)" in proc.stderr
    assert "preview only" not in proc.stderr


def test_mv_quiet_suppresses_every_line_but_prints_a_refusal(docs_script, fixtures_dir, tmp_path):
    """R3: `--quiet` governs the ordinary prose — the move line, every rewrite
    line and the footer — while a refusal still prints, as every refusal does.
    """
    quiet_root = _movelink_tree(fixtures_dir, tmp_path / "a", "movelink-incoming")
    proc = _run(docs_script, "mv", "plan.md", "milestone-plan.md", "--quiet", cwd=quiet_root)
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == "", f"--quiet must silence the whole apply summary, got {proc.stderr!r}"

    malformed = _mv_malformed_tree(fixtures_dir, tmp_path / "b")
    refused = _run(docs_script, "mv", "good-a.md", "good-b.md", "--quiet", cwd=malformed)
    assert refused.returncode == 2
    assert "broken.md" in refused.stderr, "a refusal prints even under --quiet"


@pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="root bypasses 0o555 directory write protection; the OSError trigger does not fire",
)
def test_mv_oserror_mid_execution_admits_the_partial_state(docs_script, tmp_path):
    """R9 / D4: the residual mid-execution `OSError` is admitted EXACTLY, in
    M26's partial-state shape extended by a `Rewritten:` clause — naming what
    moved, what was rewritten, and what was not written.

    This is the boundary M26 — D4 froze and M28 inherits: a `0o644` file inside
    a `0o555` directory passes the pre-flight's `os.access` test and must be
    admitted there, failing later as the residual admission. Exit 2 and the
    no-traceback guarantee are unchanged; only the message is upgraded.

    RED reason: `_cmd_mv` prints the bare `docs: mv: <OSError>` today (Phase 6).
    """
    root, source, locked = _readonly_referrer_tree(tmp_path)
    try:
        proc = _run(docs_script, "mv", str(source), str(root / "renamed.md"))
    finally:
        os.chmod(locked, 0o755)

    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
    assert "Traceback" not in proc.stderr
    assert "docs: mv: write failed for " in proc.stderr
    assert "PARTIAL MOVE — not rolled back." in proc.stderr
    assert "Moved: source.md -> renamed.md." in proc.stderr
    assert "Rewritten: none." in proc.stderr, (
        "an empty list renders as the literal word `none`, never as a blank "
        "(the M25 `_rollback_relate` lesson, M26's `_archive_partial_state` precedent)"
    )
    assert "Not written: locked/referrer.md." in proc.stderr
    assert "Repair manually." in proc.stderr
    assert proc.stdout == ""


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

    assert [
        (r["path"], r["line"], r["column"], r["old"], r["new"]) for r in record["rewrites"]
    ] == [
        ("note.md", 13, 16, "plan.md", "milestone-plan.md"),
        ("sub/deep.md", 10, 59, "../plan.md", "../milestone-plan.md"),
    ], (
        "`column` is 1-based, of the destination TOKEN's first character — "
        "not the `[`, and not a byte offset"
    )
    for rewrite in record["rewrites"]:
        assert list(rewrite) == ["path", "line", "column", "old", "new"]


def test_mv_json_source_is_the_argument_exactly_as_typed(docs_script, fixtures_dir, tmp_path):
    """K: `source` is the argument as typed and `path` is canonical. Invoked as
    a bare `plan.md` the two coincide, so the distinction needs a spelling that
    separates them.
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-incoming")
    proc = _run(docs_script, "mv", "./plan.md", "./milestone-plan.md", "--json", cwd=root)

    assert proc.returncode == 0, proc.stderr
    record = json.loads(proc.stdout)
    assert record["old"] == {"source": "./plan.md", "path": "plan.md"}
    assert record["new"] == {"source": "./milestone-plan.md", "path": "milestone-plan.md"}


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
    assert len(preview_record["rewrites"]) == 2, (
        "equality of two EMPTY arrays would satisfy this test vacuously"
    )
    assert preview_record["rewrites"] == apply_record["rewrites"]
    assert (preview_record["dry_run"], preview_record["applied"]) == (True, False)
    assert (apply_record["dry_run"], apply_record["applied"]) == (False, True)


def _mv_readonly_root_tree(tmp_path: Path) -> Path:
    """A tree whose docs are writable but whose ROOT is not.

    `_readonly_root_tree`'s shape from `tests/test_cli_archive.py`, applied to
    `mv`: both documents live in `w/`, so the rename and every planned rewrite
    land, and then the end-of-move `atomic_write(root / "INDEX.md", …)` fails
    because its `.docs-tmp` sibling cannot be created in the read-only root.
    """
    root = tmp_path / "roroot"
    (root / "w").mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "roroot"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: roroot\n"
    (root / "w" / "a.md").write_text(f"# A\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\na.\n")
    (root / "w" / "b.md").write_text(
        f"# B\n\n{hdr}Updated: 2026-01-02\n\nRelated:\n- pairs-with: w/a.md\n\n"
        "## Body\n\nSee [a](a.md).\n"
    )
    root.chmod(0o555)
    return root


@_SKIP_AS_ROOT_MV
def test_mv_json_record_is_emitted_on_an_index_refresh_failure(docs_script, tmp_path):
    """The ONE documented exception to "no record on a refusal", now on `mv`
    too — the two verbs share one schema, so they must share this rule or
    `index_refreshed`'s documented `false` value is unobservable on `mv`.

    An INDEX-refresh failure is a **post-write** failure: the move and every
    rewrite already landed, so the record IS emitted with `"applied": true,
    "index_refreshed": false` and the run exits 2. Without this lock the
    natural reading of "no record on a refusal" — suppress it on every
    non-zero exit — passes the whole suite, and 1.x's bare `docs: mv: <err>`
    would look correct too.
    """
    root = _mv_readonly_root_tree(tmp_path)
    try:
        proc = _run(docs_script, "mv", str(root / "w" / "a.md"), str(root / "w" / "c.md"), "--json")

        assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
        assert "Traceback" not in proc.stderr
        assert "docs: INDEX refresh failed: " in proc.stderr, proc.stderr
        record = json.loads(proc.stdout)
        assert record["applied"] is True, "the move really did land"
        assert record["index_refreshed"] is False
        assert record["dry_run"] is False
        # …and the disk agrees with the record.
        assert (root / "w" / "c.md").is_file()
        assert not (root / "w" / "a.md").exists()
        assert "[a](c.md)" in (root / "w" / "b.md").read_text()
        assert not (root / "INDEX.md").exists()
    finally:
        root.chmod(0o755)


@_SKIP_AS_ROOT_MV
def test_mv_failed_rename_leaves_no_directory_behind(docs_script, tmp_path):
    """A partial-state admission that says nothing was moved must be TRUE.

    `mkdir(parents=True)` runs before `replace`, so a `replace` that raises
    would otherwise leave an empty destination directory behind — and the
    admission would read `Moved: none. Rewritten: none. Not written: none.`
    over a tree the call had in fact changed. `_archive_partial_state` prunes
    its dated directory for exactly this reason; `mv` has the same failure
    shape, and now the same care.

    The trigger is a read-only SOURCE directory: the root stays writable so
    the `mkdir` succeeds, and only the rename fails.
    """
    root = tmp_path / "prune"
    (root / "w").mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "prune"\n')
    (root / "w" / "a.md").write_text(
        "# A\n\nLifecycle: active\nRole: notes\nProject: prune\n"
        "Updated: 2026-01-01\n\n## Body\n\nNo links at all.\n"
    )
    os.chmod(root / "w", 0o555)
    try:
        proc = _run(docs_script, "mv", str(root / "w" / "a.md"), str(root / "sub" / "a.md"))
    finally:
        os.chmod(root / "w", 0o755)

    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
    assert "Traceback" not in proc.stderr
    assert "PARTIAL MOVE — not rolled back. Moved: none." in proc.stderr, proc.stderr
    assert not (root / "sub").exists(), (
        "an admission that names nothing moved must leave nothing behind — the "
        f"directory the failed move created is still there: {proc.stderr!r}"
    )
    assert (root / "w" / "a.md").is_file(), "the source is untouched"


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
    proc = _run(docs_script, "mv", "sub/deep/x.md", "x.md", "--json", cwd=root)
    assert proc.returncode == 0, proc.stderr

    reported = {(r["line"], r["column"], r["old"]) for r in json.loads(proc.stdout)["rewrites"]}
    assert (11, 32, "../../sub/../root.md") in reported, (
        "`old` is `link.raw` — the token EXACTLY as written. Every other fixture "
        "spells its target canonically, so only this one distinguishes carrying "
        "M27's record verbatim from re-deriving the spelling ((K), (L))"
    )

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


def test_mv_of_an_archived_document_rebases_its_own_destinations(
    docs_script, fixtures_dir, tmp_path
):
    """Item (G)'s last sentence: an archived document that is ITSELF moved by
    `docs mv` gets class-2 rebasing of its own destinations, under the same
    move-driven licence.

    Without this lock an implementation that gates class-2 rebasing on
    `not doc.archived` — a very plausible reading of M3's "the archive subtree
    is read-only" — passes every other M28 test, because the only archived
    document in the corpus is exercised as a class-1 REFERRER.

    `docs check` is deliberately not asserted afterwards: the destination is
    outside the archive subtree, so `Lifecycle: archived` there is a
    `status-drift` finding this move is not responsible for.
    """
    root = _movelink_tree(fixtures_dir, tmp_path, "movelink-archived-referrer")
    proc = _run(docs_script, "mv", "archive/2026-01-01/old-log.md", "old-log.md", cwd=root)
    assert proc.returncode == 0, proc.stderr

    moved = (root / "old-log.md").read_text()
    assert "[the plan](plan.md)" in moved
    assert "[the keeper](keep.md)" in moved
    assert "../../" not in moved, "every `../../` must have been flattened by the rebase"
    assert "A bare plan.md mention" in moved, "prose is still untouched"


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
        # `--json` is deliberate: `cli.md` freezes "no `--json` record on a
        # refusal" for BOTH verbs, and without the flag an implementation that
        # emitted one would still satisfy the empty-stdout assertion below.
        proc = _run(docs_script, "mv", "plan.md", "milestone-plan.md", "--json", cwd=root)
    finally:
        (root / "note.md").chmod(0o644)

    assert proc.returncode == 2
    assert "docs: mv: note.md is not writable; refusing before any write" in proc.stderr
    assert proc.stdout == "", "no --json record on a refusal (M26's frozen rule, D7 for mv)"
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


# ===========================================================================
# M28a — Leg 2: `docs mv` refuses a cross-dated archived relocation.
#
# The contract under test is the milestone's *Decisions (Phase 1 — BINDING)*
# items (E) and (F), and `cli.md` › `docs mv` ›
# *Cross-dated archived relocations*. Every test below asserts a frozen
# contract string as well as an exit code.
# ===========================================================================

_M28A_REFUSAL = (
    "docs: mv: archive/2026-01-01/{name} -> archive/2026-03-04/{name} "
    "crosses dated archive directories (2026-01-01 to 2026-03-04); "
    "refusing before any write"
)
_M28A_ESCAPE = (
    "docs: mv: the dated directory records when a document was archived; to "
    "correct a genuinely mis-dated archive, move the file by hand, correct its "
    "`Archived:` line, and re-run `docs check`"
)


def _archivedate_tree(fixtures_dir: Path, tmp_path: Path, name: str) -> Path:
    """Copy an `archivedate-*` fixture tree into tmp_path; return its root.

    Asserts the SOURCE tree exists, so between Phase 2 and Phase 3 these tests
    are honestly RED on a missing fixture rather than vacuously green on an
    empty copy.
    """
    source = fixtures_dir / "trees" / name
    assert source.is_dir(), f"Phase 3 must author the `{name}` fixture tree"
    root = tmp_path / "tree"
    shutil.copytree(source, root)
    return root


def _check_pairs(docs_script: Path, root: Path) -> tuple[int, list[tuple[str, str]]]:
    """`docs check --json` over `root` as `(exit_code, [(path, rule), …])`.

    Every intended-exit-0 assertion below goes through this rather than a bare
    `returncode == 0`, so it asserts the absence of a NAMED finding on a NAMED
    document instead of whole-tree silence.
    """
    proc = _run(docs_script, "check", str(root), "--json")
    records = json.loads(proc.stdout) if proc.stdout.strip() else []
    return proc.returncode, [(r["path"], r["rule"]) for r in records]


def _cross_dated(docs_script: Path, fixtures_dir: Path, tmp_path: Path, name: str, *extra: str):
    """Attempt the E1d relocation of `name` between the two dated directories.

    Returns `(root, snapshot_before, completed_process)` so every caller can
    assert the zero-bytes guarantee as well as the exit code.
    """
    root = _archivedate_tree(fixtures_dir, tmp_path, "archivedate-two-dated-dirs")
    before = _snapshot(root)
    proc = _run(
        docs_script,
        "mv",
        f"archive/2026-01-01/{name}",
        f"archive/2026-03-04/{name}",
        *extra,
        cwd=root,
    )
    return root, before, proc


def test_mv_refuses_a_cross_dated_relocation_of_a_witness_carrying_document(
    docs_script, fixtures_dir, tmp_path
):
    """E1d, prevented. The exact relocation that completes at exit 0 today,
    rewrites every stale reference so nothing dangles, and leaves `docs check`
    clean — the one silent path in the tool's own surface.

    Both frozen lines, exit 2, ZERO bytes written, and no `--json` record.
    `--json` is deliberate: without the flag an implementation that emitted a
    record would still satisfy the empty-stdout assertion.
    """
    root, before, proc = _cross_dated(
        docs_script, fixtures_dir, tmp_path, "with-witness.md", "--json"
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert _M28A_REFUSAL.format(name="with-witness.md") in proc.stderr
    assert _M28A_ESCAPE in proc.stderr, "the escape ships in the same breath as the refusal"
    assert proc.stdout == "", "no --json record on a refusal (M26's frozen rule)"
    assert _snapshot(root) == before, "a refusal writes zero bytes"


def test_mv_refuses_the_same_relocation_without_the_witness(docs_script, fixtures_dir, tmp_path):
    """D5's whole point, and the case Leg 1 alone can NEVER reach: the
    predicate is decided from the two paths alone, so it protects the 46
    documents this tree archived before the field existed and every archived
    document in every tree upgrading from 1.x.
    """
    root, before, proc = _cross_dated(docs_script, fixtures_dir, tmp_path, "no-witness.md")

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "\nArchived:" not in (root / "archive" / "2026-01-01" / "no-witness.md").read_text(), (
        "the fixture member must carry NO witness"
    )
    assert _M28A_REFUSAL.format(name="no-witness.md") in proc.stderr
    assert _M28A_ESCAPE in proc.stderr
    assert _snapshot(root) == before, "a refusal writes zero bytes"


def test_mv_dry_run_refuses_the_cross_dated_relocation_too(docs_script, fixtures_dir, tmp_path):
    """Phase-1 amendment 2: the refusal sits BEFORE the `--dry-run` branch, so
    it refuses in every mode.

    `_cmd_mv` returns at that branch before `preflight_move_plan` runs, so
    D5's literal "inside the pre-flight" reading would leave this printing
    `would move …` at exit 0 for an operation the apply refuses — a preview
    that lies, in the milestone whose whole point is that nothing silently
    falsifies the archive record.
    """
    root, before, proc = _cross_dated(
        docs_script, fixtures_dir, tmp_path, "with-witness.md", "--dry-run"
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "would move" not in proc.stderr, "a preview must not promise a move the apply refuses"
    assert _M28A_REFUSAL.format(name="with-witness.md") in proc.stderr
    assert _M28A_ESCAPE in proc.stderr
    assert _snapshot(root) == before


def test_mv_quiet_still_prints_both_refusal_lines(docs_script, fixtures_dir, tmp_path):
    """Item (E): both lines print even under `--quiet`, as every refusal does."""
    root, before, proc = _cross_dated(
        docs_script, fixtures_dir, tmp_path, "with-witness.md", "--quiet"
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert _M28A_REFUSAL.format(name="with-witness.md") in proc.stderr
    assert _M28A_ESCAPE in proc.stderr
    assert "moved" not in proc.stderr, "--quiet still suppresses the ordinary prose"
    assert _snapshot(root) == before


def test_mv_cross_dated_refusal_precedes_the_whole_tree_walk(docs_script, fixtures_dir, tmp_path):
    """Item (F) reason 3, and M26's stated precedence: naming the document the
    operator asked for is strictly more actionable than naming an unrelated
    malformed sibling.

    The refusal is decidable from the two arguments alone, so it must win over
    the validate-all-first walk — which would otherwise report the malformed
    document and leave the operator repairing the wrong thing.
    """
    root = _archivedate_tree(fixtures_dir, tmp_path, "archivedate-two-dated-dirs")
    (root / "broken.md").write_text("no h1 at all\n")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "mv",
        "archive/2026-01-01/with-witness.md",
        "archive/2026-03-04/with-witness.md",
        cwd=root,
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert _M28A_REFUSAL.format(name="with-witness.md") in proc.stderr, proc.stderr
    assert "broken.md" not in proc.stderr, (
        "the cross-dated refusal is reported, not the unrelated malformed sibling"
    )
    assert _snapshot(root) == before


# --- item (F)'s permitted neighbours: each one COMPLETES -------------------


def test_mv_neighbour_1_rename_within_one_dated_directory_completes(
    docs_script, fixtures_dir, tmp_path
):
    """Neighbour 1: the basename changes, the date does not."""
    root = _archivedate_tree(fixtures_dir, tmp_path, "archivedate-two-dated-dirs")
    proc = _run(
        docs_script,
        "mv",
        "archive/2026-01-01/with-witness.md",
        "archive/2026-01-01/renamed.md",
        cwd=root,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (root / "archive" / "2026-01-01" / "renamed.md").is_file()
    code, pairs = _check_pairs(docs_script, root)
    assert pairs == [], f"the rename must add no finding anywhere: {pairs!r}"
    assert code == 0


def test_mv_neighbour_1_rename_into_a_subdirectory_of_one_dated_directory_completes(
    docs_script, fixtures_dir, tmp_path
):
    """Neighbour 1's depth half: `archive/D/sub/b.md` still corroborates `D`,
    because corroboration reads the FIRST segment under the archive dir."""
    root = _archivedate_tree(fixtures_dir, tmp_path, "archivedate-two-dated-dirs")
    proc = _run(
        docs_script,
        "mv",
        "archive/2026-01-01/with-witness.md",
        "archive/2026-01-01/sub/with-witness.md",
        cwd=root,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    moved = root / "archive" / "2026-01-01" / "sub" / "with-witness.md"
    assert moved.is_file(), "the move must actually have happened"
    assert "Archived: 2026-01-01" in moved.read_text(), "and the witness is unchanged"
    code, pairs = _check_pairs(docs_script, root)
    nested = [rule for path, rule in pairs if path == "archive/2026-01-01/sub/with-witness.md"]
    assert nested == [], f"a deeper path still corroborates its dated directory: {nested!r}"
    assert pairs == [], f"and nothing else in the tree moved: {pairs!r}"
    assert code == 0


def test_mv_neighbour_2_out_of_the_archive_completes_with_only_status_drift(
    docs_script, fixtures_dir, tmp_path
):
    """Neighbour 2 / E1b: `status-drift` already owns this at exit 2, and D5
    does NOT double-report it. Uses the member with no witness, so
    `status-drift` is provably the only finding."""
    root = _archivedate_tree(fixtures_dir, tmp_path, "archivedate-two-dated-dirs")
    proc = _run(docs_script, "mv", "archive/2026-01-01/no-witness.md", "escaped.md", cwd=root)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)

    check = _run(docs_script, "check", str(root), "--json")
    assert check.returncode == 2
    assert [(r["path"], r["rule"]) for r in json.loads(check.stdout)] == [
        ("escaped.md", "status-drift")
    ]


def test_mv_neighbour_2_out_of_the_archive_with_a_witness_adds_the_drift_finding(
    docs_script, fixtures_dir, tmp_path
):
    """The same neighbour, on a witness-carrying document: `status-drift` AND
    `archive-date-drift` (message form B), independently, on one document.

    Q7's independence rule, observed through a real move rather than a
    hand-built fixture.
    """
    root = _archivedate_tree(fixtures_dir, tmp_path, "archivedate-two-dated-dirs")
    proc = _run(docs_script, "mv", "archive/2026-01-01/with-witness.md", "escaped.md", cwd=root)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)

    check = _run(docs_script, "check", str(root), "--json")
    assert check.returncode == 2
    assert [(r["path"], r["rule"]) for r in json.loads(check.stdout)] == [
        ("escaped.md", "status-drift"),
        ("escaped.md", "archive-date-drift"),
    ]


def test_mv_neighbour_2_into_a_dated_directory_completes_with_only_status_drift(
    docs_script, fixtures_dir, tmp_path
):
    """Neighbour 2's other direction / E1c: an active document moved INTO the
    archive subtree. `status-drift` owns it, and no archive-date finding can
    exist — the document carries no witness, because only `docs archive`
    writes one."""
    root = _archivedate_tree(fixtures_dir, tmp_path, "archivedate-two-dated-dirs")
    proc = _run(docs_script, "mv", "active.md", "archive/2026-03-04/active.md", cwd=root)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)

    check = _run(docs_script, "check", str(root), "--json")
    assert check.returncode == 2
    assert [(r["path"], r["rule"]) for r in json.loads(check.stdout)] == [
        ("archive/2026-03-04/active.md", "status-drift")
    ]


def test_mv_neighbour_3_to_an_undated_archive_subdirectory_completes(
    docs_script, fixtures_dir, tmp_path
):
    """Neighbour 3: the destination segment does not parse as a date, so there
    is no pair of dates to disagree. Both directions."""
    root = _archivedate_tree(fixtures_dir, tmp_path, "archivedate-two-dated-dirs")
    out = _run(
        docs_script,
        "mv",
        "archive/2026-01-01/no-witness.md",
        "archive/notes/no-witness.md",
        cwd=root,
    )
    assert out.returncode == 0, (out.stdout, out.stderr)

    back = _run(
        docs_script,
        "mv",
        "archive/notes/keep.md",
        "archive/2026-03-04/keep.md",
        cwd=root,
    )
    assert back.returncode == 0, (back.stdout, back.stderr)
    assert (root / "archive" / "notes" / "no-witness.md").is_file()
    assert (root / "archive" / "2026-03-04" / "keep.md").is_file()
    code, pairs = _check_pairs(docs_script, root)
    assert pairs == [], (
        "neither moved document carries a witness, so neither end of the "
        f"neighbour may produce a finding: {pairs!r}"
    )
    assert code == 0


def test_mv_neighbour_3_to_the_archive_root_completes_and_leg_1_reports_it(
    docs_script, fixtures_dir, tmp_path
):
    """OQ-7 (OPERATOR): the predicate is deliberately NOT widened to refuse
    this. `archive/x.md` has no dated segment, so there is no pair of dates —
    and refusing it would also refuse a legitimate reorganisation of the
    archive subtree, which `convention.md` permits.

    What the milestone owes instead is honesty about the cost, and this is the
    lock for the half that IS covered: on a witness-carrying document the move
    completes and `docs check` then reports message form B. `status-drift` is
    silent, because the destination is still inside the archive subtree — which
    is exactly why D8 names this as its second residual.
    """
    root = _archivedate_tree(fixtures_dir, tmp_path, "archivedate-two-dated-dirs")
    proc = _run(
        docs_script,
        "mv",
        "archive/2026-01-01/with-witness.md",
        "archive/with-witness.md",
        cwd=root,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)

    check = _run(docs_script, "check", str(root), "--json")
    assert check.returncode == 2
    records = json.loads(check.stdout)
    assert [(r["path"], r["rule"]) for r in records] == [
        ("archive/with-witness.md", "archive-date-drift")
    ], records
    assert records[0]["message"] == (
        "Archived: 2026-01-01 but the file is not under a dated archive/ directory "
        "(move it back, or remove the field)"
    )


def test_mv_neighbour_3_to_the_archive_root_is_silent_without_a_witness(
    docs_script, fixtures_dir, tmp_path
):
    """D8's second residual, locked as the KNOWN GAP rather than left to be
    discovered: the same move on a pre-2.0 document destroys the only
    archive-date record it has and nothing reports it.

    Recorded as *Follow-ups* item 7. If a later milestone closes it, this test
    is the one that must be revisited — deliberately, not by accident.
    """
    root = _archivedate_tree(fixtures_dir, tmp_path, "archivedate-two-dated-dirs")
    proc = _run(
        docs_script,
        "mv",
        "archive/2026-01-01/no-witness.md",
        "archive/no-witness.md",
        cwd=root,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    moved = root / "archive" / "no-witness.md"
    assert moved.is_file(), "the move must actually have happened"
    assert "\nArchived:" not in moved.read_text(), (
        "…and the document carries no witness, which is precisely why nothing "
        "can report the loss of its dated directory"
    )
    code, pairs = _check_pairs(docs_script, root)
    assert [rule for path, rule in pairs if path == "archive/no-witness.md"] == [], (
        "THE GAP, stated as the absence of a NAMED finding on the NAMED document: "
        "neither `status-drift` (the destination is still inside the archive "
        "subtree) nor `archive-date-drift` (there is no witness) reports it"
    )
    assert pairs == [], f"and nothing else in the tree moved either: {pairs!r}"
    assert code == 0


def test_mv_neighbour_4_two_spellings_of_one_date_completes(docs_script, tmp_path):
    """Neighbour 4 (implied by Q2): the predicate compares PARSED dates, so
    `2026-01-01` and `2026-1-1` are the same date and there is nothing to
    refuse.

    An implementation that compared the raw segments would refuse this — it
    passes every other Leg-2 test in this file and fails only here.

    GREEN at baseline (degenerate — nothing refuses anything yet) and one of
    the four locks that keep the Phase-6 predicate from creeping.
    """
    root = tmp_path / "unpadded"
    (root / "archive" / "2026-01-01").mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "unpadded"\n')
    (root / "archive" / "2026-01-01" / "old.md").write_text(
        "# Old\n\nLifecycle: archived\nRole: notes\nProject: unpadded\n"
        "Updated: 2026-01-01\nArchived: 2026-01-01\n\n## Body\n\nProse.\n"
    )
    proc = _run(
        docs_script,
        "mv",
        "archive/2026-01-01/old.md",
        "archive/2026-1-1/old.md",
        cwd=root,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (root / "archive" / "2026-1-1" / "old.md").is_file()
    code, pairs = _check_pairs(docs_script, root)
    assert [rule for path, rule in pairs if path == "archive/2026-1-1/old.md"] == [], (
        "`2026-1-1` corroborates `Archived: 2026-01-01` — parsed dates, not strings"
    )
    assert code == 0


def test_mv_refusal_names_the_raw_directory_segments(docs_script, tmp_path):
    """Item (E): `<D1>` and `<D2>` are the RAW directory segments.

    An implementation that re-rendered the parsed dates through
    `config.date_format` would pass every other Leg-2 assertion here — they all
    use zero-padded spellings that survive a round trip — and would then name
    two directories the tree does not have. This also proves an unpadded
    directory still participates in the predicate rather than being skipped.
    """
    root = tmp_path / "rawsegments"
    (root / "archive" / "2026-1-1").mkdir(parents=True)
    (root / "archive" / "2026-03-04").mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "rawsegments"\n')
    (root / "archive" / "2026-1-1" / "old.md").write_text(
        "# Old\n\nLifecycle: archived\nRole: notes\nProject: rawsegments\n"
        "Updated: 2026-01-01\nArchived: 2026-1-1\n\n## Body\n\nProse.\n"
    )
    (root / "archive" / "2026-03-04" / "other.md").write_text(
        "# Other\n\nLifecycle: archived\nRole: notes\nProject: rawsegments\n"
        "Updated: 2026-03-04\nArchived: 2026-03-04\n\n## Body\n\nProse.\n"
    )
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "mv",
        "archive/2026-1-1/old.md",
        "archive/2026-03-04/old.md",
        cwd=root,
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert (
        "docs: mv: archive/2026-1-1/old.md -> archive/2026-03-04/old.md "
        "crosses dated archive directories (2026-1-1 to 2026-03-04); "
        "refusing before any write"
    ) in proc.stderr, proc.stderr
    assert _M28A_ESCAPE in proc.stderr
    assert _snapshot(root) == before


def test_mv_of_an_archived_document_leaves_its_witness_byte_identical(
    docs_script, fixtures_dir, tmp_path
):
    """The M18/M28-widened move-driven exception, extended to the witness
    (D9 / Q6): a move-driven destination or bullet rewrite in an ARCHIVED
    referrer changes the moving destination and nothing else.

    `Archived:` sits on the byte-identical side beside `Archived-reason:` in
    all three of `convention.md`'s immutability paragraphs, and this is the
    lock that makes that promise real for a move.

    RED until Phase 3 (the fixture), then GREEN and degenerate — the witness it
    preserves is hand-authored in the fixture, because no verb writes one until
    Phase 6 — and genuine from Phase 6 on.
    """
    root = _archivedate_tree(fixtures_dir, tmp_path, "archivedate-clean")
    referrer = root / "archive" / "2026-03-04" / "second.md"
    before = referrer.read_text()
    assert "Archived: 2026-03-04" in before, "the fixture referrer must carry the witness"

    proc = _run(
        docs_script,
        "mv",
        "archive/2026-01-01/first.md",
        "archive/2026-01-01/renamed-first.md",
        cwd=root,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)

    after = referrer.read_text()
    expected = before.replace(
        "pairs-with: archive/2026-01-01/first.md",
        "pairs-with: archive/2026-01-01/renamed-first.md",
    )
    assert after == expected, "only the moving bullet may change"
    assert "Archived: 2026-03-04" in after, "the witness is byte-identical"


def _attic_tree(tmp_path: Path) -> Path:
    """A tree whose archive subtree is `attic/` and whose dates are `%d-%m-%Y`.

    It also carries an ORDINARY `archive/` subdirectory holding two
    date-shaped directories. On this tree `archive/` is not the archive subtree
    at all — `_is_archived_rel`'s own docstring names that trap — so a move
    between those two directories is an everyday reorganisation the tool must
    not touch.

    Every `Updated:` is ISO because `parse()` still reads it with the hardcoded
    default (defect E8, *Follow-ups* item 1); the tree's own `date_format`
    governs the dated directories and the witness, which is what is under test.
    """
    root = tmp_path / "attictree"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "attictree"\n\n[archive]\ndir = "attic"\ndate_format = "%d-%m-%Y"\n'
    )

    def _doc(title: str, lifecycle: str, archived: str | None) -> str:
        text = (
            f"# {title}\n\nLifecycle: {lifecycle}\nRole: notes\nProject: attictree\n"
            "Updated: 2026-05-20\n"
        )
        if archived is not None:
            text += f"Archived: {archived}\n"
        return text + "\n## Body\n\nProse.\n"

    for rel, lifecycle, archived in (
        ("attic/01-01-2026/old.md", "archived", "01-01-2026"),
        ("attic/04-03-2026/other.md", "archived", "04-03-2026"),
        ("archive/2026-01-01/note.md", "active", None),
        ("archive/2026-03-04/sibling.md", "active", None),
    ):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_doc(rel.rsplit("/", 1)[1], lifecycle, archived))
    return root


def test_mv_refuses_a_cross_dated_relocation_on_a_non_default_archive_tree(docs_script, tmp_path):
    """D5 / item (F): the predicate is `archive_dir_date`, so it honours BOTH
    `[archive] dir` and `[archive] date_format`.

    Every other Leg-2 test in this file runs on a tree using the defaults, so
    an implementation that inlined `rel.startswith("archive/")` and
    `strptime(seg, "%Y-%m-%d")` — `detect_archive_layout`'s config-blind idiom,
    the exact mistake E7 warns against — would pass all of them and leave
    M28a's hole wide open on this tree. The message names the configured
    directory and the raw segments, in the tree's own format.
    """
    root = _attic_tree(tmp_path)
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "mv",
        "attic/01-01-2026/old.md",
        "attic/04-03-2026/old.md",
        cwd=root,
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert (
        "docs: mv: attic/01-01-2026/old.md -> attic/04-03-2026/old.md "
        "crosses dated archive directories (01-01-2026 to 04-03-2026); "
        "refusing before any write"
    ) in proc.stderr, proc.stderr
    assert _M28A_ESCAPE in proc.stderr
    assert _snapshot(root) == before, "a refusal writes zero bytes"


def test_mv_does_not_refuse_inside_an_ordinary_archive_named_subdirectory(docs_script, tmp_path):
    """The other half of the config-blindness trap, and the more dangerous one:
    a config-blind predicate would FALSELY refuse here.

    On a tree configured `dir = "attic"`, `archive/` is an ordinary
    subdirectory and its date-shaped children are ordinary folders. Moving a
    document between them is a reorganisation the convention permits, so it
    must complete — `_is_archived_rel`'s docstring names exactly this case, and
    D5's predicate inherits its answer by using the same helper.
    """
    root = _attic_tree(tmp_path)
    proc = _run(
        docs_script,
        "mv",
        "archive/2026-01-01/note.md",
        "archive/2026-03-04/note.md",
        cwd=root,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "crosses dated archive directories" not in proc.stderr
    assert (root / "archive" / "2026-03-04" / "note.md").is_file()
    assert not (root / "archive" / "2026-01-01" / "note.md").exists()


def test_mv_collision_still_exits_1_before_the_cross_dated_refusal(
    docs_script, fixtures_dir, tmp_path
):
    """The frozen precedence: `<old>` is not a file and `<new>` already exists
    are argument errors decided BEFORE either path is resolved to a
    root-relative one, so they still win at exit **1**.

    A cross-dated move onto an occupied destination is therefore exit 1 naming
    the collision, not exit 2 naming the refusal — the invocation is wrong in a
    way the operator must fix before the refusal is even meaningful. Pinned so
    Step 2 does not have to guess, and so a Phase-6 implementer cannot hoist
    the predicate above the two `is_file` / `exists` guards.
    """
    root = _archivedate_tree(fixtures_dir, tmp_path, "archivedate-two-dated-dirs")
    occupied = root / "archive" / "2026-03-04" / "with-witness.md"
    occupied.write_text(
        "# Occupant\n\nLifecycle: archived\nRole: notes\nProject: archivedate-two-dated-dirs\n"
        "Updated: 2026-03-04\nArchived: 2026-03-04\n\n## Body\n\nProse.\n"
    )
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "mv",
        "archive/2026-01-01/with-witness.md",
        "archive/2026-03-04/with-witness.md",
        cwd=root,
    )
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "destination already exists" in proc.stderr
    assert "crosses dated archive directories" not in proc.stderr, (
        "the collision is the actionable message; the refusal does not preempt it"
    )
    assert _snapshot(root) == before
