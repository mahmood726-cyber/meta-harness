"""Build docs/iv_iron_strands.json -- iv-iron HF-hospitalisation as declared strands (never one forced pool). The
compatibility key keeps the strands apart; where a pool would cross a compatibility dimension it is REFUSED and shown as
a counterfactual, not computed.

External review 11 (this rewrite): every strand goes through the ONE analysis/provenance/gate path, harness/strand_pool:
  - every member effect is READ from the held source text at a quoted span (cache/iv-iron-hfref-hosp/records.json
    abstracts; the CONFIRM-HF held full text for its table); this script types no trial number. A quote that is not in
    the held text refuses the member and the build fails.
  - strand pools run synth.pool then harness/k2.py: at k=2 the single-df HKSJ interval is NOT served (11-02).
  - strand D (CONFIRM-HF participants with >=1 HF hospitalisation) is read from Table 2 of the held full text
    ('Hospitalizations and deaths (full-analysis set)', FCM n = 150, placebo n = 151): 10 v 25 participants. The
    bracketed figures 7.6 and 19.4 are incidence per 100 patient-years (the table's own footnote), so the old 'crude RR
    0.39' was a RATE ratio and its '~132/~129' denominators were invented (11-03).

FINDING kept from the first pass: the recurrent-event rate ratios split by ENDPOINT -- HF hospitalisation ALONE
(AFFIRM-AHF, FAIR-HF2) vs the HF hospitalisation + CV death COMPOSITE (AFFIRM-AHF, IRONMAN).

    python scripts/build_iv_iron_strands.py [--out PATH]      (default docs/iv_iron_strands.json)
"""
import argparse
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import strand_pool as sp  # noqa: E402

SLUG = "iv-iron-hfref-hosp"
_HF_ALONE = "HF hospitalisation (alone)"
_COMPOSITE = "HF hospitalisation + cardiovascular death (composite)"

# (trial, pmid, nct, endpoint, event_process, scale, the quote that must occur in the held abstract)
MEMBERS = {
    "AFFIRM_hfalone": ("AFFIRM-AHF", "33197395", "NCT02937454", _HF_ALONE, "RATE", "RR",
                       "(RR 0·74; 95% CI 0·58-0·94"),
    "AFFIRM_composite": ("AFFIRM-AHF", "33197395", "NCT02937454", _COMPOSITE, "RATE", "RR",
                         "(rate ratio [RR] 0·79, 95% CI 0·62-1·01"),
    "FAIRHF2_hfalone": ("FAIR-HF2", "40159390", "NCT03036462", _HF_ALONE, "RATE", "RR",
                        "(rate ratio, 0.80 [95% CI, 0.60-1.06]"),
    "IRONMAN_composite": ("IRONMAN", "36347265", "NCT02642562", _COMPOSITE, "RATE", "RR",
                          "(rate ratio [RR] 0·82 [95% CI 0·66 to 1·02]"),
    "CONFIRM_firstevent": ("CONFIRM-HF", "25176939", "NCT01453608", _HF_ALONE, "FIRST_EVENT_RATIO", "HR",
                           "hazard ratio (95% confidence interval): 0.39 (0.19-0.82)"),
}
# the table layout this builder STATES and the held source must confirm (codex strands-r1#3-#5): the FAS caption, the
# row, the arm cells by position (events | 'subjects (incidence)' per arm), and the footnote phrase saying the
# bracketed cell counts subjects
CONFIRM_TABLE = {"caption": "full-analysis set", "row": "Hospitalizations due to worsening HF", "arm_cells": (2, 4),
                 "count_basis": "computed using the number of subjects with the end-point/event"}


def _held(root=ROOT):
    recs = json.load(open(os.path.join(root, "cache", SLUG, "records.json"), encoding="utf-8"))
    ab = {str(r.get("id")): r.get("abstract") or "" for r in recs.get("records") or []}
    ft_path = os.path.join(root, "cache", SLUG, "ft_25176939.txt")
    ft = open(ft_path, encoding="utf-8").read() if os.path.exists(ft_path) else ""
    return ab, ft


def member(key, ab):
    trial, pmid, nct, endpoint, process, scale, quote = MEMBERS[key]
    got = sp.read_member(ab.get(pmid), quote)
    if not got:
        raise SystemExit(f"REFUSED: {trial} ({key}) quote not in the held abstract of PMID {pmid}, or its numbers do not "
                         f"parse: {quote!r}")
    return {"trial": trial, "pmid": pmid, "nct": nct, "event_process": process, "endpoint": endpoint, "scale": scale,
            "effect": got["effect"], "ci_low": got["ci_low"], "ci_high": got["ci_high"], "ci_level": got["ci_level"],
            "source_span": got["source_span"],
            "source": f"held abstract, cache/{SLUG}/records.json PMID {pmid}"}


