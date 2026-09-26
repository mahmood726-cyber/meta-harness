"""R4 AMBIGUITY of the regex layer: every place harness/extract.py takes ONE match where several could disagree.

Each function here is a drop-in replacement for the harness function of the same name (installed in-process by
regex_layer.radius CHANGES, never by editing harness/extract.py). It computes the full candidate set at its site and:
  * RECORDS a hit when >1 DISTINCT candidate value exists (site in RECORD) -- used to count ambiguity on held text;
  * REFUSES (returns the function's existing absent result) when the site is in ENABLED;
  * otherwise returns EXACTLY what the harness function returns (the first pick) -- so installing these with ENABLED
    empty must change no output. That is a control, checked by scripts/r4_ambiguity_count.py.

Candidate value = the value the function would return had it picked that candidate instead (same assignment rule).
"""
from __future__ import annotations

import itertools
import re

from harness import extract as X
from harness.extract_values import ArmCounts, ArmHit, ContinuousArms, MeanSDHit, RateArms, RateHit

ENABLED: set[str] = set()
RECORD: set[str] = set()
HITS: list[dict] = []
CONTEXT: dict = {}


def _hit(site: str, text: str, values) -> None:
    if site in RECORD:
        HITS.append({**CONTEXT, "site": site, "text": text, "values": sorted(repr(v) for v in values)})


def _pair_values(hits, key=lambda h: tuple(h[1:])):
    """Every choice of two hits in reading order (the extractor always takes the first two)."""
    return {(key(a), key(b)) for a, b in itertools.combinations(hits, 2)}


# --- extract_arm_counts: sites arm_den (best-corroborating denominator), arm_samepos (dedup), arm_pairs (first two) ---
def extract_arm_counts(sentence, interv_terms, comp_terms, denom_each=None, arm_ns=None):
    groups = []
    for m in X._ARM.finditer(sentence):
        ev, pct, n = int(m.group(1)), float(m.group(2)), int(m.group(3))
        if n > 0 and abs(ev / n * 100 - pct) <= 1.5 and not X._negated(sentence, m.start()):
            groups.append(ArmHit(m.start(), ev, n))
    for m in X._ARM2.finditer(sentence):
        ev, n, pct = int(m.group(1)), int(m.group(2)), float(m.group(3))
        if n > 0 and abs(ev / n * 100 - pct) <= 1.5 and not X._negated(sentence, m.start()):
            groups.append(ArmHit(m.start(), ev, n))
    for m in X._ARM3.finditer(sentence):
        ev, n, pct = int(m.group(1)), int(m.group(2)), float(m.group(3))
        if n > 0 and ev <= n and abs(ev / n * 100 - pct) <= 1.5 and not X._negated(sentence, m.start()):
            groups.append(ArmHit(m.start(), ev, n))
    for m in X._ARM4.finditer(sentence):
        pct, ev, n = float(m.group(1)), int(m.group(2)), int(m.group(3))
        if n > 0 and ev <= n and abs(ev / n * 100 - pct) <= 1.5 and not X._negated(sentence, m.start()):
            groups.append(ArmHit(m.start(), ev, n))
    if len(groups) < 2 and (denom_each or arm_ns):
        low_s = sentence.lower()
        cands = denom_each if isinstance(denom_each, (list, tuple, set)) else [denom_each]
        cands = [int(c) for c in cands if c]
        arm_ns = arm_ns or {}
        armp = [(m.start(), int(m.group(1)), float(m.group(2)))
                for m in X._ARMP.finditer(sentence) if not X._negated(sentence, m.start())]
        ipos = min((low_s.find(t.lower()) for t in interv_terms if t.lower() in low_s), default=-1)
        cpos = min((low_s.find(t.lower()) for t in comp_terms if t.lower() in low_s), default=-1)
        used_reading_order = False
        if len(armp) == 2 and arm_ns.get("i") and arm_ns.get("c") and ipos >= 0 and cpos >= 0:
            first_arm = "i" if ipos <= cpos else "c"
            order = [first_arm, "c" if first_arm == "i" else "i"]
            paired = []
            for (pos, ev, pct), arm in zip(armp, order):
                d = int(arm_ns[arm])
                if d > 0 and ev <= d and abs(ev / d * 100 - pct) <= 1.0:
                    paired.append(ArmHit(pos, ev, d))
            if len(paired) == 2:
                groups.extend(paired)
                used_reading_order = True
        if not used_reading_order:
            for pos, ev, pct in armp:
                best = None
                ok = set()
                for den in cands:
                    if den > 0 and ev <= den and abs(ev / den * 100 - pct) <= 1.0:
                        ok.add(den)
                        if best is None or abs(ev / den * 100 - pct) < abs(ev / best * 100 - pct):
                            best = den
                if len(ok) > 1:
                    _hit("arm_den", sentence, ok)
                    if "arm_den" in ENABLED:
                        # the sentence is refused, not just this count: dropping only the count let a DIFFERENT
                        # group fill its place (tocilizumab 33085857 full text: 18/161 vs 5/82 -> 18/161 vs 27/243),
                        # which is a new guess, not a refusal
                        return None
                if best:
                    groups.append(ArmHit(pos, ev, best))
    seen, uniq = set(), []
    bypos: dict = {}
    for g in groups:
        bypos.setdefault(g[0], set()).add((g[1], g[2]))
    conflict = {p: v for p, v in bypos.items() if len(v) > 1}
    if conflict:
        _hit("arm_samepos", sentence, [v for vs in conflict.values() for v in vs])
        if "arm_samepos" in ENABLED:
            return None
    for g in sorted(groups):
        if g[0] not in seen:
            seen.add(g[0]); uniq.append(g)
    groups = uniq
    if len(groups) < 2:
        return None
    groups.sort()
    low = sentence.lower()
    i_pos = min((low.find(t.lower()) for t in interv_terms if t.lower() in low), default=-1)
    c_pos = min((low.find(t.lower()) for t in comp_terms if t.lower() in low), default=-1)
    if i_pos < 0 or c_pos < 0:
        return None
    if len(groups) > 2:
        pv = _pair_values(groups)
        if len(pv) > 1:
            _hit("arm_pairs", sentence, pv)
            if "arm_pairs" in ENABLED:
                return None
    (p1, e1, n1), (p2, e2, n2) = groups[0], groups[1]
    if i_pos <= c_pos:
        return ArmCounts(e1, n1, e2, n2)
    return ArmCounts(e2, n2, e1, n1)


