"""Unit tests for the M4 migration inference + planning helpers (Phase 2, RED).

Targets: `infer_role`, `infer_project`, `infer_status`, `infer_updated`,
`detect_archive_layout`, `insert_metadata_block`, and `plan_migration`. The
pure-inference tests use inline data; `plan_migration` runs against the
`foreign/` fixture tree (Phase 3).

Every test fails at the RED baseline with `NotImplementedError` from a stub.
The contract tests assert the *shape* of the result so the implementation has
a precise target.
"""

from __future__ import annotations

import time
from datetime import date
from pathlib import Path

from docs import (
    BUILTIN_ROLES,
    BUILTIN_STATUSES,
    FileMigration,
    MigrationPlan,
    check_doc,
    detect_archive_layout,
    infer_project,
    infer_role,
    infer_status,
    infer_updated,
    insert_metadata_block,
    load_config,
    parse,
    parse_metadata_block,
    plan_migration,
)


def _foreign(fixtures_dir: Path) -> Path:
    return fixtures_dir / "trees" / "foreign"


# --- infer_role ------------------------------------------------------------


def test_infer_role_spec_suffix():
    role, confident = infer_role("auth-spec.md", {})
    assert role == "spec"
    assert confident is True


def test_infer_role_plan_suffix():
    role, confident = infer_role("release-plan.md", {})
    assert role == "plan"
    assert confident is True


def test_infer_role_adr_suffix_maps_to_decision():
    role, confident = infer_role("db-adr.md", {})
    assert role == "decision"
    assert confident is True


def test_infer_role_log_suffix():
    role, confident = infer_role("deploy-log.md", {})
    assert role == "log"
    assert confident is True


def test_infer_role_status_suffix():
    role, confident = infer_role("project-status.md", {})
    assert role == "status"
    assert confident is True


def test_infer_role_charter_suffix():
    role, confident = infer_role("product-charter.md", {})
    assert role == "charter"
    assert confident is True


def test_infer_role_guide_suffix():
    role, confident = infer_role("setup-guide.md", {})
    assert role == "guide"
    assert confident is True


def test_infer_role_runbook_suffix():
    role, confident = infer_role("incident-runbook.md", {})
    assert role == "runbook"
    assert confident is True


def test_infer_role_reference_suffix():
    role, confident = infer_role("api-reference.md", {})
    assert role == "reference"
    assert confident is True


def test_infer_role_no_suffix_falls_back_to_notes_low_confidence():
    role, confident = infer_role("random.md", {})
    assert role == "notes"
    assert confident is False


def test_infer_role_in_file_role_wins_over_suffix():
    # The filename suffix says spec; the in-file Role says guide — Role wins.
    role, confident = infer_role("auth-spec.md", {"Role": "guide"})
    assert role == "guide"
    assert confident is True


def test_infer_role_always_returns_a_builtin_role():
    for name in ("random.md", "auth-spec.md", "x-adr.md", "thing-log.md"):
        role, _ = infer_role(name, {})
        assert role in BUILTIN_ROLES


# --- infer_project ---------------------------------------------------------


def test_infer_project_common_prefix():
    names = ["proj-auth-spec.md", "proj-release-plan.md", "proj-db-adr.md"]
    assert infer_project(names, "some-dir") == "proj"


def test_infer_project_no_common_prefix_falls_back_to_dir_name():
    names = ["auth-spec.md", "release-plan.md", "db-adr.md"]
    assert infer_project(names, "fallback-dir") == "fallback-dir"


def test_infer_project_single_file():
    # A single file: its whole stem is the "common prefix"; the rule trims to
    # the last separator and falls back to the dir name when nothing usable
    # remains shared by every file. Either way the result is non-empty.
    result = infer_project(["lonely-spec.md"], "solo-dir")
    assert isinstance(result, str) and result


# --- infer_status ----------------------------------------------------------


def test_infer_status_in_file_status_wins():
    status, confident = infer_status({"Status": "blocked"}, in_archive=False)
    assert status == "blocked"
    assert confident is True


