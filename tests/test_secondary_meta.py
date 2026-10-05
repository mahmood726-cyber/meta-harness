"""Secondary-source tier (harness/secondary_meta.py): one plant per rule. Each builds the shape the rule exists for."""
import hashlib
import os
import sys

# scripts/ on the path for the tests that import secondary_meta_build: without it they passed only when another test file
# had added it first (consolidation 2026-10-05: test_a_forest_reads_measure_wording_is_normalised_typed failed alone)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from harness import secondary_meta as sm  # noqa: E402

D = hashlib.sha256(b"meta table bytes").hexdigest()


def _row(meta="111", label="LEADER", eff=("0.87", "0.78", "0.97"), measure="HR", outcome="3-point MACE", **kw):
    r = sm.SecondaryRow(meta_pmid=meta, meta_doi="", location={"kind": "figure", "id": "Fig3", "row_label": label},
                        source_digest=D, provenance="TYPED_TABLE", trial_label=label, measure=measure,
                        outcome_definition=outcome, effect=eff[0], lower=eff[1], upper=eff[2])
    for k, v in kw.items():
        setattr(r, k, v)
    return r


SPEC = {"estimand": "HR", "keywords": ["MACE", "major adverse cardiovascular"], "components": ["nonfatal myocardial infarction"]}


def test_g1_anti_circularity_a_row_from_meta_x_never_counts_for_meta_x():
    x = _row(meta="111", state=sm.VERIFIED, family_id="LEADER")
    y = _row(meta="222", label="SUSTAIN-6", eff=("0.74", "0.58", "0.95"), state=sm.VERIFIED, family_id="SUSTAIN-6")
    u = _row(meta="222", label="EXSCEL", state=sm.UNVERIFIED, family_id="EXSCEL")
    naive = [r for r in (x, y, u) if r.state == sm.VERIFIED]          # what a state-only filter would count
    assert x in naive                                                   # ... the comparator agreeing with itself
    got = sm.g1_countable([x, y, u], {"111"})
    assert x not in got and y in got and u not in got                   # the plant fires: x is excluded for X
    assert x in sm.g1_countable([x, y, u], {"999"})                     # but counts against another comparator


def test_positive_control_reproduces_and_a_tampered_row_breaks_it():
    rows = [_row(label=l, eff=e) for l, e in (("A", ("0.87", "0.78", "0.97")), ("B", ("0.74", "0.58", "0.95")),
                                              ("C", ("0.91", "0.83", "1.00")), ("D", ("0.78", "0.68", "0.90")))]
    import math
    yi = [sm.row_yi_vi(r)[0] for r in rows]
    vi = [sm.row_yi_vi(r)[1] for r in rows]
    mu, lo, hi = (math.exp(v) for v in sm.pool(yi, vi, "FE"))
    printed = {"effect": f"{mu:.2f}", "lower": f"{lo:.2f}", "upper": f"{hi:.2f}"}
    assert sm.positive_control(rows, printed, "HR")["reproduced"]
    rows[0].effect, rows[0].lower, rows[0].upper = "0.57", "0.51", "0.64"   # self-consistent but not the meta's row
    assert not sm.positive_control(rows, printed, "HR")["reproduced"]


def test_nested_subgroup_plato_planned_invasive_is_not_plato():
    r = _row(label="PLATO (planned invasive)", measure="HR")
    assert sm.nested_subgroup(r, 18624).startswith("NESTED_SUBGROUP_LABEL")
    r2 = _row(label="PLATO", measure="RR", eff=(None, None, None), events_t=569, n_t=6732, events_c=668, n_c=6676)
    assert sm.nested_subgroup(r2, 18624).startswith("NESTED_SUBGROUP_N:13408_of_18624")
    assert sm.nested_subgroup(_row(label="PLATO"), 18624) is None


def test_measure_and_outcome_identity():
    assert sm.measure_identity(_row(measure="HR"), "RR") == "MEASURE_HR_IS_NOT_ESTIMAND_RR"
    counts = _row(measure="RR", eff=(None, None, None), events_t=10, n_t=100, events_c=20, n_c=100)
    assert sm.measure_identity(counts, "OR") is None                    # counts -> OR without assumption
    assert sm.outcome_identity(_row(outcome="nonfatal myocardial infarction"), SPEC["keywords"],
                               tuple(SPEC["components"])) is not None
    assert sm.outcome_identity(_row(outcome="3-point MACE"), SPEC["keywords"]) is None


def test_admission_refuses_an_unlocated_row_and_admits_a_complete_one():
    bad = _row(source_digest="")
    assert sm.admit(bad, SPEC, lambda r: "LEADER").state == sm.REFUSED and "NO_SOURCE_DIGEST" in bad.reasons
    ok = sm.admit(_row(), SPEC, lambda r: "LEADER", randomised_n=9340)
    assert ok.state == sm.UNVERIFIED and ok.family_id == "LEADER"
    amb = sm.admit(_row(), SPEC, lambda r: None)
    assert amb.state == sm.REFUSED and "FAMILY_NOT_RESOLVED" in amb.reasons


def test_consolidation_refuses_two_rows_of_one_family_in_one_meta():
    a = sm.admit(_row(label="SUSTAIN-6"), SPEC, lambda r: "S6")
    b = sm.admit(_row(label="SUSTAIN-6 extension"), SPEC, lambda r: "S6")
    sm.consolidate([a, b])
    assert a.state == b.state == sm.REFUSED


