"""Uniform comparator SCOPE-MATCH audit (PICO-match), applied to ALL topics by one rule decided before
seeing the k. A comparator is a valid benchmark only if it answers the SAME question. The key axis is
intervention LEVEL: a SINGLE-drug topic benchmarked against a drug-CLASS meta-analysis is a PICO
mismatch (the NMA error class — the network is not one drug), even when the class meta happens to name
our drug. The rule is applied mechanically; the tally is reported including topics where we look good.

Records per topic: {intervention_level_match, population_match, scope_valid, ...}. Writes
docs/scope_audit.json. Non-number-changing.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Drug-CLASS indicators: a title naming a class rather than a single agent.
_CLASS_TERMS = ["inhibitors", "antagonists", "agonists", "sglt2", "sglt-2", "glp-1", "glp1",
                "mineralocorticoid receptor", "statins", "anticoagulants", "receptor blocker",
                "beta-blockers", "ace inhibitor", " arb ", "doac", "noac", "crystalloids"]


def _has_any(text, terms):
    t = (text or "").lower()
    return next((x for x in terms or [] if x and x.lower() in t), None)


def main(argv):
    base = os.path.join(ROOT, "docs", "reviews")
    out, invalid = {}, []
    for slug in sorted(os.listdir(base)):
        rp = os.path.join(base, slug, "review.json")
        if not os.path.exists(rp):
            continue
        rev = json.load(open(rp, encoding="utf-8"))
        cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
        comp = rev.get("comparator") or {}
        ctitle = comp.get("name") or ""
        inc = cfg.get("include", {})
        topic_terms = (cfg.get("intervention_terms") or []) + (inc.get("intervention_any") or [])
        topic_is_class = _has_any(" ".join(topic_terms), _CLASS_TERMS) is not None
        comparator_is_class = _has_any(ctitle, _CLASS_TERMS) is not None
        # intervention-level mismatch: comparator is a class review but the topic is a single drug
        iv_level_match = not (comparator_is_class and not topic_is_class)
        cpm = str(comp.get("pmid") or "")
        recs = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))["records"]}
        ctext = ctitle + " " + (recs.get(cpm, {}).get("abstract") or "")
        pop = _has_any(ctext, inc.get("population_any") or [])
        scope_valid = bool(iv_level_match and pop)
        out[slug] = {"pmid": cpm, "topic_is_class": topic_is_class, "comparator_is_class": comparator_is_class,
                     "intervention_level_match": iv_level_match, "population_match": bool(pop),
                     "scope_valid": scope_valid,
                     "note": ("same-question comparator" if scope_valid else
                              ("comparator is a DRUG-CLASS meta-analysis but this topic is a single agent — "
                               "PICO scope mismatch (single-drug review vs class-level review); the k gap is a "
                               "scope difference, not unretrieved evidence" if not iv_level_match else
                               "comparator population does not clearly match the topic"))}
        if not scope_valid:
            invalid.append(slug)
    json.dump(out, open(os.path.join(ROOT, "docs", "scope_audit.json"), "w", encoding="utf-8", newline=""), indent=1)
    print(f"{'topic':42} {'topicCls':8} {'compCls':7} {'ivMatch':7} {'pop':4} valid")
    for s, v in out.items():
        print(f"{s:42} {str(v['topic_is_class']):8} {str(v['comparator_is_class']):7} "
              f"{str(v['intervention_level_match']):7} {'Y' if v['population_match'] else '.':4} "
              f"{'VALID' if v['scope_valid'] else 'MISMATCH'}")
    print(f"\ncomparators INVALID by uniform scope rule: {len(invalid)}/{len(out)} -> {invalid}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
