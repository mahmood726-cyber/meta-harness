"""Concept-discovered eligible family -> study inclusion (DISPATCH_V14_04_FLOW_INCLUSION).

A family that is ELIGIBLE under the protocol (cache/<slug>/families.json, the family reconcile gate) and was found ONLY
by family discovery (concept queries over PubMed / Europe PMC, or the CT.gov cross-link) is not in the pipeline's study
set: records.json is the search cache and is never hand-edited. Such a family's own report enters the study set through
a GENERATED register, cache/<slug>/concept_admissions.json (scripts/build_concept_admissions.py), read here as an overlay
beside the signed comparator records -- and ONLY when every one of these re-verifies at read time:

  * the entry is ADMITTED under a signed item: registry/v14_signatures.json names it SEEN_AND_SIGNED with the
    recorded choice and item-section digest (a served change happens only through a signed item);
  * the family is ELIGIBLE in families.json, the report PMID is one of the family's reports, and the family id is the
    record's NCT;
  * family_discovery.json records the report as found by a concept / cross-link route;
  * the record's abstract is the HELD efetch abstract (outputs/held_abstracts/pubmed_<pmid>.txt) whose sha256 equals both
    the held manifest's and the entry's, and the article itself names the NCT (the manifest's recorded witness).

An entry that is not ADMITTED is listed, never applied. An ADMITTED entry that fails any check raises: a signed
admission that cannot be verified is a broken build, never a silent omission. The pipeline's screen still makes the
include decision on the admitted record -- the overlay only puts the record in front of it.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTER = "concept_admissions.json"
ADMITTED = "ADMITTED"
CONCEPT_ROUTES = ("pubmed_concept_query", "europepmc_concept_query", "pubmed_nct_link")
_RECORD_KEYS = ("id", "id_type", "title", "year", "journal", "doi", "nct", "pubtypes")


class AdmissionRefused(RuntimeError):
    """A signed concept admission that does not re-verify."""


def _load(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def verify_entry(e: dict[str, Any], cache_dir: str, root: str = ROOT) -> dict[str, Any]:
    """The study-set record an ADMITTED entry contributes, every check re-run; AdmissionRefused otherwise."""
    pmid, nct, item = str(e.get("pmid") or ""), str(e.get("nct") or ""), str(e.get("signed_item") or "")
    if not (pmid.isdigit() and re.fullmatch(r"NCT\d{8}", nct) and item):
        raise AdmissionRefused(f"entry lacks a pmid / NCT / signed item: {e.get('pmid')} {e.get('nct')} {item!r}")
    # 1. the signed item
    sig = (_load(os.path.join(root, "registry", "v14_signatures.json")).get("items") or {}).get(item) or {}
    want = e.get("signature") or {}
    # every field present and equal: two MISSING fields are not a match (codex flow-r1#1)
    if not (sig.get("state") == "SEEN_AND_SIGNED" and sig.get("choice") and sig.get("choice") == want.get("choice")
            and re.fullmatch(r"[0-9a-f]{64}", str(sig.get("item_section_sha256") or ""))
            and sig.get("item_section_sha256") == want.get("item_section_sha256")):
        raise AdmissionRefused(f"{pmid}: {item} is not signed as recorded (state {sig.get('state')!r})")
    # 2. the family: ELIGIBLE, the report one of ITS reports, its id the NCT
    fams = _load(os.path.join(cache_dir, "families.json")).get("families") or []
    fam = next((f for f in fams if f.get("family_id") == nct), None)
    if not fam or (fam.get("eligibility") or {}).get("state") != "ELIGIBLE":
        raise AdmissionRefused(f"{pmid}: family {nct} is not ELIGIBLE in families.json")
    if pmid not in {str(r.get("report_id")) for r in fam.get("reports") or []}:
        raise AdmissionRefused(f"{pmid}: not a report of family {nct}")
    # 3. the discovery route
    disc = _load(os.path.join(cache_dir, "family_discovery.json"))
    rec = next((r for r in (disc.get("r3_records") or []) + (disc.get("records") or [])
                if str(r.get("id")) == pmid), None)
    routes = [str(x).split("#")[0] for x in (rec or {}).get("found_by") or []]
    if not rec or not any(r in CONCEPT_ROUTES for r in routes) or str(rec.get("nct") or "") != nct:
        raise AdmissionRefused(f"{pmid}: family_discovery records no concept route to it for {nct}")
    # 4. the held abstract and its trial witness
    name = f"pubmed_{pmid}.txt"
    held = os.path.join(root, "outputs", "held_abstracts", name)
    man = (_load(os.path.join(root, "outputs", "held_abstracts", "manifest.json")).get("documents") or {}).get(name) or {}
    try:
        text = open(held, encoding="utf-8").read()
    except OSError as exc:
        raise AdmissionRefused(f"{pmid}: held abstract unreadable: {exc}") from exc
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if not (sha == man.get("sha256") == e.get("abstract_sha256")):
        raise AdmissionRefused(f"{pmid}: held abstract sha256 {sha[:12]} != manifest / entry")
    # the manifest entry is THIS paper's: its PMID, then its witness naming this trial (codex flow-r1#2)
    if str(man.get("pmid") or "") != pmid:
        raise AdmissionRefused(f"{pmid}: the held manifest entry is for PMID {man.get('pmid')!r}")
    if man.get("nct") != nct or not re.search(r"(?<![0-9A-Za-z])" + re.escape(nct) + r"(?![0-9A-Za-z])",
                                              str(man.get("nct_evidence") or "")):
        raise AdmissionRefused(f"{pmid}: the held article's recorded witness does not name {nct}")
    # ... and the HELD TEXT itself names the trial: a paper binds to a trial on its own evidence, never on manifest
    # metadata alone (agy flow-r2-agy g1#1; FLOW's abstract states 'ClinicalTrials.gov number, NCT03819153')
    if not re.search(r"(?<![0-9A-Za-z])" + re.escape(nct) + r"(?![0-9A-Za-z])", text):
        raise AdmissionRefused(f"{pmid}: the held abstract does not itself name {nct}")
    out = {k: e["record"][k] for k in _RECORD_KEYS if (e.get("record") or {}).get(k) not in (None, "")}
    out.update({"id": pmid, "id_type": "pmid", "nct": nct, "abstract": text,
                "concept_admission": {"register": f"cache/<slug>/{REGISTER}", "signed_item": item,
                                      "routes": rec.get("found_by_routes") or routes, "abstract_sha256": sha}})
    return out


def admitted_records(cache_dir: str, root: str = ROOT) -> list[dict[str, Any]]:
    p = os.path.join(cache_dir, REGISTER)
    if not os.path.exists(p):
        return []
    reg = _load(p)
    entries = reg.get("entries")
    if not isinstance(entries, list):
        raise AdmissionRefused(f"{p}: no 'entries' list")
    return [verify_entry(e, cache_dir, root) for e in entries if e.get("state") == ADMITTED]


def with_concept_admissions(records: dict, cache_dir: str, root: str = ROOT) -> dict:
    """records.json with the admitted reports appended (never one already present); records.json is never rewritten."""
    add = admitted_records(cache_dir, root)
    if not add or not isinstance(records, dict):
        return records
    have = {str(r.get("id")) for r in records.get("records") or []}
    out = dict(records)
    out["records"] = list(records.get("records") or []) + [r for r in add if r["id"] not in have]
    return out
