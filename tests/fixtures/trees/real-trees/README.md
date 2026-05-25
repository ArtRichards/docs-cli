# Real-tree fixtures

Five sanitised real-tree fixtures derived from the 2026-05-24 multi-tree
trial (501 .md files across 25 real-world sibling trees). The trees in
`/tmp/m7-trial2/` were tmpdir-scoped and not recoverable; these fixtures
are **fabricated sanitised analogs** that preserve the *shape categories*
(TitleCase / snake_TitleCase / kebab-case / mixed) the trial surfaced —
they are evidence-shaped, not literal copies. See M7's Generalisation note
(`docs/m7-migration-accuracy.md`) for the discipline behind this.

## Wiring status

Wired into the existing test suite (Phase 2):

- **`snake-medium/`** — `tests/test_migrate.py::test_confidence_distribution_meets_threshold`.
  17 snake_TitleCase files; drives the confidence-distribution success
  criterion (today 4/17 = 24%; post-Phase-6 must reach
  `(high+medium)/total >= 0.5`).

Staged for **Phase 9 manual dogfooding** (`tests/manual/m7_success_criteria.py`,
not yet created — Phase 9 work):

- **`kebab-tiny/`** — 3 kebab-case files. Smallest size class; exercises
  the inference paths against the size-class extreme.
- **`snake-large/`** — 72 snake_TitleCase files. Scale stress; surfaces
  every `_M\d+` / `_Implementation` / `_Component_*_Spec` /
  `_Task_*_Plan` shape Trial 2 saw.
- **`archive-subdir/`** — 10 active-tree files + 5 under `archived/`.
  Exercises F4 archive normalisation end-to-end via the Phase 9 dogfood
  script (the unit-level F4 coverage lives in
  `tests/test_archive_normalisation.py`).
- **`mixed-naming/`** — 10 files spanning TitleCase + space-separated +
  snake_TitleCase + kebab; F1 word-boundary stress shape.

Phase 9 runs the migrate verb against each fixture and aggregates the
five quantitative success criteria (confidence >= 50%, notes <= 30%,
status preservation 100%, archive proposals >= 80%, normalisation >= 90%).
Until then, the four staged fixtures are intentionally unwired — keeping
them in-tree pins the sanitisation work done at Phase 3 and avoids
re-generating sanitised analogs for Phase 9.

## Sanitisation

Every fixture is sanitised — no third-party product / customer / feature
names appear in any file or path. The grep at Phase 3 close-out returns
0 hits across:

```
grep -ri "langfuse\|festo\|orginfo\|embedded.ai\|gpt5\|treatment.rubric\|disambiguation\|risk.prompt\|software.first\|standalone.agents\|orgcontext" tests/fixtures/trees/real-trees/
```

The two `tests/fixtures/project-names/` dirs whose names look real
(`embedded-ai-discovery-parallel/`, `bugs-2026-01-26/`) are generic
kebab / kebab-with-date shapes; the directory names themselves are the
regression-test cases (kebab pass-through, digit-after-digit preservation).
