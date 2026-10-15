"""Opt-in held-source locators for B1; no extracted numbers are stored here.

Static: report identities, endpoint/column labels, table locations and aliases.
Dynamic: values, denominators, percentages, licence decisions, spans and digests.
Every route re-reads held bytes; failures refuse the row, never use a hand fallback.
"""
import csv
import hashlib
import io
import json
import re
from pathlib import Path

from . import copy_licence, extract
from .table_rows import plain, read_row

ROOT = Path(__file__).resolve().parents[1]
HF = "Hospitalization for heart failure"
# Report locators, not numerical extraction answers.
ROUTES = {
    ("dapagliflozin-hfpef-hosp", "Adverse events", "34711976"): {"route": "aact_abstract"},
    ("esketamine-trd-madrs", "Adverse events", "37025256"): {
        "table_label": "Table 4", "row_label": "TEAEs", "intervention": "esketamine", "comparator": "placebo"},
    ("glp1-ra-mace-t2d", "Adverse events leading to discontinuation", "27295427"): {
        "table_label": "Table 2", "row_label": "Any adverse event", "intervention": "liraglutide", "comparator": "placebo",
        "group": "Adverse event leading to permanent discontinuation of trial regimen"},
    ("melatonin-primary-insomnia-sol", "Adverse events", "20712869"): {
        "table_label": "Table 8", "row_label": "Any AE", "intervention": "PRM", "comparator": "placebo", "period": "Treatment period"},
    ("probiotics-aad-prevention", "Any adverse events", "39529939"): {"route": "sentence_counts"},
    ("probiotics-aad-prevention", "Any adverse events", "41699149"): {
        "table_label": "Table 4", "row_label": "Total Number of People with AEs", "intervention": "active", "comparator": "control", "proportions": True},
    ("sglt2-ckd-progression", "Diabetic ketoacidosis", "36331190"): {
        "table_label": "Table 2", "row_label": "Ketoacidosis", "intervention": "empagliflozin", "comparator": "placebo"},
    ("sglt2-ckd-progression", "Lower-limb amputation", "36331190"): {
        "table_label": "Table 2", "row_label": "Lower limb amputation", "intervention": "empagliflozin", "comparator": "placebo", "effect": True},
    ("sglt2-primary-prevention-hf", HF, "26378978"): {"route": "sentence_hr", "report": "26819227", "file": "pmc_26819227_fulltext.txt"},
    ("sglt2-primary-prevention-hf", HF, "28605608"): {"route": "sentence_hr", "report": "29526832", "abstract": True},
    ("sglt2-primary-prevention-hf", HF, "32966714"): {"route": "sentence_hr", "report": "33026243", "abstract": True},
}


def _record(data, pid):
    hits = [r for value in data.values() if isinstance(value, list)
            for r in value if isinstance(r, dict) and str(r.get("id")) == pid]
    abstracts = {r.get("abstract", "") for r in hits}
    if len(abstracts) != 1 or not next(iter(abstracts)):
        raise ValueError("REPORT_ABSTRACT_UNBOUND")
    return hits[0]


def sentence_hr(text):
    """Bind each HR to its immediately preceding endpoint clause, never a generic HR keyword."""
    hits = []
    for sentence in extract._sentences(text):
        for match in extract._EFFECT.finditer(sentence):
            # A previous result's closing bracket ends its endpoint clause. This
            # keeps 'fatal or hospitalized HF' distinct from 'hospitalized HF alone'.
            prior = [m for m in extract._EFFECT.finditer(sentence[:match.start()])]
            start = prior[-1].end() if prior else 0
            clause = sentence[start:match.start()]
            if not re.search(r"hospitali[sz]ation for heart failure|hospitalized HF alone|first HHF", clause, re.I):
                continue
            if re.search(r"\bdeath\b|\bfatal\b|\bcomposite\b", clause, re.I):
                continue
            effect = extract._effect_from_match(match, clause)
            if effect and effect[0] == "HR":
                # Keep the clause and numeric match as one verbatim slice.
                start = match.start() - len(clause)
                hits.append((dict(scale=effect[0], effect=effect[1], ci_low=effect[2], ci_high=effect[3]),
                             sentence[start:match.end()]))
    if len(hits) != 1:
        raise ValueError("ENDPOINT_HR_AMBIGUOUS")
    return hits[0]


