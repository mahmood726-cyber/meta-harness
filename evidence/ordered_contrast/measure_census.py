"""Census of served pooled outcomes by effect-measure mix, read from the SERVED surface (Pages), nothing written but the summary."""
import json, sys, urllib.request, collections
BASE = "https://mahmood726-cyber.github.io/meta-harness/"
slugs = [l.split(":")[0] for l in open(sys.argv[1], encoding="utf-8").read().split() if l]
out = {"base": BASE, "slugs": len(slugs), "outcomes": [], "errors": {}}
for s in slugs:
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE + f"reviews/{s}/review.json", headers={"Cache-Control": "no-cache", "User-Agent": "oc-census/1"}), timeout=300) as r:
            rev = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        out["errors"][s] = str(e)[:200]; continue
    for o in rev.get("outcomes") or []:
        res = o.get("result") or {}
        em = res.get("estmeasure") or {}
        labels = sorted({str(t.get("scale")) for t in (o.get("trials") or [])})
        out["outcomes"].append({"slug": s, "outcome": o.get("name"), "primary": bool(o.get("primary")), "k": res.get("k"),
                                "pooled": res.get("estimate") is not None, "scale": res.get("scale"), "status": em.get("status"),
                                "canonicals": em.get("canonicals"), "classes": em.get("classes"), "labels": labels,
                                "suppressed": bool(res.get("suppressed_incompatible"))})
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
pooled = [x for x in out["outcomes"] if x["pooled"]]
c = collections.Counter((x["status"], tuple(x["canonicals"] or [])) for x in pooled)
print("slugs", len(slugs), "errors", len(out["errors"]), "outcomes", len(out["outcomes"]), "pooled", len(pooled))
for k, v in c.most_common(): print(v, k)
