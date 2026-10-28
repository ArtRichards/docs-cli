#!/usr/bin/env python3
"""Check that a docs-cli source tree is ready to publish as one release.

Usage:
    python tests/manual/release_readiness.py --docs .venv/bin/docs --version 2.1.0 \\
        --release-date 2026-10-28 --changelog-base bf09748 \\
        --drop-sentence "A separate publish milestone ships it."

Reads the tree under `--repo` (default: this script's repository) and the
`--help` output of the `docs` executable under `--docs`:

  - `pyproject.toml` names docs-cli at the release version;
  - the newest CHANGELOG section is the release, dated, free of publish-state
    wording, and otherwise identical to its reviewed text at
    `--changelog-base`;
  - README.md lists every verb and sub-verb, each synopsis matches its
    `--help` usage in positional shape and flags (never in names), it does
    not mention Claude Code, and every GitHub file link points at the
    `pyproject.toml` Repository on `main` and names a file present both at
    HEAD and on `origin/main`;
  - the bundled `references/cli.md` and `references/convention.md` are
    byte-identical to `docs/`.

The references are the arguments, the reviewed CHANGELOG text, the `--help`
of `--docs`, `pyproject.toml`'s Repository URL and the local `origin/main`
ref; nothing under test is its own reference. Lives under
`tests/manual/` so pytest does NOT collect it; it is a pre-publish release
check. Stdlib-only and black-box: every `docs` call is a subprocess with
HOME and XDG state redirected to a temporary directory and the update check
disabled.

Prints one PASS/FAIL line per check; exits 0 when all pass, 1 otherwise,
2 on a usage error.
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

_PUBLISH_STATE = re.compile(
    r"unreleased|ready locally|not on pypi|publish milestone|deferred to m", re.IGNORECASE
)
_VERB_GROUP = re.compile(r"\{([a-z0-9,\-]+)\}")  # the Agent Playbook Suite guard's regex
_TOKEN = re.compile(r"\[[^\]]*\]|<[^>]+>(?:\.\.\.)?|\S+")
_SYNOPSIS_TOKEN = re.compile(r"^\[.*\]$|^<[^>]+>(\.\.\.)?$|^[A-Z][A-Z0-9_-]*$|^\.\.\.$")
_FLAG = re.compile(r"--[a-z][a-z0-9-]*")
_GITHUB_FILE_LINK = re.compile(
    r"https://github\.com/([^/\s]+/[^/\s]+)/(?:blob|tree)/([^/\s]+)/([^)\s#]+)"
)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def isolated_env(tmp: Path) -> dict[str, str]:
    """The caller's environment with HOME and XDG state under `tmp`, update check off.

    PYTHONPATH and PYTHONHOME are dropped, so the executable under test loads only
    its own installation.
    """
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")}
    for key, sub in (("HOME", "home"), ("XDG_STATE_HOME", "state"), ("XDG_CACHE_HOME", "cache")):
        (tmp / sub).mkdir(parents=True, exist_ok=True)
        env[key] = str(tmp / sub)
    env.update(DOCS_CLI_NO_UPDATE_CHECK="1", PYTHONDONTWRITEBYTECODE="1")
    return env


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


class Report:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def check(self, name: str, problem: str | None) -> None:
        if problem is None:
            self.passed += 1
            print(f"PASS  {name}")
        else:
            self.failed += 1
            print(f"FAIL  {name} — {problem}")


class Help:
    """`docs [words] --help` usage tokens, cached; the program name is dropped."""

    def __init__(self, docs: str, env: dict[str, str]) -> None:
        self.docs = docs
        self.env = env
        self._cache: dict[tuple[str, ...], list[str] | None] = {}

    def usage(self, *words: str) -> list[str] | None:
        if words not in self._cache:
            proc = subprocess.run(
                [self.docs, *words, "--help"],
                capture_output=True,
                text=True,
                env=self.env,
                stdin=subprocess.DEVNULL,
                timeout=120,
            )
            self._cache[words] = _usage_tokens(proc.stdout, words) if proc.returncode == 0 else None
        return self._cache[words]

    def sub_verbs(self, verb: str) -> list[str]:
        """The bare `{a,b}` group of `docs <verb> --help`, if the verb has sub-verbs."""
        for tok in self.usage(verb) or []:
            match = _VERB_GROUP.fullmatch(tok)
            if match:
                return match.group(1).split(",")
        return []


def _usage_tokens(text: str, words: tuple[str, ...]) -> list[str] | None:
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("usage:")), None)
    if start is None:
        return None
    block: list[str] = []
    for line in lines[start:]:
        if not line.strip():
            break
        block.append(line)
    tokens = _TOKEN.findall(" ".join(" ".join(block).split()))
    if tokens[2 : 2 + len(words)] != list(words):
        return None
    return tokens[2 + len(words) :]


def help_shape(tokens: list[str]) -> tuple[list[str], set[str]]:
    """Positional slots (S single, V variadic) and flag names of a usage line."""
    slots: list[str] = []
    flags: set[str] = set()
    run: list[str] = []
    for tok in tokens:
        if tok.startswith("["):
            flags.update(_FLAG.findall(tok))
            inner = tok[1:-1].split()
            # argparse renders nargs="+" as `M [M ...]`. A one-token M becomes
            # variadic; an M that already holds `...` keeps its own shape.
            if len(inner) == 2 and inner[1] == "..." and run[-1:] == inner[:1]:
                slots[-1] = "V"
            run = []
        elif tok == "...":
            if slots:
                slots[-1] = "V"
            run.append(tok)
        else:
            slots.append("S")
            run.append(tok)
    return slots, flags


def readme_shape(tokens: list[str]) -> tuple[list[str], set[str]]:
    """Positional slots and flag names of a README synopsis, up to its description."""
    slots: list[str] = []
    flags: set[str] = set()
    for tok in tokens:
        if not _SYNOPSIS_TOKEN.match(tok):
            break
        if tok.startswith("["):
            flags.update(_FLAG.findall(tok))
        elif tok == "...":
            if slots:
                slots[-1] = "V"
        else:
            slots.append("V" if tok.endswith("...") else "S")
    return slots, flags


def readme_synopses(readme: str) -> list[str]:
    """Lines starting `docs ` in the first fenced block after `## Commands`."""
    lines = readme.splitlines()
    if "## Commands" not in lines:
        return []
    rest = lines[lines.index("## Commands") + 1 :]
    fences = [i for i, line in enumerate(rest) if line.startswith("```")]
    if len(fences) < 2:
        return []
    return [line for line in rest[fences[0] + 1 : fences[1]] if line.startswith("docs ")]


def changelog_section(text: str, version: str) -> str | None:
    """The body of the first `## <version>` section, heading excluded."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line == f"## {version}" or line.startswith(f"## {version} "):
            end = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("## ")), None)
            return "\n".join(lines[i + 1 : end])
    return None


