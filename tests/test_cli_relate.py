"""M25 — CLI end-to-end tests for `docs relate add|remove` (Phase 2, RED).

Intended RED reason for EVERY test in this file at the Phase-4 baseline:
`relate` is not yet an argparse subcommand, so the CLI exits 2 with
`invalid choice: 'relate'`. Because argparse *already* exits 2, a
returncode-only assertion would be falsely GREEN for the exit-2 refusal
tests — so every intended-exit-2 test also asserts its exact contract
stderr string, and every write test also asserts on-disk bytes.

Phase 7 wires the verb and flips these GREEN.
"""

from __future__ import annotations

import json
import random
import stat
import string
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from docs_cli import cli


def _run(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=None if cwd is None else str(cwd),
    )


def _doc(title: str, project: str, edge: str | None, *, updated: str = "2026-05-20") -> str:
    text = f"# {title}\n\nLifecycle: active\nRole: notes\nProject: {project}\nUpdated: {updated}\n"
    if edge is not None:
        text += f"\nRelated:\n- {edge}\n"
    return text + "\n## Body\n\nProse.\n"


def _pair_tree(
    tmp_path: Path,
    name: str,
    *,
    source_edge: str | None = None,
    target_edge: str | None = None,
) -> Path:
    """A two-doc managed root (`a.md`, `b.md`) with the given `Related:` edges.

    Inline builder (M25 Phase 3): every test here mutates and byte-compares,
    so a committed static tree would only add a `copytree` step.
    """
    root = tmp_path / name
    root.mkdir(parents=True)
    (root / ".docs.toml").write_text(f'[project]\nname = "{name}"\n')
    (root / "a.md").write_text(_doc("A", name, source_edge))
    (root / "b.md").write_text(_doc("B", name, target_edge))
    return root


def _archived_pair_tree(tmp_path: Path, name: str, *, inverse_present: bool) -> Path:
    """An active `a.md` and an archived `archive/2026-01-01/old.md`."""
    root = tmp_path / name
    (root / "archive" / "2026-01-01").mkdir(parents=True)
    (root / ".docs.toml").write_text(f'[project]\nname = "{name}"\n')
    (root / "a.md").write_text(_doc("A", name, "depends-on: archive/2026-01-01/old.md"))
    edges = ["- references: a.md"]
    if inverse_present:
        edges.append("- required-by: a.md")
    (root / "archive" / "2026-01-01" / "old.md").write_text(
        f"# Old\n\nLifecycle: archived\nRole: plan\nProject: {name}\n"
        "Updated: 2026-01-01\nArchived-reason: completed\n\n"
        "Related:\n" + "\n".join(edges) + "\n\n## Body\n\nHistorical prose.\n"
    )
    return root


def _snapshot(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*.md"))}


# --- help / grammar --------------------------------------------------------


def test_relate_help_lists_add_and_remove(docs_script):
    proc = _run(docs_script, "relate", "--help")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "add" in proc.stdout
    assert "remove" in proc.stdout


def test_relate_add_help_shows_grammar_and_flags(docs_script):
    proc = _run(docs_script, "relate", "add", "--help")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    for token in ("SOURCE", "VERB", "TARGET", "--reason", "--date", "--json", "--dry-run"):
        assert token in proc.stdout, f"`relate add --help` must document {token}"


# --- happy paths -----------------------------------------------------------


def test_relate_add_writes_both_endpoints_and_bumps_updated(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "happy")
    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "docs: relate: added 'precedes: b.md' to a.md" in proc.stderr
    assert "docs: relate: added 'follows: a.md' to b.md" in proc.stderr

    a_text = (root / "a.md").read_text()
    b_text = (root / "b.md").read_text()
    assert "- precedes: b.md" in a_text
    assert "- follows: a.md" in b_text
    today = date.today().isoformat()
    assert f"Updated: {today}" in a_text, "a changed endpoint is bumped to today, not blanked"
    assert f"Updated: {today}" in b_text
    assert "Updated: 2026-05-20" not in a_text
    assert "Updated: 2026-05-20" not in b_text
    assert (root / "INDEX.md").is_file(), "one end-of-run reindex"


def test_relate_add_completes_only_the_missing_half(docs_script, tmp_path):
    """The already-correct endpoint is left byte-identical, Updated: included."""
    root = _pair_tree(tmp_path, "half", source_edge="precedes: b.md")
    a_before = (root / "a.md").read_bytes()

    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "docs: relate: no change — 'precedes: b.md' already present in a.md" in proc.stderr
    assert "docs: relate: added 'follows: a.md' to b.md" in proc.stderr
    assert (root / "a.md").read_bytes() == a_before
    assert "- follows: a.md" in (root / "b.md").read_text()


def test_relate_add_then_check_is_clean(docs_script, tmp_path):
    """The primary use case: repair the finding, then the tree validates."""
    root = _pair_tree(tmp_path, "repair", source_edge="precedes: b.md")
    add = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))
    assert add.returncode == 0, (add.stdout, add.stderr)
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


def test_relate_remove_then_check_is_clean(docs_script, tmp_path):
    """The other valid repair: the edge was wrong, so delete the pair."""
    root = _pair_tree(tmp_path, "drop", source_edge="precedes: b.md")
    rm = _run(docs_script, "relate", "remove", "a.md", "precedes", "b.md", "--root", str(root))
    assert rm.returncode == 0, (rm.stdout, rm.stderr)
    assert "docs: relate: removed 'precedes: b.md' from a.md" in rm.stderr
    assert "- precedes: b.md" not in (root / "a.md").read_text()
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


def test_relate_symmetric_invocations_produce_identical_trees(docs_script, tmp_path):
    """D1 symmetry: naming the pair from either side writes the same bytes."""
    # Same tree NAME under different parents, so project slug, root title,
    # and every root-relative path are identical and the bytes are comparable.
    forward = _pair_tree(tmp_path / "f", "sym")
    reverse = _pair_tree(tmp_path / "r", "sym")

    f = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(forward))
    r = _run(docs_script, "relate", "add", "b.md", "follows", "a.md", "--root", str(reverse))
    assert f.returncode == 0, (f.stdout, f.stderr)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert _snapshot(forward) == _snapshot(reverse)


# --- idempotency -----------------------------------------------------------


def test_relate_add_twice_is_a_no_op(docs_script, tmp_path):
    """A fully-satisfied `add` writes ZERO bytes — Updated: included."""
    root = _pair_tree(tmp_path, "idem-add")
    first = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))
    assert first.returncode == 0, (first.stdout, first.stderr)
    after_first = _snapshot(root)

    second = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))
    assert second.returncode == 0, (second.stdout, second.stderr)
    assert "no change — 'precedes: b.md' already present in a.md" in second.stderr
    assert "no change — 'follows: a.md' already present in b.md" in second.stderr
    assert _snapshot(root) == after_first


def test_relate_remove_twice_is_a_no_op(docs_script, tmp_path):
    root = _pair_tree(
        tmp_path, "idem-rm", source_edge="precedes: b.md", target_edge="follows: a.md"
    )
    first = _run(docs_script, "relate", "remove", "a.md", "precedes", "b.md", "--root", str(root))
    assert first.returncode == 0, (first.stdout, first.stderr)
    after_first = _snapshot(root)

    second = _run(docs_script, "relate", "remove", "a.md", "precedes", "b.md", "--root", str(root))
    assert second.returncode == 0, (second.stdout, second.stderr)
    assert "no change — 'precedes: b.md' already absent from a.md" in second.stderr
    assert _snapshot(root) == after_first


# --- preview / machine output ----------------------------------------------


def test_relate_dry_run_writes_nothing(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "preview")
    before = _snapshot(root)
    index_before = (root / "INDEX.md").read_bytes() if (root / "INDEX.md").is_file() else None

    proc = _run(
        docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root), "--dry-run"
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "docs: relate: would add 'precedes: b.md' to a.md" in proc.stderr
    assert "docs: relate: would add 'follows: a.md' to b.md" in proc.stderr
    assert _snapshot(root) == before
    index_after = (root / "INDEX.md").read_bytes() if (root / "INDEX.md").is_file() else None
    assert index_after == index_before, "--dry-run does not reindex either"


