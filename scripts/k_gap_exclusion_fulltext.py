"""Resolve the exclusion audit's INSUFFICIENT_RECORD items with the trial's FULL TEXT (regex first, reader second).

scripts/k_gap_exclusion_audit.py leaves an exclusion INSUFFICIENT_RECORD when the abstract lacks the fact the rule needs
(blinding, comparator, design, population). For each such item:
  1. fetch the PMC open-access full text through the harness fetcher (outputs/k_gap/_ft, sha256 in fulltext_index.json);
     no OA full text -> stays INSUFFICIENT_RECORD (reason NO_OA_FULLTEXT)
  2. re-run the SAME deterministic classifier with the full text appended to the record (regex / typed)
  3. only an item still insufficient goes to the RECORDED screening reader -- scripts/model_source_pilot.py's screening
     instrument and reproducible_ai.model_source.verify_screening (per-axis MET / NOT_MET / NOT_STATED, each MET/NOT_MET
     quoting the held text verbatim) -- on the full-text record. Records: evidence/model_calls/exclusion_audit/.
Nothing changes a screening decision; the output is a classification of each exclusion claim.

    python scripts/k_gap_exclusion_fulltext.py [--run]   -> outputs/k_gap/exclusion_fulltext.json
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import importlib.util
import io
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
import k_gap_counterfactual as cfm  # noqa: E402
import k_gap_exclusion_audit as ea  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "exclusion_audit")
RUNS = os.path.join(OUT, "exclusion_fulltext_runs.json")
MODEL, EFFORT = "gpt-6-astra", "medium"
FT_CAP = 60000          # the held text is this prefix of the full text; the reader and the verifier see the SAME bytes


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _pilot():
    spec = importlib.util.spec_from_file_location("model_source_pilot", os.path.join(ROOT, "scripts", "model_source_pilot.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def items(run):
    ea.load_reader()
    audit = _j(os.path.join(OUT, "exclusion_audit.json"))
    pop = {(it["slug"], it["pmid"]): it for it in ea.population()}
    out = []
    for row in audit["rows"]:
        if row["class"] != "INSUFFICIENT_RECORD":
            continue
        it = pop.get((row["slug"], row["pmid"]))
        rec = (it or {}).get("rec")
        ft = cfm.pmc_fulltext_cached(row["pmid"], offline=not run) if row["pmid"] else ""
        ft_src = "PMC_OA" if ft else None
        if not ft and (rec or {}).get("doi"):
            # second legitimate open route: Unpaywall's OA copy as typed text (PDF text layer / HTML), never OCR
            from kgap import k_gap
            u = k_gap.unpaywall_text(rec["doi"], os.path.join(OUT, "_upw"), os.path.join(OUT, "unpaywall_text_index.json"),
                                     offline=not run)
            ft = u.get("text") or ""
            ft_src = "UNPAYWALL_OA" if ft else None
        out.append({"slug": row["slug"], "pmid": row["pmid"], "label": row["label"], "rule_id": row["rule_id"],
                    "subclass_before": row["subclass"], "rec": rec, "fulltext": (ft or "")[:FT_CAP],
                    "fulltext_source": ft_src})
    return out


def reader_prompt(pilot, it, rec_ft):
    crit, cd = pilot.criteria(it["slug"])
    held = pilot.held_text_screening(rec_ft)
    body = pilot.SCREEN_INSTR + "\n=== REGISTERED CRITERIA ===\n" + crit + "\n" + f"\n=== RECORD item=R1 ===\n{held}\n"
    return body.encode("utf-8"), held, cd


def run_reader(args):
    from reproducible_ai import model_call_live
    pilot, it, p, held, cd = args
    rec = model_call_live.call(p, schema=pilot._schema("screening_excluded"), model=MODEL, effort=EFFORT,
                               caller={"file": "scripts/k_gap_exclusion_fulltext.py", "line": "run_reader",
                                       "purpose": f"exclusion audit full-text reader {it['slug']} PMID {it['pmid']} (acq/k-gap lane)"},
                               input_digests=cd + [{"ref": f"PMID {it['pmid']} record + PMC OA full text (first {FT_CAP} chars)",
                                                    "sha256": hashlib.sha256(held.encode("utf-8")).hexdigest(),
                                                    "what": "held record quoted by the item"}], timeout_s=1500)
    ms.write_record(rec, REC_DIR)
    return f"{it['slug']}::{it['pmid']}", {"record_id": rec["record_id"], "state": rec["state"],
                                           "prompt_sha256": hashlib.sha256(p).hexdigest()}


def main(argv):
    run = "--run" in argv
    pilot = _pilot()
    runs = _j(RUNS) if os.path.exists(RUNS) else {}
    its = items(run)
    rows, todo = [], []
    for it in its:
        key = f"{it['slug']}::{it['pmid']}"
        if not it["fulltext"]:
            rows.append({**{k: it[k] for k in ("slug", "pmid", "label", "rule_id", "subclass_before")},
                         "fulltext": "NO_OA_FULLTEXT", "class_after": "INSUFFICIENT_RECORD", "how": None})
            continue
        rec_ft = dict(it["rec"] or {}, abstract=((it["rec"] or {}).get("abstract") or "") + "\n\n" + it["fulltext"])
        cls, sub, base = ea.classify(rec_ft, ea._cfg(it["slug"]), decide_rec=it["rec"] or {})  # regex first, full text as evidence
        if cls != "INSUFFICIENT_RECORD":
            sp = dict((base or {}).get("span") or {}) or None
            if sp and sp.get("text") and sp["text"] not in ((it["rec"] or {}).get("abstract") or ""):
                # the words are the FULL TEXT's, not the record's: say so, with the text's digest, so the tracker checks
                # the span against the held full text (span_is_verbatim field 'fulltext')
                sp.update(field="fulltext", sha256=hashlib.sha256(it["fulltext"].encode("utf-8")).hexdigest(),
                          chars=len(it["fulltext"]))                 # the FT_CAP prefix the stage read
            rows.append({**{k: it[k] for k in ("slug", "pmid", "label", "rule_id", "subclass_before")},
                         "fulltext": it["fulltext_source"], "class_after": cls, "subclass_after": sub, "span": sp,
                         "how": "REGEX_ON_FULLTEXT"})
            continue
        p, held, cd = reader_prompt(pilot, it, rec_ft)
        r = runs.get(key)
        if run and (not r or r.get("prompt_sha256") != hashlib.sha256(p).hexdigest()):
            todo.append((pilot, it, p, held, cd))
        rows.append({**{k: it[k] for k in ("slug", "pmid", "label", "rule_id", "subclass_before")},
                     "fulltext": it["fulltext_source"], "_held": held, "_key": key})
    if todo:
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            for key, r in ex.map(run_reader, todo):
                runs[key] = r
                print(key, r["state"], r["record_id"], flush=True)
        json.dump(runs, open(RUNS, "w", encoding="utf-8", newline="\n"), indent=1)
    for row in rows:
        if "_key" not in row:
            continue
        r = runs.get(row.pop("_key"))
        held = row.pop("_held")
        if not r or r.get("state") != "RAN_OK":
            row.update(class_after="INSUFFICIENT_RECORD", how="READER_NOT_RUN")
            continue
        resp = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))).decode("utf-8"))
        claim = next((x for x in resp.get("items", []) if str(x.get("item", "")).startswith("R1")), None)
        v = ms.verify_screening(claim or {}, held, "exclude")
        axes = {k: (x or {}).get("verdict") for k, x in (v.get("axes") or {}).items()}
        ag = v.get("agreement", "")
        cls = ("TRUE_SCOPE_DIFFERENCE" if ag.startswith("RULE_MODEL_AGREE") else
               "SCREENER_ERROR" if ag.startswith("RULE_MODEL_DISAGREE") else "INSUFFICIENT_RECORD")
        row.update(class_after=cls, how=f"RECORDED_READER:{r['record_id']}", reader_agreement=ag.split("(")[0],
                   reader_axes=axes, verifier_state=v.get("state"))
    out = {"n": len(rows), "by_class_after": dict(Counter(r["class_after"] for r in rows)),
           "by_how": dict(Counter((r.get("how") or "NONE").split(":")[0] for r in rows)), "rows": rows}
    json.dump(out, open(os.path.join(OUT, "exclusion_fulltext.json"), "w", encoding="utf-8", newline="\n"),
              indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("n", "by_class_after", "by_how")}, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
