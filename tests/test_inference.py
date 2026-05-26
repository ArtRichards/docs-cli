"""F1 / F10 / F12 — broadened role inference (Phase 2, RED).

Today `infer_role` matches a small fixed set of `-{spec,plan,adr,…}` suffix
tokens; 73% of real-world files fall through to the `notes` low-confidence
catch-all. The 2026-05-24 multi-tree trial (501 .md files across 25 trees)
surfaced the broader inference signals the convention needs:

- F1  H1-content / section-header / sibling-set / word-boundary signals.
- F10 7 new core vocab roles + `_Draft` / `_Ready` / `_v\\d+` non-role
      suffix stripping.
- F12 `_M\\d+` milestone-suffix pattern.

The introduction of a third confidence level `medium` (OQ-D, 2026-05-24) backs
the new signals: word-boundary and new-vocab matches stay `high`; H1, section,
sibling, and post-strip matches return `medium`.

Per OQ-5 (operator decision 2026-05-24): the H1 / section-header / sibling
tests drive `plan_migration` end-to-end rather than calling `infer_role`
directly — these signals materialise only inside the plan layer (the
function-level `infer_role(filename, metadata)` has no in-tree text or
sibling-set surface). Word-boundary, non-role-suffix-strip, new-vocab, and
`_M\\d+` tests do call `infer_role` directly because they only depend on the
filename.

Confidence assertions use the forward-compatible form
`confidence in ("medium", "high", True)` so the test reads the right shape
once Phase 5 lands the third level. Today's two-level (`high`/`low`) world
makes these RED for the intended reason: the signal isn't picked up, so the
file lands in `notes`/`low` rather than the asserted role/medium.
"""

from __future__ import annotations

import pytest

from docs import Confidence, infer_role, plan_migration

# M10 (OQ-E): `infer_role` returns a `Confidence` enum member.
# `_CONFIDENCE_OK` is the {HIGH, MEDIUM} positive set — tests that pin
# strict-medium use `is Confidence.MEDIUM` directly.
_CONFIDENCE_OK = (Confidence.HIGH, Confidence.MEDIUM)


