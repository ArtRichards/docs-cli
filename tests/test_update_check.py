"""M21 — Update-check notification (PyPI new-version notice). Phase 2 (RED).

Two layers, both fully offline:

- **Unit tests** exercise the `docs_cli.update_check` seam directly (compare,
  formatter, cache I/O, throttles, the injectable `fetch_latest_version` hook,
  and the suppression predicates). The module does not exist until Phase 5, so
  the guarded import below leaves `uc is None` at the RED baseline and each unit
  test asserts `uc is not None` first — a clean assertion failure
  ("update_check module not yet implemented (Phase 5)"), never a collection or
  import error.
- **Dispatch tests** drive `cli.main([...])` in-process with capsys + a fake
  `fetch_latest_version` and a tmp `XDG_CACHE_HOME`. The `main()` hook lands in
  Phase 6, so the notice/cache-effect tests are RED at baseline (empty stderr /
  no cache file) while the absence-asserting regression locks already pass.

Phase-3 data is inline + date-independent: timestamps are stamped relative to
`datetime.now(UTC)`; no committed dated fixtures, no real `~/.cache`, no
network.
"""

from __future__ import annotations

import argparse
import importlib
import json
import shutil
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from docs_cli import cli

REPO_ROOT = Path(__file__).resolve().parents[1]

# The running version the notice quotes as `<current>`. Computed from the
# installed metadata so the dispatch tests stay correct across the Phase-7
# 1.6.5 -> 1.7.0 bump (the fake PyPI version is always strictly newer).
CURRENT = cli.__version__

# Guarded import: the module is created in Phase 5. Use importlib so mypy never
# tries to resolve a not-yet-existing module (the gate must stay clean at the
# RED baseline); `Any` lets the unit tests reference `uc.*` without a stub.
uc: Any
try:
    uc = importlib.import_module("docs_cli.update_check")
except ModuleNotFoundError:
    uc = None

_NOT_IMPL = "update_check module not yet implemented (Phase 5)"
PYPI_URL = "https://pypi.org/pypi/docs-cli/json"


# ---------------------------------------------------------------------------
# Phase-3 inline builders (date-independent; no committed fixtures)
# ---------------------------------------------------------------------------


def _iso_hours_ago(hours: int) -> str:
    """An ISO-8601 UTC timestamp `hours` in the past (e.g. 1 = fresh, 25 = stale)."""
    return (datetime.now(UTC) - timedelta(hours=hours)).isoformat()


def _fake_pypi_json(version: str) -> dict[str, dict[str, str]]:
    """The shape of the PyPI JSON the fetch hook parses `info.version` out of."""
    return {"info": {"version": version}}


def _expected_notice(latest: str) -> str:
    """The byte-exact emitted stderr line (formatter output + the emitter's \\n)."""
    return f"docs: update available {CURRENT} -> {latest} — run: pip install -U docs-cli\n"


class _FetchSpy:
    """Call-recording stand-in for `uc.fetch_latest_version`.

    Lives OUTSIDE the update_check module so call-count assertions hold even at
    the RED baseline, where `uc is None` and `_patch_fetch` is a no-op (the spy
    is simply never invoked, so `calls == 0`).
    """

    def __init__(self, version: str | None = None, exc: Exception | None = None) -> None:
        self.version = version
        self.exc = exc
        self.calls = 0

    def __call__(self, *args: Any, **kwargs: Any) -> str | None:
        self.calls += 1
        if self.exc is not None:
            raise self.exc
        return self.version


class _FakeResp:
    """Minimal context-manager HTTP response for the fetch unit tests."""

    def __init__(self, body: bytes, status: int = 200) -> None:
        self._body = body
        self.status = status

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeResp:
        return self

    def __exit__(self, *exc: Any) -> None:
        return None


def _patch_fetch(monkeypatch: Any, spy: _FetchSpy) -> None:
    """Inject the fake fetch hook — a no-op until the module exists (Phase 5)."""
    if uc is not None:
        monkeypatch.setattr(uc, "fetch_latest_version", spy)


def _write_dispatch_cache(
    cache_home: Path,
    *,
    last_check: str | None = None,
    latest_version: str | None = None,
    last_notified: str | None = None,
) -> Path:
    """Seed `$XDG_CACHE_HOME/docs-cli/update-check.json` with the given keys."""
    cache_dir = cache_home / "docs-cli"
    cache_dir.mkdir(parents=True, exist_ok=True)
    data: dict[str, str] = {}
    if last_check is not None:
        data["last_check"] = last_check
    if latest_version is not None:
        data["latest_version"] = latest_version
    if last_notified is not None:
        data["last_notified"] = last_notified
    path = cache_dir / "update-check.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _read_dispatch_cache(cache_home: Path) -> dict | None:
    path = cache_home / "docs-cli" / "update-check.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _copy_tree(fixtures_dir: Path, name: str, tmp_path: Path) -> Path:
    dst = tmp_path / "tree"
    shutil.copytree(fixtures_dir / "trees" / name, dst)
    return dst


