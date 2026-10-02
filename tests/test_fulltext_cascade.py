"""Plants for scripts/fulltext_cascade.py: a failed REQUEST must never be recorded as a fact about the ARTICLE.

The cascade it replaces (scripts/lane_fulltext.py) swallowed every exception and counted the trial "no_open_access";
at ~5 requests/s against NCBI's 3/s limit, throttled calls silently became "not open access" (G1 tocilizumab, RECOVERY
PMC8084355 not held). Each plant names the old behaviour it would have tolerated.
"""
import importlib.util
import io
import json
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("fulltext_cascade", ROOT / "scripts" / "fulltext_cascade.py")
fc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fc)

BODY = b"<article><front/><body><p>Deaths 621 of 2022 vs 729 of 2094</p></body></article>"
STUB = b"<article><front/></article>"


class Fake(fc.Http):
    """Scripted responses by URL substring; an Exception value is raised."""

    def __init__(self, script):
        super().__init__(min_interval=0, sleep=lambda s: None)
        self.script = script
        self.calls = []

    def get(self, url, params=None, timeout=60):
        key = url + "?" + json.dumps(params or {}, sort_keys=True)
        self.calls.append(key)
        for needle, value in self.script:
            if needle in key:
                if isinstance(value, Exception):
                    raise value
                return value
        raise fc.FetchFailed(f"unscripted request {key}")  # an unscripted route behaves as a failed request


def _elink(pmcid):
    return json.dumps({"linksets": [{"linksetdbs": [{"linkname": "pubmed_pmc", "links": [pmcid]}]}]}).encode()


def test_PLANT_a_request_that_keeps_failing_is_FETCH_FAILED_never_NOT_IN_PMC(tmp_path):
    http = Fake([("elink", fc.FetchFailed("HTTP 429 after 4 tries"))])
    row = fc.acquire(http, "t", "33933206", dry_run=True, root=tmp_path)
    assert row["state"] == fc.FETCH_FAILED and row["state"] != fc.NOT_IN_PMC


def test_PLANT_a_throttled_request_is_retried_and_then_succeeds(monkeypatch):
    seen = {"n": 0}

    def urlopen(req, timeout=60):
        seen["n"] += 1
        if seen["n"] == 1:
            raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", {}, io.BytesIO(b""))
        return io.BytesIO(b"ok")

    monkeypatch.setattr(fc.urllib.request, "urlopen", urlopen)
    http = fc.Http(min_interval=0, sleep=lambda s: None)
    assert http.get("https://example.invalid/x") == b"ok" and seen["n"] == 2


def test_a_non_retryable_status_fails_at_once(monkeypatch):
    def urlopen(req, timeout=60):
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, io.BytesIO(b""))
    monkeypatch.setattr(fc.urllib.request, "urlopen", urlopen)
    with pytest.raises(fc.FetchFailed, match="HTTP 404"):
        fc.Http(min_interval=0, sleep=lambda s: None).get("https://example.invalid/x")


def test_PLANT_ncbi_without_a_body_falls_back_to_europe_pmc(tmp_path):
    http = Fake([("elink", _elink("8084355")), ("efetch", STUB), ("fullTextXML", BODY)])
    row = fc.acquire(http, "t", "33933206", dry_run=False, root=tmp_path)
    assert row["state"] == fc.FETCHED and row["route"] == "EUROPEPMC_FULLTEXTXML"
    assert (tmp_path / "cache" / "t" / "ft_33933206.txt").read_bytes() == BODY


def test_no_route_with_a_body_is_NO_BODY_and_a_citing_link_is_NOT_IN_PMC(tmp_path):
    http = Fake([("elink", _elink("7953461")), ("efetch", STUB), ("fullTextXML", STUB)])
    assert fc.acquire(http, "t", "33631065", dry_run=True, root=tmp_path)["state"] == fc.NO_BODY
    refs_only = json.dumps({"linksets": [{"linksetdbs": [{"linkname": "pubmed_pmc_refs", "links": ["999"]}]}]}).encode()
    assert fc.acquire(Fake([("elink", refs_only)]), "t", "1", dry_run=True, root=tmp_path)["state"] == fc.NOT_IN_PMC


