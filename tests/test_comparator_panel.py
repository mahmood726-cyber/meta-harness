import copy
import json
from pathlib import Path

import pytest

from harness import gate

ROOT = Path(__file__).resolve().parents[1]


def planted_review():
    return {"comparator_panel": [{"id": "plant", "trial_set": [
        {"family_id": "A"}, {"family_id": "B"}]}],
        "outcomes": [{"name": "primary", "primary": True, "trials": [
            {"id": "A"}, {"id": "B"}], "result": {"k": 2}}]}


def run_gate(tmp_path, review, html):
    (tmp_path / "review.json").write_text(json.dumps(review), encoding="utf-8")
    return gate.check_no_independent_corroboration_claim(str(tmp_path), html)


def test_equal_pool_independent_corroboration_refused(tmp_path):
    assert run_gate(tmp_path, planted_review(), "<p>independent corroboration</p>")


def test_stored_overlap_drift_refused(tmp_path):
    review = planted_review()
    review["comparator_panel"][0]["overlaps"] = [{"shared": ["WRONG"]}]
    assert run_gate(tmp_path, review, "<p>Analytic membership sensitivity</p>")


@pytest.mark.parametrize("phrase", ["independently corroborated", "external validation confirms", "replicated", "replication"])
def test_synonyms_refused(tmp_path, phrase):
    assert run_gate(tmp_path, planted_review(), phrase)


def test_live_membership_changes_overlap_and_threshold():
    from harness.comparator_panel import overlaps, gate_reasons
    r = planted_review()
    c = r["comparator_panel"][0]
    assert overlaps(c, r)[0]["jaccard"] == 1
    r["outcomes"][0]["trials"] = [{"id": "C"}, {"id": "D"}]
    ov = overlaps(c, r)[0]
    assert ov["shared"] == [] and ov["harness_only"] == ["C", "D"]
    assert not gate_reasons(r, "independent corroboration")


def test_endpoint_unknown_is_not_compatible_and_strands_are_separate():
    from harness.comparator_panel import overlaps
    r = planted_review()
    r["strands"] = {"strands": [{"strand": "A", "members": [{"pmid": "A"}]},
                               {"strand": "B", "members": [{"pmid": "C"}]}]}
    rows = overlaps(r["comparator_panel"][0], r)
    assert rows[0]["endpoint_compatible_overlap"] == []
    assert rows[0]["endpoint_unknown"] == ["A", "B"]
    assert rows[1]["shared"] == ["A"] and rows[2]["shared"] == []


def test_held_source_mutations_fail_closed():
    from harness.comparator_panel import validate
    c = json.loads((ROOT / "cache/glp1-ra-mace-t2d/comparators.json").read_text(encoding="utf-8"))[0]
    validate(c)
    for mutate in (lambda x: x.update(document_sha256="bad"),
                   lambda x: x["effect"].update(value=9.99),
                   lambda x: x["trial_set"][0]["span"].update(start=0)):
        bad = copy.deepcopy(c)
        mutate(bad)
        with pytest.raises(ValueError):
            validate(bad)


def test_only_exact_adjudicated_sentence_exempt(tmp_path):
    from harness.comparator_panel import adjudication
    r = planted_review()
    c = r["comparator_panel"][0]
    c["effect"] = {"value": .86}
    sentence = adjudication(c)
    assert not run_gate(tmp_path, r, sentence)
    assert run_gate(tmp_path, r, sentence + " This independently corroborates the result.")


def test_not_held_has_no_numbers():
    from harness.comparator_panel import validate, render
    panel = json.loads((ROOT / "cache/glp1-ra-mace-t2d/comparators.json").read_text(encoding="utf-8"))
    for c in panel[1:]:
        validate(c)
        assert "NOT HELD — identity only" in render({"comparator_panel": [c]})
        c["effect"] = {"value": .86}
        with pytest.raises(ValueError):
            validate(c)


def test_contains_whole_pool_refused_even_below_jaccard_threshold(tmp_path):
    r = planted_review()
    r["comparator_panel"][0]["trial_set"] += [{"family_id": x} for x in ["C", "D", "E"]]
    assert run_gate(tmp_path, r, "independent corroboration")


def test_strict_jaccard_threshold(tmp_path):
    r = planted_review()
    r["outcomes"][0]["trials"] += [{"id": "C"}]
    r["comparator_panel"][0]["trial_set"] += [{"family_id": "D"}]
    assert not run_gate(tmp_path, r, "independent corroboration")


def test_stored_overlap_in_source_refused(tmp_path):
    from harness.comparator_panel import attach
    source = tmp_path / "cache" / "test"
    source.mkdir(parents=True)
    c = {"id": "plant", "held": False, "overlaps": []}
    (source / "comparators.json").write_text(json.dumps([c]), encoding="utf-8")
    with pytest.raises(ValueError, match="stored overlap"):
        attach("test", {}, tmp_path)