def _prep_dispatch(monkeypatch: Any, tmp_path: Path) -> Path:
    """Re-enable the check (conftest disables it), point the cache at tmp.

    Clears the ambient suppression env vars so a host with `CI` set does not
    mask the notice; returns the tmp `XDG_CACHE_HOME` directory.
    """
    monkeypatch.delenv("DOCS_CLI_NO_UPDATE_CHECK", raising=False)
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("DO_NOT_TRACK", raising=False)
    cache_home = tmp_path / "xdg-cache"
    monkeypatch.setenv("XDG_CACHE_HOME", str(cache_home))
    return cache_home


# ---------------------------------------------------------------------------
# Spec-content lock (Q7) — GREEN at baseline (Phase 1 pinned the contract)
# ---------------------------------------------------------------------------


def test_cli_md_pins_notice_template_and_suppression_env_vars():
    """cli.md carries the byte-exact notice template + the three disable vars.

    test_skill_refs transitively locks the bundled `references/cli.md` mirror.
    """
    cli_md = (REPO_ROOT / "docs" / "cli.md").read_text(encoding="utf-8")
    assert "docs: update available <current> -> <latest> — run: pip install -U docs-cli" in cli_md
    for var in ("DOCS_CLI_NO_UPDATE_CHECK", "DO_NOT_TRACK", "CI"):
        assert var in cli_md, f"cli.md must name the {var} suppression env var"


# ---------------------------------------------------------------------------
# Unit — version comparison (numeric, fail-closed)
# ---------------------------------------------------------------------------


def test_is_newer_true_when_latest_strictly_greater():
    assert uc is not None, _NOT_IMPL
    assert uc.is_newer("1.7.0", "1.7.1") is True


def test_is_newer_false_when_equal():
    assert uc is not None, _NOT_IMPL
    assert uc.is_newer("1.7.0", "1.7.0") is False


def test_is_newer_false_when_latest_older():
    assert uc is not None, _NOT_IMPL
    assert uc.is_newer("1.7.1", "1.7.0") is False


def test_is_newer_is_numeric_not_lexical():
    assert uc is not None, _NOT_IMPL
    assert uc.is_newer("1.9.0", "1.10.0") is True


def test_is_newer_fails_closed_on_local_running_version():
    assert uc is not None, _NOT_IMPL
    assert uc.is_newer("0.0.0+local", "1.7.0") is False


def test_is_newer_fails_closed_on_prerelease_running_version():
    assert uc is not None, _NOT_IMPL
    assert uc.is_newer("1.7.0rc1", "1.7.0") is False


def test_is_newer_fails_closed_on_unparseable_either_side():
    assert uc is not None, _NOT_IMPL
    assert uc.is_newer("not-a-version", "1.7.0") is False
    assert uc.is_newer("1.7.0", "not-a-version") is False


# ---------------------------------------------------------------------------
# Unit — notice formatter (no trailing newline)
# ---------------------------------------------------------------------------


def test_format_notice_is_byte_exact_without_trailing_newline():
    assert uc is not None, _NOT_IMPL
    notice = uc.format_notice("1.7.0", "1.7.1")
    assert notice == "docs: update available 1.7.0 -> 1.7.1 — run: pip install -U docs-cli"
    assert not notice.endswith("\n")


# ---------------------------------------------------------------------------
# Unit — cache path + I/O (XDG-aware; fail-silent; exactly three keys)
# ---------------------------------------------------------------------------


def test_cache_path_honours_xdg_cache_home(tmp_path, monkeypatch):
    assert uc is not None, _NOT_IMPL
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    assert uc.cache_path() == tmp_path / "docs-cli" / "update-check.json"


def test_cache_path_defaults_to_home_cache_when_xdg_unset(tmp_path, monkeypatch):
    assert uc is not None, _NOT_IMPL
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert uc.cache_path() == tmp_path / ".cache" / "docs-cli" / "update-check.json"


def test_read_cache_missing_returns_no_data(tmp_path, monkeypatch):
    assert uc is not None, _NOT_IMPL
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    assert uc.read_cache() == uc.Cache()


def test_read_cache_corrupt_returns_no_data(tmp_path, monkeypatch):
    assert uc is not None, _NOT_IMPL
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    path = uc.cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"{not json")
    assert uc.read_cache() == uc.Cache()


