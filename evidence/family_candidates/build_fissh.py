"""FISSH (Fluids in Sepsis and Septic Shock; PMID 28729329, NCT02748382) as a CANDIDATE record for the
balanced-crystalloids topic's family-linking workflow: linked, screened and decided -- NEVER pooled, and not added to
the topic's records.json (so no served number can move). V1.0.1, from an external review of the topic.

Inputs, all held and hash-checked:
  * both reports as the committed search_v2 snapshot parsed them (cache/<slug>/snapshots/2026-09-15r3-search_v2/
    records.json, read at the committed blob: snapshot bodies are excluded from some checkouts);
  * the ClinicalTrials.gov v2 record, fetched 2026-09-26 and held at evidence/held/registry/NCT02748382.json.
The family node comes from the workflow itself (harness.trial_family.families); its structural P/I/C/design screen
(screen_family) is recorded as it returns. Because it ABSTAINS (no AACT arm/population rows are held for this trial),
the decision is adjudicated against the topic's registered protocol rules (I1/I2/I3, X1/X2/X3), each with a located
span in the evidence lane's one text representation (evidence/scripts/textrep.py) or a JSON pointer into the held
registry file for fields the representation does not render.
usage: python evidence/family_candidates/build_fissh.py [--check]"""
import hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [ROOT, os.path.join(ROOT, "evidence", "scripts")]
from harness import trial_family  # noqa: E402
import textrep  # noqa: E402

SLUG = "balanced-crystalloids-vs-saline-mortality"
SNAP = f"cache/{SLUG}/snapshots/2026-09-15r3-search_v2/records.json"
REG = "evidence/held/registry/NCT02748382.json"
PROTOCOL = f"protocols/{SLUG}.md"
OUT = os.path.join(HERE, SLUG, "NCT02748382_FISSH.json")
IDS = ("28729329", "NCT02748382")


def _blob(path):
    """Committed bytes of a tracked file (the snapshot is excluded from sparse checkouts)."""
    return subprocess.run(["git", "-C", ROOT, "show", f"HEAD:{path}"], capture_output=True, check=True).stdout


def _span(ref, text, quote):
    i = text.find(quote)
    if i < 0 or text.find(quote, i + 1) >= 0:
        raise ValueError(f"{ref}: quote absent or not unique: {quote[:70]!r}")
    return {"document_ref": ref, "start": i, "end": i + len(quote), "quote": quote}


def _pointer(doc, ref, sha, pointer):
    cur = doc
    for part in pointer.strip("/").split("/"):
        cur = cur[int(part)] if isinstance(cur, list) else cur[part]
    return {"document_ref": ref, "document_sha256": sha, "json_pointer": pointer, "value": cur}


