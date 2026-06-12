"""CLI end-to-end tests for `docs list` (Phase 2 — written RED).

`list` is read-only; tests run it directly against the `multi-project/`
fixture tree.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date, timedelta
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


def test_list_filter_by_lifecycle(docs_script, fixtures_dir):
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


# --- M19 Q6 — `[check] stale_days` does NOT affect `docs list --stale` -----
#
# GREEN-at-baseline regression locks: `docs list` is deliberately NOT a
# consumer of `[check] stale_days`. These pin that bare `docs list` keeps
# listing everything and an explicit `--stale N` is identical with or without
# a `[check]` section. They pass today and must keep passing after Phases 5-6
# wire the config into the CHECK path only.


def _list_stale_config_tree(tmp_path: Path, name: str, *, with_check: bool) -> Path:
    """A docs root with a fresh + an ancient active doc, optionally carrying a
    `[check] stale_days = 1` sidecar. `today`-relative dates so it never rots.
    """
    root = tmp_path / name
    root.mkdir()
    toml = f'[project]\nname = "{name}"\n'
    if with_check:
        toml += "\n[check]\nstale_days = 1\n"
    (root / ".docs.toml").write_text(toml)
    today = date.today().isoformat()
    old = (date.today() - timedelta(days=400)).isoformat()
    (root / "fresh.md").write_text(
        f"# Fresh\n\nLifecycle: active\nRole: notes\nProject: {name}\nUpdated: {today}\n\nBody.\n"
    )
    (root / "ancient.md").write_text(
        f"# Ancient\n\nLifecycle: active\nRole: notes\nProject: {name}\nUpdated: {old}\n\nBody.\n"
    )
    return root


def test_list_stale_config_does_not_filter_bare_list(docs_script, tmp_path):
    """A `[check] stale_days = 1` tree: bare `docs list` (no `--stale`) returns
    ALL docs — the config window must not be applied as a `list` filter.
    """
    root = _list_stale_config_tree(tmp_path, "list-cfg", with_check=True)
    proc = _run(docs_script, "list", "--root", str(root), "--json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    paths = {rec["path"] for rec in data}
    assert "fresh.md" in paths
    assert "ancient.md" in paths, "[check] stale_days must NOT filter bare list"


def test_list_explicit_stale_unaffected_by_config(docs_script, tmp_path):
    """`docs list --stale 90 --json` returns the identical record set whether
    or not a `[check]` section is present — the explicit filter is the SoT.
    """
    with_cfg = _list_stale_config_tree(tmp_path, "list-with", with_check=True)
    without_cfg = _list_stale_config_tree(tmp_path, "list-without", with_check=False)

    def _stale_paths(root: Path) -> set[str]:
        proc = _run(docs_script, "list", "--root", str(root), "--stale", "90", "--json")
        assert proc.returncode == 0, proc.stderr
        return {rec["path"] for rec in json.loads(proc.stdout)}

    assert _stale_paths(with_cfg) == _stale_paths(without_cfg) == {"ancient.md"}
