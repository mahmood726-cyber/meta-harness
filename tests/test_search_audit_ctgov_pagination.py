"""Plant (search+screen audit, 2026-10-05): the registered CT.gov query retains EVERY page, and a shortfall is recorded.

Before: harness.fetch._ctgov_search fetched one page of 30 with no total, so 16 of 32 G1 topics were silently truncated
(tocilizumab 30 of 86: COV-AID, COVIDOSE2, COVIDSTORM, COVITOZ, REMAP-CAP, REMDACTA and TOCOVID matched the query and
were never retained). Both tests fail on the old code (one page; no countTotal; no funnel hits)."""
from __future__ import annotations

from harness import fetch


def _study(n):
    return {"protocolSection": {"identificationModule": {"nctId": f"NCT{n:08d}", "briefTitle": f"t{n}"},
                                "designModule": {}, "conditionsModule": {}, "armsInterventionsModule": {}}}


def _pages(total, per, served=None):
    served = total if served is None else served
    pages = [list(range(i, min(i + per, served))) for i in range(0, served, per)]

    def get_json(url, params=None, **kw):
        tok = (params or {}).get("pageToken")
        i = int(tok) if tok else 0
        d = {"studies": [_study(n) for n in pages[i]], "totalCount": total}
        if i + 1 < len(pages):
            d["nextPageToken"] = str(i + 1)
        get_json.calls.append(dict(params or {}))
        return d
    get_json.calls = []
    return get_json


def test_every_page_is_retained_and_the_total_is_recorded(monkeypatch):
    g = _pages(86, 30)
    monkeypatch.setattr(fetch.http, "get_json", g)
    r = fetch._ctgov_search_result("COVID-19", "tocilizumab", page_size=30)
    assert len(r["records"]) == 86 and r["count"] == 86 and len(set(r["ids"])) == 86
    assert r["funnel"]["hits"] == 86 and r["funnel"]["cap"]["kind"] == "none"
    assert g.calls[0].get("countTotal") == "true" and len(g.calls) == 3
    assert len(fetch._ctgov_search("COVID-19", "tocilizumab")) == 86      # the list API keeps its shape


def test_a_shortfall_against_the_sources_own_total_is_never_silent(monkeypatch):
    monkeypatch.setattr(fetch.http, "get_json", _pages(86, 30, served=60))
    r = fetch._ctgov_search_result("COVID-19", "tocilizumab", page_size=30)
    assert len(r["ids"]) == 60
    assert r["funnel"]["cap"] == {"kind": "pagination_incomplete", "n": 60, "remainder": 26}