# --- extract_effect: site effect_first (_EFFECT.search takes the first effect+CI phrase of the sentence) ---
def extract_effect(sentence):
    ms = list(X._EFFECT.finditer(sentence))
    if not ms:
        return None
    first = X._effect_from_match(ms[0], sentence)
    if first is not None:
        vals = {e for e in (X._effect_from_match(m, sentence) for m in ms) if e is not None}
        if len(vals) > 1:
            _hit("effect_first", sentence, vals)
            if "effect_first" in ENABLED:
                return None
    return first


# --- effect_in_outcome: site eio_first (first effect whose clause names the outcome) ---
def effect_in_outcome(abstract, kws, window=260):
    abstract = X._norm(abstract)
    low = abstract.lower()
    kl = [k.lower() for k in kws]
    prev_end = 0
    found = []
    for m in X._EFFECT.finditer(abstract):
        clause = low[prev_end:m.start()][-window:]
        if any(k in clause for k in kl):
            e = X._effect_from_match(m, abstract[max(0, m.start() - 260):m.end() + 120])
            if e:
                found.append((e, abstract[prev_end:m.end()].strip()[-240:]))
        prev_end = m.end()
    if not found:
        return None
    vals = {e for e, _ in found}
    if len(vals) > 1:
        _hit("eio_first", abstract, vals)
        if "eio_first" in ENABLED:
            return None
    e, src = found[0]
    return {"effect": e[1], "ci_low": e[2], "ci_high": e[3], "scale": e[0], "source": src}


# --- _arm_ns: site arm_ns (first term x first pattern x first match wins, per arm) ---
def _arm_ns_patterns(tl):
    return (rf"{tl}[^.]{{0,12}}?\(\s*n\s*=\s*(\d+)\)",
            rf"(\d+)\s+(?:patients?|participants?|adults?|subjects?)[^.]{{0,25}}?(?:received|randomi[sz]ed to|assigned to|in the)[^.]{{0,15}}?{tl}",
            rf"(\d+)\s+(?:patients?\s+|participants?\s+|adults?\s+|subjects?\s+)?(?:were\s+|had\s+been\s+)?(?:received|assigned|allocated|randomi[sz]ed)(?:\s+to)?\s+(?:the\s+)?{tl}",
            rf"(\d+)\s+to\s+(?:the\s+)?{tl}",
            rf"(?:received|assigned to|randomi[sz]ed to)[^.]{{0,15}}?{tl}[^.]{{0,15}}?\(\s*(\d+)\)",
            rf"(\d+)\s+{tl}\b")


