"""G1 sglt2-primary-prevention-hf: a comparator unit that is a LETTER stands for the article it comments on (PubMed
CommentOn, kgap/comment_on.py). 'Isreb (19)' is the NEJM letter 31509682 on CREDENCE (30990260); the comparator's row
for it (89/2202 vs 141/2199) is CREDENCE's. Pre-fix (acq/k-gap 17fb03a): an open gap INSUFFICIENT_RECORD:NO_ABSTRACT --
the letter has no abstract, so nothing about the TRIAL could be read from it."""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

from kgap import comment_on as co  # noqa: E402

SLUG = "sglt2-primary-prevention-hf"
XML = ("<PubmedArticleSet><PubmedArticle><MedlineCitation Status='MEDLINE'><PMID Version='1'>111</PMID>"
       "<Article><PublicationTypeList><PublicationType UI='D016422'>Letter</PublicationType>"
       "<PublicationType UI='D016420'>Comment</PublicationType></PublicationTypeList></Article>"
       "<CommentsCorrectionsList><CommentsCorrections RefType=\"CommentOn\"><RefSource>N Engl J Med</RefSource>"
       "<PMID Version='1'>222</PMID></CommentsCorrections>"
       "<CommentsCorrections RefType=\"Cites\"><RefSource>x</RefSource><PMID Version='1'>333</PMID></CommentsCorrections>"
       "</CommentsCorrectionsList></MedlineCitation></PubmedArticle></PubmedArticleSet>")


def test_parse_reads_only_comment_on_edges():
    assert co.parse(XML) == {"111": {"comment_on": ["222"], "pubtypes": ["Letter", "Comment"]}}


def test_the_recorded_edge_carries_its_source_hash():
    r = json.load(open(co.REC, encoding="utf-8"))["31509682"]
    assert r["comment_on"] == ["30990260"] and len(r["xml_sha256"]) == 64 and r["pubtypes"] == ["Letter", "Comment"]


def test_isreb_is_named_by_credences_own_exclusion_and_span():
    import g1_tracker as gt
    o = json.load(open(os.path.join(gt.G1_DIR, SLUG + ".json"), encoding="utf-8"))
    d = next(d for d in o["named_differences"] if d["trial"].startswith("Isreb"))
    assert (d["kind"], d["rule_id"], d["pmid"]) == ("PROTOCOL_SCOPE_DIFFERENCE", "X2", "30990260")
    assert d["span"]["text"] == "Canagliflozin and Renal Outcomes in Type 2 Diabetes and Nephropathy."  # the ARTICLE's words
    assert d["via_comment_on"]["unit_pmid"] == "31509682"
    assert gt.span_is_verbatim(SLUG, "30990260", d["span"]) and gt.scope_citation_violations(o) == []


def test_a_letter_whose_article_is_not_excluded_with_a_span_stays_eligible(monkeypatch):
    import g1_tracker as gt
    x = {"label": "L", "family": "PMID 31509682", "in_our_pool": False, "scope_difference": None, "blocker": "B"}
    rev = {"screening": {"records": [{"id": "30990260", "decision": "include"}]}}     # our screen INCLUDED the article
    gt.name_letter_units_by_comment_on(SLUG, json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8")),
                                       [x], rev)
    assert x["scope_difference"] is None and x["blocker"] == "B"
    monkeypatch.setattr(co, "comment_on", lambda p: ["30990260", "999"])               # two articles: never chosen
    rev2 = {"screening": {"records": [{"id": "30990260", "decision": "exclude", "rule_id": "X2", "reason": "r"}]}}
    gt.name_letter_units_by_comment_on(SLUG, {}, [x], rev2)
    assert x["scope_difference"] is None


def test_pre_fix_isreb_was_an_open_gap():
    base = json.loads(subprocess.check_output(["git", "show", f"17fb03ab:outputs/k_gap/g1/{SLUG}.json"], cwd=ROOT))
    assert "Isreb (19)" in base["open_gaps"] and base["N_eligible"] == 6
