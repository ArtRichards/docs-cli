"""Unit tests for the M3 validators (Phase 2 — written RED).

Targets: `check_doc`, `check_tree`, `exit_code_for`, `Finding`. The per-doc
rule tests use inline strings; the tree tests point at fixture trees.
"""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import pytest

import docs as _cli
from docs import (
    BUILTIN_ROLES,
    BUILTIN_STATUSES,
    Config,
    Finding,
    check_doc,
    check_tree,
    compile_exclude_predicate,
    exit_code_for,
    load_config,
)

_TODAY = date(2026, 5, 22)


def _config() -> Config:
    return Config(
        project="probe",
        archive_dir="archive",
        date_format="%Y-%m-%d",
        lifecycles=BUILTIN_STATUSES,
        roles=BUILTIN_ROLES,
    )


def _valid(lifecycle: str = "active", role: str = "spec", updated: str = "2026-05-20") -> str:
    """A well-formed doc body with one field optionally varied."""
    return (
        f"# Sample\n\nLifecycle: {lifecycle}\nRole: {role}\n"
        f"Project: probe\nUpdated: {updated}\n\nBody paragraph.\n"
    )


# --- clean doc -------------------------------------------------------------


def test_check_doc_clean_doc_has_no_findings():
    findings = check_doc(
        Path("/r/sample.md"), _valid(), Path("/r"), _config(), stale=None, today=_TODAY
    )
    assert findings == []


# --- missing / empty required fields --------------------------------------


def test_check_doc_missing_status():
    text = "# Sample\n\nRole: spec\nProject: probe\nUpdated: 2026-05-20\n\nBody.\n"
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=None, today=_TODAY)
    assert [f.rule for f in findings] == ["missing-field"]
    assert findings[0].severity == "error"
    assert "Lifecycle" in findings[0].message


def test_check_doc_empty_required_field():
    text = "# Sample\n\nLifecycle: active\nRole:\nProject: probe\nUpdated: 2026-05-20\n\nBody.\n"
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=None, today=_TODAY)
    assert [f.rule for f in findings] == ["missing-field"]
    assert "Role" in findings[0].message


def test_check_doc_missing_h1_is_malformed():
    text = "Lifecycle: active\nRole: spec\nProject: probe\nUpdated: 2026-05-20\n\nBody.\n"
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=None, today=_TODAY)
    assert [f.rule for f in findings] == ["malformed"]
    assert findings[0].severity == "error"


# --- vocabulary -----------------------------------------------------------


def test_check_doc_unknown_status():
    findings = check_doc(
        Path("/r/d.md"),
        _valid(lifecycle="frobnicated"),
        Path("/r"),
        _config(),
        stale=None,
        today=_TODAY,
    )
    assert [f.rule for f in findings] == ["bad-vocab"]
    assert "frobnicated" in findings[0].message


def test_check_doc_unknown_role():
    findings = check_doc(
        Path("/r/d.md"),
        _valid(role="wizard"),
        Path("/r"),
        _config(),
        stale=None,
        today=_TODAY,
    )
    assert [f.rule for f in findings] == ["bad-vocab"]
    assert "wizard" in findings[0].message


# --- date -----------------------------------------------------------------


def test_check_doc_unparseable_date():
    findings = check_doc(
        Path("/r/d.md"),
        _valid(updated="2026-13-99"),
        Path("/r"),
        _config(),
        stale=None,
        today=_TODAY,
    )
    assert [f.rule for f in findings] == ["bad-date"]
    assert findings[0].severity == "error"


# --- status / location drift ---------------------------------------------


def test_check_doc_archived_status_outside_archive_subtree(tmp_path):
    doc = tmp_path / "stray.md"
    findings = check_doc(
        doc, _valid(lifecycle="archived"), tmp_path, _config(), stale=None, today=_TODAY
    )
    assert [f.rule for f in findings] == ["status-drift"]
    assert findings[0].severity == "error"


def test_check_doc_active_status_inside_archive_subtree(tmp_path):
    doc = tmp_path / "archive" / "2026-01-01" / "lingering.md"
    findings = check_doc(
        doc, _valid(lifecycle="active"), tmp_path, _config(), stale=None, today=_TODAY
    )
    assert [f.rule for f in findings] == ["status-drift"]


def test_check_doc_archived_status_inside_archive_is_clean(tmp_path):
    doc = tmp_path / "archive" / "2026-01-01" / "proper.md"
    findings = check_doc(
        doc, _valid(lifecycle="archived"), tmp_path, _config(), stale=None, today=_TODAY
    )
    assert findings == []


# --- broken Related: refs -------------------------------------------------


def test_check_doc_broken_related_ref(tmp_path):
    (tmp_path / "exists.md").write_text(_valid())
    text = (
        "# Sample\n\nLifecycle: active\nRole: spec\nProject: probe\n"
        "Updated: 2026-05-20\n\nRelated:\n- pairs-with: ghost.md\n\nBody.\n"
    )
    findings = check_doc(
        tmp_path / "sample.md", text, tmp_path, _config(), stale=None, today=_TODAY
    )
    assert [f.rule for f in findings] == ["broken-ref"]
    assert "ghost.md" in findings[0].message


def test_check_doc_resolvable_related_ref_is_clean(tmp_path):
    (tmp_path / "exists.md").write_text(_valid())
    text = (
        "# Sample\n\nLifecycle: active\nRole: spec\nProject: probe\n"
        "Updated: 2026-05-20\n\nRelated:\n- pairs-with: exists.md\n\nBody.\n"
    )
    findings = check_doc(
        tmp_path / "sample.md", text, tmp_path, _config(), stale=None, today=_TODAY
    )
    assert findings == []


# --- stale ----------------------------------------------------------------


def test_check_doc_stale_active_doc_warns_when_stale_set():
    text = _valid(lifecycle="active", updated="2026-01-01")
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=30, today=_TODAY)
    assert [f.rule for f in findings] == ["stale"]
    assert findings[0].severity == "warning"


def test_check_doc_stale_not_reported_without_stale_flag():
    text = _valid(lifecycle="active", updated="2026-01-01")
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=None, today=_TODAY)
    assert findings == []


def test_check_doc_stale_ignores_non_active_docs():
    text = _valid(lifecycle="draft", updated="2026-01-01")
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=30, today=_TODAY)
    assert findings == []


def test_check_doc_recent_active_doc_not_stale():
    text = _valid(lifecycle="active", updated="2026-05-20")
    findings = check_doc(Path("/r/d.md"), text, Path("/r"), _config(), stale=30, today=_TODAY)
    assert findings == []


# --- exit_code_for --------------------------------------------------------


def test_exit_code_for_no_findings_is_zero():
    assert exit_code_for([]) == 0


def test_exit_code_for_warnings_only_is_one():
    findings = [Finding(Path("/r/d.md"), "warning", "stale", "stale doc")]
    assert exit_code_for(findings) == 1


