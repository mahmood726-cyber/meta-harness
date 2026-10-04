"""G1 tocilizumab: READ the primary full texts the cascade fetched but may not hold (VERIFIED_NOT_HELD), with the lane's
own binding rule and extractors, and commit only what was read: the PMCID, the body sha256, the binding, and each
candidate's counts with its short verbatim span. Never the text.

Why: the cascade records a not-held paper as {pmcid, fulltext_sha256} and drops the body, so its binding
(g1_toci_cascade.binding) and every extractor (held_texts -> assess) saw the ABSTRACT only. COVIDSTORM's report (PMID
35259529, PMC8897958) names NCT04577534 in its body but not in its abstract, so it was 'UNBOUND: names no registration'
and the trial was counted 'structurally unreachable' while its own Table 3 states 'Death at day 28, n (%) 1 (1.8) 0 (0)'
under 'Tocilizumab group ( n = 57) Standard-of-care group ( n = 29)'.

Per not-held paper: fetch the body (Europe PMC fullTextXML, then NCBI efetch db=pmc); it is READ only if its sha256 equals
the one the cascade recorded (else SHA_MISMATCH, nothing read); bind with g1_toci_cascade.binding over the body; for each
bound trial run g1.tocilizumab's table / text / safety extractors over the body, exactly as for a held text.

  python scripts/g1_toci_vnh_read.py            (online) -> g1/data/vnh_reads.json
  python scripts/g1_toci_vnh_read.py --verify   (online) re-fetch, re-check every sha256 and that every span is verbatim
"""
import hashlib
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from g1 import tocilizumab as g  # noqa: E402
import g1_toci_cascade as c  # noqa: E402

ACQ = os.path.join(ROOT, "g1", "data", "acquired")
OUT = os.path.join(ROOT, "g1", "data", "vnh_reads.json")


def fetch(pmcid: str, want: str):
    """(body, route) whose sha256 is `want`, or (None, [routes tried with their sha256])."""
    tried = []
    for route, url, params in (("EPMC_FULLTEXTXML", f"{c.EPMC}/{pmcid}/fullTextXML", None),
                               ("NCBI_EFETCH_PMC", f"{c.EUTILS}/efetch.fcgi",
                                {"db": "pmc", "id": pmcid.replace("PMC", ""), "retmode": "xml"})):
        st, b, u = c.get(url, params)
        time.sleep(0.4)
        if st != 200:
            tried.append(f"{route} http {st}")
            continue
        # the RAW bytes' digest, or (records the cascade hashed as text) the digest of a STRICT decode: a lossy decode
        # ('replace') maps different bytes to the same U+FFFD text and would pass a body that is not the recorded one
        # (codex NR-C26)
        try:
            x = b.decode("utf-8")
        except UnicodeDecodeError:
            tried.append(f"{route} not valid UTF-8 (refused)")
            continue
        if want in (hashlib.sha256(b).hexdigest(), hashlib.sha256(x.encode("utf-8")).hexdigest()):
            return x, route
        tried.append(f"{route} sha256 {hashlib.sha256(b).hexdigest()[:12]}")
    return None, tried


def read(a: dict, body: str) -> dict:
    labels, why = c.binding(dict(a, fulltext=body))
    t = g._fold(body)
    cands = []
    for label in labels:
        for kind, fn in (("SAFETY_TABLE", g.safety_candidates), ("TEXT", g.text_candidates), ("TABLE", g.table_candidates)):
            for x in fn(body):
                cands.append(dict({k: x[k] for k in g._KEY}, label=label, extractor=kind,
                                  denominator_kind=x["denominator_kind"], span=x["span"]))
    return {"binding": why, "bound_labels": labels, "candidates": cands,
            "itt_stated": bool(re.search(r"intention[- ]to[- ]treat|all randomi[sz]ed", t, re.I))}


def main(verify=False):
    prev = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    out, bad = {}, []
    for f in sorted(os.listdir(ACQ)):
        if not re.match(r"\d+\.json$", f):
            continue
        a = json.load(open(os.path.join(ACQ, f), encoding="utf-8"))
        if not isinstance(a, dict) or not (a.get("fulltext_state") or "").startswith("VERIFIED_NOT_HELD") or not a.get("pmcid"):
            continue
        body, route = fetch(a["pmcid"], a["fulltext_sha256"])
        rec = {"pmcid": a["pmcid"], "body_sha256": a["fulltext_sha256"], "title": (a.get("title") or "")[:160]}
        if body is None:
            out[a["pmid"]] = dict(rec, state="SHA_MISMATCH (nothing read)", tried=route)
            continue
        rec.update(state="VERIFIED_NOT_HELD", fetched_by=route, licence_in_bytes=c.bytes_licence(body))
        rec.update(read(a, body))
        if verify:
            t = g._fold(body)
            miss = [x["span"] for x in rec["candidates"] if x["span"].split(" ... ")[-1] not in t]
            old = prev.get(a["pmid"])
            if miss or (old and old.get("candidates") != rec["candidates"]):
                bad.append(a["pmid"])
        out[a["pmid"]] = rec
    if verify:
        print("VERIFY", "FAIL " + ", ".join(bad) if bad else f"OK ({len(out)} papers)")
        return 1 if bad else 0
    open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    for p, r in out.items():
        print(p, r["state"][:20], r.get("bound_labels"), r.get("binding", "")[:60],
              [(x["label"], x["extractor"], tuple(x[k] for k in g._KEY)) for x in r.get("candidates") or []])
    return 0


if __name__ == "__main__":
    sys.exit(main("--verify" in sys.argv))
