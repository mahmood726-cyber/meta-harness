"""Network meta-analysis comparators: network-wide vs DIRECT comparison membership (V1.0.1, denosumab review).

Wei 2023 (Heliyon) is a network meta-analysis: 92 RCTs across all outcomes, 55 RCTs (n = 104 580) in its
vertebral-fracture network, of which only the denosumab-vs-placebo edge is comparable to our trial set. A stated
count from an NMA is a NETWORK count; presenting it as the comparator's k would show "55 vs 1" as 54 missing trials.

cache/<slug>/comparator_network.json holds the counts with verbatim quotes (refused when a quote is not in the held
bytes). Without that file, an NMA comparator still never has a stated count used as its direct k (is_network).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

NMA = re.compile(r"network meta-?analys", re.I)


class NetworkRefused(ValueError):
    pass


def is_network(title: str, abstract: str) -> bool:
    return bool(NMA.search(f"{title or ''} {abstract or ''}"))


def _held_text(root: Path, block: dict) -> str:
    p = root / block["document_ref"]
    if block.get("record_id"):
        recs = json.loads(p.read_text(encoding="utf-8"))
        return next((str(r.get("abstract") or "") for v in recs.values() if isinstance(v, list) for r in v
                     if isinstance(r, dict) and str(r.get("id")) == str(block["record_id"])), "")
    return p.read_text(encoding="utf-8")


def load(root, slug) -> Optional[dict]:
    p = Path(root) / "cache" / slug / "comparator_network.json"
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    if doc.get("design") != "NETWORK_META_ANALYSIS":
        raise NetworkRefused("comparator_network: design must be NETWORK_META_ANALYSIS")
    for key in ("whole_network", "outcome_network"):
        b = doc.get(key)
        if b and b["quote"] not in _held_text(Path(root), b):
            raise NetworkRefused(f"comparator_network: {key} quote not located in {b['document_ref']}")
    d = doc.get("direct_comparison") or {}
    if d.get("k") is None and d.get("state") != "NOT_ENUMERATED":
        raise NetworkRefused("comparator_network: a direct comparison without k must be NOT_ENUMERATED with why")
    return doc


def apply(overlap: dict, network: Optional[dict], nma: bool) -> dict:
    """Move a stated network count out of theirs_k. theirs_k is the DIRECT comparison's k, or says it is not computed."""
    if not nma and not network:
        return overlap
    ov = dict(overlap)
    stated = ov.get("theirs_k")
    direct = (network or {}).get("direct_comparison") or {}
    ov["network"] = {"design": "NETWORK_META_ANALYSIS",
                     "whole_network": (network or {}).get("whole_network"),
                     "outcome_network": (network or {}).get("outcome_network"),
                     "direct_comparison": direct or {"state": "NOT_ENUMERATED",
                                                      "why": "comparator_network.json not held for this topic"},
                     "stated_count_read": ({"value": stated, "source": ov.get("theirs_k_source")}
                                           if isinstance(stated, int) else None)}
    if isinstance(direct.get("k"), int):
        ov["theirs_k"] = direct["k"]
        ov["theirs_k_source"] = f"direct comparison {direct.get('contrast')}: {direct.get('source')}"
    else:
        ov["theirs_k"] = ("not computed: network meta-analysis -- direct "
                          + (direct.get("contrast") or "comparison") + " membership not enumerated; network-wide "
                          "counts are not the k of the direct comparison")  # no quote marks: the gate
        # finds this string verbatim in the served HTML, where an apostrophe is escaped
        ov.pop("theirs_k_source", None)
    return ov


def render(ov: dict) -> str:
    import html
    n = (ov or {}).get("network")
    if not n:
        return ""
    e = lambda s: html.escape(str(s), quote=True)  # noqa: E731
    rows = []
    for key, label in (("whole_network", "Whole network"), ("outcome_network", "Network for this outcome")):
        b = n.get(key)
        if b:
            rows.append(f"<li>{label}: {e(b['k'])} RCTs, n = {e(b['n'])} ({e(b['scope'])}) &mdash; &ldquo;{e(b['quote'])}&rdquo;</li>")
    d = n.get("direct_comparison") or {}
    rows.append(f"<li>Direct comparison ({e(d.get('contrast') or 'our contrast')}): "
                + (f"{e(d['k'])} RCTs" if isinstance(d.get("k"), int) else f"<code>{e(d.get('state'))}</code> &mdash; {e(d.get('why'))}")
                + "</li>")
    return ("<div class='comparator-network'><h5>Comparator is a network meta-analysis</h5><ul>" + "".join(rows)
            + "</ul><p>Only the direct comparison is comparable with our trial set; a network count is never read as "
              "trials missing from ours.</p></div>")
