"""Offline synthetic contracts for dated searches (no real reports or networks)."""
import io
import json
from pathlib import Path
import subprocess
from urllib.error import HTTPError

import pytest

from scripts import g1_search_log as log


def epmc(**hit):
    return {"hitCount": 1, "resultList": {"result": [{"id": "12345", **hit}]}}


@pytest.mark.parametrize("source,obj,census,expected", [
    ("PUBMED_EPMC_PMID", epmc(isOpenAccess="N", inEPMC="N"), {}, "FOUND_NOT_OPEN"),
    ("PUBMED_EPMC_PMID", epmc(isOpenAccess="Y"), {}, "ERROR"),
    ("PUBMED_EPMC_PMID", epmc(isOpenAccess="Y"), {"blocker_now": "OUTCOME_NOT_IN_SOURCE"}, "OPEN_NO_OUTCOME"),
    ("PUBMED_EPMC_PMID", epmc(inEPMC="Y"), {"stage": "EXTRACTION"}, "OPEN_OUTCOME_NOT_BINDABLE"),
    ("PUBMED_EPMC_PMID", epmc(isOpenAccess="Y"), {"decision": "TYPED_NONE_NOT_MODEL_LICENSED", "blocker_now": "OUTCOME_NOT_IN_SOURCE"}, "OPEN_OUTCOME_NOT_BINDABLE"),
    ("PUBMED_EPMC_PMID", {"hitCount": 0}, {}, "NOT_FOUND"),
    ("PUBMED_EPMC_PMID", {}, {}, "ERROR"),
    ("PUBMED_EPMC_TITLE", {"hitCount": 0}, {}, "NOT_FOUND"),
    ("PUBMED_EPMC_TITLE", epmc(title="A trial"), {}, "ERROR"),
    ("UNPAYWALL_DOI", {"is_oa": False}, {}, "FOUND_NOT_OPEN"),
    ("UNPAYWALL_DOI", {"is_oa": True}, {}, "ERROR"),
    ("UNPAYWALL_DOI", {"is_oa": True}, {"blocker_now": "OUTCOME_NOT_IN_SOURCE"}, "OPEN_NO_OUTCOME"),
    ("UNPAYWALL_DOI", {}, {}, "ERROR"),
    ("CTGOV_V2", {"protocolSection": {"identificationModule": {"nctId": "NCT00000001"}}, "hasResults": False}, {}, "OPEN_NO_OUTCOME"),
    ("CTGOV_V2", {"protocolSection": {"identificationModule": {"nctId": "NCT00000001"}}, "hasResults": True, "resultsSection": {"outcomeMeasuresModule": {}}}, {}, "OPEN_OUTCOME_NOT_BINDABLE"),
    ("CTGOV_V2", {}, {}, "ERROR"),
    ("EUCTR", {"state": "RESULTS"}, {}, "OPEN_OUTCOME_NOT_BINDABLE"),
    ("EUCTR", {"state": "NO_RESULTS"}, {}, "OPEN_NO_OUTCOME"),
    ("EUCTR", {"state": "PARSE_FAILED"}, {}, "ERROR"),
    ("AACT", {"state": "RESULTS"}, {}, "OPEN_OUTCOME_NOT_BINDABLE"),
    ("AACT", {"state": "NO_RESULTS"}, {}, "OPEN_NO_OUTCOME"),
])
def test_response_mapping(source, obj, census, expected):
    assert log.response_mapping(source, log.encoded(obj), census=census)[0] == expected


@pytest.mark.parametrize("body,expected", [
    (b'<html>Cloudflare verify you are human</html>', "BLOCKED_BOT_CHALLENGE"),
    (b'<html><script src="app.js"></script>Please enable JavaScript</html>', "ERROR"),
    (b'<html>No records found</html>', "NOT_FOUND"),
])
def test_who(body, expected):
    assert log.response_mapping("WHO_ICTRP", body)[0] == expected


def test_title_rct_requires_trial_name():
    obj = epmc(title="Randomized study ALPHA NCT00000001", pubTypeList={"pubType": ["Randomized Controlled Trial"]})
    step, outcome = log.response_mapping("PUBMED_EPMC_TITLE", log.encoded(obj), identifiers={"ncts": ["NCT00000001"]})
    assert step == "ERROR"
    assert outcome["rct_reports_naming_trial"] == ["12345"]
    assert log.response_mapping("PUBMED_EPMC_TITLE", log.encoded(obj), identifiers={"ncts": ["NCT00000002"]})[1]["rct_reports_naming_trial"] == []


