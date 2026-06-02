# M16 — Bundled docs skill quality artifacts Test Matrix

Lifecycle: active
Role: spec
Project: docs
Updated: 2026-06-02

Related:
- pairs-with: m16-bundled-docs-skill-quality.md
- pairs-with: m16-bundled-docs-skill-quality-impl.md

## Risk level

Lite

Reason: documentation-only bundled skill guidance. The change affects how
agents read the installed docs skill but does not change docs-cli runtime
behavior.

## Matrix

| Contract clause | Visible test | Hidden/generalization check | Property/stateful check | Mutation target | Fuzz/benchmark/security/schema note |
|---|---|---|---|---|---|
| Bundled `docs` skill points to quality artifact guidance. | `tests/test_skill_quality_artifacts.py::test_skill_points_to_quality_artifacts_reference` | Installed skill user can find the reference without knowing the Agent Playbook Suite repo. | Not applicable for prose guidance. | Remove the `quality-artifacts.md` pointer or mechanical-validation warning. | Not applicable. |
| Quality-artifacts reference documents test matrices, quality logs, generated reports, and docs-check limits. | `tests/test_skill_quality_artifacts.py::test_quality_artifacts_reference_documents_m16_contract` | Agent can apply the pattern to Markdown companions plus non-Markdown report files. | Not applicable for prose guidance. | Remove terms such as `coverage.xml`, `mutation.json`, `benchmark.json`, or `mechanically clean`. | Not applicable. |
| Installed bundled references do not depend on source-checkout-only links. | `tests/test_skill_quality_artifacts.py::test_installed_skill_references_do_not_depend_on_source_checkout` | `docs install-skill --dest <tmp>` materializes a readable tree outside the repo. | Not applicable. | Reintroduce `../../../../docs/` or `../src/docs_cli/` links. | Packaging tests cover install materialization. |
| `docs install-skill` copies `quality-artifacts.md` with the rest of the bundled skill. | `tests/test_packaging.py::test_b3_wheel_contains_cli_and_skill`; `tests/test_packaging.py::test_d3_install_skill_tree_is_byte_identical` | Installed wheel carries the same bundled guidance as source. | Not applicable. | Remove `quality-artifacts.md` from `_SKILL_RELATIVE_FILES` or wheel data. | Wheel/package smoke only. |

## Mock policy

- New mocks: none.
- Justification: not applicable.
- Real-path test covering same behavior: package/install tests exercise the real
  wheel and `docs install-skill` path.

## Hidden-test handling

- No private hidden cases are recorded here.
- Hidden/generalization coverage is represented as installed-skill readability
  and source-checkout independence.

## Gate commands

### Fast PR gate

```sh
.venv/bin/python -m pytest tests/test_skill.py tests/test_skill_adoption.py tests/test_packaging.py tests/test_skill_refs.py tests/test_skill_quality_artifacts.py -q
.venv/bin/docs index docs
.venv/bin/docs check docs --stale 14
```

### Deep/nightly/release gate

```sh
not configured - documentation-only bundled skill guidance; release packaging smoke is covered by tests/test_packaging.py
```

## Results summary

- Visible tests: 43 passed across bundled skill structure, adoption, packaging,
  byte-sync, and M16 quality-artifact content checks.
- Hidden/generalization: installed-skill source-checkout independence pinned by
  `tests/test_skill_quality_artifacts.py`.
- Property/stateful: not applicable.
- Mutation: not configured.
- Fuzz: not applicable.
- Benchmark/security/schema: not applicable.
- Coverage: not applicable.
- Mock audit: no mocks introduced.
- Open risks: none known.
