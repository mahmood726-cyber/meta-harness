"""Typed extractors over HELD source text, and the replay limb that lets a served row claim the EXTRACTOR class.

A row read by one of these extractors carries its provenance kind, the held document it read (document_ref, under
outputs/held_*), that document's pinned text sha256 (document_sha256, equal to the held manifest's), the span it read
(source_span) and a `replay` spec naming exactly what was read. It is EXTRACTOR only when `replay(row)` re-reads the
held bytes with the same typed reader and gets IDENTICAL values and spans -- never because its provenance string says
so (DISPATCH_V14_EXTRACTOR_ROUTE: a script-typed `*_verified` row was HAND_ENTERED and stays so).

  held_abstract_clause   a signed clause of a held PubMed abstract: verbatim in the held text; HR, 95% CI and the two
                         arms' n/N read by type from the clause (V14-02, dpp4-mace-t2d hHF)
  label_adr_table        an adverse-reaction row of a held regulatory label table: caption naming the trial, then the
                         arm header 'Brand N = n ... Comparator N = n', then the row '<label> n (p) n (p)', each printed
                         p reconciling with n / N (V14-03, finerenone FIDELIO-DKD hyperkalaemia)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPLAY_PROV = frozenset({"held_abstract_clause", "held_fulltext_clause", "label_adr_table"})
_HELD = {"held_abstract_clause": "outputs/held_abstracts/", "held_fulltext_clause": "outputs/held_fulltexts/",
         "label_adr_table": "outputs/held_labels/"}
_MANIFEST_SHA = {"held_abstract_clause": "sha256", "held_fulltext_clause": "sha256", "label_adr_table": "text_sha256"}
_CLAUSE_KINDS = ("held_abstract_clause", "held_fulltext_clause")


class ReadRefused(ValueError):
    """The typed reader could not read the value it was asked for: never a partial or a guessed read."""


# ------------------------------------------------------------------------------------------------ abstract clause
# a number never continues: not with a digit, '.digit', a thousands ',ddd' ('1,000', flow-r2#1) or an exponent in any
# minus ('1.20e1', '1.20e\u22121', extr-r3#1 / r4#2); a full stop may end it
_NUM = r"(\d+(?:\.\d+)?)(?!\d|\.\d|,\d{3}|[eE][-+\u2212]?\d)"
_HR = re.compile(r"(?:HR of|\[HR\],|hazard ratio(?: \[HR\])?,?|\bHR\b)\s*" + _NUM + r"\s*\(?;?\s*95% CI,?\s*" + _NUM
                 + r"\s*(?:,|-|\u2013|to)\s*" + _NUM)
# a LOG hazard ratio is not a hazard ratio (extr-r4#1, flow-r2#2): such a clause is refused, never exponentiated here
_LOG_HR = re.compile(r"\b(?:log|ln|logarithm(?:ic)?)(?:[\s-]*(?:transformed|scale[d]?))?[\s-]*(?:of\s+(?:the\s+)?)?"
                     r"(?:hazard\s+ratio|HR)\b", re.I)                       # + 'log-transformed HR' (extr-r5#4)


def read_abstract_clause(clause: str) -> dict[str, Any]:
    """The ONE hazard ratio a signed clause states, with its 95% CI, by type -- nothing else. Counts are never read from a
    clause (codex extr-r1/r2: rates per person-years, mixed populations, Kaplan-Meier estimates and thousands separators
    each defeated a count reading; no held row serves counts from a clause). Zero or several HRs, or a log HR: refused."""
    if _LOG_HR.search(clause):
        raise ReadRefused("the clause states a LOG hazard ratio")
    hr = _HR.findall(clause)
    if len(hr) != 1:
        raise ReadRefused(f"clause must state exactly one HR with its 95% CI (got {len(hr)})")
    e, lo, hi = (float(x) for x in hr[0])
    if not lo <= e <= hi:
        raise ReadRefused(f"HR {e} outside its interval {lo}-{hi}")
    return {"effect": e, "ci_low": lo, "ci_high": hi}


# ------------------------------------------------------------------------------------------------ label ADR table
def _pct_ok(n: int, d: int, printed: str) -> bool:
    if d <= 0:
        raise ReadRefused("a denominator of zero")
    places = len(printed.split(".")[1]) if "." in printed else 0
    return f"{100.0 * n / d:.{places}f}" == printed


# a table caption ends a table whether it is 'Table N:' or 'Table N.' (extr-r4#3, flow-r2#3)
_CAPTION_START = re.compile(r"\bTable\s+\d+\s*[:.]", re.I)               # 'TABLE 4:' too (extr-r5#1)
# a caption naming a POOL of studies cannot supply one trial's counts (flow-r2#4)
_POOLED = re.compile(r"\b(?:pooled|pooling|combined|integrated|across|meta-?analy)", re.I)
_TRIAL_TOKEN = re.compile(r"\b[A-Za-z][A-Za-z0-9]+-[A-Za-z0-9]+\b")   # 'figaro-dkd' too (extr-r5#2)


def read_label_adr_table(text: str, spec: dict[str, str]) -> dict[str, Any]:
    """One adverse-reaction row of a label table, by type. spec: table ('Table 3'), trial ('FIDELIO-DKD'), arm_t
    ('Kerendia'), arm_c ('Placebo'), row_label ('Hyperkalemia') -- literals, escaped; nothing in the spec is a pattern."""
    for k in ("table", "trial", "arm_t", "arm_c", "row_label"):
        if not str(spec.get(k) or "").strip():
            raise ReadRefused(f"replay spec lacks {k!r}")
    # the trial is named within the caption's own two lines, never past another caption (extr-r2#4)
    _line = r"(?:(?![Tt][Aa][Bb][Ll][Ee]\s+\d+\s*[:.])[^\n])*"
    cap = re.search(re.escape(spec["table"]).replace(r"\ ", r"\s+") + r"\s*:\s*Adverse\s+reactions\b" + _line + r"\n?"
                    + _line + re.escape(spec["trial"]) + _line, text, re.I)
    if not cap:
        raise ReadRefused(f"{spec['table']} caption naming {spec['trial']} not found")
    caption = re.sub(r"\s+", " ", cap.group(0)).strip()
    others = sorted({t for t in _TRIAL_TOKEN.findall(caption) if t.lower() != spec["trial"].lower()})
    if _POOLED.search(caption) or others:
        raise ReadRefused(f"the caption names a pool or other trials ({others or 'pooled'}): not {spec['trial']}'s counts")
    # the table ends where the next caption starts: a header or row past it belongs to another table (extr-r1#4)
    nxt = _CAPTION_START.search(text, cap.end())
    end = nxt.start() if nxt else len(text)
    hdr_rx = re.compile(re.escape(spec["arm_t"]) + r"\s+N\s*=\s*(\d[\d,]*)\s+n\s*\(%\)\s+" + re.escape(spec["arm_c"])
                        + r"\s+N\s*=\s*(\d[\d,]*)\s+n\s*\(%\)")
    hdr = hdr_rx.search(text, cap.end(), end)
    if not hdr or hdr.start() - cap.end() > 4000:
        raise ReadRefused("arm header not within the table's reach")
    row = re.compile(r"(?:^|(?<=\n))[ \t]*" + re.escape(spec["row_label"]) + r"\s+(\d+)\s*\((\d+(?:\.\d+)?)\)\s+(\d+)\s*\("
                     r"(\d+(?:\.\d+)?)\)", re.M).search(text, hdr.end(), end)
    if not row or row.start() - hdr.end() > 400:
        raise ReadRefused(f"{spec['row_label']!r} row not directly under the header")
    # the row's denominators are the header's ONLY when nothing else states one: exactly one arm header between the
    # caption and the row, and no other 'N =' between the header and the row (randomised v safety populations;
    # extr-r3#2, r4#4, agy flow-r2 g1#2 -- the whole span before the row, not only after the header)
    if (len(list(hdr_rx.finditer(text, cap.end(), row.start()))) != 1
            or re.search(r"\b[Nn]\s*[:=]\s*\d", text[cap.end():hdr.start()] + "\n" + text[hdr.end():row.start()])):
        raise ReadRefused("more than one denominator statement before the row: the row's denominators are ambiguous")
    nt, nc = (int(x.replace(",", "")) for x in hdr.groups())
    et, pt, ec, pc = row.groups()
    et, ec = int(et), int(ec)
    if not (_pct_ok(et, nt, pt) and _pct_ok(ec, nc, pc)):
        raise ReadRefused("printed percentages do not reconcile with n / N")
    return {"ai": et, "n1i": nt, "ci": ec, "n2i": nc, "raw_row": row.group(0),
            "row_span": re.sub(r"\s+", " ", row.group(0)).strip(), "header_span": re.sub(r"\s+", " ", hdr.group(0)),
            "caption_span": caption}


# ------------------------------------------------------------------------------------------------------- replay
def _held_text(kind: str, ref: str, root: str) -> tuple[str, str]:
    ref = str(ref or "")
    if not ref.startswith(_HELD[kind]) or ".." in ref or ref.count("/") != 2:
        raise ReadRefused(f"document_ref {ref!r} is not a held document of kind {kind}")
    path = os.path.join(root, *ref.split("/"))
    try:
        text = open(path, encoding="utf-8", newline="").read()
        man = json.load(open(os.path.join(root, *ref.split("/")[:2], "manifest.json"), encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ReadRefused(f"held document or its manifest unreadable: {exc}") from exc
    pinned = ((man.get("documents") or {}).get(ref.split("/")[-1]) or {}).get(_MANIFEST_SHA[kind])
    if not pinned:
        raise ReadRefused(f"{ref} has no pinned digest in its manifest")
    return text, pinned


def _num(v):
    try:
        return round(float(v), 6)
    except (TypeError, ValueError):
        return None


def replay(t: dict[str, Any], root: str = ROOT) -> tuple[bool, str]:
    """Re-read the held source a served row claims, with the same typed reader. (True, basis) only when the held bytes
    are the pinned ones, the row's span is in them, and every served number is re-derived identically."""
    kind = str(t.get("provenance") or "")
    if kind not in REPLAY_PROV:
        return False, f"{kind!r} is not a replayable extractor"
    try:
        text, pinned = _held_text(kind, t.get("document_ref"), root)
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if sha != pinned or t.get("document_sha256") != pinned:
            raise ReadRefused(f"held text sha256 {sha[:12]} / row {str(t.get('document_sha256'))[:12]} != pinned "
                              f"{pinned[:12]}")
        span = str(t.get("source_span") or "")
        if not span or span not in text:
            raise ReadRefused("the row's source_span is not verbatim in the held text")
        if kind in _CLAUSE_KINDS:
            # this kind serves an effect and its CI only: a row carrying counts is not a clause read (extr-r1#1)
            if any(t.get(k) is not None for k in ("ai", "n1i", "ci", "n2i")):
                raise ReadRefused("a held_abstract_clause row serves an effect and its CI, never counts")
            want = read_abstract_clause(span)
        else:
            # this kind serves arm counts only: a row carrying an effect is not a table read (extr-r3#3)
            if any(t.get(k) is not None for k in ("effect", "ci_low", "ci_high")):
                raise ReadRefused("a label_adr_table row serves arm counts, never an effect")
            v = read_label_adr_table(text, t.get("replay") or {})
            if v["raw_row"] != span:
                raise ReadRefused("the replayed row is not the row's source_span")
            want = {k: v[k] for k in ("ai", "n1i", "ci", "n2i")}
        bad = [k for k, x in want.items() if _num(t.get(k)) != _num(x)]
        if bad:
            raise ReadRefused(f"replay re-derives different {bad}: {[(k, t.get(k), want[k]) for k in bad]}")
    except ReadRefused as exc:
        return False, f"{kind}: replay refused -- {exc}"
    return True, f"{kind}: replayed from {t.get('document_ref')} (sha256 {pinned[:12]}), identical values"
