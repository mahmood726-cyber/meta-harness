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
  cache_ae_clause        a committed safety clause: explicit per-arm fractions or patient counts with percentages
                         that uniquely identify integer denominators; cache bytes and selected text are pinned
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPLAY_PROV = frozenset({"held_abstract_clause", "held_fulltext_clause", "label_adr_table", "cache_ae_clause"})
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
_CAPTION_START = re.compile(r"\bTable\s+\d+\s*[:.]|(?:^|(?<=\n))[ \t]*Table\s+\d+\b", re.I)   # 'TABLE 4:', a bare
# 'Table 4' line too (extr-r5#1, flow-r3#2)
# a caption naming a POOL of studies cannot supply one trial's counts (flow-r2#4)
_POOLED = re.compile(r"\b(?:pooled|pooling|combined|integrated|across|meta-?analy|total|both|overall)", re.I)
_ACRONYM = re.compile(r"\b[A-Z][A-Z0-9]{3,}\b")
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
    others = sorted({t for t in _TRIAL_TOKEN.findall(caption) if t.lower() != spec["trial"].lower()}
                    | {a for a in _ACRONYM.findall(caption) if a not in re.split(r"[^A-Z0-9]+", spec["trial"].upper())})
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
    _rowlike = re.compile(r"^[ \t]*[A-Za-z][^\n]*?\s\d+\s*\(\d+(?:\.\d+)?\)\s+\d+\s*\(\d+(?:\.\d+)?\)[ \t]*$")
    if any(ln.strip() and not _rowlike.match(ln) for ln in text[hdr.end():row.start()].split("\n")):
        raise ReadRefused("a non-row line stands between the arm header and the row (another population?)")
    nt, nc = (int(x.replace(",", "")) for x in hdr.groups())
    et, pt, ec, pc = row.groups()
    et, ec = int(et), int(ec)
    if not (_pct_ok(et, nt, pt) and _pct_ok(ec, nc, pc)):
        raise ReadRefused("printed percentages do not reconcile with n / N")
    return {"ai": et, "n1i": nt, "ci": ec, "n2i": nc, "raw_row": row.group(0),
            "row_span": re.sub(r"\s+", " ", row.group(0)).strip(), "header_span": re.sub(r"\s+", " ", hdr.group(0)),
            "caption_span": caption}


