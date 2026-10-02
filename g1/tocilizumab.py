"""G1 MATCH, tocilizumab COVID-19 28-day mortality, against WHO REACT 2021 (PMID 34228774): 19 tocilizumab trials,
fixed-effect OR 0.83 (0.74-0.92).

Source hierarchy (Mahmood, 2026-10-02):
  PRIMARY    the trial's own posted CT.gov results (local AACT snapshot) and its own open full text / abstract;
  SECONDARY  per-trial rows printed by a meta-analysis.
TWO-SOURCE RULE: a trial's 28-day deaths per arm count as ESTABLISHED only when two INDEPENDENT sources agree, at least
  one of them primary (a registry and a paper are independent; an abstract and its own full text are one source).
ANTI-CIRCULARITY: a row read from REACT is the comparator, never a source. It is compared WITH; it never verifies
  itself, never fills a gap, and never enters 'k matched' (harness.secondary_meta.g1_countable says the same).
DENOMINATORS are kept by kind and never interchanged: RANDOMISED (ITT), ANALYSED (outcome recorded / mITT, e.g. 'all
  randomised who received study drug'), SAFETY (treated; adverse-event tables). A safety-table death count is never an
  efficacy 28-day row. Two rows that agree on deaths but differ only in denominator kind are reported as such.
TIMEPOINT: 28 days. Another day (PreToVid's day 30; a 60- or 90-day count) is never matched as day 28.

Every number is derived by rule from held bytes (AACT row ids, text spans), so the result replays offline.
"""
from __future__ import annotations

import json
import math
import os
import re
from collections import defaultdict
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "tocilizumab-covid19-mortality"
REACT_FILE = os.path.join(ROOT, "g1", "data", "react_rows.json")
AACT_FILE = os.path.join(ROOT, "g1", "data", "aact_toci.json")

RANDOMISED, ANALYSED, SAFETY, UNSTATED = "RANDOMISED", "ANALYSED", "SAFETY", "UNSTATED"
ESTABLISHED, ONE_SOURCE, CONFLICT, NO_SOURCE = "ESTABLISHED", "ONE_SOURCE", "CONFLICT", "NO_PRIMARY_SOURCE"

# REACT's 19 trial labels -> registration, with the evidence that binds them (every one read from the local AACT
# snapshot's own record: acronym, title or secondary id). None = no registration in AACT (named, not guessed).
IDENTITY = {
    "ARCHITECTS": ("NCT04412772", "AACT studies.acronym = ARCHITECTS"),
    "BACC-Bay": ("NCT04356937", "our family NCT04356937 holds Stone 2020 (PMID 33085857), the BACC Bay trial"),
    "CORIMUNO-TOCI-1": ("NCT04331808", "AACT acronym CORIMUNO-TOC; its 'Severe COVID Population (WHO-CPS =5)' groups"),
    "CORIMUNO-TOCI-ICU": ("NCT04331808", "AACT acronym CORIMUNO-TOC; its 'Critical COVID Population (WHO-CPS >5)' groups"),
    "COV-AID": ("NCT04330638", "AACT studies.acronym = COV-AID"),
    "COVACTA": ("NCT04320615", "AACT studies.acronym = COVACTA"),
    "COVIDOSE2-SS-A": ("NCT04479358", "AACT acronym COVIDOSE-2; its 'Sub-study A' groups"),
    "COVIDSTORM": ("NCT04577534", "AACT studies.acronym = COVIDSTORM"),
    "COVINTOC": (None, "registered with CTRI (India), not in AACT; its own abstract (PMID 33676589, acquired by its name) "
                       "names COVINTOC"),
    "COVITOZ": ("NCT04435717", "AACT studies.acronym = COVITOZ-01"),
    "EMPACTA": ("NCT04372186", "AACT studies.acronym = EMPACTA"),
    "HMO-020-0224": ("NCT04377750", "AACT id_information secondary id '0224-20-HMO-CTIL'"),
    "ImmCoVA": ("NCT04412291", "AACT official title names ImmCoVA; our family holds its 2023 paper (PMID 38157348)"),
    "PreToVid": (None, "registered in the Netherlands Trial Register, not in AACT"),
    "RECOVERY": ("NCT04381936", "AACT studies.acronym = RECOVERY"),
    "REMAP-CAP": ("NCT02735707", "AACT studies.acronym = REMAP-CAP"),
    "REMDACTA": ("NCT04409262", "AACT studies.acronym = REMDACTA"),
    "TOCIBRAS": ("NCT04403685", "AACT studies.acronym = TOCIBRAS"),
    "TOCOVID": ("NCT04332094", "AACT studies.acronym = TOCOVID"),
}
# a registration that holds more than one REACT row: the posted group titles that are THIS row's population
SUBPOP = {"CORIMUNO-TOCI-1": r"Severe COVID", "CORIMUNO-TOCI-ICU": r"Critical COVID", "COVIDOSE2-SS-A": r"Sub-study A"}

_DEATH_WORDS = re.compile(r"\b(?:died|deaths?|dead|fatal(?: events?)?|mortality|death from any cause|all-cause mortality)\b",
                          re.I)
