"""G1 (trial-for-trial match): comparator memberships bound from the comparator's OWN words (text rows), proposed blind
by two models (registry/model_proposals/comparator_membership*.json) and bound after a human check."""
import copy
import json
from pathlib import Path

import pytest

from harness import comparator_analysis as ca

ROOT = Path(__file__).resolve().parents[1]
TEXT_TOPICS = ["colchicine-postop-af", "colchicine-recurrent-pericarditis", "finerenone-ckd-t2d-renal",
               "iv-iron-hfref-hosp", "probiotics-aad-prevention", "statins-primary-prevention-elderly",
               "glp1-ra-mace-t2d"]


def _review(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("slug", TEXT_TOPICS)
def test_text_membership_rows_are_panel_rows_quoted_in_the_held_text(slug):
    doc = ca.load(ROOT, slug)
    rows = doc["membership"]["rows"]
    panel = json.loads((ROOT / "cache" / slug / "comparators.json").read_text(encoding="utf-8"))[0]
    assert {r["panel_row"] for r in rows} <= {t["family_id"] for t in panel["trial_set"]}
    # beside a per-outcome panel endpoint binding the membership governs (round 10, plants_round10 Q1): never an
    # emptied set -- every bound row is in the comparator's pool for our outcome
    theirs = _review(slug)["comparator"]["overlap_relation"]
    assert theirs["theirs_k"] == len(rows), slug


def test_glp1_is_compared_on_all_eight_cvots_elixa_included():
    # Giugliano 2021 Fig. 3 pools the eight CVOTs on MACE, ELIXA's 4-point MACE included; our pool excludes ELIXA and
    # adds SOUL (2025). Before round 10 the panel's "3-point MACE" binding dropped ELIXA from THEIR analysis: SUPERSET
    o = _review("glp1-ra-mace-t2d")["comparator"]["overlap_relation"]
    assert (o["relation"], o["theirs_k"], o["shared_k"]) == ("OVERLAPPING", 8, 7)
    assert o["only_ours"] == ["NCT03914326"] and o["only_theirs"] == ["ELIXA"]
    assert o["theirs_k"] == o["theirs_k_stated"]["value"]


def test_a_text_row_whose_quote_is_not_in_the_held_text_is_refused(tmp_path):
    slug = "colchicine-recurrent-pericarditis"
    doc = json.loads((ROOT / "cache" / slug / "comparator_analysis.json").read_text(encoding="utf-8"))
    bad = copy.deepcopy(doc)
    bad["membership"]["rows"][0]["quote"] = "COPE was excluded from every analysis of recurrence."
    (tmp_path / "cache" / slug).mkdir(parents=True)
    for f in ("comparators.json", "comparator_fulltext.txt"):
        (tmp_path / "cache" / slug / f).write_bytes((ROOT / "cache" / slug / f).read_bytes())
    (tmp_path / "cache" / slug / "comparator_analysis.json").write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ca.AnalysisRefused):
        ca.load(tmp_path, slug)


def test_recurrent_pericarditis_is_compared_on_its_secondary_prevention_analysis():
    ov = _review("colchicine-recurrent-pericarditis")["comparator"]["overlap"]
    assert (ov["relation"], ov["theirs_k"], ov["shared_k"]) == ("OVERLAPPING", 3, 1)


def test_both_readers_proposed_every_bound_membership():
    q1 = {e["item_id"]: e for e in json.loads((ROOT / "registry/model_proposals/comparator_membership.json").read_text(encoding="utf-8"))["items"]}
    q2 = {e["item_id"]: e for e in json.loads((ROOT / "registry/model_proposals/comparator_membership_reader2.json").read_text(encoding="utf-8"))["items"]}
    for slug in TEXT_TOPICS:
        rows = sorted(r["panel_row"] for r in ca.load(ROOT, slug)["membership"]["rows"])
        k = f"{slug}::membership"
        assert q1[k]["verification"]["model_decision"] == q2[k]["verification"]["model_decision"] == rows, slug
