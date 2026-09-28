"""Typed identity of an endpoint COMPONENT: a name plus typed parameters, never a name with a string suffix.

finerenone review (hash 00a2b7e4...): the canonical check reported HETEROGENEOUS for FIDELIO vs FIGARO
(SUSTAINED_40_EGFR_DECLINE vs SUSTAINED_EGFR_DECLINE), yet both trials define the component as a sustained decrease of at
least 40% in the eGFR. One reader kept '40%' inside the component STRING, the other dropped it, and the check compared the
strings. A threshold is a PARAMETER of the component:

    eGFR decline   -> {"name": "EGFR_DECLINE", "params": {"threshold_pct": 40, "threshold_op": "ge", "sustained": True,
                                                          "sustained_days": 28}}
    'eGFR < 15'    -> {"name": "EGFR_BELOW", "params": {"threshold_ml_min": 15}}
    kidney failure -> {"name": "KIDNEY_FAILURE", "params": {"egfr_below_ml_min": 15, "includes_dialysis": True, ...}}

Two components are the same when their names agree and every parameter stated on BOTH sides agrees. A parameter one side
does not state is UNRESOLVED -- disclosed, never counted as a difference (a lost qualifier must not raise a false
heterogeneity warning); a parameter both sides state differently (40% vs 57%, >= vs >, sustained vs not) IS a difference.

A threshold is read only where it is grammatically ATTACHED to the eGFR decline ('decline in eGFR of at least 40%', '40%
decline in eGFR', 'eGFR decline of >=40%', 'decrease from baseline of at least 40% in the eGFR') -- never 'in 40% of
patients' or 'a 30% reduction in UACR' elsewhere in the sentence (NR-C16). A parameter the component phrase does not carry
is read, by the same rule, from the row's OWN definition sentence, never from another trial or from the topic.
"""
from __future__ import annotations

import re
from typing import Any

_NUMWORDS = {"twenty": 20, "twenty-five": 25, "thirty": 30, "thirty-three": 33, "forty": 40, "forty-five": 45,
             "fifty": 50, "fifty-seven": 57, "sixty": 60, "seventy": 70}
_NUM = r"(?P<n>\d{1,2}(?:\.\d)?|" + "|".join(sorted((k.replace("-", r"[\s-]") for k in _NUMWORDS), key=len, reverse=True)) + ")"
_PCT = _NUM + r"\s*(?:%|percent\b|per\s+cent\b)"
_OP = r"(?P<op>>=|≥|=>|at\s+least|of\s+at\s+least|>|greater\s+than|more\s+than)?\s*"
_DECL = r"(?:decline|decrease|reduction|fall|drop|loss)"
_EGFR = r"(?:the\s+)?egfr\b"
_GAP = r"[^.;%]{0,90}?"
_DECLINE_FORMS = [
    # decline in eGFR (from baseline) of at least 40%
    re.compile(_DECL + r"\s+(?:in|of)\s+" + _EGFR + _GAP + r"\b(?:of|by)?\s*" + _OP + _PCT, re.I),
    # (at least) 40% (or more) (sustained) decline in eGFR
    re.compile(_OP + _PCT + r"(?P<more>\s+or\s+(?:more|greater))?\s+(?:[a-z-]+\s+){0,2}?" + _DECL + r"\s+(?:in|of)\s+"
               + _EGFR, re.I),
    # eGFR decline of at least 40% / eGFR decline >40% / eGFR decline from the baseline value ... of at least 40%
    re.compile(_EGFR + r"\s+" + _DECL + r"\s+(?:of\s+|by\s+)?" + _OP + _PCT, re.I),
    re.compile(_EGFR + r"\s+" + _DECL + _GAP + r"\b(?:of|by)\s+" + _OP + _PCT, re.I),
    # (sustained) 40% (or more) eGFR decline
    re.compile(_OP + _PCT + r"(?P<more3>\s+or\s+(?:more|greater))?\s+(?:[a-z-]+\s+){0,2}?egfr\s+" + _DECL, re.I),
    # decrease (from baseline) of at least 40% in the eGFR
    re.compile(_DECL + _GAP + r"\b(?:of|by)\s+" + _OP + _PCT + r"(?P<more2>\s+or\s+more)?\s+(?:in|of)\s+" + _EGFR, re.I),
]
_EGFR_DECLINE = re.compile(r"\begfr\b.{0,60}?\b" + _DECL + r"\b|\b" + _DECL + r"\b.{0,60}?\begfr\b", re.I | re.S)
_EGFR_BELOW = re.compile(r"\begfr\s*(?:of\s*)?(?:<|less\s+than|below|under|lower\s+than)\s*(\d{1,3})\b", re.I)
_NOT_SUSTAINED = re.compile(r"\b(?:not\s+sustained|unsustained|non-?sustained|transient|single\s+measurement)\b", re.I)
_SUSTAINED = re.compile(r"\b(?:sustained|confirmed|persistent)\b", re.I)
_SUSTAINED_FOR = re.compile(r"\b(?:sustained|confirmed|persist\w*)\s+(?:for\s+)?(?:at\s+least\s+|>=\s*|≥\s*)?"
                            r"(\d{1,3})\s*(day|week|month)s?\b", re.I)
