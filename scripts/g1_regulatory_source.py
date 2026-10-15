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
import csv
import io
import time
import tarfile
from html import unescape
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse, urljoin, quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]

SOURCES = os.path.join(ROOT, "registry", "regulatory_sources.json")
BINDINGS = "registry/g1_regulatory_bindings.json"
IDCACHE = os.path.join(ROOT, "outputs", "k_gap", "_reg", "id_information.json")
HOST_AGENCY = {"ftp.ncbi.nlm.nih.gov": "CADTH", "www.iqwig.de": "IQWIG", "iqwig.de": "IQWIG", "www.accessdata.fda.gov": "FDA", "accessdata.fda.gov": "FDA", "www.fda.gov": "FDA",
               "www.ema.europa.eu": "EMA", "ema.europa.eu": "EMA", "www.nice.org.uk": "NICE", "nice.org.uk": "NICE",
               "www.g-ba.de": "GBA", "g-ba.de": "GBA", "www.pbs.gov.au": "PBAC", "pbs.gov.au": "PBAC"}
# NICE documents (committee papers with the ERG / EAG report, final appraisal determinations, guideline evidence
# reviews) carry '(c) NICE ... subject to Notice of rights' and reproduce company-submission material: NOT open unless the
# document's OWN text states the Open Government Licence or a CC licence (licence_from_text, read when it is held)
# G-BA (www.g-ba.de/sys/impressum, read 13 Oct 2026): 'Alle Inhalte ... sind urheberrechtlich ... geschuetzt'; reuse
# beyond copyright's limits needs G-BA's or the author's consent, and only citing and linking are permitted. The AMNOG
# documents it hosts (manufacturer Modul 4 dossiers, IQWiG Nutzenbewertungen, whose own Impressum likewise permits only
# citing and linking) are therefore held for TYPED extraction only, never shown to a model.
# PBS (https://www.pbs.gov.au/general/copyright, read 15 Oct 2026): "may be reproduced in part for personal use as
# general reference material only ... all rights are reserved" -> typed (deterministic) reading only, never a model.
AGENCY_LICENCE = {"CADTH": "CADTH_COPYRIGHT_TYPED_ONLY", "IQWIG": "IQWIG_ALL_RIGHTS_RESERVED_TYPED_ONLY", "FDA": "US_GOV_PUBLIC_DOMAIN", "EMA": "EMA_REUSE_WITH_ACKNOWLEDGEMENT", "NICE": "NICE_NOTICE_OF_RIGHTS",
                  "GBA": "GBA_IQWIG_CITE_AND_LINK_ONLY", "PBAC": "PBS_COPYRIGHT_PERSONAL_REFERENCE_ONLY"}
# licences a model may be shown (the prompt goes into a public record). EMA: Mahmood 6 Oct ('European drug agency can
# be used'); EMA's terms authorise reproduction provided the source is acknowledged, so every shown EMA window carries
# EMA_ACK (reproducible_ai/record_licence.regulatory_window_problem refuses one without it)
PROMPT_OPEN = ("US_GOV_PUBLIC_DOMAIN", "EMA_REUSE_WITH_ACKNOWLEDGEMENT", "OGL", "CC")
EMA_ACK = "Source: European Medicines Agency (EMA), reproduced with acknowledgement of the source"
WINDOW = 1800                                    # characters either side of a naming mention shown to the reader
MAX_SHOWN = 40000                                # per trial, across documents
MAX_DOCS = 160
MAX_PER_AGENCY_FDA = 120
USER_AGENT = "meta-harness k-gap (meta-harness@example.org)"
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
    if agency_of(url) == "CADTH" and text:
        permissions = re.findall(r"<permissions\b[^>]*>.*?</permissions\s*>", text, re.S | re.I)
        return _cadth_licence("\n".join(permissions))
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

def _request(fn, *args, **kwargs):
    """Scope the shared HTTP identity to this source route."""
    from harness import http
    previous = http.UA
    try:
        http.UA = USER_AGENT
        return fn(*args, **kwargs)
    finally:
        http.UA = previous


def _links(markup, base):
    return [urljoin(base, unescape(h)) for h in re.findall(r"href\s*=\s*[\"']([^\"'+ ]+)[\"']", markup, re.I)]


