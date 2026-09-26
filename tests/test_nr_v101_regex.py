"""Lane NR V1.0.1 regex fixes, from an external review of colchicine-postop-af. Each test states the REQUIREMENT.

(1) COCS (PMID 36286314): '21 (18.6%) ... vs. 39 (30.7%)' with the arm sizes stated in another sentence as
    '113 in the colchicine group and 127 in the placebo group'. 21/113 = 18.58% and 39/127 = 30.71%, so the percentages
    corroborate and the counts must be extracted. A percentage that does NOT corroborate its own arm's size must
    still be refused, and the size phrase must not bind an EVENT sentence ('... occurred in 25 in the colchicine group').
    Admissibility (267 randomised, 240 analysed) is RoB's question, not the extractor's.
(2) Farzaneh (PMID 42132185): '... maintenance dose (0.5 mg daily if <70 kg; 1 mg daily if >=70 kg) for 14 days' is a
    TREATMENT duration. It is not evidence of the outcome-ascertainment window, so no reader may bind it as follow-up;
    with nothing else stating the window the value is not_stated (UNKNOWN/unresolved), never '14 days'.
"""
from __future__ import annotations

from harness import compat_check, eligibility_chain, extract

COCS = ("This double-blind randomized placebo-controlled trial included 267 patients, but 27 of them dropped out in "
        "the course of the study. Study subjects received the test drug on the day before the surgery and on "
        "postoperative days 2, 3, 4 and 5. The rhythm control was conducted immediately after the operation and until "
        "the discharge from the hospital. The final analysis included 240 study subjects: 113 in the colchicine group "
        "and 127 in the placebo group. POAF was observed in 21 (18.6%) patients of the colchicine group vs. 39 (30.7%) "
        "control patients (OR 0.515; 95% Cl 0.281-0.943; p = 0.029).")
POAF = ["atrial fibrillation", "poaf", "postoperative af", "primary outcome", "primary end point", "primary endpoint"]
INTERV = ["colchicine"]
COMP = ["placebo", "control", "usual care", "no colchicine", "no-colchicine"]

FARZANEH = ("METHODS: In this randomized, double-blind, placebo-controlled trial, 172 adults scheduled for on-pump CABG "
            "received colchicine or placebo. The regimen included a preoperative loading dose (1 mg twice daily) "
            "followed by a weight-based maintenance dose (0.5 mg daily if <70 kg; 1 mg daily if ≥70 kg) for 14 "
            "days. The primary outcome was incidence of postoperative atrial fibrillation (POAF).")


def _x(text):
    return extract.extract_trial(text, POAF, INTERV, COMP, declared_composite=False, estimand="RR")


# ---- (1) percentage corroboration ---------------------------------------------------------------------------------
def test_cocs_genuine_corroboration_is_extracted():
    ex = _x(COCS)
    assert not ex.get("absent"), ex
    assert (ex["ai"], ex["n1i"], ex["ci"], ex["n2i"]) == (21, 113, 39, 127)


def test_arm_sizes_stated_as_n_in_the_arm_group_in_a_population_sentence():
    assert extract._arm_ns(COCS, INTERV, COMP) == {"i": 113, "c": 127}


def test_a_percentage_that_does_not_corroborate_is_still_refused():
    assert _x(COCS.replace("21 (18.6%)", "21 (28.6%)")).get("absent")      # 21/113 is 18.6%, not 28.6%


def test_swapped_arm_sizes_do_not_corroborate():
    swapped = COCS.replace("113 in the colchicine group and 127 in the placebo group",
                           "127 in the colchicine group and 113 in the placebo group")
    assert _x(swapped).get("absent")                                         # 21/127 = 16.5% != 18.6%


def test_the_size_phrase_does_not_bind_an_event_sentence():
    ev = ("Adverse events occurred in 25 in the colchicine group and 11 in the placebo group. "
          "POAF was observed in 21 (18.6%) patients of the colchicine group vs. 39 (30.7%) control patients.")
    assert extract._arm_ns(ev, INTERV, COMP) == {}
    assert _x(ev).get("absent")


