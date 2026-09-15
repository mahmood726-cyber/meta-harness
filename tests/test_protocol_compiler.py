"""Protocol compiler: prose protocol vs executable config, compared as two INDEPENDENT sources.
A divergence on estimand / analysis set / design masking must be caught; agreement is clean."""
import harness.protocol_compiler as PC


def test_estimand_divergence_caught():
    md = "## Estimand\n- **Estimand** - risk ratio (RR), drug vs placebo."
    cfg = {"primary_outcome": {"estimand": "HR"}}
    div = PC.compare("x", md, cfg)
    assert any(d["code"] == "ESTIMAND_DIVERGENCE" and d["prose"] == "RR" and d["config"] == "HR" for d in div)


def test_estimand_agreement_clean():
    md = "- **Estimand** - hazard ratio (HR), drug vs placebo."
    cfg = {"primary_outcome": {"estimand": "HR"}}
    assert [d for d in PC.compare("x", md, cfg) if d["code"] == "ESTIMAND_DIVERGENCE"] == []


def test_design_masking_and_or_divergence():
    md = "The trial is double-blind or placebo-controlled."
    cfg = {"primary_outcome": {"estimand": "RR"},
           "include": {"design_double_blind": True, "comparator_any": ["placebo"]}}
    div = PC.compare("x", md, cfg)
    assert any(d["code"] == "DESIGN_MASKING_ANDOR" for d in div)


def test_population_divergence():
    md = "- **Population** - per-protocol completers."
    cfg = {"primary_outcome": {"estimand": "RR", "population": "intention-to-treat"}}
    div = PC.compare("x", md, cfg)
    assert any(d["code"] == "POPULATION_DIVERGENCE" for d in div)


def test_missing_prose_field_is_not_a_false_match():
    md = "# Protocol with no estimand or population line"
    cfg = {"primary_outcome": {"estimand": "HR", "population": "intention-to-treat"}}
    assert PC.compare("x", md, cfg) == []


def test_intervention_declaration_requires_every_existing_term_once():
    md = "## PICO\n- **I** - spironolactone or eplerenone."
    cfg = {
        "intervention_terms": ["spironolactone", "eplerenone", "MRA"],
        "intervention_agents": {
            "spironolactone": ["spironolactone"],
            "eplerenone": ["eplerenone"],
        },
        "intervention_class_terms": [],
    }
    div = PC.compare("x", md, cfg)
    assert any(d["code"] == "INTERVENTION_TERM_UNDECLARED" and d["config"] == "MRA" for d in div)


def test_intervention_agent_must_appear_in_protocol_i_line():
    md = "## PICO\n- **I** - mineralocorticoid receptor antagonist therapy."
    cfg = {
        "intervention_terms": ["spironolactone"],
        "intervention_agents": {"spironolactone": ["spironolactone"]},
        "intervention_class_terms": [],
    }
    div = PC.compare("x", md, cfg)
    assert any(d["code"] == "INTERVENTION_AGENT_PROSE_DIVERGENCE" for d in div)


def test_intervention_line_collects_wrapped_i_line():
    md = "## PICO\n- **I** - SGLT2 inhibitors, including empagliflozin,\n  canagliflozin, or dapagliflozin.\n- **C** - placebo."
    assert PC.intervention_line(md) == "sglt2 inhibitors, including empagliflozin, canagliflozin, or dapagliflozin."
