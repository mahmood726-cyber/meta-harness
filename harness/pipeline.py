"""Deterministic offline pipeline: committed cache + topic config -> screen -> extract
(primary + secondary + harms) -> synth -> review core. No network, no hand-typed numbers;
a fresh clone reproduces byte-for-byte.

Auditor defect class recorded verbatim: DIAGNOSTIC–DECISION DECOUPLING — a
validity hazard is correctly detected and represented, but its state is not
causally connected to the analytic decision it should constrain. Plain alias:
disclosure-as-control. Class PROCESS, direction optimistic, severity
major-to-critical.
"""
from __future__ import annotations
import json
import os
import re

from . import extract, screen, scope, verify, locate, unit_of_analysis, funding, estmeasure, design_key
from . import aact_cache
from . import screen_entry
from . import comparator_second_pass
from . import source_hierarchy as source_hierarchy_mod
from . import design_variance
from . import parity_relation
from . import comparator_truth
from . import endpoint_canonical as endpoint_canonical_mod
from . import k2 as k2_mod
from . import identity as identity_mod
from . import membership as membership_mod
from . import grade as grade_mod
from . import rob_sensitivity as rob_sens_mod
from . import claim as claim_mod
from . import claimgraph as claimgraph_mod
from . import invalidation as invalidation_mod
from . import known_missing as known_missing_mod
from . import missing_effect as missing_effect_mod
from . import compat as compat_mod
from . import compat_check as compat_check_mod
from . import compat_direction as compat_direction_mod
from . import recovery_recheck as recovery_recheck_mod
from . import absence as absence_mod
from . import consumer_consistency as consumer_consistency_mod
from . import reason_audit as reason_audit_mod
from . import unextracted as unextracted_mod
from . import harms as harms_mod
from . import protocol_compiler as protocol_compiler_mod
from . import target_endpoint as target_endpoint_mod
from . import second_source as second_source_mod
from . import propositions as propositions_mod
from . import eligibility_chain as eligibility_chain_mod
from . import scope_identity as scope_identity_mod
from .limitations import build_limitations
from .ctgov_results import extract_ctgov
from .synth import Study, pool, method_text, METHOD_RATIO
from .acquisition import LEDGER_FILENAME, STATES

# Back-compat alias: the ratio-scale method is the historical default. Per-outcome and manifest
# method strings are now chosen by synth.method_text(scale) so a mean-difference outcome is never
# labelled with the log-ratio method (fixed cycle 84 after the melatonin cold audit).
METHOD = METHOD_RATIO
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KNOWN_ITEM_RETRIEVAL_LABEL = "KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH"
TITLE_SEEDED_RETRIEVAL_LABEL = "TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH"
HAND_WRITTEN_KEYWORD_SEARCH_LABEL = "HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH"
CONCEPT_SEARCH_LABEL = "CONCEPT SEARCH — registered P/I/C query, full pagination"
RETRIEVAL_UNAUDITABLE_DISTINCTION = "an auditable screening ledger attached to an unauditable retrieval process"
RETRIEVAL_RETRACTION = "We retract any claim of a registry-first or systematic search for this topic."
SEARCH_PROVENANCE_HEADING = "Search provenance — not a completed systematic search."
SEARCH_PROVENANCE_CLASS_STATEMENTS = {
    "KNOWN_ITEM_RETRIEVAL": (
        "its evidence set was assembled by KNOWN-ITEM RETRIEVAL of named publications "
        "(UID/PMID-anchored queries for pre-identified trials)"
    ),
    "TITLE_SEEDED_RETRIEVAL": (
        "its evidence set was assembled by TITLE-SEEDED RETRIEVAL "
        "(title/name-anchored queries for pre-identified trials)"
    ),
    "HAND_WRITTEN_KEYWORD_SEARCH": (
        "its PubMed queries are hand-written keyword strings that were never registered as a concept search"
    ),
}
SEARCH_PROVENANCE_DISCOVERY_STATEMENTS = {
    "KNOWN_ITEM_RETRIEVAL": (
        "which cannot discover an unknown eligible trial. A fetch of named identifiers is not a systematic search."
    ),
    "TITLE_SEEDED_RETRIEVAL": (
        "which cannot discover an unknown eligible trial. A query seeded with the names of known trials "
        "is not a systematic search."
    ),
    "HAND_WRITTEN_KEYWORD_SEARCH": (
        "whose discovery reach is unmeasured — a zero here reads as not observed, never as absent. "
        "A hand-written keyword query is not a documented systematic search."
    ),
}


