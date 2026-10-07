"""OPEN SOURCES beyond PMC / Unpaywall / regulators: typed routes for G1 trial acquisition (Mahmood 7 Oct: "also any
other open access sources but use in reproducible ai"). Free to read, no account, no data-use agreement, no terms
accepted on anyone's behalf. Every route: a typed source record (url, licence of record, sha256 of the bytes and of the
typed text), deterministic reading first, a model only on text whose licence allows it, the SAME gates for admission.

Routes
  OPEN_LOCATION  a copy of the trial's OWN report found by OpenAlex (or Semantic Scholar's openAccessPdf) when PMC and
                 Unpaywall hold none. Licence of record: the HOST page's own machine-readable licence -- <meta
                 name="cc_license_url">, <meta name="DC.rights" | "dcterms.license" | "citation_license">, <link|a
                 rel="license"> naming a creativecommons.org licence -- never the discovery index's field (OpenAlex
                 called REMAP-CAP's JAMA copy cc-by; JAMA answered with a bot challenge). CC -> shown to a model (the
                 record_licence guard checks it against THIS record) and read deterministically; anything else is
                 recorded NOT_OPEN and its text is not held. Identity: the PDF must carry the report's own title words.
  EUCTR          the EU Clinical Trials Register results page for the trial's EudraCT number (AACT id_information, or
                 an EU CTR search on the NCT that returns exactly ONE trial). Licence of record: THIRD_PARTY_SPONSOR --
                 the register defers to EMA's legal notice, whose reproduction permission "does not apply to content
                 supplied by third parties", and results are entered by the sponsor. NEVER shown to a model: read only by
                 parse_euctr -> euctr_registry (the AACT registry shape) and admitted only through the AACT binding gates.
  CTIS           the EU CTIS public record (euclinicaltrials.eu public API) for a CTIS number in the trial's secondary
                 ids: results recorded when posted (state only; a posted summary is a sponsor document, typed-only).

A bot challenge (Cloudflare 'Just a moment...', cf-chl, captcha) is recorded BOT_CHALLENGE: never retried, never
solved. Records: registry/open_sources.json keyed by url; texts: outputs/k_gap/_open/ (not committed; the digest is).
"""
from __future__ import annotations

import datetime
import hashlib
import html as _html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]

SOURCES = os.path.join(ROOT, "registry", "open_sources.json")
TEXTS = os.path.join(ROOT, "outputs", "k_gap", "_open")
UA = "meta-harness/1.0 (reproducible-ma; mailto:meta-harness@example.org)"
EUCTR = "https://www.clinicaltrialsregister.eu"
CTIS_API = "https://euclinicaltrials.eu/ctis-public-api/retrieve/"
THIRD_PARTY = "THIRD_PARTY_SPONSOR"            # EMA legal notice: permissions do not apply to third-party content
MIN_TEXT = 3000                                # a shorter PDF text layer is no report (cover page, error page)
VERSION_ORDER = {"publishedVersion": 0, "acceptedVersion": 1, "submittedVersion": 2}

_CHALLENGE = re.compile(r"<title>\s*Just a moment|cf-chl|challenge-platform|cf_chl_opt|captcha|Attention Required", re.I)


# ---------------------------------------------------------------------------------------------------------- fetching

