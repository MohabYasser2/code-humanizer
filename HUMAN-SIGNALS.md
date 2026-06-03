# Human-Signal Injection (opt-in additive track)

This is the **additive** half of Code Humanizer. The 22 patterns in `SKILL.md` *remove*
AI tells (subtractive, on by default). This track *adds* the affirmative fingerprints of
human authorship: formatting entropy, lived-in comments, idiosyncratic naming, evolution
scars.

**This track is OFF by default and never runs unless the user explicitly asks for it**
(e.g. "inject human signals", "make it look hand-written", `--inject-signals`). The default
`/code-humanizer` is subtractive only.

The research basis: *Whitespaces Don't Lie* (arXiv 2601.19264) found human code shows
**15–40% higher variance in formatting metrics across identical implementations** —
*"humans create intentional inconsistency; AI generates unintentional uniformity."*
Whitespace and indentation were the single most discriminative cues. So the objective is
**add variance, not add mess** — and variance that doesn't compile is worthless.

---

## THE INJECTION CONTRACT (read this first)

The subtractive behavior contract still holds: **the program must behave identically on the
success path.** Injection makes that *harder*, not easier, so it is governed by a strict
safety tier. Every signal below is tagged:

- **SAFE** — provably behavior-neutral. Touches only comments, blank lines, and whitespace
  in languages where whitespace is non-syntactic, or the inside of string literals that are
  not keys/paths/format-sensitive. **May be auto-applied.**
- **CONDITIONAL** — behavior-neutral *only if* applied completely and in a compatible
  language (e.g. a rename touching every reference, an idiom swap that is semantically equal
  for this type). **Apply only after verifying the precondition; otherwise treat as FLAG.**
- **FLAG** — can change behavior or fail to compile (identifier typos, Python
  indentation/tab changes, `== True`/`== None` semantics, dropping a guard). **Never
  auto-apply. Emit these as a numbered suggestion list for the human to apply by hand.**

> **The hard rule that keeps code working:** the skill auto-edits SAFE and *verified* CONDITIONAL only.
> FLAG is reported, never written. If you cannot prove a CONDITIONAL edit is total and safe, demote it
> to FLAG and flag it. When unsure, flag — don't guess.

After injecting, **verify**: re-run the project's tests / type checker / linter if present,
or at minimum confirm the file still parses (`python -c "import ast,sys; ast.parse(open(f).read())"`
for Python, a compile for brace languages). Report the result. If it no longer parses, revert.

### Verifying a CONDITIONAL rename — the complete-reference rule

Renames (H27–H31) are the most common CONDITIONAL edit and the easiest to get wrong: a rename is
behavior-neutral **only if every reference moves and nothing binds the old name by string or
reflection.** A half-done rename is a `NameError`/compile error or, worse, a silent bug. Before
applying any rename, run this checklist — if you can't complete it with confidence, **demote to
FLAG and flag it, don't rename:**

1. **Enumerate every reference — don't eyeball.** Grep the exact symbol across its scope: the
   whole file for a local, the whole project for an exported/public symbol. Count them.
2. **Rename all of them in one edit:** the definition, every use, keyword/named/default
   arguments, and the name inside doc comments (Python docstring params, C#/JS XML/JSDoc
   `<param name="...">` / `@param`).
3. **Check for name-based binding that an identifier grep misses** — these don't move with a
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
   field, property, public method, or exported symbol is **FLAG — flag, never auto-rename** —
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
and inline alignment — never the indent column. In brace languages, formatting is almost all
SAFE because the compiler ignores it.

> The headline example `int x=y ;` (space before semicolon, no spaces around `=`) is a
> brace-language signal — SAFE in C/C++/Java/C#/JS/TS, not applicable in Python.

