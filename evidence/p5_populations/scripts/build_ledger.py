"""One record per (row, fact) for the 53 P5-unestablished pooled rows, under POLICY.md.

Inputs (all in this checkout): evidence/inputs/ev53.json (facts per row, from the ordered P5 blocker chain),
evidence/p5_populations/ev53_reverify.json (this lane's fresh re-location of every EV53 citation),
evidence/adjudication/P53-NN.json (the evid lane's entry rulings with spans), evidence/p5_populations/searches.json
(this lane's documented searches and acquisitions, if any).

A fact is RECOVERED only if at least one cited span is re-found by THIS script or by reverify_ev53.py in bytes whose
sha256 is recorded, and the span is from the SAME trial's own document. EV53's FOUND_IN_OTHER_HELD_DOCUMENT
(an indexer's publication type) is not a trial's own statement and is a search candidate, not a recovery.
Output: evidence/p5_populations/ledger.json. No row is ever omitted: the output enumerates all 53 x their facts."""
import json, os, re, hashlib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
EV = json.load(open(P("evidence", "inputs", "ev53.json"), encoding="utf-8"))
RVD = json.load(open(P("evidence", "p5_populations", "ev53_reverify.json"), encoding="utf-8"))
RV = RVD["citations"]
# the re-verification must be of THESE citations (review 4: an edited ev53.json kept the old verdicts) and must say
# which checkout it read
assert RVD.get("checkout"), "ev53_reverify.json records no checkout"
for _cid, _c in EV["citations"].items():
    _r = RV.get(_cid)
    assert _r is None or (_r.get("span") == _c.get("span") and _r.get("document_ref") == _c.get("document_ref")), \
        f"ev53_reverify.json is stale for {_cid}: re-run reverify_ev53.py"

import importlib.util as _iu
_spec = _iu.spec_from_file_location("textrep", P("evidence", "scripts", "textrep.py"))
textrep = _iu.module_from_spec(_spec); _spec.loader.exec_module(textrep)
SEARCH_PATH = P("evidence", "p5_populations", "searches.json")
SEARCHES = json.load(open(SEARCH_PATH, encoding="utf-8")) if os.path.exists(SEARCH_PATH) else {}
ADJ_PATH = P("evidence", "p5_populations", "entry_adjudications.json")
ENTRY_ADJ = json.load(open(ADJ_PATH, encoding="utf-8")) if os.path.exists(ADJ_PATH) else {}
LOCAL_HELD = os.environ.get("EVID2_HELD", r"C:\mh-lanes\evid2-held")


def refind_adjudicated(adj):
    """Re-find an adjudicated span; returns how it was found, or None. Repo refs: in the bytes (raw or textrep render)
    whose sha256 is recorded. LOCAL_ONLY refs (not redistributable): only when the held copy is present with the
    recorded sha256 -- an absent copy is None (the caller records RECOVERED_LOCAL_UNCHECKED, never RECOVERED). A span of
    fewer than 5 words is None: an empty or one-word span is 'in' any text."""
    import html, re
    ref = adj["ref"]
    sp = (adj.get("span") or "").strip()
    if len(sp.split()) < 5 and len(sp) < 25:   # an empty or one-word span is 'in' any text
        return None
    if ref.startswith("LOCAL_ONLY:"):
        p = os.path.join(LOCAL_HELD, ref.split(":", 1)[1])
        if not os.path.exists(p):
            return None   # absent is NOT re-found: the fact must not reach RECOVERED on the adjudication's word alone
        raw = open(p, "rb").read()
        if hashlib.sha256(raw).hexdigest() != adj["sha256"]:
            return None
        t = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", "", raw.decode("utf-8", errors="replace"))
        t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)))
        return "re-found in the LOCAL_ONLY held copy (sha256 equal)" if adj["span"] in t else None
    sha, text = pointer_text(ref)
    if sha != adj["sha256"]:
        return None
    if text and adj["span"] in text:
        return "re-found in the held bytes"
    try:
        return "re-found in the textrep render of the held bytes" if adj["span"] in textrep.render(ref) else None
    except Exception:
        return None