def test_infer_status_archive_membership_defaults_to_archived():
    status, confident = infer_status({}, in_archive=True)
    assert status == "archived"


def test_infer_status_default_active_in_active_tree():
    status, _ = infer_status({}, in_archive=False)
    assert status == "active"


def test_infer_status_out_of_vocab_in_file_value_rejected():
    # "wip" is not a built-in status — it must not leak through.
    status, confident = infer_status({"Status": "wip"}, in_archive=False)
    assert status in BUILTIN_STATUSES
    assert status != "wip"


def test_infer_status_always_returns_a_builtin_status():
    for meta, in_arch in (({}, False), ({}, True), ({"Status": "nonsense"}, False)):
        status, _ = infer_status(meta, in_archive=in_arch)
        assert status in BUILTIN_STATUSES


# --- infer_updated ---------------------------------------------------------


def test_infer_updated_in_file_line_parses():
    updated, confident = infer_updated({"Updated": "2025-03-04"}, mtime=0.0)
    assert updated == date(2025, 3, 4)
    assert confident is True


def test_infer_updated_no_line_falls_back_to_mtime():
    mtime = time.mktime(date(2024, 7, 15).timetuple())
    updated, confident = infer_updated({}, mtime=mtime)
    assert updated == date(2024, 7, 15)
    assert confident is False


def test_infer_updated_malformed_in_file_value_falls_back_to_mtime():
    mtime = time.mktime(date(2024, 7, 15).timetuple())
    updated, confident = infer_updated({"Updated": "not-a-date"}, mtime=mtime)
    assert updated == date(2024, 7, 15)
    assert confident is False


# --- detect_archive_layout -------------------------------------------------


def test_detect_archive_layout_archived_dir_is_normalised():
    dest = detect_archive_layout("archived/old.md", "2026-05-22")
    assert dest == "archive/2026-05-22/old.md"


def test_detect_archive_layout_project_history_dir_is_normalised():
    dest = detect_archive_layout("project-history/x.md", "2026-05-22")
    assert dest == "archive/2026-05-22/x.md"


def test_detect_archive_layout_already_conformant_archive_returns_none():
    # archive/<valid-date>/y.md is already conformant — no move (resolved Q2).
    assert detect_archive_layout("archive/2026-01-01/y.md", "2026-05-22") is None


def test_detect_archive_layout_active_tree_file_returns_none():
    assert detect_archive_layout("spec.md", "2026-05-22") is None


# --- insert_metadata_block -------------------------------------------------


def test_insert_metadata_block_h1_present_inserts_between_h1_and_body():
    text = "# Auth Spec\n\nThis is the body paragraph.\n"
    result = insert_metadata_block(
        text,
        title="Auth Spec",
        status="active",
        role="spec",
        project="proj",
        updated=date(2026, 5, 22),
    )
    title, metadata, body = parse_metadata_block(result)
    assert title == "Auth Spec"
    assert metadata["Status"] == "active"
    assert metadata["Role"] == "spec"
    assert metadata["Project"] == "proj"
    assert metadata["Updated"] == "2026-05-22"
    # The original body survives verbatim.
    assert "This is the body paragraph." in body


def test_insert_metadata_block_no_h1_synthesises_one():
    text = "First line is body text, no heading.\n"
    result = insert_metadata_block(
        text,
        title="Proj No H1",
        status="active",
        role="notes",
        project="proj",
        updated=date(2026, 5, 22),
    )
    assert result.startswith("# Proj No H1\n")
    title, metadata, body = parse_metadata_block(result)
    assert title == "Proj No H1"
    assert "First line is body text" in body


