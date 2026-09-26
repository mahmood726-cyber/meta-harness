"""Count, on held text, the inputs at each R4 ambiguity site of harness/extract.py where >1 DISTINCT candidate exists.

Drives harness.extract.extract_trial exactly as regex_layer/radius.py run_all does (every cached record x source x declared
outcome), with the regex_layer.ambiguity replacements installed in RECORD-ONLY mode (ENABLED empty). CONTROL: with nothing
enabled every output must equal the unpatched output; a mismatch is printed and makes the run exit 1.
  pass A: sub-function sites (arm_*, effect_first, eio_first, arm_ns, cont/rate_pairs, denom_each) under the served
          extract_trial -- only calls the served path actually makes are recorded
  pass B: sentence-stage sites (sent_*) -- the replacement extract_trial with served sub-functions
  pass C: comparator paths (comparator_effect -> eio_first; extract_meta -> meta_primary, k_first) and the
          composite_heterogeneity definition window (defn_window) over every cached record abstract

  REGEX_LAYER_DATA_ROOT=<data tree> python scripts/r4_ambiguity_count.py  -> outputs/regex_layer/R4_AMBIGUITY_COUNT.json
"""
from __future__ import annotations

import contextlib
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
SUB = ["arm_pairs", "arm_den", "arm_samepos", "effect_first", "eio_first", "arm_ns", "cont_pairs", "rate_pairs",
       "denom_each"]
SENT = ["sent_hr", "sent_arm", "sent_effect", "sent_rate", "sent_cont"]


@contextlib.contextmanager
def installed(attrs):
    old = {a: getattr(extract, a) for a in attrs}
    try:
        for a in attrs:
            setattr(extract, a, A.replacement(a, old[a]))
        yield
    finally:
        for a, v in old.items():
            setattr(extract, a, v)


def run(slug, cfg, recs, attrs, record):
    A.RECORD.clear(); A.RECORD.update(record); A.ENABLED.clear()
    interv = cfg.get("intervention_terms", ["colchicine"])
    comp = cfg.get("comparator_terms", ["placebo", "control"])
    res = {}
    with installed(attrs):
        for rec in recs:
            for src, text in radius.texts(slug, rec):
                if not text:
                    continue
                for o in radius.outcomes(cfg):
                    A.CONTEXT.clear()
                    A.CONTEXT.update({"slug": slug, "id": str(rec.get("id")), "source": src, "outcome": o.get("name")})
                    dc = extract.declared_is_composite(o.get("name", ""))
                    try:
                        ex = extract.extract_trial(text, o["keywords"], interv, comp, declared_composite=dc,
                                                   estimand=o.get("estimand"))
                    except Exception as exc:
                        ex = {"CRASH": repr(exc)}
                    res[(str(rec.get("id")), src, o.get("name"))] = json.dumps(ex, sort_keys=True, default=str)
    return res


def h(t):
    return hashlib.sha1(t.encode("utf-8", "replace")).hexdigest()[:12]


def summarise(hits, sites):
    out = {}
    for s in sites:
        hs = [x for x in hits if x["site"] == s]
        by_src = {}
        for src in ("abstract", "pmc_fulltext", "comparator_abstract", "comparator_fulltext", "record_abstract"):
            sh = [x for x in hs if x.get("source") == src]
            if not sh:
                continue
            by_src[src] = {"distinct_inputs": len({(x.get("slug"), x.get("id"), h(x["text"])) for x in sh}),
                           "extractions_touched": len({(x.get("slug"), x.get("id"), x.get("outcome")) for x in sh})}
        ex = {}
        for x in hs:
            k = (x.get("slug"), x.get("id"), x.get("source"), h(x["text"]))
            ex.setdefault(k, {"slug": x.get("slug"), "id": x.get("id"), "source": x.get("source"),
                              "text": x["text"][:400], "values": x["values"]})
        out[s] = {"by_source": by_src, "examples": list(ex.values())[:8]}
    return out


