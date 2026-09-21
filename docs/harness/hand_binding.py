"""Bind a HAND-EXTRACTED row (verified_effects / verified_arms, any override route) to HELD BYTES, or abstain.

M2 (Mahmood, 2026-09-20), measured on the served release 8b1fb37d through the real route: UNBOUND_LEGACY
was the dominant admission path (121 of 145 pooled rows on 30 of 32 pages); on the hand-verified route a
wrong tuple BROKE the abstract binding and the row was admitted because it no longer matched -- a gate whose
failure mode is "admit" rewards exactly the input it exists to stop -- and a hand-written `source` string
saying 0.68 while the held abstract says 0.86 was pooled as 0.68 (0.77-0.96) with `verified: verified`:
the haystack was the self-authored string.

This module is the narrow typed object for that route ONLY (the abstract machine-extraction route keeps
`classify_bound`; registry and derived provenance keep their own binder). Everything it reads comes from the
document `document_ref` names, checked against `document_sha256` when the entry carries one:

  * the tuple (effect + both limits, or per-arm events with denominator-or-percentage) is located in the held
    text -- in ONE prose sentence, or in ONE table row read together with its row label, section heading,
    column headers and caption;
  * endpoint ownership is read from that span (its own components; or the definition span the sentence names,
    resolved in the PROSE only -- never a reference-list or front-matter chunk; or, for single-event / harm
    outcomes, the outcome family named by the row label + heading);
  * the scale word, a declared CI level, a declared comparator direction and a declared analysis set are
    checked against the same bytes;
  * AMBIGUITY ABSTAINS: several candidate spans, several definitions, a tuple straddling two results, or a
    cited span that does not hold the tuple -> ENDPOINT_UNBOUND with the candidates listed. It never chooses.

The row's `source` field is never searched.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

from . import extract

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HAND_PROVENANCE = {"abstract_verified", "fulltext_verified", "fulltext_verified_arms", "abstract_verified_arms"}
BOUND = "BOUND"
ABSTAIN = "ABSTAIN"
NOT_HELD = "NOT_HELD"

_SCALE_WORDS = {
    "HR": (r"hazard ratio", r"\bHR\b"),
    "OR": (r"odds ratio", r"\bOR\b"),
    "RR": (r"relative risk", r"risk ratio", r"\bRR\b"),
    "IRR": (r"incidence rate ratio", r"rate ratio", r"\bIRR\b"),
    "RD": (r"risk difference", r"rate difference", r"\bRD\b"),
    "MD": (r"mean difference", r"\bMD\b"),
}
_REF_JUNK = re.compile(r"10\.\d{4}/|\bPMC\d{5,}|pmc-[a-z-]+|\.pdf\b|All Rights Reserved", re.I)
_EN_DASH = str.maketrans({"–": "-", "—": "-", "−": "-", "·": ".", " ": " ", " ": " "})


# ----------------------------------------------------------------------------- held document
def is_hand_row(row: dict[str, Any]) -> bool:
    return bool(row.get("provenance") in HAND_PROVENANCE or row.get("document_ref") or row.get("source_span"))


def _pid(row: dict[str, Any]) -> str:
    return str(row.get("id") or "").replace("PMID ", "").strip()


def resolve_document(ref: str | None, pid: str | None = None) -> dict[str, Any] | None:
    """`cache/<slug>/records.json#PMID-<pid>` -> that record's abstract; any other ref -> the file's text.
    Returns {ref, path, text, representation, sha256} or None when the file is not held."""
    if not ref:
        return None
    path, _, frag = str(ref).partition("#")
    full = os.path.join(ROOT, path)
    if not os.path.isfile(full):
        return None
    with open(full, "rb") as f:
        raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()
    if path.endswith("records.json"):
        want = (frag.replace("PMID-", "").replace("PMID ", "").strip() or pid or "").strip()
        try:
            data = json.loads(raw.decode("utf-8"))
        except ValueError:
            return None
        # The primary `records` list first, then any other held list of records in the same file (companion
        # reports such as `hhf_source_records`): a record we hold is a document we hold, whichever list it is in.
        lists = [data.get("records") or []] + [v for k, v in data.items()
                                               if k != "records" and isinstance(v, list)
                                               and v and all(isinstance(x, dict) and "abstract" in x for x in v)]
        rec = next((r for lst in lists for r in lst if str(r.get("id")) == want), None)
        if rec is None:
            return None
        text = rec.get("abstract") or ""
        return {"ref": ref, "path": path, "text": text, "representation": "abstract", "sha256": sha}
    text = raw.decode("utf-8", errors="replace")
    rep = "xml" if ("<table-wrap" in text or "<sec" in text or "<p " in text) else "text"
    return {"ref": ref, "path": path, "text": text, "representation": rep, "sha256": sha}


# ----------------------------------------------------------------------------- spans
def _plain(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def _sentences(prose: str) -> list[str]:
    """The repo's sentence rule, plus a split after ')' + '.' when a digit starts the next sentence
    ('... p=0.067). 2347 (47.4%) participants ...' is two sentences)."""
    out = []
    for x in extract._sentences(extract._norm(prose or "")):
        for p in re.split(r"(?<=\)\.)\s+(?=\d)", x):
            p = p.strip()
            if p:
                out.append(p)
    return out


def _cells(row_xml: str) -> list[str]:
    return [_plain(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_xml, flags=re.S)]


def table_rows(doc_text: str) -> list[dict[str, Any]]:
    """Every data row of every <table-wrap>, with the context the bytes carry: caption, column headers and the
    nearest preceding heading rows (rows with a single non-numeric cell)."""
    rows = []
    for tw in re.finditer(r"<table-wrap.*?</table-wrap>", doc_text, flags=re.S):
        block = tw.group(0)
        caption = _plain(" ".join(re.findall(r"<caption>(.*?)</caption>", block, flags=re.S)))
        headers = _plain(" | ".join(" | ".join(_cells(r)) for r in re.findall(r"<thead>.*?</thead>", block, flags=re.S)))
        headings: list[str] = []
        body = re.search(r"<tbody>(.*?)</tbody>", block, flags=re.S)
        for r in re.findall(r"<tr>.*?</tr>", body.group(1) if body else block, flags=re.S):
            cells = _cells(r)
            nonempty = [c for c in cells if c]
            if len(nonempty) <= 1 and nonempty and not re.search(r"\d", nonempty[0]):
                headings.append(nonempty[0])
                continue
            rows.append({"xml": r, "offset": tw.start() + block.find(r), "label": nonempty[0] if nonempty else "",
                         "cells": cells, "section_heading": headings[-1] if headings else "",
                         "column_header": headers, "caption": caption,
                         "footnotes": _plain(" ".join(re.findall(r"<table-wrap-foot>(.*?)</table-wrap-foot>", block, flags=re.S)))})
    return rows


_TEXT_TABLES_MARK = re.compile(r"^=== TABLES\b.*$", flags=re.M)


def text_table_rows(doc_text: str) -> list[dict[str, Any]]:
    """The flattened serialisation (pmc_<pid>_fulltext.txt): after '=== TABLES ... ===', each 'TABLE <caption>'
    line opens a table whose rows are ' | '-joined cells; the rows before the first row carrying a digit-only
    result are the column headers; a single-cell non-numeric row is a section heading. Same shape as table_rows."""
    m = _TEXT_TABLES_MARK.search(doc_text)
    if not m:
        return []
    rows: list[dict[str, Any]] = []
    caption, headers, headings, header_rows = "", "", [], []
    in_header = False
    for line in doc_text[m.end():].splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("TABLE "):
            caption, headings, header_rows, in_header = line[len("TABLE "):].strip(), [], [], True
            headers = ""
            continue
        cells = [c.strip() for c in line.split(" | ")]
        nonempty = [c for c in cells if c]
        if in_header and not re.search(r"\d\s*\(|\d+\.\d|^\d+$", " ".join(cells[1:]) if len(cells) > 1 else ""):
            header_rows.append(line)
            headers = _plain(" | ".join(header_rows))
            continue
        in_header = False
        if len(nonempty) <= 1 and nonempty and not re.search(r"\d", nonempty[0]):
            headings.append(nonempty[0])
            continue
        rows.append({"xml": line, "offset": None, "label": nonempty[0] if nonempty else "", "cells": cells,
                     "section_heading": headings[-1] if headings else "", "column_header": headers,
                     "caption": caption, "footnotes": ""})
    return rows


def prose_of(doc: dict[str, Any]) -> str:
    text = doc["text"]
    if doc["representation"] == "abstract":
        return text
    if doc["representation"] == "text":
        m = _TEXT_TABLES_MARK.search(text)
        return text[:m.start()] if m else text
    text = re.sub(r"<table-wrap.*?</table-wrap>", " ", text, flags=re.S)
    text = re.sub(r"<ref-list.*?</ref-list>", " ", text, flags=re.S)
    # front matter minus the abstract (a PMC file may hold ONLY front matter when the publisher blocks the body)
    for tag in ("journal-meta", "permissions", "contrib-group", "author-notes", "back", "floats-group"):
        text = re.sub(rf"<{tag}\b.*?</{tag}>", " ", text, flags=re.S)
    text = re.sub(r"<article-id[^>]*>.*?</article-id>", " ", text, flags=re.S)
    # citation markers (<xref>10</xref>) are not prose: left in place they glue sentences together
    text = re.sub(r"<xref[^>]*>.*?</xref>", " ", text, flags=re.S)
    return re.sub(r"<[^>]+>", " ", text)


# ----------------------------------------------------------------------------- tuple location
def _forms(v) -> set[str]:
    f = float(v)
    return {f"{f:g}", f"{f:.1f}", f"{f:.2f}", f"{f:.3f}"}


def _present(text: str, forms: set[str]) -> bool:
    return any(re.search(r"(?<![\d.])" + re.escape(x) + r"(?![\d])", text) for x in forms)


def _pct(events, n) -> set[str]:
    if not n:
        return set()
    r = 100.0 * float(events) / float(n)
    return {f"{r:.1f}", f"{round(r)}", f"{r:.2f}"}


def _tuple_of(row: dict[str, Any]) -> dict[str, Any] | None:
    if row.get("effect") is not None:
        return {"kind": "effect", "effect": row["effect"], "ci_low": row.get("ci_low"), "ci_high": row.get("ci_high"),
                "scale": row.get("scale")}
    if row.get("ai") is not None and row.get("ci") is not None:
        return {"kind": "counts", "ai": row["ai"], "n1i": row.get("n1i"), "ci": row["ci"], "n2i": row.get("n2i")}
    if row.get("mean1") is not None:
        return {"kind": "continuous", "mean1": row["mean1"], "sd1": row.get("sd1"), "mean2": row["mean2"], "sd2": row.get("sd2")}
    return None


def _tuple_in(text: str, tup: dict[str, Any], extra_context: str = "") -> bool:
    """Every number of the tuple in this text (denominators may sit in the extra context, i.e. column headers)."""
    t = (text or "").translate(_EN_DASH).replace(",", "")
    ctx = (extra_context or "").translate(_EN_DASH).replace(",", "")
    if tup["kind"] == "effect":
        if not _present(t, _forms(tup["effect"])):
            return False
        for k in ("ci_low", "ci_high"):
            if tup.get(k) is not None and not _present(t, _forms(tup[k])):
                return False
        return True
    if tup["kind"] == "counts":
        for ev, n in ((tup["ai"], tup.get("n1i")), (tup["ci"], tup.get("n2i"))):
            if not _present(t, _forms(ev)):
                return False
            den_ok = n is not None and (_present(t, _forms(n)) or _present(ctx, _forms(n)))
            pct_ok = n is not None and _present(t, _pct(ev, n))
            if not (den_ok or pct_ok):
                return False
        return True
    if tup["kind"] == "continuous":
        return all(_present(t, _forms(tup[k])) for k in ("mean1", "mean2") if tup.get(k) is not None)
    return False


def _effect_pattern_ok(sentence: str, tup: dict[str, Any]) -> bool:
    """For an effect tuple in prose: the point must precede its bounds inside one result clause."""
    t = sentence.translate(_EN_DASH).replace(",", "")
    if tup.get("ci_low") is None or tup.get("ci_high") is None:
        return True
    pos = {}
    for k in ("effect", "ci_low", "ci_high"):
        m = None
        for f in sorted(_forms(tup[k]), key=len, reverse=True):
            m = re.search(r"(?<![\d.])" + re.escape(f) + r"(?![\d])", t)
            if m:
                break
        if not m:
            return False
        pos[k] = m.start()
    return pos["effect"] < pos["ci_low"] < pos["ci_high"]


def candidates(doc: dict[str, Any], tup: dict[str, Any]) -> list[dict[str, Any]]:
    """Every held span that carries the whole tuple: prose sentences and table rows (with context)."""
    out = []
    # The flattened serialisation ALSO carries each table in place as run-on text without cell boundaries; a
    # prose 'sentence' that contains a structured row's cells is that row's debris, not a second owner.
    debris = ([_plain(" ".join(r["cells"])).translate(_EN_DASH)
               for r in text_table_rows(doc["text"]) if _tuple_in(" | ".join(r["cells"]), tup)]
              if doc["representation"] == "text" else [])
    for s in _sentences(prose_of(doc)):
        if _tuple_in(s, tup) and (tup["kind"] != "effect" or _effect_pattern_ok(s, tup)):
            if debris and any(d and d in _plain(s).translate(_EN_DASH) for d in debris):
                continue
            out.append({"kind": "sentence", "text": s, "spans": [{"role": "result", "text": s}]})
    if doc["representation"] in ("xml", "text"):
        for r in (table_rows(doc["text"]) if doc["representation"] == "xml" else text_table_rows(doc["text"])):
            joined = " | ".join(r["cells"])
            if _tuple_in(joined, tup, r["column_header"]):
                spans = [{"role": "result", "text": joined}, {"role": "row_label", "text": r["label"]}]
                if r["section_heading"]:
                    spans.append({"role": "section_heading", "text": r["section_heading"]})
                if r["column_header"]:
                    spans.append({"role": "column_header", "text": r["column_header"]})
                if r["caption"]:
                    spans.append({"role": "caption", "text": r["caption"]})
                out.append({"kind": "table_row", "text": joined, "xml": r["xml"], "spans": spans,
                            "label": r["label"], "section_heading": r["section_heading"],
                            "column_header": r["column_header"], "caption": r["caption"],
                            "footnotes": r["footnotes"]})
    return out


def _within_cited_span(cand: dict[str, Any], cited: str) -> bool:
    if not cited:
        return True
    c = _plain(cited).translate(_EN_DASH)
    if cand["kind"] == "table_row":
        return cand["xml"] in cited or _plain(cand["xml"]).translate(_EN_DASH) in c or (
            cand["xml"].translate(_EN_DASH) in c)
    s = cand["text"].translate(_EN_DASH)
    return s[:80] in c or c[:80] in s or s in c


# ----------------------------------------------------------------------------- ownership and checks
def _family_match_tolerant(spec: dict[str, Any], text: str) -> bool:
    """The repo's keyword-family rule (target_endpoint._keyword_family_match) with plural/singular tolerance:
    the served vocabulary lists 'gastrointestinal adverse events'; REWIND's sentence says 'a gastrointestinal
    adverse event'."""
    from . import target_endpoint as te
    if te._keyword_family_match(spec, text):
        return True
    s = re.sub(r"s\b", "", te._fold(text))
    for kw in spec.get("keywords") or []:
        k = re.sub(r"s\b", "", te._fold(kw))
        if len(k) > 3 and k in s:
            return True
    return False


