"""Structural checks over the M5 Claude Code skill artifact (Phase 1 — signatures).

M5 ships a `SKILL.md` markdown artifact, not a Python code surface. Its
correctness is verified by a **two-part oracle** (resolved OQ1):

1. This file — `tests/test_skill.py` — the *structural, automatable* half.
   It asserts the deterministic properties of the artifact: valid frontmatter
   carrying exactly `name` + `description`, a non-empty body within the
   skill-authoring size budget, every `docs` verb the body names is a real
   subcommand of `bin/docs`, every relative link resolves, and the skill
   directory carries no auxiliary clutter. It runs RED -> GREEN in CI with the
   rest of the suite: RED at Phase 4 against the Phase-1 stub body, GREEN at
   Phase 8 against the authored one.
2. The behavioural **trigger-scenario checklist** in
   `docs/m5-claude-code-skill-log.md` — the judgement half — a fixed table of
   "agent about to do X -> expected verb (or no trigger)" rows, walked by a
   human/agent at the Phase 9 dogfood pass.

These are the test *signatures* only: each body is a `pytest.fail(... Phase 2)`
placeholder so the file collects. Phase 2 implements the checks.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from docs import _build_parser  # loaded via conftest's module registration

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "docs"
SKILL_MD = SKILL_DIR / "SKILL.md"


def test_skill_md_exists_and_has_frontmatter() -> None:
    pytest.fail("Not implemented — Phase 2")


def test_frontmatter_has_exactly_name_and_description() -> None:
    pytest.fail("Not implemented — Phase 2")


def test_name_and_description_values_are_sane() -> None:
    pytest.fail("Not implemented — Phase 2")


def test_body_is_present_and_within_size_budget() -> None:
    pytest.fail("Not implemented — Phase 2")


def test_every_named_verb_is_a_real_subcommand() -> None:
    # _build_parser is imported here at Phase 1 to pin the conftest module-load
    # contract; Phase 2 uses it to derive the real verb set.
    assert _build_parser is not None
    pytest.fail("Not implemented — Phase 2")


def test_every_relative_link_resolves() -> None:
    pytest.fail("Not implemented — Phase 2")


def test_skill_dir_has_no_clutter() -> None:
    pytest.fail("Not implemented — Phase 2")


def test_frontmatter_parser_rejects_extra_keys() -> None:
    pytest.fail("Not implemented — Phase 2")
