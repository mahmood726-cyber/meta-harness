"""Summarise outputs/k_gap/k_gap_table.json -> outputs/k_gap/SUMMARY.md (n of N per source and class).

Every number is counted from the table; nothing is typed by hand. Also measures the model-proposal
instrument against the deterministic table parse on topics where both resolved trials (agreement on the
resolved trial identity sets), so the proposal fallback carries a measured error rate, not an assumed one.

    python scripts/k_gap_summary.py
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "k_gap")

GAP_ORDER = ["IDENTIFICATION", "SCREEN_OR_ELIGIBILITY", "ACQUISITION", "EXTRACTION_FROM_TABLE", "MEASURE_MISMATCH",
             "SCOPE_MISMATCH", "GENUINELY_UNAVAILABLE_OPEN"]
SRC_ORDER = ["AACT_RESULTS", "PMC_OA_FULLTEXT", "NONE_OPEN_PROBED"]


def fam_key(r):
    return r["ncts"][0] if r["ncts"] else (r["pmids"][0] if r["pmids"] else None)


def main():
    t = json.load(open(os.path.join(OUT, "k_gap_table.json"), encoding="utf-8"))
    topics, all_rows = t["topics"], t["trials"]
    # KINDS: confirmed members (citing table / gated proposal) and reference-seed CANDIDATES are different
    # objects. The headline counts confirmed members only; candidates are reported on their own line.
    rows = [r for r in all_rows if r["unit_source"] != "REFERENCE_SEED"]
    seed = [r for r in all_rows if r["unit_source"] == "REFERENCE_SEED"]
    N = len(topics)
    st = Counter(x["comparator_set_state"] for x in topics)
    wrong = [x["slug"] for x in topics if x["held_text"]["state"] == "HELD_TEXT_NOT_NAMED_ARTICLE"]
    elig = [r for r in rows if r["drug"] != "OTHER_AGENT" and r["status"] != "UNRESOLVED"]
    # one row per trial family per topic (a comparator can list two reports of one trial)
    seen, uniq = set(), []
    for r in elig:
        k = (r["slug"], fam_key(r))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    T = len(uniq)
    pooled = sum(r["gap_class"] == "POOLED" for r in uniq)
    miss = [r for r in uniq if r["gap_class"] != "POOLED"]
    M = len(miss)
    gc = Counter(r["gap_class"] for r in miss)
    closable = [r for r in miss if r["gap_class"] not in ("MEASURE_MISMATCH", "SCOPE_MISMATCH")]
    sc = Counter(r["closable_by"] for r in closable)
    unres = sum(r["status"] == "UNRESOLVED" for r in rows)
    other = sum(r["drug"] == "OTHER_AGENT" for r in rows)
    unconf = sum(r["drug"] == "AGENT_UNCONFIRMED" for r in uniq)
    typed = Counter()
    for r in closable:
        if r["closable_by"] == "AACT_RESULTS":
            pt = {m.get("param_type") for m in r["aact"]["outcome_matches"]}
            typed["COUNT_OF_PARTICIPANTS" if "COUNT_OF_PARTICIPANTS" in pt else "OTHER_PARAM_TYPE"] += 1
    per = sorted([x for x in topics if x["comparator_set_state"] in ("TABLE_ENUMERATED", "PROPOSAL_ENUMERATED_GATED")],
                 key=lambda x: -x["missing"])
    lines = [
        f"# K-GAP summary ({t['generated']}, AACT snapshot {os.path.basename(t['aact_snapshot'] or 'NONE')})",
        "",
        f"1. Topics with a comparator meta: **{N}**; lines 3-7 count the {N - st['REFERENCE_SEED_CANDIDATES'] - st['NOT_ENUMERABLE_OPEN']} whose set is CONFIRMED. Comparator trial set enumerated from: citing JATS table "
        f"{st['TABLE_ENUMERATED']}, gated model proposal {st['PROPOSAL_ENUMERATED_GATED']}, open reference-list seed "
        f"(candidate superset) {st['REFERENCE_SEED_CANDIDATES']}, not enumerable from open sources {st['NOT_ENUMERABLE_OPEN']}.",
        f"2. Held comparator text is a DIFFERENT article than the cited comparator: **{len(wrong)} of {N}** ({', '.join(wrong) or 'none'}).",
        f"3. Comparator units read: {len(rows)}; resolved, drug-specific trial families: **{T}** "
        f"(excluded: {other} other-agent units, {unres} unresolved labels; {unconf} kept with agent unconfirmed).",
        f"4. Of those {T}: pooled by us **{pooled}**, missing **{M}**.",
        "5. Missing by class: " + ", ".join(f"{k.lower()} {gc[k]}" for k in GAP_ORDER if gc[k]) + f" (of {M}).",
        f"6. Missing and not a deliberate measure refusal: {len(closable)}. Open source that could supply a typed result: "
        + ", ".join(f"{k} {sc[k]} of {len(closable)}" for k in SRC_ORDER) + ".",
        f"7. AACT-closable by result type: COUNT_OF_PARTICIPANTS {typed['COUNT_OF_PARTICIPANTS']}, other param types "
        f"{typed['OTHER_PARAM_TYPE']} (hazard ratios / rates / means need a measure-compatible estimand, not a 2x2).",
        f"7b. Reference-seed CANDIDATES (not confirmed members; {len({r['slug'] for r in seed})} topics whose comparator "
        f"set is not enumerable from an open table or quoted text): {len(seed)} RCT-typed, agent-named reports cited "
        f"by the comparator; pooled by us {sum(r['gap_class'] == 'POOLED' for r in seed)}, not pooled "
        f"{sum(r['gap_class'] != 'POOLED' for r in seed)}.",
        "8. Largest gaps: " + "; ".join(f"{x['slug']} {x['missing']}/{x['drug_specific_resolved']}" for x in per[:6]) + ".",
        "9. NOT probed yet (so absent from 'closable'): Drugs@FDA reviews, EMA EPARs, NICE committee papers, "
        "Unpaywall non-PMC OA copies, OA supplements. 'NONE_OPEN_PROBED' means none of AACT posted results / PMC OA held it.",
        "10. Read with: the comparator set is the comparator's DRUG-SPECIFIC included studies (any outcome); a trial "
        "missing here may be outside our registered outcome/estimand, which a class of SCREEN_OR_ELIGIBILITY or "
        "MEASURE_MISMATCH records rather than hides.",
        "",
    ]
    # instrument agreement: proposal vs table on topics where both resolved
    agr = []
    for x in topics:
        tried = {d["source"]: d for d in x.get("sources_tried", [])}
        if "JATS_TABLE" in tried and "MODEL_PROPOSAL_GATED" in tried:
            agr.append((x["slug"], tried["JATS_TABLE"]["drug_specific_resolved"],
                        tried["MODEL_PROPOSAL_GATED"]["drug_specific_resolved"]))
    if agr:
        lines += ["## Proposal instrument vs deterministic table parse (drug-specific resolved counts)", "",
                  "| topic | table | proposal |", "|---|---|---|"]
        lines += [f"| {s} | {a} | {b} |" for s, a, b in agr]
        both = [z for z in agr if z[1] > 0]
        eq = sum(1 for z in both if z[1] == z[2])
        lines += ["", f"Equal counts on {eq} of {len(both)} topics where the table resolved >=1 trial.", ""]
    lines += ["## Per topic", "", "| topic | our k | comparator set | theirs (drug-specific) | pooled | missing | classes | closable by |",
              "|---|---|---|---|---|---|---|---|"]
    for x in topics:
        lines.append(f"| {x['slug']} | {x['our_k']} | {x['comparator_set_state']} | {x['drug_specific_resolved']} | "
                     f"{x['pooled_of_theirs']} | {x['missing']} | "
                     f"{', '.join(f'{k} {v}' for k, v in sorted(x['by_class'].items()))} | "
                     f"{', '.join(f'{k} {v}' for k, v in sorted(x['by_source'].items()))} |")
    s = "\n".join(lines) + "\n"
    open(os.path.join(OUT, "SUMMARY.md"), "w", encoding="utf-8").write(s)
    return s


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print(main())
