"""Topic/outcome-local routing of retained PubMed bytes to the normal extractor.

The coverage registry pins the acquisition; no effect values are stored here.
"""
import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET

from .source_coverage import coverage_for

ROOT = Path(__file__).resolve().parents[1]
SLUG = "dpp4-mace-t2d"
PMID = "28893244"
OUTCOME = "Hospitalization for heart failure"


def route_records(slug, outcome, records, root=ROOT):
    if slug != SLUG or outcome != OUTCOME or PMID not in records:
        return records
    coverage = coverage_for(SLUG, PMID)
    ref = coverage.get("complete_abstract_ref")
    if not ref:
        raise ValueError("dpp4 retained abstract unavailable or SHA-256 mismatch")
    raw = (Path(root) / ref["path"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != ref["sha256"]:
        raise ValueError("dpp4 retained abstract SHA-256 mismatch")
    article = ET.fromstring(raw)
    if article.findtext(".//MedlineCitation/PMID") != PMID:
        raise ValueError("dpp4 retained abstract PMID mismatch")
    units = article.findall(".//Abstract/AbstractText")
    text = " ".join((u.get("Label", "") + ": " if u.get("Label") else "")
                    + "".join(u.itertext()).strip() for u in units).strip()
    if not text:
        raise ValueError("dpp4 retained abstract empty")
    return {**records, PMID: {**records[PMID], "abstract": text, "retained_abstract_ref": ref}}
