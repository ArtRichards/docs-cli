"""F4 — archive-subdir normalisation (Phase 2, RED).

Trial 2 (2026-05-24) confirmed 0 of 25 trees with an `archived/` or
`archive/` flat subdir generated a normalising move proposal. M4's
`detect_archive_layout` already handles the move shape, but it was wired with
a single migration-run-wide `archive_date` — per-file dates from mtime (or
`Updated:`) never reached the plan.

M7's F4 proposes that the date for an archive-normalising move come per-file
from the file's mtime (or `Updated:` line), with the existing `--date` flag
preserved as the global-override knob. The three regression-lock tests in
this file are GREEN at baseline (M4 already handles the layout shapes); only
the per-file-date test is RED for the intended unimplemented reason.
"""

from __future__ import annotations

import os
import time
from datetime import date

from docs import plan_migration


def _write(path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


# --- F4 — per-file mtime drives the archive move date ----------------------


def test_archived_subdir_generates_move_with_mtime_date(tmp_path):
    """A file under `archived/<file>.md` generates a planned move into
    `archive/<YYYY-MM-DD>/<file>.md`, where the date comes from the file's
    own mtime (NOT a single migration-run-wide default).

    Today every archive_move ignores per-file mtime and uses
    `plan_migration`'s `archive_date` argument (default: today) for every
    file. This test sets a fixed past mtime and asserts the planned move
    carries that date.
    """
    fixed = date(2023, 7, 15)
    file_path = tmp_path / "archived" / "old-thing.md"
    _write(file_path, "# Old Thing\n\nBody.\n")
    fixed_epoch = time.mktime(fixed.timetuple())
    os.utime(file_path, (fixed_epoch, fixed_epoch))

    # No `archive_date` argument — the per-file mtime must drive it.
    plan = plan_migration(tmp_path)
    archived = [f for f in plan.files if f.rel.endswith("old-thing.md")]
    assert archived, "expected one archive-subdir file in the plan"
    fm = archived[0]
    assert fm.archive_move == "archive/2023-07-15/old-thing.md", (
        f"expected per-file-mtime-driven move; got {fm.archive_move!r}"
    )


# --- F4 — `archive/` (no `d`) also normalises (regression lock) ------------


def test_archive_subdir_no_d_also_normalises(tmp_path):
    """A file under `archive/<file>.md` (the no-`d` shape, with no dated
    subdir below) is normalised into `archive/<date>/<file>.md`. M4's
    `detect_archive_layout` already handles this branch — regression lock,
    GREEN at baseline.
    """
    _write(tmp_path / "archive" / "loose.md", "# Loose\n\nBody.\n")
    plan = plan_migration(tmp_path, archive_date="2026-05-22")
    moves = [f for f in plan.files if f.rel.endswith("loose.md")]
    assert moves
    assert moves[0].archive_move == "archive/2026-05-22/loose.md"


# --- F4 — `--date` CLI flag overrides per-file dates (regression lock) -----


def test_date_cli_flag_overrides_per_file_dates(tmp_path):
    """When `plan_migration` is called with an explicit `archive_date`, the
    per-file mtime/`Updated:` falls back to that global date — the existing
    `--date` flag preserves its current semantics.

    Regression lock — GREEN at baseline.
    """
    fixed = date(2020, 1, 1)
    file_path = tmp_path / "archived" / "x.md"
    _write(file_path, "# X\n\nBody.\n")
    fixed_epoch = time.mktime(fixed.timetuple())
    os.utime(file_path, (fixed_epoch, fixed_epoch))

    plan = plan_migration(tmp_path, archive_date="2026-05-22")
    fm = next(f for f in plan.files if f.rel.endswith("x.md"))
    assert fm.archive_move == "archive/2026-05-22/x.md", (
        f"with explicit archive_date the global date wins; got {fm.archive_move!r}"
    )


# --- F4 — already-conformant archive file: no move (regression lock) -------


def test_already_conformant_archive_file_no_move(tmp_path):
    """A file already at `archive/<YYYY-MM-DD>/<file>.md` is conformant —
    no move is proposed. Regression lock — GREEN at baseline.
    """
    _write(
        tmp_path / "archive" / "2024-03-04" / "kept.md",
        "# Kept\n\nBody.\n",
    )
    plan = plan_migration(tmp_path)
    fm = next(f for f in plan.files if f.rel.endswith("kept.md"))
    assert fm.archive_move is None, (
        f"a file already at archive/<date>/ must NOT be re-moved; got {fm.archive_move!r}"
    )
