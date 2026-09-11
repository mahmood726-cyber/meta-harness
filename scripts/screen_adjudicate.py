"""Genuinely-INDEPENDENT model screener (PRISMA item 8, honest v2). The two rule screeners flag
disagreements; a capable MODEL adjudicates the CONTENT-BEARING ones (different information + method =
real independence, unlike the two correlated rule sets). ADVISORY: rendered model-derived, screener 1
remains the served decision, so it changes NO pooled number. Judgment = a source (5 checkable fields,
cached to cache/<slug>/screen_adjudication.json, committed, replayed offline).

  python scripts/screen_adjudicate.py <slug> --prompts        # emit per-record eligibility prompts
  python scripts/screen_adjudicate.py <slug> --write judg.json # validate + commit model judgments
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQ = ("is_eligible", "population_match", "design_match", "intervention_match", "rationale")


def disagreements(slug):
    rev = json.load(open(f"{ROOT}/docs/reviews/{slug}/review.json", encoding="utf-8"))
    recs = {r["id"]: r for r in json.load(open(f"{ROOT}/cache/{slug}/records.json", encoding="utf-8"))["records"]}
    dual = (rev.get("screening") or {}).get("dual") or {}
    cfg = json.load(open(f"{ROOT}/topics/{slug}.json", encoding="utf-8"))
    out = []
    for d in dual.get("disagreements", []):
        pid = str(d["id"])
        r = recs.get(pid, {})
        if pid.isdigit() and (r.get("abstract") or r.get("title")):
            out.append((pid, r, d))
    return cfg, out


def prompt(cfg, r):
    inc = cfg.get("include", {})
    pico = (f"Population: one of {inc.get('population_any')} (NOT {inc.get('population_none')}); "
            f"Intervention: {inc.get('intervention_any')}; Comparator: {inc.get('comparator_any')}; "
            f"Design: {'double-blind/placebo-controlled RCT' if inc.get('design_double_blind') else 'RCT'}.")
    return (f"Decide if THIS trial is eligible for a meta-analysis with these criteria.\n{pico}\n\n"
            f"TITLE: {r.get('title')}\nABSTRACT: {(r.get('abstract') or '')[:1200]}\n\n"
            'Reply ONLY JSON: {"is_eligible":true|false,"population_match":"...","design_match":"...",'
            '"intervention_match":"...","rationale":"one sentence"}')


def main(argv):
    slug = argv[0]
    cfg, dis = disagreements(slug)
    if "--prompts" in argv:
        for pid, r, d in dis:
            print("=" * 70); print(f"PMID {pid} (rule1={d['screener1']} rule2={d['screener2']})")
            print(prompt(cfg, r))
        return 0
    if "--write" in argv:
        src = argv[argv.index("--write") + 1]
        j = json.load(open(src, encoding="utf-8"))
        j = j.get("judgments", j)
        for pid, jr in j.items():
            miss = [f for f in REQ if f not in jr]
            if miss or not isinstance(jr.get("is_eligible"), bool):
                print(f"REFUSE: {pid} invalid ({miss or 'is_eligible not bool'})", file=sys.stderr); return 2
        json.dump({"model": "adjudicator", "judgments": j}, open(f"{ROOT}/cache/{slug}/screen_adjudication.json", "w",
                  encoding="utf-8", newline=""), indent=2, ensure_ascii=False)
        # disagreement of model vs served rule-1 decision
        agree_rule1 = sum(1 for pid, r, d in dis if j.get(pid, {}).get("is_eligible") == (d["screener1"] == "include"))
        print(f"wrote {len(j)} model judgments; model agrees with served rule-1 on {agree_rule1}/{len(dis)} disagreements")
        return 0
    print(f"{slug}: {len(dis)} content-bearing disagreements to adjudicate")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
