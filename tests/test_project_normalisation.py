"""F11 — project-name normalisation to lowercase-kebab (Phase 2, RED).

The 2026-05-24 multi-tree trial produced 25 distinct project values inferred
from directory names — 16 of them in non-conformant shapes (TitleCase,
SNAKE_UPPER, digit-glued, mixed underscore). M7's F11 normalises the inferred
project name to lowercase-kebab via the OQ-B rule (split on case boundaries +
underscores + letter-to-digit boundaries; preserve digit-after-digit).

The tests drive `plan_migration` end-to-end against tmp trees whose directory
names exercise each casing shape (OQ7, 2026-05-24: never import undefined
names). The plan record's `.project` field carries the normalised value;
human-output testing goes through the `docs migrate` CLI to assert the
"(normalised from \"<original>\")" annotation surfaces when normalisation
changed the value (and is suppressed when it didn't).

`--config-project <name>` (the one new M7 CLI flag, per F5) short-circuits
normalisation entirely — when set, the override is used verbatim and no
"(normalised from …)" annotation appears (OQ2, 2026-05-24).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

import pytest

from docs import plan_migration


def _seed(fixture_root, tmp_path, dir_name):
    """Copy `fixture_root/<dir_name>/` into tmp_path; return the copy's path."""
    src = fixture_root / dir_name
    dst = tmp_path / dir_name
    shutil.copytree(src, dst)
    return dst


# --- F11 — TitleCase / snake-upper / mixed underscore -----------------------


@pytest.mark.parametrize(
    "dir_name,expected_project",
    [
        ("FooBarBaz", "foo-bar-baz"),
        ("FOO_BAR_BAZ", "foo-bar-baz"),
        ("Foo_Bar_Baz", "foo-bar-baz"),
        ("Plan", "plan"),
    ],
)
def test_normalise_project_name_titlecase(fixtures_dir, tmp_path, dir_name, expected_project):
    """TitleCase / SNAKE_UPPER / mixed-underscore TitleCase / bare TitleCase
    single word — every case normalises to lowercase-kebab. Today the
    project value is inherited verbatim from the directory name, so each
    case fails for its own (wrong) value.
    """
    tree = _seed(fixtures_dir / "project-names", tmp_path, dir_name)
    plan = plan_migration(tree)
    assert plan.files
    for fm in plan.files:
        assert fm.project == expected_project, (
            f"expected normalised project={expected_project!r}, got {fm.project!r} "
            f"for dir {dir_name!r}"
        )


# --- F11 — digit-glued lowercase (OQ-B) ------------------------------------


@pytest.mark.parametrize(
    "dir_name,expected_project",
    [
        ("Abc5Migration", "abc-5-migration"),
    ],
)
def test_normalise_project_name_digit_glued(fixtures_dir, tmp_path, dir_name, expected_project):
    """Letter-to-digit boundaries split (OQ-B): `Abc5Migration` →
    `abc-5-migration`. Today digit-glued names inherit the directory name
    verbatim and fail the convention's lowercase-kebab implicit shape.
    """
    tree = _seed(fixtures_dir / "project-names", tmp_path, dir_name)
    plan = plan_migration(tree)
    assert plan.files
    for fm in plan.files:
        assert fm.project == expected_project, (
            f"expected normalised project={expected_project!r}, got {fm.project!r} "
            f"for dir {dir_name!r}"
        )


# --- F11 — already-kebab + digit-after-digit pass through (regression lock) -