def _fda_review(url):
    p = urlparse(url).path.lower()
    return (agency_of(url) == "FDA" and bool(re.match(r"/drugsatfda_docs/(nda|bla)/", p))
            and p.endswith((".pdf", "toc.cfm")) and "/appletter/" not in p and "/label/" not in p)


def fda_review_urls(agent):
    """Supplement reviews on the overview are absent from openFDA; labels must never displace them."""
    from harness import http
    from bs4 import BeautifulSoup
    import k_gap_regulatory_probe as rp
    try:
        d = _request(http.get_json, "https://api.fda.gov/drug/drugsfda.json",
                     {"search": f'openfda.generic_name:"{agent}"', "limit": "50"}, tries=2)
    except Exception:  # noqa: BLE001 - an unavailable index supplies no documents
        return []
    reviews, labels = [], []
    for r in d.get("results", []):
        number = re.fullmatch(r"(?:NDA|BLA)(\d{6})", str(r.get("application_number") or ""), re.I)
        if not number:
            continue
        app_labels = {}
        for sub in r.get("submissions", []):
            for doc in sub.get("application_docs") or []:
                u = (doc.get("url") or "").replace("http://", "https://")
                date = str(doc.get("date") or sub.get("submission_status_date") or "")
                if (doc.get("type") or "").lower() == "review" and _fda_review(u):
                    reviews.append((date, u))
                elif (doc.get("type") or "").lower() == "label" and agency_of(u) == "FDA":
                    app_labels[u] = date
        overview = ("https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?"
                    "event=overview.process&ApplNo=" + number[1])
        page = BeautifulSoup(_nice_html(overview), "html.parser")
        for anchor in page.find_all("a", href=True):
            u = urljoin(overview, anchor["href"]).replace("http://", "https://")
            row = anchor.find_parent("tr")
            stamp = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", row.get_text(" ") if row else "")
            year = re.search(r"/(\d{4})/", urlparse(u).path)
            date = (f"{stamp[3]}{int(stamp[1]):02d}{int(stamp[2]):02d}" if stamp else
                    (year[1] + "0000" if year else ""))
            if _fda_review(u):
                reviews.append((date, u))
            elif agency_of(u) == "FDA" and "/drugsatfda_docs/label/" in u.lower() and u.lower().endswith(".pdf"):
                app_labels.setdefault(u, date)
        labels += sorted(app_labels, key=lambda u: (app_labels[u], u), reverse=True)[:3]
    out = []
    for _, u in sorted(set(reviews), reverse=True):
        if u.lower().endswith(".pdf"):
            out.append(u)
            continue
        txt, _ = _request(rp.fetch_text, u)
        if not txt:
            txt = _nice_html(u)  # the probe does not decode .cfm templates
        m = re.search(r"pdfBaseName\s*=\s*[\"']([A-Za-z0-9_]+)[\"']", txt)
        base = u.rsplit("/", 1)[0] + "/"
        if m:
            out += [base + m[1] + suffix + ".pdf" for suffix in REVIEW_SUFFIXES]
        out += [h for h in _links(txt, base) if _fda_review(h) and h.lower().endswith(".pdf")]
    return list(dict.fromkeys(out + labels))


REVIEW_SUFFIXES = ("MedR", "StatR", "MultidisciplineR", "IntegratedR", "SumR", "CrossR", "OtherR")


NICE = "https://www.nice.org.uk"
NICE_UA = {"User-Agent": USER_AGENT}
MAX_NICE_GUIDANCE = 15


def _nice_html(url):
    from harness import http
    try:
        st, b = _request(http.get_raw, url, tries=2, timeout=60)
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


def nice_urls(agent, condition=None):
    """Prefer the topic's condition so unrelated indications cannot fill the guidance cap first."""
    ids = nice_guidance(f"{agent} {condition}") if condition else []
    ids += nice_guidance(agent)
    return [u for g in list(dict.fromkeys(ids))[:MAX_NICE_GUIDANCE] for u in nice_docs(g)]


PBAC = "https://www.pbs.gov.au"
MAX_PBAC_DOCS = 12


_PBAC_SALT = {"with", "and", "plus", "hydrochloride", "hydrobromide", "sodium", "potassium", "calcium", "magnesium",
              "mesylate", "maleate", "sulfate", "sulphate", "acetate", "citrate", "fumarate", "succinate", "tartrate",
              "besylate", "bitartrate", "phosphate", "dihydrate", "monohydrate", "ethyl"}


