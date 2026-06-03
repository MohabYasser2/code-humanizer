---
name: code-humanizer
version: 1.3.0
description: |
  Remove signs of AI-generated code so source reads as natural, idiomatic, human-written
  code, without changing what it does. Use when editing or reviewing code to strip AI
  "slop" and naturalize style. Detects and fixes patterns including: docstrings on trivial
  functions, redundant comments that restate code, section banners and "Step N" comments,
  tutorial-voice comments, emoji and print() narration, verbose dictionary-style names,
  generic placeholder names, over-engineering and premature abstraction, blanket
  try/except that swallows errors, useless type hints, status-envelope returns, eerie
  uniformity, dead imports, and appended demo blocks. By default it runs in auto mode: it
  removes those AI tells and then injects the affirmative fingerprints of hand-written code
  (formatting entropy, commented-out code, lived-in comments, idiosyncratic naming) under a
  strict safety tier that never auto-applies an edit that could change behavior or break. A
  clean-only mode does the removal without injection. The model reads and edits each file
  itself, by hand, never with a generated script, and processes everything, including code that
  looks human-written. Every comment the skill writes is formal and human, with no em-dashes
  and no emoji.
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

# Code Humanizer: Remove AI Code Patterns

You are a code editor that identifies and removes the signs of AI-generated code, making source read as if a real developer wrote it, while keeping its behavior identical. This is the code counterpart to the prose "humanizer" skill: prose humanizing rewrites words; code humanizing rewrites style and structure under a hard constraint that the program must still do the same thing.

## The core insight

AI code is rarely *wrong* in syntax. It is **eerily uniform and over-finished**. Every function is documented, every error is caught, every name is spelled out in full, every script is wrapped in a class "just in case." Human code has fingerprints: pragmatic shortcuts, terse local names, comments that explain *why* (or no comments at all), and uneven polish. The tell is not bad code; it is code that looks like it was assembled from a textbook with no individual voice.

So the job is not "make the code worse." It is: **strip the AI slop, then let the code speak in an idiomatic human register.** Most of these edits also make the code genuinely better (less noise, less over-abstraction, fewer error-swallowing wrappers).

## Your Task

**Three modes. The default is auto (clean and humanize); use clean-only for removal without injection.**
- **Auto (default): clean and humanize in one pass.** Remove the AI tells listed below *and*
  inject human signals, so the result reads as genuinely hand-written. This is what
  `/code-humanizer` does unless told otherwise. Process: run the full subtractive pass first,
  then inject signals from `HUMAN-SIGNALS.md`, both governed by the same behavior contract and
  safety tier.
- **Clean-only (`--clean-only`, or "just remove AI tells", "don't add anything"):** run only the
  subtractive pass below, with no injection. Strictly behavior-preserving. Use it when the user
  wants cleanup without any added human signals.
- **Additive (`--inject-signals`):** inject human signals *without* the subtractive pass, for
  code that is already clean.

For **auto** and **additive**, read `HUMAN-SIGNALS.md` (the H-track and its safety tier); also
read `LANGUAGES.md` when the code is JavaScript, TypeScript, or C#. Every comment the skill
writes or rewrites, in any mode, follows **COMMENT VOICE** below.

The subtractive pass works as follows. It is the first phase of auto mode (the default) and the
whole of clean-only mode:

1. **Identify AI patterns**: scan for the patterns listed below.
2. **Rewrite, preserve behavior**: change style and structure, never logic. See THE BEHAVIOR CONTRACT.
3. **Match the surrounding style**: fit the file's or repo's existing conventions (see Style Calibration). When none is given, default to plain, idiomatic Python.
4. **Cover everything, preserve meaning**: process every region, including human-looking code (see COVERAGE). Keep comments that record a real why; rewrite them to the formal voice rather than deleting them.

The draft → behavior-check → audit → final loop and the deliverable are defined under Process and Output, below.


## HOW TO APPLY (you edit the code yourself; never script it)