_DAY28 = re.compile(r"\b(?:day\s*28|28\s*days?|28-day|by day 28|week\s*4|within 28)\b", re.I)
_OTHER_DAY = re.compile(r"\b(?:day\s*(?:14|21|30|60|90)|(?:14|21|30|60|90)\s*days?|(?:30|60|90)-day)\b", re.I)
_TOCI = re.compile(r"toci|tcz|actemra|il-6|interleukin", re.I)
_CONTROL = re.compile(r"placebo|standard of care|standard care|usual care|\bsoc\b|control", re.I)
_SURVIV = re.compile(r"surviv|alive", re.I)
# a composite ('mechanical ventilation or death', 'alive and free of respiratory failure') is never 28-day mortality
_OTHER_EVENT = re.compile(r"ventilat|intubat|\bicu\b|intensive care|respiratory failure|discharge|progression|"
                          r"worsening|clinical failure|recovery|improvement|free of", re.I)
SECOND_META = "34019122"          # Tocilizumab in COVID-19: meta-analysis, TSA and meta-regression of RCTs (PMC8139226)
SECOND_META_FILE = os.path.join(ROOT, "registry", "secondary_meta", f"{SLUG}.json")
# the second meta's row label names the trial's acronym in parentheses; CORIMUNO names two REACT rows, and its first
# author (Hermine) is the first author of our held CORIMUNO-TOCI-1 report (PMID 33080017)
_META_ACRONYM = {"BACC": "BACC-Bay", "EMPACTA": "EMPACTA", "TOCIBRAS": "TOCIBRAS", "COVINTOC": "COVINTOC",
                 "COVACTA": "COVACTA", "RECOVERY": "RECOVERY", "REMAP-CAP": "REMAP-CAP", "CORIMUNO": "CORIMUNO-TOCI-1"}


# ------------------------------------------------------------------------------------------------- derivations
def unique_count(percent: str, n: int) -> Optional[int]:
    """The ONE integer k with round(100*k/n, d) == percent (d = the printed decimals); None if zero or several do --
    a percentage is converted to a count only when the count is determined."""
    try:
        p = float(percent)
    except (TypeError, ValueError):
        return None
    d = len(str(percent).split(".")[1]) if "." in str(percent) else 0
    ks = [k for k in range(0, n + 1) if round(100.0 * k / n, d) == round(p, d)]
    return ks[0] if len(ks) == 1 else None


def denominator_kind(population: str) -> str:
    t = (population or "").lower()
    if re.search(r"safety|treated population|received (?:any|at least one)", t) and "itt" not in t:
        return SAFETY
    if re.search(r"modified intent|mitt|received (?:any amount|study (?:drug|medication|treatment))|outcome (?:data|recorded)|"
                 r"evaluable|analy[sz]ed", t):
        return ANALYSED
    if re.search(r"intent(?:ion)?[- ]to[- ]treat|all randomi[sz]ed|\bitt\b", t):
        return RANDOMISED
    return UNSTATED


# ------------------------------------------------------------------------------------------------- AACT (primary)
def build_aact_extract(ncts: list) -> dict:
    """One streaming pass over the local snapshot: every posted outcome that names death or survival, with its groups,
    measurements and analysed counts, keyed by AACT row ids (so the extract is checkable against the snapshot)."""
    import sys
    sys.path.insert(0, ROOT)
    from harness import aact
    want = set(ncts)
    outs = {}
    for r in aact._iter_rows(aact._table("outcomes")):
        if r["nct_id"] in want and (_DEATH_WORDS.search(r.get("title") or "") or _SURVIV.search(r.get("title") or "")):
            outs[r["id"]] = {k: r.get(k) for k in ("nct_id", "outcome_type", "title", "time_frame", "population", "units",
                                                     "param_type")}
    groups = {}
    for r in aact._iter_rows(aact._table("result_groups")):
        if r["nct_id"] in want:
            groups[r["id"]] = r.get("title")
    meas, cnt = defaultdict(list), defaultdict(dict)
    for r in aact._iter_rows(aact._table("outcome_measurements")):
        if r.get("outcome_id") in outs:
            meas[r["outcome_id"]].append({"row_id": r["id"], "group": groups.get(r.get("result_group_id")),
                                          "classification": r.get("classification") or r.get("category") or "",
                                          "param_type": r.get("param_type"), "value": r.get("param_value")})
    for r in aact._iter_rows(aact._table("outcome_counts")):
        if r.get("outcome_id") in outs:
            cnt[r["outcome_id"]][groups.get(r.get("result_group_id"))] = r.get("count")
    snap = aact.snapshot_dir()
    return {"snapshot": os.path.basename(snap or ""), "ncts": sorted(want),
            "outcomes": {oid: dict(o, measurements=meas[oid], analysed=cnt[oid]) for oid, o in outs.items()}}


