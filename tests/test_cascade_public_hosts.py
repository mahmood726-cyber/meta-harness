"""The cascade follows URLs that REMOTE metadata hands it (Unpaywall locations, a repository page's citation_pdf_url).
Seen in a Codex acquisition lane, 2026-09-27: a DSpace repository advertised citation_pdf_url
http://localhost:4000/bitstreams/... and the cascade requested it. A URL from remote metadata may never reach a
loopback, private, link-local or non-http(s) address -- neither directly nor by redirect. Refused before any socket
opens, and recorded as REFUSED_NONPUBLIC_HOST."""
import urllib.request

import pytest

from scripts import acquisition_cascade as ac


@pytest.mark.parametrize("url", ["http://localhost:4000/bitstreams/x/download", "http://127.0.0.1/a.pdf",
                                 "http://[::1]/a.pdf", "http://10.0.0.5/a.pdf", "http://192.168.1.2/a.pdf",
                                 "http://169.254.169.254/latest/meta-data", "file:///C:/Windows/win.ini",
                                 "ftp://example.org/a.pdf", "http://printer.local/a.pdf"])
def test_non_public_urls_are_refused_without_a_request(url, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("a request was opened")
    monkeypatch.setattr(ac, "_open", boom)
    assert ac._get(url) == ("REFUSED_NONPUBLIC_HOST", b"")


def test_a_redirect_to_a_non_public_host_is_refused():
    h = ac._PublicOnlyRedirect()
    req = urllib.request.Request("https://repository.example.org/handle/1")
    with pytest.raises(ac.NonPublicHost):
        h.redirect_request(req, None, 302, "Found", {}, "http://localhost:4000/bitstreams/x")


def test_public_hosts_pass_the_check():
    assert ac._public_url("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=x")
    assert ac._public_url("https://publicatio.bibl.u-szeged.hu/27237/1/Rosenstock.pdf")


def test_a_screening_target_holds_the_registration_without_posted_results(tmp_path, monkeypatch):
    """FIVE-STAR / CONFIDENCE: no posted results, but the registration is the evidence of a screening gap. Only a
    target that asks for it (hold_registration) holds it; the default still holds posted results only."""
    import json as _j
    held = {}
    monkeypatch.setattr(ac, "_get", lambda url, accept=None: (200, _j.dumps({"hasResults": False, "protocolSection": {}}).encode()))
    monkeypatch.setattr(ac, "_record", lambda *a, **k: None)
    monkeypatch.setattr(ac, "_hold", lambda rel, body, meta: held.setdefault(rel, meta))
    ac.route_registry({"trial": "X", "nct": "NCT05887817"})
    assert held == {}
    ac.route_registry({"trial": "X", "nct": "NCT05887817", "hold_registration": True})
    assert list(held) == ["X/NCT05887817.json"] and "registration record" in held["X/NCT05887817.json"]["what"]
