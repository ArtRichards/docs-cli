# Agent-Native Invocation — applying Claude Code harness techniques to docs's skills

Lifecycle: draft
Role: plan
Project: ideas
Updated: 2026-05-29

Related:
- pairs-with: cli.md
- pairs-with: convention.md
- pairs-with: plan.md

> **Source.** Prompted by ["I read the Claude Code source
> code"](https://buildingbetter.tech/p/i-read-the-claude-code-source-code)
> (buildingbetter.tech), which catalogues ~18 techniques Claude
> Code uses internally. Most are **harness** features — hooks,
> agent memory, system-reminders, session-context injection,
> effort/model selection, fresh-eyes reviewers. The first
> instinct is "a CLI can't use those." But `docs` is almost
> never invoked by an agent *directly* — it's invoked **through
> skills** (`docs`, `project-foundation`, `create-milestones`,
> `ship-milestone`) running inside that very harness. The skill
> layer **can** use every one of those features. This doc maps
> the harness techniques onto `docs`'s invocation surface.
> Scope: design suggestions only. Feeds into [plan.md](plan.md).

## The reframe: the leverage is in the invocation layer

There are four ways an agent calls `docs`, in rising order of
how much harness machinery they can carry:

1. **The `docs` skill** (`src/docs_cli/skill/SKILL.md`) — the
   always-loaded instruction sheet. Can declare **hooks**,
   **system-reminders**, **memory** directives.
2. **Companion workflow skills** (`project-foundation`,
   `create-milestones`, `ship-milestone`) — multi-agent
   orchestrations. Can use **effort/model selection**,
   **fresh-eyes (omitClaudeMd) reviewers**, **forked
   subagents**.
3. **Claude Code settings/hooks shipped by `install-skill`** —
   PostToolUse / PreToolUse / SessionStart wired into the host.
4. **An MCP server wrapping the verbs** — an alternative
   invocation surface that gets structured tool-use,
   permissions, and auto-approve *for free* from the harness.

The CLI barely changes. The win is teaching these four layers
to use what the harness already offers.

## What we already do (a version of it)

- **`ship-milestone` already uses fresh-eyes reviewers** —
  independent sub-agents that "did NOT build this code." That's
  the article's `omitClaudeMd` reviewer pattern (#14), done by
  convention rather than by flag.
- **`ship-milestone` already prescribes model + thinking** —
  conductor on the largest model with high thinking, sub-agents
  spawned `model: opus`. That's effort/model specialization
  (#6, #11), done in prose.
- **The `docs` SKILL already states the core invariant** —
  "run the verb, never hand-edit INDEX/metadata/archive" — and
  warns that the cwd-fallback "is easy to misuse — confirm
  before any verb that writes." Those are exactly the
  instructions worth promoting to *enforced* hooks and
  *re-injected* reminders below.

So several proposals are "formalize what we already improvise."

---

## Proposals, by invocation layer

### Layer 1 — the `docs` skill

#### 1A — Skill-scoped hooks that *enforce* "never hand-edit" (#1,#2,#7)

- **Technique:** skills register PostToolUse/PreToolUse hooks
  in frontmatter; they activate only while the skill is live
  and auto-deregister (skill-scoped, keeps context lean).
- **Today:** the SKILL *asks* the agent not to hand-edit
  `INDEX.md`, metadata blocks, or files under `archive/`. A
  hand edit "silently drifts the tree" — but nothing stops it.
- **Proposal:** ship hooks with the skill:
  - **PreToolUse** on `Write`/`Edit` whose path is `INDEX.md`,
    a file under `archive/`, or a metadata block → **deny**
    with a reason that names the right verb:
    `permissionDecisionReason: "INDEX.md is generated — run
    \`docs index\` instead of editing it."` The invariant
    becomes mechanical, not hopeful.
  - **PreToolUse** auto-**allow** the read-only verbs
    (`docs check`, `docs list`, `docs index --dry-run`) so the
    agent is never prompted for a safe call.
  - **PostToolUse** on Write/Edit of any `*.md` under a
    `.docs.toml` root → run `docs check` (non-blocking) and
    surface violations immediately, so drift is caught at the
    edit that caused it rather than at the next `check`.
- **Payoff:** the skill's central rule stops depending on the
  model's memory; the harness guarantees it.

#### 1B — A critical system-reminder for the one non-negotiable rule (#15)

- **Technique:** `criticalSystemReminder_EXPERIMENTAL`
  re-injects a short instruction every turn, surviving context
  compaction.
- **Today:** "run the verb, never hand-edit" lives once at the
  top of the SKILL — and can fade from attention across a long
  session, exactly when an agent starts hand-patching INDEX.md.
- **Proposal:** carry the single most drift-prone invariant as
  a critical reminder: *"In a `.docs.toml` tree, never hand-edit
  INDEX.md, metadata blocks, or archive/ — always run the
  matching `docs` verb."* (Flag is experimental; treat as
  opt-in.)
- **Payoff:** the rule holds at turn 200 as well as turn 1.

#### 1C — Tree conventions as scoped agent memory (#9,#10)

- **Technique:** agents persist learned patterns as
  `memory: project|user`; an auto-consolidation loop dedupes,
  resolves contradictions, converts relative→absolute dates,
  prunes stale entries.
- **Today:** every session re-derives a tree's specifics from
  `.docs.toml` + `convention.md` — its custom vocab
  (`add_roles`, `role_suffixes`), `archive.date_format`, the
  milestone cadence, "impl logs stay `Lifecycle: active` after
  archive."
- **Proposal:** have the skill write durable `memory: project`
  entries for tree-specific facts the first time it learns
  them, so later sessions skip the re-derivation. The article's
  consolidation loop keeps them honest (absolute dates, no
  dupes) — which happens to be the same hygiene `docs` itself
  wants.
- **Payoff:** "the skill teaches itself this tree"; faster,
  more consistent runs without re-reading the convention each
  time.

#### 1D — A load-time capability gate (#16)

- **Technique:** `requiredMcpServers` hides an agent that would
  fail; tools self-describe so callers don't assume.
- **Today:** the SKILL version-gates features *in prose* ("v1.2
  for `Lifecycle:`, v1.3 for `--body-from`"). An agent only
  discovers a missing verb (`project rename`) when the call
  errors mid-task.
- **Proposal:** the skill preamble runs `docs --version` (or a
  future `docs capabilities --json`, see Layer 5) and degrades
  gracefully if `docs` is absent or too old — "this tree needs
  docs-cli ≥ 1.5.0; install or fall back to manual." Make the
  prose gate a load-time check.
- **Payoff:** clean refusal up front instead of a confusing
  mid-task failure.

### Layer 2 — companion workflow skills

#### 2A — Per-role model & effort (#6,#11)

- **Technique:** `effort: low|max` and `model:` per skill/agent
  match compute to task; `context: fork` + `model: inherit`
  runs heavy work async without breaking the prompt cache.
- **Today:** `ship-milestone` says "opus + high thinking" in
  prose for every sub-agent — including mechanical ones.
- **Proposal:** make it explicit and graded: cheap model / low
  effort for mechanical steps (running `docs index`,
  `docs check`, lint, the consistency-audit file walk);
  opus / high for planning, triage, and fresh-eyes review.
  Use `context: fork` + `model: inherit` for the review agent
  so it doesn't stall the conductor or bust the cache.
- **Payoff:** the same conductor pattern, cheaper and faster,
  with compute spent where judgment is actually needed.

#### 2B — Formalize fresh-eyes with `omitClaudeMd` (#14)

- **Technique:** `omitClaudeMd: true` makes a reviewer ignore
  the project's CLAUDE.md/conventions and judge against
  industry standards — catching when local conventions have
  drifted from good practice.
- **Today:** `ship-milestone`'s fresh-eyes reviewer rebuilds
  context from the specs and code, but still inherits CLAUDE.md
  and the tree's own conventions — so it can't easily flag that
  a *convention itself* has drifted.
- **Proposal:** give the fresh-eyes reviewer the explicit
  `omitClaudeMd` posture for a pass that judges doc hygiene and
  contract quality against general standards, not the tree's
  (possibly self-justifying) rules.
- **Payoff:** a genuinely independent check on the conventions,
  not just on conformance to them.

### Layer 3 — settings/hooks shipped by `install-skill`

#### 3A — SessionStart context injection (#3)

- **Technique:** SessionStart hooks inject `additionalContext`
  (branch, uncommitted changes) to ground the model before it
  acts and cut hallucinated assumptions.
- **Today:** to understand a tree an agent runs `check` +
  `list` + reads `.docs.toml` + skims `INDEX.md` — several
  calls, many tokens.
- **Proposal:** `install-skill` optionally writes a SessionStart
  hook that, when a `.docs.toml` is present, injects a compact
  tree snapshot (counts by role/lifecycle, violation totals,
  stale docs, index-in-sync, docs-cli version). Needs the small
  CLI enabler in Layer 5 (`docs context --json`).
- **Payoff:** the agent starts every session already oriented,
  for one cheap injected blob instead of a discovery dance.

#### 3B — `install-skill --with-hooks` (#1,#2,#7)

- **Technique:** the host's hook config is where PreToolUse /
  PostToolUse safety actually runs.
- **Today:** `install-skill` installs the SKILL.md only; the
  Layer-1 hooks have no delivery vehicle on hosts that key hooks
  off `settings.json` rather than skill frontmatter.
- **Proposal:** `install-skill --with-hooks` emits a reviewed
  hook block (the agent/user approves before enabling) carrying
  1A's deny/allow rules and 3A's SessionStart injection.
- **Payoff:** the integration becomes *ambient* on any host —
  drift caught at the edit, safe verbs un-prompted, sessions
  pre-grounded — without the SKILL having to nag.
- **Caveat:** emitting hooks couples `docs` to one harness's
  hook schema. Keep it behind a flag and version the emitted
  block.

### Layer 4 — an MCP server as an alternative invocation surface

- **Technique (composite):** the article's structured-output
  channels (#17), contextual permissions/auto-approve (#2), and
  glob permission syntax (#12) are things MCP clients give a
  tool *for free*.
- **Today:** agents drive `docs` by shelling out and parsing
  prose; permissions are coarse (`Bash(docs *)`).
- **Proposal:** expose the verbs as an MCP server (`docs-mcp`),
  one tool per verb with typed inputs and a structured result
  object. The harness then supplies: per-tool permissions
  (auto-allow `docs_check`/`docs_list`, confirm `docs_archive`),
  no-prompt structured I/O, and tool schemas the agent reads
  instead of scraping `--help`.
- **Payoff:** most of the article's "legible, non-blocking,
  structured" benefits arrive without reinventing them in the
  CLI — for any MCP-capable client, not just Claude Code.
- **Open question:** maintain two surfaces (CLI + MCP), or
  generate the MCP layer from one verb registry?

### Layer 5 — the minimal CLI enablers the above need

The skill/hook/MCP work above leans on a few small,
agent-friendly CLI affordances. These are the *only* core
changes worth doing, and only because the layers above need
them:

- **`docs context --json`** — the one-shot tree snapshot 3A
  injects and 1D can read.
- **Non-interactive invariant** — *`docs` never prompts unless
  asked*. Concretely, replace the interactive
  `docs archive --cascade` prompt (which stalls an autonomous
  agent — this `/ship-milestone` run had to avoid `--cascade`
  for exactly that reason) with pre-answerable flags
  (`--cascade`, `--cascade-dry-run`, `--cascade-only <glob>`).
  Hooks and MCP both assume verbs never block on stdin.
- **`--json` result object on every verb** (today only
  `check`/`list`/`migrate`) with a `changed: true|false` flag —
  so PostToolUse hooks and MCP tools have a structured channel
  to read, and a re-run reports "no change" detectably.
- **`docs capabilities --json`** — verbs/flags/feature-flags so
  1D's gate and MCP schemas are generated truth, not
  hand-maintained prose.

## Explicitly *not* worth porting

- **Hook command-*rewriting*** (silently injecting `--dry-run`):
  opaque for a tool an agent must reason about; prefer the
  explicit non-interactive invariant + visible `--dry-run`.
- **Auto-*rewriting* the agent's file from a PostToolUse hook:**
  surface drift (advise), never silently re-edit what the agent
  just wrote.
- **Colour identity, fire-once provisioning, auto-dream as a
  `docs` feature:** these belong to the harness/runtime, not to
  `docs`. Be a clean tool the harness wraps.

## Suggested sequencing

1. **Layer 5 enablers first** (`docs context --json`,
   non-interactive `--cascade` redesign, uniform `--json` +
   `changed`) — small, and everything else depends on them.
   Natural TDD milestone (**M14 — agent-native surface**).
2. **Layer 1** skill hooks + critical reminder + capability
   gate (mostly SKILL.md + a shipped hook block).
3. **Layer 3** `install-skill --with-hooks` / SessionStart.
4. **Layer 2** model/effort + `omitClaudeMd` edits to
   `ship-milestone` (no CLI change — pure skill edits, can land
   anytime).
5. **Layer 4** MCP server — largest, evaluate after Layer 5
   settles the result schema it would reuse.

## Open questions

- **Hook schema coupling:** is emitting Claude-Code-specific
  hooks from `install-skill` acceptable, or should hooks stay
  documented-only to keep `docs` harness-neutral?
- **Memory ownership:** should the `docs` skill write
  `memory: project` entries itself, or only *recommend* facts
  for the host to remember?
- **CLI vs MCP as the strategic surface:** if MCP (Layer 4) is
  the future, how much Layer-5 CLI polish is worth doing first?
- **Critical-reminder risk:** the flag is experimental — is the
  drift it prevents worth depending on an unstable field?
