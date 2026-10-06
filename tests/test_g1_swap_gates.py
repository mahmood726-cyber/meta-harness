"""Plants (codex binding-v8-fe3ed2a7, reproduced on the binding branch): the swap gates validated a pooled estimate /
bound by SUBSTRING ('0.8' inside '0.85'), never checked k against the quote (999 vs '12 trials'), and accepted an
all-whitespace quote (it folds to '', contained in every text)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_swap as sw  # noqa: E402

Q = "RR 0.85 (95% CI 0.70-1.03); 12 trials."


def _p(**kw):
    p = {"measure": "RR", "estimate": "0.85", "lower": "0.70", "upper": "1.03", "k": 12, "quote": Q}
    p.update(kw)
    return p


def test_a_substring_value_is_refused():
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p(estimate="0.8", upper="1.0")}, Q)
    assert pooled is None and k is None


def test_an_unprinted_k_is_refused():
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p(k=999)}, Q)
    assert pooled is None and k is None


def test_the_printed_claim_stands():
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p()}, Q)
    assert pooled is not None and k == 12


def test_a_whitespace_quote_supports_nothing():
    out, _, _ = sw.gate_screen({"criteria": {"C2": {"verdict": "PASS", "quote": "   "}}, "pooled": {}}, Q)
    assert out["C2"]["verdict"] == "UNCLEAR"


def test_codex_re_review_v8_p0_fixes():
    q = "RR .85 (95% CI .70-1.03); 12 trials."
    # g1#2: a fabricated '85' is not the printed .85
    _, pooled, _ = sw.gate_screen({"criteria": {}, "pooled": _p(estimate="85", lower="70", quote=q)}, q)
    assert pooled is None
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p(estimate="0.85", lower="0.70", quote=q)}, q)
    assert pooled is not None and k == 12
    # g1#3: a fractional k is refused, never truncated
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p(k="12.6")}, Q)
    assert pooled is None and k is None
    _, pooled, k = sw.gate_screen({"criteria": {}, "pooled": _p(k="12")}, Q)
    assert k == 12 and isinstance(k, int)


def _xml(body):
    return (f"<article><p>{body}</p><ref id=\"r1\"><label>1</label><article-title>Alpha trial</article-title>"
            "<pub-id pub-id-type=\"pmid\">11111111</pub-id></ref><ref id=\"r2\"><label>2</label><article-title>Beta trial"
            "</article-title><pub-id pub-id-type=\"pmid\">22222222</pub-id></ref></article>")


def test_a_label_bound_to_another_reference_is_refused():
    # codex binding-v8-fe3ed2a7:g2#6: 'Alpha' cited as [1] was bound to reference 2's PMID
    xml = _xml("Included: Alpha [1]. Excluded: Beta [2].")
    units, refused, _, _ = sw.gate_enum({"trials": [{"label": "Alpha", "ref": "2", "row_quote": None}], "pooled": {},
                                         "set_quote": None}, {"text": sw.jats_text(xml), "xml": xml, "pmid": "33333333"})
    assert not units and refused[0]["why"].startswith("LABEL_CITES_ANOTHER_REFERENCE")
    units, refused, _, _ = sw.gate_enum({"trials": [{"label": "Alpha", "ref": "1", "row_quote": None}], "pooled": {},
                                         "set_quote": None}, {"text": sw.jats_text(xml), "xml": xml, "pmid": "33333333"})
    assert [u["pmid"] for u in units] == ["11111111"]


def test_an_xref_citation_is_read_through_the_reference_list():
    xml = _xml('Alpha et al. (2014) <xref ref-type="bibr" rid="r1">1</xref> and Beta <xref ref-type="bibr" rid="r2">2</xref>.')
    assert sw.label_cites("Alpha", xml, sw.jats_refs(xml)) == {"1"}
    assert sw.label_cites("Beta", xml, sw.jats_refs(xml)) == {"2"}


def test_one_unit_of_a_two_trial_analysis_is_not_complete():
    # codex binding-v8-fe3ed2a7:g2#7: enumeration was 'complete' whenever one unit passed and none was refused
    u1 = {"label": "Alpha", "pmid": "11111111"}
    u2 = {"label": "Beta", "pmid": "22222222"}
    assert sw.enumeration_state([u1], [], {"k": 2}) == "ENUMERATION_INCOMPLETE"
    assert sw.enumeration_state([u1, u2], [], {"k": 2}) == "ENUMERATED"
    assert sw.enumeration_state([u1, u2], [], {}) == "ENUMERATION_K_NOT_STATED"
    assert sw.enumeration_state([u1, u2], [{"why": "x"}], {"k": 2}) == "ENUMERATION_INCOMPLETE"
    assert sw.enumeration_state([], [], {"k": 2}) == "NOT_ENUMERATED"
