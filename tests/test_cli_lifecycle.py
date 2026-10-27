"""CLI end-to-end tests for `docs lifecycle <file>... <state>`.

The contract under test is the task plan's *Decisions (Phase 1 — BINDING)*
› P1.1 for milestone `lifecycle-and-free-form-relate` (D1–D3, plus D2's
extension-state clause through D10), mirrored in `docs/cli.md` › `docs
lifecycle`. The message ids `L1`–`L12` cited in docstrings are that
section's catalogue.

Written RED: `lifecycle` is not yet an argparse subcommand, so every
invocation exits 2 with argparse's `invalid choice: 'lifecycle'`. Because
argparse *already* exits 2, every intended-exit-2 test also asserts its exact
frozen stderr line, and every write test asserts on-disk bytes — a
returncode-only assertion would be falsely GREEN.

Every tree is an inline `tmp_path` builder: each test mutates and
byte-compares, so a committed tree would only add a `copytree` step.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

_TODAY = date.today().isoformat()


def _run(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=None if cwd is None else str(cwd),
        stdin=subprocess.DEVNULL,
    )


def _doc(
    title: str,
    *,
    lifecycle: str = "draft",
    role: str = "notes",
    project: str = "lc",
    updated: str = "2026-05-20",
    related: tuple[str, ...] = (),
) -> str:
    text = (
        f"# {title}\n\nLifecycle: {lifecycle}\nRole: {role}\n"
        f"Project: {project}\nUpdated: {updated}\n"
    )
    if related:
        text += "\nRelated:\n" + "".join(f"- {edge}\n" for edge in related)
    return text + "\n## Body\n\nProse.\n"


def _tree(
    tmp_path: Path, docs: dict[str, str], *, name: str = "lc", sidecar_extra: str = ""
) -> Path:
    """A managed root holding `docs` (root-relative path → full text)."""
    root = tmp_path / name
    root.mkdir(parents=True)
    (root / ".docs.toml").write_text(f'[project]\nname = "{name}"\n{sidecar_extra}')
    for rel, text in docs.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


def _snapshot(root: Path) -> dict[str, bytes]:
    """Every file under `root` — `INDEX.md` and `.docs.toml` included."""
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _promoted(text: str, *, to: str, updated: str = _TODAY) -> str:
    """`text` with exactly its `Lifecycle:` and `Updated:` metadata lines replaced.

    The expected bytes of a lifecycle edit, derived from the contract (two
    lines change, nothing else) rather than from the implementation.
    """
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    seen: set[str] = set()
    for line in lines:
        for label, value in (("Lifecycle", to), ("Updated", updated)):
            if label not in seen and line.startswith(f"{label}: "):
                ending = line[len(line.rstrip("\r\n")) :]
                line = f"{label}: {value}{ending}"
                seen.add(label)
                break
        out.append(line)
    assert seen == {"Lifecycle", "Updated"}, "test fixture must carry both lines"
    return "".join(out)


# --- help and the external consumer ----------------------------------------


def test_lifecycle_help_documents_the_grammar_and_flags(docs_script):
    proc = _run(docs_script, "lifecycle", "--help")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    for token in ("state", "--json", "--dry-run", "--quiet", "--root"):
        assert token in proc.stdout, f"`docs lifecycle --help` must document {token}"
    assert "docs archive" in proc.stdout, (
        "the help must say archiving belongs to `docs archive`, not to this verb"
    )


def test_help_verb_list_names_lifecycle_for_the_playbook_guard(docs_script):
    """The Agent Playbook Suite's CI guard, replicated exactly: it parses the
    FIRST brace group of `docs --help` with this regex and looks for a
    top-level `lifecycle` entry (`lifecycle-and-free-form-relate` — D1, D9)."""
    proc = _run(docs_script, "--help")
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    verb_match = re.search(r"\{([a-z0-9,\-]+)\}", proc.stdout)
    assert verb_match, "the guard could not parse a verb list from `docs --help`"
    assert "lifecycle" in verb_match.group(1).split(","), verb_match.group(1)


# --- the success path --------------------------------------------------------


def test_lifecycle_promotes_a_draft_to_active_and_bumps_updated(docs_script, tmp_path):
    original = _doc("M")
    root = _tree(tmp_path, {"m.md": original})

    proc = _run(docs_script, "lifecycle", "m.md", "active", "--root", str(root))

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "docs: lifecycle: set m.md from draft to active" in proc.stderr
    assert (root / "m.md").read_text() == _promoted(original, to="active")
    index = (root / "INDEX.md").read_text()
    assert f"Updated {_TODAY}." in index, "the INDEX is refreshed with the new state's date"


def test_lifecycle_accepts_several_files_then_one_state_and_refreshes_the_index(
    docs_script, tmp_path
):
    """D1's `*files, <state>` split: every token but the last is a document."""
    originals = {name: _doc(name.upper()) for name in ("a.md", "b.md", "c.md")}
    root = _tree(tmp_path, originals)

    proc = _run(docs_script, "lifecycle", "a.md", "b.md", "c.md", "active", "--root", str(root))

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    for name, original in originals.items():
        assert (root / name).read_text() == _promoted(original, to="active"), name
        assert f"docs: lifecycle: set {name} from draft to active" in proc.stderr
    index = (root / "INDEX.md").read_text()
    for name in originals:
        assert f"- [{name}]({name})" in index
    assert index.count(f"Updated {_TODAY}.") == 3, "the INDEX reflects the final state"


