"""SHADOW RE-SCREEN under the FIXED rules (external audit R6 P3 / R7-1 / R9-1, captain triage 9 Oct; Mahmood 9 Oct: "work hard
on evidence completeness"). Nothing served changes: the served screen (harness/screen.py) is re-run on the build's own
inputs (pipeline.outcome_inputs: dedup, contrast evictions, companion reports), first UNCHANGED (the baseline must
reproduce the served review.json decisions), then with a recorded OVERLAY of five fixes, each tagged on the flip it causes:

  F1 PLACEBO_ARM_IS_A_CONTRAST   the computed background-only contrast rule (_background_only_randomised_contrast) does not
                                 evict when a placebo / sham / usual-care arm exists beside an arm of our intervention
                                 (ARTS-DN Japan NCT01968668: BAY94-8862 x7 + Placebo read CONTRAST_ABSENT)
  F2 PLACEBO_FOR_X               'Placebo for Empagliflozin', 'matching placebo (finerenone)', 'BAY94-8862 placebo' are a
                                 placebo arm, never an arm of X (SAK NCT05138575)
  F3 DEVELOPMENT_CODE            a development code of our drug is our drug (BAY94-8862 = finerenone, LCZ696 = sacubitril/
                                 valsartan, ...): typed table DEV_CODES, each code cited
  F4 POPULATION_SYNONYM          'Diabetes Mellitus, Type 2' / 'type II diabetes' / 'T2DM' ... = 'type 2 diabetes': typed
                                 concept table POP_SYNONYMS, applied only to concepts the protocol's population names
  F5 MISSPELLING                 a record token within edit distance 1 (>= 7 letters) or 2 (>= 10) of an intervention term
                                 (and not itself a different known drug) is that term (INDORSE 'sitagliptin' class miss)

A FLIP is an X2 / X3 / X-CONTRAST exclusion that the same screen INCLUDES under the overlay. Each flip carries the fixes that
made it, the record's own span, and goes to recorded dual codex verification (scripts/g1_shadow_verify.py) before any count.
Curated, audit-confirmed contrast evictions (docs/contrast_evictions.json) are not overridden; they are listed.

    python scripts/g1_shadow_rescreen.py [SLUG ...] [--all] -> outputs/k_gap/rescreen/<slug>.json + _summary.json
"""
from __future__ import annotations

import copy
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "outputs", "k_gap", "rescreen")
EXCL = ("X2", "X3", "X-CONTRAST")

# F3: development codes (sponsor compound codes as printed in registries / abstracts), by INN
DEV_CODES = {
    "finerenone": ["BAY94-8862", "BAY 94-8862", "BAY-94-8862", "BAY948862"],
    "sacubitril": ["LCZ696", "LCZ 696", "LCZ-696"],
    "dapagliflozin": ["BMS-512148", "BMS512148"], "empagliflozin": ["BI 10773", "BI10773", "BI-10773"],
    "canagliflozin": ["JNJ-28431754", "TA-7284"], "ertugliflozin": ["MK-8835", "PF-04971729"],
    "sotagliflozin": ["LX4211", "SAR439954"], "edoxaban": ["DU-176b", "DU176b", "DU-176"],
    "dabigatran": ["BIBR 1048", "BIBR1048", "BIBR 953"], "rivaroxaban": ["BAY 59-7939", "BAY59-7939"],
    "apixaban": ["BMS-562247", "BMS562247"], "semaglutide": ["NN9535", "NN9536", "NN9924", "NNC 0113-0217"],
    "liraglutide": ["NN2211", "NN8022"], "dulaglutide": ["LY2189265"], "albiglutide": ["GSK716155"],
    "exenatide": ["AC2993"], "lixisenatide": ["AVE0010"], "efpeglenatide": ["HM11260C"], "tirzepatide": ["LY3298176"],
    "evolocumab": ["AMG 145", "AMG145"], "alirocumab": ["SAR236553", "REGN727"], "inclisiran": ["ALN-PCSsc"],
    "omarigliptin": ["MK-3102"], "sitagliptin": ["MK-0431"], "linagliptin": ["BI 1356"], "saxagliptin": ["BMS-477118"],
    "alogliptin": ["SYR-322", "SYR322"], "denosumab": ["AMG 162", "AMG162"], "esketamine": ["JNJ-54135419"],
    "ticagrelor": ["AZD6140"], "tocilizumab": ["MRA"], "ferric carboxymaltose": ["VIT-45"],
    "ferric derisomaltose": ["iron isomaltoside 1000"],
}
DEV_CODES = {k: [c for c in v if len(c) >= 5] for k, v in DEV_CODES.items()}   # 'MRA' too short to be a safe code

