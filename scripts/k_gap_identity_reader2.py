"""INDEPENDENT second reader on the k-gap identity resolver (comparator table unit -> PMID/NCT).

The step-1 audit (outputs/k_gap/IDENTITY_AUDIT.md, 24/25) was labelled by the resolver's own author. This draws a
fresh sample at a seed fixed BEFORE the draw (20260930) from the resolved, drug-specific, confirmed-set rows and
asks a recorded model call whether the comparator's row and the resolved report are the SAME trial.

Gate (deterministic): MATCH / NO_MATCH must quote the comparator row AND the resolved report text verbatim
(whitespace-normalised) -- the same bytes shown. CANNOT_TELL quotes nothing. A NO_MATCH is a candidate resolver
error for adjudication; nothing is changed by this script.

    python scripts/k_gap_identity_reader2.py --run
    python scripts/k_gap_identity_reader2.py --verify
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import model_source as ms  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
PROP = os.path.join(ROOT, "registry", "model_proposals", "k_gap_identity_reader2.json")
REC_DIR = os.path.join(ROOT, ms.RECORD_DIR)
MODEL, EFFORT, SEED, N, BATCH = "gpt-6-astra", "medium", 20260930, 40, 8

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {"items": {
    "type": "array", "items": {"type": "object", "additionalProperties": False,
                               "required": ["item", "verdict", "row_quote", "report_quote"],
                               "properties": {"item": {"type": "string"},
                                              "verdict": {"type": "string", "enum": ["MATCH", "NO_MATCH", "CANNOT_TELL"]},
                                              "row_quote": {"type": ["string", "null"]},
                                              "report_quote": {"type": ["string", "null"]}}}}}}

INSTR = """Each item below pairs (A) one row from a meta-analysis's table of included studies with (B) the publication and
registry record that a program resolved that row to. Decide whether A and B describe the SAME clinical trial.
Do not run commands or read files. Use only the text given.
  MATCH       A and B are the same trial (same trial name / first author + year / design details agree).
  NO_MATCH    A and B are different trials (e.g. different acronym, different drug or population, different year).
  CANNOT_TELL the text does not let you decide.
