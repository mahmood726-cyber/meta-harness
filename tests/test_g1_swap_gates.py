"""Plants (codex binding-v8-fe3ed2a7, reproduced on the binding branch): the swap gates validated a pooled estimate /
bound by SUBSTRING ('0.8' inside '0.85'), never checked k against the quote (999 vs '12 trials'), and accepted an
all-whitespace quote (it folds to '', contained in every text)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_swap as sw  # noqa: E402

Q = "RR 0.85 (95% CI 0.70-1.03); 12 trials."


def _p(**kw):
    p = {"measure": "RR", "estimate": "0.85", "lower": "0.70", "upper": "1.03", "k": 12, "quote": Q}
    p.update(kw)
    return p


def test_a_substring_value_is_refused():
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p(estimate="0.8", upper="1.0")}, Q)
    assert pooled is None and k is None


def test_an_unprinted_k_is_refused():
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p(k=999)}, Q)
    assert pooled is None and k is None


def test_the_printed_claim_stands():
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p()}, Q)
    assert pooled is not None and k == 12


def test_a_whitespace_quote_supports_nothing():
    out, _, _ = sw.gate_screen({"criteria": {"C2": {"verdict": "PASS", "quote": "   "}}, "pooled": {}}, Q)
    assert out["C2"]["verdict"] == "UNCLEAR"


def test_codex_re_review_v8_p0_fixes():
    q = "RR .85 (95% CI .70-1.03); 12 trials."
    # g1#2: a fabricated '85' is not the printed .85
    _, pooled, _ = sw.gate_screen({"criteria": {}, "pooled": _p(estimate="85", lower="70", quote=q)}, q)
    assert pooled is None
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p(estimate="0.85", lower="0.70", quote=q)}, q)
    assert pooled is not None and k == 12
    # g1#3: a fractional k is refused, never truncated
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p(k="12.6")}, Q)
    assert pooled is None and k is None
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p(k="12")}, Q)
    assert k == 12 and isinstance(k, int)


def _xml(body):
    return (f"<article><p>{body}</p><ref id=\"r1\"><label>1</label><article-title>Alpha trial</article-title>"
            "<pub-id pub-id-type=\"pmid\">11111111</pub-id></ref><ref id=\"r2\"><label>2</label><article-title>Beta trial"
            "</article-title><pub-id pub-id-type=\"pmid\">22222222</pub-id></ref></article>")


def test_a_label_bound_to_another_reference_is_refused():
    # codex binding-v8-fe3ed2a7:g2#6: 'Alpha' cited as [1] was bound to reference 2's PMID
    xml = _xml("Included: Alpha [1]. Excluded: Beta [2].")
    units, refused, _, _ = sw.gate_enum({"trials": [{"label": "Alpha", "ref": "2", "row_quote": None}], "pooled": {},
                                         "set_quote": None}, {"text": sw.jats_text(xml), "xml": xml, "pmid": "33333333"})
    assert not units and refused[0]["why"].startswith("LABEL_CITES_ANOTHER_REFERENCE")
    units, refused, _, _ = sw.gate_enum({"trials": [{"label": "Alpha", "ref": "1", "row_quote": None}], "pooled": {},
                                         "set_quote": None}, {"text": sw.jats_text(xml), "xml": xml, "pmid": "33333333"})
    assert [u["pmid"] for u in units] == ["11111111"]


def test_an_xref_citation_is_read_through_the_reference_list():
    xml = _xml('Alpha et al. (2014) <xref ref-type="bibr" rid="r1">1</xref> and Beta <xref ref-type="bibr" rid="r2">2</xref>.')
    assert sw.label_cites("Alpha", xml, sw.jats_refs(xml)) == {"1"}
    assert sw.label_cites("Beta", xml, sw.jats_refs(xml)) == {"2"}


def test_one_unit_of_a_two_trial_analysis_is_not_complete():
    # codex binding-v8-fe3ed2a7:g2#7: enumeration was 'complete' whenever one unit passed and none was refused
    u1 = {"label": "Alpha", "pmid": "11111111"}
    u2 = {"label": "Beta", "pmid": "22222222"}
    assert sw.enumeration_state([u1], [], {"k": 2}) == "ENUMERATION_INCOMPLETE"
    assert sw.enumeration_state([u1, u2], [], {"k": 2}) == "ENUMERATED"
    assert sw.enumeration_state([u1, u2], [], {}) == "ENUMERATION_K_NOT_STATED"
    assert sw.enumeration_state([u1, u2], [{"why": "x"}], {"k": 2}) == "ENUMERATION_INCOMPLETE"
    assert sw.enumeration_state([], [], {"k": 2}) == "NOT_ENUMERATED"


def test_codex_v8_p1_fixes_round():
    # g1#1 / v8-round3 g1#1: '1.2 -3.4' is ambiguous (two values or a range): the token supports NEITHER sign
    assert sw._num_tokens("change 1.2 -3.4") == [1.2]
    assert sw._num_tokens("RR 0.85 (0.80-1.01)") == [0.85, 0.80, 1.01]          # glued dash: a range, unambiguous
    assert sw._num_tokens("difference: -1.7") == [-1.7]
    # g1#2: a label never matches inside another name
    xml = _xml("Kleen [2] and Lee [1].")
    assert sw.label_cites("Lee", xml, sw.jats_refs(xml)) == {"1"}
    # g1#3: a spaced citation range keeps its middle
    xml3 = _xml("Alpha [1 - 2].")
    assert sw.label_cites("Alpha", xml3, sw.jats_refs(xml3)) == {"1", "2"}


# ---- k from the meta's own SET QUOTE, digits or a number word (doac-vte 29795629, 7 Oct) ------------------------------
SET_Q = ("In the five Phase 3 studies of DOACs for acute treatment of patients with a DVT, participants randomized to "
         "receive a DOAC did not differ (OR 0.88, CI 0.75-1.03).")


def test_k_may_be_read_from_the_verbatim_set_quote_as_a_number_word():
    nt = sw._norm(SET_Q)
    pl = {"measure": "OR", "estimate": "0.88", "lower": "0.75", "upper": "1.03", "k": 5, "quote": "OR 0.88, CI 0.75-1.03"}
    got, k = sw.pooled_gate(pl, nt, set_quote=SET_Q, verified_units=5)
    assert got and k == 5
    assert sw.pooled_gate(pl, nt)[0] is None                      # without the set quote the k is not printed: refused
    assert sw.pooled_gate(pl, nt, set_quote=SET_Q)[0] is None     # set quote without verified units: refused (r12 #3)


def test_PLANT_a_phase_number_is_never_the_trial_count():
    nt = sw._norm(SET_Q)
    pl = {"measure": "OR", "estimate": "0.88", "lower": "0.75", "upper": "1.03", "k": 3, "quote": "OR 0.88, CI 0.75-1.03"}
    assert sw.pooled_gate(pl, nt, set_quote=SET_Q, verified_units=3)[0] is None  # 'Phase 3 studies' is not k = 3


def test_PLANT_a_set_quote_not_in_the_text_is_never_read():
    nt = sw._norm("OR 0.88, CI 0.75-1.03 in some trials.")
    pl = {"measure": "OR", "estimate": "0.88", "lower": "0.75", "upper": "1.03", "k": 5, "quote": "OR 0.88, CI 0.75-1.03"}
    assert sw.pooled_gate(pl, nt, set_quote="In the five studies we found OR 0.88, CI 0.75-1.03.")[0] is None


def test_PLANT_only_trial_adjectives_may_stand_between_the_count_and_trials():
    q = "Five large international multicentre studies reported OR 0.88, CI 0.75-1.03."
    nt = sw._norm(q)
    pl = {"measure": "OR", "estimate": "0.88", "lower": "0.75", "upper": "1.03", "k": 5, "quote": "OR 0.88, CI 0.75-1.03"}
    assert sw.pooled_gate(pl, nt, set_quote=q)[0] is None


def test_PLANT_compound_words_and_decimals_are_never_counts():
    """codex swap-setquote #1 ('Twenty-one' -> 1) and #2 ('11.6 Phase 3 studies' -> 6)."""
    assert 1 not in sw.printed_counts("Twenty-one randomized trials were pooled.")
    assert sw.printed_counts("Across reviews, the mean was 11.6 Phase 3 studies.") == set()
    assert sw.printed_counts("In the five Phase 3 studies") == {5}
    assert sw.printed_counts("12 randomised controlled trials") == {12}


