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
import stat
import subprocess
import sys
from pathlib import Path


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
    assert "Updated: 2026-05-20" not in a_text, "a changed endpoint gets its Updated: bumped"
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
        "pairs-with",
        "b.md",
        "--root",
        str(root),
        "--quiet",
    )
    assert refused.returncode == 2
    assert "docs: relate: unknown verb 'pairs-with'" in refused.stderr, (
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


def test_relate_unknown_verb_refuses(docs_script, tmp_path):
    root = _pair_tree(tmp_path, "unknownverb")
    before = _snapshot(root)
    proc = _run(docs_script, "relate", "add", "a.md", "pairs-with", "b.md", "--root", str(root))
    assert proc.returncode == 2
    assert (
        "docs: relate: unknown verb 'pairs-with'; expected one of: "
        "blocked-by, blocks, depends-on, follows, precedes, required-by"
    ) in proc.stderr
    assert _snapshot(root) == before


def test_relate_case_variant_verb_refuses(docs_script, tmp_path):
    """Matching is case-sensitive exact: `Precedes` is a free-form verb."""
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
    assert text.index("2026-08-11") < text.index("2026-08-12"), "chronological"


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
