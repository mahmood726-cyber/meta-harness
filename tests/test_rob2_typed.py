"""Plants for the typed RoB 2 answers (robgrade/rob2_typed.py): registry fields and regex phrases answer only what they
state, every answer carries its verbatim span and the sha256 of its source, and contradicting typed sources answer
nothing (the question goes to the recorded dual reading)."""
from robgrade import rob2_typed as rt

DESIGNS = {"nct_id": "NCT0", "allocation": "RANDOMIZED", "masking": "DOUBLE", "subject_masked": "t",
           "caregiver_masked": "f", "outcomes_assessor_masked": "", "intervention_model": "PARALLEL"}


def _src(abstract=None, designs=None, fulltext=None, ft_open=False):
    s = []
    if abstract:
        s.append({"id": "abstract:PMID 1", "kind": "abstract", "text": abstract, "sha256": rt.sha(abstract),
                  "open_for_prompt": True})
    if fulltext:
        s.append({"id": "fulltext:PMID 1", "kind": "fulltext", "text": fulltext, "sha256": rt.sha(fulltext),
                  "open_for_prompt": ft_open})
    if designs:
        s.append({"id": "registry:NCT0:designs", "kind": "registry_row", "row": designs,
                  "text": "\n".join(f"{k}: {v}" for k, v in designs.items()), "sha256": rt.sha(rt.canonical_row(designs)),
                  "open_for_prompt": True})
    return s


def test_registry_randomized_and_masked_roles():
    a, c = rt.typed_answers(_src(designs=DESIGNS))
    assert a["1.1"]["answer"] == "PY" and a["1.1"]["span"] == "allocation: RANDOMIZED"
    assert a["2.1"]["answer"] == "N"                       # subject_masked t
    assert "2.2" not in a                                   # caregiver_masked f answers nothing (under-reporting)
    assert "4.3" not in a
    assert a["1.1"]["source_sha256"] == rt.sha(rt.canonical_row(DESIGNS))


def test_regex_method_beats_registry_randomized_and_spans_are_verbatim():
    text = ("Patients were randomly assigned in a 1:1 ratio. Randomisation used an interactive web response system "
            "with permuted blocks. Analyses were by intention to treat.")
    a, _ = rt.typed_answers(_src(abstract=text, designs=DESIGNS))
    assert a["1.1"]["answer"] == "Y" and a["1.1"]["span"] in text
    assert a["1.2"]["answer"] == "Y" and "interactive web response" in a["1.2"]["span"]
    # 'Analyses were by intention to treat' STATES the analysis: Y under regex:itt_stated_v2 (the v1 rule gave PY)
    assert a["2.6"]["answer"] == "Y" and a["2.6"]["rule_id"] == "regex:itt_stated_v2"
    for q in ("1.1", "1.2", "2.6"):
        assert a[q]["source_sha256"] == rt.sha(text)


def test_PLANT_contradicting_typed_sources_answer_nothing():
    # the registry says participants were masked; the report says open-label: no typed winner
    a, c = rt.typed_answers(_src(abstract="This open-label trial randomised 300 patients.", designs=DESIGNS))
    assert "2.1" not in a and [x["question"] for x in c] == ["2.1"]


def test_PLANT_open_label_is_never_read_as_blinded():
    text = "A prospective, randomized, open-label trial with blinded endpoint adjudication (PROBE design); not double-blind."
    a, _ = rt.typed_answers(_src(abstract=text))
    assert a["2.1"]["answer"] == "Y" and a["2.2"]["answer"] == "Y"


def test_PLANT_a_negated_phrase_answers_nothing():
    a, _ = rt.typed_answers(_src(abstract="The trial was not double-blind, and there was no intention-to-treat analysis."))
    assert "2.1" not in a and "2.6" not in a


def test_PLANT_ambiguous_unblinded_says_nothing_about_participants():
    a, _ = rt.typed_answers(_src(abstract="Outcome assessors were unblinded to allocation."))
    assert "2.1" not in a and "2.2" not in a


def test_PLANT_a_sentence_about_other_trials_answers_nothing():
    # CONFIRM-HF (PMID 25176939) introduction, verbatim shape: background about earlier trials, with citation markup
    bg = ('e="bibr">16</xref></sup> These trials, however, suffer from several drawbacks: the vast majority was '
          'single-centre studies with heterogeneous design (open-label vs. placebo-controlled, treating only patients '
          'with anaemia vs. all ID patients).')
    a, _ = rt.typed_answers(_src(fulltext=bg))
    assert "2.1" not in a and "2.2" not in a
    own = "This was a multicentre, double-blind, placebo-controlled study."
    a, _ = rt.typed_answers(_src(fulltext=bg + " " + own))
    assert a["2.1"]["answer"] == "PN" and a["2.1"]["span"] == own


def test_PLANT_silence_answers_nothing():
    a, c = rt.typed_answers(_src(abstract="We enrolled adults with heart failure and followed them for two years."))
    assert a == {} and c == []


def test_regex_may_read_a_non_open_full_text_and_says_so():
    a, _ = rt.typed_answers(_src(fulltext="Allocation was concealed using sequentially numbered, opaque, sealed envelopes.",
                                 ft_open=False))
    assert a["1.2"]["answer"] == "Y" and "D8 allows regex" in a["1.2"]["note"]


