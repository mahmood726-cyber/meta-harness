"""Corpus-wide n of N for the lane NR V1.0.1 label fixes (statins-older-adults and ticagrelor reviews).

usage: python scripts/nr_v101_label_audit.py HEAD            # the served (committed) pages: the pre-fix corpus
       python scripts/nr_v101_label_audit.py <build_dir>     # <slug>.review.json + <slug>.index.html from a rebuild
       [--json out.json]

Every detector derives its answer from the rows and the held records (cache/<slug>/records.json at HEAD); none trusts a
field the fixes add, so the same detector counts the pre-fix corpus and the post-fix corpus.
  A  pages that serve a post-hoc (or unresolved) subgroup as pre-specified         (subgroup_provenance)
  B  pooled composite results carrying an unqualified MACE / 3-point label           (composite_label)
  C  k=2 pages whose computed-but-withheld registered CI is worded as a refusal     (k2)
  D  k=2 results whose served primary interval is the common-effect interval        (k2)
  E  direction-conflict pages: refusal wording, anchor read as conclusion, explanatory/equivalence claims (k2 / gate)
  F  machine RoB D5 signals whose supporting evidence fails the identity check but are shown, not withdrawn (rob2)
  G  primary k=1 results served as a synthesis, or without the trial's own derived population    (population_qualifier)
"""
from __future__ import annotations

import html as _html
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import composite_label, k2, population_qualifier, rob2, subgroup_provenance  # noqa: E402

_FAILURE_WORDING_CI = re.compile(r"REFUSED at k=2|registered CI refused|Registered PM/HKSJ CI REFUSED|"
                                 r"served pooled CI \(refused\)|CI refused at k=2", re.I)
_FAILURE_WORDING_POOL = re.compile(r"Pooled result REFUSED|pooled row (?:is )?refused|invalid pooled row is quarantined|"
                                   r"served pooled CI \(refused\)", re.I)


def _git(path):
    try:
        return subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT).decode("utf-8")
    except subprocess.CalledProcessError:
        return None


def _slugs(src):
    if src == "HEAD":
        out = subprocess.check_output(["git", "ls-tree", "--name-only", "HEAD", "docs/reviews/"], cwd=ROOT).decode()
        return sorted(os.path.basename(p) for p in out.split())
    return sorted(f[:-len(".review.json")] for f in os.listdir(src) if f.endswith(".review.json"))


def _load(src, slug):
    if src == "HEAD":
        rj, hj = _git(f"docs/reviews/{slug}/review.json"), _git(f"docs/reviews/{slug}/index.html")
    else:
        rp, hp = os.path.join(src, f"{slug}.review.json"), os.path.join(src, f"{slug}.index.html")
        rj = open(rp, encoding="utf-8").read() if os.path.exists(rp) else None
        hj = open(hp, encoding="utf-8").read() if os.path.exists(hp) else None
    return (json.loads(rj) if rj else None), (hj or "")


def _records(slug):
    raw = _git(f"cache/{slug}/records.json")
    if not raw:
        return {}
    return {str(r.get("id")): r for r in json.loads(raw).get("records", [])}


def _text(h):
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", h or "")))


def _prim(rev):
    return next((o for o in rev.get("outcomes") or [] if o.get("primary")), None) or {}


def _conflict_segments(text):
    """The generated text about a direction conflict: each refusal/withholding block and the manuscript Results
    sentence, cut from the page (quoted source abstracts elsewhere on the page are data, not claims)."""
    segs = []
    for m in re.finditer(r"(?i)direction conflict", text):
        segs.append(text[max(0, m.start() - 200):m.end() + 1200])
    for m in re.finditer(r"Results\. ", text):
        segs.append(text[m.start():m.start() + 900])
    return segs


