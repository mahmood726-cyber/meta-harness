"""agy v14-apply-r1-agy #2: the V14-02 script verifies each trial's NCT against the article itself, never trusts it."""
import importlib.util
import os

_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "v14_02_dpp4_hhf.py")
_spec = importlib.util.spec_from_file_location("v14_02", _p)
v = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v)

ART = ("<PubmedArticle><Abstract><AbstractText>hHF was reduced.</AbstractText></Abstract>{bank}"
       "<ReferenceList><Reference>Prior trial NCT01897532.</Reference></ReferenceList></PubmedArticle>")


def test_databank_accession_is_a_witness():
    art = ART.format(bank="<DataBankList><DataBank><AccessionNumberList><AccessionNumber>NCT01897532"
                          "</AccessionNumber></AccessionNumberList></DataBank></DataBankList>")
    assert v.nct_witness(art, "NCT01897532") == "databank accession number"


def test_reference_list_mention_is_not_a_witness():
    assert v.nct_witness(ART.format(bank=""), "NCT01897532") is None


def test_abstract_mention_must_be_the_exact_identifier():
    """codex v14-apply-r3 g1#1: NCT017032080 is not NCT01703208."""
    art = "<PubmedArticle><Abstract><AbstractText>Trial registration: NCT017032080.</AbstractText></Abstract></PubmedArticle>"
    assert v.nct_witness(art, "NCT01703208") is None


def test_offline_refuses_unverified_manifest_identity():
    """codex v14-apply-r3 g1#2: offline mode never accepts a basis it cannot check against the recorded evidence."""
    good = {"nct": "NCT01703208", "nct_basis": "databank accession number",
            "nct_evidence": "<AccessionNumber>NCT01703208</AccessionNumber>"}
    assert v.offline_identity_ok(good, "NCT01703208")
    assert not v.offline_identity_ok(dict(good, nct="NCT00000000"), "NCT01703208")
    assert not v.offline_identity_ok(dict(good, nct_basis="unverified"), "NCT01703208")
    assert not v.offline_identity_ok(dict(good, nct_evidence="no identifier here"), "NCT01703208")