def test_PLANT_larger_numbers_written_phases_and_identifiers_are_never_counts():
    """codex swap-setquote-r2 #1, #2, #3."""
    assert 20 not in sw.printed_counts("We included one hundred and twenty trials.")
    assert sw.printed_counts("We included Phase three studies.") == set()
    assert sw.printed_counts("We reviewed BRCA1 studies.") == set()
    assert sw.printed_counts("In the five Phase 3 studies") == {5}


def test_PLANT_unhyphenated_compounds_and_any_whitespace_before_a_phase_word():
    """codex swap-setquote-r3 #1 ('twenty five trials') and #2 ('Phase\nthree studies')."""
    assert sw.printed_counts("We included twenty five trials.") == set()
    assert sw.printed_counts("Phase\nthree studies") == set()
    assert sw.printed_counts("Phase   3 studies") == set()
    assert sw.printed_counts("In the five Phase 3 studies") == {5}
    assert sw.printed_counts("We pooled 12 randomised controlled trials.") == {12}


def test_PLANT_tens_compounds_refuse_and_a_plain_conjunction_does_not():
    """codex swap-setquote-r4 #1 ('thirty-five studies' -> not 5) and #2 ('cohorts and 5 randomized trials' -> 5)."""
    assert sw.printed_counts("We pooled thirty-five studies.") == set()
    assert sw.printed_counts("We pooled thirty five studies.") == set()
    assert sw.printed_counts("We included observational cohorts and 5 randomized trials.") == {5}
    assert sw.printed_counts("cohorts and five randomized trials") == {5}
    assert 20 not in sw.printed_counts("We included one hundred and twenty trials.")


