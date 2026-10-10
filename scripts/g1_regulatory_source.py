"""REGULATORY: open regulatory review documents as a PRIMARY-grade source route for G1 trial acquisition (typed; no model).

A drugs@FDA medical / statistical review or an EMA EPAR is the regulator's own analysis of the sponsor's trial report: a
primary source for the trials of a marketing submission (TOCILIZUMAB's COVID-19 sBLA holds RECOVERY / EMPACTA / COVACTA /
REMDACTA; Repatha's holds FOURIER). This module only HOLDS the documents and says where a trial is named in them; the
acquisition reader proposes a tuple and scripts/g1_trial_acquire.gate admits it only against the WHOLE held document.

Typed source record (registry/regulatory_sources.json, keyed by url):
  agency      FDA | EMA | NICE                  -- from the url's HOST, never from the document or a model
  licence     US_GOV_PUBLIC_DOMAIN (FDA, a US Government work)
              EMA_REUSE_WITH_ACKNOWLEDGEMENT (EMA: 'reproduction is authorised provided the source is acknowledged';
              shown since 6 Oct on Mahmood's word, every window carrying EMA_ACK)
              NICE_NOTICE_OF_RIGHTS (held for typed extraction only) unless the document's own text states OGL / CC
  doc_sha256  digest of the PDF bytes as fetched; text_sha256 of the typed text layer (pypdf; never OCR)
  state       TEXT | NO_TEXT_LAYER | NOT_PDF | FETCH_FAILED
Discovery is by the topic's intervention agents (openFDA drugsfda application_docs typed 'Review', NDA/BLA only -- an
ANDA review is a generic's bioequivalence file and never holds an outcome trial; EMA EPAR public assessment reports by
INN in the EMA medicines JSON). No hand list of products or documents.

Where a trial is named: its acronym, NCT ids and the registry's own secondary ids (AACT id_information: FDA reviews name
trials by sponsor study code, 'Study 20110118' = FOURIER).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]

SOURCES = os.path.join(ROOT, "registry", "regulatory_sources.json")
IDCACHE = os.path.join(ROOT, "outputs", "k_gap", "_reg", "id_information.json")
HOST_AGENCY = {"www.accessdata.fda.gov": "FDA", "accessdata.fda.gov": "FDA", "www.fda.gov": "FDA",
               "www.ema.europa.eu": "EMA", "ema.europa.eu": "EMA", "www.nice.org.uk": "NICE", "nice.org.uk": "NICE"}
# NICE documents (committee papers with the ERG / EAG report, final appraisal determinations, guideline evidence
# reviews) carry '(c) NICE ... subject to Notice of rights' and reproduce company-submission material: NOT open unless the
# document's OWN text states the Open Government Licence or a CC licence (licence_from_text, read when it is held)
AGENCY_LICENCE = {"FDA": "US_GOV_PUBLIC_DOMAIN", "EMA": "EMA_REUSE_WITH_ACKNOWLEDGEMENT", "NICE": "NICE_NOTICE_OF_RIGHTS"}
# licences a model may be shown (the prompt goes into a public record). EMA: Mahmood 6 Oct ('European drug agency can
# be used'); EMA's terms authorise reproduction provided the source is acknowledged, so every shown EMA window carries
# EMA_ACK (reproducible_ai/record_licence.regulatory_window_problem refuses one without it)
PROMPT_OPEN = ("US_GOV_PUBLIC_DOMAIN", "EMA_REUSE_WITH_ACKNOWLEDGEMENT", "OGL", "CC")
EMA_ACK = "Source: European Medicines Agency (EMA), reproduced with acknowledgement of the source"
WINDOW = 1800                                    # characters either side of a naming mention shown to the reader
MAX_SHOWN = 40000                                # per trial, across documents
MAX_DOCS = 160
MAX_PER_AGENCY = 70                              # documents held per agency per topic
TYPED_REACH = 6000                               # the typed reader looks as far from a naming mention as the gate does


def agency_of(url):
    return HOST_AGENCY.get((urlparse(url or "").hostname or "").lower())


def licence_of(url):
    """The licence follows from the HOST alone (a prompt or a document cannot declare itself open)."""
    return AGENCY_LICENCE.get(agency_of(url))


def licence_from_text(url, text):
    """The held record's licence: the host's, except a NICE document whose OWN text states OGL / a CC licence."""
    lic = licence_of(url)
    if agency_of(url) == "NICE" and text:
        if re.search(r"Open Government Licen[cs]e", text):
            return "OGL"
        if re.search(r"creativecommons\.org/licenses/|Creative Commons Attribution", text):
            return "CC"
    return lic


def prompt_open(url, rec=None):
    """By the HELD record's licence (a prompt can never declare one); the host's when no record is given."""
    return ((rec or {}).get("licence") or licence_of(url)) in PROMPT_OPEN


def _ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def text_sha256(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------------------------- discovery and holding

DISCOVERY_ERRORS = {}          # agent -> [failed openFDA searches] of the latest fda_review_urls(agent) call


def fda_review_urls(agent):
    """drugs@FDA documents for an INN: NDA/BLA application_docs typed 'Review' (a TOC page followed to its PDFs) or
    'Label' (section 14, Clinical Studies, prints the pivotal trials' results)."""
    from harness import http
    import k_gap_regulatory_probe as rp
    # two typed searches: the openFDA generic name, and the application's OWN active ingredient -- some applications
    # carry no openfda block (KERENDIA NDA215341: finerenone was never discovered by the first; R9-4, 9 Oct)
    results, seen = [], set()
    DISCOVERY_ERRORS.pop(agent, None)
    for q in (f'openfda.generic_name:"{agent}"', f'products.active_ingredients.name:"{agent.upper()}"'):
        try:
            d = http.get_json("https://api.fda.gov/drug/drugsfda.json", {"search": q, "limit": "50"}, tries=2)
        except Exception as exc:  # noqa: BLE001 - openFDA's 404 'No matches found!' is a result; anything else is
            # a FAILED search, recorded so it is never read as 'no applications' (codex r9-4-label-r1 #7)
            if "NOT_FOUND" not in str(exc) and "No matches found" not in str(exc) and "404" not in str(exc):
                DISCOVERY_ERRORS.setdefault(agent, []).append(f"{q}: {type(exc).__name__}: {str(exc)[:160]}")
            continue
        for r in d.get("results", []):
            if r.get("application_number") not in seen:
                seen.add(r.get("application_number"))
                results.append(r)
    subs = []
    for r in results:
        if not str(r.get("application_number") or "").upper().startswith(("NDA", "BLA")):
            continue
        for s in r.get("submissions", []):
            for dd in s.get("application_docs") or []:
                if (dd.get("type") or "").lower() in ("review", "label") and dd.get("url"):
                    subs.append((str(dd.get("date") or s.get("submission_status_date") or ""),
                                 dd["url"].replace("http://", "https://")))
    out = []
    for _d, u in sorted(set(subs), reverse=True):                 # newest first: outcome-trial supplements are late
        if u.lower().endswith(".pdf"):
            out.append(u)
            continue
        # a TOC page is a TEMPLATE: 'pdfBaseName = "125276Orig1s137"' + the review suffixes, shown by script only when
        # the document exists -- so the clinical / statistical review suffixes are tried, and a missing one is recorded
        txt, _rec = rp.fetch_text(u)
        m = re.search(r"pdfBaseName\s*=\s*[\"']([A-Za-z0-9_]+)[\"']", txt)
        base = u.rsplit("/", 1)[0] + "/"
        if m:
            out += [base + m.group(1) + sfx + ".pdf" for sfx in REVIEW_SUFFIXES]
        for h in re.findall(r"href=\"([^\"'+ ]+\.pdf)\"", txt, re.I):
            out.append(h if h.startswith("http") else base + h)
    return list(dict.fromkeys(out))


REVIEW_SUFFIXES = ("MedR", "StatR", "MultidisciplineR", "IntegratedR", "SumR", "CrossR", "OtherR")


NICE = "https://www.nice.org.uk"
NICE_UA = {"User-Agent": "meta-harness (meta-harness@example.org)"}
MAX_NICE_GUIDANCE = 6


def _nice_html(url):
    from harness import http
    try:
        st, b = http.get_raw(url, tries=2, timeout=60)
    except Exception:  # noqa: BLE001 - an unreachable page is nothing held, never guessed
        return ""
    return b.decode("utf-8", "replace") if st == 200 else ""


def nice_guidance(agent, html=None):
    """Published NICE guidance ids (ta / ng / cg) a NICE site search for the INN returns (in-development ids skipped)."""
    from urllib.parse import quote
    h = _nice_html(f"{NICE}/search?q={quote(agent)}&ndt=Guidance") if html is None else html
    ids = re.findall(r'href="/guidance/((?:ta|ng|cg)\d+)"', h, re.I)
    return list(dict.fromkeys(i.lower() for i in ids))[:MAX_NICE_GUIDANCE]


def nice_docs(gid, history_html=None, evidence_html=None):
    """A guidance's evidence documents: for a TA its committee papers (they contain the ERG / EAG report) and final
    appraisal determination (from /history); for an NG / CG its evidence reviews (from /evidence)."""
    out = []
    if gid.startswith("ta"):
        h = _nice_html(f"{NICE}/guidance/{gid}/history") if history_html is None else history_html
        for m in re.findall(r'href="(/guidance/' + gid + r'/documents/(?:committee-papers[-\w]*|final-appraisal-'
                            r'determination[-\w]*))"', h, re.I):
            out.append(NICE + m)
    else:
        h = _nice_html(f"{NICE}/guidance/{gid}/evidence") if evidence_html is None else evidence_html
        for m in re.findall(r'href="(/guidance/' + gid + r'/evidence/[-\w]*pdf-\d+)"', h, re.I):
            # evidence reviews / appendices / full guideline -- never the process documents around them
            if not re.search(r"stakeholder|consultation|equality|surveillance|comments|matrix|scope", m, re.I):
                out.append(NICE + m)
    return list(dict.fromkeys(out))


def nice_urls(agent):
    return [u for g in nice_guidance(agent) for u in nice_docs(g)]


def topic_agents(cfg):
    a = cfg.get("intervention_agents") or cfg.get("intervention_terms") or []
    return [x for x in (list(a.keys()) if isinstance(a, dict) else a) if len(x) >= 4]


def hold_topic(slug, cfg, fetch=True):
    """Typed source records for one topic's regulatory documents (fetched and cached by the probe's fetch_text)."""
    import k_gap_regulatory_probe as rp
    cur = _load(SOURCES)
    urls = []
    agents = topic_agents(cfg)
    for a in agents:
        urls += fda_review_urls(a) if fetch else []
        urls += nice_urls(a) if fetch else []
    try:
        ema = rp._j_ema() if fetch else []
        urls += [u for p in rp.ema_products(agents, ema) for u in rp.ema_docs(p)]
    except Exception:  # noqa: BLE001 - EMA index unavailable is recorded as nothing held, never guessed
        pass
    for u in [u for u in cur if "'" in u or " " in u]:           # a TOC template's unexpanded href is no document
        del cur[u]
    held = []
    import g1_trial_acquire as ga
    # the cap is PER AGENCY: one global cap let FDA + NICE fill it before any EMA document was reached
    # (corticosteroids: 160 = 64 FDA + 84 NICE + 12 failed, EMA never tried)
    per = {}
    capped = []
    for u in dict.fromkeys(urls):
        a = agency_of(u)
        if a and per.get(a, 0) < MAX_PER_AGENCY:
            per[a] = per.get(a, 0) + 1
            capped.append(u)
    for u in capped:
        if not ga.disk_ok():                       # Mahmood 6 Oct: work only while C: and F: each keep >= 5 GB free
            print("DISK_FLOOR: stopped holding documents", slug, flush=True)
            break
        txt, rec = rp.fetch_text(u)
        r = {"url": u, "agency": agency_of(u), "licence": licence_from_text(u, txt), "state": rec.get("state"),
             "doc_sha256": rec.get("sha256"), "bytes": rec.get("bytes"),
             "text_sha256": text_sha256(txt) if txt else None, "text_chars": len(txt or "")}
        topics = set((cur.get(u) or {}).get("topics") or []) | {slug}
        r["topics"] = sorted(topics)
        cur[u] = r
        held.append(r)
    _dump(SOURCES, cur)
    return held


def doc_text(url):
    """The held typed text of a source record; refused (None) unless its digest still matches the record."""
    import k_gap_regulatory_probe as rp
    rec = _load(SOURCES).get(url)
    if not rec or rec.get("state") != "TEXT":
        return None
    fp = os.path.join(rp.REG, hashlib.sha1(url.encode("utf-8")).hexdigest()[:16] + ".txt")
    if not os.path.exists(fp):
        return None
    t = open(fp, encoding="utf-8").read()
    return t if text_sha256(t) == rec.get("text_sha256") else None


# ------------------------------------------------------------------------------------------------- naming a trial

def study_codes(ncts):
    """AACT id_information secondary ids per NCT (sponsor study codes), cached; one streaming pass for missing NCTs."""
    from harness import aact
    d = _load(IDCACHE)
    want = [n for n in ncts if n and n not in d]
    if want:
        snap = aact.snapshot_dir(None)
        got = {n: [] for n in want}
        if snap and os.path.exists(os.path.join(snap, "id_information.txt")):
            for r in aact._iter_rows(os.path.join(snap, "id_information.txt")):
                if r.get("nct_id") in got and r.get("id_value"):
                    got[r["nct_id"]].append(r["id_value"].strip())
        d.update(got)
        _dump(IDCACHE, d)
    return {n: d.get(n) or [] for n in ncts}


_GENERIC = re.compile(r"^(?:study|trial|protocol|phase|cohort|part|the|and)$", re.I)


def trial_names(label, ncts, acronym=None, codes=()):
    """Strings that NAME this trial in a document. A code shorter than 5 characters or a bare number names nothing."""
    names = set(n for n in ncts if n)
    if acronym:
        names.add(acronym)
    for tok in re.findall(r"\b[A-Z][A-Z0-9]{2,}(?:-[A-Z0-9]+)*\b", label or ""):
        names.add(tok)
    for c in codes:
        c = c.strip()
        if len(c) >= 5 and not c.isdigit() and not _GENERIC.match(c):
            names.add(c)
        m = re.match(r"^\D{0,12}?(\d{6,9})$", c)          # sponsor protocol numbers: 'Study 20110118'
        if m:
            names.add(m.group(1))
    return sorted(n for n in names if len(n) >= 4)


def _name_re(n):
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(n) + r"(?![A-Za-z0-9])")


