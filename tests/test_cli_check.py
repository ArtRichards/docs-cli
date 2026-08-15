"""CLI end-to-end tests for `docs check` (Phase 2 — written RED).

`check` is read-only, so most tests run it directly against a fixture tree.
The stale tests build a tree with `date.today()`-relative dates so they do not
rot as the wall clock advances.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
    )


def _stale_tree(tmp_path: Path, name: str, *, include_fresh: bool) -> Path:
    """Build a tree whose only possible problem is a very old active doc."""
    root = tmp_path / name
    root.mkdir()
    (root / ".docs.toml").write_text(f'[project]\nname = "{name}"\n')
    old = (date.today() - timedelta(days=400)).isoformat()
    (root / "ancient.md").write_text(
        f"# Ancient\n\nLifecycle: active\nRole: notes\nProject: {name}\nUpdated: {old}\n\nBody.\n"
    )
    if include_fresh:
        fresh = date.today().isoformat()
        (root / "fresh.md").write_text(
            f"# Fresh\n\nLifecycle: active\nRole: notes\n"
            f"Project: {name}\nUpdated: {fresh}\n\nBody.\n"
        )
    return root


def test_check_help(docs_script):
    proc = _run(docs_script, "check", "--help")
    assert proc.returncode == 0
    assert "violation" in proc.stdout.lower()


def test_check_clean_tree_exits_0(docs_script, fixtures_dir):
    proc = _run(docs_script, "check", str(fixtures_dir / "trees" / "minimal"))
    assert proc.returncode == 0, proc.stderr
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)


def test_check_drift_tree_exits_2(docs_script, fixtures_dir):
    proc = _run(docs_script, "check", str(fixtures_dir / "trees" / "drift"))
    assert proc.returncode == 2
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)


def test_check_invalid_tree_exits_2_and_lists_findings(docs_script, fixtures_dir):
    proc = _run(docs_script, "check", str(fixtures_dir / "trees" / "invalid"))
    assert proc.returncode == 2
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    # Output is grouped by file — offending files are named.
    assert "bad-status.md" in proc.stdout
    assert "bad-date.md" in proc.stdout


def test_check_stale_only_tree_exits_1(docs_script, tmp_path):
    """A tree whose only problem is a stale doc → exit 1 (warnings only)."""
    root = _stale_tree(tmp_path, "stalecheck", include_fresh=True)
    proc = _run(docs_script, "check", str(root), "--stale", "30")
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "NotImplementedError" not in (proc.stdout + proc.stderr)
    assert "ancient.md" in proc.stdout
    assert "stale" in proc.stdout.lower()


def test_check_without_stale_flag_ignores_old_docs(docs_script, tmp_path):
    root = _stale_tree(tmp_path, "nostale", include_fresh=False)
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


def test_check_json_emits_finding_array(docs_script, fixtures_dir):
    proc = _run(docs_script, "check", str(fixtures_dir / "trees" / "invalid"), "--json")
    assert proc.returncode == 2
    data = json.loads(proc.stdout)
    assert isinstance(data, list) and data
    for rec in data:
        assert set(rec) == {"path", "severity", "rule", "message"}
        assert rec["severity"] in ("error", "warning")


def test_check_human_output_groups_by_file(docs_script, fixtures_dir):
    proc = _run(docs_script, "check", str(fixtures_dir / "trees" / "invalid"))
    assert "no-status.md" in proc.stdout
    assert "broken-ref.md" in proc.stdout


def test_check_dogfood_repo_docs_is_clean(docs_script):
    """`docs check` on this repo's own docs/ must be clean — the M3 exit criterion."""
    proc = _run(docs_script, "check", str(REPO_ROOT / "docs"))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


# --- M10 D3 — `unknown-field` rule wired through the CLI ------------------


def _vocab_tree(tmp_path: Path, name: str, add_fields: list[str]) -> Path:
    """Build a tiny docs root with a `[vocabulary] add_fields = [...]`
    sidecar and one doc carrying an `Owner:` extra metadata line.
    """
    root = tmp_path / name
    root.mkdir()
    fields_token = ", ".join(f'"{f}"' for f in add_fields)
    (root / ".docs.toml").write_text(
        f'[project]\nname = "{name}"\n\n[vocabulary]\nadd_fields = [{fields_token}]\n'
    )
    today = date.today().isoformat()
    (root / "doc.md").write_text(
        f"# Doc\n\nLifecycle: active\nRole: notes\nProject: {name}\n"
        f"Updated: {today}\nOwner: alice\n\nBody.\n"
    )
    return root


