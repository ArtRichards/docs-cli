"""CLI end-to-end tests for `docs archive` (Phase 2 — written RED)."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

_M26_DATE = "2026-05-28"
_M26_DATED = f"archive/{_M26_DATE}"
_DIR_MARKER = b"\x00<directory>"

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

    Directories are recorded too, with a marker value: a refusal that had
    already `mkdir`\'d `archive/<date>/` before aborting left the tree
    observably changed, and a files-only snapshot would call that
    byte-identical.
    """
    return {
        p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else _DIR_MARKER)
        for p in sorted(root.rglob("*"))
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

    `parents=True` because callers that need a FRESH tree inside one test
    pass a per-case subdirectory of `tmp_path` that does not exist yet (see
    `test_archive_help_still_registers_the_retired_flags`); for the usual
    caller, which passes `tmp_path` itself, it is a no-op.
    """
    root = tmp_path / "two-rel"
    root.mkdir(parents=True)
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
    # BARE `--cascade`, not `--cascade-only` / `--cascade-dry-run` satisfying a
    # substring test, and both flags marked — one global "retired" would not
    # prove the second one is.
    assert re.search(r"--cascade(?![-\w])", help_proc.stdout), help_proc.stdout
    assert "--interactive" in help_proc.stdout
    assert help_proc.stdout.lower().count("retired") >= 2, (
        "--help must mark BOTH retired flags as removed and name the replacement:\n"
        + help_proc.stdout
    )
    assert "--cascade-dry-run" in help_proc.stdout
    assert "--cascade-only" in help_proc.stdout

    # A fresh tree per flag: the first invocation must not be able to mutate
    # the tree the second one runs against.
    for flag in ("--cascade", "--interactive"):
        root = _two_relation_tree(tmp_path / flag.strip("-"))
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
    assert not (root / "archive").exists(), "not even the dated directory is created"


def test_cascade_only_excludes_an_archived_neighbour(docs_script, fixtures_dir, tmp_path):
    """E4 / D3: an already-archived candidate is excluded — its bytes, its
    path, and its `Updated:` value are untouched — while the eligible
    candidate is archived normally.

    **The boundary against M18 is the point of this test.** `old.md` carries
    `- references: plan.md`, and `plan.md` is the primary moving in this very
    operation, so M18 — D1 leg 2 REQUIRES that one bullet to be repointed to
    the new archive path or it would dangle as a `broken-ref`. M26 excludes
    `old.md` from the archive PLAN; it does not switch off the referring-edge
    rewrite. So the assertions below are: the file did not move, and its
    `Lifecycle:`, `Updated:`, `Archived-reason:`, H1 and prose are unchanged —
    AND the M18 rewrite still happened — AND `docs check` is clean afterwards.

    A blanket `read_bytes() == before` assertion would be **unsatisfiable**,
    and the cheapest way to satisfy it would be to suppress the rewrite for
    ineligible archived candidates, leaving a dangling edge no other test
    catches (`test_archive_repoints_already_archived_referrer` archives with
    no candidates at all).

    RED reason: today `--cascade-only '*'` matches the archive-subtree target
    too, so `archive/2026-01-01/old.md` is relocated to
    `archive/<date>/old.md` with `Updated:` rewritten. That is data
    corruption, not merely over-reach.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-archived-neighbour")
    archived = root / "archive" / "2026-01-01" / "old.md"
    before = archived.read_text()

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
    assert not (root / _M26_DATED / "old.md").exists()
    after = archived.read_text()
    # History is immutable: everything that says WHEN and WHY it was archived,
    # and everything a reader would quote, is byte-stable.
    for line in (
        "Lifecycle: archived",
        "Updated: 2026-01-01",
        "Archived-reason: superseded by the current plan",
        "# Old",
    ):
        assert line in after, f"{line!r} must survive verbatim:\n{after}"
    assert after.split("## Body", 1)[1] == before.split("## Body", 1)[1], (
        "the archived doc's prose is untouched"
    )
    # …but M18 — D1 leg 2 still applies: the one bullet pointing at the moving
    # primary IS repointed, so the archive subtree keeps resolving.
    assert f"- references: {_M26_DATED}/plan.md" in after, after
    assert "- references: plan.md\n" not in after, after

    assert (root / _M26_DATED / "plan.md").is_file()
    assert (root / _M26_DATED / "log.md").is_file()
    assert (
        "docs: archive: candidate archive/2026-01-01/old.md — ineligible (already archived)"
    ) in proc.stderr, proc.stderr
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


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
    assert not (root / "archive").exists(), "not even the dated directory is created"


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
    "mode",
    [pytest.param([], id="write"), pytest.param(["--cascade-dry-run"], id="preview")],
)
@pytest.mark.parametrize(
    "pattern",
    [pytest.param("", id="empty"), pytest.param("# just a comment", id="comment-only")],
)
def test_cascade_only_empty_pattern_refuses(docs_script, tmp_path, pattern, mode):
    """D5 (Phase-1 Q9): a pattern that compiles to nothing is its own refusal,
    on the M25 `--reason must not be empty` precedent.

    The refusal is **unconditional, a preview included** (conductor-resolved).
    D6's "a preview never fails" governs a VALID glob that selects nothing —
    a selection outcome, which stays exit 0 and is named loudly. A blank or
    comment-only pattern is a MALFORMED INVOCATION, refused at check-order
    step 2 before any candidate work, like any other bad argument. Without
    the `preview` parametrization the intersection of D5 and D6 would be
    undetermined.

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
        *mode,
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

# M28 (K): the closed key set widens by EXACTLY two, inserted after
# `candidates`. Updating this expected value is contract-mandated, not a
# relaxation: item (K) forbids omitting an empty array, so the two ids below
# now pin a TEN-key closed set — a strictly stronger assertion than the
# eight-key one, and the only edit that keeps them honest.
# `tests/test_archive_plan.py::_TOP_LEVEL_KEYS` is deliberately NOT touched:
# `archive_plan_to_json`'s `move_plan` parameter defaults to None, so a direct
# caller with no rewrite plan still sees the M26 key set.
_JSON_TOP_LEVEL_KEYS = [
    "primary",
    "date",
    "scope",
    "reason",
    "candidates",
    "rewrites",
    "strands",
    "dry_run",
    "applied",
    "index_refreshed",
]
_JSON_CANDIDATE_KEYS = {"path", "verb", "selected", "destination", "exclusion_reason"}


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
    assert record["reason"] is None
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
    # `primary` is compared separately because `source` carries the FILE
    # argument as typed and the two runs use different tmp roots — but its
    # VALUE must still be asserted on the apply side, or an implementation
    # returning `"destination": null` once the move has happened would pass.
    assert applied["primary"] == {
        "source": str(apply_root / "milestone.md"),
        "path": "milestone.md",
        "destination": f"{_M26_DATED}/milestone.md",
    }
    assert preview["primary"]["path"] == applied["primary"]["path"]
    assert preview["primary"]["destination"] == applied["primary"]["destination"]
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
            "exclusion_reason": None,
        },
        {
            "path": "archive/2026-01-01/old.md",
            "verb": "pairs-with",
            "selected": False,
            "destination": None,
            "exclusion_reason": "already-archived",
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

    **Re-pointed at `_two_relation_tree` in M28 Phase 7.** The subject of this
    lock is the APPLY-path record of a primary-only archive, and that subject
    is preserved exactly. The tree changed because `archive-neighborhood`'s
    `milestone-impl.md` is still active and declares `child-of: milestone.md`,
    so archiving `milestone.md` alone now — correctly — refuses on the
    strand-check's leg 1 before any write; that refusal has its own lock in
    `test_archive_primary_only_leg_1_refuses_on_a_live_child` below. Here
    `root.md` is the primary, its two one-hop candidates report `not-selected`,
    and its own `child-of: beta.md` is exempt because the DECLARER is the plan
    member. Deliberately not `--dry-run`: that would weaken an apply-path lock
    into a preview-path one.
    """
    root = _two_relation_tree(tmp_path)

    proc = _run(docs_script, "archive", str(root / "root.md"), "--json", "--date", _M26_DATE)

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert record["scope"] is None
    assert record["applied"] is True, "the subject is the APPLY-path record"
    assert [c["path"] for c in record["candidates"]] == ["sub/alpha.md", "beta.md"]
    assert all(c["selected"] is False for c in record["candidates"])
    assert all(c["exclusion_reason"] == "not-selected" for c in record["candidates"])
    assert all(c["destination"] is None for c in record["candidates"])
    # …and the prose stays quiet about them (setup Q7).
    assert "candidate" not in proc.stderr


