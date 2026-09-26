"""Ordered-contrast census of EVERY served topic's primary pool (lane OC, V1.1; report only -- nothing served is changed).

For each pooled trial row of each live page's primary outcome (review.json fetched from Pages), apply the V1 verifier's own
rules (scripts/verify_bundle.py loaded from a pinned commit of oc/ordered-contrast, blob id recorded) with the topic's own
vocabulary (topics/<slug>.json at the same main commit the pages were built from), and classify:
  PROVEN               the clause orders the arms, EXPERIMENTAL is the numerator, the clause states a measure equal to the
                       row's label, and the per-arm rate witness does not contradict
  REVERSED             the clause orders REFERENCE over EXPERIMENTAL (would need a declared reciprocal to be poolable)
  UNORDERED            a clause holds the tuple, but its words do not order the arms (or rates contradict the ordering)
  NO_MEASURE_IN_CLAUSE the clause orders the arms but names no ratio measure (estimator unprovable from the clause)
  LABEL_MISMATCH       the clause names a measure different from the row's stored label
  NO_CLAUSE_LOCATED    the row carries no endpoint_result_span, or no clause in it holds the row's own tuple
  COUNTS_DERIVED       the ratio was computed by the harness from arm counts (no stated estimator exists to prove)
  REGISTRY_ANALYSIS    a ClinicalTrials.gov results analysis: its orientation is the registry's group order, not words
  basis                where the clause was read: endpoint_result_span, or the row's `source` quotation with its provenance
                       labels stripped (rows that carry no endpoint_result_span)
  CONTINUOUS           a mean difference / SMD row (outside a ratio-orientation check)
usage: python cross_topic_census.py <verifier_commit> <main_commit> <live_slugs.txt> <out.json>"""
import collections
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import urllib.request

BASE = "https://mahmood726-cyber.github.io/meta-harness/"
_LABELS = __import__("re").compile(r"^(?:\s*(?:abstract|full[- ]text|registry|ct\.gov|ctgov)\b[^:]{0,80}?:\s*)+", __import__("re").I)
REPO = os.environ.get("OC_REPO", "C:/mh-lanes/oc")


def git_show(ref, path):
    p = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=REPO, capture_output=True, stdin=subprocess.DEVNULL)
    if p.returncode != 0:
        raise FileNotFoundError(f"{ref}:{path}")
    return p.stdout


def load_verifier(commit):
    src = git_show(commit, "scripts/verify_bundle.py")
    d = tempfile.mkdtemp()
    f = os.path.join(d, "vb_pinned.py")
    open(f, "wb").write(src)
    spec = importlib.util.spec_from_file_location("vb_pinned", f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    blob = subprocess.run(["git", "rev-parse", f"{commit}:scripts/verify_bundle.py"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    return m, blob, hashlib.sha256(src).hexdigest()


def classify(vb, t, vocab):
    scale = (t.get("scale") or "").upper()
    if scale in ("MD", "SMD") or t.get("mean1") is not None:
        return "CONTINUOUS", {}
    vals = [t.get("effect"), t.get("ci_low"), t.get("ci_high")]
    if t.get("ai") is not None and (t.get("effect") is None or not t.get("endpoint_result_span")):
        return "COUNTS_DERIVED", {}
    span, basis = t.get("endpoint_result_span") or "", "endpoint_result_span"
    if not span and t.get("source"):
        # the producer's quotation of the held text, behind provenance labels ("abstract effect+CI (RR): ..."): strip the labels,
        # which carry measure words of their own, and locate the tuple's clause in the quotation
        span, basis = _LABELS.sub("", str(t["source"])), "source_field"
    if not span or any(v is None for v in vals):
        return ("COUNTS_DERIVED" if t.get("ai") is not None else "NO_CLAUSE_LOCATED"), {"basis": basis}
    clause = vb.clause_with_effect(span, vals)
    if not clause:
        return ("COUNTS_DERIVED" if t.get("ai") is not None else "NO_CLAUSE_LOCATED"), {"basis": basis}
    oc = vb.ordered_contrast(clause, vals, vocab, None)
    det = {"basis": basis, "rule": (oc.get("direction_witness") or {}).get("rule"), "rate_witness": (oc.get("rate_witness") or {}).get("state"),
           "measure": (oc.get("measure") or {}).get("measure"), "measure_state": (oc.get("measure") or {}).get("state"),
           "reason": oc.get("reason"), "clause": clause[:260]}
    if oc["state"] != "ORDERED":
        if "ClinicalTrials.gov outcome measure" in clause:
            return "REGISTRY_ANALYSIS", det    # direction is the registry analysis's group order, not in any words
        return "UNORDERED", det
    if oc["numerator_side"] != "EXPERIMENTAL":
        return "REVERSED", det
    cm = oc["measure"]
    if cm["state"] != "STATED":
        return "NO_MEASURE_IN_CLAUSE", det
    if vb.scale_measure(t.get("scale")) != cm["measure"]:
        det["label"] = t.get("scale")
        return "LABEL_MISMATCH", det
    return "PROVEN", det


def main(verifier_commit, main_commit, live_file, out):
    vb, blob, sha = load_verifier(verifier_commit)
    slugs = open(live_file, encoding="utf-8").read().split()
    rows, errors = [], {}
    for slug in slugs:
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE + f"reviews/{slug}/review.json",
                                                               headers={"Cache-Control": "no-cache", "User-Agent": "oc-census/2"}), timeout=300) as r:
                rev = json.loads(r.read().decode("utf-8"))
            topic = json.loads(git_show(main_commit, f"topics/{slug}.json").decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            errors[slug] = f"{type(e).__name__}: {str(e)[:160]}"
            continue
        vocab = vb.contrast_vocabulary(topic)
        prim = next((o for o in rev.get("outcomes") or [] if o.get("primary")), None)
        if not prim:
            errors[slug] = "no primary outcome"
            continue
        pooled = (prim.get("result") or {}).get("estimate") is not None
        for t in prim.get("trials") or []:
            kind, det = classify(vb, t, vocab)
            rows.append({"slug": slug, "trial": t.get("id"), "scale": t.get("scale"), "pool_served": pooled,
                         "vocab_sizes": [len(vocab["experimental"]), len(vocab["reference"])], "kind": kind, **det})
    summary = collections.Counter(r["kind"] for r in rows)
    ratio_rows = [r for r in rows if r["kind"] not in ("CONTINUOUS",)]
    unprovable = [r for r in ratio_rows if r["kind"] != "PROVEN"]
    by_topic = collections.defaultdict(collections.Counter)
    for r in rows:
        by_topic[r["slug"]][r["kind"]] += 1
    res = {"rules": __doc__, "verifier_commit": verifier_commit, "verifier_blob": blob, "verifier_sha256": sha,
           "topics_commit": main_commit, "pages": len(slugs) - len(errors), "errors": errors,
           "rows_primary": len(rows), "ratio_rows": len(ratio_rows), "unprovable_ratio_rows": len(unprovable),
           "summary": dict(summary), "by_topic": {k: dict(v) for k, v in sorted(by_topic.items())}, "rows": rows}
    json.dump(res, open(out, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps({k: res[k] for k in ("verifier_blob", "pages", "errors", "rows_primary", "ratio_rows", "unprovable_ratio_rows", "summary")}, indent=1))
    for s, c in res["by_topic"].items():
        print(f"  {s:44s} {c}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
