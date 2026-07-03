"""M23 — Agent-aware install-skill dest resolution + recorded-dest state.

Phase 2 (RED). All in-process (``cli.main([...])``) and fully offline:

- ``XDG_STATE_HOME`` is pointed at ``tmp_path`` so no test reads or writes the
  real ``~/.local/state``; ``HOME`` is pointed at ``tmp_path`` whenever
  ``--dest`` is omitted so the ``~/.claude/skills/docs/`` default lands inside
  ``tmp_path`` and never clobbers the host's real skill.
- The M21 update-check stays disabled for this file (conftest sets
  ``DOCS_CLI_NO_UPDATE_CHECK=1`` and these tests never clear it), so
  ``install-skill`` runs never reach the network.

The seams these tests pin (implemented in Phases 5–6):

- ``cli.py``: ``--dest`` defaults to ``None`` + a module const
  ``_DEFAULT_SKILL_DEST``; a TTY-aware ``_resolve_install_dest(args)``;
  ``_cmd_install_skill`` records the resolved dest on exit 0.
- ``update_check.py``: ``state_path()`` / ``read_recorded_dest()`` /
  ``write_recorded_dest()`` (path-only per-user state, fail-silent).

Until those land, the ``hasattr`` guards below fail cleanly with a
"not implemented (Phase 5)" message rather than raising a collection error.
"""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any

from docs_cli import cli

# update_check already exists (M21); the M23 state helpers do not yet. Import
# defensively so a future refactor that (re)moves the module still yields a
# clean assertion failure rather than a collection error.
uc: Any
try:
    uc = importlib.import_module("docs_cli.update_check")
except ModuleNotFoundError:  # pragma: no cover — module ships with M21
    uc = None

_NOT_IMPL_STATE = "update_check dest-state helpers not yet implemented (Phase 5)"


# ---------------------------------------------------------------------------
# Phase-3 inline builders (date-independent; no committed fixtures)
# ---------------------------------------------------------------------------


def _prep_state(monkeypatch: Any, tmp_path: Path) -> Path:
    """Point XDG_STATE_HOME at a tmp dir; return the state-home directory."""
    state_home = tmp_path / "xdg-state"
    monkeypatch.setenv("XDG_STATE_HOME", str(state_home))
    return state_home


def _prep_home(monkeypatch: Any, tmp_path: Path) -> Path:
    """Point HOME at a tmp dir so the ``~/.claude/skills/docs/`` default is
    contained inside tmp; return the default dest that resolves under it."""
    home = tmp_path / "home"
    home.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(home))
    return (home / ".claude" / "skills" / "docs").resolve()


def _state_file(state_home: Path) -> Path:
    return state_home / "docs-cli" / "install-skill.json"


def _read_state_raw(state_home: Path) -> dict | None:
    """The recorded-dest JSON as a dict, or None if the file is absent."""
    path = _state_file(state_home)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _install_skill_subparser() -> argparse.ArgumentParser:
    """The `install-skill` subparser object from the real parser tree."""
    parser = cli._build_parser()
    sub = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    return sub.choices["install-skill"]


def _install_skill_short_help() -> str:
    """The one-line ``help=`` string argparse shows in the parent listing."""
    parser = cli._build_parser()
    sub = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    for action in sub._choices_actions:  # pseudo-actions carrying `.help`
        if action.dest == "install-skill":
            return action.help or ""
    return ""


def _raise_input(*_a: Any, **_k: Any) -> str:
    raise AssertionError("install-skill must not prompt in this scenario")


# ---------------------------------------------------------------------------
# D1 — `--dest` is the agent-agnostic source of truth (explicit → no prompt)
# ---------------------------------------------------------------------------


def test_d1_explicit_dest_installs_and_never_prompts(tmp_path, monkeypatch):
    """An explicit ``--dest`` installs there and never prompts (input raises)."""
    _prep_state(monkeypatch, tmp_path)
    monkeypatch.setattr("builtins.input", _raise_input)
    dest = tmp_path / "explicit-dest"
    code = cli.main(["install-skill", "--dest", str(dest), "--copy"])
    assert code == 0
    assert (dest / "SKILL.md").exists(), f"skill not materialised at {dest}"


# ---------------------------------------------------------------------------
# D2 — TTY-aware resolution when `--dest` is omitted
# ---------------------------------------------------------------------------


def test_d2_tty_prompt_installs_at_prompted_dest(tmp_path, monkeypatch):
    """On a TTY with `--dest` omitted, the prompted answer is used (RED).

    At the baseline `--dest` still carries a static default so the prompt is
    never consulted and the skill lands at the default — this fails until the
    Phase-6 TTY-aware resolver honours the prompted answer.
    """
    _prep_state(monkeypatch, tmp_path)
    _prep_home(monkeypatch, tmp_path)
    prompted = tmp_path / "prompted-dest"
    monkeypatch.setattr("sys.stdin.isatty", lambda: True, raising=False)
    monkeypatch.setattr("builtins.input", lambda *_a, **_k: str(prompted))
    code = cli.main(["install-skill", "--copy"])
    assert code == 0
    assert (prompted / "SKILL.md").exists(), "TTY prompt answer must be used as the dest"


