#!/usr/bin/env python3
"""whitespace_entropy.py - mechanical inline-whitespace entropy for the code-humanizer skill.

PHASE 2 of the humanizer. The by-hand pass (phase 1) does the judgment work that needs a model:
subtractive removal of AI tells, variable/function renames, idiom swaps, casual comments,
commented-out scars, the occasional typo. THIS script then lays down the blanket inline-whitespace
entropy a model reliably under-applies by hand (it reads as vandalizing working code, so the model
stops short). Whitespace entropy needs zero judgment, so a deterministic script is the right tool.

Languages (dispatched by file extension):
  - Python (.py): uses the stdlib tokenizer; never touches indentation (it is syntactic).
  - Brace family (.js .jsx .mjs .cjs .ts .tsx .cs .c .h .cpp .cc .hpp .hh .java): a generic lexer
    protects strings/chars/comments, then perturbs whitespace only around the delimiters
    ( ) [ ] { } , ; and a standalone = . Those positions can never merge two tokens, so the
    change is safe; leading indentation is left alone for plausibility.
  - Go/Rust (.go .rs): handled by the brace path, but gofmt/rustfmt will erase the entropy on the
    next build, so it warns.

It changes ONLY whitespace: the gaps between tokens, the space after a # or // on about half of
comments, and the occasional blank line at a safe statement boundary. It never alters indentation,
string/char/comment contents, or any code token, and it verifies that
before writing: Python re-tokenizes; brace languages compare the protected spans and the
whitespace-stripped code skeleton. Compile the result with the language's own tool for final proof.

Usage:
    python whitespace_entropy.py FILE [--rate 0.5] [--seed 0] [--check-only]
"""
import argparse
import io
import os
import re
import sys
import random
import tokenize

# ----------------------------------------------------------------------------- Python path

_WS = {tokenize.INDENT, tokenize.DEDENT, tokenize.NEWLINE, tokenize.NL,
       tokenize.ENCODING, tokenize.ENDMARKER}
_FSTRING = {getattr(tokenize, n) for n in ('FSTRING_START', 'FSTRING_MIDDLE', 'FSTRING_END')
            if hasattr(tokenize, n)}


def _py_code_tokens(src):
    out = []
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                      tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING, tokenize.ENDMARKER):
            continue
        out.append((t.type, t.string))
    return out


def _toggle_hash(s, rng, rate, mark='#'):
    if not s.startswith(mark) or s.startswith('#!'):
        return s
    body = s[len(mark):]
    if rng.random() >= rate:
        return s
    if body.startswith(' '):
        return mark + body[1:]
    if body and not body[0].isspace():
        return mark + ' ' + body
    return s


def perturb_python(src, rate=0.5, seed=0):
    rng = random.Random(seed)
    lines = src.splitlines(keepends=True)
    real = [t for t in tokenize.generate_tokens(io.StringIO(src).readline) if t.type not in _WS]

    def between(a, b):
        (r1, c1), (r2, c2) = a, b
        if r1 == r2:
            return lines[r1 - 1][c1:c2]
        parts = [lines[r1 - 1][c1:]] + [lines[r - 1] for r in range(r1 + 1, r2)] + [lines[r2 - 1][:c2]]
        return ''.join(parts)

    def safe(p, t, in_fstr):
        if p is None or in_fstr or p.type in _FSTRING or t.type in _FSTRING:
            return False
        if (p.type == tokenize.OP and p.string == '.') or (t.type == tokenize.OP and t.string == '.'):
            return False
        return p.type == tokenize.OP or t.type == tokenize.OP

    eligible = {t.start[0] for i, t in enumerate(real) if i and t.start[0] == real[i - 1].end[0]
                and safe(real[i - 1], t, 0)}
    chosen = {ln for ln in eligible if rng.random() < rate}

    out, cur, in_fstr = [], (1, 0), 0
    for i, t in enumerate(real):
        gap = between(cur, t.start)
        p = real[i - 1] if i else None
        if (p is not None and t.start[0] == p.end[0] and t.start[0] in chosen
                and gap == ' ' * len(gap) and safe(p, t, in_fstr)):
            gap = ' ' * rng.choice([0, 0, 1, 1])
        out.append(gap)
        out.append(_toggle_hash(t.string, rng, 0.5) if t.type == tokenize.COMMENT else t.string)
        if t.type in _FSTRING:
            in_fstr += 1 if t.type == getattr(tokenize, 'FSTRING_START', -1) else 0
            in_fstr -= 1 if t.type == getattr(tokenize, 'FSTRING_END', -1) and in_fstr else 0
        cur = t.end
    out.append(between(real[-1].end, (len(lines), len(lines[-1]))) if real and lines else '')
    return ''.join(out)