def test_crosscheck_disagreement_blocks_both():
    a = sm.admit(_row(meta="111"), SPEC, lambda r: "LEADER")
    b = sm.admit(_row(meta="222", eff=("0.83", "0.74", "0.93")), SPEC, lambda r: "LEADER")
    sm.cross_check([a, b])
    assert a.state == b.state == sm.BLOCKED
    c = sm.admit(_row(meta="111"), SPEC, lambda r: "LEADER")
    d = sm.admit(_row(meta="333", eff=("0.87", "0.78", "0.97")), SPEC, lambda r: "LEADER")
    sm.cross_check([c, d])
    assert c.state == d.state == sm.UNVERIFIED


def test_primary_verification_match_and_typed_mismatch():
    r = sm.admit(_row(eff=("0.79", "0.57", "1.10"), label="PIONEER 6"), SPEC, lambda r: "P6")
    prim = {"measure": "HR", "effect": "0.79", "lower": "0.57", "upper": "1.11", "source": "PMID 31185157 abstract",
            "span": "hazard ratio, 0.79; 95% confidence interval [CI], 0.57 to 1.11"}
    sm.verify_against_primary(r, prim)
    assert r.state == sm.MISMATCH and r.verification["which_side"].startswith("SECONDARY_WRONG")
    ok = sm.admit(_row(), SPEC, lambda r: "LEADER")
    sm.verify_against_primary(ok, {"measure": "HR", "effect": "0.87", "lower": "0.78", "upper": "0.97",
                                   "source": "PMID 27295427", "span": "hazard ratio, 0.87; 95% CI, 0.78 to 0.97"})
    assert ok.state == sm.VERIFIED


def test_timepoint_unstated_is_refused_when_the_topic_registers_one_and_equal_lengths_match():
    r = _row(outcome="Effect of tocilizumab on mortality", measure="OR")
    assert sm.outcome_identity(r, ["28-day all-cause mortality"]) == "OUTCOME_NOT_THE_TOPICS"   # phrase only
    assert sm.outcome_identity(r, ["28-day all-cause mortality"], (), ("mortality",)) is None    # core word
    assert sm.timepoint_identity(r, "28 days") == "TIMEPOINT_NOT_STATED_BY_META"
    r.timepoint = "day 28"
    assert sm.timepoint_identity(r, "28 days") is None
    r.timepoint = "60-day"
    assert sm.timepoint_identity(r, "28 days").startswith("TIMEPOINT_60-day_NE")


def test_a_registered_timepoint_that_is_not_a_length_is_not_compared():
    r = _row(timepoint="12 days")
    assert sm.timepoint_identity(r, "trial end") is None          # GLP-1 registers 'trial end': no length to match
    assert sm.timepoint_identity(_row(), "trial end") is None


_JATS = b"""<article><body><table-wrap id="T2"><caption><p>Major adverse cardiovascular events (MACE), hazard ratio
(95% CI) by trial</p></caption><table><thead><tr><th>Trial</th><th>HR (95% CI)</th></tr></thead><tbody>
<tr><td>LEADER</td><td>0.87 (0.78\xe2\x80\x930.97)</td></tr>
<tr><td>SUSTAIN-6</td><td>0.74 (0.58\xe2\x80\x930.95)</td></tr>
<tr><td>EXSCEL</td><td>0.91 (0.83\xe2\x80\x931.00)</td></tr>
<tr><td>Overall</td><td>POOLED</td></tr></tbody></table></table-wrap></body></article>"""


def _jats_with_pool():
    import math
    t = sm.typed_rows_from_jats(_JATS.replace(b"POOLED", b"x"), "555")[0]
    yi = [sm.row_yi_vi(r)[0] for r in t["rows"]]
    vi = [sm.row_yi_vi(r)[1] for r in t["rows"]]
    mu, lo, hi = (math.exp(v) for v in sm.pool(yi, vi, "FE"))
    return _JATS.replace(b"POOLED", f"{mu:.2f} ({lo:.2f}–{hi:.2f})".encode("utf-8"))


def test_typed_table_rows_are_read_by_regex_with_the_tables_own_pool_as_control():
    t = sm.typed_rows_from_jats(_jats_with_pool(), "555")[0]
    assert [r.trial_label for r in t["rows"]] == ["LEADER", "SUSTAIN-6", "EXSCEL"]
    assert t["measure"] == "HR" and t["rows"][2].upper == "1.00" and t["rows"][0].provenance == "TYPED_TABLE"
    assert t["pooled"] and sm.positive_control(t["rows"], t["pooled"], "HR")["reproduced"]
    assert len(t["digest"]) == 64


def test_typed_table_without_a_pooled_row_has_no_control():
    t = sm.typed_rows_from_jats(_JATS.replace(b"<tr><td>Overall</td><td>POOLED</td></tr>", b""), "555")[0]
    assert t["pooled"] is None