def fetch(url, timeout=60, accept=None):
    """(status, content_type, body bytes, final_url). One attempt: a refusal is a result, never retried around."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, **({"Accept": accept} if accept else {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode(), r.headers.get("Content-Type") or "", r.read(), r.geturl()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get("Content-Type") if exc.headers else "", exc.read() or b"", url
    except Exception as exc:  # noqa: BLE001 - a failed fetch is recorded, never guessed around
        return "EXCEPTION", "", str(exc).encode("utf-8", "replace"), url


def is_challenge(status, body):
    """A bot challenge, in any status: recorded and never solved."""
    head = (body or b"")[:20000].decode("utf-8", "replace")
    return bool(_CHALLENGE.search(head)) and (status in (403, 429, 503) or "<html" in head.lower())


def text_sha256(t):
    return hashlib.sha256((t or "").encode("utf-8")).hexdigest()


def _load(p=None):
    p = p or SOURCES                               # resolved at call time (a test isolates it)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def _dump(d, p=None):
    import g1_regulatory_source as rs              # the same atomic, retried writer
    rs._dump(p or SOURCES, d)


def _text_path(url):
    return os.path.join(TEXTS, hashlib.sha1(url.encode("utf-8")).hexdigest()[:16] + ".txt")


def _hold(url, text):
    os.makedirs(TEXTS, exist_ok=True)
    with open(_text_path(url), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def held_text(url):
    """The held typed text of a record; None unless its digest still matches the record."""
    rec = _load().get(url)
    fp = _text_path(url)
    if not rec or not rec.get("text_sha256") or not os.path.exists(fp):
        return None
    t = open(fp, encoding="utf-8").read()
    return t if text_sha256(t) == rec["text_sha256"] else None


def record(url, **kw):
    cur = _load()
    r = dict(cur.get(url) or {}, url=url, **kw)
    r["fetched"] = datetime.date.today().isoformat()
    cur[url] = r
    _dump(cur)
    return r


def pdf_text(body):
    """The PDF's own text layer (pypdf; never OCR), whitespace-normalised; '' when there is none."""
    import io
    try:
        import pypdf
        r = pypdf.PdfReader(io.BytesIO(body))
        return re.sub(r"[ \t\r\f\v]+", " ", "\n".join((p.extract_text() or "") for p in r.pages)).strip()
    except Exception:  # noqa: BLE001 - no text layer is a state, never a guess
        return ""


# ------------------------------------------------------------------------------------------------ OPEN_LOCATION route

_LIC_TAG = re.compile(r"<meta\b[^>]*\b(?:name|property)\s*=\s*[\"'](?:cc_license_url|dc\.rights|dcterms\.license|"
                      r"citation_license|dc\.license)[\"'][^>]*>|<(?:link|a)\b[^>]*\brel\s*=\s*[\"']license[\"'][^>]*>",
                      re.I)
_CC_URL = re.compile(r"creativecommons\.org/(?:licenses/([a-z-]+)/\d|publicdomain/(zero|mark)/\d)", re.I)


def page_licence(page):
    """('cc-by-nc-nd', the tag) when the page's OWN licence tag names a Creative Commons licence; (None, None) else.
    Only licence tags count: a footer link to creativecommons.org elsewhere on a page licenses nothing."""
    for m in _LIC_TAG.finditer(page or ""):
        c = _CC_URL.search(m.group(0))
        if c:
            kind = (c.group(1) or c.group(2) or "").lower()
            return ("cc0" if kind in ("zero", "mark") else f"cc-{kind}"), _html.unescape(m.group(0))[:300]
    return None, None


def oa_locations(doi):
    """Candidate OA copies of a DOI: OpenAlex locations (is_oa) then Semantic Scholar's openAccessPdf; published
    versions first. The index's licence is kept only as 'index_licence' -- it is never the licence of record."""
    out = []
    st, _ct, b, _u = fetch("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi), timeout=40)
    if st == 200:
        try:
            for loc in json.loads(b).get("locations") or []:
                if loc.get("is_oa") and loc.get("pdf_url"):
                    out.append({"via": "OpenAlex", "pdf_url": loc["pdf_url"], "landing_url": loc.get("landing_page_url"),
                                "version": loc.get("version"), "index_licence": loc.get("license")})
        except ValueError:
            pass
    st, _ct, b, _u = fetch(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi)}"
                           "?fields=openAccessPdf", timeout=40)
    if st == 200:
        try:
            p = (json.loads(b).get("openAccessPdf") or {})
            if p.get("url") and p["url"] not in {o["pdf_url"] for o in out}:
                out.append({"via": "SemanticScholar", "pdf_url": p["url"], "landing_url": f"https://doi.org/{doi}",
                            "version": None, "index_licence": p.get("license")})
        except ValueError:
            pass
    return sorted(out, key=lambda o: VERSION_ORDER.get(o.get("version") or "", 3))


def _title_words(title):
    return [w for w in re.findall(r"[a-z]{4,}", (title or "").lower())][:8]


def identity_ok(text, title):
    """The copy is the trial's own report: at least 6 of the first 8 long title words appear in its text."""
    w = _title_words(title)
    low = (text or "").lower()
    return len(w) >= 3 and sum(1 for x in w if x in low) >= min(6, len(w))


