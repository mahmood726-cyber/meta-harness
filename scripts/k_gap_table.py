"""K-GAP TABLE: for every served topic with a comparator meta, the comparator's drug-specific included
set (from its included-studies TABLE, not its headline k) against our pool, trial by trial, with the
open source that could supply each missing trial's typed result.

Measurement only: reads committed caches + the local AACT snapshot + (network, cached) PMC idconv /
Europe PMC OA flags. It admits nothing and edits no topic page.

    python scripts/k_gap_table.py            # writes outputs/k_gap/{k_gap_table.json,k_gap_table.csv,SUMMARY.md}
    python scripts/k_gap_table.py --offline  # skip the OA probe (reads the cached probe if present)
"""
from __future__ import annotations

import csv
import glob
import hashlib
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from kgap import k_gap  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
DATE = "2026-09-28"

MEASURE = {"EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH", "RESULT_INCOMPATIBLE", "ENGINE_CANNOT_CONSUME",
           "outcome_post_hoc_not_pooled"}
EXTRACT = {"COUNTS_PRESENT_NOT_CORROBORATED", "EXTRACTION_NOT_PERFORMED", "KNOWN_REPORTED_NOT_YET_EXTRACTED",
           "ENDPOINT_UNBOUND"}
ACQUIRE = {"SOURCE_NOT_RETRIEVED", "OUTCOME_NOT_IN_SOURCE", "outcome_not_reported"}
DELIBERATE_KINDS = {"refused_on_evidence", "result_withdrawn", "adjudicated_absent"}


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _num(i):
    return re.sub(r"^(PMID|pmid)\s*", "", str(i or "")).strip().upper()


def topic_agents(topic: dict) -> list[str]:
    ag = topic.get("intervention_agents") or {}
    terms = list(ag.keys()) + [s for v in ag.values() for s in (v or [])] + list(topic.get("intervention_terms") or [])
    return sorted({t for t in terms if t and len(t) >= 3}, key=str.lower)


def molecule_names(topic: dict) -> list[str]:
    """Named molecules only (intervention_agents keys + synonyms) -- the vocabulary for "this row names ANOTHER
    served topic's drug". Class terms ("statin", "SGLT2 inhibitor") are excluded: they appear in background-
    therapy columns of trials of a different drug."""
    ag = topic.get("intervention_agents") or {}
    return sorted({t for t in list(ag.keys()) + [x for v in ag.values() for x in (v or [])] if t and len(t) >= 5})


def outcome_keywords(topic: dict) -> list[str]:
    po = topic.get("primary_outcome") or {}
    kws = [po.get("name") or ""] + list(po.get("keywords") or [])
    return [k for k in kws if k and len(k) >= 4 and k.lower() not in (
        "primary outcome", "primary end point", "primary endpoint", "primary efficacy end point",
        "risk of the primary end point", "primary end-point event", "composite primary end-point")]


def ours(slug: str) -> dict:
    rev = _j(os.path.join(ROOT, "docs", "reviews", slug, "review.json"))
    prim = next((o for o in rev.get("outcomes", []) if o.get("primary")), {})
    mem = prim.get("membership") or {}
    pooled = {_num(t.get("id")) for t in prim.get("trials", [])} | {_num(x) for x in mem.get("pooled", [])}
    pooled_fam = {_num(x) for x in mem.get("pooled_family_ids", [])}
    absent = {}
    for d in prim.get("declared_absent_trials", []):
        rec = {"reason_code": d.get("reason_code") or "", "absent_kind": d.get("absent_kind") or "",
               "reason": (d.get("reason") or "")[:240], "id": d.get("id")}
        for k in (d.get("id"), d.get("trial_family_id"), d.get("trial_id"), d.get("report_id")):
            if k:
                absent[_num(k)] = rec
    fams = []
    fp = os.path.join(ROOT, "cache", slug, "families.json")
    if os.path.exists(fp):
        for f in _j(fp).get("families", []):
            fams.append({"family_id": _num(f["family_id"]),
                         "reports": {_num(r["report_id"]) for r in f.get("reports", [])},
                         "acronyms": {k_gap.norm_acronym(a) for a in (f.get("aliases") or {}).get("acronym", [])},
                         "eligibility": (f.get("eligibility") or {}).get("state")})
    rec_ids, rec_acr, rec_text = set(), set(), []
    rp = os.path.join(ROOT, "cache", slug, "records.json")
    if os.path.exists(rp):
        rj = _j(rp)
        for r in rj.get("records", []):
            rec_ids.add(_num(r.get("id")))
            rec_text.append((_num(r.get("id")), r.get("title") or "", r.get("abstract") or ""))
            if r.get("nct"):
                rec_ids.add(_num(r["nct"]))
        for r in rj.get("ctgov", []) or []:
            rec_ids.add(_num(r.get("id")))
            if r.get("acronym"):
                rec_acr.add(k_gap.norm_acronym(r["acronym"]))
    return {"k": (prim.get("result") or {}).get("k"), "pooled": pooled, "pooled_fam": pooled_fam,
            "absent": absent, "families": fams, "rec_ids": rec_ids, "rec_acr": rec_acr, "records_text": rec_text,
            "estimand": (prim.get("estimand") or ""), "outcome": prim.get("name")}


def comparator_units(slug, pmid, agents, others=None):
    p = os.path.join(ROOT, "cache", "comparators", pmid, f"{DATE}_kgap_jats.xml")
    if not os.path.exists(p):
        return {"state": "NO_OPEN_JATS", "units": [], "tables_used": []}, None
    with open(p, "rb") as fh:
        body = fh.read()
    parsed = k_gap.parse_jats(body)
    inc = k_gap.included_trials(parsed, agents, others)
    inc["jats_file"] = os.path.relpath(p, ROOT).replace(os.sep, "/")
    inc["jats_sha256"] = k_gap.sha256(body)
    return inc, parsed


_STUDY_ID = re.compile(r"([A-Z][A-Za-z'’‐\- ]{1,40}? (?:19|20)\d\d[a-z]?) \{(?:published|unpublished)[^}]{0,60}\}")
_AUTHORS_END = re.compile(r"^(?P<authors>(?:[^.]{1,40}? [A-Z]{1,4}(?:, |\. ))+?)(?=[A-Z0-9])")


def _save_cache(cp, cache):
    """Shared PubMed caches are written by several tracker processes at once (g1_batch runs topics in parallel): a
    plain open('w') let a reader see a truncated file and corrupted pubmed_titles.json (2 Oct). Union with what is on
    disk now (another process's new entries survive; ours win on a key both hold), write a temp file, os.replace.
    Bounded retry: Windows refuses the replace while another process holds the file open."""
    import time
    for attempt in range(5):
        try:
            disk = _j(cp) if os.path.exists(cp) else {}
        except ValueError:
            disk = {}
        merged = {**disk, **cache}
        tmp = f"{cp}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(merged, fh, indent=1, sort_keys=True)
        try:
            os.replace(tmp, cp)
            return
        except PermissionError:
            time.sleep(0.5 * (attempt + 1))
    raise PermissionError(f"could not replace {cp} after 5 attempts")


def _first_citation(chunk):
    """'Baillargeon JP, Jakubowicz DJ, Nestler JE. Effects of ... sensitivity. Fertility and Sterility 2004;82:893-902.'
    -> (first author surname, title, year). Authors are 'Surname INITIALS' items ending at the first '. '."""
    first = re.split(r"\[ ?(?:DOI|PubMed|Google Scholar|PMC free article|CrossRef|Ref list) ?\]", chunk)[0].strip()
    # authors end at initials, 'et al .' or '...; COPPS Investigators.'
    a = re.match(r"(?P<authors>.+?(?:\bet al\s*|\bInvestigators|\b[A-Z]{1,4}))\s?\. (?P<after>.*)$", first, re.S)
    if not a:
        return "", "", "", first
    # the first author item ('Ben Ayed B', 'Morin-Papunen L') minus its trailing initials
    item = a.group("authors").split(",")[0].strip()
    surname = re.match(r"(.+?)(?:\s+[A-Z]{1,4})?$", item)
    after = a.group("after")
    t = re.match(r"(?P<title>.{12,400}?[.?!])\s+(?P<rest>.*)$", after, re.S)
    year = re.search(r"\b((?:19|20)\d\d)\b", t.group("rest") if t else after)
    return (surname.group(1) if surname else "", (t.group("title").rstrip(".?!").strip() if t else ""),
            year.group(1) if year else "", first)


def kt_fold(s):
    """Surname comparison only: diacritics, case and spaces folded ('Ben Ayed' == 'BenAyed')."""
    import unicodedata
    return re.sub(r"\s+", "", "".join(c for c in unicodedata.normalize("NFKD", s or "")
                                      if not unicodedata.combining(c)).lower())


def study_id_citations(text):
    """A review's 'References to studies included in this review' section (Cochrane layout) as reference records:
    one per STUDY ID ('Baillargeon 2004'), carrying its FIRST citation's first author, title and year. No PMID is
    invented -- the identity chain looks the title up and admits only a CONFIRMED PubMed record."""
    m = re.search(r"References to studies included in this review(.*?)(?:References to studies excluded|"
                  r"References to studies awaiting|References to ongoing studies|Additional references|$)", text, re.S)
    if not m:
        return {}
    body, out, dup = m.group(1), {}, set()
    ids = list(_STUDY_ID.finditer(body))
    for i, sid in enumerate(ids):
        chunk = body[sid.end(): ids[i + 1].start() if i + 1 < len(ids) else len(body)]
        label = sid.group(1).replace("’", "'").replace("‐", "-").strip()
        # the study ID names its PRIMARY report ('Legro 2007' = Legro RS, NEJM 2007), which need not be listed first
        # (Cataldo 2008, a secondary report, is): take the ONE citation whose first author and year are the ID's
        cites = [c for c in re.split(r"(?:\[ ?(?:DOI|PubMed|Google Scholar|PMC free article|CrossRef|Ref list|"
                                     r"original article|[a-z ]{3,30}) ?\]\s*)+", chunk) if c.strip()]
        id_sur, id_year = re.match(r"(.+?) ((?:19|20)\d\d)[a-z]?$", label).groups()
        named = [p for p in map(_first_citation, cites)
                 if p[2] == id_year and kt_fold(p[0]) == kt_fold(id_sur)]
        surname, title, year, first = named[0] if len(named) == 1 else _first_citation(chunk)
        if label in out:                               # a study ID listed twice is not an identity
            dup.add(label)
            continue
        out[label] = {"rid": "SID:" + label, "label": label, "ordinal": len(out) + 1, "pmid": None, "doi": None,
                      "first_author": surname, "title": title, "year": year, "text": first[:400],
                      "ncts": sorted(set(re.findall(r"NCT\d{8}", chunk)))}
    return {k: v for k, v in out.items() if k not in dup}


def numbered_citations(text):
    """A held TEXT copy's numbered reference list ('REFERENCES 1. Imazio M, Bobbio M, et al . Colchicine ... (COPE)
    trial. Circulation 2005;112:...') as reference records keyed by number. Numbers must run 1, 2, 3, ... in order;
    a list that does not is not trusted. No PMID is invented."""
    m = re.search(r"\bREFERENCES\b(.*)$", text, re.S) or re.search(r"\bReferences\b(.*)$", text, re.S)
    if not m:
        return {}
    body = m.group(1)
    marks, want = [], 1
    for x in re.finditer(r"(?:(?<=\s)|^)(\d{1,3})\. (?=[A-Z])", body):
        if int(x.group(1)) == want:
            marks.append(x)
            want += 1
    if len(marks) < 3:
        return {}
    out = {}
    for i, x in enumerate(marks):
        chunk = body[x.end(): marks[i + 1].start() if i + 1 < len(marks) else len(body)]
        chunk = re.split(r"\bTable \d+\b|\bFigure \d+\b", chunk)[0]
        surname, title, year, first = _first_citation(chunk)
        out[x.group(1)] = {"rid": "REF:" + x.group(1), "label": x.group(1), "ordinal": int(x.group(1)), "pmid": None,
                           "doi": None, "first_author": surname, "title": title, "year": year, "text": first[:400],
                           "ncts": sorted(set(re.findall(r"NCT\d{8}", chunk)))}
    return out


_LF_STOP = {"of", "and", "the", "for", "in", "with", "on", "to", "a", "an", "vs", "versus", "by", "after"}


_TRIAL_TYPES = {"randomized controlled trial", "clinical trial", "clinical trial, phase iii", "clinical trial, phase ii",
                "clinical trial, phase iv", "controlled clinical trial", "pragmatic clinical trial"}


def trial_context(ref):
    """Is this reference a TRIAL report? Trial words in its own text/title, or a PubMed publication type of RCT /
    clinical trial for its PMID -- its own, or the one its title CONFIRMED (outputs/k_gap/pubmed_collective.json holds
    publication types beside collective names)."""
    if re.search(r"\b(?:trial|randomi[sz]ed|placebo|double[- ]blind|controlled)\b",
                 (ref.get("text") or "") + " " + (ref.get("title") or ""), re.I):
        return True
    pmid = ref.get("pmid")
    if not pmid:
        hit = REF_PMID.get(_ref_key(ref)) or {}
        pmid = hit.get("pmid") if hit.get("state") == "CONFIRMED" else None
    types = {t.lower() for t in ((COLLECTIVE.get(pmid or "") or {}).get("pubtypes") or [])}
    return bool(types & _TRIAL_TYPES)


