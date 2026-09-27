"""V1.0.1 non-PubMed retrieval route (harness/journal_route.py). Fixture: Sarzaeem 2014, Tehran Univ Med J 72:147-154,
retrieved from the journal's own page; its counts stay RECONSTRUCTED (not pooled) until the full report is held."""
import copy, json, os

import pytest

from harness import journal_route as jr, screen, trial_family

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "colchicine-postop-af"
RAW = json.load(open(os.path.join(ROOT, "cache", SLUG, "journal_records.json"), encoding="utf-8"))


def test_fixture_loads_with_every_field_located_in_the_held_page():
    rec = jr.load(ROOT, SLUG)[0]
    assert rec["id"] == "JOURNAL:tehranunivmedj:2014:72:147" and rec["id_type"] == "journal"
    res = jr.reconstructed(rec)
    assert (res["intervention"]["events"], res["intervention"]["n"]) == (16, 108)
    assert (res["comparator"]["events"], res["comparator"]["n"]) == (33, 108)


@pytest.mark.parametrize("mutate,why", [
    (lambda r: r["held"].__setitem__("document_sha256", "0" * 64), "hash mismatch"),
    (lambda r: r.__setitem__("abstract", r["abstract"] + " invented sentence."), "not printed"),
    (lambda r: r["result"]["intervention"].__setitem__("events", 17), "round-trip"),
    (lambda r: r["result"].__setitem__("full_report_held", True), "full_report_held false"),
    (lambda r: r.__setitem__("volume", 73), "derived from journal"),
])
def test_PLANT_a_bad_journal_record_is_refused(mutate, why):
    r = copy.deepcopy(RAW[0])
    mutate(r)
    with pytest.raises(jr.JournalRecordRefused, match=why):
        jr.validate(r, ROOT)


def test_journal_record_is_screened_on_its_own_text_and_forms_a_family():
    rec = jr.load(ROOT, SLUG)[0]
    assert screen._is_rct(rec)       # 'by using a table of random numbers are divided into ... groups'
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    assert screen.run([rec], cfg)["decisions"][0]["decision"] == "include"
    node = trial_family.families([rec], config=cfg)[0]
    assert node["aliases"]["bib_keys"] == ["bib:tehranunivmedj:2014:72:147"]
    assert [r["role"] for r in node["reports"]] == ["PRIMARY"]


def test_PLANT_quasi_random_journal_record_is_not_an_rct():
    rec = dict(jr.load(ROOT, SLUG)[0])
    rec["abstract"] = rec["abstract"].replace("by using a table of random numbers", "by alternate allocation")
    assert not screen._is_rct(rec)


def test_served_page_shows_reconstructed_not_pooled_and_the_pool_is_unchanged():
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "review.json"), encoding="utf-8"))
    prim = next(o for o in rev["outcomes"] if o.get("primary"))
    assert "JOURNAL:tehranunivmedj:2014:72:147" not in [t.get("id") for t in prim["trials"]]
    row = next(a for a in prim["declared_absent_trials"] if a.get("id") == "JOURNAL:tehranunivmedj:2014:72:147")
    assert row["state"] == "RECONSTRUCTED_NOT_POOLED"
    assert row["reconstructed"]["intervention"]["events"] == 16 and row["reconstructed"]["comparator"]["events"] == 33
    html = open(os.path.join(ROOT, "docs", "reviews", SLUG, "index.html"), encoding="utf-8").read()
    assert "RECONSTRUCTED" in html and "16/108 vs 33/108" in html


def test_PLANT_icap_named_by_acronym_and_by_article_is_one_family():
    from harness import trial_family
    rec = {"id": "1", "id_type": "pmid", "title": "t", "abstract": "(Funded by X; ICAP ClinicalTrials.gov number, NCT00128453.)",
           "nct": "NCT00128453", "pubtypes": ["Randomized Controlled Trial"]}
    assert trial_family.trailer_acronyms([rec], ["NCT00128453"]) == {"ICAP"}
    assert trial_family.trailer_acronyms([rec], ["NCT09999999"]) == set()      # another trial's registration binds nothing
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", "colchicine-recurrent-pericarditis", "review.json"), encoding="utf-8"))
    rows = next(o for o in rev["outcomes"] if o.get("primary"))["known_missing_sensitivity"]["rows"]
    icap = [r for r in rows if r.get("family_id") == "NCT00128453"]
    assert len(icap) == 1 and "ICAP" in icap[0].get("also_named", [])
    assert not [r for r in rows if r.get("trial_key") == "ICAP"]
