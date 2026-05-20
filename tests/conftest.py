"""Test setup: load `bin/docs` as the `docs` module.

The executable at `bin/docs` has no `.py` extension, and the repo's
top level has a `docs/` directory that would shadow it under normal
imports. We use `importlib` to load the script as a module under
the name `docs` in `sys.modules`, so tests can write the natural
`from docs import Doc, parse, ...`.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_SCRIPT = REPO_ROOT / "bin" / "docs"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _load_docs():
    loader = importlib.machinery.SourceFileLoader("docs", str(DOCS_SCRIPT))
    spec = importlib.util.spec_from_loader("docs", loader, origin=str(DOCS_SCRIPT))
    if spec is None:  # pragma: no cover - safety net
        raise RuntimeError(f"failed to create spec for {DOCS_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    # Register before exec — @dataclass resolves field types via sys.modules.
    sys.modules["docs"] = module
    loader.exec_module(module)
    return module


# Module-level load so test files can `from docs import X`.
docs = _load_docs()


@pytest.fixture(scope="session")
def docs_script() -> Path:
    """Absolute path to the executable (used by subprocess CLI tests)."""
    return DOCS_SCRIPT


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Absolute path to tests/fixtures/."""
    return FIXTURES_DIR
