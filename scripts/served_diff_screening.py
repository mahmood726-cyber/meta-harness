"""Served diff for the screening-roles change: every topic, every outcome -- result (k, estimate, ci, pi, tau2), the
pooled membership and the declared-absent membership -- at a base ref vs the working tree. Anything that moves is
named; a moved pooled NUMBER is a served-number change and needs Mahmood's signature before it lands.
  python scripts/served_diff_screening.py <base_ref> [--out <json>]"""
import argparse, json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = ("k", "estimate", "ci_low", "ci_high", "pi_low", "pi_high", "tau2")
# result STATES a reader acts on as much as on a number: presence, completeness, refusal, suppression
STATE_KEYS = ("present", "harms_incomplete", "state", "suppressed_incompatible", "unrenderable")


def _load(ref, slug):
    if ref:
        p = subprocess.run(["git", "show", f"{ref}:docs/reviews/{slug}/review.json"], cwd=ROOT, capture_output=True)
        return json.loads(p.stdout) if p.returncode == 0 else None
    p = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def _ids(xs):
    return sorted(str(x.get("id")) for x in xs or [])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    slugs = sorted(subprocess.run(["git", "ls-tree", "--name-only", f"{a.base}:docs/reviews"], cwd=ROOT,
                                  capture_output=True, text=True, check=True).stdout.split())
    moved, report = [], {}
    for slug in slugs:
        b, w = _load(a.base, slug), _load(None, slug)
        if b is None or w is None:
            report[slug] = {"state": "UNREADABLE", "base": b is not None, "tree": w is not None}
            moved.append(slug)
            continue
        bo = {o["name"]: o for o in b.get("outcomes") or []}
        wo = {o["name"]: o for o in w.get("outcomes") or []}
        diffs = []
        for name in sorted(set(bo) | set(wo)):
            x, y = bo.get(name) or {}, wo.get(name) or {}
            rx, ry = x.get("result") or {}, y.get("result") or {}
            num = {k: [rx.get(k), ry.get(k)] for k in KEYS if rx.get(k) != ry.get(k)}
            states = {k: [rx.get(k), ry.get(k)] for k in STATE_KEYS if rx.get(k) != ry.get(k)}
            if bool(rx.get("pool_refused")) != bool(ry.get("pool_refused")):
                states["pool_refused"] = [bool(rx.get("pool_refused")), bool(ry.get("pool_refused"))]
            pooled = (_ids(x.get("trials")), _ids(y.get("trials")))
            absent = (_ids(x.get("declared_absent_trials")), _ids(y.get("declared_absent_trials")))
            d = {}
            if num:
                d["result"] = num
            if states:
                d["result_state"] = states
            if pooled[0] != pooled[1]:
                d["pooled"] = {"left": sorted(set(pooled[0]) - set(pooled[1])), "entered": sorted(set(pooled[1]) - set(pooled[0]))}
            if absent[0] != absent[1]:
                d["declared_absent"] = {"left": sorted(set(absent[0]) - set(absent[1])), "entered": sorted(set(absent[1]) - set(absent[0]))}
            if d:
                diffs.append({"outcome": name, "primary": bool(y.get("primary") or x.get("primary")), **d})
        if diffs:
            moved.append(slug)
        report[slug] = {"state": "MOVED" if any("result" in d or "pooled" in d for d in diffs) else
                                 "RESULT_STATE_CHANGED" if any("result_state" in d for d in diffs) else
                                 ("MEMBERSHIP_ONLY" if diffs else "UNCHANGED"), "outcomes": diffs}
    summary = {"base": a.base, "topics": len(slugs),
               "served_number_moved": sorted(s for s, r in report.items() if r["state"] == "MOVED"),
               "result_state_changed": sorted(s for s, r in report.items() if r["state"] == "RESULT_STATE_CHANGED"),
               "declared_absent_membership_only": sorted(s for s, r in report.items() if r["state"] == "MEMBERSHIP_ONLY"),
               "unchanged": sum(1 for r in report.values() if r["state"] == "UNCHANGED"), "per_topic": report}
    if a.out:
        open(a.out, "w", encoding="utf-8", newline="\n").write(json.dumps(summary, indent=1, ensure_ascii=False) + "\n")
    print(f"topics {len(slugs)} | served number moved: {summary['served_number_moved']} | result state changed: "
          f"{summary['result_state_changed']} | declared-absent only: "
          f"{summary['declared_absent_membership_only']} | unchanged {summary['unchanged']}")
    return 1 if summary["served_number_moved"] else 0


if __name__ == "__main__":
    sys.exit(main())
