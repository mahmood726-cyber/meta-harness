"""Source-derived 16 Oct item rulings; provenance is not a publishing signature."""
import hashlib
import json
import math
from pathlib import Path
from scripts import m2_pretriage as pre

ROOT = Path(__file__).resolve().parents[1]
PRE = "outputs/m2_pretriage/ncsrc-2026-10-16/pretriage.json"
PROVENANCE = "registry/v15c_dispatch_rulings_2026-10-16.json"
STATE = "DECIDED_BY_DISPATCH_ON_DELEGATION"
BASIS = "Dispatch relay, 16 Oct, item-by-item ruling on Mahmood's delegation"
# Identifiers are the item scope explicitly supplied by Dispatch, not research outputs.
IDS = ("PMID 37025256", "PMID 31109201", "NCT02422186", "NCT02417064", "NCT04320615", "NCT04403685")
REFERENCE = "Cochrane Handbook 6.5.2.10, Table 6.5.a"
URL = "https://training.cochrane.org/handbook/current/chapter-06#section-6-5-2-10"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf8"))


def conversion(row):
    path, nct = row["source_ref"].split("#ctgov_results/")
    measures = read(path)["ctgov_results"][nct]
    candidates = [m for m in measures if m.get("type") == "PRIMARY" and m.get("paramType") == "MEAN"
                  and m.get("dispersionType") == "Standard Deviation" and "Day 28" in m.get("timeFrame", "")
                  and "MADRS" in m.get("title", "")
                  and m.get("title") == row["served_source"].split(" || ")[0]]
    if len(candidates) != 1:
        raise ValueError("R4: primary Day-28 MADRS arm table is not unique")
    m = candidates[0]
    ms = m["classes"][0]["categories"][0]["measurements"]
    ns = m["denoms"][0]["counts"]
    inputs = []
    for g in m["groups"]:
        values = [x for x in ms if x["groupId"] == g["id"]]
        counts = [x for x in ns if x["groupId"] == g["id"]]
        if len(values) != 1 or len(counts) != 1:
            raise ValueError("R4: ambiguous group measurements")
        inputs.append(dict(group_id=g["id"], label=g["title"], mean=float(values[0]["value"]),
                           sd=float(values[0]["spread"]), n=int(counts[0]["value"])))
    active = [a for a in inputs if "esketamine" in a["label"].lower()]
    control = [a for a in inputs if "placebo" in a["label"].lower()]
    if len(active) != 2 or len(control) != 1 or len(inputs) != 3:
        raise ValueError("R4: expected two esketamine doses and one placebo")
    a, b = active
    c = control[0]
    n = a["n"] + b["n"]
    mean = (a["n"] * a["mean"] + b["n"] * b["mean"]) / n
    sd = math.sqrt(((a["n"]-1)*a["sd"]**2 + (b["n"]-1)*b["sd"]**2
                    + a["n"]*b["n"]/n*(a["mean"]-b["mean"])**2)/(n-1))
    output = dict(mean1=mean, sd1=sd, nc1=n, mean2=c["mean"], sd2=c["sd"], nc2=c["n"])
    if any(abs(output[k]-row["served"][k]) > 1e-9 for k in output):
        raise ValueError("R4: served tuple is not the declared conversion")
    return dict(reference=REFERENCE, reference_url=URL, source_ref=row["source_ref"],
                inputs=inputs, output=output,
                formula="N=nA+nB; M=(nA*mA+nB*mB)/N; SD=sqrt(((nA-1)*sA^2+(nB-1)*sB^2+nA*nB/N*(mA-mB)^2)/(N-1))",
                source_span=json.dumps(m, ensure_ascii=False, sort_keys=True, indent=2))


