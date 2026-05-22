# Release Plan

We ship the next version in three stages, each gated on the previous one
passing its acceptance checks.

## Stage one — internal

Deploy to the internal environment and let the team dogfood it for a week.
Collect crash reports and obvious usability complaints.

## Stage two — beta

Open the build to the beta cohort. Watch the error dashboards; hold here
until the error rate is below the agreed threshold for three consecutive
days.

## Stage three — general availability

Promote the beta build to everyone. No code changes between stage two and
stage three — only the audience widens.
