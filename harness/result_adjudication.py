"""SIGNED RESULT-LEVEL ADJUDICATION: admit an eligible trial's result into an outcome pool from a committed decision
file, when no automated route can bind it (V1.0.1, GLP-1: FLOW is not in the screened set; ELIXA's 3-point MACE is
not in its abstract and the hand binder abstains on the regulatory text, where the 4-point primary rounds to the
same HR).

The outcome spec declares each admission under `adjudicated_results`:
    {"trial": "ELIXA", "id": "PMID 26630143", "nct": "NCT01147250",
     "decision": "evidence/glp1_adjudication/ELIXA.json", "decision_sha256": "<sha256 of the decision bytes>",
     "strand": "CONVENTIONAL_GLP1RA"}
and pins the two renderers the witnesses depend on (`adjudication_renderer_sha256` for the lane's text renderer,
`adjudication_text_extractions` {committed .pdf.txt path: sha256} for PDF sources).

Nothing is taken on trust. For every declared admission the decision bytes must hash to the pinned value; the
decision must name the same trial, PMID and NCT, record ELIGIBLE on the declared strand, and carry an estimate, a
95% interval and an HR scale; and EVERY witness in it ({ref, sha256, span}) must name held bytes whose sha256 is the
one recorded and whose rendered text contains the span verbatim (whitespace-normalised; PDF page markers ignored).
Any failure raises AdjudicationRefused: a declared admission that does not verify fails the build (fail closed),
and a row that claims this provenance without verifying is refused at admissibility.

Admission here is not signature. The served-number change it causes is recorded in docs/result_changes.json and
the publication gate refuses the page until the reviewer countersignature on that notice is signed."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
from typing import Any

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RENDERER = "evidence/scripts/textrep.py"
PROVENANCE = "signed_result_adjudication"
BINDING = "signed_result_adjudication_witnesses"
_PAGE = re.compile(r"###\s*PAGE\s+\d+|=====\s*page\s+\d+\s*=====")


class AdjudicationRefused(ValueError):
    pass


def _sha(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", _PAGE.sub(" ", s or "")).strip()


_renderer_cache: dict[str, Any] = {}
_text_cache: dict[tuple[str, str], str] = {}


def _renderer(spec: dict[str, Any], root: str):
    pinned = spec.get("adjudication_renderer_sha256")
    path = os.path.join(root, RENDERER)
    if not pinned:
        raise AdjudicationRefused("no adjudication_renderer_sha256 pinned in the outcome spec")
    got = _sha(path)
    if got != pinned:
        raise AdjudicationRefused(f"renderer {RENDERER} sha256 {got[:12]} != pinned {pinned[:12]}")
    if got not in _renderer_cache:
        s = importlib.util.spec_from_file_location("_adjudication_textrep", path)
        mod = importlib.util.module_from_spec(s)
        s.loader.exec_module(mod)
        _renderer_cache[got] = mod
    return _renderer_cache[got]


def _text(spec: dict[str, Any], ref: str, root: str) -> str:
    path = os.path.join(root, ref)
    key = (root, ref)
    if key in _text_cache:
        return _text_cache[key]
    if ref.endswith(".pdf"):
        # PDF text is never re-extracted at build time (the pinned extractor is not a build dependency): the committed
        # extraction beside the held PDF is used, and its sha256 must be pinned in the outcome spec.
        d, name = os.path.split(ref)
        if os.path.basename(d) == "held":
            d = os.path.dirname(d)
        ext = f"{d}/{name}.txt"
        pinned = (spec.get("adjudication_text_extractions") or {}).get(ext)
        if not pinned:
            raise AdjudicationRefused(f"PDF witness {ref}: its text extraction {ext} is not pinned in the outcome spec")
        got = _sha(os.path.join(root, ext))
        if got != pinned:
            raise AdjudicationRefused(f"text extraction {ext} sha256 {got[:12]} != pinned {pinned[:12]}")
        text = open(os.path.join(root, ext), encoding="utf-8").read()
    else:
        text = _renderer(spec, root).render(path)
    _text_cache[key] = _norm(text)
    return _text_cache[key]


def _witnesses(o: Any, path: str = ""):
    if isinstance(o, dict):
        if "ref" in o and "span" in o:
            yield path, o
        for k, v in o.items():
            yield from _witnesses(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _witnesses(v, f"{path}/{i}")


def verify_witness(spec: dict[str, Any], w: dict[str, Any], root: str | None = None) -> None:
    root = root or ROOT
    ref, span, want = w.get("ref"), w.get("span"), w.get("sha256")
    if not (ref and span and want):
        raise AdjudicationRefused(f"witness missing ref/span/sha256: {str(w)[:120]}")
    path = os.path.join(root, ref)
    if not os.path.exists(path):
        raise AdjudicationRefused(f"witness source {ref} is not held")
    got = _sha(path)
    if got != want:
        raise AdjudicationRefused(f"witness source {ref} sha256 {got[:12]} != recorded {want[:12]}")
    if _norm(span) not in _text(spec, ref, root):
        raise AdjudicationRefused(f"witness span not verbatim in {ref}: {span[:90]!r}")


def verify(spec: dict[str, Any], entry: dict[str, Any], root: str | None = None) -> dict[str, Any]:
    """Verify one declared admission; return the pooled row (raises AdjudicationRefused)."""
    root = root or ROOT
    for k in ("trial", "id", "decision", "decision_sha256", "strand"):
        if not entry.get(k):
            raise AdjudicationRefused(f"adjudicated_results entry lacks {k!r}: {entry}")
    dpath = os.path.join(root, entry["decision"])
    if not os.path.exists(dpath):
        raise AdjudicationRefused(f"decision {entry['decision']} is not committed")
    got = _sha(dpath)
    if got != entry["decision_sha256"]:
        raise AdjudicationRefused(f"decision {entry['decision']} sha256 {got[:12]} != pinned {entry['decision_sha256'][:12]}")
    d = json.load(open(dpath, encoding="utf-8"))
    if d.get("object") != "RESULT_LEVEL_ADJUDICATION":
        raise AdjudicationRefused(f"{entry['decision']} is not a RESULT_LEVEL_ADJUDICATION")
    if d.get("trial") != entry["trial"]:
        raise AdjudicationRefused(f"decision is for {d.get('trial')!r}, entry declares {entry['trial']!r}")
    pmid = entry["id"].replace("PMID", "").strip()
    if str(d.get("pmid")) != pmid or (entry.get("nct") and d.get("nct") != entry["nct"]):
        raise AdjudicationRefused(f"decision identity {d.get('pmid')}/{d.get('nct')} != entry {entry['id']}/{entry.get('nct')}")
    decision = str((d.get("eligibility") or {}).get("decision") or "")
    # Exact prefix, never a substring: FREEDOM-CVO's decision NAMES the primary strand in order to exclude itself
    # ("ELIGIBLE for GLP1RA_ANY_DELIVERY only; NOT in the CONVENTIONAL_GLP1RA primary pool").
    if not decision.startswith(f"ELIGIBLE -- {entry['strand']} (primary)"):
        raise AdjudicationRefused(f"{entry['trial']}: decision {decision[:80]!r} does not admit it on strand {entry['strand']}")
    if not str(spec.get("name") or "").strip().lower().startswith("3-point major adverse cardiovascular"):
        raise AdjudicationRefused(f"decision binds the 3-point MACE result; outcome is {spec.get('name')!r}")
    b = d.get("bound_result") or {}
    est, ci = b.get("estimate") or {}, b.get("ci") or {}
    lo_hi = ci.get("value") or []
    if est.get("value") is None or len(lo_hi) != 2 or est.get("scale") != (spec.get("estimand") or "HR"):
        raise AdjudicationRefused(f"{entry['trial']}: bound result lacks estimate/interval on the outcome's scale")
    if ci.get("level") not in (0.95, 95):
        raise AdjudicationRefused(f"{entry['trial']}: interval level {ci.get('level')} is not 95%")
    e, lo, hi = float(est["value"]), float(lo_hi[0]), float(lo_hi[1])
    if not lo <= e <= hi:
        raise AdjudicationRefused(f"{entry['trial']}: estimate {e} outside its interval ({lo}, {hi})")
    ws = list(_witnesses(d))
    if not ws:
        raise AdjudicationRefused(f"{entry['trial']}: decision carries no witnesses")
    for _, w in ws:
        verify_witness(spec, w, root)
    # The numbers themselves are witnessed: estimate AND both bounds, as written, inside ONE verified span of the
    # bound result (a decision edited to a different tuple and re-pinned still has no span that carries it).
    toks = [f"{x:.2f}" if len(f"{x:g}") < 4 else f"{x:g}" for x in (e, lo, hi)]
    carrier = next((p for p, w in _witnesses(b) if all(
        re.search(r"(?<![\d.])" + re.escape(t) + r"(?!\d)", w["span"]) for t in toks)), None)
    if carrier is None:
        raise AdjudicationRefused(f"{entry['trial']}: no witnessed span of the bound result carries "
                                  f"{toks[0]} ({toks[1]}, {toks[2]}) together")
    fields = sorted({p.split("/")[2] if p.startswith("/bound_result/") else p.split("/")[1] for p, _ in ws})
    return {
        "label": entry["trial"], "id": entry["id"], "effect": e, "ci_low": lo, "ci_high": hi,
        "scale": est["scale"], "provenance": PROVENANCE,
        "result_adjudication": {"decision": entry["decision"], "decision_sha256": got, "strand": entry["strand"],
                                "witnesses_verified": len(ws), "fields_witnessed": fields,
                                "tuple_witnessed_by": "bound_result" + carrier,
                                "protocol": d.get("protocol"),
                                **({"source_conflict": b["source_conflict"]} if b.get("source_conflict") else {})},
        "endpoint_result_span": ((b.get("analysis") or {}).get("witness") or {}).get("span")
                                or (b.get("endpoint") or {}).get("span"),
        "endpoint_definition_span": (b.get("endpoint") or {}).get("span"),
        "document_ref": ((b.get("endpoint") or {}).get("ref")),
        "source": (f"{entry['trial']} ({entry['id']}, {d.get('nct')}): 3-point MACE HR {e:g} (95% CI {lo:g}-{hi:g}), "
                   f"admitted by signed result-level adjudication {entry['decision']} "
                   f"(sha256 {got[:12]}; {len(ws)} witness spans verified against held bytes)"),
    }


def admitted_rows(spec: dict[str, Any], root: str | None = None) -> list[dict[str, Any]]:
    root = root or ROOT
    return [verify(spec, entry, root) for entry in (spec.get("adjudicated_results") or [])]


def reverify_row(spec: dict[str, Any], row: dict[str, Any], root: str | None = None) -> str | None:
    """Admissibility check for a row claiming this provenance: None if it is exactly what its declared, verified
    admission produces; otherwise the reason it is refused."""
    root = root or ROOT
    entry = next((e for e in (spec.get("adjudicated_results") or []) if e.get("id") == row.get("id")), None)
    if entry is None:
        return f"{row.get('label')}: claims {PROVENANCE} but the outcome declares no such admission"
    try:
        want = verify(spec, entry, root)
    except AdjudicationRefused as exc:
        return str(exc)
    for k in ("effect", "ci_low", "ci_high", "scale"):
        if row.get(k) != want[k]:
            return f"{row.get('label')}: row {k}={row.get(k)!r} differs from its verified decision ({want[k]!r})"
    return None
