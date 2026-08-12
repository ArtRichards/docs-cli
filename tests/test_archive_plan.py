"""M26 — `docs archive` core seam: candidates, planning, pre-flight, apply, JSON.

Phase 2 (written RED). Every symbol under test lands in Phase 5/6:
`ARCHIVE_EXCLUSION_REASONS`, `ArchiveMove`, `ArchivePlan`,
`archive_candidates`, `plan_archive`, `preflight_archive_plan`,
`apply_archive_plan`, `archive_plan_to_json`. They are reached through
`getattr(cli, ...)` rather than a module-level import, so collection stays
clean, the RED reason is a single honest `AttributeError`, and
`mypy src/ tests/` stays green at baseline (getattr yields `Any`).

The contract under test is D3 (candidate discovery / dedup / canonical
matching / ineligibility), D4 (validate-all-first pre-flight and the residual
partial-state admission), D5 (empty selection), and D7 (the operation-plan
record) of the milestone's *Decisions (Phase 1 — BINDING)* section.

Every tree here is an inline `tmp_path` builder rather than a committed
fixture: each test writes and then byte-compares, so a `shutil.copytree` of a
static tree would be pure overhead (the M25 rule, `test-strategy.md`). All
`Updated:` dates are static and no stale window is ever applied, so nothing
rots.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

import pytest

from docs_cli import cli

_DATE = "2026-08-11"
_DATED = f"archive/{_DATE}"

_SKIP_AS_ROOT = pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="root bypasses 0o444/0o555 write protection; the unwritable trigger does not fire",
)


def _m26(name: str):
    """Fetch an M26 symbol that does not exist yet.

    The indirection is deliberate: a module-level import of a missing name
    would be a COLLECTION error (the Phase-4 exit criterion forbids those),
    and a literal `getattr(cli, "…")` trips ruff's B009. This keeps the RED
    reason a single clean `AttributeError` and keeps mypy green.
    """
    return getattr(cli, name)


def _root(tmp_path: Path, name: str = "archprobe") -> Path:
    """An empty docs root with an explicit `[archive] dir`."""
    root = tmp_path / name
    root.mkdir()
    (root / ".docs.toml").write_text(f'[project]\nname = "{name}"\n\n[archive]\ndir = "archive"\n')
    return root


def _doc(
    root: Path,
    rel: str,
    *,
    edges: Sequence[str] = (),
    lifecycle: str = "active",
    updated: str = "2026-05-20",
) -> Path:
    """Write one conformant doc at `rel` under `root` and return its path."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (
        f"# {path.stem}\n\nLifecycle: {lifecycle}\nRole: notes\n"
        f"Project: {root.name}\nUpdated: {updated}\n"
    )
    if lifecycle == "archived":
        text += "Archived-reason: completed\n"
    if edges:
        text += "\nRelated:\n" + "".join(f"- {edge}\n" for edge in edges)
    text += "\n## Body\n\nProse.\n"
    path.write_text(text)
    return path


def _snapshot(root: Path) -> dict[str, bytes]:
    """Every file under `root`, keyed by root-relative POSIX path.

    Whole-tree byte identity — `INDEX.md` and `.docs.toml` included — is what
    makes "zero bytes written" a real assertion rather than a
    `not (root / "archive").exists()` proxy.
    """
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _candidates(root: Path, primary: str, scope: str | None = None):
    config = cli.load_config(root)
    path = root / primary
    doc = cli.parse(path.read_text(), path, root)
    return _m26("archive_candidates")(doc, root, config, scope)


def _plan(
    root: Path,
    primary: str,
    *,
    scope: str | None = None,
    date_str: str = _DATE,
    reason: str | None = None,
):
    config = cli.load_config(root)
    path = root / primary
    doc = cli.parse(path.read_text(), path, root)
    return _m26("plan_archive")(
        root,
        config,
        primary=path,
        doc=doc,
        scope=scope,
        date_str=date_str,
        reason=reason,
    )


# --- D3 — candidate discovery ----------------------------------------------


