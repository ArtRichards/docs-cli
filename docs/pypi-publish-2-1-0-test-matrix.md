# M31 — Publish docs-cli 2.1.0 to PyPI — Test Matrix

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-10-29

Related:
- pairs-with: pypi-publish-2-1-0.md
- pairs-with: pypi-publish-2-1-0-impl.md

## Risk level

Standard

Reason: proposed at setup, and accepted by the conductor's triage on
2026-10-28. The reasoning is in *Risk Level* in
[the task plan](pypi-publish-2-1-0.md):
- M30 is already reviewed, and no product code changes.
- The milestone's own risk is release integrity, and process gates control
  it: D2, D4 and the stop conditions.
- High's distinctive gates do not fit a publish.

There is no Phase-4 operator checkpoint.

## Check classification

Product tests belong in default test discovery
(`.venv/bin/python -m pytest -q`). This milestone **adds and changes none**
(D1). The 1671-test suite is regression evidence only, including the 2.1.0
pins and the two suite-probe replicas.

Every check this milestone adds is a **non-product release check**, run as an
explicit workflow gate:
- the two `tests/manual/` scripts (D5), outside discovery;
- `twine check`;
- the D4 comparisons;
- the D9 checks (the release-input diff and the script blobs);
- the D6 token search;
- `docs check .`, the INDEX snapshot and the reference byte identity.

## Contract clauses

Clause ids are local to this matrix. Each one cites the task plan's binding
decision (D1–D13) and evidence ids. The decisions' operative wording lives
only in the task plan, so the clauses below state what is **checked**, not
the decision again. The exact check ids and command lines are frozen in the
task plan's *Decisions (Phase 1 — BINDING)* (P1.1–P1.5).

| Id | Clause (what is checked) | Source |
|---|---|---|
| C1 | `pyproject.toml`, the packaging pins, both artifact filenames and `docs --version` (canonical builds) all read 2.1.0. No version literal moves | D1; E6 |
| C2 | The CHANGELOG section is dated and has no publish-state sentence. A diff against M30's section at `bf09748` shows only those two lines changed. It is re-dated before build (c) if the day rolled | D7; E6 |
| C3 | The README lists every `docs --help` verb and sub-verb. Every synopsis line matches its verb's `--help` usage in positional shape and flags. There is no "Claude Code", and every GitHub file link points at the `pyproject.toml` Repository on `main` and resolves at HEAD and on `origin/main`, including after the Step 3 archive | D5, D8; E7 |
| C4 | Surface parity: `--help` agrees with the CHANGELOG surface, the references are byte-identical, and M30's stale-wording grep returns 0 | runbook *Surface parity*; E5 |
| C5 | The tree-wide gate is GREEN at the Phase 4 baseline, at the tag-target commit and at closeout: 1671 passed; ruff, the formatter and mypy are clean; `docs check .` exits 0; the INDEX is idempotent and in lockstep | runbook *Quality gate*; E5 |
| C6 | Every build passes `twine check`, with `Metadata-Version` and the backend version recorded. The dependency oracle holds: every `Requires-Dist` carries an `extra ==` marker, with `Provides-Extra: dev` and `Requires-Python: >=3.11`. CHANGELOG is in neither artifact, and the wheel carries the seven skill files | D4; plan *Non-functional constraints*; E4 |
| C7 | Wheel (a) passes both probe groups in a fresh venv with scratch XDG directories | D5, D6 |
| C8 | The rehearsal: built from an empty `dist/`; uploaded by explicit filename; installed from TestPyPI alone with `--no-deps`. The served wheel equals the uploaded build by sha, and its `docs_cli/` payload equals (a)'s. Both probe groups pass, with the version check skipped. The edit is reverted, and (b) equals (a) | D4, D6, D9; E2 |
| C9 | No upload happens unless every stop-table precondition holds at that moment, including that `dist/` holds exactly the two canonical files with (c)'s shas | D2, D4 |
| C10 | The wheel sha is one value across (a), (b), (c) and the served bytes. The sdist is bit-perfect against the served one, and its members outside `docs/` and `tests/` match (a)'s recorded manifest. Both match the per-version JSON digests | D4 |
| C11 | The PyPI-served wheel passes both probe groups, version included, **before** the tag exists | D5, D13 |
| C12 | Before the tag, the suite's capability probes run verbatim against the PyPI-served wheel and read `lifecycle verb: True` and `free-form relate: True`. The suite's full guard is expected to fail; that is recorded, not treated as a regression | D12, D13; E11 |
| C13 | The tag and the release follow C11 and C12. `refs/tags/v2.1.0^{}` on the remote equals the tag-target commit. `gh release create` ran with `--verify-tag` and `--title`. The final report states the merge instruction | D2, D13; E8 |
| C14 | No throwaway run writes host state, and every index install names one index with `--no-deps`. No credential value is printed, logged or committed | D6; E3, E9, E10 |
| C15 | Phase 9 verifies D10's host state: the binary version and its install source, the skill's byte identity, the recorded destination, and the untouched symlink. Host state outside D10's list stays unchanged | D10; E9 |
| C16 | A 2.0.0 install prints `docs: update available 2.0.0 -> 2.1.0 — run: pip install -U docs-cli` once on stderr, with its exit code unchanged | Goal; M21 contract |
| C17 | The sweep table is recorded, the suite and the plugin cache are untouched, and the hand-off is updated and left open | D10, D12; E11 |
| C18 | The runbook carries the lessons and corrections, the archive selects exactly the trio, and the tracker row is `complete` | D11 |
| C19 | Every release-check run records its script's git blob sha. A script that changed after its Phase 4 run is re-run before Step 1 closes | D5, D9 |

