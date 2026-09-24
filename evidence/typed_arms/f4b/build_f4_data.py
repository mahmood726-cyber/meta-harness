"""F4B_DATA.json -- evid2's DATA for the F4 schema v1 (SCHEMA-count-observations-v1.md), one entry per held count entry.

For each of the 34 held entries (held_population.json):
  1. evid2's independent typed evidence: the served-row record whose (slug, pmid, outcome, tuple) is the entry's, or a
     record gated from a held-entry extraction (check_typed_arms.check_row on the held job dir);
  2. if that evidence is BOUND, comparator_direction = "<intervention arm> vs <comparator arm>" in the SOURCE's own arm
     names (the form count_observations.names() parses: '<a> vs <b>');
  3. the F4 producer (drive_f4.py, run separately) computes observations with that direction;
  4. observations are SUPPLIED only if the producer bound the entry AND, arm by arm, its (role, events, n) equal
     evid2's (f4b_slot, events, total) -- two independent instruments agreeing. The supplied object is the producer's
     own, byte for byte, because observation_mismatch() demands equality with its re-extraction.
Nothing here edits cache/: this is an overlay for the F4 lane to apply when its code lands.

usage: python build_f4_data.py <held jobs dir> <producer run json (drive_f4 with overlay)> [--overlay-only out.json]"""
import copy, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TA = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(TA, "scripts"))
import check_typed_arms as cta  # noqa: E402

pop = json.load(open(os.path.join(HERE, "held_population.json"), encoding="utf-8"))
served = [json.load(open(p, encoding="utf-8")) for p in glob.glob(os.path.join(TA, "records", "*.json"))]
held_jobs = sys.argv[1]


def core(label):
    return re.sub(r"\s+(group|arm)s?$", "", (label or "").strip(), flags=re.I).strip()


def evidence_for(r):
    pid = r["trial_id"].split()[-1]
    t = [r["served"][k] for k in ("ai", "n1i", "ci", "n2i")]
    for rec in served:
        if rec["slug"] == r["slug"] and re.sub(r"\D", "", str(rec["trial_id"])) == pid and rec["outcome_name"] == r["outcome_name"]:
            e = [a for a in rec["arm_observations"] if a.get("f4b_slot") == "ai/n1i"]
            c = [a for a in rec["arm_observations"] if a.get("f4b_slot") == "ci/n2i"]
            if rec["state"] == "BOUND" and e and c and [e[0]["events"], e[0]["total"], c[0]["events"], c[0]["total"]] == t:
                return "served-row record " + rec["row_id"], rec
    if os.path.isdir(os.path.join(held_jobs, r["row_id"])):
        rec = cta.check_row(r, held_jobs)
        return "held-entry extraction " + r["row_id"], rec
    return None, None


ADJ = json.load(open(os.path.join(HERE, "ADJUDICATIONS.json"), encoding="utf-8"))["rulings"]
out, overlay = {}, {}
for r in pop["rows"]:
    src, rec = evidence_for(r)
    if rec and r["held_key"] in ADJ:
        a = ADJ[r["held_key"]]
        assert a["state"] == "SET_ASIDE", "a ruling may only move an entry away from a number"
        rec = dict(rec, state="SET_ASIDE", reasons=[f"EVID2 RULING (by eye): {a['reason']}"] + rec["reasons"])
    ent = {"held_key": r["held_key"], "outcome": r["outcome_name"], "tuple": r["served"], "provenance": r["provenance"],
           "entry_sha256": r["row_sha256"], "evid2_evidence": src,
           "evid2_state": rec["state"] if rec else "NO_EVIDENCE",
           "evid2_reasons": rec["reasons"] if rec else ["no extraction for this entry"]}
    if rec and rec["state"] == "BOUND":
        e = [a for a in rec["arm_observations"] if a["f4b_slot"] == "ai/n1i"][0]
        c = [a for a in rec["arm_observations"] if a["f4b_slot"] == "ci/n2i"][0]
        ent["comparator_direction"] = f"{core(e['arm_label'])} vs {core(c['arm_label'])}"
        ent["evid2_arms"] = [{"f4b_slot": a["f4b_slot"], "arm_label": a["arm_label"], "events": a["events"], "total": a["total"],
                              "total_basis": a["total_basis"], "events_ownership": a["events_ownership"],
                              "total_ownership": a["total_ownership"],
                              "events_span": (a.get("events_span") or {}).get("text"),
                              "total_span": (a.get("total_span") or {}).get("text"),
                              "document": (a.get("events_span") or {}).get("document")} for a in (e, c)]
        overlay[r["held_key"]] = {"comparator_direction": ent["comparator_direction"]}
    out[r["held_key"]] = ent

if "--overlay-only" in sys.argv:
    json.dump(overlay, open(sys.argv[sys.argv.index("--overlay-only") + 1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(len(overlay), "overlay entries of", len(out))
    sys.exit(0)

run = {x["key"]: x for x in json.load(open(sys.argv[2], encoding="utf-8"))["results"]}
counts = {}
for key, ent in out.items():
    p = run.get(key) or {}
    ent["producer"] = {"state": p.get("state"), "count_binding_state": p.get("count_binding_state"),
                       "reason_code": p.get("reason_code") or p.get("reason_codes"), "reason": (p.get("reasons") or [None])[0]}
    obs = p.get("observations") if p.get("count_binding_state") == "BOUND" else None
    decision = "NO_OBSERVATIONS_SUPPLIED"
    if obs and ent.get("evid2_arms"):
        mine = {("intervention" if a["f4b_slot"] == "ai/n1i" else "comparator"): (a["events"], a["total"]) for a in ent["evid2_arms"]}
        theirs = {o["arm"]["role"]: (o["events"], o["n"]) for o in obs}
        if mine == theirs and len(obs) == 2:
            ent["observations"] = copy.deepcopy(obs)
            decision = "SUPPLIED (producer and evid2 agree on every arm)"
        else:
            decision = f"WITHHELD: producer {theirs} != evid2 {mine}"
    elif obs:
        decision = "WITHHELD: producer bound it but evid2 has no bound evidence to confirm"
    elif ent.get("comparator_direction"):
        decision = "DIRECTION_ONLY: evid2 bound the arms; the producer did not bind with this direction (reason above)"
    ent["decision"] = decision
    counts[decision.split(":")[0].split(" (")[0]] = counts.get(decision.split(":")[0].split(" (")[0], 0) + 1
doc = {"schema": "SCHEMA-count-observations-v1 (F4 repair lane); evid2 supplies DATA only",
       "population": {"ref": pop["ref"], "n": pop["n"], "rule": pop["rule"]},
       "counts": counts, "entries": out}
json.dump(doc, open(os.path.join(HERE, "F4B_DATA.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
print(json.dumps(counts))