def test_d2_tty_empty_input_accepts_default(tmp_path, monkeypatch):
    """On a TTY, empty input accepts the `~/.claude/skills/docs/` default."""
    _prep_state(monkeypatch, tmp_path)
    default_dest = _prep_home(monkeypatch, tmp_path)
    monkeypatch.setattr("sys.stdin.isatty", lambda: True, raising=False)
    monkeypatch.setattr("builtins.input", lambda *_a, **_k: "")
    code = cli.main(["install-skill", "--copy"])
    assert code == 0
    assert (default_dest / "SKILL.md").exists(), (
        f"empty prompt must fall back to the default dest {default_dest}"
    )


def test_d2_non_tty_never_blocks_uses_default(tmp_path, monkeypatch):
    """On a non-TTY with `--dest` omitted, resolution never prompts and uses
    the default (OQ-1 = default; preserves the M6 non-TTY behaviour)."""
    _prep_state(monkeypatch, tmp_path)
    default_dest = _prep_home(monkeypatch, tmp_path)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False, raising=False)
    monkeypatch.setattr("builtins.input", _raise_input)  # a prompt would raise
    code = cli.main(["install-skill", "--copy"])
    assert code == 0
    assert (default_dest / "SKILL.md").exists(), (
        f"non-TTY must fall back to the default dest {default_dest}, never block"
    )


# ---------------------------------------------------------------------------
# D3 — record the resolved dest (path only; no content/hash)
# ---------------------------------------------------------------------------


def test_d3_copy_success_records_dest_path_only(tmp_path, monkeypatch):
    """A successful copy records exactly ``{"dest": <resolved-abs-path>}`` —
    no content, no hash key (RED until the Phase-6 recording lands)."""
    state_home = _prep_state(monkeypatch, tmp_path)
    dest = tmp_path / "explicit-dest"
    code = cli.main(["install-skill", "--dest", str(dest), "--copy"])
    assert code == 0
    assert hasattr(uc, "read_recorded_dest"), _NOT_IMPL_STATE
    assert uc.read_recorded_dest() == str(dest.resolve())
    raw = _read_state_raw(state_home)
    assert raw == {"dest": str(dest.resolve())}
    assert "hash" not in raw and "content" not in raw, (
        "the state file records a path only — never content or a hash"
    )


def test_d3_noop_also_records(tmp_path, monkeypatch):
    """An already-identical no-op (exit 0) also records the dest (RED)."""
    state_home = _prep_state(monkeypatch, tmp_path)
    dest = tmp_path / "explicit-dest"
    assert cli.main(["install-skill", "--dest", str(dest), "--copy"]) == 0
    # Blow away the state file so the second (no-op) run must re-record it.
    _state_file(state_home).unlink(missing_ok=True)
    code = cli.main(["install-skill", "--dest", str(dest), "--copy"])
    assert code == 0  # byte-identical dest → no-op
    assert hasattr(uc, "read_recorded_dest"), _NOT_IMPL_STATE
    assert uc.read_recorded_dest() == str(dest.resolve()), (
        "an already-identical no-op must still record the resolved dest"
    )


def test_d3_refusal_records_nothing(tmp_path, monkeypatch):
    """A refusal (non-identical dest, no --force → exit 2) records nothing."""
    state_home = _prep_state(monkeypatch, tmp_path)
    dest = tmp_path / "occupied-dest"
    dest.mkdir()
    (dest / "SKILL.md").write_text("DIFFERENT CONTENT\n", encoding="utf-8")
    code = cli.main(["install-skill", "--dest", str(dest)])
    assert code == 2  # refusal
    assert _read_state_raw(state_home) is None, "a refusal must record nothing"


def test_d3_omitted_dest_records_resolved_default_path(tmp_path, monkeypatch):
    """An install with ``--dest`` OMITTED records the *resolved* default path —
    the fully-expanded absolute dest, never ``None`` and never an unexpanded
    ``~`` (RED until the Phase-6 recording lands).

    This pins that recording keys off the *resolved* dest the resolver picked,
    not the raw ``args.dest``: on a non-TTY the default is used (OQ-1), and what
    lands in the state file must be the expanded ``~/.claude/skills/docs``
    absolute path — the same value the D5 hint later replays."""
    state_home = _prep_state(monkeypatch, tmp_path)
    default_dest = _prep_home(monkeypatch, tmp_path)  # resolved default under tmp HOME
    monkeypatch.setattr("sys.stdin.isatty", lambda: False, raising=False)  # non-TTY → default
    monkeypatch.setattr("builtins.input", _raise_input)  # and never prompts
    code = cli.main(["install-skill", "--copy"])
    assert code == 0
    assert hasattr(uc, "read_recorded_dest"), _NOT_IMPL_STATE
    recorded = uc.read_recorded_dest()
    assert recorded == str(default_dest), (
        "an omitted --dest must record the RESOLVED default path, "
        "not None and not an unexpanded '~'"
    )
    assert recorded is not None and "~" not in recorded
    assert _read_state_raw(state_home) == {"dest": str(default_dest)}


