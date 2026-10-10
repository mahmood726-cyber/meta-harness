"""DISAGREE LIST for the Captain: every dual-screen record the two readers split on (never counted either way), with each
reader's decision, rule and verbatim quote, so a ruling can be made per record. A tie-break reader would change the
pre-registered dual rule, which is the Captain's decision, not the lane's.

    python scripts/g1_disagree_list.py -> outputs/k_gap/concept/_disagree_for_captain.md
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CON = os.path.join(ROOT, "outputs", "k_gap", "concept")


def main():
    w = ["# Dual-screen DISAGREE records -- for a Captain ruling (k-gap)", "",
         "Each row: the record, then reader A (gpt-6-astra) and B (gpt-5.5) decision / rule / verbatim quote. "
         "The VOID GLP-1 run is not included. noac is held as (b); its rows are listed for completeness only.", ""]
    for p in sorted(glob.glob(os.path.join(CON, "_dual_a_*.json"))):
        rows = json.load(open(p, encoding="utf-8"))["rows"]
        dis = {k: r for k, r in rows.items() if r.get("verdict") == "DISAGREE"}
        if not dis:
            continue
        w += [f"## {os.path.basename(p)} -- {len(dis)} DISAGREE", ""]
        for k, r in dis.items():
            rec = r.get("record") or {}
            w.append(f"- **{k.split('::')[-1]}** ({k.split('::')[1]}) {(r.get('title') or rec.get('title') or '')[:140]}")
            for tag, v in sorted((r.get("readers") or {}).items()):
                q = (v.get("quote") or "").replace("\n", " ")[:260]
                w.append(f"  - {tag}: {v.get('gated') or v.get('decision')} / {v.get('rule')} -- \"{q}\" ({v.get('record_id')})")
        w.append("")
    out = os.path.join(CON, "_disagree_for_captain.md")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(w) + "\n")
    print(out, sum(1 for l in w if l.startswith("- **")))
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