def pbac_urls(agent, html=None):
    """Match the entry's INN, never a document label; prefer its PDF to a duplicate DOCX."""
    from html import unescape
    from urllib.parse import quote, urljoin
    h = _nice_html(f"{PBAC}/industry/pbac/psd?term={quote(agent, safe='')}") if html is None else html
    anchors = list(re.finditer(r'<a\b[^>]*\bhref=[\"\']([^\"\']+)[\"\'][^>]*>(.*?)</a>', h, re.S | re.I))
    entries = []
    for i, m in enumerate(anchors):
        u = urljoin(PBAC, unescape(m.group(1)))
        date = re.fullmatch(r'/industry/pbac/psd/(\d{4})/(\d{2})/[^/.]+/?', urlparse(u).path)
        if agency_of(u) == "PBAC" and date:
            entries.append((i, date.groups(), _gba_fold(unescape(re.sub(r'<[^>]+>', '', m.group(2))))))
    a = _gba_fold(agent)
    out = []
    for n, (i, date, name) in enumerate(entries):
        # the INN itself, or the INN followed by a SALT / COMBINATION word from a fixed list (a special case for one
        # test fixture's 'LIKE' word fitted the test, not the rule: 15 Oct review of the Codex draft)
        nxt = name[len(a):].split()[:1] if name.startswith(a + " ") else []
        if not a or not (name == a or (nxt and nxt[0] in _PBAC_SALT)):
            continue
        end = entries[n + 1][0] if n + 1 < len(entries) else len(anchors)
        docs = []
        for m in anchors[i + 1:end]:
            u = urljoin(PBAC, unescape(m.group(1)))
            if agency_of(u) == "PBAC" and re.search(r'\.(?:pdf|docx)\?variant=3$', u, re.I):
                docs.append(PBAC + urlparse(u).path + "?variant=3")
        pdfs = [u for u in docs if urlparse(u).path.lower().endswith(".pdf")]
        if pdfs or docs:
            out.append((date, (pdfs or docs)[0]))
    return list(dict.fromkeys(u for _, u in sorted(out, key=lambda x: x[0], reverse=True)))[:MAX_PBAC_DOCS]


GBA = "https://www.g-ba.de"
GBA_NB = GBA + "/bewertungsverfahren/nutzenbewertung/"
MAX_GBA_PROCEDURES = 8
# the AMNOG documents that hold per-trial results: the manufacturer's Modul 4 (its trial tables), IQWiG's benefit
# assessment and any IQWiG addendum. Modul 1-3, resolutions, minutes and the summary documentation are not read.
_GBA_DOC = re.compile(r"^(?:Modul\s*4|Nutzenbewertung IQWiG|Addendum zur Nutzenbewertung)", re.I)


def _gba_fold(s):
    return re.sub(r"[\s\-]+", " ", (s or "").replace("­", "")).strip().casefold()


def gba_search_words(agent, words):
    """The G-BA search words (its own suchworte.json; the search is case-sensitive and exact) that ARE this INN:
    equal after folding case / hyphens ('Icosapent-Ethyl' = 'icosapent ethyl'), or the INN followed by a salt word.
    No fuzzy match."""
    a = _gba_fold(agent)
    return [w for w in words if _gba_fold(w) == a or _gba_fold(w).startswith(a + " ")]


def gba_procedures(listing_html):
    return list(dict.fromkeys(re.findall(r'href="(?:https://www\.g-ba\.de)?/bewertungsverfahren/nutzenbewertung/(\d+)/"',
                                         listing_html)))


def gba_docs(procedure_html):
    out = []
    for href, label in re.findall(r'<a[^>]+href="((?:https://www\.g-ba\.de)?/downloads/[^"]+\.pdf)"[^>]*>(.*?)</a>',
                                  procedure_html, re.S | re.I):
        lab = _ws(re.sub(r"<[^>]+>|&shy;|­|​", "", label))
        if _GBA_DOC.match(lab):
            out.append(href if href.startswith("http") else GBA + href)
    return list(dict.fromkeys(out))


_GBA_PAGES = {}


