"""Plants (captain order, 8 Oct): harness.fetch._pmc_fulltext swallowed every error into '' -- a rate limit, a network
fault and 'not in PMC' were indistinguishable, and the k-gap index recorded 'swallows errors; not cached'. Now every call
leaves a TYPED state in LAST_PMC_STATE, failures are printed to stderr, strict=True raises PmcFetchError, and the
supplement fetch is typed the same way. The abstract fallback ('' to the pipeline) is unchanged."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import fetch  # noqa: E402


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(fetch.time, "sleep", lambda s: None)
    fetch.LAST_PMC_STATE.clear()
    fetch.LAST_SUPPLEMENT_STATE.clear()


def test_PLANT_a_resolve_failure_is_typed_loud_and_strict_raises(monkeypatch, capsys):
    def boom(*a, **k):
        raise RuntimeError("HTTP 429 Too Many Requests")
    monkeypatch.setattr(fetch.http, "get_json", boom)
    assert fetch._pmc_fulltext("111") == ""
    st = fetch.LAST_PMC_STATE["111"]
    assert st.startswith("FETCH_FAILED:RESOLVE:RuntimeError") and "429" in st
    assert "FETCH_FAILED" in capsys.readouterr().err
    with pytest.raises(fetch.PmcFetchError) as e:
        fetch._pmc_fulltext("111", strict=True)
    assert e.value.stage == "RESOLVE" and e.value.pmid == "111"


def test_PLANT_an_efetch_failure_and_a_parse_failure_are_typed(monkeypatch):
    monkeypatch.setattr(fetch, "_resolve_pmcid", lambda pmid: "999")

    def boom(*a, **k):
        raise ConnectionError("reset by peer")
    monkeypatch.setattr(fetch.http, "get_text", boom)
    assert fetch._pmc_fulltext("222") == ""
    assert fetch.LAST_PMC_STATE["222"].startswith("FETCH_FAILED:EFETCH:ConnectionError")
    monkeypatch.setattr(fetch.http, "get_text", lambda *a, **k: "<article>")

    def bad(xml):
        raise ValueError("not JATS")
    monkeypatch.setattr(fetch._ft, "parse_pmc_xml", bad)
    assert fetch._pmc_fulltext("333") == ""
    assert fetch.LAST_PMC_STATE["333"].startswith("FETCH_FAILED:PARSE:ValueError")


def test_PLANT_success_no_pmcid_and_empty_body_are_typed(monkeypatch):
    monkeypatch.setattr(fetch, "_resolve_pmcid", lambda pmid: None)
    assert fetch._pmc_fulltext("444") == "" and fetch.LAST_PMC_STATE["444"] == "NO_PMCID"
    monkeypatch.setattr(fetch, "_resolve_pmcid", lambda pmid: "1")
    monkeypatch.setattr(fetch.http, "get_text", lambda *a, **k: "<article/>")
    monkeypatch.setattr(fetch._ft, "parse_pmc_xml", lambda xml: {})
    monkeypatch.setattr(fetch._ft, "combined_text", lambda parsed: "")
    assert fetch._pmc_fulltext("555") == "" and fetch.LAST_PMC_STATE["555"] == "EMPTY_BODY"
    monkeypatch.setattr(fetch._ft, "combined_text", lambda parsed: "Body text.")
    assert fetch._pmc_fulltext("666") == "Body text." and fetch.LAST_PMC_STATE["666"] == "HELD"


def test_PLANT_a_supplement_failure_is_typed(monkeypatch):
    def boom(*a, **k):
        raise TimeoutError("timed out")
    monkeypatch.setattr(fetch.http, "get_text", boom)
    assert fetch._pmc_oa_supplement_text("777", ["s1.xlsx"]) == ""
    assert fetch.LAST_SUPPLEMENT_STATE["777"].startswith("FETCH_FAILED:SUPPLEMENT:TimeoutError")


def test_PLANT_a_failed_supplement_beside_a_held_body_is_a_failure_of_the_run(monkeypatch):
    """codex fetch-loud #1: the body succeeded, the supplement failed, and the run read RAN_OK."""
    monkeypatch.setattr(fetch, "_resolve_pmcid", lambda pmid: "42")
    monkeypatch.setattr(fetch.http, "get_text", lambda url, *a, **k: "<article/>" if "efetch" in url else (_ for _ in ()).throw(TimeoutError("timed out")))
    monkeypatch.setattr(fetch._ft, "parse_pmc_xml", lambda xml: {"supplements": ["s1.xlsx"]})
    monkeypatch.setattr(fetch._ft, "combined_text", lambda parsed: "Body text.")
    assert fetch._pmc_fulltext("888", with_supplements=True) == "Body text."
    assert fetch.LAST_PMC_STATE["888"].startswith("HELD_WITH_SUPPLEMENT_FAILURE:FETCH_FAILED:SUPPLEMENT")
    assert fetch.run_failed("888")
