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
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT =os.path.join(ROOT, "registry", "canonical_effect_types.json")
REG = os.path.join(ROOT, "outputs", "k_gap", "_reg")
_COX = re.compile(r"\bCox\b", re.I)
_EST = re.compile(r"\brelative\s+risks?\b|\bhazard\s+ratios?\b", re.I)
_TTE = re.compile(r"\b(?:primary\s+(?:end\s*-?point|outcome)[^.]{0,80}?\bwas\s+)?time\s+to\s+(?:the\s+)?(?:first\s+)?"
                  r"[a-z][a-z -]{2,60}", re.I)
_HAZ = re.compile(r"\bhazard\s+ratios?\b|\blog\s*-?\s*rank\b", re.I)   # PDF text: 'Log- rank'


def _sentences(t):
    return re.split(r"(?<=[.;])\s+(?=[A-Z(])", re.sub(r"\s+", " ", t or ""))


_SECONDARY_OR_OTHER_MODEL = re.compile(r"\bsecondary\b|\bexploratory\b|\bsubgroup|\bonly\s+for\b|log[- ]binomial|"
                                       r"\bpoisson\b|\blogistic\b|mantel", re.I)
_PRIMARY = re.compile(r"\bprimary\s+(?:composite\s+|efficacy\s+)?(?:end\s*-?points?|outcomes?)\b", re.I)


def own_text_cox(text):
    """The first sentence of the trial's own text naming Cox WITH the relative risk / hazard ratio, and naming no
    secondary analysis or other model ('... relative risk from a log-binomial model; Cox only for secondary outcomes'
    establishes nothing), or None."""
    for s in _sentences(text):
        if _COX.search(s) and _EST.search(s) and not _SECONDARY_OR_OTHER_MODEL.search(s):
            return s[:300]
    return None


def label_passage(text, acronym, span=4000):
    """A PROPOSED passage of an FDA label on `acronym` (regex proposer only; readers decide): from a sentence naming
    the trial's PRIMARY endpoint (in a passage that starts at a mention of the trial) through the following
    hazard-ratio / log-rank / Cox / Kaplan-Meier time-to evidence -- stopping at another primary-endpoint sentence
    that does not name the trial, and never using a sentence about a secondary / exploratory / subgroup analysis.
    Returns the passage text or None."""
    t = re.sub(r"\s+", " ", text or "")
    acr = re.compile(r"\b" + re.escape(acronym) + r"\b")
    for m in acr.finditer(t):
        sents = _sentences(t[m.start():m.start() + span])
        p = None
        for k, s in enumerate(sents):
            if _PRIMARY.search(s) and not _SECONDARY_OR_OTHER_MODEL.search(s):
                if p is not None and not acr.search(s):
                    break                                    # another trial's primary endpoint: the passage ends
                if p is None and (acr.search(s) or k <= 12) and not re.search(r"\b[A-Z][A-Z0-9-]{2,}'s\s+primary", s):
                    p = k
                    if acr.search(s) and _TTE.search(s):
                        # the trial's primary endpoint DEFINED as 'time to ...' (RALES): propose it with the sentences
                        # that report its result; the readers decide whether the estimate is time-to-event
                        return " ".join(sents[k:k + 8])[:3000]
                continue
            if p is not None and (_HAZ.search(s) or _COX.search(s) or re.search(r"kaplan[- ]meier[^.]{0,80}time\s+to", s, re.I)) \
                    and not _SECONDARY_OR_OTHER_MODEL.search(s):
                return " ".join(sents[p:k + 1])[:3000]
    return None


def label_time_to_event(text, acronym):
    """Back-compatible proposer: the proposed label passage, or None."""
    return label_passage(text, acronym)


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
                # PROPOSED only: two recorded readers of different families must confirm (readers())
                return {"state": "PROPOSED_LABEL_PASSAGE", "rule": "LABEL_TIME_TO_EVENT", "document": url,
                        "text_sha256": hashlib.sha256(t.encode("utf-8")).hexdigest(), "passage": span,
                        "acronym": acr, "searched_n": len(searched)}
    return {"state": "NOT_ESTABLISHED", "acronym": acr, "searched": searched[:3], "searched_n": len(searched)}


READER_SCHEMA = {"type": "object", "additionalProperties": False,
                 "required": ["primary_estimate_is_time_to_event", "quote", "note"],
                 "properties": {"primary_estimate_is_time_to_event": {"type": "boolean"}, "quote": {"type": "string"},
                                "note": {"type": "string"}}}