def test_archive_exclusion_reasons_is_the_frozen_token_set():
    """The four machine-stable `--json` `reason` values, and only those.

    RED reason: `ARCHIVE_EXCLUSION_REASONS` does not exist (Phase 5).
    """
    assert _m26("ARCHIVE_EXCLUSION_REASONS") == frozenset(
        {"not-selected", "already-archived", "unresolved-target", "outside-root"}
    )


def test_candidates_follow_only_pairs_with_and_child_of(tmp_path):
    """D3: exactly two candidate verbs. M25's six reciprocal verbs, plus
    `references` / `implements` / `parent-of`, are never candidates —
    sequence, dependency, and blocking do not imply archive membership.

    RED reason: `archive_candidates` does not exist (Phase 5).
    """
    root = _root(tmp_path)
    for name in ("keep-a", "keep-b", "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"):
        _doc(root, f"{name}.md")
    _doc(
        root,
        "primary.md",
        edges=[
            "pairs-with: keep-a.md",
            "child-of: keep-b.md",
            "precedes: x1.md",
            "follows: x2.md",
            "depends-on: x3.md",
            "required-by: x4.md",
            "blocks: x5.md",
            "blocked-by: x6.md",
            "references: x7.md",
            "implements: x8.md",
            "parent-of: x9.md",
        ],
    )

    candidates = _candidates(root, "primary.md")
    assert [c.rel for c in candidates] == ["keep-a.md", "keep-b.md"]
    assert [c.verb for c in candidates] == ["pairs-with", "child-of"]


def test_candidates_are_in_related_declaration_order(tmp_path):
    """D3: the surviving order is `Related:` declaration order, not sorted.

    RED reason: `archive_candidates` does not exist (Phase 5).
    """
    root = _root(tmp_path)
    for name in ("charlie", "alpha", "bravo"):
        _doc(root, f"{name}.md")
    _doc(
        root,
        "primary.md",
        edges=["pairs-with: charlie.md", "child-of: alpha.md", "pairs-with: bravo.md"],
    )

    assert [c.rel for c in _candidates(root, "primary.md")] == [
        "charlie.md",
        "alpha.md",
        "bravo.md",
    ]


def test_candidates_deduplicate_a_doc_reachable_by_two_verbs(tmp_path):
    """E2 / D3: a doc reachable by `pairs-with` AND `child-of` appears ONCE,
    with the first-declared verb.

    Today `_cascade_set` yields it twice, so the second `_archive_one` call
    fails with `[Errno 2] No such file or directory` — a false failure line on
    a successful run.

    RED reason: `archive_candidates` does not exist (Phase 5).
    """
    root = _root(tmp_path)
    _doc(root, "b.md")
    _doc(root, "a.md", edges=["pairs-with: b.md", "child-of: b.md"])

    candidates = _candidates(root, "a.md")
    assert len(candidates) == 1, "a doc reachable by two edges is ONE candidate"
    assert candidates[0].rel == "b.md"
    assert candidates[0].verb == "pairs-with", "first declaration wins"


def test_candidates_dedup_on_the_canonical_path(tmp_path):
    """D3: `./b.md` and `b.md` are ONE candidate, keyed on the canonical path,
    and every declared spelling survives in `aliases`.

    `aliases` is load-bearing: `_rewrite_referring_edges` matches a bullet iff
    its target EXACTLY equals an `old_rel`, so a `./b.md` bullet is only
    repointed when the batch carries that spelling too.

    RED reason: `archive_candidates` does not exist (Phase 5).
    """
    root = _root(tmp_path)
    _doc(root, "b.md")
    _doc(root, "a.md", edges=["pairs-with: ./b.md", "child-of: b.md"])

    candidates = _candidates(root, "a.md")
    assert len(candidates) == 1
    assert candidates[0].rel == "b.md", "the canonical form is the identity"
    assert candidates[0].aliases == ("./b.md", "b.md"), "every declared spelling is kept"