def _definition_binding(prose: str, sentence: str) -> dict[str, Any]:
    """bind_result_span over the PROSE only, with reference-list / front-matter chunks excluded from the
    definition pool (CARMELINA's reference list impersonated a definition span)."""
    from . import target_endpoint as te
    clean = " ".join(s for s in _sentences(prose) if not _REF_JUNK.search(s))
    return te.bind_result_span(clean, sentence)


_LABEL_STOP = {"outcome", "outcomes", "end", "point", "points", "endpoint", "endpoints", "the", "of", "a", "an",
               "event", "events", "measure", "variable"}


def _label_definition(prose: str, cand: dict[str, Any]) -> dict[str, Any]:
    """A table label that NAMES an endpoint ('Primary composite outcome', 'Expanded composite outcome') resolves to
    the definition span whose text carries the label's own words -- in the prose or in the table's own footnotes --
    never to 'the only definition around' (LEADER's expanded composite would otherwise inherit the primary's
    definition and pass as 3-point MACE). Several matching definitions with different component sets abstain."""
    from . import target_endpoint as te
    words = [w for w in re.sub(r"[^a-z ]", " ", cand["label"].lower()).split() if w not in _LABEL_STOP]
    clean = " ".join(s for s in _sentences(prose) if not _REF_JUNK.search(s))
    pool = te._definition_sentences(clean + " " + (cand.get("footnotes") or ""))
    hits = [d for d in pool if all(w in d["span"].lower() for w in words)] if words else []
    sets = {frozenset(d["components"]) for d in hits}
    if len(sets) == 1:
        d = hits[0]
        return {"binding": te.BINDING_DEFINITION, "endpoint_result_span": cand["text"],
                "endpoint_definition_span": d["span"], "components": set(d["components"]),
                "binding_reason": f"table label '{cand['label']}' names an endpoint; one definition span carries the label's words"}
    reason = (f"table label '{cand['label']}' names an endpoint but the held text holds no definition span carrying its words"
              if not sets else f"table label '{cand['label']}' resolves to {len(sets)} different definitions")
    return {"binding": te.BINDING_NONE, "endpoint_result_span": cand["text"], "endpoint_definition_span": None,
            "components": set(), "binding_reason": reason}


