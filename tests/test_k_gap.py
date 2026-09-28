"""K-GAP measurement: comparator included-set extraction and the members-proposal gate.

Each test PLANTS the shape that a naive implementation gets wrong and asserts the property, not a snapshot."""
from harness import k_gap

JATS = b"""<article><front><article-meta><title-group><article-title>MA</article-title></title-group></article-meta></front>
<body><p>x</p>
<table-wrap><label>Table 1</label><caption><p>Characteristics of the included trials</p></caption><table>
<thead><tr><th></th><th>WOMAN<xref ref-type="bibr" rid="R1">1</xref></th><th>TRAAP<xref ref-type="bibr" rid="R2">2</xref></th></tr></thead>
<tbody><tr><td>Randomly assigned, n</td><td>20060</td><td>4079</td></tr></tbody></table></table-wrap>
<table-wrap><label>Table 2</label><caption><p>Characteristics of included studies</p></caption><table>
<thead><tr><th>Study</th><th>Drug</th></tr></thead>
<tbody><tr><td>Year</td><td></td></tr>
<tr><td>ODYSSEY LONG TERM NCT01507831</td><td>Alirocumab</td></tr>
<tr><td>Smith 2010</td><td>Evolocumab</td></tr>
<tr><td>RALES1999</td><td>Spironolactone</td></tr></tbody></table></table-wrap>
<table-wrap><label>Table 3</label><caption><p>Subgroup analysis</p></caption><table>
<tbody><tr><td>SHOULDNOTCOUNT<xref ref-type="bibr" rid="R3">3</xref></td></tr></tbody></table></table-wrap>
</body><back><ref-list>
<ref id="R1"><mixed-citation>WOMAN Collaborators. Effect of tranexamic acid (WOMAN). Lancet 2017. <pub-id pub-id-type="pmid">28456509</pub-id></mixed-citation></ref>
<ref id="R2"><element-citation><person-group><name><surname>Sentilhes</surname></name></person-group><article-title>TRAAP</article-title><year>2018</year><pub-id pub-id-type="pmid">29791809</pub-id></element-citation></ref>
<ref id="R3"><mixed-citation>Other. <pub-id pub-id-type="pmid">11111111</pub-id></mixed-citation></ref>
<ref id="R4"><element-citation><person-group><name><surname>Smith</surname></name></person-group><year>2010</year><pub-id pub-id-type="pmid">22222222</pub-id></element-citation></ref>
</ref-list></back></article>"""


def _units():
    parsed = k_gap.parse_jats(JATS)
    return parsed, k_gap.included_trials(parsed, ["alirocumab", "evolocumab"])


def test_transposed_table_header_citations_are_units():
    # PLANT: trials cited only in HEADER cells (the tranexamic comparator layout). Dropping header xrefs
    # (the pre-fix parse) yields zero units from Table 1.
    _, inc = _units()
    t1 = [u for u in inc["units"] if u["table"] == "Table 1"]
    assert [u["label"] for u in t1] == ["WOMAN1", "TRAAP2"]
    assert {c["pmid"] for u in t1 for c in u["cited"]} == {"28456509", "29791809"}
    assert all(u["layout"] == "column" for u in t1)


def test_uncited_rows_kept_by_name_and_furniture_dropped():
    _, inc = _units()
    labels = [u["label"] for u in inc["units"] if u["table"] == "Table 2"]
    assert "Year" not in labels                     # table furniture is not a trial
    assert "ODYSSEY LONG TERM NCT01507831" in labels
    od = next(u for u in inc["units"] if u["label"].startswith("ODYSSEY"))
    assert od["ncts"] == ["NCT01507831"]
    sm = next(u for u in inc["units"] if u["label"] == "Smith 2010")
    assert (sm["author"], sm["year"]) == ("Smith", "2010")


def test_outcome_table_rows_are_not_included_set():
    _, inc = _units()
    assert not any("SHOULDNOTCOUNT" in u["label"] for u in inc["units"])


def test_agent_filter_marks_other_agent_only_when_some_row_names_a_topic_agent():
    _, inc = _units()
    by = {u["label"]: u["drug_match"] for u in inc["units"]}
    assert by["RALES1999"] == "OTHER_AGENT"         # a spironolactone row in a PCSK9 topic
    assert by["Smith 2010"] == "DRUG_MATCH"


