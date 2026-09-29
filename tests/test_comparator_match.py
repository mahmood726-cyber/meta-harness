import copy
import hashlib
import json

import pytest

from harness.comparator_extract import extract, parse_text, fact
from harness.meta_match import match
from harness import comparator_panel


TOPIC = {"slug": "plant", "primary_outcome": {"name": "Mortality"}, "secondary_outcomes": [{"name": "Hospitalization"}]}
ROW = "ALPHA | NCT12345678 | PMID: 12345678 | n1=100 | n2=120 | events1=10 | events2=20 | RR 0.60 (0.40-0.90) | 12 months | intention-to-treat"
TEXT = "Included-studies table\nSmith 2020 | n=220\n\nForest plot: Mortality\n" + ROW + "\nPooled | k=1 | RR 0.60 (0.40-0.90) | random-effects | I2=0 | tau2=0\n\nForest plot: Hospitalization\nBETA | n=90 | RR 0.5 (0.3-0.8)\n"


def fixture():
    comp = parse_text(TEXT, TOPIC)
    row = copy.deepcopy(comp["trial_set"][1])
    review = {"outcomes": [{"primary": True, "name": "Mortality", "trials": [row], "result": {"estimate": .6, "scale": "RR"}}]}
    return review, comp


def test_table_forest_exact_and_negative_secondary():
    review, comp = fixture()
    assert [r["label"] for r in comp["trial_set"]] == ["Smith 2020", "ALPHA", "BETA"]
    row = comp["trial_set"][1]
    assert {k: row[k]["value"] for k in ("registration", "pmid", "n1", "n2", "events1", "events2", "effect", "ci_low", "ci_high", "measure", "outcome", "timepoint")} == dict(registration="NCT12345678", pmid="12345678", n1=100, n2=120, events1=10, events2=20, effect=.6, ci_low=.4, ci_high=.9, measure="RR", outcome="Mortality", timepoint="12 months")
    assert row["span"] == ROW
    assert comp["pooled"]["k"]["value"] == 1
    result = match(review, comp)
    assert result["K_MATCH"] == result["ESTIMATE_WITHIN_CI"] == "yes"
    assert next(r for r in result["trials"] if r["label"] == "ALPHA")["status"] == "MATCH"
    assert not any(r["label"] == "BETA" for r in result["trials"])


@pytest.mark.parametrize("field,value,reason", [("timepoint", "6 months", "TIMEPOINT_DIFFERS"), ("population", "per-protocol", "POPULATION_DIFFERS"), ("measure", "OR", "MEASURE_DIFFERS"), ("events1", 11, "COUNTS_DIFFER"), ("effect", .7, "UNKNOWN")])
def test_difference_plants(field, value, reason):
    review, comp = fixture()
    review["outcomes"][0]["trials"][0][field] = fact(value, str(value))
    r = next(r for r in match(review, comp)["trials"] if r["label"] == "ALPHA")
    assert (r["status"], r["reason"]) == ("VALUE_DIFFERS", reason)


def test_ambiguous_author_year_abstains():
    review, comp = fixture()
    for row in (review["outcomes"][0]["trials"][0], comp["trial_set"][1]):
        row.update(label="Smith 2020", registration=fact(), pmid=fact())
    review["outcomes"][0]["trials"].append(copy.deepcopy(review["outcomes"][0]["trials"][0]))
    assert any(r.get("reason") == "AMBIGUOUS_IDENTITY" for r in match(review, comp)["trials"])


def test_sha_guard_and_valid_document(tmp_path):
    (tmp_path / "topics").mkdir()
    (tmp_path / "topics/plant.json").write_text(json.dumps(TOPIC), encoding="utf-8")
    cache = tmp_path / "cache/plant"
    cache.mkdir(parents=True)
    raw = TEXT.encode()
    (cache / "comparator_fulltext.txt").write_bytes(raw)
    panel = [{"held": True, "document_ref": "cache/plant/comparator_fulltext.txt", "document_sha256": hashlib.sha256(raw).hexdigest()}]
    (cache / "comparators.json").write_text(json.dumps(panel), encoding="utf-8")
    assert extract("plant", tmp_path)["trial_set"]
    (cache / "comparator_fulltext.txt").write_bytes(raw + b"tampered")
    with pytest.raises(ValueError, match="REFUSED_SHA256_MISMATCH: plant"):
        extract("plant", tmp_path)
    panel[0]["document_ref"] = "topics/plant.json"
    (cache / "comparators.json").write_text(json.dumps(panel), encoding="utf-8")
    with pytest.raises(ValueError, match="REFUSED_DOCUMENT_PATH"):
        extract("plant", tmp_path)


