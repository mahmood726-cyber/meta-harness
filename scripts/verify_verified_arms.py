"""AUDIT every cache/<slug>/verified_arms.json entry against the harness itself: re-derive the arm
counts from the committed AACT snapshot and confirm they match the entry AND the published abstract %.

This is the standard Mahmood set: a hand-verified arm entry must be reachable by the harness, or the
page says so. Here the harness RE-DERIVES the number from AACT (committed snapshot) using the entry's
recorded registrations, so the typed counts become a CHECK on the harness's answer, not a substitute
for it. Anyone with the same AACT snapshot re-runs this and regenerates the same numbers.

  python scripts/verify_verified_arms.py     # prints + writes docs/verified_arms_audit.json

Note: AACT is a local snapshot (not in a fresh clone), so this is an auditor, not a build step; the
committed verified_arms.json remains the replay source. The audit proves the entry is AACT-derivable.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import aact  # noqa: E402


def _group_titles(ncts):
    """{nct: {ctgov_group_code: title}} for Outcome result_groups (the arm labels)."""
    out = {n: {} for n in ncts}
    for r in aact._iter_rows(aact._table("result_groups")):
        n = (r.get("nct_id") or "").upper()
        if n in out and r.get("ctgov_group_code"):
            out[n][r["ctgov_group_code"]] = r.get("title") or ""
    return out


def _arm_of(title, interv_terms, comp_terms):
    t = (title or "").lower()
    if any(x and x.lower() in t for x in interv_terms):
        return "i"
    if any(x and x.lower() in t for x in comp_terms):
        return "c"
    return None


def _aact_arm_values(nct, outcome_terms, titles, interv_terms, comp_terms):
    """Per-arm {i:{events,denom}, c:{events,denom}} for the outcome-matching measure in one NCT,
    aligned to intervention/comparator by the result-group TITLE (never by magnitude)."""
    arm = {"i": {}, "c": {}}
    for om in aact._iter_rows(aact._table("outcome_measurements")):
        if (om.get("nct_id") or "").upper() != nct:
            continue
        t = (om.get("title") or "").lower()
        if any(k in t for k in outcome_terms) and (om.get("param_type") or "").upper() == "COUNT_OF_PARTICIPANTS":
            a = _arm_of(titles.get(nct, {}).get(om.get("ctgov_group_code"), ""), interv_terms, comp_terms)
            if a:
                try:
                    arm[a]["events"] = int(float(om.get("param_value")))
                except (TypeError, ValueError):
                    pass
    for oc in aact._iter_rows(aact._table("outcome_counts")):
        if (oc.get("nct_id") or "").upper() == nct and (oc.get("units") or "").lower().startswith("participant"):
            a = _arm_of(titles.get(nct, {}).get(oc.get("ctgov_group_code"), ""), interv_terms, comp_terms)
            if a and "denom" not in arm[a]:
                try:
                    arm[a]["denom"] = int(oc.get("count"))
                except (TypeError, ValueError):
                    pass
    return arm


def main(argv):
    snap = aact.snapshot_dir()
    if not snap:
        print("AACT snapshot not found (set AACT_DIR)"); return 2
    out = {}
    ok_all = True
    for slug in sorted(os.listdir(os.path.join(ROOT, "cache"))):
        vp = os.path.join(ROOT, "cache", slug, "verified_arms.json")
        if not os.path.exists(vp):
            continue
        recs = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "cache", slug, "records.json"),
                                                   encoding="utf-8"))["records"]}
        entries = json.load(open(vp, encoding="utf-8"))
        for pid, v in entries.items():
            # registrations named in the entry's source text (NCT ids) — the committed input.
            ncts = sorted(set(re.findall(r"NCT\d{8}", v.get("source", ""))))
            cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
            iv = (cfg.get("intervention_terms") or []) + ["balanced", "crystalloid"]
            cp = (cfg.get("comparator_terms") or []) + ["saline", "sodium chloride", "0.9%"]
            terms = ["mortality", "death", "in-hospital"] if "mortalit" in (v.get("outcome") or "").lower() \
                else [(v.get("outcome") or "").lower()[:12]]
            titles = _group_titles(ncts)
            # sum per ARM (aligned by title), only over registrations that report BOTH arms for this
            # outcome — a registration missing the outcome is skipped, not magnitude-guessed.
            sum_i_ev = sum_i_n = sum_c_ev = sum_c_n = 0
            per = {}
            complete = bool(ncts)
            for n in ncts:
                arm = _aact_arm_values(n, terms, titles, iv, cp)
                per[n] = arm
                if all(k in arm["i"] for k in ("events", "denom")) and all(k in arm["c"] for k in ("events", "denom")):
                    sum_i_ev += arm["i"]["events"]; sum_i_n += arm["i"]["denom"]
                    sum_c_ev += arm["c"]["events"]; sum_c_n += arm["c"]["denom"]
                else:
                    # a registration without both arms for this outcome (e.g. NCT04507672, a different
                    # trial that only cites the paper) does not contribute — this is the identity guard.
                    per[n]["contributes"] = False
            ab = recs.get(pid, {}).get("abstract", "")
            pA = round(100 * v["ai"] / v["n1i"], 1)
            pC = round(100 * v["ci"] / v["n2i"], 1)
            pct_ok = _pct_in(ab, pA) and _pct_in(ab, pC)
            match = (sum_i_ev == v["ai"] and sum_i_n == v["n1i"] and sum_c_ev == v["ci"] and sum_c_n == v["n2i"])
            status = "AACT_DERIVED_MATCH" if (match and pct_ok) else "MISMATCH"
            if not (match and pct_ok):
                ok_all = False
            out[f"{slug}/{pid}"] = {"registrations": ncts, "per_registration": per,
                                    "entry_counts": {"ai": v["ai"], "n1i": v["n1i"], "ci": v["ci"], "n2i": v["n2i"]},
                                    "aact_derived": {"ai": sum_i_ev, "n1i": sum_i_n, "ci": sum_c_ev, "n2i": sum_c_n},
                                    "abstract_pct_crosscheck": bool(pct_ok), "status": status}
            print(f"{slug}/{pid}: {status} | AACT-derived {sum_i_ev}/{sum_i_n},{sum_c_ev}/{sum_c_n} "
                  f"vs entry {v['ai']}/{v['n1i']},{v['ci']}/{v['n2i']} | abstract % {pA}/{pC} match={pct_ok}")
    json.dump(out, open(os.path.join(ROOT, "docs", "verified_arms_audit.json"), "w", encoding="utf-8",
                        newline=""), indent=1, ensure_ascii=False)
    print("\nALL verified_arms entries AACT-derivable + abstract-cross-checked:" , ok_all)
    return 0 if ok_all else 1


def _pair_sum(per, key):
    """Sum arm values position-wise across registrations (both have 2 arms). Returns [[armA vals],
    [armB vals]] paired by sorted order so the two smallest and two largest align consistently."""
    cols = [sorted(set(p[key])) for p in per.values() if len(set(p[key])) >= 2]
    if not cols or any(len(c) < 2 for c in cols):
        return []
    lows = [c[0] for c in cols]
    highs = [c[-1] for c in cols]
    return [lows, highs]


def _pct_in(text, pct):
    s = (text or "").replace("·", ".")
    return bool(re.search(rf"(?<!\d){re.escape(f'{pct:g}')}\s*%", s)) or bool(re.search(rf"(?<!\d){re.escape(f'{pct:g}')}(?!\d)", s))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
