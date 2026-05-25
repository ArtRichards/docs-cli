"""RED-baseline tests for M8 F8 — skill adoption playbook + .docs.toml template.

Phase 2 of M8. The bundled skill (M5/M6) targets greenfield use; M8
extends it with adoption-flow guidance. Per the F8 design rule
(operator decision 2026-05-24), SKILL.md stays slim — extended only
with adoption trigger phrases + a one-line pointer to
`references/adoption-playbook.md`. The substance lives in
`references/`.

This file has 5 tests, NOT 6 (per OQ6 planning resolution): the
proposed "lockstep guarantee still holds" test would duplicate
`tests/test_skill_refs.py::test_bundled_ref_matches_source`, which
already runs in the suite. No need for a second copy.

Helpers `_read_skill` / `_split_frontmatter` / `_parse_frontmatter`
are imported from tests/test_skill.py (the M5 oracle module).
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

# Reuse the M5 oracle helpers (test_skill.py lines 49-85).
from tests.test_skill import _parse_frontmatter, _read_skill, _split_frontmatter

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "src" / "docs_cli" / "skill"
ADOPTION_PLAYBOOK = SKILL_DIR / "references" / "adoption-playbook.md"
DOCS_TOML_TEMPLATE = SKILL_DIR / "references" / "docs-toml-template.toml"


# --- 1. SKILL.md description carries adoption triggers ---------------------


def test_skill_md_description_carries_adoption_triggers():
    text = _read_skill()
    frontmatter, _ = _split_frontmatter(text)
    parsed = _parse_frontmatter(frontmatter)
    description = parsed.get("description", "")
    adoption_triggers = [
        "adopt this directory",
        "migrate this folder",
        "bring this into docs convention",
        "import existing markdown specs",
    ]
    hits = [phrase for phrase in adoption_triggers if phrase in description]
    assert len(hits) >= 3, (
        f"SKILL.md description should carry at least 3 of the 4 adoption "
        f"trigger phrases {adoption_triggers!r}; found {hits!r} in:\n{description!r}"
    )


# --- 2. SKILL.md contains the one-line adoption pointer --------------------


def test_skill_md_contains_one_line_adoption_pointer():
    text = _read_skill()
    _, body = _split_frontmatter(text)
    # Two load-bearing substrings: the bolded prompt and the link.
    assert "**Adopting an existing Markdown directory?** Read" in body, body
    assert "](references/adoption-playbook.md)" in body, body


# --- 3. adoption-playbook.md exists with the required H2 sections ----------


def test_adoption_playbook_exists_with_required_sections():
    assert ADOPTION_PLAYBOOK.exists(), f"{ADOPTION_PLAYBOOK} does not exist"
    body = ADOPTION_PLAYBOOK.read_text(encoding="utf-8")
    required_h2s = [
        "## When this applies",
        "## Step 1",
        "## Step 2",
        "## Step 3",
        "## Step 4",
        "## Step 5",
        "## Step 6",
        "## Worked example",
        "## Pitfalls",
    ]
    for heading in required_h2s:
        # Match the heading at the start of a line, allowing trailing
        # phrases (e.g. `## Step 1 — docs migrate ...`).
        pattern = rf"^{re.escape(heading)}"
        assert re.search(pattern, body, re.M), (
            f"adoption-playbook.md is missing required H2 starting {heading!r}"
        )


# --- 4. docs-toml-template.toml exists and is valid TOML -------------------


def test_docs_toml_template_exists_and_is_valid_toml():
    assert DOCS_TOML_TEMPLATE.exists(), f"{DOCS_TOML_TEMPLATE} does not exist"
    raw = DOCS_TOML_TEMPLATE.read_text(encoding="utf-8")
    # Must parse cleanly — the operator copies this verbatim.
    tomllib.loads(raw)


# --- 5. docs-toml-template.toml has documented sections + examples ---------


def test_docs_toml_template_has_documented_sections():
    assert DOCS_TOML_TEMPLATE.exists(), f"{DOCS_TOML_TEMPLATE} does not exist"
    raw = DOCS_TOML_TEMPLATE.read_text(encoding="utf-8")
    # Literal section headers — the operator scans for these.
    for section in ("[exclude]", "[migrate]", "[vocabulary]"):
        assert section in raw, f"docs-toml-template.toml missing {section!r}"

    # Each section must have at least one commented example. The
    # heuristic: between section header and the next blank/header, at
    # least one line starting (after indent) with `#`. We split the
    # raw text per section.
    def _section_block(name: str) -> str:
        idx = raw.find(name)
        assert idx != -1, name
        # Read until the next `[xxx]` section or EOF.
        tail = raw[idx + len(name):]
        next_section = re.search(r"^\[[a-zA-Z_-]+\]", tail, re.M)
        return tail[: next_section.start()] if next_section else tail

    for section in ("[exclude]", "[migrate]", "[vocabulary]"):
        block = _section_block(section)
        commented_lines = [
            ln for ln in block.splitlines() if ln.lstrip().startswith("#") and ln.strip() != "#"
        ]
        assert len(commented_lines) >= 1, (
            f"docs-toml-template.toml section {section!r} has no commented examples; "
            f"block was:\n{block!r}"
        )
