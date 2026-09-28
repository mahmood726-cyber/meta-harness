"""REGISTRY-ONLY ENTRIES AND THEIR PUBLICATIONS (docs/registry_publications.json): a registration that the inventory
holds only as a registry record may have a journal publication (NOAC-AF: the edoxaban phase II trials NCT00504556 ->
Weitz 2010, NCT00806624 -> Chung 2011, NCT00829933 -> Yamashita 2012). The link is declared with the publication's held
record, its coverage (ABSTRACT_ONLY / FULL_TEXT_LOCAL) and an identity check (enrolment, regimens, duration), and is put
on the registration's rows for every outcome -- the publication is a REPORT of that registration, never a second trial.

Per outcome the declaration may carry, each with a held witness re-verified here (fail closed):
  zero_events_span (+ zero_events_scope)   the publication states zero events for the compared arms -> REPORTED_ZERO_EVENTS
  held_out_row (+ not_admitted_because)    counts held in the publication, not admitted -> EXTRACTED_NOT_ADMITTED
  statement                                what the held publication does and does not settle (an abstract that is silent
                                           on an outcome never makes it 'not reported')"""
from __future__ import annotations

import json
import os
import re
from typing import Any

PATH = os.path.join("docs", "registry_publications.json")
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _nct(x) -> str:
    m = re.search(r"NCT\d{8}", str(x or ""))
    return m.group(0) if m else ""


def load(slug: str | None, root: str = _ROOT) -> list[dict[str, Any]]:
    p = os.path.join(root, PATH)
    if not slug or not os.path.exists(p):
        return []
    return list(((json.load(open(p, encoding="utf-8")) or {}).get("topics") or {}).get(slug) or [])


def _check_witness(root: str, w: dict[str, Any] | None, what: str) -> None:
    from .comparison_family import _verified
    if not w:
        raise ValueError(f"registry publication {what}: a declared state needs a held witness")
    _verified(root, {"witness": w})


def attach(review: dict[str, Any], slug: str | None, root: str = _ROOT) -> None:
    links = load(slug, root)
    if not links:
        return
    shown = []
    for link in links:
        _check_witness(root, link.get("record_witness"), f"{link.get('registration')} -> PMID {link.get('pmid')}")
        per = link.get("per_outcome") or {}
        for name, st in per.items():
            for key in ("zero_events_span", "held_out_row"):
                if st.get(key):
                    _check_witness(root, st.get("witness"), f"{link['registration']} / {name} / {key}")
                    if key == "zero_events_span" and st["zero_events_span"] != st["witness"]["span"]:
                        raise ValueError(f"{link['registration']} / {name}: the zero-events span is not the witnessed span")
                    if key == "held_out_row":
                        digits = " ".join(st["witness"]["span"].split())
                        for k in ("ai", "n1i", "ci", "n2i"):
                            if st["held_out_row"].get(k) is not None and str(st["held_out_row"][k]) not in digits:
                                raise ValueError(f"{link['registration']} / {name}: held_out_row {k} is not in its witness span")
        pub = {k: link.get(k) for k in ("pmid", "label", "coverage", "identity_check", "design")}
        shown.append({"registration": link["registration"], **pub})
        for o in review.get("outcomes") or []:
            for row in (o.get("trials") or []) + (o.get("declared_absent_trials") or []):
                if _nct(row.get("id")) != link["registration"]:
                    continue
                row["linked_publication"] = pub
                st = per.get(o.get("name")) or {}
                if row in (o.get("trials") or []):
                    continue
                if st.get("zero_events_span"):
                    row["zero_events_span"] = st["zero_events_span"]
                    if st.get("zero_events_scope"):
                        row["zero_events_scope"] = st["zero_events_scope"]
                if st.get("held_out_row"):
                    row["held_out_row"] = dict(st["held_out_row"])
                    row["source_span"] = st["witness"]["span"]
                    row["not_admitted_because"] = st.get("not_admitted_because")
                if st.get("statement"):
                    row["publication_statement"] = st["statement"]
    review["registry_publications"] = shown