def apply(rows):
    rereads = read(PRE)
    if tuple(r["id"] for r in rereads) != IDS:
        raise ValueError("Dispatch item order/identity differs from the six recorded rereads")
    keyed = {(r["slug"], r["outcome"], r["id"]): r for r in rows}
    for i, r in enumerate(rereads, 1):
        source = pre.open_source(r)
        if source is None or source[1] != r["source_ref"] or hashlib.sha256(source[0].encode("utf8")).hexdigest() != r["source_sha256"]:
            raise ValueError(f"R{i}: held source identity/hash differs from recorded reread")
        item = dict(item_id=f"R{i}", state=STATE, basis=BASIS, by="Dispatch", provenance_file=PROVENANCE)
        d = {k: r.get(k) for k in ("slug","outcome","id","label","primary","served","source_ref","source_sha256")}
        d.update(ruling=item, readers={k:r.get(k) for k in ("codex_record","agy_record","adjudicator_record","state")})
        if i <= 3:
            proposal = r["proposal"]
            if proposal["decision"] != "BIND" or proposal["span"] not in source[0] or not source.admissible:
                raise ValueError(f"R{i}: absent or inadmissible binding")
            if any(proposal["numbers"].get(k) != v for k,v in r["served"].items()):
                raise ValueError(f"R{i}: binding differs from served tuple")
            d.update(decision="ADMIT", **{"class":"BIND_CONFIRMS_SERVED"}, span=proposal["span"],
                     basis="Dispatch item ruling: admit the CT.gov posted-results raw change-score binding")
        elif i == 4:
            c = conversion(r)
            d.update(decision="ADMIT", **{"class":"DECLARED_CONVERSION"}, declared_conversion=c,
                     span=c["source_span"], basis="Dispatch item ruling: declared arm-combination conversion; " + REFERENCE)
        else:
            if source.admissible or r["state"] != "NOT_ADMISSIBLE_LICENCE" or source.licence_statement != r["licence_statement"]:
                raise ValueError(f"R{i}: licence refusal does not match held source")
            d.update(decision="REFUSE", kind="licence", **{"class":"NOT_ADMISSIBLE_LICENCE"},
                     basis=r["why"], licence_class=r["licence_class"], licence_statement=r["licence_statement"])
        keyed[(r["slug"],r["outcome"],r["id"])] = d
    touched = sorted({(r["slug"],r["outcome"]) for r in keyed.values() if r["decision"]=="REFUSE"
                      and r.get("class")=="NOT_ADMISSIBLE_LICENCE" and r.get("kind")!="refused_on_evidence"})
    expected = sorted({(r["slug"],r["outcome"]) for r in rereads[4:]})
    if touched != expected:
        raise ValueError(f"STOP: licence rule unexpected blast radius: {touched}")
    return list(keyed.values())


def provenance(rows):
    items = {r["ruling"]["item_id"]: dict(r["ruling"], trial_id=r["id"], decision=r["decision"],
             source_ref=r["source_ref"], source_sha256=r["source_sha256"]) for r in rows if r.get("ruling")}
    notices = read("docs/result_changes.json")["notices"]
    ns = [n for n in notices if n["slug"]=="dpp4-mace-t2d" and n["outcome"]=="3-point major adverse cardiovascular events"
          and "PMID 26052984" in n.get("left_pool",[])]
    if len(ns) != 1:
        raise ValueError("V6-01: expected one TECOS removal notice")
    n = ns[0]
    from harness.result_changes import conclusion_changed
    if conclusion_changed(n["before"],n["after"],"HR"):
        raise ValueError("V6-01: conclusion changed")
    items["V6-01"] = dict(item_id="V6-01", state=STATE, basis=BASIS, by="Dispatch", decision="ACKNOWLEDGE",
                         before=n["before"], after=n["after"], conclusion_changed=False,
                         notice_ref="docs/result_changes.json", notice_when_utc=n["when_utc"],
                         reviewer_countersignature={"state":"OPEN"})
    return dict(pretriage=PRE, pretriage_sha256=hashlib.sha256((ROOT/PRE).read_bytes()).hexdigest(),
                role="Item ruling provenance only; never a publishing countersignature", items=items)
