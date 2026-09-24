"""DERIVED NOTICES: what would change on each served page if the delegated bulk acceptance of `screening`
(registry/model_proposals/screening.delegated_acceptance.json) were applied. Read-only: nothing is applied, no page or
queue is written. The output is the before -> after list to be shown to Mahmood BEFORE any served number moves.

An accepted item changes a page only when its accepted decision differs from the page's: the screening queue holds the
records a page SCREENED IN, so an accepted INELIGIBLE means include -> exclude. For each such record:
  * the screened-in count of its page, before -> after;
  * every outcome that POOLS it (outcomes[*].trials[*]): k before -> after, and the pooled estimate recomputed from the
    remaining rows with the served code path (harness.synth.pool), or 'no pooled estimate' when k becomes 0;
  * its trial family;
  * the model's own reasons (the NOT_MET axes and the quotes it read them from), so the reader judges the proposal.

  python scripts/delegated_served_impact.py   -> outputs/model_source/DELEGATED_screening_SERVED_IMPACT.{json,md}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import synth  # noqa: E402

ACC = ROOT / "registry" / "model_proposals" / "screening.delegated_acceptance.json"
QUEUE = ROOT / "registry" / "model_proposals" / "screening.json"


def _num(item_id: str) -> str:
    return item_id.split("::", 1)[1].split(":", 1)[1]


def _row_is(trial: dict, num: str) -> bool:
    return num in (str(trial.get("id") or ""), str(trial.get("label") or "")) or str(trial.get("id") or "").endswith(" " + num)


def _pool(rows: list[dict], scale: str) -> dict:
    if not rows:
        return {"k": 0, "estimate": None, "note": "no pooled estimate (k = 0)"}
    studies = [synth.Study(label=str(t.get("id")), effect=t.get("effect"), ci_low=t.get("ci_low"), ci_high=t.get("ci_high"))
               for t in rows]
    try:
        r = synth.pool(studies, scale=scale)
    except Exception as exc:  # reported, never hidden
        return {"k": len(rows), "estimate": None, "note": f"pool refused: {exc}"}
    return {"k": len(rows), "estimate": round(r.estimate, 4) if getattr(r, "estimate", None) is not None else None,
            "ci_low": getattr(r, "ci_low", None), "ci_high": getattr(r, "ci_high", None),
            "note": "recomputed with harness.synth.pool from the remaining served rows"}


def main() -> int:
    acc = json.loads(ACC.read_text(encoding="utf-8"))
    queue = {e["item_id"]: e for e in json.loads(QUEUE.read_text(encoding="utf-8"))["items"]}
    flips = [a for a in acc["accepted"] if a["accepted_decision"] == "INELIGIBLE" and a.get("rule_decision") == "include"]
    pages: dict[str, dict] = {}
    for a in flips:
        slug = a["item_id"].split("::", 1)[0]
        pages.setdefault(slug, {"records": []})["records"].append(a)
    notices = []
    for slug, p in sorted(pages.items()):
        rv = json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))
        nums = {_num(a["item_id"]) for a in p["records"]}
        screened_in = sum(1 for e in queue.values() if e["item_id"].startswith(slug + "::"))
        outcomes = []
        for o in rv.get("outcomes") or []:
            rows = o.get("trials") or []
            gone = [t for t in rows if any(_row_is(t, n) for n in nums)]
            if not gone:
                continue
            keep = [t for t in rows if t not in gone]
            before = o.get("result") or {}
            outcomes.append({"outcome": o.get("name"), "primary": o.get("primary"),
                             "rows_removed": [t.get("id") for t in gone],
                             "before": {"k": before.get("k", len(rows)), "estimate": before.get("estimate"),
                                        "ci_low": before.get("ci_low"), "ci_high": before.get("ci_high"),
                                        "scale": before.get("scale")},
                             "after": _pool(keep, before.get("scale") or o.get("served_estimand") or "RR")})
        recs = []
        for a in p["records"]:
            ax = (queue[a["item_id"]].get("claim") or {}).get("axes") or {}
            fams = [f["family_id"] for f in rv.get("trial_families") or [] if _num(a["item_id"]) in json.dumps(f)]
            recs.append({"item_id": a["item_id"], "trial_families": fams,
                         "served": "screened in (include)", "proposed": "exclude (INELIGIBLE)",
                         "model_reasons": {k: {"verdict": v.get("verdict"), "quote": v.get("quote")}
                                           for k, v in ax.items() if v.get("verdict") == "NOT_MET"},
                         "proposal_sha256": a["proposal_sha256"]})
        notices.append({"page": slug, "state": "DERIVED_NOTICE_NOT_APPLIED",
                        "screened_in_records": {"before": screened_in, "after": screened_in - len(recs)},
                        "records": recs, "pooled_outcomes_changed": outcomes})
    out = {"source": "registry/model_proposals/screening.delegated_acceptance.json",
           "basis": acc["display"], "applied": False,
           "pages": len(notices), "records_flipped": len(flips),
           "records_in_a_pooled_row": sum(1 for n in notices for r in n["records"]
                                          if any(any(_num(r["item_id"]) in str(x) for x in oc["rows_removed"])
                                                 for oc in n["pooled_outcomes_changed"])),
           "notices": notices}
    base = ROOT / "outputs" / "model_source" / "DELEGATED_screening_SERVED_IMPACT"
    base.with_suffix(".json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    md = ["# Served impact of the delegated bulk acceptance (`screening`) -- DERIVED, NOT APPLIED", "",
          f"Basis: *{acc['display']}* ({acc['authorised_by']}, {acc['date']}, \"{acc['instruction_text']}\"). "
          "Nothing below has been applied. It is the before -> after list for Mahmood.", "",
          f"**{out['records_flipped']} accepted records would go from screened-in to excluded, on {out['pages']} pages; "
          f"{out['records_in_a_pooled_row']} of them sit in a pooled row.**", ""]
    for n in notices:
        md.append(f"## {n['page']}")
        md.append(f"- screened-in records: {n['screened_in_records']['before']} -> {n['screened_in_records']['after']}")
        for oc in n["pooled_outcomes_changed"]:
            b, a = oc["before"], oc["after"]
            md.append(f"- **pooled outcome changes: {oc['outcome']}**{' (primary)' if oc['primary'] else ''}: "
                      f"k {b['k']} -> {a['k']}; {b['scale']} {b['estimate']} -> "
                      f"{a['estimate'] if a['estimate'] is not None else a['note']}")
        if not n["pooled_outcomes_changed"]:
            md.append("- no pooled number changes (the records feed no pooled row)")
        for r in n["records"]:
            why = "; ".join(f"{k} NOT_MET: \"{(v['quote'] or '')[:120]}\"" for k, v in r["model_reasons"].items())
            md.append(f"  - `{r['item_id']}` (families {', '.join(r['trial_families']) or '-'}): {why}")
        md.append("")
    base.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"pages {out['pages']}; records flipped {out['records_flipped']}; in a pooled row {out['records_in_a_pooled_row']}")
    for n in notices:
        for oc in n["pooled_outcomes_changed"]:
            print(f"  {n['page']} / {oc['outcome']}: k {oc['before']['k']} -> {oc['after']['k']}; "
                  f"{oc['before']['estimate']} -> {oc['after']['estimate'] or oc['after']['note']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