def aact_28d(label: str, extract: dict) -> list:
    """Candidate 28-day death rows for one REACT label from its posted results: a death/mortality/survival outcome whose
    time frame or classification is day 28, one tocilizumab group and one control group of the row's population."""
    nct = IDENTITY[label][0]
    out = []
    for oid, o in (extract.get("outcomes") or {}).items():
        if o["nct_id"] != nct or _OTHER_EVENT.search(o.get("title") or ""):
            continue
        if (o.get("param_type") or "").upper() in ("MEDIAN", "MEAN") and "percent" not in (o.get("units") or "").lower():
            continue                                  # a time-to-death summary is not a count of the dead
        sub = SUBPOP.get(label)
        surv = bool(_SURVIV.search(o.get("title") or "")) and not _DEATH_WORDS.search(o.get("title") or "")
        rows = defaultdict(dict)
        for m in o["measurements"]:
            g = m["group"] or ""
            if sub and not re.search(sub, g, re.I):
                continue
            cls = m["classification"]
            when = cls if cls else (o.get("time_frame") or "")
            if not _DAY28.search(when) or (cls and _OTHER_DAY.search(cls)) or (not cls and _OTHER_DAY.search(when)
                                                                               and not _DAY28.search(when)):
                continue
            arm = "t" if _TOCI.search(g) and not re.search(r"free|placebo", g, re.I) else "c" if _CONTROL.search(g) else None
            if not arm:
                continue
            n = o["analysed"].get(m["group"])
            try:
                n = int(n)
            except (TypeError, ValueError):
                continue
            pt = (m["param_type"] or "").upper()
            if pt == "COUNT_OF_PARTICIPANTS":
                k = int(float(m["value"]))
                deaths, how = (n - k, "survivors counted") if surv else (k, "count posted")
            elif pt == "NUMBER" and "percent" in (o.get("units") or "").lower():
                k = unique_count(m["value"], n)
                if k is None:
                    continue
                deaths, how = (n - k, f"survival {m['value']}% of {n}") if surv else (k, f"{m['value']}% of {n}")
            else:
                continue
            rows[arm].setdefault("parts", []).append((deaths, n, how, m["row_id"], g))
        if "t" in rows and "c" in rows:
            t = rows["t"]["parts"]
            c = rows["c"]["parts"]
            out.append({"source": "AACT", "outcome_id": oid, "title": o.get("title"), "time_frame": o.get("time_frame"),
                        "deaths_t": sum(p[0] for p in t), "n_t": sum(p[1] for p in t),
                        "deaths_c": sum(p[0] for p in c), "n_c": sum(p[1] for p in c),
                        "denominator_kind": denominator_kind(o.get("population") or "") if o.get("population")
                        else ANALYSED,           # an AACT outcome count IS the number of participants analysed
                        "derivation": "; ".join(f"{p[4]}: {p[2]} -> {p[0]} deaths (row {p[3]})" for p in t + c)})
    return out


# ------------------------------------------------------------------------------------------------- text (primary)
def _fold(s: str) -> str:
    import html as _h
    s = re.sub(r"<[^>]+>", " ", s or "")                      # held full texts are JATS XML
    s = _h.unescape(s).replace(" ", " ").replace("\xa0", " ").replace("−", "-")
    return re.sub(r"\s+", " ", s)


def _pct_ok(p: str, d: int, n: int) -> bool:
    """The printed percentage is d/n at its printed precision, ROUNDED or TRUNCATED (BMJ tables truncate: TOCIBRAS
    prints 14/65 = 21.5% as '21')."""
    dec = len(p.split(".")[1]) if "." in p else 0
    if n <= 0:
        return False
    x, f = 100.0 * d / n, float(p)
    return round(x, dec) == round(f, dec) or math.floor(x * 10 ** dec) / 10 ** dec == round(f, dec)


def text_locates(row: dict, text: str) -> Optional[str]:
    """Both arms' deaths, each with its denominator stated ('58 of 294', '58/294') or implied by a printed percentage
    that the row's N reproduces ('58 patients (19.7%)' with N=294), in one window with a death word and a 28-day word.
    A percentage computed on ANOTHER denominator (a safety population: '28 (19.6%)' = 28/143) does not locate the
    efficacy row 28/144: denominator kinds are never interchanged."""
    t = _fold(text)

    def arm(d, n):
        nn = f"(?:{n:,}|{n})"
        return re.compile(rf"(?<![\d.]){d}\s*(?:patients?\s*|participants?\s*)?(?:\((?P<p>\d+(?:\.\d+)?)\s*%\)\s*)?"
                          rf"(?:(?:/|of|out of)\s*(?:the\s+)?(?P<n>{nn})(?![\d]))?", re.I)

    def hits(d, n, win):
        for m in arm(d, n).finditer(win):
            if m.group("n") or (m.group("p") and _pct_ok(m.group("p"), d, n)):
                return True
        return False
    for m in arm(row["deaths_t"], row["n_t"]).finditer(t):
        if not (m.group("n") or (m.group("p") and _pct_ok(m.group("p"), row["deaths_t"], row["n_t"]))):
            continue
        win = t[max(0, m.start() - 300): m.end() + 300]
        if hits(row["deaths_c"], row["n_c"], win) and _DEATH_WORDS.search(win) and _DAY28.search(win):
            return win
    # percentages only, in one death + day-28 sentence ('Death from any cause by day 28 occurred in 10.4% of the
    # patients in the tocilizumab group and 8.6% of those in the placebo group'): both percentages reproduced by the
    # row's counts at the row's N, in the order of their arm words
    for s in re.split(r"(?<=[.;])\s+(?=[A-Z(])", t):
        if not (_DEATH_WORDS.search(s) and _DAY28.search(s)) or _OTHER_EVENT.search(s):
            continue
        # a CI level ('95% CI') is not an arm's percentage; a percentage printed BESIDE a count ('42 (19.5%)') is the
        # count's -- the count must then match (the first path), never be bypassed by its percentage: REMDACTA's paper
        # prints '42 (19.5%) ... died on or before day 28' while the registry's mITT row is 41/210 (19.5%)
        ps = [p for p in re.finditer(r"(?<![\d.])(\d{1,3}(?:\.\d)?)\s*%(?!\s*(?:CI|confidence|credib))", s)]
        if len(ps) != 2 or any(re.search(r"\d\s*(?:patients?\s*|participants?\s*)?\(\s*$", s[max(0, p.start() - 25):p.start()])
                               for p in ps):
            continue
        low = s.lower()
        a1 = low.find("tocilizumab", ps[0].end())
        c1 = min([i for i in (low.find(w, ps[0].end()) for w in ("placebo", "usual care", "standard")) if i >= 0] or [10 ** 6])
        first_t = a1 >= 0 and a1 < c1
        pt, pc = (ps[0], ps[1]) if first_t else (ps[1], ps[0])
        if _pct_ok(pt.group(1), row["deaths_t"], row["n_t"]) and _pct_ok(pc.group(1), row["deaths_c"], row["n_c"]):
            return s
    return None


