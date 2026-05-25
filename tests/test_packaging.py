"""End-to-end packaging tests for the M6 PyPI distribution.

M6 ships `docs-cli` as a Python distribution: a real `[build-system]`,
a `docs_cli` package, a `docs` console-script entry point, and a bundled
Claude Code skill that the new `docs install-skill` verb materialises on
a host. None of that can be verified by an in-tree green run — a missing
`package-data` glob, a broken entry-point string, or a wheel that omits
the skill all leave the in-tree suite green while breaking every real
install. This file is the test no in-tree green run can replace.

The tests are RED at Phase 4 (the contract is declared, nothing is
implemented yet) and turn GREEN incrementally through Phases 5–6 as the
relocation and the packaging surface land. The intended-RED matrix lives
in `docs/m6-pypi-distribution.md` (Testing / Quality Gate section); each
test below is annotated with its intended RED reason.

Group A — `pyproject.toml` static contract
Group B — wheel / sdist build artefacts
Group C — installed CLI surface (--version, --help)
Group D — `docs install-skill` verb
Group E — installed `docs` against fixture trees
Group F — repo-layout invariants (package shape; legacy paths removed)

Test design:
- `built_dist` (session-scoped): runs `python -m build` once in a tmp_path,
  produces both wheel and sdist. Every later test that needs an artifact
  reuses these files via the fixture.
- `wheel_venv` (session-scoped): creates a throwaway venv with
  `venv.EnvBuilder`, pip-installs the wheel from `built_dist`, and yields
  the path to its `bin/docs` entry point. Every C/D/E test reuses this.

`pytest.importorskip("build")` at module load: M6 added `build` to the
`[dev]` extra (per Step 1 OQ-D); if a contributor's venv predates that
edit, the suite skips packaging tests cleanly instead of crashing.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tomllib
import venv
import zipfile
from pathlib import Path

import pytest

# Required by every B/C/D/E test — `python -m build` actually has to import.
build = pytest.importorskip("build", reason="`build` required for M6 packaging tests")

from docs import _build_parser  # noqa: E402, I001  (conftest-aliased; load after importorskip)


REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"

# The skill source under the package layout. Phase 5 moves
# `skills/docs/` → `src/docs_cli/skill/`; until then, this path does not
# exist and the F1/F2/F3 layout checks are RED on purpose.
PKG_SKILL_DIR = REPO_ROOT / "src" / "docs_cli" / "skill"


# --- Group A: pyproject.toml static contract --------------------------------


def _load_pyproject() -> dict:
    """Read `pyproject.toml` once per test (cheap; <1ms)."""
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def test_a1_build_system_is_hatchling() -> None:
    """A1: `[build-system]` declares hatchling.

    Intended RED reason: `pyproject.toml` has no `[build-system]` table
    at Phase 4 (Phase 6 adds it). Asserts the table exists and
    `requires` mentions `hatchling`.
    """
    data = _load_pyproject()
    assert "build-system" in data, "[build-system] table is missing from pyproject.toml"
    bs = data["build-system"]
    assert "requires" in bs, "[build-system].requires is missing"
    requires_str = " ".join(bs["requires"]).lower()
    assert "hatchling" in requires_str, (
        f"[build-system].requires must include hatchling; got {bs['requires']!r}"
    )


def test_a2_project_name_is_docs_cli() -> None:
    """A2: `[project].name` is `docs-cli`.

    Intended RED reason: Phase 4 pyproject still says `name = "docs"`.
    """
    data = _load_pyproject()
    assert data["project"]["name"] == "docs-cli", (
        f"[project].name must be 'docs-cli'; got {data['project']['name']!r}"
    )


def test_a3_project_version_is_1_3_0() -> None:
    """A3: `[project].version` is `1.3.0`.

    Intended RED reason: Phase 4 pyproject still says
    `version = "0.2.0-m2"`. Phase 6 bumps it.
    """
    data = _load_pyproject()
    assert data["project"]["version"] == "1.3.0", (
        f"[project].version must be '1.3.0'; got {data['project']['version']!r}"
    )


def test_a4_console_script_entry_point_present() -> None:
    """A4: `[project.scripts].docs` points at `docs_cli.cli:main`.

    Intended RED reason: Phase 4 pyproject has no `[project.scripts]`
    table. Phase 6 adds it.
    """
    data = _load_pyproject()
    scripts = data["project"].get("scripts", {})
    assert "docs" in scripts, (
        "[project.scripts].docs entry-point missing; wheel cannot install a `docs` command"
    )
    assert scripts["docs"] == "docs_cli.cli:main", (
        f"docs entry-point must be 'docs_cli.cli:main'; got {scripts['docs']!r}"
    )


def test_a5_project_urls_present() -> None:
    """A5: `[project.urls]` declares Homepage / Repository / Issues.

    Intended RED reason: Phase 4 pyproject has no `[project.urls]`.
    PyPI surface metadata is part of the publishable contract.
    """
    data = _load_pyproject()
    urls = data["project"].get("urls", {})
    expected = {"Homepage", "Repository", "Issues"}
    missing = expected - set(urls.keys())
    assert not missing, f"[project.urls] missing keys: {sorted(missing)}"


def test_a6_hatch_build_packages_the_skill() -> None:
    """A6: hatchling is configured to package the bundled skill.

    Per Step 1 OQ-K this asserts loosely: any `[tool.hatch.build...]`
    table mentions 'skill' (e.g. `force-include`, `include`,
    `artifacts`, `package-data`, or a hatchling-specific table). The
    strict shape lands at Phase 6 when hatchling is actually wired.

    Intended RED reason: Phase 4 has no hatch configuration at all.
    """
    text = PYPROJECT.read_text(encoding="utf-8")
    # Look for any [tool.hatch.build...] block referencing "skill".
    # Both straight-prose and TOML constructs (include/force-include lists)
    # land under this loose match.
    found = False
    in_hatch_build = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[tool.hatch.build"):
            in_hatch_build = True
            continue
        if (
            in_hatch_build
            and stripped.startswith("[")
            and not stripped.startswith("[tool.hatch.build")
        ):
            in_hatch_build = False
        if in_hatch_build and "skill" in stripped.lower():
            found = True
            break
    assert found, (
        "expected a [tool.hatch.build...] table mentioning 'skill' "
        "(force-include / include / artifacts / package-data); none found"
    )


# A7 — `[dev]` extra includes `build` — DEFERRED (Step 1 OQ-A7-SKIP).
# Step 1's plan defers the dev-extra-contract decision to Phase 6.


# --- Group B: wheel and sdist build artefacts -------------------------------


@pytest.fixture(scope="session")
def built_dist(tmp_path_factory: pytest.TempPathFactory) -> dict:
    """Run `python -m build` once per session; cache wheel + sdist paths.

    Returns a dict with `wheel`, `sdist`, `outdir`. Tests that depend on
    a successful build acquire this fixture; tests that exercise the
    pre-build state (Group A) do not.

    Build failure surfaces as a pytest setup error — distinguishable
    from an in-test assertion failure, which is what Phase 4 wants:
    "build fails because no [build-system]" is the *intended* RED.
    """
    outdir = tmp_path_factory.mktemp("dist")
    cmd = [sys.executable, "-m", "build", "--outdir", str(outdir), str(REPO_ROOT)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        pytest.fail(
            "`python -m build` failed (this is the intended Phase-4 RED "
            f"if no [build-system] is declared):\nstdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    wheels = sorted(outdir.glob("docs_cli-*.whl"))
    sdists = sorted(outdir.glob("docs_cli-*.tar.gz"))
    if not wheels or not sdists:
        pytest.fail(
            f"build produced unexpected files (wheel={wheels}, sdist={sdists});\n"
            f"outdir contents: {sorted(p.name for p in outdir.iterdir())}"
        )
    return {"wheel": wheels[0], "sdist": sdists[0], "outdir": outdir}


def test_b1_wheel_builds(built_dist: dict) -> None:
    """B1: `python -m build` produces a wheel named `docs_cli-1.3.0-*.whl`.

    Intended RED reason: no `[build-system]` at Phase 4 — `python -m
    build` errors out. The fixture surfaces that as a pytest failure.
    """
    assert built_dist["wheel"].exists()
    assert built_dist["wheel"].name.startswith("docs_cli-1.3.0-"), (
        f"wheel filename must encode version 1.3.0; got {built_dist['wheel'].name}"
    )


def test_b2_sdist_builds(built_dist: dict) -> None:
    """B2: `python -m build` produces an sdist `docs_cli-1.3.0.tar.gz`.

    Intended RED reason: same as B1 — no build backend.
    """
    assert built_dist["sdist"].exists()
    assert built_dist["sdist"].name == "docs_cli-1.3.0.tar.gz", (
        f"sdist filename must be 'docs_cli-1.3.0.tar.gz'; got {built_dist['sdist'].name}"
    )


def test_b3_wheel_contains_cli_and_skill(built_dist: dict) -> None:
    """B3: wheel ships `docs_cli/cli.py` and the bundled skill tree.

    Intended RED reason: package data not declared / skill not relocated
    → wheel either fails to build or omits the skill directory.
    """
    with zipfile.ZipFile(built_dist["wheel"]) as zf:
        names = set(zf.namelist())
    assert "docs_cli/cli.py" in names, (
        f"wheel missing docs_cli/cli.py; entries:\n{sorted(names)[:20]}…"
    )
    assert "docs_cli/skill/SKILL.md" in names, (
        "wheel missing docs_cli/skill/SKILL.md — package-data glob is wrong "
        "or the skill was not relocated"
    )
    assert "docs_cli/skill/references/convention.md" in names, (
        "wheel missing docs_cli/skill/references/convention.md"
    )
    assert "docs_cli/skill/references/cli.md" in names, (
        "wheel missing docs_cli/skill/references/cli.md"
    )


def test_b4_entry_point_recorded_in_wheel(built_dist: dict) -> None:
    """B4: wheel's `entry_points.txt` registers `docs = docs_cli.cli:main`.

    Intended RED reason: no `[project.scripts]` at Phase 4 → no
    entry_points.txt in the wheel.
    """
    with zipfile.ZipFile(built_dist["wheel"]) as zf:
        entry_points_members = [n for n in zf.namelist() if n.endswith("entry_points.txt")]
        assert entry_points_members, (
            "wheel has no entry_points.txt — `[project.scripts]` not declared"
        )
        ep_text = zf.read(entry_points_members[0]).decode("utf-8")
    assert "docs = docs_cli.cli:main" in ep_text, (
        f"entry_points.txt missing `docs = docs_cli.cli:main`; got:\n{ep_text}"
    )


# --- Group C: installed CLI surface -----------------------------------------


@pytest.fixture(scope="session")
def wheel_venv(tmp_path_factory: pytest.TempPathFactory, built_dist: dict) -> Path:
    """Create a throwaway venv and pip-install the wheel into it.

    Yields the absolute path to the venv's `docs` entry-point script.
    Session-scoped so the (slow) venv-create + pip-install cost is paid
    once for the whole packaging-test run.
    """
    venv_dir = tmp_path_factory.mktemp("wheel_venv")
    venv.EnvBuilder(with_pip=True, clear=True).create(venv_dir)
    pip = venv_dir / "bin" / "pip"
    if not pip.exists():  # pragma: no cover — non-POSIX bench
        pytest.skip(f"venv pip not found at {pip}; this test assumes POSIX layout")
    result = subprocess.run(
        [str(pip), "install", "--quiet", str(built_dist["wheel"])],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail(
            f"pip install of {built_dist['wheel'].name} failed:\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    docs_bin = venv_dir / "bin" / "docs"
    if not docs_bin.exists():
        pytest.fail(
            f"`docs` entry-point not installed at {docs_bin}; [project.scripts] is missing or wrong"
        )
    return docs_bin


def test_c1_docs_on_path_in_venv(wheel_venv: Path) -> None:
    """C1: the installed venv has a `docs` entry point.

    Intended RED reason: no entry point → fixture fails.
    """
    assert wheel_venv.exists()
    assert wheel_venv.is_file()


def test_c2_docs_version_is_1_3_0(wheel_venv: Path) -> None:
    """C2: `docs --version` prints `1.3.0`.

    Intended RED reason: `__version__` is `0.4.0-m4` in `bin/docs` at
    Phase 4. Phase 6 bumps it.
    """
    result = subprocess.run(
        [str(wheel_venv), "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`docs --version` exited {result.returncode}:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    combined = (result.stdout + result.stderr).strip()
    # Exact-token match: bare substring `"1.3.0" in combined` would also
    # accept `21.3.0` or `1.3.0.dev0`. Split on whitespace and require the
    # version token to appear verbatim.
    tokens = combined.split()
    assert "1.3.0" in tokens, (
        f"`docs --version` must print '1.3.0' as a standalone token; got: {combined!r}"
    )


def test_c3_docs_help_lists_every_verb(wheel_venv: Path) -> None:
    """C3: `docs --help` documents every verb registered by `_build_parser`,
    plus `install-skill`.

    Per Step 1 OQ-O, the expected verb set is derived from the in-tree
    parser via `from docs import _build_parser` (conftest alias), so the
    test will follow the parser as Phase 6 adds `install-skill`.

    Intended RED reason: at Phase 4 there is no installed `docs` binary,
    so the wheel_venv fixture fails before this test runs.
    """
    parser = _build_parser()
    import argparse as _arg

    sub = next(
        a for a in parser._actions if isinstance(a, _arg._SubParsersAction) and a.dest == "command"
    )
    expected_verbs = set(sub.choices.keys()) | {"install-skill"}
    result = subprocess.run(
        [str(wheel_venv), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"`docs --help` exited {result.returncode}:\n{result.stderr}"
    out = result.stdout
    missing = {v for v in expected_verbs if v not in out}
    assert not missing, f"`docs --help` is missing verbs: {sorted(missing)}\nfull help:\n{out}"


# --- Group D: `docs install-skill` verb -------------------------------------


def test_d1_install_skill_subcommand_exists(wheel_venv: Path) -> None:
    """D1: `docs install-skill --help` exits 0.

    Intended RED reason: the verb does not exist at Phase 4 → argparse
    errors out with exit 2 ("invalid choice").
    """
    result = subprocess.run(
        [str(wheel_venv), "install-skill", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`docs install-skill --help` exited {result.returncode}:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def test_d2_install_skill_default_action_is_copy(wheel_venv: Path, tmp_path: Path) -> None:
    """D2: `docs install-skill --dest <tmp>` succeeds with default `--copy`.

    The destination is always explicit (`--dest <tmp>`) per Step 1
    OQ-H — the test must never trigger the `~/.claude/skills/docs/`
    default.

    Intended RED reason: verb does not exist at Phase 4.
    """
    dest = tmp_path / "skill-out"
    result = subprocess.run(
        [str(wheel_venv), "install-skill", "--dest", str(dest)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"install-skill exited {result.returncode}:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert (dest / "SKILL.md").exists(), f"SKILL.md not materialised at {dest / 'SKILL.md'}"


def test_d3_install_skill_tree_is_byte_identical(wheel_venv: Path, tmp_path: Path) -> None:
    """D3: the materialised tree matches the in-repo source byte-for-byte.

    Intended RED reason: verb does not exist; also, `src/docs_cli/skill/`
    is not yet present until Phase 5 relocates it.
    """
    if not PKG_SKILL_DIR.exists():
        pytest.fail(
            f"in-repo source dir {PKG_SKILL_DIR} does not exist — "
            "Phase 5 has not relocated the skill yet"
        )
    dest = tmp_path / "skill-out"
    result = subprocess.run(
        [str(wheel_venv), "install-skill", "--dest", str(dest)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"install-skill exited {result.returncode}"
    for rel in (
        Path("SKILL.md"),
        Path("references") / "convention.md",
        Path("references") / "cli.md",
    ):
        src = PKG_SKILL_DIR / rel
        out = dest / rel
        assert out.exists(), f"{out} missing"
        assert src.read_bytes() == out.read_bytes(), f"materialised {rel} does not match {src}"


def test_d4_install_skill_is_idempotent(wheel_venv: Path, tmp_path: Path) -> None:
    """D4: running install-skill twice into the same dest exits 0 both times.

    Intended RED reason: verb does not exist.
    """
    dest = tmp_path / "skill-out"
    for invocation in ("first", "second"):
        result = subprocess.run(
            [str(wheel_venv), "install-skill", "--dest", str(dest)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"{invocation} invocation exited {result.returncode}:\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def test_d5_install_skill_refuses_non_identical_without_force(
    wheel_venv: Path, tmp_path: Path
) -> None:
    """D5: install-skill errors when the destination exists with different
    content, unless `--force` is given.

    Intended RED reason: verb does not exist.
    """
    dest = tmp_path / "skill-out"
    dest.mkdir()
    (dest / "SKILL.md").write_text("DIFFERENT CONTENT\n", encoding="utf-8")
    result = subprocess.run(
        [str(wheel_venv), "install-skill", "--dest", str(dest)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, (
        "install-skill must refuse a non-identical existing dest without --force; "
        f"exited {result.returncode}"
    )
    # On rejection, dest must be preserved byte-for-byte. A buggy
    # implementation that errored out partway through a non-atomic write
    # would still satisfy the non-zero-exit check above without this guard.
    assert (dest / "SKILL.md").read_text(encoding="utf-8") == "DIFFERENT CONTENT\n", (
        "install-skill must leave dest unchanged when refusing a non-identical "
        "existing destination without --force"
    )
    # And with --force, it succeeds.
    forced = subprocess.run(
        [str(wheel_venv), "install-skill", "--dest", str(dest), "--force"],
        capture_output=True,
        text=True,
    )
    assert forced.returncode == 0, (
        f"install-skill --force must succeed; exited {forced.returncode}:\nstderr:\n{forced.stderr}"
    )


def test_d6_install_skill_rejects_symlink_on_wheel_install(
    wheel_venv: Path, tmp_path: Path
) -> None:
    """D6: `--symlink` is rejected when running from a wheel install.

    A wheel-installed package's data files may not survive symlinks
    (read-only mounts, zip-import). The contract: `--symlink` errors on
    a wheel install, succeeds only for an editable install.

    Intended RED reason: verb does not exist.
    """
    dest = tmp_path / "skill-out"
    result = subprocess.run(
        [str(wheel_venv), "install-skill", "--dest", str(dest), "--symlink"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, (
        f"install-skill --symlink must be rejected on a wheel install; exited {result.returncode}"
    )


def test_d7_install_skill_default_dest_documented(wheel_venv: Path) -> None:
    """D7: `docs install-skill --help` documents the default dest as
    `~/.claude/skills/docs/`.

    Per Step 1 OQ-H, the test asserts the default via help text only —
    it never triggers the default (which would mutate the host).

    Intended RED reason: verb does not exist.
    """
    result = subprocess.run(
        [str(wheel_venv), "install-skill", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`docs install-skill --help` exited {result.returncode}:\n{result.stderr}"
    )
    out = result.stdout
    assert "~/.claude/skills/docs" in out, (
        f"default dest `~/.claude/skills/docs/` must appear in --help text;\ngot:\n{out}"
    )


# --- Group E: installed `docs` against fixture trees ------------------------


def test_e1_installed_docs_check_passes_minimal_fixture(wheel_venv: Path) -> None:
    """E1: `docs check tests/fixtures/trees/minimal/` exits 0.

    Per Phase 3 (Step 1 plan, Option A), the existing minimal fixture is
    reused for the installed-docs-check smoke; `./bin/docs check` against
    it exits 0 in-tree at Phase 1, so the GREEN expectation is symmetric.

    Intended RED reason: no installed `docs` at Phase 4.
    """
    fixture = REPO_ROOT / "tests" / "fixtures" / "trees" / "minimal"
    result = subprocess.run(
        [str(wheel_venv), "check", str(fixture)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"installed `docs check` exited {result.returncode} on {fixture}:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def test_e2_installed_docs_index_dry_run_clean(wheel_venv: Path) -> None:
    """E2: `docs index --root <fixture> --dry-run` exits 0 with no errors.

    Intended RED reason: no installed `docs` at Phase 4.
    """
    fixture = REPO_ROOT / "tests" / "fixtures" / "trees" / "minimal"
    result = subprocess.run(
        [str(wheel_venv), "index", "--root", str(fixture), "--dry-run"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"installed `docs index --dry-run` exited {result.returncode}:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


# --- Group F: repo-layout invariants ----------------------------------------


def test_f1_src_docs_cli_layout() -> None:
    """F1: `src/docs_cli/{__init__.py, cli.py, skill/SKILL.md}` exist.

    Intended RED reason: nothing relocated at Phase 4. Phase 5 moves
    `bin/docs` → `src/docs_cli/cli.py`, creates `__init__.py`, moves
    `skills/docs/` → `src/docs_cli/skill/`.
    """
    expected = (
        REPO_ROOT / "src" / "docs_cli" / "__init__.py",
        REPO_ROOT / "src" / "docs_cli" / "cli.py",
        REPO_ROOT / "src" / "docs_cli" / "skill" / "SKILL.md",
    )
    missing = [str(p.relative_to(REPO_ROOT)) for p in expected if not p.exists()]
    assert not missing, f"package layout missing: {missing}"


def test_f2_top_level_skills_docs_removed() -> None:
    """F2: top-level `skills/docs/` is gone after the OQ4 relocation.

    Intended RED reason: at Phase 4 the directory still exists.
    """
    assert not (REPO_ROOT / "skills" / "docs").exists(), (
        "top-level skills/docs/ must be removed (single source of truth "
        "under src/docs_cli/skill/ per OQ4)"
    )


def test_f3_bin_docs_removed() -> None:
    """F3: `bin/docs` is gone after the OQ5 deletion.

    Intended RED reason: at Phase 4 the file still exists (Phase 5
    deletes it).
    """
    assert not (REPO_ROOT / "bin" / "docs").exists(), (
        'bin/docs must be removed (OQ5 — contributors use `pip install -e ".[dev]"`)'
    )


# Quiet ruff about the unused `shutil` import — keep handy for the GREEN-side
# Phase 5 file moves a future test author may add.
_ = shutil