def test_exit_code_for_any_error_is_two():
    findings = [
        Finding(Path("/r/d.md"), "warning", "stale", "stale doc"),
        Finding(Path("/r/e.md"), "error", "bad-vocab", "bad status"),
    ]
    assert exit_code_for(findings) == 2


# --- check_tree -----------------------------------------------------------


def test_check_tree_clean_tree_has_no_findings(fixtures_dir):
    root = fixtures_dir / "trees" / "minimal"
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    assert findings == []


def test_check_tree_drift_tree_reports_status_drift(fixtures_dir):
    root = fixtures_dir / "trees" / "drift"
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    assert {f.rule for f in findings} == {"status-drift"}
    assert len(findings) == 2


def test_check_tree_invalid_tree_reports_every_rule(fixtures_dir):
    root = fixtures_dir / "trees" / "invalid"
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    rules = {f.rule for f in findings}
    assert {"missing-field", "bad-vocab", "bad-date", "broken-ref", "malformed"} <= rules


def test_check_tree_findings_sorted_by_path(fixtures_dir):
    root = fixtures_dir / "trees" / "invalid"
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    paths = [f.path.as_posix() for f in findings]
    assert paths == sorted(paths)


# --- M10 D3 — `unknown-field` rule (gated by [vocabulary] add_fields) ------


def _config_with_fields(fields: frozenset[str]) -> Config:
    return Config(
        project="probe",
        archive_dir="archive",
        date_format="%Y-%m-%d",
        lifecycles=BUILTIN_STATUSES,
        roles=BUILTIN_ROLES,
        fields=fields,
    )


def _doc_with_extra_field(label: str, value: str) -> str:
    """A well-formed doc body that ALSO carries an extra inline metadata
    line under the metadata block.
    """
    return (
        f"# Sample\n\n"
        f"Lifecycle: active\nRole: spec\nProject: probe\nUpdated: 2026-05-20\n"
        f"{label}: {value}\n\nBody paragraph.\n"
    )


def test_check_doc_unknown_field_with_no_allowlist_is_clean():
    """OQ-H + OQ-O: with empty Config.fields, an `Owner:` extra metadata
    line is opaque to `unknown-field` — no finding.
    """
    cfg = _config_with_fields(frozenset())
    findings = check_doc(
        Path("/r/sample.md"),
        _doc_with_extra_field("Owner", "alice"),
        Path("/r"),
        cfg,
        stale=None,
        today=_TODAY,
    )
    assert [f.rule for f in findings if f.rule == "unknown-field"] == [], (
        "no allowlist set ⇒ no unknown-field finding"
    )


def test_check_doc_unknown_field_warning_when_allowlist_set():
    """OQ-F shape: `Finding(severity="warning", rule="unknown-field",
    message="metadata field '<Label>:' not in [vocabulary] add_fields
    allowlist", path=<rel>)`. Allowlist = {"Tags"}; doc carries Owner:.
    """
    cfg = _config_with_fields(frozenset({"Tags"}))
    doc_path = Path("/r/sample.md")
    findings = check_doc(
        doc_path,
        _doc_with_extra_field("Owner", "alice"),
        Path("/r"),
        cfg,
        stale=None,
        today=_TODAY,
    )
    unknown = [f for f in findings if f.rule == "unknown-field"]
    assert len(unknown) == 1, f"expected exactly one unknown-field finding, got {findings!r}"
    f = unknown[0]
    assert f.severity == "warning"
    assert f.rule == "unknown-field"
    # OQ-F: pin the exact message + path shape, not just substrings.
    assert f.message == "metadata field 'Owner:' not in [vocabulary] add_fields allowlist", (
        f"unexpected message: {f.message!r}"
    )
    assert f.path == doc_path, f"unexpected path: {f.path!r}"


def test_check_doc_allowed_field_is_clean():
    """OQ-H: `fields={'Owner','Tags'}` + doc carrying both → clean."""
    cfg = _config_with_fields(frozenset({"Owner", "Tags"}))
    text = (
        "# Sample\n\n"
        "Lifecycle: active\nRole: spec\nProject: probe\nUpdated: 2026-05-20\n"
        "Owner: alice\nTags: infra, urgent\n\nBody.\n"
    )
    findings = check_doc(Path("/r/sample.md"), text, Path("/r"), cfg, stale=None, today=_TODAY)
    assert [f.rule for f in findings if f.rule == "unknown-field"] == [], (
        "Owner: + Tags: are both on the allowlist; no unknown-field findings"
    )


def test_check_doc_allowlist_is_case_sensitive():
    """OQ-H: exact-match, case-sensitive — `fields={'owner'}` does NOT
    cover `Owner:`.
    """
    cfg = _config_with_fields(frozenset({"owner"}))
    findings = check_doc(
        Path("/r/sample.md"),
        _doc_with_extra_field("Owner", "alice"),
        Path("/r"),
        cfg,
        stale=None,
        today=_TODAY,
    )
    unknown = [f for f in findings if f.rule == "unknown-field"]
    assert len(unknown) == 1, "case-sensitive match: 'owner' ≠ 'Owner'"
    assert "Owner" in unknown[0].message


def test_check_doc_related_is_never_flagged_by_unknown_field():
    """OQ-O + OQ-P: the built-in always-allowed set
    `{"Lifecycle","Role","Project","Updated","Related","Archived-reason"}`
    must NEVER trip `unknown-field`, regardless of the `add_fields`
    configuration. The classic risk: `Related:` is a required-shape
    bullet container that lives in the metadata block but isn't on
    `add_fields`. An empty allowlist + a `Related:` block must still
    produce zero `unknown-field` findings.
    """
    cfg = _config_with_fields(frozenset({"Tags"}))  # an allowlist that doesn't cover Related
    text = (
        "# Sample\n\nLifecycle: active\nRole: spec\nProject: probe\n"
        "Updated: 2026-05-20\n\nRelated:\n- pairs-with: exists.md\n\nBody.\n"
    )
    # Set up the Related: target so we don't also get a `broken-ref`.
    findings = check_doc(Path("/r/sample.md"), text, Path("/r"), cfg, stale=None, today=_TODAY)
    # Allow any other rule fire (e.g. broken-ref if the file doesn't exist),
    # but Related: itself must not show up as `unknown-field`.
    unknown_related = [f for f in findings if f.rule == "unknown-field" and "Related" in f.message]
    assert unknown_related == [], (
        f"OQ-O: Related: must never trip unknown-field, got {unknown_related!r}"
    )