# "Standard-of-care group ( n = 29)" (COVIDSTORM): the hyphenated form is the same arm word (plant Q9)
_TABLE_HEAD = re.compile(r"(tocilizumab|tcz|usual care|placebo|standard[- ](?:of[- ])?care|control)[^()]{0,30}\(\s*n\s*=\s*(\d+)\s*\)",
                         re.I)
_TABLE_ROW = re.compile(r"((?:mortality|death|died)[^0-9]{0,40}?(?:28 days|day 28|28-day|28 d\b)[^0-9]{0,20})"
                        r"(\d{1,4})\s*\((\d{1,3}(?:\.\d+)?)\)\s*(\d{1,4})\s*\((\d{1,3}(?:\.\d+)?)\)", re.I)


def table_candidates(text: str) -> list:
    """A flattened table row naming death at day 28 with two 'd (p)' cells, under a header that gives each arm's n
    ('Tocilizumab group (n=65) Control group (n=64) ... Mortality up to 28 days 14 (21) 6 (9)'): columns follow the
    header order, and each printed percentage must be its d over that column's n."""
    t = _fold(text)
    out = []
    for m in _TABLE_ROW.finditer(t):
        heads = list(_TABLE_HEAD.finditer(t, max(0, m.start() - 4000), m.start()))
        if len(heads) < 2:
            continue
        h1, h2 = heads[-2], heads[-1]
        a1 = "t" if h1.group(1).lower() in ("tocilizumab", "tcz") else "c"
        a2 = "t" if h2.group(1).lower() in ("tocilizumab", "tcz") else "c"
        if {a1, a2} != {"t", "c"}:
            continue
        cells = {a1: (int(m.group(2)), m.group(3), int(h1.group(2))), a2: (int(m.group(4)), m.group(5), int(h2.group(2)))}
        if not all(_pct_ok(p, d, n) for d, p, n in cells.values()):
            continue
        out.append({"deaths_t": cells["t"][0], "n_t": cells["t"][2], "deaths_c": cells["c"][0], "n_c": cells["c"][2],
                    "denominator_kind": UNSTATED, "span": (h1.group(0) + " ... " + h2.group(0) + " ... " + m.group(0))[:400]})
    return out


_PAIR = re.compile(r"(?<![\d.,])(\d{1,4})\s*(?:patients?\s*|participants?\s*)?(?:\(\s*\d+(?:\.\d+)?\s*%\s*\)\s*)?"
                   r"(?:of|/|out of)\s*(?:the\s+)?(\d{1,3}(?:,\d{3})|\d{1,5})(?![\d])", re.I)


def text_candidates(text: str) -> list:
    """INDEPENDENT extraction (never guided by REACT): a sentence naming death and day 28 that carries exactly two
    'd of N' pairs, each after an arm word (tocilizumab vs usual care / placebo / standard care)."""
    out = []
    for s in re.split(r"(?<=[.;])\s+(?=[A-Z(])", _fold(text)):
        if not (_DEATH_WORDS.search(s) and _DAY28.search(s)) or _OTHER_EVENT.search(s) or _OTHER_DAY.search(s):
            continue
        pairs = list(_PAIR.finditer(s))
        if len(pairs) != 2:
            continue
        arms = []
        low = s.lower()
        for i, p in enumerate(pairs):
            # the NEAREST arm word on either side, bounded by the neighbouring pair ('621 (31%) of 2022 patients
            # allocated tocilizumab and 729 (35%) of 2094 ... usual care': each pair's arm follows it)
            lo = pairs[i - 1].end() if i else 0
            hi = pairs[i + 1].start() if i + 1 < len(pairs) else len(s)
            arm_rx = re.compile(r"tocilizumab|\btcz\b|usual care|placebo|standard (?:of )?care|control")
            after = arm_rx.search(low, p.end(), min(hi, p.end() + 60))      # '621 ... patients allocated tocilizumab'
            before = list(arm_rx.finditer(low, lo, p.start()))              # 'in the tocilizumab group, 58 of 294'
            w = after.group(0) if after else (before[-1].group(0) if before else None)
            arms.append(None if w is None else "t" if w in ("tocilizumab", "tcz") else "c")
        if sorted(arms) != ["c", "t"]:
            continue
        v = {a: (int(p.group(1)), int(p.group(2).replace(",", ""))) for a, p in zip(arms, pairs)}
        if v["t"][0] > v["t"][1] or v["c"][0] > v["c"][1]:
            continue
        out.append({"deaths_t": v["t"][0], "n_t": v["t"][1], "deaths_c": v["c"][0], "n_c": v["c"][1],
                    "denominator_kind": RANDOMISED if re.search(r"randomi[sz]ed|intention", s, re.I) else UNSTATED,
                    "span": s[:400]})
    return out


