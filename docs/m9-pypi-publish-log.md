# M9 — PyPI publish 1.3.0 (log)

Lifecycle: draft
Role: log
Project: docs
Updated: 2026-05-24

Related:
- child-of: m9-pypi-publish.md
- pairs-with: release-runbook.md

Per-phase log for M9. Entries get appended as the operator walks
[release-runbook.md](release-runbook.md) post-M8.

## Phase progress

| Phase | Status | Notes |
|---|---|---|
| Operator one-time prep | not started | accounts + 2FA + tokens + `~/.pypirc` |
| Pre-publish prep | not started | version bump, CHANGELOG restructure, tree state, quality gate, artifact build, local smoke |
| TestPyPI rehearsal | not started | upload + install + smoke |
| Real PyPI publish | not started | upload + install + smoke |
| Post-release | not started | repo public, tag + GitHub release, token re-scope, doc closeouts |

## Entries

### 2026-05-24 — stub created

M9 stub-drafted as part of the M6 scope reframe. The milestone
exists; activates once M8 ships. No prep work has started.
