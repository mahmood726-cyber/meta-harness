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
REPLAY_PROV = frozenset({"held_abstract_clause", "label_adr_table"})
_HELD = {"held_abstract_clause": "outputs/held_abstracts/", "label_adr_table": "outputs/held_labels/"}
_MANIFEST_SHA = {"held_abstract_clause": "sha256", "label_adr_table": "text_sha256"}


class ReadRefused(ValueError):
    """The typed reader could not read the value it was asked for: never a partial or a guessed read."""


# ------------------------------------------------------------------------------------------------ abstract clause
_NUM = r"(\d+(?:\.\d+)?)"
_HR = re.compile(r"(?:HR of|\[HR\],|hazard ratio(?: \[HR\])?,?)\s*" + _NUM + r"\s*\(?;?\s*95% CI,?\s*" + _NUM
                 + r"\s*(?:,|-|–|to)\s*" + _NUM)
_COUNTS = re.compile(r"(?<![\d.])(\d+)/(\d+)(?![\d.])")          # never a rate such as 0.51/100


def read_abstract_clause(clause: str) -> dict[str, Any]:
    """HR, its 95% CI and both arms' n/N, by type, from ONE clause. Exactly two n/N pairs and one HR, else refused."""
    hr = _HR.findall(clause)
    counts = _COUNTS.findall(clause)
    if len(hr) != 1 or len(counts) != 2:
        raise ReadRefused(f"clause must state one HR with its 95% CI and two n/N pairs (got {len(hr)} HR, "
                          f"{len(counts)} n/N)")
    e, lo, hi = (float(x) for x in hr[0])
    if not lo <= e <= hi:
        raise ReadRefused(f"HR {e} outside its interval {lo}-{hi}")
    (et, nt), (ec, nc) = ((int(a), int(b)) for a, b in counts)
    if et > nt or ec > nc:
        raise ReadRefused("an event count exceeds its denominator")
    return {"effect": e, "ci_low": lo, "ci_high": hi, "events_t": et, "n_t": nt, "events_c": ec, "n_c": nc}


# ------------------------------------------------------------------------------------------------ label ADR table
def _pct_ok(n: int, d: int, printed: str) -> bool:
    places = len(printed.split(".")[1]) if "." in printed else 0
    return f"{100.0 * n / d:.{places}f}" == printed


def read_label_adr_table(text: str, spec: dict[str, str]) -> dict[str, Any]:
    """One adverse-reaction row of a label table, by type. spec: table ('Table 3'), trial ('FIDELIO-DKD'), arm_t
    ('Kerendia'), arm_c ('Placebo'), row_label ('Hyperkalemia') -- literals, escaped; nothing in the spec is a pattern."""
    for k in ("table", "trial", "arm_t", "arm_c", "row_label"):
        if not str(spec.get(k) or "").strip():
            raise ReadRefused(f"replay spec lacks {k!r}")
    cap = re.search(re.escape(spec["table"]).replace(r"\ ", r"\s+") + r"\s*:\s*Adverse\s+reactions\b[^\n]*\n?[^\n]*"
                    + re.escape(spec["trial"]), text, re.I)
    if not cap:
        raise ReadRefused(f"{spec['table']} caption naming {spec['trial']} not found")
    hdr = re.compile(re.escape(spec["arm_t"]) + r"\s+N\s*=\s*(\d[\d,]*)\s+n\s*\(%\)\s+" + re.escape(spec["arm_c"])
                     + r"\s+N\s*=\s*(\d[\d,]*)\s+n\s*\(%\)").search(text, cap.end())
    if not hdr or hdr.start() - cap.end() > 4000:
        raise ReadRefused("arm header not within the table's reach")
    row = re.compile(r"(?<![A-Za-z])" + re.escape(spec["row_label"]) + r"\s+(\d+)\s*\((\d+(?:\.\d+)?)\)\s+(\d+)\s*\("
                     r"(\d+(?:\.\d+)?)\)").search(text, hdr.end())
    if not row or row.start() - hdr.end() > 400:
        raise ReadRefused(f"{spec['row_label']!r} row not directly under the header")
    nt, nc = (int(x.replace(",", "")) for x in hdr.groups())
    et, pt, ec, pc = row.groups()
    et, ec = int(et), int(ec)
    if not (_pct_ok(et, nt, pt) and _pct_ok(ec, nc, pc)):
        raise ReadRefused("printed percentages do not reconcile with n / N")
    return {"ai": et, "n1i": nt, "ci": ec, "n2i": nc, "raw_row": row.group(0),
            "row_span": re.sub(r"\s+", " ", row.group(0)).strip(), "header_span": re.sub(r"\s+", " ", hdr.group(0)),
            "caption_span": re.sub(r"\s+", " ", cap.group(0)).strip()}


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
        if kind == "held_abstract_clause":
            v = read_abstract_clause(span)
            want = {"effect": v["effect"], "ci_low": v["ci_low"], "ci_high": v["ci_high"]}
        else:
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