def test_check_doc_archived_reason_is_never_flagged_by_unknown_field(tmp_path):
    """OQ-O + OQ-P (sibling to the Related: lock): `Archived-reason:` is
    the documented archive-time hint label (see archive.md / convention.md).
    It is part of the built-in always-allowed set — an `add_fields = []`
    allowlist (empty) MUST NOT trip `unknown-field` on it.

    Tests the convention's M4 archive flow: an archived doc carries an
    `Archived-reason:` line and lives under archive/<date>/. The status
    is `archived` and the location is correct (so no status-drift),
    `add_fields=[]` means nothing extra is allowed, yet
    `Archived-reason:` is built-in-permitted.
    """
    cfg = _config_with_fields(frozenset())  # empty allowlist
    doc = tmp_path / "archive" / "2026-01-01" / "retired.md"
    text = (
        "# Retired\n\nLifecycle: archived\nRole: spec\nProject: probe\n"
        "Updated: 2026-01-01\nArchived-reason: superseded by new-spec.md\n\nBody.\n"
    )
    findings = check_doc(doc, text, tmp_path, cfg, stale=None, today=_TODAY)
    unknown_archived_reason = [
        f for f in findings if f.rule == "unknown-field" and "Archived-reason" in f.message
    ]
    assert unknown_archived_reason == [], (
        f"OQ-O: Archived-reason: must never trip unknown-field, got {unknown_archived_reason!r}"
    )


# --- M25 (D1 / D2) — reciprocal relationship integrity --------------------
#
# Phase 2 (written RED). Intended RED reasons, per test:
#
# - `inverse_verb` / `RECIPROCAL_INVERSES` do not exist yet — accessed via
#   `getattr(cli, ...)` so the failure is a clean `AttributeError` at runtime
#   and mypy still sees `Any` (no module-level import of a missing symbol,
#   which would be a collection error).
# - the `missing-inverse` rule does not exist yet — plain assertion RED.
# - `Revision` is not yet in `_BUILTIN_METADATA_FIELDS` — plain assertion RED.
#
# The "no finding" tests are GREEN-at-baseline but DEGENERATE: they pass today
# only because the rule does not exist. They become meaningful after Phase 6
# and are what stops the rule from over-firing.


def _m25(name: str):
    """Fetch an M25 symbol that does not exist yet.

    The indirection is deliberate: a module-level `from docs import
    inverse_verb` would be a COLLECTION error (the Phase-4 exit criterion
    forbids those), and a literal `getattr(_cli, "inverse_verb")` trips
    ruff's B009. Going through a variable keeps the RED reason a single
    clean `AttributeError` and keeps `mypy src/ tests/` green (the result
    is `Any`).
    """
    return getattr(_cli, name)


_TREES = Path(__file__).resolve().parent / "fixtures" / "trees"

_RECIPROCAL_PAIRS = (
    ("precedes", "follows"),
    ("depends-on", "required-by"),
    ("blocks", "blocked-by"),
)


def _pair_root(
    tmp_path: Path,
    *,
    source_edge: str | None,
    target_edge: str | None,
    source_role: str = "notes",
) -> Path:
    """Build a two-doc root (`a.md`, `b.md`) with the given `Related:` edges.

    Inline builder (M25 Phase 3): the mutation-shaped and parametrised cases
    vary one edge at a time, which a committed static tree per case would
    multiply into noise. `source_edge` / `target_edge` are the bullet bodies
    (`"precedes: b.md"`), or None for a doc with no `Related:` group at all.
    Static dates; no stale window is ever passed, so nothing rots.
    """
    root = tmp_path / "pairprobe"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "pairprobe"\n')

    def _doc(title: str, role: str, edge: str | None) -> str:
        text = (
            f"# {title}\n\nLifecycle: active\nRole: {role}\n"
            f"Project: pairprobe\nUpdated: 2026-05-20\n"
        )
        if edge is not None:
            text += f"\nRelated:\n- {edge}\n"
        return text + "\n## Body\n\nProse.\n"

    (root / "a.md").write_text(_doc("A", source_role, source_edge))
    (root / "b.md").write_text(_doc("B", "notes", target_edge))
    return root


def _tree_findings(name: str) -> list[Finding]:
    """Run `check_tree` over a committed fixture tree with its own config.

    The exclusion predicate is compiled from the tree's `.docs.toml` (plus
    any `.docsignore`) exactly as the `docs check` CLI does, so the
    `reciprocal-excluded` fixture exercises the real predicate.
    """
    root = _TREES / name
    config = load_config(root)
    predicate = compile_exclude_predicate(config, [])
    return check_tree(root, config, stale=None, today=_TODAY, predicate=predicate)


def _inverse_findings(name: str) -> list[Finding]:
    return [f for f in _tree_findings(name) if f.rule == "missing-inverse"]


def test_inverse_verb_map_is_symmetric_and_exact():
    """D1: exactly six recognized verbs in three symmetric pairs.

    RED: `inverse_verb` / `RECIPROCAL_INVERSES` land in Phase 5
    (`AttributeError` via getattr).
    """
    inverse_verb = _m25("inverse_verb")
    inverses = _m25("RECIPROCAL_INVERSES")
    verbs = _m25("RECIPROCAL_VERBS")

    assert len(inverses) == 6, f"exactly six recognized verbs, got {sorted(inverses)}"
    assert set(verbs) == set(inverses)

    for forward, reverse in _RECIPROCAL_PAIRS:
        assert inverse_verb(forward) == reverse
        assert inverse_verb(reverse) == forward
        # Symmetric in both directions: applying the map twice is identity.
        assert inverse_verb(inverse_verb(forward)) == forward
        assert inverse_verb(inverse_verb(reverse)) == reverse

    # Free-form verbs are NOT members, and matching is case-sensitive exact.
    assert inverse_verb("pairs-with") is None
    assert inverse_verb("supersedes") is None
    assert inverse_verb("superseded-by") is None
    assert inverse_verb("child-of") is None
    assert inverse_verb("parent-of") is None
    assert inverse_verb("Precedes") is None
    assert inverse_verb("PRECEDES") is None


def test_check_tree_missing_inverse_frozen_message():
    """D2: one error against the SOURCE doc, with the frozen message.

    RED: no `missing-inverse` rule exists yet (plain assertion).
    """
    findings = _inverse_findings("reciprocal-missing")
    assert len(findings) == 1, f"exactly one missing-inverse, got {findings!r}"
    finding = findings[0]
    assert finding.severity == "error"
    assert finding.rule == "missing-inverse"
    assert finding.path == _TREES / "reciprocal-missing" / "a.md", (
        "OQ-B: the finding blames the SOURCE — the doc declaring the un-reciprocated edge"
    )
    assert finding.message == (
        "Related: 'precedes: b.md' has no inverse; "
        "b.md must declare 'follows: a.md' (or remove the edge)"
    )


def test_check_tree_complete_pair_clean():
    """All three pairs complete in both directions → zero findings.

    RED after Phase 6 would mean the rule over-fires; GREEN-at-baseline
    today only because the rule does not exist (degenerate).
    """
    assert _tree_findings("reciprocal-clean") == []


