#!/usr/bin/env python3
"""Probe one `docs` executable against the docs-cli release contract.

Usage:
    python tests/manual/release_probe.py --docs <venv>/bin/docs --group all \\
        --expect-version 2.1.0 --repo . --scratch /path/outside/the/repo

Two groups of checks, each a black-box run of the executable on throwaway
trees built inline or copied from `<repo>/tests/fixtures/trees/` (or
`<repo>/docs`) into a fresh directory under `--scratch`:

  - contract (any executable): the 2.1 headline contracts, the Agent
    Playbook Suite's two capability probes exactly as its CI guard runs
    them, and the 2.0 contracts as regression;
  - distribution (`--group all`; wheel installs only): `docs --version`,
    `install-skill` byte identity, its no-op re-run, and the wheel-only
    `--symlink` refusal.

Expected values are quoted from `docs/cli.md`, the CHANGELOG, and the
product tests that pin each fixture, never from an executable's output.
Every 2.1-only exit-2 refusal also asserts its message, because older
releases exit 2 for an unknown verb or flag too.

Lives under `tests/manual/` so pytest does NOT collect it; the release
runbook runs it against every wheel it ships or rehearses. Stdlib-only;
every `docs` call runs with HOME and XDG state redirected under `--scratch`
and the update check disabled, so no run writes host state.

Prints one PASS/FAIL/SKIP line per check; exits 0 when nothing failed, 1
otherwise, 2 on a usage error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

_VERB_GROUP = re.compile(r"\{([a-z0-9,\-]+)\}")  # the Agent Playbook Suite guard's regex
Snapshot = dict[str, bytes]


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def isolated_env(tmp: Path) -> dict[str, str]:
    """The caller's environment with HOME and XDG state under `tmp`, update check off."""
    env = dict(os.environ)
    for key, sub in (("HOME", "home"), ("XDG_STATE_HOME", "state"), ("XDG_CACHE_HOME", "cache")):
        (tmp / sub).mkdir(parents=True, exist_ok=True)
        env[key] = str(tmp / sub)
    env.update(DOCS_CLI_NO_UPDATE_CHECK="1", PYTHONDONTWRITEBYTECODE="1")
    return env


def snapshot(root: Path) -> Snapshot:
    """Every file under `root`, `INDEX.md` and `.docs.toml` included."""
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def changed(before: Snapshot, after: Snapshot) -> list[str]:
    return sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))


def doc(title: str, *, lifecycle: str = "active", updated: str = "2026-05-20") -> str:
    return (
        f"# {title}\n\nLifecycle: {lifecycle}\nRole: notes\nProject: probe\n"
        f"Updated: {updated}\n\n## Body\n\nProse.\n"
    )


class Run:
    """One `docs` invocation's exit code and decoded streams."""

    def __init__(self, proc: subprocess.CompletedProcess[bytes], run_dir: Path) -> None:
        self.code = proc.returncode
        self.raw_out = proc.stdout
        self.out = proc.stdout.decode("utf-8", "replace")
        self.err = proc.stderr.decode("utf-8", "replace")
        self.run_dir = str(run_dir)

    def brief(self) -> str:
        """The exit code and last stderr line, with the run's scratch path masked."""
        tail = (self.err.strip().splitlines() or [""])[-1].replace(self.run_dir, "<run>")
        return f"exit {self.code}" + (f" ({tail})" if tail else "")


class Probe:
    """Runs the executable under test in throwaway trees beneath one run directory."""

    def __init__(self, docs: str, repo: Path, run_dir: Path) -> None:
        self.docs, self.repo, self.run_dir = docs, repo, run_dir
        self.env = isolated_env(run_dir / "env")
        self.trio: Path | None = None  # N1's tree, re-used by N2
        self.docs_copy: Path | None = None  # G1's tree, re-used by G2
        self.skill_dest = run_dir / "skill"

    def __call__(self, *args: str, cwd: Path) -> Run:
        return Run(
            subprocess.run(
                [self.docs, *args],
                cwd=cwd,
                env=self.env,
                capture_output=True,
                stdin=subprocess.DEVNULL,
                timeout=120,
            ),
            self.run_dir,
        )

    def tree(self, files: dict[str, str]) -> Path:
        root = Path(tempfile.mkdtemp(prefix="tree-", dir=self.run_dir))
        for rel, text in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
        return root

    def fixture(self, name: str) -> Path:
        source = self.repo / "tests" / "fixtures" / "trees" / name
        if not source.is_dir():
            raise FileNotFoundError(f"fixture tree {name} is missing")
        root = Path(tempfile.mkdtemp(prefix=f"{name}-", dir=self.run_dir)) / "tree"
        shutil.copytree(source, root)
        return root

    def unchanged(self, root: Path, before: Snapshot) -> str | None:
        diff = changed(before, snapshot(root))
        return f"wrote {diff}" if diff else None

    def refusal(self, run: Run, code: int, fragment: str) -> str | None:
        if run.code != code or fragment not in run.err:
            return f"{run.brief()}; expected exit {code} naming {fragment!r}"
        return None