def test_insert_metadata_block_reconciles_existing_metadata_lines():
    # The file already carries Status:/Updated:-shaped lines; the block must
    # not end up with duplicate Status: lines.
    text = "# Has Metadata\n\nStatus: wip\nUpdated: 2020-01-01\n\nBody text.\n"
    result = insert_metadata_block(
        text,
        title="Has Metadata",
        status="active",
        role="notes",
        project="proj",
        updated=date(2026, 5, 22),
    )
    assert result.count("Status:") == 1
    assert result.count("Updated:") == 1
    _title, metadata, _body = parse_metadata_block(result)
    assert metadata["Status"] == "active"
    assert metadata["Updated"] == "2026-05-22"


def test_insert_metadata_block_preserves_trailing_newline():
    with_nl = "# Doc\n\nBody.\n"
    without_nl = "# Doc\n\nBody."
    kw = dict(
        title="Doc",
        status="active",
        role="notes",
        project="proj",
        updated=date(2026, 5, 22),
    )
    assert insert_metadata_block(with_nl, **kw).endswith("\n")
    assert not insert_metadata_block(without_nl, **kw).endswith("\n")


def test_insert_metadata_block_result_round_trips_through_parse():
    text = "# Round Trip\n\nBody paragraph here.\n"
    result = insert_metadata_block(
        text,
        title="Round Trip",
        status="active",
        role="spec",
        project="proj",
        updated=date(2026, 5, 22),
    )
    doc = parse(result, Path("/r/round-trip.md"), Path("/r"))
    assert doc.status == "active"
    assert doc.role == "spec"
    assert doc.project == "proj"
    assert doc.updated == date(2026, 5, 22)


def test_insert_metadata_block_result_passes_check_doc():
    text = "# Checkable\n\nBody.\n"
    result = insert_metadata_block(
        text,
        title="Checkable",
        status="active",
        role="spec",
        project="proj",
        updated=date(2026, 5, 22),
    )
    config = load_config(Path("/nonexistent"))
    findings = check_doc(
        Path("/r/checkable.md"), result, Path("/r"), config, stale=None, today=date(2026, 5, 22)
    )
    assert [f for f in findings if f.severity == "error"] == []


# --- plan_migration --------------------------------------------------------


def test_plan_migration_returns_a_plan(fixtures_dir):
    plan = plan_migration(_foreign(fixtures_dir))
    assert isinstance(plan, MigrationPlan)


def test_plan_migration_one_file_migration_per_md_file(fixtures_dir):
    root = _foreign(fixtures_dir)
    plan = plan_migration(root)
    md_count = sum(1 for _ in root.rglob("*.md"))
    assert len(plan.files) == md_count
    assert all(isinstance(f, FileMigration) for f in plan.files)


def test_plan_migration_files_in_root_relative_path_order(fixtures_dir):
    plan = plan_migration(_foreign(fixtures_dir))
    rels = [f.rel for f in plan.files]
    assert rels == sorted(rels)


def test_plan_migration_confidence_and_ambiguities_are_consistent(fixtures_dir):
    plan = plan_migration(_foreign(fixtures_dir))
    for fm in plan.files:
        if fm.confidence == "high":
            assert fm.ambiguities == ()
        else:
            assert fm.confidence == "low"
            assert fm.ambiguities


def test_plan_migration_flags_the_no_h1_file(fixtures_dir):
    plan = plan_migration(_foreign(fixtures_dir))
    no_h1 = [f for f in plan.files if f.rel.endswith("proj-no-h1.md")]
    assert len(no_h1) == 1
    assert no_h1[0].synthesized_h1 is True


def test_plan_migration_archive_subdir_file_has_archive_move(fixtures_dir):
    plan = plan_migration(_foreign(fixtures_dir))
    archived = [f for f in plan.files if "archived/" in f.rel]
    assert archived, "fixture must contain an archive-style subdir file"
    for fm in archived:
        assert fm.archive_move is not None
        assert fm.archive_move.startswith("archive/")
        assert fm.status == "archived"


def test_plan_migration_active_tree_files_have_no_archive_move(fixtures_dir):
    plan = plan_migration(_foreign(fixtures_dir))
    active = [f for f in plan.files if "/" not in f.rel]
    assert active, "fixture must contain active-tree files"
    for fm in active:
        assert fm.archive_move is None
