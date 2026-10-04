"""PubMed author-year identity: a pre-registry trial indexed only as 'Controlled Clinical Trial' whose abstract says
'randomly' (Nestler 1998, NEJM, PMID 9637806) was invisible to the RCT filter, so 16 metformin-PCOS comparator trials
stayed IDENTITY_UNRESOLVED. The strict query is still tried first (every existing resolution unchanged); the widened
design filter runs only when the strict one finds nothing, and the single-hit rule is unchanged."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
import k_gap_table as kt  # noqa: E402


def _cache(tmp_path, monkeypatch, answers):
    monkeypatch.setattr(kt, "OUT", str(tmp_path))
    (tmp_path / "pubmed_author_year.json").write_text(json.dumps(answers), encoding="utf-8")


def _strict(a, y):
    return f'{a}[1au] AND {y}[dp] AND ("metformin"[tiab]) AND (randomized controlled trial[pt] OR randomi*[tiab])'


def test_a_controlled_clinical_trial_with_randomly_in_its_abstract_resolves(tmp_path, monkeypatch):
    _cache(tmp_path, monkeypatch, {_strict("Nestler", "1998"): [],
                                   kt.author_year_wide_query("Nestler", "1998", ["metformin"]): ["9637806"]})
    pm, _q, _ids = kt.pubmed_author_year("Nestler", "1998", ["metformin"], offline=True)
    assert pm == "9637806"


def test_the_strict_answer_wins_and_the_wide_query_is_never_consulted_when_it_found_anything(tmp_path, monkeypatch):
    _cache(tmp_path, monkeypatch, {_strict("Palomba", "2004"): ["15472166"],
                                   kt.author_year_wide_query("Palomba", "2004", ["metformin"]): ["1", "2"]})
    assert kt.pubmed_author_year("Palomba", "2004", ["metformin"], offline=True)[0] == "15472166"
    _cache(tmp_path, monkeypatch, {_strict("Baillargeon", "2004"): ["15482765", "14715857"],
                                   kt.author_year_wide_query("Baillargeon", "2004", ["metformin"]): ["15482765"]})
    assert kt.pubmed_author_year("Baillargeon", "2004", ["metformin"], offline=True)[0] is None   # ambiguity stays


def test_the_widened_query_still_needs_exactly_one_hit_and_an_error_is_never_a_hit(tmp_path, monkeypatch):
    _cache(tmp_path, monkeypatch, {_strict("Ko", "2001"): [],
                                   kt.author_year_wide_query("Ko", "2001", ["metformin"]): ["1", "2"]})
    assert kt.pubmed_author_year("Ko", "2001", ["metformin"], offline=True)[0] is None
    _cache(tmp_path, monkeypatch, {_strict("Ko", "2001"): [],
                                   kt.author_year_wide_query("Ko", "2001", ["metformin"]): {"error": "503"}})
    assert kt.pubmed_author_year("Ko", "2001", ["metformin"], offline=True)[0] is None


def test_the_papers_own_registration_breaks_an_nct_tie_before_our_pool_does():
    # STEP 1 (PMID 33567185) is RESULT-linked by its own NCT03548935 and by SELECT's NCT03574597; SELECT is in our pool,
    # so the pool tie-break gave STEP 1 SELECT's identity (and SELECT's comparator row)
    m = ["NCT03548935", "NCT03574597"]
    kept, note = kt.nct_tiebreak(m, {"33567185"}, {"NCT03574597"}, {"33567185": "NCT03548935"})
    assert kept == ["NCT03548935"] and "paper_record" in note
    # the paper names no candidate: the old tie-break, unchanged
    assert kt.nct_tiebreak(m, {"1"}, {"NCT03574597"}, {"1": ""})[0] == ["NCT03574597"]
    assert kt.nct_tiebreak(m, {"1"}, set(), {})[0] == m