def main() -> int:
    hits_a, hits_b, hits_c, control_bad = [], [], [], []
    n = 0
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for cfgp in sorted((DATA / "topics").glob("*.json")):
        slug = cfgp.stem
        if only and slug != only:
            continue
        rp = DATA / "cache" / slug / "records.json"
        if not rp.exists():
            continue
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        records = json.loads(rp.read_text(encoding="utf-8"))
        recs = records.get("records") or []
        base = radius.run_all(slug, cfg, recs)
        n += len(base)
        A.HITS.clear()
        ra = run(slug, cfg, recs, ["extract_arm_counts", "extract_effect", "effect_in_outcome", "_arm_ns",
                                   "extract_continuous", "extract_rate", "_DENOM_EACH"], SUB)
        hits_a += list(A.HITS)
        A.HITS.clear()
        rb = run(slug, cfg, recs, ["extract_trial"], SENT)
        hits_b += list(A.HITS)
        for k in base:
            for name, r in (("A", ra), ("B", rb)):
                if base[k] != r.get(k):
                    control_bad.append({"pass": name, "slug": slug, "key": list(k), "base": base[k], "patched": r.get(k)})
        # pass C: comparator paths + composite definition windows
        A.HITS.clear()
        A.RECORD.clear(); A.RECORD.update({"eio_first", "meta_primary", "k_first"})
        if cfg.get("comparator_pmid"):
            byid = {str(r.get("id")): r for r in recs}
            comp_abs = (byid.get(str(cfg["comparator_pmid"])) or {}).get("abstract") or ""
            comp_full = records.get("comparator_fulltext") or ""
            with installed(["effect_in_outcome", "extract_meta", "_parse_k"]):
                for src, txt in (("comparator_abstract", comp_abs), ("comparator_fulltext", comp_full)):
                    if not txt:
                        continue
                    A.CONTEXT.clear(); A.CONTEXT.update({"slug": slug, "id": str(cfg["comparator_pmid"]), "source": src})
                    for co in cfg.get("comparator_outcomes", []):
                        A.CONTEXT["outcome"] = co.get("name")
                        extract.effect_in_outcome(txt, co["keywords"], window=140)
                    A.CONTEXT["outcome"] = "k/primary"
                    extract.extract_meta(txt, cfg["primary_outcome"]["keywords"])
        hits_c += list(A.HITS)
        for rec in recs:
            ab = (rec.get("abstract") or "").lower()
            wins = A.defn_windows(ab)
            if len(wins) > 1:
                for vocab in ("cv", "kidney"):
                    kws = (["50%", "40%", "57%", "doubling", "end-stage", "dialysis"] if vocab == "kidney" else
                           ["unstable angina", "revascular", "heart failure", "transient ischemic", "hospital for cardiovascular"])
                    sigs = {tuple(sorted(k for k in kws if k in w)) for w in wins}
                    if len(sigs) > 1:
                        hits_c.append({"slug": slug, "id": str(rec.get("id")), "source": "record_abstract",
                                       "outcome": vocab, "site": "defn_window", "text": " || ".join(wins),
                                       "values": sorted(map(repr, sigs))})
        print(f"{slug}: {len(base)} extractions; hits A {len(hits_a)} B {len(hits_b)} C {len(hits_c)}; "
              f"control mismatches {len(control_bad)}", flush=True)
    res = {"extractions": n, "control_mismatches": control_bad,
           "sites": summarise(hits_a, SUB) | summarise(hits_b, SENT) | summarise(hits_c, ["eio_first", "meta_primary",
                                                                                           "k_first", "defn_window"])}
    # pass C's eio_first is the comparator path; keep it apart from pass A's extract_trial path
    res["sites"]["eio_first"] = summarise(hits_a, ["eio_first"])["eio_first"]
    res["sites"]["eio_first_comparator"] = summarise(hits_c, ["eio_first"])["eio_first"]
    out = ROOT / "outputs" / "regex_layer" / "R4_AMBIGUITY_COUNT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    for s, v in res["sites"].items():
        print(f"{s}: {json.dumps(v['by_source'])}")
    print(f"CONTROL: {len(control_bad)} mismatches of {n} extractions x 2 passes")
    return 1 if control_bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
