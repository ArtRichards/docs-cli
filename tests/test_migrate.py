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
    apply_migration,
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


def test_infer_role_trailing_token_that_is_a_builtin_role_resolves_directly():
    # A trailing token that is itself a built-in role (no _ROLE_SUFFIXES
    # entry needed) resolves to that role — `-milestone` branch of the
    # documented extension (cli.md), previously without coverage.
    role, confident = infer_role("m5-skill-milestone.md", {})
    assert role == "milestone"
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


def test_infer_updated_honours_a_non_default_date_format():
    updated, confident = infer_updated({"Updated": "04/03/2025"}, mtime=0.0, date_format="%d/%m/%Y")
    assert updated == date(2025, 3, 4)
    assert confident is True


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


# --- insert_metadata_block: extra-field preservation (review finding #3) ----


_INSERT_KW = dict(
    title="Doc",
    status="active",
    role="notes",
    project="proj",
    updated=date(2026, 5, 22),
)


def test_insert_metadata_block_preserves_extra_fields_in_a_migrated_section():
    # Owner: / Tags: are non-required metadata — they must be preserved into a
    # `## Migrated metadata` body section, not silently dropped.
    text = "# Doc\n\nStatus: wip\nOwner: alice\nTags: infra, urgent\nUpdated: 2020-01-01\n\nBody.\n"
    result = insert_metadata_block(text, **_INSERT_KW)
    assert "## Migrated metadata" in result
    assert "Migrated-Owner: alice" in result
    assert "Migrated-Tags: infra, urgent" in result
    # The required fields are NOT echoed under the Migrated- prefix.
    assert "Migrated-Status" not in result
    assert "Migrated-Updated" not in result


def test_insert_metadata_block_migrated_section_sits_below_block_above_body():
    text = "# Doc\n\nStatus: wip\nOwner: alice\nUpdated: 2020-01-01\n\nThe real body.\n"
    result = insert_metadata_block(text, **_INSERT_KW)
    block_end = result.index("Updated: 2026-05-22")
    migrated = result.index("## Migrated metadata")
    body = result.index("The real body.")
    # Order: canonical block, then `## Migrated metadata`, then the body.
    assert block_end < migrated < body


def test_insert_metadata_block_preserves_a_related_block():
    # A foreign `Related:` block (bare label + bullet sub-items) is preserved
    # verbatim under the `Migrated-Related:` label.
    text = (
        "# Doc\n\nStatus: wip\nUpdated: 2020-01-01\n"
        "Related:\n- pairs-with: other.md\n- see-also: ext.md\n\nBody.\n"
    )
    result = insert_metadata_block(text, **_INSERT_KW)
    assert "## Migrated metadata" in result
    assert "Migrated-Related:" in result
    assert "- pairs-with: other.md" in result
    assert "- see-also: ext.md" in result


def test_insert_metadata_block_no_extra_fields_emits_no_section():
    # A foreign doc whose only metadata is required fields gets NO section.
    text = "# Doc\n\nStatus: wip\nUpdated: 2020-01-01\n\nBody.\n"
    result = insert_metadata_block(text, **_INSERT_KW)
    assert "## Migrated metadata" not in result


def test_insert_metadata_block_with_extras_round_trips_through_parse():
    # The preserved fields live in the BODY — the real metadata block must
    # still carry exactly the four required fields and nothing else.
    text = "# Doc\n\nStatus: wip\nOwner: alice\nTags: x\nUpdated: 2020-01-01\n\nBody.\n"
    result = insert_metadata_block(text, **_INSERT_KW)
    doc = parse(result, Path("/r/doc.md"), Path("/r"))
    assert doc.status == "active"
    assert doc.role == "notes"
    assert doc.updated == date(2026, 5, 22)
    # parse_metadata_block must not re-harvest the Migrated- lines into the
    # block — they sit under a `## ` heading in the body.
    _title, metadata, _body = parse_metadata_block(result)
    assert set(metadata) == {"Status", "Role", "Project", "Updated"}
    # The Migrated- lines are not convention fields, so `Doc.extra` is empty.
    assert doc.extra == {}