def test_missing_extra_and_incomplete_abstention():
    review, comp = fixture()
    review["outcomes"][0]["trials"][0]["registration"] = fact("NCT87654321", "NCT87654321")
    statuses = [r["status"] for r in match(review, comp)["trials"]]
    assert "MISSING_FROM_OURS" in statuses and "EXTRA_IN_OURS" in statuses
    review["absent_trials"] = [{"registration": "NCT12345678", "absence_code": "NOT_EXTRACTED"}]
    assert any(r.get("our_state") == "NOT_EXTRACTED" for r in match(review, comp)["trials"])
    comp["membership_complete"] = False
    assert "EXTRA_IN_OURS" not in [r["status"] for r in match(review, comp)["trials"]]


def test_no_guessing_missing_values_or_nonratio():
    review, comp = fixture()
    review["outcomes"][0]["trials"][0]["timepoint"] = fact()
    assert any(r.get("reason") == "UNPARSED_VALUES_OR_SCOPE" for r in match(review, comp)["trials"])
    parsed = parse_text("Forest plot: Mortality\nALPHA | n=20 | investigator relayed HR .5\n", TOPIC)
    assert parsed["trial_set"][0]["effect"]["status"] == "RELAYED"
    assert parsed["proposals"]


def test_log_tolerance_and_k_mismatch():
    review, comp = fixture()
    review["outcomes"][0]["trials"][0]["effect"] = fact(.601, "0.601")
    assert any(r["status"] == "MATCH" for r in match(review, comp)["trials"])
    comp["pooled"]["k"] = fact(2, "k=2")
    assert match(review, comp)["K_MATCH"] == "no"


def test_flattened_label_recovery_and_unparsed_binding():
    c = parse_text("Table 1 Characteristics of included studies Study Year Smith 2020 n=500 Jones 2021 n=600 Fig. 2 Mortality", TOPIC)
    assert [r["label"] for r in c["trial_set"]] == ["Smith 2020", "Jones 2021"]
    assert all(r["n"]["status"] == "UNPARSED" for r in c["trial_set"])
    assert all(r["outcome"]["status"] == "UNPARSED" for r in c["trial_set"])
    assert not parse_text("Discussion Smith 2020 n=500", TOPIC)["trial_set"]


def test_enumeration_and_pooled_sentence():
    c = parse_text("Trials included: ALPHA and BETA. Overall analysis of Mortality pooled 2 trials: RR 0.60 (0.40-0.90).", TOPIC)
    assert len(c["trial_set"]) == 2
    assert c["pooled"]["k"]["value"] == 2
    assert not c["membership_complete"]
    wrong = parse_text("Overall analysis of Hospitalization pooled 2 trials: RR 0.60 (0.40-0.90).", TOPIC)
    assert wrong["pooled"]["effect"]["status"] == "UNPARSED"


def test_base_pre_fix_behavior():
    review, comp = fixture()
    # Base compares membership only: it has no timepoint/value diff.
    base = {"trial_set": [{"family_id": "ALPHA"}]}
    base_review = {"outcomes": [{"name": "Mortality", "trials": [{"family_id": "ALPHA", "timepoint": "6 months"}]}]}
    assert comparator_panel.overlaps(base, base_review)[0]["shared"] == ["ALPHA"]
    assert comparator_panel.overlaps({"trial_set": []}, base_review)[0]["comparator_k"] == 0


def test_pooled_ambiguity_and_author_apostrophe():
    c = parse_text(TEXT + "\nForest plot: Mortality\nPooled | k=2 | RR 0.7 (0.5-0.9)\n", TOPIC)
    assert c["pooled"]["k"]["status"] == "UNPARSED"
    assert not c["membership_complete"]
    c = parse_text("Table 1 Patient baseline characteristics. First author, year O’Neil, 2018 113.2 114.2 Fig. 2", TOPIC)
    assert c["trial_set"][0]["label"] == "O’Neil, 2018"


def test_relayed_numbers_never_match():
    review, c = fixture()
    c["trial_set"][1]["effect"]["status"] = "RELAYED"
    c["trial_set"][1]["n1"]["status"] = "RELAYED"
    # Even otherwise matching cells must not turn a relayed row into MATCH.
    assert not any(r["status"] == "MATCH" for r in match(review, c)["trials"])
