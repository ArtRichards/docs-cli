"""Version SoT tests (M12 — Phase 2, written RED).

M12 sources `__version__` from `importlib.metadata.version("docs-cli")`
so a single `pyproject.toml` `version` bump propagates to
`docs --version` automatically. The tests below pin that wiring:

- `__version__` matches `importlib.metadata.version("docs-cli")`.
- `__version__` matches the static `pyproject.toml` `[project] version`.
- The literal hardcoded version is GONE from `src/docs_cli/cli.py`.

These tests are RED at Phase 4 (cli.py still has the literal `1.4.0`);
Phase 5/6 replaces the literal with the `importlib.metadata` lookup.
"""

from __future__ import annotations

import importlib.metadata as _md
import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLI_PY = REPO_ROOT / "src" / "docs_cli" / "cli.py"
PYPROJECT = REPO_ROOT / "pyproject.toml"


def _load_pyproject() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def test_version_is_sourced_from_importlib_metadata() -> None:
    """`docs_cli.cli.__version__` equals `importlib.metadata.version("docs-cli")`.

    Intended RED reason: cli.py still carries `__version__ = "1.4.0"`
    as a hardcoded literal; Phase 5/6 replaces with the runtime lookup.
    """
    from docs_cli import cli as _cli

    assert _cli.__version__ == _md.version("docs-cli")


def test_version_matches_pyproject() -> None:
    """`__version__` matches `pyproject.toml` `[project] version`.

    Intended RED reason: bare literal `1.4.0` in cli.py vs the
    M12-bumped pyproject `1.5.0` after Phase 7.
    """
    from docs_cli import cli as _cli

    data = _load_pyproject()
    assert _cli.__version__ == data["project"]["version"]


def test_cli_py_has_no_hardcoded_version_literal() -> None:
    """`src/docs_cli/cli.py` MUST source `__version__` from
    `importlib.metadata`, not a hardcoded `__version__ = "<digit>...`
    literal.

    Intended RED reason: at Phase 4 the file still carries
    `__version__ = "1.4.0"`. Phase 5/6 swaps in the runtime lookup.
    """
    source = CLI_PY.read_text(encoding="utf-8")

    # Refuse a literal `__version__ = "<digit>...` form.
    hardcoded_re = re.compile(r'^__version__\s*=\s*["\']\d', re.MULTILINE)
    assert not hardcoded_re.search(source), (
        'cli.py contains a hardcoded `__version__ = "<literal>"` line; '
        "M12 sources the dunder from `importlib.metadata.version('docs-cli')` "
        "with a `PackageNotFoundError` fallback to `'0.0.0+local'`."
    )

    # The runtime lookup MUST be present.
    assert "importlib.metadata.version" in source or "metadata.version" in source, (
        "cli.py must source `__version__` via `importlib.metadata.version(...)`"
    )
