# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, etc.) working in this skill directory.

## What this is

A **Claude Code / OpenCode skill** implemented entirely as Markdown. The runtime artifact is `SKILL.md`: the agent reads its YAML frontmatter (metadata + allowed tools) followed by the editor prompt. There is no build step and no code to run.

This is the **code** humanizer — the companion to the prose `humanizer` skill. Where the prose skill rewrites words, this one rewrites code *style and structure under a hard behavior-preservation constraint*. That constraint is the soul of the skill: any edit to the prompt that weakens it (allowing logic changes, bug injection, silent failure-path changes, or unverifiable rewrites) is a regression.

The skill has **two tracks**: the default **subtractive** one (`SKILL.md`, remove AI tells) and an opt-in **additive** one (`HUMAN-SIGNALS.md`, inject human signals). The additive track does deliberately add formatting/comment entropy, but the behavior-preservation constraint survives intact through its **🟢/🟡/🔴 safety tier**: only provably behavior-neutral (🟢) or verified-complete (🟡) edits are auto-applied; anything that could change behavior or fail to compile (🔴) is flagged for the human, never written. Weakening that tier — letting the additive track auto-apply a 🔴 edit, or apply Python indentation/tab changes — is a regression of the same kind as weakening the behavior contract.

## Key files

- `SKILL.md` — the skill itself. YAML frontmatter (`name`, `version`, `description`, `license`, `compatibility`, `allowed-tools`) followed by the numbered pattern list with Before/After examples, plus the pointer to the opt-in injection track. **This is the source of truth for the default (subtractive) mode.**
- `HUMAN-SIGNALS.md` — the opt-in **additive** track loaded on demand when the user asks to inject human signals. Holds the injection contract, the 🟢/🟡/🔴 safety tier, the per-language whitespace matrix, the H1–H50 catalog, the density rule, the complete-reference rename checklist, and worked examples. **This is the source of truth for the additive mode.**
- `LANGUAGES.md` — per-language safety detail for the additive track, loaded when injecting into **JavaScript, TypeScript, or C#** (plus shorter C-family / Go-Rust notes). Holds the per-language tier shifts, language-specific human signals, the formatter caveat, and 🔴 traps. **This is the source of truth for language-specific tiers.**
- `README.md` — for humans: what it does, installation, usage, style calibration, the subtractive pattern tables, the additive H-track summary, the language coverage, the worked example, and version history.

## The maintenance contract

`SKILL.md`, `HUMAN-SIGNALS.md`, `LANGUAGES.md`, and `README.md` must stay in sync. When you change behavior or content:

- **Subtractive patterns:** the skill defines **22 numbered patterns** (1–22) in `SKILL.md`. If you add, remove, or renumber any, update the README pattern tables, its "N Patterns Detected" heading, and every cross-reference in the same change. Keep numbering stable unless deliberately renumbering.
- **Additive signals:** the injection track defines **50 signals** (H1–H50) in `HUMAN-SIGNALS.md`, grouped into seven categories. If you add, remove, or renumber any, update the README H-track summary table and group ranges in the same change. The `H` namespace is kept separate from the `1–22` namespace on purpose — do not merge them.
- **Language coverage:** `LANGUAGES.md` gives first-class tiers for **JavaScript, TypeScript, C#** (plus C-family / Go-Rust). The per-language tier shifts there must not contradict the safety-matrix row in `HUMAN-SIGNALS.md` or the cross-references in `SKILL.md`/`README.md`. If you add a language or change a tier, update all four. Every tier claim must be true (e.g. "TS type edits are compile-gated 🟡", "C# `var`↔explicit is 🟢"); a wrong tier that auto-applies a breaking edit is a regression.
- **The behavior contract** (the "THE BEHAVIOR CONTRACT" section in `SKILL.md`) and the **injection contract + safety tier** (in `HUMAN-SIGNALS.md`) are the non-negotiable core. Do not soften either. The skill must never trade correctness for "looking human," and the additive track must never auto-apply a 🔴 edit.
- **Version:** `SKILL.md` frontmatter has a `version:` field and `README.md` has a "Version History" section. Bump both together.
- **Non-obvious fixes:** if you change the prompt to handle a tricky failure mode (a rewrite that changed behavior, a mis-applied idiom), add a short note to the README version history explaining what was fixed and why.

## Editing the prompt files

- Preserve valid YAML frontmatter in `SKILL.md` (formatting and indentation). `HUMAN-SIGNALS.md` and `README.md` carry no frontmatter.
- The prose below the frontmatter is the product. Edit it like a careful instruction document, not code.
- All Before/After examples must be **correct, runnable, and behavior-equivalent on the success path**. If an example intentionally shows a failure-path change (e.g., removing a swallow-all `except`), it must be labelled as such — mirroring what the skill asks its user-facing output to do.
- In `HUMAN-SIGNALS.md`, every catalog row needs a **safety tier** (🟢/🟡/🔴), and worked examples must (a) stay behavior-equivalent, (b) leave Python indentation/tabs untouched, and (c) show 🔴 items as *flagged, not applied*. An example that auto-applies a 🔴 edit is a bug in the skill.
- Default example language is **Python**, with **C/C++/Java/JS** used where a whitespace signal needs a brace language. Keep examples idiomatic and minimal.
