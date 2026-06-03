# Language Guide — per-language safety for human-signal injection

The injection track (`HUMAN-SIGNALS.md`) tags every signal SAFE/CONDITIONAL/FLAG, but those tiers
**shift by language**. The same whitespace edit is free in C# and fatal in Python. This file
gives the per-language specifics for the languages the skill targets first-class —
**JavaScript, TypeScript, C#** — plus shorter notes for the rest of the C-family.

Read this before applying any whitespace, type, or idiom signal in these languages.

> **Formatter caveat (applies to all three).** If the project runs an autoformatter on save or
> in CI — **Prettier** (JS/TS), **`dotnet format`/EditorConfig/IDE format** (C#) — then injected
> whitespace entropy (H1, H2, H4, H5, H8, H10) gets normalized away on the next format. In a
> formatted project, whitespace injection is pointless (or actively reverted); lean on
> **comments, commented-out code, naming, and idioms** instead, which formatters don't touch.
> Check for `.prettierrc`, `.editorconfig`, a `format` script, or a CI format step first.

---

## Quick safety matrix (vs. Python for contrast)

| Signal class | JavaScript | TypeScript | C# | Python |
|---|---|---|---|---|
| Operator/brace/indent whitespace (H1–H10) | SAFE | SAFE | SAFE | indent/tabs FLAG, rest SAFE |
| Remove a semicolon | SAFE (ASI traps → FLAG, see below) | SAFE (same traps) | FLAG **required** | n/a |
| Comments / commented-out code (H12–H21) | SAFE | SAFE | SAFE | SAFE |
| Typos in comments / strings (H22) | SAFE | SAFE | SAFE | SAFE |
| Drop a type annotation | n/a | CONDITIONAL **compile-gated** | CONDITIONAL (`var`↔explicit is SAFE) | SAFE |
| `===`→`==` / `==`→loose equality | FLAG | FLAG | CONDITIONAL (value vs ref/`.Equals`) | n/a |
| Rename a local (H27–H31) | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL |
| Rename a field/prop/public symbol | FLAG (string/reflection refs) | FLAG | FLAG (serialization/reflection by name) | FLAG |

"CONDITIONAL compile-gated" = runtime-neutral but must pass the compiler; verify before applying.

---

## JavaScript

**Whitespace.** Non-syntactic → H1–H10 are SAFE. Indentation width, brace style (`if(x){` vs
`if (x) {`), spaces around `=`/operators, blank lines: all free (unless Prettier reverts them).

**Semicolons (ASI).** Removing semicolons is usually SAFE, but Automatic Semicolon Insertion has
real traps — a statement that *begins* with `(`, `[`, `` ` ``, `+`, `-`, or `/` can glue onto the
previous line and change meaning. Removing the `;` before such a line is FLAG. Adding semicolons is
always SAFE.

**Equality.** `===`↔`==` and `!==`↔`!=` change behavior via coercion (`0 == ""` is `true`).
FLAG — flag, never auto-swap.

**Declarations.** `const`→`let` is SAFE (only widens what's allowed; current behavior identical).
`let`/`const`→`var` is FLAG (hoisting + function-scope + closure capture differ — classic loop-var
bug). `var`→`let` is CONDITIONAL (usually fine, can change a closure that relied on hoisting).

**Arrow vs `function`.** Swapping is FLAG if the body uses `this`, `arguments`, `new`, or
`yield`; SAFE for a pure callback that uses none of them.

**Strings.** `'…'`↔`"…"` is SAFE (mind escaping). A template literal `` `…${x}…` `` is **not**
interchangeable with a plain string unless you actually interpolate — converting a static
template to a quote is SAFE, the reverse only if there's no `${}`.

**Human/legacy signals to inject (SAFE unless noted):** `var` and `function` declarations instead
of `const`/arrow; sloppy `==` *where it was already sloppy* (don't introduce it — FLAG); classic
`for (var i = 0; i < a.length; i++)` loops next to a `.map`; string `+` concat mixed with
templates; `var self = this;`; callback style next to `async/await`; `// eslint-disable-line`;
JSDoc `/** */` on one function and nothing on the next; `console.log('here')` left in (CONDITIONAL — it's
a side effect; prefer commented `// console.log(x)`).

**Comments:** `//`, `/* */`, JSDoc `/** */`.

---

## TypeScript

Everything in **JavaScript** applies (TS is a superset). The one big difference: **types are
load-bearing at compile time**, even though they erase at runtime.

**Type edits are runtime-neutral but compile-gated → CONDITIONAL, verify with `tsc --noEmit`:**
- **Removing an annotation** is SAFE *only if* inference produces the same type and
  `noImplicitAny` won't error. Otherwise it's a compile error → keep it / treat as FLAG.
- **Adding `: any`** (a very human "make the error go away" move) erases to nothing at runtime,
  but loosens checking and can cascade. CONDITIONAL.
- **`!` non-null assertion** and **`as` casts**: erased at runtime, so adding/removing is
  runtime-SAFE, but can introduce or hide compile errors → CONDITIONAL.
- **`interface` ↔ `type`** for object shapes: SAFE (interchangeable in the common case).
- **`enum` ↔ union of literals**: **not** equivalent (enums emit runtime objects) → FLAG.

**Human signals to inject:** `any` sprinkled to silence the checker; `// @ts-ignore` /
`// @ts-expect-error`; `as any`; trailing `!`; mixing `interface` and `type` in one file;
inconsistent optional `?`; `Array<T>` next to `T[]`. These are authentic TS-dev tells and are
SAFE/CONDITIONAL (run `tsc` after).

**Do not** "humanize" by deleting types in a strict project — that breaks the build. In TS,
prefer comment/naming/idiom signals over type-stripping.

---

## C#

Compiled and statically typed, but **whitespace is fully non-syntactic → H1–H10 are SAFE**
(again, only useful if no formatter/EditorConfig reverts them).

**Brace style.** The C# default is Allman (brace on its own line); plenty of real code mixes
Allman and K&R. Mixing is SAFE and a genuine human signal.

**`var` ↔ explicit type.** SAFE when the inferred type matches the explicit one (identical IL).
Humans mix `var x = new List<int>();` with `List<int> y = ...` freely — a strong, safe signal.

**`this.` qualifier.** Adding `this.` is SAFE. Removing it is SAFE **unless** a parameter or local
shadows the field — then removal rebinds to the wrong symbol → FLAG. Inconsistent `this.` usage is
very human; inject it only where no shadowing exists.

**`#region` / `#endregion`.** Compiler-ignored → SAFE. Real C# devs (and IDE refactors) leave
these everywhere; a stray `#region` is an authentic, safe organizational signal.

**XML doc `///` and `//` / `/* */`.** All SAFE. A `///` summary on one method and nothing on the
next is normal.

**Idioms (SAFE when provably equivalent):** LINQ query syntax (`from x in xs where … select x`)
↔ method syntax (`xs.Where(…).Select(…)`) — the compiler translates one to the other; mixing is
human. Expression-bodied members (`=> expr`) ↔ block bodies. `$"{x}"` interpolation ↔
`string.Format`/`+` concat — SAFE if the result string is identical (watch culture and format
specifiers like `{x:0.00}`).

**Equality.** `==` vs `.Equals()` can differ for reference types and nullable values → CONDITIONAL/FLAG.
Don't swap them as a "signal."

**Properties.** Auto-property `{ get; set; }` ↔ a manual backing field is SAFE *only* if the
manual version adds no logic; if there's a setter side effect, they differ → FLAG.

**Renames are dangerous in C#** because names are bound by string in several places — see the
checklist below. Renaming a **local** is CONDITIONAL; renaming a **field/property/method/public symbol**
is FLAG.

**Human signals to inject:** mixed `var`/explicit types; inconsistent `this.`; `#region`
blocks; `// TODO:` / `// HACK:`; commented-out old code; a manual `for`/`foreach` next to a LINQ
chain; `string.Format` next to interpolation; private fields as `_camelCase` in one class and
`camelCase` in another; an oversized method left unsplit.

---

## Other C-family (C, C++, Java) — short version

Whitespace H1–H10 are SAFE (compiler ignores formatting); semicolons are **required** (removing
one is FLAG). Pointer-spacing style in C/C++ (`int* p` vs `int *p` vs `int * p`) is a SAFE signal and
a real per-dev habit. `int x=y ;` (no spaces around `=`, space before `;`) is the canonical
brace-language whitespace tell — SAFE. Java: brace style and `final` usage vary by dev. Renames of
public members are FLAG (reflection, serialization, overrides).

## Formatter-enforced languages (Go, Rust) — caution

`gofmt`/`rustfmt` rewrite formatting on every save/build, so **whitespace injection is erased**
— don't bother. Go *requires* tabs (mixing in spaces is FLAG). In these languages the only durable
human signals are comments, commented-out code, naming, and idiom choices, not whitespace.

---

## How the skill uses this file

When the injection track runs (opt-in), after the language branch:
1. Detect the language and whether a formatter is configured (skip whitespace signals if so).
2. Pull that language's SAFE set from the matrix above; demote anything language-risky to FLAG.
3. Apply SAFE + verified CONDITIONAL edits only; collect FLAG items as suggestions. Then compile/parse-check with the language's tool
   (`tsc --noEmit`, `node --check`, `dotnet build`, etc.) and revert anything that breaks.
