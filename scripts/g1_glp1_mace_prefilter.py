"""REGEX-FIRST PREFILTER for the GLP-1 reading-(ii) screen (Captain ruling 1, 10 Oct). Under reading (ii) a trial is eligible
only if 3-point MACE (or its exact components) is prespecified as a primary or key-secondary EFFICACY endpoint. A record
whose title + abstract/summary never mentions MACE or any of its three components cannot show that, so no model is asked:
it is recorded NO_MACE_MENTION (typed, with the pattern), and only the remainder goes to the recorded readers.

    python scripts/g1_glp1_mace_prefilter.py -> outputs/k_gap/concept/glp1-ra-mace-t2d.prefilter.json
                                                + glp1-ra-mace-t2d.dual_items_ii.json (the remainder; gitignored)
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CON = os.path.join(ROOT, "outputs", "k_gap", "concept")
MACE = re.compile(r"\bMACE\b|major adverse cardi|cardiovascular (?:death|mortality|outcome|event|safety)|"
                  r"myocardial infarction|\bstroke\b|cardiovascular disease outcome|\bCVOT\b|cardiovascular endpoint",
                  re.I)


def main():
    items = json.load(open(os.path.join(CON, "glp1-ra-mace-t2d.dual_items.json"), encoding="utf-8"))
    keep, drop = [], []
    for it in items:
        r = it["record"]
        text = " ".join(str(r.get(k) or "") for k in ("title", "abstract", "acronym"))
        (keep if MACE.search(text) else drop).append(it)
    out = {"writer": "scripts/g1_glp1_mace_prefilter.py", "pattern": MACE.pattern, "n_items": len(items),
           "n_to_readers": len(keep), "n_no_mace_mention": len(drop),
           "no_mace_mention": [{"key": i["key"], "id": i["record"].get("id"),
                                "title": (i["record"].get("title") or "")[:160]} for i in drop]}
    json.dump(out, open(os.path.join(CON, "glp1-ra-mace-t2d.prefilter.json"), "w", encoding="utf-8", newline="\n"),
              indent=1, ensure_ascii=False)
    json.dump(keep, open(os.path.join(CON, "glp1-ra-mace-t2d.dual_items_ii.json"), "w", encoding="utf-8", newline="\n"),
              indent=1, ensure_ascii=False)
    print(len(items), "items ->", len(keep), "to readers;", len(drop), "NO_MACE_MENTION")
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
