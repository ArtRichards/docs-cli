"""CLI end-to-end tests for `docs check` (Phase 2 — written RED).

`check` is read-only, so most tests run it directly against a fixture tree.
The stale tests build a tree with `date.today()`-relative dates so they do not
rot as the wall clock advances.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
    )


def _stale_tree(tmp_path: Path, name: str, *, include_fresh: bool) -> Path:
    """Build a tree whose only possible problem is a very old active doc."""
    root = tmp_path / name
    root.mkdir()
    (root / ".docs.toml").write_text(f'[project]\nname = "{name}"\n')
    old = (date.today() - timedelta(days=400)).isoformat()
    (root / "ancient.md").write_text(
        f"# Ancient\n\nLifecycle: active\nRole: notes\nProject: {name}\nUpdated: {old}\n\nBody.\n"
    )
    if include_fresh:
        fresh = date.today().isoformat()
        (root / "fresh.md").write_text(
            f"# Fresh\n\nLifecycle: active\nRole: notes\n"
            f"Project: {name}\nUpdated: {fresh}\n\nBody.\n"
        )
    return root


def test_check_help(docs_script):
    proc = _run(docs_script, "check", "--help")
    assert proc.returncode == 0
    assert "violation" in proc.stdout.lower()


def test_check_clean_tree_exits_0(docs_script, fixtures_dir):
    proc = _run(docs_script, "check", str(fixtures_dir / "trees" / "minimal"))
    assert proc.returncode == 0, proc.stderr
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)


def test_check_drift_tree_exits_2(docs_script, fixtures_dir):
    proc = _run(docs_script, "check", str(fixtures_dir / "trees" / "drift"))
    assert proc.returncode == 2
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)


def test_check_invalid_tree_exits_2_and_lists_findings(docs_script, fixtures_dir):
    proc = _run(docs_script, "check", str(fixtures_dir / "trees" / "invalid"))
    assert proc.returncode == 2
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    # Output is grouped by file — offending files are named.
    assert "bad-status.md" in proc.stdout
    assert "bad-date.md" in proc.stdout


def test_check_stale_only_tree_exits_1(docs_script, tmp_path):
    """A tree whose only problem is a stale doc → exit 1 (warnings only)."""
    root = _stale_tree(tmp_path, "stalecheck", include_fresh=True)
    proc = _run(docs_script, "check", str(root), "--stale", "30")
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert "ancient.md" in proc.stdout
    assert "stale" in proc.stdout.lower()


def test_check_without_stale_flag_ignores_old_docs(docs_script, tmp_path):
    root = _stale_tree(tmp_path, "nostale", include_fresh=False)
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


def test_check_json_emits_finding_array(docs_script, fixtures_dir):
    proc = _run(docs_script, "check", str(fixtures_dir / "trees" / "invalid"), "--json")
    assert proc.returncode == 2
    data = json.loads(proc.stdout)
    assert isinstance(data, list) and data
    for rec in data:
        assert set(rec) == {"path", "severity", "rule", "message"}
        assert rec["severity"] in ("error", "warning")


def test_check_human_output_groups_by_file(docs_script, fixtures_dir):
    proc = _run(docs_script, "check", str(fixtures_dir / "trees" / "invalid"))
    assert "no-status.md" in proc.stdout
    assert "broken-ref.md" in proc.stdout


def test_check_dogfood_repo_docs_is_clean(docs_script):
    """`docs check` on this repo's own docs/ must be clean — the M3 exit criterion."""
    proc = _run(docs_script, "check", str(REPO_ROOT / "docs"))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
