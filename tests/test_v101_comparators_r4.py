"""V1.0.1 round 4 (metformin-PCOS, NOAC-AF and PCSK9 reviews): governing comparator analysis, same-trials-different-
model, comparator scope, registry-id table rows, and comparator-named trials entering screening.
Served fixtures read the committed pages; plants build synthetic inputs in tmp_path (never pinned to corpus pages)."""
import hashlib
import json
from pathlib import Path

import pytest

from harness import comparator_analysis as ca
from harness import comparator_named as cn
from harness import comparator_panel as cp
from harness.overlap_relation import _TITLE_ACR
from harness.pipeline import _query_classification

ROOT = Path(__file__).resolve().parents[1]


def _review(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _page(slug):
    return (ROOT / "docs" / "reviews" / slug / "index.html").read_text(encoding="utf-8")


# ---- metformin-PCOS: the protocol benchmarked the wrong comparison -------------------------------------------------
def test_metformin_governing_analysis_replaces_the_wrong_benchmark():
    r = _review("metformin-pcos-ovulation")
    row = r["comparator"]["reported"][0]
    assert (row["analysis"], row["estimate"], row["ci_low"], row["ci_high"]) == ("Analysis 2.4", 1.65, 1.35, 2.03)
    b = row["replaces_protocol_benchmark"]
    assert b["state"] == "WRONG_COMPARISON" and b["estimate"] == 2.64


def test_metformin_membership_shares_our_three_trials_with_the_same_counts():
    r = _review("metformin-pcos-ovulation")
    ov = r["comparator"]["overlap"]
    assert (ov["relation"], ov["ours_k"], ov["theirs_k"], ov["shared_k"]) == ("SUBSET", 3, 21, 3)
    assert len(r["comparator"]["analysis"]["membership"]["shared_same_counts"]) == 3


def test_metformin_legro_row_is_flagged_and_never_copied():
    r = _review("metformin-pcos-ovulation")
    flags = r["comparator"]["analysis"]["row_flags"]
    assert any(f["state"] == "COMPARATOR_ROW_UNRECONCILED" and "Legro" in f["row"] for f in flags)
    assert "108/209" not in json.dumps(r["outcomes"])


def test_a_joined_legacy_row_is_classified_query_by_query():
    q = '"metformin"[Title] AND "polycystic ovary syndrome"[Title] || "clomiphene"[Title] AND "metformin"[Title]'
    got = _query_classification(q)
    assert got["kind"] == "TITLE_RESTRICTED_CONCEPT" and "joined_queries:2" in got["features"]
    # a UID part makes the joined row an enumeration: the most seeded part decides
    assert _query_classification("123[uid] || metformin[Title]")["kind"] == "PMID_ENUMERATION"


# ---- NOAC-AF: COMBINE AF is the same trials under another model -----------------------------------------------------
def test_noac_combine_af_is_identical_set_and_its_model_difference_is_rendered():
    r = _review("noac-vs-warfarin-af-stroke")
    ov = r["comparator"]["overlap"]
    assert (ov["relation"], ov["shared_k"]) == ("IDENTICAL_SET", 4)
    page = _page("noac-vs-warfarin-af-stroke")
    assert "Same trials, different model" in page and "32-months" in page and "not an independent result" in page


def test_title_acronym_reader_keeps_trial_names_and_refuses_drug_codes():
    assert _TITLE_ACR.findall("Dabigatran versus warfarin (RE-LY)") == ["RE-LY"]
    assert _TITLE_ACR.findall("Rivaroxaban (BAY 59-7939) in AF") == []


# ---- PCSK9: comparator scope, independence, and trials the comparator names -----------------------------------------
def test_pcsk9_wang_table_enumerates_twelve_and_shares_our_two():
    ov = _review("pcsk9-mace")["comparator"]["overlap"]
    assert (ov["relation"], ov["ours_k"], ov["theirs_k"], ov["shared_k"], ov["only_ours"]) == ("SUBSET", 2, 12, 2, [])


def test_pcsk9_scope_and_independence_are_stated_and_the_gate_holds():
    r, page = _review("pcsk9-mace"), _page("pcsk9-mace")
    assert "Scope, in the comparator&#x27;s words" in page or "Scope, in the comparator's words" in page
    assert "OSLER-1" in page and "not 10 trials missing from ours" in page
    assert "46,488 of its 53,486" in page
    assert cp.gate_reasons(r, page) == []
    assert "trial membership remain unknown" not in page


def test_pacman_ami_is_a_screened_candidate_found_by_comparator_named():
    rows = {str(d["id"]).split(" · ")[-1]: d for d in _review("pcsk9-mace")["screening"]["records"]}
    assert rows["35368058"]["found_by"] == ["COMPARATOR_NAMED"] and rows["35368058"]["decision"] == "include"
    fam = next(f for f in _review("pcsk9-mace")["trial_families"] if f["family_id"] == "NCT03067844")
    assert fam["entered_via"] == ["COMPARATOR_NAMED"]
    # its imaging substudies are reports of the SAME family
    assert {"35368058", "37341586", "39221516"} <= {x["report_id"] for x in fam["reports"]}


def test_pcsk9_pool_is_unmoved_by_the_candidates():
    o = next(o for o in _review("pcsk9-mace")["outcomes"] if o.get("primary"))
    assert sorted(str(t["label"]) for t in o["trials"]) == ["28304224", "30403574"]


# ---- plants: comparator_named (synthetic root) ----------------------------------------------------------------------
def _art(pmid, ncts, year="2020", pt="Randomized Controlled Trial"):
    db = "".join(f"<AccessionNumber>{n}</AccessionNumber>" for n in ncts)
    return (f"<PubmedArticle><MedlineCitation><PMID>{pmid}</PMID><Article><Journal><JournalIssue><PubDate><Year>{year}"
            f"</Year></PubDate></JournalIssue></Journal><ArticleTitle>T{pmid}</ArticleTitle><PublicationTypeList>"
            f"<PublicationType>{pt}</PublicationType></PublicationTypeList><DataBankList><DataBank><DataBankName>"
            f"ClinicalTrials.gov</DataBankName><AccessionNumberList>{db}</AccessionNumberList></DataBank></DataBankList>"
            f"</Article></MedlineCitation></PubmedArticle>")


def _named_root(tmp_path, rows, arts, trial_set):
    c = tmp_path / "cache" / "s"
    c.mkdir(parents=True)
    (c / "comparators.json").write_text(json.dumps([{"id": "C1", "trial_set": trial_set}]), encoding="utf-8")
    xml = "<PubmedArticleSet>" + "".join(arts) + "</PubmedArticleSet>"
    (c / "comparator_named_pubmed.xml").write_text(xml, encoding="utf-8")
    doc = {"rows": rows, "pubmed_xml": {"document_ref": "cache/s/comparator_named_pubmed.xml",
                                        "sha256": hashlib.sha256(xml.encode("utf-8")).hexdigest()}}
    (c / "comparator_named.json").write_text(json.dumps(doc), encoding="utf-8")
    return tmp_path


def _ts(*rows):
    return [{"family_id": f, "aliases": [{"id": i} for i in ids]} for f, ids in rows]


def test_plant_a_named_trial_enters_screening_and_a_joint_report_is_not_duplicated(tmp_path):
    root = _named_root(tmp_path,
                       [{"comparator": "C1", "row": "A", "identifiers": ["NCT00000001"], "state": "CANDIDATE", "pmids": ["11"]},
                        {"comparator": "C1", "row": "B", "identifiers": ["NCT00000002"], "state": "CANDIDATE", "pmids": ["11"]}],
                       [_art("11", ["NCT00000001", "NCT00000002"])], _ts(("A", ["NCT00000001"]), ("B", ["NCT00000002"])))
    out = cn.merge(root, "s", {"records": []})
    assert [r["id"] for r in out["records"]] == ["11"] and out["records"][0]["found_by"] == ["COMPARATOR_NAMED"]
    assert [x["state"] for x in out["comparator_named"]["rows"]] == ["ENTERED_SCREENING", "JOINT_REPORT_ENTERED"]


def test_plant_a_candidate_never_displaces_a_held_trial(tmp_path):
    root = _named_root(tmp_path, [{"comparator": "C1", "row": "A", "identifiers": ["NCT00000001"], "state": "CANDIDATE",
                                   "pmids": ["11"]}], [_art("11", ["NCT00000001"])], _ts(("A", ["NCT00000001"])))
    held = {"records": [{"id": "99", "nct": "NCT00000001"}]}
    out = cn.merge(root, "s", held)
    assert [r["id"] for r in out["records"]] == ["99"]


def test_plant_a_pooled_analysis_attributed_to_an_unnamed_trial_is_refused(tmp_path):
    root = _named_root(tmp_path, [{"comparator": "C1", "row": "A", "identifiers": ["NCT00000001"], "state": "CANDIDATE",
                                   "pmids": ["11"]}], [_art("11", ["NCT00000009", "NCT00000001"])], _ts(("A", ["NCT00000001"])))
    with pytest.raises(cn.NamedRefused, match="no comparator row names"):
        cn.merge(root, "s", {"records": []})


def test_plant_a_record_not_registered_as_the_row_is_refused(tmp_path):
    root = _named_root(tmp_path, [{"comparator": "C1", "row": "A", "identifiers": ["NCT00000001"], "state": "CANDIDATE",
                                   "pmids": ["11"]}], [_art("11", ["NCT00000005"])], _ts(("A", ["NCT00000001"])))
    with pytest.raises(cn.NamedRefused, match="not registered"):
        cn.merge(root, "s", {"records": []})


def test_plant_a_row_the_panel_no_longer_enumerates_is_refused(tmp_path):
    root = _named_root(tmp_path, [{"comparator": "C1", "row": "GONE", "identifiers": ["NCT00000001"], "state": "CANDIDATE",
                                   "pmids": ["11"]}], [_art("11", ["NCT00000001"])], _ts(("A", ["NCT00000001"])))
    with pytest.raises(cn.NamedRefused, match="no longer"):
        cn.merge(root, "s", {"records": []})


def test_plant_a_changed_held_xml_is_refused(tmp_path):
    root = _named_root(tmp_path, [{"comparator": "C1", "row": "A", "identifiers": ["NCT00000001"], "state": "CANDIDATE",
                                   "pmids": ["11"]}], [_art("11", ["NCT00000001"])], _ts(("A", ["NCT00000001"])))
    p = root / "cache" / "s" / "comparator_named_pubmed.xml"
    p.write_text(p.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(cn.NamedRefused, match="changed"):
        cn.merge(root, "s", {"records": []})


# ---- plants: registry-id table rows (scripts/comparator_trial_tables.py) -------------------------------------------
def _tables():
    import importlib.util
    spec = importlib.util.spec_from_file_location("ctt", ROOT / "scripts" / "comparator_trial_tables.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _jats(caption, cells):
    rows = "".join(f"<tr><td>{c}</td><td>2015</td></tr>" for c in cells)
    return f"<table-wrap id='T1'><caption><p>{caption}</p></caption><table><tbody>{rows}</tbody></table></table-wrap>"


def test_plant_registry_rows_are_read_only_from_an_included_caption_with_one_nct_per_row():
    m = _tables()
    ok = _jats("Characteristics of the included RCTs", ["ALPHA<break/> NCT00000001", "BETA<break/> NCT00000002"])
    (cap, rows), = m.registry_tables(ok)
    assert [r[2] for r in rows] == ["NCT00000001", "NCT00000002"]
    ents = m.build_registry_rows(ok, ok.encode(), "x.xml", rows)
    assert [e["name_in_source"] for e in ents] == ["ALPHA", "BETA"]
    assert all(e["aliases"][0]["span"]["quote"] == ok[e["span"]["start"]:e["span"]["end"]] for e in ents)
    two = _jats("Characteristics of the included RCTs", ["ALPHA NCT00000001 NCT00000003", "BETA NCT00000002"])
    assert m.registry_tables(two) == []
    other = _jats("Adverse events by arm", ["ALPHA NCT00000001", "BETA NCT00000002"])
    assert m.registry_tables(other) == []


# ---- plants: comparator_analysis ------------------------------------------------------------------------------------
def _analysis_root(tmp_path, doc, held="The held comparator text says exactly this sentence."):
    c = tmp_path / "cache" / "s"
    c.mkdir(parents=True)
    (c / "held.txt").write_text(held, encoding="utf-8")
    (c / "comparator_analysis.json").write_text(json.dumps(doc), encoding="utf-8")
    return tmp_path


def test_plant_a_scope_quote_not_in_the_held_text_is_refused(tmp_path):
    doc = {"outcome": "o", "scope": {"quotes": [{"document_ref": "cache/s/held.txt", "quote": "a sentence never printed there"}],
                                     "reading": "r"}}
    with pytest.raises(ca.AnalysisRefused, match="not located"):
        ca.load(_analysis_root(tmp_path, doc), "s")


def _membership_doc(k, n, counts):
    q = {"document_ref": "cache/s/held.txt", "quote": "exactly this sentence"}
    return {"outcome": "o", "governing": dict(q, k=k, n=n), "membership": {"figure": {"caption": q},
            "rows": [{"label": f"r{i}", "counts": c} for i, c in enumerate(counts)]}}


def test_plant_membership_arithmetic_must_match_the_governing_analysis(tmp_path):
    with pytest.raises(ca.AnalysisRefused, match="states 3 studies"):
        ca.load(_analysis_root(tmp_path, _membership_doc(3, 40, [[1, 10, 2, 10], [1, 10, 2, 10]])), "s")


def test_plant_a_bound_row_with_other_counts_than_ours_is_refused(tmp_path):
    doc = _membership_doc(1, 20, [[1, 10, 2, 10]])
    doc["membership"]["rows"][0]["report_pmid"] = "7"
    got = ca.load(_analysis_root(tmp_path, doc), "s")
    review = {"outcomes": [{"primary": True, "trials": [{"label": "7", "ai": 1, "n1i": 10, "ci": 3, "n2i": 10}]}]}
    with pytest.raises(ca.AnalysisRefused, match="differ from our served"):
        ca.assess(got, review)


# ---- the ascertainment evidence map never leaks into a family's eligibility span ------------------------------------
def test_no_family_row_carries_the_topic_ascertainment_evidence():
    # round 3 printed the whole topic evidence map (35 KB, naming other trials) into every population-excluded family's
    # eligibility span on the GLP-1 page
    for p in sorted((ROOT / "docs" / "reviews").glob("*/review.json")):
        for f in json.loads(p.read_text(encoding="utf-8")).get("trial_families") or []:
            span = json.dumps((f.get("eligibility") or {}).get("span") or {})
            assert '"ascertainment": {"clause"' not in span, (p.parent.name, f["family_id"])


# ---- REV-R2 (codex review of this round's modules): each finding reproduced, fixed, and pinned here -----------------
def test_REV_R2_1_a_quote_is_never_located_by_deleting_text_between_lt_and_gt(tmp_path):
    held = "Patients aged 65 years were included."
    doc = {"outcome": "o", "scope": {"reading": "r", "quotes": [
        {"document_ref": "cache/s/held.txt", "quote": "Patients aged <18 years were excluded; those >65 years were included."}]}}
    with pytest.raises(ca.AnalysisRefused, match="not located"):
        ca.load(_analysis_root(tmp_path, doc, held=held), "s")
    # real markup in a held JATS is still ignored
    assert ca._norm("<td>OSLER-1</td> <break/> SOC") == "OSLER-1 SOC"


def test_REV_R2_2_a_candidate_whose_doi_we_hold_never_enters(tmp_path):
    root = _named_root(tmp_path, [{"comparator": "C1", "row": "A", "identifiers": ["22"], "state": "CANDIDATE", "pmids": ["22"]}],
                       [_art("22", [])], _ts(("A", ["22"])))
    xml = (root / "cache" / "s" / "comparator_named_pubmed.xml")
    x = xml.read_text(encoding="utf-8").replace("</Article>", '</Article><PubmedData><ArticleIdList><ArticleId IdType="doi">10.1/X</ArticleId></ArticleIdList></PubmedData>')
    xml.write_text(x, encoding="utf-8")
    d = json.loads((root / "cache" / "s" / "comparator_named.json").read_text(encoding="utf-8"))
    d["pubmed_xml"]["sha256"] = hashlib.sha256(x.encode("utf-8")).hexdigest()
    (root / "cache" / "s" / "comparator_named.json").write_text(json.dumps(d), encoding="utf-8")
    out = cn.merge(root, "s", {"records": [{"id": "1", "doi": "10.1/x"}]})
    assert [r["id"] for r in out["records"]] == ["1"]


def test_REV_R2_3_a_row_recorded_already_held_is_refused_when_nothing_holds_it(tmp_path):
    root = _named_root(tmp_path, [{"comparator": "C1", "row": "A", "identifiers": ["NCT00000001"], "state": "ALREADY_HELD"}],
                       [_art("11", ["NCT00000001"])], _ts(("A", ["NCT00000001"])))
    with pytest.raises(cn.NamedRefused, match="re-run"):
        cn.merge(root, "s", {"records": []})
    assert cn.merge(root, "s", {"records": [{"id": "5", "nct": "NCT00000001"}]})["comparator_named"]["rows"][0]["state"] == "ALREADY_HELD"


def test_REV_R2_4_an_unreconciled_row_is_never_bound_as_shared_inputs(tmp_path):
    doc = _membership_doc(1, 20, [[1, 10, 2, 10]])
    doc["membership"]["rows"][0]["report_pmid"] = "7"
    doc["row_flags"] = [{"row": "r0", "state": "COMPARATOR_ROW_UNRECONCILED"}]
    got = ca.load(_analysis_root(tmp_path, doc), "s")
    review = {"outcomes": [{"primary": True, "trials": [{"label": "7", "ai": 1, "n1i": 10, "ci": 2, "n2i": 10}]}]}
    with pytest.raises(ca.AnalysisRefused, match="never bound"):
        ca.assess(got, review)


def test_REV_R2_6_a_doi_only_row_binds_the_record_carrying_that_doi(tmp_path):
    root = _named_root(tmp_path, [{"comparator": "C1", "row": "A", "identifiers": ["10.1/Y"], "state": "CANDIDATE", "pmids": ["33"]}],
                       [_art("33", [])], _ts(("A", ["10.1/Y"])))
    xml = (root / "cache" / "s" / "comparator_named_pubmed.xml")
    x = xml.read_text(encoding="utf-8").replace("</Article>", '</Article><PubmedData><ArticleIdList><ArticleId IdType="doi">10.1/Y</ArticleId></ArticleIdList></PubmedData>')
    xml.write_text(x, encoding="utf-8")
    d = json.loads((root / "cache" / "s" / "comparator_named.json").read_text(encoding="utf-8"))
    d["pubmed_xml"]["sha256"] = hashlib.sha256(x.encode("utf-8")).hexdigest()
    (root / "cache" / "s" / "comparator_named.json").write_text(json.dumps(d), encoding="utf-8")
    assert [r["id"] for r in cn.merge(root, "s", {"records": []})["records"]] == ["33"]


def test_REV_R2_5_and_7_registry_rows_with_tbody_attributes_and_an_excluded_reference_table():
    m = _tables()
    reg = ("<table-wrap id='T1'><caption><p>Characteristics of the included RCTs</p></caption><table>"
           "<tbody valign='top'><tr><td>ALPHA NCT00000001</td></tr><tr><td>BETA NCT00000002</td></tr></tbody></table></table-wrap>")
    (cap, rows), = m.registry_tables(reg)
    assert [r[2] for r in rows] == ["NCT00000001", "NCT00000002"]
    excl = ('<table-wrap id="T2"><caption><p>Excluded studies</p></caption><table><tbody>'
            '<tr><td>X <xref ref-type="bibr" rid="B1">1</xref></td></tr><tr><td>Y <xref ref-type="bibr" rid="B2">2</xref></td></tr>'
            '</tbody></table></table-wrap>')
    assert m.trial_tables(excl + reg)                                   # a reference-linked table IS present ...
    route, tables = m.choose_route(excl + reg)                          # ... and does not win: its caption is 'Excluded'
    assert route == "REGISTRY_ID_IN_ROW" and [r[2] for r in tables[0][1]] == ["NCT00000001", "NCT00000002"]
    assert m.choose_route(excl)[0] == "REFERENCE_LINKED"                # alone, the old route is unchanged