_KIDNEY_FAILURE = re.compile(r"\b(?:kidney|renal)\s+failure\b|\bend[\s-]stage\s+(?:kidney|renal)\b|\besk?rd\b", re.I)
_DIALYSIS = re.compile(r"\bdialysis\b|\b(?:kidney|renal)[\s-]replacement\b", re.I)
_TRANSPLANT = re.compile(r"\btransplant", re.I)
_DEFINED = re.compile(r"\bdefined\s+as\b|\(|:", re.I)
_UNITS = {"day": 1, "week": 7, "month": 30}


def _norm(text: str | None) -> str:
    """Also reads a registered CODE ('SUSTAINED_EGFR_DECLINE_GE_40_PERCENT') as the phrase it stands for."""
    s = (text or "").replace("e-gfr", "egfr").replace("eGFR", "egfr")
    if "_" in s and " " not in s.strip():
        s = re.sub(r"\bPERCENT\b", "%", s.replace("_", " "), flags=re.I)
        s = re.sub(r"\bGE\s+(\d)", r">= \1", s, flags=re.I)
        s = re.sub(r"\bGT\s+(\d)", r"> \1", s, flags=re.I)
        s = re.sub(r"\bLT\s+(\d)", r"< \1", s, flags=re.I)
        # a code is a component NAME followed by its threshold: 'SUSTAINED EGFR DECLINE >= 40 %' -> '... decline of >= 40%'
        s = re.sub(r"(decline|decrease|reduction)\s+(>=|>|<)", r"\1 of \2", s, flags=re.I)
    return re.sub(r"\s+", " ", s).strip()


def _token(text: str | None) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", str(text or "").upper()).strip("_") or "UNSPECIFIED_COMPONENT"


def _number(s: str) -> float | int:
    s = re.sub(r"[\s-]+", "-", s.lower())
    if s in _NUMWORDS:
        return _NUMWORDS[s]
    v = float(s)
    return int(v) if v.is_integer() else v


def _op(m: re.Match[str]) -> str | None:
    op = re.sub(r"\s+", " ", (m.group("op") or "").lower()).strip()
    more = any(g in m.groupdict() and m.group(g) for g in ("more", "more2", "more3"))
    if op in (">=", "≥", "=>", "at least", "of at least") or more:
        return "ge"
    if op in (">", "greater than", "more than"):
        return "gt"
    return None


