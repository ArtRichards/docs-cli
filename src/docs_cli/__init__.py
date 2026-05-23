"""docs-cli — prescriptive CLI for managing trees of structured Markdown docs.

The console-script entry point lives in :mod:`docs_cli.cli` and is exposed
as ``main`` here for convenience::

    from docs_cli import main

The bundled Claude Code skill is shipped as package data under
``docs_cli/skill/`` and is materialised onto a host via
``docs install-skill``.

``main`` is loaded lazily via ``__getattr__`` so that
``python -m docs_cli.cli`` does not trigger the runpy
"found in sys.modules after import of package" warning (the warning
fires when the package's ``__init__`` eagerly imports the submodule
``runpy`` is about to execute).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover — type-only.
    from docs_cli.cli import main  # noqa: F401

__all__ = ["main"]


def __getattr__(name: str) -> Any:
    if name == "main":
        from docs_cli.cli import main as _main

        return _main
    raise AttributeError(f"module 'docs_cli' has no attribute {name!r}")
