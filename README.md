# Code Humanizer

A skill for Claude Code and OpenCode that removes the signs of AI-generated **code**, making source read as natural, idiomatic, human-written code — without changing what it does. It is the code-focused companion to the prose [`humanizer`](../humanizer) skill.

## What it does

AI-generated code is rarely wrong in syntax. It is *eerily uniform and over-finished*: a docstring on every function, a comment on every line, a blanket `try/except` around everything, names spelled out as full sentences, and a class where a function would do. This skill strips that "slop" and naturalizes the style to match a real codebase, under one hard rule: **the program must still behave identically.**

Most of these edits also make the code genuinely better — less noise, less over-abstraction, fewer error-swallowing wrappers.

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

Configured for **behavior-preserving naturalization** (remove AI tells + match idiomatic human/repo style), with **Python** as the primary example language. It does **not** inject deliberate bugs, vulnerabilities, or stale dependencies, and it does not silently rewrite code it can't verify.

> Note on honest use: where authorship disclosure is required (for example, academic submissions or assessments), disclosing AI assistance remains your responsibility. This skill is a code-quality and style tool, not a way to misrepresent authorship.

## Version History

- **1.0.0** — Initial release. 22 patterns across comments/docs, naming, structure, error handling, types/formatting/idioms, and audit-only. Behavior contract, style calibration, detection guidance, and a full worked example. Python-focused.

## License

MIT
