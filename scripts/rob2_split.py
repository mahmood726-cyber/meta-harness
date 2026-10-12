"""FROZEN split for RoB 2 rule development (AGENTS.md held-out rule). TEST = the calibration trials (every trial a
published comparator RoB figure rates, outputs/robgrade/calibration.json): no rule may be tuned on them. DEV = every
trial in any served review's outcomes (docs/reviews/*/review.json), minus TEST. Written once to
outputs/robgrade/split.json with its seed-free rule and the sha256 of each list; a later run that would change the
frozen TEST set refuses.

    python scripts/rob2_split.py            (write once; verify thereafter)
"""
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "robgrade", "split.json")


def served_trials():
    out = set()
    d = os.path.join(ROOT, "docs", "reviews")
    for slug in sorted(os.listdir(d)):
        p = os.path.join(d, slug, "review.json")
        if not os.path.exists(p):
            continue
        r = json.load(open(p, encoding="utf-8"))
        for o in r.get("outcomes") or []:
            for t in o.get("trials") or []:
                m = re.search(r"PMID (\d+)", str(t.get("id")))
                if m:
                    out.add(m.group(1))
    return out


def h(xs):
    return hashlib.sha256("\n".join(sorted(xs)).encode()).hexdigest()


def main():
    cal = json.load(open(os.path.join(ROOT, "outputs", "robgrade", "calibration_v1_abstract_registry.json"), encoding="utf-8"))
    test = sorted({p["pmid"] for p in cal["pairs"]} | {p["pmid"] for p in cal["excluded"]})
    dev = sorted(served_trials() - set(test))
    obj = {"rule": "TEST = trials rated by a published comparator RoB figure in the v1 calibration (pairs + excluded); "
                   "DEV = trials of any served outcome, minus TEST. Frozen 2026-10-12, before any v3 rule.",
           "test": test, "test_sha256": h(test), "dev": dev, "dev_sha256": h(dev),
           "note": "v2 rules (12 Oct) were written after reading phrasing samples from TEST full texts: v2's TEST "
                   "numbers are partly in-sample, and are reported as such."}
    if os.path.exists(OUT):
        old = json.load(open(OUT, encoding="utf-8"))
        if old["test_sha256"] != obj["test_sha256"]:
            raise SystemExit(f"REFUSED: the frozen TEST set would change ({old['test_sha256'][:12]} -> {obj['test_sha256'][:12]})")
        print("split verified:", len(old["test"]), "TEST,", len(old["dev"]), "DEV")
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1)
    print("split written:", len(test), "TEST,", len(dev), "DEV")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
