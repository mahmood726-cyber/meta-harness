"""V1.1 discovery recall test cases (antibiotics-vs-appendectomy-appendicitis): ASAA (PMID 30560527), COMMA (33534226),
the 2026 Sierra Leone trial (42251306) and the Talan 2017 US pilot (27974169) are randomised antibiotics-vs-appendectomy
trials that the registered title+journal+year reconstruction queries can never retrieve. Found by a concept query and a
blind codex screen of the held records, each call verified against its record (screen/VERIFIED.json).
Held run: evidence/discovery/antibiotics-vs-appendectomy-appendicitis/run/."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "evidence", "discovery", "antibiotics-vs-appendectomy-appendicitis")
CASES = ("30560527", "33534226", "42251306", "27974169")


def _fetch():
    return json.load(open(os.path.join(D, "run", "recall_fetch.json"), encoding="utf-8"))


def test_the_registered_queries_miss_every_recall_case_and_the_concept_query_finds_them():
    d = _fetch()
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    assert len(reg) == 6
    for pmid in CASES:
        assert pmid not in reg and pmid in d["broad_pmids"], pmid


def test_the_concept_query_also_retrieves_every_registered_report():
    d = _fetch()
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    assert reg <= set(d["broad_pmids"])


def test_every_recall_case_is_a_randomised_antibiotics_vs_surgery_record():
    recs = {str(r["id"]): r for r in _fetch()["broad_records"]}
    for pmid in CASES:
        r = recs[pmid]
        text = (r["title"] + " " + (r.get("abstract") or "")).lower()
        assert "randomi" in text and "appendicitis" in text, pmid
        assert "antibiotic" in text or "non-operative" in text, pmid


def test_every_blind_screen_quote_is_in_its_record_and_the_cases_were_verified():
    recs = {str(r["id"]): r for r in _fetch()["broad_records"]}
    screen = json.load(open(os.path.join(D, "screen", "blind_screen_codex_DISC-D1.json"), encoding="utf-8"))
    assert [s["id"] for s in screen] == [str(r["id"]) for r in _fetch()["broad_records"]]
    for s in screen:
        r = recs[s["id"]]
        assert s["quote"] in r["title"] + " " + (r.get("abstract") or "") or s["quote"] in (r.get("abstract") or ""), s["id"]
    verified = json.load(open(os.path.join(D, "screen", "VERIFIED.json"), encoding="utf-8"))
    assert set(verified["recall_cases"]) == set(CASES)


def test_the_registered_Hansson_2009_report_states_date_of_birth_allocation():
    # a finding for the registered set, from the same blind screen: quasi-randomised despite its RCT index term
    r = {str(x["id"]): x for x in _fetch()["broad_records"]}["19358184"]
    assert "according to date of birth" in r["abstract"]
