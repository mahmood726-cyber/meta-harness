"""K-gap fill PHASE 3 (open sources): the identity-less missing trials with a PMID, through open full text.

Per trial (scope and open-copy class from PHASE3_OPEN_CENSUS.json, scripts/g1_open_census.py):
  CENSUS      NOT_OPEN stops here (phase 4: published metas, SECONDARY)
  ELIGIBLE    a trial blocked on SCREENING (screener error / unaudited screen-out / record insufficient) is queued to the
              screening lane with its open-copy pointer, never acquired here
  TEXT        PMC structured text (k_gap_counterfactual.pmc_fulltext_cached) else the Unpaywall copy (kgap.k_gap.
              unpaywall_text, PDF / HTML text); held by sha256 + source + retrieval date (text cached, gitignored)
  TYPED       DETERMINISTIC first: g1_trial_acquire.table_tuple on PMC tables; on prose text the conservative line reader
              g1_regulatory_source.typed_counts (one outcome line, two percent-corroborated e/N cells, arms ordered by a
              header naming both), in windows around the outcome terms; a posted total short of the randomised total
              (posted_population_short) is refused
  COPY GATE   a find is ADMISSIBLE only from a copy the existing gate admits (g1_trial_acquire.OPEN_COPY: PMC CC / PMC author
              manuscript; an Unpaywall copy only under a 'cc' licence). A find from a copy with NO licence (bronze / green)
              is TYPED_FOUND_PENDING_RULING: Mahmood's ladder reads 'other OA text is regex-only', the gate refuses it,
              and changing the gate is the Captain's (never loosened here)
  MODEL       only CC BY / CC0 text may be shown to a model (D8); counted here when the typed step found nothing
Nothing is admitted into the tracker by this script: an ADMISSIBLE find is written as a candidate row for the real
admission path (phase '3_OPEN:<origin>').

    python scripts/g1_open_fill.py run SLUG [SLUG ...]   -> outputs/k_gap/registry_fill/phase3/<slug>.json
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
CENSUS = os.path.join(ROOT, "outputs", "k_gap", "registry_fill", "PHASE3_OPEN_CENSUS.json")
OUT = os.path.join(ROOT, "outputs", "k_gap", "registry_fill", "phase3")
WINDOW = 1800
_SCREENING = re.compile(r"^(?:SCREENER_ERROR|SCREENED_OUT_UNAUDITED|INSUFFICIENT_RECORD)")
MODEL_LICENCES = ("CC_BY_OR_CC0",)


def screening_blocked(row):
    return bool(_SCREENING.match(row.get("blocker_now") or ""))


def licence_class(lic):
    """Unpaywall / Europe PMC licence string -> CC_BY_OR_CC0 | CC_OTHER | NONE."""
    l_ = (lic or "").lower().replace("_", "-").replace(" ", "-")
    if not l_:
        return "NONE"
    if l_ in ("cc-by", "cc0", "pd", "public-domain") or re.fullmatch(r"cc-by(-\d(\.\d)?)?", l_):
        return "CC_BY_OR_CC0"
    if l_.startswith("cc"):
        return "CC_OTHER"
    return "NONE"


def prose_windows(text, terms, width=WINDOW):
    rx = re.compile("|".join(re.escape(t) for t in terms if t) or r"$^", re.I)
    spans = []
    for m in rx.finditer(text or ""):
        a, b = max(0, m.start() - width), m.end() + width
        if spans and a <= spans[-1][1]:
            spans[-1] = (spans[-1][0], b)
        else:
            spans.append((a, b))
    return [text[a:b] for a, b in spans]


def typed_read(text, origin, cfg):
    """(tuple dict, span, reader) or (None, None, None). Deterministic only."""
    import g1_trial_acquire as ta
    import g1_regulatory_source as rs
    po = cfg.get("primary_outcome") or {}
    terms = ta.outcome_row_terms(cfg)
    if origin == "PMC":
        tt = ta.table_tuple(text, terms, po.get("timepoint"))
        if tt:
            return tt[1], tt[2], "table_tuple"
    found = {}
    for w in prose_windows(text, terms):
        g = rs.typed_counts(w, terms, cfg.get("intervention_terms") or [], cfg.get("comparator_terms") or [])
        if g:
            found[tuple(sorted(g[0].items()))] = g
    if len(found) == 1:
        rr, line = next(iter(found.values()))
        return rr, line, "typed_counts"
    return None, None, None


def run_trial(slug, cfg, r):
    import g1_trial_acquire as ta
    out = {"label": r["label"], "pmid": r["pmid"], "phase": None, "census_class": r["class"],
           "blocker_now": r.get("blocker_now"), "stage": "CENSUS"}
    if r["class"] == "NOT_OPEN":
        return dict(out, decision="NOT_OPEN")
    if screening_blocked(r):
        return dict(out, stage="ELIGIBLE", decision="ELIGIBILITY_BLOCKED_QUEUED_TO_SCREENING",
                    open_copy={"pmcid": (r.get("europepmc") or {}).get("pmcid"), "unpaywall": r.get("unpaywall")})
    out["stage"] = "ELIGIBLE"
    text, origin, src = "", None, {}
    pmcid = (r.get("europepmc") or {}).get("pmcid") or r.get("held_pmcid")
    if pmcid:
        import k_gap_counterfactual as cfm
        try:
            text = cfm.pmc_fulltext_cached(r["pmid"]) or ""
        except Exception as exc:  # noqa: BLE001 - typed
            src["pmc_error"] = str(exc)[:120]
        if text:
            copy = ta.pmc_copy(r["pmid"])
            origin, src = "PMC", dict(src, pmcid=pmcid, copy_licence=copy["licence"],
                                      admissible=copy["licence"] in ta.OPEN_COPY,
                                      model_ok=copy["licence"] in ta.PROMPT_COPY and
                                      licence_class((r.get("europepmc") or {}).get("license")) in MODEL_LICENCES)
    doi = ((r.get("europepmc") or {}).get("doi") or "").lower()
    if not text and doi:
        from kgap import k_gap
        try:
            u = k_gap.unpaywall_text(doi, os.path.join(ROOT, "outputs", "k_gap", "_upw"),
                                     os.path.join(ROOT, "outputs", "k_gap", "unpaywall_text_index.json"), offline=False)
        except Exception as exc:  # noqa: BLE001 - typed
            u = {"state": "FETCH_ERROR", "error": str(exc)[:120]}
        text = u.get("text") or ""
        lic = (r.get("unpaywall") or {}).get("license")
        src = dict(src, doi=doi, unpaywall_state=u.get("state"), unpaywall_tried=u.get("tried"), licence=lic,
                   admissible=str(lic or "").startswith("cc"), model_ok=licence_class(lic) in MODEL_LICENCES)
        origin = "UNPAYWALL" if text else None
    if not text:
        return dict(out, decision="NO_TEXT_LAYER_OR_NOT_FETCHED", source=src)
    out.update(stage="TEXT", source=dict(src, origin=origin, chars=len(text),
                                         text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                                         retrieved=datetime.date.today().isoformat()))
    rr, span, reader = typed_read(text, origin, cfg)
    if rr:
        short = ta.posted_population_short(slug, r["pmid"], rr["n_t"] + rr["n_c"])
        if short:
            return dict(out, stage="TYPED", decision="TYPED_REFUSED_SUBPOPULATION", note=short)
        out.update(stage="TYPED", typed={"reader": reader, "value": rr, "span": (span or "")[:600]},
                   phase=f"3_OPEN:{origin}")
        return dict(out, decision="TYPED_FOUND_ADMISSIBLE" if src.get("admissible") else "TYPED_FOUND_PENDING_RULING")
    if src.get("model_ok"):
        return dict(out, decision="TYPED_NONE_MODEL_ELIGIBLE")
    return dict(out, decision="TYPED_NONE_NOT_MODEL_LICENSED")


def run(slugs):
    import g1_registry_fill as rf
    census = json.load(open(CENSUS, encoding="utf-8"))["rows"]
    os.makedirs(OUT, exist_ok=True)
    tot = {}
    for slug in slugs:
        cfg = rf.config(slug)
        rows = [run_trial(slug, cfg, r) for r in census if r["slug"] == slug]
        for x in rows:
            print(slug, "|", x["label"][:34], "|", x["census_class"], "|", x["decision"], "|",
                  (x.get("typed") or {}).get("value"), flush=True)
        json.dump({"slug": slug, "writer": "scripts/g1_open_fill.py", "census": os.path.basename(CENSUS), "rows": rows},
                  open(os.path.join(OUT, f"{slug}.json"), "w", encoding="utf-8", newline="\n"), indent=1,
                  ensure_ascii=False)
        st = lambda k: sum(1 for x in rows if x["decision"].startswith(k))  # noqa: E731
        f = {"n": len(rows), "open": sum(x["census_class"] != "NOT_OPEN" for x in rows),
             "eligible": sum(x["stage"] not in ("CENSUS",) and x["decision"] != "ELIGIBILITY_BLOCKED_QUEUED_TO_SCREENING"
                             for x in rows),
             "text": sum(x["stage"] in ("TEXT", "TYPED") for x in rows),
             "typed": st("TYPED_FOUND"), "admissible": st("TYPED_FOUND_ADMISSIBLE"),
             "pending": st("TYPED_FOUND_PENDING_RULING"), "model_eligible": st("TYPED_NONE_MODEL_ELIGIBLE")}
        tot[slug] = f
        print(f"FUNNEL OPEN {slug}: {f['n']} -> open {f['open']} -> eligible {f['eligible']} -> text {f['text']} -> typed "
              f"{f['typed']} (admissible {f['admissible']}, pending ruling {f['pending']}) | model-eligible "
              f"{f['model_eligible']}", flush=True)
    return tot


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    if not a or a[0] != "run":
        raise SystemExit("usage: run SLUG ...")
    run([x for x in a[1:] if not x.startswith("--")])