Check = Callable[[Probe], str | None]


# --- contract group: new in 2.1 ---------------------------------------------


def trio_promoted(p: Probe) -> str | None:
    root = p.tree({".docs.toml": '[project]\nname = "probe"\n'})
    p.trio = root
    for argv in (
        ("new", "milestone", "m", "--quiet"),
        ("new", "log", "m-impl", "--quiet"),
        ("new", "spec", "m-test-matrix", "--quiet"),
        ("relate", "add", "m.md", "pairs-with", "m-impl.md"),
        ("relate", "add", "m.md", "pairs-with", "m-test-matrix.md"),
        ("lifecycle", "m.md", "m-impl.md", "m-test-matrix.md", "active"),
        ("check", "."),
    ):
        run = p(*argv, cwd=root)
        if run.code != 0:
            return f"`docs {' '.join(argv)}`: {run.brief()}"
    for name in ("m.md", "m-impl.md", "m-test-matrix.md"):
        if "Lifecycle: active" not in (root / name).read_text().splitlines():
            return f"{name} does not read Lifecycle: active"
    lines = (root / "m.md").read_text().splitlines()
    missing = [
        b for b in ("- pairs-with: m-impl.md", "- pairs-with: m-test-matrix.md") if b not in lines
    ]
    return f"m.md lacks {missing}" if missing else None


def promotion_rerun_is_noop(p: Probe) -> str | None:
    if p.trio is None:
        return "the promoted trio was not built"
    before = snapshot(p.trio)
    run = p("lifecycle", "m.md", "m-impl.md", "m-test-matrix.md", "active", cwd=p.trio)
    return run.brief() if run.code != 0 else p.unchanged(p.trio, before)


def freeform_edge_to_archived_target(p: Probe) -> str | None:
    old = "archive/2026-08-16/old.md"
    root = p.tree(
        {
            ".docs.toml": '[project]\nname = "probe"\n',
            "m.md": doc("M"),
            old: "# Old\n\nLifecycle: archived\nRole: notes\nProject: probe\n"
            "Updated: 2026-08-16\nArchived: 2026-08-16\n\n## Body\n\nHistory.\n",
        }
    )
    before = snapshot(root)
    run = p("relate", "add", "m.md", "references", old, cwd=root)
    if run.code != 0:
        return run.brief()
    diff = changed(before, snapshot(root))
    if "m.md" not in diff or not set(diff) <= {"m.md", "INDEX.md"}:
        return f"changed {diff}; expected m.md (and INDEX.md) only"
    bullet = f"- references: {old}"
    return None if bullet in (root / "m.md").read_text().splitlines() else f"m.md lacks {bullet!r}"


def lifecycle_refuses_archived(p: Probe) -> str | None:
    root = p.tree(
        {".docs.toml": '[project]\nname = "probe"\n', "a.md": doc("A", lifecycle="draft")}
    )
    before = snapshot(root)
    run = p("lifecycle", "a.md", "archived", cwd=root)
    fragment = "docs archive <file> moves lifecycle and location together"
    return p.refusal(run, 2, fragment) or p.unchanged(root, before)


def relate_refuses_out_of_grammar_verb(p: Probe) -> str | None:
    root = p.tree({".docs.toml": '[project]\nname = "probe"\n', "a.md": doc("A"), "b.md": doc("B")})
    before = snapshot(root)
    run = p("relate", "add", "a.md", "Pairs-With", "b.md", cwd=root)
    fragment = "a free-form verb matching [a-z][a-z0-9-]*"
    return p.refusal(run, 2, fragment) or p.unchanged(root, before)


