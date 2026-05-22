# Deployment Log

A running record of production deployments, newest entries appended at the
bottom.

## 2026-04-02 — v0.9.1

Hotfix for the session-expiry rounding bug. Deployed mid-afternoon, no
rollback needed.

## 2026-04-18 — v0.10.0

Minor release: new refresh-token endpoint, dashboard tidy-up. Smooth
deploy; error rates flat afterwards.

## 2026-05-06 — v0.10.1

Reverted a logging change from v0.10.0 that was flooding the aggregator.