def _write(path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


# --- Word-boundary tolerance (F1) ------------------------------------------


def test_infer_role_word_boundary_space_separated():
    """A TitleCase filename whose final whitespace-separated token is a role
    (`Project Name - Database Population Plan.md`) infers `role: plan` —
    today the splitter only splits on `-` / `_`, so the trailing word is
    `Plan` (capitalised, no leading separator) and inference falls back to
    `notes`.
    """
    role, conf = infer_role("Project Name - Database Population Plan.md", {})
    assert role == "plan"
    assert conf in _CONFIDENCE_OK


# --- Non-role suffix stripping (F10) ---------------------------------------


@pytest.mark.parametrize(
    "filename,strict_medium",
    [
        # First case is the strict-medium anchor (review finding #1): the
        # post-strip match must be specifically `medium`, not "any of medium/
        # high/True". A Phase 6 implementation that returns "high" for every
        # strip would silently degrade OQ-D's three-confidence-level resolution.
        ("MyPlan_v2.md", True),
        ("MyPlan_Draft.md", False),
        ("MyPlan_v3.md", False),
    ],
)
def test_infer_role_strips_non_role_suffixes(filename, strict_medium):
    """`_v\\d+`, `_Draft`, `_Ready` are non-role signals: strip them and
    re-match the remaining stem. After stripping, `_Plan` matches → role
    `plan` at medium confidence. Today the matcher sees the full stem and
    falls back to `notes`.

    The first parametric case (`MyPlan_v2.md`) asserts confidence ==
    `"medium"` exactly, pinning OQ-D's three-level resolution against an
    accidental Phase-6 implementation that always returns `"high"`.
    """
    role, conf = infer_role(filename, {})
    assert role == "plan", f"stripping failed for {filename}: got {role!r}"
    if strict_medium:
        assert conf is Confidence.MEDIUM, (
            f"non-role-suffix strip must return medium confidence (OQ-D); "
            f"got {conf!r} for {filename}"
        )
    else:
        assert conf in _CONFIDENCE_OK


# --- New core vocab roles (F10) --------------------------------------------


@pytest.mark.parametrize(
    "filename,expected_role",
    [
        ("MyDoc_Implementation.md", "implementation"),
        ("MyDoc_Sketch.md", "sketch"),
        ("MyDoc_Outline.md", "outline"),
        ("MyDoc_Memo.md", "memo"),
        ("MyDoc_Brief.md", "brief"),
        ("MyDoc_Template.md", "template"),
        ("MyDoc_Example.md", "example"),
    ],
)
def test_infer_role_new_core_vocab_roles(filename, expected_role):
    """The 7 new core controlled-role vocab additions (OQ-A) — case-insensitive
    suffix match in `_TitleCase` shape. Today none of these are roles, so
    every case lands in `notes`.

    OQ-A puts these in the CORE controlled-role vocab — direct suffix match
    yields **high** confidence (same as today's pre-existing `_Plan` / `_Spec`
    matchers). `medium` is reserved for derived signals (post-strip,
    H1-content, section-header, sibling-set defaulting). This assertion drops
    `medium` from the accepted set so a Phase 6 implementation can't quietly
    degrade these to medium confidence (review finding #2).
    """
    role, conf = infer_role(filename, {})
    assert role == expected_role, f"{filename}: expected {expected_role}, got {role!r}"
    assert conf is Confidence.HIGH, (
        f"new core vocab roles are direct suffix matches → high confidence (OQ-A); "
        f"got {conf!r} for {filename}"
    )


# --- F12 — milestone-number suffix pattern ---------------------------------


@pytest.mark.parametrize(
    "filename",
    # `Foo_M1.md`, `Foo_M2.md`, `Foo_M10.md` come straight from the milestone
    # task plan (line 530). `Foo_M01.md` is an intentional regex-coverage
    # addition (review finding #3): the `_M\d+` pattern must accept leading
    # zeros so a tree that names its milestones `_M01.._M09` still matches.
    # Trial 2 did not surface this shape; pinning it here keeps the pattern
    # forward-compatible without requiring a separate test.
    ["Foo_M1.md", "Foo_M2.md", "Foo_M10.md", "Foo_M01.md"],
)
def test_infer_role_milestone_number_suffix(filename):
    """Filenames ending with `_M\\d+` are milestone-task-plan docs (Trial 2
    surfaced 12+ such files). Phase 5/6 maps the pattern to `role:
    milestone` at medium confidence. Today the bare `_M1` token is not a
    role; inference falls to `notes`.
    """
    role, conf = infer_role(filename, {})
    assert role == "milestone", f"{filename}: got {role!r}"
    assert conf in _CONFIDENCE_OK


def test_infer_role_milestone_number_suffix_with_log_combines():
    """`Foo_M1_Implementation_Log.md` ends with `_Log` — the existing log
    matcher wins over the `_M\\d+` pattern. Today the `_Log` suffix is
    correctly detected (this is a regression lock — GREEN at baseline once
    suffix matching handles the mixed shape).
    """
    role, _conf = infer_role("Foo_M1_Implementation_Log.md", {})
    assert role == "log"


# --- F1 — H1-content inference (via plan_migration) ------------------------


def test_infer_role_h1_content_inference(tmp_path):
    """A file whose filename suffix doesn't match a role but whose H1 ends in
    a role word (`# Foo Plan`) should infer `role: plan` at medium
    confidence. Today H1-content inference isn't wired into `plan_migration`,
    so the file falls back to `notes`.

    OQ-D pins H1-content inference at **medium** confidence (review
    finding #1). Asserting medium exactly — not the
    medium/high/True compatibility set — prevents a Phase 6 implementation
    from quietly upgrading H1-content matches to "high".
    """
    _write(
        tmp_path / "foo.md",
        "# Foo Plan\n\nA plan-shaped document body.\n",
    )
    plan = plan_migration(tmp_path)
    fm = next(f for f in plan.files if f.rel == "foo.md")
    assert fm.role == "plan"
    assert fm.confidence is Confidence.MEDIUM, (
        f"H1-content inference must return medium confidence (OQ-D); got {fm.confidence!r}"
    )


# --- F1 — section-header pattern inference (via plan_migration) ------------


def test_infer_role_section_header_pattern_plan(tmp_path):
    """A file with `## Goal` + `## Scope` + `## Requirements` section
    headers should infer `role: plan` at medium confidence even when neither
    the filename suffix nor the H1 reveals the role. Today section-header
    inference is unimplemented; inference falls back to `notes`.

    OQ-D pins section-header inference at **medium** confidence (review
    finding #1). Strict-medium assertion prevents accidental upgrade to
    "high" by a Phase 6 implementation.
    """
    _write(
        tmp_path / "ambiguous.md",
        (
            "# Ambiguous Document\n\n"
            "## Goal\nAchieve X.\n\n"
            "## Scope\nIn-tree work.\n\n"
            "## Requirements\nMust-haves.\n\n"
            "## Exit criteria\nDone when…\n"
        ),
    )
    plan = plan_migration(tmp_path)
    fm = next(f for f in plan.files if f.rel == "ambiguous.md")
    assert fm.role == "plan"
    assert fm.confidence is Confidence.MEDIUM, (
        f"section-header inference must return medium confidence (OQ-D); got {fm.confidence!r}"
    )


# --- F1 — section-header pattern inference: status (positive + negative) ---


def test_infer_role_section_header_pattern_status_current_state_plus_updates(tmp_path):
    """OQ-D / milestone spec (m7-migration-accuracy.md:157): the
    section-header signal for ``role: status`` requires an AND-of-multiple-
    signals shape — ``## Current state + ## Progress`` OR
    ``## Current state + ## Updates``. A bare ``## Updates`` heading alone
    must NOT trigger status inference (it is too common across miscellaneous
    notes to carry the signal on its own).

    Positive: ``## Current state`` + ``## Updates`` → role=status, medium.
    """
    _write(
        tmp_path / "status-doc.md",
        ("# Some Doc\n\n## Current state\nNow.\n\n## Updates\n- 2026-05-25: did the thing.\n"),
    )
    plan = plan_migration(tmp_path)
    fm = next(f for f in plan.files if f.rel == "status-doc.md")
    assert fm.role == "status", (
        f"`## Current state` + `## Updates` must infer status; got {fm.role!r}"
    )
    assert fm.confidence is Confidence.MEDIUM, (
        f"section-header inference must return medium confidence (OQ-D); got {fm.confidence!r}"
    )


def test_infer_role_section_header_bare_updates_does_NOT_infer_status(tmp_path):
    """Negative companion: a file whose ONLY ``##`` heading is
    ``## Updates`` (no ``## Current state``) must NOT silently infer
    ``role: status``. Status inference is an AND-of-multiple-signals
    contract; the bare-``Updates`` shape is the negative case that the
    earlier `or "updates" in headings_set` clause swallowed too loosely.

    Today's tighter implementation falls back to ``notes``.
    """
    _write(
        tmp_path / "notes-doc.md",
        ("# Some Notes\n\n## Updates\n- 2026-05-25: just a notes file with an Updates section.\n"),
    )
    plan = plan_migration(tmp_path)
    fm = next(f for f in plan.files if f.rel == "notes-doc.md")
    assert fm.role == "notes", (
        f"a bare `## Updates` heading must NOT infer status (spec requires "
        f"`## Current state` + (`## Progress` OR `## Updates`)); got {fm.role!r}"
    )
    assert fm.confidence is Confidence.LOW, (
        f"with no inference signal, the file lands in notes/low; got {fm.confidence!r}"
    )


# --- F1 — sibling-set defaulting (OQ-C: ≥ 60% modal, ≥ 5 sample) -----------


def test_sibling_set_defaulting_fires_when_majority_met(fixtures_dir):
    """In a 10-file subdir where 7 files carry a `-spec` suffix, the 3
    remaining no-suffix files default to `role: spec` at medium confidence
    via sibling-set defaulting. Today the fallback is `notes` at low
    confidence — the modal-sibling code path doesn't exist.

    OQ-D / OQ-C pin sibling-set defaulting at **medium** confidence (review
    finding #1). Strict-medium assertion on every defaulted file prevents
    a Phase 6 implementation from quietly returning "high" for defaulted
    files (which would erase the operator-attention signal the medium
    level is designed to carry).
    """
    fixture = fixtures_dir / "sibling-defaulting" / "majority-met"
    plan = plan_migration(fixture)
    # The three no-suffix files (file-08, file-09, file-10 by naming) should
    # now resolve to `spec` via sibling-set defaulting. Review finding #7:
    # the prior `endswith(("08.md","09.md","10.md"))` clause was a redundant
    # over-broad filter — every no-suffix file in the fixture has
    # "no-suffix" in its rel path already.
    defaulted = [f for f in plan.files if "no-suffix" in f.rel]
    assert defaulted, "fixture must contain no-suffix files"
    for fm in defaulted:
        assert fm.role == "spec", f"{fm.rel}: expected spec via defaulting, got {fm.role!r}"
        assert fm.confidence is Confidence.MEDIUM, (
            f"{fm.rel}: sibling-set defaulting must return medium confidence (OQ-D); "
            f"got {fm.confidence!r}"
        )


def test_sibling_set_NOT_defaulting_when_sample_too_small(fixtures_dir):
    """A 4-file subdir (below the ≥ 5 minimum sample, OQ-C) must NOT default
    even if a single role is the modal one. The no-suffix file falls to
    `notes` at low confidence (today's behaviour) — this is a regression
    lock that should be GREEN at baseline.
    """
    fixture = fixtures_dir / "sibling-defaulting" / "sample-too-small"
    plan = plan_migration(fixture)
    no_suffix = [f for f in plan.files if "no-suffix" in f.rel]
    assert no_suffix, "fixture must contain a no-suffix file"
    for fm in no_suffix:
        assert fm.role == "notes"
        assert fm.confidence is Confidence.LOW


def test_sibling_set_NOT_defaulting_when_no_majority(fixtures_dir):
    """A 10-file subdir whose roles are mixed enough that no single role
    reaches 60% modal share must NOT default. The no-suffix files fall to
    `notes` at low confidence (today's behaviour) — regression lock,
    GREEN at baseline.
    """
    fixture = fixtures_dir / "sibling-defaulting" / "majority-not-met"
    plan = plan_migration(fixture)
    no_suffix = [f for f in plan.files if "no-suffix" in f.rel]
    assert no_suffix, "fixture must contain no-suffix files"
    for fm in no_suffix:
        assert fm.role == "notes"
        assert fm.confidence is Confidence.LOW
