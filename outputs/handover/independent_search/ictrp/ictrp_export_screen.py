"""WHO ICTRP concept-search export for glp1-ra-mace-t2d: source record, per-record screening with rule ids, funnel, four
states, and the sentinel (rediscovery of the held families by a query that names no trial + a negative control).

Executed query (browser-driven, portal https://trialsearch.who.int/AdvSearch.aspx, no machine API exists):
  condition = "type 2 diabetes"  AND  intervention = "liraglutide OR semaglutide OR dulaglutide OR albiglutide OR
  efpeglenatide OR exenatide OR lixisenatide", recruitment status = ALL, synonyms ON (portal default), no other filter.
No trial name, acronym or identifier was entered: this is a concept query, not a look-up of trials already held.

Usage: python ictrp_export_screen.py <export.xml> <families.json of the topic> <families.json of a control topic> <out.json>
Every decision names its rule id; a record that no rule can decide is UNRESOLVED (fail-closed), never excluded.
"""
import hashlib
import io
import json
import re
import sys
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

AGENTS = ("liraglutide", "semaglutide", "dulaglutide", "albiglutide", "efpeglenatide", "exenatide", "lixisenatide")
QUERY = {
    "portal": "https://trialsearch.who.int/AdvSearch.aspx",
    "condition": "type 2 diabetes",
    "intervention": "liraglutide OR semaglutide OR dulaglutide OR albiglutide OR efpeglenatide OR exenatide OR lixisenatide",
    "recruitment_status": "ALL",
    "synonyms": "portal default (on); 'Without synonyms' boxes unchecked",
    "other_filters": "none (title blank, sponsor blank, countries all, dates all, phases all, results-only off)",
    "trial_names_or_identifiers_entered": "none",
}
RETRIEVAL = {
    "search_executed_utc": "2026-09-18T05:48Z (results page: '1779 records for 1062 trials found', read before export)",
    "terms_accepted_utc": "2026-09-18T06:03:41.062Z",
    "export_all_trials_clicked_utc": "2026-09-18T06:04:36.735Z",
    "export_date_stamped_by_portal": "09/18/2026 06:04:38 (Export_date element, portal clock)",
    "retrieved_utc": "2026-09-18T06:04:36Z",
    "retrieved_utc_precision": "instant",
    "retrieval_mode": "browser-driven export (WebForms postback 'Export all trials to XML'); bytes saved by the browser and copied unchanged",
}
ATTRIBUTION = {
    "attribution_required": True,
    "attribution_text": "Data obtained from the WHO International Clinical Trials Registry Platform (WHO ICTRP), export of 18 September 2026; "
                        "WHO ICTRP must be credited as the source in any publication or distribution of these data.",
    "terms": "Terms and Conditions for Use of WHO ICTRP Data (accepted in the portal 2026-09-18T06:03:41Z, authorised by Mahmood): "
             "publicly available at no charge; no warranties; in any publication or distribution attribute the source as WHO ICTRP; "
             "trial data are not endorsed by WHO.",
}


def text(t, tag):
    return " ".join((t.findtext(tag) or "").split())


def rules(t):
    """Per-record decision. Eligibility on P/I/C/design only; the MACE outcome is recorded, never used to exclude."""
    interv = text(t, "Intervention").lower()
    cond = text(t, "Condition").lower()
    design = text(t, "Study_design").lower()
    stype = text(t, "Study_type").lower()
    title = (text(t, "Public_title") + " " + text(t, "Scientific_title")).lower()
    outcomes = (text(t, "Primary_outcome") + " " + text(t, "Secondary_outcome")).lower()
    agents = sorted({a for a in AGENTS if a in interv or a in title})
    d = {"trial_id": text(t, "TrialID"), "register": text(t, "Source_Register"), "agents_named": agents}
    # R1 intervention: one of the seven agents named in the intervention/title text of the registry record
    if not agents:
        d.update(decision="RETRIEVED_REFUSED", rule="ICTRP-R1-INTERVENTION",
                 reason="none of the seven prespecified agents named in Intervention/title (portal synonym expansion retrieved it)")
        return d
    # R2 design: randomised, interventional
    if "interventional" not in stype and "interventional" not in design:
        d.update(decision="UNRESOLVED", rule="ICTRP-R2-DESIGN", reason=f"study type not stated interventional (Study_type={stype[:40]!r})")
        return d
    if "randomi" not in design and "randomi" not in title:
        d.update(decision="UNRESOLVED", rule="ICTRP-R2-DESIGN", reason="allocation not stated randomised in registry text")
        return d
    # R3 comparator: placebo named
    if "placebo" not in interv and "placebo" not in title and "placebo" not in design:
        d.update(decision="UNRESOLVED", rule="ICTRP-R3-COMPARATOR", reason="placebo comparator not stated in registry text")
        return d
    # R4 population: type 2 diabetes named (the portal condition filter used synonyms; confirm on the record)
    if not re.search(r"type 2|type ii|t2d|niddm|non-insulin", cond + " " + title):
        d.update(decision="UNRESOLVED", rule="ICTRP-R4-POPULATION", reason="type 2 diabetes not stated on the record")
        return d
    d.update(decision="CANDIDATE_FAMILY", rule="ICTRP-R1..R4", reason="agent + interventional randomised + placebo + T2D stated")
    # target-result status, recorded SEPARATELY (never an eligibility axis)
    d["mace_in_registry_outcome_text"] = bool(re.search(r"cardiovascular death|major adverse cardiovascular|mace|myocardial infarction|stroke", outcomes))
    return d