# F3b: drug-CLASS synonyms (applied only when the protocol's own intervention terms name the class)
CLASS_SYNONYMS = {
    "dpp-4": ["dipeptidyl peptidase-4", "dipeptidyl peptidase 4", "dipeptidyl peptidase iv", "dipeptidyl peptidase-iv",
              "dpp4", "dpp-iv"],
    "sglt2": ["sodium-glucose cotransporter 2", "sodium-glucose co-transporter 2", "sodium glucose cotransporter 2",
              "sodium-glucose cotransporter-2", "sglt-2"],
    "glp-1": ["glucagon-like peptide-1 receptor agonist", "glucagon-like peptide 1 receptor agonist", "glp1",
              "glp-1 receptor agonist"],
    "pcsk9": ["proprotein convertase subtilisin/kexin type 9", "pcsk-9"],
}

# F4: population concepts -> synonyms (applied only when the protocol's population names the concept)
POP_SYNONYMS = {
    "type 2 diabetes": ["diabetes mellitus, type 2", "diabetes mellitus type 2", "type ii diabetes", "type-2 diabetes",
                        "type 2 diabetic", "t2dm", "niddm", "non-insulin-dependent diabetes", "noninsulin-dependent diabetes",
                        "non-insulin dependent diabetes"],
    "chronic kidney disease": ["renal insufficiency, chronic", "chronic renal insufficiency", "chronic renal failure",
                               "kidney failure, chronic", "diabetic kidney disease", "chronic kidney diseases"],
    "heart failure": ["cardiac failure", "heart failure, systolic", "heart failure, diastolic", "congestive heart failure",
                      "hfref", "hfpef"],
    "atrial fibrillation": ["non-valvular atrial fibrillation", "nonvalvular atrial fibrillation", "nvaf",
                            "auricular fibrillation"],
    "venous thromboembolism": ["deep vein thrombosis", "deep venous thrombosis", "venous thrombosis", "pulmonary embolism",
                               "venous thromboembolic"],
    "obesity": ["obese", "overweight", "weight management"],
    "osteoporosis": ["osteoporosis, postmenopausal", "postmenopausal osteoporosis", "osteoporotic"],
    "insomnia": ["sleep initiation and maintenance disorders", "sleeplessness", "insomnia disorder"],
    "polycystic ovary syndrome": ["polycystic ovarian syndrome", "pcos", "stein-leventhal"],
    "treatment-resistant depression": ["depressive disorder, treatment-resistant", "treatment resistant depression",
                                       "trd"],
    "covid-19": ["sars-cov-2", "coronavirus disease 2019", "covid 19", "2019-ncov"],
    "postpartum haemorrhage": ["postpartum hemorrhage", "post-partum haemorrhage", "post-partum hemorrhage",
                               "postpartum bleeding"],
    "pericarditis": ["recurrent pericarditis", "pericardial inflammation"],
    "acute coronary syndrome": ["acute coronary syndromes", "myocardial infarction", "unstable angina", "nstemi", "stemi"],
    "community-acquired pneumonia": ["community acquired pneumonia", "pneumonia, community-acquired"],
}