def test_check_tree_reverse_direction_validated(tmp_path):
    """D1 symmetry: a lone `follows:` obliges the target to declare `precedes:`.

    RED: plain assertion (no rule yet).
    """
    root = _pair_root(tmp_path, source_edge="follows: b.md", target_edge=None)
    findings = [
        f
        for f in check_tree(root, load_config(root), stale=None, today=_TODAY)
        if f.rule == "missing-inverse"
    ]
    assert len(findings) == 1, f"expected one missing-inverse, got {findings!r}"
    assert findings[0].message == (
        "Related: 'follows: b.md' has no inverse; "
        "b.md must declare 'precedes: a.md' (or remove the edge)"
    )


@pytest.mark.parametrize(
    "verb,inverse",
    [
        ("precedes", "follows"),
        ("follows", "precedes"),
        ("depends-on", "required-by"),
        ("required-by", "depends-on"),
        ("blocks", "blocked-by"),
        ("blocked-by", "blocks"),
    ],
)
def test_check_tree_all_three_pairs_both_directions(tmp_path, verb, inverse):
    """Every recognized verb, in both directions, is validated identically.

    RED: plain assertion (no rule yet).
    """
    root = _pair_root(tmp_path, source_edge=f"{verb}: b.md", target_edge=None)
    findings = [
        f
        for f in check_tree(root, load_config(root), stale=None, today=_TODAY)
        if f.rule == "missing-inverse"
    ]
    assert len(findings) == 1, f"{verb} must be reciprocity-checked, got {findings!r}"
    assert findings[0].message == (
        f"Related: '{verb}: b.md' has no inverse; "
        f"b.md must declare '{inverse}: a.md' (or remove the edge)"
    )


def test_check_tree_freeform_verbs_never_flagged():
    """THE SUPERSEDES TRAP: verbs that *look* like inverse pairs are not members.

    One-sided `pairs-with`, `child-of`, `supersedes`, `superseded-by`, and
    `references` edges must produce ZERO `missing-inverse` findings.
    GREEN-at-baseline (degenerate); becomes the real over-fire guard after
    Phase 6.
    """
    assert _inverse_findings("reciprocal-freeform") == []


def test_check_tree_broken_target_owns_the_case():
    """Applicability (2): an unresolvable target is `broken-ref`'s case, not ours.

    GREEN-at-baseline (degenerate).
    """
    findings = _tree_findings("reciprocal-broken")
    assert [f.rule for f in findings] == ["broken-ref"], (
        f"broken-ref owns an unresolvable target; got {[(f.rule, f.message) for f in findings]}"
    )


def test_check_tree_excluded_endpoint_no_inverse_finding():
    """Applicability (1): an excluded endpoint yields no inverse finding.

    GREEN-at-baseline (degenerate).
    """
    findings = _tree_findings("reciprocal-excluded")
    assert findings == [], f"excluded endpoint must not produce a finding, got {findings!r}"


def test_check_tree_malformed_endpoint_no_inverse_finding():
    """Applicability (4): a target with no H1 is `malformed`'s case, not ours.

    GREEN-at-baseline (degenerate).
    """
    findings = _tree_findings("reciprocal-malformed")
    assert [f.rule for f in findings] == ["malformed"], (
        f"malformed owns an unparseable endpoint; got {[(f.rule, f.message) for f in findings]}"
    )


def test_check_tree_non_markdown_target_no_inverse_finding():
    """Applicability (3): `depends-on: data.yaml` (a real, non-`.md` file) is fine.

    The convention deliberately allows non-Markdown `Related:` targets.
    GREEN-at-baseline (degenerate).
    """
    findings = _tree_findings("reciprocal-nonmd")
    assert findings == [], f"non-Markdown target must not be reciprocity-checked, got {findings!r}"


def test_check_tree_source_with_bad_vocab_still_reciprocity_checked(tmp_path):
    """Applicability (4) is about PARSEABILITY ONLY.

    A source that also trips `bad-vocab` still gets its reciprocity checked —
    the two rules are independent. RED: plain assertion (no rule yet).
    """
    root = _pair_root(
        tmp_path,
        source_edge="precedes: b.md",
        target_edge=None,
        source_role="not-a-real-role",
    )
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    rules = sorted(f.rule for f in findings)
    assert rules == ["bad-vocab", "missing-inverse"], (
        f"a bad-vocab source is still reciprocity-checked; got {rules}"
    )


def test_check_tree_archived_endpoint_is_in_scope():
    """Archived docs are walked, so they are reciprocity-checked too.

    This is exactly why `docs relate`'s audited archive exception (D4)
    exists. RED: plain assertion (no rule yet).
    """
    findings = _inverse_findings("reciprocal-archived-missing")
    assert len(findings) == 1, f"expected one missing-inverse, got {findings!r}"
    assert findings[0].message == (
        "Related: 'depends-on: archive/2026-01-01/old.md' has no inverse; "
        "archive/2026-01-01/old.md must declare 'required-by: a.md' (or remove the edge)"
    )


def test_check_tree_archived_pair_complete_is_clean():
    """The same active↔archived pair, reciprocated, is clean.

    GREEN-at-baseline (degenerate).
    """
    assert _tree_findings("reciprocal-archived-complete") == []


def test_check_tree_duplicate_edge_single_finding(tmp_path):
    """D2 dedupe: one finding per distinct (source, verb, target) triple.

    RED: plain assertion (no rule yet).
    """
    root = _pair_root(
        tmp_path,
        source_edge="precedes: b.md\n- precedes: b.md",
        target_edge=None,
    )
    findings = [
        f
        for f in check_tree(root, load_config(root), stale=None, today=_TODAY)
        if f.rule == "missing-inverse"
    ]
    assert len(findings) == 1, f"a duplicated bullet yields ONE finding, got {findings!r}"


def test_check_tree_findings_grouped_by_path(tmp_path):
    """Per-doc findings stay contiguous, in root-relative path order.

    `missing-inverse` is interleaved into `check_tree`'s existing per-doc
    grouping — it must not be appended as a separate tail block.
    RED: plain assertion (no rule yet).
    """
    root = _pair_root(
        tmp_path,
        source_edge="precedes: b.md",
        target_edge=None,
        source_role="not-a-real-role",
    )
    # A third doc, alphabetically last, with its own unrelated error.
    (root / "c.md").write_text("no h1 here\n")

    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    names = [f.path.name for f in findings]
    assert names == sorted(names), f"findings must be in root-relative path order, got {names}"
    # a.md's two findings are contiguous, then c.md's.
    assert names == ["a.md", "a.md", "c.md"], names
    # Intra-doc ORDER is pinned too: `check_doc`'s findings first, then any
    # `missing-inverse` (cli.md / the milestone's Decisions — `check_tree`
    # interleaves rather than appending a separate tail block).
    assert [f.rule for f in findings] == ["bad-vocab", "missing-inverse", "malformed"]


