"""Build per-pooled-trial ARM-CONTRAST disclosure from the local AACT snapshot, writing committed
cache/<slug>/arm_contrast.json. Measure-time (AACT scan); replayed offline; rendered.

For each pooled trial we record whether its intervention of interest is a genuine RANDOMISED CONTRAST
(differs across the registered arms) or is only background co-present. This makes the arm-contrast
fail-open state VISIBLE: a trial admitted because the registry has no arm data is shown as
'contrast unverified', never silently treated as a verified randomised comparison.

    python scripts/arm_contrast_build.py [--write] [<slug> ...]
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import armcontrast  # noqa: E402


def pooled(slug):
    """{pid: nct_or_None} for EVERY pooled trial (across all outcomes). A trial with no NCT is KEPT
    (nct=None) and rendered 'contrast unverified — no registry match', never DROPPED. Dropping a
    no-NCT/unmatched trial let it pass the randomised-contrast check silently -- the identity gap the
    external audit flagged (RALES, and any recovery-added trial whose file went stale)."""
    rev = json.load(open(f"{ROOT}/docs/reviews/{slug}/review.json", encoding="utf-8"))
    recs = {str(r["id"]): r for r in json.load(open(f"{ROOT}/cache/{slug}/records.json", encoding="utf-8"))["records"]}
    out = {}
    for o in rev.get("outcomes", []) or []:
        for t in o.get("trials", []) or []:
            pid = str(t.get("id", "")).replace("PMID ", "")
            if pid:
                out[pid] = recs.get(pid, {}).get("nct") or (pid if pid.startswith("NCT") else None)
    return out


def keywords(slug):
    t = json.load(open(f"{ROOT}/topics/{slug}.json", encoding="utf-8"))
    return t.get("intervention_terms") or (t.get("include") or {}).get("intervention_any") or []


def main(argv):
    write = "--write" in argv
    slugs = [a for a in argv if not a.startswith("-")] or [
        s for s in sorted(os.listdir(f"{ROOT}/docs/reviews")) if os.path.exists(f"{ROOT}/docs/reviews/{s}/review.json")]
    topics = {s: pooled(s) for s in slugs}
    allnct = {n for d in topics.values() for n in d.values() if n}
    index = armcontrast.build_arm_index(allnct)  # ONE AACT scan for the whole batch
    for slug, d in topics.items():
        kws = keywords(slug)
        trials = {}
        for pid, nct in d.items():
            if not nct:
                # no NCT to check against -> the contrast is UNVERIFIED and shown as such, never a
                # silent pass (the identity gap: an unidentifiable trial must not read as verified).
                trials[pid] = {"nct": None, "status": "unverified_no_registry_match",
                               "basis": "no NCT/registry match for this pooled trial; the randomised "
                                        "contrast of the intervention of interest cannot be registry-confirmed."}
                continue
            status, basis = armcontrast.contrast_status(nct, kws, index)
            entry = index.get(nct.upper())
            trials[pid] = {"nct": nct, "status": status, "basis": basis}
            if entry is not None:
                common, differing = entry
                trials[pid]["common"] = sorted(common)
                trials[pid]["differing"] = sorted(differing)
        n_ver = sum(1 for t in trials.values() if t["status"] == "verified")
        print(f"{slug}: {n_ver}/{len(trials)} contrasts registry-verified"
              + (f"  [{','.join(p+':'+t['status'] for p,t in trials.items() if t['status']=='background_only')}]"
                 if any(t["status"] == "background_only" for t in trials.values()) else ""))
        if write:
            json.dump({"source": f"AACT {os.path.basename(__import__('harness').aact.snapshot_dir())} design_groups+interventions",
                       "trials": trials},
                      open(f"{ROOT}/cache/{slug}/arm_contrast.json", "w", encoding="utf-8", newline=""),
                      indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