_RESULT_PAREN = re.compile(r"[\[(][^\[\]()]*\d[^\[\]()]*(?:95\s*%|CI)[^\[\]()]*[\])]")
_LEADING_JOIN = re.compile(r"^\s*(?:[,;]\s*)?(?:as was|as were|and|whereas|while|but)\b\s*", flags=re.I)


def _owning_clause(sentence: str, tup: dict[str, Any] | None, names_endpoint) -> str:
    """In a sentence carrying SEVERAL parenthesised results, the text attached to OUR result -- from the end of
    the previous result to the start of ours -- owns it (CANVAS HF: '... composite (HR, 0.78 ...), as was fatal
    or hospitalized HF (HR, 0.70 ...) and hospitalized HF alone (HR, 0.67; 95% CI, 0.52-0.87)'). When that
    attachment names no endpoint (CARMELINA: '... per 100 person-years) (HR, 1.02 ...)' after a rate-difference
    parenthesis), it extends back over earlier attachments until something does, or to the sentence start.
    With one result, the sentence is the clause."""
    if not tup or tup.get("kind") != "effect":
        return sentence
    parens = list(_RESULT_PAREN.finditer(sentence))
    if len(parens) < 2:
        return sentence
    idx = next((i for i, m in enumerate(parens) if _tuple_in(m.group(0), tup)), None)
    if idx is None:
        return sentence
    start = idx
    while start >= 0:
        begin = parens[start - 1].end() if start > 0 else 0
        clause = _LEADING_JOIN.sub("", sentence[begin:parens[idx].end()]).strip(" ,;")
        if names_endpoint(sentence[begin:parens[idx].start()]):
            return clause
        start -= 1
    return sentence


