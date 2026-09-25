"""Turn a VERIFIED extraction into an adjudication DRAFT for hand review (never written as a ruling by itself).
Only rows whose extraction verifies with no errors are drafted. The draft carries the verified spans as evidence,
the served comparison computed by the verifier, and a typed analysis-set reading:
  ITT_STATED        a bound span names intention-to-treat / all randomised
  OTHER_SET_STATED  a bound span names a different set (mITT, FAS with a condition, per-protocol, safety, available)
  NOT_STATED        no span states the set (the served label is then unsupported, not wrong)
The reviewer (the lane) must set `reviewed_note` before adjudicate.py will accept it."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import verify_records as V
ROOT = V.ROOT
ITT = re.compile(r"intent(?:ion)?[-‐‑–\s]to[-‐‑–\s]treat|\bITT\b|all randomi[sz]ed (participants|patients|subjects)"
                 r"|among (the|all)? ?[\d,  ]+ randomi[sz]ed (participants|patients|subjects)|randomi[sz]ed set", re.I)
RESTRICT = re.compile(r"at least (one|1) (dose|tablet|capsule|injection|infusion)|who (took|received) (at least|any)|≥ ?1"
                      r"|available|who (had|have)|modified|\bmITT\b|treated set|excluded from the analysis|with the exception"
                      r"|non-missing|but the following|exclusions?\b", re.I)
SET_WORDS = re.compile(r"analysis set|population|analy[sz]ed|analys[ie]s|per[- ]protocol|modified|\bmITT\b|available|\bFAS\b|treated set"
                       r"|at least (one|1)|excluded|data from|allocated treatment|intent|\bITT\b|randomi[sz]ed set", re.I)


def set_reading(span):
    """Clause by clause: a clause naming ITT/all-randomised with no restriction IN THAT CLAUSE states ITT (so
    'ITT analysis of 214 ... and per-protocol analysis of 172' is ITT, but 'ITT ... on the available participants' is
    not). A span with no analysis-set vocabulary at all (a bare denominator line) states NO set."""
    if not span:
        return "NOT_STATED"
    clauses = re.split(r";|\band\b(?= (?:a )?per[- ]protocol)|\. ", span)
    # a restriction anywhere restricts the set a following label sentence names ('...non-missing endpoint. Intent-to-
    # treat population.'); only a restriction confined to a separate per-protocol clause leaves an ITT clause standing
    restricted = any(RESTRICT.search(c) and not re.search(r"per[- ]protocol", c, re.I) for c in clauses)
    if not restricted and any(ITT.search(c) for c in clauses):
        return "ITT_STATED"
    if not SET_WORDS.search(span):
        return "NOT_STATED"
    return "OTHER_SET_STATED"


def main(keys):
    for k in keys:
        rec = json.load(open(os.path.join(ROOT, f"evidence/extractions/raw/{k}.json"), encoding="utf-8"))
        pk = json.load(open(os.path.join(ROOT, f"evidence/packets/{k}.json"), encoding="utf-8"))
        v = V.verify(rec, pk)
        if v["errors"]:
            print(k, "NOT DRAFTED: extraction fails verification"); continue
        sc = (v["served_compare"] or {}).get("state")
        ev = {f: rec["fields"][f] for f in V.FIELDS if (rec.get("fields") or {}).get(f)}
        ep = rec.get("entry_population_matches_question") or {}
        if ep.get("span"):
            ev["entry_population_reading"] = {"ref": ep["ref"], "span": ep["span"]}
        d = {"key": k,
             "ruling": {"MATCH": "SERVED_CONFIRMED", "DIFFERS": "NEEDS_HAND_RULING"}.get(sc, "NEEDS_HAND_RULING")
                        if rec.get("verdict") == "BOUND" else "SET_ASIDE",
             "reason": None, "reviewed_note": None,
             "served_compare": v["served_compare"],
             "evidence": ev,
             "typed_estimand": {
                 "analysis_set": {"served_label": V.served_row(pk).get("analysis_set"),
                                  "source_reading": set_reading((ev.get("analysis_set") or {}).get("span")),
                                  "absent_reason": (rec.get("absent_reason") or {}).get("analysis_set")},
                 "treatment_strategy": "bound" if "treatment_strategy" in ev else (rec.get("absent_reason") or {}).get("treatment_strategy"),
                 "follow_up": "bound" if "follow_up" in ev else (rec.get("absent_reason") or {}).get("follow_up")},
             "entry_population": {"extractor_reading": ep.get("value"), "extractor_why": ep.get("why"), "lane_ruling": None},
             "extractor_mismatch_note": rec.get("served_mismatch"),
             "set_aside_reason": rec.get("set_aside_reason")}
        json.dump(d, open(os.path.join(ROOT, f"evidence/adjudication/drafts/{k}.json"), "w", encoding="utf-8", newline="\n"),
                  indent=1, ensure_ascii=False)
        print(k, "drafted", d["ruling"], d["typed_estimand"]["analysis_set"]["source_reading"])


if __name__ == "__main__":
    main(sys.argv[1:])
