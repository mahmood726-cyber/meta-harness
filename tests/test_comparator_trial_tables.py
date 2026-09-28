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
    # V1.0.1 (PCSK9 review): a trial a held comparator names enters screening (harness/comparator_named.py); COPE is now
    # screened and excluded (no placebo arm), never "missing eligible"
    assert inv["COPE (row 2)"]["status"] == "SCREENED_OUT"
    assert "open-label" in inv["COPE (row 2)"]["row_design_as_printed"].lower()                   # not 'missing eligible'


def test_PLANT_CORP_never_binds_to_a_CORP_2_report():
    panel = json.load(open(os.path.join(ROOT, "cache", "colchicine-recurrent-pericarditis", "comparators.json"), encoding="utf-8"))
    corp = next(m for c in panel for m in c.get("trial_set") or [] if m["name_in_source"] == "CORP")
    assert [a["id"] for a in corp["aliases"]] == ["21873705"]                                     # CORP, not CORP-2 24694983


def test_PLANT_esketamine_transform3_is_shared_through_screenings_dedup_parent():
    # the comparator cites TRANSFORM-3's paper (PMID 31734084); we pool TRANSFORM-3 from its registry record
    # (NCT02422186) and screening excluded the paper as its secondary publication (X-DEDUP). Binding the row to the
    # paper's own family made TRANSFORM-3 look "ours only" and the relation OVERLAPPING; it is SUBSET.
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", "esketamine-trd-madrs", "review.json"), encoding="utf-8"))
    o = rev["comparator"]["overlap_relation"]
    # theirs_k 6 -> 4 (V1.0.1 esketamine review): generic row labels never count as identities; at trial level the
    # comparator holds TRANSFORM-1, TRANSFORM-2, TRANSFORM-3 and Chen 2023
    assert o["relation"] == "SUBSET" and o["theirs_k"] == 4 and o["only_ours"] == []
    assert o["shared"] == ["NCT02418585", "NCT02422186", "NCT03434041"]           # TRANSFORM-2, TRANSFORM-3, Chen 2023
    inv = {r["comparator_trial"].split(" ")[1]: r for r in o["inventory_comparison"]["rows"]}
    assert inv["D"]["status"] == "POOLED" and inv["D"]["family"] == "NCT02422186"
    assert inv["B"]["family"] == "NCT02417064"          # TRANSFORM-1, held by registry only: bound by its title acronym
    # SUSTAIN-2 (row E) is outside the comparator's Day-28 MADRS pool (outcome-level membership A-D, row n = stated
    # participants); it is listed as out of scope with its endpoint, never dropped. Since comparator-named trials enter
    # screening (V1.0.1, PCSK9 review) its cited report 32316080 is screened, so it binds to that family -- which is
    # never pooled
    oos = {m["name"].split(" ")[1]: m for m in o["theirs"]["out_of_scope"]}
    assert oos["E"]["family"] == "NCT02497287" and oos["E"]["endpoint"] == "maintenance randomised-withdrawal analysis"
    assert "NCT02497287" not in o["shared"]
    assert "E" not in inv


def _synthetic(title, families, screening=()):
    from harness import overlap_relation as ov
    rid = "R1"
    quote = f'<ref id="{rid}"><mixed-citation><article-title>{title}</article-title> <pub-id pub-id-type="pmid">99999999</pub-id></mixed-citation></ref>'
    panel = {"trial_set": [{"family_id": "Row 1", "aliases": [{"id": "99999999", "span": {"quote": quote}}]}]}
    review = {"trial_families": families, "screening": {"records": list(screening)}}
    acr = ov._acronym_index(review, lambda _r: None)
    return ov._members(review, panel, "x", acr, set())[1][0]


def _fam(fid, acr, reports=()):
    return {"family_id": fid, "aliases": {"acronym": [acr], "registry_ids": [fid], "report_ids": list(reports)}}


