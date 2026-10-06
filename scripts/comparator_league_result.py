"""The comparator's OWN result for the topic contrast when it prints it only in a NETWORK LEAGUE TABLE (typed; no model).

dpp4-mace-t2d's replacement comparator (PMID 31462224, a network meta-analysis) states DPP-4 inhibitor vs placebo for
MACE only in Table 2, a league table. A league cell's meaning depends on the table's stated orientation, so:
  1. the table, its outcome block ('MACE') and the diagonal therapy names are read from the JATS structure;
  2. the orientation is taken from the table's own footnote ('... in the column-defining therapy compared with ...
     the row-defining therapy') -- no footnote saying so, no result;
  3. the cell is read for <intervention> vs <control>;
  4. ORIENTATION CHECK: the same reading must reproduce an OR + 95% CI that the comparator's ABSTRACT prints for another
     pair of the same block (GLP-1 RA vs placebo 0.87, 0.82-0.93), else refused.
Writes registry/comparator_results.json[<slug>]; g1_tracker reads it only for THIS comparator.

    python scripts/comparator_league_result.py dpp4-mace-t2d "DPP-4 inhibitor" "Placebo" MACE
"""
from __future__ import annotations

import glob
import hashlib
import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTP = os.path.join(ROOT, "registry", "comparator_results.json")
_CELL = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*\(\s*(\d+(?:\.\d+)?)\s*[–—\-–—]\s*(\d+(?:\.\d+)?)\s*\)\s*$")
_COL_VS_ROW = re.compile(r"in the column-defining (?:therapy|treatment)\s+compared with\s+(?:the\s+[a-z ]{1,40}?\s+in\s+)?"
                         r"the row-defining (?:therapy|treatment)", re.I)

# A measure is NAMED only in words (odds ratio / risk ratio / relative risk / hazard ratio); the abbreviations alone
# are too common in glossary footnotes ("HR: hazard ratio") of tables that print something else. A glossary entry
# 'HR: hazard ratio' does name it -- so a footnote with a glossary of several measures refuses as ambiguous.
_MEASURES = (("OR", re.compile(r"\bodds ratios?\b", re.I)),
             ("RR", re.compile(r"\b(?:risk ratios?|relative risks?)\b", re.I)),
             ("HR", re.compile(r"\bhazard ratios?\b", re.I)))


def _text(x):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))).strip()


def read_league(jats, intervention, control, outcome):
    """Returns (result dict, None) or (None, why). Pure function of the JATS bytes."""
    abstract = _text((re.search(r"<abstract.*?</abstract>", jats, re.S) or re.match("", "")).group(0))
    for tw in re.findall(r"<table-wrap.*?</table-wrap>", jats, re.S):
        foot = _text((re.search(r"<table-wrap-foot>(.*?)</table-wrap-foot>", tw, re.S) or re.match("", "")).group(0))
        if not _COL_VS_ROW.search(foot):
            continue
        # The MEASURE comes from the table's own words, never assumed (codex P0, merge-ede33d9b2:g1#1: a table
        # printing risk ratios was returned as odds ratios). Exactly one measure named, or no result.
        cap = _text((re.search(r"<caption>(.*?)</caption>", tw, re.S) or re.match("", "")).group(0))
        named = {code for code, rx in _MEASURES if rx.search(foot + " " + cap)}
        if len(named) != 1:
            return None, ("MEASURE_NOT_STATED_BY_THE_TABLE" if not named
                          else "MEASURE_AMBIGUOUS_IN_THE_TABLE:" + ",".join(sorted(named)))
        scale = named.pop()
        rows = [[_text(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)] for tr in re.findall(r"<tr.*?</tr>", tw, re.S)]
        # blocks: a single-cell row names the outcome; the following rows form its league square
        blocks, cur = {}, None
        for r in rows:
            if len([c for c in r if c]) == 1 and not _CELL.match(r[0]):
                cur = r[0]
                blocks[cur] = []
            elif cur is not None:
                blocks[cur].append(r)
        sq = blocks.get(outcome)
        if not sq:
            continue
        names = [r[i] if i < len(r) else "" for i, r in enumerate(sq)]       # the diagonal
        if intervention not in names or control not in names:
            return None, f"THERAPY_NOT_ON_DIAGONAL:{names}"
        ri, ci = names.index(control), names.index(intervention)             # column vs row: intervention vs control
        m = _CELL.match(sq[ri][ci] if ci < len(sq[ri]) else "")
        if not m:
            return None, f"CELL_NOT_A_RATIO:{sq[ri][ci] if ci < len(sq[ri]) else None}"
        # orientation check against the abstract: another cell in the control's row, read the same way
        check = None
        for cj, nm in enumerate(names):
            if cj in (ri, ci):
                continue
            mm = _CELL.match(sq[ri][cj] if cj < len(sq[ri]) else "")
            if not mm:
                continue
            e, lo, hi = mm.groups()
            pat = re.compile(re.escape(scale) + r"\s*" + re.escape(e) + r",?\s*95%\s*CI\s*" + re.escape(lo) + r"\s*[–—\-–—]\s*" + re.escape(hi))
            hit = pat.search(abstract)
            if hit:
                check = {"pair": f"{nm} vs {control}", "cell": sq[ri][cj], "abstract_quote": hit.group(0)}
                break
        if not check:
            return None, "ORIENTATION_NOT_CONFIRMED_BY_THE_ABSTRACT"
        e, lo, hi = m.groups()
        return {"outcome": outcome, "contrast": f"{intervention} vs {control}", "scale": scale, "estimate": float(e),
                "ci_low": float(lo), "ci_high": float(hi), "printed": sq[ri][ci],
                "location": {"table": _text((re.search(r"<label>(.*?)</label>", tw, re.S) or re.match("", "")).group(0)),
                             "block": outcome, "row": control, "column": intervention},
                "orientation": _COL_VS_ROW.search(foot).group(0), "orientation_check": check}, None
    return None, "NO_LEAGUE_TABLE_WITH_STATED_ORIENTATION"


def main(argv):
    slug, intervention, control, outcome = argv[:4]
    cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    comp = str(cfg["comparator_pmid"])
    fp = sorted(glob.glob(os.path.join(ROOT, "cache", "comparators", comp, "*jats*.xml")))[0]
    b = open(fp, "rb").read()
    res, why = read_league(b.decode("utf-8", "replace"), intervention, control, outcome)
    cur = json.load(open(OUTP, encoding="utf-8")) if os.path.exists(OUTP) else {}
    cur[slug] = dict(res or {"state": "REFUSED", "why": why}, comparator_pmid=comp,
                     source=os.path.relpath(fp, ROOT).replace(os.sep, "/"), sha256=hashlib.sha256(b).hexdigest(),
                     state="RECORDED" if res else "REFUSED")
    with open(OUTP, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cur, fh, indent=1, ensure_ascii=False, sort_keys=True)
    print(json.dumps(cur[slug], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