OWN_REGS = {}
for _c in EV["citations"].values():
    if _c.get("record_id") and re.fullmatch(r"\d+", str(_c["record_id"])):
        OWN_REGS.setdefault(str(_c["record_id"]), set()).update(re.findall(r"NCT\d{8}", _c.get("span") or ""))


def check_population(ev):
    """The population is fixed (POLICY.md): 53 unique rows 1..53, each with >= 1 fact and unique fact ids, equal to
    the53.json by (slug, trial). Called by the main loop on the rows it is about to count (review 4)."""
    _idx = [r["index"] for r in ev["rows"]]
    assert sorted(_idx) == list(range(1, 54)), "the population is rows 1..53, each exactly once"
    assert all(r["facts"] and len({f["fact_id"] for f in r["facts"]}) == len(r["facts"]) for r in ev["rows"]),         "every row carries >= 1 fact, each fact once"
    _T53 = P("evidence", "inputs", "the53.json")
    if os.path.exists(_T53):
        _t = json.load(open(_T53, encoding="utf-8"))
        _trows = _t.get("rows") if isinstance(_t, dict) else _t
        if isinstance(_trows, list) and _trows and isinstance(_trows[0], dict) and "slug" in _trows[0]:
            assert sorted((x["slug"], x.get("trial")) for x in _trows) == sorted((r["slug"], r["trial"]) for r in ev["rows"]),                 "ev53 rows differ from the frozen population the53.json"


def own_document(row, cit):
    """A citation is of the trial's OWN document when its record id is the trial's PMID, or its document/pointer/span
    names the trial's own registration (the row's family NCT or its trial id)."""
    pmid = (re.search(r"PMID (\d+)", row.get("trial") or "") or [None, None])[1]
    if pmid and str(cit.get("record_id") or "") == pmid:
        return True
    ids = {x for x in (row.get("family_id"), (re.search(r"NCT\d{8}", row.get("trial") or "") or [None])[0]) if x}
    # the registrations the trial's OWN report prints (record id = its PMID) are its own too -- a programme reported
    # once over two registrations (CANVAS) has no single family id
    ids |= OWN_REGS.get(pmid, set())
    hay = " ".join(str(cit.get(k) or "") for k in ("document_ref", "span", "logical_ref", "record_id"))
    if any(i in hay for i in ids):
        return True
    ref = (cit.get("document_ref") or "").split("#")
    if len(ref) == 2 and ref[1]:
        _, txt = pointer_text(cit["document_ref"])
        return bool(txt) and any(i in txt for i in ids)
    return False


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


