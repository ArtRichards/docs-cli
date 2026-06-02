"""M16 checks for bundled docs skill quality-artifact guidance."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "src" / "docs_cli" / "skill"


def test_skill_points_to_quality_artifacts_reference() -> None:
    body = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert "references/quality-artifacts.md" in body
    assert "test matrices" in body
    assert "generated reports" in body
    assert "not prove behavior is correct" in body
    assert "visible tests are adequate" in body


def test_quality_artifacts_reference_documents_m16_contract() -> None:
    body = (SKILL_DIR / "references" / "quality-artifacts.md").read_text(encoding="utf-8")

    required = [
        "m4-risky-change-test-matrix.md",
        "quality/m4-quality-log.md",
        "coverage.xml",
        "mutation.json",
        "benchmark.json",
        "Risk level",
        "Gate commands",
        "docs check",
        "mechanically clean",
        "does not prove the contract is strong",
    ]
    for phrase in required:
        assert phrase in body


def test_installed_skill_references_do_not_depend_on_source_checkout() -> None:
    for path in (SKILL_DIR / "references").glob("*.md"):
        body = path.read_text(encoding="utf-8")

        assert "../../../../docs/" not in body, (
            f"{path.name} links back to the source checkout docs tree"
        )
        assert "../src/docs_cli/" not in body, f"{path.name} contains a source-layout relative link"
