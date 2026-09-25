"""Would any SERVED declared-absent entry change -- or gain a poolable result -- once '<' in source text stops being eaten?

For every declared_absent_trials row on every live page (review.json fetched from Pages, never the repo), re-run the pipeline's
own call -- absence.classify_reason(keywords, abstract, ft_<pid>.txt, outcome_name, declared_estimand, reason, absent_kind, row),
exactly as harness/pipeline.py makes it -- twice on identical inputs: once with the pre-fix regex patched back in (`<[^>]+>`) and
once with harness.markup.strip_markup. Also reason_audit.find_value_in_sources (the held-source value finder).
  CONTROL: the pre-fix run must reproduce the served reason_code (agreement rate reported; a disagreement is the harness having
           moved since the page was built, not the fix).
  CHANGE:  rows whose reason_code / state differ between the two runs, and rows where a value becomes visible.
  POOLABLE: classify_reason is documented as an audit layer that "never makes a non-pooled value poolable", and extraction
           (harness/extract.py) reads the raw abstract with no markup strip, so a newly visible value is EXTRACTION DEBT, not a
           pooled result; the count of rows that would enter a pool is reported separately and derived, not assumed.
usage: python evidence/v11_tag_strip/rederive_declared_absent.py <live_slugs.txt> <out.json>"""
import collections
import copy
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from harness import absence, reason_audit, markup  # noqa: E402
from harness.pipeline import _outcome_specs  # noqa: E402

BASE = "https://mahmood726-cyber.github.io/meta-harness/"
OLD = re.compile(r"<[^>]+>")


def old_strip(text, repl=" "):
    return OLD.sub(repl, text or "")


def run_both(fn):
    out = {}
    for mode, strip in (("before", old_strip), ("after", markup.strip_markup)):
        absence.strip_markup, reason_audit.strip_markup = strip, strip
        out[mode] = fn()
    absence.strip_markup, reason_audit.strip_markup = markup.strip_markup, markup.strip_markup
    return out


def main(live_file, out):
    slugs = open(live_file, encoding="utf-8").read().split()
    rows_out, errors = [], {}
    for slug in slugs:
        try:
            req = urllib.request.Request(BASE + f"reviews/{slug}/review.json", headers={"Cache-Control": "no-cache", "User-Agent": "oc-v11/1"})
            with urllib.request.urlopen(req, timeout=300) as r:
                rev = json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            errors[slug] = str(e)[:200]
            continue
        config = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
        specs = {sp.get("name"): sp for sp, _ in _outcome_specs(config)}
        recp = os.path.join(ROOT, "cache", slug, "records.json")
        recs = {str(r.get("id")): r for r in (json.load(open(recp, encoding="utf-8")).get("records") or [])} if os.path.exists(recp) else {}
        for o in rev.get("outcomes") or []:
            sp = specs.get(o.get("name")) or {}
            kws = sp.get("keywords") or []
            for t in o.get("declared_absent_trials") or []:
                pid = str(t.get("id", "")).replace("PMID ", "")
                ab = (recs.get(pid) or {}).get("abstract", "")
                ftp = os.path.join(ROOT, "cache", slug, f"ft_{pid}.txt")
                ft = open(ftp, encoding="utf-8").read() if os.path.exists(ftp) else None
                has_lt = "<" in (ab or "") or "<" in (ft or "")
                try:
                    cr = run_both(lambda: absence.classify_reason(kws, ab, ft, outcome_name=o.get("name"),
                                                                  declared_estimand=sp.get("estimand") or o.get("estimand"),
                                                                  reason=t.get("reason"), absent_kind=t.get("absent_kind"), row=copy.deepcopy(t)))
                    srcs = [{"source_id": f"PMID {pid}", "source_kind": "abstract", "text": ab}] + ([{"source_id": f"ft_{pid}", "source_kind": "fulltext", "text": ft}] if ft else [])
                    fv = run_both(lambda: reason_audit.find_value_in_sources(srcs, kws, o.get("name")))
                    err = None
                except Exception as e:  # noqa: BLE001
                    cr, fv, err = {"before": {}, "after": {}}, {"before": None, "after": None}, f"{type(e).__name__}: {str(e)[:160]}"
                rows_out.append({
                    "slug": slug, "outcome": o.get("name"), "trial": t.get("id"), "served_code": t.get("reason_code"),
                    "has_lt_in_held_text": has_lt, "fulltext_held": ft is not None, "error": err,
                    "code_before": (cr["before"] or {}).get("reason_code"), "code_after": (cr["after"] or {}).get("reason_code"),
                    "state_before": (cr["before"] or {}).get("state"), "state_after": (cr["after"] or {}).get("state"),
                    "value_before": bool(fv["before"]), "value_after": bool(fv["after"]),
                    "value_after_span": (fv["after"] or {}).get("span") if fv["after"] and not fv["before"] else None,
                })
    n = len(rows_out)
    s = {
        "declared_absent_rows": n, "pages": len(slugs) - len(errors), "fetch_errors": errors,
        "rows_with_lt_in_held_text": sum(r["has_lt_in_held_text"] for r in rows_out),
        "control_before_reproduces_served_code": sum(r["code_before"] == r["served_code"] for r in rows_out),
        "code_or_state_changes": sum((r["code_before"], r["state_before"]) != (r["code_after"], r["state_after"]) for r in rows_out),
        "value_newly_visible_in_held_sources": sum(r["value_after"] and not r["value_before"] for r in rows_out),
        "value_lost": sum(r["value_before"] and not r["value_after"] for r in rows_out),
        "errors": sum(1 for r in rows_out if r["error"]),
        "code_transitions": collections.Counter(f"{r['code_before']} -> {r['code_after']}" for r in rows_out
                                                if r["code_before"] != r["code_after"]),
    }
    json.dump({"rules": __doc__, "summary": s, "rows": rows_out}, open(out, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False, default=dict)
    print(json.dumps(s, indent=1, default=dict))
    for r in rows_out:
        if (r["code_before"], r["state_before"]) != (r["code_after"], r["state_after"]) or (r["value_after"] and not r["value_before"]):
            print("CHANGED:", r["slug"], "|", r["outcome"], "|", r["trial"], "|", r["code_before"], "->", r["code_after"],
                  "| value", r["value_before"], "->", r["value_after"], "|", (r["value_after_span"] or "")[:140])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
