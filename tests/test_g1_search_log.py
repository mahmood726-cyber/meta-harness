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
    ("PUBMED_EPMC_PMID", epmc(isOpenAccess="Y"), {}, "OPEN_NOT_ASSESSED"),
    ("PUBMED_EPMC_PMID", epmc(isOpenAccess="Y"), {"blocker_now": "OUTCOME_NOT_IN_SOURCE"}, "OPEN_NO_OUTCOME"),
    ("PUBMED_EPMC_PMID", epmc(inEPMC="Y"), {"stage": "EXTRACTION"}, "OPEN_OUTCOME_NOT_BINDABLE"),
    ("PUBMED_EPMC_PMID", epmc(isOpenAccess="Y"), {"decision": "TYPED_NONE_NOT_MODEL_LICENSED", "blocker_now": "OUTCOME_NOT_IN_SOURCE"}, "OPEN_OUTCOME_NOT_BINDABLE"),
    ("PUBMED_EPMC_PMID", {"hitCount": 0}, {}, "NOT_FOUND"),
    ("PUBMED_EPMC_PMID", {}, {}, "ERROR"),
    ("PUBMED_EPMC_TITLE", {"hitCount": 0}, {}, "NOT_FOUND"),
    ("PUBMED_EPMC_TITLE", epmc(title="A trial"), {}, "NOT_FOUND"),
    ("UNPAYWALL_DOI", {"is_oa": False}, {}, "FOUND_NOT_OPEN"),
    ("UNPAYWALL_DOI", {"is_oa": True}, {}, "OPEN_NOT_ASSESSED"),
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
    (b'<html><script src="app.js"></script>Please enable JavaScript</html>', "BLOCKED_JS_ONLY"),
    (b'<html>No records found</html>', "NOT_FOUND"),
])
def test_who(body, expected):
    assert log.response_mapping("WHO_ICTRP", body)[0] == expected


def test_title_rct_requires_trial_name():
    obj = epmc(title="Randomized study ALPHA NCT00000001", pubTypeList={"pubType": ["Randomized Controlled Trial"]})
    step, outcome = log.response_mapping("PUBMED_EPMC_TITLE", log.encoded(obj), identifiers={"ncts": ["NCT00000001"]})
    assert step == "NEW_REPORT_FOUND"
    assert outcome["new_pmids"] == ["12345"]
    assert log.response_mapping("PUBMED_EPMC_TITLE", log.encoded(obj), identifiers={"ncts": ["NCT00000002"]})[1]["reports_naming_trial"] == []


def test_identifier_mismatch():
    assert log.response_mapping("PUBMED_EPMC_PMID", log.encoded(epmc()), identifiers={"pmid": "999"})[0] == "ERROR"
    obj = {"protocolSection": {"identificationModule": {"nctId": "NCT00000001"}}}
    assert log.response_mapping("CTGOV_V2", log.encoded(obj), identifiers={"nct": "NCT00000002"})[0] == "ERROR"


def test_regulator_metadata_plant(tmp_path):
    path = tmp_path / "plant.json"
    plant = dict(label="ALPHA", phase="2_REGULATOR:FDA", stage="READ", decision="REFUSED", verdict="NOT_ADMITTED", ncts=["NCT00000001", {"span": "SECRET"}, "SECRET"],
                 documents_naming=["SECRET DOCUMENT"], candidate={"span": "SECRET"}, readers={"secret": "SECRET"}, span="SECRET")
    path.write_text(json.dumps({"rows": [plant]}), encoding="utf-8")
    result = log.regulator_summary(path)
    assert set(result[0]) == {"label", "phase", "stage", "decision", "verdict", "ncts"}
    assert result[0]["ncts"] == ["NCT00000001"]
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
            {"label": "ALPHA", "route": "NO_ROW", "family": "PMID 12345", "identity": {"nct": "NCT00000001"}},
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
    assert trial["identifiers"]["ncts"] == ["NCT00000001"]
    assert trial["identifiers"]["provenance"]["NCT00000001"] == ["outputs/k_gap/g1/demo.json#trials[label=ALPHA].identity.nct"]
    assert {r["source"] for r in trial["searched"]} == {"FDA", "EMA_CLINICAL_DATA"}
    assert "PLANTED" not in json.dumps(out)
    assert "trials=1, records=2" in capsys.readouterr().out


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
    assert "synthetic missing snapshot" in aact["outcome"]
    assert aact["step_reached"] == "ERROR"
    assert ids["eudract"] == ["2020-000001-01"]
    assert ids["dois"] == ["10.1234/demo"]
    assert ids["provenance"]["2020-000001-01"] == ["https://clinicaltrials.gov/api/v2/studies/NCT00000001#secondaryIdInfos.id"]
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


