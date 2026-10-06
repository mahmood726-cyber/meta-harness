"""Probe regulatory documents (EMA EPARs, FDA Drugs@FDA reviews) for the k-gap rows no open literature source covers.

A regulatory document can hold only a trial that was part of a marketing submission, so the population is first
narrowed deterministically: rows closable by NONE_OPEN_PROBED whose topic's intervention has an EMA-authorised or
FDA-approved product (discovered by INN in the EMA medicines JSON and openFDA drugsfda; no hand list of products).

Per product, typed text only (PDF text layer via pypdf; a scanned review with no text layer is recorded, never OCR'd):
  EMA   <name>-epar-public-assessment-report_en.pdf and <name>-epar-scientific-discussion_en.pdf
  FDA   every application_docs entry typed 'Review' (a TOC page is followed to its PDFs on accessdata.fda.gov)
Per row: is the trial NAMED in any document (acronym / NCT / study code), and if so does an outcome keyword with a
number occur within 400 characters of the name? That is a probe of WHERE numbers may exist, not an extraction:
nothing here enters a pool.

    python scripts/k_gap_regulatory_probe.py        -> outputs/k_gap/regulatory_probe.json
Text caches: outputs/k_gap/_reg/ (gitignored); outputs/k_gap/regulatory_index.json holds url, sha256, bytes, state.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from kgap import k_gap  # noqa: E402
from harness import http, lexicon  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
REG = os.path.join(OUT, "_reg")
IDX = os.path.join(OUT, "regulatory_index.json")
EMA_JSON = "https://www.ema.europa.eu/en/documents/report/medicines-output-medicines_json-report_en.json"
MAX_FDA_DOCS = 30


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _idx():
    return _j(IDX) if os.path.exists(IDX) else {}


def fetch_text(url):
    """Typed text of one document, cached by url; records state (TEXT / NO_TEXT_LAYER / NOT_PDF / FETCH_FAILED)."""
    os.makedirs(REG, exist_ok=True)
    key = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    fp = os.path.join(REG, key + ".txt")
    idx = _idx()
    if os.path.exists(fp) and url in idx:
        return open(fp, encoding="utf-8").read(), idx[url]
    try:
        st, b = http.get_raw(url, tries=2, timeout=180)
    except Exception as exc:  # noqa: BLE001
        rec = {"state": "FETCH_FAILED", "error": str(exc)[-160:]}
        idx[url] = rec
        json.dump(idx, open(IDX, "w", encoding="utf-8"), indent=1, sort_keys=True)
        return "", rec
    if b[:4] != b"%PDF":
        rec = {"state": "NOT_PDF", "http_status": st, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
        txt = b.decode("utf-8", "replace") if url.endswith((".html", ".htm")) else ""
    else:
        txt = k_gap._pdf_text(b)
        rec = {"state": "TEXT" if len(txt) >= 2000 else "NO_TEXT_LAYER", "http_status": st, "bytes": len(b),
               "sha256": hashlib.sha256(b).hexdigest(), "text_chars": len(txt)}
    open(fp, "w", encoding="utf-8").write(txt)
    idx[url] = rec
    json.dump(idx, open(IDX, "w", encoding="utf-8"), indent=1, sort_keys=True)
    return txt, rec


def ema_products(agents, ema):
    out = []
    for m in ema:
        subst = lexicon.fold(" ".join(str(m.get(k) or "") for k in ("active_substance", "international_non_proprietary_name_common_name", "inn_common_name")))
        if m.get("category", "Human") != "Human":
            continue
        if any(a and re.search(r"\b" + re.escape(lexicon.fold(a)) + r"\b", subst) for a in agents):
            name = str(m.get("name_of_medicine") or m.get("medicine_name") or "").strip()
            if name:
                out.append(name)
    return sorted(set(out))


def ema_docs(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    base = "https://www.ema.europa.eu/en/documents/"
    return [base + f"assessment-report/{slug}-epar-public-assessment-report_en.pdf",
            base + f"scientific-discussion/{slug}-epar-scientific-discussion_en.pdf"]


EMA_DOC_INDEX = "https://www.ema.europa.eu/en/documents/report/documents-output-json-report_en.json"
EMA_REPORT_TYPES = ("assessment-report", "variation-report", "scientific-discussion")


def ema_index_docs(names, index):
    """Every assessment / variation / extension report EMA's own documents index lists for these medicines (exact
    medicine name, case-folded): a new indication lives in a VARIATION report, not the initial EPAR."""
    want = {str(n).strip().lower() for n in names if n}
    return sorted({x["document_url"] for x in index or []
                   if x.get("type") in EMA_REPORT_TYPES and str(x.get("medicine_name") or "").strip().lower() in want
                   and str(x.get("document_url") or "").endswith(".pdf")})


def ema_doc_index():
    """EMA's documents index (JSON, ~37 MB), fetched once per run; its sha256 is returned with it. [] when unreachable."""
    import hashlib
    try:
        st, b = http.get_raw(EMA_DOC_INDEX, None, tries=2)
        return (json.loads(b.decode("utf-8")).get("data") or []), hashlib.sha256(b).hexdigest()
    except Exception:  # noqa: BLE001 - index unavailable: only the initial EPAR urls, never a guess
        return [], None