def test_exit_code_for_missing_inverse_is_2():
    """D2: `missing-inverse` is an error, so the tree exits 2.

    RED: plain assertion (no rule yet).
    """
    findings = _tree_findings("reciprocal-missing")
    assert exit_code_for(findings) == 2


def test_check_doc_revision_field_never_flagged_by_unknown_field(tmp_path):
    """`Revision:` is a built-in always-allowed label (M25 — D4).

    Sibling of the `Related:` / `Archived-reason:` locks. `docs relate`
    WRITES this label onto archived endpoints, so a tree with an
    `add_fields` allowlist must never see `unknown-field` on it.

    RED: `_BUILTIN_METADATA_FIELDS` gains `"Revision"` in Phase 5.
    """
    cfg = _config_with_fields(frozenset({"Owner"}))  # an allowlist that omits Revision
    doc = tmp_path / "archive" / "2026-01-01" / "retired.md"
    text = (
        "# Retired\n\nLifecycle: archived\nRole: spec\nProject: probe\n"
        "Updated: 2026-01-01\nArchived-reason: superseded\n\n"
        "Revision:\n- 2026-08-11: relate add 'required-by: a.md'; reason: complete the pair\n\n"
        "Body.\n"
    )
    findings = check_doc(doc, text, tmp_path, cfg, stale=None, today=_TODAY)
    offenders = [f for f in findings if f.rule == "unknown-field" and "Revision" in f.message]
    assert offenders == [], f"Revision: must never trip unknown-field, got {offenders!r}"


def _legacy_tree_names() -> list[str]:
    """Every committed fixture tree that is NOT one of M25's own.

    Deriving the list from the directory (rather than hard-coding four
    names) means a fixture tree added later is covered for free — and if
    someone adds a recognized verb to one, this lock catches it.
    """
    return sorted(
        d.name for d in _TREES.iterdir() if d.is_dir() and not d.name.startswith("reciprocal-")
    )


@pytest.mark.parametrize("tree", _legacy_tree_names())
def test_check_tree_legacy_fixtures_gain_no_new_findings(fixtures_dir, tree):
    """No pre-M25 fixture tree may gain a `missing-inverse` finding.

    None of them uses a recognized verb, so the new rule must be silent on
    every one. GREEN-at-baseline (degenerate), and a genuine regression lock
    after Phase 6 — including for fixture trees added by later milestones.
    """
    root = fixtures_dir / "trees" / tree
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    assert [f for f in findings if f.rule == "missing-inverse"] == [], (
        f"legacy fixture {tree} must gain no missing-inverse findings"
    )


def test_check_tree_inverse_pointing_elsewhere_is_still_missing(tmp_path):
    """The inverse must point BACK AT THE SOURCE — not merely exist.

    `b.md` declares the right verb (`follows`) at the wrong target (`c.md`).
    An implementation that only asks "does the target declare `follows` at
    all?" would pass every other test in this file while silently
    under-reporting real one-sided edges. `c.md` reciprocates `b.md`, so the
    b↔c pair is complete and the ONE expected finding is isolated.

    RED: plain assertion (no rule yet).
    """
    root = _pair_root(tmp_path, source_edge="precedes: b.md", target_edge="follows: c.md")
    (root / "c.md").write_text(
        "# C\n\nLifecycle: active\nRole: notes\nProject: pairprobe\n"
        "Updated: 2026-05-20\n\nRelated:\n- precedes: b.md\n\n## Body\n\nProse.\n"
    )
    findings = [
        f
        for f in check_tree(root, load_config(root), stale=None, today=_TODAY)
        if f.rule == "missing-inverse"
    ]
    assert len(findings) == 1, f"expected exactly one missing-inverse, got {findings!r}"
    assert findings[0].path == root / "a.md"
    assert findings[0].message == (
        "Related: 'precedes: b.md' has no inverse; "
        "b.md must declare 'follows: a.md' (or remove the edge)"
    )


def test_check_tree_self_edge_is_exempt():
    """Amendment A: a recognized edge to the declaring doc is EXEMPT.

    `docs relate` refuses a self-edge (`SOURCE and TARGET must be different
    documents`), so a finding here would name a repair the repair verb
    declines to perform. GREEN-at-baseline (degenerate); a genuine
    over-fire guard after Phase 6.
    """
    assert _tree_findings("reciprocal-self-edge") == []


def test_check_tree_non_canonical_target_path_still_reciprocal(tmp_path):
    """Amendment B: `precedes: ./b.md` is the same edge as `precedes: b.md`.

    Paths are compared canonically, not textually — a hard check must not
    fail over a `./` prefix. GREEN-at-baseline (degenerate).
    """
    root = _pair_root(tmp_path, source_edge="precedes: ./b.md", target_edge="follows: a.md")
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    assert findings == [], f"a `./` prefix must not break reciprocity, got {findings!r}"


def test_check_tree_non_canonical_inverse_path_still_reciprocal(tmp_path):
    """Amendment B, converse: the INVERSE bullet may be spelled loosely too."""
    root = _pair_root(tmp_path, source_edge="precedes: b.md", target_edge="follows: ./a.md")
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    assert findings == [], f"a `./` prefix on the inverse must still count, got {findings!r}"


def test_check_tree_dotdot_target_path_still_reciprocal(tmp_path):
    """Amendment B: a `sub/..`-style detour normalizes to the same edge."""
    root = _pair_root(tmp_path, source_edge="precedes: sub/../b.md", target_edge="follows: a.md")
    (root / "sub").mkdir()
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    assert findings == [], f"`sub/../b.md` is `b.md`, got {findings!r}"


def test_check_tree_no_conflict_detection(tmp_path):
    """The "no conflict detection" statement, locked.

    `a.md` declares BOTH `precedes: b.md` and `follows: b.md`; `b.md`
    reciprocates both. Contradictory as sequencing, but every recognized
    edge has its exact inverse, so the tree is clean. A naive per-doc
    implementation that treats a verb and its inverse as mutually exclusive
    would over-fire here. GREEN-at-baseline (degenerate).
    """
    root = _pair_root(
        tmp_path,
        source_edge="precedes: b.md\n- follows: b.md",
        target_edge="follows: a.md\n- precedes: a.md",
    )
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    assert findings == [], f"conflicting-but-reciprocated edges are clean, got {findings!r}"


# --- M25 (D7) — duplicate metadata labels ----------------------------------
#
# Written RED first, as a self-contained mini-cycle inside Phase 10 (operator
# decision 2026-08-12, in response to a fresh-eyes review finding). The rule
# is per-doc, so it lives in `check_doc`, NOT in `reciprocity_findings`.


def _dup(*metadata_lines: str) -> str:
    """A doc whose metadata block is exactly `metadata_lines`."""
    body = "\n".join(metadata_lines)
    return f"# Sample\n\n{body}\n\n## Body\n\nProse.\n"


