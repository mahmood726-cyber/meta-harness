"""V14-03 (signed "sign v14", option A): serve FIDELIO-DKD's FDA-label hyperkalaemia adverse reaction as its own harms
endpoint in finerenone-ckd-t2d-renal.

Typed, reproducible, nothing hand-entered:
  1. fetch the Kerendia label (drugs@FDA 215341s000lbl.pdf, Jul 2021; US-government text, public domain), extract its
     typed text layer exactly as the binding lane did (kgap.k_gap._pdf_text, pypdf, never OCR), and REFUSE unless the
     PDF bytes and the text match the digests the lane pinned (registry/regulatory_sources.json on g1/r9-4-fda-label);
  2. hold the text verbatim at outputs/held_labels/fda_215341s000lbl.txt (+ manifest.json);
  3. read Table 3 typed: its caption must name FIDELIO-DKD, the arm header 'Kerendia N = <n> ... Placebo N = <n>' must
     follow it, and the 'Hyperkalemia <n> (<p>) <n> (<p>)' row must follow the header, with each p = 100 n / N at the
     printed precision;
  4. write the canonical count row (cache/finerenone-ckd-t2d-renal/verified_arms.json, key FIDELIO-DKD PMID 33264825)
     and add the endpoint to the topic's harm outcomes (separate from the trials' own lab-threshold hyperkalaemia).

    python scripts/v14_03_fidelio_label_hyperk.py [--offline]
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT]
SLUG = "finerenone-ckd-t2d-renal"
PID = "33264825"
ITEM = "V14-03"
URL = "https://www.accessdata.fda.gov/drugsatfda_docs/label/2021/215341s000lbl.pdf"
DOC_SHA = "d8ba75830e0184919d30ab5cedccec4c76eba1821545aea29209b67a1a142b94"
TEXT_SHA = "26c58886d7802376ecc2c3235a2e1acc0bae3dc775bf8744f4df116b23ee0c9d"
HELD_DIR = os.path.join(ROOT, "outputs", "held_labels")
HELD_NAME = "fda_215341s000lbl.txt"
OUTCOME = {"name": "Hyperkalemia (FDA label adverse reaction, FIDELIO-DKD safety population)",
           "keywords": ["hyperkalemia", "hyperkalaemia"], "estimand": "RR",
           "population": "FIDELIO-DKD safety population (FDA label adverse-reaction table)",
           "timepoint": "trial-reported follow-up",
           # the endpoint is the LABEL's table: only the trials it covers can report it (V14-03 scoping); FIGARO's own
           # lab-threshold hyperkalaemia is a different endpoint, not 'known reported, unresolved'
           "source_scope": {"document_ref": f"outputs/held_labels/{HELD_NAME}", "trials": [PID],
                            "basis": "FDA label Table 3 (FIDELIO-DKD safety population)"}}
REPLAY = {"table": "Table 3", "trial": "FIDELIO-DKD", "arm_t": "Kerendia", "arm_c": "Placebo",
          "row_label": "Hyperkalemia"}


def parse(text):
    """The shared typed table reader -- the SAME reader the served row is replayed with
    (harness/extractor_replay.read_label_adr_table); a refusal stops the script."""
    from harness.extractor_replay import ReadRefused, read_label_adr_table
    try:
        return read_label_adr_table(text, REPLAY)
    except ReadRefused as exc:
        raise SystemExit(f"REFUSED: {exc}")


def main(argv):
    offline = "--offline" in argv
    path = os.path.join(HELD_DIR, HELD_NAME)
    if offline:
        text = open(path, encoding="utf-8", newline="").read()
    else:
        sys.path.insert(0, os.path.join(ROOT, "outputs"))
        from harness import http
        from kgap import k_gap
        st, b = http.get_raw(URL, tries=2, timeout=180)
        if hashlib.sha256(b).hexdigest() != DOC_SHA:
            raise SystemExit("REFUSED: label PDF bytes moved (apply nothing)")
        text = k_gap._pdf_text(b)
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != TEXT_SHA:
        raise SystemExit("REFUSED: label text digest moved (apply nothing)")
    v = parse(text)
    if not offline:
        os.makedirs(HELD_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        mp = os.path.join(HELD_DIR, "manifest.json")
        man = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {"documents": {}}
        man["documents"][HELD_NAME] = {
            "source": URL, "agency": "FDA", "licence": "US_GOV_PUBLIC_DOMAIN", "doc_sha256": DOC_SHA,
            "text_sha256": TEXT_SHA, "text_layer": "pypdf typed text (kgap.k_gap._pdf_text); never OCR",
            "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "held_for": f"{ITEM} {SLUG} '{OUTCOME['name']}'"}
        with open(mp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(man, f, indent=2, sort_keys=True)
            f.write("\n")
    row = {"kind": "extracted_counts", "outcome": OUTCOME["name"], "override": True,
           "ai": v["ai"], "n1i": v["n1i"], "ci": v["ci"], "n2i": v["n2i"],
           "provenance": "label_adr_table", "source_level": 1, "replay": dict(REPLAY),
           "document_ref": f"outputs/held_labels/{HELD_NAME}", "document_sha256": TEXT_SHA,
           "source_span": v["raw_row"],
           "source": (f"Kerendia US label (215341s000, Jul 2021) Table 3, FIDELIO-DKD safety population: "
                      f"'{v['header_span']}' / '{v['row_span']}'"),
           "verification": (f"{ITEM}: typed Table 3 read (caption '{v['caption_span'][:80]}'); percentages reconcile "
                            f"with n / N; label text sha256 {TEXT_SHA}; label doc sha256 {DOC_SHA}"),
           "reason": (f"{ITEM} (signed by Mahmood, 'sign v14'): investigator-reported hyperkalaemia adverse reaction, its "
                      f"own harms endpoint -- not the trials' lab-threshold hyperkalaemia; binding lane label_adr (R9-4).")}
    vpath = os.path.join(ROOT, "cache", SLUG, "verified_arms.json")
    data = json.load(open(vpath, encoding="utf-8")) if os.path.exists(vpath) else {}
    cur = data.get(PID)
    cur = [] if cur is None else (cur if isinstance(cur, list) else [cur])
    data[PID] = [e for e in cur if e.get("outcome") != OUTCOME["name"]] + [row]
    with open(vpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tp = os.path.join(ROOT, "topics", f"{SLUG}.json")
    topic = json.load(open(tp, encoding="utf-8"))
    # the outcome is (re)written whole, so a scope added later reaches a topic that already carries the outcome
    topic["harm_outcomes"] = [o for o in topic["harm_outcomes"] if o.get("name") != OUTCOME["name"]] + [OUTCOME]
    with open(tp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(topic, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: v[k] for k in ("ai", "n1i", "ci", "n2i", "row_span", "header_span")}))


if __name__ == "__main__":
    main(sys.argv[1:])
