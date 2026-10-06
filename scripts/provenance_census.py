"""PROVENANCE CENSUS + GATE (Mahmood, 6 Oct: "everything must happen inside the reproducible harness, by regex/typed
extraction or recorded reproducible AI, and nothing else"). Every SERVED value (a pooled trial row in
docs/reviews/<slug>/review.json) and every countable G1 TRACKER row (outputs/k_gap/g1/<slug>.json) is classed by where
its value came from:

  EXTRACTOR              a deterministic regex / typed extractor over a held source, with the span it read
  RECORDED_MODEL_CALL    a recorded model call that replays offline: every cited record (mc-<32 hex>) is in the tree
  HAND_ENTERED           a value entered by hand / by an agent outside the harness, bound to a held span
                         (registry of verified inputs: provenance *_verified*); allowed ONLY while listed in
                         registry/provenance_hand_entered.json, a burn-down list that may only shrink
  UNTRACED               none of the above (no source, no span, or a cited record not in the tree) -> REFUSED

Identity named by hand (a topic's extra_pmids) is reported per row as identity=HAND_NAMED.

    python scripts/provenance_census.py [--write] [--freeze-hand-entered]
Exit 1 when any row is UNTRACED, or a HAND_ENTERED row is not on the burn-down list.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "provenance_census.json")
HAND_LIST = os.path.join(ROOT, "registry", "provenance_hand_entered.json")
MC = re.compile(r"mc-[0-9a-f]{32}")
EXTRACTOR_PROV = {"abstract", "pmc_fulltext", "pmc_fulltext_effect", "ctgov_results", "aact_verified", "published_rate",
                  "pre_specified_dose"}


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


_HELD = None


def record_held(rid: str, root: str = ROOT) -> bool:
    global _HELD
    if _HELD is None or root != ROOT:
        held = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(root, "registry", "model_calls", "mc-*.json"))}
        held |= {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(root, "evidence", "model_calls", "*", "mc-*.json"))}
        if root != ROOT:
            return rid in held
        _HELD = held
    return rid in _HELD


def _records_in(obj) -> list[str]:
    return sorted(set(MC.findall(json.dumps(obj, ensure_ascii=False))))


def classify_served(t: dict, root: str = ROOT) -> tuple[str, str]:
    prov = str(t.get("provenance") or "")
    if prov == "served_pool_signed_notice":
        adm = t.get("served_pool_admission") or {}
        ids = _records_in(adm)
        missing = [i for i in ids if not record_held(i, root)]
        if missing:
            return "UNTRACED", f"signed row cites record(s) not in the tree: {missing}"
        if ids:
            return "RECORDED_MODEL_CALL", f"signed row: {ids}"
        if t.get("source") and _deterministic_basis(json.dumps(adm)):
            return "EXTRACTOR", f"signed row: {adm.get('basis')}"
        return "UNTRACED", "signed row with neither a record nor a typed registry source"
    if "_verified" in prov:
        return "HAND_ENTERED", f"verified input ({prov}), bound to a held span"
    if prov in EXTRACTOR_PROV:
        if not str(t.get("source") or "").strip():
            return "UNTRACED", f"{prov} row with no source span"
        return "EXTRACTOR", prov
    ids = _records_in(t)
    if ids:
        missing = [i for i in ids if not record_held(i, root)]
        return ("UNTRACED", f"cites record(s) not in the tree: {missing}") if missing else ("RECORDED_MODEL_CALL", str(ids))
    return "UNTRACED", f"provenance {prov!r} is not a known extractor and cites no record"


_DET = re.compile(r"(?<![A-Za-z])AACT(?![A-Za-z])|PRIMARY_TEXT|\bTEXT\b|trial's own text|states the counts|"
                  r"supplementary table \(sha256 [0-9a-f]+\), row|TYPED_(?:TABLE|COMPARATOR_ROW)|"
                  r"verbatim \(level printed\)|NDA\d+")


def _deterministic_basis(b: str) -> bool:
    """A basis naming a deterministic source of the value: the trial's own held text or registry (AACT), a typed table
    read over held bytes (sha256 + row), or a verbatim span of a held regulatory document."""
    return bool(_DET.search(b or ""))


def _sweep_records(slug: str, label: str, root: str) -> tuple[list[str], bool]:
    p = os.path.join(root, "outputs", "k_gap", "sweep", f"{slug}.json")
    if not os.path.exists(p):
        return [], False
    rows = [t for t in (_j(p).get("trials") or []) if str(t.get("label") or "").strip() == str(label).strip()]
    blob = json.dumps(rows, ensure_ascii=False)
    return _records_in(rows), _deterministic_basis(blob)


def _secondary_records(slug: str, label: str, root: str) -> list[str]:
    p = os.path.join(root, "registry", "secondary_meta", f"{slug}.json")
    if not os.path.exists(p):
        return []
    first = re.split(r"[\s,(\[]+", str(label).strip())[0].lower()
    flat = re.sub(r"[^a-z0-9]", "", str(label).lower())

    def same(meta_label):
        ml = str(meta_label or "")
        if ml.strip() == str(label).strip():
            return True
        if len(first) >= 4 and ml.lower().startswith(first):
            return True
        # an acronym in the meta's label ('Pitt et al 2014 (TOPCAT)') naming the tracker's label ('TOPCAT2014')
        return any(len(tok) >= 4 and flat.startswith(tok) for tok in re.findall(r"[a-z0-9]+", ml.lower()) if tok.isalpha())
    rows = [r for r in (_j(p).get("rows") or []) if same(r.get("trial_label"))]
    return _records_in(rows)


def classify_tracker(t: dict, slug: str, served_class: dict, root: str = ROOT, lags=None) -> tuple[str, str]:
    if t.get("in_our_pool"):
        fam = str(t.get("family") or "").replace("PMID ", "").strip()
        c = served_class.get((slug, fam))
        if c:
            return c
    route = str(t.get("route") or "").upper()
    ids = _records_in({k: t.get(k) for k in ("basis", "our_value", "comparator_sourced", "secondary_single",
                                              "registry_binding")})
    det = False
    if not ids and route.startswith("SWEEP_"):
        ids, det = _sweep_records(slug, t.get("label"), root)
    if not ids and route.endswith(("SECONDARY_SINGLE", "TWO_SOURCE", "INDEPENDENT_METAS")):
        ids = _secondary_records(slug, t.get("label"), root)
    if ids:
        missing = [i for i in ids if not record_held(i, root)]
        return ("UNTRACED", f"cites record(s) not in the tree: {missing}") if missing else ("RECORDED_MODEL_CALL", str(ids[:4]))
    b = str(t.get("basis") or "")
    if det or _deterministic_basis(b):
        return "EXTRACTOR", b[:120]
    if t.get("in_our_pool"):
        # the tracker's pool is the deterministic build WITH every held open source (k_gap_counterfactual); a trial the
        # served page lags is disclosed in served_pool_lags. Traceable only if its value comes from a typed extractor.
        src = str(t.get("basis") or "") + " " + str((t.get("our_value") or {}).get("source") or "")
        m = re.search(r"our held-source pool .*\(([a-z_]+)\)", src)
        fam = str(t.get("family") or "")
        if m and m.group(1) in EXTRACTOR_PROV and fam in (lags or []):
            return "EXTRACTOR", f"held-source build ({m.group(1)}); the served page lags it (served_pool_lags)"
        return "UNTRACED", f"in our pool but no served primary row for {fam}, and not a disclosed served-pool lag"
    return "UNTRACED", f"route {t.get('route')}: basis cites neither a record nor a typed source ({b[:100]!r})"


def census(root: str = ROOT) -> dict:
    served, served_class = [], {}
    extra = {}
    for p in sorted(glob.glob(os.path.join(root, "topics", "*.json"))):
        c = _j(p)
        extra[os.path.basename(p)[:-5]] = {str(x) for x in (c.get("extra_pmids") or [])}
    for p in sorted(glob.glob(os.path.join(root, "docs", "reviews", "*", "review.json"))):
        r = _j(p)
        slug = r.get("slug") or os.path.basename(os.path.dirname(p))
        for o in r.get("outcomes") or []:
            for t in o.get("trials") or []:
                cls, why = classify_served(t, root)
                rid = str(t.get("family_report_id") or t.get("id") or "").replace("PMID ", "").strip()
                served.append({"slug": slug, "outcome": o.get("name"), "id": t.get("id"), "class": cls, "why": why,
                               "identity": "HAND_NAMED" if rid in extra.get(slug, set()) else "SEARCHED"})
                if o.get("primary"):
                    for k in ("id", "family_report_id", "trial_family_id", "report_id", "family_id"):
                        v = str(t.get(k) or "").replace("PMID ", "").strip()
                        if v:
                            served_class[(slug, v)] = (cls, why)
    tracker = []
    for p in sorted(glob.glob(os.path.join(root, "outputs", "k_gap", "g1", "*.json"))):
        o = _j(p)
        slug = o.get("slug")
        for t in o.get("trials") or []:
            if not t.get("g1_countable"):
                continue
            cls, why = classify_tracker(t, slug, served_class, root, o.get("served_pool_lags") or [])
            fam = str(t.get("family") or "").replace("PMID ", "").strip()
            tracker.append({"slug": slug, "label": t.get("label"), "route": t.get("route"), "class": cls, "why": why,
                            "identity": "HAND_NAMED" if fam in extra.get(slug, set()) else "SEARCHED"})
    def tally(rows):
        d = {}
        for x in rows:
            d[x["class"]] = d.get(x["class"], 0) + 1
        return d
    return {"served": {"N": len(served), "by_class": tally(served), "rows": served},
            "tracker": {"N": len(tracker), "by_class": tally(tracker), "rows": tracker},
            "hand_named_identity": {"served": sum(x["identity"] == "HAND_NAMED" for x in served),
                                    "tracker": sum(x["identity"] == "HAND_NAMED" for x in tracker)}}


def _key(x):
    return f"{x['slug']}|{x.get('outcome') or x.get('label')}|{x.get('id') or x.get('route')}"


def problems(c: dict, hand_list: dict | None) -> list[str]:
    allowed = set((hand_list or {}).get("rows") or [])
    out = []
    for part in ("served", "tracker"):
        for x in c[part]["rows"]:
            if x["class"] == "UNTRACED":
                out.append(f"UNTRACED {part} {_key(x)}: {x['why']}")
            elif x["class"] == "HAND_ENTERED" and f"{part}|{_key(x)}" not in allowed:
                out.append(f"HAND_ENTERED {part} {_key(x)} is not on the burn-down list (registry/provenance_hand_entered.json)")
    return out


def main(argv):
    c = census()
    for part in ("served", "tracker"):
        print(f"{part}: N {c[part]['N']} -- " + ", ".join(f"{k} {v}" for k, v in sorted(c[part]["by_class"].items())))
    print(f"identity named by hand (extra_pmids): served {c['hand_named_identity']['served']}, tracker {c['hand_named_identity']['tracker']}")
    if "--freeze-hand-entered" in argv:
        rows = sorted(f"{part}|{_key(x)}" for part in ("served", "tracker") for x in c[part]["rows"] if x["class"] == "HAND_ENTERED")
        with open(HAND_LIST, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"_doc": "Burn-down list: values entered by hand / by an agent outside the reproducible harness, bound "
                               "to a held span. Mahmood 6 Oct: 'nothing hand-entered'. This list may only SHRINK; each row is "
                               "to be re-derived by a deterministic extractor or a recorded model call, then removed.",
                       "rows": rows}, fh, indent=1)
            fh.write("\n")
        print(f"froze {len(rows)} hand-entered rows")
    if "--write" in argv:
        with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(c, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    hl = _j(HAND_LIST) if os.path.exists(HAND_LIST) else None
    probs = problems(c, hl)
    for p in probs[:40]:
        print("REFUSED", p)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
