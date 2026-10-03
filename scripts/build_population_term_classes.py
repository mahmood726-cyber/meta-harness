"""POPULATION-RULE TERM CLASSES, derived from the versioned AACT snapshot (Mahmood 3 Oct): a population rule (X2,
include.population_none) may only match POPULATION descriptors, never ARM names. O'Neil 2018 randomised adults with
obesity to semaglutide / liraglutide / placebo and was excluded as 'wrong population' because its title names its
active-comparator arm 'liraglutide' -- the same family as condition-as-outcome: a word about the TRIAL'S ARMS read as a
word about WHO WAS ENROLLED.

For every population_none term of every topic (topics/*.json), count exact (case-folded, whole-name) occurrences in the
snapshot's intervention names of an agent type (DRUG / BIOLOGICAL / DIETARY_SUPPLEMENT / COMBINATION_PRODUCT) and in
its condition names. ARM_NAME iff its last word ends in a WHO INN stem, OR it names an agent at least 10 times and at least 3x as often
as it names a condition, OR it is one of the topic's own intervention/comparator terms. Generic words that AACT also
uses as intervention names ('maintenance' 5, 'chemotherapy' 584 vs 234 as a condition, 'androgen deprivation' 4) stay
POPULATION: they describe a design or an exposure-defined population, not an arm. Everything else stays POPULATION. Nothing is typed by
hand; the artefact records the snapshot id + digest and every count.

    python scripts/build_population_term_classes.py   -> harness/data/population_term_classes.json
"""
from __future__ import annotations

import csv
import glob
import io
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "harness", "data", "population_term_classes.json")
AGENT_TYPES = {"DRUG", "BIOLOGICAL", "DIETARY_SUPPLEMENT", "COMBINATION_PRODUCT"}
MIN_AGENT, RATIO = 10, 3
# WHO INN stems (WHO, "The use of stems in the selection of INN"): a word ending in one names an agent
INN_STEMS = ("glutide", "tide", "mab", "gliptin", "gliflozin", "vastatin", "goline", "parin", "xaban", "gatran", "sartan",
             "pril", "olol", "dipine", "prazole", "floxacin", "cillin", "mycin", "nib", "lukast", "setron", "triptan",
             "afil", "oxetine", "semide", "thiazide", "dronate", "parib", "ciclib", "zomib", "grel", "grelor")


def inn_stem(term):
    """The INN stem a term's last word ends in (word of >= 7 letters), or None."""
    w = (term.split() or [""])[-1]
    return next((st for st in INN_STEMS if len(w) >= 7 and w.endswith(st)), None)


def fold(s):
    from harness import lexicon
    return " ".join(lexicon.fold(str(s or "")).lower().split())


def counts(path, name_col, type_col, want, keep):
    csv.field_size_limit(10 ** 9)
    c = Counter()
    with open(path, encoding="utf-8", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="|"):
            if type_col and (r.get(type_col) or "").upper() not in keep:
                continue
            n = fold(r.get(name_col))
            if n in want:
                c[n] += 1
    return c


def main():
    from kgap import aact_adapter
    snap = aact_adapter.snapshot()
    d = aact_adapter.snapshot_dir()
    topics = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "topics", "*.json"))):
        inc = (json.load(open(p, encoding="utf-8")).get("include") or {})
        if inc.get("population_none"):
            topics[os.path.basename(p)[:-5]] = inc
    want = {fold(t) for inc in topics.values() for t in inc["population_none"]}
    ci = counts(os.path.join(d, "interventions.txt"), "name", "intervention_type", want, AGENT_TYPES)
    cc = counts(os.path.join(d, "conditions.txt"), "name", None, want, None)
    out = {"snapshot": {"id": snap.get("id"), "digest": snap.get("digest")}, "agent_types": sorted(AGENT_TYPES),
           "rule": f"ARM_NAME iff INN stem, or agent-name count >= {MIN_AGENT} and >= {RATIO}x condition-name count, "
                   f"or a topic arm term", "inn_stems": list(INN_STEMS),
           "topics": {}}
    for slug, inc in sorted(topics.items()):
        arms = {fold(t) for k in ("intervention_any", "comparator_any", "intervention_none") for t in inc.get(k) or []}
        rows = {}
        for t in inc["population_none"]:
            f = fold(t)
            a, c = ci.get(f, 0), cc.get(f, 0)
            stem = inn_stem(f)
            basis = ("TOPIC_ARM_TERM" if f in arms else f"INN_STEM:-{stem}" if stem else
                     "AACT_COUNTS" if (a >= MIN_AGENT and a >= RATIO * c) else None)
            rows[t] = {"class": "ARM_NAME" if basis else "POPULATION", "agent_name_count": a,
                       "condition_name_count": c, "basis": basis or "AACT_COUNTS"}
        out["topics"][slug] = rows
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
    arm = {s: [t for t, r in v.items() if r["class"] == "ARM_NAME"] for s, v in out["topics"].items()}
    print(json.dumps({s: v for s, v in arm.items() if v}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