def open_location(pmid, doi, title, fetch_new=True):
    """The best HELD CC copy of the report: (text, record) or ('', None). Tries each candidate once; records every
    outcome (CC_TEXT / NOT_OPEN / BOT_CHALLENGE / NOT_PDF / NO_TEXT_LAYER / IDENTITY_NOT_CONFIRMED / FETCH_FAILED)."""
    cur = _load()
    for url, r in cur.items():                       # an already-held CC copy of this DOI
        if r.get("route") == "OPEN_LOCATION" and r.get("doi") == doi and r.get("state") == "CC_TEXT":
            t = held_text(url)
            if t:
                return t, r
    if not fetch_new or not doi:
        return "", None
    for loc in oa_locations(doi):
        url = loc["pdf_url"]
        if (cur.get(url) or {}).get("state") in ("BOT_CHALLENGE", "NOT_OPEN", "IDENTITY_NOT_CONFIRMED"):
            continue                                 # recorded once; never retried around
        base = dict(route="OPEN_LOCATION", pmid=str(pmid), doi=doi, via=loc["via"], version=loc.get("version"),
                    landing_url=loc.get("landing_url"), index_licence=loc.get("index_licence"))
        lst, _lct, lb, lfinal = fetch(loc["landing_url"]) if loc.get("landing_url") else (None, "", b"", None)
        if lst is not None and is_challenge(lst, lb):
            record(url, **base, state="BOT_CHALLENGE", licence=None, note=f"landing page {lfinal} answered a challenge")
            continue
        lic, tag = page_licence(lb.decode("utf-8", "replace") if lb else "")
        if not lic:
            record(url, **base, state="NOT_OPEN", licence=None, landing_sha256=hashlib.sha256(lb).hexdigest() if lb else
                   None, note="the host page states no Creative Commons licence (index licence is not of record)")
            continue
        st, ct, b, final = fetch(url, timeout=90, accept="application/pdf")
        if is_challenge(st, b):
            record(url, **base, state="BOT_CHALLENGE", licence=lic, licence_evidence=tag)
            continue
        if st != 200 or not b.startswith(b"%PDF"):
            record(url, **base, state="NOT_PDF" if st == 200 else "FETCH_FAILED", licence=lic, licence_evidence=tag,
                   status=st, content_type=ct)
            continue
        t = pdf_text(b)
        common = dict(base, licence=lic, licence_evidence=tag, landing_final_url=lfinal,
                      landing_sha256=hashlib.sha256(lb).hexdigest(), doc_sha256=hashlib.sha256(b).hexdigest(),
                      bytes=len(b), final_url=final)
        if len(t) < MIN_TEXT:
            record(url, **common, state="NO_TEXT_LAYER", text_chars=len(t))
            continue
        if not identity_ok(t, title):
            record(url, **common, state="IDENTITY_NOT_CONFIRMED", text_chars=len(t),
                   note="the PDF does not carry the report's own title words")
            continue
        _hold(url, t)
        r = record(url, **common, state="CC_TEXT", text_sha256=text_sha256(t), text_chars=len(t))
        return t, r
    return "", None


def _meta_path():
    return os.path.join(TEXTS, "europepmc_meta.json")


def report_meta(pmid, fetch_new=True):
    """{'doi', 'title'} of a PubMed record (Europe PMC REST, open metadata; cached). The title is the identity check of
    an open-location copy; the DOI names it when the held records carry none."""
    d = _load(_meta_path())
    if str(pmid) in d or not fetch_new:
        return d.get(str(pmid)) or {}
    st, _ct, b, _u = fetch("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:"
                           f"{urllib.parse.quote(str(pmid))}%20AND%20SRC:MED&resultType=core&format=json", timeout=40)
    if st != 200:
        return {}
    m = {}
    try:
        r = (json.loads(b).get("resultList") or {}).get("result") or []
        if r:
            m = {"doi": (r[0].get("doi") or "").lower() or None, "title": r[0].get("title")}
    except ValueError:
        return {}
    d[str(pmid)] = m
    os.makedirs(TEXTS, exist_ok=True)
    _dump(d, _meta_path())
    return m


