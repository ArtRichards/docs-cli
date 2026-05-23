"""Structural checks over the M5 Claude Code skill artifact.

M5 ships a `SKILL.md` markdown artifact, not a Python code surface. Its
correctness is verified by a **two-part oracle** (resolved OQ1):

1. This file — `tests/test_skill.py` — the *structural, automatable* half.
   It asserts the deterministic properties of the artifact: valid frontmatter
   carrying exactly `name` + `description`, a body within the skill-authoring
   size budget (a minimum non-blank-line floor and a maximum) that carries the
   never-hand-edit guardrail language, every one of `bin/docs`'s real verbs
   named as a `docs <verb>` inline-code span, every relative link resolves, and
   the skill directory carries no auxiliary clutter. It runs RED -> GREEN in CI
   with the rest of the suite: RED at Phase 4 against the Phase-1 stub body,
   GREEN at Phase 8 against the authored one.
2. The behavioural **trigger-scenario checklist** in
   `docs/m5-claude-code-skill-log.md` — the judgement half — a fixed table of
   "agent about to do X -> expected verb (or no trigger)" rows, walked by a
   human/agent at the Phase 9 dogfood pass.

The frontmatter is parsed by hand: this repo is stdlib-only (no `pyyaml`), and
the skill frontmatter is exactly two flat `key: value` lines, so a tiny
splitter is enough. `_split_frontmatter` enforces the `---` fence;
`_parse_frontmatter` splits the fenced lines into a dict.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pytest

from docs import _build_parser  # loaded via conftest's module registration

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "src" / "docs_cli" / "skill"
SKILL_MD = SKILL_DIR / "SKILL.md"


# --- helpers ---------------------------------------------------------------


def _read_skill() -> str:
    """Return the raw text of src/docs_cli/skill/SKILL.md."""
    return SKILL_MD.read_text(encoding="utf-8")


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split a SKILL.md into (frontmatter, body).

    The artifact must open with a `---` fence on its own first line and carry
    a matching closing `---` line; the text between the fences is the
    frontmatter, everything after the closing fence is the body. Raises
    AssertionError if the opening or closing fence is missing — a malformed
    artifact is a hard failure, not a silent empty parse.
    """
    lines = text.split("\n")
    assert lines and lines[0] == "---", "SKILL.md must open with a --- fence line"
    closing: int | None = None
    for i in range(1, len(lines)):
        if lines[i] == "---":
            closing = i
            break
    assert closing is not None, "SKILL.md frontmatter has no closing --- fence"
    frontmatter = "\n".join(lines[1:closing])
    body = "\n".join(lines[closing + 1 :])
    return frontmatter, body


def _parse_frontmatter(frontmatter: str) -> dict[str, str]:
    """Split fenced frontmatter into an ordered key -> value dict.

    Each non-blank line must be a flat `key: value` pair (split on the first
    `:`); both sides are stripped. Raises AssertionError on a line with no
    colon. dict preserves insertion order, so callers can check key order.
    """
    parsed: dict[str, str] = {}
    for line in frontmatter.split("\n"):
        if not line.strip():
            continue
        assert ":" in line, f"frontmatter line is not key: value -> {line!r}"
        key, _, value = line.partition(":")
        parsed[key.strip()] = value.strip()
    return parsed


# --- check 1: artifact exists and is frontmatter-fenced --------------------


def test_skill_md_exists_and_has_frontmatter() -> None:
    assert SKILL_MD.exists(), f"{SKILL_MD} does not exist"
    text = _read_skill()
    assert text.startswith("---\n"), "SKILL.md must start with a --- fence line"
    # A closing fence must exist — _split_frontmatter raises otherwise.
    _split_frontmatter(text)


# --- check 2: exactly name + description -----------------------------------


def test_frontmatter_has_exactly_name_and_description() -> None:
    frontmatter, _ = _split_frontmatter(_read_skill())
    parsed = _parse_frontmatter(frontmatter)
    assert set(parsed) == {"name", "description"}, (
        f"frontmatter must carry exactly name + description, got {sorted(parsed)}"
    )
    # name must be the first key, description the second (Claude Code reads
    # both, but the canonical authoring order is name then description).
    assert list(parsed) == ["name", "description"], (
        f"frontmatter keys must be in order [name, description], got {list(parsed)}"
    )


# --- check 3: name + description values are sane ---------------------------


def test_name_and_description_values_are_sane() -> None:
    frontmatter, _ = _split_frontmatter(_read_skill())
    parsed = _parse_frontmatter(frontmatter)
    assert parsed["name"] == "docs", f"skill name must be 'docs', got {parsed['name']!r}"
    description = parsed["description"]
    assert isinstance(description, str) and description.strip(), (
        "description must be a non-empty string"
    )
    assert "TODO" not in description, "description still carries the Phase-1 TODO placeholder"
    assert 20 <= len(description) <= 1024, (
        f"description length {len(description)} outside the sane 20..1024 window"
    )


# --- check 4: body present and within the size budget ----------------------


