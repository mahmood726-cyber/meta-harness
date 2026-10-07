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


# REGULATORY review windows (scripts/g1_regulatory_source.py): the licence follows from the document url's HOST only --
# a prompt cannot declare its own licence. FDA (a US Government work) is open; EMA ('reproduction authorised provided the
# source is acknowledged') only WITH that acknowledgement; NICE only when its held record says OGL/CC
# (regulatory_window_problem). Any other host is not marked open for a public record.
REG_HOST_OPEN = ("www.accessdata.fda.gov", "accessdata.fda.gov", "www.fda.gov")


def regulatory_sources(record, with_obj=False):
    """[(url, chars)] of regulatory document text a record's prompt carries (an evidence object with a url + windows);
    with_obj: [(url, chars, the evidence object)]."""
    p = _prompt_text(record)
    i = p.find("=== EVIDENCE ===")
    if i < 0:
        return []
    try:
        ev = json.loads(p[i + len("=== EVIDENCE ==="):])
    except ValueError:
        return []
    out = []
    for d in _walk(ev):
        if "windows" in d and ("url" in d or "agency" in d):
            chars = sum(len(str((w or {}).get("text") or "")) for w in d.get("windows") or [] if isinstance(w, dict))
            if chars:
                out.append((str(d.get("url") or ""), chars, d) if with_obj else (str(d.get("url") or ""), chars))
    return out


UPW_INDEX = os.path.join(ROOT, "outputs", "k_gap", "unpaywall_text_index.json")
REG_SOURCES = os.path.join(ROOT, "registry", "regulatory_sources.json")
EMA_HOSTS = ("www.ema.europa.eu", "ema.europa.eu")
NICE_HOSTS = ("www.nice.org.uk", "nice.org.uk")
# a whole-text block (scripts/k_gap_upw_locate.py: '<<<TEXT ... TEXT>>>'): 21 committed records carried whole Unpaywall
# texts in this shape and neither detector above saw them (6 Oct audit) -- 14 of them were not CC
_TEXT_BLOCK = re.compile(r"<<<TEXT\n(.*?)\nTEXT>>>", re.S)
_DOI_REF = re.compile(r"\bDOI\s+(10\.[^\s)]+)")


def doi_licences(index_path=UPW_INDEX):
    idx = json.load(open(index_path, encoding="utf-8")) if os.path.exists(index_path) else {}
    return {str(d).lower(): (e or {}).get("license") for d, e in idx.items()}


def jats_licence(path):
    """'CC' when the held JATS's own <permissions> name a Creative Commons licence, else 'NOT_OPEN'."""
    try:
        x = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return "NOT_HELD"
    perm = " ".join(re.findall(r"<permissions>.*?</permissions>", x, re.S))
    # the licence named by URL, or IN WORDS inside the article's own <permissions> ('distributed under the terms of the
    # Creative Commons Attribution License (CC BY)': 19 open articles had no URL, 6 Oct); never words outside <permissions>
    return "CC" if (re.search(r"creativecommons\.org/(?:licenses|publicdomain)/", perm)
                    or re.search(r"Creative\s+Commons\s+(?:Attribution|Zero|CC0)|\bCC0\b|\bCC[ -]BY\b", perm)) else "NOT_OPEN"


def _comparator_jats(pmid):
    import glob
    fs = sorted(glob.glob(os.path.join(ROOT, "cache", "comparators", str(pmid), "*jats*.xml")))
    return fs[0] if fs else None


_PMID_DOI = None


def pmid_doi(pmid):
    """A trial report's DOI from the held records (member_records + every topic's cache records)."""
    global _PMID_DOI
    if _PMID_DOI is None:
        import glob
        _PMID_DOI = {}
        srcs = [os.path.join(ROOT, "outputs", "k_gap", "member_records.json")] + \
            glob.glob(os.path.join(ROOT, "cache", "*", "records.json"))
        for f in srcs:
            try:
                d = json.load(open(f, encoding="utf-8"))
            except (OSError, ValueError):
                continue
            recs = d.get("records") if isinstance(d, dict) and "records" in d else \
                (list(d.values()) if isinstance(d, dict) else d)
            for r in recs or []:
                if isinstance(r, dict) and r.get("id") and r.get("doi"):
                    _PMID_DOI.setdefault(str(r["id"]), str(r["doi"]).lower())
    return _PMID_DOI.get(str(pmid))


