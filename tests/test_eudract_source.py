"""Offline EU CTR contracts: synthetic cases and saved live EMA results.

Live fixtures: European Medicines Agency, EU Clinical Trials Register;
reused with acknowledgement under EMA's reuse policy (see eu.EMA_ACK).
"""
import copy
import hashlib
import json
import os
import socket
from pathlib import Path
import sys
import urllib.request

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import g1_eudract_source as eu

FIXTURES = Path(__file__).parent / "fixtures" / "eudract"
NO = "2099-000001-01"
URL = eu.BASE + "/ctr-search/trial/" + NO + "/results"


@pytest.fixture(autouse=True)
def offline(monkeypatch, tmp_path):
    def deny(*args, **kwargs):
        raise AssertionError("Network forbidden in tests")
    monkeypatch.setattr(eu, "urlopen", deny)
    monkeypatch.setattr(urllib.request, "urlopen", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(eu, "CACHE_DIR", tmp_path / "eudract")


@pytest.fixture
def body():
    return (FIXTURES / "results.html").read_bytes()


def pick(endpoints):
    return eu.eudract_typed(endpoints, ["survival"], ["Drug Alpha"], ["Drug Beta"], "HR")


def test_numbers_secondary_and_search(monkeypatch):
    calls = []
    def fetch(url):
        calls.append(url)
        if "clinicaltrials.gov" in url:
            return json.dumps({"protocolSection": {"identificationModule": {
                "nctId": "NCT99999999", "secondaryIdInfos": [
                    {"id": NO, "type": "EUDRACT_NUMBER"}, {"id": "sponsor-code"}]}}}).encode()
        return (FIXTURES / "search.html").read_bytes()
    monkeypatch.setattr(eu, "_fetch", fetch)
    result = eu.eudract_numbers(["NCT99999999", "NCT99999999"], ["2099-999999-99"])
    assert [r["eudract_no"] for r in result] == [NO, "2099-000002-02"]
    assert result[0]["provenance"] == [
        {"nct": "NCT99999999", "url": calls[0], "field": "secondaryIdInfos.id"},
        {"nct": "NCT99999999", "url": calls[1], "field": "search_result.trial_link"}]
    assert len(result[1]["provenance"]) == 1
    assert len(calls) == 2


def test_no_results(monkeypatch):
    monkeypatch.setattr(eu, "_fetch", lambda url: (FIXTURES / "no_results.html").read_bytes())
    assert eu.eudract_results(NO) == {"state": "NO_RESULTS"}


def test_exact_results(body, monkeypatch):
    monkeypatch.setattr(eu, "_fetch", lambda url: body)
    result = eu.eudract_results(NO)
    assert result["state"] == "RESULTS"
    assert result["url"] == URL
    assert result["licence"] == "EMA_REUSE_WITH_ACKNOWLEDGEMENT"
    assert result["acknowledgement"] == eu.EMA_ACK
    assert result["html_sha256"] == hashlib.sha256(body).hexdigest()
    assert result["attachments"] == [eu.BASE + "/ctr-search/rest/download/result/attachment/synthetic-summary"]
    assert result["endpoints"] == [{
        "title": "30-day survival", "description": "Survival in the modified full analysis set; per protocol sensitivity.",
        "type": "Primary", "timeframe": "30 days after inclusion",
        "reporting_groups": [{"title": "Drug Beta", "subjects_analysed": "40"},
                             {"title": "Drug Alpha", "subjects_analysed": "50"}],
        "statistics": [{"label": "alive at 30 days", "measure_type": "alive at 30 days", "unit": "Subjects",
                        "dispersion": "", "values": {"Drug Beta": "32", "Drug Alpha": "45"}}],
        "analyses": [{"title": "Primary analysis", "description": "Adjusted for synthetic stratum.",
                      "comparison_groups": "Drug Alpha v Drug Beta", "method": "Regression, Cox",
                      "parameter": "Hazard ratio (HR)", "point_estimate": "0.70", "ci_level": "95%",
                      "sides": "2-sided", "lower": "0.50", "upper": "0.98"}]}]


def test_swapped_headers_map_by_name(body):
    result = pick(eu._parse(body, URL)["endpoints"])
    assert result["decision"] == "CANDIDATE"
    candidate = result["candidates"][0]
    assert candidate["counts"] == [{"label": "alive at 30 days", "arms": {
        "experimental": {"count": 45, "subjects_analysed": 50},
        "control": {"count": 32, "subjects_analysed": 40}}}]
    assert candidate["effects"][0]["point_estimate"] == "0.70"
    assert candidate["divergences"] == {"timeframe": "30 days after inclusion",
        "analysis_population": ["full analysis set", "modified", "per protocol"], "measure_type": ["alive at 30 days"]}


def test_percentages_never_become_counts(body):
    body = body.replace(b"Units: Subjects", b"Units: percent").replace(b">32<", b">80<").replace(b">45<", b">90<")
    candidate = pick(eu._parse(body, URL)["endpoints"])["candidates"][0]
    assert candidate["counts"] == []
    assert candidate["statistics"][0]["values"] == {"Drug Beta": "80", "Drug Alpha": "90"}


@pytest.mark.parametrize("title", ["Drug Alpha and Drug Beta", "Unidentified group"])
def test_refuse_both_or_neither(body, title):
    endpoints = eu._parse(body, URL)["endpoints"]
    endpoints[0]["reporting_groups"][0]["title"] = title
    result = pick(endpoints)
    assert result["decision"] == "REFUSED"
    assert result["candidates"] == []


def test_two_matching_endpoints_ambiguous(body):
    endpoint = eu._parse(body, URL)["endpoints"][0]
    second = copy.deepcopy(endpoint)
    second["title"] = "90-day survival"
    result = pick([endpoint, second])
    assert result["decision"] == "AMBIGUOUS"
    assert [c["title"] for c in result["candidates"]] == ["30-day survival", "90-day survival"]


@pytest.mark.parametrize("field,value", [("ci_level", "90%"), ("sides", "1-sided"),
                                       ("point_estimate", "-"), ("lower", "1.1")])
def test_effect_requires_valid_two_sided_95_ci(body, field, value):
    endpoints = eu._parse(body, URL)["endpoints"]
    endpoints[0]["analyses"][0][field] = value
    assert pick(endpoints)["candidates"][0]["effects"] == []


def test_cache_reuse_and_expiry(body, monkeypatch):
    calls = []
    def fetch(url):
        calls.append(url)
        return body
    monkeypatch.setattr(eu, "_fetch", fetch)
    first = eu.eudract_results(NO)
    assert eu.eudract_results(NO) == first
    assert calls == [URL]
    path = eu.CACHE_DIR / (NO + ".html")
    assert path.read_bytes() == body
    old = eu.time.time() - eu.TTL - 1
    os.utime(path, (old, old))
    assert eu.eudract_results(NO) == first
    assert calls == [URL, URL]
    assert not list(eu.CACHE_DIR.glob("*.lock"))


def test_unknown_page_not_cached(monkeypatch):
    monkeypatch.setattr(eu, "_fetch", lambda url: b"<html>Service unavailable</html>")
    result = eu.eudract_results(NO)
    assert result == {"state": "PARSE_FAILED", "url": URL,
                      "html_sha256": hashlib.sha256(b"<html>Service unavailable</html>").hexdigest(),
                      "reason": "Unrecognised EU CTR results page"}
    assert not list(eu.CACHE_DIR.glob("*.html"))


def test_dispersion_and_printed_precision(body):
    body = body.replace(b"alive at 30 days", b"mean (standard deviation)").replace(b">32<", b">32.00 (2.10)<")
    stat = eu._parse(body, URL)["endpoints"][0]["statistics"][0]
    assert stat["measure_type"] == "mean"
    assert stat["dispersion"] == "standard deviation"
    assert stat["values"]["Drug Beta"] == "32.00 (2.10)"


def test_cli_no_values(body, monkeypatch, capsys):
    monkeypatch.setattr(eu, "eudract_numbers", lambda ncts, labels: [{"eudract_no": NO, "provenance": []}])
    monkeypatch.setattr(eu, "eudract_results", lambda no: eu._parse(body, URL))
    eu.main(["probe", "NCT99999999"])
    record, summary = capsys.readouterr().out.splitlines()
    assert summary == "EUDRACT_SUMMARY ncts=1 with_number=1 results=1 parse_failed=0 no_results=0"
    result = json.loads(record)
    assert result["results"] == [{"eudract_no": NO, "state": "RESULTS", "endpoint_titles": ["30-day survival"]}]


def test_http_user_agent_and_pause(monkeypatch):
    seen = []
    class Response:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return b"synthetic"
    def open_request(request, timeout):
        seen.append((request.get_header("User-agent"), timeout))
        return Response()
    monkeypatch.setattr(eu, "urlopen", open_request)
    monkeypatch.setattr(eu.time, "sleep", lambda seconds: seen.append(seconds))
    assert eu._fetch(URL) == b"synthetic"
    assert seen == [("meta-harness k-gap (meta-harness@example.org)", 30), eu.PAUSE]


def test_endpoint_boundaries_and_multiple_blocks(body):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(body, "html.parser")
    table = soup.select_one("#endPoint1Section")
    table.find(string="Statistical analysis title").find_parent("tr").extract()
    # Remove analyses so an unrelated later table could otherwise become a statistic.
    for row in list(table.find_all("tr")):
        if row.find_parent("table") is table and row.find(string="Statistical analysis description"):
            for sibling in list(row.find_next_siblings("tr")):
                sibling.extract()
            row.extract()
    first = str(table)
    second = first.replace("30-day survival", "90-day survival").replace("Primary", "Secondary")
    unrelated = '<table><tr><td>Other outcome</td><td>999</td><td>999</td></tr></table>'
    endpoints = eu._parse((first + unrelated + second + unrelated).encode(), URL)["endpoints"]
    assert len(endpoints) == 2
    assert [ep["type"] for ep in endpoints] == ["Primary", "Secondary"]
    assert all(len(ep["statistics"]) == 1 for ep in endpoints)
    assert pick(endpoints)["decision"] == "AMBIGUOUS"


def test_effect_comparison_must_name_mapped_arms(body):
    endpoints = eu._parse(body, URL)["endpoints"]
    analysis = endpoints[0]["analyses"][0]
    analysis["comparison_groups"] = "Drug Beta v Drug Alpha"
    effect = pick(endpoints)["candidates"][0]["effects"][0]
    assert effect["comparison_order"] == ["control", "experimental"]
    assert effect["point_estimate"] == "0.70"
    analysis["comparison_groups"] = "Other drug v Drug Alpha"
    assert pick(endpoints)["candidates"][0]["effects"] == []


def test_stale_cache_failure_does_not_fall_back(body, monkeypatch):
    monkeypatch.setattr(eu, "_fetch", lambda url: body)
    eu.eudract_results(NO)
    path = eu.CACHE_DIR / (NO + ".html")
    old = eu.time.time() - eu.TTL - 1
    os.utime(path, (old, old))
    def fail(url):
        raise RuntimeError("Synthetic HTTP failure")
    monkeypatch.setattr(eu, "_fetch", fail)
    with pytest.raises(RuntimeError, match="Synthetic HTTP failure"):
        eu.eudract_results(NO)
    assert path.read_bytes() == body
    assert not list(eu.CACHE_DIR.glob("*.lock"))


def test_invalid_identifiers_refused_before_fetch():
    with pytest.raises(ValueError, match="Invalid NCT"):
        eu.eudract_numbers(["not-an-NCT"], [])
    with pytest.raises(ValueError, match="Invalid EudraCT"):
        eu.eudract_results("../escape")


def test_ctgov_identity_mismatch(monkeypatch):
    monkeypatch.setattr(eu, "_fetch", lambda url: json.dumps({"protocolSection": {
        "identificationModule": {"nctId": "NCT99999998"}}}).encode())
    with pytest.raises(ValueError, match="identifier mismatch"):
        eu.eudract_numbers(["NCT99999999"], [])



def live_result(number):
    body = (FIXTURES / f"live_{number}.html").read_bytes()
    result = eu._parse(body, eu.BASE + f"/ctr-search/trial/{number}/results")
    assert result["state"] == "RESULTS"
    assert result["html_sha256"] == hashlib.sha256(body).hexdigest()
    assert result["acknowledgement"] == eu.EMA_ACK
    return result


def test_live_pretovid():
    endpoints = live_result("2020-001375-32")["endpoints"]
    assert len(endpoints) == 1
    ep = endpoints[0]
    assert ep["title"] == "30-day survival"
    assert ep["timeframe"] == "30 days after inclusion"
    assert ep["reporting_groups"] == [
        {"title": "SOC + tocilizumab", "subjects_analysed": "174"},
        {"title": "Standard of Care (SOC)", "subjects_analysed": "180"}]
    assert ep["statistics"] == [
        {"label": label, "measure_type": label, "unit": "347", "dispersion": "",
         "values": dict(zip(["SOC + tocilizumab", "Standard of Care (SOC)"], values))}
        for label, values in [("alive at 30 days", ["153", "146"]),
                              ("death at 30 days", ["21", "34"])]]
    assert len(ep["analyses"]) == 1
    analysis = ep["analyses"][0]
    assert analysis["comparison_groups"] == "SOC + tocilizumab v Standard of Care (SOC)"
    assert analysis["method"] == "Regression, Cox"
    assert analysis["parameter"] == "Hazard ratio (HR)"
    assert [analysis[k] for k in ("ci_level", "sides", "lower", "upper")] == ["90%", "2-sided", "-", "-"]
    assert "point_estimate" not in analysis  # Not reported in the source.


def test_live_odyssey_plant_endpoint_boundaries():
    # PLANT: the previous parser consumed endpoint 27's navigation heading
    # as a statistic of endpoint 26 and raised a header-count error.
    endpoints = live_result("2011-005109-56")["endpoints"]
    assert len(endpoints) == 28
    assert sum(len(ep["analyses"]) for ep in endpoints) == 25
    assert all(len(ep["statistics"]) == 1 for ep in endpoints)
    ep = endpoints[0]
    assert ep["title"] == "Percent Change From Baseline in Calculated LDL-C at Week 24 - Intent-to-Treat (ITT) Analysis"
    assert ep["reporting_groups"] == [
        {"title": "Placebo", "subjects_analysed": "163"},
        {"title": "Alirocumab 75 mg/Up to 150 mg Q2W", "subjects_analysed": "322"}]
    assert ep["statistics"] == [{
        "label": "least squares mean (standard error)", "measure_type": "least squares mean",
        "unit": "percent change", "dispersion": "standard error",
        "values": {"Placebo": "9.1 ( 2.2 )", "Alirocumab 75 mg/Up to 150 mg Q2W": "-48.8 ( 1.6 )"}}]
    analysis = ep["analyses"][0]
    assert analysis["comparison_groups"] == "Placebo v Alirocumab 75 mg/Up to 150 mg Q2W"
    assert analysis["parameter"] == "LS mean difference"
    assert [analysis[k] for k in ("point_estimate", "ci_level", "sides", "lower", "upper")] == [
        "-57.9", "95%", "2-sided", "-63.3", "-52.6"]
    assert all(ep["analyses"] == [] for ep in endpoints[25:])
    assert endpoints[-1]["reporting_groups"][1]["subjects_analysed"] == "321"


def test_malformed_groups_return_parse_failed(body):
    result = eu._parse(body.replace(b"Drug Beta", b"Drug Alpha"), URL)
    assert result["state"] == "PARSE_FAILED"
    assert result["reason"] == "Missing or duplicate endpoint group names"


def test_cli_continues_after_parse_failed(body, monkeypatch, capsys):
    ncts = [f"NCT9999999{i}" for i in range(6)]
    calls = []
    def numbers(ids, labels):
        calls.extend(ids)
        return [] if ids[0] == ncts[-1] else [{"eudract_no": NO, "provenance": []}]
    responses = iter([eu._parse(b"<html>Unknown layout</html>", URL),
                      eu._parse(body, URL), {"state": "NO_RESULTS"},
                      live_result("2020-001375-32"), live_result("2011-005109-56")])
    monkeypatch.setattr(eu, "eudract_numbers", numbers)
    monkeypatch.setattr(eu, "eudract_results", lambda no: next(responses))
    eu.main(["probe", *ncts])
    lines = capsys.readouterr().out.splitlines()
    records = [json.loads(line) for line in lines[:-1]]
    assert calls == ncts
    assert [record["nct"] for record in records] == ncts
    failure = records[0]["results"][0]
    assert failure["state"] == "PARSE_FAILED"
    assert failure["reason"] == "Unrecognised EU CTR results page"
    assert failure["url"] == URL
    assert failure["html_sha256"] == hashlib.sha256(b"<html>Unknown layout</html>").hexdigest()
    assert records[1]["results"][0]["state"] == "RESULTS"
    assert lines[-1] == "EUDRACT_SUMMARY ncts=6 with_number=5 results=3 parse_failed=1 no_results=1"


def test_PLANT_live_no_public_results_page_is_no_results_not_a_parse_failure():
    """15 Oct: 6 live pages saying 'There are no public results for the specified EudraCT number' were PARSE_FAILED."""
    import pathlib
    body = (pathlib.Path(__file__).parent / "fixtures" / "eudract" / "live_no_public_results.html").read_bytes()
    assert eu._parse(body, "https://www.clinicaltrialsregister.eu/ctr-search/trial/2005-001570-28/results")["state"] == "NO_RESULTS"