def test_scope_matches_the_canonical_path_not_the_declared_spelling(tmp_path):
    """D3: `--cascade-only 'b.md'` selects a candidate declared as `./b.md`.

    Pins the canonical amendment: today `_cascade_set` matches the raw target,
    so `./b.md` would dodge the scope entirely.

    RED reason: `archive_candidates` does not exist (Phase 5).
    """
    root = _root(tmp_path)
    _doc(root, "b.md")
    _doc(root, "a.md", edges=["pairs-with: ./b.md"])

    (candidate,) = _candidates(root, "a.md", "b.md")
    assert candidate.selected is True
    assert candidate.reason is None
    # `archive_candidates` takes no date, so it cannot compute a destination —
    # that is `plan_archive`'s job, and only for the selected members.
    assert candidate.dest is None and candidate.dest_rel is None
    (planned,) = [c for c in _plan(root, "a.md", scope="b.md").candidates if c.selected]
    assert planned.dest_rel == f"{_DATED}/b.md"


def test_candidates_exclude_the_primary_itself(tmp_path):
    """D3 (Phase-1 Q6): a self-edge is silently excluded — not a candidate,
    and NOT reported as ineligible.

    RED reason: `archive_candidates` does not exist (Phase 5).
    """
    root = _root(tmp_path)
    _doc(root, "b.md")
    _doc(root, "a.md", edges=["pairs-with: ./a.md", "pairs-with: b.md"])

    candidates = _candidates(root, "a.md")
    assert [c.rel for c in candidates] == ["b.md"], "the self-edge is not a candidate"
    assert all(c.reason != "already-archived" for c in candidates)


def test_archived_candidate_is_ineligible_with_reason(tmp_path):
    """E4 / D3: a candidate under the archive subtree is excluded and named
    ineligible with `already-archived`.

    Today `--cascade` relocates and re-dates it — data corruption.

    RED reason: `archive_candidates` does not exist (Phase 5).
    """
    root = _root(tmp_path)
    _doc(root, "log.md")
    _doc(root, "archive/2026-01-01/old.md", lifecycle="archived", updated="2026-01-01")
    _doc(
        root,
        "plan.md",
        edges=["pairs-with: log.md", "pairs-with: archive/2026-01-01/old.md"],
    )

    candidates = _candidates(root, "plan.md", "*")
    by_rel = {c.rel: c for c in candidates}
    assert set(by_rel) == {"log.md", "archive/2026-01-01/old.md"}
    archived = by_rel["archive/2026-01-01/old.md"]
    assert archived.selected is False
    assert archived.reason == "already-archived"
    assert archived.dest is None and archived.dest_rel is None


def test_unresolved_candidate_is_ineligible_with_reason(tmp_path):
    """D3: a `pairs-with` target that is not a file is `unresolved-target`.

    `docs check`'s `broken-ref` still owns the finding; the archive planner
    only refuses to move it.

    RED reason: `archive_candidates` does not exist (Phase 5).
    """
    root = _root(tmp_path)
    _doc(root, "a.md", edges=["pairs-with: ghost.md"])

    (candidate,) = _candidates(root, "a.md", "*")
    assert candidate.selected is False
    assert candidate.reason == "unresolved-target"


def test_candidate_outside_the_root_is_ineligible(tmp_path):
    """D3 (Phase-1 Q7): a candidate whose canonical path escapes the root is
    `outside-root`, even when the file really exists out there.

    RED reason: `archive_candidates` does not exist (Phase 5).
    """
    root = _root(tmp_path)
    (tmp_path / "escape.md").write_text(
        "# Escape\n\nLifecycle: active\nRole: notes\nProject: other\nUpdated: 2026-05-20\n"
    )
    _doc(root, "a.md", edges=["pairs-with: ../escape.md"])

    (candidate,) = _candidates(root, "a.md", "*")
    assert candidate.selected is False
    assert candidate.reason == "outside-root"