def test_read_cache_malformed_missing_keys_is_no_data(tmp_path, monkeypatch):
    assert uc is not None, _NOT_IMPL
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    path = uc.cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"last_check": _iso_hours_ago(1)}), encoding="utf-8")
    assert uc.read_cache() == uc.Cache()


def test_cache_roundtrips_exactly_three_keys(tmp_path, monkeypatch):
    assert uc is not None, _NOT_IMPL
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    c = uc.Cache(
        last_check=_iso_hours_ago(0),
        latest_version="1.7.1",
        last_notified=_iso_hours_ago(0),
    )
    uc.write_cache(c)
    raw = json.loads(uc.cache_path().read_text(encoding="utf-8"))
    assert set(raw) == {"last_check", "latest_version", "last_notified"}
    assert "last_skill_drift_notified" not in raw  # D5 cut — no fourth key
    assert uc.read_cache() == c


def test_write_cache_creates_parent_dir_on_first_write(tmp_path, monkeypatch):
    assert uc is not None, _NOT_IMPL
    xdg = tmp_path / "fresh"
    monkeypatch.setenv("XDG_CACHE_HOME", str(xdg))
    assert not (xdg / "docs-cli").exists()
    uc.write_cache(uc.Cache(last_check=_iso_hours_ago(0), latest_version="1.7.1"))
    assert uc.cache_path().exists()


def test_write_cache_unwritable_swallows_oserror(tmp_path, monkeypatch):
    assert uc is not None, _NOT_IMPL
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    path = uc.cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Make the cache *file path* a directory so opening it for write raises
    # IsADirectoryError (an OSError) — write must swallow it, never raise.
    path.mkdir()
    uc.write_cache(uc.Cache(last_check=_iso_hours_ago(0), latest_version="1.7.1"))


# ---------------------------------------------------------------------------
# Unit — 24h throttles (check vs notify, independent)
# ---------------------------------------------------------------------------


def test_should_check_true_when_no_cache():
    assert uc is not None, _NOT_IMPL
    assert uc.should_check(uc.Cache()) is True


def test_should_check_false_within_24h():
    assert uc is not None, _NOT_IMPL
    assert uc.should_check(uc.Cache(last_check=_iso_hours_ago(1))) is False


def test_should_check_true_after_24h():
    assert uc is not None, _NOT_IMPL
    assert uc.should_check(uc.Cache(last_check=_iso_hours_ago(25))) is True


def test_should_notify_true_when_no_cache():
    assert uc is not None, _NOT_IMPL
    assert uc.should_notify(uc.Cache()) is True


def test_should_notify_false_within_24h():
    assert uc is not None, _NOT_IMPL
    assert uc.should_notify(uc.Cache(last_notified=_iso_hours_ago(1))) is False


def test_should_notify_true_after_24h():
    assert uc is not None, _NOT_IMPL
    assert uc.should_notify(uc.Cache(last_notified=_iso_hours_ago(25))) is True


def test_throttles_are_independent():
    assert uc is not None, _NOT_IMPL
    # Fresh check + stale notify → check throttled, notify allowed.
    c1 = uc.Cache(last_check=_iso_hours_ago(1), last_notified=_iso_hours_ago(25))
    assert uc.should_check(c1) is False
    assert uc.should_notify(c1) is True
    # Stale check + fresh notify → check allowed, notify throttled.
    c2 = uc.Cache(last_check=_iso_hours_ago(25), last_notified=_iso_hours_ago(1))
    assert uc.should_check(c2) is True
    assert uc.should_notify(c2) is False


def test_should_check_treats_naive_timestamp_as_stale():
    assert uc is not None, _NOT_IMPL
    # A JSON-valid cache whose last_check is a NAIVE (offset-less) ISO timestamp
    # parses via fromisoformat into a naive datetime; the `now(UTC) - when`
    # subtract would then raise TypeError (aware-minus-naive). `_stale` must
    # self-heal — treat it as stale (re-check) rather than let the TypeError
    # abort the check and permanently disable the notice. No raise.
    assert uc.should_check(uc.Cache(last_check="2026-06-29T12:00:00")) is True


# ---------------------------------------------------------------------------
# Unit — fetch hook fail-silent (monkeypatched urllib; offline)
# ---------------------------------------------------------------------------