def test_check_cli_unknown_field_exits_1(docs_script, tmp_path):
    """OQ-F + OQ-H: allowlist = `["Tags"]` + doc with `Owner:` ⇒ exit 1
    + `unknown-field` token in stdout.
    """
    root = _vocab_tree(tmp_path, "uf-mismatch", add_fields=["Tags"])
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "unknown-field" in proc.stdout, proc.stdout
    assert "Owner" in proc.stdout, proc.stdout


def test_check_cli_allowlist_match_exits_0(docs_script, tmp_path):
    """OQ-H: allowlist = `["Owner"]` + doc with `Owner:` ⇒ exit 0; no
    `unknown-field` mention.
    """
    root = _vocab_tree(tmp_path, "uf-match", add_fields=["Owner"])
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "unknown-field" not in proc.stdout, proc.stdout


# --- M19 D2 — `[check] stale_days` config default + threshold provenance ---
#
# RED at baseline: nothing reads `[check] stale_days` until Phases 5-6, so a
# configured default does not affect bare `docs check` and the provenance
# parenthetical is not yet emitted. These fail as plain assertion mismatches
# (exit code / stdout substring), not tracebacks or argparse refusals.
#
# Phase 3 fixture: `_stale_config_tree` mirrors `_stale_tree` but emits the
# `[check] stale_days = N` sidecar; the stale doc's `Updated:` is
# `today`-relative so the case never rots.


def _stale_config_tree(tmp_path: Path, name: str, *, stale_days: int) -> Path:
    """A docs root with `[check] stale_days = N` + one ancient active doc.

    Mirrors `_stale_tree`, adding the `[check]` sidecar. The ancient doc is
    400 days old (well past any small window), so a configured `stale_days`
    makes bare `docs check` flag it.
    """
    root = tmp_path / name
    root.mkdir()
    (root / ".docs.toml").write_text(
        f'[project]\nname = "{name}"\n\n[check]\nstale_days = {stale_days}\n'
    )
    old = (date.today() - timedelta(days=400)).isoformat()
    (root / "ancient.md").write_text(
        f"# Ancient\n\nLifecycle: active\nRole: notes\nProject: {name}\nUpdated: {old}\n\nBody.\n"
    )
    return root


def test_check_config_stale_days_applies_to_bare_check(docs_script, tmp_path):
    """HEADLINE D2 (Q5): a configured `[check] stale_days` makes BARE
    `docs check` (no `--stale` flag) apply the stale rule → exit 1.
    """
    root = _stale_config_tree(tmp_path, "cfg-bare", stale_days=30)
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "ancient.md" in proc.stdout
    assert "stale" in proc.stdout.lower()


def test_check_cli_stale_overrides_config(docs_script, tmp_path):
    """An explicit CLI `--stale 99999` overrides the configured `stale_days`,
    clearing the ancient doc → exit 0 (CLI wins).
    """
    root = _stale_config_tree(tmp_path, "cfg-override", stale_days=30)
    proc = _run(docs_script, "check", str(root), "--stale", "99999")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


def test_check_no_check_section_unchanged(docs_script, tmp_path):
    """GREEN-at-baseline regression lock: a tree with NO `[check]` section and
    an old active doc, checked bare (no `--stale`), is unchanged → exit 0.
    """
    root = _stale_tree(tmp_path, "no-check-section", include_fresh=False)
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


def test_check_config_sourced_provenance_message(docs_script, tmp_path):
    """A config-sourced stale finding names the file + key so the operator
    knows where to change the window.
    """
    root = _stale_config_tree(tmp_path, "cfg-prov", stale_days=30)
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    # Full frozen parenthetical (Decision: BINDING), not just the trailing clause.
    assert "(stale threshold 30, set in .docs.toml [check] stale_days)" in proc.stdout
    # Mutually exclusive with the CLI-sourced variant — config did not come via --stale.
    assert "via --stale" not in proc.stdout