@pytest.mark.parametrize(
    ("edge", "expected"),
    [
        pytest.param("pairs-with: ../ghost.md", "outside-root", id="outside-beats-unresolved"),
        pytest.param(
            "pairs-with: archive/2026-01-01/ghost.md",
            "already-archived",
            id="archived-beats-unresolved",
        ),
    ],
)
def test_ineligibility_reason_precedence_is_pinned(tmp_path, edge, expected):
    """D3: two ineligibility conditions can hold at once, so the reported
    reason must be deterministic — `outside-root`, then `already-archived`,
    then `unresolved-target`.

    RED reason: `archive_candidates` does not exist (Phase 5).
    """
    root = _root(tmp_path)
    _doc(root, "a.md", edges=[edge])

    (candidate,) = _candidates(root, "a.md", "*")
    assert candidate.selected is False
    assert candidate.reason == expected


def test_unselected_candidate_carries_not_selected(tmp_path):
    """D3/D7: an eligible candidate the scope did not select reports
    `not-selected` and gets no destination.

    RED reason: `archive_candidates` does not exist (Phase 5).
    """
    root = _root(tmp_path)
    _doc(root, "b.md")
    _doc(root, "c.md")
    _doc(root, "a.md", edges=["pairs-with: b.md", "pairs-with: c.md"])

    by_rel = {c.rel: c for c in _candidates(root, "a.md", "b.md")}
    assert by_rel["b.md"].selected is True and by_rel["b.md"].reason is None
    assert by_rel["c.md"].selected is False
    assert by_rel["c.md"].reason == "not-selected"
    assert by_rel["c.md"].dest_rel is None


# --- D4 — planning purity and the validate-all-first pre-flight -------------


def test_plan_archive_writes_nothing(tmp_path):
    """D4: planning is pure — building the whole plan touches no byte.

    RED reason: `plan_archive` does not exist (Phase 5).
    """
    root = _root(tmp_path)
    _doc(root, "b.md")
    _doc(root, "a.md", edges=["pairs-with: b.md"])
    before = _snapshot(root)

    plan = _plan(root, "a.md", scope="b.md")

    assert _snapshot(root) == before, "plan_archive must not write"
    assert plan.primary.rel == "a.md"
    assert plan.primary.selected is True
    assert plan.primary.verb is None, "the primary has no discovering verb"
    assert plan.primary.dest_rel == f"{_DATED}/a.md"
    assert plan.scope == "b.md"
    assert plan.date_str == _DATE
    assert [m.rel for m in plan.moves] == ["a.md", "b.md"], (
        "moves is the primary plus the selected candidates, primary first"
    )


def _collision_root(tmp_path: Path) -> Path:
    root = _root(tmp_path, "collision")
    _doc(root, "x/dup.md")
    _doc(root, "y/dup.md")
    _doc(root, "root.md", edges=["pairs-with: x/dup.md", "pairs-with: y/dup.md"])
    return root


def test_preflight_refuses_intra_plan_destination_collision(tmp_path):
    """E3 / D4: two selected candidates sharing a basename resolve to ONE
    destination — refuse before any write, naming both sources.

    Today the second `_archive_one` raises `FileExistsError`, the loop prints a
    bare-path line, one doc is silently left behind, and the run exits 0.

    RED reason: `plan_archive` / `preflight_archive_plan` do not exist
    (Phase 5).
    """
    root = _collision_root(tmp_path)
    plan = _plan(root, "root.md", scope="dup.md")
    before = _snapshot(root)

    with pytest.raises(_m26("CoordinatedWriteError")) as excinfo:
        _m26("preflight_archive_plan")(plan)

    assert str(excinfo.value) == (
        f"x/dup.md and y/dup.md would both archive to {_DATED}/dup.md; refusing before any write"
    )
    assert _snapshot(root) == before


def _occupied_root(tmp_path: Path) -> Path:
    root = _root(tmp_path, "occupied")
    _doc(root, "b.md")
    _doc(root, "a.md", edges=["pairs-with: b.md"])
    _doc(root, f"{_DATED}/b.md", lifecycle="archived", updated=_DATE)
    return root


