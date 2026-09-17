import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import arm_object, gate, screen  # noqa: E402


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = "ad5e7c66"


def _git_json(path):
    out = subprocess.check_output(
        ["git", "-C", ROOT, "show", f"{PREFIX}:{path}"],
        text=True,
        encoding="utf-8",
    )
    return json.loads(out)


def _load_topic(slug):
    return json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))


def _load_cache_records(slug):
    data = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    return list(data.get("records") or []) + list(data.get("ctgov") or [])


def _prefixed_screen_row(slug, wanted):
    review = _git_json(f"docs/reviews/{slug}/review.json")
    rows = (review.get("screening") or {}).get("records") or []
    hit = [r for r in rows if str(r.get("id")).endswith(str(wanted))]
    assert hit, f"{wanted} absent from pre-fix screening rows"
    return hit[0]


def _post_screen_row(slug, wanted):
    cfg = _load_topic(slug)
    out = screen.run(_load_cache_records(slug), cfg)["decisions"]
    hit = [r for r in out if str(r.get("id")) == str(wanted)]
    assert hit, f"{wanted} absent from post-fix screen.run rows"
    return hit[0]


def test_pyy1875_prefixed_include_then_arm_object_x_contrast():
    pre = _prefixed_screen_row("semaglutide-obesity-weight", "40629530")
    assert pre["decision"] == "include"
    assert "PYY1875" in pre["span"]

    post = _post_screen_row("semaglutide-obesity-weight", "40629530")
    assert post["decision"] == "exclude"
    assert post["rule_id"] == "X-CONTRAST"
    assert "background=semaglutide 2.4 mg both arms" in post["reason"]


def test_crusaders_prefixed_include_then_strategy_bundle_x_contrast():
    pre = _prefixed_screen_row("balanced-crystalloids-vs-saline-mortality", "NCT07189091")
    assert pre["decision"] == "include"
    assert "Plasmalyte" in pre["reason"]

    post = _post_screen_row("balanced-crystalloids-vs-saline-mortality", "NCT07189091")
    assert post["decision"] == "exclude"
    assert post["rule_id"] == "X-CONTRAST"
    assert "strategy_bundle" in post["reason"]


def test_histori_prefixed_include_then_dose_refusal():
    pre = _prefixed_screen_row("semaglutide-obesity-weight", "41778920")
    assert pre["decision"] == "include"

    post = _post_screen_row("semaglutide-obesity-weight", "41778920")
    assert post["decision"] == "exclude"
    assert post["rule_id"] == "X-DOSE"
    assert "1.0 mg" in post["reason"]


def test_step_teens_prefixed_include_then_age_refusal():
    pre = _prefixed_screen_row("semaglutide-obesity-weight", "41296499")
    assert pre["decision"] == "include"

    post = _post_screen_row("semaglutide-obesity-weight", "41296499")
    assert post["decision"] == "exclude"
    assert post["rule_id"] == "X-AGE"
    assert "12 to <18" in post["reason"]


def test_hfpef_prefixed_include_then_population_inconsistency():
    pre = _prefixed_screen_row("semaglutide-obesity-weight", "41045908")
    assert pre["decision"] == "include"

    post = _post_screen_row("semaglutide-obesity-weight", "41045908")
    assert post["decision"] == "exclude"
    assert post["rule_id"] == "ELIGIBILITY_STATE_INCONSISTENT"
    assert "population_none:heart failure" in post["reason"]


def test_step7_and_step12_mixed_t2d_population_refused():
    pre7 = _prefixed_screen_row("semaglutide-obesity-weight", "40069849")
    assert pre7["decision"] == "include"
    post7 = _post_screen_row("semaglutide-obesity-weight", "40069849")
    assert post7["rule_id"] == "X-POPULATION"
    assert "mixed T2D" in post7["reason"]

    pre12 = _prefixed_screen_row("semaglutide-obesity-weight", "42575111")
    assert pre12["decision"] == "include"
    post12 = _post_screen_row("semaglutide-obesity-weight", "42575111")
    assert post12["rule_id"] == "X-POPULATION"
    assert "mixed T2D" in post12["reason"]


def test_miro_ckd_prefixed_include_then_arm_object_x_contrast():
    pre = _prefixed_screen_row("sglt2-ckd-progression", "NCT06350123")
    assert pre["decision"] == "include"

    post = _post_screen_row("sglt2-ckd-progression", "NCT06350123")
    assert post["decision"] == "exclude"
    assert post["rule_id"] == "X-CONTRAST"
    assert "CONTRAST_ABSENT" in post["reason"]
    assert "balcinrenone" in post["reason"].lower()
    assert "dapagliflozin" in post["reason"].lower()


