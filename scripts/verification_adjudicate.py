"""Adjudicate the per-topic source-verification lanes (brief-V) against their finish condition -- mechanically.

For each harvested topic under outputs/search_v2/verification/<slug>/:
  - the JSON has exactly N objects, N == the report's first-line NEW count, and the seven category counts sum to N;
  - every verdict is from the brief's list and carries a non-empty quote (or is UNDECIDABLE / NOT_VERIFIED_CAP);
  - N is re-derived HERE from the committed artefacts (r2 snapshot includes minus legacy includes, pooled trials and
    declared-absent trials of the served review) so a lane cannot shrink its own denominator silently;
  - the ELIGIBLE_RCT rows are listed by name (these are the only rows that could move a pool).
Prints one line per topic and the totals as n of N; writes docs/evidence/search-v2-verification-2026-09-15/01-adjudication.txt
when --write is given. Never reads the lanes' prose.
"""
from __future__ import annotations
import argparse
import io
import json
import os
import re
import sys

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import screen  # noqa: E402
from harness.pipeline import _dedup  # noqa: E402

HARVEST = os.path.join(ROOT, "outputs", "search_v2", "verification")
VERDICTS = ("ELIGIBLE_RCT", "ELIGIBLE_RCT_NO_PRIMARY", "NOT_RCT", "WRONG_POPULATION", "WRONG_INTERVENTION",
            "WRONG_COMPARATOR", "WRONG_OUTCOME_ONLY", "DUPLICATE_OF_ACCOUNTED", "UNDECIDABLE_FROM_RECORD", "NOT_VERIFIED_CAP",
            "REGISTRY_ONLY_NO_PUBLICATION")
FIRST_RE = re.compile(r"VERDICTS: NEW (\d+); ELIGIBLE_RCT (\d+); ELIGIBLE_RCT_NO_PRIMARY (\d+); NOT_RCT (\d+); WRONG_\* (\d+); "
                      r"DUPLICATE_OF_ACCOUNTED (\d+); UNDECIDABLE (\d+); NOT_VERIFIED_CAP (\d+)(?:; REGISTRY_ONLY (\d+))?")


def _load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _pmid(x):
    s = str(x or "").strip()
    return s if s.isdigit() else None


def _key(rec):
    return _pmid(rec.get("pmid")) or _pmid(rec.get("id")) or (str(rec.get("nct") or "").upper() or None) or (str(rec.get("doi") or "") or None)


def expected_new(slug):
    cfg = _load(os.path.join(ROOT, "topics", f"{slug}.json"))
    legacy = _load(os.path.join(ROOT, "cache", slug, "records.json"))
    if not isinstance(legacy, dict):
        legacy = {"records": legacy}
    merged = _dedup(legacy, cfg.get("pivotal_trials"))
    by_id = {str(r.get("id")): r for r in merged}
    accounted = set()
    for d in screen.run(merged, cfg).get("decisions") or []:
        if d.get("decision") == "include":
            k = _key(by_id.get(str(d.get("id")), {"id": d.get("id")}))
            if k:
                accounted.add(k)
    review = _load(os.path.join(ROOT, "docs", "reviews", slug, "review.json"))
    prim = next((o for o in review.get("outcomes", []) if o.get("primary")), None) or {}
    for t in (prim.get("trials") or []) + (prim.get("declared_absent_trials") or []):
        k = _key({"id": t.get("id"), "pmid": t.get("pmid"), "nct": t.get("nct")})
        if k:
            accounted.add(k)
    snap = _load(os.path.join(ROOT, "cache", slug, "snapshots", "2026-09-15r2-search_v2", "records.json"))
    recs = {str(r.get("id")): r for r in snap.get("records") or []}
    new = []
    for d in snap.get("screening", {}).get("decisions") or []:
        if d.get("decision") != "include":
            continue
        r = recs.get(str(d.get("id")), {"id": d.get("id")})
        k = _key(r)
        if k and k not in accounted:
            new.append(k)
    return len(new), len(accounted)