@pytest.mark.parametrize("field", ["family", "identity", "acquisition_cascade", "identification"])
def test_tracker_identifier_sources(field):
    ids = log.identifiers({"label": "ALPHA", field: {"note": "NCT00000001 EudraCT 2020-000001-01"}}, "demo", [], [], {})
    assert ids["ncts"] == ["NCT00000001"]
    assert ids["eudract"] == ["2020-000001-01"]
    assert any(field + ".note" in p for p in ids["provenance"]["NCT00000001"])


@pytest.mark.parametrize("source", ["funnel", "identification", "regulator", "eu"])
def test_identifier_files(tmp_path, source):
    row = {"slug": "demo", "label": "ALPHA", "ncts": ["NCT00000001"]}
    paths = {"funnel": "outputs/k_gap/registry_fill/demo.funnel.json",
             "identification": "outputs/k_gap/registry_fill/IDENTIFICATION.json",
             "regulator": "registry/g1_acquired_regulator/demo.json",
             "eu": "outputs/k_gap/registry_fill/EUDRACT_PROBE.json"}
    if source == "identification":
        row["identified"] = row.pop("ncts") + ["2020-000001-01"]
    if source == "eu":
        row.pop("ncts")
        row["label"] = "ALPHA NCT00000001"
        row["results"] = [{"eudract": "2020-000001-01"}]
    obj = {"trials" if source == "eu" else "rows": [row]}
    path = tmp_path / paths[source]
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(obj), encoding="utf-8")
    class Repo:
        def matching(self, pattern):
            return [paths[source]]
        def read(self, name):
            return json.loads((tmp_path / name).read_text(encoding="utf-8"))
    loaded = log.source_rows(Repo(), "*") if source not in ("regulator", "eu") else []
    ids = log.identifiers({"label": row["label"]}, "demo", loaded if source == "identification" else [], [],
                          obj if source == "eu" else {}, loaded if source == "funnel" else [],
                          log.regulator_summary(path) if source == "regulator" else [])
    assert ids["ncts"] == ["NCT00000001"]
    assert any(p.startswith(paths[source] + "#") for p in ids["provenance"]["NCT00000001"])
    if source == "eu":
        assert ids["eudract"] == ["2020-000001-01"]
        assert paths[source] + "#trials[0].label" in ids["provenance"]["NCT00000001"]


def test_probe_join_and_wrong_trial_exclusion():
    probe = {"ncts_probed": [{"nct": "NCT00000001", "eudract_numbers": ["2020-000001-01"]},
                              {"nct": "NCT00000002", "eudract_numbers": ["2020-000001-01"]}]}
    ids = log.identifiers({"label": "ALPHA", "ncts": ["NCT00000001"]}, "demo", [], [], probe,
                          [{"slug": "other", "label": "ALPHA", "ncts": ["NCT00000003"]}])
    assert ids["ncts"] == ["NCT00000001"]
    assert ids["eudract"] == ["2020-000001-01"]
    assert ids["provenance"]["2020-000001-01"] == ["outputs/k_gap/registry_fill/EUDRACT_PROBE.json#ncts_probed[0].eudract_numbers[0]"]


@pytest.mark.parametrize("known,expected", [([], "NEW_REPORT_FOUND"), (["12345"], "NOT_FOUND")])
def test_title_known_report_without_rct_tag(known, expected):
    step, outcome = log.response_mapping("PUBMED_EPMC_TITLE", log.encoded(epmc(title="ALPHA follow-up")),
                                         identifiers={"acronym": "ALPHA", "pmids": known})
    assert step == expected
    assert outcome["new_pmids"] == ([] if known else ["12345"])
    if known:
        assert outcome["outcome"] == "no additional report"


def test_open_copy_metadata():
    step, outcome = log.response_mapping("UNPAYWALL_DOI", log.encoded({"is_oa": True, "best_oa_location": {
        "license": "cc-by", "url": "https://example.org/report"}}))
    assert step == "OPEN_NOT_ASSESSED"
    assert outcome["license"] == "cc-by"
    assert outcome["copy"] == "https://example.org/report"