READER_INSTR = (
    "Below is a passage of a U.S. FDA drug label (U.S. government text) about the trial {acr}. Question: is the "
    "estimate the label reports for {acr}'s PRIMARY endpoint a time-to-event estimate (a hazard ratio from a "
    "survival / Cox / log-rank analysis of time to the event)? Answer false if the passage does not show this for the "
    "PRIMARY endpoint (a secondary, subgroup or exploratory analysis does not count). Give a VERBATIM quote from the "
    "passage that decides it. Answer only with JSON matching: {schema}")


def _answer(text):
    t = text.strip()
    m = re.fullmatch(r"```(?:json)?\s*(\{.*\})\s*```", t, re.S)
    try:
        return json.loads(m.group(1) if m else t)
    except ValueError:
        return None


def reader_verdict(answer, passage):
    """CONFIRMS only on an explicit true with a non-empty verbatim quote from the passage; anything else does not."""
    norm = lambda s: re.sub(r"\s+", " ", s or "").strip().lower()
    if not isinstance(answer, dict) or not isinstance(answer.get("primary_estimate_is_time_to_event"), bool):
        return "INVALID_REPLY"
    q = norm(answer.get("quote"))
    if not q or q not in norm(passage):
        return "QUOTE_NOT_IN_PASSAGE"
    return "CONFIRMS" if answer["primary_estimate_is_time_to_event"] else "REFUTES"


def readers(key, ev, run):
    """codex + agy (Gemini) over the proposed US-government passage, recorded; both must CONFIRM."""
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    led = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "canonical_effect_type_readers.json")
    prev = json.load(open(led, encoding="utf-8")) if os.path.exists(led) else {}
    p = (READER_INSTR.format(acr=ev["acronym"], schema=json.dumps(READER_SCHEMA)) +
         f"\n\n<<<LABEL PASSAGE ({ev['document']})\n{ev['passage']}\nPASSAGE>>>\n").encode("utf-8")
    ps = hashlib.sha256(p).hexdigest()
    rec_dir = os.path.join(ROOT, "registry", "model_calls")
    dig = [{"ref": f"{ev['document']} (U.S. FDA label, U.S. government work; passage on {ev['acronym']})",
            "sha256": ev["text_sha256"], "what": "the label text the passage is cut from"}]
    caller = {"file": "scripts/canonical_effect_type.py", "line": "readers", "lane": "g1/binding",
              "purpose": f"canonical effect type second reader {key}"}
    out = dict(prev.get(key) or {})
    for who in ("codex", "agy"):
        r0 = out.get(who) or {}
        fp = os.path.join(rec_dir, f"{r0.get('record_id')}.json")
        if os.path.exists(fp) and r0.get("prompt_sha256") == ps:
            rec = ms.load_record(fp)
        elif run:
            rec = (mcl.call(p, schema=READER_SCHEMA, model="gpt-6-astra", effort="high", caller=caller,
                            input_digests=dig, timeout_s=1200) if who == "codex" else
                   mcl.agy_call(p, schema=READER_SCHEMA, caller=caller, input_digests=dig, timeout_s=1200))
            ms.write_record(rec, rec_dir)
        else:
            out[who] = {"state": "NOT_RUN"}
            continue
        a = _answer(ms.replay(rec).decode("utf-8")) if rec.get("state") == "RAN_OK" else None
        out[who] = {"record_id": rec["record_id"], "prompt_sha256": ps, "answer": a,
                    "model_reported": (rec.get("model") or {}).get("id_reported"),
                    "verdict": reader_verdict(a, ev["passage"]) if a is not None else "RAN_ERROR"}
        prev[key] = out
        with open(led, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(prev, fh, indent=1, ensure_ascii=False)
    return out


def build(run=False):
    urls = _reg_urls()
    out = {}
    for c in candidates():
        key = f"{c['slug']}|{c['id']}"
        ev = evidence(c, urls)
        if ev["state"] == "PROPOSED_LABEL_PASSAGE":
            rd = readers(key, ev, run)
            verdicts = {w: (rd.get(w) or {}).get("verdict", (rd.get(w) or {}).get("state")) for w in ("codex", "agy")}
            ok = all(v == "CONFIRMS" for v in verdicts.values())
            ev = dict(ev, readers=verdicts, state="ESTABLISHED_HR" if ok else "NOT_ESTABLISHED",
                      span=next(((rd.get(w) or {}).get("answer") or {}).get("quote") for w in ("codex", "agy")) if ok
                      else None)
        out[key] = dict(c, canonical=ev)
    return out


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    res = build(run="--readers" in sys.argv)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"rule": "canonical effect type from the methods (r13/r20); source wording kept separately",
                   "rows": res}, fh, indent=1, ensure_ascii=False)
    for k, v in res.items():
        e = v["canonical"]
        print(k, v["source_wording"], "->", e["state"], e.get("rule"), (e.get("span") or "")[:140])