def test_archive_primary_only_leg_1_refuses_on_a_live_child(docs_script, fixtures_dir, tmp_path):
    """M28 — D6 leg 1 on the M26-era `archive-neighborhood` tree, at the shape
    that used to complete: a plain `docs archive FILE`.

    `milestone-impl.md` is still active and declares `child-of: milestone.md`,
    so archiving the milestone alone would archive a parent out from under a
    live child — precisely the harm leg 1 exists to prevent, and precisely the
    behaviour change D8 calls out as breaking. The scenario is too good a
    leg-1 witness to lose when
    `test_archive_json_of_a_primary_only_archive_lists_candidates_as_not_selected`
    is re-pointed away from this tree, so it is pinned here in its own right —
    on a tree M26 authored, with no body links anywhere in it, which proves
    leg 1 does not depend on the `movelink-*` family.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-neighborhood")
    before = _snapshot(root)

    proc = _run(docs_script, "archive", str(root / "milestone.md"), "--json", "--date", _M26_DATE)

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert (
        "docs: archive: milestone-impl.md is still active and declares "
        "'child-of: milestone.md', which this operation would archive; "
        "refusing before any write" in proc.stderr
    )
    assert (
        "docs: archive: 1 still-active child(ren) would be stranded; zero bytes written"
        in proc.stderr
    )
    assert proc.stdout == "", "no --json record on a refusal (M26's frozen rule)"
    assert _snapshot(root) == before


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
    assert "would archive" not in preview.stderr, (
        "cli.md gates ALL preview prose on `not --quiet`, the primary line included"
    )
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


# --- M26 — post-review locks ------------------------------------------------


def _locked_candidate_tree(tmp_path: Path) -> tuple[Path, Path]:
    """A plan whose candidate passes the pre-flight but fails mid-execution.

    `locked/b.md` is mode `0o644` inside a `0o555` directory: an explicit
    `os.access(file, W_OK)` test returns **True** — so D4's writability
    pre-flight legitimately passes — while `atomic_write` raises
    `PermissionError` creating its `.docs-tmp` sibling. This is the same
    portable trigger `_readonly_referrer_tree` uses for the M14 (A4) guard.

    Returns (root, locked_dir) so the caller can restore the mode.
    """
    root = tmp_path / "midfail"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "midfail"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: midfail\n"
    (root / "a.md").write_text(
        f"# A\n\n{hdr}Updated: 2026-01-01\n\nRelated:\n- pairs-with: locked/b.md\n\n## Body\n\na.\n"
    )
    locked = root / "locked"
    locked.mkdir()
    (locked / "b.md").write_text(f"# B\n\n{hdr}Updated: 2026-01-02\n\n## Body\n\nb.\n")
    locked.chmod(0o555)
    return root, locked


@_SKIP_AS_ROOT
def test_mid_execution_failure_admits_the_partial_state(docs_script, tmp_path):
    """D4 residual: an unexpected `OSError` DURING execution is admitted
    exactly — naming what moved and what did not — at exit 2, with no `--json`
    record, and is **not** rolled back.

    The Step-1 baseline recorded this as unreachable from a subprocess test;
    that was wrong, and the fresh-eyes review disproved it. A member at mode
    `0o644` inside a `0o555` directory passes `os.access(..., W_OK)` and still
    breaks `atomic_write`, so the pre-flight legitimately admits the plan and
    execution fails on the second member. Without this test the whole
    matrix row — exit code, the `docs: archive: ` prefix, and the empty
    stdout — is unpinned.

    The `<err>` text is the OS's and carries an absolute path, so it is the
    one span not asserted verbatim; everything either side of it is.

    RED reason: today there is no plan and no admission — the cascade loop
    catches the `OSError` per candidate, prints
    `docs: could not archive locked/b.md: …`, and the run exits **0**.
    """
    root, locked = _locked_candidate_tree(tmp_path)
    try:
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

        assert proc.returncode == 2, (proc.stdout, proc.stderr)
        assert "docs: archive: write failed for locked/b.md: " in proc.stderr, proc.stderr
        assert (
            "; PARTIAL ARCHIVE — not rolled back. "
            f"Archived: a.md -> {_M26_DATED}/a.md. "
            "Still at their original paths: locked/b.md. Repair manually."
        ) in proc.stderr, proc.stderr
        assert proc.stdout == "", "a partial-state admission emits no --json record"
        assert "Traceback" not in proc.stderr
        # The admission is checkable against the disk, exactly as written.
        assert (root / _M26_DATED / "a.md").is_file()
        assert not (root / "a.md").exists()
        assert (locked / "b.md").is_file()
        assert not (root / _M26_DATED / "b.md").exists()
    finally:
        locked.chmod(0o755)


def _readonly_root_tree(tmp_path: Path) -> Path:
    """A tree whose docs are writable but whose ROOT is not.

    Every plan member lives in `w/` and the dated archive directory is
    pre-created, so the whole plan passes the pre-flight AND executes — and
    then the end-of-batch `atomic_write(root / "INDEX.md", …)` fails, because
    its `.docs-tmp` sibling cannot be created in the read-only root. That is
    the one post-write failure the contract singles out.
    """
    root = tmp_path / "roroot"
    (root / "w").mkdir(parents=True)
    (root / _M26_DATED).mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "roroot"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: roroot\n"
    (root / "w" / "a.md").write_text(
        f"# A\n\n{hdr}Updated: 2026-01-01\n\nRelated:\n- pairs-with: w/b.md\n\n## Body\n\na.\n"
    )
    (root / "w" / "b.md").write_text(
        f"# B\n\n{hdr}Updated: 2026-01-02\n\nRelated:\n- pairs-with: w/a.md\n\n## Body\n\nb.\n"
    )
    root.chmod(0o555)
    return root


@_SKIP_AS_ROOT
def test_archive_json_record_is_emitted_on_an_index_refresh_failure(docs_script, tmp_path):
    """D7 (Phase-1 Q3): the ONE documented exception to "no record on a
    refusal".

    An INDEX-refresh failure is a **post-write** failure — every document has
    already moved correctly — so the record IS emitted, with
    `"applied": true, "index_refreshed": false`, and the run exits 2. Without
    this lock the natural reading of "no record on a refusal" (suppress it on
    every non-zero exit) passes the whole suite.

    RED reason: `--json` is not a recognised flag on `archive` today
    (argparse: `unrecognized arguments: --json`, exit 2 with empty stdout).
    """
    root = _readonly_root_tree(tmp_path)
    try:
        proc = _run(
            docs_script,
            "archive",
            str(root / "w" / "a.md"),
            "--cascade-only",
            "b.md",
            "--json",
            "--date",
            _M26_DATE,
        )

        assert proc.returncode == 2, (proc.stdout, proc.stderr)
        assert "unrecognized arguments" not in proc.stderr, proc.stderr
        record = json.loads(proc.stdout)
        assert record["applied"] is True, "the documents really did move"
        assert record["index_refreshed"] is False
        assert record["dry_run"] is False
        # …and the disk agrees with the record.
        assert (root / _M26_DATED / "a.md").is_file()
        assert (root / _M26_DATED / "b.md").is_file()
        assert not (root / "INDEX.md").exists()
    finally:
        root.chmod(0o755)


def _outside_root_tree(tmp_path: Path) -> tuple[Path, Path]:
    """A docs root `w/` next to an `ext/` directory holding a foreign doc."""
    root = tmp_path / "w"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "w"\n\n[archive]\ndir = "archive"\n')
    outside = tmp_path / "ext"
    outside.mkdir()
    (outside / "real.md").write_text(
        "# Real\n\nLifecycle: active\nRole: notes\nProject: other\nUpdated: 2026-01-01\n"
        "\n## Body\n\nA doc that does not live in this tree.\n"
    )
    return root, outside


def test_primary_reached_through_a_symlink_out_of_the_tree_refuses(docs_script, tmp_path):
    """A primary that RESOLVES outside the root is refused before any write.

    Found by the Step-2 fresh-eyes review. `_root_relative` falls back to the
    bare filename for a path it cannot relativise, so without this check a
    symlink pointing out of the tree yielded a fabricated in-tree rel and the
    archive moved the FOREIGN file into this tree — leaving the symlink
    dangling and `INDEX.md` stale — before dying on the follow-up read. 1.x
    raised `ValueError` here and stopped, so this is a regression guard, at
    1.x's own exit 1 and in the wording `touch` / `stamp` / `project set` /
    `relate` already use.
    """
    root, outside = _outside_root_tree(tmp_path)
    (root / "link.md").symlink_to(outside / "real.md")
    before_outside = (outside / "real.md").read_bytes()

    proc = _run(docs_script, "archive", "link.md", cwd=root, stdin_text="")

    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "is outside the resolved docs root" in proc.stderr, proc.stderr
    assert "refusing before any write" in proc.stderr, proc.stderr
    assert proc.stdout == ""
    # The foreign file is untouched and was NOT moved into this tree.
    assert (outside / "real.md").read_bytes() == before_outside
    assert not (root / "archive").exists(), "not even the dated directory is created"
    assert (root / "link.md").is_symlink(), "the symlink must not be left dangling"


def test_primary_outside_an_explicit_root_refuses(docs_script, tmp_path):
    """The same refusal for the second shape: a `--root` naming a different
    tree than the file.

    This one was the more dangerous of the two — it exited **0**, moved the
    foreign document across the tree boundary, reported an in-tree rel on
    stderr and in the `--json` record, and left `docs check` reporting no
    violations: the silent, undetectable write E3 exists to eliminate.
    """
    root, outside = _outside_root_tree(tmp_path)
    before_outside = (outside / "real.md").read_bytes()

    proc = _run(
        docs_script,
        "archive",
        str(outside / "real.md"),
        "--root",
        str(root),
        "--json",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "is outside the resolved docs root" in proc.stderr, proc.stderr
    assert proc.stdout == "", "a refusal emits no --json record"
    assert (outside / "real.md").read_bytes() == before_outside
    assert (outside / "real.md").is_file(), "the foreign doc must not move"
    assert not (root / _M26_DATED).exists()
    assert not (root / "INDEX.md").exists(), "nothing was reindexed either"


@_SKIP_AS_ROOT
def test_unreadable_primary_exits_cleanly_without_a_traceback(docs_script, tmp_path):
    """An unreadable PRIMARY gets the same clean exit 2 as an unreadable plan
    member — never a traceback.

    Pre-existing behaviour in 1.x (which tracebacked too), but M26 had made it
    inconsistent: the audit fixed the member case and left the primary and the
    referring-doc walk raising. All three now share one rule — an unreadable
    file is `docs: archive: <exc>` at exit 2.
    """
    root = tmp_path / "roprimary"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "roprimary"\n\n[archive]\ndir = "archive"\n'
    )
    target = root / "a.md"
    target.write_text(
        "# A\n\nLifecycle: active\nRole: notes\nProject: roprimary\nUpdated: 2026-01-01\n"
        "\n## Body\n\na.\n"
    )
    before = _snapshot(root)
    target.chmod(0o000)
    try:
        proc = _run(docs_script, "archive", str(target), "--date", _M26_DATE)
    finally:
        target.chmod(0o644)

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "Traceback" not in proc.stderr, proc.stderr
    assert "docs: archive: " in proc.stderr, proc.stderr
    assert _snapshot(root) == before


@_SKIP_AS_ROOT
def test_unreadable_referring_doc_exits_cleanly_without_a_traceback(docs_script, tmp_path):
    """The third face of the same condition: an unreadable doc found by the
    whole-tree validation walk (M12 / M14 — A6).

    A MALFORMED referring doc stays exit 1 (unchanged since M12,
    `test_archive_referring_edge_rewrite_is_atomic`); an UNREADABLE one is not
    malformed, and gets the clean exit 2 the other two unreadable cases get.
    """
    root = tmp_path / "roreferrer"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "roreferrer"\n\n[archive]\ndir = "archive"\n'
    )
    hdr = "Lifecycle: active\nRole: notes\nProject: roreferrer\n"
    (root / "a.md").write_text(f"# A\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\na.\n")
    other = root / "other.md"
    other.write_text(f"# Other\n\n{hdr}Updated: 2026-01-02\n\n## Body\n\nother.\n")
    before = _snapshot(root)
    other.chmod(0o000)
    try:
        proc = _run(docs_script, "archive", str(root / "a.md"), "--date", _M26_DATE)
    finally:
        other.chmod(0o644)

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "Traceback" not in proc.stderr, proc.stderr
    assert "docs: archive: " in proc.stderr, proc.stderr
    assert _snapshot(root) == before, "the walk runs before any write"


def test_empty_reason_is_dropped_from_the_record(docs_script, tmp_path):
    """`--reason ""` leaves no `Archived-reason:` line, so the record must not
    claim one.

    `_archive_one`'s `if reason:` has always declined to write an empty
    `Archived-reason:`; carrying `""` into the `--json` record would make the
    record MISDESCRIBE the file it reports on, which is the one failure mode
    D7 exists to prevent. Refusing an empty `--reason` outright (the
    `docs relate` precedent) would add to the frozen message catalog and is
    deliberately left for M29.
    """
    root = _two_relation_tree(tmp_path)

    proc = _run(
        docs_script,
        "archive",
        str(root / "root.md"),
        "--reason",
        "",
        "--json",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert record["reason"] is None, "an empty --reason is not a reason"
    assert "Archived-reason:" not in (root / _M26_DATED / "root.md").read_text()


def test_two_spellings_of_one_edge_survive_the_rewrite_as_duplicate_bullets(docs_script, tmp_path):
    """DOCUMENTED CURRENT BEHAVIOUR, not an endorsement (M28 follow-up).

    A primary declaring the same candidate twice — `beta.md` and `./beta.md` —
    produces one `(alias, new_rel)` pair per declared spelling (Phase-1 Q5),
    which is what keeps a `./` bullet from dangling. Both bullets therefore
    repoint to the same new path, and the moved doc ends up carrying two
    byte-identical bullets.

    Every edge resolves and `docs check` is clean, so the cost is cosmetic.
    The fix is NOT local: the duplicate exists because two different
    `old_rel`s map to one `new_rel`, so suppressing it needs `Related:`-block
    aware editing rather than `rewrite_related_refs`' per-pair exact-match
    substitution — and dropping the alias pair instead would leave `./beta.md`
    dangling, which is strictly worse than a duplicate. Recorded as an M28
    follow-up (M28 reworks that rewriter for body links anyway). This test
    exists so the behaviour cannot change silently in either direction.
    """
    root = tmp_path / "dupspell"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "dupspell"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: dupspell\n"
    (root / "beta.md").write_text(f"# Beta\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\nb.\n")
    (root / "alpha.md").write_text(
        f"# Alpha\n\n{hdr}Updated: 2026-01-02\n\n"
        "Related:\n- pairs-with: beta.md\n- pairs-with: ./beta.md\n\n## Body\n\na.\n"
    )

    proc = _run(
        docs_script,
        "archive",
        str(root / "alpha.md"),
        "--cascade-only",
        "beta.md",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    moved = (root / _M26_DATED / "alpha.md").read_text()
    assert moved.count(f"- pairs-with: {_M26_DATED}/beta.md\n") == 2, (
        "both declared spellings are repointed — today that leaves two identical bullets"
    )
    assert "./beta.md" not in moved, "neither spelling is left dangling"
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


@_SKIP_AS_ROOT
def test_unreadable_plan_member_exits_cleanly_without_a_traceback(docs_script, tmp_path):
    """An existing but UNREADABLE plan member is a clean exit 2, never a
    traceback.

    Added by the Step-2 same-instance audit, which found the defect: the
    pre-flight's first proof calls `read_text()` on every member, so a `0o000`
    candidate raises `PermissionError` before its writability is ever tested —
    and `PermissionError` is an `OSError`, not a `CoordinatedWriteError`, so it
    escaped `_cmd_archive`'s refusal handler. This is not one of the five
    enumerated pre-flight refusals; it is the unenumerated read failure, and it
    gets the same mapping as the M14 (A4) rewrite failure: `docs: archive: …`
    at exit 2, with the tree untouched because the pre-flight writes nothing.
    """
    root = tmp_path / "unreadable"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "unreadable"\n\n[archive]\ndir = "archive"\n'
    )
    hdr = "Lifecycle: active\nRole: notes\nProject: unreadable\n"
    (root / "a.md").write_text(
        f"# A\n\n{hdr}Updated: 2026-01-01\n\nRelated:\n- pairs-with: b.md\n\n## Body\n\na.\n"
    )
    (root / "b.md").write_text(f"# B\n\n{hdr}Updated: 2026-01-02\n\n## Body\n\nb.\n")
    # Snapshotted BEFORE the chmod, and the mode restored before the
    # comparison: `_snapshot` reads every file, so it cannot read a 0o000 one.
    before = _snapshot(root)
    (root / "b.md").chmod(0o000)
    try:
        proc = _run(
            docs_script,
            "archive",
            str(root / "a.md"),
            "--cascade-only",
            "b.md",
            "--date",
            _M26_DATE,
        )
    finally:
        (root / "b.md").chmod(0o644)

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "Traceback" not in proc.stderr, proc.stderr
    assert "docs: archive: " in proc.stderr, proc.stderr
    assert proc.stdout == ""
    assert _snapshot(root) == before, "the pre-flight writes nothing"


def test_archive_json_source_is_the_file_argument_exactly_as_typed(
    docs_script, fixtures_dir, tmp_path
):
    """D7 (post-review finding 6): `primary.source` is the `FILE` argument
    **exactly as typed** — a relative argument stays relative — while `path`
    and `destination` are canonical root-relative.

    `archive_plan_to_json` only ever sees the plan, so the raw argument has to
    be threaded onto it; deriving `str(plan.primary.path)` would always be
    absolute. Every other `--json` test passes an absolute path, so all three
    of the specification's earlier readings passed.

    RED reason: `--json` is not a recognised flag on `archive` today.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-neighborhood")

    proc = _run(
        docs_script,
        "archive",
        "./milestone.md",
        "--cascade-dry-run",
        "--json",
        "--date",
        _M26_DATE,
        cwd=root,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert record["primary"]["source"] == "./milestone.md", record["primary"]
    assert record["primary"]["path"] == "milestone.md"
    assert record["primary"]["destination"] == f"{_M26_DATED}/milestone.md"


def test_archive_json_carries_the_reason_flag(docs_script, tmp_path):
    """D7 (post-review amendment A): the record carries `--reason` as a
    top-level `reason`, mirroring `relate --json`; the candidate-level field
    is `exclusion_reason`, so the two never collide.

    RED reason: `--json` is not a recognised flag on `archive` today.
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
        "--json",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert record["reason"] == "milestone closed out"
    assert all("reason" not in c for c in record["candidates"]), (
        "the candidate field is `exclusion_reason`; `reason` is the primary's"
    )
    assert all("exclusion_reason" in c for c in record["candidates"])
    # …and it really did land on the primary only (D1 / Q10).
    assert "Archived-reason: milestone closed out" in (root / _M26_DATED / "root.md").read_text()
    assert "Archived-reason:" not in (root / _M26_DATED / "beta.md").read_text()


@pytest.mark.parametrize(
    "mode",
    [pytest.param([], id="write"), pytest.param(["--cascade-dry-run"], id="preview")],
)
@pytest.mark.parametrize(
    "pattern",
    [pytest.param("!plan.md", id="negated"), pytest.param("!*", id="negated-glob")],
)
def test_cascade_only_negated_pattern_refuses(docs_script, fixtures_dir, tmp_path, pattern, mode):
    """D5 (post-review amendment C): a negated (`!`) scope is refused.

    `_compile_docsignore_pattern` returns a `negate` flag that 1.x's
    `_cascade_set` silently discarded, so `!plan.md` behaved as `plan.md` —
    the opposite of what it reads as. And the honest reading, "everything
    except X", is exactly the unbounded selection D1 exists to prevent.
    Refusing is the only answer consistent with "state the exact bounded
    selection the operator intends".

    Refused **in every mode, a preview included** (conductor-resolved), for
    the same reason as the empty pattern above: a negated glob is a malformed
    invocation, not a selection outcome, so D6's "a preview never fails" does
    not reach it.

    RED reason: today the negation bit is dropped, the pattern matches
    `plan.md`, and the run archives the primary plus `plan.md` at exit 0.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-neighborhood")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "milestone.md"),
        "--cascade-only",
        pattern,
        *mode,
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert (
        "docs: archive: --cascade-only does not support negated ('!') patterns; "
        "state the exact bounded selection"
    ) in proc.stderr, proc.stderr
    assert _snapshot(root) == before
    assert not (root / "archive").exists()


def test_preview_names_a_candidate_the_exclude_predicate_hides(docs_script, tmp_path):
    """D3 (Phase-1 Q8, BINDING) at the CLI: `[exclude]` / `.docsignore` govern
    the tree walks, not the primary's own declared edges, so an excluded
    target is still discovered, named, and selectable.

    The unit-seam lock is
    `test_archive_plan.py::test_candidate_scan_ignores_the_exclude_predicate`;
    this is the same rule through the real command.

    RED reason: no candidate-state vocabulary exists today.
    """
    root = tmp_path / "excl"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "excl"\n\n[archive]\ndir = "archive"\n\n[exclude]\ndirs = ["vendor"]\n'
    )
    hdr = "Lifecycle: active\nRole: notes\nProject: excl\n"
    (root / "vendor").mkdir()
    (root / "vendor" / "x.md").write_text(f"# X\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\nx.\n")
    (root / "a.md").write_text(
        f"# A\n\n{hdr}Updated: 2026-01-02\n\nRelated:\n- pairs-with: vendor/x.md\n\n## Body\n\na.\n"
    )

    proc = _run(
        docs_script,
        "archive",
        str(root / "a.md"),
        "--cascade-dry-run",
        "--cascade-only",
        "x.md",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (
        f"docs: archive: candidate vendor/x.md — selected -> {_M26_DATED}/x.md"
    ) in proc.stderr, proc.stderr
    assert "docs: archive: 1 candidate(s): 1 selected, 0 not selected, 0 ineligible" in proc.stderr


def test_none_matched_counts_ineligible_candidates_and_is_not_no_candidates(
    docs_script, fixtures_dir, tmp_path
):
    """D5: `<N>` is the size of the WHOLE deduplicated candidate set,
    ineligible members included, and a glob that hits only an ineligible
    candidate is "matched none" — not "no candidates".

    On the archived-neighbour fixture `old.md` matches `'old.md'` but is
    ineligible, so the selection is empty while two candidates exist. Both
    halves of `cli.md`'s "matched means SELECTED" sentence are pinned here.

    RED reason: today the archived neighbour is happily selected and archived,
    so the run exits 0.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-archived-neighbour")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "plan.md"),
        "--cascade-only",
        "old.md",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert (
        "docs: archive: --cascade-only 'old.md' matched none of the 2 one-hop candidate(s); "
        "refusing before any write"
    ) in proc.stderr, proc.stderr
    assert "has no one-hop pairs-with / child-of candidates" not in proc.stderr, (
        "two candidates exist — this is 'matched none', not 'no candidates'"
    )
    assert _snapshot(root) == before


def test_empty_scope_is_checked_before_the_filesystem(docs_script, tmp_path):
    """Check-order step 2: the `--cascade-only` shape test is purely lexical,
    so it precedes every filesystem access — including the missing-file check.

    RED reason: today `_cmd_archive` stats the file first and exits 1 with
    `docs: file not found`.
    """
    root = _two_relation_tree(tmp_path)

    proc = _run(
        docs_script,
        "archive",
        str(root / "no-such-doc.md"),
        "--cascade-only",
        "",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "docs: archive: --cascade-only must not be empty" in proc.stderr, proc.stderr
    assert "file not found" not in proc.stderr


def test_archived_primary_is_checked_before_the_selection(docs_script, fixtures_dir, tmp_path):
    """Check-order step 4: the archived-primary refusal precedes plan
    construction, so it wins over an empty selection.

    Both refusals exit 2, so without this the message an operator sees for an
    archived primary plus a typo'd scope would be undetermined — and the more
    fundamental fact (you are re-archiving history) is the one worth saying.

    RED reason: today neither condition refuses; the run re-archives the
    already-archived primary at exit 0.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-archived-neighbour")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "archive",
        str(root / "archive" / "2026-01-01" / "old.md"),
        "--cascade-only",
        "typo-*",
        "--date",
        _M26_DATE,
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert (
        "docs: archive: archive/2026-01-01/old.md is already under the archive subtree; "
        "refusing before any write"
    ) in proc.stderr, proc.stderr
    assert "matched none of the" not in proc.stderr
    assert "has no one-hop" not in proc.stderr
    assert _snapshot(root) == before


# --- M28 — move-safe body-link rewrites and the strand-check ---------------
#
# The contract under test is the milestone's *Decisions (Phase 1 — BINDING)*
# and `cli.md` › *Move-safe body-link rewrites (M28 — D1–D7)*. Every
# subprocess test below asserts a frozen contract string as well as an exit
# code, so an unrelated failure with the same code cannot satisfy it (M26's
# falsely-GREEN lesson).

_M28_DATE = "2026-08-15"
_M28_DATED = f"archive/{_M28_DATE}"


def _m28_tree(fixtures_dir: Path, tmp_path: Path, name: str) -> Path:
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


def _m28_snapshot(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def test_archive_single_document_repairs_both_classes(docs_script, fixtures_dir, tmp_path):
    """E2: one ordinary archive produces BOTH move classes, so both are
    repaired by the one formula — and a co-moving pair's link to each other is
    left byte-identical.
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-both")
    proc = _run(
        docs_script, "archive", "a.md", "--cascade-only", "b.md", "--date", _M28_DATE, cwd=root
    )
    assert proc.returncode == 0, proc.stderr

    moved = (root / _M28_DATED / "a.md").read_text()
    assert "[b](b.md)" in moved, "a co-moving sibling link keeps its bytes (the no-op rule)"
    assert "[c](../../c.md)" in moved, "class 2: the non-moving target is rebased"
    assert f"[a]({_M28_DATED}/a.md)" in (root / "c.md").read_text(), "class 1"

    assert _run(docs_script, "check", str(root)).returncode == 0


def test_closeout_leaves_the_tracker_links_resolving(docs_script, fixtures_dir, tmp_path):
    """E3: the real milestone-closeout invocation — the one M26 prescribes and
    `create-milestones` will prescribe — must leave the two most-read documents
    resolving, and `docs check` clean.
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-closeout")
    proc = _run(
        docs_script,
        "archive",
        "feature.md",
        "--cascade-only",
        "feature-*",
        "--date",
        _M28_DATE,
        "--reason",
        "milestone closed out",
        cwd=root,
    )
    assert proc.returncode == 0, proc.stderr

    status = (root / "status.md").read_text()
    assert f"[the feature]({_M28_DATED}/feature.md)" in status
    assert f"[its log]({_M28_DATED}/feature-impl.md)" in status
    assert f"[the feature]({_M28_DATED}/feature.md)" in (root / "plan.md").read_text()

    moved = (root / _M28_DATED / "feature.md").read_text()
    assert "[the log](feature-impl.md)" in moved, "the co-moving pair keeps its bytes"
    assert "[the plan](../../plan.md)" in moved, "class 2 two directories deeper"

    checked = _run(docs_script, "check", str(root))
    assert checked.returncode == 0, checked.stdout + checked.stderr


def test_archived_referrer_destination_is_repointed_and_nothing_else_changes(
    docs_script, fixtures_dir, tmp_path
):
    """E5 / D5: an already-archived referrer whose target moves has its
    destination repointed and NOTHING else changed — M18's shape, widened by
    exactly one token class (Q2/A2: no `Updated:` bump, no `Revision:`).
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-archived-referrer")
    archived = root / "archive" / "2026-01-01" / "old-log.md"
    before = archived.read_text()

    proc = _run(docs_script, "archive", "plan.md", "--date", _M28_DATE, cwd=root)
    assert proc.returncode == 0, proc.stderr

    after = archived.read_text()
    expected = before.replace("(../../plan.md)", f"(../{_M28_DATE}/plan.md)").replace(
        "- references: plan.md", f"- references: {_M28_DATED}/plan.md"
    )
    assert after == expected, "only the moving destination and its bullet may change"
    assert "Revision:" not in after
    assert "Updated: 2026-01-01" in after
    assert _run(docs_script, "check", str(root)).returncode == 0


def test_archive_leg_1_refuses_and_writes_zero_bytes(docs_script, fixtures_dir, tmp_path):
    """D6 leg 1: a parent archived out from under its live children refuses
    before any write, one line per orphaned pair naming BOTH ends, then a
    count — and the whole tree is byte-identical afterwards.
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-strand")
    before = _m28_snapshot(root)
    proc = _run(docs_script, "archive", "plan.md", "--date", _M28_DATE, "--json", cwd=root)

    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
    assert (
        "docs: archive: live-child.md is still active and declares 'child-of: plan.md', "
        "which this operation would archive; refusing before any write" in proc.stderr
    )
    assert (
        "docs: archive: milestone.md is still active and declares 'child-of: plan.md', "
        "which this operation would archive; refusing before any write" in proc.stderr
    )
    assert (
        "docs: archive: 2 still-active child(ren) would be stranded; zero bytes written"
        in proc.stderr
    )
    assert proc.stdout == "", "no --json record on a refusal (M26's frozen rule)"
    assert _m28_snapshot(root) == before


def test_archive_leg_1_refuses_even_under_quiet(docs_script, fixtures_dir, tmp_path):
    """Every refusal prints even under `--quiet` (M26's rule, unchanged): a
    silent refusal would leave an agent with an exit code and nothing to act on.
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-strand")
    proc = _run(docs_script, "archive", "plan.md", "--date", _M28_DATE, "--quiet", cwd=root)

    assert proc.returncode == 2
    assert (
        "docs: archive: live-child.md is still active and declares 'child-of: plan.md', "
        "which this operation would archive; refusing before any write" in proc.stderr
    )
    assert (
        "docs: archive: 2 still-active child(ren) would be stranded; zero bytes written"
        in proc.stderr
    )
    assert "docs: archive: would archive" not in proc.stderr, (
        "--quiet still suppresses the ordinary prose; only the refusal survives"
    )


def test_archive_leg_1_preview_reports_the_verdict_at_exit_0(docs_script, fixtures_dir, tmp_path):
    """D6: a preview REPORTS leg 1 rather than adopting it — and it does so on a
    plain `--dry-run`, not only behind a cascade flag, because leg 1 applies to
    all three archive shapes (D1's quiet rule governs CANDIDATE prose only).
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-strand")
    before = _m28_snapshot(root)
    proc = _run(docs_script, "archive", "plan.md", "--date", _M28_DATE, "--dry-run", cwd=root)

    assert proc.returncode == 0, proc.stderr
    assert (
        "docs: archive: would strand live-child.md — still active, declares "
        "'child-of: plan.md'; a write would refuse" in proc.stderr
    )
    assert (
        "docs: archive: would strand milestone.md — still active, declares "
        "'child-of: plan.md'; a write would refuse" in proc.stderr
    )
    assert "docs: archive: 2 still-active child(ren) would be stranded" in proc.stderr
    assert _m28_snapshot(root) == before


def test_every_preview_ends_by_saying_it_wrote_nothing(docs_script, fixtures_dir, tmp_path):
    """A preview must always end on the sentence that says nothing happened.

    M26 gated `preview only — nothing was written` on a cascade flag because a
    plain `--dry-run` printed a single line and a disclaimer under it was noise.
    Since M28 that same preview prints the rewrite lines, the counts footer,
    both strand blocks and possibly `a write would refuse` — so the M26
    rationale is void, and a reader who never reaches the disclaimer is left
    with exactly the ambiguity this milestone exists to remove.

    Both shapes are asserted, and the line is asserted LAST in each: a preview
    that announced itself in the middle of its own plan would be worse than one
    that did not announce itself at all.
    """
    for flag in ("--dry-run", "--cascade-dry-run"):
        root = _m28_tree(fixtures_dir, tmp_path / flag.strip("-"), "movelink-closeout")
        before = _m28_snapshot(root)
        proc = _run(docs_script, "archive", "feature.md", "--date", _M28_DATE, flag, cwd=root)

        assert proc.returncode == 0, (flag, proc.stderr)
        lines = proc.stderr.splitlines()
        assert lines[-1] == "docs: archive: preview only — nothing was written", (
            f"{flag}: the preview must END on the disclaimer, got {lines[-1]!r}"
        )
        assert sum(1 for ln in lines if "preview only" in ln) == 1, "exactly once"
        assert any(ln.startswith("docs: archive: rewrite ") for ln in lines), (
            "the fixture must make this a preview with real content to disclaim"
        )
        assert _m28_snapshot(root) == before


def test_archive_leg_1_preview_pair_is_suppressed_by_quiet(docs_script, fixtures_dir, tmp_path):
    """(L) splits the two leg-1 pairs, and `--quiet` is where the split is
    observable: the PREVIEW pair is a report, so `--quiet` silences it, while
    the WRITE path's pair is a refusal and survives (pinned above).

    Without this the split is invisible to the suite — the existing `--quiet`
    locks run on a refusal (which has no preview pair) and on a completing
    apply (whose plan has no orphans at all), so an implementation that put
    the preview pair in the verb beside the refusal would pass both.
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-strand")
    before = _m28_snapshot(root)
    proc = _run(
        docs_script, "archive", "plan.md", "--date", _M28_DATE, "--dry-run", "--quiet", cwd=root
    )

    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stderr == "", (
        "a preview reports rather than refuses, so --quiet silences ALL of it — "
        f"the leg-1 `would strand` pair included; got {proc.stderr!r}"
    )
    assert _m28_snapshot(root) == before


def test_legitimate_closeout_completes_despite_still_active_referrers(
    docs_script, fixtures_dir, tmp_path
):
    """The leg-1 over-fire lock at the CLI seam (A1). E7 measured the literal
    predicate refusing this repository's own standard closeout; the narrowed
    predicate must let a scoped closeout through even though two still-active
    references — the roadmap's `parent-of` bullet and its body link — point
    into the archived set.
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-strand")
    proc = _run(
        docs_script,
        "archive",
        "milestone.md",
        "--cascade-only",
        "milestone-*",
        "--date",
        _M28_DATE,
        cwd=root,
    )

    assert proc.returncode == 0, proc.stderr
    assert "would be stranded" not in proc.stderr
    assert "refusing before any write" not in proc.stderr
    assert (root / _M28_DATED / "milestone.md").is_file()
    assert (root / _M28_DATED / "milestone-impl.md").is_file()
    assert _run(docs_script, "check", str(root)).returncode == 0


def test_strand_report_names_both_ends_on_stderr_in_preview_and_apply(
    docs_script, fixtures_dir, tmp_path
):
    """D6 leg 2: every still-active inbound reference is named — both ends —
    on stderr, in the preview AND in the apply output, in the frozen
    deterministic order (walk order; bullets before body links within one
    referrer).
    """
    expected = [
        "docs: archive: strand plan.md — still active, 'parent-of: feature.md'",
        "docs: archive: strand plan.md:13 — still active, links to feature.md",
        "docs: archive: strand status.md — still active, 'pairs-with: feature.md'",
        "docs: archive: strand status.md:13 — still active, links to feature.md",
        "docs: archive: strand status.md:13 — still active, links to feature-impl.md",
        "docs: archive: 5 still-active inbound reference(s) into the archived set",
    ]
    args = ("archive", "feature.md", "--cascade-only", "feature-*", "--date", _M28_DATE)

    preview_root = _m28_tree(fixtures_dir, tmp_path / "a", "movelink-closeout")
    apply_root = _m28_tree(fixtures_dir, tmp_path / "b", "movelink-closeout")
    preview = _run(docs_script, *args, "--cascade-dry-run", cwd=preview_root)
    applied = _run(docs_script, *args, cwd=apply_root)

    assert preview.returncode == 0, preview.stderr
    assert applied.returncode == 0, applied.stderr
    for line in expected:
        assert line in preview.stderr, f"missing from the preview: {line}"
        assert line in applied.stderr, f"missing from the apply output: {line}"

    for stream, label in ((preview.stderr, "preview"), (applied.stderr, "apply")):
        observed = [ln for ln in stream.splitlines() if ln.startswith("docs: archive: strand ")]
        assert observed == expected[:5], (
            f"the {label} order is frozen: walk order, bullets before body links"
        )


def test_archive_rewrite_section_is_identical_in_preview_and_apply(
    docs_script, fixtures_dir, tmp_path
):
    """The rewrite lines and the counts footer are the same in both modes — a
    scoped write is all-or-nothing, so the plan IS what happened.
    """
    expected = [
        "docs: archive: rewrite feature.md:16 plan.md -> ../../plan.md",
        f"docs: archive: rewrite plan.md:13 feature.md -> {_M28_DATED}/feature.md",
        f"docs: archive: rewrite status.md:13 feature.md -> {_M28_DATED}/feature.md",
        f"docs: archive: rewrite status.md:13 feature-impl.md -> {_M28_DATED}/feature-impl.md",
        "docs: archive: 4 destination(s) in 3 document(s) rebased",
    ]
    args = ("archive", "feature.md", "--cascade-only", "feature-*", "--date", _M28_DATE)

    preview_root = _m28_tree(fixtures_dir, tmp_path / "a", "movelink-closeout")
    apply_root = _m28_tree(fixtures_dir, tmp_path / "b", "movelink-closeout")
    before = _m28_snapshot(preview_root)
    preview = _run(docs_script, *args, "--cascade-dry-run", cwd=preview_root)
    applied = _run(docs_script, *args, cwd=apply_root)

    assert preview.returncode == 0, preview.stderr
    assert applied.returncode == 0, applied.stderr
    assert _m28_snapshot(preview_root) == before, (
        "a COMPLETING preview writes zero bytes — every other snapshot lock in "
        "this file is on a REFUSAL path, so without this a preview that applied "
        "its own rewrite plan and then declined to move the files would pass"
    )
    rewrite_lines = [
        ln
        for ln in preview.stderr.splitlines()
        if ln.startswith("docs: archive: rewrite ") or "destination(s) in" in ln
    ]
    assert rewrite_lines == expected
    assert [
        ln
        for ln in applied.stderr.splitlines()
        if ln.startswith("docs: archive: rewrite ") or "destination(s) in" in ln
    ] == expected


def test_archive_json_top_level_keys_widen_by_exactly_rewrites_and_strands(
    docs_script, fixtures_dir, tmp_path
):
    """K: the closed key set widens by exactly two, inserted after
    `candidates`, and nothing else moves.
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-closeout")
    proc = _run(
        docs_script,
        "archive",
        "feature.md",
        "--cascade-only",
        "feature-*",
        "--date",
        _M28_DATE,
        "--json",
        "--cascade-dry-run",
        cwd=root,
    )
    assert proc.returncode == 0, proc.stderr

    record = json.loads(proc.stdout)
    assert list(record) == [
        "primary",
        "date",
        "scope",
        "reason",
        "candidates",
        "rewrites",
        "strands",
        "dry_run",
        "applied",
        "index_refreshed",
    ]


def test_archive_json_strands_present_for_a_plan_that_completes(
    docs_script, fixtures_dir, tmp_path
):
    """Leg 2's report is delivered to the CALLER, in a form it can parse —
    which is the half that answers issue #1's actual complaint — and it is
    present on a plan that COMPLETES, not only on one that refuses.
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-closeout")
    proc = _run(
        docs_script,
        "archive",
        "feature.md",
        "--cascade-only",
        "feature-*",
        "--date",
        _M28_DATE,
        "--json",
        cwd=root,
    )
    assert proc.returncode == 0, proc.stderr

    record = json.loads(proc.stdout)
    assert "strands" in record, "`strands` is present in every record, never missing"
    assert record["applied"] is True
    observed = [
        (s["path"], s["target"], s["kind"], s["verb"], s["line"]) for s in record["strands"]
    ]
    assert observed == [
        ("plan.md", "feature.md", "related", "parent-of", None),
        ("plan.md", "feature.md", "body-link", None, 13),
        ("status.md", "feature.md", "related", "pairs-with", None),
        ("status.md", "feature.md", "body-link", None, 13),
        ("status.md", "feature-impl.md", "body-link", None, 13),
    ]
    for strand in record["strands"]:
        assert list(strand) == ["path", "target", "kind", "verb", "line"]


def test_archive_json_strands_observed_in_the_preview_of_a_refusing_plan(
    docs_script, fixtures_dir, tmp_path
):
    """Phase-1 amendment 2: a leg-1 refusal emits no record at all, so the
    `strands` array of a plan leg 1 would refuse is observed in its PREVIEW —
    exit 0, record emitted, verdict reported rather than adopted.
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-strand")
    proc = _run(
        docs_script, "archive", "plan.md", "--date", _M28_DATE, "--json", "--dry-run", cwd=root
    )
    assert proc.returncode == 0, proc.stderr

    record = json.loads(proc.stdout)
    assert "strands" in record, "`strands` is present in every record, never missing"
    assert record["dry_run"] is True and record["applied"] is False
    assert [
        (s["path"], s["target"], s["kind"], s["verb"], s["line"]) for s in record["strands"]
    ] == [
        ("live-child.md", "plan.md", "related", "references", None),
        ("milestone.md", "plan.md", "body-link", None, 15),
    ], (
        "leg 2 still reports here, and it reports EXACTLY the edges leg 1 does "
        "not own — the child-of bullets belong to leg 1, so the two legs partition "
        "the graph by EDGE rather than by document: `live-child.md` contributes an "
        "orphan AND a strand. The `references: ./plan.md` bullet is also the only "
        "CLI-level proof that a free-form verb and an alias spelling both reach the "
        "record"
    )


def test_archive_json_strands_is_empty_array_not_missing(docs_script, tmp_path):
    """An empty neighbourhood yields an empty array, never a missing key."""
    root = tmp_path / "lonely"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "lonely"\n\n[archive]\ndir = "archive"\n')
    (root / "solo.md").write_text(
        "# Solo\n\nLifecycle: active\nRole: notes\nProject: lonely\n"
        "Updated: 2026-05-20\n\n## Body\n\nNothing points here.\n"
    )
    (root / "other.md").write_text(
        "# Other\n\nLifecycle: active\nRole: notes\nProject: lonely\n"
        "Updated: 2026-05-20\n\n## Body\n\nUnrelated prose.\n"
    )

    proc = _run(docs_script, "archive", "solo.md", "--date", _M28_DATE, "--json", cwd=root)
    assert proc.returncode == 0, proc.stderr

    record = json.loads(proc.stdout)
    assert "strands" in record and "rewrites" in record, (
        "both arrays are PRESENT and empty, never missing — a consumer must not "
        "have to distinguish `absent` from `nothing to report`"
    )
    assert record["strands"] == []
    assert record["rewrites"] == []


def test_archive_cascade_dry_run_on_a_malformed_tree_exits_1(docs_script, fixtures_dir, tmp_path):
    """Phase-1 amendment 1: a preview adopts failures of plan CONSTRUCTION.
    It now walks the tree in order to build the rewrite plan and the strand
    analysis, so a malformed referrer turns its exit 0 into the exit 1 the
    write path already uses.

    RED reason: today the preview returns at check-order step 5, before the
    whole-tree walk at step 8.
    """
    root = _crossrefs_tree(fixtures_dir, tmp_path)
    (root / "helper.md").write_text("This file has no H1 — it's malformed for parse().\n")
    before = _m28_snapshot(root)

    proc = _run(
        docs_script, "archive", str(root / "core.md"), "--cascade-dry-run", "--date", _M28_DATE
    )
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert "helper.md" in proc.stderr
    assert "Traceback" not in proc.stderr
    assert _m28_snapshot(root) == before


@_SKIP_AS_ROOT
def test_archive_refuses_when_a_planned_referrer_is_unwritable(docs_script, fixtures_dir, tmp_path):
    """(F) at the `docs archive` seam, check-order step 8c.

    M26's pre-flight (step 7) proves every plan MEMBER writable; M28's proves
    every planned REFERRER writable. `status.md` is not a plan member here, so
    only the new pre-flight can catch it — and the refusal must leave the whole
    tree byte-identical, the primary included.
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-closeout")
    before = _m28_snapshot(root)
    (root / "status.md").chmod(0o444)
    try:
        proc = _run(
            docs_script,
            "archive",
            "feature.md",
            "--cascade-only",
            "feature-*",
            "--date",
            _M28_DATE,
            cwd=root,
        )
    finally:
        (root / "status.md").chmod(0o644)

    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
    assert "docs: archive: status.md is not writable; refusing before any write" in proc.stderr
    assert proc.stdout == ""
    assert _m28_snapshot(root) == before


@_SKIP_AS_ROOT
def test_archive_rewrite_oserror_admits_the_partial_state(docs_script, tmp_path):
    """D4's residual, on the phase M28 created — check-order step 9b.

    Step 9a (the members move) has admitted its partial state since M26. Step 9b
    (the referrer rewrites) had none: it printed a bare
    `docs: archive: write failed for <rel>: <err>` and exited 2, while `docs mv`
    on the identical tree printed the complete admission. Pre-M28 that was
    defensible — the phase wrote only `Related:` bullets — but M28 widened it to
    prose bytes across the whole tree, making it the operation's LARGEST
    partial-state window and the only one that would not say what it had done.

    The trigger is the boundary `preflight_archive_plan` documents itself as
    deliberately admitting: a `0o644` file inside a `0o555` directory passes
    `os.access(file, W_OK)` and fails at the `.docs-tmp` sibling. `ref2.md` is
    outside that directory, so it lands first and the admission has a non-empty
    `Rewritten:` clause — without it, three of the four clauses would render
    `none` and the test could not tell a real admission from a template.
    """
    root = tmp_path / "rw"
    (root / "ro").mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "rw"\n\n[archive]\ndir = "archive"\n')
    hdr = "Lifecycle: active\nRole: notes\nProject: rw\n"
    (root / "a.md").write_text(f"# A\n\n{hdr}Updated: 2026-01-01\n\n## Body\n\nThe primary.\n")
    (root / "ref2.md").write_text(
        f"# R2\n\n{hdr}Updated: 2026-01-03\n\nRelated:\n- pairs-with: a.md\n\n"
        "## Body\n\nSee [a](a.md).\n"
    )
    (root / "ro" / "ref.md").write_text(
        f"# R1\n\n{hdr}Updated: 2026-01-02\n\nRelated:\n- pairs-with: a.md\n\n"
        "## Body\n\nSee [a](../a.md).\n"
    )
    os.chmod(root / "ro", 0o555)
    try:
        proc = _run(docs_script, "archive", str(root / "a.md"), "--date", _M28_DATE, "--json")
    finally:
        os.chmod(root / "ro", 0o755)

    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
    assert "Traceback" not in proc.stderr
    assert "docs: archive: write failed for ro/ref.md: " in proc.stderr, proc.stderr
    assert "PARTIAL ARCHIVE — not rolled back." in proc.stderr
    assert f"Archived: a.md -> {_M28_DATED}/a.md." in proc.stderr, (
        "every member moved in this phase, so they are ALL named as archived"
    )
    assert "Rewritten: ref2.md." in proc.stderr, (
        "the referrer that did land must be named — this is the clause that "
        "distinguishes a real admission from a template of `none`s"
    )
    assert "Not written: ro/ref.md." in proc.stderr
    assert "Repair manually." in proc.stderr
    assert proc.stdout == "", "no --json record: the operation did not complete"
    # …and the admission is checkable against the disk, clause by clause.
    assert (root / _M28_DATED / "a.md").is_file()
    assert f"[a]({_M28_DATED}/a.md)" in (root / "ref2.md").read_text()
    assert "[a](../a.md)" in (root / "ro" / "ref.md").read_text()


def test_archive_quiet_suppresses_the_rewrite_and_strand_lines(docs_script, fixtures_dir, tmp_path):
    """R3's other half: `--quiet` governs the whole summary on a COMPLETING
    run — the rewrite lines, the counts footer and the strand report alike —
    while the write still happens.

    The existing `--quiet` lock is on a refusal path, which has no rewrite or
    strand lines to suppress, so it cannot see this.
    """
    root = _m28_tree(fixtures_dir, tmp_path, "movelink-closeout")
    proc = _run(
        docs_script,
        "archive",
        "feature.md",
        "--cascade-only",
        "feature-*",
        "--date",
        _M28_DATE,
        "--quiet",
        cwd=root,
    )

    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == "", f"--quiet must silence the whole summary, got {proc.stderr!r}"
    assert (root / _M28_DATED / "feature.md").is_file(), "the write still happened"
    assert f"[the feature]({_M28_DATED}/feature.md)" in (root / "status.md").read_text()


def test_the_rewrite_footer_prints_its_zero(docs_script, tmp_path):
    """R3 read literally, and pinned because the zero case looks like noise.

    The counts footer prints on EVERY archive, including one over a tree with
    no body links at all — `0 destination(s) in 0 document(s) rebased`. That is
    positive evidence the new phase ran, and it keeps the two verbs' footers
    symmetrical. Leg 2's count line is deliberately NOT symmetrical with it: it
    summarises a list, so `0 still-active inbound reference(s)` on every
    archive would be pure noise, and it prints only when the list is non-empty.

    Both halves of that asymmetry are asserted here, because each looks like
    the other's bug.
    """
    root = tmp_path / "bare"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "bare"\n\n[archive]\ndir = "archive"\n')
    header = "Lifecycle: active\nRole: notes\nProject: bare\nUpdated: 2026-05-20\n"
    (root / "a.md").write_text(f"# A\n\n{header}\n## Body\n\nNo links anywhere.\n")
    (root / "b.md").write_text(f"# B\n\n{header}\n## Body\n\nNone here either.\n")

    proc = _run(docs_script, "archive", "a.md", "--date", _M28_DATE, cwd=root)

    assert proc.returncode == 0, proc.stderr
    assert "docs: archive: 0 destination(s) in 0 document(s) rebased" in proc.stderr, (
        f"the counts footer is unconditional (R3), zero included: {proc.stderr!r}"
    )
    assert "still-active inbound reference(s)" not in proc.stderr, (
        "leg 2's count line summarises a LIST, so it stays conditional — the "
        "asymmetry with the footer above is deliberate, not an oversight"
    )


def test_archive_never_rewrites_or_reports_an_excluded_document(docs_script, tmp_path):
    """R11, stated in `cli.md` as a named limitation and locked here.

    `[exclude]` / `.docsignore` decide which documents are WALKED, and
    therefore which are rewritten and which can report a strand. They never
    decide what a destination may point at. So an excluded document that
    declares `child-of` the primary does **not** trip leg 1 — the archive
    completes — and its stale destination is left exactly as written.

    This is a knowable gap, which is why it is named rather than inferred.
    """
    root = tmp_path / "excl"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "excl"\n\n[archive]\ndir = "archive"\n\n[exclude]\ndirs = ["vendor"]\n'
    )
    header = "Lifecycle: active\nRole: notes\nProject: excl\nUpdated: 2026-05-20\n"
    (root / "plan.md").write_text(f"# Plan\n\n{header}\n## Body\n\nThe primary.\n")
    (root / "keep.md").write_text(f"# Keep\n\n{header}\n## Body\n\nSee [the plan](plan.md).\n")
    vendor = root / "vendor"
    vendor.mkdir()
    excluded = vendor / "child.md"
    excluded.write_text(
        f"# Vendored child\n\n{header}\nRelated:\n- child-of: plan.md\n\n"
        "## Body\n\nSee [the plan](../plan.md).\n"
    )
    before = excluded.read_text()

    proc = _run(docs_script, "archive", "plan.md", "--date", _M28_DATE, cwd=root)

    assert proc.returncode == 0, (
        f"an EXCLUDED child-of must not trip leg 1 — the walk never yields it:\n{proc.stderr}"
    )
    assert "would be stranded" not in proc.stderr
    assert "vendor" not in proc.stderr
    assert excluded.read_text() == before, "an excluded document is never rewritten"
    assert f"[the plan]({_M28_DATED}/plan.md)" in (root / "keep.md").read_text()


# ===========================================================================
# M28a — the archive-date witness, at the writer.
#
# The contract under test is the milestone's *Decisions (Phase 1 — BINDING)*
# items (A) and (B), and `cli.md` › `docs archive` ›
# *The archive-date witness*.
# ===========================================================================

_M28A_DATE = "2026-03-04"
_M28A_DATED = f"archive/{_M28A_DATE}"


def test_archive_records_the_witness_matching_the_dated_directory(
    docs_script, fixtures_dir, tmp_path
):
    """D1: the recorded value is the SAME date that names the dated directory.

    Sibling of `test_archive_bumps_updated`. RED reason: `_archive_one` writes
    `Lifecycle`, `Updated` and (conditionally) `Archived-reason`, and nothing
    else (Phase 6).
    """
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "archive", str(root / "lone-doc.md"))
    assert proc.returncode == 0, proc.stderr
    today = date.today().isoformat()
    moved = root / "archive" / today / "lone-doc.md"
    assert f"Archived: {today}" in moved.read_text()


def test_archive_date_flag_controls_the_directory_and_the_field_from_one_value(
    docs_script, fixtures_dir, tmp_path
):
    """D1: one value, one source, one rendering — never a second `strftime`
    and never a `date.today()` re-read inside `_archive_one`.

    `--date` is what makes the two provably the same value rather than two
    computations that happen to agree on the day the test runs.
    """
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "archive", str(root / "lone-doc.md"), "--date", _M28A_DATE)
    assert proc.returncode == 0, proc.stderr
    moved = root / _M28A_DATED / "lone-doc.md"
    assert moved.is_file(), "the dated directory is named by --date"
    text = moved.read_text()
    assert f"Archived: {_M28A_DATE}" in text
    assert date.today().isoformat() not in text, (
        "today's date must appear nowhere: the witness is the archive event's date"
    )