def test_preflight_refuses_an_occupied_destination(tmp_path):
    """D4: an archive slot that is already taken refuses the whole plan.

    RED reason: `plan_archive` / `preflight_archive_plan` do not exist
    (Phase 5).
    """
    root = _occupied_root(tmp_path)
    plan = _plan(root, "a.md", scope="b.md")
    before = _snapshot(root)

    with pytest.raises(_m26("CoordinatedWriteError")) as excinfo:
        _m26("preflight_archive_plan")(plan)

    assert str(excinfo.value) == (
        f"archive destination already exists: {_DATED}/b.md (for b.md); refusing before any write"
    )
    assert _snapshot(root) == before


def _unwritable_source_root(tmp_path: Path) -> Path:
    root = _root(tmp_path, "rosource")
    _doc(root, "b.md")
    _doc(root, "a.md", edges=["pairs-with: b.md"])
    (root / "b.md").chmod(0o444)
    return root


@_SKIP_AS_ROOT
def test_preflight_refuses_an_unwritable_source(tmp_path):
    """D4: an unwritable plan member refuses before any write.

    The check must be an explicit `os.access(..., W_OK)` test, NOT a trial
    write: `atomic_write` is tmpfile + rename, and POSIX `rename()` onto a
    read-only file succeeds when the directory is writable, so only the
    explicit check honours the mode (the M25 lesson).

    RED reason: `plan_archive` / `preflight_archive_plan` do not exist
    (Phase 5).
    """
    root = _unwritable_source_root(tmp_path)
    try:
        plan = _plan(root, "a.md", scope="b.md")
        before = _snapshot(root)

        with pytest.raises(_m26("CoordinatedWriteError")) as excinfo:
            _m26("preflight_archive_plan")(plan)

        assert str(excinfo.value) == "b.md is not writable; refusing before any write"
        assert _snapshot(root) == before
    finally:
        (root / "b.md").chmod(0o644)


def _unwritable_dest_root(tmp_path: Path) -> Path:
    root = _root(tmp_path, "rodest")
    _doc(root, "b.md")
    _doc(root, "a.md", edges=["pairs-with: b.md"])
    (root / "archive").mkdir()
    (root / "archive").chmod(0o555)
    return root


@_SKIP_AS_ROOT
def test_preflight_refuses_an_unwritable_destination_directory(tmp_path):
    """D4: when the dated destination dir does not exist yet, the nearest
    existing ancestor is the one that must be writable.

    RED reason: `plan_archive` / `preflight_archive_plan` do not exist
    (Phase 5).
    """
    root = _unwritable_dest_root(tmp_path)
    try:
        plan = _plan(root, "a.md", scope="b.md")
        before = _snapshot(root)

        with pytest.raises(_m26("CoordinatedWriteError")) as excinfo:
            _m26("preflight_archive_plan")(plan)

        assert str(excinfo.value) == "archive is not writable; refusing before any write"
        assert _snapshot(root) == before
    finally:
        (root / "archive").chmod(0o755)


def _archived_primary_root(tmp_path: Path) -> Path:
    root = _root(tmp_path, "archprimary")
    _doc(root, "a.md")
    _doc(
        root,
        "archive/2026-01-01/old.md",
        lifecycle="archived",
        updated="2026-01-01",
        edges=["pairs-with: a.md"],
    )
    return root


def test_preflight_refuses_an_archived_primary(tmp_path):
    """E4 / D4 (Phase-1 Q1): re-archiving an archived document is a refusal,
    not a re-dating — and the refusal is unconditional across all three D1
    shapes.

    RED reason: `plan_archive` / `preflight_archive_plan` do not exist
    (Phase 5).
    """
    root = _archived_primary_root(tmp_path)
    plan = _plan(root, "archive/2026-01-01/old.md", scope="a.md")
    before = _snapshot(root)

    with pytest.raises(_m26("CoordinatedWriteError")) as excinfo:
        _m26("preflight_archive_plan")(plan)

    assert str(excinfo.value) == (
        "archive/2026-01-01/old.md is already under the archive subtree; refusing before any write"
    )
    assert _snapshot(root) == before