def audit(src):
    res = {"source": src, "pages": 0, "A": [], "A_unresolved": [], "B": [], "B_N": 0, "C": [], "C_N": 0, "D": [], "D_N": 0,
           "E_wording": [], "E_anchor": [], "E_claims": [], "E_N": 0, "F": [], "F_N": 0, "G": [], "G_N": 0, "kinds": {}}
    for slug in _slugs(src):
        rev, page = _load(src, slug)
        if not rev:
            continue
        res["pages"] += 1
        recs = _records(slug)
        text = _text(page)
        # A
        for v in subgroup_provenance.prespecified_claim_violations(rev, recs, page):
            (res["A"] if v["derived"] == subgroup_provenance.POST_HOC else res["A_unresolved"]).append(dict(v, slug=slug))
        # B
        au = composite_label.audit(rev, recs, page)
        res["B_N"] += len(au["pooled_composites"])
        res["B"] += [dict(r, slug=slug) for r in au["unqualified"]]
        for r in au["pooled_composites"]:
            res["kinds"][r["kind"]] = res["kinds"].get(r["kind"], 0) + 1
        # C, D
        for o in rev.get("outcomes") or []:
            r = o.get("result") or {}
            if (r.get("pooled_ci_refused") or {}).get("code") == k2.K2_SINGLE_DF and r.get("ci_hksj_unserved"):
                res["C_N"] += 1
                if _FAILURE_WORDING_CI.search(text):
                    res["C"].append({"slug": slug, "outcome": o.get("name")})
            if r.get("ci_low_fixed") is not None:
                res["D_N"] += 1
                for b in k2.common_effect_promotion_violations(r):
                    res["D"].append({"slug": slug, "outcome": o.get("name"), "violation": b})
        # E
        ref = (_prim(rev).get("result") or {}).get("pool_refused") or {}
        if ref.get("code") == k2.DIRECTION_CONFLICT_K2:
            res["E_N"] += 1
            if _FAILURE_WORDING_POOL.search(text):
                res["E_wording"].append(slug)
            segs = " ".join(_conflict_segments(text))
            res["E_claims"] += [dict(v, slug=slug) for v in k2.conflict_claim_violations(segs)]
            anchor = ref.get("honest_k1_anchor") or {}
            name, eff = anchor.get("name") or anchor.get("label"), anchor.get("effect")
            if name and eff is not None:
                effs = {f"{float(eff):g}", f"{float(eff):.2f}"}
                for s in re.split(r"(?<=[.;])\s+", segs):
                    if name in s and any(e in s for e in effs) and " alone" not in s:
                        res["E_anchor"].append({"slug": slug, "sentence": s[:220]})
                        break
        # G
        topic = json.loads(_git(f"topics/{slug}.json") or "{}")
        prim = _prim(rev)
        if (prim.get("result") or {}).get("k") == 1 and (prim.get("result") or {}).get("present") is not False:
            res["G_N"] += 1
            res["G"] += [dict(v, slug=slug) for v in population_qualifier.single_trial_violations(
                rev, recs, text, topic.get("intervention_terms") or ())]
        # F
        for pid, e in ((rev.get("rob2") or {}).get("trials") or {}).items():
            d5 = (e.get("domains") or {}).get("D5_selective_reporting") or {}
            if not d5.get("inputs") or ":D5:" not in str(d5.get("rule_id") or ""):
                continue
            res["F_N"] += 1
            if d5.get("level") != rob2.WITHDRAWN and rob2.identity_check_failed(d5):
                cmp = (d5.get("inputs") or {}).get("comparison") or {}
                res["F"].append({"slug": slug, "trial": pid, "shown_level": d5.get("level"),
                                 "registered": cmp.get("registered_label"), "method": cmp.get("method")})
    return res


def summary(r):
    lines = [f"source: {r['source']}  pages: {r['pages']}",
             f"A  post-hoc subgroup served as pre-specified: {len({x['slug'] for x in r['A']})} of {r['pages']} pages"
             f" ({len(r['A'])} rows); unresolved subgroup served as pre-specified: "
             f"{len({x['slug'] for x in r['A_unresolved']})} of {r['pages']} pages",
             f"B  pooled composite results with an unqualified MACE/3-point label: {len(r['B'])} of {r['B_N']}"
             f" (pages: {len({x['slug'] for x in r['B']})}); derived kinds {r['kinds']}",
             f"C  k=2 computed-but-withheld registered CI worded as a refusal: {len(r['C'])} of {r['C_N']}",
             f"D  common-effect interval served as the primary: {len(r['D'])} of {r['D_N']}",
             f"E  direction-conflict pages ({r['E_N']}): refusal wording {len(r['E_wording'])}, anchor read as conclusion "
             f"{len(r['E_anchor'])}, explanatory/equivalence claims {len(r['E_claims'])}",
             f"F  D5 signals failing the identity check but shown: {len(r['F'])} of {r['F_N']}",
             f"G  primary k=1 results served as a synthesis or without their own population: "
             f"{len({x['slug'] for x in r['G']})} of {r['G_N']} (violations {len(r['G'])})"]
    for key in ("A", "A_unresolved", "B", "C", "D", "E_anchor", "E_claims", "F", "G"):
        for x in r[key]:
            lines.append(f"   {key}: {json.dumps(x, ensure_ascii=False)[:260]}")
    for s in r["E_wording"]:
        lines.append(f"   E_wording: {s}")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    args = sys.argv[1:]
    out = None
    if "--json" in args:
        i = args.index("--json")
        out = args[i + 1]
        del args[i:i + 2]
    r = audit(args[0] if args else "HEAD")
    print(summary(r))
    if out:
        json.dump(r, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
