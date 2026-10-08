"""Typed (regex, no model) reader of a comparator's per-trial TABLE (8 Oct, gap list: doac 29795629 Table 1).

A JATS <table> under CC BY is read deterministically: the rows of one named block, one cell per column, events/N per
arm parsed exactly. The rows then meet the forest reader's own acceptance gate (g1_forest_reader.accept): the stated
pooling model, typed from the meta's own text, must reproduce the printed pooled result within rounding. A typed row
prints counts and no per-row effect, so the per-row 'printed effect matches counts' check has nothing to compare; the
count checks that do apply (integers, 0 <= events <= N) are kept, and the pooled reconstruction is the deciding gate.
The result is written as results[slug] in registry/model_proposals/g1_forest_reader.json (the interface
g1_tracker.lane_comparator_rows reads) with provenance TYPED_JATS_TABLE:<jats sha256>; refused is recorded too.

usage: python scripts/g1_typed_table.py doac-vte-recurrence
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_reader as gfr  # noqa: E402

# (slug) -> where the comparator's per-trial table is, which block of it is the topic's, and its columns
TABLES = {
    "doac-vte-recurrence": {
        "pmid": "29795629", "table_id": "pone.0197583.t001", "block": "VTE Studies",
        "caption_has": "Baseline characteristics and corresponding primary efficacy outcomes of the Phase 3 trials",
        "cols": {"label": 0, "t": 3, "c": 5}, "measure": "OR",
        "outcome": "primary efficacy outcome (recurrent VTE and VTE-related death), Table 1 'VTE Studies'",
        "pooled_quote": "OR 0.88, CI 0.75–1.03",
    },
}
_COUNT = re.compile(r"^\s*(\d[\d,]*)\s*/\s*(\d[\d,]*)\s*$")


def _cells(tr):
    return [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip()
            for c in re.findall(r"<t[dh]\b.*?</t[dh]>", tr, re.S)]


def table_rows(xml: str, spec: dict) -> tuple:
    """(rows, problems). Rows of the named block only; a row whose count cells do not parse is a problem, never
    guessed."""
    m = re.search(r'<table-wrap\b[^>]*id="%s".*?</table-wrap>' % re.escape(spec["table_id"]), xml, re.S)
    if not m:
        return [], ["TABLE_NOT_FOUND"]
    t = m.group(0)
    cap = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", (re.search(r"<caption>(.*?)</caption>", t, re.S) or [None, ""])[1]
                                        if re.search(r"<caption>", t) else ""))
    if spec["caption_has"] not in cap:
        return [], ["CAPTION_ANCHOR_NOT_FOUND"]
    rows, probs, inblock = [], [], False
    for tr in re.findall(r"<tr\b.*?</tr>", t, re.S):
        c = _cells(tr)
        if len(c) == 1 or (c and all(not x for x in c[1:])):       # a block heading row ('VTE Studies')
            inblock = c[0] == spec["block"]
            continue
        if not inblock or len(c) <= max(spec["cols"].values()):
            continue
        mt, mc = _COUNT.match(c[spec["cols"]["t"]]), _COUNT.match(c[spec["cols"]["c"]])
        if not (mt and mc):
            probs.append(f"COUNT_CELL_NOT_PARSED:{c[0]}")
            continue
        et, nt, ec, nc = (int(x.replace(",", "")) for x in (*mt.groups(), *mc.groups()))
        if not (0 <= et <= nt and 0 <= ec <= nc):
            probs.append(f"EVENTS_EXCEED_N:{c[0]}")
            continue
        rows.append({"label": c[spec["cols"]["label"]], "events_t": et, "n_t": nt, "events_c": ec, "n_c": nc,
                     "effect": None, "lower": None, "upper": None, "span": " | ".join(c)})
    if not rows and not probs:
        probs.append("BLOCK_NOT_FOUND_OR_EMPTY")
    return rows, probs


def pooled_from_quote(q: str) -> dict | None:
    m = re.search(r"(\d+(?:\.\d+)?)\s*,?\s*(?:95%\s*)?CI\s*(\d+(?:\.\d+)?)\s*[–-]\s*(\d+(?:\.\d+)?)", q)
    return {"effect": m.group(1), "lower": m.group(2), "upper": m.group(3)} if m else None


def judge(slug: str) -> dict:
    spec = TABLES[slug]
    jp = gfr.jats_path(spec["pmid"])
    xml = open(jp, encoding="utf-8").read()
    sha = hashlib.sha256(xml.encode("utf-8")).hexdigest()
    rows, probs = table_rows(xml, spec)
    held = gfr.model_text(spec["pmid"])
    pooled = pooled_from_quote(spec["pooled_quote"]) if spec["pooled_quote"].replace("–", "-") in held.replace("–", "-") \
        else None
    if pooled is None:
        probs.append("POOLED_QUOTE_NOT_IN_META_TEXT")
    model = gfr.stated_model(held, None, measure=spec["measure"])
    # the per-row printed-effect check has nothing to compare for a counts-only typed row (see module doc): accept()
    # runs on the rows with that check satisfied by construction, the reconstruction gate unchanged
    acc = gfr.accept(rows, pooled, model, spec["measure"], held) if pooled and rows else \
        {"state": "REFUSED", "problems": [], "recomputed": {}, "methods_reproducing": [], "pooled_anchor": None}
    acc["problems"] = [p for p in acc["problems"] if not p.startswith("ROW_COUNTS_DO_NOT_GIVE_PRINTED")]
    acc["state"] = "ACCEPTED" if not acc["problems"] else "REFUSED"
    problems = probs + acc["problems"]
    # the gate's allowance includes a half-unit row-rounding extra meant for TRANSCRIBED rows; typed counts carry no
    # row rounding, so how far each reproducing method is from printed rounding alone is recorded beside the verdict
    import k_gap_forest_plot as fp
    margin = {}
    if pooled and acc.get("recomputed"):
        for name, (e, lo, hi) in acc["recomputed"].items():
            margin[name] = {k: round(abs(v - float(pooled[k])), 4) for k, v in (("effect", e), ("lower", lo), ("upper", hi))}
        margin["upper_outside_printed_rounding"] = any(
            margin[n]["upper"] > fp._half_unit(pooled["upper"]) for n in acc.get("methods_reproducing") or [])
    state = "ACCEPTED" if not problems else "REFUSED"
    src = os.path.relpath(jp, ROOT).replace(os.sep, "/")
    sec = [{"meta_pmid": spec["pmid"], "meta_doi": "", "source_digest": sha,
            "location": {"kind": "table", "id": spec["table_id"], "panel": spec["block"], "row_label": r["label"]},
            "provenance": f"TYPED_JATS_TABLE:{sha[:16]}", "trial_label": r["label"], "measure": spec["measure"],
            "outcome_definition": spec["outcome"], "effect": None, "lower": None, "upper": None,
            **{k: r[k] for k in ("events_t", "n_t", "events_c", "n_c")}} for r in rows] if state == "ACCEPTED" else []
    return {"pmid": spec["pmid"], "slug": slug, "role": "comparator", "state": state, "problems": problems,
            "measure": spec["measure"], "stated_model": model, "pooled_agreed": pooled,
            "margin": margin,
            "acceptance": {k: acc.get(k) for k in ("state", "problems", "recomputed", "methods_reproducing",
                                                    "pooled_anchor")},
            "figure": {"fig_id": spec["table_id"], "caption": spec["caption_has"], "panel": spec["block"],
                       "selected_by": "TYPED_JATS_TABLE (g1_typed_table.TABLES)"},
            "typed": {"source": src, "sha256": sha, "rows": rows, "reader": "regex, no model call"},
            "proposed_rows": rows, "secondary_rows": sec, "refused_rows": [],
            "readings": {}, "image": {"ref": src, "sha256": sha, "url": None, "via": "held JATS"}}


def main(argv):
    o = gfr._j(gfr.OUT)
    for slug in argv:
        r = judge(slug)
        gfr.retire_if_other_pmid(o, "results", slug, r["pmid"])
        o["results"][slug] = r
        o.get("skipped", {}).pop(slug, None)
        print(slug, r["state"], r["problems"], r["acceptance"]["recomputed"], "rows", len(r["proposed_rows"]))
    gfr._save(gfr.OUT, o)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
