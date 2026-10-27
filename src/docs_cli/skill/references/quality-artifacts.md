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
docs touch m4-risky-change-test-matrix.md quality/m4-quality-log.md --check
```

`docs touch --check` bumps `Updated:`, reindexes (a separate `docs index` is
redundant), and runs the tree-wide check in one step. The stale window comes
from the tree's `.docs.toml [check] stale_days`; pass `--stale N` only as a
one-off override.

## Linking reports

Link a generated report from its Markdown companion with
`docs relate add <companion> references <report>`. It is a free-form edge,
written on the companion alone: a `Related:` target need not be Markdown, so
the report may be any existing file under the docs root, and it is never read
or written. The Markdown companion stays the indexed summary.

## Important limitation

`docs check` proves metadata, lifecycle, index, and references are
mechanically clean. It does not prove the contract is strong, tests are
adequate, or behavior is correct. Those are enforced by the milestone
workflow, review agents, sync-and-commit, and CI gates.