def _omitted_registry_only(slug, items):
    """Registry-only (NCT, no PMID) screen-includes of the r2 snapshot that the lane's JSON does not carry."""
    lane_keys = {str(it.get("id")) for it in items} | {str(it.get("nct") or "").upper() for it in items}
    snap = _load(os.path.join(ROOT, "cache", slug, "snapshots", "2026-09-15r2-search_v2", "records.json"))
    recs = {str(r.get("id")): r for r in snap.get("records") or []}
    n = 0
    for d in snap.get("screening", {}).get("decisions") or []:
        if d.get("decision") != "include":
            continue
        r = recs.get(str(d.get("id")), {})
        if r.get("id_type") == "nct" and not _pmid(r.get("pmid")) and str(r.get("id")).upper() not in lane_keys:
            n += 1
    return n


def adjudicate(slug):
    d = os.path.join(HARVEST, slug)
    rp = os.path.join(d, f"LANE-V-{slug}-REPORT.md")
    jp = os.path.join(d, f"{slug}.json")
    row = {"slug": slug, "problems": []}
    if not os.path.exists(rp) or not os.path.exists(jp):
        row["problems"].append("report or json missing")
        row["state"] = "NOT-HARVESTED"
        return row
    first = open(rp, encoding="utf-8", errors="replace").readline().strip()
    m = FIRST_RE.search(first)
    if not m:
        if "VERDICTS: NEW 0" in first:
            m = None
            counts = [0] * 8
        else:
            row["problems"].append(f"first line not in the brief's form: {first[:120]}")
            row["state"] = "MALFORMED"
            return row
    else:
        counts = [int(x) if x is not None else 0 for x in m.groups()]
    N = counts[0]
    if sum(counts[1:]) != N:
        row["problems"].append(f"categories sum {sum(counts[1:])} != NEW {N}")
    items = _load(jp)
    if len(items) != N:
        row["problems"].append(f"json has {len(items)} objects, report says NEW {N}")
    # a remainder lane (W-<slug>) verified the rows the first lane capped: its verdicts replace those rows
    rem = os.path.join(HARVEST, f"{slug}-remainder", f"{slug}.json")
    if os.path.exists(rem):
        rem_items = {str(it.get("id")): it for it in _load(rem)}
        replaced = 0
        for it in items:
            if it.get("verdict") == "NOT_VERIFIED_CAP" and str(it.get("id")) in rem_items:
                it.update(rem_items[str(it.get("id"))]); replaced += 1
        counts = [N] + [0] * 8
        for it in items:
            v = it.get("verdict")
            idx = {"ELIGIBLE_RCT": 1, "ELIGIBLE_RCT_NO_PRIMARY": 2, "NOT_RCT": 3, "DUPLICATE_OF_ACCOUNTED": 5, "UNDECIDABLE_FROM_RECORD": 6,
                   "NOT_VERIFIED_CAP": 7, "REGISTRY_ONLY_NO_PUBLICATION": 8}.get(v, 4 if str(v).startswith("WRONG_") else None)
            if idx: counts[idx] += 1
        row["remainder_replaced"] = replaced
        if len(counts) < 9: counts += [0] * (9 - len(counts))
    bad_verdict = [it.get("id") for it in items if it.get("verdict") not in VERDICTS]
    if bad_verdict:
        row["problems"].append(f"verdict not in list: {bad_verdict[:5]}")
    no_quote = [it.get("id") for it in items if it.get("verdict") not in ("UNDECIDABLE_FROM_RECORD", "NOT_VERIFIED_CAP") and not str(it.get("quote") or "").strip()]
    if no_quote:
        row["problems"].append(f"verdict without quote: {no_quote[:5]}")
    try:
        exp_n, exp_acc = expected_new(slug)
    except Exception as exc:  # noqa: BLE001
        exp_n, exp_acc = None, None
        row["problems"].append(f"could not re-derive N: {exc}")
    omitted_registry = 0
    if exp_n is not None and exp_n != N:
        # the first lanes dropped NCT-only (registry, no publication) includes from N; those are counted here as
        # REGISTRY_ONLY omitted by the lane, never as verified and never as absent
        omitted_registry = _omitted_registry_only(slug, items)
        if exp_n - N == omitted_registry:
            row["problems"].append(f"lane NEW {N} omitted {omitted_registry} registry-only includes; integrator N {exp_n} (omission counted as REGISTRY_ONLY, unverified)")
        else:
            row["problems"].append(f"lane NEW {N} != integrator re-derived NEW {exp_n} (accounted {exp_acc}); registry-only omitted {omitted_registry}")
    row.update({"N": N, "expected_N": exp_n, "eligible": counts[1], "eligible_no_primary": counts[2], "not_rct": counts[3],
                "wrong": counts[4], "duplicate": counts[5], "undecidable": counts[6], "cap": counts[7],
                "registry_only": (counts[8] if len(counts) > 8 else 0) + omitted_registry,
                "screen_agrees": sum(1 for it in items if it.get("screen_agrees") is True),
                "eligible_ids": [(it.get("id"), (it.get("title") or "")[:90]) for it in items if it.get("verdict") == "ELIGIBLE_RCT"],
                "state": "OK" if not row["problems"] else "PROBLEMS"})
    return row


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    split = _load(os.path.join(ROOT, "registry", "search_benchmark_split.json"))["assignments"]
    lines = ["SOURCE-VERIFICATION LANES -- adjudicated against the brief's finish condition (mechanical; lane prose not read)", ""]
    tot = {}
    for sset in ("MEASUREMENT", "DEVELOPMENT"):
        slugs = sorted(s for s, v in split.items() if v["set"] == sset)
        lines.append(f"## {sset} ({len(slugs)} topics)")
        agg = {"topics": 0, "ok": 0, "N": 0, "eligible": 0, "eligible_no_primary": 0, "not_rct": 0, "wrong": 0, "duplicate": 0, "undecidable": 0, "cap": 0, "screen_agrees": 0, "registry_only": 0}
        for slug in slugs:
            r = adjudicate(slug)
            if r["state"] == "NOT-HARVESTED":
                lines.append(f"- {slug}: NOT HARVESTED (lane not run or ended without its artefact)")
                continue
            if r["state"] == "MALFORMED":
                lines.append(f"- {slug}: MALFORMED -- {'; '.join(r['problems'])}")
                continue
            agg["topics"] += 1
            agg["ok"] += r["state"] == "OK"
            for k in ("eligible", "eligible_no_primary", "not_rct", "wrong", "duplicate", "undecidable", "cap", "screen_agrees", "registry_only"):
                agg[k] += r[k]
            agg["N"] += r["expected_N"] if r["expected_N"] is not None else r["N"]
            lines.append(f"- {slug}: {r['state']} NEW {r['N']} (re-derived {r['expected_N']}); ELIGIBLE_RCT {r['eligible']}; NO_PRIMARY {r['eligible_no_primary']}; NOT_RCT {r['not_rct']}; WRONG {r['wrong']}; DUP {r['duplicate']}; UNDECIDABLE {r['undecidable']}; CAP {r['cap']}; REGISTRY_ONLY {r['registry_only']}; screen agreed {r['screen_agrees']} of {r['N']}"
                         + (f" -- PROBLEMS: {'; '.join(r['problems'])}" if r["problems"] else ""))
            for i, t in r["eligible_ids"]:
                lines.append(f"    ELIGIBLE_RCT {i}: {t}")
        lines.append(f"  {sset} totals: {agg['topics']} of {len(slugs)} topics harvested, {agg['ok']} of {agg['topics']} clean; NEW {agg['N']}; ELIGIBLE_RCT {agg['eligible']} of {agg['N']}; "
                     f"ELIGIBLE_RCT_NO_PRIMARY {agg['eligible_no_primary']}; NOT_RCT {agg['not_rct']}; WRONG_* {agg['wrong']}; DUPLICATE {agg['duplicate']}; UNDECIDABLE {agg['undecidable']}; NOT_VERIFIED_CAP {agg['cap']}; REGISTRY_ONLY {agg['registry_only']}; "
                     f"automated screen agreed {agg['screen_agrees']} of {agg['N']}")
        lines.append("")
        tot[sset] = agg
    text = "\n".join(lines)
    print(text)
    if args.write:
        out = os.path.join(ROOT, "docs", "evidence", "search-v2-verification-2026-09-15", "01-adjudication.txt")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