def _malformed_member_root(tmp_path: Path) -> Path:
    root = _root(tmp_path, "malformed")
    _doc(root, "a.md", edges=["pairs-with: b.md"])
    (root / "b.md").write_text("no H1, no metadata block — unparseable.\n")
    return root


def test_preflight_refuses_a_candidate_without_a_metadata_block(tmp_path):
    """D4: a selected candidate with no editable metadata block refuses the
    whole plan (exit 1 at the CLI, per the Q4 split).

    The file EXISTS, so it is an eligible candidate — `unresolved-target` is
    about resolution, not parseability. The pre-flight owns this one.

    RED reason: `plan_archive` / `preflight_archive_plan` do not exist
    (Phase 5).
    """
    root = _malformed_member_root(tmp_path)
    plan = _plan(root, "a.md", scope="b.md")
    before = _snapshot(root)

    with pytest.raises(_m26("CoordinatedWriteError")) as excinfo:
        _m26("preflight_archive_plan")(plan)

    assert str(excinfo.value) == "b.md has no editable metadata block; refusing before any write"
    assert _snapshot(root) == before


_REFUSAL_CASES = {
    "collision": (_collision_root, "root.md", "dup.md", None),
    "occupied": (_occupied_root, "a.md", "b.md", None),
    "unwritable-source": (_unwritable_source_root, "a.md", "b.md", "b.md"),
    "unwritable-dest": (_unwritable_dest_root, "a.md", "b.md", "archive"),
    "archived-primary": (_archived_primary_root, "archive/2026-01-01/old.md", "a.md", None),
    "malformed-member": (_malformed_member_root, "a.md", "b.md", None),
}


@_SKIP_AS_ROOT
@pytest.mark.parametrize("case", sorted(_REFUSAL_CASES))
def test_every_preflight_refusal_leaves_the_tree_byte_identical(tmp_path, case):
    """D4: EVERY handled pre-flight failure refuses with zero mutation, and
    says so — `rolled_back` True (the tree is trivially unchanged) and
    `published` empty.

    Whole-tree byte identity, `.docs.toml` and any `INDEX.md` included, is the
    real assertion; `not (root / "archive").exists()` would be a proxy.

    RED reason: `plan_archive` / `preflight_archive_plan` do not exist
    (Phase 5).
    """
    build, primary, scope, locked = _REFUSAL_CASES[case]
    root = build(tmp_path)
    try:
        plan = _plan(root, primary, scope=scope)
        before = _snapshot(root)

        with pytest.raises(_m26("CoordinatedWriteError")) as excinfo:
            _m26("preflight_archive_plan")(plan)

        assert excinfo.value.rolled_back is True
        assert excinfo.value.published == ()
        assert _snapshot(root) == before
    finally:
        if locked is not None:
            (root / locked).chmod(0o755 if (root / locked).is_dir() else 0o644)


# --- D4 — execution and the residual partial-state admission ----------------


def test_apply_archive_plan_moves_the_primary_and_every_selected_candidate(tmp_path):
    """D4: execution moves the whole plan and returns the `(old_rel, new_rel)`
    pairs `_rewrite_referring_edges` consumes — one per DECLARED spelling
    (Phase-1 Q5), canonical form first.

    Without the alias pairs a `./b.md` bullet elsewhere in the tree would be
    left dangling, because `rewrite_related_refs` matches a bullet iff its
    target exactly equals an `old_rel`.

    RED reason: `plan_archive` / `apply_archive_plan` do not exist (Phase 5).
    """
    root = _root(tmp_path)
    _doc(root, "b.md")
    _doc(root, "a.md", edges=["pairs-with: ./b.md", "child-of: b.md"])
    plan = _plan(root, "a.md", scope="b.md")

    moves = _m26("apply_archive_plan")(plan)

    assert moves == [
        ("a.md", f"{_DATED}/a.md"),
        ("b.md", f"{_DATED}/b.md"),
        ("./b.md", f"{_DATED}/b.md"),
    ]
    assert (root / _DATED / "a.md").is_file()
    assert (root / _DATED / "b.md").is_file()
    assert not (root / "a.md").exists()
    assert not (root / "b.md").exists()
    assert f"Updated: {_DATE}" in (root / _DATED / "b.md").read_text()
    assert "Lifecycle: archived" in (root / _DATED / "b.md").read_text()


