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
`_parse_frontmatter` splits the fenced lines into a dict. Because the
splitter is more lenient than the YAML loaders that read the skill,
`_yaml_scalar_problem` also checks that each value is a scalar YAML reads
back verbatim (no `: ` or ` #` in a plain scalar, no indicator opening it).
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
    # The verb class is `[a-z][a-z-]*`: real verbs are lowercase and may
    # include `-` (M6's `install-skill`). The leading `[a-z]` requirement
    # stops a span like `docs --root <dir> index` from capturing `--root`
    # as a bogus verb (resolved OQ-C author guidance).
    named: set[str] = set()
    for span in re.findall(r"`([^`]+)`", body):
        m = re.match(r"docs ([a-z][a-z-]*)", span.strip())
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


# --- check 9: every frontmatter value is a scalar YAML reads back verbatim --

# Characters that may not open a YAML plain scalar (YAML 1.2, section 7.3.3).
_YAML_INDICATORS = frozenset("-?:,[]{}#&*!|>'\"%@`")


def _yaml_scalar_problem(value: str) -> str | None:
    """Why `value`, written after `key: ` on one line, is not read back verbatim by YAML.

    Stdlib only: the repo has no YAML parser, but skill loaders read the
    frontmatter as YAML, and the flat splitter above accepts lines YAML
    rejects. A value opening with a quote is a quoted scalar and must close
    with the same quote. Anything else is a plain scalar. YAML rejects or
    silently rewrites a plain scalar that:
    - opens with an indicator character (`-`, `?` and `:` are allowed when a
      non-space follows);
    - contains `: `, or ends with `:` (a nested mapping);
    - contains ` #` (the rest becomes a comment).
    Returns None when the value is safe.
    """
    first = value[:1]
    if first in ("'", '"'):
        return None if len(value) >= 2 and value.endswith(first) else "an unclosed quoted scalar"
    opens_safely = first in ("-", "?", ":") and value[1:2] not in ("", " ")
    if first in _YAML_INDICATORS and not opens_safely:
        return f"a plain scalar opening with the YAML indicator {first!r}"
    if ": " in value or value.endswith(":"):
        return "a plain scalar containing ': ', which YAML reads as a nested mapping"
    if " #" in value:
        return "a plain scalar containing ' #', which YAML reads as the start of a comment"
    return None


def test_frontmatter_values_are_scalars_yaml_reads_back_verbatim() -> None:
    """Skill loaders parse the frontmatter as YAML, so each value must survive
    a YAML load unchanged. An unquoted description containing `: ` passes the
    flat splitter but makes every YAML-based loader reject the skill."""
    frontmatter, _ = _split_frontmatter(_read_skill())
    problems = {
        key: problem
        for key, value in _parse_frontmatter(frontmatter).items()
        if (problem := _yaml_scalar_problem(value)) is not None
    }
    assert not problems, f"frontmatter values a YAML loader would reject or rewrite: {problems}"


@pytest.mark.parametrize(
    ("value", "accepted"),
    [
        ("link docs with a Related edge", True),
        ("link docs with a Related: edge", False),
        ("ends with a colon:", False),
        ("see the docs #later", False),
        ("[a list]", False),
        ("&anchor x", False),
        ("- a dash item", False),
        ("-x is fine", True),
        ("50% done", True),
        ('"a quoted: value"', True),
        ("'unclosed", False),
    ],
    ids=[
        "plain-text",
        "colon-space",
        "trailing-colon",
        "space-hash",
        "opening-bracket",
        "opening-anchor",
        "opening-dash-and-space",
        "dash-then-text",
        "percent-inside",
        "quoted-colon-space",
        "unclosed-quote",
    ],
)
def test_yaml_scalar_check_rejects_exactly_what_a_yaml_loader_would_break(
    value: str, accepted: bool
) -> None:
    """The check is not vacuous: it rejects the values a YAML loader refuses or
    silently rewrites, and accepts ordinary prose and quoted scalars."""
    assert (_yaml_scalar_problem(value) is None) is accepted


# --- M25 — the bundled skill must teach `docs relate` ----------------------


