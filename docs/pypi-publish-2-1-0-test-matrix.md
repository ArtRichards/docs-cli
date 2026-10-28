# M31 — Publish docs-cli 2.1.0 to PyPI — Test Matrix

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-10-28

Related:
- pairs-with: pypi-publish-2-1-0.md
- pairs-with: pypi-publish-2-1-0-impl.md

## Risk level

Standard

Reason: proposed at setup and accepted by the conductor's triage on
2026-10-28 (see *Risk Level* in [the task plan](pypi-publish-2-1-0.md)). The
milestone ships M30, which was
already built and reviewed at an operator-confirmed Standard level, and it
changes no product code. Its own risk is release integrity: the PyPI upload is
irreversible. That is controlled by the TestPyPI rehearsal, `twine check`, the
chain-of-custody rule (D4), the stop conditions, and Step 1's dual-provider
review before the upload. High's distinctive gates do not fit a publish, and
its post-Phase-4 pause would contradict the operator's automatic-upload
decision (D2). There is no Phase-4 operator checkpoint.

## Check classification

Product tests belong in default test discovery (`.venv/bin/python -m pytest
-q`). This milestone **adds and changes none** (D1). The 1671-test suite is
regression evidence only. It already pins:
- the 2.1.0 version, in `tests/test_packaging.py`;
- the two Agent Playbook Suite probes, as replica tests run from source.

Every check this milestone adds is a **non-product release check**, run only
as an explicit workflow gate:
- the two `tests/manual/` scripts (D5), which sit outside discovery;
- `twine check`;
- the D4 sha and sdist-member comparisons;
- the D9 input diff;
- the D6 credential-hygiene search;
- `docs check .`, the INDEX snapshot and the reference byte identity.

## Contract clauses

Clause ids are local to this matrix. Each cites the task plan's binding
decision (D1–D13), evidence id or setup question. Both setup questions are
answered: Q1 in D2 and D13, Q2 in D10. Phase 1 freezes the clauses' exact
check lists and command lines.

| Id | Clause | Source |
|---|---|---|
| C1 | Version identity. `pyproject.toml`, the packaging pins, both artifact filenames and `docs --version` (canonical builds) all read 2.1.0, and no version literal moves in this milestone | D1, E6 |
| C2 | The CHANGELOG reads `## 2.1.0 — <local date of the upload>`. The publish-state sentence is gone, nothing else in the section changes, and it is re-dated before the tag-target build if the day rolled | D7, E6 |
| C3 | The README matches the shipped surface. Every `docs --help` verb is listed; the `touch`, `stamp` and `project set` synopses take several files; it has no "Claude Code"; every `blob/main/` link resolves, including after the Step 3 archive | D8, E7 |
| C4 | Surface parity holds. `--help` agrees with the CHANGELOG's 2.1.0 surface, the bundled references are byte-identical to `docs/`, and the M30 stale-wording grep returns 0 | runbook *Surface parity*; E5 |
| C5 | The tree-wide gate is GREEN at the Phase 4 baseline, at the tag-target commit and at closeout: 1671 passed, ruff, the formatter, mypy, `docs check .` at exit 0, the INDEX idempotent and in lockstep with its snapshot | runbook *Quality gate*; E5 |
| C6 | The artifacts are sound. `twine check` passes both; `Metadata-Version` and the build-backend version are recorded; CHANGELOG is in neither artifact; the wheel carries the seven bundled skill files; there is no `Requires-Dist` | D4; E4 |
| C7 | The canonical local wheel (a) passes `release_probe.py` in a fresh venv with scratch XDG directories | D5, D6 |
| C8 | The TestPyPI rehearsal passes. The served `docs-cli-rehearsal` wheel passes the probe with the version line skipped, the rename is reverted (`git diff pyproject.toml` empty), and the canonical rebuild (b) has sha (a) | D9, runbook *TestPyPI rehearsal*; E2 |
| C9 | No upload happens unless every D2 precondition holds at that moment. A failed precondition stops with nothing uploaded | D2, *Contract* › *Error cases* |
| C10 | Chain of custody holds. The wheel sha is one value across (a), (b), (c) and the PyPI-served bytes. The sdist is anchored at (c) and bit-perfect against the served sdist, and its members outside `docs/` and `tests/` equal (a)'s sdist. Both match PyPI's per-version digests | D4 |
| C11 | The PyPI-served wheel passes the same probe, `docs --version` included (`docs 2.1.0`) | D5; M13 caveat |
| C12 | Against the PyPI-served wheel, the Agent Playbook Suite's capability probes, run verbatim, read `lifecycle verb: True` and `free-form relate: True`. The full guard's expected failure, before the suite retires its stopgap, is recorded rather than treated as a regression | M30 hand-off item 2; D12; E11 |
| C13 | Right after the PyPI-served verification, the annotated `v2.1.0` tag is pushed at the tag-target commit — the exact commit the uploaded artifacts were built from — and the GitHub release carries the dated `## 2.1.0` notes. Both run under D2, and the tag push is D2's recorded exception to pushing only through sync-and-commit. The stack's merge must preserve history so the tag stays on `main` | D2, D13 (Q1 → A); E8 |
| C14 | Isolation and secrets. No throwaway run writes host state (the recorded destination and the update cache stay untouched), and no credential value is printed, logged or committed | D6; E3, E9, E10 |
| C15 | After `pipx upgrade docs-cli`, the host binary prints `docs 2.1.0`, installed from the PyPI index. Then `docs install-skill --force --dest ~/.claude/skills/docs`, run with that binary, leaves the skill byte-identical to the served wheel's bundle, and the recorded destination names `~/.claude/skills/docs`. The backup symlink `docs-local-source-backup-20260525-134621` is untouched | D10 (Q2); E9 |
| C16 | The update notice reaches a 2.0.0 install. `docs: update available 2.0.0 -> 2.1.0 — run: pip install -U docs-cli` appears once on stderr, and the exit code is unchanged | Goal; M21 contract |
| C17 | The workflow-skill sweep is recorded, with counts per file. The suite repository and the plugin cache are untouched, and the feedback-log hand-off is updated and left open | D10, D12; E11 |
| C18 | Closeout follows the tracker. The runbook carries the *From M31* lessons and the body corrections; the archive selects exactly the trio; the tracker row is `complete`; everything that must outlive the archive is in a live document | D11 |

