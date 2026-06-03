# Human-Signal Injection (auto mode's second phase, and additive mode)

This is the **additive** half of Code Humanizer. The subtractive pass (the 22 patterns,
summarized in `SKILL.md` and detailed in `PATTERNS.md`) *removes* AI tells. This track *adds* the
affirmative fingerprints of human authorship: formatting entropy, lived-in comments, idiosyncratic
naming, evolution scars.

**This track runs by default.** Auto mode (the default for `/code-humanizer`) removes AI tells
first, then injects these signals. Additive mode (`--inject-signals`) injects without the
subtractive pass, for code that is already clean. Only **clean-only** mode (`--clean-only`, or
"just remove AI tells") skips this track.

The research basis: *Whitespaces Don't Lie* (arXiv 2601.19264) found human code shows
**15-40% higher variance in formatting metrics across identical implementations**,
*"humans create intentional inconsistency; AI generates unintentional uniformity."*
Whitespace and indentation were the single most discriminative cues. So the objective is
**add variance, not add mess**, and variance that doesn't compile is worthless.

---

## Contents

- **THE INJECTION CONTRACT**: the SAFE/CONDITIONAL/FLAG safety tier, the verify step, and the
  complete-reference rename checklist.
- **LANGUAGE BRANCH**: which whitespace edits are safe per language (Python indentation is FLAG).
- **THE CATALOG (H1-H50)**: whitespace entropy, comments, typos, naming chaos, structural scars,
  import habits, legacy idioms, repo-level.
- **INJECTION VOLUME**: inject heavily, but not uniformly.
- **PROCESS**: the per-file injection steps.
- **WORKED EXAMPLES**: brace language and Python.
- **Honest use.**

## THE INJECTION CONTRACT (read this first)

The subtractive behavior contract still holds: **the program must behave identically on the
success path.** Injection makes that *harder*, not easier, so it is governed by a strict
safety tier. Every signal below is tagged:

- **SAFE**: provably behavior-neutral. Touches only comments, blank lines, and whitespace
  in languages where whitespace is non-syntactic, or the inside of string literals that are
  not keys/paths/format-sensitive. **May be auto-applied.**
- **CONDITIONAL**: behavior-neutral *only if* applied completely and in a compatible
  language (e.g. a rename touching every reference, an idiom swap that is semantically equal
  for this type). **Apply only after verifying the precondition; otherwise treat as FLAG.**
- **FLAG**: can change behavior or fail to compile (identifier typos, Python
  indentation/tab changes, `== True`/`== None` semantics, dropping a guard). **Never
  auto-apply. Emit these as a numbered suggestion list for the human to apply by hand.**

> **The hard rule that keeps code working:** the skill auto-edits SAFE and *verified* CONDITIONAL only.
> FLAG is reported, never written. If you cannot prove a CONDITIONAL edit is total and safe, demote it
> to FLAG and flag it. When unsure, flag, don't guess.

After injecting, **verify**: re-run the project's tests / type checker / linter if present,
or at minimum confirm the file still parses (`python -c "import ast,sys; ast.parse(open(f).read())"`
for Python, a compile for brace languages). Report the result. If it no longer parses, revert.

### Verifying a CONDITIONAL rename: the complete-reference rule

Renames (H27-H31) are the most common CONDITIONAL edit and the easiest to get wrong: a rename is
behavior-neutral **only if every reference moves and nothing binds the old name by string or
reflection.** A half-done rename is a `NameError`/compile error or, worse, a silent bug. Before
applying any rename, run this checklist, if you can't complete it with confidence, **demote to
FLAG and flag it, don't rename:**

1. **Enumerate every reference, don't eyeball.** Grep the exact symbol across its scope: the
   whole file for a local, the whole project for an exported/public symbol. Count them.
2. **Rename all of them in one edit:** the definition, every use, keyword/named/default
   arguments, and the name inside doc comments (Python docstring params, C#/JS XML/JSDoc
   `<param name="...">` / `@param`).
3. **Check for name-based binding that an identifier grep misses**. These don't move with a
   rename and silently break:
   - **String/dynamic access:** `obj["old"]`, `getattr`/`hasattr`, JS bracket access,
     reflection (`GetProperty("old")`, `nameof` was-string copies).
   - **Serialization / config keys:** JSON field names, `[JsonProperty("old")]` /
     `[JsonPropertyName("old")]`, any attribute or config that binds by string name.
   - **Public API / overrides / interface members:** renaming breaks callers, an `override`
     contract, or an interface implementation.
   - **Shadowing / collision:** make sure the new name doesn't already exist in scope (the
     classic C# case: removing `this.` after a rename rebinds to a parameter).