_SAFETY_CAPTION = re.compile(r"adverse events? in the safety population|safety population|adverse events?\b[^.]{0,40}table|"
                             r"table \d+\s*adverse events", re.I)
_SAFETY_ROW = re.compile(r"\b(?:death|died|fatal(?: events?)?)\s+(\d{1,4})\s*\((\d{1,3}(?:\.\d+)?)\)\s*(\d{1,4})\s*\((\d{1,3}(?:\.\d+)?)\)",
                         re.I)


def safety_candidates(text: str) -> list:
    """A death row of an ADVERSE-EVENT / SAFETY-population table ('Table 4 Adverse Events in the Safety Population ...
    Tocilizumab (N=161) Placebo (N=82) ... Death 9 (5.6) 4 (4.9)'). Read and SHOWN, labelled SAFETY: the treated
    population's adverse-event deaths are never the efficacy 28-day row (denominator kinds are not interchanged)."""
    t = _fold(text)
    out = []
    for cap in _SAFETY_CAPTION.finditer(t):
        seg = t[cap.start(): cap.start() + 2500]
        heads = list(_TABLE_HEAD.finditer(seg))
        row = _SAFETY_ROW.search(seg)
        if len(heads) < 2 or not row:
            continue
        h1, h2 = heads[0], heads[1]
        a1 = "t" if h1.group(1).lower() in ("tocilizumab", "tcz") else "c"
        a2 = "t" if h2.group(1).lower() in ("tocilizumab", "tcz") else "c"
        if {a1, a2} != {"t", "c"}:
            continue
        cells = {a1: (int(row.group(1)), row.group(2), int(h1.group(2))), a2: (int(row.group(3)), row.group(4), int(h2.group(2)))}
        if all(_pct_ok(p, d, n) for d, p, n in cells.values()):
            out.append({"deaths_t": cells["t"][0], "n_t": cells["t"][2], "deaths_c": cells["c"][0], "n_c": cells["c"][2],
                        "denominator_kind": SAFETY, "span": (cap.group(0) + " ... " + h1.group(0) + " ... " + h2.group(0)
                                                             + " ... " + row.group(0))[:400]})
    return out


def second_meta_rows() -> dict:
    """The second meta's rows (OR + CI; a recorded, replayable figure reading on the k-gap lane), bound to REACT labels
    by the acronym its label prints. SECONDARY: it can confirm a primary row's counts, never supply them."""
    if not os.path.exists(SECOND_META_FILE):
        return {}
    out = {}
    for r in json.load(open(SECOND_META_FILE, encoding="utf-8")).get("rows") or []:
        if str(r.get("meta_pmid")) != SECOND_META:
            continue
        m = re.search(r"\(([^)]+)\)", r.get("trial_label") or "")
        lab = _META_ACRONYM.get((m.group(1) if m else "").upper().replace("RCT-TCZ-COVID-19", "")) if m else None
        if lab:
            out[lab] = {k: r.get(k) for k in ("trial_label", "measure", "effect", "lower", "upper", "provenance")}
    return out


META2_FILE = os.path.join(ROOT, "g1", "data", "meta2_forest.json")
_META2 = None          # run() caches meta2_rows() here


def _pmid_to_label() -> dict:
    """PMID -> REACT label(s), from OUR bindings only: a held cache paper by its registration majority (held_texts) and
    an acquired paper by its bound_labels. Never from a meta's numbers."""
    out = {}
    for label in IDENTITY:
        for ref, _ in held_texts(label):
            out.setdefault(ref.split()[1], set()).add(label)
    return out


def _doi_to_pmid() -> dict:
    out = {}
    for f in (os.listdir(os.path.join(ROOT, "g1", "data", "cascade")) if os.path.isdir(os.path.join(ROOT, "g1", "data", "cascade")) else []):
        if f.endswith(".json") and f[0].isupper():
            for c in json.load(open(os.path.join(ROOT, "g1", "data", "cascade", f), encoding="utf-8")).get("candidates") or []:
                if c.get("doi"):
                    out[c["doi"].lower()] = c["pmid"]
    return out