### Decision ↔ clause crosswalk

| Decision | Clauses |
|---|---|
| D1 What ships | C1 |
| D2 Release authorization | C9, C13 |
| D3 The ship-milestone mapping | (structure — phase placement of every clause below) |
| D4 Chain of custody | C6, C10 |
| D5 Release checks | C7, C8, C11 |
| D6 Isolation and secrets | C7, C14 |
| D7 CHANGELOG dating | C2 |
| D8 README | C3 |
| D9 Re-rehearsal | C8, C9 |
| D10 Host work | C15, C17 |
| D11 Closeout | C18 |
| D12 The suite hand-off | C12, C17 |
| D13 Tag and release in Step 2 | C13 |

## Matrix

The check names below are **planned** at setup. Phase 2 writes the scripts,
and this table is then updated with the final check names.

| Contract clause | Visible test / explicit check | Hidden/generalization check | Property/stateful check | Mutation target | Fuzz/benchmark/security/schema note |
|---|---|---|---|---|---|
| Success path — release inputs (C1, C2, C3, C4) | `release_readiness.py`: the version, the dated heading, no publish-state wording, the README verbs and links, the mirrors. `tests/test_packaging.py` A3/B1/B2/C2 (existing) | — | — | an `UNRELEASED` heading; the sentence kept; a README missing a verb; a mirror one byte off | — |
| Success path — artifact (C6, C7) | `twine check dist/*`; the manifest checks; `release_probe.py --docs <local-venv>/bin/docs` | a fresh venv per run, with no repository on the path | an `install-skill` re-run is a no-op at exit 0; a `docs lifecycle` re-run writes zero bytes | the 2.0.0 control fails every 2.1-only check | schema: `Metadata-Version` recorded; no `Requires-Dist` |
| Success path — served artifacts (C8, C11, C12) | `release_probe.py` against the TestPyPI-served wheel (version skipped) and the PyPI-served wheel; the suite's capability probes run verbatim | index-served artifacts, not local builds; the rehearsal-name build | identical probe results across the three builds, apart from the rehearsal's version line | — | — |
| Error path — upload gate (C9) | the Phase 5 precondition checklist: the review ledger closed, GO, the D9 input diff empty, the slot free, the `~/.pypirc` shape, a clean tree, `twine check` | — | — | the precondition guard: any false precondition must stop with nothing uploaded | security: `--non-interactive` |
| Boundary — chain of custody (C10) | the sha256 table (a), (b), (c) and served; the sdist member diff outside `docs/` and `tests/`; the per-version JSON digests | backend drift between Step 1 and Step 2 (D4 remedy) | sha equality is transitive across the four wheels | the comparator, fed the rehearsal wheel against the canonical one, must report a mismatch | security: served-versus-local is the tamper check |
| Idempotency/retry/state (C8, C9, C14) | the D9 re-rehearsal rule (`2.1.0.postN` on the detour project); the partial-upload retry of one named missing file; the XDG redirection for every throwaway run | — | the host recorded destination is unchanged before Phase 9 | — | — |
| Host integration (C15, C16, C17) | `pipx` upgrade then `docs --version`; `install-skill --force --dest ~/.claude/skills/docs` then `diff -r` against the served bundle; the recorded destination read back; the backup symlink unchanged; the update notice from the 2.0.0 binary with a scratch cache; the sweep census | a real 2.0.0 install; the pipx install path | — | — | — |
| Public release surfaces (C13, C18) | `git ls-remote --tags origin v2.1.0`; `gh release view v2.1.0`; the archive dry-run and apply selecting exactly the trio; `docs check .` after the archive; the README link re-check | — | — | — | — |
| Security/privacy/perf (C14) | the credential-hygiene search over every staged diff and every log entry; shape-only `~/.pypirc` checks | — | — | — | benchmark: not applicable; elapsed times recorded |

