"""Synthetic-only reader tests: no real held text is opened."""
import hashlib
import json
from pathlib import Path
import re
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import g1_sentence_reader as sr

CFG = {"intervention_terms": ["tocilizumab"], "comparator_terms": ["saline"],
       "primary_outcome": {"keywords": ["died", "mortality", "hospitalization"]}}
EXAMPLE = ("By day 28, 49 of 249 patients (19.7%) in the tocilizumab group and "
           "25 of 128 (19.5%) in the placebo group had died.")


def test_example_and_provenance():
    text = "  " + EXAMPLE
    c, = sr.sentence_candidates(text, CFG)
    assert [c[k] for k in ("events_t", "n_t", "events_c", "n_c")] == [49, 249, 25, 128]
    assert (c["arm_t_term"], c["arm_c_term"]) == ("tocilizumab", "placebo")
    assert c["outcome_term"] == "died"
    assert c["timepoint_text"] == "day 28"
    assert c["population_text"] is None
    assert c["offset"] == 2
    assert c["sentence_sha256"] == hashlib.sha256(EXAMPLE.encode()).hexdigest()
    assert "sentence" not in c and "text" not in c
    assert sr.sentence_candidates(text, CFG) == [c]


@pytest.mark.parametrize("sentence", [
    "Mortality: 3/20 with tocilizumab and 4/21 with placebo.",
    "Mortality: 3 (15%) of 20 receiving tocilizumab and 4 (19%) of 21 receiving saline.",
    "Mortality: 4 of 21 in the placebo group and 3 of 20 in the tocilizumab group.",
    "Mortality: 3 of 20 tocilizumab arm and 4 of 21 placebo arm.",
    "Mortality: 3 of 20 with tocilizumab and 4 of 21 with usual care.",
    "Mortality: 3 of 20 with tocilizumab and 4 of 21 with standard care.",
    "Hospitalisation: 3 of 20 with tocilizumab and 4 of 21 with saline.",
    "Mortality: 0 of 20 with tocilizumab and 4 of 21 with placebo.",
    "Mortality: 300 of 2,000 with tocilizumab and 400 of 2,100 with placebo.",
])
def test_printed_count_forms(sentence):
    c, = sr.sentence_candidates(sentence, CFG)
    assert c["n_t"] > 0 and c["n_c"] > 0
    assert c["arm_t_term"] == "tocilizumab"


@pytest.mark.parametrize("sentence", [
    "Mortality was 15% with tocilizumab and 19% with placebo.",
    "Mortality: 3 of 20 and 4 of 21 with placebo.",
    "Mortality: 3 of 20 with tocilizumab and 4 of 21 with tocilizumab.",
    "Mortality: 3 of 20 with unknown and 4 of 21 with placebo.",
    "Mortality: 3 of 20 in the unknown group, with tocilizumab and 4 of 21 with placebo.",
    "Mortality was assessed. 3 of 20 with tocilizumab and 4 of 21 with placebo.",
    "Among patients aged 70, mortality: 3 of 20 with tocilizumab and 4 of 21 with placebo.",
    "In the subgroup, mortality: 3 of 20 with tocilizumab and 4 of 21 with placebo.",
    "In women, mortality: 3 of 20 with tocilizumab and 4 of 21 with placebo.",
    "Of the 377 patients, 74 died.",
    "Mortality: 23 of 20 with tocilizumab and 4 of 21 with placebo.",
    "Mortality: 0 of 0 with tocilizumab and 4 of 21 with placebo.",
    "Mortality: 3.5 of 20 with tocilizumab and 4 of 21 with placebo.",
    "Mortality: 3 of 20% with tocilizumab and 4 of 21 with placebo.",
])
def test_rejected_counts(sentence):
    assert sr.sentence_candidates(sentence, CFG) == []


@pytest.mark.parametrize("prefix", ["Smith et al. reported", "Tocilizumab vs. placebo:",
                                     "Mortality, i.e. deaths:", "Fig. 2 and Table 3 show"])
def test_abbreviations_do_not_split(prefix):
    text = prefix + " " + EXAMPLE
    c, = sr.sentence_candidates(text, CFG)
    assert c["offset"] == 0
    assert c["sentence_sha256"] == hashlib.sha256(text.encode()).hexdigest()


@pytest.mark.parametrize("population", ["intention-to-treat", "modified", "per-protocol", "safety"])
def test_population_previous_sentence(population):
    c, = sr.sentence_candidates("We used the " + population + " population. " + EXAMPLE, CFG)
    assert c["population_text"] == population


def test_population_only_immediately_previous():
    c, = sr.sentence_candidates("Safety was assessed. Follow-up ended. " + EXAMPLE, CFG)
    assert c["population_text"] is None


@pytest.mark.parametrize("flag", ["primary", "secondary"])
def test_outcome_flag(flag):
    c, = sr.sentence_candidates("The " + flag + " outcome: " + EXAMPLE, CFG)
    assert c["flag"] == flag


@pytest.mark.parametrize("time", ["at 30 days", "in hospital", "in-hospital"])
def test_timepoint(time):
    c, = sr.sentence_candidates(EXAMPLE.replace("By day 28", time), CFG)
    assert c["timepoint_text"] == time


@pytest.mark.parametrize("measure,code", [("hazard ratio", "HR"), ("odds ratio", "OR"), ("risk ratio", "RR")])
def test_ratio(measure, code):
    c, = sr.sentence_candidates("Mortality " + measure + " 0.75 (95% CI 0.50 to 0.90) with tocilizumab versus placebo.", CFG)
    assert (c["measure"], c["effect"], c["lower"], c["upper"]) == (code, .75, .5, .9)
    assert c["arm_c_term"] == "placebo"


