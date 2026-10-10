"""R8-4: 'why is our trial absent from the comparator' is decided by the comparator's SEARCH END date against the
trial's first public date, never by years. Chen 2023 (esketamine) was published in March 2023, after a December 2022
search end, and was labelled NOT_EXPLAINED_BY_DATE because 2023 == 2023. Synthetic texts; dates typed by regex."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import r8_4_search_dates as r  # noqa: E402

END_DEC22 = {"date": "2022-12", "precision": "month"}


def test_PLANT_publication_after_a_december_search_end_in_the_same_year_is_explained():
    assert r.classify("2023-03-01", END_DEC22, "2023-06-26") == "AFTER_COMPARATOR_SEARCH_END"
    assert r.classify("2022-11-30", END_DEC22, "2023-06-26") == "NOT_EXPLAINED_BY_DATE"
    assert r.classify("2022-12-15", END_DEC22, "2023-06-26") == "SAME_PERIOD_AS_SEARCH_END"
    # the MONTH decides within a year: a September report is after a June search end of the same year
    assert r.classify("2022-09-01", {"date": "2022-06", "precision": "month"}, "2023-01-01") == "AFTER_COMPARATOR_SEARCH_END"


def test_PLANT_year_precision_search_end_leaves_the_same_year_undetermined():
    end = {"date": "2015", "precision": "year"}
    assert r.classify("2015-09-16", end, None) == "SAME_PERIOD_AS_SEARCH_END"
    assert r.classify("2016-01-02", end, None) == "AFTER_COMPARATOR_SEARCH_END"


def test_PLANT_no_search_end_never_decides_on_a_year():
    assert r.classify("2022-03-01", None, "2022-06-09") == "SEARCH_END_NOT_STATED"
    assert r.classify("2022-07-01", None, "2022-06-09") == "PUBLISHED_AFTER_COMPARATOR"
    assert r.classify(None, END_DEC22, None) == "TRIAL_DATE_NOT_RECORDED"


def test_PLANT_search_end_is_typed_from_search_sentences_in_its_formats():
    assert r.search_end("The search in these databases was carried out until December 2022.")["date"] == "2022-12"
    assert r.search_end("We searched PubMed and Embase up to June 30, 2021, for trials.")["date"] == "2021-06"
    assert r.search_end("Searched PubMed (1 Jan 1987-10 Sep 2024) for trials.")["date"] == "2024-09"
    assert r.search_end("We searched electronic databases up to 02.02.2021 for RCTs.")["date"] == "2021-02"
    assert r.search_end("We searched PubMed and ClinicalTrials.gov for RCTs published before 2022.4.20.")["date"] == "2022-04"
    e = r.search_end("A search of PubMed and CENTRAL was conducted for RCTs during 2007 to 2015.")
    assert e["date"] == "2015" and e["precision"] == "year"


def test_PLANT_dates_outside_search_sentences_or_without_a_connector_are_not_the_search_end():
    assert r.search_end("Patients were enrolled until March 2019. Follow-up lasted to June 2020.") is None
    assert r.search_end("The protocol was registered in PROSPERO in May 2021.") is None
    # the registration clause is skipped, the search clause in the SAME sentence is not
    assert r.search_end("The protocol was registered in PROSPERO in May 2021 and databases were searched up to April "
                        "2021.")["date"] == "2021-04"
    assert r.search_end("We searched MEDLINE for trials that enrolled patients until March 2023, up to January "
                        "2022.")["date"] == "2022-01"
    # ambiguous D.M.Y (03.04.2021): only the year is typed
    e = r.search_end("We searched MEDLINE up to 03.04.2021.")
    assert e["date"] == "2021" and e["precision"] == "year"


def test_PLANT_a_topic_level_fulltext_is_never_read_as_the_comparators(tmp_path, monkeypatch):
    # cache/<slug>/comparator_fulltext.txt can be another comparator's text (esketamine: a review searching to
    # December 2025): only cache/comparators/<pmid>/ is the comparator's own
    monkeypatch.setattr(r, "ROOT", str(tmp_path))
    (tmp_path / "cache" / "slug").mkdir(parents=True)
    (tmp_path / "cache" / "slug" / "comparator_fulltext.txt").write_text("searched from inception to December 2025.")
    assert r.fulltext_for("123", "slug") == []


def test_PLANT_the_tracker_reads_the_typed_dates_for_THIS_comparator_only():
    import g1_tracker as gt
    dates = {"comparators": {"37377288": {"search_end": "2022-12", "precision": "month", "span": "until December 2022",
                                          "searched_trial_registry": False}},
             "trials": {"esk|PMID 1": {"comparator": "37377288", "first_public": "2023-03-01", "basis": "PubMed",
                                       "why_not_in_comparator": "AFTER_COMPARATOR_SEARCH_END",
                                       "why_by_publication_only": "AFTER_COMPARATOR_SEARCH_END"},
                        "esk|PMID 2": {"comparator": "99999999", "first_public": "2023-03-01", "basis": "PubMed",
                                       "why_not_in_comparator": "AFTER_COMPARATOR_SEARCH_END"}}}
    d = gt.extra_date_detail("esk", "37377288", ["PMID 1", "PMID 2", "PMID 3"], {"1": {"year": "2023"}}, dates)
    assert d[0]["why_not_in_comparator"] == "AFTER_COMPARATOR_SEARCH_END" and d[0]["comparator_search_end"] == "2022-12"
    # recorded against a different (earlier) comparator, or not recorded: never inferred from a year
    assert d[1]["why_not_in_comparator"] == "DATES_NOT_RECORDED"
    assert d[2]["why_not_in_comparator"] == "DATES_NOT_RECORDED"
    assert not any(x["why_not_in_comparator"] in ("PUBLISHED_AFTER_COMPARATOR", "NOT_EXPLAINED_BY_DATE") for x in d)


def test_PLANT_r1_a_later_search_update_stated_by_year_outranks_an_earlier_month():
    e = r.search_end("PubMed was searched through December 2020. Searches were updated from inception to 2022.")
    assert e["date"] == "2022" and r.classify("2022-06-01", e, None) == "SAME_PERIOD_AS_SEARCH_END"


def test_PLANT_r1_publication_and_enrolment_clauses_never_supply_the_search_end():
    assert r.search_end("PubMed was searched through December 2020, and the review was published in March "
                        "2022.")["date"] == "2020-12"
    assert r.search_end("PubMed was searched and patients were enrolled from 2018 to 2022.") is None


def test_PLANT_r1_a_negated_registry_is_not_searched():
    assert r.searched_registry(["We searched PubMed through December 2020. We did not search ClinicalTrials.gov."]) is None
    assert "ClinicalTrials.gov" in r.searched_registry(["We searched PubMed and ClinicalTrials.gov through December 2020."])


def test_PLANT_r1_a_missing_aact_snapshot_fails_closed(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        r.results_posted({"NCT01"}, snap=str(tmp_path))
    assert r.results_posted(set(), snap=str(tmp_path)) == {}


def test_PLANT_r1_a_year_only_issue_date_before_the_indexing_date_is_first_public():
    xml = ("<PubmedArticleSet><PubmedArticle><MedlineCitation><Article><Journal><JournalIssue><PubDate><Year>2020</Year>"
           "</PubDate></JournalIssue></Journal></Article></MedlineCitation><PubmedData><History>"
           "<PubMedPubDate PubStatus=\"entrez\"><Year>2021</Year><Month>2</Month><Day>1</Day></PubMedPubDate>"
           "</History></PubmedData></PubmedArticle></PubmedArticleSet>")
    d = r.pubmed_dates(xml)
    assert d["first_public"] == "2020"
    assert r.classify(d["first_public"], {"date": "2020-12", "precision": "month"}, None) == "SAME_PERIOD_AS_SEARCH_END"


def test_PLANT_r2_a_bare_in_date_is_not_a_search_end():
    assert r.search_end("We searched PubMed through December 2020 and included studies published in March "
                        "2022.")["date"] == "2020-12"


def test_PLANT_r2_registry_negation_and_prospero():
    assert r.searched_registry(["We searched PubMed but did not search trial registries, including "
                                "ClinicalTrials.gov."]) is None
    assert r.searched_registry(["We searched PubMed and registered the review in the PROSPERO registry."]) is None


def test_PLANT_r2_a_year_only_publication_date_sharing_the_indexing_year_keeps_year_precision():
    xml = ("<PubmedArticleSet><PubmedArticle><MedlineCitation><Article><Journal><JournalIssue><PubDate><Year>2020</Year>"
           "</PubDate></JournalIssue></Journal></Article></MedlineCitation><PubmedData><History>"
           "<PubMedPubDate PubStatus=\"entrez\"><Year>2020</Year><Month>12</Month><Day>01</Day></PubMedPubDate>"
           "</History></PubmedData></PubmedArticle></PubmedArticleSet>")
    d = r.pubmed_dates(xml)
    assert d["first_public"] == "2020"
    assert r.classify(d["first_public"], {"date": "2020-06", "precision": "month"}, None) == "SAME_PERIOD_AS_SEARCH_END"


def test_PLANT_r2_an_nct_absent_from_the_snapshot_is_unchecked_not_unposted(tmp_path):
    (tmp_path / "studies.txt").write_text("nct_id|results_first_posted_date\nNCT01|\nNCT02|2020-01-02\n", encoding="utf-8")
    got = r.results_posted({"NCT01", "NCT02", "NCT03"}, snap=str(tmp_path))
    assert got == {"NCT01": "", "NCT02": "2020-01-02"} and "NCT03" not in got


def test_PLANT_r2_unavailable_evidence_is_never_a_verdict(monkeypatch, tmp_path):
    monkeypatch.setattr(r, "targets", lambda: [("topic", "1", ["PMID 2", "PMID 3"]), ("topic2", "4", ["PMID 5"])])
    monkeypatch.setattr(r, "ROOT", str(tmp_path))
    for s, recs in (("topic", [{"id": "2", "nct": "NCT09"}, {"id": "3"}]), ("topic2", [{"id": "5"}])):
        (tmp_path / "cache" / s).mkdir(parents=True)
        (tmp_path / "cache" / s / "records.json").write_text(json.dumps({"records": recs}), encoding="utf-8")
    pms = {"4": {"first_public": "2022-01", "basis": "x", "abstract": "We searched PubMed and ClinicalTrials.gov "
                 "until December 2020."},
           "2": {"first_public": "2023-03", "basis": "x", "abstract": ""},
           "3": {"first_public": "2023-03", "basis": "x", "abstract": ""},
           "5": {"first_public": "2023-03", "basis": "x", "abstract": ""}}
    monkeypatch.setattr(r, "_pm", lambda p: pms.get(p))
    monkeypatch.setattr(r, "fulltext_for", lambda *a: [])
    monkeypatch.setattr(r, "results_posted", lambda ncts, snap=None: {})
    out = r.build()["trials"]
    # comparator 1 has no PubMed record and no full text: nothing was inspected
    assert out["topic|PMID 2"]["why_not_in_comparator"] == "COMPARATOR_TEXT_UNAVAILABLE"
    assert out["topic|PMID 3"]["why_not_in_comparator"] == "COMPARATOR_TEXT_UNAVAILABLE"
    assert out["topic2|PMID 5"]["why_not_in_comparator"] == "AFTER_COMPARATOR_SEARCH_END"


def test_PLANT_r3_negated_searching_voids_the_sentence_but_no_restrictions_does_not():
    assert r.searched_registry(["ClinicalTrials.gov was not searched."]) is None
    assert r.searched_registry(["ClinicalTrials.gov supplied trial identifiers."]) is None
    assert r.search_end("PubMed was not searched through December 2022.") is None
    assert r.search_end("We searched PubMed with no language restrictions up to May 2021.")["date"] == "2021-05"
    assert r.searched_registry(["We searched PubMed and ClinicalTrials.gov with no language restrictions."])


def test_PLANT_r3_an_active_voice_submission_is_not_the_search_end():
    assert r.search_end("We searched PubMed through March 2021 and submitted the manuscript on 1 December "
                        "2023.")["date"] == "2021-03"


def test_PLANT_r3_an_empty_abstract_is_no_comparator_text(monkeypatch, tmp_path):
    monkeypatch.setattr(r, "targets", lambda: [("s", "2", ["PMID 1"])])
    monkeypatch.setattr(r, "ROOT", str(tmp_path))
    (tmp_path / "cache" / "s").mkdir(parents=True)
    (tmp_path / "cache" / "s" / "records.json").write_text(json.dumps({"records": []}), encoding="utf-8")
    monkeypatch.setattr(r, "_pm", lambda p: {"first_public": "2020-01" if p == "2" else "2023-03", "basis": "x",
                                             "abstract": "   "})
    monkeypatch.setattr(r, "fulltext_for", lambda *a: [])
    monkeypatch.setattr(r, "results_posted", lambda ncts, snap=None: {})
    assert r.build()["trials"]["s|PMID 1"]["why_not_in_comparator"] == "COMPARATOR_TEXT_UNAVAILABLE"


def test_PLANT_r3_a_reference_list_access_date_is_not_a_search_end():
    # 29795629's own reference list: a URL hyphen read as 'to' gave 2017-11 instead of its July 2016 search end
    text = ("We searched PubMed (including MEDLINE) and Scopus (including Embase) databases and Cochrane libraries for "
            "randomized trials published from inception of the databases through July 2016. Retrieved from "
            "http://handbook-5-1.cochrane.org/ Accessed November 7, 2017. 34 Holst")
    assert r.search_end(text)["date"] == "2016-07"
