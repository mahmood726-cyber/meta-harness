"""V1.0.1 typed funding (harness/funding_typed.py): {funders[], material_support[], funder_role_statement} replace the
single public-vs-industry label. Fixture from the colchicine-secondary-CV review: LoDoCo2 was served public/non-profit
from "(Funded by the National Health Medical Research Council of Australia and others; ...)"."""
import json
import os

import pytest

from harness import consumer_consistency as cc, funding, funding_typed as ft, gate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "colchicine-secondary-cv-prevention"


def _typed(slug, tid, typ="public/non-profit"):
    blob = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    rows = [{"id": f"PMID {tid}", "type": typ}]
    cc.type_funding_rows(slug, rows, cc.records_by_id(blob), cc.fulltexts_by_id(slug, blob))
    return rows[0]


def test_PLANT_LoDoCo2_industry_tie_present_from_held_sources():
    row = _typed(SLUG, "32865380")
    t = row["typed"]
    assert t["industry_tie"] == "PRESENT" and row["type"] == "industry tie present"
    names = {f["name"] for f in t["funders"] if f["class"] == "INDUSTRY"}
    assert {"Teva", "Disphar", "Tiofarma"} <= names                                    # ANZCTR Commercial sector/Industry
    assert "Teva, Haarlem, Disphar, Baarn and Tiofarma, Oud-Beijerland" in names        # publisher funding metadata
    assert row["label_from_first_sentence"] == "public/non-profit"                      # what it was, kept visible
    assert {"source": "abstract funding sentence", "state": "PARTIAL"} in t["list_completeness"]
    # the paper's funder-role statement is in the NEJM full text, which is not held: typed as such, never invented
    assert t["funder_role_statement"] == {"state": "FULL_TEXT_NOT_HELD"}
    assert funding.industry_tied(row) and funding.funding_known(row)


def test_PLANT_industry_tie_is_kept_WITH_the_independence_statement():
    """The shape the review asked for, on a held full text (tocilizumab RCT-TCZ-COVID, PMID 33080005): Roche supplied
    the drug, and the funders had no role in design, analysis or reporting. Both are kept; the statement does not
    cancel the tie."""
    t = _typed("tocilizumab-covid19-mortality", "33080005", "industry")["typed"]
    assert t["industry_tie"] == "PRESENT"
    assert [m["supplier"] for m in t["material_support"]] == ["Roche"]
    role = t["funder_role_statement"]
    assert role["state"] == "STATED" and "had no role in the design" in role["quote"]
    assert {"design", "analysis", "reporting", "decision to submit"} <= set(role["roles_excluded"])


def test_PLANT_synthetic_LoDoCo2_statement_regex():
    fulltext = ("Supported by the National Health and Medical Research Council of Australia, the Netherlands Heart "
                "Foundation, and a consortium of Teva, Disphar, and Tiofarma. Colchicine and placebo tablets were "
                "provided by Tiofarma. The funders did not control the design, analysis or reporting of the trial.")
    t = ft.build("x", "", fulltext, [], [])
    assert t["industry_tie"] == "PRESENT"
    assert any("Teva" in f["name"] for f in t["funders"] if f["class"] == "INDUSTRY")   # 'consortium of Teva'
    assert t["material_support"][0]["supplier"] == "Tiofarma"
    # without a registry category, a company with no name marker stays UNCLASSIFIED -- listed for a proposal, never guessed
    assert "Tiofarma" in t["needs_proposal"]
    assert t["funder_role_statement"]["state"] == "STATED"
    assert set(t["funder_role_statement"]["roles_excluded"]) >= {"design", "analysis", "reporting"}


@pytest.mark.parametrize("abstract", [
    "(Funded by the National Health Medical Research Council of Australia and others; LoDoCo2 ...)",
    "(Funded by the Government of Quebec and others; COLCOT ClinicalTrials.gov number, NCT02551094.)",
])
def test_PLANT_a_public_funder_and_others_never_establishes_no_industry_tie(abstract):
    t = ft.build("x", abstract, "", [], [])
    assert t["industry_tie"] == "NOT_ESTABLISHED"
    assert t["label"] == "public funder named; industry tie not established"
    assert "partial" in t["industry_tie_basis"]
    assert not funding.funding_known({"typed": t}) and not funding.industry_tied({"typed": t})


def test_PLANT_absence_needs_a_complete_statement_of_classified_public_funders():
    full = "This trial was funded by the National Institutes of Health. The funders had no role in the analysis."
    assert ft.build("x", "", full, [], [])["industry_tie"] == "ABSENT"
    assert ft.build("x", "", full.replace("Health.", "Health and others."), [], [])["industry_tie"] == "NOT_ESTABLISHED"
    assert ft.build("x", "", full.replace("the National Institutes of Health", "Acme Trust"), [], [])["industry_tie"] == "NOT_ESTABLISHED"


def test_PLANT_author_conflict_of_interest_is_not_trial_funding_and_tags_are_not_text():
    full = ("<p>Dr X reported receiving grants from Pfizer outside the submitted work.</p>"
            "<p content-type='funding-statement'>This study was funded by the National Institutes of Health.</p>")
    t = ft.build("x", "", full, [], [])
    assert [f["name"] for f in t["funders"]] == ["National Institutes of Health"] and t["industry_tie"] == "ABSENT"


def test_a_model_proposal_is_shown_never_applied():
    t = ft.build("x", "Funded by Acme Trust.", "", [], [], {"x": {"model": "m", "proposal": "PUBLIC"}})
    assert t["proposal"]["applied"] is False and t["industry_tie"] == "NOT_ESTABLISHED"


def test_gate_refuses_a_public_label_without_a_proven_absence(tmp_path):
    row = _typed(SLUG, "32865380")
    bad = dict(row, type="public/non-profit")
    (tmp_path / "review.json").write_text(json.dumps({"funding": [bad]}), encoding="utf-8")
    msgs = gate.check_funding_label_derived(str(tmp_path))
    assert any("public/non-profit" in m for m in msgs) and any("typed object says" in m for m in msgs)
    (tmp_path / "review.json").write_text(json.dumps({"funding": [row]}), encoding="utf-8")
    assert gate.check_funding_label_derived(str(tmp_path)) == []


def test_served_colchicine_page_uses_the_typed_labels():
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "review.json"), encoding="utf-8"))
    by = {r["id"]: r for r in rev["funding"]}
    assert by["PMID 32865380"]["typed"]["industry_tie"] == "PRESENT"                   # LoDoCo2
    assert by["PMID 39555823"]["typed"]["industry_tie"] == "PRESENT"                   # CLEAR SYNERGY (Boston Scientific)
    assert by["PMID 31733140"]["typed"]["industry_tie"] == "NOT_ESTABLISHED"           # COLCOT: 'Quebec and others'
    assert gate.check_funding_label_derived(os.path.join(ROOT, "docs", "reviews", SLUG)) == []
