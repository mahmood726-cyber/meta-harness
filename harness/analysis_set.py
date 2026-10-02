"""ANALYSIS SET of each count pair a trial report states for an outcome, and which one a comparator's printed row
reproduces (lane G1, colchicine-postop-af).

COPPS-2 (PMID 25172965) states postoperative AF twice, for two analysis sets:
  all randomised  '... postoperative AF (colchicine, 61 patients [33.9%]; placebo, 75 patients [41.7%]; ...)'
                  with 'placebo (n=180) or colchicine (...; n=180)'                    -> RR 0.81 (0.62-1.07)
  on-treatment    '... a reduction in postoperative AF in the prespecified on-treatment analysis
                  (placebo, 61/148 patients [41.2%]; colchicine, 38/141 patients [27.0%] ...)'  -> RR 0.65 (0.47-0.91)
Our registered estimand is ITT, so we pool the first; the comparator printed RR 0.66 (0.45-0.96). Which held analysis
set a printed row comes from is a typed, checkable question, never a guess: a set REPRODUCES the row only when its RR
and both CI limits round to the printed values at the printed precision; otherwise the NEAREST set is reported as
nearest, and the row stays unreproduced.
"""
from __future__ import annotations

import math
import re
from typing import Any

RULE_ID = "analysis_set:labelled_counts_v1"

# 'placebo (n=180)', 'colchicine (0.5 mg twice daily ...; n=180)': an arm's randomised size
_ARM_N = re.compile(r"\b(?P<arm>[A-Za-z][\w-]{2,40})\s*\((?:[^()]{0,200}?[;,]\s*)?n\s*=\s*(?P<n>\d{1,6})\)", re.I)
# 'colchicine, 61 patients' / 'placebo, 61/148 patients': one arm's events (and n) inside a count group
_COUNT = re.compile(r"(?:^|[;(]\s*)(?P<arm>[A-Za-z][\w-]{2,40}),\s*(?P<e>\d{1,6})(?:\s*/\s*(?P<n>\d{1,6}))?\s+"
                    r"(?:patients|participants|subjects)\b", re.I)
# the analysis set named in the clause before a count group
_SET = re.compile(r"\b(?P<set>on[-\s]treatment|per[-\s]protocol|as[-\s]treated|modified\s+intention[-\s]to[-\s]treat|"
                  r"intention[-\s]to[-\s]treat|mITT|ITT|completers?)\b", re.I)
_PAREN = re.compile(r"\(([^()]*)\)")
_SENT = re.compile(r"(?<=[.;])\s+(?=[A-Z])")
_WS = re.compile(r"\s+")

_CANON = {"on-treatment": "on-treatment", "on treatment": "on-treatment", "per-protocol": "per-protocol",
          "per protocol": "per-protocol", "as-treated": "as-treated", "as treated": "as-treated",
          "intention-to-treat": "intention-to-treat", "intention to treat": "intention-to-treat",
          "itt": "intention-to-treat", "mitt": "modified intention-to-treat", "completer": "completers",
          "completers": "completers"}
ALL_RANDOMISED = "all randomised (no analysis set named)"


_FOLD = str.maketrans({c: " " for c in "()[]{};:,.!?/\"'"})


def _names_outcome(text: str, terms) -> bool:
    """A whole-word occurrence of any outcome term (no pattern is built from the terms: 'AF' is not in 'after')."""
    if not terms:
        return True
    padded = " " + _WS.sub(" ", (text or "").lower().translate(_FOLD)) + " "
    return any(" " + _WS.sub(" ", t.lower().translate(_FOLD)).strip() + " " in padded for t in terms if t and t.strip())


def _canon(label: str) -> str:
    low = _WS.sub(" ", label.lower()).replace("-", " ")
    if low.startswith("modified"):
        return "modified intention-to-treat"
    return _CANON.get(low, _CANON.get(low.replace(" ", "-"), low))


def _matches(arm: str, terms) -> bool:
    a = arm.lower()
    return any(t.lower() in a or a in t.lower() for t in terms if t)


def labelled_counts(text: str, treat_terms, ctrl_terms, outcome_terms) -> list[dict[str, Any]]:
    """Every count group stating the outcome for one treatment arm and one control arm, with its analysis set."""
    text = _WS.sub(" ", text or "")
    sizes: dict[str, int] = {}
    for m in _ARM_N.finditer(text):
        sizes.setdefault(m.group("arm").lower(), int(m.group("n")))
    out = []
    for sent in _SENT.split(text):
        prev_end = 0
        for g in _PAREN.finditer(sent):
            lead = sent[prev_end:g.start()]
            prev_end = g.end()
            arms = {}
            for c in _COUNT.finditer(g.group(1)):
                role = "t" if _matches(c.group("arm"), treat_terms) else "c" if _matches(c.group("arm"), ctrl_terms) else None
                if role and role not in arms:
                    n = int(c.group("n")) if c.group("n") else sizes.get(c.group("arm").lower())
                    arms[role] = {"arm": c.group("arm"), "events": int(c.group("e")), "n": n}
            if set(arms) != {"t", "c"} or not _names_outcome(lead, outcome_terms):
                continue
            lab = list(_SET.finditer(lead))
            label = _canon(lab[-1].group("set")) if lab else ALL_RANDOMISED
            out.append({"analysis_set": label, "treatment": arms["t"], "control": arms["c"],
                        "span": (lead[-160:] + "(" + g.group(1) + ")").strip(), "rule_id": RULE_ID})
    return out