# ----------------------------------------------------------------------------- brace family path

def _brace_segments(src):
    """split into ('code'|'prot', text). prot = string / char / line- or block-comment / template."""
    segs, buf, i, n = [], [], 0, len(src)

    def flush():
        if buf:
            segs.append(('code', ''.join(buf)))
            buf.clear()

    while i < n:
        c, nx = src[i], (src[i + 1] if i + 1 < n else '')
        if c == '/' and nx == '/':
            flush(); j = src.find('\n', i); j = n if j < 0 else j
            segs.append(('prot', src[i:j])); i = j
        elif c == '/' and nx == '*':
            flush(); j = src.find('*/', i + 2); j = n if j < 0 else j + 2
            segs.append(('prot', src[i:j])); i = j
        elif c in '"\'':
            flush(); q, j = c, i + 1
            while j < n:
                if src[j] == '\\':
                    j += 2; continue
                if src[j] == q:
                    j += 1; break
                if src[j] == '\n':
                    break
                j += 1
            segs.append(('prot', src[i:j])); i = j
        elif c == '`':
            flush(); j, depth = i + 1, 0
            while j < n:
                if src[j] == '\\':
                    j += 2; continue
                if src[j] == '`' and depth == 0:
                    j += 1; break
                if src[j] == '$' and j + 1 < n and src[j + 1] == '{':
                    depth += 1; j += 2; continue
                if src[j] == '}' and depth:
                    depth -= 1
                j += 1
            segs.append(('prot', src[i:j])); i = j
        else:
            buf.append(c); i += 1
    flush()
    return segs


_DELIM = set('()[]{},;')
_OPCHAIN = set('=!<>+-*/%&|^~')


def perturb_brace(src, rate=0.5, seed=0):
    rng = random.Random(seed)
    # toggle the space after // on ~half of line comments first
    segs = [('prot', _toggle_hash(t, rng, 0.5, '//')) if k == 'prot' and t.startswith('//') else (k, t)
            for k, t in _brace_segments(src)]
    s = ''.join(t for _, t in segs)
    prot = bytearray(len(s))
    pos = 0
    for k, t in segs:
        if k == 'prot':
            for j in range(pos, pos + len(t)):
                prot[j] = 1
        pos += len(t)

    line = [1] * (len(s) + 1)
    ln = 1
    for j, ch in enumerate(s):
        line[j] = ln
        if ch == '\n':
            ln += 1
    line[len(s)] = ln

    def standalone_eq(p):
        if not (0 <= p < len(s)) or s[p] != '=':
            return False
        b = s[p - 1] if p else ''
        a = s[p + 1] if p + 1 < len(s) else ''
        return b not in _OPCHAIN and a not in ('=', '>')

    runs, i = {}, 0
    while i < len(s):
        if s[i] in ' \t' and not prot[i]:
            a = i
            while i < len(s) and s[i] in ' \t' and not prot[i]:
                i += 1
            prevC = s[a - 1] if a else ''
            nextC = s[i] if i < len(s) else ''
            if prevC in ('\n', ''):          # leave leading indentation alone
                continue
            elig = (prevC in _DELIM or nextC in _DELIM
                    or (prevC == '=' and standalone_eq(a - 1))
                    or (nextC == '=' and standalone_eq(i)))
            if elig:
                runs[a] = i
        else:
            i += 1

    chosen = {l for l in {line[a] for a in runs} if rng.random() < rate}
    out, i = [], 0
    while i < len(s):
        if i in runs and line[i] in chosen:
            out.append(' ' * rng.choice([0, 0, 1, 1]))
            i = runs[i]
        else:
            out.append(s[i]); i += 1
    return ''.join(out)


def _brace_ok(orig, new):
    """behavior preserved iff the non-comment protected spans match and the whitespace-stripped
    code skeleton (newlines kept) matches. combined with the delimiter-only rule, no token merges."""
    def skel(src):
        code = ''.join(t for k, t in _brace_segments(src) if k == 'code')
        return re.sub(r'\n+', '\n', re.sub(r'[ \t]+', '', code))   # collapse \n so added blanks pass

    def strs(src):
        return [t for k, t in _brace_segments(src) if k == 'prot' and not t.startswith(('//', '/*'))]
    return skel(orig) == skel(new) and strs(orig) == strs(new)


# ----------------------------------------------------------------------------- blank lines

def _compiles(src, fname):
    try:
        compile(src, fname, "exec")
        return True
    except SyntaxError:
        return False