def test_relate_json_record_shape(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "jsonshape", source_edge="precedes: b.md")
    proc = _run(
        docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root), "--json"
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert set(record) == {
        "action",
        "verb",
        "inverse",
        "source",
        "target",
        "reason",
        "date",
        "dry_run",
        "applied",
        "index_refreshed",
        "edits",
    }
    assert record["action"] == "add"
    assert record["verb"] == "precedes"
    assert record["inverse"] == "follows"
    assert record["source"] == "a.md"
    assert record["target"] == "b.md"
    assert record["applied"] is True
    assert record["index_refreshed"] is True
    assert [e["path"] for e in record["edits"]] == ["a.md", "b.md"]
    assert record["edits"][0]["change"] == "unchanged"
    assert record["edits"][1]["change"] == "added"


def test_relate_dry_run_json_reports_not_applied(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "jsonpreview")
    before = _snapshot(root)
    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "precedes",
        "b.md",
        "--root",
        str(root),
        "--json",
        "--dry-run",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert record["dry_run"] is True
    assert record["applied"] is False
    assert record["index_refreshed"] is False
    assert _snapshot(root) == before


def test_relate_no_op_json_reports_not_applied(docs_script, tmp_path):
    """An idempotent no-op is `applied: false` too — not just a dry-run."""
    root = _pair_tree(
        tmp_path, "jsonnoop", source_edge="precedes: b.md", target_edge="follows: a.md"
    )
    before = _snapshot(root)
    proc = _run(
        docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root), "--json"
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert record["dry_run"] is False
    assert record["applied"] is False, "nothing was written, so nothing was applied"
    assert record["index_refreshed"] is False
    assert [e["change"] for e in record["edits"]] == ["unchanged", "unchanged"]
    assert _snapshot(root) == before


def test_relate_quiet_suppresses_success_but_never_a_refusal(docs_script, tmp_path):
    """`--quiet` gates the success lines only; refusals always print."""
    root = _pair_tree(tmp_path, "quiet")
    ok = _run(
        docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root), "--quiet"
    )
    assert ok.returncode == 0, (ok.stdout, ok.stderr)
    assert "docs: relate: added" not in ok.stderr
    assert "- precedes: b.md" in (root / "a.md").read_text(), "the write still happened"

    refused = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "Pairs-With",
        "b.md",
        "--root",
        str(root),
        "--quiet",
    )
    assert refused.returncode == 2
    assert "docs: relate: unknown verb 'Pairs-With'" in refused.stderr, (
        "--quiet must never silence a refusal"
    )


def test_relate_json_stdout_parses_alone(docs_script, tmp_path):
    """`--json` keeps stdout byte-clean: human lines stay on stderr."""
    root = _pair_tree(tmp_path, "jsonclean")
    proc = _run(
        docs_script, "relate", "add", "a.md", "blocks", "b.md", "--root", str(root), "--json"
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    json.loads(proc.stdout)  # raises if anything else is on stdout
    assert "docs: relate:" not in proc.stdout


# --- refusals (each asserts the contract stderr AND byte-identity) ---------


def test_relate_verb_outside_the_free_form_grammar_refuses(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "unknownverb")
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", "see also", "b.md", "--root", str(root))
    assert proc.returncode == 2
    assert (
        "docs: relate: unknown verb 'see also'; expected a reciprocal verb "
        "(blocked-by, blocks, depends-on, follows, precedes, required-by) "
        "or a free-form verb matching [a-z][a-z0-9-]*"
    ) in proc.stderr, proc.stderr
    assert _snapshot(root) == before


def test_relate_case_variant_verb_refuses(docs_script, tmp_path):
    """Matching is case-sensitive exact: `Precedes` is outside the grammar."""
    root = _pair_tree(tmp_path, "caseverb")
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", "Precedes", "b.md", "--root", str(root))
    assert proc.returncode == 2
    assert "docs: relate: unknown verb 'Precedes'" in proc.stderr
    assert _snapshot(root) == before


def test_relate_missing_endpoint_exits_1(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "missing")
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "nope.md", "--root", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "docs: relate: file not found: " in proc.stderr
    assert "nope.md" in proc.stderr
    assert _snapshot(root) == before


def test_relate_endpoint_outside_root_exits_1(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "outside")
    stray = tmp_path / "stray.md"
    stray.write_text(_doc("Stray", "outside", None))
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", "precedes", str(stray), "--root", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "is outside the resolved docs root" in proc.stderr
    assert _snapshot(root) == before


def test_relate_malformed_endpoint_exits_1(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "malformed")
    (root / "b.md").write_text("no h1 at all\n")
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "Traceback" not in proc.stderr
    # The parser's own self-locating message — a CLEAN refusal, not a lucky
    # exit 1: it names the offending file and the structural reason.
    assert str(root / "b.md") in proc.stderr
    assert "missing H1" in proc.stderr
    assert _snapshot(root) == before


def test_relate_without_docs_toml_refuses(docs_script, tmp_path):
    """A write into an unmanaged tree is the footgun the strict root closes."""
    bare = tmp_path / "bare"
    bare.mkdir()
    (bare / "a.md").write_text(_doc("A", "bare", None))
    (bare / "b.md").write_text(_doc("B", "bare", None))
    before = _snapshot(bare)
    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", cwd=bare)
    assert proc.returncode == 2
    assert "is not under a docs root with .docs.toml; refusing" in proc.stderr
    assert "docs: relate:" in proc.stderr, "the refusal speaks in relate's own voice"
    assert _snapshot(bare) == before


def test_relate_self_edge_refuses(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "selfedge")
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "a.md", "--root", str(root))
    assert proc.returncode == 2
    assert "docs: relate: SOURCE and TARGET must be different documents" in proc.stderr
    assert _snapshot(root) == before


def test_relate_bad_date_refuses(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "baddate")
    before = _snapshot(root)
    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "precedes",
        "b.md",
        "--root",
        str(root),
        "--date",
        "11-08-2026",
    )
    assert proc.returncode == 2
    assert "docs: relate: --date:" in proc.stderr
    assert _snapshot(root) == before


def test_relate_multiline_reason_refuses(docs_script, tmp_path):
    """A multi-line reason would terminate the metadata block — structural."""
    root = _archived_pair_tree(tmp_path, "multiline", inverse_present=False)
    before = _snapshot(root)
    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "depends-on",
        "archive/2026-01-01/old.md",
        "--root",
        str(root),
        "--reason",
        "first line\nsecond line",
    )
    assert proc.returncode == 2
    assert "docs: relate: --reason must be a single line" in proc.stderr
    assert _snapshot(root) == before


def test_relate_empty_reason_refuses(docs_script, tmp_path):
    """An empty audit reason is indistinguishable from no reason at all."""
    root = _archived_pair_tree(tmp_path, "emptyreason", inverse_present=False)
    before = _snapshot(root)
    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "depends-on",
        "archive/2026-01-01/old.md",
        "--root",
        str(root),
        "--reason",
        "   ",
    )
    assert proc.returncode == 2
    assert "docs: relate: --reason must not be empty" in proc.stderr
    assert _snapshot(root) == before


# --- endpoint path resolution (OQ-A) ---------------------------------------


def test_relate_resolves_root_relative_endpoint_from_outside_cwd(docs_script, tmp_path):
    """Root-relative FIRST: the path copied out of a `check` finding just works."""
    root = _pair_tree(tmp_path, "rootrel")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "precedes",
        "b.md",
        "--root",
        str(root),
        cwd=elsewhere,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "- precedes: b.md" in (root / "a.md").read_text()
    assert "- follows: a.md" in (root / "b.md").read_text()


def test_relate_falls_back_to_cwd_relative_endpoint(docs_script, tmp_path):
    """Fallback: a path that is NOT a root-relative hit resolves from the cwd.

    `sub/` holds the docs; the invocation runs from inside `sub/` and names
    the endpoints by bare filename, which is not a file at `<root>/`.
    """
    root = tmp_path / "cwdrel"
    (root / "sub").mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "cwdrel"\n')
    (root / "sub" / "a.md").write_text(_doc("A", "cwdrel", None))
    (root / "sub" / "b.md").write_text(_doc("B", "cwdrel", None))

    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", cwd=root / "sub")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "- precedes: sub/b.md" in (root / "sub" / "a.md").read_text(), (
        "the WRITTEN edge is root-relative, whatever spelling was typed"
    )
    assert "- follows: sub/a.md" in (root / "sub" / "b.md").read_text()
    assert "docs: relate: added 'precedes: sub/b.md' to sub/a.md" in proc.stderr, (
        "all output names the root-relative POSIX form"
    )


