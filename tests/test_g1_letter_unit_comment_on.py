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
    assert co.parse(XML) == {"111": {"comment_on": ["222"], "comment_on_unresolved": 0, "pubtypes": ["Letter", "Comment"]}}


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
    monkeypatch.setattr(co, "record", lambda p: {"comment_on": ["30990260", "999"]})  # two articles: never chosen
    rev2 = {"screening": {"records": [{"id": "30990260", "decision": "exclude", "rule_id": "X2", "reason": "r"}]}}
    gt.name_letter_units_by_comment_on(SLUG, {}, [x], rev2)
    assert x["scope_difference"] is None


def test_pre_fix_isreb_was_an_open_gap():
    base = json.loads(subprocess.check_output(["git", "show", f"f5f1a1bef155:outputs/k_gap/g1/{SLUG}.json"], cwd=ROOT))
    assert "Isreb (19)" in base["open_gaps"] and base["N_eligible"] == 6


# --- plants from cross-vendor review NR-C24 (Codex; artefact F:/mh-nr101-codex/c24-g1-comment-on/last_message.txt) ---
def _art(own, ccs):
    return (f"<PubmedArticle><MedlineCitation><PMID Version='1'>{own}</PMID><Article><PublicationTypeList>"
            f"<PublicationType>Letter</PublicationType></PublicationTypeList></Article><CommentsCorrectionsList>{ccs}"
            f"</CommentsCorrectionsList></MedlineCitation></PubmedArticle>")


def test_c24_a_pmid_less_comment_on_never_borrows_the_next_relationships_pmid():
    x = _art(111, '<CommentsCorrections RefType="CommentOn"><RefSource>N Engl J Med</RefSource></CommentsCorrections>'
                  '<CommentsCorrections RefType="CommentIn"><RefSource>x</RefSource><PMID>222</PMID></CommentsCorrections>')
    r = co.parse("<PubmedArticleSet>" + x + "</PubmedArticleSet>")["111"]
    assert r["comment_on"] == [] and r["comment_on_unresolved"] == 1


def test_c24_whitespace_and_quoting_variants_parse_alike():
    x = _art(" 111 ", "<CommentsCorrections RefType='CommentOn'><RefSource>y</RefSource><PMID> 222 </PMID></CommentsCorrections>")
    assert co.parse("<PubmedArticleSet>" + x + "</PubmedArticleSet>")["111"]["comment_on"] == ["222"]


def test_c24_conflicting_duplicate_records_are_refused():
    import pytest
    a = _art(111, '<CommentsCorrections RefType="CommentOn"><PMID>222</PMID></CommentsCorrections>')
    b = _art(111, '<CommentsCorrections RefType="CommentOn"><PMID>333</PMID></CommentsCorrections>')
    with pytest.raises(ValueError):
        co.parse("<PubmedArticleSet>" + a + b + "</PubmedArticleSet>")


def test_c24_a_letter_is_named_only_with_one_resolved_edge_and_a_row_bound_to_the_article(monkeypatch):
    import g1_tracker as gt
    cfg = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    rev = {"screening": {"records": [{"id": "30990260", "decision": "exclude", "rule_id": "X2", "reason": "r"}]}}

    def unit(row):
        return {"label": "L", "family": "PMID 31509682", "in_our_pool": False, "scope_difference": None, "blocker": "B",
                "comparator_row": row}
    ok = {"effect": "0.63", "n_t": 2202, "n_c": 2199}
    x = unit(ok)
    gt.name_letter_units_by_comment_on(SLUG, cfg, [x], rev)
    assert x["scope_difference"] and x["scope_difference"]["row_binding"]["total"] == 4401
    x = unit({"effect": "0.63", "n_t": 1000, "n_c": 1000})                 # the row is NOT the article's trial
    gt.name_letter_units_by_comment_on(SLUG, cfg, [x], rev)
    assert x["scope_difference"] is None and x["blocker"] == "B"
    x = unit({"effect": "0.63"})                                          # no row counts: identity unbound
    gt.name_letter_units_by_comment_on(SLUG, cfg, [x], rev)
    assert x["scope_difference"] is None
    x = unit(ok)
    gt.name_letter_units_by_comment_on(SLUG, cfg, [x], {"screening": {"records": [
        {"id": "30990260", "decision": "exclude", "rule_id": "X1", "reason": "r"}]}})    # screen rule != audit rule
    assert x["scope_difference"] is None
    monkeypatch.setattr(co, "record", lambda p: {"comment_on": ["30990260"], "comment_on_unresolved": 1})
    x = unit(ok)
    gt.name_letter_units_by_comment_on(SLUG, cfg, [x], rev)                # an unresolved second edge: ambiguous
    assert x["scope_difference"] is None


def test_PLANT_a_repointed_unit_whose_row_does_not_bind_is_left_unnamed(monkeypatch):
    # 5 Oct night decision 2: the stricter row-bound rule takes precedence over any CommentOn re-point (finish-line's
    # cited_as or k-gap's IDENTITY_CHAIN:COMMENT_ON). A re-point that named the unit by the article's screen exclusion,
    # but whose comparator row does not bind to the article's own patient count, is UNNAMED (an open gap)
    import g1_tracker as gt
    sd = {"kind": "PROTOCOL_SCOPE_DIFFERENCE", "rule_id": "X2", "span": {"field": "title", "text": "t"}, "pmid": "30990260"}
    rev = {"screening": {"records": [{"id": "30990260", "decision": "exclude", "rule_id": "X2", "reason": "r"}]}}
    cfg = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    for how in ("cited_as", "chain"):
        x = {"label": "Isreb (19)", "family": "PMID 30990260", "in_our_pool": False, "scope_difference": dict(sd),
             "blocker": None, "comparator_row": {"n_t": 1000, "n_c": 1000}}       # 2000 is not CREDENCE's 4401
        rows = []
        if how == "cited_as":
            x["cited_as"] = {"pmid": "31509682", "comment_on": "30990260"}
        else:
            rows = [{"label": "Isreb (19)", "identity_basis": ["IDENTITY_CHAIN:COMMENT_ON:31509682->30990260"]}]
        gt.name_letter_units_by_comment_on(SLUG, cfg, [x], rev, rows)
        assert x["scope_difference"] is None, how
        assert x["blocker"].startswith("IDENTIFICATION:COMMENT_ON_NOT_ROW_BOUND"), how
    # control: an unrepointed unit already named by another rule is never touched
    y = {"label": "Other", "family": "PMID 1", "in_our_pool": False, "scope_difference": dict(sd), "blocker": None}
    gt.name_letter_units_by_comment_on(SLUG, cfg, [y], rev, [])
    assert y["scope_difference"] == sd