def named_at(text, names):
    """[(offset, name)] of every naming mention."""
    out = []
    for n in names:
        out += [(m.start(), n) for m in _name_re(n).finditer(text)]
    return sorted(out)


def evidence_windows(text, names, terms, width=WINDOW):
    """Windows of the document centred on a naming mention with an outcome term inside the window (merged)."""
    from harness import lexicon
    spans = []
    for off, _n in named_at(text, names):
        a, b = max(0, off - width), min(len(text), off + width)
        w = lexicon.fold(text[a:b])
        if any(t and lexicon.fold(t) in w for t in terms):
            if spans and a <= spans[-1][1]:
                spans[-1][1] = max(spans[-1][1], b)
            else:
                spans.append([a, b])
    return [{"offset": a, "text": text[a:b]} for a, b in spans]


def regulatory_evidence(t, terms, slug, acronym=None):
    """(shown, held): shown = windows of PROMPT-OPEN documents naming the trial; held = url -> whole text + record for
    every TEXT document naming it (the gate searches the whole document)."""
    codes = [c for v in study_codes(t.get("ncts") or []).values() for c in v]
    names = trial_names(t.get("label"), t.get("ncts") or [], acronym, codes)
    shown, held, used = [], {}, 0
    for url, rec in sorted(_load(SOURCES).items()):
        if slug not in (rec.get("topics") or []) or rec.get("state") != "TEXT":
            continue
        txt = doc_text(url)
        if not txt or not named_at(txt, names):
            continue
        held[url] = {"text": txt, "record": rec, "names": names}
        if not prompt_open(url, rec):
            continue
        ws = evidence_windows(txt, names, terms)
        keep = []
        for w in ws:
            if used + len(w["text"]) > MAX_SHOWN:
                break
            keep.append(w)
            used += len(w["text"])
        if keep:
            shown.append(dict({"url": url, "agency": rec["agency"], "licence": rec["licence"],
                               "text_sha256": rec["text_sha256"], "names_searched": names, "windows": keep},
                              **({"acknowledgement": EMA_ACK} if rec["agency"] == "EMA" else {})))
    return shown, held


