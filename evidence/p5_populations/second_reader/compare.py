"""Mechanical check of the blind second reading against the ledger.
Every quote must be found verbatim (whitespace collapsed) in the WHOLE document file the reader named -- the same bytes
it was shown -- else the fact is QUOTE_NOT_FOUND (recorded with the quote, never discarded).
Agreement: RECOVERED<->STATED, ESTABLISHED_ABSENT<->STATED_OPPOSITE, UNRESOLVED<->NOT_STATED.
Usage: compare.py <jobs_dir> <out_json> <out_md>"""
import collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LED = json.load(open(os.path.join(HERE, "..", "ledger.json"), encoding="utf-8"))
AGREE = {"RECOVERED": "STATED", "ESTABLISHED_ABSENT": "STATED_OPPOSITE", "UNRESOLVED": "NOT_STATED"}
REG = re.compile(r"\b(?:NCT\s*\d{8}|ISRCTN\s*\d{8}|ACTRN\s*\d{14}|IRCT\d{8,}[A-Z]\d+|ChiCTR[-\w]+|UMIN\d{9}|DRKS\d{8}|EUCTR[-\w]+|\d{4}-\d{6}-\d{2})\b")


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def quote_found(job, q):
    name = os.path.basename(q.get("file") or "")
    p = os.path.join(job, name)
    if not name.startswith("doc") or not os.path.exists(p):
        return False
    return ws(q.get("text") or "") != "" and ws(q["text"]) in ws(open(p, encoding="utf-8").read())


def main(jobs, out_json, out_md):
    res, tally, rows_done = [], collections.Counter(), 0
    for r in LED["rows"]:
        job = os.path.join(jobs, r["key"])
        op = os.path.join(job, "out.json")
        got = {}
        if os.path.exists(op):
            try:
                o = json.load(open(op, encoding="utf-8"))
                got = {f.get("fact_id"): f for f in o.get("facts", [])}
                rows_done += 1
            except ValueError:
                got = {}
        for f in r["facts"]:
            g = got.get(f["fact_id"])
            rec = {"key": r["key"], "trial": r["trial"], "fact_id": f["fact_id"], "ledger": f["state"]}
            if g is None:
                rec["cls"] = "NO_READING"
            else:
                v = g.get("verdict")
                qs = g.get("quotes") or []
                bad = [q for q in qs if not quote_found(job, q)]
                rec.update(reader=v, quotes=qs, note=g.get("note"), other_trial=bool(g.get("other_trial")))
                if v in ("STATED", "STATED_OPPOSITE") and (not qs or bad):
                    rec["cls"] = "QUOTE_NOT_FOUND"
                    rec["unfound"] = bad or "no quote"
                elif v == "STATED" and f["fact_id"] == "registry_parent" and not any(REG.search(q["text"]) for q in qs):
                    rec["cls"] = "NO_IDENTIFIER_IN_QUOTE"
                elif v == AGREE.get(f["state"]):
                    rec["cls"] = "AGREE"
                else:
                    rec["cls"] = "DISAGREE"
            tally[rec["cls"]] += 1
            res.append(rec)
    N = len(res)
    doc = {"N_facts": N, "rows_read": rows_done, "N_rows": len(LED["rows"]), "tally": dict(tally), "facts": res}
    json.dump(doc, open(out_json, "w", encoding="utf-8"), indent=1)
    L = ["# Blind second reading of the 53 P5 rows -- mechanical comparison", "",
         f"Rows read: {rows_done} of {len(LED['rows'])}. Facts: {N}.", ""]
    for k in ("AGREE", "DISAGREE", "QUOTE_NOT_FOUND", "NO_IDENTIFIER_IN_QUOTE", "NO_READING"):
        L.append(f"- {k}: {tally.get(k, 0)} of {N}")
    L += ["", "| row | trial | fact | ledger | reader | class |", "|---|---|---|---|---|---|"]
    for x in res:
        if x["cls"] not in ("AGREE", "NO_READING"):
            L.append(f"| {x['key']} | {x['trial']} | {x['fact_id']} | {x['ledger']} | {x.get('reader')} | {x['cls']} |")
    open(out_md, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(dict(tally), f"rows {rows_done} of {len(LED['rows'])}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