def test_body_is_present_and_within_size_budget() -> None:
    _, body = _split_frontmatter(_read_skill())
    assert body.strip(), "skill body is empty"
    line_count = len(body.split("\n"))
    assert line_count <= 500, (
        f"skill body is {line_count} lines — over the ~500-line authoring budget"
    )
    assert "TODO" not in body, "skill body still carries the Phase-1 TODO stub"
    # Lower bound: a real verb-redirecting body covering eight verbs, the
    # guardrail, and binary/root guidance cannot be a one-liner. Require a
    # genuine floor of non-blank lines so a stub body cannot pass.
    non_blank = [line for line in body.split("\n") if line.strip()]
    assert len(non_blank) >= 40, (
        f"skill body has only {len(non_blank)} non-blank lines — too thin to be "
        "the verb-redirecting body M5 requires (expected >= 40)"
    )
    # The never-hand-edit guardrail is M5's central instruction — the body must
    # carry it explicitly. Match a "hand-edit" / "hand edit" phrase, case-insensitively.
    assert re.search(r"hand[ -]edit", body, re.IGNORECASE), (
        "skill body is missing the never-hand-edit guardrail language "
        "(expected a 'hand-edit' / 'hand edit' phrase)"
    )


# --- check 5: every named verb is a real subcommand ------------------------


def test_every_named_verb_is_a_real_subcommand() -> None:
    parser = _build_parser()
    # The subparsers action carries dest="command"; its .choices maps every
    # registered verb name to its sub-parser.
    sub = next(
        a
        for a in parser._actions
        if isinstance(a, argparse._SubParsersAction) and a.dest == "command"
    )
    real_verbs = set(sub.choices.keys())
    assert real_verbs, "could not derive the real verb set from _build_parser()"

    _, body = _split_frontmatter(_read_skill())
    # Verb candidates come ONLY from backtick-delimited inline code spans of
    # the form `docs <verb>` (resolved OQ-C). Bare prose mentions are ignored.
    # The verb class is `[a-z]+` (no hyphen): all eight real verbs are plain
    # lowercase, and excluding `-` stops a span like `docs --root <dir> index`
    # from capturing `--root` as a bogus verb (resolved OQ-C author guidance).
    named: set[str] = set()
    for span in re.findall(r"`([^`]+)`", body):
        m = re.match(r"docs ([a-z]+)", span.strip())
        if m:
            named.add(m.group(1))

    unknown = named - real_verbs
    assert not unknown, f"skill body names non-existent docs verbs: {sorted(unknown)}"
    # Completeness guard: the milestone requires the body to redirect EVERY
    # real verb (the trigger checklist has one positive row per verb, and the
    # Deliverables demand all eight). Assert the full real-verb set is a subset
    # of the verbs named in the body.
    missing = real_verbs - named
    assert not missing, (
        f"skill body fails to name every real docs verb — missing {sorted(missing)} "
        f"(named {sorted(named & real_verbs)})"
    )


# --- check 6: every relative link resolves ---------------------------------


def test_every_relative_link_resolves() -> None:
    _, body = _split_frontmatter(_read_skill())
    # Markdown link targets: ](target). Cross-tree spec references are authored
    # as plain inline code (resolved OQ-B), so this governs only genuine
    # repo-internal links — likely none, or a link into a bundled references/.
    for target in re.findall(r"\]\(([^)]+)\)", body):
        if target.startswith(("http://", "https://", "mailto:", "/")):
            continue
        local = target.split("#", 1)[0]
        if not local:  # a pure #anchor
            continue
        resolved = (SKILL_DIR / local).resolve()
        assert resolved.exists(), f"relative link {target!r} does not resolve to a file"


# --- check 7: no clutter in the skill directory ----------------------------


def test_skill_dir_has_no_clutter() -> None:
    # ALLOWLIST (resolved OQ-D): the only permitted entries in the skill
    # source dir are SKILL.md and an optional references/ directory.
    for entry in sorted(SKILL_DIR.iterdir()):
        if entry.name == "SKILL.md" and entry.is_file():
            continue
        if entry.name == "references" and entry.is_dir():
            continue
        pytest.fail(f"unexpected entry in src/docs_cli/skill/: {entry.name}")


# --- check 8: the frontmatter parser is non-vacuous ------------------------


def test_frontmatter_parser_rejects_extra_keys() -> None:
    """Prove the shape checks (#1, #2) are real — bad input is rejected.

    Two failure modes are exercised: a frontmatter with no `---` fence (the
    `_split_frontmatter` contract), and a three-key frontmatter (which check #2
    rejects via its exactly-two-keys assertion).
    """
    # (a) Missing fence -> _split_frontmatter raises.
    with pytest.raises(AssertionError):
        _split_frontmatter("name: docs\ndescription: nope\n")

    # (b) A three-key frontmatter does NOT satisfy the exactly-name+description
    #     key set — so check #2's assertion is discriminating, not vacuous.
    three_key = "---\nname: docs\ndescription: x\nextra: y\n---\nbody\n"
    frontmatter, _ = _split_frontmatter(three_key)
    parsed = _parse_frontmatter(frontmatter)
    assert set(parsed) != {"name", "description"}, (
        "a three-key frontmatter must not pass the exactly-name+description check"
    )