@pytest.mark.parametrize("interval", ["90% CI 0.5-0.9", "98% CI 0.5-0.9", "one-sided 95% CI 0.5-0.9",
                                       "95% one-sided CI 0.5-0.9", "CI 0.5-0.9", "95% CI below 0.9",
                                       "95% CI 0.9-0.5"])
def test_ratio_rejections(interval):
    assert sr.sentence_candidates("Mortality hazard ratio 0.75 (" + interval + ") with tocilizumab versus placebo.", CFG) == []


def test_ratio_missing_arms_and_reverse():
    assert sr.sentence_candidates("Mortality HR 0.75 (95% CI 0.5-0.9).", CFG) == []
    assert sr.sentence_candidates("Mortality HR 0.75 (95% CI 0.5-0.9) with placebo versus tocilizumab.", CFG) == []


def test_multiple_candidates_and_offsets():
    second = EXAMPLE.replace("49 of 249", "48 of 249")
    cs = sr.sentence_candidates(EXAMPLE + " " + second, CFG)
    assert len(cs) == 2
    assert cs[1]["offset"] == len(EXAMPLE) + 1
    assert sr.census_summary(cs)["ambiguous"] is True


def test_population_keyword_excluded():
    cfg = dict(CFG, primary_outcome={"keywords": ["ICU"]}, include={"population_any": ["ICU"]})
    assert sr.sentence_candidates("ICU: 3 of 20 with tocilizumab and 4 of 21 with placebo.", cfg) == []


def test_census_no_digits_except_candidate_counts():
    cs = sr.sentence_candidates("Intention-to-treat analysis. " + EXAMPLE, CFG)
    summary = sr.census_summary(cs)
    assert summary.pop("n_candidates") == 1
    assert not re.search(r"\d", json.dumps(summary))
    assert summary["timepoint_text"] is True and summary["population_text"] is True
    assert not re.search(r"\d", sr._identifier("trial-2026"))
    assert sr._identifier("trial-2") != sr._identifier("trial-~two~")


def test_census_cli_synthetic_only(monkeypatch, capsys):
    import g1_table_failure_diag as diag
    import g1_registry_fill as rf
    import g1_tracker as gt
    tmp_path = Path("synthetic-root")
    files = {}
    monkeypatch.setattr(Path, "read_text", lambda path, **kw: files[path])
    monkeypatch.setattr(Path, "write_text", lambda path, text, **kw: files.__setitem__(path, text))
    monkeypatch.setattr(Path, "is_file", lambda path: path in files)
    monkeypatch.setattr(Path, "mkdir", lambda *args, **kw: None)
    monkeypatch.setattr(sr, "ROOT", tmp_path)
    monkeypatch.setattr(rf, "config", lambda slug: CFG)
    monkeypatch.setattr(gt, "is_matched", lambda row: row.get("matched", False))
    reads = []
    def held(row):
        reads.append(row["label"])
        return (EXAMPLE, "PMC") if row["label"] != "absent" else ("", None)
    monkeypatch.setattr(diag, "_held_text", held)
    base = tmp_path / "outputs" / "k_gap"
    (base / "g1").mkdir(parents=True)
    folder = base / "registry_fill"
    folder.mkdir()
    trials = [{"label": "trial-2026"}, {"label": "absent"}, {"label": "matched", "matched": True},
              {"label": "excluded", "scope_difference": True}]
    (base / "g1" / "topic.json").write_text(json.dumps({"trials": trials}), encoding="utf-8")
    (folder / "PHASE3_OPEN_CENSUS.json").write_text(json.dumps({"rows": [dict(r, slug="topic") for r in trials]}), encoding="utf-8")
    labels = json.dumps([{"slug": "topic", "label": r["label"]} for r in trials])
    assert sr.main(["census", "--labels", labels]) == 0
    raw = (folder / "SENTENCE_CENSUS.json").read_text(encoding="utf-8")
    rows = json.loads(raw)["rows"]
    assert len(rows) == 1 and rows[0].pop("n_candidates") == 1
    assert not re.search(r"\d", json.dumps(rows))
    assert "events_t" not in raw and EXAMPLE not in raw
    assert reads == ["trial-2026", "absent"]
    assert "topic | 1 | 1 | 0" in capsys.readouterr().out


def test_errors_never_print_source(monkeypatch, capsys):
    def fail(labels):
        raise ValueError(EXAMPLE)
    monkeypatch.setattr(sr, "run_census", fail)
    assert sr.main(["census", "--labels", "[]"]) == 1
    captured = capsys.readouterr()
    assert captured.err == "SENTENCE_CENSUS_FAILED\n"
    assert not captured.out

@pytest.mark.parametrize("contrast", ["with tocilizumab versus placebo", "in the tocilizumab group compared with the placebo group"])
def test_ratio_contrast_before_estimate(contrast):
    c, = sr.sentence_candidates("Mortality " + contrast + ": hazard ratio 0.75 (95% CI 0.5-0.9).", CFG)
    assert c["measure"] == "HR" and c["arm_t_term"] == "tocilizumab"


def test_multiple_pairs_in_one_sentence():
    text = "Mortality at day 28: 3 of 20 with tocilizumab and 4 of 21 with placebo; at 30 days: 5 of 20 with tocilizumab and 6 of 21 with placebo."
    assert len(sr.sentence_candidates(text, CFG)) == 2
