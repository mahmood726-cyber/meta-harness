"""PLANTS for the defects a cross-vendor review (codex, 2 Oct) found in the shared G1 machinery. Each was REPRODUCED by
execution on the pre-fix code before it was fixed; each test below is that reproduction, asserting the requirement.
One finding was refuted and is recorded in kgap/G1_INTERFACES.md (agreement at the coarser printed precision)."""
import json
import os

import pytest

from harness import secondary_meta as sm
from kgap import runs_store


def R(**k):
    d = dict(meta_pmid="1", meta_doi="", location={}, source_digest="d", provenance="T", trial_label="X", measure="HR",
             outcome_definition="", effect="0.80", lower="0.70", upper="0.90")
    d.update(k)
    return sm.SecondaryRow(**d)


# ---------------------------------------------------------------- independence / two-source / anti-circularity

def test_single_quoted_pub_id_attributes_are_read():
    assert sm.cited_ids_from_jats(b"<ref-list><ref><pub-id pub-id-type='pmid'>2</pub-id></ref></ref-list>") == {"2"}


def test_same_meta_by_doi_is_not_two_sources():
    a = R(meta_pmid="1", meta_doi="10.1/X", source_digest="a")
    b = R(meta_pmid="", meta_doi="10.1/x", source_digest="b")
    assert sm.independence(a, b, lambda m: set(), set()) == "SAME_META"


def test_common_cited_meta_is_caught_across_identifier_types():
    refs = {"1": {"3"}, "2": {"10.1234/third"}}
    a, b = R(meta_pmid="1", source_digest="a"), R(meta_pmid="2", source_digest="b")
    assert sm.independence(a, b, refs.get, [{"3", "10.1234/third"}]).startswith("COMMON_CITED_META")
    assert sm.independence(a, b, refs.get, {"3"}) is None           # without the alias the PMID alone cannot see it


def test_two_source_requires_the_same_typed_tuple_not_just_the_same_numbers():
    refs = {"1": set(), "2": set()}
    for k, v1, v2 in (("timepoint", "28 days", "90 days"), ("population", "intention-to-treat", "per-protocol"),
                      ("arm_dose", "10 mg", "20 mg")):
        a = R(meta_pmid="1", family_id="F", source_digest="a", verification={"queue_reason": "Q"}, **{k: v1})
        b = R(meta_pmid="2", family_id="F", source_digest="b", verification={"queue_reason": "Q"}, **{k: v2})
        sm.two_source([a, b], refs.get, set())
        assert a.state == b.state == sm.UNVERIFIED, k
    a = R(meta_pmid="1", family_id="F", source_digest="a", timepoint="28 days")
    b = R(meta_pmid="2", family_id="F", source_digest="b")                 # unstated on one side: not a difference
    sm.two_source([a, b], refs.get, set())
    assert a.state == sm.TWO_SOURCE


def test_g1_comparator_ids_compare_case_insensitively_and_by_any_alias():
    c = R(meta_pmid="9", meta_doi="10.1234/ABC", state=sm.VERIFIED)
    assert sm.g1_countable([c], {"10.1234/abc"}) == []
    a = R(meta_pmid="1", meta_doi="10.1234/one", family_id="F", source_digest="a")
    b = R(meta_pmid="2", family_id="F", source_digest="b")
    sm.two_source([a, b], {"1": set(), "2": set()}.get, set())
    assert b.state == sm.TWO_SOURCE
    assert sm.g1_countable([b], {"10.1234/ONE"}) == []                     # its only pair includes the comparator


# ---------------------------------------------------------------- registry matching

def test_one_registry_group_cannot_be_both_arms():
    reg = {"outcomes": {"o": {"title": "mortality"}}, "analyses": [],
           "groups": {"o": [{"group": "g", "count": 10, "n": 100}]}}
    r = R(measure="RR", effect=None, lower=None, upper=None, events_t=10, n_t=100, events_c=10, n_c=100)
    assert sm.typed_match_registry(r, reg, ["mortality"], "x") is None
    reg["groups"]["o"].append({"group": "h", "count": 10, "n": 100})
    assert sm.typed_match_registry(r, reg, ["mortality"], "x")["result"] == "TYPED_MATCH"


def test_a_missing_registry_count_does_not_crash_a_match():
    reg = {"outcomes": {"o": {"title": "mortality"}}, "analyses": [],
           "groups": {"o": [{"group": "g", "count": 10, "n": 100}, {"group": "h", "count": 20, "n": 100},
                            {"group": "i", "count": None, "n": 100}]}}
    r = R(measure="RR", effect=None, lower=None, upper=None, events_t=10, n_t=100, events_c=20, n_c=100)
    assert sm.typed_match_registry(r, reg, ["mortality"], "x")["result"] == "TYPED_MATCH"


