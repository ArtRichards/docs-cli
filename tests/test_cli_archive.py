"""CLI end-to-end tests for `docs archive` (Phase 2 — written RED)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

_M26_DATE = "2026-05-28"
_M26_DATED = f"archive/{_M26_DATE}"

_SKIP_AS_ROOT = pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="root bypasses 0o444 write protection; the unwritable trigger does not fire",
)


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


def _snapshot(root: Path) -> dict[str, bytes]:
    """Every file under `root`, keyed by root-relative POSIX path.

    M26 refusals promise **zero bytes written**. Whole-tree byte identity —
    `INDEX.md` and `.docs.toml` included — is what makes that a real
    assertion; `not (root / "archive").exists()` would only be a proxy.
    """
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _tree(fixtures_dir: Path, tmp_path: Path, name: str, into: str = "tree") -> Path:
    """Copy a committed fixture tree into `tmp_path` so a test may mutate it."""
    root = tmp_path / into
    shutil.copytree(fixtures_dir / "trees" / name, root)
    return root


def _retirement_message(flag: str) -> str:
    """The frozen M26 — D2 refusal line for a retired flag (one template)."""
    return (
        f"docs: archive: {flag} is retired in docs 2.0 and writes nothing; "
        "preview with `docs archive <file> --cascade-dry-run`, then write an "
        "explicit scope with `docs archive <file> --cascade-only '<glob>'`"
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


def test_archive_bare_cascade_refuses_and_writes_nothing(docs_script, tmp_path):
    """E1 / D2: bare `--cascade` is RETIRED — it refuses before any write.

    This is the milestone's headline: on this project's own tree the same
    invocation would sweep `plan.md`, `cli.md`, `convention.md`,
    `test-strategy.md`, and `status.md` into the archive. The refusal is the
    mitigation, and it must leave the tree byte-identical, `INDEX.md`
    included.

    REPLACES `test_archive_cascade_no_prompt_archives_all_relations`, whose
    contract (take-all, no prompt, exit 0) M26 deliberately reverses.

    RED reason: today `--cascade` archives the primary AND both one-hop
    relations and exits 0.
    """
    root = _two_relation_tree(tmp_path)
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        "--cascade",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert _retirement_message("--cascade") in proc.stderr, proc.stderr
    assert proc.stdout == "", "a refusal emits no --json record"
    assert _snapshot(root) == before, "a refusal must write zero bytes"
    assert not (root / "archive").exists()


def test_archive_bare_cascade_refusal_names_the_replacement_invocation(docs_script, tmp_path):
    """D2: the refusal is only worth breaking compatibility for if it tells
    the caller exactly what to run instead.

    RED reason: today `--cascade` succeeds and prints no migration guidance.
    """
    root = _two_relation_tree(tmp_path)
    proc = _run(docs_script, "archive", str(root / "root.md"), "--cascade")

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "--cascade-dry-run" in proc.stderr, "the preview replacement must be named"
    assert "--cascade-only" in proc.stderr, "the scoped-write replacement must be named"
    assert "retired" in proc.stderr


def test_archive_interactive_refuses_and_writes_nothing(docs_script, tmp_path):
    """D2 (setup Q1): `--interactive` is retired under the same refusal.

    REPLACES `test_archive_interactive_yes_also_archives_related` and
    `test_archive_interactive_no_leaves_related_in_place`, both deleted: the
    prompt path they pinned no longer exists.

    RED reason: today `--interactive` + `y` archives the primary and the
    relation and exits 0.
    """
    root = _two_relation_tree(tmp_path)
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        "--interactive",
        "--date",
        _M26_DATE,
        stdin_text="y\ny\n",
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert _retirement_message("--interactive") in proc.stderr, proc.stderr
    assert _snapshot(root) == before
    assert "[y/N]" not in proc.stderr


def test_archive_interactive_refuses_without_reading_stdin(docs_script, tmp_path):
    """D2: retiring `--interactive` removes `docs archive`'s only stdin path,
    so the refusal must fire with no stdin at all and never emit a prompt.

    No `stdin_text` is supplied deliberately.

    RED reason: today the prompt is written to stderr, EOF declines it, and
    the PRIMARY is still archived at exit 0 — a silent write where M26
    promises a refusal.
    """
    root = _two_relation_tree(tmp_path)
    before = _snapshot(root)

    proc = _run(docs_script, "archive", str(root / "root.md"), "--interactive")

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "[y/N]" not in proc.stderr, "`docs archive` never prompts on stdin at all"
    assert _snapshot(root) == before, "the primary must NOT be archived"


@pytest.mark.parametrize(
    "extra",
    [
        pytest.param([], id="alone"),
        pytest.param(["--dry-run"], id="dry-run"),
        pytest.param(["--cascade-dry-run"], id="cascade-dry-run"),
        pytest.param(["--json"], id="json"),
        pytest.param(["--quiet"], id="quiet"),
        pytest.param(["--date", "2026-05-28"], id="date"),
        pytest.param(["--reason", "x"], id="reason"),
        pytest.param(["--cascade-only", "*"], id="cascade-only"),
    ],
)
@pytest.mark.parametrize("flag", ["--cascade", "--interactive"])
def test_archive_retired_flag_refuses_under_every_other_flag(docs_script, tmp_path, flag, extra):
    """D2: the retirement is UNCONDITIONAL — the combination matrix has no
    "it depends" cell.

    This is the single test that makes that claim real. It also pins two
    corollaries: a refusal prints even under `--quiet`, and it emits no
    `--json` record (Phase-1 Q3).

    RED reason: today the outcome varies by cell — `--cascade` alone archives
    everything at exit 0, `--cascade --cascade-dry-run` previews at exit 0,
    `--json` is an unrecognized argument, and the mutually-exclusive-group
    pairs die with argparse's "not allowed with" message instead of the M26
    one.
    """
    root = _two_relation_tree(tmp_path)
    before = _snapshot(root)

    proc = _run(docs_script, "archive", str(root / "root.md"), flag, *extra)

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert _retirement_message(flag) in proc.stderr, proc.stderr
    assert proc.stdout == "", "no --json record on a refusal"
    assert _snapshot(root) == before


def test_archive_help_still_registers_the_retired_flags(docs_script, tmp_path):
    """D2 (setup Q2): the retired flags stay REGISTERED so an obsolete script
    gets a legible refusal instead of argparse's `unrecognized arguments`.

    This is the only lock on the retention shape: without it a later phase
    could legally delete the flags and every other retirement test would
    still pass (on argparse's own exit 2).

    RED reason: today `--help` describes both flags as working features and
    never says `retired`.
    """
    help_proc = _run(docs_script, "archive", "--help")
    assert help_proc.returncode == 0
    assert "--cascade" in help_proc.stdout
    assert "--interactive" in help_proc.stdout
    assert "retired" in help_proc.stdout.lower(), (
        "--help must mark the retired flags as removed and name the replacement"
    )

    root = _two_relation_tree(tmp_path)
    for flag in ("--cascade", "--interactive"):
        proc = _run(docs_script, "archive", str(root / "root.md"), flag)
        assert "unrecognized arguments" not in proc.stderr, (
            f"{flag} must stay registered, not be deleted"
        )


@pytest.mark.parametrize(
    "shape",
    [
        pytest.param([], id="plain"),
        pytest.param(["--cascade-dry-run"], id="cascade-dry-run"),
        pytest.param(["--cascade-only", "beta.md"], id="cascade-only"),
    ],
)
def test_archive_never_prompts_on_stdin(docs_script, tmp_path, shape):
    """D2's strengthened invariant: `docs archive` never prompts on stdin at
    all — not in any of the three D1 shapes, with empty stdin.

    GREEN at baseline, **degenerate** (none of the three shapes reads stdin
    today either). It becomes load-bearing once Phase 7 deletes
    `_cascade_archive`, the last reader.
    """
    root = _two_relation_tree(tmp_path)
    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        *shape,
        "--date",
        _M26_DATE,
        stdin_text="",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "[y/N]" not in proc.stderr
    assert "also archive" not in proc.stderr


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
    """`--cascade-dry-run --interactive` still exits 2 and still writes
    nothing — but under M26 — D2 the REASON changes.

    AMENDED at M26. The pre-M26 contract called this "an incoherent pair"
    and produced a bespoke combination message. `--interactive` is now
    retired outright, so the single unconditional refusal covers this cell
    like every other one, and the bespoke message is deleted (Phase-1 Q12).

    RED reason: today `_cmd_archive`'s imperative guard prints
    `docs: --cascade-dry-run cannot be combined with --interactive (a dry-run
    that prompts is incoherent)`.
    """
    root = _two_relation_tree(tmp_path)
    before = _snapshot(root)
    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        "--cascade-dry-run",
        "--interactive",
        "--date",
        _M26_DATE,
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert _retirement_message("--interactive") in proc.stderr, proc.stderr
    assert "incoherent" not in proc.stderr, "the bespoke combination message is retired"
    assert _snapshot(root) == before
    assert not (root / "archive").exists()


@pytest.mark.parametrize(
    ("extra_flags", "reported"),
    [
        pytest.param(["--cascade", "--interactive"], "--cascade", id="cascade+interactive"),
        pytest.param(
            ["--cascade-only", "sub/**", "--interactive"],
            "--interactive",
            id="cascade-only+interactive",
        ),
        pytest.param(
            ["--cascade", "--cascade-only", "sub/**"], "--cascade", id="cascade+cascade-only"
        ),
    ],
)
def test_archive_mutually_exclusive_cascade_flags_rejected(
    docs_script, tmp_path, extra_flags, reported
):
    """Every combination naming a retired flag still exits 2 and writes
    nothing — but under M26 it is the RETIREMENT that produces the refusal,
    not an argparse mutually-exclusive group.

    AMENDED at M26 (Phase-1 Q12). `--cascade` and `--interactive` leave the
    argparse mutex group precisely so no combination is intercepted by
    argparse's "not allowed with" error: one message covers every cell. When
    both retired flags are passed, `--cascade` is the one reported
    (declaration order).

    RED reason: today argparse's mutex group prints
    `argument --interactive: not allowed with argument --cascade` (and the
    equivalents) instead of the M26 retirement line.
    """
    root = _two_relation_tree(tmp_path)
    before = _snapshot(root)
    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        *extra_flags,
        "--date",
        _M26_DATE,
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert _retirement_message(reported) in proc.stderr, proc.stderr
    assert "not allowed with" not in proc.stderr, (
        "the retirement guard, not an argparse mutex group, must produce this refusal"
    )
    # No interactive prompt and nothing written for any combination.
    assert "[y/N]" not in proc.stderr
    assert _snapshot(root) == before
    assert not (root / "archive").exists()


def test_archive_cascade_dry_run_composes_with_cascade_only(docs_script, tmp_path):
    """`--cascade-dry-run --cascade-only GLOB` previews ONLY the filtered
    subset and writes nothing (exit 0) — the documented composition
    (cli.md §archive: "Composes with `--cascade-dry-run` (preview the
    filtered subset, write nothing)").

    On the two-relation tree, `--cascade-only "sub/**"` matches only the
    `pairs-with: sub/alpha.md` relation (beta.md is at the root, outside
    the glob). The preview names alpha.md but NOT beta.md, and nothing
    moves: no archive dir, primary + every related doc unchanged on disk.

    AMENDED at M26 — D6. The pre-M26 contract printed ONLY the matching
    subset, so an operator could not see what a scope was leaving behind —
    exactly the judgement a preview exists to support. The filtered preview
    now names EVERY one-hop candidate with its state, so `beta.md` must
    appear, marked not selected.

    RED reason: today the preview prints one `cascade would archive <rel>`
    line per MATCHING relation only, so `beta.md` is absent and the
    candidate-state vocabulary does not exist.
    """
    root = _two_relation_tree(tmp_path)
    before = {p.name: p.read_text() for p in root.glob("*.md")}
    before["alpha.md"] = (root / "sub" / "alpha.md").read_text()

    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        "--cascade-dry-run",
        "--cascade-only",
        "sub/**",
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # Nothing moved — no archive dir, every doc still in place + unchanged.
    assert not (root / "archive").exists(), "dry-run composition must write nothing"
    assert (root / "root.md").read_text() == before["root.md"]
    assert (root / "sub" / "alpha.md").read_text() == before["alpha.md"]
    assert (root / "beta.md").read_text() == before["beta.md"]
    # D6: the filtered preview names EVERY candidate with its state.
    assert (
        f"docs: archive: candidate sub/alpha.md — selected -> {_M26_DATED}/alpha.md"
    ) in proc.stderr, proc.stderr
    assert (
        "docs: archive: candidate beta.md — not selected (outside --cascade-only 'sub/**')"
    ) in proc.stderr, (
        "beta.md is outside sub/** — D6 requires it to be NAMED as not selected, not hidden"
    )
    assert "docs: archive: 2 candidate(s): 1 selected, 1 not selected, 0 ineligible" in proc.stderr
    assert "docs: archive: preview only — nothing was written" in proc.stderr
    # And no prompt is emitted.
    assert "[y/N]" not in proc.stderr


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
    """archive `master.md --cascade-only "sidekick.md"` archives master.md
    AND sidekick.md (pairs-with).  The witness doc's two `Related:`
    edges (one to master.md, one to sidekick.md) are rewritten to point
    at the archive paths in a single atomic batch — single INDEX refresh.

    MIGRATED at M26 from bare `--cascade` (retired, D2) to the explicit
    `--cascade-only` scope that replaces it, and the `stdin_text="y\\n"` is
    dropped — `docs archive` no longer reads stdin at all. GREEN at baseline
    and GREEN throughout: this is the M12 referring-edge no-regression proof.
    """
    root = _cascade_refs_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "archive",
        str(root / "master.md"),
        "--cascade-only",
        "sidekick.md",
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, proc.stderr
    dated = root / "archive" / "2026-05-28"
    assert (dated / "master.md").is_file()
    assert (dated / "sidekick.md").is_file()
    witness = (root / "witness.md").read_text()
    assert "archive/2026-05-28/master.md" in witness
    assert "archive/2026-05-28/sidekick.md" in witness


# --- M18 — archive edge integrity (intra-archive Related: rewriting) --------


def _archive_pair_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    """Copy the archive-pair fixture (plan <-> log, child-of cascade) into tmp_path."""
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "archive-pair", root)
    return root


def _archive_trio_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    """Copy the archive-trio fixture (plan <-> impl + plan <-> test-matrix) into tmp_path."""
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "archive-trio", root)
    return root


def test_archive_cascade_rewrites_moved_docs_own_edges(docs_script, fixtures_dir, tmp_path):
    """archive `master.md --cascade-only "sidekick.md"` moves master.md AND
    sidekick.md (pairs-with). Each moved doc's OWN `Related:` bullet — which
    points at the other, co-moving doc — is repointed to the new archive
    path. Pins M18 — D1 leg-1 (the moved doc's own outgoing edges).

    MIGRATED at M26 from bare `--cascade` (retired, D2) to the explicit
    `--cascade-only` scope, `stdin_text` dropped. GREEN at baseline and GREEN
    throughout: the M18 archive-edge no-regression proof.

    RED reason: `_archive_one` (cli.py:3595) sets metadata + moves the file
    but never rewrites the moved doc's own `Related:` bullets, and
    `_rewrite_referring_edges` skips the (now-archived) sibling
    (the unconditional `if doc.archived` skip in `_rewrite_referring_edges`)
    — so master's
    `pairs-with: sidekick.md` and sidekick's `pairs-with: master.md` are
    left as bare basenames pointing at files that no longer live at the
    root. Phase 6 rewrites the moved doc's own batch-`old_rel` edges.
    """
    root = _cascade_refs_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "archive",
        str(root / "master.md"),
        "--cascade-only",
        "sidekick.md",
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, proc.stderr
    dated = root / "archive" / "2026-05-28"
    assert (dated / "master.md").is_file()
    assert (dated / "sidekick.md").is_file()
    master = (dated / "master.md").read_text()
    sidekick = (dated / "sidekick.md").read_text()
    # Each moved doc's own edge points at the other's NEW archive path.
    assert "pairs-with: archive/2026-05-28/sidekick.md" in master, master
    assert "pairs-with: archive/2026-05-28/master.md" in sidekick, sidekick
    # The bare-basename forms are gone.
    assert "pairs-with: sidekick.md\n" not in master, master
    assert "pairs-with: master.md\n" not in sidekick, sidekick


def test_archive_pair_leaves_check_clean(docs_script, fixtures_dir, tmp_path):
    """Archiving a plan/log pair in one op — by archiving the LOG with
    `--cascade-only` on the plan glob (log->plan is `child-of`, a cascade
    verb) — lands BOTH docs in the archive with every intra-pair `Related:`
    edge resolving. `docs check <root>` then exits 0. Pins M18 — D1 through
    the real check gate (M18 — Q3: drive the cascade by archiving the log,
    never bare `--cascade` on the plan — which M26 — D2 has since retired
    outright). Needs no M26 edit; GREEN at baseline and GREEN throughout.

    RED reason: neither moved doc's own edge is rewritten today (D1 not
    implemented), so the archived plan's `parent-of: <log>` and the log's
    `child-of`/`pairs-with: <plan>` bullets dangle as bare basenames ->
    `broken-ref` -> `docs check` exit 2. Phase 6 repoints them.
    """
    root = _archive_pair_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "archive",
        str(root / "feature-log.md"),
        "--cascade-only",
        "feature.md",
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, proc.stderr
    dated = root / "archive" / "2026-05-28"
    assert (dated / "feature.md").is_file(), "plan not cascaded via child-of"
    assert (dated / "feature-log.md").is_file()
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


def test_archive_leaves_unrelated_archived_content_byte_identical(
    docs_script, fixtures_dir, tmp_path
):
    """Open Q4 boundary lock (BOTH directions): when `core.md` is archived,
    the fix rewrites an archived doc's `Related:` edge IFF its target equals a
    batch `old_rel` (i.e. iff the target is moving in THIS op) — and never
    otherwise.

    Two pre-archived bystanders in DIFFERENT archive dates exercise both
    sides of the boundary:

    * `bystander.md` (`archive/2026-04-01/`) — edge -> NON-moving `helper.md`,
      plus prose mentioning the moving `core.md`. It must stay BYTE-IDENTICAL:
      its content, `Updated:`, lifecycle, and its unrelated edge are verbatim.
      This guards the read-only stance for everything OUTSIDE move-driven edge
      rewrites, and fails an over-broad fix that touched a non-moving edge OR
      prose that merely names the moving doc (e.g. a naive whole-file string
      replace instead of the structural `rewrite_related_refs` matcher).
    * `mover-ref.md` (`archive/2026-03-01/`) — edge -> the MOVING `core.md`.
      Its edge MUST be repointed to `archive/2026-05-28/core.md` (the new
      path), even though it lives in a different archive date than the move's
      destination. This fails any under-broad fix that unconditionally skips
      archived docs (the pre-M18 stance) and leaves the edge dangling.

    Together these pin the exact boundary: rewrite an archived doc's edge iff
    its target is in the batch `old_rels`. The Phase-4 partial form of this
    test (single non-moving bystander) could not distinguish the UNDER-broad
    skip; the second, moving-target bystander closes that gap (impl-log
    Phase-6 carry-forward).

    Boundary note (Q4): the `old_rels` gate and a hypothetical "walk all
    archived docs unconditionally" fix produce BYTE-IDENTICAL output here,
    because `rewrite_related_refs` only ever rewrites a bullet whose target
    EXACTLY equals an `old_rel`. The exact-match matcher — not the gate — is
    the edge-level boundary guard; the gate is an intent/efficiency screen
    (skip archived docs that reference no mover). The byte-identity assertion
    therefore catches over-broad fixes that escape the matcher (prose /
    arbitrary content), while the mover-ref assertion catches the under-broad
    skip. (Verified in Phase 6: an unconditional skip fails this test; an
    unconditional rewrite leaves it green precisely because the matcher is
    target-exact.)
    """
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    # Bystander A: archived doc whose edge points at `helper.md` (which does
    # NOT move in the op below — we archive `core.md`), plus prose.
    archived_dir = root / "archive" / "2026-04-01"
    archived_dir.mkdir(parents=True)
    bystander = archived_dir / "bystander.md"
    bystander.write_text(
        "# Bystander\n\n"
        "Lifecycle: archived\nRole: notes\nProject: cross-refs\n"
        "Updated: 2026-04-01\n\n"
        "Related:\n- references: helper.md\n\n"
        "## Body\n\n"
        "An archived doc whose edge points at helper.md (not moving) and "
        "whose prose mentions core.md and helper.md should stay verbatim.\n"
    )
    before = bystander.read_text()

    # Bystander B: archived doc in a DIFFERENT date whose edge points at the
    # MOVING `core.md`. Its edge MUST be repointed to the new archive path.
    other_dir = root / "archive" / "2026-03-01"
    other_dir.mkdir(parents=True)
    mover_ref = other_dir / "mover-ref.md"
    mover_ref.write_text(
        "# Mover ref\n\n"
        "Lifecycle: archived\nRole: notes\nProject: cross-refs\n"
        "Updated: 2026-03-01\n\n"
        "Related:\n- references: core.md\n\n"
        "## Body\n\n"
        "An archived doc whose edge points at the (moving) core.md.\n"
    )

    proc = _run(
        docs_script,
        "archive",
        str(root / "core.md"),
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, proc.stderr
    # Direction 1 — non-moving target: byte-identical (nothing rewritten).
    assert bystander.read_text() == before
    # Direction 2 — moving target: the edge IS repointed to the new path.
    after = mover_ref.read_text()
    assert "references: archive/2026-05-28/core.md" in after, after
    assert "references: core.md\n" not in after, after


def test_archive_cascade_trio_lands_edge_clean(docs_script, fixtures_dir, tmp_path):
    """archive the plan `--cascade-only "feature-*.md"` on the trio fixture
    (plan <-> impl and plan <-> test-matrix, both `pairs-with`) moves all
    three; every intra-trio edge resolves to `archive/<date>/...` and
    `docs check` exits 0. Pins scoped trio composition (M16-shaped).

    MIGRATED at M26 from bare `--cascade` (retired, D2), `stdin_text`
    dropped. GREEN at baseline and GREEN throughout.

    RED reason: D1 not implemented — the plan's two `pairs-with` bullets and
    each child's back-edge to the plan are left as bare basenames after the
    move -> `broken-ref` -> `docs check` exit 2. Phase 6 repoints the whole
    trio's intra-archive edges in one atomic batch.
    """
    root = _archive_trio_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "archive",
        str(root / "feature.md"),
        "--cascade-only",
        "feature-*.md",
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, proc.stderr
    dated = root / "archive" / "2026-05-28"
    assert (dated / "feature.md").is_file()
    assert (dated / "feature-impl.md").is_file(), "impl not cascaded (pairs-with)"
    assert (dated / "feature-test-matrix.md").is_file(), "test-matrix not cascaded (pairs-with)"
    plan = (dated / "feature.md").read_text()
    assert "pairs-with: archive/2026-05-28/feature-impl.md" in plan, plan
    assert "pairs-with: archive/2026-05-28/feature-test-matrix.md" in plan, plan
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


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
    # The archived conformant doc IS indexed — pins a FULL walk (excluding
    # only vendor/), not a fix that swallows the walk error and drops docs.
    assert "archive/2026-05-28/doomed.md" in index, "the archived doc must be indexed"


def test_archive_repoints_already_archived_referrer(docs_script, fixtures_dir, tmp_path):
    """An already-archived `old-ref.md` whose `Related:` edge points at the
    still-active `core.md` IS repointed to `archive/<date>/core.md` once
    `core.md` is archived into the subtree.

    This is the FLIPPED REPLACEMENT for the deleted
    `test_archive_does_not_rewrite_archive_subtree_edges`. The M18 Decisions
    (Q5, binding) deliberately reverse that pin: an archived referrer whose
    target MOVES INTO the archive SHOULD be repointed (otherwise the edge
    dangles), narrowing the M3 "archive is read-only" stance to leave every
    non-move-driven edge untouched.

    RED reason: `_rewrite_referring_edges`'s unconditional `if doc.archived`
    skip (`continue`s on every archived doc), so the already-archived `old-ref.md`'s
    `references: core.md` bullet is left as a bare basename pointing at the
    now-moved `core.md` — a dangling edge. Phase 6 conditions that skip so an
    archived referrer pointing at a batch `old_rel` is repointed.
    """
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
    proc = _run(
        docs_script,
        "archive",
        str(root / "core.md"),
        "--date",
        "2026-05-28",
    )
    assert proc.returncode == 0, proc.stderr
    # The archived referrer's edge is repointed to the new archive path.
    after = archived_doc.read_text()
    assert "references: archive/2026-05-28/core.md" in after, after
    assert "references: core.md\n" not in after, after


# --- M14 A4 — uncaught OSError mid edge-rewrite → clean exit 2 --------------


def _readonly_referrer_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Build a docs root where the referrer lives in a read-only subdir.

    Returns (root, source, locked_dir). `source.md` (at root) is the
    archive target; `locked/referrer.md` carries `pairs-with: source.md`,
    so the post-move referring-edge rewrite walk tries to `atomic_write`
    it — which raises `OSError` (PermissionError) when the `.docs-tmp`
    tmpfile cannot be created in the `0o555` `locked/` directory. (A bare
    `chmod 0o444` on the file is NOT a reliable trigger: POSIX `rename()`
    onto a read-only target succeeds when the directory is writable; a
    read-only *directory* is the portable trigger.)

    This mirrors `tests/test_cli_mv.py::_readonly_referrer_tree`; the
    contract under test (cli.md §archive + the exit-code matrix: "`OSError`
    raised while rewriting a referring edge after the move (M14 — A4)") is
    observable: exit 2 + no Traceback.
    """
    root = tmp_path / "ro"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "ro"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: ro\n"
    source = root / "source.md"
    source.write_text(f"# Source\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\nThe archive target.\n")
    locked = root / "locked"
    locked.mkdir()
    (locked / "referrer.md").write_text(
        f"# Referrer\n\n{hdr}Updated: 2026-01-02\n\n"
        "Related:\n- pairs-with: source.md\n\n## Body\n\nReferences the source.\n"
    )
    # Read-only directory: the post-move walk can still read referrer.md,
    # but the atomic_write tmpfile creation during the edge rewrite raises
    # OSError (PermissionError, an OSError subclass).
    os.chmod(locked, 0o555)
    return root, source, locked


@pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="root bypasses 0o555 directory write protection; the OSError trigger does not fire",
)
def test_archive_oserror_mid_rewrite_exits_2(docs_script, tmp_path):
    """An OSError raised while rewriting a referring edge after the archive
    move must surface as a clean exit 2 with no Traceback on stderr (the
    observable contract; M14 — A4).

    Regression guard for the archive half of the A4 contract: `_cmd_archive`
    maps an `OSError` from `_rewrite_referring_edges` (cli.py ~3728) to a
    clean exit 2 with `docs: archive: …` on stderr. Mirrors the mv guard
    `test_cli_mv.py::test_mv_oserror_mid_rewrite_exits_2`. GREEN against the
    shipped code (NOT a RED→GREEN cycle).
    """
    root, source, locked = _readonly_referrer_tree(tmp_path)
    try:
        proc = _run(docs_script, "archive", str(source), "--date", "2026-05-28")
        assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
        assert "Traceback" not in proc.stderr, (
            "an OSError mid edge-rewrite must be mapped to a clean exit 2, not a "
            f"traceback:\n{proc.stderr}"
        )
    finally:
        os.chmod(locked, 0o755)  # restore so tmp_path teardown can clean up


