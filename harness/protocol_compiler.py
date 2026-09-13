"""Protocol compiler + config-equality check (two INDEPENDENT sources).

The prose protocol (protocols/<slug>.md, human-written) and the executable config
(topics/<slug>.json, machine-read) are maintained separately. A conformance check that reads
only the config it certifies cannot fail (the tocilizumab self-certification defect: a check
derived from the artefact it checks). This compiler parses the PROSE protocol and compares it to
the CONFIG across dimensions that can genuinely disagree -- estimand, analysis population, and
design masking -- so the two sources can fail APART. Divergences are reported with codes; a
divergence is a defect to resolve or a dated amendment to declare, never silently widened.
"""
import re

_ESTIMAND_CANON = {"hr": "HR", "hazard ratio": "HR", "rr": "RR", "risk ratio": "RR",
                   "or": "OR", "odds ratio": "OR", "md": "MD", "mean difference": "MD",
                   "smd": "SMD", "irr": "IRR", "incidence rate ratio": "IRR"}


def _canon_estimand(s):
    s = (s or "").lower()
    # prefer an explicit parenthesised code, else a phrase
    m = re.search(r"\((hr|rr|or|md|smd|irr)\)", s)
    if m:
        return m.group(1).upper()
    for k in ("hazard ratio", "risk ratio", "odds ratio", "mean difference", "incidence rate ratio"):
        if k in s:
            return _ESTIMAND_CANON[k]
    return None


def parse_prose(md_text):
    """Extract {estimand, population, design_masking} from a prose protocol. Conservative: returns
    None for a field it cannot locate (so a missing field is 'not stated', never a false match)."""
    t = md_text or ""
    out = {"estimand": None, "population": None, "design_masking": None}
    m = re.search(r"\*\*Estimand[:*]*\*\*\s*[-:–]\s*([^\n.]+)", t, re.I)
    if m:
        out["estimand"] = _canon_estimand(m.group(1))
    m = re.search(r"\*\*Population[:*]*\*\*\s*[-:–]\s*([^\n.]+)", t, re.I)
    if m:
        p = m.group(1).lower()
        if "intention-to-treat" in p or "intention to treat" in p or "itt" in p:
            out["population"] = "intention-to-treat"
        elif "per-protocol" in p or "per protocol" in p:
            out["population"] = "per-protocol"
    tl = t.lower()
    # design masking conjunction: does the prose require double-blind AND placebo, or OR?
    if re.search(r"double-blind\s+or\s+placebo", tl):
        out["design_masking"] = "OR"
    elif re.search(r"double-blind[,;]?\s+(?:and\s+)?placebo", tl) or "double-blind, placebo-controlled" in tl:
        out["design_masking"] = "AND"
    return out


def _config_estimand(config):
    e = ((config.get("primary_outcome") or {}).get("estimand") or "").upper()
    return _ESTIMAND_CANON.get(e.lower(), e or None)


def compare(slug, md_text, config):
    """Return the list of protocol<->config divergences for one topic (empty if they agree on the
    checkable dimensions). Each divergence carries a machine-readable code."""
    prose = parse_prose(md_text)
    div = []
    ce = _config_estimand(config)
    if prose["estimand"] and ce and prose["estimand"] != ce:
        div.append({"code": "ESTIMAND_DIVERGENCE", "dimension": "estimand",
                    "prose": prose["estimand"], "config": ce})
    cp = ((config.get("primary_outcome") or {}).get("population") or "").lower()
    if prose["population"]:
        cpc = "intention-to-treat" if ("intention" in cp or "itt" in cp) else (
            "per-protocol" if "per-protocol" in cp or "per protocol" in cp else (cp or None))
        if cpc and cpc != prose["population"]:
            div.append({"code": "POPULATION_DIVERGENCE", "dimension": "analysis_set",
                        "prose": prose["population"], "config": cpc})
    # design masking AND/OR fidelity: config encodes AND (design_double_blind True AND a comparator
    # requirement). If the prose says OR, the eligibility is silently widened in one source.
    inc = config.get("include") or {}
    cfg_and = bool(inc.get("design_double_blind")) and bool(inc.get("comparator_any"))
    if prose["design_masking"] == "OR" and cfg_and:
        div.append({"code": "DESIGN_MASKING_ANDOR", "dimension": "design",
                    "prose": "double-blind OR placebo-controlled",
                    "config": "double-blind AND placebo-controlled"})
    return div
