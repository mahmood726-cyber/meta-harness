"""V12-11Q (Mahmood 9 Oct, 'yes all as recommended'): a served outcome is served on its REGISTERED estimand when a signed
effect-measure contract says so (external audit review 2 F1). Plants: the contract is honoured only when signed; without
one the old behaviour stands (never changed unsigned); RECOVERY's comparator arm N ('and 4321 to receive usual care') is
read, so its verbatim counts reach the OR."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import estimand_contract as ec  # noqa: E402
from harness import extract  # noqa: E402
from harness import source_hierarchy as sh  # noqa: E402

RR_ONLY = [{"effect": 0.83, "scale": "RR"}]
SPEC = {"name": "28-day all-cause mortality", "estimand": "OR"}
SIGNED = {"state": "SEEN_AND_SIGNED", "item": "V12-11Q", "by": "Mahmood", "quote": "q", "packet_sha256": "a" * 64,
          "item_section_sha256": "b" * 64}


def test_PLANT_a_declared_OR_falls_back_to_RR_without_a_signed_contract():
    d = sh.estimand_decision(SPEC, RR_ONLY)
    assert d["target_scale"] == "RR" and d["served_scale_changed"]


def test_PLANT_a_signed_contract_holds_the_registered_OR():
    d = sh.estimand_decision(SPEC, RR_ONLY, contract={"declared": "OR", "ratified": SIGNED})
    assert d["target_scale"] == "OR" and not d["served_scale_changed"] and "V12-11Q" in d["reason"]


def test_PLANT_an_unsigned_or_malformed_contract_is_never_honoured(tmp_path):
    p = tmp_path / "c.json"
    base = {"slug": "s", "outcome": "o", "declared": "OR"}
    for bad in ({}, dict(SIGNED, state="PROPOSED"), dict(SIGNED, packet_sha256="short"), dict(SIGNED, by="someone")):
        p.write_text(json.dumps({"contracts": [dict(base, ratified=bad)]}), encoding="utf-8")
        assert ec.signed("s", "o", path=str(p)) is None, bad
    p.write_text(json.dumps({"contracts": [dict(base, ratified=SIGNED)]}), encoding="utf-8")
    assert ec.signed("s", "o", path=str(p))["declared"] == "OR"
    assert ec.signed("s", "other", path=str(p)) is None


def test_the_committed_cortico_contract_is_signed_over_v12_11q():
    e = ec.signed("corticosteroids-covid19-mortality", "28-day all-cause mortality")
    assert e and e["ratified"]["item"] == "V12-11Q" and e["ratified"]["quote"] == "yes all as recommended"


def test_PLANT_the_comparator_arm_n_is_read_through_an_infinitive_ellipsis():
    ab = ("RESULTS: A total of 2104 patients were assigned to receive dexamethasone and 4321 to receive usual care. "
          "Overall, 482 patients (22.9%) in the dexamethasone group and 1110 patients (25.7%) in the usual care group "
          "died within 28 days after randomization (age-adjusted rate ratio, 0.83; 95% confidence interval [CI], 0.75 to 0.93).")
    assert extract._arm_ns(ab, ["dexamethasone"], ["usual care"]) == {"i": 2104, "c": 4321}
    r = extract.extract_trial(ab, ["died", "mortality"], ["dexamethasone"], ["usual care"], estimand="OR")
    assert (r["ai"], r["n1i"], r["ci"], r["n2i"]) == (482, 2104, 1110, 4321)
