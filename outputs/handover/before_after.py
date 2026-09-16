"""Before/after on the four classes Mahmood asked about, read from review objects.
usage: python before_after.py <mode> <root>   mode = 'tree' (working tree) or a git ref; root = repo path.
Prints n of N with N named; the same script runs against fetched served bytes after deploy."""
import json
import re
import subprocess
import sys

MODE, ROOT = sys.argv[1], sys.argv[2]
SLUGS = sorted(subprocess.run(["git", "ls-tree", "--name-only", "aa8ed28a", "docs/reviews/"], capture_output=True,
                              text=True, cwd=ROOT).stdout.replace("docs/reviews/", "").split())
SLUGS = [s.strip("/") for s in SLUGS if s.strip("/")]


def load(slug, name):
    if MODE == "tree":
        return json.load(open(f"{ROOT}/docs/reviews/{slug}/{name}", encoding="utf-8"))
    out = subprocess.run(["git", "show", f"{MODE}:docs/reviews/{slug}/{name}"], capture_output=True, text=True,
                         encoding="utf-8", cwd=ROOT).stdout
    return json.loads(out)


def html(slug):
    if MODE == "tree":
        return open(f"{ROOT}/docs/reviews/{slug}/index.html", encoding="utf-8").read()
    return subprocess.run(["git", "show", f"{MODE}:docs/reviews/{slug}/index.html"], capture_output=True, text=True,
                          encoding="utf-8", cwd=ROOT).stdout


rob_stale, pred_false, k2_served, parity_hand, stale, reasons = [], [], [], [], [], {}
pooled_pages = 0
for s in SLUGS:
    r = load(s, "review.json")
    prim = next(o for o in r["outcomes"] if o.get("primary"))
    res = prim["result"]
    rob2 = (r.get("rob2") or {}).get("trials") or {}
    sens = r.get("rob_sensitivity") or {}
    # stale RoB table: a pooled trial rated in rob2 (by PMID/NCT id) but absent/None in sensitivity levels
    ids = [re.sub(r"^PMID\s*", "", t["id"]) for t in prim["trials"]]
    rated = [i for i in ids if i in rob2 and (rob2[i] or {}).get("overall")]
    lv = sens.get("levels") or {}
    if rated and any(lv.get(i) is None and lv.get(next((t["label"] for t in prim["trials"] if re.sub(r"^PMID\s*", "", t["id"]) == i), "")) is None for i in rated):
        rob_stale.append(s)
    f, lo = sens.get("full"), sens.get("low_only")
    if f and lo and lo.get("k") == f.get("k") and "fewer trials than the full pool" in html(s):
        pred_false.append(s)
    if res.get("k") == 2 and res.get("ci_low") is not None and res.get("estimate") is not None:
        k2_served.append(s)
    pa = (r.get("reproduction") or {}).get("parity") or {}
    if pa and not pa.get("parity_relation") and not pa.get("unrenderable") and str(pa.get("status", "")).startswith("PARITY"):
        parity_hand.append(s)
    inv = r.get("invalidation") or {}
    if inv.get("stale"):
        stale.append(s)
    for x in inv.get("reasons", []):
        reasons[x["code"]] = reasons.get(x["code"], 0) + 1
    if (res.get("k") or 0) >= 2 and res.get("estimate") is not None:
        pooled_pages += 1

N = len(SLUGS)
print(f"[{MODE}] pages N={N}; pooled k>=2 with a served estimate: {pooled_pages}")
print(f"  stale RoB sensitivity (rated trial invisible to the re-pool): {len(rob_stale)} of {N}: {rob_stale}")
print(f"  false 'fewer trials than the full pool' rendered: {len(pred_false)} of {N}: {pred_false}")
print(f"  k=2 primaries serving a pooled CI: {len(k2_served)} of {N}: {k2_served}")
print(f"  hand 'PARITY*' status word rendered without a computed relation: {len(parity_hand)} of {N}: {parity_hand}")
print(f"  STALE: {len(stale)} of {N}; reasons: {dict(sorted(reasons.items()))}")