@pytest.mark.parametrize("failure", [TimeoutError("synthetic timeout"), OSError("synthetic transport")])
def test_transport_exception_text(tmp_path, failure):
    client = log.Client(tmp_path, opener=Opener([failure]))
    rec, body = log.search(client, "PUBMED_EPMC_PMID", "https://example.org/search")
    assert rec["step_reached"] == "ERROR"
    assert str(failure) in rec["outcome"]
    assert body is None


def test_bad_body_exception_text():
    step, outcome = log.response_mapping("PUBMED_EPMC_PMID", b"not json")
    assert step == "ERROR"
    assert "JSONDecodeError:" in outcome


def test_provenance_merge(tmp_path):
    p = tmp_path / "demo.json"
    first = payload()
    first["trials"]["ALPHA"]["identifiers"]["provenance"] = {"12345": ["one.json#pmid"]}
    log.merge_write(p, first)
    first["trials"]["ALPHA"]["identifiers"]["provenance"] = {"12345": ["two.json#pmid"]}
    merged = log.merge_write(p, first)
    assert merged["trials"]["ALPHA"]["identifiers"]["provenance"]["12345"] == ["one.json#pmid", "two.json#pmid"]



def test_any_matching_census_assessment():
    assert log.open_step([{}, {"stage": "EXTRACTION"}]) == "OPEN_OUTCOME_NOT_BINDABLE"


def test_exhausted_5xx_keeps_exception(tmp_path):
    url = "https://example.org/search"
    op = Opener([HTTPError(url, 503, "synthetic unavailable", {}, io.BytesIO(b"down")) for _ in range(3)])
    rec, _ = log.search(log.Client(tmp_path, opener=op, sleep=lambda _: None), "PUBMED_EPMC_PMID", url)
    assert len(op.requests) == 3
    assert rec["step_reached"] == "ERROR"
    assert "synthetic unavailable" in rec["outcome"]



def test_who_unparseable_is_not_js_gate():
    step, outcome = log.response_mapping("WHO_ICTRP", b"broken body")
    assert step == "ERROR"
    assert "ValueError:" in outcome


@pytest.mark.parametrize("evidence,expected", [
    ("HTTP 200; query cannot be confirmed without JavaScript", "BLOCKED_JS_ONLY"),
    ("HTTP 200; JavaScript application shell without a searchable catalogue", "BLOCKED_JS_ONLY"),
    ("HTTP 403. Server response says Request blocked", "BLOCKED_BOT_CHALLENGE"),
    ("HTTP 403 CloudFront error; stopped", "BLOCKED_BOT_CHALLENGE"),
    ("HTTP 200 but unusable search response; domain filtering failed", "ERROR"),
    ("Read timed out: synthetic timeout", "ERROR"),
])
def test_inherited_discovery_failure_mapping(evidence, expected):
    rec = log.discovery_record({"source": "NIHR HTA", "status": "ERROR", "url": "https://example.org/search", "how_checked": evidence})
    assert rec["step_reached"] == expected
    assert rec["outcome"]["how_checked"] == evidence


def test_eu_identifier_404_is_not_transport_error(tmp_path, monkeypatch):
    from kgap import aact_adapter
    def unavailable():
        raise FileNotFoundError("synthetic snapshot missing")
    monkeypatch.setattr(aact_adapter, "snapshot_dir", unavailable)
    class Transport:
        directory = tmp_path
        def get(self, url):
            if "clinicaltrials.gov" in url:
                return 404, b"missing", log.PROBE_DATE
            if "trialsearch" in url:
                return 200, b"<script>app</script>", log.PROBE_DATE
            return 200, log.encoded({"hitCount": 0}), log.PROBE_DATE
    ids = dict(pmids=[], dois=[], ncts=["NCT00000001"], eudract=[], title="ALPHA", acronym="ALPHA")
    rec = next(r for r in log.live_searches(Transport(), ids, []) if r["source"] == "EUCTR")
    assert rec["step_reached"] == "NOT_FOUND"
    assert "HTTP Error 404" in rec["outcome"]