def test_identifier_mismatch():
    assert log.response_mapping("PUBMED_EPMC_PMID", log.encoded(epmc()), identifiers={"pmid": "999"})[0] == "ERROR"
    obj = {"protocolSection": {"identificationModule": {"nctId": "NCT00000001"}}}
    assert log.response_mapping("CTGOV_V2", log.encoded(obj), identifiers={"nct": "NCT00000002"})[0] == "ERROR"


def test_regulator_metadata_plant(tmp_path):
    path = tmp_path / "plant.json"
    plant = dict(label="ALPHA", phase="2_REGULATOR:FDA", stage="READ", decision="REFUSED", verdict="NOT_ADMITTED",
                 documents_naming=["SECRET DOCUMENT"], candidate={"span": "SECRET"}, readers={"secret": "SECRET"}, span="SECRET")
    path.write_text(json.dumps({"rows": [plant]}), encoding="utf-8")
    result = log.regulator_summary(path)
    assert set(result[0]) == set(log.META_FIELDS)
    assert "SECRET" not in json.dumps(result)
    plant["decision"] = {"span": "SECRET"}
    assert log.regulator_summary(path, lambda _: log.encoded({"rows": [plant]}))[0]["decision"] is None


@pytest.mark.parametrize("agency,stage,expected", [
    ("FDA", "MISSING", "NOT_FOUND"), ("EMA", "NAMED", "OPEN_NO_OUTCOME"),
    ("FDA", "NAMED_NO_WINDOW", "OPEN_NO_OUTCOME"), ("FDA", "READ", "OPEN_OUTCOME_NOT_BINDABLE"),
    ("EMA", "TYPED", "OPEN_OUTCOME_NOT_BINDABLE"),
])
def test_holdings_mapping(agency, stage, expected):
    row = dict(label="ALPHA", phase="2_REGULATOR:" + agency, stage=stage, decision="REFUSED", verdict="NOT_ADMITTED")
    assert log.holding_record(row, "metadata.json", log.PROBE_DATE)["step_reached"] == expected


@pytest.mark.parametrize("source,status,expected", [
    ("TGA AusPARs", "ERROR", "ERROR"),
    ("FDA Advisory Committee briefing documents", "BLOCKED_BOT_CHALLENGE", "BLOCKED_BOT_CHALLENGE"),
    ("NIHR HTA", "NOT_FOUND", "NOT_FOUND"),
    ("AHRQ EPC", "NAMED_NO_DATA", "OPEN_NO_OUTCOME"),
    ("Pfizer", "PER_ARM_TARGET", "OPEN_OUTCOME_NOT_BINDABLE"),
    ("Sanofi", "PER_ARM_OTHER", "OPEN_OUTCOME_NOT_BINDABLE"),
    ("Amgen", "NOT_APPLICABLE", None),
])
def test_discovery_mapping(source, status, expected):
    row = dict(source=source, status=status, url="https://example.org/search?q=ALPHA", how_checked="Public search performed")
    result = log.discovery_record(row)
    if expected is None:
        assert result is None
    else:
        assert result["step_reached"] == expected
        assert result["when_utc"] == log.PROBE_DATE
        assert result["response_sha256"] is None  # no fabricated response hash
        row["when_utc"] = "2026-10-15T12:34:56+01:00"
        assert log.discovery_record(row)["when_utc"] == "2026-10-15T11:34:56Z"


def test_no_fake_discovery_search():
    assert log.discovery_record(dict(source="NIHR HTA", status="NOT_FOUND", url="https://example.org")) is None


def payload(label="ALPHA", searches=None):
    return {"slug": "demo", "written_utc": log.utc_now(), "trials": {label: {
        "identifiers": dict(pmids=["12345"], dois=[], ncts=[], eudract=[], title=label, acronym=label, approved_drug=False),
        "searched": searches or [], "secondary_value_available": False}}}


def test_merge_never_drops(tmp_path):
    path = tmp_path / "demo.json"
    rec = log.record("FDA", "metadata", log.PROBE_DATE, "NOT_FOUND", "missing")
    log.merge_write(path, payload(searches=[rec]))
    log.merge_write(path, payload("BETA"))
    new = payload()
    new["trials"]["ALPHA"]["identifiers"]["pmids"] = ["99999"]
    log.merge_write(path, new)
    result = log.merge_write(path, new)
    assert set(result["trials"]) == {"ALPHA", "BETA"}
    assert result["trials"]["ALPHA"]["searched"] == [rec]
    assert result["trials"]["ALPHA"]["identifiers"]["pmids"] == ["12345", "99999"]
    assert not list(tmp_path.glob("*.lock"))


class Response:
    status = 200
    def __init__(self, body):
        self.body = body
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def read(self):
        return self.body


class Opener:
    def __init__(self, replies):
        self.replies, self.requests = iter(replies), []
    def open(self, req, timeout):
        self.requests.append(req)
        value = next(self.replies)
        if isinstance(value, Exception):
            raise value
        return Response(value)


