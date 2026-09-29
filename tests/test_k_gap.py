"""K-GAP measurement: comparator included-set extraction and the members-proposal gate.

Each test PLANTS the shape that a naive implementation gets wrong and asserts the property, not a snapshot."""
from kgap import k_gap

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
    return parsed, k_gap.included_trials(parsed, ["alirocumab", "evolocumab"], ["spironolactone", "finerenone"])


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


def test_row_without_a_drug_name_is_not_another_drug():
    # PLANT (the colchicine-postop-af / tranexamic defect): in a single-agent comparator one row names the agent
    # and the rest do not. The pre-fix rule marked every unnamed row OTHER_AGENT because SOME row named the agent.
    parsed = k_gap.parse_jats(JATS)
    inc = k_gap.included_trials(parsed, ["tranexamic acid", "evolocumab"], ["spironolactone"])
    by = {u["label"]: u["drug_match"] for u in inc["units"]}
    assert by["Smith 2010"] == "DRUG_MATCH"
    assert by["WOMAN1"] == "AGENT_IMPLICIT" and by["TRAAP2"] == "AGENT_IMPLICIT"
    assert by["RALES1999"] == "OTHER_AGENT"       # names another served topic's molecule, and none of ours


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


def test_title_parenthesised_acronym_is_read():
    # PLANT (RE-LY NCT00262600 / ROCKET AF NCT00403767): AACT's acronym field is EMPTY; the acronym exists only
    # in the title. Reading the acronym field alone left both unresolved in the 2026-09-28 run.
    got = [k_gap.norm_acronym(m.group(1)) for m in k_gap._PAREN_ACRO.finditer(
        "Randomized Evaluation of Long Term Anticoagulant Therapy (RE-LY) With Dabigatran Etexilate (ROCKET AF)")]
    assert got == ["RELY", "ROCKETAF"]


def test_family_acronym_match_is_exact_or_long_prefix():
    m = _table_mod()
    fams = [{"family_id": "NCT02465515", "reports": {"30291013"}, "acronyms": {"HARMONYOUTCOMES"}, "eligibility": "ELIGIBLE"},
            {"family_id": "SYN-1", "reports": {"10471456"}, "acronyms": {"RALES"}, "eligibility": "ELIGIBLE"}]
    assert m.family_by_acronym(["RALES1999"], fams)["family_id"] == "SYN-1"
    assert m.family_by_acronym(["HARMONY"], fams)["family_id"] == "NCT02465515"
    assert m.family_by_acronym(["RAL"], fams) is None           # too short to be an identity


def test_active_comparator_trial_is_scope_not_gap():
    # PLANT (ARTS-HF: finerenone vs EPLERENONE, double-dummy -- 'placebo' is in its intervention list, so an
    # intervention-name check called it placebo-controlled). The ARM TYPE says ACTIVE_COMPARATOR.
    m = _table_mod()
    idx = {"interventions": {"NCT01807221": ["Finerenone (BAY94-8862)", "Eplerenone", "Placebo"]},
           "design_groups": {"NCT01807221": [{"group_type": "EXPERIMENTAL", "title": "Finerenone"},
                                             {"group_type": "ACTIVE_COMPARATOR", "title": "Eplerenone [25 mg] + Placebo"}],
                             "NCT00232180": [{"group_type": "EXPERIMENTAL", "title": "Eplerenone"},
                                             {"group_type": "PLACEBO_COMPARATOR", "title": "Placebo"}],
                             "NCT00262600": [{"group_type": "EXPERIMENTAL", "title": "Dabigatran 150"},
                                             {"group_type": "ACTIVE_COMPARATOR", "title": "Warfarin"}]}}
    placebo_topic = {"include": {"comparator_any": ["placebo"]}}
    warfarin_topic = {"include": {"comparator_any": ["warfarin", "VKA"]}}
    assert m.comparator_scope(["NCT01807221"], idx, placebo_topic)["state"] == "COMPARATOR_NOT_IN_REGISTRY_ARMS"
    assert m.comparator_scope(["NCT00232180"], idx, placebo_topic)["state"] == "COMPARATOR_IN_REGISTRY_ARMS"
    assert m.comparator_scope(["NCT00262600"], idx, warfarin_topic)["state"] == "COMPARATOR_IN_REGISTRY_ARMS"
    assert m.comparator_scope([], idx, placebo_topic)["state"] == "UNKNOWN"