def test_known_companion_and_protocol_pmids_are_not_new_reports():
    row = {"slug": "demo", "label": "ALPHA", "report_pmid": "12345",
           "companions": [{"pmid": "23456"}], "protocol": [{"pmid": "34567"}],
           "_source": "outputs/k_gap/registry_fill/IDENTIFICATION_COMPANIONS.json"}
    ids = log.identifiers({"label": "ALPHA"}, "demo", [row], [], {})
    assert ids["pmids"] == ["12345", "23456", "34567"]
    assert ids["provenance"]["34567"] == ["outputs/k_gap/registry_fill/IDENTIFICATION_COMPANIONS.json#rows[0].protocol[0].pmid"]
    step, outcome = log.response_mapping("PUBMED_EPMC_TITLE", log.encoded(epmc(id="34567", title="ALPHA protocol")), identifiers=ids)
    assert step == "NOT_FOUND"
    assert outcome["outcome"] == "no additional report"
    assert outcome["new_pmids"] == []


@pytest.mark.parametrize("source", ["EUCTR", "AACT"])
def test_adapter_parse_failure_preserves_reason(source):
    step, outcome = log.response_mapping(source, log.encoded({"state": "PARSE_FAILED", "reason": "synthetic invalid endpoint table"}))
    assert step == "ERROR"
    assert outcome["error"] == "synthetic invalid endpoint table"



def test_live_eu_parser_exception_reason_survives_adapter(tmp_path, monkeypatch):
    from scripts import g1_eudract_source as eu
    monkeypatch.setattr(eu, "eudract_results", lambda no: {"state": "PARSE_FAILED", "reason": "synthetic parser exception"})
    class Transport:
        directory = tmp_path
        def get(self, url):
            if "europepmc" in url:
                return 200, log.encoded({"hitCount": 0}), log.PROBE_DATE
            if "trialsearch" in url:
                return 200, b"<script>app</script>", log.PROBE_DATE
            return 200, b"<html>synthetic malformed table</html>", log.PROBE_DATE
    ids = dict(pmids=[], dois=[], ncts=[], eudract=["2020-000001-01"], title="ALPHA", acronym="ALPHA")
    rec = next(r for r in log.live_searches(Transport(), ids, []) if r["source"] == "EUCTR")
    assert rec["step_reached"] == "ERROR"
    assert rec["outcome"]["error"] == "synthetic parser exception"



def test_malformed_provider_doi_is_metadata_not_typed_identifier():
    step, outcome = log.response_mapping("PUBMED_EPMC_PMID", log.encoded(epmc(isOpenAccess="Y", doi="/synthetic-suffix")))
    assert step == "OPEN_NOT_ASSESSED"
    assert outcome["doi"] is None
    assert outcome["reported_doi"] == "/synthetic-suffix"
    assert outcome["doi_validation_error"]
    ids = log.identifiers({"label": "ALPHA", "pmid": "12345"}, "demo", [],
                          [{"pmid": "12345", "europepmc": {"doi": "/synthetic-suffix"}}], {})
    assert ids["dois"] == []
    assert "/synthetic-suffix" not in ids["provenance"]


def test_legacy_bad_doi_removed_without_losing_search_history(tmp_path):
    path = tmp_path / "demo.json"
    rec = log.record("UNPAYWALL_DOI", "https://example.org/bad-doi", log.PROBE_DATE, "NOT_FOUND", "HTTP 404")
    old = payload(searches=[rec])
    old["trials"]["ALPHA"]["identifiers"].update(dois=["/synthetic-suffix", "10.1234/valid"],
        provenance={"/synthetic-suffix": ["source.json#doi"], "10.1234/valid": ["source.json#other_doi"]})
    path.write_text(json.dumps(old), encoding="utf-8")
    result = log.merge_write(path, payload())
    trial = result["trials"]["ALPHA"]
    assert trial["identifiers"]["dois"] == ["10.1234/valid"]
    assert "/synthetic-suffix" not in trial["identifiers"]["provenance"]
    assert trial["searched"] == [rec]


