"""D5 registered-outcome identity across the corpus (V1.0.1, ticagrelor-ACS review; harness/rob2.py).

For every D5 signal served at a pinned commit, re-derive it with THIS harness's matcher (typed component sets, every
listed outcome scanned, bleeding and TIA typed, vascular death typed as CV death) and classify:
  FALSE_REASSURANCE  served "matched" to a registered outcome whose typed component set is DISJOINT from the pooled
                     outcome's (PLATO: the CV composite 'matched' Non-CABG major bleeding by text identity)
  FALSE_CONCERN      served "no matching registered outcome" while a registered outcome's component set IS the pooled
                     outcome's (PHILO: MACE = death from vascular causes, MI, stroke)
  SAME_IDENTITY      the identity verdict is unchanged
  python scripts/d5_identity_sweep.py [--base SHA] [--write]  -> evidence/v101_integrated/d5_identity_sweep.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import embed, rob2  # noqa: E402


def _match(a, b):
    """The build's own text matcher (scripts/rob2_build.py::_match), so the re-derivation differs only by the fix."""
    ranked = embed.rank(a, [b])
    return bool(ranked) and ranked[0][1] >= 0.45

OUT = ROOT / "evidence" / "v101_integrated" / "d5_identity_sweep.json"


def served(base: str, slug: str):
    try:
        return json.loads(subprocess.check_output(["git", "-C", str(ROOT), "show", f"{base}:docs/reviews/{slug}/review.json"],
                                                  stderr=subprocess.DEVNULL).decode("utf-8"))
    except subprocess.CalledProcessError:
        return None


def main(argv):
    base = argv[argv.index("--base") + 1] if "--base" in argv else "HEAD"
    rows = []
    for page in sorted((ROOT / "docs" / "reviews").iterdir()):
        r = served(base, page.name)
        for tid, t in (((r or {}).get("rob2") or {}).get("trials") or {}).items():
            d5 = (t.get("domains") or {}).get("D5_selective_reporting") or {}
            inp = d5.get("inputs") or {}
            if "pooled_outcome" not in inp:
                continue
            old = inp.get("comparison") or {}
            new = rob2.derive_d5(inp.get("registered_primary_outcomes"), inp.get("pooled_outcome"),
                                 _match, inp.get("registered_secondary_outcomes"))["inputs"].get("comparison") or {}
            pooled = set(rob2._component_set(inp["pooled_outcome"]))
            # the SERVED match's registered outcome, typed by this harness: a match to an outcome whose component set is
            # not the pooled one (PLATO: Non-CABG major bleeding for the CV composite) is false reassurance, whatever
            # the fixed matcher now binds
            old_reg = set(rob2._component_set(old.get("registered_text") or "")) if old.get("matched") else set()
            # a designed subset match (registered_secondary_component: HHF inside a CV death/HHF composite) is not one
            if old.get("matched") and pooled and old_reg and (not (old_reg & pooled) or
                                                               (old.get("method") == "text_identity" and old_reg != pooled)):
                cls = "FALSE_REASSURANCE"
            elif not old.get("matched") and new.get("matched"):
                cls = "FALSE_CONCERN"
            elif bool(old.get("matched")) != bool(new.get("matched")):
                cls = "IDENTITY_CHANGED"
            else:
                cls = "SAME_IDENTITY"
            rows.append({"slug": page.name, "trial": tid, "class": cls, "served_level": d5.get("level"),
                         "served_method": old.get("method"), "served_label": old.get("registered_label"),
                         "new_matched": new.get("matched"), "new_label": new.get("registered_label"),
                         "pooled_components": sorted(pooled)})
    by = {}
    for x in rows:
        by[x["class"]] = by.get(x["class"], 0) + 1
    served_matched = sum(1 for x in rows if x["served_method"] not in (None, "no_match", "no_registered_outcome"))
    doc = {"schema": "d5-identity-sweep-v1", "base": base, "N_signals": len(rows), "by_class": by,
           "false_reassurance": {"n": by.get("FALSE_REASSURANCE", 0), "N_served_matched": served_matched},
           "false_concern": {"n": by.get("FALSE_CONCERN", 0), "N_served_unmatched": len(rows) - served_matched},
           "rows": [x for x in rows if x["class"] != "SAME_IDENTITY"]}
    if "--write" in argv:
        OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: doc[k] for k in ("N_signals", "by_class", "false_reassurance", "false_concern")}))
    for x in doc["rows"]:
        print(x["class"], x["slug"], x["trial"], x["served_method"], repr(x["served_label"])[:60], "->", repr(x["new_label"])[:60])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
