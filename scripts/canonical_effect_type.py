"""Canonical effect type from the METHODS, not the label (reviews 13 / 20): RALES and RE-LY report a "relative risk" that
is a Cox (time-to-event) estimate, so its canonical type is HR. The source wording and the canonical type are separate
fields; nothing about a value changes, only which measure it is compared on.

Candidates: every served PRIMARY-outcome trial row labelled RR / OR that carries an estimate and NO arm counts (a
counts-derived ratio is what its label says). Evidence -- regex over held bytes only (D8: no prompt), each tied to THE
trial:
  OWN_TEXT_COX      a sentence of the trial's own abstract / held full text that names Cox together with the relative
                    risk / hazard ratio
  LABEL_TIME_TO_EVENT  an FDA label passage (US-government text) on the trial (its acronym) stating its primary endpoint
                    as 'time to ...' AND reporting hazard ratios or a log-rank analysis
ESTABLISHED_HR (with the verbatim span, the document and its sha256) or NOT_ESTABLISHED (what was searched). Never
inferred from the comparator's label (anti-circularity).

    python scripts/canonical_effect_type.py      -> registry/canonical_effect_types.json
"""
from __future__ import annotations

import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "registry", "canonical_effect_types.json")
REG = os.path.join(ROOT, "outputs", "k_gap", "_reg")
_COX = re.compile(r"\bCox\b", re.I)
_EST = re.compile(r"\brelative\s+risks?\b|\bhazard\s+ratios?\b", re.I)
_TTE = re.compile(r"\b(?:primary\s+(?:end\s*-?point|outcome)[^.]{0,80}?\bwas\s+)?time\s+to\s+(?:the\s+)?(?:first\s+)?"
                  r"[a-z][a-z -]{2,60}", re.I)
_HAZ = re.compile(r"\bhazard\s+ratios?\b|\blog[- ]?rank\b", re.I)


def _sentences(t):
    return re.split(r"(?<=[.;])\s+(?=[A-Z(])", re.sub(r"\s+", " ", t or ""))


def own_text_cox(text):
    """The first sentence of the trial's own text naming Cox WITH the relative risk / hazard ratio, or None."""
    for s in _sentences(text):
        if _COX.search(s) and _EST.search(s):
            return s[:300]
    return None


def label_time_to_event(text, acronym):
    """(span) when an FDA label passage on `acronym` states a 'time to' primary endpoint and reports hazard ratios or
    a log-rank analysis within the same passage (2,500 characters from a mention of the trial), else None."""
    t = re.sub(r"\s+", " ", text or "")
    for m in re.finditer(r"\b" + re.escape(acronym) + r"\b", t):
        win = t[m.start():m.start() + 2500]
        tte = _TTE.search(win)
        if tte and _HAZ.search(win) and re.search(r"\b" + re.escape(acronym) + r"\b", win[:tte.end() + 200]):
            hz = _HAZ.search(win)
            return f"{win[max(0, tte.start() - 60):tte.end()].strip()} ... {win[max(0, hz.start() - 40):hz.end() + 40].strip()}"
    return None


def acronym_of(label):
    """'RALES1999' -> 'RALES'; 'RE-LY' -> 'RE-LY'; a bare PMID -> None."""
    a = re.sub(r"\s*(?:19|20)\d\d$", "", str(label or "")).strip()
    return a if a and not a.isdigit() and not a.upper().startswith("PMID") else None


def _reg_urls():
    """{_reg file key: url} from every regulatory index this checkout or its R9-4 branch knows (the key is the url's
    sha1 prefix, as k_gap_regulatory_probe.fetch_text writes it)."""
    urls = set()
    p = os.path.join(ROOT, "outputs", "k_gap", "regulatory_index.json")
    if os.path.exists(p):
        urls |= set(json.load(open(p, encoding="utf-8")))
    for ref in ("origin/g1/r9-4-fda-label",):
        try:
            urls |= set(json.loads(subprocess.run(["git", "-C", ROOT, "show", f"{ref}:outputs/k_gap/regulatory_index.json"],
                                                  capture_output=True, check=True).stdout))
        except (subprocess.CalledProcessError, ValueError, OSError):
            pass
    return {hashlib.sha1(u.encode("utf-8")).hexdigest()[:16]: u for u in urls}


def candidates():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(f))
        d = json.load(open(f, encoding="utf-8"))
        g1p = os.path.join(ROOT, "outputs", "k_gap", "g1", slug + ".json")
        labels = {x.get("family"): x["label"] for x in json.load(open(g1p, encoding="utf-8"))["trials"]} \
            if os.path.exists(g1p) else {}
        for o in d.get("outcomes") or []:
            if not o.get("primary"):
                continue
            for t in o.get("trials") or []:
                if (t.get("scale") or "").upper() in ("RR", "OR") and t.get("effect") is not None \
                        and t.get("events_t") is None:
                    out.append({"slug": slug, "id": t["id"], "source_wording": (t.get("scale") or "").upper(),
                                "label": labels.get(t["id"]), "source": (t.get("source") or "")[:200]})
    return out


def evidence(c, urls):
    pmid = c["id"].replace("PMID ", "")
    recs = os.path.join(ROOT, "cache", c["slug"], "records.json")
    rec = next((r for r in json.load(open(recs, encoding="utf-8")).get("records", []) if str(r.get("id")) == pmid),
               {}) if os.path.exists(recs) else {}
    texts = [("PubMed abstract", rec.get("abstract") or "", None)]
    ft = os.path.join(ROOT, "cache", c["slug"], f"ft_{pmid}.txt")
    if os.path.exists(ft):
        texts.append((os.path.relpath(ft, ROOT).replace("\\", "/"), open(ft, encoding="utf-8", errors="replace").read(),
                      hashlib.sha256(open(ft, "rb").read()).hexdigest()))
    searched = [s for s, _, _ in texts]
    for src, t, sha in texts:
        span = own_text_cox(t)
        if span:
            return {"state": "ESTABLISHED_HR", "rule": "OWN_TEXT_COX", "document": src, "sha256": sha, "span": span,
                    "searched": searched}
    acr = acronym_of(c.get("label"))
    if acr and os.path.isdir(REG):
        for f in sorted(glob.glob(os.path.join(REG, "*.txt"))):
            url = urls.get(os.path.basename(f)[:-4])
            if not url or "accessdata.fda.gov" not in url:          # US-government text only
                continue
            t = open(f, encoding="utf-8", errors="replace").read()
            searched.append(url)
            span = label_time_to_event(t, acr)
            if span:
                return {"state": "ESTABLISHED_HR", "rule": "LABEL_TIME_TO_EVENT", "document": url,
                        "text_sha256": hashlib.sha256(t.encode("utf-8")).hexdigest(), "span": span[:400],
                        "acronym": acr, "searched_n": len(searched)}
    return {"state": "NOT_ESTABLISHED", "acronym": acr, "searched": searched[:3], "searched_n": len(searched)}


def build():
    urls = _reg_urls()
    out = {}
    for c in candidates():
        out[f"{c['slug']}|{c['id']}"] = dict(c, canonical=evidence(c, urls))
    return out


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    res = build()
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"rule": "canonical effect type from the methods (r13/r20); source wording kept separately",
                   "rows": res}, fh, indent=1, ensure_ascii=False)
    for k, v in res.items():
        e = v["canonical"]
        print(k, v["source_wording"], "->", e["state"], e.get("rule"), (e.get("span") or "")[:140])