@pytest.mark.parametrize("sponsor,kind,expected", [("Pfizer", "INDUSTRY", True), ("Synthetic University", "OTHER", False)])
def test_own_sponsor_only(tmp_path, sponsor, kind, expected):
    class Transport:
        def __init__(self): self.urls = []
        def get(self, url):
            self.urls.append(url)
            if "clinicaltrials.gov" in url:
                return 200, log.encoded({"protocolSection":{"identificationModule":{"nctId":"NCT00000001"}, "sponsorCollaboratorsModule":{"leadSponsor":{"name":sponsor,"class":kind}, "collaborators":[{"name":"Novartis","class":"INDUSTRY"}]}}}), log.PROBE_DATE
            return 200, b'<main>No results</main>', log.PROBE_DATE
    client = Transport()
    ids = {"ncts":["NCT00000001"]}
    records = log.sponsor_searches(client, ids)
    assert bool(records) is expected
    assert not any("novartis" in u for u in client.urls)
    if expected: assert records[0]["lead_sponsor"] == sponsor
    ids = {"ncts":[]}
    assert log.sponsor_searches(client, ids) == []
    assert ids["notes"] == ["sponsor unknown"]


def test_adcomm_abuse_redirect_stops_before_request(tmp_path):
    redirect = log.SafeRedirect()
    class Transport:
        def pause(self, url): pytest.fail("must not follow abuse redirect")
    redirect.client = Transport()
    with pytest.raises(log.BotBlock, match="abuse"):
        redirect.redirect_request(None, None, 302, "", {}, "https://www.fda.gov/abuse")
    class Client:
        def get(self, url): raise log.BotBlock("Redirect to FDA abuse page")
    rec = log.html_listing(Client(), "FDA_ADCOMM", log.ADCOMM_INDEX, ["agent"], {})
    assert rec["step_reached"] == "BLOCKED_BOT_CHALLENGE"
    assert rec["when_utc"] and "abuse" in rec["outcome"]


def test_tga_timeout_three_attempts(tmp_path):
    op = Opener([TimeoutError("synthetic timeout") for _ in range(3)])
    sleeps = []
    rec = log.html_listing(log.Client(tmp_path, opener=op, sleep=sleeps.append), "TGA_AUSPAR", "https://www.tga.gov.au/resources/auspar", ["agent"], {})
    assert len(op.requests) == 3
    assert 1 in sleeps and 2 in sleeps
    assert rec["step_reached"] == "ERROR"
    assert "TimeoutError: synthetic timeout" in rec["outcome"]


@pytest.mark.parametrize("source", ["TGA_AUSPAR", "FDA_ADCOMM", "AHRQ_NIHR_HTA", "SPONSOR_REGISTER"])
def test_html_sources_do_not_infer_absence(source):
    class Client:
        def get(self, url): return 200, b'<html>Unexpected page</html>', log.PROBE_DATE
    assert log.html_listing(Client(), source, "https://example.org", ["agent"], {})["step_reached"] == "ERROR"


def test_ahrq_publisher_and_title_filter():
    class Client:
        def get(self, url):
            return 200, b'Publisher,Title,File\nAgency for Healthcare Research and Quality (US),Synthetic-agent review,a.tar.gz\nWrong publisher,Synthetic-agent review,b.tar.gz\nAgency for Healthcare Research and Quality (US),Other agent,c.tar.gz\n', log.PROBE_DATE
    rec = log.ahrq_search(Client(), ["Synthetic-agent"])
    assert len(rec["outcome"]["matches"]) == 1
    assert rec["outcome"]["matches"][0]["url"].endswith("a.tar.gz")
    assert rec["response_sha256"]


@pytest.mark.parametrize("text,types,expected", [
    ("NCT00000001 results", "Randomized Controlled Trial", "PRIMARY_REPORT"),
    ("ALPHA trial results", "Randomized Controlled Trial", "PRIMARY_REPORT"),
    ("NCT00000001 secondary analysis", "Journal Article", "COMPANION"),
    ("unrelated results", "Randomized Controlled Trial", "NOT_THE_TRIAL"),
    ("smart technology", "Journal Article", "NOT_THE_TRIAL"),
])
def test_pubmed_followup_verdict(text, types, expected):
    body = f'<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>12345</PMID><Article><ArticleTitle>{text}</ArticleTitle><Abstract><AbstractText>{text}</AbstractText></Abstract><PublicationTypeList><PublicationType>{types}</PublicationType></PublicationTypeList></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>'.encode()
    verdict, _ = log.pubmed_verdict(body, "12345", {"ncts":["NCT00000001"],"acronym":"ALPHA"})
    assert verdict == expected


