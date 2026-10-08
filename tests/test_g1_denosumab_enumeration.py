"""PLANT: the denosumab comparator set, enumerated from the comparator's OWN supplementary trial table (PMID 36852077,
PMC9958453 mmc1), must reach the tracker through k_gap_table -- the tracker reads the comparator set ONLY from
k_gap_table, which said NOT_ENUMERABLE_OPEN (comparator N = 0). Requirement: comparator N = 11, 6 eligible (placebo-
controlled), the 5 active-controlled trials NAMED out of scope with a rule ID and the comparator's own row as span."""
import hashlib
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

SLUG = "denosumab-vertebral-fracture"
# the 36852077 enumeration is RETIRED with its comparator (replaced 2026-10-05 by 32492050): kept as a verifiable record
INPUT = os.path.join(ROOT, "registry", "comparator_enumerations", "retired", SLUG + ".36852077.json")


def test_enumeration_input_is_typed_units_with_ref_span_and_digest():
    e = json.load(open(INPUT, encoding="utf-8"))
    assert e["status"] == "ENUMERATED" and e["comparator_pmid"] == "36852077"
    src = os.path.join(ROOT, e["source"]["path"])
    digest = hashlib.sha256(open(src, "rb").read()).hexdigest()
    assert e["source"]["sha256"] == digest                       # the held source the spans are quoted from
    held = open(src, encoding="utf-8").read()
    assert len(e["units"]) == 11
    for u in e["units"]:
        assert u["label"] and u["ref"].isdigit() and u["pmid"].isdigit()
        for line in u["span"].split(" / "):
            assert line in held                                  # every span line verbatim in the held source
    assert sum(u["scope"] == "IN_SCOPE" for u in e["units"]) == 6


def test_k_gap_table_units_use_the_existing_schema():
    import k_gap_table as kt
    us = kt.enumeration_units(SLUG, ["denosumab"], "32492050")      # the CURRENT comparator's enumeration
    assert len(us) == 2
    assert kt.enumeration_units(SLUG, ["denosumab"], "36852077") == []   # never another comparator's
    keys = {"table", "layout", "label", "context", "rids", "cited", "ncts", "acronyms", "author", "year", "agent_hit",
            "drug_match", "design_stated"}
    assert all(keys <= set(u) for u in us)
    assert all(u["cited"] and u["cited"][0]["pmid"] for u in us)
    assert kt.set_state("SUPPLEMENT_ENUMERATION") == "ENUMERATED"


@pytest.mark.skipif(not os.path.exists(os.path.join(ROOT, "outputs", "k_gap", "_aact_store.json")),
                    reason="needs the local AACT store (gitignored cache)")
def test_tracker_shows_the_replacement_comparators_set():
    import k_gap_table as kt
    import g1_tracker as gt
    T = kt.main(["--offline", f"--only={SLUG}", "--no-write"])
    tp = next(t for t in T["topics"] if t["slug"] == SLUG)
    assert tp["comparator_set_state"] == "ENUMERATED" and tp["comparator_pmid"] == "32492050"
    o = gt.topic(SLUG, T)
    # V10-01 (signed 8 Oct, 'yes all v10'): Bone 2008 (PMID 18381571, T-score -1.0 to -2.5) is named by our protocol's
    # population span, so 1 of the 2 comparator trials is eligible
    assert o["N_comparator_trials"] == 2 and o["N_eligible"] == 1
    assert any("18381571" in json.dumps(d) for d in o["named_differences"])
    assert gt.scope_citation_violations(o) == []


def test_e2_named_difference_survives_cite_or_demote_only_when_re_derived():
    import g1_tracker as gt
    e = json.load(open(INPUT, encoding="utf-8"))
    u = next(x for x in e["units"] if x["scope"] == "OUT_OF_SCOPE")
    # the unit's ARMS ride with it exactly as k_gap_table.enumeration_units carries them: E2 needs a printed active control
    en = {"scope": u["scope"], "rule_id": u["rule_id"], "span": u["span"], "ref": u["ref"], "arms": u.get("arms"),
          "source": e["source"]["path"], "sha256": e["source"]["sha256"], "enumerated_from": e["enumerated_from"]}
    cfg = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    # without arms naming an active drug, the absence of 'placebo' names nothing (codex review g2#3)
    assert gt.enumeration_scope({"enumeration": dict(en, arms=None)}, cfg) is None

    def o_with(span_text):
        x = {"label": u["label"], "in_our_pool": False, "route": "NO_ROW", "enumeration": en}
        d = dict(gt.enumeration_scope(x, cfg), trial=u["label"])
        d["span"] = dict(d["span"], text=span_text)
        x["scope_difference"] = d
        return {"trials": [x], "named_differences": [d], "open_gaps": [], "N_eligible": 0, "k_matched": 0}

    kept = gt.cite_or_demote(o_with(u["span"]), SLUG)
    assert len(kept["named_differences"]) == 1 and kept["N_eligible"] == 0
    tampered = gt.cite_or_demote(o_with(u["span"].replace("Denosumab", "Placebo")), SLUG)
    assert tampered["named_differences"] == [] and tampered["N_eligible"] == 1
    # an enumeration whose held source digest changed names nothing
    assert gt.enumeration_scope({"enumeration": dict(en, sha256="0" * 64)}, cfg) is None
