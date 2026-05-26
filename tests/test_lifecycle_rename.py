"""F0 — `Status:` → `Lifecycle:` controlled-vocab rename (Phase 2, RED).

The 2026-05-24 multi-tree trial found that almost every real-world foreign doc
uses `Status:` as a free-form progress line ("Implemented; retained as design
record", "Draft normative companion spec", …). Today's parser coerces that
prose into the controlled-vocab `Status:` field, silently dropping the original.

M7 resolves the collision by renaming the controlled-vocab field to
`Lifecycle:`. Free-form `Status:` lines become extra metadata, preserved
verbatim into the `## Migrated metadata` body section. Breaking change — no
backward-compat window (operator decision, 2026-05-24).

These tests pin the contract before Phase 5 lands the parser change. Every
assertion fails at the RED baseline for its intended unimplemented reason
(parser still only knows `Status:`); they flip GREEN once Phase 5 ships the
rename.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from docs import Confidence, FileMigration, MetadataError, apply_migration, parse, plan_migration

# --- Parser-level: accept Lifecycle:, reject Status: as the controlled key ---


def test_parse_accepts_lifecycle_key(fixtures_dir):
    """Test 1 — Parser accepts `Lifecycle: active` as the controlled-vocab key.

    Today the parser requires `Status:`; it raises `MetadataError: missing
    Status` on this fixture. Phase 5 flips the parser to require `Lifecycle:`
    instead, after which the parse succeeds and `doc.lifecycle == "active"`
    (the dataclass attribute is renamed in lockstep — OQ1).
    """
    fixture = fixtures_dir / "lifecycle" / "lifecycle-key.md"
    text = fixture.read_text()
    doc = parse(text, fixture, fixture.parent)
    assert doc.lifecycle == "active"


def test_parse_rejects_status_as_controlled_vocab_key(fixtures_dir):
    """Test 2 — Parser rejects `Status:` as the controlled-vocab key.

    With the rename, a doc that carries `Status: active` but no `Lifecycle:`
    line is missing the required controlled-vocab field; `parse()` must raise
    `MetadataError`. Today the parser happily accepts `Status:` (and ignores
    the absence of `Lifecycle:`), so this assertion fails RED.
    """
    fixture = fixtures_dir / "lifecycle" / "status-only.md"
    text = fixture.read_text()
    try:
        parse(text, fixture, fixture.parent)
    except MetadataError:
        return
    raise AssertionError(
        "parse() must raise MetadataError when the controlled-vocab "
        "Lifecycle: line is missing (Status: alone is a free-form prose line)."
    )


# --- `docs check` exit codes on Status: vs Lifecycle: ----------------------


def test_check_errors_on_status_without_lifecycle(docs_script, fixtures_dir, tmp_path):
    """Test 3 — `docs check` exits 2 on a tree whose docs use `Status:` as
    the controlled-vocab key without a `Lifecycle:` line.

    After the rename, `Status: active` is a free-form extra field, and the
    doc is missing its required `Lifecycle:` line — that's a `missing-field`
    error (exit 2). Today the same tree passes `docs check` cleanly.
    """
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / ".docs.toml").write_text('[project]\nname = "demo"\n')
    shutil.copy(fixtures_dir / "lifecycle" / "status-only.md", tree / "status-only.md")
    proc = subprocess.run(
        [sys.executable, str(docs_script), "check", str(tree)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)


def test_check_accepts_lifecycle_with_freeform_status_line(docs_script, fixtures_dir, tmp_path):
    """Test 4 — `docs check` accepts a doc that carries `Lifecycle: active`
    plus a free-form `Status: <prose>` line.

    Phase 5's parser treats `Status:` as a non-required extra metadata field;
    the doc is valid because every required field is present. Today the
    parser's vocabulary check fires on the prose value and exits 2.
    """
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / ".docs.toml").write_text('[project]\nname = "demo"\n')
    shutil.copy(
        fixtures_dir / "lifecycle" / "lifecycle-plus-status-prose.md",
        tree / "lifecycle-plus-status-prose.md",
    )
    proc = subprocess.run(
        [sys.executable, str(docs_script), "check", str(tree)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


# --- `docs migrate` preserves free-form Status: prose -----------------------


@pytest.mark.parametrize(
    "fixture_name",
    # All four single-line prose shapes from Phase 3's status-prose/ fixtures.
    # Per OQ-3 (2026-05-24 resolution), all are single-line; multi-line
    # `Status:` continuation is out of scope for M7. Review finding #8:
    # parametrise so each prose shape is covered, not just freeform-status.md.
    [
        "freeform-status.md",
        "draft-companion.md",
        "planning-only.md",
        "p0-implemented.md",
    ],
)
def test_migrate_preserves_freeform_status_as_migrated_metadata(
    fixture_name, fixtures_dir, tmp_path
):
    """Test 5 — `docs migrate` preserves a foreign tree's `Status: <prose>`
    line through the migration.

    With F0, `Status:` is no longer special; the existing extra-field
    preservation path catches it and parks it under `## Migrated metadata`
    as `Migrated-Status: <prose>` (or otherwise carries it through — the
    test accepts any documented preservation shape). Today migrate coerces
    the prose to a built-in vocab and silently drops the original.

    Parametrised over all 4 single-line prose shapes in
    `tests/fixtures/status-prose/` (review finding #8).
    """
    src = fixtures_dir / "status-prose" / fixture_name
    tree = tmp_path / "foreign"
    tree.mkdir()
    shutil.copy(src, tree / fixture_name)

    plan = plan_migration(tree)
    apply_migration(plan)

    after = (tree / fixture_name).read_text()
    # Either preserved under `## Migrated metadata` with a `Migrated-Status:`
    # line, OR the file gains a `Lifecycle:` line AND the original `Status:`
    # prose is preserved verbatim somewhere in the file. The first shape is
    # what the M4 extra-field-preservation code already produces once
    # `Status:` is no longer a required field.
    has_lifecycle_line = any(line.startswith("Lifecycle:") for line in after.splitlines())
    # Review finding #6: parenthesise the second clause so the `or` /
    # `and` precedence is explicit. Without the parens, Python evaluates
    # `or` lowest-precedence (correct here by coincidence, but the
    # operator precedence shouldn't be load-bearing).
    preserved_prose = "Migrated-Status:" in after or (
        "## Migrated metadata" in after and "Status:" in after
    )
    assert has_lifecycle_line, f"migrate must write a Lifecycle: line into the doc; got:\n{after}"
    assert preserved_prose, (
        f"migrate must preserve the free-form Status: prose somewhere; got:\n{after}"
    )


# --- FileMigration constructor accepts the new `medium` confidence ----------


def test_file_migration_accepts_medium_confidence(tmp_path):
    """Test 6 — `FileMigration(..., confidence="medium", ambiguities=())`
    constructs successfully.

    OQ-D adds `medium` as a third confidence level between `high` and `low`.
    The dataclass `__post_init__` validator at `src/docs_cli/cli.py:264-270`
    today only accepts `("high", "low")` and rejects `medium` with a
    `ValueError`. This test pins Phase 5's validator extension as an explicit
    contract surface (review finding #9): RED today; GREEN once Phase 5
    extends the allowed set.

    Medium-confidence inferences come from derived signals (H1-content,
    section-header, sibling-set defaulting, non-role-suffix strip) and
    surface to `docs check` as warnings, not errors (exit 1, not exit 2).
    Like `high`, they carry no ambiguities — the validator must accept an
    empty `ambiguities` tuple alongside `confidence == "medium"`.
    """
    fm = FileMigration(
        path=Path(tmp_path) / "ambiguous.md",
        rel="ambiguous.md",
        role="plan",
        project="demo",
        lifecycle="active",
        updated=date(2026, 5, 25),
        synthesized_h1=False,
        reconciled_metadata=False,
        confidence=Confidence.MEDIUM,
        ambiguities=(),
        archive_move=None,
    )
    assert fm.confidence is Confidence.MEDIUM
    assert fm.ambiguities == ()


# --- `docs check` exit-code anchor for medium-confidence → warning ---------


def test_check_exits_1_on_medium_confidence_inference(docs_script, tmp_path):
    """OQ-D resolution anchor: `docs check` treats `medium` as a warning
    (exit 1), not an error (exit 2).

    Drive `docs check` against a tree whose only finding is a
    medium-confidence inference. The shape used here: a tree with a
    `.docs.toml` but a single doc that has no explicit `Role:` metadata
    line and whose role is only resolvable via the medium-confidence
    sibling-set / H1-content / section-header signals. Today `docs check`
    treats a missing required field as an error (exit 2); after Phase 6
    introduces medium-confidence inference at check time, the missing
    field becomes a medium-confidence finding (exit 1), not error
    (exit 2).

    Today this test fails RED for the intended reason: the parser raises
    `MetadataError` on the missing `Role:` line and `docs check` exits 2.
    Phase 6 wires the medium-confidence inference path so the missing
    role can be filled from H1-content, producing a warning, not an error.

    Review finding #1 — anchor the medium → warning resolution as a CLI
    exit-code contract surface so a Phase 6 implementation that always
    emits `error` (exit 2) or always emits `high` (exit 0) is caught.
    """
    tree = tmp_path / "medium-only"
    tree.mkdir()
    (tree / ".docs.toml").write_text('[project]\nname = "medium-only"\n')
    # Single doc whose role can be inferred at medium (H1 ends with a role
    # word) but is NOT explicit in the metadata block. The only finding
    # `docs check` should surface post-Phase-6 is the medium-confidence
    # inference for `Role:` — exit 1 (warning), not exit 2 (error).
    (tree / "ambiguous.md").write_text(
        "# Foo Plan\n\n"
        "Lifecycle: active\n"
        "Project: medium-only\n"
        f"Updated: {date.today().isoformat()}\n\n"
        "A plan-shaped document body.\n"
    )
    proc = subprocess.run(
        [sys.executable, str(docs_script), "check", str(tree)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1, (
        f"expected exit 1 (warning) on a medium-confidence inference; "
        f"got {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
