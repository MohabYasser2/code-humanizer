---
name: code-humanizer
version: 1.6.0
description: >-
  Humanize source code so it reads as natural, hand-written work rather than AI-generated,
  without changing behavior. Use whenever the user wants to humanize, naturalize, or de-AI code,
  make code look hand-written, strip AI "slop" or "tells", clean up AI-generated code, or pass
  code off as human-written, and whenever they point it at a file, a folder, or a whole repo. By
  default (auto mode) it removes AI tells (over-documentation, banner and Step-N comments, emoji
  and print narration, verbose names, over-engineering, error-swallowing try/except, dead
  imports) then heavily injects human fingerprints (casual comments, commented-out lines,
  formatting entropy, idiomatic naming). Clean-only mode removes without injecting; additive mode
  only injects. The model edits each file by hand, never via a generated script, going file by
  file across a repo. Every edit is behavior-preserving under a strict safety tier, and injected
  comments are casual with no em-dashes or emoji.
license: MIT
compatibility: claude-code opencode
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

# Code Humanizer

Make source code read as natural, hand-written work instead of AI-generated, without changing
what it does. AI code is rarely *wrong*; it is eerily uniform and over-finished: every function
documented, every error caught, every name spelled out, every script wrapped in a class "just in
case." This skill strips that polish and, by default, adds back the fingerprints of real human
code. It is the code companion to the prose `humanizer` skill: that one rewrites words, this one
rewrites code style and structure under a hard rule that the program must still do the same thing.

## Modes

Default to auto.

- **Auto (default, plain `/code-humanizer`):** clean, then humanize. Run the subtractive pass and
  then inject human signals, in one pass, so the result reads as genuinely hand-written.
- **Clean-only (`--clean-only`, or "just remove AI tells"):** the subtractive pass only, no
  injection. Strictly cleanup.
- **Additive (`--inject-signals`):** injection only, for code that is already clean.

Scope is a snippet, one file, or a whole folder or repo (see *Running on a folder*).

## The behavior contract (the floor under every edit)

Code is not prose; you cannot freely reword it. Every edit must satisfy these, in all modes:

- **Success-path behavior is identical:** same inputs, outputs, return types, side effects,
  ordering, and public API (function names, signatures, exports) unless the user asks otherwise.
- **Never introduce a bug, vulnerability, or drift to "look human."** Do not downgrade libraries,
  weaken validation, or break edge cases.
- **Failure-path changes are surfaced, not silent.** Removing a swallow-all `except` makes the
  code raise instead of returning `None`; that is usually the right call, but flag it as an
  explicit decision, never bury it.
- **Verify.** Run the project's tests / type checker / linter, or at least a parse or compile
  check, after editing, and report the result. If you cannot verify, say so.
- **When unsure an edit is safe, keep the behavior and flag the smell** instead of guessing.

Injection is governed by a three-level safety tier (full detail in `HUMAN-SIGNALS.md`):

- **SAFE** = provably behavior-neutral (comments, blank lines, whitespace in brace languages).
  Auto-apply.
- **CONDITIONAL** = safe only if a precondition holds (a rename touching every reference, an
  idiom swap that is equivalent for this type). Verify it, otherwise treat as FLAG.
- **FLAG** = can change behavior or fail to compile (identifier typos, Python indentation or tab
  changes, `== True`/`== None`). Never auto-apply; report it for the human to apply by hand.

## How to run

**Edit by hand. Never script it.** Read each file and make every change yourself with
Read/Edit/Write. Do not write or run a script (sed, awk, a regex pass, a codemod) to transform
the code. A script does blind substitution: it catches only the one pattern you encoded, applies
no judgment, misses every semantic rewrite (renames, restructuring, rephrasing a comment), and
produces a shallow diff such as swapping a single punctuation mark. Scripts are allowed only for
verification (tests, compile, parse check) after the edits are made.

**Cover everything.** Process every file and region top to bottom, including code that looks
human-written. "Looks clean" is never a reason to skip. The only limits are behavior (above) and
meaning: do not delete a comment that records a real reason; rewrite it to the casual voice
instead.

### Running on a folder or repo

Point the skill at a directory and it processes every source file itself, one at a time. The user
does not name each file.

1. **Enumerate.** Prefer `git ls-files` for the tracked source set (it already excludes ignored
   and generated paths); otherwise use Glob. Keep first-party source (`.py`, `.js`, `.ts`,
   `.tsx`, `.jsx`, `.cs`, `.java`, `.c`, `.cpp`, `.h`, `.go`). Skip dependency and build
   directories (`node_modules`, `vendor`, `dist`, `build`, `target`, `bin`, `obj`, `__pycache__`,
   `.venv`/`venv`, `.git`), minified or generated files, binaries, data, and model files. List the
   set and its size before starting.
2. **Loop file by file.** Take the next file, read it in full, fully humanize it (the complete
   pass: subtractive plus heavy injection in auto), verify it parses or compiles, revert just that
   file if it breaks, mark it done, take the next. Keep a running done/remaining list and repeat
   until the list is empty.
3. **Never run a repo-wide single-pattern sweep** (for example, fix em-dashes across every file
   and stop). That is the shallow, scripted failure mode this skill exists to prevent. Each file
   gets its own complete, by-hand pass before you advance.
4. **Finish** with one project-level test or type check, a per-file summary, and the combined list
   of FLAG-tier items for the human. Recommend a clean commit or fresh branch first so the diff is
   easy to review and revert.

## Comment voice

Every comment the skill writes or rewrites reads like a real developer's working notes: casual,
terse, lived-in. Match the loose, lowercase, shorthand style of genuine human comments, for
example `# tried 0.02, too weak`, `# was 0.008`, `# todo tune this`, `# hack, fix later`.