def test_verification_derives_the_ratio_from_primary_counts_and_does_not_call_a_measure_difference_a_mismatch():
    tab = sm.admit(_row(label="Tabbalat 2020", measure="RR", eff=("0.88", "0.44", "1.76"), outcome="POAF"),
                   {"estimand": "RR", "keywords": ["POAF"]}, lambda r: "T20")
    sm.verify_against_primary(tab, {"measure": "RR", "events_t": 13, "n_t": 81, "events_c": 13, "n_c": 71,
                                    "source": "abstract", "span": "13 of 81 ... 13 of 71"})
    assert tab.state == sm.VERIFIED and tab.verification["result"] == "MATCH_FROM_PRIMARY_COUNTS"
    rr = sm.admit(_row(label="Manson 2019", measure="RR", eff=("0.92", "0.80", "1.06"), outcome="MACE"),
                  {"estimand": "RR", "keywords": ["MACE"]}, lambda r: "VITAL")
    sm.verify_against_primary(rr, {"measure": "HR", "effect": "0.92", "lower": "0.8", "upper": "1.06", "span": ""})
    assert rr.state == sm.UNVERIFIED and rr.verification["result"] == "MEASURE_DIFFERS"


def test_mismatch_side_is_decided_numerically_so_a_dropped_trailing_zero_still_anchors():
    r = sm.admit(_row(label="VITAL", eff=("0.92", "0.81", "1.06")), SPEC, lambda r: "V")
    sm.verify_against_primary(r, {"measure": "HR", "effect": "0.92", "lower": "0.8", "upper": "1.06",
                                  "span": "hazard ratio, 0.92; 95% CI, 0.80 to 1.06"})
    assert r.state == sm.MISMATCH and r.verification["which_side"].startswith("SECONDARY_WRONG")


def test_a_non_numeric_primary_value_leaves_the_row_queued_not_crashing():
    r = sm.admit(_row(label="Zhdanova", measure="MD", eff=("-7.0", "-12.0", "-2.0"), outcome="sleep onset latency"),
                 {"estimand": "MD", "keywords": ["sleep onset latency"]}, lambda r: "Z")
    sm.verify_against_primary(r, {"measure": "MD", "effect": "0:31", "lower": "0:20", "upper": "0:40", "span": "0:31"})
    assert r.state == sm.UNVERIFIED and r.verification["result"] == "PRIMARY_NOT_NUMERIC"


def test_queue_invariant_every_unverified_row_has_a_typed_queue_reason():
    q = sm.admit(_row(label="LEADER"), SPEC, lambda r: "LEADER")
    assert sm.queue_complete([q]) == [q]                        # the plant: admitted, unverified, no queue entry
    sm.verify_against_primary(q, None, queue_reason="NO_PRIMARY:LOCATOR_NOT_REPORTED")
    assert sm.queue_complete([q]) == [] and q.verification["queue_reason"] == "NO_PRIMARY:LOCATOR_NOT_REPORTED"
    m = sm.admit(_row(label="VITAL", measure="RR", eff=("0.92", "0.80", "1.06"), outcome="MACE"),
                 {"estimand": "RR", "keywords": ["MACE"]}, lambda r: "V")
    sm.verify_against_primary(m, {"measure": "HR", "effect": "0.92", "lower": "0.80", "upper": "1.06", "span": ""})
    assert sm.queue_complete([m]) == [] and m.verification["queue_reason"] == "MEASURE_DIFFERS"
    n = sm.admit(_row(label="X"), SPEC, lambda r: "X")
    sm.verify_against_primary(n, None)                            # no reason given -> still a typed default, never empty
    assert n.verification["queue_reason"] == "NO_PRIMARY_VALUE"


def test_a_clipped_span_is_completed_by_the_report_text_when_deciding_the_side():
    r = sm.admit(_row(label="PIONEER 6", eff=("0.79", "0.57", "1.10")), SPEC, lambda r: "P6")
    sm.verify_against_primary(r, {"measure": "HR", "effect": "0.79", "lower": "0.57", "upper": "1.11",
                                  "span": "... (hazard ratio, 0.79; ",                       # clipped at 200 chars
                                  "report_text": "hazard ratio, 0.79; 95% confidence interval, 0.57 to 1.11"})
    assert r.state == sm.MISMATCH and r.verification["which_side"].startswith("SECONDARY_WRONG")


def _claim(quote, **kw):
    base = {"state": "REPORTED", "quote": quote, "measure": None, "point": None, "lower": None, "upper": None,
            "events_t": None, "n_t": None, "events_c": None, "n_c": None}
    base.update(kw)
    return base


def test_locator_gate_reasons_are_distinct_and_printed_number_formats_are_numbers():
    text = ("The primary end point occurred in 386 of 12,933 participants with n-3 fatty acids and 419 of 12,938 with "
            "placebo (hazard ratio, 0·92; 95% CI, 0·80 to 1·06). Sleep latency fell to 0:31.")
    # VITAL: thousands separators were refused as NON_NUMERIC -- now the counts are accepted as printed
    v, why = sm.gate_locator_claim(_claim("386 of 12,933 participants with n-3 fatty acids and 419 of 12,938",
                                          events_t="386", n_t="12,933", events_c="419", n_c="12,938"), text)
    assert why == "ACCEPTED" and v["n_t"] == 12933
    # a mid-dot decimal is the number it prints
    v, why = sm.gate_locator_claim(_claim("hazard ratio, 0·92; 95% CI, 0·80 to 1·06", measure="hazard ratio",
                                          point="0·92", lower="0·80", upper="1·06"), text)
    assert why == "ACCEPTED" and (v["effect"], v["lower"], v["upper"]) == ("0.92", "0.80", "1.06")
    # nothing copied is NOT 'number not in quote' (13 of 58 answers were mislabelled so)
    assert sm.gate_locator_claim(_claim("hazard ratio, 0·92"), text)[1] == "NO_NUMBERS_COPIED"
    assert sm.gate_locator_claim(_claim("Sleep latency fell to 0:31.", point="0:31"), text)[1] == "NON_NUMERIC"
    assert sm.gate_locator_claim(_claim("hazard ratio, 0·92", point="0.91"), text)[1] == "NUMBER_NOT_IN_QUOTE"
    assert sm.gate_locator_claim(_claim("not in the text at all", point="1"), text)[1] == "QUOTE_NOT_IN_TEXT"
    assert sm.gate_locator_claim(_claim("386 of 12,933", events_t="386", n_t="12,933"), text)[1] == "INCOMPLETE"
    assert sm.gate_locator_claim({"state": "NOT_REPORTED"}, text)[1] == "NOT_REPORTED"


