"""Every model call in the pinned path, counted -- or 'none', stated from a sweep rather than assumed.

The pinned path is the certificate's code closure (CERTIFICATE.json#analysis_code_blobs of one served review). Each
listed file is read for (a) an import of a model client or HTTP library, (b) every subprocess invocation and the
program it runs, (c) dynamic imports, and (d) model words. A model CALL is (a) with a model client, or (b) whose
program is a model CLI; everything else is reported with its line so a reader can check the classification.

    python scripts/audit_model_calls.py [--slug glp1-ra-mace-t2d] [--json]

Exit 0 iff model calls in the pinned path == 0. Prints N (paths listed), n present, and the counts by kind.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_CLIENTS = ("anthropic", "openai", "google.generativeai", "google.genai", "vertexai", "cohere", "mistralai", "groq",
                 "litellm", "langchain", "transformers", "ollama")
HTTP_LIBS = ("urllib", "urllib.request", "http.client", "httpx", "requests", "aiohttp", "socket")
MODEL_CLIS = ("claude", "codex", "agy", "gemini", "ollama", "openai")
MODEL_WORDS = re.compile(r"anthropic|openai|claude|gpt|gemini|codex|\bllm\b|messages\.create|chat\.completions|model_call", re.I)


def pinned_paths(slug: str) -> list[str]:
    cert = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "CERTIFICATE.json"), encoding="utf-8"))
    blobs = cert.get("analysis_code_blobs") or {}
    return sorted(blobs) if isinstance(blobs, dict) else sorted(b["path"] for b in blobs)


def _program_of(call: ast.Call) -> str | None:
    """The first element of the argv literal handed to subprocess, or None when it is not a literal."""
    if not call.args:
        return None
    a = call.args[0]
    if isinstance(a, (ast.List, ast.Tuple)) and a.elts:
        first = a.elts[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
        if isinstance(first, ast.Attribute) and first.attr == "executable":
            return "python"
        if isinstance(first, ast.Starred):
            return "<starred>"
    if isinstance(a, ast.Constant) and isinstance(a.value, str):
        return a.value.split()[0]
    return None


def sweep(paths: list[str]) -> dict:
    out = {"paths_listed": len(paths), "paths_present": 0, "model_client_imports": [], "http_imports": [],
           "subprocess_sites": [], "dynamic_imports": [], "model_word_lines": [], "model_calls": []}
    for rel in paths:
        p = os.path.join(ROOT, *rel.split("/"))
        if not os.path.isfile(p):
            continue
        out["paths_present"] += 1
        src = open(p, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src, filename=rel)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [n.name for n in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                for name in names:
                    top = name.split(".")[0]
                    if name in MODEL_CLIENTS or top in MODEL_CLIENTS:
                        out["model_client_imports"].append((rel, node.lineno, name))
                        out["model_calls"].append((rel, node.lineno, f"import {name}"))
                    elif name in HTTP_LIBS or top in HTTP_LIBS:
                        out["http_imports"].append((rel, node.lineno, name))
                    elif top == "importlib":
                        out["dynamic_imports"].append((rel, node.lineno, name))
            elif isinstance(node, ast.Call):
                f = node.func
                dotted = (f.value.id + "." + f.attr) if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) else (f.id if isinstance(f, ast.Name) else "")
                if dotted in ("subprocess.run", "subprocess.Popen", "subprocess.check_output", "subprocess.call", "subprocess.check_call"):
                    prog = _program_of(node)
                    out["subprocess_sites"].append((rel, node.lineno, prog))
                    if prog and os.path.basename(prog).lower().split(".")[0] in MODEL_CLIS:
                        out["model_calls"].append((rel, node.lineno, f"subprocess {prog}"))
                elif dotted in ("importlib.import_module", "__import__"):
                    out["dynamic_imports"].append((rel, node.lineno, dotted))
        for i, line in enumerate(src.splitlines(), 1):
            if MODEL_WORDS.search(line):
                out["model_word_lines"].append((rel, i, line.strip()[:120]))
    out["subprocess_programs"] = sorted({s[2] or "<non-literal>" for s in out["subprocess_sites"]})
    out["subprocess_modules"] = len({s[0] for s in out["subprocess_sites"]})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--slug", default="glp1-ra-mace-t2d")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    paths = pinned_paths(a.slug)
    r = sweep(paths)
    if a.json:
        print(json.dumps(r, indent=1))
    else:
        print(f"pinned path: {r['paths_present']} of {r['paths_listed']} listed paths present (CERTIFICATE.json of {a.slug})")
        print(f"model calls in the pinned path: {len(r['model_calls'])} of {r['paths_present']} files")
        for m in r["model_calls"]:
            print("  MODEL CALL", *m)
        print(f"model-client imports: {len(r['model_client_imports'])}; http imports: {len(r['http_imports'])} "
              f"{[f'{x[0]}:{x[1]} {x[2]}' for x in r['http_imports']]}")
        print(f"subprocess sites: {len(r['subprocess_sites'])} in {r['subprocess_modules']} modules; programs: {r['subprocess_programs']}")
        print(f"dynamic imports: {len(r['dynamic_imports'])} {r['dynamic_imports']}")
        print(f"model-word lines (reported, not calls): {len(r['model_word_lines'])}")
    return 0 if not r["model_calls"] else 1


if __name__ == "__main__":
    sys.exit(main())