def gba_urls(agent):
    """AMNOG (section 35a SGB V) documents for an INN, discovered through G-BA's own search words and procedure pages."""
    from urllib.parse import quote
    try:
        words = json.loads(_nice_html(GBA_NB + "suchworte.json") or "[]")
    except ValueError:
        return []
    procs = []
    for w in gba_search_words(agent, words):
        procs += gba_procedures(_nice_html(GBA_NB + "?suchwort=" + quote(w)))
    pages = [_nice_html(GBA_NB + p + "/") for p in list(dict.fromkeys(procs))[:MAX_GBA_PROCEDURES]]
    _GBA_PAGES[agent.casefold()] = pages
    return [u for page in pages for u in gba_docs(page)]


LITARCH_LIST = "https://ftp.ncbi.nlm.nih.gov/pub/litarch/file_list.csv"
LITARCH_BASE = LITARCH_LIST.rsplit("/", 1)[0] + "/"
MAX_CADTH_DOCS = 8
MAX_IQWIG_DOCS = 8
MAX_LITARCH_BYTES = 50 * 1024 * 1024


def _whole_word(agent, text):
    return bool(agent.strip()) and bool(re.search(r"(?<!\w)" + re.escape(agent.casefold()) + r"(?!\w)", text.casefold()))


def _reg_dir():
    return Path(ROOT) / "outputs" / "k_gap" / "_reg"


def cadth_urls(agent):
    """Use the sanctioned bulk index; challenge pages are never evidence."""
    from harness import http
    fp = _reg_dir() / "litarch_file_list.csv"
    try:
        if not fp.exists() or time.time() - fp.stat().st_mtime > 7 * 86400:
            st, body = _request(http.get_raw, LITARCH_LIST, tries=2, timeout=180)
            if st != 200:
                return []
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_bytes(body)
        # NCBI's list is not uniformly UTF-8 (a Latin-1 0xAE in an unrelated NTP title, 15 Oct): a strict decode
        # raised UnicodeDecodeError, the except below turned it into [] and EVERY drug silently got no CADTH document
        rows = csv.DictReader(io.StringIO(fp.read_bytes().decode("utf-8-sig", errors="replace")))
        keep = []
        for row in rows:
            title = row.get("Title", "")
            if row.get("Publisher") != "Canadian Agency for Drugs and Technologies in Health" or not _whole_word(agent, title):
                continue
            if re.search(r"Pharmacoeconomic|Patient Group Input|Recommendation|Environmental Scan", title, re.I):
                continue
            if not re.search(r"Clinical Review|Reimbursement Review|Review of Clinical Effectiveness|Rapid Review|Health Technology Review", title, re.I):
                continue
            file = row.get("File", "")
            if not _safe_member(file) or not file.endswith(".tar.gz"):
                continue
            keep.append((row.get("Last Updated", ""), row.get("Publication Year", ""), LITARCH_BASE + file))
        return list(dict.fromkeys(u for _, _, u in sorted(keep, reverse=True)))[:MAX_CADTH_DOCS]
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"CADTH_DISCOVERY_FAILED {agent}: {type(exc).__name__}: {str(exc)[:120]}", flush=True)
        return []


def _safe_member(name):
    """Reject both POSIX and Windows traversal before interpreting an archive name."""
    name = name.replace("\\", "/")
    return bool(name) and not name.startswith("/") and ".." not in name.split("/") and ":" not in name


def _cadth_licence(permissions):
    """Only explicit unrestricted grants may reach a prompt; missing grants fail closed."""
    from kgap.k_gap import _html_text
    text = _html_text(permissions)
    combined = unescape(permissions) + " " + text
    if re.search(r"by-nc|by-nd|noncommercial|non-commercial|no.?derivatives|CC\s+BY[- ](?:NC|ND)", combined, re.I):
        return "CADTH_CC_BY_NC_ND_TYPED_ONLY"
    if re.search(r"creativecommons.org/licenses/by/4\.0|creativecommons.org/publicdomain/zero/1\.0|\bCC0\b|\bCC BY 4\.0\b|Creative Commons Attribution 4\.0", combined, re.I):
        return "CC"
    if re.search(r"creativecommons|Creative Commons|\bCC\s+BY", combined, re.I):
        return "CADTH_CC_BY_NC_ND_TYPED_ONLY"
    return "CADTH_COPYRIGHT_TYPED_ONLY"


