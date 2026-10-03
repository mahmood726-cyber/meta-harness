"""IDREVIEW (Codex gpt-5.5, cross-vendor adversarial review of the identity class fix): its four findings, written by
the reviewer as strict xfails, kept here as REGRESSION tests now that each is fixed on g1/identity."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / "scripts"))

from kgap import k_gap  # noqa: E402
import k_gap_table as kt  # noqa: E402
import ref_title_pmid_lookup as title_lookup  # noqa: E402


IDX = {
    "pmid_nct": {},
    "nct_pmids": {},
    "agent_nct": {},
    "acr_nct": {},
    "acr_title_nct": {},
    "study": {},
}


def parsed(*refs):
    return {
        "refs": {
            r["rid"]: {
                "label": "",
                "ordinal": i + 1,
                "pmid": None,
                "doi": None,
                "title": "",
                "year": "",
                "first_author": "",
                "text": "",
                **r,
            }
            for i, r in enumerate(refs)
        }
    }


def unit(label, **kw):
    t = k_gap.identity_tokens(label)
    return {
        "cited": [],
        "ncts": [],
        "author": t["author"],
        "year": t["year"],
        "acronyms": t["acronyms"],
        "marker": t["marker"],
        "label": label,
        **kw,
    }


NAMES = [
    "Able",
    "Baker",
    "Carter",
    "Dawson",
    "Ellis",
    "Foster",
    "Garner",
    "Hughes",
    "Irwin",
    "Jordan",
    "Keller",
]


def shifted_refs_for_acronym_outlier():
    refs = [
        {
            "rid": f"R{i}",
            "label": str(i),
            "pmid": str(91000000 + i),
            "first_author": NAMES[i - 1],
            "year": "2010",
            "title": f"{NAMES[i - 1]} trial report",
        }
        for i in range(1, 12)
    ]
    rows = [
        dict(
            unit(f"{NAMES[i]} 2010 [{i}]", layout="row", table="T1"),
            distrust_links="plant shifted table",
        )
        for i in range(1, 10)
    ]
    rows.append(
        dict(
            unit("OMEGA [10]", layout="row", table="T1"),
            distrust_links="plant shifted table",
        )
    )
    return rows, parsed(*refs)


def test_p1_marker_offset_must_not_resolve_acronym_only_outlier_to_shifted_wrong_ref():
    rows, p = shifted_refs_for_acronym_outlier()
    learned = kt.learn_marker_offsets(rows, p)

    assert learned["T1"]["offset"] == 1
    outlier = rows[-1]
    r = kt.resolve_unit(outlier, p, IDX, None)

    assert r["pmids"] == []
    assert any("shifted_ref_disagrees" in b for b in r["basis"])


def test_negative_marker_offset_resolves_author_year_rows_that_prove_same_shift():
    rows, p = shifted_refs_for_acronym_outlier()
    kt.learn_marker_offsets(rows, p)

    r = kt.resolve_unit(rows[0], p, IDX, None)

    assert r["pmids"] == ["91000002"]
    assert any(b.startswith("label_marker_ref_shifted:+1:1->2") for b in r["basis"])


def test_p1_title_confirmation_must_not_accept_same_stem_with_different_trial_subtitle():
    cited = "A randomized trial of omega therapy for cardiovascular prevention"
    pubmed = cited + ": renal outcomes in the eye disease substudy"

    assert not title_lookup.same_title(pubmed, cited)


def test_negative_title_confirmation_keeps_exact_normalized_title_match():
    cited = "Combined lifestyle modification and metformin in obese patients with polycystic ovary syndrome"

    assert title_lookup.same_title(cited + ".", cited)


def test_p2_subgroup_row_must_not_discard_real_acronym_group_trial_label():
    u = unit("GROUP (n = 120)", layout="row")

    assert kt.subgroup_row(u) is None


def test_negative_subgroup_row_still_discards_plain_group_description():
    u = unit("Placebo users group (n = 120)", layout="row")

    assert kt.subgroup_row(u) == "SUBGROUP_ROW_GROUP_DESCRIPTION_WITH_SIZE_NO_STUDY_IDENTITY"


def test_p1_any_agent_acronym_requires_corroborration_before_identity(monkeypatch):
    monkeypatch.setattr(kt, "SELF_REG", {})
    idx = {
        **IDX,
        "acr_nct": {k_gap.norm_acronym("FIGARO-DKD"): ["NCT02545049"]},
        "study": {"NCT02545049": {"study_first_submitted_date": "2015-09-02"}},
        "agent_nct": {"NCT02545049": False},
    }

    r = kt.resolve_unit(unit("FIGARO-DKD2022", layout="row"), None, idx, None)

    assert r["ncts"] == []
    assert not any(b.startswith("acronym_aact_any_agent") for b in r["basis"])


def test_negative_any_agent_acronym_ambiguity_is_not_guessed(monkeypatch):
    monkeypatch.setattr(kt, "SELF_REG", {})
    idx = {
        **IDX,
        "acr_nct": {k_gap.norm_acronym("SCORED"): ["NCT03222193", "NCT03315143"]},
        "study": {
            "NCT03222193": {"study_first_submitted_date": "2017-01-01"},
            "NCT03315143": {"study_first_submitted_date": "2017-01-01"},
        },
        "agent_nct": {"NCT03222193": False, "NCT03315143": False},
    }

    r = kt.resolve_unit(unit("SCORED2021", layout="row"), None, idx, None)

    assert r["ncts"] == []
    assert "acronym_aact_any_agent_ambiguous_acronym:SCORED:2" in r["basis"]