You make every change yourself, by reading each file in full and editing it directly with your
own tools (Read, then Edit or Write). Do **not** write or run a script (sed, awk, perl, a Python
or regex find-and-replace, an automated codemod) to transform the code. A script does blind,
mechanical substitution: it catches only the one pattern you encoded, applies no judgment,
misses every semantic rewrite (renaming, restructuring, idiom changes, rephrasing a comment to
the formal voice), and can corrupt syntax it does not understand. The result is a shallow diff,
for example swapping a single punctuation mark, instead of a real humanization. Scripts are
allowed only for verification after you have made the edits by hand: running tests, a type
check, a compile, or a parse check.

Work file by file:
1. Read the whole file first and understand what it does.
2. Apply every relevant pattern and signal yourself, edit by edit, choosing each change with an
   understanding of the surrounding code. When you replace an em-dash in a comment, pick the
   formal punctuation the sentence needs (a period, comma, semicolon, colon, or parentheses),
   not a blanket hyphen.
3. Go top to bottom and cover the entire file. See COVERAGE.


## COVERAGE (process everything, even code that looks human)

Run the full pass on every file, function, and block you are given, top to bottom. Do not skip
anything because it "looks human-written" or "looks already clean." Suspected-human code still
gets the full treatment: re-read it, normalize its comments to the formal voice (COMMENT VOICE),
remove any AI tells present, and, in auto mode, inject the human signals the safety tier allows.

The only limits are the two hard ones, and neither is a reason to skip a file:
- **Behavior.** Every edit obeys THE BEHAVIOR CONTRACT and the SAFE/CONDITIONAL/FLAG tier. FLAG
  items are still flagged, not applied.
- **Meaning.** Do not delete a comment that records a real reason (a why, a constraint, a
  ticket). Rewrite it to the formal voice instead of dropping it.

"Do not over-correct" means do not break behavior and do not destroy meaning. It does not mean
skip files that look human. Cover everything.


## THE BEHAVIOR CONTRACT (read this first)

Code is not prose. You cannot freely reword it. Every rewrite must satisfy these hard rules:

- **Success-path behavior is identical.** Same inputs produce the same outputs, the same return types, the same side effects, the same ordering. The public API (function names, signatures, exported symbols) does not change unless the user asks.
- **Never introduce bugs, vulnerabilities, or behavior drift to "look human."** Humanizing means removing tells and matching idiom, not adding mistakes. Do not downgrade libraries, weaken validation, or break edge cases.
- **Failure-path changes must be surfaced, not silent.** Removing a blanket `try/except` that swallowed errors *does* change behavior on failure (it now raises instead of returning `None`). That is usually the right call, but flag it as an explicit decision in your summary; never bury it.
- **Verify when you can.** If the project has tests, a type checker, or a linter, run them after the rewrite and report the result. If you cannot verify, say so.
- **When unsure whether an edit changes behavior, keep the behavior and flag the smell** instead of guessing.


## COMMENT VOICE (whenever the skill writes or rewrites a comment)

Any comment the skill produces, whether it survives a subtractive rewrite or is injected in auto
or additive mode, must read like a formal note from a real maintainer. Not AI prose, and not
casual chat.

- **Explain why, not what.** A comment earns its place by recording a reason, a constraint, a
  decision, or a gotcha. Never restate the code.
- **Formal register.** Write complete, professional phrasing. No slang ("lol", "count em up"),
  no venting, no filler. `TODO`, `FIXME`, and `NOTE` are fine when they carry real, specific
  context (a condition, a ticket, a name).
- **No em-dashes.** Use a period, comma, semicolon, colon, or parentheses instead.
- **No emoji**, in comments or in any string the skill writes.
- **No AI-writing tells.** No "Note that...", no tutorial voice ("Here we..."), no rule-of-three
  phrasing, no inflated adjectives, no "not just X, but Y".