## Visible tests

No product test is added or changed. These are the planned explicit checks
(Phase 2 finalizes them; names state the behaviour, with no milestone or
decision ids):

- `tests/manual/release_readiness.py` — **new**; C1–C4.
- `tests/manual/release_probe.py` — **new**; C7, C8, C11, and the probe half of
  C12. It covers:
  - M30's headline contracts: `docs lifecycle` promote and no-op; the
    refusal of `archived`; the free-form `relate` writing SOURCE only; the
    grammar refusal; an extension vocabulary; a non-default `date_format`;
    the `docs stamp` refusal; an extension role rendered in the INDEX;
  - both suite probes;
  - M29's nine 2.0 contracts;
  - the `install-skill` distribution contracts;
  - `docs --version`, except under the rehearsal name.
- Reused product tests, unchanged:
  - `tests/test_packaging.py` (the 2.1.0 pins);
  - `tests/test_cli_lifecycle.py::test_help_verb_list_names_lifecycle_for_the_playbook_guard`;
  - `tests/test_cli_relate.py::test_playbook_guard_free_form_dry_run_probe_exits_0`;
  - the rest of the 1671.

## Hidden/generalization categories

The repository is fully visible, so no private cases exist and none are
recorded here. The generalization targets are:

- artifacts served by an index rather than built locally — one from TestPyPI,
  one from PyPI;
- the rehearsal-name build (`0.0.0+local`, M13; no update notice, M24);
- a fresh venv per run, with no repository on the path;
- probe trees outside the repository, including a throwaway copy of this docs
  tree;
- extension-vocabulary and non-default-`date_format` trees;
- a real 2.0.0 install, for the update notice;
- the host's pipx install path, as opposed to a throwaway venv.

## Property/stateful checks

- Idempotence: an `install-skill` re-run is a no-op at exit 0, and a
  `docs lifecycle` re-run writes zero bytes and does not reindex.
- Transitivity: wheel sha (a) = (b) = (c) = served (D4).
- Determinism: one probe gives identical results across the three builds,
  apart from the rehearsal's version line.
- State isolation: the host's recorded-destination file and update cache are
  unchanged by every throwaway run (C14).

## Mutation targets

Mutation tooling is not configured. Phase 2 runs a hand-applied mutation smoke
over these six discriminators, following the M28a and M30 precedent, and
records which check kills each:

1. a CHANGELOG copy still headed `UNRELEASED`;
2. a dated heading that keeps the publish-state sentence;
3. a README copy missing one verb;
4. a bundled reference copy one byte off its `docs/` spec;
5. the host 2.0.0 binary, which must fail every 2.1-only probe check and pass
   the 2.0 regression set;
