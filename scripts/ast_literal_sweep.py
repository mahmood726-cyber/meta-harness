"""r24 class sweep: literal trial counts / effects assigned in harness CODE, found by an AST walk (grep found only
same-line dict literals). A trial's number belongs in a source-bound record with its span, never in code.

Flags, per harness/*.py:
  COUNT_OR_EFFECT_KEY  a dict entry whose key names a trial count / effect field (ai, n1i, ci, n2i, events_t, n_t,
                       effect, ci_low, ci_high, estimate, lower, upper, ...) with a NUMERIC LITERAL value
  EFFECT_TUPLE_TEXT    a string literal that prints an effect with its interval ('0.91 (0.74-1.11)')
  COUNT_PAIR_TEXT      a string literal that prints two-arm counts ('20/169', '159/27 307')

    python scripts/ast_literal_sweep.py   -> outputs/k_gap/g1_binding/ast_literal_sweep.json
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "ast_literal_sweep.json")
ALLOW = os.path.join(ROOT, "registry", "ast_literal_allowlist.json")
_KEYS = {"ai", "bi", "ci", "di", "n1i", "n2i", "events_t", "events_c", "n_t", "n_c", "effect", "ci_low", "ci_high",
         "estimate", "lower", "upper", "hr", "rr", "or", "e1i", "e2i", "t1i", "t2i", "mean1", "mean2", "sd1", "sd2"}
# signed values too: 'SMD -0.35 (-0.50–-0.20)' (codex copps-r7#2); integer parts allowed so long as one of the three
# numbers carries a decimal ('RR 2.0 (1.0-4)', r8#2)
_N = r"[-−]?\d+(?:[.·]\d{1,6})?"          # up to 6 decimals ('0.9123', codex copps-r10#2)
_EFFECT_TEXT_ANY = re.compile(r"(?<![\w.])" + _N + r"\s*\(\s*" + _N + r"\s*(?:[-–,]|to)\s*" + _N + r"\s*\)")


class _EffectText:
    """finditer over _EFFECT_TEXT_ANY, keeping only matches with at least one decimal number."""
    @staticmethod
    def finditer(s):
        return (m for m in _EFFECT_TEXT_ANY.finditer(s) if re.search(r"\d[.·]\d", m.group(0)))


_EFFECT_TEXT = _EffectText()
# denominators: 1-6 ungrouped digits or digit-grouped thousands (codex copps-r1#3 '20/1000', r5#4 '2/8')
# and never part of a decimal ('0.75/1.25' GRADE thresholds are not the count 75/1)
# ...and never the prefix of a larger or decimal number: no [.,]digit may follow ('20/1,234.5' is not '20/1', r10#1)
# (nor of a space-grouped one: '20/1 234.5', r11#2)
# (the numerator may be grouped too, and never starts inside a grouped number: '1,234/5,678', r12#3)
_COUNT_TEXT = re.compile(r"(?<![\d.,])(?<!\d )(?:\d{1,3}(?:[ ,]\d{3})+|\d{1,5})\s*/\s*(?:\d{1,3}(?:[ ,]\d{3})+|\d{1,6})\b"
                         r"(?![.,]\d)(?! \d{3}\b)")


def _num(node):
    """The numeric value of a literal, including a negated one (-0.35 is UnaryOp(USub, Constant)); else None."""
    sign = 1
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        sign = -1 if isinstance(node.op, ast.USub) else 1
        node = node.operand
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return sign * node.value
    return None


def _unpack(target, value) -> list[tuple[str, ast.AST]]:
    """(key, value-node) for every row['key'] in an assignment target, recursing through tuple/list unpacking."""
    if value is None:
        return []
    if isinstance(target, (ast.Tuple, ast.List)):
        if isinstance(value, (ast.Tuple, ast.List)) and len(target.elts) == len(value.elts):
            return [p for t, v in zip(target.elts, value.elts) for p in _unpack(t, v)]
        return []
    if isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Constant) \
            and isinstance(target.slice.value, str):
        return [(target.slice.value, value)]
    if isinstance(target, ast.Attribute):                      # study.ai = 20 (codex copps-r14#2)
        return [(target.attr, value)]
    return []


def sweep_source(src: str, path: str) -> list[dict]:
    out = []
    tree = ast.parse(src)
    # docstrings document examples; they assign nothing
    docs = {id(n.body[0].value) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body
            and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
    for node in ast.walk(tree):
        if id(node) in docs:
            continue
        # a field set by a dict literal OR by a keyword argument of any call -- dict(ai=20), Study(ai=20, ...)
        # (codex copps-r5#3)
        pairs = []
        if isinstance(node, ast.Dict):
            pairs = [(k.value, v) for k, v in zip(node.keys, node.values)
                     if isinstance(k, ast.Constant) and isinstance(k.value, str)]
        elif isinstance(node, ast.DictComp):
            # {'ai': 20 for _ in ...} (codex copps-r9#3)
            if isinstance(node.key, ast.Constant) and isinstance(node.key.value, str):
                pairs = [(node.key.value, node.value)]
        elif isinstance(node, ast.Call):
            pairs = [(kw.arg, kw.value) for kw in node.keywords if kw.arg]
        elif isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            # row['ai'] = 20 (codex copps-r6#2)
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                # row['ai'], row['n1i'] = 20, 169 and nested ((a, b), (c, d)) = ... (codex copps-r7#1, r8#3)
                pairs += _unpack(t, node.value)
        for name, v in pairs:
            val = _num(v)
            if name.lower() in _KEYS and val is not None:     # 0 and 1 are real arm counts too (codex copps-r2#2)
                out.append({"file": path, "line": v.lineno, "kind": "COUNT_OR_EFFECT_KEY", "key": name, "value": val})
        if isinstance(node, (ast.Dict, ast.DictComp, ast.Call, ast.Assign, ast.AugAssign, ast.AnnAssign)):
            continue
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            # every effect tuple AND every count pair is reported: one allowlisted finding never hides another in the
            # same string (codex copps-r3#3, r4#2)
            for m in _EFFECT_TEXT.finditer(s):
                out.append({"file": path, "line": node.lineno, "kind": "EFFECT_TUPLE_TEXT", "value": m.group(0)})
            # each count match is judged on its own context, never the whole string (codex copps-r2#3): a URL path
            # or a date is not a count; a count beside a URL still is
            urls = [m.span() for m in re.finditer(r"https?://\S+", s)]
            for m in _COUNT_TEXT.finditer(s):
                if any(a <= m.start() < b for a, b in urls):
                    continue
                a, b = (int(x.replace(" ", "").replace(",", "")) for x in m.group(0).split("/"))
                # d/m is a date only with a third /year part ('Deaths 5/10' is a count, codex copps-r3#2)
                dmy = re.match(r"/\d{2,4}\b", s[m.end():]) or re.search(r"\b\d{1,4}/$", s[:m.start()])
                # ...or the day of an ISO date in a path ('gate-authority-2026-09-14/03-refusal')
                dmy = dmy or re.search(r"\d{4}-\d{2}-$", s[:m.start()])
                # a leading-zero denominator alone is no date ('Deaths 2/08' is a count, codex copps-r6#3)
                if (a <= 31 and b <= 12 and dmy) or (1900 <= a <= 2100 and b <= 12):
                    continue
                out.append({"file": path, "line": node.lineno, "kind": "COUNT_PAIR_TEXT", "value": m.group(0)})
    return out


def sweep(root=ROOT) -> list[dict]:
    hits = []
    hdir = os.path.join(root, "harness")
    for f in sorted(os.listdir(hdir)):
        if f.endswith(".py"):
            p = os.path.join(hdir, f)
            hits += sweep_source(open(p, encoding="utf-8").read(), f"harness/{f}")
    return hits


def key(h):
    return f"{h['file']}|{h['kind']}|{h.get('key', '')}|{h['value']}"


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    hits = sweep()
    allow = json.load(open(ALLOW, encoding="utf-8"))["allowed"] if os.path.exists(ALLOW) else {}
    for h in hits:
        h["allowlisted"] = key(h) in allow
    json.dump({"hits": hits, "n": len(hits), "not_allowlisted": [h for h in hits if not h["allowlisted"]]},
              open(OUT, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    for h in hits:
        print(("   " if h["allowlisted"] else "NEW"), h["file"], h["line"], h["kind"], h.get("key", ""), h["value"])
