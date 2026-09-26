"""Regex call sites in harness/ whose PATTERN argument is not a plain string literal (built by concatenation, f-string,
join, a variable, ...). These are the sites an inventory keyed on the literal pattern text cannot see.
Usage: python regex_layer/nonliteral_sites.py <repo root>   -> one line per site: file:line function call pattern-expression"""
import ast
import os
import sys

root = sys.argv[1]
FUNCS = {"compile", "search", "match", "fullmatch", "findall", "finditer", "sub", "subn", "split"}
n = 0
for fn in sorted(os.listdir(os.path.join(root, "harness"))):
    if not fn.endswith(".py"):
        continue
    src = open(os.path.join(root, "harness", fn), encoding="utf-8").read()
    tree = ast.parse(src)
    parents = {}
    for node in ast.walk(tree):
        for ch in ast.iter_child_nodes(node):
            parents[ch] = node
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in FUNCS
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "re" and node.args):
            continue
        pat = node.args[0]
        if isinstance(pat, ast.Constant) and isinstance(pat.value, str):
            continue
        fnode = node
        while fnode in parents and not isinstance(fnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fnode = parents[fnode]
        where = fnode.name if isinstance(fnode, (ast.FunctionDef, ast.AsyncFunctionDef)) else "<module>"
        n += 1
        print(f"{fn}:{node.lineno} {where} re.{node.func.attr} {ast.unparse(pat)[:110]}")
print(f"TOTAL {n}")
