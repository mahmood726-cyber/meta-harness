"""Corpus-wide: how many ABSENCE states in the SERVED reviews are contradicted by a matching typed row in held text (harness.held_rows).

Reads each review as SERVED (docs/reviews/<slug>/review.json at --served-ref, default origin/main) -- never the working tree, which
after regeneration already carries the enforced state and would report zero. Held text is the committed cache (abstracts, full text
and tables, registry) plus every span another extraction in the same review quotes for the trial.
Reports, by KIND of absence state:
  * n of N known-missing NOT_IN_COMMITTED_SOURCE states that are actually held;
  * n of N absent-claims (declared-absent OUTCOME_NOT_IN_SOURCE / SOURCE_NOT_RETRIEVED / outcome_not_reported, and known-missing
    NOT_IN_COMMITTED_SOURCE) contradicted by held text, and how many only through another extraction's quoted text;
  * contradicted rows whose held counts have an outcome-ascertained denominator below the analysis group (missing carried);
  * eligibility flags (a stated non-target subpopulation) on contradicted rows.
Nothing served is written.   python scripts/held_row_audit.py [--served-ref REF]  -> outputs/held_rows/HELD.{json,md}
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import held_rows, pipeline, reason_audit  # noqa: E402

OUT = ROOT / "outputs" / "held_rows"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--served-ref", default="origin/main")
    ap.add_argument("--data-root", default=str(ROOT), help="where topics/ and cache/ are read (default: this tree)")
    a = ap.parse_args()
    data = Path(a.data_root)
    sha = subprocess.run(["git", "-C", str(data), "rev-parse", a.served_ref], capture_output=True, text=True, check=True).stdout.strip()
    rows, pages = [], 0
    for topic_path in sorted((data / "topics").glob("*.json")):
        slug = topic_path.stem
        got = subprocess.run(["git", "-C", str(data), "show", f"{sha}:docs/reviews/{slug}/review.json"], capture_output=True)
        records = data / "cache" / slug / "records.json"
        if got.returncode != 0 or not records.exists():
            continue
        pages += 1
        review = json.loads(got.stdout.decode("utf-8"))
        topic = json.loads(topic_path.read_text(encoding="utf-8"))
        specs = {sp.get("name"): sp for sp, _ in pipeline._outcome_specs(topic)}
        srcs = reason_audit.sources_by_trial(slug, json.loads(records.read_text(encoding="utf-8")), data)
        for c in held_rows.contradictions(slug, review, srcs, specs, [review.get("question") or ""]):
            o = next(x for x in review["outcomes"] if x.get("name") == c["outcome"])
            if c["contradicted"]:                              # was it reachable WITHOUT another extraction's quoted text?
                c["held_without_cross_extraction"] = bool(held_rows.matching_rows(o, c["trial"], srcs.get(c["trial"], []),
                                                                                  specs.get(c["outcome"])))
            else:                                              # the detector's REACH: rows it cannot decide, shown, not dropped
                cands = reason_audit.typed_candidates(o, {"id": c["trial"]}, srcs.get(c["trial"], []) +
                                                      held_rows.review_texts(review, c["trial"]), specs.get(c["outcome"]))
                outcome_like = [x for x in cands if x.get("role") in ("OUTCOME_COUNT", "EFFECT_ESTIMATE")]
                pres = lambda x: [m.split(":", 1)[0] for m in x["mismatch"] if m.split(":", 1)[0] in held_rows._PRESENCE_FIELDS]
                tp_only = [x for x in outcome_like if pres(x) == ["timepoint"]]
                kw_only = [x for x in outcome_like if not pres(x)]          # fits every presence field, but not by the outcome's own name
                pick, why = ((tp_only[0], "names the outcome, but its timepoint is unstated or differs") if tp_only else
                             (kw_only[0], "fits, but names the outcome only through a spec keyword, not its own name") if kw_only else (None, None))
                if pick:
                    c["possibly_held"] = {"why": why, "timepoint": pick.get("timepoint"), "span": pick["span"][:200],
                                          "source_id": pick["source_id"]}
            rows.append(c)
    by_kind = Counter(f"{r['kind']}:{r['state']}" for r in rows)
    hit_kind = Counter(f"{r['kind']}:{r['state']}" for r in rows if r["contradicted"])
    km = [r for r in rows if r["kind"] == "known_missing"]
    hits = [r for r in rows if r["contradicted"]]
    cross_only = [r for r in hits if not r.get("held_without_cross_extraction")]
    missing_carried = [r for r in hits if r.get("counts") and any((x.get("missing") or 0) > 0 for x in r["counts"]["arms"])]
    flagged = [r for r in hits if r.get("eligibility")]
    possibly = [r for r in rows if r.get("possibly_held")]
    report = {"served_ref": f"{a.served_ref} = {sha}", "pages": pages,
              "not_in_committed_source_held": {"n": sum(r["contradicted"] for r in km), "N": len(km),
                                               "line": f"{sum(r['contradicted'] for r in km)} of {len(km)} NOT_IN_COMMITTED_SOURCE states are actually held"},
              "absent_claims_contradicted": {"n": len(hits), "N": len(rows),
                                             "line": f"{len(hits)} of {len(rows)} absent-claims are contradicted by held text"},
              "only_through_another_extraction": len(cross_only),
              "kinds": {k: {"N": v, "contradicted": hit_kind.get(k, 0)} for k, v in sorted(by_kind.items())},
              "missing_carried": len(missing_carried), "eligibility_flagged": len(flagged),
              "possibly_held_timepoint": len(possibly), "rows": rows}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "HELD.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    md = ["# Held-row invariant: absence states contradicted by held text (served corpus)", "",
          f"Served reviews read at `{report['served_ref']}` ({pages} pages).", "",
          f"- **{report['not_in_committed_source_held']['line']}**",
          f"- **{report['absent_claims_contradicted']['line']}**; {len(cross_only)} of them only through text another extraction in "
          "the same review quotes", f"- {len(missing_carried)} contradicted rows carry a missing count (ascertained n below the analysis "
          "group)", f"- {len(flagged)} contradicted rows are flagged for eligibility adjudication", "",
          "| kind of absence state | N | contradicted |", "|---|---|---|"] + \
         [f"| {k} | {v['N']} | {v['contradicted']} |" for k, v in report["kinds"].items()] + \
         ["", "| page | outcome | trial | state | held row (source) | counts (ascertained) | eligibility |", "|---|---|---|---|---|---|---|"] + \
         [f"| {r['slug']} | {r['outcome']} | {r['trial']} | {r['state']} | {r['held_row']['span'][:110].replace('|', '/')} "
          f"({r['held_row']['source_id']}) | "
          + ("; ".join((f"{x['events']}/{x['n_ascertained']}" if x["n_ascertained"] is not None
                        else f"{x['events']} of group {x['n_group']} (ascertainment unstated)")
                       + (f" (missing {x['missing']})" if x.get("missing") else "") for x in r["counts"]["arms"]) if r.get("counts") else "—")
          + " | " + ("; ".join(f"{f['subpopulation']} {f['share_percent']:g}%" for f in r["eligibility"]) or "—") + " |" for r in hits] + \
         ["", f"## Reach: {len(possibly)} absence states the detector cannot decide (outcome named, timepoint unstated or different)", "",
          "Not counted as contradicted; listed so the reach is visible. Each needs a reader.", "",
          "| page | outcome | trial | state | held candidate (timepoint) |", "|---|---|---|---|---|"] + \
         [f"| {r['slug']} | {r['outcome']} | {r['trial']} | {r['state']} | {r['possibly_held']['span'][:120].replace('|', '/')} "
          f"({r['possibly_held']['timepoint'] or 'unstated'}) |" for r in possibly]
    (OUT / "HELD.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(report["not_in_committed_source_held"]["line"])
    print(report["absent_claims_contradicted"]["line"], f"({len(cross_only)} only via another extraction)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
