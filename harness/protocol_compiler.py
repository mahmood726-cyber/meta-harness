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
    out = {"estimand": None, "estimand_preference": None, "population": None, "design_masking": None}
    m = re.search(r"\*\*Estimand[:*]*\*\*\s*[-:–]\s*([^\n.]+)", t, re.I)
    if m:
        estimand_line = m.group(1)
        out["estimand"] = _canon_estimand(estimand_line)
        folded = _fold_for_prose(estimand_line)
        permits_counts = any(x in folded for x in (
            "when arm counts", "arm counts are extractable", "risk ratio", "rr"
        ))
        permits_published_tte = any(x in folded for x in (
            "published hr", "published hazard", "hazard ratio", "hr rr", "hr or rr"
        ))
        explicit_preference = any(x in folded for x in (
            "prefer hazard", "prefer published", "cumulative risk as primary",
            "cumulative risk estimand", "risk ratio preferred"
        ))
        if permits_counts and permits_published_tte and not explicit_preference:
            out["estimand_preference"] = "UNDECLARED"
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


def scope_amendments(md_text):
    """Parse dated protocol amendments that explicitly change identifier/intervention scope.

    The project already records post-registration changes as appended Markdown sections headed
    ``## Amendment YYYY-MM-DD``. This parser recognizes only the narrow identifier-scope form; absent
    or ambiguous prose returns no amendment, so the identifier gate keeps failing closed.
    """
    text = md_text or ""
    out = []
    matches = list(re.finditer(r"^## Amendment\s+(\d{4}-\d{2}-\d{2})([^\n]*)\n", text, re.M))
    for i, m in enumerate(matches):
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        folded = _fold_for_prose(m.group(2) + " " + body)
        if "identifier" not in folded or not any(w in folded for w in ("widened", "widen", "scope")):
            continue
        original = re.search(r"\*\*Original identifier scope\.\*\*\s*([^\n]+)", body, re.I)
        widened = re.search(r"\*\*Widened scope\.\*\*\s*([^\n]+)", body, re.I)
        reason = re.search(r"\*\*Reason\.\*\*\s*([^\n]+)", body, re.I)
        agents = re.search(r"\*\*Pre-specified list\.\*\*\s*([^\n]+)", body, re.I)
        out.append({
            "date": m.group(1),
            "kind": "identifier_scope",
            "heading": _norm_text(m.group(2).strip(" -\u2013\u2014")),
            "original_scope": _norm_text(original.group(1) if original else ""),
            "widened_scope": _norm_text(widened.group(1) if widened else ""),
            "reason": _norm_text(reason.group(1) if reason else ""),
            "pre_specified_list": _norm_text(agents.group(1) if agents else ""),
            "body": _norm_text(body),
        })
    return out


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
    if prose.get("estimand_preference") == "UNDECLARED":
        div.append({"code": "ESTIMAND_PREFERENCE_UNDECLARED",
                    "dimension": "estimand_preference",
                    "prose": "protocol permits crude count reconstruction and published time-to-event effects",
                    "config": "no explicit preference"})
    cp = ((config.get("primary_outcome") or {}).get("population") or "").lower()
    if prose["population"]:
        cpc = "intention-to-treat" if ("intention" in cp or "itt" in cp) else (
            "per-protocol" if "per-protocol" in cp or "per protocol" in cp else (cp or None))
        if cpc and cpc != prose["population"]:
            div.append({"code": "POPULATION_DIVERGENCE", "dimension": "analysis_set",
                        "prose": prose["population"], "config": cpc})
    # design masking AND/OR fidelity: the executable screen treats design_double_blind as
    # double-blind OR placebo-controlled. If the prose says AND, the config is wider.
    inc = config.get("include") or {}
    cfg_or = bool(inc.get("design_double_blind"))
    if prose["design_masking"] == "AND" and cfg_or:
        div.append({"code": "DESIGN_MASKING_ANDOR", "dimension": "design",
                    "prose": "double-blind AND placebo-controlled",
                    "config": "double-blind OR placebo-controlled"})
    include_text = _fold_for_prose(" ".join(inc.get("population_any") or []))
    md_folded = _fold_for_prose(md_text)
    if "broad cardiovascular outcome trial" in md_folded and "broad cardiovascular outcome" not in include_text:
        div.append({"code": "POPULATION_SCOPE_DIVERGENCE", "dimension": "population",
                    "prose": "broad cardiovascular outcome trials",
                    "config": ", ".join(inc.get("population_any") or [])})
    needs_ovulation_context = (
        "ovulation induction subfertility context" in md_folded
        or "undergoing ovulation induction" in md_folded
        or "subfertility context" in md_folded
    )
    if needs_ovulation_context and not any(x in include_text for x in ("ovulation", "subfertility")):
        div.append({"code": "POPULATION_CONTEXT_DIVERGENCE", "dimension": "population",
                    "prose": "PCOS in an ovulation-induction/subfertility context",
                    "config": ", ".join(inc.get("population_any") or [])})
    div.extend(_intervention_declaration_divergences(md_text, config))
    return div


def typed_criteria(md_text):
    """Return typed protocol criteria for consumers that need executable contracts."""
    from . import eligibility_chain
    return eligibility_chain.protocol_criteria(md_text)
