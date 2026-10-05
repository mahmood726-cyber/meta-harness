"""RECORDED DUAL SCREEN REVIEW for the G1 search+screen audit: our rule screener (harness.screen, the served decision) vs
a second screener -- a recorded Codex reader (reproducible_ai.model_call_live.call, one trial per call) -- on every
comparator trial our screen decided:
  * ELIGIBLE trials our search identified (INCLUDED or EXCLUDED by our screen), and
  * SCREEN_NAMED trials: those that left the eligible set because our screen excluded them (X1/X2/X3/X-DESIGN/X-DOSE).
Instrument = scripts/model_source_pilot.py's screening task (SCREEN_INSTR, registered criteria, per-axis schema, the
held-record text format); the decision is DERIVED by reproducible_ai.model_source.verify_screening from per-axis
verdicts whose MET / NOT_MET quotes must be found in the held record -- never taken from the model.
Disagreements (RULE_MODEL_DISAGREE) and readings that cannot decide (MODEL_CANNOT_TELL) go to an ADJUDICATOR: a
recorded call to a different model that sees the criteria, the record, the rule's decision with its span and the
reader's verdicts with quotes; its decision is derived and quote-verified the same way.
Cohen's kappa (rule vs reader) is computed on the items where the reader decided (ELIGIBLE / INELIGIBLE); the
undecided are counted beside it. Licence: the prompt carries a record's title, publication types and abstract (or
registry fields) only -- never a full text (reproducible_ai/record_licence.py).

  python scripts/g1_screen_dual_review.py --run [--workers 5] [SLUG ...]   (live; skips items already RAN_OK)
  python scripts/g1_screen_dual_review.py --verify                          (offline: re-derive from the records)
  -> outputs/search_audit/screen_dual_review.json
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproducible_ai import model_source as ms  # noqa: E402

AUDIT = ROOT / "outputs" / "search_audit" / "SEARCH_SCREEN_AUDIT.json"
OUT = ROOT / "outputs" / "search_audit" / "screen_dual_review.json"
REC_DIR = ROOT / ms.RECORD_DIR
READER_MODEL, ADJ_MODEL, EFFORT = "gpt-6-astra", "gpt-5.5", "medium"
CALLER = "scripts/g1_screen_dual_review.py"


def _pilot():
    spec = importlib.util.spec_from_file_location("_mh_pilot", ROOT / "scripts" / "model_source_pilot.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


P = _pilot()

ADJ_INSTR = """You are the ADJUDICATOR between two screeners who disagree about whether one record meets a systematic
review's registered eligibility criteria. Do not run any commands or read any files. Use only the text given here.
Screener A is a rule-based screener; screener B is a reader. Their reasons are shown; neither is presumed right.
Decide each axis (population, intervention, comparator, design) yourself from the RECORD text:
  MET        the record's text states that this criterion is satisfied,
  NOT_MET    the record's text states something that violates this criterion,
  NOT_STATED the record's text does not say enough to decide.