def _egfr_decline_params(s: str) -> dict[str, Any]:
    """Parameters of the eGFR decline stated in `s`, read only from phrases attached to it."""
    params: dict[str, Any] = {}
    hits = [(m, _number(m.group("n")), _op(m)) for rx in _DECLINE_FORMS for m in rx.finditer(s)]
    values = {v for _, v, _ in hits}
    if len(values) == 1:
        params["threshold_pct"] = values.pop()
        ops = {o for _, _, o in hits if o}
        if len(ops) == 1:
            params["threshold_op"] = ops.pop()
    m = _EGFR_DECLINE.search(s)
    window = s[max(0, (m.start() if m else 0) - 40):(m.end() if m else len(s)) + 60] if m else s
    if _NOT_SUSTAINED.search(window):
        params["sustained"] = False
    elif _SUSTAINED.search(window):
        params["sustained"] = True
        d = _SUSTAINED_FOR.search(window)
        if d:
            params["sustained_days"] = int(d.group(1)) * _UNITS[d.group(2).lower()]
    return params


def _kidney_failure_params(s: str) -> dict[str, Any]:
    """A kidney-failure component DEFINED in the phrase ('kidney failure defined as eGFR <15 or maintenance dialysis') has
    its definition as parameters; an undefined 'kidney failure' has none (unresolved, not different)."""
    if not _DEFINED.search(s):
        return {}
    params: dict[str, Any] = {}
    below = _EGFR_BELOW.search(s)
    if below:
        params["egfr_below_ml_min"] = int(below.group(1))
    params["includes_dialysis"] = bool(_DIALYSIS.search(s))
    params["includes_transplant"] = bool(_TRANSPLANT.search(s))
    return params


def identity(component: str | None, definition_span: str | None = None) -> dict[str, Any]:
    """{'name': ..., 'params': {...}} for one component phrase; parameters missing from the phrase are read, by the same
    attached-phrase rule, from the row's own definition sentence."""
    s = _norm(component).lower()
    if _KIDNEY_FAILURE.search(s):
        return {"name": "KIDNEY_FAILURE", "params": _kidney_failure_params(s)}
    below = _EGFR_BELOW.search(s)
    if below and not _EGFR_DECLINE.search(s):
        return {"name": "EGFR_BELOW", "params": {"threshold_ml_min": int(below.group(1))}}
    if _EGFR_DECLINE.search(s) or any(rx.search(s) for rx in _DECLINE_FORMS):
        params = _egfr_decline_params(s)
        span = _norm(definition_span).lower()
        if span:
            for k, v in _egfr_decline_params(span).items():
                params.setdefault(k, v)
        return {"name": "EGFR_DECLINE", "params": params}
    return {"name": _token(component), "params": {}}


def identities(components, definition_span: str | None = None) -> list[dict[str, Any]]:
    out = {}
    for c in components or []:
        ident = identity(str(c), definition_span)
        prev = out.get(ident["name"])
        if prev is None:
            out[ident["name"]] = ident
        else:                                   # the same component named twice: merge what each states
            for k, v in ident["params"].items():
                prev["params"].setdefault(k, v)
    return [out[k] for k in sorted(out)]


def compare(a: list[dict[str, Any]], b: list[dict[str, Any]]) -> dict[str, Any]:
    """{'same': bool, 'differences': [...], 'unresolved': [...]} for two component identity lists."""
    pa, pb = {x["name"]: x["params"] for x in a}, {x["name"]: x["params"] for x in b}
    if set(pa) != set(pb):
        return {"same": False, "differences": [{"names": sorted(set(pa) ^ set(pb))}], "unresolved": []}
    diffs, unresolved = [], []
    for name in sorted(pa):
        for key in sorted(set(pa[name]) | set(pb[name])):
            if key in pa[name] and key in pb[name]:
                if pa[name][key] != pb[name][key]:
                    diffs.append({"component": name, "parameter": key, "values": [pa[name][key], pb[name][key]]})
            else:
                unresolved.append({"component": name, "parameter": key,
                                   "stated": pa[name].get(key, pb[name].get(key))})
    return {"same": not diffs, "differences": diffs, "unresolved": unresolved}
