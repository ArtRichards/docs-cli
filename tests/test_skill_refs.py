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


@pytest.mark.parametrize("name", ["cli.md", "convention.md"])
def test_bundled_ref_matches_source(name: str) -> None:
    """The bundled reference must be byte-identical to its source spec."""
    source = (SOURCE_DIR / name).read_bytes()
    bundle = (BUNDLE_DIR / name).read_bytes()
    assert source == bundle, (
        f"src/docs_cli/skill/references/{name} has drifted from docs/{name}. "
        f"Re-sync: cp docs/{name} src/docs_cli/skill/references/{name}"
    )