### Decision ↔ clause crosswalk

| Decision | Clauses |
|---|---|
| D1 What ships, and what may change | C1, C5 |
| D2 Release authorization | C9, C13 |
| D3 The ship-milestone mapping | (structure — the phase placement of every clause) |
| D4 Builds and chain of custody | C6, C8, C9, C10 |
| D5 Release checks | C7, C8, C11, C19 |
| D6 Isolation and secrets | C7, C8, C14 |
| D7 CHANGELOG dating | C2 |
| D8 README | C3 |
| D9 Re-rehearsal and re-runs | C8, C19 |
| D10 Host work | C15, C17 |
| D11 Closeout | C18 |
| D12 The suite hand-off | C12, C17 |
| D13 Tag and release | C11, C12, C13 |

## Matrix

Check ids refer to the task plan's P1.1 (R…) and P1.2 (N…, S…, G…, W…), where
each id's display name and assertion are frozen.

| Contract clause | Visible test / explicit check | Hidden/generalization check | Property/stateful check | Mutation target | Fuzz/benchmark/security/schema note |
|---|---|---|---|---|---|
| Success path — release inputs (C1–C4) | `release_readiness.py`: R1 (C1); R2–R4 (C2); R5–R8c (C3); R9 (C4). `tests/test_packaging.py` A3/B1/B2/C2 (existing). The stale-wording grep and surface parity (C4, P1.4) | — | — | P1.4 mutants 1–6, 1b and 5b, and the link mutants 9a–9c, each killed by exactly one R id | — |
| Success path — wheel (a) (C6, C7) | `twine check`; the manifest checks; `release_probe.py`, both groups: N1–N9, S1–S2, G1–G10, W1–W4 | a fresh venv per run; an editable build runs the contract group only | W3 and N2: the `install-skill` and `docs lifecycle` re-runs are idempotent | mutant 7: the 2.0.0 control fails N1–N9, S1, S2, W1, W2 and passes the rest | schema: the dependency oracle; `Metadata-Version` recorded |
| Success path — served artifacts (C8, C11, C12) | `release_probe.py` on the TestPyPI-served wheel (W1 skipped) and the PyPI-served wheel; the suite's capability probes: S1, S2, the replicas and the extracted guard step (P1.5) | index-served artifacts; the rehearsal-name build | identical probe results across the three wheel installs, apart from the rehearsal's W1 | — | security: single-index `--no-deps` installs |
| Error path — upload gate (C9, C19) | the Phase 5 checklist, against the stop table; `dist/` contents; the D9 checks: the release-input diff (`.gitignore` included) and each script's blob against *Release anchors (current)*; the non-disclosing token search | — | — | — | security: explicit filenames, `--non-interactive` |
| Boundary — chain of custody (C10) | the sha table (a), (b), (c) and served; the rehearsal sha and payload; the sdist member manifest; the per-version JSON digests | backend drift between Step 1 and Step 2 (D4 remedy) | sha equality is transitive across the four wheels | mutants 8, 8b and 8c (P1.4): the sha, payload and manifest comparators each report a planted difference | security: served-versus-local is the tamper check |
| Idempotency/retry/state (C8, C14) | D9's `.postN` re-rehearsal; the one-file partial-upload retry; XDG redirection | — | the host recorded-destination file is unchanged before Phase 9 | — | — |
| Public release surfaces (C13, C18) | `git ls-remote origin 'refs/tags/v2.1.0^{}'`; `gh release view v2.1.0`; the archive dry-run and apply; `docs check .` after the archive; the README link re-check | — | — | — | — |
| Host integration (C15, C16, C17) | the Phase 9 checks: version and source; `diff -r`; the recorded destination; the symlink; the notice; the sweep census | a real 2.0.0 install; the pipx install path | — | — | — |
| Security/privacy/perf (C14) | the token search over every staged diff and log entry; shape-only `~/.pypirc` checks | — | — | — | benchmark: not applicable; elapsed times recorded |

