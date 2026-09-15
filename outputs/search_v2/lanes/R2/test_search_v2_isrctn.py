import json
from pathlib import Path

import pytest

from harness import acquisition as acq
from harness import http, search_v2


ROOT = Path(search_v2.ROOT)
FIXTURE = ROOT / "tests" / "fixtures" / "isrctn_sample.xml"


def _seal_row(cfg, collisions=None):
    return {
        "vocabulary_sha256": search_v2.vocabulary_sha(cfg),
        "benchmark_acronym_collision": {"coverage_text": "plant", "collisions": collisions or []},
    }


def _zero_meta():
    return [], {
        "hits": 0,
        "state": "RAN_ZERO",
        "error": None,
        "funnel": {"hits": 0, "fetched": 0, "retained": 0, "cap": {"kind": "none", "n": None, "remainder": None}},
    }


def test_parse_isrctn_sample_records_have_ids_titles_and_fields():
    xml = FIXTURE.read_text(encoding="utf-8")
    records, total = search_v2._parse_isrctn_records(xml)

    assert total == 31
    assert [r["id"] for r in records] == ["ISRCTN41823570", "ISRCTN85064961", "ISRCTN12564318"]
    assert records[0]["id_type"] == "isrctn"
    assert records[0]["isrctn"] == "ISRCTN41823570"
    assert records[0]["title"].startswith("A trial to assess if aspirin with omega-3 and colchicine")
    assert records[0]["acronym"] == "EASE-COPD"
    assert records[0]["year"] == "2026"
    assert records[0]["source"] == "isrctn"
    assert records[0]["conditions"]
    assert records[0]["interventions"]


def test_parse_isrctn_malformed_payload_raises():
    for payload in ("", "not xml at all <<<", "<allTrials totalCount='31'></allTrials>", "<root/>"):
        with pytest.raises(ValueError):
            search_v2._parse_isrctn_records(payload)


def test_isrctn_query_guard_refuses_name_seeded_term():
    query = search_v2._isrctn_query(["colchicine"], ["FAIR-HF2"])

    with pytest.raises(search_v2.QueryRefusal) as exc:
        search_v2.assert_discovery_query_allowed(query, "ISRCTN_CONDITION_INTERVENTION")

    assert "ISRCTN_CONDITION_INTERVENTION refused NAME_SEEDED: FAIR-HF2" in str(exc.value)


def test_query_builder_allows_sealed_vocabulary_tokens_for_isrctn(monkeypatch):
    cfg = {
        "intervention_agents": {"drug": ["drug", "BAY94-8862"]},
        "include": {"population_any": ["chronic kidney disease"]},
        "comparator_terms": ["placebo"],
    }
    monkeypatch.setattr(search_v2, "load_vocabulary_seal", lambda: {"slugs": {"plant": _seal_row(cfg)}})

    queries = search_v2.build_queries(cfg, "## PICO\n", lookup_mesh=False, slug="plant")

    assert queries["structural_kinds"]["isrctn"] == "FREE_TEXT_KEYWORD"
    assert '"BAY94-8862"' in queries["isrctn"]
    assert '"chronic kidney disease"' in queries["isrctn"]
    assert "bay94-8862" in [t.lower() for t in queries["vocabulary_exemption"]["exempted_tokens_in_queries"]]


def test_isrctn_adapter_paginates_without_record_cap_and_reports_meta(monkeypatch):
    calls = []

    def payload(total, ids):
        body = [f'<allTrials totalCount="{total}" xmlns="http://www.67bricks.com/isrctn">']
        for rid in ids:
            body.append(
                f"<fullTrial><trial publicIdentifierCanonical=\"{rid}\" publicIdentifierDateAssigned=\"2026-01-01T00:00:00Z\">"
                f"<isrctn>{rid[6:]}</isrctn><trialDescription><title>{rid} title</title></trialDescription>"
                "<conditions><condition>pericarditis</condition></conditions>"
                "<interventions><intervention>colchicine</intervention></interventions>"
                "</trial></fullTrial>"
            )
        body.append("</allTrials>")
        return "".join(body)

    pages = {
        0: payload(1001, ["ISRCTN00000001"]),
        1000: payload(1001, ["ISRCTN00000002"]),
    }

    def fake_get_text(url, params=None, **kw):
        calls.append((url, dict(params or {})))
        return pages[params["offset"]]

    monkeypatch.setattr(http, "get_text", fake_get_text)
    monkeypatch.setattr(search_v2.time, "sleep", lambda seconds: calls.append(("sleep", {"seconds": seconds})))

    records, meta = search_v2._isrctn_search_records("(colchicine) AND (pericarditis)")

    assert [r["id"] for r in records] == ["ISRCTN00000001", "ISRCTN00000002"]
    assert [c[1]["offset"] for c in calls if c[0] != "sleep"] == [0, 1000]
    assert any(c == ("sleep", {"seconds": 0.5}) for c in calls)
    assert meta["hits"] == 1001
    assert meta["state"] == "RAN_OK"
    assert meta["funnel"]["cap"]["kind"] == "none"
    assert meta["funnel"]["page_size"] == 1000


def test_refresh_topic_default_does_not_call_isrctn_adapter(tmp_path, monkeypatch):
    (tmp_path / "topics").mkdir()
    (tmp_path / "protocols").mkdir()
    cfg = {
        "slug": "plant",
        "intervention_agents": {"colchicine": ["colchicine"]},
        "include": {"population_any": ["pericarditis"]},
        "comparator_terms": ["placebo"],
    }
    (tmp_path / "topics" / "plant.json").write_text(json.dumps(cfg), encoding="utf-8")
    (tmp_path / "protocols" / "plant.md").write_text("## PICO\n- P pericarditis\n", encoding="utf-8")

    def isrctn_boom(query):
        raise AssertionError("ISRCTN adapter should be opt-in")

    monkeypatch.setattr(search_v2, "ROOT", str(tmp_path))
    monkeypatch.setattr(search_v2, "_mesh_heading", lambda term: None)
    monkeypatch.setattr(search_v2, "_pubmed_search_records", lambda query: _zero_meta())
    monkeypatch.setattr(search_v2, "_epmc_search_records", lambda query: _zero_meta())
    monkeypatch.setattr(search_v2, "_ctgov_search_records", lambda query: _zero_meta())
    monkeypatch.setattr(search_v2, "_isrctn_search_records", isrctn_boom)

    row = search_v2.refresh_topic("plant", "2026-09-15", snapshot_name="2026-09-15r2-search_v2")
    kinds = [src["kind"] for src in row["ledger"]["sources"]]

    assert "ISRCTN_CONDITION_INTERVENTION" not in kinds
    assert "isrctn" not in row["records"]["search_v2"]["queries"]
    assert row["records"]["search_v2"]["queries"]["structural_kinds"] == {
        "pubmed": "FREE_TEXT_KEYWORD",
        "europepmc": "FREE_TEXT_KEYWORD",
        "ctgov": "FREE_TEXT_KEYWORD",
    }
    assert "ISRCTN_CONDITION_INTERVENTION" in acq.SOURCE_KINDS
