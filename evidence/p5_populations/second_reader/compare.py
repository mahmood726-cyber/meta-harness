"""Mechanical check of the blind second reading against the ledger.
Every quote must be found verbatim (whitespace collapsed) in the WHOLE document file the reader named -- the same bytes
it was shown -- else the fact is QUOTE_NOT_FOUND (recorded with the quote, never discarded).
Agreement: RECOVERED<->STATED, ESTABLISHED_ABSENT<->STATED_OPPOSITE, UNRESOLVED<->NOT_STATED.
Usage: compare.py <jobs_dir> <out_json> <out_md>"""
import collections, importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LED = json.load(open(os.path.join(HERE, "..", "ledger.json"), encoding="utf-8"))
_spec = importlib.util.spec_from_file_location("make_packets", os.path.join(HERE, "make_packets.py"))
MP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MP)
AGREE = {"RECOVERED": "STATED", "ESTABLISHED_ABSENT": "STATED_OPPOSITE", "UNRESOLVED": "NOT_STATED"}
REG = re.compile(r"\b(?:NCT\s*\d{8}|ISRCTN\s*\d{8}|ACTRN\s*\d{14}|IRCT\d{8,}[A-Z]\d+|ChiCTR[-\w]+|UMIN\d{9}|DRKS\d{8}|EUCTR[-\w]+|\d{4}-\d{6}-\d{2})\b")


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def quote_found(job, q, shown):
    """The quote must be >= 20 characters, in a file the packet LISTED, whose bytes equal the projection re-derived
    from its recorded origin (so a stale or edited file in the job folder cannot count)."""
    name = os.path.basename(q.get("file") or "")
    text = ws(q.get("text") or "")
    return name in shown and len(text) >= 20 and text in ws(shown[name])


def shown_documents(job):
    """{file: text} for the files row.json lists, each re-derived from its origin by make_packets.project and required
    to equal the bytes in the job folder; a mismatch or a missing origin drops the file (and is reported)."""
    row = json.load(open(os.path.join(job, "row.json"), encoding="utf-8"))
    pmid = (re.search(r"PMID (\d+)", row.get("trial") or "") or [None, None])[1]
    shown, problems = {}, []
    for d in row["documents"]:
        fp, _, ptr = d["origin"].partition("#")
        src = MP.origin_file(fp)
        p = os.path.join(job, d["file"])
        if not os.path.exists(src) or not os.path.exists(p):
            problems.append(f"{d['file']}: origin or job file missing")
            continue
        _, text = MP.project(src, ptr, pmid)
        if open(p, encoding="utf-8").read() != text:
            problems.append(f"{d['file']}: job file differs from its re-derived projection")
            continue
        shown[d["file"]] = text
    listed = {d["origin"] for d in row["documents"]}
    dropped = [p for p in MP.row_documents(next(r for r in LED["rows"] if r["key"] == row["key"])) if p not in listed]
    return shown, problems, dropped


def main(jobs, out_json, out_md):
    res, tally, rows_done = [], collections.Counter(), 0
    for r in LED["rows"]:
        job = os.path.join(jobs, r["key"])
        op = os.path.join(job, "out.json")
        got = {}
        shown, problems, dropped = shown_documents(job) if os.path.exists(os.path.join(job, "row.json")) else ({}, ["no row.json"], [])
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
                bad = [q for q in qs if not quote_found(job, q, shown)]
                rec.update(reader=v, quotes=qs, note=g.get("note"), other_trial=bool(g.get("other_trial")),
                           packet_problems=problems, documents_not_shown=dropped)
                if v in ("STATED", "STATED_OPPOSITE") and (not qs or bad):
                    rec["cls"] = "QUOTE_NOT_FOUND"
                    rec["unfound"] = bad or "no quote"
                elif v == "STATED" and f["fact_id"] == "registry_parent" and not any(REG.search(q["text"]) for q in qs):
                    rec["cls"] = "NO_IDENTIFIER_IN_QUOTE"
                elif v == "NOT_STATED" and (problems or dropped):
                    rec["cls"] = "NOT_STATED_ON_AN_INCOMPLETE_PACKET"   # agreement cannot be claimed from a doc not shown
                elif f["state"] in AGREE and v == AGREE[f["state"]]:
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