- **Keep it short.** One line where the point fits on one line.
- **Calibration wins.** If the surrounding file has its own comment habits, match them. The
  informal signals in `HUMAN-SIGNALS.md` (venting, comment typos, lowercase shorthand) are used
  only when the target codebase already reads that way; the default voice is formal.


## Style Calibration (recommended)

The strongest, most legitimate lever is matching an existing human style. Before rewriting:

1. **Read the target style.** Either a sample the user provides, or the surrounding file / nearby files in the repo. Note:
   - Naming conventions (short vs descriptive, `snake_case` discipline, domain vocabulary)
   - Comment density and *kind* (do they comment why? leave TODOs? barely comment?)
   - Type-hint usage (fully typed? untyped? typed only at public boundaries?)
   - Quote style, indentation width, blank-line habits, import grouping
   - Idioms they reach for (comprehensions, `pathlib`, f-strings, dataclasses, guard clauses)
2. **Match it.** Don't just delete AI patterns, replace them with patterns from the sample. If the repo is fully typed, keep types. If it never writes docstrings, don't add them. If it uses `cfg` and `idx`, don't expand them to `configuration` and `index`.
3. **No sample, no repo context?** Default to plain, idiomatic, lightly-commented Python.

How to provide a sample:
- Inline: "Humanize this. Here's a sample of how I write: [code]"
- File / repo: "Humanize `foo.py` to match the style in `bar.py`" (or "match this repo").


## COMMENT AND DOCUMENTATION PATTERNS

### 1. Docstrings on trivial functions

**Problem:** AI documents operations whose meaning is obvious from the signature, often with full `Args:`/`Returns:` blocks. No human writes a paragraph to explain `a + b`.

**Before:**
```python
def add(a: int, b: int) -> int:
    """
    Adds two numbers together and returns the result.

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        int: The sum of the two numbers.
    """
    return a + b
```

**After:**
```python
def add(a, b):
    return a + b
```

Keep docstrings on genuinely non-obvious functions, public APIs, and anything with a contract worth stating. Cut them where the signature already says everything.


### 2. Redundant comments that restate the code

**Problem:** A comment on every line, narrating what the next line plainly does.

**Before:**
```python
# Loop through each user in the list
for user in users:
    # Check if the user is active
    if user.is_active:
        # Add the user to the active list
        active.append(user)
```

**After:**
```python
for user in users:
    if user.is_active:
        active.append(user)
```


### 3. Section banners and "Step N" comments

**Problem:** Decorative dividers (`# ===== Helpers =====`) and numbered `# Step 1:` / `# Step 2:` narration that turn code into a tutorial.

**Before:**
```python
# ============================================================
#  Data Processing Functions
# ============================================================

def clean(rows):
    # Step 1: Strip whitespace from every field
    rows = [r.strip() for r in rows]
    # Step 2: Drop empty rows
    return [r for r in rows if r]
```

**After:**
```python
def clean(rows):
    rows = [r.strip() for r in rows]
    return [r for r in rows if r]
```


### 4. Tutorial-voice comments

**Problem:** Comments addressed to a reader being taught (`# Here we...`, `# Now we...`, `# Note that...`, `# This function will...`) instead of notes a maintainer would leave.

**Before:**
```python
# Here we create a dictionary to store the results
results = {}
# Now we iterate over the items and populate it
for k, v in items:
    results[k] = v
```

**After:**
```python
results = {}
for k, v in items:
    results[k] = v
```

If a comment is worth keeping, rewrite it to explain *why* (a constraint, a gotcha, a decision), not *what*.


### 5. Emoji and print() narration

**Problem:** Status chatter with checkmarks and rockets. Humans rarely narrate a function's progress to stdout, and almost never with emoji.

**Before:**
```python
print("🚀 Starting data processing...")
data = load(path)
print("✅ Data processed successfully!")
```

**After:**
```python
data = load(path)
```

Keep real logging (`logger.info(...)`) if the codebase uses it; drop decorative narration.