def test_d3_symlink_success_records_dest(tmp_path, monkeypatch):
    """A successful ``--symlink`` install (editable install → symlink succeeds)
    also records the resolved dest path (RED until Phase-6 recording lands).

    ``cli.md``'s *Recorded destination* prose lists a symlink among the success
    triggers, so the symlink path must record just like copy — this pins it."""
    state_home = _prep_state(monkeypatch, tmp_path)
    dest = tmp_path / "symlink-dest"
    # Capture the expected recorded value BEFORE the symlink exists: the
    # implementation records ``Path(expanduser(dest)).resolve()`` computed while
    # dest is still absent, so resolving it now (nothing to follow) matches;
    # resolving AFTER creation would chase the symlink to the source.
    expected = str(dest.resolve())
    code = cli.main(["install-skill", "--dest", str(dest), "--symlink"])
    assert code == 0, "editable install → --symlink must succeed"
    assert dest.is_symlink(), "the --symlink path must create a symlink"
    assert hasattr(uc, "read_recorded_dest"), _NOT_IMPL_STATE
    assert uc.read_recorded_dest() == expected
    assert _read_state_raw(state_home) == {"dest": expected}


# ---------------------------------------------------------------------------
# D4 — reworded help: "agent skill", never "Claude Code"
# ---------------------------------------------------------------------------


def test_d4_install_skill_description_says_agent_skill_not_claude_code():
    """The subparser description says "agent skill", never "Claude Code" (RED)."""
    help_text = _install_skill_subparser().format_help().lower()
    assert "agent skill" in help_text, "install-skill description must say 'agent skill'"
    assert "claude code" not in help_text, "install-skill description must not name 'Claude Code'"


def test_d4_install_skill_short_help_says_agent_skill_not_claude_code():
    """The one-line ``help=`` says "agent skill", never "Claude Code" (RED)."""
    short = _install_skill_short_help()
    assert "agent skill" in short.lower(), "short help must say 'agent skill'"
    assert "Claude Code" not in short, "short help must not name 'Claude Code'"


# ---------------------------------------------------------------------------
# State-file helpers (path-only per-user state; fail-silent)
# ---------------------------------------------------------------------------


def test_state_helpers_exist():
    for name in ("state_path", "read_recorded_dest", "write_recorded_dest"):
        assert hasattr(uc, name), f"update_check.{name} {_NOT_IMPL_STATE}"


def test_state_path_honours_xdg_state_home(tmp_path, monkeypatch):
    assert hasattr(uc, "state_path"), _NOT_IMPL_STATE
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    assert uc.state_path() == tmp_path / "docs-cli" / "install-skill.json"


def test_state_path_defaults_to_local_state_when_xdg_unset(tmp_path, monkeypatch):
    assert hasattr(uc, "state_path"), _NOT_IMPL_STATE
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert uc.state_path() == tmp_path / ".local" / "state" / "docs-cli" / "install-skill.json"


def test_recorded_dest_roundtrips(tmp_path, monkeypatch):
    assert hasattr(uc, "write_recorded_dest") and hasattr(uc, "read_recorded_dest"), _NOT_IMPL_STATE
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    uc.write_recorded_dest("/some/abs/dest")
    assert uc.read_recorded_dest() == "/some/abs/dest"


def test_recorded_dest_last_write_wins(tmp_path, monkeypatch):
    assert hasattr(uc, "write_recorded_dest") and hasattr(uc, "read_recorded_dest"), _NOT_IMPL_STATE
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    uc.write_recorded_dest("/first")
    uc.write_recorded_dest("/second")
    assert uc.read_recorded_dest() == "/second"


def test_read_recorded_dest_missing_returns_none(tmp_path, monkeypatch):
    assert hasattr(uc, "read_recorded_dest"), _NOT_IMPL_STATE
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    assert uc.read_recorded_dest() is None


def test_read_recorded_dest_corrupt_returns_none(tmp_path, monkeypatch):
    assert hasattr(uc, "read_recorded_dest") and hasattr(uc, "state_path"), _NOT_IMPL_STATE
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    path = uc.state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"{not json")
    assert uc.read_recorded_dest() is None


def test_write_recorded_dest_unwritable_swallows_oserror(tmp_path, monkeypatch):
    assert hasattr(uc, "write_recorded_dest") and hasattr(uc, "state_path"), _NOT_IMPL_STATE
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    path = uc.state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Make the state *file path* a directory so opening it for write raises
    # IsADirectoryError (an OSError) — write must swallow it, never raise.
    path.mkdir()
    uc.write_recorded_dest("/x")  # must not raise