def extension_state_read_back(p: Probe) -> str | None:
    root = p.fixture("vocab-extension")
    run = p("lifecycle", "draft-note.md", "shipped", cwd=root)
    if run.code != 0:
        return f"`docs lifecycle`: {run.brief()}"
    listing = p("list", "--json", cwd=root)
    if listing.code != 0:
        return f"`docs list --json`: {listing.brief()}"
    states = {r["path"]: r["lifecycle"] for r in json.loads(listing.out)}
    if states.get("draft-note.md") != "shipped":
        return f"docs list reports draft-note.md as {states.get('draft-note.md')!r}"
    index = p("index", cwd=root)
    return f"`docs index`: {index.brief()}" if index.code != 0 else None


def extension_role_in_index(p: Probe) -> str | None:
    root = p.fixture("vocab-extension")
    run = p("index", cwd=root)
    if run.code != 0:
        return run.brief()
    lines = (root / "INDEX.md").read_text().splitlines()
    if "### Active — Adr" not in lines:
        return "INDEX.md has no `### Active — Adr` group"
    group = lines[lines.index("### Active — Adr") + 1 :]
    group = group[: next((i for i, ln in enumerate(group) if ln.startswith("#")), len(group))]
    listed = any(ln.startswith("- [decision-record.md](decision-record.md)") for ln in group)
    return None if listed else "decision-record.md is not listed under `### Active — Adr`"


def relate_on_non_default_date_format(p: Probe) -> str | None:
    root = p.tree(
        {
            ".docs.toml": '[project]\nname = "probe"\n\n[archive]\ndate_format = "%d-%m-%Y"\n',
            "a.md": doc("A", updated="20-05-2026"),
            "b.md": doc("B", updated="21-05-2026"),
        }
    )
    run = p("relate", "add", "a.md", "precedes", "b.md", cwd=root)
    if run.code != 0:
        return run.brief()
    for name, bullet in (("a.md", "- precedes: b.md"), ("b.md", "- follows: a.md")):
        if bullet not in (root / name).read_text().splitlines():
            return f"{name} lacks {bullet!r}"
    check = p("check", ".", cwd=root)
    return f"`docs check`: {check.brief()}" if check.code != 0 else None


def stamp_refuses_out_of_vocabulary_block(p: Probe) -> str | None:
    root = p.tree(
        {".docs.toml": '[project]\nname = "probe"\n', "f.md": doc("F", lifecycle="activ")}
    )
    before = snapshot(root)
    run = p("stamp", "f.md", cwd=root)
    return p.refusal(run, 1, "refusing to re-stamp it") or p.unchanged(root, before)


# --- contract group: the Agent Playbook Suite's guard probes ----------------


def suite_guard_sees_lifecycle(p: Probe) -> str | None:
    run = p("--help", cwd=p.run_dir)
    match = _VERB_GROUP.search(run.out)
    if run.code != 0 or not match:
        return f"could not parse the verb list ({run.brief()})"
    verbs = match.group(1).split(",")
    return None if "lifecycle" in verbs else f"verb list {verbs} lacks lifecycle"


def suite_guard_freeform_dry_run(p: Probe) -> str | None:
    root = p.tree({".docs.toml": ""})
    for slug in ("a", "b"):
        made = p("new", "spec", slug, "--quiet", cwd=root)
        if made.code != 0:
            return f"`docs new spec {slug}`: {made.brief()}"
    before = snapshot(root)
    run = p("relate", "add", "a.md", "pairs-with", "b.md", "--dry-run", cwd=root)
    return run.brief() if run.code != 0 else p.unchanged(root, before)


# --- contract group: carried from 2.0 ---------------------------------------


def check_passes_on_docs_copy(p: Probe) -> str | None:
    root = Path(tempfile.mkdtemp(prefix="docs-", dir=p.run_dir)) / "docs"
    shutil.copytree(p.repo / "docs", root)
    p.docs_copy = root
    run = p("check", ".", cwd=root)
    return run.brief() if run.code != 0 else None


