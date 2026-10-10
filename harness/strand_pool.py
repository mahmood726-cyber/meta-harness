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

# a number never starts inside another (no digit or dot before it: '.56' is not 56, codex strands-r1#2)
_NUM = r"(?<![\d.])(\d+(?:\.\d+)?)"
# a bound is read whole or not at all (r24 whitelist): only ')', ';', ']', a prose comma, or the end may follow it; any
# digit after a comma refuses (r24 copps-r14)
_END = r"(?=\s{0,3}(?:[);\]]|,(?!\s*\d)|$))"
_EFFECT_FIRST = re.compile(
    r"(?:\bRR\b|rate ratio|\bHR\b|hazard ratio|relative risk|risk ratio)(?:\s*\[RR\])?\s*[,:]?\s*" + _NUM +
    r"\s{0,3}[;,]?\s{0,3}\[?\s{0,3}(\d+(?:\.\d+)?)%\s*(?:CI|confidence interval)(?:\s*\[CI\])?\s*[,:]?\s*" + _NUM +
    r"\s{0,3}(?:-|–|to)\s{0,3}" + _NUM + _END, re.I)
_LEVEL_FIRST = re.compile(
    r"(?:hazard ratio|rate ratio|relative risk|\bHR\b|\bRR\b)\s*\((\d+(?:\.\d+)?)%\s*(?:CI|confidence interval)\)\s*:?\s*"
    + _NUM + r"\s*\(\s*" + _NUM + r"\s{0,3}(?:-|–|to)\s{0,3}" + _NUM + _END, re.I)
# 'was 0.56 (95% CI, 0.45 to 0.68' -- the effect named earlier in the quoted sentence; the quote fixes which outcome
# (its effect may not follow a minus or a letter either: '1e-2' must not read as 2, codex strands-r2#1)
_PAREN = re.compile(r"(?<![\w\-−])" + _NUM + r"\s*\(\s*(\d+(?:\.\d+)?)%\s*(?:CI|confidence interval)\s*,?\s*" + _NUM +
                    r"\s{0,3}(?:-|–|to)\s{0,3}" + _NUM + _END, re.I)
# group order per pattern: effect, level, low, high
_READERS = ((_EFFECT_FIRST, (1, 2, 3, 4)), (_LEVEL_FIRST, (2, 1, 3, 4)), (_PAREN, (1, 2, 3, 4)))


def normalise(text: str | None) -> str:
    """Whitespace collapsed; the middle-dot decimal ('0·79', Lancet house style) read as '.'."""
    t = html.unescape(text or "").replace("·", ".").replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


def read_member(held_text: str | None, quote: str) -> dict[str, Any] | None:
    """{effect, ci_level, ci_low, ci_high, source_span} read from the held text at `quote`; else None.

    The match runs over the HELD text and must lie inside the quoted span, so the end-of-number check sees what really
    follows in the source: a quote that stops inside a held number ('0.94' of '0.945') cannot shorten it (codex
    strands-r1#1)."""
    nq, nt = normalise(quote), normalise(held_text)
    i = nt.find(nq) if nq else -1
    if i < 0:
        return None
    end = i + len(nq)
    for rx, (ge, gl, glo, ghi) in _READERS:
        for m in rx.finditer(nt, i):
            if m.start() >= end:
                break
            if m.end() <= end:
                return {"effect": float(m.group(ge)), "ci_level": float(m.group(gl)), "ci_low": float(m.group(glo)),
                        "ci_high": float(m.group(ghi)), "source_span": nq}
    return None


def _cells(row_html: str) -> list[str]:
    return [normalise(re.sub(r"<[^>]+>", " ", c)) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, re.S)]


# a header naming a population of its own ('randomised', 'analysed', ...) cannot be paired with another arm's: the
# population must come from the caption for both arms (codex strands-r1#5)
_POPULATION_WORD = re.compile(r"randomi[sz]ed|analy[sz]ed|\bITT\b|intention|per[- ]protocol|safety|evaluable|treated",
                              re.I)