def test_fractional_follow_up_is_read_whole():
    assert sm._days("0.5 years") == 182.5 and sm._days("5 years") == 1825 and sm._days("28-day") == 28
    assert sm.registry_vs_publication(R(timepoint="0.5 years"), {"time_frame": "5 years"})[0]["field"] == "timepoint"


# ---------------------------------------------------------------- typed tables and pooling

def test_reversed_or_zero_width_ci_is_not_a_poolable_row():
    assert sm.row_yi_vi(R(effect="0.80", lower="0.90", upper="0.70")) is None
    assert sm.row_yi_vi(R(effect="0.80", lower="0.80", upper="0.80")) is None
    assert sm.row_yi_vi(R(effect="0.95", lower="0.70", upper="0.90")) is None   # point outside its own CI
    assert sm.row_yi_vi(R()) is not None


def test_pooled_sentence_needs_the_term_to_govern_the_numbers():
    pooled = {"effect": "-5.00", "lower": "-7.00", "upper": "-3.00"}
    other = "Weight loss was assessed, but systolic blood pressure decreased (mean difference: -5.00; 95% CI: -7.00 to -3.00)."
    assert sm.pooled_sentence(other, pooled, ["weight loss"]) is None
    own = "Semaglutide produced greater weight loss than placebo (mean difference: -5.00%; 95% CI: -7.00 to -3.00)."
    assert sm.pooled_sentence(own, pooled, ["weight loss"])


def test_count_columns_take_arm_order_from_the_header():
    def jats(h1, h2):
        rows = "<tr><td>A</td><td>20/100</td><td>10/100</td></tr><tr><td>Overall</td><td>x</td><td>0.50 (0.25-1.00)</td></tr>"
        return (f"<article><table-wrap id='T'><caption><p>Risk ratio of death</p></caption><table><thead><tr><th>Study</th>"
                f"<th>{h1}</th><th>{h2}</th></tr></thead><tbody>{rows}</tbody></table></table-wrap></article>").encode()
    r = sm.typed_rows_from_jats(jats("Placebo n/N", "Drug n/N"), "m")[0]["rows"][0]
    assert (r.events_t, r.events_c, r.findings) == (10, 20, [])                 # control named first -> swapped
    r = sm.typed_rows_from_jats(jats("Drug n/N", "Placebo n/N"), "m")[0]["rows"][0]
    assert (r.events_t, r.events_c, r.findings) == (20, 10, [])
    r = sm.typed_rows_from_jats(jats("Group 1", "Group 2"), "m")[0]["rows"][0]
    assert r.findings == [{"finding": "ARM_ORDER_FROM_COLUMN_ORDER"}]           # unknown order is recorded, not hidden


# ---------------------------------------------------------------- AACT adapter

def _snap(tmp_path, measurements, counts):
    snap = tmp_path / "snap"
    snap.mkdir()
    files = {"outcomes.txt": "id|nct_id|outcome_type|title|time_frame|population|units_analyzed\no1|NCT1|PRIMARY|Death|Day 28|||\n",
             "outcome_analyses.txt": "id|nct_id|outcome_id|param_type|param_value|ci_lower_limit|ci_upper_limit\n",
             "outcome_measurements.txt": "id|nct_id|outcome_id|result_group_id|units|param_type|param_value_num|category|classification\n"
                                         + measurements,
             "outcome_counts.txt": "id|nct_id|outcome_id|result_group_id|scope|units|count\n" + counts,
             "result_groups.txt": "id|nct_id|ctgov_group_code|result_type|title|outcome_id\n",
             "outcome_analysis_groups.txt": "id|nct_id|outcome_analysis_id|result_group_id|ctgov_group_code\n"}
    for f, body in files.items():
        (snap / f).write_text(body, encoding="utf-8")
    return snap


def _ensure(monkeypatch, tmp_path, snap):
    from kgap import aact_adapter as aa
    monkeypatch.setenv("AACT_SNAPSHOT", str(snap))
    monkeypatch.setenv("KGAP_AACT_INDEX", str(tmp_path / f"idx_{snap.name}.json"))
    monkeypatch.setattr(aa, "DIGEST_CACHE", str(tmp_path / "digest.json"))
    aa._CACHE.clear()
    return aa, aa.ensure(["NCT1"])


