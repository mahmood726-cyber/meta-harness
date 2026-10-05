"""Plants (5 Oct, forest lane): a model may read a held full text only when its copy is marked CC. The typed regex rung
may read any held copy (text mining, nothing enters a record); the recorded locator's prompt carries full text only from
a CC copy, and otherwise the title and abstract alone -- and its ref says which."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import copy_licence as cl  # noqa: E402


def test_unpaywall_licence_open_only_when_creative_commons_or_public_domain():
    assert cl.upw_open({"license": "cc-by"}) and cl.upw_open({"license": "cc-by-nc-nd"})
    assert cl.upw_open({"license": "public-domain"})
    for x in ({"license": None}, {"license": "publisher-specific-oa"}, {"license": "implied-oa"}, {}):
        assert not cl.upw_open(x)


def test_locator_text_carries_full_text_only_from_a_cc_copy():
    rec = {"title": "T", "abstract": "A"}
    shown, ref = cl.locator_text(rec, "FULL TEXT BODY", "CC", 123)
    assert "FULL TEXT BODY" in shown and "CC full text" in ref
    for lic in ("NOT_OPEN", "PMC_AUTHOR_MANUSCRIPT", None, "UPW_NOT_CC"):
        shown, ref = cl.locator_text(rec, "FULL TEXT BODY", lic, 123)
        assert "FULL TEXT BODY" not in shown and shown.strip() == "T\nA" and "abstract only" in ref
        assert "full text" not in ref.lower()      # record_licence's 'declared' detector reads 'PMID n ... full text'


def test_typed_reader_admits_only_cc_or_author_manuscript_copies():
    # g1/finish-line 9cf9841bc: the deterministic reader admits a row only from CC or a PMC author manuscript
    assert cl.typed_may_read("CC") and cl.typed_may_read("PMC_AUTHOR_MANUSCRIPT")
    for lic in ("NOT_OPEN", "NO_PMCID", None, "UPW_NOT_CC"):
        assert not cl.typed_may_read(lic)