def test_request_email_cache_date_hash_and_backoff(tmp_path):
    url = "https://api.unpaywall.org/v2/10.1234/demo?email=" + log.EMAIL
    body = b'{"is_oa":false}'
    op = Opener([HTTPError(url, 429, "slow down", {}, io.BytesIO(b"busy")), body, body])
    sleeps = []
    client = log.Client(tmp_path, opener=op, sleep=sleeps.append, clock=lambda: 10)
    rec, _ = log.search(client, "UNPAYWALL_DOI", url)
    again, _ = log.search(client, "UNPAYWALL_DOI", url)
    assert rec == again
    assert rec["response_sha256"] == log.digest(body)
    assert rec["when_utc"].endswith("Z")
    assert len(op.requests) == 2
    assert 1 in sleeps and .34 in sleeps
    for request in op.requests:
        assert request.headers["User-agent"] == log.USER_AGENT
        assert log.EMAIL in request.full_url
    plant = "https://example.org/?email=planted%40invalid.example"
    with pytest.raises(ValueError, match="email"):
        client.get(plant)
    assert len(op.requests) == 2
    redirect = log.SafeRedirect()
    redirect.client = client
    with pytest.raises(ValueError):
        redirect.redirect_request(None, None, 302, "", {}, plant)


@pytest.mark.parametrize("source,step", [
    ("PMDA", "NOT_ATTEMPTED_PENDING_DECISION"), ("HEALTH_CANADA", "BLOCKED_TERMS"),
    ("EMA_CLINICAL_DATA", "BLOCKED_ACCOUNT"),
])
def test_policy_record(source, step):
    rec = log.record(source, "policy", "2026-10-15T01:00:00+01:00", step, "metadata")
    assert rec["when_utc"] == log.PROBE_DATE
    assert rec["response_sha256"] is None


def test_typed_identifiers_exclude_candidate_and_comparator():
    trial = dict(label="ALPHA", family="PMID 12345", identity={"nct": "NCT00000001"},
                 identification={"candidates": [{"nct": "NCT99999999"}], "meta_pmid": "66666"})
    identification = [dict(slug="demo", label="ALPHA", pmid="23456", identified=["NCT00000002"],
                           candidates=[{"nct": "NCT88888888"}])]
    census = [dict(pmid="12345", europepmc={"doi": "10.1234/demo"})]
    eu = {"ncts_probed": [{"nct": "NCT00000001", "eudract_numbers": ["2020-000001-01"]}]}
    ids = log.identifiers(trial, "demo", identification, census, eu)
    assert ids["pmids"] == ["12345", "23456"]
    assert ids["ncts"] == ["NCT00000001", "NCT00000002"]
    assert ids["dois"] == ["10.1234/demo"]
    assert ids["eudract"] == ["2020-000001-01"]


@pytest.mark.parametrize("route,phase4,expected", [
    ("SECONDARY_SINGLE", [], True), ("SWEEP_TWO_INDEPENDENT_METAS", [], True),
    ("NO_ROW", [{"label": "ALPHA", "class": "SECONDARY_PROVISIONAL (1 meta)", "value": {"effect": 1}}], True),
    ("NO_ROW", [{"label": "ALPHA", "class": "REGISTRY ONLY, NOT COUNTED", "value": {"effect": 1}}], False),
    ("NO_ROW", [], False),
])
def test_secondary(route, phase4, expected):
    assert log.secondary_available({"label": "ALPHA", "route": route}, phase4) is expected


def test_run_offline_committed_only(tmp_path, monkeypatch, capsys):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(tmp_path), *args], stderr=subprocess.PIPE)
    git("init")
    files = {
        "outputs/k_gap/g1/demo.json": {"slug": "demo", "trials": [
            {"label": "ALPHA", "route": "NO_ROW", "family": "PMID 12345"},
            {"label": "BETA", "route": "SWEEP_AACT_PRIMARY"}]},
        "topics/demo.json": {"intervention_agents": ["synthetic-agent"]},
        "outputs/k_gap/regulatory_probe.json": {"rows": [{"slug": "demo", "ema_products": ["Synthetic EPAR"]}]},
        "registry/g1_acquired_regulator/demo.json": {"rows": [dict(label="ALPHA", phase="2_REGULATOR:FDA", stage="MISSING", decision="missing", verdict="NOT_ADMITTED", readers={"span": "PLANTED"})]},
    }
    for name, data in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data), encoding="utf-8")
    git("add", ".")
    git("-c", "user.name=Synthetic", "-c", "user.email=" + log.EMAIL, "commit", "-m", "synthetic fixture")
    tracker = tmp_path / "outputs/k_gap/g1/demo.json"
    tracker.write_text('{"trials":[]}', encoding="utf-8")
    monkeypatch.setattr(log, "Client", lambda *a, **k: pytest.fail("offline transport constructed"))
    log.run(offline=True, root=tmp_path)
    out = json.loads((tmp_path / "registry/g1_search_log/demo.json").read_text(encoding="utf-8"))
    assert set(out["trials"]) == {"ALPHA"}
    trial = out["trials"]["ALPHA"]
    assert trial["identifiers"]["approved_drug"]
    assert {r["source"] for r in trial["searched"]} == {"FDA", "PMDA", "EMA_CLINICAL_DATA"}
    assert "PLANTED" not in json.dumps(out)
    assert "trials=1, records=3" in capsys.readouterr().out


