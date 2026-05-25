#!/usr/bin/env python3
"""Aggregate M7 success criteria from per-fixture `docs migrate --json` dumps.

Usage:
    python tests/manual/m7_success_criteria.py /tmp/m7-phase-9-*.json

Computes the 5 quantitative success metrics M7 pins (per
`docs/m7-migration-accuracy.md` Phase 9 / OQ-D / Trial-2):

  1. Confidence: (high + medium) / total >= 50%.
  2. Role fallback: `notes` / total <= 30%.
  3. Free-form `Status:` prose preservation: 100% of in-fixture
     foreign `Status:` lines either preserved in the body or
     captured as `Migrated-Status:`. (Reported per-tree because
     it depends on applying the plan; the JSON dump alone does
     not carry the apply-output. Phase 9 verifies via spot-apply
     against an archive-subdir fixture.)
  4. Archive moves: for trees with an `archived/` subdir, >= 80%
     of in-archive files carry an `archive_move`.
  5. Project-name normalisation: >= 90% of distinct inferred
     project values match the lowercase-kebab shape.

Lives under `tests/manual/` so pytest auto-collection does NOT
pick it up; it is an operator-runnable artefact reproducing the
M7 dogfood numbers on demand.

This script is stdlib-only and exits 0 on PASS, 1 on FAIL.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_KEBAB = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


def _load(paths: list[str]) -> dict[str, list[dict]]:
    per_tree: dict[str, list[dict]] = {}
    for p in paths:
        records = json.loads(Path(p).read_text())
        per_tree[Path(p).stem] = records
    return per_tree


def main(paths: list[str]) -> int:
    if not paths:
        print("usage: m7_success_criteria.py JSON [JSON ...]", file=sys.stderr)
        return 2
    per_tree = _load(paths)
    total = sum(len(r) for r in per_tree.values())
    if total == 0:
        print("no files in any fixture; aborting", file=sys.stderr)
        return 2

    high_plus_medium = sum(
        1
        for recs in per_tree.values()
        for r in recs
        if r.get("confidence") in ("high", "medium")
    )
    notes_count = sum(
        1 for recs in per_tree.values() for r in recs if r.get("role") == "notes"
    )
    distinct_projects = {
        r.get("project") for recs in per_tree.values() for r in recs if r.get("project")
    }
    normalised = sum(1 for p in distinct_projects if p and _KEBAB.match(p))

    high_plus_medium_pct = high_plus_medium / total
    notes_pct = notes_count / total
    normalised_pct = (normalised / max(1, len(distinct_projects))) if distinct_projects else 0.0

    print(f"Total files across {len(per_tree)} fixtures: {total}")
    print(f"  1. high+medium / total: {high_plus_medium}/{total} = {high_plus_medium_pct:.1%}")
    print(f"  2. notes / total:        {notes_count}/{total} = {notes_pct:.1%}")
    print(
        f"  5. normalised project values: "
        f"{normalised}/{len(distinct_projects)} = {normalised_pct:.1%}"
    )

    # Per-tree archive-move report (criterion 4).
    print()
    print("Per-tree archive proposals (criterion 4):")
    archive_ok = True
    for tree, recs in per_tree.items():
        in_archive = [
            r
            for r in recs
            if isinstance(r.get("path"), str) and r["path"].split("/")[0] in {"archive", "archived", "project-history"}
        ]
        moves = sum(1 for r in in_archive if r.get("archive_move"))
        if in_archive:
            ratio = moves / len(in_archive)
            mark = "OK" if ratio >= 0.80 else "MISS"
            if ratio < 0.80:
                archive_ok = False
            print(
                f"  {tree}: {moves}/{len(in_archive)} in-archive files have archive_move "
                f"= {ratio:.1%} [{mark}]"
            )
        else:
            print(f"  {tree}: no archive-style files (criterion 4 not applicable)")

    print()
    print("Pass/Fail summary:")
    crit1 = high_plus_medium_pct >= 0.5
    crit2 = notes_pct <= 0.3
    crit5 = normalised_pct >= 0.9
    print(f"  Criterion 1 (high+medium >= 50%): {'PASS' if crit1 else 'FAIL'}")
    print(f"  Criterion 2 (notes <= 30%):       {'PASS' if crit2 else 'FAIL'}")
    print(f"  Criterion 4 (archive >= 80%):     {'PASS' if archive_ok else 'FAIL'}")
    print(f"  Criterion 5 (normalised >= 90%):  {'PASS' if crit5 else 'FAIL'}")
    print(
        "  Criterion 3 (Status: preservation): see Phase 9 log spot-apply"
        " (JSON dump alone does not carry apply output)"
    )

    ok = crit1 and crit2 and crit5 and archive_ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
