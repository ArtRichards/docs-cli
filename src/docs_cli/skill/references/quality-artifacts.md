# Quality Artifacts in a Docs-Managed Tree

## Purpose

Quality artifacts make contract, test, and gate results resumable across
sessions. They also prevent agents from treating chat history or CI output as
the only record of quality decisions.

## Pattern

Use Markdown companion docs for navigability and metadata. Store generated
reports as non-Markdown artifacts next to them.

Example:

```text
docs/
  specs/
    m4-risky-change.md
    m4-risky-change-impl.md
    m4-risky-change-test-matrix.md
  quality/
    m4-quality-log.md
    reports/
      coverage.xml
      mutation.json
      benchmark.json
```

The Markdown companion carries:

- Lifecycle
- Role
- Project
- Related links to reports
- Summary of the result
- Owner/follow-up
- Risk level
- Gate commands
- Result summaries

The generated report file remains canonical for tool output.

## Suggested docs-cli commands

```sh
docs new spec m4-risky-change-test-matrix --project <project> --title "M4 - Test Matrix" --body-from -
docs new log quality/m4-quality-log --project <project> --title "M4 - Quality Log" --body-from -
docs touch m4-risky-change-test-matrix.md quality/m4-quality-log.md
docs index <root>
docs check <root> --stale 14
```

## Linking reports

`Related:` may point at non-Markdown files when the local docs-cli convention
supports artifact references. If a project version rejects non-Markdown
`Related:` targets, link generated report paths in the body instead and keep
the Markdown companion as the indexed summary.

## Important limitation

`docs check` proves metadata, lifecycle, index, and references are
mechanically clean. It does not prove the contract is strong, tests are
adequate, or behavior is correct. Those are enforced by the milestone
workflow, review agents, sync-and-commit, and CI gates.