# --- M25 — reciprocity survives `docs archive` (GREEN at baseline) ---------


def _reciprocal_archive_tree(tmp_path: Path, name: str) -> Path:
    """A complete `precedes`/`follows` pair, `pairs-with`-linked for cascade."""
    root = tmp_path / name
    root.mkdir()
    (root / ".docs.toml").write_text(f'[project]\nname = "{name}"\n')
    (root / "a.md").write_text(
        f"# A\n\nLifecycle: active\nRole: notes\nProject: {name}\nUpdated: 2026-05-20\n"
        "\nRelated:\n- precedes: b.md\n- pairs-with: b.md\n\n## Body\n\nProse.\n"
    )
    (root / "b.md").write_text(
        f"# B\n\nLifecycle: active\nRole: notes\nProject: {name}\nUpdated: 2026-05-20\n"
        "\nRelated:\n- follows: a.md\n- pairs-with: a.md\n\n## Body\n\nProse.\n"
    )
    return root


def test_archive_one_endpoint_preserves_reciprocal_pair(docs_script, tmp_path):
    """M25 lock: archiving ONE endpoint repoints the active referrer's edge.

    GREEN at baseline (M14 — A4 referring-edge rewrite). It must STAY green
    under M25's hard rule: both halves must keep resolving, so the pair is
    still complete after the move.
    """
    root = _reciprocal_archive_tree(tmp_path, "arcrecip")
    today = date.today().isoformat()
    proc = _run(docs_script, "archive", str(root / "b.md"), "--reason", "done")
    assert proc.returncode == 0, proc.stderr

    moved = root / "archive" / today / "b.md"
    assert moved.is_file()
    assert f"- precedes: archive/{today}/b.md" in (root / "a.md").read_text()
    assert "- follows: a.md" in moved.read_text()

    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