def index_dry_run_reproduces_docs_copy(p: Probe) -> str | None:
    if p.docs_copy is None:
        return "the docs-tree copy was not made"
    before = snapshot(p.docs_copy)
    run = p("index", ".", "--dry-run", cwd=p.docs_copy)
    if run.code != 0:
        return run.brief()
    if run.raw_out != before["INDEX.md"]:
        return "stdout differs from the copy's INDEX.md"
    return p.unchanged(p.docs_copy, before)


def check_records(p: Probe, fixture: str) -> tuple[Run, list[dict[str, str]]]:
    run = p("check", ".", "--json", cwd=p.fixture(fixture))
    return run, json.loads(run.out) if run.out.strip() else []


def one_sided_edge_is_missing_inverse(p: Probe) -> str | None:
    run, records = check_records(p, "reciprocal-missing")
    found = [(r["path"], r["message"]) for r in records if r["rule"] == "missing-inverse"]
    message = (
        "Related: 'precedes: b.md' has no inverse; "
        "b.md must declare 'follows: a.md' (or remove the edge)"
    )
    if run.code != 2 or found != [("a.md", message)]:
        return f"exit {run.code}, missing-inverse records {found}"
    return None


def bare_cascade_refused(p: Probe) -> str | None:
    root = p.fixture("archive-pair")
    before = snapshot(root)
    run = p("archive", "feature.md", "--cascade", cwd=root)
    fragment = "--cascade is retired in docs 2.0 and writes nothing"
    return p.refusal(run, 2, fragment) or p.unchanged(root, before)


def dead_prose_link_reported(p: Probe) -> str | None:
    run, records = check_records(p, "bodylink-broken")
    found = [(r["path"], r["rule"]) for r in records]
    if run.code != 2 or found != [("doc.md", "broken-body-link")]:
        return f"exit {run.code}, records {found}"
    return None if "plan.md" in records[0]["message"] else "the record does not name plan.md"


def mv_dry_run_names_rewrites(p: Probe) -> str | None:
    root = p.fixture("movelink-incoming")
    before = snapshot(root)
    run = p("mv", "plan.md", "milestone-plan.md", "--dry-run", cwd=root)
    expected = [
        "docs: mv: would move plan.md -> milestone-plan.md",
        "docs: mv: rewrite note.md:13 plan.md -> milestone-plan.md",
        "docs: mv: rewrite sub/deep.md:10 ../plan.md -> ../milestone-plan.md",
        "docs: mv: 2 destination(s) in 2 document(s), 1 Related: bullet(s)",
        "docs: mv: preview only — nothing was written",
    ]
    missing = [line for line in expected if line not in run.err]
    if run.code != 0 or missing:
        return f"{run.brief()}; missing {missing}"
    return p.unchanged(root, before)


def archive_reports_strands(p: Probe) -> str | None:
    root = p.fixture("movelink-closeout")
    run = p(
        "archive", "feature.md", "--cascade-only", "feature-*", "--date", "2026-08-15", cwd=root
    )
    summary = "docs: archive: 5 still-active inbound reference(s) into the archived set"
    return None if run.code == 0 and summary in run.err else f"{run.brief()}; expected {summary!r}"


def archive_records_date_on_every_member(p: Probe) -> str | None:
    root = p.fixture("archive-trio")
    run = p(
        "archive",
        "feature.md",
        "--cascade-only",
        "feature-*.md",
        "--reason",
        "trio closed out",
        "--date",
        "2026-03-04",
        cwd=root,
    )
    if run.code != 0:
        return run.brief()
    for name in ("feature.md", "feature-impl.md", "feature-test-matrix.md"):
        moved = root / "archive" / "2026-03-04" / name
        if not moved.is_file() or "Archived: 2026-03-04" not in moved.read_text().splitlines():
            return f"{moved.relative_to(root)} is missing or lacks Archived: 2026-03-04"
    return None


