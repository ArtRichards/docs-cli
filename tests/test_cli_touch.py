"""CLI end-to-end tests for `docs touch` (Phase 2 — written RED)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import date, timedelta
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


# --- M14 A6 — touch end-of-batch reindex honours [exclude] -----------------


def _touch_excluded_malformed_tree(tmp_path: Path) -> tuple[Path, Path]:
    """Build a docs root with `[exclude] dirs = ["vendor"]`, a conformant
    target doc at root, and a malformed `vendor/README.md`.

    Returns (root, target). The malformed vendor file must NOT fail the
    end-of-batch reindex because it is excluded.
    """
    root = tmp_path / "touch-excl"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "touch-excl"\n\n[archive]\ndir = "archive"\n\n'
        '[exclude]\ndirs = ["vendor"]\n'
    )
    target = root / "spec.md"
    target.write_text(
        "# Spec\n\nLifecycle: active\nRole: spec\nProject: touch-excl\n"
        "Updated: 2026-01-01\n\n## Body\n\nA conformant doc to touch.\n"
    )
    vendor = root / "vendor"
    vendor.mkdir()
    # Malformed: first non-empty line is not an H1 → parse() raises.
    (vendor / "README.md").write_text("no metadata\n# H1\n")
    return root, target


def test_touch_with_malformed_excluded_file_stamps_and_reindexes(docs_script, tmp_path):
    """`docs touch` over a tree whose `[exclude]` set holds a malformed file
    must stamp the date AND refresh the INDEX, exiting 0.

    RED reason: `_cmd_touch` calls `_refresh_index(root, config)` with NO
    predicate (cli.py:3648), so the end-of-batch walk reads the excluded
    malformed `vendor/README.md` and raises → exit 2 (after the date is
    already stamped — a partial, non-atomic result). Step 2 threads
    `compile_exclude_predicate(config, [])` into the reindex.
    """
    root, target = _touch_excluded_malformed_tree(tmp_path)
    today = date.today().isoformat()

    proc = _run(docs_script, "touch", str(target))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The target's Updated: is today.
    assert f"Updated: {today}" in target.read_text()
    # The INDEX exists and refreshed cleanly.
    assert (root / "INDEX.md").is_file()


def test_touch_excluded_malformed_file_not_in_index(docs_script, tmp_path):
    """The excluded malformed file must never appear in the refreshed INDEX,
    and must be byte-unchanged.

    RED reason: same as above — the unfiltered reindex raises on the
    excluded file rather than skipping it.
    """
    root, target = _touch_excluded_malformed_tree(tmp_path)
    vendor_readme = root / "vendor" / "README.md"
    vendor_before = vendor_readme.read_text()

    proc = _run(docs_script, "touch", str(target))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    index = (root / "INDEX.md").read_text()
    assert "vendor/README.md" not in index, "the excluded file must not appear in INDEX"
    # The conformant doc IS indexed — pins that the reindex completed the
    # FULL walk (excluding only vendor/), not a fix that merely swallows
    # the walk error and drops legitimate docs.
    assert "spec.md" in index, "the conformant doc must still be indexed"
    # The malformed excluded file is byte-unchanged.
    assert vendor_readme.read_text() == vendor_before


# --- M19 D1 — `docs touch --check [--stale N]` ----------------------------
#
# RED at baseline: the `--check` and `--stale` flags are undeclared on the
# `touch` subparser until Phase 5, so argparse rejects them with exit 2
# ("unrecognized arguments"). Every intended-exit-0/1 test below therefore
# fails its returncode assertion at baseline (a documented, honest RED per
# the milestone's Q-B/Q-D RED-classification style); the intended-exit-2
# tests fail because the message/behaviour they assert is the *contract*
# refusal, not argparse's "unrecognized arguments" refusal.


def _check_tree(tmp_path: Path, name: str = "checktree") -> tuple[Path, Path, Path]:
    """A docs root with one fresh (today) active doc + one ancient active doc.

    Returns (root, fresh, ancient). The dates are `today`-relative so the
    tree never rots: `fresh` is updated today, `ancient` 400 days ago.
    """
    root = tmp_path / name
    root.mkdir()
    (root / ".docs.toml").write_text(f'[project]\nname = "{name}"\n')
    today = date.today().isoformat()
    old = (date.today() - timedelta(days=400)).isoformat()
    fresh = root / "fresh.md"
    fresh.write_text(
        f"# Fresh\n\nLifecycle: active\nRole: notes\nProject: {name}\nUpdated: {today}\n\nBody.\n"
    )
    ancient = root / "ancient.md"
    ancient.write_text(
        f"# Ancient\n\nLifecycle: active\nRole: notes\nProject: {name}\nUpdated: {old}\n\nBody.\n"
    )
    return root, fresh, ancient


def test_touch_check_clean_tree_exits_0(docs_script, tmp_path):
    """Happy path: touch a doc with `--check` (no `--stale`, no config) over a
    tree with no validation problems → the fold of max(0, 0) is exit 0.

    With no stale window in play the `stale` rule never fires; the touched
    doc is bumped to today and the post-reindex check is clean.
    """
    root = tmp_path / "clean"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "clean"\n')
    doc = root / "doc.md"
    doc.write_text(
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: clean\nUpdated: 2026-01-01\n\nBody.\n"
    )
    proc = _run(docs_script, "touch", str(doc), "--check")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


def test_touch_check_stale_tree_exits_1(docs_script, tmp_path):
    """`touch <fresh> --check --stale 30` over a tree with an *untouched*
    ancient active sibling → the tree-wide check flags the sibling stale →
    exit 1, and the stale doc + the `stale` rule are named on stdout.
    """
    root, fresh, _ancient = _check_tree(tmp_path)
    proc = _run(docs_script, "touch", str(fresh), "--check", "--stale", "30")
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "ancient.md" in proc.stdout
    assert "stale" in proc.stdout.lower()


def test_touch_check_broken_ref_tree_exits_2(docs_script, tmp_path):
    """A doc with a `Related:` target that does not resolve + `--check` →
    the tree-wide check reports a `broken-ref` error → exit 2.
    """
    root = tmp_path / "brokenref"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "brokenref"\n')
    doc = root / "doc.md"
    doc.write_text(
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: brokenref\n"
        "Updated: 2026-01-01\n\nRelated:\n- references: nonexistent-target.md\n\nBody.\n"
    )
    proc = _run(docs_script, "touch", str(doc), "--check")
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "nonexistent-target.md" in proc.stdout or "broken-ref" in proc.stdout


def test_touch_check_runs_check_after_reindex(docs_script, tmp_path):
    """One `touch --check` invocation both refreshes the INDEX and validates
    the tree — confirming the ordering reindex → check (the check observes
    the post-reindex tree, and the single invocation produced an INDEX).
    """
    root = tmp_path / "afterreindex"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "afterreindex"\n')
    doc = root / "doc.md"
    doc.write_text(
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: afterreindex\n"
        "Updated: 2026-01-01\n\nBody.\n"
    )
    proc = _run(docs_script, "touch", str(doc), "--check")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The single invocation refreshed the INDEX...
    index = root / "INDEX.md"
    assert index.is_file(), "touch --check must still run the end-of-batch reindex"
    assert "doc.md" in index.read_text()
    # ...and the doc was bumped to today (the check ran on the touched tree).
    assert f"Updated: {date.today().isoformat()}" in doc.read_text()


def test_touch_check_touch_failure_short_circuits_check(docs_script, tmp_path):
    """A missing path in the batch fails `touch` (exit 1) BEFORE the check —
    the check does not run and touch's exit 1 is returned (Q1 short-circuit),
    not promoted to a check exit code.

    The tree carries a *broken-ref* sibling so a wrongly-run-and-folded check
    is observable: a check on this tree would report `broken-ref` → exit 2 and
    name the unresolved target on stdout. The short-circuit must instead leave
    the exit at touch's 1 with no finding on stdout (`max(1, 0)` ambiguity is
    thereby broken — a folded check would be `max(1, 2) = 2`).
    """
    root, a, b, _c = _multi_file_tree(tmp_path)
    brokenref = root / "brokenref.md"
    brokenref.write_text(
        "# Brokenref\n\nLifecycle: active\nRole: notes\nProject: multi\n"
        "Updated: 2026-01-01\n\nRelated:\n- references: nonexistent-target.md\n\nBody.\n"
    )
    bad = root / "no-such.md"
    proc = _run(docs_script, "touch", str(a), str(b), str(bad), "--check")
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert str(bad) in proc.stderr or "no-such.md" in proc.stderr
    # No INDEX written (touch failed in its validate pass, before any check).
    assert not (root / "INDEX.md").exists()
    # A wrongly-run check would have promoted the exit to 2 and surfaced the
    # broken ref on stdout; a true short-circuit shows neither.
    assert "nonexistent-target.md" not in proc.stdout
    assert "broken-ref" not in proc.stdout


def test_touch_check_outside_root_short_circuits(docs_script, tmp_path):
    """An orphan doc with no `.docs.toml` → touch refuses with exit 2 and the
    check never runs (Q1 short-circuit on the touch exit-2 path).
    """
    parent, doc = _orphan_doc(tmp_path)
    proc = _run(docs_script, "touch", str(doc), "--check", cwd=parent)
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "is not under a docs root with .docs.toml" in proc.stderr
    # The check never ran → no INDEX in the orphan dir, no stdout findings.
    assert not (parent / "INDEX.md").exists()


def test_touch_stale_without_check_exits_2(docs_script, tmp_path):
    """`--stale` without `--check` is an incoherent-flag hard refusal: exit 2,
    `--stale requires --check` on stderr, the file byte-unchanged (Q3).
    """
    root, _fresh, ancient = _check_tree(tmp_path)
    before = ancient.read_text()
    proc = _run(docs_script, "touch", str(ancient), "--stale", "30")
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "--stale requires --check" in proc.stderr
    # The file is left byte-identical — the refusal precedes any mutation.
    assert ancient.read_text() == before


def test_touch_dry_run_check_writes_nothing_and_checks_unmutated_tree(docs_script, tmp_path):
    """`--dry-run --check --stale N`: nothing is written, no INDEX refresh
    runs, and the check observes the UN-MUTATED on-disk tree (Q4). The doc
    the dry-run *would* refresh still reads as stale, so the check exits 1.
    """
    root, _fresh, ancient = _check_tree(tmp_path)
    before = ancient.read_text()
    proc = _run(docs_script, "touch", str(ancient), "--dry-run", "--check", "--stale", "30")
    # The ancient doc is un-mutated (dry-run) and therefore still stale → 1.
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert ancient.read_text() == before, "--dry-run must write nothing"
    assert not (root / "INDEX.md").exists(), "--dry-run must not refresh the INDEX"
    assert "ancient.md" in proc.stdout
    assert "stale" in proc.stdout.lower()


def test_touch_check_forwards_stale_value(docs_script, tmp_path):
    """The `--stale N` value is forwarded verbatim to the check: a huge window
    clears the ancient doc (exit 0); a tiny window flags it (exit 1) on the
    very same tree.
    """
    root, fresh, _ancient = _check_tree(tmp_path, "forward")
    loose = _run(docs_script, "touch", str(fresh), "--check", "--stale", "9999")
    assert loose.returncode == 0, (loose.stdout, loose.stderr)

    # Fresh sibling rebuilt (the first run bumped `fresh` to today already,
    # which is fine); a tiny window now flags the still-ancient sibling.
    tight = _run(docs_script, "touch", str(fresh), "--check", "--stale", "1")
    assert tight.returncode == 1, (tight.stdout, tight.stderr)
    assert "ancient.md" in tight.stdout


def test_touch_check_quiet_suppresses_touch_lines_not_findings(docs_script, tmp_path):
    """`--quiet` suppresses touch's `touched` stderr line but NEVER the check
    findings on stdout (Q-E). A stale tree under `--quiet` still prints the
    stale finding on stdout and exits 1.
    """
    root, fresh, _ancient = _check_tree(tmp_path, "quiet")
    proc = _run(docs_script, "touch", str(fresh), "--check", "--stale", "30", "--quiet")
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    # touch's own success line is suppressed...
    assert "touched" not in proc.stderr
    # ...but the check finding is on stdout regardless of --quiet.
    assert "ancient.md" in proc.stdout
    assert "stale" in proc.stdout.lower()


def test_touch_check_excluded_malformed_file_does_not_fail_check(docs_script, tmp_path):
    """`touch --check` applies the same `[exclude]` predicate as the reindex
    and bare `docs check` (Q-F): a malformed *excluded* file does not fail the
    tree-wide check, so the command exits 0 (mirrors
    `test_touch_with_malformed_excluded_file_*`).
    """
    root, target = _touch_excluded_malformed_tree(tmp_path)
    proc = _run(docs_script, "touch", str(target), "--check")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The excluded malformed file was neither indexed nor checked.
    index = (root / "INDEX.md").read_text()
    assert "vendor/README.md" not in index


def test_touch_check_config_default_provenance(docs_script, tmp_path):
    """`touch --check` (no `--stale`) over a `[check] stale_days`-configured
    tree with an untouched stale sibling → the config window applies, the
    check exits 1, and the finding names the config-sourced provenance.
    """
    root = tmp_path / "touchcfg"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "touchcfg"\n\n[check]\nstale_days = 30\n')
    today = date.today().isoformat()
    old = (date.today() - timedelta(days=400)).isoformat()
    fresh = root / "fresh.md"
    fresh.write_text(
        f"# Fresh\n\nLifecycle: active\nRole: notes\nProject: touchcfg\nUpdated: {today}\n\nBody.\n"
    )
    ancient = root / "ancient.md"
    ancient.write_text(
        f"# Ancient\n\nLifecycle: active\nRole: notes\nProject: touchcfg\nUpdated: {old}\n\nBody.\n"
    )
    proc = _run(docs_script, "touch", str(fresh), "--check")
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "ancient.md" in proc.stdout
    # Full frozen parenthetical (Decision: BINDING) — touch --check inherits the
    # config-sourced provenance when no --stale is forwarded.
    assert "(stale threshold 30, set in .docs.toml [check] stale_days)" in proc.stdout
    # Mutually exclusive with the CLI-sourced variant — no --stale was given.
    assert "via --stale" not in proc.stdout