def test_archive_cascade_preserves_reciprocal_pair(docs_script, tmp_path):
    """M25 lock: a scoped cascade moves BOTH endpoints and repoints both
    halves.

    MIGRATED at M26 from bare `--cascade` (retired, D2) to
    `--cascade-only "b.md"`. GREEN at baseline (M18 archive-subtree edge
    integrity). It must STAY green under M25's hard rule — an intra-archive
    pair whose edges were left pointing at the old paths would now be a
    `broken-ref` AND, once repaired, must still be reciprocal.
    """
    root = _reciprocal_archive_tree(tmp_path, "cascaderecip")
    today = date.today().isoformat()
    proc = _run(
        docs_script, "archive", str(root / "a.md"), "--cascade-only", "b.md", "--reason", "done"
    )
    assert proc.returncode == 0, proc.stderr

    a_arc = root / "archive" / today / "a.md"
    b_arc = root / "archive" / today / "b.md"
    assert a_arc.is_file() and b_arc.is_file()
    assert f"- precedes: archive/{today}/b.md" in a_arc.read_text()
    assert f"- follows: archive/{today}/a.md" in b_arc.read_text()

    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


# --- M26 — D6 preview: the whole neighborhood, never just the selection -----


def test_cascade_dry_run_names_every_candidate_with_its_state(docs_script, fixtures_dir, tmp_path):
    """E1 / D6: an unfiltered `--cascade-dry-run` names all six one-hop
    candidates, each marked not selected (there is no scope), and writes
    nothing.

    Pinned on the committed `archive-neighborhood` fixture rather than this
    repo's live `docs/` tree (Phase-1 Q13) so the lock cannot rot; the
    live-tree run is Phase-9 dogfood evidence.

    RED reason: today the preview prints one `docs: cascade would archive
    <rel>` line per candidate plus a `cascade would archive N related doc(s)`
    footer — no candidate-state vocabulary, no selected/not-selected/
    ineligible distinction, and no `preview only` line.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-neighborhood")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "milestone.md"),
        "--cascade-dry-run",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (
        f"docs: archive: would archive milestone.md -> {_M26_DATED}/milestone.md"
    ) in proc.stderr, proc.stderr
    for rel in (
        "plan.md",
        "milestone-impl.md",
        "cli.md",
        "convention.md",
        "test-strategy.md",
        "status.md",
    ):
        assert (
            f"docs: archive: candidate {rel} — not selected (no --cascade-only scope)"
        ) in proc.stderr, f"{rel} missing from the unfiltered preview:\n{proc.stderr}"
    assert "docs: archive: 6 candidate(s): 0 selected, 6 not selected, 0 ineligible" in proc.stderr
    assert "docs: archive: preview only — nothing was written" in proc.stderr
    assert _snapshot(root) == before, "a preview writes nothing"


def test_filtered_preview_still_names_the_unselected_candidate(docs_script, fixtures_dir, tmp_path):
    """E1 / D6: `--cascade-only 'milestone*'` selects the impl log and leaves
    the whole specification spine — which the preview must still NAME, so the
    operator can see exactly what the scope is leaving behind.

    RED reason: today a filtered preview prints only the matching subset, so
    `plan.md`, `cli.md`, `convention.md`, `test-strategy.md`, and `status.md`
    are invisible.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-neighborhood")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "milestone.md"),
        "--cascade-dry-run",
        "--cascade-only",
        "milestone*",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (
        f"docs: archive: candidate milestone-impl.md — selected -> {_M26_DATED}/milestone-impl.md"
    ) in proc.stderr, proc.stderr
    for rel in ("plan.md", "cli.md", "convention.md", "test-strategy.md", "status.md"):
        assert (
            f"docs: archive: candidate {rel} — not selected (outside --cascade-only 'milestone*')"
        ) in proc.stderr, f"the spine doc {rel} must be named, not hidden:\n{proc.stderr}"
    assert "docs: archive: 6 candidate(s): 1 selected, 5 not selected, 0 ineligible" in proc.stderr
    assert _snapshot(root) == before