def _read_text(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n").replace("\r", "\n")


_DOI_RE = re.compile(r"\b10\.\d{4,}/\S+", re.IGNORECASE)
_PMID_LITERAL_RE = re.compile(r"(?<!\d)\d{7,9}(?!\d)(?!\s*\[uid\])", re.IGNORECASE)
_TITLE_FIELD_RE = re.compile(r"\[(?:title|ti)(?:/[^\]]+)?\]", re.IGNORECASE)
_ACRONYM_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9-])([A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*)(?![A-Za-z0-9-])")
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
_JOURNAL_RE = re.compile(
    r"\b(?:JAMA|Lancet|N Engl J Med|NEJM|BMJ|Circulation|Eur J Heart Fail|J Am Coll Cardiol|Ann Intern Med)\b",
    re.IGNORECASE,
)
_NON_TRIAL_ACRONYMS = {
    "AAD",
    "ACS",
    "AF",
    "ARDS",
    "BAY",
    "BIBR",
    "BIO-K",
    "BIBR1048",
    "BMES",
    "BMS-562247",
    "CAP",
    "CKD",
    "CL1285",
    "COPD",
    "COVID",
    "COVID-19",
    "CV",
    "DOAC",
    "DOACS",
    "DPP-4",
    "DPP4",
    "DU-176B",
    "DVT",
    "GG",
    "GLP-1",
    "GLP-1RA",
    "GLP-1 RA",
    "HFPEF",
    "HFREF",
    "IL-6",
    "ICU",
    "JAMA",
    "LCS",
    "LGG",
    "MACE",
    "MADRS",
    "NOAC",
    "NOACS",
    "OR",
    "PCOS",
    "PE",
    "PIC",
    "PLASMA-LYTE",
    "PPH",
    "PUB",
    "RCT",
    "RR",
    "SGLT2",
    "SGLT-2",
    "T2D",
    "T2DM",
    "ABS",
    "TITLE",
    "TITLE_ABS",
    "TYPE",
    "PUB_TYPE",
    "VKA",
    "VTE",
}
_BOOLEAN_TOKENS = {"AND", "OR", "NOT"}


def _trial_acronym_tokens(query: str) -> list[str]:
    tokens = []
    for token in _ACRONYM_TOKEN_RE.findall(query):
        upper = token.upper()
        if upper in _BOOLEAN_TOKENS or upper in _NON_TRIAL_ACRONYMS:
            continue
        if "-" in token or any(ch.isdigit() for ch in token) or (token.isupper() and len(token) >= 4):
            tokens.append(token)
    return tokens


def _journal_year_features(query: str) -> list[str]:
    years = _YEAR_RE.findall(query)
    if not years:
        return []
    journals = [m.group(0) for m in _JOURNAL_RE.finditer(query)]
    return [f"journal_year_seed:{journal}+{year}" for journal in journals for year in years]


def _query_classification(query, exempt_tokens=None):
    """Classify a query string. `exempt_tokens` (lower-cased) are acronym-shaped tokens that come from a topic's
    SEALED registered vocabulary (docs/evidence/search-v2-guard-2026-09-15/PROTOCOL.md; the v2 engine is the
    sole caller); they are reported as vocabulary_token features instead of trial_acronym_token and do not make
    the query NAME_SEEDED. With no context (every caller that renders a served page) the classifier is unchanged."""
    text = str(query or "")
    lower = text.lower()
    features = []
    exempt = {str(t).lower() for t in (exempt_tokens or ())}

    if "[uid]" in lower:
        features.append("uid_field:[uid]")
    for nct in re.findall(r"\bNCT\d{8}\b", text, flags=re.IGNORECASE):
        features.append(f"nct_literal:{nct.upper()}")
    for doi in _DOI_RE.findall(text):
        features.append(f"doi_literal:{doi}")
    for pmid in _PMID_LITERAL_RE.findall(text):
        features.append(f"pmid_literal:{pmid}")
    for tag in _TITLE_FIELD_RE.findall(text):
        features.append(f"title_field_tag:{tag}")
    name_text = _DOI_RE.sub(" ", text)
    for token in _trial_acronym_tokens(name_text):
        if token.lower() in exempt:
            features.append(f"vocabulary_token:{token}")
        else:
            features.append(f"trial_acronym_token:{token}")
    features.extend(_journal_year_features(text))

    if any(f.startswith("uid_field:") for f in features):
        kind = "PMID_ENUMERATION"
    elif any(f.startswith(("doi_literal:", "pmid_literal:", "nct_literal:")) for f in features):
        kind = "IDENTIFIER_SEEDED"
    elif any(f.startswith("title_field_tag:") for f in features):
        kind = "TITLE_ANCHORED"
    elif any(f.startswith(("trial_acronym_token:", "journal_year_seed:")) for f in features):
        kind = "NAME_SEEDED"
    else:
        kind = "FREE_TEXT_KEYWORD"
    return {"kind": kind, "features": features}


def classify_query(query, exempt_tokens=None):
    return _query_classification(query, exempt_tokens)["kind"]


def _retrieval_basis_kind(query):
    return classify_query(query)


def _search_provenance_object(cls, registry_first_status):
    class_statement = SEARCH_PROVENANCE_CLASS_STATEMENTS.get(cls)
    discovery_statement = SEARCH_PROVENANCE_DISCOVERY_STATEMENTS.get(cls)
    if class_statement is None or discovery_statement is None:
        return None
    return {
        "heading": SEARCH_PROVENANCE_HEADING,
        "registry_first_status": registry_first_status,
        "class_statement": class_statement,
        "discovery_statement": discovery_statement,
        "retraction": RETRIEVAL_RETRACTION,
    }


def classify_retrieval(config, ledger=None, registry_first_status=None):
    """Classify retrieval from committed object inputs only.

    Without a retrieval ledger, the replay-safe fact is the committed PubMed query text.
    The classifier uses only structural features visible in that text.
    """
    basis = []
    concept_ran_ok = False
    if ledger:
        for src in ledger.get("sources") or []:
            if src.get("kind") in (
                "PUBMED_CONCEPT_QUERY",
                "EUROPEPMC_CONCEPT_QUERY",
                "CTGOV_CONDITION_INTERVENTION",
            ) and src.get("state") == "RAN_OK":
                kind = "CONCEPT"
                features = [f"concept_source_ran_ok:{src.get('kind')}"]
                concept_ran_ok = True
            else:
                detail = _query_classification(src.get("query"))
                kind = detail["kind"]
                features = detail["features"]
            basis.append({"query": src.get("query"), "kind": kind, "features": features})
    else:
        for query in config.get("pubmed_queries") or []:
            detail = _query_classification(query)
            basis.append({"query": query, "kind": detail["kind"], "features": detail["features"]})

    if concept_ran_ok:
        cls = "CONCEPT_SEARCH"
        label = CONCEPT_SEARCH_LABEL
        retrieval_auditable = True
    elif basis and all(row.get("kind") == "PMID_ENUMERATION" for row in basis):
        cls = "KNOWN_ITEM_RETRIEVAL"
        label = KNOWN_ITEM_RETRIEVAL_LABEL
        retrieval_auditable = False
    elif basis and all(row.get("kind") in ("PMID_ENUMERATION", "FREE_TEXT_KEYWORD") for row in basis):
        cls = "HAND_WRITTEN_KEYWORD_SEARCH"
        label = HAND_WRITTEN_KEYWORD_SEARCH_LABEL
        retrieval_auditable = False
    else:
        cls = "TITLE_SEEDED_RETRIEVAL"
        label = TITLE_SEEDED_RETRIEVAL_LABEL
        retrieval_auditable = False
    out = {
        "class": cls,
        "label": label,
        "basis": basis,
        "screening_auditable": True,
        "retrieval_auditable": retrieval_auditable,
    }
    if not retrieval_auditable:
        out["distinction"] = RETRIEVAL_UNAUDITABLE_DISTINCTION
        out["retraction"] = RETRIEVAL_RETRACTION
        out["search_provenance"] = _search_provenance_object(cls, registry_first_status)
    return out


_NONPRIMARY = ("letter", "comment", "editorial", "erratum", "news", "biography")


def _primacy(r):
    """How primary a PubMed record is as a trial report. A Letter/Comment/Erratum that shares
    a trial's NCT must NOT displace the trial's own RCT report during dedup — that dropped the
    canonical SMART RCT (PMID 29485925) in favour of a Comment (29768150) and lost the trial."""
    pts = [p.lower() for p in r.get("pubtypes", [])]
    if any("randomized controlled trial" in p for p in pts):
        return 3
    if any(x in p for p in pts for x in _NONPRIMARY):
        return 0
    return 2  # an ordinary journal article


def _dedup(records, pivotal=None):
    """Drop the CT.gov twin of a PubMed record (same NCT); then collapse PubMed records that
    share an NCT to the most-primary, latest-year one: a trial's RCT report beats a
    Letter/Comment/Erratum on the same NCT, and among peers the results paper (latest year)
    supersedes an earlier design/rationale paper.

    PIVOTAL PIN: 'latest year' is the WRONG tie-break when a trial's MAIN results paper (earlier)
    shares its NCT with later SUB-ANALYSES (by-subgroup, pooled re-analysis) — it silently drops the
    landmark report for a secondary paper (sacubitril: PARADIGM-HF 25176015 (2014) was dropped for a
    2025 sub-analysis of the same NCT). When the topic preregisters pivotal_trials, a record whose id
    is a declared pivotal wins its NCT outright, so the landmark report always survives dedup."""
    pivotal = {str(p) for p in (pivotal or [])}
    pubmed = list(records.get("records", []))
    by_nct = {}

    def _yr(r):
        try:
            return int(str(r.get("year") or "0")[:4])
        except (TypeError, ValueError):
            return 0

    def _key(r):
        # Highest: a preregistered pivotal wins its NCT outright. Then most-primary (RCT report >
        # ordinary article > letter/comment). Then, among equal-primacy same-NCT records, the MAIN
        # results paper beats a later SUB-ANALYSIS: the pivotal report is published first and the
        # sub-analyses (by-subgroup, substudy, pooled re-analysis) follow, so EARLIEST year wins
        # (via -year). This reverses the old 'latest year' tie-break, which silently dropped a
        # trial's main results paper whenever a later sub-analysis shared its NCT (Alpha Omega,
        # GISSI-HF mains were being discarded for subgroup/arrhythmia substudies). A design/rationale
        # paper is not RCT-pubtype, so _primacy already ranks it below the results report.
        return (1 if str(r.get("id")) in pivotal else 0, _primacy(r), -_yr(r))
    for r in pubmed:
        n = r.get("nct")
        if n:
            keep = by_nct.get(n)
            if keep is None or _key(r) > _key(keep):
                by_nct[n] = r
    deduped = []
    for r in pubmed:
        n = r.get("nct")
        if n and by_nct.get(n) is not r:
            continue  # superseded duplicate of the same NCT
        deduped.append(r)
    seen_nct = {r.get("nct") for r in deduped if r.get("nct")}
    for c in records.get("ctgov", []):
        if c.get("id") not in seen_nct:
            deduped.append(c)
    return deduped


import re as _re
_ENROLL = _re.compile(r"([\d,]{2,})\s+(?:adults?|patients?|participants?|subjects?|women|men)\b", _re.I)


def _enrollment_floor(abstract):
    """~0.6x the trial's abstract-stated enrollment, used to reject a CT.gov SUBGROUP outcome
    measure from being pooled as the whole trial (see extract_ctgov min_total). Returns None
    when no enrollment count is stated (then no floor is applied)."""
    ns = []
    for m in _ENROLL.finditer(abstract or ""):
        try:
            ns.append(int(m.group(1).replace(",", "")))
        except ValueError:
            pass
    return int(0.6 * max(ns)) if ns else None


def _rr_cs(ai, n1, ci, n2):
    if None in (ai, n1, ci, n2) or ai in (0,) or ci in (0,) or not n1 or not n2:
        return None
    return (ai / n1) / (ci / n2)


def _reported_effect_candidate(eff, provenance, source_label):
    return source_hierarchy_mod.reported_effect_candidate(eff, provenance, source_label)


def _source_effect_candidates(spec, *, abstract=None, fulltext=None, ctgov_outcomes=None,
                              verified_effect=None):
    return source_hierarchy_mod.source_effect_candidates(
        spec,
        abstract=abstract,
        fulltext=fulltext,
        ctgov_outcomes=ctgov_outcomes,
        verified_effect=verified_effect,
    )


def _selection_extras(row):
    return source_hierarchy_mod.selection_extras(row)


def _span_effect_candidates(spec, selected, base_candidates):
    return source_hierarchy_mod.span_effect_candidates(spec, selected, base_candidates)


CROSS_SOURCE_LOG_TOL = 0.12

_ENDPOINT_STOPWORDS = {
    "a", "an", "and", "any", "by", "first", "for", "from", "in", "measure", "number",
    "occurrence", "of", "outcome", "participants", "the", "time", "to", "with",
}


def _fmt_effect(x):
    return "NA" if x is None else f"{float(x):.3g}"


def _norm_endpoint_tokens(s):
    toks = re.findall(r"[a-z0-9]+", (s or "").lower())
    out = []
    for t in toks:
        if t in _ENDPOINT_STOPWORDS:
            continue
        if t.endswith("s") and len(t) > 4:
            t = t[:-1]
        out.append(t)
    return set(out)


def _mace_like(s):
    sl = (s or "").lower()
    if any(x in sl for x in ("mace", "major adverse cardiovascular", "major cardiovascular",
                             "serious vascular event")):
        return True
    components = 0
    components += int("cardiovascular death" in sl or "cv death" in sl)
    components += int("myocardial infarction" in sl or re.search(r"\bmi\b", sl) is not None)
    components += int("stroke" in sl)
    return components >= 2


def _endpoint_title_matches(spec, registry_title):
    declared = spec.get("name") or ""
    title = registry_title or ""
    dl, tl = declared.lower(), title.lower()
    if "all-cause" in dl or "all cause" in dl:
        has_all_cause = any(x in tl for x in ("all-cause", "all cause", "all causes", "any cause"))
        adds_nonmortality = any(x in tl for x in ("hospitalization", "hospitalisation", "heart failure"))
        return has_all_cause and not adds_nonmortality
    if "fracture" in dl:
        need = _norm_endpoint_tokens(declared) & {"fracture", "vertebral", "nonvertebral", "hip", "new"}
        return bool(need) and need.issubset(_norm_endpoint_tokens(title))
    if _mace_like(declared):
        return _mace_like(title)
    declared_tokens = _norm_endpoint_tokens(declared)
    title_tokens = _norm_endpoint_tokens(title)
    if declared_tokens and len(declared_tokens & title_tokens) >= max(1, len(declared_tokens) // 2):
        return True
    for kw in spec.get("keywords") or []:
        if len(kw) > 5 and kw.lower() in tl:
            return True
    return False


def _pooled_effect_for_endpoint_match(ex):
    rr = _rr_cs(ex.get("ai"), ex.get("n1i"), ex.get("ci"), ex.get("n2i"))
    if rr:
        return rr, "RR"
    eff = ex.get("effect")
    if eff is not None:
        return eff, ex.get("scale") or "effect"
    return None, None


def _classify_endpoint_match(spec, registry_title, pooled_effect, registry_effect, *,
                             registry_measure_type=None, registry_timepoint=None,
                             registry_population=None, pooled_scale=None,
                             registry_description=None, trial_components=None,
                             pooled_population=None):
    title = registry_title or ""
    if not title:
        return {
            "identity": {
                "title_match": False,
                "component_match": False,
                "measure_type": "unknown",
                "population_match": False,
                "verdict": second_source_mod.SECOND_SOURCE_NOT_CHECKABLE,
            },
            "second_source_verdict": second_source_mod.SECOND_SOURCE_NOT_CHECKABLE,
            "endpoint_match": second_source_mod.SECOND_SOURCE_NOT_CHECKABLE,
            "endpoint_match_reason": "registry outcome title is missing",
            "registry_effect_label": "CT.gov registry value",
        }
    return second_source_mod.classify_identity(
        title_match=_endpoint_title_matches(spec, title),
        spec_name=spec.get("name") or "",
        registry_title=title,
        registry_description=registry_description or "",
        declared_components=trial_components,
        registry_measure_type=registry_measure_type,
        pooled_scale=pooled_scale,
        pooled_effect=pooled_effect,
        registry_effect=registry_effect,
        pooled_population=pooled_population or spec.get("population"),
        registry_population=registry_population,
        registry_timepoint=registry_timepoint,
        log_tolerance=CROSS_SOURCE_LOG_TOL,
    )


def _refresh_cross_source_identity(cross_source, spec, trial_components=None):
    verdict = _classify_endpoint_match(
        spec,
        cross_source.get("registry_title") or "",
        cross_source.get("pooled_effect_for_endpoint_match"),
        cross_source.get("registry_implied_effect") or cross_source.get("ctgov_rr"),
        registry_measure_type=cross_source.get("registry_measure_type"),
        registry_timepoint=cross_source.get("registry_selected_timepoint") or cross_source.get("registry_timeframe"),
        registry_population=cross_source.get("registry_population"),
        pooled_scale=cross_source.get("pooled_scale_for_endpoint_match"),
        registry_description=cross_source.get("registry_description"),
        trial_components=trial_components,
        pooled_population=spec.get("population"),
    )
    cross_source.update(verdict)
    cross_source["corroborates_endpoint"] = second_source_mod.counted_as_corroboration(cross_source)
    if cross_source.get("agree") is False:
        cross_source["note"] = "DISCREPANCY vs CT.gov structured results (direction flip) -- investigate before trusting"
    elif cross_source["corroborates_endpoint"]:
        cross_source["note"] = "independently corroborated by CT.gov structured results; " + cross_source["endpoint_match_reason"]
    else:
        cross_source["note"] = f"{cross_source.get('endpoint_match')}: {cross_source.get('endpoint_match_reason')}"
    return cross_source


def _cross_source(ex, nct, ctgov_results, spec, interv, comp):
    """SECOND INDEPENDENT EXTRACTOR + adjudication. A trial pooled from its abstract is corroborated
    against CT.gov structured results (a different source, extracted independently) when the trial
    has both. Count-vs-count gets an agree verdict within tolerance; a gross DIRECTION FLIP is a
    flagged discrepancy (not auto-refused, because a difference can be a legitimate timepoint/
    definition mismatch — it is surfaced for the reader and for hand-investigation). The cross-source
    number NEVER replaces the pooled number; it only corroborates it."""
    oms = ctgov_results.get(nct)
    if not oms:
        return None
    trial_components = ex.get("components") or ex.get("target_endpoint_components")
    cg = extract_ctgov(oms, spec["keywords"], interv, comp, declared_components=trial_components)
    if not cg:
        return None
    c_rr = cg.get("registry_implied_effect")
    if c_rr is None:
        c_rr = _rr_cs(cg.get("ai"), cg.get("n1i"), cg.get("ci"), cg.get("n2i"))
    a_rr = _rr_cs(ex.get("ai"), ex.get("n1i"), ex.get("ci"), ex.get("n2i"))
    pooled_effect, pooled_scale = _pooled_effect_for_endpoint_match(ex)
    verdict = _classify_endpoint_match(
        spec,
        cg.get("registry_title") or "",
        pooled_effect,
        c_rr,
        registry_measure_type=cg.get("registry_measure_type"),
        registry_timepoint=cg.get("registry_selected_timepoint") or cg.get("registry_timeframe"),
        registry_population=cg.get("registry_population"),
        pooled_scale=pooled_scale,
        registry_description=cg.get("registry_description"),
        trial_components=trial_components,
    )
    out = {"ctgov_rr": round(c_rr, 3) if c_rr else None,
           "ctgov_source": cg.get("source", ""),
           "registry_title": cg.get("registry_title"),
           "registry_description": cg.get("registry_description"),
           "registry_type": cg.get("registry_type"),
           "registry_param_type": cg.get("registry_param_type"),
           "registry_measure_type": cg.get("registry_measure_type"),
           "registry_timeframe": cg.get("registry_timeframe"),
           "registry_selected_timepoint": cg.get("registry_selected_timepoint"),
           "registry_population": cg.get("registry_population"),
           "registry_implied_effect": round(c_rr, 6) if c_rr else None,
           "pooled_effect_for_endpoint_match": round(pooled_effect, 6) if pooled_effect else None,
           "pooled_scale_for_endpoint_match": pooled_scale,
           "endpoint_match_tolerance_log": CROSS_SOURCE_LOG_TOL,
           "registry_intervention_value": cg.get("registry_intervention_value"),
           "registry_comparator_value": cg.get("registry_comparator_value"),
           **verdict}
    if a_rr and c_rr:
        import math
        ratio = a_rr / c_rr
        flip = (a_rr - 1) * (c_rr - 1) < 0 and abs(math.log(ratio)) > 0.2
        gross = ratio > 1.5 or ratio < (1 / 1.5)
        out["abstract_rr"] = round(a_rr, 3)
        out["agree"] = not (flip and gross)
    else:
        out["agree"] = None
    return _refresh_cross_source_identity(out, spec, trial_components)


def _pool_result(studies, scale="RR", *, require_study_effect=False):
    r = pool(studies, scale=scale, require_study_effect=require_study_effect)
    i2 = k2_mod.i2_from_q(r.Q, r.k)
    def _rf(value, digits):
        return round(float(value), digits)
    res = {"k": r.k, "estimate": _rf(r.estimate, 4), "scale": r.scale,
           "ci_low": _rf(r.ci_low, 4), "ci_high": _rf(r.ci_high, 4), "tau2": _rf(r.tau2, 5),
           "Q": _rf(r.Q, 5), **({"i2": _rf(i2, 1)} if i2 is not None else {}),
           "ci_provenance": r.ci_provenance}  # engine token; the interval-provenance gate checks it
    if r.k == 1:
        # External audit: at k=1 there is nothing to pool — print the single trial's SOURCE CI
        # VERBATIM rather than back-computing the SE and regenerating the CI (SELECT's published
        # 0.72-0.90 was being reprinted as 0.7155-0.8944). Only for a reported effect+CI trial; a
        # 2x2-derived CI has no source interval to quote and its computed CI stands.
        s0 = studies[0]
        if getattr(s0, "ci_low", None) is not None and getattr(s0, "ci_high", None) is not None:
            res["ci_low"], res["ci_high"] = s0.ci_low, s0.ci_high
            if getattr(s0, "effect", None) is not None:
                res["estimate"] = s0.effect
            res["ci_note"] = "k=1: point estimate and 95% CI are the single trial's reported values, verbatim."
            res["ci_provenance"] = "source-reported-CI:k=1-verbatim"  # not engine-pooled; the trial's own CI
        res["pi_note"] = "prediction interval undefined for k=1"
    elif r.k == 2:
        # External audit: at k=2 the prediction interval needs a t-quantile on 1 degree of freedom and
        # is not reliable; suppress it rather than print a CI-coincident interval (Cochrane guidance).
        res["pi_note"] = ("prediction interval not estimated (k=2): it requires a t-quantile on a single "
                          "degree of freedom and is not reliable at k=2 (Cochrane) — see the common-effect "
                          "sensitivity CI instead.")
    else:
        res["pi_low"], res["pi_high"] = _rf(r.pi_low, 4), _rf(r.pi_high, 4)
        if r.tau2 == 0:
            res["pi_note"] = ("tau^2 estimated as 0, so the prediction interval coincides with the "
                              "confidence interval (no between-study heterogeneity detected).")
    # At k==2 the HKSJ t-multiplier (t_{1}=12.71, 1 df) makes the primary CI very wide and can read as
    # "compatible with no effect" even when both trials agree (I^2=0); an external audit asked for the
    # conventional common-effect CI alongside. (k==1 is already z-based, so its fixed CI equals the
    # primary and adds nothing.)
    if r.k == 2 and r.ci_low_fixed is not None:
        res["ci_low_fixed"] = _rf(r.ci_low_fixed, 4)
        res["ci_high_fixed"] = _rf(r.ci_high_fixed, 4)
        res["estimate_fixed"] = _rf(r.estimate_fixed, 4)
        res["fixed_note"] = ("common-effect sensitivity (z-based; not the registered interval): with only "
                             "two trials the registered HKSJ interval uses a t-multiplier on a single "
                             "degree of freedom; the z-based common-effect interval is labelled separately.")
    return res


def _invalidation_signals(slug):
    """Committed, deterministic per-topic signals for the invalidation gate that do not live in the
    core: (a) search-not-executed from docs/search_provenance.json (RAN_ERROR-rendered-as-run OR
    explicit PMID-enumeration -> no genuine concept search); (b) known-eligible-missing from
    docs/known_eligible_missing.json (audit-identified eligible trials not pooled). Read from
    committed docs so build and replay produce the same verdict."""
    out = {}
    try:
        sp = json.load(open(os.path.join(ROOT, "docs", "search_provenance.json"), encoding="utf-8"))
        for cls in ("RAN_ERROR_rendered_as_run", "PMID_ENUMERATION_explicit"):
            block = (sp.get("classes") or {}).get(cls) or {}
            if slug in (block.get("topics") or []):
                out["search_not_executed"] = {"class": cls, "detail": block.get("note", "")}
                break
    except (OSError, ValueError):
        pass
    try:
        kem = json.load(open(os.path.join(ROOT, "docs", "known_eligible_missing.json"), encoding="utf-8"))
        rows = (kem.get("topics") or {}).get(slug)
        if rows:
            rows = missing_effect_mod.enrich_from_cache(ROOT, slug, rows)
            out["known_eligible_missing"] = rows
    except (OSError, ValueError):
        pass
    try:
        nc = json.load(open(os.path.join(ROOT, "docs", "never_considered.json"), encoding="utf-8"))
        rows = (nc.get("topics") or {}).get(slug)
        if rows:
            out["never_considered"] = rows
    except (OSError, ValueError):
        pass
    return out


def _load_ghost(slug):
    """Committed ghost-protocol / registry-landscape census (cache/<slug>/ghost.json) from AACT."""
    p = os.path.join(ROOT, "cache", slug, "ghost.json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_integrity(slug):
    """Committed trial-integrity (retraction / expression-of-concern) snapshot for this topic's
    pooled trials (cache/<slug>/integrity.json), produced by scripts/integrity_check.py. Rendered on
    the page and enforced by the gate. Absent => not yet checked."""
    p = os.path.join(ROOT, "cache", slug, "integrity.json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_recall(slug):
    """Committed registry-first RECALL snapshot for this topic (cache/<slug>/recall.json), if
    measured. Recall is network-derived (registry enumeration), so — like the cache and the
    outcome-identity judgments — it is a COMMITTED INPUT the page renders, regenerable by re-running
    scripts/recall.py against the committed registry_first query. Absent => not yet measured."""
    p = os.path.join(ROOT, "cache", slug, "recall.json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_outcome_judgments(slug):
    """Committed outcome-identity judgments (the model-as-source cache). Present only for topics
    that opted into the gate and had judgments produced by scripts/outcome_judgments.py. Absent =>
    None => extract_ctgov keeps its deterministic substring selection (backward-compatible)."""
    p = os.path.join(ROOT, "cache", slug, "outcome_judgments.json")
    if not os.path.exists(p):
        return None
    data = json.load(open(p, encoding="utf-8"))
    # stored as {"judgments": {title: {...}}, "model": ..., "produced_utc": ...}
    return data.get("judgments", data)


def _load_rob2(slug):
    """Committed per-trial partial machine assessment from AACT + registry-vs-pooled."""
    import os, json
    fp = os.path.join(ROOT, "cache", slug, "rob2.json")
    if not os.path.exists(fp):
        return None
    try:
        return json.load(open(fp, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_arm_contrast(slug):
    """Committed per-pooled-trial ARM-CONTRAST disclosure (cache/<slug>/arm_contrast.json): whether the
    intervention of interest is a genuine RANDOMISED CONTRAST (differs across arms) or fail-open/background.
    Makes the arm-data-unavailable state VISIBLE rather than a silent verified-looking inclusion."""
    import os, json
    fp = os.path.join(ROOT, "cache", slug, "arm_contrast.json")
    if not os.path.exists(fp):
        return None
    try:
        return json.load(open(fp, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_rob_spancheck():
    """Corpus-level RoB span-check summary (docs/rob_spancheck.json): the cross-family agreement rate of the
    model/registry-derived partial machine ratings vs the trial abstracts. Same number on every RoB tab (it is a corpus
    measurement); rendered so the RoB block carries a credibility number after a visible rendering break."""
    import os, json
    fp = os.path.join(ROOT, "docs", "rob_spancheck.json")
    if not os.path.exists(fp):
        return None
    try:
        return json.load(open(fp, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _load_definition_audit(slug):
    """The topic's rows from the committed cross-family definition audit (docs/definition_audit.json):
    outcome-definition-identity findings (composite component set / timepoint / population / analysis set),
    each with its adjudication + resolution. Rendered on the page so a recorded mismatch is VISIBLE (the
    container/contents rule); reproduces from committed data."""
    import os, json
    fp = os.path.join(ROOT, "docs", "definition_audit.json")
    if not os.path.exists(fp):
        return None
    try:
        d = json.load(open(fp, encoding="utf-8"))
    except (OSError, ValueError):
        return None
    rows = {rid: v for rid, v in (d.get("by_row") or {}).items() if rid.startswith(slug + "::")}
    return rows or None


def _verified_for_outcome(data, outcome):
    from .verified_inputs import for_outcome
    return for_outcome(data, outcome)


def _load_verified_arms(slug):
    from .verified_inputs import load
    return load(slug, cache_root=os.path.join(ROOT, "cache"))["verified_arms.json"] or None


def _load_verified_effects(slug):
    from .verified_inputs import load
    return load(slug, cache_root=os.path.join(ROOT, "cache"))["verified_effects.json"] or None


def _load_dose_selection(slug):
    """Committed pre-specified approved-dose entries (cache/<slug>/dose_selection.json):
    {pmid: {outcome, dose, effect, ci_low, ci_high, scale, source}}. For a multi-dose trial where the
    review pools a DECLARED dose (the approved dose) rather than whatever the abstract mentions first —
    RE-LY dabigatran 150 mg, ENGAGE-AF edoxaban 60 mg. A documented rule (not arbitrary selection),
    verified against `source`; sits at the top of the source hierarchy for the named trial only."""
    p = os.path.join(ROOT, "cache", slug, "dose_selection.json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _clean_record_id(value):
    s = str(value or "").strip()
    for sep in ("Â·", "·", "ï¿½", "�"):
        if sep in s:
            s = s.split(sep)[-1].strip()
    return s.replace("PMID ", "").replace("PMID:", "").strip()


_ONGOING_STATUS = {"RECRUITING", "ACTIVE_NOT_RECRUITING", "ENROLLING_BY_INVITATION", "APPROVED_FOR_MARKETING"}
_NOT_YET_STATUS = {"NOT_YET_RECRUITING"}
_COMPLETED_STATUS = {"COMPLETED", "TERMINATED", "WITHDRAWN", "SUSPENDED", "UNKNOWN"}


def _completeness_for_record(rec, dates):
    rid = str((rec or {}).get("id") or "")
    nct = screen._nct_id(rec or {})
    d = dates.get(nct or "") if nct else {}
    status = str((d or {}).get("overall_status") or (rec or {}).get("overall_status") or (rec or {}).get("status") or "").upper()
    has_results = bool((rec or {}).get("has_results") or (d or {}).get("results_first_posted_date"))
    if status in _NOT_YET_STATUS:
        state = "eligible+not_yet_recruiting"
    elif status in _ONGOING_STATUS:
        state = "eligible+ongoing"
    elif (rec or {}).get("id_type") == "pmid" or status in _COMPLETED_STATUS or has_results:
        state = "eligible+completed+results_available" if (has_results or (rec or {}).get("id_type") == "pmid") else "eligible+completed+results_unavailable"
    else:
        state = "eligible+completed+results_unavailable"
    return {
        "completeness_state": state,
        "registry_status": status or None,
        "results_first_posted_date": (d or {}).get("results_first_posted_date") or None,
        "completion_date": (d or {}).get("completion_date") or None,
        "completeness_basis": "CT.gov status/results dates from local AACT snapshot" if nct and d else "publication record / committed cache metadata",
    }


def _annotate_completeness(review, rec_by_id):
    ncts = [screen._nct_id(r) for r in rec_by_id.values()]
    dates = aact_cache.values("study_dates") if any(ncts) else {}

    def annotate(item):
        rec = rec_by_id.get(_clean_record_id(item.get("id")))
        if not rec:
            return
        ann = _completeness_for_record(rec, dates)
        for k, v in ann.items():
            if v not in (None, "", []):
                item.setdefault(k, v)

    for row in (review.get("screening") or {}).get("records") or []:
        if row.get("decision") == "include":
            annotate(row)
    for outcome in review.get("outcomes") or []:
        for row in outcome.get("declared_absent_trials") or []:
            annotate(row)


def _load_retrieval_ledger(slug):
    p = os.path.join(ROOT, "cache", slug, LEDGER_FILENAME)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _with_model_adjudication(slug, dual, decisions):
    """Attach the committed independent-model adjudication of the rule-screener disagreements
    (cache/<slug>/screen_adjudication.json) to the dual block, with the model-vs-served agreement.
    ADVISORY only — the served decision is the rule screener's; this is the genuinely-independent
    third reader (different information + method) that earns the PRISMA item-8 independence claim."""
    p = os.path.join(ROOT, "cache", slug, "screen_adjudication.json")
    if not os.path.exists(p):
        return dual
    try:
        j = json.load(open(p, encoding="utf-8")).get("judgments", {})
    except (OSError, ValueError):
        return dual
    served = {str(d["id"]): d["decision"] for d in decisions}
    n = agree = 0
    flags = []
    for pid, jr in j.items():
        if pid not in served:
            continue
        n += 1
        model_inc = jr.get("is_eligible") is True
        if model_inc == (served[pid] == "include"):
            agree += 1
        else:
            flags.append({"id": pid, "served": served[pid],
                          "model": "include" if model_inc else "exclude", "rationale": jr.get("rationale")})
    dual["model_adjudication"] = {
        "n": n, "agree_with_served": agree, "flags": flags,
        "note": "an independent capable-model reader adjudicated the rule-screener disagreements "
                "(different information + method than the two correlated rule sets). Advisory: the rule "
                "screener remains the served decision; flags are surfaced for review."}
    return dual


def _apply_adjudicator_flags(slug, screening_records):
    p = os.path.join(ROOT, "cache", slug, "screen_adjudication.json")
    if not os.path.exists(p):
        return {"records": screening_records, "pending": []}
    try:
        judgments = json.load(open(p, encoding="utf-8")).get("judgments", {})
    except (OSError, ValueError):
        return {"records": screening_records, "pending": []}
    pending = []
    for row in screening_records:
        rid = _clean_record_id(row.get("id"))
        jr = judgments.get(rid)
        if not isinstance(jr, dict) or not isinstance(jr.get("is_eligible"), bool):
            continue
        served_include = row.get("decision") == "include"
        model_include = jr.get("is_eligible") is True
        if served_include == model_include:
            continue
        row["adjudicator_state"] = "ADJUDICATOR_DISAGREES"
        row["adjudicator_recommended_decision"] = "include" if model_include else "exclude"
        row["adjudicator_rationale"] = jr.get("rationale")
        pending.append({
            "id": rid,
            "served": row.get("decision"),
            "adjudicator": row["adjudicator_recommended_decision"],
            "rationale": jr.get("rationale"),
        })
    return {"records": screening_records, "pending": pending}


def _apply_trial_annotations(spec, trials):
    """Copy source-backed per-trial compatibility annotations from the topic spec onto pooled rows."""
    anns = spec.get("trial_annotations") or {}
    if not anns:
        return
    allowed = {
        "prior_disease_stage",
        "background_therapy",
        "components",
        "endpoint_definition",
        "follow_up_window",
        "analysis_set",
        "effect_model_class",
        "source_label",
        "background_lifestyle_intensity",
        "endpoint_event_time",
        "analysis_set_literal",
        "treatment_strategy",
        "clomifene_status",
        "dose_regimen",
        "run_in_enrichment",
        "evidence_unit",
        "evidence_unit_detail",
    }
    for t in trials:
        pid = str(t.get("id", "")).replace("PMID ", "").strip()
        ann = anns.get(pid) or anns.get(str(t.get("label") or "")) or anns.get(str(t.get("id") or ""))
        if not isinstance(ann, dict):
            continue
        for k in allowed:
            if k in ann:
                if k == "components" and t.get("components"):
                    continue
                t[k] = ann[k]


def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=None,
                   fulltext_by_pmid=None, outcome_judgments=None, verified_arms=None,
                   locate_judgments=None, verified_effects=None, dose_selection=None,
                   registry_designs=None, k2_anchor_config=None, eligibility_contract=None):
    ctgov_results = ctgov_results or {}
    fulltext_by_pmid = fulltext_by_pmid or {}
    dose_selection = dose_selection or {}
    verified_arms = _verified_for_outcome(verified_arms, spec.get("name"))
    verified_effects = _verified_for_outcome(verified_effects, spec.get("name"))
    trials, absent = [], []
    candidate_index = {}
    all_effect_candidates = []
    for d in included:
        rec = rec_by_id.get(d["id"], {})
        nct = rec.get("nct") or (d["id"] if d["id_type"] == "nct" else None)
        ft = fulltext_by_pmid.get(d["id"]) if d["id_type"] == "pmid" else None
        ve = (verified_effects or {}).get(d["id"])
        cands = _source_effect_candidates(
            spec,
            abstract=rec.get("abstract", ""),
            fulltext=ft,
            ctgov_outcomes=ctgov_results.get(nct) if nct else None,
            verified_effect=ve,
        )
        candidate_index[d["id"]] = cands
        all_effect_candidates.extend(cands)
    estimand_decision = source_hierarchy_mod.estimand_decision(spec, all_effect_candidates)
    selector_estimand = estimand_decision.get("target_scale") or spec.get("estimand") or "RR"
    for d in included:
        rec = rec_by_id.get(d["id"], {})
        label = rec.get("acronym") or d.get("label") or d["id"]
        idstr = f"PMID {d['id']}" if d["id_type"] == "pmid" else d["id"]
        # PRE-SPECIFIED DOSE (documented rule, TOP of the hierarchy): a multi-dose trial's abstract
        # headline may report a dose other than the one this review pools by a declared rule (the
        # APPROVED dose). Where a committed dose_selection entry names the dose + a verified effect+CI
        # for THIS outcome, it is used and the arbitrary abstract-dose extraction is overridden. This
        # is the RE-LY-150mg / ENGAGE-60mg resolution: a documented approved-dose rule, not arbitrary
        # selection (which the multi-arm guard still refuses). Verified against its own source span.
        ds = dose_selection.get(d["id"])
        if ds and ds.get("outcome") == spec.get("name") and ds.get("effect") is not None:
            trials.append({"label": label, "id": idstr, "effect": ds["effect"],
                           "ci_low": ds.get("ci_low"), "ci_high": ds.get("ci_high"),
                           "scale": ds.get("scale", "HR"), "provenance": "pre_specified_dose",
                           "dose": ds.get("dose"),
                           "source": ds.get("source", "pre-specified approved-dose arm (documented rule)")})
            continue
        # HAND-VERIFIED ENDPOINT-CORRECTION OVERRIDE (opt-in, TOP of the hierarchy alongside dose): a
        # committed verified_effects entry flagged `override: true` beats the abstract for THIS trial+outcome.
        # Used ONLY when the abstract extractor selects the WRONG ENDPOINT (a number that is source-backed
        # but for a different outcome than ours) and the correct value is hand-verifiable in the same source.
        # ORIGIN (PMID 22686415): the abstract's "primary outcome" is death from cardiovascular causes
        # (HR 0.98); our outcome is major vascular events, which the SAME abstract reports as HR 1.01. Scoped
        # by the flag so ordinary (unflagged) verified_effects stay a pure fallback — no other page moves.
        # ABSENT OVERRIDE (opt-in, top of the hierarchy): a committed verified_effects/verified_arms entry
        # flagged `override: true, absent: true` for THIS outcome forces the trial declared-absent. Used
        # when the abstract extractor grabbed a source-backed but WRONG-ENDPOINT number and the correct
        # value is NOT in the committed source (so no override number exists) — refuse rather than pool the
        # wrong endpoint. STEP-12 (42575111): the abstract's "141 of 161" is OVERALL adverse events, not the
        # gastrointestinal-specific count our harm outcome names (the abstract gives no GI-specific count).
        _abs_over = next((entry for entry in (
            (verified_effects or {}).get(d["id"]), (verified_arms or {}).get(d["id"]))
            if entry and entry.get("override") and entry.get("absent")), None)
        if (_abs_over and _abs_over.get("override") and _abs_over.get("absent")
                and _abs_over.get("outcome") == spec.get("name")):
            absent.append({"label": label, "id": idstr, "absent_kind": "adjudicated_absent",
                           "state": _abs_over.get("state"),  # override may pin the ontology state; else defaulted below
                           "reason_code": (_abs_over.get("reason_code") or _abs_over.get("state")
                                           or _abs_over.get("provenance")),
                           "source_adjudicated": bool(_abs_over.get("source_span")),
                           "document_sha256": _abs_over.get("document_sha256"),
                           "typed_refusal": bool(_abs_over.get("source_span") and _abs_over.get("provenance")),
                           "refusal_provenance": _abs_over.get("provenance"),
                           "source_span": _abs_over.get("source_span") or "",
                           "verbatim_span": _abs_over.get("source_span") or "",
                           "source": _abs_over.get("source", ""),
                           "document_ref": _abs_over.get("document_ref"),
                           "source_level": _abs_over.get("source_level"),
                           **({"published_alternative": _abs_over.get("published_alternative")}
                              if _abs_over.get("published_alternative") else {}),
                           "reason": _abs_over.get("reason", "declared absent (override): the committed source "
                                     "reports no value for this outcome; the extracted number was a different endpoint")})
            continue
        va_over = (verified_arms or {}).get(d["id"])
        if (va_over and va_over.get("override") and va_over.get("outcome") == spec.get("name")
                and all(va_over.get(k) is not None for k in ("ai", "n1i", "ci", "n2i"))):
            trials.append({"label": label, "id": idstr, "ai": va_over["ai"], "n1i": va_over["n1i"],
                           "ci": va_over["ci"], "n2i": va_over["n2i"], "provenance": va_over.get("provenance", "aact_verified"),
                           **{k: va_over[k] for k in ("document_ref", "document_sha256", "source_level") if k in va_over},
                           "source": va_over.get("source", "hand-verified arm-count correction (override)")})
            continue
        # CONTINUOUS override (mean/SD/n), incl. multi-arm combination: beats the automated CT.gov path,
        # which for a 3-arm trial takes a single arm pair and cannot combine dose arms against the shared
        # placebo (esketamine TRANSFORM-1). Highest-precedence continuous entry for this trial+outcome.
        if (va_over and va_over.get("override") and va_over.get("outcome") == spec.get("name")
                and all(va_over.get(k) is not None for k in ("mean1", "sd1", "nc1", "mean2", "sd2", "nc2"))):
            trials.append({"label": label, "id": idstr,
                           "mean1": va_over["mean1"], "sd1": va_over["sd1"], "nc1": va_over["nc1"],
                           "mean2": va_over["mean2"], "sd2": va_over["sd2"], "nc2": va_over["nc2"],
                           "scale": "MD", "provenance": va_over.get("provenance", "fulltext_verified_arms"),
                           "source": va_over.get("source", "hand-verified continuous per-arm mean/SD/n (override)")})
            continue
        ve_over = (verified_effects or {}).get(d["id"])
        if (ve_over and ve_over.get("override") and ve_over.get("outcome") == spec.get("name")
                and ve_over.get("effect") is not None):
            trials.append({"label": label, "id": idstr, "effect": ve_over["effect"],
                           "ci_low": ve_over.get("ci_low"), "ci_high": ve_over.get("ci_high"),
                           "scale": ve_over.get("scale", "HR"),
                           "provenance": ve_over.get("provenance", "fulltext_verified"),
                           **({"alternative_co_primary": ve_over.get("alternative_co_primary")}
                              if ve_over.get("alternative_co_primary") else {}),
                           "source": ve_over.get("source", "hand-verified endpoint correction (override)")})
            continue
        nct = rec.get("nct") or (d["id"] if d["id_type"] == "nct" else None)
        target_pick = target_endpoint_mod.select_target_endpoint(
            spec,
            rec.get("abstract", ""),
            ctgov_results.get(nct) if nct else None,
            interv,
            comp,
        )
        if target_pick.get("selected"):
            t = {"label": label, "id": idstr, **target_pick["selected"]}
            if nct and nct in ctgov_results:
                cs = _cross_source(t, nct, ctgov_results, spec, interv, comp)
                if cs and (t.get("provenance") != "ctgov_results"
                           or cs.get("registry_title") != t.get("registry_title")
                           or not cs.get("corroborates_endpoint")):
                    t["cross_source"] = cs
            trials.append(t)
            continue
        # WRONG-ENDPOINT REFUSAL (external review of served glp1 edaf5f6b, defect 1): the selector found a
        # number in the held source but its bound endpoint span is NOT the declared outcome (a component
        # alone, a different composite, or a span it could not bind). That is a typed refusal for THIS
        # trial, rendered with the refused number and both spans. It must NOT fall through to the legacy
        # abstract/registry/full-text routes below, which would pool the same number with no class.
        if target_pick.get("refusal"):
            rf = target_pick["refusal"]
            absent.append({"label": label, "id": idstr, "absent_kind": "refused_on_evidence",
                           "state": "REFUSED_ON_EVIDENCE", "reason_code": rf.get("reason_code"),
                           "endpoint_admissibility": rf.get("reason_code"),
                           "endpoint_binding": rf.get("endpoint_binding"),
                           "endpoint_result_span": rf.get("endpoint_result_span"),
                           "endpoint_definition_span": rf.get("endpoint_definition_span"),
                           "target_endpoint_class": rf.get("target_endpoint_class"),
                           "refused_effect": rf.get("refused_effect"),
                           "source": rf.get("source") or "", "provenance": "abstract",
                           "reason": rf.get("reason") or "endpoint not admissible"})
            continue
        # SOURCE HIERARCHY: the ABSTRACT headline (the authors' primary-outcome result, unambiguous)
        # first; CT.gov structured results as the FALLBACK when the abstract yields no extractable
        # number (bare %, composite-only). CT.gov-first was tried and REJECTED: outcome-measure
        # selection is ambiguous (abbreviated OM titles) and it overrode EMPEROR's correct 361-event
        # composite with a 15-event secondary. Both are primary-source; the abstract headline is safer.
        dc = extract.declared_is_composite(spec.get("name", ""))
        ft = fulltext_by_pmid.get(d["id"]) if d["id_type"] == "pmid" else None
        ve = (verified_effects or {}).get(d["id"])
        effect_candidates = candidate_index.get(d["id"], [])
        ex = extract.extract_trial(rec.get("abstract", ""), spec["keywords"], interv, comp,
                                   declared_composite=dc, estimand=spec.get("estimand"))
        if not ex.get("absent"):
            # ESTIMAND-HOMOGENEITY (composite component count): an N-point MACE outcome must not pool a
            # trial whose own composite has a different component set (e.g. TECOS's 4-point vs 3-point).
            _mm = (extract.composite_component_mismatch(spec.get("name", ""), ex.get("source", ""))
                   or extract.population_mismatch(ex.get("source", ""))
                   or extract.timepoint_mismatch(spec.get("timepoint", ""), ex.get("source", "")))
            if _mm:
                absent.append({"label": label, "id": idstr, "absent_kind": "refused_on_evidence", "reason": _mm})
                continue
            ex["provenance"] = "abstract"
            t = {"label": label, "id": idstr, **ex}
            t = design_key.select_estimator_by_source_hierarchy(
                t, _span_effect_candidates(spec, t, effect_candidates), selector_estimand
            )
            if nct and nct in ctgov_results:
                cs = _cross_source(t, nct, ctgov_results, spec, interv, comp)
                if cs:
                    t["cross_source"] = cs
            trials.append(t)
            continue
        cg = (extract_ctgov(ctgov_results.get(nct), spec["keywords"], interv, comp,
                            min_total=_enrollment_floor(rec.get("abstract", "")),
                            judgments=outcome_judgments)
              if nct and nct in ctgov_results else None)
        if cg:
            cg["provenance"] = "ctgov_results"
            t = {"label": label, "id": idstr, **cg}
            t = design_key.select_estimator_by_source_hierarchy(
                t, _span_effect_candidates(spec, t, effect_candidates), selector_estimand
            )
            trials.append(t)
            continue
        # FULL-TEXT FALLBACK: per-arm SD / person-time / rate-ratio+CI that the abstract omits
        # often live in the PMC OA full text (Albert's azithromycin IRR 0.73). Same extractors,
        # same round-trip + refuse-on-ambiguity guards; keyword-scoped so it reads the outcome's
        # own sentences, not the whole document.
        fx = extract.extract_trial(ft, spec["keywords"], interv, comp, declared_composite=dc,
                                   estimand=spec.get("estimand")) if ft else None
        if fx and not fx.get("absent"):
            fx["provenance"] = "pmc_fulltext"
            t = {"label": label, "id": idstr, **fx}
            t = design_key.select_estimator_by_source_hierarchy(
                t, _span_effect_candidates(spec, t, effect_candidates), selector_estimand
            )
            trials.append(t)
            continue
        # BOTTOM OF THE SOURCE HIERARCHY: a committed, HAND-VERIFIED structured arm-level entry
        # (e.g. AACT counts summed across a trial's two registrations, verified against the
        # published rate). Used only when the primary report / single-NCT registry / full text do
        # NOT yield the number, and only for the matching outcome. Carries its own provenance +
        # verification, rendered on the page so a reader sees which numbers we took from where.
        va = (verified_arms or {}).get(d["id"])
        if va and va.get("outcome") == spec.get("name") and all(
                va.get(k) is not None for k in ("ai", "n1i", "ci", "n2i")):
            t = {"label": label, "id": idstr, "ai": va["ai"], "n1i": va["n1i"],
                 "ci": va["ci"], "n2i": va["n2i"],
                 "provenance": va.get("provenance", "aact_verified"),
                 "source": va.get("source", "hand-verified structured arm-level counts"),
                 **_selection_extras(va)}
            t = design_key.select_estimator_by_source_hierarchy(
                t, _span_effect_candidates(spec, t, effect_candidates), selector_estimand
            )
            trials.append(t)
            continue
        # CONTINUOUS hand-verified arms (mean/SD/n), incl. MULTI-ARM COMBINATION: a multi-arm trial
        # whose dose arms are combined against the shared placebo (the unit-of-analysis rule) is
        # extracted here, since the automated CT.gov path takes one arm pair only. esketamine TRANSFORM-1
        # combines the 56 mg + 84 mg intranasal arms vs the shared placebo. verify_pooled checks the
        # mean/SD digits against the committed source span (provenance is not abstract/pmc_fulltext).
        if va and va.get("outcome") == spec.get("name") and all(
                va.get(k) is not None for k in ("mean1", "sd1", "nc1", "mean2", "sd2", "nc2")):
            t = {"label": label, "id": idstr,
                 "mean1": va["mean1"], "sd1": va["sd1"], "nc1": va["nc1"],
                 "mean2": va["mean2"], "sd2": va["sd2"], "nc2": va["nc2"],
                 "scale": "MD", "provenance": va.get("provenance", "fulltext_verified_arms"),
                 "source": va.get("source", "hand-verified continuous per-arm mean/SD/n"),
                 **_selection_extras(va)}
            t = design_key.select_estimator_by_source_hierarchy(
                t, _span_effect_candidates(spec, t, effect_candidates), selector_estimand
            )
            trials.append(t)
            continue
        # FULL-TEXT-VERIFIED EFFECT (committed): the declared-outcome effect+CI is reported only in
        # the full text and cannot be reduced to unambiguous per-arm counts. provenance is NOT
        # abstract/pmc_fulltext so verify.verify_pooled checks the effect's digits against the
        # committed source span (not the abstract). Only for the matching outcome.
        if ve and ve.get("outcome") == spec.get("name") and ve.get("effect") is not None:
            row = {"label": label, "id": idstr, "effect": ve["effect"],
                   "ci_low": ve.get("ci_low"), "ci_high": ve.get("ci_high"),
                   "scale": ve.get("scale", "HR"), "provenance": "fulltext_verified",
                   "source": ve.get("source", "full-text-verified effect+CI")}
            # A hand-verified row is not outside the endpoint-binding safeguard: its own numbers locate its
            # result sentence in the held abstract, which binds to a definition span and is classified like
            # every other route; and its provenance says where the passage IS (SOUL was pooled as
            # UNBOUND_LEGACY, provenance "fulltext_verified", with an abstract passage -- Mahmood's review of
            # 98726cc1, item 2). A row whose numbers are not in the abstract keeps the full-text label and the
            # unbound_legacy state until the FACT landing binds it to a held document.
            bound = target_endpoint_mod.bind_verified_row(spec, rec.get("abstract", ""), row)
            if bound.get("passage_location") == "abstract":
                row["provenance"] = "abstract_verified"
                row.update({k: v for k, v in bound.items() if k != "passage_location"})
            row["verified_passage_location"] = bound.get("passage_location")
            trials.append(row)
            continue
        absent.append({"label": label, "id": idstr, "absent_kind": "machine_absent", "reason": ex["reason"]})
    # MANDATORY ADMISSIBILITY (every route converges here): a row is pooled only if its bound endpoint
    # is the declared outcome. Exact targets pass; a near match passes only under the outcome's explicit
    # `allow_near_match` declaration with nothing missing; unbound/different/component-only rows are
    # refused with the number they carried and both spans, so a reader sees what was refused and why.
    trials, _inadmissible = target_endpoint_mod.admit_rows(spec, trials)
    absent.extend(_inadmissible)
    if eligibility_contract:
        kept = []
        for trial in trials:
            pid = trial["id"].replace("PMID ", "")
            admission = eligibility_chain_mod.admission_record(
                trial, rec_by_id.get(pid), spec, eligibility_contract)
            failed = [dim for dim, cell in admission.items()
                      if cell.get("verdict") == "FAIL" and dim not in eligibility_chain_mod.COMPAT_AXES]
            if not failed:
                kept.append(trial)
                continue
            span = (rec_by_id.get(pid) or {}).get("abstract") or trial.get("source", "")
            absent.append({"id": trial["id"], "label": trial["label"],
                           "absent_kind": "adjudicated_absent", "state": "REFUSED_ON_EVIDENCE",
                           "reason_code": "REFUSED_ON_EVIDENCE", "source_span": span,
                           "verbatim_span": span, "admission": admission,
                           "eligibility_refusal_code": "TRIAL_FAILS_CONTRACT",
                           "eligibility_chain_rationale": ", ".join(failed),
                           "reason": "Protocol eligibility contract not satisfied: " + "; ".join(
                               f"{dim}={admission[dim]['trial_value']} (requires {admission[dim]['contract_value']})"
                               for dim in failed)})
        trials = kept
    # ESTIMAND-CONSISTENCY GUARD (continuous topics): a mean-difference topic must pool ONLY continuous
    # per-arm mean/SD data. If the source hierarchy fell through to a COUNT/proportion or a ratio effect
    # for a trial (e.g. a multi-arm trial whose continuous MADRS was refused, then a "% with >=50% response"
    # count was grabbed — a wrong estimand AND a wrong outcome), that trial is declared-absent, never mixed
    # into the MD pool. Symmetrically, a ratio-estimand topic never pools a bare continuous mean here.
    if (spec.get("estimand") or "").upper() == "MD":
        kept = []
        for t in trials:
            if t.get("mean1") is not None:
                kept.append(t)
            else:
                absent.append({"label": t["label"], "id": t["id"], "absent_kind": "refused_on_evidence",
                               "reason": ("estimand mismatch: this is a mean-difference (continuous) topic, "
                                          "but the only extractable value for this trial was a count/proportion "
                                          "or a ratio effect (not a per-arm mean/SD) — declared absent rather "
                                          "than pooled across estimands")})
        trials = kept
    # TIMEPOINT-CONSISTENCY GUARD (opt-in, continuous topics): pooling a percent-change measured at
    # different follow-up lengths mixes timepoints (weight loss is still accruing at 44 wk vs the
    # 68 wk pre-registered primary). When the outcome spec declares timepoint_weeks, a trial whose
    # ctgov outcome timeFrame endpoint differs by more than the tolerance is declared-absent — but
    # ONLY when a timepoint is actually parsed from the source (refuse on evidence, never on absence:
    # a trial with no parseable timepoint is left in the pool, not silently dropped). Semaglutide met
    # this first: STEP-1/STEP-3 report Week 68, but the regional STEP-12 (China) and Korean trials
    # report Week 44 — pooling all four would overstate k by mixing follow-up durations.
    tp = spec.get("timepoint_weeks")
    if tp is not None:
        tol = spec.get("timepoint_tolerance_weeks", 8)
        kept = []
        for t in trials:
            tw = t.get("timeframe_weeks")
            if tw is not None and abs(tw - tp) > tol:
                absent.append({"label": t["label"], "id": t["id"], "absent_kind": "refused_on_evidence",
                               "reason": (f"timepoint mismatch: the pre-registered primary timepoint is "
                                          f"Week {tp}, but this trial's source reports the outcome at "
                                          f"Week {tw:g} ({t.get('timeframe','')}) — declared absent rather "
                                          f"than pooled across follow-up durations")})
            else:
                kept.append(t)
        trials = kept
    # LOCATE IDENTITY GATE (opt-in, model-derived): a cached judgment that a trial's located evidence
    # is NOT the target outcome forces it to declared-absent — the safeguard against the right-number/
    # wrong-endpoint class. It can only REMOVE a mis-identified number, never add one.
    if locate_judgments:
        kept = []
        for t in trials:
            pid = str(t.get("id", "")).replace("PMID ", "")
            j = locate.rejects(locate_judgments, pid, spec["name"])
            if j:
                absent.append({"label": t["label"], "id": t["id"], "absent_kind": "refused_on_evidence",
                               "reason": (f"model outcome-identity gate (model-derived) — {j.get('reject_reason','')}: "
                                          + j.get("why", "")),
                               "locate_judgment": j})
            else:
                kept.append(t)
        trials = kept
    # PER-TRIAL VERIFICATION against committed source, computed at build and rendered (not assumed):
    # each pooled number's digits must be present in the committed abstract / structured source.
    for t in trials:
        if not t.get("selection_rule"):
            selected = design_key.select_estimator_by_source_hierarchy(t, [], selector_estimand)
            t.clear()
            t.update(selected)
        source_limit = source_hierarchy_mod.mixed_by_source_limit(t, estimand_decision)
        if source_limit:
            limits = t.setdefault("source_hierarchy_limitations", [])
            if not any(lim.get("code") == source_limit.get("code") for lim in limits):
                limits.append(source_limit)
        pid = str(t.get("id", "")).replace("PMID ", "")
        ab = (rec_by_id.get(pid) or {}).get("abstract", "")
        t["verified"], t["verify_basis"] = verify.verify_pooled(t, ab)
        if t.get("ai") is not None or t.get("mean1") is not None or t.get("e1i") is not None:
            t["derivation"] = t.get("derivation") or "reconstructed"
        elif t.get("effect") is not None:
            t["derivation"] = t.get("derivation") or "reported"
        design_key.stamp_trial(t, rec_by_id, registry_designs or {}, selector_estimand)
        if design_key.maybe_use_published_adjusted(t, selector_estimand):
            t.setdefault("selection_rule", "PUBLISHED_ADJUSTED_TARGET_CLASS")
            t.setdefault("alternatives", [])
            t["verified"], t["verify_basis"] = verify.verify_pooled(t, ab)
        if design_variance.apply_design_adjustment(t, spec.get("estimand")):
            t["verified"], t["verify_basis"] = verify.verify_pooled(t, ab)
    trials, design_refusals = design_key.split_design_refusals(trials)
    for t in design_refusals:
        absent.append(design_variance.refusal_absence(t))
    included_meta = {
        str(d.get("id")): {k: d.get(k) for k in screen_entry.DECISION_EXTRA_KEYS if k in d}
        for d in included
    }
    for row in absent:
        key = str(row.get("id", "")).replace("PMID ", "")
        meta = included_meta.get(key)
        if meta:
            row.update(meta)
    _apply_trial_annotations(spec, trials)
    for t in trials:
        if t.get("cross_source"):
            _refresh_cross_source_identity(t["cross_source"], spec, t.get("components"))
    out = {"name": spec["name"], "kind": kind, "primary": bool(spec.get("primary")),
           "estimand": spec.get("estimand", "RR"), "population": spec.get("population"),
           "timepoint": spec.get("timepoint"), "method": METHOD,
           "served_estimand": selector_estimand, "estimand_decision": estimand_decision,
           "trials": trials, "declared_absent_trials": absent}
    if spec.get("component_compat_key"):
        out["component_compat_key"] = True
    if design_refusals:
        out["design_refusals"] = [design_variance.design_refusal_row(t) for t in design_refusals]
    out["membership"] = membership_mod.build_outcome_membership(out, included)
    if design_refusals and len(trials) < 2:
        out["result"] = {
            "present": False,
            "reason": ("DESIGN REFUSAL: after refusing reconstructed non-parallel designs without an "
                       f"explicit design adjustment, only k={len(trials)} trial(s) remain; no pooled "
                       "number is rendered. Remaining and refused trials are named below."),
            "design_refusal": True,
            "k_after_design_refusal": len(trials),
            "refused": out["design_refusals"],
        }
    elif trials:
        meas = (selector_estimand or spec.get("estimand") or "RR").upper()
        meas = meas if meas in ("RR", "OR") else "RR"  # 2x2 pools as RR/OR; HR only via effect+CI
        def _meas(t):
            if t.get("e1i") is not None:
                return "IRR"
            if t.get("mean1") is not None:
                return "MD"
            return meas
        # The pooled scale reflects the data actually pooled: IRR if all rate-based, MD if all
        # continuous, else the topic's ratio estimand.
        if all(t.get("e1i") is not None for t in trials):
            pooled_scale = "IRR"
        elif all(t.get("mean1") is not None for t in trials):
            pooled_scale = "MD"
        elif all(t.get("scale") for t in trials) and len({t["scale"] for t in trials}) == 1:
            # Every pooled trial reported an explicit effect on the SAME scale -> display that scale,
            # not the topic's declared estimand. This stops a rate ratio (FAIR-HF2 total HF
            # hospitalizations, scale IRR) being labelled a risk ratio just because the topic
            # declared RR. Mixed scales fall through to the declared estimand (and are a known
            # heterogeneity the label makes visible, e.g. spironolactone RR/HR).
            pooled_scale = trials[0]["scale"]
        else:
            pooled_scale = selector_estimand or spec.get("estimand", "RR")
        studies = [Study(label=t["label"], ai=t.get("ai"), n1i=t.get("n1i"), ci=t.get("ci"),
                         n2i=t.get("n2i"), effect=t.get("effect"), ci_low=t.get("ci_low"),
                         ci_high=t.get("ci_high"),
                         e1i=t.get("e1i"), t1i=t.get("t1i"), e2i=t.get("e2i"), t2i=t.get("t2i"),
                         mean1=t.get("mean1"), sd1=t.get("sd1"), nc1=t.get("nc1"),
                         mean2=t.get("mean2"), sd2=t.get("sd2"), nc2=t.get("nc2"),
                         source=t.get("source", ""), measure=_meas(t),
                         derivation=t.get("derivation", ""), design=t.get("design"),
                         design_adjustment=t.get("design_adjustment")) for t in trials]
        for study, trial in zip(studies, trials):
            yi, vi = study.yi_vi()
            trial["study_effect"] = design_key.study_effect_object(
                trial,
                yi=yi,
                vi=vi,
                estimand=selector_estimand,
                analysis_population=spec.get("population"),
                scale=pooled_scale,
            )
            study.study_effect = trial["study_effect"]
        out["result"] = _pool_result(studies, scale=pooled_scale, require_study_effect=True)
        _alts = []
        for idx, t in enumerate(trials):
            alt = t.get("alternative_co_primary")
            if not isinstance(alt, dict) or alt.get("effect") is None:
                continue
            alt_trials = [dict(x) for x in trials]
            alt_trials[idx].update({
                "effect": alt.get("effect"),
                "ci_low": alt.get("ci_low"),
                "ci_high": alt.get("ci_high"),
                "scale": alt.get("scale", t.get("scale") or pooled_scale),
                "source": alt.get("source", t.get("source")),
            })
            alt_studies = [
                Study(label=x["label"], effect=x.get("effect"), ci_low=x.get("ci_low"),
                      ci_high=x.get("ci_high"),
                      ai=x.get("ai"), n1i=x.get("n1i"), ci=x.get("ci"), n2i=x.get("n2i"),
                      source=x.get("source", ""), measure=_meas(x))
                for x in alt_trials
            ]
            ar = _pool_result(alt_studies, scale=alt.get("scale", pooled_scale))
            _alts.append({
                "trial": t.get("label"),
                "selected": t.get("co_primary_selected") or t.get("components"),
                "alternative": alt.get("label") or alt.get("components"),
                "rule": alt.get("rule", "alternative prespecified co-primary endpoint sensitivity"),
                "pool": ar,
            })
        if _alts:
            out["result"]["co_primary_sensitivities"] = _alts
        if design_refusals:
            out["result"]["design_refusal"] = {
                "pool_changed": True,
                "refused": out["design_refusals"],
                "statement": ("Pool changed because a design refusal was added: reconstructed cluster, "
                              "crossover, cluster-crossover, and stepped-wedge trials require a held "
                              "design-adjusted effect or an ICC design-effect variance before this engine "
                              "can consume them."),
            }
        # HONEST MIXED-SCALE LABEL (estimand homogeneity): if the pooled trials do NOT share one
        # ratio estimand, the label must SAY so — never present a heterogeneous pool as a single
        # clean scale ("calling it an HR" when it mixed a count-RR and a Cox HR is the shipped defect
        # this kills). The pooling math is unchanged (per-study log-effects); only the displayed scale
        # becomes truthful, and scale_mixed flags it for the page and the weakness survey.
        # ESTIMAND TYPE SYSTEM + three-field object (TIER-1 #2 / audit 18): a pool's estimand status is
        # decided by COMPATIBILITY CLASS, not by reported label. Mixing labels WITHIN one class (RALES's
        # Cox "relative risk" + EMPHASIS's "hazard ratio" -- both first-event relative ratios) is
        # compatible and disclosed, NOT the old alarming "mixed (HR/RR)". Mixing ACROSS classes (a
        # recurrent-event rate ratio + a first-event hazard ratio -- the iv-iron defect, or an odds ratio
        # + risk ratio) is a genuine INCOMPATIBILITY and is flagged as such. The pooling math is unchanged
        # (per-study log-effects).
        for t in trials:
            if t.get("e1i") is not None:
                _rl = "IRR"
            elif t.get("mean1") is not None:
                _rl = "MD"
            elif t.get("ai") is not None:
                _rl = meas
            else:
                _rl = t.get("scale")
            # model cue read ONLY from the effect's own tightly-scoped source span (not the whole
            # abstract), so a distant unrelated "rate ratio"/"Cox" mention cannot mislabel this effect.
            t["effect_object"] = estmeasure.classify(_rl, t.get("source", "") or "")
        _compat = estmeasure.pool_compatibility([t["effect_object"] for t in trials])
        out["result"]["estmeasure"] = _compat
        _incompat = _compat["status"] == "incompatible"
        if _incompat:
            # FAIL CLOSED (audit 23, DETECTED-INVALID-BUT-PUBLISHED): a pool that mixes incompatible
            # estimand classes is NOT a valid summary, so we must SUPPRESS every derived number -- pooled
            # effect, CI, tau^2, prediction interval, common-effect sensitivity, leave-one-out (and, in the
            # page/manuscript, the forest plot and the result sentence). Detecting the failure and still
            # rendering the number is a caption, not a gate: disclosure is not suppression. Only the
            # per-trial estimates (out['trials']) and the reason survive; nothing pooled.
            # COUNTERFACTUAL (COMMIT 3 constraint): a refusal that hides what it refused is
            # indistinguishable from a bug. Before popping, record what the pool WOULD have produced
            # if the incompatible estimands were combined anyway -- clearly quarantined as INVALID,
            # never a usable number -- so the reader sees the refusal is a decision, not a gap.
            out["result"]["counterfactual"] = {
                "reason_code": "INCOMPATIBLE_ESTIMANDS",
                "would_be_estimate": out["result"].get("estimate"),
                "would_be_ci_low": out["result"].get("ci_low"),
                "would_be_ci_high": out["result"].get("ci_high"),
                "note": ("this is what pooling these incompatible estimand classes would have yielded; "
                         "it is INVALID and is shown only so the refusal is auditable, never as a result")}
            for _kpop in ("estimate", "ci_low", "ci_high", "tau2", "estimate_fixed", "ci_low_fixed",
                          "ci_high_fixed", "pi_low", "pi_high", "leave_one_out", "pi_note", "fixed_note",
                          "ci_note"):
                out["result"].pop(_kpop, None)
            out["result"]["scale"] = "INCOMPATIBLE (" + " + ".join(_compat["canonicals"]) + ")"
            out["result"]["scale_mixed"] = _compat["labels"]
            out["result"]["estmeasure_incompatible"] = True
            out["result"]["suppressed_incompatible"] = True
            out["result"]["suppressed_reason"] = (
                "pooled effect SUPPRESSED: the trials mix incompatible estimand classes ("
                + " + ".join(_compat["canonicals"]) + ") — these effect measures are not one quantity "
                "without an explicit, source-backed conversion, so no pooled effect, CI, heterogeneity "
                "or sensitivity is valid. "
                "The per-trial estimates are shown; pool each coherent strand separately.")
        elif _compat["status"] == "compatible_labels":
            # one compatibility class, >1 label: keep the pooled ratio scale, disclose the label mix
            out["result"]["scale_mixed"] = _compat["labels"]
        if not _incompat and out["result"].get("k") == 2:
            k2_mod.apply_k2_policy(
                out["result"],
                trials,
                anchor_config=k2_anchor_config,
            )
        # DECLARED METHOD MATCHES THE SCALE ACTUALLY POOLED: a mean-difference outcome must carry the
        # mean-difference method string, not the log-ratio one (the melatonin/esketamine/semaglutide-weight
        # defect). Chosen from the ACTUAL result scale via the single source of truth.
        out["method"] = method_text(out["result"].get("scale"))
        # COMPOSITE-HETEROGENEITY DISCLOSURE: a MACE/composite pool whose trials use different component
        # sets (COLCOT 5-point vs LoDoCo2 4-point) is disclosed, not refused (surfaced by the cross-family
        # definition audit). Object-derived from the pooled trials' committed source spans.
        _ch_srcs = []
        for t in trials:
            _pid = str(t.get("id", "")).replace("PMID ", "").strip() or str(t.get("label", ""))
            _ab = (rec_by_id.get(_pid) or rec_by_id.get(t.get("label")) or {}).get("abstract", "")
            _ch_srcs.append({
                "source": (_ab or "") + " " + (t.get("source", "") or ""),
                "endpoint_definition": t.get("endpoint_definition"),
            })
        _ch = extract.composite_heterogeneity(spec.get("name", ""), _ch_srcs)
        if _ch:
            out["result"]["composite_heterogeneity"] = _ch
        # LEAVE-ONE-OUT / influence, always rendered: at k>=3 drop each trial and re-pool to show how
        # much any single trial moves the estimate; at k<=2 it is not assessable and we say so (never
        # hidden). Uses the same pooler and scale; no new number is invented.
        k_now = out["result"].get("k")
        if isinstance(k_now, int) and k_now >= 3 and not _incompat and not out["result"].get("pool_refused"):
            loo = []
            for j in range(len(studies)):
                sub = studies[:j] + studies[j + 1:]
                r = _pool_result(sub, scale=pooled_scale)
                loo.append({"dropped": studies[j].label, "estimate": r.get("estimate")})
            ests = [x["estimate"] for x in loo if x["estimate"] is not None]
            base = out["result"].get("estimate")
            worst = max(loo, key=lambda x: abs((x["estimate"] or base) - base)) if (ests and base) else None
            out["result"]["leave_one_out"] = {
                "min": min(ests) if ests else None, "max": max(ests) if ests else None,
                "most_influential": worst["dropped"] if worst else None,
                "per_trial": loo,
                "note": "each row drops one trial and re-pools; a stable estimate across drops = no single trial drives it."}
        elif isinstance(k_now, int) and not _incompat and not out["result"].get("pool_refused"):
            out["result"]["leave_one_out"] = {"note": f"not assessable at k={k_now} (leave-one-out needs k>=3)"}
        if out["result"].get("k") == 1:
            # A single trial is not a random-effects meta-analysis: present it honestly as the
            # trial's own effect, and do not display tau^2 / HKSJ / prediction-interval machinery.
            out["method"] = ("Single included trial that reported this outcome — the estimate is that "
                             "trial's own effect; no random-effects pooling (tau^2, HKSJ and prediction "
                             "interval are not applicable at k=1).")
            out["result"].pop("tau2", None)
    else:
        # FALSE-ABSENCE guard (audit 28/blinded-AGY, harms class): distinguish GENUINELY NOT REPORTED from
        # REPORTED-BUT-NOT-EXTRACTABLE. If an outcome keyword appears in an included trial's committed
        # abstract but no arm counts / effect+CI could be extracted (e.g. a bare percentage with no
        # denominator — omega3 bleeding "2.7% vs 2.1%", pcsk9 injection-site reactions), the outcome is NOT
        # absent; saying "no trial reported this" is a false absence (most dangerous for harms). Disclose the
        # reporting trials and flag for full-text acquisition, which would recover the countable form.
        _kws = [str(k).lower() for k in (spec.get("keywords") or [spec.get("name", "")]) if k]
        _reported_by = []
        for d in included:
            _ab = ((rec_by_id.get(d["id"], {}) or {}).get("abstract", "") or "").lower()
            if _ab and any(k in _ab for k in _kws):
                _reported_by.append(d["id"])
        if _reported_by:
            out["result"] = {
                "present": False, "reported_not_extracted": True, "reported_by": _reported_by[:10],
                "reason": ("REPORTED but not extractable as a pooled value: " + ", ".join(_reported_by[:6])
                           + (" and others" if len(_reported_by) > 6 else "")
                           + " mention this outcome in the committed abstract, but without arm counts or an "
                           "effect+CI in an extractable form (e.g. a bare percentage with no denominator). This "
                           "outcome is NOT absent — it is reported-but-not-poolable from the committed source; "
                           "full-text acquisition would recover the countable form.")}
        else:
            out["result"] = {"present": False,
                             "reason": "no included trial reported this outcome with a percentage-corroborated "
                                       "count or an effect+CI in its abstract"}
    if out.get("design_refusals"):
        out["design_consumption"] = design_variance.consumption_summary(out)
        if isinstance(out.get("result"), dict):
            out["result"]["design_consumption"] = out["design_consumption"]
    return out


def _outcome_specs(config):
    specs = [(dict(config["primary_outcome"], primary=True), "efficacy")]
    for s in config.get("secondary_outcomes", []):
        specs.append((s, "efficacy"))
    for s in config.get("harm_outcomes", []):
        specs.append((s, "harm"))
    return specs


_LEDGER_SOURCE_GROUPS = {
    "PUBMED_CONCEPT_QUERY": "PubMed",
    "PUBMED_NCT_LINK": "PubMed",
    "PUBMED_LEGACY_QUERY": "PubMed",
    "PUBMED_PMID_ENUMERATION": "PubMed",
    "EXTRA_PMIDS": "PubMed",
    "CONTROL_PMIDS": "PubMed",
    "EUROPEPMC_QUERY": "Europe PMC (OA + metadata)",
    "EUROPEPMC_CONCEPT_QUERY": "Europe PMC (OA + metadata)",
    "EPMC_NCT_LINK": "Europe PMC (OA + metadata)",
    "CTGOV_SEARCH": "ClinicalTrials.gov",
    "CTGOV_CONDITION_INTERVENTION": "ClinicalTrials.gov",
    "CTGOV_NCT_LINK": "ClinicalTrials.gov",
    "ISRCTN_CONDITION_INTERVENTION": "ISRCTN",
    "REGISTRY_FIRST": "Registry-first (AACT)",
    "COMPARATOR_REFERENCES": "Citation chase",
    "COMPARATOR_REFERENCE_LIST": "Citation chase",
    "COMPARATOR_REFERENCE_LIST_PUBMED": "Citation chase",
    "PUBMED_ELINK_BACKWARD_CITATION": "Citation chase",
    "CITATION_CHASE": "Citation chase",
    "EPMC_BACKWARD_CITATION": "Citation chase",
    "EPMC_FORWARD_CITATION": "Citation chase",
    "MODEL_CALL": "Model call",
    "LEGACY_UNRECORDED": "Legacy unrecorded retrieval",
}
_STATE_SEVERITY = {"RAN_OK": 0, "RAN_ZERO": 1, "NOT_RUN": 2, "RAN_ERROR": 3}


def _ledger_source_status(ledger):
    out = {}
    for src in ledger.get("sources") or []:
        state = src.get("state")
        group = _LEDGER_SOURCE_GROUPS.get(src.get("kind")) or src.get("kind") or src.get("source_id")
        if not group or state not in _STATE_SEVERITY:
            continue
        prev = out.get(group)
        if prev is None or _STATE_SEVERITY[state] > _STATE_SEVERITY[prev]:
            out[group] = state
    return out


def _retrieval_summary(ledger):
    sources = []
    state_counts = {state: 0 for state in STATES}
    discovery_capable_sources = 0
    for src in ledger.get("sources") or []:
        state = src.get("state")
        if state in state_counts:
            state_counts[state] += 1
        if src.get("discovery_capable"):
            discovery_capable_sources += 1
        sources.append({
            "source_id": src.get("source_id"),
            "kind": src.get("kind"),
            "query": src.get("query"),
            "run_utc": src.get("run_utc"),
            "state": state,
            "error": src.get("error"),
            "discovery_capable": bool(src.get("discovery_capable")),
            "funnel": dict(src.get("funnel") or {}),
            "n_records": len(src.get("record_ids") or []),
        })
    return {
        "snapshot": dict(ledger["snapshot"]),
        "record_cap": ledger.get("record_cap"),
        "sources": sources,
        "state_counts": state_counts,
        "discovery_capable_sources": discovery_capable_sources,
        "enumeration_only": discovery_capable_sources == 0,
    }


def _source_status(slug, config, records, merged, ledger=None):
    """Four-state (RAN_OK / RAN_ZERO / RAN_ERROR / NOT_RUN) per search source, so a reader can see
    which adapters ran, which returned nothing, and which were not attempted for this topic. Prefers
    the status fetch actually recorded (records.source_status) and fills the rest DETERMINISTICALLY
    from committed artifacts (recall.json, fulltext_by_pmid, ctgov presence) — replay-safe, no network,
    process-metadata only (never a pooled number)."""
    # With a ledger, the adapter states are the RECORDED ones (worst state wins per named group), laid over
    # the inferred base so groups the ledger never ran (e.g. PMC full text) still render as NOT_RUN rather
    # than vanishing -- a missing row reads as "not observed", not as "did not run".
    if ledger:
        base = _source_status(slug, config, records, merged, None)
        base.update(_ledger_source_status(ledger))
        return base
    committed = records.get("source_status") or {}
    ft = records.get("fulltext_by_pmid") or {}
    rc = _load_recall(slug) or {}
    has_ctgov = bool(records.get("ctgov") or records.get("ctgov_results"))
    return {
        "PubMed": committed.get("pubmed") or ("RAN_OK" if merged else "RAN_ZERO"),
        "Europe PMC (OA + metadata)": committed.get("europepmc") or ("RAN_OK" if merged else "RAN_ZERO"),
        "ClinicalTrials.gov": "RAN_OK" if has_ctgov else ("RAN_ZERO" if config.get("ctgov") else "NOT_RUN"),
        "Citation chase": committed.get("citation_chase") or ("RAN_OK" if config.get("cite_chase") else "NOT_RUN"),
        "Registry-first (AACT)": (rc.get("status") if rc else None) or ("RAN_ERROR" if config.get("registry_first") else "NOT_RUN"),
        "PMC full text": "RAN_OK" if ft else ("RAN_ZERO" if config.get("fulltext") else "NOT_RUN"),
    }


@aact_cache.cache_only_build
def build_review_core(slug, config, records, protocol_sha):
    merged = _dedup(records, config.get("pivotal_trials"))
    retrieval_ledger = _load_retrieval_ledger(slug)
    from . import trial_family as trial_family_mod
    family_nodes = trial_family_mod.prepare(ROOT, slug, list(records.get('records') or []) + list(records.get('ctgov') or []), config, retrieval_ledger)
    retrieval_records = (retrieval_ledger.get("records") or {}) if retrieval_ledger else {}
    # ARMCONTRAST INTO SCREENING: inject this topic's committed, audit-confirmed non-contrast
    # evictions so screening excludes them at eligibility (not after pooling). Deterministic from
    # docs/contrast_evictions.json, so build and replay agree.
    if "contrast_evictions" not in config:
        try:
            _ce = json.load(open(os.path.join(ROOT, "docs", "contrast_evictions.json"), encoding="utf-8"))
            config = dict(config, contrast_evictions=(_ce.get("topics") or {}).get(slug, []))
        except (OSError, ValueError):
            pass
    # TRIAL<->REPORT entity model: merge audit-identified secondary/duplicate reports into
    # companion_reports so screening collapses them to their parent (X-DEDUP) before any count is
    # promoted to a trial count. Deterministic from docs/study_families.json; merged with any
    # companion_reports already in the topic config (dedup by pmid).
    try:
        _sf = json.load(open(os.path.join(ROOT, "docs", "study_families.json"), encoding="utf-8"))
        _rows = (_sf.get("topics") or {}).get(slug, [])
        if _rows:
            _existing = list(config.get("companion_reports") or [])
            _have = {str(c.get("pmid")) for c in _existing}
            _existing += [r for r in _rows if str(r.get("pmid")) not in _have]
            config = dict(config, companion_reports=_existing)
    except (OSError, ValueError):
        pass
    scr = screen.run(merged, config)
    rec_by_id = {r["id"]: r for r in merged}
    included = [d for d in scr["decisions"] if d["decision"] == "include"]
    interv = config.get("intervention_terms", ["colchicine"])
    comp = config.get("comparator_terms", ["placebo", "control"])

    cgr = records.get("ctgov_results") or {}
    ftbp = records.get("fulltext_by_pmid") or {}
    # Outcome-identity gate is OPT-IN per topic (config.outcome_identity) AND requires a committed
    # judgments cache; absent either, judgments=None and ctgov selection is the deterministic
    # substring match. This keeps every existing topic byte-identical until it opts in.
    ojudg = _load_outcome_judgments(slug) if config.get("outcome_identity") else None
    varms = _load_verified_arms(slug)
    veffs = _load_verified_effects(slug)
    dsel = _load_dose_selection(slug)
    ljudg = locate.load(slug) if config.get("locate_gate") else None
    registry_designs = design_key.registry_designs(records)
    eligibility_contract = None
    if config.get("eligibility_chain_enforced"):
        with open(os.path.join(ROOT, "protocols", slug + ".md"), encoding="utf-8") as f:
            eligibility_contract = eligibility_chain_mod.compile_contract(slug, config, f.read())
    outcomes = [_build_outcome(spec, kind, included, rec_by_id, interv, comp, cgr, ftbp,
                               outcome_judgments=ojudg, verified_arms=varms, locate_judgments=ljudg,
                               verified_effects=veffs, dose_selection=dsel,
                               registry_designs=registry_designs,
                               k2_anchor_config=config.get("k2_direction_conflict_anchor"),
                               eligibility_contract=eligibility_contract)
                for spec, kind in _outcome_specs(config)]
    primary = outcomes[0]

    comp_rec = rec_by_id.get(config.get("comparator_pmid")) or {}
    comp_abstract = comp_rec.get("abstract", "")
    comp_full = records.get("comparator_fulltext") or ""

    reported = []
    for co in config.get("comparator_outcomes", []):
        eff = extract.comparator_effect(comp_abstract, comp_full, co["keywords"])
        if eff:
            reported.append({"outcome": co["name"], "estimate": eff["effect"], "scale": eff["scale"],
                             "ci_low": eff["ci_low"], "ci_high": eff["ci_high"]})
    # comparator_k: a SOURCE-VERIFIED override for the comparator's trial count. The auto-extraction
    # below reads a number out of the comparator abstract with the topic's outcome keywords and is
    # unreliable (an external audit found it wrong on 4 topics: it grabbed a subgroup or a cited meta's
    # k, or missed the count entirely). Where the true count has been read from the comparator's own
    # text and recorded in the config (with the quote in comparator_k_source), that value is used and
    # the fragile auto-extraction is not.
    ck = config.get("comparator_k")
    if ck is not None:
        theirs_k = ck
    else:
        theirs_k = (extract.extract_meta(comp_abstract, config["primary_outcome"]["keywords"]).get("k")
                    or extract.extract_meta(comp_full, config["primary_outcome"]["keywords"]).get("k")
                    or "not stated in the comparator abstract/full text")
    oa = records.get("comparator_oa") or {}
    comp_year = comp_rec.get("year")
    ours_k = primary["result"].get("k") if isinstance(primary["result"], dict) and primary["result"].get("k") else len(primary["trials"])
    newer = []
    for d in included:
        ry = rec_by_id.get(d["id"], {}).get("year")
        try:
            if comp_year and ry and int(ry) > int(comp_year):
                newer.append(rec_by_id.get(d["id"], {}).get("acronym") or d["id"])
        except ValueError:
            pass
    comp_scope = scope.assess(config, comp_rec.get("title") or "", comp_abstract)
    if invalid_note := parity_relation.invalid_scope_override(ROOT, slug):
        comp_scope = {**comp_scope, "scope_valid": False, "note": invalid_note}
    comparator = {
        "name": comp_rec.get("title") or "comparator", "year": comp_year,
        "journal": comp_rec.get("journal"), "pmid": comp_rec.get("id"), "doi": comp_rec.get("doi"),
        "url": (f"https://doi.org/{comp_rec.get('doi')}" if comp_rec.get("doi") else None),
        "open_access": bool(oa.get("is_oa")), "reported": reported,
        "scope": comp_scope,
        "overlap": {"ours_k": ours_k, "theirs_k": theirs_k,
                    **({"theirs_k_source": config["comparator_k_source"]} if config.get("comparator_k_source") else {}),
                    "shared_k": "not exactly verifiable (comparator trial table not machine-exposed)",
                    "only_ours": newer, "only_theirs": [],
                    "method": "publication-date + design identity (comparator trial list not extracted from source)",
                    "note": (f"Trials newer than the comparator ({comp_year}) cannot be in it (only-ours, "
                             f"verifiable by date). Exact shared count not asserted.")},
    }
    if slug in comparator_second_pass.PROFILES:
        comparator = comparator_second_pass.apply(slug, config, records, comp_rec, comparator)
    if slug in comparator_truth.PAGE_ANNOTATION_SLUGS:
        _comp_text = comparator_truth.load_cached_comparator_text(
            ROOT, slug, comparator.get("pmid"), (comp_full or comp_abstract)
        )
        comparator = comparator_truth.annotate_comparator(
            slug, comparator, primary.get("trials") or [], config, _comp_text
        )
    comparator_scope_note = config.get("comparator_scope_note")
    if (primary.get("result") or {}).get("design_refusal"):
        refused_names = ", ".join(
            str(x.get("trial") or x.get("id")) for x in (primary.get("design_refusals") or [])
        )
        comparator_scope_note = (
            f"Design-key update: our primary pool is now k={ours_k} after refusing reconstructed "
            f"non-parallel designs without an explicit design adjustment"
            + (f" ({refused_names})." if refused_names else ".")
            + " Any earlier same-scope k/parity note is superseded for this build; refused trials remain "
              "screened-in eligible records but are named exclusions, not pooled counts."
        )

    # DECLARED method = the method for the primary outcome's DECLARED estimand (from the config/protocol).
    # The SERVED method (set on the manifest by build_topic from the primary's ACTUAL result scale) is
    # derived independently, so the gate's declared==served limb can actually fail when they diverge.
    _declared_method = method_text((primary.get("estimand") or "RR"))
    if retrieval_ledger:
        screening_records = []
        for d in scr["decisions"]:
            found_by = (retrieval_records.get(str(d["id"])) or {}).get("found_by") or ["UNRECORDED"]
            screening_records.append({
                "id": (f"{rec_by_id.get(d['id'],{}).get('acronym')} · " if rec_by_id.get(d['id'],{}).get('acronym') else "") + str(d["id"]),
                "id_type": d["id_type"], "decision": d["decision"],
                "rule_id": d["rule_id"], "reason": d["reason"],
                "span": d.get("span", ""), "found_by": found_by,
                **({"matched_intervention": d.get("matched_intervention")} if d.get("matched_intervention") else {}),
                **{k: d.get(k) for k in screen_entry.DECISION_EXTRA_KEYS if k in d},
                **({"arm_object": d.get("arm_object")} if d.get("arm_object") else {}),
                **({"arm_object_hidden_eligible_contrast": d.get("arm_object_hidden_eligible_contrast")}
                   if d.get("arm_object_hidden_eligible_contrast") else {}),
            })
    else:
        screening_records = [{"id": (f"{rec_by_id.get(d['id'],{}).get('acronym')} · " if rec_by_id.get(d['id'],{}).get('acronym') else "") + str(d["id"]),
                              "id_type": d["id_type"], "decision": d["decision"],
                              "rule_id": d["rule_id"], "reason": d["reason"],
                              "span": d.get("span", ""),
                              **({"matched_intervention": d.get("matched_intervention")} if d.get("matched_intervention") else {}),
                              **{k: d.get(k) for k in screen_entry.DECISION_EXTRA_KEYS if k in d},
                              **({"arm_object": d.get("arm_object")} if d.get("arm_object") else {}),
                              **({"arm_object_hidden_eligible_contrast": d.get("arm_object_hidden_eligible_contrast")}
                                 if d.get("arm_object_hidden_eligible_contrast") else {})}
                             for d in scr["decisions"]]

    _adj = _apply_adjudicator_flags(slug, screening_records)
    screening_records = _adj["records"]

    source_status = _source_status(slug, config, records, merged, retrieval_ledger)
    retrieval_class = classify_retrieval(
        config,
        retrieval_ledger,
        source_status.get("Registry-first (AACT)"),
    )
    protocol_text = _read_text("protocols", slug + ".md")
    scope_identity = scope_identity_mod.assess(
        config=config,
        protocol_text=protocol_text,
        search={"retrieval_class": retrieval_class},
        ledger=retrieval_ledger,
        slug=slug,
    )

    integrity = membership_mod.integrity_with_membership(_load_integrity(slug), outcomes)
    arm_contrast = design_variance.current_arm_contrast(_load_arm_contrast(slug), primary)

    review = {
        "slug": slug, "title": config["title"], "question": config["question"],
        "method_declared": _declared_method,
        "protocol": {"sha": protocol_sha, "committed_utc": records.get("fetched_utc"),
                     "method_declared": _declared_method,
                     # Eligibility is GENERATED from the include object the screen enforces, so the
                     # declared eligibility on the page cannot drift from the code that screens.
                     "eligibility": screen.describe_eligibility(config.get("include", {})),
                     "text": protocol_text},
        "search": {"n_records": len(merged), "cache_ref": f"cache/{slug}/records.json",
                   "run_utc": records.get("fetched_utc"), "databases": ["PubMed", "ClinicalTrials.gov"],
                   "sources": [{"name": "PubMed", "queries": records.get("pubmed_queries", [])},
                               {"name": "ClinicalTrials.gov", "queries": [json.dumps(records.get("ctgov_query"))]}],
                   "retrieval_class": retrieval_class,
                   "source_status": source_status,
                   **({"retrieval": _retrieval_summary(retrieval_ledger)} if retrieval_ledger else {}),
                   **({"recall": _rc} if (_rc := _load_recall(slug)) else {}),
                   **({"ghost": _gh} if (_gh := _load_ghost(slug)) else {})},
        "screening": {"records": screening_records,
                      "positive_control": scr["positive_control"], "negative_control": scr["negative_control"],
                      "dual": _with_model_adjudication(slug, screen.run_dual(merged, config), scr["decisions"]),
                      **({"adjudicator_pending": _adj["pending"]} if _adj.get("pending") else {})},
        "scope_identity": scope_identity,
        "outcomes": outcomes,
        "comparator": comparator,
        "estimand_exclusions": config.get("estimand_exclusions", []),
        **({"comparator_scope_note": comparator_scope_note} if comparator_scope_note else {}),
        **({"evidence_base_caveat": config["evidence_base_caveat"]} if config.get("evidence_base_caveat") else {}),
        **({"rob2": _rb} if (_rb := _load_rob2(slug)) else {}),
        # Arm-contrast disclosure (TIER-1 structural fix): per pooled trial, whether the intervention of
        # interest is a parser-confirmed RANDOMISED CONTRAST or a fail-open/background inclusion. Visible,
        # never silent -- a trial admitted with no registry arm data reads 'contrast unverified', not verified.
        **({"arm_contrast": arm_contrast} if arm_contrast else {}),
        **({"integrity": integrity} if integrity else {}),
        # Unit-of-analysis disclosure (ME-26/27): pooled trials with a cluster-randomized or crossover
        # design, from the committed abstracts. Rendered as a caveat; not an adjustment (ICC unavailable).
        **({"unit_of_analysis": _uoa} if (_uoa := unit_of_analysis.scan_pooled({"outcomes": outcomes}, rec_by_id)) else {}),
        # Per-trial funding / COI disclosure (ME-32): classify each pooled trial's funding source from a
        # verbatim statement in the committed full text (preferred) or abstract; industry funding is the
        # documented bias direction. Rendered as a disclosure; never inferred, 'not stated' when silent.
        **({"funding": _fund} if (_fund := funding.scan_pooled({"outcomes": outcomes}, rec_by_id, ftbp)) else {}),
        # Cross-family definition-audit findings for this topic (rendered so a recorded mismatch is visible).
        **({"definition_audit": _da} if (_da := _load_definition_audit(slug)) else {}),
        # Corpus-level RoB span-check agreement (rendered on the RoB tab).
        **({"rob_spancheck": _rsc} if (_rsc := _load_rob_spancheck()) else {}),
    }
    identity_mod.annotate_review(review, merged, config.get("companion_reports") or [])
    _annotate_completeness(review, rec_by_id)
    # CANONICAL CLAIM: one derivation of significance / null-crossing / direction per result,
    # attached to every outcome (primary, secondary, harms) and every transcribed comparator claim,
    # so a surface DERIVES the stated judgement from one object instead of recomputing it (the
    # card<->object mismatch class). Part of the canonical core (hashed into review_sha256), so it
    # reproduces from the committed cache. Purely additive: no existing rendered number changes.
    for _o in review.get("outcomes", []):
        if isinstance(_o.get("result"), dict):
            _o["result"]["claim"] = claim_mod.derive(_o["result"])
    _cmp = review.get("comparator")
    if isinstance(_cmp, dict):
        for _r in _cmp.get("reported", []):
            if isinstance(_r, dict):
                _r["claim"] = claim_mod.derive(_r)
    # DECLARED STRANDS are result-bearing objects for this topic, not index-only prose.
    # Attach them before invalidation so strand members count as pooled membership.
    claimgraph_mod.attach_strands(review, ROOT)
    # PROTOCOL COMPILER (two independent sources): compare the PROSE protocol against the executable
    # config before invalidation, because identifier-scope needs the PICO I-line quote for its reason.
    _protocol_i_line = ""
    try:
        _md = open(os.path.join(ROOT, "protocols", slug + ".md"), encoding="utf-8").read()
        _protocol_i_line = protocol_compiler_mod.intervention_line(_md)
        _div = protocol_compiler_mod.compare(slug, _md, config)
        _amendments = protocol_compiler_mod.scope_amendments(_md)
        review["protocol_config"] = {"divergences": _div, "intervention_i_line": _protocol_i_line}
        if _amendments:
            review["protocol_history"] = {"amendments": _amendments}
    except OSError:
        pass
    _protocol_controls = design_variance.protocol_control_expectations(review)
    if _protocol_controls:
        review.setdefault("protocol", {})["control_expectations"] = _protocol_controls
    # IDENTIFIER SCOPE: detect a single-agent slug over a class-level included pool structurally
    # from the configured declaration and screening object, before any downstream gate can reassure it.
    _scope_config = dict(config)
    if _protocol_i_line:
        _scope_config["protocol_i_line"] = _protocol_i_line
    if review.get("protocol_history"):
        _scope_config["protocol_scope_amendments"] = review["protocol_history"].get("amendments") or []
    review["identifier_scope"] = invalidation_mod.identifier_scope(
        slug, _scope_config, (review.get("screening") or {}).get("records") or []
    )
    # INVALIDATION PROPAGATION: one per-topic STALE verdict from committed signals (retraction of a
    # pooled trial, primary reported-but-not-extracted, an ELIGIBLE trial declared absent, a search
    # source that errored). Poisons the dependent outputs -- the page renders a STALE banner and the
    # index counts STALE topics -- so a known-incomplete/unproven result cannot read as current.
    _inv_sig = _invalidation_signals(slug)
    # Identity crosswalk (read-only session #1, NAMED_BUT_UNBOUND): resolve a record's identifiers so a
    # trial screened-in under one id (NCT) but pooled under another (PMID) is not falsely counted
    # eligible-not-pooled. Built from the merged records' own nct field; verified 0 cross-space cases
    # today, wired as defense-in-depth so it stays 0.
    _inv_sig["id_nct"] = {str(r["id"]): str(r.get("nct")) for r in merged if r.get("nct")}
    review["invalidation"] = invalidation_mod.assess(review, _inv_sig)
    if _inv_sig.get("never_considered"):
        review["never_considered"] = _inv_sig["never_considered"]
    # COMPATIBILITY KEY: the explicit key each pooled outcome satisfies (effect measure, event
    # process, endpoint, follow-up window, analysis set, randomised contrast). Attached per pooled
    # outcome so the contract that lets its trials be pooled is auditable on the page; a backstop in
    # the build refuses a pool whose trials do not share the hard dimensions (defense in depth).
    for _o in review.get("outcomes", []):
        endpoint_canonical_mod.annotate_outcome(_o, slug)
        _ck = compat_mod.outcome_key(_o, review)
        if _ck:
            _o["compat_key"] = _ck
        _cd = compat_direction_mod.outcome_directions(_o, review)
        if _cd.get("dimensions"):
            _o["compat_direction"] = _cd
        _ev = endpoint_canonical_mod.diagnose(_o, slug, _ck)
        if _ev:
            _o["endpoint_canonical_diagnostics"] = _ev
        # DERIVATION provenance (melatonin defect: a harness-computed MD shown as 'the trial's own
        # effect'): label each pooled number reported (the source gave the effect+CI directly) vs
        # reconstructed (the harness computed it from arm counts / means / person-time). Both are
        # legitimate; conflating them is not.
        for _t in (_o.get("trials") or []):
            if _t.get("ai") is not None or _t.get("mean1") is not None or _t.get("e1i") is not None:
                _t["derivation"] = _t.get("derivation") or "reconstructed"
            elif _t.get("effect") is not None:
                _t["derivation"] = _t.get("derivation") or "reported"
        # RECOVERY-INDUCED-INCOMPATIBILITY RECHECK: a recovery is verified before integration, but
        # adding a trial can break the POOL it joins. Re-run the compatibility contract on the whole
        # outcome AFTER integration (derivation now set) and record the verdict + any disclosure. This
        # runs every build, so it re-checks after any recovery, not just when the trial was verified.
        _rr = recovery_recheck_mod.recheck_outcome(_o, review)
        if _rr:
            _o["recovery_recheck"] = _rr
            _disc = recovery_recheck_mod.disclosure(_rr)
            if _disc:
                _o["recovery_disclosure"] = _disc
    # REFUSAL-REASON TRUTH (STATE root system): a declared-absent/refused row must say what the cached
    # source actually supports. SOURCE_NOT_RETRIEVED is reserved for a missing cached abstract; if an
    # outcome effect is visible but belongs to a different estimand class, the row says so and quotes
    # the source span. This annotation never makes a value poolable; it only replaces generic fallback
    # prose with a typed, source-backed refusal.
    _kw_by_name = {sp.get("name"): sp.get("keywords") for sp, _ in _outcome_specs(config)}
    _spec_by_name = {sp.get("name"): sp for sp, _ in _outcome_specs(config)}
    for _o in review.get("outcomes", []):
        _kws = _kw_by_name.get(_o.get("name")) or []
        _sp = _spec_by_name.get(_o.get("name")) or {}
        for _t in (_o.get("declared_absent_trials") or []):
            _pid = str(_t.get("id", "")).replace("PMID ", "")
            _ab = (rec_by_id.get(_pid) or {}).get("abstract", "")
            _ftp = os.path.join(ROOT, "cache", slug, f"ft_{_pid}.txt")
            _ft = None
            if os.path.exists(_ftp):
                try:
                    _ft = open(_ftp, encoding="utf-8").read()
                except OSError:
                    _ft = None
            _ann = absence_mod.classify_reason(
                _kws, _ab, _ft,
                outcome_name=_o.get("name"),
                declared_estimand=_sp.get("estimand") or _o.get("estimand"),
                reason=_t.get("reason"),
                absent_kind=_t.get("absent_kind"),
                row=_t,
            )
            for _ak, _av in _ann.items():
                if _av not in (None, "", []):
                    _t[_ak] = _av
    # COMPATIBILITY-UNDERLYING CHECK (lane CK): derive the compatibility dimensions from every pooled trial row
    # and its committed source text; an asserted uniform key the rows do not support is relabelled mixed/trial-defined.
    compat_check_mod.enrich(review, records)
    # KNOWN-MISSING SENSITIVITY: invalidation names eligible evidence outside the primary pool.
    # This panel keeps the primary untouched and shows only source-backed re-pools as SENSITIVITY.
    known_missing_mod.build(review, _inv_sig, rec_by_id, records)
    consumer_consistency_mod.annotate_review(review, slug, config, records)
    # RX measurement layer: verify the declared reason codes and enumerate included-trial x
    # registered-outcome values visible in held sources but not extracted. This is deliberately
    # additive: it annotates the review object and row-level audit fields, but never changes the
    # extractor output, reason_code, membership, or pool.
    _src_map = reason_audit_mod.sources_by_trial(slug, records, ROOT)
    reason_audit_mod.annotate_review(slug, review, _spec_by_name, _src_map)
    unextracted_mod.annotate_review(slug, review, _spec_by_name, _src_map)
    if slug == "colchicine-postop-af" or config.get("eligibility_chain_enforced"):
        try:
            _md = open(os.path.join(ROOT, "protocols", slug + ".md"), encoding="utf-8").read()
            eligibility_chain_mod.apply_admissions(review, config, records, _md)
        except OSError:
            pass
    harms_mod.annotate_review(review, _spec_by_name, included, rec_by_id, ftbp)
    # PROTOCOL COMPILER (two independent sources): compare the PROSE protocol against the executable
    # config so a divergence (estimand, analysis set, design masking AND/OR) between the registered
    # prose and the machine rules cannot pass -- the tocilizumab self-certification defect (a check
    # that reads only the artefact it certifies). Divergences are rendered + counted; each is a defect
    # to resolve or a dated amendment to declare, never a silent widening.
    if "protocol_config" not in review:
        try:
            _md = open(os.path.join(ROOT, "protocols", slug + ".md"), encoding="utf-8").read()
            _div = protocol_compiler_mod.compare(slug, _md, config)
            review["protocol_config"] = {"divergences": _div,
                                         "intervention_i_line": protocol_compiler_mod.intervention_line(_md)}
        except OSError:
            pass
    # RoB-stratified sensitivity re-pool of the primary outcome (regenerates from the object, so the
    # figure the page renders is reproduced, not typed). Uses the same validated pooler.
    # RoB-stratified sensitivity is a RE-POOL, so it must also fail closed on an INCOMPATIBLE primary
    # pool (audit 23): re-pooling incompatible estimands is as invalid as the primary pool itself.
    _prim_res = next((o.get("result") or {} for o in review.get("outcomes", []) if o.get("primary")), {})
    if (_prim_res.get("present") is not False
            and not _prim_res.get("suppressed_incompatible")
            and not _prim_res.get("pool_refused")
            and (_sens := rob_sens_mod.sensitivity(review))):
        # At k=2 the registered CI is refused (K2_SINGLE_DF); rob_sensitivity.sensitivity() marks the
        # stratum CIs refused itself so the block renders strata + point estimates rather than vanishing.
        review["rob_sensitivity"] = _sens
    # Partial, object-derived GRADE certainty (risk-of-bias, inconsistency, imprecision, registry-based
    # publication bias computed from committed fields; indirectness left to human judgement).
    if (_grade := grade_mod.grade(review, _load_ghost(slug))):
        review["grade"] = _grade
        design_variance.annotate_grade(review)
    if any(
        _t.get("target_endpoint_class")
        for _o in review.get("outcomes", [])
        for _t in (_o.get("trials") or [])
    ):
        review.setdefault("protocol", {})["target_endpoint_selection"] = (
            target_endpoint_mod.protocol_rule_object()
        )
    # Scientific consumers above join held report-keyed RoB/GRADE evidence.
    # Family identity is additive; regenerate the dependent sensitivity stamp afterwards.
    trial_family_mod.attach_review(review, family_nodes)
    known_missing_mod.build(review, _inv_sig, rec_by_id, records)
    claimgraph_mod.stamp_review(review)
    _cg_bad = claimgraph_mod.check(review)
    if _cg_bad:
        raise ValueError("CLAIMGRAPH CONTRADICTION (build refused): " + json.dumps(_cg_bad))
    review["limitations"] = build_limitations(review)
    review = propositions_mod.attach(review)
    _prop_bad = propositions_mod.check_propositions(review)
    if _prop_bad:
        raise ValueError("PROPOSITION CONTRADICTION (build refused): " + json.dumps(_prop_bad))
    from . import comparator_panel
    review["comparator_panel"] = comparator_panel.attach(slug, review, ROOT)
    return review


def build_comparator_core(slug, config, records):
    comp_rec = {r["id"]: r for r in _dedup(records)}.get(config.get("comparator_pmid")) or {}
    comp_abstract = comp_rec.get("abstract", "")
    comp_full = records.get("comparator_fulltext") or ""
    k = (extract.extract_meta(comp_abstract, config["primary_outcome"]["keywords"]).get("k")
         or extract.extract_meta(comp_full, config["primary_outcome"]["keywords"]).get("k"))
    outcomes = []
    for i, co in enumerate(config.get("comparator_outcomes", [])):
        eff = extract.comparator_effect(comp_abstract, comp_full, co["keywords"])
        if eff:
            outcomes.append({"name": co["name"], "kind": co.get("kind", "efficacy"), "primary": i == 0,
                             "estimand": eff["scale"], "population": "as reported", "timepoint": "as reported",
                             "method": "Random-effects meta-analysis (as reported by the source).",
                             "result": {"k": k, "estimate": eff["effect"], "scale": eff["scale"],
                                        "ci_low": eff["ci_low"], "ci_high": eff["ci_high"]},
                             "trials": [], "declared_absent_trials": []})
        else:
            outcomes.append({"name": co["name"], "kind": co.get("kind", "efficacy"), "primary": i == 0,
                             "estimand": "RR", "result": {"present": False, "reason": "not reported/extractable from the source text"}})
    if not outcomes:
        outcomes = [{"name": config["primary_outcome"]["name"], "kind": "efficacy", "primary": True,
                     "estimand": "RR", "result": {"present": False, "reason": "no pooled effect extractable"}}]
    for _o in outcomes:  # canonical claim on the comparator page's own outcomes too
        if isinstance(_o.get("result"), dict):
            _o["result"]["claim"] = claim_mod.derive(_o["result"])
    return {
        "slug": slug + "-comparator", "title": config["title"], "question": config["question"],
        "method_declared": "Random-effects meta-analysis (as reported).",
        "protocol": {"present": False, "reason": "transcribed from a published meta-analysis; no machine-readable protocol provided by the source."},
        "search": {"n_records": None, "databases": ["as reported by the source"],
                   "sources": [{"name": "source publication", "queries": ["(reported in the article)"]}],
                   "run_utc": comp_rec.get("year")},
        "screening": {"present": False, "reason": "per-record screening not reproduced from the source."},
        "outcomes": outcomes,
        "comparator": {"present": False, "reason": "not applicable on the comparator's own page"},
        "reproduction": {"present": False, "reason": "the source publication provides no machine-checkable reproduction census."},
    }
