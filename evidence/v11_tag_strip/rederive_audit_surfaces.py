"""The two OTHER served surfaces the stripper feeds, re-derived before vs after the V1.1 fix, through the pipeline's own functions.

  reason_code_audit          -- reason_audit.annotate_review(slug, review, specs, source_map): one verdict per declared-absent row
  unextracted_outcome_audit  -- unextracted.annotate_review(...): every included-trial x registered-outcome pair whose value is
                                visible in held sources but not extracted
Both take source_map = reason_audit.sources_by_trial(slug, records, ROOT), which strips every abstract / full text through
reason_audit._plain -- a fixed site. BEFORE patches the pre-fix regex back into both modules; AFTER is the fix. The served
review.json (fetched from Pages) is deep-copied for each run, so only the stripper differs.
(An earlier draft passed RAW text to find_value_in_sources and so never exercised _plain on this path; this script replaces it.)
usage: python evidence/v11_tag_strip/rederive_audit_surfaces.py <live_slugs.txt> <out.json>"""
import copy
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from harness import absence, markup, reason_audit, unextracted  # noqa: E402
from harness.pipeline import _outcome_specs  # noqa: E402

BASE = "https://mahmood726-cyber.github.io/meta-harness/"
OLD = re.compile(r"<[^>]+>")


def old_strip(text, repl=" "):
    return OLD.sub(repl, text or "")


def surfaces(slug, review, specs, records, strip):
    absence.strip_markup = reason_audit.strip_markup = strip
    try:
        src = reason_audit.sources_by_trial(slug, records, ROOT)
        r1 = copy.deepcopy(review)
        ra = reason_audit.annotate_review(slug, r1, specs, src)
        r2 = copy.deepcopy(review)
        ua = unextracted.annotate_review(slug, r2, specs, src)
    finally:
        absence.strip_markup = reason_audit.strip_markup = markup.strip_markup
    return ra, ua


def key_ra(r):
    return (r.get("outcome"), r.get("trial_key"))


def key_ua(r):
    return (r.get("outcome"), r.get("trial_key"))


def strip_volatile(r):
    return {k: v for k, v in r.items() if k not in ("slug",)}


def main(live_file, out):
    slugs = open(live_file, encoding="utf-8").read().split()
    res = {"pages": 0, "reason_audit_rows": 0, "reason_audit_changed": [], "unextracted_rows": 0, "unextracted_changed": [],
           "unextracted_summary_before": {}, "unextracted_summary_after": {}, "errors": {}}
    for slug in slugs:
        try:
            req = urllib.request.Request(BASE + f"reviews/{slug}/review.json", headers={"Cache-Control": "no-cache", "User-Agent": "oc-v11/1"})
            with urllib.request.urlopen(req, timeout=300) as r:
                review = json.loads(r.read().decode("utf-8"))
            config = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
            specs = {sp.get("name"): sp for sp, _ in _outcome_specs(config)}
            records = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
            b_ra, b_ua = surfaces(slug, review, specs, records, old_strip)
            a_ra, a_ua = surfaces(slug, review, specs, records, markup.strip_markup)
        except Exception as e:  # noqa: BLE001
            res["errors"][slug] = f"{type(e).__name__}: {str(e)[:200]}"
            continue
        res["pages"] += 1
        for name, b, a, bucket in (("reason_audit", b_ra, a_ra, "reason_audit_changed"), ("unextracted", b_ua, a_ua, "unextracted_changed")):
            res[f"{name}_rows"] += len(a.get("rows") or [])
            bm = {key_ra(r): strip_volatile(r) for r in b.get("rows") or []}
            am = {key_ra(r): strip_volatile(r) for r in a.get("rows") or []}
            for k in sorted(set(bm) | set(am), key=str):
                if bm.get(k) != am.get(k):
                    diff = sorted(f for f in set((bm.get(k) or {})) | set((am.get(k) or {})) if (bm.get(k) or {}).get(f) != (am.get(k) or {}).get(f))
                    res[bucket].append({"slug": slug, "outcome": k[0], "trial": k[1], "fields": diff,
                                        "before": {f: (bm.get(k) or {}).get(f) for f in diff},
                                        "after": {f: (am.get(k) or {}).get(f) for f in diff}})
        res["unextracted_summary_before"][slug] = {k: v for k, v in b_ua.items() if k != "rows"}
        res["unextracted_summary_after"][slug] = {k: v for k, v in a_ua.items() if k != "rows"}
    json.dump(res, open(out, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in res.items() if not k.startswith("unextracted_summary")}, indent=1))
    for c in res["reason_audit_changed"] + res["unextracted_changed"]:
        print("CHANGED", c["slug"], "|", c["outcome"], "|", c["trial"], "|", c["fields"], "|",
              json.dumps(c["before"], default=str)[:160], "->", json.dumps(c["after"], default=str)[:160])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
