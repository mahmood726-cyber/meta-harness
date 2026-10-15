"""Entirely invented inputs. Never open held texts, census files, or caches."""
import hashlib
import json
from pathlib import Path
import socket
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import g1_table_failure_diag as diag

CFG = {"primary_outcome": {"keywords": ["diarrhea"], "timepoint": "day 30"},
       "intervention_terms": ["probiotic"], "comparator_terms": ["placebo"]}
HEADER = "Outcome | Probiotic | Placebo"
POSITIVE = "Outcome | Probiotic (N = 100) | Placebo (N = 100)\nDiarrhea | 12 (12.0) | 20 (20.0)"
CASES = [
    ("NO_TABLE", "No tabulated results are presented."),
    ("NO_OUTCOME_TABLE", HEADER + "\nNausea | 12/100 | 20/100"),
    ("NO_ARM_HEADER", "Outcome | Group A | Group B\nDiarrhea | 12/100 | 20/100"),
    ("ARM_HEADER_NOT_MAPPED", "Outcome | Probiotic and placebo | Unknown\nDiarrhea | 12/100 | 20/100"),
    ("PCT_ONLY", HEADER + "\nDiarrhea | 12% | 20%"),
    ("MULTI_TIMEPOINT_UNRESOLVED", "Outcome | Probiotic day 7 | Placebo day 7 | Probiotic day 30 | Placebo day 30\nDiarrhea | 12/100 | 20/100 | 15/100 | 25/100"),
    ("MULTI_POPULATION_UNRESOLVED", "Outcome | Probiotic ITT | Placebo ITT | Probiotic PP | Placebo PP\nDiarrhea | 12/100 | 20/100 | 10/80 | 18/80"),
    ("DISTRIBUTION_ROWS", "Table 4. Diarrhea episodes\n" + HEADER + "\n0 episodes | 70 | 60\n1 episode | 20 | 30\n2 episodes | 10 | 10"),
    ("EFFECT_ONLY_NO_COUNTS", "Outcome | Probiotic | Placebo | RR (95% CI)\nDiarrhea | Reference | Reference | 0.60 (0.30-1.20)"),
    ("OTHER", HEADER + "\nDiarrhea | 12 | 20"),
    ("NONE_TABLE_TUPLE_BINDS", POSITIVE),
]


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def refused(*args, **kwargs):
        raise AssertionError("Network forbidden")
    monkeypatch.setattr(socket, "create_connection", refused)
    monkeypatch.setattr(socket.socket, "connect", refused)


@pytest.mark.parametrize("expected,text", CASES)
def test_every_class(expected, text):
    result = diag.diagnose(text, CFG)
    assert result["failure_class"] == expected
    assert result == diag.diagnose(text, CFG)


def test_positive_calls_real_parser():
    actual = diag.ta.table_tuple(POSITIVE, diag.ta.outcome_row_terms(CFG), "day 30")
    assert actual is not None
    result = diag.diagnose(POSITIVE, CFG)
    assert result["table_tuple_result"] == sorted(actual[1])
    assert result["table_tuple_result"] == ["events_c", "events_t", "n_c", "n_t"]
    assert result["has_n_header"]
    assert result["cells_count_pct"] == 2
    assert result["row_label_exact"] and not result["row_label_partial"]


