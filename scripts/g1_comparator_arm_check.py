"""Does a comparator's per-trial row put the arms the right way round? For every comparator row with per-arm counts on a
trial with a registration, the trial's POSTED result for the topic outcome (ClinicalTrials.gov API v2) is the referee:
  CONSISTENT  the row's arms reproduce the posted per-arm figures as printed
  SWAPPED     only the swapped arms reproduce them (sglt2-primary-prevention-hf EMPA-REG: row 95/4687 vs 126/2333;
              posted empagliflozin 2.7% of 4687, placebo 4.1% of 2333)
  UNDECIDED   neither, or the posted outcome / arms cannot be identified unambiguously
Percentages are compared at their printed precision (+-0.05 of a point), counts exactly, denominators must equal the row's.
Network at acquisition only; every response's request and sha256 recorded; replayed offline from
registry/comparator_arm_check.json.

  python scripts/g1_comparator_arm_check.py [SLUG ...]
"""
import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "registry", "comparator_arm_check.json")
API = "https://clinicaltrials.gov/api/v2/studies/{}?fields=resultsSection.outcomeMeasuresModule"
CONTROL = re.compile(r"placebo|usual care|standard (?:of )?care|control|no treatment", re.I)


def fetch(nct):
    u = API.format(nct)
    b = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "meta-harness/1.0"}), timeout=60).read()
    time.sleep(0.4)
    return u, b


def arms(om):
    """(treatment, control) groups -- one each; a pooled 'All <drug>' group is the treatment when several doses are posted."""
    g = {x["id"]: x["title"] for x in om.get("groups") or []}
    ctl = [i for i, t in g.items() if CONTROL.search(t)]
    trt = [i for i, t in g.items() if i not in ctl]
    if len(trt) > 1:
        allg = [i for i in trt if re.match(r"\s*(all|total|pooled|combined)\b", g[i], re.I)]
        trt = allg if len(allg) == 1 else trt
    return (trt[0], ctl[0], g) if len(trt) == 1 and len(ctl) == 1 else (None, None, g)


def judge(row, om):
    t, c, g = arms(om)
    if not t:
        return "UNDECIDED", "posted arms not identifiable as one treatment and one control group"
    den = {d["groupId"]: int(float(d["value"])) for x in om.get("denoms") or [] for d in x.get("counts") or []
           if str(d.get("value", "")).replace(".", "").isdigit()}
    val = {m["groupId"]: m.get("value") for cl in om.get("classes") or [] for cat in cl.get("categories") or []
           for m in cat.get("measurements") or []}
    if t not in val or c not in val or t not in den or c not in den:
        return "UNDECIDED", "posted values or denominators missing"
    pct = "percent" in (om.get("unitOfMeasure") or "").lower()

    def ok(e, n, gid):
        if den[gid] != n:
            return False
        try:
            v = float(val[gid])
        except ValueError:
            return False
        return abs(100 * e / n - v) <= 0.05 + 1e-9 if pct else int(v) == e
    a, n1, b, n2 = row["events_t"], row["n_t"], row["events_c"], row["n_c"]
    direct = ok(a, n1, t) and ok(b, n2, c)
    # swapped: the row's 'treatment' events belong to the posted control arm (denominators stay with their arms)
    swapped = den[t] == n1 and den[c] == n2 and (ok(b, n1, t) if pct else int(float(val[t])) == b) and \
        (ok(a, n2, c) if pct else int(float(val[c])) == a)
    posted = f"{g[t]} {val[t]}{'%' if pct else ''} of {den[t]}; {g[c]} {val[c]}{'%' if pct else ''} of {den[c]}"
    if direct:
        return "CONSISTENT", posted
    if swapped:
        return "SWAPPED", posted
    return "UNDECIDED", posted


def main(argv):
    import g1_tracker as gt
    T = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "k_gap_table.json"), encoding="utf-8"))
    ncts = {(t["slug"], t["label"][:60]): [n for n in (t.get("ncts") or []) if str(n).startswith("NCT")] for t in T["trials"]}
    prev = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"rows": {}}
    # a trial the comparator table holds no NCT for: the registration its OWN held record states (EMPA-REG 26378978)
    mem = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "member_records.json"), encoding="utf-8"))
    rec_nct = {str(v.get("id")): v.get("nct") for v in mem.values() if str(v.get("nct") or "").startswith("NCT")}
    d = os.path.join(ROOT, "outputs", "k_gap", "g1")
    slugs = [a for a in argv if not a.startswith("--")] or [f[:-5] for f in sorted(os.listdir(d)) if f.endswith(".json")]
    for slug in slugs:
        o = json.load(open(os.path.join(d, f"{slug}.json"), encoding="utf-8"))
        cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
        po = cfg.get("primary_outcome") or {}
        name, kws = po.get("name") or "", [k.lower() for k in po.get("keywords") or [] if k]
        for x in o.get("trials") or []:
            cr = x.get("comparator_row") or {}
            if None in (cr.get("events_t"), cr.get("n_t"), cr.get("events_c"), cr.get("n_c")):
                continue
            fam = str(x.get("family") or "").replace("PMID ", "")
            own = [str(rec_nct[fam])] if not ncts.get((slug, x["label"])) and rec_nct.get(fam) else []
            for nct in (ncts.get((slug, x["label"])) or own)[:1]:
                key = f"{slug}::{x['label']}"
                try:
                    u, b = fetch(nct)
                except Exception as exc:  # noqa: BLE001 -- a failed request says nothing about the row
                    prev["rows"][key] = {"nct": nct, "state": "FETCH_FAILED", "why": str(exc)[:120]}
                    continue
                js = json.loads(b.decode("utf-8") or "{}")
                oms = ((js.get("resultsSection") or {}).get("outcomeMeasuresModule") or {}).get("outcomeMeasures") or []
                cand = [om for om in oms if (gt._name_words(name) and gt._name_words(name) <= gt._name_words(om.get("title")))
                        or any(k in (om.get("title") or "").lower() for k in kws)]
                res = [(om.get("title"), *judge(cr, om)) for om in cand]
                states = {r[1] for r in res}
                state = ("NO_POSTED_OUTCOME" if not res else "SWAPPED" if states == {"SWAPPED"} else
                         "CONSISTENT" if "CONSISTENT" in states and "SWAPPED" not in states else "UNDECIDED")
                prev["rows"][key] = {"nct": nct, "state": state, "row": {k: cr[k] for k in ("events_t", "n_t", "events_c", "n_c")},
                                     "outcomes": [{"title": t_, "verdict": v, "posted": p} for t_, v, p in res],
                                     "request": u, "response_sha256": hashlib.sha256(b).hexdigest(),
                                     "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(prev, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    from collections import Counter
    print(Counter(v["state"] for v in prev["rows"].values()))
    for k, v in prev["rows"].items():
        if v["state"] == "SWAPPED":
            print("SWAPPED", k, v["row"], [o_["posted"] for o_ in v["outcomes"]])


if __name__ == "__main__":
    main(sys.argv[1:])
