"""PIONEER 6 (oral semaglutide, NCT02692716, PMID 31185157) harm rows for glp1-ra-mace-t2d, 2026-09-27.

Both harm rows were refused with "registry-only values do not meet this lane's GLP-1 level-1-abstract/level-2-FDA
requirement". The protocol states no such requirement: its source hierarchy is 1 publication+supplement, 2 regulatory
review, 3 registry results, 4 HTA, in DESCENDING PRIORITY (5, meta-analyses, pointers only). A lower tier is used when
the higher tiers are silent. Here:
  - Adverse events leading to discontinuation: level 1 (abstract) gives no count; level 2 (the FDA review of oral
    semaglutide) is not held; level 3, the trial's own posted registry results (held), reports the outcome measure
    "Time to First AE Leading to Permanent Trial Product Discontinuation" as a count of participants, FAS:
    184/1591 oral semaglutide vs 104/1592 placebo -> bound (level 3), a served-number change behind an OPEN notice.
  - Gastrointestinal adverse events: the registry gives per-term counts under 'Gastrointestinal disorders' only; terms
    overlap within a participant, so no participant-level aggregate exists at level 3; level 2 not held ->
    REPORTED_UNRESOLVED (the abstract reports it), never refused for a tier the protocol permits.
  PYTHONPATH=. python outputs/handover/glp1_sources/make_pioneer6_rows.py"""
import hashlib, json, os

REG = "evidence/held/registry/NCT02692716.json"
EX = "evidence/acquisition_cascade/excerpts/PIONEER6_registry_AE_leading_to_discontinuation.txt"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

d = json.load(open(REG, encoding="utf-8"))
m = next(m for m in d["resultsSection"]["outcomeMeasuresModule"]["outcomeMeasures"]
         if m["title"] == "Time to First AE Leading to Permanent Trial Product Discontinuation")
assert m["paramType"] == "COUNT_OF_PARTICIPANTS" and m["reportingStatus"] == "POSTED"
g = {x["id"]: x["title"] for x in m["groups"]}
den = {c["groupId"]: int(c["value"]) for c in m["denoms"][0]["counts"]}
val = {x["groupId"]: int(x["value"]) for x in m["classes"][0]["categories"][0]["measurements"]}
assert g == {"OG000": "Oral Semaglutide", "OG001": "Placebo"}
assert (val["OG000"], den["OG000"], val["OG001"], den["OG001"]) == (184, 1591, 104, 1592)
# ONE sentence carries the outcome's name and both arms' counts (the binder reads sentence by sentence: a population
# description ending in '.' between them would leave the counts in a sentence that names no outcome)
SPAN = (f"{m['title']}, count of participants (full analysis set, all randomised): "
        f"Oral Semaglutide {val['OG000']} / {den['OG000']}; Placebo {val['OG001']} / {den['OG001']}.")
assert "all randomised" in m["populationDescription"]
os.makedirs(os.path.dirname(EX), exist_ok=True)
open(EX, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT (field rendering) of the trial's own ClinicalTrials.gov posted results, held verbatim\n"
    f"# source: {REG} (NCT02692716, public domain), sha256 {sha(REG)}\n"
    f"# fields: outcomeMeasures[title={m['title']!r}].groups / denoms / classes\n"
    f"# populationDescription: {m['populationDescription']}\n"
    f"# description: {m['description']}\n\n"
    + SPAN + "\n")

vp = "cache/glp1-ra-mace-t2d/verified_arms.json"
raw = open(vp, encoding="utf-8").read() if os.path.exists(vp) else "{}\n"
va = json.loads(raw)
rows = va.get("31185157")
rows = rows if isinstance(rows, list) else ([rows] if rows else [])
rows = [r for r in rows if r.get("outcome") != "Adverse events leading to discontinuation"]
rows.append({"outcome": "Adverse events leading to discontinuation", "ai": 184, "n1i": 1591, "ci": 104, "n2i": 1592,
             "kind": "extracted_counts", "provenance": "registry_verified_arms", "source_level": 3,
             "document_ref": EX, "document_sha256": sha(EX), "source_span": SPAN, "override": True,
             "timepoint": "on-treatment observation period + 38-day ascertainment window",
             "timepoint_span": "ends on last date on trial product +38 days (ascertainment window)",
             "supersedes": {"provenance": "REFUSED_ON_EVIDENCE", "reason": (
                 "registry-only values do not meet this lane's GLP-1 level-1-abstract/level-2-FDA requirement -- a "
                 "restriction the protocol does not state; its hierarchy is a precedence order, not a prohibition")},
             "reason": ("PIONEER 6 AE leading to permanent trial-product discontinuation, 184/1591 vs 104/1592 (FAS), from "
                        "the trial's own posted registry results (source level 3). Levels 1-2 are silent on the count: the "
                        "abstract gives none and no FDA review of oral semaglutide is held.")})
va["31185157"] = rows
open(vp, "w", encoding="utf-8", newline="\n").write(json.dumps(va, indent=1 if raw.startswith('{\n "') else 2, ensure_ascii=False) + "\n")

GI_SPAN = ("Gastrointestinal adverse events leading to discontinuation of oral semaglutide or placebo were more common "
           "with oral semaglutide.")
rec = next(x for x in json.load(open("cache/glp1-ra-mace-t2d/records.json", encoding="utf-8"))["records"] if str(x["id"]) == "31185157")
assert GI_SPAN in rec["abstract"]
vep = "cache/glp1-ra-mace-t2d/verified_effects.json"
raw_e = open(vep, encoding="utf-8").read()
ve = json.loads(raw_e)
out = []
for r in (ve["31185157"] if isinstance(ve["31185157"], list) else [ve["31185157"]]):
    if r.get("outcome") == "Adverse events leading to discontinuation":
        continue                                   # now bound in verified_arms (level 3)
    if r.get("outcome") == "Gastrointestinal adverse events":
        r = dict(r, provenance="REFUSED_ON_EVIDENCE", reason=(
            "Reported, not resolved: the abstract (level 1) reports more gastrointestinal events leading to "
            "discontinuation with oral semaglutide but gives no count; no FDA review of oral semaglutide is held "
            "(level 2 not yet retrieved); the trial's posted registry results (level 3, held) list per-term counts "
            "under 'Gastrointestinal disorders' only, and terms overlap within a participant, so they cannot be summed "
            "into a participant count. The protocol's hierarchy is a precedence order: a lower tier is used when higher "
            "tiers are silent; here none of the held tiers gives a participant-level aggregate."),
                 reported_unresolved_span=GI_SPAN)
    out.append(r)
ve["31185157"] = out
open(vep, "w", encoding="utf-8", newline="\n").write(json.dumps(ve, indent=1 if raw_e.startswith('{\n "') else 2, ensure_ascii=False) + ("\n" if raw_e.endswith("\n") else ""))
print("PIONEER 6: discontinuation bound (level 3); GI reworded; excerpt", EX)
