"""M21 — PyPI update-check notification.

`docs-cli`'s first and only network surface: a best-effort, once-per-24h,
fail-silent check of PyPI for a newer ``docs-cli`` release. When a strictly
newer released version exists, the CLI emits a single advisory line to STDERR
nudging ``pip install -U docs-cli``. The notice never touches stdout and never
alters the exit code.

The module is a self-contained, injectable seam (cache I/O, the version
compare, the network hook, the suppression predicates, the notice formatter,
and the post-dispatch ``maybe_notify`` entry point) so the whole test suite
stays offline: tests inject a fake ``fetch_latest_version``. See
``docs/cli.md`` § "Update check" for the prose contract.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

# The one PyPI endpoint consulted (stdlib `urllib` only — the zero-dependency
# wheel is preserved). A short timeout keeps even the worst-case path snappy.
PYPI_URL = "https://pypi.org/pypi/docs-cli/json"
TIMEOUT = 1.0

# Both the network and the notice are gated by a 24h throttle (independently).
THROTTLE = timedelta(hours=24)

# The byte-exact advisory line (em-dash U+2014 between `<latest>` and `run:`,
# ASCII `->` between the two versions). Pinned byte-for-byte in docs/cli.md and
# asserted verbatim by tests/test_update_check.py.
NOTICE_TEMPLATE = "docs: update available {current} -> {latest} — run: pip install -U docs-cli"


@dataclass
class Cache:
    """The per-user update-check state (exactly three keys, all optional).

    ``last_check`` / ``last_notified`` are ISO-8601 UTC timestamps;
    ``latest_version`` is the most recent PyPI version seen.
    """

    last_check: str | None = None
    latest_version: str | None = None
    last_notified: str | None = None


def _parse_version(version: str) -> tuple[int, ...] | None:
    """Parse a dot-split numeric release into a tuple, or ``None`` if any
    segment is non-numeric (pre-release / local / unparseable → fail closed)."""
    parts = version.split(".")
    out: list[int] = []
    for part in parts:
        if not part.isdigit():
            return None
        out.append(int(part))
    return tuple(out)


def is_newer(current: str, latest: str) -> bool:
    """True iff ``latest`` is a strictly-greater *released* version than
    ``current``. Numeric tuple-compare on the dot-split release segments (so
    ``1.9.0`` < ``1.10.0``), fail-closed on a pre-release / local / unparseable
    version on either side."""
    current_tuple = _parse_version(current)
    latest_tuple = _parse_version(latest)
    if current_tuple is None or latest_tuple is None:
        return False
    return latest_tuple > current_tuple


def format_notice(current: str, latest: str) -> str:
    """The advisory line, without a trailing newline (the emitter adds it)."""
    return NOTICE_TEMPLATE.format(current=current, latest=latest)


def cache_path() -> Path:
    """``${XDG_CACHE_HOME:-~/.cache}/docs-cli/update-check.json``."""
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / "docs-cli" / "update-check.json"


def read_cache() -> Cache:
    """Read the cache, treating missing / unreadable / malformed as no data.

    Requires both ``last_check`` and ``latest_version`` to be present and
    non-null; ``last_notified`` is optional. Any other shape → ``Cache()``.
    """
    try:
        raw = json.loads(cache_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Cache()
    if not isinstance(raw, dict):
        return Cache()
    last_check = raw.get("last_check")
    latest_version = raw.get("latest_version")
    if last_check is None or latest_version is None:
        return Cache()
    return Cache(
        last_check=last_check,
        latest_version=latest_version,
        last_notified=raw.get("last_notified"),
    )


def write_cache(cache: Cache) -> None:
    """Persist exactly the three keys; swallow any ``OSError`` (fail-silent)."""
    data = {
        "last_check": cache.last_check,
        "latest_version": cache.latest_version,
        "last_notified": cache.last_notified,
    }
    path = cache_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
    except OSError:
        return


def _stale(timestamp: str | None) -> bool:
    """True if ``timestamp`` is missing, unparseable, or ≥ 24h in the past."""
    if timestamp is None:
        return True
    try:
        when = datetime.fromisoformat(timestamp)
    except ValueError:
        return True
    return datetime.now(UTC) - when >= THROTTLE


def should_check(cache: Cache) -> bool:
    """Whether the network may be consulted (``last_check`` stale or absent)."""
    return _stale(cache.last_check)


def should_notify(cache: Cache) -> bool:
    """Whether a notice may be emitted (``last_notified`` stale or absent)."""
    return _stale(cache.last_notified)


def fetch_latest_version() -> str | None:
    """GET the PyPI JSON and return ``info.version``, or ``None`` on any error.

    The injectable network hook: tests monkeypatch ``urllib.request.urlopen``
    (the fetch unit tests) or replace this function wholesale (the dispatch
    tests), so the suite never reaches the network.
    """
    try:
        with urllib.request.urlopen(PYPI_URL, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
        version = data["info"]["version"]
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError, TypeError):
        return None
    return version if isinstance(version, str) else None


def _env_disabled(env: Mapping[str, str]) -> bool:
    """Any of the kill-switch env vars *present* (presence, not truthiness)."""
    return any(key in env for key in ("CI", "DOCS_CLI_NO_UPDATE_CHECK", "DO_NOT_TRACK"))


def notice_suppressed(args: argparse.Namespace, env: Mapping[str, str]) -> bool:
    """Whether the *notice* is suppressed (``--quiet`` / ``--json`` / env)."""
    return bool(getattr(args, "quiet", False) or getattr(args, "json", False) or _env_disabled(env))


def network_suppressed(args: argparse.Namespace, env: Mapping[str, str]) -> bool:
    """Whether the *network* call is skipped entirely (env kill switches only;
    ``--quiet`` / ``--json`` still warm the cache)."""
    return _env_disabled(env)


def maybe_notify(args: argparse.Namespace, env: Mapping[str, str], current: str) -> None:
    """Post-dispatch update-check hook (orchestration lands in Phase 6)."""
    return None