def _quad_plan(tmp_path: Path):
    """A four-member plan: primary `a.md` plus selected `b.md`, `c.md`, `d.md`."""
    root = _root(tmp_path, "quad")
    for name in ("b", "c", "d"):
        _doc(root, f"{name}.md")
    _doc(root, "a.md", edges=["pairs-with: b.md", "pairs-with: c.md", "pairs-with: d.md"])
    return root, _plan(root, "a.md", scope="*.md")


def _failing_write_on_call(n: int):
    """An `atomic_write` replacement that raises `OSError` on the n-th call."""
    real_write = cli.atomic_write
    calls: list[Path] = []

    def _write(path: Path, content: str) -> None:
        calls.append(path)
        if len(calls) == n:
            raise OSError("disk full")
        real_write(path, content)

    return _write


def test_apply_archive_plan_partial_failure_admits_exactly_what_moved(tmp_path):
    """D4 residual: an unexpected `OSError` mid-execution is NOT rolled back —
    it is admitted exactly, naming what moved and what did not.

    Injected via `monkeypatch.setattr(cli, "atomic_write", ...)` failing on the
    third call (the `test_relate_plan.py` pattern): `a.md` and `b.md` land,
    `c.md` fails, `d.md` is never attempted.

    RED reason: `plan_archive` / `apply_archive_plan` do not exist (Phase 5).
    """
    root, plan = _quad_plan(tmp_path)
    assert [m.rel for m in plan.moves] == ["a.md", "b.md", "c.md", "d.md"]

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(cli, "atomic_write", _failing_write_on_call(3))
        with pytest.raises(_m26("CoordinatedWriteError")) as excinfo:
            _m26("apply_archive_plan")(plan)

    assert str(excinfo.value) == (
        "write failed for c.md: disk full; PARTIAL ARCHIVE — not rolled back. "
        f"Archived: a.md -> {_DATED}/a.md, b.md -> {_DATED}/b.md. "
        "Still at their original paths: c.md, d.md. Repair manually."
    )
    assert excinfo.value.rolled_back is False, "docs archive never rolls back (D4)"
    assert excinfo.value.published == ("a.md", "b.md")
    # The admission is checkable against the disk, byte for byte.
    assert (root / _DATED / "a.md").is_file()
    assert (root / _DATED / "b.md").is_file()
    assert (root / "c.md").is_file()
    assert (root / "d.md").is_file()
    assert not (root / _DATED / "c.md").exists()
    assert not (root / _DATED / "d.md").exists()


def test_apply_archive_plan_admission_when_nothing_had_moved_yet(tmp_path):
    """D4 residual: the `Archived: none` branch — never a blank list (the M25
    `_rollback_relate` lesson).

    RED reason: `plan_archive` / `apply_archive_plan` do not exist (Phase 5).
    """
    root, plan = _quad_plan(tmp_path)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(cli, "atomic_write", _failing_write_on_call(1))
        with pytest.raises(_m26("CoordinatedWriteError")) as excinfo:
            _m26("apply_archive_plan")(plan)

    assert str(excinfo.value) == (
        "write failed for a.md: disk full; PARTIAL ARCHIVE — not rolled back. "
        "Archived: none. Still at their original paths: a.md, b.md, c.md, d.md. "
        "Repair manually."
    )
    assert excinfo.value.rolled_back is False
    assert excinfo.value.published == ()
    assert not (root / "archive").exists()


# --- D7 — the operation-plan record ----------------------------------------

_TOP_LEVEL_KEYS = [
    "primary",
    "date",
    "scope",
    "candidates",
    "dry_run",
    "applied",
    "index_refreshed",
]


