"""Every screening decision carries a VERBATIM span -- a real substring of the record's own text
evidencing the rule (checkable against source, never a paraphrase)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.screen import screen_record, _span, run  # noqa: E402

INC = {"population_any": ["cardiovascular", "myocardial"], "population_none": ["depression"],
       "intervention_any": ["omega-3", "fish oil"], "intervention_in_title": True,
       "comparator_any": ["placebo"], "design_double_blind": True}


def _rct(**kw):
    base = {"id": "1", "id_type": "pmid", "pubtypes": ["Randomized Controlled Trial"],
            "title": "", "abstract": "", "conditions": [], "interventions": [], "masking": ""}
    base.update(kw)
    return base


def test_span_is_a_real_substring():
    raw = "Effect of Fish Oil on Major Adverse Cardiovascular Events in Patients"
    s = _span(raw, "cardiovascular")
    core = s.strip("…")
    assert core.lower() in raw.lower()  # verbatim, case-insensitive
    assert "cardiovascular" in core.lower()


def test_x1_span_quotes_pubtypes():
    dec, rule, reason, span = screen_record(_rct(pubtypes=["Journal Article", "Review"],
                                                 title="A review of omega-3"), INC, set())
    assert rule == "X1"
    assert "Journal Article" in span and "Review" in span  # the actual publication types


def test_x2_wrong_pop_span_quotes_the_matched_term():
    dec, rule, reason, span = screen_record(
        _rct(title="Fish oil for depression in adults"), INC, set())
    assert rule == "X2"
    assert "depression" in span.lower()  # the offending word, verbatim from the title


def test_xdesign_span_names_absent_blinding():
    # Mirrors GISSI-P: an open-label trial with a non-placebo 'control' comparator and no blinding.
    inc = dict(INC, comparator_any=["placebo", "control"])
    dec, rule, reason, span = screen_record(
        _rct(title="Fish oil vs control for cardiovascular events",
             abstract="open-label study of myocardial infarction survivors", masking="NONE"), inc, set())
    assert rule == "X-DESIGN"
    assert "NONE" in span  # verbatim registry masking value


def test_include_span_quotes_population_and_comparator():
    dec, rule, reason, span = screen_record(
        _rct(title="Fish oil vs placebo for cardiovascular events",
             abstract="double-blind placebo-controlled trial of myocardial infarction"), INC, set())
    assert rule == "INCLUDE"
    assert "cardiovascular" in span.lower() or "placebo" in span.lower()


def test_run_attaches_span_to_every_decision():
    recs = [_rct(title="Fish oil vs placebo for cardiovascular events",
                 abstract="double-blind"), _rct(title="Trial in depression")]
    out = run(recs, {"include": INC})
    assert all("span" in d for d in out["decisions"])
    assert all(isinstance(d["span"], str) for d in out["decisions"])


# --- eligibility generated from the include object (no drift) ---------------------
from harness.screen import describe_eligibility  # noqa: E402


def test_describe_eligibility_reflects_include_faithfully():
    d = describe_eligibility(INC)
    assert "randomised controlled trial" in d
    assert "cardiovascular" in d and "myocardial" in d  # population_any
    assert "depression" in d  # population_none
    assert "omega-3" in d  # intervention_any
    assert "placebo" in d  # comparator_any
    assert "double-blind" in d  # design_double_blind => X-DESIGN clause present
    assert "X-DESIGN" in d


def test_describe_eligibility_omits_xdesign_when_not_required():
    inc = {k: v for k, v in INC.items() if k != "design_double_blind"}
    d = describe_eligibility(inc)
    assert "X-DESIGN" not in d
    assert "double-blind" not in d  # no double-blind clause when the config does not require it


# --- token-boundary matching (external-audit regression) --------------------------
from harness.screen import _has  # noqa: E402


def test_has_does_not_match_substring_inside_a_word():
    # The bug an external audit found: 'rat' (an animal population_none term) matched inside
    # 'prepaRATion' / 'administRATion' / 'RATional', excluding human RCTs as animal studies.
    assert _has("probiotic Lactobacillus preparation to prevent diarrhoea", ["rat"]) is None
    assert _has("oral administration of Lactobacillus GG", ["rat"]) is None
    assert _has("a rational dosing approach", ["rat"]) is None
    assert _has("statistical modelling of outcomes", ["model"]) is None
    # but a real whole-word mention still matches
    assert _has("study in rats and mice", ["rat", "rats"]) is not None
    assert _has("a mouse model of colitis", ["model"]) == "model"


def test_include_reason_names_the_actual_matched_intervention_not_the_first_config_term():
    # External audit (DPP-4): the INCLUDE reason hard-coded intervention_any[0], so an alogliptin
    # trial read 'RCT of sitagliptin'. The reason must name the intervention THIS record matched.
    inc = {"population_any": ["type 2 diabetes"], "intervention_any": ["sitagliptin", "alogliptin"],
           "intervention_in_title": True, "comparator_any": ["placebo"], "design_double_blind": True}
    dec, rule, reason, span = screen_record(
        _rct(title="Alogliptin after acute coronary syndrome in type 2 diabetes",
             abstract="double-blind, placebo-controlled trial"), inc, set())
    assert rule == "INCLUDE"
    assert "alogliptin" in reason and "sitagliptin" not in reason


def test_include_reason_design_clause_reflects_requirement():
    # A topic that does NOT require double-blinding (e.g. prone positioning) must not have the reason
    # claim 'double-blind placebo-controlled' — that is false for a non-blindable intervention.
    inc = {"population_any": ["acute respiratory distress"], "intervention_any": ["prone position"],
           "intervention_in_title": True, "comparator_any": ["supine"]}
    dec, rule, reason, span = screen_record(
        _rct(title="Prone position vs supine in acute respiratory distress syndrome",
             abstract="randomised trial"), inc, set())
    assert rule == "INCLUDE"
    assert "double-blind" not in reason and "placebo-controlled" not in reason
    assert "randomised controlled trial" in reason


def test_has_stem_star_matches_word_continuations():
    # An explicit trailing '*' marks an intended stem: 'diarr*' matches diarrhoea/diarrhea,
    # while a bare term stays whole-word.
    assert _has("antibiotic-associated diarrhoea in children", ["antibiotic-associated diarr*"])
    assert _has("antibiotic associated diarrhea", ["antibiotic associated diarr*"])
    assert _has("colds were shorter", ["cold*"]) == "cold*"
    # a stem still respects the LEADING boundary (no infix match)
    assert _has("the microbial preparation", ["rat*"]) is None
