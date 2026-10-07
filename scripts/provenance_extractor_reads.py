"""Retire HAND_ENTERED served values by the DETERMINISTIC extractor (harness.extract.extract_trial), no model.

For every row on the burn-down list (registry/provenance_hand_entered.json; served rows and countable tracker rows),
the extractor is run over each HELD document that can carry the value:
  * the document the served row itself cites (its 'source' names a held path: cache/<slug>/records.json <section> PMID n
    abstract, or cache/<slug>/pmc_<n>_fulltext.txt / ft_<n>.txt),
  * the trial's own record abstract, and its held full text in the PRODUCER's representation (the JATS cache converted
    by harness.fulltext.combined_text(parse_pmc_xml(...)), or the harness's own outputs/k_gap/_ft/<pmid>.txt).
A row is RETIRABLE only when the extractor's output on one document EQUALS the served value (counts exactly; an effect
and both CI bounds at the served precision). Then registry/provenance_extractor_reads.json records {document, its
sha256, span, numbers, extractor sha256}; scripts/provenance_census.py may class the row EXTRACTOR from it. Anything
else is listed with what the extractor gave on each document -- never accepted, never auto-replaced.

    python scripts/provenance_extractor_reads.py [--served-root <git ref of the served pages>]
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
from harness import extract  # noqa: E402

HAND = os.path.join(ROOT, "registry", "provenance_hand_entered.json")
OUT = os.path.join(ROOT, "registry", "provenance_extractor_reads.json")
REPORT = os.path.join(ROOT, "outputs", "provenance_extractor_reads.json")
NUM = ("ai", "n1i", "ci", "n2i", "effect", "ci_low", "ci_high")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _git(ref, path):
    p = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL)
    return p.stdout.decode("utf-8") if p.returncode == 0 else None


def served_page(slug, ref):
    s = _git(ref, f"docs/reviews/{slug}/review.json") if ref else None
    if s is None:
        p = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
        s = open(p, encoding="utf-8").read() if os.path.exists(p) else None
    return json.loads(s) if s else None


def served_row(page, outcome, pid):
    for o in (page or {}).get("outcomes") or []:
        if o.get("name") == outcome:
            for t in o.get("trials") or []:
                if str(t.get("id")).replace("PMID ", "") == str(pid).replace("PMID ", ""):
                    return o, t
    return None, None


def _records(slug):
    p = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(p):
        return {}
    d = _j(p)
    out = {}
    for key, v in (d.items() if isinstance(d, dict) else [("records", d)]):
        for r in v if isinstance(v, list) else []:
            if isinstance(r, dict) and r.get("id"):
                out.setdefault(str(r["id"]), r)
    return out


def _producer_text(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    if t.lstrip().startswith("<?xml") or "<article" in t[:3000]:
        from harness import fulltext as F
        t = F.combined_text(F.parse_pmc_xml(t))
    return t


_CITED = re.compile(r"(cache/[\w-]+/[\w.-]+)(?:\s+(?:\w+\s+)?PMID\s+(\d+))?")


def documents(slug, pid, cited_source):
    """[(label, text, sha256)] of every held document that may carry the row's value."""
    recs = _records(slug)
    docs = []
    for m in _CITED.finditer(cited_source or ""):
        path, rpid = m.group(1), m.group(2)
        fp = os.path.join(ROOT, path)
        if path.endswith("records.json") and rpid and rpid in recs:
            ab = recs[rpid].get("abstract") or ""
            docs.append((f"{path} PMID {rpid} abstract (cited)", ab))
        elif os.path.exists(fp) and path.endswith(".txt"):
            docs.append((f"{path} (cited)", _producer_text(fp)))
    own = recs.get(str(pid))
    if own and own.get("abstract"):
        docs.append((f"cache/{slug}/records.json PMID {pid} abstract", own["abstract"]))
    for fp in (os.path.join(ROOT, "cache", slug, f"ft_{pid}.txt"), os.path.join(ROOT, "outputs", "k_gap", "_ft", f"{pid}.txt")):
        if os.path.exists(fp) and os.path.getsize(fp):
            docs.append((os.path.relpath(fp, ROOT).replace(os.sep, "/") + " (producer representation)", _producer_text(fp)))
    seen, out = set(), []
    for label, text in docs:
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if text and h not in seen:
            seen.add(h)
            out.append((label, text, h))
    return out


def _eq(a, b):
    if a is None or b is None:
        return a is b
    try:
        fa, fb = float(a), float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)
    # equal at the SERVED value's printed precision
    dec = len(str(b).split(".")[1]) if "." in str(b) else 0
    return round(fa, dec) == round(fb, dec)


def agrees(ex, t):
    if ex.get("absent"):
        return False
    if t.get("ai") is not None:
        return all(ex.get(k) is not None and int(ex[k]) == int(t[k]) for k in ("ai", "n1i", "ci", "n2i"))
    if t.get("effect") is not None:
        return all(_eq(ex.get(k), t.get(k)) for k in ("effect", "ci_low", "ci_high"))
    return False