def test_PLANT_spelled_decimals_refuse_and_punctuation_ends_a_phase():
    """codex swap-setquote-r5 #1 ('four point five studies') and #2 ('Phase 3: 5 randomized trials' -> 5)."""
    assert sw.printed_counts("The mean was four point five studies per review.") == set()
    assert sw.printed_counts("Phase 3: 5 randomized trials") == {5}
    assert sw.printed_counts("In the five Phase 3 studies") == {5}
    assert sw.printed_counts("Phase 3 studies") == set()


def test_PLANT_opening_brackets_and_unicode_hyphens_keep_the_guards():
    """codex swap-setquote-r6 #1 ('(Phase three studies)', '(twenty five trials)') and #2 ('twenty\u2011five trials')."""
    assert sw.printed_counts("(Phase three studies)") == set()
    assert sw.printed_counts("(twenty five trials)") == set()
    assert sw.printed_counts("twenty\u2011five trials") == set()
    assert sw.printed_counts("twenty\u2013five trials") == set()
    assert sw.printed_counts("Phase 3: 5 randomized trials") == {5}
    assert sw.printed_counts("In the five Phase 3 studies") == {5}


def test_PLANT_the_pooled_quotes_own_count_wins_and_slash_ranges_are_never_counts():
    """codex swap-setquote-r7 #1 (a review-wide set count overriding the pooled quote's own count) and #2 ('one/two')."""
    q = "Mortality was pooled across three trials: RR 0.80 (95% CI 0.70 to 0.90)."
    sq = "Ten randomized trials were included in this review."
    nt = sw._norm(q + " " + sq)
    pl = {"measure": "RR", "estimate": "0.80", "lower": "0.70", "upper": "0.90", "k": 10, "quote": q}
    assert sw.pooled_gate(pl, nt, set_quote=sq)[0] is None
    assert sw.pooled_gate(dict(pl, k=3), nt, set_quote=sq)[1] == 3
    assert sw.printed_counts("Phase one/two studies") == set()
    assert sw.printed_counts("Phase 1/2 studies") == set()


def test_PLANT_an_unparsed_pooled_count_closes_the_fallback_and_range_ends_are_not_counts():
    """codex swap-setquote-r8 #1 ('twenty-five trials' then a review-wide 40) and #2 ('two to five trials')."""
    q = "twenty-five trials contributed to the pooled mortality estimate: RR 0.80 (95% CI 0.70 to 0.90)."
    sq = "the review included 40 trials."
    nt = sw._norm(q + " " + sq)
    pl = {"measure": "RR", "estimate": "0.80", "lower": "0.70", "upper": "0.90", "k": 40, "quote": q}
    assert sw.pooled_gate(pl, nt, set_quote=sq)[0] is None
    assert sw.printed_counts("Mortality was reported in two to five trials per comparison.") == set()
    assert sw.printed_counts("in 3 or 4 studies") == set()
    assert sw.printed_counts("We included observational cohorts and 5 randomized trials.") == {5}


def test_PLANT_spaced_slash_ranges_and_far_counts_never_admit_the_set_quote():
    """codex swap-setquote-r9 #1 ('Phase one / two studies') and #2 (a count 60 characters before 'trials')."""
    assert sw.printed_counts("Phase one / two studies") == set()
    assert sw.printed_counts("Phase 1 / 2 studies") == set()
    q = "Mortality was pooled across 25 high-quality, multicentre, double-blind, placebo-controlled trials (RR 0.8)."
    sq = "We included 40 trials."
    assert sw.mentions_a_count(q)
    pl = {"measure": "RR", "estimate": "0.8", "k": 40, "quote": q}
    assert sw.pooled_gate(pl, sw._norm(sq + " " + q), set_quote=sq)[0] is None


def test_PLANT_the_set_quote_count_stands_only_in_the_sentence_that_prints_the_pooled_result():
    """codex swap-setquote-r10: '#1 'One in five trials' is a proportion; #2 'Both trials' beside a review-wide 40. The
    structural rule: the pooled quote must lie inside the set-quote sentence, which prints exactly one count."""
    assert sw.printed_counts("One in five trials reported mortality.") == set()
    assert sw.printed_counts("three of five studies") == set()
    q = "Both trials contributed to the mortality analysis (RR 0.80)."
    sq = "The review included 40 trials."
    assert sw.pooled_gate({"measure": "RR", "estimate": "0.80", "k": 40, "quote": q},
                          sw._norm(q + " " + sq), set_quote=sq)[0] is None
    # a pooled quote OUTSIDE the set-quote sentence never borrows its count, even a clean one
    q2 = "OR 0.88, CI 0.75 to 1.03"
    sq2 = "We included 5 randomized trials."
    assert sw.pooled_gate({"measure": "OR", "estimate": "0.88", "lower": "0.75", "upper": "1.03", "k": 5, "quote": q2},
                          sw._norm(sq2 + " Recurrence: " + q2 + "."), set_quote=sq2)[0] is None
    # the doac shape: the pooled result printed INSIDE the one-count sentence is admitted
    sq3 = "In the five Phase 3 studies, recurrent VTE tended to favour DOACs (OR 0.88, CI 0.75 to 1.03)."
    got = sw.pooled_gate({"measure": "OR", "estimate": "0.88", "lower": "0.75", "upper": "1.03", "k": 5, "quote": q2},
                         sw._norm(sq3), set_quote=sq3, verified_units=5)
    assert got[0] is not None and got[1] == 5
    # two counts in the set-quote sentence: ambiguous, refused
    sq4 = "In the five Phase 3 studies and 2 randomized trials, OR 0.88, CI 0.75 to 1.03."
    assert sw.pooled_gate({"measure": "OR", "estimate": "0.88", "lower": "0.75", "upper": "1.03", "k": 5, "quote": q2},
                          sw._norm(sq4), set_quote=sq4)[0] is None