# ---------------------------------------------------------------------- extension (Mahmood 12 Oct, 'extend')

def test_extension_concealment_sequence_baseline_itt():
    t = ("Randomization was performed centrally by an independent statistician using computer-generated random numbers "
         "in blocks of four. Baseline characteristics were similar in the two groups. The analysis was performed "
         "according to the intention-to-treat principle.")
    a, _ = rt.typed_answers(_src(fulltext=t))
    assert a["1.1"]["answer"] == "Y" and a["1.2"]["answer"] == "Y"
    assert a["1.3"]["answer"] == "N" and a["2.6"]["answer"] == "Y"


def test_PLANT_extension_negations_and_imbalance_answer_nothing():
    t = ("Baseline characteristics were not similar between groups. Allocation was not concealed. "
         "No intention-to-treat analysis was performed.")
    a, _ = rt.typed_answers(_src(fulltext=t))
    assert "1.3" not in a and "1.2" not in a and "2.6" not in a


def test_attrition_thresholds_stated_and_applied():
    a, _ = rt.typed_answers(_src(fulltext="In total, 1.5% of participants were lost to follow-up."))
    assert a["3.1"]["answer"] == "Y" and "1.5%" in a["3.1"]["note"]
    a, _ = rt.typed_answers(_src(fulltext="Overall, 4% of patients were lost to follow-up."))
    assert a["3.1"]["answer"] == "PY"
    a, _ = rt.typed_answers(_src(fulltext="Overall, 12% of patients were lost to follow-up."))
    assert "3.1" not in a                                  # more loss: the reading decides, never a typed 'no'
    a, _ = rt.typed_answers(_src(fulltext="No patients were lost to follow-up."))
    assert a["3.1"]["answer"] == "Y"


def test_PLANT_assessor_blinding_both_directions():
    a, _ = rt.typed_answers(_src(fulltext="Outcome assessors were blinded to treatment allocation."))
    assert a["4.3"]["answer"] == "N"
    a, _ = rt.typed_answers(_src(fulltext="Outcome assessors were not blinded to group."))
    assert a["4.3"]["answer"] == "Y"


def test_sap_and_prespecified_primary():
    t = ("The statistical analysis plan was finalized before unblinding. The prespecified primary outcome was "
         "all-cause death.")
    a, _ = rt.typed_answers(_src(fulltext=t))
    assert a["5.1"]["answer"] == "Y" and a["5.2"]["answer"] == "PN"


def test_PLANT_all_cause_mortality_only_answers_measurement_for_all_cause():
    a, _ = rt.typed_answers([], outcome="Mortality")
    assert (a["4.1"]["answer"], a["4.2"]["answer"], a["4.4"]["answer"]) == ("N", "PN", "N")
    assert a["4.4"]["span"] == "Mortality" and a["4.4"]["source_sha256"] == rt.sha("Mortality")
    a, _ = rt.typed_answers([], outcome="Cardiovascular death")
    assert "4.4" not in a                                  # cause-specific death is adjudicated: not covered


def test_calibration_phrasings_12_oct():
    # synthetic sentences with the STRUCTURE found in the calibration full texts (no source text copied)
    t = ("The allocation sequence was produced by an external statistician and concealed from all investigators. "
         "All investigators, patients, outcome assessors and statisticians were blinded throughout. "
         "All analyses followed a pre-specified statistical analysis plan.")
    a, _ = rt.typed_answers(_src(fulltext=t))
    assert a["1.2"]["rule_id"] == "regex:allocation_concealment_v3"
    assert a["4.3"]["answer"] == "N" and a["4.3"]["rule_id"] == "regex:assessors_blinded_v2"
    assert a["5.1"]["answer"] == "PY" and a["5.3"]["answer"] == "PN"
    a, _ = rt.typed_answers(_src(fulltext="The trial protocol and the statistical analysis plan were published before the "
                                          "conclusion of enrollment."))
    assert a["5.1"]["answer"] == "Y" and a["5.3"]["answer"] == "PN"


def test_PLANT_fraction_attrition_and_list_negation():
    a, _ = rt.typed_answers(_src(fulltext="Overall 3/150 participants were lost to follow-up."))
    assert a["3.1"]["answer"] == "Y" and "2.0%" in a["3.1"]["note"]          # exactly at the 2% threshold
    a, _ = rt.typed_answers(_src(fulltext="Overall 4/150 participants were lost to follow-up."))
    assert a["3.1"]["answer"] == "PY"                                        # 2.67%
    a, _ = rt.typed_answers(_src(fulltext="Overall 22/135 patients were lost to follow-up."))
    assert "3.1" not in a                                                  # 16%: the reading decides
    a, _ = rt.typed_answers(_src(fulltext="Outcome assessors in this study were not blinded."))
    assert a.get("4.3", {}).get("answer") != "N"                           # never read as blinded


def test_machine_d5_identity_only_by_component_set_or_text():
    good = {"level": "low", "basis": "the pooled outcome matches the trial's pre-registered primary outcome by component set (X)"}
    weak = {"level": "low", "basis": "embedding match 0.52 to registered secondary outcome"}
    assert rt.typed_answers([], machine_d5=good)[0]["5.1"]["answer"] == "PY"
    assert "5.1" not in rt.typed_answers([], machine_d5=weak)[0]
