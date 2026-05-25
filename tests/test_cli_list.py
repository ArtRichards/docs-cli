"""CLI end-to-end tests for `docs list` (Phase 2 — written RED).

`list` is read-only; tests run it directly against the `multi-project/`
fixture tree.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def _run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
    )


def _multi(fixtures_dir: Path) -> str:
    return str(fixtures_dir / "trees" / "multi-project")


def test_list_help(docs_script):
    proc = _run(docs_script, "list", "--help")
    assert proc.returncode == 0
    assert "filter" in proc.stdout.lower() or "query" in proc.stdout.lower()


def test_list_default_table_output(docs_script, fixtures_dir):
    proc = _run(docs_script, "list", "--root", _multi(fixtures_dir))
    assert proc.returncode == 0, proc.stderr
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert "alpha-charter.md" in proc.stdout


def test_list_exits_0(docs_script, fixtures_dir):
    proc = _run(docs_script, "list", "--root", _multi(fixtures_dir))
    assert proc.returncode == 0


def test_list_filter_by_status(docs_script, fixtures_dir):
    proc = _run(
        docs_script, "list", "--root", _multi(fixtures_dir), "--lifecycle", "draft", "--json"
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data
    assert all(rec["lifecycle"] == "draft" for rec in data)


def test_list_filter_by_role(docs_script, fixtures_dir):
    proc = _run(docs_script, "list", "--root", _multi(fixtures_dir), "--role", "spec", "--json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data
    assert all(rec["role"] == "spec" for rec in data)


def test_list_filter_by_project(docs_script, fixtures_dir):
    proc = _run(docs_script, "list", "--root", _multi(fixtures_dir), "--project", "alpha", "--json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data
    assert all(rec["project"] == "alpha" for rec in data)


def test_list_filter_by_stale(docs_script, fixtures_dir):
    proc = _run(docs_script, "list", "--root", _multi(fixtures_dir), "--stale", "90", "--json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data  # multi-project has docs older than 90 days


def test_list_json_record_schema(docs_script, fixtures_dir):
    proc = _run(docs_script, "list", "--root", _multi(fixtures_dir), "--json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert isinstance(data, list) and data
    for rec in data:
        assert set(rec) == {
            "path",
            "title",
            "lifecycle",
            "role",
            "project",
            "updated",
            "related",
            "extra_fields",
        }
        assert isinstance(rec["path"], str)
        assert isinstance(rec["title"], str)
        assert isinstance(rec["project"], str)  # resolved — never null
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", rec["updated"])
        assert isinstance(rec["related"], list)
        assert isinstance(rec["extra_fields"], dict)


def test_list_json_related_entries_are_objects(docs_script, fixtures_dir):
    proc = _run(docs_script, "list", "--root", _multi(fixtures_dir), "--json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    related = [entry for rec in data for entry in rec["related"]]
    assert related  # at least one fixture doc has a Related: block
    for entry in related:
        assert set(entry) == {"verb", "target"}