def test_preview_names_an_ineligible_archived_candidate(docs_script, fixtures_dir, tmp_path):
    """E4 / D6: an archive-subtree candidate is named INELIGIBLE, with its
    reason, and is never counted as selected.

    RED reason: today the preview would list `archive/2026-01-01/old.md` as a
    doc it "would archive" — and a real `--cascade` run relocates and re-dates
    it.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-archived-neighbour")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "plan.md"),
        "--cascade-dry-run",
        "--cascade-only",
        "*",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (f"docs: archive: candidate log.md — selected -> {_M26_DATED}/log.md") in proc.stderr, (
        proc.stderr
    )
    assert (
        "docs: archive: candidate archive/2026-01-01/old.md — ineligible (already archived)"
    ) in proc.stderr, proc.stderr
    assert "docs: archive: 2 candidate(s): 1 selected, 0 not selected, 1 ineligible" in proc.stderr
    assert _snapshot(root) == before


def test_preview_of_a_primary_only_archive_names_no_candidates(docs_script, fixtures_dir, tmp_path):
    """D1 (setup Q7): `docs archive FILE --dry-run` stays QUIET about the
    candidates it leaves in place — a notice on every single-document archive
    would be noise, and the safe behaviour needs no announcement.

    GREEN at baseline, **degenerate**: today's `--dry-run` prints no candidate
    line either, because the cascade preview is gated on a cascade flag. It
    becomes a genuine lock once the candidate vocabulary exists.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-neighborhood")
    before = _snapshot(root)

    proc = _run(docs_script, "archive", str(root / "milestone.md"), "--dry-run")

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "candidate" not in proc.stderr, proc.stderr
    assert _snapshot(root) == before