# F6 SELF_DESCRIBED_RCT: the trial's OWN abstract names its design ('We conducted an open-label, randomized trial that
# compared ...' -- J-EINSTEIN 25717286, PubMed type 'Journal Article' only, read X1 'not an RCT'). Self-reference
# ('we', 'this', 'the present') or 'were randomly assigned / randomized' is required; the screen's negation guard holds.
_F6 = re.compile(r"\b(?:we|this|the present|the current)\b[^.]{0,80}?(?<!non-)(?<!non )(?<!not )\brandomi[sz]ed\b"
                 r"[^.]{0,40}?\b(?:trial|study)\b|\b(?:were|was|been)\s+(?:randomly\s+(?:assigned|allocated)|randomi[sz]ed)\b",
                 re.I)


def f6_patch(screen):
    """Context: screen._body_says_rct also accepts F6. Returns a restore() function."""
    orig = screen._body_says_rct

    def patched(rec):
        return orig(rec) or bool(_F6.search(rec.get("abstract", "") or ""))
    screen._body_says_rct = patched
    return lambda: setattr(screen, "_body_says_rct", orig)


_PLACEBO_FOR = re.compile(r"\b(?:matching\s+)?placebo\s+(?:for|to|of|matching|matched to)\s+[A-Za-z0-9/\- ]{2,60}"
                          r"|\bmatching\s+placebo\b(?:\s*\([^)]{0,60}\))?"
                          r"|\b[A-Za-z][A-Za-z0-9\-]{3,40}[- ]placebo\b", re.I)
_CONTROLISH = re.compile(r"placebo|sham|usual care|standard care|standard of care", re.I)


def _lev(a, b, cap=3):
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


KNOWN_DRUGS = {d for d in DEV_CODES} | {"placebo", "metformin", "insulin", "aspirin", "warfarin", "enoxaparin", "heparin",
                                         "enalapril", "valsartan", "ramipril", "atorvastatin", "simvastatin", "rosuvastatin",
                                         "pravastatin", "clopidogrel", "prasugrel", "glimepiride", "glipizide",
                                         "pioglitazone", "spironolactone", "eplerenone", "dexamethasone", "hydrocortisone",
                                         "methylprednisolone", "prednisolone", "colchicine", "melatonin", "ramelteon"}


def misspellings(rec_text, terms):
    """{token: term} record tokens that are a near-miss of an intervention term and are not themselves a known drug."""
    toks = set(re.findall(r"[A-Za-z][A-Za-z\-]{6,}", rec_text))
    out = {}
    for t in toks:
        tl = t.lower()
        if tl in KNOWN_DRUGS:
            continue
        for term in terms:
            tm = term.lower()
            if " " in tm or len(tm) < 7 or tl == tm or tm in tl:
                continue
            d = _lev(tl, tm)
            if (len(tm) >= 10 and d <= 2) or d == 1:
                out[t] = term
    return out


def overlay_config(config):
    """(config', applied) -- F3 codes into intervention_any, F4 synonyms into population_any_extra."""
    c = copy.deepcopy(config)
    inc = c.setdefault("include", {})
    applied = {"F3": [], "F4": []}
    ia = [x.lower() for x in (inc.get("intervention_any") or [])]
    for inn, codes in DEV_CODES.items():
        if any(inn in x or x in inn for x in ia):
            new = [k for k in codes if k.lower() not in ia]
            inc["intervention_any"] = list(inc.get("intervention_any") or []) + new
            applied["F3"] += [f"{k}={inn}" for k in new]
    for cls, syns in CLASS_SYNONYMS.items():
        if any(cls in x.replace(" ", "") or cls.replace("-", "") in x.replace("-", "") for x in ia):
            new = [k for k in syns if k not in ia]
            inc["intervention_any"] = list(inc.get("intervention_any") or []) + new
            applied["F3"] += [f"{k}={cls} (class)" for k in new]
    pa = " ".join(x.lower() for x in (inc.get("population_any") or []) + (inc.get("population_any_extra") or []))
    for concept, syns in POP_SYNONYMS.items():
        if concept in pa or any(s in pa for s in syns):
            new = [s for s in syns if s not in pa]
            inc["population_any_extra"] = list(inc.get("population_any_extra") or []) + new
            applied["F4"] += [f"{s}~{concept}" for s in new]
    return c, applied