- **Casual and human.** Lowercase is fine, fragments are fine, a no-space `#comment` is fine.
- **Why, or a working note**, never restating what the line plainly does.
- **No em-dashes** (use a period, comma, semicolon, colon, parentheses, or just a space) and **no
  emoji**, in comments or any string the skill writes.
- **No AI-writing tells:** no "Note that...", no tutorial voice, no rule-of-three, no inflated
  adjectives, no stiff full sentences where a human would jot a fragment.
- **Comment a lot, and vary placement** (inline, on the line above, a short aside mid-block).
- **Calibration wins:** if the file already has a comment style, match it.

## Match the surrounding style (calibration)

The strongest lever is matching the file's own conventions. Before editing, read the target file
(or a sample, or a neighbour) and note its naming length, comment density and kind, type-hint
usage, quote and indentation habits, and idioms. Then match them: if the repo uses `cfg`/`idx`,
do not expand to `configuration`/`index`; if it never writes docstrings, do not add them. With no
sample and no repo context, default to plain, lightly-commented, idiomatic code in the file's
language.

## The subtractive pass (what to remove)

Remove these AI tells. `PATTERNS.md` carries the Problem/Before/After for each; read it for the
detail and the worked example.

| # | Tell | Fix |
|---|------|-----|
| 1 | Docstrings on trivial functions | drop, or shrink to one line |
| 2 | Comments that restate the code | delete |
| 3 | Section banners and `# Step N:` | delete |
| 4 | Tutorial-voice (`# Here we...`) | delete or rewrite as a *why* |
| 5 | Emoji and `print()` narration | remove (keep real logging) |
| 6 | Placeholder comments (`# TODO: your logic`) | remove |
| 7 | What-not-why, uniform comment density | a few *why* comments, uneven |
| 8 | Verbose dictionary-style names | shorten to idiomatic |
| 9 | Generic names (`data`, `process_data`) | name for the domain |
| 10 | No short/idiomatic locals | use `i`, `n`, `tmp`, `enumerate` |
| 11 | Over-engineering (factories/ABCs/DI) | inline to a function |
| 12 | Excessive modularity / single-use helpers | merge back |
| 13 | `{"status": "success", ...}` envelope returns | return the value or raise |
| 14 | Eerie uniformity | allow valid variance (no fake mess) |
| 15 | Blanket `try/except` that swallows errors | catch specific or raise (flag it) |
| 16 | Redundant defensive null/type checks | drop the unreachable ones |
| 17 | Useless type hints | trim in untyped repos; keep in typed |
| 18 | Appended `__main__` demo block | remove throwaway demos |
| 19 | Markdown inside comments | plain text |
| 20 | Non-idiomatic verbosity (`range(len())`) | use the repo's idioms |
| 21 | Dead and over-grouped imports | trim to what is used |
| 22 | Hallucinated APIs / stale deps (audit-only) | flag, never fabricate a fix |

For pattern 14, do not manufacture fake mess during the subtractive pass; deliberate scars are
the injection pass's job, not random noise.

## The injection pass (what to add: auto and additive modes)

After the subtractive pass, add the affirmative fingerprints of hand-written code: casual
comments, commented-out trial code and debug prints, formatting entropy, idiomatic naming,
evolution scars. **Inject heavily**: reach across most of the catalog, with many casual comments
and several commented-out lines per file, kept uneven so the additions do not form a mechanically
uniform layer. Under-injection is the failure mode, not over-injection.

- Read **`HUMAN-SIGNALS.md`** for the H1-H50 catalog, the SAFE/CONDITIONAL/FLAG tier, the
  injection-volume rule, the complete-reference rename checklist, and the per-file process.
- For **JavaScript, TypeScript, or C#**, also read **`LANGUAGES.md`** for the per-language tiers
  (TS type edits are compile-gated; JS `===`/`var` swaps and C# field renames are FLAG) and the
  formatter caveat (Prettier / `dotnet format` normalize injected whitespace away).
- Auto runs the subtractive pass then injection; additive runs injection alone; clean-only skips
  injection entirely.

## What to preserve

Processing everything does not mean destroying meaning. Keep the *content* of: genuinely useful
docstrings on public APIs (bring the wording into the casual voice), why-comments, a real
`__main__`, real logging and error handling for reachable failures, a typed codebase's types, and
project conventions (a mandated envelope, a house naming scheme). Human-looking code (TODOs with
real context, terse names, domain vocabulary, uneven polish) still gets the full pass: keep its
content, do not skip it.

## Process and deliver

Per file: read it in full, edit by hand, then re-check signatures, control flow, returns, side
effects, and ordering against the original. List any failure-path change. Verify (tests, type
check, or at least a parse/compile). Ask "what still reads as AI, and what did I skip?" and go
back and cover it.

Deliver: the rewritten code, the failure-path / behavior-relevant changes (or "none, behavior
identical"), any audit-only flags (hallucinated APIs, stale deps), and a short summary of what
changed and why.

## Reference files

- **`PATTERNS.md`**: the 22 subtractive patterns with Before/After, plus a full worked example.
  Read it when running the subtractive pass.
- **`HUMAN-SIGNALS.md`**: the injection catalog (H1-H50), the safety tier, the injection-volume
  rule, the rename checklist, and the per-file process. Read it for any injection (auto or
  additive mode).
- **`LANGUAGES.md`**: per-language tiers and traps for JavaScript, TypeScript, and C#. Read it
  when humanizing those languages.

The pattern list is distilled from published forensics on AI-generated code: the tell is not that
the code is wrong, but that it is over-documented, over-engineered, over-defensive, and uniform,
with no individual voice. Humanizing removes that polish where it is noise and matches the idiom
of a real codebase, never adding bugs or changing what the program does.