def test_a_counts_request_takes_the_counts_when_an_hr_is_also_copied():
    text = "386 of 12,933 vs 419 of 12,938 (hazard ratio, 0.92; 95% CI, 0.80 to 1.06)"
    c = _claim(text, measure="hazard ratio", point="0.92", lower="0.80", upper="1.06",
               events_t="386", n_t="12,933", events_c="419", n_c="12,938")
    assert sm.gate_locator_claim(c, text)[0]["measure"] == "HR"                     # default: the reported effect
    v, why = sm.gate_locator_claim(c, text, prefer="counts")
    assert why == "ACCEPTED" and (v["events_t"], v["n_t"], v["events_c"], v["n_c"]) == (386, 12933, 419, 12938)


# ------------------------------------------------ deterministic verification (typed match, no model)

def test_typed_text_match_needs_same_numbers_same_measure_and_the_outcome_nearby():
    r = sm.admit(_row(label="PIONEER 6", eff=("0.79", "0.57", "1.11")), SPEC, lambda r: "P6")
    ok = ("Major adverse cardiovascular events (MACE) occurred in 61 of 1591 patients and 76 of 1592 "
          "(hazard ratio, 0.79; 95% confidence interval [CI], 0.57 to 1.11).")
    assert sm.typed_match_text(r, ok, ["MACE"], "abstract")["result"] == "TYPED_MATCH"
    assert sm.typed_match_text(r, ok.replace("hazard ratio", "odds ratio"), ["MACE"], "abstract") is None   # measure
    assert sm.typed_match_text(r, ok.replace("1.11", "1.10"), ["MACE"], "abstract") is None                 # numbers
    far = "Death from any cause (hazard ratio, 0.79; 95% CI, 0.57 to 1.11)."
    assert sm.typed_match_text(r, far, ["MACE"], "abstract") is None                                          # outcome


def test_typed_text_match_on_arm_counts_both_arms_with_thousands_separators():
    r = sm.admit(_row(label="VITAL", measure="RR", eff=(None, None, None), outcome="MACE", events_t=386, n_t=12933,
                      events_c=419, n_c=12938), {"estimand": "RR", "keywords": ["MACE"]}, lambda r: "V")
    t = "The MACE end point occurred in 386 of 12,933 participants and 419 of 12,938 in the placebo group."
    assert sm.typed_match_text(r, t, ["MACE"], "abstract")["result"] == "TYPED_MATCH"
    assert sm.typed_match_text(r, t.replace("419 of", "420 of"), ["MACE"], "abstract") is None


def test_typed_registry_match_analysis_and_group_counts():
    reg = {"outcomes": {"o1": {"title": "Time to First MACE", "time_frame": "3 years"}, "o2": {"title": "All-cause death"}},
           "analyses": [{"outcome_id": "o1", "param_type": "Hazard Ratio (HR)", "param_value": "0.87",
                         "ci_lower": "0.78", "ci_upper": "0.97"},
                        {"outcome_id": "o2", "param_type": "Hazard Ratio (HR)", "param_value": "0.79",
                         "ci_lower": "0.57", "ci_upper": "1.11"}],
           "groups": {"o1": [{"group": "A", "count": 608, "n": 4668}, {"group": "B", "count": 694, "n": 4672}]}}
    r = sm.admit(_row(label="LEADER"), SPEC, lambda r: "L")
    assert sm.typed_match_registry(r, reg, ["MACE"], "AACT")["result"] == "TYPED_MATCH"
    wrong = sm.admit(_row(label="X", eff=("0.79", "0.57", "1.11")), SPEC, lambda r: "X")
    assert sm.typed_match_registry(wrong, reg, ["MACE"], "AACT") is None        # those numbers belong to 'death'
    c = sm.admit(_row(label="LEADER", measure="RR", eff=(None, None, None), events_t=608, n_t=4668, events_c=694,
                      n_c=4672), {"estimand": "RR", "keywords": ["MACE"]}, lambda r: "L")
    assert sm.typed_match_registry(c, reg, ["MACE"], "AACT")["result"] == "TYPED_MATCH"
    sm.verify_typed(c, [("registry", "AACT", reg)], ["MACE"])
    assert c.state == sm.VERIFIED


# ------------------------------------------------------------------ 2 Oct decisions: registry as PRIMARY, TWO-SOURCE rule