6. the sha comparator, fed the rehearsal wheel against the canonical wheel.

## Fuzz

Not applicable. There is no new parsing surface, and M30's verb-grammar fuzz
remains in the product suite.

## Benchmark/security/schema

- Schema:
  - `twine check` on every build;
  - `Metadata-Version` recorded (2.5 is expected);
  - the wheel and sdist manifests: CHANGELOG in neither, the seven skill files
    in the wheel, no `Requires-Dist`.
- Security:
  - the D6 credential hygiene: shape-only checks, `--non-interactive`, and a
    search of every staged diff for token-shaped strings;
  - the served-versus-local sha comparison, as a tamper check.
- Benchmark: not applicable. Elapsed times are recorded, not budgeted.

## Use-case mapping

Tests map to the use-case catalog shipped in the bundled skill,
`src/docs_cli/skill/references/use-cases.md`. This project keeps no separate
`use-cases.md` in the docs tree.

| Use case | Covered by |
|---|---|
| Distribution — install `docs-cli` from PyPI and materialise the skill | C6, C7, C11, C15 |
| Greenfield — promote a scaffolded doc's lifecycle | C7, C11 (the probe's M30 contracts) |
| Greenfield — link related docs with a free-form edge | C7, C11, C12 |
| Agent Playbook Suite — `create-milestones` setup without operator asks | C12, C17 |
| Any user of 2.0.0 — learn that 2.1.0 exists | C16 |

## Mock policy

- New mocks: none.
- Justification: not applicable.
- Real-path test covering same behavior: every check runs against real
  artifacts, real indexes (TestPyPI, PyPI) and real installs.

## Hidden-test handling

- Actual hidden cases are not written here; the implementation agent can read
  this repository.
- Categories: listed under *Hidden/generalization categories*.
- Owner: the milestone conductor.
- Commands or CI job names: none configured. Generalization runs as the
  three-build probe replay and the 2.0.0 control.

## Gate commands

### Fast PR gate

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q
(cd docs && ../.venv/bin/docs check .)
.venv/bin/python tests/manual/release_readiness.py   # arguments frozen at Phase 1
```

### Deep/nightly/release gate

```sh
# Phase 4 (Step 1) — throwaway runs with XDG_STATE_HOME / XDG_CACHE_HOME in scratch (D6)
rm -rf dist/ && .venv/bin/python -m build      # record the backend version + sha256 (a)
.venv/bin/twine check dist/*
.venv/bin/python tests/manual/release_probe.py --docs <local-venv>/bin/docs
# TestPyPI rehearsal under docs-cli-rehearsal; probe with the version check skipped; revert; rebuild → (b)
# Phase 5–8 (Step 2)
.venv/bin/twine upload --non-interactive dist/*   # under D2 only
.venv/bin/python tests/manual/release_probe.py --docs <pypi-venv>/bin/docs
```

Phase 1 freezes the exact flags, scratch paths and the sha-comparison
commands. Coverage, mutation and hidden-suite tooling are not configured in
this project.

## Results summary

- Visible tests: pending (setup baseline: **1671 passed** at `be7f809`).
- Release checks: pending (Phase 2 RED and controls; Phase 4, 8 GREEN).
- Hidden/generalization: pending — the three-build replay and the 2.0.0
  control.
- Property/stateful: pending.
- Mutation: pending — a hand-applied smoke over six targets.
- Fuzz: not applicable.
- Benchmark/security/schema: pending. Benchmark is not applicable.
- Coverage: not configured.
- Mock audit: no mocks planned.
- Open risks:
  - The PyPI token's validity is proven only by use, at Phase 6.
  - Backend drift between the Step 1 and Step 2 builds is guarded by D4.

## Adequacy results

- visible_pass_rate: pending
- hidden_pass_rate: not applicable (no hidden suite; the three-build replay
  stands in)
- hidden_generalization_gap: not applicable
- changed-lines coverage: not configured
- changed-files branch coverage: not configured
- mutation score on touched modules: pending (hand-applied smoke over the
  release checks)
- property/stateful result: pending
- fuzz result: not applicable
- benchmark delta: not applicable; elapsed times recorded
- security/schema/migration result: pending
- skipped deep gates and follow-up: none skipped. Coverage and mutation
  tooling are not configured in this project.
