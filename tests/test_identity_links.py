"""Identity links (scripts/g1_identity_links.py): a comparator unit cited by a report with no registration in PubMed is
joined to the registration we pool only on TWO typed facts -- the report's own text states exactly one NCT, and an
acronym in its title equals that NCT's registered acronym -- and only to a registration already in our pool.
The case: sacubitril-valsartan-hfref 'Tsutsui, 2021' (PMID 33731544) = PARALLEL-HF (NCT02468232)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_identity_links as L  # noqa: E402

TITLE = ("Efficacy and Safety of Sacubitril/Valsartan in Japanese Patients With Chronic Heart Failure and Reduced "
         "Ejection Fraction - Results From the PARALLEL-HF Study.")
TEXT = "... was conducted in Japanese HFrEF Patients (NCT02468232). Study Population ..."


def acr(nct):
    return {"NCT02468232": ("PARALLEL-HF", "sha")}.get(nct, (None, "sha"))


def test_both_facts_make_a_link():
    v = L.decide("33731544", TITLE, TEXT, "open copy", acr)
    assert v["nct"] == "NCT02468232" and [r["rule"] for r in v["rules"]] == \
        ["ONE_NCT_STATED_IN_OWN_REPORT", "TITLE_ACRONYM_EQUALS_REGISTRY_ACRONYM"]
    assert "NCT02468232" in v["rules"][0]["span"] and v["rules"][1]["span"] == "PARALLEL-HF"


def test_one_fact_is_never_enough():
    # a report citing another trial's registration beside its own: several ids -> refused
    assert "SEVERAL_NCT" in L.decide("1", TITLE, TEXT + " as in PARADIGM-HF (NCT01035255)", "c", acr)["refused"]
    # the stated NCT's registered acronym is not in the title -> refused
    assert "TITLE_ACRONYM_NOT" in L.decide("1", "A trial of something in Japan", TEXT, "c", acr)["refused"]
    assert L.decide("1", TITLE, "", None, acr)["refused"] == "NO_OPEN_REPORT_TEXT"


def _unit(label, in_pool=False, route="NO_ROW"):
    return {"label": label, "in_our_pool": in_pool, "route": route}


def test_a_link_joins_only_to_a_registration_already_pooled():
    links = {"33731544": {"nct": "NCT02468232", "rules": [{"rule": "A"}, {"rule": "B"}]},
             "999": {"nct": "NCT09999999", "rules": [{"rule": "A"}, {"rule": "B"}]}}
    trials = [_unit("Tsutsui, 2021"), _unit("Other"), _unit("Pooled", in_pool=True, route="PRIMARY")]
    rows = [object(), object(), object()]
    rp = {id(rows[0]): "33731544", id(rows[1]): "999", id(rows[2]): "33731544"}
    routes = {"NO_ROW": 2, "PRIMARY": 1}
    matched = set()
    got = L.join(trials, rows, rp, {"NCT02468232": "NCT02468232"}, {"NCT02468232", "PMID 25176015"}, matched, routes,
                 links)
    assert [g[0]["label"] for g in got] == ["Tsutsui, 2021"]
    assert trials[0]["in_our_pool"] and trials[0]["family"] == "NCT02468232" and trials[0]["route"] == "PRIMARY"
    assert not trials[1]["in_our_pool"]                        # its registration is not in our pool: nothing added
    assert routes == {"NO_ROW": 1, "PRIMARY": 2}
    # a pool row already matched by another unit is never matched twice
    t2 = [_unit("Again")]
    r2 = [object()]
    assert L.join(t2, r2, {id(r2[0]): "33731544"}, {"NCT02468232": "NCT02468232"}, {"NCT02468232"}, matched,
                  {"NO_ROW": 1}, links) == []
