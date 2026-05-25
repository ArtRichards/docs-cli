"""Unit tests for the M3 validators (Phase 2 — written RED).

Targets: `check_doc`, `check_tree`, `exit_code_for`, `Finding`. The per-doc
rule tests use inline strings; the tree tests point at fixture trees.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from docs import (
    BUILTIN_ROLES,
    BUILTIN_STATUSES,
    Config,
    Finding,
    check_doc,
    check_tree,
    exit_code_for,
    load_config,
)

_TODAY = date(2026, 5, 22)


def _config() -> Config:
    return Config(
        project="probe",
        archive_dir="archive",
        date_format="%Y-%m-%d",
        lifecycles=BUILTIN_STATUSES,
        roles=BUILTIN_ROLES,
    )


def _valid(status: str = "active", role: str = "spec", updated: str = "2026-05-20") -> str:
    """A well-formed doc body with one field optionally varied.

    The `status` parameter name is kept for back-compat with the existing
    test helper call sites; the on-disk key is M7's `Lifecycle:`.
    """
    return (
        f"# Sample\n\nLifecycle: {status}\nRole: {role}\n"
        f"Project: probe\nUpdated: {updated}\n\nBody paragraph.\n"
    )


# --- clean doc -------------------------------------------------------------


def test_check_doc_clean_doc_has_no_findings():
    findings = check_doc(
        Path("/r/sample.md"), _valid(), Path("/r"), _config(), stale=None, today=_TODAY
    )
    assert findings == []


# --- missing / empty required fields --------------------------------------


def test_check_doc_missing_status():
    text = "# Sample\n\nRole: spec\nProject: probe\nUpdated: 2026-05-20\n\nBody.\n"
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=None, today=_TODAY)
    assert [f.rule for f in findings] == ["missing-field"]
    assert findings[0].severity == "error"
    assert "Lifecycle" in findings[0].message


def test_check_doc_empty_required_field():
    text = "# Sample\n\nLifecycle: active\nRole:\nProject: probe\nUpdated: 2026-05-20\n\nBody.\n"
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=None, today=_TODAY)
    assert [f.rule for f in findings] == ["missing-field"]
    assert "Role" in findings[0].message


def test_check_doc_missing_h1_is_malformed():
    text = "Lifecycle: active\nRole: spec\nProject: probe\nUpdated: 2026-05-20\n\nBody.\n"
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=None, today=_TODAY)
    assert [f.rule for f in findings] == ["malformed"]
    assert findings[0].severity == "error"


# --- vocabulary -----------------------------------------------------------


def test_check_doc_unknown_status():
    findings = check_doc(
        Path("/r/d.md"),
        _valid(status="frobnicated"),
        Path("/r"),
        _config(),
        stale=None,
        today=_TODAY,
    )
    assert [f.rule for f in findings] == ["bad-vocab"]
    assert "frobnicated" in findings[0].message


def test_check_doc_unknown_role():
    findings = check_doc(
        Path("/r/d.md"),
        _valid(role="wizard"),
        Path("/r"),
        _config(),
        stale=None,
        today=_TODAY,
    )
    assert [f.rule for f in findings] == ["bad-vocab"]
    assert "wizard" in findings[0].message


# --- date -----------------------------------------------------------------


def test_check_doc_unparseable_date():
    findings = check_doc(
        Path("/r/d.md"),
        _valid(updated="2026-13-99"),
        Path("/r"),
        _config(),
        stale=None,
        today=_TODAY,
    )
    assert [f.rule for f in findings] == ["bad-date"]
    assert findings[0].severity == "error"


# --- status / location drift ---------------------------------------------


def test_check_doc_archived_status_outside_archive_subtree(tmp_path):
    doc = tmp_path / "stray.md"
    findings = check_doc(
        doc, _valid(status="archived"), tmp_path, _config(), stale=None, today=_TODAY
    )
    assert [f.rule for f in findings] == ["status-drift"]
    assert findings[0].severity == "error"


def test_check_doc_active_status_inside_archive_subtree(tmp_path):
    doc = tmp_path / "archive" / "2026-01-01" / "lingering.md"
    findings = check_doc(
        doc, _valid(status="active"), tmp_path, _config(), stale=None, today=_TODAY
    )
    assert [f.rule for f in findings] == ["status-drift"]


def test_check_doc_archived_status_inside_archive_is_clean(tmp_path):
    doc = tmp_path / "archive" / "2026-01-01" / "proper.md"
    findings = check_doc(
        doc, _valid(status="archived"), tmp_path, _config(), stale=None, today=_TODAY
    )
    assert findings == []


# --- broken Related: refs -------------------------------------------------


def test_check_doc_broken_related_ref(tmp_path):
    (tmp_path / "exists.md").write_text(_valid())
    text = (
        "# Sample\n\nLifecycle: active\nRole: spec\nProject: probe\n"
        "Updated: 2026-05-20\n\nRelated:\n- pairs-with: ghost.md\n\nBody.\n"
    )
    findings = check_doc(
        tmp_path / "sample.md", text, tmp_path, _config(), stale=None, today=_TODAY
    )
    assert [f.rule for f in findings] == ["broken-ref"]
    assert "ghost.md" in findings[0].message


def test_check_doc_resolvable_related_ref_is_clean(tmp_path):
    (tmp_path / "exists.md").write_text(_valid())
    text = (
        "# Sample\n\nLifecycle: active\nRole: spec\nProject: probe\n"
        "Updated: 2026-05-20\n\nRelated:\n- pairs-with: exists.md\n\nBody.\n"
    )
    findings = check_doc(
        tmp_path / "sample.md", text, tmp_path, _config(), stale=None, today=_TODAY
    )
    assert findings == []


# --- stale ----------------------------------------------------------------


def test_check_doc_stale_active_doc_warns_when_stale_set():
    text = _valid(status="active", updated="2026-01-01")
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=30, today=_TODAY)
    assert [f.rule for f in findings] == ["stale"]
    assert findings[0].severity == "warning"


def test_check_doc_stale_not_reported_without_stale_flag():
    text = _valid(status="active", updated="2026-01-01")
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=None, today=_TODAY)
    assert findings == []


def test_check_doc_stale_ignores_non_active_docs():
    text = _valid(status="draft", updated="2026-01-01")
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=30, today=_TODAY)
    assert findings == []


def test_check_doc_recent_active_doc_not_stale():
    text = _valid(status="active", updated="2026-05-20")
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=30, today=_TODAY)
    assert findings == []


# --- exit_code_for --------------------------------------------------------


def test_exit_code_for_no_findings_is_zero():
    assert exit_code_for([]) == 0


def test_exit_code_for_warnings_only_is_one():
    findings = [Finding(Path("/r/d.md"), "warning", "stale", "stale doc")]
    assert exit_code_for(findings) == 1


def test_exit_code_for_any_error_is_two():
    findings = [
        Finding(Path("/r/d.md"), "warning", "stale", "stale doc"),
        Finding(Path("/r/e.md"), "error", "bad-vocab", "bad status"),
    ]
    assert exit_code_for(findings) == 2


# --- check_tree -----------------------------------------------------------


def test_check_tree_clean_tree_has_no_findings(fixtures_dir):
    root = fixtures_dir / "trees" / "minimal"
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    assert findings == []


def test_check_tree_drift_tree_reports_status_drift(fixtures_dir):
    root = fixtures_dir / "trees" / "drift"
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    assert {f.rule for f in findings} == {"status-drift"}
    assert len(findings) == 2


def test_check_tree_invalid_tree_reports_every_rule(fixtures_dir):
    root = fixtures_dir / "trees" / "invalid"
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    rules = {f.rule for f in findings}
    assert {"missing-field", "bad-vocab", "bad-date", "broken-ref", "malformed"} <= rules


def test_check_tree_findings_sorted_by_path(fixtures_dir):
    root = fixtures_dir / "trees" / "invalid"
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    paths = [f.path.as_posix() for f in findings]
    assert paths == sorted(paths)
