"""WHAT A COMMITTED 'FULL TEXT' ACTUALLY COVERS.

cache/<topic>/ft_<pid>.txt files are PMC downloads. For some articles the publisher does not allow the full text in XML
form, and PMC returns the front matter and the abstract only -- melatonin's ft_12790159.txt (Almeida Montes) says so in
its own bytes. A consumer that treats such a file as the full text writes 'full text scanned: not stated' and 'no SD
found in the full text' about an article whose full text was never seen.

  classify(text)      FULL_TEXT or ABSTRACT_ONLY, with the basis (the publisher's own comment, or JATS with no <body>)
  read(path)          (text, coverage): the text only when it IS a full text; an abstract-only file yields None, so
                      every consumer falls back to 'abstract only' instead of claiming a full-text scan
  coverage_map(slug)  {pid: coverage} for every committed ft_ file of a topic (rendered on the page)
"""
from __future__ import annotations

import os
from typing import Any

FULL_TEXT, ABSTRACT_ONLY = "FULL_TEXT", "ABSTRACT_ONLY"
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DISALLOW = "does not allow downloading of the full text"


def classify(text: str | None) -> dict[str, Any]:
    t = text or ""
    if _DISALLOW in t:
        return {"coverage": ABSTRACT_ONLY, "basis": ("the file's own comment: 'The publisher of this article does not "
                                                     "allow downloading of the full text in XML form.' -- front matter and abstract only")}
    if "<article" in t[:5000] and "<body" not in t:
        return {"coverage": ABSTRACT_ONLY, "basis": "JATS article with front matter only: no <body> element"}
    return {"coverage": FULL_TEXT, "basis": "article body present"}


def read(path: str) -> tuple[str | None, dict[str, Any]]:
    try:
        t = open(path, encoding="utf-8").read()
    except OSError:
        return None, {"coverage": None, "basis": "not held"}
    c = classify(t)
    return (t if c["coverage"] == FULL_TEXT else None), c


def coverage_map(slug: str, root: str = _ROOT) -> dict[str, dict[str, Any]]:
    d = os.path.join(root, "cache", slug)
    out = {}
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            if name.startswith("ft_") and name.endswith(".txt"):
                _t, c = read(os.path.join(d, name))
                out[name[3:-4]] = {**c, "path": f"cache/{slug}/{name}"}
    return out