def test_archive_writes_the_witness_at_the_pinned_block_position(
    docs_script, fixtures_dir, tmp_path
):
    """E7 / D1: nothing else pins a new field's position — there is no
    field-order list and no `field-order` rule, and `set_metadata_field`
    appends a new inline label at the end of the inline run. The position is
    therefore decided solely by the `set_metadata_field` call order in
    `_archive_one`, and this asserts the exact block, byte for byte.

    `Archived:` comes BEFORE `Archived-reason:` — the date, then the reason
    for it.
    """
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(docs_script, "archive", str(root / "lone-doc.md"), "--date", _M28A_DATE)
    assert proc.returncode == 0, proc.stderr
    block = (root / _M28A_DATED / "lone-doc.md").read_text().split("\n\n")[1]
    assert block.splitlines() == [
        "Lifecycle: archived",
        "Role: notes",
        "Project: minimal",
        f"Updated: {_M28A_DATE}",
        f"Archived: {_M28A_DATE}",
    ], block


def test_archive_with_reason_writes_the_witness_before_the_reason(
    docs_script, fixtures_dir, tmp_path
):
    """E7's coverage row, second half: the same byte-level block order with
    `--reason` present."""
    root = _minimal_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "archive",
        str(root / "lone-doc.md"),
        "--date",
        _M28A_DATE,
        "--reason",
        "milestone closed out",
    )
    assert proc.returncode == 0, proc.stderr
    block = (root / _M28A_DATED / "lone-doc.md").read_text().split("\n\n")[1]
    assert block.splitlines() == [
        "Lifecycle: archived",
        "Role: notes",
        "Project: minimal",
        f"Updated: {_M28A_DATE}",
        f"Archived: {_M28A_DATE}",
        "Archived-reason: milestone closed out",
    ], block