def quote_named_and_located(doc, quote, names, reach=6000):
    """Offset of the quote in the WHOLE document text (whitespace-normalised) if a trial name occurs within `reach`
    characters of it; else None."""
    W = _ws(doc)
    q = _ws(quote)
    if not q:
        return None
    i = W.find(q)
    if i < 0:
        return None
    lo, hi = max(0, i - reach), min(len(W), i + len(q) + reach)
    return i if any(_name_re(n).search(W[lo:hi]) for n in names) else None


def _load(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def _dump(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + f".{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, indent=1, sort_keys=True, ensure_ascii=False)
    os.replace(tmp, p)


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    for s in sys.argv[1:]:
        c = json.load(open(os.path.join(ROOT, "topics", s + ".json"), encoding="utf-8"))
        h = hold_topic(s, c)
        from collections import Counter
        print(s, len(h), dict(Counter((r["agency"], r["state"]) for r in h)), flush=True)


# ------------------------------------------------------------------------------------- typed extraction (no model)

_PAIR = re.compile(r"(?<![\d.])(\d{1,6})\s*/\s*(\d{1,6})\s*\(\s*(\d{1,3}(?:\.\d+)?)\s*%?\s*\)")


def _pairs(line):
    """e/N (p%) cells whose percent corroborates them (|100e/N - p| <= 0.15 at the printed precision)."""
    out = []
    for m in _PAIR.finditer(line):
        e, n, pc = int(m.group(1)), int(m.group(2)), float(m.group(3))
        if 0 < n and e <= n and abs(100.0 * e / n - pc) <= 0.15 + (0.5 if "." not in m.group(3) else 0):
            out.append((e, n, m.group(0)))
    return out


def typed_counts(window, terms, interv_terms, comp_terms):
    """DETERMINISTIC counts from a trial-named window of a regulatory document: the ONE line naming an outcome term with
    exactly two corroborated e/N (p%) cells, arms ordered by the nearest preceding header line that names an intervention
    term and a comparator term (their order on that line). Anything ambiguous -> None (the model step then runs)."""
    from harness import lexicon
    lines = window.splitlines()
    tf = [lexicon.fold(t) for t in terms if t]
    it = [lexicon.fold(t) for t in interv_terms if t]
    ct = [lexicon.fold(t) for t in comp_terms if t]
    cands = []
    for i, line in enumerate(lines):
        fl = lexicon.fold(line)
        if not any(t in fl for t in tf):
            continue
        ps = _pairs(line)
        if len(ps) != 2:
            continue
        order = None
        for h in reversed(lines[max(0, i - 25): i]):
            fh = lexicon.fold(h)
            pi = min((fh.find(t) for t in it if t in fh), default=-1)
            pc = min((fh.find(t) for t in ct if t in fh), default=-1)
            if pi >= 0 and pc >= 0 and pi != pc:
                order = "IC" if pi < pc else "CI"
                break
        if not order:
            continue
        (a, b) = ps if order == "IC" else ps[::-1]
        cands.append(({"events_t": a[0], "n_t": a[1], "events_c": b[0], "n_c": b[1]}, line.strip()))
    uniq = {tuple(sorted(c[0].items())) for c in cands}
    return cands[0] if len(uniq) == 1 else None


def regulatory_typed(held_reg, terms, interv_terms, comp_terms):
    """Over every held document naming the trial: the typed counts, if exactly one distinct tuple results."""
    got = []
    for url, h in sorted((held_reg or {}).items()):
        if url.startswith("_") or not isinstance(h, dict):
            continue
        for w in evidence_windows(h["text"], h["names"], terms, width=TYPED_REACH):
            r = typed_counts(w["text"], terms, interv_terms, comp_terms)
            if r:
                got.append((url, h["record"], r[0], r[1]))
    uniq = {tuple(sorted(g[2].items())) for g in got}
    return got[0] if len(uniq) == 1 else None
