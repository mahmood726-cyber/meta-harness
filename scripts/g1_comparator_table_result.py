"""The comparator's OWN printed pooled result for OUR primary outcome, typed from a results table of its held CC BY / CC0
JATS (gap list 8 Oct, tranexamic: the outcome binding under D10). Deterministic; no model:

  T1 ROW       exactly one table row whose first cell names OUR primary outcome (g1_tracker.binding_verdict on the cell)
  T2 HEADER    the nearest header above it with two 'n/N' arm columns: the FIRST names our intervention, the SECOND our
               comparator / a generic control (_arm below) -- the orientation is read, never assumed
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


_CAPTION = re.compile(r"^\s*(?:Table|Figure|Fig\.?)\s*\d", re.I)


def header_above(lines, i):
    """The nearest header above row i with two 'n/N' arm columns, never across a table / figure caption: a row of the
    NEXT table must not take the previous table's header (codex review 8 Oct counts#6 -- its arm order could be the
    reverse)."""
    for j in range(i - 1, max(i - 40, -1), -1):
        if _CAPTION.search(lines[j]):
            return None
        if len(re.findall(r"\(n/N\)", lines[j])) == 2:
            return j
    return None


def aligned(rc, arms, est_col):
    """[(arm_t, arm_c, estimate) matches] for each column offset (0 or 1) at which every index exists in the row AND all
    three cells parse (codex review 8 Oct counts#7: offset 1 indexed past a four-cell row)."""
    fits = []
    for off in (0, 1):
        idx = (arms[0] + off, arms[1] + off, est_col + off)
        if max(idx) < len(rc):
            a, b, e = _EN.match(rc[idx[0]]), _EN.match(rc[idx[1]]), _EST.match(rc[idx[2]])
            if a and b and e:
                fits.append((a, b, e))
    return fits


def is_result_row(line):
    """A RESULTS row prints two 'e/N' arm cells (a trial-characteristics row naming the outcome -- 'Diagnosis of
    postpartum haemorrhage at baseline | Yes | No' -- is not one)."""
    return sum(1 for c in line.split("|") if _EN.match(c)) >= 2


# --- arm roles (ported verbatim from g1/binding-on-d0848a72 scripts/g1_outcomes.py: _arm and its helpers, so this
# reader carries no D10 module; the D10 topic/protocol amendments stay held out) ---
GENERIC_CONTROL = ["placebo", "control", "usual care", "standard care", "standard of care", "no treatment"]


def _flat(v):
    if isinstance(v, str):
        return [v]
    if isinstance(v, dict):
        return [x for k, w in v.items() for x in [k] + _flat(w)]
    if isinstance(v, (list, tuple)):
        return [x for w in v for x in _flat(w)]
    return []


def _intervention_terms(t):
    """Our intervention's names: terms, agents (a list or a {agent: aliases} map) and class terms."""
    return [x for x in _flat(t.get("intervention_terms")) + _flat(t.get("intervention_agents")) +
            _flat(t.get("intervention_class_terms")) if len(x) >= 3]


def _term_re(terms):
    terms = [x for x in terms if x]
    if not terms:
        return re.compile(r"(?!x)x")              # matches nothing ('' would match every boundary)
    return re.compile(r"\b(" + "|".join(re.escape(x) for x in sorted(set(terms), key=len, reverse=True)) + r")", re.I)


def _arm(title, t):
    """'intervention' / 'control' / None for an arm column title, by OUR terms: the intervention names one of our
    agents / terms (a 'placebo for <drug>' clause is not the drug); the control names our comparator or a generic
    control and no intervention term."""
    import g1_binding_aact as ba
    rest = ba.PLACEBO_FOR.sub(" ", title or "")
    iv = bool(_term_re(_intervention_terms(t)).search(rest))
    ct = bool(_term_re([x for x in (t.get("comparator_terms") or []) if len(x) >= 3] + GENERIC_CONTROL).search(rest))
    return "intervention" if iv and not ct else "control" if ct and not iv else None   # both / neither: unmapped


def table_result(slug):
    import g1_swap as sw
    import g1_tracker as gt
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
    hdr = header_above(lines, i)
    if hdr is None:
        return None, "T2_HEADER: no header with two n/N columns"
    hc = [c.strip() for c in lines[hdr].split("|")]
    arms = [k for k, c in enumerate(hc) if "(n/N)" in c]
    roles = [_arm(hc[k].replace("(n/N)", ""), t) for k in arms]
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
    fits = aligned(rc, arms, est_col)
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