def test_relate_endpoint_resolution_prefers_root_relative_over_cwd(docs_script, tmp_path):
    """OQ-A PRECEDENCE, pinned where the two interpretations actually differ.

    Both `<root>/x.md` and `<cwd>/x.md` exist and are DIFFERENT files. The
    binding decision is root-relative FIRST, so the edge must land in
    `<root>/x.md` and `<root>/sub/x.md` must be byte-identical. Without
    this, a cwd-relative-first implementation passes every other
    resolution test in this file.
    """
    root = tmp_path / "precedence"
    (root / "sub").mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "precedence"\n')
    (root / "x.md").write_text(_doc("Root X", "precedence", None))
    (root / "y.md").write_text(_doc("Root Y", "precedence", None))
    (root / "sub" / "x.md").write_text(_doc("Sub X", "precedence", None))
    decoy_before = (root / "sub" / "x.md").read_bytes()

    proc = _run(
        docs_script,
        "relate",
        "add",
        "x.md",
        "precedes",
        "y.md",
        "--root",
        str(root),
        cwd=root / "sub",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "- precedes: y.md" in (root / "x.md").read_text(), "root-relative wins"
    assert (root / "sub" / "x.md").read_bytes() == decoy_before, (
        "the cwd-relative candidate must not be touched"
    )
    assert "- follows: x.md" in (root / "y.md").read_text(), (
        "the inverse names the ROOT-relative source, not sub/x.md"
    )
    assert "docs: relate: added 'precedes: y.md' to x.md" in proc.stderr


def test_relate_absolute_endpoint_inside_root_reports_root_relative(docs_script, tmp_path):
    """An absolute path is used as-is, but every message names the root-relative form."""
    root = _pair_tree(tmp_path, "absolute")
    proc = _run(
        docs_script,
        "relate",
        "add",
        str(root / "a.md"),
        "precedes",
        str(root / "b.md"),
        "--root",
        str(root),
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "docs: relate: added 'precedes: b.md' to a.md" in proc.stderr
    assert str(tmp_path) not in proc.stderr, "no absolute path may leak into the output"
    assert "- precedes: b.md" in (root / "a.md").read_text()
    assert "- follows: a.md" in (root / "b.md").read_text()


def test_relate_root_without_docs_toml_refuses(docs_script, tmp_path):
    """`--root` bypasses the up-walk ONLY when the directory is managed."""
    bare = tmp_path / "unmanaged"
    bare.mkdir()
    (bare / "a.md").write_text(_doc("A", "unmanaged", None))
    (bare / "b.md").write_text(_doc("B", "unmanaged", None))
    before = _snapshot(bare)
    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(bare))
    assert proc.returncode == 2
    assert f"docs: relate: --root {bare} does not contain .docs.toml; refusing" in proc.stderr
    assert _snapshot(bare) == before


def test_relate_json_echoes_a_non_null_reason(docs_script, tmp_path):
    """`reason` is echoed verbatim even when the pair is all-active (unused)."""
    root = _pair_tree(tmp_path, "reasonecho")
    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "precedes",
        "b.md",
        "--root",
        str(root),
        "--json",
        "--reason",
        "operator note",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert record["reason"] == "operator note"
    assert all(e["revision_appended"] is False for e in record["edits"]), (
        "--reason on an all-active pair is accepted but unused"
    )


def test_relate_reindex_honours_exclusion(docs_script, tmp_path):
    """M14 — A6: a malformed EXCLUDED file cannot fail the post-repair reindex."""
    root = tmp_path / "excluded-reindex"
    (root / "vendor").mkdir(parents=True)
    (root / ".docs.toml").write_text(
        '[project]\nname = "excluded-reindex"\n\n[exclude]\ndirs = ["vendor"]\n'
    )
    (root / "a.md").write_text(_doc("A", "excluded-reindex", None))
    (root / "b.md").write_text(_doc("B", "excluded-reindex", None))
    (root / "vendor" / "junk.md").write_text("no h1 in this excluded file\n")

    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "INDEX refresh failed" not in proc.stderr
    assert (root / "INDEX.md").is_file()
    assert "junk.md" not in (root / "INDEX.md").read_text()


# --- archived endpoints (D4) -----------------------------------------------


def test_relate_archived_endpoint_without_reason_refuses(docs_script, tmp_path):
    root = _archived_pair_tree(tmp_path, "noreason", inverse_present=False)
    before = _snapshot(root)
    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "depends-on",
        "archive/2026-01-01/old.md",
        "--root",
        str(root),
    )
    assert proc.returncode == 2
    assert (
        "docs: relate: archive/2026-01-01/old.md is under the archive subtree; --reason is required"
    ) in proc.stderr
    assert _snapshot(root) == before


def test_relate_archived_no_op_still_requires_reason(docs_script, tmp_path):
    """OQ-C: the rule is checked BEFORE planning, so a no-op still needs it."""
    root = _archived_pair_tree(tmp_path, "noopreason", inverse_present=True)
    before = _snapshot(root)
    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "depends-on",
        "archive/2026-01-01/old.md",
        "--root",
        str(root),
    )
    assert proc.returncode == 2
    assert "--reason is required" in proc.stderr
    assert _snapshot(root) == before, "and it still writes nothing"


def test_relate_archived_no_op_with_reason_writes_nothing(docs_script, tmp_path):
    """D3 + D4: an already-satisfied archived repair writes ZERO bytes.

    `--reason` is supplied and the archive rule is satisfied, so the run
    proceeds — and must then find nothing to do. Nothing may append a
    `Revision:` bullet or bump `Updated:` for a mutation that did not
    happen: D4 says one bullet per REAL mutation, D3 says a fully-satisfied
    invocation writes zero bytes. Without this lock, Step 2 can annotate an
    archived doc on every re-run.
    """
    root = _archived_pair_tree(tmp_path, "archivednoop", inverse_present=True)
    archived = root / "archive" / "2026-01-01" / "old.md"
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "depends-on",
        "archive/2026-01-01/old.md",
        "--root",
        str(root),
        "--reason",
        "re-running the same repair",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "no change — " in proc.stderr
    assert _snapshot(root) == before, "an idempotent archived run is byte-neutral"
    assert "Revision:" not in archived.read_text(), "no bullet for a mutation that did not happen"
    assert not (root / "INDEX.md").exists(), "no change ⇒ no reindex"


def test_relate_archived_repair_writes_only_the_allowed_bytes(docs_script, tmp_path):
    root = _archived_pair_tree(tmp_path, "audited", inverse_present=False)
    archived = root / "archive" / "2026-01-01" / "old.md"
    before = archived.read_text().splitlines()

    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "depends-on",
        "archive/2026-01-01/old.md",
        "--root",
        str(root),
        "--reason",
        "complete the pair",
        "--date",
        "2026-08-11",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "docs: relate: recorded revision in archive/2026-01-01/old.md" in proc.stderr

    after = archived.read_text().splitlines()
    assert [line for line in before if line not in after] == ["Updated: 2026-01-01"]
    assert [line for line in after if line not in before] == [
        "Updated: 2026-08-11",
        "- required-by: a.md",
        "Revision:",
        "- 2026-08-11: relate add 'required-by: a.md'; reason: complete the pair",
    ]
    for untouched in (
        "Lifecycle: archived",
        "Archived-reason: completed",
        "Role: plan",
        "- references: a.md",
        "# Old",
        "Historical prose.",
    ):
        assert untouched in after


