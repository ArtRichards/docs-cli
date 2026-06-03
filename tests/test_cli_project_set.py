"""CLI end-to-end tests for `docs project set` (M15 — B2; Phase 2, written RED).

`docs project set <doc>... <new-project>` reassigns the `Project:` field of
one or more named docs (the single-doc counterpart to `project rename`).
These tests pin the cli.md contract authored in Phase 1:

- grammar: one nargs="+" run split as `*docs, new_project`; >=2 tokens;
- strict-root resolution + no-root refusal (exit 2);
- normalise + empty-string rejection (exit 2);
- the --new-project typo guard with the §5E did-you-mean shape (exit 2);
- per-doc Project: rewrite (insert when absent) + ONE end-of-batch INDEX;
- NO .docs.toml rewrite, NO Related:-edge rewrite;
- archived named doc → refuse WHOLE batch (exit 2) naming the path;
- validate-all-first atomic semantics (exit 1 missing/malformed doc);
- --dry-run / no-op / outside-root refusal.

RED until Phase 5 wires the `project set` subparser + Phase 6 implements
`_cmd_project_set`. The verb tests fail today with argparse exit 2
("invalid choice: 'set'") — the verb is not registered.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _run(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


def _multi_project_alpha_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "multi-project-alpha-sidecar", root)
    return root


def _rename_with_malformed_tree(fixtures_dir: Path, tmp_path: Path) -> Path:
    root = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / "rename-with-malformed", root)
    return root


def _add_ideas_doc(root: Path) -> None:
    """Inline an `ideas`-project doc so `idea` → did-you-mean `ideas`.

    The known-project set over `multi-project-alpha-sidecar` is {alpha, beta}
    (config.project=alpha + the active docs' resolved projects). Adding an
    explicit `Project: ideas` doc puts `ideas` in the set, so a typo `idea`
    has a close match for `difflib.get_close_matches`.
    """
    (root / "ideas-doc.md").write_text(
        "# Ideas Doc\n\nLifecycle: active\nRole: idea\nProject: ideas\n"
        "Updated: 2026-05-20\n\nA doc filed under the ideas project.\n"
    )


# --- Help / registration ----------------------------------------------------


def test_project_set_help(docs_script):
    proc = _run(docs_script, "project", "set", "--help")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The synopsis names the positional run and the typo-guard flag.
    assert "new-project" in proc.stdout or "new_project" in proc.stdout
    assert "--new-project" in proc.stdout


def test_project_set_subcommand_registered(docs_script):
    proc = _run(docs_script, "project", "--help")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "set" in proc.stdout


# --- Happy path: single + multi-doc -----------------------------------------


def test_project_set_single_doc(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    # Reassign one beta doc to the existing project `alpha` (a known project,
    # so no --new-project needed).
    proc = _run(docs_script, "project", "set", "beta-notes.md", "alpha", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    text = (root / "beta-notes.md").read_text()
    assert "Project: alpha" in text, text
    assert "Project: beta" not in text, text
    # Sibling beta docs are untouched.
    assert "Project: beta" in (root / "beta-status.md").read_text()


def test_project_set_multi_doc_atomic_batch_one_index_refresh(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    # Pre-build the INDEX so `set` refreshes (not creates) it.
    pre = _run(docs_script, "index", "--root", str(root))
    assert pre.returncode == 0, pre.stderr
    index = root / "INDEX.md"

    proc = _run(
        docs_script,
        "project",
        "set",
        "beta-notes.md",
        "beta-status.md",
        "alpha",
        "--root",
        str(root),
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    for name in ("beta-notes.md", "beta-status.md"):
        assert "Project: alpha" in (root / name).read_text(), name
    # cli.md pins the success footer: "set <new-project> on <N> doc(s)".
    assert "set alpha on 2 doc(s)" in proc.stderr, proc.stderr

    # A follow-up `docs index` must be a no-op — proving the set refreshed
    # the INDEX exactly once at end-of-batch (same proof as project rename).
    index_after_set = index.read_bytes()
    noop = _run(docs_script, "index", "--root", str(root))
    assert noop.returncode == 0, noop.stderr
    assert index.read_bytes() == index_after_set, (
        "INDEX changed on a follow-up `docs index` — `set` did not leave "
        "INDEX in a fully-refreshed state."
    )


def test_project_set_inserts_project_line_when_absent(docs_script, fixtures_dir, tmp_path):
    # topics/orphan.md carries no explicit Project: line; on `set`, a
    # `Project: <new>` line must be inserted (M2 set_metadata_field behaviour).
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    orphan = root / "topics" / "orphan.md"
    pre_text = orphan.read_text()
    assert not any(line.startswith("Project:") for line in pre_text.splitlines()), (
        "fixture invariant: topics/orphan.md must carry no Project: line"
    )

    # orphan resolves to `alpha` (the root project); set it to the existing
    # `beta` project so it's a real change.
    proc = _run(
        docs_script,
        "project",
        "set",
        "topics/orphan.md",
        "beta",
        "--root",
        str(root),
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "Project: beta" in orphan.read_text(), orphan.read_text()


# --- Normalisation ----------------------------------------------------------


def test_project_set_normalises_input(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    # `Beta` normalises to `beta`, a known project (no --new-project needed),
    # and the normalisation note is printed.
    proc = _run(docs_script, "project", "set", "alpha-charter.md", "Beta", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "Project: beta" in (root / "alpha-charter.md").read_text()
    assert 'normalised "Beta" to "beta"' in proc.stderr, proc.stderr


# --- Empty / whitespace name → exit 2 ---------------------------------------


def test_project_set_rejects_empty_name(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "project",
        "set",
        "alpha-charter.md",
        "",
        "--root",
        str(root),
        "--new-project",
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "normalises to empty string; project name must be non-empty" in proc.stderr


def test_project_set_rejects_whitespace_only_name(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "project",
        "set",
        "alpha-charter.md",
        "   ",
        "--root",
        str(root),
        "--new-project",
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "normalises to empty string; project name must be non-empty" in proc.stderr


# --- Typo guard -------------------------------------------------------------


def test_project_set_unknown_project_without_flag_refuses(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    before = (root / "alpha-charter.md").read_text()
    # `gamma` is not a known project and --new-project is absent.
    proc = _run(docs_script, "project", "set", "alpha-charter.md", "gamma", "--root", str(root))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "'gamma' is not a project in this tree; refusing" in proc.stderr, proc.stderr
    assert "to create a new project group, pass --new-project" in proc.stderr, proc.stderr
    # No mutation.
    assert (root / "alpha-charter.md").read_text() == before


def test_project_set_unknown_project_with_flag_succeeds(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    proc = _run(
        docs_script,
        "project",
        "set",
        "alpha-charter.md",
        "gamma",
        "--root",
        str(root),
        "--new-project",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "Project: gamma" in (root / "alpha-charter.md").read_text()


def test_project_set_did_you_mean_candidate(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    _add_ideas_doc(root)
    # `idea` is unknown but close to the now-known `ideas`.
    proc = _run(docs_script, "project", "set", "alpha-charter.md", "idea", "--root", str(root))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "'idea' is not a project in this tree; refusing" in proc.stderr, proc.stderr
    # cli.md §5E pins BOTH clauses together on the single `→` line: the
    # conditional `did you mean '<closest>'?` prefix AND the always-printed
    # `to create a new project group, pass --new-project` recovery hint. Find
    # the one `→` line and assert both clauses are present on it together —
    # guarding against a regression to the original ambiguous wording where the
    # recovery hint dropped when a close match existed.
    arrow_lines = [ln for ln in proc.stderr.splitlines() if "→" in ln]
    assert len(arrow_lines) == 1, proc.stderr
    arrow = arrow_lines[0]
    assert "did you mean 'ideas'?" in arrow, arrow
    assert "to create a new project group, pass --new-project" in arrow, arrow


# --- Archived target → refuse whole batch (exit 2) --------------------------


def test_project_set_archived_doc_refuses_whole_batch(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    archived = root / "archive" / "2026-04-01" / "beta-old.md"
    archived_before = archived.read_text()
    live_before = (root / "alpha-charter.md").read_text()

    # Batch names one live doc + one archived doc; the archived doc must
    # refuse the WHOLE batch (exit 2), leaving the live doc byte-identical.
    proc = _run(
        docs_script,
        "project",
        "set",
        "alpha-charter.md",
        "archive/2026-04-01/beta-old.md",
        "beta",
        "--root",
        str(root),
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "archive" in proc.stderr and "beta-old.md" in proc.stderr, proc.stderr
    assert archived.read_text() == archived_before
    assert (root / "alpha-charter.md").read_text() == live_before
    # No INDEX written by an aborted batch.
    assert not (root / "INDEX.md").exists()


def test_project_set_archived_precedence_is_order_independent_missing_first(
    docs_script, fixtures_dir, tmp_path
):
    """`<missing> <archived> <proj>` must exit 2 (archived), not exit 1 (missing).

    The archived check takes PRECEDENCE over missing/outside/malformed and is
    ORDER-INDEPENDENT (cli.md `project set` archived clause; §5E; resolved Q4):
    if ANY named doc is under archive_dir, the whole batch refuses exit 2
    REGARDLESS of position — even when an earlier token is missing.
    """
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    archived = root / "archive" / "2026-04-01" / "beta-old.md"
    archived_before = archived.read_text()
    proc = _run(
        docs_script,
        "project",
        "set",
        "does-not-exist.md",  # missing, named FIRST
        "archive/2026-04-01/beta-old.md",  # archived, named SECOND
        "beta",
        "--root",
        str(root),
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    # The archived path is named (not the missing one): the archived clause won.
    assert "archive" in proc.stderr and "beta-old.md" in proc.stderr, proc.stderr
    assert "is under the archive subtree" in proc.stderr, proc.stderr
    # Nothing mutated; no INDEX from the aborted batch.
    assert archived.read_text() == archived_before
    assert not (root / "INDEX.md").exists()


def test_project_set_archived_precedence_is_order_independent_outside_first(
    docs_script, fixtures_dir, tmp_path
):
    """`<outside> <archived> <proj>` must exit 2 (archived), not exit 1 (outside)."""
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    archived = root / "archive" / "2026-04-01" / "beta-old.md"
    archived_before = archived.read_text()
    outside = tmp_path / "outside.md"
    outside.write_text(
        "# Outside\n\nLifecycle: active\nRole: notes\nProject: alpha\n"
        "Updated: 2026-05-20\n\nBody.\n"
    )
    outside_before = outside.read_text()
    proc = _run(
        docs_script,
        "project",
        "set",
        str(outside),  # outside the root, named FIRST
        "archive/2026-04-01/beta-old.md",  # archived, named SECOND
        "beta",
        "--root",
        str(root),
    )
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "archive" in proc.stderr and "beta-old.md" in proc.stderr, proc.stderr
    assert "is under the archive subtree" in proc.stderr, proc.stderr
    # Neither file mutated; no INDEX.
    assert archived.read_text() == archived_before
    assert outside.read_text() == outside_before
    assert not (root / "INDEX.md").exists()


# --- Atomic validate failure (missing / malformed doc) ----------------------


def test_project_set_atomic_validate_failure_missing_doc(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    live_before = (root / "alpha-charter.md").read_text()
    proc = _run(
        docs_script,
        "project",
        "set",
        "alpha-charter.md",
        "does-not-exist.md",
        "beta",
        "--root",
        str(root),
    )
    # A missing named doc aborts the validate-all-first pass → exit 1.
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "does-not-exist.md" in proc.stderr, proc.stderr
    assert (root / "alpha-charter.md").read_text() == live_before
    assert not (root / "INDEX.md").exists()


def test_project_set_atomic_validate_failure_malformed_doc(docs_script, fixtures_dir, tmp_path):
    root = _rename_with_malformed_tree(fixtures_dir, tmp_path)
    good_before = (root / "good-a.md").read_text()
    # --new-project satisfies the typo guard so the only failure is the
    # malformed broken.md (no H1 → MetadataError → exit 1).
    proc = _run(
        docs_script,
        "project",
        "set",
        "good-a.md",
        "broken.md",
        "newproj",
        "--root",
        str(root),
        "--new-project",
    )
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "broken.md" in proc.stderr, proc.stderr
    # The good doc is byte-identical; no INDEX.
    assert (root / "good-a.md").read_text() == good_before
    assert not (root / "INDEX.md").exists()


# --- No-op ------------------------------------------------------------------


def test_project_set_no_op_when_already_current(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    before = (root / "alpha-charter.md").read_text()
    # alpha-charter.md is already Project: alpha.
    proc = _run(docs_script, "project", "set", "alpha-charter.md", "alpha", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "already current" in proc.stderr, proc.stderr
    assert "no rewrites needed" in proc.stderr, proc.stderr
    assert (root / "alpha-charter.md").read_text() == before
    # No INDEX refresh on a no-op.
    assert not (root / "INDEX.md").exists()


def test_project_set_mixed_no_op_rewrites_only_non_matching(docs_script, fixtures_dir, tmp_path):
    """A batch mixing an already-at-target doc + a needing-rewrite doc.

    The whole batch is NOT a no-op: `set` rewrites ONLY the non-matching
    doc(s), leaves the already-current doc byte-identical, and the footer
    counts only the rewritten doc(s) — `set <proj> on 1 doc(s)`.
    """
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    # alpha-charter.md is ALREADY Project: alpha (target); beta-notes.md is
    # Project: beta and NEEDS the rewrite to alpha.
    charter_before = (root / "alpha-charter.md").read_text()
    proc = _run(
        docs_script,
        "project",
        "set",
        "alpha-charter.md",  # already at target — must NOT be rewritten
        "beta-notes.md",  # needs rewrite alpha
        "alpha",
        "--root",
        str(root),
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The already-current doc is byte-identical (not re-stamped, no Updated bump).
    assert (root / "alpha-charter.md").read_text() == charter_before
    # The non-matching doc was rewritten.
    assert "Project: alpha" in (root / "beta-notes.md").read_text()
    assert "Project: beta" not in (root / "beta-notes.md").read_text()
    # Footer counts ONLY the rewritten doc — not the whole batch, not a no-op.
    assert "set alpha on 1 doc(s)" in proc.stderr, proc.stderr
    assert "already current" not in proc.stderr, proc.stderr


# --- Dry-run ----------------------------------------------------------------


def test_project_set_dry_run_makes_no_change(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    before = (root / "beta-notes.md").read_text()
    proc = _run(
        docs_script,
        "project",
        "set",
        "beta-notes.md",
        "alpha",
        "--root",
        str(root),
        "--dry-run",
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (root / "beta-notes.md").read_text() == before
    assert "would rewrite Project: in" in proc.stderr, proc.stderr
    assert not (root / "INDEX.md").exists()


# --- Outside-root refusal ---------------------------------------------------


def test_project_set_refuses_when_no_docs_toml(docs_script, tmp_path):
    bad = tmp_path / "no_docs_toml"
    bad.mkdir()
    (bad / "doc.md").write_text(
        "# Doc\n\nLifecycle: active\nRole: notes\nProject: x\nUpdated: 2026-05-20\n\nBody.\n"
    )
    proc = _run(docs_script, "project", "set", "doc.md", "y", "--new-project", cwd=bad)
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    # The refusal must carry the verb-specific prefix `docs: project set:` —
    # NOT `docs: project rename:`. _resolve_project_root currently hardcodes
    # the `project rename` prefix; pinning it here forces Phase 5/6 to
    # generalize the helper (verb-label param) or use a set-specific resolver.
    assert "docs: project set:" in proc.stderr, proc.stderr
    assert "is not under a docs root" in proc.stderr, proc.stderr
    assert "refusing" in proc.stderr, proc.stderr


def test_project_set_refuses_doc_outside_root(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text(
        "# Outside\n\nLifecycle: active\nRole: notes\nProject: alpha\n"
        "Updated: 2026-05-20\n\nBody.\n"
    )
    proc = _run(
        docs_script,
        "project",
        "set",
        str(outside),
        "alpha",
        "--root",
        str(root),
    )
    # Cross-verb exit-code convention (cli.md): the docs root WAS resolved (a
    # valid --root), but a named doc resolves OUTSIDE it. That is an
    # explicit-path error → exit 1 (matching `docs touch`'s precedent), NOT the
    # no-docs-root hard refusal (exit 2 — see the no-docs-toml test below).
    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "outside" in proc.stderr.lower(), proc.stderr
    assert outside.read_text().count("Project: alpha") == 1


# --- Does not rewrite Related: edges ----------------------------------------


def test_project_set_does_not_rewrite_related_edges(docs_script, fixtures_dir, tmp_path):
    # `set` changes no path, so it must NOT touch any Related: bullet across
    # the tree — unlike rename/archive/mv. Add a doc that points at the doc
    # we reassign and assert its Related: edge is byte-identical.
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    referrer = root / "referrer.md"
    referrer.write_text(
        "# Referrer\n\nLifecycle: active\nRole: notes\nProject: alpha\n"
        "Updated: 2026-05-20\n\nRelated:\n- pairs-with: beta-notes.md\n\nBody.\n"
    )
    referrer_before = referrer.read_text()

    proc = _run(docs_script, "project", "set", "beta-notes.md", "alpha", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    # The reassigned doc changed; the referrer's Related: edge did NOT.
    assert "Project: alpha" in (root / "beta-notes.md").read_text()
    assert referrer.read_text() == referrer_before, "set must not rewrite Related: edges"


# --- Single-token grammar error (exit 2) ------------------------------------


def test_project_set_single_token_is_grammar_error(docs_script, fixtures_dir, tmp_path):
    root = _multi_project_alpha_tree(fixtures_dir, tmp_path)
    # Only one positional token: ambiguous (doc or project?) → exit 2.
    proc = _run(docs_script, "project", "set", "alpha", "--root", str(root))
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "need at least one" in proc.stderr.lower() or "at least" in proc.stderr.lower(), (
        proc.stderr
    )
