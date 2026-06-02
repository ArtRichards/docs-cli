"""Lockstep: bundled refs are byte-identical mirrors of the source specs.

`src/docs_cli/skill/references/{convention,cli}.md` are exact copies of
`docs/{convention,cli}.md`, so the skill ships with self-contained references
an agent can open from any installed copy of the skill — no host-specific
path baked in, no transform script to keep working.

Re-sync after a spec edit:

    cp docs/convention.md src/docs_cli/skill/references/convention.md
    cp docs/cli.md       src/docs_cli/skill/references/cli.md
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "docs"
BUNDLE_DIR = REPO_ROOT / "src" / "docs_cli" / "skill" / "references"


SKILL_DIR = REPO_ROOT / "src" / "docs_cli" / "skill"


@pytest.mark.parametrize("name", ["cli.md", "convention.md"])
def test_bundled_ref_matches_source(name: str) -> None:
    """The bundled reference must be byte-identical to its source spec."""
    source = (SOURCE_DIR / name).read_bytes()
    bundle = (BUNDLE_DIR / name).read_bytes()
    assert source == bundle, (
        f"src/docs_cli/skill/references/{name} has drifted from docs/{name}. "
        f"Re-sync: cp docs/{name} src/docs_cli/skill/references/{name}"
    )


def test_bundled_skill_has_no_repo_relative_links() -> None:
    """No bundled skill `.md` may carry a repo-relative `](../` link (M14 — C1).

    GREEN regression guard. M16 rewrote the bundled references
    self-contained, so the dangling links the post-1.5.0 review flagged
    (`use-cases.md:5` → `../../../../docs/charter.md`; `cli.md:318` →
    `../src/docs_cli/skill/SKILL.md`) no longer exist. A `](../` link in a
    bundled doc dangles once the skill is installed on a host (the repo
    layout above the install dir is gone), so this pins that the bundled
    docs stay host-self-contained.
    """
    offenders: list[str] = []
    for md in sorted(SKILL_DIR.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if "](../" in line:
                rel = md.relative_to(REPO_ROOT).as_posix()
                offenders.append(f"{rel}:{lineno}: {line.strip()}")
    assert not offenders, (
        "bundled skill docs contain repo-relative `](../` links that dangle "
        "once installed on a host:\n" + "\n".join(offenders)
    )