def fda_docs(agent):
    try:
        d = http.get_json("https://api.fda.gov/drug/drugsfda.json",
                          {"search": f'openfda.generic_name:"{agent}"', "limit": "20"}, tries=2)
    except Exception:  # noqa: BLE001 - no application for this INN is a result, not an error
        return []
    urls = []
    for r in d.get("results", []):
        for s in r.get("submissions", []):
            for dd in s.get("application_docs") or []:
                if (dd.get("type") or "").lower() == "review" and dd.get("url"):
                    urls.append(dd["url"].replace("http://", "https://"))
    out = []
    for u in dict.fromkeys(urls):
        if u.endswith(".pdf"):
            out.append(u)
        else:                                   # a TOC page: follow its PDFs on the same host
            txt, rec = fetch_text(u)
            for m in re.finditer(r'href="([^"]+\.pdf)"', txt, re.I):
                h = m.group(1)
                out.append(h if h.startswith("http") else u.rsplit("/", 1)[0] + "/" + h)
    return list(dict.fromkeys(out))[:MAX_FDA_DOCS]


def row_names(r):
    st = next((v for v in (r.get("study") or {}).values() if v), {}) or {}
    names = set(r.get("ncts") or [])
    if st.get("acronym"):
        names.add(st["acronym"])
    for tok in re.findall(r"\b[A-Z][A-Z0-9]{2,}(?:[- ][A-Z0-9]+)*\b", r["label"]):
        if tok not in ("NCT",) and not tok.isdigit():
            names.add(tok)
    m = re.match(r"\s*([A-Z][a-zA-Z'’-]+)", r["label"])
    if m and not names:
        names.add(m.group(1))                  # first-author surname only when nothing more specific exists
    return sorted(n for n in names if len(n) >= 3)


def main():
    T = _j(os.path.join(OUT, "k_gap_table.json"))
    rows = [r for r in T["trials"] if "NONE_OPEN_PROBED" in (r.get("closable_by") or [])]
    ema = _j_ema()
    res, tally = [], Counter()
    by_slug = {}
    for r in rows:
        by_slug.setdefault(r["slug"], []).append(r)
    for slug, rs in sorted(by_slug.items()):
        cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
        agents = [a for a in (cfg.get("intervention_agents") or cfg.get("intervention_terms") or []) if len(a) >= 4]
        prods = ema_products(agents, ema)
        docs = [u for p in prods for u in ema_docs(p)]
        for a in agents[:3]:
            docs += fda_docs(a)
        texts = []
        for u in dict.fromkeys(docs):
            t, rec = fetch_text(u)
            if rec.get("state") == "TEXT":
                texts.append((u, t))
        kw = [lexicon.fold(k) for k in (cfg.get("primary_outcome") or {}).get("keywords") or []]
        for r in rs:
            names = row_names(r)
            found, near = [], []
            for u, t in texts:
                for n in names:
                    for m in re.finditer(r"(?<![A-Za-z0-9])" + re.escape(n) + r"(?![A-Za-z0-9])", t):
                        found.append(u)
                        w = lexicon.fold(t[max(0, m.start() - 400): m.end() + 400])
                        if any(k and k in w for k in kw) and re.search(r"\d+\s*\(\d|\d\.\d+\s*\(|\bci\b|\d+/\d+", w):
                            near.append({"doc": u, "name": n, "window": t[max(0, m.start() - 150): m.end() + 250]})
                        break
            state = ("NO_REGULATORY_PRODUCT" if not prods and not docs else "NO_DOC_TEXT" if not texts
                     else "NAMED_WITH_OUTCOME_NUMBERS" if near else "NAMED_ONLY" if found else "NOT_NAMED")
            tally[state] += 1
            res.append({"slug": slug, "label": r["label"], "gap_class": r["gap_class"], "names_searched": names,
                        "ema_products": prods, "n_docs": len(docs), "n_docs_text": len(texts), "state": state,
                        "docs_naming": sorted(set(found))[:6], "near": near[:3]})
        print(slug, prods, "docs", len(docs), "text", len(texts), dict(Counter(x["state"] for x in res if x["slug"] == slug)), flush=True)
    out = {"n_rows": len(res), "tally": dict(tally), "rows": res}
    json.dump(out, open(os.path.join(OUT, "regulatory_probe.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps({"n_rows": len(res), "tally": dict(tally)}, indent=1))


def _j_ema():
    fp = os.path.join(REG, "ema_medicines.json")
    os.makedirs(REG, exist_ok=True)
    if not os.path.exists(fp):
        b = http.get(EMA_JSON, tries=2, timeout=180)
        open(fp, "wb").write(b)
    d = json.load(open(fp, encoding="utf-8"))
    return d.get("data") or d.get("medicines") or d if isinstance(d, (list, dict)) else []


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
