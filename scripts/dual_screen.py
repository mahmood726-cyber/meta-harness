"""Automated DUAL independent screening + disagreement rate (PRISMA 8 / AMSTAR-2 duplicate-selection).
Screener 1 = the deterministic rule screen (the served decision, the adjudicator). Screener 2 = a
genuinely independent embedding reader: cosine(record title, the PICO string) >= threshold => an
include-candidate. We report the DISAGREEMENT RATE at an a-priori threshold; the rule screener remains
the decider (embedding never lowers the eligibility bar). Writes committed cache/<slug>/screening2.json.

    python scripts/dual_screen.py [--write] [<slug> ...]
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import embed

THR = 0.30  # a-priori; the disagreement rate is descriptive, not tuned to agree

def pico_text(cfg):
    inc = cfg.get("include", {})
    pop = (inc.get("population_any") or ["patients"])[0]
    itv = (inc.get("intervention_any") or cfg.get("intervention_terms") or ["intervention"])[0]
    cmp = (inc.get("comparator_any") or ["placebo"])[0]
    return f"randomized controlled trial of {itv} versus {cmp} in {pop}"

def main(argv):
    write = "--write" in argv
    slugs = [a for a in argv if not a.startswith("-")] or [
        s for s in sorted(os.listdir(f"{ROOT}/docs/reviews"))
        if os.path.exists(f"{ROOT}/docs/reviews/{s}/review.json")]
    print(f"{'topic':42} {'n':>4} {'agree':>6} {'disagree%':>9}")
    for slug in slugs:
        cfg = json.load(open(f"{ROOT}/topics/{slug}.json", encoding="utf-8"))
        rev = json.load(open(f"{ROOT}/docs/reviews/{slug}/review.json", encoding="utf-8"))
        recs = {r["id"]: r for r in json.load(open(f"{ROOT}/cache/{slug}/records.json", encoding="utf-8"))["records"]}
        pico = pico_text(cfg)
        titles = []
        rows = []
        for d in rev["screening"]["records"]:
            pid = str(d["id"]).split("·")[-1].strip()
            title = (recs.get(pid, {}) or {}).get("title") or ""
            rows.append((pid, d["decision"], title))
            if title:
                titles.append(title)
        vecs = embed.embed([pico] + titles)
        pv = vecs.get(pico)
        agree = disagree = scored = 0
        dis = []
        for pid, decision, title in rows:
            if not title or title not in vecs or pv is None:
                continue
            sim = embed.cosine(pv, vecs[title])
            s2 = "include" if sim >= THR else "exclude"
            scored += 1
            if s2 == decision:
                agree += 1
            else:
                disagree += 1
                dis.append({"id": pid, "rule": decision, "embed": s2, "sim": round(sim, 3)})
        rate = round(100 * disagree / scored, 1) if scored else None
        print(f"{slug:42} {scored:>4} {agree:>6} {str(rate):>9}")
        if write:
            out = {"method": f"rule-based + embedding ({embed.MODEL_ID}); adjudicator=rule-based",
                   "threshold": THR, "pico": pico, "n_scored": scored, "agree": agree,
                   "disagree": disagree, "disagreement_rate_pct": rate,
                   "disagreements": dis[:60]}
            json.dump(out, open(f"{ROOT}/cache/{slug}/screening2.json", "w", encoding="utf-8", newline=""),
                      indent=2, ensure_ascii=False)
    if write:
        print("\nwrote cache/<slug>/screening2.json")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