def test_fetch_returns_version_and_calls_pypi_url_with_timeout(monkeypatch):
    assert uc is not None, _NOT_IMPL
    recorded: dict[str, Any] = {}

    def fake_urlopen(url, timeout=None):
        recorded["url"] = url
        recorded["timeout"] = timeout
        return _FakeResp(json.dumps(_fake_pypi_json("1.7.1")).encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert uc.fetch_latest_version() == "1.7.1"
    assert recorded["url"] == PYPI_URL
    assert recorded["timeout"] == 1.0


def test_fetch_returns_none_on_urlerror(monkeypatch):
    assert uc is not None, _NOT_IMPL

    def fake_urlopen(url, timeout=None):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert uc.fetch_latest_version() is None


def test_fetch_returns_none_on_timeout(monkeypatch):
    assert uc is not None, _NOT_IMPL

    def fake_urlopen(url, timeout=None):
        raise TimeoutError("timed out")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert uc.fetch_latest_version() is None


def test_fetch_returns_none_on_http_error(monkeypatch):
    assert uc is not None, _NOT_IMPL

    def fake_urlopen(url, timeout=None):
        raise urllib.error.HTTPError(url, 500, "Server Error", {}, None)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert uc.fetch_latest_version() is None


def test_fetch_returns_none_on_malformed_body(monkeypatch):
    assert uc is not None, _NOT_IMPL

    def fake_urlopen(url, timeout=None):
        return _FakeResp(b"{not json")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert uc.fetch_latest_version() is None


# ---------------------------------------------------------------------------
# Unit — suppression predicates (defensive getattr; env + flags)
# ---------------------------------------------------------------------------


def test_notice_suppressed_by_quiet():
    assert uc is not None, _NOT_IMPL
    assert uc.notice_suppressed(argparse.Namespace(quiet=True), {}) is True


def test_notice_suppressed_by_json():
    assert uc is not None, _NOT_IMPL
    assert uc.notice_suppressed(argparse.Namespace(json=True), {}) is True


def test_notice_suppressed_by_ci_env():
    assert uc is not None, _NOT_IMPL
    assert uc.notice_suppressed(argparse.Namespace(), {"CI": ""}) is True


def test_notice_suppressed_by_no_update_check_env():
    assert uc is not None, _NOT_IMPL
    assert uc.notice_suppressed(argparse.Namespace(), {"DOCS_CLI_NO_UPDATE_CHECK": "1"}) is True


def test_notice_suppressed_by_do_not_track_env():
    assert uc is not None, _NOT_IMPL
    assert uc.notice_suppressed(argparse.Namespace(), {"DO_NOT_TRACK": "1"}) is True


def test_notice_not_suppressed_by_default_and_missing_attrs():
    assert uc is not None, _NOT_IMPL
    # A namespace lacking quiet/json must use getattr(..., False) and not raise.
    assert uc.notice_suppressed(argparse.Namespace(), {}) is False


def test_network_still_allowed_under_quiet():
    assert uc is not None, _NOT_IMPL
    assert uc.network_suppressed(argparse.Namespace(quiet=True), {}) is False


def test_network_still_allowed_under_json():
    assert uc is not None, _NOT_IMPL
    assert uc.network_suppressed(argparse.Namespace(json=True), {}) is False


def test_network_suppressed_by_ci_env():
    assert uc is not None, _NOT_IMPL
    assert uc.network_suppressed(argparse.Namespace(), {"CI": ""}) is True


def test_network_suppressed_by_no_update_check_env():
    assert uc is not None, _NOT_IMPL
    assert uc.network_suppressed(argparse.Namespace(), {"DOCS_CLI_NO_UPDATE_CHECK": "1"}) is True


def test_network_suppressed_by_do_not_track_env():
    assert uc is not None, _NOT_IMPL
    assert uc.network_suppressed(argparse.Namespace(), {"DO_NOT_TRACK": "1"}) is True


def test_network_allowed_by_default():
    assert uc is not None, _NOT_IMPL
    assert uc.network_suppressed(argparse.Namespace(), {}) is False


# ---------------------------------------------------------------------------
# Dispatch — intended-RED at baseline (no main() hook until Phase 6)
# ---------------------------------------------------------------------------


def test_dispatch_newer_emits_one_stderr_notice(monkeypatch, capsys, tmp_path, fixtures_dir):
    _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    code = cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert code == 0
    assert out.err.endswith(_expected_notice("1.7.1"))  # last line, byte-exact + \n
    assert out.err.count("docs: update available") == 1  # exactly one
    assert "docs: update available" not in out.out  # never on stdout


def test_dispatch_failing_verb_keeps_exit_code_and_shows_notice(
    monkeypatch, capsys, tmp_path, fixtures_dir
):
    _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "invalid", tmp_path)
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    code = cli.main(["check", str(tree)])
    out = capsys.readouterr()
    notice = _expected_notice("1.7.1")
    assert code == 2  # the notice never changes the exit code
    # ADDITIVE, not a replacement: the verb's own diagnostic output survives.
    # `docs check` prints its findings to STDOUT (stderr stays empty until the
    # notice lands), so the additive guard targets stdout — a hook that
    # clobbered the command's output would drop these findings.
    assert "error:" in out.out  # the check findings still print
    assert out.err.endswith(notice)  # notice is the last stderr line, byte-exact + \n
    # ...and it sits on its OWN line: what precedes the notice on stderr is
    # either nothing (stderr is only the notice) or ends in a newline — never
    # glued onto a prior stderr line without a separator.
    before = out.err[: -len(notice)]
    assert before == "" or before.endswith("\n")