def add_blanks_py(orig_src, ws_text, rate, seed):
    """insert occasional blank lines after complete statements (NEWLINE ends), skipping decorators
    and clause continuations. behavior-inert; the caller compile-checks as a backstop."""
    if rate <= 0:
        return ws_text, 0
    rng = random.Random(seed + 1)
    ends = {t.start[0] for t in tokenize.generate_tokens(io.StringIO(orig_src).readline)
            if t.type == tokenize.NEWLINE}
    lines = ws_text.splitlines(keepends=True)
    out, n = [], 0
    skip = ('else', 'elif', 'except', 'finally', 'case ')
    for idx, ln in enumerate(lines):
        out.append(ln)
        if idx == len(lines) - 1:
            break
        s, nxt = ln.strip(), lines[idx + 1].strip()
        if (idx + 1) in ends and s and not s.startswith('@') and not nxt.startswith(skip):
            if rng.random() < rate:
                out.append('\n'); n += 1
                if rng.random() < 0.2:
                    out.append('\n'); n += 1
    return ''.join(out), n


def add_blanks_brace(text, rate, seed):
    """insert occasional blank lines after lines ending (in code) with ; { or }. always safe in
    brace languages; never inside a string, char, comment, or template."""
    if rate <= 0:
        return text, 0
    rng = random.Random(seed + 1)
    prot, pos = bytearray(len(text)), 0
    for k, t in _brace_segments(text):
        if k == 'prot':
            for j in range(pos, pos + len(t)):
                prot[j] = 1
        pos += len(t)
    lines = text.split('\n')
    off, acc = [], 0
    for ln in lines:
        off.append(acc); acc += len(ln) + 1
    out, n = [], 0
    for i, ln in enumerate(lines):
        out.append(ln)
        if i == len(lines) - 1:
            break
        base, last = off[i], None
        for j in range(len(ln) - 1, -1, -1):
            if ln[j] in ' \t':
                continue
            if base + j < len(prot) and prot[base + j]:
                continue
            last = ln[j]; break
        if last is not None and last in '{};' and rng.random() < rate:
            out.append(''); n += 1
            if rng.random() < 0.25:
                out.append(''); n += 1
    return '\n'.join(out), n


# ----------------------------------------------------------------------------- driver

_BRACE = {'.js', '.jsx', '.mjs', '.cjs', '.ts', '.tsx', '.cs', '.c', '.h',
          '.cpp', '.cc', '.hpp', '.hh', '.java', '.go', '.rs'}


def main():
    ap = argparse.ArgumentParser(description="add inline whitespace entropy to a source file")
    ap.add_argument("file")
    ap.add_argument("--rate", type=float, default=0.5, help="fraction of eligible lines to respace")
    ap.add_argument("--blank-rate", type=float, default=0.1,
                    help="chance of a blank line after a safe statement boundary (0 to disable)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()

    ext = os.path.splitext(a.file)[1].lower()
    src = open(a.file, encoding="utf-8").read()

    if ext == '.py':
        ws = perturb_python(src, a.rate, a.seed)
        new, nblank = add_blanks_py(src, ws, a.blank_rate, a.seed)
        if _py_code_tokens(src) != _py_code_tokens(new) or not _compiles(new, a.file):
            new, nblank = ws, 0                       # a blank upset the parser; drop the blanks
        if _py_code_tokens(src) != _py_code_tokens(new) or not _compiles(new, a.file):
            sys.exit("ABORT: code tokens changed or result does not compile (bug, not your code)")
    elif ext in _BRACE:
        if ext in ('.go', '.rs'):
            print("  note: gofmt/rustfmt will erase whitespace entropy on the next build")
        ws = perturb_brace(src, a.rate, a.seed)
        new, nblank = add_blanks_brace(ws, a.blank_rate, a.seed)
        if not _brace_ok(src, new):
            sys.exit("ABORT: protected spans or code skeleton changed (bug, not your code)")
    else:
        sys.exit(f"unsupported extension {ext!r} (python and the brace family are supported)")

    total = sum(1 for ln in src.splitlines() if ln.strip() and not ln.strip().startswith(('#', '//')))
    touched = sum(1 for o, n in zip(src.splitlines(), ws.splitlines()) if o != n)
    print(f"  whitespace pass: {touched} lines respaced (~{100*touched/max(1,total):.0f}% of code lines), "
          f"{nblank} blank lines added, protected content + code tokens identical")
    if not a.check_only:
        open(a.file, "w", encoding="utf-8", newline="\n").write(new)
        print(f"  wrote {a.file}")


if __name__ == "__main__":
    main()