def test_relate_repeat_archived_repair_appends_a_second_revision_bullet(docs_script, tmp_path):
    root = _archived_pair_tree(tmp_path, "twice", inverse_present=False)
    archived = root / "archive" / "2026-01-01" / "old.md"

    first = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "depends-on",
        "archive/2026-01-01/old.md",
        "--root",
        str(root),
        "--reason",
        "complete the pair",
        "--date",
        "2026-08-11",
    )
    assert first.returncode == 0, (first.stdout, first.stderr)
    second = _run(
        docs_script,
        "relate",
        "remove",
        "a.md",
        "depends-on",
        "archive/2026-01-01/old.md",
        "--root",
        str(root),
        "--reason",
        "edge was wrong",
        "--date",
        "2026-08-12",
    )
    assert second.returncode == 0, (second.stdout, second.stderr)

    text = archived.read_text()
    assert text.count("Revision:") == 1, "one group, appended to — never a second label"
    assert "- 2026-08-11: relate add 'required-by: a.md'; reason: complete the pair" in text
    assert "- 2026-08-12: relate remove 'required-by: a.md'; reason: edge was wrong" in text
    bullets = [line for line in text.splitlines() if line.startswith("- 2026-")]
    assert bullets == [
        "- 2026-08-11: relate add 'required-by: a.md'; reason: complete the pair",
        "- 2026-08-12: relate remove 'required-by: a.md'; reason: edge was wrong",
    ], "chronological"


def test_relate_active_endpoint_gets_no_revision(docs_script, tmp_path):
    """Audit asymmetry: an active endpoint is never annotated, even with --reason."""
    root = _pair_tree(tmp_path, "asymmetry")
    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "precedes",
        "b.md",
        "--root",
        str(root),
        "--reason",
        "not needed here",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "Revision:" not in (root / "a.md").read_text()
    assert "Revision:" not in (root / "b.md").read_text()


# --- failure handling ------------------------------------------------------


def test_relate_unwritable_endpoint_refuses_before_any_write(docs_script, tmp_path):
    """D5 stage 4: the writability pre-flight fires before the first publish.

    `atomic_write` publishes via tmpfile + rename, which would SUCCEED on a
    read-only file in a writable directory — so only an explicit pre-flight
    honours the archive's read-only intent.
    """
    root = _pair_tree(tmp_path, "unwritable")
    target = root / "b.md"
    a_before = (root / "a.md").read_bytes()
    b_before = target.read_bytes()
    target.chmod(stat.S_IRUSR)
    try:
        proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))
        assert proc.returncode == 2, (proc.stdout, proc.stderr)
        assert "docs: relate: b.md is not writable; refusing before any write" in proc.stderr
        assert "Traceback" not in proc.stderr
        assert (root / "a.md").read_bytes() == a_before, "the SOURCE is untouched"
        assert target.read_bytes() == b_before
    finally:
        target.chmod(stat.S_IRUSR | stat.S_IWUSR)


def test_relate_does_not_gate_on_whole_tree_health(docs_script, tmp_path):
    """`relate` validates only its TWO endpoints — never the whole tree.

    A whole-tree pre-flight (the `archive` / `mv` shape) would make repair
    impossible in exactly the broken tree this verb exists to repair. A
    malformed SIBLING must therefore not block the repair; it can only fail
    the end-of-run reindex, after the two endpoints are already correct.
    """
    root = _pair_tree(tmp_path, "sibling")
    (root / "c.md").write_text("no h1 in this sibling\n")

    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "docs: INDEX refresh failed:" in proc.stderr
    assert "Traceback" not in proc.stderr
    # The repair itself LANDED — that is the whole point of the exception.
    assert "- precedes: b.md" in (root / "a.md").read_text()
    assert "- follows: a.md" in (root / "b.md").read_text()


def test_relate_second_write_failure_rolls_back_and_says_so(docs_script, tmp_path):
    """D5 stage 5, end-to-end: a failed second publish rolls the first back.

    The injection is the read-only *directory* trick: `sub/` is `chmod 555`
    while `sub/b.md` keeps mode 644, so `os.access(b.md, W_OK)` is True and
    the stage-4 writability pre-flight PASSES — then `atomic_write` fails
    creating `sub/b.md.docs-tmp` inside the unwritable directory, which is
    exactly the stage-5 path. Assumes a non-root uid, the same assumption
    `test_cli_archive.py::test_archive_oserror_mid_rewrite_exits_2` makes.
    """
    root = tmp_path / "rollback"
    (root / "sub").mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "rollback"\n')
    (root / "a.md").write_text(_doc("A", "rollback", None))
    (root / "sub" / "b.md").write_text(_doc("B", "rollback", None))
    before = _snapshot(root)

    (root / "sub").chmod(0o555)
    try:
        proc = _run(
            docs_script, "relate", "add", "a.md", "precedes", "sub/b.md", "--root", str(root)
        )
        assert proc.returncode == 2, (proc.stdout, proc.stderr)
        assert "Traceback" not in proc.stderr
        assert "docs: relate: write failed for sub/b.md:" in proc.stderr
        assert "rolled back a.md — the tree is unchanged" in proc.stderr
        assert _snapshot(root) == before, (
            "the already-published source must be restored byte-for-byte"
        )
    finally:
        (root / "sub").chmod(0o755)


def test_relate_first_write_failure_says_nothing_was_published(docs_script, tmp_path):
    """D5 stage 5: when the FIRST publish fails there is nothing to roll back.

    Reachable without any injection: `a.md` already carries its half, so the
    ONLY changed endpoint is `sub/b.md`, and its write is therefore the
    first. The generic `rolled back <list>` wording would degenerate to
    `rolled back  — …` with an empty list here, which is why this branch has
    its own message. Same `chmod 555` directory trick, same non-root
    assumption, as the rollback test above.
    """
    root = tmp_path / "firstfail"
    (root / "sub").mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "firstfail"\n')
    (root / "a.md").write_text(_doc("A", "firstfail", "precedes: sub/b.md"))
    (root / "sub" / "b.md").write_text(_doc("B", "firstfail", None))
    before = _snapshot(root)

    (root / "sub").chmod(0o555)
    try:
        proc = _run(
            docs_script, "relate", "add", "a.md", "precedes", "sub/b.md", "--root", str(root)
        )
        assert proc.returncode == 2, (proc.stdout, proc.stderr)
        assert "Traceback" not in proc.stderr
        assert "docs: relate: write failed for sub/b.md:" in proc.stderr
        assert "nothing was published — the tree is unchanged" in proc.stderr
        assert "rolled back  —" not in proc.stderr, "the empty-list wording must never appear"
        assert _snapshot(root) == before
    finally:
        (root / "sub").chmod(0o755)


def test_relate_add_is_a_no_op_against_a_non_canonical_bullet(docs_script, tmp_path):
    """R1 at the CLI seam: `- precedes: ./b.md` is the SAME edge as `b.md`.

    `test_check.py` pins canonical matching for the check rule; this pins it
    for the repair verb. Without it `relate add` would append a duplicate
    bullet on exactly the loosely-spelled trees canonical matching exists to
    tolerate — i.e. `relate` would stop being idempotent there.
    """
    root = _pair_tree(
        tmp_path, "canon", source_edge="precedes: ./b.md", target_edge="follows: a.md"
    )
    before = _snapshot(root)

    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "no change — 'precedes: b.md' already present in a.md" in proc.stderr
    assert _snapshot(root) == before, "a non-canonically spelled edge is still present"
    assert (root / "a.md").read_text().count("precedes:") == 1, "no duplicate bullet"
    assert not (root / "INDEX.md").exists(), "no change ⇒ no reindex"