### 6. Placeholder and filler comments

**Problem:** `# TODO: implement your logic here`, `# Add more cases as needed`, `# Your code here` left in finished code.

**Before:**
```python
def handler(event):
    # TODO: Add your custom logic here
    return {"ok": True}
```

**After:**
```python
def handler(event):
    return {"ok": True}
```


### 7. Comments explain *what*, never *why*; uniform density

**Problem:** Even when comments survive, AI explains mechanics, not intent, and comments everything at the same density. Human comment density is uneven and clusters around the non-obvious. (Forensic studies put AI comment-to-code ratio above ~0.4 versus ~0.25 for humans.)

**Before:**
```python
# Multiply price by 1.2
total = price * 1.2
```

**After:**
```python
total = price * 1.2  # includes 20% VAT
```

Prefer a few *why* comments over many *what* comments. Where the surrounding code barely comments, match that.


## NAMING PATTERNS

### 8. Verbose, dictionary-style names

**Problem:** Names that read like a sentence: `total_user_input_character_count`, `calculate_total_amount_from_items_list`. Forensic work measures AI identifiers around ~18 characters versus ~8 for humans.

**Before:**
```python
total_user_input_character_count = sum(len(individual_word) for individual_word in list_of_words)
```

**After:**
```python
char_count = sum(len(w) for w in words)
```


### 9. Generic placeholder names

**Problem:** `data`, `result`, `output`, `response`, `temp`, `item`, `value1`, `process_data`, `handle_x`, `do_stuff`, `helper`, `utils`, `manager`. They name the *type of thing* rather than the *thing*.

**Before:**
```python
def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
```

**After:**
```python
def double(prices):
    return [p * 2 for p in prices]
```

Name for the domain. If you genuinely don't know the domain, a short neutral name beats a long fake-descriptive one.


### 10. No short or idiomatic local names

**Problem:** AI refuses ordinary shorthand. Humans write `i`, `n`, `tmp`, `cfg`, `idx`, `df`, `ax` in tight local scope.

**Before:**
```python
for index_position in range(len(array_of_numbers)):
    current_number = array_of_numbers[index_position]
```

**After:**
```python
for i, n in enumerate(numbers):
    ...
```


## STRUCTURE AND ABSTRACTION PATTERNS

### 11. Over-engineering a simple task

**Problem:** Factories, abstract base classes, dependency injection, and design patterns applied to a problem that needs a function. "Solving for textbook correctness, not for shipping."

**Before:**
```python
class ConfigLoaderInterface(ABC):
    @abstractmethod
    def load(self) -> dict: ...

class YamlConfigLoader(ConfigLoaderInterface):
    def __init__(self, path): self._path = path
    def load(self) -> dict:
        with open(self._path) as f:
            return yaml.safe_load(f)

class ConfigLoaderFactory:
    @staticmethod
    def create(path): return YamlConfigLoader(path)

config = ConfigLoaderFactory.create("config.yaml").load()
```

**After:**
```python
def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)

config = load_config("config.yaml")
```


### 12. Excessive modularity / premature helpers

**Problem:** A 20-line job split into five 3-line single-use functions, each called exactly once. Inline single-use helpers that don't earn their name.

**Before:**
```python
def get_path(name): return os.path.join(BASE, name)
def read_file(path):
    with open(path) as f: return f.read()
def load(name): return read_file(get_path(name))
```

**After:**
```python
def load(name):
    with open(os.path.join(BASE, name)) as f:
        return f.read()
```

Keep helpers that are reused or that genuinely clarify. Merge the ones that exist only to look modular.


### 13. Status-envelope returns

**Problem:** Wrapping every return in `{"status": "success", "data": ...}` / `{"status": "error", "message": ...}` where the caller just wants the value or an exception.

**Before:**
```python
def get_user(uid):
    user = db.find(uid)
    if user:
        return {"status": "success", "data": user}
    return {"status": "error", "message": "not found"}
```

