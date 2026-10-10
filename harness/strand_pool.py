"""Declared strands through the ONE analysis / provenance / gate path (external review 11).

  - read_member: a strand member's effect is READ from the held source text at a quoted span (the quote must be in the
    held text after normalising the Lancet middle-dot decimal); a quote that is not held, or numbers that do not parse,
    refuse the member. A strand builder never types a number.
  - table_arm_counts: per-arm participant counts read from a held JATS table (row label + the column header 'n = N');
    a denominator is never inferred.
  - pool_strand: the canonical PM/HKSJ engine (harness.synth.pool) followed by harness.k2.apply_k2_policy -- at k=2 the
    single-df HKSJ interval is NOT served (11-02), exactly as for an outcome pool.
  - served_view / k2_violation: what a renderer may show for any strand pool doc (including docs written before this
    module), and the gate that refuses a k=2 strand serving an interval.
"""
from __future__ import annotations

import html
import math
import re
from typing import Any

from . import k2
from .synth import Study, pool as _pool

_NUM = r"(\d+(?:\.\d+)?)"
# a bound is read whole or not at all (r24 whitelist): only ')', ';', ']', a prose comma, or the end may follow it
_END = r"(?=\s{0,3}(?:[);\]]|,(?!\d)(?!\s*\d{3}\b)|$))"
_EFFECT_FIRST = re.compile(
    r"(?:\bRR\b|rate ratio|\bHR\b|hazard ratio|relative risk|risk ratio)(?:\s*\[RR\])?\s*[,:]?\s*" + _NUM +
    r"\s{0,3}[;,]?\s{0,3}\[?\s{0,3}(\d+(?:\.\d+)?)%\s*(?:CI|confidence interval)(?:\s*\[CI\])?\s*[,:]?\s*" + _NUM +
    r"\s{0,3}(?:-|–|to)\s{0,3}" + _NUM + _END, re.I)
_LEVEL_FIRST = re.compile(
    r"(?:hazard ratio|rate ratio|relative risk|\bHR\b|\bRR\b)\s*\((\d+(?:\.\d+)?)%\s*(?:CI|confidence interval)\)\s*:?\s*"
    + _NUM + r"\s*\(\s*" + _NUM + r"\s{0,3}(?:-|–|to)\s{0,3}" + _NUM + _END, re.I)


# 'was 0.56 (95% CI, 0.45 to 0.68' -- the effect named earlier in the quoted sentence; the quote fixes which outcome
_PAREN = re.compile(_NUM + r"\s*\(\s*(\d+(?:\.\d+)?)%\s*(?:CI|confidence interval)\s*,?\s*" + _NUM +
                    r"\s{0,3}(?:-|–|to)\s{0,3}" + _NUM + _END, re.I)


def normalise(text: str | None) -> str:
    """Whitespace collapsed; the middle-dot decimal ('0·79', Lancet house style) read as '.'."""
    t = html.unescape(text or "").replace("·", ".").replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


def read_member(held_text: str | None, quote: str) -> dict[str, Any] | None:
    """{effect, ci_level, ci_low, ci_high, source_span} read from `quote`, which must occur in the held text; else None."""
    nq, nt = normalise(quote), normalise(held_text)
    if not nq or nq not in nt:
        return None
    m = _EFFECT_FIRST.search(nq)
    if m:
        eff, lvl, lo, hi = m.group(1), m.group(2), m.group(3), m.group(4)
    elif _LEVEL_FIRST.search(nq):
        m = _LEVEL_FIRST.search(nq)
        lvl, eff, lo, hi = m.group(1), m.group(2), m.group(3), m.group(4)
    else:
        m = _PAREN.search(nq)
        if not m:
            return None
        eff, lvl, lo, hi = m.group(1), m.group(2), m.group(3), m.group(4)
    return {"effect": float(eff), "ci_level": float(lvl), "ci_low": float(lo), "ci_high": float(hi), "source_span": nq}