def test_PLANT_counts_come_only_from_one_numeral_sentences_and_the_sentence_holding_the_pool():
    """codex swap-setquote-r11: #1 the count must sit in the SAME sentence as the pooled result; #2 'Two of the five
    trials'; #3 'At least five trials'. Plus the class: two quantities in one sentence refuse; symbol bounds refuse."""
    assert sw.printed_counts("Two of the five trials contributed to the mortality analysis (RR 0.8, 95% CI 0.7-0.9).") == set()
    assert sw.printed_counts("At least five trials contributed to the mortality analysis (RR 0.8, 95% CI 0.7-0.9).") == set()
    assert sw.printed_counts("More than 5 trials reported it.") == set()
    assert sw.printed_counts("Up to five trials reported it.") == set()
    assert sw.printed_counts("Data came from ~5 trials.") == set()
    assert sw.printed_counts("12 trials with 3,456 participants") == set()
    # one numeral per sentence, across two sentences: each is read on its own
    assert sw.printed_counts("Five trials were pooled. The RR was 0.8 (95% CI 0.7-0.9).") == {5}
    q = "The mortality RR was 0.8 (95% CI 0.7-0.9)."
    sq = "We included 40 trials. Ten contributed mortality data. The mortality RR was 0.8 (95% CI 0.7-0.9)."
    assert sw.pooled_gate({"measure": "RR", "estimate": "0.8", "lower": "0.7", "upper": "0.9", "k": 40, "quote": q},
                          sw._norm(sq), set_quote=sq)[0] is None


def test_PLANT_the_doac_shape_with_an_en_dash_still_finds_its_sentence():
    """The pooled quote and the set-quote sentence are cleaned alike: an en dash in both must still match."""
    q = "OR 0.88, CI 0.75\u20131.03"
    sq = "In the five Phase 3 studies, the outcome tended to favor DOACs (OR 0.88, CI 0.75\u20131.03)."
    got = sw.pooled_gate({"measure": "OR", "estimate": "0.88", "lower": "0.75", "upper": "1.03", "k": 5, "quote": q},
                         sw._norm(sq), set_quote=sq, verified_units=5)
    assert got[0] is not None and got[1] == 5


def test_PLANT_the_borrowed_count_must_equal_the_verified_units_and_r12_phrasings_refuse():
    """codex swap-setquote-r12: #1 '50% of ten trials'; #2 'Approximately (five trials)'; #3 a subset inside the one
    sentence ('Of the 40 trials, those reporting mortality ...'). The fallback now needs the enumeration's verified units."""
    assert sw.printed_counts("50% of ten trials contributed to the pooled mortality estimate (RR 0.85).") == set()
    assert sw.printed_counts("Approximately (five trials) contributed to the pooled estimate.") == set()
    q = "mortality (RR 0.85)"
    sq = "Across the 40 trials, those that reported mortality (RR 0.85) were few."
    pl = {"measure": "RR", "estimate": "0.85", "k": 40, "quote": q}
    assert sw.pooled_gate(pl, sw._norm(sq), set_quote=sq)[0] is None                    # no verified units: closed
    assert sw.pooled_gate(pl, sw._norm(sq), set_quote=sq, verified_units=6)[0] is None  # 40 != 6 verified units
    # the doac shape passes only when the verified units equal the printed count
    q2 = "OR 0.88, CI 0.75\u20131.03"
    sq2 = "In the five Phase 3 studies, the outcome tended to favor DOACs (OR 0.88, CI 0.75\u20131.03)."
    pl2 = {"measure": "OR", "estimate": "0.88", "lower": "0.75", "upper": "1.03", "k": 5, "quote": q2}
    assert sw.pooled_gate(pl2, sw._norm(sq2), set_quote=sq2, verified_units=5)[1] == 5
    assert sw.pooled_gate(pl2, sw._norm(sq2), set_quote=sq2, verified_units=4)[0] is None


