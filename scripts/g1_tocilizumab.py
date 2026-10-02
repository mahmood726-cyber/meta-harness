"""G1 MATCH, tocilizumab vs WHO REACT 2021: run g1/tocilizumab.py offline over held bytes and write the result.

  python scripts/g1_tocilizumab.py            -> g1/data/tocilizumab_g1.json (+ a summary on stdout)
  python scripts/g1_tocilizumab.py --aact     -> first rebuild g1/data/aact_toci.json from the local AACT snapshot
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from g1 import tocilizumab as g  # noqa: E402

OUT = os.path.join(ROOT, "g1", "data", "tocilizumab_g1.json")


def main(argv):
    if "--aact" in argv:
        ex = g.build_aact_extract(sorted({v[0] for v in g.IDENTITY.values() if v[0]}))
        open(g.AACT_FILE, "w", encoding="utf-8", newline="\n").write(json.dumps(ex, indent=1, ensure_ascii=False) + "\n")
    r = g.run()
    open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
    pc, pr = r["positive_control"], r["comparator"]["printed"]
    print(f"positive control: REACT's rows -> FE OR {pc['or']} ({pc['lo']}-{pc['hi']}), printed {pr['estimate']} "
          f"({pr['ci_low']}-{pr['ci_high']})")
    print("trials:", r["tally"], "| established vs REACT:", r["vs_react"], "| k matched:", r["k_matched"], "of 19")
    print("pooled, established primary rows:", r["pool_ours_established"], "| REACT, same trials:", r["pool_react_same_trials"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
