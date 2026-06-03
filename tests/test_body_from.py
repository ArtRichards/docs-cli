"""RED-baseline tests for M8 F9 — `docs new --body-from <-|path>`.

Phase 2 of M8. The `--body-from` flag closes the Read-before-Write
friction that breaks the agent flow: `docs new <role> <slug>
--body-from -` reads body content from stdin and writes the complete
file (scaffold frontmatter + body under the H1) atomically in one Bash
call.

Per OQ-E (resolved 2026-05-24) the body was REFUSED with exit 2 if any
of its first 20 lines matched `^[A-Z][A-Za-z-]+:\\s` — a conservative
any-`Label:` heuristic. M15 (C4) replaces that with detection of an
*actual* metadata block: the body is refused only when it carries a
leading `---` YAML fence OR a contiguous run with ≥ 2 of the required-
field labels `{Lifecycle, Role, Updated}` on adjacent lines (after an
optional `# H1`). A lone prose `Reason:` / `Plan:` / `Updated:` line is
now ACCEPTED — `edge-case-keyword.md` (a prose `Plan:` line) flips from
refusal to pass, and the dogfood `reason-in-body.md` shape passes too.
The footgun guard (a whole doc-with-frontmatter pasted as a body, or a
`---`-fenced doc) still refuses, with the M8 error tokens unchanged.
Refusal coverage is carried by `real-frontmatter-body.md` (cluster) and
`yaml-fence-body.md` (fence).
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


# --- 4. C4 refusal: body with a REAL metadata block (parametric × 2) ------


@pytest.mark.parametrize(
    "fixture_name",
    [
        # 1. A required-field cluster (>=2 of {Lifecycle, Role, Updated} on
        # adjacent lines after the H1) — a whole doc-with-frontmatter pasted
        # as a body. The footgun the C4 detector still refuses.
        "real-frontmatter-body.md",
        # 2. A leading `---` YAML fence — a front-matter-fenced doc pasted as
        # a body. Refused on signal (a).
        "yaml-fence-body.md",
    ],
)
def test_body_from_rejects_real_metadata_block_in_body(
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
    # Exit 2 — a real metadata block (cluster or fence) is refused (C4).
    assert proc.returncode == 2, (proc.returncode, proc.stderr, proc.stdout)
    # The documented error message (verbatim tokens, unchanged from M8).
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


# --- 8. C4: a prose body with Plan:/Reason: lines is ACCEPTED -------------


@pytest.mark.parametrize(
    "fixture_name",
    [
        # edge-case-keyword.md: a prose `Plan:` line. Under the old any-Label
        # heuristic this REFUSED; under the C4 cluster/fence detector it
        # passes (`Plan:` is not even a required-field label).
        "edge-case-keyword.md",
        # reason-in-body.md: the exact dogfood shape — a `## Risk level`
        # section opening with a prose `Reason:` line. Now accepted.
        "reason-in-body.md",
    ],
)
def test_body_from_accepts_prose_with_label_lines(
    docs_script,
    fixtures_dir,
    tmp_path,
    fixture_name,
):
    root = _minimal_tree(tmp_path)
    body_file = fixtures_dir / "body-from" / fixture_name
    body = body_file.read_text()
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
    assert proc.returncode == 0, (proc.returncode, proc.stderr, proc.stdout)
    written = (root / "my-feature.md").read_text()
    # The scaffold frontmatter is present AND the prose body is appended
    # verbatim at the tail (byte-equal).
    assert "Lifecycle: draft" in written, written
    assert written.endswith(body), (
        f"file should end with the body content byte-equal; tail was:\n{written[-200:]!r}"
    )


# --- 9. C4 cluster boundary: 1 required-field passes, 2 refuses ------------


def test_body_from_single_required_field_passes(docs_script, tmp_path):
    """A body opening with a SINGLE required-field line is accepted.

    Pins the lower edge of the cluster boundary: one `Updated:` prose line
    is not a metadata block. (cli.md C4: refusal needs >= 2 of
    {Lifecycle, Role, Updated} on adjacent lines.)
    """
    root = _minimal_tree(tmp_path)
    body = "## Notes\n\nUpdated: we shipped the thing on Tuesday.\n\nMore prose.\n"
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
    assert proc.returncode == 0, (proc.returncode, proc.stderr, proc.stdout)
    written = (root / "my-feature.md").read_text()
    assert written.endswith(body), written[-200:]


def test_body_from_two_required_fields_refuses(docs_script, tmp_path):
    """A body with TWO adjacent required-field lines is refused.

    Pins the upper edge of the cluster boundary: `Lifecycle:` + `Role:` on
    adjacent lines is the required-field cluster signal (b) — a real
    metadata block. (cli.md C4.)
    """
    root = _minimal_tree(tmp_path)
    body = "Lifecycle: active\nRole: spec\n\nSome body after a pasted block.\n"
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
    assert proc.returncode == 2, (proc.returncode, proc.stderr, proc.stdout)
    assert "appears to contain a metadata block" in proc.stderr, proc.stderr
    assert not (root / "my-feature.md").exists()


def test_body_from_two_required_fields_non_adjacent_passes(docs_script, tmp_path):
    """TWO required-field prose lines that are NON-adjacent are ACCEPTED.

    Pins the *adjacency* of the cluster boundary: the C4 refusal needs a
    CONTIGUOUS run of >= 2 of {Lifecycle, Role, Updated}. Here two such labels
    appear within the first ~20 lines but are separated by prose/blank lines,
    so they do NOT form a contiguous run — the body is legitimate prose and
    must pass. Guards against an implementation that refuses on ">= 2 required
    fields *anywhere* in the first 20 lines" (dropping the adjacency rule).
    """
    root = _minimal_tree(tmp_path)
    body = (
        "## Notes\n\n"
        "Lifecycle: we never wrote down the lifecycle of this subsystem.\n\n"
        "Some intervening prose so the two label lines are not adjacent.\n\n"
        "Role: the role of the cache here is purely advisory.\n\n"
        "More body prose at the tail.\n"
    )
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
    assert proc.returncode == 0, (proc.returncode, proc.stderr, proc.stdout)
    written = (root / "my-feature.md").read_text()
    assert "Lifecycle: draft" in written, written  # scaffold frontmatter
    assert written.endswith(body), written[-200:]


def test_body_from_required_fields_interleaved_by_non_required_label_passes(docs_script, tmp_path):
    """Two required-field labels with a NON-required label BETWEEN them PASS.

    Pins the resolved-Q2 boundary: the contiguous run is reset by a
    *non-required* `Label:` line just as it is by blank/prose. Here
    `Lifecycle:` and `Updated:` are adjacent ONLY across an intervening
    `Owner:` line — the non-required label breaks the run, so the cluster
    never reaches >= 2 directly-adjacent required fields and the body is
    accepted. Guards against an implementation that counts required fields
    across a non-required interruption.
    """
    root = _minimal_tree(tmp_path)
    body = "Lifecycle: active\nOwner: alice\nUpdated: 2026-05-20\n\nSome body prose.\n"
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
    assert proc.returncode == 0, (proc.returncode, proc.stderr, proc.stdout)
    written = (root / "my-feature.md").read_text()
    assert "Lifecycle: draft" in written, written  # scaffold frontmatter
    assert written.endswith(body), written[-200:]