def test_lifecycle_mixed_batch_rewrites_only_the_documents_that_change(docs_script, tmp_path):
    """D3: only a document whose `Lifecycle:` moved is written and bumped."""
    draft, active = _doc("A"), _doc("B", lifecycle="active")
    root = _tree(tmp_path, {"a.md": draft, "b.md": active})
    untouched_inode = (root / "b.md").stat().st_ino

    proc = _run(docs_script, "lifecycle", "a.md", "b.md", "active", "--root", str(root))

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (root / "a.md").read_text() == _promoted(draft, to="active")
    assert (root / "b.md").read_text() == active, "no Updated: bump on an unchanged document"
    assert (root / "b.md").stat().st_ino == untouched_inode, (
        "an unchanged document is not rewritten"
    )
    assert "docs: lifecycle: set a.md from draft to active" in proc.stderr
    assert "docs: lifecycle: no change — b.md is already active" in proc.stderr


def test_lifecycle_already_in_state_writes_zero_bytes_and_skips_reindex(docs_script, tmp_path):
    """D3: a whole-batch no-op writes nothing — not even the INDEX, which a
    sentinel proves was never regenerated — and its record says so."""
    root = _tree(
        tmp_path,
        {"a.md": _doc("A", lifecycle="active"), "b.md": _doc("B", lifecycle="active")},
    )
    (root / "INDEX.md").write_text("SENTINEL — never regenerated by a no-op\n")
    before = _snapshot(root)

    proc = _run(docs_script, "lifecycle", "a.md", "b.md", "active", "--root", str(root), "--json")

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert _snapshot(root) == before
    assert "docs: lifecycle: no change — a.md is already active" in proc.stderr
    assert "docs: lifecycle: no change — b.md is already active" in proc.stderr
    record = json.loads(proc.stdout)
    assert record["applied"] is False, "nothing was written, so nothing was applied"
    assert record["index_refreshed"] is False
    assert [e["change"] for e in record["edits"]] == ["unchanged", "unchanged"]


@pytest.mark.parametrize("state", ["draft", "active", "blocked", "done", "superseded"])
def test_lifecycle_round_trips_every_top_level_state_without_status_drift(
    docs_script, tmp_path, state
):
    """Every allowed transition leaves `docs check` clean (no `status-drift`),
    and applying the same invocation twice equals applying it once."""
    start = "active" if state == "draft" else "draft"
    original = _doc("M", lifecycle=start)
    root = _tree(tmp_path, {"m.md": original})

    first = _run(docs_script, "lifecycle", "m.md", state, "--root", str(root))
    assert first.returncode == 0, (first.stdout, first.stderr)
    assert (root / "m.md").read_text() == _promoted(original, to=state)
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, check.stdout + check.stderr
    once = _snapshot(root)

    second = _run(docs_script, "lifecycle", "m.md", state, "--root", str(root))
    assert second.returncode == 0, (second.stdout, second.stderr)
    assert _snapshot(root) == once, "applying twice equals applying once, byte for byte"