def test_relate_allows_an_excluded_endpoint(docs_script, tmp_path):
    """R9: an explicitly named endpoint beats a coarse exclusion.

    `relate` runs no whole-tree pre-flight and consults no exclusion
    predicate when resolving its two endpoints — refusing would make the
    pair unrepairable. The end-of-run reindex still honours the exclusion.
    """
    root = tmp_path / "excluded-endpoint"
    (root / "vendor").mkdir(parents=True)
    (root / ".docs.toml").write_text(
        '[project]\nname = "excluded-endpoint"\n\n[exclude]\ndirs = ["vendor"]\n'
    )
    (root / "a.md").write_text(_doc("A", "excluded-endpoint", None))
    (root / "vendor" / "b.md").write_text(_doc("B", "excluded-endpoint", None))

    proc = _run(
        docs_script, "relate", "add", "a.md", "precedes", "vendor/b.md", "--root", str(root)
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "- precedes: vendor/b.md" in (root / "a.md").read_text()
    assert "- follows: a.md" in (root / "vendor" / "b.md").read_text()
    assert "vendor/b.md" not in (root / "INDEX.md").read_text(), (
        "the reindex still honours [exclude]"
    )


def test_relate_dry_run_previews_the_revision_bullet(docs_script, tmp_path):
    """An archived repair's audit bullet must be visible in the preview."""
    root = _archived_pair_tree(tmp_path, "previewrev", inverse_present=False)
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "depends-on",
        "archive/2026-01-01/old.md",
        "--root",
        str(root),
        "--reason",
        "preview the audit record",
        "--dry-run",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "docs: relate: would record revision in archive/2026-01-01/old.md" in proc.stderr, (
        "a dry-run must announce the Revision: bullet it would write"
    )
    assert "docs: relate: recorded revision in" not in proc.stderr
    assert _snapshot(root) == before


# --- reindex ---------------------------------------------------------------


def test_relate_refreshes_the_index_exactly_once(docs_script, tmp_path):
    """A following `docs index` must be a byte no-op — the refresh already ran."""
    root = _pair_tree(tmp_path, "reindex")
    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    after_relate = (root / "INDEX.md").read_bytes()

    idx = _run(docs_script, "index", "--root", str(root))
    assert idx.returncode == 0, (idx.stdout, idx.stderr)
    assert (root / "INDEX.md").read_bytes() == after_relate


def test_relate_no_op_does_not_reindex(docs_script, tmp_path):
    """Idempotency extends to the INDEX: a zero-byte run refreshes nothing."""
    root = _pair_tree(
        tmp_path, "noopindex", source_edge="precedes: b.md", target_edge="follows: a.md"
    )
    assert not (root / "INDEX.md").exists()
    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert not (root / "INDEX.md").exists(), "no change ⇒ no reindex"


# ===========================================================================
# M28a — D9 / Q6: the witness survives M25 — D4's audited archived-endpoint
# repair byte-identically.
# ===========================================================================


def test_relate_archived_repair_leaves_the_witness_byte_identical(docs_script, tmp_path):
    """`convention.md`'s *Audited relationship repair* enumerates exactly three
    things that may change in an archived document — the one recognized
    `Related:` bullet, the `Updated:` value, and the `Revision:` group. M28a
    puts `Archived:` on the byte-identical side beside `Archived-reason:`, and
    this is the lock that makes that promise real.

    The witness records ENTRY into the archive, never a later repair, so a
    `relate` repair that moved it would be recording someone else's event.

    GREEN at baseline (the witness it preserves is hand-authored, since no verb
    writes one until Phase 6) and genuine afterwards. The trailing `docs check`
    becomes an over-fire guard at Phase 6.
    """
    root = tmp_path / "witnessed"
    (root / "archive" / "2026-01-01").mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "witnessed"\n')
    (root / "a.md").write_text(_doc("A", "witnessed", "depends-on: archive/2026-01-01/old.md"))
    archived = root / "archive" / "2026-01-01" / "old.md"
    archived.write_text(
        "# Old\n\nLifecycle: archived\nRole: plan\nProject: witnessed\n"
        "Updated: 2026-01-01\nArchived: 2026-01-01\nArchived-reason: completed\n\n"
        "Related:\n- references: a.md\n\n## Body\n\nHistorical prose.\n"
    )
    before = archived.read_text().splitlines()

    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "depends-on",
        "archive/2026-01-01/old.md",
        "--root",
        str(root),
        "--reason",
        "complete the pair",
        "--date",
        "2026-08-11",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)

    after = archived.read_text().splitlines()
    assert [line for line in before if line not in after] == ["Updated: 2026-01-01"], (
        "the ONLY line that may disappear is the old Updated: value"
    )
    assert [line for line in after if line not in before] == [
        "Updated: 2026-08-11",
        "- required-by: a.md",
        "Revision:",
        "- 2026-08-11: relate add 'required-by: a.md'; reason: complete the pair",
    ]
    assert "Archived: 2026-01-01" in after, "the witness is byte-identical"
    assert "Archived-reason: completed" in after
    assert _run(docs_script, "check", str(root)).returncode == 0, (
        "and the repaired document still corroborates its dated directory"
    )


# ===========================================================================
# Free-form edges, one-sided (milestone `lifecycle-and-free-form-relate` —
# D4–D6; the task plan's *Decisions (Phase 1 — BINDING)* › P1.2, whose
# message ids R1–R3 the docstrings cite). RED until free-form `relate` lands:
# today every verb outside the six recognized ones refuses at exit 2 with the
# old `expected one of:` message, so every test below asserts the frozen R1
# text, the written bytes, or a zero-byte refusal — never a bare exit code.
# ===========================================================================

_R1_TAIL = (
    "; expected a reciprocal verb (blocked-by, blocks, depends-on, follows, precedes, "
    "required-by) or a free-form verb matching [a-z][a-z0-9-]*"
)


def _r1(verb: str) -> str:
    """The frozen grammar refusal for `verb` — rendered with `repr`, so a verb
    carrying a newline stays on one line."""
    return f"docs: relate: unknown verb {verb!r}{_R1_TAIL}"


def _every_file(root: Path) -> dict[str, bytes]:
    """Every file under `root`, not only Markdown — binary targets included."""
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _listed_edges(docs_script: Path, root: Path, rel: str) -> list[tuple[str, str]]:
    """`rel`'s `Related:` edges as `docs list --json` reads them back."""
    proc = _run(docs_script, "list", "--root", str(root), "--json")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    for record in json.loads(proc.stdout):
        if record["path"] == rel:
            return [(edge["verb"], edge["target"]) for edge in record["related"]]
    raise AssertionError(f"{rel} is missing from `docs list --json`")


def test_relate_free_form_add_writes_only_the_source_bullet(docs_script, tmp_path):
    """D4: SOURCE gains the bullet (its `Related:` group created) and today's
    `Updated:`; TARGET is byte-identical; the INDEX is refreshed."""
    root = _pair_tree(tmp_path, "ffadd")
    b_before = (root / "b.md").read_bytes()

    proc = _run(docs_script, "relate", "add", "a.md", "pairs-with", "b.md", "--root", str(root))

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    relate_lines = [ln for ln in proc.stderr.splitlines() if ln.startswith("docs: relate:")]
    assert relate_lines == ["docs: relate: added 'pairs-with: b.md' to a.md"], (
        "one line, about SOURCE — TARGET is never an edit"
    )
    today = date.today().isoformat()
    assert (root / "a.md").read_text() == _doc("A", "ffadd", "pairs-with: b.md", updated=today)
    assert (root / "b.md").read_bytes() == b_before
    assert (root / "INDEX.md").is_file()


def test_relate_free_form_remove_drops_only_the_source_bullet(docs_script, tmp_path):
    """D4: `remove` drops SOURCE's bullet (and the emptied group); TARGET keeps
    its own back-edge — a free-form edge has no inverse to unwrite."""
    root = _pair_tree(
        tmp_path, "ffrm", source_edge="pairs-with: b.md", target_edge="pairs-with: a.md"
    )
    b_before = (root / "b.md").read_bytes()

    proc = _run(docs_script, "relate", "remove", "a.md", "pairs-with", "b.md", "--root", str(root))

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "docs: relate: removed 'pairs-with: b.md' from a.md" in proc.stderr
    today = date.today().isoformat()
    assert (root / "a.md").read_text() == _doc("A", "ffrm", None, updated=today)
    assert (root / "b.md").read_bytes() == b_before


def test_relate_free_form_is_idempotent(docs_script, tmp_path):
    """A satisfied `add` or `remove` writes zero bytes, INDEX included."""
    root = _pair_tree(tmp_path, "ffidem")
    first = _run(docs_script, "relate", "add", "a.md", "pairs-with", "b.md", "--root", str(root))
    assert first.returncode == 0, (first.stdout, first.stderr)
    after_add = _snapshot(root)

    again = _run(docs_script, "relate", "add", "a.md", "pairs-with", "b.md", "--root", str(root))
    assert again.returncode == 0, (again.stdout, again.stderr)
    assert "docs: relate: no change — 'pairs-with: b.md' already present in a.md" in again.stderr
    assert _snapshot(root) == after_add

    removed = _run(
        docs_script, "relate", "remove", "a.md", "pairs-with", "b.md", "--root", str(root)
    )
    assert removed.returncode == 0, (removed.stdout, removed.stderr)
    after_remove = _snapshot(root)
    twice = _run(docs_script, "relate", "remove", "a.md", "pairs-with", "b.md", "--root", str(root))
    assert twice.returncode == 0, (twice.stdout, twice.stderr)
    assert "docs: relate: no change — 'pairs-with: b.md' already absent from a.md" in twice.stderr
    assert _snapshot(root) == after_remove