def _arm_ns(abstract, interv_terms, comp_terms):
    """Candidates for an arm = every match, for ANY of the arm's terms, of the highest-priority pattern that the
    harness's winning (term, pattern) used. Pattern priority is the harness's documented order and is kept; which
    term / which occurrence is the silent pick."""
    out = {}
    for key, terms in (("i", interv_terms), ("c", comp_terms)):
        best, win_pi = None, None
        for t in terms:
            tl = re.escape(t)
            for pi, pat in enumerate(_arm_ns_patterns(tl)):
                m = re.search(pat, abstract, re.I)
                if m:
                    best, win_pi = int(m.group(1)), pi; break
            if best:
                break
        if best:
            cands = {int(m.group(1)) for t in terms
                     for m in re.finditer(_arm_ns_patterns(re.escape(t))[win_pi], abstract, re.I) if int(m.group(1))}
            if len(cands) > 1:
                _hit("arm_ns", abstract, [(key, c) for c in cands])
                if "arm_ns" in ENABLED:
                    continue   # arm size ambiguous: omitted, exactly as when it is not stated
            out[key] = best
    return out


# --- extract_continuous / extract_rate: sites cont_pairs, rate_pairs (first two hits) ---
def extract_continuous(sentence, interv_terms, comp_terms, n_by_arm=None):
    vals = []
    for m in X._MEAN_SD.finditer(sentence):
        vals.append(MeanSDHit(m.start(), float(m.group(1)), float(m.group(2) or m.group(3))))
    for m in X._MED_IQR.finditer(sentence):
        sd = (float(m.group(3)) - float(m.group(2))) / 1.35
        if sd > 0:
            vals.append(MeanSDHit(m.start(), float(m.group(1)), sd))
    if len(vals) < 2 or not n_by_arm:
        return None
    n1, n2 = n_by_arm.get("i"), n_by_arm.get("c")
    if not (n1 and n2):
        return None
    low = sentence.lower()
    i_pos = min((low.find(t.lower()) for t in interv_terms if t.lower() in low), default=-1)
    c_pos = min((low.find(t.lower()) for t in comp_terms if t.lower() in low), default=-1)
    if i_pos < 0 or c_pos < 0:
        return None
    vals.sort()
    if len(vals) > 2:
        pv = _pair_values(vals)
        if len(pv) > 1:
            _hit("cont_pairs", sentence, pv)
            if "cont_pairs" in ENABLED:
                return None
    (_, m1, s1), (_, m2, s2) = vals[0], vals[1]
    return ContinuousArms(m1, s1, n1, m2, s2, n2) if i_pos <= c_pos else ContinuousArms(m2, s2, n2, m1, s1, n1)


def extract_rate(sentence, interv_terms, comp_terms):
    pairs = []
    for m in X._RATE_EVPT.finditer(sentence):
        ev = int(m.group(1).replace(",", ""))
        pt = float(m.group(2).replace(",", ""))
        if pt > 0 and ev >= 0:
            pairs.append(RateHit(m.start(), ev, pt))
    if len(pairs) < 2:
        return None
    low = sentence.lower()
    i_pos = min((low.find(t.lower()) for t in interv_terms if t.lower() in low), default=-1)
    c_pos = min((low.find(t.lower()) for t in comp_terms if t.lower() in low), default=-1)
    if i_pos < 0 or c_pos < 0:
        return None
    pairs.sort()
    if len(pairs) > 2:
        pv = _pair_values(pairs)
        if len(pv) > 1:
            _hit("rate_pairs", sentence, pv)
            if "rate_pairs" in ENABLED:
                return None
    (_, e1, t1), (_, e2, t2) = pairs[0], pairs[1]
    return RateArms(e1, t1, e2, t2) if i_pos <= c_pos else RateArms(e2, t2, e1, t1)


