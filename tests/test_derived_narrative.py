import copy
import json
from pathlib import Path
import subprocess

import pytest
from harness import derived_narrative as D
from harness import compat_check, page

PIN = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
ROOT = Path(__file__).resolve().parents[1]


def pinned(path):
    return json.loads(subprocess.check_output(["git", "show", f"{PIN}:{path}"], cwd=ROOT))


@pytest.fixture
def review():
    return pinned("docs/reviews/pcsk9-mace/review.json")


def test_served_fourier_is_stale_and_matching_annotation_passes(review):
    t = review["outcomes"][0]["trials"][0]
    d = D.audit_trial(t)
    assert any(x["code"] == D.STALE_NARRATIVE for x in d["audit"])
    assert d["role"] == "key secondary"
    assert len(d["components"]) == 3
    assert "26 months" in d["timepoint"]
    assert "5-point primary" not in d["value"]
    assert not D.contradictions(d, {"endpoint_definition": "3-point key secondary", "components": t["components"]})


def test_generic_plant_and_timepoint():
    t = {"endpoint_definition_span": "The secondary endpoint was hip fracture at 24 months.",
         "components": ["hip fracture"], "endpoint_definition": "2-point primary",
         "follow_up_window": "12 months"}
    a = D.audit_trial(t)
    assert set(a["audit"][0]["conflicts"]) >= {"endpoint role", "component count", "timepoint"}


def test_display_derivation_never_uses_an_annotation_or_a_whole_abstract():
    """Verifier-revised: the DISPLAY description comes only from the input's binding (derived_narrative.derive). The compat
    CHECKING derivation (compat_check._derive_endpoint) keeps reading the trial's source text on purpose -- that is how real
    definition heterogeneity (probiotics' AAD definitions) is detected (tests/test_compat_underlying.py)."""
    d = D.derive({"name": "Mortality", "source": "", "abstract": "The primary outcome was treatment failure.",
                  "endpoint_definition": "made up endpoint"})
    assert "made up" not in str(d.get("value")) and "treatment failure" not in str(d.get("value"))


def test_enrichment_retains_stale_original_and_emits_flag(review):
    original = copy.deepcopy(review["outcomes"][0]["trials"][0])
    compat_check.enrich(review, pinned("cache/pcsk9-mace/records.json"))
    t = review["outcomes"][0]["trials"][0]
    assert "5-point primary" not in t["endpoint_definition"]
    assert any("5-point primary" in str(a["original"]) for a in t["narrative_audit"])
    assert t["effect"] == original["effect"]
    assert any(v["code"] == D.STALE_NARRATIVE for v in compat_check.check(review))


def test_render_replaces_all_old_endpoint_surfaces_without_mutating(review):
    o = review["outcomes"][0]
    before = copy.deepcopy(o)
    html = page.render_outcome_block(o)
    assert "FOURIER: 5-point primary" not in html
    assert "STALE_NARRATIVE" in html
    assert "Role: key secondary" in html
    assert o == before


def test_undeclared_never_guessed_and_every_trial_reported(review):
    topic = pinned("topics/pcsk9-mace.json")
    held = json.loads((ROOT / "evidence/compat_narrative/held_results.json").read_text(encoding="utf-8"))
    report = D.selection_report(topic, review["outcomes"][0], held,
                               ["cardiovascular death", "myocardial infarction", "stroke"])
    assert report["declared_rule"] is None
    assert report["status"] == "RESULT_SELECTION_RULE_NOT_DECLARED"
    rows = {r["trial_id"]: r for r in report["per_trial"]}
    assert len(rows) == 5
    assert rows["28304224"]["selections"][D.RULES[0]]["served_matches"] is False
    assert rows["28304224"]["selections"][D.RULES[1]]["served_matches"] is True
    assert rows["41211925"]["refusal"] == "RESULT_INCOMPATIBLE"
    assert rows["41211925"]["selections"][D.RULES[0]]["selected"] == ["41211925:3-point"]
    assert rows["25773378"]["selections"][D.RULES[0]]["selected"] == []
    assert rows["27846344"]["selections"][D.RULES[1]]["selected"] == []


@pytest.mark.parametrize("rule", D.RULES)
def test_explicit_rule_applies_to_every_trial(rule, review):
    topic = pinned("topics/pcsk9-mace.json")
    topic["primary_outcome"]["result_selection_rule"] = rule
    held = json.loads((ROOT / "evidence/compat_narrative/held_results.json").read_text(encoding="utf-8"))
    report = D.selection_report(topic, review["outcomes"][0], held, ["cardiovascular death", "myocardial infarction", "stroke"])
    assert report["declared_rule"] == rule
    assert all(r["declared_selection"] == r["selections"][rule] for r in report["per_trial"])