def meta2_rows() -> dict:
    """{label: [row, ...]} from the REACT-independent open second metas (scripts/g1_toci_meta2_forest.py): rows admitted
    by its gates AND printed identically by two readers. A row binds to a trial through the META'S OWN REFERENCE LIST
    (its superscript reference number, or its first author + year) -> the cited paper's PMID/DOI -> the trial our held
    copy of that paper is bound to. SECONDARY: it can confirm a primary reading's counts, never supply them."""
    if not os.path.exists(META2_FILE):
        return {}
    p2l, d2p = _pmid_to_label(), _doi_to_pmid()
    out = {}
    for mp, res in json.load(open(META2_FILE, encoding="utf-8")).items():
        if res.get("state") != "PASS" or (res.get("independence") or {}).get("state") != "INDEPENDENT":
            continue
        jp = next((os.path.join(ROOT, "cache", "comparators", mp, f) for f in
                   os.listdir(os.path.join(ROOT, "cache", "comparators", mp)) if f.startswith("g1_meta2_")), None)
        x = open(jp, encoding="utf-8").read() if jp else ""
        refs = []
        for r in re.findall(r"<ref[ >].*?</ref>", x, re.S):
            lab = re.search(r"<label>\s*(\d+)", r)
            pm = re.search(r'pub-id-type="pmid">(\d+)', r)
            doi = re.search(r'pub-id-type="doi">([^<]+)', r) or re.search(r"(10\.\d{4,9}/[^\s<\"]+)", r)
            refs.append({"n": lab.group(1) if lab else None, "text": _fold(re.sub(r"<[^>]+>", " ", r)),
                         "pmid": pm.group(1) if pm else (d2p.get(doi.group(1).rstrip(".").lower()) if doi else None)})
        for row in res.get("admitted_rows") or []:
            lab = row["label"]
            sup = re.search(r"[¹²³⁰-⁹]+$", lab.strip())
            hit = []
            if sup:
                n = sup.group(0).translate(str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹",
                                                         "0123456789"))
                hit = [r for r in refs if r["n"] == n]
            else:
                m = re.match(r"\s*([A-Z][A-Za-z'\-]+)(?:\s+et al\.?)?\s+(\d{4})", lab)
                if m:
                    hit = [r for r in refs if re.match(r"\s*\d*\.?\s*" + re.escape(m.group(1)) + r"\b", r["text"])
                           and m.group(2) in r["text"]]
            labels = sorted(p2l.get(hit[0]["pmid"], set())) if len(hit) == 1 and hit[0]["pmid"] else []
            rec = {"meta_pmid": mp, "label": lab, "cited_pmid": hit[0]["pmid"] if len(hit) == 1 else None,
                   "binding": ("BOUND" if labels else "UNBOUND: " + ("reference not resolved" if len(hit) != 1 else
                                                                     "cited paper is not one we hold bound to a trial")),
                   **{k: row[k] for k in ("events_t", "total_t", "events_c", "total_c")}}
            for l in labels or ["_unbound"]:
                out.setdefault(l, []).append(rec)
    return out


def meta_consistent(row: dict, m: dict) -> bool:
    """The meta's printed OR and CI (2 decimals) reproduced from the row's counts (Woolf, 0.5 for a single zero cell)."""
    lo = log_or(row)
    if not lo or m.get("measure") != "OR":
        return False
    y, v = lo
    est, l, u = math.exp(y), math.exp(y - 1.959964 * math.sqrt(v)), math.exp(y + 1.959964 * math.sqrt(v))
    try:
        return all(abs(a - float(b)) <= 0.0051 for a, b in ((est, m["effect"]), (l, m["lower"]), (u, m["upper"])))
    except (TypeError, ValueError):
        return False


def _held_papers() -> dict:
    """{pmid: text} for every held full text (cache ft_<pmid>.txt) and every held abstract, full text and abstract of one
    paper joined (they are ONE source)."""
    recs = {}
    for v in json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8")).values():
        if isinstance(v, list):
            recs.update({str(x.get("id")): x for x in v if isinstance(x, dict)})
    out = {}
    for pmid, r in recs.items():
        if pmid.isdigit() and r.get("abstract"):
            out[pmid] = r["abstract"]
    d = os.path.join(ROOT, "cache", SLUG)
    for f in os.listdir(d):
        m = re.match(r"ft_(\d+)\.txt$", f)
        if m:
            out[m.group(1)] = open(os.path.join(d, f), encoding="utf-8").read() + "\n" + out.get(m.group(1), "")
    return out


_HELD = None
# which acquired papers are read (plants switch these guards off): every acquired paper, and only for the trial(s) its
# own text binds it to (scripts/g1_toci_cascade.binding)
_ACQ_KEEP = lambda a: True                                              # noqa: E731
_ACQ_BOUND = lambda a, label: label in (a.get("bound_labels") or [])    # noqa: E731


