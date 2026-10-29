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