def _ownership(spec: dict[str, Any], cand: dict[str, Any], prose: str, tup: dict[str, Any] | None = None) -> dict[str, Any]:
    from . import target_endpoint as te
    if cand["kind"] == "table_row":
        own_text = " ; ".join(x for x in (cand["label"], cand["section_heading"], cand["caption"]) if x)
    else:
        own_text = _owning_clause(cand["text"], tup, lambda x: bool(
            te._components_from_text(x, expand_named_composites=False)
            or te._NAMED_COMPOSITE_RX.search(x.lower()) or _family_match_tolerant(spec, x)))
    canon = te.canonical_components(spec)
    own = te._components_from_text(own_text, expand_named_composites=False)
    if own:
        cls = te._classify(spec, own_text, components=own)
        cls.update({"endpoint_binding": te.BINDING_SELF, "endpoint_result_span": cand["text"],
                    "endpoint_definition_span": own_text,
                    "endpoint_binding_reason": "span names its own component set: " + ", ".join(sorted(own))})
        return cls
    if te._NAMED_COMPOSITE_RX.search(own_text.lower()):
        if cand["kind"] == "table_row":
            b = _label_definition(prose, cand)
        else:
            b = _definition_binding(prose, own_text)
        if b["binding"] == te.BINDING_NONE:
            out = te._unbound_classification(b)
            out["endpoint_result_span"] = cand["text"]
            return out
        cls = te._classify(spec, b["endpoint_definition_span"], components=b["components"])
        cls.update({"endpoint_binding": b["binding"], "endpoint_result_span": cand["text"],
                    "endpoint_definition_span": b["endpoint_definition_span"],
                    "endpoint_binding_reason": b["binding_reason"],
                    **{k: b[k] for k in ("definition_candidates", "endpoint_reference", "selected_definition",
                                        "unresolved_alternatives") if k in b}})
        return cls
    if not canon:
        ok = _family_match_tolerant(spec, own_text)
        return {"target_endpoint_class": te.EXACT_TARGET if ok else te.DIFFERENT_OUTCOME,
                "target_components": [], "extra_components": [], "missing_components": [],
                "component_distance": 0 if ok else 999,
                "endpoint_binding": te.BINDING_SELF, "endpoint_result_span": cand["text"],
                "endpoint_definition_span": own_text,
                "endpoint_binding_reason": ("span names the outcome family" if ok
                                            else "span names neither the outcome family nor a component")}
    return te._unbound_classification({"binding": te.BINDING_NONE, "endpoint_result_span": cand["text"],
                                       "endpoint_definition_span": None, "components": set(),
                                       "binding_reason": "span names neither components nor an endpoint"})


