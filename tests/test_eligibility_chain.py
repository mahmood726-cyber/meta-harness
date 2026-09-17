import copy
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import eligibility_chain as EC  # noqa: E402
from harness import screen  # noqa: E402


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = "ad5e7c66"
SLUG = "colchicine-postop-af"


def _git_text(path):
    return subprocess.check_output(
        ["git", "-C", ROOT, "show", f"{PREFIX}:{path}"],
        text=True,
        encoding="utf-8",
    )


def _git_json(path):
    return json.loads(_git_text(path))


def _current_json(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def _prefixed_colchicine_inputs():
    return (
        _git_json(f"topics/{SLUG}.json"),
        _git_text(f"protocols/{SLUG}.md"),
        _git_json(f"docs/reviews/{SLUG}/review.json"),
        _git_json(f"cache/{SLUG}/records.json"),
    )


def _annotated_prefixed_colchicine():
    cfg, proto, review, records = _prefixed_colchicine_inputs()
    return EC.apply_admissions(copy.deepcopy(review), cfg, records, proto)


def _codes(review):
    return [v["code"] for v in EC.check_review(review)]


def test_prefix_protocol_states_masking_but_config_has_no_masking_rule_and_page_claims_agreement():
    cfg, proto, review, records = _prefixed_colchicine_inputs()
    contract = EC.compile_contract(SLUG, cfg, proto)
    divs = contract["divergences"]
    assert any(
        d["code"] == "PROTOCOL_CONFIG_DIVERGENCE"
        and d["dimension"] == "design_masking"
        and d["config_value"] is None
        for d in divs
    )
    html = _git_text(f"docs/reviews/{SLUG}/index.html")
    assert "agree on the checked dimensions" in html
    annotated = EC.apply_admissions(copy.deepcopy(review), cfg, records, proto)
    assert "PROTOCOL_CONFIG_DIVERGENCE" in _codes(annotated)


def test_prefix_end_af_pooled_open_label_fails_protocol_contract():
    review = _annotated_prefixed_colchicine()
    failures = [v for v in EC.check_review(review) if v["code"] == "TRIAL_FAILS_CONTRACT"]
    end_af = [v for v in failures if v.get("trial_id") == "PMID 27502857" and v["dimension"] == "design_masking"]
    assert end_af
    assert "open-label" in (end_af[0].get("span") or "").lower()


def test_prefix_zarpelon_has_two_rationales_but_current_vocab_reaches_single_design_rationale():
    review = _annotated_prefixed_colchicine()
    z = [v for v in EC.check_review(review)
         if v["code"] == "ELIGIBILITY_STATE_INCONSISTENT" and v.get("trial") == "PMID 27223641"]
    assert z
    assert "population not on-topic" in z[0]["rationales"][0]
    assert "multi-arm/dose-timing ambiguity" in z[0]["rationales"][1]

    current_cfg = _current_json(f"topics/{SLUG}.json")
    records = _git_json(f"cache/{SLUG}/records.json")
    rec = next(r for r in records["records"] if str(r.get("id")) == "27223641")
    decision = screen.screen_record(rec, current_cfg["include"], set())
    assert decision[0] == "include"
    single = EC.single_rationale_for_record(rec, current_cfg, _git_text(f"protocols/{SLUG}.md"))
    assert single["single_rationale"] == "design_masking"


def test_prefix_copps2_followup_key_violates_protocol_window():
    review = _annotated_prefixed_colchicine()
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    copps2 = next(t for t in primary["trials"] if t["id"] == "PMID 25172965")
    row = copps2["admission"]["follow_up_window"]
    assert row["trial_value"] == "3 months"
    assert row["verdict"] == "FAIL"
    key = primary["compat_key"]["follow_up_window"]
    assert key["matched"] is False


def test_prefix_2026_trial_is_available_case_not_itt():
    review = _annotated_prefixed_colchicine()
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    trial = next(t for t in primary["trials"] if t["id"] == "PMID 42132185")
    row = trial["admission"]["analysis_set"]
    assert row["trial_value"] == "AVAILABLE_CASE"
    assert row["verdict"] == "FAIL"


def test_prefix_shipped_prose_predicates_are_false():
    review = _annotated_prefixed_colchicine()
    preds = [v for v in EC.check_review(review) if v["code"] == "PROSE_PREDICATE_FALSE"]
    dims = {v["dimension"] for v in preds}
    assert {"reach_vs_screening", "extraction_debt"} <= dims


def test_synthetic_clean_contract_has_no_violations():
    proto = """
    ## Eligibility
    Include double-blind OR placebo-controlled RCTs.
    ## Estimand / population / timepoint
    - **Population** - intention-to-treat.
    - **Timepoint** - trial end.
    """
    cfg = {
        "slug": "synthetic-clean",
        "include": {"design_double_blind": True, "comparator_any": ["placebo"]},
        "primary_outcome": {"population": "intention-to-treat", "timepoint": "trial end"},
    }
    review = {"slug": "synthetic-clean", "outcomes": [{
        "name": "x", "primary": True, "trials": [{
            "id": "PMID 12345678", "label": "A",
            "source": "randomized, double-blind, placebo-controlled trial; intention-to-treat at trial end",
        }],
        "result": {"k": 1},
    }], "screening": {"records": []}}
    records = {"records": [{"id": "12345678", "title": "A", "abstract": review["outcomes"][0]["trials"][0]["source"]}]}
    annotated = EC.apply_admissions(review, cfg, records, proto)
    assert EC.check_review(annotated) == []


def test_synthetic_config_rule_without_protocol_sentence_is_divergence():
    proto = "## Eligibility\nInclude randomized trials."
    cfg = {"slug": "synthetic-extra", "include": {"design_double_blind": True, "comparator_any": ["placebo"]}}
    contract = EC.compile_contract("synthetic-extra", cfg, proto)
    assert any(d["code"] == "CONFIG_WITHOUT_PROTOCOL" and d["dimension"] == "design_masking"
               for d in contract["divergences"])


def test_additional_protocol_config_divergence_plants():
    cases = [
        ("sglt2-primary-prevention-hf", "design_population_context"),
        ("colchicine-secondary-cv-prevention", "design_masking"),
        ("metformin-pcos-ovulation", "population_context"),
        ("colchicine-postop-af", "design_masking"),
    ]
    for slug, dim in cases:
        cfg = _current_json(f"topics/{slug}.json")
        proto = open(os.path.join(ROOT, "protocols", f"{slug}.md"), encoding="utf-8").read()
        contract = EC.compile_contract(slug, cfg, proto)
        assert any(d["code"] == "PROTOCOL_CONFIG_DIVERGENCE" and d["dimension"] == dim
                   for d in contract["divergences"]), slug
