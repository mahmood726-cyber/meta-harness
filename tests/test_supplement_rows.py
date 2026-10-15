"""Synthetic plants prove column binding and primary-copy gates without external calls."""
import copy
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import g1_supplement_rows as sr

CFG = {"primary_outcome": {"keywords": ["28-day all-cause mortality"]},
       "intervention_terms": ["Drug"], "comparator_terms": ["Placebo"]}
TEXT = ("Trial | Mortality n/N (%) | Length of stay\n"
        "Trial | Drug | Placebo | Drug | Placebo\n"
        "TRIALX | 10/100 (10%) | 20/100 (20%) | 5 | 6")
EFFECT_TEXT = ("Drug versus placebo\n"
               "Trial | HR (95% CI) for mortality | Other\n"
               "ZETAX | 0.80 (0.65-0.98) | x")


def test_PLANT_effect_row_read_with_measure_from_header():
    rows, reasons = sr.typed_rows(EFFECT_TEXT, "ZETAX", "meta", "s.docx", CFG)
    assert reasons == [] and len(rows) == 1
    row = rows[0]
    assert (row.measure, row.effect, row.lower, row.upper) == ("HR", "0.80", "0.65", "0.98")
    assert row.provenance == "TYPED_SUPPLEMENT_EFFECT"
    assert (row.events_t, row.n_t, row.events_c, row.n_c) == (None, None, None, None)
    row, classification = sr.classify(row, {}, CFG)
    assert classification == "SECONDARY_PROVISIONAL"
    assert {"TIMEPOINT_NOT_STATED_BY_META", "OUTCOME_FAMILY_ONLY"} <= set(row.reasons)


def test_effect_without_measure_gives_no_row():
    rows, reasons = sr.typed_rows(EFFECT_TEXT.replace("HR ", ""), "ZETAX", "meta", "s.docx", CFG)
    assert rows == [] and reasons == ["EFFECT_MEASURE_NOT_STATED"]


@pytest.mark.parametrize("effect", ["0.60", "1.10"])
def test_effect_outside_ci_gives_no_row(effect):
    rows, reasons = sr.typed_rows(EFFECT_TEXT.replace("0.80", effect), "ZETAX", "meta", "s.docx", CFG)
    assert rows == [] and reasons == ["EFFECT_OUTSIDE_CI"]


@pytest.mark.parametrize("caption", ["", "Drug and placebo", "Placebo versus Drug"])
def test_effect_orientation_required(caption):
    rows, reasons = sr.typed_rows(EFFECT_TEXT.replace("Drug versus placebo", caption),
                                  "ZETAX", "meta", "s.docx", CFG)
    assert rows == [] and reasons == ["EFFECT_ORIENTATION_NOT_STATED"]


@pytest.mark.parametrize("estimand,expected", [("RR", "SECONDARY_PROVISIONAL"), ("HR", "PRIMARY_VERIFIED")])
def test_PLANT_effect_on_another_estimand_is_never_primary(monkeypatch, estimand, expected):
    cfg = copy.deepcopy(CFG)
    cfg["primary_outcome"]["estimand"] = estimand
    rows, _ = sr.typed_rows(EFFECT_TEXT, "ZETAX", "meta", "s.docx", cfg)

    def verify(row, sources, terms):
        row.state = sr.VERIFIED
        row.reasons = []
        return row

    monkeypatch.setattr(sr, "verify_typed", verify)
    held = {"text": EFFECT_TEXT, "text_origin": "UNPAYWALL", "doi_licence": "cc-by", "pmid": "primary"}
    row, classification = sr.classify(rows[0], held, cfg)
    assert classification == expected
    assert ("MEASURE_NOT_TOPIC_ESTIMAND" in row.reasons) == (estimand != "HR")


@pytest.mark.parametrize("measure,expected", [("HR", "HR"), ("hazard ratio", "HR"), ("RR", "RR"),
                                            ("risk ratio", "RR"), ("relative risk", "RR"),
                                            ("OR", "OR"), ("odds ratio", "OR")])
@pytest.mark.parametrize("location", ["header", "above", "caption"])
def test_effect_measure_sources(measure, expected, location):
    text = EFFECT_TEXT.replace("HR ", "")
    if location == "header":
        text = text.replace("(95% CI)", measure + " (95% CI)")
    elif location == "above":
        text = text.replace("Trial |", measure + " | Effect\nTrial |", 1)
    else:
        text = text.replace("Drug versus placebo", measure + ": Drug versus placebo")
    rows, reasons = sr.typed_rows(text, "ZETAX", "meta", "s.docx", CFG)
    assert reasons == [] and rows[0].measure == expected