def test_PLANT_symbol_bounds_zero_ranges_and_subset_sentences_refuse():
    """codex swap-setquote-r13: #1 '≥five trials'; #2 'Between zero and five trials'; #3 a subset restriction inside the
    one sentence, even with the verified units equal to the printed count."""
    assert sw.printed_counts("\u2265five trials contributed to mortality (RR 0.85).") == set()
    assert sw.printed_counts("\u2265 5 trials contributed to mortality (RR 0.85).") == set()
    assert sw.printed_counts("Between zero and five trials reported mortality (RR 0.85).") == set()
    sq = "Five trials were included, but only a subset reported mortality (RR 0.85)."
    pl = {"measure": "RR", "estimate": "0.85", "k": 5, "quote": "RR 0.85"}
    assert sw.pooled_gate(pl, sw._norm(sq), set_quote=sq, verified_units=5)[0] is None


def test_PLANT_a_retirement_names_only_the_criteria_the_old_comparator_FAILED():
    """doac R0: C1 FAIL, C2-C6 UNCLEAR (never read because C1 failed). The reason code must not claim six failures."""
    fails = [{"criterion": "C1_OPEN_LICENCE", "verdict": "FAIL", "evidence": "no CC BY"},
             {"criterion": "C2_RCT_ONLY", "verdict": "UNCLEAR", "evidence": "not read: C1 failed"}]
    code = sw.retirement_code(fails)
    assert code == "R0:C1_OPEN_LICENCE (not read after the failure: C2_RCT_ONLY)"
    assert sw.retirement_code([{"criterion": "C2_RCT_ONLY", "verdict": "UNCLEAR"}]) is None   # nothing failed: no retirement


def test_PLANT_r14_denominators_post_bounds_percent_sentences_and_the_k_basis_is_recorded():
    """codex swap-setquote-r14: #1 '50% of the ten trials'; #2 'Five trials at most'; #3 a percentage in the set-quote
    sentence. And a k borrowed from the set-quote sentence is never silent: it carries k_basis with the sentence."""
    assert sw.printed_counts("50% of the ten trials contributed to the mortality analysis (RR 0.85).") == set()
    assert sw.printed_counts("Five trials at most contributed to the pooled RR 0.85.") == set()
    assert sw.printed_counts("5 studies or more reported it.") == set()
    assert sw.printed_counts("Five trials contributed to the pooled RR 0.85.") == {5}
    q = "the pooled mortality estimate was RR 0.85 (95% CI 0.75-0.95)."
    sq = "Five trials were included, mortality was reported by 40%, and the pooled mortality estimate was RR 0.85 (95% CI 0.75-0.95)."
    pl = {"measure": "RR", "estimate": "0.85", "lower": "0.75", "upper": "0.95", "k": 5, "quote": q}
    assert sw.pooled_gate(pl, sw._norm(sq), set_quote=sq, verified_units=5)[0] is None
    q2 = "OR 0.88, CI 0.75\u20131.03"
    sq2 = "In the five Phase 3 studies, the outcome tended to favor DOACs (OR 0.88, CI 0.75\u20131.03)."
    pl2 = {"measure": "OR", "estimate": "0.88", "lower": "0.75", "upper": "1.03", "k": 5, "quote": q2}
    got, k = sw.pooled_gate(pl2, sw._norm(sq2), set_quote=sq2, verified_units=5)
    assert k == 5 and got["k_basis"]["from"] == "SET_QUOTE_SENTENCE" and "five Phase 3 studies" in got["k_basis"]["sentence"]
    assert "k_basis" not in pl2                                      # the caller's claim is not mutated
    # a k printed in the pooled quote itself carries no k_basis (nothing for the reviewer to re-read)
    q3 = "Five trials gave RR 0.85 (95% CI 0.75-0.95)."
    got3, _ = sw.pooled_gate({"measure": "RR", "estimate": "0.85", "k": 5, "quote": q3}, sw._norm(q3))
    assert got3 and "k_basis" not in got3


def test_PLANT_r15_subset_in_the_pooled_quote_bracketed_bounds_and_adjectival_denominators_refuse():
    """codex swap-setquote-r15: #1 a subset restriction in the pooled quote itself; #2 'Five trials (at most)';
    #3 '50% of the eligible ten trials'."""
    q = "Five trials were included, but only a subset reported mortality (RR 0.85, CI 0.75 to 0.95)."
    assert sw.printed_counts(q) == set()
    assert sw.pooled_gate({"measure": "RR", "estimate": "0.85", "lower": "0.75", "upper": "0.95", "k": 5, "quote": q},
                          sw._norm(q))[0] is None
    assert sw.printed_counts("Five trials (at most) contributed to the pooled mortality result (RR 0.85, CI 0.75 to 0.95).") == set()
    assert sw.printed_counts("Mortality was reported in 50% of the eligible ten trials (RR 0.85, CI 0.75 to 0.95).") == set()
    assert sw.printed_counts("Five trials contributed to the pooled mortality result (RR 0.85, CI 0.75 to 0.95).") == {5}