def test_pubmed_secondary_identifier():
    body = b'<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>12345</PMID><Article><ArticleTitle>Results</ArticleTitle><DataBankList><DataBank><AccessionNumberList><AccessionNumber>NCT00000001</AccessionNumber></AccessionNumberList></DataBank></DataBankList><PublicationTypeList><PublicationType>Randomized Controlled Trial</PublicationType></PublicationTypeList></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>'
    assert log.pubmed_verdict(body, "12345", {"ncts":["NCT00000001"]})[0] == "PRIMARY_REPORT"
    with pytest.raises(ValueError, match="absent"):
        log.pubmed_verdict(body, "99999", {})


def test_pmda_listing_no_trial_match(tmp_path):
    class Client:
        def get(self, url): return 200, b'<main>Review Reports. Public Data License 1.0</main>', log.PROBE_DATE
    rec = log.pmda_search(Client(), ["synthetic-agent"], {"ncts":["NCT00000001"]}, ["mortality"], tmp_path)
    assert rec["step_reached"] == "NOT_FOUND"
    assert rec["outcome"]["licence"] == "Public Data License 1.0"
    assert rec["response_sha256"]


@pytest.mark.parametrize("text,licence,expected", [
    ("NCT00000001 mortality results", True, "OPEN_OUTCOME_NOT_BINDABLE"),
    ("NCT00000001 safety only", True, "OPEN_NO_OUTCOME"),
    ("NCT00000001 mortality results", False, "FOUND_NOT_OPEN"),
    ("NCT99999999 mortality results", True, "NOT_FOUND"),
])
def test_pmda_report_text_rules(tmp_path, monkeypatch, text, licence, expected):
    import pypdf
    class Page:
        def extract_text(self): return text
    class Reader:
        def __init__(self, body): self.pages = [Page()]
    monkeypatch.setattr(pypdf, "PdfReader", Reader)
    class Client:
        def get(self, url):
            if url.endswith(".pdf"): return 200, b"synthetic PDF fixture", log.PROBE_DATE
            policy = "Public Data License 1.0" if licence else ""
            return 200, (f'<main>{policy}<table><tr><td>synthetic-agent</td><td><a href="/files/synthetic.pdf">English</a></td></tr></table></main>').encode(), log.PROBE_DATE
    rec = log.pmda_search(Client(), ["synthetic-agent"], {"ncts":["NCT00000001"]}, ["mortality"], tmp_path)
    assert rec["step_reached"] == expected
    assert rec["outcome"]["reports"][0]["response_sha256"] == log.digest(b"synthetic PDF fixture")
    assert list((tmp_path / "outputs/k_gap/_reg/pmda").glob("*.txt"))


def test_acronym_collision_is_not_companion():
    body = b'<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>12345</PMID><Article><ArticleTitle>ALPHA software tool</ArticleTitle><PublicationTypeList><PublicationType>Journal Article</PublicationType></PublicationTypeList></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>'
    assert log.pubmed_verdict(body,"12345",{"acronym":"ALPHA"})[0] == "NOT_THE_TRIAL"


def test_held_regulator_metadata_only(monkeypatch):
    from scripts import g1_regulatory_source as reg
    def evidence(*args):
        return [], {"https://example.org/review": {"text":"PLANTED SECRET SPAN", "record":{"agency":"FDA", "text_sha256":"a"*64}}}
    monkeypatch.setattr(reg,"regulatory_evidence",evidence)
    recs = log.held_searches({"label":"ALPHA"},{"ncts":[]},"demo")
    assert [r["step_reached"] for r in recs] == ["FOUND_NOT_OPEN","NOT_FOUND"]
    assert "PLANTED" not in json.dumps(recs)


