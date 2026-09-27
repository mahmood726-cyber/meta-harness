"""SOURCE COVERAGE: what exactly was inspected when the page says a result is "not reported".

The DPP-4 review found the committed record for OMNeON (PMID 28893244) is not the abstract: it is an EDITED abridgement
(1,138 of 2,163 characters; sentences shortened, both hospitalisation-for-heart-failure result sentences and the
"or hHF" of the conclusion removed). The page then said HHF was "not found in the abstract", while the verbatim abstract
reports hHF 20/2,092 vs 33/2,100, HR 0.60 (0.35-1.05).

Coverage of an inspected text, against the VERBATIM original held by the acquisition cascade (its bytes, sha256,
source and retrieval time in evidence/acquisition_cascade/held/HELD.json):
  VERBATIM    every sentence of the original is in the inspected text, and nothing else
  EXCERPT     every inspected sentence is a verbatim sentence of the original, but some original sentences are missing
  ALTERED     some inspected sentence is not a verbatim sentence of the original (edited / rewritten)
  UNVERIFIED  no verbatim original is held to compare with
An absence decision names its coverage. EXCERPT and ALTERED texts can never support a publication-level absence
(ABSENCE_ON_EXCERPT blocks); UNVERIFIED is stated as such.
"""
from __future__ import annotations

import glob
import hashlib
import html
import json
import os
import re
from typing import Any

VERBATIM, EXCERPT, ALTERED, UNVERIFIED = "VERBATIM", "EXCERPT", "ALTERED", "UNVERIFIED"
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HELD = os.path.join("evidence", "acquisition_cascade", "held")
# structured-abstract section labels, which a verbatim record renders as headings and a record may render inline
# (longest first, case-insensitive: records render them as 'CONCLUSIONS AND RELEVANCE:' or 'Conclusions and relevance')
_LABELS = re.compile(r"(?:(?<=^)|(?<=[.;:]\s)|(?<=\s))(?:CONCLUSIONS AND RELEVANCE|DESIGN, SETTING, AND PARTICIPANTS|"
                     r"MAIN OUTCOMES AND MEASURES|TRIAL REGISTRATION|AIMS?/HYPOTHESIS|BACKGROUND|METHODS|RESULTS|"
                     r"CONCLUSIONS?|IMPORTANCE|OBJECTIVES?|INTERVENTIONS?|EXPOSURES?|AIMS?)\s*:?\s+(?=[A-Z0-9(])",
                     re.IGNORECASE)


def _plain(s: str) -> str:
    s = re.sub(r"</?[A-Za-z][A-Za-z0-9]*(?:\s[^<>]{0,200})?/?>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def _sentences(s: str) -> list[str]:
    s = _LABELS.sub(" ", _plain(s))
    parts = re.split(r"(?<=[.;])\s+(?=[A-Z(])", s)
    return [re.sub(r"\s+", " ", p).strip().rstrip(".").strip() for p in parts if len(p.strip()) > 3]


def classify(inspected: str, verbatim: str | None) -> str:
    if not verbatim:
        return UNVERIFIED
    orig = _sentences(verbatim)
    got = _sentences(inspected)
    if not got:
        return ALTERED
    orig_set = set(orig)
    if any(g not in orig_set for g in got):
        return ALTERED
    return VERBATIM if set(got) == orig_set else EXCERPT


def verbatim_record(pmid: str, root: str = _ROOT) -> dict[str, Any] | None:
    """The held VERBATIM Europe PMC record for a PMID (abstract text, path, sha256), or None."""
    for p in sorted(glob.glob(os.path.join(root, _HELD, "*", f"europepmc_record_{pmid}.json"))):
        raw = open(p, "rb").read()
        try:
            res = ((json.loads(raw).get("resultList") or {}).get("result") or [{}])[0]
        except ValueError:
            continue
        if res.get("abstractText") and str(res.get("pmid")) == str(pmid):
            return {"text": res["abstractText"], "path": os.path.relpath(p, root).replace(os.sep, "/"),
                    "sha256": hashlib.sha256(raw).hexdigest()}
    return None


def coverage_of(pmid: str, inspected: str, root: str = _ROOT) -> dict[str, Any]:
    v = verbatim_record(pmid, root)
    cov = classify(inspected, v["text"] if v else None)
    out = {"inspected": "the committed record abstract", "coverage": cov}
    if v:
        out.update(verbatim_path=v["path"], verbatim_sha256=v["sha256"])
        orig = set(_sentences(v["text"]))
        out["missing_sentences"] = len(orig - set(_sentences(inspected)))
    return out


def _pmid(x) -> str:
    m = re.search(r"\b(\d{7,8})\b", str(x or ""))
    return m.group(1) if m else ""


def attach(review: dict[str, Any], rec_by_id: dict[str, Any], root: str = _ROOT) -> None:
    """Stamp `source_coverage` on every absent row whose inspected source is a record abstract."""
    for o in review.get("outcomes") or []:
        for row in o.get("declared_absent_trials") or []:
            pid = _pmid(row.get("id"))
            rec = rec_by_id.get(pid) if pid else None
            if rec and rec.get("abstract"):
                row["source_coverage"] = coverage_of(pid, rec["abstract"], root)


def mentions(pmid: str, keywords: list[str], root: str = _ROOT) -> bool:
    """Does the held VERBATIM original name this outcome?"""
    v = verbatim_record(pmid, root)
    t = _plain(v["text"]).lower() if v else ""
    return bool(t) and any(k and k.lower() in t for k in keywords)
