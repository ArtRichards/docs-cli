"""M14 A5 — `atomic_write` durability: fsync before the rename.

The operator decision (2026-06-02) is to ADD `os.fsync` to `atomic_write`
so the `cli.md` §archive "fsync'd" durability claim becomes true. These
tests pin the behavioral contract: an `atomic_write`-backed mutation must
flush the new bytes to disk (via `os.fsync`) *before* the rename that
publishes them.

RED reason (Phase 4): `atomic_write` (cli.py:584-592) today does
`tmp.write_text(content); tmp.replace(path)` — no `os.fsync` call — so
the patched `os.fsync` below is never invoked. Step 2 (Phase 6) adds the
fsync.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

from docs_cli import cli


def test_atomic_write_fsyncs_before_rename(tmp_path: Path, monkeypatch) -> None:
    """`atomic_write` must fsync BOTH the tmpfile and its parent directory.

    The A5 Decision (milestone doc, 2026-06-02) is that `atomic_write`
    fsyncs "the tmpfile (and its parent directory)" before the rename —
    the correct durable-rename pattern: flushing the file's bytes alone
    does not durably persist the *rename* itself; the directory entry that
    publishes the new name must also be fsync'd.

    We patch `os.fsync` to record the kind (regular file vs. directory) of
    every fd it is handed, then run an `atomic_write`. The contract: the
    set of fsynced targets includes BOTH a regular file and a directory.
    """
    fsync_kinds: list[str] = []
    real_fsync = os.fsync

    def _recording_fsync(fd: int) -> None:
        # Classify the fd by stat'ing it, so we can pin that *both* a file
        # and its parent directory are flushed (not just one or the other).
        mode = os.fstat(fd).st_mode
        if stat.S_ISDIR(mode):
            fsync_kinds.append("dir")
        elif stat.S_ISREG(mode):
            fsync_kinds.append("file")
        else:
            fsync_kinds.append("other")
        real_fsync(fd)

    # Patch the name `cli` resolves at call time (it calls `os.fsync`).
    monkeypatch.setattr(cli.os, "fsync", _recording_fsync)

    target = tmp_path / "doc.md"
    cli.atomic_write(target, "# Title\n\nbody\n")

    # The write must have landed correctly...
    assert target.read_text() == "# Title\n\nbody\n"
    # ...AND fsync'd at least twice — the tmpfile AND its parent directory.
    assert len(fsync_kinds) >= 2, (
        "atomic_write fsync'd fewer than twice — the A5 durable-rename "
        f"pattern fsyncs the tmpfile AND its parent dir; saw {fsync_kinds!r}"
    )
    # ...covering BOTH a regular file and a directory (the durable-rename
    # contract: flushing file bytes alone does not persist the rename).
    assert "file" in fsync_kinds, (
        "atomic_write did not fsync the tmpfile — the cli.md 'fsync'd' "
        f"durability claim is unmet (M14 A5); saw {fsync_kinds!r}"
    )
    assert "dir" in fsync_kinds, (
        "atomic_write did not fsync the parent directory — the durable "
        "rename is not persisted (M14 A5 decision: fsync the tmpfile AND "
        f"its parent directory); saw {fsync_kinds!r}"
    )


def test_atomic_write_still_publishes_content(tmp_path: Path) -> None:
    """Regression guard: adding fsync must not change the published bytes.

    GREEN today and after Step 2 — the fsync is a durability addition, not
    a content change. An overwrite replaces the prior content atomically.
    """
    target = tmp_path / "doc.md"
    cli.atomic_write(target, "first\n")
    assert target.read_text() == "first\n"
    cli.atomic_write(target, "second\n")
    assert target.read_text() == "second\n"
    # No stray tmpfile is left behind.
    assert not list(tmp_path.glob("*.docs-tmp"))