def test_norm_acronym_strips_trailing_year_only():
    assert k_gap.norm_acronym("RALES1999") == "RALES"
    assert k_gap.norm_acronym("EMPEROR-Preserved") == "EMPERORPRESERVED"
    assert k_gap.norm_acronym("PIONEER 6") == "PIONEER6"
    assert k_gap.norm_acronym("SUSTAIN-6") == "SUSTAIN6"


HELD = "We included RECOVERY (n=6425) and\nthe CoDEX trial, both randomised."


def test_members_gate_admits_verbatim_quote_across_whitespace():
    v = k_gap.verify_members({"state": "ENUMERATED", "studies": [
        {"label": "RECOVERY", "quote": "We included RECOVERY (n=6425) and the CoDEX trial", "design_stated": "RCT"}]}, HELD)
    assert v["state"] == "VERIFIER_PASS" and len(v["admitted"]) == 1


def test_members_gate_refuses_paraphrase_and_label_outside_quote():
    # PLANT: a paraphrased quote (not in the held bytes) and a label the quote does not contain. Both must be
    # REFUSED and KEPT with their reason, never dropped.
    v = k_gap.verify_members({"state": "ENUMERATED", "studies": [
        {"label": "RECOVERY", "quote": "RECOVERY enrolled 6425 patients", "design_stated": "RCT"},
        {"label": "REMAP-CAP", "quote": "the CoDEX trial, both randomised", "design_stated": "RCT"}]}, HELD)
    assert v["admitted"] == []
    assert [r["problems"] for r in v["refused"]] == [["SPAN_NOT_IN_SOURCE"], ["LABEL_NOT_IN_QUOTE"]]
    assert v["state"] == "VERIFIER_REFUSED"


def test_members_gate_refuses_untyped_claim():
    assert k_gap.verify_members({"studies": []}, HELD)["state"] == "VERIFIER_REFUSED"


def _table_mod():
    import importlib.util
    import os
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "k_gap_table.py")
    spec = importlib.util.spec_from_file_location("k_gap_table", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_held_text_of_a_different_article_is_caught():
    # PLANT (the doac-vte-recurrence / corticosteroids-cap-mortality defect): the held text is a DIFFERENT article
    # on the same topic. It shares the topic's vocabulary (a title-word check passed both real cases) but none of
    # the comparator abstract's 6-word shingles.
    abstract = ("Direct oral anticoagulants were compared with vitamin K antagonists in six phase 3 trials that "
                "enrolled 27023 patients with acute venous thromboembolism; recurrent VTE occurred in 2.0 percent "
                "of DOAC recipients and 2.2 percent of VKA recipients")
    wrong = ("Venous thromboembolism is a multifactorial disease; thrombophilia testing is requested in patients "
             "treated with direct oral anticoagulants or vitamin K antagonists after acute venous thromboembolism")
    right = "Methods ... six phase 3 trials that enrolled 27023 patients with acute venous thromboembolism; recurrent VTE occurred in 2.0 percent of DOAC recipients ..."
    assert k_gap.held_text_identity(abstract, wrong)["state"] == "HELD_TEXT_NOT_NAMED_ARTICLE"
    assert k_gap.held_text_identity(abstract, right)["state"] == "NAMED_ARTICLE"
    assert k_gap.held_text_identity("", right)["state"] == "NO_ABSTRACT"


def test_reference_seed_keeps_only_rct_typed_agent_named_reports():
    refs = [{"pmid": "1", "title": "", "year": "2019"}, {"pmid": "2", "title": "", "year": "2019"},
            {"pmid": "3", "title": "", "year": "2019"}, {"pmid": "", "title": "Tocilizumab RCT", "year": "2020"}]
    pt = {"1": {"pubtypes": ["Randomized Controlled Trial"], "title": "Tocilizumab in hospitalized COVID-19"},
          "2": {"pubtypes": ["Review"], "title": "Tocilizumab: a review"},
          "3": {"pubtypes": ["Randomized Controlled Trial"], "title": "Sarilumab in COVID-19"}}
    u = k_gap.reference_seed_units(refs, pt, ["tocilizumab"])
    assert [x["cited"][0]["pmid"] for x in u] == ["1"]          # review, other agent, and no-PMID refs are out
    assert u[0]["table"] == "reference_seed"                     # labelled a candidate source, not a table