4. **Compile/parse-check** with the language's tool (`tsc --noEmit`, `node --check`,
   `dotnet build`, `python -c ast.parse`). If anything fails, revert the rename.
5. **Scope discipline:** only rename **locals and single-file private symbols** as CONDITIONAL. A
   field, property, public method, or exported symbol is **FLAG, flag, never auto-rename**,
   because step 3's surface is too large to clear by inspection.

The same rule covers any CONDITIONAL that depends on completeness (e.g. a file rename, H50): incomplete =
broken, so verify totality or demote to FLAG.

---

## LANGUAGE BRANCH (do this before any whitespace edit)

Whitespace safety is **language-dependent**. The same edit is free in C and fatal in Python.

| Signal class | Python | C / C++ / Java / **C#** / JS / TS | Go |
|---|---|---|---|
| Operator spacing `a=b` vs `a = b` | SAFE (PEP8 warn, runs) | SAFE | SAFE (gofmt reverts on save) |
| Space before `;` / inside `( )` | n/a | SAFE | SAFE |
| Indent **width** change (2↔4) | FLAG **IndentationError** | SAFE | SAFE (tabs) |
| Mixed tabs/spaces | FLAG **TabError** | SAFE | FLAG (tabs required) |
| Brace style `if(x){` vs `if (x) {` | n/a | SAFE | SAFE→gofmt |
| Blank lines / trailing whitespace | SAFE | SAFE | SAFE→gofmt |
| `#`/`//` comment spacing | SAFE | SAFE | SAFE |

**Rule:** in Python, *never* touch leading indentation or tabs (FLAG). All Python whitespace
entropy must come from operator spacing, blank lines, trailing whitespace, comment spacing,
and inline alignment, never the indent column. In brace languages, formatting is almost all
SAFE because the compiler ignores it.

> The headline example `int x=y ;` (space before semicolon, no spaces around `=`) is a
> brace-language signal, SAFE in C/C++/Java/C#/JS/TS, not applicable in Python.

