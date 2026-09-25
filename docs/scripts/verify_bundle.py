#!/usr/bin/env python3
"""Independent verifier for a served evidence bundle. STANDARD LIBRARY ONLY -- imports nothing from this repository.

Given only the served tree (a directory that mirrors the site root, or the site URL) and a review slug, it:

  1. fetches reviews/<slug>/BUNDLE.json and re-derives, from served bytes alone,
     - every artefact and supporting-file digest (sha256 of bytes; canonical-JSON digests; git blob ids of code),
     - CERTIFICATE.json's release_sha256 and review.json's review_sha256,
     - every admission predicate of every primary-pool row (P1..P7) -- NOT read from the bundle but recomputed from
       records.json, review.json and the normalization manifest, then compared with what the bundle recorded,
     - every preservation record (cached abstract vs the retained EFetch XML, unit by unit) and hence the
       coverage_status behind every absence claim, applying the asymmetric rule itself,
     - the pooled estimate: log-scale inverse-variance random effects, Paule-Mandel tau^2, HKSJ on t_{k-1} with the
       Q/(k-1) floor -- Student-t quantile by regularized incomplete beta, no scipy -- compared to 1e-9;
  2. with --corrupt <pmid> <limb>, mutates ONE limb of ONE row in memory (span | effect | components | eligibility |
     conflict | binding | container) and reports which rows changed admissibility, so "an executable gate refuses when the
     evidence is damaged" is demonstrated rather than asserted;
  3. for EVERY document with a retained acquisition, recomputes the preservation record (cached abstract vs the
     retained EFetch XML, unit by unit) and FAILS if the bundle's coverage_status disagrees -- a self-consistent
     package that deleted a sentence and recomputed every digest is caught here, provided the XML was not altered too;
  4. with --anchor live, re-fetches EFetch XML from PubMed NOW for every pooled record and compares its abstract units
     to BOTH the retained XML and the cached abstract. That is the external observation nothing inside the package can
     substitute for; a difference is reported as a discrepancy (with DateRevised), not attributed.

What a PASS here establishes: identity (bytes hash as declared, under the canonicalisation the bundle publishes:
Python json.dumps sort_keys / compact separators / ensure_ascii=False, NOT RFC 8785), selection (every #PMID selector
resolves to exactly one record -- zero or two matches refuse), location (spans sit at the stated code-point offsets in
the stated representation of THAT record), arithmetic (the pool follows from the rows), and the asymmetric rule.

What it does NOT check, stated in the same breath:
  * that any acquired or cached representation faithfully preserves the upstream publication. SOUL's cache is known to
    omit the HbA1c entry range, the follow-up figures and the safety sentence; the preservation record detects that
    against a POST-HOC acquisition, and a saved response plus its hash establish what was saved, not that it came from
    the claimed publisher;
  * that the source set is complete, or that the clinical interpretation is right (four_questions carry those states);
  * whether a CI-to-SE conversion was appropriate for a source whose interval was not a Wald interval (statistical_input
    records the construction; SOUL's is group-sequential-adjusted; the pool is reproduced, its appropriateness is not);
  * the PRODUCTION admission path. No production falsification test has been executed by anyone. This verifier checks
    the bundle, not the producer's gate. A green run here is not evidence that the producer refuses damaged evidence.

Usage:
  python scripts/verify_bundle.py --root docs --slug glp1-ra-mace-t2d
  python scripts/verify_bundle.py --url https://mahmood726-cyber.github.io/meta-harness/ --slug glp1-ra-mace-t2d
  python scripts/verify_bundle.py --root docs --slug glp1-ra-mace-t2d --corrupt 40162642 span
  python scripts/verify_bundle.py --root docs --slug glp1-ra-mace-t2d --corrupt 27295427 contrast_reverse   (ordered-contrast limbs: LEADER)
  add --json for machine-readable output
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

Z975 = 1.959963984540054
_WS = re.compile(r"\s+")
_UNICODE_MAP = str.maketrans({
    "·": ".", "–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-",
    " ": " ", " ": " ", " ": " ", "‘": "'", "’": "'", "“": '"', "”": '"',
    "≤": "<=", "≥": ">=",
})


# ---------------------------------------------------------------- primitives

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_text(s: str) -> str:
    return sha256(s.encode("utf-8"))


def git_blob(b: bytes, lf: bool = False) -> str:
    if lf:
        b = b.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


def normalize(s: str) -> str:
    return _WS.sub(" ", s).strip().translate(_UNICODE_MAP)


class Store:
    """Bytes by served path, from a directory or a URL; every fetch is remembered so a corruption is applied once."""

    def __init__(self, root: str | None, url: str | None):
        self.root, self.url, self.cache = root, url, {}

    def get(self, path: str) -> bytes:
        if path in self.cache:
            return self.cache[path]
        if self.root:
            try:
                data = (Path(self.root) / path).read_bytes()
            except FileNotFoundError:
                raise Refusal("ARTEFACT_UNREACHABLE", f"{path} is not present in the served tree")
        else:
            req = urllib.request.Request(self.url.rstrip("/") + "/" + path, headers={"Cache-Control": "no-cache", "User-Agent": "verify_bundle/1"})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    data = r.read()
            except urllib.error.HTTPError as e:
                raise Refusal("ARTEFACT_UNREACHABLE", f"{path}: HTTP {e.code}")
            except Exception as e:  # noqa: BLE001
                raise Refusal("ARTEFACT_UNREACHABLE", f"{path}: {str(e)[:120]}")
        self.cache[path] = data
        return data

    def json(self, path: str):
        return json.loads(self.get(path).decode("utf-8"))


# ---------------------------------------------------------------- statistics (stdlib)

def _betacf(a, b, x):
    MAXIT, EPS, FPMIN = 300, 3e-16, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
        c = 1.0 + aa / c
        c = c if abs(c) > FPMIN else FPMIN
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
        c = 1.0 + aa / c
        c = c if abs(c) > FPMIN else FPMIN
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1 - x) / b


def t_cdf(t, df):
    x = df / (df + t * t)
    p = 0.5 * betainc(df / 2.0, 0.5, x)
    return 1 - p if t > 0 else p


def t_ppf(p, df):
    lo, hi = 0.0, 1.0
    while t_cdf(hi, df) < p:
        hi *= 2
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-14:
            break
    return 0.5 * (lo + hi)


def _wmean(yi, vi, tau2):
    w = [1.0 / (v + tau2) for v in vi]
    sw = sum(w)
    return sum(wi * y for wi, y in zip(w, yi)) / sw, w, sw


def paule_mandel(yi, vi, tol=1e-10, max_iter=200):
    k = len(yi)
    if k < 2:
        return 0.0

    def F(tau2):
        mu, w, _ = _wmean(yi, vi, tau2)
        return sum(wi * (y - mu) ** 2 for wi, y in zip(w, yi)) - (k - 1)

    if F(0.0) <= 0:
        return 0.0
    lo, hi = 0.0, 1.0
    while F(hi) > 0 and hi < 1e6:
        hi *= 2.0
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        fm = F(mid)
        if abs(fm) < tol:
            return mid
        if fm > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def pool(rows):
    yi = [math.log(r["effect"]) for r in rows]
    vi = [((math.log(r["ci_high"]) - math.log(r["ci_low"])) / (2 * Z975)) ** 2 for r in rows]
    k = len(yi)
    tau2 = paule_mandel(yi, vi)
    mu, w, sw = _wmean(yi, vi, tau2)
    se_re = math.sqrt(1.0 / sw)
    Q_gen = sum(wi * (y - mu) ** 2 for wi, y in zip(w, yi))
    se = se_re * math.sqrt(max(1.0, Q_gen / (k - 1))) if k > 1 else se_re
    tcrit = t_ppf(0.975, k - 1) if k > 1 else Z975
    mu0, w0, _ = _wmean(yi, vi, 0.0)
    Q = sum(wi * (y - mu0) ** 2 for wi, y in zip(w0, yi))
    return {"k": k, "tau2": tau2, "mu_log": mu, "se_log": se, "estimate": math.exp(mu),
            "ci_low": math.exp(mu - tcrit * se), "ci_high": math.exp(mu + tcrit * se), "Q": Q, "t_crit": tcrit}


# ---------------------------------------------------------------- checks

# ---- endpoint binding (P9): a POSITIVE requirement read from the tuple's own clause --------------------------------
TARGET_PHRASES = ("major adverse cardiovascular", "mace")
PRIMARY_NAMES = ("primary outcome", "primary composite outcome", "primary-outcome", "primary end point", "primary endpoint",
                 "primary composite end point", "primary cardiovascular end-point", "primary cardiovascular end point",
                 "primary cardiovascular endpoint", "primary cardiovascular outcome")
DEFINITION_CUES = ("composite", "first occurrence", "defined as", "consisting of", "consisted of", "major adverse", "mace",
                   "primary outcome", "primary end point", "primary endpoint", "primary composite", "primary cardiovascular")
COMPONENT_WORDS = {"CARDIOVASCULAR_DEATH": ("cardiovascular death", "death from cardiovascular", "cardiovascular causes", "cardiovascular mortality"),
                   "MYOCARDIAL_INFARCTION": ("myocardial infarction",), "STROKE": ("stroke",)}
NON_TARGET_MENTIONS = ("death from any cause", "all-cause mortality", "all-cause death", "any-cause death", "hospitalization for heart failure",
                       "hospitalisation for heart failure", "heart failure", "kidney", "renal", "nephropathy", "retinopathy", "amputation",
                       "pancreatitis", "adverse event", "serious adverse", "gastrointestinal", "hypoglyc", "unstable angina")
_NUM = re.compile(r"\d+(?:\.\d+)?")


_STAT_CONTINUATION = re.compile(r"\s*(?:95\s*%|CI\b|P\s*[=<>]|p\s*[=<>]|HR\b|hazard ratio)")   # a ';' inside a statistical tuple does not end a clause


def clauses(span):
    """Clause boundaries: sentence ends (period + space + capital) AND semicolons OUTSIDE brackets."""
    out, buf, depth = [], [], 0
    text = span or ""
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        buf.append(ch)
        if depth == 0 and ch == ";" and not _STAT_CONTINUATION.match(text, i + 1):
            out.append("".join(buf).strip()); buf = []
        elif depth == 0 and ch == "." and i + 2 < len(text) and text[i + 1] == " " and text[i + 2].isupper():
            out.append("".join(buf).strip()); buf = []
        i += 1
    if "".join(buf).strip():
        out.append("".join(buf).strip())
    return [c for c in out if c]


def clause_numbers(clause):
    return [float(x) for x in _NUM.findall(normalize(clause))]


def clause_with_effect(span, values):
    """The clause whose own numbers contain every value of the tuple -- by NUMERIC equality, never substring."""
    vals = [float(v) for v in values]
    for c in clauses(span):
        nums = clause_numbers(c)
        if all(any(abs(v - n) < 1e-12 for n in nums) for v in vals):
            return c
    return None


_EXCLUSION = re.compile(r"\b(excluding|except(?:ing)?|exclusive of|but not|other than|not including|without)\b\s*", re.I)
_EXCLUSION_STOP = re.compile(r",\s*(?:and|which|that|the|was|were|occurred|did|with|namely|i\.e\.|that is|specifically)\b|;|\(")
_DEFINES = re.compile(r"(primary (?:composite )?(?:outcome|end ?point)|primary cardiovascular (?:composite )?(?:outcome|end-?point)|composite (?:outcome|end ?point))"
                      r"\s+(?:was|were|is|are|consisted of|consists of|defined as|comprised|comprising|included|includes)\b", re.I)
# exclusion STATEMENTS anywhere in the span (next sentence, footnote), scoped to the analysis/outcome -- not to the population
_POPULATION = re.compile(r"\b(patients?|participants?|subjects?|individuals?|persons?|people|those|women|men|adults?|children|"
                         r"enrol+ment|enrol+ed|randomi[sz](?:ed|ation)|eligib\w*|screen\w*|the (?:trial|study|cohort|population))\b", re.I)
_ANALYSIS_EXCL = re.compile(
    r"(?P<subj>(?:^|(?<=[.;*]))\s*[^.;]{3,160}?)\s+(?:was|were)\s+"
    r"(?:not\s+(?:included|counted|considered|analy[sz]ed|part\s+of)|excluded\s+from|omitted\s+from|left\s+out\s+of|removed\s+from|censored\s+from)"
    r"(?:\s+(?:in|as\s+part\s+of|toward|towards|to))?\s+"
    r"(?P<scope>(?:the|this|its|our)?\s*(?:primary|composite|main|prespecified|pre-specified)?\s*(?:analysis|analyses|outcome|end ?point|composite|definition|event count|events?)\b[^.;]*)", re.I)
_NEITHER = re.compile(r"neither\s+(?P<a>[^.;]{3,80}?)\s+nor\s+(?P<b>[^.;]{3,80}?)\s+(?:contributed|counted|was\s+(?:included|counted)|were\s+(?:included|counted)|"
                      r"was\s+part|were\s+part|formed\s+part)", re.I)
_NOT_CONTRIB = re.compile(r"(?P<subj>(?:^|(?<=[.;*]))\s*[^.;]{3,160}?)\s+did\s+not\s+(?:contribute|count)\b", re.I)
# a statement framed by ANOTHER outcome ('for the secondary renal outcome, stroke was not included in the composite') is not about the target
_OTHER_OUTCOME_FRAME = re.compile(r"\b(?:secondary|key secondary|tertiary|exploratory|safety|sensitivity)\b[^.;]{0,60}?\b(?:outcome|end ?point|analysis|composite)\b", re.I)


def named_components(text):
    return sorted(k for k, ws in COMPONENT_WORDS.items() if any(w in text for w in ws))


def split_exclusions(text):
    """Relational, not a blacklist: every segment governed by an exclusion cue is cut out BEFORE membership is read. Returns
    (included_text, excluded_text). 'cardiovascular death only, excluding nonfatal MI and nonfatal stroke' -> included names
    one component, excluded names two; '3-point MACE excluding unstable angina' -> included keeps the target phrase. A cue INSIDE
    a parenthetical is scoped to the parenthetical, and when it qualifies the component it follows ('nonfatal myocardial
    infarction (excluding silent infarction)') it excludes nothing -- a qualifier on a component is not an exclusion of one."""
    included, excluded, rest = "", "", text
    while True:
        m = _EXCLUSION.search(rest)
        if not m:
            return included + rest, excluded.strip()
        head = rest[:m.start()]
        if head.rstrip().endswith("("):
            close = rest.find(")", m.end())
            scope = rest[m.end():close] if close >= 0 else rest[m.end():]
            governing = named_components(head.rstrip()[:-1][-60:])
            if not set(named_components(scope)) <= set(governing):          # names a component the head does not: a real exclusion
                excluded += " " + scope
            included += head.rstrip()[:-1] + " "
            rest = rest[close + 1:] if close >= 0 else ""
            continue
        stop = _EXCLUSION_STOP.search(rest, m.end())
        excluded += " " + (rest[m.end():stop.start()] if stop else rest[m.end():])
        included += head + " "
        rest = rest[stop.start():] if stop else ""


def analysis_exclusions(text):
    """Exclusion STATEMENTS anywhere in a span -- 'X and Y were not included in the primary analysis', '*X and Y were excluded
    from the primary analysis', 'neither X nor Y contributed', 'X did not contribute' -- returned as the excluded subject text.
    A statement whose subject or scope is the POPULATION ('patients with a prior stroke were excluded from enrolment') is not an
    outcome exclusion and is left alone. Returns (excluded_text, [statements])."""
    out, stmts = [], []
    def other_frame(whole):
        return bool(_OTHER_OUTCOME_FRAME.search(whole)) and "primary" not in whole.lower()
    for m in _ANALYSIS_EXCL.finditer(text):
        if _POPULATION.search(m.group("subj")) or _POPULATION.search(m.group("scope")) or other_frame(m.group(0)):
            continue
        out.append(m.group("subj")); stmts.append(m.group(0).strip())
    for m in _NEITHER.finditer(text):
        if _POPULATION.search(m.group("a")) or _POPULATION.search(m.group("b")) or other_frame(m.group(0)):
            continue
        out.append(m.group("a") + " " + m.group("b")); stmts.append(m.group(0).strip())
    for m in _NOT_CONTRIB.finditer(text):
        if _POPULATION.search(m.group("subj")) or other_frame(m.group(0)):
            continue
        out.append(m.group("subj")); stmts.append(m.group(0).strip())
    return " ; ".join(out), stmts


def span_target_mention(span, values, definition_span, canonical_components, context=None):
    """POSITIVE binding. The tuple's own clause must carry a TARGET mention: a target phrase, a target DEFINITION (>= 2 canonical
    components AND a definitional cue -- co-occurrence of component words is not ownership), or a primary-outcome name that the
    row's definition span binds to the target. Exclusion scopes ('excluding X') are removed before membership is read, exclusion
    STATEMENTS anywhere in the span or the row's definition ('X was not included in the primary analysis', a footnote after the
    result, 'neither X nor Y contributed') cut the same components, and the excluded components are reported -- mentioning what
    is excluded must never make it included. A qualifier inside a component and a POPULATION exclusion cut nothing. A clause that
    itself DEFINES the primary outcome as something other than the target is not rescued by the row's definition span. `context`
    (the document neighbourhood of the located span, see document_neighbourhood) is searched for exclusion STATEMENTS too, so a
    footnote outside both of the row's spans still cuts. A clause
    that ALSO carries a non-target mention (or a lone component) is AMBIGUOUS_ENDPOINT_BINDING, never a pass; only a non-target
    mention is ENDPOINT_INCOMPATIBLE; no recognised mention is AMBIGUOUS_ENDPOINT_BINDING. Never a fallback to the definition span."""
    clause = clause_with_effect(span, values)
    if clause is None:
        return {"state": "AMBIGUOUS_ENDPOINT_BINDING", "mention": "no clause of the span carries the tuple's numbers by numeric equality",
                "witness": span, "clause": None}
    s_all, c_all, d_all = normalize(span).lower(), normalize(clause).lower(), normalize(definition_span or "").lower()
    c, c_exc = split_exclusions(c_all)
    d, d_exc = split_exclusions(d_all)
    s_exc, s_stmts = analysis_exclusions(s_all)
    d_stmt_exc, d_stmts = analysis_exclusions(d_all)
    x_exc, x_stmts = analysis_exclusions(normalize(context).lower()) if context else ("", [])
    x_stmts = [x for x in x_stmts if x not in s_stmts and x not in d_stmts]
    named = named_components
    comps_c, comps_d = named(c), named(d)
    excluded_c, excluded_d, excluded_s, excluded_x = named(c_exc), named(d_exc + " ; " + d_stmt_exc), named(s_exc), named(x_exc)
    canon = set(canonical_components or [])
    primary_named = any(n in c for n in PRIMARY_NAMES)
    cue = any(k in c for k in DEFINITION_CUES)
    clause_defines = bool(_DEFINES.search(c))
    target = []
    if any(ph in c for ph in TARGET_PHRASES):
        target.append({"kind": "target phrase", "witness": [ph for ph in TARGET_PHRASES if ph in c]})
    if len(set(comps_c) & canon) >= 2 and cue and not (set(excluded_c) & canon):
        target.append({"kind": "target definition in clause", "witness": comps_c})
    # the row's definition span binds a primary-outcome NAME to the target -- unless the clause itself defines the primary differently,
    # or the definition span excludes a target component
    if (primary_named and "primary" in d and len(set(comps_d) & canon) >= 2 and not (set(excluded_d) & canon)
            and not (clause_defines and len(set(comps_c) & canon) < 2 and not any(ph in c for ph in TARGET_PHRASES))):
        target.append({"kind": "primary-outcome name bound by the row's definition span", "witness": [n for n in PRIMARY_NAMES if n in c]})
    non_target = [m for m in NON_TARGET_MENTIONS if m in c]
    lone_component = (len(comps_c) == 1 and not target)
    excluded_all = sorted(set(excluded_c) | set(excluded_d) | set(excluded_s) | set(excluded_x))
    excluded_target = sorted(set(excluded_all) & canon)
    where = [w for w, xs in (("clause", excluded_c), ("definition", excluded_d), ("span statement", excluded_s), ("document neighbourhood", excluded_x)) if set(xs) & canon]
    base = {"clause": clause, "excluded_components": excluded_all or None, "exclusion_statements": (s_stmts + d_stmts + x_stmts) or None,
            "exclusion_scope_searched": ["clause", "row span", "row definition span"] + (["document neighbourhood (+/-400 code points around the located span)"] if context else [])}
    if excluded_target and not any(ph in c for ph in TARGET_PHRASES):
        return {"state": "ENDPOINT_INCOMPATIBLE", "mention": f"the {' / '.join(where)} EXCLUDES a target component; mentioning what is excluded does not include it",
                "witness": {"included": comps_c, "excluded": excluded_target}, **base}
    if target and (non_target or lone_component):
        return {"state": "AMBIGUOUS_ENDPOINT_BINDING", "mention": "clause carries BOTH a target mention and a non-target mention",
                "witness": {"target": target, "non_target": non_target or comps_c}, **base}
    if target:
        return {"state": "PASS", "mention": target[0]["kind"], "witness": target[0]["witness"], **base}
    if non_target or lone_component:
        return {"state": "ENDPOINT_INCOMPATIBLE", "mention": "recognised NON-target mention bound to the target claim" if non_target else
                "the clause defines or names a single component, not the composite", "witness": non_target or comps_c, **base}
    return {"state": "AMBIGUOUS_ENDPOINT_BINDING", "mention": "no recognised target mention in the tuple's own clause", "witness": clause, **base}

def locate_all(span, hay):
    """Zero / one / many are three states. Returns match kind, occurrence count and the first offset."""
    if not span:
        return {"match": "NO_SPAN", "occurrences": 0}
    n = hay.count(span)
    if n:
        i = hay.find(span)
        return {"match": "VERBATIM", "parent": "PARSED_SOURCE", "start": i, "end": i + len(span), "occurrences": n}
    s, h = normalize(span), normalize(hay)
    n = h.count(s)
    if n:
        i = h.find(s)
        return {"match": "NORMALISED", "parent": "NORMALIZED_SOURCE", "start": i, "end": i + len(s), "occurrences": n}
    return {"match": "NOT_LOCATED", "occurrences": 0}


def document_neighbourhood(span, hay, radius=400):
    """The document text around the located span: `radius` code points before its start and after its end, in the representation
    where it was located. This is where an exclusion statement lives when it is not inside the row's own spans (a footnote after
    the result, the sentence before it). None when the span is not located."""
    loc = locate_all(span, hay)
    if loc["match"] not in ("VERBATIM", "NORMALISED"):
        return None
    text = hay if loc["parent"] == "PARSED_SOURCE" else normalize(hay)
    return text[max(0, loc["start"] - radius):loc["end"] + radius]


# ---- pooled state and component-set consistency (pcsk9-mace, 2026-09-20: a NEAR_MATCH with extra ['unstable angina'] and missing []
#      pooled beside an EXACT_TARGET and an UNBOUND row; the producer renders the three alike) ----------------------------------
def _aslist(v):
    if isinstance(v, list):
        return [str(x) for x in v]
    if isinstance(v, str) and v.startswith("["):
        try:
            return [str(x) for x in json.loads(v.replace("'", '"'))]
        except Exception:
            return [v]
    return []


def pooled_state(t):
    """EXACT_TARGET_POOLED / NEAR_MATCH_POOLED / UNBOUND_POOLED (no class: admitted through the UNBOUND_LEGACY fail-open) / OTHER."""
    cls, adm, b = t.get("target_endpoint_class"), t.get("endpoint_admissibility") or "", t.get("endpoint_binding")
    if cls == "EXACT_TARGET":
        return "EXACT_TARGET_POOLED"
    if cls == "NEAR_MATCH" or adm.startswith("NEAR_MATCH"):
        return "NEAR_MATCH_POOLED"
    if b == "unbound_legacy" or adm == "UNBOUND_LEGACY" or not cls:
        return "UNBOUND_POOLED"
    return f"OTHER:{cls}"


def component_set_checks(t, row_canonical, target_canonical):
    """P13: no EXTRA component in a pooled row. P14: missing_components must name every target component the row lacks (a row that
    lacks 'cardiovascular death' with missing [] is the withdrawn-review defect). Surplus with extra [] is reported (C3), not a
    predicate: against a lexicon-collapsed target it names the target's defect, not the row's."""
    extra, missing = _aslist(t.get("target_endpoint_extra_components")), _aslist(t.get("target_endpoint_missing_components"))
    row, target = set(row_canonical or []), set(target_canonical or [])
    lacks = sorted(target - row) if row and target else []
    surplus = sorted(row - target) if row and target else []
    return {"pooled_state": pooled_state(t), "row_components_canonical": sorted(row), "target_components_canonical": sorted(target),
            "extra_components": extra, "missing_components": missing, "row_lacks": lacks, "row_surplus": surplus,
            "P13_no_extra_components": not extra,
            "P14_missing_components_consistent": not (lacks and not missing),
            "C3_surplus_with_empty_extra": bool(surplus) and not extra}


# ---- estimand evidence: analysis set / window / contrast / estimator WITH a span, or an explicit default ----------
_ESTIMAND = {
    "analysis_set": [(r"intention[- ]to[- ]treat|\bITT\b", "intention-to-treat"), (r"per[- ]protocol", "per-protocol"),
                     (r"as[- ]treated", "as-treated"), (r"on[- ]treatment (?:population|analysis)", "on-treatment population")],
    "analysis_window": [(r"on[- ]treatment", "on-treatment"), (r"on[- ]study|in[- ]trial", "on-study"),
                        (r"time[- ]to[- ](?:first[- ])?event|time to (?:the )?first (?:occurrence|event)", "time-to-first-event (treatment-policy)"),
                        (r"median follow-up (?:of|was) [\d.]+ (?:years|months)|(?:over|during) a median (?:follow-up )?of [\d.]+ (?:years|months)", "follow-up stated")],
    "estimator": [(r"hazard ratio", "hazard ratio"), (r"(?-i:\bHR\b)", "hazard ratio"), (r"odds ratio", "odds ratio"), (r"(?-i:\bOR\b)", "odds ratio"),
                  (r"relative risk|risk ratio", "risk ratio"), (r"(?-i:\bRR\b)", "risk ratio"), (r"rate ratio|incidence rate ratio", "rate ratio")],
}
DEFAULT_REGISTERED = {"analysis_set": "intention-to-treat (registered primary-analysis default)",
                      "analysis_window": "on-study, treatment-policy (registered primary-analysis default)",
                      "contrast": "intervention vs placebo; effect < 1 favours intervention (topic registration)",
                      "estimator": "UNSTATED"}


def _sentence_at(text, pos):
    s = text.rfind(". ", 0, pos) + 1
    e = text.find(". ", pos)
    e = len(text) if e < 0 else e + 1
    return s, e


def estimand_evidence(parsed, result_clause):
    """Per field: STATED (value + located sentence with code-point offsets in PARSED_SOURCE), DEFAULT_REGISTERED (no statement in the
    held representation), or ESTIMAND_UNBOUND (the same source states >= 2 differing values for the field)."""
    out = {}
    for field, pats in _ESTIMAND.items():
        hits = []
        for rx, value in pats:
            for m in re.finditer(rx, parsed, re.I):
                s, e = _sentence_at(parsed, m.start())
                hits.append({"value": value, "matched": m.group(0), "start": s, "end": e, "span": parsed[s:e].strip()})
        values = {h["value"] for h in hits}
        if field == "analysis_window":
            strategies = {v for v in values if v in ("on-treatment", "on-study")}
            if len(strategies) >= 2:
                out[field] = {"state": "UNRESOLVED", "values": sorted(values), "evidence": hits[:4],
                              "rule": "the same source states two strategies for the analysis; the field cannot default"}
                continue
            if "on-treatment" in values and "on-study" not in values:
                pick = next(h for h in hits if h["value"] == "on-treatment")
                out[field] = {"state": "STATED_IN_OWNING_EVIDENCE", "value": "on-treatment", **{k: pick[k] for k in ("start", "end", "span")}, "parent_representation": "PARSED_SOURCE"}
                continue
            prefer = [h for h in hits if h["value"] == "on-study"] or [h for h in hits if h["value"].startswith("time-to")] or [h for h in hits if h["value"] == "follow-up stated"]
            if prefer:
                pick = prefer[0]
                out[field] = {"state": "STATED_IN_OWNING_EVIDENCE", "value": pick["value"], **{k: pick[k] for k in ("start", "end", "span")}, "parent_representation": "PARSED_SOURCE",
                              "also_stated": sorted(values - {pick["value"]})}
            else:
                out[field] = {"state": "REGISTERED_DEFAULT", "value": DEFAULT_REGISTERED[field]}
            continue
        if len(values) >= 2:
            out[field] = {"state": "UNRESOLVED", "values": sorted(values), "evidence": hits[:4]}
        elif hits:
            pick = hits[0]
            out[field] = {"state": "STATED_IN_OWNING_EVIDENCE", "value": pick["value"], **{k: pick[k] for k in ("start", "end", "span")}, "parent_representation": "PARSED_SOURCE"}
        else:
            out[field] = {"state": "REGISTERED_DEFAULT", "value": DEFAULT_REGISTERED[field]}
    rc = result_clause or ""
    if "placebo" in rc.lower():
        i = parsed.find(rc)
        if i >= 0:
            out["contrast"] = {"state": "STATED_IN_OWNING_EVIDENCE", "value": "vs placebo (named in the result clause)", "span": rc,
                               "start": i, "end": i + len(rc), "parent_representation": "PARSED_SOURCE"}
        else:   # the clause exists only after normalisation (e.g. Lancet middle dots): offsets in NORMALIZED_SOURCE coordinates
            nrc, npar = normalize(rc), normalize(parsed)
            j = npar.find(nrc)
            out["contrast"] = {"state": "STATED_IN_OWNING_EVIDENCE", "value": "vs placebo (named in the result clause)", "span": nrc,
                               "start": j if j >= 0 else None, "end": (j + len(nrc)) if j >= 0 else None, "parent_representation": "NORMALIZED_SOURCE"}
    else:
        out["contrast"] = {"state": "REGISTERED_DEFAULT", "value": DEFAULT_REGISTERED["contrast"]}
    return out


# ---- ordered contrast: WHICH arm is the numerator is a VALUE, recomputed from the tuple's own clause ----------------
# (lane OC, 2026-09-25, external audit: "ordered contrast and estimator must be value-checked, not state-checked").
# 'placebo' appearing in a clause is a STATE; it says nothing about whether 0.87 is liraglutide/placebo or placebo/liraglutide,
# and a ratio read the wrong way round is a different clinical claim with every digit still present in the source. The value is
#   {measure, experimental_arm, reference_arm, numerator_side, estimate, ci_low, ci_high, direction_witness}
# P10 compares the served contrast and estimator VALUES with it; P11 compares it with the registered contrast and estimator; a
# reversal is admissible only as a DECLARED reciprocal normalisation (A/B = 1/(B/A); the CI's endpoints swap) under a policy that
# permits it -- absent a policy, refused (fail closed).
RATIO_MEASURES = ("HR", "OR", "RR", "IRR")
_CLAUSE_MEASURE = (("HR", r"hazard ratio|(?-i:\bHR\b)"), ("OR", r"odds ratio|(?-i:\bOR\b)"),
                   ("RR", r"relative risk|risk ratio|(?-i:\bRR\b)"), ("IRR", r"(?:incidence[- ])?rate ratio|(?-i:\bIRR\b)"))
_ESTIMATOR_MEASURE = {"hazard ratio": "HR", "odds ratio": "OR", "risk ratio": "RR", "rate ratio": "IRR"}
_SCALE_ALIASES = {"HR": "HR", "OR": "OR", "RR": "RR", "IRR": "IRR", "RATE RATIO": "IRR", "RISK RATIO": "RR", "HAZARD RATIO": "HR", "ODDS RATIO": "OR"}
# the object of a comparison is the REFERENCE arm: "... than in the placebo group", "compared with placebo", "A versus B"
_REFERENCE_MARK = re.compile(r"\b(?:as\s+)?(?:compared\s+(?:with|to)|versus|vs\.?|relative\s+to|than|(?:non-?)?inferior\s+to|superior\s+to)\s+"
                             r"(?:(?:in|on|with|among|receiving|assigned\s+to(?:\s+receive)?|those|patients|participants|the)\s+){0,4}$", re.I)
# ... and a ratio 'for' an arm names that arm as the NUMERATOR: "hazard ratio for liraglutide, 0.87", "the hazard ratio for placebo versus ..."
_NUMERATOR_MARK = re.compile(r"\b(?:hazard|odds|risk|rate)\s+ratios?\s*(?:\([A-Z]{2,3}\)\s*|\[[A-Z]{2,3}\]\s*)?,?\s*(?:for|with|of)\s+"
                             r"(?:(?:the|patients|participants|those|in|receiving|assigned\s+to(?:\s+receive)?)\s+){0,4}$", re.I)
_PCT = re.compile(r"(\d+(?:\.\d+)?)\s*%")
_NOT_AN_ARM = re.compile(r"^-(?:controlled|matched|treated|based|like)", re.I)
_GENERIC_REFERENCE = ("control",)          # names an arm only as '<control> group|arm'; 'glycaemic control' is not an arm


def scale_measure(scale):
    """The measure a served label names (HR / OR / RR / IRR), None when unidentified. No class mapping: OR is not RR."""
    return _SCALE_ALIASES.get(str(scale or "").strip().upper())


def clause_measure(clause):
    """The ratio measure the tuple's OWN clause names: STATED (exactly one), UNRESOLVED (two differ), UNSTATED (none)."""
    found = {}
    for m, rx in _CLAUSE_MEASURE:
        hit = re.search(rx, clause or "", re.I)
        if hit:
            found[m] = hit.group(0)
    if len(found) == 1:
        (m, word), = found.items()
        return {"state": "STATED", "measure": m, "matched": word}
    return {"state": "UNRESOLVED" if found else "UNSTATED", "measure": None, "matched": sorted(found.values())}


def contrast_vocabulary(topic):
    """Arm vocabulary from the SERVED topic registration (digest-checked artefact): experimental = the intervention agents, their
    aliases and the class terms; reference = the comparator terms. Longest first so 'oral semaglutide' never loses to a fragment."""
    exp = set(topic.get("intervention_class_terms") or []) | set(topic.get("intervention_terms") or [])
    for k, v in (topic.get("intervention_agents") or {}).items():
        exp.add(k)
        exp.update(v or [])
    ref = set(topic.get("comparator_terms") or [])
    key = lambda s: (-len(s), s)
    return {"experimental": sorted({t.strip().lower() for t in exp if t and t.strip()}, key=key),
            "reference": sorted({t.strip().lower() for t in ref if t and t.strip()}, key=key)}


def side_of(text, vocab):
    """EXPERIMENTAL / REFERENCE / None for a free-text arm name. A name carrying a reference term is the reference ('placebo for X')."""
    low = (text or "").lower()
    if any(re.search(r"(?<![\w])" + re.escape(t) + r"(?![\w])", low) for t in vocab.get("reference", [])):
        return "REFERENCE"
    if any(re.search(r"(?<![\w])" + re.escape(t) + r"(?![\w])", low) for t in vocab.get("experimental", [])):
        return "EXPERIMENTAL"
    return None


def arm_mentions(clause, vocab):
    """Every non-overlapping arm mention in the clause, in order: (start, end, side, term)."""
    cands = []
    for side, terms in (("EXPERIMENTAL", vocab.get("experimental", [])), ("REFERENCE", vocab.get("reference", []))):
        for t in terms:
            for m in re.finditer(r"(?<![\w])" + re.escape(t) + r"(?![\w])", clause or "", re.I):
                if _NOT_AN_ARM.match((clause or "")[m.end():]):
                    continue
                if t in _GENERIC_REFERENCE and not re.match(r"\s+(?:group|arm)\b", (clause or "")[m.end():], re.I):
                    continue
                cands.append((m.start(), m.end(), side, t))
    cands.sort(key=lambda c: (c[0], -(c[1] - c[0])))
    out, last = [], -1
    for c in cands:
        if c[0] >= last:
            out.append(c)
            last = c[1]
    return out


def family_arm_ids(fam, vocab):
    """F4 / families.json arm identities (<NCT>:<AACT design_group id>) by side, from the certified family's arm labels."""
    by = {"EXPERIMENTAL": [], "REFERENCE": []}
    for a in (fam or {}).get("arms") or []:
        s = side_of(((a.get("label") or {}).get("value")) or "", vocab)
        if s:
            by[s].append(a.get("arm_id"))
    return by


def rate_witness(clause, ms, num_side, estimate):
    """Second, NUMERIC witness of orientation: the two per-arm percentages stated before the tuple ('608 of 4668 [13.0%] ... 694 of 4672
    [14.9%]'), paired to their arms by position (all percentages precede their arm, or all follow it), must put the numerator arm on the
    same side of 1 as the estimate. Informative only when both the crude ratio and the estimate are at least 5% from 1 (an HR and a crude
    proportion ratio can straddle 1 near the null). CONTRADICTS makes the contrast UNORDERED: two witnesses that disagree order nothing."""
    tuple_at = min([m.start() for _, rx in _CLAUSE_MEASURE for m in [re.search(rx, clause, re.I)] if m] or [len(clause)])
    arms = []
    for m in ms:
        if m[0] < tuple_at and m[2] not in {a[2] for a in arms}:
            arms.append(m)
    pcts = [(m.start(), float(m.group(1))) for m in _PCT.finditer(clause[:tuple_at])]
    out = {"state": "NOT_INFORMATIVE"}
    if len(arms) != 2 or len(pcts) != 2 or estimate is None:
        return dict(out, reason=f"{len(arms)} arm(s) and {len(pcts)} percentage(s) before the tuple; estimate {'given' if estimate is not None else 'absent'}")
    (a1, a2), (p1, p2) = arms, pcts
    if not (p1[0] < a1[0] < p2[0] < a2[0] or a1[0] < p1[0] < a2[0] < p2[0]):
        return dict(out, reason="percentages and arms are not interleaved one-to-one")
    rate = {a1[2]: p1[1], a2[2]: p2[1]}
    ref_side = "REFERENCE" if num_side == "EXPERIMENTAL" else "EXPERIMENTAL"
    if not rate[ref_side] or not rate[num_side] or float(estimate) <= 0:
        return dict(out, reason="a zero rate or a non-positive estimate")
    crude = rate[num_side] / rate[ref_side]
    out.update(rates={"numerator": rate[num_side], "reference": rate[ref_side]}, crude_ratio=round(crude, 6), estimate=estimate)
    if abs(math.log(crude)) < math.log(1.05) or abs(math.log(float(estimate))) < math.log(1.05):
        return dict(out, reason="the crude ratio or the estimate is within 5% of 1")
    return dict(out, state="AGREES" if (crude < 1) == (float(estimate) < 1) else "CONTRADICTS")


def ordered_contrast(clause, values, vocab, fam=None):
    """Recompute the ordered contrast from the tuple's own clause.
    Rule 0 (NUMERATOR_NAMED): 'hazard ratio for X' names X as the numerator.
    Rule 1 (COMPARATIVE_CONNECTIVE): an arm introduced by 'than (in the)', 'compared with', 'versus', 'relative to',
      '(non)inferior/superior to' is the REFERENCE (the denominator).
    Rule 2 (ORDER_OF_MENTION): with neither, the first-named arm is the numerator ('X in the A group and Y in the B group (HR ...)'
      reports A/B) -- the reporting convention, recorded as a weaker witness.
    Conflicting marks (both arms named numerator, both marked reference, or one arm marked both ways) -> UNORDERED.
    Then the NUMERIC witness (rate_witness): per-arm percentages that contradict the ordering -> UNORDERED (fail closed)."""
    out = {"measure": clause_measure(clause), "experimental_arm": None, "reference_arm": None, "numerator_side": None,
           "estimate": values[0] if values else None, "ci_low": values[1] if values else None, "ci_high": values[2] if values else None,
           "direction_witness": None, "rate_witness": None, "state": "UNORDERED"}
    if not clause:
        out["reason"] = "no result clause holds the effect tuple"
        return out
    ms = arm_mentions(clause, vocab)
    sides = {m[2] for m in ms}
    ref_marked = {m[2]: m for m in ms if _REFERENCE_MARK.search(clause[:m[0]])}
    num_marked = {m[2]: m for m in ms if _NUMERATOR_MARK.search(clause[:m[0]])}
    first = {}
    for m in ms:
        first.setdefault(m[2], m)
    if len(ref_marked) == 2 or len(num_marked) == 2 or set(ref_marked) & set(num_marked):
        out["reason"] = "conflicting marks: " + "; ".join(clause[max(0, m[0] - 30):m[1]] for m in list(ref_marked.values()) + list(num_marked.values()))
        return out
    if num_marked:
        num_side = next(iter(num_marked))
        nm = num_marked[num_side]
        lead = _NUMERATOR_MARK.search(clause[:nm[0]])
        out["direction_witness"] = {"rule": "NUMERATOR_NAMED", "text": clause[lead.start():nm[1]], "clause_start": lead.start(), "clause_end": nm[1]}
    elif ref_marked:
        ref_side = next(iter(ref_marked))
        num_side = "EXPERIMENTAL" if ref_side == "REFERENCE" else "REFERENCE"
        rm = ref_marked[ref_side]
        lead = _REFERENCE_MARK.search(clause[:rm[0]])
        out["direction_witness"] = {"rule": "COMPARATIVE_CONNECTIVE", "text": clause[lead.start():rm[1]], "clause_start": lead.start(), "clause_end": rm[1]}
    elif sides == {"EXPERIMENTAL", "REFERENCE"}:
        a, b = sorted((first["EXPERIMENTAL"], first["REFERENCE"]))
        num_side = a[2]
        out["direction_witness"] = {"rule": "ORDER_OF_MENTION", "text": clause[a[0]:b[1]], "clause_start": a[0], "clause_end": b[1],
                                    "note": "no comparative connective; the first-named arm is the numerator by the reporting convention"}
    else:
        out["reason"] = f"the clause names {sorted(sides) or 'no arm'} and no comparative connective orders them"
        return out
    rw = rate_witness(clause, ms, num_side, out["estimate"])
    out["rate_witness"] = rw
    if rw["state"] == "CONTRADICTS":
        out["reason"] = (f"{out['direction_witness']['rule']} puts the {num_side} arm in the numerator, but the stated rates "
                         f"({rw['rates']['numerator']}% vs {rw['rates']['reference']}%, crude {rw['crude_ratio']}) and the estimate {rw['estimate']} disagree")
        out["direction_witness"] = None
        return out
    ids = family_arm_ids(fam, vocab)
    for s, key in (("EXPERIMENTAL", "experimental_arm"), ("REFERENCE", "reference_arm")):
        m = first.get(s)
        out[key] = {"side": s, "term": m[3] if m else None, "named_in_clause": bool(m), "arm_ids": ids[s],
                    "arm_id_basis": "certified families.json arm labels matched to the topic vocabulary" if ids[s] else "no certified arm label matches"}
    out["numerator_side"] = num_side
    out["state"] = "ORDERED"
    return out


def served_orientation(cd, vocab):
    """The numerator side a SERVED comparator_direction VALUE declares: 'A vs B', or a legacy 'vs B' that names only the reference
    (the numerator is then the other side). A typed ordered_contrast beside it is checked separately, never preferred to the value."""
    v = re.sub(r"\s*\(.*$", "", str((cd or {}).get("value") or "")).strip()
    m = re.match(r"^(?:(?P<a>.+?)\s+)?(?:vs\.?|versus)\s+(?P<b>.+)$", v, re.I)
    if not m:
        return None
    sa, sb = (side_of(m.group("a"), vocab) if m.group("a") else None), side_of(m.group("b"), vocab)
    if sa and sb:
        return sa if sa != sb else None
    if sb:
        return "EXPERIMENTAL" if sb == "REFERENCE" else "REFERENCE"
    return None


def normalisation_policy(regd):
    """The registered policy for re-orienting a ratio. Absent -> FORBIDDEN (a reversal nobody permitted is refused)."""
    pol = (regd or {}).get("contrast_normalisation") or {}
    return str(pol.get("reciprocal_for_ratio_measures") or "FORBIDDEN").upper()


def _dec(x):
    s = str(x)
    return len(s.split(".")[1]) if "." in s else 0


def reciprocal_reproduces(src, dst):
    """dst == 1/src with the interval's endpoints swapped, to the precision BOTH sides were printed at (|d(1/x)| = |dx|/x^2)."""
    pairs = ((src["estimate"], dst["estimate"]), (src["ci_high"], dst["ci_low"]), (src["ci_low"], dst["ci_high"]))
    for s, d in pairs:
        if s is None or d is None or float(s) <= 0:
            return False
        tol = 0.5 * 10 ** -_dec(d) + 0.5 * 10 ** -_dec(s) / float(s) ** 2 + 1e-12
        if abs(1.0 / float(s) - float(d)) > tol:
            return False
    return True


def contrast_value_check(served_row, oc, ee_re, vocab, regd):
    """P10 (value) and P11 (registered) for contrast and estimator. Returns {'p10': [...codes], 'p11': [...departures], 'pooled': tuple, ...}.
    The row's effect is ALWAYS the tuple as the source states it; a re-orientation lives in effect.normalisation, never in effect.*."""
    br = served_row or {}
    ai = br.get("analysis_identity") or {}
    cd = ai.get("comparator_direction") or {}
    eff = br.get("effect") or {}
    p10, p11 = [], []
    detail = {}
    # --- contrast VALUE: the served numerator side must be the one the clause orders ---
    srv_num = served_orientation(cd, vocab)
    detail["served_numerator_side"], detail["recomputed_numerator_side"] = srv_num, oc.get("numerator_side")
    if cd.get("basis") == "STATED_IN_OWNING_EVIDENCE" or oc.get("state") == "ORDERED":
        if oc.get("state") != "ORDERED":
            p10.append(("COMPARATOR_DIRECTION_UNRESOLVED", f"served basis {cd.get('basis')} but the clause does not order the arms: {oc.get('reason')}"))
        elif srv_num != oc["numerator_side"]:
            p10.append(("COMPARATOR_DIRECTION_MISMATCH", f"served {cd.get('value')!r} puts the {srv_num} arm in the numerator; the clause orders "
                        f"{oc['numerator_side']} over the other ({oc['direction_witness']['rule']}: {oc['direction_witness']['text']!r}); the stated tuple "
                        f"{eff.get('estimate')} was not reciprocated"))
    typed = cd.get("ordered_contrast")
    if isinstance(typed, dict) and oc.get("state") == "ORDERED":
        diffs = [k for k, a, b in (("numerator_side", typed.get("numerator_side"), oc.get("numerator_side")),
                                   ("measure", (typed.get("measure") or {}).get("measure"), (oc.get("measure") or {}).get("measure")),
                                   ("experimental_arm_ids", (typed.get("experimental_arm") or {}).get("arm_ids"), (oc.get("experimental_arm") or {}).get("arm_ids")),
                                   ("reference_arm_ids", (typed.get("reference_arm") or {}).get("arm_ids"), (oc.get("reference_arm") or {}).get("arm_ids")),
                                   ("estimate", typed.get("estimate"), oc.get("estimate")), ("ci_low", typed.get("ci_low"), oc.get("ci_low")),
                                   ("ci_high", typed.get("ci_high"), oc.get("ci_high")),
                                   ("direction_witness", (typed.get("direction_witness") or {}).get("text"), (oc.get("direction_witness") or {}).get("text")))
                 if a != b]
        if diffs:
            p10.append(("COMPARATOR_DIRECTION_MISMATCH", f"the served ordered_contrast object disagrees with the recomputation on {diffs}"))
    # --- estimator VALUE: the served label and the served estimator field must be the measure the source states ---
    cm = oc.get("measure") or {}
    srv_scale = scale_measure(eff.get("scale"))
    est_field = ai.get("estimator") or {}
    est_re = (ee_re or {}).get("estimator") or {}
    detail["served_scale"], detail["clause_measure"] = srv_scale, cm.get("measure")
    if cm.get("state") == "STATED" and srv_scale != cm["measure"]:
        p10.append(("ESTIMATOR_MISMATCH", f"served effect.scale {eff.get('scale')!r} but the tuple's own clause states {cm['matched']!r} ({cm['measure']})"))
    elif cm.get("state") != "STATED" and srv_scale is None:
        p10.append(("ESTIMATOR_MISMATCH", f"served effect.scale {eff.get('scale')!r} is not an identified measure and the clause states {cm.get('state')}"))
    if est_field.get("basis") == "STATED_IN_OWNING_EVIDENCE" and est_re.get("state") == "STATED_IN_OWNING_EVIDENCE" and est_field.get("value") != est_re.get("value"):
        p10.append(("ESTIMATOR_MISMATCH", f"served estimator {est_field.get('value')!r}, recomputed from the source {est_re.get('value')!r}"))
    if est_field.get("value") and _ESTIMATOR_MEASURE.get(est_field.get("value")) and srv_scale and _ESTIMATOR_MEASURE[est_field["value"]] != srv_scale:
        p10.append(("ESTIMATOR_MISMATCH", f"served estimator {est_field.get('value')!r} and served effect.scale {eff.get('scale')!r} name different measures"))
    # --- declared normalisation: the only admissible way a reversed contrast reaches the pool ---
    stated = {k: eff.get(k) for k in ("estimate", "ci_low", "ci_high")}
    norm = eff.get("normalisation")
    pooled_num, pooled = srv_num, stated
    if norm:
        pol = normalisation_policy(regd)
        detail["normalisation"] = {"operation": norm.get("operation"), "policy": pol}
        if str(norm.get("operation") or "").upper() != "RECIPROCAL":
            p10.append(("CONTRAST_NORMALISATION_UNKNOWN", f"declared normalisation {norm.get('operation')!r}; only RECIPROCAL is defined"))
        elif srv_scale not in RATIO_MEASURES:
            p10.append(("CONTRAST_NORMALISATION_UNKNOWN", f"a reciprocal is defined for ratio measures only; served scale {eff.get('scale')!r}"))
        elif not pol.startswith("PERMITTED"):
            p10.append(("CONTRAST_NORMALISATION_NOT_PERMITTED", f"a declared reciprocal re-orientation is refused under policy {pol} "
                        "(registered_estimand.contrast_normalisation; absent = FORBIDDEN)"))
        else:
            dst = {k: norm.get(k) for k in ("estimate", "ci_low", "ci_high")}
            nnum = served_orientation({"value": norm.get("orientation")}, vocab)
            if not reciprocal_reproduces(stated, dst):
                p10.append(("CONTRAST_NORMALISATION_NOT_REPRODUCED", f"declared reciprocal {dst} is not 1/{stated} with the endpoints swapped"))
            elif nnum is None or nnum == srv_num:
                p10.append(("CONTRAST_NORMALISATION_NOT_REPRODUCED", f"declared orientation {norm.get('orientation')!r} is not the reverse of the stated one"))
            else:
                pooled_num, pooled = nnum, dst
    detail["pooled_numerator_side"], detail["pooled_tuple"] = pooled_num, pooled
    # --- P11: what enters the pool must be the REGISTERED contrast and estimator ---
    reg_num = served_orientation({"value": (regd or {}).get("contrast")}, vocab)
    reg_measure = next((m for w, m in _ESTIMATOR_MEASURE.items() if w in str((regd or {}).get("estimator") or "").lower()), None)
    detail["registered_numerator_side"], detail["registered_measure"] = reg_num, reg_measure
    if (regd or {}).get("contrast") not in (None, "UNSTATED"):
        if reg_num is None:
            p11.append("contrast (the registered contrast names no arm this topic's vocabulary resolves)")
        elif pooled_num != reg_num:
            p11.append(f"contrast (pooled orientation puts the {pooled_num} arm in the numerator; registered {regd.get('contrast')!r})")
        elif oc.get("experimental_arm") and oc["experimental_arm"].get("term") is None and oc.get("state") == "ORDERED":
            pass   # 'HR vs placebo': the experimental arm is implied, not named -- the registered class is not contradicted
    if (regd or {}).get("estimator") not in (None, "UNSTATED") and reg_measure and srv_scale != reg_measure:
        p11.append(f"estimator (served {eff.get('scale')!r}; registered {regd.get('estimator')!r})")
    return {"p10": p10, "p11": p11, "detail": detail, "pooled": pooled, "pooled_numerator_side": pooled_num, "measure": srv_scale}


def pool_measure_guard(inputs, rows_by_pmid, declared_scale):
    """Refuse BEFORE any log is taken: pool() is log(effect) whatever the effect is. Every input's measure must be identified from its
    row (served label value-checked against the clause), all inputs one ratio measure, equal to the pool's declared scale; and every
    input must be its row's tuple in the orientation that enters the pool (a reciprocal in the pool beside a canonical row is refused)."""
    measures, problems = {}, []
    for i in inputs:
        pid = str(i.get("id", "")).replace("PMID ", "")
        r = rows_by_pmid.get(pid)
        if r is None:
            problems.append(("POOL_MEASURE_UNIDENTIFIED", f"{pid}: pool input has no verified row"))
            continue
        cv = r
        m = cv.get("measure")
        measures[pid] = m
        if m is None or "ESTIMATOR_MISMATCH" in cv.get("p10", []):
            problems.append(("POOL_MEASURE_UNIDENTIFIED", f"{pid}: the row's measure is not identified (served {m!r}; clause {(cv.get('detail') or {}).get('clause_measure')!r})"))
        want = cv.get("pooled") or {}
        if want and any(want.get(k) is None or abs(float(i.get(src)) - float(want[k])) > 1e-12
                        for k, src in (("estimate", "effect"), ("ci_low", "ci_low"), ("ci_high", "ci_high"))):
            problems.append(("POOL_INPUT_DISAGREES_WITH_ROW", f"{pid}: pool input {i.get('effect')} ({i.get('ci_low')}-{i.get('ci_high')}) is not the row's "
                              f"pooled-orientation tuple {want}"))
    ids = {m for m in measures.values() if m}
    if len(ids) > 1:
        problems.append(("POOL_MEASURE_MIXED", f"inputs carry {sorted(ids)}: log(HR), log(OR), log(RR) are different quantities"))
    if any(m not in RATIO_MEASURES for m in ids):
        problems.append(("POOL_MEASURE_NOT_RATIO", f"{sorted(ids)}: the pool takes logs; only ratio measures are defined"))
    ds = scale_measure(declared_scale)
    if ids and len(ids) == 1 and ds != next(iter(ids)):
        problems.append(("POOL_MEASURE_MIXED", f"the pool declares scale {declared_scale!r}; its inputs are {sorted(ids)}"))
    return {"measures": measures, "refusals": problems, "refused": bool(problems)}


# LEADER's primary clause, as held, and two re-orientations of it -- the fixtures of the OC --corrupt limbs (in memory only)
_OC_LEADER_HELD = ("fewer patients in the liraglutide group (608 of 4668 patients [13.0%]) than in the placebo group (694 of 4672 [14.9%]) "
                   "(hazard ratio, 0.87; 95% confidence interval [CI], 0.78 to 0.97")
_OC_LEADER_SWAPPED = ("fewer patients in the placebo group (608 of 4668 patients [13.0%]) than in the liraglutide group (694 of 4672 [14.9%]) "
                      "(hazard ratio, 0.87; 95% confidence interval [CI], 0.78 to 0.97")          # arm NAMES swapped: a self-consistent source in which
                                                                                                  # placebo/liraglutide = 0.87 (its rates agree)
_OC_LEADER_RECIPROCAL = ("more patients in the placebo group (694 of 4672 [14.9%]) than in the liraglutide group (608 of 4668 patients [13.0%]) "
                         "(hazard ratio, 1.15; 95% confidence interval [CI], 1.03 to 1.28")        # the same trial stated placebo/liraglutide


def _oc_source_edit(store, bundle, rec_by_pmid, t, br, pmid, old, new):
    """A controlled source edit that keeps every OTHER layer self-consistent (records, span, offsets, representation digests, the
    retained XML and its recorded digest), so only the contrast can be what a refusal is about. In memory; nothing is written."""
    ab = rec_by_pmid[pmid]["abstract"]
    if old not in ab or old not in t["endpoint_result_span"]:
        raise Refusal("UNKNOWN_LIMB", f"{pmid}: the OC contrast fixture is not in this record")
    rec_by_pmid[pmid] = dict(rec_by_pmid[pmid], abstract=ab.replace(old, new))
    t["endpoint_result_span"] = t["endpoint_result_span"].replace(old, new)
    parsed = rec_by_pmid[pmid]["abstract"]
    br["source"]["representation_sha256"] = sha256_text(parsed)
    rep = parsed if br["span"].get("parent_representation") == "PARSED_SOURCE" else normalize(parsed)
    br["span"]["representation_sha256"] = sha256_text(rep)
    if br["span"].get("start") is not None:
        br["span"]["end"] = br["span"]["start"] + len(t["endpoint_result_span"] if br["span"].get("parent_representation") == "PARSED_SOURCE" else normalize(t["endpoint_result_span"]))
    delta = len(new) - len(old)
    for fv in (br.get("analysis_identity") or {}).values():
        if isinstance(fv, dict) and fv.get("span") and old in fv["span"]:
            fv["span"] = fv["span"].replace(old, new)
            fv["end"] = fv["end"] + delta if fv.get("end") is not None else None
            if isinstance(fv.get("observed"), dict):
                fv["observed"].update(span=fv["span"], end=fv["end"])
    for d in bundle.get("documents", []):
        ac = (d.get("representations") or {}).get("ACQUIRED_SOURCE") or {}
        if d["document_id"] == f"pubmed:{pmid}" and ac.get("ref"):
            path = ac["ref"].removeprefix("docs/")
            xml = store.get(path).replace(old.encode("utf-8"), new.encode("utf-8"))
            store.cache[path] = xml
            ac["sha256_original"] = sha256(xml)


def _oc_set_tuple(t, br, est, lo, hi, scale=None):
    t["effect"], t["ci_low"], t["ci_high"] = est, lo, hi
    br["effect"].update(estimate=est, ci_low=lo, ci_high=hi)
    if scale is not None:
        t["scale"] = br["effect"]["scale"] = scale


def _oc_set_contrast(br, value):
    cd = br["analysis_identity"]["comparator_direction"]
    cd["value"] = value
    if isinstance(cd.get("observed"), dict):
        cd["observed"]["value"] = value


def _oc_recip(x, nd=4):
    return round(1.0 / float(x), nd)


# ---- CI level: the level the source STATES vs the level the derivation ASSUMED --------------------------------------
_CI_PCT = re.compile(r"(\d{2}(?:[.\u00b7]\d+)?)\s*%\s*(?:confidence interval|CI\b|credible interval)", re.I)
Z_ASSUMED_BY_DERIVATION = 1.959963984540054   # the harness derives SE_log with the 97.5th normal quantile, i.e. a 95% two-sided interval


def inverse_normal(p):
    """Phi^-1(p) by bisection on math.erf; standard library only; |error| < 1e-12."""
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if 0.5 * (1.0 + math.erf(mid / math.sqrt(2.0))) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def stated_ci_pct(clause):
    """The CI level the tuple's own clause states, e.g. '95% CI', '95.03% confidence interval'; None when unstated."""
    if not clause:
        return None
    m = _CI_PCT.search(normalize(clause))
    return float(m.group(1).replace("\u00b7", ".")) if m else None


def ci_level_record(clause, se_used, ci_low, ci_high):
    """source_ci_pct with its basis, the z the derivation assumed, the z the stated level implies, and MATCH / MISMATCH / UNSTATED.
    A mismatch is a refusal, not a relabel: an SE derived with z(95%) from a 95.03% interval is wrong, and silently so."""
    pct = stated_ci_pct(clause)
    rec = {"assumed_ci_pct": 95.0, "z_assumed_by_derivation": Z_ASSUMED_BY_DERIVATION}
    if pct is None:
        rec.update({"source_ci_pct": None, "basis": "UNSTATED", "level_agreement": "UNSTATED",
                    "note": "the tuple's clause does not state the interval's level; the derivation assumed 95% and that assumption is recorded, not verified"})
        return rec
    z_stated = inverse_normal(1.0 - (1.0 - pct / 100.0) / 2.0)
    rec.update({"source_ci_pct": pct, "basis": "STATED_IN_OWNING_EVIDENCE", "z_for_stated_level": z_stated,
                "level_agreement": "MATCH" if abs(pct - 95.0) < 1e-9 else "MISMATCH"})
    if ci_low and ci_high and se_used:
        rec["se_log_at_stated_level"] = (math.log(ci_high) - math.log(ci_low)) / (2.0 * z_stated)
        rec["se_log_used"] = se_used
    return rec


class Refusal(Exception):
    """A named refusal that must become a JSON verdict, never a crash."""

    def __init__(self, code, detail):
        super().__init__(f"{code} {detail}")
        self.code, self.detail = code, detail


def resolve_selector(records, pmid):
    """The bundle's selector rule: the UNIQUE record with id_type pmid and id == pmid; 0 or >=2 matches refuse."""
    m = [r for r in records["records"] if str(r.get("id_type", "pmid")).lower() == "pmid" and str(r.get("id")) == str(pmid)]
    if len(m) != 1:
        raise Refusal("SELECTOR_REFUSED", f"#PMID-{pmid}: resolves to {len(m)} records (rule requires exactly one)")
    return m[0]


def locate(span, hay):
    if not span:
        return {"match": "NO_SPAN"}
    i = hay.find(span)
    if i >= 0:
        return {"match": "VERBATIM", "parent": "PARSED_SOURCE", "start": i, "end": i + len(span)}
    s, h = normalize(span), normalize(hay)
    i = h.find(s)
    if i >= 0:
        return {"match": "NORMALISED", "parent": "NORMALIZED_SOURCE", "start": i, "end": i + len(s)}
    return {"match": "NOT_LOCATED"}


def tokens_of(x):
    if x is None:
        return []
    s = repr(float(x))
    return [s[:-2] if s.endswith(".0") else s]


def preservation(cached: str, xml_bytes: bytes):
    root = ET.fromstring(xml_bytes)
    units = [_WS.sub(" ", "".join(a.itertext())).strip() for a in root.findall(".//Abstract/AbstractText")]
    labels = [a.get("Label") for a in root.findall(".//Abstract/AbstractText")]
    c = _WS.sub(" ", cached or "").strip()
    resid = c
    states = []
    for u, lab in zip(units, labels):
        ok = bool(u) and u in c
        states.append("PRESERVED" if ok else "MISSING")
        if ok:
            resid = resid.replace(u, "")
            if lab:
                resid = resid.replace(lab + ":", "")
    resid = _WS.sub(" ", resid).strip()
    verdict = "PRESERVED" if units and all(s == "PRESERVED" for s in states) and not resid else "FAILURE"
    return {"units": len(units), "preserved": states.count("PRESERVED"), "missing": states.count("MISSING"), "extra_chars": len(resid), "verdict": verdict}


def live_anchor(pmid: str, retained_xml: bytes, cached_abstract: str) -> dict:
    """External observation: EFetch NOW, compare abstract units with the retained XML and with the cached abstract."""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml&tool=verify_bundle&email=meta-harness@example.org"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "verify_bundle/1"})
        with urllib.request.urlopen(req, timeout=120) as r:
            live = r.read()
    except Exception as exc:  # network is an external dependency; report, do not pretend
        return {"fetched": False, "error": str(exc)[:200]}

    def units(b):
        root = ET.fromstring(b)
        return [_WS.sub(" ", "".join(a.itertext())).strip() for a in root.findall(".//Abstract/AbstractText")]

    def revised(b):
        d = ET.fromstring(b).find(".//MedlineCitation/DateRevised")
        return f"{d.findtext('Year')}-{d.findtext('Month')}-{d.findtext('Day')}" if d is not None else None

    lu, ru = units(live), units(retained_xml)
    c = _WS.sub(" ", cached_abstract or "").strip()
    return {"fetched": True, "live_sha256": sha256(live), "live_bytes": len(live), "live_date_revised": revised(live), "retained_date_revised": revised(retained_xml),
            "live_units": len(lu), "retained_units": len(ru),
            "units_in_live_not_in_retained": [u[:120] for u in lu if u not in ru],
            "units_in_retained_not_in_live": [u[:120] for u in ru if u not in lu],
            "live_units_missing_from_cached_abstract": sum(1 for u in lu if u and u not in c),
            "live_equals_retained_bytes": sha256(live) == sha256(retained_xml)}


def run(store: Store, slug: str, corrupt: tuple[str, str] | None, anchor_live: bool = False):
    R = f"reviews/{slug}/"
    bundle = store.json(R + "BUNDLE.json")
    report = {"slug": slug, "schema_version": bundle.get("schema_version"), "artefacts": [], "supporting": [], "certificate": {},
              "rows": [], "absence_claims": [], "pool": {}, "corruption": None, "verdict": None}
    failures = []

    # 1. artefacts ---------------------------------------------------------------------------------------------
    for a in bundle["artefacts"]:
        if a["state"] != "SERVED":
            report["artefacts"].append({"ref": a["ref"], "state": a["state"], "checked": "not served; verification route stated in bundle"})
            continue
        try:
            data = store.get(a["served_path"])
        except Refusal as r:
            report["artefacts"].append({"ref": a["ref"], "bytes_ok": False, "declared_digest_ok": False, "refusal": r.code})
            failures.append(f"{r.code} {r.detail}")
            continue
        ok_bytes = sha256(data) == a["sha256"] and len(data) == a["bytes"]
        role = a["role"]
        if role == "held_documents":
            got = sha256(data)
        elif role == "analysis_code_sha256":
            got = git_blob(data, lf=True)
        elif role == "protocol_text_sha256":
            got = sha256_text(data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))
        elif a.get("declared_digest") is not None:
            got = sha256_text(canonical(json.loads(data.decode("utf-8"))))
        else:
            got = None
        ok_decl = a.get("declared_digest") is None or got == a["declared_digest"]
        report["artefacts"].append({"ref": a["ref"], "bytes_ok": ok_bytes, "declared_digest_ok": ok_decl})
        if not (ok_bytes and ok_decl):
            failures.append(f"ARTEFACT_DIGEST_MISMATCH {a['ref']}: bytes_ok={ok_bytes} declared_digest_ok={ok_decl}")
    for f in bundle.get("supporting_files", []):
        try:
            data = store.get(f["path"].removeprefix("docs/"))
        except Refusal as r:
            report["supporting"].append({"path": f["path"], "ok": False, "refusal": r.code})
            failures.append(f"{r.code} {r.detail}")
            continue
        ok = sha256(data) == f["sha256"] and len(data) == f["bytes"]
        report["supporting"].append({"path": f["path"], "ok": ok})
        if not ok:
            failures.append(f"SUPPORTING_FILE_DIGEST_MISMATCH {f['path']}")

    # 2. certificate and review core --------------------------------------------------------------------------
    cert_bytes = store.get(R + "CERTIFICATE.json")
    cert = json.loads(cert_bytes.decode("utf-8"))
    review = store.json(R + "review.json")
    rel_ok = sha256_text(canonical({k: v for k, v in cert.items() if k != "release_sha256"})) == cert["release_sha256"]
    rev_ok = sha256_text(canonical({k: v for k, v in review.items() if k != "reproduction"})) == cert["review_sha256"]
    file_ok = sha256(cert_bytes) == bundle["certificate"]["sha256_of_file"]
    report["certificate"] = {"release_sha256_recomputed": rel_ok, "review_sha256_recomputed": rev_ok, "file_sha256_matches_bundle": file_ok,
                             "release_sha256": cert["release_sha256"]}
    for name, ok in report["certificate"].items():
        if ok is False:
            failures.append(f"CERTIFICATE_MISMATCH {name}")

    # 3. load records / families; apply corruption in memory ----------------------------------------------------
    records = store.json(f"cache/{slug}/records.json")
    rec_by_pmid, selector_refusals = {}, {}
    for br in bundle["verification_rows"]:
        pmid = br["trial"]["id"].replace("PMID ", "")
        frag = (br["source"].get("document_ref") or "").split("#PMID-")[-1] if "#PMID-" in (br["source"].get("document_ref") or "") else None
        try:
            dref = br["source"].get("document_ref") or ""
            if dref and not dref.split("#")[0].endswith("records.json"):
                raise Refusal("UNSUPPORTED_REPRESENTATION", f"{pmid}: source {dref.split('#')[0]} is a text artefact; this checker binds pooled rows to PubMed records only (bundle limit L14) -- no claim is made")
            if frag is None:
                raise Refusal("SELECTOR_REFUSED", f"{pmid}: document_ref carries no #PMID fragment")
            if frag != pmid:
                raise Refusal("SELECTOR_MISMATCH", f"{pmid}: document_ref fragment #PMID-{frag} does not name the row's trial")
            rec_by_pmid[pmid] = resolve_selector(records, frag)       # refuses on 0 or >=2, by the FRAGMENT the rule names
        except Refusal as r:
            selector_refusals[pmid] = r
            failures.append(f"{r.code} {r.detail}")
    for r in records["records"]:
        rec_by_pmid.setdefault(str(r["id"]), r)
    try:
        certified = store.json(f"cache/{slug}/families.json")
        fam_certified = {f.get("family_id"): f for f in certified.get("families", []) if isinstance(f, dict)}
    except Refusal as r:
        fam_certified, certified = {}, None
        failures.append(f"{r.code} {r.detail} (certified eligibility copy)")
    # digest scopes the bundle publishes for the container: all three must reproduce
    raw = store.get(f"cache/{slug}/records.json")
    scopes = {sc["subject"]: sc["value"] for d in bundle.get("digest_scopes", []) for sc in d["scopes"]}
    if scopes:
        got = {"raw served bytes": sha256(raw), "whole file as JSON object": sha256_text(canonical(json.loads(raw.decode("utf-8")))),
               "obj['records'] only": sha256_text(canonical(json.loads(raw.decode("utf-8"))["records"]))}
        for k, v in scopes.items():
            if got.get(k) != v:
                failures.append(f"DIGEST_SCOPE_MISMATCH '{k}' does not reproduce under the published canonicalisation")
        report["digest_scopes_reproduced"] = all(got.get(k) == v for k, v in scopes.items())
    container_sha = sha256(store.get(f"cache/{slug}/records.json"))
    families = {f.get("family_id"): f for f in review.get("trial_families", []) if isinstance(f, dict)}   # rendered copy (cross-check only)
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    trials = [dict(t) for t in primary["trials"]]
    canonical_components = sorted((primary.get("endpoint_canonical") or {}).get("components") or [])
    bundle_rows = {r["trial"]["id"].replace("PMID ", ""): r for r in bundle["verification_rows"]}
    if corrupt:
        pmid, limb = corrupt
        if limb in ("regulatory_strategy_swap", "regulatory_consistent_swap"):   # ELIXA tests (pmid ignored)
            for rf in bundle.get("regulatory_facts", []):
                if rf["trial"] == "ELIXA":
                    rf["decision"]["effect"] = {"scale": "HR", "estimate": 1.01, "ci_low": 0.87, "ci_high": 1.17}
                    if limb == "regulatory_consistent_swap":
                        rf["decision"]["claimed_treatment_strategy"] = "on-treatment"
            report["corruption"] = {"pmid": pmid, "limb": limb}
            t = br = None
        else:
            t = next(x for x in trials if str(x["id"]).replace("PMID ", "") == pmid)
            br = bundle_rows[pmid]
        if t is None:
            pass
        elif limb == "span":
            t["endpoint_result_span"] = t["endpoint_result_span"][:-1] + ("x" if not t["endpoint_result_span"].endswith("x") else "y")
        elif limb == "effect":
            t["effect"] = round(float(t["effect"]) + 0.01, 4)
        elif limb == "components":
            br["endpoint"]["components_canonical"] = br["endpoint"]["components_canonical"][:-1]
        elif limb == "eligibility":
            fam_certified[t["family_id"]] = dict(fam_certified.get(t["family_id"], {}), eligibility={"state": "UNKNOWN", "absence_code": "CORRUPTED_BY_VERIFIER"})
        elif limb == "conflict":
            families[t["family_id"]] = dict(families[t["family_id"]], conflicts=[{"state": "UNRESOLVED", "note": "planted by verifier"}])
        elif limb == "binding":
            t["endpoint_binding"] = "unbound_legacy"
        elif limb == "near_match":         # ODYSSEY's served fields (pcsk9-mace, PMID 30403574): NEAR_MATCH, extra ['unstable angina'], missing [] while lacking CV death
            t["target_endpoint_class"], t["endpoint_admissibility"] = "NEAR_MATCH", "NEAR_MATCH_DECLARED"
            t["target_endpoint_components"] = ["coronary heart disease death", "myocardial infarction", "stroke", "unstable angina"]
            t["target_endpoint_extra_components"], t["target_endpoint_missing_components"] = ["unstable angina"], []
            br["endpoint"]["components_canonical"] = ["CORONARY_HEART_DISEASE_DEATH", "MYOCARDIAL_INFARCTION", "STROKE", "UNSTABLE_ANGINA"]
        elif limb == "nontarget_span":     # M7a shape: a genuine non-target sentence from the same record, numbers intact
            t["endpoint_result_span"] = f"Death from cardiovascular causes occurred in fewer patients (hazard ratio, {t['effect']}; 95% CI, {t['ci_low']} to {t['ci_high']})."
        elif limb == "unlisted_span":      # M8 shape: an unlisted outcome with genuine numbers
            t["endpoint_result_span"] = f"Retinopathy complications occurred in more patients (hazard ratio, {t['effect']}; 95% CI, {t['ci_low']} to {t['ci_high']})."
        elif limb == "fragment":           # M11 shape: document_ref fragment rewritten
            br["source"]["document_ref"] = br["source"]["document_ref"].split("#")[0] + "#PMID-99999999"
        elif limb == "ci_high_rounded":       # the rounded-match defect: stored upper limit 0.96 where the clause says 1.0 (or 0.97 -> 0.9)
            t["ci_high"] = round(float(t["ci_high"]) - 0.04, 2) if float(t["ci_high"]) >= 1.0 else float(str(t["ci_high"])[:3])
        elif limb == "ci_low_truncated":      # stored 0.7 where the clause says 0.78: substring would accept, numeric refuses
            t["ci_low"] = float(str(t["ci_low"])[:3])
        elif limb == "duplicate_span_no_offsets":   # B3: the span occurs twice and the bundle carries no offsets (digests follow the edit)
            rec_by_pmid[pmid] = dict(rec_by_pmid[pmid], abstract=rec_by_pmid[pmid]["abstract"] + " " + t["endpoint_result_span"])
            br["source"]["representation_sha256"] = sha256_text(rec_by_pmid[pmid]["abstract"])
            br["span"]["representation_sha256"] = sha256_text(rec_by_pmid[pmid]["abstract"]) if br["span"].get("parent_representation") == "PARSED_SOURCE" else sha256_text(normalize(rec_by_pmid[pmid]["abstract"]))
            br["span"]["start"] = br["span"]["end"] = None
        elif limb == "default_as_statement":   # a REGISTERED_DEFAULT field given a span: a default rendered as a statement
            for fname, fv in br["analysis_identity"].items():
                if isinstance(fv, dict) and fv.get("basis") == "REGISTERED_DEFAULT":
                    fv["span"] = "intention-to-treat"; break
        elif limb == "served_basis_lie":   # the bundle says REGISTERED_DEFAULT where the source states on-treatment (a deserialised state must not be trusted)
            rec_by_pmid[pmid] = dict(rec_by_pmid[pmid], abstract=rec_by_pmid[pmid]["abstract"].replace("intention-to-treat", "on-treatment population"))
            br["source"]["representation_sha256"] = sha256_text(rec_by_pmid[pmid]["abstract"])
            br["span"]["representation_sha256"] = sha256_text(rec_by_pmid[pmid]["abstract"]) if br["span"].get("parent_representation") == "PARSED_SOURCE" else sha256_text(normalize(rec_by_pmid[pmid]["abstract"]))
        elif limb in ("contrast_reverse", "contrast_reverse_served", "contrast_reverse_declared", "contrast_reverse_declared_permitted",
                      "contrast_reverse_declared_forbidden", "contrast_reverse_declared_away", "estimator_swap", "measure_unidentified",
                      "pool_input_reciprocal"):
            # lane OC: ordered contrast / estimator / measure limbs (fixtures: LEADER's primary clause; see _OC_LEADER_*)
            regd_ = bundle.setdefault("registered_estimand", {})
            pin = next(i for i in bundle["pooled_reference"]["inputs"] if str(i["id"]).replace("PMID ", "") == pmid)
            if limb == "contrast_reverse":                  # the SOURCE orders placebo/liraglutide; the served 0.87 stays liraglutide/placebo
                _oc_source_edit(store, bundle, rec_by_pmid, t, br, pmid, _OC_LEADER_HELD, _OC_LEADER_SWAPPED)
            elif limb == "contrast_reverse_served":         # the SERVED contrast claims placebo/liraglutide for the unreciprocated 0.87
                _oc_set_contrast(br, "placebo vs liraglutide")
            elif limb.startswith("contrast_reverse_declared") and limb != "contrast_reverse_declared_away":
                # the source states placebo/liraglutide 1.15 (1.03-1.28); the row carries that tuple AS STATED and a DECLARED reciprocal to the
                # registered orientation, 0.87 (0.78-0.97) -- the pool input. PASS only where the registered policy permits it.
                _oc_source_edit(store, bundle, rec_by_pmid, t, br, pmid, _OC_LEADER_HELD, _OC_LEADER_RECIPROCAL)
                _oc_set_tuple(t, br, 1.15, 1.03, 1.28)
                _oc_set_contrast(br, "placebo vs liraglutide")
                cl = clause_with_effect(t["endpoint_result_span"], [t["effect"], t["ci_low"], t["ci_high"]])   # a CONSISTENT producer re-emits the typed object
                br["analysis_identity"]["comparator_direction"]["ordered_contrast"] = ordered_contrast(
                    cl, [t["effect"], t["ci_low"], t["ci_high"]], contrast_vocabulary(store.json(f"topics/{slug}.json")), fam_certified.get(t.get("family_id")))
                br["effect"]["normalisation"] = {"operation": "RECIPROCAL", "orientation": "liraglutide vs placebo",
                                                 "estimate": pin["effect"], "ci_low": pin["ci_low"], "ci_high": pin["ci_high"]}
                if limb.endswith("_permitted"):
                    regd_["contrast_normalisation"] = {"reciprocal_for_ratio_measures": "PERMITTED_WHEN_DECLARED"}
                elif limb.endswith("_forbidden"):
                    regd_["contrast_normalisation"] = {"reciprocal_for_ratio_measures": "FORBIDDEN"}
            elif limb == "contrast_reverse_declared_away":  # LEADER 0.87 declared-reciprocated to placebo/liraglutide ~1.149, and pooled so
                regd_["contrast_normalisation"] = {"reciprocal_for_ratio_measures": "PERMITTED_WHEN_DECLARED"}
                norm = {"operation": "RECIPROCAL", "orientation": "placebo vs liraglutide", "estimate": _oc_recip(t["effect"]),
                        "ci_low": _oc_recip(t["ci_high"]), "ci_high": _oc_recip(t["ci_low"])}
                br["effect"]["normalisation"] = norm
                pin.update(effect=norm["estimate"], ci_low=norm["ci_low"], ci_high=norm["ci_high"])
                bundle["pooled_reference"]["expected"] = pool(bundle["pooled_reference"]["inputs"])
            elif limb == "estimator_swap":                  # the hazard ratio relabelled an odds ratio (label AND estimator field)
                _oc_set_tuple(t, br, t["effect"], t["ci_low"], t["ci_high"], scale="OR")
                est = br["analysis_identity"]["estimator"]
                est["value"] = "odds ratio"
                if isinstance(est.get("observed"), dict):
                    est["observed"]["value"] = "odds ratio"
            elif limb == "measure_unidentified":            # the label dropped: log() would be taken of a number of unknown kind
                t["scale"] = br["effect"]["scale"] = None
            elif limb == "pool_input_reciprocal":           # the row stays canonical; its POOL INPUT is the reciprocal
                pin.update(effect=_oc_recip(t["effect"]), ci_low=_oc_recip(t["ci_high"]), ci_high=_oc_recip(t["ci_low"]))
                bundle["pooled_reference"]["expected"] = pool(bundle["pooled_reference"]["inputs"])
        elif limb == "container":
            rec_by_pmid[pmid] = dict(rec_by_pmid[pmid], abstract=rec_by_pmid[pmid]["abstract"] + " ")
            container_sha = sha256(container_sha.encode())  # the container bytes would differ; represent that
        else:
            raise Refusal("UNKNOWN_LIMB", f"{limb}")
        report["corruption"] = {"pmid": pmid, "limb": limb}
        if limb == "fragment":
            frag = br["source"]["document_ref"].split("#PMID-")[-1]
            try:
                if frag != pmid:
                    raise Refusal("SELECTOR_MISMATCH", f"{pmid}: document_ref fragment #PMID-{frag} does not name the row's trial")
            except Refusal as r:
                selector_refusals[pmid] = r

    # 4. predicates per row -----------------------------------------------------------------------------------
    for t in trials:
        pmid = str(t["id"]).replace("PMID ", "")
        br = bundle_rows.get(pmid)
        parsed = (rec_by_pmid.get(pmid) or {}).get("abstract") or ""
        span = t.get("endpoint_result_span") or ""
        loc = locate_all(span, parsed)
        fam_c = fam_certified.get(t.get("family_id")) or {}
        fam = families.get(t.get("family_id")) or {}
        elig = (fam_c.get("eligibility") or {}).get("state") if fam_c else None          # CERTIFIED copy is authoritative
        elig_rendered = (fam.get("eligibility") or {}).get("state")
        if fam_c and elig != elig_rendered and not corrupt:
            failures.append(f"ELIGIBILITY_COPIES_DISAGREE {t.get('family_id')}: certified {elig} vs rendered {elig_rendered}")
        conf = (fam_c.get("conflicts") if fam_c.get("conflicts") is not None else fam.get("conflicts")) or []
        unresolved = [c for c in conf if isinstance(c, dict) and str(c.get("state", "")).upper().startswith("UNRESOLVED")]
        toks = tokens_of(t.get("effect")) + tokens_of(t.get("ci_low")) + tokens_of(t.get("ci_high"))
        values = [t.get("effect"), t.get("ci_low"), t.get("ci_high")]
        eff_clause = clause_with_effect(span, values) if all(x is not None for x in values) else None
        nums = clause_numbers(eff_clause) if eff_clause else []
        located = loc["match"] in ("VERBATIM", "NORMALISED")
        # zero / one / many: many is only acceptable when the bundle's offsets pin one occurrence
        span_state = None
        if loc.get("occurrences", 0) > 1:
            pinned = bool(br and br["span"].get("start") is not None)
            if not pinned:
                located = False
                span_state = "SPAN_LOCATION_AMBIGUOUS"
        # span offsets as recorded by the bundle must reproduce the span text in the named representation
        offsets_ok = None
        if br and br["span"].get("start") is not None and not (corrupt and corrupt[0] == pmid and corrupt[1] == "span"):
            rep = parsed if br["span"]["parent_representation"] == "PARSED_SOURCE" else normalize(parsed)
            piece = rep[br["span"]["start"]:br["span"]["end"]]     # code-point slice, half-open, per bundle.coordinates
            offsets_ok = piece == (span if br["span"]["parent_representation"] == "PARSED_SOURCE" else normalize(span))
            rep_sha_ok = sha256_text(rep) == br["span"]["representation_sha256"]
            offsets_ok = offsets_ok and rep_sha_ok
        comps_canon = (br or {}).get("endpoint", {}).get("components_canonical") or []
        P = {
            "P1_source_bytes": container_sha == (br or {}).get("source", {}).get("source_sha256") and sha256_text(parsed) == (br or {}).get("source", {}).get("representation_sha256") if not (corrupt and corrupt[1] == "container" and corrupt[0] == pmid) else False,
            "P2_span_located": located and (offsets_ok is not False),
            "P3_effect_tokens_in_span": bool(toks) and bool(nums) and all(any(abs(float(tok) - n) < 1e-12 for n in nums) for tok in toks),
            "P4_endpoint_components": bool(comps_canon) and sorted(comps_canon) == canonical_components,
            "P5_family_eligible": elig == "ELIGIBLE",
            "P6_no_unresolved_conflict": not unresolved,
            "P7_coverage_adequate_for_claim": located,
            "P8_endpoint_bound": t.get("endpoint_binding") == "named_endpoint_resolved_to_definition_span",
        }
        p9 = (span_target_mention(span, values, t.get("endpoint_definition_span"), canonical_components, context=document_neighbourhood(span, parsed))
              if all(x is not None for x in values) else {"state": "AMBIGUOUS_ENDPOINT_BINDING", "mention": "no effect tuple"})
        P["P9_span_target_mention"] = p9["state"] == "PASS"
        if pmid in selector_refusals:
            P["P1_source_bytes"] = False
        # estimand evidence: a stated field must reproduce at its offsets; a default must carry no span; no bare values
        ee_ok = True
        for fname, fv in ((br or {}).get("analysis_identity") or {}).items():
            if not isinstance(fv, dict) or "basis" not in fv:
                continue
            if fv["basis"] == "STATED_IN_OWNING_EVIDENCE":
                rep_text = normalize(parsed) if fv.get("parent_representation") == "NORMALIZED_SOURCE" else parsed
                if fv.get("start") is None or rep_text[fv["start"]:fv["end"]].strip() != (fv.get("span") or "").strip():
                    ee_ok = False
                    if not corrupt:
                        failures.append(f"ESTIMAND_EVIDENCE_MISMATCH {pmid}/{fname}: stated field does not reproduce at its offsets")
            elif fv["basis"] == "REGISTERED_DEFAULT" and fv.get("span"):
                ee_ok = False
                if not corrupt:
                    failures.append(f"ESTIMAND_EVIDENCE_MISMATCH {pmid}/{fname}: a REGISTERED_DEFAULT carries a span (a default rendered as a statement)")
        P["P10_estimand_evidence"] = ee_ok
        cil = ci_level_record(eff_clause, ((t.get("study_effect") or {}).get("standard_error")), t.get("ci_low"), t.get("ci_high"))
        P["P12_ci_level"] = cil["level_agreement"] != "MISMATCH"
        if cil["level_agreement"] == "MISMATCH" and not corrupt:
            failures.append(f"CI_LEVEL_MISMATCH {pmid}: the clause states a {cil['source_ci_pct']}% interval; the SE was derived at the 95% level (z {Z_ASSUMED_BY_DERIVATION})")
        # REVALIDATE ON LOAD: recompute the estimand bases from the source and compare with what the bundle recorded
        regd = bundle.get("registered_estimand") or {}
        ai = (br or {}).get("analysis_identity") or {}
        ee_re = estimand_evidence(parsed, eff_clause)
        basis_map = {"analysis_set": "analysis_set", "treatment_strategy": "analysis_window", "follow_up_window": "analysis_window", "estimator": "estimator", "comparator_direction": "contrast"}
        for fname, src in basis_map.items():
            fv = ai.get(fname)
            if isinstance(fv, dict) and fv.get("basis") in ("STATED_IN_OWNING_EVIDENCE", "REGISTERED_DEFAULT", "UNRESOLVED") and ee_re.get(src, {}).get("state") != fv.get("basis"):
                ee_ok = False
                if not corrupt:
                    failures.append(f"ESTIMAND_BASIS_DISAGREES {pmid}/{fname}: served basis {fv.get('basis')}, recomputed from the source {ee_re.get(src, {}).get('state')}")
        # P10 is a VALUE check, not a state check (lane OC): the ordered contrast and the estimator are recomputed from the tuple's own
        # clause and compared with the served values; the basis agreeing is necessary and not sufficient
        try:
            vocab = contrast_vocabulary(store.json(f"topics/{slug}.json"))
        except Refusal:
            vocab = {"experimental": [], "reference": []}      # no vocabulary: nothing orders, every STATED contrast refuses (fail closed)
        oc = ordered_contrast(eff_clause, values, vocab, fam_c)
        cv = contrast_value_check(br, oc, ee_re, vocab, regd)
        stated_copy = {k: (br or {}).get("effect", {}).get(k) for k in ("estimate", "ci_low", "ci_high")}
        if br and not corrupt and ([stated_copy[k] for k in ("estimate", "ci_low", "ci_high")] != values
                                   or scale_measure(br["effect"].get("scale")) != scale_measure(t.get("scale"))):
            cv["p10"].append(("ROW_EFFECT_COPIES_DISAGREE", f"bundle row {stated_copy} {br['effect'].get('scale')!r} vs rendered row {values} {t.get('scale')!r}"))
        # admission is computed and reported; it fails the VERDICT only where it contradicts what the bundle served (a row recorded
        # ADMISSIBLE) or under a declared plant -- a refusal the bundle already discloses is not a second defect (F4 lane's constraint:
        # publication eligibility must not collapse into scientific admission)
        contradicts_served = bool(corrupt) or (br or {}).get("admission", {}).get("final") == "ADMISSIBLE"
        for code, why in cv["p10"]:
            ee_ok = False
            if contradicts_served or code == "ROW_EFFECT_COPIES_DISAGREE":
                failures.append(f"{code} {pmid}: {why}")
            else:
                report.setdefault("disclosed_refusals", []).append(f"{code} {pmid}: {why}")
        P["P10_estimand_evidence"] = ee_ok
        # P11: the bound identity must be the REGISTERED one -- from the RECOMPUTED evidence
        dep = []
        if ee_re["analysis_set"]["state"] == "STATED_IN_OWNING_EVIDENCE" and ee_re["analysis_set"]["value"] != regd.get("analysis_set"):
            dep.append("analysis_set")
        if ee_re["analysis_window"]["state"] == "STATED_IN_OWNING_EVIDENCE" and ee_re["analysis_window"].get("value") == "on-treatment":
            dep.append("treatment_strategy")
        if ee_re["analysis_set"]["state"] == "UNRESOLVED" or ee_re["analysis_window"]["state"] == "UNRESOLVED":
            dep.append("UNRESOLVED")
        dep += cv["p11"]                                          # the registered contrast ("GLP-1 RA vs placebo") and estimator ("hazard ratio")
        P["P11_registered_estimand"] = not dep
        if dep and ((not corrupt and not cv["p11"]) or (cv["p11"] and contradicts_served)):
            failures.append(f"BOUND_TO_UNREGISTERED_ESTIMAND {pmid}: {dep}")
        elif dep and cv["p11"]:
            report.setdefault("disclosed_refusals", []).append(f"BOUND_TO_UNREGISTERED_ESTIMAND {pmid}: {dep}")
        report.setdefault("ordered_contrasts", {})[pmid] = {"recomputed": oc, "p10": [c for c, _ in cv["p10"]], "p11": cv["p11"],
                                                            "detail": cv["detail"], "pooled": cv["pooled"], "measure": cv["measure"]}
        csc = component_set_checks(t, comps_canon, canonical_components)
        P["P13_no_extra_components"] = csc["P13_no_extra_components"]
        P["P14_missing_components_consistent"] = csc["P14_missing_components_consistent"]
        if not P["P13_no_extra_components"] and not corrupt:
            failures.append(f"EXTRA_COMPONENT_IN_POOLED_ROW {pmid}: {csc['extra_components']} ({csc['pooled_state']})")
        if not P["P14_missing_components_consistent"] and not corrupt:
            failures.append(f"MISSING_COMPONENTS_UNRECORDED {pmid}: row lacks {csc['row_lacks']} while missing_components is []")
        failing = [k for k, ok in P.items() if not ok]
        final = ("ADMISSIBLE" if not failing else
                 "MIGRATION_STATE_UNBOUND_LEGACY" if failing == ["P8_endpoint_bound"] and t.get("endpoint_binding") == "unbound_legacy" else
                 "INADMISSIBLE")
        recorded = (br or {}).get("admission", {}).get("final")
        recorded_P = {k: v["state"] == "PASS" for k, v in ((br or {}).get("admission", {}).get("predicates") or {}).items()}
        span_code = span_state
        if not located and span and span_code is None:
            container_text = json.dumps(records, ensure_ascii=False)
            span_code = "SPAN_NOT_IN_RECORD" if (span in container_text or normalize(span) in normalize(container_text)) else "SPAN_NOT_IN_SOURCE"
            if not corrupt:
                failures.append(f"{span_code} {pmid}: " + ("the quotation occurs more than once and no offsets pin an occurrence" if span_code == "SPAN_LOCATION_AMBIGUOUS" else
                                f"the quotation is {'elsewhere in the container but' if span_code == 'SPAN_NOT_IN_RECORD' else 'not'} in the selected record's representation"))
        report["rows"].append({"pmid": pmid, "label": t.get("label"), "predicates": P, "final": final, "bundle_recorded": recorded,
                               "pooled_state": csc["pooled_state"], "component_sets": {k: csc[k] for k in ("row_components_canonical", "target_components_canonical", "extra_components", "missing_components", "row_lacks", "row_surplus")},
                               "revalidated_on_load": True, "served_state_trusted": False,
                               "p9": p9, "refusal": (selector_refusals[pmid].code if pmid in selector_refusals else
                                                     span_code if span_code else
                                                     p9["state"] if p9["state"] != "PASS" else None),
                               "agrees_with_bundle": (final == recorded) if not corrupt else None,
                               "predicates_agree_with_bundle": all(P.get(k) == recorded_P[k] for k in recorded_P) if not corrupt else None,
                               "span_match": loc["match"], "span_occurrences": loc.get("occurrences"), "offsets_reproduce_span": offsets_ok,
                               "clause_numbers": nums, "estimand_evidence_ok": ee_ok, "ci_level": cil,
                               "estimand_basis": {k: v.get("basis") for k, v in ((br or {}).get("analysis_identity") or {}).items() if isinstance(v, dict)}})
        if p9["state"] != "PASS" and not corrupt:
            failures.append(f"{p9['state']} {pmid}: {json.dumps(p9.get('witness'), ensure_ascii=False)[:160]}")
        if not corrupt and final != recorded:
            failures.append(f"ROW_VERDICT_DISAGREES {pmid}: verifier says {final}, bundle recorded {recorded}")

    # 4b. certificate pins: every analysis_code_blobs value is a 40-hex blob id or exactly the sentinel; the prose list of absences equals
    #     the sentinel set in BOTH directions -- a sentinel nothing validates is a string nobody checks
    pins = (cert.get("analysis_code_blobs") or {})
    bad_pins = {k: v for k, v in pins.items() if not (isinstance(v, str) and (re.fullmatch(r"[0-9a-f]{40}", v) or v == "NOT_PRESENT"))}
    sentinels = sorted(k for k, v in pins.items() if v == "NOT_PRESENT")
    declared_absent = sorted(((cert.get("certificate_scope") or {}).get("declared_but_absent")) or [])
    report["certificate_pins"] = {"entries": len(pins), "blob_ids": sum(1 for v in pins.values() if isinstance(v, str) and re.fullmatch(r"[0-9a-f]{40}", v)),
                                  "sentinels": sentinels, "declared_but_absent": declared_absent, "malformed": bad_pins,
                                  "rule": "value is ^[0-9a-f]{40}$ or exactly NOT_PRESENT; declared_but_absent == sentinel set (both directions)"}
    if bad_pins and not corrupt:
        failures.append(f"CERTIFICATE_PIN_MALFORMED: {bad_pins}")
    if sentinels != declared_absent and not corrupt:
        failures.append(f"CERTIFICATE_ABSENCE_UNDECLARED: sentinels {sentinels} vs declared_but_absent {declared_absent}")
    # 4c. execution record (when the release carries one): the bundle's review_files digest must match the served bytes, and the record's
    #     release identity must be THIS certificate's -- a swapped record fails either link
    rf = {f["file"]: f for f in bundle.get("review_files", [])}
    report["execution_record"] = {"present": "EXECUTION_RECORD.json" in rf}
    if "EXECUTION_RECORD.json" in rf:
        try:
            er_bytes = store.get(f"reviews/{slug}/EXECUTION_RECORD.json")
            er = json.loads(er_bytes.decode("utf-8"))
            digest_ok = sha256(er_bytes) == rf["EXECUTION_RECORD.json"]["sha256"]
            release_ok = (er.get("release") or {}).get("release_sha256") == cert.get("release_sha256")
            review_ok = (er.get("release") or {}).get("review_sha256") == cert.get("review_sha256")
            report["execution_record"].update({"sha256_matches_bundle": digest_ok, "release_sha256_matches_certificate": release_ok,
                                               "review_sha256_matches_certificate": review_ok,
                                               "generating_commit": (er.get("tree") or {}).get("generating_commit"), "tree_state": (er.get("tree") or {}).get("tree_state"),
                                               "dirty_other_paths": (er.get("tree") or {}).get("dirty_other_paths")})
            if not (digest_ok and release_ok and review_ok) and not corrupt:
                failures.append(f"EXECUTION_RECORD_MISMATCH: digest_ok={digest_ok} release_ok={release_ok} review_ok={review_ok}")
        except Refusal as r:
            report["execution_record"]["refusal"] = r.code
            if not corrupt:
                failures.append(f"EXECUTION_RECORD_UNREACHABLE: {r.code}")
    else:
        report["execution_record"]["meaning"] = "no record served: the generating tree of this release is UNRECORDED (true value, not reconstructed)"

    # 5. anchors: every document with a retained acquisition -- recompute preservation, compare to recorded coverage ----
    acq_by_pmid = {}
    report["anchors"] = []
    for d in bundle.get("documents", []):
        ac = (d.get("representations") or {}).get("ACQUIRED_SOURCE") or {}
        if d["document_id"].startswith("pubmed:") and ac.get("ref"):
            pmid = d["document_id"].split(":")[1]
            acq_by_pmid[pmid] = ac["ref"].removeprefix("docs/")
            xml_bytes = store.get(acq_by_pmid[pmid])
            xml_ok = sha256(xml_bytes) == ac.get("sha256_original")
            pres = preservation((rec_by_pmid.get(pmid) or {}).get("abstract") or "", xml_bytes)
            recorded = (d.get("coverage_status") or {}).get("value")
            recomputed = "COMPLETE_ABSTRACT" if pres["verdict"] == "PRESERVED" else "EXCERPT_ONLY"
            row = {"pmid": pmid, "acquired_xml_sha256_ok": xml_ok, "preservation": pres, "coverage_recomputed": recomputed,
                   "coverage_recorded": recorded, "agrees": recomputed == recorded}
            if anchor_live:
                row["live"] = live_anchor(pmid, xml_bytes, (rec_by_pmid.get(pmid) or {}).get("abstract") or "")
                if row["live"].get("units_in_live_not_in_retained") or row["live"].get("units_in_retained_not_in_live"):
                    row["live"]["discrepancy"] = "RECORDED (not attributed): live PubMed and the retained acquisition differ; see DateRevised"
            report["anchors"].append(row)
            if not xml_ok:
                failures.append(f"ANCHOR_XML_DIGEST_MISMATCH {pmid}: retained XML does not hash to ACQUIRED_SOURCE.sha256_original")
            if recomputed != recorded:
                failures.append(f"ANCHOR_PRESERVATION_FAILURE {pmid}: {pres['missing']} of {pres['units']} retained-XML abstract units MISSING from the cached "
                                f"abstract (extra chars {pres['extra_chars']}); coverage recomputed {recomputed} vs recorded {recorded} -- the cached "
                                f"abstract does not preserve the retained XML as the bundle claims")
    for c in bundle.get("absence_claims", []):
        pmid = c["trial"]["id"].replace("PMID ", "")
        row = {"outcome": c["outcome"], "pmid": pmid, "producer_state": c["producer_state"], "claim_kind": c["claim_kind"]}
        if c["claim_kind"] == "NEGATIVE" and pmid in acq_by_pmid:
            pres = preservation((rec_by_pmid.get(pmid) or {}).get("abstract") or "", store.get(acq_by_pmid[pmid]))
            coverage = "COMPLETE_ABSTRACT" if pres["verdict"] == "PRESERVED" else "EXCERPT_ONLY"
            admissible = coverage == "COMPLETE_ABSTRACT"
            row.update({"preservation": pres, "coverage_recomputed": coverage, "negative_claim_admissible": admissible,
                        "bundle_recorded": c["negative_claim_admissible"], "agrees": admissible == c["negative_claim_admissible"]})
            if admissible != c["negative_claim_admissible"]:
                failures.append(f"ABSENCE_CLAIM_DISAGREES {pmid}/{c['outcome']}: verifier {admissible} vs bundle {c['negative_claim_admissible']}")
        elif c["claim_kind"] == "NEGATIVE":
            row.update({"coverage_recomputed": "UNKNOWN_COMPLETENESS", "negative_claim_admissible": False, "bundle_recorded": c["negative_claim_admissible"]})
        report["absence_claims"].append(row)

    # 5b. regulatory facts: every candidate analysis located; the decision's tuple bound to the claimed identity -------
    report["regulatory_facts"] = []
    for rf in bundle.get("regulatory_facts", []):
        try:
            text = store.get(rf["document"]["parsed_ref"]).decode("utf-8", "replace")
        except Refusal as r:
            failures.append(f"{r.code} {r.detail}"); continue
        found = {}
        for a in rf["candidate_analyses"]:
            loc = locate(a["text"], text)
            state = loc["match"]
            if state == "NOT_LOCATED":   # a linearised table span: locate its pieces
                pieces = [x.strip() for x in a["text"].split("|") if x.strip()]
                if len(pieces) >= 2:
                    n = sum(1 for pc in pieces if locate(pc, text)["match"] != "NOT_LOCATED")
                    state = f"PARTIAL_TABLE_BINDING {n}/{len(pieces)} pieces" if n else "NOT_LOCATED"
            flat = a["text"].replace("\n", " ")
            words = {("on-treatment" if "treatment" in m.lower() else "on-study (ITT)") for m in re.findall(r"on-?\s?study|on-?\s?treatment|end of study|\bEOS\b", flat, re.I)}
            recomputed = (next(iter(words)) if len(words) == 1 else "UNRESOLVED" if len(words) > 1 else None)
            served = a["analysis_identity"]["treatment_strategy"]
            ev_state = (a.get("strategy_evidence") or {}).get("state")
            if recomputed is None and ev_state in ("BOUND_VIA_COUNTS", "BOUND_VIA_ROUNDING"):
                # inherited from a labelled candidate: revalidate the inheritance -- the cited labelled span must exist and carry that strategy
                cited = (a.get("strategy_evidence") or {}).get("labelled_span") or ""
                recomputed = served if cited and ("treatment" in cited.lower()) == ("treatment" in served.lower()) else "UNRESOLVED"
            strategy = recomputed if recomputed is not None else served if ev_state == "REGISTERED_DEFAULT" else "UNRESOLVED"
            if recomputed is not None and recomputed != served and not corrupt:
                failures.append(f"IDENTITY_REVALIDATION_DISAGREES {rf['trial']}/{a['kind']}: served strategy {served!r}, recomputed from the span {recomputed!r}")
            found[a["kind"]] = {"located": state, "strategy": strategy, "served_strategy": served, "endpoint": a["analysis_identity"]["endpoint"]}
        eff = rf["decision"]["effect"]
        etoks = [str(eff.get("estimate")), str(eff.get("ci_low")), str(eff.get("ci_high"))]
        claimed = rf["decision"]["claimed_treatment_strategy"]
        claimed_ep = rf["decision"].get("claimed_endpoint")

        def _holds(a):
            flat = normalize(a["text"])
            return all(tok in flat for tok in etoks)
        holders = [a["kind"] for a in rf["candidate_analyses"] if _holds(a)]
        holder_ids = {(found[k]["strategy"], found[k]["endpoint"]) for k in holders}
        regd = bundle.get("registered_estimand") or {}
        if len(holder_ids) > 1:
            code = "AMBIGUOUS"
        elif not holders:
            code = "TUPLE_NOT_IN_ANY_CANDIDATE_SPAN"
        elif holder_ids <= {(claimed, claimed_ep)} or (claimed == "UNSTATED" and {h[1] for h in holder_ids} <= {claimed_ep} and {h[0] for h in holder_ids} <= {"UNSTATED", regd.get("treatment_strategy")}):
            code = "BOUND" if claimed in (regd.get("treatment_strategy"), "UNSTATED") else "BOUND_TO_UNREGISTERED_ESTIMAND"
        else:
            code = "ANALYSIS_IDENTITY_MISMATCH"
        keys = {a["analysis_identity"]["analysis_identity_key"] for a in rf["candidate_analyses"]}
        report["regulatory_facts"].append({"trial": rf["trial"], "candidates": found, "decision_tuple_holders": holders, "claimed_strategy": claimed,
                                           "binding": code, "bundle_recorded": rf["tuple_to_identity_binding"], "distinct_identity_keys": len(keys),
                                           "distinguishable": len(keys) >= 2 and all(f["located"] != "NOT_LOCATED" for f in found.values())})
        if any(f["located"] == "NOT_LOCATED" for f in found.values()):
            failures.append(f"REGULATORY_SPAN_NOT_LOCATED {rf['trial']}: " + ", ".join(k for k, f in found.items() if f["located"] == "NOT_LOCATED"))
        partial = [k for k, f in found.items() if str(f["located"]).startswith("PARTIAL")]
        if partial:
            report.setdefault("partial_table_bindings", []).append({"trial": rf["trial"], "kinds": partial,
                                                                    "note": "a linearised table span located piece-wise; recorded as a partial binding, not refused"})
        if code != "BOUND":
            failures.append(f"{code} {rf['trial']}: decision tuple {etoks} claims ({claimed}, {claimed_ep}); found in {holders} ({sorted(holder_ids)})"
                            + ("; competing candidates carried" if code == "AMBIGUOUS" else ""))
        elif code != rf["tuple_to_identity_binding"] and not corrupt:
            failures.append(f"ROW_VERDICT_DISAGREES regulatory {rf['trial']}: verifier {code} vs bundle {rf['tuple_to_identity_binding']}")

    # 6. pool ------------------------------------------------------------------------------------------------------
    inputs = bundle["pooled_reference"]["inputs"]
    exp = bundle["pooled_reference"]["expected"]
    # pool() takes log(effect) of whatever it is given: the measure is identified and single, and every input is its row's tuple in the
    # pooled orientation, BEFORE any log is taken (lane OC); a refused pool is not computed at all
    mg = pool_measure_guard(inputs, report.get("ordered_contrasts") or {}, bundle["pooled_reference"].get("scale"))
    report["pool_measure_guard"] = mg
    for code, why in mg["refusals"]:
        failures.append(f"{code} {why}")
    got = pool(inputs) if not mg["refused"] else None
    deltas = {k: abs(got[k] - exp[k]) for k in ("estimate", "ci_low", "ci_high", "tau2")} if got else {}
    pool_ok = bool(got) and all(d < 1e-9 for d in deltas.values())
    adm = [i for i in inputs if any(r["pmid"] == i["id"].replace("PMID ", "") and r["final"] == "ADMISSIBLE" for r in report["rows"])]
    report["binding_states"] = {"rendered_rows": [], "migration_state_unbound_legacy": 0}
    for o in review.get("outcomes", []):
        for t in o.get("trials", []):
            b = t.get("endpoint_binding")
            cls = "BOUND" if b == "named_endpoint_resolved_to_definition_span" else "MIGRATION_STATE_UNBOUND_LEGACY" if b == "unbound_legacy" else "OTHER"
            report["binding_states"]["rendered_rows"].append({"outcome": o["name"], "id": t.get("id"), "binding_class": cls})
            report["binding_states"]["migration_state_unbound_legacy"] += (cls == "MIGRATION_STATE_UNBOUND_LEGACY")
    report["binding_states"]["migration_rows_counted_admissible"] = sum(
        1 for r in report["rows"] if r["final"] == "MIGRATION_STATE_UNBOUND_LEGACY")  # by construction never in admissible set
    report["pool"] = {"k_declared": len(inputs), "recomputed": got, "declared": exp, "abs_deltas": deltas, "reproduced_to_1e-9": pool_ok,
                      "t_crit_recomputed": got["t_crit"] if got else None, "admissible_rows": len(adm),
                      "admissible_only_pool_for_information": pool(adm) if got and len(adm) >= 2 and len(adm) != len(inputs) else None,
                      "refused_before_logs": [c for c, _ in mg["refusals"]] or None,
                      "note": "the declared pool is the page's; admissible_only_pool is a verifier sensitivity, not a replacement result"}
    if got and not pool_ok:
        failures.append(f"POOL_NOT_REPRODUCED {deltas}")

    report["endpoint_compatibility"] = {"state": (bundle.get("endpoint_compatibility") or {}).get("state"),
                                        "per_trial": {k: v["value"] for k, v in ((bundle.get("endpoint_compatibility") or {}).get("per_trial") or {}).items()}}
    report["statistical_input"] = {r["trial"]["id"]: {"interval_construction": r["statistical_input"]["interval_construction"],
                                                      "se_source": r["statistical_input"]["se_source"],
                                                      "approximation_appropriate": r["statistical_input"]["approximation_appropriate"]}
                                   for r in bundle["verification_rows"] if "statistical_input" in r}
    report["not_checked"] = ["upstream fidelity of any representation", "completeness of the source set", "clinical interpretation",
                             "appropriateness of CI-to-SE conversions for non-Wald intervals", "the production admission path"]
    report["failures"] = failures
    report["verdict"] = "PASS" if not failures else "FAIL"
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description="stdlib verifier for a served evidence bundle")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--root", help="directory mirroring the site root (e.g. docs)")
    g.add_argument("--url", help="site root URL")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--corrupt", nargs=2, metavar=("PMID", "LIMB"), help="mutate one limb of one row in memory: span|effect|components|eligibility|conflict|binding|nontarget_span|unlisted_span|fragment|ci_high_rounded|ci_low_truncated|duplicate_span_no_offsets|default_as_statement|served_basis_lie|regulatory_strategy_swap|regulatory_consistent_swap|container|contrast_reverse|contrast_reverse_served|contrast_reverse_declared[_permitted|_forbidden|_away]|estimator_swap|measure_unidentified|pool_input_reciprocal")
    ap.add_argument("--anchor", choices=["live"], help="live: re-fetch EFetch XML from PubMed now and compare to the retained acquisition and the cached abstract")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:  # the report carries source text (thin spaces, middle dots); a cp1252 console must not turn a verdict into a crash
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    store = Store(a.root, a.url)
    try:
        rep = run(store, a.slug, tuple(a.corrupt) if a.corrupt else None, anchor_live=(a.anchor == "live"))
    except Refusal as r:
        rep = {"slug": a.slug, "verdict": "REFUSED", "refusal_code": r.code, "detail": r.detail, "failures": [f"{r.code} {r.detail}"],
               "note": "the verifier could not complete; this is a verdict, not a crash"}
        print(json.dumps(rep, indent=1, ensure_ascii=False) if a.json else f"verdict REFUSED  {r.code}: {r.detail}")
        return 1
    except Exception as e:  # noqa: BLE001 -- a validator that crashes only when it has something to say looks like a clean corpus
        rep = {"slug": a.slug, "verdict": "REFUSED", "refusal_code": "VERIFIER_INTERNAL_ERROR", "detail": f"{type(e).__name__}: {str(e)[:300]}",
               "failures": [f"VERIFIER_INTERNAL_ERROR {type(e).__name__}: {str(e)[:300]}"]}
        print(json.dumps(rep, indent=1, ensure_ascii=False) if a.json else f"verdict REFUSED  VERIFIER_INTERNAL_ERROR: {type(e).__name__}: {e}")
        return 1
    if a.json:
        print(json.dumps(rep, indent=1, ensure_ascii=False))
    else:
        print(f"bundle schema {rep['schema_version']}  verdict {rep['verdict']}")
        print(f"artefacts ok: {sum(1 for x in rep['artefacts'] if x.get('bytes_ok') and x.get('declared_digest_ok'))}/{sum(1 for x in rep['artefacts'] if 'bytes_ok' in x)}"
              f"  supporting ok: {sum(1 for x in rep['supporting'] if x['ok'])}/{len(rep['supporting'])}  certificate: {rep['certificate']}")
        for r in rep["rows"]:
            fails = [k for k, v in r["predicates"].items() if not v]
            print(f"  row {r['pmid']:>9} {r['final']:<12} {'(bundle: ' + str(r['bundle_recorded']) + ')':<24} span={r['span_match']:<11} fails={fails}")
        for c in rep["absence_claims"]:
            if c["claim_kind"] == "NEGATIVE":
                print(f"  absence {c['pmid']} {c['outcome'][:36]:<36} coverage={c.get('coverage_recomputed')} negative_claim_admissible={c.get('negative_claim_admissible')}")
        p = rep["pool"]
        if p["recomputed"] is None:
            print(f"pool k={p['k_declared']}: REFUSED before any log was taken {p['refused_before_logs']}  admissible rows {p['admissible_rows']}")
        else:
            print(f"pool k={p['k_declared']}: recomputed {p['recomputed']['estimate']:.16f} ({p['recomputed']['ci_low']:.16f}-{p['recomputed']['ci_high']:.16f}) "
                  f"tau2 {p['recomputed']['tau2']:.16e}  reproduced_to_1e-9={p['reproduced_to_1e-9']}  admissible rows {p['admissible_rows']}")
        print(f"endpoint_compatibility {rep['endpoint_compatibility']['state']} {rep['endpoint_compatibility']['per_trial']}")
        print("statistical_input: " + "; ".join(f"{k}={v['interval_construction']}" for k, v in rep["statistical_input"].items() if v["interval_construction"] != "UNSTATED_IN_HELD_REPRESENTATION") + " (others UNSTATED_IN_HELD_REPRESENTATION; all SE DERIVED_FROM_CI)")
        for an in rep.get("anchors", []):
            live = an.get("live")
            extra = (f" live: fetched={live.get('fetched')} equal_bytes={live.get('live_equals_retained_bytes')} "
                     f"revised live={live.get('live_date_revised')} retained={live.get('retained_date_revised')} "
                     f"units +{len(live.get('units_in_live_not_in_retained', []))}/-{len(live.get('units_in_retained_not_in_live', []))} "
                     f"live_units_missing_from_cache={live.get('live_units_missing_from_cached_abstract')}") if live else ""
            print(f"  anchor {an['pmid']} xml_ok={an['acquired_xml_sha256_ok']} preservation={an['preservation']['verdict']} "
                  f"({an['preservation']['preserved']}/{an['preservation']['units']}) coverage {an['coverage_recomputed']} recorded {an['coverage_recorded']}{extra}")
        bs = rep["binding_states"]
        print(f"binding: {bs['migration_state_unbound_legacy']} rendered row(s) UNBOUND_LEGACY = migration state, not admissible, not refused: "
              + ", ".join(f"{r['id']} ({r['outcome'][:28]})" for r in bs["rendered_rows"] if r["binding_class"] != "BOUND"))
        for rf in rep.get("regulatory_facts", []):
            print(f"  regulatory {rf['trial']}: candidates {len(rf['candidates'])} located, distinct identity keys {rf['distinct_identity_keys']}, "
                  f"distinguishable={rf['distinguishable']}, decision tuple -> {rf['decision_tuple_holders']} binding {rf['binding']}")
        print("NOT checked: " + "; ".join(rep["not_checked"]))
        if rep["corruption"]:
            print(f"corruption {rep['corruption']}: rows no longer ADMISSIBLE = {[(r['pmid'], r['final']) for r in rep['rows'] if r['final'] != 'ADMISSIBLE']}")
        for f in rep["failures"]:
            print("  FAIL:", f)
    return 0 if rep["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
