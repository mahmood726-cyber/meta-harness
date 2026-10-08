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


def test_PLANT_a_supplement_failure_survives_an_empty_body_and_strict_raises_on_it(monkeypatch):
    """codex fetch-loud-r2: #1 EMPTY_BODY overwrote the supplement failure; #2 strict=True did not raise on it."""
    monkeypatch.setattr(fetch, "_resolve_pmcid", lambda pmid: "43")
    monkeypatch.setattr(fetch.http, "get_text", lambda url, *a, **k: "<article/>" if "efetch" in url else (_ for _ in ()).throw(TimeoutError("timed out")))
    monkeypatch.setattr(fetch._ft, "parse_pmc_xml", lambda xml: {"supplements": ["s1.xlsx"]})
    monkeypatch.setattr(fetch._ft, "combined_text", lambda parsed: "")
    assert fetch._pmc_fulltext("889", with_supplements=True) == ""
    assert fetch.LAST_PMC_STATE["889"].startswith("EMPTY_BODY_WITH_SUPPLEMENT_FAILURE:") and fetch.run_failed("889")
    monkeypatch.setattr(fetch._ft, "combined_text", lambda parsed: "Body.")
    with pytest.raises(fetch.PmcFetchError) as e:
        fetch._pmc_fulltext("890", with_supplements=True, strict=True)
    assert e.value.stage == "SUPPLEMENT"
    assert fetch.LAST_PMC_STATE["890"].startswith("HELD_WITH_SUPPLEMENT_FAILURE:")


def test_PLANT_the_kgap_cache_records_a_supplement_failure_as_a_failure(monkeypatch, tmp_path):
    """codex fetch-loud-r3 #1: EMPTY_BODY_WITH_SUPPLEMENT_FAILURE was recorded as FETCH_EMPTY by the k-gap cache."""
    import json as _json
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import k_gap_counterfactual as kc
    monkeypatch.setattr(kc, "FT_DIR", str(tmp_path / "_ft"))
    monkeypatch.setattr(kc, "OUT", str(tmp_path))
    monkeypatch.setattr(kc, "committed_open_fulltext", lambda pmid, idx=None: None)
    monkeypatch.setattr(fetch.http, "get_json", lambda *a, **k: {"records": [{"pmcid": "PMC43"}]})

    def fake(pmid, with_supplements=False, strict=False):
        fetch.LAST_PMC_STATE[pmid] = "EMPTY_BODY_WITH_SUPPLEMENT_FAILURE:FETCH_FAILED:SUPPLEMENT:TimeoutError: x"
        return ""
    monkeypatch.setattr(fetch, "_pmc_fulltext", fake)
    assert kc.pmc_fulltext_cached("891") == ""
    idx = _json.load(open(tmp_path / "fulltext_index.json", encoding="utf-8"))
    assert idx["891"]["state"] == "FETCH_FAILED"


def test_PLANT_an_oa_service_error_is_a_failure_and_not_open_access_is_not(monkeypatch):
    """codex fetch-loud-r4 #1: an OA service error with no archive link read as NO_OA_PACKAGE."""
    monkeypatch.setattr(fetch.http, "get_text", lambda *a, **k: '<OA><error code="internalError">Service unavailable</error></OA>')
    assert fetch._pmc_oa_supplement_text("901", ["s.xlsx"]) == ""
    assert fetch.LAST_SUPPLEMENT_STATE["901"].startswith("FETCH_FAILED:SUPPLEMENT:OA_SERVICE_ERROR: internalError")
    monkeypatch.setattr(fetch.http, "get_text", lambda *a, **k: '<OA><error code="idIsNotOpenAccess">identifier is not Open Access</error></OA>')
    assert fetch._pmc_oa_supplement_text("902", ["s.xlsx"]) == ""
    assert fetch.LAST_SUPPLEMENT_STATE["902"] == "NO_OA_PACKAGE"


def test_PLANT_single_quoted_and_codeless_oa_errors_are_failures(monkeypatch):
    """codex fetch-loud-r5 #1: a single-quoted error attribute fell through to NO_OA_PACKAGE."""
    monkeypatch.setattr(fetch.http, "get_text", lambda *a, **k: "<OA><error code='internalError'>down</error></OA>")
    assert fetch._pmc_oa_supplement_text("903", ["s.xlsx"]) == ""
    assert fetch.LAST_SUPPLEMENT_STATE["903"].startswith("FETCH_FAILED:SUPPLEMENT:OA_SERVICE_ERROR: internalError")
    monkeypatch.setattr(fetch.http, "get_text", lambda *a, **k: "<OA><error>down</error></OA>")
    assert fetch._pmc_oa_supplement_text("904", ["s.xlsx"]) == ""
    assert fetch.LAST_SUPPLEMENT_STATE["904"].startswith("FETCH_FAILED:SUPPLEMENT:OA_SERVICE_ERROR: NO_CODE")
    monkeypatch.setattr(fetch.http, "get_text", lambda *a, **k: "<OA><error code='idIsNotOpenAccess'>not OA</error></OA>")
    assert fetch._pmc_oa_supplement_text("905", ["s.xlsx"]) == ""
    assert fetch.LAST_SUPPLEMENT_STATE["905"] == "NO_OA_PACKAGE"


def test_PLANT_a_single_quoted_archive_link_is_followed_not_read_as_no_package(monkeypatch):
    """codex fetch-loud-r5 #1 (same class): a single-quoted href was missed and the package read as absent."""
    seen = []
    monkeypatch.setattr(fetch.http, "get_text", lambda *a, **k: "<OA><record><link format='tgz' href='https://ftp.ncbi.nlm.nih.gov/pub/pmc/x.tar.gz'/></record></OA>")

    def get(url, *a, **k):
        seen.append(url)
        raise TimeoutError("timed out")
    monkeypatch.setattr(fetch.http, "get", get)
    assert fetch._pmc_oa_supplement_text("906", ["s.xlsx"]) == ""
    assert seen == ["https://ftp.ncbi.nlm.nih.gov/pub/pmc/x.tar.gz"]
    assert fetch.LAST_SUPPLEMENT_STATE["906"].startswith("FETCH_FAILED:SUPPLEMENT")


def test_PLANT_absence_is_only_established_positively(monkeypatch):
    """codex fetch-loud-r6 #1: a malformed or unexpected OA reply was silently classified NO_OA_PACKAGE."""
    for i, reply in enumerate(["<html>Bad Gateway</html>", "<OA><records/></OA>", "not xml <<"]):
        monkeypatch.setattr(fetch.http, "get_text", lambda *a, _r=reply, **k: _r)
        assert fetch._pmc_oa_supplement_text(f"91{i}", ["s.xlsx"]) == ""
        assert fetch.LAST_SUPPLEMENT_STATE[f"91{i}"].startswith("FETCH_FAILED:SUPPLEMENT:"), reply
    monkeypatch.setattr(fetch.http, "get_text", lambda *a, **k: "<OA><records><record id='PMC1'><link format='pdf' href='https://x/y.pdf'/></record></records></OA>")
    assert fetch._pmc_oa_supplement_text("919", ["s.xlsx"]) == ""
    assert fetch.LAST_SUPPLEMENT_STATE["919"] == "NO_OA_PACKAGE"
