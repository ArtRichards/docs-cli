# CLAUDE.md

## Skill update flow (operator policy, 2026-06-12)

Two different update channels — do not mix them up:

- **Bundled skill, every CLI update.** `src/docs_cli/skill/` (SKILL.md +
  references/) is updated in the SAME change as every CLI surface update.
  This is the surface-parity gate in docs/milestone-plan.md "Ongoing conventions":
  argparse `--help` strings and the bundled skill land together, with
  `references/cli.md` and `references/convention.md` byte-identical to
  `docs/cli.md` and `docs/convention.md` (tests/test_skill_refs.py
  enforces; tests/test_skill_quality_artifacts.py pins the quality
  guidance).
- **Host-machine skills, only at production ship.** Skills on this host
  (`~/.claude/skills/`) are NOT refreshed when the CLI changes in-repo.
  Refresh them only when a new version ships to production (PyPI
  publish): upgrade the host `docs` binary to the published version
  first (`pipx upgrade docs-cli`), then run `docs install-skill --force`
  with it, and sweep the workflow skills' docs-cli prescriptions for the
  new surface at that point. Binary and skill move together in the same
  step: a refreshed skill prescribing verbs the old binary lacks is the
  gap M29 left open and M31 closed (operator decision, 2026-10-29).
- **Every other `install-skill` run is state-isolated.** `docs
  install-skill` records its destination on every success, so any run
  other than the host refresh above — re-vendoring into the Agent
  Playbook Suite, a smoke test, a throwaway tree — sets scratch
  `XDG_STATE_HOME` and `XDG_CACHE_HOME`, or it overwrites the host's
  recorded destination (`~/.claude/skills/docs`). Procedure:
  docs/release-runbook.md *Isolation and hygiene*.
- **The Agent Playbook Suite rides its own release cycle.**
  `~/opt/agent-playbook-suite` (marketplace and plugin-cache copies under
  `~/.claude/plugins/`) pins a docs-cli version per suite release and
  vendors the bundled `docs` skill from it. Never change it ad hoc from a
  docs-cli change; update it after a docs-cli publish, and only when the
  operator asks, on a release branch per the suite's
  `marketplace-publishing-guide.md`. A docs-cli milestone records what the
  suite needs in a feedback-log hand-off instead of editing the suite.

## Normative surfaces change only through a milestone (operator policy, 2026-06)

A change to `docs/convention.md`, `src/docs_cli/skill/SKILL.md` or the
bundled `references/` is scoped as a milestone and driven through the
10-phase TDD flow with a RED pinning test first (M16 is the precedent) —
never hand-edited directly. These surfaces are normative and parity-gated
(tests/test_skill_refs.py, tests/test_skill.py). Stage the CHANGELOG under
the next `UNRELEASED` version; the feature milestone owns the version bump,
and a separate publish milestone ships it.

## docs-cli stays agent-agnostic and out of the user's skills (operator policy, 2026-06-29)

- **Never inspect or police an installed skill.** No skill-drift
  detection, no diffing an installed skill against the bundled one, no
  "your skill is stale" checks. The only skill action docs-cli takes is
  installing it where the user asks. Recording the user's `--dest` and
  replaying it (M23's update hint) is fine; judging its content is not.
- **Never assume a particular agent.** The axis is "which directory"
  (`--dest`), not "which agent": no hard-coded agent paths presented as
  the only home, no agent auto-detection. On a TTY ask; for a non-TTY
  caller never block on a prompt.
- A network update check that only says a newer docs-cli exists inspects
  nothing of the user's and is fine (M21).

## Milestone docs: state each binding fact once (operator policy, 2026-10-29)

In a milestone's task plan, implementation log and test matrix, each
binding fact has exactly one home and every other section points to it:

- **decisions** live once, under their D-id;
- **commands** live once, in the frozen command catalogue (M31's P1
  blocks);
- **measured values** (counts, shas, timings) live once, in the
  implementation log.

Restated measurements and command sequences are what drift: they are the
text a writer copies to make a section read on its own. Amend a decision
in place with a dated note rather than restating it. Reviews treat a
restatement as a taste-anchor violation. Evidence: M30 Step 1 claude-T4
and the M31 trial (feedback-log 2026-10-28).
