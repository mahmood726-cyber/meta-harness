"""V1.0.1 (sacubitril-HFrEF review): Ji 2023's HFrEF-composite membership from its own outcome-level citation list,
PARALLEL-HF bound by its printed acronym to the trial we pool, the scope (17 network-wide, 10 in the composite, two
direct ARNI-vs-RASi trials in HFrEF), and RR-vs-HR agreement stated as not validation. Plants are synthetic."""
import json
from pathlib import Path

import pytest

from harness import comparator_panel as cp
from harness import overlap_relation as orl

ROOT = Path(__file__).resolve().parents[1]
SLUG = "sacubitril-valsartan-hfref"


def _review():
    return json.loads((ROOT / "docs" / "reviews" / SLUG / "review.json").read_text(encoding="utf-8"))


def _page():
    return (ROOT / "docs" / "reviews" / SLUG / "index.html").read_text(encoding="utf-8")


def test_ji_hfref_composite_is_enumerated_and_both_our_trials_are_shared():
    ov = _review()["comparator"]["overlap"]
    assert (ov["relation"], ov["ours_k"], ov["theirs_k"], ov["shared_k"], ov["only_ours"]) == ("SUBSET", 2, 10, 2, [])


def test_parallel_hf_binds_to_the_registered_trial_and_its_paper_is_disclosed_as_unlinked():
    th = _review()["comparator"]["overlap_relation"]["theirs"]["members"]
    m = next(x for x in th if "PARALLEL" in x["name"])
    assert m["family"] == "NCT02468232"
    assert "PARALLEL-HF" in m["identity"] and "unlinked report-only family" in m["identity"]


def test_scope_mismatch_and_representation_are_rendered_and_the_gate_holds():
    r, page = _review(), _page()
    assert "network-wide 17 is not the target" in page and "PARADIGM-HF and PARALLEL-HF" in page
    assert "not an independent result" in page and "COMPARATOR_INTERNAL_MISMATCH" in page
    assert cp.gate_reasons(r, page) == []
    # our control stays a RAS inhibitor: the comparator row beside our result is the main text's RASi comparison
    assert "RAS inhibitors" in r["comparator"]["reported"][0]["outcome"]


def test_pool_unchanged():
    o = next(o for o in _review()["outcomes"] if o.get("primary"))
    assert sorted(str(t["label"]) for t in o["trials"]) == ["25176015", "PARALLEL-HF"]


# ---- plants ---------------------------------------------------------------------------------------------------------
def _x(rid, n):
    return f'<xref rid="{rid}" ref-type="bibr">\n<sup>{n}</sup>\n</xref>'


def test_plant_outcome_list_rids_reads_a_trailing_citation_run_with_digit_ids():
    frag = "was available in 3 trials." + ", ".join(_x(f"e9-bib-000{i}", i) for i in (2, 3, 7))
    assert cp.outcome_list_rids(frag) == ["e9-bib-0002", "e9-bib-0003", "e9-bib-0007"]
    assert cp.outcome_list_rids(frag + " and more text") is None           # the run must END the fragment
    assert cp.outcome_list_rids(frag + ", " + _x("e9-bib-0002", 2)) is None  # a repeated id refuses


def _member(tmp_path, k_printed, k_claimed, cited, rid):
    xml = ("<p>The outcome was available in %d trials.%s</p>" % (k_printed, ", ".join(_x(r, i) for i, r in enumerate(cited)))
           + f'<ref id="{rid}"><article-title>ALPHA trial</article-title><pub-id pub-id-type="pmid">111</pub-id></ref>')
    (tmp_path / "j.xml").write_bytes(xml.encode("utf-8"))            # bytes: no newline translation
    import hashlib
    sha = hashlib.sha256(xml.encode("utf-8")).hexdigest()
    a, b = xml.index("The outcome"), xml.index("</p>")
    ra, rb = xml.index(f'<ref id="{rid}">'), xml.index("</ref>") + len("</ref>")
    ref = {"start": ra, "end": rb, "quote": xml[ra:rb]}
    return {"held": True, "document_ref": "j.xml", "document_sha256": sha,
            "trial_set": [{"family_id": "ALPHA [x]", "name_in_source": "ALPHA", "span": ref, "endpoint": None,
                           "aliases": [{"id": "111", "document_ref": "j.xml", "document_sha256": sha, "span": ref,
                                        "linked_rid": rid, "stated_k": k_claimed,
                                        "outcome_list_span": {"start": a, "end": b, "quote": xml[a:b]}}]}]}


def test_plant_an_outcome_list_member_is_validated_against_the_printed_count(tmp_path):
    ok = _member(tmp_path, 2, 2, ["r1", "r2"], "r1")
    cp.validate(ok, tmp_path)
    for args in ((3, 3, ["r1", "r2"], "r1"),                     # prints 3 trials, cites 2
                 (2, 2, ["r1", "r2"], "r9")):                    # the member is not in the cited list
        bad = _member(tmp_path, *args)
        with pytest.raises(ValueError, match="outcome-list member"):
            cp.validate(bad, tmp_path)


def test_plant_unicode_hyphen_is_read_as_a_hyphen():
    assert "PARALLEL‐HF".translate(orl._UNICODE_HYPHENS) == "PARALLEL-HF"