def test_check_cli_sourced_provenance_message(docs_script, tmp_path):
    """A CLI-sourced stale finding names `--stale` and does NOT carry the
    config clause (the threshold did not come from the config).
    """
    root = _stale_tree(tmp_path, "cli-prov", include_fresh=False)
    proc = _run(docs_script, "check", str(root), "--stale", "30")
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    # Full frozen parenthetical (Decision: BINDING), not just the trailing clause.
    assert "(stale threshold 30, via --stale)" in proc.stdout
    assert "set in .docs.toml [check] stale_days" not in proc.stdout


def test_check_stale_zero_honored(docs_script, tmp_path):
    """GREEN-at-baseline: `--stale 0` is honoured as given (flag every active
    doc not updated *today*), not treated as unset. An old active doc → 1.
    """
    root = _stale_tree(tmp_path, "stale-zero", include_fresh=False)
    proc = _run(docs_script, "check", str(root), "--stale", "0")
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "ancient.md" in proc.stdout


def test_check_config_stale_days_zero_honored(docs_script, tmp_path):
    """A configured `[check] stale_days = 0` is honoured as given (not treated
    as unset): a >0-day-old active doc is flagged → exit 1, with the config-
    sourced provenance. The config-side mirror of `test_check_stale_zero_honored`
    — locks `resolve_stale`'s `is not None` (vs truthiness) on the config path.
    """
    root = _stale_config_tree(tmp_path, "cfg-zero", stale_days=0)
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "ancient.md" in proc.stdout
    assert "(stale threshold 0, set in .docs.toml [check] stale_days)" in proc.stdout


def test_check_malformed_stale_days_refused_cleanly(docs_script, tmp_path):
    """OQ-1 (Step-2 review amendment): a non-integer `[check] stale_days`
    (e.g. the TOML string `"14"`) is refused at config load — clean exit 2 with
    the `malformed .docs.toml` message naming the key, NOT a TypeError traceback
    flowing through the stale comparison.
    """
    root = _stale_config_tree(tmp_path, "cfg-bad", stale_days=30)
    # Overwrite the sidecar with a string value (the helper writes a bare int).
    (root / ".docs.toml").write_text('[project]\nname = "cfg-bad"\n\n[check]\nstale_days = "14"\n')
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "malformed .docs.toml" in proc.stderr
    assert "stale_days must be an integer" in proc.stderr
    # A clean refusal, not an uncaught crash.
    assert "Traceback" not in proc.stderr
    assert "TypeError" not in proc.stderr


# --- M25 (D2) — `missing-inverse` through the CLI --------------------------
#
# Phase 2 (written RED). Intended RED: the rule does not exist yet, so the
# fixture tree exits 0 and prints nothing (plain assertion failure).

TREES = REPO_ROOT / "tests" / "fixtures" / "trees"


def test_check_missing_inverse_exits_2_and_names_repair(docs_script):
    """A one-sided recognized edge is a hard error naming the exact repair."""
    proc = _run(docs_script, "check", str(TREES / "reciprocal-missing"))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "Traceback" not in (proc.stdout + proc.stderr)
    # Grouping header, not a substring hit: `a.md` also occurs inside the
    # message body ("must declare 'follows: a.md'"), so only the bare
    # header line proves the finding is FILED against the source doc.
    assert "a.md" in proc.stdout.splitlines(), "output is grouped by file; the SOURCE is named"
    assert "missing-inverse" in proc.stdout
    assert (
        "Related: 'precedes: b.md' has no inverse; "
        "b.md must declare 'follows: a.md' (or remove the edge)"
    ) in proc.stdout


def test_check_missing_inverse_json_record_keys_unchanged(docs_script):
    """D2: no new JSON field — the record key set stays exactly the M3 four."""
    proc = _run(docs_script, "check", str(TREES / "reciprocal-missing"), "--json")
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    data = json.loads(proc.stdout)
    records = [rec for rec in data if rec.get("rule") == "missing-inverse"]
    assert len(records) == 1, f"exactly one missing-inverse record, got {data!r}"
    rec = records[0]
    assert set(rec) == {"path", "severity", "rule", "message"}, (
        "M25 adds NO new JSON field; the repair lives in `message`"
    )
    assert rec["severity"] == "error"
    assert rec["path"] == "a.md", "root-relative POSIX path of the SOURCE doc"
    assert "follows: a.md" in rec["message"], "the message names the exact missing inverse"
    assert "b.md" in rec["message"]


