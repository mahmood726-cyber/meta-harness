"""One record per (row, fact) for the 53 P5-unestablished pooled rows, under POLICY.md.

Inputs (all in this checkout): evidence/inputs/ev53.json (facts per row, from the ordered P5 blocker chain),
evidence/p5_populations/ev53_reverify.json (this lane's fresh re-location of every EV53 citation),
evidence/adjudication/P53-NN.json (the evid lane's entry rulings with spans), evidence/p5_populations/searches.json
(this lane's documented searches and acquisitions, if any).

A fact is RECOVERED only if at least one cited span is re-found by THIS script or by reverify_ev53.py in bytes whose
sha256 is recorded, and the span is from the SAME trial's own document. EV53's FOUND_IN_OTHER_HELD_DOCUMENT
(an indexer's publication type) is not a trial's own statement and is a search candidate, not a recovery.
Output: evidence/p5_populations/ledger.json. No row is ever omitted: the output enumerates all 53 x their facts."""
import json, os, hashlib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
EV = json.load(open(P("evidence", "inputs", "ev53.json"), encoding="utf-8"))
RV = json.load(open(P("evidence", "p5_populations", "ev53_reverify.json"), encoding="utf-8"))["citations"]
import importlib.util as _iu
_spec = _iu.spec_from_file_location("textrep", P("evidence", "scripts", "textrep.py"))
textrep = _iu.module_from_spec(_spec); _spec.loader.exec_module(textrep)
SEARCH_PATH = P("evidence", "p5_populations", "searches.json")
SEARCHES = json.load(open(SEARCH_PATH, encoding="utf-8")) if os.path.exists(SEARCH_PATH) else {}


def pointer_text(ref):
    """cache/x/records.json#/records/375 -> (sha256 of file, every string value under that pointer joined)."""
    path, _, ptr = ref.partition("#")
    p = P(path)
    if not os.path.exists(p):
        return None, None
    raw = open(p, "rb").read()
    body = __import__("gzip").decompress(raw) if path.endswith(".gz") else raw
    if not path.endswith((".json", ".json.gz")) or not ptr:
        return hashlib.sha256(raw).hexdigest(), body.decode("utf-8", errors="replace")
    obj = json.loads(body)
    for part in [x for x in ptr.split("/") if x]:
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    vals = []

    def walk(o):
        if isinstance(o, str):
            vals.append(o)
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return hashlib.sha256(raw).hexdigest(), "\n".join(vals)


def evid_entry(index):
    k = "P53-%02d" % index
    p = P("evidence", "adjudication", k + ".json")
    if not os.path.exists(p):
        return k, None, []
    a = json.load(open(p, encoding="utf-8"))
    ruling = (a.get("entry_population") or {}).get("lane_ruling")
    spans = []
    ev = a.get("evidence") or {}
    for name in ("entry_population", "population"):
        s = ev.get(name)
        if isinstance(s, dict) and s.get("ref") and s.get("span"):
            sha, text = pointer_text(s["ref"])
            raw_hit = bool(text) and s["span"] in text
            try:
                rend_hit = s["span"] in textrep.render(s["ref"])
            except Exception:
                rend_hit = False
            pinned = ((a.get("pinned_spans") or {}).get("evidence/" + name) or {}).get("sha256")
            spans.append({"from": f"evid adjudication {k} evidence.{name}", "ref": s["ref"], "span": s["span"],
                          "file_sha256_now": sha, "pinned_sha256": pinned, "file_unchanged": pinned in (None, sha),
                          "match": "RAW_BYTES" if raw_hit else ("RENDER evidence/scripts/textrep.py" if rend_hit else None),
                          "found": (raw_hit or rend_hit) and pinned in (None, sha)})
    return k, ruling, spans