**For JavaScript, TypeScript, and C#, read `LANGUAGES.md`** before applying any whitespace,
type, equality, or idiom signal. It has the per-language tiers (TS type edits are compile-gated
CONDITIONAL; JS `===`→`==` and `let`→`var` are FLAG; C# `var`↔explicit and `#region` are SAFE) and the
**formatter caveat**: if Prettier / `dotnet format` / EditorConfig runs on save or in CI,
whitespace injection is normalized away — lean on comments, naming, and idioms instead.

---

## THE CATALOG (H-track)

Grouped for reference. Apply a *subset*, at *uneven* density — see the density rule below.

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
| H11 | No-space-after-`#`/`//` | `#like this` mixed with `# like this` | SAFE |

### Comments — the human kind (AI strips these; their presence is the strongest tell)

| ID | Signal | Example | Tier |
|----|--------|---------|------|
| H12 | **Commented-out code left in** | `# old_lr = 3e-4` · `// for(i..) print(i)` | SAFE |
| H13 | Debug prints | `print("here")` `print("aaaa")` · commented `# breakpoint()` | SAFE commented · CONDITIONAL live (adds a side effect) |
| H14 | TODO/FIXME/HACK/XXX with real context | `# FIXME: breaks on empty input, ask Omar` | SAFE |
| H15 | Stale comment that contradicts the code | comment says "0=stay" but `0` means up | SAFE |
| H16 | Venting / emotional | `# this is dumb but it works` · `# don't touch` | SAFE |
| H17 | Dated / signed scribbles | `# 12/03 hack — revisit` · `# -MY` | SAFE |
| H18 | Native-language comment | a non-English line mid-file | SAFE |
| H19 | Pragmatic suppressions | `# noqa` `# type: ignore` `# pylint: disable=...` | CONDITIONAL (must be a real, valid pragma) |
| H20 | External references | `# from stackoverflow.com/q/...` · ticket #, a name | SAFE |
| H21 | Half-finished thought | `# need to handle the case where` (stops) | SAFE |

### Spelling, typos, grammar

| ID | Signal | Example | Tier |
|----|--------|---------|------|
| H22 | Typos in **comments / log strings** | `recieve`, `seperate`, `occured`, `lenght` | SAFE |
| H23 | Typos in **identifiers** | `recieved_data`, `widht` used everywhere | **FLAG** (one missed ref = `NameError`) |
| H24 | British/American mix | `colour`/`color` in comments | SAFE comment · FLAG identifier |
| H25 | Non-native / loose grammar in comments | "this make the thing for calc" | SAFE |
| H26 | Inconsistent message capitalization | `"Error:"` vs `"error :"` | SAFE (watch exact-match consumers) |

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
| H45 | `== True` / `== None` | `if active == True:` `if x == None:` | **FLAG** — semantics differ for numpy/None |
| H46 | `range(len(x))` instead of `enumerate` | | SAFE |
| H47 | `len(x) == 0` instead of `not x` | | CONDITIONAL (differs for numpy/pandas) |
| H48 | Redundant parens | `return (x)` `if (a and b):` | SAFE |
| H49 | `+` concat instead of f-string (mixed) | `"hi " + name` and `f"hi {name}"` | SAFE |

### Repo level (multi-file)

| ID | Signal | Example | Tier |
|----|--------|---------|------|
| H50 | Human file names | `test2.py`, `Copy of x`, `final_v3.py`, `.bak` | CONDITIONAL (update imports if renaming a module) |

---

## THE DENSITY RULE (the part most people get wrong)

A *uniform* layer of injected noise is just a new, detectable uniformity. Per the research,
human inconsistency is **inconsistently** distributed. So:

1. **Apply a random subset, not all of it.** Pick ~5–10 signal *types* for a file, not 50.
2. **Vary density by region.** Leave one function almost clean; rough up another. Real code
   has a careful core and a rushed edge (evolution scars, H35/H39).
3. **Don't make every line messy.** Operator-spacing entropy means *some* `=` have spaces and
   *some* don't — not that none do.
4. **Match plausibility.** A misspelling a real dev makes (`recieve`) beats a random one
   (`receeeive`). Venting comments fit hard code, not a one-line helper.
5. **Never inject the same transform on a fixed interval.** That interval *is* a signature.

Over-injection is a tell and risks breakage. Under-injection on top of a good subtractive
pass is usually enough — the subtractive pass already removes ~80% of the AI signal.

---

## PROCESS

1. **Confirm opt-in.** Only run this track if the user asked for injection.
2. **Branch on language.** Build the safe set from the LANGUAGE BRANCH table. In Python, drop
   all indentation/tab signals to FLAG.
3. **(Recommended) Run the subtractive pass first.** Remove AI tells (SKILL.md 1–22), *then*
   inject. Subtract-then-inject is more robust and safer than leading with typos.
4. **Pick an uneven subset** per the density rule.
5. **Apply SAFE and verified CONDITIONAL edits only.** Collect every FLAG as a suggestion list.
6. **Verify** it still parses / tests still pass. Revert anything that breaks.
7. **Deliver:** the rewritten code, the list of signals injected (with IDs), the **FLAG-tier
   suggestions the human must apply manually**, the verification result, and a one-line note
   that injection is opt-in style work, not a behavior change.

---

## WORKED EXAMPLE — brace language (lots of SAFE room)

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

**After (signals injected — H1, H2, H4, H10, H12, H14, H37):**
```javascript
function sumPositives(nums){
  let total=0;
  // let total = 0.0;  // had a float bug here before

  for (const n of nums) {
    if(n > 0) total = total + n ;   // FIXME do we count 0? prob not
  }
  return total;
}
```
Behavior identical (sums positives). All edits are SAFE/CONDITIONAL: brace-spacing (H10), operator
spacing (H1), space-before-`;` (H2), a commented-out old line (H12), a real-context FIXME
(H14), `total = total + n` (H37), a renamed param `numbers→nums` applied to *both* references
(a CONDITIONAL rename with every reference checked — H30). **FLAG (not applied):** none needed here.

## WORKED EXAMPLE — Python (indentation is FLAG, so lean on comments/idioms)

**Before (AI-clean Python):**
```python
def active_users(users):
    return [u for u in users if u.get("is_active")]
```

**After (signals injected — H1, H11, H12, H16, H22, H46):**
```python
def active_users(users):
    out = []
    #loop and grab the active ones (comprehension was slower somehow??)
    for i in range(len(users)):
        u = users[i]
        if u.get("is_active"):   # recieve only the live accounts
            out.append(u)
    # return [u for u in users if u["is_active"]]
    return out
```
Behavior identical. Edits: `range(len(...))` expansion (H46, SAFE), no-space `#` comment (H11),
a venting/uncertain aside (H16), a typo in a comment `recieve` (H22, SAFE), operator/format
entropy (H1), a commented-out old one-liner (H12). **Indentation left untouched** (FLAG in
Python). **FLAG (emitted, NOT applied):** "change `u.get(\"is_active\")` to
`u[\"is_active\"] == True` (H45) — skipped: changes behavior on missing key + truthiness."

---

## Honest use

Where authorship disclosure is required — academic submissions, assessments, hiring tests —
making AI code read as hand-written can cross into misrepresenting authorship. This track is a
style/forensics tool (and a way to study what detectors key on); disclosing AI assistance
where it's required remains the user's responsibility. Keep this note in any output that uses
the injection track.
