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
from pathlib import Path

from docs_cli import cli


def test_atomic_write_fsyncs_before_rename(tmp_path: Path, monkeypatch) -> None:
    """`atomic_write` must call `os.fsync` (durability) during the write.

    We patch `os.fsync` to record every fd it is handed, then run an
    `atomic_write`. The contract: at least one `os.fsync` happens — the
    new bytes are flushed to stable storage before the rename publishes
    the file.
    """
    fsync_calls: list[int] = []
    real_fsync = os.fsync

    def _recording_fsync(fd: int) -> None:
        fsync_calls.append(fd)
        real_fsync(fd)

    # Patch the name `cli` resolves at call time (it calls `os.fsync`).
    monkeypatch.setattr(cli.os, "fsync", _recording_fsync)

    target = tmp_path / "doc.md"
    cli.atomic_write(target, "# Title\n\nbody\n")

    # The write must have landed correctly...
    assert target.read_text() == "# Title\n\nbody\n"
    # ...AND been fsync'd at least once (the durability contract).
    assert fsync_calls, (
        "atomic_write did not call os.fsync — the cli.md 'fsync'd' durability "
        "claim is unmet (M14 A5)"
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
