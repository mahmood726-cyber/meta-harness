"""Served radius of the R4 ambiguity changes on the paths extract_trial does not reach (read-only; installed in-process).

  eio_first    extract.comparator_effect (harness/pipeline.py ~1902 review comparator.reported, ~2290 blind comparator page)
  k_first      extract._parse_k via extract_meta(...).k (pipeline ~1916 review overlap.theirs_k unless comparator_k is set,
               ~2286 blind comparator page result.k)
  meta_primary extract_meta(...)["primary"] -- no consumer reads it (pipeline reads only .get("k")); measured anyway
  defn_window  extract.composite_heterogeneity (pipeline ~1634, served as result.composite_heterogeneity), recomputed
               from each committed outcome's pooled trials exactly as the pipeline builds _ch_srcs
For each, the served value is computed BEFORE and AFTER, and BEFORE is checked against the committed page where the
page states it (a before that does not reproduce the page means the measurement is off, and is printed).

  REGEX_LAYER_DATA_ROOT=<data tree> python scripts/radius_r4_comparator.py -> outputs/regex_layer/RADIUS_r4_comparator.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import extract  # noqa: E402
from regex_layer import ambiguity as A  # noqa: E402
from regex_layer import radius  # noqa: E402

DATA = radius.DATA


def blind_token(slug: str) -> str:   # scripts/build_topic.py _token(slug, "comparator")
    return "m" + hashlib.sha1(f"{slug}|comparator|mh-blind-v1".encode()).hexdigest()[:8]


def auto_k(a, f, kws):
    return extract.extract_meta(a, kws).get("k") or extract.extract_meta(f, kws).get("k")


def primaries(a, f, kws):
    return [extract.extract_meta(a, kws).get("primary"), extract.extract_meta(f, kws).get("primary")]


def main() -> int:
    rows = {"eio_first": [], "k_first": [], "meta_primary": [], "defn_window": []}
    checked = {"eio_first": [0, 0], "k_first": [0, 0], "defn_window": [0, 0]}   # [reproduced, comparable]
    not_repro = []
    for cfgp in sorted((DATA / "topics").glob("*.json")):
        slug = cfgp.stem
        rp = DATA / "cache" / slug / "records.json"
        if not rp.exists():
            continue
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        records = json.loads(rp.read_text(encoding="utf-8"))
        recs = records.get("records") or []
        byid = {str(r.get("id")): r for r in recs}
        rv = DATA / "docs" / "reviews" / slug / "review.json"
        review = json.loads(rv.read_text(encoding="utf-8")) if rv.exists() else {}
        blind = (DATA / "docs" / "m" / blind_token(slug) / "index.html").exists()
        if cfg.get("comparator_pmid"):
            ca = (byid.get(str(cfg["comparator_pmid"])) or {}).get("abstract") or ""
            cf = records.get("comparator_fulltext") or ""
            committed_rep = {r.get("outcome"): r for r in ((review.get("comparator") or {}).get("reported") or [])}
            for co in cfg.get("comparator_outcomes", []):
                b = extract.comparator_effect(ca, cf, co["keywords"])
                with A.change("eio_first"):
                    a = extract.comparator_effect(ca, cf, co["keywords"])
                cr = committed_rep.get(co["name"])
                if cr is not None and b:
                    checked["eio_first"][1] += 1
                    ok = cr.get("estimate") == b["effect"] and cr.get("ci_low") == b["ci_low"]
                    checked["eio_first"][0] += ok
                    if not ok:
                        not_repro.append({"site": "eio_first", "slug": slug, "outcome": co["name"], "before": b, "page": cr})
                if (b or {}).get("effect") != (a or {}).get("effect") or (b or {}).get("ci_low") != (a or {}).get("ci_low"):
                    rows["eio_first"].append({"slug": slug, "outcome": co["name"], "before": b, "after": a,
                                              "on_review_page": cr is not None, "blind_page": blind})
            kws = cfg["primary_outcome"]["keywords"]
            bk = auto_k(ca, cf, kws)
            with A.change("k_first"):
                ak = auto_k(ca, cf, kws)
            override = cfg.get("comparator_k")
            committed_k = ((review.get("comparator") or {}).get("overlap") or {}).get("theirs_k")
            if override is None and committed_k is not None:
                checked["k_first"][1] += 1
                ok = str(committed_k) == str(bk or "not stated in the comparator abstract/full text")
                checked["k_first"][0] += ok
                if not ok:
                    not_repro.append({"site": "k_first", "slug": slug, "before": bk, "page": committed_k,
                                      "note": "a later stage (second pass / comparator truth) may replace theirs_k"})
            if bk != ak:
                rows["k_first"].append({"slug": slug, "before": bk, "after": ak, "comparator_k_override": override,
                                        "review_theirs_k_committed": committed_k, "blind_page": blind})
            bp = primaries(ca, cf, kws)
            with A.change("meta_primary"):
                ap = primaries(ca, cf, kws)
            if bp != ap:
                rows["meta_primary"].append({"slug": slug, "before": bp, "after": ap, "consumer": "none"})
        # composite heterogeneity over every committed outcome's pooled trials (pipeline _ch_srcs)
        for o in review.get("outcomes") or []:
            trials = o.get("trials") or []
            if not trials:
                continue
            srcs = []
            for t in trials:
                pid = str(t.get("id", "")).replace("PMID ", "").strip() or str(t.get("label", ""))
                ab = (byid.get(pid) or byid.get(str(t.get("label"))) or {}).get("abstract", "")
                srcs.append({"source": (ab or "") + " " + (t.get("source", "") or ""),
                             "endpoint_definition": t.get("endpoint_definition")})
            b = extract.composite_heterogeneity(o.get("name", ""), srcs)
            with A.change("defn_window"):
                a = extract.composite_heterogeneity(o.get("name", ""), srcs)
            committed = (o.get("result") or {}).get("composite_heterogeneity") if isinstance(o.get("result"), dict) else None
            checked["defn_window"][1] += 1
            ok = (committed or "") == (b or "")
            checked["defn_window"][0] += ok
            if not ok:
                not_repro.append({"site": "defn_window", "slug": slug, "outcome": o.get("name"), "before": b, "page": committed})
            if a != b:
                rows["defn_window"].append({"slug": slug, "outcome": o.get("name"), "before": b, "after": a,
                                            "page": committed})
    res = {"differ": {k: len(v) for k, v in rows.items()},
           "before_reproduces_page": {k: f"{v[0]} of {v[1]}" for k, v in checked.items()},
           "not_reproduced": not_repro, "rows": rows}
    out = ROOT / "outputs" / "regex_layer" / "RADIUS_r4_comparator.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("differ", "before_reproduces_page")}))
    for k, v in rows.items():
        for r in v:
            print(k, json.dumps(r, default=str)[:600])
    for r in not_repro:
        print("NOT REPRODUCED", json.dumps(r, default=str)[:400])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
