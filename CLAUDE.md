# CLAUDE.md

## Skill update flow (operator policy, 2026-06-12)

Two different update channels — do not mix them up:

- **Bundled skill, every CLI update.** `src/docs_cli/skill/` (SKILL.md +
  references/) is updated in the SAME change as every CLI surface update.
  This is the surface-parity gate in docs/plan.md "Ongoing conventions":
  argparse `--help` strings and the bundled skill land together, with
  `references/cli.md` and `references/convention.md` byte-identical to
  `docs/cli.md` and `docs/convention.md` (tests/test_skill_refs.py
  enforces; tests/test_skill_quality_artifacts.py pins the quality
  guidance).
- **Host-machine skills, only at production ship.** Skills on this host
  (`~/.claude/skills/`) are NOT refreshed when the CLI changes in-repo.
  Refresh them only when a new version ships to production (PyPI
  publish): run `docs install-skill --force` from the published version,
  and sweep the workflow skills' docs-cli prescriptions for the new
  surface at that point.