def check_changelog(report: Report, args: argparse.Namespace, repo: Path) -> None:
    text = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    expected = f"## {args.version} — {args.release_date}"
    first = next((line for line in text.splitlines() if line.startswith("## ")), None)
    report.check(
        f"The newest CHANGELOG section is the release, dated {args.release_date}",
        None if first == expected else f"first heading {first!r}, expected {expected!r}",
    )
    body = changelog_section(text, args.version)
    claims = [] if body is None else [ln for ln in body.splitlines() if _PUBLISH_STATE.search(ln)]
    claim: str | None
    if body is None:
        claim = f"no `## {args.version}` section"
    elif args.drop_sentence and args.drop_sentence in body:
        claim = f"still says {args.drop_sentence!r}"
    else:
        claim = f"publish-state wording: {claims[0]!r}" if claims else None
    report.check("The release's CHANGELOG section makes no publish-state claim", claim)

    base = git(repo, "show", f"{args.changelog_base}:CHANGELOG.md")
    base_body = changelog_section(base.stdout, args.version) if base.returncode == 0 else None
    if body is None or base_body is None:
        drift: str | None = f"section missing here or at {args.changelog_base}"
    else:
        # An empty --drop-sentence means the release removes nothing.
        drop = " " + args.drop_sentence if args.drop_sentence else None
        ours = body.replace(drop, "") if drop else body
        theirs = base_body.replace(drop, "") if drop else base_body
        diff = difflib.unified_diff(theirs.splitlines(), ours.splitlines(), n=0, lineterm="")
        changed = [d for d in list(diff)[2:] if not d.startswith("@@")]
        drift = "; ".join(changed[:4]) if changed else None
    report.check(
        "The release's CHANGELOG section matches its reviewed text apart from the heading "
        "and the dropped sentence",
        drift,
    )


