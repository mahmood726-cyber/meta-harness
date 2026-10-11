"""V12-02Q / V12-03Q (Mahmood, 9 Oct, "yes all as recommended"; registry/v12_signatures.json, packet ae88366b...).

V12-02Q choice B: EFFECT-HF is left UNBOUND -- the 11 v 6 are safety-set patients and the safety-set N is not printed,
so there are no verbatim denominators. It supersedes D15's 11/86 v 6/86 FAS binding.
V12-03Q sign: EFFECT-HF's comparator finding COMPARATOR_COUNTS_ARE_EVENTS (its 13 v 13 are hospitalisations).
The plants read the committed registries: the binding must be gone, cannot be re-applied, and every SIGNED comparator
finding must resolve to a signature on record."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_final5_typed as T  # noqa: E402
import g1_tracker as gt  # noqa: E402


def _j(*p):
    return json.load(open(os.path.join(ROOT, *p), encoding="utf-8"))


def test_PLANT_v12_02q_effect_hf_is_not_admitted_in_the_acquisition_ledger():
    rows = [r for r in _j("registry", "g1_acquired", "iv-iron-hfref-hosp.json")["rows"] if r.get("label") == "EFFECT-HF [21]"]
    assert len(rows) == 1 and rows[0].get("verdict") != "ADMITTED" and not rows[0].get("admitted")
    assert "V12-02Q" in json.dumps(rows[0])


def test_PLANT_v12_02q_the_d15_binding_cannot_be_reapplied():
    row, why = T.effect_hf_row()
    assert row is None and "V12-02Q" in why


def test_PLANT_v12_03q_effect_hf_finding_is_signed_and_verifies():
    fs = [e for e in _j("registry", "g1_signed_comparator_findings.json")["findings"] if e["label"] == "EFFECT-HF"]
    assert len(fs) == 1 and fs[0]["state"] == "SIGNED" and fs[0]["decision"].startswith("V12-03Q")
    e = fs[0]
    assert gt._finding_check(e, {"comparator_row": dict(e["comparator_counts"])}, gt.ROOT) is None


def test_PLANT_every_signed_finding_resolves_to_a_signature_on_record():
    sig = _j("registry", "v12_signatures.json")["items"]
    dec = json.dumps(_j("registry", "g1_decisions.json"))
    for e in _j("registry", "g1_signed_comparator_findings.json")["findings"]:
        if e["state"] != "SIGNED":
            continue
        if e["decision"].startswith("V12-"):
            item = sig[e["decision"].split()[0]]
            assert item["state"] == "SEEN_AND_SIGNED" and item["choice"] == "sign", e["decision"]
        else:
            assert e["decision"].split()[0] == "D14" and "D14-CONFIRM-HF" in dec, e["decision"]


def test_PLANT_an_unbound_trial_still_carries_its_signed_finding():
    # unbound (no our_value, not matched): the finding is still named on the page, and no side is invented
    e = [e for e in _j("registry", "g1_signed_comparator_findings.json")["findings"] if e["label"] == "EFFECT-HF"][0]
    x = {"label": "EFFECT-HF [21]", "family": "PMID 28701470", "agreement_with_comparator_row": "NOT_IN_OUR_POOL",
         "comparator_row": {"events_t": 13, "n_t": 88, "events_c": 13, "n_c": 86, "measure": "OR"}}
    gt.signed_comparator_findings([x], "iv-iron-hfref-hosp")
    assert x["comparator_finding"]["state"] == "SIGNED" and x.get("disagreement_side") is None
    assert e["finding"] == "COMPARATOR_COUNTS_ARE_EVENTS"
