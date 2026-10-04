"""A comparator reference that is a LETTER / COMMENT about a trial is that trial, by PubMed's own CommentOn link
(scripts/g1_comment_on.py -> registry/comment_on.json; g1_tracker.topic). sglt2-primary-prevention-hf 'Isreb (19)' cites
letter 31509682 on CREDENCE (30990260): our screen excludes the trial X2 'nephropathy', and the trial is named with that
rule and its title as span instead of standing as an INSUFFICIENT_RECORD open gap on the letter's empty record."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_comment_on as co  # noqa: E402

XML = ('<PubmedArticle><CommentsCorrectionsList><CommentsCorrections RefType="CommentOn"><RefSource>N Engl J Med'
       '</RefSource><PMID Version="1">30990260</PMID></CommentsCorrections><CommentsCorrections RefType="Cites">'
       '<PMID Version="1">111</PMID></CommentsCorrections></CommentsCorrectionsList></PubmedArticle>')


def test_comment_on_reads_only_the_commenton_links():
    assert co.comment_on(XML) == ["30990260"]                       # a 'Cites' link is not what the letter is about
    assert co.comment_on("<PubmedArticle/>") == []


def test_only_a_letter_comment_or_editorial_is_resolved():
    assert co.is_comment({"pubtypes": ["Letter", "Comment"]})
    assert not co.is_comment({"pubtypes": ["Journal Article", "Randomized Controlled Trial"]})
    assert not co.is_comment({"pubtypes": ["Comment", "Randomized Controlled Trial"]})   # a trial report that comments
    assert not co.is_comment({"pubtypes": []})


def test_registry_records_the_request_and_response_digest():
    reg = json.load(open(os.path.join(ROOT, "registry", "comment_on.json"), encoding="utf-8"))
    assert reg["31509682"]["comment_on"] == ["30990260"]
    assert all(len(v["response_sha256"]) == 64 and v["request"].startswith("https://eutils") for v in reg.values())


def test_isreb_19_is_credence_named_out_of_scope_and_an_unlinked_letter_is_not_resolved():
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "sglt2-primary-prevention-hf.json"), encoding="utf-8"))
    x = next(t for t in o["trials"] if t["label"].startswith("Isreb"))
    assert x["cited_as"]["pmid"] == "31509682" and x["cited_as"]["comment_on"] == "30990260"
    sd = x["scope_difference"]
    assert sd["rule_id"] == "X2" and "Nephropathy" in sd["span"]["text"] and sd["pmid"] == "30990260"
    assert "Isreb (19)" not in o["open_gaps"]
    # control: a cited letter with NO CommentOn link (24820749) is never resolved by guesswork
    reg = json.load(open(os.path.join(ROOT, "registry", "comment_on.json"), encoding="utf-8"))
    assert reg["24820749"]["comment_on"] == []