def build():
    snap_raw = _blob(SNAP)
    snap = json.loads(snap_raw)
    recs = [r for r in snap["records"] if str(r.get("id")) in IDS]
    if sorted(str(r["id"]) for r in recs) != sorted(IDS):
        raise ValueError("FISSH reports not both present in the committed snapshot")
    reg_raw = open(os.path.join(ROOT, REG), "rb").read()
    reg_sha = hashlib.sha256(reg_raw).hexdigest()
    reg = json.loads(reg_raw)
    rt = textrep.render(REG)
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    proto = open(os.path.join(ROOT, PROTOCOL), encoding="utf-8").read()

    nodes = trial_family.families(recs, config=cfg)
    if len(nodes) != 1:
        raise ValueError(f"family workflow produced {len(nodes)} families for FISSH (expected 1)")
    node = nodes[0]
    structural = trial_family.screen_family(node, cfg)

    pm = next(r for r in recs if r["id"] == "28729329")
    ev = {
        "I1_randomised": _span(REG, rt, "DESIGN: allocation RANDOMIZED | model PARALLEL | masking QUADRUPLE"),
        "I2_population": [_span(REG, rt, "CONDITION: Sepsis"), _span(REG, rt, "CONDITION: Septic Shock"),
                          {"document_ref": SNAP + "#28729329", "quote": "We will include adult critically ill patients with septic shock",
                           "in_abstract": "We will include adult critically ill patients with septic shock" in pm["abstract"]}],
        "I3_balanced_vs_saline": [
            _span(REG, rt, "lower chloride crystalloid (Ringer's lactate)"),
            _span(REG, rt, "higher chloride crystalloid (Normal saline)")],
        "co_randomised_albumin": [
            _span(REG, rt, "lower chloride albumin (5% Plasbumin)"),
            _span(REG, rt, "higher chloride albumin (5% Octalbin)")],
        "entry_age": _span(REG, rt, "minimum age 16 Years"),
        "status": _pointer(reg, REG, reg_sha, "/protocolSection/statusModule/overallStatus"),
        "completion": _pointer(reg, REG, reg_sha, "/protocolSection/statusModule/completionDateStruct/date"),
        "enrollment": _pointer(reg, REG, reg_sha, "/protocolSection/designModule/enrollmentInfo/count"),
        "results_posted": _pointer(reg, REG, reg_sha, "/hasResults"),
        "registered_mortality_outcome": next(
            _pointer(reg, REG, reg_sha, f"/protocolSection/outcomesModule/secondaryOutcomes/{i}/measure")
            for i, o in enumerate(reg["protocolSection"]["outcomesModule"]["secondaryOutcomes"])
            if "mortality" in o["measure"].lower()),
        "report_role": {"report_id": "28729329", "role": [r["role"] for r in node["reports"] if r["report_id"] == "28729329"][0],
                        "title": pm["title"]},
    }
    if ev["results_posted"]["value"] is not False or ev["status"]["value"] != "COMPLETED":
        raise ValueError("registry state changed: re-adjudicate FISSH")
    rules = {k: _span(PROTOCOL, proto, q) for k, q in (
        ("I1", "**I1** - randomised trial;"),
        ("I2", "**I2** - population is critically ill adults, ICU patients, adult sepsis patients, or adult trauma "
               "resuscitation patients, judged from title or registry conditions;"),
        ("I3", "**I3** - balanced/buffered crystalloid solution vs 0.9% saline / normal saline / sodium chloride;"),
        ("X1", "**X1** - not a randomised trial (review, guideline, observational study, protocol-only when not a trial "
               "results record);"),
        ("X3", "**X3** - wrong intervention/comparison (no balanced-crystalloid-vs-saline contrast);"),
        ("outcome_axis", "**Eligibility is NOT on the outcome axis.**"))}
    return {
        "object": "FAMILY_CANDIDATE", "topic": SLUG, "family_id": node["family_id"], "acronym": "FISSH",
        "made_utc": "2026-09-26", "by": "Claude Opus 5.5, lane evid2 (V1.0.1 branch evid2/v101-overlap)",
        "pooled": False, "in_topic_records": False,
        "why_candidate_only": "external review asked for FISSH to be linked as a candidate record only, with no pooling",
        "inputs": {"snapshot": {"ref": SNAP, "sha256": hashlib.sha256(snap_raw).hexdigest()},
                   "registry": {"ref": REG, "sha256": reg_sha, "fetched_utc": "2026-09-26",
                                "url": "https://clinicaltrials.gov/api/v2/studies/NCT02748382"},
                   "results_search": {"pubmed_query": "FISSH[tiab] OR NCT02748382[si] OR NCT02748382[tiab]",
                                      "run_utc": "2026-09-26", "hits": ["28729329", "8039423", "1427876"],
                                      "note": "28729329 is the FISSH protocol; 8039423 (1994) and 1427876 (1992) are "
                                              "unrelated genetics papers matching the string 'FISSH'"}},
        "family_node": {k: node[k] for k in ("family_id", "is_trial_family", "identity_basis", "aliases", "reports")},
        "structural_screen": {"result": structural,
                              "why": "screen_family abstains: no held AACT design/arm/population rows for this trial, "
                                     "so it cannot prove P/I/C/design from structured registry data"},
        "adjudication": {
            "rules": rules,
            "I1": {"met": True, "evidence": ev["I1_randomised"]},
            "I2": {"met": True, "evidence": ev["I2_population"],
                   "caveat": "registry entry age is 16 years (the protocol paper says adults); I2 is judged from the "
                             "registry conditions and title per the protocol", "entry_age": ev["entry_age"]},
            "I3": {"met": True, "evidence": ev["I3_balanced_vs_saline"],
                   "note": "lactated Ringer's is on the topic's own intervention list; normal saline is the comparator",
                   "caveat": "both arms also receive albumin, and the albumin product differs (5% Plasbumin vs 5% "
                             "Octalbin): the randomised contrast is a low- vs high-chloride fluid STRATEGY whose "
                             "crystalloid component is balanced vs saline", "co_intervention": ev["co_randomised_albumin"]},
            "X1": {"applies_to_family": False,
                   "note": "X1's protocol-only exclusion applies to the RECORD 28729329 (role "
                           + ev["report_role"]["role"] + "), not to the trial family; the family is a completed RCT"},
            "X3": {"true_of_record": False, "why": "the registry names a balanced crystalloid vs 0.9% saline contrast"},
        },
        "decision": {
            "eligibility": "ELIGIBLE (P/I/C/design: I1, I2, I3 met; no exclusion true of the family)",
            "target_result_status": "RESULT_NOT_AVAILABLE",
            "target_result_evidence": [ev["status"], ev["completion"], ev["enrollment"], ev["results_posted"],
                                       ev["registered_mortality_outcome"]],
            "target_result_note": ("completed 2017, 50 randomised, hospital mortality a registered secondary outcome; "
                                   "no results posted and no results report found -- per the protocol this is a "
                                   "target-result status, never an exclusion"),
            "pooled": False,
            "if_served": ("would be listed as an eligible family with RESULT_NOT_AVAILABLE for Mortality (known missing), "
                          "contributing no number; serving it is a separate decision"),
        },
    }


def main(check=False):
    text = json.dumps(build(), indent=1, ensure_ascii=False) + "\n"
    if check:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else None
        print("current" if cur == text else "STALE")
        return 0 if cur == text else 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8", newline="\n").write(text)
    print("written", os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