def test_live_adapters_with_unavailable_snapshot(tmp_path, monkeypatch):
    from kgap import aact_adapter
    def unavailable():
        raise FileNotFoundError("synthetic missing snapshot")
    monkeypatch.setattr(aact_adapter, "snapshot_dir", unavailable)
    class Transport:
        directory = tmp_path
        def get(self, url):
            if "europepmc" in url:
                obj = epmc(isOpenAccess="N", inEPMC="N", doi="10.1234/demo")
            elif "unpaywall" in url:
                assert "email=meta-harness%40example.org" in url
                obj = {"is_oa": False}
            elif "clinicaltrials.gov" in url:
                obj = {"protocolSection": {"identificationModule": {"nctId": "NCT00000001", "secondaryIdInfos": [{"id": "2020-000001-01"}]}}, "hasResults": False}
            elif "ctr-search/search" in url:
                return 200, b"<html>No trials</html>", log.PROBE_DATE
            elif "/results" in url:
                return 200, b"<html>Cloudflare challenge-platform</html>", log.PROBE_DATE
            elif "trialsearch" in url:
                return 200, b"<html>captcha</html>", log.PROBE_DATE
            else:
                pytest.fail("Unexpected request " + url)
            return 200, log.encoded(obj), log.PROBE_DATE
    ids = dict(pmids=["12345"], dois=[], ncts=["NCT00000001"], eudract=[], title="ALPHA", acronym="ALPHA")
    result = log.live_searches(Transport(), ids, [])
    assert {r["source"] for r in result} == {"PUBMED_EPMC_PMID", "PUBMED_EPMC_TITLE", "UNPAYWALL_DOI", "CTGOV_V2", "AACT", "EUCTR", "WHO_ICTRP"}
    aact = next(r for r in result if r["source"] == "AACT")
    assert aact["outcome"] == "AACT snapshot unavailable"
    assert aact["step_reached"] == "ERROR"
    assert ids["eudract"] == ["2020-000001-01"]
    assert ids["dois"] == ["10.1234/demo"]
    for row in result:
        assert row["when_utc"].endswith("Z")
        if row["source"] != "AACT":
            assert len(row["response_sha256"]) == 64


def test_approval_cached_per_agent_anda_excluded():
    class Transport:
        def __init__(self):
            self.urls = []
        def get(self, url):
            self.urls.append(url)
            obj = {"results": [{"application_number": "ANDA000001"}]} if "api.fda.gov" in url else [{"category": "Human", "active_substance": "synthetic-agent", "name_of_medicine": "Synthetic EPAR"}]
            return 200, log.encoded(obj), log.PROBE_DATE
    client = Transport()
    approval = log.Approval(client)
    assert approval.approved("synthetic-agent")
    assert approval.approved("synthetic-agent")
    assert len(client.urls) == 2
    assert not approval.approved("other-agent")
    assert len(client.urls) == 3  # EMA metadata reused, ANDA alone insufficient


@pytest.mark.parametrize("body,status,expected", [(b"captcha", 403, "BLOCKED_BOT_CHALLENGE"), (b"upstream error", 503, "ERROR")])
def test_hc_gates(tmp_path, body, status, expected):
    class Transport:
        directory = tmp_path
        def get(self, url):
            return status, body, log.PROBE_DATE
    result = log.health_canada(Transport(), "synthetic-agent")
    assert result["step_reached"] == expected
    assert result["response_sha256"] == log.digest(body)


def test_hc_transport_error(tmp_path):
    class Transport:
        directory = tmp_path
        def get(self, url):
            raise OSError("synthetic unavailable")
    assert log.health_canada(Transport(), "synthetic-agent")["step_reached"] == "ERROR"


def test_ctgov_inconsistent_results_fail_closed():
    obj = {"protocolSection": {"identificationModule": {"nctId": "NCT00000001"}}, "hasResults": True}
    assert log.response_mapping("CTGOV_V2", log.encoded(obj))[0] == "ERROR"