## Visible tests

No product test is added or changed. The explicit checks are frozen in the
task plan's P1.1 and P1.2; their display names state behaviour without
milestone or decision ids.

**`tests/manual/release_readiness.py`** — **new.** Covers C1–C4 with R1–R9
(25 lines on this tree since the Step 1 review split R8 into R8a–R8c). In
Phase 2 it is RED for exactly the reasons in the
task plan's *Acceptance examples* › *Readiness*.

**`tests/manual/release_probe.py`** — **new.** Covers C7, C8, C11, C12 and
C19. It has two groups:
- **The contract group** (21) runs against any executable: M30's headline
  contracts (N1–N9), the two suite probes (S1, S2), and M29's contracts plus
  the index smoke (G1–G10).
- **The distribution group** (4) runs against wheel installs only:
  `docs --version` (W1), `install-skill` byte identity (W2), the no-op re-run
  (W3) and the `--symlink` refusal (W4).

**Reused, unchanged:**
- `tests/test_packaging.py`;
- `tests/test_cli_lifecycle.py::test_help_verb_list_names_lifecycle_for_the_playbook_guard`;
- `tests/test_cli_relate.py::test_playbook_guard_free_form_dry_run_probe_exits_0`;
- the rest of the 1671.

## Hidden/generalization categories

The repository is fully visible, so there are no private cases. The
generalization targets are:
- index-served artifacts, as opposed to local builds;
- the rehearsal-name build (`0.0.0+local`, M13; no update notice, M24);
- an editable build, as opposed to wheel installs;
- a fresh venv per run;
- probe trees outside the repository, including a throwaway copy of this
  docs tree;
- extension-vocabulary trees and a non-default-`date_format` tree;
- a real 2.0.0 install;
- the host's pipx install.

## Property/stateful checks

- **Idempotence.** An `install-skill` re-run is a no-op at exit 0. A
  `docs lifecycle` re-run writes zero bytes and does not reindex.
- **Transitivity.** Wheel sha (a) = (b) = (c) = the served wheel.
- **Determinism.** The distribution probe gives identical results across the
  three wheel installs, apart from the rehearsal's version line.
- **State isolation.** The host's recorded-destination file and update cache
  stay unchanged by every throwaway run.

## Mutation targets

Mutation tooling is not configured. Phase 2 runs a hand-applied smoke, as
M28a and M30 did, and records which check kills each mutant. The task plan's
P1.4 freezes each mutant and its intended killer, adding the cheap 1b, 5b, 8b
and 8c:
1. a CHANGELOG copy still headed `UNRELEASED`;
2. a dated heading that keeps the publish-state sentence;
3. a 2.1.0 section with one other line edited;
4. a README missing one verb;
5. a README with one lagging synopsis;
6. a bundled reference one byte off its `docs/` spec;
7. the host's 2.0.0 binary, which must fail every 2.1-only check;
8. the sha comparator, fed the rehearsal wheel against (a).

## Fuzz

Not applicable. There is no new parsing surface, and M30's verb-grammar fuzz
remains in the product suite.

## Benchmark/security/schema

- **Schema:**
  - `twine check`;
  - `Metadata-Version` recorded;
  - the dependency oracle (C6);
  - the manifests (C6).
- **Security:**
  - D6's credential hygiene and single-index installs;
  - D4's explicit filenames;
  - the served-versus-local sha comparison, as a tamper check.
- **Benchmark:** not applicable. Elapsed times are recorded.

## Use-case mapping

Tests map to the use-case catalog in the bundled skill,
`src/docs_cli/skill/references/use-cases.md`.

| Use case | Covered by |
|---|---|
| Distribution — install `docs-cli` from PyPI and materialise the skill | C6, C7, C11, C15 |
| Greenfield — promote a scaffolded doc's lifecycle | C7, C11 |
| Greenfield — link related docs with a free-form edge | C7, C11, C12 |
| Agent Playbook Suite — `create-milestones` setup without operator asks | C12, C17 |
| Any user of 2.0.0 — learn that 2.1.0 exists | C16 |

## Mock policy

- New mocks: none.
- Justification: not applicable.
- Real-path test covering same behavior: every check runs against real
  artifacts, indexes and installs.

## Hidden-test handling

- Actual hidden cases are not written here; the implementation agent can read
  this repository.
- Categories: see *Hidden/generalization categories*.
- Owner: the milestone conductor.
- Commands or CI job names: none configured. Generalization runs as the
  three-wheel probe replay and the 2.0.0 control.

## Gate commands