def test_check_doc_duplicate_bare_label_group_is_an_error():
    """Two `Related:` labels: the parser keeps only the last — silent data loss.

    RED until D7 lands. This is the defect a fresh-eyes review surfaced:
    `parse_metadata_block` assigns `metadata[label] = tuple(values)`, so the
    second label REPLACES the first and every bullet under the earlier one
    is discarded before any rule, the INDEX renderer, or `Related:`
    resolution ever sees it.
    """
    text = _dup(
        "Lifecycle: active",
        "Role: spec",
        "Project: probe",
        "Updated: 2026-05-20",
        "",
        "Related:",
        "- precedes: b.md",
        "",
        "Related:",
        "- references: b.md",
    )
    findings = check_doc(
        Path("/r/sample.md"), text, Path("/r"), _config(), stale=None, today=_TODAY
    )
    dups = [f for f in findings if f.rule == "duplicate-field"]
    assert len(dups) == 1, f"exactly one duplicate-field finding, got {findings!r}"
    assert dups[0].severity == "error"
    assert dups[0].path == Path("/r/sample.md")
    assert dups[0].message == (
        "metadata field 'Related:' appears 2 times; only the last occurrence is read"
    )


def test_check_doc_duplicate_scalar_field_is_an_error():
    """A repeated INLINE label is the same defect — `Updated:` twice."""
    text = _dup(
        "Lifecycle: active",
        "Role: spec",
        "Project: probe",
        "Updated: 2026-05-20",
        "Updated: 2026-05-21",
    )
    findings = check_doc(
        Path("/r/sample.md"), text, Path("/r"), _config(), stale=None, today=_TODAY
    )
    dups = [f for f in findings if f.rule == "duplicate-field"]
    assert len(dups) == 1, f"expected one duplicate-field, got {findings!r}"
    assert dups[0].message == (
        "metadata field 'Updated:' appears 2 times; only the last occurrence is read"
    )


def test_check_doc_duplicate_one_bare_and_one_inline_yields_two_findings():
    """One finding PER repeated label, in metadata-block order."""
    text = _dup(
        "Lifecycle: active",
        "Role: spec",
        "Project: probe",
        "Updated: 2026-05-20",
        "Updated: 2026-05-21",
        "",
        "Related:",
        "- precedes: b.md",
        "",
        "Related:",
        "- references: b.md",
    )
    findings = check_doc(
        Path("/r/sample.md"), text, Path("/r"), _config(), stale=None, today=_TODAY
    )
    dups = [f for f in findings if f.rule == "duplicate-field"]
    assert [f.message for f in dups] == [
        "metadata field 'Updated:' appears 2 times; only the last occurrence is read",
        "metadata field 'Related:' appears 2 times; only the last occurrence is read",
    ]


def test_check_doc_thrice_repeated_label_is_still_one_finding():
    """One finding per repeated LABEL, not per extra occurrence."""
    text = _dup(
        "Lifecycle: active",
        "Role: spec",
        "Project: probe",
        "Updated: 2026-05-20",
        "Owner: a",
        "Owner: b",
        "Owner: c",
    )
    findings = check_doc(
        Path("/r/sample.md"), text, Path("/r"), _config(), stale=None, today=_TODAY
    )
    dups = [f for f in findings if f.rule == "duplicate-field"]
    assert len(dups) == 1, f"one finding per repeated label, got {[f.message for f in dups]}"
    assert dups[0].message == (
        "metadata field 'Owner:' appears 3 times; only the last occurrence is read"
    )


def test_check_doc_many_bullets_under_one_label_never_fires():
    """THE NEGATIVE CASE: repeatability lives in the bullets, not the label.

    A long `Related:` run plus a `Revision:` run — the exact shape `docs
    relate` writes — must never produce a `duplicate-field` finding. A rule
    that counted bullets rather than labels would fire on every real doc in
    the tree.
    """
    text = _dup(
        "Lifecycle: archived",
        "Role: plan",
        "Project: probe",
        "Updated: 2026-05-20",
        "Archived-reason: completed",
        "",
        "Related:",
        "- precedes: b.md",
        "- follows: c.md",
        "- references: d.md",
        "- pairs-with: e.md",
        "",
        "Revision:",
        "- 2026-08-11: relate add 'precedes: b.md'; reason: one",
        "- 2026-08-12: relate remove 'follows: c.md'; reason: two",
    )
    findings = check_doc(
        Path("/r/sample.md"), text, Path("/r"), _config(), stale=None, today=_TODAY
    )
    assert [f for f in findings if f.rule == "duplicate-field"] == [], (
        "many bullets under ONE label is the convention, not a duplicate"
    )


def test_check_doc_clean_doc_has_no_duplicate_field_finding():
    findings = check_doc(
        Path("/r/sample.md"), _valid(), Path("/r"), _config(), stale=None, today=_TODAY
    )
    assert [f for f in findings if f.rule == "duplicate-field"] == []


def test_check_tree_duplicate_field_fixture_is_an_error():
    """The committed tree: exit 2, one finding, against the offending doc."""
    findings = _tree_findings("duplicate-field")
    dups = [f for f in findings if f.rule == "duplicate-field"]
    assert len(dups) == 1, f"expected one duplicate-field, got {findings!r}"
    assert dups[0].path == _TREES / "duplicate-field" / "a.md"
    assert exit_code_for(findings) == 2


def test_check_tree_duplicate_field_diagnoses_the_unfixable_missing_inverse(tmp_path):
    """Why the rule exists (M25 — D7) — the exact shape the review found.

    `a.md`'s FIRST `Related:` label is free-form and its LAST declares the
    un-reciprocated `precedes: b.md`. The parser is **last-wins**, so
    `missing-inverse` fires; the editors are **find-first**, so
    `remove_related_edge` inspects the first label, finds nothing, and
    reports "already absent" — the repair the finding names claims success
    (exit 0) while the finding survives.

    Kept inline rather than committed: the `duplicate-field/` tree isolates
    ONE semantic, and a committed tree emitting `missing-inverse` would also
    trip `test_check_tree_legacy_fixtures_gain_no_new_findings`.
    """
    root = tmp_path / "unfixable"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "unfixable"\n')
    (root / "a.md").write_text(
        "# A\n\nLifecycle: active\nRole: notes\nProject: unfixable\n"
        "Updated: 2026-05-20\n\nRelated:\n- references: b.md\n\n"
        "Related:\n- precedes: b.md\n\n## Body\n\nProse.\n"
    )
    (root / "b.md").write_text(
        "# B\n\nLifecycle: active\nRole: notes\nProject: unfixable\n"
        "Updated: 2026-05-20\n\n## Body\n\nProse.\n"
    )

    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    rules = sorted(f.rule for f in findings)
    assert rules == ["duplicate-field", "missing-inverse"], (
        "the unfixable finding now travels with the duplicate that causes it"
    )
    assert exit_code_for(findings) == 2

    # The repair `missing-inverse` names is a no-op here: the editor reads
    # the FIRST label, which does not carry the edge.
    _out, changed = _cli.remove_related_edge((root / "a.md").read_text(), "precedes", "b.md")
    assert changed is False, "find-first editor vs last-wins parser — this is why D7 must fire too"


