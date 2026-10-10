"""STAGE B (full read) of the sglt2-ckd comparator-swap screen for the stage-A SURVIVORS, under D17 (Captain ruling 6,
10 Oct): a host-page Creative Commons licence may admit a text to a prompt. The pre-registered procedure is g1_swap's,
unchanged (rule, SCREEN_INSTR / SCREEN_SCHEMA prompt, gate_screen quote gate, one recorded codex call per candidate);
only the TEXT SOURCE differs: the candidate's CC BY / CC0 open location (Unpaywall) fetched from its host page, instead of
a PMC JATS copy (none exists for these).

Licence (D17, typed, recorded per candidate): the licence statement is captured VERBATIM from the fetched host page
(a creativecommons.org licence link and/or a 'Creative Commons ...' sentence). Only CC BY (no NC/ND) or CC0 admits the
text. NC / ND / no statement / a bot challenge / a stub page -> the text NEVER enters a prompt, and the state says why.
No paywall is crossed and no challenge is solved.

    python scripts/g1_swap_fullread_d17.py SLUG [--run]
      -> registry/comparator_selection/<slug>.d17_fullread.json (states, licence spans, verdicts); raw host pages are held
         under C:/mh-tmp/kgap/d17/ with their sha256 recorded (the prompt record carries the admitted text)
"""
from __future__ import annotations

import concurrent.futures as cf
import datetime
import hashlib
import html as _html
import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_swap as sw  # noqa: E402  (main's, unchanged: rule, prompt, schema, gate)

RAW = "C:/mh-tmp/kgap/d17"
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "swap_screen")
_CC_LINK = re.compile(r'https?://creativecommons\.org/(licenses|publicdomain)/([a-z0-9.-]+)/?([0-9.]*)', re.I)
_CC_SENT = re.compile(r"[^.<>]{0,200}Creative Commons[^.<>]{0,250}", re.I)
_CHALLENGE = re.compile(r"cf-chl|Just a moment\.\.\.|captcha|challenge-platform|Attention Required|Client Challenge",
                        re.I)
_PDF_META = re.compile(r'<meta\s+name="citation_pdf_url"\s+content="([^"]+)"', re.I)


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def licence_of(page):
    """(class, verbatim spans). class: CC_BY / CC0 (admits) or CC_NC_ND / NONE (refuses)."""
    links = sorted({m.group(0) for m in _CC_LINK.finditer(page)})
    sents = [re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", m.group(0)))).strip()
             for m in _CC_SENT.finditer(page)][:3]
    kinds = {m.group(2).lower() for m in _CC_LINK.finditer(page)}
    if any(k in kinds for k in ("by-nc", "by-nd", "by-nc-nd", "by-nc-sa", "by-sa")) or \
            any(re.search(r"non-?commercial|no ?deriv", s, re.I) for s in sents):
        cls = "CC_NC_ND_OR_SA"
    elif "by" in kinds or any(re.search(r"Creative Commons Attribution(?! ?-? ?Non)(?! ?-? ?No ?Deriv)", s) for s in sents):
        cls = "CC_BY"
    elif "zero" in kinds or "publicdomain" in " ".join(links).lower():
        cls = "CC0"
    else:
        cls = "NONE"
    return cls, {"links": links, "sentences": sents}


def page_text(page):
    t = re.sub(r"(?is)<(script|style|noscript|nav|header|footer)\b.*?</\1>", " ", page)
    t = _html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t).strip()


def is_full_text(text):
    """A full text, not a stub / abstract / app shell: an 8000-char floor only. Whether it is a meta-analysis with
    methods is the RULE's question (C2-C6), answered by the recorded reader -- never pre-judged here (a methods/results
    test refused 37705832, a complete narrative review)."""
    return len(text) >= 8000


def _hold(pmid, b, ext):
    sha = hashlib.sha256(b or b"").hexdigest()
    os.makedirs(RAW, exist_ok=True)
    path = f"{RAW}/{pmid}_{sha[:12]}.{ext}"
    open(path, "wb").write(b or b"")
    return sha, path