# ------------------------------------------------------------------------------------------------------- replay
def _unique_denominator(events: int, percentage: str) -> int:
    """Invert a rounded percentage only when exactly one integer N is possible.

    Include both rounding boundaries conservatively: the quote does not specify
    its tie-breaking convention. Zero percentages cannot identify a denominator.
    """
    p = Fraction(percentage)
    half_unit = Fraction(1, 2 * 10 ** (len(percentage.split('.')[1]) if '.' in percentage else 0))
    if events <= 0 or p <= half_unit or p > 100:
        raise ReadRefused("percentage does not identify one denominator")
    lower = events * 100 / (p + half_unit)
    upper = events * 100 / (p - half_unit)
    lo = max(events, -(-lower.numerator // lower.denominator))
    hi = upper.numerator // upper.denominator
    if lo != hi:
        raise ReadRefused("rounded percentage permits multiple denominators")
    return lo


def read_cache_ae_clause(span: str, spec: dict[str, str]) -> dict[str, int]:
    """Two patient-count grammars designed from permitted short committed quotes.

    No served numbers are inputs. Arm names and endpoint identity are literal
    selectors. Unsupported prose/tables are refused, not searched for matching digits.
    """
    if not isinstance(spec, dict) or spec.get("outcome") not in ("Adverse events", "Any adverse events"):
        raise ReadRefused("unsupported adverse-event endpoint")
    if any(not isinstance(spec.get(k), str) or not spec[k].strip() for k in ("arm_t", "arm_c")):
        raise ReadRefused("missing literal arm names")
    arm_t, arm_c = (re.escape(spec[k]) for k in ("arm_t", "arm_c"))
    integer = r"(0|[1-9]\d*)"
    pct = r"(\d+(?:\.\d+)?)"
    if spec.get("reader") == "ae_safety_fractions":
        rx = (r"Of " + integer + r" participants included in the safety analysis, only " + pct
              + r"% \(" + integer + r"/" + integer + r"\) experienced an AE: " + pct + r"% \("
              + integer + r"/" + integer + r"\) in the " + arm_t + r" and " + pct + r"% \("
              + integer + r"/" + integer + r"\) in the " + arm_c + r" group\.")
        m = re.fullmatch(rx, span)
        if not m:
            raise ReadRefused("unsupported safety-fraction clause")
        total, p, events, denom, pt, et, nt, pc, ec, nc = m.groups()
        total, events, denom, et, nt, ec, nc = map(int, (total, events, denom, et, nt, ec, nc))
        if (total != denom or total != nt + nc or events != et + ec
                or not 0 <= et <= nt or not 0 <= ec <= nc
                or not all(_pct_ok(n, d, q) for n, d, q in ((events, denom, p), (et, nt, pt), (ec, nc, pc)))):
            raise ReadRefused("safety counts, totals or percentages disagree")
    elif spec.get("reader") == "ae_patient_percentages":
        # The second sentence of the permitted quote is interpretation, not a denominator.
        rx = (r"Adverse events were similar between " + arm_t + r" and " + arm_c + r" \("
              + integer + r" \(" + pct + r"%\) versus " + integer + r" \(" + pct
              + r"%\) patients, respectively\)\.")
        m = re.fullmatch(rx + r"(?P<tail> These results indicate that [^.\r\n]+\.)?", span)
        if not m:
            raise ReadRefused("unsupported patient-percentage clause")
        # the interpretation may say nothing that changes what the percentages are or how many patients they are of:
        # estimate wording, or a stated patient count, makes a derived denominator wrong (codex b1-cap-r1 #1, P0)
        tail = m.group("tail") or ""
        if re.search(r"Kaplan|Meier|estimat|cumulative|life[- ]?table|incidence|\bper arm\b|\beach arm\b|"
                     r"\d[\d,]*\s+(?:patients|participants|subjects|people|individuals)\b", tail, re.I):
            raise ReadRefused("the interpretive sentence qualifies the percentages or states a denominator")
        et, pt, ec, pc = m.group(1), m.group(2), m.group(3), m.group(4)
        et, ec = int(et), int(ec)
        nt, nc = _unique_denominator(et, pt), _unique_denominator(ec, pc)
    else:
        raise ReadRefused("unknown adverse-event reader")
    return {"ai": et, "n1i": nt, "ci": ec, "n2i": nc}


def _cache_held_text(t: dict[str, Any], root: str) -> tuple[str, str]:
    """Pin cache bytes independently of the row, then select one PMID abstract if needed."""
    ref = t.get("document_ref")
    spec = t.get("replay") or {}
    if not isinstance(ref, str) or not re.fullmatch(r"cache/[a-z0-9-]+/(?:records\.json|ft_\d+\.txt)", ref):
        raise ReadRefused("not an allowed cache document")
    if not isinstance(spec, dict) or not re.fullmatch(r"\d+", str(spec.get("pmid", ""))):
        raise ReadRefused("missing PMID selector")
    pid = spec["pmid"]
    if str(t.get("id", "")).removeprefix("PMID ") != pid:
        raise ReadRefused("row and document PMID selectors differ")
    path = Path(root) / ref
    if not path.resolve().is_relative_to(Path(root).resolve()):
        raise ReadRefused("cache document escapes root")
    try:
        raw = path.read_bytes()
        manifest = json.loads((Path(root) / "cache" / "b1_replay_manifest.json").read_text(encoding="utf-8"))
        pin = manifest["documents"][ref]
        pinned = pin["sha256"]
        if hashlib.sha256(raw).hexdigest() != pinned or t.get("document_sha256") != pinned:
            raise ReadRefused("cache document digest differs from pinned bytes")
        text = raw.decode("utf-8")
        if ref.endswith("records.json"):
            records = [r for r in json.loads(text)["records"] if str(r.get("id")) == pid]
            if len(records) != 1 or not isinstance(records[0].get("abstract"), str):
                raise ReadRefused("PMID does not select exactly one held abstract")
            text = records[0]["abstract"]
        elif not ref.endswith(f"/ft_{pid}.txt"):
            raise ReadRefused("fulltext filename and PMID differ")
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != pin["text_sha256"]:
            raise ReadRefused("selected text differs from pinned digest")
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        # Never include source text (including JSON decoder snippets) in diagnostics.
        raise ReadRefused("cache document or pinned manifest failed validation") from None
    return text, pinned


AACT_TOTALS = "outputs/handover/in3/aact/reported_event_totals.txt"


def _aact_at_risk(text: str, nct: str) -> int:
    """The ONE subjects_at_risk the held AACT reported-event totals state for every row of `nct`; refused when the NCT
    is absent, a value is blank or not an integer, or the groups state different values (that would need a group-to-arm
    mapping this reader does not have)."""
    lines = text.splitlines()
    if not lines:
        raise ReadRefused("empty AACT totals")
    head = lines[0].split("|")
    try:
        i_nct, i_risk = head.index("nct_id"), head.index("subjects_at_risk")
    except ValueError:
        raise ReadRefused("AACT totals lack nct_id / subjects_at_risk columns") from None
    vals = set()
    for ln in lines[1:]:
        f = ln.split("|")
        if len(f) == len(head) and f[i_nct] == nct:
            if not re.fullmatch(r"[1-9]\d*", f[i_risk]):
                raise ReadRefused("an AACT row of the NCT has no integer subjects_at_risk")
            vals.add(int(f[i_risk]))
    if len(vals) != 1:
        raise ReadRefused("the held AACT totals state no single subjects_at_risk for the NCT")
    return vals.pop()


def _held_denominator(t: dict[str, Any], root: str) -> int:
    """The denominator a percentage clause is OF, read from the held AACT totals the row names (sha-pinned in the B1
    manifest): a percentage is never the source of a count (agy b1-cap-r1-agy2, P0)."""
    ds = t.get("denominator_source")
    if not isinstance(ds, dict) or ds.get("document_ref") != AACT_TOTALS or not re.fullmatch(r"NCT\d{8}", str(ds.get("nct"))):
        raise ReadRefused("no held AACT denominator source")
    try:
        raw = (Path(root) / AACT_TOTALS).read_bytes()
        manifest = json.loads((Path(root) / "cache" / "b1_replay_manifest.json").read_text(encoding="utf-8"))
        if hashlib.sha256(raw).hexdigest() != manifest["documents"][AACT_TOTALS]["sha256"]:
            raise ReadRefused("AACT totals digest differs from pinned bytes")
        return _aact_at_risk(raw.decode("utf-8"), ds["nct"])
    except (OSError, ValueError, KeyError, TypeError):
        raise ReadRefused("AACT totals or pinned manifest failed validation") from None


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
        if kind == "cache_ae_clause":
            text, pinned = _cache_held_text(t, root)
            sha = pinned  # raw bytes already checked, before selecting a records.json abstract
        else:
            text, pinned = _held_text(kind, t.get("document_ref"), root)
            sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if sha != pinned or t.get("document_sha256") != pinned:
            raise ReadRefused(f"held text sha256 {sha[:12]} / row {str(t.get('document_sha256'))[:12]} != pinned "
                              f"{pinned[:12]}")
        span = str(t.get("source_span") or "")
        if not span or span not in text:
            raise ReadRefused("the row's source_span is not verbatim in the held text")
        if kind == "cache_ae_clause":
            if any(t.get(k) is not None for k in ("effect", "ci_low", "ci_high")):
                raise ReadRefused("an adverse-event count clause never serves an effect")
            if t.get("outcome") is not None and t["outcome"] != (t.get("replay") or {}).get("outcome"):
                raise ReadRefused("row and replay endpoint selectors differ")
            want = read_cache_ae_clause(span, t.get("replay") or {})
            if (t.get("replay") or {}).get("reader") == "ae_patient_percentages":
                # the inverted percentages are a CROSS-CHECK; the denominator is the held AACT at-risk count
                n = _held_denominator(t, root)
                if want["n1i"] != n or want["n2i"] != n:
                    raise ReadRefused("percentage-derived denominators disagree with the held AACT at-risk count")
            if any(type(t.get(k)) is not int or t[k] != v for k, v in want.items()):
                raise ReadRefused("re-derived counts differ from served integers")
        elif kind in _CLAUSE_KINDS:
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
