"""AMENDMENT PROBE (read-only): what a candidate outcome-keyword amendment WOULD admit from a topic's held full texts,
through the unchanged full-text rung (harness.pipeline._fulltext_extract). Nothing is written to topics/ or docs/:
widening registered keywords moves protocol_sha, so it is Mahmood's decision, and this probe is the evidence for it.

Each candidate keyword set is run on every held cache/<slug>/ft_<pmid>.txt; every admitted value is listed with its
source sentence, so a wrong admission (a composite, a baseline count) is visible before anyone signs anything.

    python scripts/g1_amendment_probe.py   -> outputs/k_gap/amendment_probe.json
"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import extract, pipeline  # noqa: E402

CANDIDATES = {
    "tocilizumab-covid19-mortality": {
        "REGISTERED": [],
        "DEATH_VERBS": ["died by day 28", "death was reported by day 28", "died on or before day 28", "had died"],
        "BROAD_AT_DAY_28": ["died by day 28", "death was reported by day 28", "died on or before day 28", "at day 28"],
    },
}


def probe(slug, extra):
    c = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    spec = dict(c["primary_outcome"])
    spec["keywords"] = list(spec["keywords"]) + extra
    d = os.path.join(ROOT, "cache", slug)
    out = {}
    for f in sorted(os.listdir(d)):
        if not (f.startswith("ft_") and f.endswith(".txt")):
            continue
        with open(os.path.join(d, f), encoding="utf-8", errors="replace") as fh:
            r = pipeline._fulltext_extract(fh.read(), spec, c["intervention_terms"], c["comparator_terms"],
                                           extract.declared_is_composite(spec["name"]))
        out[f[3:-4]] = ({"admitted": {k: r.get(k) for k in ("ai", "n1i", "ci", "n2i", "effect", "ci_low", "ci_high",
                                                             "scale") if r.get(k) is not None},
                         "source": (r.get("source") or "")[:300]} if not r.get("absent")
                        else {"refused": (r.get("reason") or "")[:200]})
    return out


def main():
    res = {s: {name: {"keywords_added": kw, "by_pmid": probe(s, kw)} for name, kw in sets.items()}
           for s, sets in CANDIDATES.items()}
    with open(os.path.join(ROOT, "outputs", "k_gap", "amendment_probe.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
    for s, sets in res.items():
        for name, v in sets.items():
            adm = {p: x["admitted"] for p, x in v["by_pmid"].items() if "admitted" in x}
            print(s, name, "admitted", len(adm), adm)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
