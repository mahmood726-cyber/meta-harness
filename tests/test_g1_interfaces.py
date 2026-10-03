"""SHARED G1 INTERFACES (acq/k-gap): other lanes build NOAC, tocilizumab and the forest-plot reader on top of these.
Each test pins one contract; changing it must be a deliberate, announced interface change, never a side effect.
See kgap/G1_INTERFACES.md."""
import inspect
import json
import os

import pytest

from harness import secondary_meta as sm
from kgap import runs_store

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_verification_states_and_routes_are_stable():
    assert (sm.UNVERIFIED, sm.VERIFIED, sm.TWO_SOURCE, sm.MISMATCH, sm.BLOCKED, sm.REFUSED) == (
        "SECONDARY_UNVERIFIED", "PRIMARY_VERIFIED", "TWO_SOURCE_VERIFIED", "MISMATCH", "BLOCKED_CROSSCHECK", "REFUSED")
    r = sm.SecondaryRow(meta_pmid="1", meta_doi="", location={}, source_digest="", provenance="TYPED_TABLE",
                        trial_label="X", measure="HR", outcome_definition="")
    for state, route in ((sm.VERIFIED, "PRIMARY"), (sm.TWO_SOURCE, "TWO_SOURCE"), (sm.UNVERIFIED, "UNVERIFIED"),
                         (sm.MISMATCH, "UNVERIFIED"), (sm.BLOCKED, "UNVERIFIED")):
        r.state = state
        assert sm.route_of(r) == route


@pytest.mark.parametrize("fn,params", [
    (sm.verify_typed, ["row", "sources", "outcome_terms"]),
    (sm.typed_match_text, ["row", "text", "outcome_terms", "source_ref"]),
    (sm.typed_match_registry, ["row", "registry", "outcome_terms", "source_ref"]),
    (sm.verify_against_primary, ["row", "primary", "queue_reason"]),
    (sm.two_source, ["rows", "refs_of", "known_metas"]),
    (sm.independence, ["a", "b", "refs_of", "known_metas"]),
    (sm.g1_countable, ["rows", "comparator_meta_ids"]),
    (sm.cited_ids_from_jats, ["jats"]),
    (sm.registry_fields, ["registry", "outcome_id", "analysis"]),
    (sm.registry_vs_publication, ["row", "outcome"]),
    (sm.queue_complete, ["rows"]),
    (sm.positive_control, ["rows", "printed", "measure"]),
])
def test_function_signatures_are_stable(fn, params):
    assert list(inspect.signature(fn).parameters)[:len(params)] == params


def test_every_primary_verification_names_its_route():
    row = sm.SecondaryRow(meta_pmid="1", meta_doi="", location={}, source_digest="", provenance="TYPED_TABLE",
                          trial_label="LEADER", measure="HR", outcome_definition="MACE",
                          effect="0.87", lower="0.78", upper="0.97")
    sm.verify_against_primary(row, {"measure": "HR", "effect": "0.87", "lower": "0.78", "upper": "0.97",
                                    "source": "x", "span": "HR 0.87 (0.78-0.97)"})
    assert row.state == sm.VERIFIED and row.verification["route"] == "PRIMARY_EXTRACTION"
    t = sm.SecondaryRow(**{**row.to_dict(), "state": sm.UNVERIFIED, "verification": None})
    sm.verify_typed(t, [("text", "abs", "MACE occurred: hazard ratio, 0.87; 95% CI, 0.78 to 0.97")], ["MACE"])
    assert t.verification["route"] == "PRIMARY_TEXT"


