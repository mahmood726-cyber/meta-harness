"""PMC serves only front matter when 'The publisher of this article does not allow downloading of the full text in XML
form.' (JAMA's COVID-19 corticosteroid trials, CoDEX PMC7489411 among 24 index entries): that is a final state, not a
transient FETCH_EMPTY to retry -- and never a reason to scrape the article page."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import fetch  # noqa: E402

XML = ('<?xml version="1.0"  ?><pmc-articleset><article><!--The publisher of this article does not allow downloading of '
       'the full text in XML form.--><front><article-meta><title-group><article-title>CoDEX</article-title>'
       '</title-group></article-meta></front></article></pmc-articleset>')


def test_the_publishers_refusal_is_recorded(monkeypatch):
    monkeypatch.setattr(fetch, "_resolve_pmcid", lambda pmid: "PMC7489411")
    monkeypatch.setattr(fetch.http, "get_text", lambda *a, **k: XML)
    monkeypatch.setattr(fetch.time, "sleep", lambda s: None)
    fetch.LAST_PMC_STATE.clear()
    assert fetch._pmc_fulltext("32876695") == ""
    assert fetch.LAST_PMC_STATE["32876695"] == "PUBLISHER_DISALLOWS_XML"