def test_check_clean_reciprocal_tree_exits_0(docs_script):
    """All three pairs complete in both directions → clean.

    GREEN-at-baseline but DEGENERATE (passes today only because the rule
    does not exist); the real over-fire guard after Phase 6.
    """
    proc = _run(docs_script, "check", str(TREES / "reciprocal-clean"))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


def test_check_archived_pair_missing_inverse_exits_2(docs_script):
    """Archived endpoints are walked, so they are reciprocity-checked too.

    The finding an operator can only repair through `docs relate --reason`
    (D4). Intended RED: no rule yet.
    """
    proc = _run(docs_script, "check", str(TREES / "reciprocal-archived-missing"))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "archive/2026-01-01/old.md must declare 'required-by: a.md'" in proc.stdout


# --- M25 (D7) — `duplicate-field` through the CLI --------------------------


def test_check_duplicate_field_exits_2_and_names_the_label(docs_script):
    """A repeated metadata label is a hard error naming the label and the loss."""
    proc = _run(docs_script, "check", str(TREES / "duplicate-field"))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "Traceback" not in (proc.stdout + proc.stderr)
    assert "a.md" in proc.stdout.splitlines(), "output is grouped by file"
    assert "duplicate-field" in proc.stdout
    assert (
        "metadata field 'Related:' appears 2 times; only the last occurrence is read"
    ) in proc.stdout


def test_check_duplicate_field_json_record_shape(docs_script):
    """The record's key set is closed — `duplicate-field` adds no JSON field."""
    proc = _run(docs_script, "check", str(TREES / "duplicate-field"), "--json")
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    data = json.loads(proc.stdout)
    records = [rec for rec in data if rec.get("rule") == "duplicate-field"]
    assert len(records) == 1, f"exactly one duplicate-field record, got {data!r}"
    assert set(records[0]) == {"path", "severity", "rule", "message"}
    assert records[0]["severity"] == "error"
    assert records[0]["path"] == "a.md"


# --- M26 — a scoped archive leaves the check gate clean --------------------


def test_check_clean_after_a_scoped_archive(docs_script, tmp_path):
    """M26 — D1 through the real `docs check` gate: an explicitly scoped
    archive of a milestone pair lands with every `Related:` edge resolving.

    This is the M12 / M18 no-regression proof restated for the invocation
    that replaces bare `--cascade`: `milestone.md` and its impl log move
    together, the five spine docs stay put, and their edges to the moved
    pair are repointed into `archive/2026-05-28/`.

    Uses the committed `archive-neighborhood` fixture (M26 — Phase-1 Q13), so
    the lock does not depend on this repo's live docs tree.
    """
    root = tmp_path / "tree"
    shutil.copytree(TREES / "archive-neighborhood", root)

    archive = _run(
        docs_script,
        "archive",
        str(root / "milestone.md"),
        "--cascade-only",
        "milestone*",
        "--date",
        "2026-05-28",
    )
    assert archive.returncode == 0, (archive.stdout, archive.stderr)
    assert (root / "archive" / "2026-05-28" / "milestone.md").is_file()
    assert (root / "archive" / "2026-05-28" / "milestone-impl.md").is_file()
    # The specification spine is NOT selected and stays in the active tree.
    for rel in ("plan.md", "cli.md", "convention.md", "test-strategy.md", "status.md"):
        assert (root / rel).is_file(), f"{rel} must not be archived by a milestone* scope"

    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, (check.stdout, check.stderr)


# --- M27 (D4 / D4b) — body-link validation through the CLI -----------------
#
# Phase 2 (written RED). Intended RED: neither rule exists yet, so every
# `bodylink-*` fixture tree exits 0 and prints nothing (plain assertion
# failure). Every intended-exit-2 test here ALSO asserts its frozen contract
# message, so none can be satisfied by an unrelated exit 2 — the M26
# falsely-GREEN lesson.
#
# Between Phase 2 and Phase 3 these fail on the missing fixture directory
# instead; `_bodylink_tree` makes that explicit rather than letting a
# vacuously-empty walk look like a pass.