def test_registry_verification_records_snapshot_fields_and_differences_without_reconciling():
    reg = {"_snapshot": {"id": "AACT 2026-08-30", "digest": "abc"},
           "outcomes": {"o1": {"title": "All-cause mortality", "time_frame": "Day 60",
                               "population": "Safety population: all participants who received study drug"}},
           "analyses": [], "group_titles": {"g1": "Tocilizumab", "g2": "Placebo"},
           "groups": {"o1": [{"group": "g1", "count": 49, "n": 294}, {"group": "g2", "count": 25, "n": 144}]}}
    r = _row(label="COVACTA", measure="RR", eff=(None, None, None), events_t=49, n_t=294, events_c=25, n_c=144,
             timepoint="28 days", population="intention-to-treat")
    sm.verify_typed(r, [("registry", "NCT04320615 AACT", reg)], ["mortality"])
    v = r.verification
    assert r.state == sm.VERIFIED and v["route"] == "PRIMARY_REGISTRY"     # the numbers match: verified, not refused
    assert v["registry_fields"]["snapshot"] == {"id": "AACT 2026-08-30", "digest": "abc"}
    assert [a["title"] for a in v["registry_fields"]["arm_counts"]] == ["Tocilizumab", "Placebo"]
    diffs = {d["field"]: d for d in v["registry_vs_publication"]}
    assert diffs["timepoint"]["registry"] == "Day 60" and diffs["timepoint"]["publication"] == "28 days"
    assert (diffs["analysis_population"]["registry"], diffs["analysis_population"]["publication"]) == ("SAFETY", "ITT")
    same = _row(label="COVACTA", measure="RR", eff=(None, None, None), events_t=49, n_t=294, events_c=25, n_c=144)
    sm.verify_typed(same, [("registry", "AACT", reg)], ["mortality"])
    assert same.verification["registry_vs_publication"] == []              # unstated is not a difference


def test_population_class_reads_modified_itt_before_itt():
    assert sm.population_class("modified intention-to-treat population") == "MITT"
    assert sm.population_class("Intention-to-treat") == "ITT"
    assert sm.population_class("participants who received at least one dose") == "SAFETY"
    assert sm.population_class(None) == "NOT_STATED"


def test_cited_ids_from_jats_and_unknown_when_no_reference_list():
    j = (b'<article><body/><back><ref-list><ref><pub-id pub-id-type="pmid">34526024</pub-id></ref>'
         b'<ref><pub-id pub-id-type="doi">10.1/ABC</pub-id></ref></ref-list></back></article>')
    assert sm.cited_ids_from_jats(j) == {"34526024", "10.1/abc"}
    assert sm.cited_ids_from_jats(b"<article><body/></article>") is None


def _pair(ma, mb, eb=("0.87", "0.78", "0.97")):
    a = _row(meta=ma, family_id="LEADER", source_digest="da")
    b = _row(meta=mb, family_id="LEADER", eff=eb, source_digest="db")
    for r in (a, b):
        r.verification = {"result": "QUEUED", "queue_reason": "NO_PRIMARY:NOT_FOUND"}
    return a, b


def test_two_source_needs_agreement_and_independence():
    refs = {"111": {"9"}, "222": {"8"}, "333": {"111"}, "444": {"777"}, "555": {"777"}}
    a, b = _pair("111", "222")
    sm.two_source([a, b], refs.get, {"777"})
    assert a.state == b.state == sm.TWO_SOURCE and a.verification["independent_pairs"] == [["111", "222"]]
    a, b = _pair("111", "333")                                    # 333 cites 111: may have copied its extraction
    sm.two_source([a, b], refs.get, {"777"})
    assert a.state == sm.UNVERIFIED and "CITES_OTHER:333->111" in a.verification["queue_reason"]
    a, b = _pair("444", "555")                                    # both cite meta 777 of this topic
    sm.two_source([a, b], refs.get, {"777"})
    assert b.state == sm.UNVERIFIED and "COMMON_CITED_META:777" in b.verification["queue_reason"]
    a, b = _pair("111", "999")                                    # no reference list for 999: fail closed
    sm.two_source([a, b], refs.get, set())
    assert a.state == sm.UNVERIFIED and "CITATIONS_UNKNOWN:999" in a.verification["queue_reason"]
    a, b = _pair("111", "222", eb=("0.88", "0.79", "0.98"))       # independent but different numbers
    sm.two_source([a, b], refs.get, set())
    assert a.state == b.state == sm.UNVERIFIED
    assert not sm.queue_complete([a, b])                          # still queued, with reasons


def test_two_source_row_counts_for_g1_only_if_an_independent_pair_survives_removing_the_comparator():
    refs = {"111": set(), "222": set(), "333": set()}
    a, b = _pair("111", "222")
    sm.two_source([a, b], refs.get, set())
    assert sm.g1_countable([a, b], {"111"}) == []                 # the only pair includes the comparator
    a, b = _pair("222", "333")
    sm.two_source([a, b], refs.get, set())
    assert sm.g1_countable([a, b], {"111"}) == [a, b]
    assert sm.route_of(a) == "TWO_SOURCE"