def test_lifecycle_leaves_every_other_byte_unchanged(docs_script, tmp_path):
    """The M2 surgical contract: only the metadata block's `Lifecycle:` and
    `Updated:` values move — not a body line that merely looks like one, not
    an extra field, not `Related:`, not the missing trailing newline."""
    original = (
        "# Rich\n\nLifecycle: draft\nRole: spec\nProject: lc\nUpdated: 2026-05-20\n"
        "Owner: someone\n\nRelated:\n- pairs-with: other.md\n\n## Body\n\n"
        "Lifecycle: draft — a prose line that only looks like metadata.\n"
        "Updated: 2026-05-20 is also prose here, and the file has no final newline."
    )
    root = _tree(tmp_path, {"rich.md": original, "other.md": _doc("Other")})

    proc = _run(docs_script, "lifecycle", "rich.md", "blocked", "--root", str(root))

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (root / "rich.md").read_text() == _promoted(original, to="blocked")


def test_lifecycle_writes_an_extension_state_and_the_tree_reindexes(docs_script, tmp_path):
    """D2's extension-state clause through D10: a configured `add_lifecycles`
    state is a valid target, and the reindex, `docs list`, `docs relate` and
    `docs index` all read the document afterwards."""
    original = _doc("M")
    root = _tree(
        tmp_path,
        {"m.md": original, "n.md": _doc("N", lifecycle="active")},
        sidecar_extra='\n[vocabulary]\nadd_lifecycles = ["shipped"]\n',
    )

    proc = _run(docs_script, "lifecycle", "m.md", "shipped", "--root", str(root))
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (root / "m.md").read_text() == _promoted(original, to="shipped")
    assert "- [m.md](m.md)" in (root / "INDEX.md").read_text()

    listed = _run(docs_script, "list", "--root", str(root), "--json")
    assert listed.returncode == 0, listed.stderr
    states = {record["path"]: record["lifecycle"] for record in json.loads(listed.stdout)}
    assert states.get("m.md") == "shipped", states

    related = _run(docs_script, "relate", "add", "n.md", "precedes", "m.md", "--root", str(root))
    assert related.returncode == 0, (related.stdout, related.stderr)
    assert _run(docs_script, "index", "--root", str(root)).returncode == 0
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, check.stdout + check.stderr


# --- refusals: the archive boundary (D2) ------------------------------------


def test_lifecycle_refuses_archived_as_a_target_state(docs_script, tmp_path):
    """L5 — `archived` is never a target: `docs archive` owns that move."""
    root = _tree(tmp_path, {"m.md": _doc("M", lifecycle="done")})
    before = _snapshot(root)

    proc = _run(docs_script, "lifecycle", "m.md", "archived", "--root", str(root))

    assert proc.returncode == 2
    assert (
        "docs: lifecycle: 'archived' is not a lifecycle target — docs archive <file> "
        "moves lifecycle and location together; refusing"
    ) in proc.stderr, proc.stderr
    assert _snapshot(root) == before


def test_lifecycle_treats_a_capitalised_archived_as_an_unknown_state(docs_script, tmp_path):
    """L6 — matching is case-sensitive exact, so `Archived` is not a spelling of
    `archived`: it is an unknown state, and the message lists the default set."""
    root = _tree(tmp_path, {"m.md": _doc("M")})
    before = _snapshot(root)

    proc = _run(docs_script, "lifecycle", "m.md", "Archived", "--root", str(root))

    assert proc.returncode == 2
    assert (
        "docs: lifecycle: unknown state 'Archived'; expected one of: "
        "active, blocked, done, draft, superseded"
    ) in proc.stderr, proc.stderr
    assert _snapshot(root) == before


def test_lifecycle_unknown_state_names_the_allowed_states(docs_script, tmp_path):
    """L6 — the allowed states are the TREE's configured vocabulary minus
    `archived`, so a configured extension is listed among them."""
    root = _tree(
        tmp_path,
        {"m.md": _doc("M")},
        sidecar_extra='\n[vocabulary]\nadd_lifecycles = ["shipped"]\n',
    )
    before = _snapshot(root)

    proc = _run(docs_script, "lifecycle", "m.md", "shiped", "--root", str(root))

    assert proc.returncode == 2
    assert (
        "docs: lifecycle: unknown state 'shiped'; expected one of: "
        "active, blocked, done, draft, shipped, superseded"
    ) in proc.stderr, proc.stderr
    assert _snapshot(root) == before


def test_lifecycle_refuses_a_document_under_the_archive_subtree(docs_script, tmp_path):
    """L7 — an archived document is never a source."""
    root = _tree(
        tmp_path,
        {"archive/2026-01-01/old.md": _doc("Old", lifecycle="archived")},
    )
    before = _snapshot(root)

    proc = _run(
        docs_script, "lifecycle", "archive/2026-01-01/old.md", "active", "--root", str(root)
    )

    assert proc.returncode == 2
    assert (
        "docs: lifecycle: archive/2026-01-01/old.md is under the archive subtree "
        "(read-only); refusing"
    ) in proc.stderr, proc.stderr
    assert _snapshot(root) == before