def _cells(row_html: str) -> list[str]:
    return [normalise(re.sub(r"<[^>]+>", " ", c)) for c in re.findall(r"<td[^>]*>(.*?)</td>", row_html, re.S)]


def table_arm_counts(jats: str | None, caption_term: str, row_label: str) -> dict[str, Any] | None:
    """Per-arm participants with the event, and the arm sizes, from ONE held table:
      - the table whose caption contains `caption_term` (e.g. 'full-analysis set');
      - arm sizes from its header cells '... (n = N)', in column order;
      - the row whose first cell is `row_label`; each arm's 'X (rate)' cell gives X participants.
    Returns None when any piece is missing or ambiguous -- never an inferred denominator."""
    if not jats:
        return None
    for tw in re.findall(r"<table-wrap\b.*?</table-wrap>", jats, re.S):
        cap = normalise(re.sub(r"<[^>]+>", " ", (re.search(r"<caption>(.*?)</caption>", tw, re.S) or [None, ""])[1]))
        if caption_term.lower() not in cap.lower():
            continue
        head = normalise(re.sub(r"<[^>]+>", " ", (re.search(r"<thead>(.*?)</thead>", tw, re.S) or [None, ""])[1]))
        ns = [int(x) for x in re.findall(r"\(\s*n\s*=\s*(\d+)\s*\)", head)]
        rows = [r for r in re.findall(r"<tr>(.*?)</tr>", tw, re.S) if _cells(r) and _cells(r)[0] == row_label]
        if len(ns) != 2 or len(rows) != 1:
            return None
        arm = [c for c in _cells(rows[0])[1:] if re.fullmatch(r"\d+ \(\d+(?:\.\d+)?\)", c)]
        if len(arm) != 2:
            return None
        a, c = (int(x.split(" ")[0]) for x in arm)
        return {"ai": a, "n1i": ns[0], "ci": c, "n2i": ns[1], "caption": cap[:160], "row": " | ".join(_cells(rows[0])),
                "arm_header": head[:240]}
    return None


def counts_rr(ai: int, n1i: int, ci: int, n2i: int) -> dict[str, Any]:
    """Single-trial risk ratio from the read counts, through the canonical engine (k=1: the trial's own interval)."""
    r = _pool([Study(label="t", ai=ai, n1i=n1i, ci=ci, n2i=n2i, measure="RR")], scale="RR")
    return {"effect": round(r.estimate, 4), "ci_low": round(r.ci_low, 4), "ci_high": round(r.ci_high, 4),
            "ci_level": 95.0, "scale": "RR", "ci_provenance": r.ci_provenance}


def pool_strand(members: list[dict[str, Any]], scale: str) -> dict[str, Any] | None:
    """PM/HKSJ via synth.pool, then the k=2 policy (no single-df interval served; direction conflict refuses)."""
    if len(members) < 2:
        return None
    r = _pool([Study(label=m["trial"], effect=m["effect"], ci_low=m["ci_low"], ci_high=m["ci_high"])
               for m in members], scale=scale)
    res = {"k": r.k, "estimate": r.estimate, "ci_low": r.ci_low, "ci_high": r.ci_high, "tau2": r.tau2,
           "i2": getattr(r, "i2", None), "scale": scale, "ci_provenance": r.ci_provenance,
           "estimate_fixed": r.estimate_fixed, "ci_low_fixed": r.ci_low_fixed, "ci_high_fixed": r.ci_high_fixed}
    res = k2.apply_k2_policy(res, [{"effect": m["effect"], "ci_low": m["ci_low"], "ci_high": m["ci_high"]}
                                   for m in members])
    return _rounded(res)