def test_dispatch_stale_check_fetches_once_and_advances_last_check(
    monkeypatch, capsys, tmp_path, fixtures_dir
):
    cache_home = _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    old = _iso_hours_ago(25)
    _write_dispatch_cache(cache_home, last_check=old, latest_version=CURRENT)
    spy = _FetchSpy(version="1.7.1")
    _patch_fetch(monkeypatch, spy)
    code = cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert code == 0
    assert spy.calls == 1  # stale last_check → exactly one network attempt
    after = _read_dispatch_cache(cache_home)
    assert after is not None and after["last_check"] != old  # advanced
    assert out.err.endswith(_expected_notice("1.7.1"))


def test_dispatch_notify_throttle_is_independent_of_check(
    monkeypatch, capsys, tmp_path, fixtures_dir
):
    cache_home = _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _write_dispatch_cache(
        cache_home,
        last_check=_iso_hours_ago(25),  # stale → check runs
        latest_version=CURRENT,
        last_notified=_iso_hours_ago(1),  # fresh → notice throttled
    )
    spy = _FetchSpy(version="1.7.1")
    _patch_fetch(monkeypatch, spy)
    cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert spy.calls == 1  # cache warmed
    assert "docs: update available" not in out.err  # but notice throttled


def test_dispatch_quiet_warms_cache_without_notice(monkeypatch, capsys, tmp_path, fixtures_dir):
    cache_home = _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    code = cli.main(["touch", str(tree / "lone-doc.md"), "--root", str(tree), "--quiet"])
    out = capsys.readouterr()
    assert code == 0
    assert "docs: update available" not in out.err  # --quiet suppresses the notice
    after = _read_dispatch_cache(cache_home)
    assert after is not None
    assert after.get("last_check")  # cache warmed (last_check advanced)
    assert not after.get("last_notified")  # notice budget untouched


def test_dispatch_corrupt_cache_recovers_and_notifies(monkeypatch, capsys, tmp_path, fixtures_dir):
    cache_home = _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    cache_dir = cache_home / "docs-cli"
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "update-check.json").write_bytes(b"{not json")
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    code = cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert code == 0
    assert out.err.endswith(_expected_notice("1.7.1"))  # no traceback, notice emitted
    after = _read_dispatch_cache(cache_home)  # parses → was rewritten to valid JSON
    assert after is not None and set(after) == {"last_check", "latest_version", "last_notified"}


def test_dispatch_naive_timestamp_cache_self_heals(monkeypatch, capsys, tmp_path, fixtures_dir):
    cache_home = _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    # A naive (offset-less) last_check would raise TypeError on the
    # aware-minus-naive subtract; the check must treat it as stale, re-probe,
    # emit, and rewrite an offset-aware cache — never abort fatally.
    _write_dispatch_cache(cache_home, last_check="2026-06-29T12:00:00", latest_version=CURRENT)
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    code = cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert code == 0
    assert out.err.endswith(_expected_notice("1.7.1"))  # self-healed → notice emitted
    after = _read_dispatch_cache(cache_home)
    assert after is not None
    # rewritten with an offset-aware last_check (parses back to an aware datetime)
    assert datetime.fromisoformat(after["last_check"]).tzinfo is not None


def test_dispatch_non_tty_still_sees_notice(monkeypatch, capsys, tmp_path, fixtures_dir):
    _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    assert not sys.stderr.isatty()  # capsys replaces stderr with a non-TTY buffer
    cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert out.err.endswith(_expected_notice("1.7.1"))  # TTY inversion: shown anyway


# ---------------------------------------------------------------------------
# Dispatch — GREEN at baseline (absence the tool already exhibits; regression locks)
# ---------------------------------------------------------------------------