def _json_root(tmp_path: Path) -> Path:
    root = _root(tmp_path, "jsonprobe")
    _doc(root, "b.md")
    _doc(root, "c.md")
    _doc(root, "archive/2026-01-01/old.md", lifecycle="archived", updated="2026-01-01")
    _doc(
        root,
        "a.md",
        edges=[
            "pairs-with: b.md",
            "child-of: c.md",
            "pairs-with: archive/2026-01-01/old.md",
        ],
    )
    return root


def test_archive_plan_to_json_preview_shape(tmp_path):
    """D7: the exact record — closed top-level key set in order, per-candidate
    key set, `destination` non-null iff `selected`, `reason` null iff
    `selected`.

    RED reason: `plan_archive` / `archive_plan_to_json` do not exist (Phase 5).
    """
    root = _json_root(tmp_path)
    plan = _plan(root, "a.md", scope="b.md")

    record = _m26("archive_plan_to_json")(plan, dry_run=True, applied=False, index_refreshed=False)

    assert list(record) == _TOP_LEVEL_KEYS
    assert record["primary"] == {
        "source": str(root / "a.md"),
        "path": "a.md",
        "destination": f"{_DATED}/a.md",
    }
    assert record["date"] == _DATE
    assert record["scope"] == "b.md"
    assert record["dry_run"] is True
    assert record["applied"] is False
    assert record["index_refreshed"] is False
    assert record["candidates"] == [
        {
            "path": "b.md",
            "verb": "pairs-with",
            "selected": True,
            "destination": f"{_DATED}/b.md",
            "reason": None,
        },
        {
            "path": "c.md",
            "verb": "child-of",
            "selected": False,
            "destination": None,
            "reason": "not-selected",
        },
        {
            "path": "archive/2026-01-01/old.md",
            "verb": "pairs-with",
            "selected": False,
            "destination": None,
            "reason": "already-archived",
        },
    ]


def test_archive_plan_to_json_apply_shape_is_identical(tmp_path):
    """D7: a preview record and an apply record are diffable — the same key
    sets throughout; only `dry_run` / `applied` / `index_refreshed` differ.

    RED reason: `plan_archive` / `archive_plan_to_json` do not exist (Phase 5).
    """
    root = _json_root(tmp_path)
    plan = _plan(root, "a.md", scope="b.md")

    preview = _m26("archive_plan_to_json")(plan, dry_run=True, applied=False, index_refreshed=False)
    applied = _m26("archive_plan_to_json")(plan, dry_run=False, applied=True, index_refreshed=True)

    assert list(preview) == list(applied)
    assert preview["primary"] == applied["primary"]
    assert preview["candidates"] == applied["candidates"]
    assert [set(c) for c in preview["candidates"]] == [set(c) for c in applied["candidates"]]
    assert {
        k: v for k, v in preview.items() if k not in ("dry_run", "applied", "index_refreshed")
    } == {k: v for k, v in applied.items() if k not in ("dry_run", "applied", "index_refreshed")}
    assert (applied["dry_run"], applied["applied"], applied["index_refreshed"]) == (
        False,
        True,
        True,
    )


def test_archive_plan_to_json_lists_candidates_without_a_scope(tmp_path):
    """D7 (Phase-1 Q14): a plain `docs archive FILE` record still carries the
    WHOLE candidate set, each eligible one `selected: false` /
    `reason: "not-selected"`.

    D1's quiet rule governs stderr prose, not the record — the record's
    consumer is the agent deciding whether a selection is correct.

    RED reason: `plan_archive` / `archive_plan_to_json` do not exist (Phase 5).
    """
    root = _json_root(tmp_path)
    plan = _plan(root, "a.md", scope=None)

    record = _m26("archive_plan_to_json")(plan, dry_run=False, applied=True, index_refreshed=True)

    assert record["scope"] is None
    assert [c["path"] for c in record["candidates"]] == [
        "b.md",
        "c.md",
        "archive/2026-01-01/old.md",
    ]
    assert [c["reason"] for c in record["candidates"]] == [
        "not-selected",
        "not-selected",
        "already-archived",
    ]
    assert all(c["selected"] is False for c in record["candidates"])
    assert all(c["destination"] is None for c in record["candidates"])
