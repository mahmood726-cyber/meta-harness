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


def _norm_text(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _fold_for_prose(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def intervention_line(md_text):
    """Return the protocol PICO intervention line, including wrapped continuation lines."""
    lines = (md_text or "").splitlines()
    out = []
    collecting = False
    start_re = re.compile(r"^\s*-\s*\*\*(?:I|Intervention)\b[^*]*\*\*\s*(?:[-:–—])?\s*(.*)$", re.I)
    bullet_re = re.compile(r"^\s*-\s*\*\*")
    for line in lines:
        m = start_re.match(line)
        if m:
            out = [m.group(1).strip()]
            collecting = True
            continue
        if collecting:
            if bullet_re.match(line):
                break
            if line.startswith((" ", "\t")) and line.strip():
                out.append(line.strip())
                continue
            if not line.strip():
                break
            break
    return _norm_text(" ".join(out))


def _intervention_declaration_divergences(md_text, config):
    agents = config.get("intervention_agents")
    class_terms = config.get("intervention_class_terms")
    if agents is None and class_terms is None:
        return []
    div = []
    if not isinstance(agents, dict):
        div.append({"code": "INTERVENTION_DECLARATION_MALFORMED", "dimension": "intervention_agents",
                    "prose": "protocol", "config": "intervention_agents must be an object"})
        agents = {}
    if not isinstance(class_terms, list):
        div.append({"code": "INTERVENTION_DECLARATION_MALFORMED", "dimension": "intervention_class_terms",
                    "prose": "protocol", "config": "intervention_class_terms must be a list"})
        class_terms = []

    declared: dict[str, list[str]] = {}
    for agent, terms in sorted((agents or {}).items()):
        if not isinstance(terms, list):
            div.append({"code": "INTERVENTION_DECLARATION_MALFORMED", "dimension": "intervention_agents",
                        "prose": str(agent), "config": "agent terms must be a list"})
            continue
        for term in terms:
            declared.setdefault(_norm_text(term), []).append(f"agent:{agent}")
    for term in class_terms or []:
        declared.setdefault(_norm_text(term), []).append("class")

    for term in config.get("intervention_terms") or []:
        key = _norm_text(term)
        owners = declared.get(key, [])
        if not owners:
            div.append({"code": "INTERVENTION_TERM_UNDECLARED", "dimension": "intervention_declaration",
                        "prose": "intervention_terms", "config": str(term)})
        elif len(owners) > 1:
            owners = sorted(set(owners))
        if len(owners) > 1:
            div.append({"code": "INTERVENTION_TERM_AMBIGUOUS", "dimension": "intervention_declaration",
                        "prose": str(term), "config": ", ".join(owners)})

    iline = intervention_line(md_text)
    folded_line = _fold_for_prose(iline)
    for agent in sorted((agents or {}).keys()):
        folded_agent = _fold_for_prose(agent)
        if folded_agent and folded_agent not in folded_line:
            div.append({"code": "INTERVENTION_AGENT_PROSE_DIVERGENCE", "dimension": "intervention_i_line",
                        "prose": iline or "(missing PICO intervention line)", "config": str(agent)})
    return div


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
    div.extend(_intervention_declaration_divergences(md_text, config))
    return div