def table_arm_counts(jats: str | None, caption: str, row: str, arm_cells: tuple[int, int],
                     count_basis: str) -> dict[str, Any] | None:
    """Per-arm participants with the event, and the arm sizes, from ONE held table, under a layout the CALLER states and
    the source must confirm (codex strands-r1#3-#5) -- never guessed from cell shape:
      - the table whose caption contains `caption` (the population, e.g. 'full-analysis set');
      - exactly two header arm sizes '(n = N)', with no population word of their own in the header;
      - the row whose first cell is `row`; the arm cells are read at the stated POSITIONS `arm_cells`, each 'X (r)';
      - `count_basis`, a phrase of the table itself (caption, header or footnote) stating that X counts participants.
    Returns None when any piece is missing or ambiguous -- never an inferred denominator."""
    if not jats:
        return None
    for tw in re.findall(r"<table-wrap\b.*?</table-wrap>", jats, re.S):
        cap = normalise(re.sub(r"<[^>]+>", " ", (re.search(r"<caption>(.*?)</caption>", tw, re.S) or [None, ""])[1]))
        if caption.lower() not in cap.lower():
            continue
        whole = normalise(re.sub(r"<[^>]+>", " ", tw))
        if count_basis.lower() not in whole.lower():
            return None
        thead = (re.search(r"<thead>(.*?)</thead>", tw, re.S) or [None, ""])[1]
        cols = _header_columns(thead)
        rows = [r for r in re.findall(r"<tr>(.*?)</tr>", tw, re.S) if _cells(r) and _cells(r)[0] == row]
        if len(rows) != 1:
            return None
        cells = _cells(rows[0])
        if max(arm_cells) >= len(cells) or max(arm_cells) >= len(cols):
            return None
        out = []
        for j in arm_cells:
            # each arm cell takes ITS OWN column's header: the denominator comes from there (strands-r2#3), and the
            # column must not be a percentage / SE / SD / mean column (strands-r2#2) or name its own population (r1#5)
            hdr = cols[j]
            n = re.findall(r"\(\s*n\s*=\s*(\d+)\s*\)", hdr)
            if len(n) != 1 or _NOT_A_COUNT_COLUMN.search(hdr) or _POPULATION_WORD.search(hdr):
                return None
            if not re.fullmatch(r"\d+ \(\d+(?:\.\d+)?\)", cells[j]):
                return None
            out.append((int(cells[j].split(" ")[0]), int(n[0])))
        (a, n1), (c, n2) = out
        return {"ai": a, "n1i": n1, "ci": c, "n2i": n2, "caption": cap[:160], "row": " | ".join(cells),
                "arm_header": " | ".join(cols[j] for j in arm_cells), "count_basis": count_basis}
    return None


_NOT_A_COUNT_COLUMN = re.compile(r"%|percent|\bSE\b|\bSD\b|standard (?:error|deviation)|\bmean\b|\bmedian\b|\bIQR\b",
                                 re.I)


def _header_columns(thead: str) -> list[str]:
    """The header text of every column, with rowspan and colspan expanded into a grid: column j's text is every header
    cell that covers column j, top to bottom ('FCM (n = 150) | Incidence/100 patient-years at risk')."""
    grid: dict[tuple[int, int], str] = {}
    for r, tr in enumerate(re.findall(r"<tr>(.*?)</tr>", thead or "", re.S)):
        c = 0
        # a self-closing '<th .../>' is an empty cell -- it must not be read as an opening tag that swallows the next
        cells = [(m.group(1) if m.group(1) is not None else m.group(3), m.group(2) or "")
                 for m in re.finditer(r"<t[dh]((?:[^>/]|/(?!>))*)>(.*?)</t[dh]>|<t[dh]([^>]*)/>", tr, re.S)]
        for attrs, body in cells:
            while (r, c) in grid:
                c += 1
            rs = int((re.search(r'rowspan="(\d+)"', attrs) or [None, "1"])[1])
            cs = int((re.search(r'colspan="(\d+)"', attrs) or [None, "1"])[1])
            text = normalise(re.sub(r"<[^>]+>", " ", body))
            for dr in range(rs):
                for dc in range(cs):
                    grid[(r + dr, c + dc)] = text
            c += cs
    width = max((c for _, c in grid), default=-1) + 1
    rows = max((r for r, _ in grid), default=-1) + 1
    return [" | ".join(t for t in dict.fromkeys(grid.get((r, c), "") for r in range(rows)) if t) for c in range(width)]


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
    span = m.get("source_span") or ""
    if span and str(m.get("source") or "").startswith("held ") and _numbers_match_span(m, span):
        return "EXTRACTOR", f"read by harness/strand_pool.py from {m.get('source')}"
    if span:
        # a span is recorded but the member's numbers do not re-read from it (codex strands-r1#7): never certified
        return "HAND_ENTERED", "the member's numbers do not re-read from its recorded span"
    return "HAND_ENTERED", ("the strand doc was written outside harness/strand_pool.py; no held span is recorded on "
                            "this member")


def _numbers_match_span(m: dict[str, Any], span: str) -> bool:
    """The member's numbers re-read from its own span: an effect + CI from the quote, or counts from the table row and
    header (with the effect recomputed from them)."""
    def close(a, b):
        return a is not None and b is not None and abs(float(a) - float(b)) < 1e-9
    if m.get("ai") is not None:
        # whole numbers only: '1 (' must not match inside '11 (' nor 'n = 10' inside 'n = 100' (codex strands-r2#4)
        need = (rf"(?<![\d.]){m['ai']} \(", rf"(?<![\d.]){m['ci']} \(", rf"\bn = {m['n1i']}(?!\d)",
                rf"\bn = {m['n2i']}(?!\d)")
        if not all(re.search(x, span) for x in need):
            return False
        rr = counts_rr(m["ai"], m["n1i"], m["ci"], m["n2i"])
        return all(close(m.get(k), rr[k]) for k in ("effect", "ci_low", "ci_high"))
    got = read_member(span, span)
    return bool(got) and all(close(m.get(k), got[k]) for k in ("effect", "ci_low", "ci_high"))


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
    if k_ == 2:     # at k=2 an interval is never served, whether or not the doc carries one (codex strands-r1#8)
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