def main(export, families, control, out, registry_rows=None):
    raw = open(export, "rb").read()
    root = ET.fromstring(raw)
    trials = root.findall("Trial")
    decisions = [rules(t) for t in trials]
    ids = {d["trial_id"] for d in decisions}
    fam = json.load(open(families, encoding="utf-8"))["families"]
    held = {f["family_id"]: (f["aliases"].get("acronym") or [f["family_id"]])[0] for f in fam
            if any(r["role"] == "PRIMARY" for r in f["reports"])}
    ctrl = json.load(open(control, encoding="utf-8"))["families"]
    negatives = {f["family_id"]: (f["aliases"].get("acronym") or [""])[0] for f in ctrl if (f["aliases"].get("acronym") or [""])[0] == "SELECT"}
    secondary = {}
    for t in trials:
        for s in re.findall(r"NCT\d{8}", text(t, "Secondary_ID")):
            secondary.setdefault(s, []).append(text(t, "TrialID"))
    # family-level linkage through HELD secondary identifiers (AACT id_information rows, each with its row sha256):
    # an ICTRP record of another registry (EUCTR, NL-OMON, PER, CTRI...) belongs to a held family when its TrialID or
    # any token of its Secondary_ID equals the family's NCT or one of that NCT's held secondary ids (EudraCT number,
    # sponsor study code). ICTRP does not surface every NCT record by search (measured 2026-09-18: NCT02465515 and
    # NCT03496298 are in ICTRP but not retrieved by their agent terms, while their EUCTR siblings are).
    held_secondary = {}
    if registry_rows:
        import gzip
        for row in json.load(gzip.open(registry_rows, "rt", encoding="utf-8")):
            if row.get("table") == "id_information" and row.get("nct_id") in held:
                v = (row.get("inline") or {}).get("id_value") or ""
                if len(v) >= 5:
                    held_secondary.setdefault(row["nct_id"], set()).add(v)
    def tokens(t):
        return set(re.split(r"[;,\s]+", tx_secondary(t))) | {text(t, "TrialID")}
    def tx_secondary(t):
        return text(t, "Secondary_ID")
    linked = {fid: [] for fid in held}
    for t in trials:
        tid = text(t, "TrialID"); toks = tokens(t)
        for fid in held:
            keys = {fid} | held_secondary.get(fid, set())
            if tid == fid or any(k in toks or (k and k in tid) for k in keys):
                linked[fid].append(tid)
    found = {fid: (fid in ids, sorted(set(secondary.get(fid, [])) | set(linked[fid]) - {fid})) for fid in held}
    n_found = sum(1 for fid, v in found.items() if (v[0] or v[1]) and fid not in negatives)
    positives = [fid for fid in held if fid not in negatives]
    funnel = {"records_reported_by_portal": 1779, "trials_exported": len(trials), "unique_trial_ids": len(ids)}
    for k in ("RETRIEVED_REFUSED", "UNRESOLVED", "CANDIDATE_FAMILY"):
        funnel[k] = sum(1 for d in decisions if d["decision"] == k)
    funnel["by_rule"] = {}
    for d in decisions:
        funnel["by_rule"][d["rule"]] = funnel["by_rule"].get(d["rule"], 0) + 1
    record = {
        "source_id": "ictrp_concept_query#1",
        "kind": "ICTRP_CONCEPT_QUERY",
        "entered_via": "executed query",
        "topic": "glp1-ra-mace-t2d",
        "query": QUERY,
        "retrieval": RETRIEVAL,
        "document_path": "outputs/handover/independent_search/ictrp/ictrp_export_2026-09-18.xml",
        "document_sha256": hashlib.sha256(raw).hexdigest(),
        "document_bytes": len(raw),
        "state": "RAN_OK" if trials else "RAN_ZERO",
        "state_note": "RAN_ERROR would carry the portal error text; none occurred. A zero here would be RAN_ZERO, never RAN_OK.",
        "funnel": funnel,
        "attribution": ATTRIBUTION,
        "sentinel": {
            "rule": "every PRIMARY family held by the harness for this topic must be rediscovered by the concept query that names none of them, "
                    "directly (its registry id among the exported TrialIDs) or via an exported record's Secondary_ID; "
                    "and the negative control (SELECT: semaglutide in obesity WITHOUT diabetes, held under semaglutide-obesity-mace) must NOT be retrieved "
                    "-- if it is, the condition filter did not do what the query says",
            "held_families": {fid: {"acronym": acr, "direct": found[fid][0], "via_secondary_id_of": found[fid][1]} for fid, acr in held.items()},
            "positives": positives,
            "held_secondary_ids_used": {k: sorted(v) for k, v in held_secondary.items()},
            "rediscovered": f"{n_found} of {len(positives)}",
            "missed": [fid for fid in positives if not (found[fid][0] or found[fid][1])],
            "negative_control": {fid: {"acronym": acr, "retrieved": fid in ids, "via_secondary_id_of": secondary.get(fid, [])} for fid, acr in negatives.items()},
        },
        "decisions": decisions,
    }
    json.dump(record, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps({k: record[k] for k in ("document_sha256", "state", "funnel")}, indent=1))
    print("sentinel rediscovered", record["sentinel"]["rediscovered"])
    for fid, v in record["sentinel"]["held_families"].items():
        print(f"  {fid} {v['acronym']:14s} direct={v['direct']} secondary={v['via_secondary_id_of']}")
    print("negative control", record["sentinel"]["negative_control"])


if __name__ == "__main__":
    main(*sys.argv[1:6])
