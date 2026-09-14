"""Build docs/iv_iron_strands.json -- iv-iron HF-hospitalisation as THREE declared analyses
(never one forced pool). The compatibility key keeps the strands apart; where a pool would
cross a compatibility dimension it is REFUSED and shown as a counterfactual, not computed.

Every effect is source-verified from the trial's own report (abstracts fetched from PubMed
efetch this session; audit-relayed numbers are not sources). The verbatim source span is
carried with each number.

FINDING that this pass surfaces: the recurrent-event rate ratios do NOT form one pool. They
split by ENDPOINT -- HF-hospitalisation ALONE (AFFIRM-AHF 0.74, FAIR-HF2 0.80) vs the
HF-hospitalisation + CV-death COMPOSITE (AFFIRM-AHF 0.79, IRONMAN 0.82). The previously
proposed "recurrent strand" 0.783 pooled AFFIRM-AHF's HF-alone rate with IRONMAN's composite
rate -- a cross-endpoint pool the compatibility key refuses.
"""
import json, math, os, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


from harness.synth import Study, pool as _canonical_pool  # the ONE validated PM + HKSJ engine


def pool_strand(members):
    """Pool a strand through the CANONICAL PM/HKSJ engine (harness.synth.pool) -- the same inference
    layer every other pool uses. A prior version computed its own z-based common-effect interval and
    advertised it as the result; at k=2 that understates the interval by the HKSJ t(1)=12.7 vs z=1.96
    factor and flipped 'significant' vs 'crosses null'. Returns dict or None for k<2. The registered
    method is HKSJ; the z-based common-effect interval is carried only as a labelled sensitivity."""
    if len(members) < 2:
        return None
    studies = [Study(label=m["trial"], effect=m["effect"], ci_low=m["ci_low"], ci_high=m["ci_high"])
               for m in members]
    r = _canonical_pool(studies, scale="RR")
    hksj_crosses = not (r.ci_low < 1.0 and r.ci_high < 1.0) and not (r.ci_low > 1.0 and r.ci_high > 1.0)
    return {"estimand": "random-effects, Paule-Mandel tau^2, HKSJ 95% CI on t(k-1) (the registered method)",
            "k": r.k,
            "effect": round(r.estimate, 3),
            "ci_low": round(r.ci_low, 3),
            "ci_high": round(r.ci_high, 3),
            "tau2": round(r.tau2, 5),
            "crosses_null": hksj_crosses,
            "common_effect_sensitivity": {
                "effect": round(r.estimate_fixed, 3),
                "ci_low": round(r.ci_low_fixed, 3), "ci_high": round(r.ci_high_fixed, 3),
                "note": "z-based common-effect (fixed) interval, shown ONLY as a small-k sensitivity; "
                        "NOT the registered result. At k=2 it is far narrower than the HKSJ interval."},
            "note_k2": ("k=2: the HKSJ interval uses a t-multiplier on ONE degree of freedom (t=12.7), "
                        "so the registered interval is wide and here crosses the null; the tight "
                        "common-effect sensitivity is not the headline." if r.k == 2 else "")}


# back-compat alias for the callers below
pool_common_effect = pool_strand


# --- source-verified members (verbatim spans fetched from PubMed efetch 2026-09-14) ---
# Each member carries its OWN event_process + endpoint so a strand's homogeneity is checkable:
# a permitted strand is one where every member matches the strand's declared (event_process, endpoint).
_HF_ALONE = "HF hospitalisation (alone)"
_COMPOSITE = "HF hospitalisation + cardiovascular death (composite)"
AFFIRM_hfalone = {"trial": "AFFIRM-AHF", "pmid": "33197395", "nct": "NCT02937454",
    "effect": 0.74, "ci_low": 0.58, "ci_high": 0.94, "scale": "RR",
    "event_process": "RATE", "endpoint": _HF_ALONE,
    "source": "Lancet 2020;396:1895-1904 (abstract): '217 total heart failure hospitalisations "
              "occurred in the ferric carboxymaltose group and 294 occurred in the placebo group "
              "(RR 0.74; 95% CI 0.58-0.94, p=0.013)'."}
