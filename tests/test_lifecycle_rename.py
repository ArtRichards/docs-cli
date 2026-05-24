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

from docs import MetadataError, apply_migration, parse, plan_migration

# --- Parser-level: accept Lifecycle:, reject Status: as the controlled key ---


def test_parse_accepts_lifecycle_key(fixtures_dir):
    """Test 1 — Parser accepts `Lifecycle: active` as the controlled-vocab key.

    Today the parser requires `Status:`; it raises `MetadataError: missing
    Status` on this fixture. Phase 5 flips the parser to require `Lifecycle:`
    instead, after which the parse succeeds and `doc.status == "active"`
    (the field name on `Doc` may also rename — see plan).
    """
    fixture = fixtures_dir / "lifecycle" / "lifecycle-key.md"
    text = fixture.read_text()
    doc = parse(text, fixture, fixture.parent)
    assert doc.status == "active"


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


def test_migrate_preserves_freeform_status_as_migrated_metadata(fixtures_dir, tmp_path):
    """Test 5 — `docs migrate` preserves a foreign tree's `Status: <prose>`
    line through the migration.

    With F0, `Status:` is no longer special; the existing extra-field
    preservation path catches it and parks it under `## Migrated metadata`
    as `Migrated-Status: <prose>` (or otherwise carries it through — the
    test accepts any documented preservation shape). Today migrate coerces
    the prose to a built-in vocab and silently drops the original.
    """
    src = fixtures_dir / "status-prose" / "freeform-status.md"
    tree = tmp_path / "foreign"
    tree.mkdir()
    shutil.copy(src, tree / "freeform-status.md")

    plan = plan_migration(tree)
    apply_migration(plan)

    after = (tree / "freeform-status.md").read_text()
    # Either preserved under `## Migrated metadata` with a `Migrated-Status:`
    # line, OR the file gains a `Lifecycle:` line AND the original `Status:`
    # prose is preserved verbatim somewhere in the file. The first shape is
    # what the M4 extra-field-preservation code already produces once
    # `Status:` is no longer a required field.
    has_lifecycle_line = any(line.startswith("Lifecycle:") for line in after.splitlines())
    preserved_prose = (
        "Migrated-Status:" in after or "## Migrated metadata" in after and "Status:" in after
    )
    assert has_lifecycle_line, f"migrate must write a Lifecycle: line into the doc; got:\n{after}"
    assert preserved_prose, (
        f"migrate must preserve the free-form Status: prose somewhere; got:\n{after}"
    )
