"""Plant (E1 re-acquisition, 11 Oct): verbatim EFetch acquisition of a NAMED subset of a topic's records (the records an
absence claim rests on, and the abridged-abstract census list), append-only, with the subset stated in the manifest."""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import acquire_bundle_evidence as abe  # noqa: E402


class _Resp(io.BytesIO):
    status = 200

    def __init__(self, pmid):
        body = (f"<?xml version='1.0' encoding='UTF-8'?><PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>{pmid}"
                "</PMID></MedlineCitation></PubmedArticle></PubmedArticleSet>").encode("utf-8")
        super().__init__(body)
        self.headers = {"Content-Length": str(len(body)), "Content-Type": "application/xml"}
        self._url = f"https://eutils.example/{pmid}"

    def geturl(self):
        return self._url

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_PLANT_acquires_only_the_named_records_and_says_so(tmp_path, monkeypatch):
    (tmp_path / "cache" / "t").mkdir(parents=True)
    (tmp_path / "cache" / "t" / "records.json").write_text(json.dumps(
        {"records": [{"id": "111", "id_type": "pmid"}, {"id": "222", "id_type": "pmid"}, {"id": "333", "id_type": "pmid"}],
         "fetched_utc": "2026-09-11"}), encoding="utf-8")
    monkeypatch.setattr(abe, "ROOT", tmp_path)
    monkeypatch.setattr(abe.time, "sleep", lambda s: None)
    asked = []
    monkeypatch.setattr(abe.urllib.request, "urlopen",
                        lambda req, timeout=0: asked.append(req.full_url) or _Resp(req.full_url.split("id=")[1].split("&")[0]))
    out = abe.acquire_pubmed("t", pmids=["222", "999"], scope="records an absence claim rests on")
    man = json.loads((out / "ACQUISITION.json").read_text(encoding="utf-8"))
    assert [e["identifier"]["pmid"] for e in man["entries"]] == ["222"]          # 999 is not this topic's record
    assert man["scope"]["subset"] == ["222"] and man["scope"]["not_in_topic_records"] == ["999"]
    assert man["scope"]["why"] == "records an absence claim rests on" and len(asked) == 1