@pytest.mark.parametrize(
    "dir_name,expected_project",
    [
        ("embedded-ai-discovery-parallel", "embedded-ai-discovery-parallel"),
        ("bugs-2026-01-26", "bugs-2026-01-26"),
    ],
)
def test_normalise_project_name_kebab_passes_through(
    fixtures_dir, tmp_path, dir_name, expected_project
):
    """A kebab-case directory name is already conformant — the normaliser
    must not mangle it. Digit-after-digit (e.g. `2026-01-26`) must NOT
    trigger a split (OQ-B: preserve dates).

    Regression lock — GREEN at baseline today, must stay GREEN through
    Phase 6. (Today the inferred project for `embedded-ai-discovery-parallel`
    is built from the common-prefix or dir-name path; this fixture is
    crafted so the dir name wins, and the expected output equals the input.)
    """
    tree = _seed(fixtures_dir / "project-names", tmp_path, dir_name)
    plan = plan_migration(tree)
    assert plan.files
    for fm in plan.files:
        assert fm.project == expected_project, (
            f"expected {expected_project!r}, got {fm.project!r} for dir {dir_name!r}"
        )


# --- F5 / F11 — --config-project CLI override -------------------------------


def test_config_project_cli_override_wins_over_normalisation(docs_script, fixtures_dir, tmp_path):
    """`docs migrate <dir> --config-project override` short-circuits
    normalisation entirely (OQ2): every plan record carries
    `project == "override"`, and the human output must NOT contain
    "(normalised from …)" because the override path bypasses normalisation.

    Today `--config-project` is not a recognised argparse argument — the
    subprocess exits with argparse's usage error (2), and JSON cannot
    parse, so this fails RED on the argparse layer.
    """
    tree = _seed(fixtures_dir / "project-names", tmp_path, "FooBarBaz")
    # JSON-mode invocation pins every plan record's project value.
    proc_json = subprocess.run(
        [
            sys.executable,
            str(docs_script),
            "migrate",
            str(tree),
            "--config-project",
            "override",
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    assert proc_json.returncode == 0, (proc_json.stdout, proc_json.stderr)
    data = json.loads(proc_json.stdout)
    assert data, "expected at least one record"
    for rec in data:
        assert rec["project"] == "override", rec

    # Human-mode invocation must NOT carry the normalisation annotation.
    proc_human = subprocess.run(
        [
            sys.executable,
            str(docs_script),
            "migrate",
            str(tree),
            "--config-project",
            "override",
        ],
        capture_output=True,
        text=True,
    )
    assert proc_human.returncode == 0, (proc_human.stdout, proc_human.stderr)
    assert "(normalised from" not in proc_human.stdout, (
        "with --config-project set, the human plan output must not show "
        "'(normalised from \"X\")' — the override path short-circuits "
        "normalisation entirely (OQ2, 2026-05-24)."
    )


# --- F11 — plan human output surfaces "(normalised from …)" ----------------


def test_migrate_plan_human_output_shows_normalised_from_when_changed(
    docs_script, fixtures_dir, tmp_path
):
    """When normalisation changed the project value (e.g. `FooBarBaz` →
    `foo-bar-baz`), the human dry-run output must surface the original
    inline as `project: foo-bar-baz (normalised from "FooBarBaz")` so the
    operator can spot mis-normalisations. Today no such annotation exists.
    """
    tree = _seed(fixtures_dir / "project-names", tmp_path, "FooBarBaz")
    proc = subprocess.run(
        [sys.executable, str(docs_script), "migrate", str(tree)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "foo-bar-baz" in proc.stdout
    assert '(normalised from "FooBarBaz")' in proc.stdout, proc.stdout


def test_migrate_plan_human_output_omits_normalised_from_when_unchanged(
    docs_script, fixtures_dir, tmp_path
):
    """When the inferred project value is already conformant (kebab-case),
    the human output must NOT emit the "(normalised from …)" annotation —
    no signal-noise on the dominant happy path.

    Regression lock — GREEN at baseline today (the annotation doesn't
    exist yet so it correctly doesn't appear).
    """
    tree = _seed(fixtures_dir / "project-names", tmp_path, "embedded-ai-discovery-parallel")
    proc = subprocess.run(
        [sys.executable, str(docs_script), "migrate", str(tree)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "(normalised from" not in proc.stdout, (
        "no annotation expected for an already-kebab project name; got:\n" + proc.stdout
    )