def test_a_held_text_is_not_refetched(tmp_path):
    (tmp_path / "cache" / "t").mkdir(parents=True)
    (tmp_path / "cache" / "t" / "ft_5.txt").write_bytes(BODY)
    http = Fake([])
    assert fc.acquire(http, "t", "5", dry_run=False, root=tmp_path)["state"] == fc.HELD and http.calls == []


def test_PLANT_targets_include_the_comparators_trials_not_only_ours(tmp_path):
    (tmp_path / "docs" / "reviews" / "t").mkdir(parents=True)
    (tmp_path / "docs" / "reviews" / "t" / "review.json").write_text(json.dumps(
        {"outcomes": [{"trials": [{"id": "PMID 11111111"}]}], "screening": {"records": []}}), encoding="utf-8")
    (tmp_path / "registry" / "secondary_meta").mkdir(parents=True)
    (tmp_path / "registry" / "secondary_meta" / "t.json").write_text(json.dumps(
        {"rows": [{"trial": "REMAP-CAP", "pmid": "33631065"}]}), encoding="utf-8")
    tg = fc.targets("t", tmp_path)
    assert "11111111" in tg and tg["33631065"] == ["comparator trial (secondary_meta)"]


def test_a_registration_is_resolved_to_its_reports(tmp_path):
    http = Fake([("esearch", json.dumps({"esearchresult": {"idlist": ["33631065"]}}).encode()),
                 ("elink", _elink("7953461")), ("efetch", BODY)])
    led = fc.run("t", http, dry_run=True, extra_ncts=["NCT02735707"], root=tmp_path)
    row = next(r for r in led["rows"] if r["pmid"] == "33631065")
    assert row["state"] == fc.FETCHED and "registration NCT02735707 (PubMed secondary id)" in row["why"]


def test_stage_writes_outside_the_cache_so_served_pages_cannot_move(tmp_path):
    http = Fake([("elink", _elink("8084355")), ("efetch", BODY)])
    stage = tmp_path / "stage"
    led = fc.run("t", http, dry_run=False, extra_pmids=["33933206"], root=tmp_path, stage=stage)
    assert (stage / "t" / "ft_33933206.txt").read_bytes() == BODY
    assert not (tmp_path / "cache").exists() and led["tally"][fc.FETCHED] == 1


PDF = b"%PDF-1.7 RECOVERY tocilizumab report"


def test_PLANT_recovery_is_acquired_through_unpaywall_when_pmc_has_no_body(tmp_path):
    """RECOVERY (PMID 33933206): even when no PMC route returns a body, its CC-BY Lancet PDF is located by DOI."""
    unpay = json.dumps({"is_oa": True, "best_oa_location": {"url_for_pdf": "https://pdf.example/recovery.pdf",
                                                             "host_type": "publisher", "license": "cc-by"}}).encode()
    http = Fake([("elink", _elink("8084355")), ("efetch", STUB), ("fullTextXML", STUB), ("unpaywall", unpay),
                 ("recovery.pdf", PDF)])
    row = fc.acquire(http, "t", "33933206", dry_run=False, root=tmp_path,
                     ident={"doi": "10.1016/S0140-6736(21)00676-0", "nct": None})
    assert row["state"] == fc.FETCHED and row["route"] == "UNPAYWALL_PDF"
    assert (tmp_path / "cache" / "t" / "ft_33933206.pdf").read_bytes() == PDF
    assert [r["route"] for r in row["routes"]][:3] == ["PMC_ELINK", "NCBI_EFETCH_PMC", "EUROPEPMC_FULLTEXTXML"]


def test_registry_results_status_is_logged_beside_the_text_routes(tmp_path):
    http = Fake([("clinicaltrials.gov", json.dumps({"hasResults": True}).encode()), ("elink", _elink("1")),
                 ("efetch", BODY)])
    row = fc.acquire(http, "t", "2", dry_run=True, root=tmp_path, ident={"nct": "NCT04320615"})
    assert row["registry"]["ctgov"] == {"nct": "NCT04320615", "has_results": True} and row["state"] == fc.FETCHED


def test_all_routes_failing_by_request_is_FETCH_FAILED(tmp_path):
    http = Fake([("elink", fc.FetchFailed("HTTP 503 after 4 tries"))])
    assert fc.acquire(http, "t", "3", dry_run=True, root=tmp_path, ident={})["state"] == fc.FETCH_FAILED
