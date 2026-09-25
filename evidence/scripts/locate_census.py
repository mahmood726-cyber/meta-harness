"""Source-location census on the CURRENT served tree: for every served effect/mean row (count rows belong to Evidence
lane two), do the row's exact served numbers co-occur in ONE window of a held source for that trial?

  effect rows: estimate, ci_low and ci_high all printed within one window (a sentence or a registry line)
  mean rows  : mean_t, sd_t, mean_c, sd_c all printed within one window
Numbers are compared as numbers at the printed precision (0.8 == 0.80), minus signs normalised. Sources searched:
the trial's record in cache/<slug>/records.json, cache/<slug>/ft_<pmid>.txt, evidence/held/<pmid>/*, the registry
records named by the row, and the row's own document_ref if any. Output: evidence/census_main/census.json with
N, LOCATED n (with ref + window) and NOT_LOCATED n (with what was searched). A located window is a CANDIDATE
source, not a binding: binding (endpoint, population, estimand) is the adjudication step."""
import glob, json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
import textrep, verify_records as V
ROOT = textrep.ROOT


def refs_for(slug, t):
    pid = str(t.get("id", "")).replace("PMID ", "").strip()
    refs = []
    rec = os.path.join(ROOT, "cache", slug, "records.json")
    if os.path.exists(rec) and pid:
        d = json.load(open(rec, encoding="utf-8"))
        for k, v in d.items():
            if isinstance(v, list):
                for i, r in enumerate(v):
                    if isinstance(r, dict) and str(r.get("id")) == pid:
                        refs.append(f"cache/{slug}/records.json#/{k}/{i}")
    for p in glob.glob(os.path.join(ROOT, "cache", slug, f"ft_{pid}*")) if pid else []:
        refs.append(os.path.relpath(p, ROOT).replace(os.sep, "/"))
    for p in glob.glob(os.path.join(ROOT, "evidence", "held", pid, "*")) if pid else []:
        if not p.endswith("europepmc_core.json") or True:
            refs.append(os.path.relpath(p, ROOT).replace(os.sep, "/"))
    for n in {t.get("family_id"), t.get("trial_family_id"), t.get("nct")}:
        if n and str(n).startswith("NCT") and os.path.exists(os.path.join(ROOT, "evidence", "held", "registry", f"{n}.json")):
            refs.append(f"evidence/held/registry/{n}.json")
    dr = t.get("document_ref")
    if dr and os.path.exists(os.path.join(ROOT, dr.partition("#")[0])):
        refs.append(dr)
    return list(dict.fromkeys(refs))


def windows(text):
    for line in text.split("\n"):
        for w in re.split(r"(?<=[.;])\s+(?=[A-Z(])", line):
            yield w


def has_all(window, vals):
    toks = {abs(float(x)) for x in V._num_tokens_text(window)}
    return all(any(abs(abs(v) - t) < 1e-9 for t in toks) for v in vals)


def target_values(t):
    if t.get("effect") is not None:
        return "effect", [t["effect"], t.get("ci_low"), t.get("ci_high")]
    if t.get("mean1") is not None:
        return "means", [t.get("mean1"), t.get("sd1"), t.get("mean2"), t.get("sd2")]
    if t.get("m1i") is not None:
        return "means", [t.get("m1i"), t.get("sd1i"), t.get("m2i"), t.get("sd2i")]
    return None, None


def main():
    rows, c = [], collections.Counter()
    for f in sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))):
        r = json.load(open(f, encoding="utf-8")); slug = r["slug"]
        for oi, o in enumerate(r["outcomes"]):
            for ti, t in enumerate(o.get("trials") or []):
                kind, vals = target_values(t)
                if t.get("ai") is not None or kind is None:
                    continue   # count rows: Evidence lane two
                vals = [float(v) for v in vals if v is not None]
                refs = refs_for(slug, t)
                hit = None
                for ref in refs:
                    try:
                        text = textrep.render(ref)
                    except Exception:
                        continue
                    for w in windows(text):
                        if has_all(w, vals):
                            hit = {"ref": ref, "window": w[:400]}; break
                    if hit:
                        break
                state = "LOCATED" if hit else "NOT_LOCATED"
                c[state] += 1
                rows.append({"slug": slug, "outcome": o["name"], "trial": t.get("id"), "json_ref": f"docs/reviews/{slug}/review.json#/outcomes/{oi}/trials/{ti}",
                             "kind": kind, "served": vals, "provenance": t.get("provenance"), "state": state, "hit": hit, "searched": refs})
    N = len(rows)
    out = {"population": {"N": N, "denominator": "served effect/mean trial-outcome rows on the current tree (count rows excluded: Evidence lane two)"},
           "counts": dict(c), "rows": rows}
    os.makedirs(os.path.join(ROOT, "evidence", "census_main"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "evidence", "census_main", "census.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(f"N={N}; " + ", ".join(f"{k} {v}" for k, v in c.items()))
    for r in rows:
        if r["state"] == "NOT_LOCATED":
            print("  NOT_LOCATED", r["slug"][:28], r["trial"], r["outcome"][:40], r["served"], r["provenance"], len(r["searched"]))


if __name__ == "__main__":
    main()
