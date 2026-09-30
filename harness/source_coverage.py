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
import subprocess
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


# Words that make up structured-abstract HEADINGS. A difference consisting only of these (a heading rendered, dropped,
# re-cased or glued to the next sentence) is not an alteration. Anything else -- a number, a content word -- is.
_HEADING_WORDS = frozenset("""background backgrounds introduction context objective objectives aim aims purpose purposes
hypothesis rationale importance method methods materials design designs setting settings participant participants patient
patients subject subjects study studies intervention interventions exposure exposures main primary secondary outcome
outcomes measure measures measurement measurements result results finding findings conclusion conclusions relevance
interpretation discussion summary significance trial registration funding clinical evidence level data sources selection
extraction synthesis limitations unlabelled and of or in the""".split())


def _words(s: str) -> list[str]:
    s = _plain(s).replace("−", "-").replace("·", ".")
    return re.findall(r"[a-z]+|\d+(?:[.,/]\d+)*|[^\sa-z\d]", s.lower())


_ENDS = frozenset(".;:")


def _diff(inspected: str, verbatim: str):
    """Word-level difference of an inspected text against the verbatim original: (inserted, cut_within, missing).
    inserted:   runs in the inspected text that the original does not have (an edit, a changed number);
    cut_within: runs of the original removed from INSIDE a sentence the inspected text keeps ('or hHF' dropped);
    missing:    whole sentences of the original that the inspected text omits.
    Runs made only of heading words and punctuation are ignored."""
    import difflib
    a, b = _words(verbatim), _words(inspected)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ins, cut, miss = [], [], []
    content = lambda ws: [w for w in ws if w not in _HEADING_WORDS and re.match(r"[a-z\d]", w)]
    skip = lambda w: w not in _ENDS and (w in _HEADING_WORDS or not re.match(r"[a-z\d]", w))

    def whole_sentences(i1, i2):
        lo, hi = i1, i2
        while lo > 0 and skip(a[lo - 1]):
            lo -= 1
        while hi > lo and skip(a[hi - 1]):
            hi -= 1
        start_ok = lo == 0 or a[lo - 1] in _ENDS
        end_ok = hi == len(a) or a[hi - 1] in _ENDS or all(skip(w) or w in _ENDS for w in a[hi:])
        return start_ok and end_ok

    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        if op == "replace" and "".join(a[i1:i2]) == "".join(b[j1:j2]):
            continue      # same characters, different spacing: a flattened superscript (10<sup>8</sup> -> 108), a tag seam
        if content(b[j1:j2]):
            ins.append(" ".join(b[j1:j2]))
        if content(a[i1:i2]):
            (miss if whole_sentences(i1, i2) else cut).append(" ".join(a[i1:i2]))
    return ins, cut, miss


def classify(inspected: str, verbatim: str | None) -> str:
    """Word-level comparison (not sentence matching: that depends on parsing headings, and graded 99 of 211 real
    records ALTERED for heading artefacts). ALTERED: words added or changed, or words cut from inside a kept sentence.
    EXCERPT: only whole sentences of the original missing. VERBATIM: neither."""
    if not verbatim:
        return UNVERIFIED
    if not _words(inspected):
        return ALTERED
    ins, cut, miss = _diff(inspected, verbatim)
    if ins or cut:
        return ALTERED
    return EXCERPT if miss else VERBATIM


def verbatim_record(pmid: str, root: str = _ROOT) -> dict[str, Any] | None:
    """The git-tracked VERBATIM Europe PMC record, never a local acquisition.

    HELD.json is an acquisition ledger, not a redistribution allowlist: it also
    names records absent from the repository. Git is already a build dependency
    (registration.py). Read the index without refreshing or modifying it.
    """
    try:
        tracked = set(subprocess.check_output(
            ["git", "--no-optional-locks", "-C", os.fspath(root),
             "ls-files", "--cached", "--full-name", "-z", "--", _HELD.replace(os.sep, "/") + "/"],
            stderr=subprocess.PIPE,
        ).decode("utf-8").split("\0"))
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        raise ValueError(f"SOURCE_COVERAGE refused PMID {pmid}: cannot establish tracked held files") from exc
    for p in sorted(glob.glob(os.path.join(root, _HELD, "*", f"europepmc_record_{pmid}.json"))):
        relative = os.path.relpath(p, root).replace(os.sep, "/")
        if relative not in tracked:
            continue  # Refuse untracked witnesses; coverage_of names the PMID's row UNVERIFIED if none remain.
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
        ins, cut, miss = _diff(inspected, v["text"])
        # NAMED, not only counted: what the inspected text lacks, and what it has that the original does not
        out["missing_text"] = [m[:300] for m in miss + cut]
        out["inserted_text"] = [m[:300] for m in ins]
        out["missing_sentences"] = len(miss) + len(cut)
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