def test_cascade_only_with_global_dry_run_matches_cascade_dry_run(
    docs_script, fixtures_dir, tmp_path
):
    """D1: `--cascade-only GLOB --dry-run` is byte-for-byte the same preview
    as `--cascade-dry-run --cascade-only GLOB`. Two spellings, one behaviour —
    another cell the compatibility matrix must not leave to chance.

    RED reason: both invocations name only the matching subset today, so the
    D6 assertion below fails on each. (The equality itself already holds —
    that is the point of asserting the content too.)
    """
    root_a = _tree(fixtures_dir, tmp_path, "archive-neighborhood", into="a")
    root_b = _tree(fixtures_dir, tmp_path, "archive-neighborhood", into="b")

    global_dry = _run(
        docs_script,
        "archive",
        str(root_a / "milestone.md"),
        "--cascade-only",
        "milestone*",
        "--dry-run",
        "--json",
        "--date",
        _M26_DATE,
    )
    cascade_dry = _run(
        docs_script,
        "archive",
        str(root_b / "milestone.md"),
        "--cascade-dry-run",
        "--cascade-only",
        "milestone*",
        "--json",
        "--date",
        _M26_DATE,
    )

    assert global_dry.returncode == cascade_dry.returncode == 0
    assert global_dry.stderr.replace(str(root_a), "") == cascade_dry.stderr.replace(
        str(root_b), ""
    ), (global_dry.stderr, cascade_dry.stderr)
    assert "docs: archive: candidate plan.md — not selected" in global_dry.stderr
    # The `--dry-run` matrix row promises a record too, and the same one.
    record_a = json.loads(global_dry.stdout)
    record_b = json.loads(cascade_dry.stdout)
    record_a["primary"].pop("source")
    record_b["primary"].pop("source")
    assert record_a == record_b
    assert record_a["dry_run"] is True and record_a["applied"] is False