@pytest.mark.parametrize("title,abstract,ids,expected", [
    ("ALPHA II trial", "synthetic-agent trial", {"acronym":"ALPHA"}, "NOT_THE_TRIAL"),
    ("ALPHA-HF trial", "synthetic-agent trial", {"acronym":"ALPHA"}, "NOT_THE_TRIAL"),
    ("O fish trial", "Fish feeding", {"acronym":"O"}, "NOT_THE_TRIAL"),
    ("Other condition treatment (ALPHA) trial", "unrelated treatment", {"acronym":"ALPHA", "topic_terms":["synthetic-agent"]}, "NOT_THE_TRIAL"),
    ("ALPHA trial subanalysis", "synthetic-agent", {"acronym":"ALPHA"}, "COMPANION"),
    ("ALPHA trial", "A post hoc analysis of synthetic-agent", {"acronym":"ALPHA"}, "COMPANION"),
    ("ALPHA trial", "Randomized synthetic-agent results", {"acronym":"ALPHA", "topic_agents":["synthetic-agent"],"topic_terms":["synthetic-agent"]}, "PRIMARY_REPORT"),
    ("ALPHA trial", "Randomized synthetic-agent results with median follow-up reported", {"acronym":"ALPHA", "topic_agents":["synthetic-agent"],"topic_terms":["synthetic-agent"]}, "PRIMARY_REPORT"),
    ("ALPHA trial update", "Clinical trial meeting report", {"acronym":"ALPHA", "topic_agents":["synthetic-agent"],"topic_terms":["synthetic-agent"]}, "COMPANION"),
])
def test_followup_disambiguation_and_secondary_reports(title, abstract, ids, expected):
    body = f'<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>12345</PMID><Article><ArticleTitle>{title}</ArticleTitle><Abstract><AbstractText>{abstract}</AbstractText></Abstract><PublicationTypeList><PublicationType>Randomized Controlled Trial</PublicationType></PublicationTypeList></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>'.encode()
    assert log.pubmed_verdict(body,"12345",ids)[0] == expected


@pytest.mark.parametrize("name,allowed", [("Merck Sharp & Dohme LLC", True), ("Merck KGaA", False)])
def test_distinct_merck_sponsors_are_not_cross_routed(name, allowed):
    class Client:
        def __init__(self): self.urls=[]
        def get(self,url):
            self.urls.append(url)
            if "clinicaltrials.gov" in url:
                return 200, log.encoded({"protocolSection":{"identificationModule":{"nctId":"NCT00000001"},"sponsorCollaboratorsModule":{"leadSponsor":{"name":name,"class":"INDUSTRY"}}}}),log.PROBE_DATE
            return 200,b"No results",log.PROBE_DATE
    client=Client()
    records=log.sponsor_searches(client,{"ncts":["NCT00000001"]})
    assert any("merckclinicaltrials.com" in u for u in client.urls) is allowed
    if not allowed:
        assert records[0]["step_reached"] == "ERROR"
        assert name in records[0]["outcome"]


def test_PLANT_read_target_rows_reach_the_search_log():
    """18 Oct: phase3_targets rows (copies read by job H) were never matched -- a DOI-only Unpaywall copy carries its DOI
    in source.doi, and OUTCOME_FOUND_NOT_BINDABLE was not mapped -- so every read copy stayed OPEN_NOT_ASSESSED."""
    rows = [{"source": {"doi": "10.1/X"}, "decision": "OUTCOME_NOT_IN_SOURCE"},
            {"doi": "10.2/y", "decision": "OUTCOME_FOUND_NOT_BINDABLE:SUBPOPULATION"},
            {"europepmc": {"doi": "10.3/z"}, "decision": "NOT_OPEN"}]
    assert log.open_step(log.census_rows_for_doi(rows, "10.1/x")) == "OPEN_NO_OUTCOME"
    assert log.open_step(log.census_rows_for_doi(rows, "10.2/Y")) == "OPEN_OUTCOME_NOT_BINDABLE"
    assert log.census_rows_for_doi(rows, "10.9/none") == []
    assert log.open_step([]) == "OPEN_NOT_ASSESSED"