@pytest.mark.parametrize(
    "existing_edge",
    [None, "references: b.md"],
    ids=["without-a-related-group", "with-an-existing-related-group"],
)
def test_relate_free_form_add_then_remove_restores_the_original_bytes(
    docs_script, tmp_path, existing_edge
):
    """The round-trip property, from an initially ABSENT edge: add then remove,
    both under `--date` equal to the original `Updated:`, restores every byte —
    whether the group had to be created (and dropped) or already existed."""
    root = _pair_tree(tmp_path, "ffround", source_edge=existing_edge)
    original = (root / "a.md").read_bytes()

    for action in ("add", "remove"):
        proc = _run(
            docs_script,
            "relate",
            action,
            "a.md",
            "child-of",
            "b.md",
            "--root",
            str(root),
            "--date",
            "2026-05-20",
        )
        assert proc.returncode == 0, (action, proc.stdout, proc.stderr)

    assert (root / "a.md").read_bytes() == original


def test_relate_free_form_matches_a_non_canonical_existing_bullet(docs_script, tmp_path):
    """Canonical-target matching, as for recognized verbs: `./b.md` is `b.md`."""
    root = _pair_tree(tmp_path, "ffcanon", source_edge="pairs-with: ./b.md")
    before = _snapshot(root)

    add = _run(docs_script, "relate", "add", "a.md", "pairs-with", "b.md", "--root", str(root))
    assert add.returncode == 0, (add.stdout, add.stderr)
    assert _snapshot(root) == before, "an existing `./b.md` bullet already satisfies the edge"

    rm = _run(docs_script, "relate", "remove", "a.md", "pairs-with", "b.md", "--root", str(root))
    assert rm.returncode == 0, (rm.stdout, rm.stderr)
    assert "pairs-with" not in (root / "a.md").read_text(), "…and `remove` drops it"


def test_relate_free_form_write_rewrites_exactly_one_managed_document(docs_script, tmp_path):
    """The write footprint: SOURCE plus the one INDEX refresh — nothing else."""
    root = _pair_tree(tmp_path, "fffoot")
    (root / "c.md").write_text(_doc("C", "fffoot", "pairs-with: a.md"))
    assert _run(docs_script, "index", "--root", str(root)).returncode == 0
    before = _every_file(root)

    proc = _run(docs_script, "relate", "add", "a.md", "references", "c.md", "--root", str(root))

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    after = _every_file(root)
    assert set(after) == set(before), "no file appears or disappears"
    changed = sorted(rel for rel in before if before[rel] != after[rel])
    assert changed == ["INDEX.md", "a.md"]


def test_relate_free_form_json_record_has_null_inverse_and_one_edit(docs_script, tmp_path):
    """C15: the recognized record's eleven keys, `inverse: null`, one edit."""
    root = _pair_tree(tmp_path, "ffjson")

    proc = _run(
        docs_script, "relate", "add", "a.md", "pairs-with", "b.md", "--root", str(root), "--json"
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert set(record) == {
        "action",
        "verb",
        "inverse",
        "source",
        "target",
        "reason",
        "date",
        "dry_run",
        "applied",
        "index_refreshed",
        "edits",
    }
    assert record["inverse"] is None
    assert (record["action"], record["verb"]) == ("add", "pairs-with")
    assert (record["source"], record["target"]) == ("a.md", "b.md")
    assert record["reason"] is None
    assert (record["applied"], record["index_refreshed"], record["dry_run"]) == (True, True, False)
    assert record["edits"] == [
        {
            "path": "a.md",
            "archived": False,
            "edge": "pairs-with: b.md",
            "present_before": False,
            "present_after": True,
            "change": "added",
            "updated_bumped": True,
            "revision_appended": False,
        }
    ]


def test_relate_free_form_dry_run_writes_nothing(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "ffpreview")
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "pairs-with",
        "b.md",
        "--root",
        str(root),
        "--dry-run",
        "--json",
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "docs: relate: would add 'pairs-with: b.md' to a.md" in proc.stderr
    record = json.loads(proc.stdout)
    assert (record["dry_run"], record["applied"], record["index_refreshed"]) == (True, False, False)
    assert len(record["edits"]) == 1
    assert _snapshot(root) == before
    assert not (root / "INDEX.md").exists(), "a preview does not reindex"


def test_relate_free_form_self_edge_is_refused(docs_script, tmp_path):
    """The self-edge refusal stays for free-form verbs (*Also settled*)."""
    root = _pair_tree(tmp_path, "ffself")
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", "pairs-with", "a.md", "--root", str(root))
    assert proc.returncode == 2
    assert "docs: relate: SOURCE and TARGET must be different documents" in proc.stderr, proc.stderr
    assert _snapshot(root) == before


def test_relate_free_form_still_shape_checks_a_given_reason(docs_script, tmp_path):
    """P1.2 step 8: a free-form edge never NEEDS `--reason`, but a reason that
    is given is still shape-checked — empty or multi-line refuses with the
    unchanged messages, and nothing is written."""
    root = _pair_tree(tmp_path, "ffreason")
    before = _snapshot(root)
    for reason, message in (
        ("   ", "docs: relate: --reason must not be empty"),
        ("first line\nsecond line", "docs: relate: --reason must be a single line"),
    ):
        proc = _run(
            docs_script,
            "relate",
            "add",
            "a.md",
            "pairs-with",
            "b.md",
            "--root",
            str(root),
            "--reason",
            reason,
        )
        assert proc.returncode == 2, (reason, proc.stdout, proc.stderr)
        assert message in proc.stderr, (reason, proc.stderr)
        assert _snapshot(root) == before


def test_relate_free_form_source_must_parse_and_exits_1_when_malformed(docs_script, tmp_path):
    """SOURCE is written, so it must parse even for a free-form verb: a
    malformed SOURCE is the parser's own exit-1 refusal, never a traceback
    from the editor (only TARGET is exempt from parsing)."""
    root = _pair_tree(tmp_path, "ffbadsource")
    (root / "a.md").write_text("no h1 at all\n")
    before = _snapshot(root)

    proc = _run(docs_script, "relate", "add", "a.md", "pairs-with", "b.md", "--root", str(root))

    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "Traceback" not in proc.stderr
    assert str(root / "a.md") in proc.stderr, proc.stderr
    assert "missing H1" in proc.stderr
    assert _snapshot(root) == before


def test_relate_free_form_refuses_an_archived_source_even_when_nothing_would_change(
    docs_script, tmp_path
):
    """R2 — an archived SOURCE refuses in the validate-all-first pass, for
    `add` and `remove`, with or without `--reason`, even when the edge is
    already in the requested state (`old.md` already carries
    `references: a.md`): predictable, not plan-dependent."""
    root = _archived_pair_tree(tmp_path, "ffarchsrc", inverse_present=False)
    before = _snapshot(root)
    refusal = (
        "docs: relate: archive/2026-01-01/old.md is under the archive subtree; "
        "a free-form edge is never written to an archived document"
    )

    for action, extra in (("add", ()), ("remove", ()), ("add", ("--reason", "context"))):
        proc = _run(
            docs_script,
            "relate",
            action,
            "archive/2026-01-01/old.md",
            "references",
            "a.md",
            "--root",
            str(root),
            *extra,
        )
        assert proc.returncode == 2, (action, extra, proc.stdout, proc.stderr)
        assert refusal in proc.stderr, (action, extra, proc.stderr)
        assert _snapshot(root) == before


def test_relate_free_form_archived_target_needs_no_reason_and_is_untouched(docs_script, tmp_path):
    """D5: an archived TARGET is never written, so no `--reason` is needed and
    no `Revision:` is ever written; a given `--reason` is still echoed."""
    root = _archived_pair_tree(tmp_path, "ffarchtgt", inverse_present=False)
    archived = root / "archive" / "2026-01-01" / "old.md"
    archived_before = archived.read_bytes()

    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "references",
        "archive/2026-01-01/old.md",
        "--root",
        str(root),
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    a_text = (root / "a.md").read_text()
    assert "- references: archive/2026-01-01/old.md" in a_text
    assert "Revision:" not in a_text
    assert archived.read_bytes() == archived_before

    reasoned = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "pairs-with",
        "archive/2026-01-01/old.md",
        "--root",
        str(root),
        "--reason",
        "historical context",
        "--json",
    )
    assert reasoned.returncode == 0, (reasoned.stdout, reasoned.stderr)
    record = json.loads(reasoned.stdout)
    assert record["reason"] == "historical context"
    assert [e["revision_appended"] for e in record["edits"]] == [False]
    assert "Revision:" not in (root / "a.md").read_text()
    assert archived.read_bytes() == archived_before