# --- _DENOM_EACH.search in extract_trial: site denom_each (first "N ... assigned to each") ---
class DenomEach:
    """Wraps the served (whole_numbers-wrapped) _DENOM_EACH: .search returns None when the abstract states >1 distinct
    per-arm size -- the existing 'no per-arm size stated' path."""

    def __init__(self, rx):
        self.rx = rx

    def search(self, s, *a):
        m = self.rx.search(s, *a)
        if m is not None:
            vals = {int(x.group(1)) for x in self.rx.finditer(s, *a)}
            if len(vals) > 1:
                _hit("denom_each", s, vals)
                if "denom_each" in ENABLED:
                    return None
        return m

    def __getattr__(self, a):
        return getattr(self.rx, a)


# --- _parse_k: site k_first ---
def _k_value(m):
    tok = m.group(1).lower()
    return int(tok) if tok.isdigit() else X._WORDNUM.get(tok)


def _parse_k(abstract):
    m = X._K.search(abstract)
    if m:
        first = _k_value(m)
        if first is not None:
            vals = {v for v in (_k_value(x) for x in X._K.finditer(abstract)) if v is not None}
            if len(vals) > 1:
                _hit("k_first", abstract, vals)
                if "k_first" in ENABLED:
                    return None
        return first
    return None


# --- extract_meta: site meta_primary (first effect in the first sentence pool that has one) ---
def extract_meta(abstract, outcome_kws):
    abstract = X._norm(abstract)
    eff = None
    for pool_sents in (X._outcome_sentences(abstract, outcome_kws), X._sentences(abstract)):
        found = [(e, s) for s in pool_sents for e in [X.extract_effect(s)] if e]
        if found:
            vals = {e for e, _ in found}
            if len(vals) > 1:
                _hit("meta_primary", abstract, vals)
                if "meta_primary" in ENABLED:
                    break
            e, s = found[0]
            eff = {"effect": e[1], "ci_low": e[2], "ci_high": e[3], "scale": e[0], "source": s.strip()[:220]}
            break
    return {"primary": eff, "k": X._parse_k(abstract)}


# --- extract_trial: sites sent_hr / sent_arm / sent_effect / sent_rate / sent_cont (first admissible sentence) ---
def _strip(d):
    return tuple(sorted((k, v) for k, v in d.items() if k != "source"))


def _stage(site, sents, per_sentence):
    """per_sentence(s) -> result dict or None. The harness returns the first non-None. Candidates are the distinct
    NON-REFUSAL results over every admissible sentence of the stage."""
    results = [r for r in (per_sentence(s) for s in sents) if r is not None]
    if not results:
        return None
    first = results[0]
    if first.get("absent"):
        return first
    vals = {_strip(r) for r in results if not r.get("absent")}
    if len(vals) > 1:
        _hit(site, " || ".join(r["source"] for r in results if not r.get("absent")), vals)
        if site in ENABLED:
            return {"absent": True, "reason": (
                f"ambiguous: {len(vals)} admissible sentences state different values for this outcome "
                f"({site.split('_', 1)[1]} stage); refused rather than take the first")}
    return first


