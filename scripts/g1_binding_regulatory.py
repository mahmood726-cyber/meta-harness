"""OWN-TUPLE EFFECT_CI from an OPEN REGULATORY DOCUMENT (US FDA approved labelling / review; EMA EPAR) for a lane target
whose own report and posted results print no two-sided interval (G1 binding lane, route 5 of the acquisition ladder:
AACT -> PMC/EPMC OA -> Unpaywall -> independent meta -> FDA/EMA). Deterministic; no model.

Held source: cache/regulatory/<application>/<date>_<file>.txt -- the typed text of the section that reports the trial,
cut from the PDF's text layer (k_gap_regulatory_probe.fetch_text), with the PDF's url and sha256 in manifest.json.
US FDA labelling and reviews are works of the US government (redistributable).

Gates (all must hold; the comparator's numbers are never read):
  R1 NAMED     a table caption names the trial (acronym)
  R2 ESTIMAND  the caption states the topic's composite and g1_tracker.own_tuple_establishes_estimand(slug, span) holds
               (3-point MACE: CV death + MI + stroke named, no extra component)
  R3 CI        the table header states the CI level ('(98% CI)') and the row prints the effect with BOTH bounds
               (a one-sided bound alone is refused)
  R4 UNIQUE    exactly one such row follows the caption
The tracker re-checks effect, both bounds and the stated level verbatim in the span, and re-expresses a non-95% two-sided
interval at 95% on the log scale (SE = (ln U - ln L) / (2 z_level)), recording that it did so.

    python scripts/g1_binding_regulatory.py   -> outputs/k_gap/g1_binding/bindings_regulatory.json
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

OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding")
HELD = os.path.join(ROOT, "cache", "regulatory")

# (slug, label, acronym, application, document url, held section: start marker, end marker)
TARGETS = [
    ("dpp4-mace-t2d", "EXAMINE", "EXAMINE", "NDA022271",
     "https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/022271s015lbl.pdf",
     "Cardiovascular Safety Trial A randomized", "16 HOW SUPPLIED"),
]

ROW = re.compile(r"N=(\d+) N=(\d+) (\d+) \(([\d.]+)\) ([\d.]+) (\d+) \(([\d.]+)\) ([\d.]+) (\d+\.\d+) \((\d+\.\d+), (\d+\.\d+)\)")


def norm(t):
    return re.sub(r"\s+", " ", t).strip()


def hold(app, url, start, end):
    """Cut the section from the cached text layer and hold it (idempotent); returns (relative path, text)."""
    import k_gap_regulatory_probe as rp
    txt, rec = rp.fetch_text(url)
    if rec.get("state") != "TEXT":
        raise SystemExit(f"FAIL-CLOSED: {url} not held as text ({rec.get('state')})")
    t = norm(txt)
    i = t.find(start)
    j = t.find(end, i + 1) if i >= 0 else -1
    if i < 0 or j <= i:
        raise SystemExit(f"FAIL-CLOSED: section markers not found in {url}")
    sec = t[i:j]
    d = os.path.join(HELD, app)
    os.makedirs(d, exist_ok=True)
    name = "2026-10-05_" + url.rsplit("/", 1)[1].replace(".pdf", "") + "_section.txt"
    with open(os.path.join(d, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(sec + "\n")
    mp = os.path.join(d, "manifest.json")
    man = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {}
    man[name] = {"url": url, "pdf_sha256": rec.get("sha256"), "pdf_bytes": rec.get("bytes"),
                 "text_sha256": hashlib.sha256((sec + "\n").encode("utf-8")).hexdigest(),
                 "cut": {"from": start, "to_before": end}, "licence": "US government work (FDA labelling)"}
    with open(mp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(man, fh, indent=1, ensure_ascii=False)
    return os.path.relpath(os.path.join(d, name), ROOT).replace("\\", "/"), sec


def candidates(sec, acronym, slug):
    """R1-R4 over one held section. Returns (bindings, refusals)."""
    import g1_tracker as gt
    out, ref = [], []
    for cap in re.finditer(r"Table \d+\.[^.]{0,200}?\b" + re.escape(acronym) + r"\b", sec):
        win = sec[cap.start(): cap.start() + 900]
        lvl = re.search(r"\((\d{2})% CI\)", win)
        rows = list(ROW.finditer(win))
        caption = win[: (lvl.start() if lvl else 300)]
        if not lvl:
            ref.append({"gate": "R3_CI", "why": "no stated two-sided CI level in the table header", "caption": caption[:160]})
            continue
        if len(rows) != 1:
            ref.append({"gate": "R4_UNIQUE", "why": f"{len(rows)} effect rows", "caption": caption[:160]})
            continue
        r = rows[0]
        span = win[: r.end()]
        if not gt.own_tuple_establishes_estimand(slug, span):
            ref.append({"gate": "R2_ESTIMAND", "why": "the caption does not establish the topic composite", "caption": caption[:160]})
            continue
        out.append({"span": span, "ci_level": lvl.group(1), "effect": r.group(9), "lower": r.group(10), "upper": r.group(11),
                    "counts": {"n_t": int(r.group(1)), "n_c": int(r.group(2)), "events_t": int(r.group(3)),
                               "events_c": int(r.group(6))}})
    return out, ref


def main():
    bindings, not_bound = [], []
    for slug, label, acr, app, url, start, end in TARGETS:
        path, sec = hold(app, url, start, end)
        ok, ref = candidates(sec, acr, slug)
        if len(ok) != 1:
            not_bound.append({"slug": slug, "label": label, "why": "R4_AMBIGUOUS" if ok else "NO_ADMISSIBLE_TABLE_ROW",
                              "refused": ref})
            continue
        c = ok[0]
        bindings.append({"slug": slug, "label": label, "own_tuple": True, "tuple_kind": "EFFECT_CI",
                         "source_kind": "REGULATORY", "source": f"{app} {url.rsplit('/', 1)[1]} (held {path})",
                         "source_path": path, "source_sha256": hashlib.sha256(open(os.path.join(ROOT, path), "rb").read()).hexdigest(),
                         "values": {"measure": "HR", "effect": c["effect"], "lower": c["lower"], "upper": c["upper"],
                                    "ci_level": c["ci_level"]},
                         "counts_printed": c["counts"], "span": c["span"], "rules": "R1-R4 scripts/g1_binding_regulatory.py",
                         "refused_alternatives": ref})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "bindings_regulatory.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"bindings": bindings, "not_bound": not_bound}, fh, indent=1, ensure_ascii=False)
    for b in bindings:
        print("BOUND", b["slug"], b["label"], b["values"], "|", b["span"][-160:])
    for r in not_bound:
        print("NOT  ", r)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