def extract_bound(slug, outcome, pid, *, root=ROOT):
    root = Path(root)
    selector = ROUTES[(slug, outcome, str(pid))]
    cfg = json.loads((root / "topics" / (slug + ".json")).read_text(encoding="utf-8"))
    specs = [cfg.get("primary_outcome")] + cfg.get("secondary_outcomes", []) + cfg.get("harm_outcomes", [])
    spec = next(s for s in specs if s and s["name"] == outcome)
    route = selector.get("route", "table")
    report = selector.get("report", pid)
    abstract = selector.get("abstract") or route == "aact_abstract"
    ref = f"cache/{slug}/" + ("records.json" if abstract else selector.get("file", f"ft_{pid}.txt"))
    raw = (root / ref).read_bytes()
    text = raw.decode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    bindings = []
    def bind(role, span, doc=ref, sha=digest):
        bindings.append(dict(role=role, span=span, document_ref=doc, document_sha256=sha))
    if abstract:
        rec = _record(json.loads(text), report)
        text = rec["abstract"]
    else:
        licence, statement = copy_licence.classify_permissions(text)
        if selector.get("file"):
            lp = root / "registry" / "typed_source_licences.json"
            evidence = json.loads(lp.read_text(encoding="utf-8"))[report]
            if evidence["document_sha256"] != digest:
                raise ValueError("LICENCE_COPY_DIGEST_CHANGED")
            licence = evidence["copy_licence"]
        if not copy_licence.typed_may_read(licence):
            raise ValueError("HELD_COPY_NOT_OPEN")
        perm = re.search(r"<permissions>.*?</permissions>", text, re.S)
        if perm:
            bind("licence", perm.group())
    if route == "table":
        # Bind the registered endpoint through the row label or the group heading.
        label = selector.get("group") or selector["row_label"]
        aliases = {"TEAEs": "adverse events", "Any AE": "adverse events",
                   "Total Number of People with AEs": "adverse events"}
        endpoint = aliases.get(label, label)
        if not any(extract._kw_in_sentence(k, endpoint) for k in spec["keywords"]):
            raise ValueError("ENDPOINT_UNBOUND")
        arm = selector["intervention"]
        if not any(t.lower() in arm.lower() for t in cfg["intervention_terms"]):
            # Source-defined abbreviations / class members, never inferred from N.
            patterns = {
                "PRM": r"PRM, prolonged release melatonin",
                "liraglutide": r"liraglutide, a glucagon-like peptide 1 analogue",
                "active": r"The active yogurt also contained.*?BB-12",
            }
            m = re.search(patterns[arm], plain(text), re.I | re.S)
            if not m:
                raise ValueError("INTERVENTION_ALIAS_UNBOUND")
            # Locate a verbatim paragraph containing the source definition.
            paras = re.findall(r"<p\b[^>]*>.*?</p>", text, re.S)
            para = next((p for p in paras if re.search(patterns[arm], plain(p), re.I | re.S)), None)
            if para is None:
                raise ValueError("INTERVENTION_ALIAS_SPAN_UNBOUND")
            bind("arm_definition", para)
        value, spans = read_row(text, **selector)
        for role, span in spans:
            bind(role, span)
        source_span = next(s for role, s in spans if role == "row")
    elif route == "aact_abstract":
        nct = rec.get("nct")
        if not nct or nct not in text:
            raise ValueError("REGISTRY_ID_UNBOUND")
        aref = "outputs/handover/in3/aact/reported_event_totals.txt"
        ab = (root / aref).read_bytes()
        at = ab.decode("utf-8")
        rows = [r for r in csv.DictReader(io.StringIO(at), delimiter="|") if r["nct_id"] == nct and r["event_type"] == "serious"]
        ns = {r["ctgov_group_code"]: int(r["subjects_at_risk"]) for r in rows}
        if len(rows) != 2 or len(ns) != 2 or len(set(ns.values())) != 1:
            raise ValueError("AACT_EQUAL_ARM_DENOMINATORS_UNBOUND")
        n = next(iter(ns.values()))
        candidates = extract._outcome_sentences(text, spec["keywords"])
        hits = [(s, extract.extract_arm_counts(s, cfg["intervention_terms"], cfg["comparator_terms"], denom_each=n)) for s in candidates]
        hits = [(s,v) for s,v in hits if v]
        if len(hits) != 1:
            raise ValueError("COUNT_SENTENCE_UNBOUND")
        source_span, counts = hits[0]
        # Require agreement to the displayed one-decimal percentage, not the broad prose tolerance.
        pcts = [float(m[2]) for m in extract._ARMP.finditer(source_span)]
        if len(pcts) != 2 or any(abs(100*e/n-p) > .051 for e,p in zip((counts[0], counts[2]), pcts)):
            raise ValueError("AACT_PERCENT_DISAGREES")
        value = dict(zip(("ai", "n1i", "ci", "n2i"), counts))
        bind("result", source_span)
        for line in at.splitlines():
            if any(line.startswith(r["id"] + "|") for r in rows):
                bind("subjects_at_risk", line, aref, hashlib.sha256(ab).hexdigest())
    elif route == "sentence_counts":
        paragraphs = re.findall(r"<p\b[^>]*>.*?</p>", text, re.S)
        hits = []
        for p in paragraphs:
            for sentence in extract._sentences(plain(p)):
                if "experienced an AE:" not in sentence:
                    continue
                counts = extract.extract_arm_counts(sentence, cfg["intervention_terms"], cfg["comparator_terms"])
                if counts:
                    hits.append((p, counts))
        if len(hits) != 1:
            raise ValueError("COUNT_SENTENCE_UNBOUND")
        source_span, counts = hits[0]
        value = dict(zip(("ai", "n1i", "ci", "n2i"), counts))
        bind("result", source_span)
    elif route == "refuse_severe":
        if re.search(r"serious adverse", plain(text), re.I):
            raise ValueError("REFUSAL_REQUIRES_REVIEW")
        source_span = next(t for t in re.findall(r"<table-wrap\b.*?</table-wrap>", text, re.S)
                           if "Summary of severe adverse events" in plain(t))
        value = dict(kind="typed_refusal", absent=True, override=True,
                     state="RETRIEVED_REFUSED_WITH_REASON", reason_code="ENDPOINT_UNBOUND",
                     reason="ENDPOINT_UNBOUND: severe != serious; held report does not bind the declared serious adverse events endpoint.",
                     provenance="REFUSED_ON_EVIDENCE")
        bind("endpoint_refusal", source_span)
    else:
        # Plain text companion or a stored abstract: no XML normalization needed.
        value, source_span = sentence_hr(text)
        bind("result", source_span)
    # An effect cell needs its header context downstream as well (scale/model
    # classification reads source). Both pieces remain individually verbatim-bound.
    source = ("\n".join(span for role, span in spans if role in ("header", "row"))
              if route == "table" and selector.get("effect") else source_span)
    result = dict(outcome=outcome, override=True, source=source, source_span=source_span,
                document_ref=ref, document_sha256=digest, source_level=1,
                provenance="typed_held_source", typed_bindings=bindings,
                typed_route={"slug": slug, "outcome": outcome, "pid": str(pid)},
                **({"effect_source_id": f"PMID {report}"} if report != pid else {}))
    result.update(value)
    return result


def for_outcome(slug, outcome, root=ROOT):
    return {pid: extract_bound(s, o, pid, root=root) for s, o, pid in ROUTES if s == slug and o == outcome}


def validate_row(row, outcome=None):
    """Re-extract before admission: a forged provenance token or altered tuple is insufficient."""
    locator = row.get("typed_route") or {}
    if outcome is not None and locator.get("outcome") != outcome:
        return False
    if str(row.get("id", "")).replace("PMID ", "") != locator.get("pid"):
        return False
    try:
        got = extract_bound(**locator)
    except (KeyError, ValueError, OSError):
        return False
    keys = ("ai", "n1i", "ci", "n2i", "effect", "ci_low", "ci_high", "scale",
            "document_ref", "document_sha256", "source", "source_span", "typed_bindings")
    return all(row.get(k) == got.get(k) for k in keys)
