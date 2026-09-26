"""Every compiled regex in harness/*.py, found by AST (any `re.compile(...)` call, at any depth), so coverage of the
regex layer is reported against a population derived from the source -- never against a remembered count. Inline
literal patterns (`re.search(r"...", s)`) are sites too: they are counted, keyed by line, and have no plant yet.

A site is "<file>:<name>" for a named compiled pattern, "<file>:L<line>" for an unnamed one, and
"<file>:<method>:<sha256(pattern text)[:10]>" for an inline literal.
  python -m regex_layer.inventory        prints n with plants of N sites, per file
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INLINE = ("search", "match", "fullmatch", "findall", "finditer", "sub", "subn", "split")


def _enclosing(tree: ast.AST, target: ast.AST) -> str:
    """The name of the innermost function containing `target`, or '<module>'."""
    best = "<module>"
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(n is target for n in ast.walk(node)):
            best = node.name        # ast.walk is breadth-first, so a later hit is nested deeper
    return best


def sites(root: Path = ROOT) -> list[dict]:
    out = []
    for p in sorted((root / "harness").glob("*.py")):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        named = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(node.value, ast.Call):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    if isinstance(t, ast.Name):
                        named[id(node.value)] = t.id
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and getattr(node.func.value, "id", "") == "re"):
                continue
            if node.func.attr == "compile":
                name = named.get(id(node))
                out.append({"file": p.name, "name": name, "line": node.lineno, "kind": "compiled",
                            "site": f"{p.name}:{name}" if name else f"{p.name}:L{node.lineno}"})
            elif node.func.attr in INLINE and node.args and isinstance(node.args[0], (ast.Constant, ast.JoinedStr)):
                # a literal pattern written at the call: a regex site with no name to hang a plant on
                lit = ast.unparse(node.args[0])
                out.append({"file": p.name, "name": None, "line": node.lineno, "kind": f"inline:{node.func.attr}",
                            "pattern": lit,
                            # keyed by the pattern's text, not its line: another lane's edit must not rename a site
                            "site": f"{p.name}:{node.func.attr}:{hashlib.sha256(lit.encode('utf-8')).hexdigest()[:10]}"})
            elif node.func.attr in INLINE and node.args:
                # a pattern BUILT at run time (concatenation, re.escape, a variable): still a regex site. Skipping it
                # made "n of N planted" true of literal sites only (pva, RAI-C13 / PVA-D12). Keyed by the expression's
                # text and named by its enclosing function; planted by calling that function (regex_layer.specs_built)
                expr = ast.unparse(node.args[0])
                out.append({"file": p.name, "name": _enclosing(tree, node), "line": node.lineno,
                            "kind": f"built:{node.func.attr}", "pattern": expr,
                            "site": f"{p.name}:{node.func.attr}:built:"
                                    f"{hashlib.sha256(expr.encode('utf-8')).hexdigest()[:10]}"})
    out.sort(key=lambda s: (s["file"], s["line"]))
    seen = {}
    for s in out:                                   # the same literal twice in a file: #2, #3 in reading order
        k = seen[s["site"]] = seen.get(s["site"], 0) + 1
        if k > 1:
            s["site"] += f"#{k}"
    return out


def planted() -> set[str]:
    from regex_layer.specs import INLINE_SPECS, SPECS
    from regex_layer.specs_built import BUILT_SPECS
    return {f"extract.py:{n}" for n in SPECS} | set(INLINE_SPECS) | set(BUILT_SPECS)


if __name__ == "__main__":
    s = sites()
    have = planted()
    print(f"R3 sites with plants: {sum(x['site'] in have for x in s)} of {len(s)}")
    by = {}
    for x in s:
        by.setdefault(x["file"], [0, 0])
        by[x["file"]][1] += 1
        by[x["file"]][0] += x["site"] in have
    for f, (a, b) in sorted(by.items(), key=lambda kv: -kv[1][1]):
        print(f"  {f:28s} {a} of {b}")
