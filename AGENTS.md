# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, etc.) working in this skill directory.

## What this is

A **Claude Code / OpenCode skill** implemented entirely as Markdown. The runtime artifact is `SKILL.md`: the agent reads its YAML frontmatter (metadata + allowed tools) followed by the editor prompt. There is no build step and no code to run.

This is the **code** humanizer — the companion to the prose `humanizer` skill. Where the prose skill rewrites words, this one rewrites code *style and structure under a hard behavior-preservation constraint*. That constraint is the soul of the skill: any edit to the prompt that weakens it (allowing logic changes, bug injection, silent failure-path changes, or unverifiable rewrites) is a regression.

## Key files

- `SKILL.md` — the skill itself. YAML frontmatter (`name`, `version`, `description`, `license`, `compatibility`, `allowed-tools`) followed by the numbered pattern list with Before/After examples. **This is the source of truth.**
- `README.md` — for humans: what it does, installation, usage, style calibration, a summary table of the patterns, the worked example, and version history.

## The maintenance contract

`SKILL.md` and `README.md` must stay in sync. When you change behavior or content:

- **Patterns:** the skill currently defines **22 numbered patterns**. If you add, remove, or renumber any, update the README pattern tables, its "N Patterns Detected" heading, and every cross-reference in the same change. Keep numbering stable unless deliberately renumbering.
- **The behavior contract** (the "THE BEHAVIOR CONTRACT" section in `SKILL.md`) is the non-negotiable core. Do not soften it. The skill must never trade correctness for "looking human."
- **Version:** `SKILL.md` frontmatter has a `version:` field and `README.md` has a "Version History" section. Bump both together.
- **Non-obvious fixes:** if you change the prompt to handle a tricky failure mode (a rewrite that changed behavior, a mis-applied idiom), add a short note to the README version history explaining what was fixed and why.

## Editing SKILL.md

- Preserve valid YAML frontmatter (formatting and indentation).
- The prompt below the frontmatter is the product. Edit it like a careful instruction document, not code.
- All Before/After examples must be **correct, runnable, and behavior-equivalent on the success path**. If an example intentionally shows a failure-path change (e.g., removing a swallow-all `except`), it must be labelled as such — mirroring what the skill asks its user-facing output to do.
- Default example language is **Python**. Keep examples idiomatic and minimal.
