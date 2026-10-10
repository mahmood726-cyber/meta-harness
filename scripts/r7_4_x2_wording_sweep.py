"""R7-4 X2 wording sweep (read-only; any config change alters screening and goes to the captain / V14): every topic's
include.population_none term against its protocol's X2 (wrong population) text. The empagliflozin protocol excludes
'diabetes-only' populations, the config excluded any record mentioning 'diabetes' -- broader than the protocol, so an
HF trial in people with diabetes (SOLOIST-WHF) was excluded on a word.
  CONFIG_BROADER_THAN_PROTOCOL  the protocol qualifies the term ('diabetes-only', 'only diabetes', '... alone') and the
                                config uses it bare
  NOT_IN_PROTOCOL_X2            the config term does not occur in the protocol's X2 text at all
  MATCHES_PROTOCOL              the term occurs in X2 as written

    python scripts/r7_4_x2_wording_sweep.py   -> outputs/k_gap/g1_binding/r7_4_x2_wording_sweep.json
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "r7_4_x2_wording_sweep.json")


def x2_text(md):
    """The protocol's X2 rule text (a line naming X2 and its continuation), or None."""
    # a continuation line ends at any line naming another rule (list item '- X3', table row '| X3 |', '**X3**')
    # the rule's DEFINITION line ('- X2:', '| X2 |', '**X2** -') before any cross-reference ('See X2 for ...')
    # (continuation runs to the next rule or a blank line -- no line cap; numbered items '2. **X2**:' are definitions)
    cont = r"(?:\n(?![^\n]*\bX(?:[013-9]|\d\d)\b)[^\n]*\S[^\n]*)*"
    # only a DEFINITION counts: a bare cross-reference ('See X2 for ...') is not the rule (-> NO_PROTOCOL_X2)
    m = re.search(r"(?m)^[ \t>*|#-]*(?:\d+[.)]\s*)?\**X2\b\**\s*[:|*‐-—-][^\n]*" + cont, md)
    if not m:
        # an INLINE bold definition ('- Exclude: **X1** not RCT; **X2** wrong population (...); **X3** ...') runs to
        # the next bold rule or a blank line; a bold cross-reference ('See **X2** for ...') is not one
        m = next((mm for mm in re.finditer(r"\*\*X2\*\*(?:(?!\*\*X\d)(?!\n\s*\n)[\s\S])*", md)
                  if not re.search(r"\b(?:see|per|under|in|as\s+in|cf\.?)\s*$", md[:mm.start()], re.I)), None)
    if not m:
        return None
    # either way the rule ends where the next rule's bold label starts on the same line ('**X2**: ...; **X3**: ...')
    return re.sub(r"\s+", " ", re.split(r"\*\*X(?:[013-9]|\d\d)\b", m.group(0))[0])


def _dash(s):
    """Unicode hyphens/dashes (U+2010..U+2015, U+2212) read as an ASCII hyphen, NBSP as a space."""
    return re.sub(r"[‐-―−]", "-", s).replace(" ", " ")


def classify(term, x2):
    t = _dash(term.lower().strip())
    x = _dash((x2 or "").lower())
    if not x2:
        return "NO_PROTOCOL_X2"
    # a sentence that declares a population ELIGIBLE ('trials with HF and diabetes are eligible') is not exclusion
    # wording: its mentions neither match nor clear the config term
    sents = [s for s in re.split(r"(?<=[.;,])\s+", x)
             if not (re.search(r"\b(?:are|is|remain|be)\s+(?:eligible|included|allowed|permitted)\b", s)
                     and not re.search(r"\b(?:not|never)\s+eligible\b|\bineligible\b|\bexclud", s))
             and not re.search(r"\b(?:do|does|should|must)\s+not\s+exclude\b|\bnot\s+(?:be\s+)?excluded\b", s)]
    x = " ".join(sents)
    hits = list(re.finditer(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", x))
    if not hits:
        return "NOT_IN_PROTOCOL_X2"
    # BROADER only when EVERY occurrence of the term is qualified ('diabetes-only', 'only diabetes', 'diabetes alone')
    if all(re.match(r"[- ]only\b|\s+alone\b", x[h.end():]) or re.search(r"\bonly\s+$", x[:h.start()]) for h in hits):
        return "CONFIG_BROADER_THAN_PROTOCOL"
    return "MATCHES_PROTOCOL"


def main():
    res, tot = {}, {}
    for f in sorted(os.listdir(os.path.join(ROOT, "topics"))):
        if not f.endswith(".json"):
            continue
        slug = f[:-5]
        cfg = json.load(open(os.path.join(ROOT, "topics", f), encoding="utf-8"))
        terms = list((cfg.get("include") or {}).get("population_none") or [])
        if not terms:
            continue
        pp = os.path.join(ROOT, "protocols", f"{slug}.md")
        x2 = x2_text(open(pp, encoding="utf-8").read()) if os.path.exists(pp) else None
        rows = [{"term": t, "kind": classify(t, x2)} for t in terms]
        for r in rows:
            tot[r["kind"]] = tot.get(r["kind"], 0) + 1
        res[slug] = {"protocol_x2": x2, "terms": rows,
                     "broader": [r["term"] for r in rows if r["kind"] == "CONFIG_BROADER_THAN_PROTOCOL"],
                     "not_in_protocol": [r["term"] for r in rows if r["kind"] == "NOT_IN_PROTOCOL_X2"]}
    out = {"totals": tot, "topics": res}
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps(tot, indent=1))
    for s, t in res.items():
        if t["broader"] or t["not_in_protocol"]:
            print(s, "BROADER", t["broader"], "| NOT_IN_PROTOCOL", t["not_in_protocol"][:6])
    return out


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
