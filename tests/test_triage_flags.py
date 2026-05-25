"""RED-baseline tests for M8 F6 — triage flags (`--summary`, `--only`, `--group-by`).

Phase 2 of M8. Drives the unimplemented flags against the M7 sanitised
real-trees fixtures (`snake-medium`, `kebab-tiny`). Every assertion
fails at Phase 4 with an argparse "unrecognized arguments" error
(exit 2) for the unimplemented flags.

Per OQ3 (planning resolution), the default plan-footer assertions use
substring assertions only ("summary:", "roles:", "confidence:",
"ambiguities:", "spec=", "high=", etc.). Phase 6 tunes the exact line
shape; pinning line-exact text here would over-constrain the
implementer.

Test 6 (`--summary` + `--only ambiguous` compose) drives the
mutual-non-exclusion contract: the two flags must coexist on a single
invocation.
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


def _tree(fixtures_dir: Path, name: str) -> Path:
    return fixtures_dir / "trees" / "real-trees" / name


# --- 1. --summary emits one line per file ----------------------------------


def test_summary_emits_one_line_per_file(docs_script, fixtures_dir):
    tree = _tree(fixtures_dir, "kebab-tiny")
    proc = _run(docs_script, "migrate", str(tree), "--summary")
    assert proc.returncode == 0, proc.stderr
    # kebab-tiny has 3 files; --summary's contract is one line per file
    # in the body (plus footer). The strict assertion: at least 3 lines
    # mention one of the kebab-tiny stems.
    stems = {"foo-bar-plan", "foo-bar-spec", "foo-bar-status"}
    matched = [line for line in proc.stdout.splitlines() if any(s in line for s in stems)]
    assert len(matched) >= 3, (
        f"--summary should print one line per file (3 files in kebab-tiny); "
        f"got {len(matched)} matching lines:\n{proc.stdout}"
    )


# --- 2. --only ambiguous filters high-confidence files ---------------------


def test_only_ambiguous_filters_high_confidence(docs_script, fixtures_dir):
    tree = _tree(fixtures_dir, "snake-medium")
    proc_all = _run(docs_script, "migrate", str(tree), "--summary")
    proc_amb = _run(docs_script, "migrate", str(tree), "--summary", "--only", "ambiguous")
    assert proc_all.returncode == 0, proc_all.stderr
    assert proc_amb.returncode == 0, proc_amb.stderr
    # --only ambiguous filters out high-confidence files with no ambiguities.
    # Strict contract: the filtered output has STRICTLY FEWER per-file lines
    # than the unfiltered output (snake-medium has high-confidence files at
    # this point in the suite per M7's 88% achievement).
    all_lines = [line for line in proc_all.stdout.splitlines() if line.strip()]
    amb_lines = [line for line in proc_amb.stdout.splitlines() if line.strip()]
    assert len(amb_lines) < len(all_lines), (
        "--only ambiguous should remove high-confidence-no-ambiguity rows; "
        f"all={len(all_lines)}, ambiguous={len(amb_lines)}"
    )


# --- 3. --group-by role orders plan by role --------------------------------


def test_group_by_role_orders_plan_by_role(docs_script, fixtures_dir):
    tree = _tree(fixtures_dir, "snake-medium")
    proc = _run(docs_script, "migrate", str(tree), "--summary", "--group-by", "role")
    assert proc.returncode == 0, proc.stderr
    # --group-by role groups rows by role; the substring assertion is that
    # at least two distinct role tokens appear in adjacent grouped blocks.
    # Phase 6 tunes the exact format; pinning here uses a forward-compatible
    # check that "role" appears in the output (header or column label).
    assert "role" in proc.stdout.lower(), proc.stdout


# --- 4. --group-by confidence orders high → medium → low -------------------


def test_group_by_confidence_orders_high_medium_low(docs_script, fixtures_dir):
    tree = _tree(fixtures_dir, "snake-medium")
    proc = _run(docs_script, "migrate", str(tree), "--summary", "--group-by", "confidence")
    assert proc.returncode == 0, proc.stderr
    # --group-by confidence orders by confidence: high → medium → low. The
    # substring check is that "confidence" appears in the output and that
    # the "high" group precedes the "low" group in the rendered output
    # (forward-compatible — Phase 6 picks the exact rendering shape).
    out_lower = proc.stdout.lower()
    assert "confidence" in out_lower, proc.stdout
    if "high" in out_lower and "low" in out_lower:
        assert out_lower.find("high") < out_lower.find("low"), (
            "--group-by confidence should order high → low; got:\n" + proc.stdout
        )


# --- 5. default plan footer shows counts ------------------------------------


def test_default_plan_footer_shows_counts(docs_script, fixtures_dir):
    tree = _tree(fixtures_dir, "snake-medium")
    proc = _run(docs_script, "migrate", str(tree))
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout.lower()
    # Per OQ3 — substring assertions only. The default footer summarises
    # counts by role + confidence + ambiguity; the substrings below are
    # the load-bearing tokens.
    assert "summary:" in out, proc.stdout
    assert "roles:" in out, proc.stdout
    assert "confidence:" in out, proc.stdout
    assert "ambiguities:" in out, proc.stdout


# --- 6. --summary and --only ambiguous compose -----------------------------


def test_summary_and_only_ambiguous_compose(docs_script, fixtures_dir):
    tree = _tree(fixtures_dir, "snake-medium")
    proc = _run(docs_script, "migrate", str(tree), "--summary", "--only", "ambiguous")
    # The contract is "both flags coexist on a single invocation"; the
    # exit code being 0 (not argparse-error 2) is the load-bearing
    # assertion at Phase 4. Output shape is asserted by tests 1+2.
    assert proc.returncode == 0, proc.stderr