def test_positive_controls_still_include():
    step1 = _post_screen_row("semaglutide-obesity-weight", "33567185")
    step3 = _post_screen_row("semaglutide-obesity-weight", "33625476")
    assert step1["decision"] == "include"
    assert step3["decision"] == "include"

    dapa_hf = _post_screen_row("sglt2-hfref-hosp-cvdeath", "31535829")
    emperor_reduced = _post_screen_row("sglt2-hfref-hosp-cvdeath", "32865377")
    assert dapa_hf["decision"] == "include"
    assert emperor_reduced["decision"] == "include"


def test_confidence_synthetic_contrast_passes():
    cfg = {
        "include": {
            "population_any": ["chronic kidney disease"],
            "intervention_any": ["finerenone", "empagliflozin"],
            "comparator_any": ["placebo"],
            "design_double_blind": True,
        },
        "intervention_terms": ["finerenone", "empagliflozin"],
        "arm_object": {"contrast": {"drug_any": ["finerenone", "empagliflozin"], "comparator_any": ["placebo"]}},
    }
    rec = {
        "id": "SYNTH-CONFIDENCE",
        "id_type": "pmid",
        "title": "CONFIDENCE randomized trial in chronic kidney disease.",
        "abstract": "Adults with chronic kidney disease were randomized double-blind to finerenone 10 mg plus empagliflozin 10 mg versus matching placebo.",
        "pubtypes": ["Randomized Controlled Trial"],
    }
    row = screen.run([rec], cfg)["decisions"][0]
    assert row["decision"] == "include"


def test_step8_hidden_matched_placebo_contrast_is_visible():
    cfg = _load_topic("semaglutide-obesity-weight")
    synthetic = {
        "id": "SYNTH-STEP8",
        "id_type": "pmid",
        "title": "STEP 8 semaglutide versus liraglutide in overweight or obesity.",
        "abstract": "The active treatment groups double-blinded against matched placebo groups compared semaglutide 2.4 mg, matched placebo, liraglutide, and matched placebo.",
        "pubtypes": ["Randomized Controlled Trial"],
        "interventions": ["Semaglutide", "Placebo (semaglutide)", "Liraglutide", "Placebo (liraglutide)"],
    }
    obj = arm_object.build(synthetic, cfg)
    hidden = arm_object.hidden_eligible_contrasts(obj, cfg)
    assert hidden
    assert hidden[0]["code"] == "CONTRAST_HIDDEN_BY_TITLE"
    assert hidden[0]["drug"]["value"] == "semaglutide"


def test_gate_refuses_pooled_trial_that_fails_arm_object_contract(tmp_path, monkeypatch):
    slug = "sglt2-ckd-progression"
    monkeypatch.setattr(gate, "ROOT", str(tmp_path))
    (tmp_path / "topics").mkdir()
    (tmp_path / "cache" / slug).mkdir(parents=True)
    review_dir = tmp_path / "docs" / "reviews" / slug
    review_dir.mkdir(parents=True)
    (tmp_path / "topics" / f"{slug}.json").write_text(json.dumps({
        "include": {
            "intervention_any": ["dapagliflozin"],
            "comparator_any": ["placebo"],
        },
        "intervention_terms": ["dapagliflozin"],
    }), encoding="utf-8")
    (tmp_path / "cache" / slug / "records.json").write_text(json.dumps({
        "records": [],
        "ctgov": [{
            "id": "NCT06350123",
            "id_type": "nct",
            "acronym": "MIRO-CKD",
            "title": "Efficacy, Safety and Tolerability of Balcinrenone/Dapagliflozin Compared to Dapagliflozin in Adults With Chronic Kidney Disease",
            "interventions": [
                "Balcinrenone/dapagliflozin 15 mg/10 mg and matching placebo for dapagliflozin 10 mg",
                "Dapagliflozin 10 mg and matching placebo for balcinrenone/dapagliflozin",
            ],
        }],
    }), encoding="utf-8")
    (review_dir / "review.json").write_text(json.dumps({
        "outcomes": [{
            "name": "Primary",
            "trials": [{"id": "NCT06350123", "label": "MIRO-CKD"}],
        }],
    }), encoding="utf-8")

    reasons = gate.check_arm_object_contract(str(review_dir))
    assert reasons
    assert "TRIAL_FAILS_CONTRACT" in reasons[0]
    assert "X-CONTRAST" in reasons[0]
