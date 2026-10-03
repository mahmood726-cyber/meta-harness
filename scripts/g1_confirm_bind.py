"""CONFIRM UNVERIFIED (Mahmood 3 Oct, goal 1): every comparator trial the G1 tracker routes UNVERIFIED holds exactly ONE
source -- the comparator's own printed row, which never counts (anti-circularity). Seek a PRIMARY binding for it:
the same typed tuple printed by the trial's OWN open report (PMC OA / Unpaywall / abstract, via the shared cascade:
scripts/g1_confirm_acquire.py) or by its posted CT.gov results (AACT, versioned snapshot).

Deterministic and regex-only, through the SHARED gates of the secondary tier (harness.secondary_meta):
  typed_match_text      both arms' 'events/N' ('e/n', 'e of n', 'e out of n') within 400 characters, with a topic
                        outcome term near; OR an effect + CI triple equal to the row's (rounding-aware) with the SAME
                        measure word just before it and the outcome near
  typed_match_registry  the posted outcome's title names the topic outcome; two distinct result groups carry the two
                        arms' (count, N), or an analysis of the same measure carries the same estimate + CI
plus: a subgroup / post-hoc span is refused (harness.extract._is_subgroup_sentence, the extractor's own detector).

THE SEARCH KEY IS THE COMPARATOR'S ROW. What counts is the primary span, never the comparator: the tuple is admitted
only because the trial's own report prints it. Consequence, stated on every binding and carried to the tracker: the
row's agreement with the comparator is TRUE BY CONSTRUCTION and is reported NOT_INDEPENDENT, never as AGREE.

No model call. A miss is not a mismatch: the row stays UNVERIFIED with the reason recorded.

    python scripts/g1_confirm_bind.py [--registry]   -> outputs/k_gap/g1_confirm/bindings.json
        --registry   also index the rows' NCTs in the local AACT snapshot (writes the shared AACT index: never run it
                     while another process builds trackers on the same index)
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import extract  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402
import g1_confirm_acquire as acq  # noqa: E402
import secondary_meta_build as smb  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap")
BIND = os.path.join(OUT, "g1_confirm", "bindings.json")
SEARCH_KEY = "COMPARATOR_ROW"
# subgroup language the shared detector (harness.extract._SUBGROUP) does not hold; local to this binder, reported to the
# k-gap lane for the shared detector. DECLARE-TIMI 58: '(HR, 0.88 [0.76-1.02]; P for interaction=0.046), ... similar in
# those with HF without known reduced EF (HR, 0.88 [95% CI, 0.66-1.17])'. Narrow on purpose: 'in patients with X'
# names a trial's OWN population and is not here.
import re as _re  # noqa: E402
SUBGROUP_EXTRA = _re.compile(r"\bp[-\s]?(?:value\s+)?for\s+interaction\b|\binteraction\s*(?:p|=)|\bin those (?:with|without)\b"
                             r"|\bthose without\b", _re.I)


def _int(v):
    try:
        f = float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None
    return int(f) if f == int(f) else None


def key_row(slug, x):
    """The comparator's printed row as a SecondaryRow -- the SEARCH KEY only."""
    cr = x.get("comparator_row") or {}
    return sm.SecondaryRow(meta_pmid="COMPARATOR", meta_doi="", location={}, source_digest="",
                           provenance="COMPARATOR_ROW_AS_SEARCH_KEY", trial_label=x["label"],
                           measure=(cr.get("measure") or "").upper(), outcome_definition="",
                           events_t=_int(cr.get("events_t")), n_t=_int(cr.get("n_t")),
                           events_c=_int(cr.get("events_c")), n_c=_int(cr.get("n_c")),
                           effect=cr.get("effect"), lower=cr.get("lower"), upper=cr.get("upper"))


def text_span(row, text, has_counts):
    """(span, 200 chars before it, by_counts) for a typed_match_text hit: the CONTIGUOUS window from 120 characters before
    the first matched item to 60 after the last, so a count tuple's span holds BOTH arms' pairs (the shared matcher
    returns the first 400 characters around the treatment pair only, which can cut the control pair off)."""
    import re
    t = sm._fold_text(text or "")
    if has_counts:
        def pair(e, n):
            return re.compile(rf"(?<![\d.]){e}\s*(?:/|of|out of)\s*(?:{n:,}|{n})(?![\d])")
        for m in pair(row.events_t, row.n_t).finditer(t):
            lo, hi = max(0, m.start() - 400), m.end() + 400
            c = pair(row.events_c, row.n_c).search(t, lo, hi)
            if c:
                a, b = min(m.start(), c.start()), max(m.end(), c.end())
                return t[max(0, a - 120): b + 60], t[max(0, a - 320): max(0, a - 120)], True
    if row.effect not in (None, ""):
        for m in sm._TEXT_TRIPLE.finditer(t):
            if sm._eq_printed(m.group(1), row.effect) and sm._eq_printed(m.group(2), row.lower) and \
                    sm._eq_printed(m.group(3), row.upper):
                return t[max(0, m.start() - 160): m.end() + 40], t[max(0, m.start() - 360): max(0, m.start() - 160)], False
    return None, "", False


