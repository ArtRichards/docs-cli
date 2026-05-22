"""Unit tests for `query_docs` — the `docs list` query engine (Phase 2, RED).

All tests run against the `multi-project/` fixture tree, which spans several
projects, statuses, roles, and `Updated:` dates.
"""

from __future__ import annotations

from datetime import date
from itertools import groupby
from pathlib import Path

from docs import Config, load_config, query_docs

_TODAY = date(2026, 5, 22)


def _multi(fixtures_dir: Path) -> tuple[Path, Config]:
    root = fixtures_dir / "trees" / "multi-project"
    return root, load_config(root)


def _q(fixtures_dir: Path, **kw):
    root, config = _multi(fixtures_dir)
    kw.setdefault("status", None)
    kw.setdefault("role", None)
    kw.setdefault("project", None)
    kw.setdefault("stale", None)
    kw.setdefault("today", _TODAY)
    return query_docs(root, config, **kw)


def test_query_no_filters_returns_all_docs(fixtures_dir):
    docs = _q(fixtures_dir)
    # multi-project has 8 docs: 7 in the active tree + 1 archived.
    assert len(docs) == 8


def test_query_filter_by_status(fixtures_dir):
    docs = _q(fixtures_dir, status="active")
    assert docs
    assert all(d.status == "active" for d in docs)


def test_query_filter_by_role(fixtures_dir):
    docs = _q(fixtures_dir, role="spec")
    assert docs
    assert all(d.role == "spec" for d in docs)


def test_query_filter_by_project(fixtures_dir):
    docs = _q(fixtures_dir, project="alpha")
    assert docs
    assert all(d.project == "alpha" for d in docs)


def test_query_filter_by_project_includes_project_less_docs_under_default(fixtures_dir):
    # orphan.md carries no Project: line; it resolves to the root's project.
    docs = _q(fixtures_dir, project="multi-project")
    assert any(d.path.name == "orphan.md" for d in docs)


def test_query_filters_are_and_combined(fixtures_dir):
    docs = _q(fixtures_dir, project="beta", status="active")
    assert docs
    assert all(d.project == "beta" and d.status == "active" for d in docs)


def test_query_stale_filter(fixtures_dir):
    docs = _q(fixtures_dir, stale=90)
    assert docs
    assert all((_TODAY - d.updated).days > 90 for d in docs)


def test_query_sorted_within_group_by_updated_descending(fixtures_dir):
    docs = _q(fixtures_dir)
    for _key, group in groupby(docs, key=lambda d: (d.status, d.role)):
        dates = [d.updated for d in group]
        assert dates == sorted(dates, reverse=True)