def check_readme(report: Report, docs_help: Help, repo: Path, repository: str) -> None:
    readme = (repo / "README.md").read_text(encoding="utf-8")
    top = docs_help.usage() or []
    group = next((m for m in map(_VERB_GROUP.fullmatch, top) if m), None)
    verbs = group.group(1).split(",") if group else []
    required: set[tuple[str, str | None]] = {(v, None) for v in verbs}
    required |= {(v, s) for v in verbs for s in docs_help.sub_verbs(v)}

    listed: set[tuple[str, str | None]] = set()
    parsed: list[tuple[str, list[str], list[str]]] = []
    for line in readme_synopses(readme):
        tokens = _TOKEN.findall(line)
        verb, rest = tokens[1], tokens[2:]
        has_subs = rest and verb in verbs and docs_help.sub_verbs(verb)
        subs = rest.pop(0).split("|") if has_subs else []
        listed |= {(verb, None)} | {(verb, s) for s in subs}
        parsed.append((verb, subs, rest))

    missing = sorted(" ".join(w for w in pair if w) for pair in required - listed)
    if not verbs:
        absent: str | None = "could not parse the verb list from `docs --help`"
    else:
        absent = f"no synopsis for: {', '.join(missing)}" if missing else None
    report.check("README.md lists every docs verb and sub-verb", absent)
    for verb, subs, rest in parsed:
        label = " ".join(["docs", verb, *(["|".join(subs)] if subs else [])])
        slots, flags = readme_shape(rest)
        problems = []
        variants: list[tuple[str, ...]] = [(verb, s) for s in subs] or [(verb,)]
        for words in variants:
            usage = docs_help.usage(*words)
            if usage is None:
                problems.append(f"`docs {' '.join(words)} --help` gave no usage")
                continue
            want, have = help_shape(usage)
            if slots != want or not flags <= have:
                extra = sorted(flags - have)
                problems.append(
                    f"README {slots} vs `docs {' '.join(words)}` usage {want}"
                    + (f"; flags not in usage: {extra}" if extra else "")
                )
        report.check(
            f"README.md synopsis for `{label}` matches `{label} --help`",
            "; ".join(problems) or None,
        )

    mentions = readme.count("Claude Code")
    report.check(
        "README.md does not mention Claude Code",
        f"{mentions} mention(s)" if mentions else None,
    )
    links = sorted(set(_GITHUB_FILE_LINK.findall(readme)))
    home = repository.removesuffix("/").removesuffix(".git")
    slug = home.removeprefix("https://github.com/")
    if slug == home:
        stray = [f"pyproject.toml's Repository URL {repository!r} is not on github.com"]
    else:
        stray = sorted({f"{s}/{ref}" for s, ref, _ in links if (s, ref) != (slug, "main")})
    report.check(
        "Every README.md GitHub file link points at the pyproject Repository on main",
        f"links elsewhere: {stray}" if stray else None,
    )
    paths = sorted({path for _, _, path in links})
    for ref, where in (("HEAD", "tracked at HEAD"), ("origin/main", "on origin/main")):
        dead = [p for p in paths if git(repo, "cat-file", "-e", f"{ref}:{p}").returncode != 0]
        report.check(
            f"Every README.md GitHub file link names a file {where}",
            f"missing at {ref}: {dead}" if dead else None,
        )


def _iso_date(text: str) -> str:
    try:
        datetime.date.fromisoformat(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"not a YYYY-MM-DD date: {text!r}") from exc
    return text


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Check that a docs-cli source tree is ready to publish as one release."
    )
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--docs", required=True, help="the docs executable whose --help is read")
    parser.add_argument("--version", required=True)
    parser.add_argument("--release-date", required=True, type=_iso_date)
    parser.add_argument("--changelog-base", required=True, help="commit holding reviewed text")
    parser.add_argument(
        "--drop-sentence",
        required=True,
        help='the publish-state sentence the release removes; "" when it removes none',
    )
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    docs = str(Path(args.docs).absolute())
    if not os.access(docs, os.X_OK):
        parser.error(f"--docs {args.docs} is not an executable")

    head = git(repo, "rev-parse", "HEAD")
    print(f"release_readiness.py blob {git_blob_sha(Path(__file__))}")
    print(f"repo HEAD {head.stdout.strip() if head.returncode == 0 else 'unknown'}")
    print(f"docs {args.docs}")

    report = Report()
    project = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    found = (project.get("name"), project.get("version"))
    report.check(
        "pyproject.toml declares docs-cli at the release version",
        None if found == ("docs-cli", args.version) else f"name/version {found}",
    )
    check_changelog(report, args, repo)
    with tempfile.TemporaryDirectory() as tmp:
        repository = project.get("urls", {}).get("Repository", "")
        check_readme(report, Help(docs, isolated_env(Path(tmp))), repo, repository)
    for name in ("cli.md", "convention.md"):
        bundled = repo / "src" / "docs_cli" / "skill" / "references" / name
        same = bundled.read_bytes() == (repo / "docs" / name).read_bytes()
        report.check(
            f"Bundled references/{name} is byte-identical to docs/{name}",
            None if same else "the bytes differ",
        )

    print(f"{report.passed} passed, {report.failed} failed")
    return 0 if report.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