def test_typed_table_reads_unicode_minus_signs_and_pools_md_from_the_arms():
    # Medicine (Baltimore) 2026 (PMID 42536519) prints its mean-difference forest table with U+2212 MINUS SIGN; the
    # typed reader saw no row and no pooled row, so the table was dropped and the meta fell to a refused figure read.
    # Its total follows from the ARM columns (RevMan), not from the printed row CIs: Rubino's printed CI is a typo.
    m = "−"
    rows = [("O'Neil 2018", f"{m}13.8 (8.38)", 102, f"{m}2.3 (8.63)", 136, f"{m}11.50 ({m}13.68, {m}9.32)"),
            ("Rubino 2021", f"{m}17.4 (9.2)", 535, f"{m}5 (9.2)", 268, f"{m}12.40 ({m}14.75, {m}10.05)"),
            ("Wadden 2021", f"{m}16 (10.11)", 407, f"{m}5.7 (10.11)", 204, f"{m}10.30 ({m}12.00, {m}8.60)"),
            ("Wilding 2021", f"{m}14.85 (9.91)", 1306, f"{m}2.41 (9.91)", 655, f"{m}12.44 ({m}13.37, {m}11.51)")]
    body = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td><td>x%</td><td>{f}</td></tr>"
                   for a, b, c, d, e, f in rows)
    body += f"<tr><td>Total (95% CI)</td><td/><td>2350</td><td/><td>1263</td><td>100%</td><td>{m}11.85 ({m}12.81, {m}10.90)</td></tr>"
    jats = (f"<article><body><table-wrap id='T3'><caption><p>Effect of semaglutide on mean weight difference versus "
            f"placebo.</p></caption><table><thead><tr><th>Study</th><th>Semaglutide mean (SD)</th><th>Semaglutide total</th>"
            f"<th>Placebo mean (SD)</th><th>Placebo total</th><th>Weight</th>"
            f"<th>Mean difference (IV, random, 95% CI)</th></tr></thead><tbody>{body}</tbody></table></table-wrap>"
            f"</body></article>").encode("utf-8")
    t = sm.typed_rows_from_jats(jats, "42536519")
    assert len(t) == 1 and t[0]["measure"] == "MD" and len(t[0]["rows"]) == 4
    w = t[0]["rows"][3]
    assert (w.effect, w.lower, w.upper) == ("-12.44", "-13.37", "-11.51")
    assert (w.mean_t, w.sd_t, w.n_t, w.mean_c, w.sd_c, w.n_c) == ("-14.85", "9.91", 1306, "-2.41", "9.91", 655)
    assert t[0]["pooled"]["effect"] == "-11.85"
    pc = sm.positive_control(t[0]["rows"], t[0]["pooled"], "MD")
    assert pc["reproduced"] and "DL" in pc["methods"]
    assert [r.findings[0]["finding"] for r in t[0]["rows"] if r.findings] == ["ROW_CI_NOT_FROM_ARMS"]
    assert t[0]["rows"][1].findings[0]["printed_vs_arm_derived"]["lower"] == ("-14.75", -13.75)
    # no aligned header naming the control -> arm-level data are NOT taken (arm order unknown)
    bad = jats.replace(b"<th>Placebo mean (SD)</th>", b"<th>Mean (SD)</th>")
    assert sm.typed_rows_from_jats(bad, "x")[0]["rows"][3].mean_t is None


# ------------------------------------------------------------------ SECONDARY_SINGLE (Mahmood decision, 3 Oct)
def _single_row(meta="111", state=None):
    r = _row(measure="HR", effect="0.80", lower="0.70", upper="0.91")
    r.meta_pmid, r.family_id = meta, "PMID 1"
    r.state = state or sm.UNVERIFIED
    r.verification = {"result": "QUEUED", "queue_reason": "NO_PRIMARY_VALUE"}
    return r


def test_SECONDARY_SINGLE_counts_one_self_reproducing_non_comparator_meta_when_no_primary_is_open():
    r = _single_row()
    assert sm.secondary_single([r], {"999"}, lambda x: None, lambda x: True) == [r]
    assert r.state == sm.SECONDARY_SINGLE and sm.route_of(r) == "SECONDARY_SINGLE"
    assert sm.g1_countable([r], {"999"}) == [r]


def test_PLANT_SECONDARY_SINGLE_never_from_the_comparator_an_open_primary_or_a_non_reproducing_meta():
    comp = _single_row(meta="999")
    assert sm.secondary_single([comp], {"999"}, lambda x: None, lambda x: True) == [] and comp.state == sm.UNVERIFIED
    opened = _single_row()
    assert sm.secondary_single([opened], {"999"}, lambda x: "PMID 1 PMC OA", lambda x: True) == []
    assert opened.state == sm.UNVERIFIED and "PRIMARY_SOURCE_OPEN" in opened.verification["queue_reason"]
    norep = _single_row()
    assert sm.secondary_single([norep], {"999"}, lambda x: None, lambda x: False) == [] and norep.state == sm.UNVERIFIED
    blocked = _single_row(state=sm.BLOCKED)
    assert sm.secondary_single([blocked], {"999"}, lambda x: None, lambda x: True) == [] and blocked.state == sm.BLOCKED
    # anti-circularity holds even if a comparator row were somehow marked SECONDARY_SINGLE
    comp.state = sm.SECONDARY_SINGLE
    assert sm.g1_countable([comp], {"999"}) == []


