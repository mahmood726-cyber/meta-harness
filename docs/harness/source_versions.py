"""SOURCE VERSIONS: a value can match the original article and still be superseded (DOAC-VTE review: the Hokusai-VTE
CSR erratum of 26 Feb 2015 moves recurrent VTE 130 -> 131/4,118 and HR 0.89 -> 0.90; the J-EINSTEIN erratum corrects
some "1.4%" cells and explicitly not another, "calculated by another definition").

A VERSION CHAIN per result: every version (ORIGINAL article, CORRECTION / ERRATUM, CSR / CSR_ERRATUM, REGULATORY
document) is recorded with its source, date, held witness (path + sha256 + verbatim span, or the reason it is not
held) and value, and one GOVERNING decision {state DECIDED | PENDING, version_id, reason}. Nothing is overwritten:
  * a correction applies to the CELLS it lists and to no other -- never a global find-and-replace of a value
    (apply_per_cell refuses a cell the original does not have);
  * a correction that is not held cannot govern (a PENDING decision keeps the original served and SHOWS the chain);
  * a served row whose value equals a version that a DECIDED governing version supersedes is refused
    (VERSION_SUPERSEDED_SERVED), and a declared chain that is not shown on its row is refused (VERSION_CHAIN_UNSHOWN).
Declared in docs/source_versions.json; held witnesses re-hashed, spans required (fail closed).
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from .comparison_family import _verified

PATH = os.path.join("docs", "source_versions.json")
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KINDS = ("ORIGINAL", "CORRECTION", "ERRATUM", "CSR", "CSR_ERRATUM", "REGULATORY")
_VAL_KEYS = ("ai", "n1i", "ci", "n2i", "effect", "ci_low", "ci_high")


def load(root: str, slug: str | None) -> list[dict[str, Any]]:
    p = os.path.join(root, PATH)
    if not slug or not os.path.exists(p):
        return []
    return list(((json.load(open(p, encoding="utf-8")) or {}).get("topics") or {}).get(slug) or [])


def verify_chain(root: str, chain: dict[str, Any]) -> dict[str, Any]:
    """Re-verify every HELD version's witness; a governing version must be held. Returns the chain as shown."""
    ids = set()
    shown = []
    for v in chain.get("versions") or []:
        if v.get("kind") not in KINDS:
            raise ValueError(f"{chain['chain_id']}: unknown version kind {v.get('kind')!r}")
        held = v.get("held")
        if held:
            _verified(root, {"witness": held})
        elif not v.get("not_held_reason"):
            raise ValueError(f"{chain['chain_id']}/{v['version_id']}: a version not held must say why")
        ids.add(v["version_id"])
        shown.append({k: v.get(k) for k in ("version_id", "kind", "date", "source", "value", "cells", "relation",
                                            "not_held_reason")} | {"held": bool(held),
                                                                   **({"span": held["span"]} if held else {})})
    gov = chain.get("governing") or {}
    if gov.get("state") not in ("DECIDED", "PENDING") or gov.get("version_id") not in ids or not gov.get("reason"):
        raise ValueError(f"{chain['chain_id']}: governing decision must name a version, a state and a reason")
    gv = next(v for v in chain["versions"] if v["version_id"] == gov["version_id"])
    if gov["state"] == "DECIDED" and not gv.get("held"):
        raise ValueError(f"{chain['chain_id']}: a version that is not held cannot govern")
    return {"chain_id": chain["chain_id"], "trial_id": chain.get("trial_id"), "outcome": chain.get("outcome"),
            "versions": shown, "governing": gov}


def apply_per_cell(cells: dict[str, Any], corrections: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply corrections cell by cell. A correction names the cells it changes; a cell it does not name is untouched,
    even when it holds the same value (J-EINSTEIN: '1.4%' in Table 3 stays, 'calculated by another definition')."""
    out = dict(cells)
    for c in corrections:
        for cell, new in (c.get("cells") or {}).items():
            if cell not in out:
                raise ValueError(f"correction names a cell the original does not have: {cell!r}")
            out[cell] = new
    return out


def _pid(x) -> str:
    m = re.search(r"(\d{7,8}|NCT\d{8})", str(x or ""))
    return m.group(1) if m else str(x or "")


def _served_value(row: dict[str, Any]) -> dict[str, Any]:
    return {k: row.get(k) for k in _VAL_KEYS if row.get(k) is not None}


def attach(review: dict[str, Any], root: str = _ROOT) -> None:
    """Put each declared chain on its row (pooled or declared-absent) for its outcome; keep them on the review."""
    chains = [verify_chain(root, c) for c in load(root, review.get("slug"))]
    if not chains:
        return
    review["source_versions"] = chains
    for ch in chains:
        for o in review.get("outcomes") or []:
            if o.get("name") != ch["outcome"]:
                continue
            for row in (o.get("trials") or []) + (o.get("declared_absent_trials") or []):
                if _pid(row.get("id")) == _pid(ch["trial_id"]):
                    row["version_chain"] = {"chain_id": ch["chain_id"], "governing": ch["governing"],
                                            "versions": ch["versions"]}


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for ch in review.get("source_versions") or []:
        rows = [(o, r) for o in review.get("outcomes") or [] if o.get("name") == ch["outcome"]
                for r in (o.get("trials") or []) + (o.get("declared_absent_trials") or [])
                if _pid(r.get("id")) == _pid(ch["trial_id"])]
        for o, r in rows:
            if (r.get("version_chain") or {}).get("chain_id") != ch["chain_id"]:
                out.append({"kind": "VERSION_CHAIN_UNSHOWN", "report_id": _pid(ch["trial_id"]),
                            "detail": f"{ch['outcome']}: chain {ch['chain_id']} is not shown on its row"})
            gov = ch["governing"]
            if gov["state"] != "DECIDED" or r not in (o.get("trials") or []):
                continue
            gval = next(v for v in ch["versions"] if v["version_id"] == gov["version_id"]).get("value") or {}
            served = _served_value(r)
            superseded = [v for v in ch["versions"] if v["version_id"] != gov["version_id"] and v.get("value")
                          and all(served.get(k) == v["value"].get(k) for k in v["value"] if k in served)
                          and any(k in served for k in v["value"])]
            if superseded and any(served.get(k) != gval.get(k) for k in gval if k in served):
                out.append({"kind": "VERSION_SUPERSEDED_SERVED", "report_id": _pid(ch["trial_id"]),
                            "detail": f"{ch['outcome']}: served value equals superseded version "
                                      f"{superseded[0]['version_id']}; governing is {gov['version_id']}"})
    return out
