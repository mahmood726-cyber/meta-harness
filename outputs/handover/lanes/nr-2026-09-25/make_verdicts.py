"""Lane NR verdicts for judgement B1: codex bulk verdict (raw kept) + the lane's hostile verdict per notice."""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:/mh-lanes/nr/wt")
from scripts import notice_anchor as anchor  # noqa: E402
from scripts import notice_rejudge as rj  # noqa: E402

SERVED, PROPOSED = sys.argv[1], sys.argv[2]
codex = {v["audit_id"]: v for v in json.loads(Path(r"C:/mh-lanes/nr/codex/rejudge-b1/last_message.txt")
                                              .read_text(encoding="utf-8"))["verdicts"]}
checks = {c["audit_id"]: c for c in json.loads(Path(r"C:/mh-lanes/nr/work/packets/checks.json")
                                               .read_text(encoding="utf-8"))["checks"]}
audit = json.loads(rj.AUDIT.read_text(encoding="utf-8"))

NO_PRIOR = ("The rendered block says 'Conclusion withdrawn: the outcome no longer has a pooled estimate', but the "
            "served page had NO pooled estimate before (k = 2 refused, DIRECTION_CONFLICT_K2, confirmed on served "
            "main c9d665e0). Only candidate membership changes; no conclusion existed to withdraw.")
NEW_CLAIM = ("The rendered block says 'The direction of the estimate is unchanged' and has NO 'Conclusion changed' "
             "sentence, but the change creates a NEW claim of a difference: before, the interval was refused "
             "(k = 2, K2_SINGLE_DF); after, {after} excludes 1. Compare N20, where this kind of change is rendered "
             "'Conclusion changed: the interval now excludes the null'. The block understates the change.")
DEFECTS = {
    "N30": NO_PRIOR, "N32": NO_PRIOR, "N39": NO_PRIOR,
    "N06": ("The notice is the ONLY place on the proposed page where 3.74 appears; the outcome section withholds the "
            "number (claim state HARMS_INCOMPLETE: 'No quantitative safety conclusion while source-reporting trials "
            "remain unresolved'). 'A pooled estimate is now served' is true of review.json, but in the HTML the "
            "notice itself publishes a harm estimate (RR 3.74, no interval) that the page otherwise refuses to state."),
    "N27": ("The notice is the ONLY place on the proposed page where RR 1.23 (0.98 to 1.54) appears for this outcome "
            "(the outcome section withholds it: HARMS_INCOMPLETE). The number appears with NO membership change "
            "(PMID 30146932 is the sole member before and after), and the ledger's 'why' is only the generic P5 "
            "mechanism sentence, which explains nothing here (already recorded at ceb6d8e as a generator defect). "
            "The notice does not state what produced this result."),
    "N28": NEW_CLAIM.format(after="HR 0.85 (0.78 to 0.93)"),
    "N38": NEW_CLAIM.format(after="HR 0.70 (0.61 to 0.82)"),
    "N17": ("The rendered block says 'The direction of the estimate is unchanged', but the point moves from HR 1.0074 "
            "(above the null) to exactly 1.00 (on the null), and the page's own claim direction changes from harm "
            "to none. Minor, but the sentence is not true."),
}
SEE_N01 = "See N01's note: a point estimate was served with its interval refused."
NOTES = {
    "N25": ("Hostile note: all four trials leave for INTERVENTION_CONTRAST_NOT_PROVEN on held registry evidence, so "
            "NOAC vs warfarin for stroke then serves NO pooled estimate. The audit groups this in G1 "
            "(COUNTERSIGN_AS_IS); the lane recommends reading it individually. The transition is exact; the "
            "clinical consequence is large."),
    "N29": ("Hostile note: 11 of 11 trials leave (9 REGISTRY_PARENT_UNRESOLVED, several pre-dating trial registries), "
            "withdrawing RR 0.69 (0.48 to 0.98). Exact, but read it individually despite G1."),
    "N13": "Hostile note: 6 of 6 trials leave; HR 0.91 (0.75 to 1.11) is withdrawn. Exact.",
    "N37": ("Hostile note: RALES (PMID 10471456, RR 0.70, 0.60 to 0.82) leaves on REGISTRY_PARENT_UNRESOLVED (a 1999 "
            "trial with no registry parent). EMPHASIS-HF (eplerenone, PMID 21073363) leaves as INELIGIBLE, with the "
            "held-source conflict the audit records (its registry id resolves to a NON_RANDOMIZED single-group "
            "record). The page then withdraws the mortality benefit on ONE remaining trial with an unbound (legacy) "
            "endpoint. The before pool also mixed an RR (RALES) into an HR synthesis. Exact, but a clinically heavy "
            "withdrawal; D01 (the RR correction for EMPHASIS-HF) is related and pending."),
    "N20": ("Hostile note: a newly significant benefit (MD -4.4, -8.03 to -0.77) from ONE remaining trial whose "
            "admission is MIGRATION_STATE_UNBOUND_LEGACY, reversing an earlier signed withdrawal. The block states "
            "the conclusion change correctly."),
    "N23": ("Hostile note: a new claim, HR 0.39 (0.19 to 0.82), from ONE trial (PMID 25176939) after the only other "
            "trial leaves on INTERVENTION_CONTRAST_NOT_PROVEN. The block says so correctly."),
    "N01": ("Lane note (applies alike to N15, N16, N40): the before served a point estimate with its interval refused, "
            "so 'Conclusion withdrawn' is strong wording for a point that never carried a claim. The clause after "
            "the colon ('no longer has a pooled estimate') is true. Not marked as a defect."),
    "N15": SEE_N01, "N16": SEE_N01,
    "N40": SEE_N01 + " A harm-side bleeding point (HR 1.17) disappears; disappearance is not evidence of safety.",
    "N02": "Retained trials are MIGRATION_STATE_UNBOUND_LEGACY; the interval is lost at k = 2.",
    "N03": "Retained trials are MIGRATION_STATE_UNBOUND_LEGACY; the interval is lost at k = 2.",
}
REFUTED = {"N30": ("Codex concern 'the DIRECTION_CONFLICT_K2 explanation is not established by the result object' is "
                   "refuted: the served page (main c9d665e0) states DIRECTION_CONFLICT_K2 for this outcome in its "
                   "earlier signed notice (ledger chain index 9 -> 42).")}