def test_cascade_dry_run_with_a_non_matching_scope_exits_zero(docs_script, fixtures_dir, tmp_path):
    """D6 (Phase-1 Q2, operator): a PREVIEW is never a write, so it never
    fails. A `--cascade-only` that selects nothing still exits **0** — the
    typo stays loudly visible instead of becoming a refusal.

    D5's exit-2 refusal governs the WRITE path only; the same scope on a real
    write is `test_cascade_only_none_matched_refuses` below.

    RED reason: `--json` is an unrecognized argument today (argparse exit 2),
    and no `matched none of the N` line exists.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-neighborhood")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "milestone.md"),
        "--cascade-dry-run",
        "--cascade-only",
        "typo-*",
        "--json",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (
        "docs: archive: --cascade-only 'typo-*' matched none of the 6 one-hop candidate(s)"
    ) in proc.stderr, proc.stderr
    assert "refusing before any write" not in proc.stderr, "a preview never refuses"
    record = json.loads(proc.stdout)
    assert [c for c in record["candidates"] if c["selected"]] == [], record
    assert record["dry_run"] is True and record["applied"] is False
    assert _snapshot(root) == before


# --- M26 — D1/D3/D4/D5 scoped write ----------------------------------------


def test_cascade_only_dedups_and_prints_no_false_failure(docs_script, fixtures_dir, tmp_path):
    """E2 / D3: a doc reachable by `pairs-with` AND `child-of` is archived
    ONCE, and the run reports no failure.

    RED reason: `_cascade_set` yields `b.md` twice, so the second
    `_archive_one` call reads a file that has already moved and the run
    prints `docs: could not archive b.md: [Errno 2] No such file or
    directory` — a false failure on a successful operation — while still
    exiting 0.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-duplicate-edge")

    proc = _run(
        docs_script,
        "archive",
        str(root / "a.md"),
        "--cascade-only",
        "b.md",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "could not archive" not in proc.stderr, proc.stderr
    assert "No such file or directory" not in proc.stderr, proc.stderr
    assert (root / _M26_DATED / "a.md").is_file()
    assert (root / _M26_DATED / "b.md").is_file()
    # The apply-mode primary line: `archived`, not `would archive`, and no
    # `preview only` line — the only two things distinguishing an apply from a
    # preview on stderr.
    assert f"docs: archive: archived a.md -> {_M26_DATED}/a.md" in proc.stderr, proc.stderr
    assert "preview only" not in proc.stderr
    assert "docs: archive: 1 candidate(s): 1 selected, 0 not selected, 0 ineligible" in proc.stderr


def test_cascade_only_collision_refuses_before_any_write(docs_script, fixtures_dir, tmp_path):
    """E3 / D4: two candidates that would land on ONE destination refuse the
    whole operation before any byte moves, naming both sources.

    RED reason: today `x/dup.md` is archived, `y/dup.md` fails with a bare
    `docs: could not archive y/dup.md: …` line, the run exits **0**, and
    `docs check` afterwards reports no violations — a partial write that
    leaves no detectable drift.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-collision")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        "--cascade-only",
        "dup.md",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert (
        f"docs: archive: x/dup.md and y/dup.md would both archive to {_M26_DATED}/dup.md; "
        "refusing before any write"
    ) in proc.stderr, proc.stderr
    assert proc.stdout == ""
    assert _snapshot(root) == before, "both docs must still be at their original paths"


def test_cascade_only_excludes_an_archived_neighbour(docs_script, fixtures_dir, tmp_path):
    """E4 / D3: an already-archived candidate is excluded — its bytes, its
    path, and its `Updated:` value are untouched — while the eligible
    candidate is archived normally.

    RED reason: today `--cascade-only '*'` matches the archive-subtree target
    too, so `archive/2026-01-01/old.md` is relocated to
    `archive/<date>/old.md` with `Updated:` rewritten. That is data
    corruption, not merely over-reach.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-archived-neighbour")
    archived = root / "archive" / "2026-01-01" / "old.md"
    archived_before = archived.read_bytes()

    proc = _run(
        docs_script,
        "archive",
        str(root / "plan.md"),
        "--cascade-only",
        "*",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert archived.is_file(), "the archived neighbour must not move"
    assert archived.read_bytes() == archived_before, "its bytes and Updated: are history"
    assert not (root / _M26_DATED / "old.md").exists()
    assert (root / _M26_DATED / "plan.md").is_file()
    assert (root / _M26_DATED / "log.md").is_file()
    assert (
        "docs: archive: candidate archive/2026-01-01/old.md — ineligible (already archived)"
    ) in proc.stderr, proc.stderr


@pytest.mark.parametrize(
    "shape",
    [
        pytest.param([], id="plain"),
        pytest.param(["--cascade-dry-run"], id="cascade-dry-run"),
        pytest.param(["--cascade-only", "*"], id="cascade-only"),
    ],
)
def test_archive_archived_primary_refuses(docs_script, fixtures_dir, tmp_path, shape):
    """E4 / D4 (Phase-1 Q1): naming an already-archived document as the
    PRIMARY is a refusal in ALL THREE D1 shapes — the preview included. D1's
    table describes authorization, not an exemption from validity checks.

    RED reason: today every shape happily re-archives it, relocating
    `archive/2026-01-01/old.md` to `archive/<date>/old.md` and rewriting
    `Updated:` (the preview shape exits 0 having previewed exactly that).
    """
    root = _tree(fixtures_dir, tmp_path, "archive-archived-neighbour")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "archive" / "2026-01-01" / "old.md"),
        *shape,
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert (
        "docs: archive: archive/2026-01-01/old.md is already under the archive subtree; "
        "refusing before any write"
    ) in proc.stderr, proc.stderr
    assert proc.stdout == ""
    assert _snapshot(root) == before


def test_cascade_only_none_matched_refuses(docs_script, fixtures_dir, tmp_path):
    """E5 / D5: a typo'd scope on a WRITE refuses with exit 2 and the primary
    is NOT archived.

    RED reason: today `--cascade-only 'typo-*'` archives the primary, prints
    `docs: cascade: no one-hop relations to archive`, and exits 0 — a typo
    indistinguishable from a deliberate primary-only archive.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-neighborhood")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "milestone.md"),
        "--cascade-only",
        "typo-*",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert (
        "docs: archive: --cascade-only 'typo-*' matched none of the 6 one-hop candidate(s); "
        "refusing before any write"
    ) in proc.stderr, proc.stderr
    assert _snapshot(root) == before, "the primary must NOT be archived"


def test_cascade_only_with_no_candidates_refuses_distinctly(docs_script, tmp_path):
    """D5: "candidates existed but none was selected" and "this doc has no
    candidates at all" are DIFFERENT mistakes and get different messages —
    the second one names the invocation that does what the caller meant.

    RED reason: today both cases print the same
    `docs: cascade: no one-hop relations to archive` footer and exit 0.
    """
    root = tmp_path / "solo"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "solo"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: solo\n"
    (root / "other.md").write_text(f"# Other\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\nx.\n")
    (root / "solo.md").write_text(
        f"# Solo\n\n{hdr}Updated: 2026-01-02\n\n"
        "Related:\n- references: other.md\n\n## Body\n\nno cascade verbs.\n"
    )
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "solo.md"),
        "--cascade-only",
        "*",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert (
        "docs: archive: solo.md has no one-hop pairs-with / child-of candidates; "
        "refusing before any write (use `docs archive <file>` to archive it alone)"
    ) in proc.stderr, proc.stderr
    assert "matched none of the" not in proc.stderr, (
        "the two empty-selection cases must be distinguishable"
    )
    assert _snapshot(root) == before


@pytest.mark.parametrize(
    "pattern",
    [pytest.param("", id="empty"), pytest.param("# just a comment", id="comment-only")],
)
def test_cascade_only_empty_pattern_refuses(docs_script, tmp_path, pattern):
    """D5 (Phase-1 Q9): a pattern that compiles to nothing is its own refusal,
    on the M25 `--reason must not be empty` precedent.

    RED reason: today `_cascade_set` returns `[]` for a comment/blank pattern,
    so the primary is archived alone at exit 0.
    """
    root = _two_relation_tree(tmp_path)
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        "--cascade-only",
        pattern,
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "docs: archive: --cascade-only must not be empty" in proc.stderr, proc.stderr
    assert _snapshot(root) == before


def test_scoped_write_with_a_dotted_edge_leaves_check_clean(docs_script, tmp_path):
    """D3 / Phase-1 Q5: a `./b.md` bullet is selected by `--cascade-only
    'b.md'` AND repointed, so `docs check` is clean afterwards.

    GREEN at baseline and **genuine, load-bearing**. It is the only guard
    against the canonicalization regression: once the candidate set is keyed
    on the canonical path, the batch handed to `_rewrite_referring_edges`
    must still carry the DECLARED `./b.md` spelling as an alias, because that
    matcher rewrites a bullet iff its target exactly equals an `old_rel`.
    Dropping the alias would leave `./b.md` dangling and `docs check` at
    exit 2.
    """
    root = tmp_path / "dotted"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "dotted"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: dotted\n"
    (root / "a.md").write_text(
        f"# A\n\n{hdr}Updated: 2026-01-01\n\nRelated:\n- pairs-with: ./b.md\n\n## Body\n\na.\n"
    )
    (root / "b.md").write_text(
        f"# B\n\n{hdr}Updated: 2026-01-02\n\nRelated:\n- pairs-with: a.md\n\n## Body\n\nb.\n"
    )

    proc = _run(
        docs_script,
        "archive",
        str(root / "a.md"),
        "--cascade-only",
        "b.md",
        "--date",
        _M26_DATE,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (root / _M26_DATED / "a.md").is_file()
    assert (root / _M26_DATED / "b.md").is_file(), "a ./b.md edge must still be selectable"

    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


def test_archive_reason_is_written_to_the_primary_only(docs_script, tmp_path):
    """D1 (Phase-1 Q10): `--reason` explains why THIS archive was requested,
    so it lands on the named primary and never on a cascaded candidate.

    GREEN at baseline (today's cascade already passes `None` for the related
    docs' reason) — pinned so the M26 rewrite cannot quietly generalise it.
    """
    root = _two_relation_tree(tmp_path)

    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        "--cascade-only",
        "beta.md",
        "--reason",
        "milestone closed out",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    primary = (root / _M26_DATED / "root.md").read_text()
    candidate = (root / _M26_DATED / "beta.md").read_text()
    assert "Archived-reason: milestone closed out" in primary
    assert "Archived-reason:" not in candidate, (
        "a cascaded candidate never receives the primary's Archived-reason:"
    )


# --- M26 — the Q4 exit-code split at the CLI --------------------------------


def test_cascade_only_malformed_candidate_exits_1(docs_script, tmp_path):
    """Q4: a plan member with no editable metadata block keeps 1.x's exit
    **1** — it is one of the three conditions the pre-M26 matrix already
    assigned that code — but gains the M26 refusal message and the
    zero-bytes-written guarantee.

    RED reason: today the whole-tree pre-flight walk raises first and prints
    the bare `docs: <MetadataError>` text; the M26 plan pre-flight runs
    BEFORE that walk so the refusal names the plan member the operator
    actually asked for.
    """
    root = tmp_path / "badmember"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "badmember"\n\n[archive]\ndir = "archive"\n'
    )
    (root / "a.md").write_text(
        "# A\n\nLifecycle: active\nRole: notes\nProject: badmember\nUpdated: 2026-01-01\n\n"
        "Related:\n- pairs-with: b.md\n\n## Body\n\na.\n"
    )
    (root / "b.md").write_text("no H1, no metadata block — unparseable.\n")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "a.md"),
        "--cascade-only",
        "b.md",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert (
        "docs: archive: b.md has no editable metadata block; refusing before any write"
    ) in proc.stderr, proc.stderr
    assert _snapshot(root) == before


def test_cascade_only_occupied_destination_exits_1(docs_script, tmp_path):
    """Q4: an occupied archive slot keeps 1.x's exit **1**, and now refuses
    the WHOLE plan instead of dropping one document.

    RED reason: today the occupied slot only fails that one candidate — a
    `docs: could not archive b.md: …` line — while the primary is archived
    and the run exits 0.
    """
    root = tmp_path / "occupied"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "occupied"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: occupied\n"
    (root / "a.md").write_text(
        f"# A\n\n{hdr}Updated: 2026-01-01\n\nRelated:\n- pairs-with: b.md\n\n## Body\n\na.\n"
    )
    (root / "b.md").write_text(f"# B\n\n{hdr}Updated: 2026-01-02\n\n## Body\n\nb.\n")
    dated = root / _M26_DATED
    dated.mkdir(parents=True)
    (dated / "b.md").write_text(
        "# B\n\nLifecycle: archived\nRole: notes\nProject: occupied\n"
        f"Updated: {_M26_DATE}\nArchived-reason: earlier\n\n## Body\n\nolder b.\n"
    )
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "a.md"),
        "--cascade-only",
        "b.md",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert (
        f"docs: archive: archive destination already exists: {_M26_DATED}/b.md (for b.md); "
        "refusing before any write"
    ) in proc.stderr, proc.stderr
    assert _snapshot(root) == before


@_SKIP_AS_ROOT
def test_cascade_only_unwritable_candidate_refuses_with_exit_2(docs_script, tmp_path):
    """Q4 / D4: an unwritable plan member is a NEW M26 refusal, so it exits
    **2** and writes nothing.

    The check must be an explicit access test: `atomic_write` is tmpfile +
    rename, and POSIX `rename()` onto a read-only file succeeds when the
    directory is writable.

    RED reason: today the archive succeeds — exit 0 — precisely because the
    read-only mode is never consulted.
    """
    root = _two_relation_tree(tmp_path)
    (root / "beta.md").chmod(0o444)
    try:
        before = _snapshot(root)
        proc = _run(
            docs_script,
            "archive",
            str(root / "root.md"),
            "--cascade-only",
            "beta.md",
            "--date",
            _M26_DATE,
        )
        assert proc.returncode == 2, (proc.stdout, proc.stderr)
        assert (
            "docs: archive: beta.md is not writable; refusing before any write"
        ) in proc.stderr, proc.stderr
        assert _snapshot(root) == before
    finally:
        # At baseline the archive SUCCEEDS and beta.md has already moved, so
        # the restore must tolerate its absence — otherwise the cleanup's
        # FileNotFoundError masks this test's real RED reason.
        for candidate in (root / "beta.md", root / _M26_DATED / "beta.md"):
            if candidate.exists():
                candidate.chmod(0o644)


# --- M26 — D7 `docs archive --json` -----------------------------------------

_JSON_TOP_LEVEL_KEYS = [
    "primary",
    "date",
    "scope",
    "candidates",
    "dry_run",
    "applied",
    "index_refreshed",
]
_JSON_CANDIDATE_KEYS = {"path", "verb", "selected", "destination", "reason"}


def test_archive_json_preview_record_shape(docs_script, fixtures_dir, tmp_path):
    """D7: the preview record's exact shape — closed, ordered top-level key
    set and a fixed per-candidate key set.

    RED reason: `--json` is not a recognised flag on `archive` today
    (argparse: `unrecognized arguments: --json`, exit 2).
    """
    root = _tree(fixtures_dir, tmp_path, "archive-neighborhood")

    proc = _run(
        docs_script,
        "archive",
        str(root / "milestone.md"),
        "--cascade-dry-run",
        "--cascade-only",
        "milestone*",
        "--json",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert list(record) == _JSON_TOP_LEVEL_KEYS
    assert record["primary"] == {
        "source": str(root / "milestone.md"),
        "path": "milestone.md",
        "destination": f"{_M26_DATED}/milestone.md",
    }
    assert record["date"] == _M26_DATE
    assert record["scope"] == "milestone*"
    assert record["dry_run"] is True
    assert record["applied"] is False
    assert record["index_refreshed"] is False
    assert all(set(c) == _JSON_CANDIDATE_KEYS for c in record["candidates"])


def test_archive_json_apply_record_has_the_same_key_set(docs_script, fixtures_dir, tmp_path):
    """D7: a preview record and an apply record are DIFFABLE — identical key
    sets throughout, and identical values everywhere except the three state
    bits.

    RED reason: `--json` is not a recognised flag on `archive` today.
    """
    preview_root = _tree(fixtures_dir, tmp_path, "archive-neighborhood", into="preview")
    apply_root = _tree(fixtures_dir, tmp_path, "archive-neighborhood", into="apply")
    args = ("--cascade-only", "milestone*", "--json", "--date", _M26_DATE)

    preview_proc = _run(
        docs_script, "archive", str(preview_root / "milestone.md"), "--cascade-dry-run", *args
    )
    apply_proc = _run(docs_script, "archive", str(apply_root / "milestone.md"), *args)
    assert preview_proc.returncode == 0, preview_proc.stderr
    assert apply_proc.returncode == 0, apply_proc.stderr

    preview = json.loads(preview_proc.stdout)
    applied = json.loads(apply_proc.stdout)
    assert list(preview) == list(applied) == _JSON_TOP_LEVEL_KEYS
    assert [set(c) for c in preview["candidates"]] == [set(c) for c in applied["candidates"]]
    state = ("dry_run", "applied", "index_refreshed")
    preview_body = {k: v for k, v in preview.items() if k not in state and k != "primary"}
    applied_body = {k: v for k, v in applied.items() if k not in state and k != "primary"}
    assert preview_body == applied_body
    assert (preview["dry_run"], preview["applied"], preview["index_refreshed"]) == (
        True,
        False,
        False,
    )
    assert (applied["dry_run"], applied["applied"], applied["index_refreshed"]) == (
        False,
        True,
        True,
    )


def test_archive_json_names_every_candidate_with_selected_and_reason(
    docs_script, fixtures_dir, tmp_path
):
    """D7: every candidate carries `selected` and, when excluded, a
    machine-stable `reason` — `destination` non-null iff selected, `reason`
    null iff selected.

    RED reason: `--json` is not a recognised flag on `archive` today.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-archived-neighbour")

    proc = _run(
        docs_script,
        "archive",
        str(root / "plan.md"),
        "--cascade-dry-run",
        "--cascade-only",
        "log.md",
        "--json",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert record["candidates"] == [
        {
            "path": "log.md",
            "verb": "pairs-with",
            "selected": True,
            "destination": f"{_M26_DATED}/log.md",
            "reason": None,
        },
        {
            "path": "archive/2026-01-01/old.md",
            "verb": "pairs-with",
            "selected": False,
            "destination": None,
            "reason": "already-archived",
        },
    ]


def test_archive_json_stdout_is_exactly_one_object(docs_script, fixtures_dir, tmp_path):
    """D7: stdout carries ONE JSON object and nothing else; the human summary
    stays on stderr so `--json` output is byte-clean for a pipe.

    RED reason: `--json` is not a recognised flag on `archive` today.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-neighborhood")

    proc = _run(
        docs_script,
        "archive",
        str(root / "milestone.md"),
        "--cascade-only",
        "milestone*",
        "--json",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    json.loads(proc.stdout)  # raises if stdout is not exactly one object
    assert "docs:" not in proc.stdout, proc.stdout
    assert "docs: archive:" in proc.stderr, "the human summary belongs on stderr"


@pytest.mark.parametrize(
    ("extra", "expected"),
    [
        pytest.param(["--cascade"], _retirement_message("--cascade"), id="retired-flag"),
        pytest.param(
            ["--cascade-only", "typo-*"],
            "docs: archive: --cascade-only 'typo-*' matched none of the 6 one-hop "
            "candidate(s); refusing before any write",
            id="none-matched",
        ),
        pytest.param(
            ["--cascade-only", ""],
            "docs: archive: --cascade-only must not be empty",
            id="empty-scope",
        ),
    ],
)
def test_archive_json_emits_no_record_on_a_refusal(
    docs_script, fixtures_dir, tmp_path, extra, expected
):
    """D7 (Phase-1 Q3): a refusal emits NO record — the exit code plus the
    stderr message is the contract, exactly as M25 pinned for
    `docs relate`.

    The contract message is asserted, and argparse's own error is asserted
    ABSENT. Without that this test would be **falsely GREEN**: `--json` is an
    unrecognized argument today, so argparse already exits 2 with an empty
    stdout and an untouched tree, satisfying every other assertion here for
    entirely the wrong reason. (Caught at the Phase-4 baseline.)

    RED reason: `--json` is not a recognised flag on `archive` today, and none
    of these three invocations refuses on M26's terms.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-neighborhood")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "milestone.md"),
        *extra,
        "--json",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert expected in proc.stderr, proc.stderr
    assert "unrecognized arguments" not in proc.stderr, (
        "this must be the M26 refusal, not argparse rejecting an unknown --json"
    )
    assert proc.stdout == "", proc.stdout
    assert _snapshot(root) == before


def test_archive_json_of_a_primary_only_archive_lists_candidates_as_not_selected(
    docs_script, fixtures_dir, tmp_path
):
    """D7 (Phase-1 Q14): a plain `docs archive FILE --json` still carries the
    WHOLE candidate set, each one `selected: false` / `reason:
    "not-selected"`.

    D1's quiet rule governs stderr prose; the record's consumer is the agent
    deciding whether a selection is correct, and it must be able to see the
    neighborhood it just declined to touch.

    RED reason: `--json` is not a recognised flag on `archive` today.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-neighborhood")

    proc = _run(docs_script, "archive", str(root / "milestone.md"), "--json", "--date", _M26_DATE)

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert record["scope"] is None
    assert [c["path"] for c in record["candidates"]] == [
        "plan.md",
        "milestone-impl.md",
        "cli.md",
        "convention.md",
        "test-strategy.md",
        "status.md",
    ]
    assert all(c["selected"] is False for c in record["candidates"])
    assert all(c["reason"] == "not-selected" for c in record["candidates"])
    assert all(c["destination"] is None for c in record["candidates"])
    # …and the prose stays quiet about them (setup Q7).
    assert "candidate" not in proc.stderr


def test_archive_json_records_index_refreshed(docs_script, fixtures_dir, tmp_path):
    """D7: the record reports the end-of-batch reindex state, so a caller can
    tell a complete run from one that moved documents and then failed to
    refresh `INDEX.md`.

    RED reason: `--json` is not a recognised flag on `archive` today.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-duplicate-edge")

    proc = _run(
        docs_script,
        "archive",
        str(root / "a.md"),
        "--cascade-only",
        "b.md",
        "--json",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert record["applied"] is True
    assert record["dry_run"] is False
    assert record["index_refreshed"] is True
    assert f"{_M26_DATED}/a.md" in (root / "INDEX.md").read_text()


def _mixed_eligibility_tree(tmp_path: Path) -> Path:
    """`a.md` with one eligible, one unresolved, and one escaping candidate."""
    root = tmp_path / "mixed"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "mixed"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: mixed\n"
    (root / "b.md").write_text(f"# B\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\nb.\n")
    (tmp_path / "escape.md").write_text(
        "# Escape\n\nLifecycle: active\nRole: notes\nProject: other\nUpdated: 2026-01-01\n"
    )
    (root / "a.md").write_text(
        f"# A\n\n{hdr}Updated: 2026-01-02\n\n"
        "Related:\n- pairs-with: b.md\n- pairs-with: ghost.md\n"
        "- pairs-with: ../escape.md\n\n## Body\n\na.\n"
    )
    return root


def test_preview_names_the_unresolved_and_outside_root_ineligibilities(docs_script, tmp_path):
    """D6 / D3: the two remaining ineligibility reasons get their own frozen
    preview lines, and both count as ineligible in the footer.

    `already-archived` is covered by
    `test_preview_names_an_ineligible_archived_candidate`; without this test
    the other two rendered lines would be unpinned and Phase 7 could word them
    however it liked. An escaping candidate is named by its canonical
    root-relative form, escape included.

    RED reason: no candidate-state vocabulary exists today; a non-resolving
    target is silently dropped by `_cascade_set`'s `is_file()` filter and an
    escaping one is dropped the same way, so neither is ever reported.
    """
    root = _mixed_eligibility_tree(tmp_path)
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "a.md"),
        "--cascade-dry-run",
        "--cascade-only",
        "b.md",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (f"docs: archive: candidate b.md — selected -> {_M26_DATED}/b.md") in proc.stderr, (
        proc.stderr
    )
    assert (
        "docs: archive: candidate ghost.md — ineligible (target does not resolve to a file)"
    ) in proc.stderr, proc.stderr
    assert (
        "docs: archive: candidate ../escape.md — ineligible (target resolves outside the docs root)"
    ) in proc.stderr, proc.stderr
    assert "docs: archive: 3 candidate(s): 1 selected, 0 not selected, 2 ineligible" in proc.stderr
    assert _snapshot(root) == before


@pytest.mark.parametrize(
    "case",
    [
        pytest.param("missing-file", id="missing-file"),
        pytest.param("bad-date", id="bad-date"),
        pytest.param("malformed-primary", id="malformed-primary"),
    ],
)
def test_archive_retired_flag_is_checked_before_any_filesystem_access(docs_script, tmp_path, case):
    """D2 (Phase-1 Q11): the retirement check runs FIRST — immediately after
    argument parsing, before any filesystem access — so it wins over a missing
    file, a malformed `--date`, and a primary that does not parse.

    Without this ordering the refusal would be conditional on the tree's
    state, which is exactly the "it depends" cell D2 exists to remove.

    RED reason: today `_cmd_archive` checks the file, the config, the date and
    the primary's metadata before it ever looks at the cascade flags — a
    missing file exits 1 with `docs: file not found`, and a bad `--date`
    exits 2 with `docs: --date: …`.
    """
    root = _two_relation_tree(tmp_path)
    target = root / "root.md"
    args = ["--cascade"]
    if case == "missing-file":
        target = root / "no-such-doc.md"
    elif case == "bad-date":
        args += ["--date", "not-a-date"]
    else:
        target.write_text("no H1, no metadata block — unparseable.\n")

    proc = _run(docs_script, "archive", str(target), *args)

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert _retirement_message("--cascade") in proc.stderr, proc.stderr
    assert "file not found" not in proc.stderr
    assert "docs: --date:" not in proc.stderr


def test_quiet_silences_the_preview_but_never_a_refusal(docs_script, fixtures_dir, tmp_path):
    """`--quiet` gates the preview prose, and only the preview prose: a
    refusal is a failure, not output, so it prints regardless.

    The preview half is GREEN-degenerate today (`--quiet` already suppresses
    the whole cascade preview); the refusal half is the RED one and pins the
    rule for a NON-argparse refusal, complementing the retirement matrix's
    `--quiet` cell.

    RED reason: `--cascade-only 'typo-*'` does not refuse at all today — it
    archives the primary and exits 0.
    """
    quiet_root = _tree(fixtures_dir, tmp_path, "archive-neighborhood", into="quiet")
    before = _snapshot(quiet_root)
    preview = _run(
        docs_script,
        "archive",
        str(quiet_root / "milestone.md"),
        "--cascade-dry-run",
        "--quiet",
        "--date",
        _M26_DATE,
    )
    assert preview.returncode == 0, (preview.stdout, preview.stderr)
    assert "candidate" not in preview.stderr, preview.stderr
    assert "preview only" not in preview.stderr
    assert _snapshot(quiet_root) == before

    refuse_root = _tree(fixtures_dir, tmp_path, "archive-neighborhood", into="refuse")
    refuse_before = _snapshot(refuse_root)
    refusal = _run(
        docs_script,
        "archive",
        str(refuse_root / "milestone.md"),
        "--cascade-only",
        "typo-*",
        "--quiet",
        "--date",
        _M26_DATE,
    )
    assert refusal.returncode == 2, (refusal.stdout, refusal.stderr)
    assert (
        "docs: archive: --cascade-only 'typo-*' matched none of the 6 one-hop candidate(s); "
        "refusing before any write"
    ) in refusal.stderr, "a refusal prints even under --quiet"
    assert _snapshot(refuse_root) == refuse_before