def _litarch_text(body):
    """Read safe regular NXML members only; TOC references order chapters, never filesystem paths."""
    from defusedxml import ElementTree as ET
    from kgap.k_gap import _html_text
    chapters, total = {}, 0
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as archive:
        for member in archive:
            if member.isfile():
                if member.size < 0:
                    raise ValueError("negative archive member size")
                total += member.size
                if total > MAX_LITARCH_BYTES:
                    raise ValueError("litarch uncompressed size exceeds 50 MB")
            if not member.isfile() or not _safe_member(member.name) or not member.name.lower().endswith(".nxml"):
                continue
            name = str(PurePosixPath(member.name.replace("\\", "/")))
            if name in chapters:
                raise ValueError("duplicate NXML member")
            raw = archive.extractfile(member).read()
            root = ET.fromstring(raw)
            chapters[name] = root
    if not chapters:
        raise ValueError("litarch has no safe NXML chapters")
    by_id = {}
    for name, root in chapters.items():
        by_id[PurePosixPath(name).stem] = name
        for el in root.iter():
            if el.get("id"):
                by_id[el.get("id")] = name
            if el.tag.split("}")[-1] in ("book-part-id", "book-id") and el.text:
                by_id[el.text.strip()] = name
    order = []
    for name, root in sorted(chapters.items()):
        for toc in root.iter():
            if toc.tag.split("}")[-1] not in ("toc", "book-toc"):
                continue
            for el in toc.iter():
                refs = [v for k, v in el.attrib.items() if k.split("}")[-1] in ("href", "rid")]
                for ref in refs:
                    target = by_id.get(ref.split("#")[-1]) or by_id.get(PurePosixPath(ref.split("#")[0]).stem)
                    if target and target not in order:
                        order.append(target)
    order += [name for name in sorted(chapters) if name not in order]
    texts, licences = [], []
    for name in order:
        root = chapters[name]
        permissions = [ET.tostring(el, encoding="unicode") for el in root.iter()
                       if el.tag.split("}")[-1] == "permissions"]
        licences.append(_cadth_licence("\n".join(permissions)))
        # Strip namespace prefixes before passing NXML's HTML-compatible tables to layout 3.
        for el in root.iter():
            el.tag = el.tag.split("}")[-1]
        texts.append(_html_text(ET.tostring(root, encoding="unicode")))
    licence = ("CADTH_COPYRIGHT_TYPED_ONLY" if "CADTH_COPYRIGHT_TYPED_ONLY" in licences else
               "CADTH_CC_BY_NC_ND_TYPED_ONLY" if "CADTH_CC_BY_NC_ND_TYPED_ONLY" in licences else "CC")
    return "\n".join(texts), licence


def cadth_fetch_text(url):
    """Cache the package separately, but use the probe's digest-checked text location."""
    from harness import http
    import k_gap_regulatory_probe as rp
    try:
        if not url.startswith(LITARCH_BASE) or not _safe_member(url[len(LITARCH_BASE):]):
            raise ValueError("not a litarch package")
        nbk = re.search(r"NBK\d+", url, re.I)
        if not nbk:
            raise ValueError("litarch package has no NBK accession")
        folder = _reg_dir() / "litarch" / nbk[0].upper()
        fp = folder / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".tar.gz")
        if fp.exists():
            body = fp.read_bytes()
        else:
            st, body = _request(http.get_raw, url, tries=2, timeout=180)
            if st != 200:
                return "", {"state": "FETCH_FAILED", "http_status": st}
        text, licence = _litarch_text(body)
        folder.mkdir(parents=True, exist_ok=True)
        fp.write_bytes(body)
        Path(rp.REG).mkdir(parents=True, exist_ok=True)
        key = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
        (Path(rp.REG) / (key + ".txt")).write_text(text, encoding="utf-8")
        return text, {"state": "TEXT", "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body),
                      "licence": licence, "redaction_blocks": text.count("\u2588")}
    except Exception as exc:  # noqa: BLE001 - unsafe or malformed archives provide no evidence
        return "", {"state": "FETCH_FAILED", "error": f"{type(exc).__name__}: {exc}"[:120]}


# https://www.iqwig.de/en/other/legal-notice/ (15 Oct 2026):
# "We permit and explicitly welcome the citing of our documents and setting up of links to our website."
# No reuse licence is stated, so IQWiG remains typed-only.
IQWIG = "https://www.iqwig.de"