def test_insert_metadata_block_with_extras_passes_check_doc():
    text = "# Doc\n\nStatus: wip\nOwner: alice\nUpdated: 2020-01-01\n\nBody.\n"
    result = insert_metadata_block(text, **_INSERT_KW)
    config = load_config(Path("/nonexistent"))
    findings = check_doc(
        Path("/r/doc.md"), result, Path("/r"), config, stale=None, today=date(2026, 5, 22)
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


def _by_name(plan: MigrationPlan, name: str) -> FileMigration:
    matches = [f for f in plan.files if f.rel.endswith(name)]
    assert len(matches) == 1, f"expected exactly one {name}, got {len(matches)}"
    return matches[0]


def test_plan_migration_pins_low_confidence_fixture_files(fixtures_dir):
    plan = plan_migration(_foreign(fixtures_dir))

    # proj-has-metadata.md carries an out-of-vocab `Status: wip` — inference
    # must force a built-in substitution and flag it.
    has_metadata = _by_name(plan, "proj-has-metadata.md")
    assert has_metadata.confidence == "low"
    assert has_metadata.ambiguities

    # proj-no-h1.md has no H1 — a synthesised title is an ambiguity.
    no_h1 = _by_name(plan, "proj-no-h1.md")
    assert no_h1.confidence == "low"
    assert no_h1.ambiguities

    # proj-overview.md has no role suffix — Role falls back to `notes`,
    # which is a flagged, low-confidence inference.
    overview = _by_name(plan, "proj-overview.md")
    assert overview.confidence == "low"
    assert overview.ambiguities


def test_plan_migration_pins_a_high_confidence_fixture_file(fixtures_dir):
    plan = plan_migration(_foreign(fixtures_dir))
    # proj-auth-spec.md has a clean `-spec` suffix, an H1, and no
    # pre-existing metadata — every field infers unambiguously.
    auth_spec = _by_name(plan, "proj-auth-spec.md")
    assert auth_spec.confidence == "high"
    assert auth_spec.ambiguities == ()


def test_plan_migration_pins_inferred_values_for_known_files(fixtures_dir):
    plan = plan_migration(_foreign(fixtures_dir))

    auth_spec = _by_name(plan, "proj-auth-spec.md")
    assert auth_spec.role == "spec"
    assert auth_spec.project == "proj"
    assert auth_spec.status == "active"

    deploy_log = _by_name(plan, "proj-deploy-log.md")
    assert deploy_log.role == "log"
    assert deploy_log.project == "proj"

    db_adr = _by_name(plan, "proj-db-adr.md")
    assert db_adr.role == "decision"
    assert db_adr.project == "proj"

    old_decision = _by_name(plan, "proj-old-decision.md")
    assert old_decision.role == "decision"
    assert old_decision.status == "archived"


# The foreign fixture files that carry pre-existing metadata-shaped lines.
_FIXTURES_WITH_METADATA = frozenset({"proj-has-metadata.md", "proj-extra-metadata.md"})


def test_plan_migration_marks_reconciled_metadata(fixtures_dir):
    plan = plan_migration(_foreign(fixtures_dir))
    # proj-has-metadata.md carries pre-existing Status:/Updated: lines —
    # migrate reconciles them into the block.
    has_metadata = _by_name(plan, "proj-has-metadata.md")
    assert has_metadata.reconciled_metadata is True
    # proj-extra-metadata.md additionally carries non-required fields.
    extra_metadata = _by_name(plan, "proj-extra-metadata.md")
    assert extra_metadata.reconciled_metadata is True
    # Every other fixture file has no pre-existing metadata-shaped lines.
    for fm in plan.files:
        if not any(fm.rel.endswith(name) for name in _FIXTURES_WITH_METADATA):
            assert fm.reconciled_metadata is False


def test_plan_migration_synthesized_h1_is_false_for_files_with_an_h1(fixtures_dir):
    plan = plan_migration(_foreign(fixtures_dir))
    # Only proj-no-h1.md lacks an H1; every other fixture file has one.
    for fm in plan.files:
        if not fm.rel.endswith("proj-no-h1.md"):
            assert fm.synthesized_h1 is False, f"{fm.rel} has an H1"


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


def test_plan_migration_preserves_extra_metadata_fixture(fixtures_dir):
    # proj-extra-metadata.md carries Owner: / Tags: / Related: beyond the
    # required fields — plan_migration must mark it reconciled, and an apply
    # must park those extras in a `## Migrated metadata` section.
    plan = plan_migration(_foreign(fixtures_dir))
    extra = _by_name(plan, "proj-extra-metadata.md")
    assert extra.reconciled_metadata is True


# --- archive-move collision detection (review finding #1) ------------------


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_plan_migration_flags_archive_move_destination_collision(tmp_path):
    # Two foreign files with the same basename in different archive-style
    # subdirs both normalise to archive/<date>/dup.md — a silent-overwrite
    # hazard the plan must surface as an ambiguity before --apply.
    _write(tmp_path / "archived" / "dup.md", "# One\n\nFirst body.\n")
    _write(tmp_path / "project-history" / "dup.md", "# Two\n\nSecond body.\n")
    plan = plan_migration(tmp_path, archive_date="2026-05-22")
    colliding = [f for f in plan.files if f.rel.endswith("dup.md")]
    assert len(colliding) == 2
    for fm in colliding:
        assert fm.archive_move == "archive/2026-05-22/dup.md"
        assert fm.confidence == "low"
        assert any("collision" in note for note in fm.ambiguities)


def test_plan_migration_no_collision_for_distinct_archive_basenames(tmp_path):
    _write(tmp_path / "archived" / "a.md", "# A\n\nBody.\n")
    _write(tmp_path / "project-history" / "b.md", "# B\n\nBody.\n")
    plan = plan_migration(tmp_path, archive_date="2026-05-22")
    for fm in plan.files:
        assert not any("collision" in note for note in fm.ambiguities)


def test_apply_migration_raises_on_archive_move_collision(tmp_path):
    # apply_migration must refuse to silently overwrite a colliding archive
    # destination — mirroring the _archive_one FileExistsError guard.
    _write(tmp_path / "archived" / "dup.md", "# One\n\nFirst body.\n")
    _write(tmp_path / "project-history" / "dup.md", "# Two\n\nSecond body.\n")
    plan = plan_migration(tmp_path, archive_date="2026-05-22")
    try:
        apply_migration(plan)
    except FileExistsError:
        pass
    else:
        raise AssertionError("apply_migration must raise FileExistsError on a collision")
