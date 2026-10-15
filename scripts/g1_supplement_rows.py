"""Read independent metas' supplements; a secondary number stays secondary until primary verification."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from kgap import k_gap
from harness.secondary_meta import SecondaryRow, UNVERIFIED, VERIFIED, verify_typed
import g1_trial_acquire as ta
import g1_registry_fill as rf
import g1_regulatory_source as rs
import g1_open_fill as of
import secondary_meta_build as sb
from k_gap_supplements import pmcid_of, supplement_hrefs

DATE = "2026-10-15"
BASE = ROOT / "outputs" / "k_gap" / "registry_fill"
OUT = BASE / "phase4_supplements"
COUNTS = re.compile(r"(?<!\d)(\d{1,6})\s*/\s*(\d{1,6})(?!\d)")
EFFECT = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*[\(\[]\s*(\d+(?:\.\d+)?)\s*(?:-|–|—|,|to)\s*(\d+(?:\.\d+)?)\s*[\)\]]")
MEASURES = {"HR": r"\bHR\b|\bhazard ratio\b", "RR": r"\bRR\b|\brisk ratio\b|\brelative risk\b",
            "OR": r"\bOR\b|\b(?i:odds ratio)\b"}
TIME = re.compile(r"\b\d+\s*[- ]\s*(?:day|week|month)s?\b", re.I)
IMAGES = {".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".bmp", ".svg", ".mp4"}


EXTRA_NAMES = {}       # label -> names from source-linked identity (trial_names), filled per run
_GENERIC_ACR = {"COVID", "COVID-19", "SARS", "SARS-CoV-2", "ARDS", "ICU", "RCT", "JAMA", "BMJ", "NEJM", "HF", "MACE",
                "PCOS", "CAP", "LDL", "HDL", "NYHA", "LVEF", "CI", "HR", "RR", "OR", "USA", "UK", "II", "III", "IV"}


def names(label):
    out = set(rs._label_acronyms(label)) | set(EXTRA_NAMES.get(label, ()))
    first = re.match(r"\s*([A-Z][a-z]+(?:[-'][A-Za-z]+)?)\b", label)
    if first and first[1] not in ("Effect", "Effects", "Efficacy", "Impact", "Comparison", "The", "A", "An"):
        out.add(first[1])
    return sorted(out, key=lambda s: (-len(s), s))


def trial_names(trial):
    """Names a supplement may print for the trial, each from a SOURCE: the acronym(s) in its report's PubMed title
    (': The CoDEX Randomized Clinical Trial'), its registry acronym (CT.gov API v2), and its first author's surname.
    A title-labelled trial ('Effect of Dexamethasone on ...') otherwise had only the name 'Effect' (14 Oct)."""
    import g1_identify as gi
    out = set()
    pm = str(trial.get("pmid") or "")
    if pm:
        try:
            rec = (gi.pubmed_records([pm]) or {}).get(pm) or {}
        except Exception:  # noqa: BLE001 - no name from a failed fetch, never a guess
            rec = {}
        for tok in re.findall(r"\b[A-Za-z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*\b", rec.get("title") or ""):
            if sum(c.isupper() for c in tok) >= 2 and len(tok) >= 4 and tok not in _GENERIC_ACR:
                out.add(tok)
        if rec.get("first_author"):
            out.add(rec["first_author"])
    for n in trial.get("ncts") or []:
        try:
            d, _sha, _st = gi.ctgov({"query.term": f"AREA[NCTId]{n}", "fields": "NCTId,Acronym", "pageSize": "1"})
            acr = ((d.get("studies") or [{}])[0].get("protocolSection") or {}).get("identificationModule", {}).get("acronym")
        except Exception:  # noqa: BLE001
            acr = None
        if acr and acr not in _GENERIC_ACR:
            out.add(acr)
    return sorted(out)


def named(text, labels, start=False):
    return any(re.search((r"^" if start else r"(?<!\w)") + re.escape(n) + r"\b", text) for n in labels)


def family_words(cfg):
    stop = set("all cause day days week weeks month months year years at by within overall total primary secondary "
               "any first incidence rate risk of the and or in to from through follow up hospital admission "
               "short long term cumulative new onset".split())
    words = set(re.findall(r"[a-z]+", " ".join(ta.outcome_terms(cfg)).lower())) - stop
    if words & {"mortality", "death", "deaths", "died"}:
        words |= {"mortality", "death", "deaths", "died"}
    return words


def contains(text, terms):
    return any(re.search(r"\b" + re.escape(t) + r"\b", text, re.I) for t in terms if t)


def arm(cell, cfg):
    inc = cfg.get("include") or {}
    # the intervention arm must name THIS topic's intervention: generic words ('steroids', 'treatment') let a
    # corticosteroid meta's 'Steroids' column pass as the tocilizumab arm of REMAP-CAP (15 Oct). Only the comparator
    # side may be generic (placebo / control / standard care)
    t = contains(cell, (cfg.get("intervention_terms") or []) + (inc.get("intervention_any") or []))
    c = contains(cell, (cfg.get("comparator_terms") or []) + (inc.get("comparator_any") or []) +
                 ["placebo", "control", "SOC", "standard", "usual"])
    return "t" if t and not c else "c" if c and not t else None


def typed_rows(text, label, meta, filename, cfg):
    """Column identity and arm identity must both be explicit; no positional guess."""
    rows, reasons = [], []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not named(line.strip(), names(label), start=True):
            continue
        cells = [c.strip() for c in line.strip().split(" | ")]
        hits = {j: list(COUNTS.finditer(c)) for j, c in enumerate(cells)}
        hits = {j: m for j, m in hits.items() if m}
        # the header of THIS table, however many rows sit above the trial: walk up through the contiguous '|' rows to
        # the table's edge (a 6-line window lost the header of every row below the fifth: REMAP-CAP, 14 Oct)
        k = i
        while k > 0 and " | " in lines[k - 1] and i - k < 200:
            k -= 1
        preceding = lines[max(0, k - 3):i]
        headers = [[c.strip() for c in s.split(" | ")] for s in reversed(preceding)
                   if " | " in s and not COUNTS.search(s) and not EFFECT.search(s)]
        outcome = next((h for h in headers if any(contains(c, family_words(cfg)) for c in h)), None)
        cols = [j for j, c in enumerate(outcome or []) if contains(c, family_words(cfg))]
        if len(cols) != 1:
            reasons.append("AMBIGUOUS_OUTCOME_COLUMNS" if cols else "NO_OUTCOME_HEADER")
            continue
        j = cols[0]
        if j not in hits or j + 1 not in hits or len(hits[j]) != 1 or len(hits[j + 1]) != 1:
            effects = list(EFFECT.finditer(cells[j])) if j < len(cells) else []
            if len(effects) != 1:
                reasons.append("FEWER_THAN_TWO_COUNT_CELLS" if len(hits) < 2 else "COUNTS_NOT_ADJACENT_AT_OUTCOME")
                continue
            caption = next((s for s in reversed(lines[max(0, k - 3):k]) if "|" not in s), "")
            above = headers[headers.index(outcome) + 1:headers.index(outcome) + 2]
            measure_text = " ".join([outcome[j], caption] + [" | ".join(h) for h in above])
            measures = {m for m, pattern in MEASURES.items()
                        if re.search(pattern, measure_text, 0 if m == "OR" else re.I)}
            if len(measures) != 1:
                reasons.append("EFFECT_MEASURE_AMBIGUOUS" if measures else "EFFECT_MEASURE_NOT_STATED")
                continue
            effect, lower, upper = effects[0].groups()
            if not float(lower) <= float(effect) <= float(upper):
                reasons.append("EFFECT_OUTSIDE_CI")
                continue
            orientation_cells = [c for h in headers for c in h] + [caption]
            phrases = [re.split(r"\b(?:vs|versus|compared with)\b", c, flags=re.I)
                       for c in orientation_cells]
            oriented = any(len(p) == 2 and arm(p[0], cfg) == "t" and arm(p[1], cfg) == "c"
                           for p in phrases)
            arm_headers = any({arm(c, cfg) for c in h} >= {"t", "c"} for h in headers)
            if not (oriented or arm_headers):
                reasons.append("EFFECT_ORIENTATION_NOT_STATED")
                continue
            header = outcome[j]
            times = {m.group() for m in TIME.finditer(header)}
            if not times:
                times = {m.group() for s in preceding if " | " not in s for m in TIME.finditer(s)}
            rows.append(SecondaryRow(meta_pmid=meta, meta_doi="", location={"kind": "supplement", "id": filename,
                                     "row_label": cells[0]}, source_digest=hashlib.sha256(text.encode()).hexdigest(),
                                     provenance="TYPED_SUPPLEMENT_EFFECT", trial_label=label, measure=measures.pop(),
                                     outcome_definition=header, timepoint=next(iter(times)) if len(times) == 1 else None,
                                     effect=effect, lower=lower, upper=upper))
            continue
        # a header with a different cell count than the row (merged 'Not specified' cells) is used only when the
        # outcome is the FIRST data column: no merged cell can precede it and shift the columns
        orders = {tuple(arm(h[k], cfg) for k in (j, j + 1)) for h in headers
                  if (len(h) == len(cells) or j == 1) and j + 1 < len(h) and
                  set(arm(h[k], cfg) for k in (j, j + 1)) == {"t", "c"}}
        if len(orders) != 1:
            reasons.append("AMBIGUOUS_ARM_HEADER" if orders else "NO_ARM_HEADER")
            continue
        order = next(iter(orders))
        values = {a: tuple(int(v) for v in hits[k][0].groups()) for a, k in zip(order, (j, j + 1))}
        if any(e > n or n == 0 for e, n in values.values()):
            reasons.append("INVALID_COUNTS")
            continue
        header = outcome[j]
        times = {m.group() for m in TIME.finditer(header)}
        if not times:
            times = {m.group() for s in preceding if " | " not in s for m in TIME.finditer(s)}
        rows.append(SecondaryRow(meta_pmid=meta, meta_doi="", location={"kind": "supplement", "id": filename,
                                 "row_label": cells[0]}, source_digest=hashlib.sha256(text.encode()).hexdigest(),
                                 provenance="TYPED_SUPPLEMENT", trial_label=label, measure="COUNTS",
                                 outcome_definition=header, timepoint=next(iter(times)) if len(times) == 1 else None,
                                 events_t=values["t"][0], n_t=values["t"][1], events_c=values["c"][0], n_c=values["c"][1]))
    return rows, reasons or ([] if rows else ["NO_TRIAL_ROW"])


def classify(row, held, cfg):
    different_estimand = (row.measure != "COUNTS" and
                          row.measure != (cfg.get("primary_outcome") or {}).get("estimand"))
    if different_estimand:
        row.reasons.append("MEASURE_NOT_TOPIC_ESTIMAND")
    if held.get("text"):
        open_copy = (held.get("text_origin") == "PMC" and
                     ta.pmc_copy(held["pmid"])["licence"] in ta.OPEN_COPY) or (
                         held.get("text_origin") == "UNPAYWALL" and str(held.get("doi_licence") or "").startswith("cc"))
        if not open_copy:
            return row, "PRIMARY_VERIFY_PENDING_RULING"
        row = verify_typed(row, [("text", f"PMID {held['pmid']}", held["text"])], ta.outcome_terms(cfg))
        if different_estimand and "MEASURE_NOT_TOPIC_ESTIMAND" not in row.reasons:
            row.reasons.append("MEASURE_NOT_TOPIC_ESTIMAND")
        if row.state == VERIFIED and not different_estimand:
            return row, "PRIMARY_VERIFIED"
    if row.timepoint is None:
        row.reasons.append("TIMEPOINT_NOT_STATED_BY_META")
    if not contains(row.outcome_definition, ta.outcome_terms(cfg)):
        row.reasons.append("OUTCOME_FAMILY_ONLY")
    return row, "SECONDARY_PROVISIONAL"


def held_jats(meta):
    paths = sorted((Path(k_gap.COMP_DIR) / meta).glob("*_kgap_jats.xml"))
    if not paths:
        return [], None
    path = paths[-1]
    # the harness's own JATS licence typing (D8): 'CC' only for CC BY / CC0, CC_RESTRICTED for NC / ND / SA. Comparing
    # the licence SENTENCE with short codes made every meta unlicensed (14 Oct review of the Codex draft)
    from reproducible_ai import record_licence as rl
    licence = "cc-by" if rl.jats_licence(str(path)) == "CC" else rl.jats_licence(str(path))
    return supplement_hrefs(meta, path.name.removesuffix("_kgap_jats.xml")), licence


def blocks(result):
    text = result.get("text") or ""
    markers = list(re.finditer(r"^=== SUPPLEMENT (.+?) ===\r?$", text, re.M))
    if markers:
        return [(m[1], text[m.end():markers[i + 1].start() if i + 1 < len(markers) else len(text)].strip("\r\n"))
                for i, m in enumerate(markers)]
    files = [f for f in result.get("files", []) if not f.get("skipped")]
    return [(files[0]["file"], text)] if text and len(files) == 1 else []


def model_gate(answer, text, label):
    if not isinstance(answer, dict) or answer.get("verdict") != "FOUND":
        return False
    quote = answer.get("quote")
    if not isinstance(quote, str) or not quote or quote not in text or not named(quote, names(label)):
        return False
    counts = [answer.get(k) for k in ("events_t", "n_t", "events_c", "n_c")]
    effects = [answer.get(k) for k in ("effect", "lower", "upper")]
    if any(v is not None for v in counts):
        if not all(type(v) is int and v >= 0 for v in counts) or answer.get("measure") != "COUNTS":
            return False
        if counts[0] > counts[1] or counts[2] > counts[3] or not counts[1] or not counts[3]:
            return False
    elif not all(v is not None and re.fullmatch(r"-?\d+(?:\.\d+)?", str(v)) for v in effects) or answer.get(
            "measure") not in {"RR", "OR", "HR", "MD"}:
        return False
    return all(re.search(r"(?<![\d.])" + re.escape(str(v)) + r"(?![\d.])", quote)
               for v in counts + effects if v is not None)


def model_row(text, label, meta, filename, licence, cfg):
    """Two recorded proposals must survive verbatim gates before primary verification."""
    if of.licence_class(licence) != "CC_BY_OR_CC0":
        return None, {"decision": "MODEL_REFUSED_LICENCE"}
    shown = "\n\n".join(of.prose_windows(text, names(label)))[:20000]
    ev = {"trial": label, "outcome": cfg.get("primary_outcome"),
          "supplement": {"meta_pmid": meta, "pmid": meta, "licence": licence, "text": shown}}
    instr = ("Read THIS trial's result only from this meta's supplement. Return events_t/n_t/events_c/n_c or "
             "effect/lower/upper exactly as printed, never calculated. Identify intervention versus comparator. "
             "quote must be an exact substring containing the trial name and every number returned. Use source META. "
             "If absent return SOURCE_ABSENT. Return JSON matching this schema: " + json.dumps(ta.SCHEMA))
    prompt = (instr + "\nEVIDENCE\n" + json.dumps(ev, ensure_ascii=False)).encode()
    audit, gated = {"readers": {}, "record_dir": str(Path(of.REC_DIR).relative_to(ROOT))}, []

    def read(reader, payload):
        rec = of._call(payload, reader, f"phase 4 supplement {meta} / {label}", hashlib.sha256(payload).hexdigest())
        ans = rf._answer(rec) if rec.get("state") == "RAN_OK" else None
        ok = model_gate(ans, text, label)
        audit["readers"][reader[0]] = {"state": rec.get("state"), "record_id": rec.get("record_id"),
                                      "gate": "ADMITTED" if ok else "REFUSED", "answer": ans}
        return rec, ans if ok and rec.get("record_id") else None

    for reader in (rf.READER_A, rf.READER_B):
        rec, ans = read(reader, prompt)
        if ans:
            gated.append(ans)
    states = [r["state"] for r in audit["readers"].values()]
    chosen = None
    if "REFUSED_LICENCE" in states:
        decision = "MODEL_REFUSED_LICENCE"
    elif any(s != "RAN_OK" for s in states):
        decision = "WAITING_READER_UNAVAILABLE"
    elif len(gated) == 2 and signature(gated[0]) == signature(gated[1]):
        chosen, decision = gated[0], "MODEL_ADMITTED_BOTH_READERS"
    elif gated:
        adj = prompt + ("\nAdjudicate these readings; equal one gated reader or SOURCE_ABSENT:\n" +
                        json.dumps(audit["readers"], ensure_ascii=False)).encode()
        rec, ans = read(rf.ADJUDICATOR, adj)
        chosen = next((a for a in gated if ans and signature(a) == signature(ans)), None)
        decision = ("MODEL_REFUSED_LICENCE" if rec.get("state") == "REFUSED_LICENCE" else
                    "WAITING_READER_UNAVAILABLE" if rec.get("state") != "RAN_OK" else
                    "MODEL_ADMITTED_ADJUDICATED" if chosen else "MODEL_NOT_ADMITTED_READERS_DISAGREE")
    else:
        decision = "MODEL_NOT_ADMITTED_NO_GATED_READING"
    audit["decision"] = decision
    if not chosen:
        return None, audit
    ids = [r["record_id"] for r in audit["readers"].values() if r["record_id"]]
    row = SecondaryRow(meta_pmid=meta, meta_doi="", location={"kind": "supplement", "id": filename,
                       "row_label": label}, source_digest=hashlib.sha256(text.encode()).hexdigest(),
                       provenance="MODEL_PROPOSAL:" + ",".join(ids), trial_label=label, state=UNVERIFIED,
                       outcome_definition=chosen.get("outcome_as_stated") or "",
                       timepoint=chosen.get("timepoint_as_stated") or None,
                       **{k: chosen.get(k) for k in ("measure", "events_t", "n_t", "events_c", "n_c", "effect", "lower", "upper")})
    return row, audit


def signature(answer):
    return (answer.get("measure"), of._tuple(answer), answer.get("outcome_as_stated"), answer.get("timepoint_as_stated"))


def read_sweep(slug):
    """The refreshed sweep where it changed (phase4_sweep_refresh/), else the committed one: a topic whose verdicts did
    not change has no refreshed copy (melatonin, 14 Oct)."""
    p = BASE / "phase4_sweep_refresh" / f"{slug}.json"
    if not p.exists():
        p = ROOT / "outputs" / "k_gap" / "sweep" / f"{slug}.json"
    return json.loads(p.read_text(encoding="utf-8"))


def aliases(meta):
    return {str(x).strip().lower().removeprefix("pmid ").removeprefix("https://doi.org/").removeprefix("doi:")
            for x in {str(meta)} | set(sb.meta_aliases(meta))}


def run_slug(slug, offline=False, model=False):
    cfg = rf.config(slug)
    tracker, trials = ta.targets(slug, None)
    comp = ta.comparator_pmid(slug, tracker)
    excluded = aliases(comp) | aliases(sb.comparator_pmid(slug))
    sweep = read_sweep(slug)
    by_label = {}
    for trial in sweep["trials"]:
        by_label.setdefault(trial["label"], set()).update(str(m) for m in trial.get("metas_found", []))
    candidates = {t["label"]: sorted(m for m in by_label.get(t["label"], []) if not aliases(m) & excluded)
                  for t in trials}
    out = {"slug": slug, "date": DATE, "metas": {}, "rows": [], "attempts": []}
    texts = {}
    for meta in sorted({m for ms in candidates.values() for m in ms}):
        hrefs, licence = held_jats(meta)
        has = any(Path(h.split("?", 1)[0]).suffix.lower() not in IMAGES for h in hrefs)
        result = k_gap.comparator_supplements(meta, pmcid_of(meta), hrefs, DATE, offline=offline) if has else {
            "state": "NO_SUPPLEMENTS", "files": []}
        files = [dict(f, format=Path(f["file"]).suffix.lower().lstrip("."), parsed=bool(f.get("text_chars")),
                      skipped=f.get("skipped") or (None if f.get("text_chars") else "NO_PARSED_TEXT"))
                 for f in result.get("files", [])]
        out["metas"][meta] = {"has_supplement": has, "formats": sorted({f["format"] for f in files}),
                              "fetched_state": result.get("fetched_state") or result["state"],
                              "state": result["state"], "files": files, "licence": licence}
        texts[meta] = blocks(result)
    for trial in trials:
        held = None
        if candidates[trial["label"]] and not offline:
            EXTRA_NAMES[trial["label"]] = trial_names(trial)
        for meta in candidates[trial["label"]]:
            for filename, text in texts[meta]:
                rows, reasons = typed_rows(text, trial["label"], meta, filename, cfg)
                attempt = {"trial": trial["label"], "meta": meta, "file": filename, "reasons": reasons}
                if not rows and model and named(text, names(trial["label"])) and contains(text, family_words(cfg)):
                    row, audit = model_row(text, trial["label"], meta, filename, out["metas"][meta]["licence"], cfg)
                    attempt["model"] = audit
                    if row:
                        rows.append(row)
                out["attempts"].append(attempt)
                for row in rows:
                    if held is None:
                        held = ta.evidence(dict(trial, slug=slug), cfg, comp)[1]
                    row, cls = classify(row, held, cfg)
                    out["rows"].append(dict(row.to_dict(), **{"class": cls, "trial": trial["label"], "meta": meta}))
    metas, rows = out["metas"], out["rows"]
    f = {"metas": len(metas), "with_supplement": sum(m["has_supplement"] for m in metas.values()),
         "fetched": sum(m["fetched_state"] in {"OK", "NO_TEXT_IN_SUPPLEMENTS", "CACHED"} for m in metas.values()),
         "parsed": sum(bool(texts[m]) for m in metas), "rows": len(rows), "trials": len({r["trial"] for r in rows})}
    f.update({c: sum(r["class"] == c for r in rows) for c in
              ("PRIMARY_VERIFIED", "PRIMARY_VERIFY_PENDING_RULING", "SECONDARY_PROVISIONAL")})
    out["funnel"] = f
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["run"])
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--model", action="store_true")
    a = ap.parse_args()
    for slug in a.slugs:
        out = run_slug(slug, a.offline, a.model)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"{slug}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        f = out["funnel"]
        print(f"FUNNEL SUPP {slug}: metas {f['metas']} -> with supplement {f['with_supplement']} -> fetched "
              f"{f['fetched']} -> parsed {f['parsed']} -> rows {f['rows']} (trials {f['trials']}) -> "
              f"PRIMARY_VERIFIED {f['PRIMARY_VERIFIED']} | PENDING_RULING {f['PRIMARY_VERIFY_PENDING_RULING']} | "
              f"SECONDARY_PROVISIONAL {f['SECONDARY_PROVISIONAL']}", flush=True)


if __name__ == "__main__":
    main()