def test_archive_cascade_writes_the_witness_to_every_member(docs_script, fixtures_dir, tmp_path):
    """D2 / A2 / E4: the ONE place M28a deliberately does not copy
    `Archived-reason:`'s primary-only rule.

    The reported case was a cascaded trio split across two dated directories,
    and a trio's non-primary members are exactly the documents a primary-only
    witness would leave blind. Every member carries the operation's single
    date; `Archived-reason:` stays on the primary alone (M26 — D1, untouched).
    """
    root = _tree(fixtures_dir, tmp_path, "archive-trio")
    proc = _run(
        docs_script,
        "archive",
        str(root / "feature.md"),
        "--cascade-only",
        "feature-*.md",
        "--reason",
        "trio closed out",
        "--date",
        _M28A_DATE,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)

    members = ["feature.md", "feature-impl.md", "feature-test-matrix.md"]
    for name in members:
        moved = root / _M28A_DATED / name
        assert moved.is_file(), f"{name} must have moved"
        assert f"Archived: {_M28A_DATE}" in moved.read_text(), (
            f"{name} must carry the witness with the operation's single date"
        )

    primary = (root / _M28A_DATED / "feature.md").read_text()
    assert "Archived-reason: trio closed out" in primary
    for name in members[1:]:
        assert "Archived-reason:" not in (root / _M28A_DATED / name).read_text(), (
            "a cascaded candidate still never receives the primary's Archived-reason:"
        )