def test_skill_md_documents_relate_verb() -> None:
    """M25: the bundled skill's verb table and trigger description name `relate`.

    Intended RED until Phase 7 — the verb does not exist yet, so the surface
    parity gate (bundled skill updated in the SAME change as the CLI surface)
    has nothing to mirror at Phase 2. The existing
    `test_every_named_verb_is_a_real_subcommand` completeness guard would
    ALSO start failing the moment `relate` is registered without this edit;
    this test names the requirement explicitly so it cannot be mistaken for
    an incidental break.
    """
    frontmatter, body = _split_frontmatter(_read_skill())
    meta = _parse_frontmatter(frontmatter)

    assert "relate" in meta["description"], (
        "the skill's `description:` verb list must name `relate` so the skill "
        "triggers on relationship repair"
    )

    table_rows = [line for line in body.split("\n") if line.startswith("|")]
    assert any("`docs relate" in row for row in table_rows), (
        "the skill body's verb table must carry a `docs relate` row"
    )


# --- M26 — the bundled skill must teach safe archive selection -------------


_BARE_CASCADE = re.compile(r"--cascade(?![-\w])")


def test_skill_md_teaches_safe_archive_selection() -> None:
    """M26 — D8 surface parity: the bundled skill's archive row must teach the
    two safe flags and must NOT prescribe the retired bare `--cascade`.

    `SKILL.md`'s archive row currently reads
    `| Archive a finished doc | \\`docs archive <file>\\` | \\`--reason\\`,
    \\`--date\\`, \\`--cascade\\` |` — i.e. the shipped skill actively recommends
    the invocation M26 retires. An agent reading it would write a command
    that now refuses with exit 2, which is exactly the ecosystem risk the
    milestone names.

    The rule is deliberately absolute: the row may not name bare `--cascade`
    even to mark it retired. The flags column is read as a prescription, the
    retirement is documented at length in `cli.md`, and `references/cli.md`
    ships alongside — so the skill row's job is to teach the safe flow, not to
    carry an obituary.

    Intended RED until Phase 7 (the bundled skill lands in the SAME change as
    the CLI surface; there is nothing to mirror at Phase 2).
    """
    _frontmatter, body = _split_frontmatter(_read_skill())
    archive_rows = [
        line for line in body.split("\n") if line.startswith("|") and "docs archive" in line
    ]
    assert archive_rows, "the skill body's verb table must carry a `docs archive` row"
    joined = "\n".join(archive_rows)

    assert "--cascade-dry-run" in joined, (
        "the archive row must teach `--cascade-dry-run` — previewing the "
        "neighborhood is now the first step of every multi-doc archive"
    )
    assert "--cascade-only" in joined, (
        "the archive row must teach `--cascade-only GLOB` — the only way to "
        "write a related document"
    )
    # `_BARE_CASCADE` matches `--cascade` NOT followed by `-` or a word
    # character, so `--cascade-only` and `--cascade-dry-run` never trip it.
    assert not _BARE_CASCADE.search(joined), (
        "the archive row must not NAME bare `--cascade` at all: the row's flag "
        "column is a prescription, and an agent skimming the table would read "
        "any mention there as a suggestion. It is retired in docs 2.0 and "
        f"refuses with exit 2. Got: {joined!r}"
    )


def test_bundled_use_cases_teaches_safe_archive_selection() -> None:
    """M26 — D8: the shipped use-case catalog carries the same prescription.

    `references/use-cases.md` currently says "`--cascade` opt-in for one-hop
    dependents" — the second place the retired flag is recommended to an
    agent.

    Intended RED until Phase 7.
    """
    text = (SKILL_DIR / "references" / "use-cases.md").read_text()
    archive_rows = [
        line for line in text.split("\n") if line.startswith("|") and "docs archive" in line
    ]
    assert archive_rows, "use-cases.md must carry a `docs archive` row"
    joined = "\n".join(archive_rows)

    assert "--cascade-only" in joined, "the archive row must name the scoped write"
    assert not _BARE_CASCADE.search(joined), (
        f"use-cases.md must not prescribe bare `--cascade`. Got: {joined!r}"
    )


# --- M27 — the bundled skill must teach body-link validation ---------------


