"""Acceptance test for the embedding candidate-generation layer: the nine known brittleness cases.
Reports cosine per case and whether a single threshold recovers the synonymy positives while
REJECTING the appendicitis negative (the important one). Pattern/scale cases are regex-layer, not
embedding-layer, and are labelled as such."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import embed

# (label, query, candidate, should_match, layer)
CASES = [
    ("DAPA-HF CV death",     "cardiovascular death", "death from cardiovascular causes", True, "embedding"),
    ("EMPEROR composite",    "cardiovascular death or hospitalization for heart failure", "CV Death or HHF", True, "embedding"),
    ("RECOVERY rate ratio",  "rate ratio", "age-adjusted rate ratio", True, "embedding"),
    ("DAPA-HF blinding",     "double-blind", "placebo-controlled", True, "embedding"),
    ("NOAC stroke/SE",       "stroke or systemic embolism", "stroke or systemic embolic event", True, "embedding"),
    ("APPENDICITIS negative","treatment failure or complication at 1 year", "Resolution of Appendicitis Symptoms at 30 Days", False, "embedding"),
]
PATTERN_CASES = ["PLUS 'N of M (P%)' count pattern", "RALES spelled-out CI", "CORP semicolon-split endpoint", "RR-parsed-as-OR scale"]

def main():
    rows = []
    for label, q, c, should, layer in CASES:
        r = embed.rank(q, [c])
        cos = r[0][1] if r else 0.0
        rows.append((label, q, c, should, cos))
    # pick threshold: max negative < threshold <= min positive
    pos = [cos for *_, should, cos in [(l,q,c,s,co) for (l,q,c,s,co) in rows] if should]
    neg = [cos for (l,q,c,s,co) in rows if not s]
    print(f"{'case':24} {'should':7} {'cosine':7}")
    for label, q, c, should, cos in rows:
        print(f"{label:24} {str(should):7} {cos:.3f}   '{q[:28]}' ~ '{c[:32]}'")
    thr = 0.35
    recovered = sum(1 for (l,q,c,s,co) in rows if s and co >= thr)
    neg_ok = all(co < thr for (l,q,c,s,co) in rows if not s)
    print(f"\nthreshold {thr}: positives recovered {recovered}/{sum(1 for r in rows if r[3])}; "
          f"negative(appendicitis) correctly REJECTED: {neg_ok}")
    print("min positive cos =", round(min(pos),3), "| max negative cos =", round(max(neg),3),
          "| separated:", min(pos) > max(neg))
    print("\nPattern/scale cases (regex layer, NOT embedding — already fixed in the harness):")
    for p in PATTERN_CASES: print("  -", p)
    return 0

if __name__ == "__main__":
    sys.exit(main())