def _bodylink_tree(name: str) -> Path:
    """Path to a committed `bodylink-*` fixture tree, proving it exists.

    `docs check` on a missing directory walks nothing and exits 0, so the
    exit-0 locks below would pass on a fixture that was never written. The
    guard is what keeps them honest before Phase 3.
    """
    root = TREES / name
    assert root.is_dir(), f"missing fixture tree {name!r} (Phase 3 supplies it)"
    return root


def test_check_broken_body_link_exits_2_and_names_the_line(docs_script):
    """D4: a local body link naming no existing path is a hard error, and the
    finding carries everything an agent needs to repair it in `message`.
    """
    proc = _run(docs_script, "check", str(_bodylink_tree("bodylink-broken")))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "Traceback" not in (proc.stdout + proc.stderr)
    # Grouping header, not a substring hit: `doc.md` also occurs elsewhere in
    # the output, so only the bare header line proves the finding is FILED
    # against the referring doc.
    assert "doc.md" in proc.stdout.splitlines(), "output is grouped by file; the REFERRER is named"
    assert "broken-body-link" in proc.stdout
    assert (
        "body link at line 8 does not resolve to an existing path: plan.md (resolves to plan.md)"
    ) in proc.stdout


def test_check_broken_body_link_json_record_keys_unchanged(docs_script):
    """D4/Q4: no new JSON field — the record key set stays exactly the M3 four."""
    proc = _run(docs_script, "check", str(_bodylink_tree("bodylink-broken")), "--json")
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    data = json.loads(proc.stdout)
    records = [rec for rec in data if rec.get("rule") == "broken-body-link"]
    assert len(records) == 1, f"exactly one broken-body-link record, got {data!r}"
    rec = records[0]
    assert set(rec) == {"path", "severity", "rule", "message"}, (
        "M27 adds NO new JSON field; the line, the raw destination and the "
        "candidate all live in `message`"
    )
    assert rec["severity"] == "error"
    assert rec["path"] == "doc.md", "root-relative POSIX path of the REFERRING doc"
    assert "line 8" in rec["message"]
    assert "plan.md" in rec["message"]


def test_check_outside_root_body_link_exits_2_and_names_the_url_repair(docs_script):
    """D4b: an escaping destination is reported, and the message names the
    repair — replace it with a URL — mirroring `missing-inverse`'s
    `(or remove the edge)`.
    """
    proc = _run(docs_script, "check", str(_bodylink_tree("bodylink-outside-root")))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "Traceback" not in (proc.stdout + proc.stderr)
    assert "doc.md" in proc.stdout.splitlines(), "output is grouped by file"
    assert "outside-root-body-link" in proc.stdout
    assert "leaves the docs root:" in proc.stdout
    assert "links outside the tree must be URLs" in proc.stdout


def test_check_outside_root_body_link_json_record_keys_unchanged(docs_script):
    """D4b: the second rule leaves the record closed too."""
    proc = _run(docs_script, "check", str(_bodylink_tree("bodylink-outside-root")), "--json")
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    data = json.loads(proc.stdout)
    records = [rec for rec in data if rec.get("rule") == "outside-root-body-link"]
    assert len(records) == 2, f"exactly two outside-root-body-link records, got {data!r}"
    for rec in records:
        assert set(rec) == {"path", "severity", "rule", "message"}
        assert rec["severity"] == "error"
        assert rec["path"] == "doc.md"


def test_check_outside_root_emits_no_broken_body_link_record(docs_script):
    """BINDING precedence, at the CLI: containment is tested BEFORE existence,
    so an escaping destination yields `outside-root-body-link` ONLY.

    One of the fixture's two escapes points at a path that CANNOT exist and
    the other at one that provably does; neither may produce a
    `broken-body-link`, because deciding brokenness would need precisely the
    stat the boundary forbids.
    """
    proc = _run(docs_script, "check", str(_bodylink_tree("bodylink-outside-root")), "--json")
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    data = json.loads(proc.stdout)
    assert [rec["rule"] for rec in data] == ["outside-root-body-link"] * 2, (
        f"the two rules must never double-report, got {data!r}"
    )


def test_check_bodylink_clean_tree_exits_0(docs_script):
    """Every supported form, resolving → clean.

    GREEN-at-baseline but DEGENERATE (passes today only because the rules do
    not exist); the real over-fire guard after Phase 6.
    """
    proc = _run(docs_script, "check", str(_bodylink_tree("bodylink-clean")))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