For MET and NOT_MET you MUST give "quote": a short passage copied EXACTLY, character for character, from the RECORD
(not from the screeners' reasons; no ellipses, no paraphrase). For NOT_STATED give "quote": null.
design = a randomised controlled trial of the kind the question asks for. Use item key R1. Return only the JSON object.
"""


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


_MEMBERS = None


def _members():
    """outputs/k_gap/member_records.json at the audit's pinned acq commit: the PubMed records acq fetched for comparator
    members our search never retrieved (the records our screen was run on for the SCREEN_NAMED rows)."""
    global _MEMBERS
    if _MEMBERS is None:
        sys.path.insert(0, str(ROOT / "scripts"))
        import g1_search_screen_audit as A
        d, sha = A._pinned("outputs/k_gap/member_records.json")
        _MEMBERS = ({str(k): dict(v, id=str(k), id_type="pmid") for k, v in (d or {}).items()}, sha)
    return _MEMBERS


def _records(slug):
    r = json.load(open(ROOT / "cache" / slug / "records.json", encoding="utf-8"))
    out = {}
    for x in (r.get("records") or []) + (r.get("ctgov") or []):
        k = str(x.get("id"))
        out[k.upper() if k.upper().startswith("NCT") else k] = x
    return out


def items():
    a = json.load(open(AUDIT, encoding="utf-8"))
    out = []
    for t in a["topics"]:
        recs = _records(t["slug"])
        for r in t["trials"]:
            if r["kind"] == "ELIGIBLE" and r["screen"] in ("INCLUDED", "EXCLUDED"):
                if r["screen"] == "INCLUDED":
                    rid, dec, why = r["screen_include"]["record"], "include", {"rule_id": "INCLUDE"}
                else:
                    e = r["screen_exclusion"]
                    rid, dec, why = e["record"], "exclude", {k: e.get(k) for k in ("rule_id", "reason", "span", "stage")}
            elif r["kind"] == "SCREEN_NAMED":
                mem, msha = _members()
                rid = next((x for x in r["pmids"] + r["ncts"] if x in recs), None)
                if rid is None:
                    rid = next((x for x in r["pmids"] if x in mem), None)
                    if rid is not None:
                        recs = dict(recs, **{rid: mem[rid]})
                        recs["__member_ref__"] = f"outputs/k_gap/member_records.json@acq:{msha[:12]}"
                dec, why = "exclude", {"rule_id": (r.get("named") or {}).get("rule_id"),
                                       "reason": (r.get("named") or {}).get("screen_reason")}
                if rid is None:
                    out.append({"slug": t["slug"], "label": r["label"], "kind": r["kind"], "state": "NO_HELD_RECORD",
                                "rule_decision": dec, "rule": why})
                    continue
            else:
                continue
            rec = recs.get(rid)
            it = {"slug": t["slug"], "label": r["label"], "kind": r["kind"], "record": rid, "rule_decision": dec,
                  "rule": why, "item_id": f"{t['slug']}::{r['label']}::{rid}"}
            if rec is None:
                it["state"] = "NO_HELD_RECORD"
            else:
                ht = P.held_text_screening(rec)
                where = (recs.get("__member_ref__") if rid not in _records(t["slug"]) else f"cache/{t['slug']}/records.json")
                it.update(held_text=ht, held_sha256=_sha(ht.encode("utf-8")),
                          held_ref=f"{where}#{rec.get('id_type')}:{rec.get('id')}")
            out.append(it)
    return out


INSTRUMENT = "v2"   # v1 (screen_dual_review_v1.json): pilot criteria only -- the reader never saw the REGISTERED
                    # exclusion lists, so it judged protocol-excluded populations (CABG, assisted reproduction, eye
                    # disease) against a looser standard than the protocol; v2 states the registered criteria as enforced.


def criteria(slug):
    crit, cd = P.criteria(slug)
    if INSTRUMENT == "v1":
        return crit, cd
    inc = json.load(open(ROOT / "topics" / f"{slug}.json", encoding="utf-8")).get("include") or {}
    extra = []
    if inc.get("population_none"):
        extra.append(f"Population must NOT be (registered exclusions): {inc['population_none']}")
    if inc.get("intervention_none"):
        extra.append(f"Intervention must NOT be (registered exclusions): {inc['intervention_none']}")
    ca = list(inc.get("comparator_any") or []) + list(inc.get("comparator_any_extra") or [])
    if ca:
        extra.append(f"Comparator must be one of (registered): {ca}")
    if inc.get("design_double_blind"):
        extra.append("Design must be double-blind or placebo-controlled (registered)")
    if inc.get("design_none"):
        extra.append(f"Design/context must NOT be (registered): {inc['design_none']}")
    return crit + ("\n" + "\n".join(extra) if extra else ""), cd


def reader_prompt(it):
    crit, cd = criteria(it["slug"])
    body = (P.READER2_HEADER + P.SCREEN_INSTR + "\n=== REGISTERED CRITERIA ===\n" + crit + "\n"
            + f"\n=== RECORD item=R1 ===\n{it['held_text']}\n")
    return body.encode("utf-8"), cd + [{"ref": it["held_ref"], "sha256": it["held_sha256"], "what": "held record"}]


def adj_prompt(it, claim):
    """The reader's per-axis verdicts WITH its quotes (from its claim; the verification keeps verdicts only)."""
    reading = claim if isinstance(claim, dict) else {}
    crit, cd = criteria(it["slug"])
    rule = it["rule"]
    a = (f"decision {it['rule_decision']} (rule {rule.get('rule_id')})" + (f": {rule.get('reason')}" if rule.get("reason") else "")
         + (f" | span: {rule.get('span')}" if rule.get("span") else ""))
    b = "; ".join(f"{ax}: {v['verdict']}" + (f" (quote: {v.get('quote')})" if v.get("quote") else "")
                  for ax, v in (reading.get("axes") or {}).items())
    body = (ADJ_INSTR + "\n=== REGISTERED CRITERIA ===\n" + crit + "\n\n=== SCREENER A ===\n" + a
            + "\n\n=== SCREENER B ===\n" + b + f"\n\n=== RECORD item=R1 ===\n{it['held_text']}\n")
    return body.encode("utf-8"), cd + [{"ref": it["held_ref"], "sha256": it["held_sha256"], "what": "held record"}]


def _have():
    """{prompt sha256: RAN_OK record} over the committed record directory (newest wins)."""
    out = {}
    idx = OUT.with_name("screen_dual_review_records.json")
    known = json.load(open(idx, encoding="utf-8")) if idx.exists() else {}
    for sha, name in known.items():
        p = REC_DIR / name
        if p.exists():
            rec = ms.load_record(p)
            if rec.get("state") == "RAN_OK":
                out[sha] = (name, rec)
    return out, known


def _claim(rec):
    return ms.claim_for_item(ms.extract_claim("screening", ms.replay(rec)), "R1")


def call(prompt, digests, model, purpose):
    from reproducible_ai import model_call_live
    rec = model_call_live.call(prompt, schema=P._schema("screening"), model=model, effort=EFFORT,
                               caller={"file": CALLER, "lane": "search-screen-audit", "line": "call", "purpose": purpose},
                               input_digests=digests)
    path = ms.write_record(rec, REC_DIR)
    return path.name, rec


def kappa(pairs):
    """Cohen's kappa over (a, b) decision pairs in {ELIGIBLE, INELIGIBLE}."""
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    cats = ("ELIGIBLE", "INELIGIBLE")
    pe = sum((sum(a == c for a, _ in pairs) / n) * (sum(b == c for _, b in pairs) / n) for c in cats)
    return None if pe == 1 else round((po - pe) / (1 - pe), 4)


def run(argv, live):
    workers = 5
    if "--workers" in argv:
        workers = int(argv[argv.index("--workers") + 1])
    slugs = [a for a in argv if not a.startswith("--") and not a.isdigit()]
    its = [i for i in items() if not slugs or i["slug"] in slugs]
    have, known = _have()
    callable_ = [i for i in its if "held_text" in i]
    if live:
        todo = []
        for i in callable_:
            pb, dg = reader_prompt(i)
            if _sha(pb) not in have:
                todo.append((i, pb, dg))
        print(f"reader: {len(todo)} of {len(callable_)} items to call (workers {workers})", flush=True)
        with cf.ThreadPoolExecutor(workers) as ex:
            futs = {ex.submit(call, pb, dg, READER_MODEL, f"G1 screen dual review, reader, {i['item_id']}"): (i, pb)
                    for i, pb, dg in todo}
            for f in cf.as_completed(futs):
                i, pb = futs[f]
                try:
                    name, rec = f.result()
                    known[_sha(pb)] = name
                    print(f"  reader {i['item_id']}: {rec['state']}", flush=True)
                except Exception as exc:  # noqa: BLE001 -- reported; the item stays uncalled
                    print(f"  reader {i['item_id']}: FAILED {exc}", flush=True)
        json.dump(known, open(OUT.with_name("screen_dual_review_records.json"), "w", encoding="utf-8"), indent=0)
        have, known = _have()
    rows = []
    for i in its:
        row = {k: i.get(k) for k in ("slug", "label", "kind", "record", "rule_decision", "rule", "item_id", "held_ref",
                                      "held_sha256")}
        if "held_text" not in i:
            rows.append(dict(row, state="NO_HELD_RECORD"))
            continue
        pb, _ = reader_prompt(i)
        hr = have.get(_sha(pb))
        if not hr:
            rows.append(dict(row, state="READER_NOT_CALLED"))
            continue
        claim = _claim(hr[1])
        v = ms.verify_screening(claim, i["held_text"], i["rule_decision"])
        row.update(state="READ", reader_record=hr[0], reader=v, reader_claim=claim)
        rows.append(row)
    # adjudication of disagreements and cannot-tell readings
    need = [r for r in rows if r.get("state") == "READ" and str(r["reader"].get("agreement", "")).startswith(
        ("RULE_MODEL_DISAGREE", "MODEL_CANNOT_TELL"))]
    by_id = {i["item_id"]: i for i in its}
    if live and need:
        todo = []
        for r in need:
            pb, dg = adj_prompt(by_id[r["item_id"]], r["reader_claim"])
            if _sha(pb) not in have:
                todo.append((r, pb, dg))
        print(f"adjudicator: {len(todo)} of {len(need)} to call", flush=True)
        with cf.ThreadPoolExecutor(workers) as ex:
            futs = {ex.submit(call, pb, dg, ADJ_MODEL, f"G1 screen dual review, adjudicator, {r['item_id']}"): (r, pb)
                    for r, pb, dg in todo}
            for f in cf.as_completed(futs):
                r, pb = futs[f]
                try:
                    name, rec = f.result()
                    known[_sha(pb)] = name
                    print(f"  adjudicator {r['item_id']}: {rec['state']}", flush=True)
                except Exception as exc:  # noqa: BLE001
                    print(f"  adjudicator {r['item_id']}: FAILED {exc}", flush=True)
        json.dump(known, open(OUT.with_name("screen_dual_review_records.json"), "w", encoding="utf-8"), indent=0)
        have, known = _have()
    for r in need:
        pb, _ = adj_prompt(by_id[r["item_id"]], r["reader_claim"])
        hr = have.get(_sha(pb))
        if hr:
            r["adjudicator_record"] = hr[0]
            r["adjudicator"] = ms.verify_screening(_claim(hr[1]), by_id[r["item_id"]]["held_text"], r["rule_decision"])
    for r in rows:
        if r.get("state") != "READ":
            continue
        rd = {"include": "ELIGIBLE", "exclude": "INELIGIBLE"}[r["rule_decision"]]
        md = r["reader"].get("model_decision")
        adj = (r.get("adjudicator") or {}).get("model_decision")
        final = rd if md == rd else (adj if adj in ("ELIGIBLE", "INELIGIBLE") else "UNRESOLVED")
        r["final"] = final
        r["screen_error"] = ("FALSE_EXCLUSION" if rd == "INELIGIBLE" and final == "ELIGIBLE" else
                             "FALSE_INCLUSION" if rd == "ELIGIBLE" and final == "INELIGIBLE" else None)
    decided = [({"include": "ELIGIBLE", "exclude": "INELIGIBLE"}[r["rule_decision"]], r["reader"]["model_decision"])
               for r in rows if r.get("state") == "READ" and r["reader"].get("model_decision") in ("ELIGIBLE", "INELIGIBLE")]
    tally = {}
    for r in rows:
        k = r.get("state") if r.get("state") != "READ" else str(r["reader"].get("agreement", "")).split("(")[0]
        tally[k] = tally.get(k, 0) + 1
    out = {"schema": 1, "instrument": INSTRUMENT, "reader_model": READER_MODEL, "adjudicator_model": ADJ_MODEL, "n_items": len(rows),
           "tally": tally, "kappa_rule_vs_reader": {"kappa": kappa(decided), "n_decided": len(decided),
                                                    "n_undecided": sum(1 for r in rows if r.get("state") == "READ") - len(decided)},
           "screen_errors": {k: sum(1 for r in rows if r.get("screen_error") == k) for k in ("FALSE_EXCLUSION", "FALSE_INCLUSION")},
           "unresolved": sum(1 for r in rows if r.get("final") == "UNRESOLVED"), "items": rows}
    json.dump(out, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("n_items", "tally", "kappa_rule_vs_reader", "screen_errors", "unresolved")}))


if __name__ == "__main__":
    a = sys.argv[1:]
    run(a, live="--run" in a)
