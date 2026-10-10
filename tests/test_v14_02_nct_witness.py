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