# 'randomized, 69 to the control group and 71 to the colchicine group': arm sizes stated as 'N to the X group'
_N_TO_GROUP = re.compile(r"\b(?P<n>\d{1,6})\s+to\s+the\s+(?P<arm>[A-Za-z][\w-]{2,40})\s+group\b", re.I)
# '(7.04% versus 13.04%, respectively' / '7.04% vs 13.04%': a percentage pair for two arms
_PCT_PAIR = re.compile(r"(?P<p1>\d{1,3}(?:\.\d{1,3})?)\s*%\s*(?:versus|vs\.?|and)\s*(?P<p2>\d{1,3}(?:\.\d{1,3})?)\s*%", re.I)


def percent_back_calculation(text: str, treat_terms, ctrl_terms, outcome_terms) -> dict[str, Any] | None:
    """Whole-number counts implied by an outcome's PERCENTAGE pair and the arms' stated sizes, accepted only when exactly
    one assignment of the two percentages to the two arms gives integers that round back to BOTH printed percentages at
    their printed precision (Zarpelon 27223641: 7.04% of 71 = 5, 13.04% of 69 = 9; the swapped assignment fails)."""
    text = _WS.sub(" ", text or "")
    sizes = {}
    for m in _N_TO_GROUP.finditer(text):
        role = "t" if _matches(m.group("arm"), treat_terms) else "c" if _matches(m.group("arm"), ctrl_terms) else None
        if role:
            sizes.setdefault(role, int(m.group("n")))
    if set(sizes) != {"t", "c"}:
        return None
    for sent in _SENT.split(text):
        m = _PCT_PAIR.search(sent)
        if not m or not _names_outcome(sent, outcome_terms):
            continue
        ok = []
        for pt, pc in ((m.group("p1"), m.group("p2")), (m.group("p2"), m.group("p1"))):
            et, ec = round(float(pt) / 100 * sizes["t"]), round(float(pc) / 100 * sizes["c"])
            if _same_at_printed(100 * et / sizes["t"], pt) and _same_at_printed(100 * ec / sizes["c"], pc):
                ok.append((et, ec, pt, pc))
        if len(ok) == 1:
            et, ec, pt, pc = ok[0]
            return {"treatment": {"events": et, "n": sizes["t"], "printed_pct": pt},
                    "control": {"events": ec, "n": sizes["c"], "printed_pct": pc}, "span": sent[:300],
                    "basis": "the only assignment whose whole counts round back to both printed percentages",
                    "rule_id": "analysis_set:percent_back_calculation_v1"}
        return {"state": "AMBIGUOUS" if ok else "NO_EXACT_COUNTS", "span": sent[:300]}
    return None


def rr_ci(et: int, nt: int, ec: int, nc: int) -> tuple[float, float, float] | None:
    """Risk ratio and its 95% CI on the log scale; 0.5 added only when a cell is zero."""
    if not all(isinstance(x, int) for x in (et, nt, ec, nc)) or nt <= 0 or nc <= 0:
        return None
    a, b, c, d = et, nt - et, ec, nc - ec
    if 0 in (a, b, c, d):
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    rr = (a / (a + b)) / (c / (c + d))
    se = math.sqrt(1 / a - 1 / (a + b) + 1 / c - 1 / (c + d))
    return rr, math.exp(math.log(rr) - 1.959964 * se), math.exp(math.log(rr) + 1.959964 * se)


def _decimals(s: Any) -> int:
    s = str(s)
    return len(s.split(".")[1]) if "." in s else 0


def _same_at_printed(value: float, printed: Any) -> bool:
    d = _decimals(printed)
    return abs(value - float(printed)) <= 0.5 * 10 ** -d + 1e-9


def attribute(row: dict[str, Any], sets: list[dict[str, Any]]) -> dict[str, Any]:
    """Which held analysis set reproduces a printed comparator row (RR + both CI limits at printed precision)."""
    if not row or row.get("effect") in (None, "") or (row.get("measure") or "RR").upper() != "RR":
        return {"state": "NOT_COMPARABLE", "per_set": []}
    per = []
    for s in sets:
        v = rr_ci(s["treatment"]["events"], s["treatment"]["n"], s["control"]["events"], s["control"]["n"])
        if not v:
            continue
        rr, lo, hi = v
        repro = (_same_at_printed(rr, row["effect"]) and row.get("lower") not in (None, "")
                 and _same_at_printed(lo, row["lower"]) and _same_at_printed(hi, row["upper"]))
        per.append({"analysis_set": s["analysis_set"], "rr": round(rr, 4), "ci": [round(lo, 4), round(hi, 4)],
                    "reproduces_printed_row": repro, "distance_log_rr": round(abs(math.log(rr) - math.log(float(row["effect"]))), 4),
                    "span": s["span"]})
    if not per:
        return {"state": "NO_HELD_COUNTS", "per_set": []}
    hit = [p for p in per if p["reproduces_printed_row"]]
    near = min(per, key=lambda p: p["distance_log_rr"])
    return {"state": "REPRODUCED" if hit else "NOT_REPRODUCED", "reproduced_by": hit[0]["analysis_set"] if hit else None,
            "nearest": near["analysis_set"], "per_set": per, "printed": {k: row.get(k) for k in ("effect", "lower", "upper")},
            "rule_id": RULE_ID}
