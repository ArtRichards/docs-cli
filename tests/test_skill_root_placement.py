"""M22 checks for docs-tree root-placement guidance (project ≠ directory).

The docs convention spec and the bundled skill must teach where to put
`.docs.toml`: a `Project:` is metadata, not a directory, and because
`Related:` paths are root-relative, nesting a lone project beneath a parent
root prefixes every intra-project sibling reference with a redundant
`<subdir>/`. The default for a single project is to make the project's own
directory the docs root. See `docs/m22-root-placement-guidance.md`.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "src" / "docs_cli" / "skill"
DOCS_DIR = REPO_ROOT / "docs"


def test_skill_md_has_root_placement_note() -> None:
    body = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    # Discriminating phrases first (absent before M22) so a failure points at
    # the missing guidance, not at the pre-existing reference pointer.
    assert "Where to put" in body
    assert "not a directory" in body
    assert "redundant" in body
    assert "<subdir>/" in body  # pin the specific consequence mechanism, not just the adjective
    assert "references/convention.md" in body


def test_convention_documents_root_placement() -> None:
    body = (DOCS_DIR / "convention.md").read_text(encoding="utf-8")

    assert "Where to put" in body
    assert "metadata field, not a directory" in body
    assert "root is the project" in body
    assert "redundant" in body
    assert "<subdir>/" in body


def test_bundled_convention_carries_root_placement_guidance() -> None:
    # Self-containment: the bundled reference shipped in the wheel must carry
    # the same guidance. Full byte-identity with docs/convention.md is pinned
    # by test_skill_refs.py; this asserts the guidance specifically rides along
    # so an installed skill (no source checkout) still teaches placement.
    bundled = (SKILL_DIR / "references" / "convention.md").read_text(encoding="utf-8")

    assert "metadata field, not a directory" in bundled
    assert "root is the project" in bundled
    assert "<subdir>/" in bundled