AFFIRM_composite = {"trial": "AFFIRM-AHF", "pmid": "33197395", "nct": "NCT02937454",
    "effect": 0.79, "ci_low": 0.62, "ci_high": 1.01, "scale": "RR",
    "event_process": "RATE", "endpoint": _COMPOSITE,
    "source": "Lancet 2020;396:1895-1904 (abstract): '293 primary events (57.2 per 100 "
              "patient-years) occurred in the ferric carboxymaltose group and 372 (72.5 per 100 "
              "patient-years) occurred in the placebo group (rate ratio [RR] 0.79, 95% CI "
              "0.62-1.01, p=0.059)'. Primary = total HF hospitalisations AND cardiovascular death."}
FAIRHF2_hfalone = {"trial": "FAIR-HF2", "pmid": "40159390", "nct": "NCT03036462",
    "effect": 0.80, "ci_low": 0.60, "ci_high": 1.06, "scale": "RR",
    "event_process": "RATE", "endpoint": _HF_ALONE,
    "source": "JAMA 2025 (abstract): 'The second primary outcome (total heart failure "
              "hospitalizations) occurred 264 times in the ferric carboxymaltose group vs 320 "
              "times in the placebo group (rate ratio, 0.80 [95% CI, 0.60-1.06]; P = .12)'."}
IRONMAN_composite = {"trial": "IRONMAN", "pmid": "36347265", "nct": "NCT02642562",
    "effect": 0.82, "ci_low": 0.66, "ci_high": 1.02, "scale": "RR",
    "event_process": "RATE", "endpoint": _COMPOSITE,
    "source": "Lancet 2022;400:2199-2209 (abstract): '336 primary endpoints (22.4 per 100 "
              "patient-years) occurred in the ferric derisomaltose group and 411 (27.5 per 100 "
              "patient-years) occurred in the usual care group (rate ratio [RR] 0.82 [95% CI 0.66 "
              "to 1.02]; p=0.070)'. Primary = recurrent HF hospitalisations AND cardiovascular death."}
CONFIRM_firstevent = {"trial": "CONFIRM-HF", "pmid": "25176939", "nct": "NCT01453608",
    "effect": 0.39, "ci_low": 0.19, "ci_high": 0.82, "scale": "HR",
    "event_process": "FIRST_EVENT_RATIO", "endpoint": _HF_ALONE,
    "source": "CONFIRM-HF full text (PMC4359359): 'HR of 0.39 with a 95% CI of (0.19-0.82) "
              "(P = 0.009)' for time-to-first hospitalisation due to worsening HF."}

strands = [
    {"strand": "A", "name": "First-event hazard ratio (time to first HF hospitalisation)",
     "event_process": "FIRST_EVENT_RATIO", "endpoint": _HF_ALONE,
     "effect_measure": "HR", "members": [CONFIRM_firstevent]},
    {"strand": "B", "name": "Recurrent-event rate ratio, HF hospitalisation ALONE",
     "event_process": "RATE", "endpoint": _HF_ALONE,
     "effect_measure": "RR", "members": [AFFIRM_hfalone, FAIRHF2_hfalone]},
    {"strand": "C", "name": "Recurrent-event rate ratio, HF hospitalisation + CV death COMPOSITE",
     "event_process": "RATE", "endpoint": _COMPOSITE,
     "effect_measure": "RR", "members": [AFFIRM_composite, IRONMAN_composite]},
    {"strand": "D", "name": "Participant-level risk (patients with >=1 HF hospitalisation)",
     "event_process": "PARTICIPANT_RISK", "endpoint": _HF_ALONE,
     "effect_measure": "risk (counts)",
     "members": [{"trial": "CONFIRM-HF", "pmid": "25176939", "nct": "NCT01453608",
                  "event_process": "PARTICIPANT_RISK", "endpoint": _HF_ALONE,
                  "counts": "10 of ~132 (FCM) vs 25 of ~129 (placebo) with >=1 HF hospitalisation",
                  "crude_rr": 0.39, "scale": "RR (crude)",
                  "source": "CONFIRM-HF full text (PMC4359359, Table 2): 10 (7.6%) vs 25 (19.4%) "
                            "patients with >=1 HF hospitalisation; crude RR 0.39 corroborates the "
                            "time-to-event HR."}]},
]
for s in strands:
    p = pool_common_effect(s["members"]) if s["effect_measure"] in ("RR", "HR") else None
    s["pool"] = p
    s["k"] = len(s["members"])