def test_check_bodylink_excluded_forms_tree_exits_0(docs_script):
    """E5/E8/D2: images, autolinks, raw HTML, code, schemed, protocol-relative,
    root-absolute, fragment-only, reference uses and an escaped span → silence.

    GREEN-at-baseline but DEGENERATE; the over-fire guard after Phase 6.
    """
    proc = _run(docs_script, "check", str(_bodylink_tree("bodylink-excluded-forms")))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


def test_check_verdict_is_identical_from_a_relocated_copy(docs_script, tmp_path):
    """D4b hermeticity: the verdict is a function of the tree ALONE.

    The same bytes checked from a different location — with no sibling
    directories of any kind around them — must produce the identical exit code
    and the identical stdout. This is the property that makes `docs check`
    usable as a CI gate: a tree that passes in a git clone must pass in a
    container and in a vendored subtree.

    GREEN-at-baseline but DEGENERATE (nothing reads the body yet); the real
    hermeticity lock from Phase 6.
    """
    src = _bodylink_tree("bodylink-outside-root")
    dst = tmp_path / "relocated"
    shutil.copytree(src, dst)

    here = _run(docs_script, "check", str(src))
    there = _run(docs_script, "check", str(dst))
    assert here.returncode == there.returncode, (here.stdout, there.stdout)
    assert here.stdout == there.stdout, "identical bytes must yield an identical verdict"


# --- M28 — the `movelink-*` fixture family is clean as committed -----------

_MOVELINK_TREES = (
    "movelink-archived-referrer",
    "movelink-both",
    "movelink-closeout",
    "movelink-incoming",
    "movelink-moved-referrer",
    "movelink-nested",
    "movelink-strand",
)


def test_check_every_movelink_fixture_tree_is_clean_as_committed(docs_script, fixtures_dir):
    """Phase 3's exit criterion, asserted rather than assumed.

    Every `movelink-*` tree is swept automatically into
    `test_check_tree_legacy_fixtures_gain_no_new_findings` (29 -> 36) and
    `test_check_tree_pre_m27_fixtures_gain_no_body_link_findings` (33 -> 40),
    but those two assert only that ONE rule stays silent. This asserts the
    whole gate: each tree is `docs check`-clean as committed, so every
    post-move clean assertion elsewhere measures the MOVE rather than
    pre-existing damage in the fixture.

    Named explicitly rather than derived from the directory: a parametrization
    over a glob would generate zero ids before Phase 3 and be vacuously green.

    Intended RED until Phase 3.
    """
    on_disk = sorted(
        d.name
        for d in (fixtures_dir / "trees").iterdir()
        if d.is_dir() and d.name.startswith("movelink-")
    )
    assert on_disk == sorted(_MOVELINK_TREES), (
        "the hand-written list and the directory must agree, or an eighth "
        f"`movelink-*` tree would be silently unchecked here. On disk: {on_disk!r}"
    )

    for name in _MOVELINK_TREES:
        root = fixtures_dir / "trees" / name
        assert root.is_dir(), f"Phase 3 must author the `{name}` fixture tree"
        proc = _run(docs_script, "check", str(root))
        assert proc.returncode == 0, f"{name} is not clean as committed:\n{proc.stdout}"


# ===========================================================================
# M28a — `archive-date-drift` at the CLI, over the `archivedate-*` fixture
# family.
#
# The contract under test is the milestone's *Decisions (Phase 1 — BINDING)*
# items (C)–(E) and `cli.md` › `docs check` › *Archive-date corroboration*.
# Every test below asserts a frozen contract string as well as an exit code,
# so an unrelated failure with the same code cannot satisfy it (M26's
# falsely-GREEN lesson).
# ===========================================================================

_FORM_A = (
    "Archived: 2026-01-01 but the file is in archive/2026-03-04/ "
    "(move it back, or correct the recorded date)"
)
_FORM_B = (
    "Archived: 2026-01-01 but the file is not under a dated archive/ directory "
    "(move it back, or remove the field)"
)