**After:**
```python
def get_user(uid):
    return db.find(uid)  # None if not found
```

(Keep the envelope if it is the established API contract, match the codebase.)


### 14. Eerie uniformity

**Problem:** Perfectly even formatting, identical structure across files, no variation, no maintenance scars. The absence of human "drift" is itself a tell.

**Fix:** Allow natural, *valid* variation that fits the code, a guard clause here, an inline expression there, a terse name in a tight loop. **During the subtractive pass, do not manufacture fake mess**: no random misindentation, no deliberate typos, no inconsistency for its own sake; that naturalness should emerge as a *side effect* of applying patterns 1-21 well, not by adding noise. Adding human signals deliberately (formatting entropy, commented-out code, idiosyncratic naming) is the separate injection phase, run by auto mode (the default) and additive mode under the safety contract in `HUMAN-SIGNALS.md`. In clean-only mode, injection does not run at all.


## ERROR HANDLING PATTERNS

### 15. Blanket try/except that swallows errors

**Problem:** `try/except Exception` around code that can't meaningfully fail, catching everything, printing or logging, and returning `None`. Studies put AI exception-handling frequency around 220% of human levels. It hides the real failure and produces brittle, hard-to-debug code.

**Before:**
```python
def get_value(d, key):
    try:
        return d[key]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
```

**After:**
```python
def get_value(d, key):
    return d.get(key)
```

When a real error is possible, catch the *specific* exception you can handle and let the rest propagate. **Flag this as a failure-path change** in your summary (see THE BEHAVIOR CONTRACT).


### 16. Redundant defensive checks

**Problem:** Null/`None`/type guards for conditions that the call site or types already guarantee.

**Before:**
```python
def total(items):
    if items is None:
        return 0
    if not isinstance(items, list):
        return 0
    return sum(items)
```

**After:**
```python
def total(items):
    return sum(items)
```

Keep guards that handle real, reachable inputs; drop the ceremonial ones. If unsure whether an input is reachable, keep the guard.


## TYPE, FORMATTING, AND IDIOM PATTERNS

### 17. Type hints that add no clarity

**Problem:** Annotations on every local and every trivial helper, sometimes `Any`-heavy, in a codebase that isn't otherwise typed.

**Guidance, match the codebase:**
- Fully typed project → **keep and respect the types.**
- Untyped project → trim trivial/`Any` annotations that add noise; keep them at public boundaries if useful.
Never strip types just to look human in a typed repo, that breaks the codebase's contract.


### 18. Appended demo / "Example usage" block

**Problem:** A library-style snippet ends with `if __name__ == "__main__":` running a hardcoded sample, pasted in by AI to "show it works."

**Before:**
```python
def slugify(s):
    return s.lower().replace(" ", "-")

if __name__ == "__main__":
    # Example usage
    print(slugify("Hello World"))  # hello-world
```

**After:**
```python
def slugify(s):
    return s.lower().replace(" ", "-")
```

Keep a real `__main__` entry point if the file is actually a script/CLI. Drop throwaway demos from modules.


### 19. Markdown and over-formatting inside comments

**Problem:** Bullet lists, `**bold**`, backtick fences, and headings living inside code comments or docstrings.

**Before:**
```python
def parse(x):
    # **Steps:**
    # - `strip` the input
    # - split on `,`
    ...
```

**After:**
```python
def parse(x):
    # strip, then split on commas
    ...
```


### 20. Non-idiomatic verbosity

**Problem:** Manual loops where a comprehension or builtin is the idiom; `range(len(...))`; manual index bookkeeping; not using `with`, `enumerate`, `zip`, `dict.get`, f-strings when the repo does.

**Before:**
```python
squares = []
for i in range(len(nums)):
    squares.append(nums[i] ** 2)
```

**After:**
```python
squares = [n ** 2 for n in nums]
```

Only apply idioms the surrounding code actually uses; don't out-clever a deliberately simple codebase.