def test_label_citation_number_resolves_against_ref_list_with_surname_guard():
    # PLANT (7 topics in the 2026-09-28 run): proposal labels carry the comparator's citation number
    # ('Imazio [19]', 'Zinman (8)'). Unresolved, the proposal instrument scored 0 trials where the table scored 8-36.
    parsed = k_gap.parse_jats(JATS)
    assert [r["pmid"] for r in k_gap.refs_by_number("Smith [4]", parsed["refs"])] == ["22222222"]
    assert k_gap.refs_by_number("Jones [4]", parsed["refs"]) == []     # surname disagrees with ref 4 -> nothing
    assert k_gap.refs_by_number("Smith [99]", parsed["refs"]) == []    # no such ref -> nothing, never nearest


def _cf_mod():
    import importlib.util
    import os
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "k_gap_counterfactual.py")
    spec = importlib.util.spec_from_file_location("k_gap_counterfactual", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_a_larger_k_in_a_suppressed_pool_is_not_a_gain():
    # PLANT (colchicine-postop-af + COCS full text): one OR admitted into an RR pool -> k 3->4 AND the pooled effect
    # SUPPRESSED (INCOMPATIBLE estimands). Counting k alone scores the loss of the result as a gain.
    m = _cf_mod()
    base = {"outcomes": [{"primary": True, "result": {"k": 3, "estimate": 0.65, "scale": "RR"}, "trials": []}]}
    cf = {"outcomes": [{"primary": True, "result": {"k": 4, "scale": "INCOMPATIBLE (ODDS_RATIO + RISK_RATIO)",
                                                    "suppressed_incompatible": True}, "trials": []}]}
    assert m.core_primary(base)["k_valid"] == 3
    assert m.core_primary(cf)["k"] == 4 and m.core_primary(cf)["k_valid"] == 0


def test_citation_link_contradicting_its_row_is_not_followed():
    # PLANT (omega-3 comparator PMID 35905212): the table cites 'Kromhout 2010 [36]' but ref 36 is Quinn 2010 (a DHA
    # Alzheimer trial) and 'GISSI-HF 2008 [33]' but ref 33 is JELIS -- the whole table is one off from its ref list.
    unit = {"label": "Kromhout 2010 [36]", "author": "Kromhout", "year": "2010", "acronyms": []}
    assert k_gap.label_ref_conflict(unit, {"label": "36", "first_author": "Quinn", "year": "2010", "title": "DHA"})
    gissi = {"label": "GISSI-HF 2008 [33]", "author": "", "year": "2008", "acronyms": ["GISSI-HF 2008"]}
    jelis = {"label": "33", "first_author": "Yokoyama", "year": "2007",
             "title": "Effects of eicosapentaenoic acid on major coronary events in hypercholesterolaemic patients (JELIS)"}
    assert k_gap.label_ref_conflict(gissi, jelis)


def test_absence_is_not_contradiction():
    # A title that omits the acronym, a generic 'Trial A' label, an accent, or the ref number glued to the label
    # must NOT count as a conflict (each of these made the first version drop correct links -- esketamine lost 6/6).
    assert k_gap.label_ref_conflict({"label": "HEART-FID [11]", "acronyms": ["HEART-FID"]},
                                    {"label": "11", "first_author": "Mentz", "year": "2023",
                                     "title": "Ferric Carboxymaltose in Heart Failure with Iron Deficiency"}) is None
    assert k_gap.label_ref_conflict({"label": "Trial A (2019) (19)", "acronyms": []},
                                    {"label": "19", "first_author": "Popova", "year": "2019", "title": "x"}) is None
    assert k_gap.label_ref_conflict({"label": "Garz\u00f3n C [26]", "acronyms": []},
                                    {"label": "26", "first_author": "Garzon", "year": "2009", "title": "x"}) is None
    assert k_gap.label_ref_conflict({"label": "STEP 1 29", "acronyms": ["STEP 1 29"]},
                                    {"label": "29", "first_author": "Wilding", "year": "2021", "title": "Once-Weekly Semaglutide"},
                                    registry_acronyms=["STEP 1"]) is None


def test_typographic_hyphen_does_not_truncate_an_acronym():
    # PLANT (sglt2-hfref comparator): 'DAPA‐HF' (U+2010) tokenised as 'DAPA' and resolved to an unrelated DAPA-named
    # registration; 'EMPEROR‐Reduced' became 'EMPEROR'. Both are trials we POOL.
    assert k_gap._label_tokens("DAPA‐HF (n = 4744)")["acronyms"] == ["DAPA-HF"]
    assert k_gap._label_tokens("EMPEROR‐Reduced (n = 3730)")["acronyms"] == ["EMPEROR-Reduced"]
    assert k_gap._label_tokens("RALES Study")["acronyms"] == ["RALES"]      # an ordinary word is not absorbed


def test_self_naming_is_title_or_exact_parenthesised_definition():
    # PLANT (colchicine-pericarditis): a held 2024 paper citing '(CORE, CORP)' resolved the CORE row to itself.
    m = _table_mod()
    assert m.self_names("ROCKET AF", "Rivaroxaban versus warfarin", "... in Atrial Fibrillation (ROCKET AF) ...")
    assert not m.self_names("CORE", "A new trial", "Earlier trials (CORE, CORP) showed")
    assert m.self_names("CORE", "Colchicine for recurrent pericarditis: results of the CORE trial", "")
    assert not m.self_names("RALES1999", "The effect of spironolactone", "Randomized Aldactone Evaluation Study")


def test_a_paper_is_not_the_result_of_a_trial_registered_after_it():
    # PLANT (colchicine-postop-af): Deftereos' 2012-14 PMIDs are listed by NCT04906720 / NCT06731595 (2021+ trials
    # that cite them); following that link made Deftereos 'POOLED' through another paper of the later NCT.
    m = _table_mod()
    idx = {"study": {"NCT04906720": {"study_first_submitted_date": "2021-05-20"},
                     "NCT00128414": {"study_first_submitted_date": "2005-08-08"}}}
    assert m.registered_before("NCT04906720", 2014, idx) is False
    assert m.registered_before("NCT00128414", 2011, idx) is True
    assert m.registered_before("NCT09999999", 2014, idx) is True        # unknown date -> not excluded


def test_title_key_matches_a_second_record_of_the_same_article():
    # EMPA-REG's NEJM article has two PubMed records (26378978, 26981940); the comparator cites the second.
    m = _table_mod()
    assert m._title_key("Empagliflozin, Cardiovascular Outcomes, and Mortality in Type 2 Diabetes.") == \
        m._title_key("Empagliflozin, cardiovascular outcomes, and mortality in type 2 diabetes")


# ------------------------------------------------ comparator supplements (Europe PMC supplementaryFiles ZIP)

def _zip(members):
    import io
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, data in members:
            z.writestr(name, data)
    return buf.getvalue()


def _supp_env(tmp_path, monkeypatch, body):
    from harness import http
    monkeypatch.setattr(k_gap, "COMP_DIR", str(tmp_path))
    calls = []

    def fake(url, params=None, tries=4, timeout=30):
        calls.append(url)
        return 200, body
    monkeypatch.setattr(http, "get_raw", fake)
    return calls


def test_supplement_error_body_is_not_a_package_and_is_not_cached(tmp_path, monkeypatch):
    # EPMC answers an XML error body with HTTP 200 for a non-OA article: that must not become '' supplement text
    _supp_env(tmp_path, monkeypatch, b"<?xml version='1.0'?><error>not found</error>")
    r = k_gap.comparator_supplements("1", "PMC1", ["s1.csv"], "2026-09-29")
    assert r["state"] == "NOT_A_ZIP" and r["text"] == ""
    assert not list(tmp_path.rglob("*_kgap_supplements.txt"))


def test_supplement_zip_nested_zip_csv_read_doc_and_image_skipped(tmp_path, monkeypatch):
    inner = _zip([("S2.csv", "trial,rr\nALPHA,0.81\n")])
    _supp_env(tmp_path, monkeypatch, _zip([("fig1.jpg", b"\xff\xd8"), ("old.doc", b"\xd0\xcf\x11\xe0"),
                                           ("nested.zip", inner)]))
    r = k_gap.comparator_supplements("1", "PMC1", ["fig1.jpg", "old.doc", "nested.zip"], "2026-09-29")
    assert r["state"] == "OK" and "ALPHA" in r["text"] and "0.81" in r["text"]
    skipped = {f["file"]: f.get("skipped", "") for f in r["files"]}
    assert "OCR" in skipped["fig1.jpg"] and ".doc" in skipped["old.doc"]
    assert r["zip_sha256"] and r["route"].endswith("/PMC1/supplementaryFiles")


def test_supplement_cache_hit_keeps_manifest_and_refuses_a_tampered_text(tmp_path, monkeypatch):
    calls = _supp_env(tmp_path, monkeypatch, _zip([("S1.csv", "trial,rr\nBETA,1.10\n")]))
    first = k_gap.comparator_supplements("1", "PMC1", ["S1.csv"], "2026-09-29")
    again = k_gap.comparator_supplements("1", "PMC1", ["S1.csv"], "2026-09-29", offline=True)
    assert len(calls) == 1 and again["state"] == "CACHED" and again["zip_sha256"] == first["zip_sha256"]
    txt = next(tmp_path.rglob("*_kgap_supplements.txt"))
    txt.write_text(txt.read_text(encoding="utf-8").replace("1.10", "0.10"), encoding="utf-8")
    bad = k_gap.comparator_supplements("1", "PMC1", ["S1.csv"], "2026-09-29", offline=True)
    assert bad["state"] == "CACHE_HASH_MISMATCH" and bad["text"] == ""


def test_member_seeding_uses_resolved_report_when_cited_xref_was_rejected(tmp_path, monkeypatch):
    # omega-3 shape: the table's xref points one row off (DART), the resolver settled Eritsland by author+year
    import importlib
    import json
    import sys
    sys.path.append("scripts")
    cf = importlib.import_module("k_gap_counterfactual")
    rows = [{"slug": "s", "unit_source": "JATS_TABLE", "gap_class": "IDENTIFICATION", "drug": "OURS",
             "cited_pmids": ["2571009"], "pmids": ["8540453"]},                       # distrusted xref
            {"slug": "s", "unit_source": "JATS_TABLE", "gap_class": "IDENTIFICATION", "drug": "OURS",
             "cited_pmids": ["111"], "pmids": ["111", "222"]},                         # cited == resolved
            {"slug": "s", "unit_source": "JATS_TABLE", "gap_class": "IDENTIFICATION", "drug": "OURS",
             "cited_pmids": [], "pmids": ["333"]}]                                     # NCT-only
    (tmp_path / "k_gap_table.json").write_text(json.dumps({"topics": [], "trials": rows}), encoding="utf-8")
    monkeypatch.setattr(cf, "OUT", str(tmp_path))
    seeded, nct_only = cf.member_pmids("s")
    assert "8540453" in seeded and "2571009" not in seeded
    assert "111" in seeded and "222" not in seeded and nct_only == ["333"]


# ------------------------------------------------ forest-plot proposal gate (recomputation against the printed pool)

def _fp():
    import importlib
    import sys
    if "scripts" not in sys.path:
        sys.path.append("scripts")
    return importlib.import_module("k_gap_forest_plot")


def _plot(ratio=True):
    """Rows and a pooled row as a forest plot would print them (2 dp), with the pool computed FE from those rows."""
    import math
    fp = _fp()
    raw = [(0.87, 0.78, 0.97), (0.74, 0.58, 0.95), (0.91, 0.80, 1.04), (0.79, 0.62, 1.00)] if ratio else \
          [(-10.3, -12.0, -8.6), (-12.4, -13.4, -11.4), (-9.6, -11.4, -7.8)]
    rows = [{"effect": e, "lower": lo, "upper": hi} for e, lo, hi in raw]
    m, lo, hi = fp.pool_methods(rows, ratio=ratio)["FE"]
    fmt = (lambda x: f"{x:.2f}") if ratio else (lambda x: f"{x:.1f}")
    resp = {"legible": True, "measure": "HR" if ratio else "MD", "notes": "",
            "rows": [{"label": f"T{i}", "effect": fmt(e), "lower": fmt(a), "upper": fmt(b), "weight_pct": None}
                     for i, (e, a, b) in enumerate(raw)],
            "pooled": {"effect": fmt(m), "lower": fmt(lo), "upper": fmt(hi)}}
    text = f"The pooled result was {fmt(m)} (95% CI {fmt(lo)}-{fmt(hi)}) across trials."
    return fp, resp, text


def test_forest_gate_passes_a_plot_whose_rows_reproduce_the_printed_pool():
    fp, resp, text = _plot()
    g = fp.gate(resp, None, text)
    assert g["state"] == "PASS", g["problems"]
    assert "FE" in g["methods_reproducing"]


def test_forest_gate_refuses_a_misread_point_asymmetric_to_its_ci():
    fp, resp, text = _plot()
    resp["rows"][1]["effect"] = "0.54"                         # misread 0.74 -> 0.54; CI still 0.58-0.95
    g = fp.gate(resp, None, text)
    assert g["state"] == "REFUSED" and any(p.startswith("ROW_ORDER") or p.startswith("ROW_CI_ASYMMETRIC") for p in g["problems"])


def test_forest_gate_refuses_a_consistent_row_shift_by_recomputation():
    fp, resp, text = _plot()
    resp["rows"][0].update({"effect": "0.67", "lower": "0.60", "upper": "0.75"})   # self-consistent, but not the paper's
    g = fp.gate(resp, None, text)
    assert g["state"] == "REFUSED" and "RECOMPUTATION_DOES_NOT_REPRODUCE_PRINTED_POOL" in g["problems"]
    assert not any(p.startswith("ROW_CI_ASYMMETRIC") for p in g["problems"])      # the row checks alone pass it


def test_forest_gate_refuses_a_pooled_row_not_printed_in_the_text():
    fp, resp, text = _plot()
    g = fp.gate(resp, None, "The pooled hazard ratio was 0.99 (0.90-1.09).")
    assert g["state"] == "REFUSED" and "PLOT_POOLED_NOT_PRINTED_IN_TEXT" in g["problems"]


def test_forest_gate_pools_a_mean_difference_plot_on_the_raw_scale():
    fp, resp, text = _plot(ratio=False)
    g = fp.gate(resp, None, text)
    assert g["ratio"] is False and g["state"] == "PASS", g["problems"]


def test_forest_figure_selection_prefers_the_comparators_endpoint_over_a_component():
    # glp1: the MACE figure, not nonfatal MI (the topic's MACE keywords list 'myocardial infarction')
    fp = _fp()
    c, pmid, _ = fp.comparator("glp1-ra-mace-t2d")
    fig, why = fp.select_figure("glp1-ra-mace-t2d", pmid)
    assert why == "SELECTED" and "on MACE" in fig["caption"]


def test_forest_gate_anchor_requires_the_upper_bound_too():
    fp, resp, text = _plot()
    wrong_hi = text.replace("-" + resp["pooled"]["upper"] + ")", "-9.99)")
    assert wrong_hi != text
    g = fp.gate(resp, None, wrong_hi)
    assert g["state"] == "REFUSED" and "PLOT_POOLED_NOT_PRINTED_IN_TEXT" in g["problems"]


def test_agreement_keeps_the_printed_trailing_zero():
    # a forest plot prints '1.10'; our trial row says 1.11. As a float, '1.10' became 1.1 (one decimal) and the
    # comparison passed at 0.05 tolerance. At the PRINTED two decimals the upper limits differ by one unit.
    import importlib
    import sys
    if "scripts" not in sys.path:
        sys.path.append("scripts")
    ra = importlib.import_module("k_gap_result_agreement")
    assert ra._decimals("1.10") == 2 and ra._decimals("0.9") == 1
    assert ra.agree(("HR", 0.79, 0.57, 1.11), ("HR", "0.79", "0.57", "1.10"), "reported") != "AGREE"
    assert ra.agree(("HR", 0.87, 0.78, 0.97), ("HR", "0.87", "0.78", "0.97"), "reported") == "AGREE"


def test_forest_figure_refuses_multipanel_and_secondary_but_not_an_abbreviation():
    fp = _fp()
    assert fp.MULTIPANEL.search("Forest plots of MI, CVD and stoke.(A) Incidence of MI")
    assert fp.MULTIPANEL.search("Forest plot: A) renal composite B) HHF")          # missed when \b was a backspace byte
    assert not fp.MULTIPANEL.search("Forest plot for cardiovascular death (CVD) and MACE")
    assert fp.SECONDARY.search("Forest plot of secondary outcome: HFH")


def test_forest_gate_sets_aside_a_ratio_row_whose_lower_limit_prints_as_zero():
    fp, resp, text = _plot()
    resp["rows"].append({"label": "Tiny 2013", "effect": "0.07", "lower": "0.00", "upper": "1.14", "weight_pct": "0.3"})
    g = fp.gate(resp, None, text)
    assert [x["label"] for x in g["excluded_rows"]] == ["Tiny 2013"]
    assert "Tiny 2013" not in [r["label"] for r in g["rows"]]
    assert not any("Tiny" in p for p in g["problems"])


def test_forest_join_by_first_word_ignores_punctuation_and_joins_numbered_labels_by_author_and_year(monkeypatch):
    import importlib
    import sys
    if "scripts" not in sys.path:
        sys.path.append("scripts")
    ra = importlib.import_module("k_gap_result_agreement")
    rows = [{"label": "SELECT, 2023", "effect": 0.8, "lower": 0.71, "upper": 0.9, "printed": {"effect": "0.80", "lower": "0.71", "upper": "0.90"}},
            {"label": "Wallentin 2009", "effect": 0.83, "lower": 0.76, "upper": 0.92, "printed": {"effect": "0.83", "lower": "0.76", "upper": "0.92"}},
            {"label": "Wallentin 2014", "effect": 0.9, "lower": 0.8, "upper": 1.0, "printed": {"effect": "0.90", "lower": "0.80", "upper": "1.00"}}]
    monkeypatch.setattr(ra, "_FOREST", {"t": {"state": "PASS", "measure": "OR", "gate": {"rows": rows}}})
    monkeypatch.setattr(ra, "first_author_year", lambda p: {"111": ("wallentin", "2009")}.get(p))
    assert ra.forest_row("t", "SELECT 18") == ("OR", "0.80", "0.71", "0.90")          # comma no longer blocks it
    assert ra.forest_row("t", "9 [28]", ["111"]) == ("OR", "0.83", "0.76", "0.92")    # author AND year: 2009, not 2014
    assert ra.forest_row("t", "9 [28]", ["999"]) is None                               # no identity -> no join