out = []
for row in audit["notices"]:
    aid = row["audit_id"]
    c, k = codex[aid], checks[aid]
    anchors = rj.anchors_for(row, SERVED, PROPOSED)
    if aid in audit.get("specific_conflicts", {}):
        anchors.append(anchor.make(rj.ROOT, "held", PROPOSED, audit["specific_conflicts"][aid]["cache_path"]))
    facts = all(c[f] for f in ("before_matches_served", "after_matches_proposed", "left_pool_exact",
                               "entered_pool_exact", "departing_reasons_ok")) and c["direction_matches_audit"]
    if c["verdict"] == "HOLDS":
        bulk = "HOLDS"
    elif facts and not c["block_text_consistent"]:
        bulk = "HOLDS_WITH_DEFECT"  # DIFFERS on rendered wording only; facts 1-5 and direction all agreed
    else:
        bulk = "DIFFERS"
    notes = NOTES.get(aid, "")
    if aid in REFUTED:
        notes = (notes + " " if notes else "") + REFUTED[aid]
    out.append({"audit_id": aid, "anchors": {a["ref"]: a["sha256"] for a in anchors},
                "bulk_reader": "Codex GPT-6, call NR-C01-rejudge-b1 (read-only sandbox; packets built from pinned bytes)",
                "bulk_verdict_raw": c["verdict"], "bulk_reasons_raw": c["reasons"], "bulk_verdict": bulk,
                "bulk_concerns": c["concerns"],
                "lane_verdict": "HOLDS_WITH_DEFECT" if aid in DEFECTS else "HOLDS",
                "defects": [DEFECTS[aid]] if aid in DEFECTS else [], "lane_notes": notes,
                "before_after": c["before_after"], "rendered_block_sha256": k["rendered_block_sha256"]})
Path(r"C:/mh-lanes/nr/work/verdicts_b1.json").write_text(
    json.dumps({"served": SERVED, "proposed": PROPOSED, "verdicts": out}, ensure_ascii=False, indent=1) + "\n",
    encoding="utf-8")
print(collections.Counter((v["bulk_verdict_raw"], v["bulk_verdict"], v["lane_verdict"]) for v in out))
