# Code Humanizer

A skill for Claude Code and OpenCode that removes the signs of AI-generated **code**, making source read as natural, idiomatic, human-written code — without changing what it does. It is the code-focused companion to the prose [`humanizer`](../humanizer) skill.

## What it does

AI-generated code is rarely wrong in syntax. It is *eerily uniform and over-finished*: a docstring on every function, a comment on every line, a blanket `try/except` around everything, names spelled out as full sentences, and a class where a function would do. This skill strips that "slop" and naturalizes the style to match a real codebase, under one hard rule: **the program must still behave identically.**

Most of these edits also make the code genuinely better — less noise, less over-abstraction, fewer error-swallowing wrappers.

It has **two modes**:

- **Subtractive (default):** the 22 patterns below — remove AI tells, behavior-preserving.
- **Additive (opt-in):** a separate `HUMAN-SIGNALS.md` track that *injects* the affirmative
  fingerprints of hand-written code (formatting entropy, commented-out trial code, lived-in
  `FIXME`s, typos in comments, idiosyncratic naming). Off by default; runs only when you ask.
  It is governed by a SAFE/CONDITIONAL/FLAG safety tier so it never auto-applies an edit that could change
  behavior or break — see [Human-signal injection](#human-signal-injection-opt-in) below.

## Installation

The skill is just a folder of Markdown files. Drop it into your skills directory and it's live.

### Option A — clone (recommended)

**macOS / Linux:**
```bash
git clone https://github.com/MohabYasser2/code-humanizer.git ~/.claude/skills/code-humanizer
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/MohabYasser2/code-humanizer.git "$env:USERPROFILE\.claude\skills\code-humanizer"
```

### Option B — download ZIP

On the GitHub page, click **Code ▸ Download ZIP**, then extract so that `SKILL.md` lands at:
- macOS / Linux: `~/.claude/skills/code-humanizer/SKILL.md`
- Windows: `%USERPROFILE%\.claude\skills\code-humanizer\SKILL.md`

### OpenCode

OpenCode also scans `~/.claude/skills/`, so the same folder works for both tools (or clone into `~/.config/opencode/skills/code-humanizer`).

Then restart Claude Code / OpenCode and run `/code-humanizer`.

## Usage

```
/code-humanizer

[paste your code here]
```

Or ask directly:

```
Humanize this code so it doesn't look AI-generated: [code]
```

### Style calibration (recommended)

The strongest lever is matching an existing human style. Point the skill at a sample or the surrounding repo:

```
/code-humanizer

Match the style in this file of mine: [paste sample]

Now humanize:
[paste AI code]
```

Or, in a repo: *"Humanize `foo.py` to match the conventions in `bar.py`."* The skill reads naming, comment density, type-hint usage, quote style, and idioms, then rewrites to fit — instead of producing generic "clean" output.

## The behavior contract

This is what makes a *code* humanizer different from a prose one:

- **Success-path behavior is identical** — same inputs, outputs, return types, side effects, ordering, and public API.
- **No bugs, no vulnerabilities, no behavior drift** introduced to "look human."
- **Failure-path changes are surfaced, not silent** — e.g., removing a swallow-all `except` makes the code raise instead of returning `None`; that is flagged as an explicit decision.
- **Verified when possible** — tests / type checker / linter are run after the rewrite if the project has them.

## 22 Patterns Detected (with Before/After)

### Comments & documentation

| # | Pattern | Fix |
|---|---------|-----|
| 1 | Docstrings on trivial functions | Drop, or shrink to one line |
| 2 | Comments that restate the code | Delete |
| 3 | Section banners & `# Step N:` comments | Delete |
| 4 | Tutorial-voice comments (`# Here we...`) | Delete or rewrite as *why* |
| 5 | Emoji & `print()` narration | Remove (keep real logging) |
| 6 | Placeholder comments (`# TODO: your logic`) | Remove |
| 7 | Comments explain *what*, uniform density | Prefer a few *why* comments |

### Naming

| # | Pattern | Fix |
|---|---------|-----|
| 8 | Verbose dictionary-style names | Shorten to idiomatic |
| 9 | Generic names (`data`, `result`, `process_data`) | Name for the domain |
| 10 | No short/idiomatic local names | Use `i`, `n`, `tmp`, `enumerate` |

### Structure & abstraction

| # | Pattern | Fix |
|---|---------|-----|
| 11 | Over-engineering (factories/ABCs/DI) for simple tasks | Inline to a function |
| 12 | Excessive modularity / single-use helpers | Merge back |
| 13 | `{"status": "success", ...}` envelope returns | Return the value / raise |
| 14 | Eerie uniformity | Allow valid variance (never fake mess) |

### Error handling

| # | Pattern | Fix |
|---|---------|-----|
| 15 | Blanket `try/except` that swallows errors | Catch specific or let it raise (flag it) |
| 16 | Redundant defensive null/type checks | Drop the unreachable ones |

### Types, formatting, idioms

| # | Pattern | Fix |
|---|---------|-----|
| 17 | Useless type hints | Trim in untyped repos; keep in typed ones |
| 18 | Appended `if __name__ == "__main__"` demo | Remove throwaway demos |
| 19 | Markdown inside comments/docstrings | Plain text |
| 20 | Non-idiomatic verbosity (`range(len(...))`) | Use the repo's idioms |
| 21 | Dead & over-grouped imports | Trim to what's used |

### Audit-only (flag, don't silently rewrite)

| # | Pattern | Fix |
|---|---------|-----|
| 22 | Hallucinated APIs / deprecated libraries | Flag for the user; never fabricate a fix |

## Human-signal injection (opt-in)

The patterns above *remove* AI tells. The opt-in **additive** track in
[`HUMAN-SIGNALS.md`](HUMAN-SIGNALS.md) does the reverse — it *injects* the affirmative
fingerprints of hand-written code. Trigger it explicitly: *"inject human signals"*,
*"make this look hand-written"*, or `--inject-signals`. It stays off otherwise.

The research basis ([*Whitespaces Don't Lie*](https://arxiv.org/pdf/2601.19264)): human code
shows **15–40% higher formatting variance** than AI on identical logic — *"humans create
intentional inconsistency; AI generates unintentional uniformity."* So the goal is to add
**variance, not mess** — and variance that doesn't compile is useless.

Every signal carries a safety tier:

- **SAFE** — behavior-neutral (comments, blank lines, whitespace in brace languages, typos
  inside log strings). Auto-applied.
- **CONDITIONAL** — safe only if applied completely / in a compatible language (a total
  rename, an equivalent idiom swap). Applied only after verifying.
- **FLAG** — can change behavior or fail to compile (identifier typos, Python
  indentation/tabs, `== True`/`== None`). **Reported, never auto-applied.**

The H-track has 50 signals across seven groups:

| Group | Examples | Notes |
|-------|----------|-------|
| Whitespace entropy (H1–H11) | `x=y` vs `x = y`, `int x = y ;`, irregular blank lines, mixed quotes | SAFE in C/Java/JS; indentation/tabs are FLAG in **Python** |
| Lived-in comments (H12–H21) | commented-out code, `# FIXME ask Omar`, venting, stale comments | the strongest human tell — AI strips these |
| Typos & grammar (H22–H26) | `recieve`/`occured` in comments, loose grammar | SAFE in comments; FLAG in identifiers |
| Naming chaos (H27–H31) | `tmp`/`tmp2`, `df_copy`, camel+snake mix | CONDITIONAL — rename every reference |
| Structural scars (H32–H40) | copy-paste duplication, magic numbers, `i = i + 1` | uneven polish, careful core + rushed edge |
| Import habits (H41–H44) | mid-file imports, unused leftovers, commented-out imports | SAFE |
| Legacy idioms (H45–H49) | `range(len(x))`, redundant parens, `== True` | `== True`/`== None` are FLAG |

Plus the **density rule**: apply an *uneven* subset (5–10 signal types per file), not a
uniform layer — a uniform layer of noise is just a different detectable uniformity. And a hard
**language branch**: in Python, never touch leading indentation or tabs (syntactic → FLAG); all
Python entropy comes from operator spacing, blank lines, comments, and idioms.

For **JavaScript, TypeScript, and C#**, [`LANGUAGES.md`](LANGUAGES.md) carries the per-language
tiers and traps — TS type edits are compile-gated CONDITIONAL; JS `===`→`==` and `let`→`var` are FLAG; C#
`var`↔explicit, `#region`, and LINQ↔method syntax are SAFE — plus a **formatter caveat**: if
Prettier / `dotnet format` / EditorConfig runs on save or in CI, injected whitespace is
normalized away, so lean on comments, naming, and idioms instead. Renames are hardened by a
**complete-reference checklist** (locals are CONDITIONAL; fields/properties/public symbols are FLAG because
they bind by string in serialization and reflection).

## Full Example

**Before (obviously AI-generated):**
```python
def process_user_data(user_data_list):
    """Processes a list of user data dictionaries and returns the active users."""
    try:
        # Initialize the list to store active users
        active_users_list = []
        # Step 1: Loop through each user
        for user_data_item in user_data_list:
            # Step 2: Check if the user is active
            if user_data_item.get("is_active") == True:
                active_users_list.append(user_data_item)
        print("✅ Successfully processed user data!")
        return active_users_list
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None
```

**After (humanized):**
```python
def active_users(users):
    """Return the users with a truthy `is_active`, in input order."""
    return [u for u in users if u.get("is_active")]
```

*Behavior note:* the swallow-all `except` was removed, so malformed input now raises instead of returning `None` (intentional — surfaces real errors). Success-path output is unchanged.

## Scope

The **default subtractive mode** does behavior-preserving naturalization (remove AI tells +
match idiomatic human/repo style). The **opt-in additive mode** injects human signals, but is
bounded by the same hard line: it auto-applies only edits proven behavior-neutral (SAFE) or
verified-complete (CONDITIONAL), and **flags — never auto-writes — anything that could change behavior
or fail to compile** (FLAG: identifier typos, Python indentation/tab changes, `== True`/`== None`).
Neither mode injects deliberate bugs, vulnerabilities, or stale dependencies, and neither
silently rewrites code it can't verify. Examples are **Python**-primary; the additive track has
first-class, per-language coverage for **JavaScript, TypeScript, and C#** (see
[`LANGUAGES.md`](LANGUAGES.md)), plus the wider C-family, because it branches on language —
whitespace that is free in C# is fatal in Python, and type edits that are safe in JS break a
strict TypeScript build.

> Note on honest use: where authorship disclosure is required (for example, academic submissions or assessments), disclosing AI assistance remains your responsibility. This skill is a code-quality and style tool, not a way to misrepresent authorship.

## Version History

- **1.1.0** — Added the opt-in **additive** track (`HUMAN-SIGNALS.md`): 50 human-signal
  patterns (H1–H50) across whitespace entropy, lived-in comments, typos, naming chaos,
  structural scars, import habits, and legacy idioms. Introduced the SAFE/CONDITIONAL/FLAG safety tier
  (auto-apply only behavior-neutral edits; flag-only for anything that could break), a
  per-language whitespace matrix (Python indentation/tabs are flag-only), the density rule
  (uneven subset, not a uniform layer), and two worked examples. Added **`LANGUAGES.md`** with
  first-class per-language coverage for **JavaScript, TypeScript, and C#** (plus the wider
  C-family and a formatter caveat), and hardened the CONDITIONAL rename rule with a
  **complete-reference checklist** (locals CONDITIONAL; fields/properties/public symbols FLAG). Resolved
  the Pattern 14 contradiction (the "no fake mess" rule now scopes to the default subtractive
  mode). Grounded in published code-stylometry forensics (*Whitespaces Don't Lie*,
  arXiv 2601.19264). Behavior-preservation validated on a sample (subtractive + injection,
  parse + behavior-identical).
- **1.0.0** — Initial release. 22 patterns across comments/docs, naming, structure, error handling, types/formatting/idioms, and audit-only. Behavior contract, style calibration, detection guidance, and a full worked example. Python-focused.

## License

MIT