def long_form_refusal(acr, text, phrase):
    """Why a matched long form belongs to ANOTHER named trial (IDREVIEW2 P1): it starts with a different all-caps
    acronym ('CORE COlchicine for REcurrent pericarditis' read as CORP), or the text labels that phrase with a
    different acronym in parentheses ('COlchicine for REcurrent pericarditis (CORE)'). None when it is ours."""
    want = re.sub(r"[^A-Z0-9]", "", (acr or "").upper())
    first = (phrase.split() or [""])[0]
    if re.fullmatch(r"[A-Z][A-Z0-9]{2,}", first) and re.sub(r"[^A-Z0-9]", "", first) != want:
        return f"starts_with_other_acronym:{first}"
    folded = k_gap.fold_dashes(text or "")
    i = folded.find(phrase.split()[-1]) if phrase else -1
    tail = re.match(r"\W*\(\s*([A-Z][A-Z0-9-]{2,})\s*\)", folded[i + len(phrase.split()[-1]):]) if i >= 0 else None
    if tail and re.sub(r"[^A-Z0-9]", "", tail.group(1)) != want:
        return f"labelled_as_other_acronym:{tail.group(1)}"
    return None


def acronym_long_form(acr, text, max_skips=4, check=True, anchored=True):
    """Does `text` spell out acronym `acr` (Schwartz-Hearst style)? The acronym's letters are consumed IN ORDER by
    prefixes of consecutive words: the FIRST letter from the first word's initial, the LAST letters from the last
    word; a word may contribute nothing only if it is a stopword or one of at most `max_skips` skipped content
    words. 'RALES' <- 'Randomized ALdactone Evaluation Study'; 'EPHESUS' <- 'Eplerenone Post-Acute Myocardial
    Infarction Heart Failure Efficacy and SUrvival Study'. Returns the matched phrase, or ''."""
    letters = re.sub(r"[^a-z0-9]", "", (acr or "").lower())
    if len(letters) < 4:
        return ""
    words = re.findall(r"[A-Za-z0-9]+", k_gap.fold_dashes(text or ""))
    low = [w.lower() for w in words]

    def match(i, j, skips):
        # letters[i:] must be consumed starting AT word j (word j must contribute)
        if i == len(letters):
            return j
        if j >= len(low):
            return None
        w = low[j]
        for k in range(min(len(w), len(letters) - i), 0, -1):
            if w[:k] == letters[i:i + k]:
                end = match_next(i + k, j + 1, skips)
                if end is not None:
                    return end
        return None

    def match_next(i, j, skips):
        if i == len(letters):
            return j
        for jj in range(j, len(low)):
            r = match(i, jj, skips + sum(1 for x in low[j:jj] if x not in _LF_STOP))
            if r is not None and skips + sum(1 for x in low[j:jj] if x not in _LF_STOP) <= max_skips:
                return r
            if skips + sum(1 for x in low[j:jj + 1] if x not in _LF_STOP) > max_skips:
                return None
        return None
    anchor = {"study", "trial", "investigators", "group", "collaborators", "collaborative"}
    for s in range(len(low)):
        if low[s][0] != letters[0]:
            continue
        end = match(0, s, 0)
        # a long form NAMES A TRIAL or its investigators: the phrase ends in, or is followed within two words by,
        # study / trial / investigators / group / collaborators ('...Evaluation Study Investigators'). A loose phrase
        # inside a sentence ('COlchicine in addition ... PEricarditis') is not a name.
        # ...and is a LONG form: at least 3 words, not the acronym's own tokens ('Aldo DHF' is not a long form of
        # 'Aldo-DHF' -- that is chain 3's evidence, whose ambiguity must stand)
        if end is not None and end - s >= 3 and "".join(low[s:end]) != letters and \
                (not anchored or low[end - 1] in anchor or any(w in anchor for w in low[end:end + 2])):
            if not check or long_form_refusal(acr, text, " ".join(words[s:end])) is None:
                return " ".join(words[s:end])
    return ""


def pmc_html_refs(html):
    """The reference list of a PMC article page ('<li id="bib7"><span class="label">7.</span><cite>Anker S.D., ...
    Empagliflozin in heart failure ... N Engl J Med. 2021;385:1451-1461.</cite> [PubMed link]'): one record per
    numbered item, with the PMID / DOI the page itself links. No PMID is invented."""
    out = {}
    for m in re.finditer(r'<li id="(?P<rid>[^"]+)">\s*<span class="label">(?P<lab>\d{1,3})\.?</span>\s*<cite>(?P<cite>.*?)</cite>'
                         r'(?P<tail>.*?)</li>', html, re.S):
        cite = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group("cite"))).strip()
        tail = m.group("tail")
        pmid = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", tail)
        doi = re.search(r"doi\.org/([^\"\s<]+)", tail)
        surname = re.match(r"([^\s,]+(?:\s+[a-z][^\s,]*)*)\s+[A-Z]", cite)
        year = re.search(r"\b((?:19|20)\d\d)\b", cite)
        parts = re.split(r"(?<=[a-z0-9\)])\.\s+(?=[A-Z])", cite)
        if m.group("lab") in out:
            # a number used twice makes every marker -> reference link on the page unsafe: no reference list at all
            # (IDREVIEW2 P2), never a silent overwrite
            return {}
        out[m.group("lab")] = {"rid": m.group("rid"), "label": m.group("lab"), "ordinal": int(m.group("lab")),
                               "pmid": pmid.group(1) if pmid else None, "doi": doi.group(1) if doi else None,
                               "first_author": surname.group(1) if surname else "",
                               "title": parts[1].strip() if len(parts) > 2 else "", "year": year.group(1) if year else "",
                               "text": cite[:400], "ncts": sorted(set(re.findall(r"NCT\d{8}", cite)))}
    return out


def subgroup_row(u):
    """A GROUP DESCRIPTION with a group size and no study identity -- 'Statin used group in QRISK 10-19% (n = 6438)'
    under the Gitsels 2016 study row -- is a sub-row of the study above it, not a trial. Requires a group word AND an
    '(n = N)' size AND no author-year, reference marker, NCT or citation link. Returns the reason, or None."""
    lab = u.get("label") or ""
    if u.get("layout") != "row" or u.get("cited") or u.get("ncts"):
        return None
    t = k_gap.identity_tokens(lab)
    if t["author"] or t["marker"] or t["ncts"]:
        return None
    core = re.sub(r"\(\s*n\s*=.*$", "", lab).strip()
    if re.fullmatch(r"[A-Z0-9][A-Z0-9\- ]{2,}", core):
        return None
    if re.search(r"\b(?:sub)?groups?\b|\barms?\b|\bcohorts?\b|\b(?:non-?)?users?\b", lab, re.I) and \
            re.search(r"\(\s*n\s*=\s*[\d,]+", lab, re.I):
        return "SUBGROUP_ROW_GROUP_DESCRIPTION_WITH_SIZE_NO_STUDY_IDENTITY"
    return None


def identity_refs(pmid):
    """The comparator's REFERENCE LIST for the identity chain when no kgap JATS is held: its open full text already
    held under the comparator's PMCID (Europe PMC fullTextXML / PMC OAI, both JATS). Refs only -- the tables of this
    copy are never used to enumerate units, so no topic's trial set moves. None when nothing parseable is held."""
    d = os.path.join(ROOT, "cache", "comparators", pmid)
    for pat in ("*_europepmc_fulltext.xml", "*_pmc_oai.xml"):
        for p in sorted(glob.glob(os.path.join(d, pat)), reverse=True):
            with open(p, "rb") as fh:
                body = fh.read()
            try:
                refs = k_gap.parse_refs(k_gap.ET.fromstring(body)) if hasattr(k_gap, "ET") else k_gap.parse_jats(body)["refs"]
            except Exception:  # noqa: BLE001 -- a copy that does not parse is not a reference list
                continue
            if refs:
                return {"refs": refs, "source": os.path.relpath(p, ROOT).replace(os.sep, "/"), "sha256": k_gap.sha256(body)}
    # a held PMC ARTICLE PAGE (dapagliflozin: Europe PMC 500 / PMC OAI 400 for PMC10123444; the page itself is the
    # open copy) -- its numbered reference list with the PMIDs the page links. Held locally only (licence), never committed.
    for p in sorted(glob.glob(os.path.join(d, "*_pmc_article.html")), reverse=True):
        with open(p, "rb") as fh:
            body = fh.read()
        refs = pmc_html_refs(body.decode("utf-8", errors="replace"))
        if refs:
            return {"refs": refs, "source": os.path.relpath(p, ROOT).replace(os.sep, "/"), "sha256": k_gap.sha256(body),
                    "layout": "PMC_ARTICLE_HTML"}
    # no JATS copy (metformin: the Europe PMC fetch was a 404 recorded as a 0-byte file): a held TEXT copy's
    # included-studies citation list, keyed by study ID
    for p in sorted(glob.glob(os.path.join(d, "*_legacy_comparator_fulltext.txt")), reverse=True):
        with open(p, "rb") as fh:
            body = fh.read()
        txt = body.decode("utf-8", errors="replace")
        for layout, refs in (("STUDY_ID_CITATIONS", study_id_citations(txt)),
                             ("NUMBERED_REFERENCES", numbered_citations(txt))):
            if refs:
                return {"refs": refs, "source": os.path.relpath(p, ROOT).replace(os.sep, "/"),
                        "sha256": k_gap.sha256(body), "layout": layout}
    return None


def pub_years(pmids, offline=False) -> dict:
    """PMID -> publication year (NCBI esummary pubdate; cached outputs/k_gap/pubmed_years.json)."""
    cp = os.path.join(OUT, "pubmed_years.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [] if offline else sorted({x for x in pmids if x and x.isdigit() and x not in cache})
    if todo:
        from harness import http
        for i in range(0, len(todo), 150):
            chunk = todo[i:i + 150]
            try:
                d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                                  {"db": "pubmed", "id": ",".join(chunk), "retmode": "json"})
            except Exception as exc:  # noqa: BLE001
                print("esummary failed", exc)
                continue
            for x in chunk:
                m = re.match(r"(\d{4})", ((d.get("result") or {}).get(x) or {}).get("pubdate") or "")
                cache[x] = int(m.group(1)) if m else None
        _save_cache(cp, cache)
    return cache


