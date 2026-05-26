# Mypy-only stub: tests use `from docs import X`. tests/conftest.py
# aliases docs_cli.cli as `docs` in sys.modules at collection time —
# mypy cannot see runtime sys.modules edits, so this stub re-exports
# the public surface to keep type-checking honest.
#
# Excluded from ruff (see pyproject.toml [tool.ruff] extend-exclude) so
# the import-block stays in a single readable group rather than being
# expanded into N single-import statements by isort.

from docs_cli.cli import *
from docs_cli.cli import (
    BUILTIN_ROLES as BUILTIN_ROLES,
    BUILTIN_STATUSES as BUILTIN_STATUSES,
    CANONICAL_ROLE_ORDER as CANONICAL_ROLE_ORDER,
    Confidence as Confidence,
    Config as Config,
    Doc as Doc,
    FileMigration as FileMigration,
    Finding as Finding,
    INDEX_FILENAME as INDEX_FILENAME,
    MARKER_END as MARKER_END,
    MARKER_START as MARKER_START,
    MetadataError as MetadataError,
    MigrationPlan as MigrationPlan,
    VocabularyError as VocabularyError,
    _build_parser as _build_parser,
    atomic_write as atomic_write,
    find_root as find_root,
    load_config as load_config,
    main as main,
    parse as parse,
    parse_metadata_block as parse_metadata_block,
    render_index as render_index,
    walk as walk,
)