def test_aact_adapter_entry_shape_and_fail_closed(tmp_path, monkeypatch):
    from kgap import aact_adapter as aa
    monkeypatch.setenv("AACT_SNAPSHOT", str(tmp_path / "missing"))
    with pytest.raises(FileNotFoundError):
        aa.snapshot_dir()                               # never an empty registry from a missing snapshot
    snap = tmp_path / "snap"
    snap.mkdir()
    rows = {"outcomes.txt": "id|nct_id|outcome_type|title|time_frame|population|units_analyzed\n"
                            "o1|NCT1|PRIMARY|All-cause mortality|Day 28|ITT||\n",
            "outcome_analyses.txt": "id|nct_id|outcome_id|param_type|param_value|ci_lower_limit|ci_upper_limit\n",
            "outcome_measurements.txt": "id|nct_id|outcome_id|result_group_id|units|param_type|param_value_num|category|"
                                        "classification\n"
                                        "m1|NCT1|o1|g1|Participants|COUNT_OF_PARTICIPANTS|10|||\n"
                                        "m2|NCT1|o1|g2|Participants|COUNT_OF_PARTICIPANTS|20||\n",
            "outcome_counts.txt": "id|nct_id|outcome_id|result_group_id|scope|units|count\n"
                                  "c1|NCT1|o1|g1|Measure|Participants|100\nc2|NCT1|o1|g2|Measure|Participants|100\n",
            "result_groups.txt": "id|nct_id|ctgov_group_code|result_type|title|outcome_id\n"
                                 "g1|NCT1|OG000|Outcome|Drug|o1\ng2|NCT1|OG001|Outcome|Placebo|o1\n",
            "outcome_analysis_groups.txt": "id|nct_id|outcome_analysis_id|result_group_id|ctgov_group_code\n"}
    for f, body in rows.items():
        (snap / f).write_text(body, encoding="utf-8")
    monkeypatch.setenv("AACT_SNAPSHOT", str(snap))
    monkeypatch.setenv("KGAP_AACT_INDEX", str(tmp_path / "idx.json"))
    monkeypatch.setattr(aa, "DIGEST_CACHE", str(tmp_path / "digest.json"))
    aa._CACHE.clear()
    st = aa.ensure(["NCT1", "NCT2"])
    e = aa.registry_for("NCT1")
    assert set(e) == {"_snapshot", "outcomes", "analyses", "groups", "group_titles"}
    assert e["_snapshot"] == st["snapshot"] and e["_snapshot"]["id"] == "AACT snap"
    assert e["outcomes"]["o1"]["population"] == "ITT" and e["group_titles"] == {"g1": "Drug", "g2": "Placebo"}
    assert sorted((g["count"], g["n"]) for g in e["groups"]["o1"]) == [(10, 100), (20, 100)]
    assert aa.registry_for("NCT2") is None              # indexed, nothing posted
    assert aa.ensure(["NCT1"])["added"] == 0            # incremental: nothing re-read
    (snap / "outcomes.txt").write_text(rows["outcomes.txt"] + "o2|NCT1|SECONDARY|Stroke|1 year|||\n", encoding="utf-8")
    aa._CACHE.clear()
    assert aa.ensure(["NCT1"])["rebuilt_stale"] == 2    # a changed snapshot never mixes with the old index


def test_runs_store_is_one_file_per_topic_and_lossless(tmp_path, monkeypatch):
    monkeypatch.setattr(runs_store, "RUNS_DIR", str(tmp_path))
    runs = {"glp1-ra-mace-t2d::34526024": {"state": "RAN_OK"}, "locate::noac-vs-warfarin-af-stroke::1": {"state": "X"},
            "weird key": {"state": "Y"}}
    runs_store.save(runs)
    assert sorted(os.listdir(tmp_path)) == ["_other.json", "glp1-ra-mace-t2d.json", "noac-vs-warfarin-af-stroke.json"]
    assert runs_store.load() == runs
    runs["glp1-ra-mace-t2d::1"] = {"state": "RAN_OK"}
    runs["locate::noac-vs-warfarin-af-stroke::2"] = {"state": "RAN_OK"}
    wrote = runs_store.save(runs, slugs={"glp1-ra-mace-t2d"})          # a GLP-1 build never rewrites the NOAC file
    assert [os.path.basename(p) for p in wrote] == ["glp1-ra-mace-t2d.json"]


def test_committed_tracker_files_carry_the_pinned_schema():
    d = os.path.join(ROOT, "outputs", "k_gap", "g1")
    keys = {"schema_version", "slug", "comparator_pmid", "N_comparator_trials", "k_matched", "k_ours_total", "routes",
            "trials", "per_trial_agreement", "same_trials", "ours", "comparator", "ours_not_in_comparator"}
    files = [f for f in os.listdir(d) if f.endswith(".json")] if os.path.isdir(d) else []
    assert files, "no committed tracker files"
    for f in files:
        with open(os.path.join(d, f), encoding="utf-8") as fh:
            o = json.load(fh)
        assert keys <= set(o), (f, keys - set(o))
        assert set(o["routes"]) <= {"PRIMARY", "TWO_SOURCE", "UNVERIFIED", "NO_ROW"}
        assert sum(o["routes"].values()) == o["N_comparator_trials"] == len(o["trials"])