def test_a_percentage_is_never_an_event_count(tmp_path, monkeypatch):
    snap = _snap(tmp_path, "m1|NCT1|o1|g1|percentage of patients|NUMBER|63.6||\n"
                           "m2|NCT1|o1|g2|Participants|COUNT_OF_PARTICIPANTS|12||\n",
                 "c1|NCT1|o1|g1|Measure|Participants|44\nc2|NCT1|o1|g2|Measure|Participants|40\n")
    aa, _ = _ensure(monkeypatch, tmp_path, snap)
    assert aa.registry_for("NCT1")["groups"]["o1"] == [{"group": "g2", "count": 12, "n": 40}]


def test_a_non_people_denominator_is_never_the_arm_n(tmp_path, monkeypatch):
    snap = _snap(tmp_path, "m1|NCT1|o1|g1|Participants|COUNT_OF_PARTICIPANTS|10||\n",
                 "c1|NCT1|o1|g1|Measure|Participants|37\nc2|NCT1|o1|g1|Measure|Patient-months|920\n")
    aa, _ = _ensure(monkeypatch, tmp_path, snap)
    assert aa.registry_for("NCT1")["groups"]["o1"] == [{"group": "g1", "count": 10, "n": 37}]


def test_two_snapshot_directories_never_share_a_cached_identity(tmp_path, monkeypatch):
    from kgap import aact_adapter as aa
    a = _snap(tmp_path, "m1|NCT1|o1|g1|Participants|COUNT_OF_PARTICIPANTS|10||\n", "")
    b = tmp_path / "other" / "snap"
    b.parent.mkdir()
    b.mkdir()
    for f in os.listdir(a):
        body = (a / f).read_text(encoding="utf-8")
        (b / f).write_text(body.replace("|10||", "|11||"), encoding="utf-8")   # same size, different content
        st = os.stat(a / f)
        os.utime(b / f, (st.st_atime, st.st_mtime))                             # same mtime
    monkeypatch.setattr(aa, "DIGEST_CACHE", str(tmp_path / "digest.json"))
    monkeypatch.setenv("AACT_SNAPSHOT", str(a))
    da = aa.snapshot()["digest"]
    monkeypatch.setenv("AACT_SNAPSHOT", str(b))
    assert aa.snapshot()["digest"] != da
    assert "dir_sha256" in json.load(open(tmp_path / "digest.json")) and str(tmp_path) not in open(tmp_path / "digest.json").read()


def test_an_index_built_under_older_rules_is_rebuilt(tmp_path, monkeypatch):
    from kgap import aact_adapter as aa
    snap = _snap(tmp_path, "m1|NCT1|o1|g1|Participants|COUNT_OF_PARTICIPANTS|10||\n", "")
    aa_, st = _ensure(monkeypatch, tmp_path, snap)
    assert st["snapshot"]["rules"] == aa.INDEX_RULES
    idx = json.load(open(aa.index_path()))
    idx["NCT1"]["_snapshot"] = {k: v for k, v in idx["NCT1"]["_snapshot"].items() if k != "rules"}
    json.dump(idx, open(aa.index_path(), "w"))
    aa._CACHE.clear()
    assert aa.ensure(["NCT1"])["rebuilt_stale"] == 1


# ---------------------------------------------------------------- run ledger

def test_a_stale_caller_never_deletes_entries_saved_in_between(tmp_path, monkeypatch):
    monkeypatch.setattr(runs_store, "RUNS_DIR", str(tmp_path))
    runs_store.save({"a::1": {"s": 1}, "b::1": {"s": 1}})
    stale = runs_store.load()
    other = runs_store.load()
    other["b::2"] = {"s": 2}
    runs_store.save(other, slugs={"b"})                  # another process adds b::2
    stale["a::2"] = {"s": 2}
    runs_store.save(stale)                               # the stale caller saves everything it holds
    got = runs_store.load()
    assert "b::2" in got and "a::2" in got and len(got) == 4


def test_a_failing_build_still_ledgers_its_completed_calls(monkeypatch):
    import sys
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
    import secondary_meta_build as smb
    saved = []

    def failing_build(s, run, runs):
        runs[s + "::1"] = {"state": "RAN_OK"}
        raise RuntimeError("queue invariant")
    monkeypatch.setattr(smb, "build", failing_build)
    monkeypatch.setattr(smb.runs_store, "load", lambda: {})
    monkeypatch.setattr(smb.runs_store, "save", lambda runs, slugs=None: saved.append(dict(runs)))
    with pytest.raises(RuntimeError):
        smb.main(["topic-a"])
    assert saved and "topic-a::1" in saved[0]
