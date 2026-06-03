#!/usr/bin/env python3
"""whitespace_entropy.py - mechanical inline-whitespace entropy for the code-humanizer skill.

This is PHASE 2 of the humanizer. The by-hand pass (phase 1) does the judgment work that needs a
model: the subtractive removal of AI tells, variable/function renames, idiom swaps, casual
comments, commented-out scars, and the occasional typo. THIS script then lays down the blanket
inline-whitespace entropy that a model reliably under-applies by hand (it reads as vandalizing
working code, so the model stops short). Whitespace entropy needs zero judgment, so a
deterministic script is the right and complete tool for it.

What it changes, and only this:
  - inter-token whitespace on selected lines, but only next to a punctuation/operator token
    (so `x = y` may become `x=y`, `f(a, b)` may become `f(a ,b)`, never `return x` -> `returnx`)
  - the space after `#` on about half of line comments (the 50/50 hash split)

What it never touches: leading indentation (syntactic in Python), string and f-string contents,
or any code token. It proves this by re-tokenizing its own output and aborting if the code-token
stream is not byte-identical to the input. So behavior is provably unchanged.

Python only (indentation is syntactic; brace languages would use a different pass).

Usage:
    python whitespace_entropy.py FILE [--rate 0.5] [--seed 0] [--check-only]
"""
import argparse
import io
import sys
import random
import tokenize

# tokens that carry structural whitespace; we reproduce that whitespace from the source slice
# instead of from the token string, so indentation and newlines stay byte-exact.
_WS = {tokenize.INDENT, tokenize.DEDENT, tokenize.NEWLINE, tokenize.NL,
       tokenize.ENCODING, tokenize.ENDMARKER}
# f-string sub-tokens (python 3.12+); empty set on older pythons where an f-string is one STRING.
_FSTRING = {getattr(tokenize, n) for n in ('FSTRING_START', 'FSTRING_MIDDLE', 'FSTRING_END')
            if hasattr(tokenize, n)}


def code_tokens(src):
    """the (type, text) of every token that carries meaning. comments and whitespace excluded."""
    out = []
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                      tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING, tokenize.ENDMARKER):
            continue
        out.append((t.type, t.string))
    return out


def _toggle_hash(s, rng, rate):
    """flip the space after a leading '#' on a line comment, about `rate` of the time."""
    if not s.startswith('#') or s.startswith('#!'):
        return s
    body = s.lstrip('#')
    hashes = s[:len(s) - len(body)]
    if rng.random() >= rate:
        return s
    if body.startswith(' '):
        return hashes + body[1:]          # "# foo" -> "#foo"
    if body and not body[0].isspace():
        return hashes + ' ' + body        # "#foo" -> "# foo"
    return s


def perturb(src, rate=0.5, seed=0):
    rng = random.Random(seed)
    lines = src.splitlines(keepends=True)
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    real = [t for t in toks if t.type not in _WS]

    def between(a, b):
        (r1, c1), (r2, c2) = a, b
        if r1 == r2:
            return lines[r1 - 1][c1:c2]
        parts = [lines[r1 - 1][c1:]]
        for r in range(r1 + 1, r2):
            parts.append(lines[r - 1])
        parts.append(lines[r2 - 1][:c2])
        return ''.join(parts)

    def gap_is_safe(p, t, in_fstr):
        # a gap is safe to resize only next to an operator/punctuation token, and never inside
        # an f-string replacement field. the global token re-check is the backstop.
        if p is None or in_fstr:
            return False
        if p.type in _FSTRING or t.type in _FSTRING:
            return False
        # skip attribute dots: humans almost never write `a . b`, so it reads fake
        if (p.type == tokenize.OP and p.string == '.') or (t.type == tokenize.OP and t.string == '.'):
            return False
        return p.type == tokenize.OP or t.type == tokenize.OP

    # pick ~rate of the lines that actually have an eligible gap
    eligible = set()
    in_fstr = 0
    for i in range(1, len(real)):
        p, t = real[i - 1], real[i]
        if t.start[0] == p.end[0] and gap_is_safe(p, t, 0):
            eligible.add(t.start[0])
    chosen = {ln for ln in eligible if rng.random() < rate}

    out = []
    cur = (1, 0)
    in_fstr = 0
    for i, t in enumerate(real):
        gap = between(cur, t.start)
        p = real[i - 1] if i > 0 else None
        same_line = p is not None and t.start[0] == p.end[0]
        if (same_line and t.start[0] in chosen and gap == ' ' * len(gap)
                and gap_is_safe(p, t, in_fstr)):
            gap = ' ' * rng.choice([0, 0, 1, 1])   # flip tight <-> single space, never doubled
        out.append(gap)
        txt = t.string
        if t.type == tokenize.COMMENT:
            txt = _toggle_hash(txt, rng, 0.5)
        out.append(txt)
        if t.type in _FSTRING:
            if t.type == getattr(tokenize, 'FSTRING_START', -1):
                in_fstr += 1
            elif t.type == getattr(tokenize, 'FSTRING_END', -1):
                in_fstr = max(0, in_fstr - 1)
        cur = t.end

    tail_to = (len(lines), len(lines[-1])) if lines else (1, 0)
    out.append(between(real[-1].end, tail_to) if real else '')
    return ''.join(out)


def main():
    ap = argparse.ArgumentParser(description="add inline whitespace entropy to a python file")
    ap.add_argument("file")
    ap.add_argument("--rate", type=float, default=0.5, help="fraction of eligible lines to touch")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--check-only", action="store_true", help="don't write, just report")
    a = ap.parse_args()

    src = open(a.file, encoding="utf-8").read()
    new = perturb(src, rate=a.rate, seed=a.seed)

    # the backstop: behavior is preserved iff the code-token stream is byte-identical.
    if code_tokens(src) != code_tokens(new):
        sys.exit("ABORT: code tokens changed, refusing to write (this is a bug, not your code)")
    try:
        compile(new, a.file, "exec")
    except SyntaxError as e:
        sys.exit(f"ABORT: result does not compile: {e}")

    total = sum(1 for ln in src.splitlines() if ln.strip() and not ln.strip().startswith("#"))
    touched = sum(1 for o, n in zip(src.splitlines(), new.splitlines()) if o != n)
    print(f"  whitespace pass: {touched} lines changed (~{100*touched/max(1,total):.0f}% of code lines), "
          f"code tokens identical, compiles")
    if not a.check_only:
        open(a.file, "w", encoding="utf-8", newline="\n").write(new)
        print(f"  wrote {a.file}")


if __name__ == "__main__":
    main()