def test_skill_md_teaches_body_link_validation() -> None:
    """M27 — D7 surface parity: the skill's `docs check` row must name BOTH new
    hard errors.

    The row currently teaches `missing-inverse` and `duplicate-field` and says
    nothing about prose links, so an agent reading it would not know that a
    2.0 `docs check` can now fail on a body link at all — and would have no
    idea which of the two repairs (rebase the destination, or use a URL) the
    finding is asking for. The flags column of that table is read as a
    prescription, which is precisely why the rule ids belong in it.

    Intended RED until Phase 7 (the bundled skill lands in the SAME change as
    the CLI surface; there is nothing to mirror at Phase 2).
    """
    _frontmatter, body = _split_frontmatter(_read_skill())
    check_rows = [
        line for line in body.split("\n") if line.startswith("|") and "docs check" in line
    ]
    assert check_rows, "the skill body's verb table must carry a `docs check` row"
    joined = "\n".join(check_rows)

    assert "broken-body-link" in joined, (
        "the check row must name `broken-body-link` — a missing local body-link "
        "destination is a hard error from 2.0"
    )
    assert "outside-root-body-link" in joined, (
        "the check row must name `outside-root-body-link` — a destination that "
        "leaves the tree root is its own hard error, with a different repair"
    )


def test_bundled_use_cases_teaches_body_link_repair() -> None:
    """M27 — D7: the shipped use-case catalog carries the same prescription,
    and names the TWO repairs an adopter faces.

    `references/use-cases.md`'s "Validate in CI" row lists what `docs check`
    reports; it must include body links. The catalog is also where an upgrading
    adopter looks for the recipe, so both repairs must be findable: rebase the
    destination for `broken-body-link`, use a URL for `outside-root-body-link`.

    Intended RED until Phase 7.
    """
    text = (SKILL_DIR / "references" / "use-cases.md").read_text()

    check_rows = [
        line for line in text.split("\n") if line.startswith("|") and "docs check" in line
    ]
    assert check_rows, "use-cases.md must carry a `docs check` row"
    assert "body link" in "\n".join(check_rows).lower(), (
        "the validate row must say body links are now checked"
    )

    assert "broken-body-link" in text, "the catalog must name the rule id an adopter will see"
    assert "outside-root-body-link" in text, "…and the second one, whose repair is different"
    assert "URL" in text, "the outside-root repair is to use a URL, and it must be spelled out"


# --- M28 — the bundled skill must teach move-safe link rewrites ------------


def test_skill_md_teaches_move_safe_link_rewrites() -> None:
    """M28 — D8 surface parity: the skill's `docs mv` and `docs archive` rows
    must say that a move now rewrites prose destinations, and that an archive
    can refuse.

    Both are behaviour changes an agent has to know BEFORE it invokes the verb:
    a move now writes bytes into documents the agent did not name, and a
    `docs archive` that used to complete can now exit 2. An agent reading only
    the current rows would be surprised by both.

    Intended RED until Phase 7 (the bundled skill lands in the SAME change as
    the CLI surface; there is nothing to mirror at Phase 2).
    """
    _frontmatter, body = _split_frontmatter(_read_skill())
    rows = [line for line in body.split("\n") if line.startswith("|")]
    mv_rows = "\n".join(line for line in rows if "docs mv" in line)
    archive_rows = "\n".join(line for line in rows if "docs archive" in line)

    assert mv_rows, "the skill body's verb table must carry a `docs mv` row"
    assert archive_rows, "the skill body's verb table must carry a `docs archive` row"

    assert "body link" in mv_rows.lower() or "prose link" in mv_rows.lower(), (
        "the mv row must say the move rebases body links, not just Related: edges"
    )
    assert "--dry-run" in mv_rows and "--json" in mv_rows, (
        "the mv row must name BOTH halves of its new surface (D7) — an `or` here "
        "would let Phase 7 document one and skip the other"
    )
    assert "child-of" in archive_rows, (
        "the archive row must name the strand refusal's predicate, so an agent "
        "knows which shape exits 2 before it runs the write"
    )


