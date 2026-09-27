"""Corpus-wide: how many PLATFORM / multi-comparison registrations were screened, and how many were rejected -- and on
what basis. A platform registration lists the conditions of ALL its domains (REMAP-CAP: 'Community-acquired Pneumonia,
Influenza, COVID-19'), so a population veto read off the registration's condition labels judges one domain by another
domain's population. Offline: reads cache/<slug>/records.json (registry records) and the served screening ledger.
  python scripts/platform_registration_audit.py [--ref <git ref for the served ledger>] [--out <json>]"""
import argparse
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# a registration is a PLATFORM when its own title/acronym says so -- a property of the record, not of a trial name list
PLATFORM = re.compile(r"\bplatform\b|\bREMAP\b|multi-?arm,? multi-?stage|\bMAMS\b|master protocol|\bumbrella trial|"
                      r"\bbasket trial|multifactorial adaptive", re.I)


def _ledger(ref, slug):
    path = f"docs/reviews/{slug}/review.json"
    if ref:
        p = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True)
        return json.loads(p.stdout) if p.returncode == 0 else None
    full = os.path.join(ROOT, path)
    return json.load(open(full, encoding="utf-8")) if os.path.exists(full) else None


def _conditions(rec):
    c = rec.get("conditions")
    return c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    slugs = sorted(d for d in os.listdir(os.path.join(ROOT, "docs", "reviews"))
                   if os.path.isdir(os.path.join(ROOT, "docs", "reviews", d)))
    kinds = {"topics": len(slugs), "registry_records_screened": 0, "platform_registrations_screened": 0,
             "platform_registrations_not_in_ledger": 0}
    rows = []
    for slug in slugs:
        rp = os.path.join(ROOT, "cache", slug, "records.json")
        rev = _ledger(a.ref, slug)
        if not os.path.exists(rp) or not rev:
            continue
        data = json.load(open(rp, encoding="utf-8"))
        regs = [r for v in data.values() if isinstance(v, list) for r in v
                if isinstance(r, dict) and r.get("id_type") == "nct"]
        ledger = {}
        for x in ((rev.get("screening") or {}).get("records") or []):
            m = re.search(r"NCT\d{8}", str(x.get("id")))
            if m:
                ledger[m.group(0)] = x
        seen = set()
        for r in regs:
            nct = str(r.get("id"))
            if nct in seen:
                continue
            seen.add(nct)
            if nct in ledger:
                kinds["registry_records_screened"] += 1
            text = " ".join(str(r.get(k) or "") for k in ("title", "acronym"))
            if not PLATFORM.search(text):
                continue
            x = ledger.get(nct)
            if not x:
                kinds["platform_registrations_not_in_ledger"] += 1
                continue
            kinds["platform_registrations_screened"] += 1
            reason = x.get("reason") or ""
            term = re.search(r"mention '([^']+)'", reason)
            cond = _conditions(r)
            rows.append({"slug": slug, "nct": nct, "acronym": r.get("acronym"), "title": r.get("title"),
                         "decision": x.get("decision"), "rule_id": x.get("rule_id"), "reason": reason,
                         "registration_conditions": cond,
                         "veto_term_from_registration_conditions": bool(
                             x.get("rule_id") == "X2" and term and term.group(1).lower() in cond.lower())})
    rejected = [r for r in rows if r["decision"] == "exclude"]
    by_cond = [r for r in rejected if r["veto_term_from_registration_conditions"]]
    out = {"ref": a.ref or "working tree", "population_kinds": kinds,
           "n_platform_rejected": len(rejected), "N_platform_screened": len(rows),
           "n_rejected_on_a_registration_condition_label": len(by_cond),
           "sentence": (f"{len(rejected)} of {len(rows)} platform registrations screened across {kinds['topics']} topics "
                        f"were rejected; {len(by_cond)} of those on a population term read off the registration's "
                        "condition labels (which list every domain's population)."),
           "rows": rows}
    if a.out:
        json.dump(out, open(a.out, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(out["sentence"])
    print("kinds:", kinds)
    for r in rows:
        print(f"  {r['slug']:40} {r['nct']} {str(r['acronym'])[:14]:14} {r['decision']:8} {r['rule_id'] or '':6} "
              f"{'COND-LABEL' if r['veto_term_from_registration_conditions'] else ''} {r['reason'][:70]}")


if __name__ == "__main__":
    main()
