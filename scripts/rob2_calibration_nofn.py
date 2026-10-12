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
V2 = os.path.join(ROOT, "outputs", "robgrade", "calibration_v2_extended.json")
V3 = os.path.join(ROOT, "outputs", "robgrade", "calibration.json")
FREEZE = os.path.join(ROOT, "outputs", "robgrade", "freeze_v3.json")
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


def _frozen():
    """v3's TEST number belongs to v3 only if no frozen file changed after the freeze."""
    import hashlib
    fz = json.load(open(FREEZE, encoding="utf-8"))
    bad = [f for f, h in fz["files_sha256"].items()
           if not f.startswith("outputs/robgrade/dev/")
           and hashlib.sha256(open(os.path.join(ROOT, f), "rb").read()).hexdigest() != h]
    if bad:
        raise SystemExit(f"REFUSED: changed after the v3 freeze: {bad}")
    return fz


def main():
    fz = _frozen()
    cals = [json.load(open(f, encoding="utf-8")) for f in (V1, V2, V3)]
    slugs = set(cals[2]["topics"])                     # the same four CC comparators in all three
    t = [tally(c, slugs) for c in cals]
    lines = ["# RoB 2 calibration: agreement with the published comparator judgements, n of N", "",
             f"Comparators: {', '.join(sorted(slugs))}. v1 = abstract + ClinicalTrials.gov text; v2 = v1 + extended regex "
             "over held open-access full texts (Mahmood 12 Oct, 'extend'); v3 = v2 + rules mined on DEV only "
             f"(frozen {fz['frozen_utc']}, outputs/robgrade/freeze_v3.json) and evaluated ONCE on these TEST trials. "
             "v2's rules were partly written after reading TEST phrasing (in-sample); v3's additions were not.", "",
             "| domain | v1 agree / N (excl.) | v2 agree / N (excl.) | v3 agree / N (excl.) | v3, full-text answered |",
             "|---|---|---|---|---|"]
    for d in DOMS:
        cells = " | ".join(f"{x[d]['agree']} / {x[d]['N']} ({x[d]['excluded']})" for x in t)
        lines.append(f"| {d} | {cells} | {t[2][d]['ft_agree']} / {t[2][d]['ft_N']} |")
    tot = " | ".join(f"{sum(x[d]['agree'] for d in DOMS)} / {sum(x[d]['N'] for d in DOMS)}" for x in t)
    lines.append(f"| all | {tot} | {sum(t[2][d]['ft_agree'] for d in DOMS)} / {sum(t[2][d]['ft_N'] for d in DOMS)} |")
    key = lambda p: (p["slug"], p.get("pmid") or p.get("trial"), p["domain"])
    v2p, v3p = {key(p): p for p in cals[1]["pairs"]}, {key(p): p for p in cals[2]["pairs"]}
    moved = [(k, v2p[k]["ours"], v3p[k]["ours"], v3p[k]["theirs"]) for k in sorted(set(v2p) & set(v3p))
             if v2p[k]["ours"] != v3p[k]["ours"]]
    lines += ["", f"Pairs whose judgement changed v2 -> v3: {len(moved)}"]
    lines += [f"- {k[0]} {k[1]} {k[2]}: {a} -> {b} (comparator {c})" for k, a, b, c in moved]
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
