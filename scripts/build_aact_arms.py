"""Generate cache/<slug>/verified_arms.json from the committed AACT snapshot — HARNESS-DERIVED, not
hand-typed. For each topic's committed `aact_arm_trials` spec (pmid + outcome terms = a query, not a
number), harness.aact.summed_arms discovers the trial's registrations from study_references, aligns
arms by result-group title, sums per arm, and refuses recurrent-event outcomes. The counts are then
CROSS-CHECKED against the trial's abstract percentages (a round-trip); an entry is written only if it
reconciles. So the committed number is produced by committed code from committed AACT and validated
against the paper — reproducible by anyone with the snapshot, and the former hand-verified tier is now
a derived+audited tier.

  python scripts/build_aact_arms.py            # regenerate verified_arms.json for all specced topics

Fresh-clone note: AACT is a local snapshot, so this is a cache-population step (like fetch), run where
AACT is present; the committed verified_arms.json is what replay/fresh-clone reads.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import aact  # noqa: E402


def _pct_in(text, pct):
    s = (text or "").replace("·", ".")
    return bool(re.search(rf"(?<!\d){re.escape(f'{pct:g}')}(?!\d)", s))


def main(argv):
    if not aact.snapshot_dir():
        print("AACT snapshot not found"); return 2
    n_written = 0
    for f in sorted(os.listdir(os.path.join(ROOT, "topics"))):
        if not f.endswith(".json"):
            continue
        slug = f[:-5]
        cfg = json.load(open(os.path.join(ROOT, "topics", f), encoding="utf-8"))
        specs = cfg.get("aact_arm_trials") or []
        if not specs:
            continue
        recs_p = os.path.join(ROOT, "cache", slug, "records.json")
        recs = {r["id"]: r for r in json.load(open(recs_p, encoding="utf-8"))["records"]} if os.path.exists(recs_p) else {}
        iv, cp = cfg.get("intervention_terms") or [], cfg.get("comparator_terms") or []
        entries = {}
        for spec in specs:
            pmid = str(spec["pmid"])
            arms = aact.summed_arms(pmid, iv, cp, [t.lower() for t in spec["outcome_terms"]])
            if not arms:
                print(f"{slug}/{pmid}: summed_arms returned None (no clean AACT arms / recurrent) — SKIP")
                continue
            ab = recs.get(pmid, {}).get("abstract", "")
            pA = round(100 * arms["ai"] / arms["n1i"], 1)
            pC = round(100 * arms["ci"] / arms["n2i"], 1)
            if not (_pct_in(ab, pA) and _pct_in(ab, pC)):
                print(f"{slug}/{pmid}: derived {pA}%/{pC}% NOT corroborated by abstract — REFUSE (no entry)")
                continue
            regs = ", ".join(arms["registrations"])
            entries[pmid] = {
                "outcome": spec["outcome"],
                "ai": arms["ai"], "n1i": arms["n1i"], "ci": arms["ci"], "n2i": arms["n2i"],
                "provenance": "aact_verified",
                "source": (f"AACT structured '{arms['outcome_title']}' summed across {regs} "
                           f"(harness-derived by scripts/build_aact_arms.py via aact.summed_arms: registrations "
                           f"discovered from study_references, arms aligned by result-group title, recurrent-event "
                           f"guarded). Cross-checked to the abstract: {arms['ai']}/{arms['n1i']}={pA}% and "
                           f"{arms['ci']}/{arms['n2i']}={pC}% match the published percentages."),
                "verification": f"AACT-derived + abstract-corroborated ({pA}% / {pC}%); regenerable from the snapshot.",
            }
            print(f"{slug}/{pmid}: {arms['ai']}/{arms['n1i']}, {arms['ci']}/{arms['n2i']} "
                  f"({pA}%/{pC}%) from {regs} — WRITTEN")
        if entries:
            os.makedirs(os.path.join(ROOT, "cache", slug), exist_ok=True)
            json.dump(entries, open(os.path.join(ROOT, "cache", slug, "verified_arms.json"), "w",
                                    encoding="utf-8", newline=""), indent=2, ensure_ascii=False)
            n_written += len(entries)
    print(f"\nwrote {n_written} harness-derived arm entries")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
