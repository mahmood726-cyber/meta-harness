"""Identity links on main (scripts/g1_identity_links.py, reader side): a comparator unit cited by a report with no
registration in PubMed is joined to the registration we pool only through a committed link that rests on TWO typed facts
-- the report's own text states exactly one NCT, and an acronym in its title equals that NCT's registered acronym -- and
only to a registration already in our pool. The links are written by the k-gap lane (acq/k-gap 125802eb5); the builder's
own plants live there. The case: sacubitril-valsartan-hfref 'Tsutsui, 2021' (PMID 33731544) = PARALLEL-HF (NCT02468232)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_identity_links as L  # noqa: E402


def test_every_committed_link_rests_on_both_typed_facts_with_spans():
    links = L.load()
    assert links, "registry/identity_links.json is empty"
    for pmid, lk in links.items():
        rules = {r["rule"]: r for r in lk["rules"]}
        assert set(rules) == {"ONE_NCT_STATED_IN_OWN_REPORT", "TITLE_ACRONYM_EQUALS_REGISTRY_ACRONYM"}, pmid
        assert lk["nct"] in rules["ONE_NCT_STATED_IN_OWN_REPORT"]["span"], pmid
        assert rules["TITLE_ACRONYM_EQUALS_REGISTRY_ACRONYM"]["span"] in rules["TITLE_ACRONYM_EQUALS_REGISTRY_ACRONYM"]["title"]
        assert len(rules["ONE_NCT_STATED_IN_OWN_REPORT"]["text_sha256"]) == 64


def _link(nct, acro):
    return {"nct": nct, "rules": [
        {"rule": "ONE_NCT_STATED_IN_OWN_REPORT", "span": f"... Patients ({nct}). Study ...", "text_sha256": "a" * 64},
        {"rule": "TITLE_ACRONYM_EQUALS_REGISTRY_ACRONYM", "span": acro, "title": f"Results From the {acro} Study."}]}


def _unit(label, in_pool=False, route="NO_ROW"):
    return {"label": label, "in_our_pool": in_pool, "route": route}


def test_a_link_joins_only_to_a_registration_already_pooled():
    links = {"33731544": _link("NCT02468232", "PARALLEL-HF"), "999": _link("NCT09999999", "OTHER-HF")}
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


def test_PLANT_a_link_without_both_supporting_facts_never_joins():
    """codex idlink-r1 #1: join() accepted a PMID -> NCT link carrying zero supporting facts."""
    good = _link("NCT02468232", "PARALLEL-HF")
    bad = [{"nct": "NCT02468232", "rules": []},
           {"nct": "NCT02468232", "rules": good["rules"][:1]},
           {"nct": "NCT02468232", "rules": [good["rules"][0], dict(good["rules"][0])]},
           {"nct": "NCT02468232", "rules": [dict(good["rules"][0], span="... (NCT01111111) ..."), good["rules"][1]]},
           {"nct": "NCT02468232", "rules": [good["rules"][0], dict(good["rules"][1], span="OTHER")]}]
    for lk in bad:
        trials, rows = [_unit("Tsutsui, 2021")], [object()]
        got = L.join(trials, rows, {id(rows[0]): "33731544"}, {"NCT02468232": "NCT02468232"}, {"NCT02468232"}, set(),
                     {"NO_ROW": 1}, {"33731544": lk})
        assert got == [] and not trials[0]["in_our_pool"], lk
    assert L.supported(good)


def test_PLANT_a_missing_links_file_is_an_error_not_no_links(tmp_path):
    """codex idlink-r1 #2: a missing file read as an empty set of links."""
    import pytest
    with pytest.raises(FileNotFoundError):
        L.load(str(tmp_path / "identity_links.json"))
