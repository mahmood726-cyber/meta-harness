import copy
import json
import pathlib
import subprocess

from harness import claimgraph
from harness import propositions as P


ROOT = pathlib.Path(__file__).resolve().parents[1]
PREFIX = "ad5e7c66"


def _git_json(ref, path):
    data = subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT)
    return json.loads(data)


def _review(slug, ref=PREFIX):
    return _git_json(ref, f"docs/reviews/{slug}/review.json")


def _codes(violations):
    return {v["code"] for v in violations}


def test_PLANT_publication_bias_state_fires_on_prefix_objects():
    for slug in [
        "sglt2-ckd-progression",
        "colchicine-secondary-cv-prevention",
        "metformin-pcos-ovulation",
    ]:
        violations = P.check_propositions(_review(slug))
        assert "PUBLICATION_BIAS_STATE" in _codes(violations), (slug, violations)
        hit = next(v for v in violations if v["code"] == "PUBLICATION_BIAS_STATE")
        assert hit["asserted_assessed"] is True
        assert hit["actual_assessed"] is False


def test_PLANT_declared_equals_enforced_fires_on_named_prefix_objects():
    expected = {
        "sglt2-ckd-progression": {"INTERVENTION_AGENT_PROSE_DIVERGENCE"},
        "sglt2-primary-prevention-hf": {"POPULATION_SCOPE_DIVERGENCE"},
        "colchicine-secondary-cv-prevention": {"DESIGN_MASKING_ANDOR"},
        "metformin-pcos-ovulation": {"POPULATION_CONTEXT_DIVERGENCE"},
    }
    for slug, wanted in expected.items():
        violations = P.check_propositions(_review(slug))
        hit = next(v for v in violations if v["code"] == "DECLARED_ENFORCED_FALSE")
        assert wanted <= set(hit["divergence_codes"]), (slug, hit)


def test_PLANT_byte_reproducible_fires_on_all_prefix_pages():
    slugs = subprocess.check_output(
        ["git", "ls-tree", "-d", "--name-only", f"{PREFIX}:docs/reviews"],
        cwd=ROOT,
        text=True,
    ).split()
    hits = []
    for slug in slugs:
        if "BYTE_REPRODUCIBLE_FALSE" in _codes(P.check_propositions(_review(slug))):
            hits.append(slug)
    assert len(slugs) == 32
    assert len(hits) == 32


def test_PLANT_membership_and_count_sentences_fire_on_prefix_objects():
    sglt2 = P.check_propositions(_review("sglt2-primary-prevention-hf"))
    sglt2_count = [v for v in sglt2 if v["code"] == "POOLED_COUNT_MISMATCH"]
    assert sglt2_count and sglt2_count[0]["subject"] == "primary_randomisations"
    assert (sglt2_count[0]["asserted"], sglt2_count[0]["actual"]) == (4, 5)

    em = P.check_propositions(_review("esketamine-trd-madrs"))
    em_count = [v for v in em if v["code"] == "POOLED_COUNT_MISMATCH"]
    assert em_count and em_count[0]["subject"] == "parity_our_k"
    assert (em_count[0]["asserted"], em_count[0]["actual"]) == (2, 4)

    cp = P.check_propositions(_review("colchicine-postop-af"))
    search = [v for v in cp if v["code"] == "SEARCH_FOUND_CONTRADICTION"]
    assert search and search[0]["pmid"] == "22090167"
    assert search[0]["asserted_found"] is False
    assert search[0]["actual_found"] is True


def test_PLANT_refused_and_pooled_fires_prefix_and_current_dispute_passes():
    old_review = _git_json("aa8ed28a", "docs/reviews/metformin-pcos-ovulation/review.json")
    old_refusals = _git_json("aa8ed28a", "docs/refusals.json")
    old_codes = _codes(P.check_propositions(old_review, {"refusals": old_refusals}))
    assert "REFUSED_AND_POOLED" in old_codes

    current = json.loads((ROOT / "docs/reviews/metformin-pcos-ovulation/review.json").read_text(encoding="utf-8"))
    current_refusals = json.loads((ROOT / "docs/refusals.json").read_text(encoding="utf-8"))
    current_violations = P.check_propositions(P.attach(current), {"refusals": current_refusals})
    assert "REFUSED_AND_POOLED" not in _codes(current_violations)
    disputes = claimgraph.disputes(current, {"refusals": current_refusals})
    assert len([d for d in disputes if d["code"] == "POOL_SCOPE_DISPUTE"]) == 1
    html = (ROOT / "docs/reviews/metformin-pcos-ovulation/index.html").read_text(encoding="utf-8")
    assert "the build refuses a trial both pooled and declared-absent" not in html


def test_controls_do_not_regress():
    esketamine = json.loads((ROOT / "docs/reviews/esketamine-trd-madrs/review.json").read_text(encoding="utf-8"))
    mono = [
        rec for rec in (esketamine.get("screening") or {}).get("records") or []
        if rec.get("id") == "40601310"
    ]
    assert mono and mono[0]["decision"] == "exclude"
    assert "monotherapy" in mono[0]["reason"].lower()

    refusals = json.loads((ROOT / "docs/refusals.json").read_text(encoding="utf-8"))
    omega = " ".join(str(row) for row in refusals.get("omega3-cardiovascular-events") or [])
    assert "DART" in omega and "GISSI-HF" in omega
    assert P.check_propositions(P.attach(
        json.loads((ROOT / "docs/reviews/omega3-cardiovascular-events/review.json").read_text(encoding="utf-8"))
    )) == []


def test_synthetic_clean_page_has_no_proposition_violation():
    clean = {
        "slug": "clean",
        "protocol": {
            "sha": "abc123",
            "eligibility": "Included iff ALL hold: randomised trial; placebo comparator.",
            "text": "Eligibility is randomised trial and placebo comparator.",
        },
        "search": {"retrieval": {"snapshot": {"records_sha256": "abc"}}},
        "screening": {"records": [{"id": "111", "decision": "include"}]},
        "outcomes": [{
            "name": "Outcome",
            "primary": True,
            "result": {"k": 1},
            "trials": [{"id": "PMID 111", "source": "trial"}],
            "declared_absent_trials": [],
        }],
        "rob_sensitivity": {"n_trials": 1, "n_rob_rated": 1},
        "integrity": {"n_pooled": 1, "retracted": []},
        "grade": {"domains": {"publication_bias": {"assessed": True, "basis": "clean plant"}}},
    }
    assert P.check_propositions(P.attach(clean)) == []


def test_state_collapsed_plant_fires():
    dirty = P.attach({
        "outcomes": [{"name": "O", "primary": True, "result": {"k": 1}, "trials": [{"id": "PMID 111"}]}],
    })
    dirty = copy.deepcopy(dirty)
    dirty["propositions"]["objects"].append({
        "kind": "state_collapsed",
        "surface": "plant",
        "source_path": "/plant",
        "claim_id": "plant-state-collapse",
        "source_state": "SOURCE_NOT_RETRIEVED",
        "rendered_state": "unknown",
    })
    violations = P.check_propositions(dirty)
    assert "STATE_COLLAPSED" in _codes(violations)