def test_same_trials_result_verdict_is_typed():
    import sys
    sys.path.append(os.path.join(ROOT, "scripts"))
    import g1_tracker as gt
    v = gt.result_verdict({"estimate": 0.85, "ci_low": 0.80, "ci_high": 0.90},
                          {"estimate": 0.85, "ci_low": 0.80, "ci_high": 0.90}, "HR")
    assert v["verdict"] == "AGREE" and v["conclusion"] == "BENEFIT"
    v = gt.result_verdict({"estimate": 0.85, "ci_low": 0.70, "ci_high": 1.02},
                          {"estimate": 0.85, "ci_low": 0.80, "ci_high": 0.90}, "HR")
    assert v["verdict"] == "DIFFERENT_CONCLUSION"                       # one crosses the null, the other does not
    v = gt.result_verdict({"estimate": -10.0, "ci_low": -12.0, "ci_high": -8.0},
                          {"estimate": -11.5, "ci_low": -13.5, "ci_high": -9.5}, "MD")
    assert v["verdict"] == "SAME_CONCLUSION_DIFFERENT_ESTIMATE" and v["estimate_gap_over_ci_halfwidth"] == 0.75


def test_a_registry_outcome_title_is_gated_as_a_composite_definition():
    # ELIXA (NCT01147250): its 5- and 6-component posted secondaries passed the composite gate as bindable 3-point MACE,
    # because the gate reads only spans that say 'composite'/'primary' and a registry title says neither
    import sys
    sys.path.append(os.path.join(ROOT, "scripts"))
    import g1_tracker as gt
    name = "3-point major adverse cardiovascular events"
    for t in ("Time to First Occurence of CV Event: CV Death, Non-Fatal MI, Non-Fatal Stroke, Hospitalization for "
              "Unstable Angina or Hospitalization For Heart Failure",
              "Time to First Occurence of Primary CV Event: CV Death, Non-Fatal MI, Non-Fatal Stroke or Hospitalization "
              "for Unstable Angina"):
        assert gt.definition_gate(name, t)
    assert not gt.definition_gate(name, "Time to First Occurrence of MACE: CV Death, Non-Fatal MI or Non-Fatal Stroke")


def test_every_served_topic_has_a_tracker_row():
    # denosumab-vertebral-fracture had NO tracker file and no stated reason (3 Oct): a silent omission. Every served
    # topic must have a row; one whose comparator lists no enumerable trial states COMPARATOR_NOT_ENUMERATED.
    served = sorted(s for s in os.listdir(os.path.join(ROOT, "docs", "reviews"))
                    if os.path.exists(os.path.join(ROOT, "docs", "reviews", s, "review.json")))
    have = {f[:-5] for f in os.listdir(os.path.join(ROOT, "outputs", "k_gap", "g1")) if f.endswith(".json")}
    assert sorted(set(served) - have) == []
    for s in served:
        with open(os.path.join(ROOT, "outputs", "k_gap", "g1", f"{s}.json"), encoding="utf-8") as fh:
            o = json.load(fh)
        assert (o.get("g1_status") or {}).get("state"), s
        if not o["N_comparator_trials"]:
            assert o["g1_status"]["state"] == "COMPARATOR_NOT_ENUMERATED" and o["g1_status"].get("why"), s


def test_the_canonical_tracker_json_is_keyed_not_positional():
    """outputs/k_gap/G1_TRACKER.json is the canonical machine-readable output: every topic carries exactly TOPIC_KEYS;
    totals equal the sums of the topics; no consumer parses the markdown table by column position."""
    import json as _json
    import sys as _sys
    _sys.path.append(os.path.join(ROOT, "scripts"))
    import g1_tracker as _gt
    p = os.path.join(ROOT, "outputs", "k_gap", "G1_TRACKER.json")
    d = _json.load(open(p, encoding="utf-8"))
    assert d["schema"] == _gt.CANONICAL_SCHEMA and d["topic_keys"] == list(_gt.TOPIC_KEYS)
    assert set(d["topics"]) == set(_gt.served_topics())
    for slug, t in d["topics"].items():
        assert set(t) == set(_gt.TOPIC_KEYS), slug
        assert t["N_comparator_trials"] - t["N_eligible"] == t["excluded_by_scope"], slug
    assert d["totals"]["k_matched"] == sum(t["k_matched"] for t in d["topics"].values())
