"""Secondary-source tier (harness/secondary_meta.py): one plant per rule. Each builds the shape the rule exists for."""
import hashlib

from harness import secondary_meta as sm

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