def test_PLANT_applied_enumeration_spans_are_in_k_gap_tables_rendering_of_the_held_source():
    """The swap reads table rows through its own JATS rendering (cells joined ' | '); k_gap_table.enumeration_units
    checks each span against held_norm (tags -> spaces) and refuses the WHOLE enumeration on one miss. doac 29795629
    was refused as NOT_ENUMERABLE that way. The applied span is the row with cells joined by single spaces: verbatim in
    held_norm, row identity kept."""
    import json
    import os
    import k_gap_table as kt
    e = json.load(open(os.path.join(sw.ROOT, "registry", "comparator_enumerations", "doac-vte-recurrence.swap.json"),
                       encoding="utf-8"))
    held = kt.held_norm(os.path.join(sw.ROOT, e["source"]["path"]))
    assert len(e["units"]) == 5
    for u in e["units"]:
        assert kt.held_norm(None, u["span"]) not in held                       # the swap's own rendering: not found
        assert kt.held_norm(None, sw.kgap_span(u["span"])) in held             # the applied rendering: found


def test_PLANT_r16_percent_fractions_at_the_most_and_excluded_trials_refuse_while_ci_levels_do_not():
    """codex swap-setquote-r16: #1 'Ten trials were included, and 40% reported mortality'; #2 'at the most';
    #3 'Five trials were excluded'. A CI level or an I-squared is not a fraction of the trials and keeps a clean count."""
    assert sw.printed_counts("Ten trials were included, and 40% reported mortality (RR 0.85, CI 0.70-1.03).") == set()
    assert sw.printed_counts("Five trials at the most contributed to the pooled RR 0.85 (CI 0.70-1.03).") == set()
    assert sw.printed_counts("Five trials were excluded from the mortality analysis (RR 0.85, CI 0.70-1.03).") == set()
    assert sw.printed_counts("Five trials gave RR 0.85 (95% CI 0.70-1.03; I2 = 0%).") == {5}
    assert sw.printed_counts("Five trials gave RR 0.85 (95% confidence interval 0.70-1.03).") == {5}


def test_PLANT_r17_estimated_counts_other_sentences_and_halves_never_supply_k():
    """codex swap-setquote-r17: #1 'An estimated five trials'; #2 a count in a sentence other than the one printing the
    pooled estimate; #3 'half reported mortality' in the set-quote sentence."""
    assert sw.printed_counts("An estimated five trials reported mortality (RR 0.85).") == set()
    q = "Six trials were included. Only three trials reported mortality (RR 0.85)."
    assert sw.pooled_gate({"measure": "RR", "estimate": "0.85", "k": 6, "quote": q}, sw._norm(q))[0] is None
    q2 = "Six trials were included. Mortality was lower (RR 0.85)."
    assert sw.pooled_gate({"measure": "RR", "estimate": "0.85", "k": 6, "quote": q2}, sw._norm(q2))[0] is None
    q3 = "Mortality was lower across six trials (RR 0.85)."
    assert sw.pooled_gate({"measure": "RR", "estimate": "0.85", "k": 6, "quote": q3}, sw._norm(q3))[1] == 6
    sq = "Six trials were included; half reported mortality (RR 0.85, CI 0.70 to 1.03)."
    pl = {"measure": "RR", "estimate": "0.85", "lower": "0.70", "upper": "1.03", "k": 6, "quote": "RR 0.85, CI 0.70 to 1.03"}
    assert sw.pooled_gate(pl, sw._norm(sq), set_quote=sq, verified_units=6)[0] is None


def test_PLANT_citation_markers_and_squared_statistics_are_not_numerals():
    """Part B replay regression: colchicine's 'the pooled results from the 3 RCTs ... (RR 0.48, 95 % CI 0.36-0.63,
    p < 0.0001, I 2 = 0 % [ 20 - 22 ]; interaction p = 0.56)' read as four numerals and was refused. The citation
    marker and the spaced I-squared are not quantities of trials; the count is still read only by the trial grammar."""
    q = ("the pooled results from the 3 RCTs enrolling patients with recurrent pericarditis (RR 0.48, 95\u00a0% CI "
         "0.36-0.63, p\u2009<\u20090.0001, I 2 \u2009=\u20090\u00a0% [ 20 \u2013 22 ]; interaction p\u2009=\u20090.56)")
    assert sw.printed_counts(q) == {3}
    assert sw.printed_counts("Five trials [12] and 3 cohorts gave RR 0.8.") == set()     # a real second quantity stays


def test_PLANT_r18_minimum_bounds_and_trials_lacking_the_outcome_never_supply_k():
    """codex swap-setquote-r18: #1 'At a minimum five trials'; #2 'Five trials lacked mortality data; the pooled ...'."""
    q = "At a minimum five trials yielded a pooled RR of 0.85."
    assert sw.pooled_gate({"measure": "RR", "estimate": "0.85", "k": 5, "quote": q}, sw._norm(q))[0] is None
    q2 = "Five trials lacked mortality data; the pooled mortality RR was 0.85 (95% CI 0.70-1.03)."
    assert sw.pooled_gate({"measure": "RR", "estimate": "0.85", "lower": "0.70", "upper": "1.03", "k": 5, "quote": q2},
                          sw._norm(q2))[0] is None
    assert sw.printed_counts("Mortality was not reported in five trials (RR 0.85).") == set()