# ------------------------------------------------------------------ Mantel-Haenszel in our engine (pool_mh)
# PMID 34385227 Fig 3 (42 trials), counts as the dual-model reader agreed them; references computed with R 4.6.0:
# meta::metabin(a,n1,c,n2,sm="RR",method="MH",method.tau="DL",Q.Cochrane=TRUE) and metafor::rma.mh (no zero cells)
PROBIOTICS_COUNTS = [(159, 1470, 153, 1471), (7, 44, 16, 45), (13, 105, 23, 97), (4, 41, 5, 45), (1, 73, 7, 78), (19, 176, 26, 167), (1, 13, 5, 10), (9, 62, 19, 62), (4, 30, 5, 58), (14, 204, 28, 185), (21, 246, 19, 231), (21, 80, 29, 80), (37, 171, 34, 84), (3, 36, 9, 43), (16, 44, 14, 41), (7, 57, 19, 56), (16, 181, 23, 90), (3, 26, 0, 20), (1, 12, 3, 7), (1, 20, 5, 20), (9, 19, 17, 21), (7, 33, 5, 36), (6, 80, 5, 83), (7, 97, 14, 96), (54, 336, 41, 167), (17, 340, 63, 338), (23, 65, 38, 65), (15, 69, 15, 69), (13, 106, 16, 98), (106, 549, 103, 577), (4, 23, 6, 16), (47, 216, 70, 221), (0, 61, 7, 61), (1, 18, 2, 17), (9, 103, 16, 111), (11, 116, 14, 64), (39, 133, 40, 134), (50, 247, 14, 67), (2, 34, 8, 29), (13, 76, 44, 82), (5, 41, 4, 46), (27, 132, 15, 32)]


def _count_rows(counts, measure="RR"):
    out = []
    for a, n1, c, n2 in counts:
        r = _row(measure=measure)
        r.effect = r.lower = r.upper = None
        r.events_t, r.n_t, r.events_c, r.n_c = a, n1, c, n2
        out.append(r)
    return out


def test_pool_mh_matches_R_meta_metabin_revman_mode_on_42_trials():
    import math
    rows = _count_rows(PROBIOTICS_COUNTS)
    fe = [math.exp(x) for x in sm.pool_mh(rows, "RR")]
    re_ = [math.exp(x) for x in sm.pool_mh(rows, "RR", random=True)]
    assert all(abs(a - b) < 2e-6 for a, b in zip(fe, (0.7035394, 0.6471383, 0.7648562)))
    assert all(abs(a - b) < 2e-5 for a, b in zip(re_, (0.6255739, 0.5356020, 0.7306596)))


def test_pool_mh_matches_metafor_rma_mh_without_zero_cells_and_refuses_without_counts():
    import math
    c3 = [(12, 100, 18, 100), (8, 90, 15, 92), (20, 150, 24, 148)]
    rr = [math.exp(x) for x in sm.pool_mh(_count_rows(c3), "RR")]
    orr = [math.exp(x) for x in sm.pool_mh(_count_rows(c3, "OR"), "OR")]
    assert all(abs(a - b) < 2e-6 for a, b in zip(rr, (0.700988, 0.481530, 1.020465)))
    assert all(abs(a - b) < 2e-6 for a, b in zip(orr, (0.661155, 0.427577, 1.022333)))
    assert sm.pool_mh(_count_rows(c3), "HR") is None                    # M-H needs a 2x2 measure
    no_counts = _count_rows(c3)
    no_counts[0].events_t = None
    assert sm.pool_mh(no_counts, "RR") is None
    assert sm.pool_mh(_count_rows([(0, 30, 0, 30)] + c3[:1]), "RR") is None   # double-zero not estimable -> < 2 rows


def test_reml_pool_matches_metafor_on_dat_bcg():
    # metafor 5.0.1 (R 4.6.0): escalc("RR", dat.bcg); rma(method="REML") and rma(method="REML", test="knha")
    yi = [-0.889311333920, -1.585388657201, -1.348073148300, -1.441551190021, -0.217547322211, -0.786115585819,
          -1.620898223598, 0.011952333524, -0.469417648738, -1.371344803473, -0.339358828338, 0.445913400571,
          -0.017313948217]
    vi = [0.325584765004, 0.194581121398, 0.415367965368, 0.020010031902, 0.051210172170, 0.006905618456,
          0.223017247572, 0.003961579298, 0.056434210463, 0.073024793613, 0.012412213972, 0.532505845200,
          0.071404659684]
    assert abs(sm.reml_tau2(yi, vi) - 0.313243325981) < 1e-6
    mu, lo, hi = sm.pool(yi, vi, "REML")
    assert max(abs(mu + 0.714532348365), abs(lo + 1.066897675740), abs(hi + 0.362167020990)) < 1e-6
    _, lo, hi = sm.pool(yi, vi, "REML", hk=True)
    assert max(abs(lo + 1.108443723000), abs(hi + 0.320620973730)) < 1e-6
    # homogeneous pair: tau^2 truncated at 0 and the pool is the fixed-effect mean (metafor: 0, 0.108888888889)
    assert sm.reml_tau2([0.1, 0.12], [0.04, 0.05]) == 0.0
    assert abs(sm.pool([0.1, 0.12], [0.04, 0.05], "REML")[0] - 0.108888888889) < 1e-9