# The hand-written registration of M28a's fixture family, with each tree's
# COMPLETE expected finding set as committed. Named explicitly rather than
# derived from a glob: a parametrization over a glob would generate zero ids
# before Phase 3 and be vacuously green. Three of the six are deliberately
# drifted, so "clean" is not the whole gate here — the expected set is.
_ARCHIVEDATE_TREES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("archivedate-absent", ()),
    ("archivedate-clean", ()),
    ("archivedate-drifted", (("archive/2026-03-04/moved.md", "archive-date-drift"),)),
    (
        "archivedate-outside",
        (
            ("escaped.md", "archive-date-drift"),
            ("stale-both.md", "status-drift"),
            ("stale-both.md", "archive-date-drift"),
        ),
    ),
    ("archivedate-two-dated-dirs", ()),
    ("archivedate-undated", (("archive/misc/filed.md", "archive-date-drift"),)),
)


def _archivedate_tree(fixtures_dir: Path, name: str) -> Path:
    """The committed `archivedate-*` tree, asserted to exist.

    `docs check` is read-only, so these run against the committed tree; the
    existence assertion is what keeps the family honestly RED between Phase 2
    and Phase 3 rather than erroring on a missing directory.
    """
    root = fixtures_dir / "trees" / name
    assert root.is_dir(), f"Phase 3 must author the `{name}` fixture tree"
    return root


def _findings(docs_script: Path, root: Path) -> tuple[int, list[tuple[str, str]], list[dict]]:
    proc = _run(docs_script, "check", str(root), "--json")
    records = json.loads(proc.stdout) if proc.stdout.strip() else []
    return proc.returncode, [(r["path"], r["rule"]) for r in records], records


def test_check_every_archivedate_fixture_tree_matches_its_registration(docs_script, fixtures_dir):
    """Phase 3's exit criterion, asserted rather than assumed.

    Every `archivedate-*` tree is swept automatically into the three
    whole-corpus sweeps, but each of those asserts only that ONE rule family
    stays silent. This asserts the whole gate: each tree's COMPLETE finding
    set, as committed, is exactly the one its semantic calls for — so every
    assertion elsewhere measures the thing under test rather than pre-existing
    damage in the fixture.

    Intended RED until Phase 3 (the trees) and Phase 6 (the rule).
    """
    on_disk = sorted(
        d.name
        for d in (fixtures_dir / "trees").iterdir()
        if d.is_dir() and d.name.startswith("archivedate-")
    )
    assert on_disk == sorted(name for name, _ in _ARCHIVEDATE_TREES), (
        "the hand-written list and the directory must agree, or a seventh "
        f"`archivedate-*` tree would be silently unchecked here. On disk: {on_disk!r}"
    )

    for name, expected in _ARCHIVEDATE_TREES:
        root = _archivedate_tree(fixtures_dir, name)
        code, pairs, _records = _findings(docs_script, root)
        assert pairs == list(expected), f"{name} findings as committed: {pairs!r}"
        assert code == (2 if expected else 0), f"{name} exit code"


def test_check_archivedate_clean_tree_exits_0(docs_script, fixtures_dir):
    """E5, the DECLINE locked: `archivedate-clean` carries a deliberate
    cross-dated `pairs-with` pair, both ends corroborated, and says nothing.

    The reporter's suggested rule — warn when `pairs-with` partners sit in
    different dated archive directories — would fire here. It is declined, and
    this is the lock that proves it was not smuggled in.
    """
    root = _archivedate_tree(fixtures_dir, "archivedate-clean")
    first = (root / "archive" / "2026-01-01" / "first.md").read_text()
    second = (root / "archive" / "2026-03-04" / "second.md").read_text()
    assert "pairs-with: archive/2026-03-04/second.md" in first, (
        "the fixture must carry the cross-dated pair the decline is about"
    )
    assert "pairs-with: archive/2026-01-01/first.md" in second
    assert "Archived: 2026-01-01" in first and "Archived: 2026-03-04" in second

    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 0, proc.stdout
    assert "archive-date-drift" not in proc.stdout


