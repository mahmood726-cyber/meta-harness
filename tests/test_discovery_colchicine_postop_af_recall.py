"""V1.1 discovery recall test cases (colchicine-postop-af): four randomised colchicine-vs-placebo trials in cardiac
surgery (PMIDs 36747296, 25784519, 32175647, 12574898) that the registered queries cannot retrieve, because their titles
and abstracts never mention atrial fibrillation while both registered queries require it. Found by a second concept
query and a blind codex screen of the held records, each call verified against its record (screen/VERIFIED.json).
Whether each trial REPORTS postoperative AF is a full-text question this test does not answer.
Held run: evidence/discovery/colchicine-postop-af/run/."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "evidence", "discovery", "colchicine-postop-af")
CASES = ("36747296", "25784519", "32175647", "12574898")


def _fetch():
    return json.load(open(os.path.join(D, "run", "recall_fetch.json"), encoding="utf-8"))


def test_the_registered_queries_miss_every_recall_case_and_the_concept_query_finds_them():
    d = _fetch()
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    for pmid in CASES:
        assert pmid not in reg and pmid in d["broad_pmids"], pmid


def test_every_registered_query_requires_atrial_fibrillation_which_no_case_mentions():
    d = _fetch()
    assert all("atrial fibrillation" in q.lower() for q in d["registered_queries"])
    recs = {str(r["id"]): r for r in d["broad_records"]}
    for pmid in CASES:
        text = recs[pmid]["title"] + " " + (recs[pmid].get("abstract") or "")
        assert not re.search(r"fibrill", text, re.I), pmid
        assert "colchicine" in text.lower() and "random" in text.lower(), pmid


def test_every_blind_screen_quote_is_in_its_record_and_the_cases_were_verified():
    d = _fetch()
    recs = {str(r["id"]): r for r in d["broad_records"]}
    screen = json.load(open(os.path.join(D, "screen", "blind_screen_codex_DISC-D2b.json"), encoding="utf-8"))
    assert [s["id"] for s in screen] == [str(r["id"]) for r in d["broad_records"]]
    for s in screen:
        r = recs[s["id"]]
        assert s["quote"] in r["title"] + " " + (r.get("abstract") or "") or s["quote"] in (r.get("abstract") or ""), s["id"]
    verified = json.load(open(os.path.join(D, "screen", "VERIFIED.json"), encoding="utf-8"))
    assert set(verified["recall_cases"]) == set(CASES)


def test_the_open_full_text_recall_case_reports_postoperative_AF_counts():
    import hashlib, html
    v = json.load(open(os.path.join(D, "screen", "VERIFIED.json"), encoding="utf-8"))["full_text_checks"]["36747296"]
    raw = open(os.path.join(D, "fulltext", "PMC9903414.xml"), "rb").read()
    assert hashlib.sha256(raw).hexdigest() == v["sha256"]
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw.decode("utf-8"))))
    assert v["quote_table"] in text and v["quote_discussion"] in text