**For JavaScript, TypeScript, and C#, read `LANGUAGES.md`** before applying any whitespace,
type, equality, or idiom signal. It has the per-language tiers (TS type edits are compile-gated
CONDITIONAL; JS `===`→`==` and `let`→`var` are FLAG; C# `var`↔explicit and `#region` are SAFE) and the
**formatter caveat**: if Prettier / `dotnet format` / EditorConfig runs on save or in CI,
whitespace injection is normalized away, lean on comments, naming, and idioms instead.

---

## THE CATALOG (H-track)

Grouped for reference. Inject heavily and unevenly across the file, see INJECTION VOLUME below.

### Whitespace & formatting entropy

| ID | Signal | Example | Tier |
|----|--------|---------|------|
| H1 | Inconsistent operator spacing | `x=y` here, `x = y` there | SAFE brace · SAFE Py |
| H2 | Space before `;` / inside parens | `int x = y ;` · `foo(a ,b)` | SAFE brace |
| H3 | Trailing whitespace on some lines | (invisible; detectors measure it) | SAFE |
| H4 | Irregular blank lines | 3 blanks, then 0 between the next pair | SAFE |
| H5 | Inconsistent indent **width** | 4 spaces here, 2 there | SAFE brace · FLAG **Py** |
| H6 | Mixed tabs/spaces | | SAFE some · FLAG **Py/Go** |
| H7 | Variable line length | 30-char lines next to 140-char ones | SAFE |
| H8 | Align `=` in one block, abandon in next | | SAFE |
| H9 | Mixed quote style | `'foo'` and `"bar"` for no reason | SAFE (watch escaping) |
| H10 | Mixed brace/keyword spacing | `if(x)` and `if (x)` in one file | SAFE brace |
| H11 | No-space-after-`#`/`//` (about 50% of all comments) | `#like this` and `# like this`, roughly half each | SAFE |

### Comments: the human kind (AI strips these; their presence is the strongest tell)

| ID | Signal | Example | Tier |
|----|--------|---------|------|
| H12 | **Commented-out code left in** | `# old_lr = 3e-4` · `// for(i..) print(i)` | SAFE |
| H13 | Debug prints | `print("here")` `print("aaaa")` · commented `# breakpoint()` | SAFE commented · CONDITIONAL live (adds a side effect) |
| H14 | TODO/FIXME/HACK/XXX with real context | `# FIXME: breaks on empty input, ask Omar` | SAFE |
| H15 | Stale comment that contradicts the code | comment says "0=stay" but `0` means up | SAFE |
| H16 | Casual aside / working note | `# this was slower somehow, kept the loop` · `# dont touch, breaks otherwise` | SAFE |
| H17 | Dated / signed scribbles | `# 12/03 hack, revisit` · `# -MY` | SAFE |
| H18 | Native-language comment | a non-English line mid-file | SAFE |
| H19 | Pragmatic suppressions | `# noqa` `# type: ignore` `# pylint: disable=...` | CONDITIONAL (must be a real, valid pragma) |
| H20 | External references | `# from stackoverflow.com/q/...` · ticket #, a name | SAFE |
| H21 | Half-finished thought | `# need to handle the case where` (stops) | SAFE |

### Spelling, typos, grammar

| ID | Signal | Example | Tier |
|----|--------|---------|------|
| H22 | Typos in **comments / log strings** | `recieve`, `seperate`, `occured`, `lenght` | SAFE (encouraged) |
| H23 | Typos in **identifiers** | `recieved_data`, `widht` used everywhere | **FLAG** (one missed ref = `NameError`) |
| H24 | British/American mix | `colour`/`color` in comments | SAFE comment · FLAG identifier |
| H25 | Non-native / loose grammar in comments | "this make the thing for calc" | SAFE |
| H26 | Inconsistent message capitalization | `"Error:"` vs `"error :"` | SAFE (watch exact-match consumers) |

> **The injected comment voice is casual, and the casual signals are encouraged.** H16 (asides
> and working notes), H22 (the odd comment typo), and H25 (loose grammar) are part of the default
> voice, not calibration-only. Inject plenty of them. Follow the "Comment voice" section in `SKILL.md`:
> casual, human, lots of comments, no em-dashes, no emoji. Auto mode uses the same voice.

### Naming chaos

| ID | Signal | Example | Tier |
|----|--------|---------|------|
| H27 | Mixed conventions in one file | `camelCase` next to `snake_case` | CONDITIONAL (rename all refs) |
| H28 | Numbered / lazy locals | `tmp`, `tmp2`, `data2`, `final`, `real_final` | CONDITIONAL |
| H29 | Copy-paste residue | `df_copy`, `user2`, `result_old` | CONDITIONAL |
| H30 | Idiosyncratic abbreviations | `val`, `cfg`, `idx`, `n`, `foo` | CONDITIONAL |
| H31 | Inconsistent plurality | `user` holds a list; `items` holds one | CONDITIONAL |

### Structural / pragmatic scars

| ID | Signal | Example | Tier |
|----|--------|---------|------|
| H32 | Copy-paste duplication (WET) | same 6 lines pasted 3× instead of a loop | SAFE (more code, same behavior) |
| H33 | Magic number inline | `if speed > 0.47:` no named constant | SAFE |
| H34 | Hardcoded personal path | `C:\Users\mohab\...` `/home/omar/` | SAFE (never inject real secrets) |
| H35 | One oversized function (don't split) | 150-line `main()` | SAFE (leave as-is) |
| H36 | Dead / unreachable branch | `if False:` block, code after `return` | CONDITIONAL (must stay unreachable) |
| H37 | `i = i + 1` instead of `i += 1` (mixed) | | SAFE |
| H38 | Leftover debug scaffolding | `t0 = time.time()` timing, `import pdb` | CONDITIONAL (side effects/imports) |
| H39 | Inconsistent error handling | careful `try` here, none there | CONDITIONAL |
| H40 | "Temporary" hack made permanent | `time.sleep(2)  # why does this fix it??` | FLAG (sleep changes timing) |

### Import habits

| ID | Signal | Example | Tier |
|----|--------|---------|------|
| H41 | Import added mid-file at point of use | `import os` on line 80 | SAFE |
| H42 | Unused import left after a refactor | imported `json`, never used | SAFE |
| H43 | Chronological (not alphabetical) order | order they were needed | SAFE |
| H44 | Commented-out import | `# import seaborn as sns` | SAFE |

### Legacy / non-idiomatic syntax

| ID | Signal | Example | Tier |
|----|--------|---------|------|
| H45 | `== True` / `== None` | `if active == True:` `if x == None:` | **FLAG**: semantics differ for numpy/None |
| H46 | `range(len(x))` instead of `enumerate` | | SAFE |
| H47 | `len(x) == 0` instead of `not x` | | CONDITIONAL (differs for numpy/pandas) |
| H48 | Redundant parens | `return (x)` `if (a and b):` | SAFE |
| H49 | `+` concat instead of f-string (mixed) | `"hi " + name` and `f"hi {name}"` | SAFE |

### Repo level (multi-file)

| ID | Signal | Example | Tier |
|----|--------|---------|------|
| H50 | Human file names | `test2.py`, `Copy of x`, `final_v3.py`, `.bak` | CONDITIONAL (update imports if renaming a module) |

---

## INJECTION VOLUME (inject heavily, but not uniformly)

Inject **as much as the file can carry**. By default apply most of the signal types below across
the whole file: casual comments, commented-out old or alternative lines, commented-out debug
prints, whitespace entropy on the large majority of lines, idiom swaps, casual naming, and the
rest. The bar is high: **at least 80% of the lines in a file should be altered** with some human
mark (the whitespace rule below is how you reach that). A real, lived-in file that never saw a
formatter is dense with these; aim well past a token few.

The one constraint is that the injection must not be *mechanically uniform*, because a uniform
layer of noise is its own detectable pattern. Heavy and uneven, not light:

1. **Use most of the catalog, heavily.** Reach across the whole H-track for each file, not 5 of
   50. Add many casual comments and several commented-out lines wherever they fit.
2. **Vary density by region, do not go sparse.** Some functions get a heavy dusting of comments
   and scars, others fewer, but nothing is left looking machine-clean. Uneven means the *amount*
   varies, not that most of the file stays untouched.
3. **Spread the kinds around.** Do not repeat the same one transform on a fixed interval; mix
   comments, commented-out lines, spacing, and idiom changes so no single pattern recurs.
4. **Add lines, do not only edit them.** Inject new commented-out alternatives, commented-out
   debug prints, extra blank lines, and short asides. Adding lived-in lines is part of the job.
5. **Match plausibility.** A misspelling a real dev makes (`recieve`) beats a random one
   (`receeeive`). A casual aside fits hard code better than a one-line helper.

The only ceilings are the safety tier (every edit stays SAFE or verified CONDITIONAL; FLAG items
are still flagged, not applied) and basic readability (do not turn the file into unreadable
garbage). Within those, inject heavily; under-injection is the failure mode, not over-injection.

### Whitespace and `#` spacing (the phase-2 script does this)

Whitespace entropy is the single most discriminative cue (per the research) and it is purely
mechanical, so the **phase-2 script** lays it down, not by hand: run
`python scripts/whitespace_entropy.py FILE --rate 0.7`. It varies inline spacing, the `#`/`//`
split, and occasional blank lines (`--blank-rate`, the H4 random-blank-lines signal) on about half
the lines, and verifies its own output to prove no code token changed. The rules
below are what that script applies; it now covers Python and the brace family (JS, TS, C#, C/C++,
Java), so hand-apply only for a language it does not handle. Most
lines have room (an `=`, an operator, a comma, a call, a bracket); only `pass`, a bare `)`, or a
decorator have none. Mix the kind so it is not one repeated transform:

- spacing around `=` and operators: `x=y`, `x =y`, `x= y`, `x = y`
- spaces after or before commas: `f(a,b)`, `f(a, b)`, `f(a ,b)`, `f(a , b)`
- spaces inside parens and brackets: `f( x )`, `arr[ 0 ]`, `f(x)`
- a trailing space on some lines (invisible to read, but detectors measure it)
- the odd extra or missing blank line between statements

**The `#` / `//` space, roughly 50/50.** Hand-written code is split between `# comment` and
`#comment`; AI puts a space after the hash every single time, so an all-spaced file is a tell.
Drop the space after the hash on **about half of all comments, the ones already in the file and
the ones you inject**, and the same for `//` in brace languages. Vary which ones get it.

**Python safety, do not break the file:** vary only *inline* whitespace. **Never change the
leading indentation or tabs on a line.** Indentation is syntactic in Python; touching it is FLAG
and raises `IndentationError`. All Python whitespace entropy comes from inside the line, never the
indent column. In brace languages (C/C++/Java/C#/JS/TS) indent width, braces, and space before
`;` are also fair game.

Do not collapse it into one uniform pattern (every `=` tight, say). The point is that the spacing
is *inconsistent* line to line, the way someone who never ran a formatter writes. If a formatter
is configured (black, Prettier, gofmt, `dotnet format`), this entropy is erased on the next run,
so skip it there and lean on comments and idioms instead (see `LANGUAGES.md`).

### Comment typos and punctuation: about 1 in 4 comments

Roughly **one in every four comments** should carry a small human error. These are SAFE because
they live in comment text and log strings, never in identifiers (an identifier typo is FLAG; it
breaks references). Rotate the kinds so they do not repeat:

- a plausible misspelling: `recieve`, `seperate`, `occured`, `lenght`, `shouldnt`, `dont`, `wich`,
  `arguement`, `successfull`, `paramter`. Use words a real dev actually fat-fingers, not random
  garble (`recieve` beats `receeeive`).
- punctuation a hurried dev mistypes: a space before a comma (`# strip , then split`), a missing
  space after one (`# fast,but rough`), a double space, a dropped apostrophe (`dont`, `wont`).
- loose grammar or a dropped word (`# this make the thing`), or lowercase where a capital belongs.

Keep it near a quarter, not all of them; a file where every comment is misspelled reads fake.
Vary which comments get hit, and never typo an identifier, a string key, a path, or a format
specifier.

---

## PROCESS

Make every edit by hand (Read, then Edit/Write); never script the transformation. See **HOW TO
APPLY** in `SKILL.md`.

1. **Confirm the mode.** This track runs in auto mode (the default) and additive mode; skip it only in clean-only mode.
2. **Branch on language.** Build the safe set from the LANGUAGE BRANCH table. In Python, drop
   all indentation/tab signals to FLAG.
3. **(Recommended) Run the subtractive pass first.** Remove AI tells (SKILL.md 1-22), *then*
   inject. Subtract-then-inject is more robust and safer than leading with typos.
4. **Inject heavily and unevenly** per INJECTION VOLUME (most of the catalog, many comments and commented-out lines).
5. **Apply SAFE and verified CONDITIONAL edits only.** Collect every FLAG as a suggestion list.
6. **Verify** it still parses / tests still pass. Revert anything that breaks.
7. **Deliver:** the rewritten code, the list of signals injected (with IDs), the **FLAG-tier
   suggestions the human must apply manually**, the verification result, and a one-line note
   that injection is style work, not a behavior change.

---

## WORKED EXAMPLE: brace language (lots of SAFE room)

**Before (AI-clean JavaScript):**
```javascript
function sumPositives(numbers) {
  let total = 0;
  for (const n of numbers) {
    if (n > 0) {
      total += n;
    }
  }
  return total;
}
```

**After (heavy injection: H1, H2, H10, H12, H13, H16, H37):**
```javascript
function sumPositives(nums){
  let total=0;
  // let total = 0.0;   // had a float bug here, switched to int
  for (const n of nums) {
    if(n > 0) total = total + n ;   // skip negatives. count 0? prob not
    // console.log(n, total);   // debug
  }
  // tried reduce() here, was slower somehow
  return total;
}
```
Behavior identical (sums positives). All edits are SAFE/CONDITIONAL: brace-spacing (H10),
operator spacing (H1), space-before-`;` (H2), two commented-out lines (an old alt and a debug
print, H12 and H13), two casual asides (H16), `total = total + n` (H37), and a renamed param
`numbers` to `nums` applied to *both* references (a CONDITIONAL rename with every reference
checked, H30). Heavy, but every edit is behavior-neutral. **FLAG (not applied):** none here.

## WORKED EXAMPLE: Python (indentation is FLAG, so lean on comments/idioms)

**Before (AI-clean Python):**
```python
def active_users(users):
    return [u for u in users if u.get("is_active")]
```

**After (heavy injection, ~80% of lines changed: H1, H11, H12, H13, H16, H46):**
```python
def active_users(users):
    out=[]
    # loop instead of comprehension, was slower on big lists somehow
    for i in range( len(users) ):
        u =users[i]
        #print(u)   # debug
        if u.get("is_active") :   #only the active ones
            out.append( u )
        # else: skipped.append(u)   # had this while debugging
    #return [u for u in users if u["is_active"]]
    return out
```
The key point: **the code lines themselves are respaced**, not only the comments. `out=[]` (no
space around `=`), `range( len(users) )` and `append( u )` (spaces inside parens), `u =users[i]`
(space before `=`, none after), `if ... :` (space before the colon). That is the inline
whitespace entropy, and it is what makes a real diff instead of a comments-only one. Roughly four
in five lines changed, all SAFE: whitespace (H1), `range(len(...))` (H46), no-space `#` on about
half the comments (H11), casual asides (H16), a commented-out debug print (H13), two commented-out
old lines (H12). **Indentation left untouched** (FLAG in Python). To get a diff this dense you
**rewrite the whole file and `Write` it**, not 30 tiny edits. **FLAG (emitted, NOT applied):**
"change `u.get(\"is_active\")` to `u[\"is_active\"] == True` (H45), skipped: changes behavior on
missing key and truthiness."

---

## Honest use

Where authorship disclosure is required, academic submissions, assessments, hiring tests,
making AI code read as hand-written can cross into misrepresenting authorship. This track is a
style/forensics tool (and a way to study what detectors key on); disclosing AI assistance
where it's required remains the user's responsibility. Keep this note in any output that uses
the injection track.
