"""Renders M2_RESULTS_battery.md for the repo: tree + commit named, every verdict MEASURED, the historical
'parity cascade -> conditional' pairs kept visible beside the resolved single-build verdicts."""
import json
import os
import subprocess
import sys

USAGE = ("python scripts/m2_battery_table.py <served_report.json>[,<more.json>] <step1_report.json> <final_report.json> "
         "<out.md>   (a later report of the same case id overrides an earlier one in a comma list)")
if len(sys.argv) != 5:
    sys.exit(USAGE)


def _load(spec):
    out = {}
    for path in spec.split(","):
        for c in json.load(open(path, encoding="utf-8"))["cases"]:
            out[c["id"]] = c
    return out


served, step1, final = _load(sys.argv[1]), _load(sys.argv[2]), _load(sys.argv[3])
ORDER = ["W1a", "W1b", "W1c", "W1d", "W1e", "W2a", "W2b", "W3a", "W3b", "W4a", "W4b", "W5a", "W5b",
         "P1", "P2", "P3", "P4", "P5", "L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9"]
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def v(c):
    return c["verdict"]["verdict"]


def pair(c):
    pc = c["observed"].get("parity_cascade")
    if pc:
        return f"REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to {pc['re_declared_status']}) → {v(c)}"
    return v(c)


lines = [
    "# M2 battery — counterexamples through the real publication route",
    "",
    f"Topic `glp1-ra-mace-t2d`. Served tree = commit `{head}` (8b1fb37d). Repaired trees = the same commit plus branch "
    "`m2/bind-hand-rows` at two states: **step 1** (hand-row binder only; the parity hand status still a build "
    "refusal) and **final** (parity ruling, W1b, companion documents, locator refinements). Every row below is "
    "MEASURED: `scripts/build_topic.py` then `python -m harness.gate` on the real inputs, one committed input "
    "changed per case, exact byte restoration checked after every case (`restoration exact` = the four served files "
    "byte-equal the control rebuild). Runner: `scripts/m2_battery.py`; per-case evidence in the JSON reports beside it.",
    "",
    "**How to read the step-1 column.** Fifteen cases there show a PAIR: the first build refused the WHOLE topic "
    "(`PARITY-RELATION REFUSED: hand status 'SUPERSET' disagrees with computed relation OVERLAPPING`) because a "
    "row-level refusal moved the pool and the hand-written parity status went stale; the harness then re-declared "
    "the hand status to the computed relation and ran again, and the verdict after the arrow is that SECOND build. "
    "A verdict that required an edit to reach is the verdict plus the edit — those pairs are kept here as the record. "
    "In the final column the same cases refuse on the FIRST build (0 cascades): the parity ruling (computed status, "
    "hand text rendered stale, a recorded acknowledgement when the relation changes) removed the cause.",
    "",
    "| id | class | change | served 8b1fb37d | step 1 (binder only) | final | restoration exact (all three) |",
    "|---|---|---|---|---|---|---|",
]
for i in ORDER:
    s, a, f = served[i], step1[i], final[i]
    exact = all(x["restoration"]["served_bytes_equal_control"] for x in (s, a, f))
    lines.append(f"| {i} | {s['class']} | {s['description']} | {v(s)} | {pair(a)} | {v(f)} | {exact} |")


def tally(cases):
    from collections import Counter
    c = Counter(v(x) for x in cases)
    return ", ".join(f"{k} {n}" for k, n in sorted(c.items(), key=lambda kv: -kv[1]))


lines += [
    "",
    "## Tallies (28 cases)",
    "",
    f"- served: {tally(served[i] for i in ORDER)}",
    f"- step 1: {tally(step1[i] for i in ORDER)}; parity cascades {sum(1 for i in ORDER if step1[i]['observed'].get('parity_cascade'))}",
    f"- final: {tally(final[i] for i in ORDER)}; parity cascades {sum(1 for i in ORDER if final[i]['observed'].get('parity_cascade'))}",
    "",
    "## Named misses in the final column (not fixed here, by decision)",
    "",
    "- W4a / W4b — an excluded component treated as included: the layer-1 exclusion relation, not this object.",
    "- W2a / W5b — a canonical `source_span` no longer in the held document: `verified_inputs._validate` raises at "
    "load and the whole topic dies (right check, wrong scope; design note §3).",
    "",
    "## Verdict vocabulary",
    "",
    "WRONG_ADMISSION — the changed row was pooled and the gate passed. REFUSED_CORRECT_REASON — the row was set "
    "aside or refused with the named semantic code (`ENDPOINT_UNBOUND` abstain, `RESULT_INCOMPATIBLE`), the trial "
    "stays visible, the page publishes. GATE_REFUSED_CORRECT_REASON — right reason, page scope (row still pooled, "
    "page withheld). REFUSED_WHOLE_BUILD — the build raised. ADMITTED / ADMITTED_UNCHECKED — a positive pooled with / "
    "without a binding. DOCUMENTED_DECISION_RECORDED — a signed typed refusal rendered as such.",
]
out = sys.argv[4]
open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print("written", out, len(lines), "lines")
