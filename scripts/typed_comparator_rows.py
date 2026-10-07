"""TYPED COMPARATOR ROWS from a comparator's own held table (deterministic regex reader; no model).

Writes registry/comparator_rows/<slug>.json in the contract scripts/g1_tracker.typed_comparator_rows re-checks: the
held source path + sha256, and per row a span that is verbatim in the tag-stripped held text with every typed number
printed in it. These rows are ONLY ever the comparator side of a comparison (anti-circularity): they never become our
value and never count a trial.

One reader per table shape, declared below (D8: the held text must carry an open licence -- the CC BY JATS of the
comparator selected under rule 6ee4126f).

    python scripts/typed_comparator_rows.py doac-vte-recurrence [--write]
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

READERS = {
    # doac-vte-recurrence -> PMID 29795629 (PLoS One 2018, CC BY), Table 1 'Baseline characteristics and corresponding
    # primary efficacy outcomes of the Phase 3 trials included': the 'VTE Studies' block, columns Study | Publication
    # Year | DOAC and dosing regimen | Primary Events /Total N | Comparator | Primary Events /Total N | Age | Women %
    "doac-vte-recurrence": {
        "comparator_pmid": "29795629",
        "source": "cache/comparators/29795629/2026-10-07_kgap_jats.xml",
        "table_id": "pone.0197583.t001",
        "block": "VTE Studies",
        "header": ["Study", "Publication Year", "DOAC and dosing regimen", "Primary Events /Total N", "Comparator",
                   "Primary Events /Total N", "Age Years", "Women %"],
        "measure": "OR",
        "outcome": ("primary efficacy outcome of each VTE trial (Table 1 'Primary Events /Total N'; the comparator pools "
                    "recurrent VTE and related death as OR)"),
    },
}


def _cells(tr):
    return [" ".join(html.unescape(re.sub(r"<[^>]+>", " ", c)).split())
            for c in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, re.S)]


def held_norm(raw):
    """Tag-stripped, unescaped, whitespace-collapsed (the tracker's _held_norm for markup sources)."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()


def read(slug):
    cfg = READERS[slug]
    path = os.path.join(ROOT, cfg["source"])
    raw = open(path, encoding="utf-8", errors="replace").read()
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    m = re.search(r'<table-wrap\b[^>]*id="' + re.escape(cfg["table_id"]) + r'".*?</table-wrap>', raw, re.S)
    if not m:
        raise SystemExit(f"REFUSED: table {cfg['table_id']} not in {cfg['source']}")
    trs = [_cells(tr) for tr in re.findall(r"<tr\b.*?</tr>", m.group(0), re.S)]
    multi = [c for c in trs if len(c) > 1]
    if not multi or multi[0] != cfg["header"]:
        raise SystemExit(f"REFUSED: header {multi[0] if multi else None} is not the declared {cfg['header']}")
    rows, inside, held = [], False, held_norm(raw)
    for c in trs:
        if len(c) == 1:                                   # a block heading row ('NVAF Studies', 'VTE Studies')
            inside = c[0] == cfg["block"]
            continue
        if c == cfg["header"]:
            continue
        if not inside:
            continue
        if len(c) != len(cfg["header"]):
            raise SystemExit(f"REFUSED: row {c} has {len(c)} cells, header has {len(cfg['header'])}")
        et = re.fullmatch(r"(\d+)\s*/\s*(\d+)", c[3])
        ec = re.fullmatch(r"(\d+)\s*/\s*(\d+)", c[5])
        if not et or not ec:
            raise SystemExit(f"REFUSED: events/N cells not 'e/N' in row {c}")
        span = " ".join(c)
        if span not in held:
            raise SystemExit(f"REFUSED: row span not verbatim in the held text: {span!r}")
        rows.append({"label": c[0], "measure": cfg["measure"], "events_t": int(et.group(1)), "n_t": int(et.group(2)),
                     "events_c": int(ec.group(1)), "n_c": int(ec.group(2)), "intervention": c[2], "comparator": c[4],
                     "span": span})
    if not rows:
        raise SystemExit(f"REFUSED: no rows in block {cfg['block']!r}")
    return {"slug": slug, "comparator_pmid": cfg["comparator_pmid"], "outcome": cfg["outcome"],
            "note": (f"read by scripts/typed_comparator_rows.py (deterministic regex) from table {cfg['table_id']}, "
                     f"block '{cfg['block']}'; events/N per arm as printed"),
            "source": {"path": cfg["source"], "sha256": sha}, "rows": rows}


def main(argv):
    slug = argv[0]
    d = read(slug)
    for r in d["rows"]:
        print(r["label"], f"{r['events_t']}/{r['n_t']} vs {r['events_c']}/{r['n_c']}")
    if "--write" in argv:
        p = os.path.join(ROOT, "registry", "comparator_rows", f"{slug}.json")
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
        print("wrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main(sys.argv[1:])
