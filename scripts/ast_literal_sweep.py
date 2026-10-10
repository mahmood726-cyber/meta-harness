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
_EFFECT_TEXT = re.compile(r"\b\d+[.·]\d{1,3}\s*\(\s*\d+[.·]\d{1,3}\s*[-–,]\s*\d+[.·]\d{1,3}\s*\)")
_COUNT_TEXT = re.compile(r"\b\d{1,5}\s*/\s*\d{2,3}(?:[ ,]\d{3})?\b")


def _is_num(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool)


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
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and isinstance(k.value, str) and k.value.lower() in _KEYS and _is_num(v) \
                        and v.value not in (0, 1, None):
                    out.append({"file": path, "line": v.lineno, "kind": "COUNT_OR_EFFECT_KEY",
                                "key": k.value, "value": v.value})
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            if _EFFECT_TEXT.search(s):
                out.append({"file": path, "line": node.lineno, "kind": "EFFECT_TUPLE_TEXT",
                            "value": _EFFECT_TEXT.search(s).group(0)})
            elif _COUNT_TEXT.search(s) and not re.search(r"https?://|\d{4}/\d{2}|/\d+/", s):
                m = _COUNT_TEXT.search(s)
                a, b = (int(x.replace(" ", "").replace(",", "")) for x in m.group(0).split("/"))
                if not (a <= 31 and b <= 12) and not re.match(r"\d+\s*/\s*0\d", m.group(0)):   # a date is not a count
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