def test_archive_leaves_the_tree_check_clean(docs_script, fixtures_dir, tmp_path):
    """The over-fire guard at the CLI: the new rule must not fire on the tree
    the writer just produced. A witness whose own writer trips the rule would
    be worse than no witness at all.

    GREEN at baseline (degenerate — neither the writer nor the rule exists);
    the strongest single end-to-end assertion in the milestone after Phase 6.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-trio")
    proc = _run(
        docs_script,
        "archive",
        str(root / "feature.md"),
        "--cascade-only",
        "feature-*.md",
        "--date",
        _M28A_DATE,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, check.stdout
    assert "archive-date-drift" not in check.stdout


def test_archive_replaces_an_existing_witness_rather_than_duplicating_it(docs_script, tmp_path):
    """Item (A)'s pinned edge case: `set_metadata_field` replaces an existing
    inline label in place, so the archive event's date WINS and the document
    never ends up with two `Archived:` lines (which `duplicate-field` would
    then report as data loss).
    """
    root = tmp_path / "prewitnessed"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "prewitnessed"\n')
    (root / "thing.md").write_text(
        "# Thing\n\nLifecycle: active\nRole: notes\nProject: prewitnessed\n"
        "Updated: 2026-05-20\nArchived: 2020-01-01\n\n## Body\n\nProse.\n"
    )
    proc = _run(docs_script, "archive", str(root / "thing.md"), "--date", _M28A_DATE)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)

    text = (root / _M28A_DATED / "thing.md").read_text()
    assert text.count("Archived:") == 1, f"exactly one Archived: line, got:\n{text}"
    assert f"Archived: {_M28A_DATE}" in text
    assert "2020-01-01" not in text
    assert _run(docs_script, "check", str(root)).returncode == 0


def test_archive_keeps_a_related_group_after_the_witness(docs_script, fixtures_dir, tmp_path):
    """Item (A)'s second pinned edge case: `set_metadata_field` inserts a new
    inline label BEFORE the first bare-label group, so a `Related:` group still
    follows the inline run and the block stays convention-shaped."""
    root = _tree(fixtures_dir, tmp_path, "archive-trio")
    proc = _run(docs_script, "archive", str(root / "feature-impl.md"), "--date", _M28A_DATE)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    lines = (root / _M28A_DATED / "feature-impl.md").read_text().splitlines()
    assert f"Archived: {_M28A_DATE}" in lines
    assert lines.index(f"Archived: {_M28A_DATE}") < lines.index("Related:"), (
        "the witness is an INLINE label and must precede the bare-label group"
    )


def test_archive_renders_the_witness_in_the_trees_date_format(docs_script, tmp_path):
    """E8-adjacent: on a `[archive] dir = "attic"`, `date_format = "%d-%m-%Y"`
    tree the witness renders in the tree's format — ONE spelling in the file,
    never a second hardcoded ISO one (M25's rule, restated by Q2).

    The run's pre-existing exit-2 tail is asserted EXPLICITLY: `parse()` uses
    the hardcoded default while `check_doc` honours `config.date_format`
    (defect E8, *Follow-ups* item 1), so the end-of-batch INDEX refresh fails.
    M28a does not fix it, and pinning it here means this test can never be
    satisfied by the defect being fixed somewhere else.
    """
    root = tmp_path / "attic-tree"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "attictree"\n\n[archive]\ndir = "attic"\ndate_format = "%d-%m-%Y"\n'
    )
    (root / "thing.md").write_text(
        "# Thing\n\nLifecycle: active\nRole: notes\nProject: attictree\n"
        "Updated: 2026-05-20\n\n## Body\n\nProse.\n"
    )
    proc = _run(docs_script, "archive", str(root / "thing.md"), "--date", "04-03-2026")

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "docs: INDEX refresh failed:" in proc.stderr, (
        "the pre-existing E8 defect, pinned so this test measures the WITNESS"
    )
    assert "Updated: malformed date '04-03-2026' (expected %Y-%m-%d)" in proc.stderr

    text = (root / "attic" / "04-03-2026" / "thing.md").read_text()
    assert "Archived: 04-03-2026" in text
    assert "Updated: 04-03-2026" in text
    assert "2026-03-04" not in text, "no second date spelling anywhere in the file"


def test_archive_json_top_level_key_set_does_not_widen(docs_script, fixtures_dir, tmp_path):
    """*Also settled*: M28a adds no new JSON field, anywhere. `archive --json`
    already carries `date`, which is the same value the field records.

    GREEN at baseline and a genuine regression lock: it is what stops a
    Phase-6/7 implementer from adding an `archived` key beside it.
    """
    root = _tree(fixtures_dir, tmp_path, "archive-trio")
    proc = _run(
        docs_script,
        "archive",
        str(root / "feature.md"),
        "--cascade-only",
        "feature-*.md",
        "--date",
        _M28A_DATE,
        "--json",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert list(record) == _JSON_TOP_LEVEL_KEYS, list(record)
    assert record["date"] == _M28A_DATE
