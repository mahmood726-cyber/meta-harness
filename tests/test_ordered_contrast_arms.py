"""Arm orientation (scripts/arm_orientation.py) and the scope of harness/armcontrast.py: eligibility is not direction (lane OC, 2026-09-25; external audit).

The auditor's armcontrast_direction_probe.py re-implemented contrast_status() with the standard library and showed its answer is
invariant to reversing the clinical orientation of an effect. Here the same question is asked of the REAL module: the claim
it supports is eligibility (the drug is part of the randomised difference); the orientation API retains which AACT group is
experimental and which is reference, as F4 arm ids, from the committed digest-bound row bodies."""
import json
import os
import shutil
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from harness import armcontrast as ac   # noqa: E402
import arm_orientation as ao            # noqa: E402  scripts/arm_orientation.py
import verify_bundle as vb              # noqa: E402

SLUG = "glp1-ra-mace-t2d"
TOPIC = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
AGENTS = sorted(TOPIC["intervention_agents"])


def test_auditor_probe_on_the_real_module_status_is_orientation_invariant_and_says_nothing_about_direction():
    """The probe's two claims (liraglutide/placebo HR 0.87 and placebo/liraglutide HR 0.87) reach contrast_status() identically,
    because it is never given an effect or an orientation. That is its scope -- ELIGIBILITY -- and this pins the scope, so no
    surface may cite it as evidence of direction."""
    index = {"NCT01179048": (set(), {"liraglutide"})}          # LEADER after placebo is normalised away, as measure_arm_index does
    canonical = ac.contrast_status("NCT01179048", ["liraglutide"], index)
    reversed_claim = ac.contrast_status("NCT01179048", ["liraglutide"], index)
    assert canonical == reversed_claim and canonical[0] == "verified"
    assert "direction" not in canonical[1].lower() and "numerator" not in canonical[1].lower()
    # the meaningful negative control the parser was built for: the drug in every arm, a different drug randomised
    assert ac.contrast_status("NCTBG", ["liraglutide"], {"NCTBG": ({"liraglutide"}, {"other_randomized_drug"})})[0] == "background_only"
    assert "does NOT establish which arm is the numerator" in ao.CLAIM_SCOPE


@pytest.fixture(scope="module")
def groups():
    return ao.load_arm_groups(SLUG, root=ROOT)


def test_leader_orientation_retains_group_ids_and_roles(groups):
    o = ao.oriented_contrast("NCT01179048", ["liraglutide"], groups)
    assert o["status"] == "verified" and o["group_type_witness"] == "AGREES"
    assert o["arm_ids"] == {"EXPERIMENTAL": ["NCT01179048:433876840"], "REFERENCE": ["NCT01179048:433876841"]}
    assert [g["group_type"] for g in o["experimental_arms"]] == ["EXPERIMENTAL"] and [g["group_type"] for g in o["reference_arms"]] == ["PLACEBO_COMPARATOR"]
    assert o["effect_direction"] == "NOT_ESTABLISHED_HERE" and o["claim_scope"] == ao.CLAIM_SCOPE


def test_multi_dose_trials_keep_every_group(groups):
    o = ao.oriented_contrast("NCT01720446", ["semaglutide"], groups)          # SUSTAIN-6: two doses, two matched placebos
    assert len(o["arm_ids"]["EXPERIMENTAL"]) == 2 and len(o["arm_ids"]["REFERENCE"]) == 2
    assert all("placebo" in g["title"].lower() for g in o["reference_arms"])      # 'Semaglutide placebo 0.5 mg' is REFERENCE


def test_two_independent_routes_to_the_arm_ids_agree_for_every_pooled_trial(groups):
    """Route 1: AACT coded interventions per design group (this module). Route 2: the certified families.json arm LABELS matched to
    the topic vocabulary (the verifier's family_arm_ids). Different inputs, same identities -- or the disagreement is named."""
    fams = {f["family_id"]: f for f in json.load(open(os.path.join(ROOT, "docs", "cache", SLUG, "families.json"), encoding="utf-8"))["families"]}
    bundle = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "BUNDLE.json"), encoding="utf-8"))
    vocab = vb.contrast_vocabulary(TOPIC)
    checked = 0
    for r in bundle["verification_rows"]:
        nct = r["trial"]["family_id"]
        o = ao.oriented_contrast(nct, AGENTS, groups)
        by_label = vb.family_arm_ids(fams[nct], vocab)
        assert o["status"] == "verified", (nct, o["status"])
        assert sorted(o["arm_ids"]["EXPERIMENTAL"]) == sorted(by_label["EXPERIMENTAL"]), nct
        assert sorted(o["arm_ids"]["REFERENCE"]) == sorted(by_label["REFERENCE"]), nct
        # and the served ordered contrast names the same F4 identities
        oc = r["analysis_identity"]["comparator_direction"]["ordered_contrast"]
        assert sorted(oc["experimental_arm"]["arm_ids"]) == sorted(o["arm_ids"]["EXPERIMENTAL"]), nct
        checked += 1
    assert checked == 8


def test_background_and_no_data_are_typed_never_oriented():
    synthetic = {"NCTBG": [{"arm_id": "NCTBG:1", "group_id": "1", "group_type": "EXPERIMENTAL", "title": "A", "active": ["drugx", "liraglutide"]},
                           {"arm_id": "NCTBG:2", "group_id": "2", "group_type": "ACTIVE_COMPARATOR", "title": "B", "active": ["liraglutide"]}]}
    o = ao.oriented_contrast("NCTBG", ["liraglutide"], synthetic)
    assert o["status"] == "background_only" and not o["experimental_arms"] and not o["reference_arms"]
    assert ao.oriented_contrast("NCTNONE", ["liraglutide"], synthetic)["status"] == "unverified_no_arm_data"


def test_a_group_type_disagreement_is_reported_not_resolved():
    synthetic = {"NCTX": [{"arm_id": "NCTX:1", "group_id": "1", "group_type": "PLACEBO_COMPARATOR", "title": "mislabelled", "active": ["drugx"]},
                          {"arm_id": "NCTX:2", "group_id": "2", "group_type": "EXPERIMENTAL", "title": "other", "active": []}]}
    o = ao.oriented_contrast("NCTX", ["drugx"], synthetic)
    assert o["status"] == "verified" and o["group_type_witness"].startswith("DISAGREES") and "NCTX:1" in o["group_type_witness"]


def test_a_row_body_that_does_not_hash_refuses_the_whole_load(tmp_path):
    src = os.path.join(ROOT, "docs", "acquisitions", SLUG)
    dst = tmp_path / "docs" / "acquisitions" / SLUG
    d = next(p for p in sorted(os.listdir(src)) if p.startswith("aact_rows_"))
    (dst / d).mkdir(parents=True)
    doc = json.load(open(os.path.join(src, d, "rows.json"), encoding="utf-8"))
    g = next(r for r in doc["tables"]["design_groups"] if r["keys"]["nct_id"] == "NCT01179048")
    g["row"]["group_type"] = "PLACEBO_COMPARATOR" if g["row"]["group_type"] == "EXPERIMENTAL" else "EXPERIMENTAL"   # swap a role, keep the digest
    (dst / d / "rows.json").write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(ao.ArmRowsRefused):
        ao.load_arm_groups(SLUG, root=str(tmp_path))
    shutil.rmtree(tmp_path, ignore_errors=True)
