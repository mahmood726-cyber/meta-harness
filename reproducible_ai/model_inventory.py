"""Where a model is called, and where a model's OUTPUT is read -- over the whole repository, not only the certificate
closure. Read-only: parses tracked Python with ast and reads committed JSON; calls nothing.

Why a second sweep: scripts/audit_model_calls.py classifies a subprocess program only when argv[0] is a string
literal. On 2026-09-24 it reported 0 model calls over all 541 tracked .py files, while two files call codex:
reproducible_ai/model_call_live.py (argv[0] = _codex_exe(), resolved with shutil.which("codex")) and
scripts/outcome_judgments.py (cmd = ["codex", "exec", ...] passed as a variable). It also counts CALLS only; a model's
answer committed to cache/ and read by the build (outcome_judgments.json, locate_judgments.json) is a model in the
served path whether or not the call happens during the build.

  call_sites(root)          every place a model can be reached: a model-client import, a model CLI name used as the
                            head of an argv list (anywhere, not only inside subprocess.run), or shutil.which(<cli>)
  unresolved_subprocess(root) subprocess calls whose program cannot be read statically (listed, never assumed safe)
  model_outputs(root)       committed cache files that carry model provenance ("model" at the top or on a judgment),
                            each RECORDED (every judgment names a record in registry/model_calls) or UNRECORDED
"""
from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

MODEL_CLIS = ("claude", "codex", "agy", "gemini", "ollama", "openai")
MODEL_CLIENTS = ("anthropic", "openai", "google.generativeai", "google.genai", "vertexai", "cohere", "mistralai", "groq",
                 "litellm", "langchain", "transformers", "ollama")
SUBPROCESS_FNS = ("run", "Popen", "check_output", "call", "check_call")
PROVENANCE_KEYS = ("model", "model_id", "judge", "judge_model")


def tracked_python(root: Path) -> list[str]:
    out = subprocess.run(["git", "ls-files", "*.py"], cwd=root, capture_output=True, text=True, check=True).stdout
    return sorted(out.split())


def _is_cli(s) -> bool:
    return isinstance(s, str) and s.strip().lower() in MODEL_CLIS


def _scan(rel: str, src: str) -> tuple[list[tuple], list[tuple]]:
    """(model sites, unresolved subprocess sites) for one file."""
    tree = ast.parse(src, filename=rel)
    sites, unresolved = [], []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [n.name for n in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            for name in names:
                if name in MODEL_CLIENTS or name.split(".")[0] in MODEL_CLIENTS:
                    sites.append((rel, node.lineno, f"import {name}"))
        elif isinstance(node, ast.List) and node.elts:
            # an argv is a list; a tuple of CLI names is a vocabulary (scripts/audit_model_calls.py MODEL_CLIS)
            h = node.elts[0]
            if isinstance(h, ast.Constant) and _is_cli(h.value):
                sites.append((rel, node.lineno, f"argv head {h.value!r}"))
        elif isinstance(node, ast.Call):
            f = node.func
            fname = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if fname == "which" and node.args and isinstance(node.args[0], ast.Constant) and _is_cli(node.args[0].value):
                sites.append((rel, node.lineno, f"shutil.which({node.args[0].value!r})"))
            owner = f.value.id if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) else ""
            if owner == "subprocess" and fname in SUBPROCESS_FNS and node.args:
                a0 = node.args[0]
                head = a0.elts[0] if isinstance(a0, (ast.List, ast.Tuple)) and a0.elts else None
                literal = isinstance(a0, ast.Constant) or isinstance(head, ast.Constant) or \
                    (isinstance(head, ast.Attribute) and head.attr == "executable")      # sys.executable = python
                if not literal:
                    unresolved.append((rel, node.lineno, ast.unparse(a0)[:60]))
    return sites, unresolved


def call_sites(root: Path, files: list[str] | None = None) -> list[tuple]:
    out = []
    for rel in files if files is not None else tracked_python(root):
        out += _scan(rel, (root / rel).read_text(encoding="utf-8", errors="replace"))[0]
    return out


def unresolved_subprocess(root: Path, files: list[str] | None = None) -> list[tuple]:
    out = []
    for rel in files if files is not None else tracked_python(root):
        out += _scan(rel, (root / rel).read_text(encoding="utf-8", errors="replace"))[1]
    return out


def _judgments(doc) -> list[dict]:
    """The provenance-bearing objects in a cache file: the file itself, and any dict nested up to two levels."""
    out = []
    if isinstance(doc, dict):
        if any(k in doc for k in PROVENANCE_KEYS):
            out.append(doc)
        for v in doc.values():
            if isinstance(v, dict):
                if any(k in v for k in PROVENANCE_KEYS):
                    out.append(v)
                for w in v.values():
                    if isinstance(w, dict) and any(k in w for k in PROVENANCE_KEYS):
                        out.append(w)
    return out


def model_outputs(root: Path, record_dir: str = "registry/model_calls", max_bytes: int = 5_000_000) -> list[dict]:
    have = {p.stem for p in (root / record_dir).glob("mc-*.json")}
    out = []
    for p in sorted((root / "cache").glob("*/*.json")):
        if p.stat().st_size > max_bytes:
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError):
            continue
        js = _judgments(doc)
        if not js:
            continue
        recorded = all(str(j.get("record_id") or "") in have for j in js)
        models = sorted({str(j.get(k)) for j in js for k in PROVENANCE_KEYS if j.get(k) is not None})
        out.append({"path": p.relative_to(root).as_posix(), "state": "RECORDED" if recorded else "UNRECORDED",
                    "models_named": models, "provenance_objects": len(js)})
    return out