def test_bundled_use_cases_teaches_the_move_rewrite_and_the_strand_check() -> None:
    """M28 — D7/D8: the shipped use-case catalog carries the same prescription.

    The catalog is where an agent looks for the closeout recipe, so it is where
    the two new facts belong: the closeout now leaves the tracker resolving,
    and a plan that would strand a live child refuses.

    Intended RED until Phase 7.
    """
    text = (SKILL_DIR / "references" / "use-cases.md").read_text()
    rows = [line for line in text.split("\n") if line.startswith("|")]
    joined = "\n".join(rows)

    assert "body link" in joined.lower() or "prose link" in joined.lower(), (
        "the catalog must say a coordinated move rebases body links"
    )
    assert "child-of" in joined, (
        "the catalog must name the strand refusal, which is the one case where a "
        "previously-completing archive now exits 2"
    )


# --- M28a — the bundled skill must teach the witness and the refusal -------


def test_skill_md_teaches_the_archive_date_witness_and_the_mv_refusal() -> None:
    """M28a — D9 surface parity: the skill's `docs archive` and `docs mv` rows
    must name the witness and the refusal.

    Both are things an agent has to know BEFORE it invokes the verb: an archive
    now writes a field the agent did not ask for, and a `docs mv` that used to
    complete now exits 2. An agent reading only the current rows would be
    surprised by the second and would not know the first exists.

    Intended RED until Phase 7 (the bundled skill lands in the SAME change as
    the CLI surface; there is nothing to mirror at Phase 2).
    """
    _frontmatter, body = _split_frontmatter(_read_skill())
    rows = [line for line in body.split("\n") if line.startswith("|")]
    archive_rows = "\n".join(line for line in rows if "docs archive" in line)
    mv_rows = "\n".join(line for line in rows if "docs mv" in line)

    assert archive_rows, "the skill body's verb table must carry a `docs archive` row"
    assert mv_rows, "the skill body's verb table must carry a `docs mv` row"

    assert "Archived:" in archive_rows, (
        "the archive row must name the field the verb now writes, by its exact label"
    )
    assert "refus" in mv_rows.lower(), (
        "the mv row must say a cross-dated archived relocation now REFUSES — "
        "the milestone's one behaviour change"
    )
    assert "archive" in mv_rows.lower(), (
        "…and must say which moves it applies to, or the refusal reads as universal"
    )


def test_bundled_use_cases_teaches_the_archive_date_witness() -> None:
    """M28a — D9: the shipped use-case catalog carries the same prescription.

    The catalog is where an agent looks for the closeout recipe, so it is where
    the two new facts belong: a closeout now records the archive date on every
    member it moves, and `docs check` reports a document whose location
    contradicts it.

    Intended RED until Phase 7.
    """
    text = (SKILL_DIR / "references" / "use-cases.md").read_text()
    assert "Archived:" in text, "the catalog must name the field a closeout now writes"
    assert "archive-date-drift" in text, (
        "…and the rule id an adopter will see in `docs check` output"
    )


def test_argparse_help_teaches_the_archive_date_witness_and_the_mv_refusal() -> None:
    """M28a — D9 surface parity, at the argparse layer this time.

    The milestone's *Testing and quality gate* names `docs archive --help` /
    `docs check --help` / `cli.md` surface parity, and D9 says the argparse
    surface must describe the same behaviour as the specs and the skill. M28a
    adds no flag, so nothing in the option set moves — which is exactly why
    the `description` strings are the only thing that can carry the change,
    and why nothing else in the suite would notice one going missing.

    All three verbs are asserted, because the one that was silently dropped
    at Phase 7 was `archive` — the verb that WRITES the field.
    """
    parser = _build_parser()
    sub = next(
        a
        for a in parser._actions
        if isinstance(a, argparse._SubParsersAction) and a.dest == "command"
    )

    archive_help = sub.choices["archive"].description or ""
    assert "Archived:" in archive_help, (
        "`docs archive --help` must name the field the verb now writes, by its exact label"
    )
    assert "EVERY" in archive_help or "every" in archive_help, (
        "…and must say it lands on every document the operation moves, not the primary only"
    )

    mv_help = sub.choices["mv"].description or ""
    assert "REFUSES" in mv_help or "refuses" in mv_help, (
        "`docs mv --help` must say a cross-dated archived relocation now refuses — "
        "the milestone's one behaviour change, and a move that used to exit 0"
    )
    assert "archive" in mv_help.lower(), (
        "…and must say which moves it applies to, or the refusal reads as universal"
    )

    check_help = sub.choices["check"].description or ""
    assert "Archived:" in check_help, "`docs check --help` must name the rule's subject field"
    assert "archived document" not in check_help, (
        "the rule is NOT limited to archived documents — Q7's motivating case is a "
        "document moved OUT of the archive whose Lifecycle: was then hand-edited, "
        "where status-drift is silent. Both specs say 'a document'."
    )


