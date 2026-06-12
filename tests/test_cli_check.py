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


# --- M10 D3 — `unknown-field` rule wired through the CLI ------------------


def _vocab_tree(tmp_path: Path, name: str, add_fields: list[str]) -> Path:
    """Build a tiny docs root with a `[vocabulary] add_fields = [...]`
    sidecar and one doc carrying an `Owner:` extra metadata line.
    """
    root = tmp_path / name
    root.mkdir()
    fields_token = ", ".join(f'"{f}"' for f in add_fields)
    (root / ".docs.toml").write_text(
        f'[project]\nname = "{name}"\n\n[vocabulary]\nadd_fields = [{fields_token}]\n'
    )
    today = date.today().isoformat()
    (root / "doc.md").write_text(
        f"# Doc\n\nLifecycle: active\nRole: notes\nProject: {name}\n"
        f"Updated: {today}\nOwner: alice\n\nBody.\n"
    )
    return root


def test_check_cli_unknown_field_exits_1(docs_script, tmp_path):
    """OQ-F + OQ-H: allowlist = `["Tags"]` + doc with `Owner:` ⇒ exit 1
    + `unknown-field` token in stdout.
    """
    root = _vocab_tree(tmp_path, "uf-mismatch", add_fields=["Tags"])
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "unknown-field" in proc.stdout, proc.stdout
    assert "Owner" in proc.stdout, proc.stdout


def test_check_cli_allowlist_match_exits_0(docs_script, tmp_path):
    """OQ-H: allowlist = `["Owner"]` + doc with `Owner:` ⇒ exit 0; no
    `unknown-field` mention.
    """
    root = _vocab_tree(tmp_path, "uf-match", add_fields=["Owner"])
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "unknown-field" not in proc.stdout, proc.stdout


# --- M19 D2 — `[check] stale_days` config default + threshold provenance ---
#
# RED at baseline: nothing reads `[check] stale_days` until Phases 5-6, so a
# configured default does not affect bare `docs check` and the provenance
# parenthetical is not yet emitted. These fail as plain assertion mismatches
# (exit code / stdout substring), not tracebacks or argparse refusals.
#
# Phase 3 fixture: `_stale_config_tree` mirrors `_stale_tree` but emits the
# `[check] stale_days = N` sidecar; the stale doc's `Updated:` is
# `today`-relative so the case never rots.


def _stale_config_tree(tmp_path: Path, name: str, *, stale_days: int) -> Path:
    """A docs root with `[check] stale_days = N` + one ancient active doc.

    Mirrors `_stale_tree`, adding the `[check]` sidecar. The ancient doc is
    400 days old (well past any small window), so a configured `stale_days`
    makes bare `docs check` flag it.
    """
    root = tmp_path / name
    root.mkdir()
    (root / ".docs.toml").write_text(
        f'[project]\nname = "{name}"\n\n[check]\nstale_days = {stale_days}\n'
    )
    old = (date.today() - timedelta(days=400)).isoformat()
    (root / "ancient.md").write_text(
        f"# Ancient\n\nLifecycle: active\nRole: notes\nProject: {name}\nUpdated: {old}\n\nBody.\n"
    )
    return root


def test_check_config_stale_days_applies_to_bare_check(docs_script, tmp_path):
    """HEADLINE D2 (Q5): a configured `[check] stale_days` makes BARE
    `docs check` (no `--stale` flag) apply the stale rule → exit 1.
    """
    root = _stale_config_tree(tmp_path, "cfg-bare", stale_days=30)
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "ancient.md" in proc.stdout
    assert "stale" in proc.stdout.lower()


def test_check_cli_stale_overrides_config(docs_script, tmp_path):
    """An explicit CLI `--stale 99999` overrides the configured `stale_days`,
    clearing the ancient doc → exit 0 (CLI wins).
    """
    root = _stale_config_tree(tmp_path, "cfg-override", stale_days=30)
    proc = _run(docs_script, "check", str(root), "--stale", "99999")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


def test_check_no_check_section_unchanged(docs_script, tmp_path):
    """GREEN-at-baseline regression lock: a tree with NO `[check]` section and
    an old active doc, checked bare (no `--stale`), is unchanged → exit 0.
    """
    root = _stale_tree(tmp_path, "no-check-section", include_fresh=False)
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


def test_check_config_sourced_provenance_message(docs_script, tmp_path):
    """A config-sourced stale finding names the file + key so the operator
    knows where to change the window.
    """
    root = _stale_config_tree(tmp_path, "cfg-prov", stale_days=30)
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    # Full frozen parenthetical (Decision: BINDING), not just the trailing clause.
    assert "(stale threshold 30, set in .docs.toml [check] stale_days)" in proc.stdout
    # Mutually exclusive with the CLI-sourced variant — config did not come via --stale.
    assert "via --stale" not in proc.stdout


def test_check_cli_sourced_provenance_message(docs_script, tmp_path):
    """A CLI-sourced stale finding names `--stale` and does NOT carry the
    config clause (the threshold did not come from the config).
    """
    root = _stale_tree(tmp_path, "cli-prov", include_fresh=False)
    proc = _run(docs_script, "check", str(root), "--stale", "30")
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    # Full frozen parenthetical (Decision: BINDING), not just the trailing clause.
    assert "(stale threshold 30, via --stale)" in proc.stdout
    assert "set in .docs.toml [check] stale_days" not in proc.stdout


def test_check_stale_zero_honored(docs_script, tmp_path):
    """GREEN-at-baseline: `--stale 0` is honoured as given (flag every active
    doc not updated *today*), not treated as unset. An old active doc → 1.
    """
    root = _stale_tree(tmp_path, "stale-zero", include_fresh=False)
    proc = _run(docs_script, "check", str(root), "--stale", "0")
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "ancient.md" in proc.stdout