def mv_refuses_cross_dated_move(p: Probe) -> str | None:
    root = p.fixture("archivedate-two-dated-dirs")
    before = snapshot(root)
    run = p(
        "mv",
        "archive/2026-01-01/with-witness.md",
        "archive/2026-03-04/with-witness.md",
        cwd=root,
    )
    refusal = (
        "docs: mv: archive/2026-01-01/with-witness.md -> archive/2026-03-04/with-witness.md "
        "crosses dated archive directories (2026-01-01 to 2026-03-04); refusing before any write"
    )
    escape = (
        "docs: mv: the dated directory records when a document was archived; to correct a "
        "genuinely mis-dated archive, move the file by hand, correct its `Archived:` line, "
        "and re-run `docs check`"
    )
    lines = run.err.splitlines()
    if run.code != 2 or refusal not in lines or escape not in lines:
        return f"{run.brief()}; expected exit 2 with both refusal lines"
    return p.unchanged(root, before)


def relocated_archive_is_date_drift(p: Probe) -> str | None:
    run, records = check_records(p, "archivedate-drifted")
    found = [(r["path"], r["message"]) for r in records if r["rule"] == "archive-date-drift"]
    message = (
        "Archived: 2026-01-01 but the file is in archive/2026-03-04/ "
        "(move it back, or correct the recorded date)"
    )
    if run.code != 2 or found != [("archive/2026-03-04/moved.md", message)]:
        return f"exit {run.code}, archive-date-drift records {found}"
    return None


# --- distribution group (wheel installs) -------------------------------------


def version_is(expected: str) -> Check:
    def check(p: Probe) -> str | None:
        printed = p("--version", cwd=p.run_dir).out.rstrip("\n")
        return (
            None
            if printed == f"docs {expected}"
            else f"printed {printed!r}, expected 'docs {expected}'"
        )

    return check