doc = {
    "slug": "iv-iron-hfref-hosp",
    "_doc": ("iv-iron for heart-failure hospitalisation, expressed as THREE (here four) declared "
             "analyses rather than one forced pool. The compatibility key keeps strands apart: "
             "first-event HR, recurrent-event rate ratio, and participant-level risk are different "
             "estimands of different event processes and MUST NOT be pooled together. Within the "
             "recurrent rate ratios the ENDPOINT further splits them (HF-hosp alone vs HF-hosp+CV-death "
             "composite). Every number is source-verified with its verbatim span; no risk-of-bias or "
             "clinical judgement is added here."),
    "generated_utc": "2026-09-14",
    "why_topic_is_suppressed": ("Strands A and B measure the SAME endpoint (HF hospitalisation) two "
             "incompatible ways -- first-event HR (CONFIRM-HF) vs recurrent rate ratio "
             "(AFFIRM-AHF + FAIR-HF2). A hazard ratio of the first event and a rate ratio of all "
             "events are not the same quantity and cannot be pooled; the single-pool primary is "
             "therefore correctly suppressed. The strands below are the honest decomposition."),
    "refused_cross_endpoint_pool": {
        "description": ("The recurrent-event rate ratios do NOT form one pool. A pool of AFFIRM-AHF's "
                        "HF-hosp-ALONE rate (0.74) with IRONMAN's HF-hosp+CV-death COMPOSITE rate "
                        "(0.82) crosses the endpoint dimension of the compatibility key."),
        # The refused number is carried as a descriptive STRING, not machine-readable derived-stat
        # fields -- it is explicitly the counterfactual of a pool that was refused, never a served
        # estimate. This is the visible-counterfactual pattern (compat.py), one layer down.
        "if_forced_it_would_be": None,  # filled below (string)
        "verdict": "REFUSED -- endpoint mismatch (HF-hosp alone vs composite)"},
    "strands": strands,
}
# compute the refused cross-endpoint number to show the counterfactual explicitly (as a string)
xf = pool_common_effect([AFFIRM_hfalone, IRONMAN_composite])
doc["refused_cross_endpoint_pool"]["if_forced_it_would_be"] = (
    f"{xf['effect']} ({xf['ci_low']}-{xf['ci_high']}) -- this is the 0.783 figure previously "
    f"treated as the recurrent strand; it mixes endpoints and is refused, not published.")

outp = os.path.join(ROOT, "docs", "iv_iron_strands.json")
json.dump(doc, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote", outp)
for s in strands:
    p = s["pool"]
    if p:
        print(f"  Strand {s['strand']} ({s['effect_measure']}, k={s['k']}): HKSJ "
              f"{p['effect']} ({p['ci_low']}-{p['ci_high']}) tau2={p['tau2']} "
              f"{'crosses null' if p['crosses_null'] else 'significant'}"
              f" | z-fixed sensitivity {p['common_effect_sensitivity']['effect']} "
              f"({p['common_effect_sensitivity']['ci_low']}-{p['common_effect_sensitivity']['ci_high']})")
    else:
        m = s["members"][0]
        eff = m.get("effect", m.get("crude_rr"))
        print(f"  Strand {s['strand']} ({s['effect_measure']}, k={s['k']}): single trial {m['trial']} {eff}")
print(f"  REFUSED cross-endpoint pool would be: {xf['effect']} ({xf['ci_low']}-{xf['ci_high']})")
