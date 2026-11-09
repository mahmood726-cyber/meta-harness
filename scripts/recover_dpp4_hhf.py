"""Recover the hHF effect from the hash-verified retained PubMed acquisition.

No source text is sent to a model and no research number is entered manually.
Read-only diagnostic. The pipeline routes the retained source to its normal extractor.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import extract
from harness.source_coverage import coverage_for

SLUG = "dpp4-mace-t2d"
PMID = "28893244"


def recover():
    config = json.loads((ROOT / "topics" / f"{SLUG}.json").read_text(encoding="utf-8"))
    spec = next(s for s in config["harm_outcomes"] if s["name"] == "Hospitalization for heart failure")
    coverage = coverage_for(SLUG, PMID)
    ref = coverage["complete_abstract_ref"]
    raw = (ROOT / ref["path"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ref["sha256"]
    article = ET.fromstring(raw)
    assert article.findtext(".//MedlineCitation/PMID") == PMID
    text = coverage["complete_abstract_text"]
    candidates = [(s, extract.extract_effect(s)) for s in extract._outcome_sentences(text, spec["keywords"])]
    candidates = [(s, e) for s, e in candidates if e is not None]
    assert len(candidates) == 1, "Ambiguous or missing hHF effect"
    span, effect = candidates[0]
    assert span in raw.decode("utf-8"), "Evidence must be a verbatim retained span"
    assert effect.scale == spec["estimand"]
    trial = extract.extract_trial(text, spec["keywords"], config["intervention_terms"],
                                  config["comparator_terms"], estimand=spec["estimand"])
    values = dict(scale=effect.scale, effect=effect.point, ci_low=effect.lo, ci_high=effect.hi)
    assert all(trial[k] == v for k, v in values.items())
    return {**values, "outcome": spec["name"], "source_span": span,
            "source": "Deterministic extraction from retained PubMed abstract: " + span,
            "document_ref": ref["path"], "document_sha256": ref["sha256"],
            "source_level": 1, "kind": "extracted_effect", "provenance": "abstract_verified",
            "verification": "scripts/recover_dpp4_hhf.py: source identity and SHA-256 checked; "
                            "unique keyword/defined-alias effect agrees with extract_trial"}


def main():
    print(json.dumps(recover(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