def test_PLANT_title_acronym_binds_only_a_whole_token_naming_exactly_one_family():
    fams = [_fam("NCT00000002", "TRANSFORM-2"), _fam("NCT00000003", "TRANSFORM-3")]
    assert _synthetic("Esketamine in elderly patients-TRANSFORM-3", fams)["family"] == "NCT00000003"
    assert _synthetic("Esketamine in adults (TRANSFORM)", fams)["family"] is None               # not TRANSFORM-2/-3
    assert _synthetic("A study (TRANSFORM-3)", fams)["family"] == "NCT00000003"
    assert _synthetic("A study (PRE-TRANSFORM-3)", fams)["family"] is None                       # a fragment is not a token
    two = fams + [_fam("NCT00000009", "TRANSFORM-3")]
    assert _synthetic("Esketamine-TRANSFORM-3", two)["family"] is None                           # ambiguous: refused


def test_PLANT_dedup_parent_needs_a_registration_that_is_one_family():
    fams = [_fam("NCT00000003", "T3"), {"family_id": "SYN-x", "aliases": {"report_ids": ["99999999"]}}]
    dd = {"id": "99999999", "rule_id": "X-DEDUP", "secondary_publication_of": "T3 (NCT00000003, already pooled)"}
    assert _synthetic("A paper", fams, [dd])["family"] == "NCT00000003"
    assert _synthetic("A paper", fams, [dict(dd, secondary_publication_of="T3 (NCT09999999)")])["family"] == "SYN-x"
    assert _synthetic("A paper", fams)["family"] == "SYN-x"                                       # no decision: no redirect


def test_PLANT_name_only_rows_are_bound_through_their_own_citations_not_by_date():
    """With the publication-year rule removed, a name-only comparator row is identified by the reference it cites:
    Zayed's 'Young [10]' -> CR10 (2015, PMID 26444692), 'Young [17]' -> CR17 (2014, PMID 23732264); Imazio 2012's
    'COPE study 1' -> reference 1 -> PubMed ecitmatch PMID 16186437."""
    bc = json.load(open(os.path.join(ROOT, "cache", "balanced-crystalloids-vs-saline-mortality", "comparators.json"), encoding="utf-8"))
    got = {m["family_id"]: [a["id"] for a in m.get("aliases") or []] for c in bc for m in c.get("trial_set") or []}
    assert got["Young 2015"] == ["26444692"] and got["Young 2014"] == ["23732264"] and got["Verma 2016"] == ["27604335"]
    assert got["Ratanarat 2017"] == []                      # its reference carries no identifier: left unbound, reported
    pc = json.load(open(os.path.join(ROOT, "cache", "colchicine-recurrent-pericarditis", "comparators.json"), encoding="utf-8"))
    got = {m["family_id"]: [a["id"] for a in m.get("aliases") or []] for c in pc for m in c.get("trial_set") or []}
    assert got["COPE (row 2)"] == ["16186437"] and got["CORE (row 3)"] == ["16186468"] and got["Finkelstein (row 1)"] == ["12574898"]


def test_PLANT_swapping_the_two_Young_rows_citations_is_refused():
    import copy
    bc = json.load(open(os.path.join(ROOT, "cache", "balanced-crystalloids-vs-saline-mortality", "comparators.json"), encoding="utf-8"))
    c = copy.deepcopy(next(x for x in bc if x.get("trial_set")))
    rows = {m["family_id"]: m for m in c["trial_set"]}
    rows["Young 2015"]["aliases"], rows["Young 2014"]["aliases"] = rows["Young 2014"]["aliases"], rows["Young 2015"]["aliases"]
    with pytest.raises(ValueError, match="table row / reference / year"):
        comparator_panel.validate(c, ROOT)


def test_balanced_crystalloids_is_disjoint_by_identity_alone():
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", "balanced-crystalloids-vs-saline-mortality", "review.json"), encoding="utf-8"))
    o = rev["comparator"]["overlap_relation"]
    assert o["relation"] == "DISJOINT" and o["shared_k"] == 0 and "date" not in o["basis"]