_NCT = re.compile(r"\bNCT\d{8}\b")


def stated_registration(text):
    """The ONE NCT id the trial's own report prints, or None when it prints none or several (a report citing another
    trial's registration names that trial, not itself)."""
    ids = set(_NCT.findall(text or ""))
    return ids.pop() if len(ids) == 1 else None


def doi_licences():
    """{doi: licence} for every CC_TEXT open-location record (licence read from the HOST page): the record_licence
    guard's second licence index beside Unpaywall's."""
    return {str(r.get("doi") or "").lower(): r.get("licence") for r in _load().values()
            if r.get("route") == "OPEN_LOCATION" and r.get("state") == "CC_TEXT" and r.get("doi")}


# --------------------------------------------------------------------------------------------------------- EUCTR route

_EUDRACT = re.compile(r"^\d{4}-\d{6}-\d{2}$")
_CTIS = re.compile(r"^\d{4}-\d{6}-\d{2}-\d{2}$")


def registry_ids(ncts):
    """{'eudract': [...], 'ctis': [...]} from the trials' AACT secondary ids (typed patterns only)."""
    import g1_regulatory_source as rs
    codes = [c.strip() for v in rs.study_codes(ncts).values() for c in v or []]
    return {"eudract": sorted({c for c in codes if _EUDRACT.match(c)}),
            "ctis": sorted({c for c in codes if _CTIS.match(c)})}


def euctr_search(nct):
    """EudraCT numbers an EU CTR search on the NCT returns; used only when it returns exactly ONE trial."""
    st, _ct, b, _u = fetch(f"{EUCTR}/ctr-search/search?query={urllib.parse.quote(nct)}", timeout=60)
    if st != 200:
        return []
    return sorted(set(re.findall(r"EudraCT Number:</span>\s*(\d{4}-\d{6}-\d{2})", b.decode("utf-8", "replace"))))


def _cell(s):
    raw = _html.unescape(re.sub(r"<sup>.*?</sup>", "", s, flags=re.S)).replace("\xa0", " ")
    indent = bool(re.match(r"\s*<div>\s*(?:&nbsp;|\xa0)", s)) or bool(re.match(r"\s*(?:&nbsp;){2,}", s))
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw)).strip(), indent


_ROW = re.compile(r"<tr[^>]*>((?:(?!<tr[\s>]).)*?)</tr>", re.S | re.I)
_TD = re.compile(r"<td[^>]*>(.*?)</td>", re.S | re.I)
_STOP = re.compile(r"^(?:Adverse events information|Timeframe for reporting adverse events|Adverse events reporting)",
                   re.I)


def parse_euctr(page):
    """The results page's END POINTS, typed: [{title, description, type, time_frame, arms, n, units, categories:
    [(label, [values])], analyses: [{title, groups, n_included, param_type, value, level, sides, lower, upper}]}].
    Rows are the page's innermost <tr>s in document order; an indented label under an end point is a category row.
    Parsing stops at the adverse-events section."""
    eps, cur, ana = [], None, None
    for m in _ROW.finditer(page or ""):
        cells = [_cell(c) for c in _TD.findall(m.group(1))]
        if not cells:
            continue
        lab, ind = cells[0]
        vals = [c[0] for c in cells[1:]]
        if _STOP.match(lab):
            break
        if lab == "End point title":
            cur = {"title": vals[0] if vals else "", "description": "", "type": "", "time_frame": "", "arms": [],
                   "n": [], "units": "", "categories": [], "analyses": []}
            eps.append(cur)
            ana = None
            continue
        if cur is None:
            continue
        v0 = vals[0] if vals else ""
        if lab == "End point description":
            cur["description"] = v0
        elif lab == "End point type":
            cur["type"] = v0
        elif lab == "End point timeframe":
            cur["time_frame"] = v0
        elif lab == "End point values":
            cur["arms"] = vals
        elif lab == "Number of subjects analysed":
            cur["n"] = [int(v) if v.isdigit() else None for v in vals]
        elif lab.startswith("Units:"):
            cur["units"] = lab[len("Units:"):].strip()
        elif lab == "Statistical analysis title":
            ana = {"title": v0, "groups": "", "n_included": None, "param_type": "", "value": None, "level": "",
                   "sides": "", "lower": None, "upper": None}
            cur["analyses"].append(ana)
        elif ana is not None and lab in ("Comparison groups", "Number of subjects included in analysis", "Parameter type",
                                         "Point estimate", "level", "sides", "lower limit", "upper limit"):
            key = {"Comparison groups": "groups", "Number of subjects included in analysis": "n_included",
                   "Parameter type": "param_type", "Point estimate": "value", "lower limit": "lower",
                   "upper limit": "upper"}.get(lab, lab)
            ana[key] = v0
        elif ana is None and ind and cur["arms"] and len(vals) == len(cur["arms"]):
            cur["categories"].append((lab, vals))
    return eps