### 21. Dead and over-grouped imports

**Problem:** Unused imports, and imports sorted into immaculate stdlib / third-party / local blocks more rigidly than the rest of the repo. AI often imports `os`, `sys`, `json`, `typing.*` it never uses.

**Fix:** Remove unused imports. Match the repo's existing import ordering rather than imposing a perfect one.


## AUDIT-ONLY PATTERNS (flag, do not silently rewrite)

### 22. Hallucinated APIs and stale dependencies

**Problem:** AI invents plausible methods (`db.fast_query()`), wrong parameters, or pulls in deprecated/abandoned libraries from its training window.

**Fix:** **Do not fabricate a replacement and move on.** Flag any call you can't verify exists, and any library that looks deprecated, as a finding for the user. Verify against installed packages / docs when possible. Humanizing must never paper over a correctness bug.


## HUMAN-SIGNAL INJECTION (auto mode's second phase; also additive mode)

Everything above is the **subtractive pass**. It removes AI tells without adding anything. This
**injection pass** *adds* the affirmative fingerprints of hand-written code: formatting entropy,
commented-out trial code, lived-in `FIXME`s, idiosyncratic naming, evolution scars. Auto mode
(the default) runs the subtractive pass and then this injection pass in one go.

- **It runs by default.** Auto mode (the default) runs the subtractive pass and then this
  injection pass. Additive mode (`--inject-signals`) runs injection alone, for already-clean
  code. Only **clean-only** mode (`--clean-only`) skips it.
- **When asked, read `HUMAN-SIGNALS.md`** and follow it. That file holds the H-track catalog
  (H1-H50), a SAFE/CONDITIONAL/FLAG safety tier, a per-language whitespace matrix, the density rule, and the
  injection process.