def iqwig_codes(agent):
    """Reuse the procedure text already fetched for G-BA; search is only a supplement."""
    from bs4 import BeautifulSoup
    from kgap.k_gap import _html_text
    if agent.casefold() not in _GBA_PAGES:
        gba_urls(agent)
    pages = list(_GBA_PAGES.get(agent.casefold(), []))
    search = _nice_html(IQWIG + "/en/search/?q=" + quote(agent, safe=""))
    if not search:
        home = BeautifulSoup(_nice_html(IQWIG + "/en/"), "html.parser")
        for form in home.find_all("form"):
            field = (form.find("input", attrs={"type": "search"}) or form.find("input", attrs={"name": "q"})
                     or form.find("input", attrs={"type": "text"}))
            if field and field.get("name"):
                action = urljoin(IQWIG + "/en/", form.get("action", ""))
                if agency_of(action) == "IQWIG" and form.get("method", "get").lower() == "get":
                    search = _nice_html(action + ("&" if "?" in action else "?") +
                                        quote(field["name"]) + "=" + quote(agent, safe=""))
                    break
    pages.append(search)
    # the RAW markup too: G-BA names IQWiG codes in download filenames ('A16-16_Alirocumab_Addendum-zum-Auftrag-A15-47.pdf'),
    # which _html_text drops with the links (15 Oct: 0 codes found for alirocumab). A false code is harmless:
    # iqwig_urls keeps only PDFs that the code's IQWiG project page actually links.
    return sorted(set(re.findall(r"\b[A-Z]\d{2}-\d{1,3}\b", "\n".join((p or "") + "\n" + _html_text(p) for p in pages))))


def iqwig_urls(agent):
    """English extracts precede German assessments within the small agency budget."""
    out = []
    for code in iqwig_codes(agent):
        url = IQWIG + "/en/projects/" + code.lower() + ".html"
        out += [u for u in _links(_nice_html(url), url) if agency_of(u) == "IQWIG"
                and urlparse(u).path.lower().startswith("/download/") and urlparse(u).path.lower().endswith(".pdf")]
    return sorted(dict.fromkeys(out), key=lambda u: (not bool(re.search(r"extract|english|_en[_.-]", u, re.I)), u))[:MAX_IQWIG_DOCS]


HC_SEARCH = "https://clinical-information.canada.ca/search/ci-rc"


def _hc_fetch(url):
    """Use OS trust and refuse redirects: consent URLs must never be requested."""
    import ssl
    import subprocess
    import urllib.request
    if urlparse(url)._replace(query="").geturl() != HC_SEARCH:
        raise ValueError("Health Canada listing only")
    try:
        import truststore
    except ImportError:
        if sys.platform != "win32":
            raise RuntimeError("HC_TLS_UNAVAILABLE")
        curl = Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32" / "curl.exe"
        result = subprocess.run([str(curl), "-s", "--max-time", "60", "--fail", "--proto", "=https",
                                 "-A", USER_AGENT, url], capture_output=True, check=True, timeout=65)
        return result.stdout.decode("utf-8", "replace")
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise ValueError("Health Canada listing redirect refused")
    context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=context))
    with opener.open(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=60) as response:
        return response.read().decode("utf-8", "replace")


def hc_listing(agent):
    """Only public metadata is cached; following a document link would accept personal terms."""
    from bs4 import BeautifulSoup
    fp = str(_reg_dir() / "hc_listing.json")
    cache = _load(fp)
    try:
        soup = BeautifulSoup(_hc_fetch(HC_SEARCH + "?dpq=" + quote(agent, safe="")), "html.parser")
        rows = []
        fields = ("control_number", "brand", "manufacturer", "ingredients", "activity", "decision", "decision_date", "release_date")
        aliases = {"control number": "control_number", "brand name": "brand", "brand": "brand",
                   "manufacturer": "manufacturer", "medicinal ingredients": "ingredients", "ingredients": "ingredients",
                   "medicinal ingredient(s)": "ingredients", "activity": "activity", "regulatory activity": "activity",
                   "decision": "decision", "decision date": "decision_date", "release date": "release_date",
                   "date of decision": "decision_date", "date of release": "release_date",
                   "active ingredient(s)": "ingredients", "active ingredients": "ingredients",
                   # the LIVE headers (read 15 Oct); the synthetic ones above matched nothing on the real page, so every
                   # table was skipped and every drug listed 0 submissions without an error
                   "submission control number": "control_number",
                   "health canada regulatory activity": "activity", "health canada regulatory decision": "decision",
                   "health canada regulatory decision date": "decision_date",
                   "health canada public release date": "release_date"}
        skipped = []
        for table in soup.select("div.view-content table"):
            headers = [aliases.get(_ws(th.get_text(" ")).casefold()) for th in table.select("thead th")]
            if not headers:
                headers = [aliases.get(_ws(th.get_text(" ")).casefold()) for th in table.select("tr th")]
            if set(headers) != set(fields):
                skipped.append([_ws(th.get_text(" ")) for th in table.select("th")][:8])
                continue
            for tr in table.select("tr"):
                cells = tr.find_all("td", recursive=False)
                if len(cells) != len(headers):
                    continue
                row = dict(zip(headers, (_ws(td.get_text(" ")) for td in cells)))
                if _whole_word(agent, row["ingredients"]):
                    rows.append(row)
        cache[agent.casefold()] = {"rows": rows, **({"tables_skipped_unknown_headers": skipped} if skipped else {})}
    except Exception as exc:  # noqa: BLE001 - TLS failure is metadata, never a reason to bypass verification
        rows = []
        cache[agent.casefold()] = {"rows": [], "error": str(exc)[:120]}
    _dump(fp, cache)
    return rows