_ALIAS = re.compile(r"^(.{3,80}?)\s*\(([A-Za-z][A-Za-z0-9/+-]{1,11})\)$")


def arm_aliases(page):
    """{'SoC': 'Standard of Care'} from the page's OWN arm / reporting-group titles of the form 'Full name (ABBR)': the
    end-point groups are often named by the abbreviation only ('Safety Set (SS) - SoC')."""
    out = {}
    for m in _ROW.finditer(page or ""):
        cells = [_cell(c)[0] for c in _TD.findall(m.group(1))]
        if len(cells) >= 2 and cells[0] in ("Arm title", "Reporting group title"):
            a = _ALIAS.match(cells[1])
            if a:
                out.setdefault(a.group(2), a.group(1).strip())
    return out


def expand_arm(title, aliases):
    """The group title with every abbreviation it uses spelled out from the page's own definitions."""
    extra = [full for ab, full in (aliases or {}).items()
             if re.search(rf"(?<![A-Za-z0-9]){re.escape(ab)}(?![A-Za-z0-9])", title or "")]
    return " ".join([title or ""] + extra)


_PEOPLE_UNITS = re.compile(r"^(?:number of )?(?:subjects?|participants?|patients?|people|persons?)\b", re.I)
_INT = re.compile(r"^\d+$")


def euctr_registry(eps, eid, digest, aliases=None):
    """The AACT registry shape (kgap.aact_adapter.registry_for) of a parsed EU CTR results page, so the SAME binding
    gates and typed matcher read it: one outcome per end point (analyses attach here) and one per category row; arm
    counts only under people units and only when printed as whole numbers (a percent is never turned into a count)."""
    reg = {"_snapshot": {"id": f"EUCTR {eid} results page", "digest": digest}, "outcomes": {}, "analyses": [],
           "groups": {}, "group_titles": {}, "_source": "EUCTR", "arm_aliases": dict(aliases or {})}
    for k, e in enumerate(eps):
        gids = [f"{eid}:{k}:g{i}" for i in range(len(e["arms"]))]
        for g, a in zip(gids, e["arms"]):
            reg["group_titles"][g] = a
        people = bool(_PEOPLE_UNITS.match(e["units"] or ""))
        base = f"{eid}:{k}"
        pop = " ".join(x for x in [e["description"], " / ".join(e["arms"])] if x)
        common = {"type": (e["type"] or "").upper(), "time_frame": e["time_frame"], "population": pop,
                  "units_analyzed": e["units"], "description": e["description"]}
        reg["outcomes"][base] = dict(common, title=e["title"])
        rows = [(base, e["title"], None)] if not e["categories"] else \
            [(f"{base}.{j}", f"{e['title']}: {lab}", vals) for j, (lab, vals) in enumerate(e["categories"])]
        for oid, title, vals in rows:
            if oid != base:
                reg["outcomes"][oid] = dict(common, title=title)
            if people and vals and all(_INT.match(v or "") for v in vals) and len(e["n"]) == len(vals) and \
                    None not in e["n"]:
                reg["groups"][oid] = [{"group": g, "count": int(v), "n": n} for g, v, n in zip(gids, vals, e["n"])]
        for a in e["analyses"]:
            if a.get("level") != "95%" or a.get("sides") != "2-sided":
                continue                             # only a two-sided 95% CI is a CI here
            names = [x.strip() for x in re.split(r"\s+v\s+", a.get("groups") or "") if x.strip()]
            groups = [g for g, t in zip(gids, e["arms"]) if t in names]
            reg["analyses"].append({"outcome_id": base, "param_type": a.get("param_type"), "param_value": a.get("value"),
                                    "ci_lower": a.get("lower"), "ci_upper": a.get("upper"), "groups": groups,
                                    "title": a.get("title")})
    return reg