def test_effect_ambiguous_measure_gives_no_row():
    text = EFFECT_TEXT.replace("Drug versus placebo", "RR: Drug versus placebo")
    rows, reasons = sr.typed_rows(text, "ZETAX", "meta", "s.docx", CFG)
    assert rows == [] and reasons == ["EFFECT_MEASURE_AMBIGUOUS"]


@pytest.mark.parametrize("separator", ["-", "–", "—", ",", "to"])
def test_effect_preserves_printed_precision_and_interval_separators(separator):
    text = EFFECT_TEXT.replace("0.80 (0.65-0.98)", f"1.10 [1.00{separator}1.20]")
    rows, reasons = sr.typed_rows(text, "ZETAX", "meta", "s.docx", CFG)
    assert reasons == []
    assert (rows[0].effect, rows[0].lower, rows[0].upper) == ("1.10", "1.00", "1.20")


@pytest.mark.parametrize("caption", ["Drug vs placebo", "Drug compared with placebo"])
def test_effect_orientation_phrases(caption):
    rows, _ = sr.typed_rows(EFFECT_TEXT.replace("Drug versus placebo", caption), "ZETAX", "meta", "s.docx", CFG)
    assert len(rows) == 1


def test_effect_orientation_from_arm_cells():
    text = EFFECT_TEXT.replace("Drug versus placebo\n", "").replace(
        "ZETAX |", "Trial | Drug | Placebo\nZETAX |")
    rows, reasons = sr.typed_rows(text, "ZETAX", "meta", "s.docx", CFG)
    assert reasons == [] and len(rows) == 1


def test_effect_requires_exactly_one_pattern_in_outcome_cell():
    text = EFFECT_TEXT.replace("0.80 (0.65-0.98)", "0.80 (0.65-0.98); 1.10 (1.00-1.20)")
    rows, _ = sr.typed_rows(text, "ZETAX", "meta", "s.docx", CFG)
    assert rows == []


@pytest.mark.parametrize("prefix", ["HR: Drug versus placebo\n\n\n\n", "HR: Drug versus placebo\nUnrelated caption\n"])
def test_effect_caption_is_nearest_and_within_three_lines(prefix):
    text = prefix + EFFECT_TEXT.split("\n", 1)[1].replace("HR ", "")
    rows, reasons = sr.typed_rows(text, "ZETAX", "meta", "s.docx", CFG)
    assert rows == [] and reasons == ["EFFECT_MEASURE_NOT_STATED"]