# --- M27 (D4 / D4b) — Markdown body-link validation ------------------------
#
# Phase 2 (written RED). Intended RED reasons, per test:
#
# - the `broken-body-link` and `outside-root-body-link` rules do not exist
#   yet, so `check_doc` returns no body-link finding and `check_tree` returns
#   `[]` for `bodylink-broken` — plain assertion RED.
#
# The "no finding" tests are GREEN-at-baseline but DEGENERATE: they pass today
# only because the rules do not exist. They become meaningful after Phase 6 and
# are what stops the rules over-firing. Each says so in its own docstring.
#
# The pure scanner seam (`scan_body_links`, `_mask_code`,
# `classify_destination`, `normalise_body_link_target`, `body_link_findings`)
# is exercised in `tests/test_body_links.py`; this section owns the rule as
# `check_doc` / `check_tree` expose it.


def _bodylink_findings(name: str) -> list[Finding]:
    """`check_tree` over a committed `bodylink-*` tree, proving it EXISTS first.

    The existence guard is load-bearing, not decoration. `load_config`
    tolerates a missing directory and the walk then yields nothing, so the
    three "silent" locks below would pass on a fixture tree that was never
    written — exactly the falsely-GREEN shape the Phase-2 authoring rules
    exist to prevent. Between Phase 2 and Phase 3 this assertion is what makes
    them honestly RED.
    """
    assert (_TREES / name).is_dir(), f"missing fixture tree {name!r} (Phase 3 supplies it)"
    return _tree_findings(name)


def _body_link_findings_of(name: str) -> list[Finding]:
    return [
        f
        for f in _bodylink_findings(name)
        if f.rule in {"broken-body-link", "outside-root-body-link"}
    ]


def _bodylink_doc(project: str, body: str, *, lifecycle: str = "active") -> str:
    """A well-formed doc whose only interesting content is its body prose."""
    return (
        f"# Doc\n\nLifecycle: {lifecycle}\nRole: notes\nProject: {project}\n"
        f"Updated: 2026-05-20\n\n{body}"
    )


def test_check_doc_broken_body_link_is_an_error(tmp_path):
    """D4: a local body link naming no existing path is a hard error.

    RED: plain assertion (no rule yet — the body is opaque, E3).
    """
    text = _bodylink_doc("probe", "See [the plan](plan.md) for context.\n")
    findings = check_doc(tmp_path / "doc.md", text, tmp_path, _config(), stale=None, today=_TODAY)
    body_links = [f for f in findings if f.rule == "broken-body-link"]
    assert len(body_links) == 1, f"expected exactly one broken-body-link, got {findings!r}"
    assert body_links[0].severity == "error"
    assert body_links[0].path == tmp_path / "doc.md"
    assert body_links[0].message == (
        "body link at line 8 does not resolve to an existing path: plan.md (resolves to plan.md)"
    )


def test_check_doc_outside_root_body_link_is_an_error(tmp_path):
    """D4b: a destination that leaves the root is its own hard error.

    RED: plain assertion (no rule yet).
    """
    text = _bodylink_doc("probe", "See [the glossary](../shared/glossary.md).\n")
    findings = check_doc(tmp_path / "doc.md", text, tmp_path, _config(), stale=None, today=_TODAY)
    escapes = [f for f in findings if f.rule == "outside-root-body-link"]
    assert len(escapes) == 1, f"expected exactly one outside-root-body-link, got {findings!r}"
    assert escapes[0].severity == "error"
    assert escapes[0].message == (
        "body link at line 8 leaves the docs root: ../shared/glossary.md "
        "(normalises to ../shared/glossary.md); links outside the tree must be URLs"
    )


def test_check_doc_body_link_findings_follow_the_broken_ref_group(tmp_path):
    """D4 ordering: body-link findings are emitted immediately AFTER the
    `broken-ref` group and before the `stale` block, keeping the two
    reference-resolution rules adjacent.

    The doc carries both, so the relative order is observable rather than
    vacuous.

    RED: plain assertion (no rule yet).
    """
    text = (
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: probe\nUpdated: 2026-05-20\n\n"
        "Related:\n- references: nowhere.md\n\n"
        "See [the plan](plan.md).\n"
    )
    findings = check_doc(tmp_path / "doc.md", text, tmp_path, _config(), stale=None, today=_TODAY)
    assert [f.rule for f in findings] == ["broken-ref", "broken-body-link"]


def test_check_doc_malformed_doc_gets_no_body_link_findings(tmp_path):
    """A `malformed` doc keeps sole ownership of its case (D4).

    `check_doc`'s existing early return on a missing H1 stands, so a doc with
    no H1 gets its `malformed` finding and no body-link pile-on — mirroring
    how `reciprocity_findings` skips unparseable docs.

    GREEN-at-baseline but DEGENERATE: passes today only because the rules do
    not exist. Genuine once the early return is load-bearing.
    """
    text = "No H1 here.\n\nSee [the plan](plan.md).\n"
    findings = check_doc(tmp_path / "doc.md", text, tmp_path, _config(), stale=None, today=_TODAY)
    assert [f.rule for f in findings] == ["malformed"]


def test_check_tree_bodylink_broken_is_exactly_one_error():
    """E3 at the tree level: the `bodylink-broken` fixture's single unresolved
    inline link is one `broken-body-link` and nothing else.

    RED: plain assertion (the tree exits 0 today).
    """
    findings = _bodylink_findings("bodylink-broken")
    assert [f.rule for f in findings] == ["broken-body-link"]
    assert findings[0].path.name == "doc.md"
    assert "plan.md" in findings[0].message


def test_exit_code_for_broken_body_link_is_2():
    """D4: `broken-body-link` is an error, so the tree exits 2.

    RED: plain assertion (no rule yet).
    """
    assert exit_code_for(_bodylink_findings("bodylink-broken")) == 2


def test_check_tree_bodylink_archived_reproduces_the_unrebased_shape():
    """E1/E2: the un-rebased archive move, which is 132 of this repository's
    139 breaks — a relative link that was correct at the document's original
    location and that no version of the tool has ever rebased.

    RED: plain assertion (the tree exits 0 today).
    """
    findings = _body_link_findings_of("bodylink-archived")
    assert len(findings) == 1, f"expected exactly one finding, got {findings!r}"
    assert findings[0].rule == "broken-body-link"
    assert findings[0].path.name == "old-log.md"
    assert "(resolves to archive/2026-01-01/plan.md)" in findings[0].message, (
        "the message must name the candidate the destination normalises to, "
        "which is what makes the ../../ rebase obvious"
    )