For MATCH or NO_MATCH give row_quote: a short passage copied exactly from A, and report_quote: a short passage copied
exactly from B, that show why. For CANNOT_TELL set both to null. Answer every item.
"""


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _norm(s):
    return re.sub(r"\s+", " ", (s or "").replace(" ", " ")).strip()


def sample():
    t = _j(os.path.join(OUT, "k_gap_table.json"))
    pop = [r for r in t["trials"] if r["unit_source"] != "REFERENCE_SEED" and r["drug"] != "OTHER_AGENT"
           and r["status"] != "UNRESOLVED" and r["pmids"]]
    if SEED != FIRST_SEED:
        # a re-audit must not re-use the first sample: its NO_MATCHes shaped the current rules, so it is burned
        first = _j(PROP.replace(f".s{SEED}.json", ".json")) if os.path.exists(PROP.replace(f".s{SEED}.json", ".json")) else {}
        burned = {x["item_id"] for x in first.get("rows", [])}      # item_id = slug::label[:40], as built in items()
        pop = [r for r in pop if f"{r['slug']}::{r['label'][:40]}" not in burned]
    rng = random.Random(SEED)
    return pop, rng.sample(pop, min(N, len(pop)))


_STORE = None


def shown_pmid(r):
    """The report the resolver ACTUALLY resolved to -- the thing under audit. Never cited_pmids: when a table's
    xrefs are distrusted, the cited PMID is exactly the link the resolver rejected (Eritsland 1996 was shown DART).
    For an NCT-keyed family, prefer a PMID AACT types RESULT for that NCT over pmids[0], which is merely the oldest
    linked PMID and may be a DERIVED paper that only mentions the NCT (ELIXA was shown a rat study)."""
    global _STORE
    if _STORE is None:
        sp = os.path.join(OUT, "_aact_store.json")
        _STORE = (_j(sp).get("pmid") or {}) if os.path.exists(sp) else {}
    ncts = {n.upper() for n in r.get("ncts") or []}
    for p in r["pmids"]:
        if any(n in ncts and t == "RESULT" for n, t in _STORE.get(p, [])):
            return p
    # AACT types no RESULT reference for the NCT (DELIVER: 48 linked PMIDs, all DERIVED; the oldest is a review): the
    # earliest PMID whose OWN PubMed record links the NCT, typed Randomized Controlled Trial, that is not a design /
    # protocol / secondary-analysis paper. Caches only (pubmed_ncts.json, pubmed_pubtypes.json); else the old fallback.
    nc, pt = _pubmed_caches()
    for p in sorted(r["pmids"], key=lambda x: int(x) if str(x).isdigit() else 10 ** 12):
        # the pubtype cache may lack a PMID whose record we HOLD (WOMAN-2's results report 39461792: the merged identity
        # chain linked an unheld paper ahead of it and selection fell to pmids[0]); the held record is the same fact
        info = pt.get(p) or _held_info(p, r.get("slug"))
        if ((nc.get(p) or "").upper() in ncts and "Randomized Controlled Trial" in (info.get("pubtypes") or [])
                and not NOT_A_MAIN_REPORT.search(info.get("title") or "")
                and not IN_A_NAMED_TRIAL.search(info.get("title") or "")):
            return p
    return r["pmids"][0]


_PM = None
NOT_A_MAIN_REPORT = re.compile(r"\bprotocol\b|rationale|\bdesign\b|statistical analysis plan|baseline characteristics|"
                               r"post[- ]?hoc|secondary analys|subgroup|sub-?study|pre-?specified|exploratory analys|"
                               r"according to|by baseline|insights from|\bpooled analys|participant-level", re.I)


# 'Inflammatory and Cholesterol Risk in the FOURIER Trial': a paper set INSIDE a named trial is a secondary analysis
IN_A_NAMED_TRIAL = re.compile(r"\b(?:in|from) the [A-Z][A-Z0-9-]{2,}(?:[ -][A-Z0-9-]+)? (?:[Tt]rial|[Ss]tudy)\b")


_HELD = {}


def _held_info(pmid, slug=None):
    """{'title', 'pubtypes'} of a PMID from a record WE HOLD (outputs/k_gap/member_records.json, else the topic's pinned
    cache/<slug>/records.json); {} when not held. Held bytes only: no fetch."""
    if "member" not in _HELD:
        mp = os.path.join(OUT, "member_records.json")
        _HELD["member"] = _j(mp) if os.path.exists(mp) else {}
    rec = _HELD["member"].get(str(pmid))
    if rec is None and slug:
        if slug not in _HELD:
            cp = os.path.join(os.path.dirname(os.path.dirname(OUT)), "cache", slug, "records.json")
            _HELD[slug] = {str(x.get("id")): x for x in ((_j(cp).get("records") or []) if os.path.exists(cp) else [])}
        rec = _HELD[slug].get(str(pmid))
    return {"title": rec.get("title"), "pubtypes": rec.get("pubtypes")} if rec else {}


def _pubmed_caches():
    global _PM
    if _PM is None:
        nc_p, pt_p = os.path.join(OUT, "pubmed_ncts.json"), os.path.join(OUT, "pubmed_pubtypes.json")
        _PM = (_j(nc_p) if os.path.exists(nc_p) else {}, _j(pt_p) if os.path.exists(pt_p) else {})
    return _PM


def report_text(r, titles):
    pm = shown_pmid(r)
    study = next((v for v in (r.get("study") or {}).values() if v), {}) or {}
    return (f"PMID {pm}: {titles.get(pm, '(title not held)')}\n"
            f"Registry: {', '.join(r['ncts']) or '(none)'} {study.get('acronym') or ''} {study.get('brief_title') or ''}").strip()


def items():
    from harness import http
    pop, s = sample()
    cp = os.path.join(OUT, "pubmed_titles.json")
    titles = _j(cp) if os.path.exists(cp) else {}
    need = sorted({shown_pmid(r) for r in s} - set(titles))
    if need:
        d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                          {"db": "pubmed", "id": ",".join(need), "retmode": "json"})
        for p in need:
            titles[p] = (d.get("result", {}).get(p) or {}).get("title", "")
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(titles, fh, indent=1, sort_keys=True)
    out = []
    for r in s:
        a = f"{r['label']} | {r['context']}"
        b = report_text(r, titles)
        out.append({"item_id": f"{r['slug']}::{r['label'][:40]}", "slug": r["slug"], "row": a, "report": b,
                    "identity_basis": r["identity_basis"], "pmids": r["pmids"][:3], "ncts": r["ncts"]})
    return len(pop), out


def batches(its):
    out = []
    for k in range(0, len(its), BATCH):
        keyed = [(f"R{n + 1}", i) for n, i in enumerate(its[k:k + BATCH])]
        body = INSTR
        for key, i in keyed:
            body += f"\n=== ITEM {key} ===\n(A) {i['row']}\n(B) {i['report']}\n"
        out.append({"batch": f"b{k // BATCH + 1}", "prompt": body.encode("utf-8"), "keyed": keyed})
    return out


def verify_item(claim, it):
    if not isinstance(claim, dict) or claim.get("verdict") not in ("MATCH", "NO_MATCH", "CANNOT_TELL"):
        return {"state": "VERIFIER_REFUSED", "problems": ["NOT_TYPED"]}
    probs = []
    if claim["verdict"] != "CANNOT_TELL":
        if not claim.get("row_quote") or _norm(claim["row_quote"]) not in _norm(it["row"]):
            probs.append("ROW_QUOTE_NOT_IN_A")
        if not claim.get("report_quote") or _norm(claim["report_quote"]) not in _norm(it["report"]):
            probs.append("REPORT_QUOTE_NOT_IN_B")
    return {"state": "VERIFIER_REFUSED" if probs else "VERIFIER_PASS", "problems": probs, "verdict": claim["verdict"]}


def run_one(b):
    from reproducible_ai import model_call_live
    rec = model_call_live.call(b["prompt"], schema=SCHEMA, model=MODEL, effort=EFFORT,
                               caller={"file": "scripts/k_gap_identity_reader2.py", "line": "run_one",
                                       "purpose": f"k-gap identity reader-2 {b['batch']} (acq/k-gap lane)"},
                               input_digests=[{"ref": "outputs/k_gap/k_gap_table.json + pubmed_titles.json",
                                               "sha256": hashlib.sha256(b["prompt"]).hexdigest(),
                                               "what": "rows and resolved reports shown (inline in the prompt)"}],
                               timeout_s=900)
    ms.write_record(rec, REC_DIR)
    return {"batch": b["batch"], "record_id": rec["record_id"], "state": rec["state"],
            "prompt_sha256": hashlib.sha256(b["prompt"]).hexdigest()}


FIRST_SEED = SEED


def main(argv):
    global SEED, PROP
    if "--seed" in argv:
        # the seed is fixed on the command line BEFORE the draw and written into the output
        SEED = int(argv[argv.index("--seed") + 1])
        PROP = PROP.replace(".json", f".s{SEED}.json")
    npop, its = items()
    bs = batches(its)
    data = _j(PROP) if os.path.exists(PROP) else {}
    runs = data.get("runs", {})
    if "--run" in argv:
        done = {r["prompt_sha256"] for r in runs.values() if r["state"] == "RAN_OK"}
        todo = [b for b in bs if hashlib.sha256(b["prompt"]).hexdigest() not in done]
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            for r in ex.map(run_one, todo):
                runs[r["batch"]] = r
                print(r["batch"], r["state"], r["record_id"], flush=True)
    by_sha = {r["prompt_sha256"]: r for r in runs.values()}
    rows = []
    for b in bs:
        run = by_sha.get(hashlib.sha256(b["prompt"]).hexdigest())
        resp = {}
        if run and run["state"] == "RAN_OK":
            resp = {x["item"]: x for x in json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, run["record_id"] + ".json"))).decode("utf-8")).get("items", [])}
        for key, i in b["keyed"]:
            c = resp.get(key)
            rows.append({**i, "record_id": (run or {}).get("record_id"), "claim": c,
                         "verification": verify_item(c, i) if c else {"state": "NO_ANSWER"}})
    from collections import Counter
    tally = Counter(r["verification"].get("verdict", r["verification"]["state"]) for r in rows
                    if r["verification"]["state"] in ("VERIFIER_PASS",))
    refused = sum(r["verification"]["state"] != "VERIFIER_PASS" for r in rows)
    out = {"seed": SEED, "population": npop, "n": len(its), "passed_gate": dict(tally), "refused_or_missing": refused,
           "runs": runs, "rows": rows}
    with open(PROP, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
    print(json.dumps({k: out[k] for k in ("seed", "population", "n", "passed_gate", "refused_or_missing")}, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