def assert_short(value):
    if isinstance(value, str):
        assert len(value) <= 40
    elif isinstance(value, dict):
        for key, child in value.items():
            assert_short(key)
            assert_short(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            assert_short(child)


@pytest.mark.parametrize("expected,text", CASES)
def test_no_output_string_exceeds_40(expected, text):
    text = "A synthetic long caption " * 20 + "\n" + text
    assert_short(diag.diagnose(text, CFG))


def test_no_source_span_or_count_values():
    secret = "Invented unique narrative " * 25
    result = diag.diagnose(secret + "\n" + POSITIVE, CFG)
    encoded = json.dumps(result)
    assert "Invented" not in encoded and "Probiotic" not in encoded
    assert "100" not in encoded


def test_numeric_runs_and_partial_label():
    text = "Table 1. Diarrhea\nOutcome  Probiotic  Placebo\nSevere diarrhea  12  20  0.3\nNausea  15  30  0.4"
    result = diag.diagnose(text, CFG)
    assert result["n_tables"] == result["tables_with_outcome_term"] == 1
    assert result["row_label_partial"] and not result["row_label_exact"]
    assert result["has_arm_header"]
    assert result["arm_header_mapped"]
    assert result["failure_class"] == "OTHER"


def test_isolated_numeric_line_is_not_a_run():
    assert diag.diagnose("There were 12, 20 and 30 participants.", CFG)["n_tables"] == 0


def test_best_table_and_separate_blocks():
    text = HEADER + "\nSevere diarrhea | 12/100 | 20/100\n\n" + HEADER + "\nDiarrhea | 12% | 20%"
    result = diag.diagnose(text, CFG)
    assert result["n_tables"] == result["tables_with_outcome_term"] == 2
    assert result["best_table_index"] == 1
    assert result["failure_class"] == "PCT_ONLY"


def test_best_tie_is_earliest():
    text = HEADER + "\nDiarrhea | 12% | 20%"
    assert diag.diagnose(text + "\n\n" + text, CFG)["best_table_index"] == 0


def test_outcome_in_caption_and_subgroups():
    result = diag.diagnose("Table 1. Diarrhea\n" + HEADER + "\nWomen | 12/100 | 20/100", CFG)
    assert result["tables_with_outcome_term"] == 1
    assert result["has_stratified_subgroup_rows"]
    assert not result["row_label_exact"] and not result["row_label_partial"]


def test_population_terms_excluded():
    cfg = dict(CFG, primary_outcome={"keywords": ["diarrhea", "ICU"]},
               include={"population_any": ["ICU"]})
    assert diag.diagnose(HEADER + "\nICU | 12 | 20", cfg)["failure_class"] == "NO_OUTCOME_TABLE"


@pytest.mark.parametrize("n", ["n=100", "N = 100", "(n = 100)"])
def test_n_variants(n):
    result = diag.diagnose(f"Outcome | Probiotic {n} | Placebo {n}\nDiarrhea | 12/100 | 20/100", CFG)
    assert result["has_n_header"] and result["cells_count_pct"] == 2


def test_baseline_counts_do_not_hide_target_percentages():
    result = diag.diagnose(HEADER + "\nNausea | 12/100 | 20/100\nDiarrhea | 8% | 9%", CFG)
    assert result["failure_class"] == "PCT_ONLY"


def test_percent_column_headings():
    result = diag.diagnose("Outcome | Probiotic (%) | Placebo (%)\nDiarrhea | 8 | 9", CFG)
    assert result["cells_pct_only"] == 2
    assert result["failure_class"] == "PCT_ONLY"


def test_count_percentage_and_fraction_cells():
    result = diag.diagnose(HEADER + "\nDiarrhea | 12 (8.5) | 12/140", CFG)
    assert result["cells_count_pct"] == 2
    assert result["cells_pct_only"] == 0


def test_arm_names_in_body_are_not_headers():
    result = diag.diagnose("Outcome | Group A | Group B\nDiarrhea | 12/100 | 20/100\nProbiotic placebo | 1 | 2", CFG)
    assert result["failure_class"] == "NO_ARM_HEADER"


def test_numeric_timepoint_headers():
    text = "Outcome | Probiotic | Placebo\nTime | 7 days | 30 days\nDiarrhea | 12/100 | 20/100"
    result = diag.diagnose(text, CFG)
    assert result["has_multiple_timepoint_columns"]
    assert result["failure_class"] == "MULTI_TIMEPOINT_UNRESOLVED"


def test_population_precedes_time_and_mapping():
    text = "Outcome | Probiotic ITT day 7 | Placebo PP day 30\nDiarrhea | 12/100 | 20/100"
    result = diag.diagnose(text, CFG)
    assert result["has_multiple_timepoint_columns"]
    assert result["has_itt_pp_split_columns"]
    assert result["failure_class"] == "MULTI_POPULATION_UNRESOLVED"


def test_success_precedes_structural_flags():
    text = POSITIVE.replace("Probiotic (", "Probiotic ITT day 7 (").replace("Placebo (", "Placebo PP day 30 (")
    result = diag.diagnose(text, CFG)
    assert result["failure_class"] == "NONE_TABLE_TUPLE_BINDS"


def test_numerical_percent_mismatch_is_other():
    text = POSITIVE.replace("12 (12.0)", "12 (99.0)")
    assert diag.diagnose(text, CFG)["failure_class"] == "OTHER"


def test_timepoint_row_resolution_passed_to_parser():
    text = POSITIVE.replace("Diarrhea", "Diarrhea day 7") + "\nDiarrhea day 30 | 15 (15.0) | 25 (25.0)"
    assert diag.diagnose(text, CFG)["failure_class"] == "NONE_TABLE_TUPLE_BINDS"
    cfg = dict(CFG, primary_outcome={"keywords": ["diarrhea"]})
    assert diag.diagnose(text, cfg)["table_tuple_result"] is None


def test_runtime_held_lookup_in_memory(monkeypatch):
    """Mock all filesystem accesses; no actual held text is read."""
    doi = "10.synthetic/invented"
    key = hashlib.sha1(doi.encode()).hexdigest()[:16]
    texts = {"123.txt": POSITIVE, key + ".txt": HEADER}
    monkeypatch.setattr(Path, "is_file", lambda p: p.name in texts)
    monkeypatch.setattr(Path, "stat", lambda p: type("Stat", (), {"st_size": 100})())
    monkeypatch.setattr(Path, "read_text", lambda p, **kw: texts[p.name])
    assert diag._held_text({"pmid": "123", "source": {"doi": doi}}) == (POSITIVE, "PMC")
    del texts["123.txt"]
    assert diag._held_text({"pmid": "123", "source": {"doi": doi}}) == (HEADER, "UNPAYWALL")
    assert diag._held_text({"pmid": "456"}) == ("", None)


def test_cli_in_memory_only(monkeypatch, capsys):
    import g1_registry_fill as rf
    slug, label = "synthetic-topic-" * 5, "Invented trial label " * 5
    docs = {name: {"rows": [{"slug": slug, "label": label, "pmid": "123"},
                            {"slug": slug, "label": "not selected", "pmid": "456"}]}
            for name in ("PHASE3_OPEN_CENSUS.json", "PHASE3_OPEN_CENSUS_REGISTERED.json",
                         "PHASE3_OPEN_CENSUS_COMPANIONS.json")}
    monkeypatch.setattr(diag, "_json", lambda p: docs[p.name])
    monkeypatch.setattr(Path, "is_dir", lambda p: p.name.startswith("phase3"))
    monkeypatch.setattr(Path, "is_file", lambda p: p.name in docs)
    monkeypatch.setattr(Path, "mkdir", lambda *a, **kw: None)
    written = []
    monkeypatch.setattr(Path, "write_text", lambda p, text, **kw: written.append((p.name, text)))
    monkeypatch.setattr(diag, "_held_text", lambda row: (POSITIVE, "PMC"))
    monkeypatch.setattr(rf, "config", lambda slug: CFG)
    assert diag.main(["run", "--census", "phase3", "phase3_registered", "phase3_companions",
                      "--labels", json.dumps([{"slug": slug, "label": label}])]) == 0
    assert written[0][0] == "TABLE_FAILURE_DIAG.json"
    report = json.loads(written[0][1])
    assert len(report["rows"]) == 1
    assert report["counts"][0]["count"] == 1
    assert_short(report)
    out = capsys.readouterr().out
    assert "NONE_TABLE_TUPLE_BINDS" in out and "Probiotic" not in out
    assert all(len(field.strip()) <= 40 for line in out.splitlines() for field in line.split("|"))


def test_cli_error_does_not_expose_source(monkeypatch, capsys):
    def fail(*args):
        raise ValueError("Sensitive synthetic text " * 20)
    monkeypatch.setattr(diag, "run", fail)
    assert diag.main(["run", "--census", "unused", "--labels", "[]"]) == 1
    assert capsys.readouterr().err.strip() == "DIAGNOSTIC_FAILED"