def test_a_forest_reads_measure_wording_is_normalised_typed():
    # omega3 5 Oct: GISSI-P's row was refused 'MEASURE_FIXED EFFECT RELATIVE RISK (95% CI)_IS_NOT_ESTIMAND_RR' -- the
    # reader wrote the measure as 'Fixed effect relative risk (95% CI)'; and 'Std. Mean Difference' became MD
    import secondary_meta_build as smb
    assert smb.normalize_measure("Fixed effect relative risk (95% CI)") == "RR"
    assert smb.normalize_measure("Risk Ratio, M-H, Random, 95% CI") == "RR"
    assert smb.normalize_measure("RELATIVE RISK (95% CI)") == "RR"
    assert smb.normalize_measure("Odds Ratio (M-H, Fixed)") == "OR"
    assert smb.normalize_measure("Hazard ratio") == "HR"
    assert smb.normalize_measure("Rate ratio") == "IRR"                 # never a ratio of risks
    assert smb.normalize_measure("Std. Mean Difference, IV, Random") == "SMD"
    assert smb.normalize_measure("Standardised mean difference") == "SMD"
    assert smb.normalize_measure("Mean Difference IV, Fixed") == "MD"
    assert smb.normalize_measure("WMD") == "MD"
    assert smb.normalize_measure("ES (95% CI)") == "ES (95% CI)"         # unknown wording stays as printed


def test_a_meta_whose_pool_cannot_be_checked_is_only_ever_a_second_source():
    # decision 5 Oct (tocilizumab 35802687: rows agreed by both readers, the figure prints no pooled row): such a meta
    # never counts as SECONDARY_SINGLE alone, and two of them never confirm each other; it may only be the SECOND
    # source beside an independent meta that passed the gate
    refs = {"111": {"9"}, "222": {"8"}}
    unchecked = [sm.POOL_UNCHECKABLE + ": the figure prints no pooled row"]
    a, b = _pair("111", "222")
    a.findings, b.findings = list(unchecked), list(unchecked)
    sm.two_source([a, b], refs.get, set())
    assert a.state == b.state == sm.UNVERIFIED and "BOTH_POOLS_UNCHECKABLE" in a.verification["queue_reason"]
    a, b = _pair("111", "222")
    a.findings = list(unchecked)                                    # b's meta passed the gate
    sm.two_source([a, b], refs.get, set())
    assert a.state == b.state == sm.TWO_SOURCE
    c = _row(meta="333", state=sm.UNVERIFIED, family_id="LEADER")
    c.findings = list(unchecked)
    assert sm.secondary_single([c], {"999"}, lambda r: None, lambda r: True) == []
    assert c.state == sm.UNVERIFIED and "SECONDARY_SINGLE_REFUSED:POOL_UNCHECKABLE" in c.verification["queue_reason"]
def test_pool_uncheckable_reads_a_finding_typed_as_a_dict():
    # secondary_meta_build.as_finding types every lane finding as {'finding': CODE, 'detail': ...} at entry: the
    # second-source-only mark must survive that typing, or a no-pool meta could become SECONDARY_SINGLE
    r = _row(meta="333", state=sm.UNVERIFIED, family_id="LEADER")
    r.findings = [{"finding": sm.POOL_UNCHECKABLE, "detail": "no printed pooled row"}]
    assert sm.pool_uncheckable(r)
    assert sm.secondary_single([r], {"999"}, lambda x: None, lambda x: True) == [] and r.state == sm.UNVERIFIED


def test_PLANT_a_forest_lane_row_takes_its_timepoint_from_the_meta_like_every_figure_row():
    # corticosteroids-covid (5 Oct consolidation): k-gap's forest_lane_metas rows carried no timepoint, so the meta's
    # 28-day statement was never read and three SECONDARY_SINGLE rows fell to TIMEPOINT_NOT_STATED_BY_META
    import secondary_meta_build as smb
    r = sm.SecondaryRow(meta_pmid="33612824", meta_doi="", location={}, source_digest="", provenance="FOREST_READER_DUAL",
                        trial_label="Tomazini 2020 CoDEX", measure="RR", outcome_definition="Forest plot", events_t=1,
                        n_t=10, events_c=2, n_c=10)
    smb.lane_row_timepoint(r, {"core": True}, held_text=lambda pm: "The primary outcome was all-cause mortality at 28 days.")
    assert r.timepoint
    kept = sm.SecondaryRow(**{**r.__dict__, "timepoint": "90 days"})
    smb.lane_row_timepoint(kept, {"core": True}, held_text=lambda pm: "mortality at 28 days")
    assert kept.timepoint == "90 days"                                   # a stated timepoint is never overwritten
    other = sm.SecondaryRow(**{**r.__dict__, "timepoint": None})
    smb.lane_row_timepoint(other, {"core": False}, held_text=lambda pm: "mortality at 28 days")
    assert other.timepoint is None                                       # only core outcomes read the meta's text


def test_a_forest_lane_row_gets_the_timepoint_its_caption_states_like_every_figure_row():
    # the build derives a figure row's timepoint from the meta's own words (secondary_meta_build.meta_timepoint); the
    # forest-lane rows entered without it, so every 28-day tocilizumab row read TIMEPOINT_NOT_STATED_BY_META (5 Oct)
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
    import secondary_meta_build as smb
    r = _row(measure="OR", outcome="Pooled comparison of 28-day mortality according to treatment received")
    spec = {"estimand": "OR", "keywords": ["mortality"], "core": ["mortality"], "timepoint": "28 days"}
    smb.lane_timepoint(r, spec, held="")
    assert r.timepoint == "28 days"
    assert sm.timepoint_identity(r, spec["timepoint"]) is None
    r2 = _row(measure="OR", outcome="Overall meta-analysis of 28/30-day mortality")
    smb.lane_timepoint(r2, spec, held="mortality at 30 days was the primary outcome")
    assert sm.timepoint_identity(r2, spec["timepoint"]) is not None       # the gate itself is unchanged