# --- lifecycle and free-form edges are routed through verbs -----------------
#
# Milestone `lifecycle-and-free-form-relate` — D9's surface parity (the task
# plan's *Decisions (Phase 1 — BINDING)* › P1.8): the bundled skill lands in
# the SAME change as the CLI surface, so these are RED until Phase 7.


def _section(body: str, heading: str) -> str:
    """The text of the `## <heading>` section of `body`, up to the next `## `."""
    start = body.index(f"## {heading}\n")
    end = body.find("\n## ", start + 1)
    return body[start:] if end == -1 else body[start:end]


def test_skill_routes_lifecycle_and_free_form_edges_through_verbs() -> None:
    """The skill names `docs lifecycle` and free-form `docs relate` as the
    routes for the two edits it used to leave without a verb: its description,
    its verb table, *Three things never to hand-edit*, the *Quality artifacts*
    guidance for linking a report, and the bundled use-case catalog."""
    frontmatter, body = _split_frontmatter(_read_skill())
    description = _parse_frontmatter(frontmatter)["description"]
    assert "lifecycle" in description, "the description's verb list must name `lifecycle`"

    rows = [line for line in body.split("\n") if line.startswith("|")]
    assert any("`docs lifecycle" in row for row in rows), "the verb table needs a lifecycle row"
    relate_rows = "\n".join(row for row in rows if "docs relate" in row)
    assert "free-form" in relate_rows, "the relate row must cover free-form edges"

    never = _section(body, "Three things never to hand-edit")
    assert "docs lifecycle" in never, "the hand-edit guardrail must route lifecycle to its verb"
    assert "docs relate" in never, "…and free-form `Related:` edits to `docs relate`"

    quality = _section(body, "Quality artifacts")
    assert "docs relate add" in quality, "a generated report is linked with `docs relate add`"
    linking = (SKILL_DIR / "references" / "quality-artifacts.md").read_text()
    assert "docs relate add" in _section(linking, "Linking reports")

    catalog = (SKILL_DIR / "references" / "use-cases.md").read_text()
    catalog_rows = [line for line in catalog.split("\n") if line.startswith("|")]
    assert any("`docs lifecycle" in row for row in catalog_rows), "a lifecycle use-case row"
    assert any("docs relate add" in row and "free-form" in row for row in catalog_rows), (
        "a free-form edge use-case row"
    )


_STALE_PHRASES = (
    "free-form verbs stay hand-edited",
    "refuses to edit them",
    "Only the six recognized verbs",
)


def test_shipped_surface_no_longer_says_free_form_verbs_are_hand_edited() -> None:
    """Nothing an agent reads — the bundled skill and its references, or the
    `docs relate` help text — may still say free-form edges are hand-edits,
    and the help must name the free-form grammar it now enforces."""
    offenders = [
        f"{md.relative_to(SKILL_DIR).as_posix()}: {phrase!r}"
        for md in sorted(SKILL_DIR.rglob("*.md"))
        for phrase in _STALE_PHRASES
        if phrase in " ".join(md.read_text(encoding="utf-8").split())
    ]

    parser = _build_parser()
    sub = next(
        a
        for a in parser._actions
        if isinstance(a, argparse._SubParsersAction) and a.dest == "command"
    )
    relate = sub.choices["relate"]
    helps = {"docs relate --help": relate.format_help()}
    relate_sub = next(a for a in relate._actions if isinstance(a, argparse._SubParsersAction))
    for action in ("add", "remove"):
        helps[f"docs relate {action} --help"] = relate_sub.choices[action].format_help()
    offenders += [
        f"{name}: {phrase!r}"
        for name, text in helps.items()
        for phrase in _STALE_PHRASES
        if phrase in " ".join(text.split())
    ]
    assert not offenders, "stale hand-edit wording ships:\n" + "\n".join(offenders)

    for action in ("add", "remove"):
        text = helps[f"docs relate {action} --help"]
        assert "[a-z][a-z0-9-]*" in text, f"`docs relate {action} --help` must name the grammar"