def extract_trial(abstract, outcome_kws, interv_terms, comp_terms, declared_composite=True, estimand=None):
    abstract = X._norm(abstract)
    _skip_composite = not declared_composite
    dm = X._DENOM_EACH.search(abstract)
    cand = [int(x) for x in X._NEQ.findall(abstract)]
    if dm:
        cand.append(int(dm.group(1)))
    denom_each = sorted(set(cand)) or None
    arm_ns = X._arm_ns(abstract, interv_terms, comp_terms)
    factorial = X._is_factorial(abstract)
    if len(X._multi_dose_arms(abstract)) >= 2 and not X._intervention_dose_specified(interv_terms):
        return {"absent": True, "reason": (
            "multi-arm dose-ranging trial (>1 intervention dose arm vs one comparator): the effect "
            "cannot be attributed to a single pre-specified comparison; refused (multi-arm guard). "
            "Specify the dose in the topic's intervention terms to pin the arm.")}
    sents = X._outcome_sentences(abstract, X._effective_kws(abstract, outcome_kws))
    adm = [s for s in sents if not (X._is_subgroup_sentence(s) or (factorial and not X._interv_in(s, interv_terms))
                                    or (_skip_composite and X._names_composite(s))
                                    or X._kw_only_in_null_result(s, outcome_kws))]
    if estimand and "hazard" in str(estimand).lower().replace("hr", "hazard"):
        def hr(s):
            eff = X.extract_effect(s)
            if eff and eff[0] == "HR":
                return {"effect": eff[1], "ci_low": eff[2], "ci_high": eff[3], "scale": "HR",
                        "source": "abstract source-reported HR (registered estimand): " + s.strip()[:200]}
            return None
        r = _stage("sent_hr", adm, hr)
        if r is not None:
            return r

    def arm(s):
        arms = X.extract_arm_counts(s, interv_terms, comp_terms, denom_each, arm_ns)
        if not arms:
            return None
        rep = X.extract_effect(s)
        if not rep:
            d = X.effect_in_outcome(abstract, outcome_kws)
            if d:
                rep = (d["scale"], d["effect"], d.get("ci_low"), d.get("ci_high"))
        if rep and not X._roundtrip_ok(arms[0], arms[1], arms[2], arms[3], rep[0], rep[1]):
            return {"absent": True,
                    "reason": (f"round-trip mismatch: extracted counts {arms[0]}/{arms[1]} vs "
                               f"{arms[2]}/{arms[3]} imply "
                               f"{round(X._rr_from_counts(*arms) or 0, 3)} but the source reports "
                               f"{rep[0]} {rep[1]} — counts likely belong to a different outcome; refused")}
        return {"ai": arms[0], "n1i": arms[1], "ci": arms[2], "n2i": arms[3],
                "source": "abstract arm-level counts (percentage-corroborated): " + s.strip()[:200]}
    r = _stage("sent_arm", adm, arm)
    if r is not None:
        return r

    def eff(s):
        e = X.extract_effect(s)
        if e:
            return {"effect": e[1], "ci_low": e[2], "ci_high": e[3], "scale": e[0],
                    "source": f"abstract effect+CI ({e[0]}): " + s.strip()[:200]}
        return None
    r = _stage("sent_effect", adm, eff)
    if r is not None:
        return r

    def rate(s):
        rt = X.extract_rate(s, interv_terms, comp_terms)
        if rt:
            return {"e1i": rt[0], "t1i": rt[1], "e2i": rt[2], "t2i": rt[3], "measure": "IRR",
                    "source": "abstract events + person-time (incidence-rate ratio): " + s.strip()[:200]}
        return None
    r = _stage("sent_rate", adm, rate)
    if r is not None:
        return r
    ns = X._arm_ns(abstract, interv_terms, comp_terms)

    def cont(s):
        c = X.extract_continuous(s, interv_terms, comp_terms, ns)
        if c:
            return {"mean1": c[0], "sd1": c[1], "nc1": c[2], "mean2": c[3], "sd2": c[4], "nc2": c[5],
                    "measure": "MD", "source": "abstract mean+/-SD per arm (mean difference): " + s.strip()[:200]}
        return None
    r = _stage("sent_cont", adm, cont)
    if r is not None:
        return r
    if factorial:
        return {"absent": True, "reason": ("factorial-design trial: no extraction sentence explicitly "
                "names the intervention, so the effect cannot be attributed to our comparison "
                "rather than the co-randomised factor; refused (factorial guard)")}
    return {"absent": True, "reason": "no percentage-corroborated arm counts or effect+CI for this outcome found in the abstract"}


# --- composite_heterogeneity's _defn_window: site defn_window (first qualifying composite-definition clause) ---
def defn_windows(s):
    out = []
    for m in re.finditer(r"(composite (?:of|end ?point|outcome)|primary (?:composite )?(?:end ?point|outcome)"
                         r"[^.]{0,20}(?:was|comprised|consist|defined))", s):
        tail = s[m.end():m.end() + 220]
        seg = m.group(0) + re.split(r"[.;:]", tail)[0]
        if "death" in seg or "myocardial" in seg or "stroke" in seg:
            out.append(seg)
    return out