def test_PLANT_r19_the_count_sentence_prints_the_whole_result_no_outcome_data_and_punctuated_approximators():
    """codex swap-setquote-r19: #1 the estimate's value appearing as another outcome's CI bound; #2 'had no mortality
    data'; #3 'Approximately: five trials'."""
    q = "Five trials reported recurrence (RR 0.70, 95% CI 0.50-0.85). Mortality RR 0.85 (95% CI 0.70-1.03)."
    assert sw.pooled_gate({"measure": "RR", "estimate": "0.85", "lower": "0.70", "upper": "1.03", "k": 5, "quote": q},
                          sw._norm(q))[0] is None
    q2 = "Five trials had no mortality data; pooled mortality RR 0.85 (95% CI 0.70-1.03)."
    assert sw.pooled_gate({"measure": "RR", "estimate": "0.85", "lower": "0.70", "upper": "1.03", "k": 5, "quote": q2},
                          sw._norm(q2))[0] is None
    q3 = "Approximately: five trials contributed to mortality (RR 0.85)."
    assert sw.pooled_gate({"measure": "RR", "estimate": "0.85", "k": 5, "quote": q3}, sw._norm(q3))[0] is None
    assert sw.printed_counts("Phase 3: 5 randomized trials gave RR 0.85.") == {5}


def test_PLANT_r20_singular_quantities_and_bracketed_symbol_bounds_refuse():
    """codex swap-setquote-r20: #1 'Five trials reported recurrence; mortality was reported by a single trial (...)';
    #2 'pooled from ≥(five trials)'."""
    q = "Five trials reported recurrence; mortality was reported by a single trial (RR 0.85, 95% CI 0.70-1.03)."
    pl = {"measure": "RR", "estimate": "0.85", "lower": "0.70", "upper": "1.03", "k": 5, "quote": q}
    assert sw.printed_counts(q) == set() and sw.pooled_gate(pl, sw._norm(q))[0] is None
    q2 = "Mortality was pooled from \u2265(five trials) (RR 0.85, 95% CI 0.70-1.03)."
    pl2 = dict(pl, quote=q2)
    assert sw.printed_counts(q2) == set() and sw.pooled_gate(pl2, sw._norm(q2))[0] is None
    assert sw.printed_counts("Five trials and a randomized trial gave RR 0.85.") == set()


def test_PLANT_r21_at_a_minimum_all_cause_and_two_sentences_printing_the_same_result():
    """codex swap-setquote-r21: #1 'Five trials at a minimum'; #2 'all-cause' is not a quantity (a false refusal);
    #3 two sentences printing identical numbers for different outcomes are ambiguous, never unioned."""
    base = {"measure": "RR", "estimate": "0.85", "lower": "0.70", "upper": "1.03"}
    q = "Five trials at a minimum reported mortality (RR 0.85, 95% CI 0.70-1.03)."
    assert sw.pooled_gate(dict(base, k=5, quote=q), sw._norm(q))[0] is None
    q2 = "5 trials reported all-cause mortality (RR 0.85, 95% CI 0.70-1.03)."
    assert sw.pooled_gate(dict(base, k=5, quote=q2), sw._norm(q2))[1] == 5
    q3 = ("Five trials reported recurrence (RR 0.85, 95% CI 0.70-1.03). "
          "Ten trials reported mortality (RR 0.85, 95% CI 0.70-1.03).")
    assert sw.pooled_gate(dict(base, k=5, quote=q3), sw._norm(q3))[0] is None
    assert sw.pooled_gate(dict(base, k=10, quote=q3), sw._norm(q3))[0] is None


def test_PLANT_r22_k_equals_with_a_bound_and_most_reporting_refuse_but_doacs_other_studies_do_not():
    """codex swap-setquote-r22: #1 'k = 5 or more' through the set-quote fallback; #2 'most reported' a share of these
    trials. doac 29795629's 'in most studies of secondary prevention' refers to OTHER studies and still admits."""
    q = "RR 0.85 (CI 0.70-1.03)."
    pl = {"quote": q, "measure": "RR", "estimate": "0.85", "lower": "0.70", "upper": "1.03", "k": 5}
    sq = "Mortality: k = 5 or more; " + q
    assert sw.pooled_gate(pl, sw._norm(sq), set_quote=sq, verified_units=5)[0] is None
    q2 = "mortality RR 0.85 (CI 0.70-1.03)."
    sq2 = "Five trials were included; most reported " + q2
    assert sw.pooled_gate(dict(pl, quote=q2), sw._norm(sq2), set_quote=sq2, verified_units=5)[0] is None
    assert sw.printed_counts("k = 5 (RR 0.85).") == {5}
    sq3 = ("In the five Phase 3 studies, the primary outcome in most studies of secondary prevention tended to favor "
           "DOACs (OR 0.88, CI 0.75-1.03).")
    pl3 = {"quote": "OR 0.88, CI 0.75-1.03", "measure": "OR", "estimate": "0.88", "lower": "0.75", "upper": "1.03", "k": 5}
    assert sw.pooled_gate(pl3, sw._norm(sq3), set_quote=sq3, verified_units=5)[1] == 5