def ref_licences(ref, lic, dlic):
    """[(source, licence)] for one declared input ref; licence 'CC'/'cc-*' is open, anything else is not."""
    ref = str(ref or "")
    m = re.match(r"cache/comparators/(\d+)/\S*jats\S*\.xml", ref)
    if m:
        return [(f"comparator JATS {m.group(1)}", jats_licence(os.path.join(ROOT, ref.split("#")[0].split(" ")[0])))]
    m = re.match(r"cache/([a-z0-9-]+)/comparator_fulltext\.txt", ref)
    if m:
        t = os.path.join(ROOT, "topics", m.group(1) + ".json")
        comp = json.load(open(t, encoding="utf-8")).get("comparator_pmid") if os.path.exists(t) else None
        j = _comparator_jats(comp) if comp else None
        return [(f"comparator {comp} text", jats_licence(j) if j else "NOT_HELD")]
    m = re.match(r"held open text PMID (\d+) \(([A-Z_+]+)\)", ref)
    if m:
        out = []
        for part in m.group(2).split("+"):
            if part in ("PMC_OA", "HELD_CACHE_FT"):
                out.append((f"PMID {m.group(1)} {part}", lic.get(m.group(1))))
            elif part == "UNPAYWALL":
                d = pmid_doi(m.group(1))
                out.append((f"PMID {m.group(1)} Unpaywall DOI {d}", dlic.get(d) if d else None))
        return out
    m = re.match(r"trial report PMID (\d+)", ref)
    if m:
        return [(f"PMID {m.group(1)} report", lic.get(m.group(1)))]
    m = _DOI_REF.search(ref)
    if m:
        return [(f"DOI {m.group(1)}", dlic.get(m.group(1).lower()))]
    return []


def _is_open(licence):
    return licence == "CC" or str(licence or "").startswith("cc")


def text_block_problems(record, dlic=None, lic=None):
    """A full-text-sized block (> DECLARED_MIN; abstract-sized blocks are the existing abstract policy) may come only from
    DECLARED sources that each resolve, from held data, to a CC licence (ref_licences)."""
    p = _prompt_text(record)
    chars = sum(len(b) for b in _TEXT_BLOCK.findall(p) if len(b) > DECLARED_MIN)
    if not chars:
        return []
    dlic = doi_licences() if dlic is None else dlic
    lic = licences() if lic is None else lic
    srcs = [s for dg in (record or {}).get("input_digests") or [] for s in ref_licences(dg.get("ref"), lic, dlic)]
    if not srcs:
        return [f"{record.get('record_id')}: prompt carries a {chars}-char text block with no declared source"]
    return [f"{record.get('record_id')}: prompt carries {chars} chars of {name} text; its copy is not CC-licensed "
            f"(licence={l!r})" for name, l in srcs if not _is_open(l)]


def regulatory_window_problem(record, url, chars, windows_obj, reg=None):
    """FDA: open (US Government work). EMA: open WITH an acknowledgement of the source in the evidence (EMA: 'reproduction
    is authorised provided the source is acknowledged'; Mahmood 6 Oct: EMA may be used). NICE: open only when the HELD
    source record says OGL or CC (read from the document by scripts/g1_regulatory_source.py -- never from the prompt).
    Anything else: refused."""
    from urllib.parse import urlparse
    host = (urlparse(url).hostname or "").lower()
    rid = record.get("record_id")
    if host in REG_HOST_OPEN:
        return None
    if host in EMA_HOSTS:
        ack = str((windows_obj or {}).get("acknowledgement") or "")
        return None if "European Medicines Agency" in ack else \
            f"{rid}: prompt carries {chars} chars of EMA document {url!r} without the source acknowledgement"
    if host in NICE_HOSTS:
        reg = (json.load(open(REG_SOURCES, encoding="utf-8")) if os.path.exists(REG_SOURCES) else {}) if reg is None else reg
        lic = (reg.get(url) or {}).get("licence")
        return None if lic in ("OGL", "CC") else \
            f"{rid}: prompt carries {chars} chars of NICE document {url!r}; held licence {lic!r} is not OGL/CC"
    return f"{rid}: prompt carries {chars} chars of regulatory document {url!r}; its host is not an open-licence host"


def record_problems(record, lic=None, dlic=None, reg=None):
    """Problems (empty = fine): one per source text whose PMID is not marked open, per whole-text block whose DOI copy is
    not CC, and per regulatory document whose licence does not allow it (regulatory_window_problem)."""
    lic = licences() if lic is None else lic
    probs = text_block_problems(record, dlic, lic)
    # an Unpaywall copy shown in the acquisition evidence: {"doi": ..., "text": ...} -- the DOI's licence must be CC
    p = _prompt_text(record)
    i = p.find("=== EVIDENCE ===")
    if i >= 0:
        try:
            ev = json.loads(p[i + len("=== EVIDENCE ==="):])
        except ValueError:
            ev = None
        dl = None
        for d in _walk(ev):
            t = d.get("text")
            if d.get("doi") and not d.get("pmid") and isinstance(t, str) and len(t) > MIN_TEXT:
                dl = doi_licences() if dlic is None and dl is None else (dlic if dlic is not None else dl)
                if not str(dl.get(str(d["doi"]).lower()) or "").startswith("cc"):
                    probs.append(f"{record.get('record_id')}: prompt carries {len(t)} chars of DOI {d['doi']} text; its "
                                 f"Unpaywall copy is not CC-licensed ({dl.get(str(d['doi']).lower())!r})")
    for url, chars, obj in regulatory_sources(record, with_obj=True):
        pr = regulatory_window_problem(record, url, chars, obj, reg)
        if pr:
            probs.append(pr)
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
