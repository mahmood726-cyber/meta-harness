"""Outcome-specific RoB 2 PROPOSALS for the 3-point MACE result (HR, effect of assignment) of each GLP-1 trial.
Input: evidence/rob2_glp1/SPEC.json (the lane's hand-written reading: per trial, per domain, a proposed judgement,
the reason, and witnesses given as {ref, start, end} anchors into held sources). Output: one file per trial and
SUMMARY.json with `n of N` domains that carry evidence.

Rules enforced here (each refusal names the trial and domain; nothing is written if any rule fails):
  R1 every judgement is a PROPOSAL awaiting human review -- the status is fixed, never 'final'.
  R2 a domain with no witness can only be NO_EVIDENCE_HELD: missing evidence is never relabelled high (or low) risk.
  R3 a proposed level must come with at least one witness.
  R4 D5 is not proposed 'low' on registry witnesses alone: a registry entry is not by itself proof of
     prespecification.
  R5 D3 (missing OUTCOME data) witnesses must speak to outcome ascertainment (vital status, follow-up, lost,
     withdrew, complete...). A span that only reports stopping treatment is refused here; treatment discontinuation
     is recorded separately under D2_treatment_discontinuation.
Every witness is cut from textrep.render(<held file>) by anchors, asserted verbatim, and sha256-pinned.
  python evidence/rob2_glp1/build_rob2.py"""
import collections, datetime, hashlib, json, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evidence", "scripts"))
import textrep  # noqa: E402

DOMAINS = ("D1_randomisation", "D2_deviations_assignment", "D3_missing_outcome_data", "D4_outcome_measurement",
           "D5_selection_of_reported_result")
LEVELS = {"low", "some_concerns", "high", "NO_EVIDENCE_HELD"}
STATUS = "PROPOSAL_AWAITING_HUMAN_REVIEW"
D3_OUTCOME_WORDS = re.compile(r"vital status|follow[- ]?up|lost to|withdr|complete|ascertain|missing|known", re.I)
_cache = {}


def _render(ref):
    if ref not in _cache:
        _cache[ref] = textrep.render(ref)
    return _cache[ref]


def witness(w):
    t = _render(w["ref"])
    i = t.find(w["start"])
    if i < 0:
        raise ValueError(f"anchor not found in {w['ref']}: {w['start'][:60]!r}")
    j = t.find(w["end"], i)
    if j < 0:
        raise ValueError(f"end anchor not found in {w['ref']}: {w['end'][:60]!r}")
    span = t[i:j + len(w["end"])]
    return {"ref": w["ref"], "sha256": hashlib.sha256(open(os.path.join(ROOT, w["ref"]), "rb").read()).hexdigest(),
            "span": span, "source_kind": w.get("kind", "")}


def check_domain(trial, dom, d, ws):
    level = d.get("proposal")
    if level not in LEVELS:
        return f"{trial} {dom}: proposal {level!r} not in {sorted(LEVELS)}"
    if not ws and level != "NO_EVIDENCE_HELD":
        return f"{trial} {dom}: R2/R3 -- '{level}' proposed with no witness (missing evidence must be NO_EVIDENCE_HELD)"
    if ws and level == "NO_EVIDENCE_HELD":
        return f"{trial} {dom}: witnesses given but proposal is NO_EVIDENCE_HELD"
    if dom.startswith("D5") and level == "low" and ws and all(w["source_kind"] == "registry" for w in ws):
        return f"{trial} {dom}: R4 -- 'low' on registry witnesses alone (a registry entry is not proof of prespecification)"
    if dom.startswith("D3"):
        for w in ws:
            if not D3_OUTCOME_WORDS.search(w["span"]):
                return f"{trial} {dom}: R5 -- witness does not speak to outcome ascertainment (e.g. only treatment or a bare count): {w['span'][:80]!r}"
    return None


def build(spec):
    out, errs, n_ev, N = {}, [], 0, 0
    levels = collections.Counter()
    for trial, t in spec["trials"].items():
        rec = {"object": "ROB2_OUTCOME_PROPOSAL", "trial": trial, "pmid": t["pmid"], "nct": t["nct"],
               "result_assessed": "3-point MACE (CV death, nonfatal MI, nonfatal stroke), hazard ratio, effect of assignment (ITT)",
               "status": STATUS, "domains": {}}
        for dom in DOMAINS:
            N += 1
            d = t["domains"].get(dom) or {"proposal": "NO_EVIDENCE_HELD", "why": "no domain entry in SPEC", "witnesses": []}
            try:
                ws = [witness(w) for w in d.get("witnesses", [])]
            except (ValueError, OSError) as e:
                errs.append(f"{trial} {dom}: {e}"); continue
            e = check_domain(trial, dom, d, ws)
            if e:
                errs.append(e); continue
            n_ev += bool(ws)
            levels[d["proposal"]] += 1
            rec["domains"][dom] = {"status": STATUS, "proposal": d["proposal"], "why": d.get("why", ""),
                                   "signalling": d.get("signalling", {}), "witnesses": ws}
        if len(rec["domains"]) < len(DOMAINS):
            continue   # a refused domain is already in errs; the overall is not computed on a partial record
        td = t.get("D2_treatment_discontinuation")
        if td:
            try:
                rec["D2_treatment_discontinuation"] = {"note": "stopped treatment -- recorded for D2 context; NOT missing outcome data",
                                                        "why": td.get("why", ""), "witnesses": [witness(w) for w in td.get("witnesses", [])]}
            except (ValueError, OSError) as e:
                errs.append(f"{trial} D2_treatment_discontinuation: {e}")
        overall = {"status": STATUS,
                   "proposal": ("NOT_PROPOSED (one or more domains lack evidence)" if any(
                       rec["domains"].get(dm, {}).get("proposal") == "NO_EVIDENCE_HELD" for dm in DOMAINS) else
                                "high" if any(rec["domains"][dm]["proposal"] == "high" for dm in DOMAINS) else
                                "some_concerns" if any(rec["domains"][dm]["proposal"] == "some_concerns" for dm in DOMAINS) else "low"),
                   "rule": "RoB 2 algorithm on the proposals; not computed when any domain lacks evidence"}
        rec["overall"] = overall
        out[trial] = rec
    return out, errs, n_ev, N, levels


def main():
    spec = json.load(open(os.path.join(os.path.dirname(__file__), "SPEC.json"), encoding="utf-8"))
    out, errs, n_ev, N, levels = build(spec)
    if errs:
        print("REFUSED:", *errs, sep="\n  "); return 1
    here = os.path.dirname(__file__)
    for trial, rec in out.items():
        fn = re.sub(r"[^A-Za-z0-9-]+", "_", trial).strip("_") + ".json"
        json.dump(rec, open(os.path.join(here, fn), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    summary = {"made_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "status": STATUS, "population": {"N_trials": len(out), "N_domains": N,
                                                "denominator": "trials in the GLP-1 MACE pool (8 served + FLOW + ELIXA) x 5 RoB 2 domains"},
               "domains_with_evidence": n_ev, "proposals": dict(levels),
               "per_trial": {k: {dm: v["domains"][dm]["proposal"] for dm in DOMAINS} | {"overall": v["overall"]["proposal"]}
                             for k, v in out.items()}}
    json.dump(summary, open(os.path.join(here, "SUMMARY.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(f"domains with evidence: {n_ev} of {N}; proposals: {dict(levels)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
