"""Synthetic-only acquisition contracts; urllib is intercepted for every test."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
from unittest.mock import Mock
import urllib.error

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import reacquire_stub_fulltexts as r


def jats(lic="by", body="<body><p>Synthetic article body.</p></body>", pmid="123", extra=""):
    return (f'<?xml version="1.0" encoding="UTF-8"?><article><front><article-meta>'
            f'<article-id pub-id-type="pmid">{pmid}</article-id>'
            '<article-id pub-id-type="pmc">PMC456</article-id>'
            f'<permissions><license><ext-link href="https://creativecommons.org/licenses/{lic}/4.0/">'
            f'Creative Commons</ext-link></license></permissions>{extra}'
            f'</article-meta></front>{body}</article>').encode()


REGISTRY = {"documents": [{"slug": "synthetic", "path": "held.xml", "pmid": "123", "label": "STUB"}]}
SEARCH = json.dumps({"resultList": {"result": [{"id": "123", "source": "MED", "pmcid": "PMC456",
                                               "isOpenAccess": "Y", "license": "cc-by"}]}}).encode()
OA_NONE = b'<OA><error code="idIsNotOpenAccess">No package</error></OA>'


class Response(io.BytesIO):
    def __init__(self, raw, code=200, headers=None, url=None):
        super().__init__(raw)
        self.code, self.headers, self.url = code, headers or {"Content-Type": "application/xml"}, url

    def geturl(self):
        return self.url


@pytest.fixture
def network(monkeypatch):
    queue, calls, sleeps = [], [], []

    def open_request(req, timeout):
        calls.append(req.full_url)
        assert queue, "unexpected HTTP request"
        response = queue.pop(0)
        if isinstance(response, Exception):
            raise response
        response.url = response.url or req.full_url
        return response

    opener = Mock(open=open_request)
    monkeypatch.setattr(r.urllib.request, "build_opener", lambda *a: opener)
    monkeypatch.setattr(r.urllib.request, "urlopen", lambda *a, **kw: pytest.fail("unmocked urllib call"))
    monkeypatch.setattr(r.time, "sleep", sleeps.append)
    monkeypatch.setattr(r.time, "monotonic", lambda: 100.0)
    return queue, calls, sleeps


def execute(tmp_path, network, raw, **kwargs):
    network[0].extend([Response(SEARCH), Response(raw, **kwargs), Response(OA_NONE)])
    entries = r.run(REGISTRY, tmp_path, date="2026-10-14")
    manifest = json.loads((tmp_path / "synthetic/fulltext_2026-10-14/manifest.json").read_text())
    assert entries == manifest["entries"]
    return entries[0]


def test_cc_by_fulltext_stored_with_provenance(tmp_path, network):
    raw = jats()
    entry = execute(tmp_path, network, raw, headers={"Content-Type": "application/xml", "Content-Length": str(len(raw))})
    assert (tmp_path / "synthetic/fulltext_2026-10-14/123.xml").read_bytes() == raw
    assert entry["stored"] and len(network[1]) == 2
    meta = entry["attempts"][-1]
    assert meta["licence"] == "CC" and meta["label"] == "FULLTEXT"
    assert meta["sha256"] == hashlib.sha256(raw).hexdigest()
    assert meta["requested_url"] == meta["final_url"] and meta["http_status"] == 200
    assert meta["declared_encoding"] == "UTF-8" and not meta["truncated"]
    assert meta["acquired_utc"]["start"] and meta["content_type"] == "application/xml"
    assert network[2] == [0.5]


@pytest.mark.parametrize("license", ["by-nc", "by-nd", "by-sa"])
def test_restricted_never_stored(tmp_path, network, license):
    entry = execute(tmp_path, network, jats(license))
    assert not entry["stored"]
    assert entry["attempts"][1]["licence"] == "CC_RESTRICTED"
    assert not list(tmp_path.rglob("*.xml"))


@pytest.mark.parametrize("raw,label", [(jats(body=""), "STUB"),
    (b'<article>publisher does not allow downloading of the full text</article>', "STUB"),
    (b'<html><title>500 Server Error</title></html>', "STUB")])
def test_stub_and_html_never_stored(tmp_path, network, raw, label):
    entry = execute(tmp_path, network, raw)
    assert not entry["stored"] and entry["attempts"][1]["label"] == label
    assert not list(tmp_path.rglob("*.xml"))


def test_append_only_different_bytes_refused(tmp_path, network):
    path = tmp_path / "synthetic/fulltext_2026-10-14/123.xml"
    r._write_once(path, b"existing")
    with pytest.raises(ValueError, match="immutable acquisition differs"):
        execute(tmp_path, network, jats())
    assert path.read_bytes() == b"existing"
    r._write_once(path, b"existing")


def test_existing_manifest_refused_before_network(tmp_path, network):
    execute(tmp_path, network, jats())
    calls = len(network[1])
    with pytest.raises(ValueError, match="dated manifest"):
        r.run(REGISTRY, tmp_path, date="2026-10-14")
    assert len(network[1]) == calls


def test_429_then_success(tmp_path, network):
    error = urllib.error.HTTPError(r.EPMC + "PMC456/fullTextXML", 429, "rate", {}, io.BytesIO(b"slow down"))
    network[0].extend([Response(SEARCH), error, Response(jats())])
    entry = r.run(REGISTRY, tmp_path)[0]
    assert entry["stored"] and len(network[1]) == 3
    assert entry["attempts"][1]["http_status"] == 429
    assert entry["attempts"][2]["attempt"] == 2
    assert 1 in network[2] and all(s >= 0.5 for s in network[2])


@pytest.mark.parametrize("status", [429, 500, 503])
def test_retry_budget(tmp_path, network, status):
    network[0].extend([Response(b"unavailable", status) for _ in range(3)])
    entry = r.run(REGISTRY, tmp_path)[0]
    assert not entry["stored"] and len(network[1]) == 3
    assert [a["attempt"] for a in entry["attempts"]] == [1, 2, 3]


@pytest.mark.parametrize("status,raw", [(403, b"denied"), (200, b'<html>captcha challenge</html>')])
def test_denial_and_challenge_stop_without_route_around(tmp_path, network, status, raw):
    entry = execute(tmp_path, network, raw, code=status)
    assert not entry["stored"] and len(network[1]) == 2


def test_truncation_refused(tmp_path, network):
    entry = execute(tmp_path, network, jats(), headers={"Content-Length": "999999"})
    assert not entry["stored"] and entry["attempts"][1]["outcome"] == "TRUNCATED"
    assert not list(tmp_path.rglob("*.xml"))


def test_dry_run_no_writes_or_http(tmp_path, network, capsys):
    r.run(REGISTRY, tmp_path, dry_run=True)
    assert not list(tmp_path.iterdir()) and not network[1]
    assert "123" in capsys.readouterr().out


def test_filters_and_real_registry_shape():
    reg = {"documents": {"cache/topic/ft_123.txt": {"label": "STUB"},
                         "cache/comparators/456/body.txt": {"label": "METADATA"},
                         "cache/topic/comparator_fulltext.txt": {"label": "STUB"},
                         "cache/topic/ft_789.txt": {"label": "FULLTEXT"}}}
    assert len(r.selected(reg)) == 2
    assert r.selected(reg, "topic", {"123"})[0]["pmid"] == "123"
    assert not r.selected(reg, "topic", {"456"})


def test_unread_terms_manuscript_and_wrong_identifier(tmp_path, network):
    for i, raw in enumerate([jats().replace(b"creativecommons.org", b"example.org"),
                             jats(extra="<custom-meta>author manuscript NIHMS123</custom-meta>"),
                             jats(pmid="999")]):
        entry = execute(tmp_path / str(i), network, raw)
        assert not entry["stored"]
    assert not list(tmp_path.rglob("*.xml"))


def package(raw):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:gz") as archive:
        member = tarfile.TarInfo("../../unsafe-name.nxml")
        member.size = len(raw)
        archive.addfile(member, io.BytesIO(raw))
    return stream.getvalue()


def test_oa_fallback_package_checked_without_extracting_paths(tmp_path, network):
    oa = b'<OA><records><record id="PMC456"><link format="tgz" href="ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/test.tar.gz"/></record></records></OA>'
    network[0].extend([Response(SEARCH), Response(jats(body="")), Response(oa), Response(package(jats()))])
    entry = r.run(REGISTRY, tmp_path)[0]
    assert entry["stored"] and len(network[1]) == 4
    assert network[1][-1].startswith("https://ftp.ncbi.nlm.nih.gov/")
    assert entry["attempts"][-1]["sha256"] == hashlib.sha256(jats()).hexdigest()
    assert [p.name for p in tmp_path.rglob("*.xml")] == ["123.xml"]


def test_pmcid_only(tmp_path, network):
    network[0].append(Response(jats()))
    reg = {"documents": [{"slug": "synthetic", "path": "held.xml", "pmcid": "PMC456", "label": "METADATA"}]}
    assert r.run(reg, tmp_path)[0]["stored"]
    assert len(network[1]) == 1 and list(tmp_path.rglob("PMC456.xml"))


def test_search_identity_mismatch_fails_closed(tmp_path, network):
    network[0].append(Response(SEARCH.replace(b'"123"', b'"999"')))
    assert not r.run(REGISTRY, tmp_path)[0]["stored"]
    assert len(network[1]) == 1


def test_redirect_not_followed_and_host_allowlist():
    assert r.NoRedirect().redirect_request(None, None, 302, "", {}, "https://publisher.example") is None
    for url in ("https://publisher.example/x", "http://www.ebi.ac.uk/x", "https://www.ebi.ac.uk@evil.example/x"):
        assert not r.safe_url(url)


def test_network_error_not_retried(tmp_path, network):
    network[0].append(urllib.error.URLError("offline"))
    entry = r.run(REGISTRY, tmp_path)[0]
    assert not entry["stored"] and len(network[1]) == 1
    assert entry["attempts"][0]["error"] == "URLError"


def test_invalid_slug_refused():
    with pytest.raises(ValueError, match="slug"):
        r.selected({"documents": [{"slug": "../cache", "pmid": "123", "label": "STUB"}]})


@pytest.mark.parametrize("permission", ["publicdomain/zero/1.0/", "publicdomain/mark/1.0/"])
def test_cc0_public_domain_stored(tmp_path, network, permission):
    raw = jats().replace(b"licenses/by/4.0/", permission.encode())
    assert execute(tmp_path, network, raw)["stored"]


def test_malformed_fulltext_never_stored(tmp_path, network):
    entry = execute(tmp_path, network, jats().replace(b"</article>", b""))
    assert not entry["stored"]
    assert entry["attempts"][1]["outcome"] == "INVALID_XML"


def test_incomplete_read_captured_before_rejection(tmp_path, network):
    class Incomplete(Response):
        def read(self, *args):
            raise r.http.client.IncompleteRead(b"partial", 100)
    network[0].extend([Response(SEARCH), Incomplete(b""), Response(OA_NONE)])
    entry = r.run(REGISTRY, tmp_path)[0]
    meta = entry["attempts"][1]
    assert not entry["stored"] and meta["error"] == "INCOMPLETE_READ"
    assert meta["sha256"] == hashlib.sha256(b"partial").hexdigest()


def test_oa_link_cannot_target_publisher(tmp_path, network):
    oa = b'<OA><record id="PMC456"><link format="tgz" href="https://publisher.example/a.tgz"/></record></OA>'
    network[0].extend([Response(SEARCH), Response(jats(body="")), Response(oa)])
    entry = r.run(REGISTRY, tmp_path)[0]
    assert not entry["stored"] and entry["outcome"] == "NO_OA_PACKAGE"
    assert len(network[1]) == 3
