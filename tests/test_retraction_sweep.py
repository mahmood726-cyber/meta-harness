"""Retraction sweep + gate (captain dispatch review 27-A). No network: held fixtures + a stub fetcher.

Plants:
  1. Kazerooni PMID 19552904 reads RETRACTED (notice PMID 42781833) from a held, trimmed real PubMed efetch.
  2. A served pool row that is retracted makes the gate REFUSE (pure function AND the --check path over a tree);
     the same PMID only screened/excluded is listed, not refused.
  3. A fetch failure never reads as NONE_FOUND (PubMed down, PMID not returned, Crossref down).
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scripts import retraction_sweep as rs  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "retraction")
KAZ_XML = os.path.join(FIX, "pubmed_19552904_trimmed.xml")
KAZ_CR = os.path.join(FIX, "crossref_10.1016_j.ijgo.2009.04.022_trimmed.json")
KAZ, KAZ_NOTICE, KAZ_DOI = "19552904", "42781833", "10.1016/j.ijgo.2009.04.022"

# a SYNTHETIC clean control (PMID 1 cannot collide with a live record): no notice of any kind
CLEAN_XML = (b'<?xml version="1.0" ?><PubmedArticleSet><PubmedArticle><MedlineCitation><PMID Version="1">1</PMID>'
             b'<Article><PublicationTypeList><PublicationType>Journal Article</PublicationType>'
             b'<PublicationType>Randomized Controlled Trial</PublicationType></PublicationTypeList></Article>'
             b'</MedlineCitation><PubmedData><ArticleIdList><ArticleId IdType="pubmed">1</ArticleId>'
             b'<ArticleId IdType="doi">10.9999/control.clean</ArticleId></ArticleIdList></PubmedData></PubmedArticle>'
             b'</PubmedArticleSet>')
CLEAN_CR = json.dumps({"message": {"DOI": "10.9999/control.clean", "relation": {}}}).encode()


def _read(p):
    with open(p, "rb") as f:
        return f.read()


class StubFetcher:
    """Serves held bytes by leg; a leg mapped to None fails like the network does (status None, error)."""

    def __init__(self, pubmed=None, crossref=None, pubmed_status=200, crossref_status=200):
        self.pubmed, self.crossref = pubmed, crossref
        self.pubmed_status, self.crossref_status = pubmed_status, crossref_status
        self.calls = []

    def get(self, leg, url, ext, headers=None):
        self.calls.append((leg, url))
        body = self.pubmed if leg == "pubmed" else self.crossref
        status = self.pubmed_status if leg == "pubmed" else self.crossref_status
        if body is None:
            status, body = None, b""
        err = None if status == 200 else ("URLError: stub network down" if status is None else f"HTTP {status}")
        return ({"leg": leg, "url": url, "status": status, "sha256": hashlib.sha256(body).hexdigest(),
                 "bytes": len(body), "fetched_utc": "2026-10-10T00:00:00Z", "raw_name": "stub", "error": err}, body)

    def save_index(self):
        pass


# ---- plant 1: Kazerooni ---------------------------------------------------------------------------------------
def test_PLANT_kazerooni_held_pubmed_xml_reads_RETRACTED_with_notice_pmid():
    parsed = rs.parse_pubmed(_read(KAZ_XML))
    assert KAZ in parsed
    assert parsed[KAZ]["doi"] == KAZ_DOI
    sig = parsed[KAZ]["signals"]
    assert any(s["type"] == "PublicationType:Retracted Publication" and s["state"] == rs.RETRACTED for s in sig)
    assert any(s["type"] == "CommentsCorrections:RetractionIn" and s["notice_pmid"] == KAZ_NOTICE for s in sig)
    state, reason = rs.classify(rs.LEG_OK, rs.LEG_OK, sig)
    assert (state, reason) == (rs.RETRACTED, None)


def test_PLANT_kazerooni_end_to_end_sweep_RETRACTED_from_both_legs():
    res, fetches = rs.run_sweep([KAZ], StubFetcher(pubmed=_read(KAZ_XML), crossref=_read(KAZ_CR)), log=lambda *_: None)
    r = res[KAZ]
    assert r["state"] == rs.RETRACTED
    assert r["notice_pmids"] == [KAZ_NOTICE]
    assert r["notice_dois"] == ["10.1002/ijgo.71389"]
    assert {s["source"] for s in r["signals"]} == {"pubmed", "crossref"}
    assert len(fetches) == 2 and all(f["sha256"] and f["url"] for f in fetches)


def test_PLANT_kazerooni_pubmed_alone_still_RETRACTED_when_crossref_is_down():
    res, _ = rs.run_sweep([KAZ], StubFetcher(pubmed=_read(KAZ_XML), crossref=None), log=lambda *_: None)
    assert res[KAZ]["state"] == rs.RETRACTED
    assert res[KAZ]["crossref_leg"] == rs.LEG_FAILED


def test_crossref_updated_by_retraction_alone_reads_RETRACTED():
    sig = rs.parse_crossref(_read(KAZ_CR))
    assert [s["state"] for s in sig] == [rs.RETRACTED]
    assert rs.classify(rs.LEG_OK, rs.LEG_OK, sig)[0] == rs.RETRACTED


def test_expression_of_concern_and_erratum_signals():
    xml = (b'<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>2</PMID><CommentsCorrectionsList>'
           b'<CommentsCorrections RefType="ExpressionOfConcernIn"><PMID>3</PMID></CommentsCorrections>'
           b'<CommentsCorrections RefType="ErratumIn"><PMID>4</PMID></CommentsCorrections>'
           b'</CommentsCorrectionsList></MedlineCitation></PubmedArticle></PubmedArticleSet>')
    sig = rs.parse_pubmed(xml)["2"]["signals"]
    assert rs.classify(rs.LEG_OK, rs.LEG_NO_DOI, sig)[0] == rs.EOC
    only_erratum = [s for s in sig if s["state"] == rs.CORRECTED]
    assert rs.classify(rs.LEG_OK, rs.LEG_NO_DOI, only_erratum)[0] == rs.CORRECTED


# ---- plant 2: the gate ----------------------------------------------------------------------------------------
def test_PLANT_gate_REFUSES_a_retracted_served_row_and_names_it():
    sweep = {KAZ: {"state": rs.RETRACTED, "notice_pmids": [KAZ_NOTICE]}, "1": {"state": rs.NONE_FOUND}}
    g = rs.retraction_gate(sweep, [(KAZ, "metformin-pcos-ovulation", rs.SERVED_POOL, "review.outcomes.trials.id"),
                                   ("1", "metformin-pcos-ovulation", rs.SERVED_POOL, "review.outcomes.trials.id")])
    assert g["verdict"] == "REFUSED"
    assert [(r["pmid"], r["topic"], r["notice_pmids"]) for r in g["refused"]] == [(KAZ, "metformin-pcos-ovulation", [KAZ_NOTICE])]


def test_gate_REFUSES_expression_of_concern_in_a_served_tracker_row():
    g = rs.retraction_gate({"5": {"state": rs.EOC}}, [("5", "t", rs.TRACKER_SERVED, "x")])
    assert g["verdict"] == "REFUSED"


def test_gate_passes_clean_and_corrected_served_rows():
    g = rs.retraction_gate({"1": {"state": rs.NONE_FOUND}, "6": {"state": rs.CORRECTED}},
                           [("1", "t", rs.SERVED_POOL, "x"), ("6", "t", rs.SERVED_POOL, "x")])
    assert g["verdict"] == "PASS"


def _tree(tmp_path, served_ids, screened_ids, sweep):
    rev = {"slug": "t", "outcomes": [{"trials": [{"id": f"PMID {p}"} for p in served_ids]}],
           "screening": {"records": [{"id": p, "id_type": "pmid", "decision": "exclude"} for p in screened_ids]},
           "trial_families": [], "comparator": {}}
    d = tmp_path / "docs" / "reviews" / "t"
    d.mkdir(parents=True)
    (d / "review.json").write_text(json.dumps(rev), encoding="utf-8")
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "retraction_sweep.json").write_text(json.dumps({"pmids": sweep}), encoding="utf-8")
    return str(tmp_path)


def test_PLANT_check_exits_1_when_a_served_row_is_retracted(tmp_path):
    root = _tree(tmp_path, [KAZ, "1"], [], {KAZ: {"state": rs.RETRACTED, "notice_pmids": [KAZ_NOTICE]},
                                            "1": {"state": rs.NONE_FOUND}})
    lines = []
    assert rs.check(root, out=lines.append) == 1
    assert any(ln.startswith("REFUSED RETRACTED PMID 19552904 served in t") and KAZ_NOTICE in ln for ln in lines)


def test_check_does_not_refuse_a_retracted_pmid_that_is_only_screened_out(tmp_path):
    root = _tree(tmp_path, ["1"], [KAZ], {KAZ: {"state": rs.RETRACTED}, "1": {"state": rs.NONE_FOUND}})
    assert rs.check(root, out=lambda *_: None) == 0
    c, _ = rs.collect(root)
    assert (KAZ, "t", "screening_record", "review.screening.records.id") in c.occurrences()


# ---- plant 3: a failure is never clean -------------------------------------------------------------------------
def test_PLANT_pubmed_fetch_failure_is_NOT_CHECKED_never_NONE_FOUND():
    res, _ = rs.run_sweep(["1"], StubFetcher(pubmed=None, crossref=CLEAN_CR), log=lambda *_: None)
    assert res["1"]["state"] == rs.NOT_CHECKED
    assert res["1"]["reason"] == "PUBMED_FETCH_FAILED"
    assert res["1"]["state"] != rs.NONE_FOUND


def test_PLANT_pmid_missing_from_a_200_efetch_is_NOT_CHECKED():
    res, _ = rs.run_sweep(["1", "7"], StubFetcher(pubmed=CLEAN_XML, crossref=CLEAN_CR), log=lambda *_: None)
    assert res["7"]["state"] == rs.NOT_CHECKED and res["7"]["reason"] == "PUBMED_NOT_RETURNED"
    assert res["1"]["state"] == rs.NONE_FOUND


def test_PLANT_crossref_failure_with_clean_pubmed_is_NOT_CHECKED():
    res, _ = rs.run_sweep(["1"], StubFetcher(pubmed=CLEAN_XML, crossref=None), log=lambda *_: None)
    assert res["1"]["state"] == rs.NOT_CHECKED and res["1"]["reason"] == "CROSSREF_FETCH_FAILED"
    res, _ = rs.run_sweep(["1"], StubFetcher(pubmed=CLEAN_XML, crossref=b"<html>busy</html>", crossref_status=503),
                          log=lambda *_: None)
    assert res["1"]["state"] == rs.NOT_CHECKED


def test_unparseable_efetch_body_is_NOT_CHECKED():
    res, _ = rs.run_sweep(["1"], StubFetcher(pubmed=b"<html>Service unavailable", crossref=CLEAN_CR), log=lambda *_: None)
    assert res["1"]["state"] == rs.NOT_CHECKED


def test_none_found_only_when_both_legs_checked():
    assert rs.classify(rs.LEG_OK, rs.LEG_OK, []) == (rs.NONE_FOUND, None)
    assert rs.classify(rs.LEG_OK, rs.LEG_NO_DOI, []) == (rs.NONE_FOUND, None)
    assert rs.classify(rs.LEG_OK, rs.LEG_NOT_RUN, [])[0] == rs.NOT_CHECKED
    assert rs.classify(rs.LEG_FAILED, rs.LEG_NO_DOI, [])[0] == rs.NOT_CHECKED


def test_gate_UNVERIFIED_and_check_exit_2_when_a_served_pmid_was_not_checked(tmp_path):
    g = rs.retraction_gate({"1": {"state": rs.NOT_CHECKED, "reason": "PUBMED_FETCH_FAILED"}},
                           [("1", "t", rs.SERVED_POOL, "x"), ("8", "t", rs.SERVED_POOL, "x")])
    assert g["verdict"] == "UNVERIFIED" and {u["pmid"] for u in g["unverified"]} == {"1", "8"}
    root = _tree(tmp_path, ["1"], [], {"1": {"state": rs.NOT_CHECKED, "reason": "PUBMED_FETCH_FAILED"}})
    assert rs.check(root, out=lambda *_: None) == 2


def test_check_could_not_execute_without_registry(tmp_path):
    (tmp_path / "docs" / "reviews").mkdir(parents=True)
    assert rs.check(str(tmp_path), out=lambda *_: None) == 2


# ---- the committed sweep ---------------------------------------------------------------------------------------
def test_committed_sweep_reads_kazerooni_RETRACTED_and_holds_hashes():
    reg = json.load(open(os.path.join(ROOT, "registry", "retraction_sweep.json"), encoding="utf-8"))
    rec = reg["pmids"][KAZ]
    assert rec["state"] == rs.RETRACTED and KAZ_NOTICE in rec["notice_pmids"]
    f = reg["fetches"][rec["pubmed_fetch"]]
    assert f["status"] == 200 and len(f["sha256"]) == 64 and f["fetched_utc"].endswith("Z") and "19552904" in f["url"]
    assert all(e["state"] in rs.STATES for e in reg["pmids"].values())
    # NONE_FOUND never sits on a failed leg
    for e in reg["pmids"].values():
        if e["state"] == rs.NONE_FOUND:
            assert e["pubmed_leg"] == rs.LEG_OK and e["crossref_leg"] in (rs.LEG_OK, rs.LEG_NO_DOI, rs.LEG_NOT_IN_CROSSREF)


# ---- a record that IS a notice is not itself "retracted" -------------------------------------------------------
def test_a_retraction_notice_record_is_flagged_is_notice_not_RETRACTED_and_refused_if_served():
    notice_cr = json.dumps({"message": {"DOI": "10.9999/notice", "update-to": [
        {"DOI": "10.9999/original", "type": "retraction", "source": "publisher"}]}}).encode()
    res, _ = rs.run_sweep(["1"], StubFetcher(pubmed=CLEAN_XML, crossref=notice_cr), log=lambda *_: None)
    r = res["1"]
    assert r["state"] == rs.NONE_FOUND
    assert r["is_notice"] == [rs.RETRACTED] and r["notice_for_dois"] == ["10.9999/original"]
    assert r["notice_dois"] == []
    g = rs.retraction_gate({"1": r}, [("1", "t", rs.SERVED_POOL, "x")])
    assert g["verdict"] == "REFUSED" and g["refused"][0]["state"] == "IS_NOTICE:RETRACTED"
