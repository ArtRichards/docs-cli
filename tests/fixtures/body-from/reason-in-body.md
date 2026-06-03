## Risk level

Reason: the rollout touches the auth path, so a regression here is
high-impact. We gate it behind a flag.

## Plan

Plan: stage one ships the flag off; stage two flips it on for 5%.
