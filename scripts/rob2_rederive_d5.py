"""Re-derive ONLY Domain 5 of every committed cache/<slug>/rob2.json from the D5 inputs the cache already holds
(V1.0.1, ticagrelor-ACS review: typed components, identity -> timing -> judgment). D1-D4, the trial's registry
resolution and every other field are left exactly as committed; overall and the per-trial rob basis are recomputed
from the domains because D5 feeds them. scripts/rob2_build.py re-reads the AACT snapshot and would also refresh
D1-D4 -- a different change, not made here.

  python scripts/rob2_rederive_d5.py [--write]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import embed, rob2  # noqa: E402


def _match(a, b):
    """The build's own text matcher (scripts/rob2_build.py::_match)."""
    ranked = embed.rank(a, [b])
    return bool(ranked) and ranked[0][1] >= 0.45


def main(argv):
    write = "--write" in argv
    changed = 0
    for p in sorted((ROOT / "cache").glob("*/rob2.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        for tid, t in (doc.get("trials") or {}).items():
            inp = ((t.get("domains") or {}).get("D5_selective_reporting") or {}).get("inputs") or {}
            if "pooled_outcome" not in inp:
                continue
            d5 = rob2.derive_d5(inp.get("registered_primary_outcomes"), inp["pooled_outcome"], _match,
                                inp.get("registered_secondary_outcomes"))
            if d5 == t["domains"]["D5_selective_reporting"]:
                continue
            t["domains"]["D5_selective_reporting"] = d5
            basis = rob2.rob_basis(t["domains"])
            t.update(overall=rob2.overall(t["domains"]), rob_basis=basis,
                     assessed_domains=basis["assessed_domains"], unassessed_domains=basis["unassessed_domains"])
            changed += 1
        if write:
            p.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8", newline="")
    print("D5 re-derived on", changed, "trials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
