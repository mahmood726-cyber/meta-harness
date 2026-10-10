"""Tranexamic D10 comparator binding, rebased onto main without the D10 topic/protocol amendments (main's tranexamic
primary is already 'Death due to bleeding'). Plants carried from g1/binding-on-d0848a72 (tests/test_g1_binding_counts.py
and tests/test_g1_codex_review_1008.py, 8 Oct), copied as fixed strings."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402
import g1_comparator_table_result as tr  # noqa: E402

TX_KW = ["death due to bleeding", "death from post-partum haemorrhage", "death from postpartum haemorrhage"]


def test_a_served_comparator_result_for_another_outcome_is_not_our_comparison():
    # 8 Oct (gap list, tranexamic): the tracker took the served review's comparator.reported[0] -- 'Life-threatening
    # postpartum bleeding', the COMPARATOR's primary -- as the result for OUR primary 'Death due to bleeding'
    assert not gt.reported_is_our_outcome("Life-threatening postpartum bleeding", "Death due to bleeding", TX_KW)
    assert gt.reported_is_our_outcome("Death due to bleeding", "Death due to bleeding", TX_KW)
    assert gt.reported_is_our_outcome("Recurrent VTE", "Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or "
                                      "VTE-related death)", ["recurrent VTE", "recurrent venous thromboembolism"])
    assert not gt.reported_is_our_outcome(None, "Death due to bleeding", TX_KW)  # an UNNAMED result cannot be verified


def test_only_a_results_row_with_two_arm_cells_is_the_comparators_result():
    assert tr.is_result_row("Death due to bleeding | WOMAN, 1 WOMAN-2, 10 TRAAP | 159/27 307 | 194/27 097 | "
                            "0·81 (0·66–1·00) | 0·52 |")
    assert not tr.is_result_row("Diagnosis of postpartum haemorrhage at baseline | Yes | No † | No | No | No |")
    assert tr._n("27 307") == 27307 and tr._f("0·81") == 0.81


def test_counts_6_a_header_search_never_crosses_a_table_caption():
    lines = ["Outcome | DrugA (n/N) | placebo (n/N) | OR (95% CI)", "Stroke | 10/100 | 20/100 | 0.44 (0.20–0.99)",
             "Table 2", "Outcome | placebo | DrugA | OR (95% CI)", "All-cause mortality | 30/100 | 10/100 | 3.86 (1.76–8.45)"]
    assert tr.header_above(lines, 4) is None
    assert tr.header_above(lines, 1) == 0


def test_counts_7_alignment_never_indexes_past_the_row():
    rc = ["All-cause mortality", "0.44 (0.20–0.99)", "10/100", "20/100"]
    assert len(tr.aligned(rc, [2, 3], 1)) == 1


def test_arm_roles_are_read_from_our_terms_never_assumed():
    t = {"intervention_terms": ["tranexamic acid", "TXA"], "comparator_terms": ["placebo", "control"]}
    assert tr._arm("Tranexamic acid group (n/N)", t) == "intervention"
    assert tr._arm("Placebo group (n/N)", t) == "control"
    # the drug a placebo mimics is never the intervention arm: the whole 'placebo for X' clause is removed, so the
    # column is unmapped and the reader refuses (T2_HEADER) rather than guessing
    assert tr._arm("Placebo for tranexamic acid", t) != "intervention"
    assert tr._arm("Tranexamic acid or placebo", t) is None                # both named: unmapped
    assert tr._term_re([]).search("anything") is None                      # an empty vocabulary matches nothing


def test_the_recorded_tranexamic_result_is_re_read_from_the_held_cc_table():
    # the registry entry must be what the reader produces from the held CC BY JATS today (sha-pinned)
    import json
    rec = json.load(open(os.path.join(ROOT, "registry", "comparator_results.json"), encoding="utf-8"))["tranexamic-acid-pph"]
    got, why = tr.table_result("tranexamic-acid-pph")
    assert got is not None, why
    for k in ("estimate", "ci_low", "ci_high", "scale", "counts", "sha256", "outcome"):
        assert got[k] == rec[k], k
    assert rec["counts"] == {"events_t": 159, "n_t": 27307, "events_c": 194, "n_c": 27097}


def _reader(monkeypatch, tmp_path, text):
    """table_result over a synthetic held CC table (the real reader path, held-source checks stubbed)."""
    import json as _json
    import g1_swap as sw
    from reproducible_ai import record_licence as rl
    (tmp_path / "topics").mkdir(exist_ok=True)
    (tmp_path / "topics" / "demo.json").write_text(_json.dumps({
        "primary_outcome": {"name": "Death", "keywords": ["death"]}, "comparator_pmid": "123",
        "intervention_terms": ["Tranexamic acid"], "comparator_terms": ["placebo"]}), encoding="utf-8")
    d = tmp_path / "cache" / "comparators" / "123"
    d.mkdir(parents=True, exist_ok=True)
    (d / "2026-01-01_kgap_jats.xml").write_text("<x/>", encoding="utf-8")
    monkeypatch.setattr(tr, "ROOT", str(tmp_path))
    monkeypatch.setattr(rl, "jats_licence", lambda p: "CC")
    monkeypatch.setattr(sw, "jats_text", lambda s: text)
    return tr.table_result("demo")


def test_PLANT_r1_positive_control_the_reader_records_a_clean_row(monkeypatch, tmp_path):
    r, why = _reader(monkeypatch, tmp_path, "Outcome | Tranexamic acid (n/N) | Placebo (n/N) | Pooled OR (95% CI)\n"
                                            "Death | 10/100 | 20/100 | 0.44 (0.20-0.99)")
    assert r and r["counts"] == {"events_t": 10, "n_t": 100, "events_c": 20, "n_c": 100}, why


def test_PLANT_r1_arm_headers_over_different_populations_are_refused(monkeypatch, tmp_path):
    r, why = _reader(monkeypatch, tmp_path, "Outcome | Tranexamic acid randomised population (n/N) | Placebo safety "
                                            "population (n/N) | Pooled OR (95% CI)\nDeath | 10/100 | 20/80 | 0.40 (0.20-0.90)")
    assert r is None and "populations differ" in why


def test_PLANT_r1_a_reverse_contrast_is_refused_never_inverted(monkeypatch, tmp_path):
    r, why = _reader(monkeypatch, tmp_path, "Outcome | Tranexamic acid (n/N) | Placebo (n/N) | Placebo vs tranexamic "
                                            "acid OR (95% CI)\nDeath | 10/100 | 20/100 | 2.25 (1.00-5.06)")
    assert r is None and "reverse contrast" in why
    r, why = _reader(monkeypatch, tmp_path, "Outcome | Tranexamic acid (n/N) | Placebo (n/N) | Pooled OR (95% CI)\n"
                                            "Death | 10/100 | 20/100 | 2.25 (1.00-5.06)")
    assert r is None and "other side of 1" in why


def test_PLANT_r1_a_decimal_comma_is_never_a_count():
    assert tr._EN.match("12,5/100") is None
    assert tr._EN.match("27 307/27 097") and tr._EN.match("27,307/27,097") and tr._EN.match("159/27 307")


def test_PLANT_r1_a_supplementary_caption_stops_the_header_search():
    lines = ["Outcome | Tranexamic acid (n/N) | Placebo (n/N) | Pooled OR (95% CI)", "Table S2. Supplementary results",
             "Outcome | Placebo | Tranexamic acid | Pooled OR (95% CI)", "Death | 20/100 | 10/100 | 2.25 (1.00–5.06)"]
    assert tr.header_above(lines, 3) is None