def pubmed_ncts(pmids, offline=False) -> dict:
    """PMID -> the NCT PubMed itself attaches to the paper (DataBankList / 'ClinicalTrials.gov number' in the abstract),
    via harness.fetch._efetch's own selection. A SECONDARY report of a trial carries its trial's NCT here even when
    AACT's study_references never lists it (EMPA-REG secondary 26981940). Cached outputs/k_gap/pubmed_ncts.json."""
    cp = os.path.join(OUT, "pubmed_ncts.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [] if offline else sorted({x for x in pmids if x and x.isdigit() and x not in cache})
    if todo:
        from harness import fetch
        for i in range(0, len(todo), 150):
            chunk = todo[i:i + 150]
            try:
                recs = fetch._efetch(chunk)
            except Exception as exc:  # noqa: BLE001
                print("efetch failed", exc)
                continue
            got = {r.get("id"): (r.get("nct") or "").upper() for r in recs}
            for x in chunk:
                cache[x] = got.get(x, "")
        _save_cache(cp, cache)
    return cache


def pubmed_titles_of(pmids, offline=False) -> dict:
    """PMID -> PubMed title (esummary; shares outputs/k_gap/pubmed_titles.json with the identity reader)."""
    cp = os.path.join(OUT, "pubmed_titles.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [] if offline else sorted({x for x in pmids if x and x.isdigit() and x not in cache})
    if todo:
        from harness import http
        for i in range(0, len(todo), 150):
            chunk = todo[i:i + 150]
            try:
                d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                                  {"db": "pubmed", "id": ",".join(chunk), "retmode": "json"})
            except Exception as exc:  # noqa: BLE001
                print("esummary failed", exc)
                continue
            for x in chunk:
                cache[x] = ((d.get("result") or {}).get(x) or {}).get("title", "")
        _save_cache(cp, cache)
    return cache


def _title_key(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", k_gap.fold_dashes(t or "").lower()).strip()



def _first_surname(label):
    import re as _r
    m = _r.match(r"\s*([A-Za-z][A-Za-z'-]{2,})", str(label or ""))
    return m.group(1).lower() if m else None


def mark_duplicate_units(rows):
    """ONE comparator trial listed in two of the comparator's tables (balanced-crystalloids: 'Semler (SMART trial)' in
    one table, 'Semler [15]' in another, both PMID 29485925) is one trial: the later unit is status DUPLICATE_UNIT with
    duplicate_of, and leaves the comparator's N. Only when both units resolve to the same identity (same NCT set, else
    same PMID set) AND name the same first author -- two numbered rows of one registration ('1 [21]' / '9 [28]', PLATO)
    may be two analyses the comparator itself counts, so they stay. (consolidation 2026-10-04: SMART was counted twice
    once both units resolved; before, a first-accession tie-break mislabelled one OTHER_AGENT and hid it.)"""
    seen = {}
    for r in rows:
        if r.get("drug") == "OTHER_AGENT" or r.get("status") in ("UNRESOLVED", "DUPLICATE_UNIT"):
            continue
        ident = tuple(sorted(r.get("ncts") or [])) or tuple(sorted(r.get("pmids") or []))
        if not ident:
            continue
        key = (r.get("slug"), ident)
        prev = seen.get(key)
        if prev is not None and _first_surname(r.get("label")) and \
                _first_surname(r.get("label")) == _first_surname(prev.get("label")):
            r["status"], r["duplicate_of"] = "DUPLICATE_UNIT", prev.get("label")
            continue
        seen.setdefault(key, r)
    return rows

def registered_before(n, year, idx) -> bool:
    """True unless we KNOW the registration was first submitted after the paper's publication year."""
    d = ((idx.get("study") or {}).get(n) or {}).get("study_first_submitted_date") or ""
    return not (year and d[:4].isdigit() and int(d[:4]) > int(year))


def _paper_registration(cands, pmids, u, idx, basis):
    """ONE registration for a paper AACT links to `cands` (registered before publication), or None. A single candidate
    is it. Several: the paper's OWN full accession list (DATABANK) must name exactly one of them, or -- when it names
    several -- the row's own label must name exactly one by its registered acronym. No family tiebreak here."""
    if len(cands) == 1:
        return cands[0]
    if len(cands) < 2:
        return None
    own = sorted({n for p in pmids if p in DATABANK for n in DATABANK[p]["databank"] + DATABANK[p]["abstract"]}
                 & set(cands))
    if len(own) == 1:
        basis.append(f"pmid_nct_from_pubmed_record_among_aact:{own[0]}")
        return own[0]
    want = {k_gap.norm_acronym(a) for a in u["acronyms"]} - {""}
    named = [n for n in (own or cands)
             if k_gap.norm_acronym(((idx.get("study") or {}).get(n) or {}).get("acronym") or "") in want]
    if len(own) > 1 and len(named) == 1:
        basis.append(f"pmid_nct_paper_lists_several_label_acronym:{named[0]}")
        return named[0]
    basis.append(f"pmid_nct_ambiguous:{','.join(cands[:4])}")
    return None


def nct_tiebreak(mapped, pmids, our_fams, pubnct):
    """Several registrations link the paper as RESULT (STEP 1's PMID 33567185 is listed by its own NCT03548935 AND by
    SELECT's NCT03574597). The paper's OWN PubMed record names its registration: that wins. Only when it names none of
    the candidates, the one candidate in our pool's families (the older tie-break -- which, alone, made STEP 1 inherit
    SELECT's identity because SELECT is pooled). Returns (candidates kept, basis note or None)."""
    own = sorted({(pubnct.get(p) or "").upper() for p in pmids} & set(mapped))
    if len(own) == 1:
        return own, f"pmid_nct_tiebreak_paper_record:{own[0]}"
    if our_fams:
        ours = [n for n in mapped if n in our_fams]
        if len(ours) == 1:
            return ours, f"pmid_nct_tiebreak_our_family:{ours[0]}"
    return mapped, None


def resolve_unit(u, parsed, idx, agents_re, years=None, our_fams=None):
    """Identity: cited ref PMID > NCT written in the unit > Author-Year against the comparator's own
    ref-list > acronym against AACT studies.acronym restricted to NCTs whose interventions name a topic
    agent. Each step records its basis; an acronym hitting >1 agent NCT is AMBIGUOUS, not guessed."""
    basis = []
    # identity fields from the label itself (marker / glued year / '(n = N)' separated); the unit's own tokens are kept
    # wherever the identity reading finds nothing, so a unit the old reading resolved keeps its inputs
    # ...only for a trial LABEL (table row/column, review text). A reference-seed unit's 'label' is a paper title and it
    # carries its own PMID: reading 'COVID-19' out of a title as an acronym dropped five correct cited identities.
    if u.get("layout") in ("row", "column", "text"):
        t = k_gap.identity_tokens(u.get("label") or "")
        u = dict(u, marker=t["marker"], acronyms=t["acronyms"] or list(u.get("acronyms") or []),
                 author=u.get("author") or t["author"], year=u.get("year") or t["year"])
    # A citation link is trusted only when the row's own label does not contradict the reference it points to:
    # the omega-3 comparator's table is numbered one off from its reference list (28/28 links), so following the
    # link faithfully resolved every row to the trial in the row above.
    kept = []
    for c in u["cited"]:
        if c.get("basis") is None and u.get("distrust_links"):
            basis.append("xref_table_distrusted:" + u["distrust_links"])
            continue
        why = k_gap.label_ref_conflict(u, c, registry_acronyms_of(c.get("pmid"), idx)) if c.get("basis") is None else None
        if why:
            basis.append(f"xref_label_conflict:{why}")
        else:
            kept.append(c)
    # (chain 1) the label's own reference marker -> the comparator's numbered reference, when the row has no usable
    # citation link and the table's links are NOT distrusted (a shifted table's numbering is exactly what we distrust)
    if not kept and u.get("marker") and parsed and not u.get("distrust_links"):
        hits = [r for r in parsed["refs"].values() if r.get("label") == u["marker"]] or \
               [r for r in parsed["refs"].values() if not r.get("label") and str(r.get("ordinal")) == u["marker"]]
        if len(hits) == 1:
            kept.append(dict(hits[0], basis=None))
            basis.append(f"label_marker_ref:{u['marker']}")
        else:
            basis.append(f"label_marker_ref_not_unique:{u['marker']}:{len(hits)}")
    elif u.get("marker") and u.get("distrust_links") and u.get("marker_offset") and parsed:
        # a SYSTEMATIC numbering shift measured on this table (omega-3: +1 on 27 of 28 labelled rows): marker N -> the
        # reference N+offset, admitted per row only when that reference agrees with the row's OWN label and year
        n = str(int(u["marker"]) + u["marker_offset"])
        hits = [r for r in parsed["refs"].values() if r.get("label") == n]
        ok = len(hits) == 1 and (name_words_match(u.get("label"), hits[0]) or
                                 (k_gap.label_ref_conflict(u, hits[0], []) is None and positive_ref_evidence(u, hits[0])))
        if ok:
            kept.append(dict(hits[0], basis=None))
            basis.append(f"label_marker_ref_shifted:{u['marker_offset']:+d}:{u['marker']}->{n}:{u['marker_offset_evidence']}")
        else:
            basis.append(f"label_marker_shifted_ref_disagrees_with_row:{u['marker']}->{n}")
    elif u.get("marker") and u.get("distrust_links"):
        basis.append(f"label_marker_not_used:table_links_distrusted:{u['marker']}")
    # (chain 1b) the label IS a study ID in the comparator's reference list ('Palomba 2005a'), else Author + Year names
    # exactly one reference -- with or without a PMID (chain 2 below confirms one, or the row says it could not)
    if not kept and parsed and not u.get("distrust_links") and (u.get("author") and u.get("year")):
        lab = k_gap.fold_dashes(re.sub(r"\s+", " ", u.get("label") or "")).replace("’", "'").strip()
        hits = [r for r in parsed["refs"].values() if r.get("label") and r["label"] == lab]
        how = "study_id"
        if not hits:
            def fold(x):
                import unicodedata
                return "".join(c for c in unicodedata.normalize("NFKD", x or "") if not unicodedata.combining(c)).lower()
            hits = [r for r in parsed["refs"].values() if fold(r.get("first_author")) == fold(u["author"])
                    and r.get("year") == u["year"]]
            how = "author_year"
        if len(hits) == 1:
            kept.append(dict(hits[0], basis=None))
            basis.append(f"{how}_ref:{hits[0]['rid']}")
        elif len(hits) > 1:
            basis.append(f"{how}_ref_ambiguous:{len(hits)}")
    # (chain 1c) 'Surname [I] et al' with NO year: the reference whose FIRST author is that surname -- exactly one in
    # the whole list (whitespace folded: the PDF text splits 'Finke lstein'). Two such references: ambiguous.
    elif not kept and parsed and not u.get("distrust_links") and u.get("author") and not u.get("year") and \
            re.search(r"\bet\s+al\b", u.get("label") or ""):
        def fold2(x):
            import unicodedata
            return re.sub(r"\s+", "", "".join(c for c in unicodedata.normalize("NFKD", x or "")
                                                if not unicodedata.combining(c)).lower())
        hits = [r for r in parsed["refs"].values() if fold2(r.get("first_author")) == fold2(u["author"])]
        if len(hits) == 1 and not trial_context(hits[0]):
            # a unique first author is not yet a TRIAL: a background, guideline or methods citation would pass
            # (IDREVIEW2 P1). Trial words in the reference, or a PubMed RCT / clinical-trial publication type, needed.
            basis.append(f"author_only_ref_refused_no_trial_context:{hits[0]['rid']}")
        elif len(hits) == 1:
            kept.append(dict(hits[0], basis=None))
            basis.append(f"author_only_ref:{hits[0]['rid']}")
        elif len(hits) > 1:
            basis.append(f"author_only_ref_ambiguous:{len(hits)}")
    # (chain 2) a cited reference with NO PMID: its DOI or its exact title, CONFIRMED in PubMed by title + first author
    # + year (scripts/ref_title_pmid_lookup.py, cached with retrieval time); never a guess
    for i, c in enumerate(kept):
        if c.get("pmid"):
            continue
        # a citation LINK carries rid/title/ids but not the citation text; the title of a congress abstract lives only
        # in that text (Ratanarat [18]), so the key is built from the full reference record when one is held
        full = (parsed or {}).get("refs", {}).get(c.get("rid")) if c.get("rid") else None
        if full and not c.get("text"):
            c = kept[i] = dict(full, **{k: v for k, v in c.items() if v not in (None, "")})
        hit = REF_PMID.get(_ref_key(c))
        if hit and hit.get("state") == "CONFIRMED":
            kept[i] = dict(c, pmid=hit["pmid"])
            basis.append(f"ref_title_pubmed_confirmed:{hit['pmid']}")
        elif hit:
            basis.append(f"ref_not_in_pubmed:{hit['state']}" if hit["state"].startswith("NOT_IN_PUBMED")
                         else f"ref_pubmed_lookup:{hit['state']}")
        else:
            basis.append("ref_has_no_pmid:" + ("doi_unmapped" if c.get("doi") else "no_doi") + ":not_looked_up")
    pmids = {c["pmid"] for c in kept if c.get("pmid")}
    ncts = set(u["ncts"])
    if pmids:
        basis.append("comparator_ref_pmid")
    if ncts:
        basis.append("nct_in_table")
    if not pmids and u["author"] and u["year"] and parsed:
        hits = [r for r in parsed["refs"].values()
                if r.get("pmid") and r.get("first_author", "").lower() == u["author"].lower() and r.get("year") == u["year"]]
        if len(hits) == 1:
            pmids.add(hits[0]["pmid"])
            basis.append("author_year_ref_list")
        elif len(hits) > 1:
            basis.append(f"author_year_ambiguous:{len(hits)}")
    # PMID -> NCT only when AACT links the PMID to exactly ONE registration: a paper is cited as background by later
    # trials' registrations (Deftereos' PMIDs are listed by NCT04906720 and NCT06731595, colchicine trials of 2021+),
    # and following those links made Deftereos 'POOLED' via another paper of that NCT (COPPS-2).
    pmid_resolved = bool(pmids)
    years = years or {}
    mapped = sorted({n for p in pmids for n, _t in idx["pmid_nct"].get(p, []) if registered_before(n, years.get(p), idx)})
    dropped = sorted({n for p in pmids for n, _t in idx["pmid_nct"].get(p, [])} - set(mapped))
    if dropped:
        basis.append(f"pmid_nct_registered_after_publication:{','.join(dropped[:4])}")
    paper_lists_several = False
    if len(mapped) > 1:
        # the paper's OWN accessions (PubMed DataBankList + abstract, the FULL list) name its registration(s); a later
        # trial that lists the paper as a reference does not (STEP 1's NEJM paper is a RESULT reference of SELECT too).
        # Exactly one of the candidates named by the paper -> that one. Two or more -> the paper reports several trials
        # (CANVAS + CANVAS-R; a pooled RE-COVER/RE-MEDY analysis): no tiebreak may pick one. Before any family tiebreak.
        held = [p for p in pmids if p in DATABANK]
        own = sorted({n for p in held for n in DATABANK[p]["databank"] + DATABANK[p]["abstract"]} & set(mapped))
        if len(own) == 1:
            basis.append(f"pmid_nct_from_pubmed_record_among_aact:{own[0]}")
            mapped = own
        elif len(own) > 1:
            # the ROW'S OWN LABEL may name exactly one of them by its registered acronym (synthetic example:
            # a label naming one of a paper's two listed registrations by its acronym): direct evidence, not a
            # tiebreak. SMART's own record lists SMART-MED and SMART-SURG: 'SMART' names neither, so it stays refused
            want = {k_gap.norm_acronym(a) for a in u["acronyms"]} - {""}
            named = [n for n in own if k_gap.norm_acronym(((idx.get("study") or {}).get(n) or {}).get("acronym") or "")
                     in want]
            if len(named) == 1:
                basis.append(f"pmid_nct_paper_lists_several_label_acronym:{named[0]}")
                mapped = named
            else:
                paper_lists_several = True
                basis.append(f"pmid_nct_paper_lists_several:{','.join(own[:4])}")
    # (acq/k-gap f21c0aa4's first-accession tie-break, nct_tiebreak with PUBNCT, is NOT applied: PUBNCT holds only the
    # FIRST DataBank NCT and picked SMART-MED for SMART -> OTHER_AGENT; the identity lane's rule (test_idaudit_findings::
    # test_single_nct_cache_is_not_used_as_the_papers_full_list) is that it never decides. STEP 1 resolves by the paper's
    # full accession list (DATABANK). Consolidation 2026-10-04.)
    if len(mapped) > 1 and our_fams and not paper_lists_several:
        ours = [n for n in mapped if n in our_fams]
        if len(ours) == 1:
            basis.append(f"pmid_nct_tiebreak_our_family:{ours[0]}")
            mapped = ours
    if not mapped:
        own = sorted({PUBNCT.get(p) for p in pmids if PUBNCT.get(p)})
        # PUBNCT is the FIRST accession only; when the full list is held and names several, the paper is multi-trial
        several = sorted({n for p in pmids if p in DATABANK for n in DATABANK[p]["databank"] + DATABANK[p]["abstract"]})
        if len(own) == 1 and len(several) > 1:
            basis.append(f"pmid_nct_paper_lists_several:{','.join(several[:4])}")
        elif len(own) == 1:
            mapped = own
            basis.append(f"pmid_nct_from_pubmed_record:{own[0]}")
    if len(mapped) == 1:
        ncts.add(mapped[0])
    elif len(mapped) > 1:
        basis.append(f"pmid_nct_ambiguous:{','.join(mapped[:4])}")
    if not ncts:
        for a in u["acronyms"]:
            # an acronym names a trial only if that registration EXISTED by the label's year: 'ASCEND 2018' is not the
            # 2020 HARPOON device study NCT04382612 that reuses the name
            cands = [n for n in idx["acr_nct"].get(k_gap.norm_acronym(a), [])
                     if idx["agent_nct"].get(n) and registered_before(n, u.get("year"), idx)]
            cands = sorted(set(cands))
            if len(cands) == 1:
                ncts.add(cands[0])
                basis.append(f"acronym_aact:{a}")
                break
            if len(cands) > 1:
                basis.append(f"acronym_ambiguous:{a}:{','.join(cands[:4])}")
                continue
            tc = sorted({n for n in idx.get("acr_title_nct", {}).get(k_gap.norm_acronym(a), [])
                     if idx["agent_nct"].get(n) and registered_before(n, u.get("year"), idx)})
            if len(tc) == 1:
                ncts.add(tc[0])
                basis.append(f"acronym_aact_title:{a}")
                break
            if len(tc) > 1:
                basis.append(f"acronym_title_ambiguous:{a}:{','.join(tc[:4])}")
                continue
            sr = sorted({n for n in SELF_REG.get(k_gap.norm_acronym(a), [])
                     if idx["agent_nct"].get(n) and registered_before(n, u.get("year"), idx)})
            if len(sr) == 1:
                ncts.add(sr[0])
                basis.append(f"acronym_self_registration_sentence:{a}")
                break
            if len(sr) > 1:
                basis.append(f"acronym_self_registration_ambiguous:{a}:{','.join(sr[:4])}")
    # (chain 3) an acronym the comparator's OWN reference list names, in exactly one reference (and that reference's
    # year equals the label's year when the label has one): 'Aldo-DHF2013' -> Edelmann 2013 (PMID 23443441)
    if not ncts and not pmids and parsed and u["acronyms"]:
        for a in u["acronyms"]:
            # the acronym as written, '-' and ' ' interchangeable ('VERTIS-CV' == 'VERTIS CV'), searched in the
            # reference text AND its PMID's PubMed collective-author name ('SOLOIST-WHF Trial Investigators')
            pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(k_gap.fold_dashes(a)).replace(r"\-", r"[-\s]").replace(
                r"\ ", r"[-\s]") + r"(?![A-Za-z0-9])", re.I)
            refs = [r for r in parsed["refs"].values()
                    if pat.search(k_gap.fold_dashes(" ".join([r.get("text") or ""] + list(
                        (COLLECTIVE.get(r.get("pmid") or "") or {}).get("collective") or []))))
                    and (not u.get("year") or r.get("year") == u["year"])]
            if len(refs) == 1 and not refs[0].get("pmid"):
                hit = REF_PMID.get(_ref_key(refs[0]))
                if hit and hit.get("state") == "CONFIRMED":
                    refs = [dict(refs[0], pmid=hit["pmid"])]
                    basis.append(f"ref_title_pubmed_confirmed:{hit['pmid']}")
                else:
                    basis.append(f"acronym_ref_without_confirmed_pmid:{a}:{refs[0]['rid']}:"
                                 + (hit["state"] if hit else "not_looked_up"))
            if len(refs) == 1 and refs[0].get("pmid"):
                pmids.add(refs[0]["pmid"])
                pmid_resolved = True
                basis.append(f"acronym_named_in_comparator_ref:{a}:{refs[0]['rid']}")
                only = sorted({n for n, _t in idx["pmid_nct"].get(refs[0]["pmid"], [])
                               if registered_before(n, years.get(refs[0]["pmid"]), idx)})
                one = _paper_registration(only, [refs[0]["pmid"]], u, idx, basis)
                if one:
                    ncts.add(one)
                break
            if len(refs) > 1:
                # REPORT-FAMILY at reference level: several references naming the acronym are ONE trial when every
                # one of them is a report of the same single registration (AACT study_references, registered before
                # publication) -- VERTIS-CV's primary paper and its heart-failure secondary report. Else: ambiguous.
                regs = [{n for n, _t in idx["pmid_nct"].get(r.get("pmid") or "", [])
                         if registered_before(n, years.get(r.get("pmid")), idx)} for r in refs]
                common = set.intersection(*regs) if regs and all(regs) else set()
                unit_words = re.compile(r"\bextension\b|\bfollow-?up\b|\blong-term\b|\bopen-label\b|\bsubstudy\b",
                                        re.I)
                if len(common) == 1 and any(unit_words.search(r.get("text") or "") for r in refs):
                    basis.append(f"acronym_in_comparator_refs_same_registration_publication_unit_ambiguous:{a}:{len(refs)}")
                    break
                if len(common) == 1 and all(len(x) == 1 for x in regs):
                    ncts.add(next(iter(common)))
                    pmids |= {r["pmid"] for r in refs if r.get("pmid")}
                    pmid_resolved = True
                    basis.append(f"acronym_in_comparator_refs_one_trial:{a}:{next(iter(common))}:"
                                 + ",".join(r["rid"] for r in refs))
                    break
                basis.append(f"acronym_in_comparator_refs_ambiguous:{a}:{len(refs)}")
    # (chain 3b) the acronym's LONG FORM spelled out by exactly one comparator reference -- in its text, or in the
    # PubMed collective-author name of its PMID (outputs/k_gap/pubmed_collective.json): 'RALES' <- 'Randomized
    # aldactone evaluation study investigators' (ref text); 'EPHESUS' <- 'Eplerenone Post-Acute Myocardial Infarction
    # Heart Failure Efficacy and Survival Study Investigators' (collective author only). Year-checked; unique or nothing.
    if not ncts and not pmids and parsed and u["acronyms"]:
        for a in u["acronyms"]:
            if any(b.startswith(f"acronym_in_comparator_refs_ambiguous:{a}:") for b in basis):
                continue                              # two references NAME it: no long form overrides that
            refs = []
            for r in parsed["refs"].values():
                if u.get("year") and r.get("year") and r["year"] != u["year"]:
                    continue
                coll = (COLLECTIVE.get(r.get("pmid") or "") or {}).get("collective") or []
                lf = acronym_long_form(a, r.get("text") or "") or next(
                    (x for x in (acronym_long_form(a, c) for c in coll) if x), "")
                if not lf:
                    # what the matcher WOULD take with no refusal and no anchor: if that is another trial's phrase,
                    # record WHY it was refused (the acceptance above keeps every rule)
                    raw = acronym_long_form(a, r.get("text") or "", check=False, anchored=False)
                    if raw and long_form_refusal(a, r.get("text") or "", raw) is None:
                        raw = ""
                    if raw:
                        basis.append(f"acronym_long_form_refused:{a}:{r['rid']}:"
                                     + (long_form_refusal(a, r.get("text") or "", raw) or "other_trial_phrase"))
                if lf:
                    refs.append((r, lf))
            if len(refs) == 1 and refs[0][0].get("pmid"):
                r, lf = refs[0]
                pmids.add(r["pmid"])
                pmid_resolved = True
                basis.append(f"acronym_long_form_in_comparator_ref:{a}:{r['rid']}:{lf[:60]}")
                only = sorted({n for n, _t in idx["pmid_nct"].get(r["pmid"], [])
                               if registered_before(n, years.get(r["pmid"]), idx)})
                one = _paper_registration(only, [r["pmid"]], u, idx, basis)
                if one:
                    ncts.add(one)
                break
            if len(refs) > 1:
                basis.append(f"acronym_long_form_ambiguous:{a}:{len(refs)}")
    # (chain 4, last resort) a trial of ANOTHER agent: the agent-restricted acronym steps refuse it by design (a
    # finerenone trial in a spironolactone review), so nothing typed it. An acronym of >= 5 characters that names
    # exactly ONE registration in ALL of AACT (by acronym, else by brief title), registered by the label's year,
    # resolves; the REGISTRY then decides the drug (OTHER_AGENT). Two or more registrations: ambiguous, recorded.
    if not ncts and not pmids and u["acronyms"]:
        for a in u["acronyms"]:
            key = k_gap.norm_acronym(a)
            if len(key) < 5:
                continue
            for src, m in (("acronym", idx.get("acr_nct") or {}), ("title", idx.get("acr_title_nct") or {})):
                cand = sorted({n for n in m.get(key, []) if registered_before(n, u.get("year"), idx)})
                if len(cand) == 1 and not served_agent_in(cand[0], idx):
                    # unique, but nothing ties it to this corpus's drugs: a candidate, never an identity
                    basis.append(f"uncorroborated_any_agent_acronym_{src}:{a}:{cand[0]}")
                    break
                if len(cand) == 1:
                    ncts.add(cand[0])
                    basis.append(f"acronym_aact_any_agent_{src}:{a}")
                    break
                if len(cand) > 1:
                    basis.append(f"acronym_aact_any_agent_ambiguous_{src}:{a}:{len(cand)}")
                    break
            if ncts:
                break
    # never an EMPTY basis: an unresolved row says which link of the chain it stopped at
    if not ncts and not pmids:
        why = []
        if not parsed:
            why.append("no_comparator_reference_list")
        if not (u.get("cited") or u.get("marker")):
            why.append("no_citation_link_or_marker")
        if not (u.get("author") and u.get("year")):
            why.append("no_author_year_in_label")
        if not u["acronyms"]:
            why.append("no_acronym_in_label")
        basis.append("unresolved_at:" + (",".join(why) or "every_step_ran_without_a_unique_hit"))
    # NCT -> its PMIDs only when the NCT IS the identity (printed in the table, or an acronym match). When the identity is
    # a cited PMID, adding every other paper registered to its NCT is association, not identity.
    if not pmid_resolved:
        for n in list(ncts):
            cand = set(idx.get("nct_pmids", {}).get(n, []))
            if not cand:
                cand = background_self_reports(n, idx)
                if cand:
                    basis.append(f"background_ref_names_its_nct:{len(cand)}")
            # a paper published BEFORE the trial started cannot report it: a registration may type its own background
            # literature as RESULT (PACMAN-AMI, started 2017, lists ODYSSEY LONG TERM 2015 and FH I/II 2015 as RESULT and
            # so inherited LONG TERM's identity). Kept when either year is unknown.
            ys = dict(pub_years(sorted(q for q in cand if q not in YEARS), _OFFLINE), **YEARS) if cand else {}
            early = {q for q in cand if published_before_start(q, n, idx, ys)}
            if early:
                basis.append(f"nct_pmids_published_before_trial_start:{len(early)}")
            pmids |= cand - early
    return {"pmids": sorted(pmids), "ncts": sorted(ncts), "basis": basis}


_OFFLINE = False


def background_self_reports(n, idx) -> set:
    """A registration with NO RESULT/DERIVED reference: its BACKGROUND references whose OWN PubMed record names this NCT
    (pubmed_ncts). Background literature names other trials' registrations or none; a trial's own report names its own."""
    bg = (idx.get("background_pmids") or {}).get(n) or []
    nc = pubmed_ncts(bg, _OFFLINE) if bg else {}
    return {p for p in bg if (nc.get(p) or "").upper() == n.upper()}


def published_before_start(pmid, n, idx, years) -> bool:
    """True only when we KNOW the paper's year precedes the trial's start year (AACT studies.start_date)."""
    st = (idx.get("study") or {}).get(n) or {}
    d = (st.get("start_date") or "")[:4]
    y = years.get(pmid)
    return d.isdigit() and bool(y) and int(str(y)[:4]) < int(d)


def registry_acronyms_of(pmid, idx):
    """Acronyms the REGISTRY gives the trial(s) a PMID reports: AACT acronym field + parenthesised title acronyms."""
    out = []
    for n, _t in (idx.get("pmid_nct") or {}).get(pmid or "", []):
        st = (idx.get("study") or {}).get(n) or {}
        if st.get("acronym"):
            out.append(st["acronym"])
        out += [m.group(1) for m in k_gap._PAREN_ACRO.finditer(st.get("brief_title") or "")]
    return out


def distrust_shifted_tables(units, idx):
    """A publisher numbering shift is SYSTEMATIC: when >=3 and >=50% of a table's citation links contradict their
    rows' labels, no link in that table is trusted (every row then resolves from its own label). The omega-3
    comparator's Table 1 is one off from its reference list on 28 of 28 links."""
    by_table = {}
    for u in units:
        for c in u["cited"]:
            if c.get("basis") is None:
                by_table.setdefault(u["table"], []).append(
                    bool(k_gap.label_ref_conflict(u, c, registry_acronyms_of(c.get("pmid"), idx))))
    for u in units:
        v = by_table.get(u["table"], [])
        if len(v) and sum(v) >= 3 and sum(v) / len(v) >= 0.5:
            u["distrust_links"] = f"{sum(v)}/{len(v)} links in {u['table']} contradict their rows"
    return {t: (sum(v), len(v)) for t, v in by_table.items()}


_NAME_STOP = {"and", "of", "the", "for", "in", "with", "study", "trial", "group", "et", "al"}


def name_words_match(label, ref):
    """A trial NAME ('Risk & Prevention 2013 [42]') positively matches a reference whose own text or PubMed
    collective-author name ('Risk and Prevention Study Collaborative Group') contains EVERY capitalised content word of
    the name (at least two). This is the evidence for a named trial; label_ref_conflict's first-word-as-surname guess
    ('Risk' vs 'Roncaglioni') does not apply to it."""
    core = re.sub(r"\[\d+\]|\(\s*n\s*=.*$|(?:19|20)\d\d", " ", label or "")
    words = [w for w in re.findall(r"[A-Z][A-Za-z]+", core) if w.lower() not in _NAME_STOP]
    if len(words) < 2:
        return False
    hay = " ".join([ref.get("text") or "", ref.get("title") or ""] +
                   list((COLLECTIVE.get(ref.get("pmid") or "") or {}).get("collective") or [])).lower()
    hay_words = set(re.findall(r"[a-z]+", hay))
    return all(w.lower() in hay_words for w in words)


def positive_ref_evidence(t, ref):
    """The row and the reference POSITIVELY agree -- absence of a contradiction is not agreement (IDREVIEW P1: an
    acronym-only row passed against an unrelated shifted reference that simply carried no acronym). Evidence: the
    label's year equals the reference's year (and no stated year disagrees), or the label's author IS the reference's
    first author, or a label acronym appears in the reference's own text."""
    import unicodedata

    def fold(x):
        return re.sub(r"\s+", "", "".join(c for c in unicodedata.normalize("NFKD", x or "")
                                            if not unicodedata.combining(c)).lower())
    year = t.get("year")
    if year and ref.get("year") and ref["year"] != year:
        return False
    if year and ref.get("year") == year:
        return True
    if t.get("author") and fold(t["author"]) == fold(ref.get("first_author")):
        return True
    text = k_gap.fold_dashes((ref.get("text") or "") + " " + (ref.get("title") or ""))
    return any(re.search(r"(?<![A-Za-z0-9])" + re.escape(k_gap.fold_dashes(a)) + r"(?![A-Za-z0-9])", text, re.I)
               for a in t.get("acronyms") or [])


def learn_marker_offsets(units, parsed, offsets=(1, -1, 2, -2)):
    """For a DISTRUSTED table, the numbering shift its own labels prove: the single non-zero offset k for which >= 90%
    (and >= 5) of the table's marker rows agree with reference N+k by label and year -- and offset 0 does not. Sets
    u['marker_offset'] / ['marker_offset_evidence']; each row is still checked individually when it is used."""
    out = {}
    if not parsed:
        return out
    refs = {r.get("label"): r for r in parsed["refs"].values() if r.get("label")}
    tables = {}
    for u in units:
        if u.get("distrust_links") and u.get("layout") in ("row", "column"):
            t = k_gap.identity_tokens(u["label"])
            if t["marker"]:
                tables.setdefault(u["table"], []).append((u, dict(t, label=u["label"])))

    def agree(t, k):
        r = refs.get(str(int(t["marker"]) + k))
        v = {"label": "", "acronyms": t["acronyms"], "author": t["author"], "year": t["year"]}
        return bool(r) and (name_words_match(t.get("label"), r) or
                            (k_gap.label_ref_conflict(v, r, []) is None and positive_ref_evidence(t, r)))
    for table, rows in tables.items():
        score = {k: sum(agree(t, k) for _u, t in rows) for k in (0,) + tuple(offsets)}
        best = max(offsets, key=lambda k: score[k])
        n = len(rows)
        if n >= 5 and score[best] >= 0.9 * n and score[0] < 0.5 * n and \
                sum(1 for k in offsets if score[k] == score[best]) == 1:
            ev = f"{score[best]}/{n} rows agree at {best:+d}, {score[0]}/{n} at 0"
            for u, _t in rows:
                u["marker_offset"], u["marker_offset_evidence"] = best, ev
            out[table] = {"offset": best, "evidence": ev}
        else:
            out[table] = {"offset": None, "scores": score}
    return out


def registry_agent(ncts, idx):
    """True/False when AACT interventions for the resolved NCTs do / do not name a topic agent; None when
    no NCT resolved or AACT holds no intervention rows."""
    vals = [idx["agent_nct"][n] for n in ncts if n in idx["agent_nct"]]
    return any(vals) if vals else None


def consolidate_report_family(ident, families):
    """REPORT-FAMILY CONSOLIDATION: an identity is a TRIAL, not a paper. When the chain lands on one report of a trial we
    hold as a family (PCOSMIC: the review cites Johnson 2011, a secondary report; we hold the 2010 primary) the identity
    carries the whole family -- its NCT and every report -- so two reports of one trial never read as two identities.
    Exactly one family must claim the identity; two families claiming it is recorded, never merged."""
    # An identity that HAS a registration consolidates only into THAT registration's family. Its PMID list may be the
    # NCT's associated papers (pooled analyses, reviews), which overlap OTHER trials' families: PACMAN-AMI's list shares
    # a paper with ODYSSEY LONG TERM's family, and matching on PMIDs merged two trials.
    if ident["ncts"]:
        hits = [f for f in families if set(ident["ncts"]) & ({f["family_id"]} | set(f["reports"]))]
    else:
        hits = [f for f in families if set(ident["pmids"]) & ({f["family_id"]} | set(f["reports"]))]
    if len(hits) > 1:
        ident["basis"].append("report_family_ambiguous:" + ",".join(sorted(f["family_id"] for f in hits))[:80])
        return ident
    if not hits:
        return ident
    f = hits[0]
    reports = {r for r in f["reports"] if str(r).isdigit()}
    new_p, new_n = reports - set(ident["pmids"]), ({f["family_id"]} - set(ident["ncts"])
                                                   if f["family_id"].startswith("NCT") else set())
    if new_p or new_n:
        ident["pmids"] = sorted(set(ident["pmids"]) | reports)
        ident["ncts"] = sorted(set(ident["ncts"]) | new_n)
        ident["basis"].append(f"report_family_consolidated:{f['family_id']}:+{len(new_p)}pmid+{len(new_n)}nct")
    return ident


def match_ours(ident, acronyms, o):
    ids = set(ident["pmids"]) | set(ident["ncts"])
    acr = {k_gap.norm_acronym(a) for a in acronyms}
    fam = None
    for f in o["families"]:
        if (ids & ({f["family_id"]} | f["reports"])) or (acr & f["acronyms"]):
            fam = f
            break
    fam_ids = ({fam["family_id"]} | fam["reports"]) if fam else set()
    allids = ids | fam_ids
    if allids & (o["pooled"] | o["pooled_fam"]):
        return "POOLED", fam, None
    for k in allids:
        if k in o["absent"]:
            return "DECLARED_ABSENT", fam, o["absent"][k]
    if fam or (allids & o["rec_ids"]) or (acr & o["rec_acr"]):
        return "IDENTIFIED_NOT_POOLED", fam, None
    return "NOT_IDENTIFIED", None, None


def aact_source(ncts, idx, kws, estimand):
    """Does AACT hold POSTED results for an outcome matching the topic's primary outcome? Returns the
    matching outcome rows with their type (param_type), timeframe and analysis population verbatim."""
    kre = re.compile("|".join(re.escape(k) for k in kws), re.I) if kws else None
    posted, matches = False, []
    for n in ncts:
        outs = idx["outcomes"].get(n, [])
        if outs:
            posted = True
        for oc in outs:
            if kre and kre.search(oc["title"] + " " + oc.get("time_frame", "")):
                matches.append({"nct": n, **{k: oc[k] for k in ("outcome_type", "title", "time_frame", "population",
                                                                "param_type", "units")}})
    return {"results_posted": posted, "outcome_matches": matches[:4], "n_matches": len(matches)}


def classify(status, absent, reg_agent, aact_src, oa):
    if status == "POOLED":
        return "POOLED"
    if status == "UNRESOLVED":
        return "UNRESOLVED_IDENTITY"
    if status == "IDENTIFIED_NOT_INDEXED":
        return "IDENTIFIED_NOT_INDEXED"
    if status == "SCOPE_MISMATCH":
        return "SCOPE_MISMATCH"
    if status == "DECLARED_ABSENT":
        rc, kind = absent["reason_code"], absent["absent_kind"]
        if rc in MEASURE or kind in ("refused_on_evidence", "engine_cannot_consume"):
            return "MEASURE_MISMATCH"
        if rc in EXTRACT:
            return "EXTRACTION_FROM_TABLE"
        if kind in DELIBERATE_KINDS and rc not in ACQUIRE:
            return "MEASURE_MISMATCH"
    if status == "IDENTIFIED_NOT_POOLED":
        pass
    open_src = aact_src["n_matches"] > 0 or oa
    if status == "NOT_IDENTIFIED":
        return "IDENTIFICATION"
    if status == "IDENTIFIED_NOT_POOLED":
        return "SCREEN_OR_ELIGIBILITY"
    return "ACQUISITION" if open_src else "GENUINELY_UNAVAILABLE_OPEN"


NOT_YET_EXTRACTED = {"IDENTIFICATION", "SCREEN_OR_ELIGIBILITY"}


def closable_by(cls, aact_src, oa, upw=False, abstract_hit=False):
    """Best open source for a typed result, in the harness's own ladder order for a trial of this class.
    The PubMed abstract counts only for a trial the pipeline has NOT yet tried to extract (not identified, or
    screened out): for a declared-absent trial the abstract was already read and found wanting."""
    if cls in ("POOLED", "MEASURE_MISMATCH", "UNRESOLVED_IDENTITY", "SCOPE_MISMATCH"):
        return ""
    if aact_src["n_matches"] > 0:
        return "AACT_RESULTS"
    if oa:
        return "PMC_OA_FULLTEXT"
    if upw:
        return "UNPAYWALL_OA_COPY"
    if abstract_hit and cls in NOT_YET_EXTRACTED:
        return "PUBMED_ABSTRACT_OUTCOME"
    return "NONE_OPEN_PROBED"


_EFFECT = re.compile(r"\b(?:HR|RR|OR|hazard ratio|risk ratio|relative risk|odds ratio|rate ratio|mean difference|"
                     r"difference)\b[^.;]{0,60}?\d|\b\d+\s*/\s*\d+\b|\b\d+\s*\(\s*\d+(?:\.\d+)?\s*%\)", re.I)


def abstract_reports_outcome(abstract: str, kws: list[str]) -> str | None:
    """A sentence of the abstract that names the topic outcome AND carries a numeric result (an effect with a
    number, n/N, or n (x%)). Returns the sentence (the span) or None. A signal that the abstract rung is worth
    running -- not an extraction, and never an admitted number."""
    if not abstract or not kws:
        return None
    kre = re.compile("|".join(re.escape(k) for k in kws), re.I)
    for sent in re.split(r"(?<=[.;])\s+", abstract):
        if kre.search(sent) and _EFFECT.search(sent):
            return sent[:300]
    return None


def trial_abstracts(pmids, offline) -> dict:
    """PMID -> {abstract, doi} via efetch (batched 150, cached outputs/k_gap/trial_abstracts.json)."""
    cp = os.path.join(OUT, "trial_abstracts.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [] if offline else sorted({p for p in pmids if p.isdigit() and p not in cache})
    if todo:
        import time
        import xml.etree.ElementTree as ET
        from harness import http
        for i in range(0, len(todo), 150):
            chunk = todo[i:i + 150]
            try:
                x = http.get_text("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                                  {"db": "pubmed", "id": ",".join(chunk), "retmode": "xml"}, timeout=60)
            except Exception as exc:  # noqa: BLE001
                print("efetch failed", exc)
                continue
            for a in ET.fromstring(x).iter("PubmedArticle"):
                pm = a.find(".//PMID").text
                doi = next((e.text for e in a.iter("ArticleId") if e.get("IdType") == "doi" and e.text), "")
                cache[pm] = {"abstract": " ".join("".join(e.itertext()) for e in a.iter("AbstractText")), "doi": doi}
            time.sleep(0.4)
        _save_cache(cp, cache)
    return cache


def unpaywall_probe(dois, offline) -> dict:
    """DOI -> {is_oa, host_type, url} via Unpaywall (cached outputs/k_gap/unpaywall.json). Records where an OA
    copy is; fetching it is the adapter's job, not the probe's."""
    cp = os.path.join(OUT, "unpaywall.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [] if offline else sorted({d.lower() for d in dois if d and d.lower() not in cache})
    if todo:
        import time
        import urllib.parse
        from harness import http
        for d in todo:
            try:
                r = http.get_json("https://api.unpaywall.org/v2/" + urllib.parse.quote(d),
                                  {"email": "meta-harness@example.org"}, tries=2)
                b = r.get("best_oa_location") or {}
                cache[d] = {"is_oa": bool(r.get("is_oa")), "host_type": b.get("host_type"),
                            "url": b.get("url_for_pdf") or b.get("url"), "license": b.get("license")}
            except Exception as exc:  # noqa: BLE001
                cache[d] = {"error": str(exc)[:160]}
            time.sleep(0.15)
        _save_cache(cp, cache)
    return cache


def oa_probe(pmids: list[str], offline: bool) -> dict:
    """PMID -> {pmcid, is_oa} via NCBI idconv (batches of 150) + Europe PMC OA flag. Cached."""
    cp = os.path.join(OUT, "oa_probe.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = sorted({p for p in pmids if p.isdigit() and p not in cache})
    if todo and not offline:
        from harness import http
        for i in range(0, len(todo), 150):
            chunk = todo[i:i + 150]
            try:
                d = http.get_json("https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/",
                                  {"ids": ",".join(chunk), "format": "json", "tool": "meta-harness",
                                   "email": "meta-harness@example.org"})
            except Exception as exc:  # noqa: BLE001
                print("idconv failed", exc)
                continue
            for r in d.get("records", []):
                p = str(r.get("pmid") or "")
                if p:
                    cache[p] = {"pmcid": r.get("pmcid") or "", "doi": r.get("doi") or "", "is_oa": None}
        pmcs = sorted({v["pmcid"] for v in cache.values() if v.get("pmcid") and v.get("is_oa") is None})
        for i in range(0, len(pmcs), 40):
            chunk = pmcs[i:i + 40]
            q = " OR ".join(f"PMCID:{c}" for c in chunk)
            try:
                d = http.get_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                                  {"query": q, "format": "json", "resultType": "lite", "pageSize": 100})
            except Exception as exc:  # noqa: BLE001
                print("epmc failed", exc)
                continue
            flag = {r.get("pmcid"): r.get("isOpenAccess") == "Y" for r in d.get("resultList", {}).get("result", [])}
            for v in cache.values():
                if v.get("pmcid") in flag:
                    v["is_oa"] = flag[v["pmcid"]]
        os.makedirs(OUT, exist_ok=True)
        _save_cache(cp, cache)
    return cache


PROP = os.path.join(ROOT, "registry", "model_proposals", "comparator_members.json")
YEARS: dict = {}
PUBNCT: dict = {}
# PMID -> {"databank": [...], "abstract": [...]}: EVERY NCT the PubMed record lists (scripts/pubmed_databank_lookup.py);
# PUBNCT holds only the first, which is wrong evidence for a paper reporting several trials
DATABANK: dict = {}
# comparator references with no PMID, looked up by exact title + first author + year (outputs/k_gap/ref_title_pmid.json)
REF_PMID: dict = {}
# PubMed collective-author names of comparator reference PMIDs (scripts/pubmed_collective_lookup.py)
COLLECTIVE: dict = {}


def ref_title(ref) -> str:
    """The reference's title; when JATS carries none (a congress abstract in a <mixed-citation>: 'Ratanarat ...
    The effects of normal saline versus ... trial. 30th Annu Congr ESICM 2017'), the one sentence of its citation
    text that reads as a trial title ('The ... trial|study.'). '' when there is no such single sentence."""
    if ref.get("title"):
        return ref["title"]
    hits = re.findall(r"(The [a-z][^.]{20,300}?(?:trial|study))\.", ref.get("text") or "")
    return hits[0] if len(hits) == 1 else ""


def _ref_key(ref) -> str:
    return re.sub(r"[^a-z0-9]+", " ", ref_title(ref).lower()).strip() + "|" + (ref.get("first_author") or "").lower()


def load_ref_pmid() -> dict:
    p = os.path.join(OUT, "ref_title_pmid.json")
    return {_ref_key(v["ref"]): v for v in (_j(p).values() if os.path.exists(p) else []) if v.get("ref", {}).get("title")}
# PROPOSED on g1/noac for the k-gap lane to adopt or reject (the session channel to that lane was unavailable):
# acronym -> NCTs, read from a trial's OWN registration sentence in a held PubMed abstract
# ("... ROCKET AF ClinicalTrials.gov number, NCT00403767."). Used only after both AACT acronym steps fail.
SELF_REG: dict = {}
# every molecule any served topic names (set in main): the corroborator for an other-agent registration
SERVED_AGENTS: list = []


def served_agent_in(nct, idx):
    """True when the registration's AACT interventions name a molecule some served topic names (finerenone,
    empagliflozin...): the corroboration an any-agent acronym identity needs (IDREVIEW P1)."""
    ivs = (idx.get("interventions") or {}).get(nct) or []
    return bool(SERVED_AGENTS) and any(re.search(r"(?<![A-Za-z])" + re.escape(a) + r"(?![A-Za-z])", x, re.I)
                                       for x in ivs for a in SERVED_AGENTS)
_SELF_REG_RE = re.compile(r"\b([A-Z][A-Za-z0-9-]*(?: [A-Z0-9][A-Za-z0-9-]*){0,3}) ClinicalTrials\.gov (?:number|identifier),? (NCT\d{8})\b")


def self_registration_sentences(paths) -> dict:
    """{normalised acronym: sorted NCTs} from every held records.json given. Deterministic, offline, no model."""
    out = defaultdict(set)
    for path in sorted(paths):
        try:
            recs = _j(path)
        except (OSError, ValueError):
            continue
        for r in (recs.get("records") if isinstance(recs, dict) else recs) or []:
            for m in _SELF_REG_RE.finditer(str(r.get("abstract") or "")):
                out[k_gap.norm_acronym(m.group(1))].add(m.group(2))
    return {a: sorted(v) for a, v in out.items()}
TITLES: dict = {}
STORE = os.environ.get("K_GAP_AACT_STORE") or os.path.join(OUT, "_aact_store.json")
_AUTH_YR = re.compile(r"^([A-Z][A-Za-z'À-ſ‐-]+)[^0-9]{0,14}((?:19|20)\d\d)[a-z]?$")


def comparator_abstracts(pmids, offline) -> dict:
    """PMID -> PubMed abstract text for the comparators (cached outputs/k_gap/comparator_abstracts.json)."""
    cp = os.path.join(OUT, "comparator_abstracts.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    todo = [p for p in pmids if p not in cache]
    if todo and not offline:
        import xml.etree.ElementTree as ET
        from harness import http
        x = http.get_text("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                          {"db": "pubmed", "id": ",".join(todo), "retmode": "xml"})
        for a in ET.fromstring(x).iter("PubmedArticle"):
            cache[a.find(".//PMID").text] = " ".join("".join(e.itertext()) for e in a.iter("AbstractText"))
        _save_cache(cp, cache)
    return cache


def proposal_units(slug: str, agents: list[str], others: list[str] | None = None) -> list[dict]:
    if not os.path.exists(PROP):
        return []
    it = _j(PROP)["items"].get(slug) or {}
    v = it.get("verification") or {}
    agent_re = re.compile("|".join(re.escape(a) for a in agents), re.I) if agents else None
    other_re = re.compile("|".join(re.escape(a) for a in others), re.I) if others else None
    out = []
    for s in v.get("admitted", []):
        lab = s["label"].strip()
        toks = k_gap._label_tokens(lab)
        m = _AUTH_YR.match(lab)
        acr = toks["acronyms"] or ([lab] if re.match(r"^[A-Z][A-Z0-9-]{2,}", lab) else [])
        hit = bool(agent_re and agent_re.search(lab + " " + s["quote"]))
        oth = bool(other_re and other_re.search(lab + " " + s["quote"]))
        out.append({"table": "proposal:" + it.get("record_id", ""), "layout": "text", "label": lab,
                    "context": s["quote"], "rids": [], "cited": [], "ncts": toks["ncts"], "acronyms": acr,
                    "author": toks["author"] or (m.group(1) if m else ""), "year": toks["year"] or (m.group(2) if m else ""),
                    "agent_hit": hit, "drug_match": "DRUG_MATCH" if hit else ("OTHER_AGENT" if oth else "AGENT_IMPLICIT"),
                    "design_stated": s["design_stated"]})
    return out


ENUM_DIR = os.path.join(ROOT, "registry", "comparator_enumerations")


def held_norm(path, text=None):
    """Whitespace-normalised text of a held source (or of `text`). Markup sources (.xml/.html/.htm) are tag-stripped and
    unescaped first; plain text is NOT tag-stripped (a bare '<' in 'p<0.05' would swallow text up to the next '>')."""
    import html as _html
    raw = text if text is not None else open(path, encoding="utf-8", errors="replace").read()
    if path and path.lower().endswith((".xml", ".html", ".htm")):
        raw = _html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", raw).strip()


def enumeration_units(slug: str, agents: list[str], comparator_pmid: str | None = None) -> list[dict]:
    """A comparator set ENUMERATED from the comparator's own supplementary trial table (scripts/g1_binding_enumerate.py
    --write-input): one typed unit per trial, in the schema every other source uses. The unit's identity is the
    comparator's OWN reference-list entry (reference number -> CONFIRMED PMID by exact title + first author + year), its
    context is the row's arm lines verbatim, and the held source's sha256 rides on every unit. The file is refused
    whole when its source digest no longer matches the held text."""
    p = os.path.join(ENUM_DIR, slug + ".json")
    if not os.path.exists(p):
        return []
    e = _j(p)
    if comparator_pmid is not None and str(e.get("comparator_pmid")) != str(comparator_pmid):
        return []                                  # an enumeration of ANOTHER comparator never enumerates this one
    src = os.path.join(ROOT, e["source"]["path"])
    if not os.path.exists(src) or hashlib.sha256(open(src, "rb").read()).hexdigest() != e["source"]["sha256"]:
        return []
    held = held_norm(src)
    if not all(held_norm(None, line) in held for u in e.get("units") or [] for line in u["span"].split(" / ")):
        return []                                  # a span not in its held source refuses the whole enumeration
    agent_re = re.compile("|".join(re.escape(a) for a in agents), re.I) if agents else None
    out = []
    for u in e.get("units") or []:
        toks = k_gap._label_tokens(u["label"])
        m = _AUTH_YR.match(u["label"])
        out.append({"table": f"supplement:{e['source']['path']}", "layout": "text", "label": u["label"],
                    "context": u["span"], "rids": [u["ref"]],
                    "cited": [{"pmid": u["pmid"], "basis": f"comparator_supplement_ref_{u['ref']}_{u['identity']}"}],
                    "ncts": toks["ncts"], "acronyms": toks["acronyms"],
                    "author": toks["author"] or (m.group(1) if m else ""), "year": toks["year"] or (m.group(2) if m else ""),
                    "agent_hit": bool(agent_re and agent_re.search(u["span"])), "drug_match": "DRUG_MATCH",
                    "design_stated": None, "ref": u["ref"], "source_sha256": e["source"]["sha256"],
                    "enumeration": {"scope": u["scope"], "rule_id": u.get("rule_id"), "span": u["span"],
                                    "ref": u["ref"], "source": e["source"]["path"], "sha256": e["source"]["sha256"],
                                    "enumerated_from": e.get("enumerated_from")}})
    return out


def set_state(chosen):
    """The comparator-set state from the source that resolved it."""
    return {"JATS_TABLE": "TABLE_ENUMERATED", "SUPPLEMENT_ENUMERATION": "ENUMERATED",
            "MODEL_PROPOSAL_GATED": "PROPOSAL_ENUMERATED_GATED",
            "REFERENCE_SEED": "REFERENCE_SEED_CANDIDATES"}.get(chosen, "NOT_ENUMERABLE_OPEN")


def self_names(acr, title, abstract) -> bool:
    """Does a record NAME ITSELF by this acronym -- in its title, or defined in parentheses in its abstract?"""
    core = k_gap.fold_dashes(re.sub(r"\s+(?:(?:19|20)\d\d|\d{1,3})$", "", (acr or "").strip()))
    core = re.sub(r"(?<=[A-Za-z])(?:19|20)\d\d$", "", core)
    if len(k_gap.norm_acronym(core)) < 4:
        return False
    pat = re.escape(core).replace("\\-", "[-\\s]?").replace("\\ ", "[-\\s]?")
    if re.search(rf"(?<![A-Za-z0-9]){pat}(?![A-Za-z0-9])", k_gap.fold_dashes(title or ""), re.I):
        return True
    # exactly "(ACRONYM)": a parenthesised LIST "(CORE, CORP)" is a citation of several trials, not a definition
    return bool(re.search(rf"\(\s*{pat}\s*\)", k_gap.fold_dashes(abstract or ""), re.I))


def acronym_in_our_records(acronyms, recs, families):
    """An acronym-only label (ROCKET AF, HARMONY, CORE) resolved against OUR OWN held records: a record names ITSELF
    by an acronym in its TITLE, or DEFINES it in parentheses in its abstract ('... Stroke and Embolism Trial in Atrial
    Fibrillation (ROCKET AF)'). A bare mention does not count -- other trials' abstracts cite landmark trials in
    passing. Resolves only when every self-naming record falls in ONE of our trial families."""
    rep_to_fam = {}
    for f in families:
        for r in f["reports"]:
            rep_to_fam[r] = f
    for a in acronyms:
        core = k_gap.fold_dashes(re.sub(r"\s+(?:(?:19|20)\d\d|\d{1,3})$", "", a.strip()))
        if len(k_gap.norm_acronym(core)) < 4:
            continue
        pat = re.escape(core).replace("\\-", "[-\\s]?").replace("\\ ", "[-\\s]?")
        tre = re.compile(rf"(?<![A-Za-z0-9]){pat}(?![A-Za-z0-9])")
        dre = re.compile(rf"\(\s*{pat}\s*[),;]")
        hits = {rid for rid, title, abstract in recs
                if tre.search(k_gap.fold_dashes(title or "")) or dre.search(k_gap.fold_dashes(abstract or ""))}
        fams = {rep_to_fam[h]["family_id"] for h in hits if h in rep_to_fam}
        if hits and len(fams) == 1 and all(h in rep_to_fam for h in hits):
            return rep_to_fam[next(iter(hits))], a, sorted(hits)
    return None, None, []


def family_by_acronym(acronyms, families):
    """Our own trial family whose registered acronym equals, or is a >=5-char prefix-extension of, the unit's
    acronym (RALES == RALES; HARMONY -> 'HARMONY Outcomes'). Our families are a small, topic-scoped set, so a
    prefix here cannot wander into an unrelated trial the way a registry-wide prefix search would."""
    for a in acronyms:
        na = k_gap.norm_acronym(a)
        if len(na) < 4:
            continue
        hits = [f for f in families if any(fa == na or (len(na) >= 5 and fa.startswith(na)) for fa in f["acronyms"])]
        if len(hits) == 1:
            return hits[0]
    return None


_COMP_DEFAULT = ["placebo", "sham", "usual care", "standard care", "standard of care", "no treatment", "control"]


_PLACEBO_TYPES = {"PLACEBO_COMPARATOR", "SHAM_COMPARATOR", "NO_INTERVENTION"}


def comparator_scope(ncts, idx, topic):
    """Does the trial's registered design contain the topic's registered comparator? A comparator meta can
    include active-comparator trials (finerenone vs EPLERENONE in an MRA-vs-placebo topic); such a trial is a
    SCOPE difference, not a gap. Read from the ARM TYPE (design_groups.group_type), not intervention names: a
    double-dummy active-comparator trial lists 'placebo' among its interventions. For a placebo topic the
    comparator is present iff some arm is PLACEBO/SHAM/NO_INTERVENTION; for an active-comparator topic iff some
    arm's title names a comparator term. UNKNOWN when no NCT resolved or AACT holds no arms."""
    terms = list((topic.get("include") or {}).get("comparator_any") or []) or _COMP_DEFAULT
    groups = [g for n in ncts for g in (idx.get("design_groups") or {}).get(n, [])]
    if not groups:
        return {"state": "UNKNOWN"}
    placebo_topic = any(t.lower() in ("placebo", "sham", "control", "no treatment", "usual care") for t in terms)
    types = [g["group_type"].upper() for g in groups]
    tre = re.compile("|".join(re.escape(t) for t in terms), re.I)
    # placebo topic: the arm TYPE alone decides ('Eplerenone [25 mg] + Placebo' is ARTS-HF's ACTIVE arm, so a
    # title match on 'placebo' would call a double-dummy active-comparator trial placebo-controlled)
    present = any(t in _PLACEBO_TYPES for t in types) if placebo_topic else any(tre.search(g["title"]) for g in groups)
    st = "COMPARATOR_IN_REGISTRY_ARMS" if present else "COMPARATOR_NOT_IN_REGISTRY_ARMS"
    return {"state": st, "arm_types": sorted(set(types)), "terms": terms[:6]}


def pubmed_acronym(acr, agents, offline):
    """Last-resort identity for an acronym-only label (pre-registry trials): PubMed acronym[tiab] + topic agent +
    RCT publication type. One hit -> that PMID; several -> the EARLIEST (lowest PMID), with the hit count
    recorded in the basis so a reader sees it was a choice among n. Cached for replay.
    CHANGED 2026-09-29: several hits now resolve NOTHING. 'Earliest of n' mapped HARMONY (Outcomes) to a
    HARMONY-3 report (earliest of 14) -- a choice among n reports of a programme is not an identity."""
    cp = os.path.join(OUT, "pubmed_acronym.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    ag = " OR ".join(f'"{a}"[tiab]' for a in agents)
    acr = re.sub(r"(?<=[A-Za-z])(?:19|20)\d\d$", "", acr)       # 'RALES1999' -> 'RALES'
    q = f'"{acr}"[tiab] AND ({ag}) AND randomized controlled trial[pt]'
    if q not in cache and not offline:
        import time
        from harness import http
        try:
            d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                              {"db": "pubmed", "term": q, "retmode": "json", "retmax": 50})
            cache[q] = d.get("esearchresult", {}).get("idlist", [])
        except Exception as exc:  # noqa: BLE001
            cache[q] = {"error": str(exc)[:200]}
        _save_cache(cp, cache)
        time.sleep(0.4)
    ids = cache.get(q)
    if isinstance(ids, list) and len(ids) == 1:
        return ids[0], q, 1
    return None, q, len(ids) if isinstance(ids, list) else 0


def pubmed_acronym_ids(acr, agents, offline):
    """All PMIDs for the acronym query pubmed_acronym runs (same cached query, same bytes)."""
    pubmed_acronym(acr, agents, offline)
    cp = os.path.join(OUT, "pubmed_acronym.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    acr2 = re.sub(r"(?<=[A-Za-z])(?:19|20)\d\d$", "", acr)
    ag = " OR ".join(f'"{a}"[tiab]' for a in agents)
    ids = cache.get(f'"{acr2}"[tiab] AND ({ag}) AND randomized controlled trial[pt]')
    return ids if isinstance(ids, list) else []


WIDE_DESIGN = ('(randomized controlled trial[pt] OR controlled clinical trial[pt] OR clinical trial[pt] OR '
               'randomi*[tiab] OR randomly[tiab])')


def author_year_wide_query(author, year, agents):
    """The widened design filter: a pre-registry trial indexed only as 'Controlled Clinical Trial' whose abstract says
    'randomly' (Nestler 1998, NEJM) is invisible to the RCT filter. Consulted only when the strict query finds nothing;
    design is decided later by the screen, never by this query."""
    ag = " OR ".join(f'"{a}"[tiab]' for a in agents)
    return f"{author}[1au] AND {year}[dp] AND ({ag}) AND {WIDE_DESIGN}"


def _esearch_cached(q, cache, offline):
    if q not in cache and not offline:
        import time
        from harness import http
        try:
            d = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                              {"db": "pubmed", "term": q, "retmode": "json", "retmax": 5})
            cache[q] = d.get("esearchresult", {}).get("idlist", [])
        except Exception as exc:  # noqa: BLE001
            cache[q] = {"error": str(exc)[:200]}
        time.sleep(0.4)
        return True
    return False


def pubmed_author_year(author, year, agents, offline):
    """PMID for 'Author Year' + topic agent via NCBI ESearch -- admitted only when EXACTLY one hit.
    The strict RCT-filtered query first; only when it returns NO hit (an empty list, never an error), the widened design
    filter (author_year_wide_query). Queries and answers are cached (outputs/k_gap/pubmed_author_year.json) so a rerun
    replays them."""
    cp = os.path.join(OUT, "pubmed_author_year.json")
    cache = _j(cp) if os.path.exists(cp) else {}
    ag = " OR ".join(f'"{a}"[tiab]' for a in agents)
    q = f"{author}[1au] AND {year}[dp] AND ({ag}) AND (randomized controlled trial[pt] OR randomi*[tiab])"
    dirty = _esearch_cached(q, cache, offline)
    ids = cache.get(q)
    if ids == []:
        q = author_year_wide_query(author, year, agents)
        dirty = _esearch_cached(q, cache, offline) or dirty
        ids = cache.get(q)
    if dirty:
        _save_cache(cp, cache)            # atomic, union with disk (integrate: parallel trackers share this cache)
    return (ids[0] if isinstance(ids, list) and len(ids) == 1 else None), q, ids


def main(argv=None):
    argv = argv or sys.argv[1:]
    offline = "--offline" in argv
    global _OFFLINE
    _OFFLINE = offline
    only = {a.split("=", 1)[1] for a in argv if a.startswith("--only=")}
    write = "--no-write" not in argv
    log = lambda m: print(m, flush=True)  # noqa: E731
    os.makedirs(OUT, exist_ok=True)
    topics = []
    for f in sorted(glob.glob(os.path.join(ROOT, "cache", "*", "comparators.json"))):
        slug = os.path.basename(os.path.dirname(f))
        c = _j(f)[0]
        m = re.search(r"PMID (\d+)", c.get("citation", ""))
        topics.append((slug, m.group(1) if m else str(c["id"]), c.get("citation", "")))
    store = k_gap.AactStore(STORE)
    store.build_maps(log=log)
    abstracts = comparator_abstracts([t[1] for t in topics], offline)
    per = {}
    other_all = sorted({a for t in topics for a in molecule_names(_j(os.path.join(ROOT, "topics", t[0] + ".json")))},
                       key=str.lower)
    SERVED_AGENTS[:] = other_all
    # --only=<slug>: rebuild ONE topic's rows (its comparator changed) and keep every other topic's rows as they are;
    # the other-agent list above still spans all topics
    if only:
        topics = [t for t in topics if t[0] in only]
    for slug, cpmid, cit in topics:
        topic = _j(os.path.join(ROOT, "topics", slug + ".json"))
        agents = topic_agents(topic)
        others = [a for a in other_all if not re.search("|".join(re.escape(x) for x in agents), a, re.I)]
        inc, parsed = comparator_units(slug, cpmid, agents, others)
        try:
            text, ref = k_gap.held_text(slug, DATE)
        except Exception as exc:  # noqa: BLE001
            text, ref = "", f"UNREADABLE: {exc}"
        held = {"ref": ref, **k_gap.held_text_identity(abstracts.get(cpmid, ""), text)}
        cands = [("JATS_TABLE", inc)]
        eu = enumeration_units(slug, agents, cpmid)
        if eu:
            # a TYPED enumeration (registry/comparator_enumerations: span-verified, digest-pinned, the trial set of the
            # comparator's RESULT) takes precedence over parsing its tables: statins 32529863's Table 1 lists all 16
            # trials (primary + secondary prevention), while its primary-prevention result pools 7 (refs 29, 35-40)
            cands.insert(0, ("SUPPLEMENT_ENUMERATION", {"state": "ENUMERATED", "units": eu,
                                                        "tables_used": [eu[0]["table"]],
                                                        "enumerated_from": eu[0]["enumeration"]["enumerated_from"]}))
        if held["state"] == "NAMED_ARTICLE":
            pu = proposal_units(slug, agents, others)
            if pu:
                cands.append(("MODEL_PROPOSAL_GATED", {"state": "PROPOSAL_GATED", "units": pu,
                                                       "tables_used": [pu[0]["table"]]}))
        # identity reads the reference list from the PMCID copy when the kgap JATS is absent (metformin: PMC6915832
        # held since 2026-09-15, yet every row resolved against NO reference list)
        id_parsed = parsed or identity_refs(cpmid)
        per[slug] = {"topic": topic, "agents": agents, "others": others, "parsed": parsed, "id_parsed": id_parsed,
                     "ours": ours(slug),
                     "comparator_pmid": cpmid, "citation": cit, "held": held, "cands": cands, "tried": []}

    def prep(P, units):
        need = set()
        for u in units:
            if not u["cited"] and P["id_parsed"] and u["layout"] == "text":
                rs = k_gap.refs_by_number(u["label"], P["id_parsed"]["refs"])
                if rs and all(r.get("pmid") for r in rs):
                    u["cited"] = [{"pmid": r["pmid"], "doi": r.get("doi"), "basis": "label_ref_number"} for r in rs]
            if not u["cited"] and not u["ncts"] and u["author"] and u["year"]:
                refhit = None
                if P["id_parsed"]:
                    hits = [r for r in P["id_parsed"]["refs"].values() if r.get("pmid") and
                            r.get("first_author", "").lower() == u["author"].lower() and r.get("year") == u["year"]]
                    refhit = hits[0]["pmid"] if len(hits) == 1 else None
                if refhit:
                    u["cited"] = [{"pmid": refhit, "basis": "author_year_ref_list"}]
                else:
                    pm, q, ids = pubmed_author_year(u["author"], u["year"], P["agents"], offline)
                    u["pubmed_query"] = {"q": q, "ids": ids}
                    if pm:
                        u["cited"] = [{"pmid": pm, "basis": "pubmed_author_year_single_hit"}]
            for c in u["cited"]:
                need |= {n for n, _t in store.d["pmid"].get(c.get("pmid") or "", [])}
            need |= set(u["ncts"])
            # index the registrations the identity chain may name: the unit's tokens AND its identity tokens
            # ('FIGARO-DKD2022' -> 'FIGARO-DKD'), by acronym and by brief title
            id_acr = k_gap.identity_tokens(u["label"])["acronyms"] if u.get("layout") in ("row", "column", "text") else []
            for a in list(u["acronyms"]) + id_acr:
                need |= set(store.d["acr"].get(k_gap.norm_acronym(a), [])[:25])
                need |= set((store.d.get("acr_title") or {}).get(k_gap.norm_acronym(a), [])[:25])
        return need

    def resolve_rows(slug, P, units, source):
        tidx = store.index(P["agents"])
        P.setdefault("link_audit", {})[source] = distrust_shifted_tables(units, tidx)
        P.setdefault("marker_offsets", {})[source] = learn_marker_offsets(units, P["id_parsed"])
        agents_re = re.compile("|".join(re.escape(a) for a in P["agents"]), re.I)
        out = []
        # a SUB-ROW of a study (statins: 'Statin used group in QRISK 10-19% (n = 6438)' under Gitsels 2016) is not a
        # trial unit: no identity token at all + a group size, in a table that has real trial rows. Listed, never dropped
        # silently (topic 'not_a_trial_units').
        trial_rows_in = Counter(x["table"] for x in units if subgroup_row(x) is None)
        for u in units:
            why = subgroup_row(u)
            if why and trial_rows_in[u["table"]]:
                P.setdefault("not_a_trial_units", []).append({"table": u["table"], "label": u["label"], "why": why})
                continue
            ident = resolve_unit(u, P["id_parsed"], tidx, agents_re, years=YEARS,
                                 our_fams={f["family_id"] for f in P["ours"]["families"]})
            ident["basis"] += [c["basis"] for c in u["cited"] if c.get("basis")]
            ident = consolidate_report_family(ident, P["ours"]["families"])
            if ident["pmids"] and not ident["ncts"]:
                # the cited PMID is a second record of a paper we HOLD (same title): EMPA-REG's NEJM article has two
                # PubMed records (26378978, 26981940); the comparator cites the other one. Exact normalised title only.
                keys = {_title_key(TITLES.get(p, "")) for p in ident["pmids"] if len(_title_key(TITLES.get(p, ""))) >= 30}
                same = {rid for rid, title, _ab in P["ours"]["records_text"] if _title_key(title) in keys}
                r2f = {r: f for f in P["ours"]["families"] for r in f["reports"]}
                fams = {r2f[x]["family_id"]: r2f[x] for x in same if x in r2f}
                if len(fams) == 1:
                    f = next(iter(fams.values()))
                    if f["family_id"].startswith("NCT"):
                        ident["ncts"] = [f["family_id"]]
                    ident["pmids"] = sorted(set(ident["pmids"]) | {x for x in same if x in f["reports"]})
                    ident["basis"].append(f"cited_title_equals_our_record:{','.join(sorted(same))[:40]}")
            if not ident["pmids"] and not ident["ncts"] and u["acronyms"]:
                fam_rec, acr_used, hits = acronym_in_our_records(u["acronyms"], P["ours"]["records_text"],
                                                                 P["ours"]["families"])
                if fam_rec:
                    ident["ncts"] = [fam_rec["family_id"]] if fam_rec["family_id"].startswith("NCT") else []
                    ident["pmids"] = sorted(x for x in fam_rec["reports"] if x.isdigit())
                    ident["basis"].append(f"acronym_self_named_in_our_records:{acr_used}:{','.join(hits[:3])}")
            if not ident["pmids"] and not ident["ncts"] and u["acronyms"]:
                # PubMed's reports of the acronym (RCT-typed, topic drug) INTERSECTED with the families we hold: PubMed
                # supplies the trial's reports, our corpus disambiguates. ROCKET AF: many PubMed reports, one family ours.
                ids = pubmed_acronym_ids(u["acronyms"][0], P["agents"], offline)
                r2f = {r: f for f in P["ours"]["families"] for r in f["reports"]}
                # the held record must NAME ITSELF by the acronym (title, or defined in parentheses): a held paper
                # that merely CITES the trial matched the tiab query too -- CORE resolved to a 2024 paper citing it
                named = {rid for rid, title, ab in P["ours"]["records_text"]
                         if self_names(u["acronyms"][0], title, ab)}
                fams = {r2f[i]["family_id"]: r2f[i] for i in ids if i in r2f and i in named}
                if len(fams) == 1:
                    f = next(iter(fams.values()))
                    ident["ncts"] = [f["family_id"]] if f["family_id"].startswith("NCT") else []
                    ident["pmids"] = sorted(x for x in f["reports"] if x.isdigit())
                    ident["basis"].append(f"pubmed_acronym_x_our_family:{u['acronyms'][0]}:{len(ids)}_hits")
            if not ident["pmids"] and not ident["ncts"]:
                fam_hit = family_by_acronym(u["acronyms"], P["ours"]["families"])
                if fam_hit:
                    ident["ncts"] = [fam_hit["family_id"]] if fam_hit["family_id"].startswith("NCT") else []
                    ident["pmids"] = sorted(x for x in fam_hit["reports"] if x.isdigit())
                    ident["basis"].append("acronym_our_family:" + fam_hit["family_id"])
                elif u["acronyms"] and u["layout"] == "text":
                    # only for a label the model QUOTED as an included study -- never a table row (the noac IPD
                    # baseline table's 'CHADS2 score' row resolved to a RE-LY sub-analysis through this path)
                    pm, q, n_hits = pubmed_acronym(u["acronyms"][0], P["agents"], offline)
                    u["pubmed_query"] = {"q": q, "n": n_hits}
                    if pm:
                        ident["pmids"] = [pm]
                        ident["basis"].append("pubmed_acronym_single_hit")
                        ident["ncts"] = [n for n, _t in tidx["pmid_nct"].get(pm, [])]
            reg = registry_agent(ident["ncts"], tidx)
            scope = comparator_scope(ident["ncts"], tidx, P["topic"])
            # the unit's own text naming our agent wins; else the REGISTRY decides when an NCT resolved; the
            # text "names another served topic's molecule" check applies only when the registry cannot speak.
            if u["agent_hit"] or reg:
                drug = "DRUG_MATCH"
            elif reg is False or u["drug_match"] == "OTHER_AGENT":
                drug = "OTHER_AGENT"
            else:
                drug = "AGENT_UNCONFIRMED"
            if not ident["pmids"] and not ident["ncts"]:
                # identified BY CITATION (marker/link -> one reference) but that reference is not in PubMed: the trial
                # is known, it is just not findable by a PubMed/registry search -- a different gap from "who is this?"
                status = ("IDENTIFIED_NOT_INDEXED" if any(b.startswith("ref_not_in_pubmed") for b in ident["basis"])
                          else "UNRESOLVED")
                fam, absent = None, None
            else:
                status, fam, absent = match_ours(ident, u["acronyms"], P["ours"])
                if status in ("NOT_IDENTIFIED", "IDENTIFIED_NOT_POOLED") and \
                        scope["state"] == "COMPARATOR_NOT_IN_REGISTRY_ARMS":
                    status = "SCOPE_MISMATCH"
            src = aact_source(ident["ncts"], tidx, outcome_keywords(P["topic"]), P["ours"]["estimand"])
            out.append({"slug": slug, "comparator_pmid": P["comparator_pmid"], "unit_source": source,
                        "table": u["table"], "layout": u["layout"], "label": u["label"], "context": u["context"][:300],
                        "drug": drug, "pmids": ident["pmids"], "ncts": ident["ncts"], "identity_basis": ident["basis"],
                        "pubmed_query": u.get("pubmed_query"), "design_stated": u.get("design_stated"),
                        "cited_doi": [c.get("doi") for c in u["cited"] if c.get("doi")],
                        "cited_pmids": sorted({c["pmid"] for c in u["cited"] if c.get("pmid")}),
                        "status": status, "family_id": fam["family_id"] if fam else "",
                        "family_eligibility": fam["eligibility"] if fam else "",
                        "declared_absent": absent, "aact": src, "comparator_scope": scope,
                        "study": {n: tidx["study"].get(n) for n in ident["ncts"]},
                        **({"enumeration": u["enumeration"]} if u.get("enumeration") else {})})
        return out

    def n_elig(rs):
        return sum(r["drug"] != "OTHER_AGENT" and r["status"] not in ("UNRESOLVED", "DUPLICATE_UNIT") for r in rs)

    # round 1: every held candidate source for every topic (one batched AACT fact scan)
    need = set()
    for P in per.values():
        for _src, inc in P["cands"]:
            need |= prep(P, inc["units"])
        o = P["ours"]
        need |= {x for x in o["pooled_fam"] | set(o["absent"]) if x.startswith("NCT")}
    store.ensure_ncts(need, log=log)
    store.ensure_design_groups(log=log)
    store.ensure_background_refs(need, log=log)
    cited = {c.get("pmid") for P in per.values() for _src, inc in P["cands"] for u in inc["units"]
             for c in u["cited"] if c.get("pmid")}
    YEARS.update(pub_years(cited, offline))
    PUBNCT.update(pubmed_ncts(cited, offline))
    _dbp = os.path.join(OUT, "pubmed_databank_ncts.json")
    if os.path.exists(_dbp):
        DATABANK.update({p: v for p, v in _j(_dbp).items() if "databank" in v})
    TITLES.update(pubmed_titles_of(cited, offline))
    SELF_REG.update(self_registration_sentences(glob.glob(os.path.join(ROOT, "cache", "*", "records.json"))))
    REF_PMID.update(load_ref_pmid())
    cp_ = os.path.join(OUT, "pubmed_collective.json")
    COLLECTIVE.update(_j(cp_) if os.path.exists(cp_) else {})
    store.ensure_ncts({n for v in SELF_REG.values() for n in v}, log=log)
    store.ensure_ncts({n for n in PUBNCT.values() if n}, log=log)
    store.ensure_registration_dates({n for p in cited for n, _t in store.d["pmid"].get(p, [])}, log=log)
    for slug, P in per.items():
        P["chosen"] = None
        for src, inc in P["cands"]:
            rs = resolve_rows(slug, P, inc["units"], src)
            P["tried"].append({"source": src, "units": len(rs), "drug_specific_resolved": n_elig(rs)})
            if P["chosen"] is None and n_elig(rs):
                P["chosen"], P["rows"], P["inc"] = src, rs, inc
    # round 2: reference seeding, only where no held source resolved a drug-specific trial
    need = set()
    for slug, P in per.items():
        if P["chosen"]:
            continue
        er = k_gap.fetch_epmc_references(P["comparator_pmid"], DATE, offline)
        pt = k_gap.pubmed_pubtypes([r["pmid"] for r in er["refs"]], os.path.join(OUT, "pubmed_pubtypes.json"), offline) \
            if er["refs"] else {}
        su = k_gap.reference_seed_units(er["refs"], pt, P["agents"])
        P["seed"] = {"state": "REFERENCE_SEEDED_CANDIDATES", "units": su, "tables_used": [er.get("file", "")],
                     "refs_held": len(er["refs"])}
        need |= prep(P, su)
    store.ensure_ncts(need, log=log)
    store.ensure_design_groups(log=log)
    store.ensure_background_refs(need, log=log)
    cited2 = {c.get("pmid") for P in per.values() if P.get("seed") for u in P["seed"]["units"] for c in u["cited"]
              if c.get("pmid")}
    YEARS.update(pub_years(cited2, offline))
    PUBNCT.update(pubmed_ncts(cited2, offline))
    TITLES.update(pubmed_titles_of(cited2, offline))
    store.ensure_ncts({n for n in PUBNCT.values() if n}, log=log)
    store.ensure_registration_dates({n for p in cited2 for n, _t in store.d["pmid"].get(p, [])}, log=log)
    rows = []
    for slug, P in per.items():
        if not P["chosen"] and P.get("seed"):
            rs = resolve_rows(slug, P, P["seed"]["units"], "REFERENCE_SEED")
            P["tried"].append({"source": "REFERENCE_SEED", "units": len(rs), "drug_specific_resolved": n_elig(rs),
                               "refs_held": P["seed"]["refs_held"]})
            if n_elig(rs):
                P["chosen"], P["rows"], P["inc"] = "REFERENCE_SEED", rs, P["seed"]
        if not P["chosen"]:
            P["rows"], P["inc"] = [], {"state": "NONE", "tables_used": []}
        P["unit_source"] = P["chosen"] or "NONE"
        rows += P["rows"]
    oa = oa_probe([p for r in rows for p in r["pmids"] if r["status"] != "POOLED"], offline)
    notpooled = [r for r in rows if r["status"] not in ("POOLED", "UNRESOLVED")]
    abst = trial_abstracts([p for r in notpooled for p in r["pmids"][:4]], offline)
    for r in notpooled:
        r["dois"] = sorted({d for d in r["cited_doi"] if d} | {abst[p]["doi"] for p in r["pmids"][:4]
                                                                if p in abst and abst[p].get("doi")})
    upw = unpaywall_probe([d for r in notpooled for d in r.get("dois", [])], offline)
    for r in rows:
        oas = [oa.get(p, {}) for p in r["pmids"]]
        r["pmc_oa"] = [{"pmid": p, **oa.get(p, {})} for p in r["pmids"] if oa.get(p, {}).get("pmcid")]
        is_oa = any(v.get("is_oa") for v in oas)
        r["unpaywall"] = [{"doi": d, **upw.get(d.lower(), {})} for d in r.get("dois", []) if upw.get(d.lower(), {}).get("is_oa")]
        kws = outcome_keywords(per[r["slug"]]["topic"])
        r["abstract_outcome_span"] = next((sp for p in r["pmids"][:4]
                                           for sp in [abstract_reports_outcome((abst.get(p) or {}).get("abstract", ""), kws)]
                                           if sp), None)
        r["gap_class"] = classify(r["status"], r["declared_absent"], None, r["aact"], is_oa or bool(r["unpaywall"]))
        r["closable_by"] = closable_by(r["gap_class"], r["aact"], is_oa, bool(r["unpaywall"]),
                                       bool(r["abstract_outcome_span"]))
    mark_duplicate_units(rows)
    topics_out = []
    for slug, cpmid, cit in topics:
        P = per[slug]
        tr = [r for r in rows if r["slug"] == slug]
        elig = [r for r in tr if r["drug"] != "OTHER_AGENT" and r["status"] not in ("UNRESOLVED", "DUPLICATE_UNIT")]
        state = set_state(P["chosen"])
        topics_out.append({
            "slug": slug, "comparator_pmid": cpmid, "comparator": cit[:160], "unit_source": P["unit_source"],
            "comparator_set_state": state, "enumerated_from": P["inc"].get("enumerated_from"), "held_text": P["held"], "tables_used": P["inc"]["tables_used"],
            "sources_tried": P["tried"], "link_audit": P.get("link_audit", {}),
            "our_k": P["ours"]["k"], "comparator_units": len(tr), "drug_specific_resolved": len(elig),
            "other_agent": sum(r["drug"] == "OTHER_AGENT" for r in tr),
            "unresolved_labels": sum(r["status"] == "UNRESOLVED" for r in tr),
            "not_a_trial_units": P.get("not_a_trial_units", []),
            "pooled_of_theirs": sum(r["gap_class"] == "POOLED" for r in elig),
            "missing": sum(r["gap_class"] != "POOLED" for r in elig),
            "by_class": dict(Counter(r["gap_class"] for r in elig if r["gap_class"] != "POOLED")),
            "by_source": dict(Counter(r["closable_by"] for r in elig if r["closable_by"])),
            "missing_trials": [{"label": r["label"], "pmids": r["pmids"], "ncts": r["ncts"], "gap_class": r["gap_class"],
                                "closable_by": r["closable_by"]} for r in elig if r["gap_class"] != "POOLED"],
        })
    out = {"generated": DATE, "aact_snapshot": store.snap, "topics": topics_out, "trials": rows}
    if not write:
        return out
    if only:
        prev = _j(os.path.join(OUT, "k_gap_table.json"))
        keep_t = [t for t in prev.get("topics") or [] if t.get("slug") not in only]
        keep_r = [r for r in prev.get("trials") or [] if r.get("slug") not in only]
        out = dict(prev, topics=sorted(keep_t + topics_out, key=lambda t: t["slug"]), trials=keep_r + rows)
        rows = out["trials"]
    with open(os.path.join(OUT, "k_gap_table.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, default=list)
    cols = ["slug", "comparator_pmid", "unit_source", "label", "drug", "status", "gap_class", "closable_by", "pmids",
            "ncts", "identity_basis", "family_id", "family_eligibility", "declared_reason_code", "aact_results_posted",
            "aact_outcome_match", "aact_param_type", "aact_time_frame", "aact_population", "pmc_oa", "table"]
    with open(os.path.join(OUT, "k_gap_table.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            m = r["aact"]["outcome_matches"][0] if r["aact"]["outcome_matches"] else {}
            w.writerow([r["slug"], r["comparator_pmid"], r["unit_source"], r["label"], r["drug"], r["status"],
                        r["gap_class"], r["closable_by"], ";".join(r["pmids"]), ";".join(r["ncts"]),
                        ";".join(r["identity_basis"]), r["family_id"], r["family_eligibility"],
                        (r["declared_absent"] or {}).get("reason_code", ""), r["aact"]["results_posted"],
                        m.get("title", ""), m.get("param_type", ""), m.get("time_frame", ""), m.get("population", "")[:160],
                        ";".join(x["pmcid"] for x in r["pmc_oa"] if x.get("is_oa")), r["table"]])
    return out


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    o = main()
    for t in o["topics"]:
        print(f"{t['slug'][:38]:38s} state={t['comparator_set_state'][:14]:14s} ourk={t['our_k']} units={t['comparator_units']:3d} "
              f"elig={t['drug_specific_resolved']:3d} pooled={t['pooled_of_theirs']:2d} miss={t['missing']:2d} "
              f"other={t['other_agent']:2d} unres={t['unresolved_labels']:2d} {t['by_class']} {t['by_source']}")