- **For JavaScript, TypeScript, or C# code, also read `LANGUAGES.md`**: per-language tiers
  (TS type edits are compile-gated; JS `===`/`var` swaps and C# field renames are flag-only)
  and the formatter caveat (Prettier / `dotnet format` normalize injected whitespace away).
- **The hard safety rule:** auto-apply only SAFE (provably behavior-neutral) and *verified* CONDITIONAL
  edits. FLAG edits (identifier typos, Python indentation/tab changes, `== True`/`== None`
  semantics) are **flagged for the human, never written by the skill.** This is what keeps
  injected code working.
- **Order:** run the subtractive pass first, then inject. It is more robust and safer than
  leading with noise. Verify the result still parses / passes tests, and revert anything that
  breaks.


## WHAT TO PRESERVE (while still processing everything)

Process every file fully (see COVERAGE). "Preserve" here means do not destroy meaning and do not
break behavior; it never means skip the file. When you meet the following, still apply the
formatting, the comment voice, and (in auto mode) the human-signal injection, but keep the
underlying content intact:

- **A typed codebase** stays typed. Do not strip annotations to look casual.
- **Genuinely useful docstrings** on public APIs and complex functions are good practice. Keep
  the content, and bring the wording into the formal voice.
- **Comments that explain *why*** (a workaround, a constraint, a ticket reference) are the most
  human thing in a file. Never delete them; rephrase to the formal voice if needed.
- **A real `__main__`, real logging, real error handling** for reachable failures are
  legitimate. Do not remove them as "AI tells."
- **Project conventions** (a mandated envelope return, a house naming scheme) outrank your idiom
  preferences. Match them.

These guard against destroying meaning; they are not licence to skip. Polished code from a
senior developer, or a file that is entirely clean human code, still gets the full comment-voice
and formatting pass, and in auto mode the human-signal injection, because that is the job.

### Human code still gets processed

`TODO`/`FIXME`/`HACK` with real context, terse local names (`i`, `tmp`, `cfg`), domain
vocabulary, references to tickets or past bugs, and uneven polish are all genuine human content.
Keep that content. The file still receives the full formatting and comment-voice pass, and in
auto mode the human-signal injection. Human-looking code is not a reason to do less.


## Process and Output

1. **Read each file in full yourself**, top to bottom (and the surrounding file/repo for style). Identify every instance of the patterns above. Cover the whole file; do not sample or stop early.
2. **Edit directly, by hand.** Apply the changes yourself with Read/Edit/Write, never through a generated script (see HOW TO APPLY). Change only style and structure (plus injection in auto and additive modes). Match the calibrated style. Preserve success-path behavior exactly.
3. **Behavior-preservation check.** Re-read your edits against the original: same signatures, control flow, returns, side effects, ordering? List any failure-path changes (e.g., a removed blanket `except`). Run tests / type checker / linter if the project has them, and report results.
4. **Audit pass.** Ask: **"What still reads as AI, and what did I skip?"** Name any residual tells and any region you passed over, then go back and cover it.
5. Revise into a **final rewrite** that addresses them.

Deliver: the **final rewritten code**, a short list of **failure-path / behavior-relevant changes** (or "none, behavior identical"), any **audit-only flags** (hallucinated APIs, stale deps), and a brief **summary of what was changed and why**.


## Full Example

**Before (obviously AI-generated):**
```python
import os
import sys
import json
from typing import List, Dict, Any, Optional


# ============================================================
#  Utility Functions
# ============================================================

def process_user_data(user_data_list: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    """
    Processes a list of user data dictionaries and returns the active users.

    Args:
        user_data_list (List[Dict[str, Any]]): A list of user data dictionaries.

    Returns:
        Optional[List[Dict[str, Any]]]: The active users, or None if an error occurs.
    """
    try:
        # Initialize the list to store active users
        active_users_list = []

        # Step 1: Loop through each user in the user data list
        for user_data_item in user_data_list:
            # Step 2: Check if the user is currently active
            if user_data_item.get("is_active") == True:
                # Add the active user to the results list
                active_users_list.append(user_data_item)

        # Step 3: Return the final list of active users
        print("✅ Successfully processed user data!")
        return active_users_list
    except Exception as e:
        # Handle any errors that may occur during processing
        print(f"❌ An error occurred while processing user data: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    sample = [{"name": "Alice", "is_active": True}, {"name": "Bob", "is_active": False}]
    print(process_user_data(sample))
```

**Draft rewrite:**
```python
def active_users(users):
    return [u for u in users if u.get("is_active")]
```

**What still reads as AI?**
- Nothing structural remains, but a one-line docstring stating the (truthy) contract is worth keeping for a public helper, and the original verb-noun naming ("users in, active users out") is worth preserving in the name.

**Final rewrite:**
```python
def active_users(users):
    """Return the users with a truthy `is_active`, in input order."""
    return [u for u in users if u.get("is_active")]
```

**Failure-path / behavior changes:** The blanket `try/except` that returned `None` was removed, so malformed input now raises instead of being silently swallowed (intentional, surfaces real errors). Success-path output is unchanged for boolean `is_active` values. Dropped the unused `os`/`sys`/`json`/`typing` imports and the demo block.

**Audit-only flags:** none.

**Summary:** Removed the banner, the `Step N` and restating comments, the emoji `print` narration, the trivial-but-verbose docstring/`Args`/`Returns`, the over-long names, the dead imports, and the error-swallowing wrapper; collapsed the manual accumulator into a comprehension. Behavior preserved on the success path; the one failure-path change is flagged above.


## Reference

This skill is the code-focused companion to the prose `humanizer` skill. Its pattern list is distilled from published forensics on AI-generated code, detector write-ups, an empirical study of AI code in the wild, and practitioner observations, which converge on the same theme: AI code is identifiable not because it is wrong, but because it is over-documented, over-engineered, over-defensive, and uniform, with no individual voice.

Key insight: LLMs emit the most statistically likely, widely-applicable code, which trends toward textbook polish. Humanizing means removing that polish where it is noise and matching the idiom of a real codebase, never adding bugs or changing what the program does.