def _scale_ok(scale: str | None, cand: dict[str, Any]) -> str | None:
    if not scale:
        return None
    words = _SCALE_WORDS.get(str(scale).upper())
    if not words:
        return None
    hay = cand["text"] + " " + cand.get("column_header", "")
    if any(re.search(w, hay, flags=re.I if not w.startswith(r"\b") else 0) for w in words):
        return None
    stated = [k for k, ws in _SCALE_WORDS.items() if any(re.search(w, hay, flags=re.I if not w.startswith(r"\b") else 0) for w in ws)]
    return f"scale '{scale}' is not stated in the located span" + (f" (the span states {', '.join(stated)})" if stated else "")


def _direction_ok(declared: str | None, cand: dict[str, Any]) -> str | None:
    """A declared 'A vs B' must agree with the order the held span names the arms in."""
    if not declared:
        return None
    m = re.match(r"\s*(.+?)\s+(?:vs\.?|versus)\s+(.+?)\s*$", str(declared), flags=re.I)
    if not m:
        return None
    a, b = m.group(1).lower(), m.group(2).lower()
    hay = (cand["text"] + " " + cand.get("column_header", "") + " " + cand.get("caption", "")).lower()
    pa, pb = hay.find(a), hay.find(b)
    if pa < 0 or pb < 0:
        return f"declared comparator direction '{declared}' names an arm the located span does not"
    if pa > pb:
        return (f"declared comparator direction '{declared}' contradicts the held span, which names "
                f"'{b}' before '{a}'")
    return None


