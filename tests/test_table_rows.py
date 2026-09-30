import json

import pytest

from harness.table_rows import parse, select, typed
from harness.extract import extract_effect, extract_trial


def excerpt(tmp_path, body, comments=""):
    path = tmp_path / "plant.tables.txt"
    path.write_text("# held sha256 " + "a" * 64 + "\n" + comments +
                    "\n=== TABLES (excerpt) ===\n" + body, encoding="utf-8")
    return parse(path)[0]


HEADER = "Outcome | Drug (N=100) n (%) | Control (N=200) n (%) | HR/OR\n"
ROW = "Major bleeding | 10 (10) | 40 (20) | 0.60 (0.40-0.90)\n"


def test_footnote_override_and_negative(tmp_path):
    t = excerpt(tmp_path, "TABLE Safety\n" + HEADER + ROW + "Footnote: Estimates are hazard ratios.\n")
    v = typed(t["rows"][0], t)
    assert (v["measure"], v["measure_basis"]) == ("HAZARD_RATIO", "footnote")
    t["footnotes"] = []
    assert typed(t["rows"][0], t)["measure"] == "UNKNOWN"
    t["footnotes"] = ["Footnote: Odds ratios for dyspnoea."]
    assert typed(t["rows"][0], t)["measure"] == "UNKNOWN"
    t["footnotes"] = ["Footnote: Hazard ratios for major bleeding."]
    assert typed(t["rows"][0], t)["measure"] == "HAZARD_RATIO"
    t["footnotes"].append("Footnote: Odds ratios for major bleeding.")
    assert typed(t["rows"][0], t)["measure"] == "UNKNOWN"


@pytest.mark.parametrize("label,keyword,flag", [
    ("non-CABG major bleeding", "major bleeding", "NON_CABG"),
    ("major bleeding not related to CABG", "major bleeding", "NON_CABG"),
    ("dyspnoea leading to discontinuation", "dyspnoea", "LEADING_TO_DISCONTINUATION"),
    ("dyspnoea causing discontinuation", "dyspnoea", "LEADING_TO_DISCONTINUATION"),
    ("serious dyspnoea", "dyspnoea", "SERIOUS"),
])
def test_variant_selection(tmp_path, label, keyword, flag):
    t = excerpt(tmp_path, "TABLE Safety\n" + HEADER + ROW.replace("Major bleeding", label))
    selected, reason = select(t, [keyword], [flag])
    assert selected is None and flag in reason and label in reason
    t["rows"].append(dict(label=keyword, cells=t["rows"][0]["cells"]))
    assert select(t, [keyword], [flag])[0]["label"] == keyword


def test_parent_and_ambiguous_selection(tmp_path):
    t = excerpt(tmp_path, "TABLE Safety\n" + HEADER + "Serious adverse events\n" + ROW)
    assert select(t, ["major bleeding"], ["SERIOUS"])[0] is None
    t["rows"][0].pop("parent_label")
    t["rows"].append(t["rows"][0].copy())
    assert "ambiguous" in select(t, ["major bleeding"], [])[1]
    assert select(t, ["absent"], [])[0] is None
    assert "unknown excluded" in select(t, ["major bleeding"], ["TYPO"])[1]


def test_separate_candidates_and_negative(tmp_path):
    t = excerpt(tmp_path, "TABLE Safety\n" + HEADER.replace("HR/OR", "Hazard ratio") + ROW)
    v = typed(t["rows"][0], t)
    published, reconstructed = v["candidates"]
    assert (published["measure"], published["derivation"], published["effect"]["value"]) == ("HAZARD_RATIO", "PUBLISHED", 0.6)
    assert (reconstructed["measure"], reconstructed["derivation"], reconstructed["effect"]["value"]) == ("RISK_RATIO", "RECONSTRUCTED", 0.5)
    t["rows"][0]["cells"][1] = "0 (0)"
    assert len(typed(t["rows"][0], t)["candidates"]) == 1
    t["rows"][0]["cells"][-1] = "-"
    assert typed(t["rows"][0], t)["candidates"] == []


@pytest.mark.parametrize("sep", ["-", "–", "â€“", " to ", ", "])
def test_ci_encodings_and_metadata(tmp_path, sep):
    t = excerpt(tmp_path, "TABLE Safety population\n" + HEADER + ROW.replace("0.40-0.90", "0.40" + sep + "0.90"),
                "# window: all treated patients through 7 days after last dose\n")
    v = typed(t["rows"][0], t)
    assert v["effect"] == dict(value=0.6, ci_low=0.4, ci_high=0.9)
    assert any("through 7 days after" in w for w in v["window"])
    assert "all treated patients" in v["analysis_population"]
    assert t["source_sha"] == "a" * 64


def test_mixed_events_rates_and_patient_counts(tmp_path):
    t = excerpt(tmp_path, "TABLE Safety\nOutcome | Drug (N=100) participants no. (%) | Drug events | Control (N=200) participants no. (%) | Control events\nGI | 10 (10) | 30 | 40 (20) | 60\n")
    v = typed(t["rows"][0], t)
    assert v["count_unit"] == "UNKNOWN"
    assert [a["count_unit"] for a in v["arms"]] == ["PATIENTS", "EVENTS", "PATIENTS", "EVENTS"]
    assert v["candidates"][0]["effect"]["value"] == 0.5
    t = excerpt(tmp_path, "TABLE Events\nOutcome | Drug N | Drug rate | Control N | Control rate | HR\nPain | 494 | 8.92 | 467 | 8.50 | 1.04 (0.92-1.19)\n")
    v = typed(t["rows"][0], t)
    assert [a["n_events"] for a in v["arms"]] == [494, 467]
    assert all(a["percent"] is None for a in v["arms"])
    assert len(v["candidates"]) == 1


def test_invalid_alignment_ci_and_missing_sha(tmp_path):
    t = excerpt(tmp_path, "TABLE Safety\n" + HEADER + ROW.replace("0.40-0.90", "0.90-0.40"))
    assert any("invalid" in s for s in typed(t["rows"][0], t)["refusals"])
    t["rows"][0]["cells"].insert(0, "HR")
    assert typed(t["rows"][0], t)["arms"] == []
    path = tmp_path / "bad.tables.txt"
    path.write_text("=== TABLES (excerpt) ===", encoding="utf-8")
    with pytest.raises(ValueError, match="source sha256"):
        parse(path)


def test_base_harness_same_excerpt_bytes(tmp_path):
    outputs = {}
    for name, body, keyword in [
        ("footnote", "TABLE Safety\n" + HEADER + ROW + "Footnote: Estimates are hazard ratios.\n", "major bleeding"),
        ("variant", "TABLE Safety\n" + HEADER + ROW.replace("Major bleeding", "non-CABG major bleeding"), "major bleeding"),
        ("discontinuation", "TABLE Safety\n" + HEADER + ROW.replace("Major bleeding", "dyspnoea leading to discontinuation"), "dyspnoea"),
        ("two_candidates", "TABLE Safety\n" + HEADER.replace("HR/OR", "Hazard ratio") + ROW, "major bleeding"),
    ]:
        excerpt(tmp_path, body)
        text = (tmp_path / "plant.tables.txt").read_text(encoding="utf-8")
        outputs[name] = {"extract_effect": extract_effect(text),
                         "extract_trial": extract_trial(text, [keyword], ["Drug"], ["Control"])}
        assert outputs[name]["extract_effect"] is None
        assert outputs[name]["extract_trial"]["absent"] is True
    print("BASE_OUTPUT=" + json.dumps(outputs, ensure_ascii=False, sort_keys=True))