def overlay_record(rec, terms):
    """(rec', fixes) -- F2 'placebo for X' arms normalised to 'placebo' in the structured arm fields only."""
    r = copy.deepcopy(rec)
    fixes = []
    for k in ("interventions", "arms", "arm_groups"):
        v = r.get(k)
        if not isinstance(v, list):
            continue
        nv = []
        for a in v:
            s = a.get("name") if isinstance(a, dict) else str(a)
            if s and _PLACEBO_FOR.search(s) and _CONTROLISH.search(s):
                ns = _PLACEBO_FOR.sub("placebo", s)
                if ns != s:
                    fixes.append(f"F2:{s[:60]}->{ns[:40]}")
                    s = ns
            nv.append(dict(a, name=s) if isinstance(a, dict) else s)
        r[k] = nv
    return r, fixes


def run_topic(slug):
    from harness import pipeline, screen, served_comparator as sc, fetch
    config = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    config = sc.served_config(slug, config)
    records = fetch.ensure(config, "2026-10-09T00:00:00Z")
    # outcome_inputs MUTATES the record objects after screening (a registry record's id becomes its AACT id), so the
    # shadow screens a PRISTINE deep copy, deduplicated exactly as the pipeline does, under the pipeline's own config
    inp = pipeline.outcome_inputs(slug, config, copy.deepcopy(records))
    cfg = inp["config"]
    merged = pipeline._dedup(copy.deepcopy(records), cfg.get("pivotal_trials"))
    base = {d["id"]: d for d in screen.run(copy.deepcopy(merged), cfg)["decisions"]}
    build = {d["id"]: (d["decision"], d["rule_id"]) for d in inp["scr"]["decisions"]}
    rebuild_agree = sum(1 for i, d in base.items() if build.get(i) == (d["decision"], d["rule_id"]))
    rec_by_id = {r["id"]: r for r in merged}
    served = {}
    rp = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    if os.path.exists(rp):
        served = {str(s["id"]).split(" · ")[-1]: s for s in
                  (json.load(open(rp, encoding="utf-8")).get("screening") or {}).get("records") or []}
    agree = sum(1 for i, s in served.items() if i in base and (base[i]["decision"], base[i]["rule_id"]) ==
                (s["decision"], s["rule_id"]))
    cfg2, applied = overlay_config(cfg)
    terms = list((cfg2.get("include") or {}).get("intervention_any") or [])
    excl = [i for i, d in base.items() if d["decision"] == "exclude" and d["rule_id"] in EXCL]
    rec_fix, merged2 = {}, []
    for r in merged:
        if r["id"] in excl:
            r2, fx = overlay_record(r, terms)
            txt = " ".join(str(r.get(k) or "") for k in ("title", "abstract", "conditions", "interventions", "arms"))
            ms = misspellings(txt, list((cfg.get("include") or {}).get("intervention_any") or []))
            if ms:
                fx += [f"F5:{t}~{m}" for t, m in ms.items()]
            rec_fix[r["id"]] = (fx, ms)
            merged2.append(r2)
        else:
            merged2.append(r)
    comp_any = " ".join((cfg.get("include") or {}).get("comparator_any") or []).lower()
    if "placebo" in comp_any:
        ovs = []
        for r in merged2:
            if r["id"] in excl and r.get("id_type") == "nct":
                arms = [str(a.get("name") if isinstance(a, dict) else a) for a in (r.get("interventions") or [])]
                pl = next((a for a in arms if re.search(r"\bplacebo\b", a, re.I)), None)
                if pl:
                    ovs.append({"key": r["id"], "term": "placebo"})
                    rec_fix.setdefault(r["id"], ([], {}))[0].append(f"F1b: registry arm {pl[:50]!r} is a placebo comparator")
        if ovs:
            cfg2["include"]["comparator_overrides"] = list(cfg2["include"].get("comparator_overrides") or []) + ovs
    extra_terms = sorted({t for fx, ms in rec_fix.values() for t in ms})
    if extra_terms:
        cfg2["include"]["intervention_any"] = list(cfg2["include"].get("intervention_any") or []) + extra_terms
    curated = {str(e.get("key") or e.get("nct") or e.get("id")) for e in (cfg.get("contrast_evictions") or [])}
    orig_bg = screen._background_only_randomised_contrast
    f1_hits = {}

    def bg_fixed(rec, keywords, arm_index):
        bg, basis = orig_bg(rec, keywords, arm_index)
        if not bg:
            return bg, basis
        arms = [str(a.get("name") if isinstance(a, dict) else a) for a in (rec.get("interventions") or [])]
        ctrl = [a for a in arms if _CONTROLISH.search(a)]
        kw = [k.lower() for k in keywords] + [c.lower() for k in keywords for c in DEV_CODES.get(k.lower(), [])] +             [t.lower() for t in (cfg2.get("include") or {}).get("intervention_any") or []]
        act = [a for a in arms if a not in ctrl and any(k in a.lower() for k in kw)]
        if ctrl and act:
            f1_hits[str(rec.get("id"))] = f"F1: placebo/control arm {ctrl[0][:60]!r} beside {act[0][:60]!r}"
            return False, ""
        return bg, basis
    screen._background_only_randomised_contrast = bg_fixed
    try:
        new = {d["id"]: d for d in screen.run(merged2, cfg2)["decisions"]}
    finally:
        screen._background_only_randomised_contrast = orig_bg
    flips, still = [], []
    for i in excl:
        b, n = base[i], new.get(i) or {}
        rec = rec_by_id.get(i) or {}
        row = {"id": i, "label": b.get("label"), "title": (rec.get("title") or "")[:200], "nct": rec.get("nct"),
               "before": {k: b.get(k) for k in ("rule_id", "reason", "span")},
               "after": {k: n.get(k) for k in ("decision", "rule_id", "reason", "span")},
               "fixes": rec_fix.get(i, ([], {}))[0] + ([f1_hits[str(i)]] if str(i) in f1_hits else []),
               "curated_eviction": str(i) in curated}
        (flips if n.get("decision") == "include" else still).append(row)
    out = {"slug": slug, "n_records": len(merged), "baseline_vs_served": {"served": len(served), "agree": agree},
           "baseline_vs_build": {"build": len(build), "agree": rebuild_agree},
           "overlay": applied, "n_excluded_x2_x3_contrast": len(excl), "flips": flips,
           "flip_count": len(flips), "flip_by_rule": {r: sum(1 for f in flips if f["before"]["rule_id"] == r) for r in EXCL},
           "still_excluded": len(still),
           "still_changed_rule": [r for r in still if (r["after"].get("rule_id") != r["before"].get("rule_id"))]}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{slug}.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return out


def main(argv):
    slugs = [a for a in argv if not a.startswith("--")]
    if "--all" in argv:
        slugs = sorted(d for d in os.listdir(os.path.join(ROOT, "docs", "reviews"))
                       if os.path.exists(os.path.join(ROOT, "docs", "reviews", d, "review.json")))
    summ = {}
    for s in slugs:
        try:
            o = run_topic(s)
            summ[s] = {k: o[k] for k in ("n_excluded_x2_x3_contrast", "flip_count", "flip_by_rule", "baseline_vs_served")}
            print(f"{s}: excluded {o['n_excluded_x2_x3_contrast']} -> flips {o['flip_count']} {o['flip_by_rule']} "
                  f"| baseline agrees with served {o['baseline_vs_served']['agree']}/{o['baseline_vs_served']['served']}",
                  flush=True)
        except Exception as exc:  # noqa: BLE001 - one topic's failure is reported, never hidden
            summ[s] = {"error": f"{type(exc).__name__}: {str(exc)[:300]}"}
            print(s, "ERROR", summ[s]["error"], flush=True)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "_summary.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(summ, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
