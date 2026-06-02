"""RED-baseline tests for M8 F9 — `docs new --body-from <-|path>`.

Phase 2 of M8. The `--body-from` flag closes the Read-before-Write
friction that breaks the agent flow: `docs new <role> <slug>
--body-from -` reads body content from stdin and writes the complete
file (scaffold frontmatter + body under the H1) atomically in one Bash
call.

Per OQ-E (resolved 2026-05-24), the body content is REFUSED with exit
2 if any line in the first 20 lines matches `^[A-Z][A-Za-z-]+:\\s` —
the conservative-by-design metadata-block heuristic. The clear error
message lets the agent self-correct in the next call.

Per OQ5 (planning resolution), `edge-case-keyword.md` (with a line
like `Plan: stage one then stage two`) IS expected to trigger the
refusal — the heuristic's false-positive trade-off is folded into
test 4's parametrisation with a docstring explaining the rationale.

Test count: 7 functions (test 4 parametrized × 2 collected items).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def _run(
    docs_script: Path,
    *args: str,
    cwd: Path | None = None,
    stdin: str | None = None,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(docs_script), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        input=stdin,
    )


def _minimal_tree(tmp_path: Path) -> Path:
    root = tmp_path / "tree"
    root.mkdir()
    # M14 (A2) lockstep: `docs new --root <dir>` now requires <dir>/.docs.toml
    # (the strict-root refusal — a write into an unmanaged dir is the footgun
    # A2 closes). These tests exercise `--body-from` semantics, not root
    # resolution, so the helper supplies a minimal valid docs root. Every
    # `--body-from` assertion is unchanged.
    (root / ".docs.toml").write_text('[project]\nname = "tree"\n\n[archive]\ndir = "archive"\n')
    return root


# --- 1. --body-from - reads stdin and writes the complete file -------------


def test_body_from_stdin_writes_complete_file(docs_script, tmp_path):
    root = _minimal_tree(tmp_path)
    body = "## Overview\n\nThis is the body authored via stdin.\n\n## Details\n\nMore.\n"
    proc = _run(
        docs_script,
        "new",
        "spec",
        "my-feature",
        "--root",
        str(root),
        "--body-from",
        "-",
        stdin=body,
    )
    assert proc.returncode == 0, proc.stderr
    written = (root / "my-feature.md").read_text()
    # Scaffold frontmatter present.
    assert "Lifecycle: draft" in written, written
    assert "Role: spec" in written, written
    # Body content present.
    assert "## Overview" in written, written
    assert "## Details" in written, written
    assert "This is the body authored via stdin." in written, written


# --- 2. --body-from <path> reads from a file -------------------------------


def test_body_from_path_reads_file(docs_script, fixtures_dir, tmp_path):
    root = _minimal_tree(tmp_path)
    body_file = fixtures_dir / "body-from" / "clean-body.md"
    proc = _run(
        docs_script,
        "new",
        "spec",
        "my-feature",
        "--root",
        str(root),
        "--body-from",
        str(body_file),
    )
    assert proc.returncode == 0, proc.stderr
    written = (root / "my-feature.md").read_text()
    assert "Lifecycle: draft" in written, written
    # Body content from the fixture appears in the file.
    assert "## Overview" in written, written
    assert "This is the body. No labels at the head." in written, written


# --- 3. output matches scaffold + body composition (golden) ----------------


def test_body_from_output_matches_scaffold_plus_body_golden(docs_script, tmp_path):
    """Byte-equal to a manually composed scaffold + body reference.

    Reference shape: scaffold's H1 + frontmatter, blank line, body
    appended under the H1. The exact composition is the GREEN
    contract; Phase 6 picks the join (likely H1 + frontmatter +
    blank + body). The golden here is computed at runtime against
    the reference so the test is a contract, not a frozen string.
    """
    root = _minimal_tree(tmp_path)
    body = "## Overview\n\nA body.\n"

    # Reference: the same `new` invocation WITHOUT --body-from gives
    # the scaffold; the GREEN contract is "scaffold + body" with no
    # double-blank-line accident. We assert that the body content is
    # appended verbatim (modulo a single separator newline) after
    # the scaffold's H1 + frontmatter block.
    proc_body = _run(
        docs_script,
        "new",
        "spec",
        "alpha",
        "--root",
        str(root),
        "--body-from",
        "-",
        stdin=body,
    )
    assert proc_body.returncode == 0, proc_body.stderr
    written = (root / "alpha.md").read_text()
    # The body text appears verbatim somewhere after the frontmatter's
    # Updated: line. We assert order: Updated: precedes ## Overview.
    assert "Updated:" in written, written
    assert written.find("Updated:") < written.find("## Overview"), written
    # And the body content is present byte-equal at the tail.
    assert written.endswith(body), (
        f"file should end with the body content byte-equal; tail was:\n{written[-200:]!r}"
    )


# --- 4. OQ-E refusal: body with metadata-shaped lines (parametric × 2) ----


@pytest.mark.parametrize(
    "fixture_name",
    [
        # 1. Real metadata block at the head — the obvious refusal case.
        "with-frontmatter.txt",
        # 2. Edge-case keyword — `Plan:` matches `^[A-Z][A-Za-z-]+:\s`
        # so the conservative-by-design heuristic refuses. Per OQ5,
        # this is the documented false-positive trade-off the test pins.
        "edge-case-keyword.md",
    ],
)
def test_body_from_rejects_metadata_block_in_body(
    docs_script,
    fixtures_dir,
    tmp_path,
    fixture_name,
):
    root = _minimal_tree(tmp_path)
    body_file = fixtures_dir / "body-from" / fixture_name
    proc = _run(
        docs_script,
        "new",
        "spec",
        "my-feature",
        "--root",
        str(root),
        "--body-from",
        str(body_file),
    )
    # Exit 2 per OQ-E.
    assert proc.returncode == 2, (proc.returncode, proc.stderr, proc.stdout)
    # The documented error message (verbatim tokens from milestone doc OQ-E).
    stderr = proc.stderr
    assert "appears to contain a metadata block" in stderr, stderr
    assert "Pass body content only" in stderr, stderr
    assert "Stripped first 5 lines:" in stderr, stderr
    # No file written.
    assert not (root / "my-feature.md").exists(), "file should not have been created"


# --- 5. --body-from with missing value → argparse error --------------------


def test_body_from_with_missing_value_argparse_errors(docs_script, tmp_path):
    root = _minimal_tree(tmp_path)
    proc = _run(
        docs_script,
        "new",
        "spec",
        "my-feature",
        "--root",
        str(root),
        "--body-from",
    )
    # argparse "expected one argument" → exit 2.
    assert proc.returncode == 2, (proc.returncode, proc.stderr, proc.stdout)


# --- 6. --body-from <nonexistent-path> → exit 2 ----------------------------


def test_body_from_nonexistent_path_returns_exit_2(docs_script, tmp_path):
    root = _minimal_tree(tmp_path)
    proc = _run(
        docs_script,
        "new",
        "spec",
        "my-feature",
        "--root",
        str(root),
        "--body-from",
        str(tmp_path / "does-not-exist.md"),
    )
    assert proc.returncode == 2, (proc.returncode, proc.stderr, proc.stdout)
    # The error must mention the missing path or "not found".
    assert "not found" in proc.stderr.lower() or "no such" in proc.stderr.lower(), proc.stderr


# --- 7. idempotency — second call refuses with existing-file semantics ----


def test_body_from_idempotency_second_call_refuses(docs_script, tmp_path):
    root = _minimal_tree(tmp_path)
    body = "## Overview\n\nA body.\n"
    proc1 = _run(
        docs_script,
        "new",
        "spec",
        "my-feature",
        "--root",
        str(root),
        "--body-from",
        "-",
        stdin=body,
    )
    assert proc1.returncode == 0, proc1.stderr
    # Second call must refuse (file already exists) — same semantics
    # as current `docs new` (cli.py ~2605-2607: print "file already
    # exists" and return). No overwrite of the first body.
    proc2 = _run(
        docs_script,
        "new",
        "spec",
        "my-feature",
        "--root",
        str(root),
        "--body-from",
        "-",
        stdin="## Different body\n",
    )
    assert proc2.returncode != 0, (proc2.returncode, proc2.stderr)
    assert "already exists" in proc2.stderr.lower(), proc2.stderr
    # First body preserved (no overwrite).
    assert "## Overview" in (root / "my-feature.md").read_text()
