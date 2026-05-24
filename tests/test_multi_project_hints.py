"""F5 — multi-project tree hints + `--config-project` override (Phase 2, RED).

Trial 1 (2026-05-24) saw a 185-file generated-data subdir muddy the migration
plan. Trial 2 reframed the problem: multi-project trees (one parent dir
hosting multiple semantic sub-projects) are common in monorepo doc roots,
and the tool should help an agent recognise them — without baking the
decision into the verb.

The heuristic (per F5): for each immediate subdir, compute the longest
common filename prefix among `.md` files. If that prefix differs meaningfully
from the parent's inferred project AND covers ≥ 5 `.md` files, emit one
advisory hint in the plan footer. The agent then picks one of three actions:
ignore, exclude + recurse, or `--config-project` override.

The one new M7 CLI flag is `--config-project <name>` on `docs migrate` —
overrides the inferred project for the run; consumed by every plan record.
"""

from __future__ import annotations

import json
import subprocess
import sys


def _write(path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _make_multi_project_tree(root, parent_files=5, child_subdir="foo-tools", child_files=6):
    """Make a tmp foreign tree with a parent dir + one distinct-prefix subdir.

    Parent root holds N kebab-prefixed `parent-*` files (a single project);
    the subdir holds M files whose common filename prefix `foo_tools_` is
    distinct from the parent's inferred project AND covers ≥ 5 files.
    """
    for i in range(parent_files):
        _write(root / f"parent-{i}-spec.md", f"# Parent {i}\n\nBody.\n")
    sub = root / child_subdir
    for i in range(child_files):
        _write(sub / f"foo_tools_thing_{i}.md", f"# Foo Tools Thing {i}\n\nBody.\n")


# --- F5 — hint emitted when subdir's common prefix differs (≥ 5 files) -----


def test_subdir_with_distinct_common_prefix_emits_hint(docs_script, tmp_path):
    """A subdir of 6 `.md` files whose common filename prefix is distinct
    from the parent's project triggers one advisory hint in the plan
    footer. The hint names the subdir and suggests the
    `--config-project <name>` invocation.

    Today there is no multi-project hint emission — the plan footer is
    silent and this assertion fails RED.
    """
    tree = tmp_path / "multi-project"
    _make_multi_project_tree(tree, parent_files=5, child_subdir="foo-tools", child_files=6)
    proc = subprocess.run(
        [sys.executable, str(docs_script), "migrate", str(tree)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "hint:" in proc.stdout, (
        "expected a multi-project hint line in the plan footer; got:\n" + proc.stdout
    )
    assert "foo-tools" in proc.stdout, "hint must name the candidate subdir"
    assert "--config-project" in proc.stdout, "hint must suggest the --config-project invocation"


# --- F5 — subdir below the 5-file threshold: no hint (regression lock) -----


def test_subdir_below_five_file_threshold_emits_no_hint(docs_script, tmp_path):
    """A subdir with fewer than 5 `.md` files is below the heuristic
    threshold; no hint is emitted. Regression lock — GREEN at baseline
    today (no hint emission at all yet, so this trivially passes).
    """
    tree = tmp_path / "multi-project-small"
    _make_multi_project_tree(tree, parent_files=5, child_subdir="small-sub", child_files=3)
    proc = subprocess.run(
        [sys.executable, str(docs_script), "migrate", str(tree)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # "hint:" must not appear naming the small subdir.
    if "hint:" in proc.stdout:
        # Allow other unrelated hint lines; assert no hint for small-sub.
        assert "small-sub" not in proc.stdout, (
            "no hint expected for a subdir below the 5-file threshold; got:\n" + proc.stdout
        )


# --- F5 — --config-project propagates to every record ----------------------


def test_config_project_cli_flag_overrides_inferred_project_for_every_file(docs_script, tmp_path):
    """`docs migrate --config-project <name>` is the one new M7 CLI flag.
    When set, every plan record carries `project == "<name>"`, regardless
    of what the inference would have produced.

    Today the flag is not in the argparse spec — the subprocess exits
    with usage error 2, asserting RED on argparse rejection.
    """
    tree = tmp_path / "multi-project-override"
    _make_multi_project_tree(tree, parent_files=5, child_subdir="foo-tools", child_files=6)
    proc = subprocess.run(
        [
            sys.executable,
            str(docs_script),
            "migrate",
            str(tree),
            "--config-project",
            "my-custom-name",
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    data = json.loads(proc.stdout)
    assert data, "expected at least one record"
    for rec in data:
        assert rec["project"] == "my-custom-name", rec
