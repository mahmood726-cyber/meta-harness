"""FILL NOTICES (Mahmood decision 3 Oct): the served review is completed with COMPARATOR_SOURCED rows -- every served
number change goes through a result-change notice (harness/result_changes.py schema) that Mahmood signs. This lane does
not write docs/: it derives ONE packet, batched by topic, guard-checked, for countersignature
(scripts/countersign_result_change.py).

Per topic with comparator-sourced rows (outputs/k_gap/g1/<slug>.json, coverage COMPARATOR_SOURCED):
  before   the served primary result (docs/reviews/<slug>/review.json), exactly as served (result_changes.result_tuple)
  after    harness.synth.pool -- the served engine (Paule-Mandel + HKSJ with floor) -- over the served pool's trials PLUS
           each comparator-sourced row on the served scale (counts when the row carries them; else its effect + CI when
           its measure IS the served scale; otherwise the row cannot fill this page and is listed as not fillable)
  entered_pool  one entry per filled trial, labelled 'from <meta PMID>, <table/figure>, row <label>' with its digest
Guard (fails the packet, never a notice): required keys present; before == served; after recomputed from the listed
inputs; every entered trial carries its provenance; no entered trial is independently confirmed (those are not fills);
the comparator self-reproduces (G1-R REPRODUCED).

    python scripts/g1_fill_notices.py   -> outputs/k_gap/fill_notices_packet.json (state NOT_COUNTERSIGNED)
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import result_changes as rc  # noqa: E402
from harness import synth  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
STUDY_KEYS = ("ai", "n1i", "ci", "n2i", "effect", "ci_low", "ci_high", "e1i", "t1i", "e2i", "t2i",
              "mean1", "sd1", "nc1", "mean2", "sd2", "nc2")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _num(v):
    try:
        return float(str(v).replace(",", "").replace("·", ".").replace("−", "-"))
    except (TypeError, ValueError):
        return None


def served(slug):
    rev = _j(os.path.join(ROOT, "docs", "reviews", slug, "review.json"))
    return next((o for o in rev["outcomes"] if o.get("primary")), None)


def served_studies(prim, scale):
    out = []
    for t in prim.get("trials") or []:
        kw = {k: t.get(k) for k in STUDY_KEYS if t.get(k) is not None}
        out.append(synth.Study(label=str(t.get("label") or t.get("id")), measure=scale, **kw))
    return out


def fill_study(row, scale):
    """A comparator-sourced row as a Study on the SERVED scale, or (None, why)."""
    v = row
    counts = [v.get(k) for k in ("events_t", "n_t", "events_c", "n_c")]
    if all(c is not None for c in counts) and scale.upper() in ("RR", "OR"):
        a, n1, c, n2 = (float(x) for x in counts)
        return synth.Study(label=row["trial"], ai=a, n1i=n1, ci=c, n2i=n2, measure=scale.upper(),
                           source="COMPARATOR_SOURCED counts"), None
    if (v.get("measure") or "").upper() == scale.upper() and None not in (_num(v.get("effect")), _num(v.get("lower")),
                                                                           _num(v.get("upper"))):
        return synth.Study(label=row["trial"], effect=_num(v["effect"]), ci_low=_num(v["lower"]), ci_high=_num(v["upper"]),
                           measure=scale.upper(), source="COMPARATOR_SOURCED effect+CI"), None
    # a continuous row on the served MD scale from per-arm mean / SD / N (V9-02: a 6.5.2.10 arms-combined row; the
    # register re-derives the merge from the printed arms before anything is admitted)
    arms = [_num(v.get(k)) for k in ("mean_t", "sd_t", "n_t", "mean_c", "sd_c", "n_c")]
    if scale.upper() == "MD" and str(v.get("measure") or "").upper() == "MD" and None not in arms:
        m1, s1, n1, m2, s2, n2 = arms
        if n1 != int(n1) or n2 != int(n2) or n1 <= 0 or n2 <= 0:
            # never truncated: a fractional or non-positive N is not a sample size (codex v9-apply-r3 #1)
            return None, f"NOT_FILLABLE: arm N {v.get('n_t')!r} / {v.get('n_c')!r} is not a whole positive number"
        return synth.Study(label=row["trial"], mean1=m1, sd1=s1, nc1=int(n1), mean2=m2, sd2=s2, nc2=int(n2),
                           measure="MD", source="per-arm mean/SD/N"), None
    return None, f"NOT_FILLABLE_ON_SERVED_SCALE ({v.get('measure')} row, served {scale}, no counts)"


def label_of(prov, comp):
    loc = (prov or {}).get("location") or {}
    where = f"{loc.get('kind', 'row')} {loc.get('id', '?')}" + (f" panel {loc['panel']}" if loc.get("panel") else "")
    return (f"from comparator meta PMID {(prov or {}).get('meta_pmid') or comp}, {where}, row "
            f"'{(prov or {}).get('row_label') or loc.get('row_label') or '?'}' (digest {str((prov or {}).get('digest') or '')[:12]}; "
            f"read {(prov or {}).get('read') or '?'})")


def topic_notice(o):
    slug = o["slug"]
    prim = served(slug)
    if not prim or not prim.get("result"):
        return None, ["NO_SERVED_PRIMARY_RESULT"]
    scale = (prim["result"].get("scale") or "").upper()
    before = rc.result_tuple(prim["result"])
    studies = served_studies(prim, scale)
    entered, not_fillable = [], []
    for x in o.get("trials") or []:
        if x.get("coverage") != "COMPARATOR_SOURCED":
            continue
        val = dict((x.get("comparator_sourced") or {}).get("value") or {}, trial=x["label"])
        st, why = fill_study(val, scale)
        if not st:
            not_fillable.append({"trial": x["label"], "why": why})
            continue
        studies.append(st)
        entered.append({"id": f"COMPARATOR_SOURCED::{x['label']}", "label": x["label"],
                        "source": label_of((x.get("comparator_sourced") or {}).get("provenance"), o.get("comparator_pmid")),
                        "values": {k: val.get(k) for k in ("measure", "effect", "lower", "upper", "events_t", "n_t",
                                                           "events_c", "n_c")}})
    if not entered:
        return None, [f"NOTHING_FILLABLE: {not_fillable}"] if not_fillable else ["NO_COMPARATOR_SOURCED_ROWS"]
    pr = synth.pool(studies, scale=scale)
    after = {"k": pr.k, "estimate": round(pr.estimate, 4), "ci_low": round(pr.ci_low, 4), "ci_high": round(pr.ci_high, 4)}
    n = {"slug": slug, "outcome": prim.get("name"), "before": before, "after": after, "left_pool": [],
         "entered_pool": entered,
         "reason": (f"COMPARATOR_SOURCED fill (Mahmood decision 3 Oct): {len(entered)} comparator trial(s) not "
                    f"independently confirmed enter from the comparator meta's OWN per-trial rows; the comparator "
                    f"reproduces its printed pooled result from its rows (G1-R {(o.get('g1r_reproduction') or {}).get('state')}, "
                    f"{(o.get('g1r_reproduction') or {}).get('methods')}); each row is labelled with its meta, figure/table "
                    f"and digest. These rows are COVERAGE, not independent confirmation; they stay queued for primary "
                    f"verification and any disagreement with a primary is a typed discrepancy finding."),
         "conclusion_changed": rc.conclusion_changed(before, after, scale),
         "by": "Claude Opus 5.5 (lane acq/k-gap, g1_fill_notices.py); reviewer countersignature owed: Mahmood",
         "when_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "scale": scale, "engine": "harness.synth.pool (Paule-Mandel + HKSJ, floor max(1, Q/(k-1)))",
         "not_fillable": not_fillable, "state": "NOT_COUNTERSIGNED",
         "inputs_sha256": hashlib.sha256(json.dumps([s.__dict__ for s in studies], sort_keys=True, default=str)
                                         .encode("utf-8")).hexdigest()}
    return n, []


def guard(notice, o):
    """Problems with one notice; [] when it may go to the reviewer."""
    bad = [f"MISSING:{k}" for k in rc.REQUIRED if k not in notice]
    prim = served(notice["slug"])
    if rc.result_tuple(prim["result"]) != notice["before"]:
        bad.append("BEFORE_NOT_THE_SERVED_RESULT")
    if (o.get("g1r_reproduction") or {}).get("state") != "REPRODUCED":
        bad.append("COMPARATOR_DOES_NOT_SELF_REPRODUCE")
    cov = {x["label"]: x for x in o.get("trials") or []}
    for e in notice["entered_pool"]:
        x = cov.get(e["label"]) or {}
        if x.get("coverage") != "COMPARATOR_SOURCED":
            bad.append(f"NOT_COMPARATOR_SOURCED:{e['label']}")
        pv = (x.get("comparator_sourced") or {}).get("provenance") or {}
        if not e.get("source") or "PMID" not in e["source"] or not (pv.get("location") or {}).get("id")                 or not (pv.get("digest") or pv.get("read")):
            bad.append(f"NO_PROVENANCE:{e['label']}")
    # after recomputed from the listed inputs
    scale = notice["scale"]
    st = served_studies(prim, scale) + [fill_study(dict(e["values"], trial=e["label"]), scale)[0] for e in notice["entered_pool"]]
    pr = synth.pool(st, scale=scale)
    if (pr.k, round(pr.estimate, 4), round(pr.ci_low, 4), round(pr.ci_high, 4)) != tuple(
            notice["after"][k] for k in ("k", "estimate", "ci_low", "ci_high")):
        bad.append("AFTER_NOT_RECOMPUTABLE")
    return bad


def main():
    gdir = os.path.join(OUT, "g1")
    notices, skipped, problems = [], {}, {}
    for f in sorted(os.listdir(gdir)):
        if not f.endswith(".json") or ".tmp" in f:
            continue
        o = _j(os.path.join(gdir, f))
        if not o.get("k_comparator_sourced"):
            continue
        n, why = topic_notice(o)
        if not n:
            skipped[o["slug"]] = why
            continue
        g = guard(n, o)
        if g:
            problems[o["slug"]] = g
            continue
        notices.append(n)
    packet = {"packet": "G1 COMPARATOR_SOURCED fill, batched by topic", "state": "NOT_COUNTERSIGNED",
              "guard": {"passed": len(notices), "refused": problems, "skipped": skipped},
              "notices": notices}
    with open(os.path.join(OUT, "fill_notices_packet.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(packet, fh, indent=1, ensure_ascii=False)
    print(json.dumps({"notices": [(n["slug"], n["before"], n["after"], len(n["entered_pool"]), n["conclusion_changed"])
                                  for n in notices], "refused": problems, "skipped": skipped}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
