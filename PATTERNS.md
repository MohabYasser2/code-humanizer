# Subtractive patterns: the 22 AI tells, with before/after

These are the AI tells the subtractive pass removes. `SKILL.md` carries the one-line summary of
each; this file has the Problem, Before, and After. Read it when you run the subtractive pass.

## Contents

- Comments and documentation: 1 docstrings on trivial functions, 2 redundant comments, 3 section
  banners and Step-N, 4 tutorial-voice, 5 emoji and print narration, 6 placeholder/filler, 7
  what-not-why and uniform density
- Naming: 8 verbose dictionary-style names, 9 generic placeholder names, 10 no short/idiomatic
  locals
- Structure and abstraction: 11 over-engineering, 12 excessive modularity, 13 status-envelope
  returns, 14 eerie uniformity
- Error handling: 15 blanket try/except, 16 redundant defensive checks
- Type, formatting, idiom: 17 useless type hints, 18 appended demo block, 19 markdown in comments,
  20 non-idiomatic verbosity, 21 dead/over-grouped imports
- Audit-only: 22 hallucinated APIs / stale dependencies
- A full worked example

---

## Comments and documentation

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

---

## Naming

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

---

## Structure and abstraction

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

**Fix:** Allow natural, *valid* variation that fits the code, a guard clause here, an inline expression there, a terse name in a tight loop. **During the subtractive pass, do not manufacture fake mess**: no random misindentation, no deliberate typos, no inconsistency for its own sake; that naturalness should emerge as a *side effect* of applying patterns 1-21 well, not by adding noise. Adding human signals deliberately (formatting entropy, commented-out code, idiosyncratic naming) is the separate injection phase, run by auto and additive modes under the safety contract in `HUMAN-SIGNALS.md`. In clean-only mode, injection does not run at all.

---

## Error handling

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

When a real error is possible, catch the *specific* exception you can handle and let the rest propagate. **Flag this as a failure-path change** in your summary (see "The behavior contract" in `SKILL.md`).

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

---

## Type, formatting, and idiom

### 17. Type hints that add no clarity

**Problem:** Annotations on every local and every trivial helper, sometimes `Any`-heavy, in a codebase that isn't otherwise typed.

**Guidance, match the codebase:**
- Fully typed project: **keep and respect the types.**
- Untyped project: trim trivial/`Any` annotations that add noise; keep them at public boundaries if useful.

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

---

## Audit-only (flag, do not silently rewrite)

### 22. Hallucinated APIs and stale dependencies

**Problem:** AI invents plausible methods (`db.fast_query()`), wrong parameters, or pulls in deprecated/abandoned libraries from its training window.

**Fix:** **Do not fabricate a replacement and move on.** Flag any call you can't verify exists, and any library that looks deprecated, as a finding for the user. Verify against installed packages / docs when possible. Humanizing must never paper over a correctness bug.

---

## Full example (clean-only / subtractive)

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

> In auto mode this same input would then go through the injection pass (heavy casual comments,
> commented-out lines, formatting entropy) on top of this clean result. See `HUMAN-SIGNALS.md`.
