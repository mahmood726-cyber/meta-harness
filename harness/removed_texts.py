"""Texts taken OUT of the tree by a signed licence decision (V12-08Q, V13-04Q) must never be written back into cache/.

The record is typed and central: registry/tracked_fulltext_licences.json rows with state REMOVED_FROM_TREE_D8 (V13-04Q), plus
a topic's own cache/<slug>/fulltext_ledger.json rows in that state (V12-08Q). Every tool that WRITES cache/<slug>/ft_<pmid>.*
(scripts/fulltext_cascade.py, scripts/lane_fulltext.py) asks is_removed() first.
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = "REMOVED_FROM_TREE_D8"


def _central(root):
    p = os.path.join(root, "registry", "tracked_fulltext_licences.json")
    if not os.path.exists(p):
        return set()
    rows = (json.load(open(p, encoding="utf-8")) or {}).get("rows") or []
    return {(r.get("slug"), str(r.get("pmid"))) for r in rows if r.get("state") == STATE}


def _ledger(root, slug):
    p = os.path.join(root, "cache", slug, "fulltext_ledger.json")
    if not os.path.exists(p):
        return set()
    rows = (json.load(open(p, encoding="utf-8")) or {}).get("rows") or []
    return {str(r.get("pmid")) for r in rows if r.get("state") == STATE}


def is_removed(slug: str, pmid, root: str | None = None) -> bool:
    root = root or ROOT
    pmid = str(pmid)
    return (slug, pmid) in _central(root) or pmid in _ledger(root, slug)