def topic_agents(cfg):
    a = cfg.get("intervention_agents") or cfg.get("intervention_terms") or []
    return [x for x in (list(a.keys()) if isinstance(a, dict) else a) if len(x) >= 4]


def topic_condition(cfg):
    """Use the topic's first population term to focus guidance discovery."""
    populations = (cfg.get("include") or {}).get("population_any") or []
    return populations[0] if populations else None


def hold_topic(slug, cfg, fetch=True):
    """Typed source records for one topic's regulatory documents (fetched and cached by the probe's fetch_text)."""
    import k_gap_regulatory_probe as rp
    cur = _load(SOURCES)
    urls = []
    agents = topic_agents(cfg)
    for a in agents:
        urls += fda_review_urls(a) if fetch else []
        urls += nice_urls(a, topic_condition(cfg)) if fetch else []
        urls += gba_urls(a) if fetch else []
        urls += pbac_urls(a) if fetch else []
        urls += cadth_urls(a) if fetch else []
        urls += iqwig_urls(a) if fetch else []
    try:
        ema = _request(rp._j_ema) if fetch else []
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
    for u in sorted(dict.fromkeys(urls), key=lambda u: agency_of(u) == "FDA" and not _fda_review(u)):
        a = agency_of(u)
        if a and per.get(a, 0) < (MAX_PER_AGENCY_FDA if a == "FDA" else MAX_PER_AGENCY):
            per[a] = per.get(a, 0) + 1
            capped.append(u)
    for u in capped:
        if not ga.disk_ok():                       # Mahmood 6 Oct: work only while C: and F: each keep >= 5 GB free
            print("DISK_FLOOR: stopped holding documents", slug, flush=True)
            break
        txt, rec = cadth_fetch_text(u) if agency_of(u) == "CADTH" else _request(rp.fetch_text, u)
        licence = rec.get("licence") if agency_of(u) == "CADTH" else licence_from_text(u, txt)
        r = {"url": u, "agency": agency_of(u), "licence": licence, "state": rec.get("state"),
             "doc_sha256": rec.get("sha256"), "bytes": rec.get("bytes"),
             "text_sha256": text_sha256(txt) if txt else None, "text_chars": len(txt or "")}
        if rec.get("state") == "FETCH_FAILED":
            r["fetch_error"] = str(rec.get("http_status") or rec.get("error") or "UNKNOWN")[:120]
        if agency_of(u) == "CADTH":
            r["licence"] = r["licence"] or licence_of(u)
            r["redaction_blocks"] = (txt or "").count("\u2588")
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


_ACR_TOK = re.compile(r"[A-Z0-9][A-Z0-9-]*")


