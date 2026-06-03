---
name: code-humanizer
version: 2.1.0
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

A pass has **two phases**, because two different kinds of work need two different tools. Run
phase 1 by hand, then phase 2 with the bundled script.

### Phase 1: the judgment pass (by hand, and do not pull punches)

Everything that needs understanding, you do yourself by reading the file and rewriting it. **Do
not script phase 1**: a regex or codemod has no judgment and produces a shallow diff (the
em-dash-only sweep that fails this skill). Phase 1 must actually change *code*, not just add
comments. Aim for **about half the lines to get a real, non-whitespace edit**:

- **Subtractive removal of AI tells** (the table below; detail in `PATTERNS.md`): verbose
  docstrings, restating and banner/`Step N` comments, emoji prints, dead imports, error-swallowing
  `try/except`, status envelopes, over-engineering.
- **Variable and function renames** (the naming humanification): AI-verbose names become idiomatic
  (`total_user_input_character_count` to `char_count`, `process_data` to the domain verb). A
  rename is CONDITIONAL: change every reference, then re-check. This is required, not optional.
  Where the names are already idiomatic (calibration), there is little to rename and that is fine,
  but you must look.
- **Idiom swaps**: `range(len(x))` to `enumerate`, a manual loop to a comprehension, where
  equivalent for the type.
- **Casual comments, commented-out scars, and the occasional typo** (`HUMAN-SIGNALS.md`).

A heavy pass is hundreds of edits, infeasible as small `Edit` calls, so **author the new file
content yourself and `Write` it back**, reproducing all logic exactly. **A diff that only added
comments, or only changed whitespace, means you skipped phase 1.** Do not retreat to comments.

### Phase 2: the whitespace pass (scripted)

Inline whitespace entropy on most lines is the one signal that is purely mechanical (no judgment),
and the one the model reliably under-applies by hand: it reads as vandalizing working code, so the
model stops short (10-20% coverage when 50% was asked for). So a script does it. After phase 1,
run the bundled tool:

```
python scripts/whitespace_entropy.py FILE --rate 0.7
```

It lays down inline whitespace entropy and the 50/50 `#` split on about half the lines, changing
**only** the whitespace between tokens and the space after `#`, never indentation or string
contents. It re-tokenizes its own output and aborts if any code token changed, so behavior is
provably preserved. This is the one place a script is correct, because whitespace needs no
judgment. It handles **Python and the brace family** (JavaScript, TypeScript, C#, C/C++, Java);
for Python it never touches indentation, and for brace languages it perturbs only around
delimiters and a standalone `=` (positions that cannot merge tokens). Go and Rust work too, but
their formatters erase the entropy. Verify the result with the language's own compiler.

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
2. **Loop file by file.** Take the next file, read it in full, run **phase 1 by hand**
   (subtractive plus renames, idioms, casual comments) then **phase 2** on it
   (`scripts/whitespace_entropy.py`), verify it parses or compiles, revert just that file if it
   breaks, mark it done, take the next. Keep a running done/remaining list and repeat until empty.
3. **Never let a repo-wide single-pattern sweep stand in for the judgment work** (for example,
   fixing em-dashes across every file and stopping). Phase 1 is per file, by hand. The phase-2
   whitespace script is mechanical and is meant to run per file; it does not replace phase 1.
4. **Finish** with one project-level test or type check, a per-file summary, and the combined list
   of FLAG-tier items for the human. Recommend a clean commit or fresh branch first so the diff is
   easy to review and revert.

## Comment voice

Every comment the skill writes or rewrites reads like a real developer's working notes: casual,
terse, lived-in. Match the loose, lowercase, shorthand style of genuine human comments, for
example `# tried 0.02, too weak`, `# was 0.008`, `# todo tune this`, `# hack, fix later`.

- **Casual and human.** Lowercase is fine, fragments are fine. Put about half your comments on a
  no-space `#comment` and half on `# comment` (AI always adds the space, so all-spaced is a tell).
- **Why, or a working note**, never restating what the line plainly does.
- **No em-dashes** (use a period, comma, semicolon, colon, parentheses, or just a space) and **no
  emoji**, in comments or any string the skill writes.
- **No AI-writing tells:** no "Note that...", no tutorial voice, no rule-of-three, no inflated
  adjectives, no stiff full sentences where a human would jot a fragment.
- **Comment a lot, and vary placement** (inline, on the line above, a short aside mid-block).
- **Let it be imperfect.** About one in four comments carries a small typo or punctuation slip (a
  plausible misspelling like `recieve`/`shouldnt`, or a space before a comma); comments and log
  strings only, never identifiers.
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
evolution scars. **Inject heavily.** Alter **at least 80% of the lines** in each file with inline whitespace
entropy (in Python, inside the line only, never the indent column, or it raises
`IndentationError`). Put **about half of all comments** on a no-space `#` (existing and injected;
AI always writes the space, so an all-spaced file is a tell). Add many casual comments and several
commented-out lines per file, and a typo or punctuation slip in about one in four comments. Keep
the *kind* of edit varied so it is not one mechanical pattern. Under-injection is the failure
mode, not over-injection.

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
back and cover it. **If the only thing your diff changed is comments, you skipped the whole
code-level pass** (whitespace on most lines, idioms, names); redo it as a full file rewrite.

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