def test_check_tree_bodylink_archived_repaired_copy_is_clean(tmp_path):
    """D6: the documented repair recipe works, and touches nothing else.

    A copy of the damaged tree gets a DESTINATION-TOKEN-ONLY rewrite — the
    `../../` rebase the archive move should have applied — and every other
    byte in the tree stays identical. That second half is the point: the D6
    migration's blast radius is destination tokens, `Updated:`, and one
    `Revision:` bullet, and this proves the recipe an adopter is handed does
    not need to touch prose.

    GREEN-at-baseline but DEGENERATE: no rule exists yet, so both the damaged
    and the repaired tree are silent today. It becomes the proof that the
    recipe works from Phase 6.
    """
    src = _TREES / "bodylink-archived"
    dst = tmp_path / "repaired"
    shutil.copytree(src, dst)

    doc = dst / "archive" / "2026-01-01" / "old-log.md"
    before = doc.read_text()
    after = before.replace("](plan.md)", "](../../plan.md)")
    assert after != before, "the fixture must carry the un-rebased destination"
    doc.write_text(after)

    findings = check_tree(dst, load_config(dst), stale=None, today=_TODAY)
    assert [
        f for f in findings if f.rule in {"broken-body-link", "outside-root-body-link"}
    ] == [], f"the repaired copy must be clean, got {findings!r}"

    # Every other byte in the tree is untouched — only the destination token moved.
    for path in sorted(p for p in src.rglob("*") if p.is_file()):
        rel = path.relative_to(src)
        mirror = (dst / rel).read_bytes()
        if rel.as_posix() == "archive/2026-01-01/old-log.md":
            assert mirror == after.encode()
            assert mirror.replace(b"](../../plan.md)", b"](plan.md)") == path.read_bytes()
        else:
            assert mirror == path.read_bytes(), f"{rel} must be byte-identical"


def test_check_tree_bodylink_outside_root_reports_only_the_containment_rule():
    """E7/D4b: an escaping destination yields `outside-root-body-link` ONLY.

    Never additionally `broken-body-link` — deciding brokenness would require
    precisely the stat the boundary forbids.

    RED: plain assertion (the tree exits 0 today).
    """
    findings = _bodylink_findings("bodylink-outside-root")
    assert [f.rule for f in findings] == ["outside-root-body-link"] * 2
    assert [f.severity for f in findings] == ["error"] * 2
    assert exit_code_for(findings) == 2


def test_check_tree_bodylink_outside_root_reports_a_target_that_does_exist():
    """E7: "whether or not it would have resolved".

    One of the fixture's two escaping destinations is self-referential —
    `../bodylink-outside-root/doc.md` — so it is GUARANTEED to exist on disk,
    and the other names a directory that cannot exist. Both are reported the
    same way, which is what proves the rule is decided by path arithmetic and
    not by a stat that happened to fail.

    RED: plain assertion (the tree exits 0 today).
    """
    findings = _bodylink_findings("bodylink-outside-root")
    messages = [f.message for f in findings]
    assert any("bodylink-outside-root/doc.md" in m for m in messages), (
        "the escaping destination that DOES exist must still be reported"
    )
    assert all(f.rule == "outside-root-body-link" for f in findings)
    assert (_TREES / "bodylink-outside-root" / "doc.md").is_file(), (
        "the self-referential escape only proves E7 while its target really exists"
    )


def test_check_tree_indented_link_in_a_blockquote_is_scanned(tmp_path):
    """E6/Q3: a real link indented four spaces inside a blockquote / list
    continuation IS scanned — the scanner buys no false negatives to avoid
    false positives.

    All nine 4-space-indented link-shaped spans in this repository are real
    links, six of them among the 139 genuine breaks, so an indented-code rule
    would hide live damage.

    RED: plain assertion (no rule yet).
    """
    root = tmp_path / "indented"
    root.mkdir()
    (root / ".docs.toml").write_text('[project]\nname = "indented"\n')
    (root / "doc.md").write_text(
        _bodylink_doc(
            "indented",
            "> A quoted paragraph:\n>\n    See [the plan](plan.md) for context.\n",
        )
    )
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    assert [f.rule for f in findings] == ["broken-body-link"]


def test_check_tree_bodylink_clean_is_clean():
    """Every supported form, resolving: plain, `./`, fragment, non-Markdown,
    directory, angle, all three title quotings, and a reference definition.

    GREEN-at-baseline but DEGENERATE (passes today only because the rules do
    not exist); the over-fire guard from Phase 6.
    """
    assert _bodylink_findings("bodylink-clean") == []


def test_check_tree_bodylink_excluded_forms_is_silent():
    """E5/E8/D2: every excluded form produces NOTHING.

    Image, autolink, raw HTML, fenced code, inline code, fragment-only,
    schemed, protocol-relative, root-absolute, all three reference USES, and
    a backslash-escaped opt-out — on a doc that is otherwise valid, so the
    silence cannot come from `check_doc`'s malformed early return.

    GREEN-at-baseline but DEGENERATE; the over-fire guard from Phase 6.
    """
    assert _bodylink_findings("bodylink-excluded-forms") == []


def test_check_tree_bodylink_nested_resolves_up_and_down():
    """D3: resolution is relative to the REFERRING document, so a nested doc
    links up with `../` and back down again — including
    `../sub/../back-inside.md`, which normalises back under the root and is
    validated normally.

    GREEN-at-baseline but DEGENERATE; the over-fire guard from Phase 6.
    """
    assert _bodylink_findings("bodylink-nested") == []


def _pre_m27_tree_names() -> list[str]:
    """Every committed fixture tree that is NOT one of M27's own.

    A SIBLING of `_legacy_tree_names`, not a replacement (Phase-1 amendment
    3). That list excludes `reciprocal-*`, so it covers 23 trees rather than
    the 33 the milestone's Phase-3 exit criterion names — and extending its
    assertion to the two new rules would additionally make M27's three
    deliberately damaged `bodylink-*` trees fail it. Adding a sibling delivers
    the stated coverage AND leaves every pre-existing test id in place.
    """
    return sorted(
        d.name for d in _TREES.iterdir() if d.is_dir() and not d.name.startswith("bodylink-")
    )


@pytest.mark.parametrize("tree", _pre_m27_tree_names())
def test_check_tree_pre_m27_fixtures_gain_no_body_link_findings(fixtures_dir, tree):
    """No pre-M27 fixture tree may gain either M27 finding.

    The setup census measured all 33 read-only: zero unresolved local
    destinations and zero escapes in every one of them, so both rules must be
    silent across the whole set. GREEN-at-baseline (degenerate), and a genuine
    regression lock after Phase 6 — including for trees added by later
    milestones.
    """
    root = fixtures_dir / "trees" / tree
    findings = check_tree(root, load_config(root), stale=None, today=_TODAY)
    offenders = [f for f in findings if f.rule in {"broken-body-link", "outside-root-body-link"}]
    assert offenders == [], f"pre-M27 fixture {tree} must gain no body-link findings"