def _analysis_set_ok(declared: str | None, cand: dict[str, Any]) -> str | None:
    if not declared:
        return None
    hay = (cand["text"] + " " + cand.get("section_heading", "") + " " + cand.get("column_header", "")
           + " " + cand.get("caption", "")).lower()
    d = str(declared).lower()
    if d in hay or d.replace("-", " ") in hay:
        return None
    return f"declared analysis set '{declared}' is not stated in the located span"


def _ci_pct_ok(declared, cand: dict[str, Any]) -> str | None:
    if declared is None:
        return None
    hay = cand["text"] + " " + cand.get("column_header", "")
    if re.search(r"(?<![\d.])" + re.escape(f"{float(declared):g}") + r"\s*%", hay):
        return None
    return f"declared CI level {declared}% is not stated in the located span"


# ----------------------------------------------------------------------------- the binder
def bind_hand_row(spec: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    """Returns the classification fields for a hand row plus `hand_binding_state` (BOUND / ABSTAIN / NOT_HELD),
    `spans`, `held_document`, and on ABSTAIN `candidate_locations` and `endpoint_binding_reason`."""
    from . import target_endpoint as te
    tup = _tuple_of(row)
    pid = _pid(row)
    refs = [r for r in [row.get("document_ref")] + list(row.get("document_candidates") or []) if r]
    doc = None
    for ref in refs:
        doc = resolve_document(ref, pid)
        if doc:
            break
    if doc is None and row.get("handed_abstract") and not row.get("document_ref"):
        # no held FILE resolves (a fixture, or a record outside records.json): the abstract the pipeline was handed
        # is the document, named as such -- never a hand-written source string
        text = str(row["handed_abstract"])
        doc = {"ref": f"record:{pid or row.get('id')} (abstract handed to the pipeline)", "path": None, "text": text,
               "representation": "abstract", "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}

    def _abstain(reason: str, cands=None, state=ABSTAIN):
        out = te._unbound_classification({"binding": te.BINDING_NONE, "endpoint_result_span": None,
                                          "endpoint_definition_span": None, "components": set(),
                                          "binding_reason": reason})
        out["hand_binding_state"] = state
        out["held_document"] = {"ref": doc["ref"], "sha256": doc["sha256"], "representation": doc["representation"]} if doc else {"ref": refs[0] if refs else None}
        out["candidate_locations"] = [{"kind": c["kind"], "text": c["text"][:240],
                                       **({"row_label": c["label"], "section_heading": c["section_heading"]} if c["kind"] == "table_row" else {})}
                                      for c in (cands or [])][:6]
        return out

    if tup is None:
        return _abstain("row carries no extractable tuple")
    if doc is None:
        return _abstain("the document the entry names is not held" + (f" ({refs[0]})" if refs else " (no document_ref)"), state=NOT_HELD)
    if row.get("document_sha256") and row["document_sha256"] != doc["sha256"]:
        return _abstain(f"held document {doc['ref']} changed since the approval (sha256 {doc['sha256'][:12]} != "
                        f"approved {str(row['document_sha256'])[:12]}): the approval is stale")
    cands = candidates(doc, tup)
    cited = row.get("source_span") or ""
    if cited and cands:
        inside = [c for c in cands if _within_cited_span(c, cited)]
        if not inside:
            return _abstain("the tuple is not located in the cited span; it is located elsewhere in the held document", cands)
        cands = inside
    if not cands:
        return _abstain(f"tuple not located in the held document {doc['ref']} ({doc['representation']}): no span carries it")
    prose = prose_of(doc)
    duplicates = 0
    if len(cands) > 1:
        # Ambiguity is several OWNERS for one tuple (L9: the MI row and the stroke row both carry 0.86), not
        # several copies under one owner (a results sentence and the table row that names the same endpoint).
        owners = [_ownership(spec, c, prose, tup) for c in cands]
        keys = {(o["target_endpoint_class"], tuple(o.get("extra_components") or []),
                 tuple(o.get("missing_components") or [])) for o in owners}
        if len(keys) != 1 or owners[0]["target_endpoint_class"] not in (te.EXACT_TARGET, te.NEAR_MATCH):
            # several locations under one FOREIGN owner (or none) is not a refusal of a located result -- it is a
            # tuple that was not located (colchicine-postop-af: the count '1' matched '1 mg' three times)
            return _abstain(f"tuple located in {len(cands)} spans of the held document; ambiguity abstains", cands)
        duplicates = len(cands) - 1
        cands = [next((c for c in cands if c["kind"] == "sentence"), cands[0])]
    cand = cands[0]
    for problem in (_scale_ok(row.get("scale") if tup["kind"] == "effect" else None, cand),
                    _ci_pct_ok(row.get("ci_pct"), cand),
                    _analysis_set_ok(row.get("analysis_set"), cand)):
        if problem:
            out = _abstain(problem, [cand])
            out["endpoint_result_span"] = cand["text"]
            return out
    direction = _direction_ok(row.get("comparator_direction"), cand)
    cls = _ownership(spec, cand, prose, tup)
    cls["hand_binding_state"] = BOUND if cls["target_endpoint_class"] != te.ENDPOINT_UNBOUND else ABSTAIN
    cls["spans"] = cand["spans"]
    if duplicates:
        cls["duplicate_locations"] = duplicates
    cls["held_document"] = {"ref": doc["ref"], "sha256": doc["sha256"], "representation": doc["representation"]}
    if direction:
        cls["direction_conflict"] = direction
    return cls
