"""PLANTS for the swap harness gates (scripts/g1_swap.py): a recorded screening / enumeration answer counts only where
the meta's own held text supports it verbatim; identity comes from the meta's own reference list; apply never touches a
topic that was not PICKED or whose enumeration is incomplete."""
import json
import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

import g1_swap as sw  # noqa: E402

TEXT = ("We included only randomised controlled trials. Patients hospitalised with COVID-19. Tocilizumab versus usual "
        "care. 28-day mortality: OR 0.87 (95% CI 0.79 to 0.96), 19 trials. RECOVERY 621/2022 729/2094")


def test_gate_screen_counts_only_verbatim_quotes():
    claim = {"criteria": {"C2_RCT_ONLY": {"verdict": "PASS", "quote": "We included only randomised controlled trials."},
                          "C3_POPULATION": {"verdict": "PASS", "quote": "Patients with mild COVID-19."},
                          "C4_INTERVENTION_VS_COMPARATOR": {"verdict": "FAIL", "quote": None}},
             "pooled": {"measure": "OR", "estimate": "0.87", "lower": "0.79", "upper": "0.96", "k": 19,
                        "quote": "OR 0.87 (95% CI 0.79 to 0.96), 19 trials"}}
    crit, pooled, k = sw.gate_screen(claim, TEXT)
    assert crit["C2_RCT_ONLY"]["verdict"] == "PASS"
    assert crit["C3_POPULATION"]["verdict"] == "UNCLEAR" and crit["C3_POPULATION"]["evidence"].startswith("QUOTE_NOT_IN_TEXT")
    assert crit["C4_INTERVENTION_VS_COMPARATOR"]["verdict"] == "UNCLEAR"          # a FAIL needs its quote too
    assert pooled["estimate"] == "0.87" and k == 19
    bad = dict(claim, pooled=dict(claim["pooled"], estimate="0.77"))
    assert sw.gate_screen(bad, TEXT)[1] is None                                    # a number not in its own quote


XML = ("<article><body><p>RECOVERY [1] and REMAP-CAP [2] and Fake [3].</p></body><back><ref-list>"
       "<ref id=\"CR1\"><label>1.</label><element-citation><article-title>Tocilizumab in RECOVERY</article-title>"
       "<pub-id pub-id-type=\"pmid\">33933206</pub-id></element-citation></ref>"
       "<ref id=\"CR2\"><label>2.</label><element-citation><article-title>Interleukin-6 receptor antagonists</article-title>"
       "<pub-id pub-id-type=\"pmid\">33631065</pub-id></element-citation></ref></ref-list></back></article>")


def test_gate_enum_identity_from_the_metas_own_reference_list():
    it = {"pmid": "999", "xml": XML, "text": sw.jats_text(XML)}
    claim = {"set_quote": None, "pooled": {}, "trials": [
        {"label": "RECOVERY", "ref": "1", "row_quote": None}, {"label": "REMAP-CAP", "ref": "2", "row_quote": None},
        {"label": "Fake", "ref": "3", "row_quote": None},                       # reference 3 is not in the list
        {"label": "GHOST", "ref": "1", "row_quote": None}]}                     # label not in the text
    units, refused, _, _ = sw.gate_enum(claim, it)
    assert [(u["label"], u["pmid"], u["identity"]) for u in units] == [
        ("RECOVERY", "33933206", "COMPARATOR_REFERENCE_LIST_PMID"), ("REMAP-CAP", "33631065", "COMPARATOR_REFERENCE_LIST_PMID")]
    assert {r["label"]: r["why"] for r in refused} == {"Fake": "REFERENCE_NUMBER_NOT_IN_THE_METAS_REFERENCE_LIST",
                                                        "GHOST": "LABEL_NOT_IN_TEXT"}


def test_apply_never_touches_a_kept_or_incomplete_topic(tmp_path, capsys):
    (tmp_path / "x.selection.json").write_text(json.dumps({"result": "NO_SWAP_CURRENT_COMPARATOR_PASSES"}), encoding="utf-8")
    (tmp_path / "y.selection.json").write_text(json.dumps({"result": "PICKED", "pick": {"pmid": "1"}}), encoding="utf-8")
    with patch.object(sw, "SEL", str(tmp_path)), patch.object(sw, "ROOT", str(tmp_path)):
        os.makedirs(tmp_path / "registry" / "comparator_enumerations")
        (tmp_path / "registry" / "comparator_enumerations" / "y.swap.json").write_text(
            json.dumps({"status": "ENUMERATION_INCOMPLETE", "pooled": {"estimate": "1"}}), encoding="utf-8")
        sw.cmd_apply(["x", "y"])
    out = capsys.readouterr().out
    assert "x not applied: NO_SWAP_CURRENT_COMPARATOR_PASSES" in out and "y not applied: enumeration ENUMERATION_INCOMPLETE" in out