### Fast PR gate

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/ tests/
.venv/bin/python -m pytest -q
(cd docs && ../.venv/bin/docs check .)
.venv/bin/python tests/manual/release_readiness.py …   # arguments: task plan P1.4
```

### Deep/nightly/release gate

The task plan's Phases 4–7 carry the exact sequences:
- `rm -rf dist/` before every build;
- explicit filenames in every `twine upload`;
- single-index `--no-deps` installs;
- `release_probe.py --docs <venv>/bin/docs` on every wheel install.

The task plan's P1.3–P1.5 freeze the flags and the scratch paths. Coverage,
mutation and hidden-suite tooling are not configured in this project.

## Results summary

- Visible tests: **1671 passed, 1671 collected** at Phase 1 (`8515f1c`),
  Phase 3, the Phase 4 baseline (`X` = `a25cb5d`) and the tag-target
  commit (`33c936f`, Phase 5).
- Upload gate (C9): at Phase 5 every pre-upload precondition held at the
  tag target, and build (c)'s wheel equals (a) with (a)'s sdist manifest
  (the log's *Phase 5*). Phase 6 re-checks them immediately before the
  upload.
- Release checks: **Phase 2 RED recorded.** Readiness fails exactly the
  lines *Acceptance examples* › *Readiness* names (as R2, R3 and R6), and
  its green control passes every line. The probe passes 21/21 on the
  editable build. **Phase 4 GREEN:** readiness passes every line (23 at
  Phase 4; 25 after the review split R8); the probe 25/25 on wheel (a) and
  24 + W1 SKIP on the
  TestPyPI-served rehearsal; the extracted suite guard step reads True /
  True against (a) and fails against 2.0.0. Phases 7 and 8 record the
  served wheel.
- Hidden/generalization: the 2.0.0 control fails exactly N1–N9, S1, S2, W1
  and W2 and passes G1–G10, W3 and W4, as frozen. The three-wheel replay:
  (a) and the TestPyPI-served rehearsal give one result set (W1 aside); the
  PyPI-served wheel is Step 2's.
- Property/stateful: N2 and W3 (idempotent re-runs) pass on every
  executable that has the verb, and both are write-sensitive (bytes and
  mtimes; N2 also reads the `--json` no-op record); wheel (a) = (b) by sha; the rehearsal's
  `docs_cli/` payload equals (a)'s, downloaded and installed; no run changed
  the repository or host state.
- Mutation: readiness mutants 1–6, 1b and 5b are 8/8 killed, each by
  exactly its intended check, and the review's link mutants 9a–9c are 3/3;
  mutant 7 is the control above; the comparator mutants 8, 8b and 8c each
  report their planted difference. The review's three probe negative
  controls — `--version` printing the right text with exit 3, an `index`
  that drops the promoted entry, and a `lifecycle` re-run that rewrites
  identical bytes — each fail exactly W1, N6 or N2, and each passed the
  probe as it stood before the review.
- Script provenance (C19): every run printed its blob sha. Both script
  changes after Phase 4 — the audit's docstrings and the review's
  strengthened checks — were re-run under D9 against wheel (a) and a fresh
  install of the served rehearsal, with identical result lines; the log's
  anchors carry the current blobs.
- Fuzz: not applicable.
- Benchmark/security/schema: schema — `twine check` passed on both builds,
  `Metadata-Version: 2.5`, the dependency oracle holds, CHANGELOG is in
  neither artifact, and the wheel carries the seven skill files. Security —
  shape-only credential checks that fail closed on malformed input, a
  token search that never prints what it matches and stops when the search
  itself fails (proven on synthetic tokens and files),
  explicit-filename `--non-interactive`
  upload, a single-index `--no-deps` install with the payload compared
  before execution, served = local = JSON digests. Benchmark is not
  applicable; the Phase 4 run took about seven minutes.
- Coverage: not configured.
- Mock audit: no mocks planned.
- Open risks:
  - the PyPI token's validity is proven only by use, at Phase 6;
  - backend drift is guarded by D4.

## Adequacy results

- visible_pass_rate: 1.0 (1671/1671)
- hidden_pass_rate: not applicable (no hidden suite; the three-wheel replay
  stands in)
- hidden_generalization_gap: not applicable
- changed-lines coverage: not configured
- changed-files branch coverage: not configured
- mutation score on touched modules: 17/17 hand-applied mutants detected
  (readiness 1–6, 1b, 5b, 9a–9c; comparators 8, 8b, 8c; probe negative
  controls for W1, N6 and N2), each by its intended check; the 2.0.0
  control (mutant 7) fails exactly the 13 release-bound checks
- property/stateful result: pass (Phase 4)
- fuzz result: not applicable
- benchmark delta: not applicable; elapsed times recorded
- security/schema/migration result: pass (Phase 4); migration not
  applicable
- skipped deep gates and follow-up: none skipped. Coverage and mutation
  tooling are not configured.