# ---- (2) follow-up window vs treatment duration --------------------------------------------------------------------
def test_dosing_duration_is_not_follow_up_evidence():
    from harness import window_evidence
    i = FARZANEH.index("14 days")
    assert window_evidence.duration_role(FARZANEH, i, i + len("14 days")) == "DOSING"
    assert not window_evidence.is_follow_up_evidence("maintenance dose ... for 14 days")
    assert not window_evidence.is_follow_up_evidence("14-day regimen / analysed population")


def test_ascertainment_windows_still_pass():
    from harness import window_evidence
    for s in ("during 14 days of follow-up", "The co-primary outcomes were AF and MINS during the 14-day follow-up.",
              "until the discharge from the hospital", "within 3 months / 1- and 3-month visits", "at 1 month",
              "chest CT within 14 days after surgery", "median follow-up of 2.3 years"):
        assert window_evidence.is_follow_up_evidence(s), s


def test_compat_follow_up_does_not_bind_a_dosing_sentence():
    fu = compat_check._derive_follow_up({"name": "Postoperative atrial fibrillation"}, {"source": FARZANEH}, None, None)
    assert fu["value"] != "14 days", fu
    assert fu["value"] is None and fu["source"] == "underivable"


def test_compat_follow_up_keeps_a_genuine_14_day_window():
    txt = "The coprimary outcomes were clinically important perioperative atrial fibrillation and MINS during 14 days of follow-up."
    assert compat_check._derive_follow_up({"name": "x"}, {"source": txt}, None, None)["value"] == "14 days"


def test_compat_follow_up_skips_a_dosing_match_and_takes_a_later_window():
    txt = FARZANEH + " Patients were followed for 14 days after surgery."
    fu = compat_check._derive_follow_up({"name": "x"}, {"source": txt}, None, None)
    assert fu["value"] == "14 days" and "after surgery" in fu["span"]


def test_admission_follow_up_for_farzaneh_is_not_stated():
    v, s = eligibility_chain._follow_up_value("42132185", FARZANEH)
    assert (v, s) == ("not_stated", "")


def test_admission_generic_reader_skips_dosing():
    assert eligibility_chain._follow_up_value("999", "Colchicine 0.5 mg twice daily for 14 days.")[0] == "not_stated"
    assert eligibility_chain._follow_up_value("999", "AF was assessed at 14 days after surgery.")[0] == "14 days"


def test_admission_endpoint_surveillance_window_is_not_a_regimen():
    assert eligibility_chain._endpoint_definition("42132185", FARZANEH)["surveillance_window"] == "not_stated"


def test_admission_verdict_is_unknown_when_the_window_is_unresolved():
    contract = {"criteria": {"follow_up_window": {"value": "in-hospital / index admission"}}, "config_rules": {}}
    cell = eligibility_chain.admission_record({"id": "42132185", "source": FARZANEH},
                                              {"id": "42132185", "abstract": FARZANEH},
                                              {"name": "Postoperative atrial fibrillation"}, contract)["follow_up_window"]
    assert cell["trial_value"] == "not_stated" and cell["verdict"] == "UNKNOWN" and cell["finding_code"] == "COMPAT_UNKNOWN"


def test_a_match_that_begins_a_sentence_does_not_inherit_the_previous_sentence():
    from harness import window_evidence
    t = "Colchicine 0.5 mg daily was given. 3 months later the rhythm was recorded."
    i = t.index("3 months")
    assert window_evidence.duration_role(t, i, i + len("3 months")) != "DOSING"
    txt = ("The primary outcome was treatment failure (early; late; or both early and late treatment failure). "
           "In-hospital mortality was a secondary outcome and adverse events were assessed.")
    assert eligibility_chain._follow_up_value("999", txt)[0] == "in-hospital"   # 'in-hospital' is not a duration
