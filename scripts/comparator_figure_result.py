"""The comparator's OWN pooled result when it is printed only in a FIGURE (8 Oct, gap list: melatonin 35691474 Fig X2).

registry/comparator_results.json is what g1_tracker.comparator_result_recorded reads. comparator_league_result.py
types a league-table cell; this records a figure-only pool, and only from a figure the forest reader ACCEPTED for THIS
comparator: two recorded model readings agree on every row and on the pooled row, and the stated model reproduces that
pooled row from the rows (acceptance.methods_reproducing). The value recorded is the AGREED pooled row as printed --
never a recomputation -- with the two record ids, the image sha256 and the reproducing methods beside it. A pool the
meta's own text prints is left to the text readers: this refuses unless the anchor is PRINTED_IN_FIGURE_ONLY.

    python scripts/comparator_figure_result.py melatonin-primary-insomnia-sol
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTP = os.path.join(ROOT, "registry", "comparator_results.json")
READER = os.path.join(ROOT, "registry", "model_proposals", "g1_forest_reader.json")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _f(s):
    return float(str(s).replace("−", "-").replace("–", "-"))


def figure_result(slug, reader, comp_pmid):
    """(entry, None) or (None, why). Pure function of the reader file and the topic's current comparator."""
    r = (reader.get("results") or {}).get(slug) or {}
    if str(r.get("pmid")) != str(comp_pmid):
        return None, f"NO_READ_OF_THIS_COMPARATOR (read {r.get('pmid')}, comparator {comp_pmid})"
    acc = r.get("acceptance") or {}
    if r.get("state") != "ACCEPTED" or acc.get("state", "ACCEPTED") != "ACCEPTED":
        return None, f"FIGURE_NOT_ACCEPTED ({r.get('state')})"
    if not acc.get("methods_reproducing"):
        return None, "POOL_NOT_REPRODUCED"
    if acc.get("pooled_anchor") != "PRINTED_IN_FIGURE_ONLY":
        return None, "POOL_PRINTED_IN_TEXT: type it from the text instead"
    rd = r.get("readings") or {}
    ids = {k: (rd.get(k) or {}).get("record_id") for k in ("codex", "agy")}
    if not all(ids.values()):
        return None, "NOT_TWO_RECORDED_READINGS"
    p = r.get("pooled_agreed") or {}
    try:
        est, lo, hi = _f(p["effect"]), _f(p["lower"]), _f(p["upper"])
    except (KeyError, TypeError, ValueError):
        return None, "POOLED_ROW_NOT_NUMERIC"
    if not lo <= est <= hi:
        return None, "POOLED_ROW_ORDER"
    fig, img = r.get("figure") or {}, r.get("image") or {}
    return {"state": "RECORDED", "comparator_pmid": str(comp_pmid), "outcome": fig.get("caption"),
            "estimate": est, "ci_low": lo, "ci_high": hi, "scale": r.get("measure"),
            "printed": f"{p['effect']} ({p['lower']}, {p['upper']})",
            "location": {"figure": fig.get("fig_id"), "panel": fig.get("panel")},
            "source": img.get("ref"), "sha256": img.get("sha256"), "source_url": img.get("url"),
            "basis": "FIGURE_ONLY_DUAL_READ: the forest reader's ACCEPTED dual-model reading of this comparator's figure",
            "readings": ids, "methods_reproducing": acc.get("methods_reproducing"),
            "recomputed": acc.get("recomputed")}, None


def main(argv):
    out = _j(OUTP) if os.path.exists(OUTP) else {}
    reader = _j(READER)
    rc = 0
    for slug in argv:
        comp = _j(os.path.join(ROOT, "topics", slug + ".json")).get("comparator_pmid")
        e, why = figure_result(slug, reader, comp)
        if e is None:
            print(slug, "REFUSED", why)
            rc = 1
            continue
        out[slug] = e
        print(slug, "RECORDED", e["printed"], e["scale"], e["methods_reproducing"])
    with open(OUTP, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
