"""OWN-TUPLE TABLE BINDER for UNMATCHED comparator trials (G1 binding lane, Mahmood 4 Oct). Deterministic: no model.

Mahmood 3 Oct: a comparator trial is matched by ANY verified typed tuple for it. When the trial's own held open text
prints the topic outcome in a results table, the per-arm counts are read by regex and admitted only when the table
itself proves them:
  T1  the table is not a baseline / characteristics / subgroup table
  T2  the row label names a NON-GENERIC topic outcome term (harness.extract.GENERIC_ANCHORS excluded; the shared
      table-location gate's rule)
  T3  exactly one column whose header names an intervention term and one whose header names a comparator term each hold
      an 'e (p%)' cell; each header states its N ('(n=206)')
  T4  each p equals e/N at its printed precision (the percentage proves the pairing of e with N)
  T5  the candidate is unique across the trial's held texts (the same tuple printed twice counts once)
The binding carries the verbatim table title, header and row as its span (single_primary_source then checks every count
is in the span). The comparator's numbers are never used: agreement with the comparator is COMPUTED by the tracker.

    python scripts/g1_binding_bind.py   -> outputs/k_gap/g1_binding/bindings.json
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import extract  # noqa: E402
import g1_confirm_bind as cb  # noqa: E402
import secondary_meta_build as smb  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding")
_TABLE = re.compile(r"^TABLE (?P<title>[^\n]*)\n(?P<body>.*?)(?=^TABLE |\Z)", re.M | re.S)
_N = re.compile(r"\(\s*[Nn]\s*=\s*([\d,]+)\s*\)|\b[Nn]\s*=\s*([\d,]+)\b")
_CELL = re.compile(r"^\s*([\d,]+)\s*[(\[]\s*(\d{1,3}(?:\.\d+)?)\s*%?\s*[)\]]\s*$")


def _pct_ok(e, n, printed):
    d = len(printed.split(".")[1]) if "." in printed else 0
    return n > 0 and abs(100.0 * e / n - float(printed)) <= 0.5 * 10 ** -d + 1e-9


def table_own_tuples(text, terms, interv, comp):
    """Every candidate (title, header, row, (e_t, n_t, e_c, n_c), term) in one held text."""
    named = [t.lower() for t in terms if t and len(t) > 3 and t.lower() not in extract.GENERIC_ANCHORS]
    iv = [w.lower() for w in list(interv or []) + cb.GENERIC_INTERV if w]
    cp = [w.lower() for w in list(comp or []) + cb.GENERIC_COMP if w]
    out = []
    # T3b: an arm column whose header states no N takes it from ANOTHER table of the same report whose header carries the
    # IDENTICAL arm label with an N ('Colchicine (n = 120)' in Table 1 for 'Colchicine' in Table 2); that header line joins
    # the span, and T4's percentage check must still hold (it is what proves the pairing)
    label_n = {}
    for tm in _TABLE.finditer(text or ""):
        hl = [ln for ln in tm.group("body").split("\n") if ln.strip()][:1]
        for c in (hl[0].split(" | ") if hl else []):
            m = _N.search(c)
            lab = _N.sub("", c).strip().lower()
            if m and lab:
                label_n.setdefault(lab, set()).add((int((m.group(1) or m.group(2)).replace(",", "")), hl[0]))
    for tm in _TABLE.finditer(text or ""):
        title = tm.group("title")
        if re.search(r"baseline|characteristic|demograph|subgroup", title, re.I) and \
                not re.search(r"outcome|event|end ?point|result", title, re.I):
            continue
        lines = [ln for ln in tm.group("body").split("\n") if ln.strip()]
        if not lines:
            continue
        head = [c.strip() for c in lines[0].split(" | ")]
        ns, borrowed = [], []
        for c in head:
            m = _N.search(c)
            if m:
                ns.append(int((m.group(1) or m.group(2)).replace(",", "")))
                continue
            got = label_n.get(c.strip().lower()) or set()
            if len(got) == 1:                         # one N for this exact arm label in the report: borrowed, cited
                n, hline = next(iter(got))
                ns.append(n)
                borrowed.append(hline)
            else:
                ns.append(None)
        ti = [i for i, c in enumerate(head) if ns[i] and any(w in c.lower() for w in iv) and not any(w in c.lower() for w in cp)]
        ci = [i for i, c in enumerate(head) if ns[i] and any(w in c.lower() for w in cp) and not any(w in c.lower() for w in iv)]
        if len(ti) != 1 or len(ci) != 1:
            continue
        ti, ci = ti[0], ci[0]
        for ln in lines[1:]:
            cells = [c.strip() for c in ln.split(" | ")]
            lab = cells[0].lower()
            term = next((t for t in named if t in lab), None)
            if not term or max(ti, ci) >= len(cells):
                continue
            if extract._is_subgroup_sentence(title + " " + cells[0]) or cb.SUBGROUP_EXTRA.search(title + " " + cells[0]):
                continue
            mt, mc = _CELL.match(cells[ti]), _CELL.match(cells[ci])
            if not (mt and mc):
                continue
            et, ec = int(mt.group(1).replace(",", "")), int(mc.group(1).replace(",", ""))
            if not (_pct_ok(et, ns[ti], mt.group(2)) and _pct_ok(ec, ns[ci], mc.group(2))):
                continue
            out.append({"title": f"TABLE {title}", "header": lines[0], "row": ln, "n_from": sorted(set(borrowed)),
                        "tuple": (et, ns[ti], ec, ns[ci]), "term": term})
    return out


def bind(t):
    spec = smb.spec_of(t["slug"])
    terms = [k for k in (spec.get("keywords") or []) if k] + list(spec.get("core") or [])
    iv, cp = cb.arm_terms(t["slug"])
    cands, srcs = {}, {}
    for p in t["pmids"][:3]:
        for kind, ref, pl in smb.primary_sources(t["slug"], p):
            if kind != "text" or not isinstance(pl, str):
                continue
            for c in table_own_tuples(pl, terms, iv, cp):
                cands.setdefault(c["tuple"], c)
                srcs.setdefault(c["tuple"], (p, ref, hashlib.sha256(pl.encode("utf-8")).hexdigest()))
    if not cands:
        return None, "NO_OUTCOME_TABLE_ROW"
    if len(cands) > 1:
        return None, "AMBIGUOUS:" + ";".join(f"{k}" for k in list(cands)[:4])
    (tup, c), = cands.items()
    p, ref, sha = srcs[tup]
    parts = [c["title"], c["header"], c["row"]] + list(c.get("n_from") or [])
    return {"slug": t["slug"], "label": t["label"], "pmid": p, "ncts": t.get("ncts"), "source_kind": "TEXT",
            "source": ref, "source_sha256": sha, "route": "PRIMARY_TEXT_TABLE_OWN_TUPLE",
            "span": " … ".join(parts), "span_parts": parts, "tuple_kind": "COUNTS", "own_tuple": True,
            "values": dict(zip(("events_t", "n_t", "events_c", "n_c"), tup)), "named_by": c["term"],
            "arm_check": "TABLE_HEADERS_INTERVENTION_AND_COMPARATOR", "search_key": "TOPIC_OUTCOME_TABLE_ROW (regex)"}, "BOUND"


def main():
    targets = json.load(open(os.path.join(OUT, "targets.json"), encoding="utf-8"))
    res, nb = [], []
    for t in targets:
        b, why = bind(t)
        (res if b else nb).append(b or {"slug": t["slug"], "label": t["label"], "why": why})
        print(t["slug"][:14], "|", t["label"][:34], "|", (b or {}).get("values") or why, flush=True)
    out = {"bindings": res, "not_bound": nb}
    p = os.path.join(OUT, "bindings.json")
    with open(p + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    os.replace(p + ".tmp", p)
    print(len(res), "bound of", len(targets))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
