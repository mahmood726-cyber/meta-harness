"""PLANTS for scripts/g1_two_source_sweep.py and its tracker merge (g1_tracker.sweep_merge). What may count as MATCHED from
the sweep: only a SWEEP_* verdict (two sources agreeing on the typed tuple). Posted results alone (SMART: 5,381 patients
posted vs 15,802 reported), an unverified meta row, or a trial named out of scope never count; the comparator is never
discovered as a source of itself."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
import g1_tracker as gt  # noqa: E402
import g1_two_source_sweep as sw  # noqa: E402


def _trials():
    return [{"label": "A", "in_our_pool": False, "route": "NO_ROW", "scope_difference": None, "comparator_row": None},
            {"label": "B", "in_our_pool": False, "route": "NO_ROW", "scope_difference": None, "comparator_row": None},
            {"label": "C", "in_our_pool": False, "route": "NO_ROW", "scope_difference": None, "comparator_row": None},
            {"label": "D", "in_our_pool": False, "route": "NO_ROW", "scope_difference": {"kind": "PROTOCOL_SCOPE_DIFFERENCE"},
             "comparator_row": None}]


def test_only_a_two_source_verdict_is_merged_as_matched(monkeypatch):
    v = {"measure": "RR", "effect": "0.80", "lower": "0.60", "upper": "1.05"}
    monkeypatch.setattr(gt, "sweep_results", lambda slug: {
        "A": {"label": "A", "verdict": "SWEEP_TWO_INDEPENDENT_METAS", "value": v},
        "B": {"label": "B", "verdict": "AACT_ONLY_SINGLE_SOURCE", "value": {"measure": "COUNTS"}},
        "C": {"label": "C", "verdict": "ROWS_NOT_VERIFIED"},
        "D": {"label": "D", "verdict": "SWEEP_META+TRIAL_TEXT", "value": v}})
    tr = _trials()
    assert gt.sweep_merge("t", tr) == ["A"]
    assert [gt.is_matched(x) for x in tr] == [True, False, False, False]      # D is named out of scope: never matched
    assert tr[0]["route"] == "SWEEP_TWO_INDEPENDENT_METAS" and tr[0]["g1_countable"]


def test_a_merged_trial_leaves_the_open_gaps_and_the_counts_follow(monkeypatch):
    monkeypatch.setattr(gt, "sweep_results", lambda slug: {
        "A": {"label": "A", "verdict": "SWEEP_META+AACT", "value": {"measure": "HR", "effect": "0.9", "lower": "0.8",
                                                                     "upper": "1.0"}}})
    o = {"trials": _trials()[:3], "open_gaps": ["A", "B", "C"], "named_differences": [], "N_eligible": 3,
         "N_comparator_trials": 3, "k_matched": 0}
    gt.apply_sweep(o, "t")
    assert o["k_matched"] == 1 and o["open_gaps"] == ["B", "C"] and gt.scope_citation_violations(o) == []
    assert o["sweep_merged"] == {"trials": ["A"], "same_trials_recomputed": False}


def test_the_comparator_is_never_discovered_as_a_source(monkeypatch):
    hits = {"hits": [{"pmid": "111", "doi": "10.1/comp"}, {"pmid": "222", "doi": "10.1/other", "cited": 5},
                     {"pmid": "999", "doi": ""}]}
    monkeypatch.setattr(sw, "search", lambda q, run: dict(hits, state="SEARCHED"))
    t = {"report_pmid": "999", "cited_pmids": [], "ncts": [], "acronyms": [], "pmids": ["999"]}
    got, _ = sw.discover(t, {"111", "10.1/comp"}, run=False)
    assert got == ["222"]                     # neither the comparator (by PMID or DOI) nor the trial's own report


def test_label_acronyms_split_the_year_and_refuse_author_labels():
    assert sw.label_acronyms("RALES1999") == {"RALES"}
    assert sw.label_acronyms("ARTS-HF2013") == {"ARTS-HF"}
    assert sw.label_acronyms("Yusuf, 1991") == set() and sw.label_acronyms("STEP 1") == set()


def test_forest_plan_gives_each_trial_two_metas_greedily():
    by = {"A": ["m1", "m2", "m3"], "B": ["m1", "m3"], "C": ["m4"]}
    ts = [{"label": k} for k in by]
    plan = sw.forest_plan(ts, by, typed_ok=set())
    assert plan[0] == "m1" and set(plan) == {"m1", "m3", "m4"}      # m2 not needed once A has m1 + m3


def test_every_committed_sweep_file_counts_only_two_source_verdicts():
    d = os.path.join(ROOT, "outputs", "k_gap", "sweep")
    if not os.path.isdir(d):
        return
    bad = []
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json") or f == "sweep_summary.json":
            continue
        for t in json.load(open(os.path.join(d, f), encoding="utf-8"))["trials"]:
            if str(t["verdict"]).startswith("SWEEP_"):
                ok = ("PRIMARY_VERIFIED", "TWO_SOURCE_VERIFIED") + (
                    ("SECONDARY_UNVERIFIED",) if t["verdict"] == "SWEEP_SECONDARY_SINGLE" else ())
                rows = [r for r in t["rows"] if r["state"] in ok]
                if not rows or t["value"] is None:
                    bad.append(f"{f}::{t['label']}")
    assert not bad, bad


def test_a_lane_file_without_pool_membership_counts_its_verified_routes():
    # g1/tocilizumab writes in_our_pool null and counts COVACTA (PRIMARY) / TOCIBRAS (TWO_SOURCE) as matched: they must
    # never be relisted as open gaps (they were, once, on 3 Oct, by cite_or_demote)
    o = {"trials": [{"label": "COVACTA", "in_our_pool": None, "g1_countable": True, "route": "PRIMARY"},
                    {"label": "TOCIBRAS", "in_our_pool": None, "g1_countable": True, "route": "TWO_SOURCE"},
                    {"label": "RECOVERY", "in_our_pool": None, "g1_countable": False, "route": "UNVERIFIED"}],
         "open_gaps": ["RECOVERY"], "named_differences": [], "N_eligible": 3, "k_matched": 2}
    gt.cite_or_demote(o, "t")
    assert o["open_gaps"] == ["RECOVERY"] and gt.scope_citation_violations(o) == []
    o["k_matched"] = 3
    assert gt.scope_citation_violations(o) == ["k_matched 3 != matched trials 2"]


def test_a_reader_disagreement_is_never_a_silent_pick():
    # sglt2-hfref EMPEROR-Reduced: the forest reader's two readings of the comparator row are 0.75 (0.65-0.87) and
    # 0.75 (0.65-0.86). RESULT_AGREES holds only if the same-trials verdict is the same under BOTH readings.
    o = {"N_eligible": 1, "k_matched": 1, "open_gaps": [], "named_differences": [],
         "same_trials": {"verdict": {"verdict": "AGREE"}},
         "trials": [{"label": "A", "in_our_pool": True, "route": "PRIMARY", "agreement_with_comparator_row": "READERS_DIFFER",
                     "comparator_row_readings": {"state": "READERS_DIFFER"}}]}
    assert "RESULT_AGREES" in gt.g1_status(o)["unmet"]
    o["same_trials"]["readers_agree_on_verdict"] = True
    assert gt.g1_status(o)["state"] == "G1_MATCHED"


def _one_source(source, **kw):
    return {"label": "T", "route": "UNVERIFIED", "g1_state": "ONE_SOURCE", "in_our_pool": None,
            "readings": [{"values": {"deaths_t": 621, "n_t": 2022, "deaths_c": 729, "n_c": 2094},
                          "sources": [dict(source=source, **kw)]}]}


def test_one_primary_source_is_primary_when_typed_and_never_when_reconstructed():
    # 2 Oct decision: ONE bound PRIMARY source verifies a row; the two-source rule is for metas. RECOVERY's own text
    # prints all four counts verbatim -> PRIMARY. Posted percentages turned into counts are a reconstruction -> no.
    span = ("Overall, 621 (31%) of the 2022 patients allocated tocilizumab and 729 (35%) of the 2094 patients "
            "allocated to usual care died within 28 days")
    assert gt.single_primary_source(_one_source("TEXT PMID 33933206", span=span))[0] is True
    assert gt.single_primary_source(_one_source("TEXT PMID 33933206", span=span.replace("729", "7290")))[1] == "COUNTS_NOT_IN_SPAN"
    pct = _one_source("AACT", derivation="survival 84% of 49 -> 8 deaths", time_frame="28 days")
    assert gt.single_primary_source(pct) == (False, "AACT_COUNTS_DERIVED_FROM_PERCENTAGE")
    multi = _one_source("AACT", derivation="posted participant counts", time_frame="Days 14, 28, and 60")
    assert gt.single_primary_source(multi) == (False, "AACT_MULTIPLE_TIME_FRAMES")
    o = {"trials": [_one_source("TEXT PMID 33933206", span=span)], "open_gaps": ["T"]}
    assert gt.apply_single_primary(o) == ["T"] and o["k_matched"] == 1 and o["open_gaps"] == []


def _srow(meta, state="SECONDARY_UNVERIFIED", prov="MODEL_PROPOSAL:mc-1"):
    from harness import secondary_meta as _sm
    r = _sm.SecondaryRow(meta_pmid=meta, meta_doi="", location={"kind": "figure", "id": "f1"}, source_digest="d" * 64,
                         provenance=prov, trial_label="T", measure="RR", outcome_definition="", effect="0.8",
                         lower="0.6", upper="1.0")
    r.state = state
    return r


def test_secondary_single_counts_one_self_reproducing_non_comparator_meta_only(monkeypatch):
    # Mahmood 3 Oct: with no open primary, ONE non-comparator meta's typed-admitted row counts (route SECONDARY_SINGLE);
    # the comparator's own row never does; a contradiction, an uncontrolled table or an open primary refuses it
    monkeypatch.setattr(gt, "primary_open", lambda slug, mine, t: [])
    metas = {"M": {"usable": True, "positive_control": {"reproduced": True}, "figure": "f1", "record_id": "mc-1"},
             "N": {"usable": False, "positive_control": {"reproduced": False}}}
    assert gt.secondary_single([_srow("C")], metas, {"C"}, "t", {}, {}) is None                 # comparator only
    ok = gt.secondary_single([_srow("M")], metas, {"C"}, "t", {}, {})
    assert ok["row"].meta_pmid == "M" and ok["provenance"]["meta_pmid"] == "M" and "queued for primary" in ok["basis"]
    assert gt.secondary_single([_srow("N")], metas, {"C"}, "t", {}, {})["why"] == "NO_ADMITTED_ROW_FROM_A_SELF_REPRODUCING_META"
    assert gt.secondary_single([_srow("M"), _srow("N", "MISMATCH")], metas, {"C"}, "t", {}, {})["why"].startswith("CONTRADICTED")
    assert "row" not in gt.secondary_single([_srow("M", prov="TYPED_TABLE_UNCONTROLLED")], metas, {"C"}, "t", {}, {})
    monkeypatch.setattr(gt, "primary_open", lambda slug, mine, t: ["OPEN_FULL_TEXT"])
    assert gt.secondary_single([_srow("M")], metas, {"C"}, "t", {}, {})["why"].startswith("PRIMARY_OPENLY_AVAILABLE")


def test_a_named_trial_is_never_matched_and_secondary_single_is_its_own_route_group():
    x = {"in_our_pool": False, "g1_countable": True, "route": "SECONDARY_SINGLE", "scope_difference": None}
    assert gt.is_matched(x) and gt.route_group("SWEEP_SECONDARY_SINGLE") == "SECONDARY_SINGLE"
    assert not gt.is_matched(dict(x, scope_difference={"kind": "PROTOCOL_SCOPE_DIFFERENCE"}))
    assert gt.route_group("SWEEP_META+AACT") == "PRIMARY" and gt.route_group("SWEEP_TWO_INDEPENDENT_METAS") == "TWO_SOURCE"


def test_g1r_reproduction_is_separate_from_g1():
    assert gt.g1r_reproduction({}, "C", [])["state"] == "NO_PER_TRIAL_ROWS"
    meta = {"positive_control": {"reproduced": True, "methods": ["FE"]}, "figure": "f2", "record_id": "mc-x"}
    assert gt.g1r_reproduction(meta, "C", [_srow("C")])["state"] == "REPRODUCED"
    assert gt.g1r_reproduction(dict(meta, positive_control={"reproduced": False}), "C", [_srow("C")])["state"] == "NOT_REPRODUCED"


def test_text_linked_figures_need_the_outcome_sentence_and_its_pooled_triple(monkeypatch):
    # a meta whose forest caption does not name the outcome: the body sentence naming the outcome, printing the effect
    # and citing 'Figure N' links figure N; the read's pooled triple must BE that sentence's triple
    assert sw._FIGREF.findall("all-cause mortality (RR 0.85, 95% CI 0.75-0.96; Fig. 2)") == ["2"]
    assert sw._NOT_FOREST.search("PRISMA flow diagram of study selection") and not sw._NOT_FOREST.search("Forest plot")
    import secondary_meta_build as smb
    from reproducible_ai import model_source as ms
    it = {"figure": {"fig_id": "f2"}, "link_sentence": "Mortality was lower (RR 0.85, 95% CI 0.75 to 0.96; Figure 2)."}
    monkeypatch.setattr(smb, "figure_rows", lambda *a, **k: ([_srow("M")], {"gate": "PASS"}))
    monkeypatch.setattr(ms, "load_record", lambda p: {})
    for pooled, ok in (({"effect": "0.85", "lower": "0.75", "upper": "0.96"}, True),
                       ({"effect": "0.80", "lower": "0.70", "upper": "0.91"}, False)):
        monkeypatch.setattr(ms, "replay", lambda rec, _p=pooled: json.dumps({"pooled": _p}).encode())
        rows, why = sw.ref_rows("t", it, {"record_id": "mc-1"}, {}, "C")
        assert bool(rows) is ok, why
        if ok:
            assert rows[0].outcome_definition.startswith("Mortality was lower")
        else:
            assert why == "POOLED_NOT_IN_LINKING_SENTENCE"


def test_counts_attach_only_when_they_reproduce_the_printed_effect():
    # tocilizumab: the figure prints RR, the protocol registers OR; counts read from the same figure are attached ONLY
    # when the RR they imply equals the row's printed RR (CORIMUNO-TOCI-1 7/63 vs 8/67 -> 0.93)
    ok, bad = _srow("M"), _srow("M")
    ok.trial_label, ok.effect = "CORIMUNO-TOCI-1", "0.93"
    bad.trial_label, bad.effect = "BACC Bay", "1.53"
    got = {"rows": [{"label": "CORIMUNO-TOCI-1", "events_t": "7", "n_t": "63", "events_c": "8", "n_c": "67"},
                    {"label": "BACC Bay", "events_t": "9", "n_t": "161", "events_c": "9", "n_c": "82"}]}
    assert sw.attach_counts([ok, bad], got) == 1
    assert (ok.events_t, ok.n_t, ok.events_c, ok.n_c) == (7, 63, 8, 67) and bad.events_t is None


def test_two_2x2_tables_compare_as_counts_whatever_ratio_label():
    theirs = _srow("C")
    theirs.measure, theirs.events_t, theirs.n_t, theirs.events_c, theirs.n_c = "OR", 26, 249, 11, 128
    assert gt.agreement({"measure": "RR", "events_t": 26, "n_t": 249, "events_c": 11, "n_c": 128}, theirs) == "AGREE"


def test_a_sweep_row_never_replaces_a_matched_trial_and_is_flagged_when_the_primary_contradicts(monkeypatch):
    v = {"measure": "RR", "effect": "0.89", "lower": "0.80", "upper": "0.99", "events_t": 596, "n_t": 2022,
         "events_c": 694, "n_c": 2094}
    monkeypatch.setattr(gt, "sweep_results", lambda slug: {
        "RECOVERY": {"label": "RECOVERY", "verdict": "SWEEP_SECONDARY_SINGLE", "value": v, "basis": {"meta": "33745918"}},
        "OPEN": {"label": "OPEN", "verdict": "SWEEP_SECONDARY_SINGLE", "value": v, "basis": {"meta": "33745918"}}})
    lane_matched = {"label": "RECOVERY", "in_our_pool": None, "g1_countable": True, "route": "PRIMARY"}
    contradicted = {"label": "OPEN", "in_our_pool": None, "route": "NO_ROW", "scope_difference": None,
                    "readings": [{"values": {"deaths_t": 621, "n_t": 2022, "deaths_c": 729, "n_c": 2094},
                                  "sources": [{"source": "TEXT PMID 33933206", "span": "621 ... 729"}]}]}
    assert gt.sweep_merge("t", [lane_matched, contradicted]) == []
    assert lane_matched["route"] == "PRIMARY"
    assert contradicted["secondary_single_flag"]["state"] == "CONTRADICTED_BY_PRIMARY"