def held_texts(label: str) -> list:
    """[(ref, text)]: the held papers that are THIS trial's -- a paper belongs to the registration its own text names
    most often (an assumption-free binding: PMID 34609549 names NCT04409262, so it is REMDACTA's paper, not COVINTOC's).
    A trial with no registration in AACT has no paper bound by this rule."""
    global _HELD
    _HELD = _HELD if _HELD is not None else _held_papers()
    nct = IDENTITY[label][0]
    out = []
    for pmid, text in sorted(_HELD.items()) if nct else []:
        names = re.findall(r"NCT\d{8}", text)
        if names and max(set(names), key=names.count) == nct:
            out.append((f"PMID {pmid}", text))
    # papers acquired for THIS trial (scripts/g1_toci_acquire.py): found by its registration in PubMed's secondary-id
    # field (or, for a trial with none, by its name in title/abstract), never a protocol, review or meta-analysis
    acq = os.path.join(ROOT, "g1", "data", "acquired")
    have = {r.split()[1] for r, _ in out}
    for f in sorted(os.listdir(acq)) if os.path.isdir(acq) else []:
        if not re.match(r"\d+\.json$", f):
            continue
        a = json.load(open(os.path.join(acq, f), encoding="utf-8"))
        if not _ACQ_KEEP(a):
            continue
        kinds = " ".join(a.get("pub_types") or []) + " " + (a.get("title") or "")
        # bound by scripts/g1_toci_cascade.binding(): the paper's own text names THIS trial's registration most (or,
        # for a trial with no registration, its name is in the title) -- being found by a search for it is not enough
        if not _ACQ_BOUND(a, label) or re.search(r"protocol|review|meta-analysis", kinds, re.I):
            continue
        if a["pmid"] in have:
            # the cache held this paper's ABSTRACT only; its acquired FULL TEXT joins it (one paper = one source). Before
            # this, the cached abstract shadowed RECOVERY's acquired full text (plant Q10).
            if a.get("fulltext"):
                i = next(j for j, (r, _) in enumerate(out) if r.split()[1] == a["pmid"])
                out[i] = (out[i][0] + " + acquired full text", a["fulltext"] + "\n" + out[i][1])
            continue
        body = (a.get("fulltext") or "") + "\n" + (a.get("abstract") or "")
        if body.strip():
            out.append((f"PMID {a['pmid']} (acquired: {a.get('query')})", body))
    return out


# ------------------------------------------------------------------------------------------------- per trial
_KEY = ("deaths_t", "n_t", "deaths_c", "n_c")


def assess(label: str, extract: dict, metas: Optional[dict] = None) -> dict:
    """Primary candidates (registry; the trial's own text, extracted independently), each confirmed or not by the other
    primary source and by the second meta. ESTABLISHED = two independent sources on the same four numbers, at least one
    primary. Primary sources that disagree on the numbers = CONFLICT (both kept, never averaged, never first-wins)."""
    nct, why = IDENTITY[label]
    texts = held_texts(label)
    metas = second_meta_rows() if metas is None else metas
    cands = [dict(c) for c in (aact_28d(label, extract) if nct else [])]
    for ref, txt in texts:
        for c in safety_candidates(txt):
            cands.append(dict(c, source=f"TEXT {ref} (safety-population table)"))
        for c in text_candidates(txt) + table_candidates(txt):
            if re.search(r"intention[- ]to[- ]treat|all randomi[sz]ed", _fold(txt), re.I) and c["denominator_kind"] == UNSTATED \
                    and re.search(r"randomi[sz]ed", c["span"], re.I):
                c["denominator_kind"] = RANDOMISED
            cands.append(dict(c, source=f"TEXT {ref}"))
    by_value = {}
    for c in cands:
        # a SAFETY reading never merges with an efficacy reading of the same numbers: they are different quantities
        key = tuple(c[k] for k in _KEY) + ((SAFETY,) if c.get("denominator_kind") == SAFETY else ())
        g = by_value.setdefault(key, {"row": {k: c[k] for k in _KEY}, "kinds": set(), "sources": [],
                                      "denominator_kind": c.get("denominator_kind")})
        g["kinds"].add(c["source"].split()[0])
        g["sources"].append({k: c.get(k) for k in ("source", "title", "time_frame", "derivation", "span", "denominator_kind")
                             if c.get(k)})
        if c["source"] == "AACT":                       # the registry row located in the trial's own text
            for ref, txt in texts:
                span = text_locates(c, txt)
                if span:
                    g["kinds"].add("TEXT")
                    g["sources"].append({"source": f"TEXT {ref} (locates the registry numbers)", "span": span[:400]})
                    break
    m = metas.get(label)
    for g in by_value.values():
        if m and meta_consistent(g["row"], m):
            g["kinds"].add("META")
            g["sources"].append({"source": f"SECONDARY meta {SECOND_META}: {m['trial_label']} OR {m['effect']} "
                                           f"({m['lower']}-{m['upper']}) reproduced from these counts"})
    m2 = (_META2 if _META2 is not None else meta2_rows()).get(label) or []
    for g in by_value.values():
        for r in m2:
            if (r["events_t"], r["total_t"], r["events_c"], r["total_c"]) == tuple(g["row"][k] for k in _KEY):
                g["kinds"].add("META")
                g["sources"].append({"source": f"SECONDARY meta {r['meta_pmid']} (independent of the comparator by its reference list; two readers): "
                                               f"'{r['label']}' cites PMID {r['cited_pmid']}; prints these counts"})
    every = list(by_value.values())
    groups = [g for g in every if g["denominator_kind"] != SAFETY]          # only efficacy readings can be the row
    est = [g for g in groups if len(g["kinds"]) >= 2 and g["kinds"] & {"AACT", "TEXT"}]
    if len(est) == 1 and len(groups) == 1:
        state, chosen = ESTABLISHED, est[0]
    elif len(groups) > 1:
        # two primary readings disagree. If exactly one is two-source established it stands, and the other is shown
        state, chosen = (ESTABLISHED, est[0]) if len(est) == 1 else (CONFLICT, None)
    elif groups:
        state, chosen = ONE_SOURCE, groups[0]
    else:
        state, chosen = NO_SOURCE, None
    row = dict(chosen["row"], denominator_kind=chosen["denominator_kind"]) if chosen else None
    return {"label": label, "registration": nct, "identity": why, "state": state, "row": row,
            "readings": [{"values": g["row"], "independent_sources": sorted(g["kinds"]), "sources": g["sources"],
                          "denominator_kind": g["denominator_kind"]} for g in every],
            "second_meta": m, "meta2_rows": m2, "texts_held": [r for r, _ in texts]}


