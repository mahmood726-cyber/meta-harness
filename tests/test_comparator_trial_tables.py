"""V1.0.1: comparator trial tables read from the held PMC JATS (scripts/comparator_trial_tables.py) and the overlap
relation computed from explicit trial identities. Fixture: Zhao 2022 (PMC9438305), 9 trials; shared with our
colchicine-POAF pool = COPPS-2 and END-AF Low Dose; Farzaneh (PMID 42132185) ours only."""
import glob, importlib.util, json, os

import pytest

from harness import comparator_panel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("ctt", os.path.join(ROOT, "scripts", "comparator_trial_tables.py"))
ctt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctt)
ZHAO = os.path.join(ROOT, "cache", "colchicine-postop-af", "comparator_pmc_jats.xml")


def test_zhao_table_parses_to_nine_rows_each_linked_to_its_reference():
    xml = open(ZHAO, encoding="utf-8").read()
    tables = ctt.trial_tables(xml)
    rows = tables[0][1]
    assert len(rows) == 9
    rf = ctt.refs(xml)
    pmids = {rf[r]["ids"].get("pmid") for _, _, rids in rows for r in rids}
    assert {"25172965", "32720823"} <= pmids                       # COPPS-2, END-AF Low Dose
    sar = [rf[r] for _, _, rids in rows for r in rids if rf[r]["surname"] == "Sarzaeem"][0]
    assert not sar["ids"] and (sar["source"], sar["volume"], sar["fpage"]) == ("Tehran Univ Med J", "72", "147")


def test_bibr_links_are_read_whatever_the_attribute_order():
    assert ctt.bibr_rids('<xref ref-type="bibr" rid="R1">1</xref>') == ["R1"]
    assert ctt.bibr_rids('<xref rid="R2 R3" ref-type="bibr">2,3</xref>') == ["R2", "R3"]
    assert ctt.bibr_rids('<xref rid="T1" ref-type="table">T1</xref>') == []


@pytest.mark.parametrize("path", sorted(glob.glob(os.path.join(ROOT, "cache", "*", "comparators.json"))),
                         ids=lambda p: os.path.basename(os.path.dirname(p)))
def test_every_stored_trial_set_revalidates(path):
    for c in json.load(open(path, encoding="utf-8")):
        comparator_panel.validate(c, ROOT)


def test_PLANT_a_row_bound_to_a_reference_it_does_not_cite_is_refused():
    panel = json.load(open(os.path.join(ROOT, "cache", "colchicine-postop-af", "comparators.json"), encoding="utf-8"))
    c = next(x for x in panel if x.get("trial_set"))
    rows = c["trial_set"]
    a, b = next(r for r in rows if r["aliases"]), next(r for r in reversed(rows) if r["aliases"])
    a["aliases"] = [dict(b["aliases"][0])]                          # row a now claims row b's reference
    with pytest.raises(ValueError, match="reference link not located"):
        comparator_panel.validate(c, ROOT)


def test_PLANT_colchicine_poaf_overlap_from_explicit_identities():
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", "colchicine-postop-af", "review.json"), encoding="utf-8"))
    o = rev["comparator"]["overlap_relation"]
    assert o["relation"] == "OVERLAPPING" and o["theirs_k"] == 9 and o["shared_k"] == 2
    assert o["shared"] == ["NCT01552187", "NCT03015831"]           # COPPS-2, END-AF Low Dose
    assert o["only_ours"] == ["SYN-f9c2d88aa0de"]                   # Farzaneh (PMID 42132185, 2026)
    assert "not machine-exposed" not in json.dumps(rev["comparator"]["overlap"])


def test_PLANT_pericarditis_overlap_from_the_committed_transcription_table():
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", "colchicine-recurrent-pericarditis", "review.json"), encoding="utf-8"))
    o = rev["comparator"]["overlap_relation"]
    fam = {f["family_id"]: f["aliases"].get("acronym") for f in rev["trial_families"]}
    assert o["relation"] == "OVERLAPPING" and o["theirs_k"] == 5 and o["shared_k"] == 1
    assert [fam[x] for x in o["shared"]] == [["CORP"]] and o["only_ours"] == ["NCT00235079"]        # CORP-2 ours only
    assert o["only_theirs"] == ["Finkelstein (row 1)", "COPE (row 2)", "CORE (row 3)", "COPPS (row 4)"]
    assert rev["comparator"]["overlap"]["only_ours"] == ["NCT00235079"]                               # not ICAP
    inv = {r["comparator_trial"]: r for r in o["inventory_comparison"]["rows"]}
    assert inv["COPPS (row 4)"]["status"] == "SCREENED_OUT"                                         # postoperative
    assert inv["COPE (row 2)"]["status"] == "NOT_IN_OUR_RECORDS"
    assert "open-label" in inv["COPE (row 2)"]["row_design_as_printed"].lower()                   # not 'missing eligible'


def test_PLANT_CORP_never_binds_to_a_CORP_2_report():
    panel = json.load(open(os.path.join(ROOT, "cache", "colchicine-recurrent-pericarditis", "comparators.json"), encoding="utf-8"))
    corp = next(m for c in panel for m in c.get("trial_set") or [] if m["name_in_source"] == "CORP")
    assert [a["id"] for a in corp["aliases"]] == ["21873705"]                                     # CORP, not CORP-2 24694983