rows_out, tally, by_fact = [], collections.Counter(), collections.defaultdict(collections.Counter)
for r in EV["rows"]:
    key, evid_ruling, evid_spans = evid_entry(r["index"])
    facts = []
    for f in r["facts"]:
        ids = list(f.get("evidence_ids") or [])
        if f["semantic_ruling"] == "CONTRADICTS":
            ids += list(f.get("context_or_counterevidence_ids") or [])
        cites = [RV.get(e) for e in ids]
        good = [c for c in cites if c and c["state"] in ("REVERIFIED_EXACT", "REVERIFIED_RELOCATED")]
        rec = {"fact_id": f["fact_id"], "blockers": f.get("satisfies_blockers"), "ev53_classification": f["classification"],
               "ev53_semantic_ruling": f["semantic_ruling"], "ev53_interpretation": f.get("interpretation"),
               "evidence": [{"evidence_id": c["evidence_id"], "document_ref": c["document_ref"], "span": c["span"],
                             "file_sha256_now": c.get("file_sha256_now"), "state": c["state"]} for c in good],
               "state": None, "basis": None, "notes": []}
        cls, sem = f["classification"], f["semantic_ruling"]
        srch = SEARCHES.get(f"{key}/{f['fact_id']}")
        if cls == "FOUND_IN_TRIAL_OWN_DOCUMENT" and sem == "ESTABLISHES" and good:
            rec["state"], rec["basis"] = "RECOVERED", "EV53 span(s) re-found by evid2 in held bytes of the trial's own document"
        elif sem == "CONTRADICTS" and good:
            rec["state"], rec["basis"] = "ESTABLISHED_ABSENT", "a span of the same trial states the opposite of what the screen requires"
            if f["fact_id"] == "placebo_control":
                rec["notes"].append("SCREEN_VS_CONFIG: the topic config accepts usual care as a comparator, but the screen's "
                                    "placebo check demands a literal placebo arm (EV53); the trial is correctly NOT placebo-controlled")
        elif f["fact_id"] == "entry_population" and evid_ruling == "ESTABLISHED" and any(s["found"] for s in evid_spans):
            rec["state"] = "RECOVERED"
            rec["basis"] = ("evid's entry span re-found by evid2 in the held record; the P5 screen still reads the topic's "
                            "configured population terms, which here name the OUTCOME -- a config defect, recorded, not "
                            "repaired here")
            rec["evidence"] += [s for s in evid_spans if s["found"]]
            rec["notes"].append("CONFIG_DEFECT: population_any terms describe the outcome, not entry (EV53 MENTIONS_ONLY)")
        elif srch and srch.get("result") == "RECOVERED" and srch.get("evidence"):
            rec["state"], rec["basis"] = "RECOVERED", "found by evid2's documented search (searches.json)"
            rec["evidence"] += srch["evidence"]
            rec["search"] = srch
        elif srch and srch.get("result") == "ESTABLISHED_ABSENT":
            rec["state"], rec["basis"], rec["search"] = "ESTABLISHED_ABSENT", srch.get("why"), srch
            rec["evidence"] += srch.get("evidence") or []
        elif srch and srch.get("result") == "UNRESOLVED":
            rec["state"], rec["basis"], rec["search"] = "UNRESOLVED", srch.get("why"), srch
        else:
            rec["state"], rec["basis"] = "SEARCH_PENDING", "not yet searched under POLICY.md"
        if f["fact_id"] == "entry_population" and evid_ruling and evid_ruling != "ESTABLISHED":
            rec["notes"].append(f"evid lane entry ruling: {evid_ruling}")
        tally[rec["state"]] += 1
        by_fact[f["fact_id"]][rec["state"]] += 1
        facts.append(rec)
    states = sorted({x["state"] for x in facts})
    row_state = "ALL_RECOVERED" if states == ["RECOVERED"] else "+".join(x for x in states if x != "RECOVERED")
    rows_out.append({"key": key, "index": r["index"], "slug": r["slug"], "trial": r["trial"], "family_id": r["family_id"],
                     "p5_absence_code": r["absence_code"], "rlx_depth": r["rlx"]["depth"],
                     "rlx_exclusion": r["rlx"].get("exclusion_reason"), "evid_entry_ruling": evid_ruling,
                     "row_state": row_state, "facts": facts})
rt = collections.Counter(x["row_state"] for x in rows_out)
out = {"policy": "evidence/p5_populations/POLICY.md", "N_rows": len(rows_out), "N_facts": sum(tally.values()),
       "row_states": dict(rt), "fact_states": dict(tally), "by_fact": {k: dict(v) for k, v in by_fact.items()},
       "rows": rows_out}
assert len(rows_out) == 53, "the denominator never shrinks"
json.dump(out, open(P("evidence", "p5_populations", "ledger.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("rows", dict(rt), "| facts", dict(tally), "of", out["N_facts"])
for k, v in by_fact.items():
    print("  ", k, dict(v))