def test_lifecycle_refuses_an_active_tree_document_already_marked_archived(docs_script, tmp_path):
    """L11 — a document reading `Lifecycle: archived` outside the archive
    subtree is in status-drift; flipping it would unarchive it by hand."""
    root = _tree(tmp_path, {"stray.md": _doc("Stray", lifecycle="archived")})
    before = _snapshot(root)

    proc = _run(docs_script, "lifecycle", "stray.md", "active", "--root", str(root))

    assert proc.returncode == 2
    assert (
        "docs: lifecycle: stray.md reads 'Lifecycle: archived' outside the archive subtree "
        "(status-drift); refusing — only docs archive sets archived"
    ) in proc.stderr, proc.stderr
    assert _snapshot(root) == before


def test_lifecycle_batch_with_one_archived_document_writes_nothing(docs_script, tmp_path):
    """L7 runs over the whole batch FIRST: the archived document is named last,
    after a valid document and a missing one, and still decides the outcome —
    exit 2, and the valid document is not written."""
    root = _tree(
        tmp_path,
        {"a.md": _doc("A"), "archive/2026-01-01/old.md": _doc("Old", lifecycle="archived")},
    )
    before = _snapshot(root)

    proc = _run(
        docs_script,
        "lifecycle",
        "a.md",
        "missing.md",
        "archive/2026-01-01/old.md",
        "active",
        "--root",
        str(root),
    )

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert (
        "docs: lifecycle: archive/2026-01-01/old.md is under the archive subtree "
        "(read-only); refusing"
    ) in proc.stderr, proc.stderr
    assert _snapshot(root) == before


# --- refusals: grammar, resolution, root ------------------------------------


def test_lifecycle_single_token_is_refused_as_ambiguous(docs_script, tmp_path):
    """L1 — one token could be a document or a state."""
    root = _tree(tmp_path, {"m.md": _doc("M")})
    before = _snapshot(root)

    proc = _run(docs_script, "lifecycle", "m.md", "--root", str(root))

    assert proc.returncode == 2
    assert "docs: lifecycle: need at least one <file> and a <state>" in proc.stderr, proc.stderr
    assert _snapshot(root) == before


@pytest.mark.parametrize("problem", ["missing", "outside-the-root"])
def test_lifecycle_missing_or_outside_root_file_exits_1_unchanged(docs_script, tmp_path, problem):
    """L9 / L8 — validate-all-first: the valid document named before the bad
    one is not written, and nothing else is either."""
    root = _tree(tmp_path, {"a.md": _doc("A")})
    if problem == "missing":
        bad, phrase = "nope.md", "docs: lifecycle: file not found: "
    else:
        stray = tmp_path / "stray.md"
        stray.write_text(_doc("Stray"))
        bad, phrase = str(stray), " is outside the resolved docs root ("
    before = _snapshot(root)

    proc = _run(docs_script, "lifecycle", "a.md", bad, "active", "--root", str(root))

    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert phrase in proc.stderr, proc.stderr
    assert "docs: lifecycle: " in proc.stderr, "the refusal speaks in the verb's own voice"
    assert Path(bad).name in proc.stderr, "the refusal names the offending path"
    assert _snapshot(root) == before


def test_lifecycle_malformed_document_exits_1_with_the_parser_message(docs_script, tmp_path):
    """L10 — the parser's own self-locating message, not a lucky exit 1."""
    root = _tree(tmp_path, {"a.md": _doc("A"), "b.md": "no h1 at all\n"})
    before = _snapshot(root)

    proc = _run(docs_script, "lifecycle", "a.md", "b.md", "active", "--root", str(root))

    assert proc.returncode == 1, (proc.stdout, proc.stderr)
    assert "Traceback" not in proc.stderr
    assert f"docs: {root.resolve() / 'b.md'}: " in proc.stderr, proc.stderr
    assert "missing H1" in proc.stderr
    assert _snapshot(root) == before