check_population(EV)
rows_out, tally, by_fact = [], collections.Counter(), collections.defaultdict(collections.Counter)
for r in EV["rows"]:
    key, evid_ruling, evid_spans = evid_entry(r["index"])
    facts = []
    for f in r["facts"]:
        ids = list(f.get("evidence_ids") or [])
        if f["semantic_ruling"] == "CONTRADICTS":
            ids = list(f.get("context_or_counterevidence_ids") or []) + ids   # the opposite must be stated by the trial
        cites = [RV.get(e) for e in ids]
        # re-found AND of THIS trial's own document (review 4: any one re-found citation used to do, whatever trial)
        good = [c for c in cites if c and c["state"] in ("REVERIFIED_EXACT", "REVERIFIED_RELOCATED")
                and own_document(r, EV["citations"].get(c["evidence_id"]) or {})]
        rec = {"fact_id": f["fact_id"], "blockers": f.get("satisfies_blockers"), "ev53_classification": f["classification"],
               "ev53_semantic_ruling": f["semantic_ruling"], "ev53_interpretation": f.get("interpretation"),
               "evidence": [{"evidence_id": c["evidence_id"], "document_ref": c["document_ref"], "span": c["span"],
                             "file_sha256_now": c.get("file_sha256_now"), "state": c["state"]} for c in good],
               "state": None, "basis": None, "notes": [],
               # re-found spans of OTHER documents (a review, a reference, another trial): context under POLICY.md, never
               # the fact -- kept visible, never counted
               "context_not_own_document": [{"evidence_id": c["evidence_id"], "document_ref": c["document_ref"],
                                             "span": c["span"]} for c in cites
                                            if c and c["state"] in ("REVERIFIED_EXACT", "REVERIFIED_RELOCATED")
                                            and not own_document(r, EV["citations"].get(c["evidence_id"]) or {})]}
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
            # evid's ruling is a LOCATOR, not the fact: a re-found span proves the words exist, not that they state entry.
            # The blind second reading (2026-09-25) showed one such span (P53-41) did not state it. So the fact is
            # RECOVERED only through evid2's own adjudicated span (entry_adjudications.json), re-found here.
            adj = ENTRY_ADJ.get(key)
            hit = adj and adj.get("verdict") == "STATES" and refind_adjudicated(adj)
            rec["evidence"] += [s for s in evid_spans if s["found"]]
            if hit:
                rec["state"] = "RECOVERED"
                rec["basis"] = ("evid2's adjudicated span states entry (entry_adjudications.json), " + hit + "; evid's span "
                                "kept as the locator. The P5 screen still reads the topic's configured population terms, "
                                "which here name the OUTCOME -- a config defect, recorded, not repaired here")
                rec["evidence"].append({"from": "evid2 entry adjudication", "ref": adj["ref"], "span": adj["span"],
                                        "sha256": adj["sha256"], "why": adj["why"]})
            elif srch and srch.get("result") == "UNRESOLVED":
                rec["state"], rec["basis"], rec["search"] = "UNRESOLVED", srch.get("why"), srch
            elif adj and adj.get("verdict") == "STATES" and adj.get("ref", "").startswith("LOCAL_ONLY:") and \
                    not os.path.exists(os.path.join(LOCAL_HELD, adj["ref"].split(":", 1)[1])):
                rec["state"] = "RECOVERED_LOCAL_UNCHECKED"
                rec["basis"] = ("evid2's adjudicated span is in a LOCAL_ONLY document not present in this checkout, so it "
                                "was not re-found here; NOT counted as RECOVERED")
            else:
                rec["state"], rec["basis"] = "SEARCH_PENDING", "evid's span re-found but not adjudicated by evid2 as stating entry"
            rec["notes"].append("CONFIG_DEFECT: population_any terms describe the outcome, not entry (EV53 MENTIONS_ONLY)")
        elif srch and srch.get("result") in ("RECOVERED", "ESTABLISHED_ABSENT"):
            # a search's evidence is re-found here like any other (review 4: it used to be taken on its word)
            found = [(e, refind_adjudicated(e)) for e in srch.get("evidence") or [] if e.get("ref") and e.get("sha256")]
            ok = [dict(e, refound=how) for e, how in found if how]
            rec["search"] = srch
            rec["evidence"] += ok or (srch.get("evidence") or [])
            if ok and len(ok) == len(srch.get("evidence") or []):
                rec["state"] = srch["result"]
                rec["basis"] = ("found by evid2's documented search (searches.json), every span re-found: "
                                + "; ".join(sorted({h for _, h in found if h})))
            elif any(str(e.get("ref", "")).startswith("LOCAL_ONLY:") for e in srch.get("evidence") or []) and \
                    not any(os.path.exists(os.path.join(LOCAL_HELD, str(e.get("ref", "")).split(":", 1)[-1]))
                            for e in srch.get("evidence") or [] if str(e.get("ref", "")).startswith("LOCAL_ONLY:")):
                rec["state"] = srch["result"] + "_LOCAL_UNCHECKED"
                rec["basis"] = "the search's spans are in LOCAL_ONLY documents not present in this checkout; not counted"
            else:
                rec["state"], rec["basis"] = "SEARCH_EVIDENCE_NOT_REFOUND", "a search span was not re-found in its recorded bytes"
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
