import json
from pathlib import Path
import pytest
from harness.identity_join import ROOT, identity, join, our_identities
from harness.inventory_queue import source, resolve
from harness.meta_match import match

@pytest.mark.parametrize("slug,label,key", [
    ("dapagliflozin-hfpef-hosp", "DELIVER", "dois"),
    ("pcsk9-mace", "GLAGOV", "ncts"),
    ("pcsk9-mace", "ODYSSEY LONG TERM", "ncts"),
])
def test_real_held_plants(slug, label, key):
    proposal, text, _ = source(slug, ROOT)
    row = next(r for r in proposal["trials"] if r["label"] == label)
    resolved, _, _, _ = resolve(row, text)
    # Isolate the named key, deriving its value exclusively from held bytes.
    field = {"dois":"doi", "ncts":"nct"}[key]
    value = resolved[field] or row.get("registration")
    assert value
    result = join({field:value}, our_identities(slug))
    assert result["status"] == "JOINED"
    assert result["key"] == key
    assert result["our_value"] == result["comparator_value"]


def test_shared_acronym_abstains_and_unique_negative():
    ours = [{"nct":"NCT11111111", "acronym":"ALPHA-ONE"},
            {"nct":"NCT22222222", "acronym":"Alpha One"}]
    assert join({"acronym":"alpha one"}, ours)["status"] == "AMBIGUOUS"
    assert join({"nct":"NCT11111111", "acronym":"alpha one"}, ours)["status"] == "JOINED"
    assert join({"acronym":"NEVER HELD"}, ours)["status"] == "NOT_JOINED"
    assert join({"acronym":"AB"}, [{"acronym":"AB"}])["status"] == "NOT_JOINED"


def test_conflict_refuses_weak_fallback_and_relayed():
    assert join({"nct":"NCT11111111", "acronym":"ALPHA"},
                [{"nct":"NCT22222222", "acronym":"ALPHA"}])["status"] == "NOT_JOINED"
    assert join({"doi":{"value":"10.1234/example", "status":"RELAYED"}},
                [{"doi":"10.1234/example"}])["status"] == "NOT_JOINED"
    assert join({"doi":"10.1234/EXAMPLE"}, [{"doi":"10.1234/example"}])["key"] == "dois"
    assert join({"label":"Smith 2020"}, [{"author":"Smith AB", "year":"2020"}])["key"] == "author_years"
    assert join({"label":"Smith 2020"}, [{"author":"Smith AB", "year":"2021"}])["status"] == "NOT_JOINED"


def test_held_unpooled_preserves_refusal_and_missing_negative():
    review = {"outcomes":[{"primary":True,"name":"Mortality","trials":[],
        "declared_absent_trials":[{"nct":"NCT11111111","reason_code":"NOT_EXTRACTED"}],
        "result":{"present":False}}]}
    comp = {"primary_outcome":"Mortality", "trial_set":[
        {"label":"ALPHA","nct":"NCT11111111","outcome":"Mortality"},
        {"label":"BETA","nct":"NCT22222222","outcome":"Mortality"}]}
    a,b = match(review, comp)["trials"]
    assert (a["status"], a["our_state"]) == ("IN_INVENTORY_UNPOOLED", "NOT_EXTRACTED")
    assert b["status"] == "MISSING_FROM_OURS"
    assert match(review,comp)["K_MATCH"] == "UNKNOWN"


def test_real_states():
    from scripts.g1_proposal_census import census
    result = census()
    rows = {t["slug"]+"::"+r["label"]:r for t in result["topics"] for r in t["trials"]}
    for item in ["dapagliflozin-hfpef-hosp::DELIVER", "pcsk9-mace::GLAGOV", "pcsk9-mace::ODYSSEY LONG TERM"]:
        assert rows[item]["status"] == "IN_INVENTORY_UNPOOLED"
        assert rows[item]["our_state"] != "NOT_IN_INVENTORY"
