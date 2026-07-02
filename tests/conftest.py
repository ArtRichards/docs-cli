"""Test setup: expose `docs_cli.cli` under both `docs_cli` and the legacy
``docs`` alias so test files can keep writing ``from docs import Doc, parse``.

M6 relocates the CLI to a real package at ``src/docs_cli/cli.py``. The
repo's top-level ``docs/`` *directory* (the specs tree) used to shadow
the in-tree script under normal imports — the package move removes that
collision, but the test suite predates the rename and references the
script as ``from docs import …``. To avoid a sweeping test rewrite for
no contract change, this conftest:

1. Inserts ``src/`` on ``sys.path`` so ``import docs_cli`` resolves to
   the relocated package.
2. Registers ``docs_cli.cli`` under the alias ``docs`` in
   ``sys.modules``, preserving the existing test imports.
3. Exposes a ``docs_script`` session fixture pointing at the relocated
   ``src/docs_cli/cli.py`` so the CLI-subprocess tests
   (``test_cli_*.py``) can keep launching it as
   ``[sys.executable, str(docs_script), …]``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
DOCS_SCRIPT = REPO_ROOT / "src" / "docs_cli" / "cli.py"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# Make `src/docs_cli/` importable without an editable install.
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# M21 (D6) — hard-disable the PyPI update-check for the whole suite so no
# test (in-process or subprocess) ever reaches the network. Inert at baseline
# (nothing reads it until the M21 dispatch hook lands); inherited by every
# `subprocess.run` child. Dispatch tests that need to SEE the notice opt back
# in per-test via `monkeypatch.delenv("DOCS_CLI_NO_UPDATE_CHECK", raising=False)`.
os.environ["DOCS_CLI_NO_UPDATE_CHECK"] = "1"

from docs_cli import cli as _cli  # noqa: E402  (must follow sys.path insert)

# Preserve the legacy `from docs import …` import path used by the
# pre-M6 test files. `setdefault` so a real `docs` module in the
# environment (unlikely; the PyPI name is `docs-cli`) wins.
sys.modules.setdefault("docs", _cli)


@pytest.fixture(scope="session")
def docs_script() -> Path:
    """Absolute path to the CLI script (used by subprocess CLI tests)."""
    return DOCS_SCRIPT


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Absolute path to tests/fixtures/."""
    return FIXTURES_DIR