def test_relate_free_form_accepts_a_non_markdown_target(docs_script, tmp_path):
    """D5 / E9: any existing file under the root is a TARGET — a report, or a
    binary that is not even UTF-8, which proves TARGET is never read — and the
    tree stays `docs check` clean."""
    root = _pair_tree(tmp_path, "ffnonmd")
    (root / "coverage.xml").write_text('<coverage line-rate="0.9"/>\n')
    (root / "deck.bin").write_bytes(b"\xff\xfe\x00 not utf-8 \x80\x81")
    blobs = {name: (root / name).read_bytes() for name in ("coverage.xml", "deck.bin")}

    for verb, target in (("references", "coverage.xml"), ("artifact-of", "deck.bin")):
        proc = _run(docs_script, "relate", "add", "a.md", verb, target, "--root", str(root))
        assert proc.returncode == 0, (verb, proc.stdout, proc.stderr)
        assert "Traceback" not in proc.stderr

    a_text = (root / "a.md").read_text()
    assert "- references: coverage.xml" in a_text
    assert "- artifact-of: deck.bin" in a_text
    assert {name: (root / name).read_bytes() for name in blobs} == blobs
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, check.stdout + check.stderr


def test_relate_free_form_target_outside_the_root_exits_1(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "ffoutside")
    stray = tmp_path / "stray.txt"
    stray.write_text("outside the tree\n")
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", "references", str(stray), "--root", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "docs: relate: " in proc.stderr
    assert "is outside the resolved docs root" in proc.stderr
    assert _snapshot(root) == before


def test_relate_free_form_target_that_is_a_directory_exits_1(docs_script, tmp_path):
    """A directory is not a file: today's `file not found:` refusal."""
    root = _pair_tree(tmp_path, "ffdir")
    (root / "sub").mkdir()
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", "references", "sub", "--root", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "docs: relate: file not found: " in proc.stderr
    assert _snapshot(root) == before


def test_relate_free_form_missing_target_exits_1(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "ffmissing")
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", "references", "nope.md", "--root", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "docs: relate: file not found: " in proc.stderr
    assert "nope.md" in proc.stderr
    assert _snapshot(root) == before


def test_relate_free_form_target_symlink_escaping_the_root_exits_1(docs_script, tmp_path):
    """Containment is checked on the RESOLVED path, so a symlink inside the
    tree that points outside it is refused like any outside path."""
    root = _pair_tree(tmp_path, "ffsymlink")
    outside = tmp_path / "secret.txt"
    outside.write_text("outside the tree\n")
    (root / "escape.txt").symlink_to(outside)
    before = _snapshot(root)
    proc = _run(
        docs_script, "relate", "add", "a.md", "references", "escape.txt", "--root", str(root)
    )
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "is outside the resolved docs root" in proc.stderr
    assert _snapshot(root) == before


_GRAMMAR_CASES = [
    ("pairs-with", True, "accepts-pairs-with"),
    ("child-of", True, "accepts-child-of"),
    ("a", True, "accepts-a-single-letter"),
    ("a-", True, "accepts-a-trailing-hyphen"),
    ("a--b", True, "accepts-a-doubled-hyphen"),
    ("x9", True, "accepts-a-digit-after-the-first-letter"),
    ("", False, "refuses-an-empty-verb"),
    ("see also", False, "refuses-an-internal-space"),
    (" pairs-with", False, "refuses-a-leading-space"),
    ("pairs-with ", False, "refuses-a-trailing-space"),
    ("pairs-with\n", False, "refuses-a-trailing-newline"),
    ("pairs-with\r", False, "refuses-a-trailing-carriage-return"),
    ("pairs:with", False, "refuses-a-colon"),
    ("9to5", False, "refuses-a-leading-digit"),
    ("Pairs-With", False, "refuses-uppercase"),
    ("Precedes", False, "refuses-a-capitalised-recognized-verb"),
    ("pairs_with", False, "refuses-an-underscore"),
    ("pairs.with", False, "refuses-a-dot"),
    ("@#!$", False, "refuses-punctuation"),
    ("é", False, "refuses-a-non-ascii-letter"),
    ("a٣", False, "refuses-an-arabic-indic-digit"),
    ("a１", False, "refuses-a-fullwidth-digit"),
]


@pytest.mark.parametrize(
    ("verb", "accepted"),
    [(verb, accepted) for verb, accepted, _ in _GRAMMAR_CASES],
    ids=[case_id for _, _, case_id in _GRAMMAR_CASES],
)
def test_relate_free_form_verb_grammar_boundary(docs_script, tmp_path, verb, accepted):
    """D6, at its boundary: `[a-z][a-z0-9-]*` in full, ASCII only. An accepted
    verb is written as typed and read back by the parser as the identical
    verb; a refused one gets R1 and zero bytes. `pairs-with\\n` is what
    `re.match` with `$` would wrongly accept, and the two non-ASCII digits are
    what `\\d` would."""
    root = _pair_tree(tmp_path, "ffgrammar")
    before = _snapshot(root)

    proc = _run(docs_script, "relate", "add", "a.md", verb, "b.md", "--root", str(root))

    if accepted:
        assert proc.returncode == 0, (proc.stdout, proc.stderr)
        assert _listed_edges(docs_script, root, "a.md") == [(verb, "b.md")]
    else:
        assert proc.returncode == 2, (proc.stdout, proc.stderr)
        assert _r1(verb) in proc.stderr, proc.stderr
        assert _snapshot(root) == before


@pytest.mark.parametrize(
    "verb",
    ["pairs:with", "pairs\nwith", "pairs\rwith"],
    ids=["a-colon", "a-newline", "a-carriage-return"],
)
def test_relate_verb_that_would_corrupt_the_block_is_refused(docs_script, tmp_path, verb):
    """The metadata-injection guard: a `:` would split the bullet differently
    and a line break would end the block — both refused with zero bytes, and
    the tree is still `docs check` clean afterwards."""
    root = _pair_tree(tmp_path, "ffinject")
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", verb, "b.md", "--root", str(root))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert _r1(verb) in proc.stderr, proc.stderr
    assert _snapshot(root) == before
    assert _run(docs_script, "check", str(root)).returncode == 0


def test_relate_leading_hyphen_verb_is_consumed_by_argparse_and_writes_nothing(
    docs_script, tmp_path
):
    """R3 — `-x` is read as an option before the grammar sees it: an argparse
    usage error at exit 2 that never reaches the command, and zero bytes."""
    root = _pair_tree(tmp_path, "ffhyphen")
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", "-x", "b.md", "--root", str(root))
    assert proc.returncode == 2
    assert "usage:" in proc.stderr and "error:" in proc.stderr, proc.stderr
    assert "docs: relate:" not in proc.stderr, "argparse refused it; the command never ran"
    assert _snapshot(root) == before


def test_relate_leading_hyphen_verb_after_a_separator_is_refused_by_the_grammar(
    docs_script, tmp_path
):
    """R3 — after `--` (in either position), or as a bare `-`, the verb reaches
    the command, and the grammar refuses it with R1."""
    root = _pair_tree(tmp_path, "ffseparator")
    before = _snapshot(root)
    for argv, verb in (
        (("a.md", "--", "-x", "b.md"), "-x"),
        (("--", "a.md", "-x", "b.md"), "-x"),
        (("a.md", "-", "b.md"), "-"),
    ):
        proc = _run(docs_script, "relate", "add", "--root", str(root), *argv)
        assert proc.returncode == 2, (argv, proc.stdout, proc.stderr)
        assert _r1(verb) in proc.stderr, (argv, proc.stderr)
        assert _snapshot(root) == before