def test_check_archivedate_absent_tree_exits_0(docs_script, fixtures_dir):
    """D6, the whole compatibility story: a pre-2.0 archived document — an
    `Archived-reason:` line and no witness — is silent."""
    root = _archivedate_tree(fixtures_dir, "archivedate-absent")
    old = (root / "archive" / "2026-01-01" / "old.md").read_text()
    assert "Archived-reason:" in old, "the fixture must look archived, minus the witness"
    assert "\nArchived:" not in old, "…and must carry NO witness at all"

    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 0, proc.stdout
    assert "archive-date-drift" not in proc.stdout


def test_check_archivedate_drifted_tree_exits_2_with_form_a(docs_script, fixtures_dir):
    """E1d detected: a witness-carrying document in a DIFFERENT dated
    directory, however the relocation was produced."""
    root = _archivedate_tree(fixtures_dir, "archivedate-drifted")
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "archive/2026-03-04/moved.md" in proc.stdout.splitlines(), (
        "output is grouped by file; the drifted document is named"
    )
    assert f"  error: [archive-date-drift] {_FORM_A}" in proc.stdout


def test_check_archivedate_drifted_json_record_keys_unchanged(docs_script, fixtures_dir):
    """D4: no new JSON field — the key set stays exactly the M3 four, and BOTH
    dates travel in `message`."""
    root = _archivedate_tree(fixtures_dir, "archivedate-drifted")
    code, _pairs, records = _findings(docs_script, root)
    assert code == 2
    drift = [r for r in records if r.get("rule") == "archive-date-drift"]
    assert len(drift) == 1, f"exactly one archive-date-drift record, got {records!r}"
    rec = drift[0]
    assert set(rec) == {"path", "severity", "rule", "message"}, (
        "M28a adds NO new JSON field; both dates live in `message`"
    )
    assert rec["severity"] == "error"
    assert rec["path"] == "archive/2026-03-04/moved.md"
    assert rec["message"] == _FORM_A
    assert "2026-01-01" in rec["message"] and "2026-03-04" in rec["message"]


def test_check_archivedate_outside_tree_reports_both_status_drift_directions(
    docs_script, fixtures_dir
):
    """Q7, both directions of the `status-drift` interaction in one tree.

    `escaped.md` is `Lifecycle: active` outside the archive — `status-drift` is
    SILENT and the stale witness is the only evidence. `stale-both.md` is
    `Lifecycle: archived` outside the archive — both rules fire, independently,
    on one document, in the frozen order.
    """
    root = _archivedate_tree(fixtures_dir, "archivedate-outside")
    code, pairs, _records = _findings(docs_script, root)
    assert code == 2
    assert pairs == [
        ("escaped.md", "archive-date-drift"),
        ("stale-both.md", "status-drift"),
        ("stale-both.md", "archive-date-drift"),
    ], pairs

    proc = _run(docs_script, "check", str(root))
    assert f"  error: [archive-date-drift] {_FORM_B}" in proc.stdout


def test_check_archivedate_undated_tree_exits_2_with_form_b_and_no_status_drift(
    docs_script, fixtures_dir
):
    """Q7's second shape: `archive/misc/filed.md` is `Lifecycle: archived`
    INSIDE the archive subtree, so `status-drift` is silent by construction —
    and the recorded date still has no corroborating location.
    """
    root = _archivedate_tree(fixtures_dir, "archivedate-undated")
    code, pairs, _records = _findings(docs_script, root)
    assert code == 2
    assert pairs == [("archive/misc/filed.md", "archive-date-drift")], pairs
    assert "status-drift" not in [rule for _path, rule in pairs]

    proc = _run(docs_script, "check", str(root))
    assert f"  error: [archive-date-drift] {_FORM_B}" in proc.stdout


def test_check_archivedate_two_dated_dirs_tree_is_clean_as_committed(docs_script, fixtures_dir):
    """The `docs mv` fixture is clean before any move, so every Leg-2
    assertion measures the MOVE rather than pre-existing damage."""
    root = _archivedate_tree(fixtures_dir, "archivedate-two-dated-dirs")
    with_witness = (root / "archive" / "2026-01-01" / "with-witness.md").read_text()
    no_witness = (root / "archive" / "2026-01-01" / "no-witness.md").read_text()
    assert "Archived: 2026-01-01" in with_witness
    assert "\nArchived:" not in no_witness, (
        "the no-witness member is what makes Leg 2 provably independent of the field"
    )
    proc = _run(docs_script, "check", str(root))
    assert proc.returncode == 0, proc.stdout