def _rounded(res: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for k_, v in res.items():
        out[k_] = round(v, 4) if isinstance(v, float) else v
    if isinstance(out.get("ci_hksj_unserved"), dict):
        out["ci_hksj_unserved"] = {k_: (round(v, 4) if isinstance(v, float) else v)
                                   for k_, v in out["ci_hksj_unserved"].items()}
    return out


def member_class(m: dict[str, Any]) -> tuple[str, str]:
    """The provenance class of one strand member -- ONE function shared by the page's extraction tab and the
    provenance census (external review 11-01): EXTRACTOR when this module read it from a held source (a held span is
    recorded), HAND_ENTERED when the strand doc was written outside this module."""
    if m.get("source_span") and str(m.get("source") or "").startswith("held "):
        return "EXTRACTOR", f"read by harness/strand_pool.py from {m.get('source')}"
    return "HAND_ENTERED", ("the strand doc was written outside harness/strand_pool.py; no held span is recorded on "
                            "this member")


def strand_rows(r: dict[str, Any]) -> list[dict[str, Any]]:
    """(outcome label, id, member) for every served strand member -- the census and the page enumerate the same rows."""
    out = []
    for s in ((r.get("strands") or {}).get("strands")) or []:
        for m in s.get("members") or []:
            out.append((f"Strand {s.get('strand') or s.get('id')}: {s.get('name')}",
                        f"PMID {m.get('pmid')}" if m.get("pmid") else None, s, m))
    return out


def policy_pool(pool: dict[str, Any] | None) -> dict[str, Any] | None:
    """Apply the k=2 rule to a strand pool from ANY doc (claimgraph.attach_strands calls this, so a hand-written doc
    such as pcsk9's is served under the same rule): a k=2 interval moves to ci_hksj_unserved and is not served."""
    if not isinstance(pool, dict) or pool.get("k") != 2 or pool.get("pool_refused") or pool.get("pooled_ci_refused"):
        return pool
    if pool.get("ci_low") is None and pool.get("ci_high") is None:
        return pool
    res = k2.refuse_k2_ci(dict(pool))
    res["crosses_null"] = None
    return res


def served_view(pool: dict[str, Any] | None) -> dict[str, Any] | None:
    """What may be rendered for a strand pool from ANY strand doc: the estimate, and an interval only when the k=2
    rule allows it. A doc written before this module (pcsk9) that still carries a k=2 interval is shown withheld."""
    if not pool:
        return None
    est = pool.get("estimate", pool.get("effect"))
    k_ = pool.get("k")
    lo, hi = pool.get("ci_low"), pool.get("ci_high")
    withheld = None
    if pool.get("pool_refused"):
        return {"k": k_, "estimate": None, "ci_low": None, "ci_high": None,
                "withheld": f"{pool['pool_refused'].get('code')}: {pool['pool_refused'].get('detail')}"}
    if k_ == 2 and (lo is not None or hi is not None or pool.get("pooled_ci_refused")):
        withheld = (pool.get("pooled_ci_refused") or {}).get("detail") or (
            "Registered PM/HKSJ uses t(1)=12.71 at k=2; the interval is not served as a pooled confidence interval.")
        lo = hi = None
    crosses = None if lo is None else not ((lo < 1.0 and hi < 1.0) or (lo > 1.0 and hi > 1.0))
    return {"k": k_, "estimate": est, "ci_low": lo, "ci_high": hi, "withheld": withheld, "crosses_null": crosses,
            "tau2": pool.get("tau2")}


def k2_violation(pool: dict[str, Any] | None) -> str | None:
    """The gate: a k=2 strand pool that serves an interval, judged by the same predicate as an outcome pool."""
    if not isinstance(pool, dict) or pool.get("k") != 2:
        return None
    view = {"k": 2, "ci_low": pool.get("ci_low"), "ci_high": pool.get("ci_high"), "scale": pool.get("scale")}
    for key in ("pooled_ci_refused", "pool_refused"):          # k2_check reads these with .get(key, {})
        if isinstance(pool.get(key), dict):
            view[key] = pool[key]
    return k2.k2_check(view)
