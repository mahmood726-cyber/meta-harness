"""Plant: a comparator-swap search records the database's own COUNT and pages to it. The first run of 7 Oct stopped at
PubMed's retmax 600 and Europe PMC's single page of 1000 while reporting 'pubmed 600' -- its reach, read as the population.
Now every page is fetched; a search that still falls short is written as TRUNCATED, never as complete."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_swap as g  # noqa: E402


class _Fake:
    """1,234 PubMed ids and 2,345 Europe PMC hits, served page by page like the real APIs."""

    def __init__(self):
        self.pm = [str(10000 + i) for i in range(1234)]
        self.ep = [str(50000 + i) for i in range(2345)]

    def get_raw(self, url, params=None, **kw):
        if "esearch" in url:
            s, n = int(params.get("retstart", 0)), int(params["retmax"])
            return 200, json.dumps({"esearchresult": {"count": str(len(self.pm)), "idlist": self.pm[s:s + n]}}).encode()
        cur, n = params.get("cursorMark", "*"), int(params["pageSize"])
        s = 0 if cur == "*" else int(cur)
        nxt = str(s + n) if s + n < len(self.ep) else cur
        return 200, json.dumps({"hitCount": len(self.ep), "nextCursorMark": nxt,
                                "resultList": {"result": [{"pmid": p} for p in self.ep[s:s + n]]}}).encode()


def test_search_pages_to_the_databases_count():
    f = _Fake()
    pm, pm_meta = g.pubmed_ids(f.get_raw, "q")
    ep, ep_meta = g.europepmc_ids(f.get_raw, "q")
    assert len(pm) == 1234 and pm_meta["count"] == 1234 and pm_meta["state"] == "COMPLETE"
    assert len(ep) == 2345 and ep_meta["count"] == 2345 and ep_meta["state"] == "COMPLETE"


def test_a_short_search_is_written_truncated():
    f = _Fake()
    pm, meta = g.pubmed_ids(f.get_raw, "q", cap=500)
    assert len(pm) == 500 and meta["state"] == "TRUNCATED" and meta["count"] == 1234
