"""Census of harness/verify.py's 'verified' label over the served review.json files -- WHICH BYTES each pooled row's label was
checked against. Rule, read from harness/verify.py at git blob e5187ea9cc8e (verify_pooled, lines 65-107):

  line 73   text = abstract  if provenance in ("abstract", "pmc_fulltext", "abstract_verified")  else  row["source"]
            -> for every other provenance the haystack is the row's own hand-written `source` field: the needle is checked against
               the text the same process supplied. This is the HAYSTACK defect.
  line 75   provenance == "aact_verified" with counts -> returns "verified_handchecked" with NO check at all (UNCONDITIONAL).
  line 78   provenance == "published_rate" -> percentage round-trip against the ABSTRACT (a real check of the abstract).
  line 88+  counts / continuous (mean, sd) / events / effect: digits of the value searched in `text`; the CI is never checked, the
            RRR complement is accepted (line 58), the effect measure is never compared.

Populations (denominators printed, never only counts):
  per-arm rows  = rows carrying ai/n1i/ci/n2i (counts) or mean1/sd1 (continuous)   -- one lane counted counts only (46), another
                  counts+continuous (53); this script prints both so the two censuses reconcile by rows, not totals
  effect rows   = rows carrying effect/ci_low/ci_high and no per-arm values
Usage: python scripts/verify_label_census.py [--json out.json]"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ABSTRACT_PROVS = ("abstract", "pmc_fulltext", "abstract_verified")


def classify(t: dict) -> tuple[str, str]:
    """(value_kind, haystack) per verify_pooled's branches."""
    prov = t.get("provenance")
    if t.get("ai") is not None:
        kind = "COUNT"
        if prov == "aact_verified":
            return kind, "NONE_UNCONDITIONAL"
        if prov == "published_rate":
            return kind, "ABSTRACT_PERCENT_ROUNDTRIP"
    elif t.get("mean1") is not None:
        kind = "CONTINUOUS"
    elif t.get("e1i") is not None:
        kind = "EVENTS"
    elif t.get("effect") is not None:
        kind = "EFFECT"
    else:
        return "NONE", "NONE"
    return kind, ("ABSTRACT" if prov in ABSTRACT_PROVS else "SOURCE_FIELD_SELF")


def census(root: Path) -> dict:
    rows = []
    for rp in sorted(glob.glob(str(root / "docs" / "reviews" / "*" / "review.json"))):
        slug = os.path.basename(os.path.dirname(rp))
        r = json.load(open(rp, encoding="utf-8"))
        for o in r.get("outcomes", []):
            for t in o.get("trials") or []:
                kind, hay = classify(t)
                rows.append({"slug": slug, "id": str(t.get("id")), "outcome": o.get("name"), "primary": bool(o.get("primary")),
                             "provenance": t.get("provenance"), "verified": t.get("verified"), "kind": kind, "haystack": hay})
    def n(pred):
        return [x for x in rows if pred(x)]
    counts = n(lambda x: x["kind"] == "COUNT"); cont = n(lambda x: x["kind"] == "CONTINUOUS"); per_arm = counts + cont
    effects = n(lambda x: x["kind"] == "EFFECT")
    out = {
        "rule": "harness/verify.py blob e5187ea9cc8e, verify_pooled lines 65-107; haystack per line 73; unconditional per lines 75-76; published_rate checks the abstract per lines 78-87",
        "rows_in_served_pools": len(rows),
        "count_rows": {"denominator": len(counts), "self_checked": len([x for x in counts if x["haystack"] == "SOURCE_FIELD_SELF"]),
                       "unconditional": len([x for x in counts if x["haystack"] == "NONE_UNCONDITIONAL"]),
                       "abstract_checked": len([x for x in counts if x["haystack"].startswith("ABSTRACT")])},
        "per_arm_rows_counts_plus_continuous": {"denominator": len(per_arm), "self_checked": len([x for x in per_arm if x["haystack"] == "SOURCE_FIELD_SELF"]),
                                                "unconditional": len([x for x in per_arm if x["haystack"] == "NONE_UNCONDITIONAL"]),
                                                "abstract_checked": len([x for x in per_arm if x["haystack"].startswith("ABSTRACT")])},
        "effect_rows": {"denominator": len(effects), "self_checked": len([x for x in effects if x["haystack"] == "SOURCE_FIELD_SELF"]),
                        "abstract_checked": len([x for x in effects if x["haystack"] == "ABSTRACT"])},
        "self_checked_by_provenance": dict(Counter(x["provenance"] for x in rows if x["haystack"] == "SOURCE_FIELD_SELF")),
        "unconditional_rows": [x for x in rows if x["haystack"] == "NONE_UNCONDITIONAL"],
        "glp1_self_checked_rows": [x for x in rows if x["slug"] == "glp1-ra-mace-t2d" and x["haystack"] == "SOURCE_FIELD_SELF"],
        "rows": rows,
    }
    return out


def main(argv=None):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(); ap.add_argument("--json", default=None); a = ap.parse_args(argv)
    c = census(ROOT)
    print("RULE:", c["rule"])
    for k in ("count_rows", "per_arm_rows_counts_plus_continuous", "effect_rows"):
        v = c[k]; print(f"{k}: " + ", ".join(f"{kk}={vv}" for kk, vv in v.items()))
    print("self-checked by provenance:", c["self_checked_by_provenance"])
    print("unconditional rows:", [(x["slug"], x["id"]) for x in c["unconditional_rows"]])
    print("glp1-ra-mace-t2d self-checked rows:", [(x["id"], x["outcome"], x["provenance"], x["verified"]) for x in c["glp1_self_checked_rows"]])
    if a.json:
        Path(a.json).write_text(json.dumps(c, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