def composite_heterogeneity(outcome_name: str, trial_sources) -> str:
    """harness.extract.composite_heterogeneity with its _defn_window replaced: the harness takes the FIRST qualifying
    composite-definition clause of a source; when a source has several clauses whose component signatures differ, the
    source is refused (no window -> skipped, exactly as a source with no definition clause)."""
    name = (outcome_name or "").lower()
    if not any(w in name for w in ("mace", "major adverse cardiovascular", "major vascular",
                                   "cardiovascular events", "composite")):
        return ""
    _is_kidney = any(w in name for w in ("kidney", "renal", "ckd", "egfr", "nephro"))
    explicit_defs = []
    for src in trial_sources:
        if isinstance(src, dict) and src.get("endpoint_definition"):
            explicit_defs.append(str(src.get("endpoint_definition")))
    if explicit_defs and len(explicit_defs) == len(trial_sources):
        vals = sorted(set(explicit_defs))
        if len(vals) > 1:
            return ("pooled trials use each trial's OWN primary composite; component sets differ across trials"
                    + " (endpoint definitions: " + "; ".join(vals) + ")"
                    + " -- the pooled estimate mixes composite definitions (disclosed, not adjusted)")
        return ""
    if _is_kidney:
        comp_kws = [("50%", "50% eGFR-decline threshold"), ("40%", "40% eGFR-decline threshold"),
                    ("57%", "57% eGFR-decline threshold"), ("doubling", "creatinine-doubling"),
                    ("end-stage", "ESKD"), ("dialysis", "ESKD")]
    else:
        comp_kws = [("unstable angina", "unstable angina"), ("revascular", "revascularization"),
                    ("heart failure", "HF hospitalization"), ("transient ischemic", "TIA"),
                    ("hospital for cardiovascular", "CV hospitalization")]
    sigs = set()
    for src in trial_sources:
        if isinstance(src, dict):
            src = src.get("source", "")
        wins = defn_windows((src or "").lower())
        if not wins:
            continue
        wsigs = {tuple(sorted(label for kw, label in comp_kws if kw in w)) for w in wins}
        if len(wsigs) > 1:
            _hit("defn_window", src, wsigs)
            if "defn_window" in ENABLED:
                continue
        sigs.add(tuple(sorted(label for kw, label in comp_kws if kw in wins[0])))
    if len(sigs) > 1:
        allc = sorted({label for sig in sigs for label in sig})
        extra = f" (varying extra components across trials: {', '.join(allc)})" if allc else ""
        return ("pooled trials use each trial's OWN primary composite; component sets differ across trials"
                + extra + " — the pooled estimate mixes composite definitions (disclosed, not adjusted)")
    return ""


# Every site this module covers, mapped to the harness attribute(s) its replacement is installed on.
SITES = {
    "arm_pairs": ("extract_arm_counts",), "arm_den": ("extract_arm_counts",), "arm_samepos": ("extract_arm_counts",),
    "effect_first": ("extract_effect",), "eio_first": ("effect_in_outcome",), "arm_ns": ("_arm_ns",),
    "cont_pairs": ("extract_continuous",), "rate_pairs": ("extract_rate",), "denom_each": ("_DENOM_EACH",),
    "k_first": ("_parse_k",), "meta_primary": ("extract_meta",),
    "sent_hr": ("extract_trial",), "sent_arm": ("extract_trial",), "sent_effect": ("extract_trial",),
    "sent_rate": ("extract_trial",), "sent_cont": ("extract_trial",),
    "defn_window": ("composite_heterogeneity",),
}


def replacement(attr: str, served):
    return {"extract_arm_counts": extract_arm_counts, "extract_effect": extract_effect,
            "effect_in_outcome": effect_in_outcome, "_arm_ns": _arm_ns, "extract_continuous": extract_continuous,
            "extract_rate": extract_rate, "_DENOM_EACH": DenomEach(served), "_parse_k": _parse_k,
            "extract_meta": extract_meta, "extract_trial": extract_trial,
            "composite_heterogeneity": composite_heterogeneity}[attr]


def change(site: str):
    """Context manager: install the replacement for `site` with that one refusal ENABLED (nothing recorded)."""
    import contextlib

    @contextlib.contextmanager
    def _cm():
        attrs = SITES[site]
        old = {a: getattr(X, a) for a in attrs}
        en, rec = set(ENABLED), set(RECORD)
        try:
            for a in attrs:
                setattr(X, a, replacement(a, old[a]))
            ENABLED.clear(); ENABLED.add(site); RECORD.clear()
            yield
        finally:
            for a, v in old.items():
                setattr(X, a, v)
            ENABLED.clear(); ENABLED.update(en); RECORD.clear(); RECORD.update(rec)
    return _cm()