def _valid_verb(rng: random.Random) -> str:
    """A verb generated FROM the grammar: a lowercase letter, then lowercase
    letters, digits and hyphens — trailing and doubled hyphens included."""
    tail = string.ascii_lowercase + string.digits + "-"
    while True:
        length = rng.choice([0, 0, 1, 2, 5, 12, 40])
        verb = rng.choice(string.ascii_lowercase) + "".join(rng.choice(tail) for _ in range(length))
        if verb not in cli.RECIPROCAL_VERBS:  # a recognized verb is not free-form
            return verb


def _invalid_verb(rng: random.Random) -> str:
    """A verb generated from the grammar's complement, one defect per verb,
    each category independently of the valid generator."""
    base = _valid_verb(rng)
    cut = rng.randrange(len(base) + 1)
    defect = rng.choice(
        [
            lambda: base[:cut] + rng.choice(string.ascii_uppercase) + base[cut:],
            lambda: rng.choice(string.digits) + base,
            lambda: "-" + base,
            lambda: base[:cut] + " " + base[cut:],
            lambda: base[:cut] + ":" + base[cut:],
            lambda: base + "\n",
            lambda: base[:cut] + "\r" + base[cut:],
            lambda: base[:cut] + rng.choice("_.@#!$/,;'\"") + base[cut:],
            lambda: base[:cut] + rng.choice("éßøΩж") + base[cut:],
            lambda: base[:cut] + rng.choice("٣१１") + base[cut:],
            lambda: "",
        ]
    )
    return defect()


def _fuzz_root(base: Path, index: int) -> Path:
    root = base / f"fuzz-{index}"
    root.mkdir(parents=True)
    (root / ".docs.toml").write_text('[project]\nname = "fuzz"\n')
    (root / "a.md").write_text(_doc("A", "fuzz", None))
    (root / "b.md").write_text(_doc("B", "fuzz", None))
    return root


def test_relate_free_form_verb_fuzz_round_trips_valid_and_refuses_invalid(tmp_path, capsys):
    """D6 fuzz, in process through `cli.main` (a real path, no mock), with a
    fixed seed: every generated valid verb succeeds and is parsed back as the
    identical verb; every generated invalid verb refuses with R1 and zero
    bytes. The two generators are independent, so an over-accepting grammar
    and an over-refusing one both fail here."""
    rng = random.Random(20261027)
    cases = [(_valid_verb(rng), True) for _ in range(30)]
    cases += [(_invalid_verb(rng), False) for _ in range(40)]

    for index, (verb, valid) in enumerate(cases):
        root = _fuzz_root(tmp_path, index)
        before = _every_file(root)
        argv = ["relate", "add", "--root", str(root), "--quiet", "--", "a.md", verb, "b.md"]
        code = cli.main(argv)
        stderr = capsys.readouterr().err
        if valid:
            assert code == 0, (verb, stderr)
            doc = cli.parse((root / "a.md").read_text(), root / "a.md", root)
            assert doc.related == ((verb, "b.md"),), (verb, doc.related)
            assert (root / "b.md").read_bytes() == before["b.md"], verb
        else:
            assert code == 2, (verb, stderr)
            assert _r1(verb) in stderr, (verb, stderr)
            assert _every_file(root) == before, verb


def test_relate_recognized_pair_still_writes_both_halves_unchanged(docs_script, tmp_path):
    """D4's byte-for-byte promise, locked at the byte level: the exact files
    and the exact two-record `--json` plan a recognized verb produces today.
    GREEN at baseline; it rejects any free-form branch that perturbs the
    recognized path."""
    root = _pair_tree(tmp_path, "recognized")

    proc = _run(
        docs_script,
        "relate",
        "add",
        "a.md",
        "precedes",
        "b.md",
        "--root",
        str(root),
        "--date",
        "2026-06-01",
        "--json",
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (root / "a.md").read_text() == _doc(
        "A", "recognized", "precedes: b.md", updated="2026-06-01"
    )
    assert (root / "b.md").read_text() == _doc(
        "B", "recognized", "follows: a.md", updated="2026-06-01"
    )
    assert json.loads(proc.stdout) == {
        "action": "add",
        "verb": "precedes",
        "inverse": "follows",
        "source": "a.md",
        "target": "b.md",
        "reason": None,
        "date": "2026-06-01",
        "dry_run": False,
        "applied": True,
        "index_refreshed": True,
        "edits": [
            {
                "path": "a.md",
                "archived": False,
                "edge": "precedes: b.md",
                "present_before": False,
                "present_after": True,
                "change": "added",
                "updated_bumped": True,
                "revision_appended": False,
            },
            {
                "path": "b.md",
                "archived": False,
                "edge": "follows: a.md",
                "present_before": False,
                "present_after": True,
                "change": "added",
                "updated_bumped": True,
                "revision_appended": False,
            },
        ],
    }
    assert proc.stderr.splitlines()[:2] == [
        "docs: relate: added 'precedes: b.md' to a.md",
        "docs: relate: added 'follows: a.md' to b.md",
    ]


def test_relate_accepts_an_endpoint_in_an_extension_lifecycle(docs_script, tmp_path):
    """D10: an endpoint in a configured `add_lifecycles` state parses, so the
    recognized pair is written exactly as on any other tree (2.0.0 refused the
    endpoint at exit 1)."""
    root = tmp_path / "ffextension"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "ffextension"\n\n[vocabulary]\nadd_lifecycles = ["shipped"]\n'
    )
    (root / "a.md").write_text(_doc("A", "ffextension", None).replace("active", "shipped", 1))
    (root / "b.md").write_text(_doc("B", "ffextension", None))

    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "- precedes: b.md" in (root / "a.md").read_text()
    assert "Lifecycle: shipped" in (root / "a.md").read_text()
    assert "- follows: a.md" in (root / "b.md").read_text()


def test_relate_refuses_an_endpoint_dated_outside_the_trees_date_format(docs_script, tmp_path):
    """D4's second D10 qualification (the E11 direction): on a `%d-%m-%Y` tree,
    an endpoint still carrying an ISO `Updated:` — which `docs check` already
    rejects as `bad-date` — is refused at exit 1 with that same diagnosis
    (2.0.0 accepted it and wrote the pair)."""
    root = tmp_path / "ffdmy"
    root.mkdir()
    (root / ".docs.toml").write_text(
        '[project]\nname = "ffdmy"\n\n[archive]\ndate_format = "%d-%m-%Y"\n'
    )
    (root / "a.md").write_text(_doc("A", "ffdmy", None, updated="20-05-2026"))
    (root / "b.md").write_text(_doc("B", "ffdmy", None))  # ISO: mis-spelled here
    before = _snapshot(root)

    proc = _run(docs_script, "relate", "add", "a.md", "precedes", "b.md", "--root", str(root))

    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "b.md: Updated: malformed date '2026-05-20' (expected %d-%m-%Y)" in proc.stderr, (
        proc.stderr
    )
    assert _snapshot(root) == before


def test_playbook_guard_free_form_dry_run_probe_exits_0(docs_script, tmp_path):
    """The Agent Playbook Suite's CI probe, replicated exactly: an EMPTY
    `.docs.toml`, two `docs new spec` documents, then a free-form `--dry-run`
    from the tree's own cwd with no `--root` — exit 0 and nothing written
    (`lifecycle-and-free-form-relate` — D9)."""
    tree = tmp_path / "guard"
    tree.mkdir()
    (tree / ".docs.toml").write_text("", encoding="utf-8")
    for slug in ("a", "b"):
        made = _run(docs_script, "new", "spec", slug, "--quiet", cwd=tree)
        assert made.returncode == 0, (made.stdout, made.stderr)
    before = _every_file(tree)

    probe = _run(docs_script, "relate", "add", "a.md", "pairs-with", "b.md", "--dry-run", cwd=tree)

    assert probe.returncode == 0, (probe.stdout, probe.stderr)
    assert _every_file(tree) == before