def _label_acronyms(label):
    """The label's acronym PHRASES (maximal runs of upper-case / numeral tokens, NCT ids and bare years excluded). A run of
    several tokens names the trial only WHOLE ('ODYSSEY COMBO I'), or without its programme prefix when two or more
    tokens remain ('COMBO I', 'FH II'); a lone programme or fragment token ('ODYSSEY', 'COMBO', 'JAPAN') never does: it
    names every sibling trial (13 Oct, G-BA pilot). A one-token acronym ('DESCARTES') and a hyphenated mixed-case
    acronym ('BACC-Bay') name the trial as before."""
    out, run = set(), []

    def flush():
        if len(run) == 1:
            out.add(run[0])
        elif len(run) > 1:
            out.add(" ".join(run))
            if len(run) > 2:
                out.add(" ".join(run[1:]))
        run.clear()
    for tok in re.findall(r"[A-Za-z0-9][A-Za-z0-9-]*", re.sub(r"\s+-\s+", "-", label or "")):
        acr = _ACR_TOK.fullmatch(tok) and re.search(r"[A-Z]", tok) and not re.fullmatch(r"NCT\d+", tok)
        if acr:
            run.append(tok)
            continue
        flush()
        if re.fullmatch(r"[A-Z]{3,}-[A-Za-z0-9]+", tok):
            out.add(tok)
    flush()
    return out


def trial_names(label, ncts, acronym=None, codes=()):
    """Strings that NAME this trial in a document. A code shorter than 5 characters or a bare number names nothing."""
    names = set(n for n in ncts if n)
    if acronym:
        names.add(acronym)
    names |= _label_acronyms(label)
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


def binding_for(slug, label, url, text_sha256):
    """Only a complete, digest-bound ruling can resolve a held effect's scope."""
    try:
        rulings = _load(os.path.join(ROOT, BINDINGS))
    except (OSError, ValueError):
        return None
    r = rulings.get(f"{slug}|{label}|{text_sha256}") if isinstance(rulings, dict) else None
    required = ("arm", "outcome", "timepoint", "population", "analysis_set", "ruled_by", "ruled_on", "decision", "reason")
    if not isinstance(r, dict) or not all(isinstance(r.get(k), str) and r[k].strip() for k in required):
        return None
    if r["decision"] not in ("BOUND", "NOT_BOUND") or ("url" in r and r["url"] != url):
        return None
    return r


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


def typed_effect(text, names, terms, measure="HR"):
    """A nearby trial name and explicit 95% CI identify a candidate, never its population binding."""
    from harness import lexicon
    if measure != "HR":
        return []
    num = r"\d+(?:\.\d+)?"
    ci = r"95\s*%\s*(?:CI|confidence\s+interval)\b"
    pattern = re.compile(
        rf"\b(?:hazard\s+ratio|HR)\b\s*[,:]?\s*(?P<effect>{num})\s*"
        rf"(?:[;,]?\s*(?P<ci>{ci})\s*[,:]?\s*|(?P<paren>\()\s*(?:(?P<pci>{ci})\s*[,:]?\s*)?)"
        rf"(?P<lower>{num})\s*(?:to|[-–]|,)\s*(?P<upper>{num})(?!\d|[.,]\d)(?(paren)\s*\))", re.I)
    mentions = named_at(text, names)
    out = []
    for m in pattern.finditer(text):
        preceding = [(off, name) for off, name in mentions if off + len(name) <= m.start()]
        if not preceding:
            continue
        off, name = preceding[-1]
        if m.end() - off > 600:
            continue
        span = text[off:m.end()]
        if re.search(r"pool|pooled|meta-analys|global|integrated|across\s+studies|combined\s+analysis",
                     text[off + len(name):m.start()], re.I):
            continue
        if not (m.group("ci") or m.group("pci") or re.search(ci, text[off:m.start()], re.I)):
            continue
        if not any(t and lexicon.fold(t) in lexicon.fold(span) for t in terms):
            continue
        effect, lower, upper = (float(m.group(k)) for k in ("effect", "lower", "upper"))
        if 0 < lower < effect < upper:
            out.append({"effect": effect, "lower": lower, "upper": upper, "span": span, "offset": off})
    return out


def regulatory_typed_effect(held_reg, terms, measure="HR"):
    """Disagreement anywhere in the held documents prevents choosing an effect."""
    got = []
    for url, h in sorted((held_reg or {}).items()):
        if url.startswith("_") or not isinstance(h, dict):
            continue
        for hit in typed_effect(h["text"], h["names"], terms, measure):
            value = {k: hit[k] for k in ("effect", "lower", "upper")}
            got.append((url, h["record"], dict(value, measure=measure), hit["span"]))
    uniq = {(g[2]["effect"], g[2]["lower"], g[2]["upper"]) for g in got}
    return got[0] if len(uniq) == 1 else None
