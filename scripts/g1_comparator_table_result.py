"""The comparator's OWN printed pooled result for OUR primary outcome, typed from a results table of its held CC BY / CC0
JATS (gap list 8 Oct, tranexamic: the outcome binding under D10). Deterministic; no model:

  T1 ROW       exactly one table row whose first cell names OUR primary outcome (g1_tracker.binding_verdict on the cell)
  T2 HEADER    the nearest header above it with two 'n/N' arm columns: the FIRST names our intervention, the SECOND our
               comparator / a generic control (g1_outcomes._arm) -- the orientation is read, never assumed
  T3 CELLS     both arm cells 'e/N' (a (thin-)space thousands separator allowed) and one 'est (lo–hi)' cell; the measure
               from the header ('Pooled OR (95% CI)')
Written to registry/comparator_results.json[<slug>] as state RECORDED with the held source's sha256.

    python scripts/g1_comparator_table_result.py SLUG
"""
from __future__ import annotations

import glob
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "registry", "comparator_results.json")
_EN = re.compile(r"^\s*(\d[\d\s  ,]*)\s*/\s*(\d[\d\s  ,]*)\s*$")
_EST = re.compile(r"^\s*(\d+[.·]\d+)\s*\(\s*(\d+[.·]\d+)\s*[–-]\s*(\d+[.·]\d+)\s*\)\s*$")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _n(s):
    return int(re.sub(r"[\s  ,]", "", s))


def _f(s):
    return float(s.replace("·", "."))


def is_result_row(line):
    """A RESULTS row prints two 'e/N' arm cells (a trial-characteristics row naming the outcome -- 'Diagnosis of
    postpartum haemorrhage at baseline | Yes | No' -- is not one)."""
    return sum(1 for c in line.split("|") if _EN.match(c)) >= 2


def table_result(slug):
    import g1_swap as sw
    import g1_tracker as gt
    import g1_outcomes as go
    from reproducible_ai import record_licence as rl
    t = _j(os.path.join(ROOT, "topics", slug + ".json"))
    po = t["primary_outcome"]
    comp = str(t["comparator_pmid"])
    jats = sorted(glob.glob(os.path.join(ROOT, "cache", "comparators", comp, "*_kgap_jats.xml")))
    if not jats or rl.jats_licence(jats[-1]) != "CC":
        return None, "NO_HELD_CC_JATS"
    text = sw.jats_text(open(jats[-1], encoding="utf-8", errors="replace").read())
    lines = text.splitlines()
    rows = [i for i, ln in enumerate(lines) if "|" in ln and is_result_row(ln) and
            gt.binding_verdict(po["name"], po.get("keywords") or [], ln.split("|")[0].strip(), 2)["verdict"] == "BINDABLE"
            and len(ln.split("|")[0].strip()) <= 80]
    if len(rows) != 1:
        return None, f"T1_ROW: {len(rows)} rows name the outcome"
    i = rows[0]
    hdr = next((j for j in range(i - 1, max(i - 40, -1), -1) if len(re.findall(r"\(n/N\)", lines[j])) == 2), None)
    if hdr is None:
        return None, "T2_HEADER: no header with two n/N columns"
    hc = [c.strip() for c in lines[hdr].split("|")]
    arms = [k for k, c in enumerate(hc) if "(n/N)" in c]
    roles = [go._arm(hc[k].replace("(n/N)", ""), t) for k in arms]
    if roles != ["intervention", "control"]:
        return None, f"T2_HEADER: arm columns read {roles}"
    est_col = next((k for k, c in enumerate(hc) if re.search(r"\b(OR|RR|HR)\b.*95", c)), None)
    if est_col is None:
        return None, "T3: no estimate column"
    measure = re.search(r"\b(OR|RR|HR)\b", hc[est_col]).group(1)
    rc = [c.strip() for c in lines[i].split("|")]
    # a header may omit the row-label column ('Contributing trials | Tranexamic acid group (n/N) | ...' over rows that
    # begin with the outcome name): the column offset is the one -- 0 or 1 -- at which BOTH arm cells and the estimate
    # cell parse; zero or two such offsets refuse
    fits = []
    for off in (0, 1):
        if len(rc) > est_col + off:
            a, b, e = _EN.match(rc[arms[0] + off]), _EN.match(rc[arms[1] + off]), _EST.match(rc[est_col + off])
            if a and b and e:
                fits.append((a, b, e))
    if len(fits) != 1:
        return None, f"T3_CELLS: {len(fits)} column alignments parse"
    a, b, e = fits[0]
    sha = hashlib.sha256(open(jats[-1], "rb").read()).hexdigest()
    return {"state": "RECORDED", "comparator_pmid": comp, "outcome": rc[0], "contrast": f"{hc[arms[0]]} vs {hc[arms[1]]}",
            "scale": measure, "estimate": _f(e.group(1)), "ci_low": _f(e.group(2)), "ci_high": _f(e.group(3)),
            "counts": {"events_t": _n(a.group(1)), "n_t": _n(a.group(2)), "events_c": _n(b.group(1)), "n_c": _n(b.group(2))},
            "printed": lines[i].strip(), "location": {"table": "results table", "block": rc[0], "row": rc[0],
                                                      "column": hc[est_col]},
            "orientation": f"arm columns in header order: {hc[arms[0]]} | {hc[arms[1]]}",
            "orientation_check": {"header": lines[hdr].strip()},
            "source": os.path.relpath(jats[-1], ROOT).replace("\\", "/"), "sha256": sha,
            "typed_by": "scripts/g1_comparator_table_result.py (T1-T3)"}, None


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    data = _j(OUT) if os.path.exists(OUT) else {}
    changed = False
    for s in sys.argv[1:]:
        r, why = table_result(s)
        if not r:
            print(s, "NOT_RECORDED", why)
            continue
        data[s], changed = r, True
        print(s, "RECORDED", r["outcome"], r["scale"], r["estimate"], r["ci_low"], r["ci_high"], r["counts"])
    if changed:                                   # nothing recorded -> the registry file is never rewritten
        with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh, indent=1, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