@pytest.mark.parametrize("content,step,named,row", [
    ("<p>Other trial 10 20</p>", "OPEN_NO_OUTCOME", False, False),
    ("<table><tr><td>Burr 1989</td><td>12</td><td>24</td></tr></table>", "OPEN_OUTCOME_NOT_BINDABLE", True, True),
    ("<p>Burr 19890</p>", "OPEN_NO_OUTCOME", False, False),
    ("<p>Burr 1989 12 24</p>", "OPEN_OUTCOME_NOT_BINDABLE", True, False),
    ("<table><tr><td>GISSI-HF</td><td>12</td><td>24</td></tr></table>", "OPEN_OUTCOME_NOT_BINDABLE", True, True),
    ("<p>NCT00000001</p>", "OPEN_OUTCOME_NOT_BINDABLE", True, False),
])
def test_assess_ahrq(tmp_path, content, step, named, row):
    import tarfile
    folder = tmp_path / "outputs/k_gap/_search_log_cache/litarch/NBK123"
    folder.mkdir(parents=True)
    with tarfile.open(folder / "package.tar.gz", "w:gz") as archive:
        for name, xml in [("chapter.nxml", "<book><permissions><copyright-statement>Public domain</copyright-statement></permissions>" + content + "</book>"),
                          ("../unsafe.nxml", "<book><table><tr><td>Burr 1989 50 60</td></tr></table></book>")]:
            raw = xml.encode()
            member = tarfile.TarInfo(name)
            member.size = len(raw)
            archive.addfile(member, io.BytesIO(raw))
    old = log.record("AHRQ_NIHR_HTA", "https://ftp.ncbi.nlm.nih.gov/pub/litarch/file_list.csv", "2026-01-01T00:00:00Z",
                     "OPEN_NOT_ASSESSED", {"provider": "AHRQ", "matches": [{"url": "https://ftp.ncbi.nlm.nih.gov/pub/litarch/aa/bb/book_NBK123.tar.gz"}]})
    original = json.loads(json.dumps(old))
    ids = dict(label="Burr et al, 1989 [23]", acronym="GISSI-HF", ncts=["NCT00000001"])
    assessed = log.assess_ahrq(old, ids, root=tmp_path)
    assert old == original
    assert assessed["step_reached"] == step
    assert assessed["outcome"]["named"] is named
    assert assessed["outcome"].get("per_trial_row_present", False) is row
    assert assessed["outcome"].get("secondary_source", False) is named
    assert "Public domain" in assessed["outcome"]["licence"]["NBK123"]["permissions"][0]
    assert assessed["identifier_or_query"] == old["identifier_or_query"]
    assert assessed["when_utc"] > old["when_utc"]
    assert log.ahrq_pending([old, assessed]) == []
    path = tmp_path / "search.json"
    for rec in (old, assessed):
        merged = log.merge_write(path, dict(slug="synthetic", written_utc=rec["when_utc"], trials={"Burr": dict(
            identifiers=ids, searched=[rec], secondary_value_available=rec["outcome"].get("per_trial_row_present", False))}))
    assert merged["trials"]["Burr"]["secondary_value_available"] is row
    assert merged["trials"]["Burr"]["searched"] == [old, assessed]


def test_ahrq_download_once_and_failure_closed(tmp_path):
    import tarfile
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:gz") as archive:
        raw = b"<book><p>ALPHA</p><p>ALPHA &amp; BETA</p><p>MixedCase</p></book>"
        member = tarfile.TarInfo("chapter.nxml")
        member.size = len(raw)
        archive.addfile(member, io.BytesIO(raw))
    class Client:
        calls = 0
        def get(self, url):
            self.calls += 1
            return 200, stream.getvalue(), log.utc_now()
    rec = log.record("AHRQ_NIHR_HTA", "https://ftp.ncbi.nlm.nih.gov/pub/litarch/file_list.csv", log.PROBE_DATE,
                     "OPEN_NOT_ASSESSED", {"provider": "AHRQ", "matches": [{"url": "https://ftp.ncbi.nlm.nih.gov/pub/litarch/aa/bb/test_NBK456.tar.gz"}]})
    with pytest.raises(ValueError, match="Missing cached"):
        log.assess_ahrq(rec, {"acronym": "ALPHA"}, root=tmp_path)
    client = Client()
    for _ in range(2):
        assert log.assess_ahrq(rec, {"acronym": "ALPHA"}, root=tmp_path, client=client)["outcome"]["named"]
    assert client.calls == 1
    assert log.assess_ahrq(rec, {"label": "ALPHA 2013 [42]"}, root=tmp_path)["outcome"]["named"] is False
    # A multiword trial designation is taken literally from the label.
    assert log.assess_ahrq(rec, {"label": "ALPHA & BETA 2013 [42]"}, root=tmp_path)["outcome"]["named"] is True
    assert log.assess_ahrq(rec, {"label": "MixedCase"}, root=tmp_path)["outcome"]["named"]
    with pytest.raises(ValueError, match="No trial names"):
        log.assess_ahrq(rec, {"label": "2 [22]"}, root=tmp_path)
    assert log.assess_ahrq(rec, {"acronym": "ALPHA"}, root=tmp_path)["outcome"]["named"]