_TABLE = _re.compile(r"^TABLE (?P<title>[^\n]*)\n(?P<body>.*?)(?=^TABLE |\Z)", _re.M | _re.S)
_HEAD_N = _re.compile(r"\(\s*[Nn]\s*=\s*([\d,]+)\s*\)|\b[Nn]\s*=\s*([\d,]+)\b")
_CELL_PCT = _re.compile(r"^\s*([\d,]+)\s*[(\[]\s*(\d{1,3}(?:\.\d+)?)\s*%?\s*[)\]]\s*$")
_CELL_TRIPLE = _re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*[(\[]\s*(-?\d+(?:\.\d+)?)\s*(?:[-–—]|to|,)\s*"
                           r"(-?\d+(?:\.\d+)?)\s*[)\]]")
_MEASURE_HEAD = {"HR": r"hazard ratio|\bHR\b", "RR": r"relative risk|risk ratio|\bRR\b", "OR": r"odds ratio|\bOR\b",
                 "MD": r"mean difference|\bMD\b|difference"}


def _pct_ok(e, n, printed):
    """The printed percentage is e/n x 100 at ITS printed precision (half a unit of the last digit)."""
    d = len(printed.split(".")[1]) if "." in printed else 0
    return n > 0 and abs(100.0 * e / n - float(printed)) <= 0.5 * 10 ** -d + 1e-9


def table_match(row, text, terms):
    """(span_parts, by_counts) from a held text's STRUCTURED tables (harness.fulltext renders cells ' | '), or None.
    COUNTS: a row whose label names the topic outcome, with 'e (p%)' in the column whose header states N = the row's
    N for each arm, p consistent with e/N at its printed precision. EFFECT_CI: 'effect (lower-upper)' in a column
    whose header names the measure. Never a baseline table; never a subgroup title/row; equal arm Ns refused (the
    columns cannot then be told apart by N)."""
    low_terms = [t.lower() for t in terms if t and len(t) > 3]
    for tm in _TABLE.finditer(text or ""):
        title = tm.group("title")
        if _re.search(r"baseline|characteristic|demograph", title, _re.I):
            continue
        lines = [ln for ln in tm.group("body").split("\n") if ln.strip()]
        if not lines:
            continue
        head = [c.strip() for c in lines[0].split(" | ")]
        ns = []
        for c in head:
            m = _HEAD_N.search(c)
            ns.append(int((m.group(1) or m.group(2)).replace(",", "")) if m else None)
        for ln in lines[1:]:
            cells = [c.strip() for c in ln.split(" | ")]
            lab = cells[0].lower()
            if not any(t in lab for t in low_terms):
                continue
            if extract._is_subgroup_sentence(title + " " + cells[0]) or SUBGROUP_EXTRA.search(title + " " + cells[0]):
                continue
            if None not in (row.events_t, row.n_t, row.events_c, row.n_c) and row.n_t != row.n_c:
                ok = {}
                for i, c in enumerate(cells[1:], 1):
                    m = _CELL_PCT.match(c)
                    if not m or i >= len(ns) or ns[i] is None:
                        continue
                    e = int(m.group(1).replace(",", ""))
                    for arm, (ee, nn) in (("t", (row.events_t, row.n_t)), ("c", (row.events_c, row.n_c))):
                        if ns[i] == nn and e == ee and _pct_ok(e, nn, m.group(2)):
                            ok[arm] = i
                if "t" in ok and "c" in ok and ok["t"] != ok["c"]:
                    return [f"TABLE {title}", lines[0], ln], True
            if row.effect not in (None, "") and row.measure in _MEASURE_HEAD:
                for i, c in enumerate(cells[1:], 1):
                    m = _CELL_TRIPLE.match(c)
                    if m and i < len(head) and _re.search(_MEASURE_HEAD[row.measure], head[i], _re.I) and \
                            sm._eq_printed(m.group(1), row.effect) and sm._eq_printed(m.group(2), row.lower) and \
                            sm._eq_printed(m.group(3), row.upper):
                        return [f"TABLE {title}", lines[0], ln], False
    return None


def bind_one(slug, x, pmids, ncts, terms):
    """(binding | None, why). The first source whose bytes carry the typed tuple, in a fixed order: each PMID's
    sources as primary_sources lists them (abstract, PMC OA, held ft, Unpaywall, then posted results)."""
    row = key_row(slug, x)
    has_counts = None not in (row.events_t, row.n_t, row.events_c, row.n_c)
    has_effect = row.effect not in (None, "") and row.measure in ("HR", "RR", "OR", "MD")
    if not (has_counts or has_effect):
        return None, "COMPARATOR_ROW_HAS_NO_TYPED_TUPLE"
    tried = []
    for p in pmids or [""]:
        for kind, ref, payload in smb.primary_sources(slug, p, (ncts or [None])[0]):
            tried.append(ref)
            hit = (sm.typed_match_text(row, payload, terms, ref) if kind == "text"
                   else sm.typed_match_registry(row, payload, terms, ref))
            if not hit and kind == "text":
                tb = table_match(row, payload, terms)
                if tb:
                    parts, by_counts = tb
                    body = payload
                    return {"slug": slug, "label": x["label"], "pmid": p or None, "ncts": ncts,
                            "source_kind": "TEXT", "source": ref,
                            "source_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                            "route": "PRIMARY_TEXT_TABLE", "span": " … ".join(parts), "span_parts": parts,
                            "tuple_kind": "COUNTS" if by_counts else "EFFECT_CI",
                            "values": ({"events_t": row.events_t, "n_t": row.n_t, "events_c": row.events_c,
                                        "n_c": row.n_c} if by_counts else
                                       {"measure": row.measure, "effect": row.effect, "lower": row.lower,
                                        "upper": row.upper}),
                            "search_key": SEARCH_KEY,
                            "agreement_with_comparator_row": "NOT_INDEPENDENT:SEARCH_KEYED_BY_COMPARATOR_ROW"}, "BOUND"
            if not hit:
                continue
            span = hit.get("span") or ""
            if kind == "text":
                span, before, by_counts = text_span(row, payload, has_counts)
                if span is None:
                    return None, f"SPAN_NOT_RELOCATED:{ref}"
                # the extractor's own subgroup detector, on the span AND the 200 characters before it (the shared
                # table-location gate's rule): DECLARE's 'HR 0.88 (0.66-1.17)' is 'in those with HF without known
                # reduced EF ... P for interaction', a subgroup, not the trial's result
                if extract._is_subgroup_sentence(span) or extract._is_subgroup_sentence(before) or \
                        SUBGROUP_EXTRA.search(span) or SUBGROUP_EXTRA.search(before):
                    return None, f"SUBGROUP_OR_POST_HOC_SPAN:{ref}"
            else:
                by_counts = has_counts and hit.get("route") == "PRIMARY_REGISTRY" and "groups" in span
            body = payload if isinstance(payload, str) else json.dumps(payload, sort_keys=True)
            return {"slug": slug, "label": x["label"], "pmid": p or None, "ncts": ncts,
                    "source_kind": "TEXT" if kind == "text" else "AACT", "source": ref,
                    "source_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                    "route": hit.get("route") or "PRIMARY_TEXT", "span": span,
                    "tuple_kind": "COUNTS" if by_counts else "EFFECT_CI",
                    "values": ({"events_t": row.events_t, "n_t": row.n_t, "events_c": row.events_c, "n_c": row.n_c}
                               if by_counts else {"measure": row.measure, "effect": row.effect, "lower": row.lower,
                                                  "upper": row.upper}),
                    "registry_fields": hit.get("registry_fields"),
                    "search_key": SEARCH_KEY,
                    "agreement_with_comparator_row": "NOT_INDEPENDENT:SEARCH_KEYED_BY_COMPARATOR_ROW"}, "BOUND"
    return None, ("NO_PRIMARY_SOURCE_HELD" if not tried else
                  "TUPLE_NOT_PRINTED_IN_HELD_PRIMARY:" + "; ".join(tried)[:300])


def main(argv):
    targets = acq.unverified_targets()
    if "--registry" in argv:
        smb.ensure_registry(sorted({n for t in targets for n in t["ncts"]}))
    out, tally = [], Counter()
    for t in targets:
        g = acq._j(os.path.join(OUT, "g1", t["slug"] + ".json"))
        x = next(r for r in g["trials"] if r["label"] == t["label"])
        spec = smb.spec_of(t["slug"])
        terms = [k for k in (spec.get("keywords") or []) if k] + list(spec.get("core") or [])
        b, why = bind_one(t["slug"], x, t["pmids"], t["ncts"], terms)
        tally[(b or {}).get("source_kind", why.split(":")[0])] += 1
        out.append(b or {"slug": t["slug"], "label": t["label"], "pmid": None, "state": "NOT_BOUND", "why": why})
        print(t["slug"], "|", t["label"], "|", (b or {}).get("source") or why[:120], flush=True)
    res = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "search_key": SEARCH_KEY,
           "registry_indexed": "--registry" in argv, "targets": len(targets), "tally": dict(tally),
           "bindings": [b for b in out if b.get("source_kind")], "not_bound": [b for b in out if not b.get("source_kind")]}
    os.makedirs(os.path.dirname(BIND), exist_ok=True)
    tmp = BIND + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, BIND)
    print(json.dumps(res["tally"]))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