def via_pmc_jats(pmid):
    """Route 1: the Europe PMC full-text JATS of the article's PMC copy. Its own <license> element is the host's
    licence statement (captured verbatim). Admits only CC BY / CC0 (D17)."""
    from harness import http
    st, b = http.get_raw("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                         {"query": f"EXT_ID:{pmid} AND SRC:MED", "resultType": "core", "format": "json"}, tries=2, timeout=60)
    r = ((json.loads(b).get("resultList") or {}).get("result") or [{}])[0] if st == 200 else {}
    pmcid = r.get("pmcid")
    if not pmcid:
        return None
    st, b = http.get_raw(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", None, tries=2, timeout=90)
    att = {"route": "EUROPEPMC_JATS", "url": f"europepmc rest {pmcid}/fullTextXML", "status": st}
    if st != 200 or not b:
        return dict(att, state=f"HTTP_{st}")
    sha, path = _hold(pmid, b, "xml")
    x = b.decode("utf-8", "replace")
    lic = re.search(r"<license\b.*?</license>", x, re.S)
    span = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", lic.group(0)))).strip() if lic else ""
    cls, spans = licence_of((lic.group(0) if lic else "") + " " + span)
    spans["license_element"] = span[:500]
    text = sw.jats_text(x)
    return dict(att, sha256=sha, held=path, licence_class=cls, licence_spans=spans, text_chars=len(text), _text=text)


def via_pdf(pmid, url):
    """Route 2: the CC location's PDF; the licence sentence is captured from the PDF's own text."""
    from harness import http
    import pypdf
    st, b = http.get_raw(url, None, tries=2, timeout=120)
    att = {"route": "PDF", "url": url, "status": st}
    if st != 200 or not (b or b"").startswith(b"%PDF"):
        return dict(att, state=("BOT_CHALLENGE" if b and _CHALLENGE.search(b[:20000].decode("utf-8", "replace"))
                                else f"NOT_PDF_OR_HTTP_{st}"))
    sha, path = _hold(pmid, b, "pdf")
    try:
        text = re.sub(r"\s+", " ", " ".join((pg.extract_text() or "") for pg in pypdf.PdfReader(io.BytesIO(b)).pages))
    except Exception as exc:  # noqa: BLE001 - typed
        return dict(att, sha256=sha, held=path, state="PDF_UNREADABLE", error=str(exc)[:120])
    cls, spans = licence_of(text)
    return dict(att, sha256=sha, held=path, licence_class=cls, licence_spans=spans, text_chars=len(text), _text=text)


def _decide(att, row, pmid):
    """Admit a route's text only under CC BY / CC0 and only when it is a full text."""
    text = att.pop("_text", None)
    row.setdefault("attempts", []).append(att)
    if text is None or att.get("licence_class") not in ("CC_BY", "CC0"):
        att.setdefault("state", "LICENCE_" + str(att.get("licence_class")))
        return None
    if not is_full_text(text):
        att["state"] = "STUB_OR_ABSTRACT_ONLY"
        return None
    att["state"] = "ADMITTED_D17"
    return dict(row, state="ADMITTED_D17", text=text, source=att)


def acquire(pmid, doi):
    from harness import http
    row = {"pmid": pmid, "doi": doi, "fetched": now()}
    try:
        att = via_pmc_jats(pmid)
    except Exception as exc:  # noqa: BLE001 - next route
        att = {"route": "EUROPEPMC_JATS", "state": "FETCH_FAILED", "error": str(exc)[:120]}
    if att:
        got = _decide(att, row, pmid)
        if got:
            return got
    try:
        u0 = http.get_json(f"https://api.unpaywall.org/v2/{doi}", {"email": sw.CONTACT}, tries=2)
        for l in u0.get("oa_locations") or []:
            if str(l.get("license") or "") in ("cc-by", "cc0", "public-domain") and l.get("url_for_pdf"):
                try:
                    got = _decide(via_pdf(pmid, l["url_for_pdf"]), row, pmid)
                except Exception as exc:  # noqa: BLE001 - next location
                    row.setdefault("attempts", []).append({"route": "PDF", "url": l["url_for_pdf"],
                                                           "state": "FETCH_FAILED", "error": str(exc)[:120]})
                    got = None
                if got:
                    return got
    except Exception as exc:  # noqa: BLE001 - fall through to the landing pages
        row.setdefault("attempts", []).append({"route": "UNPAYWALL", "state": "FETCH_FAILED", "error": str(exc)[:120]})
    try:
        u = http.get_json(f"https://api.unpaywall.org/v2/{doi}", {"email": sw.CONTACT}, tries=2)
    except Exception as exc:  # noqa: BLE001 - typed
        return dict(row, state="UNPAYWALL_FAILED", error=str(exc)[:160])
    locs = [l for l in u.get("oa_locations") or [] if str(l.get("license") or "") in ("cc-by", "cc0", "public-domain")]
    row["unpaywall_cc_locations"] = [{"url": l.get("url"), "license": l.get("license"), "host_type": l.get("host_type")}
                                     for l in locs]
    for l in locs:
        url = l.get("url_for_landing_page") or l.get("url")
        if not url:
            continue
        try:
            st, b = http.get_raw(url, None, tries=2, timeout=90)
        except Exception as exc:  # noqa: BLE001 - next location
            row.setdefault("attempts", []).append({"url": url, "state": "FETCH_FAILED", "error": str(exc)[:120]})
            continue
        page = (b or b"").decode("utf-8", "replace")
        sha = hashlib.sha256(b or b"").hexdigest()
        os.makedirs(RAW, exist_ok=True)
        path = f"{RAW}/{pmid}_{sha[:12]}.html"
        open(path, "wb").write(b or b"")
        att = {"url": url, "status": st, "sha256": sha, "bytes": len(b or b""), "held": path}
        if st != 200 or _CHALLENGE.search(page[:20000]):
            row.setdefault("attempts", []).append(dict(att, state="BOT_CHALLENGE" if _CHALLENGE.search(page[:20000])
                                                       else f"HTTP_{st}"))
            continue
        cls, spans = licence_of(page)
        text = page_text(page)
        att.update(licence_class=cls, licence_spans=spans, text_chars=len(text))
        row.setdefault("attempts", []).append(att)
        if cls not in ("CC_BY", "CC0"):
            continue
        if not is_full_text(text):
            # a repository record page (HAL) states the licence and links the deposited file: admit that file's text
            # under the HOST PAGE's licence, captured verbatim above (D17)
            m = _PDF_META.search(page)
            if m:
                try:
                    pa = via_pdf(pmid, _html.unescape(m.group(1)))
                except Exception as exc:  # noqa: BLE001 - typed
                    pa = {"route": "PDF", "url": m.group(1), "state": "FETCH_FAILED", "error": str(exc)[:120]}
                if pa.get("_text") is not None:
                    pa["licence_class"], pa["licence_spans"] = cls, dict(spans, basis="host record page (D17), "
                                                                         "file linked by its citation_pdf_url")
                got = _decide(pa, row, pmid)
                if got:
                    return got
            att["state"] = "STUB_OR_ABSTRACT_ONLY"
            continue
        att["state"] = "ADMITTED_D17"
        return dict(row, state="ADMITTED_D17", text=text, source=att)
    states = [a.get("state") or a.get("licence_class") for a in row.get("attempts") or []]
    return dict(row, state="NOT_ADMITTED", why=states or ["no CC BY / CC0 location"])


def main(argv):
    slug = next(a for a in argv if not a.startswith("--"))
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    import k_gap_forest_plot as fp
    sel = sw._j(os.path.join(sw.SEL, f"{slug}.unread_reads.json"))
    srch = sw._j(os.path.join(sw.SEL, f"{slug}.search.json"))["records"]
    rule_ = sw._j(os.path.join(sw.SEL, f"{slug}.rule.json"))
    p = sw.protocol(slug)
    out_p = os.path.join(sw.SEL, f"{slug}.d17_fullread.json")
    led = json.load(open(out_p, encoding="utf-8")) if os.path.exists(out_p) else {"rows": {}}
    crit = "\n".join(f"{c['id']}: PASS if {c['pass_if']}" for c in rule_["criteria"] if c["id"] != "C1_OPEN_LICENCE")
    items = []
    for pmid in sel["survivors"]:
        r = led["rows"].get(pmid) or {}
        if r.get("state") != "ADMITTED_D17" or not os.path.exists(r.get("source", {}).get("held", "")):
            r = acquire(pmid, (srch.get(pmid) or {}).get("doi"))
            time.sleep(1)
        if r.get("state") == "ADMITTED_D17":
            text = r.pop("text", None) or page_text(open(r["source"]["held"], encoding="utf-8", errors="replace").read())
            prompt = (sw.SCREEN_INSTR + f"\n\nPROTOCOL: {p['question']}\nPRIMARY OUTCOME: {p['primary_outcome']} "
                      f"(estimand {p['estimand']}, timepoint {p['timepoint']})\nCRITERIA:\n{crit}\n<<<TEXT\n"
                      f"{text[:180000]}\nTEXT>>>\n").encode("utf-8")
            items.append((pmid, prompt, text, r))
        led["rows"][pmid] = r
        print(pmid, r.get("state"), (r.get("source") or {}).get("licence_class", ""), flush=True)
    # the call-time licence guard (reproducible_ai/record_licence.text_block_problems) admits a text block only from a
    # DECLARED source that resolves, from HELD data, to a CC licence. The held Unpaywall text index is that data for a
    # DOI: each admitted text is recorded there with its url, sha256 and the host page's licence statement VERBATIM (D17),
    # and the call declares 'DOI <doi>'. The guard itself is unchanged.
    upw_p = os.path.join(ROOT, "outputs", "k_gap", "unpaywall_text_index.json")
    upw = json.load(open(upw_p, encoding="utf-8")) if os.path.exists(upw_p) else {}
    for pmid, _prompt, _text, r in items:
        s = r["source"]
        upw[str(r["doi"]).lower()] = {"state": "OA_TEXT", "url": s["url"], "sha256": s["sha256"], "bytes": s.get("bytes"),
                                      "kind": s.get("route") or "HTML", "license": "cc-by" if s["licence_class"] == "CC_BY"
                                      else "cc0", "n_tried": len(r.get("attempts") or []),
                                      "d17_host_licence": s.get("licence_spans"),
                                      "writer": "scripts/g1_swap_fullread_d17.py (D17, signed V12)"}
    json.dump(upw, open(upw_p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False, sort_keys=True)
    if "--run" in argv:
        def one(it):
            pmid, prompt, text, r = it
            psha = hashlib.sha256(prompt).hexdigest()
            if (r.get("call") or {}).get("prompt_sha256") == psha and r["call"].get("state") == "RAN_OK":
                return pmid, r["call"]
            rec = mcl.call(prompt, schema=json.loads(json.dumps(sw.SCREEN_SCHEMA)), model=fp.MODEL, effort=fp.EFFORT,
                           caller={"file": "scripts/g1_swap_fullread_d17.py", "line": "stage B",
                                   "purpose": f"G1 comparator swap: full read of {pmid} for {slug} (C2-C6, rule; D17)"},
                           input_digests=[{"ref": f"DOI {str(r['doi']).lower()} (D17 host-page CC licence; "
                                                  f"{r['source']['url']})", "sha256": r["source"]["sha256"],
                                           "what": f"host page, licence {r['source']['licence_class']} captured verbatim "
                                                   "(D17), rendered to text, first 180000 chars"}], timeout_s=1500)
            ms.write_record(rec, REC_DIR)
            return pmid, {"record_id": rec["record_id"], "state": rec["state"], "prompt_sha256": psha}
        with cf.ThreadPoolExecutor(max_workers=int(next((a.split("=", 1)[1] for a in argv if a.startswith("--workers=")),
                                                       "3"))) as ex:
            for f in cf.as_completed([ex.submit(one, it) for it in items]):
                try:
                    pmid, call = f.result()
                    led["rows"][pmid]["call"] = call
                    print(pmid, call["state"], call["record_id"], flush=True)
                except Exception as exc:  # noqa: BLE001 - named, never dropped
                    print("CALL_FAILED", type(exc).__name__, str(exc)[:200], flush=True)
    for pmid, _prompt, text, r in items:
        c = r.get("call") or {}
        if c.get("state") == "RAN_OK":
            claim = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, c["record_id"] + ".json"))).decode("utf-8"))
            r["criteria"], r["pooled"], r["k"] = sw.gate_screen(claim, text)
            r["passes_all"] = all(v["verdict"] == "PASS" for v in r["criteria"].values())
    led.update(slug=slug, written=now(), writer="scripts/g1_swap_fullread_d17.py",
               rule=f"registry/comparator_selection/{slug}.rule.json",
               licence_basis="D17 (signed V12): host-page Creative Commons licence, captured verbatim; CC BY / CC0 only")
    json.dump(led, open(out_p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print("written", out_p)
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
