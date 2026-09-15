"""DIAGNOSTIC-DECISION DECOUPLING WAS UNIVERSAL: the headline capture, generated from the hazard-consumer sweep.

Reads the pre-wiring sweep (docs/evidence/hazard-consumers-2026-09-14/01-sweep-32.txt, computed against the base
tree before any consumer was wired) and docs/hazard_acknowledgements.json, and writes
docs/evidence/decoupling-universal-2026-09-15/01-per-topic-before.txt: for every one of the 32 topics, the hazards
that were detected, represented on the page, and routed to the reader instead of to a decision -- named -- and, per
hazard pair, whether it is now WIRED to a gate, acknowledged as INFORMATIONAL, or acknowledged as OWED a consumer.
Crystalloids was not an unlucky page. A zero on any topic reads "not observed under this sweep", never "clean".
"""
from __future__ import annotations
import io
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWEEP = os.path.join(ROOT, "docs", "evidence", "hazard-consumers-2026-09-14", "01-sweep-32.txt")
ACKS = os.path.join(ROOT, "docs", "hazard_acknowledgements.json")
OUT_DIR = os.path.join(ROOT, "docs", "evidence", "decoupling-universal-2026-09-15")
# Pairs wired to a consumer by the hazard-consumer tranche (9f541dde); everything else UNWIRED was acknowledged.
WIRED_IN_TRANCHE = {("RETRIEVAL_CLASS", "NOT_RUN"), ("RETRIEVAL_CLASS", "UNRECORDED"),
                    ("SEARCH_ENUMERATION_ONLY", "NOT_RUN"), ("SEARCH_PROVENANCE", "RETRACTED")}
OWED = {"DEFINITION_AUDIT", "ROB_SENSITIVITY"}


def parse_sweep(path: str):
    rows = []
    base_ref = None
    for line in open(path, encoding="utf-8"):
        if line.startswith("base_ref:"):
            base_ref = line.split(":", 1)[1].strip()
        parts = [p.strip() for p in line.rstrip("\n").split(" | ")]
        if len(parts) == 8 and parts[0] != "slug":
            rows.append(dict(zip(("slug", "limitation_id", "kind", "severity", "evidence_state", "consumer_gate",
                                  "verdict", "status"), parts)))
    return base_ref, rows


def main() -> int:
    base_ref, rows = parse_sweep(SWEEP)
    acks = {(a.get("kind"), a.get("evidence_state")): a for a in json.load(open(ACKS, encoding="utf-8"))["acknowledgements"]}
    by_topic = defaultdict(list)
    for r in rows:
        by_topic[r["slug"]].append(r)
    topics = sorted(by_topic)
    unwired_topics = [s for s in topics if any(r["status"] == "UNWIRED" and r["severity"] in ("BLOCKS_CLAIM", "QUALIFIES_CLAIM") for r in by_topic[s])]
    out = [
        "DIAGNOSTIC-DECISION DECOUPLING WAS UNIVERSAL ACROSS THE CORPUS",
        f"Sweep source: {os.path.relpath(SWEEP, ROOT).replace(os.sep, '/')} (computed against base {base_ref}, before any consumer was wired)",
        "Definition (external auditor, 2026-09-15): a validity hazard correctly detected and represented, but its state not causally",
        "connected to the analytic decision it should constrain -- disclosure-as-control. PROCESS, optimistic, major-to-critical.",
        "",
        f"RESULT: {len(unwired_topics)} of {len(topics)} topics carried at least one BLOCKS_CLAIM or QUALIFIES_CLAIM hazard that was detected,",
        "rendered for the reader, and routed to NO decision. Named:",
        "  " + ", ".join(unwired_topics),
        "",
        "Per topic, the hazards that were routed to the reader instead of to a decision (kind / evidence_state / severity),",
        "and what happened to each pair afterwards: WIRED (now feeds invalidation.assess, 9f541dde) | INFORMATIONAL (acknowledged:",
        "disclosure suffices, signed) | OWED (acknowledged as owed a consumer -- NOT informational; GATE_GAPS).",
        "",
    ]
    pair_counts = defaultdict(int)
    for s in topics:
        unwired = [r for r in by_topic[s] if r["status"] == "UNWIRED"]
        wired = [r for r in by_topic[s] if r["status"] == "WIRED"]
        out.append(f"== {s}: {len(unwired)} unwired of {len(by_topic[s])} hazard objects at base; {len(wired)} already wired")
        for r in sorted(unwired, key=lambda x: (x["severity"], x["kind"])):
            pair = (r["kind"], r["evidence_state"])
            pair_counts[pair] += 1
            if pair in WIRED_IN_TRANCHE:
                fate = "WIRED -> invalidation.assess (search_not_executed)"
            elif r["kind"] in OWED:
                fate = "OWED a consumer (acknowledged, not informational)"
            elif pair in acks:
                fate = "INFORMATIONAL (acknowledged, signed)"
            else:
                fate = "UNACCOUNTED -- not observed"
            out.append(f"   {r['severity']:15s} {r['kind']:26s} {r['evidence_state']:20s} -> {fate}   [{r['limitation_id'].split(':', 2)[-1]}]")
    out += ["", "PAIR TOTALS ACROSS THE CORPUS (unwired at base):"]
    for pair, n in sorted(pair_counts.items(), key=lambda kv: -kv[1]):
        fate = ("WIRED" if pair in WIRED_IN_TRANCHE else "OWED" if pair[0] in OWED else "INFORMATIONAL" if pair in acks else "UNACCOUNTED")
        out.append(f"   {n:4d}  {pair[0]:26s} {pair[1]:20s} {fate}")
    out += ["",
            "What this confirms: the auditor's mechanism is real and general, not an instance they happened to construct.",
            "Crystalloids (SMART/SALT/SPLIT pooled with a cluster-crossover caveat and every compatibility key MATCH) was the",
            "instance; the corpus state was the rule. The honest distinction kept here: DEFINITION_AUDIT and ROB_SENSITIVITY are",
            "acknowledged as OWED a consumer, not as informational; a signed acknowledgement is not a wiring."]
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "01-per-topic-before.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print(f"decoupling-universal: {len(unwired_topics)} of {len(topics)} topics; {sum(pair_counts.values())} unwired hazard objects at base")
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
