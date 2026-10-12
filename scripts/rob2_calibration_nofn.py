"""Calibration agreement as n of N (Mahmood, 12 Oct), before (v1: abstract + registry) and after (v2: extended regex
over held OA full texts), per domain and for the stratum whose domain had any answer from a full text. N is every
(trial, domain) pair both sides rated; pairs excluded (ours INSUFFICIENT_OPEN_SOURCE, or the reference cell unmapped /
unresolved) are COUNTED beside it, never dropped silently.

    python scripts/rob2_calibration_nofn.py   -> outputs/robgrade/CALIBRATION_NOFN.md
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V1 = os.path.join(ROOT, "outputs", "robgrade", "calibration_v1_abstract_registry.json")
V2 = os.path.join(ROOT, "outputs", "robgrade", "calibration.json")
OUT = os.path.join(ROOT, "outputs", "robgrade", "CALIBRATION_NOFN.md")
DOMS = ("D1", "D2", "D3", "D4", "D5")


def tally(cal, slugs=None):
    ps = [p for p in cal["pairs"] if slugs is None or p["slug"] in slugs]
    ex = [p for p in cal["excluded"] if slugs is None or p["slug"] in slugs]
    out = {}
    for d in DOMS:
        xs = [p for p in ps if p["domain"] == d]
        ft = [p for p in xs if p.get("from_full_text")]
        out[d] = {"agree": sum(p["ours"] == p["theirs"] for p in xs), "N": len(xs),
                  "ft_agree": sum(p["ours"] == p["theirs"] for p in ft), "ft_N": len(ft),
                  "excluded": sum(1 for p in ex if p["domain"] == d)}
    return out


def main():
    v1, v2 = json.load(open(V1, encoding="utf-8")), json.load(open(V2, encoding="utf-8"))
    slugs = set(v2["topics"])                          # the same four CC comparators in both
    a, b = tally(v1, slugs), tally(v2, slugs)
    lines = ["# RoB 2 calibration: agreement with the published comparator judgements, n of N", "",
             f"Comparators: {', '.join(sorted(slugs))}. v1 = abstract + ClinicalTrials.gov text; v2 = v1 + extended regex "
             "over held open-access full texts (Mahmood 12 Oct, 'extend').", "",
             "| domain | v1 agree / N (excluded) | v2 agree / N (excluded) | v2, domains with a full-text answer |",
             "|---|---|---|---|"]
    for d in DOMS:
        x, y = a[d], b[d]
        lines.append(f"| {d} | {x['agree']} / {x['N']} ({x['excluded']}) | {y['agree']} / {y['N']} ({y['excluded']}) | "
                     f"{y['ft_agree']} / {y['ft_N']} |")
    ta, tb = (sum(t[d]["agree"] for d in DOMS) for t in (a, b)), None
    sa_agree, sa_n = sum(a[d]["agree"] for d in DOMS), sum(a[d]["N"] for d in DOMS)
    sb_agree, sb_n = sum(b[d]["agree"] for d in DOMS), sum(b[d]["N"] for d in DOMS)
    sb_ft_agree, sb_ft_n = sum(b[d]["ft_agree"] for d in DOMS), sum(b[d]["ft_N"] for d in DOMS)
    lines.append(f"| all | {sa_agree} / {sa_n} | {sb_agree} / {sb_n} | {sb_ft_agree} / {sb_ft_n} |")
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
