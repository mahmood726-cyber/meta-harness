"""Re-bind every served HARM row in the corpus through the GI safety outcome taxonomy (harness/safety_taxonomy.py) and report
`n of N` harms rows re-bound. Nothing served is written: each change is a NOTICE (before -> after, the source label that decides it).
Also runs the harms-only RoB check on every review, on the served membership.

Sources per trial: the same held sources the refusal auditor reads (abstract, cache full text, registry), plus any verbatim excerpt
file under evidence/safety_taxonomy/sources/<trial>.json -- an added source, read identically for every trial that has one.

Usage: python scripts/rebind_safety_outcomes.py   -> outputs/safety_rebind/REBIND.{json,md}
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import reason_audit, safety_taxonomy as st  # noqa: E402

OUT = ROOT / "outputs" / "safety_rebind"
EXCERPTS = ROOT / "evidence" / "safety_taxonomy" / "sources"


def excerpt_sources(trial: str) -> list[dict]:
    fp = EXCERPTS / f"{trial}.json"
    if not fp.exists():
        return []
    doc = json.loads(fp.read_text(encoding="utf-8"))
    return [{"source_id": f"excerpt:{doc['article'].get('pmcid') or trial}:{i}", "source_kind": "fulltext_excerpt", "text": e["text"]}
            for i, e in enumerate(doc.get("excerpts") or [])]


def main() -> int:
    rows, flags, pages = [], [], 0
    for rv_path in sorted((ROOT / "docs" / "reviews").glob("*/review.json")):
        slug = rv_path.parent.name
        review = json.loads(rv_path.read_text(encoding="utf-8"))
        harm = [o for o in review.get("outcomes") or [] if o.get("kind") == "harm"]
        if not harm:
            continue
        pages += 1
        records = ROOT / "cache" / slug / "records.json"
        sources = reason_audit.sources_by_trial(slug, json.loads(records.read_text(encoding="utf-8")), ROOT) if records.exists() else {}
        for f in st.harms_only_rob_flags(review, reason_audit.canonical_trial_id):
            flags.append({"slug": slug, **f})
        for o in harm:
            for included, bucket in ((True, o.get("trials") or []), (False, o.get("declared_absent_trials") or [])):
                for row in bucket:
                    tid = reason_audit.canonical_trial_id(row.get("id") or row.get("label"))
                    bound = st.bind_results(sources.get(tid, []) + excerpt_sources(tid), tid)
                    r = st.rebind_row(o.get("name"), row, included, bound)
                    rows.append({"slug": slug, "outcome": o.get("name"), "trial": tid, **r})
    rebound = [r for r in rows if r["rebound"]]
    in_tax = [r for r in rows if r["before"]["outcome"]]
    trans = Counter(f"{r['before']['outcome']}/{r['before']['state']} -> {r['after']['outcome']}/"
                    f"{'ADMISSIBLE' if r['after']['admissible'] else r['after']['status']}" for r in rebound)
    notices = [{"kind": "SAFETY_OUTCOME_REBOUND", "slug": r["slug"], "served_outcome": r["outcome"], "trial": r["trial"],
                "before": r["before"], "after_outcome": r["after"]["outcome"], "after_status": r["after"]["status"],
                "after_admissible": r["after"]["admissible"], "admission": r["after"]["admission"],
                "source_label": r["after"]["label"], "source_sentence": r["after"]["label_sentence"], "source_id": r["after"]["source_id"], "why": r["why"],
                "served_number_changed": bool(r["before"]["state"] == "INCLUDED" or r["after"]["admissible"]),
                "note": "a served harm row changes outcome/admission under the taxonomy; applied only through a signed release"}
               for r in rebound]
    report = {"line": f"{len(rebound)} of {len(rows)} harms rows re-bound corpus-wide",
              "N_harms_rows": len(rows), "N_in_taxonomy": len(in_tax), "rebound": len(rebound), "pages_with_harms": pages,
              "transitions": dict(trans), "notices": notices,
              "harms_only_rob": {"line": f"{len(flags)} harms-only contributions lack an outcome-specific RoB entry", "flags": flags},
              "rows": rows}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "REBIND.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    md = ["# GI safety-outcome taxonomy: corpus re-binding", "",
          f"**{report['line']}** ({len(in_tax)} of them are served under a GI taxonomy outcome; {pages} pages carry harms).", "",
          "Outcomes: GI_ANY (unique-patient total required), DIARRHOEA, GI_HOSPITALISATION, GI_DISCONTINUATION. Every result is bound "
          "by its source label to exactly one; percentages alone are RECONSTRUCTED candidates, never pooled.", "",
          "| transition | n |", "|---|---|"] + [f"| {k} | {v} |" for k, v in trans.most_common()] + \
         ["", "Limits: ADMISSIBLE here means the result binds to its outcome with exact counts or an effect+CI; whether an OR can "
          "pool with an RR is still the pool gate's decision. Counts printed as 'n (x%)' take their arm denominators from the "
          "served row. Only GI harms are in the taxonomy; the other harm rows are counted in N and left as served. LoDoCo2's "
          "GI-hospitalisation result is not in any held source, so it cannot re-bind until the source is held (the plant uses a "
          "labelled fixture)."] + \
         ["", "## Notices (served changes; none applied here)", "", "| page | served outcome | trial | before | after | status | source label |",
          "|---|---|---|---|---|---|---|"] + \
         [f"| {n['slug']} | {n['served_outcome']} | {n['trial']} | {n['before']['state']} | {n['after_outcome']} | "
          f"{'ADMISSIBLE' if n['after_admissible'] else n['after_status']} | {n['source_label'][:140].replace('|', '/')} |" for n in notices] + \
         ["", f"## Harms-only RoB check: {report['harms_only_rob']['line']}", "", "| page | trial | outcome | flag |", "|---|---|---|---|"] + \
         [f"| {f['slug']} | {f['trial']} | {f['outcome']} | {f['flag']} |" for f in flags]
    (OUT / "REBIND.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(report["line"]); print(report["harms_only_rob"]["line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
