"""A recorded model call stores its PROMPT (base64) in a committed, public record. A prompt may therefore carry text
only from a source MARKED OPEN: outputs/k_gap/fulltext_index.json `copy_licence == "CC"` for that PMID (written by
scripts/g1_trial_acquire.pmc_copy from the PMC permissions). Anything else -- an NIH author manuscript ('available for
text mining ... fair use'), an unknown licence, no index entry -- is NOT marked open, and the record is refused.

Incident (5 Oct): mc-dcb6796c carried SMART's full text (PMC5846085, an author manuscript), 24,886 bytes, into the
public repo. tests/test_record_licence.py runs this over every tracked record (the unit-test limb of verify_all, the
pre-commit hook and CI), with a plant.

How a prompt's source text is found (both, so a new prompt shape cannot slip past):
  structural  the acquisition evidence block: an object with a "pmid" and a "text" longer than MIN_TEXT characters
  declared    an input digest whose ref names a PMID and a full text ('PMID 123 record + PMC OA full text ...')
"""
from __future__ import annotations

import base64
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "outputs", "k_gap", "fulltext_index.json")
OPEN = ("CC",)
MIN_TEXT = 1500          # a structural "text" field longer than this is a source text, not a label
DECLARED_MIN = 6000      # a declared full-text prompt shorter than this holds an abstract only (DART mc-3a8f4717: 1927)
_DECLARED = re.compile(r"PMID\s*(\d{4,9})\b[^\"]{0,80}?full[ -]?text", re.I)


def licences(index_path=INDEX):
    idx = json.load(open(index_path, encoding="utf-8")) if os.path.exists(index_path) else {}
    return {str(p): (e or {}).get("copy_licence") for p, e in idx.items()}


def _prompt_text(record):
    p = (record or {}).get("prompt") or {}
    if isinstance(p, dict) and p.get("b64"):
        return base64.b64decode(p["b64"]).decode("utf-8", "replace")
    return p if isinstance(p, str) else ""


def _walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def embedded_sources(record):
    """[(pmid, chars, how)] of source texts a record's prompt carries."""
    out = []
    p = _prompt_text(record)
    i = p.find("=== EVIDENCE ===")
    if i >= 0:
        try:
            ev = json.loads(p[i + len("=== EVIDENCE ==="):])
        except ValueError:
            ev = None
        for d in _walk(ev):
            t = d.get("text")
            if d.get("pmid") and isinstance(t, str) and len(t) > MIN_TEXT:
                out.append((str(d["pmid"]), len(t), "structural"))
    for dg in (record or {}).get("input_digests") or []:
        m = _DECLARED.search(str(dg.get("ref") or ""))
        if m and len(p) > DECLARED_MIN:
            out.append((m.group(1), len(p), "declared"))
    return out


def record_problems(record, lic=None):
    """Problems (empty = fine): one per source text whose PMID is not marked open."""
    lic = licences() if lic is None else lic
    probs = []
    for pmid, chars, how in embedded_sources(record):
        if lic.get(pmid) not in OPEN:
            probs.append(f"{record.get('record_id')}: prompt carries {chars} chars of PMID {pmid} text ({how}); its copy "
                         f"is not marked open (copy_licence={lic.get(pmid)!r})")
    return probs


def tracked_records(root=ROOT):
    import subprocess
    p = subprocess.run(["git", "ls-files", "registry/model_calls", "evidence/model_calls"], cwd=root,
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return [os.path.join(root, f) for f in p.stdout.split() if f.endswith(".json") and "/mc-" in f.replace("\\", "/")]