def outcome_spec(slug, name):
    cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
    for key in ("primary_outcome", "secondary_outcomes", "harm_outcomes"):
        v = cfg.get(key)
        for o in (v if isinstance(v, list) else [v] if v else []):
            if isinstance(o, dict) and o.get("name") == name:
                return cfg, o
    return cfg, None


def main(argv):
    ref = next((a.split("=", 1)[1] for a in argv if a.startswith("--served-root=")), "")
    hand = _j(HAND)
    xsha = hashlib.sha256(open(os.path.join(ROOT, "harness", "extract.py"), "rb").read()).hexdigest()
    reads, report, tracker_rows = {}, [], []
    for key in hand.get("rows") or []:
        kind, slug, outcome, pid = key.split("|", 3)
        row = {"key": key}
        if kind != "served":
            tracker_rows.append((key, slug, outcome, row))
            continue
        page = served_page(slug, ref)
        o, t = served_row(page, outcome, pid)
        cfg, spec = outcome_spec(slug, outcome)
        if not t or not spec:
            row["state"] = "SERVED_ROW_OR_OUTCOME_NOT_FOUND"
            report.append(row)
            continue
        row["served"] = {k: t.get(k) for k in NUM + ("scale", "provenance") if t.get(k) is not None}
        interv, comp = cfg.get("intervention_terms") or [], cfg.get("comparator_terms") or []
        dc = extract.declared_is_composite(outcome)
        tried = []
        for label, text, h in documents(slug, pid.replace("PMID ", ""), t.get("source") or ""):
            ex = extract.extract_trial(text, spec["keywords"], interv, comp, declared_composite=dc,
                                       estimand=spec.get("estimand"), outcome_name=outcome)
            got = {k: ex.get(k) for k in NUM + ("scale",) if ex.get(k) is not None} or {"absent": ex.get("reason", "")[:160]}
            tried.append({"document": label, "sha256": h, "extractor": got})
            if agrees(ex, t):
                reads[key] = {"document": label, "document_sha256": h, "span": (ex.get("source") or "")[:600],
                              "numbers": {k: ex.get(k) for k in NUM if ex.get(k) is not None},
                              "extractor": "harness/extract.py", "extractor_sha256": xsha}
                break
        row["state"] = "RETIRABLE_BY_EXTRACTOR" if key in reads else "EXTRACTOR_DOES_NOT_REPRODUCE"
        row["tried"] = tried
        report.append(row)
    # a TRACKER row (outputs/k_gap/g1/<slug>.json, our held-source pool row) is retired only when ITS OWN value equals a
    # retired served row's extractor read for the same trial -- the same number from the same held span
    for key, slug, label, row in tracker_rows:
        trk = os.path.join(ROOT, "outputs", "k_gap", "g1", f"{slug}.json")
        x = next((t for t in (_j(trk).get("trials") if os.path.exists(trk) else []) if t.get("label") == label), None)
        fam = str((x or {}).get("family") or "").replace("PMID ", "")
        v = (x or {}).get("our_value") or {}
        served_key = next((k for k in reads if k.startswith(f"served|{slug}|") and k.endswith(f"PMID {fam}")), None)
        if x is None or not served_key:
            row["state"] = "EXTRACTOR_DOES_NOT_REPRODUCE (no retired served read for this trial)"
        else:
            num = reads[served_key]["numbers"]
            same = all(_eq(num.get(a), v.get(b)) for a, b in (("effect", "effect"), ("ci_low", "lower"), ("ci_high", "upper")))                 if v.get("effect") is not None else                 all(num.get(a) is not None and int(num[a]) == int(v.get(b)) for a, b in
                    (("ai", "events_t"), ("n1i", "n_t"), ("ci", "events_c"), ("n2i", "n_c")))
            row["state"] = "RETIRABLE_BY_EXTRACTOR" if same else "EXTRACTOR_DOES_NOT_REPRODUCE (tracker value differs)"
            row["tracker_value"] = v
            if same:
                reads[key] = dict(reads[served_key], via=served_key)
        report.append(row)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    json.dump({"rule": __doc__.split("\n\n")[1], "extractor_sha256": xsha, "served_ref": ref or "working tree",
               "rows": report}, open(REPORT, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    json.dump({"_doc": "HAND_ENTERED served values the deterministic extractor reproduces from a held document "
                       "(scripts/provenance_extractor_reads.py); each names the document, its sha256, the span and the "
                       "extractor bytes", "reads": reads},
              open(OUT, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False, sort_keys=True)
    for r in report:
        print(r["state"], "|", r["key"], "|", r.get("served"))
        for x in r.get("tried") or []:
            print("     ", x["document"][:80], "->", x["extractor"])
    print(f"{len(reads)} of {len(hand.get('rows') or [])} hand-entered rows reproduced by the extractor")
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