def euctr_results(eid, fetch_new=True):
    """(registry, record) for one EudraCT number's results page, or (None, record). Held as typed text (never shown)."""
    url = f"{EUCTR}/ctr-search/trial/{eid}/results"
    rec = _load().get(url)
    page = None
    if rec and rec.get("state") == "RESULT_TABLES":
        page = held_text(url)
    if page is None:
        if not fetch_new:
            return None, rec
        st, ct, b, final = fetch(url, timeout=90)
        if is_challenge(st, b):
            return None, record(url, route="EUCTR", eudract=eid, state="BOT_CHALLENGE", licence=THIRD_PARTY)
        if st != 200:
            return None, record(url, route="EUCTR", eudract=eid, state="FETCH_FAILED", status=st, licence=THIRD_PARTY)
        page = b.decode("utf-8", "replace")
        atts = sorted(set(re.findall(r"/ctr-search/rest/download/result/attachment/[\w/-]+", page)))
        state = "RESULT_TABLES" if "End point title" in page else ("RESULT_ATTACHMENT_ONLY" if atts else
                                                                     "NO_POSTED_RESULTS")
        if state == "RESULT_TABLES":
            _hold(url, page)
        rec = record(url, route="EUCTR", eudract=eid, state=state, licence=THIRD_PARTY,
                     licence_evidence="clinicaltrialsregister.eu disclaimer -> EMA legal notice: 'The above-mentioned "
                                      "permissions do not apply to content supplied by third parties'",
                     doc_sha256=hashlib.sha256(b).hexdigest(), text_sha256=text_sha256(page) if state ==
                     "RESULT_TABLES" else None, text_chars=len(page), attachments=[EUCTR + a for a in atts])
        if state != "RESULT_TABLES":
            return None, rec
    return euctr_registry(parse_euctr(page), eid, rec["text_sha256"], arm_aliases(page)), rec


def ctis_state(ct_number, fetch_new=True):
    """The CTIS public record's results state for one CTIS number (recorded; a posted result is a sponsor document)."""
    url = CTIS_API + ct_number
    rec = _load().get(url)
    if rec or not fetch_new:
        return rec
    st, _ct, b, _u = fetch(url, timeout=60)
    if is_challenge(st, b):
        return record(url, route="CTIS", ctis=ct_number, state="BOT_CHALLENGE", licence=THIRD_PARTY)
    if st != 200:
        return record(url, route="CTIS", ctis=ct_number, state="FETCH_FAILED", status=st, licence=THIRD_PARTY)
    try:
        d = json.loads(b)
    except ValueError:
        return record(url, route="CTIS", ctis=ct_number, state="NOT_JSON", licence=THIRD_PARTY)
    res = d.get("results") or {}
    return record(url, route="CTIS", ctis=ct_number, licence=THIRD_PARTY, doc_sha256=hashlib.sha256(b).hexdigest(),
                  state="RESULTS_POSTED" if res else "NO_POSTED_RESULTS", status_code=d.get("ctStatus"))


def euctr_evidence(ncts, fetch_new=True):
    """{eudract: {'_reg': registry, 'record': record}} for every EudraCT number of the trial with result tables, plus
    CTIS states; the search fallback is used only when AACT names no EudraCT number and the search returns ONE trial."""
    ids = registry_ids(ncts)
    eids = list(ids["eudract"])
    how = {e: "AACT id_information" for e in eids}
    if not eids and fetch_new:
        for n in ncts:
            hits = euctr_search(n)
            if len(hits) == 1:
                eids.append(hits[0])
                how[hits[0]] = f"EU CTR search on {n} (one trial returned)"
    out = {}
    for e in eids:
        reg, rec = euctr_results(e, fetch_new)
        out[e] = {"_reg": reg, "record": rec, "found_by": how.get(e)}
    for c in ids["ctis"]:
        out["CTIS " + c] = {"_reg": None, "record": ctis_state(c, fetch_new), "found_by": "AACT id_information"}
    return out