def test_ties_are_not_guessed():
    candidate = {"candidate_id": "a", "components": ["x", "y"], "endpoint_definition_span": "Primary endpoint: x and y"}
    r = D.selection_report({}, {}, {"trial": [candidate, dict(candidate, candidate_id="b")]}, ["x", "y"])
    assert all(s["status"] == "AMBIGUOUS" for s in r["per_trial"][0]["selections"].values())


def test_held_results_are_verified_against_pinned_source_bytes():
    import re
    recs = {r["id"]: r for r in pinned("cache/pcsk9-mace/records.json")["records"]}
    held = json.loads((ROOT / "evidence/compat_narrative/held_results.json").read_text(encoding="utf-8"))
    for pid, candidates in held.items():
        assert pid in recs
        for c in candidates:
            assert c["endpoint_definition_span"] in recs[pid]["abstract"]
            assert c["endpoint_result_span"] in recs[pid]["abstract"]
            m = re.search(r"hazard ratio, ([0-9.]+); 95% (?:confidence interval(?: \[CI\])?|CI), ([0-9.]+) to ([0-9.]+)", c["endpoint_result_span"])
            assert [float(x) for x in m.groups()] == [c[k] for k in ("effect", "ci_low", "ci_high")]


def test_idempotent_description(review):
    o = review["outcomes"][0]
    D.apply_outcome(o)
    values = [t["endpoint_definition"] for t in o["trials"]]
    D.apply_outcome(o)
    assert values == [t["endpoint_definition"] for t in o["trials"]]


def test_protocol_explicit_declaration_and_mentions_are_distinct():
    r = D.selection_report({}, {}, {}, protocol="Result-selection rule: EACH_TRIAL_PRIMARY_COMPOSITE")
    assert r["declared_rule"] == D.RULES[0]
    r = D.selection_report({}, {}, {}, protocol="Consider EACH_TRIAL_PRIMARY_COMPOSITE or CLOSEST_TO_COMMON_COMPONENT_SET.")
    assert r["declared_rule"] is None


def test_census_denominator_and_rows_match_pinned_bytes():
    evidence = json.loads((ROOT / "evidence/compat_narrative/census_inputs.json").read_text(encoding="utf-8"))
    files = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", PIN, "docs/reviews"], cwd=ROOT, text=True).splitlines()
    rows = []
    for path in files:
        if not path.endswith("/review.json"):
            continue
        r = pinned(path)
        for o in r.get("outcomes", []):
            z = o.get("result") or {}
            if not z.get("k") or z.get("present") is False or z.get("suppressed_incompatible"):
                continue
            rows.extend((r["slug"], o["name"], t) for t in o.get("trials", []))
    assert len(rows) == evidence["denominator"] == 117
    assert sum(r["adjudication"] == "STALE_NARRATIVE" for r in evidence["rows"]) == evidence["contradictions"] == 24
    for (slug, outcome, trial), saved in zip(rows, evidence["rows"]):
        assert (slug, outcome) == (saved["slug"], saved["outcome"])
        assert all(trial[k] == v for k, v in saved["trial"].items())


def test_matching_odyssey_annotation_is_not_stale(review):
    t = review["outcomes"][0]["trials"][1]
    topic = pinned("topics/pcsk9-mace.json")
    a = topic["primary_outcome"]["trial_annotations"]["30403574"]
    assert not D.contradictions(D.derive(t), a)


def test_cached_component_and_direction_tables_cannot_override_inputs(review):
    o = review["outcomes"][0]
    o["compat_direction"]["dimensions"][0]["underlying"]["values"] = ["FOURIER: 5-point primary"]
    D.apply_outcome(o)
    assert "coronary heart disease death" in o["compat_key"]["endpoint_canonical"]["components"]
    assert "unstable angina" in o["compat_key"]["endpoint_canonical"]["components"]
    assert "FOURIER: 5-point primary" not in str(o["compat_direction"])


def test_conflicting_annotations_flagged_without_choosing_a_timepoint():
    t = {"source": "Diarrhea occurred in 39 patients versus 40 patients.",
         "endpoint_definition": "Primary outcome was diarrhea in the first 21 days after enrollment",
         "follow_up_window": "14 days"}
    d = D.audit_trial(t)
    assert d["timepoint"] is None
    assert d["audit"][0]["code"] == D.STALE_NARRATIVE
    assert "input timepoint unbound" in d["audit"][0]["conflicts"][0]