def confirm_participants(ft):
    c = sp.table_arm_counts(ft, **CONFIRM_TABLE)
    if not c:
        return {"trial": "CONFIRM-HF", "pmid": "25176939", "nct": "NCT01453608", "event_process": "PARTICIPANT_RISK",
                "endpoint": _HF_ALONE, "status": "REFUSED_DENOMINATORS_NOT_STATED",
                "reason": "the held full text's FAS table row or arm sizes could not be read; no denominator is inferred"}
    rr = sp.counts_rr(c["ai"], c["n1i"], c["ci"], c["n2i"])
    return {"trial": "CONFIRM-HF", "pmid": "25176939", "nct": "NCT01453608", "event_process": "PARTICIPANT_RISK",
            "endpoint": _HF_ALONE, "scale": "RR", "ai": c["ai"], "n1i": c["n1i"], "ci": c["ci"], "n2i": c["n2i"],
            "effect": rr["effect"], "ci_low": rr["ci_low"], "ci_high": rr["ci_high"], "ci_level": rr["ci_level"],
            "ci_provenance": rr["ci_provenance"],
            "source_span": f"{c['caption']} | {c['arm_header']} | {c['row']}",
            "source": f"held full text cache/{SLUG}/ft_25176939.txt (PMC4359359), Table 2",
            "note": ("participants with >=1 HF hospitalisation in the full-analysis set; the bracketed 7.6 and 19.4 are "
                     "incidence per 100 patient-years at risk (the table's footnote), not percentages")}


def build(root=ROOT):
    ab, ft = _held(root)
    m = {k: member(k, ab) for k in MEMBERS}
    strands = [
        {"strand": "A", "name": "First-event hazard ratio (time to first HF hospitalisation)",
         "event_process": "FIRST_EVENT_RATIO", "endpoint": _HF_ALONE, "effect_measure": "HR",
         "members": [m["CONFIRM_firstevent"]]},
        {"strand": "B", "name": "Recurrent-event rate ratio, HF hospitalisation ALONE",
         "event_process": "RATE", "endpoint": _HF_ALONE, "effect_measure": "RR",
         "members": [m["AFFIRM_hfalone"], m["FAIRHF2_hfalone"]]},
        {"strand": "C", "name": "Recurrent-event rate ratio, HF hospitalisation + CV death COMPOSITE",
         "event_process": "RATE", "endpoint": _COMPOSITE, "effect_measure": "RR",
         "members": [m["AFFIRM_composite"], m["IRONMAN_composite"]]},
        {"strand": "D", "name": "Participant-level risk (participants with >=1 HF hospitalisation)",
         "event_process": "PARTICIPANT_RISK", "endpoint": _HF_ALONE, "effect_measure": "RR",
         "members": [confirm_participants(ft)]},
    ]
    for s in strands:
        poolable = [x for x in s["members"] if x.get("effect") is not None]
        s["pool"] = sp.pool_strand(poolable, s["effect_measure"]) if len(poolable) >= 2 else None
        s["k"] = len(poolable)
    xf = sp.pool_strand([m["AFFIRM_hfalone"], m["IRONMAN_composite"]], "RR")
    return {
        "slug": SLUG,
        "_doc": ("iv-iron for heart-failure hospitalisation as declared strands rather than one forced pool. First-event "
                 "HR, recurrent-event rate ratio and participant-level risk are different estimands and are never pooled "
                 "together; within the recurrent rate ratios the ENDPOINT splits them further. Every number is read from "
                 "held source text by harness/strand_pool.py; pools run synth.pool then the k=2 rule (harness/k2.py)."),
        "generated_by": "scripts/build_iv_iron_strands.py",
        "why_topic_is_suppressed": ("Strands A and B measure the SAME endpoint (HF hospitalisation) two incompatible ways "
                                    "-- first-event HR (CONFIRM-HF) vs recurrent rate ratio (AFFIRM-AHF + FAIR-HF2). A "
                                    "hazard ratio of the first event and a rate ratio of all events are not the same "
                                    "quantity and cannot be pooled; the single-pool primary is therefore suppressed."),
        "refused_cross_endpoint_pool": {
            "description": ("The recurrent-event rate ratios do NOT form one pool. A pool of AFFIRM-AHF's HF-hosp-ALONE "
                            "rate with IRONMAN's HF-hosp+CV-death COMPOSITE rate crosses the endpoint dimension."),
            "if_forced_it_would_be": (f"{xf['estimate']} (k=2; no interval would be served) -- the 0.783 figure once "
                                      "treated as the recurrent strand; it mixes endpoints and is refused, not published."),
            "verdict": "REFUSED -- endpoint mismatch (HF-hosp alone vs composite)"},
        "open_question_v15": ("CONFIRM-HF's post hoc recurrent HF-hospitalisation RR 0.30 (0.14-0.64) (external review "
                              "11-04) is not admitted, as a sensitivity or otherwise, without a signed decision."),
        "strands": strands,
    }


if __name__ == "__main__":
    # only when run as a script: an importer (a test) keeps its own stdout (lessons: module-level stdout reassignment)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "iv_iron_strands.json"))
    a = ap.parse_args()
    doc = build()
    json.dump(doc, open(a.out, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print("wrote", a.out)
    for s in doc["strands"]:
        p = s["pool"]
        if p:
            ci = (f"({p['ci_low']}-{p['ci_high']})" if p.get("ci_low") is not None else
                  f"CI not served at k=2 (HKSJ for audit {p.get('ci_hksj_unserved', {}).get('ci_low')}-"
                  f"{p.get('ci_hksj_unserved', {}).get('ci_high')})")
            print(f"  Strand {s['strand']} k={s['k']}: {p.get('estimate')} {ci}")
        else:
            x = s["members"][0]
            print(f"  Strand {s['strand']} k={s['k']}: {x['trial']} {x.get('effect')} ({x.get('ci_low')}-{x.get('ci_high')})"
                  f"{' counts %s/%s v %s/%s' % (x['ai'], x['n1i'], x['ci'], x['n2i']) if x.get('ai') is not None else ''}")