@pytest.fixture(autouse=True)
def no_external_io(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Unexpected external I/O")
    import socket
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    for obj, methods in ((sr.ta, ["targets", "evidence", "pmc_copy", "comparator_pmid"]),
                         (sr.rf, ["config"]), (sr.sb, ["comparator_pmid", "meta_aliases"]),
                         (sr.of, ["_call"]), (sr.k_gap, ["comparator_supplements"]),
                         (sr, ["read_sweep", "held_jats", "pmcid_of"])):
        for method in methods:
            monkeypatch.setattr(obj, method, forbidden)


@pytest.fixture
def route(monkeypatch):
    monkeypatch.setattr(sr.rf, "config", lambda slug: copy.deepcopy(CFG))
    monkeypatch.setattr(sr.ta, "targets", lambda *a: ({}, [{"label": "TRIALX", "pmid": "primary", "ncts": []}]))
    monkeypatch.setattr(sr.ta, "comparator_pmid", lambda *a: "comparator")
    monkeypatch.setattr(sr.sb, "comparator_pmid", lambda *a: "comparator")
    monkeypatch.setattr(sr.sb, "meta_aliases", lambda m: {m, "10.synthetic/comparator"} if m == "comparator" else {m})
    monkeypatch.setattr(sr, "read_sweep", lambda slug: {"trials": [{"label": "TRIALX", "metas_found": ["meta"]}]})
    monkeypatch.setattr(sr, "held_jats", lambda m: (["s2.docx"], "CC BY"))
    monkeypatch.setattr(sr, "pmcid_of", lambda m: "PMC-synthetic")
    calls = []

    def fetch(meta, pmcid, hrefs, date, offline=False):
        calls.append((meta, offline, date))
        return {"state": "OK", "text": "=== SUPPLEMENT s2.docx ===\n" + TEXT,
                "files": [{"file": "s2.docx", "text_chars": len(TEXT)}]}

    monkeypatch.setattr(sr.k_gap, "comparator_supplements", fetch)
    monkeypatch.setattr(sr.ta, "evidence", lambda *a: ({}, {"text": "", "pmid": "primary", "text_origin": None}))
    return calls


def test_PLANT_supplement_row_is_read_by_column_and_arm_header(route):
    out = sr.run_slug("synthetic", offline=True)
    assert route == [("meta", True, sr.DATE)]
    assert len(out["rows"]) == 1
    row = out["rows"][0]
    assert [row[k] for k in ("events_t", "n_t", "events_c", "n_c")] == [10, 100, 20, 100]
    assert row["location"] == {"kind": "supplement", "id": "s2.docx", "row_label": "TRIALX"}
    assert row["provenance"] == "TYPED_SUPPLEMENT"
    assert row["class"] == "SECONDARY_PROVISIONAL"
    assert set(row["reasons"]) == {"TIMEPOINT_NOT_STATED_BY_META", "OUTCOME_FAMILY_ONLY"}


def test_PLANT_comparator_meta_is_never_a_source(route, monkeypatch):
    monkeypatch.setattr(sr, "read_sweep", lambda slug: {"trials": [{"label": "TRIALX", "metas_found":
                        ["comparator", "10.SYNTHETIC/COMPARATOR", "alias", "meta"]}]})
    monkeypatch.setattr(sr.sb, "meta_aliases", lambda m: {m, "10.synthetic/comparator"}
                        if m in {"comparator", "alias"} else {m})
    out = sr.run_slug("synthetic")
    assert list(out["metas"]) == ["meta"]
    assert [c[0] for c in route] == ["meta"]


def test_ambiguous_columns_give_no_row():
    text = TEXT.replace("Length of stay", "Death n/N")
    rows, reasons = sr.typed_rows(text, "TRIALX", "meta", "s.docx", CFG)
    assert not rows
    assert "AMBIGUOUS_OUTCOME_COLUMNS" in reasons


def test_PLANT_unlicensed_primary_copy_is_pending_never_verified(route, monkeypatch):
    monkeypatch.setattr(sr.ta, "evidence", lambda *a: ({}, {"text": TEXT, "text_origin": "PMC", "pmid": "primary"}))
    monkeypatch.setattr(sr.ta, "pmc_copy", lambda p: {"licence": "NOT_OPEN"})

    def forbidden(*a):
        pytest.fail("Unlicensed text reached verification")

    monkeypatch.setattr(sr, "verify_typed", forbidden)
    out = sr.run_slug("synthetic")
    assert out["rows"][0]["class"] == "PRIMARY_VERIFY_PENDING_RULING"
    assert out["rows"][0]["state"] == sr.UNVERIFIED


def test_verified_when_primary_text_holds_the_numbers(route, monkeypatch):
    monkeypatch.setattr(sr.ta, "evidence", lambda *a: ({}, {"text": TEXT, "text_origin": "PMC", "pmid": "primary"}))
    monkeypatch.setattr(sr.ta, "pmc_copy", lambda p: {"licence": "CC"})

    def verify(row, sources, terms):
        assert sources == [("text", "PMID primary", TEXT)]
        assert terms == CFG["primary_outcome"]["keywords"]
        row.state = sr.VERIFIED
        return row

    monkeypatch.setattr(sr, "verify_typed", verify)
    assert sr.run_slug("synthetic")["rows"][0]["class"] == "PRIMARY_VERIFIED"


@pytest.mark.parametrize("text,reason", [
    (TEXT.replace("Drug", "Unknown"), "NO_ARM_HEADER"),
    (TEXT.replace("10/100 (10%) | 20/100 (20%) | 5", "10/100 (10%) | 5 | 20/100 (20%)"),
     "COUNTS_NOT_ADJACENT_AT_OUTCOME"),
    (TEXT.replace("TRIALX", "TRIALXY"), "NO_TRIAL_ROW"),
])
def test_refuses_missing_binding(text, reason):
    rows, reasons = sr.typed_rows(text, "TRIALX", "meta", "s.docx", CFG)
    assert not rows and reason in reasons


def test_reversed_arms_and_caption_timepoint():
    text = "Table S2: 28-day mortality\n" + TEXT.replace("Drug | Placebo", "Placebo | Drug")
    rows, _ = sr.typed_rows(text, "TRIALX", "meta", "s.docx", CFG)
    assert rows[0].events_t == 20 and rows[0].events_c == 10
    assert rows[0].timepoint == "28-day"


def answer():
    return {"verdict": "FOUND", "quote": TEXT, "measure": "COUNTS", "events_t": 10, "n_t": 100,
            "events_c": 20, "n_c": 100, "outcome_as_stated": "Mortality", "timepoint_as_stated": ""}


def test_model_gate_requires_verbatim_trial_and_each_number():
    a = answer()
    assert sr.model_gate(a, TEXT, "TRIALX")
    assert not sr.model_gate(dict(a, events_t=1), TEXT, "TRIALX")
    assert not sr.model_gate(dict(a, quote="10/100 (10%) | 20/100 (20%)"), TEXT, "TRIALX")
    assert not sr.model_gate(dict(a, quote=TEXT + "invented"), TEXT, "TRIALX")


@pytest.mark.parametrize("states,decision", [
    (["RAN_OK", "RAN_OK"], "MODEL_ADMITTED_BOTH_READERS"),
    (["RAN_OK", "UNAVAILABLE"], "WAITING_READER_UNAVAILABLE"),
    (["REFUSED_LICENCE", "RAN_OK"], "MODEL_REFUSED_LICENCE"),
])
def test_recorded_readers_only(monkeypatch, states, decision):
    calls = []

    def call(prompt, reader, purpose, digest):
        assert b'"pmid": "meta"' in prompt and len(digest) == 64
        calls.append(reader[0])
        return {"state": states[len(calls) - 1], "record_id": "synthetic-" + reader[0], "answer": answer()}

    monkeypatch.setattr(sr.of, "_call", call)
    monkeypatch.setattr(sr.rf, "_answer", lambda rec: rec["answer"])
    row, audit = sr.model_row(TEXT, "TRIALX", "meta", "s.docx", "CC BY", CFG)
    assert audit["decision"] == decision
    assert calls == ["A", "B"]
    assert bool(row) == (decision == "MODEL_ADMITTED_BOTH_READERS")
    if row:
        assert row.provenance == "MODEL_PROPOSAL:synthetic-A,synthetic-B"
        assert row.state == sr.UNVERIFIED


def test_restricted_meta_never_reaches_reader():
    row, audit = sr.model_row(TEXT, "TRIALX", "meta", "s.docx", "cc-by-nc", CFG)
    assert row is None and audit["decision"] == "MODEL_REFUSED_LICENCE"


def test_adjudicator_must_match_a_gated_reader(monkeypatch):
    replies = [answer(), dict(answer(), events_t=20, events_c=10), dict(answer(), events_t=100)]
    monkeypatch.setattr(sr.of, "_call", lambda p, r, *a: {"state": "RAN_OK", "record_id": r[0], "answer": replies.pop(0)})
    monkeypatch.setattr(sr.rf, "_answer", lambda rec: rec["answer"])
    row, audit = sr.model_row(TEXT, "TRIALX", "meta", "s.docx", "cc0", CFG)
    assert row is None and audit["decision"] == "MODEL_NOT_ADMITTED_READERS_DISAGREE"


def test_PLANT_a_title_labelled_trial_is_named_by_its_sourced_acronym():
    # 14 Oct: 'Effect of Dexamethasone on Days Alive ...' had only the name 'Effect'; the supplement row says 'CoDEX'
    import g1_supplement_rows as s
    label = "Effect of Drug Z on Days Alive and Free of Support"
    assert "Effect" not in s.names(label)
    s.EXTRA_NAMES[label] = ["ZETAX"]
    try:
        assert "ZETAX" in s.names(label)
    finally:
        s.EXTRA_NAMES.pop(label, None)


def test_PLANT_a_row_far_below_its_header_keeps_the_header():
    # 14 Oct: the sixth row of a table (REMAP-CAP) lost its header: the lookup scanned only 6 lines up
    import g1_supplement_rows as s
    cfg = {"primary_outcome": {"keywords": ["mortality"]}, "include": {}, "intervention_terms": ["drug"],
           "comparator_terms": ["placebo"]}
    head = ["Trial | Mortality n/N (%) | Other", "Trial | Drug | Placebo | Drug | Placebo"]
    filler = [f"OTHER{i} | {i}/50 (2%) | {i + 1}/50 (2%) | x" for i in range(1, 8)]
    text = "\n".join(head + filler + ["ZETAX | 10/100 (10%) | 20/100 (20%) | x"])
    import g1_trial_acquire as ta
    orig = ta.outcome_terms
    ta.outcome_terms = lambda c: ["mortality"]
    try:
        rows, _r = s.typed_rows(text, "ZETAX", "1", "f.docx", cfg)
    finally:
        ta.outcome_terms = orig
    assert [(r.events_t, r.n_t, r.events_c, r.n_c) for r in rows] == [(10, 100, 20, 100)]


def test_PLANT_another_agents_column_never_passes_as_the_intervention():
    # 15 Oct: a corticosteroid meta's 'Steroids | SOC/placebo' row for REMAP-CAP was taken for the TOCILIZUMAB topic
    import g1_supplement_rows as s
    toci = {"primary_outcome": {"keywords": ["mortality"]}, "include": {"intervention_any": ["tocilizumab"]},
            "intervention_terms": ["tocilizumab"], "comparator_terms": ["standard care"]}
    assert s.arm("Steroids", toci) is None
    assert s.arm("Tocilizumab", toci) == "t" and s.arm("SOC/placebo", toci) == "c"