# ------------------------------------------------------------------------------------------------- comparison, pooling
def compare(ours: Optional[dict], react: dict) -> dict:
    if not ours:
        return {"verdict": "NO_PRIMARY_ROW"}
    diffs = [f for f in ("deaths_t", "n_t", "deaths_c", "n_c") if ours[f] != react[f]]
    if not diffs:
        return {"verdict": "AGREE"}
    deaths_same = ours["deaths_t"] == react["deaths_t"] and ours["deaths_c"] == react["deaths_c"]
    return {"verdict": "DENOMINATOR_KIND_DIFFERS" if deaths_same else "DIFFER", "fields": diffs,
            "ours": {f: ours[f] for f in diffs}, "react": {f: react[f] for f in diffs},
            "our_denominator_kind": ours.get("denominator_kind")}


def log_or(row: dict) -> Optional[tuple]:
    a, b, c, d = row["deaths_t"], row["n_t"] - row["deaths_t"], row["deaths_c"], row["n_c"] - row["deaths_c"]
    if a + c == 0 or b + d == 0:
        return None                                   # no events (or no non-events) in either arm: carries no OR
    if 0 in (a, b, c, d):
        a, b, c, d = a + .5, b + .5, c + .5, d + .5   # a single zero cell only
    return math.log((a * d) / (b * c)), 1 / a + 1 / b + 1 / c + 1 / d


def pool_fe(rows: list) -> Optional[dict]:
    ys = [x for x in (log_or(r) for r in rows) if x]
    if not ys:
        return None
    w = [1 / v for _, v in ys]
    mu = sum(wi * y for wi, (y, _) in zip(w, ys)) / sum(w)
    se = math.sqrt(1 / sum(w))
    return {"k_informative": len(ys), "or": round(math.exp(mu), 4), "lo": round(math.exp(mu - 1.959964 * se), 4),
            "hi": round(math.exp(mu + 1.959964 * se), 4)}


def react() -> dict:
    return json.load(open(REACT_FILE, encoding="utf-8"))


def run(extract: Optional[dict] = None) -> dict:
    rx = react()
    extract = extract or json.load(open(AACT_FILE, encoding="utf-8"))
    rrows = {r["label"]: r for r in rx["rows"]}
    trials = []
    metas = second_meta_rows()
    global _META2
    _META2 = meta2_rows()
    for label in sorted(rrows):
        a = assess(label, extract, metas)
        a["vs_react"] = compare(a["row"], rrows[label])
        rv = {k: rrows[label][k] for k in _KEY}
        safety = [x for x in a["readings"] if x["denominator_kind"] == SAFETY and x["values"] == rv]
        if safety and a["vs_react"]["verdict"] != "AGREE":
            # REACT's row IS the paper's safety-population adverse-event count, not its efficacy 28-day row
            a["vs_react"] = dict(a["vs_react"], verdict="REACT_ROW_IS_SAFETY_POPULATION",
                                 safety_source=safety[0]["sources"][0].get("source"))
        a["react_row"] = rrows[label]
        trials.append(a)
    established = [t for t in trials if t["state"] == ESTABLISHED]
    same = [t["label"] for t in established]
    return {
        "comparator": {"pmid": rx["comparator_pmid"], "printed": {k: rx["governing"][k] for k in ("estimate", "ci_low", "ci_high", "k")}},
        "positive_control": pool_fe(rx["rows"]),            # REACT's own rows must reproduce its printed pool
        "trials": trials,
        "tally": {s: sum(1 for t in trials if t["state"] == s) for s in (ESTABLISHED, ONE_SOURCE, CONFLICT, NO_SOURCE)},
        "vs_react": {v: sum(1 for t in established if t["vs_react"]["verdict"] == v)
                     for v in ("AGREE", "DENOMINATOR_KIND_DIFFERS", "DIFFER", "REACT_ROW_IS_SAFETY_POPULATION")},
        "react_rows_that_are_safety_counts": [t["label"] for t in trials
                                               if t["vs_react"]["verdict"] == "REACT_ROW_IS_SAFETY_POPULATION"],
        # G1 'k matched': ESTABLISHED primary rows only, never a REACT row (anti-circularity)
        "k_matched": sum(1 for t in established if t["vs_react"]["verdict"] == "AGREE"),
        "pool_ours_established": pool_fe([t["row"] for t in established]),
        "pool_react_same_trials": pool_fe([rrows[l] for l in same]),
    }