def test_dispatch_version_flag_never_emits_notice(monkeypatch, capsys, tmp_path):
    """`docs --version` SystemExits inside argument parsing — before the
    post-dispatch hook — so it never emits the update notice, even with the
    offline guard cleared and a strictly-newer version available. GREEN at
    baseline (no hook exists yet → trivially silent); becomes a real
    hook-placement lock once the Phase-5/6 post-dispatch hook lands.
    """
    _prep_dispatch(monkeypatch, tmp_path)
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))  # strictly newer than CURRENT
    with pytest.raises(SystemExit):
        cli.main(["--version"])  # argparse version action exits before dispatch
    out = capsys.readouterr()
    assert "docs: update available" not in out.err


def test_dispatch_same_version_is_silent(monkeypatch, capsys, tmp_path, fixtures_dir):
    _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _patch_fetch(monkeypatch, _FetchSpy(version=CURRENT))
    cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert "docs: update available" not in out.err


def test_dispatch_older_latest_is_silent(monkeypatch, capsys, tmp_path, fixtures_dir):
    _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _patch_fetch(monkeypatch, _FetchSpy(version="0.0.1"))
    cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert "docs: update available" not in out.err


def test_dispatch_fresh_cache_skips_network(monkeypatch, capsys, tmp_path, fixtures_dir):
    cache_home = _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _write_dispatch_cache(cache_home, last_check=_iso_hours_ago(1), latest_version=CURRENT)
    spy = _FetchSpy(version="1.7.1")
    _patch_fetch(monkeypatch, spy)
    cli.main(["list", "--root", str(tree)])
    capsys.readouterr()
    assert spy.calls == 0  # fresh last_check → no network


def test_dispatch_json_keeps_stdout_clean_and_suppresses_notice(
    monkeypatch, capsys, tmp_path, fixtures_dir
):
    _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    code = cli.main(["list", "--json", "--root", str(tree)])
    out = capsys.readouterr()
    assert code == 0
    parsed = json.loads(out.out)  # stdout stays byte-clean parseable JSON
    assert isinstance(parsed, list)
    assert "docs: update available" not in out.err


def test_dispatch_ci_env_silent_and_no_network(monkeypatch, capsys, tmp_path, fixtures_dir):
    _prep_dispatch(monkeypatch, tmp_path)
    monkeypatch.setenv("CI", "true")
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    spy = _FetchSpy(version="1.7.1")
    _patch_fetch(monkeypatch, spy)
    cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert spy.calls == 0
    assert "docs: update available" not in out.err


def test_dispatch_no_update_check_env_silent_and_no_network(
    monkeypatch, capsys, tmp_path, fixtures_dir
):
    _prep_dispatch(monkeypatch, tmp_path)
    monkeypatch.setenv("DOCS_CLI_NO_UPDATE_CHECK", "1")
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    spy = _FetchSpy(version="1.7.1")
    _patch_fetch(monkeypatch, spy)
    cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert spy.calls == 0
    assert "docs: update available" not in out.err


def test_dispatch_do_not_track_env_silent_and_no_network(
    monkeypatch, capsys, tmp_path, fixtures_dir
):
    _prep_dispatch(monkeypatch, tmp_path)
    monkeypatch.setenv("DO_NOT_TRACK", "1")
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    spy = _FetchSpy(version="1.7.1")
    _patch_fetch(monkeypatch, spy)
    cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert spy.calls == 0
    assert "docs: update available" not in out.err


def test_dispatch_offline_fetch_none_is_silent_exit_unchanged(
    monkeypatch, capsys, tmp_path, fixtures_dir
):
    _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _patch_fetch(monkeypatch, _FetchSpy(version=None))  # offline → fetch returns None
    code = cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert code == 0
    assert "docs: update available" not in out.err


def test_dispatch_offline_fetch_none_writes_no_cache(monkeypatch, capsys, tmp_path, fixtures_dir):
    cache_home = _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _patch_fetch(monkeypatch, _FetchSpy(version=None))  # offline → fetch returns None
    code = cli.main(["list", "--root", str(tree)])
    capsys.readouterr()
    assert code == 0
    # A None fetch is neither a successful check nor an emit, so `if fetched or
    # notified: write_cache(...)` is False → nothing is persisted (no file at
    # all here, since there was no pre-existing cache). last_check never advances.
    assert _read_dispatch_cache(cache_home) is None