def test_PLANT_r23_trailing_approximation_counts_in_another_clause_and_ci_levels_in_the_fallback():
    """codex swap-setquote-r23: #1 'five trials, approximately'; #2 a count in a ';'-clause about another outcome;
    #3 a '95% CI' must not close the set-quote fallback (a false refusal)."""
    base = {"measure": "RR", "estimate": "0.85", "lower": "0.70", "upper": "1.03"}
    q = "The mortality analysis used five trials, approximately (RR 0.85, 95% CI 0.70-1.03)."
    assert sw.printed_counts(q) == set() and sw.pooled_gate(dict(base, k=5, quote=q), sw._norm(q))[0] is None
    q2 = "Five trials reported recurrence; mortality RR 0.85 (95% CI 0.70-1.03)."
    assert sw.pooled_gate(dict(base, k=5, quote=q2), sw._norm(q2))[0] is None
    q3 = "RR 0.85 (95% CI 0.70-1.03); 12 trials."                      # a bare count clause still binds
    assert sw.pooled_gate(dict(base, k=12, quote=q3), sw._norm(q3))[1] == 12
    sq = "Five trials reported mortality RR 0.85 (95% CI 0.70-1.03)."
    q4 = "mortality RR 0.85 (95% CI 0.70-1.03)."
    got, k = sw.pooled_gate(dict(base, k=5, quote=q4), sw._norm(sq), set_quote=sq, verified_units=5)
    assert k == 5 and got["k_basis"]["from"] == "SET_QUOTE_SENTENCE"


def test_PLANT_r24_k_equals_after_an_approximator_and_scientific_notation_refuse():
    """codex swap-setquote-r24 #2 'approximately k = 5'; #3 'k = 5e1'. (#1, a count in another comma-clause of the same
    sentence, is the disclosed semantic residue: a clause rule would also refuse doac 29795629's own sentence.)"""
    vals = [0.85, 0.70, 1.03]
    assert sw._bound_counts("Mortality RR 0.85 (95% CI 0.70-1.03), approximately k = 5.", vals) == set()
    assert sw._bound_counts("Mortality RR 0.85 (95% CI 0.70-1.03), k = 5e1.", vals) == set()
    assert sw._bound_counts("Mortality RR 0.85 (95% CI 0.70-1.03), k = 5.", vals) == {5}


def test_PLANT_r25_a_k_regex_never_backtracks_into_a_decimal():
    """codex swap-setquote-r25 #1: 'k = 12.5' read as k = 1 because the regex backtracked inside the decimal."""
    q = "Mortality RR 1 (95% CI 0.8-1.2), k = 12.5."
    assert sw.printed_counts(q) == set()
    assert sw.pooled_gate({"quote": q, "measure": "RR", "estimate": "1", "lower": "0.8", "upper": "1.2", "k": 1},
                          sw._norm(q))[0] is None


def test_PLANT_r26_an_abbreviation_never_detaches_its_approximator():
    """codex swap-setquote-r26 #1: 'Approx. 5 trials' was split after 'Approx.' and the 5 read as exact."""
    assert sw.printed_counts("Approx. 5 trials reported mortality RR 0.85 (95% CI 0.70-1.03).") == set()
    assert sw.printed_counts("Ca. 5 trials reported mortality RR 0.85.") == set()
    assert len(sw._sentences("See Fig. 2 for the forest plot. Five trials were pooled.")) == 2


def test_PLANT_r27_contrasts_second_estimates_trial_noun_bounds_and_article_approximators():
    """codex swap-setquote-r27: #1 (and r24-r26 #1) a contrast between outcomes in one sentence, or a second effect
    estimate; #2 'k = 5 trials or more'; #3 'At least the five trials'."""
    vals = [0.85, 0.70, 1.03]
    assert sw._bound_counts("Five trials reported recurrence (RR 0.75), whereas mortality RR 0.85 (95% CI 0.70-1.03) "
                            "was pooled separately.", vals) == set()
    assert sw._bound_counts("Five trials reported recurrence, whereas mortality RR 0.85 (95% CI 0.70-1.03).", vals) == set()
    assert sw._bound_counts("Five trials gave recurrence RR 0.75 and mortality RR 0.85 (95% CI 0.70-1.03).", vals) == set()
    assert sw._bound_counts("Mortality RR 0.85 (95% CI 0.70-1.03), k = 5 trials or more.", vals) == set()
    assert sw._bound_counts("At least the five trials contributed to mortality RR 0.85 (95% CI 0.70-1.03).", vals) == set()
    assert sw._bound_counts("The five trials contributed to mortality RR 0.85 (95% CI 0.70-1.03).", vals) == {5}


def test_PLANT_r28_a_different_trial_fraction_k_and_dash_bounds_refuse():
    """codex swap-setquote-r28: #1 'but a different trial reported mortality'; #2 'k = 5/6'; #3 'Five trials—at least—'."""
    assert sw._bound_counts("Five trials reported recurrence, but a different trial reported mortality (RR 0.85).",
                            [0.85]) == set()
    assert sw.printed_counts("Mortality RR 0.85 (k = 5/6).") == set()
    assert sw.printed_counts("Five trials\u2014at least\u2014reported mortality (RR 0.85).") == set()
