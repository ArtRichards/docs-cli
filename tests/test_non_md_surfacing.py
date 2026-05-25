"""RED-baseline tests for M8 F7 — non-Markdown sibling surfacing.

Phase 2 of M8. The migrate plan footer surfaces non-md siblings at the
tree root so adopting agents see the binaries (HTML, XLSX, ODT, etc.)
that are referenced from prose but skipped by the (markdown-only)
convention. Per F7 and OQ4:

- N>0 non-md siblings at root → footer line:
  `N non-Markdown siblings at root not considered: <names>`.
- N==0 → no footer line.
- `--exclude-ext` filters the displayed list; when filtered list is
  empty, the line is suppressed entirely.

Today the plan footer carries none of this (the surfacing logic is
unimplemented), and `--exclude-ext` is not yet an argparse argument
on migrate, so every assertion here goes RED at Phase 4.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(docs_script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(docs_script), *args],
        capture_output=True,
        text=True,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _foreign_with_non_md(root: Path) -> None:
    _write(root / "spec.md", "# Spec\n\nBody.\n")
    _write(root / "plan.md", "# Plan\n\nBody.\n")
    _write(root / "report-2026-05-21.html", "<html></html>")
    _write(root / "ceo-review.xlsx", "binary")
    _write(root / "source-pack.odt", "binary")


# --- 1. footer surfaces non-md siblings with names + count -----------------


def test_non_md_siblings_surface_in_footer(docs_script, tmp_path):
    root = tmp_path / "tree"
    _foreign_with_non_md(root)
    proc = _run(docs_script, "migrate", str(root))
    assert proc.returncode == 0, proc.stderr
    # Exact contract: "3 non-Markdown siblings at root not considered:".
    assert "3 non-Markdown siblings at root not considered:" in proc.stdout, proc.stdout
    # All three filenames must be reachable in the footer line.
    for name in ("report-2026-05-21.html", "ceo-review.xlsx", "source-pack.odt"):
        assert name in proc.stdout, f"missing {name!r} in:\n{proc.stdout}"


# --- 2. footer omits the line when no non-md siblings ----------------------


def test_no_footer_line_when_no_non_md_siblings(docs_script, tmp_path):
    root = tmp_path / "tree"
    _write(root / "spec.md", "# Spec\n\nBody.\n")
    _write(root / "plan.md", "# Plan\n\nBody.\n")
    proc = _run(docs_script, "migrate", str(root))
    assert proc.returncode == 0, proc.stderr
    # No "non-Markdown siblings" substring in the output at all.
    assert "non-Markdown siblings" not in proc.stdout, proc.stdout


# --- 3. --exclude-ext suppresses the footer when filtered list is empty ----


def test_exclude_ext_suppresses_non_md_footer_entries(docs_script, tmp_path):
    root = tmp_path / "tree"
    _foreign_with_non_md(root)
    # Exclude every non-md extension present → filtered list is empty →
    # footer line entirely suppressed per OQ4.
    proc = _run(
        docs_script,
        "migrate",
        str(root),
        "--exclude-ext",
        "xlsx,html,odt",
    )
    assert proc.returncode == 0, proc.stderr
    assert "non-Markdown siblings" not in proc.stdout, proc.stdout
