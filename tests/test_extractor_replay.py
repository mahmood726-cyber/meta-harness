"""DISPATCH_V14_EXTRACTOR_ROUTE: a value read by a typed extractor over HELD text is EXTRACTOR only when its replay limb
re-derives it identically from the pinned bytes; a script-typed `*_verified` row stays HAND_ENTERED."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import extractor_replay as xr  # noqa: E402
from harness import provenance_class as pc  # noqa: E402

LABEL_SHA = "26c58886d7802376ecc2c3235a2e1acc0bae3dc775bf8744f4df116b23ee0c9d"
LABEL_SPEC = {"table": "Table 3", "trial": "FIDELIO-DKD", "arm_t": "Kerendia", "arm_c": "Placebo",
              "row_label": "Hyperkalemia"}
OMA_SHA = "6ade2476f3f931f8ef952c2afc46f2b11b3292361e933428cbb54784b6420c9b"
OMA_CLAUSE = ("The hHF outcome occurred in 20/2092 patients in the omarigliptin group (0.96%; 0.51/100 patient-years) and "
              "33/2100 patients in the placebo group (1.57%; 0.85/100 patient-years), with an HR of 0.60 (95% CI 0.35, 1.05)")
LINA_SHA = "94e500fb2025e3a5d004490722412507eb1aca81e62c61475b8cee6b17548705"
LINA_CLAUSE = ("Linagliptin versus placebo did not affect the incidence of hHF (209/3494 [6.0%] versus 226/3485 [6.5%], "
               "respectively; hazard ratio [HR], 0.90; 95% CI, 0.74-1.08)")


def _label_row(**kw):
    text = open(os.path.join(ROOT, "outputs", "held_labels", "fda_215341s000lbl.txt"), encoding="utf-8", newline="").read()
    v = xr.read_label_adr_table(text, LABEL_SPEC)
    row = {"id": "PMID 33264825", "provenance": "label_adr_table", "ai": v["ai"], "n1i": v["n1i"], "ci": v["ci"],
           "n2i": v["n2i"], "document_ref": "outputs/held_labels/fda_215341s000lbl.txt", "document_sha256": LABEL_SHA,
           "source_span": v["raw_row"], "source": "label Table 3", "replay": dict(LABEL_SPEC)}
    row.update(kw)
    return row


def _abs_row(pmid, sha, clause, effect, lo, hi, **kw):
    row = {"id": f"PMID {pmid}", "provenance": "held_abstract_clause", "effect": effect, "ci_low": lo, "ci_high": hi,
           "document_ref": f"outputs/held_abstracts/pubmed_{pmid}.txt", "document_sha256": sha, "source_span": clause,
           "source": f"PMID {pmid} abstract"}
    row.update(kw)
    return row


def _held(_):
    return True


def test_the_label_reader_reads_fidelio_hyperkalaemia_by_type():
    r = _label_row()
    assert (r["ai"], r["n1i"], r["ci"], r["n2i"]) == (516, 2827, 255, 2831)


def test_PLANT_a_replayed_label_row_is_extractor():
    assert pc.classify_served(_label_row(), _held)[0] == "EXTRACTOR"


@pytest.mark.parametrize("change", [{"ai": 517}, {"n2i": 2830}, {"document_sha256": "0" * 64},
                                    {"replay": dict(LABEL_SPEC, row_label="Hypokalemia")}, {"replay": {}},
                                    {"document_ref": "cache/finerenone-ckd-t2d-renal/records.json"},
                                    {"document_ref": "outputs/held_labels/../held_abstracts/pubmed_28893244.txt"},
                                    {"source_span": "Hyperkalemia 516 (18.3) 255 (9.0) X"}])
def test_PLANT_a_label_row_that_does_not_replay_identically_is_untraced(change):
    cls, why = pc.classify_served(_label_row(**change), _held)
    assert cls == "UNTRACED", why


@pytest.mark.parametrize("pmid,sha,clause,eff", [("28893244", OMA_SHA, OMA_CLAUSE, (0.60, 0.35, 1.05)),
                                                 ("30586723", LINA_SHA, LINA_CLAUSE, (0.90, 0.74, 1.08))])
def test_PLANT_a_replayed_held_abstract_clause_is_extractor(pmid, sha, clause, eff):
    assert pc.classify_served(_abs_row(pmid, sha, clause, *eff), _held)[0] == "EXTRACTOR"
    # one number moved, or the clause not in the held bytes, or another document: never extractor
    assert pc.classify_served(_abs_row(pmid, sha, clause, eff[0] + 0.01, *eff[1:]), _held)[0] == "UNTRACED"
    assert pc.classify_served(_abs_row(pmid, sha, clause + " x", *eff), _held)[0] == "UNTRACED"
    assert pc.classify_served(_abs_row(pmid, "f" * 64, clause, *eff), _held)[0] == "UNTRACED"


@pytest.mark.parametrize("clause", ["HR 0.60 (95% CI 0.35, 1.05) with 20/2092 events",           # one n/N only
                                    "20/2092 v 33/2100; HR of 0.60 (95% CI 0.65, 1.05)",           # HR outside its CI
                                    "20/2092 v 33/2100; HR of 0.60 (95% CI 0.35, 1.05); HR of 0.70 (95% CI 0.5, 0.9)"])
def test_PLANT_the_clause_reader_refuses_rather_than_guesses(clause):
    with pytest.raises(xr.ReadRefused):
        xr.read_abstract_clause(clause)


def test_a_script_typed_verified_row_stays_hand_entered():
    """The class follows the replay, never the provenance string: '*_verified' is HAND_ENTERED as before."""
    assert pc.classify_served({"provenance": "abstract_verified", "source": "x", "effect": 0.6}, _held)[0] == \
        "HAND_ENTERED"


def _harm_outcome():
    return {"name": "Hyperkalemia (FDA label adverse reaction, FIDELIO-DKD safety population)", "kind": "harm",
            "trials": [{"id": "PMID 33264825", "label": "FIDELIO-DKD", "ai": 516, "n1i": 2827, "ci": 255, "n2i": 2831,
                        "source_span": "Hyperkalemia 516 (18.3) 255 (9.0)"}],
            "declared_absent_trials": [], "result": {"present": True}}


def test_PLANT_a_source_scoped_harm_is_not_incomplete_because_another_trial_uses_its_keyword():
    """V14-03: FIGARO's abstract reports LAB hyperkalaemia; the label endpoint is scoped to the label table, which covers
    FIDELIO only -- FIGARO is 'not in this source', never 'known reported, unresolved' (publication gate L1)."""
    from harness import harms
    spec = {"keywords": ["hyperkalemia", "hyperkalaemia"],
            "source_scope": {"document_ref": "outputs/held_labels/fda_215341s000lbl.txt", "trials": ["33264825"]}}
    included = [{"id": "33264825"}, {"id": "34449181"}]
    recs = {"34449181": {"abstract": "Hyperkalemia led to discontinuation in 1.2% of finerenone patients."}}
    out = harms.annotate_outcome(_harm_outcome(), spec, included, recs)
    assert not out["result"].get("harms_incomplete") and not out["result"].get("harms_synthesis_suppressed")
    # the same keyword WITHOUT a scope still makes it incomplete (the gate is unchanged for every other outcome)
    out = harms.annotate_outcome(_harm_outcome(), {"keywords": spec["keywords"]}, included, recs)
    assert out["result"].get("harms_incomplete")


def test_PLANT_a_malformed_source_scope_fails_loudly():
    from harness import harms
    with pytest.raises(ValueError):
        harms.annotate_outcome(_harm_outcome(), {"keywords": ["x"], "source_scope": {"trials": ["1"]}},
                               [{"id": "33264825"}, {"id": "2"}], {"2": {"abstract": "x"}})
