"""Outsider walk, stdlib only: served review.json -> its review_sha256 -> a pooled row -> document_ref -> held bytes at the
served commit (public repo) -> span in bytes -> digits in span -> per-trial log-effects -> pooled estimate recomputed."""
import json, hashlib, re, urllib.request, math, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SITE = "https://mahmood726-cyber.github.io/meta-harness"; RAW = "https://raw.githubusercontent.com/mahmood726-cyber/meta-harness"
get = lambda u: urllib.request.urlopen(u, timeout=90).read()
prod = json.loads(get(f"{SITE}/_production/manifest.json")); commit = prod["commit_sha"]
man = json.loads(get(f"{SITE}/reviews/glp1-ra-mace-t2d/manifest.json"))
raw = get(f"{SITE}/reviews/glp1-ra-mace-t2d/review.json"); review = json.loads(raw)
core = {k: v for k, v in review.items() if k != "reproduction"}
canon = json.dumps(core, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
print("1 review_sha256 recomputed == manifest:", hashlib.sha256(canon).hexdigest() == man["review_sha256"], "| served commit", commit[:8])
prim = next(o for o in review["outcomes"] if o.get("primary")); res = prim["result"]
print("2 primary:", prim["name"], "| k", res["k"], "| served estimate", res["estimate"], res.get("scale"))
norm = lambda s: re.sub(r"\s+", " ", s)
held_cache = {}
ok_rows = 0; yi = []; vi = []
for t in prim["trials"]:
    pid = str(t["id"]).replace("PMID ", "")
    span = t.get("endpoint_result_span") or t.get("source_span") or ""
    ref = f"cache/glp1-ra-mace-t2d/records.json"
    if ref not in held_cache: held_cache[ref] = get(f"{RAW}/{commit}/{ref}")
    recs = json.loads(held_cache[ref])["records"]; rec = next(r for r in recs if str(r["id"]) == pid)
    in_held = norm(span) in norm(rec.get("abstract", "")) if span else None
    digits = all(str(x) in span for x in (t.get("effect"), t.get("ci_low"), t.get("ci_high")) if x is not None) if span else None
    print(f"   {t.get('label') or pid:12s} {t.get('effect')} [{t.get('ci_low')}, {t.get('ci_high')}] span-in-held={in_held} digits-in-span={digits} prov={t.get('provenance')}")
    if t.get("effect") and t.get("ci_low") and t.get("ci_high"):
        yi.append(math.log(t["effect"])); vi.append(((math.log(t["ci_high"]) - math.log(t["ci_low"])) / (2 * 1.959964)) ** 2)
    ok_rows += bool(in_held and digits)
# DerSimonian-Laird -> then PM is what the page declares; DL shown as the outsider's independent check of the point estimate
w = [1 / v for v in vi]; mu_fe = sum(a * b for a, b in zip(w, yi)) / sum(w); q = sum(a * (b - mu_fe) ** 2 for a, b in zip(w, yi))
c = sum(w) - sum(a * a for a in w) / sum(w); tau2 = max(0.0, (q - (len(yi) - 1)) / c)
wr = [1 / (v + tau2) for v in vi]; mu = sum(a * b for a, b in zip(wr, yi)) / sum(wr)
print(f"3 rows with span-in-held AND digits-in-span: {ok_rows}/{len(prim['trials'])}")
print(f"4 outsider re-pool (DL, from the {len(yi)} effect+CI rows): {math.exp(mu):.4f}  vs served {res['estimate']} ({res.get('method','?')[:60] if isinstance(res.get('method'),str) else ''})")
print("5 held-document digests declared in CERTIFICATE.json checked against raw bytes at the served commit:")
cert = json.loads(get(f"{SITE}/reviews/glp1-ra-mace-t2d/CERTIFICATE.json")); n = ok = 0
for hd in cert.get("held_documents", [])[:12]:
    b = get(f"{RAW}/{commit}/{hd['ref']}"); n += 1; good = hashlib.sha256(b).hexdigest() == hd["sha256"]; ok += good
    if not good: print("   MISMATCH", hd["ref"], hd["sha256"][:12], hashlib.sha256(b).hexdigest()[:12])
print(f"   {ok}/{n} match")