def test_dispatch_offline_reprobes_each_invocation(monkeypatch, capsys, tmp_path, fixtures_dir):
    _prep_dispatch(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    spy = _FetchSpy(version=None)  # permanently offline
    _patch_fetch(monkeypatch, spy)
    cli.main(["list", "--root", str(tree)])
    cli.main(["list", "--root", str(tree)])
    capsys.readouterr()
    # The first None fetch left last_check unwritten, so the second invocation
    # is still stale and re-probes — the resolved-Q2 bounded offline-retry
    # property (each call pays the network attempt until a success persists).
    assert spy.calls == 2


# ===========================================================================
# M23 (D5) — recorded-dest skill-refresh hint on M21's notice channel.
#
# Phase 2 (RED). The hint rides M21's exact STDERR channel: appended only when
# the CLI notice actually prints, under the same suppression matrix + 24h
# last_notified throttle. It replays the recorded dest verbatim (no fs check).
# Every test points XDG_STATE_HOME at tmp so no test reads the real
# ~/.local/state; the recorded dest is seeded inline (date-independent).
#
# INVARIANT: the M21 dispatch tests above run list/check/touch — never
# install-skill — so they never record a dest; with XDG_STATE at a fresh tmp
# (or unseeded), read_recorded_dest() is None and their endswith(_expected_
# notice) locks stay GREEN. M23 must never record a dest on a non-install-skill
# path.
# ===========================================================================


def _prep_state(monkeypatch: Any, tmp_path: Path) -> Path:
    """Point XDG_STATE_HOME at a tmp dir; return the state-home directory."""
    state_home = tmp_path / "xdg-state"
    monkeypatch.setenv("XDG_STATE_HOME", str(state_home))
    return state_home


def _write_recorded_dest(state_home: Path, dest: str) -> Path:
    """Seed `$XDG_STATE_HOME/docs-cli/install-skill.json` with a recorded dest."""
    state_dir = state_home / "docs-cli"
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / "install-skill.json"
    path.write_text(json.dumps({"dest": dest}), encoding="utf-8")
    return path


def _expected_hint(dest: str) -> str:
    """The byte-exact emitted stderr hint line (formatter output + \\n)."""
    return (
        f"docs: refresh the agent skill at {dest} — run: docs install-skill --dest {dest} --force\n"
    )


# ---------------------------------------------------------------------------
# Spec-content lock (AF-1) — GREEN at baseline (Phase 1 pinned the template)
# ---------------------------------------------------------------------------


def test_cli_md_pins_skill_hint_template():
    """cli.md carries the byte-exact skill-refresh hint template (AF-1)."""
    cli_md = (REPO_ROOT / "docs" / "cli.md").read_text(encoding="utf-8")
    assert (
        "docs: refresh the agent skill at <dest> — run: docs install-skill --dest <dest> --force"
        in cli_md
    )


# ---------------------------------------------------------------------------
# Unit — SKILL_HINT_TEMPLATE / format_skill_hint seam (RED until Phase 5)
# ---------------------------------------------------------------------------


def test_skill_hint_template_and_formatter_seam():
    assert hasattr(uc, "SKILL_HINT_TEMPLATE"), "SKILL_HINT_TEMPLATE not implemented (Phase 5)"
    assert hasattr(uc, "format_skill_hint"), "format_skill_hint not implemented (Phase 5)"
    assert uc.format_skill_hint("/x") == uc.SKILL_HINT_TEMPLATE.format(dest="/x")


def test_format_skill_hint_is_byte_exact_without_trailing_newline():
    assert hasattr(uc, "format_skill_hint"), "format_skill_hint not implemented (Phase 5)"
    hint = uc.format_skill_hint("/a/b")
    assert hint == (
        "docs: refresh the agent skill at /a/b — run: docs install-skill --dest /a/b --force"
    )
    assert not hint.endswith("\n")


# ---------------------------------------------------------------------------
# Dispatch — hint present / absent (RED / GREEN at baseline)
# ---------------------------------------------------------------------------


def test_dispatch_recorded_dest_appends_skill_hint(monkeypatch, capsys, tmp_path, fixtures_dir):
    """Recorded dest + newer version → CLI line AND the byte-exact hint as the
    LAST stderr line, exactly once; neither line on stdout (RED)."""
    _prep_dispatch(monkeypatch, tmp_path)
    state_home = _prep_state(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    dest = "/home/agent/.claude/skills/docs"
    _write_recorded_dest(state_home, dest)
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    code = cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert code == 0
    assert "docs: update available" in out.err  # the CLI line is still there
    assert out.err.endswith(_expected_hint(dest))  # hint is the LAST line, byte-exact + \n
    assert out.err.count("docs: refresh the agent skill") == 1  # exactly once
    assert "docs: refresh the agent skill" not in out.out  # never on stdout
    assert "docs: update available" not in out.out


def test_dispatch_no_recorded_dest_emits_cli_line_only(monkeypatch, capsys, tmp_path, fixtures_dir):
    """No recorded dest + newer version → only the CLI line (M21 unchanged).

    GREEN at baseline: this is exactly today's M21 behaviour.
    """
    _prep_dispatch(monkeypatch, tmp_path)
    _prep_state(monkeypatch, tmp_path)  # XDG_STATE at tmp, but nothing recorded
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert out.err.endswith(_expected_notice("1.7.1"))  # CLI line is the last line
    assert "docs: refresh the agent skill" not in out.err


def test_dispatch_recorded_dest_replayed_verbatim(monkeypatch, capsys, tmp_path, fixtures_dir):
    """A recorded dest that does not exist on disk is still replayed verbatim —
    no stat/existence check (AF-2) (RED)."""
    _prep_dispatch(monkeypatch, tmp_path)
    state_home = _prep_state(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    dest = "/nonexistent/path/does/not/exist/skills/docs"
    _write_recorded_dest(state_home, dest)
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert out.err.endswith(_expected_hint(dest))  # exact path replayed, no fs check


# ---------------------------------------------------------------------------
# Dispatch — the hint is coupled to the CLI notice (suppression + throttle)
# ---------------------------------------------------------------------------


def test_dispatch_json_suppresses_hint_and_cli(monkeypatch, capsys, tmp_path, fixtures_dir):
    """`--json` suppresses BOTH the CLI line and the hint; stdout stays clean."""
    _prep_dispatch(monkeypatch, tmp_path)
    state_home = _prep_state(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _write_recorded_dest(state_home, "/x/dest")
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    code = cli.main(["list", "--json", "--root", str(tree)])
    out = capsys.readouterr()
    assert code == 0
    json.loads(out.out)  # stdout stays byte-clean JSON
    assert "docs: update available" not in out.err
    assert "docs: refresh the agent skill" not in out.err


def test_dispatch_quiet_suppresses_hint_and_cli(monkeypatch, capsys, tmp_path, fixtures_dir):
    """`--quiet` suppresses BOTH the CLI line and the hint (touch supports it)."""
    _prep_dispatch(monkeypatch, tmp_path)
    state_home = _prep_state(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _write_recorded_dest(state_home, "/x/dest")
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    code = cli.main(["touch", str(tree / "lone-doc.md"), "--root", str(tree), "--quiet"])
    out = capsys.readouterr()
    assert code == 0
    assert "docs: update available" not in out.err
    assert "docs: refresh the agent skill" not in out.err


@pytest.mark.parametrize("env_key", ["CI", "DOCS_CLI_NO_UPDATE_CHECK", "DO_NOT_TRACK"])
def test_dispatch_env_suppression_silences_hint_and_cli(
    env_key, monkeypatch, capsys, tmp_path, fixtures_dir
):
    """Each env kill-switch suppresses BOTH the CLI line and the hint."""
    _prep_dispatch(monkeypatch, tmp_path)
    monkeypatch.setenv(env_key, "1")
    state_home = _prep_state(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _write_recorded_dest(state_home, "/x/dest")
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert "docs: update available" not in out.err
    assert "docs: refresh the agent skill" not in out.err


def test_dispatch_fresh_last_notified_throttles_hint_too(
    monkeypatch, capsys, tmp_path, fixtures_dir
):
    """A fresh `last_notified` throttles the CLI notice — and the hint with it
    (the hint shares the SAME throttle, no independent budget) (AF-3)."""
    cache_home = _prep_dispatch(monkeypatch, tmp_path)
    state_home = _prep_state(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _write_dispatch_cache(
        cache_home,
        last_check=_iso_hours_ago(25),  # stale → check runs
        latest_version=CURRENT,
        last_notified=_iso_hours_ago(1),  # fresh → notice (and hint) throttled
    )
    _write_recorded_dest(state_home, "/x/dest")
    _patch_fetch(monkeypatch, _FetchSpy(version="1.7.1"))
    cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert "docs: update available" not in out.err  # CLI throttled
    assert "docs: refresh the agent skill" not in out.err  # hint coupled → also silent


def test_dispatch_current_version_emits_no_hint(monkeypatch, capsys, tmp_path, fixtures_dir):
    """When the CLI is current (no CLI notice), no hint is emitted even with a
    recorded dest (the hint never fires on its own) (AF-3)."""
    _prep_dispatch(monkeypatch, tmp_path)
    state_home = _prep_state(monkeypatch, tmp_path)
    tree = _copy_tree(fixtures_dir, "minimal", tmp_path)
    _write_recorded_dest(state_home, "/x/dest")
    _patch_fetch(monkeypatch, _FetchSpy(version=CURRENT))  # not newer → no CLI notice
    cli.main(["list", "--root", str(tree)])
    out = capsys.readouterr()
    assert "docs: update available" not in out.err
    assert "docs: refresh the agent skill" not in out.err
