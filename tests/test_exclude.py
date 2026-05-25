"""RED-baseline tests for M8 F3 — `--exclude` flag + `[exclude]` config + `.docsignore`.

Phase 2 of M8. Every assertion here MUST fail at Phase 4's RED baseline
for the intended unimplemented surface:

- `--exclude` is not yet an argparse argument on migrate / index / check / list
  (argparse error exit 2).
- `--exclude-ext` is not yet an argparse argument on migrate.
- `[exclude]` is not yet a recognised section in `.docs.toml`; the loader
  may silently accept the section today, but no verb honours it.
- `.docsignore` is not yet parsed at the tree root by any verb.
- The plan footer does not surface excluded counts.

All RED traces to an unimplemented contract surface. Phase 5 (argparse +
config schema + predicate helper) flips most of these from argparse-error
RED to assertion RED — forward progress. Phase 6 (walker + render) takes
them to GREEN.

Per the OQ2 planning resolution, this file has 9 distinct test functions;
parametrisation (tests 3, 5, 6, 7) expands the collected item count. The
Phase 4 log records the exact item count.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _run(docs_script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(docs_script), *args],
        capture_output=True,
        text=True,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _foreign_tree_with_subdir(root: Path) -> None:
    """Build a small foreign tree: 2 root .md files + a build/ subdir with 3 .md."""
    _write(root / "spec.md", "# Spec\n\nBody.\n")
    _write(root / "plan.md", "# Plan\n\nBody.\n")
    _write(root / "build" / "a.md", "# A\n\nGenerated.\n")
    _write(root / "build" / "b.md", "# B\n\nGenerated.\n")
    _write(root / "build" / "c.md", "# C\n\nGenerated.\n")


# --- 1. --exclude flag basic skip ------------------------------------------


def test_migrate_exclude_flag_skips_subdir(docs_script, tmp_path):
    root = tmp_path / "tree"
    _foreign_tree_with_subdir(root)
    proc = _run(docs_script, "migrate", str(root), "--exclude", "build/", "--json")
    assert proc.returncode == 0, proc.stderr
    plan = json.loads(proc.stdout)
    # Files under build/ must not appear in the JSON plan.
    paths = [entry.get("path") or entry.get("rel") or "" for entry in plan]
    assert not any("build/" in p for p in paths), (
        f"`--exclude build/` should skip every build/* file; got: {paths}"
    )


# --- 2. --exclude flag repeatable ------------------------------------------


def test_migrate_exclude_flag_is_repeatable(docs_script, tmp_path):
    root = tmp_path / "tree"
    _foreign_tree_with_subdir(root)
    _write(root / "generated" / "x.md", "# X\n\nGen.\n")
    _write(root / "generated" / "y.md", "# Y\n\nGen.\n")
    proc = _run(
        docs_script,
        "migrate",
        str(root),
        "--exclude",
        "build/",
        "--exclude",
        "generated/",
        "--json",
    )
    assert proc.returncode == 0, proc.stderr
    plan = json.loads(proc.stdout)
    paths = [entry.get("path") or entry.get("rel") or "" for entry in plan]
    assert not any("build/" in p for p in paths), paths
    assert not any("generated/" in p for p in paths), paths


# --- 3. --exclude supports glob patterns (parametric × 2) ------------------


@pytest.mark.parametrize(
    "pattern, hit_substr",
    [
        ("**/data/**", "data/"),
        ("*memo*", "memo"),
    ],
)
def test_migrate_exclude_supports_glob_patterns(docs_script, tmp_path, pattern, hit_substr):
    root = tmp_path / "tree"
    _write(root / "spec.md", "# Spec\n\nBody.\n")
    _write(root / "nested" / "data" / "x.md", "# X\n\nData.\n")
    _write(root / "nested" / "data" / "y.md", "# Y\n\nData.\n")
    _write(root / "alpha-memo.md", "# Alpha memo\n\nBody.\n")
    _write(root / "beta-memo-revised.md", "# Beta memo\n\nBody.\n")
    proc = _run(docs_script, "migrate", str(root), "--exclude", pattern, "--json")
    assert proc.returncode == 0, proc.stderr
    plan = json.loads(proc.stdout)
    paths = [entry.get("path") or entry.get("rel") or "" for entry in plan]
    assert not any(hit_substr in p for p in paths), (
        f"`--exclude {pattern}` should skip every {hit_substr!r}-matching path; got: {paths}"
    )


# --- 4. --exclude-ext skips by extension -----------------------------------


def test_migrate_exclude_ext_skips_extensions(docs_script, tmp_path):
    root = tmp_path / "tree"
    _write(root / "spec.md", "# Spec\n\nBody.\n")
    _write(root / "report.html", "<html></html>")
    _write(root / "sheet.xlsx", "binary")
    _write(root / "kept.odt", "binary")
    proc = _run(
        docs_script,
        "migrate",
        str(root),
        "--exclude-ext",
        "xlsx,html",
        "--json",
    )
    assert proc.returncode == 0, proc.stderr
    # The footer-style human output is suppressed by --json, but the
    # excluded extensions must not appear in any plan/non-md surfacing
    # surface the JSON exposes. The strict contract: stderr / stdout must
    # not surface report.html or sheet.xlsx as a "non-md sibling" line
    # (those are filtered). Phase 5/6 lands the exact JSON shape; the
    # baseline assertion is the absence of the suppressed extensions in
    # both streams.
    combined = proc.stdout + proc.stderr
    assert "report.html" not in combined, combined
    assert "sheet.xlsx" not in combined, combined
    # The non-suppressed odt sibling, if surfaced at all, may legitimately
    # appear; not asserted here.


# --- 5. [exclude] dirs applies tree-wide (parametric × 4) ------------------


@pytest.mark.parametrize("verb", ["index", "check", "list", "migrate"])
def test_docs_toml_exclude_dirs_applies_tree_wide(docs_script, tmp_path, verb):
    root = tmp_path / "tree"
    _write(
        root / ".docs.toml",
        '[project]\nname = "exclude-tree"\n\n[exclude]\ndirs = ["build"]\n',
    )
    # Two conformant root docs.
    _write(
        root / "spec.md",
        "# Spec\n\nLifecycle: draft\nRole: spec\nProject: exclude-tree\n"
        "Updated: 2026-05-25\n\nBody.\n",
    )
    _write(
        root / "plan.md",
        "# Plan\n\nLifecycle: draft\nRole: plan\nProject: exclude-tree\n"
        "Updated: 2026-05-25\n\nBody.\n",
    )
    # A malformed file under build/ — if walker honours [exclude] dirs,
    # every verb runs clean; otherwise the malformed file surfaces.
    _write(root / "build" / "malformed.md", "no metadata\n# H1\n")

    if verb == "index":
        proc = _run(docs_script, "index", "--root", str(root))
        assert proc.returncode == 0, proc.stderr + proc.stdout
        index_text = (root / "INDEX.md").read_text()
        assert "build/malformed.md" not in index_text, index_text
    elif verb == "check":
        proc = _run(docs_script, "check", str(root))
        # build/malformed.md would otherwise raise malformed/missing-meta findings
        # → exit 1. With [exclude] honoured, exit 0.
        assert proc.returncode == 0, proc.stdout + proc.stderr
    elif verb == "list":
        proc = _run(docs_script, "list", "--root", str(root), "--json")
        assert proc.returncode == 0, proc.stderr
        records = json.loads(proc.stdout)
        paths = [r.get("path", "") for r in records]
        assert not any("build/" in p for p in paths), paths
    elif verb == "migrate":
        # `migrate` accepts [exclude] (managed-marker refusal is project /
        # archive / vocabulary only — exclude is allowed on a foreign tree).
        proc = _run(docs_script, "migrate", str(root), "--json")
        assert proc.returncode == 0, proc.stderr
        plan = json.loads(proc.stdout)
        paths = [entry.get("path") or entry.get("rel") or "" for entry in plan]
        assert not any("build/" in p for p in paths), paths


# --- 6. [exclude] globs applies tree-wide (parametric × 4) -----------------


@pytest.mark.parametrize("verb", ["index", "check", "list", "migrate"])
def test_docs_toml_exclude_globs_apply_tree_wide(docs_script, tmp_path, verb):
    root = tmp_path / "tree"
    _write(
        root / ".docs.toml",
        '[project]\nname = "exclude-globs"\n\n[exclude]\nglobs = ["**/*.draft.md"]\n',
    )
    _write(
        root / "spec.md",
        "# Spec\n\nLifecycle: draft\nRole: spec\nProject: exclude-globs\n"
        "Updated: 2026-05-25\n\nBody.\n",
    )
    # A malformed draft file that the glob should skip.
    _write(root / "nested" / "wip.draft.md", "no metadata\n# WIP\n")

    if verb == "index":
        proc = _run(docs_script, "index", "--root", str(root))
        assert proc.returncode == 0, proc.stderr + proc.stdout
        index_text = (root / "INDEX.md").read_text()
        assert "wip.draft.md" not in index_text, index_text
    elif verb == "check":
        proc = _run(docs_script, "check", str(root))
        assert proc.returncode == 0, proc.stdout + proc.stderr
    elif verb == "list":
        proc = _run(docs_script, "list", "--root", str(root), "--json")
        assert proc.returncode == 0, proc.stderr
        records = json.loads(proc.stdout)
        paths = [r.get("path", "") for r in records]
        assert not any("wip.draft.md" in p for p in paths), paths
    elif verb == "migrate":
        proc = _run(docs_script, "migrate", str(root), "--json")
        assert proc.returncode == 0, proc.stderr
        plan = json.loads(proc.stdout)
        paths = [entry.get("path") or entry.get("rel") or "" for entry in plan]
        assert not any("wip.draft.md" in p for p in paths), paths


# --- 7. .docsignore syntax subset (parametric × 7 — OQ-B cases) ------------


@pytest.mark.parametrize(
    "ignore_pattern, present_files, excluded_paths, kept_paths",
    [
        # 1. trailing * — extension match
        (
            "*.tmp",
            {"keep.md": "# K\n", "scratch.tmp": "raw"},
            ["scratch.tmp"],
            ["keep.md"],
        ),
        # 2. trailing / — directory match
        (
            "data/",
            {"keep.md": "# K\n", "data/x.md": "# X\n", "data/y.md": "# Y\n"},
            ["data/x.md", "data/y.md"],
            ["keep.md"],
        ),
        # 3. leading / — anchored at tree root
        (
            "/specific.md",
            {"specific.md": "# S\n", "keep/specific.md": "# K\n"},
            ["specific.md"],
            ["keep/specific.md"],
        ),
        # 4. ** — any-segment match
        (
            "**/build/**",
            {
                "keep.md": "# K\n",
                "nested/build/y.md": "# Y\n",
                "deep/inner/build/z.md": "# Z\n",
            },
            ["nested/build/y.md", "deep/inner/build/z.md"],
            ["keep.md"],
        ),
        # 5. comment-only (no exclusion)
        (
            "# only a comment",
            {"keep.md": "# K\n", "other.md": "# O\n"},
            [],
            ["keep.md", "other.md"],
        ),
        # 6. blank lines (no exclusion)
        (
            "\n\n",
            {"keep.md": "# K\n", "other.md": "# O\n"},
            [],
            ["keep.md", "other.md"],
        ),
        # 7. negation `!keep-me.md` after a preceding `*.md` (re-include)
        (
            "*.md\n!keep-me.md",
            {"drop.md": "# D\n", "keep-me.md": "# K\n"},
            ["drop.md"],
            ["keep-me.md"],
        ),
    ],
)
def test_docsignore_syntax_subset(
    docs_script,
    tmp_path,
    ignore_pattern,
    present_files,
    excluded_paths,
    kept_paths,
):
    root = tmp_path / "tree"
    _write(root / ".docsignore", ignore_pattern + "\n")
    for rel, body in present_files.items():
        _write(root / rel, body)

    # Drive the predicate via `docs migrate --json` — every walker that
    # consults the predicate must agree, so testing one is sufficient at
    # this layer; the tree-wide tests above already cover the per-verb
    # plumbing.
    proc = _run(docs_script, "migrate", str(root), "--json")
    assert proc.returncode == 0, proc.stderr
    plan = json.loads(proc.stdout)
    paths = [entry.get("path") or entry.get("rel") or "" for entry in plan]

    for excluded in excluded_paths:
        assert excluded not in paths, (
            f"`.docsignore` pattern {ignore_pattern!r} should exclude {excluded!r}; "
            f"plan contained {paths}"
        )
    for kept in kept_paths:
        if kept.endswith(".md"):
            assert kept in paths, (
                f"`.docsignore` pattern {ignore_pattern!r} should NOT exclude {kept!r}; "
                f"plan contained {paths}"
            )


# --- 8. CLI --exclude layers over .docs.toml -------------------------------


def test_cli_exclude_layers_over_docs_toml(docs_script, tmp_path):
    root = tmp_path / "tree"
    _write(
        root / ".docs.toml",
        '[project]\nname = "layer-test"\n\n[exclude]\ndirs = ["build"]\n',
    )
    _write(root / "spec.md", "# Spec\n\nBody.\n")
    _write(root / "build" / "a.md", "# A\n\nBody.\n")
    _write(root / "generated" / "g.md", "# G\n\nBody.\n")

    proc = _run(
        docs_script,
        "migrate",
        str(root),
        "--exclude",
        "generated/",
        "--json",
    )
    assert proc.returncode == 0, proc.stderr
    plan = json.loads(proc.stdout)
    paths = [entry.get("path") or entry.get("rel") or "" for entry in plan]
    # `[exclude] dirs = ["build"]` from .docs.toml AND CLI `--exclude
    # generated/` must both apply (layered, not replaced).
    assert not any("build/" in p for p in paths), paths
    assert not any("generated/" in p for p in paths), paths


# --- 9. plan footer surfaces excluded count --------------------------------


def test_plan_footer_surfaces_excluded_count(docs_script, tmp_path):
    root = tmp_path / "tree"
    _write(root / "spec.md", "# Spec\n\nBody.\n")
    # 5 files under build/ so the footer can report "5 files excluded".
    for i in range(5):
        _write(root / "build" / f"gen-{i}.md", f"# Gen {i}\n\nBody.\n")

    proc = _run(docs_script, "migrate", str(root), "--exclude", "build/")
    assert proc.returncode == 0, proc.stderr
    # The exact footer wording is pinned by the milestone doc's F3 example:
    # "5 files excluded under build/".
    assert "5 files excluded under build/" in proc.stdout, proc.stdout