def test_lifecycle_refuses_outside_a_docs_root(docs_script, tmp_path):
    """L2 / L3 — the strict-root rule every mutating verb follows."""
    bare = tmp_path / "bare"
    bare.mkdir()
    (bare / "m.md").write_text(_doc("M"))
    before = _snapshot(bare)

    walked = _run(docs_script, "lifecycle", "m.md", "active", cwd=bare)
    assert walked.returncode == 2
    assert "docs: lifecycle: " in walked.stderr, walked.stderr
    assert "is not under a docs root with .docs.toml; refusing" in walked.stderr, walked.stderr

    named = _run(docs_script, "lifecycle", "m.md", "active", "--root", str(bare))
    assert named.returncode == 2
    assert (
        f"docs: lifecycle: --root {bare} does not contain .docs.toml; refusing" in named.stderr
    ), named.stderr
    assert _snapshot(bare) == before


# --- preview, output, record -------------------------------------------------


def test_lifecycle_dry_run_writes_nothing_and_previews_each_change(docs_script, tmp_path):
    root = _tree(tmp_path, {"a.md": _doc("A"), "b.md": _doc("B", lifecycle="active")})
    before = _snapshot(root)

    proc = _run(
        docs_script, "lifecycle", "a.md", "b.md", "active", "--root", str(root), "--dry-run"
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert "docs: lifecycle: would set a.md from draft to active" in proc.stderr
    assert "docs: lifecycle: no change — b.md is already active" in proc.stderr
    assert _snapshot(root) == before, "a preview writes nothing at all, INDEX included"


def test_lifecycle_json_record_has_a_closed_key_set(docs_script, tmp_path):
    """C15: the record's keys are closed — `updated_bumped` and `after` are
    deliberately absent (P1.1)."""
    root = _tree(tmp_path, {"a.md": _doc("A"), "b.md": _doc("B", lifecycle="active")})

    proc = _run(docs_script, "lifecycle", "a.md", "b.md", "active", "--root", str(root), "--json")

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    record = json.loads(proc.stdout)
    assert set(record) == {"state", "date", "dry_run", "applied", "index_refreshed", "edits"}
    assert record["state"] == "active"
    assert record["date"] == _TODAY
    assert record["dry_run"] is False
    assert record["applied"] is True
    assert record["index_refreshed"] is True
    assert record["edits"] == [
        {"path": "a.md", "before": "draft", "change": "set"},
        {"path": "b.md", "before": "active", "change": "unchanged"},
    ]


def test_lifecycle_dry_run_json_has_the_apply_shape(docs_script, tmp_path):
    """One shape for preview and apply, so the two are diffable: only the
    three mode flags differ."""
    docs = {"a.md": _doc("A"), "b.md": _doc("B", lifecycle="active")}
    previewed = _tree(tmp_path / "preview", docs, name="twin")
    applied = _tree(tmp_path / "apply", docs, name="twin")

    invocation = ("lifecycle", "a.md", "b.md", "active", "--json")
    preview = _run(docs_script, *invocation, "--root", str(previewed), "--dry-run")
    apply = _run(docs_script, *invocation, "--root", str(applied))

    assert preview.returncode == 0, (preview.stdout, preview.stderr)
    assert apply.returncode == 0, (apply.stdout, apply.stderr)
    preview_record, apply_record = json.loads(preview.stdout), json.loads(apply.stdout)
    assert set(preview_record) == set(apply_record)
    assert (preview_record["dry_run"], preview_record["applied"]) == (True, False)
    assert preview_record["index_refreshed"] is False
    for key in ("state", "date", "edits"):
        assert preview_record[key] == apply_record[key], key


def test_lifecycle_quiet_suppresses_success_but_never_a_refusal(docs_script, tmp_path):
    root = _tree(tmp_path, {"m.md": _doc("M")})

    ok = _run(docs_script, "lifecycle", "m.md", "active", "--root", str(root), "--quiet")
    assert ok.returncode == 0, (ok.stdout, ok.stderr)
    assert "docs: lifecycle:" not in ok.stderr
    assert "Lifecycle: active" in (root / "m.md").read_text(), "the write still happened"

    refused = _run(docs_script, "lifecycle", "m.md", "archived", "--root", str(root), "--quiet")
    assert refused.returncode == 2
    assert "docs: lifecycle: 'archived' is not a lifecycle target" in refused.stderr, (
        "--quiet must never silence a refusal"
    )


# --- the post-write tail, exclusion, duplicates -----------------------------


def test_lifecycle_index_refresh_failure_exits_2_with_documents_written(docs_script, tmp_path):
    """L12 — a malformed SIBLING fails the end-of-run reindex after the write:
    exit 2, the named document already carries its new state, and the record
    is still emitted with `index_refreshed: false`. A real malformed file, no
    mock."""
    original = _doc("A")
    root = _tree(tmp_path, {"a.md": original, "broken.md": "# Broken\n\nno metadata block\n"})

    proc = _run(docs_script, "lifecycle", "a.md", "active", "--root", str(root), "--json")

    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "docs: INDEX refresh failed: " in proc.stderr, proc.stderr
    assert (root / "a.md").read_text() == _promoted(original, to="active")
    record = json.loads(proc.stdout)
    assert record["applied"] is True
    assert record["index_refreshed"] is False


def test_lifecycle_reindex_honours_exclusion(docs_script, tmp_path):
    """A named document under `[exclude]` is accepted and written, and the
    reindex still leaves the excluded directory out — including the malformed
    file there that would otherwise fail it (M14 — A6)."""
    note = _doc("Vendored note")
    root = _tree(
        tmp_path,
        {
            "a.md": _doc("A"),
            "vendor/notes.md": note,
            "vendor/README.md": "a vendored readme with no H1 and no metadata\n",
        },
        sidecar_extra='\n[exclude]\ndirs = ["vendor"]\n',
    )

    proc = _run(docs_script, "lifecycle", "a.md", "vendor/notes.md", "active", "--root", str(root))

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert (root / "vendor" / "notes.md").read_text() == _promoted(note, to="active")
    index = (root / "INDEX.md").read_text()
    assert "- [a.md](a.md)" in index
    assert "vendor/" not in index


def test_lifecycle_plans_and_reports_a_duplicated_path_once(docs_script, tmp_path):
    """A document named twice — in two spellings — is one edit: one line, one
    record entry, and the same bytes as naming it once."""
    original = _doc("A")
    root = _tree(tmp_path, {"a.md": original})

    proc = _run(
        docs_script, "lifecycle", "a.md", "./a.md", "a.md", "active", "--root", str(root), "--json"
    )

    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert proc.stderr.count("docs: lifecycle: set a.md from draft to active") == 1, proc.stderr
    assert json.loads(proc.stdout)["edits"] == [
        {"path": "a.md", "before": "draft", "change": "set"}
    ]
    assert (root / "a.md").read_text() == _promoted(original, to="active")


# --- the primary use case ----------------------------------------------------


def test_milestone_setup_needs_no_hand_edit(docs_script, tmp_path):
    """The milestone's primary use case, end to end and unattended (stdin
    closed): scaffold a milestone trio with `docs new`, link it with
    `docs relate add`, promote all three with ONE `docs lifecycle`, and pass
    `docs check` — no file is edited outside a verb. Run again, the promotion
    writes nothing at all."""
    root = _tree(
        tmp_path,
        {
            "milestone-plan.md": _doc("Plan", lifecycle="active", role="plan", project="setup"),
            "charter.md": _doc("Charter", lifecycle="active", role="charter", project="setup"),
        },
        name="setup",
    )
    trio = ("feat.md", "feat-impl.md", "feat-test-matrix.md")
    steps: list[tuple[str, ...]] = [
        ("new", "milestone", "feat", "--quiet"),
        ("new", "log", "feat-impl", "--quiet"),
        ("new", "spec", "feat-test-matrix", "--quiet"),
    ]
    for source in trio:
        for target in trio:
            if source != target:
                steps.append(("relate", "add", source, "pairs-with", target, "--quiet"))
    steps.append(("relate", "add", "feat.md", "child-of", "milestone-plan.md", "--quiet"))
    steps.append(("relate", "add", "feat.md", "implements", "charter.md", "--quiet"))
    steps.append(("lifecycle", *trio, "active", "--quiet"))

    for step in steps:
        proc = _run(docs_script, *step, cwd=root)
        assert proc.returncode == 0, (step, proc.stdout, proc.stderr)

    for name in trio:
        assert "Lifecycle: active" in (root / name).read_text().splitlines(), name
    check = _run(docs_script, "check", str(root))
    assert check.returncode == 0, check.stdout + check.stderr

    settled = _snapshot(root)
    again = _run(docs_script, "lifecycle", *trio, "active", cwd=root)
    assert again.returncode == 0, (again.stdout, again.stderr)
    assert _snapshot(root) == settled, "a repeated promotion writes nothing, INDEX included"
