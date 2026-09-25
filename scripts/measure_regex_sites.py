"""R2 report for the regex sites outside extract.py: precision on the sample where the site fires, SAMPLED recall on
both pools, from registry/model_proposals/site_label_v2.json (recorded labels, not countersigned). Every owned site is
listed: measured, or not measured with the reason. Read-only; writes outputs/regex_layer/SITE_MEASUREMENT.{json,md}.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from regex_layer import site_measure as m  # noqa: E402
from regex_layer.site_detects import DETECTS  # noqa: E402

QUEUES = [ROOT / "registry" / "model_proposals" / f"{t}.json" for t in ("site_label_v2", "site_label_ol", "site_label_ol2", "site_label_ol3", "site_label_ol4", "site_label_ol5", "site_label_deep", "site_label_deep2", "site_label_deep3", "site_label_deep4")]


def main() -> int:
    items = [e for qp in QUEUES if qp.exists() for e in json.loads(qp.read_text(encoding="utf-8"))["items"]]
    cands = {f"{c['site']}::{c['held_sha256'][:16]}": c for c in m.candidates(40)}
    labelled, per_state = [], {}
    for e in items:
        c = cands.get(e["item_id"])
        site = e["item_id"].split("::")[0]
        st = (e.get("verification") or {}).get("state") if e.get("status") == "PROPOSED" else e.get("status")
        if c is None or hashlib.sha256(c["text"].encode("utf-8")).hexdigest() != e.get("held_sha256"):
            st = "HELD_TEXT_MISMATCH"
        per_state.setdefault(site, {}).setdefault(st, 0)
        per_state[site][st] += 1
        if st == "VERIFIER_PASS":
            labelled.append((site, c["text"], bool(e["claim"]["states"])))
    per = m.measure(labelled)
    rows = []
    for site in sorted(DETECTS):
        reason = m.not_measured_reason(site)
        r = per.get(site, {})
        rows.append({"site": site, "measured": reason is None, "reason": reason, "states": per_state.get(site, {}),
                     "precision": r.get("precision", "0 of 0"), "sampled_recall": r.get("recall", "0 of 0"),
                     "fp_examples": r.get("fp_examples", []), "fn_examples": r.get("fn_examples", [])})
    n_meas = sum(r["measured"] for r in rows)
    out = ROOT / "outputs" / "regex_layer" / "SITE_MEASUREMENT"
    out.with_suffix(".json").write_text(json.dumps({"sites": len(rows), "measured": n_meas, "rows": rows}, indent=1,
                                                   ensure_ascii=False) + "\n", encoding="utf-8")
    md = ["# Regex sites outside extract.py -- R2 precision / sampled recall", "",
          f"Measured: **{n_meas} of {len(rows)}** owned sites. Labels: recorded model proposals "
          "(`registry/model_proposals/site_label_v2.json`, `site_label_ol.json`, `site_label_deep.json` when present), "
          "**not countersigned**; recall is sampled recall.", "",
          "| site | precision | sampled recall | labelled |", "|---|---|---|---|"]
    for r in rows:
        if r["measured"]:
            md.append(f"| `{r['site']}` | {r['precision']} | {r['sampled_recall']} | {sum(r['states'].values())} |")
    md += ["", "## Not measured (listed, never dropped)", ""]
    md += [f"- `{r['site']}`: {r['reason']}" for r in rows if not r["measured"]]
    out.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"measured {n_meas} of {len(rows)}")
    for r in rows:
        if r["measured"]:
            print(f"  {r['site'][:44]:44s} P {r['precision']:>9}  R {r['sampled_recall']:>9}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
