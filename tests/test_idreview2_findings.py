"""IDREVIEW2 (Codex gpt-5.5, adversarial review round 2): its five findings, written as strict xfails by the reviewer, kept as
REGRESSION tests now that each is fixed on g1/identity."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / "scripts"))

from kgap import k_gap  # noqa: E402
import k_gap_table as kt  # noqa: E402


IDX = {
    "pmid_nct": {},
    "agent_nct": {},
    "acr_nct": {},
    "acr_title_nct": {},
    "nct_pmids": {},
    "study": {},
}


def parsed(*refs):
    return {
        "refs": {
            r["rid"]: dict(
                {
                    "label": "",
                    "ordinal": i + 1,
                    "title": "",
                    "year": "",
                    "first_author": "",
                    "text": "",
                },
                **r,
            )
            for i, r in enumerate(refs)
        }
    }


def unit(label, **kw):
    t = k_gap.identity_tokens(label)
    return dict(
        {
            "cited": [],
            "ncts": [],
            "author": t["author"],
            "year": t["year"],
            "acronyms": t["acronyms"],
            "marker": t["marker"],
            "label": label,
        },
        **kw,
    )


@pytest.fixture(autouse=True)
def clean_state(monkeypatch):
    monkeypatch.setattr(kt, "REF_PMID", {})
    monkeypatch.setattr(kt, "PUBNCT", {})
    monkeypatch.setattr(kt, "SELF_REG", {})
    monkeypatch.setattr(kt, "COLLECTIVE", {})
    monkeypatch.setattr(kt, "registered_before", lambda n, y, idx: True)


def test_long_form_refuses_embedded_different_trial_acronym():
    assert not kt.acronym_long_form("CORP", "CORE COlchicine for REcurrent pericarditis")
    assert not kt.acronym_long_form("CORP", "COPPS a multicentre randomized double blind placebo controlled trial")


def test_resolver_does_not_turn_core_reference_into_corp_identity(monkeypatch):
    ref = {
        "rid": "REF:2",
        "label": "2",
        "pmid": None,
        "first_author": "Imazio",
        "year": "2005",
        "title": "CORE COlchicine for REcurrent pericarditis",
        "text": "Imazio M. CORE COlchicine for REcurrent pericarditis. 2005.",
    }
    monkeypatch.setattr(kt, "REF_PMID", {kt._ref_key(ref): {"state": "CONFIRMED", "pmid": "11111111"}})
    idx = dict(IDX, pmid_nct={"11111111": [("NCT01111111", "RESULT")]})

    r = kt.resolve_unit(unit("CORP study", layout="text"), parsed(ref), idx, None)

    assert r["pmids"] == []
    assert r["ncts"] == []
    assert any(b.startswith("acronym_long_form_refused") for b in r["basis"])


def test_one_registration_consolidation_refuses_primary_plus_extension_publications():
    primary = {
        "rid": "R1",
        "pmid": "22222221",
        "year": "2020",
        "text": "Smith J. VERTIS CV randomized trial primary cardiovascular outcomes.",
    }
    extension = {
        "rid": "R2",
        "pmid": "22222222",
        "year": "2021",
        "text": "Jones J. VERTIS CV open-label extension study of renal follow-up outcomes.",
    }
    idx = dict(
        IDX,
        pmid_nct={
            "22222221": [("NCT01986881", "RESULT")],
            "22222222": [("NCT01986881", "DERIVED")],
        },
    )

    r = kt.resolve_unit(unit("VERTIS-CV", layout="text"), parsed(primary, extension), idx, None)

    assert r["pmids"] == []
    assert r["ncts"] == []
    assert "acronym_in_comparator_refs_same_registration_publication_unit_ambiguous:VERTIS-CV:2" in r["basis"]


def test_author_only_ref_requires_trial_context_not_just_unique_surname():
    ref = {
        "rid": "REF:9",
        "label": "9",
        "pmid": "33333333",
        "first_author": "Smith",
        "year": "2018",
        "title": "Background epidemiology in recurrent pericarditis",
        "text": "Smith J. Background epidemiology in recurrent pericarditis. 2018.",
    }
    idx = dict(IDX, pmid_nct={"33333333": [("NCT03333333", "REFERENCE")]})

    r = kt.resolve_unit(unit("Smith et al", layout="text"), parsed(ref), idx, None)

    assert r["pmids"] == []
    assert r["ncts"] == []
    assert "author_only_ref_refused_no_trial_context:REF:9" in r["basis"]


def test_pmc_html_refs_refuses_duplicate_number_labels():
    html = """
    <ol>
      <li id="bib1"><span class="label">1.</span><cite>Alpha A. First trial. J. 2020.</cite>
        <a href="https://pubmed.ncbi.nlm.nih.gov/44444441/">PubMed</a></li>
      <li id="bib1-dup"><span class="label">1.</span><cite>Beta B. Second trial. J. 2021.</cite>
        <a href="https://pubmed.ncbi.nlm.nih.gov/44444442/">PubMed</a></li>
    </ol>
    """

    refs = kt.pmc_html_refs(html)

    assert refs == {}


def test_negative_long_form_keeps_true_trial_name_and_loose_phrase_separate():
    assert kt.acronym_long_form("RALES", "Randomized aldactone evaluation study investigators.")
    assert not kt.acronym_long_form(
        "COPE",
        "Colchicine in addition to conventional therapy for acute pericarditis: results.",
    )


def test_negative_one_registration_different_ncts_remains_ambiguous():
    a = {"rid": "A", "pmid": "55555551", "text": "VERTIS CV trial."}
    b = {"rid": "B", "pmid": "55555552", "text": "VERTIS CV trial follow-up."}
    idx = dict(
        IDX,
        pmid_nct={
            "55555551": [("NCT01986881", "RESULT")],
            "55555552": [("NCT09999999", "RESULT")],
        },
    )

    r = kt.resolve_unit(unit("VERTIS-CV", layout="text"), parsed(a, b), idx, None)

    assert r["pmids"] == []
    assert r["ncts"] == []
    assert "acronym_in_comparator_refs_ambiguous:VERTIS-CV:2" in r["basis"]