def files_under(root: Path) -> dict[str, tuple[bytes, int]]:
    return {
        p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
        for p in sorted(root.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts
    }


def skill_materialised_identically(p: Probe) -> str | None:
    run = p("install-skill", "--dest", str(p.skill_dest), cwd=p.run_dir)
    if run.code != 0:
        return run.brief()
    want = {k: v[0] for k, v in files_under(p.repo / "src" / "docs_cli" / "skill").items()}
    have = {k: v[0] for k, v in files_under(p.skill_dest).items()}
    differ = changed(want, have)
    return f"{len(differ)} file(s) differ from the bundled skill: {differ}" if differ else None


def skill_rerun_is_noop(p: Probe) -> str | None:
    before = files_under(p.skill_dest)
    run = p("install-skill", "--dest", str(p.skill_dest), cwd=p.run_dir)
    if run.code != 0 or "no-op" not in run.err:
        return f"{run.brief()}; expected exit 0 reporting a no-op"
    return (
        None if files_under(p.skill_dest) == before else "the destination's bytes or mtimes moved"
    )


def symlink_refused_from_wheel(p: Probe) -> str | None:
    dest = p.run_dir / "skill-symlink"
    run = p("install-skill", "--dest", str(dest), "--symlink", cwd=p.run_dir)
    problem = p.refusal(run, 2, "wheel install")
    if problem is None and (dest.exists() or dest.is_symlink()):
        problem = "the destination was created"
    return problem


CONTRACT: list[tuple[str, Check]] = [
    (
        "A milestone trio scaffolded with docs new is linked with free-form edges and "
        "promoted to active in one call, and docs check passes",
        trio_promoted,
    ),
    ("Re-running the same promotion changes no file", promotion_rerun_is_noop),
    (
        "A free-form edge to an archived document needs no --reason and rewrites only its source",
        freeform_edge_to_archived_target,
    ),
    (
        "docs lifecycle refuses archived as a target, points at docs archive, and changes nothing",
        lifecycle_refuses_archived,
    ),
    (
        "An out-of-grammar relate verb is refused with the grammar named, and nothing changes",
        relate_refuses_out_of_grammar_verb,
    ),
    (
        "An extension lifecycle state set by docs lifecycle is read back by docs list and "
        "docs index",
        extension_state_read_back,
    ),
    ("An extension-role document appears in INDEX.md", extension_role_in_index),
    (
        "On a tree with a non-default date_format, relate links documents dated in that format",
        relate_on_non_default_date_format,
    ),
    (
        "docs stamp refuses a file whose complete block fails the configured vocabulary, "
        "writing nothing",
        stamp_refuses_out_of_vocabulary_block,
    ),
    (
        "The docs --help verb list names lifecycle, as the Agent Playbook Suite guard parses it",
        suite_guard_sees_lifecycle,
    ),
    (
        "A free-form dry-run relate on a fresh tree exits 0 and writes nothing, as the "
        "Agent Playbook Suite guard probes it",
        suite_guard_freeform_dry_run,
    ),
    (
        "docs check passes on a throwaway copy of this repository's docs tree",
        check_passes_on_docs_copy,
    ),
    (
        "docs index --dry-run on a copy of this docs tree reproduces its INDEX.md and "
        "writes nothing",
        index_dry_run_reproduces_docs_copy,
    ),
    (
        "A one-sided recognized edge is reported as missing-inverse",
        one_sided_edge_is_missing_inverse,
    ),
    ("Bare --cascade is refused and nothing changes", bare_cascade_refused),
    ("A dead prose link is reported as broken-body-link", dead_prose_link_reported),
    (
        "mv --dry-run names every planned reference rewrite and writes nothing",
        mv_dry_run_names_rewrites,
    ),
    (
        "Archiving reports the still-active inbound references into the archived set",
        archive_reports_strands,
    ),
    (
        "docs archive records the Archived: date on every moved member",
        archive_records_date_on_every_member,
    ),
    (
        "docs mv refuses a move between two dated archive directories and changes nothing",
        mv_refuses_cross_dated_move,
    ),
    (
        "A hand-relocated archived document is reported as archive-date-drift",
        relocated_archive_is_date_drift,
    ),
]
DISTRIBUTION: list[tuple[str, Check]] = [
    (
        "install-skill materialises a skill byte-identical to the repository's bundled skill",
        skill_materialised_identically,
    ),
    ("Re-running install-skill on an identical destination is a no-op", skill_rerun_is_noop),
    (
        "install-skill --symlink is refused from a wheel install, leaving the destination absent",
        symlink_refused_from_wheel,
    ),
]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Probe one docs executable against the docs-cli release contract."
    )
    parser.add_argument("--docs", required=True, help="the docs executable under test")
    parser.add_argument("--group", required=True, choices=("contract", "all"))
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--scratch", type=Path, required=True, help="a directory outside --repo")
    version = parser.add_mutually_exclusive_group()
    version.add_argument("--expect-version")
    version.add_argument("--no-version-check", action="store_true")
    args = parser.parse_args(argv)
    repo, scratch = args.repo.resolve(), args.scratch.resolve()
    docs = str(Path(args.docs).absolute())
    if not os.access(docs, os.X_OK):
        parser.error(f"--docs {args.docs} is not an executable")
    if scratch == repo or repo in scratch.parents:
        parser.error("--scratch must lie outside --repo")
    if args.group == "all" and not (args.expect_version or args.no_version_check):
        parser.error("--group all needs --expect-version or --no-version-check")
    scratch.mkdir(parents=True, exist_ok=True)

    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True
    )
    print(f"release_probe.py blob {git_blob_sha(Path(__file__))}")
    print(f"repo HEAD {head.stdout.strip() if head.returncode == 0 else 'unknown'}")
    print(f"docs {args.docs}")

    probe = Probe(docs, repo, Path(tempfile.mkdtemp(prefix="probe-", dir=scratch)))
    counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}

    def report(name: str, problem: str | None, skip: str | None = None) -> None:
        status = "SKIP" if skip else ("PASS" if problem is None else "FAIL")
        counts[status] += 1
        print(f"{status}  {name}" + (f" — {skip or problem}" if status != "PASS" else ""))

    def run_check(name: str, check: Check) -> None:
        try:
            problem = check(probe)
        except Exception as exc:  # a crashing executable is a failed check, not a crash
            problem = f"{type(exc).__name__}: {exc}"
        report(name, problem)

    for name, check in CONTRACT:
        run_check(name, check)
    if args.group == "all":
        version_name = "docs --version names the expected release"
        if args.no_version_check:
            report(version_name, None, skip="rehearsal-name install reports 0.0.0+local")
        else:
            run_check(version_name, version_is(args.expect_version))
        for name, check in DISTRIBUTION:
            run_check(name, check)

    print(f"{counts['PASS']} passed, {counts['FAIL']} failed, {counts['SKIP']} skipped")
    return 0 if counts["FAIL"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
